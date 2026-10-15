#!/usr/bin/env python3
"""Structural checks for every skill in this repo.

Run from anywhere: python3 scripts/check_skills.py
Exits non-zero and lists each problem if any check fails.

Checks per skill folder (any top-level folder with a SKILL.md):
- frontmatter has name (matching the folder) and a description of at most 1024 chars
- SKILL.md body stays under 500 lines
- every references/ or scripts/ path named in SKILL.md exists
- every `/skill-name` mentioned in any .md file is a skill in this repo
- evals/evals.json parses, names the right skill, and every listed file, project folder and setup script exists
- files under scripts/ are executable
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []


def fail(msg):
    problems.append(msg)


skills = sorted(
    d for d in os.listdir(ROOT)
    if os.path.isfile(os.path.join(ROOT, d, "SKILL.md"))
)
if not skills:
    fail("no skills found")

for name in skills:
    sdir = os.path.join(ROOT, name)
    text = open(os.path.join(sdir, "SKILL.md"), encoding="utf-8").read()

    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        fail(f"{name}: SKILL.md has no frontmatter block")
        continue
    front, body = m.groups()
    fields = dict(
        line.split(":", 1) for line in front.splitlines() if ":" in line
    )
    if fields.get("name", "").strip() != name:
        fail(f"{name}: frontmatter name is {fields.get('name', '').strip()!r}")
    desc = fields.get("description", "").strip()
    if not desc:
        fail(f"{name}: missing description")
    elif len(desc) > 1024:
        fail(f"{name}: description is {len(desc)} chars (max 1024)")
    if body.count("\n") >= 500:
        fail(f"{name}: SKILL.md body is {body.count(chr(10))} lines (keep under 500)")

    for ref in sorted(set(re.findall(r"`((?:references|scripts)/[^`\s]+)", text))):
        if not os.path.exists(os.path.join(sdir, ref.split()[0])):
            fail(f"{name}: SKILL.md names {ref}, which does not exist")

    sdir_scripts = os.path.join(sdir, "scripts")
    if os.path.isdir(sdir_scripts):
        for f in os.listdir(sdir_scripts):
            p = os.path.join(sdir_scripts, f)
            if os.path.isfile(p) and not os.access(p, os.X_OK):
                fail(f"{name}: scripts/{f} is not executable")

    evals = os.path.join(sdir, "evals", "evals.json")
    if not os.path.isfile(evals):
        fail(f"{name}: no evals/evals.json")
        continue
    try:
        data = json.load(open(evals, encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{name}: evals.json does not parse: {e}")
        continue
    if data.get("skill_name") != name:
        fail(f"{name}: evals.json skill_name is {data.get('skill_name')!r}")
    ids = [e.get("id") for e in data.get("evals", [])]
    if len(ids) != len(set(ids)):
        fail(f"{name}: duplicate eval ids {ids}")
    for e in data.get("evals", []):
        if not e.get("prompt") or not e.get("expectations"):
            fail(f"{name}: eval {e.get('id')} needs a prompt and expectations")
        for f in e.get("files", []):
            if not os.path.exists(os.path.join(sdir, f)):
                fail(f"{name}: eval {e.get('id')} lists missing file {f}")
        project = e.get("project")
        if project and not os.path.isdir(os.path.join(sdir, project)):
            fail(f"{name}: eval {e.get('id')} names missing project folder {project}")
        setup = e.get("setup")
        if setup and not os.access(os.path.join(sdir, setup), os.X_OK):
            fail(f"{name}: eval {e.get('id')} setup script {setup} is missing or not executable")

# Slash references in prose must point at skills that exist here.
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if not d.startswith(".")]
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        path = os.path.join(dirpath, fn)
        for ref in set(re.findall(r"`/([a-z][a-z0-9-]+)`", open(path, encoding="utf-8").read())):
            if ref not in skills:
                fail(f"{os.path.relpath(path, ROOT)}: mentions /{ref}, which is not a skill in this repo")

if problems:
    print("FAIL")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
print(f"OK: {len(skills)} skills checked ({', '.join(skills)})")
