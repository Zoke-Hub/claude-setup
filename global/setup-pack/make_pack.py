#!/usr/bin/env python3
"""Build a Claude setup file from this computer's setup and zip it (run whenever rules, house notes, skills or tools change).

  python3 ~/.claude/setup-pack/make_pack.py                          # the general setup file -> ~/Downloads
  python3 ~/.claude/setup-pack/make_pack.py --full --owner-code '<code>'   # the full setup file (owner's computers only)
  ... --out <folder>                                                  # write the zip and PROMPT.md somewhere else
  python3 ~/.claude/setup-pack/make_pack.py --git                    # the git edition: general, without the three tools;
                                                                     #   setup asks which to install from GitHub (TOOL_REPO)
  python3 ~/.claude/setup-pack/make_pack.py --git --repo <folder>    # the same, as a repository's files (GIT_REPO): its
                                                                     #   README, PROMPT.md and LICENSE from templates/*-git*

The git edition is public, so it carries no third-party skill that can come from its maker. DOWNLOADS (real-sfx,
HeyGen's current skills, Higgsfield's optional ones) are fetched by `sync.py install` from their own repos, pinned to the
commit each repo had when the edition was built; MANIFEST "downloads" names them and every file's sha256 is in MANIFEST,
so install checks what it fetched. HeyGen's retired skills (KEPT_RETIRED) ship as installed here, with HeyGen's Apache
licence and a SOURCE.md beside each, and a line at the end of any file that differs from HeyGen's copy. The other
third-party skills ship with their own licence files.

The three tools (MarkRoom, PulseWise, Folio) are optional. A zip setup file carries each one installed here as a folder
(one installed as a GitHub plugin instead, or not at all, is left out). The git edition carries none: its MANIFEST names
TOOL_REPO and TOOL_MARKETPLACE, and `sync.py tools --install` puts in the ones the user ticks. Owner's computers keep the
tools as folders, so the git edition is general only.

The builder lives in ~/.claude/setup-pack on every computer the pack is installed on, so any computer can build its own
general setup file. The full setup file also carries the owner's own edition, locked into owner.bin with the owner code
(never written in any file). It can only be built on a computer that has the owner's edition installed
(OWNER_CFG): the code is checked against it first, and a wrong code, or no owner's edition, builds the general file.

Collects only general, machine-wide material that anyone can use: the "# Global rules" block of ~/.claude/CLAUDE.md (plus
this computer's other OS sections, which sync.py adds on macOS only), the general house notes (~/.claude/house), the
ElevenLabs hook, every skill except LOCAL_SKILLS and the owner's own skills (OWNER_CFG "personal_skills", owner's edition only; SEED_SKILLS are installed only where missing), the mods in MODS (the
PulseWise progress bar, which carries its own helper, and the Folio archive, ~/.claude/mods, code only), the video-use path patch, the Windows sections (templates/CLAUDE-sections-windows.md), this builder itself
(BUILDER_FILES -> ~/.claude/setup-pack), plus pack/sync.py, pack/SETUP.md, pack/bootstrap-mac.sh and
pack/bootstrap-windows.ps1. Writes MANIFEST.json with a sha256 per file.

Never packed: ~/.claude/house-private, CLAUDE.md's "# Personal (not packed)" and per-machine sections, any project memory,
mods still in development (~/.claude/dev-mods), and the owner's own house rules (OWNER_CFG "personal_house": the note and
its lines in CLAUDE.md and the house README are cut out). Every file is scanned for secrets; on the owner's computers
also for the owner's personal traces (OWNER_CFG "traces", and the credited name outside CREDIT_OK). A hit stops the build.

The owner's edition (owner.bin) adds ~/.claude/house-private, the Personal section (on macOS and Windows), the owner's
own skills (OWNER_CFG "personal_skills"), the Unfold AE text presets' installer part (UNFOLD -> ~/.claude/ae-presets/unfold;
their renders travel in house-private), the owner's own house rules kept whole, its own MANIFEST.json and OWNER.md (from OWNER_TEXT). It holds only the files that differ
from the general pack, encrypted with the code (sync.py's owner lock: PBKDF2-SHA256, an HMAC-SHA256 stream,
encrypt-then-MAC).
"""
import argparse, hashlib, hmac, io, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CL = Path.home() / ".claude"
PACK = HERE / "pack"
NAME = "Claude-setup-pack"
SKIP = {"__pycache__", ".venv", "node_modules", ".DS_Store", ".git"}
RETIRED = ["review-dashboard", "redline",   # skills merged or renamed (redline is now markroom); install backs them up and removes them
           "animation-easing", "after-effects-translation", "puppet-rig",   # merged into animation (2026-11-03)
           "aroll-zooms-and-cuts"]                                         # retired (2026-11-03)
MODS = ["pulsewise", "folio"]          # mods in ~/.claude/mods that ship; sync.py loads each in every chat
TOOL_SKILLS = ["markroom"]             # the third tool, a skill; the git edition leaves all three out
# skills written for this setup (not third-party): a git-edition build lists every OTHER shipped skill without a licence file,
# so the owner checks it may be redistributed before the git edition goes in a public repo
OWN_SKILLS = {"markroom", "logo-recreation", "animation", "cutout", "chat-archive", "local-transcribe", "earshot"}   # (owner-only skills never ship here)
# where the git edition installs the tools from: placeholders until the repo is published (filled in one pass with the tools')
TOOL_REPO = "Zoke-Hub/claude-tools"
TOOL_MARKETPLACE = "zoke"
MOD_DEV = {"tests", "tsconfig.json"}   # each mod's own tests; .claude-plugin/types is the generated SDK typing (gitignored)
LOCAL_SKILLS = {"video-use"}          # cloned on the other side; its .env holds a key
SEED_SKILLS = ["local-transcribe"]    # installed only where missing: each machine keeps its own copy
# files of a skill that are this computer's own and never ship; and a skill's stock file shipped in place of this computer's
SKILL_LOCAL = {"real-sfx": {"library_index.json"}}                      # real-sfx: the index of this computer's sound library
SKILL_STOCK = {"real-sfx/config.json": "real-sfx/config.example.json"}   # its libraries: each computer runs `setup.py init`
# this builder, installed on every computer as ~/.claude/setup-pack (pack/ also holds the staged pack while building)
BUILDER_FILES = ["make_pack.py", "PROMPT.md", "templates/CLAUDE-sections-mac.md", "templates/CLAUDE-sections-windows.md",
                 "templates/README-git.md", "templates/PROMPT-git.md", "templates/LICENSE-git.txt",
                 "templates/unfold-README.md", "templates/cutout-test.jpg", "CHANGES.md",
                 "pack/sync.py", "pack/SETUP.md",
                 "pack/bootstrap-mac.sh", "pack/bootstrap-windows.ps1"]
