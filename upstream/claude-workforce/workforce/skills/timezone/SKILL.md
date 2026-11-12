---
name: timezone
description: Set the time zone Claude Code shows times in — the "done 7:55 PM" at the end of a turn, and the clock every command Claude runs sees. Use when the user asks to change, pick, set, fix or clear their time zone, or says the times shown are wrong (a remote server on UTC is the usual cause). Writes one key, env.TZ, into the user's own settings file.
lane: coding
allowed-tools: Bash, AskUserQuestion
strictness: standard
---

# Time zone

Claude Code prints the time a turn finished in its own process's time zone. On a server whose clock
is UTC, that is UTC. Setting `env.TZ` in the user's settings file moves it to the user's zone
(`platform.md` § Fact 27). This skill picks the zone, writes that one key, and reads it back.

Resolve the script first, in every Bash call:

```bash
TZB="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/timezone/bin/wf-timezone"; [ -x "$TZB" ] || TZB="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/skills/timezone/bin/wf-timezone"
```

## Steps

1. **Show.** Run `"$TZB" --root "${CLAUDE_PROJECT_DIR:-$PWD}" show --json`. It returns the current
   setting, this machine's zone, a guess from the user's own commit times, and up to four
   `candidates`, each with its local time `now`.
2. **Ask once.** One `AskUserQuestion` call, one question:
   - header `Time zone`; question: *Which time zone should Claude Code show times in?*
   - one option per candidate, in the order given. Label: the zone, plus ` (current)` when
     `current` is true or ` (recommended)` when `recommended` is true. Description: `Now <now>` and
     the candidate's `note`.
   - say in the question that the blank field takes any zone name, like `America/New_York` or
     `Europe/Berlin`, and that **none** removes the setting.

   If the user already named a zone in their message, skip the question and use it.
3. **Apply.** A zone: `"$TZB" set <zone>`. **none**: `"$TZB" clear`. An unknown name is refused
   with exit 2 and a plain message; ask again with the same question.
4. **Report the receipt.** Quote the `verified on disk` line and the `now` line the script
   printed, not a summary of them. Then say: Claude Code's own "done" time uses the new zone after
   Claude Code is restarted, and commands Claude runs use it straight away. If `show` listed an
   `overridden_by` entry, say that project's own settings still win there.

## When the write is refused

Claude Code may refuse an agent's write to a user settings file. Then give the user the exact
command to run themselves, built from `set_command` (or `clear_command`) in the `show --json`
output, with the REPL `!` prefix, on one line:

```
! /home/you/.claude/skills/timezone/bin/wf-timezone set America/New_York
```

Never hand over JSON to paste. The script writes the same key, keeps every other byte of the
file, and records what it wrote in `<config>/workforce/.settings-owned.json`.

## What it changes

One key in `${CLAUDE_CONFIG_DIR:-~/.claude}/settings.json`, so it reaches every project on the
machine. `TZ` also reaches every command Claude runs, so `date` and anything else reading local
time follows it. `clear` removes the key and gives the file back exactly as it was before `set`.
