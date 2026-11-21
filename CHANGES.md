# What's new in the setup pack

Each build of the setup pack has its own stamp, in its heading here. On a computer that has the pack, `sync.py news` lists
the entries newer than the build installed there, so this list works even when the version number stays the same.

## Build 2026-11-21.192858 · version 2026-11-06.073618

- **A new house rule, "Notify when waiting"** (`house/notify-when-waiting.md`, and a line in CLAUDE.md's Communication
  rule): when work stops because it needs the person's input, Claude sends a notification and opens its message with
  exactly what's needed, numbered, with the suggested answer.
- **Folio** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-21): a redesign of how Folio keeps a chat: parts and tasks, a ledger of rules, decisions and values, a
  folded history with a fixed budget, folds in real tokens between a ceiling and a floor, faster recall, a log, and a
  reworked panel. Each chat's saved data upgrades the first time it loads, keeping every part's number.

## Build 2026-11-20.232941 · version 2026-11-06.073618

- **animation skill:** text that moves, scales or sits under a camera move in an HTML / HyperFrames animation is
  outlined to SVG paths at build time with the new `scripts/outline_text.cjs` (fontkit, kerning and ligatures), since
  live text snaps to whole pixels and jitters during slow moves. The rule is in `references/easing.md` (section 4 and
  the checklist) and in the skill's short list.
- **MarkRoom** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-20): the save status beside "Notes on the whole image" is a short word that is never cut off, with its full
  sentence on hover; a failed save shows its whole message under the heading.
- **PulseWise** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-20): a stopped command or agent ends the jobs it reported with, and a job silent for 2 hours leaves the bar;
  each job lands on its own agent's beat, with the progress lines added to agents' briefs by PulseWise itself; steps
  count what is inside them; names read better; short lists aren't asked for an estimate; hover boxes no longer stay
  up after the pointer leaves.

## Build 2026-11-20.130316 · version 2026-11-20.130316

- **Folio** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-19): as a chat starts, Folio reads where the project already keeps renders, editing projects, references
  and sound, and tells Claude to save new files of each kind there; it never moves a file. Auto-save, backup and
  scratch folders don't count; the `projectLayout` setting turns it off.

## Build 2026-11-19.125247 · version 2026-11-06.073618

- **PulseWise** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-19): Claude counts its own work on each point, so a beat fills from real counts (no more empty "no count"
  part); servers and watchers stay off the bar; a command and the job its script starts show as one bar; list
  changes show at once; a long name gets a short label from Haiku; each new list gets Claude's estimate, logged
  against the real times in `~/.claude/progress/eta-log.jsonl`; Other pulses shows every local chat on this computer
  and finds the app's chat records where the Store app keeps them now, so finished chats leave once seen.
- **Setup guide:** its PulseWise lines say so, that Other pulses covers every local chat, and that PulseWise now uses
  a little Claude usage (short notes, and a Haiku call for an overlong name).

## Build 2026-11-19.083758 · version 2026-11-19.083758

- **MarkRoom** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-19): a link to a live round opens it when the link opens a closed board; a new round comes forward only in
  the tab on screen or a related tab (`build_board.mjs --for "<tab>"`), elsewhere it only shows a notice; the Version
  list sits at the far right of the header. Boards get the new page from their next republish.

## Build 2026-11-17.003707 · version 2026-11-06.073618

- **Rules:** a MarkRoom file link is the one the skill's `build_board.mjs --link <file id>` prints: `#open-<file id>`,
  or a plain `#<file id>` on a board whose published page is older than `#open-` links (such a page opened the first
  tab for them). CLAUDE.md's review-pages line and `dashboard-means-markroom.md` say so.
- **MarkRoom** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-17): the page carries its version, `--published` records which one a board runs, and the current page also
  opens a plain `#<file id>`, a live round included.

## Build 2026-11-15.125802 · version 2026-11-15.125802

