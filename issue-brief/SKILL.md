---
name: issue-brief
description: Write or rewrite a tracker issue (Linear, GitHub, Jira) as a self-contained brief another agent can implement cold. Verifies every fact in the code at a named commit, settles open decisions with the owner before writing steps, and produces stop conditions, tests to write first, and numbered acceptance criteria that each say how they are verified. Use when filing work for another agent, a cheaper model or a later session ("write an issue for this", "make this issue ready for an agent", "polish these issues", "so another agent can start it"). Not for one-line notes to yourself; for a design doc in the repo, use design-doc.
---

# Issue brief

An issue another agent will implement has to stand alone. The agent was not in your conversation, follows explicit steps well, fills gaps badly, and does not know when to stop. A good brief gives it every fact it needs, true in the code today, plus the edges it must not cross and a way to check its own work.

If the work already has a design doc, the issue links to it and does not copy it. If the work needs requirements and a design first, run `/design-doc`; its handoff plans are the in-repo form of the same idea.

## Steps

1. **Find the owner.** Search open issues for the same outcome a person would notice. Add to that issue instead of filing a sibling. One issue is one outcome; slices are a checklist inside it.
2. **Size it** and say which size: *small fix* or *feature / multi-slice*. The template for each is in `references/template.md`.
3. **Read the code at the current default branch**, not your memory or someone's review. Fetch, record the commit, and name the files, functions and constants the implementer will touch. Mark every fact **verified** (you read it at that commit) or **reported** (someone else said it). If a reported claim is false in the code, say so in the brief.
4. **List the decisions.** Every choice the owner must make, each with your recommendation and its reason. Ask before writing steps that depend on an answer. Record each answer in the brief with its date; a decision that lives only in chat is lost.
5. **Make vague decisions explicit.** "Inherit by default" or "where it makes sense" becomes a list: add, do not add, unchanged. Say so if your list is narrower than the decision.
6. **Write the brief** from the template:
   - *What exists today*: numbered facts with paths and symbols.
   - *Steps*: smallest complete change, in order.
   - *Stop and ask when*: one line per boundary the implementer could cross (authority, public API, data shape, cost, a limit), plus what not to stop for (moved line numbers, a symbol found by search).
   - *Tests to write first*, each pointing at an acceptance criterion.
   - *Acceptance criteria*, numbered, each with **how it is verified**: a named test, a command, a rendered check, a diff review, or an owner-only check.
7. **Gate risky slices.** A slice that changes cost (billed calls), security, sandboxing, stored data shapes or a public contract needs a written proposal approved before code. List what the proposal must answer.
8. **Route owner-only checks.** Anything that needs a signed-in account, billed turns, a device or a second machine goes to whoever can run it (a standing checklist issue if the project has one). The implementer prepares for it and does not wait.
9. **Sequence related issues.** If issues touch the same files or build on each other, write the order into each.
10. **Read it as a stranger, save it, read it back.** Reread the brief as if you knew nothing from this session. After saving, fetch the issue again and confirm the text landed; tracker edits can silently fail on link markup.

## Rules that matter most

- **One current text.** Replace stale content in place. Never stack a "corrections" section on an older text, and keep exactly one dated status block.
- **Facts carry their commit.** "Verified at `abc1234`" lets the implementer detect drift.
- **No silent assumptions.** An open question in the brief beats a guessed answer in the code.
- **Every criterion is checkable.** "Works well" is not a criterion; "the export includes tags, proven by `test_export_includes_tags`" is.
- **Name things exactly**: paths, symbols, test names, the project's own check commands.
- **Keep tracker IDs out of code**, comments and test titles; they belong in the issue and the pull request description.

## Done when

- [ ] The size is stated and the matching template is used.
- [ ] Every fact names its file or symbol and is marked verified (with commit) or reported.
- [ ] No step depends on an open decision; decisions are recorded with dates.
- [ ] Every boundary has a stop condition.
- [ ] Every acceptance criterion is numbered and says how it is verified, and every test to write first points at one.
- [ ] Owner-only checks are routed away from the implementer.
- [ ] The saved issue was read back and matches what you wrote.
