#!/usr/bin/env python3
"""Fix modal bleed-through, subscription cancel UX, platform install picker."""

from pathlib import Path

path = Path(__file__).resolve().parent.parent / "index.html"
text = path.read_text(encoding="utf-8")
n = 0


def once(old, new, label):
    global text, n
    if old not in text:
        raise SystemExit(f"FAIL: {label}")
    text = text.replace(old, new, 1)
    n += 1
    print("ok", label)


# ── 1) Global modal layering CSS ────────────────────────────────────────────
CSS_ANCHOR = """    .modal-overlay-blur {
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
    }"""

CSS_NEW = """    .modal-overlay-blur {
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
    }

    /*
     * Harbor modal stacking — app chrome sits at z~50–55 (header, FAB).
     * Every body-level full-screen overlay must sit well above that with a
     * solid scrim so weather / tabs never “show through”.
     */
    body > .fixed.inset-0 {
      z-index: 300 !important;
    }
    body > .fixed.inset-0.modal-overlay-blur,
    body > .fixed.inset-0[class*="bg-harbor-bg"] {
      background-color: rgba(6, 14, 14, 0.88) !important;
    }
    html[data-theme="dark"] body > .fixed.inset-0.modal-overlay-blur,
    html[data-theme="dark"] body > .fixed.inset-0[class*="bg-harbor-bg"] {
      background-color: rgba(0, 0, 0, 0.9) !important;
    }
    /* Keep day-events sheet above Summary when both open */
    body > #summary-day-events-modal {
      z-index: 320 !important;
    }
    body > #summary-modal {
      z-index: 300 !important;
    }
    body.harbor-modal-open #site-root {
      pointer-events: none !important;
    }
    body.harbor-modal-open .summary-orb {
      visibility: hidden !important;
      pointer-events: none !important;
    }

    .platform-pick-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.45rem;
    }
    @media (min-width: 420px) {
      .platform-pick-grid { grid-template-columns: 1fr 1fr 1fr; }
    }
    .platform-pick-btn {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 0.2rem;
      text-align: left;
      padding: 0.65rem 0.7rem;
      border-radius: 0.85rem;
      border: 1px solid rgb(var(--harbor-border));
      background: rgb(var(--harbor-raised));
      color: rgb(var(--harbor-text));
      font-size: 0.72rem;
      font-weight: 650;
      line-height: 1.25;
      transition: border-color 0.12s ease, background 0.12s ease;
    }
    .platform-pick-btn:hover,
    .platform-pick-btn:active {
      border-color: rgba(107, 191, 176, 0.45);
      background: rgba(47, 155, 140, 0.12);
    }
    .platform-pick-btn i {
      color: rgb(var(--harbor-primary-light));
      font-size: 0.95rem;
      margin-bottom: 0.15rem;
    }
    .platform-pick-btn .platform-pick-sub {
      font-size: 0.58rem;
      font-weight: 500;
      color: rgb(var(--harbor-muted));
    }
    .platform-pick-btn .platform-pick-badge {
      font-size: 0.52rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: rgb(var(--harbor-primary-light));
      margin-top: 0.15rem;
    }
    .sub-cancel-choice {
      display: block;
      width: 100%;
      text-align: left;
      padding: 0.85rem 1rem;
      border-radius: 1rem;
      border: 1px solid rgb(var(--harbor-border));
      background: rgb(var(--harbor-raised));
      margin-bottom: 0.5rem;
    }
    .sub-cancel-choice:active {
      background: rgba(47, 155, 140, 0.12);
      border-color: rgba(107, 191, 176, 0.4);
    }
    .sub-cancel-choice .sub-cancel-title {
      font-size: 0.88rem;
      font-weight: 700;
      color: rgb(var(--harbor-text));
    }
    .sub-cancel-choice .sub-cancel-desc {
      font-size: 0.68rem;
      color: rgb(var(--harbor-muted));
      margin-top: 0.2rem;
      line-height: 1.35;
    }
    .sub-tracked-cancel {
      font-size: 0.65rem;
      font-weight: 700;
      color: #fca5a5;
      letter-spacing: 0.02em;
    }
    .sub-tracked-cancel:active {
      color: #fecaca;
    }"""

once(CSS_ANCHOR, CSS_NEW, "modal stacking + platform/sub CSS")

