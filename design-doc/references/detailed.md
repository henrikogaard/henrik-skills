# Detailed design, one slice at a time

Read this before writing a slice's detailed design. Write it just before building that slice, under "Detailed design → Slice n", so it describes code that is about to exist rather than code imagined months ahead.

The bar: an engineer or agent who was not in the conversation could build this slice from the doc without asking a question the doc should have answered. Put every question you cannot answer in "Open questions".

Inputs, in order of authority: the logical design in this doc (structure and contracts come from there; detailed design deepens it and never re-architects it), the slice's requirement IDs and acceptance criteria, then the code as it actually is. If the code contradicts the design, record it under "Codebase deltas" with a ruling.

This is where products and versions get pinned. Each pivotal choice becomes a `D-n` entry in the decisions log, with its alternatives.

## Depth

Spend depth where the risk is: components that own data, components behind the hardest NFRs, and anything in the risk register. A simple CRUD change gets a short paragraph; padding it is ceremony. Say which parts got the short treatment and why.

## For each component the slice touches

1. **Modules.** Package or folder layout with one line per module's job, for new modules only. Implementers otherwise each invent a different layout.
2. **Interfaces.** Every operation the slice adds or changes, made concrete: endpoint (method, path, auth) or function signature; request and response schemas with field names, types and required/optional; **one literal example** of a request and response (an example catches more ambiguity than a page of prose); each error case; idempotency and rate limits where they matter. A consumer must be able to mock the component from this section alone.
3. **Data changes.** Tables or collections with fields, types, constraints and defaults. Justify each index by a query ("`(user_id, created_at)` serves the feed query NFR-4 pins to 50 ms"). Retention. Numbered migration steps, including backfill, ordered so each step leaves the system working.
4. **Sequences.** The slice's scenarios at message level: which endpoint, query or event, in order, including the failure branch. For externally reachable interfaces, add an abuse branch: what an attacker tries at this hop, tied to the context map's trust boundaries.
5. **State machines** for any entity with a lifecycle that the slice adds or changes: states, legal transitions, triggers, and the transitions that must be illegal. Illegal transitions are where bugs live.
6. **Failure modes.** For each external dependency the slice calls: behavior on timeout, on retry (say whether the operation is idempotent, and why), on poison input, and when the dependency is fully down. State the fallback even when it is "fail closed with this error".
7. **Observability.** Named metrics that would show this slice misbehaving, the log events that matter (with fields), and the NFR each one evidences.
8. **Security and config.** Authentication and authorization per interface; secrets and where they live (by name, never the value); data classification; config knobs with defaults.

## For the slice as a whole

9. **Tests.** A table of acceptance criterion (requirement ID) → test name → type (unit, contract, integration, e2e, load/soak) → location. Every acceptance criterion in the slice gets at least one test. A numeric NFR the slice affects gets a load or soak test, or a stated reason it waits for a later slice. After building, copy each result into the doc's Verification table.
10. **Budget.** If the slice affects a numeric NFR, allocate the number across its hops (latency) or size its components (throughput, storage), so the parts sum under the target.
11. **Rollout.** For changes to live behavior: feature flag, staged rollout, rollback step.

## Once per doc, in the first slice that needs it

- **Interface conventions**: style (REST, RPC, events), versioning, pagination, error model, compatibility rules. Write them once so later slices do not diverge.

## After building the slice

Update the doc in the same commit as the code: the Verification table (criterion → test → result → change: the PR, or "this change", since a commit cannot contain its own hash), the status line, the build plan, any Codebase deltas, any new `D-n` entries, and a change-log line. If the code had to differ from this detailed design, fix the detailed design to match what was built and say why in the delta.
