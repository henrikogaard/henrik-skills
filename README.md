# henrik-skills

Architecture, planning, orchestration, and delivery skills for agent
harnesses that support the open Agent Skills layout (`SKILL.md` +
frontmatter). Seven skills organized into three layers: a design pipeline,
an orchestration pair, a delivery pipeline that composes them, and one
standalone output-format skill.

---

## Quick reference

| Skill | What it does | When to reach for it |
|---|---|---|
| `/requirement-mapping` | Fuzzy ask → testable, traced requirements map | "What are we actually building?" |
| `/conceptual-logical-design` | Requirements → architecture (conceptual + logical) | "Design the system" |
| `/detailed-design` | Logical design → implementation-ready spec | "Spec the API / schema / contracts" |
| `/delegate-subagents` | Fan out work to external agent CLIs in parallel | "Get codex and claude to review this" |
| `/graph-orchestration` | Role-based research → draft → review loop | "Research this topic with multiple agents" |
| `/pipeline-orchestration` | Source → Research → Clarify → Plan → Approve → Execute → Verify → Review → Deliver | "Take this issue through to done" |
| `/summary-tables` | Compact, evidence-backed status readouts | "Summary", "status", "gap vs plan" |

---

## How the skills compose

The skills form three layers. Lower layers are self-contained; higher layers
call lower ones. You can enter at any layer depending on how much structure
the task needs.

```
Layer 3 — Delivery pipeline
┌─────────────────────────────────────────────────────────────────────┐
│  /pipeline-orchestration                                            │
│  Source → Research → Clarify → Plan → Approve → Execute → Verify   │
│  → Independent Review → Deliver                                     │
│                                                                     │
│  Composes everything below into an 8-stage gated pipeline           │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │                              │
Layer 2 — Orchestration                       │
┌──────────────┴──────────────┐  ┌────────────┴──────────────────────┐
│  /graph-orchestration        │  │  /delegate-subagents              │
│  Fan-out researchers,        │  │  External agent CLIs in parallel: │
│  writer-reviewer loops,      │  │  counsel, division, arena modes   │
│  convergence rounds          │  │                                   │
└──────────────┬──────────────┘  └────────────┬──────────────────────┘
               │                              │
Layer 1 — Design pipeline                     │
┌──────────────┴──────────────────────────────┴──────────────────────┐
│  /requirement-mapping                                              │
│        ↓                                                           │
│  /conceptual-logical-design                                        │
│        ↓                                                           │
│  /detailed-design                                                  │
│        ↓                                                           │
│  implementers (/implement-spec, /to-tickets, fan-out, …)           │
└────────────────────────────────────────────────────────────────────┘

Always loaded:
  /summary-tables — output format for any status, comparison, or readout
```

---

## When to use which skill

### Start here: what kind of work is it?

**"I have a Linear issue / RFC / plan and I want it done properly."**
Use `/pipeline-orchestration`. It drives the full lifecycle — research,
clarification, planning, approval, execution, verification, independent
review, delivery — with configurable gates so you control how much autonomy
the pipeline gets. This is the top-level entry point for structured delivery.

**"I need to understand what we're building before any code."**
Start with `/requirement-mapping`. It turns vague asks into numbered, testable
requirements with bidirectional traceability. If the system needs architecture
next, hand the map to `/conceptual-logical-design`, then `/detailed-design`.

**"I need a research report, not code."**
Use `/graph-orchestration` directly. It fans out researchers on partitioned
sub-questions, runs a writer-reviewer loop with convergence rounds, and
synthesizes the findings.

**"I want multiple agents to review / compete on this."**
Use `/delegate-subagents`. Counsel mode gets N agents' independent opinions
and adjudicates them. Arena mode produces competing artifacts and picks the
best base. Division mode splits work across agents.

**"Give me a status update / comparison / gap analysis."**
Use `/summary-tables`. It formats any readout as a compact, evidence-backed
table with a bottom line and a verdict.

### Decision tree

```
Is it a full feature / issue to deliver end-to-end?
├── Yes → /pipeline-orchestration
│         (it will call the other skills internally)
└── No
    ├── Do I need requirements / acceptance criteria?
    │   └── Yes → /requirement-mapping
    │             └── Need architecture? → /conceptual-logical-design
    │                 └── Need implementation spec? → /detailed-design
    ├── Do I need research / analysis / a report?
    │   └── Yes → /graph-orchestration
    ├── Do I want multiple external agents on this?
    │   └── Yes → /delegate-subagents
    └── Do I need a status readout?
        └── Yes → /summary-tables
```

---

## Skill details

### The design pipeline

A chain where each artifact feeds the next. Traceability runs end to end —
every requirement keeps an ID from first mention through design to
verification. Paths are defaults; each skill follows the repo's own docs
convention first. Each stage is opt-in: the skills right-size themselves and
say when an ask is too small for the ceremony.

```
/requirement-mapping          → docs/requirements-map.md
        ↓
/conceptual-logical-design    → docs/design/conceptual-logical-design.md
        ↓
/detailed-design              → docs/design/detailed-design.md
        ↓
implementers (/implement-spec, /to-tickets, /delegate-subagents fan-out, …)
```