- **Windows:** the Bonjour note no longer offers a Bonjour update, which turned out not to stop the "Local Security
  Authority" pop-up: 3.1.0.1, the newest, is blocked too. The note now shows wherever Bonjour's name-lookup add-in is
  in Windows' name-lookup list and LSA protection is on, whatever the version, and gives the two `regsvr32 /u` lines
  (the user's to run as administrator) or uninstalling Bonjour.
- **PulseWise** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-15): a job's counts land on its own point (a job run through a shell or interpreter is matched to its
  command by the script it runs or its name), and every name the bar shows is kept to 32 characters, summarised.
- **Folio** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-15): the Custom slider's knob is larger, sits on the track's centre and covers the rounded end at the
  lowest and highest stops; the fill blends from blue to amber between 500k and 550k, and nothing lags a drag.

## Build 2026-11-14.203815 · version 2026-11-06.073618

- **Rules:** the owner code may be used again only within 30 minutes of when it was typed in the chat; after that,
  Claude asks for it again. Only the time counts (`locked-needs-the-code.md`).
- **Folio** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-14): a fold leaves one short line in the chat, and Claude gets the folded history in a context block of its
  own. FolioPack's "This chat" also lists files made or used by shell commands (renders above all), and renders are
  grouped under their animation's name.

## Build 2026-11-14.130117 · version 2026-11-14.130117

- **PulseWise** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-14): the beats' click and hover areas line up with the beats again, and the bars are pressed level with
  where they are drawn.

## Build 2026-11-14.011914 · version 2026-11-06.073618

- **Rules:** a new, soft one: where an interface or graphic needs an icon, use a real one (SVG or an icon set, sized
  and centred with its text) rather than an emoji, emoticon or symbol; a style that calls for emojis wins
  (`icons-over-emojis.md`).
- **MarkRoom** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update, dated
  2026-11-14): Claude replies to each note as soon as its change is made, and marks the notes done once the new round
  is up. Each note's state is kept in its own fields, and moving a mark after a reply opens the note again.
- **Setup file builder:** the PROMPT.md beside a new zip gets the build's date, so the two sort together in a folder.

## Build 2026-11-13.095559 · version 2026-11-06.073618

- **Rules:** the clean-up check also looks for implicit state machines: a mode or lifecycle spread over several flags,
  timers or maybe-empty values, each listed with its states and how it can go wrong (`cleanup-check.md`).
- **The three tools** (in a setup file that carries them; a GitHub install gets them from the tools' own update, dated
  2026-11-13):
  - **MarkRoom:** the tool bar's dividers are centred and both drawn; Alt/Option + arrows switch tabs (← / →) and
    versions (↑ / ↓), and moving a tab is Alt/Option + Shift + ← / →. Failed note saves are retried, words in the
    whole-file note survive Claude replying, empty drafts are dropped, undo goes to its own file, and a lost
    connection reconnects.
  - **Folio:** after `/clear` nothing from the old chat comes back; "Folding…" and "Packing…" never stick; new output is
    saved word for word while older parts are summarised; recalled and pinned answers are looked up again once newer
    parts could change them, and Unpin sticks.
  - **PulseWise:** a job that stops reporting waits instead of failing, with no false "Stopped" toast or flash; a turn
    that ends with points open reads "waiting for your reply"; dead jobs don't come back on reload. The progress helper
    treats `sys.exit(0)` as done.

## Build 2026-11-12.074024 · version 2026-11-12.074024

- **Owner's edition:** a line in the Personal section that ends in `<!-- this machine only -->` (a note about one
  computer's hardware or paths) stays on that computer: the builder leaves it out of both the Mac's and Windows'
  sections, and names any Personal line about "this PC" or "this Mac" that isn't marked. The Personal section also has
  three lines it lacked on one computer.

## Build 2026-11-12.050711 · version 2026-11-06.073618

- **Rules:** the owner code. A code typed recently in the same chat, for the same work, can be used again for a rebuild
  right after; one given a long time ago is asked for again (`locked-needs-the-code.md`).
