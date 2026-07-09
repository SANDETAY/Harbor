#!/usr/bin/env python3
"""Apply Harbor splash rewrite + remaining rebrand fixes to index.html."""

from pathlib import Path

path = Path(__file__).resolve().parent.parent / "index.html"
text = path.read_text(encoding="utf-8")

# --- 1) Reduced-motion splash block ---
old_rm = """      .splash-slogan.is-visible,
      .splash-slogan.is-exiting,
      .splash-screen-v3.is-revealing,
      .splash-slogan.is-visible .splash-slogan-lit,
      .splash-slogan.is-visible .splash-slogan-base,
      .splash-slogan.is-visible .splash-slogan-lit .splash-slogan-lead,
      .splash-slogan.is-visible .splash-slogan-lit .splash-slogan-accent,
      .splash-slogan.is-lit .splash-slogan-lit .splash-slogan-lead,
      .splash-slogan.is-lit .splash-slogan-lit .splash-slogan-accent,
      .app-content-wrap.splash-app-reveal {
        animation: none !important;
      }
      .splash-slogan.is-visible,
      .splash-slogan.is-lit { opacity: 1; transform: none; }
      .splash-slogan-base { opacity: 0.25; }
      .splash-slogan-lit { opacity: 1; }
      .splash-slogan-lit .splash-slogan-lead {
        background: none;
        color: var(--harbor-text);
        -webkit-text-fill-color: var(--harbor-text);
        filter: none;
      }
      .splash-slogan-lit .splash-slogan-accent {
        background: linear-gradient(90deg, #5BB8A8 0%, #3D9A8B 45%, #00C4A0 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 12px rgba(91, 184, 168, 0.45));
      }
      .splash-slogan.is-exiting { opacity: 0; transform: none; }
      .splash-screen-v3.is-revealing { opacity: 0; }
      .app-content-wrap.splash-app-reveal { opacity: 1; transform: none; }"""

new_rm = """      .splash-screen-harbor,
      .splash-screen-harbor.is-revealing,
      .splash-brand,
      .splash-mark,
      .splash-wordmark,
      .splash-slogan,
      .splash-wave-layer,
      .app-content-wrap.splash-app-reveal {
        animation: none !important;
      }
      .splash-screen-harbor { opacity: 1; }
      .splash-brand { opacity: 1; transform: none; }
      .splash-mark { transform: none; }
      .splash-slogan { opacity: 1; transform: none; }
      .splash-screen-harbor.is-revealing { opacity: 0; transform: none; }
      .app-content-wrap.splash-app-reveal { opacity: 1; transform: none; }
      .splash-wave-layer { opacity: 0.35; }"""

if old_rm not in text:
    # May already be patched or CSS comments changed
    if "splash-screen-harbor" not in text and "splash-screen-v3" in text:
        raise SystemExit("reduced-motion splash block not found")
    print("skip reduced-motion (already new or missing old)")
else:
    text = text.replace(old_rm, new_rm, 1)
    print("ok reduced-motion")

# --- 2) Old splash CSS block ---
markers = [
    "    /* ── Splash: black void + letter-shaped neon sweep L→R ── */",
    "    /* -- Splash: black void + letter-shaped neon sweep L->R -- */",
    "    /* ── Splash: black void",
]
start = -1
for m in markers:
    start = text.find(m)
    if start >= 0:
        break
if start < 0:
    # fuzzy: find neon splash section
    idx = text.find("Splash: black void")
    if idx >= 0:
        start = text.rfind("/*", 0, idx)
if start < 0 and "splash-screen-harbor" not in text:
    # find .splash-screen-v3 block
    idx = text.find(".splash-screen-v3 {")
    if idx >= 0:
        start = text.rfind("/*", 0, idx)
if start < 0:
    if "splash-screen-harbor" in text:
        print("skip splash css (already harbor)")
    else:
        raise SystemExit("splash css start not found")
