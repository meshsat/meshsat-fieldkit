#!/usr/bin/env python3
"""S-117's session decision for tools/pcb_decisions.yaml (stream s117, MESHSAT-1357, 29 September 2026). DRAFT for the
integrator, run at the merge that applies apply_gen_sch_a_s117.py, then decisions_render.py; the author ran --check.

It appends one decision, numbered one above the register's highest at the time it runs (56 on main at 867a18a7), ruled by
the SESSION under the owner's rulings of 21 and 26 September 2026 (engineering decisions are the session's; never ask),
with its authority fields. The text is checked by the project's claims screen (int7's screen: no claim word, no dash), the
result parses, and nothing but the new entry moves. A second run refuses (a decision already names S-117 in its title).

Usage: python3 apply_decision_s117.py [--check]"""
import argparse, copy, os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
DEC = os.path.join(TOP, "v2/ecad/tools/pcb_decisions.yaml")
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A

MARK = "(S-117)"
TITLE = ("board A: the charger U3 takes TI's 400 kHz row, 4.7 uH on the XAL1010 land (XAL1010-472ME), 191 kOhm on IADPT and the "
         "400 kHz compensation " + MARK)
AUTHORITY_WHY = (
    "it changes no line the never-auto floor protects (no class of tools/reserved.json names gen_sch_a.py, pcb_emc.yaml or "
    "HW-FW-CONTRACT.md), spends nothing the owner decides (one inductor part number and five small passives inside board A's "
    "BOM; no purchase; the order codes of the XAL1010-472ME, the 191k 1 percent and the 15 pF NP0 0603 still need the parts "
    "stream's entry), changes no claim about the kit (the charger's input limits, charge voltage and charge current are "
    "untouched), and accepts no residual risk a measurement in this tree cannot remove (the switch node's frequency, the "
    "IADPT reading and the loop are bench items, V-A05). After the measurement one option stands: the drawn inductor's land "
    "(XAL60xx) fails the input's own bound at either row, and the 800 kHz row on the XAL1010 land asks more gate current of "
    "REGN than its 50 mA minimum limit with the drawn FETs and doubles every switching term.")
OUTCOME = (
    "U3 RUNS TI'S 400 kHz ROW: L2 BECOMES A COILCRAFT XAL1010-472ME (4.7 uH, ISAT 25.4 A, IRMS 17.5 / 24.0 A AT A 20 / 40 C "
    "RISE, DCR 5.20 / 5.70 mOhm; DOCUMENT 804-1) ON THE XAL1010 LAND BOARD A ALREADY CARRIES FOR L1 AND L8; R219 191k 1 PERCENT "
    "0603 FROM IADPT TO GROUND WITH C233 33 pF C0G (SLUSE66A 9.3.11 AND TABLE 9-4, PRINTED PAGE 27: 191 OR 187 kOhm FOR 4.7 uH, 3 "
    "PERCENT OR BETTER; THE PIN TABLE, PAGE 6, AND CIADPT_MAX, PAGE 12: 100 pF OR LESS); TABLE 9-5'S 400 kHz ROW (PAGES 27 AND "
    "28) AS FIGURE 9-2 DRAWS IT: R25 40.2k 1 PERCENT IN SERIES WITH C26 4.7 nF AND C234 33 pF ON COMP1, R220 15k 1 PERCENT IN "
    "SERIES WITH C235 680 pF AND C27 15 pF ON COMP2; PWM_FREQ STAYS AT ITS POWER-ON 1b, 400 kHz (TABLE 9-8, PAGE 43; FW-A17), "
    "SO THE RESISTOR, THE REGISTER AND THE COMPENSATION AGREE BEFORE ANY HOST WRITE; C121'S 10 nF IS THE CDIFF 10.2.2.2 ASKS "
    "FOR AT 400 kHz (PAGE 84); THE EMC ROW READS 400 kHz, 340 TO 460 kHz OVER THE FSW SPREAD (8.5, PAGE 16). The figures "
    "(v2/docs/records/s117/charger_l_f.out, currents at an efficiency of 1): the front end's 5.7 A maximum at 20.7 V into a "
    "pack at its 10.0 V CUV puts 11.80 A through L2; the drawn XAL6030-332ME fails SLUSE66A Equation 2 there at either row "
    "(13.53 A peak at 800 kHz and 15.27 A at 400 kHz, worst case, against 12.2 A) and runs at 148 percent of its 40 C rise "
    "current, 103 to 104 percent already with the pack at 14.4 V; the XAL6060-472ME on the same land fails Equation 2 from 8.85 A; "
    "the XAL1010-472ME at 400 kHz peaks at 14.10 A worst (L at minus 20 percent with its fall, 340 kHz) and carries 49 percent "
    "of its 40 C rise current, 56 percent at Option A(i)'s bound of 13.35 A. With board A's 10 mOhm input sense "
    "(RSNS_RAC = 0b, FW-A01) the input limit is 6.35 A whatever the inductance (9.3.5, page 25), so Table 9-1's lack of a "
    "4.7 uH row does not bind this board.")
REVERSED_BY = (
    "take the 800 kHz row on the same land with v2/docs/records/s117/apply_gen_sch_a_s117.py's calls changed: L2 "
    "XAL1010-332ME (3.3 uH), R219 169k 1 percent, R25 16.9k 1 percent, C26 3.3 nF, C235 1200 pF (R220 15k, C234 33 pF, C27 "
    "15 pF and C233 unchanged), FW-A17 written to set PWM_FREQ = 0b before the charge current is raised, the EMC row at 800 "
    "kHz and C121 optional; only once board A's power FETs keep 2 x Qg(6 V) x 920 kHz under REGN's 50 mA (the FET item this "
    "stream opens), or if R16 becomes 5 mOhm with an input limit above 6.35 A (Table 9-1, printed page 26, gives the 10 A limit "
    "for the 3.3 uH row and no 4.7 uH row).")
