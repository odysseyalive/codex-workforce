"""End-to-end tests for the codex-workforce sensory layer (cwf/bin/cwf-hook).

Run:  python3 -m unittest discover -s tests -v
No network and no model calls: the juror is switched off (CWF_JUROR=off) except in
test_juror_prompt_has_no_drift, which only builds the prompt.

Each test works in a fresh git repository in a temp directory. Run them from a normal
shell, not from inside a Codex sandbox: on this machine Codex's sandbox gives /tmp its own
view, and files written there do not persist.
"""
import contextlib
import glob
import importlib.machinery
import importlib.util
import io
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
        # An empty CODEX_HOME, so the re-trust check never reads this machine's own hooks.
        os.makedirs(os.path.join(self.tmp, "codex-home"))
        self.env = dict(os.environ, CWF_JUROR="off",
                        CODEX_HOME=os.path.join(self.tmp, "codex-home"))

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

    def test_tool_map_covers_every_recorded_codex_tool(self):
        names = {"exec_command", "shell", "local_shell", "apply_patch", "web_search",
                 "web_search_call", "web_fetch", "spawn_agent", "wait_agent", "close_agent",
                 "write_stdin", "view_image"}
        self.assertEqual(names - set(cwf_codex.TOOL_MAP), set())
        self.assertEqual(cwf_codex.TOOL_MAP["web_fetch"], "WebFetch")
        # C0.5: lifecycle calls are reads, never outside evidence. A poll or close alone
        # must not let a world claim pass as though something outside had been read.
        self.assertEqual(cwf_codex.TOOL_MAP["wait_agent"], "Read")
        self.assertEqual(cwf_codex.TOOL_MAP["close_agent"], "Read")
        _, rows = self.convert(rollout_rows(
            "who wrote the incident report?",
            [("web_fetch", {"url": "https://example.test/x"}, "outside evidence")],
            "the report says so"))
        tool = [b for r in rows if r["type"] == "assistant"
                for b in r["message"]["content"] if b["type"] == "tool_use"][0]
        self.assertEqual(tool["name"], "WebFetch")

    def test_truncated_rollout_is_not_judged(self):
        path = os.path.join(self.tmp, "cut.jsonl")
        with open(path, "w") as fh:
            fh.write('{"type":"response_item","payload":{"type":"message","role":"assistant"')
        out, matched = cwf_codex.convert_until_reply(
            path, os.path.join(self.tmp, "out.jsonl"), "a reply never written")
        self.assertIsNone(out)
        self.assertFalse(matched)

    def test_wait_or_close_alone_never_opens_hearing(self):
        """C0.5, regression of .codex-workforce/audit/probe_close.py: a world claim whose only
        tool call is a lifecycle poll or close must still block for want of hearing."""
        q = "what is the latest version of the API?"
        reply = "The latest version is 3.2, from the official release page."
        for name, args in (("close_agent", {"id": "a1"}), ("wait_agent", {"ids": ["a1"]})):
            r = self.write_rollout(rollout_rows(q, [(name, args, "{}")], reply))
            self.hook("prompt", self.payload(r, sid="s-" + name, hook_event_name="UserPromptSubmit",
                                             prompt=q))
            out = self.hook("stop", self.payload(r, sid="s-" + name, hook_event_name="Stop",
                                                 stop_hook_active=False,
                                                 last_assistant_message=reply))
            self.assertEqual(out.get("decision"), "block", name)
            self.assertIn("hearing NOT OPENED", out.get("systemMessage", ""), name)

    def test_truncated_rollout_through_the_hook_is_not_judged(self):
        """C0.5, regression of probe_trunc.py: the clean rollout blocks; the same rollout
        with a cut last line is reported not judged, never silently matched."""
        q = "what is the latest version of the API?"
        reply = "The latest version is 3.2, from the official release page."
        rows = rollout_rows(q, [], reply)
        r = self.write_rollout(rows)
        for sid in ("s1", "s2"):
            self.hook("prompt", self.payload(r, sid=sid, hook_event_name="UserPromptSubmit",
                                             prompt=q))
        clean = self.hook("stop", self.payload(r, hook_event_name="Stop", stop_hook_active=False,
                                               last_assistant_message=reply))
        self.assertEqual(clean.get("decision"), "block")
        with open(r, "a") as fh:
            fh.write('{"type":"response_item","payl')
        cut = self.hook("stop", self.payload(r, sid="s2", hook_event_name="Stop",
                                             stop_hook_active=False, last_assistant_message=reply))
        self.assertNotEqual(cut.get("decision"), "block")
        self.assertIn("not judged", cut.get("systemMessage", ""))
        self.assertIn("truncated", cut.get("systemMessage", ""))

    def test_a_claude_chart_is_invisible_to_codex(self):
        """C0.5/M1-M2: a marked Claude chart must not switch Codex into org dispatch, and a
        tagged prompt carries exactly one dispatch line."""
        chart = os.path.join(self.proj, ".claude", "workforce")
        os.makedirs(chart)
        with open(os.path.join(chart, "org-chart.md"), "w") as fh:
            fh.write("<!-- AUTO-GENERATED by /workforce org index -->\n- Lead (T2)\n")
        q = "Fix the bug in parser.py where empty input crashes, then add a regression test."
        r = self.write_rollout(rollout_rows(q, [], ""))
        ctx = self.resume_context(self.hook("prompt", self.payload(
            r, hook_event_name="UserPromptSubmit", prompt=q)))
        self.assertEqual(ctx.count("This project has no workforce org"), 1)
        self.assertNotIn("has a workforce org", ctx)

    def test_turn_budget_never_reads_a_claude_handbook(self):
        """C0.5/M4: a same-named `.claude/agents/<name>.md` cannot cap a Codex agent."""
        os.makedirs(os.path.join(self.proj, ".claude", "agents"))
        with open(os.path.join(self.proj, ".claude", "agents", "worker.md"), "w") as fh:
            fh.write("---\nname: worker\nmaxTurns: 12\n---\n")
        TB = cwf_codex.load_upstream("wf-turn-budget")
        self.assertIsNone(TB.read_cap(self.proj, "worker"))
        self.assertNotIn(".claude", TB.config_root())

    def test_populated_subagent_stop_fixture_is_judged(self):
        """C0.8/F05: the SubagentStop payload Codex 0.167.1 sent live, with its parent and
        child rollouts, is converted and judged, not reported unjudged or unmatched."""
        fx = os.path.join(ROOT, "tests", "fixtures", "subagent-stop-0.167.1")
        with open(os.path.join(fx, "payload.json")) as fh:
            payload = json.load(fh)
        for key in ("transcript_path", "agent_transcript_path"):
            payload[key] = os.path.join(fx, payload[key])
        payload["cwd"] = self.proj
        self.assertEqual(payload["hook_event_name"], "SubagentStop")
        self.assertEqual(payload["last_assistant_message"], "SUBAGENT_PROBE_DONE2")
        p, _env = cwf_codex.normalize_payload(payload)
        self.assertNotIn("cwf_unjudged", p)
        self.assertNotIn("cwf_reply_unmatched", p)
        with open(p["agent_transcript_path"]) as fh:
            rows = [json.loads(l) for l in fh]
        self.assertTrue(all(r.get("isSidechain") for r in rows if "isSidechain" in r))
        out = self.hook("stop", payload)
        msg = out.get("systemMessage", "")
        self.assertNotEqual(out.get("decision"), "block")
        self.assertIn("GROUNDING", msg, "the stop steps never ran on the fixture")
        self.assertIn("not judged", msg)
        self.assertNotIn("never appeared in the transcript", msg)
        self.assertNotIn("failed", msg)

    def test_org_chart_and_dispatch_patches(self):
        TT = cwf_codex.load_upstream("wf-task-tag")
        self.assertEqual(TT.ORG_CHART, os.path.join(".codex-workforce", "org-chart.md"))
        self.assertEqual(TT.ORG_MARKER, cwf_codex.ORG_MARKER)
        self.assertEqual(TT.dispatch_line({"cwd": self.proj}, "i1"), "")

    def test_directives_resolve_codex_toml_handbooks(self):
        TT = cwf_codex.load_upstream("wf-task-tag")
        os.makedirs(os.path.join(self.proj, ".codex", "agents"), exist_ok=True)
        path = os.path.join(self.proj, ".codex", "agents", "worker.toml")
        with open(path, "w") as fh:
            fh.write("name = \"worker\"\n")
        self.assertEqual(TT.handbook_path(self.proj, {"agent_type": "worker"}), path)
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude")))

    def test_widen_patches_never_write_under_claude(self):
        W = cwf_codex.load_upstream("wf-widen")
        TT = cwf_codex.load_upstream("wf-task-tag")
        self.assertEqual(W.OUTPUT_WORK_SEG,
                         os.path.join(".codex-workforce", "work") + os.sep)
        self.assertIn(".codex-workforce/work/<run-id>/{who}/", W.NO_BRIEF)
        self.assertEqual(W.PERF_STORE_PARTS, (".codex-workforce", "personnel"))
        self.assertEqual(W.WORK_DIRS, (".codex-workforce", "work"))
        self.assertNotIn("AskUserQuestion", TT.CHOOSER_RULE)
        self.assertNotIn("shutdown_request", TT.CLEANUP_RULE)
        self.assertNotIn("AskUserQuestion", TT.USER_WORDS + TT.CHOOSER_RULE + TT.CLEANUP_RULE)
        self.assertIn("close_agent", TT.CLEANUP_RULE)
        self.assertIn("plain-text question", TT.CHOOSER_RULE)
        # The paths consumers, not just the constants: a patched constant that a helper
        # ignores is the false-clean F01 was.
        self.assertEqual(W.perf_store(self.proj), os.path.join(
            self.proj, ".codex-workforce", "personnel"))
        os.makedirs(os.path.join(self.proj, ".codex-workforce", "work", "run", "worker"), exist_ok=True)
        with open(os.path.join(self.proj, ".codex-workforce", "work", "run", "worker",
                               "HANDOFF.md"), "w") as fh:
            fh.write("1. The order\n2. The next section\n")
        self.assertIn("The order", W.handoff_brief(self.proj, "worker"))
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude")))

    def test_cap_hit_perf_lands_under_codex_workforce(self):
        """F19/F01: the producer path, not only the constant. Force `at_cap` to report a
        cut and a missing OUTPUT.md, then assert the PERF file lands in the Codex state
        directory and no `.claude/` appears."""
        W = cwf_codex.load_upstream("wf-widen")
        payload = {"cwd": self.proj, "agent_type": "worker", "hook_event_name": "SubagentStop",
                   "session_id": "s1", "agent_id": "a1",
                   "agent_transcript_path": os.path.join(self.tmp, "agent.jsonl")}
        order = ("Write your report to .codex-workforce/work/run/worker/OUTPUT.md")
        os.makedirs(os.path.join(self.proj, ".codex-workforce", "work", "run", "worker"), exist_ok=True)
        with open(os.path.join(self.proj, ".codex-workforce", "work", "run", "worker",
                               "HANDOFF.md"), "w") as fh:
            fh.write("1. " + order + "\n2. done\n")
        path = os.path.join(self.proj, ".codex-workforce", "work", "run", "worker", "OUTPUT.md")
        old = W.at_cap
        W.at_cap = lambda _p: (3, 3, 1)
        try:
            out = W.cap_perf(payload, path, order, (3, 3, 1))
        finally:
            W.at_cap = old
        self.assertIn(".codex-workforce/personnel", out.get("systemMessage", ""))
        self.assertTrue(os.path.isdir(os.path.join(self.proj, ".codex-workforce", "personnel")))
        self.assertTrue(any(n.startswith("PERF-") for n in os.listdir(
            os.path.join(self.proj, ".codex-workforce", "personnel"))))
        name = [n for n in os.listdir(os.path.join(self.proj, ".codex-workforce", "personnel"))
                if n.startswith("PERF-")][0]
        with open(os.path.join(self.proj, ".codex-workforce", "personnel", name)) as fh:
            record = fh.read()
        self.assertIn("**Handbook:** `", record)
        self.assertIn("`.codex/agents/worker.toml`", record)
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude")))

    def test_web_only_research_opens_hearing(self):
        """The F02 case: a `web_fetch` must count as OUTSIDE evidence. The turn's ask is a
        world/history question, so widen's applicable sense is hearing; without the map it
        sees zero outside calls and blocks. With it, the claim has its channel."""
        q = "what is the latest version of the API?"
        reply = "The latest version is 3.2, from the official release page."
        r = self.write_rollout(rollout_rows(
            q, [("web_fetch", {"url": "https://example.test/releases"}, "version 3.2")], reply))
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        out = self.hook("stop", self.payload(r, hook_event_name="Stop", stop_hook_active=False,
                                             last_assistant_message=reply))
        self.assertNotEqual(out.get("decision"), "block", out)

    def test_web_only_research_without_the_fetch_would_block(self):
        """Control for the test above: the same reply and ask with no outside read trips
        the missing-hearing rule. This proves the passing test is not vacuous."""
        q = "what is the latest version of the API?"
        reply = "The latest version is 3.2, from the official release page."
        r = self.write_rollout(rollout_rows(q, [], reply))
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        out = self.hook("stop", self.payload(r, hook_event_name="Stop", stop_hook_active=False,
                                             last_assistant_message=reply))
        self.assertEqual(out.get("decision"), "block", out)

    def test_null_transcript_is_reported_not_judged(self):
        out = self.hook("stop", {"session_id": "s1", "turn_id": "t1", "cwd": self.proj,
                                 "hook_event_name": "Stop", "transcript_path": None,
                                 "last_assistant_message": "done"})
        self.assertNotEqual(out.get("decision"), "block")
        self.assertIn("not judged", out.get("systemMessage", ""))
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude")))

    def test_ephemeral_subagent_null_paths_are_reported(self):
        out = self.hook("stop", {"session_id": "s1", "turn_id": "t1", "cwd": self.proj,
                                 "hook_event_name": "SubagentStop",
                                 "transcript_path": None,
                                 "agent_transcript_path": None,
                                 "last_assistant_message": "done"})
        self.assertIn("not judged", out.get("systemMessage", ""))
        self.assertIn("agent_transcript_path", out.get("systemMessage", ""))
        self.assertFalse(os.path.exists(os.path.join(self.proj, ".claude")))

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

    # ── generated skills and custom agents ───────────────────────────────────

    def test_timezone_writes_the_key_codex_reads_and_round_trips(self):
        """C0.7: cwf-timezone writes `shell_environment_policy.set.TZ` in the user config.toml
        (the key Codex passes to commands; settings.json is not read, measured 2026-11-13),
        and set then clear gives the file back byte for byte."""
        import tomllib
        tool = os.path.join(ROOT, "cwf", "skills", "cwf-timezone", "bin", "cwf-timezone")
        self.assertTrue(os.access(tool, os.X_OK))
        home = os.path.join(self.tmp, "tz-home")
        os.makedirs(home)
        cfg = os.path.join(home, "config.toml")
        original = 'model = "x"\n\n[shell_environment_policy]\ninherit = "all"\n'
        with open(cfg, "w") as fh:
            fh.write(original)
        env = dict(os.environ, CODEX_HOME=home)
        run = lambda *a: subprocess.run([sys.executable, tool, *a], capture_output=True,
                                        text=True, env=env, timeout=30)
        r = run("set", "Asia/Tokyo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('verified on disk: TZ = "Asia/Tokyo"', r.stdout)
        with open(cfg, "rb") as fh:
            data = tomllib.load(fh)
        self.assertEqual(data["shell_environment_policy"]["set"]["TZ"], "Asia/Tokyo")
        self.assertEqual(data["shell_environment_policy"]["inherit"], "all")
        self.assertFalse(os.path.exists(os.path.join(home, "settings.json")))
        r = run("set", "Europe/Berlin")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(cfg, "rb") as fh:
            self.assertEqual(tomllib.load(fh)["shell_environment_policy"]["set"]["TZ"],
                             "Europe/Berlin")
        r = run("clear")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(cfg) as fh:
            self.assertEqual(fh.read(), original)
        self.assertEqual(run("set", "Not/AZone").returncode, 2)
        with open(cfg) as fh:
            self.assertEqual(fh.read(), original)
        shown = json.loads(run("--root", self.proj, "show", "--json").stdout)
        self.assertEqual(shown["config"], cfg)
        self.assertIsNone(shown["preference"])

    def test_timezone_refuses_an_inline_table_rather_than_guessing(self):
        tool = os.path.join(ROOT, "cwf", "skills", "cwf-timezone", "bin", "cwf-timezone")
        home = os.path.join(self.tmp, "tz-home")
        os.makedirs(home)
        cfg = os.path.join(home, "config.toml")
        original = 'shell_environment_policy = { set = { PATH = "/bin" } }\n'
        with open(cfg, "w") as fh:
            fh.write(original)
        r = subprocess.run([sys.executable, tool, "set", "Asia/Tokyo"], capture_output=True,
                           text=True, env=dict(os.environ, CODEX_HOME=home), timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Edit it by hand", r.stderr)
        with open(cfg) as fh:
            self.assertEqual(fh.read(), original)

    def test_code_eval_settings_writer_sibling_loads(self):
        """wf-code-eval imports wf-settings-apply as a sibling for its CWE-59 refusal; the
        generated copy must exist and target Codex's config root."""
        writer = os.path.join(ROOT, "cwf", "bin", "wf-settings-apply")
        with open(writer) as fh:
            text = fh.read()
        self.assertIn('os.environ.get("CODEX_HOME") or os.path.join(os.path.expanduser("~"), ".codex")', text)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "cwf", "bin", "wf-code-eval"),
                            "--root", self.proj, "--stamp"], capture_output=True, text=True,
                           timeout=60)
        self.assertNotIn("Traceback", r.stderr)

    def test_generated_skills_are_nine_and_speak_codex(self):
        """Generation is a product surface: seven upstream skills plus the port's own
        `cwf-dev` and `cwf-timezone`, `$cwf-` invocation,
        no Claude command namespace or `.claude/` state path, and valid YAML metadata."""
        import yaml
        base = os.path.join(ROOT, "cwf", "skills")
        skills = sorted(d for d in os.listdir(base)
                        if d.startswith("cwf-") and os.path.isfile(
                            os.path.join(base, d, "SKILL.md")))
        self.assertEqual(skills, ["cwf-blueprint", "cwf-code-evaluator", "cwf-dev",
                                  "cwf-records-code-map", "cwf-security-evaluator",
                                  "cwf-shared-artifact", "cwf-text-eval", "cwf-timezone",
                                  "cwf-ui-design"])
        for name in skills:
            p = os.path.join(base, name, "SKILL.md")
            with open(p, encoding="utf-8") as fh:
                text = fh.read()
            head = text.split("\n---\n", 1)[0].lstrip("---\n")
            meta = yaml.safe_load(head)
            self.assertEqual(meta.get("name"), name)
            # Skip the generated-by comment: it names the upstream source path.
            body = text.split("-->", 1)[-1]
            for bad in (".claude/", "AskUserQuestion", "/blueprint", "/code-evaluator",
                        "/records-code-map", "/security-evaluator", "/shared-artifact",
                        "/text-eval", "/timezone", "/ui-design"):
                self.assertNotIn(bad, body, f"{name} still carries {bad}")
        with open(os.path.join(base, "cwf-blueprint", "SKILL.md"), encoding="utf-8") as fh:
            self.assertIn("$cwf-blueprint", fh.read())

    def test_generated_skill_scripts_start_and_stay_in_codex_paths(self):
        """The skills name three scripts by path. A shipped copy that cannot start, or that
        still writes `.claude/`, makes the documented command a dead end."""
        code_eval = subprocess.run([sys.executable, os.path.join(ROOT, "cwf", "bin", "wf-code-eval"),
                                    "--root", self.proj], capture_output=True, text=True, timeout=30)
        self.assertEqual(code_eval.returncode, 0, code_eval.stderr)
        self.assertIn("0 gate(s)", code_eval.stdout)
        code_map = subprocess.run([sys.executable, os.path.join(ROOT, "cwf", "bin", "wf-map"),
                                   "--root", self.proj, "--topic", "nothing-here"],
                                  capture_output=True, text=True, timeout=30)
        self.assertEqual(code_map.returncode, 0, code_map.stderr)
        self.assertIn("nothing matched", code_map.stdout)
        # The installed layout is <root>/cwf/bin. Both skills must use that path,
        # not the upstream repository layout they were copied from.
        for skill, needle in (("cwf-code-evaluator", "$WF/cwf/bin/wf-code-eval"),
                              ("cwf-records-code-map", "$WF/cwf/bin/wf-map")):
            with open(os.path.join(ROOT, "cwf", "skills", skill, "SKILL.md"),
                      encoding="utf-8") as fh:
                self.assertIn(needle, fh.read())
        for name, forbidden in (
                ("wf-code-eval", ('".claude"', "CLAUDE_CONFIG_DIR", "CLAUDE_PROJECT_DIR")),
                ("wf-map", ('".claude"', "CLAUDE_PROJECT_DIR")),
                # wf-census carries unrelated Claude-era audit helpers; only the paths
                # wf-code-eval reaches are in scope, and those are checked by the run above.
                ("wf-census", ('os.environ.get("CLAUDE_CONFIG_DIR")',))):
            with open(os.path.join(ROOT, "cwf", "bin", name), encoding="utf-8") as fh:
                text = fh.read()
            for bad in forbidden:
                self.assertNotIn(bad, text, name)

    def test_readme_counts_match_generated_tree(self):
        with open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8") as fh:
            agents_md = fh.read()
        self.assertIn("Seven upstream skills", agents_md)
        self.assertIn("ten Codex custom agents", agents_md)
        with open(os.path.join(ROOT, "VERSION")) as fh:
            self.assertIn("VERSION` holds the release (`" + fh.read().strip(), agents_md)

    def test_generated_custom_agents_parse_and_state_host_limits(self):
        import tomllib
        base = os.path.join(ROOT, "cwf", "agents")
        files = sorted(f for f in os.listdir(base) if f.endswith(".toml"))
        self.assertEqual(len(files), 10)
        for fn in files:
            with open(os.path.join(base, fn), "rb") as fh:
                data = tomllib.load(fh)
            for key in ("name", "description", "developer_instructions"):
                self.assertTrue(data.get(key), f"{fn} lacks {key}")
            self.assertTrue(data["name"].startswith("cwf-") or data["name"] in (
                "code-design-advisor", "deadcode-gardener"))
            self.assertIn("Host limits:", data["developer_instructions"])
            self.assertNotIn("tools =", data)
            self.assertNotIn("disallowedTools =", data)
            for bad in (".claude/", "CLAUDE_PROJECT_DIR", "AskUserQuestion",
                        "shutdown_request"):
                self.assertNotIn(bad, data["developer_instructions"], fn)

    # ── prompt hook ─────────────────────────────────────────────────────────

    def test_prompt_hook_tags_existence_ask(self):
        q = "is there any file named foo.txt anywhere in this repo?"
        out = self.hook("prompt", self.payload(self.write_rollout(rollout_rows(q, [], "")),
                                               hook_event_name="UserPromptSubmit", prompt=q))
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("existence", ctx)
        self.assertIn("TASTE", ctx)

    # ── resume handoff ──────────────────────────────────────────────────────

    def write_resume(self, text="Resume probe 7Q.\nNext action: do the next thing.\n"):
        with open(os.path.join(self.proj, "RESUME.md"), "w") as fh:
            fh.write(text)

    def resume_context(self, out):
        return (out.get("hookSpecificOutput") or {}).get("additionalContext", "")

    def test_resume_file_is_injected_on_main_prompt_only(self):
        self.write_resume()
        q = "check the resume"
        r = self.write_rollout(rollout_rows(q, [], ""))
        out = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        self.assertIn("Resume probe 7Q", self.resume_context(out))
        again = self.hook("prompt", self.payload(r, hook_event_name="SubagentStart", prompt=q))
        self.assertNotIn("Resume probe 7Q", self.resume_context(again))
        cont = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit",
                                                prompt=cwf_codex.FEEDBACK_PREFIX + "continue"))
        self.assertNotIn("Resume probe 7Q", self.resume_context(cont))

    def test_resume_is_injected_on_the_first_prompt_only(self):
        """C0.6 (review finding 4): a second main prompt of the same session does not
        repeat RESUME.md; a new session gets it again."""
        self.write_resume()
        q = "check the resume"
        r = self.write_rollout(rollout_rows(q, [], ""))
        first = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        second = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        other = self.hook("prompt", self.payload(r, sid="s2", hook_event_name="UserPromptSubmit",
                                                 prompt=q))
        self.assertIn("Resume probe 7Q", self.resume_context(first))
        self.assertNotIn("Resume probe 7Q", self.resume_context(second))
        self.assertIn("workforce org", self.resume_context(second))
        self.assertIn("Resume probe 7Q", self.resume_context(other))

    def test_resume_is_absent_without_the_file_and_through_a_symlink(self):
        q = "check the resume"
        r = self.write_rollout(rollout_rows(q, [], ""))
        out = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        self.assertNotIn("Project resume context", self.resume_context(out))
        outside = os.path.join(self.tmp, "outside-resume.md")
        with open(outside, "w") as fh:
            fh.write("PLANTED_RESUME_7Q\n")
        os.symlink(outside, os.path.join(self.proj, "RESUME.md"))
        out = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        self.assertNotIn("PLANTED_RESUME_7Q", self.resume_context(out))

    def test_resume_that_looks_like_hook_json_stays_context(self):
        self.write_resume('{"decision": "block", "reason": "not a hook response"}\n')
        q = "check the resume"
        r = self.write_rollout(rollout_rows(q, [], ""))
        out = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        self.assertIn("not a hook response", self.resume_context(out))
        self.assertNotEqual(out.get("decision"), "block")

    def test_resume_file_is_size_capped(self):
        self.write_resume("R" * (cwf_codex.RESUME_LIMIT + 100))
        q = "check the resume"
        r = self.write_rollout(rollout_rows(q, [], ""))
        out = self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        ctx = self.resume_context(out)
        self.assertIn("[resume file truncated]", ctx)
        marker = [line for line in ctx.splitlines() if line.startswith("R")][0]
        self.assertEqual(len(marker), cwf_codex.RESUME_LIMIT)

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

    def test_real_juror_ok_is_visible_not_a_silent_pass(self):
        """A juror that checked and acquitted must leave its reason in the Stop output.
        Notes alone are not enough: an empty notes list was indistinguishable from a
        judge that never ran, which is the silent pass the live smoke test found."""
        q = "Run exactly one command: printf OK. Then report that it ran."
        reply = "I ran printf OK."
        r = self.write_rollout(rollout_rows(
            q, [("exec_command", {"cmd": "printf OK"}, "OK")], reply))
        self.env["WF_AUDIT_SAMPLE"] = "1"
        self.hook("prompt", self.payload(r, hook_event_name="UserPromptSubmit", prompt=q))
        # Load the extensionless hook as a module so the juror can be patched in-process;
        # the hook itself still runs the real ledger and widen and writes a real flag.
        loader = importlib.machinery.SourceFileLoader("cwf_hook_under_test", HOOK)
        spec = importlib.util.spec_from_loader("cwf_hook_under_test", loader)
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)
        old = cwf_juror.judge
        cwf_juror.judge = lambda *_a, **_k: ({
            "ok": True, "reason": "touch: ran printf and saw OK", "notes": []}, "")
        try:
            payload = self.payload(r, hook_event_name="Stop", stop_hook_active=False,
                                   last_assistant_message=reply)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(hook.stop_event(payload), 0)
        finally:
            cwf_juror.judge = old
        out = json.loads(buf.getvalue())
        self.assertEqual(len(glob.glob(os.path.join(
            self.proj, ".codex-workforce", "scratch", "s1", "wf-widen-flag.*.json"))), 1)
        self.assertNotEqual(out.get("decision"), "block", out)
        self.assertIn("cwf juror: touch: ran printf and saw OK", out.get("systemMessage", ""))

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

    INFRA = [".claude/workforce/x.json", "CLAUDE.md", ".crush/crush.db", ".crushrc",
             "crushrc", ".opencode/x", ".playwright-mcp/page.yml",
             ".codex-workforce/issues/s.json",
             "tests/__pycache__/x.pyc", ".env"]
    PACKAGE = ["AGENTS.md", "RESUME.md", "cwf/skills/cwf-blueprint/SKILL.md",
               "cwf/skills/cwf-code-evaluator/SKILL.md",
               "cwf/skills/cwf-text-eval/SKILL.md", ".codex/hooks.json",
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
        allowed = {"AGENTS.md", "RESUME.md", ".codex", "cwf", "scripts", "tests",
                   "upstream", ".gitignore", "README.md", "LICENSE", "install", "install.ps1",
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


class HookTrustTests(unittest.TestCase):
    """C0.8: Codex skips a hook whose definition changed since `/hooks` trusted it. The hash
    format was reproduced against live trusted_hash rows on codex-cli 0.169.0."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cwf-trust-")
        self.proj = os.path.join(self.tmp, "proj")
        os.makedirs(os.path.join(self.proj, ".codex"))
        subprocess.run(["git", "init", "-q", self.proj], check=True)
        self.home = os.path.join(self.tmp, "codex-home")
        os.makedirs(self.home)
        self.hooks = os.path.join(self.proj, ".codex", "hooks.json")
        shutil.copy(os.path.join(ROOT, ".codex", "hooks.json"), self.hooks)
        self.env = dict(os.environ, CODEX_HOME=self.home, CWF_JUROR="off")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def trust_all(self):
        with open(self.hooks) as fh:
            hooks = json.load(fh)["hooks"]
        lines = ["[hooks.state]", ""]
        path = os.path.abspath(self.hooks)
        for event, groups in hooks.items():
            for gi, g in enumerate(groups):
                for hi, h in enumerate(g["hooks"]):
                    key = f"{path}:{cwf_codex._snake(event)}:{gi}:{hi}"
                    lines += [f'[hooks.state."{key}"]',
                              f'trusted_hash = "{cwf_codex.hook_trust_hash(event, g, h)}"', ""]
        with open(os.path.join(self.home, "config.toml"), "w") as fh:
            fh.write("\n".join(lines))

    def test_hash_matches_a_recorded_codex_trust_row(self):
        # Recorded from this repository's own ~/.codex/config.toml on 2026-11-13.
        group = {"hooks": [{"type": "command", "timeout": 300,
                            "command": 'python3 "$(git rev-parse --show-toplevel)/cwf/bin/cwf-hook" stop'}]}
        self.assertEqual(cwf_codex.hook_trust_hash("SubagentStop", group, group["hooks"][0]),
                         "sha256:aea799b5f836efd7172d52f598bab76bc70465f1e0ecc1e1058fc9ec95e4cfd7")

    def prompt(self, sid):
        r = subprocess.run([sys.executable, HOOK, "prompt"], capture_output=True, text=True,
                           env=self.env, timeout=60,
                           input=json.dumps({"session_id": sid, "cwd": self.proj,
                                             "hook_event_name": "UserPromptSubmit",
                                             "prompt": "hello"}))
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout).get("systemMessage", "")

    def test_trusted_hooks_say_nothing_and_a_changed_one_is_named_once(self):
        self.trust_all()
        self.assertNotIn("re-trusted", self.prompt("s1"))
        check = subprocess.run([sys.executable, HOOK, "trust-check", self.hooks],
                               capture_output=True, text=True, env=self.env, timeout=30)
        self.assertEqual(check.returncode, 0, check.stdout)
        with open(self.hooks) as fh:
            data = json.load(fh)
        data["hooks"]["Stop"][0]["hooks"][0]["timeout"] = 299
        with open(self.hooks, "w") as fh:
            json.dump(data, fh)
        msg = self.prompt("s2")
        self.assertIn("open /hooks", msg)
        self.assertIn("stop", msg)
        self.assertNotIn("open /hooks", self.prompt("s2"), "the notice repeats every prompt")
        check = subprocess.run([sys.executable, HOOK, "trust-check", self.hooks],
                               capture_output=True, text=True, env=self.env, timeout=30)
        self.assertEqual(check.returncode, 1)
        self.assertIn("changed", check.stdout)

    def test_never_trusted_hooks_are_new(self):
        states = [st for _k, st in cwf_codex.hook_trust_status(
            self.hooks, os.path.join(self.home, "config.toml"))]
        self.assertEqual(states, ["unknown"] * 4)
        with open(os.path.join(self.home, "config.toml"), "w") as fh:
            fh.write("model = \"x\"\n")
        states = [st for _k, st in cwf_codex.hook_trust_status(
            self.hooks, os.path.join(self.home, "config.toml"))]
        self.assertEqual(states, ["new"] * 4)


class ModelLaneTests(unittest.TestCase):
    """Every generated agent pins a model, and every pin is a model Codex can catalogue.

    The pin is the feature: an agent that inherits the session model is not on its lane.
    The catalog check exists because a model catalog entry with a bad field is a Codex-wide
    startup error — one malformed `input_modalities` value broke every `codex exec` here on
    2026-11-12, and a test that only parsed the TOMLs would have missed it.
    """

    def setUp(self):
        self.agents = sorted(glob.glob(os.path.join(ROOT, "cwf", "agents", "*.toml")))
        self.assertTrue(self.agents, "no generated agents found")

    def test_every_agent_pins_a_model_and_an_effort(self):
        import tomllib
        for path in self.agents:
            with open(path, "rb") as fh:
                fields = tomllib.load(fh)
            with self.subTest(agent=os.path.basename(path)):
                self.assertTrue(fields.get("model"), "no model pin")
                self.assertIn(fields.get("model_reasoning_effort"),
                              ("low", "medium", "high"),
                              "effort missing or outside the sanctioned rungs")
                self.assertIn("Model lane:", fields["developer_instructions"])
                for key in ("name", "description", "developer_instructions"):
                    self.assertTrue(fields.get(key), key)

    def test_every_pin_is_a_unique_lane_default(self):
        import tomllib
        pins = {}
        for path in self.agents:
            with open(path, "rb") as fh:
                fields = tomllib.load(fh)
            pins[os.path.basename(path)] = fields["model"]
        lane_models = {"google/gemini-4-carbon", "meta/muse-wonder",
                       "anthropic/claude-opus-5", "anthropic/claude-opus-5.5"}
        for name, model in pins.items():
            with self.subTest(agent=name):
                self.assertIn(model, lane_models,
                              "a pin outside the four lane defaults drifted in")

    def test_an_installed_catalog_entry_is_well_formed(self):
        """If a catalog exists, every modality must be one Codex accepts.

        This is the regression for the field that broke Codex's startup: `file` is
        carried by OpenRouter but is not a valid Codex input modality.
        """
        import json
        catalog = os.path.join(os.path.expanduser("~"), ".codex",
                               "openrouter-model-catalog.json")
        if not os.path.isfile(catalog):
            self.skipTest("no local model catalog on this machine")
        with open(catalog) as fh:
            models = json.load(fh)["models"]
        allowed = {"text", "image", "audio"}
        for model in models:
            bad = set(model.get("input_modalities") or []) - allowed
            with self.subTest(model=model.get("id")):
                self.assertFalse(bad, f"invalid input modalities: {sorted(bad)}")


class DispatchContextTests(unittest.TestCase):
    """The prompt hook must tell a session that a job can go to a subagent.

    Upstream added this line after measuring a project that did a whole job in the main thread
    because nothing said otherwise (wf-task-tag, measured 2026-11-08). Codex has no tagger
    hook, so this port injects it on every main-session prompt. It is advisory: nothing refuses.
    """

    def test_no_org_names_a_plain_subagent_and_the_code_lane(self):
        with tempfile.TemporaryDirectory() as d:
            ctx = cwf_codex.dispatch_context(d)
        self.assertIn("no workforce org", ctx)
        self.assertIn("plain `general-purpose` subagent", ctx)
        self.assertIn("cwf-implementer", ctx)
        self.assertIn("close_agent", ctx)
        self.assertIn("Work inline only when", ctx)

    def test_a_marked_chart_selects_the_org_line(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".codex-workforce"))
            with open(os.path.join(d, ".codex-workforce", "org-chart.md"), "w") as fh:
                fh.write("# chart\n<!-- AUTO-GENERATED by an index run -->\n")
            ctx = cwf_codex.dispatch_context(d)
        self.assertIn("has a workforce org", ctx)
        self.assertNotIn("no workforce org", ctx)
        self.assertIn("background plain subagent", ctx)

    def test_an_unmarked_chart_is_not_an_org(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".codex-workforce"))
            with open(os.path.join(d, ".codex-workforce", "org-chart.md"), "w") as fh:
                fh.write("# hand-written, no marker\n")
            ctx = cwf_codex.dispatch_context(d)
        self.assertIn("no workforce org", ctx)

    def test_only_a_main_prompt_receives_it(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".codex-workforce"))
            base = {"session_id": "s1", "cwd": d, "transcript_path": ""}
            prompt, _ = cwf_codex.normalize_payload(
                dict(base, hook_event_name="UserPromptSubmit", prompt="hi"))
            stop, _ = cwf_codex.normalize_payload(dict(base, hook_event_name="Stop"))
        self.assertIn("workforce org", prompt["cwf_dispatch_context"])
        self.assertEqual(stop["cwf_dispatch_context"], "")


if __name__ == "__main__":
    unittest.main()
