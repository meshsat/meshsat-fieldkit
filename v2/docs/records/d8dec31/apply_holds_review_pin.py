#!/usr/bin/env python3
"""Pin the review of decision 31 into the three holds (MESHSAT-1357, worker d8dec31, 28 September 2026).

The holds of boards A, D and E in v2/ecad/tools/pcb_board_holds.yaml (the integrator's file) each carry a
`layout_entry_requires` entry of kind `review` with `sha256: null` and `netlist_sha16: null`. This script writes the
sha256 of v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md as it stands in the tree, and for each board the first
sixteen hex digits of the sha256 of the netlist the review read, which it refuses to do unless the netlist in the
tree is that netlist (a review pinned to a netlist it never read would be a false record). It asserts the old text
(three identical null blocks, in the order a, d, e), asserts the new text differs, re-parses the file, and refuses a
second run.

THIS PINS A RECORD, NOT A VERDICT. rules_status reads the pinned review as "met" for the hold's review requirement;
the review's own findings (A-F2, D-F1, E-F1, E-F2, E-F3 and the rest) stay open in the requirements registry
(apply_registry_d31.py) and the hold's other two requirements stand on their own. A circuit change moves the netlist
and the pin then reads "re-review it", which is the rule's own text.

Usage: apply_holds_review_pin.py <tree root> [--check]
"""
import hashlib, os, sys

import yaml

REVIEW = "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"
NETLISTS = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
            "e": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"}
READ = {"a": "0a2b59087bcc2678", "d": "7a2c0ac2190b141a", "e": "56adc9746d61c4e0"}     # what the review read
NULL = ('       document: "%s"\n       sha256: null\n       netlist_sha16: null\n' % REVIEW)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry = os.path.abspath(argv[0]), "--check" in argv
    holds = os.path.join(root, "v2", "ecad", "tools", "pcb_board_holds.yaml")
    old = open(holds, encoding="utf-8").read()
    if old.count(NULL) != 3:
        raise SystemExit("apply_holds_review_pin: expected three unpinned review blocks, found %d (already applied, or the file moved)" % old.count(NULL))
    rp = os.path.join(root, REVIEW)
    if not os.path.exists(rp):
        raise SystemExit("apply_holds_review_pin: %s is not in the tree" % REVIEW)
    doc = sha(rp)
    for letter, rel in NETLISTS.items():
        have = sha(os.path.join(root, rel))[:16]
        if have != READ[letter]:
            raise SystemExit("apply_holds_review_pin: board %s's netlist is %s and the review read %s: re-review it first"
                             % (letter.upper(), have, READ[letter]))
    t, pos = old, 0
    for letter in ("a", "d", "e"):        # the holds stand in this order in the file
        i = t.index(NULL, pos)
        new = NULL.replace("sha256: null", 'sha256: "%s"' % doc).replace("netlist_sha16: null", 'netlist_sha16: "%s"' % READ[letter])
        t = t[:i] + new + t[i + len(NULL):]
        pos = i + len(new)
    assert t != old and NULL not in t
    d = yaml.safe_load(t)
    for letter in ("a", "d", "e"):
        q = [x for x in d["holds"][letter]["layout_entry_requires"] if x.get("kind") == "review"]
        assert len(q) == 1 and q[0]["sha256"] == doc and q[0]["netlist_sha16"] == READ[letter], (letter, q)
    if not dry:
        with open(holds, "w", encoding="utf-8") as f: f.write(t)
        yaml.safe_load(open(holds, encoding="utf-8"))
    print("apply_holds_review_pin: %s pinned as %s on netlists a %s, d %s, e %s%s"
          % (REVIEW, doc[:16], READ["a"], READ["d"], READ["e"], " (checked, not written)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
