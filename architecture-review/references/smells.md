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
| **Dead code** | Functions, classes or files with no callers, and commented-out code. `code_leads.py` lists unreferenced names and commented-out blocks. | A search showing zero callers (include dynamic use: string lookups, reflection, config, entry points). | Delete it; git keeps the history. Mark it `Speculative` if dynamic use cannot be ruled out. |
| **Unfinished work** | Stubs (`NotImplementedError`, empty bodies, "not implemented" throws), TODO/FIXME clusters, features behind a flag that is always off, half-wired features (a route with no UI, a table nothing writes to). | The stub or flag with `file:line`, what calls it, and any stated intent (the TODO text, the flag's comment, the commit that added it). | Finish it or delete it; never leave it half-built. Recommend one, and ask the user as a `Q-n` when intent is unclear, because that is a product call. |
| **Special case** | Code for one situation instead of a rule: a branch on one literal value (`if tenant == "legacy-co"`), a parameter only one caller sets, a swallowed exception, a sleep or retry, a disabled test. | Each instance with `file:line`, and where the same value or rule repeats across files (`code_leads.py` sorts repeats first). | Do not fix them one by one. Find the requirement the design never modelled and propose that as the candidate (see below). |
| **Hidden dependencies** | A module creates its own collaborators (database, clock, HTTP client, mail) inside its logic, so it cannot be tested without them. | The construction site and the tests that patch around it. | Pass the dependency in at a seam; test through the interface with a fake at that seam. |
| **Config and flag sprawl** | Many options, flags or modes that each fork behavior, most never changed. | The flags, their defaults, and how many are ever set. | Remove dead flags; collapse modes that never differ. |

## Group symptoms under a root cause

Most findings are symptoms. Before ranking, ask of each group of findings: **what single change would make several of these unnecessary?** That change is the candidate, and the findings are its evidence. A root cause often looks nothing like its symptoms: a `provider == "paypal"` branch in refunds, a direct Stripe import in checkout and a retry that only one provider needs can all come from there being no payment-provider interface.

- Name the missing concept or rule, then list each symptom under it with `file:line`.
- Look for drift between the symptoms: two places that special-case the same thing differently are a live bug and raise the candidate's strength.
- A special case that still has a reason of its own after the fix (a real external quirk) stays; say why.

## Ranking

- **Strong**: clear evidence, it sits in a hot spot, and the fix is incremental.
- **Worth exploring**: real evidence, but the payoff or the fix is less certain.
- **Speculative**: plausible, but evidence is thin or dynamic use cannot be ruled out.

Weigh hot spots highest. Clean-up in code nobody touches pays back little; the same clean-up in the file that changes every week pays back every week.
