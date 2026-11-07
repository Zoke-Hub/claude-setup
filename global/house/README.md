# House notes

The full notes behind the "How to work" rules in `~/.claude/CLAUDE.md`, for every project. `CLAUDE.md` says which to
read when. Notes link to each other with [[name]]. Keep this list in step when adding a note.

**4K delivery**
- [4K delivery](delivery-4k.md) — deliver 3840×2160 at 25 fps; review rounds at 1080p; 4K renders only on request; sources and cut-outs at full resolution

**Motion rules**
- [Motion rules](motion-rules.md) — titles unfold word by word from the baseline, paragraphs line by line, photos a quick fade + small rise, staggered; each move's curve picked for it (house curve only where it suits); bar-wipe highlights
- [First frame never empty](first-frame-never-empty.md) — frame 0 opens on a partly built shot; the opening is retimed so later beats keep their frames
- [Time to the voiceover](time-to-the-voiceover.md) — transcribe the voiceover first; a name lands on its spoken word, a title starts a little before it, pauses are holds
- [Spacing shows groups](spacing-groups.md) — gaps inside a group are smaller than gaps between groups, from one fixed scale, in interfaces and animation frames
- [Subtitle timing](subtitle-timing.md) — sentence subtitles stay on at least 1 second: hold into a pause, otherwise club with a neighbour and re-break into whole phrases; soft character limit, in sync, same words; not for word-by-word animated captions

**Working rules**
- [Ask before building](ask-before-building.md) — storyboard → questions → numbered still previews → build; from a script, build only the lines sent, read the lines around them, flag mismatches
- [Approve images first](approve-images-first.md) — numbered contact sheet + licence table, posted in the MarkRoom (every pick sheet goes there, finished object cut-outs don't); wait for picks before any cut-out or use
- [Verify facts on screen](verify-facts-on-screen.md) — check every date, quote and claim with sources while building; flag script mismatches
- [Keep every render](keep-every-render.md) — never overwrite or delete renders or previews; numbered rNN outputs + RENDERS.md log; dated handoff notes, old ones archived as superseded
- [Reference study scope](reference-study-scope.md) — study a reference's motion, framing, design and entrances only, not its subject; in the user's own finished edit, only their real changes
- [After Effects export](after-effects-export.md) — only on the user's go; fresh project; assets collected into a Footage folder beside the project; editable layers; motion keyed as authored from the animation's data, never sampled and fitted (2 keys a move with AE easing; arcs = 2 keys on a curved motion path; long curves = motion path with continuous middle keys; every key, in / out point, marker and section start on a whole frame, no roving keys; following = keys, not expressions; one camera null with Anchor = zoom point; one Position, no split X / Y; no stray end keys), steady motion 2 linear keys, never a key per frame; typewriter / letter builds = one Range Selector with 2 keys, eased in AE to the reveal's curve (linear only for a steady rate); movement by transform properties (path keys only for a real change of shape); ambient motion as native expressions with Slider Controls; no Posterize Time unless asked; effects made with AE's built-in effects, stills stay stills unless asked; chained `?:` written as if / else in ExtendScript
- [Build the AE export alongside](build-ae-export-alongside.md) — keep each animation's After Effects exporter current while building, so the AE file is a quick re-run
- [Dashboard means the MarkRoom](dashboard-means-markroom.md) — any review page is the MarkRoom (image + video tabs, Version dropdown)
- [Read the MarkRoom's overall notes](markroom-read-overall-notes.md) — every round, read the marks AND the whole-image/video notes on every board; reply to and close both
- [Keep a chat archive](keep-chat-archive.md) — run the chat-archive skill at milestones; it always archives the whole session
- [General rules only](general-rules-only.md) — a rule the user asks for is written for every project: no project names, subjects, files, numbers or anecdotes; project-only notes go in that project's memory
- [Cut-out pieces sheet](cutout-pieces-sheet.md) — rigged/character animation: ask if a pieces sheet is wanted; if yes, every piece shaped on purpose and shown once, pulled apart in place, approved before animating; show the current state unchanged when asked
- [Ask before new sessions](ask-before-new-sessions.md) — keep work in the chat it was asked in; move a task to another session or sub-chat only when the user says so, or ask first
- [Check every cut](check-every-cut.md) — line edges from the audio, not the transcript; a speaker's shot ends on their real end of speech (never their next sentence starting); every cut checked on its frames: no stray frame, no doubled or clipped word
- [Ask when stuck](ask-when-stuck.md) — a blocked step not fixed in 1–2 minutes: stop, say what's needed, ask, wait
- [Clean-up check](cleanup-check.md) — after a feature or a finished piece of work (above all a UI redesign), ask whether to check for dead code, duplicate logic, unused components and unnecessary complexity; find first, change only what's picked
- [Releases reach every package](release-every-package.md) — a change several packages or editions share goes into every one that carries it, in the same release, each tested with a first install and an update over edited, deleted and added files; a package left out is named and asked about; ask when unsure
- [Answer buttons are complete](answer-buttons-complete.md) — a reply button sends at once, so its message is a whole answer; never a half-sentence for the user to finish
- [No personal assumptions](no-personal-assumptions.md) — never infer the user's language, nationality, culture, beliefs or tastes from their work; suggestions come from what they asked for and said
- [Protected tools](protected-tools.md) — MarkRoom, PulseWise, Folio, logo-recreation and animation (formerly after-effects-translation): changed freely on the author's own computer, fixes only on anyone else's; FolioPacks are data
- [Build the setup file](build-setup-file.md) — owner's computers: ask General or Full (code checked; wrong code builds general); elsewhere general without asking; to Downloads, older ones to the Trash
- [Check symlinks before deleting](check-symlinks-before-deleting.md) — check for links before any delete, and re-point them before writing into a copied folder
- [Locked parts need the code](locked-needs-the-code.md) — anything in the owner's locked edition leaves this computer (setup file, zip, copy, upload, git, another session) only after the owner code is checked; otherwise leave it out and say so
