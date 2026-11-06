#!/usr/bin/env python3
"""Claude setup pack: install and check (stdlib only; macOS, Linux, Windows).

  python3 sync.py check                    # report what is missing or different; changes nothing
  python3 sync.py install                  # install / update everything, backing up what it replaces
  python3 sync.py install --cutout-env     # also build the shared cut-out venv (~/.claude/venvs/cutout) + BiRefNet HR
  python3 sync.py install --parakeet       # also install Parakeet for local transcription (~640 MB)
  python3 sync.py install --transcription english        # languages rule: English (+ European) only, Parakeet
  python3 sync.py install --transcription multilingual   # also Hindi etc.: Whisper large-v3 (~3 GB more, fetched now)
  python3 sync.py install --higgsfield yes|no            # the optional higgsfield skills (MANIFEST "optional_skills");
                                                         # left out, they stay as they are (updated only where installed)
  python3 sync.py cleanup                  # list old duplicates/leftovers; add --yes to remove them
  python3 sync.py install --owner-code '<code>'   # the owner's own edition (owner.bin); give the same code to every command
  python3 sync.py unlock --owner-code '<code>'    # open the owner's edition right after unzipping (OWNER.md says what next)
  python3 sync.py strip-owner --zip "<the zip>"   # after a general install: take owner.bin out of the zip and this folder
  python3 sync.py tools                    # MarkRoom, PulseWise and Folio here: from this pack's folders, from GitHub, or not installed
  python3 sync.py tools --install folio,markroom   # the git edition: install the ones the user ticked, from GitHub
Everything is machine-wide (~/.claude); no project folder is needed. --project "<folder>" is optional: it adds that
folder's leftovers to the cleanup and lets --cutout-env reuse an old <folder>/.cutout venv.

What the pack holds (MANIFEST.json lists every file with its sha256):
  global/CLAUDE.md                -> merged into ~/.claude/CLAUDE.md (the "# Global rules" block)
  global/CLAUDE-sections-mac.md   -> on macOS only: its top-level sections are added to ~/.claude/CLAUDE.md if missing
  global/hooks/*                  -> ~/.claude/hooks/   + the PreToolUse hook and deny rule merged into ~/.claude/settings.json
  skills/<name>/...               -> ~/.claude/skills/<name>/...   (video-use is cloned from GitHub, never copied: it holds a key)
                                     seed skills (MANIFEST "seed_skills") are installed only where missing, never replaced
  extras/video-use-windows-paths.patch -> applied to the video-use clone (keeps every machine's clone identical)
  MANIFEST "downloads"            -> the git edition's third-party skills (real-sfx, HeyGen's current skills, Higgsfield's):
                                     not in the pack. `install` fetches each from its own repo at the commit the pack was
                                     built with, into the pack folder, checks every file against MANIFEST, then installs
                                     them like the pack's own files (a failed download is reported; the rest installs)
  Fetch MCP (mcp-server-fetch)    -> user-level MCP server "fetch" in ~/.claude.json (run with uvx; free, local)
  global/house/*.md               -> ~/.claude/house/   (general working notes; CLAUDE.md says when to read each)
  global/mods/...                 -> ~/.claude/mods/      (the PulseWise progress bar and the Folio archive; loaded in every
                                     chat through two env lines in ~/.claude/settings.json, plus the "local-mods" marketplace)
  The three tools (MarkRoom, PulseWise, Folio) are optional. A zip setup file carries them as folders; the git edition
  carries none and `tools --install` puts the ticked ones in from GitHub (MANIFEST "tool_source"). Where a tool is already
  installed as a plugin from GitHub, its folder copy is never installed and an older one is moved to the backup, with its
  settings line, so it can't load twice. The owner's edition keeps the folders, its working copies, and never does this.
  global/house-private/*.md       -> ~/.claude/house-private/  (the owner's edition only: their private notes)
  global/setup-pack/...           -> ~/.claude/setup-pack/  (the builder: make_pack.py builds this computer's own setup file)
  owner.bin                       -> the owner's own edition, locked with their code: the files that differ from the general
                                     pack, its own MANIFEST.json and OWNER.md. Only --owner-code opens it; a wrong or missing
                                     code leaves the general pack as it is.
  global/ae-presets/unfold/...    -> ~/.claude/ae-presets/unfold/  (owner's edition only: the Unfold text presets for After
                                     Effects; installed into AE only on a yes: `sudo zsh install_presets.sh` on a Mac, by hand on Windows)
  MANIFEST "retired_folders"      -> ~/.claude folders an older general pack installed (Unfold); a general `install` moves them to the backup
  MANIFEST "retired_skills"       -> skills merged into others; `install` moves them to the backup
  MANIFEST "retired_house_notes"  -> notes older packs installed; `install` moves them to ~/.claude/house-private/
  MANIFEST "replaced_house_notes" -> notes an older pack installed under an old name; `install` moves them to the backup
  MANIFEST "retired_mods"         -> mods an older pack installed under an old name; `install` moves them to the backup
  Older setup zips in Downloads / Desktop also go to the backup on `install`: the setup leaves no older version behind.
Anything replaced is copied first to ~/.claude/sync-backups/<time>/. Run `check` again at the end: it must say IN SYNC.

An update never undoes what the person changed or added. Each install records what it wrote (~/.claude/setup-pack/
installed.json), and earlier.json carries the fingerprint of every file any earlier setup file shipped. Only a file
that is still exactly as a setup file wrote it is updated. A file the person changed stays as it is: the pack's new
version goes to ~/.claude/setup-pack/updates/<version>/ and the report lists it, to merge by hand or with Claude. A
pack file the person removed stays removed. The rules block in CLAUDE.md is merged line by line, keeping the person's
lines. Clean-up moves only what an earlier setup file installed and nobody changed; anything else is listed for the
person to decide (`cleanup --move <path>`). settings.json only gains or updates the pack's own entries. The tools' data
(Folio's ~/.claude/folio, PulseWise's jobs and history, MarkRoom boards in projects) is never touched. The owner's
edition updates as before: there the setup's files are the owner's own working copies.
"""
import argparse, difflib, hashlib, hmac, io, json, os, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parent
HOME = Path.home()
CLAUDE = HOME / ".claude"

# --- owner lock (make_pack.py runs this block too, so both use the same code) ---
OWNER_FILE = "owner.bin"
OWNER_MAGIC = b"CSPOWN1\n"

def owner_keys(code, salt, rounds):
    k = hashlib.pbkdf2_hmac("sha256", code.encode("utf-8"), salt, rounds, dklen=64)
    return k[:32], k[32:]

