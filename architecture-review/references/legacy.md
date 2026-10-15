# Changing legacy code safely

Read this when planning the build for a candidate. Legacy code is code without tests you trust. Change it in steps that each keep it working.

1. **Characterization tests first.** Before changing behavior-bearing code with no test at a seam, write tests that pin down what it does today, including odd behavior. They describe, not judge: if today's output looks wrong, record it as a `Q-n` instead of "fixing" it inside the refactor.
2. **Find or make a seam.** Test through an existing interface if one exists. If not, make the smallest seam that lets a test in: pass a dependency as a parameter, extract a function, wrap a global.
3. **Small, reversible steps.** Move one responsibility at a time. Run the tests after each step. Each step is its own commit, so any one can be reverted.
4. **Strangler, not rewrite.** For a big split: build the new module beside the old one, route callers to it one at a time, then delete the old path once nothing calls it.
5. **Branch by abstraction** when callers are many: put a thin interface in front of the old code, move callers to the interface, swap the implementation behind it, then remove the interface again if only one implementation is left.
6. **Separate moves from changes.** A slice either moves code (behavior identical, tests unchanged and green) or changes behavior (tests change on purpose). Never both in one slice.
7. **Where there is no safe seam**, say so in the plan. That is a finding: the first slice is to create one.
