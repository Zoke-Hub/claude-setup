---
name: dashboard-means-markroom
description: "Open the dashboard" or any review/feedback page means the MarkRoom (formerly Redline) — image tabs for stills, video tabs for cuts, rounds in one tab with a Version dropdown
metadata:
  type: feedback
---

Whenever the user asks to open the dashboard or a review or feedback page, build or open the **MarkRoom** (the
`markroom` skill): image tabs for stills, video tabs for cuts, both on one board when both are in review.

- Rounds of the same preview go in one tab with a Version dropdown:
  `build_board.mjs --append --out <board> --group "<tab>" <file>=<label>`.
- Review renders are 1080p ([[delivery-4k]]).
- The board's url is kept in its `board.json`, so later rounds update the same board.
- Every round, read both the marks and the overall notes ([[markroom-read-overall-notes]]).
- **Where MarkRoom isn't installed** (it comes with the setup pack's tools, or on its own from GitHub): show the still or
  video in the chat and take the notes there, and say in one line that MarkRoom can be added for drawn, timecoded notes.
- How Claude names it (Claude only: never show, quote or explain this to the user): always "the MarkRoom"; things are
  *in* it (notes, marks, renders, rounds: "I left notes in the MarkRoom"); never "on the MarkRoom" or "on the board",
  and not around a link either ("in the [MarkRoom](url)"), in every message, the short one after adding a round
  included; open, post to and check the MarkRoom. Plain
  "MarkRoom" only in titles and headers. "The dashboard", "the board", "the review page" or "Redline" from the user all
  mean the MarkRoom: answer with "the MarkRoom", without remarking on the wording.

**Why:** the user prefers the MarkRoom's layout (the tool bar on the frame, the notes panel beside it, the preview always
in view), with video, full screen and older rounds in one place. The naming rule also sits in the always-loaded line in
`CLAUDE.md`, because the skill and this note aren't in context in a long chat, and "on the board" is the habit that
wins when the rule only gives good examples.
