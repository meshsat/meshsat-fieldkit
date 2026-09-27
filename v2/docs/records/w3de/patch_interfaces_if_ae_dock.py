#!/usr/bin/env python3
"""DRAFT for the owner of v2/ecad/tools/pcb_interfaces.yaml (board_to_board contract IF-AE-DOCK): the contract after
the EQ-16 / R8E-N01 decision (w3de, 27 September 2026, MESHSAT-1357).

What changes in the contract: VIN_RAW leaves the Preci-Dip 813 signal block and crosses on four Mill-Max 0858-class
power pins (A J_VR1-4 on E5 targets, E5 hole to E P_VR, 12 AWG) with four return pins (A J_VN1-4, E5 hole to E P_VN);
the 813 contacts 1 to 4 become GND at both ends; the contact rating, the margin with one contact open and the
temperature basis are the power pins' own maker figures; the ground current's sharing across the 813 ground contacts
is recorded as a finding with its bounds (W3DE-DOCK-R1). The numbers are drafts/w3de/dock_contacts.py's.

Usage: patch_interfaces_if_ae_dock.py <tree root holding v2/ecad>   (asserted old text; refuses a changed file)"""
import os, sys

p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "pcb_interfaces.yaml")
s = open(p, encoding="utf-8").read(); o = s

