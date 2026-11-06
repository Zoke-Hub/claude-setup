
# After Effects Translation

*By Zoke.*

The aim is a project an editor can pick up and finish in After Effects' graph editor: clean, editable, and opening
with every file found, wherever it is moved. Everything here applies to every project. The house notes behind it:
`references/house/after-effects-export.md` and `build-ae-export-alongside.md`. If this computer keeps the editor's own AE
settings in a personal note (its CLAUDE.md Personal section says where), read that too: it adds their measured values,
presets, fonts and the path to their build framework, and wins over the starting values here.

## 1. When

- **Only on the editor's go.** After a design round, show the final animation and wait. Never run or test a build script
  in a project the editor has open unless they ask for it.
- **Keep the exporter current while building.** When an animation will go to AE, add each new element type's mapping to
  its exporter the same day, so "give me the AE file" is a minutes-long re-run. Before committing to a look that is hard
  to rebuild in AE (browser filters, per-frame effects), say what it will cost there.
- Say up front how long the export will take when it is a first export (new exporter), and run independent work alongside.

## 2. The delivered project

- **A fresh, empty project every build**, saved as `<Name> rNN.aep`; never overwrite an earlier build (log each in the
  package's `BUILDS.md`).
- **Assets collected:** every file the project uses (pictures, cut-outs, stills, fonts where needed, the A-roll for sound)
  is copied into `Footage/` beside the `.aep` (one subfolder per shot, `_Shared/` for files two shots use) and imported from
  there; the AE project's folders mirror `Footage/`. The working originals stay where they are.
- **4K (3840×2160), 25 fps.** When designs are 1080p, every position, size, stroke and font size is × 2.
- **Everything on whole frames:** every key, layer in / out point, marker, section start and the comp length is a multiple
  of 0.04 s. Snap times written in seconds; stop the export if anything lands between frames. No roving keys. Time beats
  on whole frames when building the animation in the first place.
- The segment's voiceover / A-roll goes in for sound only (video off), as the **very bottom layer** of the comp, under the
  paper and everything else, never at the top. Leave out the texture overlay and Posterize Time when the editor adds them
  (see the finishing pass in section 11).

## 3. Layers

- **Text is live** (editable), lines and shapes are **shape layers** (paths, strokes, fills), pictures are **footage
  layers**. No precomps.
- **Pictures come in at their largest source,** never a working-size PNG (finished comps swapped several small cut-outs
  for bigger files). A picture the page clips (a round portrait, a coin) keeps that clip as a mask on the footage layer (`L.clip()`, or `clip` on `L.image()`).
  Before export, look at each cut-out on the paper colour: a cast shadow or floor left under it is the first thing an editor
  has to mask out by hand.
- **Stills stay stills:** backgrounds, plates, textures and many-stop gradients (which scripts can't set) come in as
  full-resolution stills rendered from the source page (headless Chrome at 3840×2160), with a guard that the source CSS
  hasn't changed since the still was made.
- **The camera is one null:** Anchor Point = the point it zooms about (world units × 2), Position = where that point sits
  on screen, Scale = the zoom (z × 100). Every world layer is parented to it; fixed screen elements (headers, source lines,
  the paper) are not. **The camera moves on Position**, so a move can follow a curved motion path (two moves in a row
  become one curved move, editable in the comp viewer). A move that pans and zooms keys **Position and Scale together,
  2 keys each, with the same ease**: the frame then lands exactly at both ends wherever the Anchor is, and everything
  travels straight across the screen in between, so the Anchor never has to change mid-shot. The **Anchor Point sits at
  the section's zoom pivot** (the world point at the frame's centre), so a zoom on its own needs only Scale keys and stays
  centred. Re-base the Anchor (Anchor and Position keyed together at one instant, nothing moving on screen) only at a cut
  or in a gap between two voiceover pieces, **never during a move**: hold keys on the Anchor mid-motion make the camera
  jerk, and moves built from 3+ keys where 2 would do look odd. One layer may key Anchor and Position at different
  moments, never both for the same move: Anchor-only pans can't follow a curved path. Tell the editor: when re-easing a
  pan-and-zoom, ease Position and Scale the same way, or the frame drifts mid-move.
- **Parent instead of re-keying:** a piece that rides another is its child, so it has no keys while it rides. Parent last,
  with values authored in the parent's space (`setParentWithJump` keeps the numbers; plain `.parent =` keeps the screen
  place). A jointed character: one shape layer per rigid part, parented joint to joint (second pass for parents made later).
