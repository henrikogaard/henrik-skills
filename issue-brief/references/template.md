# Issue brief templates

Pick the size by the work, not by habit. Leave out any section that would only say "none".

## Small fix

```markdown
## Outcome
One or two sentences a person would notice.

## Status — YYYY-MM-DD
**Delivery:** ready to implement. **Evidence:** read at `<commit>`. **Remaining:** <what is left, who owns it>.

## What exists today (verified at `<commit>`)
1. `<path>`: `<symbol>` does <current behaviour>.

## Steps
1. <exact change, file and symbol>

## Acceptance criteria
| # | Criterion | How it is verified |
|---|---|---|
| 1 | <observable result> | `<test name>` / `<command>` |

## Do not
- <scope trap>
```

## Feature or multi-slice

```markdown
## Outcome
What a person notices. One line on what this issue does not cover, and which issue does.

## Status — YYYY-MM-DD
**Delivery:** … **Evidence:** read at `<commit>`. **Remaining:** …
(One block. Replace it in place on every update.)

## Sequence
Order across issues and slices; what may run in parallel.

## Decisions (owner, YYYY-MM-DD)
1. **<decision>.** <reason or condition>
"No decision is open" when true.

## What exists today (verified at `<commit>`)
1. `<path>`: `<symbol>` — <current behaviour>. (verified / reported)

## Rules every slice keeps
- <boundary that holds throughout: authority, privacy, limits, data replay, approvals>

## Before you start
1. Read <project rules file>, <owning specs>, <named files>.
2. Branch from the current default branch and record the commit.
3. Recheck each fact above; if one no longer holds, say so and adapt.

## Stop and ask the owner when
- <one line per boundary>
Do not stop for: moved line numbers, a symbol you can find by search, pending owner-only checks.

## Slice 1. <title>
### What exists today
### Steps
### Tests (write first)
- <behaviour sentence> → criterion <n>
### Done when
- <checkable statement>

## Slice 2. <title> — proposal first
Post a proposal as a comment and wait for approval. It answers:
1. <question>

## Checks for every pull request
The project's own commands; report any check not run, with the reason.

## Owner-only check (not yours to run)
What it is, who runs it, where it is recorded.

## Acceptance criteria
| # | Criterion | How it is verified |
|---|---|---|

## Deliver
Pull request shape, how to update the status block, "do not merge".

## Do not
- <scope trap>

## Related
<issue> — how it relates.
```

## A filled acceptance table

| # | Criterion | How it is verified |
|---|---|---|
| 1 | The CSV export includes each note's tags. | `test_export_includes_tags` |
| 2 | Notes without tags export an empty tags column, not an error. | `test_export_untagged_note` |
| 3 | Existing exports still open in a spreadsheet. | Owner check: open one export in a spreadsheet app, recorded on the checklist issue |
