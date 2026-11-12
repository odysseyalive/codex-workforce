<!-- ui-design-ref-version: 2 -->
<!-- AUTHORED HERE 2026-10-08. The procedure for `/ui-design direct`, the half of this skill that runs
     BEFORE the first UI build. Everything dated "verified 2026-10-08" below was loaded that day with a
     browser tool; a source list ages, and the date is what tells a later reader to re-check rather than
     to trust. The pick belongs to the user, so the step that presents candidates runs where
     `AskUserQuestion` exists — the main session — and an employee that reaches it returns `QUESTION:`
     with the shortlist instead of choosing. -->
# Direction — the step that runs before the first UI build

**What it is for.** `review` and `sweep` grade a page that already exists, so the earliest they can
speak is after the build, when the remedy they can ask for is a reskin. Nothing gathered references,
asked about the case, or picked a direction first, so the builder designed from model memory and landed
on the model's average page. `direct` is that missing step: it reads the project's own stack, asks only
what the project does not already answer, classifies each screen by the job it does, searches for real
references that fit both the stack and that job, hands the pick to the user, and writes the choices
down where the next build and the next `review` can both read them.

**Uniqueness comes from the inputs for the case at hand** — the questions, the references, the theory
that fits this job — and from nothing else. No step here compares this project's design to another
project's. That was offered and the user rejected it: *"It's not about comparing project to project.
That's not practical, it's about asking the right questions to pull in specific direction for the case
at hand."*

**The skill owns mechanism; the person running it owns judgment.** Reading the stack, running the
searches, capturing the candidates, resolving the ergonomics catalog and writing the record are
mechanism. Which candidates are best for this case, and which principles govern this screen, are
judgment. **The pick itself belongs to the user.**

**The design record lives at `.claude/design/direction.md` in the project.** It is agent-facing
context, it travels with the project beside the org, and it stays out of the project's own docs tree.

## When `direct` runs, and how often

- **Once per surface type.** The marketing site is one surface; each app workspace is another. A
  project with a marketing site and two module workspaces runs `direct` three times.
- **`direct --component <pattern>` once per new pattern** a later build needs and the record does not
  cover yet — data table, upload flow, step bar, kanban, diff.
- **On request, any time.** A user asking for a new direction re-runs it, and the new entry is appended
  to the record beside the old one rather than replacing it.

## Step 1 — Read the project before asking it anything

Read these first, and ask only about what none of them answers. The question budget is small and every
question the project already answered is an interruption that buys nothing.

1. **The CSS stack and component library**, from the project's own files — the table below.
2. **Existing tokens or theme files** — a palette, a type scale, CSS custom properties, a Tailwind theme
   block, a `<Theme>` wrapper's accent and radius.
3. **An existing project direction**, which is INPUT and is never overwritten: a design lead's palette,
   a project's own `CATALOG-ANCHOR.md` house rules, a graphic system file, a brand guide.
4. **The project's purpose and audience**, from its README, its own docs, and its org chart.

### Detecting the CSS stack from project files

Check in this order; more than one can be true, because shadcn implies Tailwind and daisyUI implies
Tailwind. The most specific match wins for the search order.

