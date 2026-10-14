# Reconcile rules per mode

Read the section for the mode you ran. The last section covers research fan-outs and writer–reviewer loops.

## Counsel

- **Join on your question numbers.** Each delegate's F-numbers are its own, so only the Q-numbers in the brief line answers up across agents.
- **Agreement** across model families is the strongest signal you get. Record it in one line of evidence per agent.
- **Conflict:** you are the chair, with repo context the delegates lack. Rule, and put the reasoning next to the dissent so the user can overrule you. If your ruling sides with an answer from your own model family, first give the contested finding to a delegate from another family for a second read. If no other family is on the roster, rule anyway and mark the ruling "not cross-checked".
- **Lone findings** are where a multi-agent run earns its cost. List every one.
- **Follow-up rounds stay blind**: delegates do not see each other's answers. Showing peers' answers is a different, adversarial mode; use it only if the user asks.

## Division

1. Check each slice: the promised artifact exists and the branch diff applies cleanly to the base.
2. Review each diff for injection-shaped changes: new dependencies, credential or secret access, CI or build-script edits, network calls. A quick read is not a security review; flag what you could not judge.
3. Merge the passing branches one at a time, resolving conflicts against the briefs. Escalate conflicts the briefs cannot settle.
4. Report failed slices honestly: which agent, which slice, what `err-<agent>.log` said. Offer to re-run a failed slice on another agent.

## Arena

1. **Read every candidate end to end.** Skimming favors the one that looks most familiar.
2. **Cross-judge.** In parallel with your own read, have a delegate from a different model family score each candidate against a rubric of 3–6 concrete criteria from the task ("adds a `--dry-run` flag", not "code is good"). If you and the judge disagree, re-read both rationales.
3. **Check convergence.** If every candidate landed on the same shape, ship the consensus. If they diverge wildly, the brief was under-specified: rewrite it and re-run instead of blending.
4. **Pick a base** a maintainer could extend most easily: cleaner boundaries, smaller surface. Not the one that reads best.
5. **Graft** the one or two best ideas from the others by porting ideas, not pasting chunks, so the result stays one coherent design. If nothing earns a port, ship the base as is.
6. **Verify** the grafted result with the task's own check: build, tests or the rubric.
7. **Write a synthesis note**: the base, each graft and its source, each rejection and why.

## Research fan-out and writer–reviewer loops

Use these when the task is a report or investigation rather than code.

- **Partition the question** into sub-questions that do not overlap and together cover the ask, one per researcher. Cut by dimension, or for "A versus B" questions, by hypothesis (one researcher per side, one testing the assumptions both share).
- **Merge findings before writing.** Group duplicate claims and mark whether support is independent or from one shared source. Three findings citing the same URL are one data point, not three.
- **Sweep coverage against the ask** before drafting. A gap found now costs one more researcher; found after drafting, it costs the draft.
- **Run the reviewer on a different model family** from the writer when you can; a shared model shares blind spots.
- **The reviewer ends with a verdict:** `revise` with specific defects, or `ship` citing each rubric point and naming what it actually inspected. A verdict applies only to the draft it read.
- **The writer revises against the critique only**, not with a fresh rewrite.
- **Stop** at `ship`, when the round budget is spent (default 2), or at the time ceiling. Record which one stopped it. If writer and reviewer deadlock, you rule and move on.
