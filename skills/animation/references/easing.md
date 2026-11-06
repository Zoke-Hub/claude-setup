
# Animation easing: rules for motion graphics

Rules learned on client reels and approved by the user. Apply them to every animated graphic unless a brief says
otherwise. The look of entrances is summarised in `references/house/motion-rules.md`; this file holds the full rules.


## 1. One default curve

**Ease in 33 / ease out 90**, as the user calls it. It is a cubic-bezier with zero velocity at both keyframes:

| Where | Setting |
|---|---|
| After Effects (Keyframe Velocity) | first key **Outgoing influence 33%**, last key **Incoming influence 90%**, speed 0 on both |
| CSS / JS | `cubic-bezier(0.33, 0, 0.10, 1)` |
| Feel | quick start, long, soft settle into place |

**How the user's words map.** "Ease in 33" is how the move *leaves* the first keyframe. "Ease out 90" is how it *lands* on the last one. Do not flip it.

- The mapping was measured, not guessed. An area-chart reveal in a reference video was tracked frame by frame at 60 fps.
- The best fit was bezier (0.37, 0, 0.02, 1).
  - (0.33, 0, 0.10, 1) fits within **2.2% RMS**.
  - The reversed reading, (0.90, 0, 0.67, 1), is off by **49%**.

Progress values to sanity-check against:

| time | 10% | 25% | 50% | 75% | 90% | 100% |
|---|---|---|---|---|---|---|
| value | 4% | 40% | 83.5% | 97% | 99.6% | 100% |

Most of the movement happens in the first half; the second half is the settle.

```js
// JS: binary-search the bezier x, return y
const ease = bezier(.33, 0, .10, 1);
```
```python
# Python (A-roll snap zooms use the same curve)
EASE = bezier(.33, 0, .10, 1)
```

### Where it fits
**Pick each move's curve for that move; the house curve is one option, not the answer to every move (user, 2026-10-22).** It suits:
- text, circles, bars, masks, wipes, spokes and lines
- particle gathering and dot swaps
- counters and highlighter sweeps
- focus pulls (soft-focus depth)
- **A-roll snap zooms** (where an editing skill adds them; see that skill for when and how far)

**Choosing a curve.** Choose for each move
(entering, exiting, how far it travels, how fast): for example a gentle ease-in for an exit that leaves the frame, or a
softer settle for a long camera travel. Linear is for continuous ambient drift that never stops (a slow rotation).
Never use overshoot, bounce or elastic: the user rejected them, along with out-only eases that land abruptly.


## 2. Timing

- **25 fps, always.** Do not change the frame rate to get smoothness. Smoothness comes from the curve plus frame-exact rendering: seek the scene to `i / 25` for every output frame.
- **Durations ×1.5, minimum 0.75 s.** The curve front-loads the move, so durations written for an in-out ease look rushed. Have the timing helper apply `d × 1.5` (min 0.75 s) automatically.

  Typical durations as written in scene code (×1.5 on screen):

  | Element | Written duration |
  |---|---|
  | word | 0.6 |
  | circle grow | 0.45 |
  | wipe | 0.4–0.55 |
  | count-up | 1.6 |
  | highlight | 0.7–1.3 |

- **Sync to the voice.** Cue times are written in A-roll seconds, taken from word-level timestamps (the `local-transcribe` skill). An element starts on its word.
  - When the user asks for things to arrive earlier, shift the cue. Example: "circles appear 0.5 s early" means cue = word start − 0.5.
- **Scene start on a cut.** Begin entrances 0.2–0.35 s *before* the scene's first frame, so the first frame after the cut already shows content and is never blank.
- **Scene start mid-shot.** Use a circle wipe that opens from the centre over the A-roll. Clip the **whole stage** to the wipe circle, not just the background. Otherwise headers and other elements show over the presenter before the wipe reaches them.
- **Scene end.** Graphics end on an A-roll cut with a hard cut. No exit animation is needed at a cut.


## 3. Text animation

**Titles and single words unfold word by word from their baseline.** Each word starts as a flat line sitting on its
baseline and opens upward to full height: scale from about **58 % wide × 0 % tall to 100 %**, with opacity
0 → 100 %, on the default curve. Stagger is **~0.045 s** per word.

**Paragraphs unfold line by line** the same way: each line from about **40 % × 0 % to 100 %**, a quick start and a
soft settle, stagger **~0.1–0.15 s** per line (or ~0.018–0.03 s per word when a paragraph is split by word).

- Set `transform-origin` to the baseline (bottom of the line box), so the text grows up from where it sits.
- **Text scales only while it enters.** The unfold must end at exactly scale 1 with the transform removed; text never
  scales after it has landed (see section 4).
- Each word (or line) is its own `inline-block` span. A small helper should walk the DOM and wrap every word at any
  depth.

Splitting rules:
- Do **not** put word spans directly inside a `display:flex` box. Flex items drop the spaces between them, so "30 min" becomes "30min". Wrap the text in a `<div>` first.
- Split highlight phrases **before** splitting the paragraph (highlight spans are handled at scene init).
- SVG `<text>` counts as one word.
- Exits: fade out on the same curve. Do not slide or fold words out.


