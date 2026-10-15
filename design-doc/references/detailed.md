# Detailed level

The bar: an engineer or agent who has never spoken to you implements the system without asking a question this doc should have answered. Answer every question you can predict. Put every question you cannot answer in "Open questions".

Inputs, in order of authority: the logical level (structure and contracts come from there), the requirements map (acceptance criteria, priorities, dependencies), then the codebase's actual conventions. If the logical level was skipped, derive a minimal one first and flag it. Never invent acceptance criteria silently; if the map has none, reconstruct them from the coverage table and flag that.

This is where technology gets pinned. Each pivotal product or version choice goes under "Decisions made here" with its alternatives.

## Depth per component

Spend depth where the risk is: components named in the risk register, components that own data, and components behind the hardest NFRs. A simple CRUD component gets a short paragraph; padding it to match the others is ceremony. Say which components got the short treatment and why. If the whole system is small (a handful of components, no numeric NFRs), use one section for all of them and say so up front.

## Per component

1. **Modules.** Package or folder layout with one line per module's job. Implementers otherwise each invent a different layout.
2. **Interfaces.** Every operation from the logical contract, made concrete: endpoint (method, path, auth) or function signature; request and response schemas with field names, types and required/optional; **one literal example** of a request and response (an example catches more ambiguity than a page of prose); each error case; idempotency and rate limits where they matter. A consumer must be able to mock the component from this section alone.
3. **Physical data model.** Tables or collections with fields, types, constraints and defaults. Justify each index by a query ("`(user_id, created_at)` serves the feed query NFR-4 pins to 50 ms"). Retention and archival. Numbered migration steps, including backfill, ordered so each step leaves the system working.
4. **Sequences.** Re-walk the logical scenarios at message level: which endpoint, query or event, in order, including the failure branch. For externally reachable interfaces, add an abuse branch: what an attacker tries at this hop, tied to the context map's trust boundaries. Every hop names a real artifact from this doc.
5. **State machines** for any entity with a lifecycle: states, legal transitions, triggers, and the transitions that must be illegal. Illegal transitions are where bugs live.
6. **Failure modes.** For each external dependency: behavior on timeout, on retry (say whether the operation is idempotent, and why), on poison input, and when the dependency is fully down. State the fallback even when it is "fail closed with this error"; an unstated fallback is what implementers each invent differently.
7. **Observability.** Named metrics that would show this component misbehaving, the log events that matter (with fields), health checks, and the NFR each one evidences. An NFR with no metric has no evidence.
8. **Security and config.** Authentication and authorization per interface; the secrets it needs and where they live; data classification (PII, sensitive, public); config knobs with defaults and what each one trades off.

## Doc-wide

9. **Budget and capacity closure.** For each numeric NFR, a table allocating the number across walkthrough hops (latency) or sizing components (throughput, storage growth, cost) so the parts sum under the target.
10. **Interface conventions.** Style (REST, RPC, events), versioning, pagination, error model, compatibility rules. Decide once for the whole doc so components do not diverge.
11. **Test strategy.** A table of acceptance criterion (requirement ID) → test → type (unit, contract, integration, e2e, load/soak) → location. Every numeric NFR gets a load or soak test. Qualitative NFRs and shipped Could FRs get a stated check (inspection, audit step, manual check) or an explicit "no test" ruling. Gaps go back to the user.
12. **Rollout.** For changes to live behavior: feature flags, staged rollout, rollback.
13. **Implementation order.** Build slices, thinnest end-to-end slice first: the one that exercises the riskiest contract. Each slice names the requirement IDs it makes testable.
14. **Deferred decisions.** Choices still open, each with its options and what it blocks.
