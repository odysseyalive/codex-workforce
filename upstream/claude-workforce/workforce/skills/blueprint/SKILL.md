---
name: blueprint
description: Author an implementation plan as a file, in whatever permission mode the session is already in, without entering plan mode and without implementing what it plans. Use when asked to build, write, draft, or revise a plan, design doc, or implementation strategy for work that happens later, or a living tracker for a long piece of work that spans many sessions. Every claim in the plan cites the tree or is labeled unverified, and the plan is checked before its path is reported. It never offers to start the work.
lane: coding
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
strictness: standard
---

# Blueprint

Authors an implementation plan as a **file**, checks it, and ends there.

**This is not plan mode, and it must never become plan mode.** The harness plan mode is a
permission state: it blocks writes, so every read, every search, and the plan itself arrives as
a prompt the operator has to approve, and it exits by asking to execute. Blueprint is
instructions, not a permission state, so it works unchanged in any mode the session is already
in, including auto. Nothing mechanical stops the work here. The plan-only contract below is the only thing that holds, and it holds because it
is followed.

## Interface

| Row | Contract |
|---|---|
| `Invoke` | /blueprint <what to plan> \| /blueprint track <what to track> \| /blueprint revise <path> [what changed] |
| `Returns` | One markdown file in the project's plan directory, its path, and one line saying how it was checked. Nothing the plan describes is built. |
| `Fails` | No exit codes declared; the skill ships no script. It fails by stating a claim nothing on disk supports, by reporting a plan it did not check, or by starting the work it planned. |

## Commands

| Command | Action |
|---------|--------|
| `/blueprint <what to plan>` | A plan for one change you implement once. Dated filename. |
| `/blueprint track <what to track>` | A living tracker for work that runs across many sessions: status block, checkboxes, resume procedure. Undated filename. |
| `/blueprint revise <path> [what changed]` | Edit an existing plan or tracker in place, keeping its filename. On a tracker this is the per-session update. |

When the operator typed a mode, use it. Otherwise pick `track` when the request describes a
module, a multi-stage build, or anything the operator says they will come back to. Don't ask
which mode; the request answers it.

## The plan-only contract

1. **Never call `EnterPlanMode` or `ExitPlanMode`.** Not to start, not to present the plan, not
   to hand it over. Entering plan mode reintroduces exactly the approval traffic this skill
   exists to avoid, and `ExitPlanMode` asks to execute, which rule 2 forbids.
2. **Never implement what the plan describes**, in the same turn or a later one, unless the
   operator asks for it in a new message. Writing the plan is not consent to run it. Ticking a
   tracker box records work that already happened; it is never a reason to do the work.
3. **Never close by offering to start.** "Want me to implement this?" is the offer this skill
   is defined against. Close with the report line and stop.
4. **Editing files that are not the plan file is out of scope.** Reading the whole tree is
   expected; writing anywhere but the plan file is not, apart from creating `plan/` when the
   directory search below ends there. That includes the project's own state record: a tracker
   points at it and never edits it.

Research may run read-only commands: `git log`, `grep`, `git diff`. They are often the difference
between a plan that cites the code and a plan that guesses at it. Don't run commands that write,
such as a test suite that leaves caches or build output; cite the last recorded result instead,
or name the command in Verification for later.

## The sourcing rule

Every factual claim about the project cites where a reader can check it: `path:line`, a commit,
or a read-only command they can re-run. A claim that comes from memory, an earlier conversation,
another session's notes, or a file that is no longer on disk is marked **(unverified: <where it
came from>)**. An unverified claim may sit in the plan as context. It may not be the reason for a
step, and it may never tick a box.

This rule exists because a plan that states recollections as facts reads exactly like a plan that
checked them, and the reader has no way to tell the two apart.

## Resolving the plan directory

Use the first of these that gives an answer:

1. **A directory the operator typed.** If you wrote the invocation arguments yourself, a
   directory you put there is your guess, not the operator's choice, and it does not skip step 2.
2. **Where plans already live.** List the project's files (`git ls-files`, or outside git
   `find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*'`) and filter with
   `grep -iE '(^|[/_.-])(plans?|blueprints?|roadmap)([/_.-].*)?\.md$'`, which matches the name
   in a filename or a folder. If the request is about
   an existing plan, write beside it. Otherwise use the directory that holds the most matches,
   and on a tie the one holding the most recently modified match.
3. The first of these that exists in the project root: `plan/  docs/plans/  .claude/plans/  notes/plans/  docs/plan/`
4. Create `plan/`.

Don't ask which one; the order is the answer.

**Filename.** A plan is `<slug>-<YYYY-MM-DD>.md`, because it is a snapshot of one decision. A
tracker is `<slug>.md` with its start date inside the file, because it will be edited for months
and a date in the name says it is frozen. The slug is a short kebab-case noun phrase. Match the
date format of existing files in the directory if it differs. On `revise` the filename never
changes.

