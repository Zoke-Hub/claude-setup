Instructions for Claude: this is the setup prompt of the Claude setup pack on GitHub (https://github.com/@@REPO@@), a ready-made Claude Code setup. If the user sends this file, its link or the repository's link with "install this", "set this up", or anything like it (or no words at all), treat that as a request to do every step below, in order, without waiting to be told each one. Stop only where a step says to ask the user, or where only they can act (a password, a click, a choice).

The pack sets up this computer, macOS or Windows, for video and motion-graphics work with Claude Code: global rules and house notes, a hook that blocks cloud (ElevenLabs) transcription, a set of skills (logo-recreation, animation, cutout, chat-archive, local-transcribe, earshot, the hyperframes family, media-use, motion-graphics, motion-broll, object-separation, the explainer skills, sound-effects, real-sfx, the optional Higgsfield skills, the UI and UX design skills), video-use, a shared cut-out tool, Parakeet for local transcription, the free Fetch MCP for reading web pages, and three optional tools by the pack's author, installed from https://github.com/@@TOOL_REPO@@: MarkRoom (a review board skill), PulseWise (a progress bar under the chat's task list) and Folio (keeps long chats light and can carry a chat's work into a new chat), the last two being mods for the Claude desktop app. Some third-party skills aren't in the repository: the install downloads real-sfx, HeyGen's current hyperframes skills and media-use, and (if the user wants them) the Higgsfield skills from their makers' own repositories, at the version this pack was checked with. Everything is installed machine-wide, so it works in any folder and any project. Nothing is tied to a project folder, so don't ask for one. If this computer already has an older version of this setup, update it: the install clears the older version's installs itself (retired skills, renamed notes and mods go to a backup folder, nothing is deleted for good), and the cleanup step clears the old duplicates.

Steps:
1. Download the pack into a short temporary folder and unpack it, with these commands (no git or Python needed yet; Windows 10 and 11 have curl and tar built in):
   - Mac: `mkdir -p ~/Downloads/claude-setup && cd ~/Downloads/claude-setup && curl -fsSL -o pack.zip https://github.com/@@REPO@@/archive/refs/heads/main.zip && unzip -q -o pack.zip`
   - Windows (PowerShell): `New-Item -ItemType Directory -Force "$env:USERPROFILE\Downloads\claude-setup" | Out-Null; Set-Location "$env:USERPROFILE\Downloads\claude-setup"; curl.exe -fsSL -o pack.zip https://github.com/@@REPO@@/archive/refs/heads/main.zip; tar -xf pack.zip`
   On Windows, if Apple's Bonjour is on this computer, a "Local Security Authority" pop-up may come up once during this download (Windows blocking Bonjour's name-lookup add-in). It's harmless and nothing setup needs is blocked: tell the user they can close it; the bootstrap in step 3 says how to stop it for good.
   The pack is then in the `claude-setup-main` folder inside it: run every later command from there. Read SETUP.md in it fully before doing anything else; it is the detailed step list, and it says which Python command to use (`python3.12` on a Mac, `py -3.12` on Windows). Its parts about owner codes, zips and `strip-owner` don't apply to this pack: skip them.
