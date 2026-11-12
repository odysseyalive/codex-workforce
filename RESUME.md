# Resume: Codex-only workforce after the Crush cut

Status: COMPLETE handoff, 2026-11-12. The 0.1.2 package passed its live-Codex smoke test;
delete or replace this file when the release commit is made.
This file is tracked. The trusted `cwf-hook prompt` injects it on the first main-session prompt;
it is not injected into subagents or Stop-feedback continuations.

## Where the project stands

- Repo: `/home/francis/lab/codex-workforce`
- HEAD: run `git log -1 --oneline`; this file deliberately does not repeat its own commit hash.
- VERSION: `0.1.2`
- Tests: `python3 -m unittest discover -s tests -v` — 46 tests, OK.
- Supported host: **Codex only**. Crush compatibility was cut by the user on 2026-11-11.
- Upstream pin: `52cdfe7e4d61d4b82d5d6cbd7c673f684eec3a86`. The full `workforce/skills/`
  tree and the `workforce/agents/` handbooks are copied, so all generated artifacts are
  reproducible. The pin also covers the later YAML fix and the work-list fix.

## What changed in the Codex-only port

- Widen's PERF store and handoff lookup are patched to `.codex-workforce/`; a regression
  test exercises both consumers, not only the constants.
- `web_fetch`, `wait_agent`, `close_agent` and `write_stdin` map to known counters. The
  adapter's tool table is tested against every measured Codex tool.
- A null transcript (`codex exec --ephemeral`) and a disabled/missing juror now say
  "not judged" instead of silently passing.
- The injected `AskUserQuestion` and `shutdown_request` wording is replaced at module load
  with a Codex plain-text question rule and `close_agent` close-out.
- All eight upstream skills ship as `cwf-*` copies with `$cwf-<name>` invocation, Codex
  paths, and the same generated-file checksum in `manifest.txt`. Nine custom-agent TOMLs are
  generated under `cwf/agents/` with host limits stated explicitly. The three scripts those
  skills call (`wf-code-eval`, `wf-map`, `wf-census`) are generated into `cwf/bin/` so the
  documented commands resolve after install.

## Live smoke test: passed 2026-11-12

- Installed the package into an isolated git project with the local `install --project`
  path, then spawned `code-design-advisor` as a real custom-agent type. The child returned
  `CUSTOM_AGENT_LIVE_7Q`; the parent waited, closed it, and returned `PARENT_SAW_LIVE_CUSTOM`.
  The agent transcript carries the generated handbook text, so the TOML was loaded by type.
- Loaded `cwf-records-code-map` by its `$cwf-` name and got `SKILL_OK
  cwf-records-code-map Records — Code Map`.
- Ran a flagged Stop. Widen sampled the work turn, the read-only juror returned a real `ok`
  with a transcript citation, and direct `cwf_juror.judge` on the same payload returned the
  same verdict through the installed copy. The hook had previously dropped an `ok` verdict
  unless it carried notes; that silent pass is now fixed and pinned by
  `test_real_juror_ok_is_visible_not_a_silent_pass`.
- The skill-script smoke test now starts `wf-code-eval` and `wf-map` from the package and
  confirms both use Codex state paths.

## Verification before commit

- `python3 -m unittest discover -s tests -v`: 46 tests, OK, after the generated-skill script
  copies and the visible-verdict fix.
- `git diff --check`: clean.
- `scripts/build-skills`: 8 skills + 9 custom-agent TOMLs + 3 skill scripts generated and
  validated.

## What was verified

- `python3 -m unittest discover -s tests -v`: 46 tests, OK. The suite covers prompt tagging,
  Stop block + continuation, normal and null subagent stops, cap-hit PERF, web-only research,
  generated metadata, generated skill scripts, install/update/uninstall, and upstream
  checksum pinning.
- `scripts/build-skills`: 8 skills + 9 custom-agent TOMLs generated and validated with
  PyYAML and `tomllib`. The TOMLs omit Claude model pins and state the lost tool
  enforcement in every instruction body.
- Both installers place the nine TOMLs in `.codex/agents/`; personal and project install
  tests pass. Uninstall removes only recorded agents and refuses traversal. The generated
  `wf-text-scan` and `wf-timezone` entry points both start and print usage.
- Widen's PERF producer, handoff lookup, web-only `web_fetch` evidence path and null
  transcript state all have regression coverage.

## Shared artifact