def owner_stream(key, nonce, n):
    out = bytearray()
    for i in range((n + 31) // 32):
        out += hmac.new(key, nonce + i.to_bytes(8, "big"), "sha256").digest()
    return bytes(out[:n])

def owner_xor(a, b):
    return (int.from_bytes(a, "big") ^ int.from_bytes(b, "big")).to_bytes(len(a), "big")

def owner_lock(data, code, rounds=600000):
    salt, nonce = os.urandom(16), os.urandom(16)
    ek, mk = owner_keys(code, salt, rounds)
    head = OWNER_MAGIC + rounds.to_bytes(4, "big") + salt + nonce
    body = owner_xor(data, owner_stream(ek, nonce, len(data)))
    return head + body + hmac.new(mk, head + body, "sha256").digest()

def owner_unlock(blob, code):
    """the locked files (a zip) when the code is exactly right, else None"""
    h = len(OWNER_MAGIC)
    if not blob.startswith(OWNER_MAGIC) or len(blob) < h + 68: return None
    rounds, salt, nonce = int.from_bytes(blob[h:h + 4], "big"), blob[h + 4:h + 20], blob[h + 20:h + 36]
    head, body, tag = blob[:h + 36], blob[h + 36:-32], blob[-32:]
    ek, mk = owner_keys(code, salt, rounds)
    if not hmac.compare_digest(hmac.new(mk, head + body, "sha256").digest(), tag): return None
    return owner_xor(body, owner_stream(ek, nonce, len(body)))
# --- end owner lock ---

def owner_open(code):
    """unlock owner.bin into this folder (the owner's files, MANIFEST.json and OWNER.md): True when the code fits"""
    p = PACK / OWNER_FILE
    data = owner_unlock(p.read_bytes(), code) if p.exists() else None
    if data is None: return False
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            q = (PACK / n).resolve()
            if PACK not in q.parents: continue
            q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(z.read(n))
    return True

_code = next((sys.argv[i + 1] for i, x in enumerate(sys.argv[:-1]) if x == "--owner-code"), None) or \
        next((x.split("=", 1)[1] for x in sys.argv if x.startswith("--owner-code=")), None)
if _code is not None:
    print("Owner's own edition: unlocked." if owner_open(_code) else "General pack.")
MANIFEST = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
STAMP = time.strftime("%Y%m%d-%H%M%S")
BACKUP = CLAUDE / "sync-backups" / STAMP
RULES_MARK = "# Global rules"
VERBOSE = "--verbose" in sys.argv
VIDEO_USE = "https://github.com/browser-use/video-use"
# the pack's mods (PulseWise, Folio), each loaded in every chat from its folder (env CLAUDE_CODE_PLUGIN_DIRS)
MODS = [CLAUDE / "mods" / m for m in sorted({Path(r).parts[2] for r in MANIFEST["files"] if r.startswith("global/mods/")} - {".claude-plugin"})]
OLD_MODS = [CLAUDE / "mods" / m for m in MANIFEST.get("retired_mods", [])]   # an older pack's names (Pulse)
# the three tools, each optional: where its files sit in the pack, and its folder here
TOOLS = {"folio": ("global/mods/folio/", CLAUDE / "mods" / "folio"),
         "pulsewise": ("global/mods/pulsewise/", CLAUDE / "mods" / "pulsewise"),
         "markroom": ("skills/markroom/", CLAUDE / "skills" / "markroom")}
TOOL_NAMES = {"folio": "Folio", "pulsewise": "PulseWise", "markroom": "MarkRoom"}
TOOL_SOURCE = MANIFEST.get("tool_source")             # the git edition: {"repo", "marketplace", "tools"}; a zip has none
OWNER_ED = MANIFEST.get("edition") == "personal"      # the owner's computers: the folders are the working copies

def plugin_tools():
    """the three tools installed as plugins from a marketplace (GitHub), not loaded from their folders"""
    found = set()
    for f, key in ((CLAUDE / "settings.json", "enabledPlugins"), (CLAUDE / "plugins" / "installed_plugins.json", "plugins")):
        try: ids = json.loads(f.read_text(encoding="utf-8")).get(key) or {}
        except (OSError, ValueError, AttributeError): ids = {}
        for k in ids:
            name, _, market = str(k).partition("@")
            if name in TOOLS and market and market != "local-mods": found.add(name)
    return found

PLUGIN_TOOLS = set() if OWNER_ED else plugin_tools()   # their folder copies are never installed (they'd load twice)
SKIP_PREFIXES = tuple(TOOLS[t][0] for t in PLUGIN_TOOLS)
MODS = [m for m in MODS if m.name not in PLUGIN_TOOLS]

def tool_file(rel):
    """a pack file of a tool this computer has from GitHub instead"""
    return bool(SKIP_PREFIXES) and rel.startswith(SKIP_PREFIXES)

def tool_state(t, plugins=None):
    plugins = plugin_tools() if plugins is None else plugins
    if t in plugins and not OWNER_ED: return "installed from GitHub (plugin)"
    if TOOLS[t][1].exists(): return "installed as a folder" + (" (the working copy)" if OWNER_ED else " (from a setup file)")
    return "not installed"
CUTOUT = CLAUDE / "venvs" / "cutout"           # shared by every project (the cutout skill, markroom's Pillow)
MODELS = ["ZhengPeng7/BiRefNet_HR"]          # HR-matting lost the side-by-side test; --model hr-matting fetches it on demand
IS_MAC = sys.platform == "darwin"
IS_WIN = os.name == "nt"
SECTIONS_MAC = "global/CLAUDE-sections-mac.md"
SECTIONS_WIN = "global/CLAUDE-sections-windows.md"
SECTION_FILES = {SECTIONS_MAC, SECTIONS_WIN}
MY_SECTIONS = SECTIONS_MAC if IS_MAC else SECTIONS_WIN if IS_WIN else None   # Linux: rules block only
CUT_HEAD = "# Cut-out settings"                    # per machine, written from the cut-out machine check; never synced
LANG_HEAD = "# Transcription languages"            # per machine, chosen by the user at setup; never synced between machines
LANG_TEXT = {
    "english": "- **This machine: English only** (chosen at setup). Transcribe with Parakeet TDT 0.6B v3 (English and the "
               "other European languages it covers). Don't download Whisper large-v3 and don't run local-transcribe with "
               "`--language hi` or `--engine whisper`. If a clip is in Hindi or another language Parakeet doesn't cover, say "
               "so and ask the user whether to switch this machine to multilingual (`sync.py install --transcription "
               "multilingual`, about 3 GB more).",
    "multilingual": "- **This machine: multilingual** (chosen at setup). English and the other European languages: Parakeet "
               "TDT 0.6B v3. Hindi, Malayalam, Tamil or any other language: `local_transcribe.py --language <code>` "
               "(Whisper large-v3 through whisper.cpp, downloaded at setup). If you don't know a clip's language, ask "
               "before transcribing: Parakeet produces nonsense on languages it doesn't cover.",
}
HOOK_SH = "block-elevenlabs-transcription.sh"     # macOS / Linux: bash + jq
HOOK_PY = "block-elevenlabs-transcription.py"     # Windows: same rules in Python, also covers the PowerShell tool
PATCH = "extras/video-use-windows-paths.patch"
SEEDS = MANIFEST.get("seed_skills", [])
CUTOUT_PKGS = ["torch", "transformers>=4.57,<5", "timm", "kornia", "einops", "opencv-python", "pillow", "numpy"]

def load_json(p, default):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError): return default

REC_FILE = CLAUDE / "setup-pack" / "installed.json"          # what the last install wrote, per pack path
REC = load_json(REC_FILE, {})
EARLIER = load_json(PACK / "earlier.json", {"files": {}, "blocks": {}})   # every earlier setup file's fingerprints
UPDATES = CLAUDE / "setup-pack" / "updates" / MANIFEST["version"]          # new versions of files the person changed
KEPT, REMOVED_KEPT, ASK_OK = [], [], set()

def known(rel, h):
    """a setup file wrote exactly this content at this path (this pack, the last install, or an earlier pack)"""
    return h == MANIFEST["files"].get(rel) or h == REC.get("files", {}).get(rel) or h in EARLIER.get("files", {}).get(rel, [])

def untouched_tree(prefix, path):
    """every file in an installed folder is still as a setup file wrote it (generated typings and caches aside)"""
    for f in path.rglob("*"):
        if not f.is_file() or any(x in f.parts for x in ("__pycache__", ".DS_Store", "node_modules")) or ".claude-plugin/types" in f.as_posix(): continue
        if f.name == ".DS_Store": continue
        if not known(prefix + f.relative_to(path).as_posix(), sha(f)): return False
    return True

def park(rel):
    """the pack's new version of a file the person changed or removed: set apart for them to merge"""
    q = UPDATES / rel
    q.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(PACK / rel, q)
    return q

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def slug(project):
    return re.sub(r"[^A-Za-z0-9]", "-", str(project))

def dest(rel, project):
    parts = Path(rel).parts
    if parts[0] == "global" and parts[1] == "hooks": return CLAUDE / "hooks" / Path(*parts[2:])
    if parts[0] == "global": return CLAUDE / Path(*parts[1:])
    if parts[0] == "skills": return CLAUDE / "skills" / Path(*parts[1:])
    if parts[0] == "memory" and project: return CLAUDE / "projects" / slug(project) / "memory" / Path(*parts[1:])
    if parts[0] == "project" and project: return project / Path(*parts[1:])
    return None                                                    # extras/: used in place, never copied

OPTIONAL = MANIFEST.get("optional_skills", {})                  # skill groups set up only on a yes (higgsfield)
OPT_CHOICE = {}                                                   # this run's answers: {group: True/False}

def opt_on(group):
    """an optional group goes in on a yes; with no answer, it stays as it is (updated where it is already installed)"""
    if OPT_CHOICE.get(group) is not None: return OPT_CHOICE[group]
    return any((CLAUDE / "skills" / n).exists() for n in OPTIONAL.get(group, []))

def opt_skip(rel):
    """a file of an optional skill this computer doesn't take"""
    parts = Path(rel).parts
    return len(parts) > 1 and parts[0] == "skills" and any(parts[1] in n and not opt_on(g) for g, n in OPTIONAL.items())

def seeded(rel):
    """a file of a seed skill that is already installed here, or a seed file (a skill's own settings, e.g. real-sfx's
    sound libraries) that already exists here: this machine's own copy wins, on every edition"""
    parts = Path(rel).parts
    if rel in MANIFEST.get("seed_files", []) and dest(rel, None) and dest(rel, None).exists(): return True
    return parts[0] == "skills" and parts[1] in SEEDS and (CLAUDE / "skills" / parts[1]).exists() and not SEED_NEW.get(parts[1])

SEED_NEW = {}                                                      # seed skills this run is installing (absent at start)

def sections(text):
    """top-level '# ' sections of a markdown file: {heading line: section text}"""
    out, cur = {}, None
    for line in text.splitlines(keepends=True):
        if re.match(r"# (?!#)", line): cur = line.strip(); out[cur] = ""
        if cur: out[cur] += line
    return out

def missing_sections(cur):
    """this OS's own CLAUDE.md sections (after the rules block) that the file doesn't have yet"""
    if not MY_SECTIONS or not (PACK / MY_SECTIONS).exists(): return {}
    return {h: s for h, s in sections((PACK / MY_SECTIONS).read_text(encoding="utf-8")).items() if h not in (cur or "")}

