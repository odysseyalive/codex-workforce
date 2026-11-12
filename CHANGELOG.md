# Changelog

The version lives in `VERSION`. Bump it in the same change that alters anything listed in
`manifest.txt`, and add an entry here.

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
