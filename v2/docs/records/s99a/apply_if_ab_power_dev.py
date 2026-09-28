#!/usr/bin/env python3
"""FOR THE INTEGRATOR (the one writer of v2/ecad/tools/pcb_interfaces.yaml): IF-AB-POWER's +5V_DEV row and the wall
port's eFuse limit after decision 55 and stream s99a's TPS2596 sign correction (MESHSAT-1357, 28 September 2026).

AI engineering text; prototype design, nothing built or measured. Two replacements: (1) the whole +5V_DEV currents row
(a_declares with the split and the corrected wall limit, b_declares unchanged, status restated: the old text described
the D8 mezzanine at zero with 7.9 and 8.9 A coincident); (2) "limit 0.89 A" on the wall port's usb line.
--check validates that each old text occurs once, that each new text differs, that the result parses as YAML with the
row's three keys, and writes nothing. Without --check it writes the file once and refuses a second run by a marker.
"""
import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
F = "v2/ecad/tools/pcb_interfaces.yaml"
MARKER = Path(__file__).with_name("apply_if_ab_power_dev.applied")

OLD_ROW = '''        - {rail: "+5V_DEV", a_declares: "5.1 A typical, 6.9 A peak at the converter, of which 3.8 A apportioned to J_5V_DEV,
             1.0 A to the D8 mezzanine's eFuse U23 and 0.3 A to the wall port's eFuse U32 (gen_sch_a.py:135)",
           b_declares: "3.8 A typical, 6.0 A peak arriving (gen_sch_b.py:111)",
           status: "AGREE at the lead since S-98 (28 September 2026), INTERIM: A apportions 3.8 A to J_5V_DEV and B declares
             3.8 A typical arriving; the PS-ALLTX mode current is INCONCLUSIVE at both ends (v2/docs/records/cx1/CORRECTION.md
             B2). The converter-side peak is S-99's: A's 6.9 A is B's 6.0 A plus the wall port's 0.9 A with the D8 mezzanine at
             zero, against 7.9 A (D8 at its 1.0 A typical) and 8.9 A (every declared limit) coincident, both above the LM5176
             average loop's minimum. Enable DEV_EN, ON by design since 458b2873 (R42)"}
'''
NEW_ROW = '''        - {rail: "+5V_DEV", a_declares: "4.1 A typical, 6.9142 A peak at the converter, of which 3.8 A apportioned to
             J_5V_DEV and 0.3 A to the wall port's eFuse U32; the peak is B's 6.0 A plus U32's 0.9142 A nominal limit (TPS2596
             equation 7, SLVSET8A p.28). The D8 mezzanine is on its own rail +5V_D8IN from the buck U41 since decision 55
             (gen_sch_a.py, the S-99 lines)",
           b_declares: "3.8 A typical, 6.0 A peak arriving (gen_sch_b.py:111)",
           status: "AGREE at the lead since S-98 (28 September 2026), INTERIM: A apportions 3.8 A to J_5V_DEV and B declares
             3.8 A typical arriving; the PS-ALLTX mode current is INCONCLUSIVE at both ends (v2/docs/records/cx1/CORRECTION.md
             B2). The converter side is S-99's: since decision 55 (stream s99a) the D8 mezzanine no longer loads +5V_DEV, and
             A's 6.9142 A declared peak is 0.142697 A under the LM5176 average loop's conditional minimum of 7.056897 A (43 mV
             over R43 at +1 percent and an assumed 50 K shunt temperature change); the P-tier with B's declared child peaks,
             8.171220 A, is above that minimum and stays open under S-99 (board B's reconciliation of its children, bench
             PT-4). Enable DEV_EN, ON by design since 458b2873 (R42)"}
'''
OLD_WALL = "VBUS_WALL comes from +5V_DEV through A's eFuse U32 (limit 0.89 A), switched and"
NEW_WALL = "VBUS_WALL comes from +5V_DEV through A's eFuse U32 (limit 0.9142 A nominal, TPS2596 equation 7), switched and"
CHANGES = [("IF-AB-POWER +5V_DEV row", OLD_ROW, NEW_ROW), ("IF-AB-WALL usb limit", OLD_WALL, NEW_WALL)]


def _find_row(obj):
    if isinstance(obj, dict):
        if obj.get("rail") == "+5V_DEV" and "a_declares" in obj: return obj
        for v in obj.values():
            r = _find_row(v)
            if r: return r
    elif isinstance(obj, list):
        for v in obj:
            r = _find_row(v)
            if r: return r
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if MARKER.exists():
        raise SystemExit("Refused: already applied or attempted.")
    path = ROOT / F
    orig = path.read_text(encoding="utf-8")
    res = orig
    for name, old, new in CHANGES:
        assert new != old, name
        assert orig.count(old) == 1, (name, "old text must occur exactly once", orig.count(old))
        res = res.replace(old, new, 1)
    assert res != orig
    row = _find_row(yaml.safe_load(res))
    assert row and set(row) == {"rail", "a_declares", "b_declares", "status"}, row
    assert "6.9142" in row["a_declares"] and "U23" not in row["a_declares"] and "7.9 A" not in row["status"]
    assert path.read_text(encoding="utf-8") == orig
    print("PASS: %d replacements, the result parses; the +5V_DEV row keys %s" % (len(CHANGES), sorted(row)))
    if a.check:
        print("CHECK ONLY: no writes, no marker.")
        return
    with MARKER.open("x") as m:
        m.write("applied or attempted\n")
    path.write_text(res, encoding="utf-8")


if __name__ == "__main__":
    main()
