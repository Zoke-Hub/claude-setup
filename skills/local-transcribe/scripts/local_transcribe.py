#!/usr/bin/env python3
"""Transcribe video or audio on this computer and write video-use's transcript format. Never calls a cloud service.

  python3 local_transcribe.py <video|folder> [...] [--edit-dir DIR] [--language CODE]
                              [--engine auto|parakeet|whisper] [--whisper-model large-v3] [--audio-track N] [--force]

Output: <edit_dir>/transcripts/<video_stem>[.trackN].json (edit_dir defaults to <video_parent>/edit), the same path and
layout video-use's own Scribe helper wrote: {"language_code", "text", "words": [{"type": "word"|"spacing", "text",
"start", "end"}], ...}, times in seconds. video-use's pack_transcripts.py, timeline_view.py and render.py read it as is.

Engines (all local):
  parakeet  NVIDIA Parakeet TDT 0.6B v3 via `npx hyperframes transcribe`, the most accurate local engine: English and
            24 other European languages.
  whisper   Whisper large-v3 for every other language (Hindi, ...): run directly by whisper-cli (whisper.cpp, on the GPU
            when its build has one) with Silero voice detection and one word per segment, when whisper-cli and
            ~/.cache/hyperframes/whisper/models/{ggml-large-v3.bin, ggml-silero-v5.1.2.bin} exist; otherwise through
            `npx hyperframes transcribe --engine whisper` (no voice detection; it can skip speech).
  auto      parakeet, unless --language names a language Parakeet doesn't cover.
Parakeet's word ends run on into pauses, so each word is trimmed to the audio with ffmpeg silencedetect; the gaps become
"spacing" entries, which is how video-use sees pauses and retakes. There are no speaker labels (no diarization).
"""
import argparse
import array
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

PARAKEET_LANGS = {"bg", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "de", "el", "hu", "it", "lv", "lt", "mt",
                  "pl", "pt", "ro", "sk", "sl", "es", "sv", "ru", "uk"}
MEDIA_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".mxf", ".webm", ".wav", ".mp3", ".m4a", ".aac", ".flac"}
SILENCE_DB, SILENCE_MIN = -35, 0.3      # a pause = audio below -35 dB for at least 0.3 s
MIN_WORD = 0.06                         # never trim a word shorter than this
WHISPER_MODELS = Path.home() / ".cache" / "hyperframes" / "whisper" / "models"   # hyperframes' whisper model cache
VAD_MODEL = "ggml-silero-v5.1.2.bin"


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def transcript_path(edit_dir: Path, video: Path, track: int) -> Path:
    """Same naming as video-use's transcribe.py, so its cache and helpers find the file."""
    return edit_dir / "transcripts" / f"{video.stem}{'' if track == 0 else f'.track{track}'}.json"


def extract_audio(video: Path, dest: Path, track: int) -> None:
    r = run(["ffmpeg", "-y", "-i", video, "-map", f"0:a:{track}", "-vn", "-ac", "1", "-ar", "16000",
             "-c:a", "pcm_s16le", dest])
    if r.returncode:
        last = (r.stderr.strip().splitlines() or ["no output"])[-1]
        raise RuntimeError(f"ffmpeg could not extract audio track {track}: {last}")


def peak_dbfs(wav_path: Path) -> float:
    peak = 0
    with wave.open(str(wav_path), "rb") as w:
        while frames := w.readframes(1 << 16):
            samples = array.array("h", frames)
            peak = max(peak, max(samples), -min(samples))
    return 20 * math.log10(peak / 32768) if peak > 0 else float("-inf")


def pauses(wav: Path) -> list[tuple[float, float]]:
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af",
             f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_MIN}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [(max(a, 0.0), ends[i] if i < len(ends) else math.inf) for i, a in enumerate(starts)]


