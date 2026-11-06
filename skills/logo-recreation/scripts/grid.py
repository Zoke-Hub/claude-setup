#!/usr/bin/env python3
"""Enlarge part of sym.png under a coordinate grid, so shape corners can be read off in units of R.  (logo-recreation by Zoke)

    grid.py <sym.png> --window x0,y0,x1,y1 [--zoom 2.5] [--step 0.05] [--out zoom.jpg]

The window is in R units, origin at the logo centre, y down (so "up" is negative y).
Labelled lines every 0.1 R, faint lines every --step. Read each corner to about 0.005 R.
"""
import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser(); ap.add_argument("sym"); ap.add_argument("--window", required=True); ap.add_argument("--zoom", type=float, default=2.5)
ap.add_argument("--step", type=float, default=0.05); ap.add_argument("--out")
a = ap.parse_args()
m = json.loads(Path(a.sym).with_name("sym.json").read_text()); N, px = m["N"], m["px_per_R"]; c = N / 2
x0, y0, x1, y1 = [float(v) for v in a.window.split(",")]
box = (int(c + x0 * px), int(c + y0 * px), int(c + x1 * px), int(c + y1 * px))
im = Image.open(a.sym).convert("RGB").crop(box); im = im.resize((int(im.width * a.zoom), int(im.height * a.zoom)), Image.BICUBIC)
d = ImageDraw.Draw(im)
X = lambda v: (c + v * px - box[0]) * a.zoom
Y = lambda v: (c + v * px - box[1]) * a.zoom
n0, n1 = int(min(x0, y0) / a.step) - 1, int(max(x1, y1) / a.step) + 1
for i in range(n0, n1 + 1):
    v = round(i * a.step, 4); major = abs(v * 10 - round(v * 10)) < 1e-6; col = (255, 0, 255) if major else (255, 185, 255)
    if x0 <= v <= x1:
        d.line([(X(v), 0), (X(v), im.height)], fill=col)
        if major: d.text((X(v) + 3, 3), f"{v:+.1f}", fill=(190, 0, 190))
    if y0 <= v <= y1:
        d.line([(0, Y(v)), (im.width, Y(v))], fill=col)
        if major: d.text((3, Y(v) + 3), f"{v:+.1f}", fill=(190, 0, 190))
out = a.out or str(Path(a.sym).with_name("zoom.jpg")); im.save(out, quality=92); print("wrote", out, im.size)
