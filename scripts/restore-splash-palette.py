#!/usr/bin/env python3
"""Restore splash dawn-harbor palette and fix CSS vars for Tailwind opacity."""
from pathlib import Path
import re

path = Path(__file__).resolve().parent.parent / "index.html"
t = path.read_text(encoding="utf-8")

# --- Tailwind: use RGB channels so /20 opacity works ---
old_tw = """            harbor: {
              bg: 'var(--harbor-bg)',
              surface: 'var(--harbor-surface)',
              raised: 'var(--harbor-raised)',
              border: 'var(--harbor-border)',
              primary: 'var(--harbor-primary)',
              'primary-light': 'var(--harbor-primary-light)',
              accent: 'var(--harbor-accent)',
              text: 'var(--harbor-text)',
              muted: 'var(--harbor-muted)',
              low: 'var(--harbor-low)',
              med: 'var(--harbor-med)',
              high: 'var(--harbor-high)',
            }"""

new_tw = """            harbor: {
              bg: 'rgb(var(--harbor-bg) / <alpha-value>)',
              surface: 'rgb(var(--harbor-surface) / <alpha-value>)',
              raised: 'rgb(var(--harbor-raised) / <alpha-value>)',
              border: 'rgb(var(--harbor-border) / <alpha-value>)',
              primary: 'rgb(var(--harbor-primary) / <alpha-value>)',
              'primary-light': 'rgb(var(--harbor-primary-light) / <alpha-value>)',
              accent: 'rgb(var(--harbor-accent) / <alpha-value>)',
              text: 'rgb(var(--harbor-text) / <alpha-value>)',
              muted: 'rgb(var(--harbor-muted) / <alpha-value>)',
              low: 'rgb(var(--harbor-low) / <alpha-value>)',
              med: 'rgb(var(--harbor-med) / <alpha-value>)',
              high: 'rgb(var(--harbor-high) / <alpha-value>)',
            }"""

if old_tw not in t:
    # already partially fixed?
    if "rgb(var(--harbor-bg)" in t:
        print("tailwind already rgb")
    else:
        raise SystemExit("tailwind harbor block not found")
else:
    t = t.replace(old_tw, new_tw, 1)
    print("tailwind ok")

# --- Replace entire theme CSS blocks ---
# From :root, html[data-theme="dark"] through end of mono swipe-action-edit block
start = t.find('    :root, html[data-theme="dark"] {')
if start < 0:
    start = t.find('    :root {')
mono_end_marker = "    html[data-theme=\"mono\"] .swipe-action-edit {"
end = t.find(mono_end_marker, start)
if end < 0:
    raise SystemExit("mono end marker not found")
# find closing brace of that rule
brace = t.find("}", end)
if brace < 0:
    raise SystemExit("brace not found")
end = brace + 1
# skip following blank lines
while end < len(t) and t[end] in "\r\n":
    end += 1

