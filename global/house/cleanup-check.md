---
name: cleanup-check
description: After a feature lands or a piece of work is finished, a UI redesign above all, ask the user whether to check it for dead code, duplicate logic, unused components, unnecessary complexity and implicit state machines; find first, change only what they pick
metadata:
  type: feedback
---

After adding a feature to a tool, app, mod, skill or page, or when the user says they're done making something, ask
them whether to run a clean-up check. Ask every time. It matters most after a UI redesign, which tends to leave old
layouts, styles, handlers and fallbacks behind.

**Why:** work built in rounds leaves things behind: functions nothing calls any more, a second copy of logic that
already existed, components no screen shows, and workarounds a later change made unnecessary. Each one makes the next
change slower and riskier, and nobody notices until it gets in the way.

**How to apply:**
- Ask at the end of the turn that finishes the feature or the redesign, as that turn's closing question with a button
  that's a whole answer ("Check for dead code"), not tucked into prose. Don't run the check unasked.
- The check covers five kinds:
  - **dead code:** never called, never reached, or behind a switch that's always off;
  - **duplicate logic:** the same work done in two places;
  - **unused components:** pieces, styles, assets, files or options nothing uses;
  - **unnecessary complexity:** indirection, options or special cases nothing needs any more;
  - **implicit state machines:** a mode or lifecycle (loading, saving, dragging, a request waiting, a job running) held
    in several flags, timers or maybe-empty values that different handlers set and clear, instead of one state with
    named steps. Each can drift into a combination that should be impossible: a flag left set after an error, a reset
    that one path skips, two async events that overwrite each other, a "busy" that never ends. For each, list its
    states and what moves it between them, then the concrete way it can go wrong, how likely, and what an explicit
    version would be (its state names). Rank them by how much they'd hurt; fix only the ones picked.
- A project can keep its own mechanical pass (a script that lists unused names, exports nothing else uses and code
  written twice) with a short guide beside its notes: run it first, then read the code for the rest.
- Find first. List each finding with its file and line, the evidence (nothing calls it, where its twin is), how sure,
  and the fix, grouped by kind, safest first.
- Confirm each one at the source before listing it. Something can look unused yet be called by name from a hook, a
  test, a page, a config, the engine or another tool.
- Change only what the user picks. Back up first, and run the tests and check the thing still works after.
