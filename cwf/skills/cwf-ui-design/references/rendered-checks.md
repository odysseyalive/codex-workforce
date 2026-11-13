<!-- ui-design-ref-version: 2 -->
<!-- ui-additions-version: 1 -->
<!-- SEED CONTRIBUTION. Materialized 2026-09-10 from the workforce distribution's shipped
     ui-design-seed.md (version anchor 1), carrying ONLY what design-quality-catalog.md does not
     already cover — evaluators.md item 3b: the existing built catalog is canonical and the seed
     contributes new entries, never a replacement. What the seed added and this file therefore
     holds: the RESPONSIVE LAYOUT category (absent from the carried catalog, which covers line
     length and target size but not reflow, breakpoints, or horizontal overflow), the declared-vs-
     rendered slot enumeration, and the required-checks report block. Everything the seed states
     about missing art, applied theme, contrast, hierarchy, and default-design tells is ALREADY in
     design-quality-catalog.md (IMG-01, COL-05, A11Y-01..04, VH-01..07, SLOP-01..04) and is NOT
     duplicated here; a second canonical text is the failure this note exists to prevent. -->
# Rendered checks — the seed contribution

**Evaluate the RENDERED result, not the source.** A passing test suite asserts structure, and
structure is exactly what these checks look past. The failure this file exists for is a page that
satisfies every automated assertion and is still wrong to look at.

---

## RC-01 — Declared vs rendered: enumerate the slots BEFORE grading them

*Every media slot, state, and element a shipped view DECLARES must be listed, and each must be
marked rendered or not rendered, before any subjective assessment begins.*

**Check:** Read the view's source for what it declares — image slots, empty states, conditional
regions, named sections. Render it. Produce the two-column list. A declared slot that renders
blank, broken, placeholder, or as its own alt text is a **FAIL** (this routes to `IMG-01` in
`design-quality-catalog.md` for its severity).
**Severity:** BLOCK — inherits IMG-01.
**Basis:** Derived — a rule written against a thing that exists cannot fire on its absence, so the
absent element has to be enumerated into existence before the catalog can see it.
**Why this exists, measured.** A design gate returned `PASS-WITH-NOTES` on six consecutive builds
of one page while the principal rejected all six: its five image rules all passed on a page with
**zero images**. Absence of art read as a deliberate empty stage. It is not — a shipped view with
a hole in it ships the hole. Separately, a missing card image once passed a full suite of 451
end-to-end tests, because the tests asserted the card's *structure* and never asked whether the
image inside it resolved.

```
Declared-vs-rendered: [pass / FAIL]
- Declared slots: [n]  Rendered: [n]  Not rendered: [list, or none]
```

---

## RC-02 — Reflow at 320 CSS pixels

*Content is presented without loss of information or functionality, and without requiring scrolling
in two dimensions, at a width equivalent to 320 CSS pixels.*

**Check:** Render at 320 px wide. The page body must not scroll horizontally. Exceptions apply only
to parts of the content that genuinely require two-dimensional layout — images required for
understanding, maps, diagrams, video, games, presentations, data tables — and the exception covers
**only that section**: a table may scroll inside its own container, but the heading, search field,
and pagination around it must still reflow.
**Severity:** MAJOR (BLOCK where non-excepted running text requires two-dimensional scrolling).
**Basis:** Stated. W3C SC 1.4.10 Reflow (AA): "without requiring scrolling in two dimensions for
vertical scrolling content at a width equivalent to 320 CSS pixels… Except for parts of the content
which require two-dimensional layout for usage or meaning." 320 CSS px is a 1280 px viewport at
400% zoom.
**Source:** https://www.w3.org/WAI/WCAG21/Understanding/reflow.html

## RC-03 — Reflow, not shrink

*Content reflows or relocates to fit a smaller viewport; it is not scaled down to fit.* Adjusting
or relocating a section is not a loss of information — content scaled below legibility is.
**Severity:** MAJOR
**Basis:** Stated (same source: "Neither adjusting or relocating content is considered a loss of
information or functionality, so long as users are still able to access the content").
**Source:** https://www.w3.org/WAI/WCAG21/Understanding/reflow.html

## RC-04 — Breakpoints exist and do something

*The layout changes between desktop and phone: multi-column regions collapse, navigation
consolidates.* A layout byte-identical from 1280 px to 390 px made no responsive decision.
**Severity:** MAJOR

## RC-05 — Wide content is contained, images are bounded

*Tables, code blocks, and diagrams scroll inside their own container rather than widening the page;
no image exceeds its column and forces the body wide.*
**Severity:** MAJOR
**Basis:** Stated — the same source's advisory technique C37 (CSS `max-width`/`height` to fit
images), and its Figure 11/12 pair: a video player without `max-width: 100%` produces a page-level
horizontal scrollbar that makes a reader hunt for off-screen content that does not exist.
**Source:** https://www.w3.org/WAI/WCAG21/Understanding/reflow.html

## RC-06 — Sticky chrome does not eat the zoomed viewport

*Headers, footers, and floating elements that are fixed at desktop width become static or
dismissible at small widths.* Fixed chrome at 320 px both obscures focused elements and takes the
space the content needs.
**Severity:** MINOR (MAJOR where it obscures a focused control)
**Basis:** Stated (same source, § Focus Not Obscured overlap; advisory technique C34).
**Source:** https://www.w3.org/WAI/WCAG21/Understanding/reflow.html

---

## Required report block

Emit this verbatim at the top of every design verdict. A missing line is not a pass.

```
### Required Checks
Declared-vs-rendered: [pass / FAIL] — [slots not rendered, or none]
Theme check:          [applied / DEFAULT] — [named palette / type / spacing decisions]  (COL-05)
Accessibility check:  [pass / flags] — [contrast ratios computed, focus visible y/n]     (A11Y-01..04)
Responsive check:     [pass / flags]
- Tested widths:        [e.g. 320 / 390 / 768 / 1280]
- Horizontal overflow:  [none / at which widths]
```

**A view with any declared-vs-rendered FAIL or a DEFAULT theme is not shippable, whatever the other
checks found.** Those two are the failures that read as success — the page renders, the tests pass,
and it is still wrong.
