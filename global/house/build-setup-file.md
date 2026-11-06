---
name: build-setup-file
description: When asked to build, make or repack the setup file (setup pack), ask General or Full on the owner's computers and build the general one elsewhere; it goes to Downloads and older ones go to the Trash
metadata:
  type: feedback
---

When someone asks to build, make, update or repack the setup file (the setup pack):

- **The builder** is `~/.claude/setup-pack/make_pack.py`, which the pack installs on every computer. Run it with
  Python 3.10+ (`python3.12` on a Mac, `py -3.12` on Windows).
- **On a computer with the owner's edition** (`~/.claude/house-private/setup-pack-owner.json` exists), ask first, with
  one question: "Which setup file? Type the code for full setup file." Options:
  - **General setup file**: "Pack-up everything for transfer."
  - **Not now**: "Build nothing for now." (The app needs at least two options; this one stays out of the way.)
  The full setup file has no option of its own: the code is typed in the app's own Other box, which is always last.
  A code typed there means Full. Then run
  `make_pack.py --full --owner-code '<code>'` with the code exactly as typed, same capitals, in single quotes. If it
  prints "Code was wrong: building the general setup file.", tell them exactly that. Never write the code into a file,
  note or memory, and never repeat it in a message.
- **On any other computer**, don't ask: build the general setup file (`make_pack.py`). There is no full option there;
  the owner's part was never installed on it.
- **The git edition** (`make_pack.py --git`, no tools inside; setup installs the picked ones from GitHub) ends with a list
  of third-party skills that carry no licence file. Before it goes in a public repo, tell the person to check on each one's
  source that it may be redistributed (a private repo doesn't need this).
- **Where it goes:** the zip and its `PROMPT.md` go to `~/Downloads`, or to a folder the person names (`--out <folder>`,
  an external drive too). First move the older setup zips and `PROMPT.md` in that folder to the Trash (Finder on a Mac;
  the Recycle Bin on Windows), never deleting them for good.
- **What goes in** is this computer's own setup: its rules, house notes, skills and tools, as the person has them. The
  protected tools follow [[protected-tools]].
- **Afterwards,** tell them the new zip's name and size and what changed since the last one.

**Why:** every computer the pack is installed on can pass a setup on, but only the owner's computers can pass on the
owner's own edition, and only with the code.

**How to apply:** check which kind of computer this is before asking anything, and keep the question to the two
options.