# ── 2) Build bump ───────────────────────────────────────────────────────────
once("const HARBOR_BUILD = 'v115';", "const HARBOR_BUILD = 'v116';", "build")

# ── 3) Add manageUrl to subscription presets (one by one) ───────────────────
PRESET_URLS = [
    ("id: 'netflix'", "https://www.netflix.com/cancelplan"),
    ("id: 'spotify'", "https://www.spotify.com/account/subscription/"),
    ("id: 'disney-plus'", "https://www.disneyplus.com/account"),
    ("id: 'hulu'", "https://secure.hulu.com/account"),
    ("id: 'max'", "https://auth.max.com/product"),
    ("id: 'youtube-premium'", "https://www.youtube.com/paid_memberships"),
    ("id: 'apple-one'", "https://www.apple.com/account/subscriptions/"),
    ("id: 'icloud'", "https://www.icloud.com/settings/"),
    ("id: 'amazon-prime'", "https://www.amazon.com/gp/primecentral"),
    ("id: 'microsoft-365'", "https://account.microsoft.com/services"),
    ("id: 'adobe'", "https://account.adobe.com/plans"),
    ("id: 'gym'", "https://www.google.com/search?q=cancel+gym+membership"),
    ("id: 'peacock'", "https://www.peacocktv.com/account"),
    ("id: 'paramount'", "https://www.paramountplus.com/account/"),
    ("id: 'dropbox'", "https://www.dropbox.com/account"),
    ("id: 'chatgpt'", "https://chatgpt.com/#settings"),
    ("id: 'claude'", "https://claude.ai/settings"),
    ("id: 'grok'", "https://x.com/settings"),
]

for key, url in PRESET_URLS:
    # insert manageUrl after id line in object: id: 'x', name:
    # pattern: id: 'netflix', name:
    old = None
    # Find the preset start
    marker = f"{{ {key}, name:"
    if marker not in text:
        marker = f"{{\n        {key}, name:"
    if marker not in text:
        # try without space after {
        idx = text.find(key)
        if idx < 0:
            print("skip preset", key)
            continue
        # insert after id line
        line_end = text.find("\n", idx)
        line = text[idx:line_end]
        if "manageUrl" in text[idx:idx+200]:
            print("skip already", key)
            continue
        text = text[:line_end] + f",\n        manageUrl: '{url}'" + text[line_end:]
        n += 1
        print("ok url", key)
    else:
        if f"manageUrl: '{url}'" in text:
            print("skip already", key)
            continue
        text = text.replace(marker, marker.replace(key + ", name:", key + f",\n        manageUrl: '{url}', name:"), 1)
        n += 1
        print("ok url", key)

# Fix botched replacements - read a sample
# Actually the replace might be wrong. Let me check after write.

# ── 4) Subscription add unshift + cancel flow ───────────────────────────────
once(
    """      state.subscriptions.push({
        id: 'sub-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6),
        name,
        amount: amount || 0,
        cycle: cycle || 'monthly',
        renewalDay: Math.min(31, Math.max(1, renewalDay || 1)),
        active: true,
        source: source || 'manual',
        presetId: presetId || null,
        tierId: tierId || null,
        tierLabel: tierLabel || null
      });
      saveState();
      renderSubscriptions();
      return true;
    }""",
    """      state.subscriptions.unshift({
        id: 'sub-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6),
        name,
        amount: amount || 0,
        cycle: cycle || 'monthly',
        renewalDay: Math.min(31, Math.max(1, renewalDay || 1)),
        active: true,
        source: source || 'manual',
        presetId: presetId || null,
        tierId: tierId || null,
        tierLabel: tierLabel || null,
        addedAt: new Date().toISOString()
      });
      saveState();
      renderSubscriptions();
      // Keep newly added sub visible at top of the tracked list
      requestAnimationFrame(() => {
        const list = document.getElementById('subscriptions-list');
        if (list) list.scrollTop = 0;
        document.getElementById('life-panel-subscriptions')?.scrollIntoView({ block: 'start' });
      });
      return true;
    }""",
    "add sub unshift",
)