Codex Compatibility Discovery

https://claude.ai/artifact/K5mSbWWdcmEzBKstaxLDap

Current page is version 5, built from the Codex-only findings file. It has 17 finding cards,
F01–F10 and F19–F25, and zero case-insensitive "crush" matches. Versions 1–4 remain in its
history and mention Crush; the user chose to keep that history.

## Local artifacts to read first

- `.codex-workforce/audit/FINDINGS.md` — the **shared, Codex-only** report. 17 findings.
  This is the file cw-dev renders. Do not add Crush to it.
- `.codex-workforce/audit/CRUSH-EVIDENCE.md` — the preserved full 26-finding discovery,
  including Crush. Local evidence only; never publish or link it as current product scope.
- `.codex-workforce/audit/CW-DEV-EVALUATION.md` — the independent review of
  `claude-workforce` at `6985840`, with exact probes and command logs.
- `.codex-workforce/scratch/cw-eval-logs/` — raw command logs for that review.
- The project issue ledger:
  `.codex-workforce/issues/01a1cb6e-0d33-79f3-8622-2fb90ea8ef50.json`.

## cw-dev project review — confirmed findings

The review covered `claude-workforce` at HEAD `69858402403400973539ea590738946b90f216e6`.
The checkout stayed clean; probes ran in detached worktrees under `.codex-workforce/scratch/`.

The latest cw-dev YAML fix is sound: it quotes the code-evaluator description, preserves the
value, and all 18 unique shipped frontmatter files parse. But the project’s own checks do not
prevent recurrence:

1. **High — `wf-conform` reports malformed frontmatter as valid.** `frontmatter()` at
   `workforce/bin/wf-conform:727-736` only splits `key: value` lines. A governed agent with
   `description: malformed: this is invalid YAML` raises a real YAML `ScannerError`, while
   `wf-conform` exits 0 with `24 checks · 0 failed`. It also does not scan `SKILL.md`
   frontmatter.
2. **High — `bin/baseline` has the same false-clean.** `bin/baseline:586-592` only checks the
   `---` delimiters. A malformed `SKILL.md` is counted as one skill and `quarantined` stays `[]`.
3. **Medium — the version rule is not enforced.** `workforce/references/version.md:18` says
   shipped changes advance `WORKFORCE-VERSION`; `6985840` changed a shipped file while the
   version stayed `1.88.0`. `core.hooksPath` points at a missing `githooks/` directory, and
   `bin/pre-commit-version:29` omits `sibling`, `exec-sibling`, and `agent` from its flags.
4. **Medium — live docs name the retired `bin/check`.** `workforce/references/version.md:11`
   and `:59-60` claim `bin/check` enforces the version mirror; it does not exist at HEAD.
   Changing the mirror to `9.99.0` still exits 0 with zero failures.
5. **Low — stale references to retired `bin/check`/`bin/prove` remain** in shipped docs and
   code comments. `invariants.md` correctly records the retirement.

The project’s own gates pass: `bin/conformance` 85/85, `bin/idempotence` 14/14,
`bin/script-conformance` 792/792. Those gates simply don’t exercise invalid frontmatter.

## Next actions, in order

1. Commit the 0.1.2 package.
2. Delete or replace this file before the next session; its work is done.

## External state and cautions

- cw-dev is a tmux peer. Use `agent-say --why "<reason>" --from codex-dev cw-dev "<message>"`.
  A message can queue behind an active pane; do not assume delivery from a nonzero/timed-out
  command. Read the mailbox to confirm.
- The old artifact versions still contain Crush. That is the user’s accepted history, not a
  pending defect.
- Do not edit `/home/francis/lab/claude-workforce` without treating it as its own repository
  and following its rules. The `codex-workforce` rule that upstream is read-only still applies
  to `upstream/claude-workforce/`.
- `claude-workforce` is 16 commits ahead of `origin/main` and not pushed. Cite the SHA, not
  “latest main”.
- The `codex-workforce` codex hook suite has no network/model calls. The separate
  `claude-workforce` conformance suites are local-only.
- There was an unrelated `bin/script-conformance` process running under
  `/home/francis/lab/claude-workforce` late in the session. Do not kill it; it belongs to
  cw-dev’s work, not this session.

## Session close-out

No subagent is still running. The review agent was closed after its report was read. The
0.1.2 package is ready to commit; the local audit artifacts are under `.codex-workforce/`
and are intentionally git-ignored.
