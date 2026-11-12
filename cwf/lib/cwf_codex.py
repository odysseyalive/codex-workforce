"""Codex adapter for the claude-workforce sensory layer.

The sense logic lives, unmodified, in upstream/claude-workforce/workforce/bin. This module
replaces only the Claude-specific edges around it, as agreed with cw-dev (2026-11-11):

  payload in      Codex hook input already uses Claude's field names; we add
                  `scratchpad_dir` (Codex sends none) and a converted `transcript_path`.
  transcript      Codex rollout JSONL is rewritten into Claude-shaped JSONL, so the
                  upstream walkers (`TL._read_lines`, `current_turn`, `turn_rows`,
                  `confirmed_reply`) run unchanged.
  paths           `issues_dir` and widen's `instruments` are patched on every load of the
                  upstream modules (see `install_patches`). Nothing writes under `.claude/`.
  output          Stop blocks carry a "Stop hook feedback:" prefix, because Codex replays
                  a block's reason as a new user prompt and wf-task-tag's INJECTED rule
                  must recognise it as injected, not as the user's words.
"""
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
UPSTREAM_BIN = os.path.join(REPO, "upstream", "claude-workforce", "workforce", "bin")
STATE_DIRNAME = ".codex-workforce"
RESUME_FILE = "RESUME.md"
RESUME_LIMIT = 12000
# How Codex opens the context it injects as user-role messages (codex-cli 0.167 rollouts).
INJECTED_PREFIXES = ("# AGENTS.md instructions", "<environment_context>", "<permissions",
                     "<skills_instructions>", "<collaboration_mode>", "<user_instructions>")
FEEDBACK_PREFIX = "Stop hook feedback:\n"

# Codex tool names -> the Claude names the upstream evidence counters understand.
TOOL_MAP = {
    "exec_command": "Bash",
    "shell": "Bash",
    "local_shell": "Bash",
    "apply_patch": "Edit",
    "web_search": "WebSearch",
    "web_search_call": "WebSearch",
    "spawn_agent": "Agent",
    "view_image": "Read",
}


# ── project and state paths ──────────────────────────────────────────────────

def project_root(cwd):
    """The git root above `cwd`, or `cwd` itself when it is not in a repository."""
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5, stdin=subprocess.DEVNULL)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return cwd


class UnsafeStateDir(RuntimeError):
    """A component of the state path is a symlink; nothing is written through it."""


def _refuse_links(base, parts):
    """Raise when `base` or any existing component below it is a symlink. The state holds
    the user's prompts and transcripts, so a planted link must never redirect them (the rule
    upstream's issues_dir applies to its ledger)."""
    p = base
    for part in ("",) + tuple(parts):
        p = os.path.join(p, part) if part else p
        if os.path.islink(p):
            raise UnsafeStateDir(f"refusing to write through symlink {p}")


def state_dir(root, *parts, create=True):
    """`<root>/.codex-workforce/<parts>`. The directory ignores itself in git on creation,
    because it holds the user's prompts (the same rule wf-task-tag applies to `issues/`).
    Raises UnsafeStateDir when any component is a symlink."""
    for part in parts:
        if not part or part in (".", "..") or os.sep in part or (os.altsep and os.altsep in part):
            raise UnsafeStateDir(f"bad state path component {part!r}")
    base = os.path.join(root, STATE_DIRNAME)
    d = os.path.join(base, *parts)
    _refuse_links(base, parts)
    if create:
        os.makedirs(d, exist_ok=True)
        _refuse_links(base, parts)   # nothing raced a link in during creation
        ignore = os.path.join(base, ".gitignore")
        if not os.path.lexists(ignore):
            try:
                fd = os.open(ignore, os.O_CREAT | os.O_EXCL | os.O_WRONLY
                             | getattr(os, "O_NOFOLLOW", 0), 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write("*\n")
            except FileExistsError:
                pass
    return d


def _safe(name):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in str(name or ""))[:120] or "none"


# ── rollout -> Claude-shaped transcript ─────────────────────────────────────

def _texts(content):
    out = []
    for c in content or []:
        if isinstance(c, dict) and isinstance(c.get("text"), str):
            out.append(c["text"])
    return out


