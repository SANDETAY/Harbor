#!/usr/bin/env python3
"""Generate Harbor iOS launch splash images (mint wash + centered mark)."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ios" / "App" / "App" / "Assets.xcassets" / "Splash.imageset"
SIZE = 2732

# Harbor Mint gradient stops (matches app body wash)
G1 = (197, 220, 212)  # #C5DCD4
G2 = (214, 232, 226)  # #D6E8E2
G3 = (224, 237, 232)  # #E0EDE8


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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    candidates = [
        ROOT / "ios" / "App" / "App" / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon-1024.png",
        ROOT / "harbor-icon-512.png",
        ROOT / "harbor-mark.png",
        ROOT / "harbor-icon-source.png",
    ]
    icon_path = next((p for p in candidates if p.exists()), None)
    if not icon_path:
        raise SystemExit("No Harbor mark found for splash")
    print("icon:", icon_path)

    bg = make_bg(SIZE).convert("RGBA")
    icon = Image.open(icon_path).convert("RGBA")

    # Center logo ~38% of canvas (safe when iOS crops for tall phones)
    logo_w = int(SIZE * 0.38)
    icon = icon.resize((logo_w, logo_w), Image.Resampling.LANCZOS)

    # Soft plate behind logo
    plate = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(plate)
    cx = cy = SIZE // 2
    r = int(logo_w * 0.62)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 72))
    bg = Image.alpha_composite(bg, plate)

    x = (SIZE - logo_w) // 2
    y = (SIZE - logo_w) // 2
    bg.paste(icon, (x, y), icon)

    out_rgb = bg.convert("RGB")
    names = [
        "splash-2732x2732.png",
        "splash-2732x2732-1.png",
        "splash-2732x2732-2.png",
    ]
    for n in names:
        p = OUT / n
        out_rgb.save(p, "PNG", optimize=True)
        print("wrote", p.name, p.stat().st_size)

    ref = ROOT / "harbor-ios-launch-splash.png"
    out_rgb.save(ref, "PNG", optimize=True)
    print("ref", ref)
    print("done")


if __name__ == "__main__":
    main()
