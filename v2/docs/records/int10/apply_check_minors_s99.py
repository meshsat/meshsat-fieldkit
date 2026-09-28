#!/usr/bin/env python3
"""Set 9's AI check (records/int10/CHECK.md), three of its minor items answered in place (MESHSAT-1357, 29 September 2026):
  M1  four judged rebind entries (CFL-005, CON-010, CFL-016, CFL-014) said U39 and R209 appear "only in an earlier rebind
      entry"; U39 also appears in each record's re-read of PANEL.md or EMCON.md about its overvoltage lockout and fault
      line. The script proves that from the record itself (U39 named in an entry that is not a rebind entry) before
      correcting the sentence; the conclusion (no result changes) stands, since that part and its value did not change.
  M7  S-99's "Closes when" still listed the regeneration, the re-takes and the interface row, which this set has done;
      they move to a sentence that says so, and what closes S-99 is what remains.
  M4  the erratum to the decision 31 review said a board A review is "owed anyway after the regeneration", while the
      hold's review pin moved to the new netlist on a parsed proof and reads met.
It asserts each old text once, re-parses the registry and checks that only the named fields changed, screens the new
text for claim words and dashes, and refuses a second run. Run from the repository root."""
import os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import apply_check1_answers as A

P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
ERR = os.path.join(TOP, "v2/docs/records/int10/ERRATA-DECISION-31-REVIEW.md")
MARK = "apply_rebind_after_circuit a 599ee964a9c23d6e"
OLD1 = "U39 and R209 appear only in an earlier rebind entry that lists the H2 differences; both are the same parts"
NEW1 = ("U39 and R209 appear in an earlier rebind entry that lists the H2 differences, and U39 also in this record's re-read "
        "of PANEL.md or EMCON.md about its overvoltage lockout and fault line, which the change leaves as it was (sentence "
        "corrected after set 9's AI check, minor item M1); both are the same parts")
OLD7 = ("Closes when: board A is regenerated from fnd/s99a on the box and its intent, netlist and ERC are read; PWR-001 and "
        "INT-001 are re-taken on it; the IF-AB-POWER +5V_DEV row reads the new figures; (a) is decided")
NEW7 = ("Done at integration set 9: board A regenerated from fnd/s99a on the box with its intent, netlist and ERC read, "
        "PWR-001 and INT-001 re-taken on it, and the IF-AB-POWER +5V_DEV row reading the new figures. Closes when: (a) is "
        "decided")
OLD4 = "The next review of board A (owed anyway after the regeneration) should quote 0.9142 A."
NEW4 = ("Any later review of board A should quote 0.9142 A; none is owed by the regeneration itself, since the decision 31 "
        "hold's review pin moved to the new netlist on a parsed proof and reads met (set 9's AI check, minor item M4).")
RIDS = ("CFL-005", "CON-010", "CFL-016", "CFL-014")


def refuse(m):
    print("apply_check_minors_s99: REFUSED: %s" % m); sys.exit(2)


def main():
    t = open(P, encoding="utf-8").read()
    if "set 9's AI check, minor item M1" in t: refuse("already applied (a second run)")
    before = yaml.safe_load(t)
    rec = {r["id"]: r for r in before["records"]}
    for rid in RIDS:
        others = [e for e in rec[rid]["evidence"] if "U39" in str(e) and "apply_rebind" not in str(e) and "rebound" not in str(e)]
        if not others: refuse("%s names U39 in no entry but the rebind ones; M1 does not apply to it" % rid)
        i, j = A.span(t, rid)
        body, text = A.edit_fold(t[i:j], "      - >-", 10, 120, [(OLD1, NEW1)],
                                 first_words="v2/ecad/pcb-a-power-a23/out/pcb-a-power.net re-read at integration set 9")
        if MARK not in text: refuse("%s: the edited block is not set 9's rebind entry" % rid)
        t = t[:i] + body + t[j:]
    i, j = A.span(t, "S-99")
    body, text = A.edit_fold(t[i:j], "    title: >-", 6, 120, [(OLD7, NEW7)])
    t = t[:i] + body + t[j:]
    after = yaml.safe_load(t)
    rb, ra = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for k in rb:
        d = {f for f in set(rb[k]) | set(ra[k]) if rb[k].get(f) != ra[k].get(f)}
        if d and not (k in RIDS and d == {"evidence"}): refuse("%s changed in %s" % (k, d))
    ib, ia = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    for k in ib:
        d = {f for f in set(ib[k]) | set(ia[k]) if ib[k].get(f) != ia[k].get(f)}
        if d and not (k == "S-99" and d == {"title"}): refuse("open item %s changed in %s" % (k, d))
    for x in ("closed_items",):
        if before.get(x) != after.get(x): refuse("%s changed" % x)
    e = open(ERR, encoding="utf-8").read()
    if e.count(OLD4) != 1: refuse("the erratum's sentence is not there once")
    A.screen(NEW4, "M4's sentence")
    e2 = e.replace(OLD4, NEW4)
    open(P, "w", encoding="utf-8").write(t)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("re-parse differs")
    open(ERR, "w", encoding="utf-8").write(e2)
    print("apply_check_minors_s99: M1 corrected in %s; M7 in S-99's title; M4 in the erratum" % ", ".join(RIDS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
