#!/usr/bin/env python3
"""
Generate placeholder app icon: rocket flying from the letter O.
Produces build/icon.icns (macOS) and build/icon.ico (Windows).
Run from project root: python3 build/make_icon.py
"""

import math
import os
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow not installed — run: pip install Pillow")

BUILD_DIR = Path(__file__).parent
ICONSET_DIR = BUILD_DIR / "icon.iconset"

# Brand colours
BG_COLOR      = (13, 17, 23, 255)      # near-black
RING_COLOR    = (88, 166, 255, 255)     # blue  #58a6ff
ROCKET_BODY   = (230, 237, 243, 255)   # light grey body
ROCKET_FLAME  = (255, 160, 50, 255)    # orange flame
GLOW_COLOR    = (88, 166, 255, 80)     # translucent blue glow


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    s = size
    cx, cy = s / 2, s / 2

    # ── Background circle ───────────────────────────────────────────────────
    pad = s * 0.03
    d.ellipse([pad, pad, s - pad, s - pad], fill=BG_COLOR)

    # ── "O" ring ─────────────────────────────────────────────────────────────
    # outer radius ~38% of size, stroke ~8% of size
    outer_r = s * 0.38
    stroke  = max(2, int(s * 0.075))
    # Draw as thick arc (simulate ring with two ellipses)
    ox, oy = cx, cy + s * 0.06      # shift O slightly downward to leave room for rocket
    o_x0, o_y0 = ox - outer_r, oy - outer_r
    o_x1, o_y1 = ox + outer_r, oy + outer_r
    # glow
    glow_pad = stroke
    d.ellipse([o_x0 - glow_pad, o_y0 - glow_pad,
               o_x1 + glow_pad, o_y1 + glow_pad], fill=GLOW_COLOR)
    # outer fill
    d.ellipse([o_x0, o_y0, o_x1, o_y1], fill=RING_COLOR)
    # inner cut-out (creates ring)
    inner_r = outer_r - stroke
    d.ellipse([ox - inner_r, oy - inner_r,
               ox + inner_r, oy + inner_r], fill=BG_COLOR)

    # ── Rocket ───────────────────────────────────────────────────────────────
    # Rocket is tilted 45° pointing up-right, placed at top-right of the O
    # We'll draw in a local upward coordinate system, then rotate + paste.

    rocket_h = s * 0.38
    rocket_w = rocket_h * 0.32
    rh, rw = rocket_h, rocket_w

    # Rocket sub-image (transparent background)
    rs = int(max(rocket_h, rocket_w) * 2.2)
    rocket_img = Image.new("RGBA", (rs, rs), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rocket_img)
    rcx, rcy_base = rs / 2, rs * 0.75

    # Body polygon (pointed at top)
    nose_y  = rcy_base - rh
    body_top_w = rw * 0.25
    body_bot_w = rw * 0.50
    body_pts = [
        (rcx, nose_y),                             # nose tip
        (rcx + body_top_w, nose_y + rh * 0.25),
        (rcx + body_bot_w, rcy_base),
        (rcx - body_bot_w, rcy_base),
        (rcx - body_top_w, nose_y + rh * 0.25),
    ]
    rd.polygon(body_pts, fill=ROCKET_BODY)

    # Window
    win_cx = rcx
    win_cy = nose_y + rh * 0.38
    win_r  = rw * 0.22
    rd.ellipse([win_cx - win_r, win_cy - win_r,
                win_cx + win_r, win_cy + win_r],
               fill=RING_COLOR)
    rd.ellipse([win_cx - win_r * 0.55, win_cy - win_r * 0.55,
                win_cx + win_r * 0.55, win_cy + win_r * 0.55],
               fill=(200, 230, 255, 200))

    # Fins
    fin_w = rw * 0.45
    fin_h = rh * 0.22
    # left fin
    rd.polygon([
        (rcx - body_bot_w, rcy_base),
        (rcx - body_bot_w - fin_w, rcy_base + fin_h * 0.6),
        (rcx - body_bot_w + rw * 0.05, rcy_base - fin_h),
    ], fill=RING_COLOR)
    # right fin
    rd.polygon([
        (rcx + body_bot_w, rcy_base),
        (rcx + body_bot_w + fin_w, rcy_base + fin_h * 0.6),
        (rcx + body_bot_w - rw * 0.05, rcy_base - fin_h),
    ], fill=RING_COLOR)

    # Flame
    flame_h = rh * 0.35
    flame_w = rw * 0.40
    flame_pts = [
        (rcx - flame_w * 0.5, rcy_base),
        (rcx + flame_w * 0.5, rcy_base),
        (rcx + flame_w * 0.25, rcy_base + flame_h * 0.5),
        (rcx, rcy_base + flame_h),
        (rcx - flame_w * 0.25, rcy_base + flame_h * 0.5),
    ]
    rd.polygon(flame_pts, fill=ROCKET_FLAME)
    # inner flame core
    inner_flame_pts = [
        (rcx - flame_w * 0.2, rcy_base + flame_h * 0.1),
        (rcx + flame_w * 0.2, rcy_base + flame_h * 0.1),
        (rcx, rcy_base + flame_h * 0.65),
    ]
    rd.polygon(inner_flame_pts, fill=(255, 220, 80, 220))

    # Rotate rocket 45° (pointing up-right) and paste onto main image
    rotated = rocket_img.rotate(-45, resample=Image.BICUBIC, expand=False)

    # Position: centre of rocket at top-right of the O ring
    # top-right of O is approximately at angle 315° (up-right) from O centre
    angle_deg = -45   # top-right
    angle_rad = math.radians(angle_deg)
    offset_r  = outer_r * 0.80
    rx_center = ox + offset_r * math.cos(math.radians(45))
    ry_center = oy - offset_r * math.sin(math.radians(45))

    paste_x = int(rx_center - rs / 2)
    paste_y = int(ry_center - rs / 2)
    img.paste(rotated, (paste_x, paste_y), rotated)

    return img


def make_icns(sizes=(16, 32, 64, 128, 256, 512, 1024)):
    ICONSET_DIR.mkdir(exist_ok=True)
    for sz in sizes:
        icon = draw_icon(sz)
        icon.save(ICONSET_DIR / f"icon_{sz}x{sz}.png")
        # macOS iconset convention: @2x files
        if sz >= 32:
            icon.save(ICONSET_DIR / f"icon_{sz//2}x{sz//2}@2x.png")

    out_icns = BUILD_DIR / "icon.icns"
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET_DIR), "-o", str(out_icns)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("iconutil error:", result.stderr)
        sys.exit(1)
    print(f"  Created: {out_icns}")


def make_ico(sizes=(16, 32, 48, 64, 128, 256)):
    # Draw the largest size and let Pillow downscale to each target size
    large = draw_icon(256).convert("RGBA")
    out_ico = BUILD_DIR / "icon.ico"
    large.save(
        out_ico,
        format="ICO",
        sizes=[(sz, sz) for sz in sizes],
    )
    print(f"  Created: {out_ico}")


if __name__ == "__main__":
    print("Generating icons...")
    make_icns()
    make_ico()
    print("Done.")