def tighten(words: list[dict], gaps: list[tuple[float, float]]) -> list[dict]:
    """Move word edges out of pauses: a word that runs on into a pause ends where the pause starts."""
    for w in words:
        s, e = w["start"], w["end"]
        for a, b in gaps:
            if b <= s or a >= e:
                continue
            if a <= s and b < e and e - b >= MIN_WORD:      # pause covers the word's start
                s = b
            elif a > s and a - s >= MIN_WORD:               # pause starts inside the word
                e = a
                break
        w["start"], w["end"] = s, e
    return words


def npx() -> str:
    for name in ("npx.cmd", "npx"):
        if path := shutil.which(name):
            return path
    sys.exit("npx (Node.js) not found. Install Node, then run: npx hyperframes models install parakeet")


def hyperframes_transcribe(wav: Path, engine: str, language: str | None, model: str) -> tuple[dict, list]:
    cmd = [npx(), "-y", "hyperframes", "transcribe", wav, "--engine", engine, "--json", "-d", wav.parent]
    if language:
        cmd += ["--language", language]
    if engine == "whisper":
        cmd += ["--model", model]
    r = run(cmd, cwd=tempfile.gettempdir())   # not inside the work folder, so nothing holds it open afterwards
    result = None
    for line in reversed(r.stdout.strip().splitlines()):
        try:
            result = json.loads(line)
            break
        except ValueError:
            continue
    if r.returncode or not isinstance(result, dict) or not result.get("ok"):
        tail = "\n".join((r.stderr or r.stdout).strip().splitlines()[-6:])
        hint = "  (Parakeet missing? run: npx hyperframes models install parakeet)" if engine == "parakeet" else ""
        raise RuntimeError(f"hyperframes transcribe --engine {engine} failed{hint}:\n{tail}")
    return result, json.loads(Path(result["transcriptPath"]).read_text(encoding="utf-8"))


def whisper_cpp(wav: Path, language: str | None, model: str) -> tuple[dict, list] | None:
    """Whisper run directly by whisper.cpp (GPU when its build has one) with Silero voice detection and one word per
    segment. Without voice detection Whisper skipped half of a 103 s Hindi test clip (119 words against 242).
    Returns None when whisper-cli or the models are missing, so the caller can fall back to hyperframes."""
    cli = shutil.which("whisper-cli")
    weights, vad = WHISPER_MODELS / f"ggml-{model}.bin", WHISPER_MODELS / VAD_MODEL
    if not (cli and weights.is_file() and vad.is_file()):
        return None
    prefix = wav.with_name("whisper")
    r = run([cli, "-m", weights, "-f", wav, "-l", language or "auto", "--vad", "-vm", vad, "-vmsd", "25", "-mc", "0",
             "-ml", "1", "-sow", "-oj", "-of", prefix], cwd=tempfile.gettempdir())
    out = prefix.with_suffix(".json")
    if r.returncode or not out.is_file():
        tail = "\n".join((r.stderr or r.stdout).strip().splitlines()[-6:])
        raise RuntimeError(f"whisper-cli failed:\n{tail}")
    words: list[dict] = []
    for seg in json.loads(out.read_text(encoding="utf-8", errors="replace"))["transcription"]:
        text = seg["text"].strip()
        if not text:
            continue
        start, end = seg["offsets"]["from"] / 1000, seg["offsets"]["to"] / 1000
        if words and not any(ch.isalnum() for ch in text):     # lone punctuation joins the word before it
            words[-1]["text"] += text
            continue
        words.append({"text": text, "start": start, "end": max(end, start)})
    gpu = "GPU" if "CUDA" in r.stderr or "Metal" in r.stderr else "CPU"
    return {"engine": "whisper", "model": model, "detectedLanguage": language,
            "label": f"whisper {model} (local whisper.cpp, {gpu}, Silero VAD)"}, words


def transcribe_wav(wav: Path, engine: str, language: str | None, model: str) -> tuple[dict, list]:
    if engine == "whisper" and (direct := whisper_cpp(wav, language, model)):
        return direct
    return hyperframes_transcribe(wav, engine, language, model)


