<!-- code-additions-version: 3 -->
<!-- origin: workforce | modifiable: true -->
# Code-eval additions — authored by workforce

**This file is NOT vendored.** `references/catalogs/code/` is a read-only import from claude-enforcer
that must stay byte-identical to its origin so a reconcile can still compute a difference
(`evaluators.md` § Seeding). This file is where **workforce's own** code-review entries live, tracked
and shipped, with no obligation to match anything upstream. The text-side twin is
text-eval's [additions.md](../../text-eval/references/additions.md), and the reasoning for the split is stated there once rather than
twice.

**Seeding order is vendored first, then this file appended**, and the anchor written at seeding
records both provenances separately.

Format follows the host catalog: **what** it is, **why** it matters, and the **signal** that detects
it. Detection method belongs in `cross-file-detection.md` and false-positive guards in `guards.md`;
a row here that needs either says so rather than restating them.

---

## Group W1 — Reachability and vacuity

Both entries were **measured in this repository**, not derived from a list. Each names the commit
that found it, because a taxonomy row whose example is hypothetical cannot be checked against
reality later.

| Class | What | Why it matters | Signal |
|-------|------|----------------|--------|
| **Guard keyed on a neighbour's precondition** | A block whose reachability depends on a condition that has nothing to do with its own purpose — typically an `else:` branch it was nested into for convenience | The block dies silently when the unrelated condition flips. Nothing fails, coverage does not drop, and the code reads as live. It stays invisible until the moment it was supposed to fire | For each conditional block, ask what the guard tests and what the body does. If the body never references the guarded subject, the nesting is incidental. Landed 2026-08-06 (`1ae454e`): a `DEVELOPMENT.md` staleness warning sat in the `else:` of `os.path.exists("CLAUDE.md")` and died when that file was deleted |
| **Filter that silently matches nothing** | A predicate — regex, glob, extension test — that selects zero items, inside a loop whose success is reported as "checked" | A pass over an empty set reports the same green as a pass over everything. This is strictly worse than a failing check, which at least announces itself | Count what the filter matched and assert the count is non-zero. Any selection step feeding a verification needs a floor. Found 2026-08-06 (`0575d9b`): `_HDR_RX` matched **0 of 72** files and the check passed having examined nothing; a sibling filter keyed on file extension excluded all 13 extensionless scripts it promised to cover |

**The guard for both.** Neither fires on code that is *conditionally* executed by design. The tell is
a mismatch between what the condition tests and what the body touches, or between what a filter
claims to cover and what it selected. State the count or the subject, never the intent.

**Why these two and nothing else.** The rest of this session's findings were prose or doctrine, and
belong in `text-tells.md` or a procedure. A code taxonomy that grows by analogy stops describing
defects anyone has seen.

---

## Complexity prioritization — a ranking method, not a defect class

**This is NOT a Group W1 row**, and the separation is deliberate. Group W1 catalogs defects
measured in this repository; this is a way to *order* hotspots a pass has already found, ported
from an outside tool rather than seen here. It is kept under its own heading so the closing
discipline above still holds — it must never be read as a taxonomy row grown by analogy, because
it describes no new defect.

**Rank hotspots by concentrated mass.** The code catalog's complexity pass
(`cross-file-detection.md` §5) flags a callable on decision-point density and on length
independently. When several are flagged, rank them by **mass = CC × √SLOC**, worst first. The
√SLOC is deliberate: it compresses size so complexity dominates, so a short branchy function
ranks above a long flat one — and the long flat function is not the failure mode.

As an orientation figure — **never a gate** — the share of total complexity mass held by
callables with CC > 10 (Σ mass(CC>10) / Σ mass(all)) sits near **0.34** in human repositories
and **0.68** in coding-agent checkpoints (SlopCodeBench, arXiv:2603.24755, via the
slopcheck-deslop reference). Use it to orient one tree against a known band and to watch a
project's own trend, never as a threshold that blocks.

**Why it is never a gate.** It is a mass *ratio*, so decomposing one complex function into
several small ones lowers it without removing complexity — it spreads the work AND pads the
denominator. Rank with it; **do not gate on it.**

*Ported 2026-08-25 from slopcheck-deslop (built on SlopCodeBench, arXiv:2603.24755). Only the
language-agnostic complexity-concentration metric is taken; the tool's per-language ast-grep
rules are measured in other repositories and are left there, so this addition stays
language-agnostic and measured-or-cited rather than imported wholesale.*

---

## Resource-awareness — recognising memory & CPU cost from what a variable holds

