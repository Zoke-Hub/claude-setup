---
name: keep-chat-archive
description: In long sessions, keep a readable archive of the whole chat with the chat-archive skill (it always archives from the first message)
metadata:
  type: feedback
---

The user expects to be able to scroll back through a whole session later. The desktop app stops loading the earliest
messages once a session is very large, its own Export refuses very large sessions, and Claude Code deletes transcripts
after about 30 days by default.

**How to apply:** in long sessions (many renders, images or compactions), run the `chat-archive` skill at milestones and
before and after a compaction, without being asked. Whenever it runs, it archives the **whole session from the first
message**, because it reads the full saved transcript, compactions included. It writes a readable HTML page plus a gzip
copy of the raw transcript into `<project>/chat-archive/`; with `--out <folder>` it writes anywhere permanent (useful
when a session wasn't opened in a project folder). Related: [[keep-every-render]].
