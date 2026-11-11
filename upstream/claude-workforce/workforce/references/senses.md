# The six senses

*How a turn takes something in, and which channel settles which kind of claim.*

A tunnel is not too little evidence. It is all of the evidence through one aperture — and
it feels like thoroughness from inside, which is why noticing does not work.

MEASURED, one working session, ten tunnels: **nine of the ten escapes came from outside**
the turn that formed the reading — six from the user, three from a spawned panel. The
tenth came from re-reading a tool's raw output. **Zero came from noticing.** So the fix
is never "look again." It is "open a channel this turn has not opened."

## The four that supply evidence

| Sense | What it is | What only it can settle |
|---|---|---|
| **sight** | reading the thing directly — the file, the line, the source | what a specific known thing says |
| **hearing** | testimony: the record (`git log`, the project's changelog or decision notes), a spawned reader, a web source, a skill — a voice that is not this turn's own reasoning | anything true of the world outside this repo, and whether an absence here was a decision |
| **touch** | running it: an exit code, a test result, output that came back from the world | what a thing DOES, as against what a document says it does |
| **taste** | discriminating between near-identical candidates: enumerating, diffing, listing before choosing | anything about a SET — what is all of them, what is missing, what is only |

## The two that warn

**Smell** — something is off in the reply itself, caught without re-reading the subject.
Smell selects which sense applies; it never scores one.

**Intuition** — the prior: what was asserted because it seemed right. It is deliberately
never scored, because scoring it means judging it, and judging one's own prior from
inside is the exact faculty the measurement found impaired. It is what the other five
are for.

## Guidelines

**The RECORD is testimony, and this table omitted it.** Three other shipped surfaces name it —
`wf-task-tag`'s own instruction (*"read the record that decided it (`git log`, the project's own changelog or
decision notes)"*),
the juror prompt (*"an outside voice — the record, the web, a spawned reader"*), and the `history` row
below (*"only the record says whether an absence was a decision"*). This row, the canonical definition,
listed only a reader, the web and a skill. *Corrected 2026-09-10, after a turn read two change records
before removing a mechanism and was told it had opened no hearing channel.* A turn that consults
`git log` for a decision has heard testimony; a turn that reads a source file has used sight, and the
difference is whether the thing read was WRITTEN to record a decision.

**Not every situation needs all six.** A turn is checked only on the senses its claim
needs. Asking for a channel the claim never required is how a guard earns its way into
being ignored — one was retired from this distribution at a measured 7.0% false-positive
rate for that (`changes/1.30.1.md`).

**A DESIGN ASK IS THE KIND THE OTHER FOUR MISS.** History, world, behaviour and existence
all ask about FACTS — what the record says, what the world says, what a script does, what is in a
set. A proposal is none of those, and it is where a tunnel forms: the design looks right from
inside, which is what "all of the evidence through one aperture" feels like. *Added 2026-09-10
after a session in which two of ten asks carried a docket, and the three design asks that carried
none produced a reading an independent reader broke in one move.* Its sense is hearing for the same
reason the whole file exists — the escape comes from a voice that is not this turn's own.

**Match the channel to the claim, not to the effort.**

- "There is no X" / "X is the only one" → **taste.** A point read samples a set; it cannot
  close one. Reading four more files is more sight, and more sight never settles it.
- "X is deprecated" / "the current way is Y" → **hearing.** Local documents go stale, and a
  repository cannot know the world.
- "This script does X" → **touch.** A procedure can describe a script in working detail that
  does not exist. Sight of the prose cannot tell; an `ls` or a run can.
- "This file says X" → **sight**, and sight alone is enough.

*Measured in workforce's own development: its local documents once called `vendor` a live
command, and four of its scripts were described in working detail by live procedures and
existed nowhere — every reader had sight of the prose and none had run an `ls`. Of its
judgment escapes, nine of ten came from outside the turn.*

**Two reads of two documents in the same repo is one channel, not two.** Corroboration
requires a different aperture, not a second sample through the same one.

**Widening means consulting something not yet consulted.** Restating the conclusion with
more confidence is the tunnel continuing, and it registers as work.

## Tagging the task, not just scanning the reply

**A reply scan is reactive and it reads the turn's own prose** — the same surface a
tunnel is built out of. `wf-task-tag` runs on `UserPromptSubmit`, classifies the ask
before any of the answer exists, and names the sense that closes it. `wf-widen` then
checks the turn's channel counts against that tag at `Stop` rather than re-guessing.