new_theme_css = r'''    /* ── Splash-inspired Harbor palette (default) ──
       Deep harbor teal · warm stone text · seafoam accents
       RGB channel form so Tailwind bg-harbor-primary/20 works. */
    :root, html[data-theme="dark"] {
      --harbor-bg: 10 31 30;              /* #0A1F1E */
      --harbor-surface: 18 46 44;         /* #122E2C */
      --harbor-raised: 26 60 57;          /* #1A3C39 */
      --harbor-border: 42 79 74;          /* #2A4F4A */
      --harbor-primary: 47 155 140;       /* #2F9B8C */
      --harbor-primary-light: 107 191 176;/* #6BBFB0 */
      --harbor-accent: 196 165 116;       /* #C4A574 warm dawn stone */
      --harbor-text: 240 235 227;         /* #F0EBE3 */
      --harbor-muted: 143 168 163;        /* #8FA8A3 */
      --harbor-low: 212 146 122;          /* #D4927A */
      --harbor-med: 212 181 106;          /* #D4B56A */
      --harbor-high: 47 155 140;          /* #2F9B8C */
      --harbor-ease-out: cubic-bezier(0.32, 0.72, 0, 1);
      --harbor-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
      --harbor-shadow-sm: 0 1px 0 rgba(255, 255, 255, 0.04) inset, 0 4px 18px rgba(4, 22, 20, 0.32);
      --harbor-shadow-md: 0 1px 0 rgba(255, 255, 255, 0.05) inset, 0 12px 36px rgba(4, 22, 20, 0.42);
      --harbor-glow-primary: 0 0 0 1px rgba(107, 191, 176, 0.22);
      --harbor-dawn: 10 58 56;            /* #0A3A38 splash deep teal */
      --safe-bottom: env(safe-area-inset-bottom, 0px);
      --safe-top: env(safe-area-inset-top, 0px);
      color-scheme: dark;
    }

    /* Stylish mono — optional black / silver / white */
    html[data-theme="mono"] {
      --harbor-bg: 10 10 10;
      --harbor-surface: 20 20 20;
      --harbor-raised: 28 28 28;
      --harbor-border: 46 46 46;
      --harbor-primary: 232 232 232;
      --harbor-primary-light: 255 255 255;
      --harbor-accent: 168 168 168;
      --harbor-text: 242 242 242;
      --harbor-muted: 138 138 138;
      --harbor-low: 176 176 176;
      --harbor-med: 200 200 200;
      --harbor-high: 232 232 232;
      --harbor-shadow-sm: 0 1px 0 rgba(255, 255, 255, 0.04) inset, 0 4px 18px rgba(0, 0, 0, 0.45);
      --harbor-shadow-md: 0 1px 0 rgba(255, 255, 255, 0.05) inset, 0 12px 36px rgba(0, 0, 0, 0.55);
      --harbor-glow-primary: 0 0 0 1px rgba(255, 255, 255, 0.18);
      --harbor-dawn: 17 17 17;
      color-scheme: dark;
    }

    html[data-theme="mono"] .site-header {
      background: linear-gradient(180deg, rgba(20, 20, 20, 0.96) 0%, rgba(10, 10, 10, 0.94) 100%);
    }

    html[data-theme="mono"] .chip-add-btn,
    html[data-theme="mono"] .today-add-btn {
      background: rgb(242 242 242);
      color: rgb(10 10 10);
    }

    html[data-theme="mono"] .chip-add-btn:active,
    html[data-theme="mono"] .today-add-btn:active {
      opacity: 0.88;
    }

    html[data-theme="mono"] .life-nav-tab.life-panel-active,
    html[data-theme="mono"] .main-nav-tab.nav-active {
      color: rgb(10 10 10);
      background: linear-gradient(180deg, rgba(242, 242, 242, 0.95) 0%, rgba(210, 210, 210, 0.9) 100%);
      box-shadow: 0 1px 0 rgba(255, 255, 255, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.35);
    }

    html[data-theme="mono"] .summary-toggle-btn.is-active {
      background: linear-gradient(135deg, #F2F2F2 0%, #C8C8C8 100%);
      color: rgb(10 10 10);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
    }

    html[data-theme="mono"] .energy-btn.is-active,
    html[data-theme="mono"] .energy-btn[aria-pressed="true"] {
      color: rgb(10 10 10);
    }

    html[data-theme="mono"] .swipe-action-edit {
      background: linear-gradient(180deg, #F0F0F0 0%, #C8C8C8 100%);
      color: rgb(10 10 10);
    }

'''

t = t[:start] + new_theme_css + t[end:]
print("theme blocks ok")

# Wrap bare color CSS vars: var(--harbor-TOKEN) -> rgb(var(--harbor-TOKEN))
# Skip ease, shadow, glow, safe
color_tokens = (
    "bg|surface|raised|border|primary-light|primary|accent|text|muted|low|med|high|dawn"
)
# Don't double-wrap existing rgb(var(...))
pattern = re.compile(
    r"(?<!rgb\()"  # not already rgb(
    r"var\(--harbor-(" + color_tokens + r")\)"
)

def repl(m):
    return f"rgb(var(--harbor-{m.group(1)}))"

t2, n = pattern.subn(repl, t)
print(f"wrapped {n} color vars")
t = t2

# color-mix with rgb(var()) is fine; fix double rgb(rgb(...)) if any
t = t.replace("rgb(rgb(var(", "rgb(var(")
# fix accidental rgb(var(--harbor-primary) / 0.2) that was already rgba - leave alone

# Ensure body/html backgrounds use rgb form
t = t.replace(
    "background-color: var(--harbor-bg);",
    "background-color: rgb(var(--harbor-bg));",
)

# Build bump
t = re.sub(r"const HARBOR_BUILD = 'v\d+'", "const HARBOR_BUILD = 'v92'", t)

path.write_text(t, encoding="utf-8", newline="\n")
print("wrote", path)
print("sample dark primary", "47 155 140" in path.read_text(encoding="utf-8"))
print("sample rgb wrap", "rgb(var(--harbor-bg))" in path.read_text(encoding="utf-8")[:5000] or path.read_text(encoding="utf-8").count("rgb(var(--harbor-bg))") > 0)
