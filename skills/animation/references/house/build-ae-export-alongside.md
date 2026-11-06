---
name: build-ae-export-alongside
description: When animations will go to After Effects, write or extend the AE exporter while building each animation, not afterwards, so the AE file is a quick re-run when the user asks
metadata:
  type: feedback
---

When a project's animations will end up in After Effects, keep the After Effects exporter up to date **while** building
each animation, not after it is approved.

- When a new element type appears (routes, a legend, regions, a torn edge, …), add its After Effects mapping to the
  animation's exporter the same day.
- After each approved round, make sure the exporter still covers everything on screen, so "give me the AE file" is a
  minutes-long re-run, not hours of catch-up.
- Before committing to a look that is hard to rebuild in After Effects (browser filters, per-frame effects), say what
  it will cost in After Effects.
- Handing over the After Effects file still waits for the user's go, and the script never runs inside a project they
  have open ([[after-effects-export]]).

**Why:** an animation with an exporter kept current re-exports in minutes; one without turns the first After Effects
hand-off into a multi-hour job.
