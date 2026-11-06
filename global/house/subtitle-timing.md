---
name: subtitle-timing
description: Sentence subtitles stay on screen at least 1 second: hold into a pause first, otherwise club with a neighbour and re-break into whole phrases, in sync, with the same words; not for word-by-word animated captions
metadata:
  type: feedback
---

Subtitles must stay on screen long enough to read. This applies to sentence subtitles (SRT files, editor caption
tracks, burnt-in subtitles), not to word-by-word animated captions.

1. **Minimum time:** no subtitle stays on screen for under 1 second (25 frames at 25 fps). Short text is fine as long as
   it stays that long, even a single word.
2. **Hold first when there is room:** let a short line stay on into a pause. A line that lands as its own beat (a
   one-word answer, a punchline) keeps its own line if it can hold.
3. **If it can't hold, club it:** join it with the previous line whenever the sense allows. Use the next line when the
   previous one ends a sentence or the fragment belongs with what follows.
4. **Re-break, don't just glue:** when clubbing makes a line too long, redistribute the words across the two or three
   neighbouring lines so each one reads as a whole phrase.
5. **The character limit is soft:** a line may run slightly past it (about 5 or 6 characters) to keep a phrase whole or
   stop a line flashing by. Reading time beats line length.
6. **Break at phrase ends:** after punctuation, or before a conjunction or preposition. Don't end a line on an article,
   preposition or helping verb. Don't split a name, or a number from its unit.
7. **Stay in sync:** keep the usual 0 to 2 frame gap within speech. A line may borrow a few frames from a neighbour if
   the neighbour still runs at least 1 second. Keep each line's start within about 8 frames of its first spoken word,
   and don't club across a pause longer than half a second.
8. **Words are untouched:** a timing fix keeps the same words in the same order, keeps the style unchanged, and never
   puts a subtitle over burnt-in text.
9. **Change only what needs it:** leave lines that are already fine, and keep any fixes the user made by hand unless one
   breaks the minimum time.
10. **Before handing over:** confirm nothing is under the minimum, there are no overlaps, the full text still matches
    word for word, and every changed line has been read.

**Why:** a line that flashes by can't be read, however short it is, so reading time comes before a tidy line length.

**How to apply:** for each line under the minimum, try 2, then 3, then 4, in that order, keeping 5 to 9 throughout.
Finish with the checks in 10. Related: [[time-to-the-voiceover]].