- **MarkRoom** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update): a board
  you come back to opens where you left it (file, zoom, spot, a video's moment), and switching video versions of the same
  length keeps the playhead even when their beat labels differ.
- **Windows:** the bootstrap checks Bonjour's version. A Bonjour older than 3.1.0.1 is what brings up the "Local
  Security Authority" pop-up at start-up; Claude now offers the update to 3.1.0.1 (one winget line, with an
  administrator prompt), which stops it. With 3.1.0.1 or newer the note no longer shows.

## Build 2026-11-07.232208 · version 2026-11-06.073618

- **Rules:** a new working rule, **Releases**: a change that several packages or editions share goes into every one
  that carries it, in the same release, each tested as a first install and as an update over edited, deleted and added
  files (`release-every-package.md`).

## Build 2026-11-07.225800 · version 2026-11-07.225800

- **MarkRoom** (in a setup file that carries the tools; a GitHub install gets it from the tools' own update): dragging
  the playhead on a video's timeline shows the frames as it goes, and so do held arrow keys and the −1f / +1f buttons.
  Clicking or dragging on the timeline, or dragging a tab, never selects text. New boards keep a keyframe every half
  second in their review videos, so the preview keeps up with the drag.
- **Your own changes** stay through an update in the owner's edition too, for every file its last install recorded:
  the new version is parked beside it, as in the general edition. A pack file you deleted stays deleted, and
  `sync.py news` now says so instead of listing it as new.

## Build 2026-11-07.220800 · version 2026-11-06.073618

- **The tools from GitHub** update through the tools repo's `UPDATE.md`: only the tools whose files changed, and also
  when an update keeps their version number (`claude plugin update` alone missed those).

## Build 2026-11-07.215142 · version 2026-11-06.073618

- **Updates:** setup first checks whether this computer has the pack already. If it does, it shows what's new, keeps the
  choices made before (transcription languages, Higgsfield), writes only the files that are new or changed, skips the
  one-time steps unless something in them changed, and ends with a short update report.
- **What's new:** `sync.py news` lists what a setup file changes on this computer: these entries and the files, by area.
- **The ElevenLabs block hook on Windows** now runs without a shell (exec form). In a chat that started before Git was
  installed it no longer blocks every command until the app restarts. The older entry is converted.
- **Settings:** an update saves its changes to `settings.json` again. Before, only a first install did, so changes to
  an existing settings file (the hook above, among others) never reached a computer that already had the pack.
- **Line endings:** every text file the pack writes uses LF on every system, a `CLAUDE.md` or `settings.json` an older
  pack left with Windows line ends is converted, and the video-use path patch applies again on Windows.
- **yt-dlp** is installed without its own second copy of FFmpeg.
- **HeyGen's skills:** a file that is an older copy from HeyGen is updated instead of being kept as yours; a newer one is
  kept and named as newer. Only files HeyGen never published count as your own changes.
- **HeyGen's retired skills** (hyperframes-animation, -audio, -core, -creative, -keyframes, -studio and motion-graphics)
  are now HeyGen's last version before it retired them, from 21 October 2026.
- **earshot's tool** installs with `sync.py earshot`, asked about with the first questions, at the version the pack was
  checked with.
- **The cut-out test** uses a CC0 museum photo that comes with the pack.
- **watch on Windows:** a fallback when WhisperX's model download fails with a symlink error.
- **real-sfx** is set up without its made-in-code UI sounds, which the house rules never use.
- **Clean-up** never lists the Claude app's own synced-skills folder.
- **Rules:** whenever Claude changes something in a MarkRoom, its message links straight to the file that changed.
- **Building a setup file:** notes that point at files outside `~/.claude` are flagged, so a setup file stays complete
  on its own.
- **The tools from GitHub:** MarkRoom's links open the file that changed; PulseWise files a background job under the point
  it was started for, and on Windows flashes the Claude app's taskbar button when long work finishes while the app is
  behind other windows; Folio's context bar names each part's tokens below and above the fold-back line, and the room
  left before the fold.
