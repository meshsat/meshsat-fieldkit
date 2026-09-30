#!/usr/bin/env python3
"""File check 3 of layer 3's closure (MESHSAT-1357, 30 September 2026): Claude's verification of the final correction of
B2 (the coordinator's mechanical check and the targeted tests; not a model review and not an Astra check), appended to
l3r2.yaml's `independent_check` as ACCEPTED after the engineering collaborator's two checks (NOT_ACCEPTED). The record's
first line must read `accepted: yes` (the renderer verifies it, never trusts it). Applied once: a second run refuses.

Usage: python3 v2/docs/records/l3r5/apply_l3r5_check3.py (from the repository root)"""
import hashlib, os, sys
import yaml
sys.dont_write_bytecode = True
Y = "v2/docs/handover/layer3/l3r2.yaml"
REC = "v2/docs/records/l3r5/checks/check-l3r5-3.md"
TOOL = "v2/docs/records/l3r5/checks/verify_b2.py"
PREV = "v2/docs/records/l3r5/checks/astra-check-l3r5-2.md"
SCOPE = ("B2 of the engineering collaborator's check 2 (astra-check-l3r5-2, which accepted B1, B3 and M1), verified "
         "against that check's own closure criterion as the owner clarified it, at the verified revision a66c4e5b (B2 at "
         "9f3eab0b), with D-22's trace into REQ-072: Claude's (the coordinator's) verification by its own check "
         "verify_b2.py and the targeted tests, not a model review and not an Astra check; Astra never examined these revisions")


def refuse(m): print("apply_l3r5_check3: REFUSED: %s" % m); sys.exit(1)


def main():
    if not os.path.exists(Y): refuse("run from the repository root")
    for p in (REC, TOOL):
        if not os.path.exists(p): refuse("%s is not in the tree" % p)
    if open(REC, encoding="utf-8").readline().strip() != "accepted: yes": refuse("%s does not open with 'accepted: yes'" % REC)
    raw = open(Y, encoding="utf-8").read(); d = yaml.safe_load(raw)
    chks = d.get("independent_check") or []
    if any(c["record"] == REC for c in chks): refuse("check 3 is already filed: this script has run")
    if not chks or chks[-1]["record"] != PREV or chks[-1]["verdict"] != "NOT_ACCEPTED": refuse("the last filed check is not %s NOT_ACCEPTED" % PREV)
    sha = hashlib.sha256(open(REC, "rb").read()).hexdigest()[:16]
    for ch in ("\u2013", "\u2014"):
        if ch in SCOPE: refuse("a dash in the scope")
    line = '  - {record: %s, sha16: %s, verdict: ACCEPTED, scope: "%s"}\n' % (REC, sha, SCOPE)
    anchor = "\nbaseline_acceptance:"
    k = raw.index(anchor)
    if not raw[:k].rstrip("\n").split("\n")[-1].lstrip().startswith("- {record: %s" % PREV): refuse("the list does not end with check 2")
    new = raw[:k + 1] + line + raw[k + 1:]
    e = yaml.safe_load(new)
    if {k2: v for k2, v in e.items() if k2 != "independent_check"} != {k2: v for k2, v in d.items() if k2 != "independent_check"}: refuse("something besides independent_check changed")
    if e["independent_check"][:-1] != chks or e["independent_check"][-1] != {"record": REC, "sha16": sha, "verdict": "ACCEPTED", "scope": SCOPE}: refuse("the list is not the old list plus check 3")
    open(Y, "w", encoding="utf-8").write(new)
    if yaml.safe_load(open(Y, encoding="utf-8").read()) != e: refuse("the file written does not re-parse to what was checked")
    print("apply_l3r5_check3: check 3 filed ACCEPTED (%s, sha16 %s)" % (REC, sha))


if __name__ == "__main__":
    main()
