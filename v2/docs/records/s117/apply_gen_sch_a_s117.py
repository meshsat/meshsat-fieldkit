#!/usr/bin/env python3
"""S-117 for board A's generator (stream s117, MESHSAT-1357, 29 September 2026): the charger U3 (BQ25731) takes TI's
400 kHz row. DRAFT for board A's generator owner; the author ran --check only.

What it writes into v2/ecad/tools/gen_sch_a.py (every figure in v2/docs/records/s117/charger_l_f.out; the choice is the
session decision drafted by apply_decision_s117.py):
  L2    3.3uH XAL6030-332ME on the XAL60xx land  ->  4.7uH XAL1010-472ME (Isat 25.4 A) on the XAL1010 land ("L1010")
  R25   10k        ->  40.2k 1%   (TI's COMP1 R1; the value R27 already carries, C12447)
  C26   10n        ->  4.7n       (TI's COMP1 C11)
  C234  new, 33p (C0G, C1663), CH_COMP1 to GND        (TI's COMP1 C12)
  R220  new, 15k 1% (C22809), CH_COMP2 to CH_COMP2C   (TI's COMP2 R2)
  C235  new, 680p (C0G, C30816), CH_COMP2C to GND     (TI's COMP2 C21)
  C27   1n         ->  15p NP0    (TI's COMP2 C22, CH_COMP2 to GND as before)
  R219  new, 191k 1%, IADPT to GND                    (Table 9-4, 4.7 uH)
  C233  new, 33p (C0G, C1663), IADPT to GND           (the pin table's 100 pF or less)
and the five new references into the charger's sheet section. TI SLUSE66A: 9.3.11 and Table 9-4 (printed page 27), the
pin table (page 6), 8.5 CIADPT_MAX (page 12), 9.3.12, Table 9-5 and Figure 9-2 (pages 27 and 28).

HOW IT GUARDS. Each old text must occur exactly once and differ from its new text; the five new references must not
occur anywhere in the generator before (read from the parsed source, never by pattern); the result must parse (ast) and
must carry each expected r(), c() and part() call exactly once with the expected value and nets (read from the parsed
calls); --check does all of it in memory and writes nothing; the write path creates an exclusive marker beside this file
first, so a second run refuses. The owner regenerates board A on the KiCad box afterwards and runs readback_s117.py on
the regenerated netlist before anything is committed.

Usage (repository root or anywhere in the tree): python3 apply_gen_sch_a_s117.py [--check]"""
import argparse, ast, hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
GEN = os.path.join(TOP, "v2/ecad/tools/gen_sch_a.py")
MARKER = os.path.join(HERE, "apply_gen_sch_a_s117.applied")
NEW_REFS = ("R219", "R220", "C233", "C234", "C235")

