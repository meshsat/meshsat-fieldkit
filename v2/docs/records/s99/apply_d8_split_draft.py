#!/usr/bin/env python3
"""UNEXECUTED DRAFT for board A's generator owner: option B of v2/docs/records/s99/ANALYSIS.md section 5.

The D8 mezzanine's 5 V leaves the +5V_DEV LM5176 stage for its own TPS62933 buck from VBAT (U41, L13, C227 to C232,
R217, R218; the part, land and capacitor types board A already fits as U12 and U33), and U23 keeps its role as the
mezzanine's eFuse (2.0 A limit, OVLO, D8_EN) fed from the new rail +5V_D8IN. The +5V_DEV declaration drops U23 from
its loads (typical 4.1 A = board B's 3.8 A interim plus the wall port's 0.3 A; peak 6.9 A = B 6.0 + wall 0.9, which
is what the line already says and now becomes true). VBAT's load map takes U41 at 0.4 A typical.

Prototype design, AI engineering analysis. Only --check is run by the author: it validates every anchor occurs once,
that each replacement changes the text, that the whole result parses with ast, and writes nothing. The application
path (no flag) writes the generator once and refuses a second run by an exclusive marker; the owner regenerates
board A on the KiCad box afterwards and reads the intent, the netlist and ERC before anything is committed.

CONFLICT: entry S99-DEV below targets the same line as v2/docs/records/cx1/apply_declarations_draft.py's B2-A-DEV.
Apply one or the other, never both; if cx1's ran first, replace its result line by hand as the comment there says.

Values (ANALYSIS.md section 2): TI SLUSEA4D Table 10-2, 5 V at 500 kHz: 52.5k / 10k, 6.8 uH, 10 uF minimum effective
COUT; 53.6k / 10k (5.088 V, the same figure as the LM5176 stages, both resistors certified on this board) is used so the
eFuse's OVLO arithmetic in the U23 comment is unchanged. Coilcraft 887-1: XAL6060-682ME 6.8 uH, Isat 9.2 A, above the
TPS62933's 5.8 A maximum high-side limit (SLUSEA4D), Irms 7.0 A at 20 K. The XAL6060 order code is the parts stream's
to certify (none is fitted on board A today; the land L6060 exists in the footprint map).
"""
import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
GEN = "v2/ecad/tools/gen_sch_a.py"

NEW_STAGE = '''# S-99 (stream s99, 28 September 2026, MESHSAT-1357; ANALYSIS.md section 5 option B, decision 55): THE D8 MEZZANINE
# LEAVES THE DEVICE RAIL FOR ITS OWN 5 V BUCK FROM VBAT. In PS-ALLTX the exciter keys with the PA, and the mezzanine's
# 1.4 to 2.0 A on +5V_DEV, with board B's 5.4 to 7.2 A and the wall port's 0.5 to 0.9 A, put the LM5176 stage's
# coincident demand (7.3 A with the makers' figures, 8.9 A at every declared limit) above its average loop's minimum
# of 7.06 A (43 mV over 6 mOhm at +1 percent and a hot shunt, SNVSAI1D p.7): the loop would fold the device rail back
# during the key-down. Raising the shunt is not open: 6 mOhm keeps the loop's maximum (9.6 A) under the JST-VH lead's
# 10 A. So the mezzanine takes the part this board already fits twice (U12, U33): a TPS62933DRLR (SLUSEA4D, 3.8 to
# 30 V in, 3 A, IHS_LIMIT 4.2 A minimum) at 5.088 V (53.6k over 10k, the LM5176 stages' figure, so U23's OVLO
# arithmetic stands), 6.8 uH XAL6060-682ME (Table 10-2's value for 5 V at 500 kHz; Isat 9.2 A over the part's 5.8 A
# maximum high-side limit, Coilcraft 887-1), two 22 uF 10 V 1210 (about 30 uF effective at 5 V, over the 10 uF
# minimum), RT open (500 kHz), SS 10 nF (TI's minimum is 6.8 nF), EN on RAIL_EN as U12: the buck is up whenever the
# 3.3 V logic is, and U23 (D8_EN, ILM 2.0 A, OVLO 5.87 to 6.12 V) still switches and protects the mezzanine. At 2.0 A
# the ripple is 1.04 A at 16.8 V in and the peak 2.5 A. The device rail's coincident demand returns to board B plus
# the wall port: 6.9 A declared, 5.9 A with the makers' figures, under the loop's minimum.
ic("U41", 8, "TPS62933DRLR 3 A buck, 5.0 V for the D8 mezzanine", "SOT583", {"1": "NC", "2": "RAIL_EN", "3": "VBAT", "4": "GND", "5": "D8B_SW", "6": "D8B_BST", "7": "D8B_SS", "8": "D8B_FB"}, "C3200405")
part("L13", "Device", "L", "6.8uH XAL6060-682ME (Isat 9.2 A)", "L6060", {"1": "D8B_SW", "2": "+5V_D8IN"})
c("C227", "100n", "D8B_BST", "D8B_SW"); c("C228", "10n", "D8B_SS", "GND")
c("C229", "10u 25V 1210", "VBAT", "GND", "C1210", bypass=("U41", "3")); c("C230", "100n", "VBAT", "GND", bypass=("U41", "3"))
for _ci in ("C229", "C230"): _cls(_ci, "R", "TI SLUSEA4D (TPS62933) 12.1 p.40: 'the most critical PCB feature is the loop formed by the input capacitors and power ground'; 'Place a 0.1-uF ceramic decoupling capacitor or capacitors as close as possible to VIN and GND pins'")
c("C231", "22u 10V X7R 1210", "+5V_D8IN", "GND", "C1210"); c("C232", "22u 10V X7R 1210", "+5V_D8IN", "GND", "C1210")
r("R217", "53.6k 1%", "+5V_D8IN", "D8B_FB"); r("R218", "10k 1%", "D8B_FB", "GND")
_intent.rail("+5V_D8IN", 5.0, 1.0, 2.0, "L13", loads={"U23": 1.0}, switch="U41", efficiency=0.90, fed_from="VBAT", budget=0.02,
             note="S-99, 28 September 2026: the D8 mezzanine's own 5.088 V from VBAT (U41, a TPS62933 at 500 kHz), between the "
                  "buck's inductor L13 and the eFuse U23; 1.0 A typical (board D's +5V_D8 declaration), 2.0 A peak (U23's limit). "
                  "It was a load of +5V_DEV until today, where it put the LM5176 stage's coincident PS-ALLTX demand above the "
                  "average loop's minimum (v2/docs/records/s99/ANALYSIS.md)")
_intent.node("D8B_SW", 16.8, "the D8 buck U41's switching node: it swings to VBAT, the pack node that feeds it, and a diode drop below ground", v_min=-1.0)
_intent.node("D8B_BST", _intent.net_volts("D8B_SW") + _TPS62933_BST,
             "the D8 buck U41's bootstrap supply (pin 6 BST): it rides on D8B_SW at up to 5.5 V, SLUSEA4D 8.3's "
             "recommended BST-SW maximum, and supplies only the part's own high-side driver",
             rides_on="D8B_SW", bias_v=_TPS62933_BST)
'''

