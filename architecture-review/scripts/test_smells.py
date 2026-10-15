#!/usr/bin/env python3
"""Leads on weak or excess tests: duplicates, same-shape piles, no assertion,
tautologies, mock-heavy, call-count assertions, private access, skipped, snapshots.

Usage: test_smells.py <repo> [--scope PATH] [--json]

Heuristics for Python, JavaScript/TypeScript and Go tests. Every hit is a lead
to confirm by reading the test, not a verdict. Read-only; standard library only.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv", "__pycache__", "coverage"}
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|specs)(/|$)|(^|/)test_[^/]+$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$")
JS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}

ASSERT = {
    "py": re.compile(r"\bassert\b|self\.assert\w*\(|pytest\.raises|\.assert_\w+\(|assertRaises"),
    "js": re.compile(r"\bexpect\s*\(|\bassert\b|\.should\b"),
    "go": re.compile(r"\bt\.(Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b|\b(require|assert)\.\w+\("),
}
# One match per mock construction: "mock.patch(" counts once, not as "mock" plus "patch(".
MOCK = re.compile(r"(?:\bmock\.)?\bpatch(?:\.object|\.dict|\.multiple)?\s*\(|(?:\bmock\.)?\b(?:Magic|Async|NonCallable)?Mock\s*\(|\bcreate_autospec\s*\(|\b(?:jest|vi)\.(?:fn|mock|spyOn)\s*\(|(?<![.\w])spyOn\s*\(|\bsinon\.\w+\s*\(|\bgomock\.\w+\s*\(")
CALLS = re.compile(r"assert_called\w*|assert_has_calls|\.call_count\b|\.called\b|toHaveBeenCalled\w*|toBeCalled\w*|calledOnce|calledWith|\.Times\(")
SNAP = re.compile(r"toMatch(Inline)?Snapshot|\bsnapshot\b", re.I)
PRIVATE = {
    "py": re.compile(r"(?<!self)(?<!cls)\.\_[A-Za-z]\w*|\bimport\s+_[A-Za-z]\w*|,\s*_[A-Za-z]\w*\b(?=[^\n]*import)"),
    "js": re.compile(r"\[\s*['\"]_\w+['\"]\s*\]|as\s+any\)\s*\.\s*\w+|\.\#\w+|\._[A-Za-z]\w*\s*\("),
    "go": re.compile(r"$^"),  # same-package tests reach unexported names by design
}
TAUT = [
    re.compile(r"^\s*assert\s+(.+?)\s*==\s*\1\s*(#.*)?$"),
    re.compile(r"^\s*assert\s+True\s*$|assertTrue\(\s*True\s*\)|assertEqual\(\s*(.+?)\s*,\s*\1\s*\)"),
    re.compile(r"expect\((.+)\)\.(toBe|toEqual|toStrictEqual)\(\1\)"),
    re.compile(r"expect\(\s*true\s*\)\.toBe\(\s*true\s*\)"),
]
LITERAL = re.compile(r"(\"[^\"\n]*\"|'[^'\n]*'|`[^`\n]*`|\b\d+(\.\d+)?\b)")


def iter_files(root):
    """Yield (dirpath, filename) under root; a file root yields just itself."""
    if os.path.isfile(root):
        yield os.path.dirname(root), os.path.basename(root)
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            yield dirpath, fn


def lang(ext):
    return "py" if ext == ".py" else "js" if ext in JS else "go" if ext == ".go" else None


def py_tests(lines):
    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)(async\s+)?def\s+(test\w*)\s*\(", lines[i])
        if not m:
            i += 1
            continue
        indent, name, start = len(m.group(1)), m.group(3), i
        deco = []
        j = i - 1
        while j >= 0 and lines[j].strip().startswith("@"):
            deco.append(lines[j]); j -= 1
        k = i + 1
        while k < len(lines) and (not lines[k].strip() or len(lines[k]) - len(lines[k].lstrip()) > indent):
            k += 1
        body = lines[i + 1:k]
        skipped = any(re.search(r"skip|xfail", d) for d in deco) or any(re.search(r"pytest\.skip\(|self\.skipTest\(", b) for b in body)
        # decorators carry mocks and patches, so they count toward the smell scan
        yield name, start + 1, list(reversed(deco)) + body, skipped
        i = k


def brace_tests(lines, header):
    i = 0
    while i < len(lines):
        m = header.search(lines[i])
        if not m:
            i += 1
            continue
        name = m.group("name")
        depth, opened, k = 0, False, i
        while k < len(lines):
            depth += lines[k].count("{") - lines[k].count("}")
            opened = opened or "{" in lines[k]
            if opened and depth <= 0:
                break
            k += 1
        body = lines[i + 1:k]
        skipped = bool(m.groupdict().get("skip")) or any("t.Skip(" in b for b in body)
        yield name, i + 1, body, skipped
        i = k + 1


JS_HEAD = re.compile(r"^\s*(?P<skip>x)?(it|test)(?P<skip2>\.skip|\.todo)?(\.each\([^)]*\))?\s*\(\s*[`'\"](?P<name>[^`'\"]*)")
GO_HEAD = re.compile(r"^func\s+(?P<name>Test\w*)\s*\(")


def tests_in(path, ext):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    l = lang(ext)
    if l == "py":
        yield from py_tests(lines)
    elif l == "js":
        for name, line, body, skipped in brace_tests(lines, JS_HEAD):
            head = lines[line - 1]
            yield name, line, body, skipped or bool(re.search(r"^\s*x(it|test)\b|\.(skip|todo)\s*\(", head))
    elif l == "go":
        yield from brace_tests(lines, GO_HEAD)


def norm(body, mask):
    text = "\n".join(b.strip() for b in body if b.strip() and not b.strip().startswith(("#", "//")))
    if mask:
        text = LITERAL.sub("_", text)
    return hashlib.sha1(text.encode()).hexdigest() if text else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo")
    ap.add_argument("--scope", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        sys.exit(f"not a directory: {repo}")
    root = os.path.join(repo, a.scope.strip("/")) if a.scope else repo

    hits = defaultdict(list)
    exact, shape = defaultdict(list), defaultdict(list)
    total = 0
    for dirpath, fn in iter_files(root):
        ext = os.path.splitext(fn)[1]
        rel = os.path.relpath(os.path.join(dirpath, fn), repo).replace(os.sep, "/")
        l = lang(ext)
        if not l or not TEST_PATH.search(rel):
            continue
        for name, line, body, skipped in tests_in(os.path.join(repo, rel), ext):
            total += 1
            ref = {"file": rel, "line": line, "test": name}
            text = "\n".join(body)
            if skipped:
                hits["skipped"].append(ref)
            if body and not ASSERT[l].search(text):
                hits["no_assertion"].append(ref)
            if any(p.search(b) for p in TAUT for b in body):
                hits["tautological"].append(ref)
            mocks = len(MOCK.findall(text))
            if mocks >= 3:
                hits["mock_heavy"].append({**ref, "count": mocks})
            if CALLS.search(text):
                hits["call_count_assertion"].append(ref)
            if PRIVATE[l].search(text):
                hits["private_access"].append(ref)
            if SNAP.search(text):
                hits["snapshot"].append(ref)
            h1, h2 = norm(body, False), norm(body, True)
            if h1:
                exact[h1].append(ref)
            if h2:
                shape[h2].append(ref)

    dup = [g for g in exact.values() if len(g) > 1]
    dup_keys = {(r["file"], r["line"]) for g in dup for r in g}
    same = [g for g in shape.values() if len(g) > 2 and not all((r["file"], r["line"]) in dup_keys for r in g)]
    result = {"tests": total, "smells": {k: v for k, v in hits.items()},
              "duplicate_groups": dup, "same_shape_groups": same}
    if a.json:
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    print(f"# Test smell leads: {a.scope or '.'} in {repo}")
    print(f"{total} tests scanned. Every row is a lead to confirm by reading the test.")
    labels = {
        "no_assertion": "No assertion", "tautological": "Tautological assertion",
        "mock_heavy": "Mock-heavy (3+ mocks)", "call_count_assertion": "Asserts calls on a mock",
        "private_access": "Reaches or patches private members", "skipped": "Skipped", "snapshot": "Snapshot",
    }
    print("\n| Smell | Count |\n|---|---|")
    print(f"| Exact duplicate groups | {len(dup)} ({sum(len(g) for g in dup)} tests) |")
    print(f"| Same-shape groups (3+, literals differ) | {len(same)} ({sum(len(g) for g in same)} tests) |")
    for k, label in labels.items():
        print(f"| {label} | {len(hits.get(k, []))} |")
    for title, groups in (("Exact duplicates", dup), ("Same shape, different literals (parametrize candidates)", same)):
        if groups:
            print(f"\n## {title}")
            for g in groups:
                print("- " + ", ".join(f"{r['file']}:{r['line']} {r['test']}" for r in g))
    for k, label in labels.items():
        if hits.get(k):
            print(f"\n## {label}")
            for r in hits[k]:
                extra = f" ({r['count']} mocks)" if "count" in r else ""
                print(f"- {r['file']}:{r['line']} {r['test']}{extra}")


if __name__ == "__main__":
    main()
