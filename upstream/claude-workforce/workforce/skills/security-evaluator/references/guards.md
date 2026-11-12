<!-- security-ref-version: 1 -->
<!-- origin: workforce | modifiable: true -->
# Guards — the false positives a security signal must clear before it is reported

A signal grep finds *sinks*. A vulnerability is a sink **reachable by untrusted data and not
neutralized**. The gap between those two is where security tools earn their false-positive reputation, so
every candidate from [security-taxonomy.md](security-taxonomy.md) clears the relevant guard below before
it is reported. This is the security twin of the code catalog's [guards.md](../../code-evaluator/references/guards.md); the
numbering is stable so the taxonomy and cross-file files can cite a guard by number.

**#1 — Constant-fed sink.** The sink's argument is a string literal, an enum, or a value provably not
derived from a request/file/env/argv. `exec("ls -la")` is not command injection. Clear it. The tell that
it is *not* clearable: any part of the argument traces back to a source (Group A defines the sources).

**#2 — Already-parameterized / already-encoded.** A query using bound parameters (`?`/`$1`/named binds),
output passed through the framework's auto-escaper, a redirect target checked against an allow-list. The
sink is present but neutralized. Clear it — and never recommend "add escaping" where the framework
already escapes (double-encoding is its own bug).

**#3 — Framework sanitizer the tool doesn't model.** ORMs, `html/template` (Go), Rails `sanitize`,
Django templates, and DOMPurify neutralize at the sink. A grep sees the sink and misses the sanitizer.
Before reporting, check whether the ecosystem's default path already encodes — [native-tool-map.md](native-tool-map.md)
tools know most of these; grep does not.

**#4 — Test / fixture / example code.** A hard-coded `password = "test123"` in a test file, a payload
string in a fixture, a deliberate-vuln sample in an `examples/` or `/test/` tree. Secrets scanners flag
these constantly. Clear it **as a security finding** — but a real-looking secret in test code is still a
hygiene note if it resembles a live credential.

**#5 — Non-web / non-reachable surface.** A CLI tool building a command from its own trusted argv, an
internal script with no untrusted input, a code path behind an auth wall that the threat model excludes.
The signal is web-shaped; the reachability is not. Name the trust boundary and clear it — but state the
assumption, because a boundary that later opens re-arms the finding.

**#6 — Placebo secret / rotated / public key.** A public key, a documented sandbox token, a `xxxxx`
placeholder, an already-rotated value. High entropy is not sensitivity. Clear it; do not clear a
plausibly-live private key on the author's say-so.

**#7 — Dynamic dispatch defeats the grep, both ways.** Reflection, dynamic `require`, and metaprogramming
mean a grep can **miss** a real sink and **misattribute** a benign one. When a class uses dynamic
dispatch (the code catalog's guard #7, same failure), lower confidence and prefer the taint tool — never
report a reflection-based finding as HIGH from grep alone.

**#8 — The source is trusted infrastructure.** Data from a signed config, a sealed secret store, or a
value the platform guarantees is not "untrusted input" even though it is not a literal. Clear it, and
cite *why* the source is trusted.

## The security safety floor — flagging a control is itself a defect (guard #20)

The mirror of the code catalog's minimalism safety floor. These are **never** false positives to be
"cleaned up," and recommending their removal is a defect in the review, not a finding in the code:

- input validation at a trust boundary;
- an authentication or authorization check;
- output encoding / escaping;
- a Content-Security-Policy, HSTS, or a cookie security flag;
- a parameterized query, a CSPRNG, a strong password hash;
- a rate limit or lockout;
- anything the user explicitly asked to keep.

A security control that looks redundant is defense in depth until proven dead — hold it to the code
catalog's dead-code bar (a reachability proof), not to taste.

## The intent marker — a bounded shortcut, declared, is not re-flagged (guard #21)

Matching the code catalog's guard #21 exactly, reused unchanged. A deliberately-bounded security decision
carries a marker naming its ceiling and upgrade path:

```
// sec-eval: trusts internal network; add mTLS if this endpoint is ever exposed
```

A marked shortcut is **not** re-flagged as a finding — the reviewer records it as accepted-with-a-ceiling
and moves on. An *unmarked* shortcut is a finding; the fix is the marker plus, where warranted, the
upgrade. This is the one mechanism shared byte-for-byte with the code and resource passes, so an author
learns it once.

*Landed 2026-08-26. The guard set is the union of the false-positive classes named across the semgrep rule
`metadata.confidence`/`likelihood` fields and the OWASP cheat sheets' "common mistakes" sections.*
<!-- /origin -->
