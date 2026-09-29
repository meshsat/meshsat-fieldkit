#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357), finding D4E-F1: a DRAFT circuit change for board C's generator, for board C's author to
review, apply, regenerate on the KiCad box and re-take. It is NOT applied by this stream (WORKER-RULES: a circuit change is
drafted as an apply script for the generator's owner).

THE FINDING. With board C's +3V3 anywhere in 0 to 1.65 V while board B's +3V3_DEV is up (EMCON.md section 5a, fault F6)
and the toggle at EMCON, U9 (Diodes 74LVC1G17, DS35124 Rev. 8-2) is outside its specified supply range, so its output
on EMCON_HW is unspecified up to its own supply, 1.65 V. Board B's readers of EMCON_HW (SN74LVC1G08, SN74LVC1G04,
74LVC1G34 at VCC 3 to 3.6 V: VIL 0.8 V; SN74LV1T08 at VCC 4.5 to 5.5 V: VIL 0.8 V) cannot be shown to read that LOW,
and every board B row (4 to 17) reads EMCON_HW alone. Boards A and D are not affected: A's gates read TX_INHIBIT_n as
well, and D reads TX_INHIBIT_n only, which the toggle's contact grounds whatever board C's rail does.

THE CHANGE (taken by the session under the owner's standing rule of 26 September 2026; reversible by deleting R52 and
D23 and returning U9 pin 4 to EMCON_HW):
  - U9 pin 4 drives a new local net EMCON_HW_DRV; R52, 330R 1 percent (UniRoyal 0603WAF3300T5E, LCSC C23138, the
    lcsc_fill.py table's 330R code), joins it to EMCON_HW;
  - D23, a BAT46W-7-F Schottky (Diodes DS30044 Rev. 20-2, v2/vendor/diodes/diodes-bat46w.pdf, LCSC C83152, the part
    board A already carries), anode on EMCON_HW, cathode on TX_INHIBIT_n.
  So EMCON_HW can never sit more than one Schottky drop above TX_INHIBIT_n, whatever U9 does. With the toggle at EMCON the
  contact holds TX_INHIBIT_n at 0 V and EMCON_HW at most at VF: U9 unspecified at VCC up to 1.65 V pushes at most
  1.65 V / 326.7 Ohm = 5.1 mA through R52 (330R at -1 percent), and VF is at most 0.45 V at 10 mA (DS30044, 25 C row;
  no row over temperature is stated, so the cold end is INFERRED), under B's 0.8 V VIL and under the 0.578 V the LVC1G
  inputs have at their own 1.65 V band edge. A U9 output stuck high (SD-EMC-6's shared-element case) pushes at most
  3.465 V / 326.7 Ohm = 10.6 mA, just over the 10 mA row (INFERRED about 0.46 V): the clamp also turns that fault, which
  released every board B row as drawn, into an asserted EMCON_HW, and the lamp then lights (both lines LOW at board C).
  Released, EMCON_HW is at least 2.4 V (DS35124 VOH at -16 mA, VCC 3.0 V; the load is under 1 mA) x 3.165 k /
  (3.165 k + 0.333 k), less the readers' 111 uA x 333 Ohm: 2.13 V, over the 2.0 V VIH of every reader; the diode is
  reverse biased or carries under about 0.2 mA there (TX_INHIBIT_n rests at 2.37 to 2.57 V, EMCON.md 4b). The unpowered
  hold (L2): with board C off the diode can only move current from EMCON_HW into TX_INHIBIT_n, and its bound is the two
  lines merged by an ideal diode: the stated pin currents of both lines (111.2 uA and 31.1 uA, EMCON.md 4b and this
  stream's fault_levels.py L-TXI-2) into both pull-down networks in parallel (R58 4.7 k 1 percent, R102 10 k 1 percent;
  R50 10 k 1 percent and the three 100 k), about 142 uA into about 2.2 k, 0.32 V, under every reader's 0.8 V VIL; the
  owner re-takes it with the instrument. The assert latency gains nothing (the diode pulls EMCON_HW down with the
  contact).

WHAT THE OWNER STILL DOES after running this: regenerate board C on the box (gen_sch_c.py, the C pipeline) and read the
netlist difference (2 parts added, 1 net added, U9 pin 4 moved); settle the PWR-001 kind of EMCON_HW_DRV if the
generator's completeness test asks for it; re-take RF-002 (tools/tx_inhibit.py must read R52 as the line's series
resistor and D23 as a clamp to the other line: if its walk refuses them, that is a tools item, not a circuit one) and the
suite; add C's +3V3 held in its band with the toggle at EMCON to bench E-11.

The script asserts every anchor is present exactly once, that the new text differs, re-parses the file with ast, and
refuses a second run (EMCON_HW_DRV already present).

usage: apply_c_d4e_f1.py <worktree root>"""
import ast, os, sys

ANCHOR_U9 = '"4": "EMCON_HW", "5": "+3V3"}, "C151394")'
NEW_U9 = '"4": "EMCON_HW_DRV", "5": "+3V3"}, "C151394")'
ANCHOR_C25 = 'c("C25", "100n", "+3V3", "GND")\n'
INSERT = ANCHOR_C25 + '''# EMCON_HW CANNOT SIT ABOVE TX_INHIBIT_n BY MORE THAN ONE SCHOTTKY DROP (stream d4emcon, finding D4E-F1, 29 September 2026;
# taken by the session under the owner's standing rule of 26 September 2026). With this board's +3V3 in 0 to 1.65 V and the toggle
# at EMCON, U9 is outside its specified supply and its output is unspecified up to 1.65 V, which board B's readers (VIL 0.8 V)
# cannot be shown to read LOW; every board B row reads EMCON_HW alone. R52 (330R 1%) limits what U9 can push, and D23 (BAT46W,
# anode EMCON_HW, cathode TX_INHIBIT_n) clamps EMCON_HW to the contact: at most 5.1 mA in the band and VF 0.45 V at 10 mA (Diodes
# DS30044 Rev. 20-2, 25 C). Released, EMCON_HW is at least 2.13 V (U9's VOH 2.4 V at -16 mA into 3.165 k through 333 Ohm), over
# VIH 2.0 V. A U9 stuck high now asserts EMCON_HW instead of releasing board B. Reverse: delete R52 and D23, U9 pin 4 on EMCON_HW.
r("R52", "330R 1%", "EMCON_HW_DRV", "EMCON_HW", "R", "C23138")
part("D23", "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (EMCON_HW clamp to TX_INHIBIT_n, D4E-F1)", "SOD123", {"1": "TX_INHIBIT_n", "2": "EMCON_HW"}, "C83152")
'''
ANCHOR_SEC = '"U9", "U12", "C39", "U13", "C40", "R46", "R50", "R51", "JP2"]'
NEW_SEC = '"U9", "U12", "C39", "U13", "C40", "R46", "R50", "R51", "R52", "D23", "JP2"]'


def main(argv):
    if len(argv) != 1:
        print(__doc__); return 2
    p = os.path.join(argv[0], "v2/ecad/tools/gen_sch_c.py")
    old = open(p, encoding="utf-8").read()
    if "EMCON_HW_DRV" in old:
        print("refused: EMCON_HW_DRV is already in %s (a second run)" % p); return 1
    for a in (ANCHOR_U9, ANCHOR_C25, ANCHOR_SEC):
        n = old.count(a)
        if n != 1:
            print("refused: anchor found %d times, not once: %r" % (n, a[:80])); return 1
    new = old.replace(ANCHOR_U9, NEW_U9).replace(ANCHOR_C25, INSERT).replace(ANCHOR_SEC, NEW_SEC)
    assert new != old
    assert new.count('r("R52"') == 1 and new.count('part("D23"') == 1 and new.count("EMCON_HW_DRV") == 2
    ast.parse(new)
    open(p, "w", encoding="utf-8").write(new)
    ast.parse(open(p, encoding="utf-8").read())
    print("applied D4E-F1 to %s: U9 pin 4 on EMCON_HW_DRV, R52 330R 1%%, D23 BAT46W; regenerate board C on the box next" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
