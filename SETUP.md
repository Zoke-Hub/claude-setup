# Claude setup pack — read this first

**Instructions for Claude:** if the user sends this zip with "install this" or anything like it ("set this up", "run
this", no words at all), treat it as a request to do every step below, in order, on this computer. Don't wait to be
told each step. Stop only where a step says to ask the user or where only they can act (a password, a click, a choice).

This pack gives a computer a ready-made Claude Code setup for video and motion-graphics work: global rules and house
notes, a hook that blocks cloud (ElevenLabs) transcription, a set of skills and the local tools behind them.
**Everything is machine-wide (`~/.claude`, the system package manager, model caches). Nothing is tied to a project
folder**, so it works in any folder and any project. `sync.py` does the copying and checking; this file is the step
list. It sets up a new computer and also updates one that has an older version of this pack.

## Steps (in order)

The pack works on **macOS and Windows**. Below, `PY` means the Python 3.12 command for this computer: `python3.12` on a
Mac (macOS's own `python3` is 3.9), `py -3.12` on Windows (or `python` if that is 3.10+).

1. **Unzip** the pack to a short path, `~/Downloads/claude-setup` (on Windows `%USERPROFILE%\Downloads\claude-setup`),
   and `cd` into it (the folder with `bootstrap-mac.sh`, `bootstrap-windows.ps1`, `sync.py`, `MANIFEST.json`,
   `SETUP.md`). A long path can break `git` on Windows. The folder is only needed during setup; delete it at the end.
   Don't ask the user for a project folder: none is needed.
2. **The package manager first, then the tools.** Run the bootstrap for this OS (neither needs Python):
   - **macOS:** `bash bootstrap-mac.sh`. It checks, in this order:
     - **Homebrew.** If missing, it stops with exit code 2 and prints the steps for the user: open Terminal, paste
       the Homebrew install line, type their password, run the two "Next steps" lines. Give the user those steps
       word for word, wait until they say it's done, then run the script again. Never type their password.
     - Apple's command-line tools. Homebrew installs them; if they're missing, the user runs `xcode-select --install`.
     - git, node + npx, python3.12, uv, jq, ffmpeg + ffprobe, ffmpeg-full (with drawtext + subtitles), yt-dlp (+ deno)
       and Google Chrome.
     If anything is missing (exit code 1), tell the user what and why, then run `bash bootstrap-mac.sh --install`.
   - **Windows:** `powershell -ExecutionPolicy Bypass -File bootstrap-windows.ps1`. It checks, in this order:
     - **winget.** If missing, it stops with exit code 2 and prints the steps for the user (Microsoft Store → App
       Installer). Give them word for word, wait until they say it's done, then run the script again.
     - git (with Git Bash), Python 3.12, node + npx, uv + uvx, a full ffmpeg build (drawtext + subtitles), yt-dlp,
       deno and Google Chrome.
     If anything is missing (exit code 1), tell the user what and why, then run it again with `-Install`. Windows may
     show a permission prompt for some installers: tell the user to click Yes. If PATH changes don't show up, open a
     new PowerShell window and run the check again.
     - **A Bonjour note** appears where Bonjour's name-lookup add-in (`mdnsNSP.dll`) is installed and LSA protection is
       on: some downloads can then bring up a "Local Security Authority" pop-up. Setup's own downloads avoid it (git
       uses OpenSSL on Windows). Pass the note on as written: the two `regsvr32 /u` lines are the user's to run, as
       administrator, if they want to; never run them yourself, and never suggest turning LSA protection off.
   Both install with the system's package manager, then check again. Carry on only once the script prints **READY**.
3. **Ask the user which languages this computer should transcribe**, before installing:
   - **English only** — Parakeet TDT 0.6B v3 (English and 24 other European languages), about 640 MB. Fast and the
     most accurate local engine for those languages.
   - **English + other languages** — also Whisper large-v3 for Hindi, Tamil, Japanese and every other language, about
     3 GB more and slower on a CPU.
   They can switch later (`sync.py install --transcription english|multilingual`).
   In the same message, ask whether they want the **optional Higgsfield skills** (8 skills that make images, videos,
   brand kits, product shots, thumbnails and sites; they need the user's own Higgsfield account, and the skill installs
   the Higgsfield CLI and asks them to log in when first used). On yes add `--higgsfield yes` to the install below, on no
   `--higgsfield no`. Where they are already installed, an update without the flag keeps them up to date; on no they
   are left as they are, not removed.
4. **Install.** Tell the user first how much this downloads (cut-out venv ~850 MB, or ~3 GB with CUDA torch on a
   Windows PC with an NVIDIA GPU; BiRefNet HR ~450 MB; Parakeet ~640 MB; Whisper large-v3 ~3 GB if they chose more
   languages; video-use's venv) and that it takes 10–40 minutes; run it in the background:
   `PY sync.py install --cutout-env --parakeet --transcription english --higgsfield no` (or `--transcription multilingual`,
   `--higgsfield yes`, as they chose)
   If the user gave an owner code, add `--owner-code '<code>'` to this and every later `sync.py` command (see "Owner
   code" below).
   **The git edition** (the pack from GitHub) doesn't carry every third-party skill: its MANIFEST "downloads" lists the
   ones `install` fetches first from their makers' repositories (real-sfx, HeyGen's current hyperframes skills and
   media-use, and the Higgsfield skills on a yes), each at the commit the pack was built with. It checks every file
   against MANIFEST, then installs them like the pack's own files. A failed download is named in the output and the
   rest installs; run `install` again later for it.
   It merges the rules into `~/.claude/CLAUDE.md` and adds this OS's own sections (transcription routing, machine
   notes) plus a `# Transcription languages` section for the user's choice, installs the house notes in
   `~/.claude/house/`, registers the ElevenLabs block hook (the bash version on a Mac, the Python version on Windows),
   installs every skill (backing up anything it replaces), clones video-use and applies its path patch, builds the
   shared cut-out venv `~/.claude/venvs/cutout` (CUDA torch automatically where there's an NVIDIA GPU) and runs the
   cut-out **machine check**: it measures this computer's GPU memory (or RAM on Apple silicon and CPUs), picks the
   cut-out precision and working size that fit (full precision only with plenty of memory, otherwise half precision,
   with a GPU memory cap on Apple silicon so a cut-out can never freeze the computer), saves them in the venv's
   `machine.json` and writes them as this machine's `# Cut-out settings` section of `~/.claude/CLAUDE.md`; installs
   Parakeet (and Whisper large-v3 for more languages), registers the **Fetch MCP** (a free, local web-page
   reader; it loads in new sessions), and, when this setup file carries them (a zip setup file; see "The three tools"), installs **PulseWise**, the progress bar under the chat's task list: the mod in
   `~/.claude/mods/pulsewise` (loaded in every chat of the Claude desktop app through two `env` lines in
   `~/.claude/settings.json`, plus a `local-mods` marketplace entry; it appears in new chats) and its helper
   `~/.claude/progress/progress.py`, which long scripts report their counts through; and **Folio**, which keeps long
   chats light by folding their older parts into an archive in a side panel that Claude can still look things up in,
   and packs a chat's study, rules and decisions into a FolioPack zip for starting the same work in a new chat on any
   computer (the mod in `~/.claude/mods/folio`, loaded the same way: its folder is added to the same `env` line, and the
   marketplace lists it too). Folio was built and tested on Claude Code 2.1.308 and may not load on an older version;
   its summaries and look-ups run on Haiku, on the user's own Claude usage; it starts in Watch mode. `local-transcribe` is only installed where it is missing (a computer keeps its
   own copy). With the owner's edition only, it also copies the **Unfold** text presets for After Effects to
   `~/.claude/ae-presets/unfold/` (they go into After Effects only on a yes, step 8); a general install moves an older
   general pack's copy of that folder to the backup. **It clears the older version's installs itself**, so nothing old is
   left behind: retired skills (review-dashboard; redline, now markroom; animation-easing, after-effects-translation and
   puppet-rig, now merged into animation; aroll-zooms-and-cuts, retired), mods and house notes an older pack
   installed under an old name, and older setup zips in Downloads / Desktop go to `~/.claude/sync-backups/<time>/cleanup/`;
   house notes this pack no longer ships go to `~/.claude/house-private/`. Nothing is deleted for good. The house notes
   that moved into the animation skill are replaced by short pointers to it.
5. **Old duplicates.** The older version's installs are already cleared by `install` (step 4). Then run
   `PY sync.py cleanup` for what's left: old copies of skills ("markroom copy", "markroom-old", folders with no
   SKILL.md), project memory notes that are now house notes, unused model caches (BiRefNet HR-matting, hyperframes
   remove-background), a hook registered twice, an old PowerShell port of the hook. If the user names an old project
   folder, add `--project "<folder>"` to also catch its leftovers (an old `.cutout` venv, old cut-out tool copies,
   exported skill zips). Show the user the list and ask. `move`, `tool` and `private` items are the pack's own
   leftovers, unchanged since a setup file installed them: only on the user's yes, run it again with `--yes` (moves go
   to `~/.claude/sync-backups/<time>/cleanup/`, re-downloadable caches are deleted). `ask` items are the user's own
   files, or pack files they changed: `--yes` never touches them; move one only on the user's yes to that one, with
   `--move "<path>"` (to the backup, never deleted). `[report]` items are left for you to sort out by hand with the user.
