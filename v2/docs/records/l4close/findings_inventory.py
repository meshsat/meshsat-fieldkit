#!/usr/bin/env python3
"""Layer 4's findings inventory (MESHSAT-1357, 2 October 2026; v2/docs/records/l4close/).

Reads every check the engineering collaborator (Astra) filed for the Layer 4 tasks L4-E7, L4-E7Q, L4-E7R, L4-E8, L4-E9,
L4-E10, L4-E11, L4-E12 and L4-E13 (`<task>/checks/astra-check-*.md`) and prints its blocking items: the file, the item's
ID and the item's first 120 characters. FINDINGS-LEDGER.md beside this script has one row per item printed here, and
`v2/ecad/tools/tests/test_l4close.py` holds the two together.

How a check file is read (the launcher files them in one form):
- the first line is the filed verdict, "accepted: yes" or "accepted: no";
- the header names the job ("Collaborator job `...`"), the run ("run `...`") and the revision read ("at commit `...`");
- the section "## Blocking discrepancies" lists the blocking items as bullets "- <ID>: <text>", or "- none";
- an item's ID is the text before its first ": " (for example "B1", "B6, R5/R6", "R3, usable energy"). Within one file the
  IDs are distinct; the script refuses a file where two items share one.

Read-only and stdlib only; it writes nothing. Run from anywhere:
    python3 v2/docs/records/l4close/findings_inventory.py
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDS = os.path.dirname(HERE)
TASKS = ("l4e7", "l4e8", "l4e9", "l4e10", "l4e11", "l4e12", "l4e13")
NAME = re.compile(r"^astra-check-l4e(7|7q|7r|8|9|10|11|12|13)-([0-9]+)\.md$")
JOB = re.compile(r"Collaborator job `([^`]+)`")
RUN = re.compile(r"\brun `([^`]+)`")
REV = re.compile(r"at commit `([0-9a-f]+)`")


def check_files():
    """Every Astra check file of the tasks in scope, in task order, then by name."""
    out = []
    for task in TASKS:
        for path in sorted(glob.glob(os.path.join(RECORDS, task, "checks", "astra-check-*.md"))):
            if NAME.match(os.path.basename(path)):
                out.append(path)
    return out


def parse(path):
    """The file's verdict line, its job, run and revision, and its blocking items as (ID, full text) pairs."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    verdict = lines[0].strip() if lines else ""
    if verdict not in ("accepted: yes", "accepted: no"):
        raise ValueError("%s: the first line is not a filed verdict: %r" % (path, verdict))
    meta = {}
    for key, rx in (("job", JOB), ("run", RUN), ("revision", REV)):
        m = rx.search(text)
        meta[key] = m.group(1) if m else ""
    bullets, inside = [], False
    for ln in lines[1:]:
        if ln.startswith("## "):
            inside = ln.strip() == "## Blocking discrepancies"
            continue
        if not inside:
            continue
        if ln.startswith("- "):
            bullets.append(ln[2:].strip())
        elif ln.strip() and bullets:
            bullets[-1] += " " + ln.strip()
    items, seen = [], set()
    for b in bullets:
        if b.lower().rstrip(".") == "none":
            continue
        ident, sep, _rest = b.partition(": ")
        ident = ident.strip()
        if not sep or not ident:
            raise ValueError("%s: a blocking item without an ID: %r" % (path, b[:80]))
        if ident in seen:
            raise ValueError("%s: two blocking items share the ID %r" % (path, ident))
        seen.add(ident)
        items.append((ident, b))
    return verdict, meta, items


def inventory():
    """[(file name, verdict, meta, [(ID, text), ...]), ...] for every check file in scope."""
    return [(os.path.basename(p),) + parse(p) for p in check_files()]


def main():
    total = 0
    for name, verdict, meta, items in inventory():
        print("%s | %s | job %s | run %s | read %s | %d blocking" % (
            name, verdict, meta["job"], meta["run"], meta["revision"], len(items)))
        for ident, text in items:
            print("  %s | %s | %s" % (name, ident, text[:120]))
        total += len(items)
    print("blocking items: %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
