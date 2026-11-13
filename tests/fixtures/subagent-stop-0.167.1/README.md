# SubagentStop fixture, measured live

The populated `SubagentStop` payload Codex 0.167.1 sent on 2026-11-11 (FINDINGS F05), with
its parent and child rollouts. Source: `.codex-workforce/scratch/final-codex-subagent-hooks/`.

Trimmed for size only: `session_meta`, `world_state`, `turn_context`, token rows and
`thread_settings_applied` events are dropped, and the injected skills/AGENTS.md text is cut
to its first line. Every row the adapter reads is kept as recorded. In `payload.json`,
`transcript_path` and `agent_transcript_path` are relative to this directory and `cwd` is
filled in by the test.