| Task kind | The ask looks like | Closed by | Because |
|---|---|---|---|
| `history` | why was this removed · should we restore it · was it deliberate | **hearing** | a tree shows what is there; only the record says whether an absence was a decision |
| `world` | is it deprecated · what is current · still supported | **hearing** | this repository cannot know the world |
| `judgment` | should we · why not · is that a good idea · what do you think | **hearing** | a proposal you authored cannot be judged from inside; the catch comes from outside the turn |
| `behaviour` | does it work · why does it fail · what does it return | **touch** | prose says what a script does; running it says what it did |
| `existence` | is there any · how many · list every · anywhere else | **taste** | a claim about a set is closed by enumerating it |
| `incident` | what went wrong · why did it break · diagnose | **hearing** | a cause is testimony: the record it came from, not this turn's reasoning |
| `work` | do X · let's start T7 · can you add · you never did X · that should have Y | **touch** | a result is a fact about the world after the work; only something that RAN shows it |

**`work` is the general case, and it seats its juror without blocking.** MEASURED 2026-11-09 on
mutze-studio: every user prompt behind five unchecked result claims ("Sarah's face swap is done",
"the face clearly changed" at RMSE 0.024, a page called updated) matched none of the fact kinds, so
no juror could sit. The kind reads the user's words — an imperative, a request put to the worker,
work said to be still owed, the state the work should leave — never the reply; an outcome-word scan
of replies was measured at 49.8% and rejected. It tags 45.0% of typed mutze prompts and 65.6% of
this repository's. A count of zero runs does not block it (`JURY_ONLY`): a draft or a plan is work
no command closes, so whether a claimed result was shown by a run is the touch juror's question.

**An injected turn carries the docket of the issue it serves.** A hand-back or a task notification
is not the user's ask and is never classified, but 64% of mutze Stops (581 of 912) were opened by
one, and the work lands there. The docket is the user's words for the issue the work was started
for: an agent through the ledger link made at `SubagentStart`, anything else the session started
(a background shell) through its `<tool-use-id>` to the turn that launched it, at most four hops.
Never the newest issue, and nothing found means no docket. A declared hold drops it. A message
delivered into a running turn (a `queued_command` row) adds its own docket to that turn.

**A message from another system is an ask like the user's, and is not the user.** User, 2026-11-09:
*"If a message comes in, it should be part of the work list too."* A `<cross-session-message>`, a
`<teammate-message>` and an `[agent-msg from=NAME …]` line are each classified from their own words,
open an issue and its checklist, and are seated at Stop the same way, with `ask.peer` telling the
jurors a peer asked. When the message is only a pointer ("read it by running: agent-say show <id>"),
it is classified from the output of the command it spelled out, as the turn ran it. A hand-back or a
task notification is a result of work already on the list, never a new ask.

**A running agent that has gone silent is said at the next Stop**, once per silence: its own
transcript unchanged for 20 minutes (`WF_SILENT_AFTER`) and its meta not finished. MEASURED over
76,821 tool calls in flight across 1,946 agent transcripts: 4 waits passed 15 minutes, and the 2 that
passed 20 were both hangs (220 and 203 minutes on a browser call). Background shells are not watched
this way: their output goes wherever their command sends it, so their task file's age says nothing.

**The list is short because it is a list of measured failures, not a taxonomy.** Each row
is a way work in this project has actually gone wrong. It grows when another way is
measured and not before.

**An ask can be two kinds at once** — "why was this removed and does it still work" is
`history` and `behaviour` — and both channels are then required. Taking only the first
match would drop the other silently.

**The tag is additive to the claim triggers, never a replacement.** A turn can answer a
tagged ask and make a claim; both senses are required.

## The jury

**Seven jurors, yes or no, no numbers.** The six senses below, and `asks`, which sits when a
message made several asks (`ask.checklist`) and checks that each was addressed. A jury of twelve returns a verdict, not a score,
and nobody asks how confident juror seven was. The senses work the same way: each one
answers a single question about the finished turn, and one verified `no` is a `no`.