OPTIONAL_SKILLS = {"higgsfield": "higgsfield-"}   # skill groups setup asks about (name prefix); installed only on a yes
# the git edition's third-party skills that setup downloads from their makers' repos (never inside it): each is pinned to
# the repo's newest commit at build time, and every file's sha256 goes in MANIFEST so install checks what it fetched
DOWNLOADS = [
    {"label": "real-sfx (Clipwing)", "repo": "https://github.com/Clipwing/skills", "skills": {"skills/real-sfx": "real-sfx"}},
    {"label": "HeyGen's hyperframes skills", "repo": "https://github.com/heygen-com/hyperframes",
     "skills": {"skills/hyperframes": "hyperframes", "skills/hyperframes-cli": "hyperframes-cli",
                "skills/hyperframes-registry": "hyperframes-registry", "skills/media-use": "media-use"}},
    {"label": "Higgsfield's skills", "repo": "https://github.com/higgsfield-ai/skills", "group": "higgsfield", "prefix": "higgsfield-"},
]
# HeyGen's skills it retired upstream on 2026-10-21 (folded into hyperframes and media-use). The git edition keeps this
# computer's copies, which are HeyGen's last version before it retired them (commit 207c8a4d, 21 October 2026): each gets
# HeyGen's Apache licence and a SOURCE.md, and any file that differs from HeyGen's says so at its end (Apache 2.0, section 4)
KEPT_RETIRED = {"repo": "https://github.com/heygen-com/hyperframes", "commit": "207c8a4daf6480d697f203784f1fd422727569e3",
                "date": "21 October 2026", "skills": ["hyperframes-animation", "hyperframes-audio", "hyperframes-core",
                "hyperframes-creative", "hyperframes-keyframes", "hyperframes-studio", "motion-graphics"]}
GIT_REPO = "Zoke-Hub/claude-setup"     # where the git edition is published (its README and PROMPT.md name it)
GIT_TEMPLATES = {"README.md": "templates/README-git.md", "PROMPT.md": "templates/PROMPT-git.md", "LICENSE": "templates/LICENSE-git.txt"}
OWNER_BUILDER_FILES = {"templates/unfold-README.md"}   # builder files only the owner's edition carries
# house notes older packs installed that this one doesn't ship; `sync.py cleanup` moves them to ~/.claude/house-private
RETIRED_HOUSE = ["article-animation-direction", "collage-composition-rules", "iconic-group-objects", "cutout-tool",
                 "logo-recreation-skill", "barty-bart-motion-skills", "video-use-run-environment", "watch-skill-setup",
                 "windows-pc-environment", "setup-pack", "final-output-4k", "render-4k-only-on-request",
                 "motion-style-decisions"]
# house notes an older pack installed under an old name; `cleanup` moves them to the backup folder
REPLACED_HOUSE = ["dashboard-means-redline", "redline-read-overall-notes",   # now dashboard-means-markroom, markroom-read-overall-notes
                  "report-long-job-progress", "run-work-in-parallel"]           # now carried by PulseWise itself
RETIRED_MODS = ["pulse"]           # mods an older pack installed under an old name (Pulse is now PulseWise)
RETIRED_FOLDERS = ["ae-presets/unfold"]   # ~/.claude folders an older general pack installed that general packs no longer ship
NOT_PACKED_SECTIONS = ("# Transcription languages", "# Cut-out settings", "# Personal (not packed)")   # per machine / personal
PERSONAL_HEAD = "# Personal (not packed)"
# a Personal line ending in this tag is about this computer alone (its hardware, its paths): it stays in this computer's
# CLAUDE.md and goes into neither OS's sections file, so another Mac or PC never gets it
MACHINE_ONLY = "<!-- this machine only -->"
# the owner's computers only (they come inside owner.bin): traces, own rules, the code check, and OWNER.md
OWNER_CFG = CL / "house-private/setup-pack-owner.json"
# the Unfold text presets for After Effects: their home is house-private (with the build tools and renders); only the owner's
# edition ships the installer part (presets/ and install_presets.sh) with its README (templates/unfold-README.md) as
# ~/.claude/ae-presets/unfold. The general pack leaves them out, and its install clears an older general pack's copy
UNFOLD = CL / "house-private/ae-presets/unfold"
UNFOLD_SHIP = ["presets", "install_presets.sh", "install_presets.ps1"]
OWNER_TEXT = CL / "house-private/setup-pack-owner.md"
# every general file and rules block any setup file has shipped (sha256 per path, block texts by hash): an update uses it to
# tell the pack's own files, unchanged, from files the person changed, and only updates the first kind. Shipped as earlier.json.
HISTORY = HERE / "history.json"
# what each build changed, newest first, shipped in the pack; the next build's entry is written as "## In this build" and
# the build stamps it. setup shows the entries newer than the build a computer has (`sync.py news`)
CHANGES = HERE / "CHANGES.md"
# the stamp of the last build that went through: a newest entry stamped by a build that didn't (a crash, a power cut) is
# stamped again by the next one
LAST_BUILD = HERE / "last-build.txt"
# a small CC0 photo for setup's cut-out test, so no one has to find one online
TEST_PHOTO = HERE / "templates/cutout-test.jpg"
ALLOWED = {"/users/<user>/"}                       # a generic placeholder in a third-party doc, not a real path
CREDIT_OK = ("SETUP.md", "MANIFEST.json", "global/house/protected-tools.md", "global/setup-pack/PROMPT.md",
             "global/setup-pack/pack/SETUP.md", "global/setup-pack/templates/unfold-README.md",
             "skills/markroom/", "skills/logo-recreation/", "skills/animation/references/after-effects.md",
             "global/ae-presets/unfold/README.md",
             "global/mods/pulsewise/", "global/mods/folio/",   # where the tools' maker may be credited: the tools themselves only
             "global/setup-pack/make_pack.py", "global/setup-pack/templates/README-git.md",      # and the builder and git
             "global/setup-pack/templates/PROMPT-git.md", "global/setup-pack/templates/LICENSE-git.txt")   # templates, which name the repos
