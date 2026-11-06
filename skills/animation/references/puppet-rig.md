
# Cut-out puppet rigs and walks

A character drawn as one flat image becomes a puppet: pieces (head, body, cloth, upper arm, forearm, thigh, shin, foot)
that turn about pivots. The reviewer sees every seam in a flat silhouette style, so the whole job is that the figure
always reads as **one drawing**: no gaps, no knobs, no steps in an outline, no change of tone between pieces.

**The first rule: at its own pose the puppet is exactly the drawing.** Every joint ball, filler and redraw lives inside
the drawn outline or hidden behind another piece; nothing bulges past the outline and nothing of the drawing goes
missing. Most "uneven" or "disconnected" limbs come from breaking this: a filler wider than the limb, a ball measured
across a slanted cut or on the pale paper rim, a cut that shaved part of the limb away. Check it every time
(`rest_compare`), and trim what shows (`rest_match.py`).

**The second rule: never make a round worse.** Before posting, put the new render beside the previous one at every
noted frame and at the reviewer's earlier notes; a part nobody flagged must not change for the worse.

Scripts (Python 3.10+ with numpy, OpenCV and Pillow; the cut-out venv has them):
- `scripts/joints.py` - fit ball joints to the drawing (`fit_joint`, `fit_bend`, `split_bend`, `side_of`) and continue a
  limb under cloth (`extend_limb`).
- `scripts/one_dark.py` - one dark for every skin piece, hairline fill seams filled.
- `scripts/pieces_sheet.py` - the cut-out pieces sheet for review before animating (reads the rig, changes nothing).
- `scripts/rest_match.py` - trims any limb filler that would show at rest past the drawn outline or over cloth (thin
  pale lines inside the figure are left alone: trimming along them cuts a notch that shows once the limb moves).
- `scripts/puppet.py` - draw a rig in any pose (`Puppet`, with the hem matte and the paper edge), a planted-feet walk with
  two-bone IK (`Gait`), cloth nudged by the limb under it (`push_cloth`), the frame checks (`qa`) and the rest-pose
  comparison with the drawing (`rest_compare`).

## 1. Before cutting

- Ask the questions that change the cut, and say how each cut is decided: which parts move, which arm is in front of the
  body and which behind, where each hidden end goes (under a sleeve, a drape, a skirt), which hand keeps its pose.
- Pieces that move are cut from the picked image itself. What a moving part uncovers comes from **generative fills**:
  edits of the same image with only that part removed (one with the arms removed, one with the lower legs removed).
  The difference between the image and a fill is the whole moving part; the fill is the drawn body behind it.
  Check every fill for leftover lumps of the removed limb (they float when the limb moves) and for a body that kept part
  of the limb (redraw that edge).
- Cut out with the `cutout` skill. Strip the baked pale paper edge from every piece; the edge is drawn live round the
  whole moving silhouette (outside only), so it never shows as a line between two pieces.
- Mid-work inspection images (piece maps, tinted pieces, crops) are not results: say so when showing them.
- **Ask whether the user wants a cut-out pieces sheet** (a figure that always stays small in frame may not need one). If
  yes, make it from the rig files with `scripts/pieces_sheet.py <rig> <out.jpg>`: every piece once, pulled apart in
  place with its name and a dot where it turns (no extra panels repeating pieces already on the sheet). Post it as its own tab on the review board, let the user mark the cut-outs, fix,
  post the sheet again, and animate only once the pieces are approved. A rig can carry plain names for its pieces in
  rig.json (`"labels": {"piece": "front arm · upper"}`).
- When the user asks to see the pieces (or any work) as it is, show exactly the current state first, unchanged; keep any
  fix in progress aside until they have marked.

## 1b. Shape every piece on purpose

A cut-out tool and a generative fill give pixels, not body parts. Cut each piece out knowing what it is, then rebuild or
remove parts until it is that shape:
- **A limb** is one solid shape: an upper arm widest at the shoulder and tapering to the elbow, a shin one convex taper
  into the ankle, rounded ends where it turns. No nicks, spikes, notches, slivers or specks; nothing left over from a
  neighbouring part (a strip of torso on a cloth piece, a wedge of arm on the body).
- **A part that belongs to one piece goes with that piece**: what the fill left of a limb on the body is removed from the
  body; a piece of cloth holds the cloth and its own outline, not a long line running off it.
- **Background is background**: pale specks or flicks the cut-out left inside an outline are cut away.
- **The ends that hide under another piece** (a neck under the head, a shin top under a hem) are rounded and kept short
  enough not to stand out when the piece turns, but long enough never to come apart.