## Workflow

1. **Read the record before writing anything.** The project's own `CLAUDE.md`, the existing
   plans found above, `git log` for the area, and the code the plan will touch. A plan that
   restates the request back in headings adds nothing; its value is what the research found.
2. **In `track` mode, find the state record.** Look for a file the project already uses to record
   what is done: its `CLAUDE.md` or README may name one, and the same file listing filtered with
   `grep -iE '(^|[/_.-])(state|status|progress|tracker)([/_.-].*)?\.md$'` finds the usual names,
   including files inside a folder such as `build-state/`. The tracker must say which
   file owns state. If one exists, it wins: the tracker is the work list on top of it, and where
   the two disagree the tracker is corrected. If none exists, the tracker says it owns state.
   Skipping this produces two trackers that drift apart.
3. **Name what is uncertain, and resolve what can be resolved.** Anything the code or the record
   answers, answer there rather than carrying it to the operator. What genuinely needs a decision
   goes in Open questions with the options and a recommendation, not as a blocking question,
   because an unanswered question does not stop the plan being written.
4. **Write the file.** The shapes are below. Apply the sourcing rule as you write, not after.
5. **Check it.** See below. Fix what the check finds before reporting.
6. **Report and stop.** The path, then one line on the check: what was re-verified, what the
   independent read found and what was fixed, and how many claims remain unverified. See rule 3.

Take the time the subject deserves. A plan is read more often than it is written.

## Checking the plan before reporting

A written file only proves the file exists. Before reporting it:

1. **Re-verify every citation.** Re-read each `path:line` and confirm it still says what the plan
   claims. Re-run each cited read-only command and compare the output. A claim that fails becomes
   a correction or is marked unverified.
2. **Run the project's own checker** if it has one for citations or links in docs, named in its
   `CLAUDE.md`, README, or package scripts.
3. **Get one independent read.** Spawn one fresh agent with the plan's path and this instruction:
   check each factual claim against its citation, and return every claim the evidence does not
   support, every step resting on an unverified claim, and every ticked box without evidence.
   The session that wrote the plan cannot grade it. If spawning is unavailable, say so in the
   report line; do not replace it with a self-review and call it a check.

On `revise`, check what changed plus every box ticked in this session.

## Plan shape

For `/blueprint <what to plan>`. Sections in order; drop any that would be empty rather than
filling it with restatement.

| Section | Holds |
|---------|-------|
| Title + date | What this plans, and when it was written |
| Problem | What is actually wrong or missing now, with `path:line` evidence |
| Approach | The shape of the fix, and why this shape over the alternatives considered |
| Steps | Ordered, each one small enough to verify on its own |
| Files touched | Every path the work will create, edit, or delete |
| Verification | How anyone can tell the work succeeded, by command where possible |
| Open questions | Decisions that need the operator, each with options and a recommendation |
| Risks | What breaks if this is wrong, and what is hard to reverse |

A step that names no file is not yet a step.

## Tracker shape

For `/blueprint track`. Paths that later stages will create can't all be known today, so a stage
names the directory or module it works in and its items name files as they become known.

| Section | Holds |
|---------|-------|
| Title + started | What this tracks, and the date it was started |
| Status | Last updated date, current stage, next open item, blockers. Rewritten every session. |
| State record | Which file owns state, and that it wins on conflict. Or: this file owns state. |
| Resume | What a fresh session does first, in order (below) |
| Definition of done | What must be true for the whole tracker to close, by command where possible |
| Human gates | Points where the operator must decide or approve before work continues |
| Stages | Ordered, each with a goal and checkbox items |
| Open questions | As in a plan |
| Unverified | Every claim still marked unverified, and what would verify it |

**Checkboxes.**

- `- [ ] item` is open.
- `- [x] item (evidence: <path:line | commit | command>)` is done. **A box is ticked only with
  evidence**, and the evidence must pass the check above. No evidence, no tick.
- `- [x] ~~item~~ (dropped <YYYY-MM-DD>: <reason>)` is obsolete. The box is filled so it never
  reads as open work; the strike and the reason say it was dropped, not done. Never delete an
  item: what was dropped and why is part of the record.

**Resume** is written into the tracker for the session that picks the work back up. A
`/blueprint revise` run does steps 1 and 2 and stops there; step 3 is the work, and rule 2 still
holds.

1. Read Status and the state record. Where they disagree, the state record is right; fix Status.
2. Re-check the evidence on the most recently ticked items. Untick any whose evidence no longer
   holds.
3. Continue from the next open item, stopping at any human gate before it.

**Revising a tracker** means: update Status, tick boxes that now have evidence, strike items
that no longer apply, add items the work uncovered, then check and report as above.
