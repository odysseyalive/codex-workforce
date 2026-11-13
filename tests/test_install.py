"""Tests for the bash installer (`install`), the manifest and the version file.

Run:  python3 -m unittest discover -s tests -v
Installs from this checkout (CWF_REPO_URL=file://...) into temporary HOME and project
directories, so nothing on the real machine is touched. install.ps1 is not exercised here.
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
        # runtime; the generated cwf/skills and cwf/agents copies are what ship.
        build_only = (os.path.join("upstream", "claude-workforce", "workforce", "skills"),
                      os.path.join("upstream", "claude-workforce", "workforce", "agents"),
                      # sources for agents and skills this package authors itself; the
                      # generator turns each into the artifact that ships
                      os.path.join("cwf", "agents") + os.sep + "cwf-implementer.md",
                      os.path.join("cwf", "skills-src"))
        for top in ("cwf", "upstream"):
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
            # cwf/skills/* is copied to the skills root, not into the install tree; the
            # agent TOMLs are promoted to <config>/agents/. Everything else lands here.
            if not p.startswith("cwf/skills/") and not p.startswith("cwf/agents/"):
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

    def make_tree(self, extra_skill=None, extra_agent=None):
        """A copy of this package's manifest tree, optionally shipping one more skill and
        agent, so an update FROM it to ROOT has something to drop."""
        tree = os.path.join(self.tmp, "tree")
        rows = manifest()
        for p in rows:
            dst = os.path.join(tree, p)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, p), dst)
        shutil.copy2(os.path.join(ROOT, "manifest.txt"), os.path.join(tree, "manifest.txt"))
        added = []
        if extra_skill:
            rel = f"cwf/skills/{extra_skill}/SKILL.md"
            os.makedirs(os.path.join(tree, os.path.dirname(rel)))
            with open(os.path.join(tree, rel), "w") as fh:
                fh.write(f"---\nname: {extra_skill}\ndescription: dropped later\n---\n")
            added.append(rel)
        if extra_agent:
            rel = f"cwf/agents/{extra_agent}"
            with open(os.path.join(tree, rel), "w") as fh:
                fh.write('name = "dropped-later"\n')
            added.append(rel)
        with open(os.path.join(tree, "manifest.txt"), "a") as fh:
            fh.write("".join(r + "\n" for r in added))
        return tree

    def test_update_prunes_what_the_new_manifest_dropped(self):
        """C0.9 (review finding 7): the install dir is replaced whole, so the old ownership
        records must be read first. A skill and an agent the previous install placed, and
        the new one no longer ships, are removed; a user's own cwf-* skill is not."""
        tree = self.make_tree("cwf-dropped", "dropped-agent.toml")
        old = dict(self.env, CWF_REPO_URL="file://" + tree)
        self.assertEqual(self.run_install("--user", env=old).returncode, 0)
        skill = os.path.join(self.home, ".agents", "skills", "cwf-dropped")
        agent = os.path.join(self.codex, "agents", "dropped-agent.toml")
        self.assertTrue(os.path.isfile(os.path.join(skill, "SKILL.md")))
        self.assertTrue(os.path.isfile(agent))
        mine = os.path.join(self.home, ".agents", "skills", "cwf-mine")
        os.makedirs(mine)
        r = self.run_install("--user")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(skill), "a dropped skill was orphaned")
        self.assertFalse(os.path.exists(agent), "a dropped agent was orphaned")
        self.assertTrue(os.path.isdir(mine), "an update removed a skill it never placed")
        inst = os.path.join(self.codex, "codex-workforce")
        with open(os.path.join(inst, "installed-skills.txt")) as fh:
            self.assertNotIn("cwf-dropped", fh.read().split())
        with open(os.path.join(inst, "installed-agents.txt")) as fh:
            self.assertNotIn("dropped-agent.toml", fh.read().split())
        self.assertFalse(os.path.exists(inst + ".cwf-new"))

    def test_same_named_foreign_agent_is_preserved(self):
        """C0.9: a user's own agent file with a shipped name is never overwritten, never
        recorded as ours, and so never deleted by update or uninstall."""
        os.makedirs(os.path.join(self.codex, "agents"))
        foreign = os.path.join(self.codex, "agents", "content-classifier.toml")
        with open(foreign, "w") as fh:
            fh.write('name = "my-own-classifier"\n')
        r = self.run_install("--user")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("kept your own", r.stdout)
        with open(foreign) as fh:
            self.assertEqual(fh.read(), 'name = "my-own-classifier"\n')
        listed = os.path.join(self.codex, "codex-workforce", "installed-agents.txt")
        with open(listed) as fh:
            names = fh.read().split()
        self.assertNotIn("content-classifier.toml", names)
        self.assertIn("doctrine-auditor.toml", names)
        self.assertEqual(self.run_install("--user").returncode, 0)
        with open(foreign) as fh:
            self.assertEqual(fh.read(), 'name = "my-own-classifier"\n')
        self.assertEqual(self.run_install("--user", "--uninstall").returncode, 0)
        self.assertTrue(os.path.isfile(foreign), "uninstall deleted a foreign same-named agent")
        self.assertFalse(os.path.exists(os.path.join(self.codex, "agents", "doctrine-auditor.toml")))

    def test_an_agent_we_placed_is_updated_in_place(self):
        """The foreign-agent guard must not freeze our own registrations on update."""
        self.assertEqual(self.run_install("--user").returncode, 0)
        ours = os.path.join(self.codex, "agents", "content-classifier.toml")
        with open(ours, "a") as fh:
            fh.write("# stale\n")
        self.assertEqual(self.run_install("--user").returncode, 0)
        with open(ours) as fh, open(os.path.join(ROOT, "cwf", "agents",
                                                 "content-classifier.toml")) as src:
            self.assertEqual(fh.read(), src.read())

    def test_install_reports_hook_trust(self):
        """C0.8: a fresh install's hooks are untrusted, and the installer says to trust them."""
        r = self.run_install("--user")
        self.assertIn("open /hooks and trust", r.stdout)

    def test_installed_timezone_skill_is_reachable_and_runs(self):
        """C0.7: the skill's documented resolver finds the installed script, and it runs."""
        self.assertEqual(self.run_install("--user").returncode, 0)
        with open(os.path.join(self.home, ".agents", "skills", "cwf-timezone", "SKILL.md")) as fh:
            line = [l for l in fh.read().splitlines() if l.startswith('TZB="')][0]
        r = subprocess.run(["bash", "-c", line + '; "$TZB" set Asia/Tokyo'],
                           capture_output=True, text=True, env=self.env, cwd=self.home, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.codex, "config.toml")) as fh:
            self.assertIn('TZ = "Asia/Tokyo"', fh.read())

    def test_project_scope_outside_git_fails_cleanly(self):
        outside = os.path.join(self.tmp, "nogit")
        os.makedirs(outside)
        r = self.run_install("--project", cwd=outside)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("inside a git repository", r.stderr)


