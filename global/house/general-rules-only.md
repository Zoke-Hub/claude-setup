---
name: general-rules-only
description: When the user asks for a new rule, write it general (no project names, subjects, files, numbers or anecdotes); project-only notes go in that project's memory
metadata:
  type: feedback
---

When the user asks to add a rule, it is meant for every project, so write it with nothing from the project it came up in.

**Why:** the rules are shared across projects and packed into the setup pack for other machines. A rule full of one
project's names and story misleads work elsewhere and leaks that project's details into the pack.

**How to apply:**
- Strip the current project's names, subjects, characters, places, file and comp names, layer names, counts, dates and
  anecdotes ("this once produced N keys in the map comp"). State the rule and why it matters in general terms.
- Use generic examples ("an idle sway, a drift, a flicker", "a jointed character", "a long timeline") instead of the
  project's own.
- Put a one-line rule in `~/.claude/CLAUDE.md`, the full note in `~/.claude/house/` (plus a line in its `README.md`), or
  a style-only note in `~/.claude/house-private/` when it is the user's personal look rather than a working rule.
- What is true only for one project (its numbering, file locations, decisions on its shots) goes in that project's memory,
  never in the general rules.
- After writing, search the rule files for the project's names to make sure nothing slipped in.
