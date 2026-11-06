---
name: markroom-read-overall-notes
description: Every MarkRoom review round, read BOTH the marks and the overall notes ("Notes on the whole image / video") on every board, reply to both and mark both done
metadata:
  type: feedback
---

When the user says their notes are done, or asks to "go over the changes", list **both** collections on every MarkRoom
board in the project: `marks` (notes pinned to marks) **and** `overall` (the "Notes on the whole image / video" box).
Reply to both and mark both done.

**Why:** the overall box saves as the user types and has no Post button, so they assume it has been read. Reading only
the marks misses whole-video notes, often the most important ones.

**How to apply:** follow the `markroom` skill's "Read the feedback" step, which makes this mandatory; `render_marks.py`
takes `--overall` to render those notes too. Related: [[dashboard-means-markroom]].
