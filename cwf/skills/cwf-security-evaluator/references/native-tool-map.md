<!-- security-ref-version: 1 -->
<!-- origin: workforce | modifiable: true -->
# Native-Tool Map — prefer a real security analyzer when present

The security twin of the code catalog's [native-tool-map](../../code-evaluator/references/native-tool-map.md), and it works the
same way: a real analyzer uses ASTs, type info, and **dataflow/taint** — so it establishes reachability
that grep only guesses at, and it is what makes the whole pass selective, because it fires **only the
rules whose sinks are present in the code under review**. Detect the ecosystem by its marker file, prefer
these over the [security-taxonomy](security-taxonomy.md) signal grep, and always reconcile the output
against [guards.md](guards.md) — tools miss dynamic dispatch, reflection, and framework-specific sanitizers.

## §1 — Detection and the decision rule

Check for both the binary and the ecosystem marker, exactly as the code catalog does:
`package.json` → JS/TS · `pyproject.toml`/`requirements.txt` → Python · `composer.json` → PHP ·
`go.mod` → Go · `pom.xml`/`build.gradle` → Java · `Gemfile` → Ruby · `*.csproj` → .NET.

**The primary analyzer is `semgrep`, and it is cross-language.** Its community ruleset is the corpus this
catalog was distilled from, so its verdicts and this taxonomy speak the same CWE/OWASP vocabulary. Probe
it with `command -v semgrep`; run the security registry with `semgrep --config auto` (or a pinned local
copy of `semgrep/semgrep-rules` for a hermetic run). A finding carries its `check_id`, CWE, and OWASP tag
— triage it through [guards.md](guards.md), do not re-derive it.

**Decision rule** (identical in spirit to the code catalog): a real analyzer present → run it, use grep
only to triage and contextualize its output. No analyzer → fall back to the taxonomy's signal grep, and
**report every finding as a candidate with a confidence band, never as a confirmed vulnerability** —
grep is blind to taint, so it raises suspicion, it does not prove exploitability. Use a tool's verdict to
*raise* confidence; never let grep alone assert a vulnerability a tool would have cleared.

## §2 — The security analyzers by ecosystem

| Ecosystem | Primary (taint/dataflow) | Secrets | Dependencies (supply chain) | Notes / limits |
|-----------|--------------------------|---------|-----------------------------|----------------|
| **Cross-language** | **`semgrep --config auto`** | `gitleaks`, `trufflehog` | `osv-scanner` (all lockfiles), `trivy fs` | semgrep is the default everywhere; the rows below add language-native depth |
| **JS/TS** | `semgrep`; `eslint-plugin-security`; CodeQL | `gitleaks` | `npm audit`, `osv-scanner`, dependabot | eslint security is heuristic, not taint — semgrep/CodeQL for dataflow |
| **Python** | `bandit`; `semgrep`; CodeQL | `detect-secrets`, `gitleaks` | `pip-audit`, `osv-scanner` | bandit is signal-level (like B\* IDs); pair with semgrep for taint |
| **PHP** | `semgrep`; Psalm/PHPStan + `vimeo/psalm` taint; `phpcs` security sniffs | `gitleaks` | `composer audit`, `osv-scanner` | Psalm taint needs a whole-project run |
| **Go** | `gosec`; `semgrep`; CodeQL | `gitleaks` | `govulncheck` (official, reachability-aware), `osv-scanner` | `govulncheck` filters to *called* vulnerable symbols — prefer it |
| **Java/Kotlin** | `semgrep`; CodeQL; SpotBugs + **`find-sec-bugs`** | `gitleaks` | `osv-scanner`, OWASP Dependency-Check | find-sec-bugs is the deepest free Java taint engine |
| **Ruby** | **`brakeman`** (Rails, taint-aware); `semgrep` | `gitleaks` | `bundler-audit`, `osv-scanner` | brakeman is Rails-specific and excellent — prefer it there |
| **C#/.NET** | `semgrep`; CodeQL; `security-scan` (Roslyn) | `gitleaks` | `osv-scanner`, `dotnet list package --vulnerable` | Roslyn security analyzers are intra-project |
| **IaC / containers** | `semgrep`; `checkov`; `tfsec`/`trivy config` | `gitleaks` | `trivy image` | the terraform/dockerfile rules were the largest semgrep buckets — IaC is in scope |

A matched marker with no installed binary degrades to the taxonomy grep with a one-line
"install `<tool>` for taint-accurate results" note — **never an auto-install, never a silent skip**, the
code catalog's rule unchanged.

## §3 — Why semgrep is the anchor and not the whole story

A local clone of `semgrep/semgrep-rules`, pinned at the commit `version.md` records, is the corpus.
Two cautions the catalog inherits from having read it:

- **Its 2025 OWASP tags are transitional** — some rules carry two conflicting `A0x:2025` strings. Map a
  finding to a class by its **CWE**, which is stable, not by the tag.
- **Community rules skew to confident, low-false-positive patterns** and under-cover access control and
  business logic (the classes no signal decides — [security-taxonomy.md](security-taxonomy.md) Groups B,
  H). A clean semgrep run is **not** an all-clear for those; the taxonomy's design-policy discipline
  (§ honesty disciplines #4) still applies. Report "semgrep clean; access-control and business-logic
  correctness not covered by it — needs review," never "semgrep clean → secure."

*Landed 2026-08-26. Tool list cross-checked against the `technology:` tags in `semgrep/semgrep-rules`
@ 40b8c63 and the OWASP `Free_for_Open_Source_Application_Security_Tools` sheet.*
<!-- /origin -->
