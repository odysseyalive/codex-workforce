<!-- security-ref-version: 1 -->
<!-- origin: workforce | modifiable: true -->
# Cross-File Detection — taint and policy defects invisible in one file

The security twin of the code catalog's [cross-file-detection](../../code-evaluator/references/cross-file-detection.md). Its
premise carries straight over: the worst defects do not fit in a single diff hunk. A source in one file
and a sink in another is invisible to a reviewer reading either alone, and it is the shape most web
vulnerabilities actually take. This file is the method for the two-file cases; the single-function cases
stay in [security-taxonomy.md](security-taxonomy.md).

## §1 — Run the native taint engine first

Cross-file taint is exactly what a real dataflow engine does and grep cannot. Before any manual tracing,
[native-tool-map.md](native-tool-map.md) §1 applies: `semgrep` in `taint` mode, CodeQL, `brakeman`,
`find-sec-bugs`, and Psalm all follow a source across function and file boundaries. Present → their path
*is* the finding. This file is the fallback method when no engine is installed, and the triage method for
an engine's output.

## §2 — The source→sink trace (fallback, three steps)

1. **Enumerate sources** in the changed files — the request surface: route handler params, `req`/`request`
   objects, `$_GET`/`$_POST`, deserialized bodies, uploaded filenames, header reads, DB reads of
   previously-tainted data (second-order).
2. **Enumerate sinks** — the Group A–I signals present anywhere the change reaches.
3. **Connect them across files.** A tainted value passed to a helper in another module, stored on an
   object and later sunk, or threaded through a queue/event. Follow the *value*, not the file. A path that
   crosses a sanitizer ([guards.md](guards.md) #2/#3) is cut; a path with none is a candidate.

State the path as `source (fileA:line) → … → sink (fileB:line)`. A finding with no stated path is a
single-file signal, not a cross-file finding — do not inflate it.

## §3 — The cross-handler consistency checks (policy, not taint)

These have no single sink to grep — the defect is an **inconsistency across siblings**, which is why they
live here and not in the taxonomy. They are the code catalog's cross-file reasoning applied to authz.

- **Missing authorization guard.** Enumerate route handlers / controller actions. Most carry an auth
  decorator or middleware (`@login_required`, `authorize`, a guard clause). Flag the sibling that does
  **not** — a handler that skips the check its peers all apply is the classic broken-access-control hole
  (CWE-862). This is a *candidate*: the odd handler may be intentionally public. Name it, do not clear it.
- **Inconsistent object-ownership check.** Handlers that load a record by request id: most filter by
  `owner = current_user`, one fetches by id alone. That one is the IDOR (CWE-1220 —
  [security-taxonomy.md](security-taxonomy.md) Group B).
- **CORS/cookie/header policy drift.** One route sets `SameSite`/`HttpOnly`; a sibling forgets. One
  endpoint validates the redirect target; another doesn't. Divergence across peers is the signal.
- **Sanitizer applied unevenly.** Output encoded on nine of ten template branches; the tenth interpolates
  raw. The inconsistency is the finding.

## §4 — Second-order and stored taint

The hardest cross-file case and the one grep never catches: data written to a store while untrusted, read
back later as if trusted, then sunk. Stored XSS and second-order SQLi both take this shape. When a change
either **writes** request data to a store or **reads** from one into a sink, note the other half may live
in a file the diff does not touch — flag it as "second-order: confirm the write side sanitizes," a
candidate a human or a whole-repo taint run resolves.

## §5 — Honesty, unchanged

Everything here is **report-only and candidate-tier** by construction — cross-file reasoning without a
taint engine cannot prove reachability. A cross-file finding names its path or its inconsistent-sibling
set, carries a confidence band, and defers the verdict to a taint tool or a human exactly as
[security-taxonomy.md](security-taxonomy.md) § honesty disciplines require. The design-policy floor holds:
a clean cross-file pass is never reported as "access control verified."

*Landed 2026-08-26. Method mirrors the code catalog's cross-file pass; the authz-consistency checks are
distilled from the `Authorization`, `Authorization_Testing_Automation`, and `Insecure Direct Object
References` sources.*
<!-- /origin -->