**Language-agnostic.** This is the pass the over-engineering rubric defers to when it says *"ignore
correctness, style, performance, security — those are other passes"* (`mistake-taxonomy.md`): that
pass did not exist, and this is it. It is a different axis from the complexity pass
(`cross-file-detection.md` §5), which scores *cyclomatic / cognitive* complexity — a **maintainability**
proxy — never *computational* time/space cost. This pass reads the other axis: **what a variable
stores, and when a copy, an allocation, or a retention happens.**

Four unrelated runtimes — C++ (value semantics), Python (names bind objects), PHP (zval / copy-on-write),
JavaScript (reference vs primitive) — collapse onto **one** set of six cost classes. That convergence is
the evidence the classes are real and cross-cutting, not analogy (this file's closing discipline). The
classes and their detection heuristics are agnostic; the language *surface* — the exact syntax and the
idiomatic fix — is an illustrative appendix, never the structure.

### The six resource-cost classes (RC1–RC6)

| Class | What (the reviewer's question) | Why it costs | Agnostic signal |
|-------|--------------------------------|--------------|-----------------|
| **RC1 — Needless copy / value-vs-reference** | Is a large value copied where a read-only view or reference would do? *(what the variable stores)* | Deep copy + allocation per call/assignment | A large value passed, assigned, or returned and only *read* through the copy |
| **RC2 — Materialize-instead-of-stream** | Is the whole collection built when it is consumed once, sequentially? | Whole dataset resident before first use | A full collection built and fed to a single sequential consumer (`sum` / `for` / write) |
| **RC3 — Unbounded retention (lifetime leak)** | Does anything stay reachable past its use? | Memory grows for the process lifetime | A long-lived container that only gains members; a registration (listener / timer / cache key) with no matching release; a cycle; a closure capturing a large value |
| **RC4 — Allocation churn on a hot path** | Is allocation or O(n²) accumulation repeated inside a loop? | Allocator traffic + copy per iteration | `new` / alloc, `+=` string build, merge/concat, or object/closure creation inside a loop with no hoist / reserve |
| **RC5 — Wrong container / representation** | Does the structure match the access pattern? | O(n) where O(1) was available; cache-hostile layout | Linear membership test in a loop; non-contiguous layout scanned hot; boxed elements for bulk numerics |
| **RC6 — Type/shape stability in hot code** | Is a hot object / array / call-site kept type-stable? | Engine/JIT deoptimisation; silent fallback to a slow path | A hot object mutated in shape (late or `delete`d property, inconsistent key order); a call site fed mixed types; an array whose element kind is degraded |

**RC6 is the one bucket whose *specifics* are runtime-bound** (V8 hidden classes / elements-kinds,
CPython 3.11+ specialisation, the PHP 8 JIT, C++ move-elision). The **principle** — keep hot code
type/shape-stable, and know your runtime's deopt cliffs — is agnostic; the cliffs themselves live in the
appendix.

### Three disciplines that keep it honest — a resource catalog without them is noise

1. **Report-only, always.** A resource finding is a *candidate*, never a verdict: reported with its class
   and location, **never auto-applied.** No static reader sees real runtime scale, so — exactly as
   `cross-file-detection.md` treats grep — this pass proposes and defers the verdict to a profiler or a
   human. It is the same status duplication and complexity already carry.
2. **The scale gate.** A signal is reportable **only on a hot path** — a loop, a request / handler, a
   large or unbounded N, or a long-lived process — and the finding must name that path (`file:line` +
   *why* it is hot), **or it is not reported.** Every source in the provenance below states the same rule
   independently: these are defects at scale and noise off it. **The one exception is RC3** — a leak is
   unbounded growth, not a constant factor, so it is reportable regardless of measured scale.
3. **The resource safety floor** (the mirror of the minimalism safety floor above). *Premature or
   ineffective optimisation is itself a defect.* A copy that does not matter, a "stream" over data
   already fully in memory, a reflexively restructured layout, a `const&`-on-an-`int` — flagging one of
   these is a **false positive**, not a finding. Cite-or-drop: a resource finding names its hot path or it
   is dropped.

A deliberately-bounded resource shortcut carries the existing intent marker (`guards.md` #21,
`// code-eval:` naming a ceiling and upgrade path) and is **never re-flagged** — the marker mechanism
already exists and is reused unchanged.

### Guards — agnostic false positives, cleared before reporting

| Guard | The "wrong" pattern is actually fine when… |
|-------|--------------------------------------------|
| **sink-that-stores** | a by-value parameter is a *sink* the callee keeps — store-then-move is correct, not a needless copy (RC1) |
| **already-materialised** | the source is already a full in-memory collection — a generator/stream over it saves nothing (RC2) |
| **small-and-bounded** | N is small and fixed — the conversion / hoist / reserve cost is not repaid (a tiny list beats a set; a few concatenations) |
| **lifetime-matches** | a listener / timer / cache lives exactly as long as the app by design (RC3) |
| **needs-the-value** | the reference or closure genuinely needs the whole value, or identity / mutation-in-place is the real contract |
| **cold-path** | the code is not hot — off a loop / handler / large-N / long-lived path it is at most a note, and not a finding unless a house rule says otherwise |

### Detection — a reading pass; where a tool exists, the tool is the verdict

Resource cost is **semantic**, and the native-tool gate (`cross-file-detection.md` §1) still runs first:
a perf/lint rule that encodes one of these — clang-tidy / clippy perf lints, ESLint, PHPStan /
`phpinspectionsea` performance rules, `ruff` — is the verdict where present, and this pass triages its
output. But most resource review is **review-by-reading** the diff against the six classes, because no
static tool sees *scale*. That is why the whole pass is report-only and scale-gated: it raises
candidates, never confidence-by-grep — the governing thesis the code catalog already states for dead
code, applied to cost.

### Language surface — illustrative examples, not structure

The same six classes as they appear per language: a reference *for the reviewer*, cited from the primary
sources below, **not** the taxonomy. A class fires by its agnostic signal above; this only makes it
concrete, and it extends to any runtime that shares the value/reference + stream + retention + churn +
container axes (Go, Rust, Java, C#, Ruby, Lua).

| Class | C++ | Python | PHP | JavaScript / V8 |
|-------|-----|--------|-----|-----------------|
| RC1 | big type by value → `const&` / `string_view` / `span`; sink-by-value + `std::move` | avoid a needless `list(x)` / `.copy()`; names already alias | `&` reference defeats COW; a write to a shared array separates (deep-copies) it | closure pins captured scope; object args are references |
| RC2 | return-by-value + `reserve`; an out-param blocks RVO | `list(...)` fed only to `sum` / `for` → generator expr; `f.read()` whole file → iterate | `fetchAll()` unbounded → streamed / unbuffered fetch loop; `file()` slurp → `fgets` | whole-payload `res.json()` / `readFileSync` → streams + backpressure |
| RC3 | `shared_ptr` cycle → `weak_ptr` | mutable default arg; module-level growing cache; no `__slots__` at scale | large data in `static` / `global` in a worker; cyclic GC | uncleared `addEventListener` / `setInterval`; growing module `Map`; detached DOM; accidental global |
| RC4 | `push_back` in a loop w/o `reserve`; alloc in a hot loop | `s += x` in a loop (O(n²)); boxed-object churn | `array_merge` / `.=` in a loop (O(n²)); `preg_*` per iteration | `.push` loop; per-iteration literal / closure; `.map().filter().map()` intermediates |
| RC5 | array-of-structs → struct-of-arrays for a hot scan; row-major loop order | `in list` O(n) → `set` / `dict` O(1); `array` / `numpy` / `bytes` for bulk | packed vs hashed array (sequential int keys stay packed) | packed vs holey elements-kind; `TypedArray` for numerics |
| RC6 | move ops absent → silent copy | hoist attribute lookups out of a hot loop | interned strings; ref-count fast path | stable hidden class; avoid `delete` / megamorphic call sites / holey arrays |

*Provenance — cited, not measured in this repository (like the complexity-mass method above, and per this
file's rule that a taxonomy row is measured-or-cited, never grown by analogy). Each of the six classes is
confirmed by four independent primary sources: **C++** — C++ Core Guidelines (F.16/F.18/F.20, R.24/R.37,
Per.18/19), Meyers *Effective Modern C++*, Carruth (CppCon 2014/2016); **Python** — CPython data model &
`gc` / `__slots__` / `functools` docs, Ramalho *Fluent Python*, Szorc, Witowski; **PHP** — Popov (zval /
copy-on-write / hashtable), the php.net GC and query-buffering manual, phpdelusions on generators;
**JavaScript / Node** — the V8 blog (elements-kinds; shapes & inline caches), MDN memory management, Node
"Don't Block the Event Loop" and "Backpressuring in Streams", Osmani. Landed 2026-08-25 by `/workforce
dev`. The convergence across four unrelated memory models is the grounding: a class that recurs in all
four is cross-cutting, which is exactly why the taxonomy is agnostic and the per-language table is only
its surface.*
<!-- /origin -->
