#!/usr/bin/env python3
"""BiRefNet cut-out at the image's FULL resolution (MIT-licensed model, runs locally: MPS on a Mac, CUDA on an NVIDIA PC).
    <cut-out venv python> birefnet_cutout.py <in> <out.png> [--model hr|hr-matting|base] [--size 2048] [--mask m.png]
                                             [--precision auto|half|full]
The model predicts the matte at --size (2048 for the HR models); the matte is upscaled to the original size and refined
with a guided filter on the full-resolution image, so edges follow the real pixels; then the backdrop colour is taken out
of the soft edge pixels. Output = original pixels + alpha, same width/height as the input (never downscaled).
Chosen on 2026-10-19 over Apple Vision (soft, blurry edges; punched holes) and hyperframes remove-background (kept
backdrop inside loops, cropped parts off): see the skill's README.md.

Memory: at 2048 the HR model needs about 16-18 GB of GPU memory in full precision and about 9 GB in half precision (the
mattes are the same to the eye). The precision and working size for this computer come from the machine check
(probe_machine.py, run by the setup; saved in machine.json in the cut-out venv); without it they are worked out here
from the GPU / RAM size. On Apple silicon a memory cap makes an over-large job stop with an error instead of freezing
the computer; if the GPU still runs out, the cut-out is retried in half precision, then at a smaller working size, and
the script says what it used.
"""
import argparse, json, os, platform, subprocess, sys
from pathlib import Path

VENV = Path(sys.prefix)
MACHINE = VENV / "machine.json"

def machine_profile():
    """Device, memory and the settings that fit them. Pure detection, no model loaded."""
    import torch
    if torch.cuda.is_available():
        dev, gb = "cuda", torch.cuda.get_device_properties(0).total_memory / 2**30
        prec, size = ("full", 2048) if gb >= 20 else ("half", 2048) if gb >= 10 else ("half", 1536) if gb >= 7 else ("half", 1024)
    elif torch.backends.mps.is_available():
        dev = "mps"
        gb = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip() or 0) / 2**30
        prec, size = ("full", 2048) if gb >= 48 else ("half", 2048) if gb >= 16 else ("half", 1536) if gb >= 12 else ("half", 1024)
    else:
        dev = "cpu"
        try: gb = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30
        except (ValueError, OSError, AttributeError): gb = 0
        prec, size = "full", (2048 if gb >= 32 else 1536 if gb >= 16 else 1024)   # half precision is slow on a CPU
    return {"device": dev, "memory_gb": round(gb, 1), "precision": prec, "size": size,
            "mps_cap": 1.0 if dev == "mps" else None, "system": platform.platform()}

def load_profile():
    try: return json.loads(MACHINE.read_text())
    except (OSError, ValueError): return None

# the Apple-GPU memory cap must be set before torch starts
_prof = load_profile()
if platform.system() == "Darwin" and "PYTORCH_MPS_HIGH_WATERMARK_RATIO" not in os.environ:
    cap = (_prof or {}).get("mps_cap") or 1.0          # = the GPU's recommended working set (torch's own default lets it go 70 % over)
    os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = str(cap)
    os.environ.setdefault("PYTORCH_MPS_LOW_WATERMARK_RATIO", str(round(cap - 0.1, 2)))

import numpy as np, torch, cv2
from PIL import Image
from transformers import AutoModelForImageSegmentation
Image.MAX_IMAGE_PIXELS = None
MODELS = {"hr": "ZhengPeng7/BiRefNet_HR", "hr-matting": "ZhengPeng7/BiRefNet_HR-matting", "base": "ZhengPeng7/BiRefNet"}

def guided(I, p, r, eps):
    mean = lambda x: cv2.boxFilter(x, -1, (r, r))
    mI, mp = mean(I), mean(p)
    a = (mean(I * p) - mI * mp) / (mean(I * I) - mI * mI + eps)
    b = mp - a * mI
    return mean(a) * I + mean(b)