# Notes, rules and the owner's own skills that name files outside ~/.claude point at nothing on another computer: no setup
# file carries those (a project's tools once stayed behind that way). Each build lists them. Places setup or the system
# makes, where setup files go and where a skill saves its output are fine; so are notes that record one machine or the
# pack itself (OWNER_CFG "outside_ok": note file names). OWNER_CFG "project_roots" (folder names such as a projects
# folder's) also catches relative mentions of a project's files.
OUTSIDE_OK_HOME = {".claude", ".claude.json", ".config", ".cache", ".local", ".npm", ".Trash", "Library", "Downloads",
                   "FolioPacks", "documents/chat-archives"}
OUTSIDE_OK_ABS = ("c:/program", "c:/windows")
_START = r"(?:~|\$HOME|%USERPROFILE%|\$env:USERPROFILE|/[Uu]sers/[^/\s`'\"]+|\b[A-Za-z]:)[\\/]"
PATH_RE = re.compile(_START + r"[^\s`'\"()<>|*]+")              # a bare path ends at a space
SPAN_PATH_RE = re.compile(_START + r"[^`'\"()<>|*]+")           # inside `code` it may hold spaces ("My Projects")

def copytree(src, dst, skip=frozenset()):
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        if any(part in SKIP for part in p.parts) or rel.parts[0] in skip or rel.as_posix().startswith(".claude-plugin/types") or p.name.startswith(".env") and p.name != ".env.example": continue
        if p.is_file():
            q = dst / p.relative_to(src); q.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, q)

def strip_personal(text, own):
    """the packed copy of a rules file without the owner's own notes: drop them from lists, then every line naming one"""
    for n in own:
        text = text.replace(f"`{n}.md`, ", "").replace(f", `{n}.md`", "")
        text = "".join(l for l in text.splitlines(True) if f"{n}.md" not in l)
    return text

def scan(pack, cfg):
    """every owner's trace (and the credited name outside the credits) in the staged pack: [(file, term)]"""
    traces, name, bad = cfg.get("traces", []) + cfg.get("personal_skills", []), cfg.get("credited_name"), []   # the owner's own skills are never named
    for p in sorted(pack.rglob("*")):
        if not p.is_file() or p.name == "owner.bin" or "__pycache__" in p.parts: continue   # caches never ship
        rel = p.relative_to(pack).as_posix()
        raw = p.read_bytes()
        low = (raw.decode("utf-8", "ignore") + "\n" + raw.decode("latin-1", "ignore")).lower()
        for a in ALLOWED: low = low.replace(a, "").replace(a.encode("utf-8").decode("latin-1"), "")   # both readings
        bad += [(rel, t) for t in traces if t in low or t in rel.lower()]
        if name and name in low and not rel.startswith(CREDIT_OK): bad.append((rel, f"{name} (outside the credits)"))
    return bad