class ModelCatalogTests(unittest.TestCase):
    """cwf-model-catalog must expose the shipped models without hijacking the user's config.

    The two failure modes this guards are both real: `model_catalog_json` REPLACES the
    catalog, so a wrong path silently hides every model the user had; and writing
    `model_provider` into the main config would reroute their whole Codex install.
    """

    TOOL = os.path.join(ROOT, "cwf", "bin", "cwf-model-catalog")
    SHIPPED = os.path.join(ROOT, "cwf", "model-catalog.json")

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cwf-catalog-")
        self.conf = os.path.join(self.tmp, ".codex")
        os.makedirs(self.conf)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tool(self, command, *extra):
        return subprocess.run([sys.executable, self.TOOL, command, "--config", self.conf, *extra],
                              capture_output=True, text=True)

    def write_config(self, text):
        with open(os.path.join(self.conf, "config.toml"), "w") as fh:
            fh.write(text)

    def test_shipped_catalog_has_only_modalities_codex_accepts(self):
        with open(self.SHIPPED) as fh:
            models = json.load(fh)["models"]
        self.assertGreaterEqual(len(models), 10)
        allowed = {"text", "image", "audio"}
        for m in models:
            self.assertTrue(set(m["input_modalities"]) <= allowed, m["id"])
            self.assertIn("context_window", m)

    def test_install_leaves_a_non_openrouter_config_alone(self):
        original = 'model = "gpt-6.1-sol"\napproval_policy = "on-request"\n'
        self.write_config(original)
        r = self.run_tool("install")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.conf, "config.toml")) as fh:
            text = fh.read()
        self.assertTrue(text.startswith(original), "the user's own settings must not move")
        self.assertNotIn("model_catalog_json", text,
                         "a non-OpenRouter user must not get their catalog replaced")
        self.assertIn("[model_providers.openrouter]", text)
        self.assertTrue(os.path.isfile(os.path.join(self.conf, "openrouter.config.toml")))
        self.assertTrue(os.path.isfile(os.path.join(self.conf, "cwf-model-catalog.json")))

    def test_install_points_an_openrouter_user_at_the_merged_catalog(self):
        self.write_config('model = "z-ai/glm-5.3"\nmodel_provider = "openrouter"\n')
        r = self.run_tool("install")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.conf, "config.toml")) as fh:
            text = fh.read()
        self.assertIn("model_catalog_json", text)
        self.assertIn("cwf-model-catalog.json", text)

    def test_install_merges_rather_than_replacing_a_user_catalog(self):
        existing = os.path.join(self.conf, "mine.json")
        with open(existing, "w") as fh:
            json.dump({"models": [{"id": "user/private-model", "model": "user/private-model",
                                   "slug": "user/private-model", "displayName": "Mine",
                                   "context_window": 1000,
                                   "input_modalities": ["text"]}]}, fh)
        self.write_config(f'model = "user/private-model"\nmodel_provider = "openrouter"\n'
                          f'model_catalog_json = "{existing}"\n')
        r = self.run_tool("install")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.conf, "cwf-model-catalog.json")) as fh:
            ids = {m["id"] for m in json.load(fh)["models"]}
        self.assertIn("user/private-model", ids, "the user's own model must survive the merge")
        self.assertIn("google/gemini-4-carbon", ids)

    def test_verify_fails_when_nothing_installed(self):
        r = self.run_tool("verify")
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL", r.stdout)

    def test_verify_passes_after_install(self):
        self.write_config('model_provider = "openrouter"\n')
        self.assertEqual(self.run_tool("install").returncode, 0)
        r = self.run_tool("verify")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_rerun_does_not_churn_backups(self):
        self.write_config('model = "gpt-6.1-sol"\n')
        self.run_tool("install")
        first = sorted(glob.glob(os.path.join(self.conf, "*.bak-*")))
        self.run_tool("install")
        second = sorted(glob.glob(os.path.join(self.conf, "*.bak-*")))
        self.assertEqual(len(first), len(second), "a no-op reinstall must not add backups")


