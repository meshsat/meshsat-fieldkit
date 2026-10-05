#!/usr/bin/env python3
"""apply_gen_sch_a_charger.py: DRAFT for board A's generator owner (task L4-E11, MESHSAT-1357, the U-04 question for the
consolidation of 2 October 2026, its fix rounds, and round 9 of 4 October 2026). NOT APPLIED to the tree by L4-E11; its author ran
it only on scratch copies (the tests write scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md sections 12 to 16 and 19, l4e11_power.out sections 12 to 16 and 19): the drawn BQ25731 has no
battery FET, so VSYS with no battery current (D1) and with the charge inhibited (D3) rest on statements TI does not print. TI's
BQ25730 (SLUSE65A, February 2021, revised January 2024) is the same 32-pin land with pin 21 as BATDRV, the gate drive of a P-channel
battery FET between VSYS and the charge sense resistor; its table prints VSYS_MIN's regulation and the system voltage with the
charge disabled, and every row the settings of L4-E4 to L4-E8 rest on is the BQ25731's row. The battery FETs are Nexperia
BUK6Y10-30P at BATDRV's least drive (8.5 V), sized to an RDS(on) allowance no printed maximum covers (section 16a, E11-36). Round 9
(section 19) adds a third in parallel, Q42, on record l9stk's junction limit (15.5, B-P2, SELECTED: the hottest battery FET at most
150 C held at 23.93 A from 76.25 C with the band and R17 in place), and holds the dock's VSYS branch and every RAIL_EN converter
off through the pack breaker's start (record l9stk's IF-1) by a VBAT supervisor, U46. Board E's auxiliary domain moves to VSYS over
the dock's pin 1 (section 15a; board E's half is apply_gen_sch_e_aux.py).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  U3      BQ25731RSNR (C2871872) becomes BQ25730RSNR (C5219071); pin 21 goes from NC to CH_BATDRV; its section comment.
  Q39,Q40,Q42 added: Nexperia BUK6Y10-30PX (C3278350), 30 V P-channel, LFPAK56, in parallel: sources on VBAT (VSYS), drains on
          CH_BATQ, gates on CH_BATDRV (pads 1 to 3 source, 4 gate, 5 the mounting base, drain), with the land key LFPAK56 (KiCad's
          Package_TO_SOT_SMD:LFPAK56); the pad map read against Nexperia's SOT669 drawing is the parts stream's. Q42 is round 9's
          third (Q41 is record l8r2's VIN_RAW cut-off FET).
  R17     the 5 mOhm RSR moves from VBAT to CH_BATQ (to CELL_FUSED), and R149 (SRP's 10 Ohm) from VBAT to CH_BATQ, as TI's
          Figure 9-1 draws the battery FET between VSYS and RSR.
  C236    added: Panasonic EEHZK1V181P (C242139) on VBAT, VSYS's effective capacitance by design (SLUSE65A 9.1: 50 uF), with its
          land key CPOL8 (KiCad's CP_Elec_8x10).
  J_DOCK  pin 1 from GND to VSYS_DOCK: board E's auxiliary domain (U12, the mixers' 12 V rail) fed from VSYS (board E's VSYS_E)
          through U42's eFuse (the review of the provisional fixes, L4-F03; section 16e).
  U42     added: TI TPS16630PWPR eFuse (SLVSET9G, held back), IN and P_IN on VBAT, UVLO (pin 7) on EF_UVLO (round 9: R88 and
          R89 from VBAT, held low by U46), OUT on VSYS_DOCK, OVP and MODE to GND (OVP off; auto-retry), R228 11.0k 0.1 % on ILIM
          (I(OL) = 18 / R(ILIM): 1.47 to 1.80 A, a steady setting), C237 22 nF on dVdT, C238 1 uF at IN, C239 0.1 uF at OUT, D23
          B540C-13-F (C72264) from GND to OUT, the land key SMC; SHDN, IMON, FLT and PGOOD open as TI allows; the land key
          HTSSOP20 (KiCad's HTSSOP-20-1EP, checked against TI's PWP0020 drawing by the parts stream); VBAT's declared loads gain
          U42's 1.32 A (section 18b); VSYS_DOCK declared AFTER VBAT (its fed_from) with source_ic (U42's OUT pins are the eFuse's
          power path: round 9, record l8p's finding L8P-F02).
  U46     added (round 9, IF-1): TI TPS37A010122DSKR (C3685740, the part U34 already is) on VBAT: channel 2 (UV) on SYS_UVS (R86
          91k over R87 10k, 1 %: 7.86 / 8.08 / 8.31 V falling, 8.01 / 8.24 / 8.48 V rising), CTR2 C105 100 nF (the release 79 to
          201 ms), RESET2 on EF_UVLO (U42 held off); channel 1 (OV) reads EF_UVLO on SENSE1, so RESET1 (SYS_HOLD_G, R105 100k
          from VBAT, D24 BZT52C12 clamp) is released while RESET2 holds and turns Q43 (2N7002, C8545) on, which pulls RAIL_EN
          low; VDD served by C238 (a bypass entry, class D, U46 beside U42).
  intent  CH_BATQ declared a segment of the pack path (source R17, loads Q39, Q40 and Q42, 10 A typical, 18 A peak); VBAT's
          source becomes Q39 (one of the three), fed from CH_BATQ; SYS_UVS, SYS_CTR, EF_UVLO and SYS_HOLD_G declared as nodes;
          the charger's sheet group names the three FETs, C236, U42 and its network, and U46 and its network.
The designators Q39, Q40, Q42, Q43, C236 to C239, C105, R228, R86 to R89, R105, D23, D24, U42 and U46 are free in gen_sch_a.py as
pinned by l4e11_power.py and disjoint from every board A draft composed in L4-E9's order (R86 to R89, R105 and C105 sit below every
draft's reference, so d8dec31's next-free reference stays R233 and C241); if another draft takes them first, renumber.

ORDER: independent of apply_gen_sch_a_guard.py (either order); apply with apply_gen_sch_e_aux.py (the dock's pin 1 on both
boards at once) and apply_pcb_interfaces_dock.py; with record l8p's apply_gen_sch_a_ptc.py in either order (that draft's PTC sits
at the three FETs' drain tabs, a layout requirement below). It withdraws E11-24's register row (the bank is not drawn). Firmware
rules come with it (E11-28): EN_OOA 0 at boot, ChargeCurrent written for any charge, the watchdog serviced, the battery FET's
registers left at their power-on values.

Usage:  apply_gen_sch_a_charger.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_charger"
_PAIR = ("# L4-E11 (MESHSAT-1357, the U-04 question for the consolidation and its fix rounds, 2 October 2026; round 9, 4 October 2026): THE\n"
         "# BQ25730's BATTERY FETS. BATDRV (pin 21) pulls the gates 10 V below VSYS (8.5 V at least, SLUSE65A p.17) to turn them fully on and\n"
         "# shorts them to VSYS to turn them off (pin table p.5); they run in linear mode to hold VSYS at VSYS_MIN under a depleted or absent\n"
         "# pack and as an ideal diode in supplement mode (8.4.1.1, p.38). TI asks a P-channel part of 20 V or more for 1 to 4 cells\n"
         "# with Ciss under 5 nF (9.2.2, p.92). Three Nexperia BUK6Y10-30P (17 April 2020): 30 V, VGS +-20 V, 175 C, RDSon at most 10\n"
         "# mOhm at -10 V and 25 C, 16 at 175 C, 25 at -4.5 V; Ciss 2.36 nF typical each (7.08 for the three at -15 V, about 8.61 near 0 V:\n"
         "# over TI's 5 nF, OPEN on E11-37 with Q-TI-17 (a) to (f)); ISM 320 A each for 10 us at Tmb 25 C. No printed maximum covers BATDRV's\n"
         "# 8.5 V hot: each is SIZED to an RDS(on) allowance of 21.1 mOhm at 8.5 V and 150 C, which E11-36 confirms or reverses. E11-29 is\n"
         "# the junction limit of record l9stk 15.5 (round 9): the hottest junction at most 150 C held at 23.93 A from 76.25 C with the band\n"
         "# (9.16 K) and R17 (2.86 W) in place, for ANY split of the RDS(on) spread under the allowance (round 11: one FET at half the\n"
         "# others' RDS(on) takes half the current, 9/8 of the even split's loss), so the three's installed (Zself + 2 Zmut) at most\n"
         "# 40.78 K/W with R17 placed apart (record l9stk's even-split 45.88 K/W times 8/9; with Zself and Zmut read apart, 45.88 x\n"
         "# 8 (1 - m)(1 + 2 m) / 9 for m = Zmut / Zself under 1/4) (the pair's fallback 20.39 K/W, the even split its worst; the\n"
         "# pair's former 33.12 K/W target at +70 C air is withdrawn). LAYOUT (Layer 9, board A's PCB generator): Q39, Q40 and Q42\n"
         "# side by side on one CH_BATQ drain pour and one VBAT source pour, the gates from one CH_BATDRV\n"
         "# node by equal branches; R17 off that pour (its coupling into each junction at most 1 K/W, read by heating R17 alone); record\n"
         "# l8p's enable-loop PTC at the three drain tabs' centroid, within 3 mm of each tab's edge; the two pours' largest paths, each from\n"
         "# its current's joint to the FET lands, summed at most 0.1 mOhm at the operating temperature, each junction's worst-split figure\n"
         "# at most 41.98 K/W and R17's coupling at most 0.294 K/W (round 15, V2RF-m5: the design target, so the limit's line passes with\n"
         "# its uncertainty; the acceptance bars unchanged). The docking pulse is taken whole in\n"
         "# ONE body diode, no sharing credited, and its whole hot waveform is E11-30's (L4-E11 sections 16, 17, 19 and 21).\n"
         "# L4-E11 (the review of the provisional fixes, L4-F03, 2 October 2026): THE DOCK'S VSYS BRANCH. J_DOCK pin 1 carries VSYS to\n"
         "# board E's auxiliary domain over one Preci-Dip 813 (3.5 A operating maximum). U42 regulates a sustained overload to 1.47 to\n"
         "# 1.80 A (SLVSET9G p.8 rows over TJ -40 to 125 C at VIN - VOUT 1 V, inferred at R228 11.0k by Equation 6), a steady setting and\n"
         "# not an instantaneous ceiling; limits for at most 202 ms and retries after 500 to 800 ms (Table 8-1, MODE to GND); a start into\n"
         "# a short limits at the setting until thermal regulation, then times out 1.1 to 1.5 s after regulation begins (the total not\n"
         "# printed); a short's first microseconds (566 A only an extrapolation), the pins' spikes and the contact's pulse are\n"
         "# E11-38's (L4-E11 section 17a). C238 at IN and C239 at OUT are TI's 0.1 uF minimum (6.3); D23 is TI's Schottky at OUT for the\n"
         "# output loop's negative spike (9.4.1, 9.5.1); U42's IN sits within 20 nH of C236 and C23 to C25 (a layout requirement).\n"
         "# L4-E11 round 9 (record l9stk's IF-1): THE VSYS HOLD. The pack breaker on board P starts its output by dv/dt over at most 40.7 ms\n"
         "# once its enable and hold release it; a load on VSYS during that ramp is carried at the breaker FET's full input-to-output drop.\n"
         "# U46 (the TPS37A010122 U34 already is; SNVSBJ1E) watches VBAT on SENSE2 through R86 / R87 and holds two things off until VBAT has\n"
         "# stood over its rising threshold (8.01 to 8.48 V) for CTR2's release, 79 to 201 ms (C105 100 nF, SNVSBJ1E Equations 1 to 3):\n"
         "# RESET2 pulls U42's UVLO (EF_UVLO) low, so the dock's VSYS branch stays open; channel 1 reads EF_UVLO on SENSE1, so its RESET1\n"
         "# is released while RESET2 holds, R105 lifts SYS_HOLD_G (D24 clamps it under 12.7 V) and Q43 pulls RAIL_EN low, which holds U12,\n"
         "# U41 and everything behind +3V3 whatever U1 asserts. A fall under 7.86 to 8.31 V re-asserts both within 90 us (CTS2 open), so a\n"
         "# quick undocking and redocking is held the same way. R88 / R89 set U42's own UVLO at 5.95 to 6.90 V, under U46's, and keep\n"
         "# EF_UVLO over U42's 1.224 V and SENSE1's 0.808 V from VBAT 8.01 V once released. The breaker's PGD is not used (L4-E11 19).\n"
         "ic(\"U42\", 21, \"TPS16630PWPR 60 V 6 A eFuse: the dock's VSYS branch to board E (I(OL) 18 / 11.0k)\", \"HTSSOP20\", {\"1\": \"VBAT\", \"2\": \"VBAT\", \"3\": \"VBAT\", \"4\": \"NC\", \"5\": \"NC\", \"6\": \"VBAT\", \"7\": \"EF_UVLO\", \"8\": \"GND\", \"9\": \"GND\", \"10\": \"EF_DVDT\", \"11\": \"EF_ILIM\", \"12\": \"GND\", \"13\": \"NC\", \"14\": \"NC\", \"15\": \"NC\", \"16\": \"NC\", \"17\": \"NC\", \"18\": \"VSYS_DOCK\", \"19\": \"VSYS_DOCK\", \"20\": \"VSYS_DOCK\", \"21\": \"GND\"})\n"
         "r(\"R228\", \"11k 0.1%\", \"EF_ILIM\", \"GND\")    # U42's overload limit, 18 / 11.0 = 1.64 A typical\n"
         "c(\"C237\", \"22n 50V C0G\", \"EF_DVDT\", \"GND\")   # U42's output slew, TI's characterised 22 nF\n"
         "c(\"C238\", \"1u 50V X7R\", \"VBAT\", \"GND\")      # at U42's IN (TI 9.4.1: at least 1 uF where surges reach the input), and U46's VDD bypass\n"
         "c(\"C239\", \"100n 50V X7R\", \"VSYS_DOCK\", \"GND\")   # at U42's OUT (TI 6.3: 0.1 uF minimum at OUT)\n"
         "part(\"D23\", \"Device\", \"D_Schottky\", \"B540C-13-F 40 V 5 A Schottky, U42's output clamp (cathode on OUT)\", \"SMC\", {\"1\": \"VSYS_DOCK\", \"2\": \"GND\"}, \"C72264\")\n"
         "r(\"R88\", \"100k 1%\", \"VBAT\", \"EF_UVLO\", lcsc=\"C25803\"); r(\"R89\", \"22k 1%\", \"EF_UVLO\", \"GND\", lcsc=\"C31850\")   # U42's own UVLO 5.95 to 6.90 V\n"
         "ic(\"U46\", 11, \"TPS37A010122DSKR 65 V OV/UV supervisor: the VSYS hold through the pack breaker's start (IF-1)\", \"WSON10\", {\n"
         " \"1\": \"VBAT\", \"2\": \"EF_UVLO\", \"3\": \"SYS_UVS\", \"4\": \"SYS_HOLD_G\", \"5\": \"EF_UVLO\", \"6\": \"NC\", \"7\": \"NC\", \"8\": \"NC\", \"9\": \"SYS_CTR\", \"10\": \"GND\", \"11\": \"GND\"}, \"C3685740\")\n"
         "r(\"R86\", \"91k 1%\", \"VBAT\", \"SYS_UVS\", lcsc=\"C23265\"); r(\"R87\", \"10k 1%\", \"SYS_UVS\", \"GND\", lcsc=\"C25804\")   # U46 channel 2 (UV) on VBAT: 8.08 V falling, 8.24 V rising\n"
         "c(\"C105\", \"100n\", \"SYS_CTR\", \"GND\", lcsc=\"C14663\")   # CTR2: the hold's release, 79 to 201 ms\n"
         "r(\"R105\", \"100k\", \"VBAT\", \"SYS_HOLD_G\", lcsc=\"C25803\"); part(\"D24\", \"Device\", \"D_Zener\", \"BZT52C12-7-F zener, the RAIL_EN hold's gate clamp\", \"SOD123\", {\"1\": \"SYS_HOLD_G\", \"2\": \"GND\"}, \"C124196\")\n"
         "part(\"Q43\", \"Transistor_FET\", \"2N7002\", \"2N7002: SYS_HOLD_G high = RAIL_EN held low (1 G, 2 S, 3 D)\", \"SOT23\", {\"1\": \"SYS_HOLD_G\", \"2\": \"GND\", \"3\": \"RAIL_EN\"}, \"C8545\")\n"
         "for _qb in (\"Q39\", \"Q40\", \"Q42\"): nfet(_qb, \"BUK6Y10-30PX 30 V P-FET (the BQ25730's battery FET, one of three in parallel: S on VSYS, D toward RSR)\", \"CH_BATDRV\", \"CH_BATQ\", \"VBAT\", fp=\"LFPAK56\", lcsc=\"C3278350\")")
_BATQ = ('\n# L4-E11 (the U-04 question for the consolidation; round 9): CH_BATQ, the copper between the BQ25730\'s battery FETs Q39, Q40 and\n'
         '# Q42 and the RSR shunt R17. The pack current crosses it in both directions, charge and discharge, so it is declared a segment of the\n'
         '# pack path as CELL_FUSED is, with the same 10 A typical and 18 A peak.\n'
         '_intent.rail("CH_BATQ", 14.4, 10.0, 18.0, "R17", v_work=16.8, converted=False, series_of="CELL+", loads={"Q39": 3.34, "Q40": 3.33, "Q42": 3.33},\n'
         '             note="L4-E11: the node between the battery FETs Q39, Q40 and Q42 (drains) and the RSR shunt R17, SRP through R149; the "\n'
         '                  "pack\'s charge and discharge current, 10.0 A typical and 18.0 A peak, counted once as a segment of CELL+")')
_VBAT_END = 'note="the 4S system node (VSYS) behind the RSR shunt R17; 10 A continuous, 18 A peak by the pack\'s rating (32.55)")'
_DOCKR = ('\n# L4-E11 (L4-F03, section 18; round 9, record l8p\'s finding L8P-F02): VSYS_DOCK is declared AFTER VBAT, the rail it is fed from, and\n'
          '# names U42 with source_ic: the eFuse\'s OUT pins 18 to 20 are its power path, the internal FET\'s source, not a sense pin.\n'
          '_intent.rail("VSYS_DOCK", 14.4, 1.32, 1.32, "U42", source_ic="U42 (TPS16630) OUT pins 18 to 20 are the internal power FET\'s source, the "\n'
          '             "branch\'s whole current; no inductor or shunt follows it", always_on=True, v_work=17.4, converted=False, fed_from="VBAT",\n'
          '             always_on_why="VSYS through the eFuse U42, which opens on its own overload, short or thermal fault and retries, and is held "\n'
          '                           "open by U46 until VBAT has stood over 8.48 V for 79 ms (the pack breaker\'s start, IF-1); nothing else switches it",\n'
          '             loads={"J_DOCK": 1.32},\n'
          '             note="L4-E11 (L4-F03, section 18): U42\'s output to J_DOCK pin 1, board E\'s VSYS_E (U12 0.8 A and the mixers\' 12 V rail U22 0.52 A at the floor); limited to 1.47 to 1.80 A")\n'
          '_r9 = "L4-E11 round 9, the VSYS hold U46 (IF-1): "\n'
          '_intent.node("SYS_UVS", 2.89, _r9 + "U46 SENSE2, VBAT over R86 / R87 (10 / 101 of it): 2.89 V at the SMCJ18A\'s 29.2 V clamp, SENSE 65 V graded")\n'
          '_intent.node("SYS_CTR", 5.5, _r9 + "U46 CTR2\'s delay capacitor C105: SNVSBJ1E recommends 0 to 5.5 V on the pin (6 V absolute)")\n'
          '_intent.node("EF_UVLO", 5.35, _r9 + "U42 UVLO, U46 RESET2 and SENSE1: VBAT over R88 / R89 (22 / 122 of it, 1 %), 5.35 V at the 29.2 V clamp; "\n'
          '             "0.3 V at most while RESET2 holds", v_work=3.14)\n'
          '_intent.node("SYS_HOLD_G", 12.7, _r9 + "Q43\'s gate, U46 RESET1, VBAT through R105 clamped by D24 (BZT52C12, 11.4 to 12.7 V, DS18004)")\n'
          '_intent.bypass("C238", "U46", "1", cls="D", basis="TI SNVSBJ1E (TPS37A) pin table: VDD \'Input Supply Voltage: Bypass with a 0.1 uF capacitor to GND\'; "\n'
          '               "C238, 1 uF X7R on VBAT at U42\'s IN, serves it with U46 placed beside it (L4-E11 round 9)")')
EDITS = [
    ("# --- charger BQ25731 (bq25731-datasheet.pdf, QFN-32 RSN; no BATFET, so the system sits on VSYS and the pack on the far side of RSR, SLUSE66A Figure 10-1): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,",
     "# --- charger BQ25730 (SLUSE65A, held back; QFN-32 RSN; an NVDC charger: the system on VSYS, the battery FETs Q39, Q40 and Q42 and RSR between it and the pack, SLUSE65A Figure 9-1; L4-E11): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,"),
    ('ic("U3", 33, "BQ25731RSNR 1 to 5 cell buck-boost charger, 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {',
     'ic("U3", 33, "BQ25730RSNR 1 to 5 cell NVDC buck-boost charger (battery FETs Q39, Q40 and Q42), 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {'),
    ('"21": "NC", "22": "VBAT"', '"21": "CH_BATDRV", "22": "VBAT"'),
    ('"33": "GND"}, "C2871872")', '"33": "GND"}, "C5219071")'),
    ('("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", "CSD17577Q5A 30 V N-FET")): nfet(_qr, _v, _g, _d, _s)',
     '("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", "CSD17577Q5A 30 V N-FET")): nfet(_qr, _v, _g, _d, _s)\n' + _PAIR),
    ('r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "VBAT", "CELL_FUSED", "RS2512")',
     'r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "CH_BATQ", "CELL_FUSED", "RS2512")'),
    ('r("R149", "10R", "VBAT", "CH_SRP_F")            # the same on SRP, so the pair sees one filter and not a half; SRP is the system side, VSYS (S-04, 26 Sep 2026)',
     'r("R149", "10R", "CH_BATQ", "CH_SRP_F")         # the same on SRP, so the pair sees one filter and not a half; SRP is the battery FETs\' side of RSR (L4-E11, SLUSE65A Figure 9-1)'),
    ('for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "VBAT", "GND", "C1210")   # the charger\'s VSYS capacitors, at Q10\'s drain (S-04, 26 Sep 2026)',
     'for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "VBAT", "GND", "C1210")   # the charger\'s VSYS capacitors, at Q10\'s drain (S-04, 26 Sep 2026)\n'
     'c("C236", "180u 35V Panasonic EEHZK1V181P hybrid polymer (10.2 mm)", "VBAT", "GND", "CPOL8", lcsc="C242139")   # VSYS\'s 50 uF effective by design (SLUSE65A 9.1; L4-E11 D5)'),
    ('"CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL10": "Capacitor_SMD:CP_Elec_10x10",',
     '"CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL10": "Capacitor_SMD:CP_Elec_10x10", "CPOL8": "Capacitor_SMD:CP_Elec_8x10", "LFPAK56": "Package_TO_SOT_SMD:LFPAK56", "HTSSOP20": "Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm", "SMC": "Diode_SMD:D_SMC",'),
    ('("CHARGER BQ25731: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), PACK BEYOND RSR, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "C16",',
     '("CHARGER BQ25730: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), BATTERY FETS Q39, Q40 AND Q42 AND RSR TO THE PACK, THE DOCK VSYS EFUSE U42 AND THE VSYS HOLD U46, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "Q39", "Q40", "Q42", "C236", "U42", "R228", "C237", "C238", "C239", "D23", "R88", "R89", "U46", "R86", "R87", "C105", "R105", "D24", "Q43", "C16",'),
    ('_intent.rail("VBAT", 14.4, 10.0, 18.0, "R17", always_on=True, v_work=16.8, converted=False, fed_from="CELL_FUSED",',
     '_intent.rail("VBAT", 14.4, 10.0, 18.0, "Q39", always_on=True, v_work=16.8, converted=False, fed_from="CH_BATQ",'),
    ('loads={"U4": 2.0, "Q28": 2.22,', 'loads={"U42": 1.32, "U4": 2.0, "Q28": 2.22,'),
    ('"10.0 A typical and 18.0 A peak, and is counted once as a segment of CELL+")',
     '"10.0 A typical and 18.0 A peak, and is counted once as a segment of CELL+")' + _BATQ),
    (_VBAT_END, _VBAT_END + _DOCKR),
    ('spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1-7 GND, 8 SHORE_INHIBIT,',
     'spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1 VSYS_DOCK (VBAT through the eFuse U42) to board E\'s VSYS_E, the auxiliary domain\'s feed (L4-E11), 2-7 GND, 8 SHORE_INHIBIT,'),
    ('The pack reaches it through the 25 A blade F1 and the RSR shunt R17, opened only by the pack\'s own BQ4050 FETs and the blade;',
     'The pack reaches it through the 25 A blade F1, the RSR shunt R17 and the battery FETs Q39, Q40 and Q42 (on with the battery alone, SLUSE65A p.27; their body diodes otherwise; L4-E11), opened only by the pack\'s own BQ4050 FETs and the blade;'),
    ('{"1": "GND", "2": "GND", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "DOCK_SPARE"})',
     '{"1": "VSYS_DOCK", "2": "GND", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "DOCK_SPARE"})'),
]

def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: task L4-E11 drafts this change for board A's generator owner and never applies it. Writing the repository's
# own gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written
# (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E11's values wait on an accepted check")
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
