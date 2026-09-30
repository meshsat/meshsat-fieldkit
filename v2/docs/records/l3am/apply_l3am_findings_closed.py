#!/usr/bin/env python3
"""The coordinator's step after the layer 3 amendment is checked (MESHSAT-1357; v2/docs/records/l3am/README.md): close
l3r2.yaml's `review_findings` once the amendment's independent check is filed as the newest `independent_check` and reads
ACCEPTED. It sets `state: CLOSED`, names the check (`checked_by`) and restates `status` as dispositioned and checked; the
baseline is then accepted again at the revision that holds it (apply_l3r5_accept.py --supersede), which refuses while the
state is OPEN. Nothing else changes; it refuses unless the named record is the newest check, filed, ACCEPTED and verified
by the renderer, and a second run is refused. Not run by the amendment's author.

Usage: python3 v2/docs/records/l3am/apply_l3am_findings_closed.py --check-record <path> [--check] [--data PATH]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402

sys.path.insert(0, os.path.join(L.TOP, "v2", "docs", "handover", "layer3"))


def build(raw, record):
    import render_l3r2 as RL
    d = L.E.parse(raw)
    rf = d.get("review_findings")
    if not rf: L.refuse("review_findings is not filed: apply_l3am_findings.py comes first")
    if str(rf.get("state")) != "OPEN": L.refuse("review_findings reads %s: this script has run" % rf.get("state"))
    chks = RL.handover_checks(d)
    if not chks or str(chks[-1]["record"]) != record or str(chks[-1].get("verdict")).upper() != "ACCEPTED":
        L.refuse("%s is not the newest independent check, filed and ACCEPTED" % record)
    lines = [l for l in raw.split("\n") if l.startswith("review_findings: {")]
    if len(lines) != 1: L.refuse("review_findings is not one flow line")
    old_tail = ", state: OPEN, status: \"%s\"}" % rf["status"]
    status = "Layer 3 amendment checked; independent review findings dispositioned (L3-R01 to L3-R05)"
    new_line = L.once(lines[0], old_tail, ", state: CLOSED, checked_by: %s, status: \"%s\"}" % (record, status), "review_findings")
    new = L.once(raw, lines[0] + "\n", new_line + "\n", "l3r2.yaml")
    a, b = L.only_keys_changed(raw, new, {"review_findings": "changed"})
    ch = sorted(k for k in set(a["review_findings"]) | set(b["review_findings"]) if a["review_findings"].get(k) != b["review_findings"].get(k))
    if ch != ["checked_by", "state", "status"]: L.refuse("review_findings changed on %s" % ch)
    return new


def main(argv):
    path = argv[argv.index("--data") + 1] if "--data" in argv else L.DATA
    rec = argv[argv.index("--check-record") + 1] if "--check-record" in argv else None
    old = open(path, encoding="utf-8").read()
    try:
        if not rec: L.refuse("no --check-record named")
        new = build(old, rec)
    except L.Refused as e:
        print("apply_l3am_findings_closed: REFUSED: %s" % e); return 2
    print("apply_l3am_findings_closed: review_findings CLOSED, checked by %s%s" % (rec, " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv: L.write(path, old, new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