def git(*args, check=True):
    """git for fetching: OpenSSL on Windows (schannel's TLS in lsass can bring up a Bonjour / LSA pop-up)"""
    g = ["git"] + (["-c", "http.sslBackend=openssl"] if os.name == "nt" else [])
    r = subprocess.run(g + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0: raise SystemExit(f"git {' '.join(args[:4])} failed: {r.stderr.strip()[-400:]}")
    return r.stdout

def git_fetch(repo, commit, paths, into):
    """a shallow checkout of repo at commit into `into`: only `paths` (and the top-level files) when given"""
    git("init", "-q", str(into)); git("-C", str(into), "remote", "add", "origin", repo)
    if paths: git("-C", str(into), "sparse-checkout", "set", *paths)
    git("-C", str(into), "-c", "core.autocrlf=false", "fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit)
    git("-C", str(into), "-c", "core.autocrlf=false", "checkout", "-q", "FETCH_HEAD")

def upstream_history(repo, src_to_pack, into, commit):
    """every version of every file under the source folders that `repo` ever published, read from its commits and trees
    only (no file contents are downloaded): ({pack path: {git blob id: unix time it was first published}}, the unix time
    of `commit`). setup uses it to tell a maker's older or newer copy of a file from the person's own change."""
    git("init", "-q", str(into)); git("-C", str(into), "remote", "add", "origin", repo)
    git("-C", str(into), "fetch", "-q", "--filter=blob:none", "origin", "HEAD")
    log = git("-C", str(into), "log", "--reverse", "--format=@%ct", "--raw", "--no-abbrev", "--no-renames", "FETCH_HEAD", "--", *src_to_pack)
    seen, at = {}, 0
    for line in log.splitlines():
        if line.startswith("@"): at = int(line[1:]); continue
        if not line.startswith(":") or "\t" not in line: continue
        info, path = line.split("\t", 1); blob = info.split()[3]
        src = next((s for s in src_to_pack if path.startswith(s + "/")), None)
        if src and set(blob) != {"0"}: seen.setdefault(src_to_pack[src] + path[len(src):], {}).setdefault(blob, at)
    return seen, int(git("-C", str(into), "log", "-1", "--format=%ct", commit).strip())

def fetch_sources(tmp):
    """the git edition's downloaded skills: pin each repo to its newest commit, fetch it, and fingerprint every file
    exactly as setup will fetch it. Returns (MANIFEST "downloads", their files {pack path: sha256}, HeyGen's LICENSE,
    every version their makers published {pack path: {blob: time}}, and each skill's pinned commit time)"""
    downloads, files, heygen_licence, upstream, pins = [], {}, None, {}, {}
    for i, d in enumerate(DOWNLOADS):
        commit = git("ls-remote", d["repo"], "HEAD").split()[0]
        into = tmp / f"dl{i}"
        git_fetch(d["repo"], commit, list(d.get("skills", {})), into)
        skills = d.get("skills") or {x.name: x.name for x in sorted(into.iterdir()) if x.is_dir() and x.name.startswith(d["prefix"])}
        hist, when = upstream_history(d["repo"], {src: f"skills/{name}" for src, name in skills.items()}, tmp / f"hist{i}", commit)
        upstream.update(hist); pins.update({name: when for name in skills.values()})
        entry = {"label": d["label"], "repo": d["repo"], "commit": commit, "skills": skills}
        if d.get("group"): entry["group"] = d["group"]
        for src, name in skills.items():
            if not (into / src / "SKILL.md").is_file(): raise SystemExit(f"{d['repo']} has no {src}/SKILL.md at {commit[:8]}")
            for p in sorted((into / src).rglob("*")):
                if p.is_file() and not SKIP & set(p.relative_to(into / src).parts) and p.name not in SKILL_LOCAL.get(name, set()):
                    files[f"skills/{name}/{p.relative_to(into / src).as_posix()}"] = hashlib.sha256(p.read_bytes()).hexdigest()
        stock = {f"skills/{to}": f"skills/{frm}" for to, frm in SKILL_STOCK.items() if to.split("/")[0] in skills.values()}
        for to, frm in stock.items(): files[to] = files[frm]
        if stock: entry["stock"] = stock
        if "heygen-com" in d["repo"] and (into / "LICENSE").is_file(): heygen_licence = (into / "LICENSE").read_bytes()
        downloads.append(entry)
    return downloads, files, heygen_licence, upstream, pins

def retired_history(tmp):
    """HeyGen's published versions of its retired skills, and the time of the commit this pack keeps them at"""
    k = KEPT_RETIRED
    hist, when = upstream_history(k["repo"], {f"skills/{s}": f"skills/{s}" for s in k["skills"]}, tmp / "hist-retired", k["commit"])
    return hist, {s: when for s in k["skills"]}

def keep_retired(root, tmp, licence):
    """HeyGen's retired skills as installed here: HeyGen's licence and a SOURCE.md beside each, and a line at the end of
    every file that differs from HeyGen's own copy (only Markdown is marked; any other changed file stops the build)"""
    k = KEPT_RETIRED
    into = tmp / "retired"
    git_fetch(k["repo"], k["commit"], [f"skills/{s}" for s in k["skills"]], into)
    norm = lambda b: b.replace(b"\r\n", b"\n")
    marked = []
    for s in k["skills"]:
        mine, theirs = root / "skills" / s, into / "skills" / s
        if not mine.is_dir(): continue
        for p in sorted(mine.rglob("*")):
            if not p.is_file(): continue
            rel = p.relative_to(mine).as_posix(); up = theirs / rel
            if up.is_file() and norm(up.read_bytes()) == norm(p.read_bytes()): continue
            if p.suffix != ".md": raise SystemExit(f"{s}/{rel} differs from HeyGen's copy and isn't Markdown: mark the change by hand first")
            what = "was added for this setup pack" if not up.is_file() else "was changed for this setup pack"
            with open(p, "a", encoding="utf-8", newline="\n") as f:
                f.write(f"\n\n---\n\n*This file {what}: it differs from HeyGen's original in "
                        f"{k['repo'].replace('https://', '')} (commit {k['commit'][:8]}).*\n")
            marked.append(f"{s}/{rel}")
        if licence: (mine / "LICENSE").write_bytes(licence)
        (mine / "SOURCE.md").write_text(
            f"# Where {s} comes from\n\n`{s}` is HeyGen's skill from {k['repo'].replace('https://', '')} (`skills/{s}`), as of "
            f"commit `{k['commit'][:8]}` ({k['date']}). HeyGen retired it upstream on 21 October 2026 and folded it into "
            "its `hyperframes` and `media-use` skills; this setup pack keeps it. It is licensed under the Apache License "
            "2.0 (`LICENSE` beside this file). A file that differs from HeyGen's copy says so at its end.\n",
            encoding="utf-8", newline="\n")
    return marked

def outside_ok(s):
    """a path setup or the system makes, or a placeholder"""
    low = s.lower()
    if "<" in s or any(a in low for a in ALLOWED): return True
    if re.match(r"[a-z]:/", low):
        return low.startswith(OUTSIDE_OK_ABS) or bool(re.match(r"c:/[u]sers/[^/]+/(\.claude|appdata)(/|$)", low))
    rest = re.sub(r"^(~|\$home|%userprofile%|\$env:userprofile|/[u]sers/[^/]+)/", "", low)
    return any(rest == x.lower() or rest.startswith(x.lower() + "/") for x in OUTSIDE_OK_HOME)

def outside_refs(pairs, ok_notes=(), roots=()):
    """(pack path, file) pairs of notes, rules and own skills -> {pack path: [paths outside ~/.claude they name]}"""
    found = {}
    for rel, p in pairs:
        if "/originals/" in rel or "/superseded/" in rel or Path(rel).name in ok_notes: continue   # kept for the record
        text, hits = p.read_text(encoding="utf-8", errors="ignore"), []
        for span in re.findall(r"`([^`\n]+)`", text):                   # paths in code marks, spaces and all
            for part in re.split(r"\s+(?=~|\$HOME|%USERPROFILE%|\$env:|/[Uu]sers/|\b[A-Za-z]:[\\/])", span):
                hits += [m.group(0) for m in SPAN_PATH_RE.finditer(part)]
                hits += [part for r in roots if r in part]
        bare = re.sub(r"`[^`\n]+`", " ", text)
        hits += [m.group(0) for m in PATH_RE.finditer(bare)]
        hits += [m.group(0) for r in roots for m in re.finditer(re.escape(r) + r"[^\s`'\"()<>|*,;]*", bare)]
        for s in hits:
            s = s.strip().rstrip(".,;:").replace("\\", "/")
            if s and not outside_ok(s) and s not in found.setdefault(rel, []): found[rel].append(s)
    return {k: v for k, v in found.items() if v}

def ref_pairs(root, own_skills=()):
    """what outside_refs reads in a staged pack: the rules, house notes, private notes and the owner's own skills (Markdown);
    third-party skills are left out, their paths are examples"""
    bases = [root / "global"] + [root / "skills" / s for s in sorted(OWN_SKILLS | set(own_skills))]
    return [(p.relative_to(root).as_posix(), p) for b in bases if b.exists() for p in sorted(b.rglob("*.md"))]

def report_outside(found):
    if not found: return
    print("\nPOINTS OUTSIDE THE PACK: these notes and skills name files outside ~/.claude, which no setup file carries, so on "
          "another computer they point at nothing. Bring what's needed into ~/.claude (a skill, or house-private for private "
          "things), or say in the note that it stays on one machine:")
    for rel, paths in sorted(found.items()):
        print(f"  {rel}: {', '.join(paths[:3])}" + (f" (+{len(paths) - 3} more)" if len(paths) > 3 else ""))

def listing(root):
    """every pack file under global/, skills/ and extras/ with its sha256"""
    files = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and rel.split("/")[0] in ("global", "skills", "extras"):
            files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return files

def rmtree_force(p):
    def again(f, path, _):
        try: os.chmod(path, 0o700); f(path)
        except OSError: pass
    shutil.rmtree(p, onerror=again)

def write_repo(folder, subs, downloads):
    """the git edition as a repository's files: the staged pack at the top, plus its README, PROMPT.md and LICENSE from
    the templates. The folder must be empty or an earlier git edition (its .git is kept)."""
    folder.mkdir(parents=True, exist_ok=True)
    kids = [p for p in folder.iterdir() if p.name != ".git"]
    if kids and not (folder / "MANIFEST.json").is_file():
        raise SystemExit(f"{folder} holds other files: give an empty folder or an earlier git edition's repo")
    for p in kids:
        if p.is_symlink(): raise SystemExit(f"{p} is a link: not clearing the folder")
        rmtree_force(p) if p.is_dir() else p.unlink()
    for p in sorted(PACK.rglob("*")):
        if not p.is_file() or p.name in ("owner.bin", "OWNER.md", ".DS_Store") or "__pycache__" in p.parts: continue
        q = folder / p.relative_to(PACK); q.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, q)
    for name, tpl in GIT_TEMPLATES.items():
        t = (HERE / tpl).read_text(encoding="utf-8")
        for k, v in subs.items(): t = t.replace(k, v)
        if "@@" in t: raise SystemExit(f"{tpl}: a placeholder is left ({t[t.index('@@'):t.index('@@') + 30]})")
        (folder / name).write_text(t, encoding="utf-8", newline="\n")
    (folder / ".gitattributes").write_text("# every file exactly as built: MANIFEST.json checks each one's bytes\n* -text\n", encoding="utf-8", newline="\n")
    (folder / ".gitignore").write_text("__pycache__/\n.DS_Store\n# the skills setup downloads land here while it installs\n" +
                                       "".join(f"/skills/{n}/\n" for d in downloads for n in d["skills"].values()), encoding="utf-8", newline="\n")

def personal_section(tail):
    """the owner's Personal section from CLAUDE.md's sections after the rules block, as both OS sections files carry it:
    without the lines marked MACHINE_ONLY. An unmarked line that names this PC or this Mac gets a NOTE, as it would
    reach other computers"""
    mine = next(x for x in re.split(r"\n(?=# (?!#))", "\n" + tail) if x.lstrip().startswith(PERSONAL_HEAD))
    keep = [ln for ln in mine.splitlines() if MACHINE_ONLY not in ln]
    for ln in keep:
        if ln.lstrip().startswith("-") and re.search(r"\bthis (PC|Mac)\b", ln, re.I):
            print(f"NOTE: a Personal line names this computer but isn't marked {MACHINE_ONLY}, so other computers get it "
                  f"too: {ln.strip()[:90]}")
    return "\n".join(keep)

def stage(root, personal, own, leave_out=(), tools=True, own_skills=(), leave_skills=()):
    """stage the pack's own files (global/, skills/, extras/) into root: the owner's edition when personal, without the
    house-private folders in leave_out (work still in progress); tools=False leaves out MarkRoom, PulseWise and Folio;
    own_skills (the owner's own skills) are left out of the general pack and ship only in the owner's edition"""
    for sub in ["global", "skills", "memory", "project", "extras"]:
        shutil.rmtree(root / sub, ignore_errors=True)
    (root / "global/hooks").mkdir(parents=True)
    # only the "# Global rules" block goes everywhere; later top-level sections are per OS or personal
    rules = (CL / "CLAUDE.md").read_text(encoding="utf-8")
    nxt = re.search(r"\n# (?!#)", rules[rules.index("# Global rules") + 1:])
    cut = rules.index("# Global rules") + 1 + nxt.start() + 1 if nxt else len(rules)
    block = rules[rules.index("# Global rules"):cut]
    (root / "global/CLAUDE.md").write_text((block if personal else strip_personal(block, own)).rstrip() + "\n", encoding="utf-8", newline="\n")
    # each OS's own sections: the Mac's from this CLAUDE.md on a Mac (kept as the template too), else from the template
    mac_t = HERE / "templates/CLAUDE-sections-mac.md"
    if sys.platform == "darwin":
        mac = "\n\n".join(x.strip() for x in re.split(r"\n(?=# (?!#))", "\n" + rules[cut:])
                          if x.strip() and not x.lstrip().startswith(NOT_PACKED_SECTIONS)) + "\n"
        if not mac_t.exists() or mac_t.read_text(encoding="utf-8") != mac: mac_t.write_text(mac, encoding="utf-8", newline="\n")
    else: mac = mac_t.read_text(encoding="utf-8")
    (root / "global/CLAUDE-sections-mac.md").write_text(mac, encoding="utf-8", newline="\n")
    # video-use's local path fixes, so a new clone matches this one (sync.py applies the patch after cloning)
    vu = CL / "skills/video-use"
    d = subprocess.run(["git", "-C", str(vu), "diff", "--", "helpers/render.py", "helpers/grade.py"],
                       capture_output=True, text=True, encoding="utf-8").stdout if (vu / ".git").exists() else ""
    if TEST_PHOTO.exists(): (root / "extras").mkdir(exist_ok=True); shutil.copy2(TEST_PHOTO, root / "extras/cutout-test.jpg")
    if d: (root / "extras").mkdir(exist_ok=True); (root / "extras/video-use-windows-paths.patch").write_text(d, encoding="utf-8", newline="\n")
    shutil.copy2(CL / "hooks/block-elevenlabs-transcription.sh", root / "global/hooks/")    # macOS / Linux
    shutil.copy2(CL / "hooks/block-elevenlabs-transcription.py", root / "global/hooks/")    # Windows (same rules)
    shutil.copy2(HERE / "templates/CLAUDE-sections-windows.md", root / "global/")          # Windows' own sections
    if personal:                                                   # the owner's Personal section goes to both OSes
        mine = personal_section(rules[cut:])
        for f in ("global/CLAUDE-sections-mac.md", "global/CLAUDE-sections-windows.md"):
            (root / f).write_text((root / f).read_text(encoding="utf-8").rstrip() + "\n\n" + mine.strip() + "\n", encoding="utf-8", newline="\n")
    for s in sorted((CL / "skills").iterdir()):
        if s.is_dir() and s.name not in LOCAL_SKILLS and (tools or s.name not in TOOL_SKILLS) and (personal or s.name not in own_skills) \
                and s.name not in leave_skills:
            copytree(s, root / "skills" / s.name, skip=SKILL_LOCAL.get(s.name, set()))
    for dst, src in SKILL_STOCK.items():                           # the stock settings, never this computer's own
        if (root / "skills" / src).exists(): shutil.copy2(root / "skills" / src, root / "skills" / dst)
    if personal:                                                   # the owner's own computers: every note, kept whole
        copytree(CL / "house", root / "global/house")
        copytree(CL / "house-private", root / "global/house-private", skip=set(leave_out))
    else:                                                          # general notes only (house-private is never read)
        copytree(CL / "house", root / "global/house", skip={f"{n}.md" for n in own})
        readme = root / "global/house/README.md"; readme.write_text(strip_personal(readme.read_text(encoding="utf-8"), own), encoding="utf-8", newline="\n")
    if personal and UNFOLD.exists():                               # the Unfold presets' installer part, owner's edition only
        u = root / "global/ae-presets/unfold"
        copytree(UNFOLD, u, skip={x for x in (y.name for y in UNFOLD.iterdir()) if x not in UNFOLD_SHIP})
        shutil.copy2(HERE / "templates/unfold-README.md", u / "README.md")
    # the mods (PulseWise, which carries its helper and puts it in ~/.claude/progress itself; Folio) and the local marketplace
    mods = [m for m in MODS if tools and (CL / "mods" / m / ".claude-plugin/plugin.json").exists()]   # a mod not here as a folder isn't carried
    for m in mods: copytree(CL / "mods" / m, root / "global/mods" / m, skip=MOD_DEV)
    if mods:
        (root / "global/mods/.claude-plugin").mkdir(parents=True)
        mk = CL / "mods/.claude-plugin/marketplace.json"
        market = json.loads(mk.read_text(encoding="utf-8")) if mk.exists() else {"name": "local-mods", "owner": {"name": "local"}}
        listed = {x["name"]: x for x in market.get("plugins", [])}
        market["plugins"] = [listed.get(m) or {"name": m, "source": f"./{m}", "description":
                             json.loads((CL / "mods" / m / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["description"]} for m in mods]
        (root / "global/mods/.claude-plugin/marketplace.json").write_text(json.dumps(market, indent=2) + "\n", encoding="utf-8", newline="\n")
    for f in BUILDER_FILES:                                        # the builder, so every computer can build its own
        if f in OWNER_BUILDER_FILES and not personal: continue     # (Unfold's README template: owner's edition only)
        q = root / "global/setup-pack" / f; q.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(HERE / f, q)
    # secret scan
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".sh", ".md", ".json", ".mjs", ".js", ".txt", ".env"):
            t = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"(sk-[A-Za-z0-9]{20,}|sk_[a-f0-9]{30,}|AKIA[0-9A-Z]{16}|hf_[A-Za-z0-9]{30,})", t):
                raise SystemExit(f"possible secret in {p} - not packing")
    for p in list(root.rglob(".DS_Store")): p.unlink()             # Finder files: never listed, never zipped
    return listing(root)

def stamp_changes(build, version):
    """CHANGES.md with its "## In this build" entry stamped with this build, copied into the pack; the stamped text, for
    the builder to keep once the build has gone through (None when there is nothing to stamp)"""
    if not CHANGES.exists(): print("no CHANGES.md: this build has no what's-new list"); return None
    t = CHANGES.read_text(encoding="utf-8")
    top = re.search(r"(?m)^## Build (\S+) · version \S+$", t)
    done = LAST_BUILD.read_text(encoding="utf-8").strip() if LAST_BUILD.exists() else ""
    if "## In this build" not in t and top and top.group(1) != done:     # stamped by a build that never finished
        t = t[:top.start()] + "## In this build" + t[top.end():]
    if "## In this build" not in t:
        print("CHANGES.md has no '## In this build' entry: this build adds nothing to its what's-new list")
        (PACK / "CHANGES.md").write_text(t, encoding="utf-8", newline="\n"); return None
    t = t.replace("## In this build", f"## Build {build} · version {version}", 1)
    (PACK / "CHANGES.md").write_text(t, encoding="utf-8", newline="\n")
    return t

def lock():
    """sync.py's owner lock (one copy of the code)"""
    src = (PACK / "sync.py").read_text(encoding="utf-8")
    ns = {"hashlib": hashlib, "hmac": hmac, "os": os}
    exec(src[src.index("# --- owner lock"):src.index("# --- end owner lock")], ns)
    return ns

def code_ok(cfg, code, ns):
    """the code against the owner's check, which only the owner's computers hold"""
    c = cfg["check"]
    _, mk = ns["owner_keys"](code, bytes.fromhex(c["salt"]), c["rounds"])
    return hmac.compare_digest(hmac.new(mk, b"setup-pack owner check", "sha256").hexdigest(), c["tag"])

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", action="store_true", help="the full setup file, with the owner's own edition locked inside")
    ap.add_argument("--owner-code", help="the owner code, exactly as given (or set OWNER_CODE)")
    ap.add_argument("--out", default=str(Path.home() / "Downloads"), help="where the zip and PROMPT.md go (default ~/Downloads)")
    ap.add_argument("--check-code", action="store_true", help="only check the owner code (before anything locked is moved or packed); builds nothing")
    ap.add_argument("--git", action="store_true", help="the git edition: no tools inside; setup installs the ticked ones from GitHub")
    ap.add_argument("--repo", help="with --git: write the git edition as a repository's files into this folder (empty, or an "
                                   "earlier git edition's repo) instead of a zip")
    ap.add_argument("--no-tools", action="store_true", help="leave MarkRoom, PulseWise and Folio out of a zip (for an owner's "
                                   "computer that keeps its own working copies of them; its loaded copies stay as they are)")
    ap.add_argument("--version", help="keep a published version number (YYYY-MM-DD.HHMMSS) for this build; every build still "
                                      "gets its own stamp, which setup uses to tell builds apart and list what's new")
    a = ap.parse_args()
    if a.repo and not a.git: raise SystemExit("--repo is for the git edition: add --git")
    if a.version and not re.fullmatch(r"\d{4}-\d{2}-\d{2}\.\d{6}", a.version): raise SystemExit("--version looks like 2026-11-06.073618")
    out_dir = Path(os.path.expanduser(a.out)).resolve(); out_dir.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(OWNER_CFG.read_text(encoding="utf-8")) if OWNER_CFG.exists() else None
    own = cfg.get("personal_house", []) if cfg else []
    own_skills = cfg.get("personal_skills", []) if cfg else []
    ns, code, full = lock(), a.owner_code or os.environ.get("OWNER_CODE", ""), a.full
    if a.check_code:
        if not cfg: print("This computer has no owner's edition: nothing here is locked."); return
        print("Code OK." if code and code_ok(cfg, code, ns) else "Code was wrong."); return
    if full and a.git:
        print("The git edition is general only (the owner's computers keep the tools as folders): building the general git edition."); full = False
    if full and not cfg:
        print("This computer has no owner's edition: building the general setup file."); full = False
    elif full and not (code and code_ok(cfg, code, ns)):
        print("Code was wrong: building the general setup file."); full = False
    build = time.strftime("%Y-%m-%d.%H%M%S")                       # this build's own stamp, whatever the version says
    version = a.version or build
    meta = {"version": version, "build": build, "made": time.strftime("%Y-%m-%d %H:%M"), "retired_skills": RETIRED, "seed_skills": SEED_SKILLS,
            "seed_files": ["skills/" + k for k in SKILL_STOCK],
            "replaced_house_notes": REPLACED_HOUSE, "retired_mods": RETIRED_MODS}
    changes = stamp_changes(build, version)                        # this build's what's-new entry, stamped first so every
    if changes: CHANGES.write_text(changes, encoding="utf-8", newline="\n")   # copy (the pack's, the builder's) carries it
    if a.git: meta["tool_source"] = {"repo": TOOL_REPO, "marketplace": TOOL_MARKETPLACE, "tools": ["folio", "pulsewise", "markroom"]}
    (PACK / ns["OWNER_FILE"]).unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        mine = Path(tmp)
        mine_files = stage(mine, True, own, cfg.get("leave_out_private", []), tools=not a.no_tools) if full else {}
        downloads, dl_files, marked = [], {}, []
        if a.git:   # third-party skills come from their makers' repos at install; HeyGen's retired ones stay, with its licence
            (mine / "git").mkdir()
            downloads, dl_files, heygen_licence, upstream, pins = fetch_sources(mine / "git")
            leave = {n for d in downloads for n in d["skills"].values()} | \
                    {s.name for s in (CL / "skills").iterdir() for pre in OPTIONAL_SKILLS.values() if s.name.startswith(pre)}
            stage(PACK, False, own, tools=False, own_skills=own_skills, leave_skills=leave)
            marked = keep_retired(PACK, mine / "git", heygen_licence)
            r_hist, r_pins = retired_history(mine / "git")
            meta["downloads"] = downloads
            # every version each maker published, so setup can tell their older or newer copy from the person's own change
            meta["upstream"] = {**upstream, **r_hist}; meta["upstream_pins"] = {**pins, **r_pins}
        else:
            stage(PACK, False, own, tools=not a.no_tools, own_skills=own_skills)
        shipped_files = listing(PACK)                              # what is inside the pack (or the repo)
        files = {**shipped_files, **dl_files}                      # plus what setup downloads, each with its fingerprint
        meta["optional_skills"] = {g: sorted({r.split("/")[1] for r in files if r.startswith(f"skills/{pre}")})
                                   for g, pre in OPTIONAL_SKILLS.items()}
        (PACK / "MANIFEST.json").write_text(json.dumps({**meta, "edition": "shareable",
            "retired_house_notes": RETIRED_HOUSE + own, "retired_folders": RETIRED_FOLDERS, "files": files}, indent=1), encoding="utf-8", newline="\n")
        hist = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {"files": {}, "blocks": {}}
        for r, h in files.items():
            if h not in hist["files"].setdefault(r, []): hist["files"][r].append(h)
        blk = (PACK / "global/CLAUDE.md").read_text(encoding="utf-8")
        hist["blocks"][hashlib.sha256(blk.strip().encode("utf-8")).hexdigest()] = blk
        HISTORY.write_text(json.dumps(hist, indent=0), encoding="utf-8", newline="\n")
        hide = [x.lower() for x in (cfg or {}).get("traces", []) + own_skills]   # never ship a path naming the owner's own things
        (PACK / "earlier.json").write_text(json.dumps({                 # block texts stay home: their fingerprints are enough
            "files": {r: hs for r, hs in hist["files"].items() if not any(x in r.lower() for x in hide)},
            "blocks": {k: "" for k in hist["blocks"]}}), encoding="utf-8", newline="\n")
        bad = scan(PACK, cfg) if cfg else []
        if bad:
            for f, t in bad: print(f"  personal trace: {t!r} in {f}")
            raise SystemExit(f"{len(bad)} personal trace(s) found - not packing")
        extra = sorted(r for r, h in mine_files.items() if files.get(r) != h)
        outside = outside_refs(ref_pairs(mine if full else PACK, own_skills if full else ()),   # read here, while staged
                               (cfg or {}).get("outside_ok", []), (cfg or {}).get("project_roots", []))
        if full:   # the owner's edition: only what differs from the general pack is locked into owner.bin
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for r in extra: z.write(mine / r, r)
                z.writestr("MANIFEST.json", json.dumps({**meta, "edition": "personal", "retired_house_notes": RETIRED_HOUSE,
                           "files": mine_files}, indent=1))
                z.writestr("OWNER.md", OWNER_TEXT.read_text(encoding="utf-8"))
            blob = ns["owner_lock"](buf.getvalue(), code)
            if ns["owner_unlock"](blob, code) != buf.getvalue(): raise SystemExit("owner lock round trip failed - not packing")
            if ns["owner_unlock"](blob, code.swapcase() + "x") is not None: raise SystemExit("owner lock opens with a wrong code - not packing")
            (PACK / ns["OWNER_FILE"]).write_bytes(blob)
    if a.git:                                                      # a public repo needs every third-party skill's licence
        shipped = sorted({r.split("/")[1] for r in shipped_files if r.startswith("skills/")} - OWN_SKILLS)
        bare = [s for s in shipped if not any(re.match(r"(?i)(licen[cs]e|copying)", Path(r).name) for r in shipped_files if r.startswith(f"skills/{s}/") and r.count("/") == 2)]
        if bare: print("\nBEFORE THIS GOES IN A PUBLIC REPO: these third-party skills have no licence file. Check on each one's source "
                       f"that it may be redistributed (a private repo doesn't need this): {', '.join(bare)}")
        for d in downloads: print(f"downloaded at install: {d['label']} from {d['repo']} at {d['commit'][:8]}: {', '.join(d['skills'].values())}")
        if marked: print("marked as changed from HeyGen's copy: " + ", ".join(marked))
    report_outside(outside)
    if a.repo:
        subs = {"@@REPO@@": GIT_REPO, "@@TOOL_REPO@@": TOOL_REPO, "@@MARKETPLACE@@": TOOL_MARKETPLACE, "@@VERSION@@": version,
                "@@HIGGSFIELD_COUNT@@": str(len(meta["optional_skills"].get("higgsfield", [])))}
        repo = Path(os.path.expanduser(a.repo)).resolve()
        write_repo(repo, subs, downloads)
        size = sum(p.stat().st_size for p in repo.rglob("*") if p.is_file() and ".git" not in p.relative_to(repo).parts)
        print(f"Built the git edition {version} as a repository: {repo} ({len(shipped_files)} pack files, {size / 1e6:.1f} MB; "
              f"{len(dl_files)} more files downloaded at install)")
        LAST_BUILD.write_text(build + "\n", encoding="utf-8", newline="\n")
        return
    out = out_dir / f"{NAME}-{'git-' if a.git else ''}{version}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(PACK.rglob("*")):
            if not p.is_file() or p.name == ".DS_Store" or "__pycache__" in p.parts: continue
            z.write(p, f"{NAME}/" + p.relative_to(PACK).as_posix())
    if (out_dir / "PROMPT.md").resolve() != (HERE / "PROMPT.md").resolve(): shutil.copy2(HERE / "PROMPT.md", out_dir / "PROMPT.md")
    kind = f"full setup file ({len(files)} files + {len(extra)} in the owner's edition)" if full else f"general setup file ({len(files)} files)"
    carried = sorted({r.split("/")[2] for r in files if r.startswith("global/mods/") and not r.startswith("global/mods/.")} |
                     ({"markroom"} if any(r.startswith("skills/markroom/") for r in files) else set()))
    kind += ", git edition: no tools inside" if a.git else f", carrying {', '.join(carried) or 'none of the three tools'}"
    print(f"Built the {kind}: {out} ({out.stat().st_size / 1e6:.1f} MB), with PROMPT.md beside it")
    LAST_BUILD.write_text(build + "\n", encoding="utf-8", newline="\n")

if __name__ == "__main__":
    main()
