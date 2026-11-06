#!/usr/bin/env python3
"""Measure where one ink colour sits in an image: its box, its band around a centre, or its rows.  (logo-recreation by Zoke)

    measure_ink.py <image> --ink "#1E6B3F" [--tol 70] [--region x0,y0,x1,y1]
                   [--centre x,y --radius R [--rmin 0.66 --rmax 0.95]]     ring text: radial band + start/end angle
                   [--rows]                                                 wordmark: each line's box

Angles are clockwise from 3 o'clock (y down), so 270 is straight up. Radial numbers are in R.
Blur widens every measurement by a pixel or so each side: discount it, especially for small lettering.
"""
import argparse, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from lib import load, hexrgb
ap = argparse.ArgumentParser(); ap.add_argument("image"); ap.add_argument("--ink", required=True); ap.add_argument("--tol", type=float, default=70)
ap.add_argument("--region"); ap.add_argument("--centre"); ap.add_argument("--radius", type=float); ap.add_argument("--rmin", type=float, default=0); ap.add_argument("--rmax", type=float, default=9)
ap.add_argument("--rows", action="store_true")
a = ap.parse_args()
im = load(a.image); h, w = im.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
m = np.linalg.norm(im - hexrgb(a.ink), axis=2) < a.tol
if a.region:
    x0, y0, x1, y1 = [float(v) for v in a.region.split(",")]; m &= (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
if a.centre:
    cx, cy = [float(v) for v in a.centre.split(",")]; rad = np.hypot(xx - cx, yy - cy) / a.radius
    m &= (rad >= a.rmin) & (rad <= a.rmax)
if not m.any(): sys.exit("No pixels within --tol of that ink. Sample the colour from the image and try again.")
ys, xs = np.nonzero(m)
core = im[m][np.argsort(np.linalg.norm(im[m] - hexrgb(a.ink), axis=1))[: max(1, m.sum() // 4)]]
print(f"{m.sum()} px   box x {xs.min()}..{xs.max()}  y {ys.min()}..{ys.max()}   core colour #%02X%02X%02X" % tuple(np.median(core, axis=0).astype(int)))
if a.centre:
    r = rad[m]; ang = np.degrees(np.arctan2(yy - cy, xx - cx))[m] % 360
    s = np.sort(ang); gaps = np.diff(np.r_[s, s[0] + 360]); k = gaps.argmax()
    print(f"radial band {np.percentile(r, 3):.3f}R .. {np.percentile(r, 97):.3f}R   angles {s[(k + 1) % len(s)]:.0f} -> {s[k]:.0f} deg (clockwise from 3 o'clock)")
if a.rows:
    on = m.any(1); edges = np.flatnonzero(np.diff(np.r_[0, on.astype(int), 0]))
    for t, b in zip(edges[::2], edges[1::2]):
        cols = np.nonzero(m[t:b].any(0))[0]
        print(f"  row y {t}..{b - 1} (height {b - t})   x {cols.min()}..{cols.max()} (width {cols.max() - cols.min() + 1}, centre {(cols.min() + cols.max()) / 2})")