- **Limbs are built from their structure**, not traced: an upper arm is the hull of a shoulder circle (about 1.2-1.3x
  the elbow's radius) and the elbow ball, so it is widest at the shoulder and tapers straight to the elbow; a shin is
  one convex taper into the ankle ball. Then keep the drawn outer edge where the drawing has one.
- **Reviewer marks are loose guides.** A drawing tool is not precise: map the strokes back to drawing pixels to know
  where and what, then cut by the structure (where an outline naturally ends, what a limb or a cloth is). Never trace a
  stroke as the edge. Read each note's words for intent: "fill this" means add to the piece, not cut it away.
- What is hidden behind a moving limb is designed on purpose, from the drawing's logic (cloth continuing up from where
  it shows, the torso as body), and checked in motion.
- Tools that do this cleanly: keep the largest part and fill holes; an opening removes slivers and spikes; a closing fills
  notches; a convex hull makes a limb one taper; a smoothing pass removes jagged edges; a refitted ellipse makes a ring
  whole. Where a prop crosses a line of the drawing (a fold over keys), let the drawing decide what is prop and what is
  line.
- **No outlines on the pieces.** Lines that run along a piece's own edge (the line between a limb and the body, a cloth's
  paper border) are recoloured to the piece's own fill; the animation draws one consistent outline round every piece
  later. Lines inside a piece (folds, fingers, a thread) stay. Pieces are flat colour: no smudges or blotches from a
  generative fill (a two-colour scheme stays exactly two colours), so nothing looks random.
- **Edges continuous and smooth**: no steps, ticks, sharp corners or stray bits along any edge; necks of head pieces are
  carried on down and rounded, and the body's neck stub under the head is removed and rounded (the head covers the join).
- **Props whole**: a book, a veil or anything a hand or the body covers in the drawing is completed where it was hidden,
  so it looks right when it moves or comes away. Small gaps and repairs by hand with shapes and colour strokes; a
  generative fill of the drawing (covering part removed) only for a large hidden area, since it gives poor results in
  small spots. A repair never looks pasted on.
- **Change only what a note marks or refers to**, and make the same fix wherever it obviously applies too (a change
  described at one joint goes to the matching joints). No global pass may recolour or reshape parts nobody marked. If a
  fix leaves a gap at rest or seems to need another piece changed, leave that piece and say so in the reply. After each
  edit, compare the piece with its backup outside the marked area to catch collateral changes.
- **Layering as drawn**: what is behind cloth in the drawing stays behind it (legs behind a skirt), and cloth made whole
  keeps fold strokes like the rest of that cloth.
- **Cloth over a joint**: when cloth covers a shoulder in the drawing, that cloth becomes its own piece in front of the
  arm, so the upper arm can be a full limb (widest at the shoulder) behind it and the drawing still matches at rest.
- Look at every piece at full size before showing it; a pieces sheet is checked by you first. Never send a sheet with
  broken pieces (fragments, wedges, a piece you cannot name): fix them or leave them out and say so.

## 2. Ball joints (why limbs come apart, and the rule that stops it)

A joint is a circle centred exactly on the pivot, **carried by both pieces** that meet there. Fit it to the drawing,
never by eye:

- **Measure on the ink.** Fit joints on the limb's dark drawing only. A moving-part mask taken from the difference with a
  fill also holds the pale paper rim round the limb, and every ball measured on it comes out too big (a bump).
- **Straight-ish joints** (`fit_joint`): the cut between the two pieces runs straight through the pivot, square to the
  limb (at a slight bend, square to the bisector); the pivot sits at the middle of the limb's cross-section along that
  cut; the ball's radius is half that cross-section, **but never more than the distance from the pivot to the nearest
  drawn edge** (a cut not quite square to the limb is longer than the limb is wide, and half of it bulges out).
- **Bent joints** (an elbow drawn near 90 degrees; `fit_bend` + `split_bend`): a bisector cut runs from the inner
  crease to the outer corner, so half of it is far wider than the limb and the ball sticks out as a knob. Instead measure
  the child segment's centre line and half-width clear of the crease, slide the ball back along that line until it just
  fits in the drawn joint, and give the upper segment only its own side of a cut square to itself through the pivot.
  **A bent elbow keeps its point**: the point is the end of the forearm bone, so it belongs to the forearm and turns
  with it. Never replace it with a round ball (that reads as a blob, not an elbow). Hidden flaps of the upper arm sit
  under the forearm, in the inner crease and in a thin strip past the cut on the outer side, so turning never opens a
  crack; keep each flap inside the bands of both segments, or it peeks out as a sliver.
- **Ankles and wrists** sit where the limb stops narrowing and flares into the heel or hand. Placed higher, the shin
  bends above the foot, which no real leg does.
- A ball wider than the limb shows as a knob; a limb trimmed to its ball looks pinched and robotic. Neither.
- A limb behind the body is drawn whole between its balls, never clipped to the body's outline (the clipped edge opens
  a gap the paper edge then fills).
