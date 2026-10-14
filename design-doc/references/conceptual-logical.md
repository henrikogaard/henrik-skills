# Conceptual and logical levels

Read this before writing either level. Each numbered step is one section of the doc.

## Conceptual level

Test for this level: a reader follows it without knowing any implementation detail. If they would need one, it leaked in.

1. **Purpose.** One paragraph: what the system does, for whom, and what it pointedly does not do. Derive it from the requirements; do not freestyle.
2. **Context map.** The system as one box, with actors and external systems around it and the data that crosses each boundary, in and out. Use Mermaid or ASCII. Mark the **trust boundaries** (wherever data moves between trust levels) and name the top 2–3 threats at each, picking from spoofing, tampering, repudiation, disclosure, denial of service and elevation. This diagram is the fastest way to find a forgotten integration or trust decision. Every actor cites a source or requirement, and every external system named in a `CON-n` appears.
3. **Capabilities.** What the system can do, as verb phrases ("accept and route inbound events"), each mapped to the FR IDs it satisfies. Every FR lands in exactly one capability. Cross-cutting FRs (authentication, audit) get one designated cross-cutting capability instead of being spread across all of them. A capability with no FR is scope creep.
4. **Components.** Usually 3–7 black boxes; fewer is fine for a small system. One line of responsibility each. Name them after the domain, not the technology: "Booking Ledger", not "Redis Service".
5. **Domain concepts.** The nouns the design leans on, one line each. Define contested or muddy terms here and flag them; every later section inherits these words.

## Logical level

1. **Component contracts.** For each component: the operations it provides (name, intent, sync or async, and the guarantee it makes: at-least-once, exactly-once or best-effort) and the components it depends on. Contracts are promises, not signatures; signatures belong to the detailed level.
2. **Domain model.** Entities, relationships, cardinality, lifecycle states, and the invariants that matter ("a booking references exactly one active payment intent").
3. **Data ownership.** A table of datum → owner → readers. Every datum has exactly one owning component; others read it through the owner's contract, never around it.
4. **Integration.** For each link between components, and between a component and an external system: direction, family (request/response, event stream, batch file, poll), who commands, who subscribes and what is authoritative.
5. **Scenario walkthroughs.** Choose a set that together covers every Must FR and every NFR mechanism at least once; 3–5 usually suffices. Start with the riskiest: requirement conflicts, concurrency, NFRs near their limit. Walk each one as a numbered hop list naming the contract called at each hop, ending with the FRs it exercised.
6. **NFR mechanisms.** A table of NFR ID → mechanism → sufficiency argument → numeric (yes/no). The argument is one line of arithmetic or capacity reasoning. An NFR with no mechanism is a hope, not a design. Mark numeric NFRs: the detailed level must close them with budgets.
7. **Decisions and alternatives.** Pivotal choices only, written ADR-style: context, options, outcome. If the repo has an ADR convention, write each pivotal decision as a numbered ADR there and cite it here, so each can be superseded on its own.
8. **Risk register.** What could make this design wrong: the assumption it leans on most (carried `ASM-n` items belong here), the component with the least precedent, the NFR closest to its limit.

## Coverage table

The acceptance test for these two levels, and what the detailed level consumes to know nothing was lost.

| Direction | Rule | A failure means |
|---|---|---|
| Requirements → design | Every FR/NFR has a capability and a component, plus a mechanism for NFRs | The design silently drops a requirement |
| Design → requirements | Every component lists at least one requirement ID | Invented scope |
| Constraints | Every `CON-n` honored or escalated as a `Q-n` | The design ignored a constraint |
| Context map | Every actor cites a source; every `CON-n` external system appears | An invented actor, or an ignored constraint |