- **Name layers plainly** ("Waffle 2 · label", "CAMERA · Anchor = zoom point, Scale = zoom") and colour-label groups.
- **Many identical marks** (waffle cells, dots): one shape layer per group of marks that change on the same frames; the
  pops are in / out points, not keys. Brute-force check the grouping against the HTML's per-frame logic.

## 4. Keys as authored

Read each move from the animation's own data (start, end, curve) and write exactly those keys.
- **A key that starts or ends a move is a normal key: speed 0 on both sides.** A move stops at its key and the next starts from there; never carry speed from one move into the next (tried on a camera, and it looked wrong in the graph). Only the middle keys of one long path stay continuous.
- **Every key is eased on both sides,** even where a side changes nothing: the first key's in, the last key's out, and both sides of a stretch where the value stays put get Easy Ease (33.33), so the editor can change a value later without easing that side. Only real steady motion stays linear.
- **A move is 2 keys** with AE's own temporal ease from its cubic-bezier(x1, y1, x2, y2): out influence x1·100, out speed
  y1/x1 · Δv/Δt; in influence (1 − x2)·100, in speed (1 − y2)/(1 − x2) · Δv/Δt. For Position / Anchor, Δv is the length of
  the motion path; for other properties, signed per dimension.
- **A move with an arc** (hop, throw, swing): 2 Position keys on a curved motion path; the arc lives in the spatial
  handles (about a third of the way along, raised 4/3 of the arc's height), the timing in the temporal ease.
- **Travel along a long curve** / one thing following another: a motion path through as few points as hold the curve within
  a pixel or two; only the ends eased, the middle keys on whole frames with continuous speed. Follow with keys, not
  expressions (unless the editor asks).
- **A move already under way at frame 0** (a remapped opening): its 2 keys carry the tail of its curve (split the
  cubic-bezier with de Casteljau and renormalise), not a fresh ease.
- **One Position property** (no split X / Y). Scale is linear in AE: a zoom in equal ratios is one eased 2-key move; say how
  far it drifts mid-move.
- **Transform first, path keys last:** move, turn and scale with transform properties or parenting; path keys only for a
  real change of shape (e.g. a chart that squashes while its stroke keeps its width: 2 path keys).
- **Never sample and fit, never a key per frame, never a key that doesn't start or finish a move.** A layer gets a key on its
  first frame only when a move starts the layer (its in point = the start of its fade or rise). A key on a layer's last
  frame is a bug.
- **Before handing over,** list every keyed property with its key times (the exporter's `--report`) and check each key
  starts or ends a move; more keys than moves is a fault to fix.

## 5. Steady and ambient motion

- **Steady motion** (a constant drift, a flowing dash, a slow rotation, a steady slow push-in): 2 linear keys.
- **Ambient motion the editor won't usually retime** (sway, bob, waves, flow, flicker, a size kept constant on screen): a
  native expression (`value + amount*Math.sin(time*speed + phase)`, `wiggle()`, `loopOut()`, `toComp()`), every number from
  an Expression Controls Slider named plainly ("Sway amount", "Sway speed"). Export the authored keys with the ambient part
  switched off, so the keys hold only what was authored.
- No Posterize Time or stepped "on twos" motion unless asked.

## 6. Text

- **Typewriter / letter builds:** one Text Animator (Opacity 0) + Range Selector, Based On Characters, **Units Percent**
  (Index-unit Start keys turn to Hold in AE), Shape Square, Smoothness 0, End 100, **Start 0 → 100 in 2 keys** covering the
  whole line. Ease them to the reveal's curve (house curve = out 33 % / in 90 %); linear only when the letters really arrive
  at a steady rate. A line already partly typed at frame 0 starts from that percentage.
- **Fonts:** set by PostScript name (check the installed fonts first: on a Mac `~/Library/Fonts`, on Windows `C:\Windows\Fonts` and `%LOCALAPPDATA%\Microsoft\Windows\Fonts`), mapping each CSS weight to
  its face; a variable font's named instances count as faces.
- **Tracking** = CSS letter-spacing in em × 1000 (.16em → 160). Font size = 1080p px × 2. Position = the baseline point.
- **Centred / right text:** don't trust `sourceRectAtTime` during the build; set the justification and, where a layout
  depends on a measured width, measure it in the browser (headless Chrome) and pass the number, or use an Anchor Point
  expression.
- Title and paragraph entrances that copy one of the editor's installed AE text presets: apply that preset to the layer
  (their personal motion notes say which).

## 7. Native effects

Use AE's own effects so every one stays adjustable in Effect Controls; never bake an effect into keys or footage.

**Roughen Edges** (`ADBE Roughen Edges`), starting values measured from finished comps: Edge Type Roughen, Edge Sharpness
**10** (thin "line" strokes 5), Fractal Influence 1, Complexity 2, Evolution 0 (static, never keyed), Stretch / Offset 0,
Scale **10** unless noted. **Border** is set per element by its on-screen size:

| Element | On-screen Border (4K px) |
|---|---|
| Text ≤ 30 px, map labels | none (0.1) |
| Body paragraphs | ≈ 0.2 |
| Text 30–160 px | ≈ 3.5 % of the font size, 1.3 → 5.5 cap |
| Highlighter bars | 5.5 |
| Lines / strokes | 2–4 (Edge Sharpness 5); axes 1.5; region outlines 2 |
| Rings | 1.7 (< 400 px) / 3 |
| Shapes | ≤ 20 px 5.5 · < 200 px 4.8 · < 1200 px 6 · bigger 8 (full-frame: Sharpness 1) |
| Photos | small 1.2 · under ~420 px 2.6 · large rectangular photos and documents 6 (Scale 50) · cut-out figures 2.6 · torn print 15 (Scale 258) |
| Real-object cut-outs | none (0.1), unless the approved HTML roughens them: then match it |
| A clearly torn paper edge (white core showing) | from an SVG "tear" (blur σ 4.6, baseFrequency 0.055, 3 octaves, in world px under a ~1.9× camera): **Border 40, Scale 130, Complexity 3** in world-4K px, set by eye. A formula from the filter alone gives a finer, shallower edge (about Border 18 / Scale 36): the tear's blur and third octave make bigger bites than it predicts. Calibrate any new tear with 1–2 scratch builds (`tNN`) compared at 100 % |

Keep these in a small helper (`roughenFor({kind, role, fontPx, minSide, maxSide})`) in the build framework. **Border in AE =
on-screen Border ÷ the layer's own scale** (Roughen works in layer pixels before scale; a camera null's zoom scales the
HTML preview and AE alike, so divide by the layer's scale, not the camera's).

**Drop Shadow** from an SVG `feDropShadow dx dy stdDeviation flood-opacity` (1080p units): Direction = atan2(dx, −dy) in
degrees, Distance = √(dx² + dy²) × 2, Softness ≈ 2.5 × σ × 2, Opacity = flood-opacity × 255, colour as the flood colour;
divide Distance and Softness by the layer's scale. A shadow filtered in a rotated group rotates with the piece in both.

**Colour:** SVG `saturate(s)` is a straight blend toward grey, and so is AE's **Tint** (`ADBE Tint`, Map Black To black, Map
White To white, Amount to Tint = (1 − s) × 100): Tint 100 % = black and white, Tint 30 % = saturate(0.7). Prefer Tint over
Hue/Saturation, whose HLS saturation is not the same blend. Contrast with Curves or Levels. Check against the HTML render
once.