| Stack | Signals |
|---|---|
| shadcn/ui | `components.json` at the repo root with `"$schema": "https://ui.shadcn.com/schema.json"`; `components/ui/*.tsx`; deps `class-variance-authority`, `tailwind-merge`, `clsx`, `lucide-react`, plus `@radix-ui/react-*` or `@base-ui-components/react` |
| Chakra UI v3 | dep `@chakra-ui/react`; v3 snippets also live in `components/ui/`, so that directory alone is not proof of shadcn — require `components.json` |
| daisyUI | dep `daisyui`; `@plugin "daisyui";` in Tailwind v4 CSS; `plugins: [require("daisyui")]` in a v3 config; a `daisyui` CDN link |
| Flowbite | deps `flowbite`, `flowbite-react`, `flowbite-svelte`, `flowbite-vue`; `@plugin "flowbite/plugin"` or the config plugin |
| Preline | dep `preline`; a `preline` CSS import or plugin entry |
| Headless UI | deps `@headlessui/react` or `@headlessui/vue`, usually with Tailwind; Catalyst files under `components/` |
| Radix Themes | dep `@radix-ui/themes`; `import "@radix-ui/themes/styles.css"`; a `<Theme>` wrapper. Distinct from Radix Primitives (`@radix-ui/react-*`), which signal shadcn or custom |
| MUI | deps `@mui/material`, `@mui/joy`, `@mui/x-data-grid`, `@mui/x-charts`, usually with `@emotion/react` |
| Mantine | deps `@mantine/core`, `@mantine/hooks`; `postcss-preset-mantine` in the PostCSS config |
| Bootstrap | deps `bootstrap`, `react-bootstrap`, `bootstrap-vue-next`, `@ng-bootstrap/ng-bootstrap`; `@import "bootstrap/scss/bootstrap"`; a jsDelivr Bootstrap 5 CDN link; a `bootstrap` gem |
| Bulma | dep `bulma`; `@use "bulma/sass"` or a `bulma.css` import; a `bulma` CDN link |
| Tailwind, plain | deps `tailwindcss`, `@tailwindcss/vite`, `@tailwindcss/postcss`, `@tailwindcss/cli`; a v3 `tailwind.config.*`; v4 has no config file, so look for `@import "tailwindcss";` in CSS; `cdn.tailwindcss.com`; `tailwindcss-rails`; `django-tailwind` |
| Plain CSS | none of the above in `package.json`, lockfiles, CSS imports, HTML `<link>` tags, `Gemfile`, `pyproject.toml`, `requirements.txt` or `composer.json`. Classless libraries such as `@picocss/pico` and `open-props` count as plain CSS for the search |

**A server-rendered project may pull its framework from a CDN with no manifest entry at all**, so also
scan `templates/**/*.html`, `layouts/*`, `*.erb`, `*.blade.php` and `*.jinja` for `<link>` and `<script>`
tags before concluding plain CSS.

## Step 2 — Ask the case questions

**At most four questions, in ONE `AskUserQuestion` call, and only the ones step 1 left unanswered.**
Several calls in one message are presented newest-first (`platform.md` fact 26), so a set split across
calls is answered in reverse; one call keeps the order the questions were written in.

**The questions are about the case, not about the style.** Plain speech, one idea per question, the way
you would say it out loud:

- What is this surface for, in one sentence?
- Who uses it, and how often?
- On each screen, what is the main job — entering something, sorting a queue, watching something run,
  comparing options, reading, buying?
- How should it feel to the person using it?

**The CSS package is asked only when step 1 found none.** A project whose files name the stack is never
asked what its stack is.

**When step 1 found an inherited direction, whether it governs this surface is one of the four.** It is
a case question — see § Whether the inherited direction governs THIS surface is a case question — and
the answer decides whether the rest of the run constrains itself to that direction or supersedes it.

Four case questions plus the pick in step 5 is five interruptions on a fresh project, which is the
ceiling. A question the project's own files answer is over-asking, and the finish-don't-hedge directive
forbids it.

## Step 3 — Classify each screen into a situation

Run each screen through `ergonomics-catalog.md` § Classifying a screen and name its primary situation
and any secondary ones. Pull that situation's principles, its layout patterns, and the `ERG-` rules the
reviewer will later grade against; those rule IDs go into the record, so the build knows them before it
starts and `review` does not have to guess which ones applied.

**A screen whose situation the catalog does not cover triggers a search here**, and the cited result is
appended to that file's growth region — the same append-only growth rule `review` already carries.

## Step 4 — Search for references

**The package's own official sources come first**, because their markup is guaranteed to match the
project, then its licensed or community block libraries, then the stack-agnostic galleries for the
situation. Verify each candidate loads before offering it. Keep the best three or four.

**Free and loadable without a login is the only kind that gets captured.** A paid or login-walled source
is offered as a LINK ONLY, labelled paid or login-walled, and is never captured or scraped. Tailwind
Plus, Mobbin, Refero and the paid tiers of shadcnblocks and Flowbite are in that set; Refero's terms
forbid automated extraction outright, so it is linked and never fetched for capture.

**A reference from another stack is shortlisted for its pattern, and never for its markup.** The TRIAGE
row's "built references" clause allows it — shadcn/ui's Tasks example is the clearest table layout there
is, whatever the project is built in — so when one is shortlisted, **name a free same-stack source for
the markup beside it**. For a plain-Tailwind project borrowing that table, HyperUI
`hyperui.dev/components/application/tables` is the one to pair it with: loaded 2026-10-08, free, MIT, and
it ships a sticky-header table. In the record, that reference's tier is labelled for what it is —
"pattern reference, not this project's stack" — and the entry names the dependencies the project does not
have, so nobody later reads the pick as permission to install Radix.

