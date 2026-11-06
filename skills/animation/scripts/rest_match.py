# At its own pose a puppet must look exactly like the drawing. Joint balls, capsules and other filler drawn into a limb
# piece are there for the moments a joint turns; wherever such filler would show at rest (not covered by a piece in
# front of it) over a part of the drawing that is light (cloth, paper edge, background), it is removed, so the limb's
# visible outline is always the drawn one. Hidden filler is kept: it is what closes the joint when the limb moves.
# Run on a finished rig folder; the rig scripts call it before one_dark.
import json, os
import numpy as np
from PIL import Image

LUM = np.array([0.299, 0.587, 0.114], np.float32)


def match_drawing(rig_dir, drawing, pieces, skip=()):
    """drawing: path of the cut-out the pieces were cut from; pieces: the limb pieces to trim (skip: pieces that are
    deliberately redrawn, such as a replaced foot)"""
    rig = json.load(open(os.path.join(rig_dir, "rig.json"))); W, H = rig["size"]
    import cv2
    D = np.asarray(Image.open(drawing)).astype(np.float32)
    pale = np.clip(((D[..., :3] @ LUM) - 110) / 60, 0, 1)
    fig = (D[..., 3] > 128).astype(np.uint8); inset = cv2.distanceTransform(fig, cv2.DIST_L2, 5)
    # light = outside the figure, its outer paper rim, or cloth (wide pale areas); a thin pale line inside the figure
    # (the paper edge drawn between two parts) is not: trimming a limb along it cuts a notch that shows once it moves
    wide = cv2.morphologyEx((pale > 0.5).astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    light = pale * np.maximum(wide.astype(np.float32), (inset < 40).astype(np.float32))
    light = np.maximum(light, 1 - D[..., 3] / 255)               # outside the drawing counts as light
    def load(n):
        p = rig["pieces"][n]; a = np.asarray(Image.open(os.path.join(rig_dir, n + ".png"))).astype(np.float32)
        return p, a
    order = sorted(rig["pieces"], key=lambda k: -rig["pieces"][k]["z"])
    covered = np.zeros((H, W), np.float32); trimmed = {}
    for n in order:                                              # front to back
        p, a = load(n); x, y, w, h = p["x"], p["y"], p["w"], p["h"]
        al = a[..., 3] / 255
        if n in pieces and n not in skip:
            vis = 1 - covered[y:y + h, x:x + w]
            dark = np.clip((150 - (a[..., :3] @ LUM)) / 40, 0, 1)   # the piece adds dark here
            cut = vis * light[y:y + h, x:x + w] * dark
            new = al * (1 - cut)
            trimmed[n] = int(((al > 0.5) & (new <= 0.5)).sum())
            a[..., 3] = new * 255
            Image.fromarray(a.round().astype(np.uint8), "RGBA").save(os.path.join(rig_dir, n + ".png"))
            al = new
        covered[y:y + h, x:x + w] = 1 - (1 - covered[y:y + h, x:x + w]) * (1 - al)
    return trimmed
