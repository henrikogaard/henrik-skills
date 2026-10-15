# Requirements map — class booking

## Sources
| ID | Location | What it contributes |
|---|---|---|
| S1 | Slack, owner, 2026-10-02 | core ask |
| S2 | call notes, 2026-10-05 | scale, payments |

## Requirements
| ID | Requirement | Priority | AC | Sources |
|---|---|---|---|---|
| FR-1 | Member books a class slot from a phone | Must | Given a slot with space, when the member books, then they hold a place and the count drops by one | S1 "book classes on their phone" |
| FR-2 | Member cancels a booking | Must | Given a booking, when cancelled, then the place frees up | S1 "cancel" |
| FR-3 | Late cancellation (< 2 h before start) charges a fee | Must | Given a booking starting in under 2 h, when cancelled, then the fee is charged through Stripe | S1 "cancel up to 2h before or they get charged" |
| FR-4 | Coach sees the attendee list for their class | Must | Given a coach, when they open their class, then they see every booked member | S1 "coaches should see who's coming" |
| FR-5 | Waitlist fills a freed place automatically | Should | Given a full class with a waitlist, when a place frees up, then the first waitlisted member is booked and notified | S2 "waitlist" |
| NFR-1 | Booking confirms in ≤ 500 ms p95 at 50 bookings/s (class release peak) | Must | — | S2 "everyone books at 6am Monday" |
| NFR-2 | Supports 5 sites, 400 classes/week each | Should | — | S1 "maybe 5 next year" |
| NFR-3 | A class is never overbooked | Must | — | S2 "double bookings are the worst" |
| CON-1 | Live before 2026-12-01 | Must | — | S1 |
| CON-2 | Payments go through the existing Stripe account | Must | — | S1 "we use stripe already" |
| CON-3 | Data stored in PostgreSQL (the team's existing database) | Must | — | S2 "we only run postgres" |

## Open questions
| ID | Question | Blocks |
|---|---|---|
| Q-1 | Is the late-cancel fee per site or global? | FR-3 |
