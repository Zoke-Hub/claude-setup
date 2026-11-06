---
name: logo-recreation
description: Rebuild a small, blurry or low-quality logo as clean vector art (SVG plus transparent PNG) by measuring the original and redrawing it as geometry with live text, never by auto-tracing. Use whenever someone wants to recreate, redraw, rebuild, vectorise, sharpen, upscale or "make an SVG / a good-quality version" of a logo, emblem, seal, badge, crest or icon from a screenshot, a tiny web image or a photo, or when a traced or upscaled logo "looks bad" or "doesn't match the original". Also use when asked to find a better-quality copy of a logo online, because that search is the first step here.
---

# Logo recreation

*By Zoke.* Every SVG it builds carries the credit in a comment and `<metadata>`, and every PNG in its
Author / Software / Comment text fields, without touching the artwork. Keep them in.

Rebuild a logo so it is clean at any size and still *is* that logo. The method is measurement, not tracing:
find the sharpest original, average away its blur, read real coordinates off it, redraw each shape as geometry,
set the lettering as live text in a matched typeface, and prove the result by overlaying it on the original.

Why not trace: an auto-trace of a 200 px logo copies the blur. Small text becomes blobs and thin lines merge.
Why not eyeball: guessed proportions look "like a logo" but not like *this* logo, and the owner sees it at once.
Both were tried on the logo this skill was built from; both were rejected. Measuring is what worked.

Everything is in this folder. `$SK` below means this skill's folder.

- `scripts/symmetry.py`: finds the repeat count and true centre, averages the repeats into a sharper image
- `scripts/grid.py`: enlarges a region under a coordinate grid for reading off corners
- `scripts/measure_ink.py`: measures a colour's box, its ring band and angles, or its text rows
- `scripts/fonts.py`: downloads candidate typefaces, compares them, and tests the fit
- `scripts/build.py`: turns a spec of measured shapes and text into SVGs and PNGs
- `scripts/check.py`: scores the rebuild against the original and draws the overlay
- `references/spec.md`: the spec format. Read it before writing a `logo.json`.
- `examples/northfield/`: a finished case on a made-up logo (spec, blurry 300 px source crop, outputs). Use it as
  the pattern and the quality bar.

Scripts need Python 3.10+ with `pillow` and `numpy`, and Chrome or Chromium for rendering. If no Python on the
machine has those two packages, make one: `uv venv .logo-venv && uv pip install --python .logo-venv/bin/python pillow numpy`.
Work in a `logo-work/` folder next to the user's file, and put the deliverables where they asked.

## 1. Get the best original first

A sharper source beats any amount of processing, so spend five minutes looking before measuring. Ask the user
only if they have not already said to go ahead and search.

- The organisation's own site: logo files, the favicon, `og:image`, press or brand pages, and PDFs
  (reports and brochures often embed the logo larger, sometimes as vector).
- Official posters and social posts, which usually carry the logo bigger than the website does.
- An SVG or a large PNG ends the job: deliver that and say where it came from.

Keep every candidate, note where each came from, and view them side by side at the same scale. Take two or
three of the sharpest forward: they can be averaged, and they cross-check each other.
Say up front if nothing better than the user's file exists, and roughly how long the rebuild will take.

## 2. Find the structure and sharpen it

Most emblems repeat around a centre. Averaging the repeats cancels blur and JPEG noise, which turns a
250 px logo into something measurable.

```bash
python $SK/scripts/symmetry.py source.png --radius 85.2 --centre 76,74 --out logo-work/a
```

- `--radius` is your unit, **R**: any clear radius in the image (an outer ring, the outer edge of the art).
  Every later number is in R, so pick something you can also find in the other sources.
- The script scores each repeat count from 0 (chance) to 1 (perfect) and picks the highest count that still
  scores well. The real count and its divisors all score high (an 8-fold logo also passes 2 and 4).
  Below 0.5 it reports no symmetry; text and lopsided marks land around 0.3 to 0.4.
- It searches for the centre itself. Do not assume the art is centred on its surrounding ring or badge:
  in real logos it can sit 5 to 10 px off, and that alone smears everything. Give `--centre` a rough guess
  when the image holds more than the emblem (a wordmark beside it pulls the search off centre).
- Lettering does not repeat, so keep text rings out of `--annulus`.
- Look at `sym.png`. Sharp edges mean the centre and count are right. A smear means they are not: pass
  `--centre` or `--order` and try again.
- With a second source measured using the same R: `symmetry.py --average out.png a/sym.png b/sym.png`.
- No rotational symmetry (wordmarks, mascots, asymmetric marks): the script says so. Skip the averaging and
  measure the sharpest source directly, using mirror symmetry and repeated elements wherever they exist.

