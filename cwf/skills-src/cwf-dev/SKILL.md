---
name: cwf-dev
description: Maintainer mode for codex-workforce itself - the port's source distribution, the only escape from the self-exclusion rule. INVOKE ONLY WHEN THE USER NAMES IT - never infer it from a maintenance-shaped task, because on this host the description is the only thing read before selection. When named, it covers changing cwf/, scripts/, tests/, install or the blueprint, fixing a defect in this package, and syncing an upstream claude-workforce change.
---

# cwf-dev — maintainer mode for the Codex port

> **Invoke only when the user names it.** Upstream makes `dev` user-typed only, and this host
> makes that rule load-bearing: Codex can pick a skill by its description, so a skill that
> volunteers itself is the path the self-exclusion rule exists to close. If a task merely
> *looks* like package maintenance, say so and ask — do not open this skill on your own.

This is the Codex port of claude-workforce's `workforce dev` mode. Upstream's rule is that
`workforce` never audits, converts, hires from, or retires **itself**, because it is
infrastructure and not an employee — converting the dispatcher into an agent creates a
dispatch loop. `dev` is the only escape, and it is **user-typed only**: never synthesize the
`dev` prefix and never pass one through from a routed ask.

The same rule holds here. `cwf-workforce` and `cwf-org` are infrastructure. This skill is the
maintenance hatch, not an employee.

## When this applies

You are in maintainer mode when the repository you are editing **is** the source
distribution: `VERSION`, `manifest.txt`, `cwf/` and `scripts/build-skills` sit at the git
root. That is this repository. A project that installed the package into
`.codex/codex-workforce/` is a **runtime** copy, not the source.

## 1. Read these before changing anything

| Read | Why |
|---|---|
| `AGENTS.md` | The project's own rules, the layout, and what ships |
| `.codex-workforce/plans/codex-conversion-completion.md` | The living tracker: what is done, what is next, gate decisions |
| `upstream/claude-workforce/UPSTREAM.md` | The pinned commit every generated file is reproducible from |
| `scripts/build-skills` | The generator; edit it, never the files it writes |

**Edit the source first, then mirror.** This port's equivalent of upstream's `bin/sync` is
`scripts/build-skills` plus `install`. `build-skills` regenerates `cwf/skills/` and
`cwf/agents/` from the pinned upstream tree and this repository's own sources. Hand-editing a
generated file is destroyed on the next build — the generator is the file that matters.

## 2. Source layout: visible sources, hidden install targets

**Origin: user, 2026-11-13.** "make note how the files are arranged in the cw-dev project. We
want to do the same here so that installed files aren't tucked inside hidden directories or
files." Measured against claude-workforce, then confirmed with cw-dev on 2026-11-13.

The rule: **a dot-directory is an install target, never a source.** Nothing this package ships
is committed under `.agents/`, `.codex/` or any other hidden path. Mirror claude-workforce's
split:

| | claude-workforce | this port |
|---|---|---|
| Skill sources | `workforce/skills/<name>/` (visible) | `cwf/skills/<name>/` (visible, generated) |
| Skill source for one authored here | — | `cwf/skills-src/cwf-dev/` |
| Agent sources | `workforce/agents/<role>/AGENT.md` | `cwf/agents/<name>.toml`, `cwf/agents/cwf-implementer.md` |
| Scripts | `workforce/bin/wf-*` | `cwf/bin/wf-*` |
| Install manifest | `manifest.txt`, path-prefix header | `manifest.txt`, same shape |
| Installed skills | claude-workforce's own user skills root | `~/.agents/skills/cwf-*/` |
| Installed agents | claude-workforce's own user agents dir | `~/.codex/agents/` |

**The manifest carries the mapping.** Its header states the prefix rule, exactly as upstream's
line 73 does (its header names the host destination and says the source path is the
remainder after a fixed prefix).
Two prefixes cover everything today:

    cwf/skills/<name>/...   -> <skills-root>/<name>/...
    cwf/agents/<name>.toml  -> <config-root>/agents/<name>.toml
    anything else           -> the install directory

**Add a per-row flag only when a row leaves its prefix rule** or needs behaviour a path cannot
express — `keep` (never overwrite a user-edited file), `exec` (chmod +x), `retired` (prune
only), `sibling`, `agent`. Upstream has 37 flagged rows out of 198; this port needs none yet,
and a new prefix is a reason to add the flag rather than to infer a destination from a path.
Do not copy upstream's stale claims that `bin/check` enforces the flag set — that script was
retired, and cw-dev fixed the leftover claims upstream in `fc00afa` (2026-11-13). Mirror those
comments from `fc00afa` or later, or leave them out; several now say plainly that nothing
enforces the rule.

**What stays hidden, and why:** `.codex/hooks.json` is this repository's own live hook config,
like upstream's gitignored install tree. `.codex-workforce/` is runtime state. Neither is shipped
source. A generated copy that is committed for review lives in a visible tree
(`cwf/skills/`), matching upstream's committed `workforce/changes/`.

## 3. Where a change belongs

Upstream's rule, ported: **change behaviour in `cwf/`, never in `upstream/`.** The vendored
upstream tree is checksum-pinned and `tests/` fails if it drifts.