- **Hidden parts continue the limb at its own drawn width**: under a drape or behind the body, the filler is the drawn
  limb continued (the hull of the drawn segment and its pivot, or a straight band at the joint's measured width), never
  a capsule with a guessed radius. A guessed one is either wider than the limb (a bump at rest) or narrower (a step when
  the limb swings out).
- **Where a limb meets cloth or the body, cut at the cloth's own edge, not further out**: the cloth's outline stays in
  its own piece, in front, so the limb can start right at it. Cutting further out shaves the limb's real width away.
- **A limb drawn merging into dark beside it** (an arm against the dark of the back) has no visible edge there: ask
  where the limb should end (the reviewer may draw it), end it there with one clean edge, solid up to it, and fill the
  body behind it solid dark from under the limb, tapering into the body's own outline below (a waist, a hip), so a swing
  shows body, never ragged pale bits, a shelf or a flat end.

## 3. Limbs under cloth

- A limb whose top is hidden (a thigh under a wrap or skirt) is **one tapered shape** from its joint ball up under the
  cloth, as wide as the drawing just below the hem (`extend_limb`). Never a drawn stub plus a filler of another width:
  that shows as a block or a notch when the limb swings out.
- Legs splay wider than a rigid cloth can cover. The limb shows **only below the cloth's hem line**, a matte that moves
  with the cloth (`hem` in rig.json; in After Effects a track matte parented to the cloth).
- The cloth's front is turned by the leading limb just enough to keep its corner ahead of every point of the limbs'
  real outlines in a short band below the hem (the pieces' own contours, moved with each frame), computed exactly every
  frame. A probe point or a straight-edge model of the limb is not enough: a drawn thigh is wider just under the hem
  than a line through it says. Verify on the rendered pixels over the whole cycle: no limb may come out past either
  side of the cloth.
- A cloth piece holds the cloth and its own outline only. Thin pale lines inside the figure are old outlines from the
  drawing, not cloth: test for wide pale areas (an opening), or a strip of body rides along with the cloth.

## 4. One dark, one paper edge

- Run `one_dark.py` last on every rig: every skin piece (body, head, limbs, drawn joint balls) gets the body's own dark,
  so pieces from different images never show a tone step. Cloth and props listed in `keep_drawing` keep their drawing.
- Pale lines that belong to the drawing (fingers, folds) stay; hairline pale seams where two fills were joined are filled.
- The paper edge is drawn round the union of all pieces every frame (`Puppet.edge`), outside only.

## 5. The walk

- Study joint motion from rigged character animation and real walking (how hips, knees and ankles move), not from a
  style reference's character motion.
- `Gait`: planted feet in four phases (heel strike, flat, toe-off, swing), feet that never slide on the ground,
  two-bone IK with the knee bending forward, the hip bobbing twice a cycle, a small lean and sway. Heel strike and
  toe-off angles stay gentle.
- **Feet stay flat** in the swing for walkers (no toe curl): a toe that curls up only works if it curls back down, which
  this style doesn't do. Give the rig flat feet (`feet` in rig.json); the back foot can reuse the front foot's piece.
- Arms swing opposite the legs, the forearm trailing a little behind the upper arm; a weighted hand (carrying
  something) swings less. Gestures are gentle, eased and in time with the words and the steps.
- Keep the pace the user approved; change stride and cadence only when asked.
- Smooth 25 fps. No stepped timing or Posterize Time in renders: it is added in After Effects if wanted.

## 6. Checks before every render

1. `rest_compare()` on every rig against its drawing: no bulges, nothing missing, except changes the reviewer asked for.
   Then `qa()` on every frame of every character: the silhouette is one connected shape, every joint circle is fully
   covered, hidden limb tops stay under their cloth.
2. Then look: render crops of every joint at the delivery canvas scale at several frames (both extremes of the stride,
   the passing pose, the frames reviewers noted), upscale them, and tint each piece to see which one a step belongs to.
   The automatic check finds gaps; only looking finds knobs, notches, steps, pokes past cloth and tone changes.
3. Put the new render beside the previous round at every noted frame, crop by crop, before posting: fixed where noted,
   and nothing else worse.
4. Review renders at 1080p; log every render (keep-every-render rule).

## 7. After Effects

Built only when the user says go, following the After Effects export rules:
- Each piece a footage layer with its anchor point on its pivot, parented as the rig (body to hip; upper arm to body;
  forearm to upper arm; thigh to body; shin to thigh; foot to shin; cloth to body).
- Motion keyed as authored with rotation and position (walk cycles can be expressions with Slider Controls for stride,
  bob and swing); no key on every frame.
- The paper edge: put the character in a precomp and give that layer a Stroke layer style, outside only (the one
  precomp the rule allows here).
- The hem matte: a shape layer parented to the cloth, used as the limb layers' track matte.
