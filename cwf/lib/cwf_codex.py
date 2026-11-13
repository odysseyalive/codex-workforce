"""Codex adapter for the claude-workforce sensory layer.

The sense logic lives, unmodified, in upstream/claude-workforce/workforce/bin. This module
replaces only the Claude-specific edges around it, as agreed with cw-dev (2026-11-11):

  payload in      Codex hook input already uses Claude's field names; we add
                  `scratchpad_dir` (Codex sends none) and a converted `transcript_path`.
  transcript      Codex rollout JSONL is rewritten into Claude-shaped JSONL, so the
                  upstream walkers (`TL._read_lines`, `current_turn`, `turn_rows`,
                  `confirmed_reply`) run unchanged.
  paths           `issues_dir`, widen's PERF/handoff directories and its `instruments`
                  are patched on every load of the upstream modules (see `install_patches`).
                  Nothing writes under `.claude/`.
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

# Injected text is upstream's Claude Code wording. These replacements are applied to the
# loaded module constants, never to upstream on disk, so the files stay checksum-pinned.
CODEX_USER_WORDS = (
    "What this user wants is decided by the user's own requests and notes, weighed by date "
    "with the newest first: this message, then earlier messages in this conversation, then "
    "older requests and notes. A report, plan, summary, or record written by an AI is an "
    "interpretation of those words, not the user's evidence, however recent it is; projects "
    "mark the difference with quoted user words, `origin: user` blocks, `source: user` "
    "attributions, and the user's own notes. An older decision that a newer request "
    "contradicts is superseded by the request, so \"keep it as it was\" is not one of the "
    "choices, and an option that delivers less than the request is not the recommended one. "
    "On how code is written, precedence runs: the user's newest requests and notes decide "
    "what gets built; the project's original human-written code decides how, newest first "
    "within it; AI-written code already in the project comes next, even when it is newer "
    "than the human code; the AI's own preferences come last. Precedent covers mechanisms, "
    "helpers, error handling, naming, and comment style, not bugs. Where a project has "
    "almost no human code, the user's own words are its human precedent. Before an edit, "
    "read the file's git blame or git log to see which lines are human, AI, or unknown."
)
CODEX_CHOOSER_RULE = (
    "Stopping to ask this user is for a decision that genuinely needs them: anything that "
    "can be decided and reversed is decided, said in one line, and the work it unblocks is "
    "finished rather than reported as pending. Codex has no question tool, so when a "
    "decision does need the user, ask one concise plain-text question in that same turn, "
    "give the options and your recommendation, and stop there rather than continuing work "
    "that depends on the answer. Plain text is the whole channel on this host."
)
CODEX_CLEANUP_RULE = (
    "One-shot work is spawned as a plain subagent by preference: a named teammate can "
    "outlive its own hand-back until something closes it, so an order reported done still "
    "shows a running agent. Close a spawned agent with `close_agent` once its report has "
    "been read. A work order names only tools the agent actually holds in this session; "
    "Codex cannot enforce a per-agent tool allowlist, so check the order against the "
    "tools the session exposes, and an order naming a tool the runner lacks is answered by "
    "saying so in the report and doing the work with what is there. Before a package is run "
    "through npx, what that name resolves to is known: the project's own package, a pinned "
    "dependency, or a package the task names. A package name is never guessed from a tool's "
    "or a project's name, and an MCP server is reached through its tools rather than started "
    "from the shell. A command that might wait on input or on the network is worth wrapping "
    "in `timeout`, and no background shell or process is left running once the work is done. "
    "A wait on a long job polls the job's own progress, prints it, and carries a timeout, "
    "with one waiter at a time; the job's own queue or the Monitor tool is preferred over a "
    "sleep loop."
)

# Codex tool names -> the Claude names the upstream evidence counters understand.
TOOL_MAP = {
    "exec_command": "Bash",
    "shell": "Bash",
    "local_shell": "Bash",
    "apply_patch": "Edit",
    "edit_file": "Edit",
    "write_file": "Write",
    "read_file": "Read",
    "list_dir": "Glob",
    "search_files": "Grep",
    "web_search": "WebSearch",
    "web_search_call": "WebSearch",
    "web_fetch": "WebFetch",
    "spawn_agent": "Agent",
    # Lifecycle calls carry no new evidence: the spawn that opened the agent was
    # counted when it happened. Mapping wait/close to Agent would let a poll open
    # "outside" hearing without anything outside being read (review finding 1).
    "wait_agent": "Read",
    "close_agent": "Read",
    # A poll of an exec_command session carries no new evidence either; the command
    # that opened it was already counted.
    "write_stdin": "Read",
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
            call_id = p.get("call_id") or p.get("id")
            result = {"type": "tool_result", "tool_use_id": call_id, "content": body}
            out.append({"type": "user", "timestamp": ts,
                        "toolUseResult": {"stdout": _stdout(body), "stderr": ""},
                        "message": {"role": "user", "content": [result]}})
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
    if path is None:
        # A truncated or otherwise unreadable rollout is never "matched". The caller
        # must report the stop as not judged rather than treating None as clean.
        return None, False
    if not reply:
        return path, True
    for _ in range(tries):
        if _norm(last_reply(path)) == _norm(reply):
            return path, True
        time.sleep(wait)
        path = convert_rollout(src, dst, sidechain) or path
    return path, _norm(last_reply(path)) == _norm(reply)


RESUME_MARKER = "cwf-resume-injected"


def resume_context(root, payload, scratch=None):
    """The tracked `RESUME.md` a new session should pick up, or "".

    Only a main-session UserPromptSubmit receives it: a subagent has neither the user's
    conversation nor a reason to inherit the parent's handoff. A Stop continuation is a
    replayed prompt with the feedback prefix, so it must not re-inject the file. The file is
    tracked, size-capped, and read as text; nothing in it is executed.

    FIRST PROMPT ONLY (C0.6, review finding 4): once injected, a marker in the session's
    own scratch directory stops every later prompt of that session from repeating it.
    """
    if payload.get("hook_event_name") != "UserPromptSubmit":
        return ""
    if str(payload.get("prompt") or "").startswith(FEEDBACK_PREFIX):
        return ""
    marker = os.path.join(scratch, RESUME_MARKER) if scratch else None
    if marker and os.path.lexists(marker):
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
    if marker:
        try:
            with open(marker, "x", encoding="utf-8") as fh:
                fh.write(RESUME_FILE + "\n")
        except OSError:
            return ""   # another prompt of this session got there first, or no state dir
    return ("Project resume context (tracked, read as context; delete or replace it when the "
            "handoff is finished):\n\n" + text)


# The dispatch line, mirroring claude-workforce's `DISPATCH_LINE` / `DISPATCH_NO_ORG` in
# wf-task-tag. Upstream injects it on every UserPromptSubmit that opens an issue; this port
# injects it on every main-session prompt, because Codex has no equivalent tagger hook and a
# session that never hears it will do all the work in the main thread. ADVISORY, NEVER A
# GATE: nothing refuses and nothing blocks. The reasons are upstream's own, measured
# 2026-11-08: a project without an org did a whole job in the main thread because nothing
# said a job could go to a subagent at all.
DISPATCH_INLINE = (" Work inline only when the answer is already in hand or the job is a few "
                   "tool calls: data in hand that answers the question is itself the answer.")
DISPATCH_ORG = (" This project has a workforce org. A job in this message goes to the employee "
                "whose description fits, spawned as a background plain subagent so this "
                "session stays free for the next message; the spawn is linked to the issue and "
                "the Work list tracks it until it hands back." + DISPATCH_INLINE)
DISPATCH_NO_ORG = (" This project has no workforce org, which changes who takes a job and not "
                   "whether one is handed off. A job in this message goes to a background plain "
                   "`general-purpose` subagent, spawned so this session stays free for the next "
                   "message; the spawn is linked to the issue and the Work list tracks it until "
                   "it hands back." + DISPATCH_INLINE)
# This package ships a code-writing agent the upstream set lacks, so the no-org line names it
# when the job is code. It is still a plain subagent for bookkeeping purposes.
DISPATCH_CODE = (" Code that changes files — a feature, a fix, a refactor, or its tests — goes "
                 "to `cwf-implementer`; a review of code that already landed goes to "
                 "`deadcode-gardener`; an approach that needs deciding before writing goes to "
                 "`code-design-advisor`. Each is one-shot: spawn it, read its report, close it "
                 "with `close_agent`.")
ORG_CHART_REL = os.path.join(".codex-workforce", "org-chart.md")
ORG_MARKER = b"AUTO-GENERATED"


def dispatch_context(root):
    """The advisory dispatch line for a main-session prompt, or "".

    An org is a chart this package's own tooling wrote, carrying the `AUTO-GENERATED` marker;
    a stray `.codex/agents/*.toml` is not one. Read-only, size-capped, never through a link.
    """
    line = DISPATCH_NO_ORG + DISPATCH_CODE
    path = os.path.join(root, ORG_CHART_REL)
    try:
        if not os.path.islink(path) and os.path.isfile(path):
            with open(path, "rb") as fh:
                head = fh.read(1024)
            if ORG_MARKER in head:
                line = DISPATCH_ORG
    except OSError:
        pass
    return line


# ── hook trust (C0.8) ───────────────────────────────────────────────────
# Codex skips a hook whose definition changed since it was trusted in `/hooks`, silently.
# The stored `trusted_hash` was reproduced on codex-cli 0.169.0 (2026-11-13, 8 of 8 live
# cwf rows plus one foreign row): sha256 of the compact, key-sorted JSON of {"event_name": <snake_case event>,
# "hooks": [<handler with async defaulted to false>]} plus "matcher" when the group has
# one. The format is Codex's, not documented, so an unreadable config reports "unknown",
# never "trusted".
def _snake(event):
    return "".join("_" + c.lower() if c.isupper() and i else c.lower()
                   for i, c in enumerate(event))


def hook_trust_hash(event, group, handler):
    import hashlib
    h = dict(handler)
    h.setdefault("async", False)
    if os.name != "nt":
        # Measured: the user-scope rows carry commandWindows and still match, and Codex
        # runs them, so off Windows the field is not part of the hashed definition.
        h.pop("commandWindows", None)
    obj = {"event_name": _snake(event), "hooks": [h]}
    if "matcher" in group:
        obj["matcher"] = group["matcher"]
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _trusted_hashes(config_path):
    try:
        with open(config_path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    try:
        import tomllib
        state = (tomllib.loads(raw.decode("utf-8")).get("hooks") or {}).get("state") or {}
        return {k: v.get("trusted_hash") for k, v in state.items() if isinstance(v, dict)}
    except ImportError:
        import re
        return dict(re.findall(r'\[hooks\.state\."([^"]+)"\]\s*\ntrusted_hash\s*=\s*"([^"]+)"',
                               raw.decode("utf-8", "replace")))
    except ValueError:
        return None


def hook_trust_status(hooks_path, config_path=None):
    """[(key, "trusted" | "changed" | "new" | "unknown")] for every cwf-hook handler in
    `hooks_path`. "changed" and "new" are entries Codex will skip until re-trusted."""
    config_path = config_path or os.path.join(
        os.environ.get("CODEX_HOME") or os.path.join(os.path.expanduser("~"), ".codex"),
        "config.toml")
    try:
        with open(hooks_path, encoding="utf-8") as fh:
            hooks = (json.load(fh) or {}).get("hooks") or {}
    except (OSError, ValueError, AttributeError):
        return []
    trusted = _trusted_hashes(config_path)
    path = os.path.abspath(hooks_path)
    out = []
    for event, groups in hooks.items():
        for gi, group in enumerate(groups if isinstance(groups, list) else []):
            for hi, handler in enumerate(group.get("hooks") or []):
                if "cwf-hook" not in str(handler.get("command", "")):
                    continue
                key = f"{path}:{_snake(event)}:{gi}:{hi}"
                if trusted is None:
                    state = "unknown"
                elif key not in trusted:
                    state = "new"
                elif trusted[key] == hook_trust_hash(event, group, handler):
                    state = "trusted"
                else:
                    state = "changed"
                out.append((key, state))
    return out


def retrust_notice(root, scratch=None):
    """One line telling the user to re-trust, or "". Shown once per session (a marker in
    the session's scratch directory), and only for cwf entries that changed or are new.
    A changed prompt hook cannot say this itself, because Codex no longer runs it; the
    entries that still run say it for the ones that do not."""
    stale = []
    for hooks_path in (os.path.join(root, ".codex", "hooks.json"),
                       os.path.join(os.environ.get("CODEX_HOME")
                                    or os.path.join(os.path.expanduser("~"), ".codex"),
                                    "hooks.json")):
        stale += [k for k, st in hook_trust_status(hooks_path) if st in ("changed", "new")]
    if not stale:
        return ""
    marker = os.path.join(scratch, "cwf-retrust-noticed") if scratch else None
    if marker:
        try:
            with open(marker, "x", encoding="utf-8") as fh:
                fh.write("\n".join(stale) + "\n")
        except OSError:
            return ""
    return ("cwf: %d codex-workforce hook(s) changed since you trusted them and will not run "
            "until re-trusted: open /hooks and trust them (%s)"
            % (len(stale), ", ".join(k.rsplit(":", 3)[-3] for k in stale)))


def normalize_payload(payload):
    """Codex hook input -> the payload the upstream hooks expect. Returns (payload, env).
    Sets `cwf_reply_unmatched` when a Stop's reply never appeared in the transcript, and
    `cwf_unjudged` when a Stop has no transcript at all."""
    p = dict(payload)
    cwd = p.get("cwd") or os.getcwd()
    root = project_root(cwd)
    sid = _safe(p.get("session_id"))
    scratch = state_dir(root, "scratch", sid)
    p["scratchpad_dir"] = scratch
    p["cwf_resume_context"] = resume_context(root, p, scratch)
    p["cwf_dispatch_context"] = (dispatch_context(root)
                                 if p.get("hook_event_name") == "UserPromptSubmit" else "")
    p["cwf_retrust_notice"] = (retrust_notice(root, scratch)
                               if p.get("hook_event_name") == "UserPromptSubmit" else "")
    p["cwf_rollout_path"] = p.get("transcript_path")
    stopping = str(p.get("hook_event_name", "")).endswith("Stop")
    if stopping:
        missing = []
        if not (isinstance(p.get("transcript_path"), str) and p.get("transcript_path")):
            missing.append("transcript_path")
        if p.get("hook_event_name") == "SubagentStop" and not (
                isinstance(p.get("agent_transcript_path"), str) and p.get("agent_transcript_path")):
            missing.append("agent_transcript_path")
        if missing:
            p["cwf_unjudged"] = ("Codex sent null " + " and ".join(missing)
                                 + "; this stop has no transcript to judge")
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
            if path is None:
                p["cwf_unjudged"] = ("the rollout transcript could not be read whole "
                                     "(truncated or invalid line); this stop has no "
                                     "transcript to judge")
            elif not matched:
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


def _perf_store(module, root):
    """Upstream's personnel-store rule with the Codex state directory."""
    if not root:
        return ""
    d = os.path.join(root, *module.PERF_STORE_PARTS)
    if os.path.islink(d) or os.path.islink(os.path.dirname(d)):
        return ""
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        return ""
    return d


def _patch(module):
    if hasattr(module, "issues_dir") and hasattr(module, "ISSUES") and hasattr(module, "project_root"):
        module.issues_dir = lambda payload, create=False, _m=module: _issues_dir(_m, payload, create)
    if hasattr(module, "instruments") and hasattr(module, "turn_rows"):
        module.instruments = _instruments
    # F01: upstream's cap-hit PERF store and handoff lookup still name `.claude/`.
    if hasattr(module, "PERF_STORE_PARTS"):
        module.PERF_STORE_PARTS = (STATE_DIRNAME, "personnel")
        module.PERF_STORE = os.path.join(*module.PERF_STORE_PARTS)
        if hasattr(module, "perf_store"):
            # Rebind the function too: it closes over the module global, so patching the
            # constant is enough in this process, but an explicit function makes the path
            # assertion unambiguous to a reader.
            module.perf_store = lambda root, _m=module: _perf_store(_m, root)
    if hasattr(module, "WORK_DIRS"):
        module.WORK_DIRS = (STATE_DIRNAME, "work")
    # C0.5/M1: upstream's tagger still reads Claude's chart. Patch the live constant
    # and suppress its own dispatch line: cwf-hook already injects the Codex dispatch
    # line, so leaving both produced contradictory org/no-org context.
    if hasattr(module, "ORG_CHART"):
        module.ORG_CHART = ORG_CHART_REL
        module.ORG_MARKER = ORG_MARKER
        module.dispatch_line = lambda _payload, _issue_id: ""
    # C0.5/M4: the turn budget must never read a Claude handbook's `maxTurns`, nor
    # Claude's personal agent root. Codex custom agents have no turn-cap field, so a Codex
    # agent has no cap here; a same-named `.claude/agents/<name>.md` cannot steer it.
    if hasattr(module, "read_cap") and hasattr(module, "MAX_TURNS_RX"):
        module.config_root = lambda: os.environ.get("CODEX_HOME") or os.path.join(
            os.path.expanduser("~"), ".codex")
        module.read_cap = lambda _root, _agent_type: None
    # C0.5/M3: directives belong to a Codex custom agent, not a Claude markdown one.
    if hasattr(module, "handbook_path") and hasattr(module, "bare_name"):
        def _codex_handbook_path(root, payload, _m=module):
            at = str(payload.get("agent_type") or "").strip()
            if not _m.bare_name(at):
                return None
            path = os.path.join(root, ".codex", "agents", at + ".toml")
            return path if _m._inside(root, path) else None
        module.handbook_path = _codex_handbook_path
    # C0.5/M7: widen's work-segment check must follow the Codex work root, not match
    # Claude's path by coincidence.
    if hasattr(module, "OUTPUT_WORK_SEG"):
        module.OUTPUT_WORK_SEG = os.path.join(STATE_DIRNAME, "work") + os.sep
    if hasattr(module, "NO_BRIEF"):
        module.NO_BRIEF = ("No readable HANDOFF.md under .codex-workforce/work/<run-id>/{who}/, "
                           "so section 1 cannot be quoted.")
    # C0.5/M4: cap PERF records the handbook that actually governed the Codex agent.
    # Rebuild just this function from upstream source with the two path literals moved;
    # upstream on disk remains checksum-pinned.
    if hasattr(module, "cap_perf"):
        import inspect
        src = inspect.getsource(module.cap_perf)
        src = src.replace('os.path.join(".claude", "agents", f"{agent}.md")',
                         'os.path.join(".codex", "agents", f"{agent}.toml")')
        ns = dict(module.__dict__)
        exec(compile(src, getattr(module, "__file__", "wf-widen"), "exec"), ns)
        module.cap_perf = ns["cap_perf"]
    # F08/F25: the injected wording names Claude-only tools. Patch the live constants so
    # every load, including a sibling's own copy, speaks the Codex surface.
    if hasattr(module, "USER_WORDS"):
        module.USER_WORDS = CODEX_USER_WORDS
    if hasattr(module, "CHOOSER_RULE"):
        module.CHOOSER_RULE = CODEX_CHOOSER_RULE
    if hasattr(module, "CLEANUP_RULE"):
        module.CLEANUP_RULE = CODEX_CLEANUP_RULE


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
