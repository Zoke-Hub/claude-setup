#!/usr/bin/env python3
"""Readable archive of a long Claude Code session, kept inside the project so it can be revisited any time.

    python3 ~/.claude/skills/chat-archive/scripts/build_archive.py [session-id] [--project DIR] [--out FOLDER]
        # (re)builds <project>/chat-archive/<title>.html; the project is the folder the session runs in (default: cwd);
        # --out writes the archive to FOLDER instead (e.g. for a session that wasn't opened in a project folder)

Whenever it runs, at any point in a chat, it archives the WHOLE session from the first message: it reads the full saved
transcript (~/.claude/projects/<folder>/<session>.jsonl), which keeps everything, compactions included.

The desktop app only loads the end of a very long session, and Claude Code deletes old transcripts after ~30 days,
so this writes everything that was said into one self-contained HTML page:
  - every message you typed (including the ones sent while Claude was working), in order, with the time
  - every reply Claude wrote
  - every file Claude sent you, linked to where it lives on disk, and every Artifact link
  - under each reply, a collapsed "work log" of the steps behind it (commands, files read and written)
  - the two context summaries written when the conversation was compacted
Pictures that were looked at are linked by path, not embedded, so the page stays small.
It also keeps a gzip copy of the raw transcript next to the page (raw/), which never expires.
"""
import gzip, html, json, os, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

_p = sys.argv.index("--project") + 1 if "--project" in sys.argv else 0
_o = sys.argv.index("--out") + 1 if "--out" in sys.argv else 0
ROOT = Path(sys.argv[_p]).expanduser().resolve() if _p else Path.cwd().resolve()   # the folder the session runs in
HERE = Path(sys.argv[_o]).expanduser().resolve() if _o else ROOT / "chat-archive"  # where the archive is written
HERE.mkdir(parents=True, exist_ok=True)
# Claude Code keeps this project's transcripts in ~/.claude/projects/<project path with every non-alphanumeric -> "-">
PROJ = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
# session: pass its id as the first argument, or the most recently updated transcript is used
_args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("-") and i not in (_p, _o)]
if not _args and not list(PROJ.glob("*.jsonl")):
    sys.exit(f"No Claude Code sessions found for {ROOT} (looked in {PROJ}). Run this from the folder the session was opened in, or pass --project.")
SESSION = _args[0] if _args else max(PROJ.glob("*.jsonl"), key=lambda q: q.stat().st_mtime).stem
SRC = PROJ / f"{SESSION}.jsonl"

def title():
    try: return json.loads((PROJ / SESSION / "custom-title.json").read_text())["customTitle"]
    except Exception: return "Claude session"

def local_time(ts):
    try: return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%a %d %b %Y, %H:%M")
    except Exception: return ts or ""

def strip_reminders(t):
    t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S)
    return t.strip()

def link(path, label=None):
    """file link relative to this page when the file is under the project; plain text otherwise"""
    p = Path(path)
    label = label or p.name
    try:
        rel = os.path.relpath(p, HERE)
        if str(p).startswith(str(ROOT)):
            exists = p.exists()
            return f'<a href="{html.escape(rel)}">{html.escape(label)}</a>' + ("" if exists else ' <span class="gone">(moved or deleted)</span>')
    except Exception:
        pass
    return f'<code title="{html.escape(str(p))}">{html.escape(label)}</code> <span class="gone">(temporary file)</span>'

URL = re.compile(r"(https://claude\.ai/(?:code/)?artifact/[A-Za-z0-9-]+)")
def fmt(text):
    """light markdown: code, bold, links, paragraphs and lists"""
    t = html.escape(text)
    t = re.sub(r"```(\w*)\n(.*?)```", lambda m: "<pre>" + m.group(2) + "</pre>", t, flags=re.S)
    t = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*\n]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r'(?<!href=")(?<!">)(https?://[^\s<)]+)', r'<a href="\1">\1</a>', t)
    t = re.sub(r"^#{1,4} (.+)$", r"<h4>\1</h4>", t, flags=re.M)
    t = re.sub(r"^\s*[-*] (.+)$", r"<li>\1</li>", t, flags=re.M)
    t = re.sub(r"(<li>.*?</li>\n?)+", lambda m: "<ul>" + m.group(0) + "</ul>", t, flags=re.S)
    t = "".join(f"<p>{p}</p>" if not p.startswith(("<pre>", "<ul>", "<h4>")) else p for p in re.split(r"\n{2,}", t))
    return t.replace("\n", "<br>")

