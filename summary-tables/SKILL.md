---
name: summary-tables
description: Format a status or close-out readout as one compact, evidence-backed Markdown table — work done against a plan, issue or acceptance criteria, review findings and fixes, verification results, PR or issue readiness, or an option comparison. Use when reporting what shipped, what is left, a gap against a plan, or whether criteria are met. Not for a one-fact answer or for ordinary prose questions.
---

# Summary tables

A readout answers one question fast and keeps the evidence attached. Use a table when there are about three or more items with a status. For one or two facts, write a sentence.

## Shape

1. **Bottom line first**, in one sentence. If the user asked yes/no, start with `Yes`, `No` or `Partly`. Include branch, commit or PR state and anything still unverified.
2. **A short label** naming what the table answers: `What changed`, `Still open`, `Verification`.
3. **One table** with 2–4 columns named for this question (see below).
4. **A closing line**: `Verified: …` (what was checked, on which commit) or `Net: …` (what is left and the next step). Add a verdict, `PASS`, `ISSUES` or `BLOCKED`, when the readout reports a run or a review.

```markdown
No — two of three criteria are met; the export criterion is missing.

#123 acceptance criteria

| Criterion | Status |
|---|---|
| User can import a CSV | Complete — `importCsv()` + `import.test.ts` (12 passed) |
| Errors show the failing row | Complete — `ImportErrors.tsx`, checked in browser |
| User can export to CSV | Missing — no export route yet |

Verified: unit tests passed on `a1b2c3d`; e2e not run (no staging access).
```

## Pick columns for the question

| Readout | Columns |
|---|---|
| Review fixes | `#`, `Finding`, `Fix` |
| New review findings | `#`, `File`, `Finding`, `Category` |
| Plan progress or gap | `#`, `Plan item`, `Status` |
| Acceptance criteria | `Criterion`, `Status` |
| Issue status | `Issue`, `Status` |
| Verification | `Check`, `Result`, `Evidence` |
| Comparison | `Option`, `Tradeoff`, `Recommendation` |

## Status words

Use exactly these, as plain text with no emoji, and follow each with evidence:

- `Complete` — done, with evidence.
- `Partial` — some parts landed; name what is missing.
- `Missing` — not started, failed, or contradicted by evidence.
- `Pending` — deferred on purpose, or awaiting a run.
- `Blocked` — an outside dependency is in the way; name it.

A label alone is not a status. Name the file, test, command, commit or UI route that proves it. If verification was not run, say so and why; never imply completion from intent.

## Rules

- **Group by state** when the list is long: Complete, Partial, Missing, Blocked, then bookkeeping (merge, close, deploy). Never bury a `Partial` or `Blocked` row among completed ones.
- **Keep cells on one line.** A pipe or line break inside a cell breaks the table. Put overflow in a short list under the table.
- **Keep the user's numbering**: issue, PR and plan numbers like `#220`.
- **Don't drop detail.** Before finishing, scan the conversation for facts the reader would need: changed files, test counts, skipped checks and why, commit SHA, branch, PR or issue state, findings with severity and location, and anything deliberately left out. Each one goes in a cell or in the list below the table.
- **Past ~10 rows**, split into groups or summarize repeated low-risk rows.
- Use `code` formatting for paths, commands, branches and identifiers.
