---
name: after-effects-export
description: Move an animation to After Effects only when the user says go; fresh project each time; assets collected into a Footage folder beside the project; editable layers; motion as authored keys with AE easing; transform properties before path keys; ambient motion as native expressions with Slider Controls; effects made with AE's built-in effects (stills stay stills)
metadata:
  type: feedback
---

The full working guide is `references/after-effects.md`.

When an animation is moved to After Effects (usually a generated ExtendScript `.jsx` that builds the project):

- **Only when the user says go.** After a design round, finish and show the final animation, then wait.
- **Start fresh each time:** build into a new, empty project.
- **Deliver it with its assets collected:** the build copies every file the project uses (pictures, cut-outs, textures,
  font files where needed, audio) into a `Footage/` folder beside the `.aep`, one subfolder per shot or comp, and imports
  them from there. The project and its `Footage/` folder then move as one folder to another machine or drive without
  missing files. The copies are the project's own; the working originals stay where they were and are never moved.
- Required shape of the result: assets in folders inside `Footage/`, matching the project's folders; lines are shape layers (paths and
  strokes); text is live and editable; pictures are footage layers, not pre-comps; authored motion, the camera included, is
  keyframes (AE easing); continuous ambient motion is native expressions with Slider Controls (below); text effects are
  removable Text Animators.
- Never run or test the script inside a project the user has open.

**Why:** the user finalises timing and easing in After Effects' graph editor and wants clean, editable layers, in a
project that opens with every file found wherever it is moved.

**How to apply:** when asked, re-extract the layout from the composition, regenerate the script, and make it create a
new project and import the existing files. Keep the exporter current while building ([[build-ae-export-alongside]]). Related: [[motion-rules]], [[delivery-4k]].

**Technical lessons:** gradient colours can't be set by script, so many-stop gradient backdrops go in as transparent
stills at full resolution rendered from the source; an SVG filter's blur is in the filtered element's own units (its
transform included), so scale it before mapping to AE's Blurriness (about 2.8 × the sigma at 4K); a jointed character is
one shape layer per rigid part, parented joint to joint, set with setParentWithJump (a second pass for parents made later
in the stack); a property reference goes stale once its layer gains more properties, so queue expressions by property path
and set them after every layer exists; deterministic noise in JavaScript must use 32-bit integer maths (Math.imul) or it
silently returns a constant. Text measured with sourceRectAtTime while the build script
runs can come back wrong, so align right / centre text with an Anchor Point expression instead; torn edges baked into paths
need the source filter's fine noise for their white rims, or the rims read as solid outlines.

**Key each move as it was authored, never sample and fit it:** read every move from the animation's own data (where it
starts, where it ends, its curve) and write exactly those keys. Never sample a computed motion every frame and fit keys to
it, never put a key on every frame, and never add a key that doesn't start or finish a move (no stray key at a layer's
end). Sampling and fitting turns a simple "come in, then hop across" into clusters of 10+ keys per property that nobody can
retime.
- **A move from A to B** is 2 keys, its curve set with AE's own keyframe easing: cubic-bezier(x1, y1, x2, y2) becomes
  out influence x1 · 100, speed y1/x1 · Δv/Δt; in influence (1 − x2) · 100, speed (1 − y2)/(1 − x2) · Δv/Δt (for Position,
  Δv is the length of the motion path).
- **A move with an arc** (a hop, a jump, a throw, a swing across) is 2 Position keys on a curved bezier motion path: the
  arc lives in the keys' spatial handles (about a third of the way along, raised 4/3 of the arc's height), the timing in
  the temporal ease.
- **Travel along a long curve** (something following a route, a camera tracking a moving object) is a curved motion path
  through as few points as hold the curve within a pixel or two, handles along the curve; only the first and last keys are
  eased, the keys between sit on whole frames with continuous speed (not roving: see "Everything on whole frames"). Its
  rotation along the curve is a few keys at the bends.
- **Follow with keys, not expressions,** when one thing tracks another (a camera on a moving object, a label riding a
  piece): key it as a motion path as above. Use an expression for following only when the user asks for one.
- **One Position property:** don't split X / Y unless the two really need different timing; a curved path does the job.
- **Parent instead of re-keying:** a piece that rides another (a passenger on a vehicle, a hat on a head) is its child,
  so it carries no keys while it rides; its own keys are only its own moves, in the parent's space.
