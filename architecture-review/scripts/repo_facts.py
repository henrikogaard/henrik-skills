#!/usr/bin/env python3
"""Facts for an architecture review: hot spots, big files, co-change pairs, test inventory.

Usage: repo_facts.py <repo> [--scope PATH] [--since "12 months ago"] [--top N] [--json]

Read-only. Uses `git log` when the repo is a git repository; without git it
reports sizes and tests only. Standard library only.
"""
import argparse
import itertools
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "out", "target", ".venv", "venv",
             "__pycache__", ".next", ".turbo", "coverage", ".mypy_cache", ".pytest_cache", ".idea", ".vscode"}
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rb", ".java", ".kt", ".swift",
            ".rs", ".cs", ".php", ".scala", ".c", ".cc", ".cpp", ".h", ".hpp", ".m", ".ex", ".exs", ".dart"}
BIG_COMMIT = 30  # commits touching more files than this are treated as noise for co-change

TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|specs)(/|$)|(^|/)test_[^/]+$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$")
TEST_CASE = {
    ".py": re.compile(r"^\s*(async\s+)?def\s+test\w*\s*\("),
    ".go": re.compile(r"^func\s+Test\w*\s*\("),
    ".rb": re.compile(r"^\s*(it|test)\s+['\"]"),
    ".java": re.compile(r"@Test\b"),
    ".kt": re.compile(r"@Test\b"),
    ".cs": re.compile(r"\[(Test|Fact|Theory)\]"),
    ".rs": re.compile(r"#\[test\]"),
    ".swift": re.compile(r"^\s*func\s+test\w*\s*\("),
}
JS_CASE = re.compile(r"^\s*(it|test)(\.each\([^)]*\))?\s*\(")
for ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
    TEST_CASE[ext] = JS_CASE


def is_test(path):
    return bool(TEST_PATH.search(path))


def walk(repo, scope):
    root = os.path.join(repo, scope) if scope else repo
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            ext = os.path.splitext(fn)[1]
            if ext in CODE_EXT:
                full = os.path.join(dirpath, fn)
                yield os.path.relpath(full, repo).replace(os.sep, "/"), ext


