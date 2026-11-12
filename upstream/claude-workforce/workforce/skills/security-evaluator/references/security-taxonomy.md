<!-- security-ref-version: 1 -->
<!-- origin: workforce | modifiable: true -->
# Security Taxonomy — the web-security flaw classes an evaluator looks for

The checklist of vulnerability classes the security-evaluator reviews a change against. The spine is
**agnostic**: it is the OWASP Top 10:2025 categories, restated as source-review classes with the
**signal** that finds each in code. The per-language sinks — `unserialize`, `ObjectInputStream`,
`dangerouslySetInnerHTML` — are a **surface appendix** at the end, read only for the ecosystem a change
actually touches. This is the same shape as the code catalog's RC1–RC6 pass: agnostic classes, with the
language syntax as illustration and never as the structure.

For each class: **what** it is, **why** it matters, and the **signal** to detect it. The signal is the
per-row key that makes review selective — grep the diff for a class's signal, and read only the rows
whose signal appears. Detection of taint that crosses files lives in
[cross-file-detection.md](cross-file-detection.md); false-positive guards live in [guards.md](guards.md);
which real analyzer supersedes the grep lives in [native-tool-map.md](native-tool-map.md).

**Provenance.** Authored by workforce, distilled and cited from three downloaded corpora — the OWASP
Cheat Sheet Series (`OWASP/CheatSheetSeries`, 121 sheets), PayloadsAllTheThings
(`swisskyrepo/PayloadsAllTheThings`, 66 classes), and the Semgrep community rules
(`semgrep/semgrep-rules`, ~2,000 rules carrying `owasp`/`cwe`/`technology` metadata). It is **cited, not
vendored**: copying 37 MB of cheat sheets verbatim would defeat the selective-loading requirement this
catalog exists to satisfy. Every row names the CWE it maps to and the source that grounds it, on the
code catalog's rule that a taxonomy row is **measured-or-cited, never grown by analogy**. Category order
follows the authoritative OWASP Top 10:2025 (`owasp.org/Top10/2025`), not the semgrep tag string —
several rules carry transitional 2025 tags (a rule tagged both `A03:2025 - Injection` and
`A05:2025 - Injection`), so mapping is by **CWE**, which is stable, and never by the tag alone.

## How selective loading falls out of this file

1. **Native-tool gate first** ([native-tool-map.md](native-tool-map.md) §1): if `semgrep` — or a
   language security linter — is installed, it fires only the rules whose sinks are present in the code,
   which is relevance-gating done by the tool. Its output is the verdict; this taxonomy triages it.
2. **Signal-keyed rows** (this file): with no tool, detect the language and grep the diff for the signals
   below. Read only the rows whose signal matched. A crypto library never pulls the XSS row because
   `innerHTML` is not in it.
3. **Language surface read last**: only the appendix block for the detected ecosystem is opened.

"Evaluate everything" mode widens the **input** — the whole tree instead of the diff — never what loads.
The matched set stays small because a class loads only where its signal is actually present.

---

## Group A — Injection & untrusted-input execution (A05:2025 Injection)

