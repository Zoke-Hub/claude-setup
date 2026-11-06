---
name: earshot
description: Listen to sound for Claude, who can't hear - describe what an audio file sounds like, check how well a file fits a description, rank candidate sound effects against one, find the best moment inside a long recording, and read a finished video's sound as a timeline, an annotated sheet (frames, events, spectrogram, loudness, sync to the cuts) or a scorecard, plus loudness measurements. Runs locally on the CPU with the earshot tool. Use whenever choosing between sound-effect files, checking that a sound is what its name says, checking sound sync and levels in a render, or measuring loudness. Never use earshot's made-in-code sounds in a video.
---

# earshot: ears for checking sound

earshot (github.com/Leonxlnx/earshot, MIT) turns sound into evidence: words, scores and pictures. It is installed
outside the skills folder, because with its two listening models it is about 2.4 GB:

- the tool: `~/.claude/tools/earshot`, its CLI `~/.claude/tools/earshot/.venv/bin/earshot` (on Windows
  `%USERPROFILE%\.claude\tools\earshot\.venv\Scripts\earshot.exe`)
- the models: `~/.claude/tools/earshot/.cache` (CLAP and an AudioSet tagger, pinned; it never downloads again)

On a Mac, put ffmpeg-full first on PATH, as for any render: `PATH="$(brew --prefix)/opt/ffmpeg-full/bin:$PATH"`. On
Windows the ffmpeg the setup installed is already on PATH.

## The house limit

Sound effects and music in a video are real recordings only. earshot can also **make** sounds in code (`forge`,
`sfx`, `kit`, `fit` and its bank of 252): those are synthesis, so they never go in a video. Use earshot only to
listen and measure. Its `llm` command uploads audio to Google: never run it without asking.

## What to use it for

| Job | Command |
|---|---|
| What a file sounds like | `earshot describe FILE` |
| Does it fit a description | `earshot match FILE "a deep wooden knock" --alts "a door slam" "a footstep"` |
| Pick the best of several downloads | `earshot rank "a soft paper flip" A.wav B.wav C.wav` |
| The best moment inside a long recording | `earshot find FILE "a single coin drop" --top 4` (start / end seconds to trim) |
| Two takes compared, in words | `earshot ab A.wav B.wav` |
| Real recording or made in code | `earshot realness FILE` (easy to fool; a hint, not proof) |
| A render's sound, second by second | `earshot timeline FILM.mp4 [--video FILM.mp4] [--cues cues.json]` |
| The same as a picture to read | `earshot sheet FILM.mp4 -o sheet.png` (frames, events, spectrogram, loudness, sync markers) |
| Loudness and peaks, no models | `earshot measure FILE` (LUFS, true peak, LRA, envelope, tempo, key) |

Every command prints a plain summary; `--json` gives everything. Each call loads the models first (20–40 s), except
`measure`. For more than a few files, run one script with the venv's Python and `from earshot import api`, so the
models load once.

These are measurements, not ears. Say what was measured, never that something "sounds good", and still give the
user the moments to check with headphones, as the `sound-effects` and `real-sfx` skills do.

## Where it isn't installed

On a Mac:

```bash
git clone https://github.com/Leonxlnx/earshot ~/.claude/tools/earshot && cd ~/.claude/tools/earshot
python3.12 -m venv .venv                     # any Python 3.10+
.venv/bin/python -m pip install torch
.venv/bin/python -m pip install -e ".[mcp]"
.venv/bin/python -m earshot doctor --fetch   # the two models, about 1.1 GB, once
.venv/bin/python -m earshot doctor --load    # must end with problems: []
```

On Windows (PowerShell):

```powershell
git -c http.sslBackend=openssl clone https://github.com/Leonxlnx/earshot "$env:USERPROFILE\.claude\tools\earshot"; cd "$env:USERPROFILE\.claude\tools\earshot"
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\python -m pip install -e ".[mcp]"
.venv\Scripts\python -m earshot doctor --fetch
.venv\Scripts\python -m earshot doctor --load
```

Ask before installing: it is about 2.4 GB.
