<!-- creative-scrub-ref-version: 2 -->
<!-- origin: skill-builder | modifiable: true -->
# creative-integrity reference version

This file is the **drift anchor** for the shipped creative-integrity reference set
(currently `text-tells.md`). `skill-builder audit` Step 4c-bis reads the integer below
(skill-builder's *shipped* version) and compares it to the `creative_scrub_ref_version`
recorded in a project's scaffold-generated evaluator skill (its SKILL.md frontmatter)
and to the version stamped in any per-skill gap-ack sidecar. Shipped > recorded →
the project's machine-owned library regions are stale → audit's gap check re-runs
against the new shipped content; previously acknowledged gap rows stay suppressed
unless their shipped entry materially changed since the acked version.

**This file, and its `creative-scrub-ref-version` anchor, track the imported set ONLY.** The
creative-integrity set (`text-tells.md` in this directory) was imported from claude-enforcer's
skill-builder on 2026-08-03 (commit `ff27cb2`) and is **workforce-owned since 2026-11-10**. User,
2026-11-10: *"please take care of items 06 through 10 to clean up this project"*, the tenth being
that claude-enforcer is superseded and other users do not have it. There is no upstream to match
byte for byte any more: a change to this set is made here, bumps the integer below, and reaches
installed copies through the forcible append. Tells that
**workforce itself** authors are not in this set and are not counted by this anchor: they live in
`text-eval/references/additions.md`, versioned by its own `text-additions-version` anchor. A reader
who reaches this file by the `catalogs/` path and never sees that slot has diffed the wrong pair
(`evaluators.md` § Seeding).

```
creative-scrub-ref-version: 2
```

Bump this integer whenever ANY file under `references/creative-integrity/` changes in
a way users should receive. Every shipped file in this set also carries a matching
`<!-- creative-scrub-ref-version: N -->` header on its first line; keep them in sync
with this number so a per-file check is possible.

## Changelog

- **v2** (2026-06-17) — Em-dash hardening. The em-/en-dash row in `text-tells.md` moves
  from a Tier-1 soft "per-1,000-words baseline" test to a **[hard] near-restriction**
  (target ≤1 per ~5,000 words; em-dash-as-crutch; every occurrence flagged) per user
  directive — em-dashes are not a default punctuation tool. The `[hard]` rule is
  clarified to be immune to voice-protection / cluster-density / human-presence demotion
  (closes the character-flag carve-out gap). The evaluator-skill scaffold
  (`creative-integrity.md` § Build Scaffolds) now seeds a **mechanical character-scanner
  agent + reasoning evaluator** with an invocation-independent character pass, so a
  single context-isolated run can no longer bypass the mechanical gate.
- **v1** (2026-06-12) — Initial release. Portable AI-text-signature library
  (`text-tells.md`): the odyssey-alive text-eval pattern set (64 patterns merged
  2026-06-11 + wit-shaped noise 2026-06-12), generalized to project-agnostic wording,
  plus 24 research-verified additions (WP:AISIGNS, Pangram 2026): markdown/heading
  tells, pipeline-artifact residue, chat-frame/sycophancy leakage, and corpus-level
  tells. Three detection tiers + corpus tier, overbuilt-prose signals, flow checks,
  human-presence markers. Severity/cluster/voice policy stays canonical in
  `creative-integrity.md`; this set carries detection content only.

**The imported set is `text-tells.md` and `human-markers.md`** (2026-09-10). The second came across
with the evaluators when they began shipping as skills: the consolidated catalog covers every topic the
project copies carried except positive human-presence signals, and an evaluator that can only score
tells over-flags writing that is plainly human. Both were imports; both are workforce's own since
2026-11-10, under the same rule as above.
