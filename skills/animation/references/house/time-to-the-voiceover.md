---
name: time-to-the-voiceover
description: When an animation has a voiceover, transcribe it first and time every beat to it; a name lands on its spoken word, a title starts a little before its word
metadata:
  type: feedback
---

**When an animation goes under a voiceover, the voiceover sets its timing.** Transcribe it first (locally, word-timed:
`local-transcribe` or `npx hyperframes transcribe`), then build the beats to the words.

- **A name or label lands on its spoken word:** the thing being named appears as the word is said, not before the
  sentence and not after it.
- **A title starts a little before its word** (about 0.4 s), so it has finished unfolding as the word is heard.
- **Groups of things said in quick succession** (a list of places, routes, items) can come in as one overlapping burst
  over those words instead of one by one.
- **Keep the voiceover's pauses.** A pause in the read is a hold in the animation; if the voiceover is re-recorded or
  re-cut, retime the beats to the new words instead of stretching the old timing.

**Why:** the editor lines each animation up against the voiceover. Beats that land on their words need no retiming in
the edit; beats timed by eye have to be moved one by one.

**How to apply:** keep the word-timed transcript with the animation's files and write each beat's time from it, not as
loose numbers. Related: [[motion-rules]], [[first-frame-never-empty]].
