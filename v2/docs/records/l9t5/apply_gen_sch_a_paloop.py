#!/usr/bin/env python3
"""apply_gen_sch_a_paloop.py: DRAFT for board A's generator owner (Layer 4 P0-1, record l9t5, F01 / D-17 on C-ALLTX rev 3,
MESHSAT-1357, 5 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write
scratch copies). Prototype design: nothing is built, bought or measured.

The defect (F01 / D-17, L9P-F01; record l9t5 l9t5_f01.out section 1): C-ALLTX rev 3 (REQ-018 with CONOPS 4a: every transmitter keyed,
fans running, the standby WiFi card off, the other loads typical, a 60 s key-down from a 15.5 V rest at 18 A indicated) needs 15.5162 V,
and 16.0718 V with the printed bounds (the BQ4050's uncalibrated 0.8036 A, the dock's power pins at 20 mOhm). The PA's DC input is the
one number nothing drawn bounds: board D sets VGG open loop (4.30 to 4.68 V), so the case takes the RA30H1317M1's 45 W rating at its
40 % printed minimum, 113 W; the bounded case allows 103.44 W. The same figure is L9P-F04: 8.19 A on +13V8_PA against U13's own
loop minimum.

The correction selected (l9t5_f01.out section 5, correction (c), SESSION; round 2 after Astra's cx44, PROVISIONAL on the supplier's
tasks B-PA1 and B-PA2): the PA's drain current is the controlled quantity.
  U551   INA250A2PWR (TI SBOS511C; 2 mOhm integrated shunt, 500 mV/A, system gain error 0.75 % max to 125 C, 15 A continuous to 85 C):
         IN+ (14 to 16) on +13V8_PA, IN- (1 to 3) on the new +13V8_PAJ, which J_PA pin 1 now carries; VIN+ with SH+ and VIN- with
         SH- (no filter, the sheet's pin table); REF to ground; VS on +5V_D8IN; OUT = PA_IMON
  U552   TLV75801PDRVR (TI SBVS351D, the part board D's U15 is) as the set point PA_ISET: R551 2.80k over R552 549 Ohm at 0.1 % 25 ppm/K,
         3.3551 V nominal with a 1.0 mA preload (the sheet's IOUT = 1 mA accuracy test condition); C552 1 uF in, C553 2.2 uF out
  R559, C557, Q551   the set point's hold and ramp: R559 1k and C557 10 uF from PA_ISET into PA_ISP; Q551 (2N7002, the board's C8545)
         holds PA_ISP at 0 V while OUTLET_OK is high (U30: OUTLET_OK = NOT (TR_APRS AND PA_EN), the PA not keyed), so at each key the set
         point rises from zero (10 ms) and the current approaches the cap from below, the RF drive arriving through K1 (3 ms at most)
         under a low set point
  U553   TLV9062IDGK (TI SBOS839N, board D's U8): half A integrates PA_IMON against PA_ISP (R553 10.0k, C554 10 nF C0G, 0.1 ms); R560 470k from
         +5V_D8IN into its summing node winds it down while the set point is held; half B inverts its output about PA_MID (R554, R555
         10.0k; R556 over R557 10.0k from +5V_D8IN, C556 100 nF), so PA_ILIM_A rests at 0 V while the current is under the set point;
         R558 1k into PA_ILIM, J_MEZZ1 pin 16 (AB_SPARE until now) and TP27, to board D's VGG_FB through R57 (apply_gen_sch_d_paloop.py,
         board D's half, in the SAME release)
  U13    its FB divider R50 162k over R51 10k at 0.1 % (record l8r2's fb01 keyword rfb_tol; values unchanged): 13.483 to 14.040 V;
         its BIAS (pin 24, VCC's supply above 8 V, the gate drive: up to 0.1141 A, l9t5_f01.out section 4) and C195 move from +13V8_PA to
         PA_OUT, ahead of R55, so U13's own average loop reads the PA's feed and microamperes
The cap over every corner (l9t5_paloop.py; MODEL on PRINTED terms with TYPICAL allowances, R553 and R559 at their corners and the
reference's load residual an ASSUMPTION, cx45): 6.3518 to 6.9259 A, 0.1075 A under U13's own loop minimum 7.0338 A with R55 hot
(L9P-F04 PROVISIONAL with the selection); the PA at most 97.24 W; C-ALLTX rev 3 with the printed bounds 15.1308 V on the MODEL.
F01 / D-17 is PROVISIONAL: the 30 W service under the cap's least on B-PA1, the loop's dynamics on B-PA2, the reference at its load on
V-PA-REF (l9t5_f01.out section 6).
What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  1. U13's call: rfb_val="10k 0.1%", rfb_tol="0.1%" (needs fb01's keyword: refused without it) and bias="PA_OUT";
  2. J_PA's pin 1 to +13V8_PAJ and the block above after it (two land keys, TSSOP16 and VSSOP8, the KiCad 9 library's);
  3. +13V8_PA's declaration: its load is U551 and its peak the cap's top, 6.93 A (it was 6.0 A typed, under the case's 8.19 A);
     +13V8_PAJ declared as its series segment; the loop's nets declared as nodes;
  4. +5V_D8IN's loads: U551, U552 and U553 (3.3 mA together, l9t5_paloop.py);
  5. J_MEZZ1 pin 16 and TP27 from AB_SPARE to PA_ILIM; 6. a section for the new parts.
Order: board A's round after record l8r2's fb01 (its keyword) and d8v3 (J_MEZZ1's row; either version of it composes), after record
l9t5's iocbuck and iocpre, and before d8dec31's mainpb (the last next-free taker: the references here, U551 to U553, Q551, R551 to R560
and C551 to C557, sit below the composed board's highest, so mainpb's picks do not move). With apply_gen_sch_d_paloop.py in one release.
Usage:  apply_gen_sch_a_paloop.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or net is in
use, fb01's keyword is absent, or the repository's own generator is named before RELEASE-F01.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_paloop"
ADDS = ("U551", "U552", "U553", "Q551", "R551", "R552", "R553", "R554", "R555", "R556", "R557", "R558", "R559", "R560",
        "C551", "C552", "C553", "C554", "C555", "C556", "C557")
NETS = ("+13V8_PAJ", "PA_SHP", "PA_SHN", "PA_IMON", "PA_ISET", "PA_ISFB", "PA_INTN", "PA_INTO", "PA_MID", "PA_INVN", "PA_ILIM_A", "PA_ILIM", "PA_ISP")
CAP_TOP = 6.93            # A: the cap's top 6.9259 A (l9t5_paloop.py, cx45's corners, MODEL) rounded up; the PA rail's declared peak
VPA_TOP = 14.04           # V: U13's output top with the 0.1 % divider, 14.0397 V rounded up (l9t5_paloop.py)
V5_TOP = 5.14             # V: +5V_D8IN's declared v_work
SUPPLY = {"U551": 0.0003, "U552": 0.0011, "U553": 0.0019}   # A on +5V_D8IN: IQ 300 uA; IGND 35 uA + the 1.0 mA preload; 2 x 800 uA + 257 uA + R560

_OLD_U13 = 'cs_filter=("R152", "R153", "C124"), isns_filter=("R162", "R163", "C129"),'
_NEW_U13 = _OLD_U13 + ' rfb_val="10k 0.1%", rfb_tol="0.1%", bias="PA_OUT",'
_OLD_JPA = 'vh2("J_PA", "13.8 V to the PA module on the face plate (JST-VH, 16 AWG): + -", "+13V8_PA")\n'
_HEAD = ("# F01 / D-17 (L9P-F01, L9P-F04), RECORD l9t5 P0-1 ROUND 2 (MESHSAT-1357, 5 October 2026; v2/docs/records/l9t5/l9t5_f01.out): THE\n"
         "# PA'S DRAIN CURRENT IS CAPPED. C-ALLTX rev 3 needs 16.0718 V with the printed bounds while the PA runs open loop (board D's VGG\n"
         "# 4.30 to 4.68 V; the case takes the 45 W rating at the 40 % minimum, 113 W). U551 (INA250A2, TI SBOS511C) carries the PA's feed\n"
         "# from +13V8_PA to J_PA; U553 half A integrates its output against the set point PA_ISP (U552, a TLV758P at 3.3551 V with a 1 mA\n"
         "# preload, through R559 and C557, held at 0 V by Q551 while OUTLET_OK is high so each key starts from zero), half B inverts it\n"
         "# about PA_MID, so PA_ILIM rests at 0 V under the set point and rises over it; on J_MEZZ1 pin 16 it reaches board D's VGG_FB\n"
         "# through R57 and lowers VGG (board D's half, apply_gen_sch_d_paloop.py, one release). The cap 6.3521 to 6.9258 A over every\n"
         "# corner is under U13's own loop minimum 7.0338 A with U13's BIAS on PA_OUT; the PA at most 97.24 W; the case 15.1308 V with the\n"
         "# printed bounds. The 30 W service under the cap is PROVISIONAL on the supplier's task B-PA1. DRAFTED, not applied.\n")
_PARTS = ('FP.update({"TSSOP16": "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", "VSSOP8": "Package_SO:VSSOP-8_3x3mm_P0.65mm"})   # KiCad 9 library lands\n'
          'ic("U551", 16, "INA250A2PWR current-sense amplifier, 2 mOhm integrated shunt, 500 mV/A: the PA\'s drain current (F01)", "TSSOP16",\n'
          '   {"1": "+13V8_PAJ", "2": "+13V8_PAJ", "3": "+13V8_PAJ", "4": "PA_SHN", "5": "PA_SHN", "6": "GND", "7": "GND", "8": "GND", "9": "PA_IMON",\n'
          '    "10": "+5V_D8IN", "11": "GND", "12": "PA_SHP", "13": "PA_SHP", "14": "+13V8_PA", "15": "+13V8_PA", "16": "+13V8_PA"})\n'
          'c("C551", "100n", "+5V_D8IN", "GND", bypass=("U551", "10"))\n'
          'ic("U552", 7, "TLV75801PDRVR adjustable LDO as the PA current set point PA_ISET, 3.3551 V with a 1 mA preload (F01)", "WSON6",\n'
          '   {"1": "PA_ISET", "2": "PA_ISFB", "3": "GND", "4": "+5V_D8IN", "5": "NC", "6": "+5V_D8IN", "7": "GND"})\n'
          'c("C552", "1u", "+5V_D8IN", "GND", bypass=("U552", "6")); c("C553", "2.2u 16V X5R", "PA_ISET", "GND")\n'
          'r("R551", "2.80k 0.1% 25ppm", "PA_ISET", "PA_ISFB"); r("R552", "549 0.1% 25ppm", "PA_ISFB", "GND")\n'
          'r("R559", "1k", "PA_ISET", "PA_ISP"); c("C557", "10u 16V X7R", "PA_ISP", "GND", "C10u")\n'
          'part("Q551", "Transistor_FET", "2N7002", "2N7002: OUTLET_OK high (the PA not keyed) holds the PA current set point PA_ISP at 0 V (1 G, 2 S, 3 D)", "SOT23", {"1": "OUTLET_OK", "2": "GND", "3": "PA_ISP"}, "C8545")\n'
          'ic("U553", 8, "TLV9062IDGK dual op amp: A integrates the PA current against PA_ISP, B inverts it about PA_MID (F01)", "VSSOP8",\n'
          '   {"1": "PA_INTO", "2": "PA_INTN", "3": "PA_ISP", "4": "GND", "5": "PA_MID", "6": "PA_INVN", "7": "PA_ILIM_A", "8": "+5V_D8IN"})\n'
          'c("C555", "100n", "+5V_D8IN", "GND", bypass=("U553", "8"))\n'
          'r("R553", "10.0k 0.1% 25ppm", "PA_IMON", "PA_INTN"); c("C554", "10n 50V C0G", "PA_INTN", "PA_INTO"); r("R560", "470k", "+5V_D8IN", "PA_INTN")\n'
          'r("R554", "10.0k 0.1% 25ppm", "PA_INTO", "PA_INVN"); r("R555", "10.0k 0.1% 25ppm", "PA_INVN", "PA_ILIM_A")\n'
          'r("R556", "10.0k 0.1% 25ppm", "+5V_D8IN", "PA_MID"); r("R557", "10.0k 0.1% 25ppm", "PA_MID", "GND"); c("C556", "100n", "PA_MID", "GND")\n'
          'r("R558", "1k", "PA_ILIM_A", "PA_ILIM")\n')
_CLS = ('_cls("C551", "R", "TI SBOS511C (INA250) p.1 and the application figures: CBYPASS 0.1 uF at VS")\n'
        '_cls("C552", "R", "TI SBVS351D (TLV758P) 5.3: CIN input capacitor 1 uF minimum")\n'
        '_cls("C555", "R", "TI SBOS839N (TLV906x) layout guidelines: \'Connect low-ESR, 0.1uF ceramic bypass capacitors between each supply pin and ground, placed as close to the device as possible\'")\n')
_DECL = ('_intent.rail("+13V8_PAJ", 13.8, 5.0, %.2f, "U551", loads={"J_PA": %.2f}, series_of="+13V8_PA", converted=False, budget=0.02,\n'
         '             source_ic="U551 is an INA250A2: its IN+ to IN- pins ARE the power path (the 2 mOhm shunt and 4.5 mOhm of package, typical)",\n'
         '             note="the PA\'s feed behind the current-sense amplifier U551 to J_PA (record l9t5 P0-1, F01): the peak is the drain-current '
         'cap\'s top, 6.9259 A on the MODEL band (l9t5_paloop.py: PRINTED terms with TYPICAL allowances and ASSUMPTION residuals), rounded up; F01 / D-17 PROVISIONAL on B-PA1 and B-PA2")\n' % (CAP_TOP, CAP_TOP))
for _n, _b in (("PA_SHP", "U551's VIN+ and SH+ (pins 12, 13), the Kelvin tap at the shunt's supply side: +13V8_PA's top with the 0.1 % divider"),
               ("PA_SHN", "U551's VIN- and SH- (pins 4, 5), the Kelvin tap at the shunt's load side: +13V8_PA's top less the shunt's drop")):
    _DECL += '_intent.node("%s", %.2f, "%s")\n' % (_n, VPA_TOP, _b)
for _n, _v, _b in (("PA_IMON", V5_TOP, "U551's OUT: 500 mV/A, swinging within its supply +5V_D8IN (5.14 V v_work)"),
                   ("PA_ISET", 3.42, "U552's output, 0.55 V x (1 + 2.80k / 549) = 3.3551 V nominal, 3.4114 V at its top corner (MODEL: VFB +1 % at 1 mA, the divider, IFB, line regulation and the load residual, l9t5_paloop.py)"),
                   ("PA_ISP", 3.42, "the integrator's set point: PA_ISET through R559, held at 0 V by Q551 while OUTLET_OK is high, ramped by C557 at each key"),
                   ("PA_ISFB", 0.56, "U552's FB pin, 0.55 V +-1 percent (TI SBVS351D)"),
                   ("PA_INTN", V5_TOP, "U553A's inverting input: at PA_ISP in regulation, within its supply +5V_D8IN while the integrator rests"),
                   ("PA_INTO", V5_TOP, "U553A's output, the integrator: rail to rail on +5V_D8IN"),
                   ("PA_MID", 2.58, "half of +5V_D8IN through R556 over R557"),
                   ("PA_INVN", V5_TOP, "U553B's inverting input: at PA_MID in regulation, within its supply"),
                   ("PA_ILIM_A", V5_TOP, "U553B's output: 0 V at rest, up to +5V_D8IN while the loop lowers VGG"),
                   ("PA_ILIM", V5_TOP, "the loop's output to board D on J_MEZZ1 pin 16 through R558: 0 V at rest, up to +5V_D8IN")):
    _DECL += '_intent.node("%s", %.2f, "%s")\n' % (_n, _v, _b)
_NEW_JPA = _OLD_JPA.replace('"+13V8_PA")', '"+13V8_PAJ")') + _HEAD + _PARTS + _CLS + _DECL
_OLD_RAIL = '_intent.rail("+13V8_PA", 13.8, 5.0, 6.0, "R55", loads={"J_PA": 6.0},'
_NEW_RAIL = '_intent.rail("+13V8_PA", 13.8, 5.0, %.2f, "R55", loads={"U551": %.2f},   # record l9t5 P0-1 (F01): J_PA moves behind U551; the peak is the cap\'s top\n            ' % (CAP_TOP, CAP_TOP)
_OLD_D8 = '_intent.rail("+5V_D8IN", 5.0, 1.0, 2.0, "L13", loads={"U23": 1.0},'
_NEW_D8 = '_intent.rail("+5V_D8IN", 5.0, 1.0, 2.0, "L13", loads={"U23": 1.0, %s},' % ", ".join('"%s": %.4f' % kv for kv in SUPPLY.items())
_OLD_MEZZ = '"15": "ZEROIZE_HW", "16": "AB_SPARE"})'
_NEW_MEZZ = '"15": "ZEROIZE_HW", "16": "PA_ILIM"})'
_OLD_TP = '("TP27", "AB_SPARE")): tp(ref, net)'
_NEW_TP = '("TP27", "PA_ILIM")): tp(ref, net)'
_OLD_SEC = "_listed = {r for _, refs in SECTIONS for r in refs}\n"
_NEW_SEC = ('SECTIONS.append(("PA DRAIN-CURRENT CAP (F01, RECORD l9t5): INA250A2 U551, SET POINT U552, INTEGRATOR AND INVERTER U553", '
            '[%s]))   # record l9t5 P0-1\n' % ", ".join('"%s"' % r for r in ADDS) + _OLD_SEC)
EDITS = [(_OLD_U13, _NEW_U13), (_OLD_JPA, _NEW_JPA), (_OLD_RAIL, _NEW_RAIL), (_OLD_D8, _NEW_D8), (_OLD_MEZZ, _NEW_MEZZ),
         (_OLD_TP, _NEW_TP), (_OLD_SEC, _NEW_SEC)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), text):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), text):
            refuse("net %s already exists in the target" % net)
    for need_ in ('rfb_tol="1%"', "def _cls(", "def vh2("):
        if need_ not in text:
            refuse("the target has no %s (record l8r2's fb01 must be applied first for rfb_tol)" % need_)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:70]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE-F01.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE-F01.md; record l9t5's F01 drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE-F01.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE-F01.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