#### requirement-mapping

Turns a fuzzy ask — a conversation, an issue, an RFC — into a **requirements
map**: every requirement traced to its source, and every source statement
accounted for by a requirement, an open question, or an explicit out-of-scope
ruling.

- **Triggers**: "requirements", "PRD", "acceptance criteria", "traceability",
  "what are we actually building".
- **ID scheme**: `FR-n`, `NFR-n`, `CON-n`, `ASM-n`, `Q-n`, with MoSCoW
  priorities and acceptance criteria on every Must/Should FR.
- **Two sweeps guarantee completeness**: forward (every extracted statement
  gets a disposition) and backward (every requirement cites a source quote).
- **Output**: `docs/requirements-map.md`.
- Sizes the ask first: a small ask gets a one-page map, or the requirements
  are carried inline.

#### conceptual-logical-design

Designs the system at two levels, with every element tied back to a
requirement ID:

- **Conceptual** — what the system is, explainable to a non-engineer:
  purpose, context map with trust boundaries and top threats, capabilities
  mapped to FRs, 3-7 domain-named components, domain concepts.
- **Logical** — how the system is shaped: component contracts (promises, not
  signatures), domain model, one-owner-per-datum rule, integration semantics,
  scenario walkthroughs covering every Must FR and NFR mechanism, NFR
  sufficiency arguments, pivotal decisions ADR-style, risk register.
- Technology families allowed; products banned unless a `CON-n` forces one.
- The bidirectional coverage table is the acceptance test for the design.
- **Boundary**: module-level design inside an existing codebase is
  `codebase-design` territory.

#### detailed-design

Deepens the logical design into an implementation-ready spec — the bar is
that an engineer (or agent) who has never spoken to you can build it without
asking a question the doc should have answered.

- Reads the codebase first; code-vs-design conflicts go into a **Codebase
  deltas** table with rulings.
- This is where technology gets pinned: products, versions, endpoints,
  schemas.
- Per component (sized by risk): module structure, fully specified interfaces
  with examples, physical data model with justified indexes and migration
  steps, message-level sequence walkthroughs, state machines, failure modes,
  observability, security/config.
- Doc-wide: budget & capacity closure for numeric NFRs, interface conventions,
  test strategy, rollout, tracer-bullet implementation order, deferred
  decisions.

### The orchestration pair

#### delegate-subagents

Runs external coding-agent CLIs — `codex`, `claude`, `grok`, `cursor agent`,
`omp`, `pi`, `devin` — headlessly in parallel under you as orchestrator.

- Always asks first: which agents (probes installed CLIs), model per agent,
  mode, scope, permissions (analysis-only by default), cost ceiling.
- **Three modes**:
  - **counsel** — N agents answer the same brief; adjudicated, never averaged.
    Agreement across model families is the strongest signal.
  - **division** — different briefs, each agent owns a slice; verified and
    diff-reviewed before merging.
  - **arena** — N competing artifacts; pick a base on extendability, graft the
    best ideas from the losers.
- Registry of per-CLI flags with `Verified` dates — probes `--help` before
  every run.
- Run directory: `.scratch/delegates/<date>-<slug>/`.
- Failure playbook: dropouts, timeouts, off-brief output, correlated failure.

#### graph-orchestration

A role-based agent graph: researchers partition the question in parallel, a
writer drafts against their findings, a reviewer critiques against a rubric,
revision rounds converge, then you synthesize.

- **Triggers**: "research graph", "multi-agent research", "writer and
  reviewer loop".
- Asks up front: roles/counts, depth (quick / standard / deep), executor,
  deliverable location.
- **Depth dial** sets fan-out, revision rounds, and rubric severity together.
- Executors are per-node: native subagents, external CLIs via
  `/delegate-subagents`, or a mix.
- Deep-run roles: synthesist, adversary, fact-checker.
- Two gates between research and writing: merge findings (independent vs.
  shared-source marking), sweep coverage.
- Run directory: `.scratch/graph/<date>-<slug>/`.

The two compose: graph nodes can execute on external CLIs via the delegate
registry. For flat fan-out without roles, use `/delegate-subagents` directly.

### The delivery pipeline

#### pipeline-orchestration

Drives a source (Linear issue, plan file, conversation, RFC) through an
8-stage delivery pipeline with configurable human gates, artifact hand-offs,
and optional cross-model review.

```
Source → 1. Research → 2. Clarify → 3. Plan → 4. Approve
  → 5. Execute → 6. Verify → 7. Independent Review → 8. Deliver
```

- **Triggers**: "pipeline", "end-to-end delivery", "take this issue through
  to done", "build this properly", "full workflow on this".
- **Source auto-detection**: Linear issues via MCP, file paths, conversation
  context.
- **Configurable gates**: minimal (plan only), standard (plan + review),
  strict (every stage), custom. The Plan gate is always mandatory.
- **Configurable review independence**: cross-model (mandatory different model
  family via `/delegate-subagents`), prefer-cross (different when available),
  same-model.
