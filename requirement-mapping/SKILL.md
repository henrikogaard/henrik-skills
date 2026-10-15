---
name: requirement-mapping
description: Turn a fuzzy ask — a conversation, an issue, an RFC, meeting notes or a rant — into a requirements map of numbered, testable requirements traced both ways to their sources, with gaps, conflicts and open questions made visible instead of guessed. Use when the user mentions requirements, a PRD, acceptance criteria or traceability, asks "what are we actually building", or before designing a system or major feature.
---

# Requirement mapping

A requirements list answers questions. A requirements **map** also accounts for everything: every requirement cites the source it came from, and every source statement ends up as a requirement, an open question or an explicit out-of-scope ruling. That two-way accounting is the whole skill. Without it, a list silently invents scope or drops half of what the stakeholder said.

The map makes gaps **visible**; it does not close them by guessing. An honest open question is a deliverable. A requirement invented to fill a hole is a defect.

**Size the ask first, and state the size in your reply's first line.**

- **Small** (one source, a handful of needs, an obvious definition of done): start with "Small ask: requirements inline." Then list the FRs with their acceptance criteria and any open questions, in the reply only. Write no map file and no empty sections; leave out Dependencies or Conflicts when there are none. Aim for under ~25 lines.
- **Full** (anything else): start with "Full map." and follow the steps below.

Running the full process on a small ask is a failure mode, not thoroughness. If a full ask turns out small mid-way, switch to the small form.

## IDs

| Prefix | Meaning |
|---|---|
| `S1`, `S2`… | Source: conversation, issue, doc, thread or existing code, with a location precise enough to re-find |
| `FR-n` | Functional requirement |
| `NFR-n` | Non-functional requirement (performance, scale, security, compliance, usability, cost) |
| `CON-n` | Constraint: deadline, budget, must-use or must-not-use technology |
| `ASM-n` | Assumption: believed, not verified; requirements that lean on it break with it |
| `Q-n` | Open question a requirement hangs on |

## Steps

1. **Collect sources** and number them before extracting anything, so the sweep in step 5 has a fixed set to account for. Existing code counts: it holds *current* requirements nobody wrote down. If the ask is thin, interview the user: users, scale, what "done" looks like, plus availability, recovery (RPO/RTO), retention, audit, data volume and who can see what. People under-state non-functional needs, so record silence as "no stated NFR", not as absence. If the user cannot answer now, file each gap as a `Q-n` and continue on a flagged assumption.
2. **Extract every statement**: needs, constraints, quiet assumptions, stated non-goals. Extract, don't interpret. Hedged statements ("maybe", "probably", "later") become `Q-n` rows asking for a decision, never out-of-scope rulings.
3. **Normalize** into one requirement per row:
   - *Atomic*: "upload, preview and delete files" is three requirements.
   - *Testable*: a number, a state or an observable behavior, never an adverb. Bad: "should be fast". Good: `NFR-3: p95 API latency ≤ 300 ms at 100 rps sustained`. If you cannot say how to check it, it becomes a `Q-n`.
   - *Solution-free*: "uses Redis" is a `CON-n` only if someone with authority said so; otherwise write the need (`NFR-n: session lookup ≤ 50 ms`).
   - Every Must and Should FR gets an **acceptance criterion** (Given/When/Then, or an observable outcome). Design and tests trace back to these.
4. **Prioritize** every FR and NFR with MoSCoW: Must, Should, Could, Won't-this-time. Constraints are Must; assumptions carry no priority. If a priority hangs on a question, write `Must? (Q-3)`.
5. **Forward sweep, source → requirement.** Give every extracted statement exactly one disposition: covered (`FR-4`, or `partially: FR-4; rest → Q-9`), out of scope, or `Q-n`. Nothing stays unmapped. This catches dropped intent.
6. **Backward sweep, requirement → source.** Cite each requirement's source with a short quote. A requirement with no source is either a smuggled design idea (delete it, or save it for the design) or an unstated assumption (make it an `ASM-n` and flag it). A quote that does not say what the requirement claims means you sharpen the requirement or open a `Q-n`.
7. **Conflicts and dependencies.** For each contradiction, state both sides with citations, propose a resolution, and park it as a `Q-n` unless the user already settled it. Record dependencies (`FR-5` needs `FR-2`); they set build order later. When a question resolves later, write the answer back with a dated note, because downstream docs cite these IDs.

## Done when

Small ask: the first line states the size, every FR has an acceptance criterion, and open questions are listed. The checks below are for full maps.

- [ ] The first line states "Full map."
- [ ] Every source statement has exactly one disposition in the Traceability table.
- [ ] Every requirement cites a source quote, or is an `ASM-n` flagged to the user.
- [ ] Every requirement is atomic and testable, and every Must and Should FR has an acceptance criterion.
- [ ] Every FR and NFR has a priority.
- [ ] Unanswered NFR topics are recorded as "no stated NFR" or a `Q-n`.

## Output

Full maps only: one Markdown file following `references/template.md`. Use the repo's docs convention; otherwise `docs/requirements-map.md`, and say where you put it. A typical feature fits in 100–150 lines; past ~200, trim prose and keep rows.

Present the map leading with the open questions, since only the user can move them. The map is **settled** when the user has answered the blocking questions or said to proceed on the assumptions. For a system or major feature, the next step is `/design-doc`.
