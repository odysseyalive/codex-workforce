<!-- ui-design-ref-version: 2 -->
<!-- design-quality-ref-version: 1 -->
<!-- The design-quality catalog for rendered interfaces. Owner: the project's UI evaluator — whichever
     employee runs `/ui-design review` (read-only library, read BY PATH per evaluators.md — never
     invoked as a skill by an IC). Where a project already carries a ui-design catalog, that one is
     canonical and this file contributes only the entries it lacks (evaluators.md item 3b); the seed's
     additions this file does not cover live in references/rendered-checks.md, never inlined here.
     Growth goes in a machine-owned region at the END of this file; existing rows are never reworded.
     Basis tags: Stated = quote-backed from the cited source; Derived = inference/owner house-rule
     anchored to nearest support.
     Provenance: seeded 2026-08-26 from 20 sources fetched and cited (WebSearch->web_fetch); carried
     forward 2026-09-10 from the project it was built in, with not one row reworded. -->
# Design-Review Standards Catalog — Rendered Interfaces (marketing, landing, beta-signup, and app screens)

**Purpose.** A cited, checkable catalog of industry-standard criteria professionals use to
evaluate and critique front-end visual design quality on marketing, presentation, landing, and
beta-signup pages. Built to seed a design-review evaluator agent. This grounds a hiring decision,
so every rule is traceable to a source that was actually fetched and read.

**How to read a rule.** Each rule is a block, keyed by a stable ID the evaluator can cite in its
findings (e.g. "fails CTA-04"):

> **ID** — *checkable assertion (pass/fail against a rendered page)*
> **Check:** how a reviewer verifies it against the rendered page.
> **Severity:** BLOCK (hard fail / must not ship) · MAJOR · MINOR.
> **Basis:** **Stated** = the source states this directly (quote-backed). **Derived** = the source
> supports the principle but the specific rule is an inference or an owner house-rule anchored to
> the nearest authoritative support.
> **Source:** a real URL that was fetched for this catalog.

**Verification note.** Every source cited below was fetched and read via `web_fetch` on
2026-08-26 unless it appears in the "Sources attempted but not verifiable" section. Two priority
sources could not be fetched (CXL — Cloudflare bot wall; storybrand.com — timeout); StoryBrand is
therefore cited through a corroborating secondary, and CXL is not cited as verified. See that
section and the Source Ledger at the end.

---

## 1. Visual hierarchy & layout  (VH)