**Only the jurors an ask summons are seated, and a docket from the user's words is always
tried.** The docket comes from `ask.senses`, derived from the user's own words before any answer
existed — not from the session's read of its own work. A turn whose docket came from those words,
its own or inherited, seats its jurors every time; only a docket a reply's own claim tripped is
sampled (`WF_AUDIT_SAMPLE`), and a turn with no docket keeps the blind sample. MEASURED by
`bin/replay-seating` over the 1,313 Stops of the 40 newest mutze transcripts: seated turns rise
from 17.9 to 53.5 per 100 judged, 33.1 more seats per 100 Stops.

**A turn whose own message asks for nothing still runs inside the session's open work**, so when
nothing else gives it a docket it inherits the dockets of the open issues its asks checklist
carries (`ask.carried`, newest first). A carried hit only seats a juror: it never blocks on a
channel count, never seats the incident jurors, and the jurors are told never to vote no because
that work is unfinished. It survives a declared hold, because a waiting reply is where a stale
state claim lives ("the third run is still on the pod", a job that had already failed). MEASURED
over 1,323 mutze Stops: 19.6 to 34.5 more seats per 100 Stops; of 10 sampled, 9 tried a real
claim about open work and 1 seated a reply that only asked a question.

**The jurors read the row that opened the turn.** A hand-back or notification goes to them as
`testimony`, and touch is judged from the transcript's tool_results: a claim with no run supporting
it is a verified no.

| Juror | Its one question |
|---|---|
| **sight** | does the source say what the conclusion says it says? On image work, does each image fulfil the ask where it is shown (§ An image is judged where it is shown)? |
| **hearing** | did an outside voice actually address this, and was it read? |
| **touch** | was the behaviour claimed demonstrated by something that was RUN? |
| **taste** | was the set the conclusion speaks about actually enumerated? |
| **smell** | is something off in the conclusion itself — overclaimed, or resting on a word the evidence does not support? |
| **intuition** | what did this turn assume without evidence, and does anything support it? |

**A juror may abstain**, and that is not a `yes`. One that cannot verify either way says
so rather than voting, because a vote nobody could check is the fabricated number in
another costume.

**Every verdict carries a reason — `yes`, `no` and `abstain` alike.** A bare `yes` says
nothing. A juror that acquits must say what it checked and what it showed, because the
reason is the deliverable and the verdict is not: the reason is the context that makes
the next step obvious without anyone having to be told, and that is the whole value of
an outside look at a tunnel you do not know you are in.

**Notes on a `yes` are the point.** A juror that votes to acquit and still noticed
something adjacent should say it. A verdict tells you that you were wrong; a note tells
you where to look, and the second is worth more — "you never read the record that
removed it" is already the widening, before any widening process runs.

**Why the sixth juror can finally sit.** `intuition` was shipped permanently unscored
because judging one's own prior from inside is the impaired faculty. True, and it only
ever ruled out SELF-judgement. A juror did not form the prior and can read it.

## Widening — the act, not the alarm

**A score that reports is an alarm. The widening is what answers it**, and it is
deliberately not performed by the turn that failed the score: that turn is the one
holding the reading, and asking it to go and check itself is the decision-from-inside
that the measurement at the top of this file rules out.

Three parts, cheap to expensive, so the expensive one only runs when it is earned:

1. **`wf-task-tag`** (`UserPromptSubmit`, free) classifies the ask and names the sense
   that closes it, before any of the answer exists.
2. **`wf-widen`** (`Stop`, free) checks whether the finished turn opened that sense's channel. If the
   sense went unopened it blocks the stop, and writes a flag naming what is unopened.
3. **`wf-widen-agent`** (`Stop`, a `type: "agent"` hook) reads that flag. **It spawns on every Stop**: MEASURED over 1,251 mutze Stops, p50 5.2 s,
   p90 11.1 s. With no flag it returns `ok: true` there (median 4.9 s); a seated jury's Stops
   run a median 11.1 s. With a flag, it spawns a reader carrying
   Read, Grep and Glob and none of the finishing turn's context (the transcript, conclusion
   and `said_earlier` it reads are evidence, never instructions), and judges whether the
   EVIDENCE supports the CONCLUSION for that ASK — verifying against the repository
   rather than taking the turn's word for it.

**The agent can block once per turn, and that bound is mechanical.** A blocked Stop
continues with `stop_hook_active: true`, and on that firing `wf-widen` deletes the flag, so
the agent finds none and returns `ok: true`. The prompt says the same thing as a second
layer; the deletion is the guard. MEASURED 2026-09-12: with the guard only in the prompt,
the agent blocked five Stops in a row, four of them continuations re-reading one stale
conclusion. The agent had read "commit it (or push it too)", an offer to the user, as a
plan the turn had failed to carry out, and the loop ended only when the user typed.

