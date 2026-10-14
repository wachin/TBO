#!/usr/bin/env python3
"""Generate the Open Graph / Twitter preview card for the project site.

Why this exists
---------------
The site's `og:image` used to point at the demo GIF. That does not work as a
link preview: the card formats used by Twitter/X, Facebook, LinkedIn, Discord
and Slack are static images, so an animated GIF is either ignored, shown as its
first frame with unpredictable cropping, or rejected outright. A preview image
also has to be a fixed aspect ratio (1.91:1, i.e. 1200x630) because every
platform crops to it.

So the card is a real asset that has to be generated once and re-generated
whenever the framing changes. Committing the PNG without the recipe would make
it an unexplainable binary, hence this script.

Usage
-----
    python3 website/tools/make_social_card.py

Reads  ../images/TBO2-en-ezgif.com.gif   (the demo GIF, tracked at the repo root)
Writes ./social-card.png                 (under website/images/)

Requires Pillow. The font is DejaVu Sans, which ships with most Linux
distributions; pass --font to point at another TTF/OTF if it is missing.

The numbers below are a design, not a result: if you change the copy, expect to
nudge the coordinates. Everything is in pixels on a 1200x630 canvas.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 630

# Palette, copied from website/styles.css so the card matches the page.
BG = (11, 13, 20)
TEXT_STRONG = (241, 245, 249)
TEXT_DIM = (148, 163, 184)
AMBER = (251, 191, 36)
VIOLET = (167, 139, 250)

HERE = Path(__file__).resolve().parent
WEBSITE = HERE.parent
REPO = WEBSITE.parent
DEFAULT_GIF = REPO / "images" / "TBO2-en-ezgif.com.gif"
DEFAULT_OUT = WEBSITE / "images" / "social-card.png"
DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEFAULT_FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def radial_glow(size: tuple[int, int], center: tuple[float, float],
                radius: float, colour: tuple[int, int, int],
                strength: float, steps: int = 48) -> Image.Image:
    """Return an additive glow layer: `colour` fading to black over `radius`."""
    glow = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(glow)
    cx, cy = center
    for i in range(steps, 0, -1):
        # Quadratic falloff reads closer to a CSS radial-gradient than a
        # linear ramp, which shows visible banding rings.
        t = i / steps
        alpha = strength * (1.0 - t) ** 2
        r = radius * t
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=tuple(int(c * alpha) for c in colour),
        )
    return glow


def screen(base: Image.Image, layer: Image.Image) -> Image.Image:
    """Photoshop-style screen blend, matching how the CSS glows stack."""
    import numpy as np

    a = np.asarray(base, dtype=np.uint16)
    b = np.asarray(layer, dtype=np.uint16)
    out = 255 - ((255 - a) * (255 - b)) // 255
    return Image.fromarray(out.astype("uint8"))


def rounded(img: Image.Image, radius: int) -> Image.Image:
    """Apply rounded corners to an RGBA image."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                                           radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def fit_font(path: Path, text: str, max_px: int, start: int) -> ImageFont.FreeTypeFont:
    """Largest font size at or below `start` where `text` fits in `max_px`.

    Hard-coding a size is how the first version of this card ended up with the
    headline running underneath the screenshot. Measuring removes the whole
    class of mistake.
    """
    size = start
    while size > 8:
        font = ImageFont.truetype(str(path), size)
        if font.getlength(text) <= max_px:
            return font
        size -= 1
    raise SystemExit(f"error: {text!r} does not fit in {max_px}px even at 9pt")


def build(gif_path: Path, font_bold: Path, font_regular: Path) -> Image.Image:
    # Geometry first: the text column and the screenshot must not overlap, so
    # the column width is derived from where the screenshot starts.
    margin = 72
    shot_w = 600
    shot_x = WIDTH - shot_w - 56
    col_w = shot_x - margin - 24

    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG)
    canvas = screen(canvas, radial_glow((WIDTH, HEIGHT), (90, -40), 900, VIOLET, 0.22))
    canvas = screen(canvas, radial_glow((WIDTH, HEIGHT), (1150, 30), 800, AMBER, 0.16))

    draw = ImageDraw.Draw(canvas)

    # Thin top accent, echoing the site's hero.
    draw.rectangle([0, 0, WIDTH, 3], fill=AMBER)

    # ── Left column: the pitch ────────────────────────────────────────────
    x = margin
    f_wordmark = ImageFont.truetype(str(font_bold), 96)
    title_lines = ["The comic editor", "that refused to die."]
    f_title = fit_font(font_bold, max(title_lines, key=len), col_w, 42)
    body_lines = [
        "Open-source comic editor for .tbo documents,",
        "rewritten in Python + PyQt6: page canvas,",
        "asset library, speech bubbles, PNG/PDF/SVG export.",
    ]
    f_body = fit_font(font_regular, max(body_lines, key=len), col_w, 24)
    f_meta = fit_font(font_regular, "Linux  \u00b7  macOS  \u00b7  Windows  \u00b7  GPL-3.0", col_w, 24)

    draw.text((x, 76), "TBO 2", font=f_wordmark, fill=TEXT_STRONG)

    y = 196
    for line in title_lines:
        draw.text((x, y), line, font=f_title, fill=AMBER)
        y += round(f_title.size * 1.18)

    y += 14
    for line in body_lines:
        draw.text((x, y), line, font=f_body, fill=TEXT_DIM)
        y += round(f_body.size * 1.5)

    y += 20
    draw.text((x, y), "Linux  \u00b7  macOS  \u00b7  Windows  \u00b7  GPL-3.0",
              font=f_meta, fill=VIOLET)
    draw.text((x, y + round(f_meta.size * 1.7)), "github.com/wachin/TBO",
              font=f_meta, fill=TEXT_DIM)

    # ── Right: a real frame from the demo GIF, not a mockup ───────────────
    gif = Image.open(gif_path)
    gif.seek(89)  # a frame with a character and the asset library populated
    shot = gif.convert("RGB")

    target_w = shot_w
    target_h = round(shot.height * target_w / shot.width)
    shot = shot.resize((target_w, target_h), Image.LANCZOS)

    sx, sy = shot_x, (HEIGHT - target_h) // 2
    card = rounded(shot, 12)

    # A 1px violet border so the bright screenshot does not float unanchored.
    border = Image.new("RGBA", (target_w + 2, target_h + 2), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle(
        [0, 0, target_w + 1, target_h + 1], radius=13,
        outline=(167, 139, 250, 110), width=1)
    canvas.paste(border, (sx - 1, sy - 1), border)
    canvas.paste(card, (sx, sy), card)

    return canvas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gif", type=Path, default=DEFAULT_GIF)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--font", type=Path, default=Path(DEFAULT_FONT))
    parser.add_argument("--font-regular", type=Path, default=Path(DEFAULT_FONT_REGULAR))
    args = parser.parse_args(argv)

    for path in (args.gif, args.font, args.font_regular):
        if not path.exists():
            print(f"error: missing required input: {path}", file=sys.stderr)
            return 1

    card = build(args.gif, args.font, args.font_regular)

    # The card format is fixed; a wrong size is silently cropped by every
    # platform, so fail loudly here instead.
    assert card.size == (WIDTH, HEIGHT), card.size

    args.out.parent.mkdir(parents=True, exist_ok=True)
    card.save(args.out, "PNG", optimize=True)

    size = args.out.stat().st_size
    print(f"wrote {args.out} ({WIDTH}x{HEIGHT}, {size:,} bytes)")
    if size > 1_000_000:
        print("warning: over 1 MB; some platforms will refuse it", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
