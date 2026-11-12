<!-- shared-artifact-ref-version: 1 -->

# House style for a shareable online artifact

The recipe behind the page the user graded. Read it before writing markup; `SKILL.md` names
the steps and this file holds the values.

## Where it came from

One session published the same brief twice. Through the Claude Docs connector first, and the
user's words on that attempt are the reason this file exists:

> okay, the formatting of that shared artifact is a bit hard on the eyes. Can we clean it up
> a bit please? Make each of the headings pop out better and just overall appearance layed
> out a bit more professionally?

Rebuilt as one HTML page in the layout below, the same content got:

> The new layout is wonderful

Both are the user's own words, retained verbatim. **The Docs viewer owns its heading styles**,
which is why the first attempt could not make headings pop however it was written. That is
not a defect in Docs; it is what routing § in `SKILL.md` is about.

## Tokens

Every colour in the page comes from a token, **including inline SVG** (`fill="var(--ink)"`).
A hard-coded hex anywhere is a value that will not follow the theme.

```css
:root {
  --bg: #f6f7f9;
  --paper: #ffffff;
  --ink: #16202b;
  --muted: #566372;
  --rule: #dfe3e8;
  --tint: #eef2f6;
  --accent: #0d5f73;
  --accent-soft: #e2f0f3;
  --crit: #b4262c;   --crit-soft: #fbe9ea;
  --warn: #9a5b00;   --warn-soft: #fbf0dc;
  --ok: #2d6a3e;     --ok-soft: #e5f2e8;
  --info: #3b4f8f;   --info-soft: #e8ecf8;
  --code-bg: #eef1f4;
  --f-display: "Archivo", "Arial Narrow", Arial, sans-serif;
  --f-body: "Public Sans", "Segoe UI", system-ui, sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
```

**A project with brand tokens of its own replaces the VALUES and never the STRUCTURE.** The
token names, the two dark blocks and the body background are what the page is built on; the
hexes are a default.

### Both dark blocks, and the guard

```css
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { /* dark values */ color-scheme: dark; }
}
:root[data-theme="dark"] { /* the same dark values */ color-scheme: dark; }
body { background: var(--bg); color: var(--ink); }
```

Three separate things, and each one is load-bearing:

| Line | Without it |
|---|---|
| the `prefers-color-scheme` block | the page is light for every viewer whose system is dark |
| `:not([data-theme="light"])` on it | a viewer who forces light still gets dark tokens |
| the `:root[data-theme="dark"]` block | a viewer who forces dark outside the system preference gets light tokens |
| an explicit `body` background | the page inherits the host's, so dark ink lands on a dark surface |

**You will not see any of these yourself.** You are publishing from one theme, and the broken
state is the other one. `wf-artifact-style` refuses a publish that is missing one for exactly
that reason.

Restating the light tokens in a `:root[data-theme="light"]` rule *after* the dark media block
reaches the same place as the `:not()` guard, and the hook accepts it. Prefer the guard: it
keeps the light palette stated once.

## Typography

| Role | Face | Settings |
|---|---|---|
| Display | Archivo | `font-stretch: 85–88%`, weight 750–800 |
| Body | Public Sans | 16px / 1.65 |
| Mono | JetBrains Mono | labels, ids, codes, contacts |

Google Fonts with a real fallback stack behind each one. Paragraphs cap at 70ch, headings
take `text-wrap: balance`, uppercase labels take `letter-spacing: .09–.14em`.

## Layout: the briefing binder

```css
.wrap { display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: 48px; max-width: 1240px; }
@media (max-width: 900px) { .wrap { grid-template-columns: minmax(0, 1fr); gap: 0; padding-inline: 16px; } }
```

A sticky contents rail on the left, one reading column on the right. Under 900px it becomes
one column, the rail turns into a static `auto-fill` grid at the top, and the side gutter
drops to 16px. **The content is fully readable with JavaScript off**; the rail's
scroll script only adds the current-section highlight. It marks the last section whose top has
passed 30% down the window, never an IntersectionObserver band: a clicked target lands above any
band and the previous entry stays lit.

Group the rail's entries under short uppercase labels once the list is long enough that a
reader has to hunt in it.

## Headings that pop

The complaint the whole style answers is headings that do not separate. The answer is a grid,
not a bigger font:

- Each H2 sits in a `.sec-head` grid: a dark **section-number chip** (mono, ink background,
  paper text), the heading in Archivo at `clamp(26px, 3.2vw, 34px)`, a 1px ink rule above it,
  and an accent mono **kicker** line underneath.
- H3s are 13px bold uppercase in the accent colour, so they read as labels rather than as
  small headings.
- The masthead carries a 3px ink bottom border, a mono eyebrow, an 800-weight H1, and a muted
  lede.

## Content structure

1. **Summary first.** Section `00` is "at a glance": one sentence, then a table of every item
   with a status pill.
2. **Most urgent first** after that, not chronological.
3. **Every repeated item opens the same way** — a case-file strip (`Status · Found · Owner ·
   Ask`), then a bordered summary paragraph, then the same H3s in the same order every time.
   The repetition is what lets a reader skim to the part they want.
4. **People are cards**, and the ones the reader must deal with carry an accent inset border.
5. **Pills are semantic** (`crit` / `warn` / `info` / `low`) and are kept separate from the
   accent colour, which belongs to the page's own structure.
6. **Tables live in an `overflow-x: auto` wrapper**, with `tabular-nums` and uppercase muted
   headers.

## Sharing hygiene

- **Title:** two to four words. **Description:** one sentence.
- **No credentials, no working exploit URLs, no personal addresses** beyond business contacts.
  A shared link is a link anybody holding it can open.
- External links are real `<a target="_blank" rel="noopener">`.
- **No print button, no `mailto:`, no `tel:`.** They look like features and do nothing useful
  on a shared page.
- Say, in the reply, that **the link is private until the user shares it from the Share menu**.
- **One source of truth.** Never keep a Docs copy and an HTML copy of the same content: they
  drift, and the reader has no way to know which one is current.

## Look at it before calling it done

Open the rendered page and take a screenshot at desktop width and again at about 390px. A
page that was never looked at is a page whose layout is a claim. Two minutes here is what
separates "the new layout is wonderful" from "a bit hard on the eyes".
