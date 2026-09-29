#!/usr/bin/env python3
"""Set 12 (MESHSAT-1357, 29 September 2026): the S-117 re-check's minor n1 carried as a registry item. Decision 57 moves board A's
charger FETs from the 40 V CSD18510Q5B to the 30 V CSD17578Q5A and CSD17577Q5A; the charger's input bus VBUS20 sits behind the
front end U2 (LM5176) at about 20.7 V, and no open item bounds an overvoltage on that bus (a front-end fault or a transient)
against the new 30 V rating and the charger's own input limit. Opens S-120 and links it from REQ-015 (the input that charges
the pack). Asserts its anchors once, re-parses, and checks that only the new item and REQ-015's waits_on changed; refuses a
second run. Run from the repository root."""
import os, subprocess, sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
ITEM = """  - id: S-120
    class: SESSION
    status: OPEN
    title: >-
      (the independent re-check of stream s117, minor n1; integration set 12) Decision 57 moves board A's charger switching
      FETs Q7 to Q10 from the 40 V CSD18510Q5B to the 30 V CSD17578Q5A (Q7) and CSD17577Q5A (Q8 to Q10). They sit on the
      charger's input bus VBUS20, which the front end U2 (LM5176) holds at about 20.7 V, and on the pack side; no open item
      bounds the bus's worst case (a front-end fault, a load dump through the front end, a transient) against the FETs' new
      30 V rating and the BQ25731's own input limit (TI SLUSE66A, absolute maximum ratings). Closed when that worst case is
      bounded from the front end's own protection or a clamp on VBUS20, with its figures and pages, or the FETs' rating is
      restated with the reason.
"""


def refuse(m):
    print("apply_s120_set12: REFUSED: %s" % m); sys.exit(2)


def main():
    t = open(REG, encoding="utf-8").read()
    if "  - id: S-120\n" in t: refuse("already applied")
    before = yaml.safe_load(t)
    anchor = "closed_items:\n"
    if t.count(anchor) != 1: refuse("the closed_items anchor is not found once")
    t2 = t.replace(anchor, ITEM + anchor)
    old = "    waits_on: [S-106, S-107, S-111]\n"
    i = t2.index("  - id: REQ-015\n")
    j = t2.index("\n  - id: ", i + 5)
    blk = t2[i:j]
    if blk.count(old) != 1: refuse("REQ-015's waits_on is not as expected")
    t2 = t2[:i] + blk.replace(old, "    waits_on: [S-106, S-107, S-111, S-120]\n") + t2[j:]
    after = yaml.safe_load(t2)
    rb, ra = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for k in rb:
        d = {f for f in set(rb[k]) | set(ra[k]) if rb[k].get(f) != ra[k].get(f)}
        if (k == "REQ-015" and d != {"waits_on"}) or (k != "REQ-015" and d): refuse("%s: %s" % (k, d))
    open(REG, "w", encoding="utf-8").write(t2)
    print("apply_s120_set12: S-120 opened (the charge bus against the 30 V FETs) and linked from REQ-015")
    return 0


if __name__ == "__main__":
    sys.exit(main())