L2_OLD = 'part("L2", "Device", "L", "3.3uH XAL6030-332ME (Isat 12.2 A)", "L6060", {"1": "CH_SW1", "2": "CH_SW2"})\n'
L2_NEW = '''# S-117 (stream s117, 29 September 2026, MESHSAT-1357; the S-117 session decision in tools/pcb_decisions.yaml): THE
# CHARGER RUNS TI'S 400 kHz ROW ON A 4.7 uH XAL1010. The BQ25731 reads its switching frequency and its inductance from
# the resistor on IADPT before it starts (SLUSE66A 9.3.11 and Table 9-4, printed page 27). The 3.3 uH XAL6030-332ME drawn
# here until today (Isat 12.2 A, Irms 6.0 / 8.0 A at 20 / 40 C rise, 20.81 mOhm maximum; Coilcraft 887-1) sits under the
# charger's own input bound: the front end's 5.7 A at 20.7 V into a pack at its 10.0 V CUV puts 11.8 A through this
# inductor, where it fails SLUSE66A Equation 2 (ISAT >= ICHG + IRIPPLE / 2, page 85) at either row and runs at 148
# percent of its 40 C rise current (103 percent already with the pack at its 14.4 V nominal). The XAL1010-472ME (4.7 uH,
# Isat 25.4 A, Irms 17.5 / 24.0 A, 5.70 mOhm maximum; Coilcraft 804-1), on the land L1 and L8 already use, peaks at 14.1
# A worst at that bound (L at -20 percent with its fall, 340 kHz) and carries 49 percent of its 40 C rise current.
# 400 kHz and not 800 kHz: with the drawn CSD18510Q5B FETs (about 75 nC of gate charge at 6 V, SLPS632 Figure 4) the
# gate drive at 800 kHz asks 93 to 120 mA of REGN, whose current limit is 50 mA minimum (8.5, page 11), and every
# switching term doubles; and 400 kHz is PWM_FREQ's power-on value (Table 9-8, page 43), so the resistor, the register
# and the compensation agree before any host write. C121's 10 nF is the CDIFF 10.2.2.2 asks for at 400 kHz. Every figure:
# v2/docs/records/s117/charger_l_f.out. LAYOUT, OWED: the XAL1010 body is 11.3 x 10.0 mm and 10.0 mm tall where the
# XAL60xx seat of gen_pcb_a3.py's CHQ row was sized for a 7.15 x 7.35 mm courtyard, so board A's layout writer re-seats
# L2 in the charger's row (with S-115's pass), and seats R219, R220 and C233 to C235 with the charger's passives.
part("L2", "Device", "L", "4.7uH XAL1010-472ME (Isat 25.4 A)", "L1010", {"1": "CH_SW1", "2": "CH_SW2"})
'''

COMP_OLD = ('; r("R25", "10k", "CH_COMP1", "CH_COMP1C"); c("C26", "10n", "CH_COMP1C", "GND"); '
            'c("C27", "1n", "CH_COMP2", "GND")\n')
COMP_NEW = '''
# S-117 (29 September 2026): THE COMPENSATION AND THE INDUCTANCE RESISTOR OF TI'S 400 kHz ROW. SLUSE66A 9.3.12 and Table
# 9-5 (printed page 27), the row for 4.7 uH at 400 kHz, drawn as Figure 9-2 draws it (page 28; its names R1, C11, C12,
# R2, C21 and C22 are TI's, not this board's references): COMP1 = R1 40.2 kOhm in series with C11 4.7 nF to ground, and
# C12 33 pF from the pin to ground; COMP2 = R2 15 kOhm in series with C21 680 pF, and C22 15 pF from the pin to ground. "It is not recommended to change the compensation network value due to the
# complexity of various operation modes." Here R25 and C26 are R1 and C11, C234 is C12, R220 and C235 are R2 and C21, and
# C27 is C22 (TI's names on the right). Until today they were 10k with 10 nF (no C12) and 1 nF alone, the values of neither row (round 4's O-24).
r("R25", "40.2k 1%", "CH_COMP1", "CH_COMP1C"); c("C26", "4.7n", "CH_COMP1C", "GND"); c("C234", "33p", "CH_COMP1", "GND")
r("R220", "15k 1%", "CH_COMP2", "CH_COMP2C"); c("C235", "680p", "CH_COMP2C", "GND", lcsc="C30816"); c("C27", "15p NP0", "CH_COMP2", "GND")
# IADPT (pin 8): 9.3.11 and Table 9-4, 191 or 187 kOhm for 4.7 uH, and "A surface mount chip resistor with +/-3% or better
# tolerance must to be used for an accurate inductance detection": 191k at 1 percent and 100 ppm/C stays inside 3 percent
# from -40 to +85 C (1 plus 0.65 percent). The pin table (page 6) asks "a 100-pF or less ceramic decoupling capacitor
# from IADPT pin to ground" and 8.5 gives CIADPT_MAX 100 pF (page 12): 33 pF C0G, C234's part, stays under it with its 5
# percent and the land's few picofarads. TP19 stays on the net; nothing on this board reads IADPT as a current monitor.
r("R219", "191k 1%", "IADPT", "GND"); c("C233", "33p", "IADPT", "GND")
'''

SEC_OLD = '"R25", "C26", "C27", "R26", "R27"]),'
SEC_NEW = '"R25", "C26", "C234", "R220", "C235", "C27", "R219", "C233", "R26", "R27"]),'