6. **Check.** `PY sync.py check` must end with **IN SYNC**. Fix anything it lists, then prove the local tools:
   - Cut-out: copy the pack's own test photo, `extras/cutout-test.jpg` (CC0: Teapot, Cleveland Museum of Art 1940.228),
     to a temp folder (no need to look for one online), run
     the cut-out venv's Python (`~/.claude/venvs/cutout/bin/python` on a Mac, `~/.claude/venvs/cutout/Scripts/python.exe`
     on Windows) on `~/.claude/skills/cutout/scripts/birefnet_cutout.py <img> <out.png>`, time it, and check the result
     is the same size as the input with clean edges on a plain paper colour. Its last line says the precision and
     working size it used; they should match the machine check (if it had to drop to a smaller size, tell the user).
   - Transcription: make a short spoken test file, `lt-test.wav`, in a temp folder. On a Mac:
     `say -o lt-test.aiff "The parcel weighs ninety five grams."` then `ffmpeg -i lt-test.aiff lt-test.wav`.
     On Windows (PowerShell): `Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer;
     $s.SetOutputToWaveFile("$PWD\lt-test.wav"); $s.Speak("The parcel weighs ninety five grams."); $s.Dispose()`.
     Then `PY ~/.claude/skills/local-transcribe/scripts/local_transcribe.py lt-test.wav` (if more languages were
     chosen, also try `--language en --engine whisper` once). It passes when `edit/transcripts/lt-test.json` holds
     those words. Don't quote the sentence in the report; just say whether it passed.
   Delete only those test files.
