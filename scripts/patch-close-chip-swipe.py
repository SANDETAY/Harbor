#!/usr/bin/env python3
"""Replace modal × close buttons with Close chips; add swipe-down-to-dismiss."""

from pathlib import Path
import re

path = Path(__file__).resolve().parent.parent / "index.html"
text = path.read_text(encoding="utf-8")
n = 0


def replace_once(old: str, new: str, label: str) -> None:
    global text, n
    if old not in text:
        raise SystemExit(f"FAIL: {label}")
    text = text.replace(old, new, 1)
    n += 1
    print(f"ok {label}")


def replace_all(old: str, new: str, label: str) -> None:
    global text, n
    c = text.count(old)
    if c == 0:
        print(f"skip {label} (0)")
        return
    text = text.replace(old, new)
    n += 1
    print(f"ok {label} ({c})")


# ── CSS ──────────────────────────────────────────────────────────────────────
CSS_ANCHOR = """    .modal-grab-pill {
      width: 2.5rem;
      height: 0.25rem;
      border-radius: 999px;
      background: rgb(var(--harbor-border));
      margin: 0 auto 0.75rem;
    }"""

CSS_NEW = """    .modal-grab-pill {
      width: 2.5rem;
      height: 0.25rem;
      border-radius: 999px;
      background: rgb(var(--harbor-border));
      margin: 0 auto 0.75rem;
      flex-shrink: 0;
      touch-action: none;
    }

    /* Stylish small close control (replaces × on sheets) */
    .modal-close-chip {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      padding: 0.28rem 0.72rem;
      min-height: 1.55rem;
      border-radius: 999px;
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: rgba(200, 214, 210, 0.78);
      background: rgba(18, 28, 34, 0.55);
      border: 1px solid rgba(143, 184, 176, 0.22);
      box-shadow: 0 1px 0 rgba(255, 255, 255, 0.04) inset;
      transition: color 0.15s ease, background 0.15s ease, border-color 0.15s ease, transform 0.12s ease;
      line-height: 1;
      font-family: inherit;
      cursor: pointer;
    }

    .modal-close-chip:hover,
    .modal-close-chip:focus-visible {
      color: #f0f5f3;
      border-color: rgba(107, 191, 176, 0.45);
      background: rgba(47, 155, 140, 0.16);
      outline: none;
    }

    .modal-close-chip:active {
      transform: scale(0.97);
      background: rgba(47, 155, 140, 0.22);
    }

    html[data-theme="dark"] .modal-close-chip {
      color: rgba(220, 220, 220, 0.78);
      background: rgba(255, 255, 255, 0.06);
      border-color: rgba(255, 255, 255, 0.12);
    }

    /* Sheet swipe-to-dismiss */
    .sheet-swipe-target {
      will-change: transform;
      touch-action: pan-y;
    }

    .sheet-swipe-target.is-sheet-dragging {
      transition: none !important;
      user-select: none;
    }

    .sheet-swipe-target.is-sheet-dismissing {
      transition: transform 0.28s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.28s ease !important;
      pointer-events: none;
    }

    .sheet-backdrop-dim {
      transition: opacity 0.2s ease;
    }"""

replace_once(CSS_ANCHOR, CSS_NEW, "css close chip + swipe")

replace_once("const HARBOR_BUILD = 'v102';", "const HARBOR_BUILD = 'v103';", "build bump")

