#!/bin/zsh
# ae_run.sh <script.jsx> [--timeout seconds] [--set name=value]...
# The only way to run a script in After Effects. Errors come back here as text, never as a dialog someone has to click.
# Exit codes: 0 finished · 1 the script reported an error (printed) · 3 AE isn't open or an earlier script is still running · 4 AE didn't finish in time.
# On 3 or 4 AE is most likely showing a dialog or stuck on a render: stop and ask the person, don't wait or retry.
HERE="${0:A:h}"; JSX="${1:A}"; shift; T=120; typeset -a SETS
while [ $# -gt 0 ]; do case "$1" in --timeout) T="$2"; shift 2;; --set) SETS+=("$2"); shift 2;; *) echo "unknown option $1"; exit 2;; esac; done
[ -f "$JSX" ] || { echo "no such script: $JSX"; exit 2; }
# alert(), confirm() and prompt() always stop AE for a click, whatever else is suppressed: refuse them unless a quiet flag guards them
bad=$(grep -nE '(^|[^.A-Za-z_$])(alert|confirm|prompt)[[:space:]]*\(' "$JSX" | grep -v -e '__AE_QUIET' -e '__MAPS_QUIET' -e '^[0-9]*:[[:space:]]*//')
[ -z "$bad" ] || { echo "REFUSED: this script would stop AE on a dialog:"; echo "$bad" | cut -c1-140; exit 2; }
# app.newProject() on unsaved work opens a Save box: use $.global.__AE_NEW_PROJECT() from ae_safe.jsx, or check P.dirty on that line
raw=$(grep -n 'app\.newProject' "$JSX" | grep -v -e 'dirty' -e '^[0-9]*:[[:space:]]*//')
[ -z "$raw" ] || { echo "REFUSED: use \$.global.__AE_NEW_PROJECT() instead, it can't open a Save box:"; echo "$raw" | cut -c1-140; exit 2; }
APP=$(ls -d /Applications/Adobe\ After\ Effects\ 20*/Adobe\ After\ Effects\ 20*.app 2>/dev/null | sort | tail -1); NAME="${APP:t:r}"
[ -n "$NAME" ] || { echo "After Effects isn't installed here"; exit 2; }
WORK=$(mktemp -d "${TMPDIR:-/tmp}/ae_run.XXXXXX"); LOG="$WORK/log.txt"; BOOT="$WORK/boot.jsx"; touch "$LOG"
# Never ping AE with a script: a second script while one is waiting raises its own warning dialog. A lock says one is still running.
PID=$(pgrep -f 'MacOS/After Effects$' | head -1)
[ -n "$PID" ] || { echo "AE_NOT_OPEN: $NAME isn't running. Ask the person to open it."; exit 3; }
LOCK="${TMPDIR:-/tmp}/ae_run.lock"
if [ -f "$LOCK" ] && [ "$(cut -d' ' -f1 "$LOCK")" = "$PID" ]; then echo "AE_BUSY: an earlier script hasn't finished ($(cut -d' ' -f2- "$LOCK")). AE may be waiting on a dialog. Nothing was sent. Ask the person to check it."; exit 3; fi
print -r -- "$PID $JSX" > "$LOCK"
{ for s in "${SETS[@]}"; do print -r -- "\$.global.${s%%=*} = ${s#*=};"; done
  print -r -- "\$.global.__AE_TARGET = \"$JSX\"; \$.global.__AE_LOG = \"$LOG\"; \$.global.__AE_LOCK = \"$LOCK\";"
  print -r -- "\$.evalFile(new File(\"$HERE/ae_safe.jsx\"));"; } > "$BOOT"
osascript -e "with timeout of $T seconds" -e "tell application \"$NAME\" to DoScriptFile \"$BOOT\"" -e 'end timeout' >/dev/null 2>"$WORK/err.txt"
rc=$?; cat "$LOG"
if [ $rc -ne 0 ] || ! grep -q -e '^FINISHED' -e '^ERROR ' "$LOG"; then echo "AE_TIMEOUT: the script didn't finish within $T s. AE is probably showing a dialog or stuck on a render. Stop and ask the person."; exit 4; fi
grep -q '^ERROR ' "$LOG" && exit 1
exit 0
