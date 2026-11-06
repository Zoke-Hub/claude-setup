# Transcription routing

- **video-use:** its transcription step always goes through the `local-transcribe` skill: `python3.12 ~/.claude/skills/local-transcribe/scripts/local_transcribe.py <video or folder>` (the script needs Python 3.10+; macOS's own `python3` is 3.9). It writes `<edit_dir>/transcripts/<video_stem>.json` in the layout video-use's helpers read, so the rest of video-use runs unchanged. video-use doesn't need an `ELEVENLABS_API_KEY`: skip its cold-start key check and never ask for a key.
- **Engine and languages:** see `# Transcription languages` below (chosen per machine at setup).
- **hyperframes and media-use captions:** `npx hyperframes transcribe` (`--engine auto`) uses Parakeet once it is installed (`npx hyperframes models install parakeet`, about 640 MB, once per machine).

# This machine (macOS)

- Homebrew's `ffmpeg` is a slim build without `drawtext`, `subtitles` or `zscale`. `ffmpeg-full` is installed keg-only at `$(brew --prefix)/opt/ffmpeg-full/bin`: put it first on PATH for any render or caption burn-in (`PATH="$(brew --prefix)/opt/ffmpeg-full/bin:$PATH"`), including in sub-agent briefs.
- Run Python 3.10+ scripts with `python3.12`. The shared cut-out venv is `~/.claude/venvs/cutout/bin/python`; video-use's is `~/.claude/skills/video-use/.venv/bin/python`.
