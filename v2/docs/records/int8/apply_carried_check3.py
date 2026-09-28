#!/usr/bin/env python3
"""The registry edits the third check of the set 6 integration carried into set 7 (MESHSAT-1357, 28 September 2026;
v2/docs/records/int7/CHECK-3.md minor items p3, p4, p5 and p7, and CHECK-RESPONSE.md part three, which carried them).

  p7  FEA-002 (hardware EMCON) rests on RF-002, whose walk leaves the SA868 row on board D (S-92) and two rows on board
      A (S-93) undecided; the record waited on neither. It waits on both from here.
  p4  S-92 quoted 2.86 V "by R88 and R89 alone" while the walk's chain line gives 3.12 V for the same divider. The item
      now names both and says which is which: 3.12 V is the divider's nominal in the report's chain line (R88 1.2 k to
      +5V_SA, R89 2 k to ground); 2.86 V is the walk's adverse level from the currents that are known.
  p5  S-92 named bench E-01 as its bench route, and E-01 (EMCON.md, the bench table) measures U2 pin 5's "1" threshold
      and input current, grounds (1) and (2), not U13 pin 4's off-state current, ground (3). The item says so and names
      what closes ground (3) at the bench: the bench row gains that current, or the item names another row (EMCON.md's
      writer, stream d4emcon).
  p3  tx_inhibit.py prints at most three failed and three unsure grounds per state (`bad[:3]`, `unsure[:3]`); on the set
      6 netlists the longest list is 2, so nothing was cut, but a longer list would drop grounds from the report with no
      sign. A new open item S-97 records the tool change owed: print every ground or say how many were cut. It changes no
      record's verdict (an item closes on its row reading decided, whatever the report prints), so it carries a
      disposition TOOLING with its reason, as the validator requires of an item no record waits on.

No statement, acceptance, status or evidence_result changes. The script re-parses the file, asserts that only these
fields changed, and refuses a second run. Run from the repository root before rules_status: python3 <this file>."""
import os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A      # span, fold, block_at, edit_fold, screen (its main is not run on import)

P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
NEW = "S-97"
LINK = {"FEA-002": ["S-92", "S-93"]}
S92_EDITS = [
    ("(3) with EMCON on, the open-drain output U13 pin 4 is released and SA_PTT_n is held at 2.86 V by R88 and R89 alone, "
     "and U13's sheet does not state that output's off-state current while powered.",
     "(3) with EMCON on, the open-drain output U13 pin 4 is released and SA_PTT_n is held by R88 (1.2 k to +5V_SA) and "
     "R89 (2 k to ground) alone: 3.12 V is that divider's nominal in the report's chain line, 2.86 V the walk's adverse "
     "level from the currents that are known, and U13's sheet does not state that output's off-state current while "
     "powered."),
    ("or by a bench reading on a built board (bench E-01 of v2/docs/feasibility/EMCON.md; prototype verification), which "
     "is a sample of one board and is recorded as one.",
     "or by a bench reading on a built board, which is a sample of one board and is recorded as one (prototype "
     "verification): bench E-01 of v2/docs/feasibility/EMCON.md measures U2 pin 5's threshold and input current, grounds "
     "(1) and (2), and not U13 pin 4's off-state current, so ground (3) needs E-01 to gain that current or another bench "
     "row named here (EMCON.md's writer, stream d4emcon)."),
]
S97_TITLE = (
    "(int7 check 3, p3: a tool item) tx_inhibit.py's report prints at most three failed grounds and three unsure grounds "
    "per state (the slices bad[:3] and unsure[:3] in its report writer), so a state with four or more grounds would lose "
    "some from the report with no sign. On the set 6 netlists the longest list is two and nothing was cut (checked by the "
    "third fresh check of the set 6 integration, v2/docs/records/int7/CHECK-3.md). Owed: the report prints every ground, "
    "or prints how many it cut; a test with a fixture of four grounds in one state. Changing the report writer changes "
    "the tool's code bundle, so RF-002 is re-taken on every board with it (with the set's next box re-take).")