7. **The house rules.** Briefly tell the user the house rules this setup follows, so they can say which apply to them:
   **4K delivery** (deliver 3840×2160 at 25 fps, review rounds at 1080p, 4K renders only on request), **motion rules**
   (titles unfold word by word from the baseline, paragraphs line by line, photos and pieces sliding in on a strong ease-out, lines drawn on, a
   curve picked for each move, bar-wipe highlights, beats timed to the voiceover, the animation flowing on across frame changes, spacing by groups, sentence subtitles held at least 1 second) and the **working rules** (questions and
   still previews before building, only the script lines the user sends, read in context, approve images first (every pick sheet posted in the MarkRoom), verify facts on screen, no assumptions about the user from their projects or rules, keep every render and dated handoff notes, symlinks checked before deleting, reference studies cover motion only, the user's own finished edits studied for their changes,
   cut-out characters rigged so they match the drawing at rest, a pieces sheet approved before animating, After
   Effects export only on request and delivered with its assets collected, the author's tools (MarkRoom, PulseWise, Folio,
   logo-recreation, animation) only fixed on this computer, never reworked, motion keyed as authored with AE's own easing on whole frames and no stepped motion,
   letter-by-letter text as one Text Animator, ambient motion as native expressions with Slider Controls, effects made
   with AE's own effects while stills stay stills, the exporter kept current while building, review pages are MarkRoom
   boards whose marks and overall notes are both read every round, independent steps run in parallel, long jobs report
   their progress to the progress bar, a stuck step raised in 1–2 minutes instead of waited on, work kept in the chat it was asked in, reply buttons that are whole answers, keep
   a chat archive, new rules written for every project with nothing from the project they came
   from). Record what they say in a `# Personal (not packed)` section at the end of `~/.claude/CLAUDE.md` (for example
   "4K delivery doesn't apply here: we deliver 1080p"); that section overrides the house rules on this computer. Don't
   edit the packed rules block or the files in `~/.claude/house/`, so `check` stays IN SYNC.
