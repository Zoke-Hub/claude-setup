---
name: local-transcribe
description: Transcribe video or audio on this computer with the best local engine (Parakeet TDT 0.6B v3 for English and other European languages, Whisper large-v3 for any other language) and write word-level transcripts in video-use's format. Use for video-use's transcription step, instead of its transcribe.py / transcribe_batch.py (those call ElevenLabs, which is banned), and whenever someone wants a transcript or word timings from footage. Never uses a cloud transcriber.
---

# local-transcribe

One command turns a clip, or a folder of takes, into the transcripts video-use's other helpers read. Everything runs
on this machine through `npx hyperframes transcribe`; nothing is uploaded.

```bash
python3 ~/.claude/skills/local-transcribe/scripts/local_transcribe.py <video-or-folder> [more ...]
```

- Writes `<edit_dir>/transcripts/<video_stem>.json` (`<edit_dir>` defaults to `<video_parent>/edit`, as in video-use;
  `--edit-dir` to change it). Same path, name and layout as video-use's own helper, so its cache, `pack_transcripts.py`,
  `timeline_view.py` and `render.py` (including `--build-subtitles`) work unchanged.
- An existing transcript is reused; `--force` redoes it. `--audio-track N` works as in video-use (OBS mic on track 1).
- `--num-speakers` is accepted and ignored.

## Which engine (`--engine auto`, the default, picks it)

| Speech | Engine | Notes |
|---|---|---|
| English, or one of the other 24 European languages Parakeet covers | **Parakeet TDT 0.6B v3** | Most accurate local engine, fast on CPU (a 17 s clip in about 6 s). |
| Anything else: Hindi, Malayalam, Tamil, ... | **Whisper large-v3** (whisper.cpp) | Pass `--language hi` (etc.). See below. |

If the language isn't English and you don't know it, ask before transcribing. Parakeet produces nonsense on languages
it doesn't cover.

**Whisper path.** When `whisper-cli` is on PATH and `~/.cache/hyperframes/whisper/models/` holds `ggml-large-v3.bin`
(3.1 GB) and `ggml-silero-v5.1.2.bin` (Silero voice detection, 0.9 MB), the script runs whisper.cpp directly, on the GPU
if its build has one, with voice detection and one word per segment. Otherwise it falls back to
`npx hyperframes transcribe --engine whisper`, which has no voice detection: on a 103 s Hindi test clip that skipped
half the speech (119 words against 242). Only the Windows PC is set up for this (whisper.cpp CUDA build in
`%LOCALAPPDATA%\Programs\whisper.cpp`); a 103 s Hindi clip takes about 100 s there.

## In video-use

Wherever video-use says `transcribe.py <video>` or `transcribe_batch.py <videos_dir>`, run this script on the same file
or folder instead. Then carry on exactly as video-use describes (`pack_transcripts.py --edit-dir <dir>` →
`takes_packed.md` → EDL → render). video-use's cold-start check for `ELEVENLABS_API_KEY` doesn't apply: never ask the
user for an ElevenLabs key. A PreToolUse hook blocks the ElevenLabs helpers anyway.

## What differs from ElevenLabs Scribe

- **Word timing.** Parakeet's word ends run on into pauses; the script trims each word where the audio drops below
  -35 dB for 0.3 s (ffmpeg `silencedetect`), so pauses and retakes show up as gaps the way Scribe reported them.
  Boundaries are good to roughly a frame or two: check cut points with `timeline_view.py` as video-use already does.
- **No speaker labels** (no diarization), so phrases never split on a speaker change. For interviews with several
  voices, split by speaker yourself from the content.
- **No audio-event tags** (laughter, music).
- **Names.** Proper nouns can come out wrong (an old place name heard as a similar-sounding word). Check names in `takes_packed.md` against the
  script before choosing takes; the timings are still right.

## Other tools

- hyperframes and media-use captions: `npx hyperframes transcribe` already picks Parakeet automatically
  (`--engine auto`) now that the model is installed. media-use's `transcribe.mjs` prefers parakeet-mlx on Apple
  Silicon and falls back to the same CLI elsewhere.
- watch: keeps its own local WhisperX setup.
- Setup on a new machine: Node + ffmpeg, then `npx hyperframes models install parakeet` (about 640 MB, once).
