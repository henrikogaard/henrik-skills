---
name: conceptual-logical-design
description: Design a system at two levels — conceptual (purpose, context, capabilities, black-box components) then logical (component contracts, domain model, data ownership, scenario walkthroughs, NFR mechanisms) — with every element traced back to a requirement. Use when asked for the architecture or high-level design of a whole system or major feature, or when arriving with a requirements map, after requirement mapping and before detailed design. Module-level design inside an existing codebase is codebase-design's territory.
---

Two levels, one rule each:

- **Conceptual** — what the system is and does, explainable to a non-engineer. Components are black boxes with a one-line responsibility each. If a reader needs to know an implementation detail to follow it, the detail leaked in.
- **Logical** — how the system is shaped: components with contracts, the domain model, who owns which data, and how scenarios flow through. Technology **families** are allowed ("persistent queue", "relational store"); technology **products** are not ("Kafka", "Postgres") unless a `CON-n` constraint forces one. Pinning products early locks in tradeoffs nobody examined.

The two levels share one non-negotiable: **traceability to the requirements map**. If one exists (from `/requirement-mapping`), load it and cite requirement IDs throughout. If it doesn't exist, say so and either run that skill first or map requirements inline — designing against an unmapped ask is how systems acquire components nobody asked for.

Scale the artifact to the system. A change spanning a few components inside a settled architecture may need only the conceptual pass and a coverage table — compress the logical sections, say what you compressed and why, rather than padding each heading to the template. A feature sized for codebase-design (module-level, one codebase, no system boundary) shouldn't be run through this pipeline at all.

Before Pass 2, present any **blocking questions** to the user — any open `Q-n` whose answer would change the domain model or a data owner. If the user can't answer, design against a recorded working assumption and flag it at the top of the artifact; a wrong assumption adopted silently invalidates everything downstream of it.

## Pass 1 — Conceptual

1. **Purpose.** One paragraph: what the system does for whom, and what it pointedly does not do. Derive it from the requirements, don't freestyle.
2. **Context map.** The system as a single box, with actors and external systems around it and the data that crosses each boundary, in and out. Mermaid or ASCII. Mark the **trust boundaries** — wherever data crosses between trust levels — and name the top 2–3 threats at each (STRIDE-lite: spoofing, tampering, repudiation, disclosure, denial, elevation; take what applies). This diagram is the fastest way to discover you've forgotten an integration or a trust decision.
3. **Capabilities.** What the system can do, as verb phrases ("accept and route inbound events"), each mapped to the FR IDs it satisfies. Every FR lands in exactly one capability — cross-cutting FRs (authentication, audit) get one designated cross-cutting capability rather than being smeared across all of them — and every capability has at least one FR: a capability with no tenant is scope creep.
4. **Conceptual components.** 3–7 black boxes — fewer is fine for a small system; the count serves the system, not the template. One line of responsibility each, named after the domain, not the technology ("Booking Ledger", not "Redis Service").
5. **Domain concepts.** The nouns the design will lean on, defined in one line each. If terminology is contested or muddy, call the Skill tool for "domain-modeling" if you have it and sharpen it there; otherwise define the contested terms inline and flag them. Every later artifact inherits these words.

## Pass 2 — Logical

