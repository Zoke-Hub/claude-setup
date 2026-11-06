#!/usr/bin/env python3
"""Build clean SVGs (and PNGs) of a logo from a spec of measured shapes and live text.  (logo-recreation by Zoke)

    build.py <logo.json> [--png 2.5]

Writes next to the spec: <name>_logo.svg (everything), <name>_emblem.svg (art + ring text), <name>_art.svg
(art only, used by check.py). --png also renders each at that scale, transparent. See references/spec.md.
All coordinates in the spec are in units of R, origin at the logo centre, y down.
"""
import argparse, json, math, sys
from pathlib import Path
from PIL import ImageFont
sys.path.insert(0, str(Path(__file__).parent))
from lib import render_svg, CREDIT
ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("--png", type=float)
a = ap.parse_args()
S = json.loads(Path(a.spec).read_text()); here = Path(a.spec).resolve().parent
R = S.get("R", 500.0); CX, CY = S["centre"]; inks = S["inks"]; order = S.get("order", 1)
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")
xy = lambda p: f"{f(CX + p[0] * R)} {f(CY + p[1] * R)}"
ink = lambda k: inks.get(k, k)

def shape(e):
    c, t = ink(e["ink"]), e["type"]
    if t == "polygon":
        d = "M" + "L".join(xy(p) for p in e["points"]) + "Z"
        return f'<path d="{d}" fill="{c}" stroke="{c}" stroke-width="{f(e.get("round", 0) * R)}" stroke-linejoin="round"/>'
    if t == "polyline":
        paths = e["paths"] if "paths" in e else [e["points"]]
        d = "".join("M" + "L".join(xy(p) for p in pts) for pts in paths)
        return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{f(e["width"] * R)}" stroke-linecap="{e.get("cap", "round")}" stroke-linejoin="round"/>'
    if t in ("ring", "disc"):
        x, y = e["centre"]; base = f'<circle cx="{f(CX + x * R)}" cy="{f(CY + y * R)}" r="{f(e["r"] * R)}"'
        return base + (f' fill="{c}"/>' if t == "disc" else f' fill="none" stroke="{c}" stroke-width="{f(e["width"] * R)}"/>')
    sys.exit("unknown shape type " + t)

def art():
    seg = "".join(shape(e) for e in S.get("segment", []))
    uses = "".join(f'<use href="#segment" transform="rotate({f(360 / order * k)} {f(CX)} {f(CY)})"/>' for k in range(1, order))
    return f'<g id="segment">{seg}</g>{uses}' + "".join(shape(e) for e in S.get("once", []))

def font(family, weight, size=1000):
    return ImageFont.truetype(str(here / S["fonts"][family][str(weight)]), size)
def P(r, deg): return f"{f(CX + r * R * math.cos(math.radians(deg)))} {f(CY + r * R * math.sin(math.radians(deg)))}"

def ring_text():
    defs, out = [], []
    for i, t in enumerate(S.get("ring_text", [])):
        ft = font(t["family"], t["weight"]); b = ft.getbbox("H"); cap = (b[3] - b[1]) / 1000
        size = (t["outer"] - t["inner"]) * R / cap                       # caps exactly fill the measured band
        top = t.get("side", "top") == "top"                              # top: baseline on the inner radius, reading clockwise
        base = t["inner"] if top else t["outer"]                         # bottom: baseline on the outer radius, tops to the centre
        sweep = (t["to"] - t["from"]) % 360 if top else (t["from"] - t["to"]) % 360
        arc = math.radians(sweep) * base * R
        track = (arc - ft.getlength(t["text"]) * size / 1000) / max(1, len(t["text"]) - 1)
        # browsers drop a glyph whose middle (advance + letter-spacing) falls past the path's end, so with wide tracking
        # the last letter vanished; run the path one letter-space further (letter positions are unchanged)
        ext = math.degrees(max(track, 0) / (base * R)); end = t["to"] + ext if top else t["to"] - ext
        defs.append(f'<path id="arc{i}" d="M{P(base, t["from"])}A{f(base * R)} {f(base * R)} 0 {1 if sweep + ext > 180 else 0} {1 if top else 0} {P(base, end)}"/>')
        style = ' font-style="italic"' if t.get("italic") else ""
        out.append(f'<text font-family="{t["family"]}, sans-serif" font-weight="{t["weight"]}"{style} font-size="{f(size)}" letter-spacing="{f(track)}" fill="{ink(t["ink"])}"><textPath href="#arc{i}">{t["text"]}</textPath></text>')
    return ("<defs>" + "".join(defs) + "</defs>" + "".join(out)) if out else ""

def wordmark():
    w = S.get("wordmark")
    if not w: return ""
    ft = font(w["family"], w["weight"])
    sizes = sorted(row[3] * R / (ft.getlength(row[0]) / 1000) for row in w["rows"])     # row = [text, x, baseline y, width]
    size = w.get("size") or sizes[len(sizes) // 2]
    print("wordmark size per row:", [round(s, 1) for s in sizes], "-> using", round(size, 1), f"(spread {100 * (sizes[-1] - sizes[0]) / size:.0f}%)")
    rows = "".join(f'<text x="{f(CX + r[1] * R)}" y="{f(CY + r[2] * R)}">{r[0]}</text>' for r in w["rows"])
    return f'<g font-family="{w["family"]}, sans-serif" font-weight="{w["weight"]}" font-size="{f(size)}" text-anchor="{w.get("anchor", "middle")}" fill="{ink(w["ink"])}">{rows}</g>'

faces = "".join(f'@font-face{{font-family:"{fam}";font-weight:{wt};src:url("{path}")}}' for fam, ws in S.get("fonts", {}).items() for wt, path in ws.items())
def svg(box, body, extra=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(f(v) for v in box)}"{extra}>\n<!-- {CREDIT} -->\n<title>{S.get("title", S["name"])}</title>\n<metadata>{CREDIT}</metadata>\n<style>{faces}</style>\n{body}\n</svg>\n'
E = S.get("emblem_half", 0.9); sq = [CX - E * R, CY - E * R, 2 * E * R, 2 * E * R]
W, H = S["viewBox"]
outs = {"logo": (svg([0, 0, W, H], ring_text() + art() + wordmark()), W, H),
        "emblem": (svg(sq, ring_text() + art()), 2 * E * R, 2 * E * R),
        "art": (svg(sq, art(), f' data-half="{E}"'), 2 * E * R, 2 * E * R)}
for k, (text, w, h) in outs.items():
    p = here / f'{S["name"]}_{k}.svg'; p.write_text(text); print("wrote", p)
    if a.png: render_svg(p, p.with_suffix(".png"), w, h, a.png); print("wrote", p.with_suffix(".png"))
