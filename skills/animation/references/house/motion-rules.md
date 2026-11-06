---
name: motion-rules
description: How text, photos, lines, the camera and highlights move in motion graphics — titles unfold word by word from the baseline, paragraphs line by line, photos slide in on a strong ease-out (fade as the base), staggered to the voiceover; lines draw on; camera tight, one curved move instead of two, holds only between voiceover pieces; the texture on the world plane, moving with the camera, never showing an edge; a per-project finishing pass; pictures graded to sit together; a curve picked for each move; highlights as a bar wipe
metadata:
  type: feedback
---

How things enter and move in every motion graphic. The `references/easing.md` skill holds the full technical rules
(25 fps, durations, the no-wiggle checks, splitting text, counters); this note is the look.

- **Titles and single words** unfold **word by word from their baseline**: each word starts as a flat line on the
  baseline and opens upward to full height (scale about 58 % wide × 0 % tall → 100 %), fading in as it opens,
  staggered word by word.
- **Paragraphs** unfold **line by line** the same way (about 40 % × 0 % → 100 %): a quick start and a soft settle,
  one line after the next.
- **Text lands perfectly still:** the unfold ends at exactly scale 1 with no transform left, and text never scales
  after it has landed.
- **Photos and pieces** enter by sliding in from some distance, often turning a little as they land, on a strong
  ease-out (they leave at full speed and spend the move settling); a quick fade on the same span is the base, and a style
  can cut them in with the motion and no fade. Several pieces are staggered (background, then the main photo, then side
  pieces, then small props); the stagger and the length come from the voiceover and the time the frame has, not a fixed
  number. Some can slide out from behind a photo.
- **Lines draw on:** wherever there is a line (a stem, a ring, a rule, a route, an axis) it draws itself on rather than
  appearing; an axis can grow in steps as the story covers more of it.
- **Camera:** frame tight on what matters; no zoom-out dip in the middle of a pan; two moves in a row (across, then
  down) become one curved move; a slight drift rather than a dead-still first frame; a section change can be a cut.
  Each move is one smooth move from start to end: no stops, holds or extra steps inside it; the camera only holds or
  jumps between two voiceover pieces or at a cut.
- **Keep it flowing across a frame change:** what's on the next stop starts while the camera is still arriving, so the animation runs on instead of stopping and starting again at each frame.
- **Each frame shows only its own elements:** frame a stop so nothing from the previous stop's content is in view; only background elements may carry across, to keep the frame feeling continuous.
- **Texture lies on the world plane:** the paper texture belongs to the scene, not the screen. It covers the whole frame
  at every framing (tiled or sized so no edge ever shows), and moves and zooms with the camera like everything else, as
  if the camera were filming one flat sheet with the pieces on it. It usually sits just above the background paper,
  under the pieces. Where the camera zooms in and out a lot, key the texture's size along with the zooms so it never gets too small or too big on screen. The texture
  file changes per project and style.
- **Finishing pass:** a project can have a finish over everything (a static grain, a lower frame rate such as Posterize
  Time); its settings come per project, and the previews carry the same finish as the After Effects file.
- **Pictures sit in the frame:** grade each picture (curves, levels, tint) so pieces from different sources look like
  they belong together on the paper.
- **Curves:** pick each move's curve for that move (entering, exiting, the distance travelled, its speed). The house
  curve (ease in 33 / ease out 90, `cubic-bezier(0.33, 0, 0.10, 1)`) is one option, used only where it suits, never by
  reflex; for example a gentle ease-in for an exit, linear for continuous drift. Never bounce, elastic or overshoot.
- **Highlights:** a solid bar wipes across the phrase behind the text, one continuous bar per line; a project's look can
  give the bar a crooked, roughened edge. Where the bar is darker than the text, the text under it turns light as the bar
  passes so it stays readable. Use the project's palette for the bar.
- **Typewriters** reveal letters without fading each one in; titles and paragraphs otherwise use the unfolds above.

**Why:** these are the user's settled decisions for how motion should feel: calm, precise entrances with curves chosen per move.

**How to apply:** read this and `references/easing.md` before the first tween. If a project's brief or reference
says otherwise, the brief wins for that project. Related: [[reference-study-scope]].

**Use the house curve selectively (user, 2026-10-22):** don't reach for it on every move or cite it as the answer to every
motion question. Pick each move's curve for that move (entrance, exit, distance, speed) and use the house curve only where
it actually suits.

**From studying finished After Effects comps (2026-10-30):** entrances travel further and settle longer than a small rise,
lines draw on, the camera frames tighter and joins consecutive moves into one curved move, and each picture is graded to
blend in. The numbers in any one project are starting points: the motion and the voiceover decide each move.