def lang_choice():
    """which transcription-languages rule this machine has: 'english', 'multilingual', 'custom' or None"""
    cm = CLAUDE / "CLAUDE.md"
    sec = sections(cm.read_text(encoding="utf-8")).get(LANG_HEAD) if cm.exists() else None
    if sec is None: return None
    return next((k for k in LANG_TEXT if "This machine: " + ("English only" if k == "english" else "multilingual") in sec), "custom")

def set_lang(choice):
    cm = CLAUDE / "CLAUDE.md"
    cur = cm.read_text(encoding="utf-8") if cm.exists() else ""
    secs = sections(cur)
    if LANG_HEAD in secs: cur = cur.replace(secs[LANG_HEAD], "")
    backup(cm); cm.parent.mkdir(parents=True, exist_ok=True)
    cm.write_text(cur.rstrip() + "\n\n" + LANG_HEAD + "\n\n" + LANG_TEXT[choice] + "\n", encoding="utf-8")

def cutout_probe():
    """run the cut-out machine check (GPU / RAM -> precision, working size, memory cap), save it in the venv's machine.json
    and write this machine's "# Cut-out settings" section of CLAUDE.md from it. Returns the one-line summary."""
    py, probe = venv_py(CUTOUT), CLAUDE / "skills/cutout/scripts/probe_machine.py"
    if not (py.exists() and probe.exists()): return "skipped (no cut-out venv or skill)"
    r = run([str(py), str(probe), "--json"], timeout=300)
    if not (r and r.returncode == 0): return "FAILED " + ((r.stderr or "")[-600:] if r else "")
    p = json.loads(r.stdout[r.stdout.index("{"):])
    cap = ", with the GPU memory capped at its recommended working set" if p.get("mps_cap") else ""
    line = (f"- **Cut-outs on this machine:** {p['device']}, {p['memory_gb']:g} GB: the cutout skill runs in "
            f"{p['precision']} precision at {p['size']}{cap} (set by the setup's machine check; saved in the cut-out "
            f"venv's machine.json). Run one cut-out at a time, not next to another memory-heavy app; after a hardware "
            f"change run `probe_machine.py` again.")
    cm = CLAUDE / "CLAUDE.md"; cur = cm.read_text(encoding="utf-8") if cm.exists() else ""
    secs = sections(cur)
    if CUT_HEAD in secs: cur = cur.replace(secs[CUT_HEAD], "")
    backup(cm); cm.write_text(cur.rstrip() + "\n\n" + CUT_HEAD + "\n\n" + line + "\n", encoding="utf-8")
    return f"{p['device']}, {p['memory_gb']:g} GB: {p['precision']} precision at {p['size']}"

def whisper_prefetch():
    """download Whisper large-v3 for hyperframes now (about 3 GB) by transcribing one second of silence. Never raises:
    a failed prefetch is reported and the install carries on (the model then downloads on first use)."""
    import tempfile
    npx = which("npx") or which("npx.cmd")
    if not (npx and which("ffmpeg")): return "FAILED: needs npx and ffmpeg (it will download on first use instead)"
    try:
        # the child runs in HOME, not in the temp folder, so nothing holds the folder open when it is removed
        kw = {"ignore_cleanup_errors": True} if sys.version_info >= (3, 10) else {}
        with tempfile.TemporaryDirectory(prefix="csp-", **kw) as t:
            wav = Path(t) / "silence.wav"
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-t", "1", str(wav)], cwd=str(HOME))
            r = run([npx, "-y", "hyperframes", "transcribe", str(wav), "--engine", "whisper", "--model", "large-v3",
                     "--json", "-d", t], timeout=7200, cwd=str(HOME))
        return "Whisper large-v3 ready" if r and r.returncode == 0 else "FAILED " + ((r.stderr or r.stdout)[-600:] if r else "")
    except Exception as e:
        return f"FAILED ({e}); it will download on first use instead"

def short_patch():
    """the patch copied to a short path: under a long unzip folder, git apply failed with 'Filename too long'"""
    import tempfile
    q = Path(tempfile.gettempdir()) / "csp-video-use.patch"
    shutil.copyfile(PACK / PATCH, q)
    return q

def patch_state():
    """'applied', 'pending' (applies cleanly), 'conflict', or None (no clone / no patch)"""
    vu = CLAUDE / "skills/video-use"
    if not (vu / ".git").exists() or not (PACK / PATCH).exists() or not which("git"): return None
    q = short_patch()
    if (r := run(["git", "-C", str(vu), "apply", "--reverse", "--check", str(q)])) and r.returncode == 0: return "applied"
    if (r := run(["git", "-C", str(vu), "apply", "--check", str(q)])) and r.returncode == 0: return "pending"
    return "conflict"

def fetch_cfg():
    cj = HOME / ".claude.json"
    try: return json.loads(cj.read_text(encoding="utf-8")).get("mcpServers", {}).get("fetch") if cj.exists() else None
    except Exception: return None

def fetch_ok():
    """the Fetch MCP is registered and its server starts"""
    c = fetch_cfg()
    if not c: return False
    r = run([c.get("command", "uvx"), *c.get("args", []), "--help"], timeout=300)
    return bool(r and r.returncode == 0)

def install_fetch():
    if fetch_cfg(): return "already set up"
    uvx = which("uvx") or which("uvx.exe")
    if not uvx: return "FAILED: uvx not found (install uv first)"
    run([uvx, "mcp-server-fetch", "--help"], timeout=600)                        # downloads it once
    cl = which("claude")
    if cl:
        r = run([cl, "mcp", "add", "--scope", "user", "fetch", "--", uvx, "mcp-server-fetch"], timeout=120)
        if fetch_cfg(): return "added with `claude mcp add --scope user`"
    cj = HOME / ".claude.json"                                                   # no CLI: merge the entry by hand
    d = json.loads(cj.read_text(encoding="utf-8")) if cj.exists() else {}
    backup(cj)
    d.setdefault("mcpServers", {})["fetch"] = {"type": "stdio", "command": uvx, "args": ["mcp-server-fetch"], "env": {}}
    cj.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    return "added to ~/.claude.json (backed up first)"

def parakeet_ok():
    npx = which("npx") or which("npx.cmd")
    r = npx and run([npx, "-y", "hyperframes", "models", "list"], timeout=300, cwd=str(HOME))
    return bool(r and any(ln.startswith("parakeet") and "installed" in ln and "not installed" not in ln for ln in r.stdout.splitlines()))

# ---------------------------------------------------------------- cleanup: old duplicates and leftovers
def old_version_items():
    """what an older version of this pack installed that this one replaces. `install` clears the ones still exactly as a
    setup file wrote them (moved to the backup, retired notes to ~/.claude/house-private/); anything changed since, and
    anything that isn't the pack's, is listed as 'ask' for the person to decide (the owner's edition clears them all)"""
    items, skills = [], CLAUDE / "skills"
    mine = lambda ok: "move" if OWNER_ED or ok else "ask"
    for name in MANIFEST.get("retired_skills", []):
        p = skills / name
        if p.exists():
            ok = untouched_tree(f"skills/{name}/", p)
            items.append((p, "retired skill, merged into another" + ("" if ok else " (has your changes)"), mine(ok)))
    for name in MANIFEST.get("retired_house_notes", []):              # notes an older pack put in ~/.claude/house
        f = CLAUDE / "house" / f"{name}.md"
        if f.exists():
            ok = known(f"global/house/{name}.md", sha(f))
            items.append((f, "house note this pack no longer ships; kept as a personal note" + ("" if ok else " (has your changes)"),
                          "private" if OWNER_ED or ok else "ask"))
    for name in MANIFEST.get("replaced_house_notes", []):             # renamed notes: the pack ships the new name
        f = CLAUDE / "house" / f"{name}.md"
        if f.exists():
            ok = known(f"global/house/{name}.md", sha(f))
            items.append((f, "house note under its old name (the pack ships it renamed)" + ("" if ok else " (has your changes)"), mine(ok)))
    for rel in ([] if OWNER_ED else MANIFEST.get("retired_folders", [])):   # folders general packs no longer ship (Unfold)
        p = CLAUDE / rel
        if p.exists():
            ok = untouched_tree(f"global/{rel}/", p)
            items.append((p, "folder an older setup file installed that this one no longer ships" + ("" if ok else " (has your changes)"), mine(ok)))
    for name in MANIFEST.get("retired_mods", []):                     # mods an older pack installed under an old name
        p = CLAUDE / "mods" / name
        if p.exists():
            ok = untouched_tree(f"global/mods/{name}/", p)
            items.append((p, "mod under its old name (replaced by the renamed one)" + ("" if ok else " (has your changes)"), mine(ok)))
    for name in sorted(PLUGIN_TOOLS):                                  # a folder copy beside the GitHub plugin would load twice
        p = TOOLS[name][1]
        if p.exists():
            if untouched_tree(TOOLS[name][0], p):
                items.append((p, f"folder copy of {TOOL_NAMES[name]} (the GitHub plugin replaces it)", "tool"))
            else:
                items.append((p, f"folder copy of {TOOL_NAMES[name]} with your changes, beside the GitHub plugin: both load. Ask "
                                 "whether to set the folder aside (`cleanup --move` it) or uninstall the plugin", "ask"))
    mine_v, packs = MANIFEST["version"], set()
    for pat in ("Claude-setup-pack-*.zip", "Claude-*-setup-pack-*.zip"):            # this name and older ones
        for d in (HOME / "Downloads", HOME / "Desktop"): packs |= set(d.glob(pat))
    for z in sorted(packs):
        v = re.search(r"setup-pack-(?:[A-Za-z]+-)?(\d{4}-\d\d-\d\d\.\d+)", z.name)
        if v and v.group(1) < mine_v.split("-no-")[0]: items.append((z, "older setup pack", "move" if OWNER_ED else "ask"))
    return items