CLOSE_REPLACEMENTS = [
    (
        'class="text-harbor-muted text-2xl leading-none">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'class="text-harbor-muted text-2xl leading-none px-1" aria-label="Close">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'class="text-harbor-muted text-2xl leading-none px-1">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'class="text-harbor-muted text-2xl leading-none" aria-label="Close">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'class="w-8 h-8 rounded-full bg-harbor-raised text-harbor-muted text-xl leading-none">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'class="w-8 h-8 rounded-full bg-harbor-raised text-harbor-muted hover:text-harbor-text text-xl leading-none">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'class="w-8 h-8 rounded-full bg-harbor-raised text-harbor-muted text-xl leading-none" aria-label="Close">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'class="flex-shrink-0 text-harbor-muted text-2xl leading-none px-2 py-1 rounded-lg active:bg-harbor-raised" aria-label="Close weather">×</button>',
        'class="modal-close-chip flex-shrink-0" aria-label="Close weather">Close</button>',
    ),
    (
        'class="text-harbor-muted text-xl px-2">×</button>',
        'class="modal-close-chip" aria-label="Close">Close</button>',
    ),
    (
        'data-weather-dismiss="1" class="text-harbor-muted text-2xl leading-none px-1" aria-label="Close">×</button>',
        'data-weather-dismiss="1" class="modal-close-chip" aria-label="Close">Close</button>',
    ),
]

for old, new in CLOSE_REPLACEMENTS:
    replace_all(old, new, f"close: {old[:48]}")

JS_ANCHOR = """    function closeSummaryModal() {
      document.getElementById('summary-modal')?.remove();
    }"""

