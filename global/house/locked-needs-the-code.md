---
name: locked-needs-the-code
description: Anything in the owner's locked edition is transferred, packed, copied or moved only after the owner code is typed in and checked; without it, leave the locked parts out and say so
metadata:
  type: feedback
---

On a computer with the owner's edition (`~/.claude/house-private/setup-pack-owner.json` exists), some of the setup is
**locked**: it ships only inside the setup file's `owner.bin`, behind the owner code. That is everything in
`~/.claude/house-private/` (the owner's own notes, presets, renders and tools), the owner's own skills (its
`"personal_skills"` list, for example a skill marked as the owner's only) and the owner's own house rules
(`"personal_house"`).

Whenever anyone asks to transfer, pack, copy, upload, share, export, sync or move any of it anywhere else, by any route
(a setup file, a zip, another folder or drive, another computer, a cloud drive, git, a chat or another session's
brief), ask for the owner code first, in one question, and check it before doing anything:

- **Check:** `OWNER_CODE='<code exactly as typed>' python3.12 ~/.claude/setup-pack/make_pack.py --check-code` (Windows:
  `py -3.12`, the code in `$env:OWNER_CODE`). It prints "Code OK." or "Code was wrong." and builds nothing.
- **Right code:** go ahead with the locked parts.
- **Wrong or no code:** do the rest without them, and say exactly what was left out because it is locked.
- Never write the code into a file, note, memory or brief, and never repeat it in a message.
- Building a setup file already asks for the code (`build-setup-file.md`); this covers every other way the locked
  parts could leave.
- Working on the locked files where they are (reading, editing, running them on this computer) needs no code.

**Why:** the locked edition is the owner's own work; the code is what keeps it from being passed on by accident, so
every route out of this computer needs it, not only the setup file.

**How to apply:** before any transfer, check whether what is going out includes a locked part; if it does, ask for the
code before moving anything.