- **Depth**: light (inline, fast), standard (full design pipeline), thorough
  (deep research + adversarial review + fact-checking).

Stage-to-skill mapping:

| Stage | Skill used | Hand-off artifact |
|---|---|---|
| 1. Research | `/graph-orchestration` or inline | `findings.md` |
| 2. Clarify | Conductor + user Q&A | `clarifications.md` |
| 3. Plan | `/requirement-mapping` → design skills → `/to-tickets` | `plan.md` + design artifacts |
| 4. Approve | Human gate (always) | `decision.md` |
| 5. Execute | `/implement-spec`, `/graph-orchestration`, or finalize | Deliverable + `execution-log.md` |
| 6. Verify | Build/test/lint or coverage checks | `verification.md` |
| 7. Review | `/delegate-subagents` cross-model or subagent | `review.md` with verdict |
| 8. Deliver | PR, Linear comment, repo publish | Shipped deliverable + `manifest.md` |

- Run directory: `.scratch/pipeline/<date>-<slug>/`.
- Resumable: the manifest is the checkpoint; a new session picks up from the
  last completed stage.
- Revision loop: max 2 rounds between Execute and Review, then ship with open
  defect list or abort.

### Standalone

#### summary-tables

Output contract for decision-ready readouts: compact, evidence-backed
Markdown tables.

- **Triggers**: "summary", "status", "gap vs plan", "acceptance criteria",
  "verification", "comparison", "readout".
- Leads with the bottom line, then a table whose columns fit the question.
- Groups rows by real state (done / partial / open / blocked).
- Every status cell carries evidence, not just a label.
- Ends with `Net:` / `Verified:` / verdict (`PASS` / `ISSUES` / `BLOCKED`).
- Defers to a more specialized skill when one fits better.

---

## Usage patterns

### Pattern 1: Full delivery from a Linear issue

```
User: "Take ENG-456 through to done"
→ /pipeline-orchestration fires
→ Fetches the issue, researches the codebase, clarifies ambiguities,
  produces a plan (requirements + tickets), presents for approval,
  implements via parallel subagents, verifies, sends to cross-model
  review, delivers PR + Linear comment
```

### Pattern 2: Architecture-first for a new system

```
User: "What are we building?" → /requirement-mapping
User: "Design it" → /conceptual-logical-design (consumes the map)
User: "Spec the API" → /detailed-design (consumes the logical design)
User: "Build it" → /implement-spec or /to-tickets (consumes the spec)
```

Each skill hands off a traced artifact. You can enter and exit at any stage.

### Pattern 3: Research report with quality bar

```
User: "Research graph on X" → /graph-orchestration
→ 3 researchers partition the question, writer drafts, reviewer
  critiques against rubric, 2 revision rounds, synthesized report
```

### Pattern 4: Multi-agent review of existing work

```
User: "Get codex and claude to review this branch"
→ /delegate-subagents in counsel mode
→ Both agents review independently, findings adjudicated, lone
  findings surfaced, dismissed items shown with reasons
```

### Pattern 5: Quick status check

```
User: "Gap vs the plan?"
→ /summary-tables
→ Bottom line, table with evidence per row, Net: line
```

---

## Depth controls

Several skills share a depth dial. Depth sets research breadth, planning
detail, review rigor, and output length as a package:

| Depth | Research | Planning | Review | Output budget |
|---|---|---|---|---|
| light / quick | 1 researcher or inline | Inline notes | 1 round | ~800 words |
| standard | 2-3 researchers | Full `/requirement-mapping` | 2 rounds + rubric | ~1500 words |
| thorough / deep | Wide fan-out + adversarial | Full design pipeline | 3 rounds + fact-check | ~2500 words |

Choose depth by risk: a well-understood bug fix is light; a new system with
unclear requirements is thorough.

---

## Run directories

Every orchestration skill writes to `.scratch/` with a timestamped run
directory:

```
.scratch/
  pipeline/<YYYYMMDD-HHMM>-<slug>/    # /pipeline-orchestration
  graph/<YYYYMMDD-HHMM>-<slug>/        # /graph-orchestration
  delegates/<YYYYMMDD-HHMM>-<slug>/    # /delegate-subagents
```

Each contains an append-only manifest, per-node/stage briefs and outputs,
error logs, and timestamped draft rounds. The manifest is the audit trail —
it records what ran, what failed, and what the gates decided.

---

## Install

Skills are discovered from `~/.agents/skills/` (or a project's
`.agents/skills/`). Symlink keeps this repo the source of truth:

```sh
for skill in requirement-mapping conceptual-logical-design detailed-design \
             delegate-subagents graph-orchestration pipeline-orchestration \
             summary-tables; do
  ln -sfn "$(pwd)/$skill" ~/.agents/skills/$skill
done
```

## Repo layout

```text
skill-name/
  SKILL.md          # frontmatter: name, description
  agents/           # optional tool metadata (e.g. openai.yaml)
```

`.scratch/` holds delegate, graph, and pipeline run artifacts and is not part
of the published skill set.