> **VH-01** — The page establishes a clear visual hierarchy: the single most important element on
> each screenful is the most visually prominent (size, weight, color, or contrast), and not
> everything competes for attention.
> **Check:** Squint / blur the rendered viewport; the primary element (headline or primary CTA)
> should still dominate. If 3+ elements read as equally loud, fail.
> **Severity:** MAJOR
> **Basis:** Stated ("Use hierarchy and visual weight to draw attention to your prioritized tasks…
> if everything is emphasized, nothing stands out").
> **Source:** [NNG — Homepage Design: 5 Fundamental Principles](https://www.nngroup.com/articles/homepage-design-principles)

> **VH-02** — Important content and the primary action are placed where the scan lands: high on
> the page and toward the top-left of the content area, following the F-pattern for text-heavy
> regions.
> **Check:** Confirm the value prop and primary CTA fall in the top band / left of the first
> screenful, not buried mid-right or below dense prose.
> **Severity:** MAJOR
> **Basis:** Stated (users scan in an F-shape; "first lines… receive more gazes," "first few words
> on the left… receive more fixations"; antidote is to put important points first and format for
> the eye).
> **Source:** [NNG — F-Shaped Pattern of Reading](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content)

> **VH-03** — Text is formatted to break the "wall of text": headings/subheadings that look
> heavier than body text, bolded key phrases, short paragraphs, and bulleted lists where
> appropriate.
> **Check:** Scan for unformatted multi-line prose blocks with no headings/bolding. Presence of a
> wall of text = fail (it forces low-value F-scanning).
> **Severity:** MAJOR
> **Basis:** Stated (the F-shape appears when text "has a 'wall of text' but no bolding, bullets,
> or subheadings"; antidotes listed verbatim).
> **Source:** [NNG — F-Shaped Pattern of Reading](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content)

> **VH-04** — Important information or the key action is made visually distinctive from its
> surroundings (the isolated element is the one remembered) — but emphasis is used with restraint
> so highlighted items don't compete or read as ads.
> **Check:** The primary CTA (or hero claim) is visually isolated/differentiated. Multiple loud
> "distinct" elements cancel each other = fail.
> **Severity:** MAJOR
> **Basis:** Stated (Von Restorff / Isolation Effect; "Use restraint… to avoid them competing…
> and to ensure salient items don't get mistakenly identified as ads").
> **Source:** [Laws of UX — Von Restorff Effect](https://lawsofux.com/von-restorff-effect)

> **VH-05** — The layout uses generous, purposeful whitespace/negative space; it is not cluttered,
> and negative space is used to group related items and separate unrelated ones.
> **Check:** Look for cramped, edge-to-edge dense regions with no breathing room, and for
> ambiguous spacing where a label/element sits equidistant between two groups. Either = fail.
> **Severity:** MAJOR
> **Basis:** Stated. Refactoring UI ships chapters "Start with too much white space," "Establish a
> spacing and sizing system," and "Avoid ambiguous spacing." NNG: maximize signal, minimize noise;
> "every piece of content should have a purpose, including negative space."
> **Source:** [Refactoring UI — table of contents](https://refactoringui.com/) · [NNG — Aesthetic & Minimalist Design (Heuristic #8)](https://www.nngroup.com/articles/aesthetic-minimalist-design)

> **VH-06** — Spacing, sizing, and alignment follow a consistent system (a constrained scale),
> and elements are aligned to a shared grid rather than placed ad hoc.
> **Check:** Sample gaps/margins across sections; wildly inconsistent spacing or misaligned
> section edges/columns = fail.
> **Severity:** MINOR
> **Basis:** Stated (Refactoring UI: "Establish a spacing and sizing system"). Derived for the
> alignment specifics.
> **Source:** [Refactoring UI — table of contents](https://refactoringui.com/)

> **VH-07** — The interface contains only elements with real informational value; decorative
> "noise" that competes with content is removed (communicate, don't decorate).
> **Check:** Flag purely decorative graphics, redundant flourishes, and multipurpose visual cues
> (e.g., same treatment for links and non-clickable text).
> **Severity:** MINOR
> **Basis:** Stated ("Maximize the 'signal'… Minimize the 'noise'… communicate; don't decorate";
> "Every extra unit of information… competes with the relevant units and diminishes their
> visibility").
> **Source:** [NNG — Aesthetic & Minimalist Design (Heuristic #8)](https://www.nngroup.com/articles/aesthetic-minimalist-design)

---

## 2. Color & brand / palette application  (COL)

> **COL-01** — Color is applied in a defined role hierarchy: a dominant neutral surface, an accent
> for the most important actions/elements, and sparing secondary/tertiary accents — not many
> equally-weighted colors.
> **Check:** Identify the role of each hue. Primary/brand accent should attach to the most
> important actions; if the palette is a flat spread of same-weight colors with no dominant surface
> and no clear accent, fail.
> **Severity:** MAJOR
> **Basis:** Stated (Material 3: Surface = backgrounds/low-emphasis; Primary = "most important
> elements needing the most emphasis"; Secondary = less prominent; Tertiary = sparing accents).
> **Source:** [Material Design 3 — Color roles](https://m3.material.io/styles/color/roles)

> **COL-02** — Accent / brand color is reserved for elements that genuinely need emphasis (e.g.,
> the primary CTA); it is not sprayed across many controls at once.
> **Check:** Count brand-accent uses in the first screenful; if the emphasis color is on many
> competing elements (so nothing is emphasized), fail.
> **Severity:** MAJOR
> **Basis:** Stated (Apple HIG: "Apply color sparingly… reserve it for elements that truly benefit
> from emphasis, such as status indicators or primary actions… Refrain from adding color to the
> background of multiple controls").
> **Source:** [Apple HIG — Color](https://developer.apple.com/design/human-interface-guidelines/color)

> **COL-03** — A "60-30-10"-style discipline is honored: one dominant color, one secondary, one
> small-dose accent. (Treat the exact ratio as a heuristic; enforce the underlying discipline via
> COL-01/COL-02.)
> **Check:** The page reads as dominant-neutral + one secondary + a small accent, not a rainbow.
> **Severity:** MINOR
> **Basis:** Derived. 60-30-10 is a widely cited industry rule of thumb with **no authoritative
> primary source located** (it is an interior-design convention that migrated into UI blogs; it is
> **not** in Refactoring UI's chapter list, contrary to common secondhand attribution). Enforce
> the same "one dominant / one accent / one sparing highlight" discipline through the two
> quote-backed rules above.
> **Source:** [Material Design 3 — Color roles](https://m3.material.io/styles/color/roles) (role-hierarchy support in lieu of a 60-30-10 primary)

> **COL-04** — Color is used consistently: the same color means the same thing throughout the
> surface (e.g., the interactive/brand color is not also used to style non-interactive text).
> **Check:** Confirm one consistent color = interactive, another = headings, etc. Reused
> ambiguous color meanings = fail.
> **Severity:** MAJOR
> **Basis:** Stated (Apple HIG: "Avoid using the same color to mean different things. Use color
> consistently… if you use your brand color to indicate that a button is interactive, using the
> same color to stylize noninteractive text is confusing").
> **Source:** [Apple HIG — Color](https://developer.apple.com/design/human-interface-guidelines/color)

> **COL-05** — When a distinct / divergent brand palette is warranted, it is applied as a coherent
> system across the whole surface (accent color as the app/brand accent), not merely recorded in a
> spec and left un-applied. A monochromatic surface is the case where committing the brand color as
> the accent pays off.
> **Check:** Compare any declared brand palette to what's rendered. If brand colors exist in the
> brand/spec but the page is generic default styling (brand accent absent from CTAs, headings,
> links), fail. Application must be consistent across sections.
> **Severity:** BLOCK  *(see Red Flags — recorded-but-un-applied palette)*
> **Basis:** Derived (owner house-rule from the FetchMLS pivot), anchored to: Apple HIG
> ("choosing your brand color as the app accent color can be an effective way to… reflect your
> company's identity"; apply consistently) and Material 3 (color roles are tokenized and applied
> in intended pairs so one decision propagates across the surface).
> **Source:** [Apple HIG — Color](https://developer.apple.com/design/human-interface-guidelines/color) · [Material Design 3 — Color roles](https://m3.material.io/styles/color/roles)

> **COL-06** — Color pairings preserve legibility: foreground/background pairs meet contrast
> (cross-refs A11Y-01), and color is never the *only* signal for meaning/state.
> **Check:** Verify text-on-color and control states carry a non-color cue (icon, label, shape).
> **Severity:** MAJOR
> **Basis:** Stated (Material 3: role pairs provide "accessible minimum 3:1 contrast"; Apple HIG:
> "Avoid relying solely on color… provide the same information in alternative ways").
> **Source:** [Material Design 3 — Color roles](https://m3.material.io/styles/color/roles) · [Apple HIG — Color](https://developer.apple.com/design/human-interface-guidelines/color)

---

## 3. Typography  (TYP)

> **TYP-01** — A clear type hierarchy distinguishes headings, subheadings, and body via a
> consistent type scale (size/weight), so the page is scannable.
> **Check:** Headings are visibly larger/heavier than body; step sizes look systematic, not
> arbitrary. All same-level headings share size/weight/font.
> **Severity:** MAJOR
> **Basis:** Stated (Refactoring UI chapter "Establish a type scale"; Smashing: "Hierarchy… refers
> to the difference in size… all `<h1>` headers in an article should look identical").
> **Source:** [Refactoring UI — table of contents](https://refactoringui.com/) · [Smashing — 10 Principles of Readability & Web Typography](https://www.smashingmagazine.com/2009/03/10-principles-for-readable-web-typography)

> **TYP-02** — Body line length (measure) sits roughly in the 50–75 character range and does not
> exceed ~80 characters per line.
> **Check:** Measure characters-per-line of the main body column (a `max-width` around 66ch /
> ~34em is the target). Full-viewport-width running text = fail.
> **Severity:** MAJOR
> **Basis:** Stated (Baymard: "optimal line length for body text is 50–75 characters"; WCAG 1.4.8
> ceiling of 80). Corroborated by Refactoring UI chapter "Keep your line length in check."
> **Source:** [Baymard — Readability: The Optimal Line Length](https://baymard.com/blog/line-length-readability)

> **TYP-03** — Line-height (leading) is comfortable and proportional to font size (~1.5× for body
> text); lines are neither cramped nor floating apart.
> **Check:** Body line-height around 1.5em; headings tighter but not colliding.
> **Severity:** MINOR
> **Basis:** Stated (Baymard cites 1.5em line height for accessible text; Refactoring UI:
> "Line-height is proportional"; Smashing: line height affects scannability).
> **Source:** [Baymard — Optimal Line Length](https://baymard.com/blog/line-length-readability) · [Smashing — Readability & Web Typography](https://www.smashingmagazine.com/2009/03/10-principles-for-readable-web-typography)

> **TYP-04** — Typographic contrast is strong: dark text on light (or vice versa), no low-contrast
> body text, no grey text on colored backgrounds.
> **Check:** Body text reads effortlessly; flag faint grey-on-white or text over busy imagery.
> (Enforce the numeric threshold via A11Y-01.)
> **Severity:** MAJOR
> **Basis:** Stated (Smashing: "Contrast is the core factor in whether text is easy to read";
> Refactoring UI chapter "Don't use grey text on colored backgrounds").
> **Source:** [Smashing — Readability & Web Typography](https://www.smashingmagazine.com/2009/03/10-principles-for-readable-web-typography) · [Refactoring UI — table of contents](https://refactoringui.com/)

> **TYP-05** — Type choices and spacing are consistent and restrained: a small set of fonts, no
> excessive font/size/color variation, adequate space between headings and the body they lead.
> **Check:** Count distinct fonts/weights/sizes; sprawling variety or no space under headings =
> fail.
> **Severity:** MINOR
> **Basis:** Stated (NNG: "don't overdo font/color variation"; Smashing: consistency + ample space
> between header and body).
> **Source:** [NNG — Aesthetic & Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design) · [Smashing — Readability & Web Typography](https://www.smashingmagazine.com/2009/03/10-principles-for-readable-web-typography)

---

## 4. Imagery & graphics  (IMG)

> **IMG-01** — No image is missing, broken, blank, or a placeholder. Every image slot renders a
> real, intended asset.
> **Check:** Scan the rendered DOM for broken `img` (alt-only/broken icon), empty/solid-color
> placeholder blocks, "lorem"/sample images, or grey boxes where art should be. Any = hard fail.
> **Severity:** BLOCK  *(see Red Flags)*
> **Basis:** Derived (owner hard gate), anchored to NNG: "Your homepage is the most valuable real
> estate… every image should serve a purpose and add value."
> **Source:** [NNG — Homepage Design: 5 Fundamental Principles](https://www.nngroup.com/articles/homepage-design-principles)

> **IMG-02** — Imagery is purposeful and information-carrying (shows the product, real people, or
> content relevant to the task) rather than decorative filler that users ignore.
> **Check:** Ask "does this image convey information about the product/company?" Generic
> mood/filler imagery that could be swapped for anything = fail.
> **Severity:** MAJOR
> **Basis:** Stated (NNG: users "pay attention to information-carrying images… and ignore purely
> decorative images"; "jazzed-up = ignored").
> **Source:** [NNG — Photos as Web Content](https://www.nngroup.com/articles/photos-as-web-content)

> **IMG-03** — Hero / featured imagery accurately reflects the brand and the actual offering; it
> is not a generic stock image that could misrepresent what the company does.
> **Check:** Hero image should let a first-time visitor infer the business. A generic stock
> abstraction (e.g., stock "water" for a company that isn't about water) = fail.
> **Severity:** MAJOR
> **Basis:** Stated (NNG homepage principle 2.4: "Ensure featured imagery accurately reflects your
> brand… Avoid purely decorative or unhelpful graphics"; the Par Pacific stock-water anti-example).
> **Source:** [NNG — Homepage Design: 5 Fundamental Principles](https://www.nngroup.com/articles/homepage-design-principles)

> **IMG-04** — People shown read as real (team/customers), not obvious generic stock models used
> as filler.
> **Check:** Flag slick, context-free "smiling model" stock that serves no functional purpose.
> **Severity:** MINOR
> **Basis:** Stated (NNG: real people get attention; "users ignore stock photos of generic
> people").
> **Source:** [NNG — Photos as Web Content](https://www.nngroup.com/articles/photos-as-web-content)

> **IMG-05** — The graphic/illustration system is consistent (one visual language, palette, and
> line/stroke treatment) across all imagery on the surface.
> **Check:** Compare all graphics for a shared style; a mix of clashing illustration styles or
> palettes = fail.
> **Severity:** MAJOR
> **Basis:** Derived (owner house-rule / graphic-system integrity), anchored to NNG: "aesthetics
> establish and reinforce your brand's identity… when used consistently."
> **Source:** [NNG — Aesthetic & Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design)

---

## 5. CTA & conversion (beta / signup pages)  (CTA)

> **CTA-01** — There is exactly one clear PRIMARY call to action, visually dominant over any
> secondary actions, and it is present above the fold.
> **Check:** Identify the single loudest action in the first screenful. If there is no obvious
> primary action, or several equally-weighted CTAs compete, fail.
> **Severity:** BLOCK  *(see Red Flags — weak/absent primary CTA)*
> **Basis:** Stated (Julian Shapiro: the CTA/signup button must be "unmissable," a single
> self-evident next action; NNG: give a "clear starting point" with visual prominence).
> **Source:** [Julian Shapiro — Landing Page Copywriting](https://www.julian.com/guide/startup/landing-pages) · [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles)

> **CTA-02** — CTA button copy is specific and action/outcome-oriented, continuing the value the
> headline promised — not generic ("Click Here", "Learn More", "Submit", vague "Get Started").
> **Check:** Read the button label out of context. If it doesn't tell you what happens next, fail.
> **Severity:** MAJOR
> **Basis:** Stated (NNG: "Generic language like Click Here, Explore, or Learn More does not tell
> users what they will get"; separate NNG article: a generic "Get Started" misleads and stalls
> users; Julian: strong CTAs like "Find food"/"Start learning" continue the hero narrative).
> **Source:** [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles) · [NNG — "Get Started" Stops Users](https://www.nngroup.com/articles/get-started) · [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages)

> **CTA-03** — The CTA target is large enough and positioned near the user's point of attention /
> the content it acts on (short travel distance).
> **Check:** Button is a comfortable click/tap target, placed by the value prop or form it
> completes, not stranded far from the flow.
> **Severity:** MINOR
> **Basis:** Stated (Fitts's Law: time-to-target depends on size and distance → make buttons large
> and keep them close to the task/attention area). Numeric size floor enforced via A11Y-02.
> **Source:** [Laws of UX — Fitts's Law](https://lawsofux.com/fittss-law)

> **CTA-04** — For a signup/beta page, the primary action is repeated as the page gets long (a
> second CTA after the value is made), so a scrolling visitor always has the next step in reach.
> **Check:** On a long page, confirm the CTA recurs after the features/value section.
> **Severity:** MINOR
> **Basis:** Stated (Julian Shapiro's page template lists "Repeat your call-to-action" as a
> structural row; CXL corroboration unverified — see Sources attempted).
> **Source:** [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages)

> **CTA-05** — Any form is as short as possible; every field is justified. Cut fields that can be
> derived, deferred, or omitted (each removed field raises conversion).
> **Check:** Count fields; flag any not strictly needed for the beta/signup ask (for a waitlist,
> often just email).
> **Severity:** MAJOR
> **Basis:** Stated (NNG: "Every time you cut a field… you increase its conversion rate"; forms
> following guidelines get 78% vs 42% error-free first-try submissions).
> **Source:** [NNG — Website Forms Usability: Top 10 Recommendations](https://www.nngroup.com/articles/web-form-design)

> **CTA-06** — Form fields use a single-column layout, labels sit adjacent to their fields (not
> ambiguous placeholder-only labels), and the submit button is clearly the most prominent form
> action (no prominent Reset/Clear next to it).
> **Check:** Verify single column; visible persistent labels; one clear Submit; no
> equally-weighted Clear/Reset that risks accidental data loss.
> **Severity:** MAJOR
> **Basis:** Stated (NNG forms: single column; labels close to fields; avoid placeholder-as-label;
> "Avoid Reset and Clear buttons"; secondary actions must be less prominent than Submit).
> **Source:** [NNG — Website Forms Usability](https://www.nngroup.com/articles/web-form-design)

> **CTA-07** — The most compelling content (headline value prop + primary CTA) is above the fold,
> and the layout invites scrolling rather than presenting a full-bleed "false floor" that looks
> like the whole page.
> **Check:** First screenful carries the value prop and CTA; there is a visual cue that content
> continues below.
> **Severity:** MAJOR
> **Basis:** Stated (NNG: place most important content above the fold, "craft a layout that guides
> users to scroll," beware false floors).
> **Source:** [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles)

---

## 6. Accessibility as visual quality  (A11Y)

> **A11Y-01** — Text contrast meets WCAG 2.2 AA: **≥ 4.5:1** for normal text; **≥ 3:1** for large
> text (≥ 18pt, or ≥ 14pt bold — ≈ 24px / 18.5px bold). Thresholds are hard floors; do not round
> up (4.499:1 fails).
> **Check:** Sample foreground/background pairs with a contrast tool. Any body text < 4.5:1 (or
> large text < 3:1) = fail. Logos are exempt.
> **Severity:** BLOCK  *(see Red Flags — contrast below AA)*
> **Basis:** Stated (WCAG 2.2 SC 1.4.3, verbatim ratios and the no-rounding note).
> **Source:** [W3C — Understanding SC 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

> **A11Y-02** — Pointer targets (buttons, links-as-buttons, form controls) are at least **24×24
> CSS px**, or have sufficient spacing (a 24px-diameter circle centered on each undersized target
> does not intersect another target). Inline text links are exempt.
> **Check:** Measure interactive target boxes; small, tightly-packed controls fail.
> **Severity:** MAJOR
> **Basis:** Stated (WCAG 2.2 SC 2.5.8 Target Size (Minimum), verbatim 24×24 and the spacing
> exception). *(Best practice / mobile primary-CTA: aim higher.)*
> **Source:** [W3C — Understanding SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

> **A11Y-03** — Every keyboard-operable control has a visible focus indicator (focus state is not
> removed / `outline:none` with no replacement).
> **Check:** Tab through the page; each interactive element must show a visible focus indicator.
> **Severity:** MAJOR
> **Basis:** Stated (WCAG 2.2 SC 2.4.7 Focus Visible).
> **Source:** [W3C — Understanding SC 2.4.7 Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)

> **A11Y-04** — Non-text UI elements and meaningful graphics have **≥ 3:1** contrast against
> adjacent colors: control boundaries/states, focus indicators, icons, and parts of graphics
> needed to understand content.
> **Check:** Sample the contrast of button borders/fills, focus rings, and key icons vs. their
> neighbors. < 3:1 = fail.
> **Severity:** MAJOR
> **Basis:** Stated (WCAG 2.2 SC 1.4.11 Non-text Contrast: "have a contrast ratio of at least 3:1
> against adjacent color(s)").
> **Source:** [W3C — Understanding SC 1.4.11 Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)

> **A11Y-05** — Meaning and state are never conveyed by color alone; a text label, icon, or shape
> also carries the information.
> **Check:** Check error/success states, links, and required-field markers for a non-color cue.
> **Severity:** MAJOR
> **Basis:** Stated (Apple HIG: "Avoid relying solely on color… provide the same information in
> alternative ways"; corroborated by WCAG Use of Color principle referenced in 1.4.11).
> **Source:** [Apple HIG — Color](https://developer.apple.com/design/human-interface-guidelines/color) · [W3C — SC 1.4.11 Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)

> **A11Y-06** — Motion triggered by interaction — scroll-linked animation, parallax, a `whileInView`
> reveal — can be disabled, and the page is usable with it disabled. Two failures live here, and the
> second is invisible in a motion-on capture: motion that cannot be turned off at all, and a reveal
> whose RESTING state is `opacity: 0`, which renders the section BLANK for a reader whose system asks
> for reduced motion.
> **Check:** Render once with `prefers-reduced-motion: reduce`. Count elements still at computed
> `opacity: 0` after load, and elements still carrying a scroll-linked transform. Both counts are 0,
> or each exception is essential and named.
> **Severity:** BLOCK where content is unreachable (a section blank or unreadable with motion
> reduced); MAJOR where motion merely cannot be disabled.
> **Basis:** Stated (W3C, Understanding SC 2.3.3 Animation from Interactions; sufficient technique
> C39 `prefers-reduced-motion`. The page states no conformance level and none is asserted here.)
> **Source:** [W3C — SC 2.3.3 Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)

*[A11Y-06 added 2026-09-05 by `/workforce audit`, run `audit-20260906T040806Z`, on an escalation from
`presentation-critic`'s own Step 5c bar research. The gap it closes: the catalog carried **zero**
reduced-motion rules (`prefers-reduced-motion` / `reduced motion` / `forced-colors` all returned 0
hits), and `presentation-critic` may not invent a criterion — so it could not BLOCK on unguarded motion
no matter what it saw. Appended, never reworded into an existing row, per this catalog's own rule.
`presentation-designer`'s matching `## Verification` check landed in the same run, and this is the row
that lets the critic hold the line the designer's check draws.]*

---

## 7. "Amateur / AI-slop" design tells  (SLOP)  — a critic must catch and BLOCK

> **SLOP-01** — No image shows AI-generation artifacts or otherwise reads as obviously
> AI-generated: check text/typography inside images, hands, screens, glass/reflections, and
> background details for the characteristic errors.
> **Check:** Inspect each generated-looking image against NNG's list: text, hands, screens, glass
> reflections, background details. Visible artifacts = fail.
> **Severity:** BLOCK
> **Basis:** Stated — and note the nuance: NNG found AI imagery caused **no** trust penalty when
> undetected; the penalty attaches to *detectability* ("when participants… believed the imagery was
> AI-generated, they tended to also rate the site… less favorably"). So the rule is "no visible
> AI tells," not "no AI." NNG supplies the exact inspection list and five pre-use gates (purpose,
> representation, authenticity, AI errors, in-context crop).
> **Source:** [NNG — AI-Generated Images Can Perform as Well as Stock Photography](https://www.nngroup.com/articles/ai-generated-images)

> **SLOP-02** — The layout is not a generic, undifferentiated template: it reflects the specific
> product/brand rather than a stock hero + three-feature-icons skeleton that could belong to any
> company.
> **Check:** Ask "could this exact page be any SaaS?" If nothing visual or verbal ties it to *this*
> product/audience, fail.
> **Severity:** BLOCK  *(see Red Flags — generic undifferentiated layout)*
> **Basis:** Derived (owner hard gate), anchored to NNG (AI/tools "could easily end up making a
> homogenized design that looks generic"; imagery must reflect the specific brand) and NNG homepage
> principle 2 (differentiate, speak the audience's language).
> **Source:** [NNG — AI-Generated Images](https://www.nngroup.com/articles/ai-generated-images) · [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles)

> **SLOP-03** — No filler or placeholder copy/imagery ships: no "lorem ipsum," no "Welcome to our
> website" empty greeting, no generic stock standing in for real content.
> **Check:** Scan for lorem text, empty welcome headlines, and stock filler. Any = fail.
> **Severity:** BLOCK
> **Basis:** Stated (NNG: "cheerful 'welcomes'… do not provide any information… Transform these
> greetings into meaningful taglines"; generic stock is ignored).
> **Source:** [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles) · [NNG — Photos as Web Content](https://www.nngroup.com/articles/photos-as-web-content)

> **SLOP-04** — Visual "noise" and over-decoration tells are absent: inconsistent icon styles,
> mismatched illustration systems, gratuitous animation/motion, excessive shadows/borders, and
> too many fonts/colors.
> **Check:** Flag decoration with no informational value, autoplaying/parallax motion, and
> style-mixing. (Cross-ref IMG-05, TYP-05.)
> **Severity:** MAJOR
> **Basis:** Stated (NNG: minimize noise, avoid decoration-only elements; homepage principle 5:
> minimize motion/animation, keep it simple/standard; Refactoring UI: "Use fewer borders").
> **Source:** [NNG — Aesthetic & Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design) · [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles)

> **SLOP-05** — Empty/edge states are designed, not blank (e.g., a submitted-form or no-data state
> shows intentional content).
> **Check:** Trigger obvious empty states; a raw blank = fail.
> **Severity:** MINOR
> **Basis:** Stated (Refactoring UI chapter "Don't overlook empty states").
> **Source:** [Refactoring UI — table of contents](https://refactoringui.com/)

---

## 8. How professionals structure a design critique  (CRIT)  — process the evaluator should mirror

> **CRIT-01** — Run a **heuristic evaluation**: judge the page against a fixed, named set of
> heuristics (Nielsen's 10) rather than by unstructured opinion, and record each violation against
> the specific heuristic it breaks.
> **Check (process):** For each of the 10 heuristics, note pass/violation with evidence. The most
> relevant to a marketing/landing page: #2 Match the real world (plain language, no jargon), #4
> Consistency & standards (follow conventions; don't reinvent patterns), #6 Recognition over
> recall, #8 Aesthetic & minimalist design.
> **Severity:** process rule
> **Basis:** Stated (NNG's 10 Usability Heuristics; heuristics were designed for exactly this
> inspection method).
> **Source:** [NNG — 10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics)

> **CRIT-02** — Assess **first impression** explicitly: an aesthetic judgment forms in ~50ms, so
> evaluate what the first rendered screenful communicates before deeper analysis.
> **Check (process):** Capture the above-the-fold view first, and judge it as a distinct step: a
> verdict of pass or fail on what that first screenful communicates, with the reason in one
> sentence, and any defect it shows filed under its own catalog row and severity.
> **Severity:** process rule
> **Basis:** Stated (NNG: "users make an aesthetics-driven first impression… in the 50 milliseconds
> after landing… ~10x faster than the time it takes to read").
> **Source:** [NNG — Aesthetic & Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design)

> **CRIT-03** — Grade each rule against the **rendered** page (real DOM/screenshot at real
> viewports), not the source spec or intent; verify claims like contrast, target size, and line
> length by measurement, not eyeball alone.
> **Check (process):** Evidence for BLOCK-level findings must be a measured value or a screenshot
> region, not an assertion.
> **Severity:** process rule
> **Basis:** Derived, anchored to the WCAG understanding docs, which define conformance by measured
> computed values against thresholds.
> **Source:** [W3C — SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) · [W3C — SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

> **CRIT-04** — Separate **must-fix (BLOCK)** from polish (MAJOR/MINOR) and report findings by
> stable rule ID with evidence, so the same page grades consistently across reviews.
> **Check (process):** Output = list of {rule ID, pass/fail, severity, evidence}. Every BLOCK
> gates the ship decision.
> **Severity:** process rule
> **Basis:** Derived (evaluator-design convention; mirrors the pass/fail structure of the WCAG and
> heuristic sources above).
> **Source:** [NNG — 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics)

---

## 9. Messaging & marketing effectiveness  (MSG)

> **MSG-01** — The page communicates **what the product is and does** within seconds: a first-time
> visitor can state what it is, roughly who it's for, and why it matters from the first screenful.
> **Check (5-second test):** Show the above-the-fold view for ~5 seconds; a naive viewer should be
> able to say what the product is. If they can't, fail. (Related NNG thresholds: an aesthetic
> impression forms in ~50ms; the first ~10 seconds decide stay-or-leave.)
> **Severity:** BLOCK  *(see Red Flags — can't tell what it is / who it's for)*
> **Basis:** Stated (NNG: "you must clearly communicate your value proposition within 10 seconds";
> "failing to communicate a site's purpose at a glance causes potential customers to abandon";
> Julian's litmus test: "If the visitor reads only [the header], will they know exactly what you
> sell?").
> **Source:** [NNG — How Long Do Users Stay on Web Pages?](https://www.nngroup.com/articles/how-long-do-users-stay-on-web-pages) · [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles) · [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages)

> **MSG-02** — There is a clear **headline value proposition** above the fold — a descriptive
> headline (plus optional subheader) that answers "why choose this over alternatives?" — not a
> vague slogan.
> **Check:** The hero headline describes the offering/benefit specifically. Slogans like
> "Supercharge your workflow" with no concrete meaning = fail. Value prop absent or pushed below
> the fold = fail.
> **Severity:** BLOCK  *(see Red Flags — value prop absent or buried)*
> **Basis:** Stated (NNG: communicate unique value prop via tagline + hero, answering "Why should I
> choose this over others?"; Julian: bad headers "read like slogans instead of descriptions,"
> good ones are specific and benefit-describing).
> **Source:** [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles) · [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages)

> **MSG-03** — The page makes obvious **who it is for** (its target customer/audience) and speaks
> that audience's language (no internal jargon); for multi-audience products, it routes each
> audience.
> **Check:** Can a reader tell the intended audience? Look for audience-specific language or
> explicit segmentation (e.g., "For Job Seekers / For Businesses"). If the audience is never
> identifiable, fail.
> **Severity:** BLOCK  *(see Red Flags — audience never identified)*
> **Basis:** Stated (NNG: "speak the users' language… avoid jargon"; Robert Half "For Job Seekers /
> For Businesses" example; Julian's "choose your own adventure" persona routing; StoryBrand: the
> customer is the hero — center the message on who they are and what they want).
> **Source:** [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles) · [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages) · [Gravity Global — StoryBrand 7-Part Framework (secondary)](https://www.gravityglobal.com/blog/complete-guide-storybrand-framework)

> **MSG-04** — Messaging is **benefit-led and differentiated**: it leads with outcomes for the
> customer and states why this vs. alternatives, rather than a feature dump or self-congratulation.
> **Check:** Headline/first section frames customer benefit and differentiation. Pure
> feature/spec listing or "we're the best" copy with no benefit = fail. (Value Proposition Canvas
> lens: does the copy connect the offering to the customer's jobs, pains, and gains?)
> **Severity:** MAJOR
> **Basis:** Stated (Julian: "talk in terms of benefits to the visitor," not self-congratulation;
> NNG: emphasize unique value and differentiation, "What Sets Us Apart"; Strategyzer VPC: map
> offering to customer jobs/pains/gains).
> **Source:** [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages) · [NNG — Homepage Design](https://www.nngroup.com/articles/homepage-design-principles) · [Strategyzer — Value Proposition Canvas](https://www.strategyzer.com/library/the-value-proposition-canvas)

> **MSG-05** — The page presents a **sufficient, compelling primary CTA aligned to the audience's
> next step** — for a pre-launch/beta product, an appropriate low-friction ask (join beta / get
> early access / join waitlist), and it flows naturally from the value prop.
> **Check:** The CTA matches the funnel stage (a pre-launch page asking for a full purchase, or
> asking for nothing, = fail) and continues the headline's promise. (Structural mechanics in
> CTA-01..07.)
> **Severity:** BLOCK  *(see Red Flags — no clear/sufficient primary CTA)*
> **Basis:** Stated (Julian: the CTA is "the actionable next step to fulfilling the claim in your
> header," must be unmissable; StoryBrand: always "Call Them to Action" with a Direct CTA and a
> lower-commitment Transitional CTA — apt for a beta/waitlist "date me, don't marry me" ask).
> **Source:** [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages) · [Gravity Global — StoryBrand 7-Part Framework (secondary)](https://www.gravityglobal.com/blog/complete-guide-storybrand-framework)

> **MSG-06** — Copy reduces **confusion and labor**: every headline/section is self-evident and
> concise; the page doesn't over-assume prior knowledge or bury the ask in verbose messaging.
> **Check:** Apply Julian's `Purchase Rate = Desire − (Labor + Confusion)`: flag obscure/verbose
> messaging, unexplained jargon, and any point where the next action isn't self-evident. Julian's
> six reviewer questions (Conversion, Interest, Clarity, Expansion, Brevity, Disbelief) are a ready
> critique rubric.
> **Severity:** MAJOR
> **Basis:** Stated (Julian Shapiro: Desire − (Labor + Confusion); "Ensure every sentence can be
> easily understood… make it self-evident which action they should take next").
> **Source:** [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages)

> **MSG-07** — Social proof / credibility is present where doubt peaks (near the value prop and the
> CTA) — logos, customer counts, or press — appropriate to the product's stage.
> **Check:** Look for at least one credibility signal supporting the primary ask. (For pre-launch,
> honest signals only.)
> **Severity:** MINOR
> **Basis:** Stated (Julian's template includes a "Social proof" row directly under the hero).
> **Source:** [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages)

---

## RED FLAGS THAT MUST BLOCK  (hard-fail gate)

If any of these is true, the page must not ship. Each maps to a rule above.

1. **Missing / placeholder / blank / broken image** anywhere on the page. → **IMG-01**
2. **Recorded-but-un-applied brand palette** — brand colors exist in the spec/brand but the
   rendered page is generic default styling; the palette isn't applied consistently across the
   surface. → **COL-05**
3. **Generic, undifferentiated layout** — a template that could be any product, with nothing tying
   it to this product/audience. → **SLOP-02**
4. **Weak or absent primary CTA** — no single clear primary action, or competing/empty CTAs; for a
   beta page, no appropriate signup/waitlist ask. → **CTA-01 / MSG-05**
5. **Text contrast below WCAG AA** — body text < 4.5:1 or large text < 3:1. → **A11Y-01**
6. **A visitor can't tell what the product is or who it's for within seconds** (fails the 5-second
   test). → **MSG-01 / MSG-03**
7. **Value proposition absent or buried** — no clear headline value prop above the fold. → **MSG-02**
8. **Target customer / audience never identified.** → **MSG-03**
9. **Visible AI-generation artifacts / obvious lorem or stock filler** presented as real content.
   → **SLOP-01 / SLOP-03**

---

## Sources attempted but not verifiable

- **CXL** (`cxl.com/blog/value-proposition-examples-how-to-create`, and the landing-page/above-the-fold
  articles) — **blocked** by a Cloudflare "verify you are human" bot wall on fetch. Not cited as a
  verified source anywhere above. Its value-prop guidance (relevancy + quantified benefit +
  differentiation; headline readable in ~5s) is *consistent with* MSG-01/02/04 but is corroboration
  only, not a verified citation.
- **storybrand.com** (`/storybrand-clarify-your-message-new-version`) — fetch **timed out** (20s).
  The StoryBrand SB7 framework (customer = hero; brand = guide with empathy + authority; give a
  plan; Direct + Transitional CTA; success vs. failure stakes) is therefore cited through a
  corroborating **secondary** source (Gravity Global, a StoryBrand-certified agency's step-by-step
  writeup), **not** as a StoryBrand primary. Treat StoryBrand rules as framework-level guidance.
- **60-30-10 color rule** — no authoritative primary source located; commonly cited but it is an
  interior-design heuristic that migrated into UI blogs, and it is **not** in Refactoring UI's
  chapter list (verified against refactoringui.com). Marked Derived in COL-03; the discipline is
  carried by quote-backed Material 3 / Apple HIG rules.
- **Refactoring UI** — the book itself is paywalled; claims are cited only to what is verifiable on
  the public `refactoringui.com` page (its full chapter list and the on-page "use fewer borders" /
  "design with tactics, not talent" content). Chapter *titles* are treated as Stated; the internal
  detail of each chapter is not quoted.

---

## Source Ledger  (every source fetched for this catalog, 2026-08-26)

| Key | Title | Author / Org | Published | URL | Fetch |
|---|---|---|---|---|---|
| NNG-Heuristics | 10 Usability Heuristics for UI Design | J. Nielsen / NN/g | 1994 (upd. 2020) | https://www.nngroup.com/articles/ten-usability-heuristics | ok |
| NNG-Fpattern | F-Shaped Pattern of Reading on the Web | K. Pernice / NN/g | 2017 | https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content | ok |
| NNG-Aesthetic | Aesthetic & Minimalist Design (Heuristic #8) | T. Fessenden / NN/g | 2021 | https://www.nngroup.com/articles/aesthetic-minimalist-design | ok |
| NNG-Homepage | Homepage Design: 5 Fundamental Principles | H-H. Wang / NN/g | 2024 | https://www.nngroup.com/articles/homepage-design-principles | ok |
| NNG-Photos | Photos as Web Content | J. Nielsen / NN/g | 2010 | https://www.nngroup.com/articles/photos-as-web-content | ok |
| NNG-AIimages | AI-Generated Images Can Perform as Well as Stock | R. Banawa / NN/g | 2026 | https://www.nngroup.com/articles/ai-generated-images | ok |
| NNG-Forms | Website Forms Usability: Top 10 Recommendations | K. Whitenton / NN/g | 2016 | https://www.nngroup.com/articles/web-form-design | ok |
| NNG-Dwell | How Long Do Users Stay on Web Pages? | J. Nielsen / NN/g | 2011 | https://www.nngroup.com/articles/how-long-do-users-stay-on-web-pages | ok |
| WCAG-143 | Understanding SC 1.4.3 Contrast (Minimum) | W3C WAI | WCAG 2.2 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | ok |
| WCAG-258 | Understanding SC 2.5.8 Target Size (Minimum) | W3C WAI | WCAG 2.2 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | ok |
| WCAG-247 | Understanding SC 2.4.7 Focus Visible | W3C WAI | WCAG 2.2 | https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html | ok |
| WCAG-1411 | Understanding SC 1.4.11 Non-text Contrast | W3C WAI | WCAG 2.2 | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | ok |
| Baymard-LineLen | Readability: The Optimal Line Length | E. Scott / Baymard | 2022 | https://baymard.com/blog/line-length-readability | ok |
| Smashing-Type | 10 Principles of Readability & Web Typography | M. Cronin / Smashing | 2009 | https://www.smashingmagazine.com/2009/03/10-principles-for-readable-web-typography | ok |
| M3-Color | Color roles — Material Design 3 | Google | current | https://m3.material.io/styles/color/roles | ok |
| Apple-Color | Human Interface Guidelines — Color | Apple | current | https://developer.apple.com/design/human-interface-guidelines/color | ok |
| LoUX-VonRestorff | Von Restorff Effect | J. Yablonski / Laws of UX | current | https://lawsofux.com/von-restorff-effect | ok |
| LoUX-Fitts | Fitts's Law | J. Yablonski / Laws of UX | current | https://lawsofux.com/fittss-law | ok |
| RefactoringUI | Refactoring UI (public page + chapter list) | A. Wathan & S. Schoger | current | https://refactoringui.com/ | ok |
| Julian-LP | Startup Handbook: Landing Page Copywriting | J. Shapiro | current | https://www.julian.com/guide/startup/landing-pages | ok |
| Strategyzer-VPC | The Value Proposition Canvas | Strategyzer | 2026 | https://www.strategyzer.com/library/the-value-proposition-canvas | ok (thin) |
| StoryBrand-2nd | StoryBrand 7-Part Framework (secondary) | Gravity Global | 2021 | https://www.gravityglobal.com/blog/complete-guide-storybrand-framework | ok |
| NNG-GetStarted | "Get Started" Stops Users | NN/g | — | https://www.nngroup.com/articles/get-started | search-cited (not fetched) |
| CXL-VP | Unique Value Proposition (how to create) | CXL | — | https://cxl.com/blog/value-proposition-examples-how-to-create/ | blocked (bot wall) |
| StoryBrand-1st | Clarify Your Message (primary) | StoryBrand | — | https://storybrand.com/storybrand-clarify-your-message-new-version/ | timeout |

*Note on NNG-GetStarted: the "Get Started stalls users / generic CTA" claim (CTA-02) is corroborated
by the fetched NNG-Homepage source ("Click Here / Learn More" anti-guidance); the dedicated
"Get Started Stops Users" article surfaced in discovery search but was not separately fetched.*

---

## 10. Brief fidelity & art-direction match  (BF)  — machine-appended

<!-- Appended 2026-08-28 (run design-hero-gen-20260828) at owner direction. Growth region per the
     header rule; no existing row above is reworded. -->

> **BF-01** — The rendered surface satisfies the SPECIFIC art-direction brief it was commissioned
> under — not only the generic rules above. When the work order names a target style, a referenced
> artist (or a meld of artists), a required medium, or a specified mood, the output must READ AS THAT.
> A surface that passes every generic rule but does not match the brief it was asked for is a FAIL.
> **Check:** Obtain the commissioning art-direction brief (from the work order / dispatch: the named
> style, artist reference(s), medium, mood). Where the brief cites reference images, open them and
> compare side by side with the rendered surface. If the brief said "in the style of X" or "a meld of
> X and Y" and a reasonable viewer would not recognize X (or the meld), fail. If a required medium was
> specified (e.g. painterly, NOT flat-vector) and the output is a different medium, fail. Name the exact
> brief element missed and the evidence (the reference vs the render).
> **Severity:** BLOCK — a surface that answers the wrong brief wastes the commission regardless of polish.
> **Basis:** Derived — owner directive 2026-08-28 ("if I ask for something like that, it should be part
> of the reviewing agent's job to notice that"); anchored to § 8 CRIT (a professional critique grades
> against the stated objective, never a generic checklist alone).
> **Source:** owner directive 2026-08-28 + § 8 CRIT (this catalog).

<!-- Appended 2026-09-04 (run home-rebuild-20260903-08-place) at CEO direction, applying the amendment
     drafted in run home-rebuild-20260903-03-design (presentation-critic OUTPUT.md § Uncatalogued finding,
     restated in OUTPUT-2.md). Growth region per the header rule; no existing row above is reworded. -->

> **MSG-08** — *When the page's copy speaks in the first person ("I", "me", "my") to make its ask, the
> rendered surface identifies the speaker: a name and role (and optionally a portrait or signature)
> placed where the ask is made, not only in a footer.*
> **Check:** Count first-person speaker pronouns in `main`. If ≥ 1 and the page renders no name/byline/
> portrait for that speaker within the band that carries the ask (or immediately beside the primary CTA),
> fail.
> **Severity:** MAJOR (a personal ask from an unnamed person is a credibility gap that suppresses the
> conversion the page exists for; it does not by itself make the page unusable).
> **Basis:** Derived — review run `home-rebuild-20260903-03-design`, 2026-09-04; anchored to MSG-07
> (Julian Shapiro's "Social proof" row under the hero) and StoryBrand's guide-with-authority beat (the
> Gravity Global secondary already cited for MSG-03/MSG-05): a guide the customer cannot identify has no
> authority to lend.
> **Source:** `.codex-workforce/work/home-rebuild-20260903-03-design/presentation-critic/OUTPUT.md` and
> `OUTPUT-2.md` (that run) · [Julian Shapiro — Landing Pages](https://www.julian.com/guide/startup/landing-pages) · [Gravity Global — StoryBrand 7-Part Framework (secondary)](https://www.gravityglobal.com/blog/complete-guide-storybrand-framework)


<!-- Appended 2026-10-08 (the direction release) at operator direction. Growth region per the header
     rule; no existing row above is reworded. The title line was broadened from "Marketing / Landing /
     Beta-Signup Pages" to "Rendered Interfaces" in the same change, because the catalog is now read
     against app screens too — and the rules that describe an app screen by the JOB it does live in the
     sibling `ergonomics-catalog.md`, keyed by situation, rather than being restated here. -->

> **BF-02** — *A surface that ships UI has a design record (`.codex-workforce/design/direction.md`), and the
> render matches the references and the choices that record names.* No record on a UI-shipping surface
> is a FINDING, not a pass: it means the direction step was skipped and the surface was designed from
> model memory rather than from the case at hand.
> **Check:** Read `.codex-workforce/design/direction.md` for the surface under review BEFORE grading it. Absent
> → report BF-02 and name `/ui-design direct <surface>` as the remedy; grade the rest of the catalog
> normally, since a missing record does not excuse any other rule. Present → compare the render against
> it item by item: the layout skeleton, density, button style, palette roles and type scale it says are
> borrowed must be recognisable in the render; the things it says are deliberately NOT borrowed must be
> absent; and the `ERG-` rules it names for that screen's situation must all be graded. A render that
> matches no chosen reference, or that reproduces something the record refuses, is a FAIL. A pattern
> the render needs and the record does not cover is reported as a component pass owed
> (`direct --component <pattern>`), at MINOR.
> **Severity:** MAJOR — a surface built with no recorded direction is the generic-page failure SLOP-02
> catches after the fact, reported where it can still be acted on. BLOCK where the record exists and
> the render contradicts it, which is BF-01's severity for the same reason: a surface that answers the
> wrong brief wastes the commission regardless of polish.
> **Basis:** Derived — operator direction 2026-10-08 ("making sure to document the choices for future
> use"); anchored to BF-01 (grade against the specific brief, never the generic checklist alone) and to
> § 8 CRIT (a critique with no agreed objective is baseless).
> **Source:** operator direction 2026-10-08 · `references/direction.md` (the record's template and the
> step that writes it) · `references/ergonomics-catalog.md` (the situation keys and the `ERG-` rules) ·
> § 10 BF-01 and § 8 CRIT (this catalog)
