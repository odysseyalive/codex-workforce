"""End-to-end tests for the codex-workforce sensory layer (cwf/bin/cwf-hook).

Run:  python3 -m unittest discover -s tests -v
No network and no model calls: the juror is switched off (CWF_JUROR=off) except in
test_juror_prompt_has_no_drift, which only builds the prompt.

Each test works in a fresh git repository in a temp directory. Run them from a normal
shell, not from inside a Codex sandbox: on this machine Codex's sandbox gives /tmp its own
view, and files written there do not persist.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "cwf", "bin", "cwf-hook")
sys.path.insert(0, os.path.join(ROOT, "cwf", "lib"))
sys.dont_write_bytecode = True
import cwf_codex  # noqa: E402
import cwf_juror  # noqa: E402


def rollout_rows(user_prompt, tool_calls, reply):
    """A Codex rollout in the shapes recorded by codex-cli 0.167: injected AGENTS.md text,
    the typed user message (response_item + item_completed UserMessage), function calls
    with outputs, and the assistant reply."""
    rows = [
        {"type": "response_item", "payload": {"type": "message", "role": "developer",
         "content": [{"type": "input_text", "text": "<permissions instructions>"}]}},
        {"type": "response_item", "payload": {"type": "message", "role": "user",
         "content": [{"type": "input_text", "text": "# AGENTS.md instructions\nx"}]}},
        {"type": "response_item", "payload": {"type": "message", "role": "user",
         "content": [{"type": "input_text", "text": user_prompt}]}},
        {"type": "event_msg", "payload": {"type": "item_completed", "item": {
         "type": "UserMessage", "content": [{"type": "text", "text": user_prompt}]}}},
    ]
    for i, (name, args, output) in enumerate(tool_calls):
        rows.append({"type": "response_item", "payload": {
            "type": "function_call", "name": name, "arguments": json.dumps(args),
            "call_id": f"call-{i}"}})
        rows.append({"type": "response_item", "payload": {
            "type": "function_call_output", "call_id": f"call-{i}", "output": output}})
    rows.append({"type": "response_item", "payload": {"type": "message", "role": "assistant",
                 "content": [{"type": "output_text", "text": reply}]}})
    return rows


class SenseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cwf-test-")
        self.proj = os.path.join(self.tmp, "proj")
        os.makedirs(self.proj)
        subprocess.run(["git", "init", "-q", self.proj], check=True)
        self.env = dict(os.environ, CWF_JUROR="off")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_rollout(self, rows):
        path = os.path.join(self.tmp, "rollout.jsonl")
        with open(path, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        return path

    def hook(self, mode, payload):
        r = subprocess.run([sys.executable, HOOK, mode], input=json.dumps(payload),
                           capture_output=True, text=True, env=self.env, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout) if r.stdout.strip() else {}

    def payload(self, rollout, sid="s1", **kw):
        p = {"session_id": sid, "turn_id": "t1", "transcript_path": rollout, "cwd": self.proj}
        p.update(kw)
        return p

    def issues(self):
        n = 0
        for f in glob.glob(os.path.join(self.proj, ".codex-workforce", "issues", "*.json")):
            if not f.endswith("index.json"):
                with open(f) as fh:
                    n += len(json.load(fh).get("issues", []))
        return n

    # ── transcript conversion ────────────────────────────────────────────────

    def convert(self, rows, sidechain=False):
        dst = cwf_codex.convert_rollout(self.write_rollout(rows),
                                        os.path.join(self.tmp, "out.jsonl"), sidechain)
        with open(dst) as fh:
            return dst, [json.loads(l) for l in fh]

    def test_converter_injected_text_is_not_a_user_row_and_tools_map(self):
        out = "Chunk ID: 1\nProcess exited with code 0\nOutput:\na.txt\n"
        _, rows = self.convert(rollout_rows(
            "list the files", [("exec_command", {"cmd": "ls -la"}, out)], "a.txt only"))
        users = [r for r in rows if r["type"] == "user" and isinstance(r["message"]["content"], str)]
        self.assertEqual([r["message"]["content"] for r in users], ["list the files"])
        self.assertEqual(sum(r["type"] == "system" and r.get("subtype") == "cwf_injected"
                             for r in rows), 2)
        tool = [b for r in rows if r["type"] == "assistant"
                for b in r["message"]["content"] if b["type"] == "tool_use"][0]
        self.assertEqual((tool["name"], tool["input"]["command"]), ("Bash", "ls -la"))
        result = [r for r in rows if r.get("toolUseResult")][0]
        self.assertEqual(result["toolUseResult"]["stdout"], "a.txt\n")

    def test_turn_end_rows_and_sidechain(self):
        rows = rollout_rows("do the subtask", [], "done")
        rows.append({"type": "event_msg", "payload": {"type": "task_complete"}})
        rows[3]["payload"]["type"] = "not_a_typed_event"   # no typed UserMessage event
        _, conv = self.convert(rows, sidechain=True)
        self.assertEqual(conv[-1], {"type": "system", "subtype": "turn_duration",
                                    "timestamp": None, "isSidechain": True})
        first_user = next(r for r in conv if r["type"] == "user")
        self.assertEqual(first_user["message"]["content"], "do the subtask")
        self.assertTrue(all(r.get("isSidechain") for r in conv))

    def test_mid_turn_developer_message_keeps_the_turn_whole(self):
        rows = rollout_rows("check the repo for foo.txt",
                            [("exec_command", {"cmd": "find . -name foo.txt"}, "")], "none found")
        dev = {"type": "response_item", "payload": {"type": "message", "role": "developer",
               "content": [{"type": "input_text", "text": "Approved command prefix saved"}]}}
        rows.insert(-1, dev)
        dst, _ = self.convert(rows)
        TL = cwf_codex.load_upstream("wf-turn-ledger")
        counts = TL.turn_counts({"transcript_path": dst, "last_assistant_message": "none found"})
        self.assertEqual(counts[0], 1, "the find must still count as this turn's read")
        self.assertEqual(counts[2], 1, "and as an enumerating read")

    def test_feedback_replay_row_is_meta(self):
        rows = rollout_rows("Stop hook feedback:\nrun the tests", [], "ok")
        dst = cwf_codex.convert_rollout(self.write_rollout(rows), os.path.join(self.tmp, "o.jsonl"))
        with open(dst) as fh:
            typed = [json.loads(l) for l in fh]
        self.assertTrue(all(r.get("isMeta") for r in typed
                            if r["type"] == "user" and isinstance(r["message"]["content"], str)))

    # ── prompt hook ─────────────────────────────────────────────────────────

    def test_prompt_hook_tags_existence_ask(self):
        q = "is there any file named foo.txt anywhere in this repo?"
        out = self.hook("prompt", self.payload(self.write_rollout(rollout_rows(q, [], "")),
                                               hook_event_name="UserPromptSubmit", prompt=q))
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("existence", ctx)
        self.assertIn("TASTE", ctx)

    def test_replayed_feedback_opens_no_issue_but_unprefixed_does(self):
        body = ("Channels this ask requires, and what the turn recorded: touch 0. Please run "
                "the full build and fix every failing test before replying to the user.")
        r = self.write_rollout(rollout_rows("x", [], ""))
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit",
                                         prompt=cwf_codex.FEEDBACK_PREFIX + body))
        self.assertEqual(self.issues(), 0, "prefixed feedback must not open an issue")
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=body))
        self.assertEqual(self.issues(), 1, "planted control: the same text unprefixed opens one")

    # ── stop hook ───────────────────────────────────────────────────────────

    def test_absence_claim_without_enumeration_blocks_with_prefix(self):
        q = "is there any file named foo.txt anywhere in this repo?"
        reply = "No, there is no file named foo.txt anywhere in this repo."
        r = self.write_rollout(rollout_rows(q, [], reply))
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        out = self.hook("stop", self.payload(r, hook_event_name="Stop", stop_hook_active=False,
                                             last_assistant_message=reply))
        self.assertEqual(out.get("decision"), "block")
        self.assertTrue(out["reason"].startswith(cwf_codex.FEEDBACK_PREFIX))

    def test_enumerated_absence_claim_passes(self):
        q = "is there any file named foo.txt anywhere in this repo?"
        reply = "No: find found no file named foo.txt in this repo."
        r = self.write_rollout(rollout_rows(
            q, [("exec_command", {"cmd": "find . -name foo.txt"}, "")], reply))
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        out = self.hook("stop", self.payload(r, hook_event_name="Stop", stop_hook_active=False,
                                             last_assistant_message=reply))
        self.assertNotEqual(out.get("decision"), "block", out)

    def test_continuation_stop_never_blocks_again(self):
        """Same setup as the blocking test; only stop_hook_active differs. If this blocked,
        Codex would loop on its own continuation."""
        q = "is there any file named foo.txt anywhere in this repo?"
        reply = "No, there is no file named foo.txt anywhere in this repo."
        r = self.write_rollout(rollout_rows(q, [], reply))
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        first = self.hook("stop", self.payload(r, hook_event_name="Stop", stop_hook_active=False,
                                               last_assistant_message=reply))
        self.assertEqual(first.get("decision"), "block", "control: the first stop must block")
        again = self.hook("stop", self.payload(r, hook_event_name="Stop", stop_hook_active=True,
                                               last_assistant_message=reply))
        self.assertNotEqual(again.get("decision"), "block", again)

    def test_unmatched_reply_is_reported_not_judged(self):
        q = "is there any file named foo.txt anywhere in this repo?"
        r = self.write_rollout(rollout_rows(q, [], "No."))
        out = self.hook("stop", self.payload(r, hook_event_name="Stop",
                                             last_assistant_message="a reply never written"))
        self.assertNotEqual(out.get("decision"), "block")
        self.assertIn("never appeared in the transcript", out.get("systemMessage", ""))

    def test_failed_step_is_reported(self):
        code, _, _, problem = cwf_codex.run_step("no-such-step", {}, dict(os.environ))
        self.assertNotEqual(code, 0)
        self.assertIn("no-such-step exited", problem)

    def test_nothing_written_under_claude_dirs(self):
        q = "is there any file named foo.txt anywhere in this repo?"
        r = self.write_rollout(rollout_rows(q, [], "No."))
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        self.hook("stop", self.payload(r, hook_event_name="Stop", last_assistant_message="No."))
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude")))
        self.assertTrue(os.path.isdir(os.path.join(self.proj, ".codex-workforce")))

    # ── juror ───────────────────────────────────────────────────────────────

    def test_juror_prompt_has_no_drift(self):
        prompt, missed = cwf_juror.build_prompt({"session_id": "s"}, "/x/flag.json")
        self.assertEqual(missed, [], "upstream juror prompt changed; update REPLACEMENTS")
        for claude_only in ("$ARGUMENTS", "<scratchpad_dir>", "Bash may be denied"):
            self.assertNotIn(claude_only, prompt)
        self.assertIn('{"ok": true}', prompt)

    # ── state directory safety ──────────────────────────────────────────────

    def test_symlinked_state_dir_is_refused_and_nothing_leaks(self):
        outside = os.path.join(self.tmp, "elsewhere")
        os.makedirs(outside)
        os.symlink(outside, os.path.join(self.proj, ".codex-workforce"))
        with self.assertRaises(cwf_codex.UnsafeStateDir):
            cwf_codex.state_dir(self.proj, "scratch", "s1")
        q = "is there any file named foo.txt anywhere in this repo?"
        out = self.hook("prompt", self.payload(self.write_rollout(rollout_rows(q, [], "")),
                                               hook_event_name="UserPromptSubmit", prompt=q))
        self.assertIn("symlink", out.get("systemMessage", ""))
        self.assertEqual(os.listdir(outside), [], "a prompt was written through the link")

    def test_symlinked_inner_dir_is_refused(self):
        outside = os.path.join(self.tmp, "elsewhere")
        os.makedirs(outside)
        os.makedirs(os.path.join(self.proj, ".codex-workforce"))
        os.symlink(outside, os.path.join(self.proj, ".codex-workforce", "scratch"))
        with self.assertRaises(cwf_codex.UnsafeStateDir):
            cwf_codex.state_dir(self.proj, "scratch", "s1")
        self.assertEqual(os.listdir(outside), [])

    def test_state_dir_rejects_path_components(self):
        for bad in ("..", "a/b", ""):
            with self.assertRaises(cwf_codex.UnsafeStateDir):
                cwf_codex.state_dir(self.proj, bad)

    # ── .gitignore ──────────────────────────────────────────────────────────

    INFRA = [".claude/workforce/x.json", "CLAUDE.md", ".crush/crush.db", ".opencode/x",
             ".playwright-mcp/page.yml", ".codex-workforce/issues/s.json",
             "tests/__pycache__/x.pyc", ".env"]
    PACKAGE = ["AGENTS.md", ".agents/skills/cwf-blueprint/SKILL.md", ".codex/hooks.json",
               "cwf/bin/cwf-hook", "cwf/lib/cwf_codex.py", "scripts/sync-upstream",
               "tests/test_senses.py", "upstream/claude-workforce/UPSTREAM.md", ".gitignore"]

    def _ignored(self, paths):
        r = subprocess.run(["git", "-C", ROOT, "check-ignore", "--no-index", "--stdin"],
                           input="\n".join(paths), capture_output=True, text=True)
        return set(r.stdout.split())

    def test_gitignore_hides_build_infrastructure(self):
        self.assertEqual(self._ignored(self.INFRA), set(self.INFRA))

    def test_gitignore_keeps_the_package(self):
        self.assertEqual(self._ignored(self.PACKAGE), set())

    def test_no_untracked_infrastructure_would_be_committed(self):
        r = subprocess.run(["git", "-C", ROOT, "ls-files", "--others", "--exclude-standard"],
                           capture_output=True, text=True)
        tops = {p.split("/", 1)[0] for p in r.stdout.split()}
        allowed = {"AGENTS.md", ".agents", ".codex", "cwf", "scripts", "tests", "upstream",
                   ".gitignore", "README.md", "LICENSE", "install", "install.ps1",
                   "manifest.txt", "VERSION", "CHANGELOG.md"}
        self.assertEqual(tops - allowed, set(), "unexpected files would be committed")

    def test_upstream_is_unmodified(self):
        """upstream/ must stay byte-identical to the pinned commit (UPSTREAM.md checksums)."""
        import hashlib
        base = os.path.join(ROOT, "upstream", "claude-workforce")
        with open(os.path.join(base, "UPSTREAM.md")) as fh:
            lines = fh.readlines()
        for line in lines:
            if line.startswith("- `workforce/"):
                rel, digest = line[3:].split("` ")
                with open(os.path.join(base, rel), "rb") as fh:
                    self.assertEqual(hashlib.sha256(fh.read()).hexdigest()[:16], digest.strip(), rel)


if __name__ == "__main__":
    unittest.main()