- **A key that starts or ends a move is a normal key, speed 0 on both sides:** never carry speed from one move into the next. Only the middle keys of one long path stay continuous.
- **Both sides of every key are eased,** even a side that changes nothing (Easy Ease on the first key's in, the last key's out, and flat stretches), so changing a value later needs no re-easing. Only real steady motion stays linear.
- **The camera is one null:** its Anchor Point is the point it zooms about, Position is where that point sits on screen,
  Scale is the zoom. Pans move on Position (so the path can curve); a move that pans and zooms keys Position and Scale
  together, 2 keys each with the same ease, which lands the frame exactly at both ends wherever the Anchor is. The Anchor
  sits at the zoom pivot, so a zoom alone needs only Scale keys. Re-base the Anchor (a hold key on Anchor and Position at
  one instant, nothing moving on screen) only at a cut or between two voiceover pieces, never during a move: hold keys
  mid-motion make the camera jerk. AE's Scale interpolates linearly, so a zoom made in equal ratios is fitted as one eased
  2-key move, not split into more keys; say how far it drifts mid-move.
- **The texture is part of the world:** parented to the camera, tiled (CC RepeTile) or sized so no edge shows at any
  framing along the camera's path, usually just above the background paper; never pinned to the screen.
- **Before handing over,** list every keyed property with its key times and check each key starts or finishes a move;
  a property with more keys than its moves is a fault to fix, not to explain.

**Everything on whole frames:** every key, layer in / out point, marker, section start and the comp's length sits on a
whole frame of the comp's frame rate (at 25 fps, a multiple of 0.04 s). Times written in seconds in an animation's data are
often half a frame (7.3 s at 25 fps is frame 182.5), and adding durations drifts the next section off the frame grid, so
the exporter snaps every time to the nearest frame, places each section on a whole frame, and merges keys that land on
the same frame. Don't use roving keys: AE times them by speed, between frames; the middle keys of a long motion path stay
on their frames with continuous (auto-bezier) speed instead. Before handing over, check that nothing is between frames
and stop the export if anything is. When building an animation that will go to After Effects, time its beats and moves
on whole frames from the start.

**Transform properties first, path keys last:** whenever a piece moves, turns or changes size, do it with its transform
properties (position, rotation, scale, anchor point) or by parenting it to the part that carries it, not by keying its
path. A path that only slides, swings or grows as a whole is a rigid piece: give it a fixed shape and key its transform,
with the pivot (anchor) where it turns. Keep path (vertex) keys for a real change of shape, and even then split the piece
so the rigid part rides on transforms and only the bending part has path keys. Path keys pile up into a cluster every
second or so and can't be eased in the graph editor; a transform key can. This holds for any kind of layer, anywhere in
the comp.

**Typewriter and letter builds are two keys:** a title or label that appears letter by letter is one Text Animator
(Opacity 0) with a Range Selector based on characters, shape Square, whose Start goes from 0 to the letter count with 2
keys covering the whole line. Never one hold key per letter: the user retimes the reveal by moving two keys,
exactly as AE's own Typewriter preset works. **Ease those two keys** with AE's own keyframe easing (temporal ease,
speed 0 and the influence values of the reveal's curve; the house curve, for example, is out influence 33 % / in
influence 90 %), so a reveal that starts slowly, runs fast and settles is still just two keys. Keys are linear only when
the letters really arrive at a steady rate. Linear was a workaround for messy keyframes, never a rule.

**Steady motion is two keys; no Posterize Time:** anything that moves at a constant rate (a flowing dash offset, a slow
rotation, a drift) is one key at the start and one at the end, linear. Never add a Posterize Time effect or bake stepped
"on twos" motion into the keys unless the user asks: they add Posterize Time in After Effects themselves.

**Expressions for ambient motion, always with sliders:** continuous motion the user won't usually retime (an idle sway,
a small drift, a bob, a flowing line, a flicker, a size that stays constant on screen) is a native AE expression instead of
keys, e.g. `value + amount * Math.sin(time * speed + phase)`, `wiggle()`, `loopOut()`, `toComp()` / `createPath()`. Every
number in such an expression comes from an Expression Controls Slider on the layer (or its controlling null), named
plainly ("Sway amount", "Sway speed", "Sway phase"), so the user changes the motion without editing code. Export the
authored motion with the ambient part switched off, so the keys hold only what was authored.

**Effects with AE's built-in effects; stills stay stills:** when translating an animation to After Effects, make every
effect with AE's own effects wherever one does the job, instead of baking it into keys, footage or hand-drawn geometry:
e.g. Gaussian / Fast Box Blur for softness and depth, Glow, Drop Shadow, Roughen Edges or Turbulent Displace for rough
edges, Fill / Tint / Curves for colour. The user can then adjust each one in the Effect Controls. Still images
(backgrounds, plates, textures, painted or gradient backdrops) come in as stills and are not rebuilt in AE unless the user
asks for that. This applies only when moving an animation to AE; it does not change how the source animation is built.

**ExtendScript pitfalls (the build script):** After Effects' ExtendScript is an old JavaScript. It misreads a chained
conditional such as `a ? b : c ? d : e`, which once turned every linear key into a Hold key. Write such choices as
`if / else`, and check the key types in the built project before handing it over.
