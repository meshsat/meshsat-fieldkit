#!/usr/bin/env python3
"""apply_gen_sch_p_breaker.py: DRAFT for board P's generator owner (Layer 8 record l8p, MESHSAT-1357, 4 October 2026; round 2
of the same day). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

The defects: W4DP-F2 (record l9stk section 15, DD-1, DD-6 and DD-8, branch fnd/l9stk at 0d72880b; its latest changes checked
CONFIRMED AS CONDITIONAL). With board P's FETs Q1 and Q2 welded and no firmware, nothing on this board opens the discharge path on
current alone (15.2); a docking with a breaker already on reaches E11-30's 242.9 A (15.4, B-P1); and a hot restart of the latching
breaker into the worst resistive fault reaches 0.82 of the FET's derated SOA (15.4b, B-R1, DD-8).

The correction drawn here, every value from record l9stk by its section (the record page's section 2 lists each with its source):
  C-1 (15.4, 15.4b)  U101 LM5069MM-1, the latch-off variant (the -2's retry overheats its own FET under a persistent fault, 15.4b;
                the family and the VSSOP-10 land of board E's U6; the -1's order code is Layer 6's to file, owed) from Q2's source,
                the new net BRK_VIN, to the pack terminal PACK_P; the sense pair R101 4 mOhm and R102 7.5 mOhm in parallel; Q101 and
                Q102 CSD18510Q5B; R103 RPWR 8.45 kOhm; C101 timer 10 nF; C102 dv/dt 22 nF; D101 SMCJ18A on BRK_VIN; OVLO, the
                controller's ground, the clamp and the small parts on PACK_N (IF-6).
  C-1b (15.4)   the make-last enable LOOP into UVLO with its RC hold: R106 10 kOhm from BRK_VIN onto J_SMB pin 7 (DOCK_EN_OUT),
                through board E, the dock and board A's thermal guard RT1 and back on J_SMB pin 5 (DOCK_EN_RET) into R107 22 kOhm on
                the first inverter Q103; Q103 holds the second inverter Q104's gate (R108, R109 1 MOhm, l9stk_protection.py's R_G)
                low; Q104 pulls UVLO DIRECTLY. The hold: R104 200 kOhm from BRK_VIN charges C103 3.3 uF 50 V on the node BRK_H, which
                reaches UVLO through R105 150 ohm and D102 1N4148W, so C103 drains behind Q104 and the turn-off is 0.41 ms; the
                release 0.110 to 0.907 s after the enable mates. J_SMB pin 6 is the ground between the loop conductors (C2).
  C-1c (15.4b)  the restart inhibit on the breaker pad (DD-8): RT101, Murata NXRT15XH103FA1B010, bonded on the breaker FETs' pad
                (10 mm leads to two lands), under R110 150 kOhm from BRK_VIN; a ratiometric reference R111 147 kOhm over R112 1.62
                kOhm (1653.06 ohm equivalent, the trip's 1653); U102, a zero-drift OPA187 used as the comparator, with R113 15 MOhm
                of hysteresis; it pulls UVLO through Q105 only while PGD is low (Q106 holds Q105's gate low while PGD is high), so it
                never turns off a running breaker. Window: allow from 77.25 C, block from 83.20 C, trip 80.22 C +-2.97 K.
  IF-6          the gauge's PACK and VCC taps R6 and R7, and Q2's R19, follow Q2's source to BRK_VIN; D1 stays on PACK_P.
  B-R2 (route R1, record l8p round 3; L4-E11 19h): THE REVERSE-CHARGE DETECTOR. While the breaker is off (latched, holding or
                guard-tripped) a source on board A can push a charge backwards through Q101's and Q102's body diodes, and
                nothing on board A could tell that from a running breaker (PGD reads good with VDS negative). U103 (OPA187)
                reads the charge into the cells on the gauge's own sense R10 (its cell side through R120 against R118 1.15
                MOhm over R119 200 ohm from BRK_VIN through R129 under D103's BZT52C12: 0.368 A at least, 1.213 A at most);
                U104 (OPA187) reads the body diodes conducting (PACK_P over R121 and R122 against BRK_SNS over R123 and R124:
                PACK_P above BRK_SNS by 0.044 to 0.268 V); both high turn Q107 and Q108 on in series and hold the loop's
                return DOCK_EN_RET low, which the existing contact J_DOCK pin 3 carries to board A (its charge inhibit sets,
                L4-E11's to draw) and which resets the -1 as an undocking does; the restart then has no forward current. C107
                and C108 the bypass, C109 and C110 the filters, R125 to R128 halve the outputs for the 2N7002 gates, TP107 and
                TP108 (E-12c).
SESSION choices (under the owner's standing rule of 26 September 2026; L8P-BREAKER.md section 3): the designators (the free
100 block), the net names, J_SMB's pin assignment, the input bypass C104 and C105 in series, the four E-12 test points; in round 2
the comparator part (OPA187, its held sheet read for its offset over temperature), the reference values 147k and 1.62k, the
hysteresis resistor, the PGD gating pair Q105 and Q106 with R114 to R117, C106, TP105 and TP106 (E-12b), the NTC's lead lands;
in round 3 the reverse-charge detector (B-R2, route R1): U103, U104, Q107, Q108, D103, R118 to R129, C107 to C110, TP107, TP108.

What it changes in v2/ecad/tools/gen_sch_p.py, and nothing else:
  1. PACK_P's declaration: the breaker's output (loads Q101 and Q102, switch U101 on BRK_UVLO); BRK_VIN and BRK_SNS declared as
     segments of PACK_P (BRK_VIN switched by the gauge as PACK_P was);
  2. R6 and R7 on BRK_VIN;
  3. Q2's source and R19 on BRK_VIN;
  4. the breaker, the enable loop, the hold, the restart inhibit and the reverse-charge detector drawn before the pack leads W_P
     and W_N, with their node declarations and C106's, C107's and C108's decoupling entries;
  5. J_SMB a 1x7 with the loop on pins 5 and 7 and the return on pin 6 (no order code: the 7-way code is Layer 6's, L8P-06);
  6. VCC_F fed from BRK_VIN;
  7. one schematic section for the new parts.
Order (L8P-BREAKER.md section 5): released together with apply_gen_sch_e_enable.py and apply_gen_sch_a_ptc.py (never alone:
J_SMB's two ends and the dock's two ends must change together), with l6r2's two board P drafts in either order.

Usage:  apply_gen_sch_p_breaker.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; no added designator or net may
exist in the target; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or
net is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_p_breaker"
ADDS = ("U101", "U102", "Q101", "Q102", "Q103", "Q104", "Q105", "Q106", "D101", "D102", "RT101", "R101", "R102", "R103", "R104",
        "R105", "R106", "R107", "R108", "R109", "R110", "R111", "R112", "R113", "R114", "R115", "R116", "R117", "C101", "C102",
        "C103", "C104", "C105", "C106", "TP101", "TP102", "TP103", "TP104", "TP105", "TP106",
        "U103", "U104", "Q107", "Q108", "R118", "R119", "R120", "R121", "R122", "R123", "R124", "R125", "R126", "R127", "R128",
        "C107", "C108", "C109", "C110", "TP107", "TP108", "R129", "D103")
NETS = ("BRK_VIN", "BRK_SNS", "BRK_GATE", "BRK_TMR", "BRK_PWR", "BRK_UVLO", "BRK_G2", "BRK_H", "BRK_HD", "BRK_PGD", "BRK_CMID",
        "INH_NTC", "INH_REF", "INH_OUT", "INH_G", "DOCK_EN_OUT", "DOCK_EN_RET", "REV_ISNS", "REV_IREF", "REV_IOUT", "REV_IG",
        "REV_VP", "REV_VN", "REV_VOUT", "REV_VG", "REV_MID", "REV_VZ")

_OLD_RAIL = (
    '_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", loads={"Q2": 10.0}, switch="U1", enable_net="DSG_R", v_work=16.8, converted=False,   # the GAUGE\'s own pin; R18, 5.1k, sits between it and the FET gate DSG_G\n'
    '             note="the pack lead. THE SWITCH IS THE GAUGE: Q2 is the discharge FET and the BQ4050 drives its gate on DSG_G, so the pack terminal is live only while the gauge allows it, which is the first stage of the energy chain")\n')
_NEW_RAIL = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1 and C-1b, IF-5, IF-6): THE PACK TERMINAL IS THE BREAKER\'S\n'
    '# OUTPUT. Q2\'s source is the net BRK_VIN, the LM5069-1 breaker U101 (drawn below, before the pack leads) passes BRK_VIN through\n'
    '# its sense pair to BRK_SNS and through Q101 and Q102 to PACK_P, so the terminal is live only while the gauge holds Q2 on AND\n'
    '# the dock\'s enable loop is closed. BRK_VIN and BRK_SNS are segments of the one pack path whose power PACK_P counts.\n'
    '_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", loads={"Q101": 5.0, "Q102": 5.0}, switch="U101", enable_net="BRK_UVLO", v_work=16.8, converted=False,\n'
    '             note="the pack lead, the breaker\'s output (record l8p; l9stk 15.4 C-1, IF-6): U101 (LM5069-1, latch-off) drives Q101 and Q102 '
    '(CSD18510Q5B, an even split when enhanced, SLVA673A 2.4) from BRK_SNS; its UVLO is held low unless the dock\'s enable loop '
    'is closed (C-1b), so the terminal is live only while the gauge holds Q2 on and the kit is docked (IF-5)")\n'
    '_intent.rail("BRK_VIN", 14.4, 10.0, 18.0, "Q2", loads={"R101": 6.52, "R102": 3.48}, switch="U1", enable_net="DSG_R", series_of="PACK_P",\n'
    '             v_work=16.8, v_max=29.2, converted=False,\n'
    '             note="Q2\'s source, the breaker\'s input (record l8p; l9stk 15.4 C-1): the gauge drives Q2 on DSG_G through R18 as it '
    'drove the terminal before; the sense pair shares 65.2 and 34.8 percent (l9stk prot 3); D101 (SMCJ18A, VC 29.2 V at 51.4 A) '
    'clamps it to PACK_N; the gauge\'s PACK and VCC taps sit here (IF-6)")\n'
    '_intent.rail("BRK_SNS", 14.4, 10.0, 18.0, ["R101", "R102"], loads={"Q101": 5.0, "Q102": 5.0}, series_of="PACK_P", v_work=16.8,\n'
    '             converted=False, note="the breaker FETs\' drains, after the sense pair R101 and R102 (record l8p; l9stk 15.4 C-1)")\n')

_OLD_R6 = 'r("R6", "1k", "PACK_P", "PACK_F")'
_NEW_R6 = 'r("R6", "1k", "BRK_VIN", "PACK_F")'
_OLD_R7 = 'r("R7", "1k", "PACK_P", "VCC_F")'
_NEW_R7 = 'r("R7", "1k", "BRK_VIN", "VCC_F")'
_OLD_Q2 = 'pfet5("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "PACK_P", "C529279")'
_NEW_Q2 = 'pfet5("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "BRK_VIN", "C529279")'
_OLD_R19 = 'r("R19", "10M", "DSG_G", "PACK_P")'
_NEW_R19 = 'r("R19", "10M", "DSG_G", "BRK_VIN")'

_ANCHOR_WP = 'part("W_P", "Connector", "Conn_01x01_Pin", "pack lead + (12 AWG to the XT60 on E6 J_BATT pin 2)", "WIRE", {"1": "PACK_P"})\n'
_BREAKER = (
    '# =========================================================================================================================\n'
    '# RECORD l8p (MESHSAT-1357, 4 October 2026, round 2): W4DP-F2\'S FIRMWARE-INDEPENDENT ELEMENT, drawn from record l9stk section\n'
    '# 15 (branch fnd/l9stk at 0d72880b, its latest changes CONFIRMED AS CONDITIONAL). With Q1 and Q2 welded and no firmware,\n'
    '# nothing on this board opened the discharge path on current alone (l9stk 15.2).\n'
    '# C-1 (15.4, 15.4b): the LM5069-1 circuit breaker U101, THE LATCH-OFF VARIANT (the -2\'s retry takes its own FET past TI\'s\n'
    '# margin in a hard short and past 150 C in a resistive fault on VSYS, 15.4b), from BRK_VIN (Q2\'s source) to PACK_P. The sense\n'
    '# pair R101 4 mOhm and R102 7.5 mOhm in parallel, 2.6087 mOhm, 1 percent and at most 50 ppm/K (current limit 18.32 to 23.93 A,\n'
    '# breaker 30.21 to 50.59 A); Q101 and Q102 CSD18510Q5B, 40 V; RPWR R103 8.45 kOhm; the timer C101 10 nF (clearing at most\n'
    '# 1.292 ms); the dv/dt capacitor C102 22 nF on the gate (a start is 0.659 A at most); the input clamp D101 SMCJ18A. The clamp,\n'
    '# the controller and its small parts return to PACK_N (IF-6), and OVLO is tied there. D1 stays on PACK_P and carries the\n'
    '# lead\'s freewheel at turn-off. Where an older comment above names PACK_P as Q2\'s source, read BRK_VIN. The -1\'s order code\n'
    '# is Layer 6\'s to file (the -2 is C111822 on the same land): OWED.\n'
    '# C-1b (15.4, conditions C1 and C2): THE MAKE-LAST ENABLE IS A LOOP. R106 10 kOhm from BRK_VIN onto J_SMB pin 7 (DOCK_EN_OUT);\n'
    '# board E passes it to the dock, board A through its thermal guard RT1 (a PRF15BB103 on the battery FETs\' copper, 15.5) and\n'
    '# back on J_SMB pin 5 (DOCK_EN_RET) into R107 22 kOhm on the first inverter Q103\'s gate. Q103 holds the second inverter Q104\'s\n'
    '# gate (R108 and R109, 1 MOhm each, l9stk_protection.py\'s R_G) low; Q104, when on, pulls UVLO DIRECTLY. THE HOLD: R104 200\n'
    '# kOhm from BRK_VIN charges C103 3.3 uF 50 V on the node BRK_H, which reaches UVLO through R105 150 ohm and D102 1N4148W, so\n'
    '# when Q104 pulls UVLO, C103 drains behind it through R105 and D102 (107 mA at most, 0.11 of D102\'s 1 A 1 ms surge and 0.71\n'
    '# of its 150 mA average) and the turn-off no longer waits for C103: the gate is low 0.41 ms after the loop opens, before the\n'
    '# pins part at a withdrawal under 2.42 m/s. The release is 0.110 to 0.907 s after the enable mates, then a dv/dt start. An\n'
    '# open or a short to ground on either conductor holds the breaker off. J_SMB pin 6 is the ground contact between the two\n'
    '# conductors (C2). The order of mating (every power pin before the enable, 1 mm short) is Layer 7\'s (C1).\n'
    '# C-1c (15.4b, DD-8): THE RESTART INHIBIT ON THE BREAKER PAD. RT101, the Murata NXRT15XH103FA1B010 NTC (10 kOhm 1 percent,\n'
    '# B25/50 3380 K 1 percent, B25/85 3434 K a reference value), BONDED ON THE BREAKER FETS\' PAD with an electrically insulating,\n'
    '# thermally conducting adhesive over the pad\'s solder mask (the pad is BRK_SNS, about BRK_VIN), its 10 mm leads soldered to\n'
    '# two lands beside it; R110 150 kOhm 0.1 percent over it from BRK_VIN (0.111 mA at most, under its 0.12 mA). The reference is\n'
    '# ratiometric from the same BRK_VIN: R111 147 kOhm over R112 1.62 kOhm, both 0.1 percent (1653.06 ohm equivalent against the\n'
    '# trip\'s 1653). U102, a TI OPA187 zero-drift amplifier used as the comparator (+IN the reference, -IN the NTC: its output is\n'
    '# high while the pad is hot), R113 15 MOhm from its output to the reference for the hysteresis. Its output drives Q105\'s gate\n'
    '# through R114 and R115 (100 kOhm each, under the 2N7002\'s 20 V), and Q105 pulls UVLO. PGD gates it: R116 and R117 (1 MOhm\n'
    '# each) hold U101\'s open-drain PGD at half BRK_VIN while the breaker runs, and Q106 then holds Q105\'s gate low, so the inhibit\n'
    '# acts only while PGD is low (the breaker off, starting or in a fault, VDS over 1.62 to 3.4 V) and never turns off a running\n'
    '# breaker. Pulling UVLO resets the -1\'s latch; the breaker restarts through the hold once the pad cools under the trip, so\n'
    '# any further event starts at 83.2 C at most. THE WINDOW: allow from 77.25 C, block from 83.20 C, trip 80.22 C +-2.97 K: the\n'
    '# NTC takes +-1.02 K (its tolerance at 80 C ASSUMED: the held sheet is Murata\'s product search sheet and B25/85 a reference\n'
    '# value; to be confirmed by Murata\'s approval sheet or E-15). THE +-1.95 K LEFT, BY PART CHOICE (l8p_drafts.out section 3):\n'
    '# the OPA187 with its offset over temperature, bias and offset currents and supply rejection at most 0.02 K; the three bridge\n'
    '# resistors at 0.1 percent and at most 25 ppm/K between 25 C and the held 101.0 C case at most 0.32 K; the NTC\'s own heating\n'
    '# 0.014 K; the hysteresis at most 0.37 K, on the allow side; the remainder, at least 1.2 K on the allow side, for the\n'
    '# pad-to-NTC gradient E-15 measures (the checker asked for about 0.9 K). AN OPEN OR DETACHED NTC READS COLD AND SILENTLY\n'
    '# REMOVES THE INHIBIT: E-12b at commissioning and each service reads TP105 against TP101 (the NTC\'s fraction of BRK_VIN at the\n'
    '# ambient, 0.0625 at 25 C; near 1 is an open NTC, near 0 a short) with TP106 low. THE LOCKOUT AT THE ALLOW EDGE: a unit\n'
    '# tripping at 77.25 C needs its pad within 1 K of a 76.25 C inside air before it restarts, and at that air the cells\' hot stop\n'
    '# has already shut the kit down. E-10 gains: VDS under 1.62 V during current-limit excursions (PGD stays high, so the inhibit\n'
    '# stays gated).\n'
    '# SESSION choices of record l8p (L8P-BREAKER.md section 3): the designators (the free 100 block), the net names, J_SMB\'s pin\n'
    '# assignment, the input bypass C104 and C105 at the sense pair (TI SNVS452G section 10 and 11.1.1), two 2.2 uF 50 V in SERIES\n'
    '# through BRK_CMID (1.1 uF) as C11 and C12 are (O-12): one shorted part across the pack must not short it; the comparator part,\n'
    '# the reference values, the hysteresis, the PGD gating, C106, the test points TP101 to TP106.\n'
    '# IF-2 for the layout (gen_pcb_p3.py): each breaker FET\'s installed RthJA at most 52.5 C/W (1 in2 of 2 oz each gives the\n'
    '# sheet\'s 50), U101 beside the sense pair with Kelvin taps (E-9), C104 and C105 at the sense pair, RT101 on the FETs\' pad\n'
    '# with U102 and its bridge away from it. Nothing here is built or measured.\n'
    'ic("U101", 10, "LM5069MM-1 circuit breaker, latch-off, on the pack path (record l8p; l9stk 15.4 C-1 and 15.4b): 1 SENSE, 2 VIN, 3 UVLO, 4 OVLO, 5 GND, 6 TIMER, 7 PWR, 8 PGD, 9 OUT, 10 GATE",\n'
    '   "Package_SO:VSSOP-10_3x3mm_P0.5mm", {"1": "BRK_SNS", "2": "BRK_VIN", "3": "BRK_UVLO", "4": "PACK_N", "5": "PACK_N", "6": "BRK_TMR",\n'
    '   "7": "BRK_PWR", "8": "BRK_PGD", "9": "PACK_P", "10": "BRK_GATE"})   # the -1\'s order code: Layer 6, owed\n'
    'r("R101", "4m 1% 2512 (breaker sense, at most 50 ppm/K; 2 W at the band\'s temperature, E-6)", "BRK_VIN", "BRK_SNS", "RS2512")\n'
    'r("R102", "7.5m 1% 2512 (breaker sense, at most 50 ppm/K; 2 W at the band\'s temperature, E-6)", "BRK_VIN", "BRK_SNS", "RS2512")\n'
    'pfet5("Q101", "CSD18510Q5B 40 V N-FET, breaker pass (one of two in parallel; IF-2: RthJA at most 52.5 C/W installed)", "BRK_GATE", "BRK_SNS", "PACK_P", "C2876544")\n'
    'pfet5("Q102", "CSD18510Q5B 40 V N-FET, breaker pass (one of two in parallel; IF-2: RthJA at most 52.5 C/W installed)", "BRK_GATE", "BRK_SNS", "PACK_P", "C2876544")\n'
    'r("R103", "8.45k 1% (PWR: the power limit)", "BRK_PWR", "PACK_N"); c("C101", "10n 50V X7R (TIMER)", "BRK_TMR", "PACK_N")\n'
    'c("C102", "22n 50V X7R (GATE: the dv/dt start)", "BRK_GATE", "PACK_N")\n'
    'c("C104", "2.2u 50V X7R 1206 (VIN bypass at the sense pair, in series with C105)", "BRK_VIN", "BRK_CMID", "C1206")\n'
    'c("C105", "2.2u 50V X7R 1206 (VIN bypass at the sense pair, in series with C104)", "BRK_CMID", "PACK_N", "C1206")\n'
    'if _tvs:\n'
    '    _tvs("D101", "SMCJ18A (breaker input clamp, unidirectional: cathode on BRK_VIN)", "BRK_VIN", "PACK_N", "Diode_SMD:D_SMC", "C374030")\n'
    'else:\n'
    '    part("D101", "Device", "D_Zener", "SMCJ18A (breaker input clamp, unidirectional: cathode on BRK_VIN)", "Diode_SMD:D_SMC", {"1": "BRK_VIN", "2": "PACK_N"}, "C374030")\n'
    'r("R106", "10k", "BRK_VIN", "DOCK_EN_OUT"); r("R107", "22k", "DOCK_EN_RET", "PACK_N")\n'
    'nfet("Q103", "DOCK_EN_RET", "PACK_N", "BRK_G2", "2N7002 60 V N-FET: the enable loop\'s first inverter, on while the loop is closed")\n'
    'r("R108", "1M", "BRK_VIN", "BRK_G2"); r("R109", "1M", "BRK_G2", "PACK_N")\n'
    'nfet("Q104", "BRK_G2", "PACK_N", "BRK_UVLO", "2N7002 60 V N-FET: the enable loop\'s second inverter, pulls UVLO while the loop is open")\n'
    'r("R104", "200k 1%", "BRK_VIN", "BRK_H"); c("C103", "3.3u 50V X7R 1206 (the RC hold on BRK_H)", "BRK_H", "PACK_N", "C1206")\n'
    'r("R105", "150R", "BRK_H", "BRK_HD")\n'
    'part("D102", "Device", "D", "1N4148W (the hold\'s diode: BRK_H through R105 to UVLO; C103 drains behind Q104 through it)", "SOD123", {"1": "BRK_UVLO", "2": "BRK_HD"}, "C81598")   # Device:D, pin 1 K, pin 2 A\n'
    'part("RT101", "Device", "Thermistor_NTC", "NXRT15XH103FA1B010 NTC 10k 1%, B25/50 3380K 1%, 10 mm leads (Murata): the restart inhibit\'s sensor, bonded on the breaker FETs\' pad", "meshsat:LeadLands_1x02",\n'
    '     {"1": "INH_NTC", "2": "PACK_N"})   # its order code: Layer 6, owed\n'
    'r("R110", "150k 0.1% 25ppm (the NTC bridge)", "BRK_VIN", "INH_NTC"); r("R111", "147k 0.1% 25ppm (the trip reference)", "BRK_VIN", "INH_REF")\n'
    'r("R112", "1.62k 0.1% 25ppm (the trip reference)", "INH_REF", "PACK_N"); r("R113", "15M 1% (the hysteresis)", "INH_OUT", "INH_REF")\n'
    'ic("U102", 5, "OPA187IDBVR zero-drift amplifier as the restart inhibit\'s comparator (record l8p; l9stk 15.4b C-1c): 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+",\n'
    '   "Package_TO_SOT_SMD:SOT-23-5", {"1": "INH_OUT", "2": "PACK_N", "3": "INH_REF", "4": "INH_NTC", "5": "BRK_VIN"})   # its order code: Layer 6, owed\n'
    'c("C106", "100n 50V X7R (U102\'s supply bypass)", "BRK_VIN", "PACK_N")\n'
    '_intent.bypass("C106", "U102", "5", "BRK_VIN", cls="D", basis="TI OPA187 SBOS807E, revised May 2020 (v2/vendor/ti/held/ti-opa187-sbos807e.pdf, "\n'
    '               "fetched by record l8p): 10.1 Layout Guidelines \\"Low-ESR, 0.1-uF ceramic bypass capacitors must be connected between each "\n'
    '               "supply pin and ground; place the capacitors as close to the device as possible. A single bypass capacitor from V+ to "\n'
    '               "ground is applicable to single-supply applications\\" (p.27); the 100n drawn at U102\'s V+ (pin 5)")\n'
    'r("R114", "100k", "INH_OUT", "INH_G"); r("R115", "100k", "INH_G", "PACK_N")\n'
    'nfet("Q105", "INH_G", "PACK_N", "BRK_UVLO", "2N7002 60 V N-FET: the restart inhibit pulls UVLO while the pad is hot and PGD is low")\n'
    'r("R116", "1M", "BRK_VIN", "BRK_PGD"); r("R117", "1M", "BRK_PGD", "PACK_N")\n'
    'nfet("Q106", "BRK_PGD", "PACK_N", "INH_G", "2N7002 60 V N-FET: PGD high (the breaker running) holds the inhibit\'s gate low")\n'
    'for _i8, _n8 in enumerate(("BRK_VIN", "BRK_UVLO", "DOCK_EN_OUT", "DOCK_EN_RET", "INH_NTC", "INH_OUT"), 101):\n'
    '    part("TP%d" % _i8, "Connector", "TestPoint", _n8, "TP", {"1": _n8})   # E-12 and E-12b: the input, the hold\'s release, each loop conductor to ground in turn, the NTC\'s reading and the inhibit\'s state\n'
    '_intent.node("BRK_GATE", 29.4, "the breaker FETs\' gate: OUT (PACK_P, at most the pack\'s 16.8 V) plus the gate drive, at most 12.6 V above OUT "\n'
    '             "(VGATE, SNVS452G 7.5; record l9stk 15.4, the FETs row)", rides_on="PACK_P", bias_v=12.6)\n'
    '_intent.node("BRK_UVLO", 29.2, "the breaker\'s UVLO, a diode drop under BRK_H and at most BRK_VIN: the pack\'s 16.8 V in service and the "\n'
    '             "input clamp D101\'s 29.2 V (SMCJ18A, VC at 51.4 A; record l9stk 15.4, the clamps row)", v_work=16.8)\n'
    '_intent.node("BRK_H", 29.2, "the RC hold\'s node, charged from BRK_VIN through R104 200 kOhm: at most BRK_VIN, the input clamp\'s 29.2 V "\n'
    '             "(record l9stk 15.4, the hold)", v_work=16.8)\n'
    '_intent.node("BRK_HD", 29.2, "between R105 and D102\'s anode: at most BRK_H (record l9stk 15.4, the hold)", v_work=16.8)\n'
    '_intent.node("BRK_G2", 14.6, "the second inverter\'s gate, half of BRK_VIN through R108 and R109 (1 MOhm each): at most half the "\n'
    '             "clamp\'s 29.2 V (record l9stk 15.4, the inverters\' bounds)")\n'
    '_intent.node("BRK_PGD", 14.6, "U101\'s open-drain PGD held at half of BRK_VIN by R116 and R117 (1 MOhm each) while released: at most "\n'
    '             "half the clamp\'s 29.2 V, under Q106\'s 20 V gate rating and PGD\'s 100 V (SNVS452G 7.1)")\n'
    '_intent.node("BRK_CMID", 29.2, "the midpoint of the series input bypass C104 and C105: about half of BRK_VIN in service, and the "\n'
    '             "whole of it, at most the input clamp\'s 29.2 V, across one part when the other has shorted (the case the pair exists "\n'
    '             "for, as PACK_MID)", v_work=16.8)\n'
    '_intent.node("INH_NTC", 29.2, "the NTC\'s node under R110 150 kOhm from BRK_VIN: 0.0625 of it at 25 C, 0.0109 at the trip, and BRK_VIN "\n'
    '             "itself with the NTC open, at most the clamp\'s 29.2 V", v_work=16.8)\n'
    '_intent.node("INH_REF", 1.0, "the trip reference, 0.0109 of BRK_VIN through R111 and R112 (0.32 V at the clamp\'s 29.2 V with the "\n'
    '             "hysteresis), lifted on the cold side by U102\'s back-to-back input diodes (SBOS807E 7.3) through the bridge\'s "\n'
    '             "resistance by under 0.4 V more: under 1 V")\n'
    '_intent.node("INH_OUT", 29.2, "U102\'s output, rail to rail from PACK_N to BRK_VIN: at most the clamp\'s 29.2 V", v_work=16.8)\n'
    '_intent.node("INH_G", 14.6, "Q105\'s gate, half of U102\'s output through R114 and R115 (100 kOhm each): at most half the clamp\'s "\n'
    '             "29.2 V, under the 2N7002\'s 20 V")\n'
    '_intent.node("DOCK_EN_OUT", 29.2, "the enable loop leaving board P, BRK_VIN through R106 10 kOhm and BRK_VIN itself with the loop open: "\n'
    '             "at most the input clamp\'s 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
    '_intent.node("DOCK_EN_RET", 17.4, "the enable loop\'s return, the first inverter\'s gate over R107 22 kOhm: at most 17.4 V under the "\n'
    '             "clamp\'s 29.2 V with RT1 at its least 5 kOhm (record l9stk 15.4, the inverters\' bounds)")\n'
    '# B-R2, ROUTE R1 (record l8p round 3, 4 October 2026; L4-E11 section 19h, its checker\'s B-R2): THE REVERSE-CHARGE DETECTOR.\n'
    '# While the breaker is off (latched, in its hold, held by C-1c or by the thermal guard) a source on board A can hold CELL+ and\n'
    '# so PACK_P above BRK_VIN through the battery FETs, and push a charge backwards through Q101\'s and Q102\'s body diodes. The -1\n'
    '# then reads nothing (PGD is high on VDS alone, and VDS is negative: SNVS452G pin 8), and board A sees CELL+ alive, so its\n'
    '# hardware inhibit (L4-E11\'s Q47 to Q49) never sets: the charge rested on the firmware. THE TWO CONDITIONS, BOTH HELD HERE:\n'
    '# U103 (OPA187) reads the charge INTO THE CELLS on the gauge\'s own sense R10 (2 mOhm, cell side GND, pack side PACK_N): its\n'
    '# +IN on GND through R120 200 ohm and C109 470 nF (94 us), its -IN on R118 1.15 MOhm over R119 200 ohm from REV_VZ, which is\n'
    '# BRK_VIN through R129 47 kOhm held under D103\'s BZT52C12: 0.0869 A per volt of REV_VZ, so 0.368 A at least at the LDO-mode\n'
    '# precharge\'s floor (BRK_VIN 4.7 V), 0.661 to 0.922 A at the pack\'s 10.6 V, 1.213 A at most anywhere (the zener at 13.46 V hot),\n'
    '# with every tolerance: above the charger\'s LDO-mode precharge (0.336 A at most, L4-E11 section 15) and its power-on 256 mA,\n'
    '# under the latched FET\'s 1.405 A (L4-E11 E-14), so a charge it lets pass holds the FET at 139.9 C at most. It reads the\n'
    '# cells\' current whatever Q1 and Q2 do (welded or not) and reads nothing while the gauge sleeps, so a dead pack\'s wake through\n'
    '# the body diodes (mA, the gauge off) never trips it. U104 (OPA187) reads the BODY DIODES CONDUCTING: PACK_P over R121 332 kOhm\n'
    '# and R122 33.2 kOhm on +IN against BRK_SNS over R123 328 kOhm and R124 33.2 kOhm on -IN, high when PACK_P exceeds BRK_SNS by\n'
    '# 1.107 % of it (0.044 to 0.268 V over BRK_VIN 7.6 to 16.8 V with every tolerance; R121 to R124 0.05 % and at most 10 ppm/K),\n'
    '# C110 1 nF across its inputs. A running breaker passing any charge up to the pack path\'s 23.93 A shows at most 20.7 mV there\n'
    '# (two CSD18510Q5B channels hot); its body diodes at the threshold\'s least current about 0.35 V (TI\'s typical figure, 150 C):\n'
    '# U104 never reads a running breaker. BOTH HIGH: Q107 and Q108 (2N7002, in series, gates through R125 to R128 at half of each\n'
    '# output) hold DOCK_EN_RET under 0.05 V. That is the loop\'s return held low, as an undocking holds it: the existing contact\n'
    '# J_DOCK pin 3 carries it to board A, whose inhibit sets on it (L4-E11 extends DD-7: DOCK_EN_RET under 1.0 V with DOCK_EN_OUT at\n'
    '# 2.0 V or over sets the inhibit within 1 ms and holds it at least 1.0 s after the return rises over 2.5 V), and Q103 and Q104\n'
    '# reset the -1 (UVLO pulled). The charge stops, U103 releases, the hold (0.110 to 0.907 s) and the dv/dt start (40.7 ms)\n'
    '# restart the breaker with board A\'s battery FETs held off, so the start meets no forward current. The detector never acts on a\n'
    '# running breaker: discharging, U103 reads a negative drop; charging through the channel, U104 reads under its threshold. It\n'
    '# pulls from BRK_VIN 7.6 V (the -1\'s PORIT; the 2N7002 gates at half of it); under that the -1 cannot run or stay latched.\n'
    '# Its own failures and E-12c: the record page, section 12. Nothing here is built or measured.\n'
    'ic("U103", 5, "OPA187IDBVR zero-drift amplifier as the reverse-charge detector\'s current comparator (record l8p, B-R2): 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+",\n'
    '   "Package_TO_SOT_SMD:SOT-23-5", {"1": "REV_IOUT", "2": "PACK_N", "3": "REV_ISNS", "4": "REV_IREF", "5": "BRK_VIN"})   # U102\'s part; its order code: Layer 6, owed\n'
    'r("R129", "47k 1% (the reference\'s feed)", "BRK_VIN", "REV_VZ")\n'
    'part("D103", "Device", "D_Zener", "BZT52C12-7-F zener, the charge threshold\'s ceiling (11.4 to 12.7 V at 5 mA, DS18004)", "SOD123", {"1": "REV_VZ", "2": "PACK_N"}, "C124196")\n'
    'r("R118", "1.15M 0.1% 25ppm (the charge threshold\'s reference)", "REV_VZ", "REV_IREF"); r("R119", "200R 0.1% 25ppm (the charge threshold\'s reference)", "REV_IREF", "PACK_N")\n'
    'r("R120", "200R (Kelvin from R10\'s cell-side pad)", "GND", "REV_ISNS"); c("C109", "470n 25V X7R (the charge sense\'s filter)", "REV_ISNS", "PACK_N")\n'
    'c("C107", "100n 50V X7R (U103\'s supply bypass)", "BRK_VIN", "PACK_N")\n'
    'ic("U104", 5, "OPA187IDBVR zero-drift amplifier as the reverse-charge detector\'s body-diode comparator (record l8p, B-R2): 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+",\n'
    '   "Package_TO_SOT_SMD:SOT-23-5", {"1": "REV_VOUT", "2": "PACK_N", "3": "REV_VP", "4": "REV_VN", "5": "BRK_VIN"})   # U102\'s part; its order code: Layer 6, owed\n'
    'r("R121", "332k 0.05% 10ppm (PACK_P\'s divider)", "PACK_P", "REV_VP"); r("R122", "33.2k 0.05% 10ppm (PACK_P\'s divider)", "REV_VP", "PACK_N")\n'
    'r("R123", "328k 0.05% 10ppm (BRK_SNS\'s divider)", "BRK_SNS", "REV_VN"); r("R124", "33.2k 0.05% 10ppm (BRK_SNS\'s divider)", "REV_VN", "PACK_N")\n'
    'c("C110", "1n 50V C0G (across U104\'s inputs)", "REV_VP", "REV_VN"); c("C108", "100n 50V X7R (U104\'s supply bypass)", "BRK_VIN", "PACK_N")\n'
    '_intent.bypass("C107", "U103", "5", "BRK_VIN", cls="D", basis="TI OPA187 SBOS807E, revised May 2020 (v2/vendor/ti/held/ti-opa187-sbos807e.pdf, "\n'
    '               "fetched by record l8p): 10.1 Layout Guidelines \\"Low-ESR, 0.1-uF ceramic bypass capacitors must be connected between each "\n'
    '               "supply pin and ground; place the capacitors as close to the device as possible\\" (p.27); the 100n drawn at U103\'s V+ (pin 5)")\n'
    '_intent.bypass("C108", "U104", "5", "BRK_VIN", cls="D", basis="TI OPA187 SBOS807E, revised May 2020 (v2/vendor/ti/held/ti-opa187-sbos807e.pdf, "\n'
    '               "fetched by record l8p): 10.1 Layout Guidelines \\"Low-ESR, 0.1-uF ceramic bypass capacitors must be connected between each "\n'
    '               "supply pin and ground; place the capacitors as close to the device as possible\\" (p.27); the 100n drawn at U104\'s V+ (pin 5)")\n'
    'r("R125", "100k", "REV_IOUT", "REV_IG"); r("R126", "100k", "REV_IG", "PACK_N")\n'
    'r("R127", "100k", "REV_VOUT", "REV_VG"); r("R128", "100k", "REV_VG", "PACK_N")\n'
    'nfet("Q107", "REV_IG", "REV_MID", "DOCK_EN_RET", "2N7002 60 V N-FET: the reverse-charge detector, a charge over the threshold into the cells (in series with Q108)")\n'
    'nfet("Q108", "REV_VG", "PACK_N", "REV_MID", "2N7002 60 V N-FET: the reverse-charge detector, the breaker\'s body diodes conducting (in series with Q107)")\n'
    'for _i8, _n8 in enumerate(("REV_IOUT", "REV_VOUT"), 107):\n'
    '    part("TP%d" % _i8, "Connector", "TestPoint", _n8, "TP", {"1": _n8})   # E-12c: each comparator\'s state\n'
    '_intent.node("REV_ISNS", 0.11, "R10\'s cell side through R120 1 kOhm: the cells\' charge current times 2 mOhm, at most the breaker\'s "\n'
    '             "largest 50.59 A discharge (0.101 V under PACK_N) and its 23.93 A (0.048 V) either way (record l9stk 15.4)", v_min=-0.11)\n'
    '_intent.node("REV_VZ", 13.5, "the reference\'s feed, BRK_VIN through R129 47 kOhm under D103 (BZT52C12: 12.7 V at most at 5 mA, "\n'
    '             "plus 10 mV/K to the held 101.0 C, 13.46 V; 0.34 mA at the input clamp\'s 29.2 V)", v_work=12.7)\n'
    '_intent.node("REV_IREF", 0.003, "the charge threshold\'s reference, REV_VZ through R118 1.15 MOhm over R119 200 ohm: 1.739e-4 of it, "\n'
    '             "2.34 mV at the zener\'s 13.46 V")\n'
    '_intent.node("REV_VP", 3.0, "PACK_P over R121 and R122 (1/11): 2.95 V at D1\'s 32.4 V clamp (SMBJ20A), 1.53 V at the pack\'s 16.8 V")\n'
    '_intent.node("REV_VN", 2.7, "BRK_SNS over R123 and R124 (1/11.04): 2.65 V at the input clamp\'s 29.2 V")\n'
    '_intent.node("REV_IOUT", 29.2, "U103\'s output, rail to rail from PACK_N to BRK_VIN: at most the clamp\'s 29.2 V", v_work=16.8)\n'
    '_intent.node("REV_VOUT", 29.2, "U104\'s output, rail to rail from PACK_N to BRK_VIN: at most the clamp\'s 29.2 V", v_work=16.8)\n'
    '_intent.node("REV_IG", 14.6, "Q107\'s gate, half of U103\'s output through R125 and R126: at most half the clamp\'s 29.2 V, under the "\n'
    '             "2N7002\'s 20 V")\n'
    '_intent.node("REV_VG", 14.6, "Q108\'s gate, half of U104\'s output through R127 and R128: at most half the clamp\'s 29.2 V, under the "\n'
    '             "2N7002\'s 20 V")\n'
    '_intent.node("REV_MID", 17.4, "between Q107 and Q108: at most DOCK_EN_RET\'s 17.4 V while Q108 is off (record l9stk 15.4)")\n'
    '# =========================================================================================================================\n')

_OLD_JSMB = (
    'part("J_SMB", "Connector_Generic", "Conn_01x04", "SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND(pack side of the shunt) PRES", "XH4", '
    '{"1": "SMBC", "2": "SMBD", "3": "PACK_N", "4": "PRES_J"}, "C144395")   # R8P-02, round 8 (26 September 2026), owner condition 1: the line '
    'carried no code and lcsc_fill.py:158\'s MAP filled C594232, JST B4B-XH-A-G (gold contacts per LCSC), which JST\'s XH catalogue '
    '(v2/vendor/connectors/jst-xh-catalogue.pdf, sha256 9426b136, page 5, Header "Top entry type" table) does not list '
    '(v2/vendor/SOURCES.yaml jlc_retake_45bde541). C144395 is B4B-XH-A(LF)(SN), the table\'s own 4-circuit header without boss '
    '("Post: Brass, copper-undercoated, tin-plated"; note 1 "This product displays (LF)(SN) on a label"), JLC API 2026-09-26T21:09Z: JST, '
    'stock 108,967. Pinned here so no fill decides it; same land, pins and nets\n')
_NEW_JSMB = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; l9stk 15.4 C-1b and condition C2): J_SMB CARRIES THE DOCK ENABLE LOOP. Pins 1 to 4\n'
    '# keep the round 4 order (S-05, A07); pin 5 is the loop\'s return DOCK_EN_RET, pin 6 the ground contact between the two loop\n'
    '# conductors (the pack side of the shunt, as pin 3), pin 7 the loop\'s outgoing DOCK_EN_OUT at the end of the row. The part is\n'
    '# the 7-circuit member of the same JST XH header row (B7B-XH-A, the held catalogue\'s page 5 table, v2/vendor/connectors/\n'
    '# jst-xh-catalogue.pdf); R8P-02\'s 4-way code C144395 is withdrawn with the 4-way header, and the 7-way code is Layer 6\'s to pin\n'
    '# here as R8P-02 pinned the 4-way one (L8P-06), so no fill decides it.\n'
    'part("J_SMB", "Connector_Generic", "Conn_01x07", "SMBus and dock enable lead to E6 J_SMB (JST-XH 1x7, B7B-XH-A): 1 SMBC, 2 SMBD, 3 GND (pack side of the shunt), 4 PRES, 5 DOCK_EN_RET, 6 GND, 7 DOCK_EN_OUT",\n'
    '     "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical",\n'
    '     {"1": "SMBC", "2": "SMBD", "3": "PACK_N", "4": "PRES_J", "5": "DOCK_EN_RET", "6": "PACK_N", "7": "DOCK_EN_OUT"})\n')

_OLD_VCCF = '_intent.rail("VCC_F", 14.4, 0.0, 0.00034, "R7", loads={"U1": 0.00034}, fed_from="PACK_P", converted=False, v_work=16.8,\n'
_NEW_VCCF = ('# record l8p: R7 follows Q2\'s source to BRK_VIN (l9stk IF-6), so VCC_F is fed from BRK_VIN, the breaker\'s input\n'
             '_intent.rail("VCC_F", 14.4, 0.0, 0.00034, "R7", loads={"U1": 0.00034}, fed_from="BRK_VIN", converted=False, v_work=16.8,\n')

_ANCHOR_SEC = 'placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}\n'
_SEC = ('SECTIONS.append(("PACK BREAKER LM5069-1 (W4DP-F2), ITS FETS, SENSE PAIR AND CLAMP; THE DOCK ENABLE LOOP, ITS INVERTERS AND THE RC HOLD; THE RESTART INHIBIT; THE REVERSE-CHARGE DETECTOR (RECORD l8p)",\n'
        '                 ["U101", "R101", "R102", "Q101", "Q102", "R103", "C101", "C102", "C104", "C105", "D101", "R106", "R107", "Q103", "R108", "R109",\n'
        '                  "Q104", "R104", "C103", "R105", "D102", "RT101", "R110", "R111", "R112", "R113", "U102", "C106", "R114", "R115", "Q105",\n'
        '                  "R116", "R117", "Q106", "TP101", "TP102", "TP103", "TP104", "TP105", "TP106",\n'
        '                  "U103", "R129", "D103", "R118", "R119", "R120", "C109", "C107", "U104", "R121", "R122", "R123", "R124", "C110", "C108",\n'
        '                  "R125", "R126", "R127", "R128", "Q107", "Q108", "TP107", "TP108"]))\n')

EDITS = [
    (_OLD_RAIL, _NEW_RAIL),
    (_OLD_R6, _NEW_R6),
    (_OLD_R7, _NEW_R7),
    (_OLD_Q2, _NEW_Q2),
    (_OLD_R19, _NEW_R19),
    (_ANCHOR_WP, _BREAKER + _ANCHOR_WP),
    (_OLD_JSMB, _NEW_JSMB),
    (_OLD_VCCF, _NEW_VCCF),
    (_ANCHOR_SEC, _SEC + _ANCHOR_SEC),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    """The generator without its comments (a designator or net named in prose is not in use)."""
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    code = code_only(text)
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), code):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), code):
            refuse("net %s already exists in the target" % net)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
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


# NOT RELEASED: record l8p drafts this change for board P's generator owner and never applies it. Writing the repository's own
# gen_sch_p.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_p.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8p's drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_p.py", "b/gen_sch_p.py", n=0))
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
