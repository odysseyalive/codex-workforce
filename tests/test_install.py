"""Tests for the bash installer (`install`), the manifest and the version file.

Run:  python3 -m unittest discover -s tests -v
Installs from this checkout (CWF_REPO_URL=file://...) into temporary HOME and project
directories, so nothing on the real machine is touched. install.ps1 is not exercised here.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL = os.path.join(ROOT, "install")


def manifest():
    with open(os.path.join(ROOT, "manifest.txt")) as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith("#")]


def version():
    with open(os.path.join(ROOT, "VERSION")) as fh:
        return fh.read().strip()


class ManifestTests(unittest.TestCase):
    def test_every_manifest_path_exists(self):
        for p in manifest():
            self.assertTrue(os.path.isfile(os.path.join(ROOT, p)), p)

    def test_every_runtime_file_is_in_the_manifest(self):
        listed = set(manifest())
        # upstream's skills/ and agents/ are build input for scripts/build-skills, not
        # runtime; the generated .agents/skills and cwf/agents copies are what ship.
        build_only = (os.path.join("upstream", "claude-workforce", "workforce", "skills"),
                      os.path.join("upstream", "claude-workforce", "workforce", "agents"))
        for top in ("cwf", "upstream", ".agents/skills"):
            for dirpath, dirs, files in os.walk(os.path.join(ROOT, top)):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for f in files:
                    rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
                    if any(rel.startswith(b) for b in build_only):
                        continue
                    self.assertIn(rel, listed, f"{rel} ships nowhere: add it to manifest.txt")

    def test_version_is_dotted_and_in_the_changelog(self):
        with open(os.path.join(ROOT, "VERSION")) as fh:
            v = fh.read().strip()
        self.assertRegex(v, r"^\d+\.\d+\.\d+$")
        with open(os.path.join(ROOT, "CHANGELOG.md")) as fh:
            self.assertIn(f"## {v}", fh.read())


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cwf-install-")
        self.home = os.path.join(self.tmp, "home")
        self.codex = os.path.join(self.home, ".codex")
        os.makedirs(self.codex)
        # An existing hook of someone else's, which every operation must leave alone.
        self.other = {"type": "command", "command": "bash herdr-agent-state.sh session", "timeout": 10}
        with open(os.path.join(self.codex, "hooks.json"), "w") as fh:
            json.dump({"hooks": {"SessionStart": [{"hooks": [self.other]}]}}, fh)
        self.env = dict(os.environ, HOME=self.home, CODEX_HOME=self.codex,
                        CWF_REPO_URL="file://" + ROOT)
        self.env.pop("CWF_SCOPE", None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_install(self, *args, cwd=None, env=None):
        return subprocess.run(["bash", INSTALL, *args], capture_output=True, text=True,
                              cwd=cwd or self.home, env=env or self.env, timeout=120)

    def hooks(self, conf):
        with open(os.path.join(conf, "hooks.json")) as fh:
            return json.load(fh)["hooks"]

    def cwf_handlers(self, hooks):
        return [h for groups in hooks.values() for g in groups for h in g["hooks"]
                if "cwf-hook" in h["command"]]

    def test_user_install_update_and_uninstall(self):
        r = self.run_install("--user")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("installed " + version()
                      + " (user scope)", r.stdout)
        inst = os.path.join(self.codex, "codex-workforce")
        for p in manifest():
            if not p.startswith(".agents/"):
                self.assertTrue(os.path.isfile(os.path.join(inst, p)), p)
        # The agent TOMLs are promoted out of the install tree; the README stays with
        # the package so the source of truth is explained beside them.
        self.assertTrue(os.path.isfile(os.path.join(inst, "cwf", "agents", "README.md")))
        self.assertTrue(os.path.isfile(os.path.join(inst, "RESUME.md")),
                        "the resume handoff must ship with the install")
        self.assertTrue(os.path.isfile(os.path.join(self.home, ".agents/skills/cwf-blueprint/SKILL.md")))
        agent_dest = os.path.join(self.codex, "agents", "content-classifier.toml")
        self.assertTrue(os.path.isfile(agent_dest))
        with open(agent_dest, encoding="utf-8") as fh:
            self.assertIn('name = "cwf-content-classifier"', fh.read())
        hooks = self.hooks(self.codex)
        self.assertEqual(hooks["SessionStart"][0]["hooks"][0], self.other)
        self.assertEqual(len(self.cwf_handlers(hooks)), 4)
        self.assertTrue(all(h["command"].startswith(f'python3 "{inst}/cwf/bin/cwf-hook"')
                            for h in self.cwf_handlers(hooks)))
        self.assertFalse(os.path.exists(os.path.join(self.home, ".claude")))

        again = self.run_install("--user")
        self.assertIn("reinstalled " + version(), again.stdout)
        self.assertEqual(len(self.cwf_handlers(self.hooks(self.codex))), 4, "no duplicate hooks")

        mine = os.path.join(self.home, ".agents/skills/cwf-mine")
        os.makedirs(mine)
        mine_agent = os.path.join(self.codex, "agents", "mine.toml")
        with open(mine_agent, "w") as fh:
            fh.write('name = "mine"\n')
        gone = self.run_install("--user", "--uninstall")
        self.assertEqual(gone.returncode, 0, gone.stderr)
        self.assertFalse(os.path.exists(inst))
        self.assertFalse(os.path.exists(os.path.join(self.home, ".agents/skills/cwf-blueprint")))
        self.assertTrue(os.path.isdir(mine), "uninstall removed a skill it did not install")
        self.assertFalse(os.path.exists(os.path.join(self.codex, "agents", "content-classifier.toml")))
        self.assertTrue(os.path.isfile(mine_agent), "uninstall removed an agent it did not install")
        self.assertEqual(self.hooks(self.codex), {"SessionStart": [{"hooks": [self.other]}]})

    def test_installed_hook_runs(self):
        self.assertEqual(self.run_install("--user").returncode, 0)
        proj = os.path.join(self.tmp, "proj")
        os.makedirs(proj)
        subprocess.run(["git", "init", "-q", proj], check=True)
        hook = os.path.join(self.codex, "codex-workforce", "cwf", "bin", "cwf-hook")
        q = "is there any file named foo.txt anywhere in this repo?"
        r = subprocess.run([sys.executable, hook, "prompt"], capture_output=True, text=True,
                           input=json.dumps({"session_id": "s", "cwd": proj, "prompt": q,
                                             "hook_event_name": "UserPromptSubmit"}),
                           env=dict(self.env, CWF_JUROR="off"), timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("existence", json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"])

    def test_tampered_skill_list_cannot_delete_outside_skills(self):
        self.assertEqual(self.run_install("--user").returncode, 0)
        victim = os.path.join(self.home, "victim")
        os.makedirs(os.path.join(victim, "keep"))
        os.makedirs(os.path.join(self.home, ".agents/skills/cwf-x"))   # makes ../ resolve
        with open(os.path.join(self.codex, "codex-workforce", "installed-skills.txt"), "a") as fh:
            fh.write("cwf-x/../../../victim\ncwf-../../victim\n")
        r = self.run_install("--user", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isdir(os.path.join(victim, "keep")), "uninstall escaped the skills folder")

    def test_tampered_agent_list_cannot_delete_outside_agent_dir(self):
        self.assertEqual(self.run_install("--user").returncode, 0)
        victim = os.path.join(self.home, "victim-agent")
        os.makedirs(victim)
        with open(os.path.join(self.codex, "codex-workforce", "installed-agents.txt"), "a") as fh:
            fh.write("../victim-agent/keep.toml\n../../victim-agent/keep.toml\n")
        r = self.run_install("--user", "--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isdir(victim), "uninstall escaped the agents folder")

    def test_downgrade_is_refused_without_force(self):
        self.assertEqual(self.run_install("--user").returncode, 0)
        with open(os.path.join(self.codex, "codex-workforce", "VERSION"), "w") as fh:
            fh.write("9.9.9\n")
        r = self.run_install("--user")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("downgrade 9.9.9 to " + version(), r.stderr)
        self.assertEqual(self.run_install("--user", "--force").returncode, 0)

    def test_project_install(self):
        proj = os.path.join(self.tmp, "proj")
        os.makedirs(proj)
        subprocess.run(["git", "init", "-q", proj], check=True)
        r = self.run_install("--project", cwd=proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(proj, ".codex/codex-workforce/cwf/bin/cwf-hook")))
        self.assertTrue(os.path.isfile(os.path.join(proj, ".agents/skills/cwf-blueprint/SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(proj, ".codex", "agents", "content-classifier.toml")))
        handlers = self.cwf_handlers(self.hooks(os.path.join(proj, ".codex")))
        self.assertEqual(len(handlers), 4)
        self.assertIn("$(git rev-parse --show-toplevel)", handlers[0]["command"])
        self.assertFalse(os.path.exists(os.path.join(proj, ".claude")))
        # The personal scope is untouched by a project install.
        self.assertEqual(len(self.cwf_handlers(self.hooks(self.codex))), 0)

    def test_project_scope_outside_git_fails_cleanly(self):
        outside = os.path.join(self.tmp, "nogit")
        os.makedirs(outside)
        r = self.run_install("--project", cwd=outside)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("inside a git repository", r.stderr)


if __name__ == "__main__":
    unittest.main()