ASK = ("run TI's 400 kHz row with a 4.7 uH inductor (191 kOhm on IADPT) or its 800 kHz row with 3.3 uH (169 kOhm), on the drawn "
       "inductor's land or on a larger one")
RECOMMENDATION = (
    "THE 400 kHz ROW ON THE XAL1010 LAND. The XAL60xx land fails the charger's own input bound with either row's part; on the "
    "XAL1010 land both rows pass the inductor's ratings, and the 400 kHz row halves every switching term with the drawn FETs "
    "(6.6 to 8.6 W less at the bound, 4.4 to 5.6 W less at the front end's typical 5.0 A), asks half the gate current of REGN "
    "and agrees with PWM_FREQ's power-on value without a host. It does not make the drawn FETs fit REGN: 46 to 60 mA at a "
    "typical 400 kHz against the 50 mA minimum limit is the FET item's, opened beside this decision.")
EVIDENCE = (
    "TI SLUSE66A (v2/vendor/ti/bq25731-datasheet.pdf) printed pages 6, 9, 11, 12, 15, 16, 25 to 28, 42, 43, 80 and 84 to 88; "
    "Coilcraft Documents 887-1 to 887-4 and 804-1 to 804-4 (v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf, "
    "v2/vendor/power/coilcraft-xal1010.pdf); TI SLPS632 p.3 and Figures 2 to 4 p.5 (v2/vendor/battery/ti-csd18510q5b.pdf); "
    "board A's netlist v2/ecad/pcb-a-power-a23/out/pcb-a-power.net (sha256/16 30ad87746d1801ca, read by "
    "v2/docs/records/s117/readback_s117.py); the pack voltages of v2/docs/review-packets/battery/FUSE-INTERPRETATION.md; "
    "Option A(i)'s settings in v2/docs/records/a1elec/CHARGER.md (a record since set 11; read only); v2/docs/records/s117/charger_l_f.py and its "
    ".out; round 4's O-24 (v2/docs/records/r4a/r4-open-items.md); set 10's check B1 and re-check N1 "
    "(v2/docs/records/int11/CHECK.md, CHECK-2.md).")
HOLDS = ("it releases no rule-board pair: S-117 closes only when board A's regenerated netlist carries the parts "
         "(readback_s117.py reads PASS); REQ-015 still waits on S-106, S-107, S-111 and the FET item.")


def refuse(m):
    print("apply_decision_s117: REFUSED: %s" % m)
    sys.exit(2)


def block(n):
    def f(key, text): return "    %s: >-\n%s" % (key, A.fold(text, 6, 120))
    return ("  - n: %d\n" % n + f("title", TITLE) + "    asked: 2026-09-29\n    status: ruled\n    authority: SESSION\n"
            + f("authority_why", AUTHORITY_WHY) + "    ruled_by: SESSION\n    ruled_on: 2026-09-29\n" + f("outcome", OUTCOME)
            + f("reversed_by", REVERSED_BY) + f("ask", ASK) + f("recommendation", RECOMMENDATION) + f("evidence", EVIDENCE)
            + "    blocks: {}\n" + f("holds_nothing_today", HOLDS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t = open(DEC, encoding="utf-8").read()
    d = yaml.safe_load(t)
    if any(MARK in str(x.get("title", "")) for x in d["decisions"]): refuse("a decision already names S-117 (a second run)")
    for what, text in (("title", TITLE), ("authority_why", AUTHORITY_WHY), ("outcome", OUTCOME), ("reversed_by", REVERSED_BY),
                       ("ask", ASK), ("recommendation", RECOMMENDATION), ("evidence", EVIDENCE), ("holds", HOLDS)):
        A.screen(text, "the decision's %s" % what)
    n = max(int(x["n"]) for x in d["decisions"]) + 1
    if not t.endswith("\n"): refuse("the register does not end with a newline")
    out = t + block(n)
    after = yaml.safe_load(out)
    if after["decisions"][:-1] != d["decisions"]: refuse("an existing decision moved")
    new = after["decisions"][-1]
    for k, v in (("n", n), ("status", "ruled"), ("authority", "SESSION"), ("ruled_by", "SESSION"), ("blocks", {})):
        if new.get(k) != v: refuse("the new entry's %s reads %r" % (k, new.get(k)))
    for k in ("authority_why", "reversed_by", "outcome", "ask", "recommendation", "evidence", "holds_nothing_today"):
        if len(str(new.get(k) or "")) < 60: refuse("the new entry's %s is short" % k)
    if ".py" not in new["reversed_by"]: refuse("the way back names no script")
    print("apply_decision_s117: decision %d appended (%s); %d decisions -> %d; nothing else moved" % (n, TITLE[:60] + "...",
                                                                                                  len(d["decisions"]), len(after["decisions"])))
    if a.check:
        print("CHECK ONLY: pcb_decisions.yaml not written. Next after the write: python3 v2/ecad/tools/decisions_render.py")
        return 0
    open(DEC, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(DEC, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("APPLIED: decision %d in v2/ecad/tools/pcb_decisions.yaml. Next: python3 v2/ecad/tools/decisions_render.py" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