def decontaminate(px, m):
    """Edge pixels (0 < alpha < 1) mix the object with the backdrop. Replace their colour with the object's own colour,
    spread outward from the solid interior (alpha-weighted normalised blur at a few radii), keeping the alpha as is."""
    f = px.astype(np.float32)
    w = (m ** 4).astype(np.float32)                              # trust only near-solid pixels
    acc, wacc = np.zeros_like(f), np.zeros_like(w)
    for r in (3, 9, 27):
        k = (2 * r + 1, 2 * r + 1)
        wb = cv2.GaussianBlur(w, k, 0)
        fb = cv2.GaussianBlur(f * w[..., None], k, 0)
        take = (wacc < 1e-3) & (wb > 1e-3)
        acc[take] = fb[take] / wb[take, None]; wacc[take] = 1
    est = np.where(wacc[..., None] > 0, acc, f)
    edge = ((m > 0.02) & (m < 0.98))[..., None]
    t = np.clip((0.98 - m) / 0.96, 0, 1)[..., None]              # the more transparent, the more of the estimate
    return np.where(edge, f * (1 - t) + est * t, f).clip(0, 255).astype(np.uint8)

def is_oom(e):
    s = str(e).lower(); return "out of memory" in s or "mps backend out of memory" in s

def predict(net, rgb, size, dev, half):
    x = np.asarray(rgb.resize((size, size), Image.BICUBIC), dtype=np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    t = torch.from_numpy(x.transpose(2, 0, 1)).unsqueeze(0).float().to(dev)
    if half: t = t.half()
    with torch.no_grad():
        return net(t)[-1].sigmoid().float().cpu().numpy()[0, 0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--model", default="hr", choices=MODELS)       # hr won the 2026-10-19 test (crispest, cleanest)
    ap.add_argument("--size", type=int, default=0)
    ap.add_argument("--precision", default="auto", choices=["auto", "half", "full"])
    ap.add_argument("--mask")
    ap.add_argument("--no-refine", action="store_true")
    ap.add_argument("--keep-edge-colour", action="store_true")
    a = ap.parse_args()
    prof = _prof or machine_profile()
    dev = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    half = dev != "cpu" and (a.precision == "half" or (a.precision == "auto" and prof.get("precision") == "half"))
    size = a.size or (1024 if a.model == "base" else min(2048, prof.get("size") or 2048))
    net = AutoModelForImageSegmentation.from_pretrained(MODELS[a.model], trust_remote_code=True).to(dev).eval()
    if half: net = net.half()
    im = Image.open(a.src)
    if im.mode in ("I;16", "I;16B", "I"): im = im.point(lambda v: v / 256)
    rgb = im.convert("RGB")
    W, H = rgb.size
    tries = [(half, size)] + ([(True, size)] if not half and dev != "cpu" else []) + \
            [(dev != "cpu", s) for s in (1536, 1024) if s < size]
    pred = None
    for h_, s_ in tries:
        try:
            if h_ and not half: net = net.half(); half = True
            pred = predict(net, rgb, s_, dev, h_); size = s_; break
        except RuntimeError as e:
            if not is_oom(e): raise
            print(f"GPU memory ran out at {s_} ({'half' if h_ else 'full'} precision), trying smaller", flush=True)
            if dev == "mps": torch.mps.empty_cache()
            if dev == "cuda": torch.cuda.empty_cache()
    if pred is None: sys.exit("the cut-out did not fit in this computer's GPU memory even at 1024")
    m = cv2.resize(pred, (W, H), interpolation=cv2.INTER_CUBIC).clip(0, 1).astype(np.float32)
    if not a.no_refine:                                           # snap the upscaled matte to the full-res edges
        g = np.asarray(rgb.convert("L"), dtype=np.float32) / 255.0
        r = max(3, int(round(min(W, H) / size * 4)) | 1)
        m = guided(g, m, r, 1e-4).clip(0, 1)
    alpha = (m * 255).round().astype(np.uint8)
    px = np.asarray(rgb)
    if not a.keep_edge_colour:                                    # take the backdrop's colour out of the soft edge pixels
        px = decontaminate(px, m)
    out = np.dstack([px, alpha])
    Image.fromarray(out, "RGBA").save(a.out, optimize=False, compress_level=6)
    if a.mask: Image.fromarray(alpha, "L").save(a.mask)
    print(f"ok {W}x{H} model {a.model} at {size}, {'half' if half else 'full'} precision on {dev}")

if __name__ == "__main__":
    main()
