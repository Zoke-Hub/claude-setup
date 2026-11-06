#!/bin/bash
# Claude setup pack: first step on a Mac. Checks Homebrew, then every tool the pack needs, and installs what's
# missing. Plain bash (macOS bash 3.2), no Python needed: run it before sync.py.
#
#   bash bootstrap-mac.sh             # check only: lists what is missing, changes nothing
#   bash bootstrap-mac.sh --install   # also install the missing tools with Homebrew
#
# Exit codes: 0 = everything ready, 1 = tools missing (run with --install), 2 = Homebrew or Apple's command-line tools
# missing (only the user can install those: they ask for the user's password or a click).

INSTALL=0; [ "$1" = "--install" ] && INSTALL=1
say() { printf '%s\n' "$*"; }
ok() { printf '  [ok] %-34s %s\n' "$1" "$2"; }
no() { printf '  [--] %-34s %s\n' "$1" "$2"; }

[ "$(uname)" = "Darwin" ] || { say "This script is for macOS. On Windows, see SETUP.md step 3."; exit 2; }
say "Claude setup pack: Mac bootstrap (macOS $(sw_vers -productVersion), $(uname -m))"
say ""

# ---------------------------------------------------------------- 1. Homebrew (everything else comes from it)
BREW="$(command -v brew)"
for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -z "$BREW" ] && [ -x "$b" ] && BREW="$b"; done
if [ -z "$BREW" ]; then
  say "HOMEBREW IS NOT INSTALLED. Only the user can install it (it asks for their Mac password)."
  say ""
  say "Ask the user to do this:"
  say "  1. Open the Terminal app (Applications > Utilities > Terminal)."
  say "  2. Paste this line and press Return:"
  say '       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  say "  3. Type their Mac login password when asked (nothing shows while typing), press Return, and press Return"
  say "     again to confirm. It also installs Apple's command-line tools. It takes 5-15 minutes."
  say "  4. When it finishes, it prints 'Next steps' with two commands. Paste and run those too, so 'brew' works in"
  say "     new terminals. On Apple silicon they are:"
  say "       echo 'eval \"\$(/opt/homebrew/bin/brew shellenv)\"' >> ~/.zprofile"
  say '       eval "$(/opt/homebrew/bin/brew shellenv)"'
  say "  5. Say 'done', then run this script again."
  exit 2
fi
eval "$("$BREW" shellenv)"                        # brew and its tools on PATH for the rest of this script
ok "Homebrew" "$("$BREW" --version | head -1)"
if [ -z "$(env -i HOME="$HOME" TERM=dumb /bin/zsh -lic 'command -v brew' 2>/dev/null)" ]; then   # does a new terminal find it?
  say "       note: brew isn't set up for new terminals; run once:"
  say "       echo 'eval \"\$($BREW shellenv)\"' >> ~/.zprofile"
fi
if xcode-select -p >/dev/null 2>&1; then ok "Apple command-line tools" "$(xcode-select -p)"
else
  no "Apple command-line tools" ""
  say ""
  say "Ask the user to run  xcode-select --install  in Terminal and click Install in the window that opens"
  say "(about 5 minutes), then run this script again."
  exit 2
fi

# ---------------------------------------------------------------- 2. the tools (name | check | brew formula | why)
FORMULAE=""; CASKS=""
need() { FORMULAE="$FORMULAE $1"; }
ffmpeg_full_ok() { local f="$(brew --prefix)/opt/ffmpeg-full/bin/ffmpeg"; [ -x "$f" ] && "$f" -hide_banner -filters 2>/dev/null | grep -q drawtext && "$f" -hide_banner -filters 2>/dev/null | grep -q subtitles; }

say ""
say "TOOLS"
check() {  # label, command to test, formula, why
  if eval "$2" >/dev/null 2>&1; then ok "$1" "$4"; else no "$1" "brew install $3   ($4)"; need "$3"; fi
}
check "git"                      "command -v git"                 git          "video-use clone"
check "node + npx"               "command -v node && command -v npx" node      "hyperframes, markroom, explainers"
check "python3.12"               "command -v python3.12"          python@3.12  "sync.py, every skill script, venvs (macOS python3 is 3.9)"
check "uv"                       "command -v uv"                  uv           "venvs: cut-out, video-use"
check "jq"                       "command -v jq"                  jq           "the ElevenLabs block hook"
check "ffmpeg + ffprobe"         "command -v ffmpeg && command -v ffprobe" ffmpeg "renders, frame checks, transcription audio"
check "ffmpeg-full (keg-only)"   "ffmpeg_full_ok"                 ffmpeg-full  "drawtext, subtitles, zscale for video-use renders"
check "yt-dlp (+ deno)"          "command -v yt-dlp"              yt-dlp       "watch skill: downloading videos"
if [ -d "/Applications/Google Chrome.app" ] || [ -d "$HOME/Applications/Google Chrome.app" ]; then ok "Google Chrome" "headless stills, logo PNGs"
else no "Google Chrome" "brew install --cask google-chrome   (headless stills, logo PNGs)"; CASKS="google-chrome"; fi

if [ -z "$FORMULAE$CASKS" ]; then
  say ""; say "READY: Homebrew and every tool are installed. Next: ask which languages to transcribe, then python3.12 sync.py install (SETUP.md steps 3-4)"
  exit 0
fi

say ""
if [ $INSTALL -eq 0 ]; then
  say "MISSING:${FORMULAE}${CASKS:+ (cask) $CASKS}"
  say "Run  bash bootstrap-mac.sh --install  to install them with Homebrew (a few minutes; no password for formulae)."
  exit 1
fi

# ---------------------------------------------------------------- 3. install
[ -n "$FORMULAE" ] && { say "Installing:$FORMULAE"; brew install $FORMULAE || say "brew install reported an error (see above)."; }
if [ -n "$CASKS" ]; then
  say "Installing Google Chrome"
  if ! brew install --cask $CASKS; then
    say ""
    say "Chrome didn't install from here (it may need the user's password). Ask the user to either:"
    say "  - run  brew install --cask google-chrome  in Terminal and type their password, or"
    say "  - download it from https://www.google.com/chrome/ and drag it into Applications."
  fi
fi
say ""
say "Re-checking..."
exec bash "$0"
