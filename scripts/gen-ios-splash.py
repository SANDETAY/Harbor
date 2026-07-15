#!/usr/bin/env python3
"""
Generate Harbor iOS launch splash (Assets.xcassets/Splash.imageset).

Matches the HTML brand splash: deep teal wash + centered anchor + Harbor wordmark
+ “One App For The Whole Day” so TestFlight LaunchScreen isn’t a blank mint plate.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ios" / "App" / "App" / "Assets.xcassets" / "Splash.imageset"
SIZE = 2732

# Deep teal wash (aligned with .splash-screen-harbor)
G1 = (6, 40, 38)      # #062826
G2 = (10, 58, 56)     # #0a3a38
G3 = (20, 96, 90)     # #14605a
G4 = (122, 171, 163)  # soft mid
MARK = (214, 232, 226)  # light mint mark on dark


def make_bg(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), G2)
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        if t < 0.45:
            u = t / 0.45
            r = int(G1[0] + (G2[0] - G1[0]) * u)
            g = int(G1[1] + (G2[1] - G1[1]) * u)
            b = int(G1[2] + (G2[2] - G1[2]) * u)
        elif t < 0.78:
            u = (t - 0.45) / 0.33
            r = int(G2[0] + (G3[0] - G2[0]) * u)
            g = int(G2[1] + (G3[1] - G2[1]) * u)
            b = int(G2[2] + (G3[2] - G2[2]) * u)
        else:
            u = (t - 0.78) / 0.22
            r = int(G3[0] + (G4[0] - G3[0]) * u * 0.35)
            g = int(G3[1] + (G4[1] - G3[1]) * u * 0.35)
            b = int(G3[2] + (G4[2] - G3[2]) * u * 0.35)
        for x in range(size):
            # soft vignette
            cx = (x / (size - 1) - 0.5) * 2
            edge = min(1.0, (cx * cx) * 0.08)
            rr = max(0, int(r * (1 - edge)))
            gg = max(0, int(g * (1 - edge)))
            bb = max(0, int(b * (1 - edge)))
            px[x, y] = (rr, gg, bb)
    return img


def load_anchor_rgba(path: Path, size: int) -> Image.Image:
    """Turn mark art into light mint on transparent."""
    src = Image.open(path).convert("RGBA")
    w, h = src.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
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
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_brand_text(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    word_font = try_font(148)
    slogan_font = try_font(64)
    word = "Harbor"
    slogan = "One App For The Whole Day"

    # Wordmark under the mark
    wb = draw.textbbox((0, 0), word, font=word_font)
    ww, wh = wb[2] - wb[0], wb[3] - wb[1]
    wx = (SIZE - ww) // 2
    wy = int(SIZE * 0.56)
    # soft shadow
    draw.text((wx + 3, wy + 4), word, font=word_font, fill=(0, 0, 0, 80))
    draw.text((wx, wy), word, font=word_font, fill=(236, 245, 242))

    # Slogan
    sb = draw.textbbox((0, 0), slogan, font=slogan_font)
    sw = sb[2] - sb[0]
    sx = (SIZE - sw) // 2
    sy = wy + wh + 48
    draw.text((sx + 2, sy + 2), slogan, font=slogan_font, fill=(0, 0, 0, 60))
    draw.text((sx, sy), slogan, font=slogan_font, fill=(180, 210, 204))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bg = make_bg(SIZE)

    candidates = [
        ROOT / "harbor-splash-anchor.png",
        ROOT / "harbor-splash-anchor-512.png",
        ROOT / "harbor-fab-anchor.png",
        ROOT / "harbor-mark.png",
    ]
    mark = None
    logo_w = int(SIZE * 0.28)
    for c in candidates:
        if c.exists():
            mark = load_anchor_rgba(c, logo_w)
            print("anchor from", c.name)
            break
    if mark is None:
        # Fallback circle mark
        mark = Image.new("RGBA", (logo_w, logo_w), (0, 0, 0, 0))
        d = ImageDraw.Draw(mark)
        pad = logo_w // 8
        d.ellipse((pad, pad, logo_w - pad, logo_w - pad), outline=MARK + (230,), width=max(8, logo_w // 40))

    x = (SIZE - logo_w) // 2
    y = int(SIZE * 0.32)
    bg.paste(mark, (x, y), mark)

    draw_brand_text(bg)

    out_rgb = bg.convert("RGB")
    for n in ("splash-2732x2732.png", "splash-2732x2732-1.png", "splash-2732x2732-2.png"):
        p = OUT / n
        out_rgb.save(p, "PNG", optimize=True)
        print("wrote", p.name, p.stat().st_size)

    solid = Image.new("RGB", (SIZE, SIZE), G2)
    solid.save(ROOT / "harbor-ios-launch-solid.png", "PNG", optimize=True)
    out_rgb.save(ROOT / "harbor-ios-launch-splash.png", "PNG", optimize=True)
    print("done — dark brand splash with slogan")


if __name__ == "__main__":
    main()
