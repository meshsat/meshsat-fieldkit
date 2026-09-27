#!/usr/bin/env python3
"""Take board B's class "the PCIe switches' own sockets on the carrier" out of pcb_reliability.yaml.

Worker set6fix, MESHSAT-1357, 27 September 2026. FOR THE INTEGRATOR: the worker did not run it on the tree.

WHY. The class was declared on 16 September for U101, U201 and U301, three soldered PI7C9X2G404SL packet
switches (LQFP-128), because reliability.py searched its word list in the whole value and found "socket" in
"port 2 card socket". Its own basis says "these are soldered ICs and not connectors: they appear in this list
because the search finds their package names". Since reliability.py judges a part's identity, the search no
longer finds them, so the class covers no wear part and that sentence is no longer true of the tool.

WHAT ELSE MOVES WITH IT, which is why it is the integrator's to run: pcb_reliability.yaml is a configuration
input of reliability.py's readings (rules_status.py CONFIG_INPUTS); board B's class count goes from 6 to 5 and
the set's from 26 to 25. pcb_rules_coverage.yaml's REL-001 note and the pages rendered from it say "declares 25
classes", a figure of 16 September that the list of 26 had already left behind; whoever runs this reads that
note again. `H1`'s copy under v2/release/handover/ is a snapshot and is not touched.

It asserts the old text is present exactly once, that the new text differs, re-parses the file, checks what the
file then declares, and refuses a second run.

Usage: apply_drop_pcie_switch_class.py [--file <pcb_reliability.yaml>]     (default: the tree's own)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "ecad", "tools", "pcb_reliability.yaml"))

OLD = '''    - {name: "the PCIe switches' own sockets on the carrier", refs: ["U101", "U201", "U301"], cycles: null,
       basis: "these are soldered ICs and not connectors: they appear in this list because the search finds
         their package names, and they carry no mating load at all",
       load: "none: a soldered QFN",
       measure: "none needed; recorded so the list is complete rather than filtered"}
'''
NEW = ""
NAME = "the PCIe switches' own sockets on the carrier"


def main(argv):
    import yaml
    p = argv[argv.index("--file") + 1] if "--file" in argv else DEFAULT
    s = open(p, encoding="utf-8").read()
    before = yaml.safe_load(s)
    names = [c.get("name") for c in (before["boards"]["b"].get("classes") or [])]
    if NAME not in names and OLD not in s:
        print("apply_drop_pcie_switch_class: REFUSED, %s no longer declares the class: it was applied already" % p)
        return 1
    assert s.count(OLD) == 1, "the class is declared, but not in the text this script was written against"
    assert OLD != NEW
    t = s.replace(OLD, NEW)
    assert t != s, "the new text does not differ from the old"
    after = yaml.safe_load(t)                                            # the patched text re-parsed
    b0, b1 = before["boards"]["b"]["classes"], after["boards"]["b"]["classes"]
    assert len(b1) == len(b0) - 1 and NAME not in [c.get("name") for c in b1], "board B's classes are not the old ones less one"
    assert [c for c in b0 if c.get("name") != NAME] == b1, "another class of board B moved"
    assert {k: v for k, v in before["boards"].items() if k != "b"} == {k: v for k, v in after["boards"].items() if k != "b"}, \
        "another board moved"
    assert not [c for c in b1 if any(r in ("U101", "U201", "U301") for r in (c.get("refs") or []))]
    open(p, "w", encoding="utf-8").write(t)
    assert yaml.safe_load(open(p, encoding="utf-8")) == after
    total = sum(len(v.get("classes") or []) for v in after["boards"].values())
    print("apply_drop_pcie_switch_class: %s, board B %d -> %d classes, the set %d -> %d"
          % (p, len(b0), len(b1), total + 1, total))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
