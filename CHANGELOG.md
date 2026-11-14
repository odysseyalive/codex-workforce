# Changelog

The version lives in `VERSION`. Bump it in the same change that alters anything listed in
`manifest.txt`, and add an entry here.

## 0.1.15 (2026-11-13)

- **`cwf/bin/cwf-org index`: the org chart** (tracker `C1.2`). It rebuilds
  `.codex-workforce/org-chart.md` from `.codex/agents/*.toml`, and `register --execute` runs it
  after writing, so the chart follows the registrations. The chart carries the `AUTO-GENERATED`
  marker the prompt hook reads (`cwf_codex.dispatch_context` then gives the org dispatch line,
  and `index` checks that it does after the write), a `workforce-version:` stamp read from
  `VERSION`, the prose-only honesty line, the chain of command, a roster, and each employee's
  scope (its `description`). The chain is built only from each agent's ORG-RECORD `reports-to`.
  An agent with no ORG-RECORD is an adopted roster row and is not drawn into the chain. A
  `reports-to` naming nobody, or a loop, is drawn under `ceo` and flagged. Unparseable,
  duplicate, shadowed and symlinked agents get loud rows. Shipped and infrastructure agents are
  left off. A rerun with nothing changed writes nothing (`UNCHANGED`). `index` refuses a chart
  without the marker (hand-written) and any symlink on the chart path. The writer is
  `register`'s temp-file, rename and read-back path, now shared. Not part of this release:
  mechanicals, the `## Skills` block, contract stamps, `org embed`, `org status`.
- Tests: `tests/test_org.py` adds nine chart cases: marker, roster, scopes and chain from a
  real registration, the prompt hook reading the chart as an org, a reports-to loop drawn once
  and flagged, a byte-identical rerun, zero
  employees, shipped agents excluded, quarantined and shadowed rows, a hand-written chart left
  alone, and a symlinked chart refused.

## 0.1.14 (2026-11-13)

- **`cwf/bin/cwf-org register`: a project's employees become Codex custom agents** (tracker
  `C1.1`). Each handbook (markdown with `name`/`description` frontmatter, the shape of upstream's
  `AGENT.md`) is rendered to `<project>/.codex/agents/<name>.toml`. Its body goes into
  `developer_instructions` byte for byte, after a host-limits paragraph, and `tools:` /
  `disallowedTools:` are kept only as instruction text. It plans by default and `--execute`
  writes. A batch is atomic or absent: one refusal writes nothing. It refuses a symlink anywhere
  on the path, an unsafe or infrastructure name (`cwf-workforce`, `cwf-org`, `cwf-dev`), a
  shipped agent's name, an existing agent it did not generate, and **any name a user-scope
  agent already has**. User scope wins on Codex, so that project copy would never load, and the
  user's file is reported and left untouched. Each write goes through a temp file and a rename,
  then is read back and parsed. `cwf-org check` parses every project agent and flags shadowed,
  symlinked or unparseable ones. Chart generation is `C1.2`, not part of this release.
- `cwf/lib/cwf_agents.py` is the one TOML writer for custom agents. `scripts/build-skills` now
  renders the shipped agents with it, and the ten committed TOMLs regenerate byte-identical.
  It escapes backslashes, triple quotes, control characters and astral characters, and it
  refuses any render that does not parse back to the same values.
- `scripts/build-skills` strips trailing whitespace from the scripts it generates. One line in
  upstream `wf-settings-apply` carried it, so a rebuild no longer drifts from the committed copy.
- Tests: `tests/test_org.py` covers the TOML parse, byte-for-byte handbook survival including
  hard escapes, plan-only, idempotent re-run, symlinked `.codex`, `.codex/agents` and target
  file, user-scope same-name by file and by `name` field, atomic batch refusal, unsafe and
  infrastructure names, adopted files, and shipped-agent regeneration.

## 0.1.13 (2026-11-13)

