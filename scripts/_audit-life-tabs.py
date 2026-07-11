#!/usr/bin/env python3
"""Audit Life flyout + tab visibility after dock redesign."""
from pathlib import Path
import re
import sys

t = Path("index.html").read_text(encoding="utf-8")
errors = []
warns = []

# Must exist
for needle in [
    'id="life-flyout"',
    "onLifeNavClick",
    "selectLifeSection",
    "closeLifeFlyout",
    "openLifeFlyout",
    "initLifeFlyout",
    ".tab-content.hidden",
    "#tab-content-life.life-tab-shell:not(.hidden)",
    "#tab-content-life.life-tab-shell.hidden",
    ".life-panel.hidden",
]:
    if needle not in t:
        errors.append(f"missing: {needle}")

# Must NOT exist (old sub-dock)
for needle in [
    "life-dock life-subnav",
    "initLifeDockNav",
    'id="life-panel-tab-schedule"',
]:
    if needle in t:
        errors.append(f"stale remnant: {needle}")

# CSS without comments: life shell must not force display:block unless :not(.hidden)
css_only = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
for m in re.finditer(r"(#tab-content-life\.life-tab-shell[^{]*)\{([^}]*)\}", css_only):
    sel, body = m.group(1).strip(), m.group(2)
    if re.search(r"display\s*:\s*block", body) and ":not(.hidden)" not in sel:
        errors.append(f"unconditional life shell display rule: {sel}")

# switchTab must hide other tab-contents
if "classList.add('hidden')" not in t and 'classList.add("hidden")' not in t:
    errors.append("switchTab may not add .hidden to tab contents")

# Function balance
for fn in ["onLifeNavClick", "selectLifeSection", "switchLifePanel", "switchTab"]:
    n = t.count(f"function {fn}")
    if n != 1:
        errors.append(f"expected 1 def of {fn}, got {n}")

# Build number
m = re.search(r"HARBOR_BUILD_NUMBER = (\d+)", t)
if not m:
    errors.append("no HARBOR_BUILD_NUMBER")
else:
    print("build", m.group(1))

# Tab content IDs
for tid in ["today", "life", "streaks", "library"]:
    if f'id="tab-content-{tid}"' not in t:
        errors.append(f"missing tab-content-{tid}")

# Report residual counts (informational)
print("--- residual counts ---")
for s in [
    "life-dock",
    "life-subnav",
    "life-panel-tab-",
    "life-chip-indicator",
    "updateLifeNavIndicator",
    "life-flyout",
    "switchTab('life')",
    "switchLifePanel(",
    "selectLifeSection(",
]:
    print(f"  {s}: {t.count(s)}")

# Stale sliding-chip CSS should be gone
if "life-chip-indicator" in t:
    errors.append("stale life-chip-indicator CSS/JS remains")
if "life-dock life-subnav" in t:
    errors.append("stale life-dock markup remains")

# Life button must open flyout (attribute can be before or after id)
if not re.search(r'onclick="onLifeNavClick\(event\)"[^>]*id="tab-life"|id="tab-life"[^>]*onclick="onLifeNavClick', t):
    errors.append("tab-life button missing onLifeNavClick")

# When lifeFlyoutOpen, switchTab should close it
sw = t[t.find("function switchTab") : t.find("function switchTab") + 2500]
if "closeLifeFlyout" not in sw:
    warns.append("switchTab may not close life flyout")

print("errors", len(errors))
for e in errors:
    print(" ERR", e)
print("warns", len(warns))
for w in warns:
    print(" WARN", w)

sys.exit(1 if errors else 0)
