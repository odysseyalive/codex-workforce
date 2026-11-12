# Changelog

The version lives in `VERSION`. Bump it in the same change that alters anything listed in
`manifest.txt`, and add an entry here.

## Unreleased (2026-11-11)

- Crush compatibility was cut by the user. Codex is the only supported host; the Crush
  discovery remains evidence, not a product target. Crush probe files stay ignored so they
  cannot be committed by accident.

## 0.1.0 (2026-11-11)

- Sensory layer from claude-workforce (commit 6967338) running as Codex hooks: ask tagging
  on UserPromptSubmit and SubagentStart; turn ledger, widen and a read-only juror on Stop
  and SubagentStop.
- `cwf-blueprint` skill generated from claude-workforce's blueprint.
- Installers for Linux/macOS (`install`) and Windows (`install.ps1`), personal or project scope.
- Hardening before release: the state directory refuses symlinks and `..` components, so
  prompts and transcripts can't be redirected outside `.codex-workforce/`; uninstall only
  removes plain `cwf-*` skill folders directly inside the skills directory.
