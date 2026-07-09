#!/usr/bin/env python3
"""Bulk rebrand Rhythm → Harbor across the web app (ordered replacements)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Longest / most-specific first so partials don't double-hit.
REPLACEMENTS = [
    # Functions & JS identifiers
    ("showRhythmBriefModal", "showSummaryModal"),
    ("closeRhythmBriefModal", "closeSummaryModal"),
    ("buildRhythmBrief", "buildSummary"),
    ("renderRhythmBriefModalContent", "renderSummaryModalContent"),
    ("refreshRhythmBriefModal", "refreshSummaryModal"),
    ("wireRhythmBriefModal", "wireSummaryModal"),
    ("updateRhythmBriefLauncher", "updateSummaryLauncher"),
    ("rhythmBriefMode", "summaryMode"),
    ("rhythmEmptyHtml", "harborEmptyHtml"),
    ("maybeAdvanceTutorial('rhythm-brief-open')", "maybeAdvanceTutorial('summary-open')"),
    ("waitFor: 'rhythm-brief-open'", "waitFor: 'summary-open'"),
    ("id: 'rhythm-brief'", "id: 'summary'"),
    ("step.id === 'rhythm-brief'", "step.id === 'summary'"),
    ("'rhythm-brief-open'", "'summary-open'"),
    # Classes / IDs (brief → summary)
    ("rhythm-brief-", "summary-"),
    ("#rhythm-brief", "#summary"),
    ("rhythm-brief", "summary"),
    # CSS design tokens & utility prefixes
    ("--rhythm-", "--harbor-"),
    ("bg-rhythm-", "bg-harbor-"),
    ("text-rhythm-", "text-harbor-"),
    ("border-rhythm-", "border-harbor-"),
    ("from-rhythm-", "from-harbor-"),
    ("to-rhythm-", "to-harbor-"),
    ("via-rhythm-", "via-harbor-"),
    ("ring-rhythm-", "ring-harbor-"),
    ("accent-rhythm-", "accent-harbor-"),
    ("hover:bg-rhythm-", "hover:bg-harbor-"),
    ("hover:text-rhythm-", "hover:text-harbor-"),
    ("focus:border-rhythm-", "focus:border-harbor-"),
    ("active:bg-rhythm-", "active:bg-harbor-"),
    ("placeholder:text-rhythm-", "placeholder:text-harbor-"),
    (".rhythm-card", ".harbor-card"),
    ("rhythm-card", "harbor-card"),
    (".rhythm-empty", ".harbor-empty"),
    ("rhythm-empty", "harbor-empty"),
    ("rhythm: {", "harbor: {"),
    # Build / global
    ("RHYTHM_BUILD", "HARBOR_BUILD"),
    ("window.RHYTHM", "window.HARBOR"),
    ("window.RHYTHM ", "window.HARBOR "),
    ("%c[Rhythm]", "%c[Harbor]"),
    ("[Rhythm]", "[Harbor]"),
    # User-facing copy
    ("Rhythm Brief", "Summary"),
    ("rhythm brief", "summary"),
    ("Rhythm Master", "Harbor Master"),
    ("rhythm-master", "harbor-master"),
    ("Welcome to Rhythm", "Welcome to Harbor"),
    ("Your Rhythm", "Your Harbor"),
    ("your Rhythm", "your Harbor"),
    ("to your Rhythm", "to your Harbor"),
    ("Rhythm caps", "Harbor caps"),
    ("One App for the Whole Day", "Find Your Harbor"),
    ("one app for the whole day", "Find your harbor"),
    ("Find Your Rhythm", "Find Your Harbor"),
    ("Find your Rhythm", "Find your harbor"),
    ("Find your rythm", "Find your harbor"),
    ("Create Your Rythm", "Find Your Harbor"),
    ("Create Your Rhythm", "Find Your Harbor"),
    # Assets (old filenames → harbor)
    ("rhythm-favicon-32.png", "harbor-favicon-32.png"),
    ("rhythm-apple-touch.png", "harbor-apple-touch.png"),
    ("rhythm-icon-192.png", "harbor-icon-192.png"),
    ("rhythm-icon-512.png", "harbor-icon-512.png"),
    ("rythm-splash-mark.svg", "harbor-mark.svg"),
    ("rythm-splash-logo.png", "harbor-mark.png"),
    ("rythm-splash-logo.jpg", "harbor-mark.png"),
    ("rythm-r-mark.png", "harbor-mark.png"),
    ("rythm-wordmark.png", "harbor-mark.png"),
    # Misspelled rythm class prefixes
    ("rythm-lockup", "harbor-lockup"),
    ("rythm-logo", "harbor-logo"),
    ("rythm-wordmark", "harbor-wordmark"),
    ("rythm-title", "harbor-title"),
    ("rythm-", "harbor-"),
    # Storage keys (specific first; keep legacy prefix match for factory reset cleanup)
    ("startsWith('rhythm_')", "startsWith('harbor_') || key.startsWith('rhythm_')"),
    ("rhythm_state_v1", "harbor_state_v1"),
    ("rhythm_factory_reset_v3", "harbor_factory_reset_v1"),
    ("rhythm_onboarded", "harbor_onboarded"),
    ("rhythm_factory_reset", "harbor_factory_reset"),
    ("CACHE_NAME = 'rhythm-preview-v71'", "CACHE_NAME = 'harbor-preview-v72'"),
    ("HARBOR_BUILD = 'v71'", "HARBOR_BUILD = 'v72'"),
    ("= 'v71'", "= 'v72'"),
    # Remaining product name (after multi-word handled)
    ("appName: 'Rhythm'", "appName: 'Harbor'"),
    ('appName: "Rhythm"', 'appName: "Harbor"'),
    ("content=\"Rhythm\"", "content=\"Harbor\""),
    ("content='Rhythm'", "content='Harbor'"),
    ("site_name\" content=\"Rhythm\"", "site_name\" content=\"Harbor\""),
    ("Rhythm —", "Harbor —"),
    ("Rhythm -", "Harbor -"),
    ("Rhythm ·", "Harbor ·"),
    ("Rhythm •", "Harbor •"),
    (">Rhythm<", ">Harbor<"),
    ("'Rhythm'", "'Harbor'"),
    ('"Rhythm"', '"Harbor"'),
    ("Rhythm ", "Harbor "),
    (" Rhythm", " Harbor"),
    ("Rhythm.", "Harbor."),
    ("Rhythm,", "Harbor,"),
    ("Rhythm)", "Harbor)"),
    ("(Rhythm", "(Harbor"),
    # Cache / package leftovers
    ("rhythm-preview-", "harbor-preview-"),
    ("rhythm-webapp", "harbor-webapp"),
    ("Rhythm simulation", "Harbor simulation"),
    ("Rhythm previews", "Harbor previews"),
    ("Rhythm webapp", "Harbor webapp"),
    ("Rhythm design", "Harbor design"),
    ("Rhythm app", "Harbor app"),
    ("# Rhythm", "# Harbor"),
    ("**Rhythm**", "**Harbor**"),
    ("of **Rhythm**", "of **Harbor**"),
    ("of Rhythm", "of Harbor"),
    ("for Rhythm", "for Harbor"),
    ("the Rhythm", "the Harbor"),
    ("with Rhythm", "with Harbor"),
]


def apply_replacements(text: str) -> str:
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
    return text


def process_file(path: Path) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    updated = apply_replacements(original)
    # Catch remaining bare Rhythm / Rythm case-insensitively for review
    if updated != original:
        path.write_text(updated, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    patterns = [
        "*.html",
        "*.js",
        "*.webmanifest",
        "*.json",
        "*.md",
        "*.toml",
        "scripts/*.py",
        "scripts/*.ps1",
    ]
    files = []
    for pat in patterns:
        files.extend(ROOT.glob(pat))
    files = sorted({f.resolve() for f in files if f.is_file()})
    # Skip this rebrand script itself
    files = [f for f in files if f.name not in ("rebrand-to-harbor.py",)]

    changed = []
    for f in files:
        if process_file(f):
            changed.append(f.relative_to(ROOT))
            print(f"updated {f.relative_to(ROOT)}")

    print(f"\n{len(changed)} files updated")


if __name__ == "__main__":
    main()