### Source list per stack — verified 2026-10-08

| Stack | Free, loadable, capturable | Link only | Notes |
|---|---|---|---|
| shadcn/ui | `ui.shadcn.com/blocks` (`/blocks/<category>`), `ui.shadcn.com/examples/<name>` (tasks, dashboard), `ui.shadcn.com/docs/components/<name>`, the registry directory at `/docs/directory` | shadcnblocks Pro (`shadcnblocks.com/blocks/<slug>`; free browse, basic tier needs a login) | shadcn/ui is MIT. shadcnblocks' licence counts an AI-restyled copy as a Derivative, so a Pro block's markup never enters a project the user has not licensed |
| Tailwind, plain | HyperUI `hyperui.dev/components/{application,marketing,neobrutalism}/<category>`, Flowbite's free blocks, `tailwindcss.com/showcase` for real sites | Tailwind Plus (`tailwindcss.com/plus/ui-blocks/...`), Preline block pages (`preline.co/blocks/<group>/<subgroup>/`) | Preline's block pages are mostly Pro now: measured 2026-10-08, every block on `/blocks/forms/document-and-import-uploads/` and `/blocks/data-display/progress-cards/` carried a Pro label and the page's own "Free" filter button was disabled, and `/blocks/data-display/user-and-contact-tables/` opened on a Pro block. A Pro block is link-only. Capture a Preline block only when that page shows it as free; its library stays dual MIT plus a fair-use licence — no competing product, and a derivative template needs attribution. Tailwind Plus redirected every anonymous URL to its login |
| daisyUI | `daisyui.com/components/<name>/` | daisyUI Store (`daisyui.com/store/`, paid templates) | Store licence terms were not loaded; treat them as unknown rather than permissive |
| Flowbite | `flowbite.com/docs/components/<name>/`, the free subset of `flowbite.com/blocks/<area>/<category>/` | Flowbite Pro blocks and the admin preview | Library is MIT with attribution. The Pro EULA forbids standalone redistribution and builders |
| Headless UI | `headlessui.com/react/<component>` for behaviour; the visual layer comes from the Tailwind sources above | Tailwind Plus Catalyst | Headless UI ships no page-level gallery, so page-scale direction is a Tailwind search |
| Radix Themes | `radix-ui.com/themes/playground`, `radix-ui.com/themes/docs/components/<name>` | — | No official template or block gallery exists; page-scale direction comes from the stack-agnostic galleries and is then built with Radix components |
| MUI | `mui.com/material-ui/getting-started/templates/<name>/`, `mui.com/material-ui/react-<component>/`, the free Store items | paid MUI Store templates (`/store/previews/<slug>/`) | Core and the free templates are MIT. The Store's standard licence covers one End Product that is not itself sold, and forbids re-displaying the content in a gallery |
| Chakra UI | `chakra-ui.com/docs/components/<name>` | Chakra UI Pro blocks (`pro.chakra-ui.com/blocks/<slug>`) | `chakra-ui.com/blocks` is a 404: there is no free official blocks page |
| Mantine | `ui.mantine.dev/category/<slug>/`, the core docs | — | |
| Bootstrap | `getbootstrap.com/docs/5.3/examples/<name>/` | the relocated theme sellers | Bootstrap Themes is SUNSET — `themes.getbootstrap.com` redirects to an FAQ saying downloads closed in August 2025 and naming where the sellers went. Do not list it as a source |
| Bulma | `bulma.io/documentation/<section>/<name>/`, `bulmatemplates.github.io/bulma-templates/` (admin, inbox, kanban) | — | The community templates' licence was not checked |
| Plain CSS | `component.gallery/components/<name>/` for component scale, `html5up.net/<name>` for marketing pages | — | HTML5 UP is CC BY 3.0, so the credit stays unless the user holds the paid attribution-free tier. Component Gallery examples belong to the design systems they came from and are reference only |

### Stack-agnostic galleries — verified 2026-10-08

