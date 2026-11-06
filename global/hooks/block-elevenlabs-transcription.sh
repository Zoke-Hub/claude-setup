#!/bin/bash
# PreToolUse guard: the user never wants transcription to run on ElevenLabs.
# Blocks running video-use's ElevenLabs Scribe helpers, direct ElevenLabs
# speech-to-text calls, and the ElevenLabs connector's transcribe tool.
# Reading or grepping the helper files is still allowed.
input=$(cat)
tool=$(printf '%s' "$input" | jq -r '.tool_name // empty')
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty')

deny() {
  jq -n --arg r "Blocked: transcription must never run on ElevenLabs ($1). Transcribe locally instead: media-use's transcribe.mjs (Parakeet), 'npx hyperframes transcribe', or whisper-cli." \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
}

case "$tool" in
  mcp__*__creative_transcribe_audio) deny "ElevenLabs connector transcribe tool" ;;
  Bash) ;;
  *) exit 0 ;;
esac

cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

# Running the helpers with a Python interpreter, or as an executable at command position.
if printf '%s' "$cmd" | grep -Eq '(python[0-9.]*|uv run)[^;&|]*helpers/transcribe(_batch)?\.py' ||
   printf '%s' "$cmd" | grep -Eq '(^|[;&|(][[:space:]]*)(\./)?([^[:space:]]*/)?helpers/transcribe(_batch)?\.py'; then
  deny "video-use helpers/transcribe*.py"
fi
# Same, from inside video-use (or its helpers folder) with a bare script name or an import.
if printf '%s %s' "$cwd" "$cmd" | grep -q 'video-use' &&
   printf '%s' "$cmd" | grep -Eq '(python[0-9.]*|uv run)[^;&|]*(^|[[:space:]/])transcribe(_batch)?\.py|(from|import)[[:space:]]+transcribe(_batch)?([[:space:]]|$|;)'; then
  deny "video-use transcribe helper"
fi
# Direct ElevenLabs speech-to-text (curl, SDK, scripts).
if printf '%s' "$cmd" | grep -Eiq 'elevenlabs\.io/v[0-9]+/speech-to-text|elevenlabs.*speech[_-]to[_-]text|speech[_-]to[_-]text.*elevenlabs'; then
  deny "ElevenLabs speech-to-text API"
fi
exit 0
