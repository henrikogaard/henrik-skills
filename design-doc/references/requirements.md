# Requirements and scope

Read this before writing the Requirements and Scope sections.

A requirements list answers questions. A requirements **map** also accounts for everything: every requirement cites the source it came from, and every source statement ends up as a requirement, an open question or an explicit out-of-scope line. That two-way accounting is the point. Without it, a list silently invents scope or drops half of what the stakeholder said.

Make gaps **visible**; do not close them by guessing. An honest open question is a deliverable. A requirement invented to fill a hole is a defect.

## IDs

| Prefix | Meaning |
|---|---|
| `S1`, `S2`… | Source: conversation, issue, doc, thread or existing code, with a location precise enough to re-find |
| `FR-n` | Functional requirement |
| `NFR-n` | Non-functional requirement (performance, scale, security, compliance, usability, cost) |
| `CON-n` | Constraint: deadline, budget, must-use or must-not-use technology |
| `ASM-n` | Assumption: believed, not verified; requirements that lean on it break with it |
| `Q-n` | Open question a requirement hangs on |

IDs never change once written. The design, the decisions, the build plan and the tests all cite them.

## Steps

1. **Collect sources** and number them before extracting anything, so the sweep in step 5 has a fixed set to account for. Existing code counts: it holds *current* requirements nobody wrote down. If the ask is thin, interview the user: users, scale, what "done" looks like, plus availability, recovery (RPO/RTO), retention, audit, data volume and who can see what. People under-state non-functional needs, so record silence as "no stated NFR", not as absence. If the user cannot answer now, file each gap as a `Q-n` and continue on a flagged assumption.
2. **Extract every statement**: needs, constraints, quiet assumptions, stated non-goals. Extract, don't interpret. Hedged statements ("maybe", "probably", "later") become `Q-n` rows asking for a decision, never silent out-of-scope lines.
3. **Normalize** into one requirement per row:
   - *Atomic*: "upload, preview and delete files" is three requirements.
   - *Testable*: a number, a state or an observable behavior, never an adverb. Bad: "should be fast". Good: `NFR-3: p95 API latency ≤ 300 ms at 100 rps sustained`. If you cannot say how to check it, it becomes a `Q-n`.
   - *Solution-free*: "uses Redis" is a `CON-n` only if someone with authority said so; otherwise write the need (`NFR-n: session lookup ≤ 50 ms`) and leave the answer to the design.
   - Every Must and Should FR gets an **acceptance criterion** (Given/When/Then, or an observable outcome). Phase 2 maps tests to these.
4. **Prioritize** every FR and NFR with MoSCoW: Must, Should, Could, Won't-this-time. Constraints are Must; assumptions carry no priority. If a priority hangs on a question, write `Must? (Q-3)`.
5. **Forward sweep, source → requirement.** Give every extracted statement exactly one disposition: covered (`FR-4`, or `partially: FR-4; rest → Q-9`), out of scope, or `Q-n`. Nothing stays unmapped. Record this in the Traceability table.
6. **Backward sweep, requirement → source.** Cite each requirement's source with a short quote. A requirement with no source is either a smuggled design idea (delete it, or move it to the design) or an unstated assumption (make it an `ASM-n` and flag it). A quote that does not say what the requirement claims means you sharpen the requirement or open a `Q-n`.
7. **Conflicts and dependencies.** For each contradiction, state both sides with citations, propose a resolution, and park it as a `Q-n` unless the user already settled it. Record dependencies (`FR-5` needs `FR-2`); they set the slice order in the build plan.

## Scope

Scope turns the requirements into a boundary the user approves:

- **In**: the requirement IDs this work delivers.
- **Out**: what this work will not do, each with who ruled it and when ("user, 2026-10-15"). Only the user rules something out; hedged statements stay `Q-n` until they do.
- **Later**: deferred items, each with its `Q-n` or the reason it waits.

## Small work

For small work, keep the same IDs but shrink the form: a short list of FRs with their acceptance criteria, any `CON-n`, the open questions, and scope as three one-line lists. Skip the Traceability, Dependencies and Conflicts tables when they would be empty or trivial.

## When answers arrive

When a `Q-n` is answered or a ruling changes, write it back into the doc with a dated note, update the affected requirements and scope, and add a change-log line. Downstream sections cite these IDs and go stale silently otherwise.
