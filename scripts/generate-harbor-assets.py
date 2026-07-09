#!/usr/bin/env python3
"""Generate Harbor app icons (anchor mark) at standard PWA sizes."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent

TEAL_MID = (45, 140, 130, 255)
TEAL_LIGHT = (91, 184, 168, 255)
BG = (8, 18, 20, 255)


def draw_anchor_mark(size: int, bg=BG) -> Image.Image:
    img = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size * 0.42
    ring_w = max(2, int(size * 0.035))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=TEAL_MID, width=ring_w)
    inner = r * 0.92
    d.ellipse(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        fill=(15, 92, 86, 28),
    )

    stem_w = max(2, int(size * 0.07))
    ring_r = size * 0.09
    top = cy - r * 0.55
    bottom = cy + r * 0.52
    stock_y = top + ring_r * 2.1
    stock_half = r * 0.38
    d.rounded_rectangle(
        [
            cx - stock_half,
            stock_y - stem_w * 0.45,
            cx + stock_half,
            stock_y + stem_w * 0.45,
        ],
        radius=max(1, stem_w // 2),
        fill=TEAL_LIGHT,
    )
    d.ellipse(
        [cx - ring_r, top, cx + ring_r, top + ring_r * 2],
        outline=TEAL_LIGHT,
        width=max(2, int(size * 0.045)),
    )
    d.rounded_rectangle(
        [cx - stem_w / 2, top + ring_r * 1.6, cx + stem_w / 2, bottom - r * 0.08],
        radius=max(1, stem_w // 2),
        fill=TEAL_LIGHT,
    )
    arm_r = r * 0.48
    arm_bbox = [cx - arm_r, bottom - arm_r * 1.55, cx + arm_r, bottom + arm_r * 0.45]
    for i in range(max(3, int(size * 0.05))):
        expand = i * 0.35
        d.arc(
            [
                arm_bbox[0] - expand,
                arm_bbox[1] - expand,
                arm_bbox[2] + expand,
                arm_bbox[3] + expand,
            ],
            start=20,
            end=160,
            fill=TEAL_LIGHT,
            width=1,
        )
    fluke = size * 0.07
    lx = cx - arm_r * 0.92
    ly = bottom - arm_r * 0.15
    d.polygon(
        [(lx, ly), (lx - fluke, ly - fluke * 0.2), (lx - fluke * 0.15, ly - fluke)],
        fill=TEAL_LIGHT,
    )
    rx = cx + arm_r * 0.92
    d.polygon(
        [(rx, ly), (rx + fluke, ly - fluke * 0.2), (rx + fluke * 0.15, ly - fluke)],
        fill=TEAL_LIGHT,
    )
    br = size * 0.045
    d.ellipse(
        [cx - br, stock_y - br * 0.2, cx + br, stock_y + br * 1.8],
        fill=TEAL_LIGHT,
    )
    return img


def main():
    svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" fill="none">
  <circle cx="64" cy="64" r="54" stroke="#2D8C82" stroke-width="4.5" opacity="0.9"/>
  <circle cx="64" cy="64" r="48" fill="#0F5C56" fill-opacity="0.12"/>
  <circle cx="64" cy="30" r="9" stroke="#5BB8A8" stroke-width="5"/>
  <rect x="40" y="40" width="48" height="7" rx="3.5" fill="#5BB8A8"/>
  <rect x="59.5" y="38" width="9" height="52" rx="4.5" fill="#5BB8A8"/>
  <path d="M28 78c4 22 22 34 36 34s32-12 36-34" stroke="#5BB8A8" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M28 78l-10-2 4-12z" fill="#5BB8A8"/>
  <path d="M100 78l10-2-4-12z" fill="#5BB8A8"/>
</svg>
"""
    (ROOT / "harbor-mark.svg").write_text(svg, encoding="utf-8")
    print("Wrote harbor-mark.svg")

    outputs = {
        "harbor-favicon-32.png": 32,
        "harbor-apple-touch.png": 180,
        "harbor-icon-192.png": 192,
        "harbor-icon-512.png": 512,
    }
    for name, size in outputs.items():
        path = ROOT / name
        draw_anchor_mark(size).convert("RGB").save(path, format="PNG", optimize=True)
        print(f"Wrote {name} ({size}x{size})")

    draw_anchor_mark(256, bg=(0, 0, 0, 0)).save(
        ROOT / "harbor-mark.png", format="PNG", optimize=True
    )
    print("Wrote harbor-mark.png")
    print("Done")


if __name__ == "__main__":
    main()