- **Fixed the false-pass paths measured by the independent review.** `wait_agent` and
  `close_agent` no longer count as outside evidence, so polling or closing an agent cannot
  open "hearing" by itself. The upstream tagger's org-chart path is patched to
  `.codex-workforce/org-chart.md`, its duplicate dispatch line is suppressed in favor of the
  adapter's, and a truncated or invalid rollout is reported "not judged" instead of matching.
- Directives now resolve Codex custom-agent handbooks at `.codex/agents/<name>.toml`; cap-hit
  PERF records do the same; widen's work-segment check follows the Codex work root.
- `cwf/bin/wf-settings-apply` is now generated and shipped (manifest row added), retargeted to
  `${CODEX_HOME:-~/.codex}`.
- The turn budget no longer reads a same-named `.claude/agents/<name>.md` `maxTurns`, nor
  Claude's personal agent root, so Claude state cannot cap a Codex agent (path map M4).
- **`RESUME.md` is injected once per session**, on the first main-session prompt, as
  `AGENTS.md` already said. A marker in the session's scratch directory stops repeats.
- **`cwf-timezone` now writes the key Codex reads.** Codex does not read `settings.json`
  (measured: `env.TZ` there left `$TZ` empty in `codex sandbox`). The skill is now authored in
  `cwf/skills-src/cwf-timezone/` and writes `shell_environment_policy.set.TZ` in the user
  `config.toml` with a line-level edit; `set` then `clear` restores the file byte for byte, and
  an inline table is refused with the line to add by hand. `bin/wf-timezone` is replaced by
  `bin/cwf-timezone`. The installer now marks skill scripts executable, so the documented
  resolver finds them. `cwf/bin/wf-settings-apply` stays: `wf-code-eval` imports it.