def cleanup_items(project):
    """(path, why, action) for things that duplicate something the pack provides. action: 'move' (to the backup
    folder), 'private' (kept in ~/.claude/house-private), 'delete' (a re-downloadable cache) or 'report' (shown only;
    fix by hand). An older version's installs (old_version_items) are listed too, for a cleanup run on its own."""
    items, skills = old_version_items(), CLAUDE / "skills"
    if skills.exists():
        names = {p.name for p in skills.iterdir() if p.is_dir()}
        for p in sorted(skills.iterdir()):
            if not p.is_dir(): continue
            m = re.match(r"(.+?)(?:[ _-](?:copy|old|backup|bak|orig)| \d+|-v\d+)$", p.name, re.I)
            if m and m.group(1) in names: items.append((p, f"old copy of the {m.group(1)} skill", "move" if OWNER_ED else "ask"))
            elif not (p / "SKILL.md").exists() and p.name != "video-use": items.append((p, "skill folder with no SKILL.md", "move" if OWNER_ED else "ask"))
        plug = CLAUDE / "plugins"
        for sk in plug.rglob("SKILL.md") if plug.exists() else []:
            if sk.parent.name in names and "cache" not in str(sk).lower():
                items.append((skills / sk.parent.name, f"same name as a plugin skill ({sk.parent})", "report"))
    house = {p.name for p in (PACK / "global/house").glob("*.md")} - {"README.md"}
    for md in sorted((CLAUDE / "projects").glob("*/memory")):         # project notes that are now global house notes
        for f in sorted(md.glob("*.md")):
            if f.name in house: items.append((f, "project memory note that is now a global house note (~/.claude/house)", "move" if OWNER_ED else "ask"))
    if project:
        ask = "move" if OWNER_ED else "ask"                         # a project's files are the person's: ask first
        for z in list(project.glob("*-skill.zip")) + list(project.glob("*.skill")):
            items.append((z, "exported copy of a skill (the installed skill is current)", ask))
        for rel in ["tools/cutout/vision_cutout", "tools/cutout/vision_cutout.swift"]:
            if (project / rel).exists(): items.append((project / rel, "Apple Vision cut-out, replaced by BiRefNet HR", ask))
        for rel in ["tools/cutout/birefnet_cutout.py", "tools/cutout/README.md"]:
            f = project / rel
            if f.exists() and not f.is_symlink() and (CLAUDE / "skills/cutout").exists():
                items.append((f, "old project copy of the cut-out tool (now the global cutout skill)", ask))
        old = project / ".cutout"
        if old.is_dir() and not old.is_symlink() and venv_py(CUTOUT).exists():
            items.append((old, "old project cut-out venv (the shared one is ~/.claude/venvs/cutout)", "delete" if OWNER_ED else "ask"))
    hub = Path(os.environ.get("HF_HOME", HOME / ".cache/huggingface")) / "hub"
    caches = [(hub / "models--ZhengPeng7--BiRefNet_HR-matting", "BiRefNet HR-matting model (lost to HR; re-downloads on demand)"),
              (HOME / ".cache/hyperframes/background-removal", "hyperframes remove-background model (BiRefNet HR replaces it)")]
    items += [(p, why, "delete") for p, why in caches if p.exists()]
    mine, packs = MANIFEST["version"], set()
    for pat in ("Claude-setup-pack-*.zip", "Claude-*-setup-pack-*.zip"):            # older packs in a project folder
        if project: packs |= set(project.glob("setup-pack*/**/" + pat))
    for z in sorted(packs):
        v = re.search(r"setup-pack-(?:[A-Za-z]+-)?(\d{4}-\d\d-\d\d\.\d+)", z.name)
        if v and v.group(1) < mine.split("-no-")[0]: items.append((z, "older setup pack", "move" if OWNER_ED else "ask"))
    sp = CLAUDE / "settings.json"
    hooks = json.loads(sp.read_text(encoding="utf-8")).get("hooks", {}).get("PreToolUse", []) if sp.exists() else []
    if sum("block-elevenlabs-transcription" in json.dumps(h) for h in hooks) > 1:
        items.append((sp, "the ElevenLabs block hook is registered more than once", "report"))
    ps1 = CLAUDE / "hooks/block-elevenlabs-transcription.ps1"
    if ps1.exists(): items.append((ps1, "an old PowerShell port of the hook (the pack's Python version replaces it)", "move" if OWNER_ED else "ask"))
    return items

def cmd_cleanup(project, yes):
    items = cleanup_items(project)
    if not items: print("CLEANUP: nothing old or duplicated found."); return 0
    print("CLEANUP CANDIDATES (old duplicates and leftovers)")
    for p, why, act in items: print(f"  [{act:6s}] {p}\n           {why}")
    if ASK_OK:
        apply_items([x for x in items if x[2] == "ask" and os.path.normpath(str(x[0])) in ASK_OK])
        left = ASK_OK - {os.path.normpath(str(x[0])) for x in items if x[2] == "ask"}
        if left: print("not in the list, left alone:", ", ".join(sorted(left)))
        return 0
    if not yes: print("\nNothing removed. Re-run with --yes to move the 'move' and 'tool' items (the pack's own leftovers, unchanged) "
                      "to the backup folder, the 'private' notes to ~/.claude/house-private/, and delete the caches. 'ask' items are "
                      "the person's own or changed: only on their yes, one by one, with --move \"<path>\" (a backup, never deleted)."); return 0
    apply_items([x for x in items if x[2] != "ask"]); return 0

def apply_items(items):
    """carry out cleanup items: moves to the backup folder, retired notes to house-private, caches deleted"""
    for p, why, act in items:
        if act == "report" or (act == "ask" and os.path.normpath(str(p)) not in ASK_OK): continue
        if act == "ask": act = "move"                                # the person said yes: to the backup, never deleted
        if act == "private":                                       # never deleted: becomes a personal note
            dst = CLAUDE / "house-private" / p.name
            if dst.exists(): dst = dst.with_name(f"{p.stem}-from-house-{STAMP}.md")
            dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(p), str(dst)); print("kept   ", p, "->", dst)
            continue
        if act == "tool":                                          # the folder, then its settings lines
            b = BACKUP / "cleanup" / p.relative_to(HOME)
            b.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(p), str(b)); print("moved  ", p, "->", b)
            prune_tool_settings(); continue
        if act == "move":
            b = BACKUP / "cleanup" / (p.relative_to(HOME) if str(p).startswith(str(HOME)) else p.name)
            b.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(p), str(b)); print("moved  ", p, "->", b)
            idx = p.parent / "MEMORY.md"
            if p.parent.name == "memory" and idx.exists():               # drop the moved note's index line
                lines = idx.read_text(encoding="utf-8").splitlines(keepends=True)
                keep = [l for l in lines if f"({p.name})" not in l]
                if len(keep) != len(lines): backup(idx); idx.write_text("".join(keep), encoding="utf-8")
        else:
            shutil.rmtree(p) if p.is_dir() else p.unlink(); print("deleted", p)

def venv_py(v):
    return v / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

def backup(p):
    """copy p into this run's backup folder once: the first copy (the state before this run) is the one kept"""
    if p.exists():
        b = BACKUP / p.relative_to(HOME) if str(p).startswith(str(HOME)) else BACKUP / "other" / p.name
        if b.exists(): return
        b.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, b)

def which(cmd):
    return shutil.which(cmd)

def run(cmd, **kw):
    try: return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=kw.pop("timeout", 60), **kw)
    except Exception as e: return None

# ---------------------------------------------------------------- special merges
def merge3(base, mine, theirs):
    """a line-by-line three-way merge: the pack went base -> theirs, the person base -> mine. The person's lines win where
    both changed the same lines; those pack lines come back as conflicts. Returns (merged lines, conflicting pack lines)."""
    def hunks(a, b, who):
        return [(i1, i2, b[j1:j2], who) for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if tag != "equal"]
    hs = sorted(hunks(base, mine, "you") + hunks(base, theirs, "pack"), key=lambda h: (h[0], h[1]))
    out, conflicts, pos, i = [], [], 0, 0
    while i < len(hs):
        s, e, grp = hs[i][0], hs[i][1], [hs[i]]; i += 1
        while i < len(hs) and (hs[i][0] < e or (hs[i][0] == s and s == e and hs[i][1] == hs[i][0])):
            e = max(e, hs[i][1]); grp.append(hs[i]); i += 1
        out += base[pos:s]; pos = e
        sides = {h[3] for h in grp}
        def side(who):                                             # that side's version of base[s:e]
            res, p = [], s
            for h in [h for h in grp if h[3] == who]: res += base[p:h[0]] + h[2]; p = h[1]
            return res + base[p:e]
        if sides == {"you"}: out += side("you")
        elif sides == {"pack"}: out += side("pack")
        elif side("you") == side("pack"): out += side("you")
        elif all(h[0] == h[1] for h in grp): out += side("pack")[: len(side("pack")) - (e - s)] + side("you")   # both only added
        else: out += side("you"); conflicts += [l for l in side("pack") if l not in side("you")]
    return out + base[pos:], conflicts

