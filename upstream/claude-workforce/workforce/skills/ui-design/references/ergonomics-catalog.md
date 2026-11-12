<!-- ui-design-ref-version: 2 -->
<!-- AUTHORED HERE 2026-10-08, cited from sources fetched that day (Source Ledger at the end).
     Keyed by SITUATION — the job the user is doing on the screen — because the carried catalog
     `design-quality-catalog.md` covers marketing/landing pages and had no rule for any app-screen
     situation: an app workspace was graded against rules that do not describe it. Nothing here
     restates a row that file already carries; where the two meet, this file CROSS-REFERENCES the
     existing ID (§ What the existing catalog already covers) and adds only what it does not say.
     GROWTH IS APPEND-ONLY and happens at the END of this file, in § Growth region. No rule above
     that region is ever reworded; a situation this catalog does not cover is searched during
     `direct` and the cited result is appended there. -->
# Ergonomics catalog — rules keyed to the job a screen does

**Purpose.** A cited, checkable catalog of ergonomic and design-theory rules for **app screens**, keyed
to the situation the screen is in rather than to the theory it comes from. The reviewer reaches a rule
by classifying the screen, not by remembering a law. `direct` reads it before a build to pull the
layout patterns a situation leads to; `review` reads it after to grade the screen against the situation
the project's design record names.

**How to read a rule.** Each rule is a block with a stable ID (`ERG-<SITUATION>-NN`) the evaluator cites
in its findings, in the same format the sibling catalog uses:

> **ID** — *checkable assertion (pass/fail against a rendered page)*
> **Check:** what to look at on the rendered page, and how.
> **Severity:** BLOCK (hard fail / must not ship) · MAJOR · MINOR.
> **Basis:** **Stated** = the source says this directly (quote-backed). **Derived** = the source
> supports the principle and the specific rule is an inference anchored to the nearest support.
> **Source:** a real URL that was fetched for this catalog.

**Severity convention.** BLOCK is reserved for a failure the source itself names as a WCAG Level A/AA
failure. Everything ergonomic but not an accessibility failure is MAJOR or MINOR, which keeps this file
aligned with the A11Y section of the sibling catalog and with its RED FLAGS gate.

**Verification note.** Every URL cited below was fetched with a browser tool on 2026-10-08. Two fetches
failed; they are listed in the Source Ledger and nothing is cited from them.

## What the existing catalog already covers

`design-quality-catalog.md` is canonical for everything in this list, and no rule below repeats it:

| Already covered there | Rules | How this file relates |
|---|---|---|
| Visual hierarchy and layout on a page | VH-01..VH-07 | the LAND rules add only the size-step count, the squint test and the false floor |
| Reading measure as a target | TYP-02 (50-75 characters) | ERG-READ-01 adds the WCAG 80-character hard ceiling above that target |
| Signup form shape and CTA placement | CTA-05, CTA-06, CTA-07 | ERG-FORM-02 generalizes the single-column rule from signup forms to every app form |
| Messaging and copy effectiveness | MSG-01..MSG-08 | not touched here; a situation never overrides a messaging rule |
| Empty and edge states | SLOP-05 | ERG-JOB rules cover the *waiting* state, which is not an empty state |
| Contrast, focus, target size | A11Y-01..A11Y-04 | cited again only where a situation makes a specific failure checkable |

A finding that fits a row above is reported against that row's ID. Reporting it twice, once per
catalog, doubles the count of a single defect.

## Classifying a screen

A screen is classified by **the job the user is doing on it**, never by its components: a table can be
triage, comparison, or a dashboard. Ask these in order; every "yes" adds a situation. A screen usually
has one **primary** situation, which decides the layout pattern, and zero or more **secondary** ones,
whose rules still apply.

| Question | If yes |
|---|---|
| Is the viewer not yet a user, and is the page's job to explain an offering and convert? | LAND |
| Does the user type or pick values that are then submitted? | FORM |
| Is there a set of incoming items, each needing an individual decision or routing? | TRIAGE |
| Did the user start a process they do not control and must wait on, then review its result? | JOB |
| Does the screen show updated aggregate state the user checks at a glance to spot deviations, without acting on each item? | DASH |
| Is the user choosing one of a small set (2-5) of mutually exclusive options that differ on several attributes? | COMPARE |
| Is the main content prose meant to be read in sequence? | READ |
| Does the screen change persistent preferences or system behaviour rather than task data? | SET |

**Tie-breakers.**

- DASH against TRIAGE: if the user acts on individual rows it is TRIAGE; if they read the aggregate and
  drill down it is DASH. An alert list on a dashboard is DASH primary, TRIAGE secondary.
- COMPARE against TRIAGE: COMPARE ends in one choice among few options; TRIAGE processes many items,
  each to its own outcome.
- SET against FORM: SET is a persistent preference, FORM a one-off submission. A settings page with a
  Save button is both, and ERG-SET-01 decides whether toggles are allowed on it.

**Common combinations.** Pricing page = LAND + COMPARE. Checkout = FORM + COMPARE. An upload flow is
FORM then JOB, so the screen changes situation after submit. An ops console = DASH + TRIAGE. A
documentation page = READ, plus SET when it carries display preferences. An onboarding wizard = staged
FORM + SET.

---

## LAND — landing and marketing page

### LAND principles

1. **Visual hierarchy.** "Refers to the organization of the design elements on the page so that the eye
   is guided to consume each design element in the order of intended importance."
2. **Attention concentrates at the top.** "Users spent about 57% of their page-viewing time above the
   fold. 74% of the viewing time was spent in the first two screenfuls." And: "Beware of false floors."
