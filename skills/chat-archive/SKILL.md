---
name: chat-archive
description: Save a whole Claude Code session as a readable HTML archive (every message, reply, file sent and artifact link, plus a gzip of the raw transcript that never expires). Whenever it is asked for, at any point in a chat, it archives the entire session from the first message. Use in long sessions at milestones and before/after a compaction, or when the user wants to keep, revisit, export or scroll back through a whole chat.
---

# Chat archive

The desktop app stops loading the start of very large sessions, its Export refuses very large sessions, and Claude
Code deletes transcripts after about 30 days. This keeps a permanent, readable copy.

**It always archives the whole session, from the first message.** Whenever it is asked for, at any point in a chat,
early or late, it reads the session's full saved transcript (`~/.claude/projects/<folder>/<session>.jsonl`), which keeps
everything, compactions included, and rebuilds the page from all of it. Nothing that scrolled out of view or was
compacted is missed.

```bash
python3.12 ~/.claude/skills/chat-archive/scripts/build_archive.py                     # this session, from its folder
python3.12 ~/.claude/skills/chat-archive/scripts/build_archive.py --out ~/Documents/chat-archives   # save it elsewhere
python3.12 ~/.claude/skills/chat-archive/scripts/build_archive.py <session-id> --project <folder>
```

- Run it from the folder the session was opened in (or pass `--project`): transcripts live in
  `~/.claude/projects/<that folder's path, non-alphanumerics -> "-">/`. With no session id, the most recently updated
  transcript there is used, which is the current session.
- Writes `<project>/chat-archive/<session title> - chat archive.html` and `chat-archive/raw/<session>.jsonl.gz`.
- **`--out <folder>`** writes the page and `raw/` to that folder instead. Use it when the session wasn't opened in a
  project folder, so the archive lands somewhere permanent rather than a temporary or home folder; ask the user where
  if they haven't said.
- Re-run it whenever you want it current; it rewrites the HTML from the full transcript.
- Standard library only; any Python 3.8+ works (on a Mac `python3.12` or `/usr/bin/python3`, on Windows `py -3.12`).
- In long sessions (many renders, images, compactions), re-run it at milestones without being asked.
