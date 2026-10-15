# Agent CLI registry

How to run each agent CLI headlessly. These flags change often and the table is machine-local, so **run the probe before trusting a row**:

```bash
scripts/probe-agents.sh codex claude   # name only the agents you will fire
```

The probe prints `OK` or `MISSING` for every flag listed below. When the probe and this table disagree, the probe wins: fix the row and its date here if the file is writable; otherwise note the correction in the run's `MANIFEST.md` and tell the user.

Last verified: **2026-10-14** on Henrik-MBPr. Treat every row as unverified when that date is more than ~30 days old or you are on another machine.

| Agent | Run from the repo root | Model flag | Long brief from a file | Analysis-only | Edits allowed | Version checked |
|---|---|---|---|---|---|---|
| codex | `codex exec -C <dir> [-m <model>] -` | `-m` | stdin: `codex exec - < brief.md` | `-s read-only` | `-s workspace-write --approve-for-me` | 0.162.1 |
| claude | `claude -p "$(cat brief.md)" [--model <model>]` | `--model` | `"$(cat brief.md)"` | `--allowedTools "Read,Grep,Glob"` | `--permission-mode acceptEdits` | 2.1.299 |
| grok | `grok -p --prompt-file brief.md [-m <model>]` | `-m` | `--prompt-file brief.md` | `--permission-mode plan` | `--always-approve` | 1.0.50 |
| cursor | `~/.local/bin/agent -p "$(cat brief.md)" [--model <model>]` | `--model` | `"$(cat brief.md)"` | `--mode plan` (required: `-p` alone can write and run shell) | `--force` | 2026.10.01 |
| omp | `omp -p [--model <fuzzy>] --max-time 10m @brief.md "Follow the brief."` | `--model` (fuzzy: `opus`, `openai/gpt-5.2`) | `@brief.md` | `--tools=` a read-only list (check tool names in `omp --help`) | `--auto-approve` | 18.6.0 |
| pi | `pi -p [--model <provider/id>] --no-session @brief.md "Follow the brief."` | `--model` | `@brief.md` | `--tools read,grep,find,ls` | none: keep pi analysis-only | 1.1.0 |
| devin | `devin -p --prompt-file brief.md [--model <model>]` | `--model` | `--prompt-file brief.md` | default (`--permission-mode auto`, read-only tools) | `--permission-mode accept-edits` | 3000.11.3 |

## Gotchas

- **Cursor is called by path.** In a non-interactive shell, a bare `agent` resolves to Grok's shim (`~/.grok/bin/agent`), and `cursor agent` starts an interactive session. Use `~/.local/bin/agent -p`.
- **codex refuses to run outside a git repo** unless you pass `--skip-git-repo-check`. Follow-ups: `codex exec resume --last`.
- **omp has the only native wall-clock cap** (`--max-time`). For the others, stop the background task yourself past the deadline. Stock macOS has no `timeout(1)`, so do not wrap commands in it.
- **JSON output** when you need machine-readable results: codex `--json`, claude and cursor `--output-format json`, grok `--output-format json`, omp and pi `--mode json`.
- **Model lists:** `omp models`, `grok models`, `pi --list-models`, `devin --help` (see `--model`). Ask the user rather than guessing a model ID.
- **Always pass long briefs through a file** (stdin, `--prompt-file`, `@file` or `"$(cat brief.md)"`). Hand-escaped inline prompts break on quotes.
- **ANSI noise in output:** strip it with `sed $'s/\x1b\[[0-9;]*[mGK]//g'`.
