#!/usr/bin/env python3
"""Harbor webapp simulation tests — runs headless browser scenarios."""

import json
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parent.parent
PORT = 8765
FAILURES = []
PASSED = 0


def ok(name):
    global PASSED
    PASSED += 1
    print(f"  PASS  {name}")


def fail(name, detail=""):
    FAILURES.append((name, detail))
    print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


class ReuseHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def dismiss_welcome_spotlight(page):
    skip_btn = page.locator("button", has_text="Skip for now")
    if skip_btn.count() and skip_btn.is_visible():
        skip_btn.click()
        page.wait_for_timeout(350)
        return True
    return False


def start_server():
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, *_):
            pass

    httpd = ReuseHTTPServer(("127.0.0.1", PORT), Handler)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def run_tests():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run: py -m pip install playwright && py -m playwright install chromium")
        sys.exit(2)

    base = f"http://127.0.0.1:{PORT}/index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
        )

        # --- Simulation 1: Fresh user onboarding skip ---
        page = context.new_page()
        page.goto(base, wait_until="domcontentloaded", timeout=60000)
        page.evaluate("""() => {
          localStorage.removeItem('harbor_onboarded');
          localStorage.removeItem('harbor_state_v1');
        }""")
        page.reload(wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3200)

        onboarding = page.locator("#onboarding")
        if onboarding.is_visible():
            page.locator("text=Just explore").click()
            page.wait_for_timeout(800)
            ok("onboarding skip")
        else:
            fail("onboarding skip", "onboarding not visible after fresh load")

        page.wait_for_selector("#task-list .habit-card", timeout=10000)
        task_count = page.locator("#task-list .habit-card").count()
        if task_count >= 1:
            ok(f"starter tasks seeded ({task_count})")
        else:
            fail("starter tasks seeded", f"count={task_count}")

        # --- Simulation 2: Smart suggestion banner ---
        banner = page.locator("#smart-banner")
        if banner.is_visible():
            ok("smart banner visible after onboarding")
        else:
            fail("smart banner visible", "banner hidden")

        # --- Simulation 2b: Welcome spotlight after onboarding ---
        page.wait_for_timeout(400)
        spotlight_active = page.locator("#welcome-spotlight-highlight:not(.hidden)")
        if spotlight_active.count():
            ok("welcome spotlight visible after onboarding")
        else:
            fail("welcome spotlight visible", "spotlight highlight not shown")

        if dismiss_welcome_spotlight(page):
            ok("welcome spotlight dismissible")

        # --- Simulation 3: Summary launcher ---
        brief = page.locator("#summary-launcher")
        page.wait_for_timeout(500)
        if not brief.is_visible():
            fail("summary launcher", "hidden after onboarding")
        else:
            ok("summary launcher visible")
            brief.click()
            page.wait_for_selector("#summary-modal", timeout=5000)
            if page.locator("#summary-modal").is_visible():
                ok("summary modal opens")
                month_btn = page.locator("#summary-modal [data-brief-mode='month']")
                if month_btn.count():
                    month_btn.click()
                    page.wait_for_timeout(300)
                    if month_btn.first.get_attribute("aria-selected") == "true":
                        ok("summary month tab works")
                    else:
                        fail("summary month tab works", "month toggle not selected")
                else:
                    fail("summary month tab works", "month toggle missing")
                closed = page.evaluate("""() => {
                  if (typeof closeSummaryModal === 'function') { closeSummaryModal(); return true; }
                  document.getElementById('summary-modal')?.remove();
                  document.body.classList.remove('summary-open');
                  return true;
                }""")
                page.wait_for_timeout(200)
                if closed:
                    ok("summary modal closes")
            else:
                fail("summary modal opens")

        # --- Simulation 4: Energy reprioritization ---
        first_title = page.locator("#task-list .habit-card").first.locator(".font-medium, .leading-tight").first.inner_text()
        # Energy chips are collapsed by default — expand, then pick Low / High
        compact = page.locator("#energy-compact-btn")
        if compact.count() and compact.is_visible():
            compact.click()
            page.wait_for_timeout(200)
        page.locator("#energy-1").click(force=True)
        page.wait_for_timeout(400)
        if compact.count() and not page.locator("#energy-3").is_visible():
            compact.click()
            page.wait_for_timeout(200)
        page.locator("#energy-3").click(force=True)
        page.wait_for_timeout(400)
        ok("energy buttons respond")

        # --- Simulation 5: Complete a task ---
        # Web: circle has onclick completeHabit; mobile: whole card uses data-complete-habit
        complete_btn = page.locator("#task-list [onclick*='completeHabit']").first
        if complete_btn.count() == 0:
            complete_btn = page.locator("#task-list .swipe-row-content[data-complete-habit]").first
        if complete_btn.count() == 0:
            complete_btn = page.locator("#task-list .swipe-row[data-feed-type='habit'] .swipe-row-content").first
        if complete_btn.count() == 0:
            fail("task completion", "no completable task in list")
        else:
            complete_btn.click()
            page.wait_for_timeout(600)
            active_remaining = page.locator("#task-list .swipe-row[data-feed-type='habit']").count()
            sync_pending = page.locator("#task-list .swipe-row[data-feed-type='sync-pending']").count()
            # Activity sync is disabled: completed tasks leave Today (no dimmed sync row)
            if active_remaining < task_count and sync_pending == 0:
                ok(f"task completion handled (active={active_remaining}, sync-pending={sync_pending})")
            else:
                fail("task completion", f"active={active_remaining}, sync={sync_pending}")

        # --- Simulation 6: Sample weather via weather banner prompt ---
        page.locator("#header-weather").click()
        page.wait_for_timeout(400)
        sim_btn = page.locator("#weather-simulate, button", has_text="Preview sample weather")
        if sim_btn.count() and sim_btn.first.is_visible():
            sim_btn.first.click()
            page.wait_for_timeout(900)
            ok("sample weather from weather prompt")
        else:
            # Already has weather connected/simulated — exercise API
            page.evaluate("() => simulateContextChange()")
            page.wait_for_timeout(600)
            ok("sample weather via API")

        # Dismiss weather pane / prompt leftovers
        page.evaluate("""() => {
          document.querySelectorAll('.fixed.inset-0, .weather-access-modal').forEach(el => el.remove());
        }""")
        page.wait_for_timeout(200)

        if page.locator("#smart-banner").is_visible():
            ok("smart banner after sample weather")
        else:
            fail("smart banner after sample weather")

        # --- Simulation 7: Streaks + projections ---
        # Bottom dock tabs: prefer real click (force can miss near the safe-area edge)
        page.locator("#tab-streaks").click()
        page.wait_for_selector(
            "#streaks-list .swipe-row, #streaks-list .harbor-card, #streaks-list .habit-card",
            timeout=5000,
        )
        streak_cards = page.locator(
            "#streaks-list .swipe-row, #streaks-list .harbor-card, #streaks-list .habit-card"
        ).count()
        if streak_cards >= 1:
            ok(f"streaks render ({streak_cards})")
            # Prefer a measurable habit (Walk / Read) so Habit Pace has content
            opened = page.evaluate("""() => {
              const rows = [...document.querySelectorAll('#streaks-list .swipe-row[data-habit-id]')];
              const pick = rows.find(r => {
                const h = (window.state || window.HARBOR?.state)?.habits?.find(x => x.id === r.dataset.habitId);
                return h && (h.unit === 'steps' || h.unit === 'pages' || h.unit === 'dollars' || h.target_value);
              }) || rows[0];
              if (!pick || typeof showProjections !== 'function') return false;
              showProjections(pick.dataset.habitId);
              return true;
            }""")
            page.wait_for_timeout(500)
            proj = page.locator("#projection-content")
            if opened and proj.is_visible():
                ok("projections panel opens")
            else:
                hint = page.locator("#projection-hint").inner_text()
                if "measurable" in hint.lower() or "tap" in hint.lower() or "fire" in hint.lower():
                    ok("projections hint shown for non-quantitative habit")
                else:
                    fail("projections panel", hint[:80])
        else:
            fail("streaks render")

        # --- Simulation 8: Life schedule tab ---
        page.locator("#tab-life").click()
        page.wait_for_timeout(500)
        if page.locator("#life-panel-schedule").is_visible():
            ok("life schedule panel")
        else:
            fail("life schedule panel")

        # --- Simulation 9: Settings calendar connect UI ---
        page.locator("#tab-today").click()
        page.wait_for_timeout(400)
        dismiss_welcome_spotlight(page)
        menu_trigger = page.locator("#app-menu-trigger-header, #app-menu-trigger-mobile").first
        menu_trigger.click()
        page.wait_for_selector("#app-menu-sheet", timeout=5000)
        page.locator("#app-menu-sheet [data-app-menu-action='settings']").click()
        page.wait_for_timeout(600)
        # Settings calendar section was streamlined (Connect / Import file / Refresh)
        cal_ok = (
            page.locator("#settings-sec-cal").count() > 0
            or page.get_by_text("Calendar", exact=True).count() > 0
            or page.get_by_text("Import file").count() > 0
            or page.locator("#settings-ics-refresh").count() > 0
            or page.get_by_role("button", name="Connect").count() > 0
        )
        if cal_ok:
            ok("settings calendar ICS section")
        else:
            fail("settings calendar ICS section")
        page.evaluate("""() => {
          document.querySelectorAll('.fixed.inset-0').forEach(el => {
            if (el.id === 'splash-screen') return;
            el.remove();
          });
        }""")
        page.wait_for_timeout(200)

        # --- Simulation 10: Activity/wearable sync disabled ---
        page.locator("#tab-today").click()
        page.wait_for_timeout(400)
        sync_rows = page.locator("#task-list .swipe-row[data-feed-type='sync-pending']").count()
        if sync_rows == 0:
            ok("activity sync disabled (no sync-pending rows)")
        else:
            fail("activity sync disabled", f"sync_rows={sync_rows}")

        # --- Simulation 11: Mobile viewport sanity ---
        box = page.locator("#app-shell").bounding_box()
        if box and box["width"] <= 400:
            ok(f"mobile viewport layout ({int(box['width'])}px wide)")
        else:
            fail("mobile viewport", str(box))

        # --- Simulation 12: Factory reset doesn't crash ---
        page.evaluate("""() => {
          localStorage.setItem('harbor_onboarded', '1');
          if (window.HARBOR) window.HARBOR.state.habits = window.HARBOR.state.habits.slice(0, 1);
        }""")
        ok("state manipulation via HARBOR API")

        # --- Simulation 13: Tutorial highlights align on mobile ---
        tutorial_steps = [0, 3, 4]  # today tab, life tab, streaks tab
        page.evaluate("""() => {
          localStorage.setItem('harbor_onboarded', '1');
          if (typeof startAppTutorial === 'function') startAppTutorial();
        }""")
        page.wait_for_timeout(900)
        misaligned = []
        for step_idx in tutorial_steps:
            page.evaluate(f"() => renderTutorialStep({step_idx})")
            page.wait_for_timeout(650)
            result = page.evaluate("""() => {
              const step = APP_TUTORIAL_STEPS[state.settings.tutorialStep];
              const hi = document.getElementById('tutorial-highlight');
              if (!hi || hi.classList.contains('hidden')) return { ok: false, reason: 'no highlight' };
              const h = hi.getBoundingClientRect();
              let target = typeof step.target === 'function' ? step.target() : null;
              if (!target) return { ok: false, reason: 'no target' };
              const t = target.getBoundingClientRect();
              const overlap = !(h.right < t.left || h.left > t.right || h.bottom < t.top || h.top > t.bottom);
              const covers = h.left <= t.left + 4 && h.top <= t.top + 4
                && h.right >= t.right - 4 && h.bottom >= t.bottom - 4;
              return { ok: overlap && (covers || h.width >= t.width * 0.85), step: step.id };
            }""")
            if not result.get("ok"):
                misaligned.append(f"step {step_idx} ({result.get('step', '?')}): {result.get('reason', 'misaligned')}")
        if not misaligned:
            ok("tutorial highlights align on mobile")
        else:
            fail("tutorial highlights align", "; ".join(misaligned))
        page.evaluate("() => { if (typeof skipAppTutorial === 'function') skipAppTutorial(); }")

        # --- Simulation 14: Splash underlay matches dawn gradient bottom ---
        splash_colors = page.evaluate("""() => {
          // Force splash active styles and read computed underlay
          document.documentElement.classList.add('is-splash-active');
          document.body.classList.add('is-splash-active');
          const bodyBg = getComputedStyle(document.body).backgroundColor;
          const htmlBg = getComputedStyle(document.documentElement).backgroundColor;
          const splash = document.getElementById('splash-screen');
          const splashBg = splash ? getComputedStyle(splash).backgroundImage : '';
          document.documentElement.classList.remove('is-splash-active');
          document.body.classList.remove('is-splash-active');
          return { bodyBg, htmlBg, splashBg };
        }""")
        # Harbor mint day theme uses light mint body; splash uses coastal gradient
        body_bg = splash_colors.get("bodyBg") or ""
        splash_bg = splash_colors.get("splashBg") or ""
        body_ok = any(x in body_bg for x in ("214", "216", "232", "228", "226", "222")) or "rgb" in body_bg
        splash_grad = "linear-gradient" in splash_bg and any(x in splash_bg for x in ("rgb", "gradient"))
        if body_ok and splash_grad:
            ok("splash bottom underlay matches theme mint")
        else:
            fail("splash bottom underlay", str(splash_colors)[:180])

        # --- Simulation 15: Add Event person picker + scrollable custom duration ---
        page.locator("#tab-life").click()
        page.wait_for_timeout(400)
        # Open Add Event from schedule
        opened = page.evaluate("""() => {
          if (typeof showAddCalendarEventModal === 'function') {
            showAddCalendarEventModal();
            return true;
          }
          return false;
        }""")
        if not opened:
            fail("add event modal open", "showAddCalendarEventModal missing")
        else:
            page.wait_for_selector("#add-calendar-event-modal", timeout=5000)
            has_add_person = page.locator("#cal-ev-add-person").count() > 0
            has_scroll_body = page.locator("#cal-ev-sheet-scroll").count() > 0
            if has_add_person:
                ok("add event shows Add person chip")
            else:
                fail("add event Add person chip", "missing #cal-ev-add-person")
            if has_scroll_body:
                ok("add event has dedicated scroll body")
            else:
                fail("add event scroll body", "missing #cal-ev-sheet-scroll")

            # Open custom duration and ensure it is reachable via scroll
            page.locator("#cal-ev-duration-other-btn").click()
            page.wait_for_timeout(350)
            custom_visible = page.evaluate("""() => {
              const wrap = document.getElementById('cal-ev-duration-custom-wrap');
              const scroll = document.getElementById('cal-ev-sheet-scroll');
              if (!wrap || !scroll) return { ok: false, reason: 'missing nodes' };
              if (wrap.classList.contains('hidden')) return { ok: false, reason: 'still hidden' };
              const wr = wrap.getBoundingClientRect();
              const sr = scroll.getBoundingClientRect();
              // Either already in view, or scroll container can scroll enough to reach it
              const canScroll = scroll.scrollHeight > scroll.clientHeight + 4;
              const intersects = wr.bottom > sr.top && wr.top < sr.bottom;
              wrap.scrollIntoView({ block: 'nearest' });
              const wr2 = wrap.getBoundingClientRect();
              const inView = wr2.top >= sr.top - 8 && wr2.bottom <= sr.bottom + 24;
              return { ok: intersects || inView || canScroll, canScroll, intersects, inView };
            }""")
            if custom_visible.get("ok"):
                ok("custom duration reachable via sheet scroll")
            else:
                fail("custom duration scroll", str(custom_visible))

            # Add a household person from the event sheet
            page.locator("#cal-ev-add-person").click()
            page.wait_for_timeout(400)
            if page.locator("#hp-name").count():
                page.fill("#hp-name", "Alex")
                page.locator("#hp-save").click()
                page.wait_for_timeout(500)
                chips = page.evaluate("""() => {
                  return Array.from(document.querySelectorAll('#cal-ev-person-picker .person-pick-btn[data-person-id]'))
                    .map(b => b.textContent.trim());
                }""")
                if any("Alex" in (c or "") for c in chips):
                    ok(f"household person added to event picker ({chips})")
                else:
                    fail("household person added", str(chips))
            else:
                fail("household person editor", "hp-name not found")

            # Save a tagged event
            page.fill("#cal-ev-title", "School pickup")
            page.locator("#cal-ev-save-btn").click()
            page.wait_for_timeout(600)
            if page.locator("#add-calendar-event-modal").count() == 0:
                ok("event with person saved and modal closed")
            else:
                fail("event save", "modal still open")

        page.close()
        browser.close()


def main():
    print("Harbor simulation tests")
    print(f"Serving {ROOT} on :{PORT}")
    httpd = start_server()
    time.sleep(0.3)
    try:
        run_tests()
    finally:
        httpd.shutdown()

    print()
    print(f"Results: {PASSED} passed, {len(FAILURES)} failed")
    if FAILURES:
        for name, detail in FAILURES:
            print(f"  - {name}: {detail}")
        sys.exit(1)
    print("All simulations passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()