**Blur:** an SVG blur is in the filtered element's own units (its transform included): scale σ to 4K screen pixels first,
then Blurriness ≈ 2.8 × σ. Glow, Turbulent Displace and the rest likewise: AE's own effect wherever one does the job.

**Chromatic aberration** (RGB split): AE's VR Chromatic Aberrations, on its own adjustment layer under the finishing layer, never
baked into footage. Its measured behaviour, properties and browser recipe are with the finishing pass (section on what the editor
does); the library call is `L.chroma(comp, P, settings)`.

## 8. The build framework

One framework builds one or more comps per project from each animation's own exporter. Its parts:

- **An exporter per animation** (`<animation>/tools/export_ae.mjs`, Node) reads the animation's scene data and guards the
  layout numbers it copies from its `index.html` (stops with an error if the HTML changed them), builds a list of layer
  specs in 4K units, checks every key (whole frames, 2 per move, in order, inside the comp), and writes a part
  (`parts/<id>.jsx`) holding that data plus the builder code. Builder code is ES3 (guarded: no arrows, let/const,
  template strings).
- **A shared ExtendScript library** with one call per job: a comp, text, shape, image, null, audio, marker, keys
  (cubic-bezier → AE ease, linear, hold), path keys, setting an ease, Roughen Edges, Drop Shadow, a slider, chromatic aberration (`L.chroma`), queued
  expressions (set after every layer exists), parenting (keeping values or screen place), footage folders, and checks.
  Shared JS helpers beside it: the frame rate, the ×2 factor, snapping to frames, colour conversion, the named curves,
  fonts and `roughenFor`.
