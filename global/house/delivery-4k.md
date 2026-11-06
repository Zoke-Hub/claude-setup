---
name: delivery-4k
description: The delivered file is always 4K (3840×2160, 16:9, 25 fps); review rounds render at 1080p; render 4K only when the user asks; sources and cut-outs at full resolution
metadata:
  type: feedback
---

**Build for 4K, review at 1080p, render 4K only on request.**

- **Delivery:** the final file is always 4K, 3840 × 2160, 16:9, 25 fps. Compositions, renders and After Effects exports
  are built at that size, or must survive a 2× upscale with nothing soft.
- **Review rounds:** render previews and drafts at 1080p. Render the 4K master only when the user asks for it; the
  composition stays built for 4K either way.
- **Sources:** keep every image at the best resolution that can be found (museum lossless master or TIFF, the Commons
  original, never a thumbnail). Never resize a source down in the pipeline.
- **Cut-outs:** made at the original's full size, never baked at "2× display size", with full-resolution masks and
  clean edges (the `cutout` skill). Check every cut-out at 100 % before using it.

**Why:** pieces baked at their preview size looked soft once the comp moved to 4K, and full 4K renders during review
rounds waste time the user would rather spend on the next round.

**How to apply:** have the render script default to a 1080p preview with a 4K flag used only on the user's go. Keep
every render numbered ([[keep-every-render]]). Related: [[after-effects-export]].
