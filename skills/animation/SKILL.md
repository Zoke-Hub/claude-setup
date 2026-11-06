---
name: animation
description: House rules for every animation, in one place - how things move (a curve picked per move, the house curve cubic-bezier(0.33, 0, 0.10, 1), 25 fps, titles word by word, photo entrances, no wiggle, bar-wipe highlights, counters), timing to the voiceover, first frame never empty, spacing, cut-out puppets (pieces, ball joints, limbs under cloth, walks), After Effects export (clean editable projects, keys as authored, native effects, the script runner), a project's finishing pass matched between the HTML preview and AE (Posterize Time, Add Grain, texture, chromatic aberration), and what finished videos showed about animation (one graphic world per video, chapter cards inside it, the device for what can't be filmed, a sound for every element). Use whenever building, animating, timing, reviewing or exporting any animated graphic, title, chart, map, collage, puppet or AE project. Replaces animation-easing, after-effects-translation and puppet-rig.
---

# Animation

One skill for how animations are built, moved, rigged and exported. It replaces three earlier skills (animation-easing, after-effects-translation, puppet-rig) and the animation house notes; their rules are kept word for word in `references/`.

**Do only what's asked, one step at a time.** If the ask is easing for one title, read the easing rules and do that. Don't also rig, export or restyle anything unless asked.

**House rules win** over any other skill's easing, motion and frame-rate defaults (motion-graphics, motion-broll, the explainer skills, hyperframes-animation).

## Which file to read

| The task | Read |
|---|---|
| Any motion: curves, timing, titles, photos, lines, camera, highlights, counters, the preview checklist | `references/easing.md` and `references/house/motion-rules.md` |
| Timing beats under a voiceover | `references/house/time-to-the-voiceover.md` |
| The opening frame of an animation | `references/house/first-frame-never-empty.md` |
| Spacing on a frame or in an interface | `references/house/spacing-groups.md` |
| A cut-out character: pieces, joints, cloth, walks, checks | `references/puppet-rig.md` and `references/house/cutout-pieces-sheet.md` |
| Exporting to After Effects, or keeping an exporter current while building | `references/after-effects.md`, `references/house/after-effects-export.md` and `references/house/build-ae-export-alongside.md` |
| A project's finishing pass in the HTML preview and in AE: Posterize Time, Add Grain, texture, VR Chromatic Aberrations (the measured browser recipe for each, and how the export stacks them) | `references/after-effects.md` (the finishing pass, in the section on what the editor does), and the project's finish kit if it has one |
| Planning a video's animations: how much, which device, the graphic world, chapter cards, history through a person, sound per element | `references/from-the-studies.md` |

Read the file that fits before writing the first tween, cutting the first piece or writing the first ExtendScript line.

## Scripts

- `scripts/ae_run.sh` (Mac) and `scripts/ae_run.ps1` (Windows): run every After Effects script through these, never a bare DoScript. `scripts/ae_safe.jsx` is their wrapper.
- `scripts/joints.py`, `scripts/one_dark.py`, `scripts/pieces_sheet.py`, `scripts/rest_match.py`, `scripts/puppet.py`: the cut-out puppet tools described in `references/puppet-rig.md`.

## The rules most often needed

- 25 fps, durations ×1.5, a curve picked for each move; the house curve only where it suits.
- Titles unfold word by word from the baseline, paragraphs line by line; text is perfectly still once it lands.
- The first frame is never empty. Every animation enters and leaves on a hard cut.
- Under a voiceover, transcribe first: a name lands on its word, a title starts about 0.4 s before its word, pauses are holds.
- Gaps inside a group are smaller than gaps between groups.
- After Effects: export only when told to go, a fresh project each time, assets collected beside the `.aep`, keys as authored with AE's own easing, whole frames, native effects, live text.
- A project's finishing pass looks the same in the HTML preview as in AE: build it into the preview while animating (Posterize Time's held frames, the grain plate, the texture, a chromatic aberration's maps), not only at export. In AE, each is native, on adjustment layers on top: the finishing layer, then a chromatic aberration directly under it.
- A puppet at its own pose is exactly the drawing; ball joints never bigger than the distance to the drawn edge; one dark per figure.
- One graphic world per video, built from references around the topic; chapter cards built inside it.
- Every element that arrives gets a sound chosen to the object.
