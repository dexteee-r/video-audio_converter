"""
make_icon.py - Generate the application icon (assets/icon.ico)

Terminal Neon Mauve identity: a dark rounded "terminal window" with a mauve
prompt glyph `>_`. Vector-drawn (no font dependency) for crisp scaling.
Run once; re-run to regenerate.
"""

import os

from PIL import Image, ImageDraw

# Theme colors
BG = (10, 10, 15, 255)         # #0A0A0F off-black
BORDER = (139, 92, 246, 255)   # #8B5CF6 mauve deep
MAUVE = (183, 148, 246, 255)   # #B794F6 neon mauve
DOT_R = (255, 107, 139, 255)
DOT_Y = (255, 204, 102, 255)
DOT_G = (88, 230, 166, 255)


def render(size: int) -> Image.Image:
    """Render the icon at the given square size with 4x supersampling."""
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    margin = int(s * 0.06)
    radius = int(s * 0.22)
    bw = max(2, int(s * 0.018))  # border width

    # Terminal window: dark card + mauve border
    d.rounded_rectangle([margin, margin, s - margin, s - margin],
                        radius=radius, fill=BG, outline=BORDER, width=bw)

    # Title-bar dots (only visible at larger sizes)
    if size >= 48:
        dot_y = int(s * 0.2)
        dot_r = int(s * 0.022)
        for i, col in enumerate((DOT_R, DOT_Y, DOT_G)):
            cx = int(s * 0.2) + i * int(s * 0.075)
            d.ellipse([cx - dot_r, dot_y - dot_r, cx + dot_r, dot_y + dot_r], fill=col)

    # Prompt glyph `>` (chevron) + `_` (underscore bar)
    cy = s * 0.56
    lw = max(3, int(s * 0.05))
    # chevron
    cx0 = s * 0.30
    ch = s * 0.13
    cw = s * 0.13
    d.line([(cx0, cy - ch), (cx0 + cw, cy), (cx0, cy + ch)],
           fill=MAUVE, width=lw, joint="curve")
    # underscore bar
    ux0 = s * 0.50
    ux1 = s * 0.70
    uy = cy + ch
    d.rounded_rectangle([ux0, uy - lw / 2, ux1, uy + lw / 2],
                        radius=lw / 2, fill=MAUVE)

    return img.resize((size, size), Image.LANCZOS)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "icon.ico")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    render(256).save(out, format="ICO", sizes=[(n, n) for n in sizes])
    print(f"Icon written: {out}")


if __name__ == "__main__":
    main()
