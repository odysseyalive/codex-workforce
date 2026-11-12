---
name: security-evaluator
description: Evaluate a code change for web-security flaws — OWASP Top 10:2025 classes as source-review classes, taint signals from source to sink, and a per-language sink appendix. Use after writing or editing code that handles input, auth, data access, templating, deserialization, or external requests; when asked to security-review a change, check for injection/XSS/SSRF/authz flaws, or evaluate the security of what was just written. Report-only, candidate-tier by construction.
lane: coding
security_ref_version: 1
allowed-tools: Read, Bash, Skill
strictness: standard
---

# Security Evaluator

Reviews a change for the web-security flaw classes an AI coder commonly introduces.
Language-agnostic: the spine is the OWASP Top 10:2025 categories restated as
source-review classes, each with a grep-able **signal**; the per-language sinks are a
surface appendix read only for the ecosystem a change actually touches. Grounded in a
strict safety model — grep proposes candidates, a real analyzer and human review decide.
**All findings are report-only and candidate-tier**; the design-policy classes (access
control, business logic) are flagged for review and never reported green.

## Interface

| Row | Contract |
|---|---|
| `Invoke` | /security-evaluator [review [path] \| sweep] |
| `Returns` | Report-only, candidate-tier findings against the OWASP Top 10:2025 source-review classes, each traced source to sink and tiered. Never edits the change it reviews; access-control and business-logic classes are flagged for review and never reported green. |
| `Fails` | No exit codes declared — the skill ships no script. Its one mechanical check is the catalog drift anchor: a grep -c of the security-ref-version marker across the four reference files must return 4. |

## Commands

| Command | Layer | Action |
|---------|-------|--------|
| `/security-evaluator review [path]` | L2 (post-write) | Review a diff or path just written against the taxonomy; trace source→sink taint; tier findings; report only |
| `/security-evaluator sweep` | L3 (full codebase) | Whole-tree security-class scan, report-only at scale |

## Workflow

### Steps

1. **Candidate set follows the mode.** `review` → the diff. `sweep` → the whole tree,
   report-only.
2. **Read the grounding files below before detecting anything.**
3. **Run the native-tool gate first** (the real analyzer named in `native-tool-map.md`
   for the ecosystem touched — `semgrep` cross-language, per-language taint engines,
   secrets and supply-chain scanners), then the ripgrep signal pipeline; reconcile every
   finding against `references/guards.md`.
4. **Trace taint source → sink** per `references/cross-file-detection.md` — a signal in
   isolation is a candidate; a signal reachable from untrusted input is a finding.
5. **Tier every finding** and display the plan. **Report only** — a security-evaluator
   never edits the change it reviews; the fix is the code owner's, verified by their
   own check.
6. **Never report a design-policy class green.** Access control and business-logic flaws
   are flagged for review; absence of a signal is not proof of their absence.

## Grounding

- [references/cross-file-detection.md](references/cross-file-detection.md) — source→sink taint tracing, cross-handler authz consistency, second-order taint (read first)
- [references/guards.md](references/guards.md) — false-positive clearances (read before flagging anything)
- [references/security-taxonomy.md](references/security-taxonomy.md) — the OWASP Top 10:2025 source-review classes, each with its signal and CWE mapping, plus the per-language sink appendix
- [references/native-tool-map.md](references/native-tool-map.md) — which real analyzer supersedes the grep, per ecosystem

## Verification

- Check: `grep -c 'security-ref-version: 1' references/security-taxonomy.md references/native-tool-map.md references/guards.md references/cross-file-detection.md` — expect 4 (every catalog file carries the matching drift anchor). A change to the catalog bumps `version.md` and every file's anchor together, or a per-file drift check is impossible.
- The catalog grep is the tier-3 self-check any IC runs; tier-4 dispatched review against the full taxonomy is this evaluator's own job.
