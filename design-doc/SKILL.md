---
name: design-doc
description: Write a traced design doc for a whole system or a major feature, at up to three levels — conceptual (purpose, context, black-box components), logical (contracts, domain model, data ownership, scenario walkthroughs, NFR mechanisms) and detailed (interfaces, schemas, failure modes, test strategy, build order). Use when asked for an architecture, a system design, a high-level or detailed design, a tech spec, "spec the API" or "design the schema", or when a requirements map is ready for design. Not for a change inside one module of an existing codebase.
---

# Design doc

One doc, up to three levels. Each level deepens the one before it and never re-architects it.

| Level | Answers | Technology named |
|---|---|---|
| Conceptual | What the system is and does, in words a non-engineer follows | None |
| Logical | How it is shaped: contracts, data owners, flows | Families only ("relational store", "persistent queue"), unless a `CON-n` forces a product |
| Detailed | What an implementer builds, with no question left that the doc should answer | Products, versions, schemas, endpoints |

Products wait until the detailed level because pinning one early locks in tradeoffs nobody examined.

## Before you start

1. **Find the requirements map** (from `/requirement-mapping`). Every design element cites requirement IDs (`FR-n`, `NFR-n`, `CON-n`, `ASM-n`). If no map exists, say so, then either run that skill first or map the requirements inline under "Requirements baseline" and flag it.
2. **Pick the depth and say why** in the doc's first lines:
   - *Conceptual only*: a change of a few components inside a settled architecture.
   - *Conceptual + logical*: a new system or a major feature.
   - *All three*: the doc goes to implementers who were not in this conversation.
3. **Read the code** if it exists. Where code and design disagree, record each conflict under "Codebase deltas" with a ruling: the design yields, the code migrates, or it becomes a `Q-n`.
4. **Ask blocking questions first**: any open `Q-n` whose answer would change the domain model, a data owner or a pinned product. If the user cannot answer, adopt a working assumption, write it at the top of the doc, and add it to the risk register.

## Write each level

Read the reference for a level before writing it. They hold the step lists and the reasons.

- Conceptual and logical: `references/conceptual-logical.md`
- Detailed: `references/detailed.md`
- Doc skeleton: `references/template.md`

## The rules that matter most

- **Trace both ways.** Every requirement has a home (capability + component, plus a mechanism for NFRs). Every component is justified by at least one requirement. A component with no requirement is invented scope: cut it or find its requirement.
- **One owner per datum.** Other components read through the owner's contract. Two owners is a future consistency bug; call it out.
- **Walkthroughs are the stress test.** Walk the riskiest scenarios hop by hop. A step with no owner, or an invariant that cannot hold mid-flow, means the design has a hole. Fix the design, not the walkthrough.
- **NFR mechanisms show arithmetic.** "100 rps × 2 KB = 200 KB/s; one replica handles 10×" is a mechanism. "Add a cache" is not.
- **Record only pivotal decisions.** Pivotal means reversing it touches more than one component's contract or forces a data migration. Give 2–3 alternatives and why the chosen one wins. Where a tradeoff is balanced, ask the user instead of choosing silently.
- **Unknowns are visible.** Put them in "Open questions", continuing the map's `Q-n` numbering. An honest gap beats a silent guess.
- **Scale to the system.** A small system gets short sections. Say what you compressed and why; never pad a heading to match the template.

## Done when

- [ ] Depth chosen and stated, with the reason.
- [ ] Coverage table closes: every requirement has a home or is escalated as a `Q-n`, and every component lists its requirement IDs.
- [ ] Every `CON-n` is honored or escalated.
- [ ] The scenario walkthroughs together exercise every Must FR and every NFR mechanism.
- [ ] Every numeric NFR has a mechanism with arithmetic (logical) and, at detailed depth, a budget that sums under the target.
- [ ] Detailed depth only: every acceptance criterion maps to a named test, and each interface can be mocked from the doc alone.

## Output

One Markdown file. Use the repo's docs convention; otherwise `docs/design/<system>-design.md`, and say where you put it. Rough size: 150–300 lines for conceptual + logical on a mid-size system; detailed adds about 80–120 lines per deep component. Length should come from components and requirements, not commentary.

Present the doc leading with what needs the user's eye: balanced tradeoffs, products pinned at the detailed level, the top risks and the open questions. Then give the implementation order, if the doc has one.
