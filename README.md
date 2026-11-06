# Claude setup pack

A ready-made setup for Claude Code, by Zoke, for video and motion-graphics work on macOS or Windows. One message to
Claude installs it: house rules and notes for how Claude works, a set of skills, local transcription, a cut-out tool,
and, if you want them, three tools from [Zoke-Hub/claude-tools](https://github.com/Zoke-Hub/claude-tools).

## Install

Open Claude Code (the desktop app's Code tab, or `claude` in a terminal) and send:

```
Set up this computer with https://github.com/Zoke-Hub/claude-setup: read its PROMPT.md and follow it.
```

Claude downloads the pack, checks the computer's tools, asks a few questions (which languages to transcribe, whether you
want the Higgsfield skills, which of the three tools to install), installs everything and ends with a report. Nothing
is tied to a project folder: it all works in any project. Running it again later updates the setup and keeps any
changes you've made.

## What it sets up

- **Rules and house notes** in `~/.claude`: how Claude plans, builds, checks and hands over video and animation work.
  Install shows them to you and asks which apply.
- **A safety hook** that stops speech from being sent to ElevenLabs for transcription: speech is turned into text on
  your own computer.
- **Skills:**
  - **animation, logo-recreation, cutout, chat-archive, local-transcribe and earshot**, by Zoke;
  - **HeyGen's hyperframes skills and media-use**, for videos made from code;
  - **motion-broll, object-separation, three explainer styles and sound-effects**;
  - **real-sfx**, for real recorded sound effects;
  - **13 UI and UX design skills**;
  - **the Higgsfield skills**, if you want them (they need a Higgsfield account).
- **Local tools:**
  - a cut-out model (BiRefNet HR);
  - Parakeet speech-to-text, with Whisper large-v3 if you choose other languages;
  - video-use for editing raw footage;
  - the free Fetch MCP for reading web pages.
- **Folio, PulseWise and MarkRoom**, if you pick them, installed from
  [Zoke-Hub/claude-tools](https://github.com/Zoke-Hub/claude-tools).

## Where the skills come from

This repository carries the setup's own files and the third-party skills whose licences allow it, each with its own
`LICENSE`:
- HeyGen's retired hyperframes skills and motion-graphics also carry a `SOURCE.md`.
- These come straight from their makers' repositories while setup installs, at the version this pack was checked with.
  Every file is checked before it's installed.
  - real-sfx, from [Clipwing/skills](https://github.com/Clipwing/skills);
  - HeyGen's current hyperframes, hyperframes-cli, hyperframes-registry and media-use, from
    [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes);
  - the optional Higgsfield skills, from [higgsfield-ai/skills](https://github.com/higgsfield-ai/skills).

## What it needs

- **A computer:** macOS or Windows 10/11.
- **Claude Code:** the Claude desktop app for PulseWise and Folio.
- **Internet and disk:** setup installs what's missing (Python 3.12, ffmpeg, Node, uv and a few more) with Homebrew or
  winget. The downloads come to a few GB, mostly the cut-out and speech models.

## Licence

The setup pack's own files are © 2026 Zoke under the [Use and Share Licence](LICENSE): free to use, paid work included,
and to share unchanged; your installed copy is yours to adjust. The third-party skills keep their own licences.

Pack version 2026-11-06.073618.
