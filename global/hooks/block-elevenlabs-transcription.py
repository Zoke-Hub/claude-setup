#!/usr/bin/env python3
"""PreToolUse guard: the user never wants transcription to run on ElevenLabs. Python port of
block-elevenlabs-transcription.sh (same rules), registered on Windows where bash/jq may be missing; it also covers the
PowerShell tool. Blocks running video-use's ElevenLabs Scribe helpers, direct ElevenLabs speech-to-text calls, and the
ElevenLabs connector's transcribe tool. Reading or grepping the helper files is still allowed. Standard library only."""
import json, re, sys

def deny(why):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": f"Blocked: transcription must never run on ElevenLabs ({why}). Transcribe locally "
        "instead: media-use's transcribe.mjs (Parakeet), 'npx hyperframes transcribe', or whisper-cli."}}))
    sys.exit(0)

try: data = json.loads(sys.stdin.read() or "{}")
except ValueError: sys.exit(0)
tool, cwd = data.get("tool_name") or "", data.get("cwd") or ""
if re.fullmatch(r"mcp__.*__creative_transcribe_audio", tool): deny("ElevenLabs connector transcribe tool")
if tool not in ("Bash", "PowerShell"): sys.exit(0)
cmd = ((data.get("tool_input") or {}).get("command") or "").replace("\\", "/")      # Windows paths -> forward slashes

# Running the helpers with a Python interpreter, or as an executable at command position.
if (re.search(r"(python[0-9.]*(\.exe)?|py(\.exe)?|uv run)[^;&|]*helpers/transcribe(_batch)?\.py", cmd)
        or re.search(r"(^|[;&|(]\s*)(\./)?(\S*/)?helpers/transcribe(_batch)?\.py", cmd)):
    deny("video-use helpers/transcribe*.py")
# Same, from inside video-use (or its helpers folder) with a bare script name or an import.
if "video-use" in f"{cwd} {cmd}".replace("\\", "/") and re.search(
        r"(python[0-9.]*(\.exe)?|py(\.exe)?|uv run)[^;&|]*(^|[\s/])transcribe(_batch)?\.py|(from|import)\s+transcribe(_batch)?(\s|$|;)", cmd):
    deny("video-use transcribe helper")
# Direct ElevenLabs speech-to-text (curl, SDK, scripts).
if re.search(r"elevenlabs\.io/v[0-9]+/speech-to-text|elevenlabs.*speech[_-]to[_-]text|speech[_-]to[_-]text.*elevenlabs", cmd, re.I):
    deny("ElevenLabs speech-to-text API")
sys.exit(0)
