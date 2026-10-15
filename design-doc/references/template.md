# Design doc skeleton

One file per piece of work: `docs/design/<slug>.md` unless the repo has its own convention. Keep the headings in this order so people and agents find them. Leave out a section that would be empty; for small work, collapse Conceptual and Logical into one short "Design" section.

Phase 1 writes sections 1–8 and stops for approval. Phase 2 adds to sections 9–11 one slice at a time.

```markdown
# <Work title>

Status: Draft
Size: <Small | Full> — <one-line reason>
Owner: <who asked> · Started: <date> · Approved: <date, who, or "not yet">
Working assumptions: <assumptions adopted while the user was away, or "none">

## 1. Requirements
### Sources
| ID | Location | What it contributes |
|---|---|---|
### Requirements
| ID | Requirement | Priority | Acceptance criterion | Sources | Notes |
|---|---|---|---|---|---|
### Traceability          <!-- full size only: source statement | disposition -->
### Dependencies and conflicts   <!-- full size only, and only if there are any -->

## 2. Scope
- In: <requirement IDs>
- Out: <item — who ruled, when>
- Later: <item — Q-n or reason>

## 3. Conceptual design
### Purpose
### Context map            <!-- trust boundaries and top threats -->
### Capabilities           <!-- capability | FR IDs -->
### Components             <!-- component | responsibility | requirement IDs -->
### Domain concepts

## 4. Logical design
### Component contracts    <!-- provides | guarantees | depends on -->
### Domain model
### Data ownership         <!-- datum | owner | readers -->
### Integration
### Scenario walkthroughs  <!-- numbered hops, contract per hop, FRs exercised -->
### NFR mechanisms         <!-- NFR ID | mechanism | arithmetic | numeric? -->
### Risk register

## 5. Decisions
### D-1: <title> (<Proposed | Accepted | Superseded by D-n>, <date>)
Context: … Options: … Choice: … Consequences: …

## 6. Coverage
<!-- requirement ID | capability | component | mechanism (NFRs) | slice | status -->

## 7. Build plan
| Slice | What it delivers | Requirement IDs | Status |
|---|---|---|---|
| 1 | <thinnest end-to-end path through the riskiest contract> | FR-1, NFR-3 | Planned |

## 8. Open questions
| ID | Question | Blocks | Asked of |
|---|---|---|---|

## 9. Detailed design
### Slice 1               <!-- written just before slice 1 is built; see references/detailed.md -->

## 10. Verification
| Acceptance criterion | Test | Result | Commit |
|---|---|---|---|

## 11. Codebase deltas and change log
### Codebase deltas        <!-- where code and design differ | ruling -->
### Change log
- <date>: <what changed in this doc and why>
```
