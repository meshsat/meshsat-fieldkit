#!/usr/bin/env python3
"""Finding I-03 (the A to B power leads, contract IF-AB-POWER) recorded in the requirements registry after the Codex
pilot and its independent check (MESHSAT-1357, integration set 7, 28 September 2026; v2/docs/records/cx1/).

  S-98  the interim alignment of the two ends' declarations, owed to the generator owners of boards A and B in the
        circuit round (a DECLARATION disposition, as S-67: it moves no record's verdict directly).
  S-99  the +5V_DEV converter's declared peak against its loads' coincident peak and the LM5176 average current limit,
        a design finding that bears on REQ-018 (every rail in regulation through the all-transmit key-down): REQ-018
        waits on it; a session decision is owed in the circuit round.

The script asserts the next free ids, re-parses the file, asserts that only these fields changed and refuses a second
run. Run from the repository root before rules_status: python3 <this file>."""
import os, subprocess, sys, re

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A      # span, fold, screen

P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
S98, S99 = "S-98", "S-99"
LINK = {"REQ-018": [S99]}
T98 = (
    "(cx1, finding I-03 on the contract IF-AB-POWER) The two ends of the board A to board B power leads declare different "
    "currents for one conductor: +5V_S2 (board A 2.5 A typical and 5.0 A peak; board B 4.2 A typical and 5.63 A coincident "
    "with the 5G module at 4 A) and +5V_DEV (board A apportions 3.2 A to J_5V_DEV; board B declares 3.8 A typical arriving). "
    "The pilot's record (v2/docs/records/cx1/ANALYSIS.md and CORRECTION.md, its independent AI check in checks/) derives "
    "board B's figures from held maker pages (the CM5's 0.9 A typical, release 3, no maximum published; the RM520N-GL's 3 A "
    "continuous and 4 A peak supply capability, Hardware Design v1.0 and v1.1) and finds no held document that decides the "
    "PS-ALLTX mode current of any of the five rails (INCONCLUSIVE on all five), so the alignment is INTERIM and the end that "
    "derives its figure is the one aligned to: board A's +5V_S2 4.2 A typical and 5.63 A peak with J_5V_S2 5.63 A and the "
    "VBAT load Q28 2.22 A, board B's +5V_S2 peak 5.63 A, board A's J_5V_DEV 3.8 A and +5V_DEV typical 5.1 A (3.8 + the D8 "
    "mezzanine's 1.0 + the wall port's 0.3), as the four verified, unexecuted entries of records/cx1/apply_declarations_draft.py "
    "(its --check passes against the generators as held). The generator owners of boards A and B apply them in the circuit "
    "round with the regeneration on the KiCad host; then the contract's currents rows are rewritten and INT-001 and PWR-001 "
    "re-taken. The mode figures are decided by TEST-PLAN power tests at J_5V_S2 and J_5V_DEV under PS-ALLTX on a built board "
    "(prototype verification). Also for board B's owner: the supervisor LDOs U40, U50 and U60 at 0.05 A against their child "
    "rails' 0.12 and 0.25 A, the LoRa module U21 at 0.6 A against Ebyte's 0.65 A transmit figure, and U25's comment of 1.4 A "
    "against the declared 1.2 A on +3V3_DEV.")
W98 = (
    "A declaration item: it moves no record's verdict directly (INT-001 judges the contract's agreement and PWR-001 judges "
    "board A's copper at the declared current). The generator owners of boards A and B apply the interim entries in the "
    "circuit round; the contract is re-read and INT-001 and PWR-001 re-taken then.")
