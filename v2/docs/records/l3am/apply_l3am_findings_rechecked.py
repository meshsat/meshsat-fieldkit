#!/usr/bin/env python3
"""Name a re-issued check of the Layer 3 amendment as the check that closed the review findings (MESHSAT-1357, 1 October
2026). apply_l3am_findings_closed.py closes OPEN findings once and refuses a second run; when a later, legitimate change
to an amendment file (here the supersede test's expected history, 8146b4cc) makes the closing check stop verifying, the
findings stay CLOSED only if a new check of the amendment verifies in its place. This script changes `checked_by` and
nothing else, and only after apply_l3am_findings_closed.verify accepts the new record (the newest independent check,
ACCEPTED, its three header lines exact, its reviewed revision the tip or an ancestor, the amendment unchanged since, not a
pre-amendment check), and only when the old closing check no longer verifies (otherwise there is nothing to replace).

Usage: python3 v2/docs/records/l3am/apply_l3am_findings_rechecked.py --check-record <path> [--check] [--data PATH] [--head REV]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402
import apply_l3am_findings_closed as FC  # noqa: E402


def build(raw, record, head="HEAD", allow_abs=False):
    d = L.E.parse(raw)
    rf = d.get("review_findings") or {}
    if str(rf.get("state")) != "CLOSED": L.refuse("review_findings reads %s: apply_l3am_findings_closed.py closes it" % rf.get("state"))
    old = str(rf.get("checked_by") or "")
    if old == record: L.refuse("review_findings is already checked by %s: this script has run" % record)
    try:
        FC.verify(old, {k: v for k, v in d.items() if k != "independent_check"} | {"independent_check": [
            c for c in d.get("independent_check") or [] if str(c.get("record")) != record]}, head, allow_abs=allow_abs)
    except L.Refused:
        pass
    else:
        L.refuse("the closing check %s still verifies: nothing to replace" % old)
    FC.verify(record, d, head, allow_abs=allow_abs)
    lines = [l for l in raw.split("\n") if l.startswith("review_findings: {")]
    if len(lines) != 1: L.refuse("review_findings is not one flow line")
    new_line = L.once(lines[0], ", checked_by: %s," % old, ", checked_by: %s," % record, "review_findings")
    new = L.once(raw, lines[0] + "\n", new_line + "\n", "l3r2.yaml")
    a, b = L.only_keys_changed(raw, new, {"review_findings": "changed"})
    ch = sorted(k for k in set(a["review_findings"]) | set(b["review_findings"]) if a["review_findings"].get(k) != b["review_findings"].get(k))
    if ch != ["checked_by"]: L.refuse("review_findings changed on %s" % ch)
    return new


def main(argv):
    path = argv[argv.index("--data") + 1] if "--data" in argv else L.DATA
    rec = argv[argv.index("--check-record") + 1] if "--check-record" in argv else None
    head = argv[argv.index("--head") + 1] if "--head" in argv else "HEAD"
    old = open(path, encoding="utf-8").read()
    try:
        if not rec: L.refuse("no --check-record named")
        new = build(old, rec, head, allow_abs=os.path.realpath(path) != os.path.realpath(L.DATA))
    except L.Refused as e:
        print("apply_l3am_findings_rechecked: REFUSED: %s" % e); return 2
    print("apply_l3am_findings_rechecked: review_findings checked by %s%s" % (rec, " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv: L.write(path, old, new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