def _tool_input(name, raw):
    if isinstance(raw, str):
        try:
            args = json.loads(raw)
        except ValueError:
            args = {"input": raw}
    elif isinstance(raw, dict):
        args = dict(raw)
    else:
        args = {}
    if not isinstance(args, dict):
        args = {"input": args}
    mapped = TOOL_MAP.get(name, name)
    if mapped == "Bash":
        cmd = args.get("cmd", args.get("command"))
        if isinstance(cmd, list):
            cmd = " ".join(str(x) for x in cmd)
        args = dict(args, command=str(cmd or ""))
    elif mapped == "Edit":
        patch = args.get("input") or args.get("patch") or args.get("command") or ""
        fp = ""
        for line in str(patch).splitlines():
            for tag in ("*** Update File: ", "*** Add File: ", "*** Delete File: "):
                if line.startswith(tag):
                    fp = line[len(tag):].strip()
                    break
            if fp:
                break
        args = dict(args, file_path=fp)
    return mapped, args


def _stdout(body):
    """The command's own output from a Codex exec_command result, which wraps it in a
    header ("Chunk ID: … Process exited with code N … Output:")."""
    if not isinstance(body, str):
        return ""
    i = body.find("\nOutput:\n")
    return body[i + len("\nOutput:\n"):] if i >= 0 else body


