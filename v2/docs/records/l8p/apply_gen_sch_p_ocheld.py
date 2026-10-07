#!/usr/bin/env python3
"""apply_gen_sch_p_ocheld.py: DRAFT for board P's generator owner (Layer 8 record l8p, MESHSAT-1357, round 11, 7 October 2026: the
correction of finding L8P-R10-F1, register row L4A-67; AMENDED IN PLACE by round 12, 7 October 2026, after the focused check L4A-69
(W147's F2 and F1: the crowbar's on-time bounded by channel 2, D106, R143, C120 at 22 nF); AMENDED IN PLACE AGAIN by round 13,
7 October 2026, after the targeted recheck L4A-69 (W153's F1: round 12's PGD-low disarm was defeated by leakage into a 2.2 MOhm node;
OCH_S2 is now pulled up from BRK_VIN by R143 330 kOhm and held low while PGD is low by Q114, whose gate is PGD inverted by Q113 with
R144 and the zener D107; BRK_PGD carries no resistor of the trip). NOT APPLIED to the tree by this record;
its authors ran it only on scratch copies (the tests write scratch copies). Nothing in this kit has been built, bought or measured.

The finding (record l8p round 10, L8P-BREAKER.md 15c): at the breaker's held 23.93 A (the LM5069-1's most current limit, held
indefinitely by design) from the 76.25 C inside air, the three 25 A MINI blades (board P's F1, board E's F3, board A's F1;
Littelfuse 297) carry 103.6 % of their printed rerated current (23.10 A at the air, 22.75 A at the band's 85.41 C). The LM5069's
printed VCL span (48.5 to 61.5 mV) cannot place its most limit under 23.10 A while its least stays over the 18 A service.

The correction drawn here (L8P-BREAKER.md section 16; l8p_cprot.out [CP 3] to [CP 5]): A HELD-OVERCURRENT TRIP that ends any held
current over a window of 19.96 to 21.52 A (printed maxima and the record's stated assumptions) by FORCING THE LM5069-1 INTO ITS OWN
PRINTED CURRENT-LIMIT AND FAULT-TIMER LATCH, so the recovery is the -1's own (redocking, an input's return, the guard's cycle):
  U106    OPA187 (U102's part) as an inverting amplifier of the gauge's sense R10 (2 mOhm, cell side GND, pack side PACK_N, Kelvin
          from its two pads): R132 1.00 kOhm from GND, R133 19.3 kOhm feedback (both 0.1 %, 25 ppm/K), +IN on PACK_N through R134;
          OCH_A = 19.3 x I x R10 in discharge, 0 when charging.
  U107    TPS37A010122DSKR (U47's and U48's part, C3685740): channel 1 (OV, 0.792 to 0.808 V printed) reads OCH_A through R135 and
          C117; RESET1 (open drain) asserts after its sense delay C119 (4.7 nF C0G: 0.460 to 0.851 ms, SNVSBJ1E Equations 5 and 6).
          Channel 2 (UV) reads OCH_S2 (round 13): pulled up from BRK_VIN by R143 330 kOhm, held low by Q114 (2N7002) while PGD is
          low (Q114's gate OCH_PN is PGD inverted: Q113, a 2N7002 with its gate on BRK_PGD, against R144 200 kOhm from BRK_VIN, the
          zener D107 keeping OCH_PN under 12.7 V), and pulled under its threshold through D106 (BAT46W) while RESET1 is asserted
          (round 12's R143 2.2 MOhm from BRK_PGD withdrawn: leakage through D106 lifted OCH_S2 over the threshold while PGD was low,
          L8P-BREAKER.md 16j). RESET2 asserts after C120's sense delay (22 nF C0G: 2.15 to 3.92 ms) once PGD has
          been low OR the trip has been asserted, and through Q112 disarms the crowbar: the trip acts only on a RUNNING breaker, never
          at power-up (the TPS37 holds both outputs asserted for tSD) or during a start, AND THE CROWBAR CONDUCTS AT MOST 3.92 ms
          AFTER THE TRIP ASSERTS whatever the breaker does (round 12: a unit whose limit is over the crowbar's own current at a low
          BRK_VIN, or a source on VSYS, can keep the -1 out of its limit; L8P-BREAKER.md 16i). It re-arms only once RESET1 has
          released (the held current under the window) and PGD is high.
  Q112    2N7002, its gate OCH_EG at half BRK_VIN through R139 and R141 (1 MOhm each) unless RESET2 holds it low, in series with
          RESET1 in the gate path of
  Q110    AO3401A (the kit's P-FET, C15127), source on BRK_VIN, gate through R136 47 kOhm over R137 100 kOhm: on (VGS -0.32 of
          BRK_VIN) only while RESET1 AND Q112 conduct; its drain through R142 1 kOhm onto the crowbar's gate OCH_CG, held by R138
          4.7 kOhm and clamped by D105 (BZT52C12, at most 12.7 V) under the gate's 20 V.
  Q111    CSD18510Q5B (Q101's part, C2876544), the CROWBAR: drain through R140 0.39 Ohm (a part whose maker prints the single
          pulse of l8p_cprot.out [CP 4c'], E-6b as round 13 states it on one basis, Layer 6) to PACK_P, source on PACK_N. Its own current from BRK_VIN
          about 9.54 to 9.61 V up (round 13: the loop's VCL at the limit, the -1's FETs and Q111 with R140; R140 alone gave 9.43 V;
          26.8 A at the pack's 10.6 V) is over the LM5069's most limit (23.93 A) whatever the load, so the -1 enters its
          current limit (or its circuit breaker, from 30.21 A) and latches after its fault timer: the event l9stk 15.6 judges
          ("an overload over the unit's limit", 0.57 of the derated SOA), once per recovery. Under that edge (C-PROT rev 1 runs the
          -1 from 7.6 V) the latch rests on the faulted load persisting; if it drops out, the crowbar's own current can hold the
          trip, and channel 2 ends it within 3.92 ms (round 12).
  TP110, TP111, TP112  OCH_S, OCH_CG and OCH_S2 for the commissioning check E-12f (a test voltage over 0.808 V on OCH_S latches the
          breaker; OCH_CG's pulse is at most 3.92 ms plus the turn-off; OCH_S2 reads the disarm).
  Q113, Q114, R144, D107  (round 13) PGD inverted onto OCH_PN and OCH_S2 held low through Q114 while PGD is low: a conducting FET,
          so no leakage into OCH_S2 can lift it; BRK_PGD carries only Q113's gate beside Q106's.
  intent  the nodes OCH_N, OCH_P, OCH_A, OCH_S, OCH_R, OCH_EG, OCH_X, OCH_PG, OCH_GD, OCH_CG, OCH_CD, OCH_CTS, OCH_CTS2, OCH_S2, OCH_PN; the
          decoupling entries C116 (U106) and C118 (U107); one schematic section.
Nothing of the drawn loop, its inverters, UVLO, the hold or DOCK_EN_OUT and DOCK_EN_RET is touched: the trip adds no sink on the
loop and none on UVLO, so L4-E11 20c's window, its readings and the RC hold's 0.110 to 0.907 s stand as drawn. Round 12's R143 loaded
BRK_PGD (Q106's gate, the restart inhibit's gating) with 2.2 MOhm (3.20 V at BRK_VIN 7.6 V while D106 pulled); round 13 moves R143 to
BRK_VIN, so BRK_PGD carries only Q106's and Q113's gates (3.72 V or more at 7.6 V on their printed 80 nA), over Q106's 2.5 V threshold
maximum in every state of the trip.
SESSION choices (under the owner's standing rule of 26 September 2026; L8P-BREAKER.md section 16g, decision L8P-R11-D1): the
arrangement (a precise held-current window ending in the -1's own latch, not a second current limit in series), the sense (R10,
low side, an OPA187 the kit carries), the parts (every type already in the kit), the values, the designators (the 100 block, after
rounds 3 and 4) and the net names; round 12 (decision L8P-R12-D1, section 16i): the on-time bound through channel 2 (D106 a BAT46W,
board A's part C83152; R143; C120 at 22 nF) over R140 lowered or the trip armed only over 9.43 V; round 13 (decision L8P-R13-D1,
section 16j): OCH_S2 held low through a conducting FET while PGD is low (Q113, Q114, R144, D107; R143 330 kOhm from BRK_VIN) over a
disarm FET driven from the crowbar's gate and over R143 lowered with a pull-down.

ORDER: AFTER this record's apply_gen_sch_p_breaker.py and apply_gen_sch_p_idealdiode.py (it reads the breaker's BRK_PGD, BRK_VIN
and PACK_P and takes the 100 block after round 4's designators; it refuses a target without them), released with them: its own
RELEASE-R11.md until L4-E9's change list gives it a row (L8P-BREAKER.md section 6 item 1), then the folder's one RELEASE.md.

Usage:  apply_gen_sch_p_ocheld.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; no added designator or net may
exist in the target; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or
net is in use, the breaker or ideal-diode draft is not applied, or the repository's own generator is named before RELEASE-R11.md
releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_p_ocheld"
ADDS = ("U106", "U107", "Q110", "Q111", "Q112", "D105", "D106", "R132", "R133", "R134", "R135", "R136", "R137", "R138", "R139", "R140",
        "R141", "R142", "R143", "C116", "C117", "C118", "C119", "C120", "TP110", "TP111", "TP112", "Q113", "Q114", "R144", "D107")
NETS = ("OCH_N", "OCH_P", "OCH_A", "OCH_S", "OCH_R", "OCH_EG", "OCH_X", "OCH_PG", "OCH_GD", "OCH_CG", "OCH_CD", "OCH_CTS",
        "OCH_CTS2", "OCH_S2", "OCH_PN")
REQUIRES = ('ic("U101", 10, "LM5069MM-1 circuit breaker', 'r("R116", "1M", "BRK_VIN", "BRK_PGD"); r("R117", "1M", "BRK_PGD", "PACK_N")',
            'ic("U105", 6, "LM74700QDBVRQ1 ideal-diode controller',
            'r("R10", "2m 2512 2W (sense)", "GND", "PACK_N", "RS2512")')

_ANCHOR_WP = 'part("W_P", "Connector", "Conn_01x01_Pin", "pack lead + (12 AWG to the XT60 on E6 J_BATT pin 2)", "WIRE", {"1": "PACK_P"})\n'
_TRIP = (
    '# =========================================================================================================================\n'
    '# RECORD l8p (MESHSAT-1357, 7 October 2026, round 11; register row L4A-67): FINDING L8P-R10-F1 CORRECTED IN THE DRAFT. At the\n'
    '# breaker\'s held 23.93 A (U101\'s most current limit, held indefinitely by design) from the 76.25 C inside air the three 25 A MINI\n'
    '# blades (this board\'s F1, board E\'s F3, board A\'s F1; Littelfuse 297) carried 103.6 % of their printed rerated current, and U101\'s\n'
    '# printed VCL span cannot place its most limit under it while its least stays over the 18 A service (L8P-BREAKER.md 15c).\n'
    '# THE CORRECTION: A HELD-OVERCURRENT TRIP THAT ENDS IN U101\'S OWN LATCH. U106 (OPA187, inverting, gain 19.3 on R132 and R133 at\n'
    '# 0.1 % and 25 ppm/K) reads R10 by Kelvin taps from its two pads (R132 from the cell-side GND pad, R134 from the PACK_N pad):\n'
    '# OCH_A = 19.3 x I x 2 mOhm in discharge, 0 when charging. U107 (TPS37A010122, channel 1 OV at 0.792 to 0.808 V) asserts RESET1\n'
    '# after C119\'s sense delay when OCH_A passes it: a held current over 19.96 to 21.52 A (printed maxima; R10 at the record\'s 1 %\n'
    '# and 75 ppm/K, ASSUMED, E-6; the window holds for R10 within -7.3 to +8.3 %). RESET1 pulls Q110\'s gate through Q112 and R137:\n'
    '# Q110 (AO3401A from BRK_VIN) drives the crowbar Q111 (CSD18510Q5B) through R142 onto OCH_CG (R138 to PACK_N, D105 BZT52C12 under\n'
    '# the gate\'s 20 V), and Q111 loads PACK_P through R140 0.39 Ohm: 26.8 A at the pack\'s least 10.6 V on its own, over U101\'s most\n'
    '# limit 23.93 A whatever the load, so U101 enters its current limit (or its circuit breaker from 30.21 A) and its fault timer\n'
    '# latches the -1 off: the event record l9stk 15.6 judges for "an overload over the unit\'s limit" (1.29 ms, 0.57 of the derated\n'
    '# SOA), once per recovery (redocking, an input\'s return, the guard\'s cycle: the -1\'s own). U107\'s channel 2 reads OCH_S2, pulled up\n'
    '# from BRK_VIN by R143, held low by Q114 while PGD is low (round 13: Q113 inverts BRK_PGD onto Q114\'s gate), and pulled under the\n'
    '# threshold by D106 (BAT46W) while RESET1 is asserted: once PGD has been low OR the trip\n'
    '# has been asserted for C120\'s sense delay (2.16 ms at least, past the trip\'s gate and U101\'s 1.292 ms clearing; 3.92 ms at most)\n'
    '# RESET2 holds Q112 off, so the crowbar acts only on a running breaker, never at power-up (U107 holds its outputs for tSD), during a\n'
    '# start or on a latched breaker, AND CONDUCTS AT MOST 3.92 ms PLUS ITS TURN-OFF WHATEVER THE BREAKER DOES (round 12, after the\n'
    '# focused check L4A-69: under BRK_VIN about 9.54 to 9.61 V a unit whose limit is over the crowbar\'s own current, or a source on VSYS, can keep\n'
    '# the -1 out of its limit with the crowbar\'s own current holding the trip). It re-arms only after RESET1 releases and PGD is high.\n'
    '# The trip adds no sink on the enable loop and none on UVLO: L4-E11 20c\'s window, its readings and the RC hold stand as drawn.\n'
    '# FOR THE LAYOUT (gen_pcb_p3.py): R132 and R134 by Kelvin traces from R10\'s two pads as R120 is; U106, U107, Q110 and Q112 off the\n'
    '# breaker pad (each at most 86.25 C, the site the record counts their leakage at); Q111 and R140 on the PACK_P band with the\n'
    '# band\'s width to PACK_N; R143 and D106 beside U107; Q113, Q114 and D107 off the breaker pad as U107 (round 13). Nothing here is\n'
    '# built or measured. The acceptance and what stays open: L8P-BREAKER.md section 16 (16i for round 12, 16j for round 13).\n'
    'ic("U106", 5, "OPA187IDBVR zero-drift amplifier as the held-overcurrent trip\'s R10 amplifier (record l8p round 11): 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+",\n'
    '   "Package_TO_SOT_SMD:SOT-23-5", {"1": "OCH_A", "2": "PACK_N", "3": "OCH_P", "4": "OCH_N", "5": "BRK_VIN"})   # U102\'s part; its order code: Layer 6, owed\n'
    'r("R132", "1.00k 0.1% 25ppm (the trip\'s input, Kelvin from R10\'s cell-side pad)", "GND", "OCH_N"); r("R133", "19.3k 0.1% 25ppm (the trip\'s gain)", "OCH_N", "OCH_A")\n'
    'r("R134", "1.00k (Kelvin from R10\'s pack-side pad)", "PACK_N", "OCH_P"); c("C116", "100n 50V X7R (U106\'s supply bypass)", "BRK_VIN", "PACK_N")\n'
    'r("R135", "1k", "OCH_A", "OCH_S"); c("C117", "10n 50V C0G (SENSE1\'s filter)", "OCH_S", "PACK_N")\n'
    'ic("U107", 11, "TPS37A010122DSKR 65 V OV/UV supervisor: the held-overcurrent trip (channel 1), its arming on PGD and its on-time bound (channel 2)",\n'
    '   "Package_SON:WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm", {"1": "BRK_VIN", "2": "OCH_S", "3": "OCH_S2", "4": "OCH_R", "5": "OCH_EG",\n'
    '   "6": "NC", "7": "OCH_CTS", "8": "OCH_CTS2", "9": "NC", "10": "PACK_N", "11": "PACK_N"}, "C3685740")\n'
    'c("C118", "100n 50V X7R (U107\'s VDD bypass)", "BRK_VIN", "PACK_N"); c("C119", "4.7n 50V C0G 5% (CTS1: the trip\'s sense delay)", "OCH_CTS", "PACK_N")\n'
    'c("C120", "22n 50V C0G 5% (CTS2: the arming\'s sense delay after PGD falls or the trip asserts: the crowbar\'s on-time bound)", "OCH_CTS2", "PACK_N")\n'
    'r("R143", "330k 1%", "BRK_VIN", "OCH_S2")   # round 13: OCH_S2 pulled up from BRK_VIN, not from BRK_PGD (L8P-BREAKER.md 16j)\n'
    'nfet("Q113", "BRK_PGD", "PACK_N", "OCH_PN", "2N7002 60 V N-FET: PGD inverted onto Q114\'s gate (record l8p round 13)")\n'
    'r("R144", "200k 1%", "BRK_VIN", "OCH_PN")   # round 13: Q114\'s gate at least 5 V while PGD is low (Q113\'s and D107\'s leakage at the site)\n'
    'part("D107", "Device", "D_Zener", "BZT52C12-7-F zener, Q114\'s gate under 12.7 V (DS18004; record l8p round 13)", "SOD123", {"1": "OCH_PN", "2": "PACK_N"}, "C124196")\n'
    'nfet("Q114", "OCH_PN", "PACK_N", "OCH_S2", "2N7002 60 V N-FET: OCH_S2 held low while PGD is low, the disarm (record l8p round 13)")\n'
    'part("D106", "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (the trip asserted pulls OCH_S2: the crowbar\'s on-time bound; DS30044)", "SOD123", {"1": "OCH_R", "2": "OCH_S2"}, "C83152")   # pin 1 K, pin 2 A\n'
    'r("R139", "1M", "BRK_VIN", "OCH_EG"); r("R141", "1M", "OCH_EG", "PACK_N")\n'
    'nfet("Q112", "OCH_EG", "OCH_R", "OCH_X", "2N7002 60 V N-FET: the trip armed while the breaker runs (RESET2 deasserted)")\n'
    'r("R136", "47k", "BRK_VIN", "OCH_PG"); r("R137", "100k", "OCH_PG", "OCH_X")\n'
    'part("Q110", "Transistor_FET", "AO3401A", "AO3401A P-FET: the crowbar\'s gate drive from BRK_VIN (1 G, 2 S, 3 D)", "SOT23", {"1": "OCH_PG", "2": "BRK_VIN", "3": "OCH_GD"}, "C15127")\n'
    'r("R142", "1k", "OCH_GD", "OCH_CG"); r("R138", "4.7k", "OCH_CG", "PACK_N")\n'
    'part("D105", "Device", "D_Zener", "BZT52C12-7-F zener, the crowbar\'s gate under 12.7 V (DS18004)", "SOD123", {"1": "OCH_CG", "2": "PACK_N"}, "C124196")\n'
    'pfet5("Q111", "CSD18510Q5B 40 V N-FET, the held-overcurrent trip\'s crowbar into U101\'s latch (record l8p round 11)", "OCH_CG", "OCH_CD", "PACK_N", "C2876544")\n'
    'r("R140", "0.39R 1% (a part whose maker prints a single pulse of at least 3.51 J in 4.41 ms with 2.21 kW for 16.5 us: Layer 6, E-6b)", "PACK_P", "OCH_CD", "RS2512")\n'
    'part("TP110", "Connector", "TestPoint", "OCH_S", "TP", {"1": "OCH_S"}); part("TP111", "Connector", "TestPoint", "OCH_CG", "TP", {"1": "OCH_CG"})   # E-12f\n'
    'part("TP112", "Connector", "TestPoint", "OCH_S2", "TP", {"1": "OCH_S2"})   # E-12f: the disarm\n'
    '_intent.bypass("C116", "U106", "5", "BRK_VIN", cls="D", basis="TI OPA187 SBOS807E, revised May 2020 (v2/vendor/ti/held/ti-opa187-sbos807e.pdf, "\n'
    '               "held back): 10.1 \\"Connect low-ESR, 0.1-uF ceramic bypass capacitors between each supply pin and ground; place the "\n'
    '               "capacitors as close to the device as possible\\" (p.27); the 100n drawn at U106\'s V+ (pin 5)")\n'
    '_intent.bypass("C118", "U107", "1", "BRK_VIN", cls="D", basis="TI SNVSBJ1E (TPS37) pin table: VDD \\"Input Supply Voltage: Bypass with a "\n'
    '               "0.1 uF capacitor to GND\\" (p.5); the 100n drawn at U107\'s VDD (pin 1)")\n'
    '_r11 = "record l8p round 11 (the held-overcurrent trip, L8P-R10-F1): "\n'
    '_intent.node("OCH_N", 0.5, _r11 + "U106\'s inverting input, held at PACK_N by its feedback; at most about 0.5 V off it while the amplifier "\n'
    '             "saturates in a hard short (GND up to 0.96 V under PACK_N for 16.5 us, through R132 1 kOhm)")\n'
    '_intent.node("OCH_P", 0.5, _r11 + "U106\'s non-inverting input, PACK_N through R134 by a Kelvin tap")\n'
    '_intent.node("OCH_A", 29.2, _r11 + "U106\'s output, rail to rail from PACK_N to BRK_VIN: at most the input clamp\'s 29.2 V", v_work=16.8)\n'
    '_intent.node("OCH_S", 29.2, _r11 + "U107\'s SENSE1, OCH_A through R135: at most the clamp\'s 29.2 V against SENSE\'s 65 V", v_work=16.8)\n'
    '_intent.node("OCH_R", 29.2, _r11 + "U107\'s RESET1 (open drain), pulled to BRK_VIN through R136 and R137 while Q112 conducts", v_work=16.8)\n'
    '_intent.node("OCH_EG", 14.6, _r11 + "Q112\'s gate, half of BRK_VIN through R139 and R141 unless RESET2 holds it low: at most half the "\n'
    '             "clamp\'s 29.2 V, under the 2N7002\'s 20 V")\n'
    '_intent.node("OCH_X", 29.2, _r11 + "between R137 and Q112\'s drain: at most BRK_VIN", v_work=16.8)\n'
    '_intent.node("OCH_PG", 29.2, _r11 + "Q110\'s gate, BRK_VIN through R136 47 kOhm; at least 0.68 of BRK_VIN while the trip pulls it, so "\n'
    '             "Q110\'s VGS is at most 9.3 V at the clamp against the AO3401A\'s 12 V", v_work=16.8)\n'
    '_intent.node("OCH_GD", 29.2, _r11 + "Q110\'s drain: BRK_VIN while the crowbar is driven, at most the clamp\'s 29.2 V", v_work=16.8)\n'
    '_intent.node("OCH_CG", 12.7, _r11 + "the crowbar\'s gate, held under D105\'s 12.7 V (BZT52C12, DS18004) against the CSD18510Q5B\'s 20 V")\n'
    '_intent.node("OCH_CD", 29.2, _r11 + "the crowbar\'s drain, PACK_P through R140: at most the pack terminal\'s 16.8 V in service, the input "\n'
    '             "clamp\'s 29.2 V in a transient", v_work=16.8)\n'
    '_intent.node("OCH_CTS", 6.0, _r11 + "U107\'s CTS1 capacitor, under the pin\'s 6 V (SNVSBJ1E 7.1)")\n'
    '_intent.node("OCH_CTS2", 6.0, _r11 + "U107\'s CTS2 capacitor, under the pin\'s 6 V (SNVSBJ1E 7.1)")\n'
    '_intent.node("OCH_S2", 29.2, "record l8p rounds 12 and 13 (the on-time bound and the disarm): U107\'s SENSE2, BRK_VIN through R143 "\n'
    '             "330 kOhm (round 13), at most the clamp\'s 29.2 V against SENSE\'s 65 V; under 0.55 V while D106 conducts into an asserted "\n'
    '             "RESET1 (VOL 0.3 V, VF 0.25 V at 0.1 mA), near PACK_N while Q114 conducts", v_work=16.8)\n'
    '_intent.node("OCH_PN", 12.7, "record l8p round 13: Q114\'s gate, BRK_VIN through R144 200 kOhm unless Q113 (PGD high) holds it low, "\n'
    '             "under D107\'s 12.7 V (BZT52C12, DS18004) against the 2N7002\'s 20 V", v_work=12.7)\n'
    '# =========================================================================================================================\n')

_ANCHOR_SEC = 'placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}\n'
_SEC = ('SECTIONS.append(("THE HELD-OVERCURRENT TRIP (L8P-R10-F1): U106, U107, THE CROWBAR Q111 INTO U101\'S LATCH (RECORD l8p)",\n'
        '                 ["U106", "R132", "R133", "R134", "C116", "R135", "C117", "U107", "C118", "C119", "C120", "R139", "R141", "Q112",\n'
        '                  "R136", "R137", "Q110", "R142", "R138", "D105", "Q111", "R140", "R143", "D106", "TP110", "TP111", "TP112",\n'
        '                  "Q113", "R144", "D107", "Q114"]))\n')

EDITS = [
    (_ANCHOR_WP, _TRIP + _ANCHOR_WP),
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
    for req in REQUIRES:
        if req not in text:
            refuse("this record's breaker and ideal-diode drafts are not applied in the target (%r missing): apply "
                   "apply_gen_sch_p_breaker.py and apply_gen_sch_p_idealdiode.py first" % req[:44])
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), code):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), code):
            refuse("net %s already exists in the target" % net)
    if text.count(_TRIP) != 0 or text.count(_SEC) != 0:
        refuse("already applied (the new text is present)")
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


# NOT RELEASED: record l8p drafts this change for board P's generator owner and never applies it. Writing the repository's own
# gen_sch_p.py is refused until RELEASE-R11.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
# Its own release file until L4-E9's change list gives it a row (L8P-BREAKER.md section 6 item 1, "Not covered"); then the integrator
# points RELEASE at the folder's one RELEASE.md, with the item's count and its register row. It refuses a board P without the
# breaker and the ideal diode, so it can never be applied ahead of them.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_p.py")
RELEASE = os.path.join(HERE, "RELEASE-R11.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE-R11.md; l8p's round 11 draft waits on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE-R11.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE-R11.md names no single check")
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
