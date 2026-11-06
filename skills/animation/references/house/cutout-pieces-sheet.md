---
name: cutout-pieces-sheet
description: For rigged or character animation, ask whether the user wants a cut-out pieces sheet; if yes, shape every piece on purpose, show each once loosely arranged in place, and get the cut-outs approved before animating
metadata:
  type: feedback
---

For rigged or character animation (a character cut into moving pieces), ask the user first whether they want a
**cut-out pieces sheet** before anything is animated. Not every animation needs one: a figure that always stays small in
frame may not be worth it. If they say yes:

- Show **every piece** at full drawing resolution, loosely pulled apart from where it sits, so each piece's own edges are
  visible: its name beside it and a dot where it turns.
- Each piece appears **once**; don't repeat pieces in extra panels (the user marks them where they are). The board's
  zoom gives the detail.
- **Shape every piece on purpose before showing the sheet**: a cut-out or a fill gives pixels, not body parts. Each piece
  is made into what it is (a limb one solid tapering shape with rounded ends; cloth only cloth; no slivers, specks,
  notches or leftovers of a neighbouring part) and checked at full size first.
- **No outlines on the pieces**: a line that runs along a piece's edge is recoloured to the piece's own fill; the animation
  adds one consistent outline later. Flat colour (no smudges), continuous smooth edges, no stray bits, rounded necks.
- **Props whole**: what a hand or the body covered (a book, a veil) is completed. Small gaps and repairs are done by hand
  with shapes and colour strokes; a generative fill only for a large hidden area, since it gives poor results in small
  spots. A patch must not look pasted on.
- **Change only what is marked, and carry a fix to where it obviously applies**: fix what a note marks or refers to, and
  make the same fix on the matching parts too (a change described at one joint goes to the other joints that have the same
  problem); leave everything else exactly as it was (no global pass that recolours or reshapes unmarked parts). If a
  marked fix leaves a gap at rest or seems to need another piece changed, don't change that piece: say so in the reply
  and let the reviewer decide. Check that every edit tool only touches what was marked (no whole-piece smoothing that
  closes finger gaps or slits elsewhere); compare each changed piece with its backup outside the marked area.
- **Layering as drawn**: what is behind cloth in the drawing stays behind it (legs behind a skirt), and cloth made whole
  keeps its fold strokes like the rest of that cloth.
- **Check every piece yourself at full size first**; never send broken pieces for review.
- Variants of a piece (a second arm pose, a prop one character has and another doesn't) sit in their own group, labelled.
- Post it to the review board as its own tab, wait for the marks, fix the pieces, post the sheet again as a new round,
  and animate only once the pieces are approved.

**Why:** a cut-out problem is much easier to see and to mark on the still piece than in a moving render, and fixing it
before animating avoids rounds of renders that each fix one thing and break another.

**How to apply:**
- When the user asks to see the pieces (or any work) **as it is** so they can mark it, show exactly the current state
  first, with no changes. If changes are already under way, put the work back to the state they saw, show that, and keep
  the draft aside until they have marked.
- Make the sheet from the rig files themselves, not from a re-cut, so it shows exactly what will move.
- The user's marks on the sheet are loose guides: find where and what they mean, then cut by the body's structure; never
  trace a stroke as an edge. Read the words for intent ("fill" adds, it never removes).
- Keep the sheet numbered and logged like any other preview, and keep earlier sheets.
- Related: [[keep-every-render]], [[dashboard-means-markroom]], [[ask-before-building]].
