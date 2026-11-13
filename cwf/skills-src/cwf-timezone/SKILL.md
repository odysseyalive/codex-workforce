---
name: cwf-timezone
description: Set the time zone every command Codex runs sees, so `date`, logs and timestamps follow the user's zone instead of the server's (a remote server on UTC is the usual cause). Use when the user asks to change, pick, set, fix or clear their time zone, or says the times shown are wrong. Writes one key, shell_environment_policy.set.TZ, into the user's own Codex config.toml.
---

<!-- Authored in cwf/skills-src/cwf-timezone. Ported from upstream skills/timezone, whose settings.json mechanism Codex does not read (measured 2026-11-13). -->

# Time zone

Codex passes `[shell_environment_policy.set]` from `config.toml` into the environment of every
command it runs. Setting `TZ` there moves those commands to the user's zone, in every project.
The upstream Claude skill wrote `env.TZ` into `settings.json`. Codex ignores that file: with it
in place, a command still saw no `TZ` (measured on codex-cli 0.169.0, 2026-11-13). This skill
picks the zone, writes that one key, and reads it back.

**What it does not move:** Codex's own interface clock. That follows the `TZ` of the shell
that started Codex. If the user also wants that changed, tell them to export `TZ` in their shell
profile. Do not claim this skill does it.

Resolve the script first, in every shell call. The user-scope copy comes first because Codex
resolves skills user-scope first:

```bash
TZB="$HOME/.agents/skills/cwf-timezone/bin/cwf-timezone"; [ -x "$TZB" ] || TZB="$(git rev-parse --show-toplevel 2>/dev/null)/.agents/skills/cwf-timezone/bin/cwf-timezone"
```

## Steps

1. **Show.** Run `"$TZB" --root "${CWF_PROJECT_DIR:-$PWD}" show --json`. It returns the current
   setting, this machine's zone, and up to four `candidates`, each with its local time `now`.
2. **Ask once**, as one plain-text question: *Which time zone should commands Codex runs use?*
   Give one option per candidate, in the order given, marked `(current)` or `(recommended)`.
   Say that any zone name works, like `America/New_York` or `Europe/Berlin`, and that **none**
   removes the setting. If the user already named a zone, skip the question.
3. **Apply.** For a zone, run `"$TZB" set <zone>`. For **none**, run `"$TZB" clear`. An unknown
   name is refused with exit 2. Ask again.
4. **Report the receipt.** Quote the `verified on disk` line and the `now` line the script
   printed, not a summary of them. Then say that commands follow the new zone from the next
   Codex start. If `overridden_by` is not empty, say that the project's own
   `.codex/config.toml` still wins there.

## When the write is refused

If the sandbox refuses the write to `~/.codex/config.toml`, give the user the exact command to
run themselves, built from `set_command` or `clear_command`, with the REPL `!` prefix:

```
! <set_command> America/New_York
```

## What it changes

It changes exactly one line in `${CODEX_HOME:-~/.codex}/config.toml`:
`TZ = "<zone>"` under `[shell_environment_policy.set]`. Every other byte of the file is kept.
If `set` had to create the table, `clear` removes it again, which returns the file to how it was
before `set`. A file that defines that table inline is refused, and the line to add by hand is
printed.
