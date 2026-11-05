#!/usr/bin/env python3
"""Leads on unfinished work and special cases: TODO clusters, stubs, commented-out
code, flags that are always off, unreferenced symbols, swallowed exceptions,
sleeps and retries, and branches on one literal value.

Usage: code_leads.py <repo> [--scope PATH] [--top N] [--json]

Heuristics for Python, JavaScript/TypeScript, Go and similar languages. Every
hit is a lead to confirm by reading the code, not a verdict: names can be used
dynamically (string lookups, reflection, config), so "unreferenced" means "no
literal mention found". Source files only; tests are skipped. Read-only;
standard library only.
"""
import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "out", "target", ".venv", "venv",
             "__pycache__", ".next", ".turbo", "coverage", ".mypy_cache", ".pytest_cache", ".idea", ".vscode"}
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rb", ".java", ".kt", ".swift",
            ".rs", ".cs", ".php", ".scala", ".c", ".cc", ".cpp", ".h", ".hpp", ".m", ".ex", ".exs", ".dart"}
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|specs)(/|$)|(^|/)test_[^/]+$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$")
HASH_COMMENT = {".py", ".rb", ".ex", ".exs"}

MARKER = re.compile(r"(?:#|//|/\*|\*|--)\s*(TODO|FIXME|HACK|XXX)\b[:(\s]?(.*)")
STUB = re.compile(
    r"raise\s+NotImplementedError|throw\s+new\s+Error\(\s*['\"`][^'\"`]*not\s+implemented"
    r"|panic\(\s*\"[^\"]*not\s+implemented|\bunimplemented!\(|\btodo!\(|NotImplementedException"
    r"|throw\s+new\s+UnsupportedOperationException", re.I)
PY_DEF = re.compile(r"^(\s*)(async\s+)?def\s+(\w+)\s*\(")
EXCEPT_PY = re.compile(r"^\s*except\b[^:]*:")
HANDLED = re.compile(r"\braise\b|\blog(ger|ging)?\.|\bprint\(|\bwarn(ings)?\b|\breport|\bsentry|\bre_raise|\breturn\s+(?!None\b)\S")
SWALLOW_C = re.compile(r"catch\s*(\([^)]*\))?\s*\{\s*(//[^\n]*)?\}|\.catch\(\s*\(\s*\w*\s*\)\s*=>\s*(\{\s*\}|null|undefined)\s*\)")
SLEEP = re.compile(r"\btime\.sleep\(|\bTime\.sleep\b|\btime\.Sleep\(|Thread\.sleep\(|\bsleep\(\s*\d|await\s+new\s+Promise\([^)]*setTimeout")
RETRY = re.compile(r"\b(retry|retries|attempts?|max_tries|backoff)\b", re.I)
ONE_VALUE = re.compile(r"\b(?:if|elif|else\s+if|case|when)\b[^\n]*?([\w.\[\]'\"]+)\s*(?:===?|!==?)\s*(['\"`])([^'\"`\n]{2,40})\2")
FLAG = re.compile(r"^\s*(?:export\s+)?(?:const\s+|let\s+|var\s+|final\s+|static\s+)*"
                  r"([A-Z][A-Z0-9_]*(?:ENABLE|ENABLED|FEATURE|FLAG|USE_|_ON\b|BETA|EXPERIMENT)[A-Z0-9_]*|"
                  r"(?:ENABLE|FEATURE|USE|FLAG)_[A-Z0-9_]+)\s*(?::\s*\w+\s*)?=\s*(False|false|0|None|null|nil|['\"]off['\"])\s*;?\s*(#.*|//.*)?$")