else:
    end = text.find("    .header-day-stack {", start)
    if end < 0:
        raise SystemExit("splash css end not found")

    new_css = r"""    /* ── Splash: peaceful harbor at dawn ── */
    .splash-screen-harbor {
      overflow: hidden;
      will-change: opacity, transform;
      background: linear-gradient(180deg, #0a3a38 0%, #1a5c56 38%, #6a9e96 72%, #d8e4de 100%);
    }

    .splash-screen-harbor.is-hidden {
      display: none !important;
      pointer-events: none;
    }

    .splash-screen-harbor.is-active {
      animation: splashHarborFadeIn 480ms ease forwards;
    }

    .splash-screen-harbor.is-revealing {
      animation: splashHarborExit 580ms cubic-bezier(0.4, 0, 0.2, 1) forwards;
      pointer-events: none;
    }

    .splash-sky {
      position: absolute;
      inset: 0;
      pointer-events: none;
      background:
        radial-gradient(ellipse 90% 55% at 50% 18%, rgba(255, 236, 210, 0.22) 0%, transparent 58%),
        radial-gradient(ellipse 70% 40% at 70% 60%, rgba(180, 220, 210, 0.12) 0%, transparent 60%);
    }

    .splash-waves {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 38%;
      pointer-events: none;
      overflow: hidden;
    }

    .splash-wave-layer {
      position: absolute;
      left: -10%;
      width: 120%;
      height: 100%;
      opacity: 0.55;
    }

    .splash-wave-layer svg {
      display: block;
      width: 100%;
      height: 100%;
    }

    .splash-wave-layer.w1 {
      bottom: -6%;
      opacity: 0.28;
      animation: splashWaveDrift 14s linear infinite;
    }

    .splash-wave-layer.w2 {
      bottom: -2%;
      opacity: 0.38;
      animation: splashWaveDrift 10.5s linear infinite reverse;
    }

    .splash-wave-layer.w3 {
      bottom: 4%;
      opacity: 0.22;
      animation: splashWaveDrift 17s linear infinite;
    }

    #splash-inner {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      position: relative;
      z-index: 2;
      padding: 0 1.5rem 2rem;
      gap: 1.1rem;
    }

    .splash-brand {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.85rem;
      opacity: 0;
      transform: scale(0.82);
    }

    .splash-brand.is-in {
      animation: splashBrandSettle 900ms cubic-bezier(0.34, 1.45, 0.64, 1) forwards;
    }

    .splash-mark {
      width: 4.6rem;
      height: 4.6rem;
      color: #0d4f4a;
      filter: drop-shadow(0 4px 18px rgba(10, 50, 48, 0.28));
      animation: splashMarkBob 3.6s ease-in-out infinite;
    }

    .splash-mark svg {
      width: 100%;
      height: 100%;
      display: block;
    }

    .splash-wordmark {
      font-family: 'Space Grotesk', 'Inter', sans-serif;
      font-size: clamp(2.15rem, 7vw, 2.75rem);
      font-weight: 600;
      letter-spacing: 0.04em;
      line-height: 1;
      color: #f4efe6;
      text-shadow:
        0 0 18px rgba(244, 239, 230, 0.35),
        0 0 36px rgba(91, 184, 168, 0.18),
        0 2px 12px rgba(8, 30, 28, 0.25);
    }

    .splash-slogan {
      margin: 0;
      font-family: 'Space Grotesk', 'Inter', sans-serif;
      font-size: clamp(1.05rem, 3.4vw, 1.28rem);
      font-weight: 500;
      letter-spacing: 0.14em;
      text-transform: none;
      color: #e7ebe4;
      opacity: 0;
      transform: translateY(14px);
    }

    .splash-slogan.is-in {
      animation: splashSloganUp 720ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .app-content-wrap.splash-app-reveal {
      animation: splashAppIn 520ms ease forwards;
    }

    @keyframes splashHarborFadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes splashHarborExit {
      from { opacity: 1; transform: scale(1); }
      to { opacity: 0; transform: scale(0.96); }
    }

    @keyframes splashBrandSettle {
      0% { opacity: 0; transform: scale(0.78); }
      70% { opacity: 1; transform: scale(1.03); }
      100% { opacity: 1; transform: scale(1); }
    }

    @keyframes splashMarkBob {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-4px); }
    }

    @keyframes splashSloganUp {
      from { opacity: 0; transform: translateY(16px); }
      to { opacity: 0.95; transform: translateY(0); }
    }

    @keyframes splashWaveDrift {
      from { transform: translateX(0); }
      to { transform: translateX(-8%); }
    }

    @keyframes splashAppIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

"""
    text = text[:start] + new_css + text[end:]
    print("ok splash css")

# --- 3) Splash HTML ---
old_html_start = text.find("      <!-- Splash / Launch screen")
if old_html_start < 0:
    old_html_start = text.find('id="splash-screen"')
    if old_html_start >= 0:
        old_html_start = text.rfind("<div", 0, old_html_start)
        old_html_start = text.rfind("\n", 0, old_html_start) + 1
if old_html_start < 0:
    raise SystemExit("splash html not found")
old_html_end = text.find("      <!-- Onboarding (low-friction, first-run only) -->", old_html_start)
if old_html_end < 0:
    raise SystemExit("onboarding comment not found")