The largest class by rule count and the oldest. A source (request data) reaches a sink (an interpreter)
without neutralization. Every row is a **taint** finding: the signal is the *sink*, and the finding is
real only if untrusted data can reach it — which is why taint that crosses files defers to
[cross-file-detection.md](cross-file-detection.md), and why a sink fed only by constants is a guard-cleared
non-finding ([guards.md](guards.md) #1).

| Class | CWE | What / why | Signal (the sink) |
|-------|-----|------------|-------------------|
| **SQL injection** | CWE-89 | String-built query reaches the DB driver; auth bypass, data theft | concatenation/interpolation into `query`/`execute`/`raw`/`DB::raw`; ORM `.where("… "+x)` (75 semgrep rules; `Injection_Prevention` + `Query_Parameterization` sheets) |
| **OS command injection** | CWE-78 | User data reaches a shell | `system`/`exec`/`popen`/`ProcessBuilder`/`child_process.exec`/`os.system` with a non-constant arg (62 rules; `OS_Command_Injection_Defense` sheet) |
| **Code injection / eval** | CWE-94 / CWE-95 | User data reaches a language evaluator | `eval`/`Function(`/`exec`/`compile`/`setTimeout("string")`/`pickle`/`yaml.load` (49+31 rules) |
| **XSS — reflected/stored** | CWE-79 | Unescaped data in an HTML response | `innerHTML`/`document.write`/`v-html`/`dangerouslySetInnerHTML`/unescaped template output/`echo $_GET` (127 rules; `Cross_Site_Scripting_Prevention` + `DOM_based_XSS_Prevention`) |
| **Template injection (SSTI)** | CWE-1336 | User data in a server template string | `render_template_string`/`Template(user)`/Twig/Freemarker with concatenated input (`Server Side Template Injection` payloads) |
| **Path traversal** | CWE-22 | User data in a filesystem path | `open`/`readFile`/`sendFile`/`File(new)` with a request-derived path lacking canonicalize+prefix-check (25 rules; `File Inclusion` / `Directory Traversal`) |
| **XXE** | CWE-611 | XML parsed with external entities enabled | an XML parser built without disabling DTD/external entities (33 rules; `XML_External_Entity_Prevention` sheet) |
| **LDAP / XPath / NoSQL / CRLF / SSI** | CWE-90/643/943/93 | Same shape, other interpreters | filter/query/header built from input reaching the respective API (payload classes present for each) |

## Group B — Broken Access Control (A01:2025)

The 2025 #1, and the one static analysis is worst at — access control is a *policy*, and its absence
looks like ordinary code. The signals below find the shapes that are *checkable*; the rest is a design
review the taxonomy flags for a human, never claims to have cleared.

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **IDOR / missing object-level auth** | CWE-1220 / CWE-639 | A handler reads `id` from the request and loads the record with no ownership check | a route param (`:id`, `req.params`, `@PathVariable`) flowing to a fetch-by-id with no `where owner = current_user` nearby (108 rules for CWE-1220; `Insecure Direct Object References` payloads) |
| **Missing function-level auth** | CWE-862 | A privileged route has no authorization guard | a route/controller method with no auth decorator/middleware while siblings have one — a *cross-handler* consistency check ([cross-file-detection.md](cross-file-detection.md)) |
| **Mass assignment** | CWE-915 | Request body bound wholesale to a model | `Model(**request)`/`update_attributes(params)`/`Object.assign(entity, req.body)` (15 rules; `Mass Assignment` payloads) |
| **Open redirect** | CWE-601 | User-controlled redirect target | `redirect(request.…)`/`Location: `+input with no allow-list (17 rules; `Open Redirect` payloads) |
| **Path/tenant confusion, SSRF-as-access** | CWE-918 | see Group F — SSRF folded under access control in 2025 | (Group F) |

## Group C — Cryptographic Failures (A04:2025)

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **Broken/weak algorithm** | CWE-327 | MD5/SHA1/DES/RC4/ECB for security | `MD5`/`SHA1`/`DES`/`RC4`/`ECB` in a hashing/cipher construction (58 rules; `Cryptographic_Storage` sheet) |
| **Weak password hash** | CWE-916 | Fast/unsalted hash for passwords | password stored via a plain digest instead of bcrypt/scrypt/argon2/PBKDF2 |
| **Inadequate key strength / mgmt** | CWE-326 / CWE-320 | Short keys, hard-coded keys, reused IV/nonce | RSA < 2048, a literal key/IV, a static nonce (49+51 rules) |
| **Cleartext transmission** | CWE-319 | Sensitive data over plaintext | `http://` endpoint, `verify=False`, disabled TLS check (76 rules) |
| **Insecure randomness for secrets** | CWE-330 | `Math.random`/`rand()` for tokens | a non-CSPRNG feeding a token/salt/session id (`Insecure Randomness` payloads) |

## Group D — Hard-coded & exposed secrets (CWE-798, spanning A02/A04/A07)

The single most frequent finding in the corpus (**265 semgrep rules**, the top CWE by a wide margin) —
so it is its own group, not a footnote.

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **Hard-coded credential/key/token** | CWE-798 / CWE-259 | A secret in source ships to every reader of the repo | a string literal assigned to `password`/`secret`/`api_key`/`token`/`private_key`, or a high-entropy blob (defer to `gitleaks`/`trufflehog` — [native-tool-map.md](native-tool-map.md); `API Key Leaks` payloads) |
| **Secret in config/log/error** | CWE-532 / CWE-200 | Secret leaked to logs or a client error | a secret-named field passed to a logger or serialized into a response |

## Group E — Security Misconfiguration (A02:2025, up from #5 in 2021)

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **Insecure default / debug on** | CWE-1188 / CWE-489 | `DEBUG=True`, default creds, stack traces to client | a framework debug flag on in prod config (17 rules) |
| **Permissive CORS** | CWE-942 | `Access-Control-Allow-Origin: *` with credentials | a wildcard origin plus `Allow-Credentials: true` (`CORS Misconfiguration` payloads) |
| **Missing security headers / cookie flags** | CWE-614 / CWE-1004 / CWE-693 | No `HttpOnly`/`Secure`/`SameSite`; missing CSP/HSTS | a `Set-Cookie` without flags; no CSP (`HTTP_Headers` + `Content_Security_Policy` sheets) |
| **Over-broad permissions** | CWE-732 / CWE-250 | World-writable, excess privilege | a `chmod 0777`, a container running as root (16+16 rules) |

## Group F — SSRF (A01:2025, folded into Broken Access Control)

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **Server-Side Request Forgery** | CWE-918 | Server fetches a user-controlled URL; reaches internal metadata/services | an HTTP client (`requests`/`fetch`/`URL(`/`http.Get`) with a request-derived URL and no allow-list (41 rules; `Server Side Request Forgery` payloads) |

## Group G — Software & Data Integrity, and Supply Chain (A08:2025 + A03:2025)

The 2025 list splits these; the code signals overlap, so they share a group.

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **Unsafe deserialization** | CWE-502 | Deserializing untrusted bytes → RCE | `pickle.loads`/`unserialize`/`ObjectInputStream`/`yaml.load`/`Marshal.load` on request data (42 rules; `Deserialization` sheet; `Insecure Deserialization` payloads) |
| **Untrusted code inclusion / dependency confusion** | CWE-829 / CWE-1357 | Loading from an untrusted source; a public package shadowing a private one | a dynamic `require`/`import` of a request-derived name; an unscoped internal package (`Dependency Confusion` payloads; `Dependency_Graph_SBOM` sheet) |
| **Unpinned / outdated dependency** | CWE-1104 / CWE-937 | A floating or known-vulnerable dependency | a manifest range with no lock, or a version in an advisory — defer to `osv-scanner`/`npm audit`/dependabot ([native-tool-map.md](native-tool-map.md)) |
| **Prototype pollution** | CWE-1321 | `__proto__` reachable from a merge/assign | a recursive merge/`set(obj, path, val)` over request keys (`Prototype Pollution` payloads; JS/TS) |

## Group H — Authentication Failures (A07:2025)

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **Broken JWT handling** | CWE-347 | `alg:none`, unverified signature, secret confusion | `decode(token, verify=False)`/no-verify JWT call (`JSON Web Token` payloads; `JSON_Web_Token_for_Java`) |
| **Missing rate-limit / lockout** | CWE-307 | No brute-force protection on auth | a login/OTP handler with no throttle (`Brute Force Rate Limit` payloads; `Authentication` sheet) |
| **Weak session management** | CWE-384 / CWE-613 | No rotation on login, no expiry | a session fixation shape; a token with no TTL (`Session_Management` sheet) |

## Group I — Logging failures & Mishandling of Exceptional Conditions (A09 + A10:2025)

A10 is new in 2025 and is the security face of the code catalog's *swallowed errors* class — the two
catalogs meet here.

| Class | CWE | What / why | Signal |
|-------|-----|------------|--------|
| **Fail-open on error** | CWE-636 | A `catch` that grants access / continues on a security check failure | an auth/verify call in a `try` whose `catch` returns success or falls through (code catalog's *swallowed errors*, read for a security effect) |
| **Sensitive data / no security logging** | CWE-778 / CWE-532 | Auth events unlogged, or secrets logged | a security-relevant action with no audit log; a secret in a log call (15 rules) |

---

## The honesty disciplines — a security catalog without them is a false-positive engine

Ported verbatim in spirit from the code catalog's resource pass, because static security review has the
exact same epistemics: **the reader cannot see runtime reachability, so most findings are candidates.**

1. **Taint is a candidate until the source→sink path is shown.** A sink alone is not a finding — the
   finding is "untrusted data reaches this sink." Where the source and sink are in one function, show the
   path; where they cross files, defer to [cross-file-detection.md](cross-file-detection.md). A sink fed
   only by constants or already-sanitized data is **cleared**, not reported ([guards.md](guards.md) #1).
2. **The native tool is the verdict where present.** `semgrep` and the language linters do real taint and
   dataflow; grep does not. Present → run it, triage its output through these guards. Absent → grep
   fallback, reported as **candidates with a confidence band**, never as confirmed vulnerabilities
   ([native-tool-map.md](native-tool-map.md) decision rule). This is the code catalog's native-tool gate,
   unchanged.
3. **The security safety floor** — the mirror of the minimalism safety floor. A security control is
   **never** flagged as over-built: input validation at a trust boundary, an auth check, output encoding,
   a CSP, a parameterized query, a rate limit. The code catalog already says "security measures" are off
   the minimalism chopping block; this is that clause, owned here. Recommending the *removal* of one of
   these is itself a defect.
4. **Design-policy findings are flagged, never cleared.** Access-control completeness, business-logic
   flaws, and authorization *correctness* are not decidable by signal. The taxonomy raises them as
   "needs a human/design review" and says so — it never reports them green, and never claims to have
   proven their absence (Core Principle 6: detection where prevention is impossible, stated plainly).

A deliberately-bounded security shortcut carries the existing intent marker (`guards.md` #21,
`// sec-eval: <ceiling and upgrade path>`) and is not re-flagged — the same marker mechanism the code
catalog already uses, reused unchanged.

## How the layers use this taxonomy (mirrors the code catalog's L1/L2/L3)

- **L1 advisor (pre-write):** the prevention rungs — parameterize, don't concatenate; encode on output;
  allow-list before redirect/fetch; a CSPRNG for secrets; a strong password hash. Prevents the Group A
  and Group C classes at authoring time.
- **L2 reviewer (post-write, the default mode):** the full signal grep against the **diff**, native tool
  where present, candidates tiered by confidence, guards cleared before reporting.
- **Sweep (the "evaluate everything" mode):** the same signals across the **whole tree** — input widened,
  matched set still gated by presence of signal.

---

## Language surface — sinks per ecosystem (illustrative appendix, NOT the structure)

Read only the block for the ecosystem a change touches. A class fires by its agnostic signal above; this
makes it concrete. Cited from the semgrep `technology:` tags and the language cheat sheets.

**JavaScript / TypeScript / Node** — `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `document.write`,
`eval`, `Function(`, `child_process.exec`, `require(<dynamic>)`, `__proto__`/recursive-merge, `Math.random`
for tokens, `res.redirect(req.…)`, an `http`/`fetch` to a request URL. Sheets: `Nodejs_Security`,
`DOM_based_XSS_Prevention`, `DOM_Clobbering_Prevention`.

**Python** — `cursor.execute(f"… ")`, `os.system`/`subprocess(..., shell=True)`, `eval`/`exec`,
`pickle.loads`, `yaml.load` (not `safe_load`), `flask … render_template_string`, `requests(..., verify=False)`,
`open(<request path>)`, `hashlib.md5` for a password. Sheets: `Django_Security`, `Django_REST_Framework`.

**PHP** — `mysqli_query("… $x")`, `unserialize($_…)`, `include $_GET`, `eval`, `system`/`exec`/`shell_exec`,
`echo $_GET` (XSS), `==` where `===` is meant (type juggling — `Type Juggling` payloads), `extract($_…)`.
Sheets: `PHP_Configuration`, `Laravel_Cheat_Sheet`.

**Java / Kotlin** — `Statement.execute(concat)`, `ObjectInputStream.readObject`, `Runtime.exec`,
`ProcessBuilder`, an XML parser without `disallow-doctype-decl`, `@PathVariable id` to a repo fetch with no
ownership check, `Cipher.getInstance("…/ECB/…")`. Sheets: `Deserialization`, `XML_External_Entity_Prevention`,
`Java_Security`.

**Go** — `db.Query(fmt.Sprintf(…))`, `exec.Command(…, userinput)`, `http.Get(userURL)`, `template.HTML(user)`
(bypasses `html/template` escaping), `md5.New()` for a secret. Sheets: `Go_SCP` references in semgrep `go/`.

**Ruby** — `where("… #{x}")`, `Marshal.load`, `system`/backticks, `constantize`/`send(user)`, `eval`,
`redirect_to params[…]`. Sheets: `Ruby_on_Rails_Cheat_Sheet`.

**C# / .NET** — `SqlCommand(concat)`, `BinaryFormatter.Deserialize`, `Process.Start`, `XmlReader` with DTD
enabled, `new Random()` for a token. Sheet: `DotNet_Security`.

*Landed 2026-08-26 by `/workforce dev`, distilled from `OWASP/CheatSheetSeries` @ c735a6e,
`swisskyrepo/PayloadsAllTheThings` @ 3bff425, `semgrep/semgrep-rules` @ 40b8c63. The convergence — the
same source→sink taint shape recurring across seven unrelated language runtimes — is the grounding: a
class that appears in all of them is cross-cutting, which is why the spine is agnostic and the table is
only its surface.*
<!-- /origin -->
