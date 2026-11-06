# logo.json

All coordinates are in units of **R** (the radius chosen in step 2), origin at the logo centre, **y down**
(so up is negative y). `R` in the file is only how many SVG units one R becomes; 500 is a good value.

```json
{
  "name": "northfield",                    // output file prefix
  "title": "Full name of the organisation",
  "viewBox": [1760, 880],                  // width, height of the full lockup in SVG units
  "centre": [440, 440],                    // where the emblem centre sits in that box
  "R": 500,
  "order": 6,                              // how many times `segment` repeats round the centre; 1 = no repeat
  "emblem_half": 0.88,                     // half-size (in R) of the square emblem/art outputs
  "inks": {"teal": "#2A9D8F", "slate": "#4A5A73"},
  "fonts": {"Khand": {"500": "fonts/Khand-Medium.ttf"}},     // family -> weight -> file, relative to the spec
  "segment": [ ...shapes drawn once pointing "up", then repeated... ],
  "once":    [ ...shapes that appear a single time (a centre ring, an outer border)... ],
  "ring_text": [ ...text on a circle... ],
  "wordmark": { ...stacked or single-line text beside the emblem... }
}
```
(Comments are for this page only: real JSON has none.)

## Shapes

| type | fields | notes |
|---|---|---|
| `polygon` | `ink`, `points: [[x,y],...]`, optional `round` | Filled. `round` (in R) softens corners slightly, e.g. 0.008. |
| `polyline` | `ink`, `width`, `points` *or* `paths: [[[x,y],...], ...]`, optional `cap` | Constant-width line(s) along centre-lines. `cap` is `round` (default), `butt` or `square`. |
| `ring` | `ink`, `centre`, `r`, `width` | Circle outline; `r` is to the middle of the stroke. |
| `disc` | `ink`, `centre`, `r` | Filled circle. |

`ink` is a key of `inks` or a hex colour.

## Ring text

```json
{"text": "TOWARDS A NEW EPISTEME", "family": "Josefin Sans", "weight": 700, "ink": "green",
 "side": "top", "inner": 0.718, "outer": 0.826, "from": 190, "to": 349}
```
- `inner` / `outer`: the radial band the capital letters occupy. The font size is set so caps fill it exactly.
- `from` / `to`: angles of the first and last letter, clockwise from 3 o'clock (270 is straight up).
  Letter-spacing is computed so the text spans exactly that arc.
- `side: "top"`: reads clockwise, tops pointing outward. `side: "bottom"`: reads left to right under the
  emblem, tops pointing to the centre; give `from` as the left end and `to` as the right end.
- `"italic": true` slants a face that has no italic.

## Wordmark

```json
{"family": "Khand", "weight": 500, "ink": "navy", "anchor": "middle",
 "rows": [["Northfield", 1.652, -0.205, 1.183], ["Makers Guild", 1.652, 0.205, 1.500]]}
```
Each row is `[text, x, baseline y, measured width]`. `x` is the row's centre for `anchor: "middle"`, its left
edge for `"start"`. The size is the median of what each row's width implies; the builder prints every row's
value and the spread. Add `"size"` to fix it by hand.
