# One dark for the whole puppet: every skin piece's dark (body, head, limbs) is set to the body's dark, so pieces cut
# from different drawings (the original, generative fills, drawn joint balls) never show a tone step where they meet.
# Pale lines (fingers, folds) stay as drawn; on the body and head, hairline pale seams left where two fills were joined
# (at most a few pixels wide, inside the dark) are filled with the dark. Cloth keeps its drawing. Run on a finished
# rig folder; the rig scripts call it last.
import json, os, sys
import cv2
import numpy as np
from PIL import Image

LUM = np.array([0.299, 0.587, 0.114], np.float32)
SEAMS = ("body", "head")


def one_dark(rig_dir, keep=None):
    """keep: pieces that keep their drawing (cloth, props); default: rig.json's "keep_drawing" list"""
    rig = json.load(open(os.path.join(rig_dir, "rig.json")))
    keep = set(keep if keep is not None else rig.get("keep_drawing", []))
    def load(n): return np.asarray(Image.open(os.path.join(rig_dir, n + ".png"))).astype(np.float32)
    b = load("body"); lb = b[..., :3] @ LUM
    target = np.median(b[..., :3][(b[..., 3] > 250) & (lb < 90)], axis=0)
    for n in rig["pieces"]:
        if n in keep: continue
        a = load(n); lum = a[..., :3] @ LUM
        if n in SEAMS:
            fig = (a[..., 3] > 128).astype(np.uint8); inset = cv2.distanceTransform(fig, cv2.DIST_L2, 5)
            pale = ((lum > 90) & (fig > 0)).astype(np.uint8)
            k, lab = cv2.connectedComponents(pale, connectivity=8)
            thick = cv2.distanceTransform(pale, cv2.DIST_L2, 5)
            wide = np.zeros(k, bool); np.maximum.at(wide, lab.ravel(), (thick > 3.5).ravel())
            seam = (lab > 0) & ~wide[lab] & (inset > 4)
            a[..., :3][seam] = target; lum = a[..., :3] @ LUM
        w = np.clip((130 - lum) / 50, 0, 1)[..., None]
        a[..., :3] = a[..., :3] * (1 - w) + target * w
        Image.fromarray(a.round().astype(np.uint8), "RGBA").save(os.path.join(rig_dir, n + ".png"))
    return target


if __name__ == "__main__":
    # one_dark.py <rig folder> [cloth or prop piece ...]
    print(sys.argv[1], "dark", one_dark(sys.argv[1], sys.argv[2:] or None).round())
