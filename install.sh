#!/usr/bin/env bash
# Link every skill in this repo into the agent skill folders.
#
#   ./install.sh            link skills, remove dangling links into this repo
#   ./install.sh --dry-run  print what would change, change nothing
#
# Targets: ~/.claude/skills (Claude Code) and ~/.agents/skills (other
# harnesses). Override with SKILL_TARGETS="dir1 dir2".
# Only symlinks are created or removed. Real files and folders are never
# touched; a name clash with one is reported and skipped.

set -eu

dry=0
[ "${1:-}" = "--dry-run" ] && dry=1

repo="$(cd "$(dirname "$0")" && pwd -P)"

# Links must point at the main checkout. A linked worktree is deleted
# later, which would leave every link dangling.
if [ "$(git -C "$repo" rev-parse --git-dir)" != "$(git -C "$repo" rev-parse --git-common-dir)" ]; then
  echo "refusing: $repo is a linked git worktree; run install.sh from the main checkout" >&2
  exit 1
fi

targets="${SKILL_TARGETS:-$HOME/.claude/skills $HOME/.agents/skills}"

run() {
  if [ "$dry" = 1 ]; then echo "  would: $*"; else "$@"; fi
}

for target in $targets; do
  echo "$target"
  [ -d "$target" ] || run mkdir -p "$target"

  # Remove links into this repo whose skill no longer exists.
  for link in "$target"/*; do
    [ -L "$link" ] || continue
    dest="$(readlink "$link")"
    case "$dest" in "$repo"/*) ;; *) continue ;; esac
    if [ ! -e "$link" ]; then
      echo "  remove dangling $(basename "$link")"
      run rm "$link"
    fi
  done

  # Link each skill folder (any top-level folder holding a SKILL.md).
  for skill in "$repo"/*/SKILL.md; do
    dir="$(dirname "$skill")"
    name="$(basename "$dir")"
    link="$target/$name"
    if [ -L "$link" ]; then
      if [ "$(readlink "$link")" = "$dir" ]; then
        echo "  ok $name"
        continue
      fi
      echo "  relink $name (was $(readlink "$link"))"
      run ln -sfn "$dir" "$link"
    elif [ -e "$link" ]; then
      echo "  skip $name: a real file or folder already exists at $link"
    else
      echo "  link $name"
      run ln -s "$dir" "$link"
    fi
  done
done

[ "$dry" = 1 ] && echo "dry run: nothing changed"
exit 0