| Gallery | URL and pattern | Access | What it is good for |
|---|---|---|---|
| Land-book | `land-book.com/?search=<q>`, `/design/<type>?search=<q>` (landing-page, pricing-page, sign-up-page) | free browse, Pro for copying | marketing and pricing pages by industry |
| Lapa Ninja | `lapa.ninja/category/<slug>/`, `/search/?q=<q>` | free browse | landing pages; the search renders only in a browser |
| recent.design | `recent.design/websites`, detail at `/i/<id>-<slug>` | free | curated award-style sites. `godly.website` now redirects here |
| SaaS Landing Page | `saaslandingpage.com/technology/<tech>/`, `/tag/<tag>/`, `/pricing/` | free browse | the best stack filter for Tailwind and React landing pages |
| SaaSFrame | `saasframe.io/categories/<slug>` | free browse | real SaaS screens paired with written reasoning per category; the strongest fit for a situation search |
| Page Flows | `pageflows.com/post/desktop-web/<flow-type>/<app>/` | paid; step names readable anonymously | naming the steps of a flow before searching for screens |
| UI Patterns | `ui-patterns.com/patterns/<PatternName>` (case-sensitive) | free | naming the pattern before searching galleries; the example screenshots are dated |
| Dribbble | `dribbble.com/search/<q>` | free first page | last resort — mostly unshipped concept art, weighted below any shipped-product source |
| Awwwards | `awwwards.com/websites/<technology>/` | free browse | expressive marketing sites; a poor fit for app screens |
| Mobbin | `mobbin.com` | login-walled; free tier has no search | the best app-screen library there is, and it needs the user's own account or its MCP server |
| Refero | `refero.design/web-apps`, `/search?q=<q>` | free browse, MCP on paid plans | app screens by situation. Its terms forbid scraping and automated extraction, so it is LINKED and never captured |

### Search order for a real product screen of a situation

With no account and no MCP connected: SaaSFrame, then Refero as a link, then Page Flows for step names,
then Land-book or Lapa for marketing surfaces, then Dribbble last. With the user's own account or MCP,
Mobbin or Refero goes first.

| Situation | Where to look, best fit first | Search terms |
|---|---|---|
| LAND | Land-book `/design/landing-page`, SaaS Landing Page by technology, Lapa Ninja, recent.design, Awwwards for expressive work only | keep the stack filter on, so what comes back is buildable |
| FORM | SaaSFrame forms and onboarding, Refero "Adding & Creating" and "Signing Up & Onboarding", Page Flows onboarding, UI Patterns `/patterns/Wizard` | search for the domain object: "create invoice", "new project" |
| TRIAGE | Refero "Table" and "Filter & Sorting", SaaSFrame inbox and table categories, shadcn `/examples/tasks` as a built reference | inbox, issues list, support tickets, review queue |
| JOB | Refero "Uploading & Downloading", Page Flows import and export flows, Component Gallery progress components | import, export, deploy, build log, processing. Real-screen coverage is thin everywhere, so expect to fall back to component scale |
| DASH | SaaSFrame `/categories/dashboard`, Refero "Dashboard" and "Stats", Dribbble last | distinguish operational from analytical from navigation dashboards |
| COMPARE | Land-book `/design/pricing-page`, SaaS Landing Page `/pricing/`, shadcnblocks compare blocks, Refero "Billing & Plans" | plan comparison is covered well; side-by-side record comparison is a gap, and daisyUI's `diff` component is the component-scale fallback |
| READ | Land-book `/design/blog-post`, Lapa editorial, Tailwind Showcase for news and docs sites, Refero "Article & Text" | for docs-style reading, the showcase's documentation entries |
| SET | Refero "Profile & Account" and "Personalizing & Customizing", shadcn's settings dialog block, shadcnblocks settings blocks, Chakra Pro settings previews | |

### Request hygiene, and the three sources that moved

**Bot walls are real and intermittent, so a block is a skip and never a retry loop.** Measured
2026-10-08: Cloudflare challenged the second request to `lapa.ninja` and to `land-book.com`, and two
other galleries returned content with a blocked status. Keep requests per host low — one search page
plus at most three or four detail pages — and drop a blocked source from the shortlist instead of
trying it again.

**Prefer a real browser over a plain fetch for a JS-rendered gallery search.** Lapa's search renders
results only in a browser.

**Keep the trailing slash.** A plain fetch normalised `https://preline.co/blocks/` to `/blocks` and got
a 404, where the browser on `/blocks/` worked. On a 404, re-try the same URL in the browser with the
slash intact before calling the source dead.

**Three things moved since common knowledge.** `godly.website` redirects to `recent.design`. Bootstrap
Themes is sunset. Tailwind Plus redirects every anonymous URL to its login, so whether a human browser
sees previews there is unverified and the agent treats it as link-only.

## Step 5 — Present the candidates and take the pick

