# Resume: codex-workforce, 0.1.14

Status: handoff written 2026-11-13 after committing release 0.1.14. Replace it when the next
session's work is merged. The trusted `cwf-hook prompt` injects it on the first main-session
prompt, not into subagents or Stop-feedback continuations.

## Where the project stands

- Repo: `/home/francis/lab/codex-workforce`
- HEAD: `3ea3e30` (`0.1.14`), two commits ahead of `origin/main` and **not pushed**.
- Tests: `python3 -m unittest discover -s tests -v` -> **117 OK**.
- Stage: **Stage 1 — local work-management core**. Stage 0 is closed.
- Upstream pin: `52cdfe7e4d61d4b82d5d6cbd7c673f684eec3a86`. Do not edit `upstream/`;
  `tests/` fails on drift.

## What just landed

### 0.1.13 — Stage 0 closed

- Fixed the measured false-pass paths: `wait_agent`/`close_agent` no longer count as outside
  evidence; a Claude org chart is invisible to Codex; each prompt gets one dispatch line; a
  truncated rollout is "not judged"; a same-named Claude handbook cannot cap a Codex agent.
- `RESUME.md` is injected on the first prompt only.
- Repaired `cwf-timezone`: it now writes `shell_environment_policy.set.TZ` in the user's
  `config.toml`, the mechanism Codex actually reads. Measured through `codex sandbox`.
- Added the live `SubagentStop` fixture and a hook-trust hash checker; the installer says
  whether re-trust is needed.
- Install updates now prune dropped skills/agents and preserve a user's own same-named agent.

### 0.1.14 — project agent registration

- `cwf/bin/cwf-org register HANDBOOK.md ... [--execute]` renders handbooks to
  `<project>/.codex/agents/<name>.toml`; `cwf-org check` reports shadowing, symlinks,
  unparseable files, and duplicate names.
- Shared writer `cwf/lib/cwf_agents.py`; `scripts/build-skills` uses it, so shipped and
  project agents use the same TOML escaping.
- Guards: symlinked paths, unsafe names, infrastructure/shipped names, user-scope shadowing,
  adopted files, duplicate project names, malformed/multi-line frontmatter, non-UTF-8 TOML,
  and a project whose `.codex` is the user Codex home.
- Independent `deadcode-gardener` review found five defects; all are fixed with tests.

## Next item: `C1.2` chart generation

The living tracker owns state:

`.codex-workforce/plans/codex-conversion-completion.md`

Start with **Status**, then Stage 1. `C1.2` adds chart generation at
`.codex-workforce/org-chart.md` with roster, scopes, chain of command, and the
`AUTO-GENERATED` marker, wired to the `cwf-org` generator from `C1.1`.

Read before working:

1. `AGENTS.md`
2. `.codex-workforce/plans/codex-conversion-completion.md` — Status and Stage 1
3. `cwf/skills-src/cwf-dev/SKILL.md` — maintainer mode; invoke only when the user names it

## Working rules and cautions

- Change behaviour in `cwf/`, never in `upstream/`.
- Run the tests after every change to `cwf/` or `.codex/hooks.json`.
- Any manifest-listed file change bumps `VERSION` and adds a `CHANGELOG.md` entry.
- Refresh the user-root install with `python3 cwf/bin/cwf-sync --execute`; `--check` must say
  `in sync`.
- Re-trust hooks in `/hooks` after any `.codex/hooks.json` change.
- `./install` fetches published code by default; in this checkout use
  `CWF_REPO_URL=file://$PWD ./install`, or `cwf-sync` for the user-root refresh.
- Stage 1 code changes go to `cwf-implementer`, one-shot, then close the agent.
