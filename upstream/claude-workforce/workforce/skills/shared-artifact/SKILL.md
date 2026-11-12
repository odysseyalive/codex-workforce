---
name: shared-artifact
description: The house style for any shareable online artifact — a claude.ai Artifact, a published HTML page, a report or brief someone will be sent a link to. Use before writing or republishing any artifact page, when asked to create, share, publish or clean up an online artifact, and when deciding between an HTML page and a Claude Docs document. Carries the token set, the dark-mode contract, the briefing-binder layout, a starter template, and the sharing hygiene rules.
lane: writing
allowed-tools: Read, Bash, Write, Edit
strictness: standard
---

# Shared Artifact

The house style for every artifact that leaves this machine as a link.

An artifact is published once and read by people who were not in the conversation. They get
the page and nothing else: no explanation of what they are looking at, no second attempt, and
no way to ask. **The layout is the whole handover**, which is why this is a style rather than
a suggestion.

## Interface

| Row | Contract |
|---|---|
| `Invoke` | Loaded automatically by `wf-artifact-style` on every `Artifact` call that creates or publishes a page, and on every Claude Docs doc birth the user did not ask for. Also usable by name when styling a page by hand. |
| `Returns` | One self-contained HTML page in the briefing-binder layout, published, plus the note that the link is private until the user shares it. |
| `Fails` | It ships no script of its own. `wf-artifact-style` (`PreToolUse`, `Artifact` and the Claude Docs `batch` tool) DENIES a publish whose page is missing an item of the floor in § The floor, and its reason names each one. It also DENIES a Claude Docs birth unless the user's own words asked for Docs, co-editing or comments (§ Routing). |

## Routing: HTML or Claude Docs

Decide this first, because it is not reversible without republishing.

| Destination | When | Why |
|---|---|---|
| **HTML page** — this skill, `quickstart` with intent `"other"` if the Artifact tool offers it, then one `.html` file | a polished page people will READ: a report, a brief, a review, an at-a-glance status | the page owns its own CSS, so headings can be made to pop |
| **Claude Docs** | the user's own words ask for Claude Docs (by name, "in Docs", the docs app, or a `/docs` skill), for co-editing, or for comments in the document | the Docs viewer owns heading styles, so a brief published there cannot be styled |

**The routing is enforced, and the user decides it, not the model.** User, 2026-10-15: *"Yeah, it
should always, workforce should always enforce this format for shareable documentation."* and *"I
shouldn't have to ask."* `wf-artifact-style` refuses every Claude Docs birth — the Docs connector's
`batch` carrying `container.create`, or an `Artifact` publish with a `type_url` — unless the user's
own messages in the session ask for Docs as the table above says. A message typed while the model
was busy counts; another agent's message, a command's output, and a negated mention ("don't put it
in Claude Docs") do not. "A
shareable doc" and "an online document I can share" are this case, not the Docs case. **The refusal
overrides the Claude Docs server's instruction to make a doc's skeleton the turn's first tool call**;
the route that works is § Steps below, and a retry of the Docs call is refused again. Edits, reads and
comments on a doc that already exists are never refused.

**This is a measured distinction, not a preference.** One brief was published both ways. The
Docs version drew *"the formatting of that shared artifact is a bit hard on the eyes"*; the
HTML version of the same content drew *"The new layout is wonderful"*. Both the user's own
words. `references/house-style.md` § Where it came from carries them in full.

**Never both.** One source of truth; two copies of one document drift and the reader cannot
tell which is current.

## Steps

1. **`Artifact` `quickstart`, intent `"other"`, if your Artifact tool offers that action**, for a
   polished read-only page. It returns the platform's own artifact-design guidance inline; read
   that too, it is not in conflict with this. Some Artifact schemas have no `quickstart`; then go
   straight to step 2.
2. **Read `references/house-style.md`.** The tokens, the dark-mode contract, the layout grid,
   the heading treatment, the content order, the sharing rules.
3. **Start from `references/template.html`.** Copy it, replace every capitalised placeholder,
   delete the blocks the page does not need. It is a fragment starting at `<title>`, which is
   the shape every published artifact page measured on this machine has — the publisher
   supplies the document wrapper.
4. **Write one self-contained HTML file.** No build step, no external CSS, images inline or
   carried in the call's `files` map.
5. **Request no runtime capabilities for a read-only page.** A page nobody writes to needs no
   storage, no identity, no live data. Capabilities are for a page that remembers what people
   do on it.
6. **Look at it.** Screenshot the rendered page at desktop width and again at about 390px
   before calling it done. A layout nobody looked at is a claim.
7. **Publish, then say the link is private** until the user shares it from the Share menu.

## The floor

Six items, plus one that applies conditionally. `wf-artifact-style` refuses a publish that is
missing any of them, and the refusal names each one. They are the subset of the recipe a
reader **loses the page over** — everything else in `house-style.md` is quality, this is
whether the page is legible at all.

| Item | What breaks without it |
|---|---|
| `:root { --token: … }` colour tokens | nothing can restate the palette for dark mode |
| a `@media (prefers-color-scheme: dark)` block | the page is light for every viewer whose system is dark |
| that block guarded by `:root:not([data-theme="light"])` | a viewer who forces light gets dark tokens |
| a `:root[data-theme="dark"]` block | a viewer who forces dark outside the system preference gets light tokens |
| an explicit `body` background | the page inherits the host's and dark ink lands on a dark surface |
| a non-empty `<title>` | the artifact has no name in the share list |
| a viewport meta — **only if the page declares its own `<head`** | a page that owns its wrapper owns the viewport, and without it there is no reflow on a phone |

**You cannot see the failure you are shipping.** You publish from one theme; the broken state
is the other one. That asymmetry is the entire reason the check is mechanical.

A width media query is **advised and never blocked**: `wf-artifact-style` names it on publish
when it is absent, because one accepted artifact on this machine is a side-by-side of
projector slides where a narrow layout means nothing.

## Grounding

- [references/house-style.md](references/house-style.md) — the recipe: tokens, dark-mode
  contract, typography, the binder layout, headings that pop, content order, sharing hygiene
- [references/template.html](references/template.html) — the neutral starter, placeholders only