new_html = """      <!-- Splash / Launch screen — harbor at dawn -->
      <div id="splash-screen" class="absolute inset-0 z-[100] splash-screen-harbor" aria-hidden="true">
        <div class="splash-sky" aria-hidden="true"></div>
        <div class="splash-waves" aria-hidden="true">
          <div class="splash-wave-layer w1">
            <svg viewBox="0 0 1440 220" preserveAspectRatio="none" aria-hidden="true">
              <path fill="rgba(12,70,66,0.35)" d="M0,120 C240,160 480,70 720,110 C960,150 1200,90 1440,130 L1440,220 L0,220 Z"/>
            </svg>
          </div>
          <div class="splash-wave-layer w2">
            <svg viewBox="0 0 1440 220" preserveAspectRatio="none" aria-hidden="true">
              <path fill="rgba(232,240,236,0.28)" d="M0,140 C200,100 400,170 720,140 C1040,110 1240,160 1440,120 L1440,220 L0,220 Z"/>
            </svg>
          </div>
          <div class="splash-wave-layer w3">
            <svg viewBox="0 0 1440 220" preserveAspectRatio="none" aria-hidden="true">
              <path fill="rgba(20,90,84,0.22)" d="M0,150 C280,180 520,100 780,140 C1040,180 1260,120 1440,150 L1440,220 L0,220 Z"/>
            </svg>
          </div>
        </div>
        <div id="splash-inner">
          <div id="splash-brand" class="splash-brand">
            <div class="splash-mark" aria-hidden="true">
              <svg viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="64" cy="64" r="54" stroke="currentColor" stroke-width="4.5" opacity="0.9"/>
                <circle cx="64" cy="64" r="48" fill="currentColor" fill-opacity="0.1"/>
                <circle cx="64" cy="30" r="9" stroke="currentColor" stroke-width="5"/>
                <rect x="40" y="40" width="48" height="7" rx="3.5" fill="currentColor"/>
                <rect x="59.5" y="38" width="9" height="52" rx="4.5" fill="currentColor"/>
                <path d="M28 78c4 22 22 34 36 34s32-12 36-34" stroke="currentColor" stroke-width="8" stroke-linecap="round" fill="none"/>
                <path d="M28 78l-10-2 4-12z" fill="currentColor"/>
                <path d="M100 78l10-2-4-12z" fill="currentColor"/>
              </svg>
            </div>
            <div class="splash-wordmark">Harbor</div>
          </div>
          <p id="splash-slogan" class="splash-slogan">Find your harbor.</p>
        </div>
      </div>

"""
text = text[:old_html_start] + new_html + text[old_html_end:]
print("ok splash html")

# --- 4) runSplashSequence ---
old_fn_start = text.find("    function runSplashSequence(onComplete) {")
if old_fn_start < 0:
    raise SystemExit("runSplashSequence not found")
old_fn_end = text.find("    function formatHeaderDate(d = new Date()) {", old_fn_start)
if old_fn_end < 0:
    raise SystemExit("formatHeaderDate after splash not found")

new_fn = """    function runSplashSequence(onComplete) {
      const splash = document.getElementById('splash-screen');
      const brandEl = document.getElementById('splash-brand');
      const sloganEl = document.getElementById('splash-slogan');
      const appWrap = document.querySelector('.app-content-wrap');
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      // Soft dawn arrival → brand settle → slogan → gentle exit (~2.3s)
      const BRAND_MS = 200;
      const SLOGAN_MS = 780;
      const EXIT_AT = 2300;
      const REVEAL_MS = 580;

      if (splash) {
        splash.classList.remove('is-hidden', 'is-revealing');
        splash.classList.add('is-active');
        splash.style.display = 'block';
        splash.style.opacity = '';
        splash.style.clipPath = '';
        splash.style.pointerEvents = 'auto';
        splash.setAttribute('aria-hidden', 'false');
      }

      brandEl?.classList.remove('is-in');
      sloganEl?.classList.remove('is-in');
      appWrap?.classList.remove('splash-app-reveal');

      let booted = false;
      const finishBoot = () => {
        if (booted) return;
        booted = true;
        onComplete?.();
      };

      const startReveal = () => {
        splash?.classList.add('is-revealing');
        splash?.setAttribute('aria-hidden', 'true');
        appWrap?.classList.add('splash-app-reveal');
        finishBoot();
      };

      const cleanupSplash = () => {
        brandEl?.classList.remove('is-in');
        sloganEl?.classList.remove('is-in');
        hideSplash();
      };

      if (reducedMotion) {
        brandEl?.classList.add('is-in');
        sloganEl?.classList.add('is-in');
        setTimeout(startReveal, 380);
        setTimeout(cleanupSplash, 520);
        return;
      }

      requestAnimationFrame(() => {
        setTimeout(() => brandEl?.classList.add('is-in'), BRAND_MS);
        setTimeout(() => sloganEl?.classList.add('is-in'), SLOGAN_MS);
      });

      setTimeout(startReveal, EXIT_AT);
      setTimeout(cleanupSplash, EXIT_AT + REVEAL_MS);
    }

"""
text = text[:old_fn_start] + new_fn + text[old_fn_end:]
print("ok splash js")

