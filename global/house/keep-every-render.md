---
name: keep-every-render
description: Never overwrite or delete renders or previews; number every output rNN_… and log it in renders/RENDERS.md; handoff notes get dated names and old ones are archived as superseded
metadata:
  type: feedback
---

Save every render as its own file, drafts and previews included, and never delete or overwrite older ones.

- Number outputs `rNN_<what>` (r01, r02, …) and add one line per render to `renders/RENDERS.md` (number, date, what
  changed, settings).
- Preview stills are numbered too.
- Never run `rm` on render outputs. For one-off ffmpeg exports or frame grabs the user will see, use new filenames
  rather than `-y` over an existing deliverable.
- Scratch frames in a scratch folder are fine to overwrite.
- **Handoff notes are versions too.** Give each handoff (the note that lets a new chat carry on the work) a dated name,
  such as `HANDOFF_<project>_<date>.md`. When a newer one replaces it, move the old one to an archive folder with a
  SUPERSEDED line at the top that names the new file; never overwrite it. Point the project's memory at the current one.

**Why:** the user compares rounds and goes back to earlier versions; an overwritten render can't be compared.

**How to apply:** give each project a small render script that picks the next number and appends the log line.
Related: [[delivery-4k]].
