#!/usr/bin/env python3
"""Set 7's fresh check (v2/docs/records/int8/CHECK.md, minor items 3 and 4): the ruling D-20's last sentence and M-02's and
EQ-13's appended sentences said the routes (c) to (e) "are not taken", which could read as excluding the second pack and the
larger pack from the options the reconciliation must present; the owner asked for such changes to be presented explicitly.
They now say "not taken by this ruling; (c) and (d) return only as options the reconciliation presents explicitly". S-114's
title now opens with the finding it rests on (EQ-13's arithmetic: the balance fails at desk) before the work it owes. Asserts
each old text once, re-parses the registry, refuses a second run. Run from the repository root: python3 <this file>."""
import os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml"); EQ = os.path.join(TOP, "v2/docs/handover/ENGINEERING-QUESTIONS.md")
OLD1 = "The routes (c) to (e) of EQ-13 are not taken."
NEW1 = ("The routes (c) to (e) of EQ-13 are not taken by this ruling; (c) and (d) return only as options the reconciliation "
        "presents explicitly, and (e) is excluded because unmet criteria stay visible.")
OLD2 = "the routes (c), (d) and (e) are not chosen; the energy budget is reconciled first (S-114)"
NEW2 = ("the routes (c), (d) and (e) are not chosen by the ruling, (c) and (d) returning only as options the reconciliation "
        "presents explicitly; the energy budget is reconciled first (S-114)")
OLD3 = "(stream energy, owner ruling D-20) The energy reconciliation of mission M1 on the approved constraints:"
NEW3 = ("(stream energy, owner ruling D-20; the finding: EQ-13's arithmetic, M-02: on the one pack of D-06 the balance of mission M1 "
        "fails at desk on both limits, the night and the day) The energy reconciliation of mission M1 on the approved constraints:")
OLD4 = "the routes (c) to (e) above are not taken."
NEW4 = "the routes (c) to (e) above are not taken by the ruling; (c) and (d) return only as options the reconciliation presents explicitly."


def refuse(m): print("apply_check_wording: REFUSED: %s" % m); sys.exit(2)


def edit(raw, header, old, new):
    r, _ = A.edit_fold(raw, header, 6, 120, [(old, new)]); return r


def main():
    reg = open(REG, encoding="utf-8").read(); eq = open(EQ, encoding="utf-8").read()
    if "not taken by this ruling" in reg: refuse("already applied")
    before = yaml.safe_load(reg)
    out = reg
    i, j = A.span(out, "D-20"); out = out[:i] + edit(out[i:j], "    ruling: >-", OLD1, NEW1) + out[j:]
    i, j = A.span(out, "M-02"); out = out[:i] + edit(out[i:j], "    title: >-", OLD2, NEW2) + out[j:]
    i, j = A.span(out, "S-114"); out = out[:i] + edit(out[i:j], "    title: >-", OLD3, NEW3) + out[j:]
    if eq.count(OLD4) != 1: refuse("EQ-13's row text occurs %d times" % eq.count(OLD4))
    eq2 = eq.replace(OLD4, NEW4)
    after = yaml.safe_load(out)
    ra, rb = {x["id"]: x for x in before["owner_rulings"]}, {x["id"]: x for x in after["owner_rulings"]}
    for k in ra:
        d = {f for f in set(ra[k]) | set(rb[k]) if ra[k].get(f) != rb[k].get(f)}
        if (k == "D-20" and d != {"ruling"}) or (k != "D-20" and d): refuse("ruling %s changed %s" % (k, d))
    oa, ob = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    for k in oa:
        d = {f for f in set(oa[k]) | set(ob[k]) if oa[k].get(f) != ob[k].get(f)}
        if (k in ("M-02", "S-114") and d != {"title"}) or (k not in ("M-02", "S-114") and d): refuse("item %s changed %s" % (k, d))
    for sec in before:
        if sec not in ("owner_rulings", "open_items") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(REG, "w", encoding="utf-8").write(out); open(EQ, "w", encoding="utf-8").write(eq2)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("apply_check_wording: D-20's sentence, M-02's and EQ-13's sentences, S-114's opening reworded as the check asked"); return 0


if __name__ == "__main__":
    sys.exit(main())
