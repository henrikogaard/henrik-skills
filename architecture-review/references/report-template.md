# Report template

Keep it scannable: tables and short lines. Leave out a section that would be empty.

```markdown
# Architecture review — <repo or area>

Date: <date> · Scope: <what was reviewed, and why: named by the user, or top hot spots>
Facts: <commits analysed and period, files, source and test lines, from repo_facts.py>

## Top three
1. <candidate title> — <one-line payoff> (Strong, effort S)
2. …
3. …

## Hot spots
| File | Commits | Lines | Note |
|---|---|---|---|

## Candidates
### C1: <short title naming the change, e.g. "Split orders.py by reason to change">
Strength: Strong · Effort: M · Risk: <what could break>
Evidence: <file:line ranges, counts, co-change pairs, deletion-test result>
Problem: <one sentence: what it costs today>
Change: <one or two sentences: what moves, merges or goes away, in incremental steps>
Payoff: <fewer files per change, a testable seam, fewer and stronger tests>
Tests affected: <kept, merged, deleted, added>

### C2: …

## Test suite
| Test or group | Smell | Verdict | Covered after by |
|---|---|---|---|
| tests/test_orders.py::test_total_1..4 | Duplicate | Merge into one parametrized test | the merged test |

Missing tests:
- <behavior> — <why it matters>

Summary: <tests now> → <tests proposed>, <what stays covered>

## Conflicts with recorded decisions
<only if a candidate contradicts a D-n in a design doc: which, and why the friction justifies reopening it>

## Open questions
- Q-1: <question> — <what it blocks>
```
