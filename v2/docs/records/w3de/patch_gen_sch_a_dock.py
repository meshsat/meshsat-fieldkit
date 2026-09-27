#!/usr/bin/env python3
"""DRAFT for board A's stream (v2/ecad/tools/gen_sch_a.py): board A's half of the EQ-16 / R8E-N01 decision (w3de,
27 September 2026, MESHSAT-1357). Board E's half is drawn in gen_sch_e.py (J_BLK, P_VR, P_VN); the record is
drafts/w3de/EQ16-dock-vin-raw.md and the arithmetic drafts/w3de/dock_contacts.py.

THE DECISION (session, under the owner's standing rule of 26 September 2026): VIN_RAW crosses the dock on four Mill-Max
0858-class power pins with four more for its return, as the pack's CELL+ does, and the four Preci-Dip 813 contacts that
carried it (J_DOCK 1 to 4) become GND. On board A:
  1. J_VR1 to J_VR4 on VIN_RAW and J_VN1 to J_VN4 on GND, each the MMPIN land J_CP and J_CN use;
  2. J_DOCK pins 1 to 4 from VIN_RAW to GND, and its value says so;
  3. VIN_RAW's declared source becomes the four power pins (a list: the current enters at all four);
  4. R8E-N01: VIN_RAW's figure from 12.31 A (6.15 + 6.16, board E's two earlier figures) to board E's 14.10 A
     (R4A-N12: board A's own front end at its ISNS limit, 5.7 A at 20.7 V over 0.93, drawing from a 9.0 V bus), and
     the rail's note says so. It was an optional --figure hunk until pass 2 of the independent check (27 September
     2026), which asked that the one integration land A declaring 14.10 A like E, so both ends of IF-AE-DOCK carry one
     figure; it is unconditional now (a --figure argument is still accepted and changes nothing);
  5. the section list names the eight new pins.
Board A's placement (gen_pcb_a3.py) must seat the eight pins over E5's new targets: a layer 7 item for A's layout owner
with E5's (drafts/w3de/EQ16-dock-vin-raw.md section 5).

THIS HALF AND BOARD E'S LAND IN ONE INTEGRATION. Board E's half alone makes check_contracts.py read "dock 2x6 contact
map identical on A (J_DOCK) and E (J_BLK)" DIFFERENT on pins 1 to 4 (A VIN_RAW, E GND), which would join A's VIN_RAW to
E's GND across four 813 contacts in the committed set. drafts/w3de/a-half/ holds board A's files regenerated on the KiCad
box from this patch (install_a_half.py installs them with their sha256 asserted), and apply_registry.py refuses to
rebind unless board A's AND boards D's and E's regenerated files are all in the tree.

Usage: patch_gen_sch_a_dock.py <tree root holding v2/ecad>   (asserted old text; refuses a changed file)"""
import os, sys
p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "gen_sch_a.py")
s = open(p, encoding="utf-8").read(); o = s
EDITS = [
 # 1. the eight power pins, after the pre-charge pin
 ('''part("J_PRE1", "Connector", "Conn_01x01_Pin", "pre-charge pin, longer, mates first (32.24 AX)", "MMPIN", {"1": "PRECHG"}); r("R1", "10R 2W 2512", "PRECHG", "CELL+", "RS2512")
''',
  '''part("J_PRE1", "Connector", "Conn_01x01_Pin", "pre-charge pin, longer, mates first (32.24 AX)", "MMPIN", {"1": "PRECHG"}); r("R1", "10R 2W 2512", "PRECHG", "CELL+", "RS2512")
# EQ-16 / R8E-N01 (27 September 2026, drafted by board E's stream w3de, taken under the owner's standing rule of 26
# September 2026): VIN_RAW CROSSES THE DOCK ON FOUR 9 A POWER PINS WITH FOUR MORE FOR ITS RETURN, AS CELL+ DOES. At board
# E's declared 14.10 A the four Preci-Dip 813 contacts of J_DOCK carried 3.53 A each against their "OPERATING CURRENT Max.
# 3.5 A" (v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf, p.34), 4.70 A with one open, and
# the maker publishes no current-temperature curve for them (only "-55 ... +85 C with music wire spring", p.31). Mill-Max
# states its 085x power pins at "Continuous 9 amps @ 10 C temperature rise", "Contact Resistance: 20 mOhm max",
# "-55/+125 C" (v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf): four carry 3.53 A each, 4.70 A with
# one open (52 percent, about 3 K of rise). The four return pins keep VIN_RAW's return off the 813 ground contacts and
# the pack's return pins: at the conservative 32.1 A of ground current (14.10 A and the pack's 18.0 A at once) an 813
# ground contact carries at most about 2.2 A with one open (drafts/w3de/dock_contacts.py). E5 carries their targets and
# two 12 AWG holes to board E's P_VR and P_VN.
for k in range(1, 5):
    part("J_VR%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, VIN_RAW (Mill-Max 0858 class, dock block; EQ-16)", "MMPIN", {"1": "VIN_RAW"})
    part("J_VN%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, VIN_RAW return (Mill-Max 0858 class, dock block; EQ-16)", "MMPIN", {"1": "GND"})
'''),
 # 2. J_DOCK pins 1 to 4 become ground
 ('''part("J_DOCK", "Connector_Generic", "Conn_01x12", "spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1-4 VIN_RAW (9 to 36 V from E6), 5-7 GND, 8 SHORE_INHIBIT, 9-10 USB of E6's sensor controller, 11 GND, 12 spare", "POGO12",
     {"1": "VIN_RAW", "2": "VIN_RAW", "3": "VIN_RAW", "4": "VIN_RAW", "5": "GND",''',
  '''part("J_DOCK", "Connector_Generic", "Conn_01x12", "spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1-7 GND, 8 SHORE_INHIBIT, 9-10 USB of E6's sensor controller, 11 GND, 12 spare (VIN_RAW crosses on J_VR1-4 since EQ-16)", "POGO12",
     {"1": "GND", "2": "GND", "3": "GND", "4": "GND", "5": "GND",'''),
 # 3. the source of VIN_RAW
 ('''_intent.rail("VIN_RAW", 12.0, _VIN_RAW_A, _VIN_RAW_A, "J_DOCK", loads=''',
  '''_intent.rail("VIN_RAW", 12.0, _VIN_RAW_A, _VIN_RAW_A, ["J_VR1", "J_VR2", "J_VR3", "J_VR4"], loads='''),
 # 5. the section list
 ('''"J_CN1", "J_CN2", "J_CN3", "J_CN4", "J_PRE1", "R1", "F1", "C1", "C2", "C3", "D1", "J_DOCK"]),''',
  '''"J_CN1", "J_CN2", "J_CN3", "J_CN4", "J_PRE1", "R1", "F1", "C1", "C2", "C3", "D1", "J_DOCK"] + ["J_VR%d" % k for k in range(1, 5)] + ["J_VN%d" % k for k in range(1, 5)]),'''),
]
EDITS += [
    ('''_VIN_RAW_A = 6.15 + 6.16
''', '''# R8E-N01 (27 September 2026, EQ-16): board E declares its VIN_RAW at 14.10 A since round 8 (R4A-N12: this board's front
# end at its ISNS limit, 5.7 A at 20.7 V over 0.93, drawing from a 9.0 V bus, which the vehicle's 6.15 A and the
# tracker's 10.33 A can supply together); the 12.31 A above was the sum of board E's two earlier figures.
_VIN_RAW_A = round(5.7 * 20.7 / 0.93 / 9.0, 2)   # 14.10 A, board E's _FE_A
'''),
    # 4b. the rail's note carries the figure it declares
    ('''ORed onto one bus, 12.31 A together (third fix-up of round 4, 26 September 2026, reconciled with board E's F-IN-02); the current enters''',
     '''ORed onto one bus, 12.31 A together at those two figures (third fix-up of round 4, 26 September 2026, reconciled with board E's F-IN-02), declared at board E's 14.10 A since R8E-N01 (27 September 2026: this board's front end at its ISNS limit drawing from a 9.0 V bus, R4A-N12) and crossing the dock on the Mill-Max power pins J_VR1 to J_VR4 (EQ-16); the current enters'''),
]
for old, new in EDITS:
    if s.count(old) != 1: raise SystemExit("patch_gen_sch_a_dock: the old text is not there exactly once: %r" % old[:100])
    s = s.replace(old, new)
assert s != o
compile(s, p, "exec")
open(p, "w", encoding="utf-8").write(s); print("patch_gen_sch_a_dock: %s edited, %d hunks" % (p, len(EDITS)))
