#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357), board B: DRAFT circuit changes for board B's generator (v2/ecad/tools/gen_sch_b.py), for
the integrator to apply, regenerate on the KiCad box and read back with readback_d4e.py. NOT applied by this stream (a circuit
change is drafted as an apply script for the generator; KiCad is not on the stream's host). Every change is taken by the session
under the owner's standing rule of 26 September 2026 and is reversible by reverting the lines this script writes.

FIVE CHANGES, each closing one item of FEA-002's layout-entry stage (EMCON.md section 4d has the arithmetic in full):

B-1  SD-EMC-2, the RockBLOCK 9704 (J_RB9704). Ground Control, hardware page (v2/vendor/rockblock/groundcontrol-docs-rockblock-
     9704-hardware-20260927.txt): pin 7 I_BTD "When this pin is LOW there should be no voltage applied to any input pins, other
     than I_EN", and the shutdown sequence "Set all pins connected to RockBLOCK 9704 inputs tristate (high-Z) or logic low";
     signal thresholds Logic In LOW max 0.4 V, Logic Out HIGH 2.9 to 3.4 V at 2 mA. As drawn, the module's two host-driven
     inputs RXD (pin 14, from U18's TXD) and P_EN (pin 6, from U6's IO1_7) are driven whatever the module does, and its outputs
     I_BTD and XMT_G (pins 7, 8) are pulled up to +3V3_DEV through R41 and R42, so with +5V_RB removed by EMCON a live 3.3 V
     sits on four of its pins. THE CHANGE: RB_GO = RB_IEN AND RB_STATUS (U537), and each input line is its source AND RB_GO
     (U538 RXD, U539 P_EN), three SN74LVC1G08 on +3V3_DEV (Ioff 10 uA, SCES217AA 5.5), R533 and R534 (10 k 1%) holding the two
     inputs low with the gates unpowered (0.10 V); R41 and R42 become 2.2 k 1% pull-DOWNS, so I_BTD and XMT_G read low with the
     module off and sit at most 100 uA (U7's pull-up, SCPS131J IIL) x 2.2 k = 0.22 V; R535 (10 k 1%) holds the module's TXD
     (pin 13) against the CP2102N's weak pull-up (10 to 30 uA, CP2102N data sheet Rev 1.5, IPU): 0.30 V. EMCON asserted:
     RB_IEN low (U536) gives RB_GO low, and every input of the module sits at the gates' VOL, 0.1 V at 100 uA (SCES217AA 5.5).
     Released: the lines follow their sources only while the module says it is booted, the maker's own startup order.
     One stated departure from the maker's shutdown order: the inputs fall with I_EN, before I_BTD falls, rather than after
     it (RB_GO reads RB_IEN, so EMCON_HW gains no reader); firmware ceases serial traffic first, the maker's step 1, and
     under EMCON the supply goes at the same instant.
B-2  SD-EMC-2, the two E72 CC2652P (U13, U14). As drawn, each CP2102N (U16, U17, on +5V_DEV, not gated) drives the module's RX,
     RESET_N and BSL push-pull (TXD, RTS, DTR), and RESET_N and BSL also reach +3V3_ZB through R28 to R31: with U22 off, a
     3.3 V source with no series resistance feeds the dead rail, whose only sink is U22's RPD (stated at VIN 5, 12 and 18 V, not
     at U22's 3.3 V, SLVSDH0C 7.5). THE CHANGE: the six host-driven lines pass through SN74LVC2G07 open-drain buffers on
     +3V3_DEV (U540 to U542; TI SCES308L: VOL 0.1 V at 100 uA, Ioff 10 uA, inputs 5.5 V tolerant, "Inputs and Open-Drain
     Outputs Accept Voltages" up to 5.5 V), whose outputs only pull low, pulled up to the GATED rail +3V3_ZB (R28 to R31 as
     drawn; R536, R537 4.7 k 1% new for RX), so with U22 off nothing drives a line up; R538 (4.7 k 1%) bleeds +3V3_ZB: the
     sources left into it are the CP2102N's weak pull-ups into each module's TXD (2 x 30 uA) and, with +3V3_DEV lost, the six
     outputs' Ioff (6 x 10 uA): 120 uA into 4.653 k is 0.56 V, under the E72's 1.9 V minimum (Ebyte E72 user manual,
     operating voltage 1.9 to 3.8 V). The bleeder costs 0.71 mA while the radios run.
B-3  SD-EMC-2, the E22-900M30S (U12). As drawn, nine CM5 slot 3 pins reach the module with no series resistance (RXEN, TXEN,
     NRST, MOSI, SCK, NSS driven by the host; DIO1, BUSY, MISO read by it, which firmware can also drive, fault F3). Series
     resistance cannot close it: at the E22's 10 Mbps SPI (user manual v1.20, "SPI 0-10Mbps") a 10 to 90 percent edge within
     15 ns at about 10 pF allows at most 680 Ohm, and nine lines at 3.3 V through 680 Ohm into U21's RPD (400 Ohm maximum at
     5 V) hold +5V_LORA at about 2.8 V, over the module's 2.5 V minimum (user manual v1.20, operating voltage 2.5 to 5.5 V).
     THE CHANGE: LORA_GO, a 74LVC1G34 copy of E22_EN (U544, II +-1 uA at VCC 0 to 5.5 V, DS36108, so E22_EN's hold with U504
     unpowered moves by 1 uA x 25.25 k = 25 mV), gates the six host-driven lines in SN74LVC1G08s (U545 to U550); the module's
     three outputs reach the host through 74LVC1G34 buffers (U551 to U553); every new part runs from slot 3's own +3V3_CM3,
     the rail that powers the host pins (EMCON L3's rule), so with the module's host dead the gates are dead with it. R539 to
     R544 (100 k 1%) hold the module's side of DIO1, BUSY, MISO, TXEN, RXEN and NRST low when their driver is off. R546 to R550 (100 k 1%)
     hold the gates' host-side inputs low while slot 3 has not configured its pins (NSS keeps R25). EMCON
     asserted: every line into the module at the gates' VOL, 0.1 V at 100 uA; the module's own outputs see only the buffers'
     inputs, 1 uA each. Cost: ten single gates and ten capacitors; the round trip of MISO gains two gate delays (SN74LVC1G08
     3.6 ns maximum at 3.3 V, 15 pF, SCES217AA 5.6); SPI3_MISO is now driven by U553 whenever slot 3 runs, so the bench
     breakout J_SPI3's CE0 can carry no second device that drives MISO.
B-4  L4 case (2) on U536 (the RockBLOCK's ENABLE gate). With +3V3_DEV in 0 to 1.65 V, U536's output is unspecified up to
     1.65 V, which the maker's Logic In LOW (0.4 V maximum) does not cover, and the module keeps its supercapacitors (EMCON.md
     4.4). A divider fails (the maker's 0.4 V LOW and 2.0 V HIGH cannot both be met from a gate at most at 1.65 V). THE CHANGE:
     U543, a TPS3808G30 (SBVS050N: VIT 2.79 V +-1.25 percent at -40 to +85 C, VDD 1.7 to 6.5 V, open-drain RESET, VOL 0.4 V at
     1 mA for VDD 1.8 to 6.5 V, SENSE independent of VDD) powered from +5V_DEV, the rail +3V3_DEV is made from (U25, AP63203,
     VIN +5V_DEV), watches +3V3_DEV and holds RB_IEN low whenever it is under VIT; U536 now drives RB_IEN through R532 (2.2 k
     1%), so in its band it pushes at most 1.65 V / 2.178 k = 0.76 mA into the supervisor, under the 1 mA of its VOL row:
     RB_IEN at most 0.4 V. R527 becomes 15 k 1%. Released (EMCON off, the request high, the supervisor released, IOH 300 nA):
     RB_IEN at least 2.08 V (U536 VOH 2.4 V through 2.222 k, the maker's divider 2.457 V through 166 k at V_IN 4.0 V, into
     14.85 k, less U537's 5 uA), over the maker's 2.0 V. EMCON asserted: at most 0.15 V. Every rail lost: (10 + 10 + 0.3) uA
     into 15 k parallel 166 k, 0.28 V. Residual: SBVS050N gives the SENSE-to-RESET delay as 20 us typical with no maximum, so a
     +3V3_DEV that falls from 2.79 V into the band faster than that is a race (bench E-11 with E-04).
B-5  D4E-F2, the Tpr hold of SD-EMC-1r8 (U221). Quectel RM520N HD v1.1 Table 9: FULL_CARD_POWER_OFF# VIL max 0.2 V, VIH min
     1.19 V, "Pull down with a 100 kOhm resistor" inside the module. As drawn, U221's open-drain RESET holds the pin against
     R238 (10 k to +3V3_S2A): at least 0.31 mA, where SBVS050N states VOL only as 0.4 V at 1 mA, so a pin inside Quectel's 0.2 V
     is not shown for the Tpr hold at desk. THE CHANGE: U221's RESET drives a new net 5G_TPR_n (R545 100 k 1% to +3V3_S2A, the
     maker's 10 k to 1 M range), which U554, an SN74LVC2G07 on slot 2's +3V3_CM2 (U220's rail), repeats open-drain onto
     5G_PWROFF_n; R238 becomes 100 k 1%, so the held pin carries at most 3.545 V / 99 k = 36 uA and U554's VOL is at most
     0.1 V (100 uA row, SCES308L 6.5), under 0.2 V; released, the pin sits at 3.135 V x 100 / 201 = 1.56 V, over 1.19 V (the
     module's 100 k taken nominal, its tolerance unstated: INFERRED). Nothing of the inhibit moves: under EMCON U220 holds the
     pin on a rail that is removed.

READ-BACK (after regeneration): readback_d4e.py --board B <regenerated pcb-b-compute.net> asserts every node these changes
make, net by net, and that the old direct connections are gone (J_RB9704 pins 6 and 14 no longer on U6 or U18; U12's nine
signal pins on no CM5 pin; U13 and U14's RX, RESET_N and BSL on no CP2102N pin; R41, R42 to GND; U543 SENSE on +3V3_DEV;
U554 1Y on 5G_PWROFF_n). Then tools/tx_inhibit.py (RF-002's walk) and the suite are re-taken; the walk's classes for the
TPS3808 (U543) and the SN74LVC2G07 are the tools author's (EMCON.md section 8), and until they land the walk may read the new
parts as unmodelled, which is a tool item.

The script asserts every anchor is present exactly once, that the new text differs, re-parses the file with ast, and refuses a
second run (the marker D4E-B already present).

usage: apply_b_d4e.py <worktree root> [--dry-run]"""
import ast, os, sys

MARK = "D4E-B"

EDITS = []   # (anchor, replacement)

# ---------- helper: SN74LVC2G07 (after the lvc1g34 helper)
A_HELPER = '''def lvc1g34(uref, a, y, vcc, cref, why):
    ic(uref, 5, "74LVC1G34 buffer (Diodes 74LVC1G34W5-7, 2 A 4 Y): " + why, "SOT235", {"1": "NC", "2": a, "3": "GND", "4": y, "5": vcc}, "C526347"); _dec(uref, cref, vcc)
'''
EDITS.append((A_HELPER, A_HELPER + '''#   SN74LVC2G07DBVR (TI SCES308L, May 2015, pin table, DBV): 1 1A 2 GND 3 2A 4 2Y 5 VCC 6 1Y, non-inverting open-drain outputs;
#     VOL 0.1 V at 100 uA (VCC 1.65 to 5.5 V), 0.4 V at 16 mA (VCC 3 V); II +-5 uA, Ioff +-10 uA; inputs and outputs 0 to 5.5 V
#     (6.3, 6.5); JLCPCB C37708, board A's U40 code (stream d4emcon, D4E-B, 29 September 2026).
def lvc2g07(uref, a1, y1, a2, y2, vcc, cref, why):
    ic(uref, 6, "SN74LVC2G07DBVR dual open-drain buffer (1 1A 6 1Y, 3 2A 4 2Y): " + why, "SOT236", {"1": a1, "2": "GND", "3": a2, "4": y2, "5": vcc, "6": y1}, "C37708"); _dec(uref, cref, vcc)
'''))

# ---------- +3V3_DEV load table
A_LOADS = '_3V3_LOADS["U536"] = 0.002   # stream w4b (27 September 2026): the RockBLOCK ENABLE gate, an SN74LVC1G08 (EMCON.md 4.4)\n'
EDITS.append((A_LOADS, A_LOADS + '''for _u in ("U537", "U538", "U539", "U540", "U541", "U542"): _3V3_LOADS[_u] = 0.002   # stream d4emcon (D4E-B, 29 September 2026): SD-EMC-2's RockBLOCK gates and E72 open drains, ICC 10 uA each at most (SCES217AA, SCES308L)
'''))

# ---------- B-5: R238 to 100 k, U221 onto 5G_TPR_n, U554 repeats it (inside the slot loop, slot 2)
A_R238 = 'r(R(38), "10k", "5G_PWROFF_n", a33); nfet(Q(7), "5G_OFF", "GND", "5G_PWROFF_n", "2N7002 expander -> FULL_CARD_POWER_OFF#")'
EDITS.append((A_R238, 'r(R(38), "100k 1%", "5G_PWROFF_n", a33, lcsc="C25803"); nfet(Q(7), "5G_OFF", "GND", "5G_PWROFF_n", "2N7002 expander -> FULL_CARD_POWER_OFF#")   # D4E-F2: 100 k so the held pin carries at most 36 uA (U554, SCES308L 100 uA row)'))
A_U221 = '{"1": "5G_PWROFF_n", "2": "GND", "3": "NC", "4": "5G_TPR_CT", "5": a33, "6": a33}, "C189211")'
EDITS.append((A_U221, '{"1": "5G_TPR_n", "2": "GND", "3": "NC", "4": "5G_TPR_CT", "5": a33, "6": a33}, "C189211")'))
A_R297 = 'r(R(97), "49.9k 1%", a33, "5G_TPR_CT", "R", "C23184"); c("C200", "100n", a33, "GND", bypass=(U(21), "6"))\n'
EDITS.append((A_R297, A_R297 + '''        # D4E-F2 (stream d4emcon, 29 September 2026; taken by the session under the owner's standing rule of 26 September 2026):
        # Quectel HD v1.1 Table 9 asks FULL_CARD_POWER_OFF# at most 0.2 V for "turn off" and at least 1.19 V for "turn on", with a
        # 100 kOhm pull-down inside the module. U221's RESET held the pin against R238 (10 k) at 0.31 mA or more, where SBVS050N
        # states VOL only as 0.4 V at 1 mA. Now U221 drives 5G_TPR_n (R545, 100 k 1% to the rail it watches, inside the maker's
        # 10 k to 1 M) and U554, an SN74LVC2G07 on +3V3_CM2 (U220's rail), repeats it open-drain onto the pin, with R238 at 100 k:
        # at most 36 uA held, VOL 0.1 V (SCES308L 6.5, 100 uA row); released 1.56 V (module pull-down nominal, INFERRED). U554's
        # second channel is spare, its input on GND (SCES308L 6.3 note 1).
        lvc2g07("U554", "5G_TPR_n", "5G_PWROFF_n", "GND", "NC", cm33, "C685", "U221's Tpr hold repeated onto FULL_CARD_POWER_OFF# (D4E-F2); channel 2 spare")
        r("R545", "100k 1%", "5G_TPR_n", a33, lcsc="C25803")
'''))

# ---------- B-3: the E22's lines
A_E22 = 'e22.update({9: "+5V_LORA", 10: "+5V_LORA", 6: "LORA_RXEN", 7: "LORA_TXEN", 8: "NC", 13: "SPI3_IO24", 14: "SPI3_IO23", 15: "SPI3_IO26", 16: "SPI3_MISO", 17: "SPI3_MOSI", 18: "SPI3_SCLK", 19: "SPI3_CE1", 21: "LORA_ANT"})'
EDITS.append((A_E22, 'e22.update({9: "+5V_LORA", 10: "+5V_LORA", 6: "LORA_RXEN_G", 7: "LORA_TXEN_G", 8: "NC", 13: "LORA_DIO1", 14: "LORA_BUSY", 15: "LORA_NRST", 16: "LORA_MISO", 17: "LORA_MOSI", 18: "LORA_SCLK", 19: "LORA_NSS", 21: "LORA_ANT"})   # D4E-B B-3: the module side of SD-EMC-2\'s gates'))
A_U21 = 'r("R25", "10k", "SPI3_CE1", "+3V3_S3B")\n'
EDITS.append((A_U21, A_U21 + '''# SD-EMC-2 for the E22 (stream d4emcon, D4E-B B-3, 29 September 2026; taken by the session under the owner's standing rule of 26
# September 2026). Nine CM5 slot 3 pins reached the module with no series resistance, and a series resistance cannot bound them at
# the module's 10 Mbps SPI (EMCON.md 4d). LORA_GO copies E22_EN (U544, II +-1 uA at VCC 0 to 5.5 V, DS36108); the six host-driven
# lines pass only while it is high (U545 to U550, SN74LVC1G08, VOL 0.1 V at 100 uA, SCES217AA 5.5), and the module's three outputs
# reach the host through U551 to U553 (74LVC1G34), so no host pin, driven or pulled, touches the module. Every part runs from slot
# 3's own +3V3_CM3 (EMCON L3). R539 to R544 hold the module's side low while its driver is off. Reverse: the module's pins back on
# the SPI3_* and LORA_RXEN/TXEN nets, U544 to U553, R539 to R544 and C674 to C683 out.
lvc1g34("U544", "E22_EN", "LORA_GO", "+3V3_CM3", "C674", "LORA_GO = E22_EN, one load on the enable (SD-EMC-2, D4E-B)")
for _u, _a, _y, _c, _w in (("U545", "LORA_RXEN", "LORA_RXEN_G", "C675", "RXEN"), ("U546", "LORA_TXEN", "LORA_TXEN_G", "C676", "TXEN"),
                           ("U547", "SPI3_IO26", "LORA_NRST", "C677", "NRST"), ("U548", "SPI3_MOSI", "LORA_MOSI", "C678", "MOSI"),
                           ("U549", "SPI3_SCLK", "LORA_SCLK", "C679", "SCK"), ("U550", "SPI3_CE1", "LORA_NSS", "C680", "NSS")):
    lvc1g08(_u, _a, "LORA_GO", _y, "+3V3_CM3", _c, "the E22's %s only while its supply is enabled (SD-EMC-2, D4E-B)" % _w)
for _u, _a, _y, _c, _w in (("U551", "LORA_DIO1", "SPI3_IO24", "C681", "DIO1"), ("U552", "LORA_BUSY", "SPI3_IO23", "C682", "BUSY"),
                           ("U553", "LORA_MISO", "SPI3_MISO", "C683", "MISO")):
    lvc1g34(_u, _a, _y, "+3V3_CM3", _c, "the E22's %s to the host, no host pin on the module (SD-EMC-2, D4E-B)" % _w)
for _r, _n in (("R539", "LORA_DIO1"), ("R540", "LORA_BUSY"), ("R541", "LORA_MISO"), ("R542", "LORA_TXEN_G"), ("R543", "LORA_RXEN_G"), ("R544", "LORA_NRST")):
    r(_r, "100k 1%", _n, "GND", lcsc="C25803")
# The gates' host-side inputs must not float while slot 3's firmware has not configured its pins (SCES217AA 6.3 note: "All
# unused inputs of the device must be held at VCC or GND"): R546 to R550 (100 k 1%) hold RXEN, TXEN, NRST, MOSI and SCK low
# there (the PA off and the module in reset until the host drives them); NSS keeps R25's pull-up.
for _r, _n in (("R546", "LORA_RXEN"), ("R547", "LORA_TXEN"), ("R548", "SPI3_IO26"), ("R549", "SPI3_MOSI"), ("R550", "SPI3_SCLK")):
    r(_r, "100k 1%", _n, "GND", lcsc="C25803")
'''))

# ---------- B-2: the E72s' lines
A_CP_E72 = 'cp2102(ub, tag, "+5V_DEV", tag + "_DP", tag + "_DM", tag + "_RXD", tag + "_TXD", rts=tag + "_RST_n", dtr=tag + "_BSL", refs=refs,'
EDITS.append((A_CP_E72, 'cp2102(ub, tag, "+5V_DEV", tag + "_DP", tag + "_DM", tag + "_RXD_H", tag + "_TXD", rts=tag + "_RST_H", dtr=tag + "_BSL_H", refs=refs,'))
A_U22 = 'c("C53", "10u", "+3V3_ZB", "GND", "C10u"); c("C54", "100n", "+3V3_ZB", "GND"); c("C55", "100n", "+3V3_ZB", "GND")\n'
EDITS.append((A_U22, A_U22 + '''# SD-EMC-2 for both E72 (stream d4emcon, D4E-B B-2, 29 September 2026; taken by the session under the owner's standing rule of 26
# September 2026). Each CP2102N (on +5V_DEV, never gated) drove the module's RX, RESET_N and BSL push-pull, and RESET_N and BSL also
# reached +3V3_ZB through R28 to R31, so a 3.3 V source with no series resistance fed the gated rail, whose only sink was U22's
# RPD, which SLVSDH0C states at 5, 12 and 18 V and not at this switch's 3.3 V. Now the six lines pass through SN74LVC2G07 open
# drains on +3V3_DEV (SCES308L), pulled up to the gated rail itself (R28 to R31 as drawn, R536 and R537 new), so with U22 off no
# line is driven up; R538 bleeds the rail: the CP2102N's weak pull-ups into each module's TXD (IPU 30 uA maximum, data sheet Rev
# 1.5) and, with +3V3_DEV lost, the six outputs' Ioff (10 uA each) are 120 uA into 4.653 k, 0.56 V, under the E72's 1.9 V minimum.
# Reverse: the CP2102N pins back on the module nets, U540 to U542, R536 to R538 and C671 to C673 out.
lvc2g07("U540", "ZBA_RXD_H", "ZBA_RXD", "ZBA_RST_H", "ZBA_RST_n", "+3V3_DEV", "C671", "ZBA's RX and RESET_N, pulled up only to the gated +3V3_ZB (SD-EMC-2, D4E-B)")
lvc2g07("U541", "ZBA_BSL_H", "ZBA_BSL", "ZBB_BSL_H", "ZBB_BSL", "+3V3_DEV", "C672", "both E72's BSL, pulled up only to the gated +3V3_ZB (SD-EMC-2, D4E-B)")
lvc2g07("U542", "ZBB_RXD_H", "ZBB_RXD", "ZBB_RST_H", "ZBB_RST_n", "+3V3_DEV", "C673", "ZBB's RX and RESET_N, pulled up only to the gated +3V3_ZB (SD-EMC-2, D4E-B)")
r("R536", "4.7k 1%", "ZBA_RXD", "+3V3_ZB", lcsc="C23162"); r("R537", "4.7k 1%", "ZBB_RXD", "+3V3_ZB", lcsc="C23162")
r("R538", "4.7k 1%", "+3V3_ZB", "GND", lcsc="C23162")   # the rail's bleeder (SD-EMC-2, D4E-B): 0.56 V worst with U22 off, 0.71 mA while on
'''))

# ---------- B-1: the RockBLOCK's lines
A_CP_RB = 'cp2102("U18", "RB", "+5V_DEV", "RB_DP", "RB_DM", "RB_RXD", "RB_TXD", refs=("R40", "C59", "C60"), vregin=("C557", "C558"))   # G7\n'
EDITS.append((A_CP_RB, 'cp2102("U18", "RB", "+5V_DEV", "RB_DP", "RB_DM", "RB_RXD_H", "RB_TXD", refs=("R40", "C59", "C60"), vregin=("C557", "C558"))   # G7; D4E-B B-1: TXD to U538, not to the module\n'))
A_R41 = 'r("R41", "10k", "RB_STATUS", "+3V3_DEV"); r("R42", "10k", "RB_XMTG", "+3V3_DEV")\n'
EDITS.append((A_R41, '''# SD-EMC-2 for the RockBLOCK (stream d4emcon, D4E-B B-1, 29 September 2026; taken by the session under the owner's standing rule
# of 26 September 2026). Ground Control (hardware page, fetched 27 September 2026): with I_BTD low "there should be no voltage
# applied to any input pins, other than I_EN", and at shutdown "Set all pins connected to RockBLOCK 9704 inputs tristate (high-Z)
# or logic low"; Logic In LOW 0.4 V maximum; Logic Out HIGH 2.9 to 3.4 V at 2 mA. The module's inputs RXD (pin 14) and P_EN (pin
# 6, "Leaving open or driving LOW enables the charge circuit") now pass only while RB_GO = RB_IEN AND I_BTD (U537 to U539,
# SN74LVC1G08 on +3V3_DEV), R533 and R534 hold them low with the gates unpowered (Ioff 10 uA into 10 k, 0.10 V); I_BTD and XMT_G
# are pulled DOWN (R41, R42, 2.2 k 1%: U7's 100 uA pull-up, SCPS131J IIL, reads 0.22 V with the module off; the module drives
# 3.4 V into 2.178 k, 1.56 mA, inside its 2 mA), and R535 holds the module's TXD against U18's weak pull-up (30 uA into 10 k,
# 0.30 V). Firmware consequence: P_EN can be driven high (charger off) only while the module reports booted. Reverse: R41, R42
# back to 10 k to +3V3_DEV, U18's TXD and U6's IO1_7 back on the module's pins, U537 to U539, R533 to R535, C668 to C670 out.
r("R41", "2.2k 1%", "RB_STATUS", "GND", lcsc="C4190"); r("R42", "2.2k 1%", "RB_XMTG", "GND", lcsc="C4190")
lvc1g08("U537", "RB_IEN", "RB_STATUS", "RB_GO", "+3V3_DEV", "C668", "RockBLOCK inputs allowed: I_EN AND I_BTD (SD-EMC-2, D4E-B)")
lvc1g08("U538", "RB_RXD_H", "RB_GO", "RB_RXD", "+3V3_DEV", "C669", "RockBLOCK RXD only while RB_GO (SD-EMC-2, D4E-B)")
lvc1g08("U539", "RB_CTRL_H", "RB_GO", "RB_CTRL", "+3V3_DEV", "C670", "RockBLOCK P_EN only while RB_GO (SD-EMC-2, D4E-B)")
r("R533", "10k 1%", "RB_RXD", "GND", lcsc="C25804"); r("R534", "10k 1%", "RB_CTRL", "GND", lcsc="C25804"); r("R535", "10k 1%", "RB_TXD", "GND", lcsc="C25804")
'''))
A_U6 = '"19": "RB_SW_IEN", "20": "RB_CTRL"}, "C2864778")'
EDITS.append((A_U6, '"19": "RB_SW_IEN", "20": "RB_CTRL_H"}, "C2864778")'))

# ---------- B-4: U536's L4 band
A_U536 = '''lvc1g08("U536", "EMCON_HW", "RB_SW_IEN", "RB_IEN", "+3V3_DEV", "C559", "RockBLOCK ENABLE (J_RB9704 pin 3, I_EN), EMCON AND software (EMCON.md 4.4, W4B-D1)")
r("R527", "10k", "RB_IEN", "GND"); r("R528", "4.7k", "RB_SW_IEN", "GND")
'''
EDITS.append((A_U536, '''# L4 case (2) on U536 (stream d4emcon, D4E-B B-4, 29 September 2026; taken by the session under the owner's standing rule of 26
# September 2026). With +3V3_DEV in 0 to 1.65 V, U536's output is unspecified up to 1.65 V against the maker's 0.4 V Logic In LOW,
# and a divider cannot meet both the 0.4 V LOW and the 2.0 V HIGH. U543, a TPS3808G30 on +5V_DEV (U25's input, so it outlives
# +3V3_DEV), watches +3V3_DEV and holds RB_IEN low while it is under VIT (2.79 V +-1.25 percent, SBVS050N); U536 drives RB_IEN
# through R532 (2.2 k 1%), 0.76 mA at most into the supervisor in U536's band, inside its 1 mA VOL row (0.4 V). R527 is 15 k 1%:
# released RB_IEN at least 2.08 V, asserted at most 0.15 V, every rail lost 0.28 V (EMCON.md 4d). CT open (td 12 to 28 ms), MR
# open (90 k to VDD inside). Residual: no maximum SENSE-to-RESET delay is stated (20 us typical), bench E-11 with E-04. Reverse:
# U536's output back on RB_IEN, R527 10 k, R532, U543 and C684 out.
lvc1g08("U536", "EMCON_HW", "RB_SW_IEN", "RB_IEN_DRV", "+3V3_DEV", "C559", "RockBLOCK ENABLE (J_RB9704 pin 3, I_EN), EMCON AND software (EMCON.md 4.4, W4B-D1), through R532 (D4E-B)")
r("R532", "2.2k 1%", "RB_IEN_DRV", "RB_IEN", lcsc="C4190")
r("R527", "15k 1%", "RB_IEN", "GND", lcsc="C22809"); r("R528", "4.7k", "RB_SW_IEN", "GND")
ic("U543", 6, "TPS3808G30DBVR supervisor on +5V_DEV watching +3V3_DEV: holds the RockBLOCK's I_EN low below 2.79 V (L4 on U536, D4E-B)", "SOT236",
   {"1": "RB_IEN", "2": "GND", "3": "NC", "4": "NC", "5": "+3V3_DEV", "6": "+5V_DEV"}, "C189211")
c("C684", "100n", "+5V_DEV", "GND", bypass=("U543", "6"))
'''))

# ---------- decoupling classifier: the SN74LVC2G07
A_DEC = '    if pv.startswith("SN74LVC86A"):\n'
EDITS.append((A_DEC, '''    if pv.startswith("SN74LVC2G07"):
        return ("D", "TI SN74LVC2G07 SCES308L (v2/vendor/ti/ti-sn74lvc2g07.pdf) 10 p.10: \\"For devices with a single supply a 0.1-uF "
                     "capacitor is recommended\\"")
''' + A_DEC))


def main(argv):
    if not argv or len(argv) > 2:
        print(__doc__); return 2
    dry = "--dry-run" in argv[1:]
    p = os.path.join(argv[0], "v2/ecad/tools/gen_sch_b.py")
    old = open(p, encoding="utf-8").read()
    if MARK in old:
        print("refused: %s is already in %s (a second run)" % (MARK, p)); return 1
    for a, _ in EDITS:
        n = old.count(a)
        if n != 1:
            print("refused: anchor found %d times, not once: %r" % (n, a[:90])); return 1
    new = old
    for a, b in EDITS:
        assert new.count(a) == 1, a[:90]
        new = new.replace(a, b)
    assert new != old and MARK in new
    for ref in ("U537", "U538", "U539", "U540", "U541", "U542", "U543", "U544", "U550", "U551", "U553", "U554", "R532", "R545", "R550"):
        assert new.count('"%s"' % ref) >= 1, ref
    ast.parse(new)
    if dry:
        print("dry run: every anchor found once, the result parses; %d edits, %+d lines" % (len(EDITS), new.count("\n") - old.count("\n")))
        return 0
    open(p, "w", encoding="utf-8").write(new)
    ast.parse(open(p, encoding="utf-8").read())
    print("applied D4E-B (B-1 to B-5) to %s: %d edits; regenerate board B on the box, then readback_d4e.py --board B" % (p, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