2. Check whether this computer has the setup pack already: look for `installed.json` in `~/.claude/setup-pack/` (the same folder under the user's home on Windows).
   - **Not there:** this is a first install. Do every step below.
   - **There:** this is an update. Run `sync.py news` with this system's Python and tell the user in a few lines what this setup file changes: its "What's new" entries and the files it would change. The version number can be the same as the one installed (each build has its own stamp), so go by what `news` says, not the number. Then do only what the update needs:
     - Step 3: run the bootstrap; it installs only tools that are missing.
     - Step 4: don't ask again. `install` keeps this computer's transcription languages and Higgsfield choice when those flags are left out; ask only if the user wants to change one. Ask about earshot only if `news` lists a change to it and its tool isn't installed.
     - Step 5: run `sync.py install` without `--transcription` and `--higgsfield`; add `--cutout-env` or `--parakeet` only if `sync.py check` reports the cut-out tool or Parakeet missing. It writes only the files that are new or changed, keeps the user's own changes, and says what it updated. Then run `sync.py tools` and update the tools that are already installed (offer the others only if the user asks).
     - Steps 6 and 7: as written. Run the test cut-out or test transcription only if `news` lists a change to the cutout or local-transcribe skill or the cut-out tool.
     - Steps 8 to 10: skip them, unless `news` lists a change to one of them or `sync.py check` says something there isn't set up yet.
     - Step 11: delete the temporary folder, then end with the update report at the end of this prompt instead of the full report.
3. Run the bootstrap script for this system from the pack folder, before anything else:
   - Mac: `bash bootstrap-mac.sh`. It checks for Homebrew first.
   - Windows: `powershell -ExecutionPolicy Bypass -File bootstrap-windows.ps1`. It checks for winget first.
   - If the package manager is missing, give the user the exact steps the script prints (they type their own password or click the prompts), wait until they say done, then run it again.
   - If any tools are missing (Python 3.12, ffmpeg, node, uv, yt-dlp, Chrome, ...), tell the user which, then install them with the same script (`--install` on a Mac, `-Install` on Windows). If something needs their password or a click, give them the steps.
   - If it prints a Bonjour note (Windows), pass it on to the user as written: the commands are theirs to run, as administrator, if they want to. It doesn't stop anything.
   - Carry on only when it says READY.
4. Ask the user which languages this computer should transcribe: English only (about 640 MB), or English + other languages such as Hindi (about 3 GB more). In the same message, ask whether they want the optional Higgsfield skills (@@HIGGSFIELD_COUNT@@ skills for images, videos, brand kits, product shots, thumbnails and sites, downloaded from Higgsfield's own repository; they need their own Higgsfield account), and whether to install earshot's listening tool for the earshot skill (about 2.4 GB).
5. Tell the user how big the downloads are and how long they'll take, then run `sync.py install --cutout-env --parakeet --transcription english --higgsfield no` (or `multilingual` and `--higgsfield yes`, as they chose) with this system's Python, in the background. It downloads the third-party skills first and checks every file; if one of those downloads fails, it says which and installs everything else (run install again later for it). It also clears the older version's installs (SETUP.md step 4). Then run `sync.py tools` ("The three tools" in SETUP.md) and ask the user one question that allows several answers: which of Folio, PulseWise and MarkRoom to install (none is fine); then run `sync.py tools --install <their picks, comma-separated>`. If the `claude` command isn't available it prints lines for the user to type in a chat: give them those. If a tool's folder here has the user's changes, it isn't replaced: ask whether to keep it or set it aside (then `--set-aside`).
6. Run `sync.py cleanup` and show the user what it lists (the older version's untouched installs are already cleared). `move` and `tool` items are the pack's own leftovers, unchanged: remove them with `--yes` only after the user says yes. `ask` items are the user's own files or ones they changed: `--yes` never touches them; move one only if the user says yes to that one, with `--move "<path>"` (to the backup, never deleted). An update never undoes the user's changes: `install` lists under "KEPT AS YOU HAD IT" each file it left as they had it and where the pack's new version went; offer to merge any of them.
7. Run `sync.py check` until it says IN SYNC, then do the test cut-out (on the pack's own `extras/cutout-test.jpg`, a CC0 museum photo) and the test transcription from SETUP.md. In the report, only say whether each passed.
8. Check that the watch plugin shows up (watch:watch in your skills). If it doesn't, give the user the two commands from SETUP.md to install it (it's free and works on any account). Once it's there, set it up as SETUP.md describes: local engine, WhisperX small, balanced detail, no API keys. If its WhisperX warm-up fails on Windows with a symlink error, use the fallback in SETUP.md.
9. Read "Claude accounts" in SETUP.md and tell the user which account-side things they may want to set up themselves (plugins, connectors, review boards). Then the two sound tools ("Sound tools" in SETUP.md): point real-sfx at the sound-effects skill's own library (`~/.claude/skills/sound-effects/sfx`) with its setup command, without asking (if the user says they have a sound library of their own, use that one instead), and, if the user said yes to earshot in step 4, run `sync.py earshot` in the background: it installs earshot's tool at the version this pack was checked with and runs earshot's own checks. If running it is refused (a safety check can block installing a third-party repository), give the user that one command to run themselves, from the pack folder.
10. Briefly tell the user the house rules (4K delivery, motion rules, working rules) so they can say which apply to them, and record their answer as SETUP.md step 7 describes.
11. Delete the temporary `claude-setup` folder in Downloads (the zip and the unpacked pack). Then end with this report, filled in, and write nothing after it. Print it as Markdown, laid out as it stands (headings, lists, the skills table), not inside a code block. Keep every description as written; fill in only the <...> parts (a skill's status is installed, updated or unchanged), and leave out the Whisper line if English only was chosen. Leave out the markroom row and the part of "How MarkRoom, PulseWise and Folio work" for any of the three tools that isn't installed (the whole section when none is), and the "From GitHub" section when none of them is:

## Setup complete

Setup pack <version>

- **For you to do:** <items, e.g. install the watch plugin (lets Claude watch videos), or nothing>
- **Check:** <IN SYNC, or what's left>
- **Kept as you had it:** <the files the update left as you'd changed them, with where the pack's new versions are (~/.claude/setup-pack/updates/), or nothing>
- **Tests:** cut-out <passed | failed>, transcription <passed | failed>. Quick checks that the cut-out tool and local transcription work on this computer.
- **Transcription:** <English only | English + other languages>. Speech in videos is turned into text on this computer; nothing is uploaded.
- **Removed:** <old duplicates that were cleared, or nothing>
- **Backed up:** <the backup folder, or nothing needed>

### Rules

In `~/.claude/CLAUDE.md`: instructions Claude follows in every session.

- **No cloud transcription:** speech is never sent to ElevenLabs; a safety hook enforces it.
- **Video skill routing:** the house rules beat other skills' defaults; real recorded sound only; HyperFrames by default.
- **How to work:** questions and still previews before building, only the script lines you send (read in context), approve images first (every pick sheet posted in the MarkRoom), verify facts, keep every render and dated handoff notes, symlinks checked before deleting, 4K delivery, cut-outs, cut-out characters and their pieces sheets, logos, review boards, references and your own finished edits studied for motion and your changes, After Effects projects delivered with their assets collected, the author's tools (MarkRoom, PulseWise, Folio, logo-recreation, animation) only fixed, never reworked, maps of India, no assumptions about you, rules kept general, clear communication (independent steps in parallel, within a job too, work kept in its own chat, reply buttons that are whole answers), long jobs shown on the progress bar, and a stuck step raised in 1–2 minutes rather than waited on.
- **Reading web pages:** the free Fetch MCP reads pages word for word; web search finds them.
- **<macOS | Windows> notes:** the Python, ffmpeg and transcription commands that work on this computer.

### House notes

In `~/.claude/house`: the detail behind the rules, read when relevant.

- **4K delivery:** deliver 3840x2160 at 25 fps, review rounds at 1080p, 4K renders only when asked.
- **Motion rules:** titles unfold word by word, paragraphs line by line, photos and pieces slide in on a strong ease-out, lines draw on, tight camera framing, a curve picked for each move, beats timed to the voiceover, the animation flowing on across frame changes, spacing by groups, sentence subtitles held at least 1 second.
- **Working rules:** how to plan, source, check, review, archive and hand over work.

### Skills

In `~/.claude/skills`: abilities Claude loads when a task needs them.

| Skill | Status | What it does |
|---|---|---|
| markroom | <status> | A review board for stills and videos; you draw on frames and leave notes (pictures too), Claude answers them. |
| logo-recreation | <status> | Rebuilds a blurry logo as a clean SVG and PNG by measuring it, with real text. |
| cutout | <status> | Cuts an object or person out of a photo at full resolution, as a transparent PNG. |
| chat-archive | <status> | Saves a whole chat as a readable web page you can keep. |
| local-transcribe | <status> | Turns speech in a video into a word-timed transcript, on this computer. |
| animation | <status> | The house rules for every animation: how things move and are timed, cut-out puppets, and clean, editable After Effects projects. |
| hyperframes (9 skills) | <status> | Makes, animates and renders videos from code. The current ones come from HeyGen; the six HeyGen retired are kept. |
| media-use | <status> | Finds music, sound effects, images, icons and voices for a video. From HeyGen. |
| motion-graphics | <status> | Short animations such as kinetic type, charts, maps and logo stings. |
| motion-broll | <status> | Animated B-roll timed to what the speaker says. |
| object-separation | <status> | Separates a person or object from the background in a video. |
| explainers (3 skills) | <status> | Three styles of product explainer video. |
| higgsfield (@@HIGGSFIELD_COUNT@@ skills, optional) | <installed, updated, unchanged or not installed (you said no)> | Makes images, videos, brand kits, product shots, thumbnails and sites with a Higgsfield account. From Higgsfield. |
| UI and UX design (13 skills) | <status> | Design guidance and usability, accessibility and UX reviews for pages and apps. |
| sound-effects | <status> | Adds measured sound effects and music to a finished animation. |
| real-sfx | <status> | Places real recorded sound effects from a sound library on the exact frame. From Clipwing. |
| earshot | <status; its tool installed or not> | Listens for Claude: describes, ranks and checks sounds, and reads a render's sound. |
| video-use | <status> | Edits raw footage by conversation: cuts, colour grade, subtitles. |

### Tools

- **Cut-out tool:** the BiRefNet HR model in a shared Python setup, used by cutout and markroom; set for this computer by the machine check (<device, memory: full or half precision at its working size>).
- **Parakeet:** local speech-to-text for English and 24 other European languages.
- **Whisper large-v3** (if chosen): local speech-to-text for Hindi and every other language.
- **Fetch MCP:** reads web pages for Claude, word for word; free and local.
- **ElevenLabs block:** a safety hook that stops any transcription from being sent to ElevenLabs.
- **Setup builder:** `~/.claude/setup-pack` makes this computer's own setup file whenever you ask Claude for one; it goes to your Downloads.

### How MarkRoom, PulseWise and Folio work

**MarkRoom** (a skill: ask for a review page, or say "open the dashboard")

- Claude publishes a private review board with a tab for each still or video. Rounds of the same thing stay in one tab, with a Version menu for the older ones.
- Stills pan and zoom. Videos play, step frame by frame and go full screen, and every note is pinned to a timecode or a range.
- You draw markers, arrows, boxes, freehand lines and text, gather as many marks as a point needs into one numbered note, and write its comment; pictures can be pasted into a note. A whole-image or whole-video note covers the overall feel.
- Claude reads every note, the overall ones included, makes the changes, then replies to each note and closes it.
- Whenever Claude changes something in the MarkRoom, its message links straight to the file that changed.

**PulseWise** (a mod: new chats in the Claude desktop app)

- A band above the prompt box shows the chat's task list as one bar, a segment per point sized by its time, filling as the work runs. The line above it names what is running, the total % and the time left.
- Click a segment to open its own bar. Background jobs (renders, agents, scripts) each get a bar under Tracks, and long scripts report real counts through `~/.claude/progress/progress.py`.
- Other pulses shows the other chats open in the same project, marked "needs input" in amber when one is waiting on you. Done lists what finished and how long it took, and Nudge reminds Claude to bring its task list up to date.
- On Windows, when a long job or the whole list finishes while the Claude app is behind other windows, its taskbar button flashes until you come back.
- It runs by itself and uses no Claude usage while it runs.

**Folio** (a mod: new chats in the Claude desktop app, Claude Code 2.1.308 or newer)

- Folio keeps long chats small. It splits the chat into chunks and writes a short summary of each in the background, on Haiku, which counts toward your own Claude usage (a small amount, but not zero).
- Folding swaps the oldest chunks for their summaries. The newest work stays word for word, and so does any chunk you mark Keep. Nothing is lost: Claude fetches any folded chunk word for word with its recall tool, and you can undo a fold from the Activity list.
- It starts in **Watch**: it shows what would fold and folds only when you press **Fold now**. **Automatic** folds by itself as the chat nears its ceiling, and Strategy (Light, Balanced, Lean) sets how big the chat may grow first.
- Open its panel from the Folio button in the footer or with `/folio`. It shows what fills the context, the chunks, the brief (rules, decisions, terms, files, open tasks) and recent activity. The footer count turns amber while chunks are due to fold and red past the ceiling.
- **FolioPacks** carry a chat's work, or a whole project's, to a new chat or another computer. Pack up writes the summaries, brief and originals into a zip, saved to `~/FolioPacks` or a folder or drive you choose in Saves to; big project files can go in a separate FolioFiles zip, and private items (keys, passwords, numbers) are never packed. To bring a pack in, drop the zip into a new chat opened in the project folder; Folio brings back the summaries and the brief, and recall works on every original.

### From GitHub

Installed: <the tools installed from GitHub>.

- **Update one:** `claude plugin update <tool>@@@MARKETPLACE@@` in a terminal, then open a new chat.
- **What they need:** MarkRoom: Node, Python 3.10+ with Pillow, ffmpeg, and a claude.ai account whose artifacts allow a database, comments and file uploads. Folio: Claude Code 2.1.308 or newer; its summaries use Haiku, on your own usage. PulseWise and Folio: the Claude desktop app.
- **Open a new chat** so they load.

*Setup pack put together by Zoke.*

---

The update report (step 2, an update), filled in the same way:

## Setup updated

Setup pack <version>, build <this build> (was build <the build installed before, or "an earlier build">)

- **What's new:** <the "What's new" entries `news` listed, one line each, or nothing new in this build>
- **Changed here:** <the files the install wrote, by area (for example 3 skills updated: animation, markroom, cutout; 2 house notes), or nothing>
- **Kept as you had it:** <the files the update left as you'd changed them, with where the pack's new versions are (~/.claude/setup-pack/updates/), or nothing>
- **Check:** <IN SYNC, or what's left>
- **Backed up:** <the backup folder, or nothing needed>

*Setup pack put together by Zoke.*
