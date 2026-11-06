---
name: check-symlinks-before-deleting
description: Before deleting anything or copying a folder to start new work in it, check for symlinks; a copied folder can still point at the original's files
metadata:
  type: feedback
---

**Check for symlinks before deleting, and before writing into a copied folder.** Projects often link shared folders
(assets, fonts, textures) into each piece of work instead of copying them. A copy of that work keeps the links, so the
copy still points at the original's files.

- **Before any `rm` (or a move or overwrite) under a folder,** check that the path and the folders above it inside the
  project are not links: `ls -la`, `realpath`. Deleting "inside the copy" through a link deletes the original's real files.
- **When starting new work from a copy of an earlier piece,** first list its links (`ls -la` in each asset folder, or
  `find . -type l`) and replace each one with a link to the new piece's own folder, or with an empty folder, before
  writing anything into it.
- **Clearing out old candidates or scratch files** gets the same check, since those folders are often the linked ones.

**Why:** a cleanup inside a copied folder once followed a link and deleted the original piece's sourced pictures and
cut-outs, which could only partly be restored. A link looks like an ordinary folder in most listings.

**How to apply:** make the check part of copying any piece of work, and run it before every delete. Never `rm` render
outputs or originals at all ([[keep-every-render]]); move doubtful files to the Trash instead.
