#!/usr/bin/env python3
"""Generate Harbor app icons (anchor mark). Prefer generate-harbor-assets.py."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("generate-harbor-assets.py")), run_name="__main__")
