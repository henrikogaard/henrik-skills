# Doc skeleton

Delete the sections for levels you did not write. Keep the headings in this order so downstream readers and tools find them.

```markdown
# <System> — design

Depth: <conceptual | conceptual + logical | all three> — <one-line reason>
Working assumptions: <each blocking Q-n with the assumption adopted, or "none">

## Requirements baseline
<!-- link to the requirements map, or the inline map flagged as such -->

## Codebase deltas
<!-- table: conflict | ruling (design yields / code migrates / Q-n); omit if no code exists -->

## Conceptual
### Purpose
### Context map            <!-- trust boundaries and top threats -->
### Capabilities           <!-- table: capability | FR IDs -->
### Components             <!-- table: component | responsibility | requirement IDs -->
### Domain concepts

## Logical
### Component contracts    <!-- per component: provides | guarantees | depends on -->
### Domain model
### Data ownership         <!-- table: datum | owner | readers -->
### Integration
### Scenario walkthroughs  <!-- numbered hops, contract per hop, FRs exercised -->
### NFR mechanisms         <!-- table: NFR ID | mechanism | sufficiency argument | numeric? -->
### Decisions and alternatives
### Risk register

## Detailed
### Decisions made here    <!-- products and versions pinned, with alternatives -->
### <Component A>          <!-- modules, interfaces, data model, sequences, states, failure modes, observability, security and config -->
### <Component B>
### Budget and capacity closure
### Interface conventions
### Test strategy          <!-- table: acceptance criterion | test | type | location -->
### Rollout
### Implementation order   <!-- slices, each naming the requirement IDs it makes testable -->

## Coverage
<!-- one row per requirement: ID | capability | component | mechanism (NFRs) | status (covered / Q-n) -->

## Open questions
<!-- continue the requirements map's Q-n numbering -->
```
