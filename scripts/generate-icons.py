#!/usr/bin/env python3
"""Generate Rhythm app icons from Logo.jpg on solid black background."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\Taylor\Desktop\Logo.jpg")
BLACK = (0, 0, 0)
PADDING_RATIO = 0.12


def is_checker_gray(r: int, g: int, b: int) -> bool:
    """Detect baked-in checkerboard grays from Logo.jpg export."""
    if max(r, g, b) - min(r, g, b) > 8:
        return False
    avg = (r + g + b) / 3
    return (74 <= avg <= 92) or (114 <= avg <= 136)


def strip_checker_to_rgba(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    w, h = rgb.size
    src = rgb.load()
    out = Image.new("RGBA", (w, h), BLACK + (255,))
    dst = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            if is_checker_gray(r, g, b):
                dst[x, y] = (0, 0, 0, 0)
            else:
                dst[x, y] = (r, g, b, 255)
    return out


def fit_on_black_square(logo: Image.Image, size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), BLACK + (255,))
    pad = int(size * PADDING_RATIO)
    inner = size - pad * 2

    lw, lh = logo.size
    scale = min(inner / lw, inner / lh)
    nw, nh = max(1, int(lw * scale)), max(1, int(lh * scale))
    resized = logo.resize((nw, nh), Image.Resampling.LANCZOS)

    ox = (size - nw) // 2
    oy = (size - nh) // 2
    canvas.paste(resized, (ox, oy), resized)
    return canvas.convert("RGB")


def main():
    if not SRC.exists():
        raise SystemExit(f"Source logo not found: {SRC}")

    logo = strip_checker_to_rgba(Image.open(SRC))

    outputs = {
        "rhythm-favicon-32.png": 32,
        "rhythm-apple-touch.png": 180,
        "rhythm-icon-192.png": 192,
        "rhythm-icon-512.png": 512,
    }

    for name, size in outputs.items():
        out = ROOT / name
        icon = fit_on_black_square(logo, size)
        icon.save(out, format="PNG", optimize=True)
        print(f"Wrote {out} ({size}x{size})")

    print("Done — black background icons generated.")


if __name__ == "__main__":
    main()