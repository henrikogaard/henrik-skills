---
name: design-doc
description: The starting point for new engineering work. Phase 1 captures requirements and scope and writes a conceptual and logical design into one Markdown design doc, then stops for approval. Phase 2 builds the work slice by slice, writing each slice's detailed design just before implementing it and keeping the doc current with decisions, deltas and test results. Use whenever someone starts a new feature, system, service, integration or significant change ("let's build", "new feature", "what are we building", requirements, PRD, spec, architecture, design), and whenever implementing work that already has a design doc. Not for trivial fixes.
---

# Design doc

Every piece of new work gets **one Markdown design doc** that grows with it. It holds the requirements, the scope, the design, the decisions and the evidence. Decisions live inside the doc as a numbered log, so the work needs no separate ADR files.

```
Phase 1 (plan):  requirements → scope → conceptual → logical → decisions → build plan → STOP for approval
Phase 2 (build): for each slice: detailed design → implement → verify → update the doc
```

The doc's first lines carry a status everyone can read at a glance:

`Status: Draft` → `Approved (<date>, <who>)` → `Building (slice <n> of <m>)` → `Done (<date>)`

## Start: find or create the doc

1. **Look for an existing doc** in the repo's design docs folder (default `docs/design/`). If one covers this work, read it, read its status, and continue from there. Never start a second doc for the same work.
2. **Size the work and say which size in your first line:**
   - *Trivial* (a typo, a config value, a one-line fix with an obvious test): say "Trivial: no design doc", then just do it.
   - *Small* (a change inside a settled architecture, a few requirements): a one-page doc. Requirements and scope in short lists, a short design section, a plan of one or two slices. Leave out any section with nothing in it.
   - *Full* (a new system, a service, an integration, or anything that crosses component boundaries): every section.
3. **Read the code** if it exists, before designing. Where the code and the design will disagree, record it under "Codebase deltas" with a ruling: the design yields, the code migrates, or it becomes a `Q-n`.

## Phase 1: plan

Write these sections in order, using the skeleton in `references/template.md`. Read each reference before writing its sections.

1. **Requirements** (`references/requirements.md`): numbered sources, then `FR-n`, `NFR-n`, `CON-n`, `ASM-n` and `Q-n` rows. Every Must and Should FR gets an acceptance criterion. Every source statement ends up as a requirement, an open question or an out-of-scope line.
2. **Scope**: three short lists. *In* (requirement IDs), *Out* (with who ruled and when), *Later* (deferred, with the `Q-n` or reason).
3. **Conceptual and logical design** (`references/conceptual-logical.md`): purpose, context map with trust boundaries, capabilities, components, then contracts, domain model, data ownership, scenario walkthroughs and NFR mechanisms. Technology families only, no products, unless a `CON-n` forces one.
4. **Decisions**: one `D-n` entry per pivotal choice. See "Decisions log" below.
5. **Build plan**: slices, thinnest end-to-end slice first (the one that exercises the riskiest contract). Each slice lists the requirement IDs it makes testable.
6. **Open questions**: every `Q-n` still unanswered, with what it blocks.

Then **stop**. Present the doc leading with the open questions, the balanced tradeoffs and the top risks, and ask the user to approve it. Write no code before approval. On approval, set `Status: Approved (<date>, <who>)`. If the user changes something, update the doc first, then ask again.

If the user is away, finish Phase 1 on stated working assumptions (listed at the top and in the risk register), leave `Status: Draft`, and stop.

## Phase 2: build, one slice at a time

Only start when the status is `Approved` or `Building`. For each slice, in plan order:

1. **Detailed design for this slice only** (`references/detailed.md`), under "Detailed design → Slice n": interfaces with one literal example, data changes and migrations, failure modes, and the tests for this slice's acceptance criteria. This is where products and versions get pinned, each pivotal one as a `D-n`. Write it just before building, so it matches the code that exists.
2. **Implement** through the repo's normal workflow (branch, tests, PR). Link the doc from the PR.
3. **Verify.** Run the tests. Fill the Verification table: acceptance criterion → test → result → commit. A criterion without a passing test is not done; say so.
4. **Update the doc** in the same commit as the code: set `Status: Building (slice n of m)`, mark the slice done in the plan, record any code that diverged from the design under "Codebase deltas", add new `D-n` entries, and add a change-log line.

If building shows the logical design is wrong (a contract, a data owner or the scope must change), stop. Update the logical section and add a `D-n` that supersedes the old choice, then ask the user before continuing. Small detail-level changes need no approval; record them as deltas.

When every slice is done and every acceptance criterion has a result, set `Status: Done (<date>)`.

If the work goes to implementers who were not in the conversation, write every slice's detailed design before Phase 2 starts, and say so.

## Decisions log

Record a decision when it is **pivotal**: reversing it would touch more than one component's contract or force a data migration. Each entry:

```markdown
### D-3: Charge late-cancel fees after the cancel commits (Accepted, 2026-10-15)
Context: a slow Stripe call must not block a member's cancel (NFR-1).
Options: (a) charge inside the cancel request; (b) charge after commit via an outbox.
Choice: (b). Cancels never wait on Stripe; a failed charge is retried and reported.
Consequences: fee status is eventually consistent; needs a retry job (slice 3).
```

Status is `Proposed`, `Accepted` or `Superseded by D-n`. Never rewrite an accepted entry; add a new one that supersedes it. Where a tradeoff is balanced, leave it `Proposed` and ask the user. If the repo already has ADR files, link the relevant ones from the log instead of adding new ADRs.

## Rules that matter most

- **Trace both ways.** Every requirement has a home in the design, and every component cites at least one requirement. A component with no requirement is invented scope.
- **Unknowns stay visible.** An honest `Q-n` beats a guessed requirement or a silent choice.
- **One owner per datum.** If unclear, name a provisional owner and raise a `Q-n`; never leave it blank.
- **Walkthroughs are the stress test.** A step with no owner means the design has a hole. Fix the design, not the walkthrough.
- **NFR mechanisms show arithmetic.** "Add a cache" is not a mechanism.
- **The doc tells the truth about the code.** When they disagree, update the doc in the same change.
- **Scale to the work.** Leave out empty sections. Never pad a heading to match the template.

## Done when

Phase 1:
- [ ] The first line states the size; the status line is present.
- [ ] Every source statement has a disposition, and every Must and Should FR has an acceptance criterion.
- [ ] Scope lists In, Out and Later.
- [ ] Coverage closes: every requirement has a design home, every component cites a requirement, every `CON-n` is honored or escalated.
- [ ] Every pivotal choice is a `D-n` entry.
- [ ] The build plan's slices cover every Must requirement.
- [ ] You stopped and asked for approval, with no code written.

Each Phase 2 slice:
- [ ] Its detailed design was written before its code.
- [ ] Every acceptance criterion of the slice has a test and a recorded result.
- [ ] The status line, plan, deltas, decisions and change log are updated in the same commit as the code.
