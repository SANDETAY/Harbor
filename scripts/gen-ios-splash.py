#!/usr/bin/env python3
"""Generate Harbor iOS launch splash: mint wash + centered teal anchor (NOT the app-icon tile)."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ios" / "App" / "App" / "Assets.xcassets" / "Splash.imageset"
SIZE = 2732

# Harbor Mint (matches app body + Capacitor SplashScreen backgroundColor)
G1 = (197, 220, 212)  # #C5DCD4
G2 = (214, 232, 226)  # #D6E8E2
G3 = (224, 237, 232)  # #E0EDE8
TEAL = (15, 74, 69)   # deep harbor teal for the mark


def make_bg(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), G2)
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        if t < 0.35:
            u = t / 0.35
            r = int(G1[0] + (G2[0] - G1[0]) * u)
            g = int(G1[1] + (G2[1] - G1[1]) * u)
            b = int(G1[2] + (G2[2] - G1[2]) * u)
        else:
            u = (t - 0.35) / 0.65
            r = int(G2[0] + (G3[0] - G2[0]) * u)
            g = int(G2[1] + (G3[1] - G2[1]) * u)
            b = int(G2[2] + (G3[2] - G2[2]) * u)
        for x in range(size):
            px[x, y] = (r, g, b)
    return img


def load_anchor_rgba(path: Path, size: int) -> Image.Image:
    """Turn white-on-black (or any) mark into solid teal on transparent."""
    src = Image.open(path).convert("RGBA")
    # Prefer square content
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
            # Luminance of mark (white/light = shape on black or on white)
            lum = (r + g + b) / 3.0
            # White-on-black splash-anchor: high lum = mark
            # Dark-on-white app icon: low lum = mark
            if a < 20:
                continue
            # Detect which kind by corners
            # Use distance from mid gray: strong dark OR strong light = mark pixels
            if lum > 200:
                # light mark on dark
                alpha = int(min(255, a * ((lum - 180) / 75.0)))
                if alpha > 12:
                    opx[x, y] = (*TEAL, alpha)
            elif lum < 90:
                # dark mark on light
                alpha = int(min(255, a * ((90 - lum) / 90.0)))
                if alpha > 12:
                    opx[x, y] = (*TEAL, alpha)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Prefer pure mark (not rounded app-icon tile)
    candidates = [
        ROOT / "harbor-splash-anchor.png",
        ROOT / "harbor-splash-anchor-512.png",
        ROOT / "harbor-fab-anchor.png",
        ROOT / "ios" / "App" / "App" / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon-1024.png",
        ROOT / "harbor-mark.png",
    ]
    mark_path = next((p for p in candidates if p.exists()), None)
    if not mark_path:
        raise SystemExit("No Harbor mark found")
    print("mark:", mark_path)

    bg = make_bg(SIZE).convert("RGBA")
    logo_w = int(SIZE * 0.28)  # modest center mark — not a giant app icon
    mark = load_anchor_rgba(mark_path, logo_w)

    # Soft teal glow plate (circle), not a white rounded-rect app icon
    plate = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(plate)
    cx = cy = SIZE // 2
    r = int(logo_w * 0.72)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 55))
    bg = Image.alpha_composite(bg, plate)

    x = (SIZE - logo_w) // 2
    y = (SIZE - logo_w) // 2
    bg.paste(mark, (x, y), mark)

    out_rgb = bg.convert("RGB")
    for n in ("splash-2732x2732.png", "splash-2732x2732-1.png", "splash-2732x2732-2.png"):
        p = OUT / n
        out_rgb.save(p, "PNG", optimize=True)
        print("wrote", p.name, p.stat().st_size)

    # Solid mint fallback (no mark) for debugging optional
    solid = Image.new("RGB", (SIZE, SIZE), G2)
    solid.save(ROOT / "harbor-ios-launch-solid.png", "PNG", optimize=True)
    out_rgb.save(ROOT / "harbor-ios-launch-splash.png", "PNG", optimize=True)
    print("done")


if __name__ == "__main__":
    main()