## 4. No wiggle: text must be perfectly still once it lands

The user saw text "wiggle slightly after it animates in". There were three causes, and each has a fix:

| Cause | Fix |
|---|---|
| Labels inside circles were scaled with the circle, so they re-rasterised during the long settle | Labels are **separate fixed-width boxes** placed over the circle and centred on whole pixels. They are never children of a scaling element. |
| Fractional `translateY` or scale during the settle (sub-pixel text) | The transform helper **rounds translations to whole pixels**, snaps the scale to exactly 1 above 0.998, and returns `none` once landed |
| Opacity of 0.999 or a blur of 0.03 px keeps the layer alive | Snap opacity to exactly **1** above 0.996; quantise blur to 0.25 px and set it to `none` when sharp |

More rules:
- No `will-change` on text.
- No percentage padding on flex items that hold text. Chrome sizes them with zero padding, so long words overflow to one side.
- Centre labels on a circle by computing `left`/`top` from the measured box and rounding.
- Large moving text, such as a number flying into a chart cell: round the translate to whole pixels and quantise the scale to 1-px size steps.

**Verify before every render:**
- A DOM check of every word on every frame: once a word has landed (opacity 1, no transform), its box, opacity and blur must not change until it fades out. Expected result: "0 words move after landing" for every scene.
- A pixel check of the last 1.6 s of each scene: only intentional graphic motion may remain (a ring that "breathes", drifting dots).


## 5. Photos, pieces, lines and the camera

Photos and pieces **slide in from some distance, often turning a little as they land, on a strong ease-out**
(`cubic-bezier(0, 0, 0, 1)` or close: they leave at full speed and spend the move settling), about 15–30 frames. A
fade on the same span is the base; a style may cut them in with the motion and no fade. Several pieces are staggered
(background, then the main photo, then side pieces, then small props); the stagger and the length come from the
voiceover and the time the frame has. Some can slide out from behind a photo. Photos may scale during a camera push.
Grade each picture (curves, levels, tint) so pieces from different sources sit together on the paper.

**Lines draw on** wherever there is a line (stems, rings, rules, routes, axes): a draw of 14–30 frames that eases into
its end (about `cubic-bezier(0.4, 0, 0.2, 1)`; long routes can settle longer).

**Camera moves** start gently and settle long (about `cubic-bezier(0.47, 0, 0.26, 1)`); a push-in on a frame can be an
even S-curve (about `cubic-bezier(0.68, 0, 0.31, 1)`). Frame tight; no zoom-out dip mid-pan; two moves in a row become
one curved move; a slight drift on the first frame rather than a dead-still one; a section change can be a cut.

These numbers are starting points: pick each move's curve and length for that move and its voiceover.

## 6. Highlighter (paper lines)

- **A solid bar wipes across the phrase**, one continuous bar per text line, not word-by-word fills. Per-word fills made the sweep step.
- The bars are measured with `getClientRects()` of the highlight span, **after** the words are split, because splitting can change the line breaks.
- The sweep runs across the total length of all lines on the same curve. A soft leading edge (about 22 px) appears only on the bar that is still filling.
- The bar sits behind the text, about 80% of the line height, starting about 13% from the top. Its colour comes from the project's palette; the text under it can turn from dark to light as the bar passes.
- Give sweeps enough time to glide: about 1.0–1.5 s written (×1.5 on screen) for a 60-character phrase. Cue the sweep on the spoken words.
- Use a highlight only where there is a lot of text, to pull attention to one word or line.


## 7. Numbers and counters

- Count up on the same curve: fast at first, then a long settle on the final value.
- Use **fixed-width digit slots** (the widest digit's width) so digits don't jitter while they change. Keep the decimal point fixed. When a tens digit appears, it grows to the left.
- Keep the number on screen as the hero, then FLIP it into its place in the next chart.
- Time any colour change on the number to when a wipe reaches it.


## 8. Graphic building blocks (all on the default curve)

- **Grow from a dot**: a small pin becomes a sphere, scaling from 0.12 to 1. The icon and label rise in about 0.1–0.2 s later.
- **Mask reveals** for bars and blocks (`clip-path: inset`), e.g. chart bars filling and timetable blocks filling from the bottom.
- **Focus pull**: whatever is not being talked about drops into soft focus (blur + fade back).
- **Wipes**: a circle wipe from the element being discussed (paper → slate cover, A-roll → graphic).
- **Particles**: dotted circles gather from scattered dots (per-particle curve) and drift linearly afterwards.
- **Swaps and paths**: items travel along a small arc (e.g. two items swapping places) with a 0.028 s stagger.


## 9. Checklist before sending a preview

1. Every move uses the default curve, or a different calm curve chosen for that move. Search the scene code for any bounce, elastic or overshoot easing.
2. Titles unfold word by word and paragraphs line by line from the baseline, landing at exactly scale 1; no text sits inside a scaling element.
3. The text-wiggle check reports 0 for every scene.
4. Contact sheets of each scene look right: no blank first frame on a cut, no element showing over the A-roll before a wipe.
5. The render is 25 fps and frame-exact.
6. On-screen figures and quotes trace back to the source document.
