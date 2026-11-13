<!-- security-ref-version: 1 -->
<!-- origin: workforce | modifiable: true -->
# security-evaluator reference version

This file is the **drift anchor** for the security catalog, mirroring the code and text catalogs. An
audit reads the integer below (workforce's *shipped* security-reference version) and compares it to the
`security_ref_version` recorded in a project's generated `security-evaluator` skill. Shipped > recorded →
the project's references are stale → drift-sync refreshes the workforce-owned (`modifiable: true`)
reference blocks, preserving any `origin: user` seams.

```
security-ref-version: 1
```

Bump this integer whenever ANY file under `references/catalogs/security/` changes in a way projects should
receive. Every file in this catalog carries a matching `<!-- security-ref-version: N -->` header on its
first line; keep them in sync so a per-file check is possible.

## Corpus provenance — the three downloaded origins

The catalog is **distilled and cited** from local clones of three repositories, not vendored verbatim
(a verbatim copy would be 37 MB and would defeat the selective-loading requirement). A re-distillation
compares against these pinned commits and appends only new classes:

| Origin | Pin at distillation | What it gave the catalog |
|--------|--------------------|--------------------------|
| `OWASP/CheatSheetSeries` | `c735a6e` (2026-08-25) | the prose spine — 121 topic sheets, the secure-pattern for each class |
| `swisskyrepo/PayloadsAllTheThings` | `3bff425` (2026-08-09) | 66 attack classes — the concrete sink shapes / signals |
| `semgrep/semgrep-rules` | `40b8c63` (2026-07-29) | ~2,000 rules with `owasp`/`cwe`/`technology` metadata — the machine layer and CWE mapping |

## Changelog

- **v1** (2026-08-26) — Initial release, authored by `/workforce dev` from the three corpora above.
  Agnostic spine = OWASP Top 10:2025 as source-review classes (Groups A–I), each with a grep-able
  **signal** and CWE mapping; a per-language sink appendix (JS/TS, Python, PHP, Java, Go, Ruby, C#) as
  illustrative surface. `native-tool-map.md` makes **semgrep** the cross-language primary, with
  per-ecosystem taint engines (`bandit`, `brakeman`, `gosec`, `find-sec-bugs`, Psalm), secrets scanners
  (`gitleaks`, `trufflehog`), and supply-chain scanners (`osv-scanner`, `govulncheck`, `npm/composer
  audit`). `guards.md` carries the false-positive clearances (#1 constant-fed sink … #8 trusted source),
  the security safety floor (#20), and the shared intent marker (#21, byte-identical to the code
  catalog's). `cross-file-detection.md` covers source→sink taint tracing, the cross-handler
  authz-consistency checks, and second-order/stored taint. All findings are report-only and
  candidate-tier by construction; the design-policy classes (access control, business logic) are flagged
  for review and never reported green.
<!-- /origin -->
