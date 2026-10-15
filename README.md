# henrik-skills

Three agent skills in the open Agent Skills layout (`SKILL.md` with frontmatter). They work in Claude Code and any harness that reads `~/.agents/skills`.

| Skill | What it does | Reach for it when |
|---|---|---|
| `/design-doc` | The start of all new engineering work: requirements, scope, conceptual and logical design in one Markdown doc, an approval stop, then detailed design written slice by slice while building | "Let's build…", "new feature", "what are we building?" |
| `/delegate-subagents` | Runs external agent CLIs (codex, claude, grok, cursor, omp, pi, devin) in parallel and reconciles their output | "Ask codex and claude", "second opinion" |
| `/summary-tables` | Formats status and close-out readouts as one evidence-backed table | "Is #88 done?", "what shipped?" |

## The design doc flow

Every piece of new work gets one file, `docs/design/<slug>.md`, that grows with the work:

```
Phase 1 (plan):  requirements → scope → conceptual → logical → decisions → build plan → stop for approval
Phase 2 (build): for each slice: detailed design → implement → verify → update the doc
```

- **A status line** at the top says where the work stands: `Draft` → `Approved` → `Building (slice n of m)` → `Done`.
- **Decisions** are a numbered `D-n` log inside the doc, not separate ADR files. An accepted decision is never rewritten; a new one supersedes it.
- **Detailed design is written per slice**, just before that slice is built, so it describes real code. The doc's Verification table maps each acceptance criterion to its test and result.
- **Size decides the depth**: trivial fixes get no doc, small work a short doc under ~60 lines, and new systems the full doc.
- **New scope on an existing doc** updates that doc, sets it back to `Draft` and asks for approval again.

Typical prompts:

| You say | What happens |
|---|---|
| "Let's build class booking for the gym" | Phase 1: writes the doc as `Draft`, stops and asks you to approve |
| "Approved, go ahead with slice 1" | Phase 2: detailed design for slice 1, code, tests, doc updated |
| "Can we also add a waitlist?" | Updates the existing doc, back to `Draft`, asks again |
| "Fix the typo in the README" | Trivial: no doc, just the fix |

## How each skill is built

Every skill follows the same shape, so it works for strong and weak models alike:

```text
skill-name/
  SKILL.md          # short core: when, steps, the rules that matter, "Done when" checklist
  references/       # detail the model reads only when a step points to it
  scripts/          # deterministic helpers, run rather than read
  evals/
    evals.json      # test prompts with checkable expectations
    files/          # fixtures the prompts refer to
```

- **SKILL.md stays short** (about 100 lines or less). A weaker model follows the steps and the checklist; a stronger one pulls in references when it needs depth.
- **Facts a model cannot guess go in references or scripts.** For example, `delegate-subagents/scripts/probe-agents.sh` checks every CLI flag against live `--help` output, because those flags change between releases.
- **No skill depends on a skill that is not in this repo.**

## Install

From the main checkout (not a worktree):

```bash
./install.sh --dry-run
./install.sh
```

It symlinks each skill folder into `~/.claude/skills` and `~/.agents/skills`, and removes links into this repo whose skill no longer exists. It never touches real files or folders; a clash with one is reported and skipped. Set `SKILL_TARGETS="dir1 dir2"` to use other folders.

Claude Code can turn a skill off in `~/.claude/settings.json` under `skillOverrides`. If a skill is linked but never shows up, check there.

## Checks

```bash
python3 scripts/check_skills.py
```

Checks frontmatter, SKILL.md length, that every `references/` and `scripts/` path a skill names exists, that every slash-named skill in a Markdown file is in this repo, and that each `evals/evals.json` parses and its fixture files and project folders exist.

## Evals

Each skill has 3–5 test prompts in `evals/evals.json`, each with a list of `expectations`: statements a grader marks true or false from the output. They follow the format of Anthropic's `skill-creator` skill.

To run them, ask an agent with `skill-creator`: "run the evals for design-doc against the version on main". For each prompt it runs one agent with the new skill and one with the baseline, grades the expectations, and opens a viewer to compare.

When running by hand:

1. Copy the skill **without** its `evals/` folder, so the agent under test cannot read the expectations.
2. Copy the fixtures from `evals/files/` to a neutral folder and point the prompt there. When an eval sets `project`, copy that folder as the agent's project root, fresh for every run, because the agent edits it.
3. Run the prompt with the skill and with the baseline (no skill, or the old version), ideally on a small model too: a skill that only works on the strongest model is fragile.
4. Tell the agent where to write files and to put its full final message in `answer.md`. If you also want a short chat reply such as "done", say plainly that it is separate from `answer.md`; otherwise some agents write only "done" there.
5. Mark each expectation true or false with evidence. Grade the whole output folder, not only `answer.md`.

## License

MIT. See `LICENSE`.
