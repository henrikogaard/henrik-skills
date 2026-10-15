# Architecture smells

Read this before reviewing code. For each smell: how to spot it, the evidence a finding needs, and the usual fix. Use the scripts' output to find suspects, then read the code to confirm.

| Smell | How to spot it | Evidence to cite | Usual fix |
|---|---|---|---|
| **God module** | One file or class with several unrelated reasons to change: pricing, email and export in one place. Often the top hot spot. | Line count, commits, and the distinct responsibilities with line ranges (`orders.py:40-95 pricing`, `:96-150 email`). | Split by reason to change: one module per responsibility, each with a small interface. Name the new modules. |
| **Shallow module / pass-through** | A wrapper, service or manager whose methods just call another function with the same arguments. | Each delegating method with `file:line`; the deletion test result; how many callers use it. | Delete it and call the real module, or move real logic into it so it earns its interface. |
| **Speculative abstraction** | An interface, base class, factory or plugin hook with exactly one implementation and no second one planned. One implementation is a hypothetical seam; two make it real. | The abstraction, its single implementation, and the absence of a second (search for subclasses or implementations). | Inline it. Reintroduce the seam when a second implementation actually arrives. |
| **Duplicated logic** | The same rule written twice, often drifting apart (tax computed in two places, two money formatters). | Both locations with `file:line`, and any difference between them (a drift is a bug waiting). | One owner for the rule; other places call it. |
| **Feature envy / leaky seam** | Code in module A reaches into B's data or internals and recomputes what B should answer. | The reaching code, the internals it touches, and the co-change count between the two files. | Move the logic into B and give B an interface for the question A asks. |
| **Shotgun surgery** | One kind of change needs edits in many files. Shows up as files that always change together. | The co-change pairs or cluster from `repo_facts.py` with counts, and an example commit. | Gather what changes together into one module. |
| **Dependency tangle** | Import cycles, or low-level modules importing high-level ones. | The import chain (`a → b → c → a`). | Break the cycle at the seam: move the shared piece down, or invert the dependency. |
| **Dead code** | Functions, classes, flags or files with no callers, or features behind flags that are always off. | A search showing zero callers (include dynamic use: string lookups, reflection, config). | Delete it. Mark it `Speculative` if dynamic use cannot be ruled out. |
| **Hidden dependencies** | A module creates its own collaborators (database, clock, HTTP client, mail) inside its logic, so it cannot be tested without them. | The construction site and the tests that patch around it. | Pass the dependency in at a seam; test through the interface with a fake at that seam. |
| **Config and flag sprawl** | Many options, flags or modes that each fork behavior, most never changed. | The flags, their defaults, and how many are ever set. | Remove dead flags; collapse modes that never differ. |

## Ranking

- **Strong**: clear evidence, it sits in a hot spot, and the fix is incremental.
- **Worth exploring**: real evidence, but the payoff or the fix is less certain.
- **Speculative**: plausible, but evidence is thin or dynamic use cannot be ruled out.

Weigh hot spots highest. Clean-up in code nobody touches pays back little; the same clean-up in the file that changes every week pays back every week.
