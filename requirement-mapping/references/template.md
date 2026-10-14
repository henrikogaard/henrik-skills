# Requirements map skeleton

Keep the sections in this order. Tables over prose.

```markdown
# Requirements map — <feature or system>

## Sources
| ID | Location | What it contributes |
|---|---|---|
| S1 | conversation, 2026-09-05 | core ask, scale hints |
| S2 | `docs/rfc-12.md` | audit and retention needs |

## Requirements
<!-- an acceptance criterion in the AC column for every Must and Should FR -->
| ID | Requirement | Priority | AC | Sources | Notes |
|---|---|---|---|---|---|
| FR-1 | Member can book a session | Must | Given a free slot, when the member books, then the slot shows as taken | S1 "book sessions" | |
| NFR-1 | Booking audit kept 2 years | Should | — | S2 ¶"audit trail" | |
| CON-1 | Live before 2026-12-01 | Must | — | S1 | deadline |
| ASM-1 | One timezone per site | — | — | inferred from S3 | unverified |

## Traceability
<!-- one row per extracted statement; ¶ marks a sub-part of a source -->
| Source statement | Disposition |
|---|---|
| S1 "book sessions" | FR-1 |
| S2 ¶"audit trail" | NFR-1 |
| S2 ¶"maybe analytics" | Q-7 → out of scope (user ruled, 2026-09-05) |

## Dependencies
| Requirement | Depends on |
|---|---|
| FR-5 | FR-2 |

## Conflicts
| Requirements | Conflict | Proposed resolution | Status |
|---|---|---|---|
| FR-3 vs NFR-2 | … | … | Q-6 |

## Open questions
| ID | Question | Blocks | Asked of |
|---|---|---|---|
| Q-1 | … | FR-3, NFR-1 | user |

## Out of scope
<!-- the home of every out-of-scope ruling; the Traceability table points here -->
- <ruling> — <source citation, or "user, <date>">
```