DEFN = [
    re.compile(r"^(?:async\s+)?def\s+([A-Za-z]\w*)\s*\("),                     # Python top-level
    re.compile(r"^class\s+([A-Za-z]\w*)\b"),                                     # Python, JS, TS
    re.compile(r"^export\s+(?:default\s+)?(?:async\s+)?function\s+([A-Za-z]\w*)"),
    re.compile(r"^(?:async\s+)?function\s+([A-Za-z]\w*)"),
    re.compile(r"^export\s+(?:const|let|class)\s+([A-Za-z]\w*)"),
    re.compile(r"^func\s+(?:\([^)]*\)\s*)?([A-Za-z]\w*)\s*\("),                # Go
]
ENTRY_NAMES = {"main", "init", "setup", "teardown", "handler", "default", "App", "index"}
CODEISH = re.compile(r"(\bdef\b|\breturn\b|\bimport\b|\bif\b.*:|\bfor\b.*:|[=;{}]|\w+\([^)]*\)\s*$)")


def iter_files(root):
    if os.path.isfile(root):
        yield os.path.dirname(root), os.path.basename(root)
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            yield dirpath, fn


def read(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data.decode("utf-8", "replace").splitlines()


def is_comment(line, ext):
    s = line.strip()
    if ext in HASH_COMMENT:
        return s.startswith("#") and not s.startswith("#!")
    return s.startswith("//")


def strip_comment(line, ext):
    s = line.strip()
    return s[1:].strip() if ext in HASH_COMMENT else s[2:].strip()


def py_handler(lines, i):
    """The statements of the except block starting at line i (inline body included)."""
    head = lines[i]
    inline = head.split(":", 1)[1].strip()
    body = [inline] if inline else []
    indent = len(head) - len(head.lstrip())
    k = i + 1
    while k < len(lines) and (not lines[k].strip() or len(lines[k]) - len(lines[k].lstrip()) > indent):
        if lines[k].strip():
            body.append(lines[k].strip())
        k += 1
    return body


def py_stubs(lines):
    """Python functions whose whole body is pass or ... (abstract methods excluded)."""
    out = []
    for i, line in enumerate(lines):
        m = PY_DEF.match(line)
        if not m:
            continue
        j = i - 1
        abstract = False
        while j >= 0 and lines[j].strip().startswith("@"):
            abstract |= "abstract" in lines[j] or "overload" in lines[j]
            j -= 1
        if abstract:
            continue
        indent = len(m.group(1))
        body = []
        k = i + 1
        while k < len(lines) and (not lines[k].strip() or len(lines[k]) - len(lines[k].lstrip()) > indent):
            s = lines[k].strip()
            if s and not s.startswith("#") and not s.startswith(('"""', "'''")):
                body.append(s)
            k += 1
        if body and all(b in ("pass", "...") for b in body):
            out.append((i + 1, m.group(3)))
    return out


def scan(rel, ext, lines, leads):
    # markers
    for i, line in enumerate(lines):
        m = MARKER.search(line)
        if m:
            leads["markers"][rel].append((i + 1, m.group(1), m.group(2).strip()[:80]))
    # stubs
    for i, line in enumerate(lines):
        if STUB.search(line):
            leads["stubs"].append({"file": rel, "line": i + 1, "text": line.strip()[:90]})
    if ext == ".py":
        for ln, name in py_stubs(lines):
            leads["stubs"].append({"file": rel, "line": ln, "text": f"def {name}(...): body is only pass/..."})
    # commented-out code: 3+ consecutive comment lines that read like code
    run = []
    for i, line in enumerate(lines + [""]):
        if is_comment(line, ext) and not MARKER.search(line):
            run.append(i)
            continue
        if len(run) >= 3:
            codeish = sum(1 for r in run if CODEISH.search(strip_comment(lines[r], ext)))
            if codeish * 2 >= len(run):
                leads["commented_out"].append({"file": rel, "start": run[0] + 1, "end": run[-1] + 1})
        run = []
    # special cases
    for i, line in enumerate(lines):
        s = line.strip()
        if ext == ".py" and EXCEPT_PY.match(line):
            body = py_handler(lines, i)
            if not any(HANDLED.search(b) for b in body):
                summary = "; ".join(b for b in body if not b.startswith("#"))[:60] or "(empty)"
                leads["swallowed"].append({"file": rel, "line": i + 1, "text": f"{s[:50]} → {summary}"})
        elif ext != ".py" and SWALLOW_C.search(line):
            leads["swallowed"].append({"file": rel, "line": i + 1, "text": s[:90]})
        if SLEEP.search(line):
            near = " ".join(lines[max(0, i - 8): i + 3])
            leads["sleeps"].append({"file": rel, "line": i + 1, "text": s[:90], "retry": bool(RETRY.search(near))})
        m = ONE_VALUE.search(line)
        if m and not s.startswith(("#", "//")) and "__name__" not in s:
            leads["one_value"].append({"file": rel, "line": i + 1, "subject": m.group(1), "value": m.group(3), "text": s[:90]})
        m = FLAG.match(line)
        if m:
            leads["flags"].append({"file": rel, "line": i + 1, "name": m.group(1), "value": m.group(2)})
    # top-level definitions, for the reference count
    for i, line in enumerate(lines):
        for pat in DEFN:
            m = pat.match(line)
            if m:
                leads["defs"].append((rel, i + 1, m.group(1)))
                break


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo")
    ap.add_argument("--scope", default="", help="only report findings under this path (references are counted repo-wide)")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        sys.exit(f"not a directory: {repo}")
    scope = ""
    if a.scope:
        rel_scope = os.path.relpath(os.path.join(repo, a.scope), repo).replace(os.sep, "/")
        if rel_scope.startswith(".."):
            sys.exit(f"--scope is outside the repo: {a.scope}")
        scope = "" if rel_scope == "." else rel_scope

    leads = {"markers": defaultdict(list), "stubs": [], "commented_out": [], "swallowed": [],
             "sleeps": [], "one_value": [], "flags": [], "defs": []}
    words = Counter()          # identifier mentions across all code, tests included
    test_words = Counter()     # mentions in test files only
    for dirpath, fn in iter_files(repo):
        ext = os.path.splitext(fn)[1]
        if ext not in CODE_EXT:
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, repo).replace(os.sep, "/")
        lines = read(full)
        if lines is None:
            continue
        test = bool(TEST_PATH.search(rel))
        toks = re.findall(r"[A-Za-z_]\w*", "\n".join(lines))
        words.update(toks)
        if test:
            test_words.update(toks)
        if not test and (not scope or rel == scope or rel.startswith(scope + "/")):
            scan(rel, ext, lines, leads)

    unreferenced, test_only = [], []
    for rel, ln, name in leads["defs"]:
        if name in ENTRY_NAMES or name.startswith("test"):
            continue
        total, in_tests = words[name], test_words[name]
        if total <= 1:
            unreferenced.append({"file": rel, "line": ln, "name": name})
        elif total - in_tests <= 1:
            test_only.append({"file": rel, "line": ln, "name": name, "test_mentions": in_tests})
    for f in leads["flags"]:
        f["mentions"] = words[f["name"]] - 1

    marker_files = sorted(({"file": f, "count": len(v), "items": v} for f, v in leads["markers"].items()),
                          key=lambda d: d["count"], reverse=True)
    # group by the last name in what is compared, so customer_id and invoice["customer_id"] land together
    for o in leads["one_value"]:
        o["key"] = (re.findall(r"\w+", o["subject"]) or [o["subject"]])[-1]
    by_key = Counter(o["key"] for o in leads["one_value"])
    by_value = Counter(o["value"] for o in leads["one_value"])
    one_value = sorted(leads["one_value"],
                       key=lambda o: (-max(by_key[o["key"]], by_value[o["value"]]), o["key"], o["file"], o["line"]))
    tools = [t for t in ("vulture", "knip", "ts-prune", "deadcode", "staticcheck") if shutil.which(t)]

    result = {
        "repo": repo, "scope": scope or ".",
        "markers": marker_files[: a.top],
        "marker_total": sum(d["count"] for d in marker_files),
        "stubs": leads["stubs"][: a.top],
        "commented_out": leads["commented_out"][: a.top],
        "flags_off": leads["flags"][: a.top],
        "unreferenced": unreferenced[: a.top],
        "test_only": test_only[: a.top],
        "swallowed": leads["swallowed"][: a.top],
        "sleeps": leads["sleeps"][: a.top],
        "one_value": one_value[: a.top],
        "dead_code_tools": tools,
    }
    if a.json:
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    p = print
    p(f"# Code leads: {result['scope']} in {repo}")
    p("Leads only. Confirm each in the code; dynamic use (string lookups, reflection, config, entry points) is not detected.")
    p("\n## Unfinished work")
    if marker_files:
        p(f"\nTODO/FIXME/HACK/XXX: {result['marker_total']} in {len(marker_files)} files\n| File | Count | First markers |\n|---|---|---|")
        for d in result["markers"]:
            first = "; ".join(f":{ln} {kind} {txt}".strip() for ln, kind, txt in d["items"][:3]).replace("|", "/")
            p(f"| {d['file']} | {d['count']} | {first} |")
    if result["stubs"]:
        p("\nStubs\n| File:line | Code |\n|---|---|")
        for s in result["stubs"]:
            p(f"| {s['file']}:{s['line']} | `{s['text'].replace('|', '/')}` |")
    if result["commented_out"]:
        p("\nCommented-out code\n| File | Lines |\n|---|---|")
        for c in result["commented_out"]:
            p(f"| {c['file']} | {c['start']}-{c['end']} |")
    if result["flags_off"]:
        p("\nFlags set off\n| File:line | Flag | Value | Other mentions |\n|---|---|---|---|")
        for f in result["flags_off"]:
            p(f"| {f['file']}:{f['line']} | {f['name']} | {f['value']} | {f['mentions']} |")
    if not (marker_files or result["stubs"] or result["commented_out"] or result["flags_off"]):
        p("\nNone found.")
    p("\n## Unreferenced code")
    if result["unreferenced"]:
        p("\nNo mention outside its definition\n| File:line | Name |\n|---|---|")
        for u in result["unreferenced"]:
            p(f"| {u['file']}:{u['line']} | {u['name']} |")
    if result["test_only"]:
        p("\nMentioned only by tests\n| File:line | Name | Test mentions |\n|---|---|---|")
        for u in result["test_only"]:
            p(f"| {u['file']}:{u['line']} | {u['name']} | {u['test_mentions']} |")
    if not (result["unreferenced"] or result["test_only"]):
        p("\nNone found.")
    if tools:
        p(f"\nInstalled dead-code tools you can run for a fuller list: {', '.join(tools)}")
    p("\n## Special cases (each one hints at a requirement the design does not model)")
    if result["one_value"]:
        p("\nBranches on one literal value (repeats first; the same value in several files is the strongest lead)\n| File:line | Compared | Value | Same value, places |\n|---|---|---|---|")
        for o in result["one_value"]:
            p(f"| {o['file']}:{o['line']} | {o['subject']} | {o['value']} | {by_value[o['value']]} |")
    if result["swallowed"]:
        p("\nSwallowed exceptions\n| File:line | Code |\n|---|---|")
        for s in result["swallowed"]:
            p(f"| {s['file']}:{s['line']} | `{s['text']}` |")
    if result["sleeps"]:
        p("\nSleeps\n| File:line | Near a retry | Code |\n|---|---|---|")
        for s in result["sleeps"]:
            p(f"| {s['file']}:{s['line']} | {'yes' if s['retry'] else 'no'} | `{s['text']}` |")
    if not (result["one_value"] or result["swallowed"] or result["sleeps"]):
        p("\nNone found.")


if __name__ == "__main__":
    main()
