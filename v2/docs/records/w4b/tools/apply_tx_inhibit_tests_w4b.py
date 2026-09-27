#!/usr/bin/env python3
"""Stream w4b (MESHSAT-1357, 27 September 2026): the three test changes that go WITH apply_tx_inhibit_w4b.py, for the owner
of v2/ecad/tools/tests/test_tx_inhibit.py. Usage: apply_tx_inhibit_tests_w4b.py <path to test_tx_inhibit.py> [--check]

  1. t_a_compute_modules_5v_is_a_load_only_with_gpio_vref_on_its_own_outputs pinned the tool's own gap: "the walk holds no
     pin map for that part [the SN74LVC2G06], so each supply pin is named as a part no class reads". With the row the
     draft adds, U113 to U115 are read as the SN74LVC2G06 they are and the sources on +3V3_CM1 are the six pulls of the
     eleventh and twelfth passes again (checked on stream w4b's regenerated board B netlist).
  2. t_a_declaration_resting_on_an_inference_leaves_its_board_undecided tests the OWED mechanism through the J_QMX row
     OWED carried; the draft moves J_QMX to ACCESSORIES (QRP Labs' schematics answer it, EMCON.md 4.3), so the test passes
     its own OWED row and keeps testing what it names.
  3. t_a_high_held_at_a_schmitt_input_is_not_read_as_passing allowed vih_gap on the two Schmitt families only; the
     SN74LV1T08 row carries one too, for its VIH of 2.03 V and 2.11 V above VIH_HIGH at VCC 4.5 V to 5.5 V (SCLS739F 6.5).
Every edit asserts the text it replaces."""
import sys, ast

EDITS = [
 ("5V sources", '''    assert sorted(x.split(" pin ")[0] for x in src) == ["R111", "R151", "R154", "R155", "R156", "R157",
                                                        "U113", "U114", "U115"], src
    assert all(x.endswith("'+3V3_CM1'), a part no class here reads") for x in src if x.startswith("U11")), src''',
  '''    # *changed with stream w4b's rows (27 September 2026): the SN74LVC2G06 has its row (SCES307J), so U113 to U115 are read
    # as the open drains they are and only the six pulls of the eleventh and twelfth passes remain*
    assert sorted(x.split(" pin ")[0] for x in src) == ["R111", "R151", "R154", "R155", "R156", "R157"], src'''),
 ("OWED test", '''    nl = _nl({"J_QMX": ("QMX USB lead (bank 2 hub, port 4)", "Connector:X", "X:Y")}, {"GND": [("J_QMX", "1", "")]})
    r = T.judge({"B": nl}, table=[], accessories=[], receivers=[])''',
  '''    nl = _nl({"J_QMX": ("QMX USB lead (bank 2 hub, port 4)", "Connector:X", "X:Y")}, {"GND": [("J_QMX", "1", "")]})
    # stream w4b: J_QMX left the tree's OWED list (QRP Labs' schematics answer it, EMCON.md 4.3), so the row is passed here
    owed = [dict(board="B", ref="J_QMX", value=r"QMX USB lead", why="the QMX's USB data lead",
                 owed="a QRP Labs statement that USB VBUS does not power the QMX's transmitter")]
    r = T.judge({"B": nl}, table=[], accessories=[], receivers=[], owed=owed)'''),
 ("vih_gap rows", '''    assert "DS35124" in row17["vih_gap"] and all(not f.get("vih_gap") for f in T.LOGIC
                                                 if f["name"] not in ("74LVC1G17 Schmitt buffer", "74LVC1G57 configurable gate"))''',
  '''    # stream w4b: the SN74LV1T08 states VIH 2.03 V and 2.11 V at VCC 4.5 V to 5.5 V (SCLS739F 6.5), above VIH_HIGH
    assert "DS35124" in row17["vih_gap"] and all(not f.get("vih_gap") for f in T.LOGIC
                                                 if f["name"] not in ("74LVC1G17 Schmitt buffer", "74LVC1G57 configurable gate",
                                                                      "74LV1T08 AND"))'''),
]


def main(a):
    if not a:
        print(__doc__); return 2
    p = a[0]; check = "--check" in a
    s = open(p, encoding="utf-8").read(); o = s; bad = []
    for name, old, new in EDITS:
        n = s.count(old); print("%-12s anchor found %d time(s)" % (name, n))
        if n != 1: bad.append(name); continue
        if not check: s = s.replace(old, new, 1)
    if bad:
        print("REFUSED: %s" % bad); return 1
    if check: return 0
    assert s != o; ast.parse(s); open(p, "w", encoding="utf-8").write(s); print("applied to %s" % p); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
