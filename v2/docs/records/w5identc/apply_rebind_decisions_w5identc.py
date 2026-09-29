#!/usr/bin/env python3
"""Records bound to v2/ecad/tools/pcb_decisions.yaml rebound after decision 59 (the DECODED binding of part identities,
stream w5identc, MESHSAT-1357, 29 September 2026) is appended by apply_decision_decoded.py. The pattern is
v2/docs/records/int14/apply_rebind_decisions_set13.py: the file is parsed at HEAD and in the tree, every decision HEAD
holds must be present and identical and exactly one decision added (the one whose title carries this stream's marker);
anything else refuses. Each bound record gets one evidence entry and its binding moves; the reason is computed, not
typed: the decisions the record names in `satisfied_by` are asserted identical in both files. No result changes.
Refuses a second run. Run after apply_decision_decoded.py (it calls `rebind` itself): python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A   # noqa: E402  (screen, span, fold: the integrator's own helpers)

TAG = "apply_rebind_decisions_w5identc"
DEC = "v2/ecad/tools/pcb_decisions.yaml"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
MARKER = "(stream w5identc)"


def refuse(m):
    raise SystemExit("%s: REFUSED: %s" % (TAG, m))


def by_n(b):
    d = yaml.safe_load(b)
    return {int(x["n"]): x for x in d["decisions"]}


def rebind(reg, old_b, new_b):
    """The requirements registry's text with every record bound to HEAD's decisions file rebound to the new one."""
    if TAG in reg: refuse("already applied")
    o16, n16 = hashlib.sha256(old_b).hexdigest()[:16], hashlib.sha256(new_b).hexdigest()[:16]
    if o16 == n16: refuse("the decisions file is HEAD's")
    od, nd = by_n(old_b), by_n(new_b)
    added = sorted(set(nd) - set(od))
    if len(added) != 1 or set(od) - set(nd): refuse("added %s, removed %s" % (added, sorted(set(od) - set(nd))))
    n = added[0]
    if MARKER not in " ".join(str(nd[n].get("title", "")).split()): refuse("decision %d is not this stream's" % n)
    if any(od[k] != nd[k] for k in od): refuse("decisions changed: %s" % [k for k in od if od[k] != nd[k]])
    before = yaml.safe_load(reg)
    key = "%s@%s" % (DEC, o16)
    bound = sorted(r["id"] for r in before["records"] if key in (r.get("evidence_bound_to") or []))
    if not bound: refuse("no record is bound to %s" % key)
    out = reg
    for rid in bound:
        rec = next(r for r in before["records"] if r["id"] == rid)
        named = sorted(int(x) for x in ((rec.get("satisfied_by") or {}).get("decisions") or []))
        if any(od.get(k) != nd.get(k) or k not in od for k in named): refuse("%s names a decision that moved" % rid)
        reason = ("the decisions this record names in satisfied_by (%s) are identical in both files, parsed" % ", ".join(str(k) for k in named)
                  if named else "this record names no decision in satisfied_by")
        entry = ("%s re-read after decision %d was appended (v2/docs/records/w5identc/%s.py, %s to %s): parsed against HEAD's "
                 "file, every decision it holds is present and identical, and exactly one is added (%d: a part identity may be "
                 "RESOLVED on the maker's ordering-code table, a DECODED binding counted apart from PRINTED, stream w5identc); "
                 "%s; rebound to %s. No result changes." % (DEC, n, TAG, o16, n16, n, reason, n16))
        A.screen(entry, rid)
        i, j = A.span(out, rid)
        t = out[i:j]
        m = re.search(r"(?m)^    evidence:\n", t)
        if not m: refuse("%s has no evidence list" % rid)
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
    return out, bound, o16, n16


def main():
    reg = open(REG, encoding="utf-8").read()
    old_b = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + DEC], capture_output=True, check=True).stdout
    new_b = open(os.path.join(TOP, DEC), "rb").read()
    out, bound, o16, n16 = rebind(reg, old_b, new_b)
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != yaml.safe_load(out): refuse("re-parse differs")
    print("%s: %s rebound from %s to %s" % (TAG, ", ".join(bound), o16, n16))
    return 0


if __name__ == "__main__":
    sys.exit(main())
