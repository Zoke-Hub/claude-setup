#!/usr/bin/env python3
"""Find a logo's rotational symmetry and true centre, and average its repeats into one sharper image.  (logo-recreation by Zoke)

    symmetry.py <image> --radius <px> [--centre x,y] [--order n] [--annulus 0.08,0.70] [--half 0.8] [--out dir]
    symmetry.py --average out.png a/sym.png b/sym.png        (combine two sources measured with the same radius)

--radius is your unit of measure "R": any clear radius in the image (outer ring, outer edge of the art).
Every later measurement is expressed in R. --annulus is the band (in R) used for scoring; keep text rings
out of it, because lettering does not repeat. Writes sym.png (covers +-half*R) and sym.json.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from lib import load, symmetrise

ap = argparse.ArgumentParser()
ap.add_argument("image", nargs="?"); ap.add_argument("--radius", type=float); ap.add_argument("--centre"); ap.add_argument("--order", type=int)
ap.add_argument("--annulus", default="0.08,0.70"); ap.add_argument("--half", type=float, default=0.8); ap.add_argument("--out"); ap.add_argument("--average", nargs="+")
a = ap.parse_args()
if a.average:
    out, *srcs = a.average
    Image.fromarray(np.mean([np.asarray(Image.open(s).convert("RGB")).astype(float) for s in srcs], axis=0).astype(np.uint8)).save(out)
    print("wrote", out); sys.exit()
if not a.image or not a.radius: ap.error("image and --radius are required")

raw = Image.open(a.image)
UP = 3                                                     # upsample first so sub-pixel sampling stays smooth
big = np.asarray(Image.fromarray(load(a.image).astype(np.uint8)).resize((raw.width * UP, raw.height * UP), Image.LANCZOS)).astype(np.float32)
R = a.radius
c0 = [float(v) for v in a.centre.split(",")] if a.centre else [raw.width / 2, raw.height / 2]
lo, hi = [float(v) for v in a.annulus.split(",")]

def score(cx, cy, order, N):
    s = symmetrise(big, cx * UP, cy * UP, R * UP, order, N, a.half)
    u = (np.arange(N) + 0.5) / N * 2 - 1; X, Y = np.meshgrid(u * a.half, u * a.half); ann = (np.hypot(X, Y) > lo) & (np.hypot(X, Y) < hi)
    return float((s.max(2) - s.min(2))[ann].var() + s.mean(2)[ann].var())    # colour + tone contrast survives only where copies line up

span = max(3.0, 0.14 * R); steps = np.linspace(-span, span, 13)
base = max(score(c0[0] + dx, c0[1] + dy, 1, 96) for dx in (0,) for dy in (0,))
results = {}
for n in ([a.order] if a.order else range(2, 13)):
    results[n] = max((score(c0[0] + dx, c0[1] + dy, n, 96), dx, dy) for dx in steps for dy in steps)
# Averaging n unrelated copies keeps about 1/n of the contrast; a true n-fold repeat keeps nearly all of it.
# q rescales that to 0 (no better than chance) .. 1 (perfect repeat), so different counts can be compared.
q = {n: (v[0] / base - 1 / n) / (1 - 1 / n) for n, v in results.items()}
best = max(q.values())
order = a.order or max(n for n, v in q.items() if v >= 0.8 * best)
print("repeat score by count (0 = chance, 1 = perfect):", {n: round(v, 2) for n, v in q.items()})
if not a.order and best < 0.5:
    order = 1; print("No rotational symmetry found (best score %.2f, need 0.5). Writing a plain enlarged view; measure it directly." % best)
_, dx, dy = results.get(order, (0, 0, 0))
cx, cy = c0[0] + dx, c0[1] + dy
if order > 1:                                              # refine the centre: coarse step, then quarter-pixel
    for step, reach in ((span / 6, 1), (0.5, 2), (0.25, 2)):
        _, cx, cy = max((score(cx + i * step, cy + j * step, order, 200), cx + i * step, cy + j * step) for i in range(-reach * 2, reach * 2 + 1) for j in range(-reach * 2, reach * 2 + 1))
N = 1200
sym = np.clip(symmetrise(big, cx * UP, cy * UP, R * UP, order, N, a.half), 0, 255).astype(np.uint8)
out = Path(a.out or Path(a.image).with_suffix("")) ; out.mkdir(parents=True, exist_ok=True)
Image.fromarray(sym).save(out / "sym.png")
meta = dict(image=str(a.image), centre=[round(cx, 2), round(cy, 2)], radius=R, order=order, half=a.half, N=N, px_per_R=N / 2 / a.half)
(out / "sym.json").write_text(json.dumps(meta, indent=2))
print(f"order {order}, centre ({cx:.2f}, {cy:.2f}) px  ->  {out / 'sym.png'}")