1. **Component contracts.** For each conceptual component, now opened up: the operations it provides (name, intent, sync/async, the guarantee it makes — at-least-once, exactly-once, best-effort), and which components it depends on to deliver them. Contracts are promises, not signatures — signatures come in `/detailed-design`.
2. **Domain model.** Entities, relationships, cardinality, lifecycle states, and the invariants that matter ("a booking references exactly one active payment intent"). This is where the domain-modeling vocabulary pays off.
3. **Data ownership.** Every datum has exactly one owning component; others read it through the owner's contract, never around it. Two owners for one datum is the design smell that becomes a consistency bug — call it out where you find it.
4. **Integration.** Component-to-component and component-to-external: direction, family (request/response, event stream, batch file, poll), and what happens semantically on each side (who commands, who subscribes, what's authoritative).
5. **Scenario walkthroughs.** Walk a set that collectively covers **every Must FR and every NFR mechanism at least once** (3–5 scenarios typically suffices; more for larger systems). Choose the riskiest ones first: the conflicts table, concurrency-relevant FRs, and NFRs near their limit. Walk each through the components step by step, naming the contract called at each hop. **The walkthrough is the design's stress test**: a walk that stutters — no component owns a step, data arrives with no owner, an invariant can't hold mid-flow — means the design has a hole, and you fix the design, not the walkthrough.
6. **NFR mechanisms.** Each NFR ID → the mechanism that satisfies it, **argued sufficient in one line of arithmetic or capacity reasoning** ("100 rps × 2 KB payload = 200 KB/s steady; one replica handles 10× that"). "Add a cache" is not a mechanism row. Mark each numeric NFR — `/detailed-design` must close those with budgets. An NFR with no mechanism is a hope, not a design.
7. **Decisions & alternatives.** For the pivotal choices only — **pivotal** means reversing the choice would touch more than one component's contract or force a data migration — record 2–3 alternatives and why the chosen one wins, ADR-style (context, options, outcome). Where the repo has an ADR convention, pivotal decisions become numbered ADRs there and this section cites them, so they can be superseded individually. Don't pad this with decisions nobody contested; a decision record nobody would have argued with is noise. Where a tradeoff is genuinely balanced, present the options to the user with a recommendation instead of choosing silently.
8. **Risk register.** What could make this design wrong: the assumption it most depends on (carried `ASM-n` items are prime entries), the component with the least precedent, the NFR closest to its limit.

## Coverage, both ways, before you call it done

| Direction | Rule | What a failure means |
|---|---|---|
| Requirements → design | every FR/NFR has a home — capability + component, plus a mechanism for NFRs | a requirement the design silently drops |
| Design → requirements | every component justified by ≥1 requirement ID | invented scope — cut it or find its tenant |
| Constraints | every `CON-n` honored or escalated as a Q | a constraint the design ignored |
| Context map | every actor cites a source or requirement; every `CON-n` external system appears | an invented actor; a constraint the design ignored |

Produce the coverage table in the artifact. It's the acceptance test for this skill, and it's what `/detailed-design` will consume to know nothing was lost.

## Artifact

One Markdown file, both levels, same location convention as the requirements map — default `docs/design/conceptual-logical-design.md`. Default target ~150–300 lines for a mid-size system; a longer doc should mean more components and NFRs, not more commentary:

```markdown
# <System> — conceptual & logical design
## Requirements baseline
<!-- link to the requirements map, or "mapped inline" with the inline map under this heading; list blocking Q-n with the working assumption chosen for each; continue the map's Q numbering for new questions -->

## Conceptual
### Purpose
### Context map   <!-- with trust boundaries and top threats -->
### Capabilities   <!-- table: capability | FR IDs -->
### Conceptual components   <!-- table: component | responsibility | requirement IDs -->
### Domain concepts

## Logical
### Component contracts   <!-- per component: provides | guarantees | depends on -->
### Domain model
### Data ownership   <!-- table: datum | owner | readers -->
### Integration
### Scenario walkthroughs   <!-- one numbered hop-list per scenario, contract named per hop, ending in the FRs exercised; the set covers every Must FR and NFR mechanism -->
### NFR mechanisms   <!-- table: NFR ID | mechanism | sufficiency argument | numeric? -->
### Decisions & alternatives   <!-- pivotal only; ADRs where the repo has a convention -->
### Risk register

## Coverage
<!-- one row per requirement: Req ID | Capability | Component | Mechanism (NFRs) | Status (covered / escalated as Q-n) -->
<!-- one row per component: its tenant requirement IDs; every row resolves or escalates -->

## Open questions carried forward
```

Present the design leading with the decisions that need the user's eye (the balanced tradeoffs and the risks), then hand off to `/detailed-design` when the coverage table closes.
