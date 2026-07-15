#!/usr/bin/env python3
"""
Generate Harbor iOS launch splash (Assets.xcassets/Splash.imageset).

Portrait art (matches phone screens) so aspectFill doesn't crop the slogan.
Includes anchor + Harbor + “One App For The Whole Day”.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ios" / "App" / "App" / "Assets.xcassets" / "Splash.imageset"

# iPhone 14 Pro Max-ish portrait (3x-friendly)
W, H = 1284, 2778

G1 = (6, 40, 38)
G2 = (10, 58, 56)
G3 = (20, 96, 90)
G4 = (90, 140, 132)
MARK = (236, 245, 242)


def make_bg(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), G2)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        if t < 0.4:
            u = t / 0.4
            r = int(G1[0] + (G2[0] - G1[0]) * u)
            g = int(G1[1] + (G2[1] - G1[1]) * u)
            b = int(G1[2] + (G2[2] - G1[2]) * u)
        elif t < 0.72:
            u = (t - 0.4) / 0.32
            r = int(G2[0] + (G3[0] - G2[0]) * u)
            g = int(G2[1] + (G3[1] - G2[1]) * u)
            b = int(G2[2] + (G3[2] - G2[2]) * u)
        else:
            u = (t - 0.72) / 0.28
            r = int(G3[0] + (G4[0] - G3[0]) * u * 0.4)
            g = int(G3[1] + (G4[1] - G3[1]) * u * 0.4)
            b = int(G3[2] + (G4[2] - G3[2]) * u * 0.4)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def load_anchor_rgba(path: Path, size: int) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    sw, sh = src.size
    side = min(sw, sh)
    left = (sw - side) // 2
    top = (sh - side) // 2
    src = src.crop((left, top, left + side, top + side))
    src = src.resize((size, size), Image.Resampling.LANCZOS)
    px = src.load()
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    opx = out.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            lum = (r + g + b) / 3.0
            if lum > 200:
                alpha = int(min(255, a * ((lum - 180) / 75.0)))
                if alpha > 12:
                    opx[x, y] = (*MARK, alpha)
            elif lum < 90:
                alpha = int(min(255, a * ((90 - lum) / 90.0)))
                if alpha > 12:
                    opx[x, y] = (*MARK, alpha)
    return out


def try_font(size: int) -> ImageFont.ImageFont:
    for p in (
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_brand(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    w, h = img.size
    word_font = try_font(int(h * 0.048))
    slogan_font = try_font(int(h * 0.022))
    word = "Harbor"
    slogan = "One App For The Whole Day"

    wb = draw.textbbox((0, 0), word, font=word_font)
    ww, wh = wb[2] - wb[0], wb[3] - wb[1]
    wx = (w - ww) // 2
    wy = int(h * 0.52)
    draw.text((wx + 2, wy + 3), word, font=word_font, fill=(0, 0, 0))
    draw.text((wx, wy), word, font=word_font, fill=(247, 243, 236))

    sb = draw.textbbox((0, 0), slogan, font=slogan_font)
    sw = sb[2] - sb[0]
    sx = (w - sw) // 2
    sy = wy + wh + int(h * 0.028)
    draw.text((sx + 1, sy + 2), slogan, font=slogan_font, fill=(0, 0, 0))
    draw.text((sx, sy), slogan, font=slogan_font, fill=(200, 220, 214))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bg = make_bg(W, H)

    logo_w = int(W * 0.34)
    mark = None
    for c in (
        ROOT / "harbor-splash-anchor.png",
        ROOT / "harbor-splash-anchor-512.png",
        ROOT / "harbor-fab-anchor.png",
        ROOT / "harbor-mark.png",
    ):
        if c.exists():
            mark = load_anchor_rgba(c, logo_w)
            print("anchor from", c.name)
            break
    if mark is None:
        mark = Image.new("RGBA", (logo_w, logo_w), (0, 0, 0, 0))
        d = ImageDraw.Draw(mark)
        pad = logo_w // 8
        d.ellipse((pad, pad, logo_w - pad, logo_w - pad), outline=MARK + (230,), width=max(10, logo_w // 36))

    x = (W - logo_w) // 2
    y = int(H * 0.30)
    bg.paste(mark, (x, y), mark)
    draw_brand(bg)

    out_rgb = bg.convert("RGB")
    for n in ("splash-2732x2732.png", "splash-2732x2732-1.png", "splash-2732x2732-2.png"):
        p = OUT / n
        out_rgb.save(p, "PNG", optimize=True)
        print("wrote", p.name, p.stat().st_size, out_rgb.size)

    solid = Image.new("RGB", (W, H), G2)
    solid.save(ROOT / "harbor-ios-launch-solid.png", "PNG", optimize=True)
    out_rgb.save(ROOT / "harbor-ios-launch-splash.png", "PNG", optimize=True)

    # Update Contents.json dimensions hint isn't required; storyboard uses image name Splash
    print("done — portrait brand splash", W, "x", H)


if __name__ == "__main__":
    main()