3. **Von Restorff (isolation) effect.** "When multiple similar objects are present, the one that differs
   from the rest is most likely to be remembered" — so "use restraint when placing emphasis".
4. **Aesthetic-usability effect.** "Users often perceive aesthetically pleasing design as design that's
   more usable." Polish buys tolerance, and it can also mask usability problems in review.
5. **Jakob's law.** "Users spend most of their time on other sites. This means that users prefer your
   site to work the same way as all the other sites they already know."
6. **Hick's law.** "The time it takes to make a decision increases with the number and complexity of
   choices" — so "avoid overwhelming users by highlighting recommended options."

### LAND layout patterns

- Hero with a single primary action, then benefit bands in layer-cake rhythm (heading plus short body
  per band), the primary action repeated near the end. Principles 1-3; CTA-01 and CTA-04 there.
- Conventional chrome — logo top-left, nav top, footer links bottom — so effort goes to the offer rather
  than to learning the page. Principle 5.
- A highlighted recommended option wherever a choice is offered, which hands off to COMPARE.

### LAND rules

> **ERG-LAND-01** — *No more than two elements in the first viewport are rendered at the largest scale
> step — the headline and at most one other.*
> **Check:** at 1440x900 and 390x844, list elements by rendered font size and area, then count those
> sitting at the top size step.
> **Severity:** MAJOR. **Basis:** Stated ("Limit how many elements are big to a maximum of 2").
> **Source:** [NN/g — Visual hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)

> **ERG-LAND-02** — *The squint test passes: blurred 5-10px, the intended primary element is still the
> most prominent shape in the first viewport.*
> **Check:** blur the first-viewport screenshot (5px, then 10px Gaussian) and name the element the eye
> lands on. It must be the headline or the primary CTA, not an image or a secondary block.
> **Severity:** MAJOR. **Basis:** Stated (the squint test is described as the check for hierarchy).
> **Source:** [NN/g — Visual hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)