once(
    """    function toggleSubscriptionActive(subId) {
      const sub = state.subscriptions.find(s => s.id === subId);
      if (!sub) return;
      const wasActive = sub.active !== false;
      sub.active = !wasActive;

      if (wasActive) {
        createSubscriptionCancelTask(sub);
        showToast(`Cancel reminder added to Today`);
      } else {
        removeSubscriptionCancelTask(sub);
        showToast(`Resumed ${sub.name}`);
      }

      saveState();
      renderSubscriptions();
      renderTasks();
      renderStreaks();
      updateSmartBanner();
    }""",
    """    function getSubscriptionManageUrl(sub) {
      if (!sub) return null;
      if (sub.manageUrl) return sub.manageUrl;
      const preset = resolveSubscriptionPreset(sub);
      if (preset?.manageUrl) return preset.manageUrl;
      // Safe fallback: search only (no auto-open of random domains)
      const q = encodeURIComponent(`cancel ${sub.name} subscription`);
      return `https://www.google.com/search?q=${q}`;
    }

    function openSubscriptionManageUrl(sub) {
      const url = getSubscriptionManageUrl(sub);
      if (!url) {
        showToast('No cancel page on file for this service', 'warn');
        return false;
      }
      // Open in a new tab — never send credentials; user completes cancel on the provider’s site
      window.open(url, '_blank', 'noopener,noreferrer');
      return true;
    }

    function showCancelSubscriptionModal(subId) {
      const sub = state.subscriptions.find(s => s.id === subId);
      if (!sub) return;
      const preset = resolveSubscriptionPreset(sub);
      const manageUrl = getSubscriptionManageUrl(sub);
      const host = (() => {
        try { return new URL(manageUrl).hostname.replace(/^www\\./, ''); } catch { return 'the provider’s site'; }
      })();

      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-harbor-bg/80 modal-overlay-blur flex items-end z-[300] harbor-modal-overlay';
      modal.innerHTML = `
        <div class="absolute inset-0" data-close="1"></div>
        <div class="modal-sheet relative w-full bg-harbor-surface border-t border-harbor-border rounded-t-3xl p-5 text-sm" onclick="event.stopPropagation()">
          <div class="modal-grab-pill" aria-hidden="true"></div>
          <div class="font-semibold text-lg mb-1 flex items-center justify-between gap-2">
            <span>Cancel ${escapeSubscriptionHtml(sub.name)}?</span>
            <button type="button" class="modal-close-chip" data-close="1" aria-label="Close">Close</button>
          </div>
          <div class="text-[11px] text-harbor-muted mb-4 leading-snug">
            Harbor never cancels for you and never sends your login. You finish on the provider’s site — your choice, your privacy.
          </div>
          <button type="button" class="sub-cancel-choice" data-cancel-now="1">
            <div class="sub-cancel-title"><i class="fa-solid fa-arrow-up-right-from-square text-rose-300 mr-1.5"></i>Cancel now</div>
            <div class="sub-cancel-desc">Opens <strong class="text-harbor-text">${escapeSubscriptionHtml(host)}</strong> in a new tab so you can cancel in your account. We’ll mark it inactive here.</div>
          </button>
          <button type="button" class="sub-cancel-choice" data-cancel-later="1">
            <div class="sub-cancel-title"><i class="fa-regular fa-clock text-amber-300 mr-1.5"></i>Schedule later</div>
            <div class="sub-cancel-desc">Adds a “Cancel ${escapeSubscriptionHtml(sub.name)}” task to Today so you remember without leaving Harbor yet.</div>
          </button>
          <button type="button" class="w-full py-3 rounded-2xl bg-harbor-raised border border-harbor-border text-harbor-muted font-semibold mt-1" data-close="1">Keep subscription</button>
        </div>`;
      document.body.appendChild(modal);
      document.body.classList.add('harbor-modal-open');

      const close = () => {
        modal.remove();
        if (!document.querySelector('.fixed.inset-0')) document.body.classList.remove('harbor-modal-open');
      };
      modal.querySelectorAll('[data-close]').forEach(el => el.addEventListener('click', close));
      modal.querySelector('[data-cancel-now]')?.addEventListener('click', () => {
        openSubscriptionManageUrl(sub);
        sub.active = false;
        removeSubscriptionCancelTask(sub);
        saveState();
        renderSubscriptions();
        renderTasks();
        updateSmartBanner();
        close();
        showToast(`Opened cancel page · ${sub.name} marked inactive`);
      });
      modal.querySelector('[data-cancel-later]')?.addEventListener('click', () => {
        createSubscriptionCancelTask(sub);
        sub.active = false;
        saveState();
        renderSubscriptions();
        renderTasks();
        updateSmartBanner();
        close();
        showToast(`Cancel reminder added to Today`);
      });
    }

    function toggleSubscriptionActive(subId) {
      // Kept for older UI hooks — prefer showCancelSubscriptionModal
      showCancelSubscriptionModal(subId);
    }""",
    "cancel subscription modal",
)

