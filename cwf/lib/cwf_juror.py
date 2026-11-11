"""The juror, as a Codex command step.

In Claude Code the juror is a `type: agent` Stop hook whose prompt lives in
wf-settings-apply's AGENT_HOOKS. Codex parses agent handlers but skips them, so cwf-hook
runs the juror itself: the upstream prompt, read with `ast` (never imported, never run),
with the Claude-only parts replaced as cw-dev listed (2026-11-11, (c)), sent to a
read-only, hook-free `codex exec`.

It never judges its own session: hooks are switched off in the nested run.
"""
import ast
import json
import os
import subprocess
import tempfile

from cwf_codex import UPSTREAM_BIN

SETTINGS = os.path.join(UPSTREAM_BIN, "wf-settings-apply")
DEFAULT_PROFILE = os.environ.get("CWF_JUROR_PROFILE", "glm")
TIMEOUT = int(os.environ.get("CWF_JUROR_TIMEOUT", "150"))

# (upstream text, Codex text). A pair whose upstream text is missing is reported, so a
# re-sync that rewords the prompt shows up instead of silently leaving a Claude term in.
REPLACEMENTS = [
    ("verifying with "
     "Read, Grep and Glob rather than taking the turn's word. Bash may be denied "
     "to this hook, so never plan on it.",
     "verifying with read-only shell commands (cat, rg, sed, ls, git log) rather than "
     "taking the turn's word. Your sandbox is read-only: never try to write."),
    ("Grep it, since it can be megabytes.",
     "search it with rg, since it can be megabytes."),
    ("LOOK at every file in `images.files` with Read, which shows you the picture;",
     "LOOK at every file in `images.files` with your image-viewing tool (view_image); if "
     "you have no way to see the picture, abstain on fit and say so, never vote yes;"),
]


def upstream_prompt():
    """AGENT_HOOKS['wf-widen-agent']['prompt'] from wf-settings-apply, without executing it."""
    with open(SETTINGS, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), SETTINGS)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "AGENT_HOOKS" for t in node.targets):
            return ast.literal_eval(node.value)["wf-widen-agent"]["prompt"]
    raise LookupError("AGENT_HOOKS not found in wf-settings-apply")


def build_prompt(payload, flag_path):
    """The juror prompt for this stop, and the list of replacements that did not apply."""
    text = upstream_prompt()
    missed = []
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
        else:
            missed.append(old[:40])
    text = text.replace("<scratchpad_dir>/wf-widen-flag.<session_id>.json", flag_path)
    shown = {k: payload.get(k) for k in (
        "session_id", "transcript_path", "cwd", "hook_event_name", "stop_hook_active",
        "agent_id", "agent_type", "agent_transcript_path", "last_assistant_message")
        if payload.get(k) is not None}
    text = text.replace("$ARGUMENTS", json.dumps(shown))
    return text, missed


def _verdict(raw):
    """The juror's {ok, reason, notes} from its last message, or None."""
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[raw.find("{"):] if "{" in raw else raw
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        v = json.loads(raw[start:end + 1])
    except ValueError:
        return None
    return v if isinstance(v, dict) and "ok" in v else None


def judge(payload, flag_path, root, profile=None):
    """Run the juror. Returns (verdict dict or None, diagnostic string)."""
    prompt, missed = build_prompt(payload, flag_path)
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False,
                                     dir=os.path.dirname(flag_path)) as out:
        out_path = out.name
    cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral",
           "-s", "read-only", "-c", "features.hooks=false",
           "-p", profile or DEFAULT_PROFILE, "-C", root, "-o", out_path, "-"]
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=TIMEOUT)
        with open(out_path, encoding="utf-8") as fh:
            last = fh.read()
    except subprocess.TimeoutExpired:
        return None, f"juror timed out after {TIMEOUT}s"
    except OSError as exc:
        return None, f"juror could not run: {exc}"
    finally:
        try:
            os.remove(out_path)
        except OSError:
            pass
    v = _verdict(last)
    diag = "" if not missed else "juror prompt drift: " + "; ".join(missed)
    if v is None:
        return None, (diag + " | " if diag else "") + f"juror gave no verdict (exit {r.returncode})"
    return v, diag
