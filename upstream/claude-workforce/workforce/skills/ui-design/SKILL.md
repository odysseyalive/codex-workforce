---
name: ui-design
description: Set a RENDERED interface's design direction before it is built, then evaluate what shipped. `direct` reads the project's CSS stack, asks about the case, researches real references for the job each screen does, hands the pick to the user, and writes the project's design record; `review` and `sweep` grade declared-vs-rendered slots (no missing or placeholder art), applied theme vs framework default, visual hierarchy, typography, colour roles, CTA, WCAG 2.2 AA contrast and focus, reflow at 320 CSS pixels, situation ergonomics, and AI-slop/templated-default tells. Use `direct` before the first UI build on a surface or for a new component pattern; use `review` after a UI-shipping change is written, when asked to design-review a page, or to decide whether a surface looks right to ship. Grades against a cited catalog with stable rule IDs and BLOCKS on hard-fail red flags. `review` and `sweep` are report-only.
lane: coding
ui_design_ref_version: 2
allowed-tools: Read, Bash, Skill, Write, Edit, WebSearch, WebFetch, ToolSearch, AskUserQuestion, ArtifactComments
strictness: standard
---

# UI Design Evaluator

**Two halves.** `direct` runs BEFORE the first UI build on a surface and decides the direction;
`review` and `sweep` run after and grade what shipped. The direction half exists because the
review half can only speak once the page is there, when the remedy it can ask for is a reskin:
nothing gathered references, asked about the case, or picked a direction first, so a builder
designed from model memory and landed on the model's average page.

Reviews a rendered interface for the design failures an automated suite cannot see.
**The interface as RENDERED is ground truth.** A page that builds, passes e2e, and reads
truthfully can still be a failure of presentation — a declared image slot that renders
blank, a palette recorded but never applied, a generic template, text below the contrast
threshold, a body that scrolls sideways at 320 px. **Every `review` and `sweep` finding is
report-only** and keys to a stable rule ID with the severity the catalog states. `direct`
is the one command that writes: it writes the project's design record and nothing else.

**An image's fit is not graded here.** This catalog checks that a declared image slot
renders (no blank or placeholder art). Whether the image in it fulfils the ask where it is
shown is the jury's question (workforce `senses.md` § An image is judged where it is shown).

## Interface

| Row | Contract |
|---|---|
| `Invoke` | /ui-design [direct <surface> \| direct --component <pattern> \| review <target> \| sweep] |
| `Returns` | From `direct`: a design record at `.claude/design/direction.md` carrying the user's answers verbatim, the situation per screen, the chosen references with capture dates, and what is and is not borrowed from each. From `review`/`sweep`: a rule-keyed verdict — `{rule ID, pass/fail, severity, evidence}` per finding — opened by the Required Checks block from `references/rendered-checks.md`. Never edits the surface it reviews. Any BLOCK finding fails the gate. |
| `Fails` | No exit codes declared — the skill ships no script. Its one mechanical check is the catalog drift anchor: every file under `references/` carries `ui-design-ref-version: 2`, and `SKILL.md`'s own `ui_design_ref_version:` matches it. `direct` run by a spawned employee cannot reach `AskUserQuestion`, so it returns `QUESTION:` with the shortlist rather than picking. |

## Commands

| Command | Layer | Action |
|---------|-------|--------|
| `/ui-design direct <surface>` | L1 (pre-write) | Read the project's CSS stack, ask the case questions, classify each screen by situation, research references, present them in a shareable page others can comment on, read those comments, take the user's pick, and write the design record |
| `/ui-design direct --component <pattern>` | L1 (pre-write) | The same loop at component scale for one pattern — data table, upload flow, step bar, kanban — appended to the existing record |
| `/ui-design review <url or route>` | L2 (post-write) | Render the target at real widths and grade it against the catalog; tier findings; report only |
| `/ui-design sweep` | L3 (whole surface) | Every shipped route, report-only at scale |

`direct` is the only command that writes, and `references/direction.md` is its procedure. The
workflow below is `review`'s and `sweep`'s.

## Workflow

0. **Read the project's design record** — `.claude/design/direction.md` — before grading
   anything. It is the brief `BF-01` grades against and the source of the situation keys the
   ergonomics rules are selected by. **A UI-shipping surface with no record is a BF-02 finding,
   not a pass**: the direction step was skipped. Report it, name `/ui-design direct <surface>`
   as the remedy, and grade the rest of the catalog anyway.
1. **Obtain the stated objective** of the surface — what it is for and who it is for. A
   critique analyses whether a design meets *its objectives*; with no agreed objective the
   feedback is baseless. No objective in the order is a `QUESTION`, never an assumed one.
2. **Enumerate declared vs rendered FIRST** (`rendered-checks.md` RC-01), before any
   subjective assessment. You cannot grep for what is not there, so the absent element is
   listed into existence before the catalog can see it.
3. **Render at real widths**, desktop and 320 px, and read the rendered DOM/screenshots —
   never the source spec or the intent (CRIT-03).
4. Judge first impression first (CRIT-02), then walk the catalog category by category:
   VH, COL, TYP, IMG, CTA, A11Y, SLOP, CRIT, MSG, BF — then RC-02..RC-06 for reflow, then
   the `ERG-` rules for the situation the record names for this screen. An app screen graded
   on landing-page rules alone is graded against rules that do not describe it.
5. **Every BLOCK finding needs measured evidence** — a computed contrast ratio, a DOM node,
   a captured region — never an assertion (CRIT-04). Thresholds are not rounded.
6. **Apply the catalog's own severities; invent none.** Any BLOCK finding fails the gate.
7. **Where no rule covers what you found**, the finding stands on its evidence at the
   severity the evidence warrants, up to BLOCK, and the catalog amendment ships in the
   same report. "The catalog does not name it" grows the catalog; it never passes a page.

## Grounding

- [references/design-quality-catalog.md](references/design-quality-catalog.md) — the ~55 cited rules with stable IDs (VH/COL/TYP/IMG/CTA/A11Y/SLOP/CRIT/MSG/BF), each with severity, Basis tag, and fetched source; the hard-fail RED FLAGS gate; the Source Ledger
- [references/rendered-checks.md](references/rendered-checks.md) — what the catalog does not cover: declared-vs-rendered enumeration and the reflow/responsive category (RC-01..RC-06), plus the Required Checks report block
- [references/direction.md](references/direction.md) — `direct`'s procedure: stack detection from the project's own files, the four-question budget in one call, the per-stack reference sources with their free-or-link-only and licence notes, the no-browser fallback, and the design-record template
- [references/ergonomics-catalog.md](references/ergonomics-catalog.md) — 46 cited `ERG-<SITUATION>-NN` rules across eight situations (LAND/FORM/TRIAGE/JOB/DASH/COMPARE/READ/SET), the "Classifying a screen" section both halves key on, and the append-only growth region

## Verification

- Check: `grep -L 'ui-design-ref-version: 2' references/*.md` — expect NO output (every reference file carries the matching drift anchor). `version.md` carries the anchor twice, so a `grep -c` total is not the test; the per-file form is. A change to the catalog bumps every file's anchor together, or a per-file drift check is impossible.
- Check: this file's own frontmatter `ui_design_ref_version:` equals the integer in `references/version.md`. The skill and its corpus drift apart silently otherwise, and `wf-catalog` reads the corpus while an audit reads the skill.
- The catalog grep is the tier-3 self-check any IC producing UI runs; tier-4 dispatched review against the full catalog is this evaluator's own job.
