# Resume: codex-workforce, 0.1.12

Status: handoff written 2026-11-13 at the 0.1.12 release commit. Replace it when the next
session's work is merged. This file is tracked; the trusted `cwf-hook prompt` injects it on the
first main-session prompt, and not into subagents or Stop-feedback continuations.

## Where the project stands

- Repo: `/home/francis/lab/codex-workforce`
- HEAD: run `git log -1 --oneline`. The 0.1.12 release commit is `44cd158`, one ahead of
  `origin/main` and **not pushed**.
- VERSION: `0.1.12`; tests: `python3 -m unittest discover -s tests -v` -> **77 OK**.
- Supported host: **Codex only**. Crush was cut on 2026-11-11.
- Upstream pin: `52cdfe7e4d61d4b82d5d6cbd7c673f684eec3a86`. Do not edit `upstream/`;
  `tests/` fails on drift.

## What this session added (0.1.3 - 0.1.12)

- **Model lanes.** Every generated agent pins a model and effort from its lane
  (`scripts/build-skills` `LANES`/`AGENT_LANES`). `cwf/model-catalog.json` (18 models) and
  `cwf/bin/cwf-model-catalog` put them in any Codex config as a merged catalog plus an
  `openrouter` profile. `cwf-model-catalog default MODEL` is the only command that changes what
  sessions run on. The API key is never written; the provider names `OPENROUTER_API_KEY`.
- **The live install** runs on `z-ai/glm-5.3` by default, with `--profile openrouter` available.
  `codex debug models` lists the set.
- **Routing.** `cwf_codex.dispatch_context()` feeds `cwf-hook prompt`, which injects the
  dispatch line on every main-session prompt: a no-org project sends a job to a background
  plain subagent, code goes to `cwf-implementer`, reviews to `deadcode-gardener`, pre-write
  decisions to `code-design-advisor`. Advisory, never a gate.
- **`cwf-implementer`** is the package's only code-writing agent, authored here because the
  pinned upstream set is nine advisors.
- **`cwf-dev`** ports `workforce dev`: self-exclusion, edit-source-first, upstream inbox,
  release transaction, the three standing Codex losses. User-typed only.
- **`cwf/bin/cwf-sync`** ports `bin/sync --personal`: mirrors the local tree into the user-root
  install (which shadows a project copy), because `./install` fetches from GitHub and would
  install the published version. Plans by default; `--execute` writes; `--check` exits 1 on
  drift.
- **Layout.** Shipped sources live in `cwf/skills/` (visible), not `.agents/skills/` (hidden).
  A dot-directory is an install target only; `manifest.txt` states the prefix mapping.

## Read before working

1. `AGENTS.md` — the package rules, routing table, layout.
2. `.codex-workforce/plans/codex-conversion-completion.md` — the living tracker. Start with
   **Status**, then the three **Standing rules**, then Stage 6 for the model research.
3. `cwf/skills-src/cwf-dev/SKILL.md` — maintainer mode. Invoke it only when the user names it.

## Next open items

- `C0.1` — the Codex capability matrix (Stage 0; unchanged from the last session).
- `M11` — repin the two code agents from `claude-opus-5.5` to `z-ai/glm-5.3` (value evidence in
  Stage 6; needs the user's call).
- `M12` — whether the six everyday agents move from `gemini-4-carbon` to `gpt-6.1-terra`.
- `M9` — the writing A/B, which needs the user's own briefs.
- Stage 0's `C0.4`-`C0.9` P0 fixes from the independent review are still open.

## Working with cw-dev

`claude-workforce` is the reference implementation. Ask it about the rule and the concept, and
for the file and line — not for an implementation:

    agent-say --why "<reason>" --from codex-dev cw-dev "<question>"

Delivery is not proven by an exit code; confirm with `agent-say read`. Four exchanges are
recorded in the tracker's standing rule, including three corrections that changed the code:
no `/org` exists before an audit; prune by ownership, never by name; and empty-directory
cleanup must touch only what that run pruned.

## Cautions

- `./install` with no `CWF_REPO_URL` fetches `main` from GitHub, which is behind this tree; it
  refuses a downgrade. Use `CWF_REPO_URL=file://$PWD ./install` for the full transaction, or
  `python3 cwf/bin/cwf-sync --execute` for the user-root refresh.
- Re-trust the hooks in `/hooks` after any `.codex/hooks.json` change.
- `.codex-workforce/` is git-ignored runtime state. The tracker lives there on purpose.
- `x-ai/grok-4.6` is retired: Codex sends a `custom` apply_patch tool xAI rejects with 422.
