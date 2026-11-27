---
name: note-the-edit-cuts
description: When cutting voiceover pieces out of an edit, note the edit's picture cuts around each piece too, and land every animation and footage (FF) edit exactly on them; never a few frames of the neighbouring shot before or after
metadata:
  type: feedback
---

When voiceover pieces are cut out of an edit (an editor timeline, a locked A-roll, a rough cut) to build animations or
footage inserts against, the picture cuts around each piece are noted down too, and every insert starts and ends exactly
on them.

- **Note the cuts with the voiceover.** For each piece, write down the edit's cuts on whole frames: where the shot before
  ends, where the insert's slot starts and ends, where the shot after begins, and any cut inside the slot. Keep them with
  the piece's word times (e.g. `Segments/<Animation>/` beside the piece, or a `cuts` list in its timing file), taken
  from the edit itself (an XML / EDL export, the timeline's markers, or a scene-change pass over its render), not
  guessed from the audio.
- **Land every insert on its cuts.** An animation's first and last frame, and a footage (FF) clip's in and out, sit on
  the noted cut frames, so no frames of the previous or next shot show before the insert starts or after it ends, and
  the insert neither falls short of a cut nor runs past it. Where the voiceover's timing and a cut disagree, the cut
  decides the insert's edges and the beats inside it are retimed; say so if the gap is more than a few frames.
- **Check the edges before handing over.** Look at the frames either side of each insert's start and end, in the
  context of the edit (the slot's neighbours placed around it), as `check-every-cut.md` checks a cut: no stray frames
  of another shot, no gap, no doubled frame.

**Why:** animations and footage edits built only to the voiceover kept leaving a few frames of the neighbouring shot
showing just before an animation started or just after it ended, because the picture cuts weren't recorded with the
voiceover pieces.
**How to apply:** every time voiceover pieces are cut from an edit for animations or footage inserts, record the edit's
cuts with them, build each insert to those frames, and check both edges before a round is shown. Related:
`check-every-cut.md`, `time-to-the-voiceover.md`.
