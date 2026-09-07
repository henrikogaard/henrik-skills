---
name: requirement-mapping
description: Turn a fuzzy ask — a conversation, an issue, an RFC, or a rant — into a requirements map: numbered, testable requirements traced in both directions to their sources, with gaps, conflicts, and open questions surfaced instead of papered over. Use when the user mentions requirements, a PRD, acceptance criteria, traceability, or asks "what are we actually building" before design starts.
---

A requirements **list** answers questions. A requirements **map** locates things: every requirement is tied to the source it came from, and every source statement is accounted for by some requirement, some open question, or an explicit out-of-scope ruling. That bidirectional accounting is the whole skill. A list that fails it silently invents scope or drops half of what the stakeholder said, and nobody notices until implementation.

The map's job is to make the gaps **visible**, not to close them by guessing. An honestly unresolved question is a deliverable; a requirement invented to fill the hole is a defect.

Size the ask before starting. One source, a handful of needs, an obvious definition of done — say so and keep the map to a page, or skip it and carry the requirements inline to whatever comes next. The process below exists for work where dropped or invented intent is expensive; running the full ceremony on a small ask is a failure mode, not thoroughness. If the ask turns out small mid-mapping, shrink the artifact rather than finishing the ceremony.

## Inputs are sources

Everything the requirements could come from is a **source**, numbered as it's found:

- The current conversation, including the user's offhand remarks and corrections
- Issues, RFCs, Slack threads, meeting notes, emails the user points at
- Repo docs (README, specs under `docs/`, ADRs, existing CONTEXT.md)
- Existing code and behavior, when the feature touches a live system — the code is a source of *current* requirements even if nobody wrote them down

Record each as `S1`, `S2`, … with a location precise enough to re-find: a file path, an issue link, a quote from the conversation. A requirement that cites nothing is suspect (see the backward sweep).

## Process

### 1. Collect the sources

List them before extracting anything, so the coverage sweep has a fixed population to account for. If the ask is thin (no scale, no users, no definition of done), interview the user first — a few sharp questions about users, scale, and what "done" looks like, plus the NFR checklist: availability, recovery (RPO/RTO), retention, audit, expected data volume, and who can see what. Stakeholders systematically under-state non-functional needs, so silence is recorded as an explicit "no stated NFR" ruling, not left as absence. If the user can't answer — AFK, done for the day — record each unanswered question as a `Q-n` and proceed on a flagged assumption; a map is allowed to ship with open questions, so don't stall the turn waiting.

### 2. Extract every statement

Sweep each source for: functional needs (what it must do), non-functional needs (performance, scale, security, compliance, usability, cost), constraints (deadlines, budget, must-use or must-not-use tech, team), assumptions someone is quietly making, and stated non-goals. Extract, don't interpret — a vague source stays vague until step 3 sharpens or files it. Statements hedged with "maybe", "probably", or "later" are questions, not rulings: they become `Q-n` rows asking for an explicit decision, never an out-of-scope line. This population — every extracted statement — is what the forward sweep in step 5 must account for.

### 3. Normalize into requirements

One requirement per row, each with an ID and a type prefix:

- `FR-n` — functional
- `NFR-n` — non-functional
- `CON-n` — constraint
- `ASM-n` — assumption (believed, not verified; if it breaks, these requirements break with it)
- `Q-n` — open question: something a requirement hangs on that nobody has answered

Normalization rules, with the reasons:

- **Atomic.** "Users can upload, preview, and delete files" is three requirements that will be prioritized and built separately whether or not you glue them together.
- **Testable.** If you can't say how you'd check it, it's not a requirement yet — sharpen it or demote it to a Q. Bad: "the system should be fast." Good: `NFR-3: p95 API latency ≤ 300 ms at 100 rps sustained.` What makes it testable is a number, a state, or an observable behavior — not an adverb.
- **Solution-free.** "Uses Redis" is a constraint only if someone with authority said so; otherwise the need is `NFR-n: session lookups ≤ 50 ms` and Redis is a design answer that isn't yours to give yet.
- **Un-testable or unattributable statements become Q-n or out-of-scope rulings**, never silently dropped.

