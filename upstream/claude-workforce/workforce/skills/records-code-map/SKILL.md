---
name: records-code-map
description: The code map for this project — where a file's sections and definitions are by line number, which files and lines mention a topic, and which checks, fixtures and cases cover a file. Use before searching or reading code to find something, before changing a file, and when deciding which test to run after an edit. The map is generated from the files on every call and never stored.
lane: coding
allowed-tools: Bash, Read
strictness: standard
---

# Records — Code Map

Holds one dataset: **the map of this project's own code**, produced by `wf-map` and
addressed by file, by topic, or by what covers a file.

**It is generated on every call and never stored.** That is the dataset's defining
property, not an optimisation. A hand-kept index drifts from the code in silence: the
`lab` workspace carried a roster of about 30 subprojects in which 12 no longer existed on
disk and 10 that did exist were missing, and nothing reported it for months. Regenerating
costs one pass over the text — measured at 0.08 s on a 19,841-line file — so there is
nothing a stored copy would buy.

## Schema

Three views, each a stream of text rows on stdout. No file on disk, in any of them.

| View | Command | One row is |
|---|---|---|
| outline | `wf-map <file> [<file>…]` | `<line:int>  <kind>  <name>  <first doc or comment line>`, where `kind` is `§` (section), `def`, `class` or `fn`. Preceded by a header: path, language (`python` \| `shell` \| `markdown` \| `generic`), line count, def count, section count |
| topic | `wf-map --topic <words…>` | a per-file block: `<path>  ·  <hits:int> hit(s) · <words matched:int>/<words asked:int>`, then up to 3 `<line:int>  <text>` rows. Ranked by words matched, then hits, then path |
| coverage | `wf-map --tests <file>` | three groups — the coverage COMMANDS present in this tree (`$ <command>    # <what it answers>`, for the caller to run; nothing is executed), the conformance cases naming the file read out of `expectations.json`, and the handbook rows `<handbook>:<line>  Check\|Regression\|Negative: <command>` |

Options: `--root DIR` (default `$CLAUDE_PROJECT_DIR`, else the working directory),
`--limit N` (outline rows, default 200; files shown per topic, max 12).

Exit codes: `0` mapped · `2` nothing readable, or the target resolved outside the root.

## Invariants

> **Degraded state may cause more work. It may never authorize a write.**

A map that is empty, truncated or refused sends its reader back to reading files. It
never licenses an edit to a file nobody located, and it is never cited as evidence that
something does not exist — `wf-map --topic` reporting nothing is a search that found
nothing, which is the state `## Degradation` answers.

| Invariant | Class |
|---|---|
| No row is ever written to disk — the map exists only on stdout | `mechanical` |
| Every target resolves inside `--root`; a symlink leaving the tree is refused by name, before it is opened | `mechanical` |
| Nothing in the mapped tree is executed, imported or loaded — not the file being mapped, and not a suite living there. A docstring match is not identity, so coverage commands are printed rather than run | `mechanical` |
| Every vcs call overrides `core.fsmonitor` and `core.hooksPath` on the command line, because repository-local config can name an executable | `mechanical` |
| At most 4 MiB is read per file, and a truncated outline says `TRUNCATED` in its header | `mechanical` |
| `--tests` reuses the project's own selectors and keeps no coverage list of its own | `mechanical` |
| A line number is the line in the file as it is on disk right now | `contextual` — true only of an unedited file; re-run after an edit |
| An outline names what a file declares, never what it means | `advisory` |

## Degradation

| State | Behaviour |
|---|---|
| **absent** | the normal state. Nothing is stored, so every call starts here and generates the map |
| **empty** | a file with no sections and no definitions prints its header with zero counts; a topic with no match says `nothing matched`. `wf-map` exits `2` when it mapped no file at all, because an empty map and a map of an empty file read alike on stdout |
| **stale** | impossible to carry between calls, and that is the point. Within one call the map is as fresh as the file; after your own edit, re-run it |
| **corrupt** | a binary or unreadable file is reported `not readable as text` and skipped; a path escaping the root is refused with its name and exit `2`. Neither is repaired, and neither is reported as a map |

## Owner

`engineering-coder` — the employee that changes this repository's code is the one whose
procedure reads this map. Its Lead is the second key.

The skill is the mechanism; the org chart is the policy. Nothing here prevents another
employee from calling `wf-map`, and nothing needs to: the dataset is read-only by
construction, since there is no stored copy for a second writer to race.

## Git policy

**Nothing to ignore, in any project.** The map is never written, so no ignore rule exists
or is needed; there is no path to name in `.gitignore`.

The script that produces it is tracked in the distribution at `workforce/bin/wf-map` and
declared `exec` in `manifest.txt`. In an installed project it lands at
`<skills-root>/workforce/bin/wf-map`.

## Seed

An empty instance is the only instance:

```
(no file; the map is produced on each call)
```

## Maintainers

| Script | Implements | Load-bearing | Negative test |
|---|---|---|---|
| `workforce/bin/wf-map` | the three views above, the root containment rule, the read cap, and the refusal to execute anything in the mapped tree | yes — an employee with no map searches by hand, which is the 21-42% of tool calls this exists to remove | `map-escape-symlink`: a symlink out of the tree is handed to it → exits 2, names the path, reads nothing. Run 2026-10-12 |
| `bin/script-conformance --list` (maintainer-only) | answers which fixtures a change to a file can reach, transitively | no — its absence costs the transitive fixture list, not correctness | `map-tests-handbook-check`: a project with neither suite falls through to handbook `Check:` lines rather than reporting no coverage. Run 2026-10-12 |

A maintainer reports; it never repairs. `wf-map` writes nothing anywhere, which is the
strongest form of that rule available to a script.

## How it is reached

An employee calls it from `Bash`, by path:

```bash
WF="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/workforce"; [ -d "$WF" ] || WF="${CLAUDE_PROJECT_DIR}/.claude/skills/workforce"
"$WF/bin/wf-map" --topic session id            # which files and lines mention it
"$WF/bin/wf-map" src/widget.py                 # that file's sections and defs
"$WF/bin/wf-map" --tests src/widget.py         # what covers it, and the command to run
```

In this distribution's own repository the script is at `workforce/bin/wf-map`.