S97_WHY = (
    "A tool item: the report's completeness. It moves no record's verdict, because an item that rests on the walk (S-92, "
    "S-93) closes on its row reading decided, whatever the report prints, and the walk's verdict counts are unaffected "
    "by the slice. RF-002's owner changes the writer with the next tool change and re-takes the rule.")


def refuse(msg):
    print("apply_carried_check3: REFUSED: %s" % msg); sys.exit(2)


def main():
    t = open(P, encoding="utf-8").read()
    if "\n  - id: %s\n" % NEW in t: refuse("%s exists already (a second run)" % NEW)
    before = yaml.safe_load(t)
    recs = {r["id"]: r for r in before["records"]}
    items = {i["id"]: i for i in before["open_items"]}
    ids = {i["id"] for i in before["open_items"]} | {i["id"] for i in before["closed_items"]}
    if max(int(x[2:]) for x in ids if x.startswith("S-")) != int(NEW[2:]) - 1: refuse("%s is not the next free S id" % NEW)
    for rid, add in LINK.items():
        if set(add) & set(recs[rid].get("waits_on") or []): refuse("%s already waits on %s" % (rid, add))
        for iid in add:
            if iid not in items: refuse("%s is not an open item" % iid)
    for txt, what in ((S97_TITLE, NEW), (S97_WHY, NEW + " why")): A.screen(txt, what)
    if len(S97_WHY) < 40: refuse("disposition_why too short")

    out = t
    i, j = A.span(out, "S-92"); it = out[i:j]
    it, _ = A.edit_fold(it, "    title: >-", 6, 120, S92_EDITS)
    out = out[:i] + it + out[j:]
    for rid, add in LINK.items():
        i, j = A.span(out, rid); r = out[i:j]
        m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", r)
        if not m: refuse("%s carries no waits_on line" % rid)
        have = [x.strip() for x in m.group(1).split(",") if x.strip()]
        out = out[:i] + r[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + add) + r[m.end():] + out[j:]
    k = out.index("\nclosed_items:\n")   # open_items is followed by closed_items, then records
    block = ("  - id: %s\n    class: SESSION\n    status: OPEN\n    disposition: TOOLING\n    disposition_why: >-\n%s"
             "    title: >-\n%s" % (NEW, A.fold(S97_WHY, 6, 120), A.fold(S97_TITLE, 6, 120)))
    out = out[:k + 1] + block + out[k + 1:]
    if out == t: refuse("nothing changed")

    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    if list(recs) != list(rb): refuse("the record list changed")
    for kk in recs:
        diff = {f for f in set(recs[kk]) | set(rb[kk]) if recs[kk].get(f) != rb[kk].get(f)}
        if kk in LINK:
            if diff != {"waits_on"} or rb[kk]["waits_on"] != list(recs[kk].get("waits_on") or []) + LINK[kk]: refuse("%s: %s" % (kk, diff))
        elif diff: refuse("record %s changed: %s" % (kk, diff))
    ob = {i["id"]: i for i in after["open_items"]}
    if list(ob) != list(items) + [NEW]: refuse("the open item list changed beyond %s" % NEW)
    for kk in items:
        diff = {f for f in set(items[kk]) | set(ob[kk]) if items[kk].get(f) != ob[kk].get(f)}
        if kk == "S-92":
            if diff != {"title"}: refuse("S-92: fields changed %s" % diff)
            for _, new in S92_EDITS:
                if new not in ob[kk]["title"]: refuse("S-92's new text did not round-trip")
        elif diff: refuse("open item %s changed: %s" % (kk, diff))
    if ob[NEW]["title"] != S97_TITLE or ob[NEW]["disposition_why"] != S97_WHY or ob[NEW]["disposition"] != "TOOLING": refuse("%s did not round-trip" % NEW)
    for sec in before:
        if sec not in ("records", "open_items") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    print("apply_carried_check3: S-92 reworded (p4, p5); FEA-002 waits on S-92 and S-93 (p7); %s opened with disposition TOOLING (p3)" % NEW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