- **A build step** runs the exporters, collects every file into `ae/<Name>/Footage/`, rewrites the parts to import the
  copies, and writes one master `build.jsx`. Register each new exporter there.
- **A test harness** opens After Effects, waits until it answers, and runs the master script through a guarded runner:
  it builds only into a new project, refuses if the open project isn't one of its own builds or has unsaved changes, and
  suppresses dialogs. It writes a report (layers, key counts, off-frame keys, missing footage) and saves check frames per
  comp at listed times. The harness can return while AE is still writing the check frames: look for them again (or do
  another step first) before comparing.
- **Check** the frames against the HTML at the same times (frames from the render with ffmpeg `-ss`, or the page's
  `#f=<frame>` still) side by side; fix and rebuild until they match. Log the build in `BUILDS.md`.
- **A layout number the HTML measures at run time** (a text's `getBBox().width` placing the next label, say) is measured once
  in Chrome from the page's own font: a scratch page with the same `@font-face` that writes the value into the DOM, read
  with `--headless=new --dump-dom`. Put it in the exporter as a named constant with where it came from; never use
  `sourceRectAtTime` during the build.
- **A cell or bar that fills only in part** (a waffle cell at 0.8): one shape layer with the ellipse and a rectangle of the
  filled width, then Merge Paths (Intersect), then the Fill; its ring stays on its own layer, as in the HTML.
- **Grouped pops** (waffle cells, dots, ticks that pop on a beat): one shape layer per set of items that change on the same
  frames, no keys, the pops as in / out points; check every item on every frame against the HTML's own per-frame logic in
  the exporter and stop on any difference.

## 9. ExtendScript pitfalls

**Run every script through the skill's runner, never a bare `DoScript`:** on a Mac `scripts/ae_run.sh <script.jsx> [--timeout s] [--set name=value]`, on Windows `powershell -ExecutionPolicy Bypass -File scripts/ae_run.ps1 <script.jsx> [--timeout s] [--set name=value]` (same flags, same exit codes). Both need AE's "Allow Scripts to Write Files and Access Network" preference on: with it off, every run ends in a timeout with an empty log. The editor
can't sit by AE to click OK. It suppresses AE's dialogs, catches every error and prints it as text, and refuses scripts with an
unguarded `alert()`, `confirm()` or `prompt()`, which nothing can suppress. It keeps a lock instead of pinging AE, because a second
script sent while one is waiting raises its own warning dialog. On exit 3 (not open, or an earlier script still running) or 4 (timed
out), AE is waiting on something: stop, tell the editor exactly what to click or close, and wait. Never send AE anything more
meanwhile. If any AE problem isn't fixed in 1–2 minutes, do the same.
- **Never call `app.newProject()` on unsaved work:** AE opens a Save box that nothing suppresses. Use `$.global.__AE_NEW_PROJECT(/comp name pattern/)` from `ae_safe.jsx`; the runner refuses the raw call. `close(CloseOptions.DO_NOT_SAVE_CHANGES)` never asks.
- Closing a project can hang for a long time while a frame renders in the viewer, and a heavy comp may never finish. Ask the editor
  to close it; don't wait on it.
- `comp.saveFrameToPng` returns before the file is written: wait for the files, not the script's end.
- On a Mac `DoScript` answers 0, not the script's result; on Windows `AfterFX.com -r` returns before the script ends. Read results from a file.
- **Text presets go on by script with `L.preset()`** (no keys: their timing comes from the layer's in-point). A preset with compiled expressions doesn't run on AE's JavaScript engine, so use a Text Animator with the same look instead (`unfold` on `L.text()`: 2 keys on Offset). A script's `sourceRectAtTime()` can't confirm a preset's text shows: look at a rendered frame.
- **Setting a temporal ease turns both sides of a key Bezier.** Set the interpolation type again afterwards, or a linear side comes back eased (`L.keys()` does this now).
- **After every build, audit the keys against a list the exporter wrote** (`key-test/tools/audit.py` is the pattern): counts, whole frames, no hold or roving keys, eases. Then compare AE's frames with the preview: the audit can't see hidden text or a wrong size.
- **In a `catch`, write `e.toString()`, never `"text" + e`.** AE can't turn its own errors into text that way: the handler itself fails with "Object of type Error found where a Number, Array, or Property is needed" and raises a dialog, even inside `try`.
- Reading `maxValue` on a dropdown effect property raises an error; a `File` log needs `lineFeed = "Unix"`.


- **A chained conditional `a ? b : c ? d : e` is misread** as `(a ? b : c) ? d : e`: write if / else. It once turned every
  linear key into Hold.
- ES3 only in builder code: `var`, `function`, no arrows, `let`/`const`, template strings, spread, classes.
- A new shape layer's Position defaults to the comp centre: set `[0,0]` when its paths are in comp pixels.
- A property reference goes stale once its layer gains more properties: queue expressions by property path and set them
  after every layer exists.
- `sourceRectAtTime` can be wrong while the script runs (fonts not settled): don't lay out from it.
- Deterministic noise in JavaScript needs 32-bit integer maths (`Math.imul`), or it silently returns a constant.
- An alert stops scripting until someone clicks it: wrap test queries in `app.beginSuppressDialogs()` and try/catch, write
  results to a file, never call methods that alert on the wrong property type (e.g. `keyRoving` on a non-spatial property).
- `setTemporalEaseAtKey` wants as many eases as the property has dimensions (Scale is 3-D even on a 2-D layer): try the
  lengths.
- Torn edges baked into paths need the source filter's fine noise for their white rims, or the rims read as outlines.

## 10. Why sampled exports put keys on the first and last frame

An exporter that checks each value on every frame of a window and thins the samples to the fewest keys within a tolerance
puts keys on a layer's ends in four ways:
1. The thinning always keeps the first and last sample, so every sampled property starts and ends with a key, even where
   nothing moves.
2. Windows that run from 0 to the comp's end (camera, line widths, fades) put those end keys on the layer's first and last
   frames.
3. Values kept a fixed size on screen while the camera zooms (line widths, label sizes) change whenever the camera moves,
   so they really are keyed across the whole layer. (Better: an expression dividing by the camera's scale, with a slider.)
4. Padding each move's window by a step adds a key just before and after every move.
This is why section 4 forbids sampling: write each move's own 2 keys from the data.

## 11. What an editor changes in After Effects (learned from finished comps)

Measured from an editor's finished comps (their own templates and the exports they re-worked). Use these when exporting,
and when an HTML animation will go to AE, build its moves with them so the export carries them as authored.

**Caveats for any later study:** ambient keys (water, waves, grain plates) are not edits; timing shifts and gaps that
follow a voiceover taken from different parts of the video are not design edits; an editor's own eases carry AE's
four-decimal values (57.0118), while exporters write round pairs or fitted 0.5 steps.

**When the editor reworks an export, carry it all back.** Read their saved file, put every change into the animation's data (keys, eases, positions, anchors, in-points, not only the keys that look changed), rebuild, and compare frames against their file: the next build must match it. A rebuild from the old data throws their work away.

**A test of the keys (one of each move, reworked by hand):** the editor kept every key count and only moved and re-eased keys, so the
structure held: 2 keys a move, Position and Scale on the same frames and ease. What changed was timing: pieces and lines on the next
stop moved 26–36 frames earlier so the animation flows on instead of stopping and starting at each frame change; the pan got 6 frames
longer with a softer landing; and a stop was reframed so it shows none of the previous stop's elements (background may carry across).

**Eases (out influence / in influence, speed 0).** Starting points, not fixed values: the editor sets each by feel for its
motion, and the voiceover and the time a frame has decide lengths. A sensible base when nothing else says otherwise:
- Pictures and objects entering (slide, turn): **0.1 / 100**: they leave at once and spend the move settling, ~17–30
  frames. Opacity on the same span (0.01 / 100) as the base, or no fade at all when the style cuts them in with the motion.
- A small hop on an arc can take the entrance ease (0.01 / 100); a typewriter or a fade can simply be Easy Ease (33 / 33).
- Camera pans and pushes: **≈ 45–48 / 73–81** (a 62 / 68 pan was re-eased to 45 / 75). A frame push-in: 68 / 69.
- Line, stem, rule draws (Trim End): 40 / 80 or 55 / 85, 14–20 frames; routes 33 / 98.5 over 30; rings 54 / 81.
- Highlighter wipe: 57 / 74, 12–20 frames. Bars growing: 54 / 74. A drop: 100 / 14 (falls faster, stops short).
- Linear only for steady motion: slow spins and drifts are 2 linear keys across the whole shot, never an expression.

**Motion:**
- Entrances slide, turn and (usually) fade together (Position, Rotation, Opacity, 2 keys each, the same ease); travel is
  larger than a 50 px rise (200–500 px at 4K); turns of 15–40° landing on 0 or a small tilt. Staggers and lengths follow
  the voiceover, the time the element has and the framing (no fixed numbers).
- Every line draws on (stems, rings, boxes, rules, routes, axes) with Trim Paths End; an axis grows in steps with the story
  (holds between). Tick marks pop with Scale.
- Camera: tighter framing (about 1.1–1.3× a first export's zoom); no zoom-out dip mid-pan; two moves in a row become one
  curved move (a roving middle key); a slight opening drift rather than a still first frame; section changes are cuts
  (Hold keys jumping the camera at once), or in templates stepped zooms (Hold keys at 100, 97.6, 95.6 …). Hold keys only
  at a cut or between two voiceover pieces, never inside a move.
- Timing to the voiceover: a title starts on its first spoken word or up to 0.5 s before it. Moves already under way at
  frame 0 start before the comp (negative key times) rather than snapping on.

**Text:** where the editor has AE text presets for word-by-word or line-by-line unfolds, titles and paragraphs use them:
apply the preset itself to the text layer where the HTML used that unfold. Where a typewriter is wanted, the letters
appear without fading in.

**Layers:** a null per group (one for the whole frame, one per collage group) is for organising and moving a group
together, used when it helps, not a fixed structure. Voiceover pieces sit under everything.

**Effects:**
- Each picture graded on its own (Curves, Lumetri, Hue/Saturation, Tint) so different kinds of elements blend in one
  frame. Do this in translations too.
- Highlighter (in a cut-paper collage style): the bar is a stroke with **Wiggle Paths** (a shape operator: Size 13,
  Detail 17, Points Corner, Correlation 50, not moving) for the crooked edge, plus Roughen Edges; where the text is darker
  than the bar, an Invert + Curves adjustment layer above it turns the text light for legibility. Use the wiggle and
  roughen when that style is used, not as a default.
- Zoom-compensating expressions (a line's width or a label's size divided by the camera's scale, so it stays the same
  size on screen while the camera zooms) are worth keeping. They read the camera layer's Scale every frame, so they follow
  whatever keys the editor sets; they don't see a zoom made by another layer (a null above the camera, a precomp's scale).
- **The project's finishing pass, as one adjustment layer on top, with native effects** (for example Add Grain and
  Posterize Time; a chromatic aberration gets its own adjustment layer directly under it, see below): the editor gives the settings per project (`L.applyFinish()` builds it; read them from the comp that matters,
  since a project can hold two versions, such as a colour-grain template). The previews carry the same finish, measured:
  - **Posterize Time** at rate r shows, at comp time t, the scene at `floor(t × r) / r`, counted from the comp's start whatever
    the adjustment layer's in point, and keys are read at that exact sub-frame time. Outside the layer's span, time runs true.
    In a preview, draw each frame at that time.
  - **Add Grain, any settings** (every control tested): render it once in AE, per settings, and use that frame as the plate;
    it is one fixed field for a given size and settings, the same in every comp. Then match its Blending Mode. Mode numbers are
    the menu's order (scripts can't read the names). All five matched AE in Chrome, mean under 0.25 of 255, a rare few pixels up
    to 5. Plate = AE on flat grey 128 (mode 4: on black), kept in full colour:

    | Mode | What it does | In a browser (SVG `feImage` + `feComposite arithmetic`, c = 128 / 255, sRGB) |
    |---|---|---|
    | 1 | Strong in darks, none on white, pattern flipped: out = L − g(1 − L) | k1 1, k2 1 − c, k3 −1, k4 c |
    | 2 | Strong in lights, none on black: out = L + gL | k1 1, k2 1 − c, k3 0, k4 0 |
    | 3 | Plain addition, same strength on every level: out = L + g, clipped | k1 0, k2 1, k3 1, k4 −c |
    | 4 | One-sided, lightens darks: screen of a plate rendered on black | `mix-blend-mode: screen` |
    | 5 | Strongest in midtones, none at black or white | `mix-blend-mode: overlay` |

    - Strength: **Intensity** is linear. **Size** enlarges the grain and multiplies strength with it (2 → ×2, 4 → ×4). **Softness**
      blurs the grain, strength unchanged (0 = single pixels). **Aspect Ratio** stretches it sideways above 1. **Presets** (14) each set
      the R, G, B strengths and grain size; those are the base Intensity multiplies. **Random Seed** gives a different field.
    - **Monochromatic on:** one pattern, at the preset's channel ratio, and the per-channel controls do nothing. **Off:** separate
      R, G, B patterns, about 1.7× stronger; Red / Green / Blue Intensity and Highlights etc. work, Saturation pulls it towards
      mono. **Tint** colours the grain through the channel strengths.
    - **Shadows / Midtones / Highlights** scale strength along a straight line: Shadows at black, Midtones at Midpoint, Highlights at
      white. At 1 / 1 / 1 Midpoint does nothing. Other values need a strength curve in the preview (not built or tested yet).
    - **Animation Speed** runs 0 to 1: 0 is static, 0.5 a new field every 2 frames, 1 a new field every frame. Animate Smoothly changed
      nothing at 1. Moving grain needs a loop of plates, not one (not built or tested yet).
    - **Blend with Original** (Amount) only protects colours near its Matching Color. Viewing Mode must be Final Output.
    - A 1080p review shows 4K grain weaker (about 61 % at Size 1), since pixels average.
  - **VR Chromatic Aberrations** (`Mettle SkyBox Chromatic Aberrat`, bundled with AE) on its own adjustment layer, directly under
    the finishing layer (`L.chroma()`, called by `L.applyFinish` from a `chroma.settings` entry). It **needs GPU rendering**: under
    Mercury Software Only it draws only a red "This effect requires GPU acceleration" banner, so the project must be Metal / CUDA
    (`L.chroma` switches it). Set the properties by matchName, `…Aberrat-0009` Auto VR Properties, `-0002` Frame Layout, `-0010` /
    `-0011` Horizontal / Vertical FOV, `-0003` Point of Interest, `-0004/5/6` Aberration R / G / B, `-0007` Falloff Distance,
    `-0008` Falloff Invert (defaults R −10, B 10, Falloff Distance 50). Measured at Frame Layout 1, FOV 360 × 180, 8 bpc:
    - It treats the frame as a 360 × 180 panorama and moves each channel straight towards or away from the Point of Interest **on
      that sphere** (the angle around the POI never changes). Flattened, that's mostly radial but bent, with sideways parts away
      from the centre lines. Positive Aberration = outward, negative = inward; linear in the amount; every channel alike.
    - Output at angle θ (radians) from the POI samples the channel at θ · (1 − a·e^(−1.387·θ^2.2)), **a = 0.00895 × Aberration**.
      It peaks about 34° out and is gone by 120°: strongest a third of the way to the edge and fading towards it, unlike a lens
      aberration. At ±2 on a 4K frame: 1.8 px at 100 px from the POI, **4.2 px at its peak, 364 px out** (4.7 px vertically,
      409 px out), 1.9 px at 700, 0.6 at 900, 0.15 at 1080, about 0 beyond.
    - Falloff Distance hardly matters from 0 to 8. Falloff Invert turns it into a ring (none in the middle, signs flipped) and a
      Horizontal FOV of 180 roughly doubles and spreads it; neither is modelled. It's static: Posterize Time doesn't touch it.
    - The top and bottom rows are the panorama's poles: AE smears them sideways (strong on fine detail, fading over ~100 rows).
    - **In a browser:** the move is fixed, so precompute maps (`make_chroma.py`) and apply them with an SVG filter
      (`Finish.chroma(el)`, chained before the grain). Chrome's `feDisplacementMap` takes the **nearest pixel** (round(x + d)), so
      each moved channel is 4 whole-pixel taps blended by fraction maps with `feComposite arithmetic`: exact bilinear. Chrome vs AE
      at 4K: mean 0.24–0.33 of 255, 99.9 % under 3; 1080p reviews about 1.1–1.4, most of it the browser's own downscale of the picture. The pole smear isn't matched (the top and bottom few
      rows stay put). Study: `ae-study/chroma-test/FINDINGS.md` (the editor's study folder).
  - **Vivid Light**, where a style uses it, in a browser: colour burn with 2t below mid grey, colour dodge with 2t − 1 above, stacked at
    the layer's opacity. AE scales the texture first and blends after, so split it after the camera's scale: two copies, each
    with an SVG `feComponentTransfer` table (`0 1 1` for burn, `0 0 1` for dodge). Splitting the file beforehand goes wrong when zooming.
  - **A shrinking texture** needs smoothing a browser's own scaling doesn't give: it stays too strong on zoom-outs. Draw it as a
    repeating fill on a frame-sized canvas from halved copies of the tile, blending the two nearest sizes. That also means no edge can show.
  - Compare against AE with a lossless render (`--format png-sequence`): plain headless Chrome stills can capture before the plate loads.

**The texture lies on the world plane.** The texture file changes per project and style; the placement doesn't:
- **Parented to the camera** (the camera null, or the frame's push-in null), so it pans and zooms with the pieces, as if
  the camera filmed one flat sheet. Never fixed to the screen.
- **No edge ever shows:** either one still sized to cover the widest framing with a margin (at 100 % under a push-in that
  only zooms in; scaled up under a camera that pulls out, keeping about 90 px spare at the widest), or a tile with
  **CC RepeTile** expanded in every direction far enough for the whole camera path (thousands of pixels on a long strip).
  Check coverage at every frame from the camera's keys before handing over.
- **Where in the stack:** usually just above the background paper (and its patterns), under the pieces, so the paper is
  textured and the cut-outs stay clean; a second, lighter copy can sit higher (over a map's land, under its labels and
  routes). Sometimes it goes on top of everything.
- **Blend and opacity belong to the texture and the style,** not to this rule: ask for them per project. (One finished style used Vivid Light at 20–50 %, for that texture only.)
- **Where the camera zooms in and out a lot** (8–12×, say), key the texture's Scale on the same keys as the
  camera's zooms so it is never too small or too big on screen; on ordinary moves it just rides the camera.
- **A tile must be seamless:** a plain texture repeated with CC RepeTile shows a line at each join (tested). Make the tile
  seamless first, or overlap copies with feathered Subtract masks, as one finished comp does (120 px feather).
- `L.texture()` reads the camera on every frame to set the RepeTile expansion, and `L.applyFinish()` adds texture and finishing layer from the project's settings file.
- In the preview HTML the same: the texture is a tiled layer inside the camera's world group, not a screen overlay.