- **Re-trust notice.** The prompt hook compares each codex-workforce entry in the project and
  user `hooks.json` with its `trusted_hash` (format reproduced from Codex's own rows) and,
  once per session, says which changed and need `/hooks`. `cwf-hook trust-check HOOKS_JSON`
  prints the states and exits 1 when one is stale; `install` uses it for its final line.
- **Install transaction.** `install` and `install.ps1` read the previous ownership records
  before replacing the install directory, so a skill or agent the new manifest dropped is
  pruned instead of orphaned. A same-named agent the installer never placed, and that differs
  from ours, is kept, not recorded, and so never deleted by update or uninstall.
- Tests: regressions for wait/close-only hearing and truncated rollouts through the real hook
  (from `.codex-workforce/audit/probe_close.py` and `probe_trunc.py`), a Claude chart being
  invisible, the turn-budget read, first-prompt resume, a populated live `SubagentStop`
  fixture in `tests/fixtures/subagent-stop-0.167.1/`, hook trust, the timezone round trip, and
  the install prune and foreign-agent cases. `install.ps1` is not exercised (no PowerShell).

## 0.1.12 (2026-11-13)

- **Fixed a second pruning defect in `cwf-sync`, found by a peer read rather than by me.**
  Cleanup after the prune rmdir'd EVERY empty directory under the skills root, so a user's
  just-made `~/.agents/skills/<anything>/` was removed. Verified before the fix: it printed
  `removed empty skill dir: .../my-own-empty-dir`. Cleanup is now limited to directories this
  run actually emptied by pruning a recorded path.
- Two tests: an empty user directory survives `--execute`, and a directory emptied by the
  prune still goes. The first fails when the old sweep is restored.
- cw-dev withdrew an earlier note about the ownership record pruning itself: the loop only
  walks paths from the prior record and the record is never in `written`. The record is kept in
  the explicit metadata set anyway, since it sits inside a root the prune walks and a future
  code path could list it.

## 0.1.11 (2026-11-13)

- **Fixed a live data-loss bug in `cwf-sync` found by running it, not by reasoning about it.**
  `manifest.txt` and `CHANGELOG.md` are not manifest rows — the script copies them as package
  metadata — so the ownership record listed them and the prune in the SAME run removed them.
  Observed on the real install: `pruned /home/francis/.codex/codex-workforce/manifest.txt`.
  The metadata paths are now named as kept explicitly, and a regression test reproduces the
  failure when that line is removed.
- `cwf-sync` also stopped printing its exit code as if it were a file count. `execute()` returns
  a status; the report now prints the number of files the plan found.

## 0.1.10 (2026-11-13)

- **Fixed a real defect in `cwf-sync`: it pruned by name.** It removed any `cwf-*` skill not in
  the manifest, which would delete a user's own hand-made `cwf-notes` or a `cwf-*` from another
  source. claude-workforce's installer forbids exactly this ("a blunt basename match would
  delete a user's own agent that happened to share a name"). Pruning is now by **ownership**: a
  previous run records the exact paths it placed, and only recorded paths the manifest no
  longer lists are removed.
- Four guards carried from that installer, each with its measured reason: the record is read
  before writing and **merged** after (a record destroyed by its own run reads as "nothing is
  ours" forever); a **partial run never prunes**; a recorded agent registration is **kept while
  another skill still bundles that agent** (upstream pruned one on removing `image-eval`,
  50f20ec); and pruning is confined to the roots this run just built, never project state.
- On a first run there is no record, so nothing is pruned and the record is seeded from what
  the manifest placed. A pre-existing `cwf-*` is then **reported, not deleted**.
- The `SyncTests` were rewritten around this: one seeds the record and asserts a recorded skill
  is pruned, and one asserts a foreign `cwf-notes` survives `--execute` and is reported. That
  second test was shown to fail when the old name-match prune is restored.

## 0.1.9 (2026-11-13)

- New `cwf/bin/cwf-sync`: the port of claude-workforce's `bin/sync --personal`. It mirrors this
  repo's local tree into the user-root install — `~/.agents/skills/cwf-*`, `~/.codex/agents/`,
  and `~/.codex/codex-workforce/` — which is the copy a session actually resolves, since the
  user-root skills root shadows a project one.
- It exists because `install` fetches from `$CWF_REPO_URL` (default
  raw.githubusercontent.com/main): with unpushed changes it overwrites the user-root install
  with the PUBLISHED version and looks successful. `cwf-sync` reads the local tree instead.
  Measured upstream 2026-08-04; the same trap applies to a maintainer checkout here.
- It plans by default and needs `--execute`; `--check` exits 1 on drift. It **never creates an
  install that was not already there**, refuses a skills or agents directory holding only
  foreign files, and removes a `cwf-*` skill the source no longer has so a stale copy cannot
  keep loading. Five tests cover those guarantees and were shown to fail when the guards were
  removed.
- `cwf-dev` § The release transaction now refreshes the user-root install with `cwf-sync`
  after regenerating and testing, and says when to use the full `install` transaction instead.

## 0.1.8 (2026-11-13)

- **Layout change: shipped sources are now visible.** The nine skills move from the hidden
  `.agents/skills/` to `cwf/skills/`, matching claude-workforce, whose sources live in a
  visible `workforce/` and whose `git ls-files` contains no shipped file under `.claude/` or
  `.agents/`. A dot-directory is now an install target only. The tree was regenerated and
  confirmed byte-identical (`diff -r`, 36 files) before the old one was removed.
- `manifest.txt` states the destination mapping in its header, as upstream's does: two prefix
  rules (`cwf/skills/<name>/...` -> skills root, `cwf/agents/<name>.toml` -> agents dir,
  everything else -> install dir). No flag column yet, because no row needs one; the header
  says when to add it and warns not to copy upstream's retired `bin/check` claim.
- Both installers map the new prefixes and exclude the skills source from the install
  directory. A clean install into a throwaway HOME put 9 skills in `~/.agents/skills`, did not
  duplicate `cwf/skills` into the install dir, and a live reinstall reports 0.1.7+ with
  `cwf-dev` present.
- `cwf-dev` gains § Source layout with the rule, the two tables, the flag policy, and what
  stays hidden on purpose; the blueprint gains a matching standing rule in the user's words.

## 0.1.7 (2026-11-13)

- New `cwf-dev` skill: the port of claude-workforce's `workforce dev` maintainer mode. It
  carries upstream's self-exclusion rule (the dispatcher is infrastructure, never an
  employee), the edit-source-first discipline, the upstream inbox, the release transaction,
  and the three standing Codex losses (no per-agent tool allowlist, no `model_provider` in a
  custom agent, no built-in router). Authored in `cwf/skills-src/cwf-dev/` and generated into
  `.agents/skills/cwf-dev/`, so it installs with the other eight.
- The blueprint gains a standing rule, **origin: user**, to mirror claude-workforce through
  cw-dev: read the upstream file rather than a summary of it, ask cw-dev about the rule and
  concept and for the file and line, prefer structural parity over local invention, and
  record any deliberate divergence with its reason. It records the two that exist
  (`cwf-implementer`, `cwf-dev` as its own skill) and the exchanges that produced them.
- AGENTS.md and the tracker now say nine skills and ten agents, and say which of each is
  authored here rather than generated from the pin.

## 0.1.6 (2026-11-13)

- The prompt hook now injects a **dispatch line** on every main-session prompt, mirroring
  claude-workforce's `DISPATCH_NO_ORG` / `DISPATCH_LINE` in `wf-task-tag`. It says a job goes
  to a background plain subagent, names `cwf-implementer` for code, `deadcode-gardener` for a
  review and `code-design-advisor` for an approach decision, and keeps the inline exception.
  Advisory, never a gate: nothing refuses. Upstream added the same line after measuring a
  project that did a whole job in the main thread because nothing said otherwise.
- An org is a chart carrying the `AUTO-GENERATED` marker that this package's tooling writes; a
  hand-written chart without it is not one, matching upstream's rule.
- New `cwf-implementer` agent: the package's only code-writing employee. The pinned upstream
  set is nine advisors with no implementer, so this one is authored here
  (`cwf/agents/cwf-implementer.md`) and generated the same way as the rest. It runs on the
  code lane and its handbook requires `changed:` / `ran:` / `not run:` / `risk:`. Verified
  live: spawned by type, it added a function, ran a `python3 -c` assertion, and reported the
  real output, its untracked-file caveat, and a blocked cleanup.
- `AGENTS.md` gains a routing section with the same ladder, and four tests pin the dispatch
  context: no-org names the code lane, a marked chart selects the org line, an unmarked chart
  does not count as an org, and only a main prompt receives it.

## 0.1.5 (2026-11-12)

- `cwf-model-catalog default MODEL` sets the session's default model. It is deliberately
  separate from `install` so a reinstall can never move someone's default. It sets `model`
  and `model_provider` together (an OpenRouter id needs the provider that can reach it),
  refuses an id the package does not ship, is idempotent, and backs the config up first.
- The shipped catalog grows to 18 models, adding the orchestrator candidates:
  `z-ai/glm-5.3` (the recommended default), `qwen/qwen3.8-max-0902`, `anthropic/claude-opus-5`,
  `anthropic/claude-fable-5.1` and `openai/gpt-6-astra`. The default on the author's machine
  is now `z-ai/glm-5.3`, verified by running a session with no `-m` flag.
- `x-ai/grok-4.6` is listed as retired rather than shipped. Codex sends `apply_patch` as a
  Responses tool of type `custom`, and xAI's endpoint rejects the request with 422 before the
  first token; the model answers fine on other endpoints, so this is a gap between the two
  sides. A reinstall now removes a retired id from the merged catalog instead of leaving it
  selectable and broken.
- Seven more tests cover the new command: install never changes the default, default refuses
  an unshipped id and a missing provider block, sets model and provider together, is
  idempotent, honours `--dry-run`, and drops a retired model from the merge.

## 0.1.4 (2026-11-12)

- The recommended OpenRouter models now ship as package content: `cwf/model-catalog.json`
  carries 16 models (each lane's default, premium and value pick) and `cwf/bin/cwf-model-catalog`
  installs them into any Codex config. Both installers run it automatically.
- The models appear with `codex --profile openrouter`. `model_catalog_json` replaces Codex's
  catalog rather than extending it, and `model_provider` reroutes every model, so the
  installer writes a profile instead of changing the user's default provider. It merges with
  any catalog the user already had, backs the file up first, and never writes an API key: the
  provider names `OPENROUTER_API_KEY` and each user exports their own.
- `cwf-model-catalog status` and `verify` report whether the catalog, profile and provider
  block are in place; `verify` exits 1 when a shipped model is missing from the merged file.
- Seven new `ModelCatalogTests` cover the failure modes that matter: a non-OpenRouter config
  being left byte-identical, a user's own catalog entry surviving the merge, and a no-op
  reinstall not churning backups. Verified live: the catalog lists all 16 models, and
  `glm-5.3-flash`, `muse-spark-1.3` and `haiku-5.5` each ran a prompt with no metadata warning.

## 0.1.3 (2026-11-12)

- Every generated custom agent now pins a model and an effort from the lane its handbook
  describes, instead of inheriting the session model. The table lives in
  `scripts/build-skills` (`LANES`, `AGENT_LANES`): everyday work runs
  `google/gemini-4-carbon`, code runs `anthropic/claude-opus-5.5`, the handbook cold-reader
  runs `anthropic/claude-opus-5`, and `meta/muse-wonder` is reserved for the visual lane the
  package does not yet staff. The research and its evidence are in
  `.codex-workforce/plans/codex-conversion-completion.md` § Stage 6.
- A new `ModelLaneTests` class fails the suite when an agent loses its pin, pins a model
  outside the four lane defaults, or (on a machine with a Codex model catalog) carries an
  `input_modalities` value Codex rejects. That last case is a regression: a catalog entry
  with `file` in `input_modalities` made every `codex exec` fail to start on 2026-11-12 until
  it was corrected.
- `cwf/agents/README.md` now states that a custom agent may set `model` but cannot set
  `model_provider`, so an OpenRouter pin resolves only when the parent session routes there.

## 0.1.2 (2026-11-11)

- Codex-only port of the discovery findings: widen's PERF store and handoff lookup now
  use `.codex-workforce/`; the adapter maps `web_fetch`, `wait_agent`, `close_agent` and
  `write_stdin` to known evidence counters; null transcripts are reported as "not judged".
- All eight upstream skills ship as `cwf-` copies with `$cwf-...` invocation, Codex paths,
  plain-text questions and `close_agent` close-out wording. Nine Codex custom-agent TOMLs
  are generated from the pinned handbooks, and both installers place them in `.codex/agents/`
  with the host-limit statement kept in every instruction body. The web-only `web_fetch`
  evidence path and the cap-hit PERF path both have regression coverage; uninstall removes
  only the agents it recorded, and a tampered list cannot escape `.codex/agents/`. The
  upstream pin moves to `52cdfe7` so the generated files are reproducible from the recorded
  commit. The code-evaluator and records-code-map skills now ship their working scripts
  (`wf-code-eval`, `wf-map`, `wf-census`) under `cwf/bin/` with Codex state paths, and a
  real juror `ok` is reported with its reason instead of being a silent pass.

## 0.1.1 (2026-11-11)

- Crush compatibility was cut by the user. Codex is the only supported host; the Crush
  discovery remains evidence, not a product target. Crush probe files stay ignored so they
  cannot be committed by accident.
- `RESUME.md` is a tracked handoff file. The existing trusted prompt hook injects it once on
  the first main-session prompt, and never into subagents or Stop-feedback continuations.

## 0.1.0 (2026-11-11)

- Sensory layer from claude-workforce (commit 6967338) running as Codex hooks: ask tagging
  on UserPromptSubmit and SubagentStart; turn ledger, widen and a read-only juror on Stop
  and SubagentStop.
- `cwf-blueprint` skill generated from claude-workforce's blueprint.
- Installers for Linux/macOS (`install`) and Windows (`install.ps1`), personal or project scope.
- Hardening before release: the state directory refuses symlinks and `..` components, so
  prompts and transcripts can't be redirected outside `.codex-workforce/`; uninstall only
  removes plain `cwf-*` skill folders directly inside the skills directory.