CHANGES = [("S117-L2", L2_OLD, L2_NEW), ("S117-COMP-IADPT", COMP_OLD, COMP_NEW), ("S117-SECTION", SEC_OLD, SEC_NEW)]

# (function, reference) -> the positional arguments after the reference, as the parsed call must carry them
EXPECT = {
    ("part", "L2"): ["Device", "L", "4.7uH XAL1010-472ME (Isat 25.4 A)", "L1010", {"1": "CH_SW1", "2": "CH_SW2"}],
    ("r", "R25"): ["40.2k 1%", "CH_COMP1", "CH_COMP1C"],
    ("c", "C26"): ["4.7n", "CH_COMP1C", "GND"],
    ("c", "C234"): ["33p", "CH_COMP1", "GND"],
    ("r", "R220"): ["15k 1%", "CH_COMP2", "CH_COMP2C"],
    ("c", "C235"): ["680p", "CH_COMP2C", "GND"],
    ("c", "C27"): ["15p NP0", "CH_COMP2", "GND"],
    ("r", "R219"): ["191k 1%", "IADPT", "GND"],
    ("c", "C233"): ["33p", "IADPT", "GND"],
}


def refuse(m):
    print("apply_gen_sch_a_s117: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b.encode("utf-8")).hexdigest()[:16]


def string_constants(tree):
    return {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def calls(tree):
    """{(function name, first argument): [the parsed calls]} for every call whose first argument is a string."""
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.args and isinstance(n.args[0], ast.Constant) \
                and isinstance(n.args[0].value, str):
            out.setdefault((n.func.id, n.args[0].value), []).append(n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate every anchor and the result in memory; write nothing")
    a = ap.parse_args()
    if not a.check and os.path.exists(MARKER): refuse("the marker %s exists (a second run)" % os.path.basename(MARKER))
    src = open(GEN, encoding="utf-8").read()
    before = ast.parse(src)
    have = string_constants(before)
    taken = [r for r in NEW_REFS if r in have]
    if taken: refuse("the generator already names %s" % ", ".join(taken))
    if "XAL1010-472ME" in have: refuse("the generator already draws an XAL1010-472ME")
    out = src
    for cid, old, new in CHANGES:
        if old == new: refuse("%s: the new text equals the old" % cid)
        n = out.count(old)
        if n != 1: refuse("%s: the old text occurs %d times, not once" % (cid, n))
        out = out.replace(old, new)
    after = ast.parse(out)
    got = calls(after)
    for (fn, ref), args in EXPECT.items():
        cs = got.get((fn, ref), [])
        if len(cs) != 1: refuse("%s(%r, ...) occurs %d times after the change, not once" % (fn, ref, len(cs)))
        vals = [ast.literal_eval(x) for x in cs[0].args[1:1 + len(args)]]
        if vals != args: refuse("%s(%r, ...) reads %r, not %r" % (fn, ref, vals, args))
    print("apply_gen_sch_a_s117: gen_sch_a.py sha256/16 %s -> %s; %d changes; L2, R25, C26, C27 changed; R219, R220, "
          "C233, C234, C235 new; every expected call read back from the parsed source" % (sha16(src), sha16(out), len(CHANGES)))
    if a.check:
        print("CHECK ONLY: 3 anchors, 9 calls read back, 1 generator; no writes, no marker.")
        return 0
    fd = os.open(MARKER, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, ("gen_sch_a.py %s -> %s\n" % (sha16(src), sha16(out))).encode())
    os.close(fd)
    open(GEN, "w", encoding="utf-8").write(out)
    if open(GEN, encoding="utf-8").read() != out: refuse("the written file differs from the text validated")
    ast.parse(open(GEN, encoding="utf-8").read())
    print("APPLIED: v2/ecad/tools/gen_sch_a.py written once; marker %s. Next: regenerate board A (schematic phase) on the "
          "box and run readback_s117.py on its netlist." % os.path.basename(MARKER))
    return 0


if __name__ == "__main__":
    sys.exit(main())
