#!/usr/bin/env python3
"""Generate Harbor iOS launch splash for seamless handoff into the web splash.

Native LaunchScreen cannot animate. It must match the HTML splash *background*
exactly so the handoff feels like one continuous screen — then mark / word /
slogan animate in HTML.

HTML reference (index.html):
  .splash-screen-harbor {
    background: linear-gradient(165deg, #062826 0%, #0a3a38 28%,
      #14605a 58%, #7aaba3 86%, #d8e4de 100%);
  }
  .splash-sky {
    radial-gradient(ellipse 80% 50% at 50% 16%, rgba(255,236,210,0.2) …),
    radial-gradient(ellipse 55% 40% at 50% 48%, primary/0.14 …);
  }

Do NOT draw hard concentric rings / “arches” — those read as a different design
from the soft CSS gradients and break the handoff.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ios" / "App" / "App" / "Assets.xcassets" / "Splash.imageset"
SIZE = 2732

# CSS 165deg-ish stops (top-left deep teal → bottom-right mist)
STOPS = [
    (0.00, (6, 40, 38)),      # #062826
    (0.28, (10, 58, 56)),     # #0a3a38
    (0.58, (20, 96, 90)),     # #14605a
    (0.86, (122, 171, 163)),  # #7aaba3
    (1.00, (216, 228, 222)),  # #d8e4de
]
MARK_LIGHT = (244, 243, 236)
WORD_COLOR = (247, 243, 236)
SLOGAN_COLOR = (236, 242, 238, 235)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_rgb(c0, c1, t):
    return tuple(int(lerp(c0[i], c1[i], t)) for i in range(3))


def color_at(t: float):
    t = max(0.0, min(1.0, t))
    for i in range(len(STOPS) - 1):
        t0, c0 = STOPS[i]
        t1, c1 = STOPS[i + 1]
        if t <= t1 or i == len(STOPS) - 2:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            u = max(0.0, min(1.0, u))
            return lerp_rgb(c0, c1, u)
    return STOPS[-1][1]


def make_bg(size: int) -> Image.Image:
    """Match CSS linear-gradient(165deg, …) — smooth top→bottom with slight diagonal."""
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        vy = y / (size - 1)
        for x in range(size):
            vx = x / (size - 1)
            # 165deg ≈ mostly vertical, slight L→R
            t = max(0.0, min(1.0, vy * 0.88 + vx * 0.12))
            px[x, y] = color_at(t)
    return img


def soft_radial(
    size: int,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    rgba: tuple[int, int, int, int],
    blur_frac: float = 0.12,
) -> Image.Image:
    """Soft ellipse glow (blurred) — matches CSS radial-gradient, not ring arches."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    r, g, b, a = rgba
    # Draw a filled ellipse then blur heavily so edges dissolve
    box = [cx - rx, cy - ry, cx + rx, cy + ry]
    draw.ellipse(box, fill=(r, g, b, a))
    blur = max(8, int(size * blur_frac))
    return layer.filter(ImageFilter.GaussianBlur(radius=blur))


def add_sky_glows(base: Image.Image) -> Image.Image:
    """HTML .splash-sky — warm top glow + soft primary mid glow."""
    size = base.size[0]
    out = base.convert("RGBA")
    # Warm highlight near top (50% y≈16%)
    warm = soft_radial(
        size,
        cx=size * 0.5,
        cy=size * 0.16,
        rx=size * 0.42,
        ry=size * 0.26,
        rgba=(255, 236, 210, 48),
        blur_frac=0.10,
    )
    # Soft mint mid glow (primary-ish at ~48%)
    mid = soft_radial(
        size,
        cx=size * 0.5,
        cy=size * 0.48,
        rx=size * 0.30,
        ry=size * 0.22,
        rgba=(47, 155, 140, 36),
        blur_frac=0.11,
    )
    out = Image.alpha_composite(out, warm)
    out = Image.alpha_composite(out, mid)
    return out


def compose_first_frame() -> Image.Image:
    """First frame of web splash: gradient + soft sky only (no mark, no arches)."""
    return add_sky_glows(make_bg(SIZE))


def load_light_anchor(path: Path, size: int) -> Image.Image:
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
            if lum > 160:
                alpha = int(min(255, a * ((lum - 140) / 115.0)))
                if alpha > 12:
                    opx[x, y] = (*MARK_LIGHT, alpha)
            elif lum < 80 and a > 200:
                alpha = int(min(255, a * ((80 - lum) / 80.0)))
                if alpha > 12:
                    opx[x, y] = (*MARK_LIGHT, alpha)
    return out