once(
    """            <button onclick="toggleSubscriptionActive('${sub.id}')" class="sub-tracked-pause mt-0.5">${active ? 'Pause' : 'Resume'}</button>""",
    """            <button type="button" onclick="event.stopPropagation(); ${active ? `showCancelSubscriptionModal('${sub.id}')` : `resumeSubscription('${sub.id}')`}" class="sub-tracked-cancel mt-0.5">${active ? 'Cancel' : 'Resume'}</button>""",
    "cancel button in card",
)

# Add resumeSubscription before removeSubscription
once(
    """    function removeSubscription(subId) {
      if (!confirm('Remove this subscription?')) return;""",
    """    function resumeSubscription(subId) {
      const sub = state.subscriptions.find(s => s.id === subId);
      if (!sub) return;
      sub.active = true;
      removeSubscriptionCancelTask(sub);
      saveState();
      renderSubscriptions();
      renderTasks();
      updateSmartBanner();
      showToast(`Resumed ${sub.name}`);
    }

    function removeSubscription(subId) {
      if (!confirm('Remove this subscription?')) return;""",
    "resumeSubscription",
)

# Sort newest first when rendering
once(
    """      const filteredSubs = subs.filter(s => trackedSubscriptionMatchesSearch(s, subscriptionSearchQuery));

      if (subs.length === 0) {""",
    """      const filteredSubs = subs
        .filter(s => trackedSubscriptionMatchesSearch(s, subscriptionSearchQuery))
        .slice()
        .sort((a, b) => {
          const ta = a.addedAt || '';
          const tb = b.addedAt || '';
          if (ta && tb) return tb.localeCompare(ta);
          return String(b.id || '').localeCompare(String(a.id || ''));
        });

      if (subs.length === 0) {""",
    "sort subs newest first",
)

# ── 5) Rewrite showAddToHomeScreenGuide with platform picker ────────────────
# Find and replace the whole function from "function showAddToHomeScreenGuide" to next function openAppMenuSheet

start = text.find("    function showAddToHomeScreenGuide(options = {}) {")
end = text.find("    function openAppMenuSheet() {")
if start < 0 or end < 0:
    raise SystemExit("FAIL: cannot locate showAddToHomeScreenGuide bounds")