RULES_NOTE = []                                                    # what happened to the rules block, for the report

def merged_claude_md(cur):
    block = (PACK / "global/CLAUDE.md").read_text(encoding="utf-8")
    if cur is None: return block
    if RULES_MARK not in cur: return cur.rstrip() + "\n\n" + block
    start = cur.index(RULES_MARK)                                  # the existing block (up to the next top-level heading)
    nxt = re.search(r"\n# (?!#)", cur[start + len(RULES_MARK):])
    end = start + len(RULES_MARK) + nxt.start() + 1 if nxt else len(cur)
    mine = cur[start:end]
    put = lambda b: cur[:start] + b.rstrip() + "\n" + ("\n" if cur[end:].strip() else "") + cur[end:].lstrip("\n")
    if mine.strip() == block.strip(): return cur
    h = hashlib.sha256(mine.strip().encode("utf-8")).hexdigest()
    base = REC.get("rules_block")
    if OWNER_ED or h in EARLIER.get("blocks", {}) or (base and mine.strip() == base.strip()):
        return put(block)                                          # the pack's own block, unchanged: replaced
    if not base:                                                   # no earlier version known: keep theirs, park the new one
        q = UPDATES / "CLAUDE-rules-block.md"; q.parent.mkdir(parents=True, exist_ok=True); q.write_text(block, encoding="utf-8")
        RULES_NOTE.append(f"your rules block differs from every version a setup file shipped: kept as it is; the new block is in {q}")
        return cur
    merged, conflicts = merge3(base.strip().splitlines(), mine.strip().splitlines(), block.strip().splitlines())
    if conflicts:
        q = UPDATES / "CLAUDE-rules-conflicts.md"; q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text("Lines the setup pack changed where you had changed the same lines (yours were kept):\n\n" + "\n".join(conflicts) + "\n", encoding="utf-8")
        RULES_NOTE.append(f"the rules block was merged, keeping your lines; {len(conflicts)} pack line(s) clashed with yours and are in {q}")
    else: RULES_NOTE.append("the rules block was merged: the pack's updates are in, and your own lines are kept")
    return put("\n".join(merged) + "\n")

def hook_cmd():
    if IS_WIN:                                                     # no bash/jq needed: the Python port, run by this Python
        return f'"{Path(sys.executable).as_posix()}" "{(CLAUDE / "hooks" / HOOK_PY).as_posix()}"'
    return str(CLAUDE / "hooks" / HOOK_SH)

def merged_settings(cur):
    s = dict(cur or {})
    perms = s.setdefault("permissions", {})
    deny = perms.setdefault("deny", [])
    rule = "mcp__*__creative_transcribe_audio"
    if not any("creative_transcribe_audio" in d for d in deny): deny.append(rule)
    hooks = s.setdefault("hooks", {}).setdefault("PreToolUse", [])
    want = {"matcher": ("Bash|PowerShell|" if IS_WIN else "Bash|") + "mcp__.*__creative_transcribe_audio",
            "hooks": [{"type": "command", "command": hook_cmd(), "timeout": 10}]}
    if IS_WIN:                                                     # an older pack registered the bash version: swap it
        hooks[:] = [h for h in hooks if not ("block-elevenlabs-transcription" in json.dumps(h) and HOOK_SH in json.dumps(h))]
        s.setdefault("env", {}).setdefault("PYTHONUTF8", "1")      # video-use's helpers print and write non-ASCII
    if not any("block-elevenlabs-transcription" in json.dumps(h) for h in hooks): hooks.append(want)
    plugin_dirs(s, MODS)                                           # each mod this pack carries loads in every chat from its folder
    return s

def plugin_dirs(s, add):
    """settings' mod lines: add these folders; drop an older pack's names, folders that are gone and folders a GitHub plugin
    replaces; with no mod folder left, no plugin-dir lines and no local-mods marketplace (the owner's edition keeps its own)"""
    env = s.setdefault("env", {})
    gone = {str(m) for m in OLD_MODS if not m.exists()} | {str(TOOLS[t][1]) for t in PLUGIN_TOOLS if not TOOLS[t][1].exists()}
    ours = {str(TOOLS[t][1]) for t in ("folio", "pulsewise")}
    have = [d for d in env.get("CLAUDE_CODE_PLUGIN_DIRS", "").split(os.pathsep)
            if d and d not in gone and (d not in ours or Path(d).exists() or Path(d) in add)]
    dirs = have + [str(m) for m in add if str(m) not in have]
    if dirs:
        env["CLAUDE_CODE_PLUGIN_DIRS"] = os.pathsep.join(dirs)
        env.setdefault("CLAUDE_CODE_PLUGIN_DIR_WATCH", "1")       # an edit to the mod reloads it in open chats
    else: env.pop("CLAUDE_CODE_PLUGIN_DIRS", None)               # an empty line only; any other entry of theirs stays
    if not env: s.pop("env", None)
    mods_left = any(Path(d) in {TOOLS[t][1] for t in ("folio", "pulsewise")} for d in map(Path, dirs))
    if add and (PACK / "global/mods/.claude-plugin/marketplace.json").exists():
        s.setdefault("extraKnownMarketplaces", {}).setdefault("local-mods", {"source": {"source": "directory", "path": str(CLAUDE / "mods")}})
    elif not mods_left and not OWNER_ED:
        km = s.get("extraKnownMarketplaces", {})
        if km.get("local-mods", {}).get("source", {}).get("path") == str(CLAUDE / "mods"): km.pop("local-mods")
        if not km: s.pop("extraKnownMarketplaces", None)

def prune_tool_settings():
    """after a tool's folder copy is moved away: its settings lines go too"""
    sp = CLAUDE / "settings.json"
    if not sp.exists(): return
    cur = json.loads(sp.read_text(encoding="utf-8")); new = json.loads(json.dumps(cur))
    plugin_dirs(new, [])
    if new != cur: backup(sp); sp.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")

def mods_off(s):
    """the pack's mods that settings.json doesn't load"""
    have = s.get("env", {}).get("CLAUDE_CODE_PLUGIN_DIRS", "").split(os.pathsep)
    return [m.name for m in MODS if str(m) not in have]

def merged_index(cur, new):
    have = set(re.findall(r"\(([^)]+\.md)\)", cur or ""))
    add = [ln for ln in new.splitlines() if (m := re.search(r"\(([^)]+\.md)\)", ln)) and m.group(1) not in have]
    return (cur.rstrip() + "\n" if cur else "") + ("\n".join(add) + "\n" if add else "")

# ---------------------------------------------------------------- checks
def tool_report(project):
    rows = []
    def add(name, ok, note=""): rows.append((name, ok, note))
    py_ok = sys.version_info >= (3, 10)
    add("python >= 3.10 (running this)", py_ok, sys.version.split()[0] + ("" if py_ok else "  - use python3.12 for skills/venvs"))
    for c, why in [("node", "hyperframes, markroom, explainers"), ("npx", "hyperframes CLI"), ("git", "video-use clone"),
                   ("uv", "venvs (cutout, video-use)"), ("uvx", "the Fetch MCP"), ("ffmpeg", "renders, frame checks"),
                   ("ffprobe", "render checks")] + ([] if IS_WIN else [("jq", "the ElevenLabs block hook")]):
        add(c, bool(which(c)), why)
    ff = None
    for cand in ["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg", "/usr/local/opt/ffmpeg-full/bin/ffmpeg", which("ffmpeg")]:
        if cand and Path(cand).exists():
            r = run([cand, "-hide_banner", "-filters"])
            if r and "drawtext" in r.stdout and "subtitles" in r.stdout: ff = cand; break
    add("ffmpeg with drawtext + subtitles (ffmpeg-full)", bool(ff), ff or ("winget install --id Gyan.FFmpeg -e" if IS_WIN else "brew install ffmpeg-full (keg-only, put it first on PATH)"))
    chrome = [p for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                          os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                          os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                          os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")] if Path(p).exists()] or [which("google-chrome") or which("chromium")]
    add("Google Chrome (still renders, headless)", bool(chrome and chrome[0]), "")
    vu = CLAUDE / "skills/video-use"
    add("video-use skill (git clone)", (vu / ".git").exists(), VIDEO_USE + "  - then `uv sync` in it; never run its transcribe helpers")
    ps = patch_state()
    if ps: add("video-use path patch applied", ps == "applied", "install applies it" if ps == "pending" else "conflicts with this clone: apply extras/video-use-windows-paths.patch by hand")
    add("Parakeet model for local transcription", parakeet_ok(), "python3 sync.py install --parakeet  (~640 MB)")
    add("Fetch MCP for reading web pages (instead of Firecrawl)", fetch_ok(), "python3 sync.py install  (adds it; loads in new sessions)")
    py = venv_py(CUTOUT)
    ok = py.exists() and (r := run([str(py), "-c", "import torch,transformers,timm,kornia,cv2,PIL;print(transformers.__version__)"], timeout=120)) and r.returncode == 0
    add("cut-out venv ~/.claude/venvs/cutout (torch, transformers 4.x, timm, kornia, cv2, Pillow)", bool(ok), "python3 sync.py install --cutout-env")
    add("cut-out machine check (machine.json: precision and memory cap for this computer)", (CUTOUT / "machine.json").exists(),
        "python3 sync.py install  (runs the check), or run the venv's Python on ~/.claude/skills/cutout/scripts/probe_machine.py")
    hub = Path(os.environ.get("HF_HOME", HOME / ".cache/huggingface")) / "hub"
    for m in MODELS:
        add("model " + m, (hub / ("models--" + m.replace("/", "--"))).exists(), "fetched by --cutout-env (about 450 MB)")
    hk = CLAUDE / "hooks" / (HOOK_PY if IS_WIN else HOOK_SH)       # test the one this OS registers
    runner = [sys.executable, str(hk)] if IS_WIN else ["bash", str(hk)]
    if hk.exists() and (IS_WIN or (which("jq") and which("bash"))):
        probe = json.dumps({"tool_name": "Bash", "tool_input": {"command": "curl https://api.elevenlabs.io/v1/speech-to-text"}, "cwd": str(HOME)})
        r = run(runner, input=probe)
        add("hook denies ElevenLabs transcription", bool(r and '"deny"' in r.stdout), "")
        r2 = run(runner, input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "npx hyperframes transcribe a.mp4"}, "cwd": str(HOME)}))
        add("hook allows local transcription", bool(r2 and '"deny"' not in r2.stdout), "")
    else:
        add("hook test", False, "needs the hook file" + ("" if IS_WIN else ", bash and jq"))
    return rows