> **ERG-LAND-03** — *The first viewport presents no false floor: where content continues below the fold,
> something visibly signals it.*
> **Check:** at 1440x900 and 390x844, inspect the bottom edge of the first viewport. A full-bleed hero
> that ends exactly at the fold with nothing crossing it fails; cut-off text, a partial card or a scroll
> cue passes.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Scrolling and attention](https://www.nngroup.com/articles/scrolling-and-attention/)

> **ERG-LAND-04** — *Isolation emphasis — accent colour, outline, badge, motion — is used on at most one
> element per viewport, and never by colour alone.*
> **Check:** per viewport screenshot, count the elements given a distinct emphasis treatment, then
> confirm each also differs by shape, weight, or label.
> **Severity:** MINOR. **Basis:** Derived, from "use restraint" plus the WCAG rule against colour alone.
> **Source:** [Laws of UX — Von Restorff](https://lawsofux.com/von-restorff-effect/) · [WCAG 2.2 — Use of colour](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)

---

## FORM — data entry

### FORM principles

1. **Recognition rather than recall.** "Information required to use the design (e.g. field labels or
   menu items) should be visible or easily retrievable when needed."
2. **Visible, associated labels.** "Most users prefer or even need visible labels to understand the
   form", and labels above the fields "helps reduce horizontal scrolling for people with low vision and
   mobile device users."
3. **Single column.** "Using a single-column layout ensures users only have one direction to go in while
   filling in information and scanning it"; two or three inputs on a line are acceptable only when they
   "logically belonged to the same single entity."
4. **One thing per page.** "Asking just one question per question page helps users understand what
   you're asking them to do"; staged disclosure is "useful when you can divide a task into distinct
   steps that have little interaction."
5. **Error prevention and recovery.** Validate when the user leaves the field, avoid "premature
   validation", and "the error message must live update on a keystroke level". Messages are "expressed
   in plain language (no error codes)".
6. **Defaults.** "Pre-populate fields with the most common value if you can determine it in advance."

### FORM layout patterns

- A single-column form, labels above the fields, grouped sections under headings, with a small gap from
  label to field and a larger gap between groups. Principles 2 and 3, plus Gestalt proximity.
- A question-page wizard: back link at the top, one question or tight group per page, a left-aligned
  continue action, then a check-answers summary with per-section change links before the final submit.
- A long single page with section anchors, where users must move back and forth between interdependent
  parts — staged disclosure "is problematic when the steps are interdependent".

### FORM rules

> **ERG-FORM-01** — *Every input carries a persistent visible label, not a placeholder alone, placed
> above or left of a text input and right of a checkbox or radio, and programmatically associated.*
> **Check:** screenshot each field empty and filled; the label stays visible when the field has a
> value. In the DOM each control has a `<label for>`, a wrapping label, or `aria-labelledby`.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [W3C WAI — Form labels](https://www.w3.org/WAI/tutorials/forms/labels/)

> **ERG-FORM-02** — *Fields run in a single column; a row holds two or three fields only when they form
> one entity — date parts, city/state/postcode, card expiry with security code, name parts.*
> **Check:** at desktop width, look for two or more independent fields side by side.
> **Severity:** MAJOR. **Basis:** Stated. Generalizes CTA-06 from signup forms to every app form.
> **Source:** [Baymard — Avoid multi-column forms](https://baymard.com/research-articles/avoid-multi-column-forms)

> **ERG-FORM-03** — *Validation is inline and well timed: focusing an empty field shows no error;
> leaving a field with an invalid value shows an error beside it before submit; correcting the value
> clears the error as the user types.*
> **Check:** focus then blur an empty required field, expecting an error on blur and none on focus; type
> an invalid value and blur, expecting an adjacent error; then fix it keystroke by keystroke and watch
> the error clear without a blur.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [Baymard — Inline form validation](https://baymard.com/research-articles/inline-form-validation)

> **ERG-FORM-04** — *Required fields and errors are not identified by colour alone: an icon, text, or
> explicit "required"/"(optional)" wording accompanies any red border or red label.*
> **Check:** render the error state and view it in greyscale; the erroring field must still be
> identifiable. Check the required/optional marking the same way.
> **Severity:** BLOCK. **Basis:** Stated — WCAG failure F81 is "identifying required or error fields
> using color differences only".
> **Source:** [WCAG 2.2 — Use of colour](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)

> **ERG-FORM-05** — *Error messages say what is wrong and how to fix it, in plain words, with no error
> codes.*
> **Check:** trigger each validation error and read the text. "Invalid input" or "Error 422" fails;
> "Enter a date in the past, like 27 3 2007" passes.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Ten usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)

> **ERG-FORM-06** — *A multi-page form carries a back link at the top of each step, a primary continue
> button, and a check-answers summary with per-section change links before the final submit, whose
> button names its action rather than reading "Submit".*
> **Check:** walk the flow. On the review page, every answered section is listed with a change link that
> returns to it with the values pre-filled.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [GOV.UK — Question pages](https://design-system.service.gov.uk/patterns/question-pages/) · [GOV.UK — Check answers](https://design-system.service.gov.uk/patterns/check-answers/)

---

## TRIAGE — working a queue of incoming items

### TRIAGE principles

1. **Flexibility and efficiency of use.** "Shortcuts — hidden from novice users — may speed up the
   interaction for the expert user", and the design should "allow users to tailor frequent actions".
2. **Find, compare, view, act.** A table must support finding records by criteria, comparing data,
   viewing or editing one row, and acting on records; "the (default) first column should be a
   human-readable record identifier"; "there should be a clear visual indication that filters are
   active."
3. **Keep the queue in view while working an item.** In list-detail, "selection of a list item updates
   the detail pane"; a modal instead "will cover adjacent records in the table and the user won't be
   able to reference or copy data from a similar record."
4. **Batch actions.** "Once an item from the table is selected, the batch action bar appears at the top
   of the table", which "can increase user efficiency compared to the effort of repetitively performing
   the same inline action."
5. **Fitts's law.** "The time to acquire a target is a function of the distance to and size of the
   target", so actions belong next to the item they act on, at a usable size.
6. **Visualize work and limit work in progress.** "WIP limits are critical for exposing bottlenecks in
   the workflow and maximizing flow."

### TRIAGE layout patterns

- Inbox list plus detail pane — list at a fixed width, detail flexible; on a narrow screen the detail
  replaces the list and a back action returns to it. Principles 3 and 5.
- A selectable data table with a batch action bar and a filter/search toolbar, plus a nonmodal side
  panel for a single record. Principles 2 and 4.
- Kanban columns, one per workflow state, with a card count and WIP limit in each header, where triage
  means moving items through stages. Principle 6.

### TRIAGE rules

> **ERG-TRIAGE-01** — *Each row or card shows, without being opened, a human-readable identifier in the
> leading position, plus its status and its age or priority.*
> **Check:** screenshot the list; for three rows, confirm the leading field is readable text rather than
> an opaque ID, and that status and age or priority are visible on the row itself.
> **Severity:** MAJOR. **Basis:** Stated for the identifier; Derived, from recognition over recall, for
> the status and age on the row.
> **Source:** [NN/g — Data tables](https://www.nngroup.com/articles/data-tables/) · [NN/g — Ten usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)

> **ERG-TRIAGE-02** — *When a filter, search, or sort is applied, the list says so visibly and offers a
> one-step clear.*
> **Check:** apply a filter and screenshot. Active filter chips or a "Filtered: N of M" line, and a
> clear control, must be visible without opening a menu.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Data tables](https://www.nngroup.com/articles/data-tables/)

> **ERG-TRIAGE-03** — *Items are multi-selectable, a selection reveals a batch action bar with the
> selection count and a deselect control, per-row actions number at most two inline with the rest in an
> overflow menu, and every action target is at least 24x24 CSS px or meets the spacing exception.*
> **Check:** select two rows and screenshot the bar; measure the row action targets in the inspector.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [Carbon — Data table guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines) · [WCAG 2.2 — Target size minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)

> **ERG-TRIAGE-04** — *At expanded width — about 840 CSS px and wider — opening an item shows it beside
> the still-visible list with the selected row highlighted, never in a modal that covers the list; at
> narrow width the detail replaces the list and a back control returns to it.*
> **Check:** at 1440 px and 390 px wide, open an item and screenshot each.
> **Severity:** MAJOR. **Basis:** Stated for the behaviour; the 840 px breakpoint is Derived from
> Material's "expanded" window class.
> **Source:** [Material — Canonical layouts](https://developer.android.com/develop/ui/compose/layouts/adaptive/canonical-layouts) · [NN/g — Data tables](https://www.nngroup.com/articles/data-tables/)

> **ERG-TRIAGE-05** — *Row status indicators combine at least two of colour, shape, and symbol plus a
> text label, and the screen uses no more than five or six distinct indicator kinds.*
> **Check:** take a greyscale screenshot of the list — statuses must stay distinguishable — then count
> the distinct indicator kinds.
> **Severity:** MAJOR, and BLOCK where colour is the only cue (WCAG 1.4.1). **Basis:** Stated.
> **Source:** [Carbon — Status indicators](https://www.carbondesignsystem.com/building-blocks/core/patterns/status-indicators) · [WCAG 2.2 — Use of colour](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)

> **ERG-TRIAGE-06** — *On a kanban board, each column header shows its card count, and where a WIP limit
> exists the column shows the limit and is visibly flagged when over it.*
> **Check:** screenshot the board and read each header.
> **Severity:** MINOR. **Basis:** Derived — the source states WIP limits are the mechanism and does not
> specify the visual treatment.
> **Source:** [Atlassian — Kanban boards](https://www.atlassian.com/agile/kanban/boards)

---

## JOB — a long-running job the user waits on

### JOB principles

1. **Visibility of system status.** "The design should always keep users informed about what is going
   on, through appropriate feedback within a reasonable amount of time."
2. **Response-time limits.** 0.1 s feels instant, 1 s keeps flow, and "anything slower than 10 seconds
   needs a percent-done indicator as well as a clearly signposted way for the user to interrupt the
   operation."
3. **Match the indicator to the wait.** "Use a looped indicator for delays of 2-9 seconds and a
   percent-done indicator for delays of 10 seconds or more"; of static "Loading..." indicators, "don't
   use them". Material adds: under 200 ms no indicator, 200 ms to 5 s a loading indicator, over 5 s a
   progress indicator, and for a very long wait "consider allowing people to navigate away".
4. **Doherty threshold.** "Provide system feedback within 400 ms in order to keep users' attention."
5. **Status trackers.** "Present the latest update prominently, so users can find it first"; "show
   previous updates, as well as the current update", in plain language rather than backend codes.
6. **Goal-gradient effect.** "Provide a clear indication of progress in order to motivate users to
   complete tasks."
7. **Status messages reach assistive technology.** A status message carries information "on the waiting
   state of an application, on the progress of a process, or on the existence of errors" and must be
   programmatically determinable without taking focus.

### JOB layout patterns

- A stepper with a persistent status panel: named stages, the current one marked, one determinate bar
  for the active stage, and cancel beside it. Principles 2, 3 and 6.
- An upload queue: a drop zone, then a per-file list with one overall indicator for the group and
  per-file state only where files are independently actionable.
- A job detail page shaped as a status tracker: the latest status card on top, dated history below it
  newest first, and a notify-me or leave-this-page affordance for a long wait. Principle 5.
- A result review screen: a summary of what was produced, errors listed with their fixes, and one clear
  next action. SLOP-05 there still governs the empty case.

### JOB rules

> **ERG-JOB-01** — *The control that starts a job changes visibly at once — pressed or disabled state,
> or an inline spinner — and the page does not rely on a "don't click twice" warning.*
> **Check:** click the start control and capture a frame within about 400 ms; scan the copy for
> do-not-click-again style warnings.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Progress indicators](https://www.nngroup.com/articles/progress-indicators/) · [Laws of UX — Doherty threshold](https://lawsofux.com/doherty-threshold/)

> **ERG-JOB-02** — *An operation running longer than about 10 s shows a determinate indicator — percent,
> bytes, or "item 3 of 50" — with text saying what is happening; an indefinite spinner or a static
> "Loading..." alone fails.*
> **Check:** run the long job, throttling the network if needed, and screenshot at 2 s, 12 s and 30 s.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Progress indicators](https://www.nngroup.com/articles/progress-indicators/) · [NN/g — Response times](https://www.nngroup.com/articles/response-times-3-important-limits/) · [Material — Progress indicators](https://m3.material.io/components/progress-indicators/guidelines)

> **ERG-JOB-03** — *Any operation longer than about 10 s has a visible cancel or stop control next to
> its progress indicator.*
> **Check:** screenshot during the job and locate the control.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Response times](https://www.nngroup.com/articles/response-times-3-important-limits/)

> **ERG-JOB-04** — *A job's status view shows the latest status first and most prominently, keeps earlier
> updates with timestamps below it, and words every status in plain language rather than a backend code.*
> **Check:** open a job mid-run and again after completion; read the status text and the history order.
> A status reading "FULFILLED" or "state=3" fails.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Status trackers](https://www.nngroup.com/articles/status-tracker-progress-update/)

> **ERG-JOB-05** — *Work on a group of items shows one overall indicator for the group; a per-item
> indicator appears only for an item the user can act on separately.*
> **Check:** start a multi-file job and count the simultaneous progress indicators.
> **Severity:** MINOR. **Basis:** Stated.
> **Source:** [Material — Progress indicators](https://m3.material.io/components/progress-indicators/guidelines)

> **ERG-JOB-06** — *Progress, completion, and failure text is exposed as a status message — `role="status"`,
> `role="alert"`, `role="log"`, `aria-live`, or a progressbar with a live value — rather than only drawn.*
> **Check:** inspect the DOM around the progress and result text for a live region or a role.
> **Severity:** MAJOR, keyed to WCAG 2.2 AA 4.1.3 and the A11Y section's severities. **Basis:** Stated.
> **Source:** [WCAG 2.2 — Status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages)

---

## DASH — monitoring dashboard

### DASH principles

1. **At a glance, on one screen.** A dashboard is "a single-page view that imparts at-a-glance
   information on which users can act quickly", and "their goal is not to facilitate exploration."
2. **Preattentive encoding.** "We are quite adept at estimating how lengths compare, and we can also
   accurately estimate position in a 2D space", while pie, donut, gauge, treemap and 3D charts are
   "difficult to interpret quickly or accurately."
3. **Colour for category, never alone, never for magnitude.** "Color should not be used to communicate
   information about quantitative values or magnitude", and colour is never the only visual means of
   conveying information.
4. **Overview first, zoom and filter, then details on demand** — Shneiderman's visual
   information-seeking mantra, cited here through a secondary source because the primary paper's PDF
   could not be fetched.
5. **Severity consolidation.** "When multiple statuses are consolidated, use the highest-attention color
   to represent the group", and "having more than five or six indicators can overwhelm users."
6. **Aesthetic and minimalist design.** "Every extra unit of information in an interface competes with
   the relevant units of information."

### DASH layout patterns

- A KPI strip, then trend charts, then a drill-down table — summary before detail, top to bottom.
- An operational status grid: tiles per service or asset, severity-sorted alerts pinned top-left, and a
  consolidated status per group. Principles 1 and 5.
- An analytical board: a global filter bar above a small set of bar, line and bullet charts that all
  respond to it. Principles 2 and 4.

### DASH rules

> **ERG-DASH-01** — *The headline metrics or statuses the dashboard exists for are all visible in the
> first viewport at 1440x900, with no scrolling, tabbing, or hovering.*
> **Check:** screenshot the first viewport, list the headline metrics the page title or the design record
> names, and confirm each is visible.
> **Severity:** MAJOR. **Basis:** Derived — single-page at-a-glance is Stated, the viewport size is this
> catalog's house choice.
> **Source:** [NN/g — Preattentive dashboards](https://www.nngroup.com/articles/dashboards-preattentive/)

> **ERG-DASH-02** — *Quantities meant to be compared are drawn with length or 2D position — bar, line,
> bullet, scatter — and no pie, donut, radial gauge, treemap, or 3D chart compares values; a pie showing
> one overwhelming share is the only exception.*
> **Check:** inventory the chart types on the page.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Preattentive dashboards](https://www.nngroup.com/articles/dashboards-preattentive/)

> **ERG-DASH-03** — *Status and category are never encoded by colour alone, colour never encodes
> magnitude, and a delta carries a sign, caret, or arrow.*
> **Check:** take a greyscale screenshot; every status, series and delta must still be readable.
> **Severity:** BLOCK. **Basis:** Stated — WCAG 1.4.1 Level A, plus Carbon's rule that a differential
> indicator "must have either a '+' or '-' sign, a caret, or an arrow".
> **Source:** [WCAG 2.2 — Use of colour](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color) · [Carbon — Status indicators](https://www.carbondesignsystem.com/building-blocks/core/patterns/status-indicators)

> **ERG-DASH-04** — *Every chart has a title, labelled axes with units, and shows the full range of its
> scale or the target it is judged against.*
> **Check:** read each chart. A gauge or bar with no visible scale range fails.
> **Severity:** MAJOR. **Basis:** Derived — the source faults example charts because they "fail to show
> the overall range of the scale".
> **Source:** [NN/g — Preattentive dashboards](https://www.nngroup.com/articles/dashboards-preattentive/)

> **ERG-DASH-05** — *A group or rollup indicator shows the worst underlying status, and the screen shows
> no more than five or six distinct status indicator kinds.*
> **Check:** find a rollup with mixed children and compare it to them; count the indicator kinds.
> **Severity:** MINOR. **Basis:** Stated.
> **Source:** [Carbon — Status indicators](https://www.carbondesignsystem.com/building-blocks/core/patterns/status-indicators)

> **ERG-DASH-06** — *The overview carries summaries, and raw record-level detail sits behind a drill-down
> — a link, an expand, or a side panel — rather than in the first viewport.*
> **Check:** confirm the first viewport holds no full raw data table, and that each summary tile or chart
> offers a way to its detail.
> **Severity:** MINOR. **Basis:** Derived via a secondary source for the mantra.
> **Source:** [Hipertext.net (UPF) — quoting Shneiderman's mantra](https://arxiu-web.upf.edu/hipertextnet/en/numero-3/busqueda_ri.html) · [NN/g — Preattentive dashboards](https://www.nngroup.com/articles/dashboards-preattentive/)

---

## COMPARE — choosing between options

### COMPARE principles

1. **Compensatory decision-making needs a table.** "When people have to select among a small set of
   alternatives (usually under 5-7), they usually engage in compensatory decision making", which "is
   best served by comparison tables."
2. **Choice overload.** "When comparison is necessary, we can avoid choice overload by enabling
   side-by-side comparison of related items and options that require a decision."
3. **Keep the labels in view.** "Keep column headers fixed as users scroll. Human short-term memory is
   limited, and users will easily forget which column is for which product."
4. **Adjacency.** "Two adjacent data points are easy to compare because... users don't need to either
   move their eyes much or store information in their working memory."
5. **Highlight the recommended option**, which is Hick's law and the isolation effect acting together.
6. **Progressive disclosure of attributes.** "Consider presenting a simplified table with those
   attributes you expect will be most important to users, but also allow access to a more detailed
   table."

### COMPARE layout patterns

- Options as columns in a comparison table, with a sticky header row, zebra or bordered rows, and a
  show-differences-only toggle. Principles 1, 3 and 4.
- Three or four tier cards with one recommended tier, followed by a compare-all-features table.
- A compare tray: a checkbox on a listing collects up to N items into a comparison page.
- On a phone, two columns side by side, or columns converted to tabs, accepting weaker comparison.

### COMPARE rules

> **ERG-COMPARE-01** — *Options are columns and attributes are rows, with row labels on the left, option
> names as column headers, and consistent alignment within each column.*
> **Check:** screenshot the table at desktop width.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Comparison tables](https://www.nngroup.com/articles/comparison-tables/)

> **ERG-COMPARE-02** — *No more than five options are compared at once, a larger set is narrowed by
> filter or selection first, and on a phone at least two options stay visible side by side or the table
> becomes tabs.*
> **Check:** count the columns at 1440 px and at 390 px.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Comparison tables](https://www.nngroup.com/articles/comparison-tables/)

> **ERG-COMPARE-03** — *Where the table is taller than the viewport, the option header row stays visible
> while scrolling.*
> **Check:** scroll to the bottom third of the table and screenshot; the option names must be on screen.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Comparison tables](https://www.nngroup.com/articles/comparison-tables/)

> **ERG-COMPARE-04** — *Every attribute is filled for every option, equivalent values are worded
> identically across columns, and symbol-only cells sit in visibly delineated rows.*
> **Check:** scan for blank or "N/A" cells where other columns carry data, and for playful variants of
> one value — the "Zip / Zero / Zilch / Nada" failure.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Comparison tables](https://www.nngroup.com/articles/comparison-tables/)

> **ERG-COMPARE-05** — *A comparison longer than about two screenfuls lets the user collapse attribute
> groups or show only the differences.*
> **Check:** look for a differences-only toggle or collapsible row groups.
> **Severity:** MINOR. **Basis:** Stated.
> **Source:** [NN/g — Comparison tables](https://www.nngroup.com/articles/comparison-tables/)

> **ERG-COMPARE-06** — *At most one option is marked as recommended, and the mark carries a text label
> such as "Most popular" rather than colour or elevation alone.*
> **Check:** count the emphasized options, then check the mark in greyscale.
> **Severity:** MINOR. **Basis:** Derived.
> **Source:** [Laws of UX — Hick's law](https://lawsofux.com/hicks-law/) · [Laws of UX — Von Restorff](https://lawsofux.com/von-restorff-effect/) · [WCAG 2.2 — Use of colour](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)

---

## READ — reading and long content

### READ principles

1. **Layer-cake scanning.** "Aside from reading almost every word, the layer-cake pattern is by far the
   most effective way in which users can scan pages", and a wall of text is answered "by chunking your
   content into sections and bulleted lists, by using meaningful subheadings."
2. **The F-pattern is a failure mode.** "In the absence of subheadings and bullets, users tend to fixate
   on the words toward the beginning of lines and toward the top of the page."
3. **Inverted pyramid.** "Start content with the most important piece of information so readers can get
   the main point, regardless of how much they read."
4. **Line length.** WCAG 1.4.8: "width is no more than 80 characters or glyphs (40 if CJK)"; Butterick:
   "aim for an average line length of 45-90 characters, including spaces."
5. **Spacing and alignment.** "Text is not justified"; line spacing is "at least space-and-a-half within
   paragraphs, and paragraph spacing is at least 1.5 times larger than the line spacing"; text resizes
   to 200% without horizontal scrolling to read a line.

### READ layout patterns

- A single text column at reading measure, centred or left-weighted, with a sticky table-of-contents
  rail on wide screens. Principles 1 and 4.
- An article head of title, a one-paragraph summary or key-points list, then the body. Principle 3.
- A supporting pane for references, comments or glossary beside the text on wide screens and below it on
  narrow ones — "for expanded width, give 70% of the space to the main content, 30% to the supporting
  content".

### READ rules

> **ERG-READ-01** — *Body text lines are no longer than 80 characters at every viewport width, targeting
> 45-75.*
> **Check:** at 1920 px and 1440 px, count the characters on three full body lines, or divide the
> container width by the average glyph width.
> **Severity:** MAJOR. **Basis:** Stated. This is the hard ceiling above TYP-02's target range.
> **Source:** [WCAG 2.2 — Visual presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation) · [Butterick — Line length](https://practicaltypography.com/line-length.html)

> **ERG-READ-02** — *Body text is not justified to both margins.*
> **Check:** the computed `text-align` on body paragraphs is not `justify`, and the right edge is
> visibly ragged.
> **Severity:** MAJOR. **Basis:** Stated — WCAG failure F88.
> **Source:** [WCAG 2.2 — Visual presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation)

> **ERG-READ-03** — *Body line-height is at least 1.5, and the space between paragraphs is visibly larger
> than the space between lines.*
> **Check:** compare the computed `line-height` to `font-size` on body paragraphs, then compare the
> paragraph margin to it.
> **Severity:** MINOR. **Basis:** Stated, and used here as a design target — WCAG 1.4.8 is AAA and
> permits a user mechanism instead.
> **Source:** [WCAG 2.2 — Visual presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation)

> **ERG-READ-04** — *No screenful of body content at 1440x900 lacks a descriptive subheading, list,
> figure, or other structural break.*
> **Check:** scroll the article one viewport at a time; any viewport of unbroken paragraphs fails. A
> heading must describe its content — "Pricing changes in 2027" — rather than label it, as "Overview"
> does.
> **Severity:** MAJOR. **Basis:** Derived.
> **Source:** [NN/g — Text scanning patterns](https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/)

> **ERG-READ-05** — *The first paragraph, or a summary block above it, states the main point.*
> **Check:** read only the title and the first paragraph; the article's conclusion must be recoverable
> from them.
> **Severity:** MINOR. **Basis:** Stated.
> **Source:** [NN/g — Inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/)

> **ERG-READ-06** — *At 200% browser zoom in a 1280 px window, reading a line of body text never needs
> horizontal scrolling.*
> **Check:** zoom to 200% and read; horizontal scrolling to finish a line fails.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [WCAG 2.2 — Visual presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation)

---

## SET — settings and configuration

### SET principles

1. **Good defaults, few settings.** "Aim to provide default settings that give the best experience to
   the largest number of people", and "minimize the number of settings you offer"; users "rarely utilize
   fancy customization features, making it important to optimize the default user experience."
2. **Task options in context, general options in settings.** "Prefer letting people modify task-specific
   options without going to your settings area."
3. **Toggles act immediately.** "Toggle switches should take immediate effect and should not require the
   user to click Save or Submit", and controls that produce instant results are separated "from those
   that require clicking a command button."
4. **Progressive disclosure for advanced options.** "Designs that go beyond 2 disclosure levels
   typically have low usability because users often get lost when moving between the levels."
5. **Stable, oriented navigation.** "Use a noncustomizable toolbar that remains visible and always
   indicates the active toolbar button", because "people rely on a stable settings interface"; and
   "restore the most recently viewed pane."
6. **Consistency, standards, and error prevention.** "Follow platform and industry conventions", and
   "present users with a confirmation option before they commit to the action."

### SET layout patterns

- A category list with a settings pane: categories at the left with the active one marked, grouped
  controls under headings at the right, and on narrow screens the categories then a pane with a back
  control. Principle 5.
- An instant section separated from a form section: toggles that apply immediately in one group, fields
  that need Save in another with its own Save button and a saved confirmation. Principle 3.
- An "Advanced" disclosure at the bottom of a pane, and a visually separated danger zone for
  destructive settings, with confirmation. Principles 4 and 6.

### SET rules

> **ERG-SET-01** — *Toggle switches apply on change with visible feedback, and no toggle shares a group
> with a Save or Submit button that governs it; a deferred choice uses a checkbox or radio instead.*
> **Check:** flip a toggle and watch for an immediate state change or confirmation; look for a Save
> button in the same group.
> **Severity:** MAJOR. **Basis:** Stated.
> **Source:** [NN/g — Toggle-switch guidelines](https://www.nngroup.com/articles/toggle-switch-guidelines/)

> **ERG-SET-02** — *Toggle labels are short, keyword-first statements that make sense with "on" or "off"
> appended — no questions, no neutral wording — and the state reads from knob position plus a
> high-contrast colour rather than colour alone.*
> **Check:** read the labels aloud with "on/off" appended, then take a greyscale screenshot of a toggle
> in each state.
> **Severity:** MINOR. **Basis:** Stated.
> **Source:** [NN/g — Toggle-switch guidelines](https://www.nngroup.com/articles/toggle-switch-guidelines/) · [WCAG 2.2 — Use of colour](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)

> **ERG-SET-03** — *Settings are grouped into labelled categories, the category navigation stays visible
> while a pane is shown and marks the active category, and the pane title matches it.*
> **Check:** open two categories and screenshot each.
> **Severity:** MAJOR. **Basis:** Derived — the source states this for macOS settings windows and it is
> generalized here to the web.
> **Source:** [Apple HIG — Settings](https://developer.apple.com/design/human-interface-guidelines/settings)

> **ERG-SET-04** — *Rarely used or advanced settings sit behind a clearly labelled disclosure, and no
> setting is more than two disclosure levels deep.*
> **Check:** count the clicks from the settings landing to the deepest setting.
> **Severity:** MINOR. **Basis:** Stated.
> **Source:** [NN/g — Progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/)

> **ERG-SET-05** — *Every setting shows its current value at rest — a selected option, a filled field, a
> toggle position — and none renders blank or as an unselected control group.*
> **Check:** screenshot each pane on first load for a fresh account.
> **Severity:** MINOR. **Basis:** Derived.
> **Source:** [Apple HIG — Settings](https://developer.apple.com/design/human-interface-guidelines/settings) · [NN/g — The power of defaults](https://www.nngroup.com/articles/the-power-of-defaults/)

> **ERG-SET-06** — *Destructive or hard-to-reverse settings are visually separated from routine ones and
> require a confirmation step, and a Save action produces a visible, programmatically exposed
> confirmation.*
> **Check:** locate the destructive controls — delete account, reset, revoke keys — and trigger one as
> far as its confirmation; save a form-type setting and inspect for a status message.
> **Severity:** MAJOR. **Basis:** Derived.
> **Source:** [NN/g — Ten usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) · [WCAG 2.2 — Status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages)

---

## Counts, and what this catalog does not cover

- Situations: 8 — LAND, FORM, TRIAGE, JOB, DASH, COMPARE, READ, SET — plus the classification section.
- Rules: 46, distributed LAND 4, FORM 6, TRIAGE 6, JOB 6, DASH 6, COMPARE 6, READ 6, SET 6. Of those, 36
  are Stated and 10 Derived.
- Gaps measured while building it, named so a reader does not take silence for coverage. Shneiderman's
  mantra is cited through a secondary source, both copies of the 1996 primary paper having been blocked.
  Keyboard shortcuts for triage are supported only in general terms by heuristic 7, so no checkable rule
  was written. Kanban WIP flagging is Derived because the source defines the limits and not their visual
  treatment. The LAND rules are deliberately few, since the sibling catalog covers landing pages in
  depth.

## Growth region — a situation this catalog does not cover

**Append-only, and it is the only place this file grows.** A screen whose situation none of the eight
above describes is researched during `direct`: the search is run, the source is fetched, and the new
situation or rule is appended HERE with its own Basis tag and a fetched URL, under a dated marker
naming the run. No rule above this heading is ever reworded, exactly as the sibling catalog's header
rule requires. A rule appended without a fetched source is not a rule; it is an opinion with an ID.

*Nothing appended yet.*

## Source Ledger — every source fetched 2026-10-08

| # | Source | URL | Status |
|---|---|---|---|
| 1 | NN/g — Ten usability heuristics | https://www.nngroup.com/articles/ten-usability-heuristics/ | fetched |
| 2 | NN/g — Progressive disclosure | https://www.nngroup.com/articles/progressive-disclosure/ | fetched |
| 3 | NN/g — Preattentive dashboards | https://www.nngroup.com/articles/dashboards-preattentive/ | fetched |
| 4 | NN/g — Progress indicators | https://www.nngroup.com/articles/progress-indicators/ | fetched |
| 5 | NN/g — Response times, three limits | https://www.nngroup.com/articles/response-times-3-important-limits/ | fetched |
| 6 | NN/g — Status trackers | https://www.nngroup.com/articles/status-tracker-progress-update/ | fetched |
| 7 | NN/g — Comparison tables | https://www.nngroup.com/articles/comparison-tables/ | fetched |
| 8 | NN/g — Data tables | https://www.nngroup.com/articles/data-tables/ | fetched |
| 9 | NN/g — Text scanning patterns | https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/ | fetched |
| 10 | NN/g — Inverted pyramid | https://www.nngroup.com/articles/inverted-pyramid/ | fetched |
| 11 | NN/g — Scrolling and attention | https://www.nngroup.com/articles/scrolling-and-attention/ | fetched |
| 12 | NN/g — Visual hierarchy | https://www.nngroup.com/articles/visual-hierarchy-ux-definition/ | fetched |
| 13 | NN/g — Toggle-switch guidelines | https://www.nngroup.com/articles/toggle-switch-guidelines/ | fetched |
| 14 | NN/g — The power of defaults | https://www.nngroup.com/articles/the-power-of-defaults/ | fetched |
| 15 | Baymard — Inline form validation | https://baymard.com/research-articles/inline-form-validation | fetched after redirect |
| 16 | Baymard — Avoid multi-column forms | https://baymard.com/research-articles/avoid-multi-column-forms | fetched after redirect |
| 17 | GOV.UK — Question pages | https://design-system.service.gov.uk/patterns/question-pages/ | fetched |
| 18 | GOV.UK — Check answers | https://design-system.service.gov.uk/patterns/check-answers/ | fetched |
| 19 | W3C WAI — Form labels | https://www.w3.org/WAI/tutorials/forms/labels/ | fetched |
| 20 | WCAG 2.2 — Visual presentation | https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation | fetched |
| 21 | WCAG 2.2 — Status messages | https://www.w3.org/WAI/WCAG22/Understanding/status-messages | fetched |
| 22 | WCAG 2.2 — Use of colour | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color | fetched |
| 23 | WCAG 2.2 — Target size minimum | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum | fetched |
| 24 | Carbon — Data table guidelines | https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines | fetched after redirect |
| 25 | Carbon — Status indicators | https://www.carbondesignsystem.com/building-blocks/core/patterns/status-indicators | fetched after redirect |
| 26 | Material 3 — Progress indicators | https://m3.material.io/components/progress-indicators/guidelines | fetched |
| 27 | Material — Canonical adaptive layouts | https://developer.android.com/develop/ui/compose/layouts/adaptive/canonical-layouts | fetched |
| 28 | Apple HIG — Settings | https://developer.apple.com/design/human-interface-guidelines/settings | fetched |
| 29 | Atlassian — Kanban boards | https://www.atlassian.com/agile/kanban/boards | fetched |
| 30 | Laws of UX — Fitts's law | https://lawsofux.com/fittss-law/ | fetched |
| 31 | Laws of UX — Hick's law | https://lawsofux.com/hicks-law/ | fetched |
| 32 | Laws of UX — Jakob's law | https://lawsofux.com/jakobs-law/ | fetched |
| 33 | Laws of UX — Law of proximity | https://lawsofux.com/law-of-proximity/ | fetched |
| 34 | Laws of UX — Doherty threshold | https://lawsofux.com/doherty-threshold/ | fetched |
| 35 | Laws of UX — Choice overload | https://lawsofux.com/choice-overload/ | fetched |
| 36 | Laws of UX — Von Restorff effect | https://lawsofux.com/von-restorff-effect/ | fetched |
| 37 | Laws of UX — Aesthetic-usability effect | https://lawsofux.com/aesthetic-usability-effect/ | fetched |
| 38 | Laws of UX — Goal-gradient effect | https://lawsofux.com/goal-gradient-effect/ | fetched |
| 39 | Butterick — Line length | https://practicaltypography.com/line-length.html | fetched |
| 40 | Hipertext.net (UPF) — secondary for Shneiderman's mantra | https://arxiu-web.upf.edu/hipertextnet/en/numero-3/busqueda_ri.html | fetched |
| F1 | Shneiderman 1996, Utrecht copy | https://webspace.science.uu.nl/~telea001/uploads/VACourse/Shneiderman96.pdf | blocked — not cited |
| F2 | Shneiderman 1996, UMD copy | https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf | blocked — not cited |

Totals: 40 fetched, 2 blocked and cited from neither.
