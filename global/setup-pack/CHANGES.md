# What's new in the setup pack

Each build of the setup pack has its own stamp, in its heading here. On a computer that has the pack, `sync.py news` lists
the entries newer than the build installed there, so this list works even when the version number stays the same.

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
