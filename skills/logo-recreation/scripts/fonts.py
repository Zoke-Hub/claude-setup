#!/usr/bin/env python3
"""Fetch candidate typefaces and compare them with the logo's lettering.  (logo-recreation by Zoke)

    fonts.py get  "Khand:500,600" "Josefin Sans:700" --out fonts/          download from Google Fonts (open licences)
    fonts.py sheet --ref crop.png --text "Northfield" --fonts fonts/*.ttf --out sheet.jpg
    fonts.py fit  --font fonts/Khand-500.ttf "Northfield=1.18" "Makers Guild=1.50" ...   widths in any one unit

`sheet` draws every candidate at the reference crop's height beside it: compare letter shapes (a, g, t, R, M, W).
`fit` is the real test: a matching font gives nearly the same size for every row. A row that disagrees by more
than ~5% means the font, or that row's measured width, is wrong.
"""
import argparse, re, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["get", "sheet", "fit"]); ap.add_argument("items", nargs="*")
ap.add_argument("--out"); ap.add_argument("--ref"); ap.add_argument("--text"); ap.add_argument("--fonts", nargs="*"); ap.add_argument("--font")
a = ap.parse_args()
if a.cmd == "get":
    out = Path(a.out or "fonts"); out.mkdir(parents=True, exist_ok=True)
    q = "&".join("family=" + f.split(":")[0].replace(" ", "+") + ":wght@" + f.split(":")[1].replace(",", ";") for f in a.items)
    css = urllib.request.urlopen(urllib.request.Request("https://fonts.googleapis.com/css2?" + q, headers={"User-Agent": "curl/8"})).read().decode()
    for fam, wt, url in re.findall(r"font-family: '([^']+)';[^}]*?font-weight: (\d+);[^}]*?src: url\(([^)]+)\)", css, re.S):
        p = out / f"{fam.replace(' ', '')}-{wt}.ttf"; urllib.request.urlretrieve(url, p); print("saved", p)
elif a.cmd == "sheet":
    ref = Image.open(a.ref).convert("RGB"); H = 150; ref = ref.resize((int(ref.width * H / ref.height), H), Image.LANCZOS)
    rows = [("reference", ref)]
    for f in a.fonts:
        font = ImageFont.truetype(f, 400); b = font.getbbox(a.text); im = Image.new("RGB", (b[2] - b[0] + 40, b[3] - b[1] + 40), (255, 255, 255))
        ImageDraw.Draw(im).text((20 - b[0], 20 - b[1]), a.text, font=font, fill=(20, 20, 20)); rows.append((Path(f).stem, im.resize((int(im.width * H / im.height), H), Image.LANCZOS)))
    sheet = Image.new("RGB", (max(r[1].width for r in rows) + 20, (H + 34) * len(rows)), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(rows): sheet.paste(im, (10, i * (H + 34) + 22)); d.text((10, i * (H + 34) + 4), name, fill=(200, 0, 0))
    sheet.save(a.out or "font-sheet.jpg", quality=90); print("wrote", a.out or "font-sheet.jpg")
else:
    font = ImageFont.truetype(a.font, 1000); sizes = []
    for item in a.items:
        text, width = item.rsplit("=", 1); s = float(width) / (font.getlength(text) / 1000); sizes.append(s); print(f"  {text!r:34} -> size {s:.3f}")
    mid = sorted(sizes)[len(sizes) // 2]; print(f"median size {mid:.3f}; spread {100 * (max(sizes) - min(sizes)) / mid:.0f}% (under ~5% = the font fits)")