YOURS = []

def kept_report():
    """what the update left as the person had it, and where the pack's new versions went"""
    if not (KEPT or REMOVED_KEPT or RULES_NOTE): return
    print("\nKEPT AS YOU HAD IT (the update never undoes your changes; merge what you want, by hand or by asking Claude)")
    for d, q in KEPT: print(f"  changed by you   {d}\n                   the pack's new version: {q}")
    for d, q in REMOVED_KEPT: print(f"  removed by you   {d}\n                   the pack's version, if you want it back: {q}")
    for note in RULES_NOTE: print(f"  CLAUDE.md        {note}")

def compare(project):
    missing, differ, same, yours = [], [], 0, YOURS
    yours.clear()
    for rel, h in MANIFEST["files"].items():
        d = dest(rel, project)
        if d is None or seeded(rel) or tool_file(rel) or opt_skip(rel): continue
        if rel in SECTION_FILES:
            if rel != MY_SECTIONS: continue
            cm = CLAUDE / "CLAUDE.md"
            for head in missing_sections(cm.read_text(encoding="utf-8") if cm.exists() else None): missing.append(f"{cm}  (section '{head}')")
            continue
        if rel == "global/CLAUDE.md":
            cur = d.read_text(encoding="utf-8") if d.exists() else None
            merged_here = REC.get("version") == MANIFEST["version"] and not OWNER_ED   # merged with the person's lines this version
            ok = cur is not None and ((PACK / rel).read_text(encoding="utf-8").strip() in cur or merged_here)
            (same := same + 1) if ok else (missing if cur is None else differ).append(str(d) + "  (rules block)")
            continue
        if rel == "memory/MEMORY.md":
            cur = d.read_text(encoding="utf-8") if d.exists() else ""
            need = set(re.findall(r"\(([^)]+\.md)\)", (PACK / rel).read_text(encoding="utf-8"))) - set(re.findall(r"\(([^)]+\.md)\)", cur))
            (same := same + 1) if not need else differ.append(str(d) + "  (index lacks: " + ", ".join(sorted(need)) + ")")
            continue
        if not d.exists():
            if rel in REC.get("files", {}) and not OWNER_ED: yours.append(str(d) + "  (removed by you; kept removed)")
            else: missing.append(str(d))
        elif sha(d) != h:
            if OWNER_ED or known(rel, sha(d)): differ.append(str(d))
            else: yours.append(str(d) + "  (changed by you; kept)")
        else: same += 1
    if not lang_choice():
        missing.append(f"{CLAUDE / 'CLAUDE.md'}  (section '{LANG_HEAD}': ask the user 'English only' or 'English + Hindi and "
                       "other languages', then run install --transcription english|multilingual)")
    sp = CLAUDE / "settings.json"
    s = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    if "block-elevenlabs-transcription" not in json.dumps(s.get("hooks", {})): differ.append(str(sp) + "  (ElevenLabs hook not registered)")
    if mods_off(s): differ.append(str(sp) + f"  (mods not loaded: env CLAUDE_CODE_PLUGIN_DIRS doesn't name {', '.join(mods_off(s))})")
    for name in MANIFEST.get("retired_skills", []):
        if (CLAUDE / "skills" / name).exists(): differ.append(str(CLAUDE / "skills" / name) + "  (retired skill still installed; install removes it)")
    return missing, differ, same

def stale_paths(project):
    """house notes naming tool paths (Homebrew, /Applications, drives) that don't exist here: machine notes to review"""
    out = []
    if not IS_MAC: return out                                      # general notes name no machine paths
    for f in sorted((CLAUDE / "house").glob("*.md")):
        for p in set(re.findall(r"(/(?:opt|Volumes|Applications)/[^\s`)\"']+)", f.read_text(encoding="utf-8"))):
            p = re.sub(r":\$PATH$", "", p).rstrip(".,;:")
            # a path with spaces is cut at the first one ("/Applications/Adobe After Effects..."): accept a prefix match
            if not Path(p).exists() and not list(Path(p).parent.glob(Path(p).name + "*")): out.append(f"{f.name}: {p}")
    return out