def convert_rollout(src, dst, sidechain=False):
    """Rewrite a Codex rollout file as Claude-shaped JSONL at `dst`. Returns `dst`, or None
    when `src` cannot be read.

    A user message counts as the user's only when an `item_completed` UserMessage event
    carries the same text; everything else Codex records with role user (AGENTS.md,
    environment context) or developer becomes an `isMeta` row, as Claude records injected
    text. A user message starting "Stop hook feedback" is always meta (cw-dev, (b))."""
    try:
        with open(src, encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
    except (OSError, ValueError, TypeError):
        return None
    typed = set()
    for r in rows:
        p = r.get("payload") if isinstance(r.get("payload"), dict) else {}
        if r.get("type") == "event_msg" and p.get("type") == "item_completed":
            it = p.get("item") or {}
            if it.get("type") == "UserMessage":
                typed.add("\n".join(_texts(it.get("content"))).strip())
        if r.get("type") == "event_msg" and p.get("type") == "user_message":
            typed.add(str(p.get("message") or "").strip())

    out = []
    for r in rows:
        p = r.get("payload") if isinstance(r.get("payload"), dict) else {}
        t = p.get("type") or ""
        ts = r.get("timestamp")
        if r.get("type") == "event_msg" and t in ("task_complete", "turn_complete", "turn_aborted"):
            # cw-dev (1): Claude's turn-end row, which bounds the turn for wf-widen's
            # `turn_rows` and wf-task-tag's walk back to a tool call's message.
            out.append({"type": "system", "subtype": "turn_duration", "timestamp": ts})
            continue
        if r.get("type") != "response_item":
            continue
        if t == "message":
            role = p.get("role")
            text = "\n".join(_texts(p.get("content")))
            if role == "assistant":
                if text.strip():
                    out.append({"type": "assistant", "timestamp": ts,
                                "message": {"role": "assistant",
                                            "content": [{"type": "text", "text": text}]}})
                continue
            if text.lstrip().startswith("Stop hook feedback"):
                # A replayed Stop block: Claude records this as an injected user row, and
                # upstream treats it as the head of the continuation, so mirror that.
                out.append({"type": "user", "isMeta": True, "timestamp": ts,
                            "message": {"role": "user", "content": text}})
            elif role == "user" and (text.strip() in typed or (
                    sidechain and not text.lstrip().startswith(INJECTED_PREFIXES))):
                # In a subagent's rollout the work order may carry no typed-message event
                # (unmeasured), so there anything that is not Codex's known injected
                # context counts as the order.
                out.append({"type": "user", "timestamp": ts,
                            "message": {"role": "user", "content": text}})
            else:
                # Developer and other injected context (AGENTS.md, environment, approvals)
                # can land mid-turn. As a user row it would be taken for the head of the
                # turn by `current_turn`, which has no isMeta test, and cut the evidence.
                out.append({"type": "system", "subtype": "cwf_injected", "timestamp": ts,
                            "content": text[:2000]})
        elif t.endswith("_call_output"):
            body = p.get("output")
            if not isinstance(body, str):
                body = json.dumps(body)
            out.append({"type": "user", "timestamp": ts,
                        "toolUseResult": {"stdout": _stdout(body), "stderr": ""},
                        "message": {"role": "user", "content": [{
                            "type": "tool_result", "tool_use_id": p.get("call_id") or p.get("id"),
                            "content": body}]}})
        elif t.endswith("_call"):
            name = p.get("name") or t
            mapped, args = _tool_input(name, p.get("arguments", p.get("input", p.get("action"))))
            out.append({"type": "assistant", "timestamp": ts,
                        "message": {"role": "assistant", "content": [{
                            "type": "tool_use", "id": p.get("call_id") or p.get("id"),
                            "name": mapped, "input": args}]}})
    if sidechain:
        # cw-dev (1): a subagent's spawn prompt is found as the first user row with
        # isSidechain true (wf-widen ~535, wf-task-tag ~763).
        for row in out:
            row["isSidechain"] = True
    tmp = dst + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for row in out:
            fh.write(json.dumps(row) + "\n")
    os.replace(tmp, dst)
    return dst


def _norm(text):
    return " ".join(str(text or "").split())


def last_reply(path):
    """Text of the last assistant text row in a converted transcript, or None."""
    try:
        with open(path, encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
    except (OSError, ValueError):
        return None
    for r in reversed(rows):
        if r.get("type") == "assistant":
            blocks = r.get("message", {}).get("content") or []
            texts = [b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text"]
            if texts:
                return " ".join(texts)
    return None


def convert_until_reply(src, dst, reply, sidechain=False, tries=8, wait=0.25):
    """Convert, and on a Stop re-convert until the transcript's last assistant row matches
    `last_assistant_message`. Upstream's own lag retry (TL.REPLY_WAIT) re-reads the PATH it
    was given, which here is a one-time conversion, so the wait for Codex's flush has to
    happen at conversion. Returns (path or None, matched)."""
    import time
    path = convert_rollout(src, dst, sidechain)
    if not reply or path is None:
        return path, True
    for _ in range(tries):
        if _norm(last_reply(path)) == _norm(reply):
            return path, True
        time.sleep(wait)
        path = convert_rollout(src, dst, sidechain) or path
    return path, _norm(last_reply(path)) == _norm(reply)


def resume_context(root, payload):
    """The tracked `RESUME.md` a new session should pick up, or "".

    Only a main-session UserPromptSubmit receives it: a subagent has neither the user's
    conversation nor a reason to inherit the parent's handoff. A Stop continuation is a
    replayed prompt with the feedback prefix, so it must not re-inject the file. The file is
    tracked, size-capped, and read as text; nothing in it is executed.
    """
    if payload.get("hook_event_name") != "UserPromptSubmit":
        return ""
    if str(payload.get("prompt") or "").startswith(FEEDBACK_PREFIX):
        return ""
    path = os.path.join(root, RESUME_FILE)
    try:
        if os.path.islink(path) or not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read(RESUME_LIMIT + 1)
    except OSError:
        return ""
    if not text.strip():
        return ""
    if len(text) > RESUME_LIMIT:
        text = text[:RESUME_LIMIT] + "\n[resume file truncated]\n"
    return ("Project resume context (tracked, read as context; delete or replace it when the "
            "handoff is finished):\n\n" + text)


def normalize_payload(payload):
    """Codex hook input -> the payload the upstream hooks expect. Returns (payload, env).
    Sets `cwf_reply_unmatched` when a Stop's reply never appeared in the transcript."""
    p = dict(payload)
    cwd = p.get("cwd") or os.getcwd()
    root = project_root(cwd)
    sid = _safe(p.get("session_id"))
    scratch = state_dir(root, "scratch", sid)
    p["scratchpad_dir"] = scratch
    p["cwf_resume_context"] = resume_context(root, p)
    p["cwf_rollout_path"] = p.get("transcript_path")
    stopping = str(p.get("hook_event_name", "")).endswith("Stop")
    for key, name in (("transcript_path", "transcript.jsonl"),
                      ("agent_transcript_path", f"agent-{_safe(p.get('agent_id'))}.jsonl")):
        src = p.get(key)
        if not (isinstance(src, str) and src):
            continue
        dst = os.path.join(scratch, name)
        side = key == "agent_transcript_path"
        mine = side == (p.get("hook_event_name") == "SubagentStop")
        if stopping and mine:
            path, matched = convert_until_reply(src, dst, p.get("last_assistant_message"), side)
            if not matched:
                p["cwf_reply_unmatched"] = True
        else:
            path = convert_rollout(src, dst, side)
        p[key] = path or src
    if os.environ.get("CWF_DEBUG"):
        with open(os.path.join(state_dir(root, "debug"), f"{sid}.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"in": payload, "normalized": p}) + "\n")
    # cw-dev (3): wf-turn-budget and wf-widen also look under tempfile.gettempdir(), which
    # Claude Code shares on this machine; give every step a temp dir of its own.
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root, CWF_PROJECT_ROOT=root,
               TMPDIR=state_dir(root, "tmp"))
    return p, env


# ── patches applied to every load of an upstream module ────────────────────

def _issues_dir(mod, payload, create=False):
    """wf-task-tag's `issues_dir` with the ledger moved to `<root>/.codex-workforce/issues`.
    Same refusals as upstream: no root, or a linked directory, gives None."""
    root = mod.project_root(payload)
    if not root:
        return None
    wf = os.path.join(root, STATE_DIRNAME)
    d = os.path.join(wf, mod.ISSUES)
    if os.path.islink(d) or os.path.islink(wf):
        return None
    if not create:
        return d if os.path.isdir(d) else None
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        return None
    ignore = os.path.join(d, ".gitignore")
    if not os.path.exists(ignore):
        try:
            fd = mod._open_nofollow(ignore, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(mod.IGNORE_RULE)
        except OSError:
            pass
    return d


def _instruments(cwd):
    """What a Codex turn could have widened with: its skills and custom agents."""
    found = {"agents": [], "skills": []}
    home = os.path.expanduser("~")
    skill_roots = [os.path.join(cwd, ".agents", "skills"), os.path.join(home, ".agents", "skills"),
                   os.path.join(os.environ.get("CODEX_HOME") or os.path.join(home, ".codex"), "skills")]
    agent_roots = [os.path.join(cwd, ".codex", "agents"),
                   os.path.join(os.environ.get("CODEX_HOME") or os.path.join(home, ".codex"), "agents")]
    for kind, roots in (("skills", skill_roots), ("agents", agent_roots)):
        for d in roots:
            if not os.path.isdir(d):
                continue
            for n in sorted(os.listdir(d)):
                name = n.rsplit(".", 1)[0] if n.endswith((".md", ".toml")) else n
                if not name.startswith(".") and name not in found[kind]:
                    found[kind].append(name)
    return found


def _patch(module):
    if hasattr(module, "issues_dir") and hasattr(module, "ISSUES") and hasattr(module, "project_root"):
        module.issues_dir = lambda payload, create=False, _m=module: _issues_dir(_m, payload, create)
    if hasattr(module, "instruments") and hasattr(module, "turn_rows"):
        module.instruments = _instruments


def install_patches():
    """Wrap SourceFileLoader so every upstream module, including the copies wf-widen and
    wf-turn-budget load for themselves, is patched as soon as it executes."""
    sys.dont_write_bytecode = True
    orig = importlib.machinery.SourceFileLoader.exec_module
    if getattr(orig, "_cwf", False):
        return

    def exec_module(self, module):
        orig(self, module)
        if os.path.dirname(os.path.abspath(self.path)) == UPSTREAM_BIN:
            _patch(module)
    exec_module._cwf = True
    importlib.machinery.SourceFileLoader.exec_module = exec_module


def load_upstream(name):
    install_patches()
    path = os.path.join(UPSTREAM_BIN, name)
    modname = name.replace("-", "_")
    loader = importlib.machinery.SourceFileLoader(modname, path)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(modname, loader))
    loader.exec_module(mod)
    return mod


# ── running one upstream step ───────────────────────────────────────────────

STEP = os.path.join(REPO, "cwf", "bin", "cwf-step")


def run_step(name, payload, env, timeout=60):
    """Run one upstream hook's main() in its own process (cw-dev, (a)): its own stdin,
    stdout and module caches. Returns (exit code, parsed JSON output or None, raw stdout,
    problem) where `problem` is "" on success and otherwise a one-line description that the
    caller must surface, so a crashed or timed-out step is never mistaken for a pass."""
    try:
        r = subprocess.run([sys.executable, "-I", STEP, name], input=json.dumps(payload),
                           capture_output=True, text=True, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, None, "", f"{name} timed out after {timeout}s"
    raw = r.stdout.strip()
    parsed = None
    for line in reversed(raw.splitlines()):
        try:
            parsed = json.loads(line)
            break
        except ValueError:
            continue
    problem = ""
    if r.returncode != 0:
        tail = (r.stderr.strip().splitlines() or ["no stderr"])[-1]
        problem = f"{name} exited {r.returncode}: {tail[:300]}"
    return r.returncode, parsed, raw, problem
