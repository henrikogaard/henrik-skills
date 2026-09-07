# henrik-skills

Architecture, planning, and orchestration skills for agent harnesses that
support the open Agent Skills layout (`SKILL.md` + frontmatter). Six skills:
a three-stage design pipeline, a two-skill orchestration pair, and one
standalone output-format skill.

## The design pipeline

A chain where each artifact feeds the next, and traceability runs end to end —
every requirement keeps an ID from first mention through design to
verification:

```
/requirement-mapping          → docs/requirements-map.md               (default)
        ↓
/conceptual-logical-design    → docs/design/conceptual-logical-design.md (default)
        ↓
/detailed-design              → docs/design/detailed-design.md         (default)
        ↓
implementers (/implement-spec, /to-tickets, a /delegate-subagents fan-out, …)
```

Paths are defaults — each skill follows the repo's own docs convention first.
Each stage is opt-in: the skills right-size themselves and will say when an ask
is too small for the ceremony.

### requirement-mapping

Turns a fuzzy ask — a conversation, an issue, an RFC, a rant — into a
**requirements map**: every requirement traced to its source, and every source
statement accounted for by a requirement, an open question, or an explicit
out-of-scope ruling. The bidirectional accounting is the point: a list that
fails it silently invents scope or drops stakeholder intent.

- Triggers: "requirements", "PRD", "acceptance criteria", "traceability",
  "what are we actually building".
- ID scheme: `FR-n`, `NFR-n`, `CON-n`, `ASM-n`, `Q-n`, with MoSCoW priorities
  and acceptance criteria on every Must/Should FR.
- Two sweeps guarantee completeness: **forward** (every extracted statement
  gets a disposition — nothing stays unmapped) and **backward** (every
  requirement cites a source quote — nothing is invented).
- Output: `docs/requirements-map.md` — requirements, traceability,
  dependencies, conflicts, open questions, out-of-scope rulings.
- Sizes the ask first: a small ask gets a one-page map, or the requirements
  are carried inline to whatever comes next.

### conceptual-logical-design

Designs the system at two levels, with every element tied back to a
requirement ID:

- **Conceptual** — what the system is and does, explainable to a
  non-engineer: purpose, context map with trust boundaries and top threats,
  capabilities (every FR lands in exactly one), 3–7 black-box components
  named for the domain, and the domain concepts.
- **Logical** — how the system is shaped: component contracts (promises and
  guarantees, not signatures), domain model, the one-owner-per-datum rule,
  integration semantics, scenario walkthroughs covering every Must FR and NFR
  mechanism, NFR sufficiency arguments in one line of arithmetic, pivotal
  decisions ADR-style, and a risk register.
- Technology **families** are allowed ("relational store"); products are
  banned unless a `CON-n` forces one — pinning early locks in tradeoffs
  nobody examined.
- The bidirectional coverage table is the acceptance test for the design and
  the input `/detailed-design` consumes.
- Boundary: module-level design inside an existing codebase is
  `codebase-design` territory, not this skill's.

### detailed-design

Deepens the logical design into an implementation-ready spec — the bar is
that an engineer (or agent) who has never spoken to you can build it without
asking a question the doc should have answered.

- Reads the codebase first; where code contradicts the design, conflicts are
  recorded in a **Codebase deltas** table with a ruling (design yields / code
  migrates / escalates as a `Q-n`), not silently absorbed.
- This is where technology gets pinned: products, versions, endpoints, schemas.
- Per component, sized by risk: module structure, fully specified interfaces
  with literal request/response examples, physical data model with justified
  indexes and numbered migration steps, message-level sequence walkthroughs
  including failure and abuse branches, state machines including *illegal*
  transitions, failure modes per dependency, observability mapped to NFRs,
  and security/config.
- Doc-wide: budget & capacity closure for every numeric NFR, interface
  conventions, a test strategy mapping every acceptance criterion to a named
  test, rollout, tracer-bullet implementation order, and deferred decisions.
- Hands off to implementers — or to a delegation fan-out via
  `/delegate-subagents`.

## The orchestration pair

