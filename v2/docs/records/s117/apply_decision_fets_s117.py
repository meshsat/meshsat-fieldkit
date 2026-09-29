#!/usr/bin/env python3
"""S-117's finding F1: the session decision on board A's charger FETs, for tools/pcb_decisions.yaml (stream s117, second
issue, MESHSAT-1357, 29 September 2026). DRAFT for the integrator, run at the merge AFTER apply_decision_s117.py (so this
entry is numbered after S-117's), then decisions_render.py; the author ran --check.

It appends one decision, numbered one above the register's highest at the time it runs (57 on the tree checked, after
decision 56), ruled by the SESSION under the owner's rulings of 21 and 26 September 2026 (engineering decisions are the
session's; a part choice inside an approved function needs no owner decision, the coordinator's brief of the second
issue), with its authority fields. The text passes int7's screen (no claim word, no dash), the result parses, and nothing
but the new entry moves. A second run refuses (a decision already carries the mark "(S-117 F1)" in its title).

Usage: python3 apply_decision_fets_s117.py [--check]"""
import argparse, copy, os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
DEC = os.path.join(TOP, "v2/ecad/tools/pcb_decisions.yaml")
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A

MARK = "(S-117 F1)"
TITLE = ("board A: the charger U3's power FETs chosen for its own 6 V gate drive, Q7 CSD17578Q5A and Q8 to Q10 CSD17577Q5A "
         + MARK)
AUTHORITY_WHY = (
    "it changes no line the never-auto floor protects (no class of tools/reserved.json names gen_sch_a.py or intent_checks.py), "
    "spends nothing the owner decides (four part numbers inside board A's BOM on the land they already use; no purchase; both "
    "order codes and the Q5A package's fit on the PowerPAK SO-8 land still need the parts stream's entry), changes no claim "
    "about the kit (a part choice inside an approved function: the charger's settings, input limits and charge current are "
    "unchanged), and accepts no residual risk a measurement in this tree cannot remove (the switch node, the loop and the "
    "temperatures are layout and bench items). After the measurement one option stands on the drawn land: the drawn "
    "CSD18510Q5B ask REGN 60 to 89 mA against its 50 mA minimum limit and put 4.8 W in Q7 at the model's peak, and no other "
    "fetched part on the drawn land brings the charger closer to the budget.")
OUTCOME = (
    "U3'S BUCK LEG TAKES A FAST HIGH SIDE AND LOW-RESISTANCE PARTS ELSEWHERE: Q7 CSD17578Q5A (30 V; Qg 10.3 nC AT 6 V, QGD 2.0 "
    "AND QGS 3.1 nC, QRR 6.5 nC, 6.6 mOhm AT 6 V; TI SLPS526 5.1 p.3 AND FIGURES 4 AND 7 p.5), Q8, Q9 AND Q10 CSD17577Q5A (30 "
    "V; 16 nC AT 6 V, QRR 8.2 nC, 3.9 mOhm AT 6 V; TI SLPS516 5.1 p.3 AND p.5), ON THE LAND AND NETS THEY HAVE (BOTH TI'S SON 5 "
    "x 6 mm Q5A WITH THE Q5B'S PIN ORDER), AND PWR-001'S PIN-ROLE TABLE LEARNS BOTH (apply_intent_checks_s117.py). REGN then "
    "supplies 10.5 mA typical in buck mode and 36.5 mA at the makers' maxima with all four switching at 460 kHz, against its "
    "50 mA minimum limit (SLUSE66A 8.5, printed page 11); the charger reads 0.979 at the energy model's peak by TI's method "
    "(Equations 6 to 22, pages 86 to 88), 0.972 to 0.983 across the readings, R16 and R17 counted, core loss excluded, where "
    "the drawn FETs read 0.943 (0.924 to 0.964); the day's energy-weighted 0.979 at entry E2 and 0.981 at E1 against 0.939 "
    "and 0.936 (v2/docs/records/s117/efficiency.out). Q7 dissipates 1.0 to 1.5 W at the peak and 1.3 to 2.2 W at the input's "
    "bounds (4.8 to 9.8 W drawn). The screen: Nexperia's PSMN4R0-30YLD meets all five of the independent check's criteria "
    "but is LFPAK56, not the drawn land, and gives the same 0.979; CSD17578Q5A misses only the 5 mOhm criterion, and as Q7 "
    "beside a CSD17577Q5A Q8 it reaches the efficiency the criteria were set for (0.979 at R16 10 mOhm). With these FETs "
    "the 800 kHz row still costs 0.6 to 1.4 W more at the peak, so decision 56's 400 kHz row stands.")
REVERSED_BY = (
    "restore nfet(_qr, \"CSD18510Q5B 40 V N-FET\", _g, _d, _s) for Q7 to Q10 in gen_sch_a.py (the line "
    "v2/docs/records/s117/apply_gen_sch_a_fets_s117.py replaces), drop the two PIN_ROLES rows apply_intent_checks_s117.py "
    "adds, regenerate board A and re-take PWR-001; or take the PSMN4R0-30YLD for Q7 and Q8 if board A's layout writer draws "
    "its LFPAK56 land, with efficiency.py re-run on it.")
ASK = ("keep the CSD18510Q5B, or choose switching FETs that the BQ25731's 6 V REGN can drive at 400 kHz, on the drawn land "
       "or on another")
RECOMMENDATION = (
    "THE Q5A PAIR ON THE DRAWN LAND. It brings REGN inside its limit in every mode with margin, U3 to 0.979 by TI's method "
    "at the model's peak (the energy chain carries 0.98), and Q7 from 4.8 to 1.0 W there; it needs no land change. The "
    "energy record's writer restates the charger rows from efficiency.out section 7 (S-117 F2).")
EVIDENCE = (
    "TI SLPS526 (CSD17578Q5A) and SLPS516 (CSD17577Q5A) pp.1, 3, 5 and 9, held back by TI's terms and pinned by sha256 in "
    "v2/vendor/sources.txt (v2/docs/records/s117/fetch_held_back.py); TI SLPS524 and SLPS630 and Nexperia's PSMN4R0-30YLD "
    "(the screen, pinned the same way); TI SLPS632 (CSD18510Q5B, v2/vendor/battery/ti-csd18510q5b.pdf); TI SLUSE66A pin "
    "table pp.5 and 6, 8.5 pp.11, 12 and 16, Table 9-3 p.27, 10.2.2.6 pp.86 to 88; Coilcraft 804-1 and 804-2; the energy "
    "model's reference day read through v2/docs/records/a1elec/energy_two_pack.py; v2/docs/records/s117/efficiency.py and "
    "its .out; the independent check of stream s117 (its blocking items B1 and B2 and its criteria for the switching pair).")
HOLDS = ("it releases no rule-board pair: F1 closes only when board A's regenerated netlist carries the four FETs "
         "(readback_s117.py --fets reads PASS); REQ-015 then still waits on S-106, S-107 and S-111, and REQ-072 on the energy "
         "chain's charger rows (F2).")

def refuse(m):
    print("apply_decision_fets_s117: REFUSED: %s" % m)
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
    if any(MARK in str(x.get("title", "")) for x in d["decisions"]): refuse("a decision already carries the mark (S-117 F1) (a second run)")
    if not any("(S-117)" in str(x.get("title", "")) for x in d["decisions"]): refuse("run apply_decision_s117.py first (S-117's decision is not in the register)")
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
    print("apply_decision_fets_s117: decision %d appended (%s); %d decisions -> %d; nothing else moved" % (n, TITLE[:60] + "...",
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
