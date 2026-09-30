#!/usr/bin/env python3
"""The coordinator's own check of B2 (MESHSAT-1357, 30 September 2026), written independently of the author's tests.
Criterion: the engineering collaborator's closure criterion for B2 (its targeted recheck, run 20260930T180749Z-114694):
"The source and generated change/impact rows consistently describe REQ-072 under D-32/D-35/D-37. No deployment band,
ground slope or push appears as an applied operating requirement; retained historical passages identify D-35 in place",
applied to every decided row, and read as the owner clarified it the same evening: "Historical descriptions of rejected
lid options may remain. An entry passes only when its current status accurately reflects the applicable ruling. Merely
mentioning D-33 must not excuse contradictory current text or an option still presented as awaiting a decision."

Units: every `impacts` entry's why and every `execution_plan_questions` note in l3r2.yaml; in REQUIREMENTS-L3-R2.md the
change table's rows (6.1) and the downstream table's rows (section 7); in L3-RECONCILIATION.md the execution-question
rows. Rules, each independent of whether the unit cites a ruling:
  R1 a unit saying "row L3-ODn answered X (D-nn)" names the row's decided option X and its deciding ruling;
  R2 split at ";", a clause carrying a phrase of an option the row's ruling did not take carries a history marker in the
     same clause ("not taken", "not adopted", "not added", "not applied", "superseded", or the denial "no ... is a
     requirement");
  R3 no downstream row renders "(if decided)" (every row is decided, or closed as layer 4 architecture);
  R4 an execution question of a decided row states its current status as "superseded by <the row's ruling>"; only
     that status clause is judged by R1 and R2 (the question before it is the plan's, history).
Usage: verify_b2.py <worktree> [--fixture]. --fixture also runs two contradictory copies (in memory) that must fail.
It writes nothing."""
import copy, os, re, sys
import yaml
WT = sys.argv[1]
H = os.path.join(WT, "v2/docs/handover/layer3")
DECIDED = {"L3-OD2": ("both-kept", "D-33"), "L3-OD3": ("unchanged", "D-34"), "L3-OD4": ("reject", "D-35"),
           "L3-OD5": ("layer4-obligation", "D-36"), "L3-OD6": ("mean-day", "D-37"), "L3-OD7": ("objective-48-72", "D-32")}
# phrases of the options each row's ruling did NOT take (from the rows' prepared restatements)
UNTAKEN = {
    "L3-OD2": ["qmx-out", "qmx-outside", "tablet-out", "QMX out", "tablet out", "no HF bearer", "HF leaves the kit",
               "HF bearer removed", "tablet bracket leaves the lid", "narrows to 8 inch", "QMX clause is removed"],
    "L3-OD3": ["1S4P", "200 W in 2S2P", "REQ-016 restated", "100 W window kept"],
    "L3-OD4": ["deployment band", "plane band", "band's least-energy plane", "ground slope", "operator push",
               "slope and push", "push are added"],
    "L3-OD5": ["reading-c", "reading of D-02a", "without its cells", "without the cells", "cells rated above +60 C"],
    "L3-OD6": ["coverage target", "coverage window"],
    "L3-OD7": ["72-required", "72 hours required", "mandatory 72", "48-required"],
}
# history markers, and one explicit denial form ("no X ... is a requirement"), which states the ruling's outcome;
# an untaken option's own content ("no HF bearer in the kit") does not match it
MARK = re.compile(r"\bnot (taken|adopted)\b|\bnot added\b|\bnot applied\b|\bsuperseded\b|\bno\b[^;]*\bis a requirement\b", re.I)
ANS = re.compile(r"\brow (L3-OD\d) answered ([\w-]+) \((D-\d+)\)")


