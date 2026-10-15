---
name: architecture-review
description: Review the architecture of an existing or legacy codebase and propose ranked, evidence-backed changes — modules to split, pass-through layers to delete, seams to move, duplicated or dead code to remove, and test suites to slim down (duplicate, tautological, over-mocked or implementation-coupled tests). Reports first and changes nothing; a candidate the user picks becomes a design-doc refactor. Use when the user asks to assess, review or untangle a codebase or module, wants refactoring or splitting advice, says some code is painful to change, or says there are too many or bad tests.
---

# Architecture review

Find where the structure makes change expensive, prove it with evidence, and rank what to fix. **Review first, change nothing.** The user picks a candidate; only then does it become work, through `/design-doc`.

## Words to think with

- **Module**: anything with an interface and an implementation (function, class, file, package).
- **Interface**: everything a caller must know to use a module: signature, invariants, error modes, ordering, config.
- **Deep module**: lots of behavior behind a small interface. **Shallow module**: the interface is nearly as big as what it hides.
- **Seam**: the place where behavior can be swapped or tested without editing the callers. Tests belong at seams.
- **Locality**: one change, one place. Its opposite is a change that drags edits across many files.
- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through; delete or inline it. If complexity reappears in many callers, it earns its place.

## Steps

1. **Scope.** If the user named an area or a pain point, review that. Otherwise let the hot spots choose (step 2). State the scope in the report's first lines.
2. **Gather facts with the scripts** (they run in seconds and work for any language):
   - `python3 <this-skill>/scripts/repo_facts.py <repo> [--scope <path>]`: hot spots (commits × size), largest files, files that change together, and the test inventory (test count and test-to-source ratio per folder).
   - `python3 <this-skill>/scripts/test_smells.py <repo> [--scope <path>]`: leads on duplicate, assertion-free, tautological, mock-heavy, call-count, private-access and skipped tests.
   Script output is a lead list, not a verdict. Confirm every lead by reading the code.
3. **Read the project's own rules first**: `AGENTS.md`, `README`, and any design docs (`docs/design/`). Decisions recorded there (`D-n`) stand unless the friction they cause is real and shown; then flag the conflict instead of ignoring the decision.
4. **Review the code in scope** against `references/smells.md`. A finding needs evidence: `file:line`, numbers (lines, callers, commits, co-changes), and one sentence on what it costs today ("a tax change touches 4 files").
5. **Review the tests in scope** against `references/tests.md`. Give each test file a verdict per test or group: keep, merge, move to a seam, delete, plus the behaviors that have no test at all. Never propose deleting the only test of a behavior.
6. **Rank the candidates.** At most 7, deepest first. Each gets a strength (`Strong`, `Worth exploring`, `Speculative`), an effort (S, M, L), a risk, and the payoff in plain terms (fewer files per change, fewer and stronger tests, a seam you can test at). A candidate without evidence is `Speculative` at best.
7. **Write the report** using `references/report-template.md`. Save it to the OS temp directory (`$TMPDIR`, falling back to /tmp) as `architecture-review-<repo>-<date>.md`, unless the user asked to keep it in the repo; then use `docs/architecture/review-<date>.md`. Give the path.
8. **Reply short, then stop.** The reply holds the report's path, the top three candidates (one line each) and one closing question: which candidate to pursue. Do not paste the report into the reply. Always end with that question, even if the user may be away; it is how the review hands over.

## When the user picks a candidate

Hand it to `/design-doc` as the source for a refactor (usually *Small*; *Full* if it moves contracts or data between modules). Its build plan must:

- start with **characterization tests** wherever the code to change has no test at a seam (see `references/legacy.md`);
- change in small, reversible slices that keep the build green, never a rewrite;
- for test cleanup, list every test to delete or merge with the kept test that covers the same behavior, and include the deletion safety check from `references/tests.md`.

## Rules

- **No changes during the review.** Read, run the scripts, run the existing tests if useful; edit nothing.
- **Fewer, deeper findings** beat a long list. Seven strong candidates are worth more than thirty nits.
- **Prefer removing to adding.** Delete pass-throughs, merge duplicates, inline speculative abstractions before proposing new layers.
- **Incremental over rewrite.** Every candidate must be doable in steps that each leave the code working.
- **Fewer, stronger tests.** The goal for a test suite is tests at seams that fail on real regressions, not a higher test count.

## Done when

- [ ] The scope is stated, and the scripts' facts are cited where they apply.
- [ ] Every candidate has evidence (`file:line` and numbers), a strength, an effort, a risk and a payoff.
- [ ] Every test file in scope has verdicts, and behaviors without tests are listed.
- [ ] No deletion is proposed for a test that is the only cover for its behavior.
- [ ] The report file exists, its path is given, and no source or test file was changed.
- [ ] The reply gives the report path and the top three, does not repeat the report, and ends by asking which candidate to pursue.