def tool_line(b):
    n, i = b.get("name", ""), b.get("input", {}) or {}
    if n == "Bash": return "Ran: " + (i.get("description") or i.get("command", "")[:120])
    if n == "Read": return "Read " + link(i.get("file_path", ""))
    if n in ("Write", "Edit"): return ("Wrote " if n == "Write" else "Edited ") + link(i.get("file_path", ""))
    if n == "Agent": return "Sub-agent: " + html.escape(i.get("description", ""))
    if n in ("WebSearch", "WebFetch"): return n + ": " + html.escape(str(i.get("query") or i.get("url") or "")[:140])
    if n == "ArtifactData": return f"Board database: {html.escape(i.get('action',''))} {html.escape(i.get('collection','') or '')}"
    if n == "Artifact": return "Artifact: " + html.escape(i.get("action", "publish")) + " " + html.escape(Path(i.get("file_path", "") or "").name)
    if n == "Skill": return "Used skill: " + html.escape(i.get("skill", ""))
    if n.startswith("mcp__"): return "Tool: " + html.escape(n.split("__")[-1])
    return html.escape(n)

def esc(s): return html.escape(s or "")

def build():
    items, log = [], []           # items: ("you"|"claude"|"file"|"summary"|"artifact", ts, html)
    seen_mid = set()
    def flush_log():
        if log:
            items.append(("log", None, "".join(f"<li>{x}</li>" for x in log)))
            log.clear()
    for line in open(SRC, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        t, ts = d.get("type"), d.get("timestamp")
        msg = d.get("message") or {}
        c = msg.get("content")
        if t == "attachment":
            a = d.get("attachment") or {}
            if isinstance(a, dict) and a.get("type") == "queued_command" and isinstance(a.get("prompt"), str):
                key = a["prompt"].strip()
                if key and key not in seen_mid and not key.startswith("<"):
                    seen_mid.add(key); flush_log()
                    items.append(("you", ts, fmt(key) + '<div class="note">sent while Claude was working</div>'))
            continue
        if t == "user":
            if d.get("isCompactSummary"):
                flush_log()
                txt = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))
                items.append(("summary", ts, fmt(strip_reminders(txt))))
                continue
            if isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict): continue
                    if b.get("type") == "tool_result":           # messages typed while Claude was working arrive inside tool results
                        rc = b.get("content")
                        rt = rc if isinstance(rc, str) else " ".join(x.get("text", "") for x in (rc or []) if isinstance(x, dict) and x.get("type") == "text")
                        for m in re.finditer(r"The user sent a new message while you were working:\n(.*?)\n\nThis is how Claude Code surfaces", rt, re.S):
                            key = m.group(1).strip()
                            if key not in seen_mid:
                                seen_mid.add(key); flush_log()
                                items.append(("you", ts, fmt(key) + '<div class="note">sent while Claude was working</div>'))
                    elif b.get("type") == "text" and not d.get("isMeta"):
                        txt = strip_reminders(b.get("text", ""))
                        if txt and not txt.startswith(("<local-command", "[Request interrupted")):
                            cm = re.search(r"<command-name>(.*?)</command-name>.*?<command-args>(.*?)</command-args>", txt, re.S)
                            flush_log()
                            items.append(("you", ts, fmt(f"{cm.group(1)} {cm.group(2)}".strip()) if cm else fmt(txt)))
            elif isinstance(c, str) and not d.get("isMeta"):
                txt = strip_reminders(c)
                if txt and not txt.startswith(("<local-command", "[Request interrupted")):
                    cm = re.search(r"<command-name>(.*?)</command-name>.*?<command-args>(.*?)</command-args>", txt, re.S)
                    flush_log()
                    items.append(("you", ts, fmt(f"{cm.group(1)} {cm.group(2)}".strip()) if cm else fmt(txt)))
        elif t == "assistant" and isinstance(c, list):
            for b in c:
                if b.get("type") == "text" and b.get("text", "").strip():
                    flush_log()
                    items.append(("claude", ts, fmt(b["text"])))
                elif b.get("type") == "tool_use":
                    i = b.get("input", {}) or {}
                    if b.get("name") == "SendUserFile":
                        flush_log()
                        files = " · ".join(link(p) for p in i.get("files", []))
                        items.append(("file", ts, files + (f'<div class="cap">{esc(i.get("caption"))}</div>' if i.get("caption") else "")))
                    else:
                        log.append(tool_line(b))
    flush_log()
    return items

def dedupe(items):
    seen, out = set(), []
    for it in items:
        key = (it[0], it[1], it[2]) if it[0] != "log" else None
        if key and key in seen: continue
        if key: seen.add(key)
        out.append(it)
    # a re-logged block can leave its work log orphaned between two copies: drop logs that follow nothing new
    clean = []
    for it in out:
        if it[0] == "log" and clean and clean[-1][0] == "log": continue
        clean.append(it)
    # keep time order (re-logged copies were appended later in the file)
    order, last = [], ""
    for it in clean:
        if it[1]: last = it[1]
        order.append((last, len(order), it))
    order.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in order]