def pick_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_centered_text(draw, text: str, cy: int, font, fill, letter_spacing: int = 0):
    if letter_spacing <= 0:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (SIZE - tw) // 2
        y = cy - th // 2 - bbox[1]
        draw.text((x, y), text, font=font, fill=fill)
        return th
    widths = []
    total = 0
    for ch in text:
        bb = draw.textbbox((0, 0), ch, font=font)
        w = bb[2] - bb[0]
        widths.append((ch, w, bb))
        total += w
    total += letter_spacing * max(0, len(text) - 1)
    x = (SIZE - total) // 2
    max_h = 0
    for ch, w, bb in widths:
        th = bb[3] - bb[1]
        max_h = max(max_h, th)
        y = cy - th // 2 - bb[1]
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + letter_spacing
    return max_h


def compose_settled_brand(mark_path: Path) -> Image.Image:
    """Full brand lockup (preview / marketing only — not LaunchScreen)."""
    bg = compose_first_frame()
    logo_w = int(SIZE * 0.22)
    mark = load_light_anchor(mark_path, logo_w)

    plate = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(plate)
    cx = SIZE // 2
    cy_mark = int(SIZE * 0.42)
    r = int(logo_w * 0.78)
    pdraw.ellipse(
        [cx - r, cy_mark - r, cx + r, cy_mark + r], fill=(232, 244, 240, 22)
    )
    plate = plate.filter(ImageFilter.GaussianBlur(radius=int(SIZE * 0.02)))
    bg = Image.alpha_composite(bg, plate)

    mx = (SIZE - logo_w) // 2
    my = cy_mark - logo_w // 2
    bg.paste(mark, (mx, my), mark)

    draw = ImageDraw.Draw(bg)
    word_font = pick_font(int(SIZE * 0.072), bold=True)
    slogan_font = pick_font(int(SIZE * 0.028), bold=False)

    cy_word = cy_mark + logo_w // 2 + int(SIZE * 0.055)
    draw_centered_text(
        draw, "Harbor", cy_word, word_font, WORD_COLOR, letter_spacing=int(SIZE * 0.004)
    )

    cy_slogan = cy_word + int(SIZE * 0.075)
    draw_centered_text(
        draw,
        "One App For The Whole Day",
        cy_slogan,
        slogan_font,
        SLOGAN_COLOR,
        letter_spacing=int(SIZE * 0.006),
    )

    rule_w = int(SIZE * 0.28)
    rule_y = cy_slogan + int(SIZE * 0.045)
    for i in range(rule_w):
        t = i / max(1, rule_w - 1)
        edge = min(t, 1 - t) * 2
        alpha = int(40 + 140 * edge)
        rr = int(lerp(244, 47, edge * 0.6))
        gg = int(lerp(239, 155, edge * 0.6))
        bb = int(lerp(230, 140, edge * 0.6))
        x = (SIZE - rule_w) // 2 + i
        draw.point((x, rule_y), fill=(rr, gg, bb, alpha))
        draw.point((x, rule_y + 1), fill=(rr, gg, bb, max(0, alpha - 40)))

    return bg


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    candidates = [
        ROOT / "harbor-splash-anchor.png",
        ROOT / "harbor-splash-anchor-512.png",
        ROOT / "harbor-fab-anchor.png",
        ROOT / "harbor-mark.png",
    ]
    mark_path = next((p for p in candidates if p.exists()), None)
    if not mark_path:
        raise SystemExit("No Harbor mark found")
    print("mark:", mark_path)

    # iOS LaunchScreen — first frame only (seamless → HTML splash)
    first = compose_first_frame().convert("RGB")
    for n in ("splash-2732x2732.png", "splash-2732x2732-1.png", "splash-2732x2732-2.png"):
        p = OUT / n
        first.save(p, "PNG", optimize=True)
        print("wrote first-frame", p.name, p.stat().st_size)

    # Solid fallback (top of gradient) for any solid-color launch uses
    solid = Image.new("RGB", (64, 64), STOPS[0][1])
    solid_path = ROOT / "harbor-ios-launch-solid.png"
    solid.save(solid_path, "PNG")
    print("solid", solid_path)

    # Settled brand preview (marketing / docs — not LaunchScreen)
    settled = compose_settled_brand(mark_path).convert("RGB")
    preview = ROOT / "harbor-ios-launch-splash.png"
    settled.save(preview, "PNG", optimize=True)
    print("preview (settled brand)", preview)
    print("done — first frame is clean gradient + soft sky (no arches)")


if __name__ == "__main__":
    main()
