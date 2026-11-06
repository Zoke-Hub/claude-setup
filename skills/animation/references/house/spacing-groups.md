---
name: spacing-groups
description: Spacing shows structure: gaps inside a group are smaller than gaps between groups, from one fixed scale, in interfaces and in animation frames alike
metadata:
  type: feedback
---

Spacing shows what belongs together. Elements in the same group sit closer to each other than the group sits to its
neighbouring groups, and every gap comes from one small fixed scale.

- Decide the groups first: what reads as one unit (a label with its value, a title with its subtitle, a chart with its
  caption, a row of controls with the line that explains them).
- The gap between groups is always clearly larger than any gap inside them. Two steps of the scale apart is a good
  starting point.
- Use the same values for the same kind of gap across the whole piece, so the rhythm is consistent from one area, screen
  or frame to the next. No one-off gaps tuned by eye.
- Applies to interfaces and to animation layouts: titles, labels, charts, captions and collage groups on a frame follow
  the same rule, and so does an element that lands next to another in a build.

**Why:** the user pointed out that a control row sat as close to the bar above it as to its own caption, so the groups
could not be read at a glance, and asked for this to hold in every design and in animations.