class ModelDefaultTests(unittest.TestCase):
    """`default` is the only command that changes what sessions run on.

    It must be explicit (never triggered by install), refuse a model that is not shippable,
    set the provider alongside the model, and be idempotent.
    """

    TOOL = os.path.join(ROOT, "cwf", "bin", "cwf-model-catalog")

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cwf-default-")
        self.conf = os.path.join(self.tmp, ".codex")
        os.makedirs(self.conf)
        with open(os.path.join(self.conf, "config.toml"), "w") as fh:
            fh.write('model = "gpt-6.1-sol"\nmodel_provider = "openai"\n')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tool(self, *args):
        return subprocess.run([sys.executable, self.TOOL, *args, "--config", self.conf],
                              capture_output=True, text=True)

    def config(self):
        with open(os.path.join(self.conf, "config.toml")) as fh:
            return fh.read()

    def test_install_never_changes_the_default(self):
        before = self.config()
        self.assertEqual(self.run_tool("install").returncode, 0)
        self.assertIn('model = "gpt-6.1-sol"', self.config())
        self.assertIn('model_provider = "openai"', self.config())
        self.assertNotEqual(before, self.config(), "install should still add the provider block")

    def test_default_requires_a_provider_block(self):
        r = self.run_tool("default", "z-ai/glm-5.3")
        self.assertEqual(r.returncode, 2)
        self.assertIn("install", r.stderr)

    def test_default_refuses_a_model_that_is_not_shipped(self):
        self.run_tool("install")
        r = self.run_tool("default", "not/a-real-model")
        self.assertEqual(r.returncode, 2)
        self.assertIn("not one of the shipped models", r.stderr)

    def test_default_sets_model_and_provider_together(self):
        self.run_tool("install")
        r = self.run_tool("default", "z-ai/glm-5.3")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('model = "z-ai/glm-5.3"', self.config())
        self.assertIn('model_provider = "openrouter"', self.config())

    def test_default_is_idempotent_and_backed_up(self):
        self.run_tool("install")
        self.run_tool("default", "z-ai/glm-5.3")
        first = sorted(glob.glob(os.path.join(self.conf, "config.toml.bak-*")))
        r = self.run_tool("default", "z-ai/glm-5.3")
        self.assertEqual(r.returncode, 0)
        self.assertIn("nothing changed", r.stdout)
        self.assertEqual(len(first), len(glob.glob(os.path.join(self.conf, "config.toml.bak-*"))))

    def test_dry_run_writes_nothing(self):
        self.run_tool("install")
        before = self.config()
        r = self.run_tool("default", "z-ai/glm-5.3", "--dry-run")
        self.assertEqual(r.returncode, 0)
        self.assertIn("would set", r.stdout)
        self.assertEqual(before, self.config())

    def test_a_retired_model_is_dropped_from_the_merged_catalog(self):
        # Seed a catalog carrying a model the package has retired.
        retired = "x-ai/grok-4.6"
        with open(os.path.join(self.conf, "cwf-model-catalog.json"), "w") as fh:
            json.dump({"models": [{"id": retired, "model": retired, "slug": retired,
                                   "displayName": "Grok", "context_window": 1,
                                   "input_modalities": ["text"]}]}, fh)
        self.run_tool("install")
        with open(os.path.join(self.conf, "cwf-model-catalog.json")) as fh:
            ids = {m["id"] for m in json.load(fh)["models"]}
        self.assertNotIn(retired, ids, "a retired model must not stay selectable")
        self.assertIn("z-ai/glm-5.3", ids)