**Present them in the session artifact** (`session-artifact.md` § The single session artifact) as
screenshots with their links — one labelled entry per candidate, the stack and situation named, and one
line on what each would give this surface. The page is updated in place rather than replaced, and
successive rounds accumulate as a progression (`session-artifact.md` § Examples break out as a
progression), because the diff between rounds is the only thing that makes the direction reviewable.

### The review round, before the pick

**The candidates are for other people to look at too, so the step waits for them.** The user asked
for this directly: *"so are the suggestions going to include URL's for people to review and comment on
for ui direction?"* The URLs were already there; the loop that collects what people say about them is
this round.

1. **Every link opens the candidate itself.** A candidate's link is its own detail page or its
   full-size image — the screen being discussed. The gallery or category page it was found on is a
   second, clearly labelled "found on" link, never the primary one. A reviewer who clicks a category
   page lands on a hundred screens and has to guess which one the round is about.
2. **The session artifact holding the candidates IS the review copy.** There is no second page. It is
   **private until the user shares it** from the page's own Share menu with whoever should weigh in —
   nothing here can share it on their behalf — and **the reply says so**: the link, who it is for, and
   that commenting happens on the page.
3. **Read every comment on that artifact before asking for the pick.** That is the `ArtifactComments`
   tool in its `read` action; load it through `ToolSearch` first when it is deferred rather than
   present. Summarise what came back **per candidate**, in the reply and on the page itself, so the
   page carries the discussion beside the thing being discussed.
4. **The pick question offers two answers, not one.** "Pick now" and "hold for more comments" are both
   valid, and **holding is a real answer** — it ends the round without a decision. The next `direct`
   run on that surface re-reads the comments before it asks again, so a hold costs nothing but time.
5. **Comments are evidence and are quoted, never paraphrased.** They land in the design record's
   Review comments section, each verbatim with its author, beside the pick they informed.
6. **An employee that reaches this step returns `QUESTION:` with the comments as well as the
   shortlist** — the candidate names, their URLs, what each offers, and what anyone has already said
   about them. A shortlist handed up without the comments asks the user to re-read a discussion they
   have already had.

**Then one `AskUserQuestion` for the pick.** "Mix: layout from A, buttons from B" is an allowed answer
and is recorded as given, and so is "hold".

**The pick, the case questions and the comment read run in the MAIN SESSION.** `AskUserQuestion`
reaches the user only there, and an employee never chooses on the user's behalf.

### When the host has no artifact tool

No artifact tool means no page and no comment thread, and the step still runs: offer the candidates as
a **links list in the reply**, take the user's own pick from that, and **say in the record** that the
review round was a direct reply rather than a shared page, so a later reader knows no one else was
asked.

### When no browser tool exists

A stranger's install may have no browser tool at all, and a browser tool present can still refuse a
legitimate URL. Neither stops the step:

- Offer the candidates as **links plus a web-search summary of each**, with no screenshots.
- **Say so in the record**, per candidate: captured, or linked-only and why — no browser tool, or the
  capture was refused.
- A candidate that could not be loaded at all is not offered. An unverified link is not a reference.

## Step 6 — Write the design record

Write `.claude/design/direction.md` in the project. Append to it on a later run; never rewrite an
earlier entry, and never overwrite a direction the project already had.

### The design-record template

```markdown
# Design direction — <surface>

*Written <date> by `/ui-design direct`. Appended to, never rewritten.*

## The answers, in the user's words
> "<answer 1, verbatim>"
> "<answer 2, verbatim>"

## Stack
<CSS package and component library, and the file each was read from.>
<Existing tokens, palette, or house rules this surface inherits — and whose they are.>

### What this direction supersedes
<"(nothing — this surface inherits its direction unchanged)" when the answers kept it.>
| Inherited rule | Where | What it requires | What replaces it, for which surfaces |
|---|---|---|---|
| <rule ID or name> | <path:line> | <the requirement, as written there> | <the user's answer, and the surfaces it now governs> |

## Screens and their situations
| Screen | Primary situation | Secondary | ERG rules that apply |
|---|---|---|---|
| <route> | <LAND/FORM/TRIAGE/JOB/DASH/COMPARE/READ/SET> | <or none> | <ERG-SET-01, ERG-SET-05 — individual IDs> |

## Chosen references
| # | URL | Captured | Reviewed by | Source tier |
|---|---|---|---|---|
| 1 | <url> | <capture date, or "linked only — <reason>"> | <who commented, or "not circulated"> | <official package source / block library / gallery / "pattern reference, not this project's stack" + the deps the project lacks> |

## Review comments
<Each comment verbatim with its author, grouped by the candidate it is about. "(none — the page was
not shared)" or "(none — this host has no artifact tool, so the round was a direct reply)" when there
are none; an empty section and an unshared page are different facts.>
> **<author>** on candidate <#>: "<comment, verbatim>"

## What is borrowed, per reference
- **Layout skeleton:** <from which reference, and what specifically.>
- **Density:** <spacing scale, row height, how much sits in one viewport.>
- **Button style:** <shape, weight, radius, size, where the primary action sits.>
- **Palette:** <role by role: ink, surface, accent, status. Named, not hex-dumped, when the project
  already owns a palette.>
- **Type scale:** <families, steps, and the measure for body text.>

## What is deliberately NOT borrowed
- <the thing that would make this surface look like the reference, and why it is refused.>

## Licence note
<Per reference: open-source and adaptable, or reference-only. No markup or asset is copied from a
reference the project is not licensed for.>
```

