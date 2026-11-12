# Resume: Codex-only workforce after the Crush cut

Status: ACTIVE handoff, 2026-11-11. Delete or replace this file when the next action is done.
This file is tracked. The trusted `cwf-hook prompt` injects it on the first main-session prompt;
it is not injected into subagents or Stop-feedback continuations.

## Where the project stands

- Repo: `/home/francis/lab/codex-workforce`
- Base commit: `cfa640b` — "Cut Crush compatibility; Codex is the only supported host"
  The resume mechanism is committed after that commit; use `git log -1` for the exact HEAD.
- VERSION: `0.1.1`
- Tests: `python3 -m unittest discover -s tests -v` — 32 tests, OK.
- Supported host: **Codex only**. Crush compatibility was cut by the user on 2026-11-11.
  The Crush probing stays as historical evidence, not a product target.

## What changed in this session

- `cfa640b`: Codex is the only supported host; Crush is historical discovery evidence.
  `CHANGELOG.md` records the cut. `scripts/build-skills` describes a Codex skill generator.
  `.gitignore` and `tests/test_senses.py` ignore/cover `.crushrc` and `crushrc`.
- The follow-up change adds the tracked `RESUME.md` and injects it through the existing trusted
  prompt hook. It does not add a new hook event, so no re-trust is needed for this change.

Decision record: the user chose to **keep the existing shared link** and its versions 1–4,
rather than delete the artifact and republish at a new URL. Version 5 is the current page and
contains zero Crush mentions. Do not reopen the URL question unless the user does.

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

1. **Fix the two false-clean checks in claude-workforce.** Use one real YAML parse helper for
   `AGENT.md` and `SKILL.md` in both `wf-conform` and `bin/baseline`; retain the parse error
   in the quarantine/detail. Add fixtures that must fail on malformed YAML. This is a
   claude-workforce change, not a codex-workforce change.
2. **Restore or replace the version enforcement.** Either make the pre-commit hook
   reachable and include every manifest flag, or remove the claim and give the surviving
   conformance path an actual anchor/mirror check. Add a negative test.
3. **Apply the Codex-only port plan from `FINDINGS.md`:** fix the two `.claude` paths
   (`F01`) and the tool map (`F02`), correct AGENTS.md’s live-hook status, generate all eight
   skills, replace Claude-only injected wording, and surface “not judged” instead of a silent
   pass. None of that is committed yet.
4. Re-run `python3 -m unittest discover -s tests -v` in `codex-workforce` after any package
   change, and the claude-workforce gates after any change there.
5. If the artifact changes, send cw-dev a new markdown source path and ask for the **same
   URL**. Do not use the old Crush-inclusive `CRUSH-EVIDENCE.md` for that.

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
package is committed; the local audit artifacts are under `.codex-workforce/` and are
intentionally git-ignored.