# --- 5) hideSplash cleanup ---
old_hide = """      splash.classList.add('is-hidden');
      splash.classList.remove('is-revealing', 'is-active');
      splash.style.display = 'none';
      splash.style.opacity = '';
      splash.style.clipPath = '';
      splash.style.pointerEvents = 'none';
      document.querySelector('.app-content-wrap')?.classList.remove('splash-app-reveal');
"""
new_hide = """      splash.classList.add('is-hidden');
      splash.classList.remove('is-revealing', 'is-active');
      splash.style.display = 'none';
      splash.style.opacity = '';
      splash.style.clipPath = '';
      splash.style.pointerEvents = 'none';
      splash.setAttribute('aria-hidden', 'true');
      document.getElementById('splash-brand')?.classList.remove('is-in');
      document.getElementById('splash-slogan')?.classList.remove('is-in');
      document.querySelector('.app-content-wrap')?.classList.remove('splash-app-reveal');
"""
if old_hide in text:
    text = text.replace(old_hide, new_hide, 1)
    print("ok hideSplash")
else:
    print("skip hideSplash")

# --- 6) Misc brand strings ---
repls = [
    (">Brief</span>", ">Summary</span>"),
    ("// ==================== RHYTHM BRIEF ====================", "// ==================== SUMMARY ===================="),
    ("noreply@rhythm.app", "noreply@harbor.app"),
    ('aria-label="Brief range"', 'aria-label="Summary range"'),
    ("glowing <strong>Brief</strong> button", "glowing <strong>Summary</strong> button"),
    ("use daily briefs for day-of prioritization.", "use daily Summary for day-of prioritization."),
    (
        "console.log('%c[Harbor] Prototype ready. Habits + Life features live.', 'color:#166534');",
        "console.log('%c[Harbor] Prototype ready. Find your harbor.', 'color:#0F5C56');",
    ),
    ("<title>Harbor • Find Your Harbor</title>", "<title>Harbor · Find Your Harbor</title>"),
    ("/* Teal neon tube for \"Rhythm\"", '/* Teal neon tube for "Harbor"'),
]
for a, b in repls:
    if a in text:
        text = text.replace(a, b)
        print("replaced:", a[:48])
    else:
        print("skip:", a[:48])

# --- 7) Storage migration in loadState ---
old_load = """    function loadState() {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
"""
new_load = """    function loadState() {
      // Migrate legacy Rhythm local data → Harbor keys (one-time)
      try {
        if (!localStorage.getItem(STORAGE_KEY)) {
          const legacy = localStorage.getItem('rhythm_state_v1');
          if (legacy) localStorage.setItem(STORAGE_KEY, legacy);
        }
        if (!localStorage.getItem('harbor_onboarded') && localStorage.getItem('rhythm_onboarded')) {
          localStorage.setItem('harbor_onboarded', localStorage.getItem('rhythm_onboarded'));
        }
      } catch (_) { /* ignore */ }
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
"""
if old_load in text:
    text = text.replace(old_load, new_load, 1)
    print("ok loadState migration")
elif "rhythm_state_v1" in text and "Migrate legacy" in text:
    print("skip loadState (already migrated)")
else:
    print("WARN loadState block not found exactly")

old_onb = "return !!(state.settings?.onboarded || localStorage.getItem('harbor_onboarded'));"
new_onb = "return !!(state.settings?.onboarded || localStorage.getItem('harbor_onboarded') || localStorage.getItem('rhythm_onboarded'));"
if old_onb in text:
    text = text.replace(old_onb, new_onb, 1)
    print("ok onboarded dual-read")

# init() factory reset should also respect legacy storage
old_init_check = """      if (!localStorage.getItem(FACTORY_RESET_VERSION)) {
        const hasExistingData = localStorage.getItem(STORAGE_KEY);
        if (!hasExistingData) {
"""
new_init_check = """      if (!localStorage.getItem(FACTORY_RESET_VERSION)) {
        const hasExistingData = localStorage.getItem(STORAGE_KEY) || localStorage.getItem('rhythm_state_v1');
        if (!hasExistingData) {
"""
if old_init_check in text:
    text = text.replace(old_init_check, new_init_check, 1)
    print("ok init legacy data check")

path.write_text(text, encoding="utf-8", newline="\n")
print("WROTE", path, "chars", len(text))
