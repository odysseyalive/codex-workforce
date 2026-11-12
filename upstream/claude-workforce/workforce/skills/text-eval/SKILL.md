---
name: text-eval
description: Evaluate written prose for AI-generation tells and register drift — mechanical character and punctuation defects, clustered judgment-class signals, citation integrity, and conversational register. Use after writing or editing any prose a person will read, when asked to check whether text reads as AI-generated, or before publishing copy. Grades against a cited catalog with clustering thresholds and hard rows that fire on first occurrence. Report-only.
creative_scrub_ref_version: 2
allowed-tools: Read, Glob, Grep, Bash, Task
minimum-effort-level: high
strictness: standard
---

# Text Evaluator

Reviews prose for the signatures of generated text. **Clustering is the default and hard rows
are the exception**: no judgment-class signal blocks alone, while a mechanical
character/punctuation defect or a factual-integrity failure is actionable at first occurrence
and is never demoted by a register, density or human-presence gate.

**Run it as a Task agent.** An evaluation performed in the session that wrote the text grades
its own work, which is the one configuration the measurement says returns a passing grade
(SKILL.md § Directives, 2026-09-09). Context isolation is the point, not a nicety.

## Interface

| Row | Contract |
|---|---|
| `Invoke` | `/text-eval [<path or passage>]`, or as a Task agent with `context: none` |
| `Returns` | The scan's output from step 1, the passage's point restated in one plain sentence, then the claim inventory, then flags keyed to catalog rows (plus step 2's `Restate the point`), each `{row, severity, evidence, fix}`. MUST FIX is reported with no cap; SHOULD FIX and CONSIDER are held to 3–5 combined. The scan, the restatement and the inventory are not flags and do not count toward the cap. |
| `Fails` | `bin/wf-text-scan` exits 1 when a scanned row is MUST FIX, 2 on a usage error or an unreadable input, 0 otherwise. The skill's own catalog drift anchor: `grep -l creative-scrub-ref-version references/*.md \| wc -l` prints 2. |

## Workflow

1. **Run the character scan first, every time, before reading a word for meaning.** The
   script does the Tier 1 *Character & punctuation* pass of `text-tells.md`, so it does not
   depend on anyone remembering to grep:

   ```bash
   TS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/text-eval/bin/wf-text-scan"; [ -x "$TS" ] || TS="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/skills/text-eval/bin/wf-text-scan"
   "$TS" --root "${CLAUDE_PROJECT_DIR:-$PWD}" <file>     # a passage with no file: printf '%s\n' "$TEXT" | "$TS" -
   ```

   It prints every em-/en-dash with its line and phrase, the rate per 5,000 words and the
   catalog verdict; rhetorical-colon candidates after the catalog's exclusions; invisible
   Unicode by class; and curly/straight quote seams. It skips frontmatter, fenced code and
   inline code, and it applies the project's house-rule elevations (step 6). **Quote its
   output in the report.** Each **[hard]** row it marks MUST FIX is MUST FIX: no step below
   demotes it, and only a supersession-register row whose scope covers the file can (step 6).
   A colon candidate is evidence, not a finding, until you read it. The scan never rewrites
   the text. If neither path resolves (a project keeping its own copy of this skill), do the
   same Tier 1 pass by hand and say the scanner was absent.

   In the same pass, build the **claim inventory**: every statistic, date, direct quote, named
   study and named case, each marked `sourced` or `unsourced`. It feeds the *Unsourced
   specific* row in `additions.md`.
2. **Restate the point.** Before reading the catalog, write the passage's point in one plain
   sentence, as if explaining it to someone outside the field. If you cannot, report it as
   `Restate the point`, a workflow signal rather than a catalog row: one CONSIDER signal, counted toward the passage's cluster like any
   other. Then take each sentence whose meaning a reader would have to guess, and check it against
   the rows for unclear meaning: Vague pronoun referents, Topic collisions and Orphaned statements.
3. **Read the catalog.** [references/text-tells.md](references/text-tells.md) is the corpus:
   pattern → tell → falsifiable test. [references/additions.md](references/additions.md)
   carries the rows authored by this distribution, including citation integrity and
   conversational register. `text-tells.md` was imported from claude-enforcer's skill-builder
   on 2026-08-03 and has been workforce's own since 2026-11-10 (`references/version.md`). Its
   header still points to a `creative-integrity.md` that exists only in that source project
   and never shipped here. The severity and cluster rules it points to are the ones step 5
   states; read those, not the dead link.
4. **Score the positive signals too**, from
   [references/human-markers.md](references/human-markers.md), BEFORE requiring any change.
   A passage with strong human markers and a few rhetorical devices is human writing. An
   evaluator that can only count tells over-flags prose that is plainly a person thinking,
   and the goal is "sounds like a person," never "contains no listed pattern." This does
   not touch a **[hard]** row: a mechanical defect is not offset by good writing around it.
5. **Count clusters, not signals.** 1 signal in a passage → CONSIDER; 2 → SHOULD FIX; 3+ →
   MUST FIX. Rows marked **[hard]** are outside clustering entirely. Dedupe by mechanism:
   two rows describing one underlying defect count once.
6. **Apply the house rules, if the project has any.** A project may carry
   `.claude/skills/text-eval/CATALOG-ANCHOR.md` with a supersession register and a precedence
   clause. **That register is the sole authority that demotes a finding**, and it is the
   project's, not this catalog's. Absent the file, nothing is demoted. A project TIGHTENS a
   scanned row with a `text-scan:` attribute on one of its own `origin: user` markers in that
   file, which step 1's script reads:
   `<!-- origin: user | added: <date> | text-scan: em-dash=0; rhetorical-colon=hard -->`.
   `em-dash=0` makes every dash MUST FIX (the catalog allows 1 per ~5,000 words), and
   `rhetorical-colon=hard` makes every colon candidate MUST FIX. A house rule written only in
   prose is yours to apply here: it can raise what the scan printed, never lower it.
7. **One pass, then stop.** Present the evaluation once. MUST FIX items are blocking and are
   resolved before the text reaches a reader. The rest is the author's call.

## Probe

Evaluate this passage and return the evaluation: *"Moreover, organizations everywhere are
utilizing these tools to delve into a tapestry of opportunities — truly transformative."* A
correct result names the em-dash as a **[hard]** mechanical flag, plus a MUST FIX cluster
citing connector overuse, hyperbolic scope, Latinate bias, AI vocabulary and superlative
stacking, and reports no cap on the hard row.

## Verification

```
grep -l 'creative-scrub-ref-version' references/*.md | wc -l   # 2: the corpus and its version anchor
printf 'a \342\200\224 b \342\200\224 c\n' | bin/wf-text-scan --root /nonexistent -; echo $?   # 1: the second em-dash is MUST FIX
```