Every Must and Should FR also gets an **acceptance criterion** — Given/When/Then, or a stated observable outcome — recorded in its row. These are the link `/detailed-design` later maps tests to; a map without them leaves the pipeline's traceability promise unbacked.

### 4. Prioritize

MoSCoW (Must / Should / Could / Won't-this-time) on every FR and NFR. Constraints are Must by definition; assumptions carry no priority (they're either true or the map changes). When a priority hangs on an open question, write it `Must? (Q-3)` so the question stays visible in the row.

### 5. Forward sweep: source → requirement

Walk every statement extracted in step 2 and assign it exactly one disposition: covered (wholly, or partially — `partially: FR-4; remainder → Q-9`), out of scope, or `Q-n`. **Nothing stays unmapped.** This sweep is where dropped stakeholder intent gets caught. Out-of-scope rulings live in the artifact's Out of scope section; the Traceability table is the index proving every statement reached a disposition, citing sub-source precision where one source splits (`S2 ¶"audit trail"`).

### 6. Backward sweep: requirement → source

Walk every requirement and cite its source(s) with a short quote. Two failure modes fall out:

- **Invented requirements** — citable to no source. Either the mapper smuggled in a design idea (delete it, or hand it to `/conceptual-logical-design`, where design answers belong), or it encodes an unstated assumption (promote to `ASM-n`, cited as such, and flag it to the user).
- **Distorted requirements** — the quote doesn't actually say what the requirement claims. Sharpen the requirement to match the quote or open a Q about the gap.

### 7. Conflicts, dependencies, and re-baselining

- Contradictions between requirements (or between a requirement and a constraint): state both sides with their citations, propose a resolution, and park it as a Q unless the user already settled it.
- Dependencies between requirements (`FR-5` needs `FR-2` first): record them; they drive build order later in the pipeline.
- When a Q later resolves or a ruling reverses, write the resolution back into the map with a delta note — downstream documents cite these IDs, and they go stale silently otherwise.

## Artifact

One Markdown file. Follow the repo's convention for where design docs live; if there is none, `docs/requirements-map.md` and say where you put it. A typical feature's map fits in 100–150 lines; past ~200 the prose is crowding out the tables — trim prose, keep rows.

```markdown
# Requirements map — <feature/system>

## Sources
| ID | Location | What it contributes |
| S1 | conversation, 2026-09-05 | core ask, scale hints |

## Requirements
<!-- acceptance criteria in the AC column for every Must/Should FR -->
| ID | Requirement | Priority | AC | Sources | Notes |
| FR-1 | … | Must | given/when/then | S1 "…" | |
| NFR-1 | … | Should | — | S2 "…" | |
| CON-1 | … | Must | — | S1 | deadline |
| ASM-1 | … | — | — | inferred from S3 | unverified |

## Traceability
<!-- one row per extracted statement; ¶ marks sub-source precision; out-of-scope rows point at the Out of scope section -->
| Source statement | Disposition |
| S1 "book sessions" | FR-1 |
| S2 ¶"audit trail" | NFR-2 |
| S2 ¶"maybe analytics" | Q-7 → out of scope (user ruled, this session) |

## Dependencies
| Requirement | depends on | <!-- drives build order downstream -->
| FR-5 | FR-2 | |

## Conflicts
| Requirements | Conflict | Proposed resolution | Status |
| FR-3 vs NFR-2 | … | … | Q-6 |

## Open questions
| ID | Question | Blocks | Asked of |
| Q-1 | … | FR-3, NFR-1 | user |

## Out of scope
<!-- the canonical home of rulings; the Traceability table indexes them -->
- <ruling> — <source citation or "user, this session">
```

Present the map, then lead with the open questions: they're the part only the user can move. The map is **settled** when the user has answered the blocking questions or explicitly said to proceed on assumptions — then the next skill in the pipeline is `/conceptual-logical-design`.
