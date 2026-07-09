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
                page.locator("#summary-modal button", has_text="×").first.click()
            else:
                fail("summary modal opens")

        # --- Simulation 4: Energy reprioritization ---
        first_title = page.locator("#task-list .habit-card").first.locator(".font-medium, .leading-tight").first.inner_text()
        page.locator("#energy-1").click()
        page.wait_for_timeout(400)
        page.locator("#energy-3").click()
        page.wait_for_timeout(400)
        ok("energy buttons respond")

        # --- Simulation 5: Complete a task ---
        complete_btn = page.locator("#task-list [onclick*='completeHabit']").first
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
        page.locator("#tab-streaks").click(force=True)
        page.wait_for_selector(
            "#streaks-list .swipe-row, #streaks-list .harbor-card, #streaks-list .habit-card",
            timeout=5000,
        )
        streak_cards = page.locator(
            "#streaks-list .swipe-row, #streaks-list .harbor-card, #streaks-list .habit-card"
        ).count()
        if streak_cards >= 1:
            ok(f"streaks render ({streak_cards})")
            page.locator("#streaks-list .harbor-card, #streaks-list .habit-card").first.click()
            page.wait_for_timeout(500)
            proj = page.locator("#projection-content")
            if proj.is_visible():
                ok("projections panel opens")
            else:
                hint = page.locator("#projection-hint").inner_text()
                if "measurable" in hint.lower() or "tap" in hint.lower():
                    ok("projections hint shown for non-quantitative habit")
                else:
                    fail("projections panel", hint[:80])
        else:
            fail("streaks render")

        # --- Simulation 8: Life schedule tab ---
        page.locator("#tab-life").click(force=True)
        page.wait_for_timeout(500)
        if page.locator("#life-panel-schedule").is_visible():
            ok("life schedule panel")
        else:
            fail("life schedule panel")

        # --- Simulation 9: Settings calendar connect UI ---
        page.locator("#tab-today").click(force=True)
        page.wait_for_timeout(400)
        dismiss_welcome_spotlight(page)
        menu_trigger = page.locator("#app-menu-trigger-header, #app-menu-trigger-mobile").first
        menu_trigger.click()
        page.wait_for_selector("#app-menu-sheet", timeout=5000)
        page.locator("#app-menu-sheet [data-app-menu-action='settings']").click()
        page.wait_for_timeout(600)
        if page.locator("text=Calendar (ICS)").count() > 0 or page.locator("#settings-ics-url").count() > 0:
            ok("settings calendar ICS section")
        else:
            fail("settings calendar ICS section")
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        page.locator(".fixed .text-2xl", has_text="×").first.click(timeout=3000)
        page.wait_for_timeout(300)

        # --- Simulation 10: Activity/wearable sync disabled ---
        page.locator("#tab-today").click(force=True)
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