#!/usr/bin/env python3
"""S-117 for board A's EMC sheet (stream s117, MESHSAT-1357, 29 September 2026): the U3 row at the frequency the S-117
decision draws. DRAFT for the integrator, run at the merge that applies apply_gen_sch_a_s117.py; the author ran --check.

The row said f_khz 800 as "the design's intent" with the IADPT resistor missing (set 10's answer to its check, B1; the
re-check's N1 asked for it to be marked provisional or recorded as a SESSION choice). It now reads 400 kHz, TI's row for
the 4.7 uH L2 with 191 kOhm on IADPT (SLUSE66A 9.3.11 and Table 9-4, printed page 27), its compensation (Table 9-5, pages
27 and 28) and PWM_FREQ at its power-on 1b (Table 9-8, page 43), with the FSW spread of 8.5 (340 to 460 kHz, page 16) and
the dithering state (9.3.15, page 28) in its basis.

Guards: the U3 row's two lines are found once each as read on main at 867a18a7 and fe97c980 (the row after apply_s117_restate.py);
the result parses (yaml) and only board A's U3 source moves, in f_khz and basis; emc_sheet.judge() (the tool's own
function, called in memory, no verdict written) reads board A with no failure that names U3, before and after; a second
run refuses (the new basis is already there). --check writes nothing.

Usage: python3 apply_emc_s117.py [--check]"""
import argparse, copy, os, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
EMC = os.path.join(TOP, "v2/ecad/tools/pcb_emc.yaml")
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))

HEAD_OLD = ('    - {ref: U3, part: BQ25731, what: "4S buck-boost charger, VBUS20 to the system node VBAT and the pack", '
            'f_khz: 800, edge_ns: null,\n')
HEAD_NEW = ('    - {ref: U3, part: BQ25731, what: "4S buck-boost charger, VBUS20 to the system node VBAT and the pack", '
            'f_khz: 400, edge_ns: null,\n')
BASIS_OLD = ('       basis: "v2/vendor/ti/bq25731-datasheet.pdf (SLUSE66A) 9.3.11 and Table 9-4, printed page 27: the charger reads '
             'its frequency and inductance from the resistor on IADPT before it starts; 800 kHz is the frequency TI recommends '
             'for the fitted 3.3 uH (L2) with 169 kOhm, the design\'s intent. Board A\'s IADPT net carries no resistor and no '
             '100 pF capacitor, so the frequency the drawn circuit starts at is not established (open item S-117); PWM_FREQ\'s '
             'power-on default is 400 kHz; frequency dithering is available and register-enabled, not declared"}\n')
BASIS_NEW = ('       basis: "v2/vendor/ti/bq25731-datasheet.pdf (SLUSE66A): 400 kHz, the row TI gives the 4.7 uH L2 (XAL1010-472ME) '
             'with R219 191 kOhm on IADPT, from which the charger reads its frequency and inductance before it starts (9.3.11 '
             'and Table 9-4, printed page 27), with the compensation of Table 9-5\'s 400 kHz row (R25, C26, C234, R220, C235, '
             'C27; pages 27 and 28) and PWM_FREQ at its power-on 1b, which FW-A17 of v2/docs/HW-FW-CONTRACT.md keeps (Table '
             '9-8, page 43). 340 to 460 kHz over the FSW spread (8.5, page 16). Frequency dithering (EN_DITHER, 9.3.15, page '
             '28) is off at power-on and not declared. The S-117 session decision in tools/pcb_decisions.yaml; figures in '
             'v2/docs/records/s117/charger_l_f.out. Drawn by v2/docs/records/s117/apply_gen_sch_a_s117.py; the committed '
             'netlist carries it once readback_s117.py reads PASS on it"}\n')


def refuse(m):
    print("apply_emc_s117: REFUSED: %s" % m)
    sys.exit(2)


def u3_fails(text):
    import emc_sheet as E
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(text); p = f.name
    try:
        r = E.judge(p, None, "a")
    finally:
        os.unlink(p)
    v = r.get("a") or {}
    return [x for x in v.get("fails", []) if "U3" in x], len(v.get("fails", [])), v.get("sources")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t = open(EMC, encoding="utf-8").read()
    if "the row TI gives the 4.7 uH L2 (XAL1010-472ME)" in t: refuse("already applied (a second run)")
    for what, old in (("the U3 row's first line", HEAD_OLD), ("the U3 row's basis", BASIS_OLD)):
        if t.count(old) != 1: refuse("%s occurs %d times, not once" % (what, t.count(old)))
    t2 = t.replace(HEAD_OLD, HEAD_NEW).replace(BASIS_OLD, BASIS_NEW)
    if t2 == t: refuse("nothing changed")
    before, after = yaml.safe_load(t), yaml.safe_load(t2)
    exp = copy.deepcopy(before)
    src = [s for s in exp["boards"]["a"]["sources"] if s["ref"] == "U3"]
    if len(src) != 1: refuse("board A has %d U3 sources" % len(src))
    src[0]["f_khz"] = 400
    src[0]["basis"] = [s for s in after["boards"]["a"]["sources"] if s["ref"] == "U3"][0]["basis"]
    if exp != after: refuse("something beyond board A's U3 row moved")
    if "\u2014" in t2 or "\u2013" in t2: refuse("a dash character")
    f0, n0, s0 = u3_fails(t)
    f1, n1, s1 = u3_fails(t2)
    if f1: refuse("emc_sheet reads board A's U3 row as failing: %s" % f1)
    print("apply_emc_s117: board A's U3 row f_khz 800 -> 400, basis restated; emc_sheet.judge on board A: %d source(s), %d "
          "failure(s) before, %d after, none naming U3" % (s1, n0, n1))
    if a.check:
        print("CHECK ONLY: pcb_emc.yaml not written.")
        return 0
    open(EMC, "w", encoding="utf-8").write(t2)
    if yaml.safe_load(open(EMC, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("APPLIED: v2/ecad/tools/pcb_emc.yaml written once.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