8. **Things only the user can do** (tell them; you can't from inside a session):
   - The **watch** plugin (lets Claude watch videos). If `watch:watch` isn't in your skills (`check` shows a FOR THE
     USER line), the user installs it — free, from GitHub, works on any Claude account — in a terminal Claude Code
     session (`claude`): `/plugin marketplace add bradautomates/claude-video` then `/plugin install watch@claude-video`,
     then starts a new session. Then set it up: engine local, WhisperX small, detail balanced, no API keys (config
     `~/.config/watch/.env`, run with `PY`); never a cloud transcriber. On Windows its WhisperX warm-up can fail with a
     symlink error (the model download makes links Windows refuses without Developer Mode). Then, with watch's own
     WhisperX Python (its venv under `~/.cache/watch`), download the model's files one at a time into the same cache:
     `from huggingface_hub import hf_hub_download, list_repo_files` and `hf_hub_download(repo, f)` for each `f` in
     `list_repo_files(repo)`, where `repo` is the model the warm-up was fetching (`Systran/faster-whisper-small` for
     WhisperX small). Then run the setup and warm-up again: they find the model already there.
   - Any plugins and claude.ai connectors they want on this account (see below).
   - **The Unfold text presets for After Effects**, with **Blink in / out** (owner's edition only; skip this on a general
     install. 90 text animation presets: words, lines and characters, each IN and OUT; Blink keys a layer's opacity on or
     off). Ask whether to install them. On yes, with After Effects closed:
     - **Mac:** it needs their password, so they run it in Terminal:
       `sudo zsh ~/.claude/ae-presets/unfold/install_presets.sh`. Terminal needs App Management first (System Settings →
       Privacy & Security → App Management → Terminal on). It puts Unfold in every After Effects as Presets/Unfold and
       Blink in / out loose in Presets/, and moves older copies to the Trash.
     - **Windows:** run `powershell -ExecutionPolicy Bypass -File "$HOME\.claude\ae-presets\unfold\install_presets.ps1"`.
       Windows asks the user for administrator permission (a click); the script then does the same in every After Effects
       under `C:\Program Files\Adobe\` (`Support Files\Presets\Unfold`, Blink loose in `Presets\`, older copies to the
       Recycle Bin) and prints what it did.
     The README beside them says how they work. On no, they stay in `~/.claude/ae-presets/unfold/` for later.
9. **After a general install, run `strip-owner` (see "Owner code"). Delete the temporary unzip folder, then finish with the report** below, filled in, and nothing after it.

## Sound tools

Two skills need one step on each computer after setup:

- **real-sfx** (real recorded sound effects) ships with its stock settings and no library. Point it at a sound
  library once: `PY ~/.claude/skills/real-sfx/scripts/setup.py init --library main="<the library folder>" --index --force`
  (the sound-effects skill's own `~/.claude/skills/sound-effects/sfx` by default, with no need to ask; a library the
  user names if they have one; no `--uisfx`: its UI sounds are made in code, which the house rule never uses (real-sfx
  always runs with `--ui library`), so its own check saying "uisfx not installed" is expected; `--force` replaces the
  stock settings; `check` reports what's missing). Its settings and index are this computer's own: an update never
  replaces them. In the git edition real-sfx itself comes from Clipwing's repository during `install` (step 4).
- **earshot** (Claude's ears for sound) is a skill; its tool, with two listening models, is about 2.4 GB and isn't in
  the pack. Ask the user first (with the first questions); on their yes, run `PY sync.py earshot` in the background. It
  clones earshot at the version this pack was checked with into `~/.claude/tools/earshot`, makes its venv (CPU torch),
  fetches its two models and runs earshot's own check, which must end with `problems: []`. A working install is left
  as it is. If running it is refused (a safety check can block installing a third-party repository), give the user the
  same command to run themselves from the pack folder.

## Updating a computer that already has the pack

`~/.claude/setup-pack/installed.json` there means the pack was installed before: this run is an update. First
`PY sync.py news`: it prints the entries of the pack's `CHANGES.md` for the builds after the one installed here, and the
files this install would change, by area, compared by their contents. Each build has its own stamp (`build` in
`MANIFEST.json`, recorded in `installed.json` by every install), so this works when the version number stays the same.
Tell the user what's new, then update only what needs it: the bootstrap installs only missing tools; `install` without
`--transcription` and `--higgsfield` keeps this computer's choices, and writes only files that are new or changed; the
one-time steps (the tests, watch, real-sfx's library, earshot, the house-rules question) run again only when `news`
lists a change to them or `check` says one isn't set up. End with the short update report (PROMPT.md).

Files a third-party skill's maker published (HeyGen's, Clipwing's, Higgsfield's) are told apart from the user's own
changes: `MANIFEST.json` lists every version each maker published (`upstream`). A file here that is the maker's older
copy is updated (backed up first); one that is the maker's newer copy is kept and reported as newer; only a file the
maker never published counts as the user's own change.

## Updates keep the user's changes

Running a newer setup file never undoes what the user changed or added. `install` records what it wrote
(`~/.claude/setup-pack/installed.json`), and `earlier.json` in the pack holds the fingerprint of every file earlier setup
files shipped (from 3 Nov 2026 on; files from older packs count as changed, the safe side). Only a file still exactly as a
setup file wrote it is updated. A file the user changed stays as it is, and the pack's new version goes to
`~/.claude/setup-pack/updates/<version>/`; a pack file the user deleted stays deleted. The rules block in `CLAUDE.md` is
merged line by line: the pack's updates go in and the user's own lines stay (where both changed the same line, theirs is
kept and the pack's line is set apart in `updates/`). `settings.json` only gains or updates the pack's own entries. Files
and folders the user added are never moved; clean-up asks first. The tools' data (Folio's `~/.claude/folio`, PulseWise's
jobs and history, MarkRoom boards in projects) is never touched. `install` prints "KEPT AS YOU HAD IT" with each such
file; the report lists them, and Claude offers to merge any of them. The owner's edition updates as before.

## The three tools

MarkRoom (a skill), PulseWise and Folio (mods for the Claude desktop app) are optional, and each can be installed on
its own. `PY sync.py tools` says where each one comes from on this computer: a folder from a setup file, a plugin from
GitHub, or not installed.

- **A zip setup file** carries the ones its maker had as folders, and `install` puts them in. A tool this computer
  already has as a GitHub plugin is skipped, and an older folder copy of it goes to the backup with its settings lines,
  so it never loads twice.
- **The git edition** carries none. After `install`, ask the user one question that allows several answers: which of
  Folio, PulseWise and MarkRoom to install (none is fine). Run `PY sync.py tools --install <picks, comma-separated>`. It
  moves any older folder copy and its settings lines to the backup first, then installs each with
  `claude plugin install <tool> --marketplace Zoke-Hub/claude-tools --scope user -y` (Claude Code 2.1.292 or newer).
  Where the `claude` command isn't available, it prints the lines to type in a chat instead
  (`/plugin marketplace add Zoke-Hub/claude-tools`, then `/plugin install <tool>@zoke`, user scope).
  New chats load them. A tool folder with the user's changes is never replaced: the command says so and installs
  nothing on top; on the user's yes, `--set-aside` moves the folder to the backup first.
- **What each needs:** MarkRoom: Node, Python 3.10+ with Pillow (the shared cut-out venv has it), ffmpeg, and a
  claude.ai account whose artifacts allow a database, comments and file uploads. PulseWise and Folio: the Claude desktop
  app; Folio Claude Code 2.1.308 or newer, and its summaries use Haiku on the user's own usage.
- **Updating** a GitHub install: `claude plugin update <tool>@zoke`, then a new chat.
- **The owner's edition** keeps the tools as folders (its working copies): nothing is moved and nothing comes from GitHub.
- Without a tool, everything else works: without MarkRoom, review pictures and videos go in the chat; without
  PulseWise, long scripts run the same with no progress bar.

## Owner code

A full setup file also holds its owner's own edition, `owner.bin`, locked with a code only the owner has. If the user's
message holds a code (one word starting with `!`), open it first, right after unzipping and before anything else:
`PY sync.py unlock --owner-code '<code>'` from the unzipped folder (any Python 3 will do; on a Windows PC with no
Python yet, right after the bootstrap). Use the code exactly as written, same capitals, in single quotes, and pass it the
same way to every later `sync.py` command. Never change, guess or ask for a code, and don't repeat it in your messages.

- `sync.py` prints **Owner's own edition: unlocked.** when the code fits. It has then added the owner's files to the
  unzipped folder, with their own `MANIFEST.json` and `OWNER.md`: read `OWNER.md` at once and follow it along with these
  steps; it starts with what to say first.
- It prints **General pack.** when the code doesn't fit, or the file has no owner's edition. Carry on with the general
  pack, as with no code at all, and say nothing about codes.
- **After a general install** (no code accepted), run `PY sync.py strip-owner --zip "<the setup zip's path>"` before
  the unzip folder is deleted: it takes the owner's locked part out of the zip and the folder, since it was never
  installed here. Without `--zip` it clears only the folder.

## Building a setup file later

The pack installs its builder in `~/.claude/setup-pack/`, so this computer can make its own setup file whenever the
user asks Claude for one (the house note `build-setup-file.md` says how): a general setup file of this computer's
setup, saved to Downloads or a folder they name.

## The final report

When everything is installed, end with exactly this report, filled in, and write nothing after it. Leave out the
markroom row and the part of "How MarkRoom, PulseWise and Folio work" for any of the three tools that isn't
installed (the whole section when none is), and keep the "From GitHub" section only when the tools were installed from
GitHub. Print it as
Markdown, laid out as it stands (headings, lists, the skills table), not inside a code block. It names no one except
Zoke. Keep every description as written; fill in only the `<...>` parts, and leave out a line only
where it says "if" and that doesn't apply (Whisper when English only was chosen). Mark each skill as installed,
updated or unchanged.

~~~markdown
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
~~~

## Claude accounts

Everything the pack installs is local files, so it works the same on any Claude account. Only account-side things
don't come with it; tell the user which of these they may want to set up:

- **Plugins** belong to the account. Install watch as above; add others only if the user wants them.
- **Connectors** (Google Drive, ElevenLabs, ...) are per account: the user connects the ones they use in claude.ai
  settings. A paid web-scraping connector isn't needed: the Fetch MCP reads pages. The pack's deny rule for ElevenLabs
  transcription works whatever the connector's id is.
- **Published artifacts** (MarkRoom review boards, other pages) belong to the account that published them. When a
  board's `board.json` url can't be updated from this account, publish a new board and save its url in `board.json`.
- **Chat history** stays with the account and computer it was made on.

Re-running `install` later is safe: it only touches files that differ and backs them up first. To update, run install,
cleanup and check again with a newer pack.

## What is in the pack

| Part | Goes to | Purpose |
|---|---|---|
| `global/setup-pack/` | `~/.claude/setup-pack/` | The builder: `make_pack.py`, its templates, `PROMPT.md` and the pack's own scripts, so this computer can build its own setup file when asked. |
| `owner.bin` | opened only with the owner's code (full setup files only) | The owner's own edition, locked: their private notes, their Personal section and credit rule, its own `MANIFEST.json` and `OWNER.md`. Without the code it is never opened. |
| `bootstrap-mac.sh` | runs from the unzipped folder (macOS) | Checks Homebrew, then installs the tools every skill needs. |
| `bootstrap-windows.ps1` | runs from the unzipped folder (Windows) | Checks winget, then installs the same tools. |
| `global/CLAUDE.md` | merged into `~/.claude/CLAUDE.md` | The "# Global rules" block: no ElevenLabs transcription; which video skill wins; how to work in every project (questions and previews before building, motion, approve images first, verify facts, keep every render, 4K delivery / 1080p reviews, cut-outs, cut-out characters and pieces sheets, logos, MarkRoom, references, After Effects, maps of India, no personal assumptions, rules kept general, communication, long jobs on the progress bar); the house notes index; reading web pages (Fetch MCP). |
| `global/CLAUDE-sections-mac.md` | added to `~/.claude/CLAUDE.md` on macOS only | Transcription routing (local-transcribe with `python3.12`) and macOS notes (keg-only `ffmpeg-full`, venv paths). |
| `global/CLAUDE-sections-windows.md` | added to `~/.claude/CLAUDE.md` on Windows only | Transcription routing (`py -3.12`) and Windows notes (`Scripts\python.exe`, the full ffmpeg build, UTF-8 mode, the Python hook). |
| `global/house/*.md` | `~/.claude/house/` | The notes behind the rules: 4K delivery, motion rules, working rules. CLAUDE.md says which to read when. |
| `global/mods/pulsewise/`, `global/mods/folio/`, `global/mods/.claude-plugin/marketplace.json` (zip setup files only) | `~/.claude/mods/` + `settings.json` | Two mods for the Claude desktop app. PulseWise, the progress bar: a bar under the task list sized by each point's time, a bar per background job, other chats in the project. Folio, the chat archive: folds a long chat's older parts into an archive in a side panel to keep the chat light, and gives Claude a `recall` tool to look them up again; a FolioPack zip carries a chat's study, rules and decisions into a new chat on any computer (`import_pack` reads it). Each is loaded in every chat through `env` `CLAUDE_CODE_PLUGIN_DIRS` (both folders, joined with `:` on macOS and `;` on Windows; + `CLAUDE_CODE_PLUGIN_DIR_WATCH=1`); the `local-mods` marketplace lists both. Their tests and generated type files are never packed. Folio needs Claude Code 2.1.308 or newer, and `~/.claude/folio` (Folio's saved data for each person's own chats, and `prefs.json` with the folder they chose for FolioPacks) is never packed: each install makes its own. FolioPacks zip with the system's own tools on both Mac and Windows (Windows 10+ `tar.exe`), so nothing extra is installed for them. |
| `global/hooks/block-elevenlabs-transcription.sh` / `.py` | `~/.claude/hooks/` + `settings.json` | PreToolUse hook that hard-blocks cloud transcription on ElevenLabs (and a deny rule for the connector's transcribe tool). The `.sh` (bash + jq) is registered on macOS, the `.py` (same rules, also the PowerShell tool) on Windows. |
| `skills/*` | `~/.claude/skills/` | markroom (formerly redline), logo-recreation and animation (by Zoke), cutout, chat-archive, local-transcribe (only where missing), the hyperframes family, media-use, motion-graphics, motion-broll, object-separation, the explainer-* skills, sound-effects, the higgsfield-* skills (optional: only on the user's yes, step 3; they need the Higgsfield CLI and the user's own Higgsfield account; the skill installs the CLI and asks the user to log in when first used), and the UI / UX design skills (frontend-design, web-interface-guidelines, refactoring-ui, laws-of-ux ×3, the usability, accessibility and design audits). Third-party skills keep their own licence files. |
| retired skills | removed (backed up first) | `review-dashboard` was merged into `redline`, which is now `markroom` (MarkRoom); both are removed. "Open the dashboard" now means a MarkRoom board. `animation-easing`, `after-effects-translation` and `puppet-rig` are merged into `animation`; `aroll-zooms-and-cuts` is retired. |
| `global/ae-presets/unfold/` | `~/.claude/ae-presets/unfold/` | The Unfold text presets for After Effects (`presets/`, 90 `.ffx`), their Mac installer `install_presets.sh` and a README. Owner's edition only (inside `owner.bin`). Installed into After Effects only on a yes (step 8). |
| video-use | cloned from GitHub | Never copied (its `.env` can hold an API key). Clone, `uv sync`, and never run its transcribe helpers: local-transcribe does that step. |
| `extras/video-use-windows-paths.patch` | applied to the video-use clone | Two `as_posix()` path fixes (needed on Windows, harmless on macOS) so every clone matches. |
| cut-out venv | `~/.claude/venvs/cutout` (`--cutout-env`) | Python 3.12 + torch, transformers 4, timm, kornia, opencv, Pillow, and the BiRefNet HR model; shared by every project (also markroom's Pillow). |
| Fetch MCP | user-level MCP server `fetch` in `~/.claude.json` | `mcp-server-fetch` via `uvx`: reads web pages word for word (licences, quotes). The rules make it the default. |
| Parakeet TDT 0.6B v3 | `~/.cache/hyperframes/parakeet` (`--parakeet`) | The local transcription model used by local-transcribe and `npx hyperframes transcribe`. |
| Whisper large-v3 | hyperframes' whisper.cpp models (`--transcription multilingual`) | Local transcription for every other language. |

Project files (a video's handoff, studies, media, renders) are not in this pack; they travel with their project folder.
