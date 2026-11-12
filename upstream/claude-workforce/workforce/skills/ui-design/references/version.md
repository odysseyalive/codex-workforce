<!-- ui-design-ref-version: 2 -->
<!-- origin: workforce | modifiable: true -->
# ui-design reference version

This file is the **drift anchor** for the ui catalog, mirroring the code, text and security
catalogs. An audit reads the integer below (workforce's *shipped* ui-reference version) and
compares it to the version recorded in a project's `ui-design` skill. Shipped > recorded → the
project's references are stale → the refresh updates the workforce-owned (`modifiable: true`)
reference blocks, preserving any `origin: user` seams.

```
ui-design-ref-version: 2
```

**v2** (2026-10-08) — the direction half. Two files join the corpus: `direction.md`, the procedure for
`/ui-design direct`, which reads the project's CSS stack, asks at most four case questions in one
`AskUserQuestion` call, classifies each screen by the job it does, searches the stack's own template and
block sources before any gallery, presents candidates for the user to pick, and writes the project's
design record at `.claude/design/direction.md`; and `ergonomics-catalog.md`, 46 cited rules keyed to
eight situations (LAND, FORM, TRIAGE, JOB, DASH, COMPARE, READ, SET) with a classification section and
an append-only growth region. `design-quality-catalog.md` gains `BF-02` in its growth region — a
UI-shipping surface has a design record and the render matches it — and its title broadens from
marketing and landing pages to rendered interfaces, no existing row reworded.

*Why the direction half and not more review rules: the review half can only speak after the build,
when the remedy it can ask for is a reskin. SLOP-02 caught the generic page and BF-01 had no durable
brief to read, because the brief was whatever the work order happened to say. v2 gives BF-01 and BF-02
a file to grade against and gives the builder references chosen for the case at hand — which is where
the user placed the whole of the uniqueness: "it's about asking the right questions to pull in specific
direction for the case at hand", not comparing one project to another.*

**v1** (2026-09-10) — the built catalog: `design-quality-catalog.md`, ~55 cited rules with stable IDs
(VH/COL/TYP/IMG/CTA/A11Y/SLOP/CRIT/MSG/BF) each carrying a severity, a Basis tag and a fetched source,
plus the hard-fail RED FLAGS gate and the Source Ledger; and `rendered-checks.md`, the
declared-vs-rendered enumeration and the reflow category (RC-01..RC-06) the rule catalog does not cover.

*This replaced a single seed spec, `ui-design-seed.md`, on the day the evaluators began shipping as
skills. The seed stated the same concerns in prose and carried NO rule IDs, so nothing an evaluator
reported could be keyed to a citable rule and nothing a project overrode could be named in a
supersession register. The catalog here is the one real projects were already grading against; what
changed is that it ships, resolvable from the install, instead of being copied into a project once and
tracked by nothing.*

*Why this file exists at all: a catalog with no anchor cannot be reported stale, and two of the nine
text-catalog copies measured on 2026-09-10 carried no anchor — a state that renders as "unknown"
rather than as a version, which is precisely the drift nobody can act on.*
<!-- /origin -->
