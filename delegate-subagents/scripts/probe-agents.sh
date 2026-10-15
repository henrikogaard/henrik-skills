#!/usr/bin/env bash
# Probe which agent CLIs are installed and whether the flags in
# references/registry.md still appear in their --help output.
# Usage: probe-agents.sh [agent ...]   (default: all known agents)
# Prints one line per flag: OK, MISSING, or a NOT INSTALLED line per agent.
# Read-only: runs only --help and --version.

set -u

# agent|binary|help command|space-separated flags to look for
REGISTRY='
codex|codex|codex exec --help|-m -C -s read-only workspace-write --approve-for-me --json --skip-git-repo-check resume
claude|claude|claude --help|-p --model --allowedTools --permission-mode acceptEdits --output-format
grok|grok|grok --help|-p --single -m --prompt-file --output-format --permission-mode --always-approve
cursor|~/.local/bin/agent|~/.local/bin/agent --help|-p --print --model --mode --force --output-format
omp|omp|omp --help|-p --model --max-time --mode --no-session --tools --auto-approve
pi|pi|pi --help|-p --model --mode --no-session --session-id --tools --list-models
devin|devin|devin --help|-p --model --prompt-file --permission-mode accept-edits
'

known="codex claude grok cursor omp pi devin"
wanted="${*:-$known}"
for w in $wanted; do
  case " $known " in *" $w "*) ;; *) echo "$w: UNKNOWN (known: $known)" ;; esac
done

# Cursor's CLI installs as ~/.local/bin/agent, but a bare "agent" on PATH
# can resolve to another vendor's shim (Grok ships ~/.grok/bin/agent), so
# the registry names Cursor by path. A "~/" prefix is expanded here.
find_bin() {
  case "$1" in
    "~/"*) local p="$HOME/${1#"~/"}"; [ -x "$p" ] && echo "$p" ;;
    *) command -v "$1" 2>/dev/null ;;
  esac
}

echo "probe date: $(date +%Y-%m-%d)  host: $(hostname -s)"
echo "$REGISTRY" | while IFS='|' read -r name bin helpcmd flags; do
  [ -z "$name" ] && continue
  case " $wanted " in *" $name "*) ;; *) continue ;; esac

  path="$(find_bin "$bin")"
  if [ -z "$path" ]; then
    echo "$name: NOT INSTALLED"
    continue
  fi

  version="$("$path" --version 2>/dev/null </dev/null | head -n 1)"
  echo "$name: $path ${version:+($version)}"

  # Swap the bare binary name for its resolved path, then capture help.
  help="$(eval "\"$path\"${helpcmd#"$bin"}" 2>&1 </dev/null)"
  for flag in $flags; do
    # Match the flag as a whole token, so "-m" does not match inside "--model".
    escaped="$(printf '%s' "$flag" | sed 's/[][\.*^$+?(){}|/]/\\&/g')"
    if printf '%s\n' "$help" | grep -Eq -- "(^|[^[:alnum:]-])${escaped}([^[:alnum:]-]|$)"; then
      echo "  OK       $flag"
    else
      echo "  MISSING  $flag"
    fi
  done
done
