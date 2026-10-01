#!/usr/bin/env python3
"""The layer 3 amendment's first step (MESHSAT-1357, 1 October 2026): file the independent review the owner relayed as
l3r2.yaml's `review_findings` (its copy REVIEW-AS-RECEIVED.md at its sha256/16, findings L3-R01 to L3-R05, state OPEN, and
the status wording the review asks for until the amendment is checked: "Layer 3 accepted baseline; independent review
findings open"), and state in the VALIDATED status level's `holds_when` that the acceptance binds the reviewed content
(L3-R04). The renderer prints both on REQUIREMENTS-L3-R2.md and OWNER-DECISIONS-L3.md; apply_l3r5_accept.py refuses while
the findings are OPEN. Nothing else changes; a second run is refused.

Usage: python3 v2/docs/records/l3am/apply_l3am_findings.py [--check]"""
import hashlib
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402

VALIDATED_OLD = ("and the baseline's acceptance filed against the verified revision after the gates pass (l3r2.yaml "
                 "baseline_acceptance, apply_l3r5_accept.py)\"}")
VALIDATED_NEW = ("and the baseline's acceptance filed against the verified revision after the gates pass (l3r2.yaml "
                 "baseline_acceptance, apply_l3r5_accept.py), its content manifest matching both that revision and the "
                 "tree (render_l3r2.acceptance_ok, L3-R04 of the independent review of 1 October 2026)\"}")
STATUS = "Layer 3 accepted baseline; independent review findings open (L3-R01 to L3-R05)"


def build(raw):
    d = L.E.parse(raw)
    if d.get("review_findings"): L.refuse("review_findings is filed: this script has run")
    fp = os.path.join(L.TOP, L.REVIEW)
    if not os.path.isfile(fp): L.refuse("%s is not filed" % L.REVIEW)
    b = open(fp, "rb").read()
    if not b.startswith(b"<!-- ABRIDGED by the coordinating session (1 October 2026)."):
        L.refuse("%s does not open with the coordinator's abridgement note" % L.REVIEW)
    for w in (b"L3-R01", b"L3-R02", b"L3-R03", b"L3-R04", b"L3-R05", b"independent review findings open"):
        if w not in b: L.refuse("%s does not read %r" % (L.REVIEW, w.decode()))
    sha = hashlib.sha256(b).hexdigest()[:16]
    block = ("# The independent review the owner relayed on 1 October 2026 (the layer 3 amendment, v2/docs/records/l3am/): the\n"
             "# status wording it asks for until the amendment is checked, the findings and their dispositions. The acceptance\n"
             "# script refuses while the state is OPEN; the coordinator closes it after the amendment's check is filed.\n"
             "review_findings: {review: %s, sha16: %s, relayed_on: \"%s\", relayed_on_text: \"%s\", findings: [L3-R01, L3-R02, "
             "L3-R03, L3-R04, L3-R05], carried: \"the engineering collaborator's layer 4 check of 30 September 2026 on the "
             "inherited unserved counter\", dispositions: %s, state: OPEN, status: \"%s\"}\n" % (
                 L.REVIEW, sha, L.RELAYED_ON, L.RELAYED_ON_TEXT, L.DISPOSITIONS, STATUS))
    # after the acceptance record, so that independent_check stays the list directly before it (the tests' fixtures
    # append a check there)
    new = L.insert_after_line(raw, "baseline_acceptance:", block, "l3r2.yaml")
    new = L.once(new, VALIDATED_OLD, VALIDATED_NEW, "the VALIDATED level's holds_when")
    a, b2 = L.only_keys_changed(raw, new, {"review_findings": "added", "status_levels": "changed"})
    ch = [x["id"] for x, y in zip(a["status_levels"], b2["status_levels"]) if x != y]
    if ch != ["VALIDATED"]: L.refuse("the status levels changed are %s, not VALIDATED" % ch)
    va = next(x for x in a["status_levels"] if x["id"] == "VALIDATED")
    vb = next(x for x in b2["status_levels"] if x["id"] == "VALIDATED")
    if [k for k in set(va) | set(vb) if va.get(k) != vb.get(k)] != ["holds_when"]: L.refuse("VALIDATED changed beyond holds_when")
    rf = b2["review_findings"]
    if rf["state"] != "OPEN" or rf["status"] != STATUS or rf["sha16"] != sha: L.refuse("review_findings does not read back")
    L.screen(block + VALIDATED_NEW, "the review findings")
    return new


def main(argv):
    old = open(L.DATA, encoding="utf-8").read()
    try:
        new = build(old)
    except L.Refused as e:
        print("apply_l3am_findings: REFUSED: %s" % e); return 2
    print("apply_l3am_findings: review_findings filed (OPEN), VALIDATED's holds_when names the content binding%s" % (
        " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv: L.write(L.DATA, old, new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
