# Handoff plans

Read this before handing slices to another agent: a cheaper model, an agent CLI, a fresh session or a person who was not in this conversation. A handoff plan turns one slice's detailed design into a file that agent can follow alone.

Write it for the weakest agent that might run it. Assume it follows explicit steps well, fills gaps badly, and does not know when to stop. Three things make a plan safe to hand over:

1. **Everything is in the file.** Paths, code excerpts, conventions, commands. Never "see above" or "as discussed".
2. **Every step proves itself.** Each step ends with a command and the output that means success. The executor never judges "looks fine".
3. **Hard edges.** A list of files it may touch, a list it must not, and STOP conditions that say "stop and report" instead of letting it improvise.

## Where it goes

One file per slice, next to the design doc: `docs/design/<slug>/slice-<n>.md`. The design doc stays the index: its build plan row for the slice gets status `Handed off` and a link to the plan file.

## Before writing

- Note the current commit: `git rev-parse --short HEAD`. If the repo is not a git repo, say so in the plan and skip the drift check.
- **Run every command you put in the plan** (install, test, lint, typecheck) and record what success looks like. Never guess a command.
- Find one existing file that shows the convention the executor must copy (error handling, test layout, naming).

## Template

```markdown
# Slice <n>: <what will be true when this is done>

Design doc: docs/design/<slug>.md · Requirements: FR-1, NFR-3
Planned at: commit <short SHA>, <date> · Depends on: slice <m> (or "none")

> **Executor:** follow the steps in order. Run each Verify command and check
> its result before the next step. Touch only the files under "In scope". If a
> STOP condition happens, stop and report; do not work around it. Do not edit
> the design doc; your reviewer updates it. End with the report at the bottom.
>
> **Drift check, run first:** `git diff --stat <SHA>..HEAD -- <in-scope paths>`
> If it lists a file, compare "Current state" with the live code. Any mismatch
> is a STOP condition.

## Why
<2–4 sentences: the problem, what it costs today, what changes when this lands.
Intent is what lets the executor make a sound call when a detail is off.>

## Current state
- `<path>`: <its role>; the part to change is lines <a–b>:
  <short excerpt with file:line, enough to confirm it is the right place>
- Convention to copy: <pattern>, as in `<exemplar file:lines>`.
- Decision to honor: <quote the D-n choice and consequence lines in full>.

## Commands
| Purpose | Command | Success looks like |
|---|---|---|
| Tests | `<exact command>` | exit 0, <n> tests pass |

## Scope
In scope (the only files you may change or create):
- `<path>`
Out of scope (do not touch, even if it looks related):
- `<path or change>`: <why>

## Git
Work on the branch you are given. Commit after each step; message style like `<an example from git log>`. Do not push, merge or open a PR.

## Steps
### Step 1: <imperative title>
<exact files and symbols; the target shape of the code when it matters>
Verify: `<command>` → <expected output>

## Tests
| Acceptance criterion | Test name | File | What it asserts |
|---|---|---|---|

## Done when
All must hold, each checkable by a command:
- [ ] `<test command>` exits 0, including the new tests above
- [ ] `<check that proves the behavior, e.g. a one-line script or grep>` → <expected>
- [ ] `git diff --stat <base branch>...HEAD` lists only in-scope files (write the real base branch, e.g. `main`)

## STOP conditions
Stop and report if:
- The code under "Current state" does not match the live code.
- A Verify command still fails after two honest fix attempts.
- The change seems to need an out-of-scope file.
- <a risk specific to this slice, e.g. "the conditional update cannot be expressed in SQLite">

## Report
Reply with exactly:
VERDICT: PASS (all steps done and verified) | ISSUES (done, some Verify failed) | BLOCKED (a STOP condition)
STEPS: per step, done or skipped, and the Verify command's actual result
STOPPED BECAUSE: only if BLOCKED: which condition, what you saw
FILES CHANGED: every file, from `git diff --stat`
NOTES: deviations from the plan and why, surprises, judgment calls
Report only what a command in this session showed you.
```

## Quality check before handing over

- Could an agent that never saw this repo or conversation run it with only this file and the repo? Inline whatever it would have to ask.
- Is every Verify and every Done line a command with an expected result, not a judgment?
- Does every step name exact files and symbols?
- Are the STOP conditions about this slice's real risks, not boilerplate?
- Do the drift-check paths match the In scope list?
- No secret values anywhere: name the secret's location, never its value.

## Refresh plans on resume

When you resume a doc that has handoff plans, check each one by its build-plan status before anything else:

- **Handed off, not yet run:** run its drift check. If in-scope files changed, re-read the code. Gone (fixed some other way): mark the slice `Done` with that evidence, or drop it with a change-log line. Still needed: refresh "Current state" and the `Planned at` SHA.
- **Blocked:** read the reason, look at the obstacle in the code, then rewrite the plan around it, or change the design (a new `D-n`) and ask the user.
- **Done:** run its cheapest Done line on the current code to confirm it still holds.

Report what is confirmed, refreshed, blocked and ready to run.
