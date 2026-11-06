Instructions for Claude: this file comes with Claude-setup-pack-*.zip, a ready-made Claude Code setup pack. If the user sends the two files with "install this", "set this up", or anything like it (or no words at all), treat that as a request to do every step below, in order, without waiting to be told each one. Stop only where a step says to ask the user, or where only they can act (a password, a click, a choice).

The pack sets up this computer, macOS or Windows, for video and motion-graphics work with Claude Code: global rules and house notes, a hook that blocks cloud (ElevenLabs) transcription, a set of skills (markroom, logo-recreation, animation, cutout, chat-archive, local-transcribe, the hyperframes family, media-use, motion-graphics, motion-broll, object-separation, the explainer skills, sound-effects, the optional higgsfield skills, the UI and UX design skills), video-use, a shared cut-out tool, Parakeet for local transcription, the free Fetch MCP for reading web pages, and three optional tools by the pack's author: MarkRoom (a review board skill), PulseWise (a progress bar under the chat's task list) and Folio (keeps long chats light and can carry a chat's work into a new chat), the last two being mods for the Claude desktop app. A zip setup file carries the tools; the git edition carries none and installs the ones the user picks from GitHub. Everything is installed machine-wide, so it works in any folder and any project. Nothing is tied to a project folder, so don't ask for one. If this computer already has an older version of this setup, update it: the install clears the older version's installs itself (retired skills, renamed notes and mods, older setup zips go to a backup folder, nothing is deleted for good), and the cleanup step clears the old duplicates.

Owner code: if the user's message also holds a code (one word starting with `!`), open it first, right after unzipping (step 1) and before anything else: run `sync.py unlock --owner-code '<code>'` from the unzipped folder with any Python 3 on this computer (on a Windows PC with no Python yet, right after the bootstrap). Use the code exactly as written, same capitals, in single quotes, and pass it the same way to every later sync.py command (install, cleanup and check). Never change, guess or ask for a code, and don't repeat it in your messages. If sync.py prints "Owner's own edition: unlocked.", read OWNER.md in the unzipped folder at once and follow it along with these steps; it starts with what to say first. If it prints "General pack.", or the message holds no code, carry on with the general pack and say nothing about codes.

Steps:
1. Unzip the zip into a short temporary folder: ~/Downloads/claude-setup (on Windows %USERPROFILE%\Downloads\claude-setup). If you can't open the attachment as a file, look for Claude-setup-pack-*.zip in Downloads. Read SETUP.md in it fully before doing anything else; it is the detailed step list, and it says which Python command to use (`python3.12` on a Mac, `py -3.12` on Windows).
2. Run the bootstrap script for this system from the unzipped folder, before anything else:
   - Mac: `bash bootstrap-mac.sh`. It checks for Homebrew first.
   - Windows: `powershell -ExecutionPolicy Bypass -File bootstrap-windows.ps1`. It checks for winget first.
   - If the package manager is missing, give the user the exact steps the script prints (they type their own password or click the prompts), wait until they say done, then run it again.
   - If any tools are missing (Python 3.12, ffmpeg, node, uv, yt-dlp, Chrome, ...), tell the user which, then install them with the same script (`--install` on a Mac, `-Install` on Windows). If something needs their password or a click, give them the steps.
   - If it prints a Bonjour note (Windows), pass it on to the user as written: the commands are theirs to run, as administrator, if they want to. It doesn't stop anything.
   - Carry on only when it says READY.
3. Ask the user which languages this computer should transcribe: English only (about 640 MB), or English + other languages such as Hindi (about 3 GB more). In the same message, ask whether they want the optional Higgsfield skills (8 skills for images, videos, brand kits, product shots, thumbnails and sites; they need their own Higgsfield account).
4. Tell the user how big the downloads are and how long they'll take, then run `sync.py install --cutout-env --parakeet --transcription english --higgsfield no` (or `multilingual` and `--higgsfield yes`, as they chose) with this system's Python, in the background. It also clears the older version's installs (SETUP.md step 4). Then run `sync.py tools` ("The three tools" in SETUP.md). If it says this setup file installs them from GitHub, ask the user one question that allows several answers: which of Folio, PulseWise and MarkRoom to install (none is fine); then run `sync.py tools --install <their picks, comma-separated>`. If the `claude` command isn't available it prints lines for the user to type in a chat: give them those. If a tool's folder here has the user's changes, it isn't replaced: ask whether to keep it or set it aside (then `--set-aside`). On the owner's edition, and when the setup file carries the tools, there is nothing to ask.
5. Run `sync.py cleanup` and show the user what it lists (the older version's untouched installs are already cleared). `move` and `tool` items are the pack's own leftovers, unchanged: remove them with `--yes` only after the user says yes. `ask` items are the user's own files or ones they changed: `--yes` never touches them; move one only if the user says yes to that one, with `--move "<path>"` (to the backup, never deleted). An update never undoes the user's changes: `install` lists under "KEPT AS YOU HAD IT" each file it left as they had it and where the pack's new version went; offer to merge any of them.
6. Run `sync.py check` until it says IN SYNC, then do the test cut-out and the test transcription from SETUP.md. In the report, only say whether each passed.
7. Check that the watch plugin shows up (watch:watch in your skills). If it doesn't, give the user the two commands from SETUP.md to install it (it's free and works on any account). Once it's there, set it up as SETUP.md describes: local engine, WhisperX small, balanced detail, no API keys.
8. Read "Claude accounts" in SETUP.md and tell the user which account-side things they may want to set up themselves (plugins, connectors, review boards). With the owner's edition only (skip it on a general install), ask whether to install the Unfold text presets into After Effects; on yes, give them the steps from SETUP.md step 8 (on a Mac a `sudo` command they run in Terminal with After Effects closed, after giving Terminal App Management; on Windows a folder they copy by hand, as there is no installer script). Then the two sound tools ("Sound tools" in SETUP.md): point real-sfx at a sound library with its setup command, and ask before installing earshot's tool (about 2.4 GB).
9. Briefly tell the user the house rules (4K delivery, motion rules, working rules) so they can say which apply to them, and record their answer as SETUP.md step 7 describes.
10. If no owner code was accepted, run `sync.py strip-owner --zip "<the setup zip's path>"` (it takes the pack's locked part out of the zip and the folder; skip the `--zip` part if you can't find the zip as a file). Delete the temporary unzip folder. Then end with this report, filled in, and write nothing after it. Print it as Markdown, laid out as it stands (headings, lists, the skills table), not inside a code block. It names no one except Zoke. Keep every description as written; fill in only the <...> parts (a skill's status is installed, updated or unchanged), and leave out the Whisper line if English only was chosen. Leave out the markroom row and the part of "How MarkRoom, PulseWise and Folio work" for any of the three tools that isn't installed (the whole section when none is), and keep the "From GitHub" section only when the tools were installed from GitHub:

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
| hyperframes (9 skills) | <status> | Makes, animates and renders videos from code. |
| media-use | <status> | Finds music, sound effects, images, icons and voices for a video. |
| motion-graphics | <status> | Short animations such as kinetic type, charts, maps and logo stings. |
| motion-broll | <status> | Animated B-roll timed to what the speaker says. |
| object-separation | <status> | Separates a person or object from the background in a video. |
| explainers (3 skills) | <status> | Three styles of product explainer video. |
| higgsfield (8 skills, optional) | <installed, updated, unchanged or not installed (you said no)> | Makes images, videos, brand kits, product shots, thumbnails and sites with a Higgsfield account. |
| UI and UX design (13 skills) | <status> | Design guidance and usability, accessibility and UX reviews for pages and apps. |
| sound-effects | <status> | Adds measured sound effects and music to a finished animation. |
| video-use | <status> | Edits raw footage by conversation: cuts, colour grade, subtitles. |

### Tools

- **Cut-out tool:** the BiRefNet HR model in a shared Python setup, used by cutout and markroom; set for this computer by the machine check (<device, memory: full or half precision at its working size>).
- **Parakeet:** local speech-to-text for English and 24 other European languages.
- **Whisper large-v3** (if chosen): local speech-to-text for Hindi and every other language.
- **Fetch MCP:** reads web pages for Claude, word for word; free and local.
- **ElevenLabs block:** a safety hook that stops any transcription from being sent to ElevenLabs.
- **Unfold presets** (owner's edition only; leave this line out on a general install): <installed in After Effects | not installed; they wait in ~/.claude/ae-presets/unfold>. 90 text animation presets for After Effects.
- **Setup builder:** `~/.claude/setup-pack` makes this computer's own setup file whenever you ask Claude for one; it goes to your Downloads.

### How MarkRoom, PulseWise and Folio work

**MarkRoom** (a skill: ask for a review page, or say "open the dashboard")

- Claude publishes a private review board with a tab for each still or video. Rounds of the same thing stay in one tab, with a Version menu for the older ones.
- Stills pan and zoom. Videos play, step frame by frame and go full screen, and every note is pinned to a timecode or a range.
- You draw markers, arrows, boxes, freehand lines and text, gather as many marks as a point needs into one numbered note, and write its comment; pictures can be pasted into a note. A whole-image or whole-video note covers the overall feel.
- Claude reads every note, the overall ones included, makes the changes, then replies to each note and closes it.

**PulseWise** (a mod: new chats in the Claude desktop app)

- A band above the prompt box shows the chat's task list as one bar, a segment per point sized by its time, filling as the work runs. The line above it names what is running, the total % and the time left.
- Click a segment to open its own bar. Background jobs (renders, agents, scripts) each get a bar under Tracks, and long scripts report real counts through `~/.claude/progress/progress.py`.
- Other pulses shows the other chats open in the same project, marked "needs input" in amber when one is waiting on you. Done lists what finished and how long it took, and Nudge reminds Claude to bring its task list up to date.
- It runs by itself and uses no Claude usage while it runs.

**Folio** (a mod: new chats in the Claude desktop app, Claude Code 2.1.308 or newer)

- Folio keeps long chats small. It splits the chat into chunks and writes a short summary of each in the background, on Haiku, which counts toward your own Claude usage (a small amount, but not zero).
- Folding swaps the oldest chunks for their summaries. The newest work stays word for word, and so does any chunk you mark Keep. Nothing is lost: Claude fetches any folded chunk word for word with its recall tool, and you can undo a fold from the Activity list.
- It starts in **Watch**: it shows what would fold and folds only when you press **Fold now**. **Automatic** folds by itself as the chat nears its ceiling, and Strategy (Light, Balanced, Lean) sets how big the chat may grow first.
- Open its panel from the Folio button in the footer or with `/folio`. It shows what fills the context, the chunks, the brief (rules, decisions, terms, files, open tasks) and recent activity. The footer count turns amber while chunks are due to fold and red past the ceiling.
- **FolioPacks** carry a chat's work, or a whole project's, to a new chat or another computer. Pack up writes the summaries, brief and originals into a zip, saved to `~/FolioPacks` or a folder or drive you choose in Saves to; big project files can go in a separate FolioFiles zip, and private items (keys, passwords, numbers) are never packed. To bring a pack in, drop the zip into a new chat opened in the project folder; Folio brings back the summaries and the brief, and recall works on every original.

### From GitHub

Installed: <the tools installed from GitHub, or none>.

- **Update one:** `claude plugin update <tool>@zoke` in a terminal, then open a new chat.
- **What they need:** MarkRoom: Node, Python 3.10+ with Pillow, ffmpeg, and a claude.ai account whose artifacts allow a database, comments and file uploads. Folio: Claude Code 2.1.308 or newer; its summaries use Haiku, on your own usage. PulseWise and Folio: the Claude desktop app.
- **Open a new chat** so they load.

*Setup pack put together by Zoke.*
