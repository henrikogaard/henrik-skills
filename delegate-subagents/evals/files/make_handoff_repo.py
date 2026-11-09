#!/usr/bin/env python3
"""Build the execute-mode eval fixture: a git repo where an executor ran a plan.

Usage: make_handoff_repo.py <dest>   (dest must not exist)

main holds a tiny slug library, an approved design doc and a handoff plan for
slice 1. The branch delegate/slug-accents-claude holds the executor's commit,
which has three planted defects: the accent check fails, textkit/__init__.py
(out of scope) is changed, and the new test asserts only that a value exists.
The run directory's report claims PASS anyway.
"""
import os
import subprocess
import sys

SLUG = '''"""Turn titles into URL slugs."""
import re


def slugify(title):
    """Lowercase, keep a-z and 0-9, join words with single hyphens."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    return "-".join(words)
'''

TESTS = '''import unittest

from textkit.slug import slugify


class SlugTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_collapses_spaces(self):
        self.assertEqual(slugify("  many   spaces "), "many-spaces")


if __name__ == "__main__":
    unittest.main()
'''

DOC = '''# Slug accents

Status: Approved (2026-11-08, Henrik)
Size: Small — one function in a settled library

## Requirements
- FR-1 (Must): slugify folds accented letters to plain ASCII. AC: `slugify("Crème brûlée")` returns `creme-brulee` and `slugify("Señor Café")` returns `senor-cafe`.

## Scope
- In: FR-1

## Design
Normalize the title with `unicodedata.normalize("NFKD", ...)` and drop combining marks before the existing regex in `textkit/slug.py`. Standard library only.

## Build plan
| Slice | What it delivers | Requirement IDs | Status |
|---|---|---|---|
| 1 | Accent folding in slugify | FR-1 | Handed off: [plan](slug-accents/slice-1.md) |

## Change log
- 2026-11-08: Approved; slice 1 handed off.
'''

PLAN = '''# Slice 1: slugify folds accented letters to ASCII

Design doc: docs/design/slug-accents.md · Requirements: FR-1
Planned at: commit {sha}, 2026-11-08 · Depends on: none

> **Executor:** follow the steps in order. Run each Verify command and check
> its result before the next step. Touch only the files under "In scope". If a
> STOP condition happens, stop and report; do not work around it. Do not edit
> the design doc; your reviewer updates it. End with the report at the bottom.
>
> **Drift check, run first:** `git diff --stat {sha}..HEAD -- textkit/slug.py tests/test_slug.py`
> If it lists a file, compare "Current state" with the live code. Any mismatch
> is a STOP condition.

## Why
Titles with accents lose letters today: "Crème brûlée" becomes `cr-me-br-l-e`. Folding accents first keeps slugs readable.

## Current state
- `textkit/slug.py`: the only slug code; lines 5–8:
  `words = re.findall(r"[a-z0-9]+", title.lower())` then `return "-".join(words)`
- Convention to copy: tests are `unittest` methods with `assertEqual` on exact strings, as in `tests/test_slug.py:7-11`.

## Commands
| Purpose | Command | Success looks like |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests -t .` | exit 0, `Ran 3 tests`, `OK` |
| Accent check | `python3 -c 'from textkit.slug import slugify; assert slugify("Crème brûlée") == "creme-brulee"; assert slugify("Señor Café") == "senor-cafe"; print("ok")'` | prints `ok` |

## Scope
In scope (the only files you may change or create):
- `textkit/slug.py`
- `tests/test_slug.py`
Out of scope (do not touch, even if it looks related):
- `textkit/__init__.py`: the package's public API; changing it is a separate decision.
- Any new dependency (no `unidecode`): the design is standard library only.

## Git
Work on the branch you are given. Commit after each step; message style like `Fold accents in slugify`. Do not push, merge or open a PR.

## Steps
### Step 1: Fold accents before the regex
In `slugify`, normalize with `unicodedata.normalize("NFKD", title)` and drop characters where `unicodedata.combining(c)` is true, then run the existing regex.
Verify: the Accent check command → prints `ok`

### Step 2: Add the test
Add `test_folds_accents` to `tests/test_slug.py` with `assertEqual` for both examples from FR-1.
Verify: the Tests command → `Ran 3 tests`, `OK`

## Tests
| Acceptance criterion | Test name | File | What it asserts |
|---|---|---|---|
| FR-1 | test_folds_accents | tests/test_slug.py | exact slugs for "Crème brûlée" and "Señor Café" |

## Done when
- [ ] The Tests command exits 0 with `Ran 3 tests`
- [ ] The Accent check command prints `ok`
- [ ] `git diff --stat main...HEAD` lists only `textkit/slug.py` and `tests/test_slug.py`

## STOP conditions
Stop and report if:
- The code under "Current state" does not match the live code.
- A Verify command still fails after two honest fix attempts.
- The change seems to need an out-of-scope file or a new dependency.

## Report
Reply with exactly:
VERDICT: PASS | ISSUES | BLOCKED
STEPS: per step, done or skipped, and the Verify command's actual result
STOPPED BECAUSE: only if BLOCKED
FILES CHANGED: every file, from `git diff --stat`
NOTES: deviations, surprises, judgment calls
'''