EDITS = [
    (
        '''      title: "A to E through the dock block E5: A J_DOCK (12 Preci-Dip 813 spring pins) on E5 targets, E5 lands to E J_BLK (12 x 24 AWG); pack power pins A J_CP1..4, J_CN1..4, J_PRE1 on E5 targets, E5 holes to E P_CP and P_CN (12 AWG)"''',
        '''      title: "A to E through the dock block E5: A J_DOCK (12 Preci-Dip 813 spring pins) on E5 targets, E5 lands to E J_BLK (12 x 24 AWG); pack power pins A J_CP1..4, J_CN1..4, J_PRE1 on E5 targets, E5 holes to E P_CP and P_CN (12 AWG); VIN_RAW power pins A J_VR1..4 and J_VN1..4 on E5 targets, E5 holes to E P_VR and P_VN (12 AWG, EQ-16)"''',
    ),
    (
        '''        - {board: a, refs: [J_DOCK, J_CP1-4, J_CN1-4, J_PRE1], src: "v2/ecad/tools/gen_sch_a.py:206-210, 226-227"}''',
        '''        - {board: a, refs: [J_DOCK, J_CP1-4, J_CN1-4, J_PRE1, J_VR1-4, J_VN1-4], src: "v2/ecad/tools/gen_sch_a.py:206-210, 226-227 and the EQ-16 pins after J_PRE1 (drafts/w3de/patch_gen_sch_a_dock.py)"}''',
    ),
    (
        '''        - {board: e, refs: [J_BLK, P_CP, P_CN], src: "v2/ecad/tools/gen_sch_e.py:233-234, 562"}''',
        '''        - {board: e, refs: [J_BLK, P_CP, P_CN, P_VR, P_VN], src: "v2/ecad/tools/gen_sch_e.py: P_CP and P_CN at the pack entry, J_BLK, P_VR and P_VN at the block lands (EQ-16)"}''',
    ),
    (
        '''      pins: {1: VIN_RAW, 2: VIN_RAW, 3: VIN_RAW, 4: VIN_RAW, 5: GND, 6: GND, 7: GND, 8: SHORE_INHIBIT, 9: USB_E6_P,
             10: USB_E6_N, 11: GND, 12: DOCK_SPARE}''',
        '''      pins: {1: GND, 2: GND, 3: GND, 4: GND, 5: GND, 6: GND, 7: GND, 8: SHORE_INHIBIT, 9: USB_E6_P,
             10: USB_E6_N, 11: GND, 12: DOCK_SPARE}
      pins_history: "1 to 4 carried VIN_RAW until EQ-16 (27 September 2026); they are ground returns for the USB pair and
        the control line since, beside 5 to 7 and 11"''',
    ),
    (
        '''                contact: "Preci-Dip 813, 'OPERATING CURRENT Max. 3.5 A' per contact; -55 to +85 C with the music wire spring
                  (v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf, VERIFIED)",
                margin: "3.08 A per contact at 12.31 A if the four share evenly, 88 percent of the rating; with one of the four
                  open, 4.10 A, over the rating (INFERRED arithmetic; R4A-N13, open): the contract carries no margin for an
                  open or high-resistance contact; hot-end derating TBD. At board E's 14.10 A (round 8) the four carry 3.53 A
                  each with even sharing, 101 percent of the 3.5 A rating: NOT MET at nominal (R8E-N01, open; the remedy is
                  board A's or the contract's: a fifth VIN_RAW contact, a front-end input bound in hardware, or the host's
                  IIN_HOST extended to the panel, the last a firmware bound only)"}''',
        '''                contact: "since EQ-16 (27 September 2026): four Mill-Max 0858-class power pins A J_VR1..4 for VIN_RAW and four
                  J_VN1..4 for its return, the class the pack pins use: 'Rated Current (Free air): Continuous 9 amps @ 10 C
                  temperature rise', 'Contact Resistance: 20 mOhm max', 'Operating temperature range: -55/+125 C'
                  (v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf, VERIFIED). Until then four Preci-Dip 813
                  contacts, 'OPERATING CURRENT Max. 3.5 A', 10 mOhm static, -55 to +85 C with the music wire spring and no
                  current-temperature curve (v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf, VERIFIED)",
                margin: "at board E's 14.10 A: 3.53 A per power pin with even sharing (39 percent of 9 A), 4.70 A with one
                  of the four open (52 percent); with a 2:1 resistance spread among the four (the maker states a maximum
                  only), 5.64 A on the lowest and 7.05 A with one open (63 and 78 percent). Temperature, from the maker's
                  10 K at 9 A scaled as I2R: at most about 6 K of rise, so under 72 C at the +55 C qualification margin's 65 C
                  inside air against 125 C (INFERRED arithmetic, drafts/w3de/dock_contacts.py). The ECSS-Q-ST-30-11C Rev.2
                  Table 6-10 screen (50 percent, 30 C under the maximum rated temperature: 4.5 A and 95 C) holds with even
                  sharing and is exceeded with one pin open or at the 2:1 spread, a space screen reported as the fuse
                  screen is, not a limit this contract claims. R8E-N01 and the supply half of R4A-N13 are answered by
                  EQ-16 (its session choice in pcb_requirements.yaml). Before EQ-16, four 813 contacts carried 3.53 A each, 101
                  percent of their maximum, and 4.70 A with one open"}''',
    ),
    (
        '''      not_judged: ["clamp orientation and value against the board (A03, A04)", "contact current at temperature", "the declared currents of the two ends"]
      findings: [R4A-N13, R4A-N12, R8E-N01, A04-D2, W3-F09, BAT-F06, PWR-F12]''',
        '''      ground_return: "W3DE-DOCK-R1 (27 September 2026): the ground current from A to E shares every ground contact of the
        dock, the Mill-Max return pins behind their pours and 12 AWG wires and the 813 ground contacts behind their 24 AWG
        wires, in the ratio of the two groups' resistances, which the makers bound only from above. As drawn before EQ-16
        (4 CN and 4 x 813 GND), with every Mill-Max pin at its 20 mOhm maximum, an 813 ground contact carries 3.06 A at
        24.1 A of ground current (this rail's 14.10 A with the pack's 10.0 A) and 4.08 A at 32.1 A (with the pack's 18.0
        A peak), 88 and 117 percent of 3.5 A. With EQ-16 (4 CN, 4 VN, 8 x 813 GND) the same case is 1.57 and 2.09 A,
        and 2.24 A with one 813 open (64 percent); the coincidence of both currents at their maxima is the conservative
        bound, not an operating point (INFERRED arithmetic, drafts/w3de/dock_contacts.py). The residual: at the +55 C
        qualification margin with that 32.1 A peak and the Mill-Max pins at their maximum, an 813 ground contact reaches
        86 to 90 C under the assumed 60 K rise at 3.5 A (the maker publishes none), over its 85 C; a bench measurement
        of the dock's contact resistances and of an 813 ground contact's temperature at the declared currents is owed
        to TEST-PLAN.md"
      not_judged: ["clamp orientation and value against the board (A03, A04)", "contact current measured at temperature (the desk bound is in margin and ground_return)", "the declared currents of the two ends", "E5's layout of the eight VIN_RAW targets and two 12 AWG holes (layer 7, A's and E5's owners)"]
      findings: [R4A-N13, R4A-N12, R8E-N01, EQ-16, W3DE-DOCK-R1, A04-D2, W3-F09, BAT-F06, PWR-F12]''',
    ),
]

for old, new in EDITS:
    if s.count(old) != 1:
        raise SystemExit("patch_interfaces_if_ae_dock: the old text is not there exactly once: %r" % old[:100])
    s = s.replace(old, new)
assert s != o
import yaml
y = yaml.safe_load(s)
c = y["board_to_board"]["contracts"]["IF-AE-DOCK"]
assert c["pins"][1] == "GND" and "EQ-16" in c["findings"], c["pins"]
open(p, "w", encoding="utf-8").write(s)
print("patch_interfaces_if_ae_dock: %s edited, %d hunks" % (p, len(EDITS)))
