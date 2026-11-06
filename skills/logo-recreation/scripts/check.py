#!/usr/bin/env python3
"""Check a rebuilt logo against the original: per-ink overlap score, and an overlay of the new outlines on it.  (logo-recreation by Zoke)

    check.py <name>_art.svg <sym.png> --inks "#1FA498,#2B6CA3" [--window x0,y0,x1,y1] [--out overlay.jpg]

The overlay is the judge: red outlines should sit on the original's edges everywhere. The score (0-1) is a
guide for iteration; blur in the original caps it well below 1, so compare runs, do not chase a number.
Thin lines score lower than solid shapes for the same visual fit.
"""
import argparse, json, re, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from lib import hexrgb, render_svg
ap = argparse.ArgumentParser(); ap.add_argument("svg"); ap.add_argument("sym"); ap.add_argument("--inks", required=True); ap.add_argument("--window"); ap.add_argument("--out")
ap.add_argument("--tol", type=float, default=95)
a = ap.parse_args()
m = json.loads(Path(a.sym).with_name("sym.json").read_text()); N, half = m["N"], m["half"]
E = float(re.search(r'data-half="([\d.]+)"', Path(a.svg).read_text()).group(1))
size = 1200; png = Path(tempfile.mkdtemp()) / "art.png"; render_svg(a.svg, png, size, size, 1.0, transparent=False)
mine = Image.open(png).convert("RGB")                                   # covers +-E*R
k = size / 2 / E * half; mine = mine.crop((int(size / 2 - k), int(size / 2 - k), int(size / 2 + k), int(size / 2 + k))).resize((N, N), Image.LANCZOS)
ref = Image.open(a.sym).convert("RGB"); A, B = np.asarray(ref).astype(np.float32), np.asarray(mine).astype(np.float32)
inner = None
for h in a.inks.split(","):
    c = hexrgb(h); ra = np.linalg.norm(A - c, axis=2) < a.tol; rb = np.linalg.norm(B - c, axis=2) < 60
    if inner is None:
        u = (np.arange(N) + 0.5) / N * 2 - 1; X, Y = np.meshgrid(u * half, u * half); inner = np.hypot(X, Y) < E * 0.98
    ra &= inner; rb &= inner
    print(f"{h}: overlap {(ra & rb).sum() / max(1, (ra | rb).sum()):.2f}   area original {ra.sum()}  rebuilt {rb.sum()}  (ratio {rb.sum() / max(1, ra.sum()):.2f})")
ink = B.sum(2) < 690; edge = ink ^ (np.roll(ink, 1, 0) & np.roll(ink, -1, 0) & np.roll(ink, 1, 1) & np.roll(ink, -1, 1) & ink)
edge |= np.roll(edge, 1, 0) | np.roll(edge, 1, 1)
over = np.asarray(ref).copy(); over[edge] = (255, 0, 60); over = Image.fromarray(over)
if a.window:
    px = m["px_per_R"]; x0, y0, x1, y1 = [float(v) for v in a.window.split(",")]
    over = over.crop((int(N / 2 + x0 * px), int(N / 2 + y0 * px), int(N / 2 + x1 * px), int(N / 2 + y1 * px))); over = over.resize((over.width * 2, over.height * 2), Image.BICUBIC)
out = a.out or str(Path(a.sym).with_name("overlay.jpg")); over.save(out, quality=92); print("wrote", out)