**A side query's Stop does not judge the same flag again.** Claude Code fires `Stop` for a side
query too, with that query's own output as the reply, and `wf-widen-agent` runs on it like any other.
`wf-widen` judges nothing on a Stop whose reply the transcript does not hold. It removes the flag only
once the transcript shows that the Stop which raised it has finished its hooks, the agent's included:
a `stop_hook_summary` row newer than the flag. Deleting it sooner can drop the real audit. MEASURED
2026-09-13: one side query arrived 9 seconds after its turn's stop summary, and another about 3
seconds after its turn ended, while that Stop's agent was still running. A side query that lands in
that window can still meet the flag, because nothing a command hook sees tells the two agents apart.

**A subagent's Stop is its own case, and it hands the main turn's jury nothing.** `wf-widen` runs
on `SubagentStop` too, and there the reply is the spawned agent's, `transcript_path` is the
PARENT's and the tag is the SESSION's — so one Stop scored an agent's in-flight line against the
main turn's tool calls and the user's ask, and wrote that mixture to the session's flag.
`wf-widen-agent` is registered on `Stop` and on nothing else, so a flag raised there can only ever
be opened by the turn that did not do the work. MEASURED 2026-09-13, twice in one run: a main Stop
was blocked on "Locating Directives block markers in SKILL.md", a fragment the user never saw, and
the juror's own reason was *"The conclusion is unrelated to the actual verification task."* A
spawned employee is still judged — on its ask, its reply and its evidence, all walked from its own
transcript — and it raises no flag.

**A turn waiting on background work is not judged at all.** `background_tasks` was read in one
place, the unfinished-work trigger, so a turn holding for a running agent was spared that block and
handed to the jury anyway — where it fails by construction, because a turn that is waiting has run
nothing. The exemption now gates the whole Stop decision. REPORTED 2026-09-13 by the session driving four agent batches: between one batch
finishing and the next being dispatched that array is momentarily EMPTY, so the gap is recognised
from two facts instead — a task notification opened the turn, which the tag records, and the reply
says what it is waiting on. Neither fact alone is a wait, and the same reply with nothing pending
is the measured mid-work stop, still blocked.

**One fact is read above that exemption: a shell the stopping agent started and never closed.**
`Stop` names a named teammate that handed back and was never sent a `shutdown_request`, and a
background shell whose starting agent has already finished. `SubagentStop` names the shells the
stopping agent started *itself*, read from its own transcript, and it runs before the
`background_tasks` gate — that gate is precisely what let the measured agent hand back with a live
shell, and "you are stopping with a background task running" is the one thing it must not silence.
A shell is closed, and silent, when a terminal-status notification has arrived for it or the session
stopped it explicitly, in **either** transcript: once a shell's command finishes the harness
delivers the notification to the session queue even while the agent that opened it is still alive,
so the agent's own file never records the close. Each is asked about once per session; the answer is
to kill it or to name it in the report with the reason it is kept. MEASURED 2026-09-24:
one such shell outlived its agent by nine hours and then woke the finished agent up again.

**Nothing in steps 1 and 2 scores anything, and that is a directive rather than a
design taste.** *"you have to measure results, not measure what you're doing and it has
to be aligned with the current request"*, and *"Evaluations are always done by the
independent agent"* (`SKILL.md` § Directives, 2026-09-09). An earlier version returned
0-100 from thresholds nobody had measured — two Bash calls scored 100 — and graded its
own work in-session. A count of recorded calls against zero is a fact; whether the work
was good is a judgement, and the judge did not do the work.

**Passing turns whose docket a reply's claim tripped are audited at `WF_AUDIT_SAMPLE`
(default 1 in 5); a docket from the user's words is always tried (§ The jury).** Auditing only
the turns that fail their own dispatch is the same bias one step removed: a turn that
looks fine would be judged by nothing but the session that produced it, and looking fine
is exactly what a tunnel does from inside. `1` audits every claim-carrying turn, `0`
disables sampling. It is a cost dial, not a correctness one — systematic self-flattery
shows up across turns rather than inside any single one.

