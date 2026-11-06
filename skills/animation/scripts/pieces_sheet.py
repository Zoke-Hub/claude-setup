# Cut-out pieces sheet for review before animating. Reads a rig folder as it is (changes nothing) and lays out:
#  - every piece at the drawing's resolution (scaled), loosely pulled apart from where it sits, with its name and a red
#    dot where it turns;
#  - only if asked (--focus): chosen pieces again on their own, larger. By default every piece appears once.
#   pieces_sheet.py <rig dir> <out.jpg> [--focus body armU,armF ...] [--labels labels.json] [--paper R,G,B]
#                   [--spread 1.35] [--scale 0.55] [--nudge nudge.json] [--title "..."]
# --focus: one group per argument, pieces joined by commas (a limb's pieces). labels.json: {"piece": "plain name"}.
# nudge.json: {"piece": [dx, dy]} extra pull-apart in source px, for pieces that still overlap.
import argparse, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def centre(p): return np.array([p["x"] + p["w"] / 2, p["y"] + p["h"] / 2])


def layout(rig, ims, only, spread, sc, paper, names, nudge=None):
    P = rig["pieces"]; nudge = nudge or {}
    cb = centre(P["body"]) if "body" in P else np.mean([centre(P[k]) for k in P], 0)
    pos = {k: np.array([P[k]["x"], P[k]["y"]]) + (centre(P[k]) - cb) * (spread - 1) + np.array(nudge.get(k, (0, 0))) for k in only}
    lo = np.min([pos[k] for k in only], 0) - 120
    hi = np.max([pos[k] + [P[k]["w"], P[k]["h"]] for k in only], 0) + [800, 120]          # room for the labels
    W, H = ((hi - lo) * sc).astype(int)
    img = Image.new("RGBA", (W, H), paper + (255,)); d = ImageDraw.Draw(img); f = font(34); marks = []
    for k in sorted(only, key=lambda k: P[k]["z"]):
        x, y = ((pos[k] - lo) * sc).astype(int)
        img.alpha_composite(ims[k].resize((max(1, int(P[k]["w"] * sc)), max(1, int(P[k]["h"] * sc))), Image.LANCZOS), (x, y))
        marks.append((k, x, y, (np.array(P[k]["pivot"]) - [P[k]["x"], P[k]["y"]]) * sc + [x, y]))
    for k, x, y, pv in marks:
        d.ellipse([pv[0] - 9, pv[1] - 9, pv[0] + 9, pv[1] + 9], fill=(220, 40, 40), outline=(255, 255, 255), width=3)
        d.text((x + 4, max(y - 40, 4)), names.get(k, k), font=f, fill=(25, 25, 25), stroke_width=4, stroke_fill=paper)
    return img


def titled(img, title, paper):
    big = font(54); tw = int(ImageDraw.Draw(img).textlength(title, font=big)) + 60
    out = Image.new("RGBA", (max(img.width, tw), img.height + 90), paper + (255,))
    out.alpha_composite(img, (0, 90)); ImageDraw.Draw(out).text((24, 18), title, font=big, fill=(25, 25, 25))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("rig"); ap.add_argument("out")
    ap.add_argument("--focus", nargs="*", default=[]); ap.add_argument("--labels"); ap.add_argument("--nudge")
    ap.add_argument("--paper", default="182,196,152"); ap.add_argument("--spread", type=float, default=1.35)
    ap.add_argument("--scale", type=float, default=0.55); ap.add_argument("--title", default="Every piece, pulled apart")
    a = ap.parse_args()
    paper = tuple(int(v) for v in a.paper.split(","))
    rig = json.load(open(os.path.join(a.rig, "rig.json")))
    ims = {k: Image.open(os.path.join(a.rig, k + ".png")).convert("RGBA") for k in rig["pieces"]}
    names = json.load(open(a.labels)) if a.labels else rig.get("labels", {})
    nudge = json.load(open(a.nudge)) if a.nudge else {}
    panels = [titled(layout(rig, ims, list(rig["pieces"]), a.spread, a.scale, paper, names, nudge), a.title, paper)]
    row = []
    for grp in a.focus:
        ks = grp.split(",")
        row.append(titled(layout(rig, ims, ks, 1.0, a.scale * 1.45, paper, names), " + ".join(names.get(k, k) for k in ks) + ", on its own", paper))
        if len(ks) > 1:   # the limb's pieces apart, down its length
            P = rig["pieces"]; apart = {k: (0, 260 * i) for i, k in enumerate(sorted(ks, key=lambda k: P[k]["y"]))}
            row.append(titled(layout(rig, ims, ks, 1.0, a.scale * 1.45, paper, names, apart), "its pieces apart", paper))
    W = max([panels[0].width] + [sum(p.width for p in row) + 40 * len(row)]) + 80
    H = panels[0].height + (max(p.height for p in row) + 60 if row else 0) + 80
    sheet = Image.new("RGBA", (W, H), paper + (255,)); sheet.alpha_composite(panels[0], (40, 40))
    x, y = 40, panels[0].height + 80
    for p in row: sheet.alpha_composite(p, (x, y)); x += p.width + 40
    ImageDraw.Draw(sheet).text((W - 700, H - 60), "red dot: where the piece turns", font=font(34), fill=(25, 25, 25))
    sheet.convert("RGB").save(a.out, quality=90)
    print("ok", a.out, sheet.size)