def cmd_strip_owner(zip_path):
    """after a general install: owner.bin out of this folder and out of the zip it came from (the owner's part is never
    this computer's; every setup file built here is general anyway)"""
    if MANIFEST.get("edition") == "personal":
        print("This is the owner's own edition: nothing to strip."); return 0
    (PACK / OWNER_FILE).unlink(missing_ok=True)
    z = Path(os.path.expanduser(zip_path)) if zip_path else None
    if not z or not z.is_file(): return 0
    with zipfile.ZipFile(z) as src:
        names = [n for n in src.namelist() if n.rsplit("/", 1)[-1] != OWNER_FILE]
        if len(names) == len(src.namelist()): return 0
        tmp = z.with_name(z.name + ".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
            for n in names: dst.writestr(src.getinfo(n), src.read(n))
    os.replace(tmp, z)
    return 0

def cmd_check(project):
    print(f"Setup pack {MANIFEST['version']} (made {MANIFEST['made']})" + (", the owner's own edition" if MANIFEST.get("edition") == "personal" else ""))
    print(f"installs into: {CLAUDE}" + (f"   (project for cleanup: {project})" if project else "") + "\n")
    missing, differ, same = compare(project)
    print(f"FILES  {same} in sync, {len(missing)} missing, {len(differ)} different" + (f", {len(YOURS)} yours (kept as you have them)" if YOURS else ""))
    for y in YOURS[: (len(YOURS) if VERBOSE else 5)]: print("  yours    ", y)
    if len(YOURS) > 5 and not VERBOSE: print(f"  yours     ... {len(YOURS) - 5} more (--verbose lists them)")
    def area(path):                                   # group by skill / memory / project / global
        s = str(path)
        m = re.search(r"[\\/]skills[\\/]([^\\/]+)", s)
        if m: return "skill " + m.group(1)
        if "memory" in s: return "memory"
        if project and s.startswith(str(project)): return "project files"
        return "global config"
    for label, items in (("missing", missing), ("different", differ)):
        groups = {}
        for it in items: groups.setdefault(area(it), []).append(it)
        for g, its in sorted(groups.items()):
            print(f"  {label:9s} {g}: {len(its)} file(s)")
            for it in its[: (len(its) if VERBOSE else 2)]: print("              ", it)
    print(f"TRANSCRIPTION LANGUAGES  {lang_choice() or 'not chosen yet'}")
    for g in OPTIONAL: print(f"OPTIONAL SKILLS  {g}: " + ("installed" if opt_on(g) else f"not installed (on a yes: install --{g} yes)"))
    plugins = plugin_tools()
    print("THE THREE TOOLS  (optional; doesn't affect IN SYNC)")
    for t in TOOLS: print(f"  {TOOL_NAMES[t]:10s} {tool_state(t, plugins)}")
    if TOOL_SOURCE and not OWNER_ED and any(tool_state(t, plugins) == "not installed" for t in TOOL_SOURCE.get("tools", [])):
        print("  (this setup file installs them from GitHub on request: `sync.py tools --install <names>`)")
    print("\nTOOLS")
    rows = tool_report(project)
    for name, ok, note in rows: print(f"  [{'ok' if ok else '--'}] {name}" + (f"   {note}" if note and not ok else ""))
    st = stale_paths(project)
    if st:
        print("\nHOUSE NOTES NAMING PATHS NOT ON THIS MACHINE (review; add where the tool lives here)")
        for s in st: print("  ", s)
    plug = CLAUDE / "plugins"
    watch_in = bool(plug.exists() and any(p.name.startswith("watch") for p in plug.rglob("watch*") if p.is_dir()))
    watch_cfg = (HOME / ".config/watch/.env").exists()
    if not (watch_in and watch_cfg):
        print("\nFOR THE USER (plugins come from their claude.ai account; doesn't affect IN SYNC)")
        if not watch_in: print("  [--] watch plugin not seen here (look for watch:watch in your skills). It's free and works on any Claude "
                               "account: the user runs, in a terminal Claude Code session (`claude`),  /plugin marketplace add "
                               "bradautomates/claude-video  then  /plugin install watch@claude-video , and starts a new session. "
                               "On an account that already has it, it appears by itself")
        if not watch_cfg: print("  [--] watch not set up (~/.config/watch/.env): after installing, run its setup with engine local, "
                                "WhisperX small, detail balanced, no API keys; it runs with python3.12")
    cl = cleanup_items(project)
    if cl:
        print("\nCLEANUP CANDIDATES (old duplicates; doesn't affect IN SYNC; `sync.py cleanup` lists them, `--yes` removes them)")
        for p, why, act in cl: print(f"  [{act}] {p}  - {why}")
    bad = missing or differ or any(not ok for _, ok, _ in rows)
    print("\n" + ("NOT IN SYNC: fix the lines marked above, then run check again." if bad else "IN SYNC"))
    return 1 if bad else 0

def cmd_tools(want, set_aside=False):
    """the three tools: show where each comes from; with --install (git edition), put the ticked ones in from GitHub"""
    plugins = plugin_tools()
    print("THE THREE TOOLS")
    for t in TOOLS: print(f"  {TOOL_NAMES[t]:10s} {tool_state(t, plugins)}")
    src = TOOL_SOURCE or {}
    if not want:
        if src and not OWNER_ED:
            print(f"\nThis setup file installs them from GitHub ({src['repo']}) on request: sync.py tools --install folio,pulsewise,markroom "
                  "(any of them, comma-separated)")
        return 0
    if OWNER_ED:
        print("\nThis is the owner's own edition: the tools stay the folders here (the working copies); nothing comes from GitHub."); return 1
    if not src:
        print("\nThis setup file carries the tools itself: nothing to install from GitHub."); return 1
    picked = [w.strip().lower() for w in want.split(",") if w.strip()]
    bad = [p for p in picked if p not in src.get("tools", [])]
    if bad: print(f"\nnot one of the tools: {', '.join(bad)} (choose from {', '.join(src.get('tools', []))})"); return 2
    held = [t for t in picked if TOOLS[t][1].exists() and not untouched_tree(TOOLS[t][0], TOOLS[t][1])]
    if held and not set_aside:                                     # the person's fix may be in there: never install on top
        for t in held:
            print(f"\n{TOOL_NAMES[t]}: the folder here ({TOOLS[t][1]}) has your changes, so it stays and nothing is installed from "
                  "GitHub on top of it (both would load). Ask whether to keep it, or to set it aside (to the backup, never deleted) "
                  f"and install from GitHub: sync.py tools --install {t} --set-aside")
        picked = [t for t in picked if t not in held]
    exe = which("claude") or which("claude.cmd")
    done, failed = [], []
    for t in picked:
        if not exe: failed.append(t); continue
        r = run([exe, "plugin", "install", t, "--marketplace", src["repo"], "--scope", "user", "-y"], timeout=900)
        ok = bool(r) and r.returncode == 0
        print(f"{TOOL_NAMES[t]}: " + ("installed" if ok else "FAILED " + ((r.stderr or r.stdout)[-600:] if r else "")))
        (done if ok else failed).append(t)
    for t in done:                                                 # an older folder copy would load twice: it goes to the backup
        if TOOLS[t][1].exists():
            b = BACKUP / "cleanup" / TOOLS[t][1].relative_to(HOME)
            b.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(TOOLS[t][1]), str(b))
            print(f"moved the older folder copy of {TOOL_NAMES[t]} to {b}")
    global PLUGIN_TOOLS; PLUGIN_TOOLS = PLUGIN_TOOLS | set(done); prune_tool_settings()
    if failed:
        print("\nInstall these by hand, in a Claude Code chat (one line at a time; then choose user scope):")
        print(f"  /plugin marketplace add {src['repo']}")
        for t in failed: print(f"  /plugin install {t}@{src['marketplace']}")
        if not exe: print("(the `claude` command isn't on this computer's PATH, so the setup couldn't run them itself)")
        if any(TOOLS[t][1].exists() for t in failed):
            print("Their older folder copies stay until then; afterwards `sync.py cleanup --yes` moves the unchanged ones to the backup.")
    print("\nOpen a new chat so the new tools load.")
    return 1 if failed or (held and not set_aside) else 0

def git_cmd():
    """git for downloads. On Windows it uses OpenSSL: the default (schannel) runs TLS inside lsass, which loads every
    Winsock name-space add-in, and with LSA protection on, an add-in Windows blocks (Bonjour's mdnsNSP.dll) brings up a
    'Local Security Authority' pop-up for each download"""
    return [which("git") or "git"] + (["-c", "http.sslBackend=openssl"] if IS_WIN else [])

def rmtree_force(p):
    """remove a folder, read-only git objects included (Windows)"""
    def again(f, path, _):
        try: os.chmod(path, 0o700); f(path)
        except OSError: pass
    shutil.rmtree(p, onerror=again)

DOWNLOADS = MANIFEST.get("downloads", [])   # the git edition's third-party skills, fetched from their own repos
NOT_FETCHED = set()                          # skills whose download failed: install leaves them out and says so

def fetch_downloads():
    """the git edition's third-party skills: each from its own repo, at the commit this pack was built and checked with,
    into the pack folder; every file is checked against MANIFEST before install copies it. Returns report lines."""
    import tempfile
    lines = []
    for dl in DOWNLOADS:
        names = list(dl["skills"].values())
        if dl.get("group") and not opt_on(dl["group"]):
            lines.append(f"{dl['label']}: not downloaded (not chosen)"); continue
        want = {r: h for r, h in MANIFEST["files"].items() if r.startswith("skills/") and Path(r).parts[1] in names}
        if all((PACK / r).is_file() and sha(PACK / r) == h for r, h in want.items()):
            lines.append(f"{dl['label']}: ready ({len(want)} files)"); continue
        err, tmp = None, Path(tempfile.mkdtemp(prefix="csp-fetch-"))
        if not which("git"): err = "git not found"
        for step in ([] if err else [["init", "-q", str(tmp)], ["-C", str(tmp), "remote", "add", "origin", dl["repo"]],
                     ["-C", str(tmp), "sparse-checkout", "set", *dl["skills"]],
                     ["-C", str(tmp), "-c", "core.autocrlf=false", "fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", dl["commit"]],
                     ["-C", str(tmp), "-c", "core.autocrlf=false", "checkout", "-q", "FETCH_HEAD"]]):
            r = run(git_cmd() + step, timeout=900)
            if not r or r.returncode != 0: err = ((r.stderr or r.stdout).strip()[-300:] if r else "git did not run"); break
        if not err:
            for src, name in dl["skills"].items():
                d = PACK / "skills" / name
                if d.exists(): rmtree_force(d)
                if not (tmp / src).is_dir(): err = f"{src} is missing from {dl['repo']} at {dl['commit'][:8]}"; break
                shutil.copytree(tmp / src, d, ignore=shutil.ignore_patterns(".git"))
        if not err:
            for to, frm in dl.get("stock", {}).items():           # a skill's stock settings (real-sfx's config.json)
                if (PACK / frm).is_file(): shutil.copy2(PACK / frm, PACK / to)
            bad = [r for r, h in want.items() if not (PACK / r).is_file() or sha(PACK / r) != h]
            if bad: err = f"{len(bad)} file(s) differ from this pack's version (e.g. {bad[0]})"
        rmtree_force(tmp)
        if err:
            for name in names:
                if (PACK / "skills" / name).exists(): rmtree_force(PACK / "skills" / name)
            NOT_FETCHED.update(names)
            lines.append(f"{dl['label']}: DOWNLOAD FAILED ({err}); not installed: run install again later")
        else: lines.append(f"{dl['label']}: downloaded from {dl['repo']} ({dl['commit'][:8]}), {len(want)} files checked")
    return lines

