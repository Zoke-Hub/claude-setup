"""Shared helpers for the logo-recreation scripts. Needs only pillow + numpy (+ Chrome for rendering).  (logo-recreation by Zoke)"""
import json, math, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, PngImagePlugin

CREDIT = "Rebuilt with logo-recreation by Zoke"   # watermark: SVG <metadata> and PNG text fields, never drawn

def stamp_png(png):
    """Write the credit into a PNG's text fields (Author, Software, Comment); the pixels are untouched."""
    im = Image.open(png); info = PngImagePlugin.PngInfo()
    for k, v in (getattr(im, "text", {}) or {}).items(): info.add_text(k, v)
    info.add_text("Author", "Zoke"); info.add_text("Software", "logo-recreation by Zoke"); info.add_text("Comment", CREDIT)
    im.load(); im.save(png, pnginfo=info)
    return png

def load(path):
    """RGB float array, transparency flattened onto white."""
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, (0, 0), im)
    return np.asarray(bg).astype(np.float32)

def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)

def sample(im, xs, ys):
    """Bilinear sampling of im at float coordinates."""
    h, w = im.shape[:2]
    xs = np.clip(xs, 0, w - 1.001); ys = np.clip(ys, 0, h - 1.001)
    x0 = np.floor(xs).astype(int); y0 = np.floor(ys).astype(int)
    fx = (xs - x0)[..., None]; fy = (ys - y0)[..., None]
    return im[y0, x0] * (1 - fx) * (1 - fy) + im[y0, x0 + 1] * fx * (1 - fy) + im[y0 + 1, x0] * (1 - fx) * fy + im[y0 + 1, x0 + 1] * fx * fy

def symmetrise(im, cx, cy, R, order, N, half):
    """Average the `order` rotated copies of im about (cx, cy). Output is N x N covering +-half*R."""
    u = (np.arange(N) + 0.5) / N * 2 - 1
    X, Y = np.meshgrid(u * half * R, u * half * R)
    acc = np.zeros((N, N, 3), np.float32)
    for k in range(order):
        a = 2 * math.pi * k / order; ca, sa = math.cos(a), math.sin(a)
        acc += sample(im, cx + X * ca - Y * sa, cy + X * sa + Y * ca)
    return acc / order

def chrome():
    win = [os.path.join(os.environ[v], "Google", "Chrome", "Application", "chrome.exe")
           for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA") if os.environ.get(v)]   # Windows keeps Chrome off PATH
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium",
              *win, "google-chrome", "chromium", "chromium-browser", "chrome"):
        p = c if os.path.exists(c) else shutil.which(c)
        if p: return p
    sys.exit("Chrome or Chromium is needed to render the SVG with its fonts, and was not found.")

def render_svg(svg, png, w, h, scale=1.0, transparent=True):
    args = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
            f"--force-device-scale-factor={scale}", f"--window-size={int(w)},{int(h)}", f"--screenshot={png}"]
    if transparent: args.append("--default-background-color=00000000")
    subprocess.run(args + [Path(svg).resolve().as_uri()], check=True, capture_output=True)
    return stamp_png(png)