**The user's answers are quoted verbatim.** A paraphrase in this file is a second author's reading of
the brief, and `BF-01` and `BF-02` both grade the render against it.

**The rules column lists individual IDs.** `ERG-SET-01, ERG-SET-05`, never `ERG-SET rules`. A family
name tells the build to go and re-derive the set, which is the derivation this step exists to do once.

## Step 7 — The component pass

When a later build needs a pattern the record does not cover — a data table, an upload flow, a step bar,
a kanban board, a diff — the same loop runs at component scale through `direct --component <pattern>`:
search the chosen package's own component library first, then its block library, then the
situation-keyed galleries; present; take the pick; append to the record. The `review` finding for an
uncovered pattern triggers the same pass.

## What a reference may and may not give the build

**A reference steers; it is never a donor.** What is taken is the layout skeleton, the density, the
button style, the palette roles and the type scale — described in the record in words, and rebuilt in
the project's own stack. What is never taken is markup, CSS or assets from a source the project is not
licensed for, and never a real product's branding or copy from a gallery screenshot.

Open-source sources — shadcn/ui, the Flowbite library, the Preline blocks a page still shows as free
under its fair-use terms, MUI core and its free templates, Bootstrap's examples, Bulma, HTML5 UP with
its credit kept — may be adapted directly. Everything in the link-only column may be looked at and
nothing more, unless the user says they hold the licence.

## An existing project direction is input

A project that already has a direction keeps it. A design lead's palette, a `CATALOG-ANCHOR.md` house
rule, a graphic system, a brand guide: each is read in step 1, recorded in the record's Stack section
as inherited and whose it is, and **constrains** the search rather than being replaced by it. A
candidate that cannot live with the inherited palette is not shortlisted. `direct` writes a new entry;
it never edits one the project's own people wrote.

### Whether the inherited direction governs THIS surface is a case question

**Ask it.** An inherited direction is a decision about some surface, taken at some date; whether it
covers the one being designed now is a fact about the case, so it belongs in the step 2 call alongside
"what is this surface for". It is not a style question, and the no-style-questions rule does not reach
it. Measured on the FetchMLS trial: the project held a ratified navy-only palette and a house rule
demanding a navy primary, the user answered "Own working palette", and nothing in this file said what
to do with the gap.

**A departing answer is recorded, not reconciled away.** The newer answer wins — it is the user's, and
it is later — and the record's **What this direction supersedes** table is where it says so: the
inherited rule, its `path:line`, what that rule requires as written, and what replaces it for which
surfaces. A direction that quietly contradicts a ratified rule leaves the next reader with two
authorities and no date between them.

**Then wire it, so `review` grades the new direction instead of reporting drift.** When the record
lands, each supersession row goes into the register in the project's own evaluator anchor — its
`CATALOG-ANCHOR.md`, whose format and rules are `evaluators.md` § The supersession register — citing
the design record as its source. That is an append to the register, which is the one place built to
hold such a row; the inherited rule's own text is still never edited. An evaluator reads the register
rather than the prose, so a supersession that never reaches it comes back as a finding against the
surface the user just approved.

**A shared shell widens the departure.** When the inherited rule governs one shell that several modules
render inside, a change to it reaches every surface that shell covers, not just this one. Say which
surfaces in the table's last column, and say it in the reply before the pick is taken, so the user is
deciding for the set they are actually deciding for.
