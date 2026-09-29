#!/usr/bin/env python3
"""Records bound to v2/ecad/tools/pcb_decisions.yaml rebound after integration set 13 added decision 58 (MESHSAT-1357, 29
September 2026; stream s119's drafted U3B for Option A(i)'s lid pack, applied by records/s119/apply_decision_s119.py). The file
is parsed at HEAD and in the tree: every decision HEAD holds must be present and identical, and exactly decision 58 added;
anything else refuses. Each bound record gets one evidence entry starting with the file's path, and its binding moves.
Refuses a second run. Run: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A

TAG = "apply_rebind_decisions_set13"
DEC = "v2/ecad/tools/pcb_decisions.yaml"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
REASON = {"CFL-016": "this record reads decisions 28 and 40, which are identical; decision 58 concerns a drafted lid charger "
                     "that no generator carries and no document this record names describes"}


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m)); sys.exit(2)


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    old_b = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + DEC], capture_output=True, check=True).stdout
    new_b = open(os.path.join(TOP, DEC), "rb").read()
    o16, n16 = hashlib.sha256(old_b).hexdigest()[:16], hashlib.sha256(new_b).hexdigest()[:16]
    if o16 == n16: refuse("the decisions file is HEAD's")
    def by_id(b):
        d = yaml.safe_load(b)
        rows = d["decisions"] if isinstance(d, dict) and "decisions" in d else d
        return {int(x["n"]): x for x in rows}   # the file numbers its decisions by `n`
    od, nd = by_id(old_b), by_id(new_b)
    if set(nd) - set(od) != {58} or set(od) - set(nd): refuse("added %s, removed %s" % (sorted(set(nd) - set(od)), sorted(set(od) - set(nd))))
    if any(od[k] != nd[k] for k in od): refuse("decisions changed: %s" % [k for k in od if od[k] != nd[k]])
    before = yaml.safe_load(reg)
    key = "%s@%s" % (DEC, o16)
    bound = sorted(r["id"] for r in before["records"] if key in (r.get("evidence_bound_to") or []))
    if bound != sorted(REASON): refuse("records bound to %s: %s" % (key, bound))
    out = reg
    for rid in bound:
        entry = ("%s re-read at integration set 13 (v2/docs/records/int14/apply_rebind_decisions_set13.py, %s to %s): parsed "
                 "against HEAD's file, every decision it holds is present and identical, and exactly one is added (58: stream "
                 "s119's U3B on U3's 400 kHz row, Option A(i)'s drafted lid charger); %s; rebound to %s. No result changes."
                 % (DEC, o16, n16, REASON[rid], n16))
        A.screen(entry, rid)
        i, j = A.span(out, rid)
        t = out[i:j]
        m = re.search(r"(?m)^    evidence:\n", t)
        tail = t[m.end():]
        k = re.search(r"(?m)^    [a-z_]+:", tail)
        end = m.end() + (k.start() if k else len(tail))
        t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
        if t.count(key) != 1: refuse("%s: the binding" % rid)
        t = t.replace(key, "%s@%s" % (DEC, n16))
        out = out[:i] + t + out[j:]
    after = yaml.safe_load(out)
    ob, ab = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        if (rid in bound and dd != {"evidence", "evidence_bound_to"}) or (rid not in bound and dd): refuse("%s: %s" % (rid, dd))
    if {k: v for k, v in before.items() if k != "records"} != {k: v for k, v in after.items() if k != "records"}: refuse("other sections moved")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("%s: %s rebound from %s to %s (decision 58 added, every other decision identical)" % (TAG, ", ".join(bound), o16, n16))
    return 0


if __name__ == "__main__":
    sys.exit(main())
