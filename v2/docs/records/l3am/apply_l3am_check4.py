#!/usr/bin/env python3
"""File the Layer 3 amendment's check 4 (check-l3am-4: Claude's re-verification after the supersede test of test_l3am.py
was corrected at 8146b4cc; not a model review and not an Astra check) as the newest entry of l3r2.yaml's
`independent_check`, ACCEPTED (MESHSAT-1357, 1 October 2026). Check 3 held only while the amendment's files were
unchanged since cd231260; a corrected test changed one of them, so the closing check is re-issued for the revision that
holds it. The record's three header lines are verified first (the format apply_l3am_findings_closed.py requires); a second
run is refused; nothing outside independent_check changes. Then apply_l3am_findings_rechecked.py names it as the check
that closed the findings. Usage: python3 v2/docs/records/l3am/apply_l3am_check4.py (from the repository root)"""
import hashlib, os, sys
import yaml
sys.dont_write_bytecode = True
Y = "v2/docs/handover/layer3/l3r2.yaml"
REC = "v2/docs/records/l3am/checks/check-l3am-4.md"
SCOPE = ("the Layer 3 amendment l3am (L3-R01 to L3-R05) at 8146b4cc, check 3's amendment with the supersede test's expected "
         "history corrected: verify_l3am.py 16 of 16 and the diff since cd231260 read by Claude (the coordinator); not a "
         "model review and not an Astra check")


def refuse(m): print("apply_l3am_check4: REFUSED: %s" % m); sys.exit(1)


def main():
    if not os.path.exists(Y): refuse("run from the repository root")
    lines = open(REC, encoding="utf-8").read().split("\n")
    if lines[0] != "accepted: yes" or lines[1] != "scope: Layer 3 amendment l3am (L3-R01 to L3-R05)" or not lines[2].startswith("reviewed-revision: "):
        refuse("%s does not carry the three header lines exactly" % REC)
    raw = open(Y, encoding="utf-8").read(); d = yaml.safe_load(raw)
    chks = d.get("independent_check") or []
    if any(c["record"] == REC for c in chks): refuse("check-l3am-4 is already filed: this script has run")
    last = chks[-1]["record"]
    if last != "v2/docs/records/l3am/checks/check-l3am-3.md": refuse("the newest check is %s, not check-l3am-3" % last)
    L = raw.split("\n")
    k = max(i for i, l in enumerate(L) if l.startswith("  - {record: %s" % last))
    sha = hashlib.sha256(open(REC, "rb").read()).hexdigest()[:16]
    for ch in ("\u2013", "\u2014"):
        if ch in SCOPE: refuse("a dash in the scope")
    L.insert(k + 1, '  - {record: %s, sha16: %s, verdict: ACCEPTED, scope: "%s"}' % (REC, sha, SCOPE))
    new = "\n".join(L); e = yaml.safe_load(new)
    if {a: b for a, b in e.items() if a != "independent_check"} != {a: b for a, b in d.items() if a != "independent_check"}: refuse("something besides independent_check changed")
    if e["independent_check"][:-1] != chks or e["independent_check"][-1]["record"] != REC: refuse("the list is not the old list plus check-l3am-4 last")
    open(Y, "w", encoding="utf-8").write(new)
    if yaml.safe_load(open(Y, encoding="utf-8").read()) != e: refuse("the file written does not re-parse to what was checked")
    print("apply_l3am_check4: check-l3am-4 filed ACCEPTED (sha16 %s)" % sha)


if __name__ == "__main__":
    main()