| You are changing | Edit |
|---|---|
| How a Codex hook or the adapter behaves | `cwf/lib/cwf_codex.py`, `cwf/bin/cwf-hook` |
| A shipped skill's content | `upstream/` (a claude-workforce change, re-synced) — or `cwf/skills-src/` for one authored here |
| A generated agent | the pinned `AGENT.md`, or `cwf/agents/cwf-implementer.md` for the one authored here |
| The model set, catalog, or a lane | `cwf/model-catalog.json` (generated), `scripts/build-skills` `LANES`/`AGENT_LANES`, `cwf/bin/cwf-model-catalog` |
| Install or uninstall behaviour | `install`, `install.ps1`, `manifest.txt` |
| What a session is told to do | `AGENTS.md` (and the dispatch line in `cwf_codex.dispatch_context`) |
| The plan itself | `.codex-workforce/plans/codex-conversion-completion.md` |

## 4. The release transaction

Every change to a manifest file bumps `VERSION` and adds a `CHANGELOG.md` entry — that rule is
enforced by `tests/test_install.py`. The order that keeps the tree consistent:

1. Make the change in the source of truth.
2. Regenerate: `scripts/build-skills`.
3. Test: `python3 -m unittest discover -s tests -v`. **Cite the run, not the memory of it.**
4. **Refresh the user-root install, which is the copy sessions actually resolve.** Run
   `python3 cwf/bin/cwf-sync --check` to see drift, then `--execute` to mirror. This is the
   port of `bin/sync --personal`, and it matters here for the same measured reason: `install`
   fetches from `$CWF_REPO_URL` (default raw.githubusercontent.com/main), so with unpushed
   changes it silently installs the PUBLISHED version instead of yours. `cwf-sync` reads the
   local tree, plans by default, never creates an install that was not already there, and
   removes a `cwf-*` skill the source no longer has.
   Use `CWF_REPO_URL=file://$PWD ./install` only when you want the whole install transaction
   (hooks, model catalog, agent registration) re-run.
5. Prove the live path when the change is behavioural — spawn the agent, run the hook, read
   the file. A passing unit test is not evidence the installed copy changed.
6. `git diff --check`, then commit only the package paths listed in `AGENTS.md`.

## 5. Upstream inbox first

Read the queue of defects real projects measured in this port before starting work:
`.codex-workforce/audit/UPSTREAM-QUEUE.md`. An open row is a waiting project. A row that has
stayed open across several audits is the strongest defect signal this distribution produces.

The mirror of upstream's `wf-upstream --list`. Close a row only when the fix is in and its
reproduction is re-run here.

## 6. Work with cw-dev, not around it

`claude-workforce` is the reference implementation this project clones. When a mechanism is
unclear — how dispatch works, how a skill is supposed to behave, why a rule exists — ask the
peer session rather than guessing. The measured precedent for this repository is in
`.codex-workforce/audit/` (the gap review and the findings file), and the queue records what
upstream already fixed upstream.

    agent-say --why "<reason>" --from codex-dev cw-dev "<question>"

Ask about the **concept and the rule**, not "tell me what to write": the point is to mirror
the structure and features, adapted to what Codex can actually do.

## 7. What this port must not claim

Codex is not Claude Code. Three limits recur, and every one of them must be stated rather than
implied:

- **No per-agent tool allowlist.** A custom agent cannot restrict tools or honour
  `disallowedTools:`. Grants are prose and detection only.
- **A custom agent cannot set `model_provider`.** A pinned OpenRouter id resolves only when
  the session already routes there.
- **No built-in router.** Dispatch is a line the prompt hook injects and the session chooses
  to follow. Advisory, never a gate.

## 8. Self-exclusion — and exactly how far the escape reaches

Upstream's rule (`workforce/SKILL.md:171`): `workforce` never audits, converts, hires from, or
retires itself, because converting the dispatcher into an agent creates a dispatch loop.
`dev` is the only escape. **`dev` widens inclusion, not disposition.** Under maintainer mode
the package **is** surveyed, counted, and given a disposition row — but that row is `RETAIN`
with the reason *"dispatcher, conversion creates a dispatch loop"*, and dev still never
converts, hires from, retires, reduces, or sweeps it. The scope follows the reason for the
rule: typing `dev` does not make the dispatch-loop reason go away
(upstream `procedures/audit.md:85-94`).

**This skill runs only when the user names it.** `dev` is user-typed only: never synthesize
it, never pass it through from a routed ask. A dispatched ask carrying a dev request stops
with *"Dev mode is reserved for manual invocation."*

The rule is prose on both hosts — upstream's `workforce` skill can also be picked by its
description, and it carries the rule in its body (`SKILL.md:172-174`). What differs is **where
the prose has to sit**. Upstream guards the *argument*: the skill body loads after selection
and says never to synthesize the `dev` prefix. Here the skill *is* dev mode, so nothing
remains to guard after selection, and the rule has to be in this description — the text read
before selection. That is why it is stated twice above. If a non-dev ask merely looks like
package maintenance, say so and ask rather than opening this skill.

So: the package is never an employee, `cwf-org` never dispatches to it, and the work happens
here in the main loop, on the user's explicit instruction.

## Verify before you report

- `scripts/build-skills` exits 0 and prints its count line.
- `python3 -m unittest discover -s tests -v` passes — quote the real count.
- `git diff --check` is clean.
- The tracker's Status block says which item this was and what the next one is.
