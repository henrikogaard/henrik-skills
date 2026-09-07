---
name: detailed-design
description: Turn a logical design into implementation-ready documentation — interface specs, physical data models, message-level sequence walkthroughs, failure modes, observability, security detail, and a test strategy mapped to acceptance criteria — so an implementer can build it without asking a question the doc should have answered. Use when the user says "detailed design", "tech spec from the design", "spec the API", "design the schema", "implementation-ready design", or when handing a finished design to implementers.
---

The bar for this skill: **an engineer (or agent) who has never spoken to you can implement the system without asking a question this document should have answered.** Every question you can predict, answer in the doc; every question you can't, put in `Open questions` — an honest gap beats a silent guess.

Inputs, in order of authority: the logical design from `/conceptual-logical-design` (structure and contracts come from there — this skill deepens, it doesn't re-architect), the requirements map (acceptance criteria, priorities, dependencies), and — if code exists — the codebase's actual conventions. If the logical design doesn't exist, say so and either run `/conceptual-logical-design` first or derive a minimal logical layer inline, flagged as such — don't silently re-architect under a detailed-design title. If the requirements map is missing, reconstruct a minimal one inline from the logical design's coverage table — flagged as such — or run `/requirement-mapping` first; never invent acceptance criteria silently.

Read the repo before specifying anything: a detailed design that fights the codebase it lands in is a rewrite proposal in disguise. Where the code contradicts the design, don't absorb it silently — record each conflict in a **Codebase deltas** section with a ruling (the design yields, the code migrates, or it escalates as a Q), and surface the list to the user.

This is where technology gets pinned. Products, versions, schemas, endpoints — the choices `/conceptual-logical-design` deliberately deferred land here, each pivotal one (by that skill's definition: reversing it touches more than one component's contract or forces a data migration) recorded with its alternatives.

## Depth per component

Not every component deserves the same depth. Spend it where the risk is: the components named in the risk register, the ones owning data, the ones behind the hardest NFRs. If NFRs are unknown (no map), depth defaults to data owners plus the risk register — and say so. For a simple CRUD-ish component, a short subsection is honest; padding it to match the others is ceremony. Say which components got the shallow treatment and why. If the whole system is small — a handful of components, no numeric NFRs — collapse the per-component headings into one section rather than padding each to the template, and say so up front.

## Per-component spec

For each component from the logical design:

1. **Module structure.** Package/folder layout with one line per module's job. Implementation detail, yes — but the kind implementers otherwise each invent differently.
2. **Interfaces, fully specified.** Every operation from the logical contract, now concrete: API endpoints (method, path, auth) or function signatures; request/response schemas with field names, types, required/optional, and **a literal request/response (or call/return) example** — one example catches more ambiguity than a page of prose; error responses enumerated by case; idempotency and rate semantics where they matter. Consumers implement against this section; it must be possible to mock from it alone.
3. **Data model, physical.** Tables/collections/indexes with fields, types, constraints, and defaults; indexes justified by a query ("`(user_id, created_at)` — the feed query NFR-4 pins to 50 ms"), not sprinkled; retention and archival; **migration steps** numbered, including backfill, ordered so each step leaves the system working.
4. **Sequence walkthroughs.** The logical design's scenarios, re-walked at message level — if the logical pass was compressed upstream, walk the conceptual pass's capabilities instead and say which source you used: which endpoint, which query, which event, in order, including the failure branch — and, for externally reachable interfaces, an abuse-case branch (what an attacker attempts here, pairing with the context map's trust boundaries). Mermaid `sequenceDiagram` or a numbered list — either, as long as every hop names a real artifact from this doc.
5. **State machines** for any entity with a lifecycle: states, legal transitions, and what triggers each — including the transitions that must be *illegal* (the invariant guards), since illegal transitions are where the bugs live.
6. **Failure modes.** Per external dependency: what happens on timeout, on retry (is the operation idempotent — say which and why), on poison input, on the dependency being down entirely. Fallback behavior stated, even when the fallback is "fail closed with this error" — *unstated* fallback is what implementers invent differently.
7. **Observability.** The metrics that would show this component misbehaving (named), the log events that matter (with fields), health checks, and where each maps to an NFR. If an NFR has no metric, it will have no evidence.
8. **Security & config.** Authn/authz per interface, secrets the component needs and where they live, data classification (what's PII, what's sensitive-but-not-PII), and configuration knobs with defaults and what each knob trades off.

Then, doc-wide:

9. **Budget & capacity closure.** For each numeric NFR, a budget table allocating the number across the walkthrough hops (latency) or sizing the components (throughput, storage growth, cost envelope), so the per-hop budgets sum under the NFR. This is where `/conceptual-logical-design`'s sufficiency arguments get closed with numbers — or exposed as hopes.
10. **Interface conventions.** Style (REST/RPC/events), versioning, pagination, error model, compatibility rules — decided once, doc-wide, so per-component specs don't diverge in ways consumers feel.
11. **Test strategy.** The traceability chain closes here: every acceptance criterion from the requirements map → at least one test, named with its type (unit / contract / integration / e2e / load-soak) and where it lives — and every numeric NFR gets at least one load or soak test. Qualitative NFRs and shipped Could FRs get a stated check — inspection, an audit step, manual verification — or an explicit no-test ruling in the table. A requirement with no test was never really a requirement; this table is where that gets caught, and gaps go back to the user rather than being hidden.
12. **Rollout.** For any system modifying live behavior, the cutover plan — feature flags, staged rollout, rollback. Schema migrations cover the data; this covers the behavior.
13. **Implementation order.** Build slices, tracer-bullet first: the thinnest end-to-end cut that exercises the riskiest contract, then outward. Each slice names the requirements it makes testable — the same IDs, so the map, the designs, and the build plan stay one chain.
14. **Deferred decisions.** Any choice still open after this doc, each with its options and what it blocks. Better one visible open decision than three implied ones.

## Artifact

Same convention as the upstream docs — default `docs/design/detailed-design.md`. Depth sets length: a shallow component is one paragraph, a deep one runs ~80–120 lines, and the doc grows with component count and risk, not with prose. If a section explains more than it specifies, cut it back to the spec:

```markdown
# <System> — detailed design
## Inputs   <!-- links: logical design, requirements map; Q-n resolved by this doc; flags if either was reconstructed inline -->
## Decisions made here   <!-- the products/versions pinned, each with alternatives and reason; ADRs where the repo has a convention -->
## Codebase deltas   <!-- table: conflict | ruling (design yields / code migrates / Q-n) -->
## <Component A>
### Modules / Interfaces / Data model / Sequences / States / Failure modes / Observability / Security & config
<!-- shallow components may collapse these headings into one paragraph; the depth section above says when that's honest -->
## <Component B> …
## Budget & capacity closure   <!-- per numeric NFR -->
## Interface conventions
## Test strategy   <!-- table: acceptance criterion (req ID) | test | type | location -->
## Rollout
## Implementation order   <!-- slices, each naming the req IDs it makes testable -->
## Open questions   <!-- continue Q numbering from the upstream docs -->
```

Present it leading with the decisions this doc pinned (they're the newest and least reviewed) and the implementation order. From here the work hands off to implementers — `/implement-spec`, `/to-tickets`, or a delegation fan-out via `/delegate-subagents`.