def to_video_use(raw: list, gaps: list, language: str | None, result: dict, video: Path, track: int) -> dict:
    words = [{"text": str(w.get("text", "")).strip(), "start": float(w["start"]), "end": float(w["end"])}
             for w in raw if str(w.get("text", "")).strip()]
    words = tighten(words, gaps)
    out: list[dict] = []
    for w in words:
        if out and w["start"] >= out[-1]["end"]:
            out.append({"type": "spacing", "text": " ", "start": out[-1]["end"], "end": round(w["start"], 3)})
        out.append({"type": "word", "text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)})
    return {
        "language_code": language or result.get("detectedLanguage"),
        "text": " ".join(w["text"] for w in words),
        "words": out,
        "transcription_engine": result.get("label") or f"{result.get('engine')} {result.get('model')} (local, hyperframes)",
        "source": str(video),
        "audio_track": track,
    }


def transcribe_one(video: Path, edit_dir: Path, engine: str, language: str | None, model: str, track: int,
                   force: bool) -> Path:
    out = transcript_path(edit_dir, video, track)
    if out.exists() and not force:
        print(f"cached: {out}")
        return out
    t0 = time.time()
    print(f"transcribing {video.name} ({engine})", flush=True)
    # Windows can briefly lock the folder (a virus scan of the new files); a leftover temp folder is harmless.
    with tempfile.TemporaryDirectory(prefix="local-transcribe-", ignore_cleanup_errors=True) as tmp:
        wav = Path(tmp) / "audio.wav"          # work on a copy: hyperframes writes transcript.json beside its input
        extract_audio(video, wav, track)
        peak = peak_dbfs(wav)
        if peak < -60:
            raise RuntimeError(f"audio track {track} is silent (peak {peak:.1f} dBFS); try --audio-track")
        result, raw = transcribe_wav(wav, engine, language, model)
        gaps = pauses(wav)
    payload = to_video_use(raw, gaps, language, result, video, track)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")   # ASCII: video-use reads it
    n = sum(1 for w in payload["words"] if w["type"] == "word")                         # with the default encoding
    print(f"  saved: {out}  ({n} words, {result.get('model')}, {time.time() - t0:.1f}s)")
    return out


def collect(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        p = Path(item).expanduser().resolve()
        if p.is_dir():
            files += sorted(f for f in p.iterdir() if f.is_file() and f.suffix.lower() in MEDIA_EXTS)
        elif p.is_file():
            files.append(p)
        else:
            sys.exit(f"not found: {p}")
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="video/audio files or folders (folders: every media file inside)")
    ap.add_argument("--edit-dir", type=Path, help="default: <video_parent>/edit, as in video-use")
    ap.add_argument("--language", help="spoken language code (en, hi, ml, ...); picks the engine")
    ap.add_argument("--engine", choices=["auto", "parakeet", "whisper"], default="auto")
    ap.add_argument("--whisper-model", default="large-v3", help="whisper engine only (default large-v3)")
    ap.add_argument("--audio-track", type=int, default=0, help="zero-based audio track, as in video-use")
    ap.add_argument("--num-speakers", type=int, help="accepted for video-use compatibility; ignored (no diarization)")
    ap.add_argument("--force", action="store_true", help="re-transcribe even if the transcript exists")
    a = ap.parse_args()

    lang = a.language.lower().split("-")[0].split("_")[0] if a.language else None
    engine = a.engine
    if engine == "auto":
        engine = "parakeet" if lang is None or lang in PARAKEET_LANGS else "whisper"
    elif engine == "parakeet" and lang and lang not in PARAKEET_LANGS:
        print(f"warning: Parakeet doesn't cover '{lang}'; use --engine whisper", file=sys.stderr)

    failed = 0
    for f in collect(a.inputs):
        try:
            transcribe_one(f, (a.edit_dir or f.parent / "edit").resolve(), engine, lang, a.whisper_model,
                           a.audio_track, a.force)
        except Exception as exc:  # keep going through a folder; report at the end
            failed += 1
            print(f"FAILED {f.name}: {exc}", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