### delegate-subagents

Runs external coding-agent CLIs — `codex`, `claude`, `grok`, `cursor agent`,
`omp`, `pi`, `devin` — headlessly in parallel under you as orchestrator. You
hold the context, write self-contained briefs, and adjudicate the results;
the delegates see nothing of the conversation.

- Always asks first: which agents (probes what's installed), which model and
  effort per agent, mode, task scope, permissions (analysis-only by default;
  edits-allowed puts each delegate on its own branch), and a cost ceiling.
- Three modes:
  - **counsel** — N agents answer the same brief; opinions are adjudicated,
    never averaged. Agreement across model families is the strongest signal;
    lone findings are where the run earns its cost.
  - **division** — different briefs, each agent owns a slice; artifacts are
    verified and diffs reviewed before anything merges.
  - **arena** — N competing artifacts off one brief; pick a base on
    extendability, graft the losers' best ideas, re-verify the synthesis.
- Registry of per-CLI invocation flags with per-machine `Verified` dates —
  probe `--help` before firing; the probe wins over the table.
- Run directory `.scratch/delegates/<date>-<slug>/` holds the briefs,
  captured `out-`/`err-` files, and an append-only manifest.
- Failure playbook covers dropouts, timeouts, off-brief output, and
  correlated failure — a delegate's failed work is never quietly absorbed.

### graph-orchestration

A role-based agent graph for fan-out-and-synthesize work: researchers
partition the question in parallel, a writer drafts against their findings, a
reviewer critiques against a rubric, and revision rounds run until a quality
bar or budget is met — then you synthesize.

- Triggers: "research graph", "multi-agent research", "writer and reviewer
  loop", "orchestrate agents for this report/review/investigation".
- Asks up front: roles and counts, depth (quick / standard / deep — the dial
  that sets fan-out, revision rounds, and rubric severity together),
  executor, and deliverable location.
- Executors are per-node: native subagents, external CLIs via the
  `/delegate-subagents` registry, or a mix — cheap parallel research on one
  provider, drafting on the strongest model, review on a different family so
  the reviewer doesn't share the writer's blind spots.
- Optional deep-run roles: synthesist (merges multiple writers), adversary
  (attacks the weakest claims), fact-checker (re-verifies citations).
- Two gates between research and writing: merge the findings with
  independent-vs-shared-source marking (parallel research manufactures false
  corroboration without it), and sweep coverage against the ask while a hole
  is still cheap to fill.
- Run directory `.scratch/graph/<date>-<slug>/` holds `plan.md`, per-node
  briefs and outputs, timestamped draft rounds, and a graph report recording
  what actually ran.

The two compose: a graph's nodes can execute on external CLIs via the
delegate registry — delegate owns the node mechanics, the graph owns the
plan, dependencies, and report. For flat fan-out without roles or rounds, use
`delegate-subagents` directly.

## Standalone

### summary-tables

A personal output contract for decision-ready readouts: compact,
evidence-backed Markdown tables for status, comparison, acceptance-criteria
checks, gap analysis, verification, and close-out summaries.

- Leads with the bottom line, then a table whose columns fit the question —
  not a one-size-fits-all shape.
- Groups rows by real state (done / partial / open / blocked / bookkeeping);
  every status cell carries evidence, not just a label.
- Preserves decision-relevant detail below the table instead of compressing
  it away; ends with a `Net:` or `Verified:` line.
- Defers to a more specialized skill when one clearly fits better.

## Install

Skills are discovered from `~/.agents/skills/` (or a project's
`.agents/skills/`). Symlink keeps this repo the source of truth:

```sh
for skill in requirement-mapping conceptual-logical-design detailed-design \
             delegate-subagents graph-orchestration summary-tables; do
  ln -sfn "$(pwd)/$skill" ~/.agents/skills/$skill
done
```

## Repo contract

```text
skill-name/
  SKILL.md          # frontmatter: name, description
  agents/           # optional tool metadata (e.g. openai.yaml)
```

`.scratch/` holds delegate and graph run artifacts and is not part of the
published skill set.