def page(items):
    T = title()
    out, day = [], None
    toc = []
    k = 0
    for kind, ts, body in items:
        dd = local_time(ts)[:15] if ts else None
        if dd and dd != day:
            day = dd; k += 1
            out.append(f'<h2 id="d{k}">{esc(dd)}</h2>'); toc.append(f'<a href="#d{k}">{esc(dd)}</a>')
        tm = f'<span class="tm">{esc(local_time(ts)[-5:])}</span>' if ts else ""
        if kind == "you": out.append(f'<div class="msg you"><div class="who">You {tm}</div>{body}</div>')
        elif kind == "claude": out.append(f'<div class="msg claude"><div class="who">Claude {tm}</div>{body}</div>')
        elif kind == "file": out.append(f'<div class="msg file"><div class="who">File sent {tm}</div>{body}</div>')
        elif kind == "summary": out.append(f'<details class="msg summary"><summary>Context summary (written when the conversation was compacted) {tm}</summary>{body}</details>')
        elif kind == "log": out.append(f'<details class="log"><summary>work log</summary><ul>{body}</ul></details>')
    n_you = sum(1 for i in items if i[0] == "you")
    css = """
:root{--paper:#F5EAD8;--ink:#201E1D;--brown:#643312;--sage:#AFBC8A;--card:#fffaf1;--muted:#7b6a5a;--line:#e3d5bf}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#1c1a18;--ink:#efe6d8;--brown:#d9a679;--card:#262320;--muted:#a8998a;--line:#3a352f}}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:28px;margin:0 0 4px} .sub{color:var(--muted);margin-bottom:18px}
h2{font:600 13px/1 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--brown);margin:34px 0 10px;padding-top:10px;border-top:1px solid var(--line)}
nav{font:13px system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:8px 14px;margin-bottom:10px} nav a{color:var(--brown)}
.msg{border-radius:10px;padding:10px 14px;margin:10px 0;overflow-wrap:anywhere}
.you{background:var(--card);border-left:4px solid var(--brown)}
.claude{background:transparent;border-left:4px solid var(--line)}
.file{background:var(--card);border-left:4px solid var(--sage);font:14px system-ui,sans-serif}
.summary{background:var(--card);border:1px dashed var(--line);font-size:14px}
.who{font:600 12px system-ui,sans-serif;color:var(--muted);margin-bottom:4px} .tm{font-weight:400;margin-left:6px}
.note,.cap{font:12px system-ui,sans-serif;color:var(--muted);margin-top:4px}
.gone{font:11px system-ui,sans-serif;color:var(--muted)}
details.log{margin:0 0 6px 18px;font:12px system-ui,sans-serif;color:var(--muted)} details.log ul{margin:6px 0;padding-left:18px}
summary{cursor:pointer} code{font:13px ui-monospace,Menlo,monospace;background:rgba(127,127,127,.12);padding:1px 4px;border-radius:4px}
pre{white-space:pre-wrap;background:rgba(127,127,127,.12);padding:8px;border-radius:6px;font:13px ui-monospace,Menlo,monospace}
a{color:var(--brown)} p{margin:.4em 0} ul{margin:.3em 0}
@media (max-width:600px){main{padding:16px}}
"""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(T)} · chat archive</title><style>{css}</style></head><body><main>
<h1>{esc(T)}</h1>
<div class="sub">Full chat archive · {n_you} messages from you · built {datetime.now().strftime('%d %b %Y, %H:%M')} from the session transcript. Re-run <code>chat-archive/build_archive.py</code> to update it.</div>
<nav>{''.join(toc)}</nav>
{''.join(out)}
</main></body></html>"""

if __name__ == "__main__":
    items = dedupe(build())
    T = re.sub(r"[^\w\- ]+", "", title()).strip() or "session"
    out = HERE / f"{T} - chat archive.html"
    out.write_text(page(items), encoding="utf-8")
    raw = HERE / "raw"; raw.mkdir(exist_ok=True)
    gz = raw / f"{SESSION}.jsonl.gz"
    with open(SRC, "rb") as fi, gzip.open(gz, "wb", compresslevel=6) as fo: shutil.copyfileobj(fi, fo)
    print(out, f"{out.stat().st_size/1e6:.1f} MB ·", sum(1 for i in items if i[0]=="you"), "messages from you ·", gz.name, f"{gz.stat().st_size/1e6:.0f} MB")
