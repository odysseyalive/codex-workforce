"""C1.1: `cwf/bin/cwf-org register` turns a project handbook into `.codex/agents/<name>.toml`.

Run:  python3 -m unittest discover -s tests -v
Each test works in a fresh git repository with its own CODEX_HOME, so the user-scope agents
directory it sees is the test's, never this machine's.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "cwf", "bin", "cwf-org")
sys.path.insert(0, os.path.join(ROOT, "cwf", "lib"))

import cwf_agents  # noqa: E402

# Bytes a naive TOML writer gets wrong: backslashes, a triple quote, a quote at the end of a
# line, a tab, a form feed, DEL, non-ASCII, an astral character, and a trailing backslash.
HARD_BODY = ('# Pricing copy\n\nMatch `\\d+\\.\\d{2}` and C:\\new\\table.\n'
             'Never write """ or "" or a closing "\n\ttabbed\x0cfeed\x7fdel — ünï 🧾\n'
             'ends with a backslash \\')


class OrgRegisterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cwf-org-test-")
        self.proj = os.path.join(self.tmp, "proj")
        os.makedirs(os.path.join(self.proj, "handbooks"))
        subprocess.run(["git", "init", "-q", self.proj], check=True)
        self.home = os.path.join(self.tmp, "codex-home")
        os.makedirs(os.path.join(self.home, "agents"))
        self.env = dict(os.environ, CODEX_HOME=self.home)
        self.agents = os.path.join(self.proj, ".codex", "agents")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def handbook(self, name, body=HARD_BODY, fm=None):
        fm = fm or {"name": name, "description": '"Owns pricing copy: edits, checks."',
                    "tools": "Read, Edit", "disallowedTools": "Agent", "effort": "medium"}
        path = os.path.join(self.proj, "handbooks", f"{name.replace('/', '_')}.md")
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write("---\n" + "".join(f"{k}: {v}\n" for k, v in fm.items()) + "---\n\n" + body)
        return path

    def run_tool(self, *args):
        return subprocess.run([sys.executable, TOOL, *args, "--project", self.proj]
                              if args[0] == "check" else
                              [sys.executable, TOOL, args[0], "--project", self.proj, *args[1:]],
                              capture_output=True, text=True, env=self.env, timeout=60)

    def load(self, name):
        with open(os.path.join(self.agents, name + ".toml"), "rb") as fh:
            return tomllib.load(fh)

    def test_register_writes_toml_that_parses_with_the_handbook_verbatim(self):
        hb = self.handbook("pricing-copy")
        r = self.run_tool("register", "--execute", hb)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("(parsed back)", r.stdout)
        data = self.load("pricing-copy")
        self.assertEqual(data["name"], "pricing-copy")
        self.assertEqual(data["description"], "Owns pricing copy: edits, checks.")
        self.assertEqual(data["model_reasoning_effort"], "medium")
        self.assertNotIn("model", data, "no model in the handbook, so none is invented")
        instr = data["developer_instructions"]
        self.assertTrue(instr.startswith("Host limits:"), instr[:80])
        self.assertIn("`Read, Edit` and `Agent`", instr.split("\n", 1)[0])
        self.assertTrue(instr.endswith("\n\n" + HARD_BODY + "\n"),
                        "the handbook body must survive byte for byte")
        self.assertEqual(set(data), {"name", "description", "model_reasoning_effort",
                                     "developer_instructions"},
                         "tools/disallowedTools are prose, never TOML keys")

    def test_plan_writes_nothing_and_a_rerun_is_unchanged(self):
        hb = self.handbook("pricing-copy")
        r = self.run_tool("register", hb)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("plan only", r.stdout)
        self.assertFalse(os.path.lexists(os.path.join(self.proj, ".codex")))
        self.run_tool("register", "--execute", hb)
        with open(os.path.join(self.agents, "pricing-copy.toml"), "rb") as fh:
            first = fh.read()
        r = self.run_tool("register", "--execute", hb)
        self.assertIn("UNCHANGED", r.stdout)
        with open(os.path.join(self.agents, "pricing-copy.toml"), "rb") as fh:
            self.assertEqual(fh.read(), first, "regenerating must be byte-identical")

    def test_a_user_scope_same_name_is_reported_and_never_overwritten(self):
        user_copy = os.path.join(self.home, "agents", "pricing-copy.toml")
        original = b'name = "pricing-copy"\ndescription = "the user\'s own"\ndeveloper_instructions = "mine"\n'
        with open(user_copy, "wb") as fh:
            fh.write(original)
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("SHADOWED", r.stdout)
        self.assertIn(user_copy, r.stdout)
        with open(user_copy, "rb") as fh:
            self.assertEqual(fh.read(), original, "the user-scope file must be untouched")
        self.assertFalse(os.path.lexists(os.path.join(self.agents, "pricing-copy.toml")))

    def test_a_user_scope_name_field_shadows_too(self):
        """Codex resolves by the `name` field, so a differently-named file still shadows."""
        with open(os.path.join(self.home, "agents", "other-file.toml"), "w") as fh:
            fh.write('name = "pricing-copy"\ndescription = "d"\ndeveloper_instructions = "x"\n')
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("SHADOWED", r.stdout)

    def test_check_reports_a_project_agent_the_user_scope_shadows(self):
        self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        self.assertEqual(self.run_tool("check").returncode, 0)
        shutil.copy(os.path.join(self.agents, "pricing-copy.toml"),
                    os.path.join(self.home, "agents", "pricing-copy.toml"))
        r = self.run_tool("check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("SHADOWED", r.stdout)

    def test_block_style_and_malformed_quoting_are_refused(self):
        """A multi-line value is refused rather than guessed; one-line JSON quoting works."""
        for bad in ("description: >", "description: \"Say \"hi\"", "description: 'broken"):
            with self.subTest(bad=bad):
                path = os.path.join(self.proj, "handbooks", "bad-quote.md")
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write("---\nname: bad-quote\n" + bad + "\n---\n\nbody\n")
                r = self.run_tool("register", "--execute", path)
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("not supported" if bad == "description: >" else "malformed", r.stdout)

    def test_project_codex_equal_to_the_user_home_is_refused_before_agents_exists(self):
        self.home = os.path.join(self.proj, ".codex")
        self.env["CODEX_HOME"] = self.home
        os.makedirs(self.home)
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("user-scope Codex home", r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.home, "agents")))

    def test_non_utf8_toml_is_reported_not_crashed(self):
        os.makedirs(self.agents)
        with open(os.path.join(self.agents, "broken.toml"), "wb") as fh:
            fh.write(b'\xffname = "broken"\n')
        r = self.run_tool("check")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("QUARANTINED", r.stdout)

    def test_check_flags_a_symlinked_agents_directory(self):
        outside = os.path.join(self.tmp, "outside")
        os.makedirs(outside)
        os.makedirs(os.path.join(self.proj, ".codex"))
        os.symlink(outside, self.agents)
        r = self.run_tool("check")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("SYMLINK", r.stdout)

    def test_duplicate_project_names_are_refused_and_flagged(self):
        # Register one generated copy first, then add a hand-made file carrying the same
        # `name` field. register itself must refuse it on a later batch, and check must
        # flag the ambiguous pair.
        self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        with open(os.path.join(self.agents, "handmade.toml"), "w") as fh:
            fh.write('name = "pricing-copy"\ndescription = "d"\ndeveloper_instructions = "x"\n')
        other = self.handbook("pricing-copy", fm={"name": "pricing-copy",
                                                   "description": '"d"'})
        shutil.move(other, os.path.join(self.proj, "handbooks", "other-name.md"))
        r = self.run_tool("register", "--execute",
                          os.path.join(self.proj, "handbooks", "other-name.md"))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("DUPLICATE", r.stdout)
        chk = self.run_tool("check")
        self.assertEqual(chk.returncode, 1)
        self.assertIn("DUPLICATE", chk.stdout)

    def test_a_refusal_writes_nothing_for_the_whole_batch(self):
        with open(os.path.join(self.home, "agents", "taken.toml"), "w") as fh:
            fh.write('name = "taken"\ndescription = "d"\ndeveloper_instructions = "x"\n')
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy"),
                          self.handbook("taken"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("nothing written", r.stdout)
        self.assertFalse(os.path.lexists(os.path.join(self.agents, "pricing-copy.toml")))

    def assert_refused_symlink(self, where):
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("symlink", r.stdout)
        self.assertEqual(os.listdir(where), [], "nothing may land behind the link")

    def test_a_symlinked_codex_dir_is_refused(self):
        outside = os.path.join(self.tmp, "outside")
        os.makedirs(os.path.join(outside, "agents"))
        os.symlink(outside, os.path.join(self.proj, ".codex"))
        self.assert_refused_symlink(os.path.join(outside, "agents"))

    def test_a_symlinked_agents_dir_is_refused(self):
        outside = os.path.join(self.tmp, "outside")
        os.makedirs(outside)
        os.makedirs(os.path.join(self.proj, ".codex"))
        os.symlink(outside, self.agents)
        self.assert_refused_symlink(outside)

    def test_a_symlinked_registration_file_is_refused(self):
        outside = os.path.join(self.tmp, "outside")
        os.makedirs(outside)
        target = os.path.join(outside, "victim.toml")
        with open(target, "w") as fh:
            fh.write("keep me\n")
        os.makedirs(self.agents)
        os.symlink(target, os.path.join(self.agents, "pricing-copy.toml"))
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("symlink", r.stdout)
        with open(target) as fh:
            self.assertEqual(fh.read(), "keep me\n")

    def test_unsafe_names_are_refused(self):
        for bad in ("../escape", "a/b", ".hidden", "Upper", "x" * 65):
            with self.subTest(name=bad):
                fm = {"name": bad, "description": "d"}
                r = self.run_tool("register", "--execute", self.handbook(bad, fm=fm))
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("not a safe agent file name", r.stdout)
        self.assertFalse(os.path.lexists(os.path.join(self.proj, ".codex")))
        self.assertFalse(os.path.lexists(os.path.join(self.tmp, "escape.toml")))

    def test_infrastructure_and_shipped_names_are_refused(self):
        for name in ("cwf-org", "cwf-workforce", "cwf-dev", "cwf-implementer",
                     "deadcode-gardener"):
            with self.subTest(name=name):
                r = self.run_tool("register", "--execute", self.handbook(name))
                self.assertEqual(r.returncode, 1, r.stdout)
        self.assertFalse(os.path.lexists(self.agents))

    def test_an_agent_cwf_org_did_not_generate_is_left_alone(self):
        os.makedirs(self.agents)
        adopted = os.path.join(self.agents, "pricing-copy.toml")
        with open(adopted, "w") as fh:
            fh.write('name = "pricing-copy"\ndescription = "hand-made"\ndeveloper_instructions = "x"\n')
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("adopted", r.stdout)
        with open(adopted) as fh:
            self.assertIn("hand-made", fh.read())

    def test_an_unknown_effort_is_refused_rather_than_written(self):
        fm = {"name": "pricing-copy", "description": "d", "effort": "maximum"}
        r = self.run_tool("register", "--execute", self.handbook("pricing-copy", fm=fm))
        self.assertEqual(r.returncode, 1)
        self.assertFalse(os.path.lexists(self.agents))


class RenderTests(unittest.TestCase):
    def test_render_round_trips_every_hard_string(self):
        for s in (HARD_BODY, '"""', '\\', 'x"', '\x00\x1f', '🧾\U0010ffff', ''):
            with self.subTest(s=s):
                text = cwf_agents.render_agent_toml("n", s, s, model=None, effort=None)
                data = tomllib.loads(text)
                self.assertEqual(data["description"], s)
                self.assertEqual(data["developer_instructions"], s + "\n")

    def test_shipped_agents_regenerate_through_the_same_renderer(self):
        """build-skills renders the package's agents with cwf_agents, so the committed
        TOMLs are the renderer's output: re-rendering each from its parsed values matches."""
        base = os.path.join(ROOT, "cwf", "agents")
        for fn in sorted(f for f in os.listdir(base) if f.endswith(".toml")):
            with self.subTest(agent=fn):
                with open(os.path.join(base, fn), encoding="utf-8") as fh:
                    text = fh.read()
                d = tomllib.loads(text)
                again = cwf_agents.render_agent_toml(
                    d["name"], d["description"], d["developer_instructions"][:-1],
                    model=d.get("model"), effort=d.get("model_reasoning_effort"))
                self.assertEqual(again, text)


if __name__ == "__main__":
    unittest.main()