JS_BLOCK = r'''    function closeSummaryModal() {
      document.getElementById('summary-modal')?.remove();
    }

    // ==================== SHEET SWIPE-TO-DISMISS ====================
    function findSheetPanel(overlay) {
      if (!overlay) return null;
      return overlay.querySelector(
        '.summary-sheet, .summary-day-events-sheet, .modal-sheet, .app-menu-sheet-panel, [data-weather-sheet], [data-sheet-panel]'
      ) || Array.from(overlay.children).find(el =>
        el.classList && !el.classList.contains('absolute') && el !== overlay
      ) || null;
    }

    function dismissBottomSheet(overlay) {
      if (!overlay || !overlay.isConnected) return;
      const id = overlay.id || '';

      if (id === 'summary-modal' || overlay.querySelector?.('#summary-body')) {
        closeSummaryModal();
        return;
      }
      if (id === 'summary-day-events-modal') {
        closeSummaryDayEventsModal();
        return;
      }
      if (id === 'app-menu-sheet' || overlay.classList.contains('app-menu-sheet')) {
        if (typeof closeAppMenu === 'function') closeAppMenu();
        else overlay.remove();
        return;
      }
      if (id === 'weather-forecast-modal' || id === 'weather-access-modal' || overlay.classList.contains('weather-access-modal')) {
        if (typeof closeWeatherModal === 'function') closeWeatherModal();
        else overlay.remove();
        return;
      }
      if (id === 'add-calendar-event-modal' || id === 'grocery-add-modal' || id === 'feedback-modal' ||
          id === 'device-sync-modal' || id === 'schedule-import-modal' || id === 'household-profiles-modal') {
        overlay.remove();
        return;
      }
      if (typeof settingsWasOpen !== 'undefined' && overlay.querySelector?.('#dark-mode-toggle, #cheat-fund-toggle, #smart-suggestions-toggle')) {
        settingsWasOpen = false;
      }
      if (typeof closeQuickTaskModal === 'function' && overlay.id === 'quick-task-modal') {
        closeQuickTaskModal();
        return;
      }
      if (typeof closeAddBillModal === 'function' && overlay.id === 'add-bill-modal') {
        try { closeAddBillModal(); return; } catch (_) { /* fall through */ }
      }
      if (typeof closeWorkScheduleModal === 'function' && overlay.id === 'work-schedule-modal') {
        try { closeWorkScheduleModal(); return; } catch (_) { /* fall through */ }
      }

      const backdrop = overlay.querySelector(':scope > .absolute.inset-0, :scope > [data-weather-dismiss]');
      if (backdrop) {
        const handler = backdrop.getAttribute('onclick');
        if (handler) {
          try {
            new Function(handler).call(backdrop);
            if (!overlay.isConnected) return;
          } catch (_) { /* ignore */ }
        }
        backdrop.click();
        if (!overlay.isConnected) return;
      }

      const chip = overlay.querySelector('.modal-close-chip');
      if (chip) {
        chip.click();
        if (!overlay.isConnected) return;
      }

      overlay.remove();
    }

    function animateSheetDismiss(overlay, sheet, onDone) {
      if (!sheet) {
        onDone();
        return;
      }
      sheet.classList.add('is-sheet-dismissing');
      sheet.style.transform = `translate3d(0, ${Math.max(sheet.offsetHeight || 400, 400)}px, 0)`;
      sheet.style.opacity = '0.85';
      const backdrop = overlay.querySelector(':scope > .absolute.inset-0, :scope > [data-weather-dismiss="1"]');
      if (backdrop) {
        backdrop.classList.add('sheet-backdrop-dim');
        backdrop.style.opacity = '0';
      }
      let done = false;
      const finish = () => {
        if (done) return;
        done = true;
        sheet.removeEventListener('transitionend', finish);
        onDone();
      };
      sheet.addEventListener('transitionend', finish);
      setTimeout(finish, 320);
    }

    function wireSheetSwipeToDismiss(overlay) {
      if (!overlay || overlay.nodeType !== 1) return;
      if (overlay.dataset.sheetSwipeBound === '1') return;
      if (!overlay.classList.contains('fixed')) return;

      const sheet = findSheetPanel(overlay);
      if (!sheet) return;

      const looksLikeSheet =
        sheet.classList.contains('summary-sheet') ||
        sheet.classList.contains('modal-sheet') ||
        sheet.classList.contains('summary-day-events-sheet') ||
        sheet.classList.contains('app-menu-sheet-panel') ||
        sheet.hasAttribute('data-weather-sheet') ||
        sheet.hasAttribute('data-sheet-panel') ||
        /rounded-t-3xl|border-t/.test(sheet.className || '');
      if (!looksLikeSheet) return;

      overlay.dataset.sheetSwipeBound = '1';
      sheet.classList.add('sheet-swipe-target');

      let startY = 0;
      let startX = 0;
      let dragging = false;
      let decided = false;
      let dy = 0;
      let pointerId = null;

      const getScrollTop = () => {
        if (sheet.scrollTop > 0) return sheet.scrollTop;
        const scroller = sheet.querySelector('.overflow-y-auto');
        return scroller ? scroller.scrollTop : 0;
      };

      const resetSheet = () => {
        sheet.classList.remove('is-sheet-dragging');
        sheet.style.transition = 'transform 0.22s cubic-bezier(0.32, 0.72, 0, 1)';
        sheet.style.transform = '';
        sheet.style.opacity = '';
        const backdrop = overlay.querySelector(':scope > .absolute.inset-0, :scope > [data-weather-dismiss="1"]');
        if (backdrop) backdrop.style.opacity = '';
        setTimeout(() => {
          if (sheet.isConnected) sheet.style.transition = '';
        }, 240);
      };

      const cleanup = () => {
        sheet.removeEventListener('pointermove', onPointerMove);
        sheet.removeEventListener('pointerup', onPointerUp);
        sheet.removeEventListener('pointercancel', onPointerUp);
        pointerId = null;
        dragging = false;
        decided = false;
      };

      const onPointerMove = (e) => {
        if (pointerId != null && e.pointerId !== pointerId) return;
        const rawDy = e.clientY - startY;
        const rawDx = e.clientX - startX;

        if (!decided) {
          if (Math.abs(rawDy) < 8 && Math.abs(rawDx) < 8) return;
          decided = true;
          if (Math.abs(rawDx) > Math.abs(rawDy) * 1.15) {
            cleanup();
            return;
          }
          if (rawDy < 0) {
            cleanup();
            return;
          }
          if (getScrollTop() > 2 && !e.target.closest('.modal-grab-pill')) {
            cleanup();
            return;
          }
          dragging = true;
          sheet.classList.add('is-sheet-dragging');
        }

        if (!dragging) return;
        e.preventDefault();
        dy = Math.max(0, rawDy);
        const resisted = dy < 120 ? dy : 120 + (dy - 120) * 0.35;
        sheet.style.transform = `translate3d(0, ${resisted}px, 0)`;
        const backdrop = overlay.querySelector(':scope > .absolute.inset-0, :scope > [data-weather-dismiss="1"]');
        if (backdrop) {
          backdrop.style.opacity = String(Math.max(0.25, 1 - resisted / 420));
        }
      };

      const onPointerUp = (e) => {
        if (pointerId != null && e.pointerId !== pointerId) return;
        const wasDragging = dragging;
        const finalDy = dy;
        cleanup();
        sheet.classList.remove('is-sheet-dragging');
        if (!wasDragging) {
          resetSheet();
          return;
        }
        const threshold = Math.min(140, Math.max(88, (sheet.offsetHeight || 300) * 0.18));
        if (finalDy >= threshold) {
          animateSheetDismiss(overlay, sheet, () => dismissBottomSheet(overlay));
        } else {
          resetSheet();
        }
        dy = 0;
      };

      const onPointerDown = (e) => {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        if (e.target.closest('input, textarea, select, button, a, [role="switch"], [role="tab"], .person-pick-btn')) {
          return;
        }
        const grab = e.target.closest('.modal-grab-pill, .summary-dash-head, .app-menu-sheet-title');
        const scrollTop = getScrollTop();
        if (!grab && scrollTop > 2) return;

        startY = e.clientY;
        startX = e.clientX;
        dragging = false;
        decided = false;
        dy = 0;
        pointerId = e.pointerId;
        try { sheet.setPointerCapture(e.pointerId); } catch (_) { /* ignore */ }
        sheet.addEventListener('pointermove', onPointerMove);
        sheet.addEventListener('pointerup', onPointerUp);
        sheet.addEventListener('pointercancel', onPointerUp);
      };

      sheet.addEventListener('pointerdown', onPointerDown);
    }

    function enhanceNewOverlays(root) {
      if (!root || root.nodeType !== 1) return;
      if (root.classList?.contains('fixed')) wireSheetSwipeToDismiss(root);
      root.querySelectorAll?.('.fixed').forEach(wireSheetSwipeToDismiss);
    }

    function installSheetSwipeObserver() {
      if (window.__harborSheetSwipeObserver) return;
      const scan = () => {
        document.querySelectorAll('.fixed').forEach(el => {
          if (/inset-0/.test(el.className) || el.classList.contains('app-menu-sheet') || el.classList.contains('weather-access-modal')) {
            wireSheetSwipeToDismiss(el);
          }
        });
      };
      window.__harborSheetSwipeObserver = new MutationObserver((mutations) => {
        for (const m of mutations) {
          m.addedNodes.forEach(node => {
            if (node.nodeType !== 1) return;
            enhanceNewOverlays(node);
          });
        }
      });
      window.__harborSheetSwipeObserver.observe(document.body, { childList: true, subtree: false });
      scan();
      setTimeout(scan, 0);
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', installSheetSwipeObserver);
    } else {
      installSheetSwipeObserver();
    }
'''

replace_once(JS_ANCHOR, JS_BLOCK, "swipe-to-dismiss JS")

# SW cache
sw_path = path.parent / "sw.js"
if sw_path.exists():
    sw = sw_path.read_text(encoding="utf-8")
    if "harbor-preview-v102" in sw:
        sw_path.write_text(sw.replace("harbor-preview-v102", "harbor-preview-v103"), encoding="utf-8")
        print("ok sw cache v103")

remaining = []
for i, line in enumerate(text.splitlines(), 1):
    if ">×</button>" not in line and ">×</button>" not in line:
        # also catch × with different encoding
        if "×</button>" not in line:
            continue
    if re.search(r"remove|delete|Remove|Delete|hp-del|cal-delete|title=\"Delete|aria-label=\"Remove", line, re.I):
        continue
    remaining.append(f"{i}:{line.strip()[:140]}")

path.write_text(text, encoding="utf-8")
print(f"\nWROTE {path} patches={n} chars={len(text)}")
print(f"remaining non-delete × buttons: {len(remaining)}")
for r in remaining[:25]:
    print(" ", r)
