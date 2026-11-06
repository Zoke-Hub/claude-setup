---
name: cutout
description: Cut an object or person out of a photo at its full original resolution with BiRefNet HR, locally, as a transparent PNG with clean edges. Use whenever someone wants a cut-out, a background removed, an object isolated, a transparent PNG, or a "real object" piece for a collage from a photo, scan, engraving or museum image. Never use hyperframes remove-background for final pieces.
---

# Cut-out (BiRefNet HR, full resolution)

The one cut-out tool for every project. It won a 100 % side-by-side on 2026-10-19 against BiRefNet HR-matting, Apple
Vision and hyperframes remove-background (details and the comparison table: `README.md` here).

```bash
~/.claude/venvs/cutout/bin/python ~/.claude/skills/cutout/scripts/birefnet_cutout.py <original> <out.png>
```

On Windows the Python is `~/.claude/venvs/cutout/Scripts/python.exe`. If the venv is missing, the setup pack's
`sync.py install --cutout-env` builds it (or build it by hand: `uv venv ~/.claude/venvs/cutout -p 3.12`, then
`uv pip install -p <its python> torch "transformers>=4.57,<5" timm kornia einops opencv-python pillow numpy`).

- **Full size, always.** The output is the original's exact width and height: original pixels plus an alpha channel.
  Never downscale the source first, and always start from the largest file that exists (museum TIFF/print, Commons
  original). A guided-filter edge snap and an edge-colour cleanup are built in.
- **Memory and speed are set per computer.** At 2048 the model needs about 16–18 GB of GPU memory in full precision and
  about 9 GB in half precision (the mattes look the same). The machine check, `scripts/probe_machine.py` (the setup runs
  it; run it again after a hardware change), picks the precision and working size that fit and saves them in
  `machine.json` in the cut-out venv. On Apple silicon the script also caps GPU memory at the system's recommended
  working set, so an over-large job stops with an error instead of freezing the computer; if the GPU still runs out, it
  retries in half precision, then at a smaller working size, and prints what it used (`ok … at 2048, half precision on
  mps`). Don't run two cut-outs, or a cut-out next to another memory-heavy app, at the same time.
- **Very large sources** (~100 MP and up) still strain the full-size edge refinement: make a copy with a 5000 px long
  side and cut that out; keep the full original in `originals/`. 5000 px is far beyond what a 4K collage piece needs.
- **Device:** picks CUDA, then MPS (Apple silicon), then CPU. About 10–20 s per image on an Apple-silicon Mac in half
  precision; seconds on an NVIDIA GPU; minutes on a CPU. `--precision half|full` overrides the machine check.
- **Options:** `--model hr-matting` for hair, fur or smoke (downloads that model on first use); `--mask m.png` to also
  save the matte; `--keep-edge-colour` to skip the edge cleanup; `--no-refine` to skip the edge snap.
- **Check every result at 100 % on the paper colour** before using it: solid, nothing
  showing through, no baked-in shadow from the source photo: no cast shadow, floor or tabletop left under or behind the
  object (BiRefNet keeps these, and an editor otherwise has to mask them out by hand); holes (a padlock's loop) cleared, real dark parts kept.
  Stamps stay as plain rectangular prints (keying punches holes in them).
- Only cut out images the user has picked (house rule: show numbered options and wait for picks first).
- **A character to be rigged:** the cut-out is only the start. Each piece is then shaped on purpose into the body part it
  is (the `puppet-rig` skill): the tool's output is pixels, not limbs.

The same Python has Pillow, so other skills (markroom's `render_marks.py`) can use it too.
