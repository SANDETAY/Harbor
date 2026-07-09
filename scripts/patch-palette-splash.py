#!/usr/bin/env python3
"""Fix splash flash, apply dawn-harbor palette, tidy dead CSS, bump to v74."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "index.html"
text = path.read_text(encoding="utf-8")

# ── 1) Color tokens (tailwind + :root) ──────────────────────────────────────
old_tw = """            harbor: {
              bg: '#0F1419',
              surface: '#1A2332',
              raised: '#232F42',
              border: '#2A3544',
              primary: '#3D9A8B',
              'primary-light': '#5BB8A8',
              accent: '#5B8FD9',
              text: '#E8EDF2',
              muted: '#8B9BB0',
              low: '#D4836A',
              med: '#C9A227',
              high: '#3D9A8B',
            }"""

new_tw = """            harbor: {
              bg: '#0A1F1E',
              surface: '#122E2C',
              raised: '#1A3C39',
              border: '#2A4F4A',
              primary: '#2F9B8C',
              'primary-light': '#6BBFB0',
              accent: '#C4A574',
              text: '#F0EBE3',
              muted: '#8FA8A3',
              low: '#D4927A',
              med: '#D4B56A',
              high: '#2F9B8C',
            }"""

if old_tw not in text:
    raise SystemExit("tailwind harbor colors not found")
text = text.replace(old_tw, new_tw, 1)
print("ok tailwind colors")

old_root = """    :root {
      --harbor-bg: #0F1419;
      --harbor-surface: #1A2332;
      --harbor-raised: #232F42;
      --harbor-border: #2A3544;
      --harbor-primary: #3D9A8B;
      --harbor-primary-light: #5BB8A8;
      --harbor-accent: #5B8FD9;
      --harbor-text: #E8EDF2;
      --harbor-muted: #8B9BB0;
      --harbor-low: #D4836A;
      --harbor-med: #C9A227;
      --harbor-high: #3D9A8B;
      --harbor-ease-out: cubic-bezier(0.32, 0.72, 0, 1);
      --harbor-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
      --harbor-shadow-sm: 0 1px 0 rgba(255, 255, 255, 0.05) inset, 0 4px 16px rgba(0, 0, 0, 0.18);
      --harbor-shadow-md: 0 1px 0 rgba(255, 255, 255, 0.06) inset, 0 10px 32px rgba(0, 0, 0, 0.28);
      --harbor-glow-primary: 0 0 0 1px rgba(91, 184, 168, 0.25);
      --safe-bottom: env(safe-area-inset-bottom, 0px);
      --safe-top: env(safe-area-inset-top, 0px);
    }"""

new_root = """    :root {
      /* Dawn-harbor palette — deep teal water, warm stone light */
      --harbor-bg: #0A1F1E;
      --harbor-surface: #122E2C;
      --harbor-raised: #1A3C39;
      --harbor-border: #2A4F4A;
      --harbor-primary: #2F9B8C;
      --harbor-primary-light: #6BBFB0;
      --harbor-accent: #C4A574;
      --harbor-text: #F0EBE3;
      --harbor-muted: #8FA8A3;
      --harbor-low: #D4927A;
      --harbor-med: #D4B56A;
      --harbor-high: #2F9B8C;
      --harbor-ease-out: cubic-bezier(0.32, 0.72, 0, 1);
      --harbor-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
      --harbor-shadow-sm: 0 1px 0 rgba(255, 255, 255, 0.04) inset, 0 4px 18px rgba(4, 22, 20, 0.32);
      --harbor-shadow-md: 0 1px 0 rgba(255, 255, 255, 0.05) inset, 0 12px 36px rgba(4, 22, 20, 0.42);
      --harbor-glow-primary: 0 0 0 1px rgba(107, 191, 176, 0.22);
      --harbor-dawn: #0A3A38;
      --safe-bottom: env(safe-area-inset-bottom, 0px);
      --safe-top: env(safe-area-inset-top, 0px);
    }"""

if old_root not in text:
    raise SystemExit(":root tokens not found")
text = text.replace(old_root, new_root, 1)
print("ok :root tokens")

# Meta theme-color
text = text.replace('content="#0F1419"', 'content="#0A1F1E"')
text = text.replace("setAttribute('content', '#0F1419')", "setAttribute('content', '#0A1F1E')")
print("ok theme-color")

# Site header gradient (was cool blue-gray)
text = text.replace(
    "background: linear-gradient(180deg, rgba(20, 27, 38, 0.92) 0%, rgba(15, 20, 25, 0.88) 100%);",
    "background: linear-gradient(180deg, rgba(18, 46, 44, 0.94) 0%, rgba(10, 31, 30, 0.9) 100%);",
)
# Other cool charcoal leftovers used as overlays
text = text.replace("rgba(15, 20, 25,", "rgba(10, 31, 30,")
text = text.replace("rgba(15,20,25,", "rgba(10,31,30,")

# Hardcoded accent blue → warm dawn accent where product-branded
text = text.replace("color: #5B8FD9;", "color: var(--harbor-accent);")
text = text.replace(
    "background: linear-gradient(90deg, #5BB8A8 0%, #3D9A8B 50%, #5B8FD9 100%);",
    "background: linear-gradient(90deg, #6BBFB0 0%, #2F9B8C 55%, #C4A574 100%);",
)

# Summary orb teal hardcodes → slightly warmer harbor teals (keep structure)
text = text.replace("rgba(91, 184, 168,", "rgba(107, 191, 176,")
text = text.replace("rgba(61, 154, 139,", "rgba(47, 155, 140,")

# Console color
text = text.replace("'color:#0F5C56'", "'color:#2F9B8C'")

# Build bump
text = text.replace("HARBOR_BUILD = 'v73'", "HARBOR_BUILD = 'v74'")
text = text.replace("HARBOR_BUILD = 'v72'", "HARBOR_BUILD = 'v74'")

# ── 2) Fix splash flash ─────────────────────────────────────────────────────
# Remove full-screen fade-in (that flash is dark app showing through opacity:0).
# Splash paints solid from first frame; only brand/slogan animate in.
# App chrome stays hidden until exit.

old_splash_css_start = text.find("    /* ── Splash: peaceful harbor at dawn ── */")
if old_splash_css_start < 0:
    raise SystemExit("splash css marker missing")
old_splash_css_end = text.find("    .header-day-stack {", old_splash_css_start)
if old_splash_css_end < 0:
    raise SystemExit("splash css end missing")

new_splash_css = r"""    /* ── Splash: peaceful harbor at dawn ── */
    /* Full-screen cover from first paint — never fade the shell in from 0
       (that caused a dark app flash). Only brand + slogan animate. */
    .splash-screen-harbor {
      overflow: hidden;
      will-change: opacity, transform;
      background: linear-gradient(180deg, #0a3a38 0%, #1a5c56 38%, #6a9e96 72%, #d8e4de 100%);
      opacity: 1;
      transform: none;
    }

    .splash-screen-harbor.is-hidden {
      display: none !important;
      pointer-events: none;
    }

    .splash-screen-harbor.is-revealing {
      animation: splashHarborExit 560ms cubic-bezier(0.4, 0, 0.2, 1) forwards;
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
        0 0 36px rgba(107, 191, 176, 0.18),
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

    /* Hide chrome only while splash is up (never leave app stuck at opacity 0) */
    body.is-splash-active .app-content-wrap {
      opacity: 0;
    }

    body.is-splash-active .site-header {
      opacity: 0;
      pointer-events: none;
    }

    body.is-splash-active {
      background-color: var(--harbor-dawn, #0A3A38);
    }

    .app-content-wrap.splash-app-reveal {
      animation: splashAppIn 480ms ease forwards;
    }

    @keyframes splashHarborExit {
      from { opacity: 1; transform: scale(1); }
      to { opacity: 0; transform: scale(0.97); }
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
text = text[:old_splash_css_start] + new_splash_css + text[old_splash_css_end:]
print("ok splash css rewrite")

# Reduced-motion block — drop is-active fade-in refs, keep harbor rules
old_rm = """      .splash-screen-harbor,
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
      .splash-screen-harbor { opacity: 1; transform: none; }
      .splash-brand { opacity: 1; transform: none; }
      .splash-mark { transform: none; }
      .splash-slogan { opacity: 1; transform: none; }
      .splash-screen-harbor.is-revealing { opacity: 0; transform: none; }
      .app-content-wrap.splash-app-reveal { opacity: 1; transform: none; }
      .splash-wave-layer { opacity: 0.35; }
      body.is-splash-active .app-content-wrap { opacity: 1; }
      body.is-splash-active .site-header { opacity: 1; pointer-events: auto; }"""

if old_rm in text:
    text = text.replace(old_rm, new_rm, 1)
    print("ok reduced-motion")
else:
    print("WARN reduced-motion block not exact")

# Remove dead Rhythm lockup CSS (no HTML uses it)
dead_lockup = """    .harbor-logo {
      display: block;
      flex-shrink: 0;
      object-fit: contain;
    }

    .harbor-wordmark {
      display: block;
      object-fit: contain;
    }

    .harbor-title {
      font-family: 'Space Grotesk', sans-serif;
      letter-spacing: -0.03em;
      line-height: 1;
      background: linear-gradient(90deg, #6BBFB0 0%, #2F9B8C 55%, #C4A574 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    /* R icon + "ythm" butted together reads as one word */
    .harbor-lockup {
      display: flex;
      align-items: flex-end;
      gap: 0;
      line-height: 1;
    }

    .harbor-lockup .harbor-logo {
      height: 2.35rem;
      width: auto;
      margin-right: -0.12rem;
      margin-bottom: 0.12rem;
    }

    .harbor-lockup .harbor-title {
      font-size: 2rem;
      font-weight: 600;
      margin-left: 0.15rem;
      padding-right: 0.35rem;
      letter-spacing: 0.1em;
      transform: translateY(5px);
    }

    .harbor-lockup .harbor-title .ltr-y { color: #5BB8A8; -webkit-text-fill-color: #5BB8A8; }
    .harbor-lockup .harbor-title .ltr-t { color: #4AAB9A; -webkit-text-fill-color: #4AAB9A; }
    .harbor-lockup .harbor-title .ltr-h { color: #3D9A8B; -webkit-text-fill-color: #3D9A8B; }
    .harbor-lockup .harbor-title .ltr-m { color: #5B8FD9; -webkit-text-fill-color: #5B8FD9; }

"""
# Try with original blue gradient if palette replace didn't hit this block yet
dead_lockup_orig = """    .harbor-logo {
      display: block;
      flex-shrink: 0;
      object-fit: contain;
    }

    .harbor-wordmark {
      display: block;
      object-fit: contain;
    }

    .harbor-title {
      font-family: 'Space Grotesk', sans-serif;
      letter-spacing: -0.03em;
      line-height: 1;
      background: linear-gradient(90deg, #5BB8A8 0%, #3D9A8B 50%, #5B8FD9 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    /* R icon + "ythm" butted together reads as one word */
    .harbor-lockup {
      display: flex;
      align-items: flex-end;
      gap: 0;
      line-height: 1;
    }

    .harbor-lockup .harbor-logo {
      height: 2.35rem;
      width: auto;
      margin-right: -0.12rem;
      margin-bottom: 0.12rem;
    }

    .harbor-lockup .harbor-title {
      font-size: 2rem;
      font-weight: 600;
      margin-left: 0.15rem;
      padding-right: 0.35rem;
      letter-spacing: 0.1em;
      transform: translateY(5px);
    }

    .harbor-lockup .harbor-title .ltr-y { color: #5BB8A8; -webkit-text-fill-color: #5BB8A8; }
    .harbor-lockup .harbor-title .ltr-t { color: #4AAB9A; -webkit-text-fill-color: #4AAB9A; }
    .harbor-lockup .harbor-title .ltr-h { color: #3D9A8B; -webkit-text-fill-color: #3D9A8B; }
    .harbor-lockup .harbor-title .ltr-m { color: #5B8FD9; -webkit-text-fill-color: #5B8FD9; }

"""
if dead_lockup in text:
    text = text.replace(dead_lockup, "", 1)
    print("ok removed dead lockup CSS (new colors)")
elif dead_lockup_orig in text:
    text = text.replace(dead_lockup_orig, "", 1)
    print("ok removed dead lockup CSS (orig)")
else:
    # fuzzy remove harbor-lockup block
    m = re.search(
        r"\n    \.harbor-logo \{.*?\n    \.harbor-lockup \.harbor-title \.ltr-m \{[^}]+\}\n\n",
        text,
        re.S,
    )
    if m:
        text = text[: m.start()] + "\n" + text[m.end() :]
        print("ok removed dead lockup CSS (fuzzy)")
    else:
        print("WARN could not remove lockup CSS")

# ── 3) Splash JS: no is-active fade, body class, keep content hidden ────────
old_fn_start = text.find("    function runSplashSequence(onComplete) {")
old_fn_end = text.find("    function formatHeaderDate(d = new Date()) {", old_fn_start)
if old_fn_start < 0 or old_fn_end < 0:
    raise SystemExit("runSplashSequence not found")

new_fn = """    function runSplashSequence(onComplete) {
      const splash = document.getElementById('splash-screen');
      const brandEl = document.getElementById('splash-brand');
      const sloganEl = document.getElementById('splash-slogan');
      const appWrap = document.querySelector('.app-content-wrap');
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      // Brand settle → slogan → soft exit. Shell stays fully opaque (no fade-in flash).
      const BRAND_MS = 120;
      const SLOGAN_MS = 700;
      const EXIT_AT = 2200;
      const REVEAL_MS = 560;

      document.body.classList.add('is-splash-active');

      if (splash) {
        splash.classList.remove('is-hidden', 'is-revealing');
        splash.style.display = 'block';
        splash.style.opacity = '1';
        splash.style.clipPath = '';
        splash.style.pointerEvents = 'auto';
        splash.setAttribute('aria-hidden', 'false');
      }

      brandEl?.classList.remove('is-in');
      sloganEl?.classList.remove('is-in');
      appWrap?.classList.remove('splash-app-reveal');
      // Keep chrome hidden until reveal so nothing flashes under the splash
      if (appWrap) appWrap.style.opacity = '0';

      let booted = false;
      const finishBoot = () => {
        if (booted) return;
        booted = true;
        onComplete?.();
      };

      const startReveal = () => {
        splash?.classList.add('is-revealing');
        splash?.setAttribute('aria-hidden', 'true');
        if (appWrap) {
          appWrap.style.opacity = '';
          appWrap.classList.add('splash-app-reveal');
        }
        document.body.classList.remove('is-splash-active');
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
        setTimeout(startReveal, 280);
        setTimeout(cleanupSplash, 420);
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

# hideSplash: clear body class + ensure app visible
old_hide = """    function hideSplash() {
      const splash = document.getElementById('splash-screen');
      if (!splash) return;
      splash.classList.add('is-hidden');
      splash.classList.remove('is-revealing', 'is-active');
      splash.style.display = 'none';
      splash.style.opacity = '';
      splash.style.clipPath = '';
      splash.style.pointerEvents = 'none';
      splash.setAttribute('aria-hidden', 'true');
      document.getElementById('splash-brand')?.classList.remove('is-in');
      document.getElementById('splash-slogan')?.classList.remove('is-in');
      document.querySelector('.app-content-wrap')?.classList.remove('splash-app-reveal');
    }"""

new_hide = """    function hideSplash() {
      const splash = document.getElementById('splash-screen');
      if (!splash) return;
      splash.classList.add('is-hidden');
      splash.classList.remove('is-revealing', 'is-active');
      splash.style.display = 'none';
      splash.style.opacity = '';
      splash.style.clipPath = '';
      splash.style.pointerEvents = 'none';
      splash.setAttribute('aria-hidden', 'true');
      document.getElementById('splash-brand')?.classList.remove('is-in');
      document.getElementById('splash-slogan')?.classList.remove('is-in');
      document.body.classList.remove('is-splash-active');
      const appWrap = document.querySelector('.app-content-wrap');
      if (appWrap) {
        appWrap.classList.remove('splash-app-reveal');
        appWrap.style.opacity = '';
      }
    }"""

if old_hide in text:
    text = text.replace(old_hide, new_hide, 1)
    print("ok hideSplash")
else:
    # softer match
    if "function hideSplash()" in text and "is-splash-active" not in text[text.find("function hideSplash()") : text.find("function hideSplash()") + 800]:
        print("WARN hideSplash block mismatch — attempting partial")
        text = text.replace(
            "splash.classList.remove('is-revealing', 'is-active');",
            "splash.classList.remove('is-revealing', 'is-active');\n      document.body.classList.remove('is-splash-active');",
            1,
        )
    else:
        print("skip hideSplash")

# Ensure .app-content-wrap base rule doesn't fight — we set opacity:0 in splash section,
# but there's also earlier .app-content-wrap { flex... }. The later opacity:0 rule is in
# splash CSS before .header-day-stack; there may be a second .app-content-wrap later.
# Make sure after splash the app is visible: default after hide is opacity ''.

# Tidy: collapse 3+ blank lines to 2
text = re.sub(r"\n{4,}", "\n\n\n", text)

path.write_text(text, encoding="utf-8", newline="\n")
print("WROTE index.html", len(text))

# ── companion files ─────────────────────────────────────────────────────────
manifest = ROOT / "manifest.webmanifest"
if manifest.exists():
    m = manifest.read_text(encoding="utf-8")
    m2 = m.replace("#0F1419", "#0A1F1E").replace("#000000", "#0A1F1E")
    if m2 != m:
        manifest.write_text(m2, encoding="utf-8", newline="\n")
        print("ok manifest")

sw = ROOT / "sw.js"
if sw.exists():
    s = sw.read_text(encoding="utf-8")
    s2 = re.sub(r"harbor-preview-v\d+", "harbor-preview-v74", s)
    if s2 != s:
        sw.write_text(s2, encoding="utf-8", newline="\n")
        print("ok sw.js v74")

for name, pairs in [
    ("mobile.html", [("#0a0e12", "#0A1F1E"), ("#0c1014", "#081716"), ("#3d9a8b", "#2F9B8C"), ("#1a222b", "#122E2C"), ("#8a9aa3", "#8FA8A3"), ("#e8eef0", "#F0EBE3")]),
    ("dual-preview.html", [("#0a0e12", "#0A1F1E"), ("#121820", "#122E2C"), ("#243039", "#2A4F4A"), ("#8a9aa3", "#8FA8A3"), ("#3d9a8b", "#2F9B8C"), ("#e8eef0", "#F0EBE3"), ("#2a3440", "#1A3C39"), ("#0c1014", "#081716")]),
]:
    fp = ROOT / name
    if not fp.exists():
        continue
    t = fp.read_text(encoding="utf-8")
    orig = t
    for a, b in pairs:
        t = t.replace(a, b)
    if t != orig:
        fp.write_text(t, encoding="utf-8", newline="\n")
        print("ok", name)

print("DONE")
