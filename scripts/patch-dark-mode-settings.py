#!/usr/bin/env python3
"""Finish dark mode settings toggle wiring after partial apply."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "index.html"
t = p.read_text(encoding="utf-8")

t = t.replace("const HARBOR_BUILD = 'v88';", "const HARBOR_BUILD = 'v89';")

old_boot = """    function bootApp() {
        loadState();
        repairOnboardedEmptyTodayList();"""
new_boot = """    function bootApp() {
        loadState();
        applyAppTheme(state.settings?.theme || 'dark');
        repairOnboardedEmptyTodayList();"""
if old_boot in t:
    t = t.replace(old_boot, new_boot, 1)
    print("bootApp ok")
else:
    print("bootApp skip")

marker = "const smartSuggestionsOn = !state.settings.smartSuggestionsMuted;"
if "const darkModeOn" not in t and marker in t:
    t = t.replace(
        marker,
        marker + "\n      const darkModeOn = getAppTheme() === 'dark';",
        1,
    )
    print("darkModeOn ok")
else:
    print("darkModeOn skip")

smart_block = """            <div class=\"flex items-center justify-between gap-3 py-1\">
              <div class=\"min-w-0\">
                <div class=\"text-sm font-medium text-harbor-text\">Smart Suggestions</div>"""
dark_block = """            <div class=\"flex items-center justify-between gap-3 py-1\">
              <div class=\"min-w-0\">
                <div class=\"text-sm font-medium text-harbor-text\">Dark mode</div>
                <div class=\"text-[10px] text-harbor-muted leading-snug\">Deep harbor teal · off for light seafoam</div>
              </div>
              <button type=\"button\" id=\"dark-mode-toggle\" role=\"switch\" aria-checked=\"${darkModeOn}\"
                class=\"smart-suggestions-toggle flex-shrink-0 w-11 h-6 rounded-full relative transition-colors ${darkModeOn ? 'bg-harbor-primary' : 'bg-harbor-border'}\">
                <span class=\"absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${darkModeOn ? 'translate-x-5' : 'translate-x-0'}\"></span>
              </button>
            </div>

            <div class=\"flex items-center justify-between gap-3 py-1\">
              <div class=\"min-w-0\">
                <div class=\"text-sm font-medium text-harbor-text\">Smart Suggestions</div>"""
if 'id="dark-mode-toggle"' not in t and smart_block in t:
    t = t.replace(smart_block, dark_block, 1)
    print("settings UI ok")
else:
    print("settings UI skip", 'id="dark-mode-toggle"' in t)

wire_marker = "wireSwitchToggle(modal.querySelector('#smart-suggestions-toggle'));"
wire_new = """wireSwitchToggle(modal.querySelector('#dark-mode-toggle'), (on) => {
        applyAppTheme(on ? 'dark' : 'light');
        saveState();
        showToast(on ? 'Dark mode on' : 'Light mode on');
      });
      wireSwitchToggle(modal.querySelector('#smart-suggestions-toggle'));"""
if "querySelector('#dark-mode-toggle')" not in t and wire_marker in t:
    t = t.replace(wire_marker, wire_new, 1)
    print("wire ok")
else:
    print("wire skip", "querySelector('#dark-mode-toggle')" in t)

save_marker = """      const corsHelperToggle = modal.querySelector('#calendar-cors-helper-toggle');
      if (corsHelperToggle) {
        state.settings.calendarAllowCorsHelper = corsHelperToggle.getAttribute('aria-checked') === 'true';
      }
      saveState();"""
save_new = """      const corsHelperToggle = modal.querySelector('#calendar-cors-helper-toggle');
      if (corsHelperToggle) {
        state.settings.calendarAllowCorsHelper = corsHelperToggle.getAttribute('aria-checked') === 'true';
      }
      const darkToggle = modal.querySelector('#dark-mode-toggle');
      if (darkToggle) {
        applyAppTheme(darkToggle.getAttribute('aria-checked') === 'true' ? 'dark' : 'light');
      }
      saveState();"""
if "const darkToggle" not in t and save_marker in t:
    t = t.replace(save_marker, save_new, 1)
    print("save ok")
else:
    print("save skip", "const darkToggle" in t)

p.write_text(t, encoding="utf-8", newline="\n")
print(
    "done",
    "v89" in t,
    'dark-mode-toggle' in t,
    "applyAppTheme(state.settings" in t,
)