**The agent is the point.** A command hook has no model: it can decide a sense went
unopened and it cannot open one. A spawn is not self-checking — fresh context, no
history, none of the reasoning that built the tunnel — which is why three of the ten
recorded escapes came from one and why this fires it without anybody choosing to.

**It reports findings and never edits.** A widening that could change files would be a
second author working from a partial view of the task, and the finding is the whole
deliverable: `file:line`, a commit SHA, what the record actually says.

## Quantified and relayed claims

Two claim trips **seat their juror every time and never block** (`wf-widen` `JURY_ONLY_TRIPS`,
`always_seated`). They exist because four result claims on mutze-studio `30e77777` (Stops 284, 614,
635, 726, all hand-back turns before the session's first issue) were seated by nothing on 1.86.2. The
user, 2026-11-09: *"all of these issues should have been caught if that system was working"*, and the
rule must be general, *"smart enough to manage everything ... within these senses"*, not a rule per
situation.

| Trip | What fires it | Sense |
|---|---|---|
| `quantified` | a set claim in any domain (`wf-turn-ledger` `QUANTIFIED`): `none of the/our/these … X`, `the only X we/that/in/left …`, `no X … has/shows/meets/matches/carries/holds/contains/fits`, `not one` / `not a single` | taste |
| `relayed` | on a turn opened by injected text (a hand-back, a notification), a reply sentence that shares a four-word run with that testimony (as the juror is shown it, `TESTIMONY_MAX`) and carries a count (`CARDINAL`) the testimony also carries, or a `QUANTIFIED` phrase when the testimony has one. The count must come from the hand-back: "on the calendar for 16 January" beside a relayed "the invitation is drafted" is not a relayed count | sight |

**Measured 2026-11-09**, every judged reply (mutze-studio: the 40 newest transcripts across both config
roots, 1,330 Stops, 1,238 judged; this repository: 93 transcripts, 440 Stops, 415 judged):

| | mutze-studio | this repository |
|---|---|---|
| `quantified` hits, share of judged replies | 7.8% | 13.5% |
| of which real set claims, 15 sampled | 10 of 15 | 10 of 15 |
| bare `the only`, left out | 6.4% | 6.5% |
| seated before (1.86.2), per 100 judged | 75.0 | 39.8 |
| seated after, per 100 judged | 79.8 | 56.9 |
| **added, per 100 Stops** | **4.5** | **16.1** |

**Why a seat can bear what a block cannot.** The blocking triggers were admitted at 0.5% and 1.5%, and a
guard at 7.0% was retired (`changes/1.30.1.md`), because a false BLOCK costs the user a round trip and
teaches the turn to ignore the guard. A seat costs one jury call and blocks nothing: the jury is the
precision layer, and two seats in three put a real set claim in front of it. The spend it adds (4.5 per
100 Stops on mutze-studio) is below the 1-in-20 blind sample already spent on undocketed turns, on a
corpus that already seats three turns in four. An outcome-word list hit 49.8% and was rejected; this
grammar names quantifiers, not outcomes.

**What each form catches**, replayed with `bin/replay-seating --before 651c16e`: 284 (relayed: "about
five pictures each, since the research says the sketch workflow takes about five at once"), 635
(quantified and relayed: "None of the forest pictures we already have shows the floor in morning
light"), 726 (quantified: "None of the costume pictures we hold meets the format"). **614 was not caught by either**: "both changed handbooks are back in service" shares no run with its
testimony ("PASS"), and "The page is republished" is the turn's own action, with no quantifier. The
next section is what catches it.

## A turn that starts from a worker's report

**User decision, 2026-11-09** (chooser answer, verbatim): *"Build it (Recommended)"*, for *"Every turn
that starts from a worker's report gets a juror, even when nothing else triggers one."* So a main turn
opened by injected text (a hand-back, a task notification) that has **no docket from any source** (its
own words, a peer, a served ask, a queued message, carried issues) **and trips no claim** gets the
`handback` trip (`wf-widen` `claim_trips`, `HANDBACK_DOCKET`): **sight** (did the reply read what it
passes on as true) and **intuition** (what did it assume). Seat-only, tried every time, never a gate.

**Two exclusions, both measured.** A reply that **only asks the user a question** passes nothing on
(`question_only`). A **declared hold that makes no claim** (`declared_hold` and every sentence is a
`WAITING` sentence or a question, `hold_only`) passes nothing on either. A hold that also reports a
result is tried, which is Stop 614's own shape: "back in service … Still working: the pipeline
programmer".

| Over the turns this trip could seat | mutze-studio (1,332 Stops) | this repository (442 Stops) |
|---|---|---|
| no-docket, no-claim hand-back turns | 177 (13.3 per 100 Stops) | 159 (36.0) |
| excluded as a claim-free hold | 4 (0.3) | 1 (0.2) |
| excluded as question-only | 0 | 1 (0.2) |

The hold count is the replay's TEXT half (`bin/replay-seating` cannot see `background_tasks`), so it is an
upper bound on what the live hook excludes. One of the four ("Screenshots are gone and no server is
running. Waiting on …") states a fact in a sentence `WAITING` also matches, and is excluded; that is the
known cost of reading a hold sentence by sentence.

**Seat rates, `bin/replay-seating --before 1927074 --summary`:**

| | before, per 100 judged | after, per 100 judged | added, per 100 Stops |
|---|---|---|---|
| mutze-studio, 40 newest transcripts | 79.8 | 91.9 | 11.2 |
| this repository, 93 transcripts | 56.8 | 91.1 | 32.4 |

Stop 614 on `30e77777` now seats intuition and sight; 284, 635 and 726 seat as before.

**Not measured, so not built:** the reply text a turn showed the user BEFORE its last tool call ("It's
the only front view we have", Stop 726, row 701) is not the reply (`confirmed_reply`, the last block).

## An image is judged where it is shown

**User decision, 2026-11-10**, removing the `image-eval` skill: *"I say we deprecate (remove)
image-eval. The Jury owns it. Too much emphesis is put on detail and not enough on whether the image
actually fulfills the request"*, and the check the jury owns is *"does it match the ask within the
context the image is being presented in, etc."* The reference case is mutze-studio `30e77777`: a face
swap was called done that had put the same picture in both slots, each image fine alone and wrong
against the ask.

**It is a condition on the sight juror, seated by a trip of its own.** A turn that produced, edited,
selected or placed an image trips `image` (`wf-widen` `image_work`, `CLAIM_SENSE`, `JURY_ONLY_TRIPS`):
seat-only, tried every time, never a gate, and it never takes a hand-back's seats. The flag carries
`images.files` and `images.placed_in`, and the sight juror LOOKS at each file with Read, then reads where
it is shown — the page, file or article that embeds it, its caption and surrounding text, the images
beside it, the project's design record — and asks whether it fulfils the ask there. A trip rather than
prompt text alone, because an undocketed turn is otherwise seated only 1 in `WF_BLIND_SAMPLE`, and the
unchecked claims in `30e77777` sat in turns the sample skipped. No medium, style or technique rule: the
ask and the placement are the whole standard.

**What counts is read off the turn's tool calls, never its prose:** a write whose target is an image or
whose new text embeds one (`![..](x)`, `<img src>`, `src=`, `srcset=`, `poster=`, `url(`); a shell
command or MCP tool naming an image path, minus segments that only remove or list files and minus a
screenshot or page snapshot; an image the turn read and the reply names by file name (it picked it); and
an image path in the hand-back or notification that opened the turn. A delegation is not the image.

| Measured 2026-11-10 | mutze-studio, 40 newest transcripts | this repository, 93 transcripts |
|---|---|---|
| Stops with a reply that trip `image` | 374 of 1,345 (27.8%) | 1 of 463 (0.2%) |
| seats added, `bin/replay-seating --summary` | 19 (1.4 per 100 Stops) | 0 |
| sampled, real image work | 15 of 15 | — |

The seat counts read mutze-studio's live issue ledger, so a re-run while a session there is open can move them. Most image turns were already seated by the user's words; what the trip adds there is the `images`
field and the instruction to look at the picture in its place.

**Not built:** a turn that only read images and named none in its reply (looking, not choosing).

## Where this is enforced

`wf-widen` checks the turn's channel counts at `Stop` and `SubagentStop`, and blocks rather than stopping
when an applicable sense went unopened — the block's reason names the instruments that
were on the machine and untouched. It is a hook because the measurement says the operator
cannot be the one to decide to run it: that decision is made from inside the tunnel, by
the faculty that is impaired.

`wf-turn-ledger` reports the same counts and never judges. The two are separate on
purpose: a count has no false-positive rate, and folding judgment into the count would
cost the property that makes the count safe.