class SyncTests(unittest.TestCase):
    """cwf-sync mirrors the local tree into the user-root install, and must never be reckless.

    Three guarantees matter: it plans unless told to execute, it never CREATES an install that
    was not already there (that is `install`'s job), and it refuses to replace a skills or
    agents directory that holds none of its own files.
    """

    TOOL = os.path.join(ROOT, "cwf", "bin", "cwf-sync")

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cwf-sync-")
        self.codex = os.path.join(self.tmp, "codex")
        self.skills = os.path.join(self.tmp, "skills")
        self.env = dict(os.environ, CODEX_HOME=self.codex, CWF_SKILLS_ROOT=self.skills)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tool(self, *args):
        return subprocess.run([sys.executable, self.TOOL, *args], capture_output=True,
                              text=True, env=self.env, cwd=ROOT)

    def test_no_install_is_never_created(self):
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 2)
        self.assertIn("never creates", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.codex, "codex-workforce")))

    def test_check_reports_drift_and_plans_without_writing(self):
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        with open(os.path.join(self.skills, "cwf-blueprint", "SKILL.md"), "w") as fh:
            fh.write("stale\n")
        r = self.run_tool("--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("DRIFT", r.stdout)
        with open(os.path.join(self.skills, "cwf-blueprint", "SKILL.md")) as fh:
            self.assertEqual(fh.read(), "stale\n", "a plan must not write")

    def test_execute_refreshes_and_then_reports_in_sync(self):
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        with open(os.path.join(self.skills, "cwf-blueprint", "SKILL.md"), "w") as fh:
            fh.write("stale\n")
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("refreshed", r.stdout)
        # The skills root is now in sync. The PACKAGE tree is deliberately absent in this
        # fixture, and sync never creates one, so it keeps reporting those rows as absent
        # rather than as drift; a second --execute over the skills root must not rewrite.
        self.assertIn("not installed on this machine", r.stdout)

    def record(self, *paths):
        """Seed the ownership record, as a previous run of cwf-sync would have."""
        os.makedirs(os.path.join(self.codex, "codex-workforce"), exist_ok=True)
        with open(os.path.join(self.codex, "codex-workforce", ".cwf-sync-ownership"), "w") as fh:
            fh.write("\n".join(paths) + "\n")

    def test_execute_prunes_a_skill_it_recorded_placing(self):
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        gone = os.path.join(self.skills, "cwf-removed-long-ago", "SKILL.md")
        os.makedirs(os.path.dirname(gone))
        with open(gone, "w") as fh:
            fh.write("gone\n")
        self.record(gone)
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pruned", r.stdout)
        self.assertFalse(os.path.exists(gone))

    def test_package_metadata_survives_the_prune_it_just_wrote(self):
        """manifest.txt and CHANGELOG.md are not manifest rows, so the prune used to eat them.

        Found live 2026-11-13: `--execute` wrote manifest.txt, recorded it, then pruned it in
        the same run because no manifest row names it.
        """
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        pkg = os.path.join(self.codex, "codex-workforce")
        self.record(os.path.join(pkg, "manifest.txt"))
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        for name in ("manifest.txt", "CHANGELOG.md", "VERSION"):
            self.assertTrue(os.path.isfile(os.path.join(pkg, name)), name)

    def test_the_ownership_record_is_never_pruned(self):
        """A record listing its own path must survive, or every later run reads "first run".

        cw-dev, 2026-11-13: the record sits in the package dir, which the prune walks. If it is
        pruned, the next run sees no record, treats it as a first run, and prunes nothing
        forever. Before the fix the prune printed `pruned .../.cwf-sync-ownership`.
        """
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        pkg = os.path.join(self.codex, "codex-workforce")
        record = os.path.join(pkg, ".cwf-sync-ownership")
        self.record(record)                     # the record names itself
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("pruned " + record, r.stdout)
        self.assertTrue(os.path.isfile(record), "the ownership record must survive its own run")

    def test_an_empty_user_directory_under_the_skills_root_survives(self):
        """Empty-dir cleanup must touch only dirs this run pruned (cw-dev, 2026-11-13).

        The earlier version rmdir'd every empty directory under the skills root, so a user's
        just-made `~/.agents/skills/<anything>/` disappeared.
        """
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        mine = os.path.join(self.skills, "my-own-empty-dir")
        os.makedirs(mine)
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isdir(mine), "a user's empty directory must survive")

    def test_a_pruned_skills_directory_is_cleaned_up(self):
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        gone = os.path.join(self.skills, "cwf-gone", "SKILL.md")
        os.makedirs(os.path.dirname(gone))
        with open(gone, "w") as fh:
            fh.write("gone\n")
        self.record(gone)
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.isdir(os.path.dirname(gone)),
                         "a directory emptied by the prune should go")

    def test_a_foreign_cwf_skill_is_reported_never_deleted(self):
        """A user's own cwf-notes must survive: prune by ownership, not by name."""
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "cwf-blueprint"))
        mine = os.path.join(self.skills, "cwf-notes", "SKILL.md")
        os.makedirs(os.path.dirname(mine))
        with open(mine, "w") as fh:
            fh.write("my own skill\n")
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("not ours, left alone", r.stdout)
        self.assertTrue(os.path.isfile(mine), "a foreign cwf-* skill must never be deleted")

    def test_a_foreign_skills_root_is_refused(self):
        os.makedirs(os.path.join(self.codex, "agents"))
        os.makedirs(os.path.join(self.skills, "someone-elses-skill"))
        os.makedirs(os.path.join(self.codex, "codex-workforce"))
        r = self.run_tool("--execute")
        self.assertEqual(r.returncode, 2)
        self.assertIn("REFUSING", r.stdout)


if __name__ == "__main__":
    unittest.main()