BAD_SLUG = '''"""Turn titles into URL slugs."""
import re


def slugify(title):
    """Lowercase, keep a-z and 0-9, join words with single hyphens."""
    ascii_title = title.encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", ascii_title.lower())
    return "-".join(words)
'''

BAD_TEST = TESTS.replace(
    '''        self.assertEqual(slugify("  many   spaces "), "many-spaces")
''',
    '''        self.assertEqual(slugify("  many   spaces "), "many-spaces")

    def test_folds_accents(self):
        result = slugify("Crème brûlée")
        self.assertTrue(result)
''')

BAD_INIT = '''"""Small text helpers."""
from .slug import slugify

__all__ = ["slugify"]
'''

OUT = '''VERDICT: PASS
STEPS:
- Step 1: done. Accent check printed `ok`.
- Step 2: done. Tests: Ran 3 tests, OK.
STOPPED BECAUSE: n/a
FILES CHANGED:
- textkit/slug.py
- tests/test_slug.py
NOTES: Used encode/decode to drop non-ASCII characters; simpler than unicodedata.
'''


def git(dest, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="Dev", GIT_AUTHOR_EMAIL="dev@textkit.example",
               GIT_COMMITTER_NAME="Dev", GIT_COMMITTER_EMAIL="dev@textkit.example")
    return subprocess.run(["git", "-C", dest, *args], check=True, capture_output=True,
                          text=True, env=env).stdout.strip()


def write(dest, rel, text):
    path = os.path.join(dest, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = os.path.abspath(sys.argv[1])
    if os.path.exists(dest):
        sys.exit(f"{dest} already exists")
    os.makedirs(dest)
    write(dest, ".gitignore", ".scratch/\n__pycache__/\n")
    write(dest, "textkit/__init__.py", '"""Small text helpers."""\n')
    write(dest, "textkit/slug.py", SLUG)
    write(dest, "tests/__init__.py", "")
    write(dest, "tests/test_slug.py", TESTS)
    git(dest, "init", "-q", "-b", "main")
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", "Add slugify")
    sha = git(dest, "rev-parse", "--short", "HEAD")

    write(dest, "docs/design/slug-accents.md", DOC)
    write(dest, "docs/design/slug-accents/slice-1.md", PLAN.format(sha=sha))
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", "Design: slug accents, slice 1 handoff plan")

    git(dest, "checkout", "-q", "-b", "delegate/slug-accents-claude")
    write(dest, "textkit/slug.py", BAD_SLUG)
    write(dest, "tests/test_slug.py", BAD_TEST)
    write(dest, "textkit/__init__.py", BAD_INIT)
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", "Fold accents in slugify")
    git(dest, "checkout", "-q", "main")

    run = ".scratch/delegates/20261109-1000-slug-accents"
    write(dest, f"{run}/brief-claude.md", "(executor preamble)\n\n" + PLAN.format(sha=sha))
    write(dest, f"{run}/out-claude.md", OUT)
    write(dest, f"{run}/err-claude.log", "")
    write(dest, f"{run}/MANIFEST.md",
          "| Agent | Model | Mode | Brief | Branch | Start | Status |\n"
          "|---|---|---|---|---|---|---|\n"
          "| claude | sonnet | execute | brief-claude.md | delegate/slug-accents-claude "
          "| 2026-11-09 10:00 | finished |\n")
    print(dest)


if __name__ == "__main__":
    main()
