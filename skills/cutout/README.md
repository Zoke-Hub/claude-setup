# Cut-outs: BiRefNet HR, at the original's full resolution

The default cut-out tool for every project, chosen on 2026-10-19 after a side-by-side at 100 % on the 1975 lamp (CMA
1999.261, 4674 × 3729 TIFF) and padlock (Met 10.100.186a,b):

| Tool | Result |
|---|---|
| **BiRefNet HR** (MIT, local, MPS) | **Winner.** Crisp edges that follow the object; no cast shadow; clears holes (the padlock's loop) and keeps real dark parts (the keyhole). |
| BiRefNet HR-matting | Softer edges, a faint milky halo where the floor reflects. Use only for hair/fur/smoke. Not pre-downloaded since 2026-10-20: `--model hr-matting` fetches it on first use. |
| Apple Vision (`vision_cutout`) | Fast (1 s) and full-res, but blurry feathered edges, kept some shadow, punched a hole in the padlock. Removed 2026-10-20 (backup in `~/.claude/sync-backups/20261020-165612-cleanup/`). |
| hyperframes remove-background (old) | Kept the grey backdrop inside the padlock's loop, cut the lamp's bowl off. Don't use for final pieces. Its model cache was deleted 2026-10-20. |

## Use

```bash
~/.claude/venvs/cutout/bin/python ~/.claude/skills/cutout/scripts/birefnet_cutout.py <original> <out.png>
```

(Windows: `~/.claude/venvs/cutout/Scripts/python.exe`.)

- The output is the same width and height as the original: original pixels plus an alpha channel. Nothing is downscaled.
- It takes 1–4 minutes per image on the Mac (MPS); on the Windows PC it uses CUDA.
- Options:
  - `--model hr-matting` for hair, fur or smoke;
  - `--mask m.png` to also save the matte;
  - `--keep-edge-colour` to skip the edge-colour cleanup;
  - `--no-refine` to skip the full-resolution guided-filter edge snap.
- The environment is shared by every project: `~/.claude/venvs/cutout/` (Python 3.12, torch, transformers 4, timm,
  kornia, einops, opencv, Pillow). The setup pack's `sync.py install --cutout-env` builds it. The model
  `ZhengPeng7/BiRefNet_HR` is cached in `~/.cache/huggingface` (HR-matting only if you've used `--model hr-matting`).
- Always look at the result at 100 % on the paper colour before using it.
