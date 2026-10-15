# Test suite review

Read this before reviewing tests. Agents often write too many tests: many near-copies, tests of private helpers, and tests that only prove a mock was called. A big suite like that is slow, breaks on every refactor, and still misses real bugs. The goal is **fewer, stronger tests at seams**.

## What earns a test its place

A test earns its place when it would **fail on a real behavior regression that no other kept test catches**, and it tests through an interface a caller uses. Everything else is a candidate to merge, move or delete.

## Smells

| Smell | How to spot it | Verdict |
|---|---|---|
| **Duplicate** | Same body, or same setup and assertion with renamed values (`test_total_1`, `test_total_2`). | Merge into one table-driven or parametrized test, keeping the distinct cases. |
| **No assertion** | The test calls code and checks nothing, or only checks that nothing raised. | Delete, or add the assertion the behavior needs. |
| **Tautological** | The expected value is computed the same way as the code (`assert f(x) == f(x)`, `expect(a+b).toBe(a+b)`), or asserts a constant against itself. | Delete, or replace the expectation with an independent known value. |
| **Implementation-coupled** | Mocks the module's own internals, asserts call counts or call order on internal helpers, or checks state through a side door (reading the database instead of the interface). Breaks on refactor while behavior stays the same. | Rewrite at the seam: assert on the result a caller sees. Keep a mock only at a real external dependency. |
| **Private helper test** | Tests a `_private` function whose behavior the public tests already cover. | Delete if covered via the interface; otherwise move the case to an interface test. |
| **Trivia** | Tests getters, constants, dataclass fields, or that the framework or language works. | Delete. |
| **Combinatorial pile** | Dozens of tests varying one input, most hitting the same branch. | Keep one case per branch or boundary in a table; drop the rest. |
| **Snapshot sprawl** | Large snapshots nobody reads, updated on every change. | Replace with targeted assertions on what matters. |
| **Permanently skipped** | `skip`, `xfail`, `xit` with no plan to fix. | Delete, or fix and unskip. Report which. |
| **Slow or flaky** | Real sleeps, network, time or randomness without control. | Pin the clock or seed, fake the network at the seam, or move it to a separate slow suite. |

Also list **missing tests**: important behaviors (often the riskiest combinations, such as discount plus tax, or a race) that no test covers. A suite can be too big and still have holes.

## Deletion safety check

Before any test is deleted (during the build, after approval), prove the behavior stays covered:

1. Run the suite and record the result.
2. If a coverage tool is available, record coverage before and after the cleanup. Covered lines in the code under test must not drop.
3. Without coverage, do a **mutation spot-check** for each removed group: briefly break the behavior it tested (flip a condition, change a constant), run the kept tests, and confirm at least one fails. Undo the break.
4. Record the result in the design doc's Verification table.

Never delete the only test of a behavior. If a weak test is the only cover, replace it with a stronger one first.
