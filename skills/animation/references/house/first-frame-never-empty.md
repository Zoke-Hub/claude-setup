---
name: first-frame-never-empty
description: An animation's first frame is never empty paper; it opens on a frame that is already partly built, and the rest is retimed around it
metadata:
  type: feedback
---

**The first frame of any animation is never empty.** Frame 0 already shows the shot taking shape: the title, the frame
of a chart (axes, labels), the main objects or the collage, a first part of the data. The build carries on from there.

- **Pick the opening state from the build itself.** Take a moment early in the build where the layout reads (for
  example, the title typed and the axis drawn, with the line just starting) and show that at frame 0.
- **Retime the rest so the beats still land.** Stretch the opening so the build reaches its first voiceover-synced beat
  at the same frame as before (time remapped over the opening only). Every later beat keeps its frame.
- **A camera move can open the shot**, such as a short push-in over the first second on a front-loaded curve, when the
  user asks for one; it is per shot (some shots open with no camera move).
- **In After Effects:** the layers already on at frame 0 start fully revealed (their reveal keys sit before or at 0, or
  have none); only what is still building keeps its keys.

**Why:** an empty paper frame at the head of a shot reads as a gap in the edit, especially after a cut from the presenter.

**How to apply:** check frame 0 of every render before handing it over; if it is blank or nearly blank, move the opening
state forward. Related: [[motion-rules]], [[after-effects-export]].
