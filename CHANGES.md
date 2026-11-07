# What's new in the setup pack

Each build of the setup pack has its own stamp, in its heading here. On a computer that has the pack, `sync.py news` lists
the entries newer than the build installed there, so this list works even when the version number stays the same.

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