def cmd_install(project, cutout_env, parakeet, transcription=None):
    n, rec = 0, {}
    for name in SEEDS: SEED_NEW[name] = not (CLAUDE / "skills" / name).exists()
    for line in fetch_downloads(): print(line)
    for rel, h in MANIFEST["files"].items():
        src, d = PACK / rel, dest(rel, project)
        if d is None or seeded(rel) or tool_file(rel) or opt_skip(rel): continue
        if rel.startswith("skills/") and Path(rel).parts[1] in NOT_FETCHED: continue   # its download failed (reported above)
        if rel in SECTION_FILES: continue                          # added after the rules block, below
        d.parent.mkdir(parents=True, exist_ok=True)
        if rel == "global/CLAUDE.md":
            cur = d.read_text(encoding="utf-8") if d.exists() else None
            new = merged_claude_md(cur)
            if new != cur: backup(d); d.write_text(new, encoding="utf-8"); n += 1
            continue
        if rel == "memory/MEMORY.md":
            cur = d.read_text(encoding="utf-8") if d.exists() else None
            new = merged_index(cur, src.read_text(encoding="utf-8"))
            if new != cur: backup(d); d.write_text(new, encoding="utf-8"); n += 1
            continue
        if not d.exists():
            if rel in REC.get("files", {}) and not OWNER_ED:       # the person removed a pack file: it stays removed
                REMOVED_KEPT.append((d, park(rel))); continue
        elif sha(d) == h: rec[rel] = h; continue
        elif not OWNER_ED and not known(rel, sha(d)):              # the person changed it: theirs stays, the new one is parked
            KEPT.append((d, park(rel)))
            if rel in REC.get("files", {}): rec[rel] = REC["files"][rel]
            continue
        backup(d); shutil.copy2(src, d); n += 1; rec[rel] = h
        if d.suffix in (".sh", ".py", ".mjs") and os.name != "nt": d.chmod(d.stat().st_mode | 0o111)
    cm = CLAUDE / "CLAUDE.md"                                      # this OS's own sections go after the rules block
    add = missing_sections(cm.read_text(encoding="utf-8") if cm.exists() else None)
    if add:
        cur = cm.read_text(encoding="utf-8") if cm.exists() else ""
        backup(cm); cm.write_text(cur.rstrip() + "\n\n" + "\n".join(x.rstrip() + "\n" for x in add.values()), encoding="utf-8"); n += 1
    sp = CLAUDE / "settings.json"
    cur = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else None
    new = merged_settings(cur)
    if new != cur: backup(sp); sp.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8"); n += 1
    old = old_version_items()                                      # the older version's installs, where nobody changed them
    if [x for x in old if x[2] not in ("ask", "report")]: print("clearing the older version's installs:"); apply_items(old); n += len(old)
    REC_FILE.parent.mkdir(parents=True, exist_ok=True)              # what this install wrote: the next update's base
    REC_FILE.write_text(json.dumps({"version": MANIFEST["version"], "files": {**REC.get("files", {}), **rec},
                                    "rules_block": (PACK / "global/CLAUDE.md").read_text(encoding="utf-8")}, indent=0), encoding="utf-8")
    hp = CLAUDE / "setup-pack" / "history.json"                    # this computer's builder keeps every fingerprint too
    hist = load_json(hp, {"files": {}, "blocks": {}})
    for r, hs in EARLIER.get("files", {}).items():
        for x in hs:
            if x not in hist["files"].setdefault(r, []): hist["files"][r].append(x)
    for k, v in EARLIER.get("blocks", {}).items(): hist.setdefault("blocks", {}).setdefault(k, v)   # never blank a kept text
    if EARLIER.get("files"): hp.write_text(json.dumps(hist, indent=0), encoding="utf-8")
    print(f"installed/updated {n} files (backups: {BACKUP if BACKUP.exists() else 'none needed'})")
    kept_report()
    vu = CLAUDE / "skills/video-use"
    if not vu.exists() and which("git") and "--skip-video-use" not in sys.argv:
        r = run(git_cmd() + ["clone", "-c", "core.autocrlf=false", VIDEO_USE, str(vu)], timeout=600)   # LF, so the patch applies
        print("video-use cloned" if r and r.returncode == 0 else "video-use clone FAILED: " + (r.stderr if r else ""))
        if which("uv") and (vu / "pyproject.toml").exists(): run(["uv", "sync"], cwd=str(vu), timeout=1800)
    if patch_state() == "pending":
        r = run(["git", "-C", str(vu), "apply", str(short_patch())])
        print("video-use path patch:", "applied" if r and r.returncode == 0 else "FAILED " + (r.stderr if r else ""))
    print("Fetch MCP:", install_fetch())
    if transcription:
        set_lang(transcription); print("transcription languages:", transcription)
        if transcription == "multilingual": print("Whisper:", whisper_prefetch())
    if parakeet and not parakeet_ok():
        npx = which("npx") or which("npx.cmd")
        r = npx and run([npx, "-y", "hyperframes", "models", "install", "parakeet"], timeout=3600, cwd=str(HOME))
        print("Parakeet:", "installed" if parakeet_ok() else "FAILED " + ((r.stderr or r.stdout)[-800:] if r else "npx not found"))
    if cutout_env:
        cut, py = CUTOUT, venv_py(CUTOUT)
        old = project / ".cutout" if project else None
        if not py.exists() and old and old.is_dir() and not old.is_symlink() and venv_py(old).exists():
            cut.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(old), str(cut))   # keeps its torch (e.g. CUDA)
            if os.name != "nt": old.symlink_to(cut)
            print(f"moved the old cut-out venv {old} -> {cut}")
        if not py.exists():
            cut.parent.mkdir(parents=True, exist_ok=True)
            if which("uv"): run(["uv", "venv", str(cut), "-p", "3.12"], timeout=600)
            else: run([sys.executable, "-m", "venv", str(cut)], timeout=600)
        # --torch-backend auto: CUDA torch where there's an NVIDIA GPU (Windows/Linux), the normal build elsewhere
        if which("uv"): r = run(["uv", "pip", "install", "-p", str(py), "--torch-backend", "auto", *CUTOUT_PKGS], timeout=3600)
        else: r = run([str(py), "-m", "pip", "install", *CUTOUT_PKGS], timeout=3600)
        print("cut-out packages:", "ok" if r and r.returncode == 0 else "FAILED " + (r.stderr[-800:] if r else ""))
        fetch = ("from transformers import AutoModelForImageSegmentation as M\n" +
                 "".join(f"M.from_pretrained('{m}', trust_remote_code=True)\n" for m in MODELS) + "print('models ok')")
        r = run([str(py), "-c", fetch], timeout=3600)
        print("models:", r.stdout.strip() if r and r.returncode == 0 else "FAILED " + (r.stderr[-800:] if r else ""))
    if cutout_env or (venv_py(CUTOUT).exists() and not (CUTOUT / "machine.json").exists()):
        print("cut-out machine check:", cutout_probe())
    print()
    return cmd_check(project)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["check", "install", "cleanup", "unlock", "strip-owner", "tools"])
    ap.add_argument("--project", help="optional: a project folder whose old leftovers (cut-out venv, tool copies, skill zips) to clean up or reuse")
    ap.add_argument("--cutout-env", action="store_true", help="also build ~/.claude/venvs/cutout and fetch the BiRefNet HR model")
    ap.add_argument("--parakeet", action="store_true", help="also install Parakeet TDT 0.6B v3 for hyperframes / local-transcribe (~640 MB)")
    ap.add_argument("--transcription", choices=["english", "multilingual"],
                    help="this machine's transcription languages (ask the user): english = Parakeet only; multilingual = also "
                         "Hindi and other languages via Whisper large-v3 (~3 GB, downloaded now)")
    ap.add_argument("--higgsfield", choices=["yes", "no"], help="install: the optional higgsfield skills (ask the user); left out, they stay as they are")
    ap.add_argument("--yes", action="store_true", help="cleanup: actually remove the candidates (moves go to the backup folder)")
    ap.add_argument("--skip-video-use", action="store_true", help="don't clone video-use (testing)")
    ap.add_argument("--verbose", action="store_true", help="list every missing/different file")
    ap.add_argument("--owner-code", help="the owner's code, exactly as they gave it: opens their own edition (owner.bin)")
    ap.add_argument("--zip", help="strip-owner: the setup zip this folder came from")
    ap.add_argument("--install", help="tools: the tools to install from GitHub, comma-separated (folio, pulsewise, markroom)")
    ap.add_argument("--move", action="append", default=[], help="cleanup: move this listed 'ask' item to the backup (only on the person's yes)")
    ap.add_argument("--set-aside", action="store_true", help="tools --install: also set aside a tool folder with the person's changes (only on their yes)")
    a = ap.parse_args()
    project = Path(os.path.expanduser(a.project)).resolve() if a.project else None
    ASK_OK.update(os.path.normpath(os.path.abspath(os.path.expanduser(m))) for m in a.move)
    if a.mode == "cleanup": sys.exit(cmd_cleanup(project, a.yes))
    if a.mode == "unlock": sys.exit(0 if MANIFEST.get("edition") == "personal" else 1)   # the message above says which
    if a.mode == "strip-owner": sys.exit(cmd_strip_owner(a.zip))
    if a.mode == "tools": sys.exit(cmd_tools(a.install, a.set_aside))
    if a.higgsfield: OPT_CHOICE["higgsfield"] = a.higgsfield == "yes"
    sys.exit(cmd_check(project) if a.mode == "check" else cmd_install(project, a.cutout_env, a.parakeet, a.transcription))
