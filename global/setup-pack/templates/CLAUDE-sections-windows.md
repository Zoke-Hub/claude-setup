# Transcription routing

- **video-use:** its transcription step always goes through the `local-transcribe` skill: `py -3.12 ~/.claude/skills/local-transcribe/scripts/local_transcribe.py <video or folder>` (or `python` if that is 3.10+). It writes `<edit_dir>/transcripts/<video_stem>.json` in the layout video-use's helpers read, so the rest of video-use runs unchanged. video-use doesn't need an `ELEVENLABS_API_KEY`: skip its cold-start key check and never ask for a key.
- **Engine and languages:** see `# Transcription languages` (chosen per machine at setup: English only, or multilingual).
- **hyperframes and media-use captions:** `npx hyperframes transcribe` (`--engine auto`) uses Parakeet once it is installed (`npx hyperframes models install parakeet`, about 640 MB, once per machine).

# This machine (Windows)

- Python venvs use `Scripts\python.exe`, not `bin/python`: the cut-out venv is `~/.claude/venvs/cutout/Scripts/python.exe`, video-use's is `~/.claude/skills/video-use/.venv/Scripts/python.exe`. Skill notes that show `bin/python` mean that file here.
- ffmpeg from winget (Gyan) is already a full build (drawtext, subtitles, zscale): no PATH prefix is needed, unlike the Mac's keg-only `ffmpeg-full`.
- `PYTHONUTF8=1` is set in `~/.claude/settings.json` (`env`) because video-use's helpers print and write non-ASCII characters.
- The ElevenLabs block hook here is the Python version, `~/.claude/hooks/block-elevenlabs-transcription.py`, registered for both the Bash and PowerShell tools.
- Run scripts with `py -3.12` (or `python`) wherever the notes say `python3.12` or `/opt/homebrew/bin/python3.12`.