def judge(where, text, bad, question=False):
    text = " ".join(str(text).split())
    if question:
        # an execution question's note is the plan's question (history) and then its current status, introduced by
        # "superseded by D-nn" naming the row's ruling; the status clause is what is judged (R1 and R2)
        m = re.search(r"\| (L3-OD\d)\b", text) or re.search(r"^(L3-OD\d)\b", text)
        row = m.group(1) if m else None
        k = text.find("superseded by ")
        if row in DECIDED:
            if k < 0 or not text[k:].startswith("superseded by %s" % DECIDED[row][1]):
                bad.append("R4 %s: no current status \"superseded by %s\"" % (where, DECIDED[row][1])); return
            text = text[k + len("superseded by "):]
        else: return
    for m in ANS.finditer(text):
        r, opt, rid = m.groups()
        if r in DECIDED and (opt, rid) != DECIDED[r]:
            bad.append("R1 %s: row %s answered %s (%s), decided %s (%s)" % (where, r, opt, rid, *DECIDED[r]))
    for cl in re.split(r";\s*", text):
        if MARK.search(cl): continue
        for r, phrases in UNTAKEN.items():
            hit = [p for p in phrases if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(p), cl)]
            if hit: bad.append("R2 %s: current clause carries %s of row %s: %s" % (where, hit, r, cl[:140]))


def units(data, req_md, rec_md):
    u = []
    for rid, e in (data.get("impacts") or {}).items():
        u.append(("l3r2.yaml impacts.%s" % rid, e.get("why") if isinstance(e, dict) else e))
    for q in data.get("execution_plan_questions") or []: u.append(("l3r2.yaml question %s" % q.get("q"), "%s %s" % (q.get("row"), q.get("note"))))
    lines = req_md.split("\n")
    a = next(i for i, l in enumerate(lines) if l.startswith("### 6.1"))
    b = next(i for i, l in enumerate(lines) if l.startswith("## 8."))
    for n in range(a, b):
        l = lines[n]
        if l.startswith("| ") and not l.startswith(("| Record", "| Layer")): u.append(("REQUIREMENTS-L3-R2.md:%d" % (n + 1), l))
    for n, l in enumerate(rec_md.split("\n"), 1):
        if re.match(r"\| Q\d \|", l): u.append(("L3-RECONCILIATION.md:%d" % n, l))
    return u


def run(data, req_md, rec_md):
    bad = []
    for where, text in units(data, req_md, rec_md): judge(where, text, bad, question=(" question " in where or "RECONCILIATION" in where))
    for n, l in enumerate(req_md.split("\n"), 1):
        if "(if decided)" in l: bad.append("R3 REQUIREMENTS-L3-R2.md:%d renders (if decided): %s" % (n, l[:120]))
    return bad


data = yaml.safe_load(open(os.path.join(H, "l3r2.yaml"), encoding="utf-8"))
req_md = open(os.path.join(H, "REQUIREMENTS-L3-R2.md"), encoding="utf-8").read()
rec_md = open(os.path.join(H, "L3-RECONCILIATION.md"), encoding="utf-8").read()
bad = run(data, req_md, rec_md)
print("units %d; FINDINGS %d" % (len(units(data, req_md, rec_md)), len(bad)))
for x in bad: print("  " + x)
rc = 1 if bad else 0
if "--fixture" in sys.argv:
    for name, why in (("contradictory current text citing D-33",
                       "row L3-OD2 answered both-kept (D-33): no HF bearer in the kit, REQ-002 restated; qmx-outside's note was not taken"),
                      ("wrong answered option citing D-33",
                       "row L3-OD2 answered qmx-out (D-33): the HF bearer removed; qmx-outside's note was not taken"),
                      ("history kept in a marked clause (must pass)",
                       "row L3-OD2 answered both-kept (D-33): the HF bearer kept, REQ-002 unchanged; the prepared restatements of qmx-out (no HF bearer in the kit) and qmx-outside (a note only) were not taken")):
        d2 = copy.deepcopy(data); d2["impacts"]["REQ-002"] = dict(d2["impacts"]["REQ-002"], why=why)
        got = [x for x in run(d2, req_md, rec_md) if "impacts.REQ-002" in x]
        want_fail = "must pass" not in name
        ok = bool(got) == want_fail
        print("fixture %-48s %s (%d finding(s) on REQ-002)" % (name, "OK" if ok else "WRONG", len(got)))
        rc |= 0 if ok else 1
sys.exit(rc)