## 3. Read the geometry off a grid

```bash
python $SK/scripts/grid.py logo-work/a/sym.png --window=-0.44,-0.74,0.44,0.04 --out logo-work/zoom.jpg
```

Zoom into **one** repeat (plus a little of its neighbours) and write down every corner in R units.

- Decide what each mark *is* before recording points: a filled polygon, a line of constant width, a ring,
  a dot. Record polygons by their corners and lines by their centre-line plus one width.
- Do not assume mirror symmetry inside a repeat. Many marks are deliberately lopsided (arms at different
  angles, arrows that chase one way). Read both sides.
- Use the neighbours as a second reading: rotate a neighbour's corner back by the repeat angle and average
  it with the first. Disagreement over about 0.01 R means one reading is wrong.
- Line widths, gaps between parallel lines, ring radii and dot sizes are measurements too. Take them.
- Sample colours from the solid core of each shape, not its edges, where blur has diluted them.

## 4. Measure the lettering

Text is set as live text, so measure where it sits and how big it is; do not draw letters.

```bash
# text on a circle: radial band and start/end angles
python $SK/scripts/measure_ink.py source.png --ink "#D98F2B" --centre 74.8,74.8 --radius 85.2 --rmin 0.70 --rmax 0.84
# a stacked wordmark: one line per row with its width and centre
python $SK/scripts/measure_ink.py lockup.png --ink "#24304F" --region 150,20,300,130 --rows
```

- Use the source that shows the whole lockup for positions, even if it is the blurriest; use the sharpest
  for shapes. Convert its pixels to R through a radius both share.
- Blur fattens small text. A measured cap height on tiny lettering is too tall by a pixel or two each side.
- Note which way ring text reads and where its tops point (out at the top, in at the bottom, usually).

## 5. Match the typefaces

```bash
python $SK/scripts/fonts.py get "Khand:500,600" "Josefin Sans:700" --out logo-work/fonts
python $SK/scripts/fonts.py sheet --ref wordmark_crop.png --text "Northfield" --fonts logo-work/fonts/*.ttf --out logo-work/fonts.jpg
python $SK/scripts/fonts.py fit --font logo-work/fonts/Khand-500.ttf "Northfield=1.18" "Makers Guild=1.50"
```

- Shortlist by the tell-tale letters: a, g, t, R, M, W, the shape of bowls, how terminals are cut.
- `fit` is the real test. A matching font gives nearly the same size for every row; a spread above about 5%
  means the font, the weight, or one row's width is wrong.
- Stick to openly licensed fonts so the files can ship with the logo.
- A slanted face with no italic: set `"italic": true`. The browser slants it; other apps may not.
- Typeface matching is by eye. Say so in the report; never claim to know the designer's font.

## 6. Build

Write `logo.json` (format in `references/spec.md`, pattern in `examples/northfield/logo.json`), then:

```bash
python $SK/scripts/build.py logo-work/logo.json --png 2.5
```

One repeat goes in `segment` and is copied round the centre; things that appear once go in `once`.
The builder sizes ring text to its measured band, spaces it to span the measured angles, and sizes the
wordmark from the measured row widths.

## 7. Check, fix, repeat

```bash
python $SK/scripts/check.py logo-work/NAME_art.svg logo-work/a/sym.png --inks "#2A9D8F,#4A5A73" --window=-0.44,-0.74,0.44,0.04
```

Look at the overlay yourself. The red outlines of the rebuild must sit on the original's edges everywhere:
that is the pass mark. Where they do not, re-read those corners on the grid and rebuild. The overlap score is
for comparing one attempt with the next; blur in the original keeps it well under 1 (about 0.75 or more is a visually exact match on solid shapes; the
bundled example's teal scores 0.87 from its 300 px source), and thin lines score lower than solid shapes.

Then compare the full lockup with the original side by side at the same size: lettering weight, size,
spacing, and the gap between mark and wordmark. Fix what differs before showing anyone.

## 8. Deliver and report

Give the user, in the folder they asked for:
- `NAME_logo.svg`, `NAME_emblem.svg`, `NAME_art.svg` and their transparent PNGs
- the `fonts/` folder (the SVGs load fonts from it, and editing apps need them installed)
- `logo.json`, so any number can be adjusted and rebuilt
- a white-background preview image, shown to them directly

Report in plain words: where the source came from, what was measured, what was matched by eye (typefaces
always), any row or shape that still differs and by how much, and that it is a redraw, not the owner's file.
Do not hand over an auto-trace, and do not call it a match before the overlay says so.