def count_lines(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return 0
    if b"\0" in data[:4096]:
        return 0
    return sum(1 for line in data.decode("utf-8", "replace").splitlines() if line.strip())


def count_cases(path, ext):
    pat = TEST_CASE.get(ext)
    if not pat:
        return 0
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return sum(1 for line in f if pat.search(line))
    except OSError:
        return 0


def git_log(repo, since, scope):
    try:
        subprocess.run(["git", "-C", repo, "rev-parse", "--git-dir"], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    cmd = ["git", "-C", repo, "log", f"--since={since}", "--no-merges", "--name-only", "--format=@@%H"]
    if scope:
        cmd += ["--", scope]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    commits, current = [], None
    for line in out.splitlines():
        if line.startswith("@@"):
            current = []
            commits.append(current)
        elif line.strip() and current is not None:
            current.append(line.strip())
    return commits


def top_folder(path, scope):
    rel = path[len(scope):].lstrip("/") if scope and path.startswith(scope) else path
    parts = rel.split("/")
    return (scope.rstrip("/") + "/" if scope else "") + (parts[0] if len(parts) > 1 else ".")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo")
    ap.add_argument("--scope", default="", help="only look under this path (relative to repo)")
    ap.add_argument("--since", default="12 months ago")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        sys.exit(f"not a directory: {repo}")
    scope = a.scope.strip("/")

    files = {}
    for rel, ext in walk(repo, scope):
        full = os.path.join(repo, rel)
        files[rel] = {"lines": count_lines(full), "test": is_test(rel), "ext": ext,
                      "cases": count_cases(full, ext) if is_test(rel) else 0}

    commits = git_log(repo, a.since, scope)
    churn = Counter()
    pairs = Counter()
    if commits is not None:
        for c in commits:
            touched = sorted({f for f in c if f in files})
            for f in touched:
                churn[f] += 1
            if 1 < len(touched) <= BIG_COMMIT:
                for x, y in itertools.combinations(touched, 2):
                    pairs[(x, y)] += 1

    src = {f: v for f, v in files.items() if not v["test"]}
    hot = sorted(src, key=lambda f: (churn[f] * max(src[f]["lines"], 1), churn[f], src[f]["lines"]), reverse=True)
    hot = [f for f in hot if churn[f] > 0 and src[f]["lines"] > 0][: a.top]
    big = [f for f in sorted(src, key=lambda f: src[f]["lines"], reverse=True) if src[f]["lines"] > 0][: a.top]
    co = [(x, y, n) for (x, y), n in pairs.most_common() if n >= 2][: a.top]

    folders = defaultdict(lambda: {"src_lines": 0, "test_lines": 0, "test_files": 0, "test_cases": 0})
    for f, v in files.items():
        d = folders[top_folder(f, scope)]
        if v["test"]:
            d["test_lines"] += v["lines"]; d["test_files"] += 1; d["test_cases"] += v["cases"]
        else:
            d["src_lines"] += v["lines"]
    test_files = sorted((f for f, v in files.items() if v["test"]), key=lambda f: files[f]["cases"], reverse=True)

    total_src = sum(v["lines"] for v in src.values())
    total_test = sum(v["lines"] for v in files.values() if v["test"])
    total_cases = sum(v["cases"] for v in files.values())
    result = {
        "repo": repo, "scope": scope or ".", "since": a.since,
        "git": commits is not None, "commits": len(commits or []),
        "files": len(files), "source_lines": total_src, "test_lines": total_test, "test_cases": total_cases,
        "hot_spots": [{"file": f, "commits": churn[f], "lines": src[f]["lines"]} for f in hot],
        "largest": [{"file": f, "lines": src[f]["lines"], "commits": churn[f]} for f in big],
        "co_change": [{"a": x, "b": y, "commits": n} for x, y, n in co],
        "folders": [{"folder": k, **v} for k, v in sorted(folders.items())],
        "test_files": [{"file": f, "cases": files[f]["cases"], "lines": files[f]["lines"]} for f in test_files[: a.top]],
    }
    if a.json:
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    p = print
    p(f"# Repo facts: {result['scope']} in {repo}")
    ratio = f" · test/source {total_test / total_src:.1f}" if total_src else ""
    p(f"{result['files']} code files · {total_src} source lines · {total_test} test lines · {total_cases} test cases{ratio}")
    if result["git"]:
        p(f"{result['commits']} commits since {a.since} (merges and commits touching >{BIG_COMMIT} files excluded from co-change)")
    else:
        p("Not a git repository: no hot spots or co-change.")
    if hot:
        p("\n## Hot spots (commits × lines)\n| File | Commits | Lines |\n|---|---|---|")
        for h in result["hot_spots"]:
            p(f"| {h['file']} | {h['commits']} | {h['lines']} |")
    p("\n## Largest source files\n| File | Lines | Commits |\n|---|---|---|")
    for b in result["largest"]:
        p(f"| {b['file']} | {b['lines']} | {b['commits']} |")
    if co:
        p("\n## Files that change together\n| File A | File B | Shared commits |\n|---|---|---|")
        for c in result["co_change"]:
            p(f"| {c['a']} | {c['b']} | {c['commits']} |")
    p("\n## Tests per folder\n| Folder | Source lines | Test lines | Test files | Test cases | Test/source |\n|---|---|---|---|---|---|")
    for d in result["folders"]:
        ratio = f"{d['test_lines'] / d['src_lines']:.1f}" if d["src_lines"] else "—"
        p(f"| {d['folder']} | {d['src_lines']} | {d['test_lines']} | {d['test_files']} | {d['test_cases']} | {ratio} |")
    if test_files:
        p("\n## Test files by case count\n| File | Cases | Lines |\n|---|---|---|")
        for t in result["test_files"]:
            p(f"| {t['file']} | {t['cases']} | {t['lines']} |")


if __name__ == "__main__":
    main()