T99 = (
    "(cx1, finding I-03's second half) Board A's +5V_DEV converter, an LM5176 stage whose average current limit is 7.10 A at "
    "the sense resistor's +1 percent and 7.17 A nominal (TI SNVSAI1D, VSNS on page 7 and section 7.3.6 on page 17), declares "
    "6.9 A peak, which is board B's 6.0 A plus the wall port's 0.9 A with the D8 mezzanine at zero, while D8 declares 1.0 A "
    "typical and 2.0 A peak (its eFuse U23's nominal limit) and nothing in the design makes the three loads non-coincident "
    "(the D-11 interlock drops POE_EN and PD_EN only). The coincident peak is 7.9 A with D8 at its typical and 8.9 A at every "
    "declared limit, both above the average loop's threshold; the registry's own power model already puts the rail's HIGH case "
    "at 7.8 A (v2/docs/feasibility/POWER-THERMAL.md, the +5V_DEV row and its LM5176 note). If demand holds above the threshold "
    "the loop folds the output back, a brown-out of the always-on fabric during REQ-018's key-down. A session decision is owed "
    "(authority SESSION, tools/pcb_decisions.yaml) with more than one option standing: raise the stage's average limit by its "
    "sense resistor within the FETs' and the inductor's ratings, make D8 or the wall port non-coincident with the PA key-down "
    "by an interlock, or declare the 8.9 A bound with the fold-back named as the limiter and REQ-018 judged on it. Board A's "
    "generator owner in the circuit round, PWR-001 and INT-001 re-taken; the bench decides the mode current at J_5V_DEV under "
    "PS-ALLTX with the LoRa, RockBLOCK and APRS bursts (prototype verification). Record: v2/docs/records/cx1/ANALYSIS.md, "
    "CORRECTION.md item B2 and checks/check-1-RESULT.md item B2.")


def refuse(msg):
    print("apply_i03_items: REFUSED: %s" % msg); sys.exit(2)


def main():
    t = open(P, encoding="utf-8").read()
    for iid in (S98, S99):
        if "\n  - id: %s\n" % iid in t: refuse("%s exists already (a second run)" % iid)
    before = yaml.safe_load(t)
    recs = {r["id"]: r for r in before["records"]}
    items = {i["id"]: i for i in before["open_items"]}
    ids = {i["id"] for i in before["open_items"]} | {i["id"] for i in before["closed_items"]}
    if max(int(x[2:]) for x in ids if x.startswith("S-")) != int(S98[2:]) - 1: refuse("%s is not the next free S id" % S98)
    for rid, add in LINK.items():
        if set(add) & set(recs[rid].get("waits_on") or []): refuse("%s already waits on %s" % (rid, add))
    for txt, what in ((T98, S98), (W98, S98 + " why"), (T99, S99)): A.screen(txt, what)
    if len(W98) < 40: refuse("disposition_why too short")

    out = t
    for rid, add in LINK.items():
        i, j = A.span(out, rid); r = out[i:j]
        m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", r)
        if not m: refuse("%s carries no waits_on line" % rid)
        have = [x.strip() for x in m.group(1).split(",") if x.strip()]
        out = out[:i] + r[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + add) + r[m.end():] + out[j:]
    k = out.index("\nclosed_items:\n")   # open_items is followed by closed_items, then records
    block = ("  - id: %s\n    class: SESSION\n    status: OPEN\n    disposition: DECLARATION\n    disposition_why: >-\n%s"
             "    title: >-\n%s" % (S98, A.fold(W98, 6, 120), A.fold(T98, 6, 120)))
    block += "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (S99, A.fold(T99, 6, 120))
    out = out[:k + 1] + block + out[k + 1:]

    after = yaml.safe_load(out)
    rb = {r["id"]: r for r in after["records"]}
    if list(recs) != list(rb): refuse("the record list changed")
    for kk in recs:
        diff = {f for f in set(recs[kk]) | set(rb[kk]) if recs[kk].get(f) != rb[kk].get(f)}
        if kk in LINK:
            if diff != {"waits_on"} or rb[kk]["waits_on"] != list(recs[kk].get("waits_on") or []) + LINK[kk]: refuse("%s: %s" % (kk, diff))
        elif diff: refuse("record %s changed: %s" % (kk, diff))
    ob = {i["id"]: i for i in after["open_items"]}
    if list(ob) != list(items) + [S98, S99]: refuse("the open item list changed beyond the two new items")
    for kk in items:
        if items[kk] != ob[kk]: refuse("open item %s changed" % kk)
    if ob[S98]["title"] != T98 or ob[S98]["disposition_why"] != W98 or ob[S98]["disposition"] != "DECLARATION": refuse("S-98 did not round-trip")
    if ob[S99]["title"] != T99 or "disposition" in ob[S99]: refuse("S-99 did not round-trip")
    for sec in before:
        if sec not in ("records", "open_items") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    print("apply_i03_items: %s opened (DECLARATION, the interim alignment for the generator owners); %s opened and REQ-018 waits on it" % (S98, S99))
    return 0


if __name__ == "__main__":
    sys.exit(main())
