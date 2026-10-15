# Class booking

Status: Approved (2026-10-10, gym owner)
Size: Full — new service with payments and concurrency
Owner: gym owner · Started: 2026-10-06 · Approved: 2026-10-10, gym owner
Working assumptions: none

## 1. Requirements
### Sources
| ID | Location | What it contributes |
|---|---|---|
| S1 | Slack, owner, 2026-10-02 | core ask |
| S2 | call notes, 2026-10-05 | scale, overbooking complaint |

### Requirements
| ID | Requirement | Priority | Acceptance criterion | Sources | Notes |
|---|---|---|---|---|---|
| FR-1 | Member books a place in a class slot | Must | Given a slot with a free place, when a member books, then they hold one place and the free count drops by one | S1 "book classes" | |
| FR-2 | Member cancels a booking | Must | Given a booking, when the member cancels, then the place is free again | S1 "cancel" | |
| FR-3 | Cancelling under 2 h before start charges a fee | Must | Given a booking starting in under 2 h, when cancelled, then a fee charge is recorded for Stripe | S1 "or they get charged" | amount → Q-2 |
| FR-4 | A member cannot book the same slot twice | Must | Given a member holding a place, when they book the same slot again, then the request is refused with "already booked" | S2 "people double-book themselves" | |
| NFR-1 | Booking confirms in ≤ 500 ms p95 at 50 bookings/s | Must | — | S2 "6am Monday rush" | |
| NFR-3 | A slot is never overbooked, even under concurrent requests | Must | Given a slot with one free place and two simultaneous requests, then exactly one succeeds and the other is refused with "class full" | S2 "double bookings are the worst" | |
| CON-1 | Live before 2026-12-01 | Must | — | S1 | |
| CON-2 | Payments through the existing Stripe account | Must | — | S1 | |
| CON-3 | Python 3, standard library, SQLite for now | Must | — | S2 "keep it simple, we host it ourselves" | |

## 2. Scope
- In: FR-1, FR-2, FR-3, FR-4, NFR-1, NFR-3, CON-1, CON-2, CON-3
- Out: attendance analytics — gym owner, 2026-10-10
- Later: waitlist that fills freed places (FR-5, Q-3) — owner wants it after launch

## 3. Conceptual design
### Purpose
Let members book and cancel gym class places, never overbook a class, and charge late cancellations through Stripe.

### Components
| Component | Responsibility | Requirement IDs |
|---|---|---|
| Booking Ledger | Holds slots, places and bookings; enforces capacity | FR-1, FR-2, FR-4, NFR-1, NFR-3 |
| Fee Billing | Records late-cancel fees and charges them through Stripe | FR-3, CON-2 |

## 4. Logical design
### Component contracts
- Booking Ledger `book(member, slot)` → booking or refusal (`class full`, `already booked`); synchronous; exactly-once per (member, slot).
- Booking Ledger `cancel(booking)` → freed place; emits `booking.cancelled` with the cancel time.
- Fee Billing subscribes to `booking.cancelled`; at-least-once; idempotent per booking.

### Data ownership
| Datum | Owner | Readers |
|---|---|---|
| Slots and capacity | Booking Ledger | Fee Billing (start time, via event) |
| Bookings | Booking Ledger | Fee Billing (via event) |
| Fee records | Fee Billing | none |

### NFR mechanisms
| NFR | Mechanism | Arithmetic | Numeric |
|---|---|---|---|
| NFR-3 | Book is one transaction: a conditional update that only succeeds while booked < capacity, plus a unique (member, slot) constraint | one row lock per slot; concurrent books on a slot serialize | no |
| NFR-1 | Book touches one slot row and inserts one booking row; no external calls on the path | ~2 ms per transaction × 50/s = 10% of one SQLite writer | yes |

## 5. Decisions
### D-1: Enforce capacity in the database transaction (Accepted, 2026-10-09)
Context: NFR-3 must hold under concurrent requests.
Options: (a) check-then-insert in application code; (b) conditional update inside one transaction.
Choice: (b). The database serializes writers on the slot, so two requests cannot both take the last place.
Consequences: every book is a short write transaction; long reads must not hold the write lock.

## 6. Coverage
| Requirement | Component | Mechanism | Slice | Status |
|---|---|---|---|---|
| FR-1, FR-4, NFR-3 | Booking Ledger | D-1 | 1 | covered |
| FR-2 | Booking Ledger | — | 2 | covered |
| FR-3, CON-2 | Fee Billing | — | 3 | covered |
| NFR-1 | Booking Ledger | no external calls on book | 1 | covered |

## 7. Build plan
| Slice | What it delivers | Requirement IDs | Status |
|---|---|---|---|
| 1 | Book a place with capacity and duplicate checks | FR-1, FR-4, NFR-3 | Planned |
| 2 | Cancel a booking | FR-2 | Planned |
| 3 | Late-cancel fee recorded and charged through Stripe | FR-3, CON-2 | Planned |

## 8. Open questions
| ID | Question | Blocks | Asked of |
|---|---|---|---|
| Q-2 | What is the late-cancel fee amount? | FR-3 | gym owner |
| Q-3 | Should a freed place go to a waitlist automatically? | FR-5 | gym owner |

## 9. Detailed design
<!-- written per slice, just before it is built -->

## 10. Verification
| Acceptance criterion | Test | Result | Commit |
|---|---|---|---|

## 11. Codebase deltas and change log
### Codebase deltas
### Change log
- 2026-10-10: Approved by the gym owner.