CHANGES = [
    {
        "id": "S99-DEV",
        "old": '_intent.rail("+5V_DEV", 5.0, 4.0, 6.9, "R43", loads={"J_5V_DEV": 3.2, "U23": 0.5, "U32": 0.3},',
        "new": '# S-99 (28 September 2026): the D8 mezzanine left this rail for its own buck U41 (decision 55), so the loads are the\n'
               '# lead to B (3.8 A, board B\'s typical arriving, S-98 interim) and the wall port; the 6.9 A peak is B 6.0 + wall 0.9.\n'
               '_intent.rail("+5V_DEV", 5.0, 4.1, 6.9, "R43", loads={"J_5V_DEV": 3.8, "U32": 0.3},',
    },
    {
        "id": "S99-VBAT",
        "old": '"Q32": 2.0, "Q11": 1.5,',
        "new": '"Q32": 2.0, "U41": 0.4, "Q11": 1.5,',
    },
    {
        "id": "S99-STAGE",
        "old": 'efuse("U23", "+5V_DEV", "+5V_D8", "D8_EN", "D8_FLT", ["C102", "R98", "R99", "R100", "R101", "C103"], "453R 1% (ILM: 2.0 A)", ovlo_top="40.2k 1%", ovlo_lcsc="C12447"); vh2("J_MEZZ_PWR1", "D8 mezzanine 5 V (JST-VH): + -", "+5V_D8")',
        "new": NEW_STAGE + 'efuse("U23", "+5V_D8IN", "+5V_D8", "D8_EN", "D8_FLT", ["C102", "R98", "R99", "R100", "R101", "C103"], "453R 1% (ILM: 2.0 A)", ovlo_top="40.2k 1%", ovlo_lcsc="C12447"); vh2("J_MEZZ_PWR1", "D8 mezzanine 5 V (JST-VH): + -", "+5V_D8")',
    },
    {
        "id": "S99-POWERNETS",
        "old": '"VMON", "VHEAT", "+5V_D8", "PD_VBUS",',
        "new": '"VMON", "VHEAT", "+5V_D8", "+5V_D8IN", "PD_VBUS",',
    },
    {
        "id": "S99-SECTION",
        "old": '"J_HEAT", "U23", "C102", "R98", "R99", "R100", "R101", "C103", "J_MEZZ_PWR1"]),',
        "new": '"J_HEAT", "U41", "L13", "C227", "C228", "C229", "C230", "C231", "C232", "R217", "R218", "U23", "C102", "R98", "R99", "R100", "R101", "C103", "J_MEZZ_PWR1"]),',
    },
]
MARKER = Path(__file__).with_name("apply_d8_split_draft.applied")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = parser.parse_args()
    if MARKER.exists():
        raise SystemExit("Refused: this draft has already been applied or attempted.")
    path = ROOT / GEN
    original = path.read_text()
    result = original
    messages = []
    for change in CHANGES:
        old, new = change["old"], change["new"]
        assert old and new != old, "Replacement must change nonempty old text"
        assert original.count(old) == 1, (change["id"], "old text must occur exactly once in the original")
        assert result.count(old) == 1, (change["id"], "old text must occur exactly once at replacement")
        result = result.replace(old, new, 1)
        messages.append("PASS %s: %s: exact old text occurs once" % (change["id"], GEN))
    assert result != original, "no effective change"
    ast.parse(result, filename=GEN)
    for ref in ("U41", "L13", "C227", "C228", "C229", "C230", "C231", "C232", "R217", "R218"):
        assert original.count('"%s"' % ref) == 0, (ref, "already used in the generator; renumber the draft")
    assert path.read_text() == original, "file changed during validation"
    messages.append("PASS AST: %s: replaced text parses; the ten new references are unused in the original" % GEN)
    if args.check:
        print("\n".join(messages))
        print("CHECK ONLY: %d entries, 1 generator; no writes, no marker." % len(CHANGES))
        return
    with MARKER.open("x") as marker:
        marker.write("Draft attempted. Do not run again.\n")
    path.write_text(result)


if __name__ == "__main__":
    main()