NEW_GUIDE = r'''    function showAddToHomeScreenGuide(options = {}) {
      closeAppMenu();
      const already = !!options.alreadyInstalled || isHarborRunningStandalone();
      const canNative = !!options.canRetryNative || canNativePwaInstall();
      const preselect = options.platformId || null;

      const PLATFORMS = [
        {
          id: 'auto',
          name: 'This browser',
          sub: 'Try one-tap when available',
          icon: 'fa-bolt',
          native: true,
          steps: [
            'If your browser supports it, Harbor can open the official “Add to Home Screen” dialog — no app store, no extra download.',
            'Tap <strong>Add to home screen</strong> below when you see it.',
            'Confirm in the system prompt. Your data stays on this device; Harbor never receives a copy of your logins.'
          ]
        },
        {
          id: 'chrome-android',
          name: 'Chrome',
          sub: 'Android',
          icon: 'fa-chrome',
          native: true,
          steps: [
            'Open Harbor in <strong>Chrome</strong> on Android.',
            'Tap <strong>Add to home screen</strong> in Harbor (or Chrome menu ⋮ → <strong>Add to Home screen</strong> / <strong>Install app</strong>).',
            'You’re only pinning a <strong>shortcut</strong> — not installing a Play Store package. Confirm, then open the new icon for full-screen Harbor.'
          ]
        },
        {
          id: 'chrome-desktop',
          name: 'Chrome',
          sub: 'Windows / Mac / Linux',
          icon: 'fa-chrome',
          native: true,
          steps: [
            'Open Harbor in <strong>Chrome</strong> on your computer.',
            'Use Harbor’s <strong>Add to home screen</strong> button, or the install icon in the address bar, or menu ⋮ → <strong>Install Harbor</strong> / <strong>Cast, save, and share</strong> → Install.',
            'Harbor opens in its own window without the browser toolbar.'
          ]
        },
        {
          id: 'edge',
          name: 'Microsoft Edge',
          sub: 'Windows / Mac / Android',
          icon: 'fa-edge',
          native: true,
          steps: [
            'Open Harbor in <strong>Edge</strong>.',
            'Tap Harbor’s install button if shown, or menu ⋯ → <strong>Apps</strong> → <strong>Install this site as an app</strong>.',
            'Confirm install. Edge uses the same secure web-app prompt as Chromium — no extra account required.'
          ]
        },
        {
          id: 'brave',
          name: 'Brave',
          sub: 'Mobile / Desktop',
          icon: 'fa-shield-halved',
          native: true,
          steps: [
            'Open Harbor in <strong>Brave</strong>.',
            'Use Harbor’s one-tap button when available, or menu → <strong>Install</strong> / <strong>Add to Home screen</strong>.',
            'Brave is Chromium-based; install is a local shortcut only.'
          ]
        },
        {
          id: 'samsung',
          name: 'Samsung Internet',
          sub: 'Galaxy phones',
          icon: 'fa-mobile-screen',
          native: true,
          steps: [
            'Open Harbor in <strong>Samsung Internet</strong>.',
            'Menu → <strong>Add page to</strong> → <strong>Home screen</strong>, or use Harbor’s button if your browser offers a prompt.',
            'Open from the home screen for a full-screen experience.'
          ]
        },
        {
          id: 'opera',
          name: 'Opera',
          sub: 'Mobile / Desktop',
          icon: 'fa-opera',
          native: true,
          steps: [
            'Open Harbor in <strong>Opera</strong>.',
            'Menu → <strong>Add to</strong> → <strong>Home screen</strong> (mobile) or look for <strong>Install</strong> on desktop.',
            'Confirm — this only creates a shortcut to this page on your device.'
          ]
        },
        {
          id: 'safari-ios',
          name: 'Safari',
          sub: 'iPhone / iPad',
          icon: 'fa-safari',
          native: false,
          steps: [
            'Open Harbor in <strong>Safari</strong> (not Chrome-on-iOS — Apple requires Safari for home-screen apps).',
            'Tap <strong>Share</strong> (square with ↑).',
            'Scroll and tap <strong>Add to Home Screen</strong>, then <strong>Add</strong>.',
            'Apple does not allow websites to do this with one automatic tap — the Share sheet is the secure, official path.'
          ]
        },
        {
          id: 'safari-mac',
          name: 'Safari',
          sub: 'Mac',
          icon: 'fa-safari',
          native: false,
          steps: [
            'Open Harbor in <strong>Safari</strong> on Mac.',
            'File → <strong>Add to Dock</strong> (macOS Sonoma+) or Share → <strong>Add to Dock</strong> when available.',
            'On older macOS, bookmark Harbor or use Chrome/Edge install if you prefer a windowed app.'
          ]
        },
        {
          id: 'firefox-android',
          name: 'Firefox',
          sub: 'Android',
          icon: 'fa-firefox-browser',
          native: false,
          steps: [
            'Open Harbor in <strong>Firefox</strong> on Android.',
            'Menu ⋮ → <strong>Install</strong> or <strong>Add to Home screen</strong> (wording varies by version).',
            'Firefox may not support the same one-tap prompt as Chrome; the menu path is normal and private to your device.'
          ]
        },
        {
          id: 'firefox-desktop',
          name: 'Firefox',
          sub: 'Desktop',
          icon: 'fa-firefox-browser',
          native: false,
          steps: [
            'Desktop Firefox has limited “install site as app” support compared with Chrome/Edge.',
            'Bookmark Harbor, or use Chrome/Edge if you want a dedicated app window.',
            'Your Harbor data still stays in the browser profile you use — nothing is uploaded to us.'
          ]
        },
        {
          id: 'duckduckgo',
          name: 'DuckDuckGo',
          sub: 'Mobile browser',
          icon: 'fa-dove',
          native: false,
          steps: [
            'Open Harbor in the <strong>DuckDuckGo</strong> browser.',
            'Menu → <strong>Add to Home</strong> / <strong>Add to Home Screen</strong> (label varies).',
            'DuckDuckGo does not always expose the Chromium install prompt; the menu path keeps the process under your control.'
          ]
        }
      ];

      const modal = document.createElement('div');
      modal.id = 'install-guide-modal';
      modal.className = 'fixed inset-0 bg-harbor-bg/85 modal-overlay-blur flex items-end harbor-modal-overlay';
      modal.innerHTML = `
        <div class="absolute inset-0" data-ig-close="1"></div>
        <div class="modal-sheet relative w-full bg-harbor-surface border-t border-harbor-border rounded-t-3xl p-5 text-sm max-h-[92vh] overflow-y-auto" data-ig-sheet="1">
          <div class="modal-grab-pill" aria-hidden="true"></div>
          <div class="font-semibold text-lg mb-1 flex items-center justify-between gap-2">
            <span>Add to Home Screen</span>
            <button type="button" class="modal-close-chip" data-ig-close="1" aria-label="Close">Close</button>
          </div>
          <div class="text-[11px] text-harbor-muted mb-3 leading-snug">
            Harbor is local-first: pinning to your home screen only creates a shortcut on <strong class="text-harbor-text">your</strong> device. We never get your passwords or a remote install agent.
          </div>
          <div id="ig-view-root"></div>
        </div>`;
      document.body.appendChild(modal);
      document.body.classList.add('harbor-modal-open');

      const root = modal.querySelector('#ig-view-root');
      const close = () => {
        modal.remove();
        if (!document.querySelector('body > .fixed.inset-0')) document.body.classList.remove('harbor-modal-open');
      };
      modal.querySelectorAll('[data-ig-close]').forEach(el => el.addEventListener('click', close));
      modal.querySelector('[data-ig-sheet]')?.addEventListener('click', (e) => e.stopPropagation());

      const renderPicker = () => {
        root.innerHTML = `
          ${already ? `
            <div class="privacy-block mb-3">
              <h4><i class="fa-solid fa-circle-check text-harbor-primary-light mr-1.5"></i>Already on this device</h4>
              <p>Harbor looks like it’s running as an installed app. You can still review platform steps below if you need them on another device.</p>
            </div>` : canNative ? `
            <button type="button" id="ig-native-btn"
              class="w-full mb-3 py-3.5 rounded-2xl bg-harbor-primary text-white font-semibold text-sm active:opacity-90">
              <i class="fa-solid fa-mobile-screen-button mr-1.5"></i>Add to home screen (this browser)
            </button>
            <div class="text-[10px] text-harbor-muted text-center mb-3 -mt-1 leading-snug">
              Official browser prompt when supported — shortcut only, no store download.
            </div>` : ''}
          <div class="text-xs font-semibold text-harbor-text mb-2">Select your platform</div>
          <div class="platform-pick-grid mb-3">
            ${PLATFORMS.map(p => `
              <button type="button" class="platform-pick-btn" data-platform="${p.id}">
                <i class="fa-brands ${p.icon} ${p.icon.startsWith('fa-') && !p.icon.includes('chrome') && !p.icon.includes('safari') && !p.icon.includes('firefox') && !p.icon.includes('edge') && !p.icon.includes('opera') ? '' : ''}"></i>
                <span>${p.name}</span>
                <span class="platform-pick-sub">${p.sub}</span>
                ${p.native ? '<span class="platform-pick-badge">One-tap when available</span>' : '<span class="platform-pick-sub">Manual steps</span>'}
              </button>
            `).join('')}
          </div>
          <div class="privacy-block">
            <h4><i class="fa-solid fa-shield-halved text-harbor-primary-light mr-1.5"></i>Privacy</h4>
            <p>Harbor never auto-installs without your confirmation. One-tap only uses your browser’s built-in prompt. Manual steps stay entirely on your phone.</p>
          </div>
          <button type="button" class="w-full mt-4 py-3 rounded-2xl bg-harbor-raised border border-harbor-border text-harbor-muted font-semibold" data-ig-close="1">Close</button>
        `;
        // Fix icons that aren't brands
        root.querySelectorAll('.platform-pick-btn i').forEach(icon => {
          const btn = icon.closest('[data-platform]');
          const id = btn?.dataset?.platform;
          const map = {
            auto: 'fa-solid fa-bolt',
            brave: 'fa-solid fa-shield-halved',
            samsung: 'fa-solid fa-mobile-screen',
            duckduckgo: 'fa-solid fa-dove',
            'chrome-android': 'fa-brands fa-chrome',
            'chrome-desktop': 'fa-brands fa-chrome',
            edge: 'fa-brands fa-edge',
            'safari-ios': 'fa-brands fa-safari',
            'safari-mac': 'fa-brands fa-safari',
            'firefox-android': 'fa-brands fa-firefox-browser',
            'firefox-desktop': 'fa-brands fa-firefox-browser',
            opera: 'fa-brands fa-opera'
          };
          if (map[id]) icon.className = map[id];
        });

        root.querySelector('#ig-native-btn')?.addEventListener('click', async () => {
          close();
          await promptPwaInstall({ forceGuide: false });
        });
        root.querySelectorAll('[data-platform]').forEach(btn => {
          btn.addEventListener('click', () => renderDetail(btn.dataset.platform));
        });
        root.querySelectorAll('[data-ig-close]').forEach(el => el.addEventListener('click', close));
      };

      const renderDetail = (platformId) => {
        const p = PLATFORMS.find(x => x.id === platformId) || PLATFORMS[0];
        const showNative = p.native && canNativePwaInstall() && !already;
        root.innerHTML = `
          <button type="button" id="ig-back" class="text-[11px] text-harbor-primary-light font-semibold mb-3">
            <i class="fa-solid fa-arrow-left mr-1"></i>All platforms
          </button>
          <div class="font-semibold text-base text-harbor-text mb-0.5">${p.name}</div>
          <div class="text-[11px] text-harbor-muted mb-3">${p.sub}</div>
          ${showNative ? `
            <button type="button" id="ig-native-btn"
              class="w-full mb-3 py-3 rounded-2xl bg-harbor-primary text-white font-semibold text-sm">
              Add to home screen (secure browser prompt)
            </button>
          ` : ''}
          <div class="privacy-block mb-3">
            <h4>Steps</h4>
            <ol class="tutorial-install-steps" style="padding-left:1.1rem;margin:0.35rem 0 0">
              ${p.steps.map(s => `<li style="margin-bottom:0.4rem">${s}</li>`).join('')}
            </ol>
          </div>
          <div class="privacy-block mb-3">
            <h4><i class="fa-solid fa-shield-halved text-harbor-primary-light mr-1.5"></i>Secure by design</h4>
            <p>No Harbor server performs the install. Any one-tap action is your browser asking you to confirm a local shortcut.</p>
          </div>
          <button type="button" class="w-full py-3 rounded-2xl bg-harbor-raised border border-harbor-border text-harbor-muted font-semibold" data-ig-close="1">Close</button>
        `;
        root.querySelector('#ig-back')?.addEventListener('click', renderPicker);
        root.querySelector('#ig-native-btn')?.addEventListener('click', async () => {
          close();
          await promptPwaInstall({ forceGuide: false });
        });
        root.querySelectorAll('[data-ig-close]').forEach(el => el.addEventListener('click', close));
      };

      if (preselect) renderDetail(preselect);
      else renderPicker();
    }

'''

text = text[:start] + NEW_GUIDE + text[end:]
n += 1
print("ok install guide rewrite")

# ── 6) Helper to mark body when any modal opens — patch appendChild patterns is too broad
# Instead ensure promptPwaInstall uses guide which sets harbor-modal-open

# Update promptPwaInstall forceGuide path already calls showAddToHomeScreenGuide

# ── 7) SW cache ─────────────────────────────────────────────────────────────
sw = path.parent / "sw.js"
if sw.exists():
    swt = sw.read_text(encoding="utf-8")
    if "harbor-preview-v115" in swt:
        sw.write_text(swt.replace("harbor-preview-v115", "harbor-preview-v116"), encoding="utf-8")
        print("ok sw")
    elif "harbor-preview-v116" not in swt:
        # try bump from any
        import re
        swt2 = re.sub(r"harbor-preview-v\d+", "harbor-preview-v116", swt, count=1)
        sw.write_text(swt2, encoding="utf-8")
        print("ok sw re")

path.write_text(text, encoding="utf-8")
print(f"\nWROTE patches~={n} chars={len(text)}")

# Verify manageUrl
import re
urls = re.findall(r"manageUrl: '([^']+)'", text)
print("manageUrls", len(urls), urls[:5])
