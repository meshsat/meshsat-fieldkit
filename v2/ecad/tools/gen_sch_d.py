#!/usr/bin/env python3
"""PCB-D APRS MEZZANINE, phase D8 (MESHSAT-830; appendix 32.56 PA on the plate, 32.57 device set, 32.59): generate the KiCad 9 schematic (netlist
style: every pin gets a stub and a net label; GND pins get power symbols). Runs where the KiCad symbol libraries are (the vast.ai box).
Usage: gen_sch_d.py <out.kicad_sch> <project>

The mezzanine sits on A22's standoffs (case X 0..100, Y -40..40) and is a USB device set of the kit: A22's J_MEZZ1 harness brings one USB 2.0 pair,
the kit I2C bus, the hardware inhibit TX_INHIBIT_n (the panel's EMCON toggle), the PA rail state PA_EN and the PTT mirror TR_APRS; J_MEZZ_PWR1 brings
5 V (2 A eFuse on A22). On the board: a TUSB2046I (TUSB2046IBVFR, -40 to 85 C) four-port hub on its own 3.44 V LDO (port 1 the PCM2912A USB audio
codec, port 2 a CP2102N bridge to the SA868's UART with RTS as the software PTT, port 3 a spare header), the NiceRF SA868 VHF exciter (bench-fitted,
2 W high / 0.5 W low), a G6K-2F-Y DPDT T/R relay, a 10 dB pad to the PA drive lead, the PA output lead into a 5-element low-pass filter and the
antenna SMA (pigtail to A22's VHF jack), the PA gate bias regulated to 4.48 V by a TLV75801P enabled by PA_KEY, a TPA6132A2 headphone amplifier
driving the two headset leads (U-174/U jacks on the face plate) with the
receive audio and the codec's playback, a TLV9062 microphone summing preamplifier into the exciter's MIC_IN together with the codec's transmit audio,
the PTT logic in single-gate 74LVC1G parts (KEY = any PTT AND TX_INHIBIT_n; PA_KEY = KEY AND PA_EN; the SA868's PTT pulled low by an open-drain
inverter and otherwise held at receive by a divider from the exciter's own rail), a PCA9555 at 0x26 on the kit I2C bus (harness
+3V3, level stages into the mezzanine's own 3.3 V domain, and one-way buffers where it reads KEY and PA_KEY back, so no software pin shares a
conductor with the EMCON gates), LEDs and test points. The RA30H1317M1 PA module bolts to the face plate (32.56): its
13.8 V comes from A22's J_PA lead directly, its drive and output coax and its VGG lead from this board's north edge.
Round 8 (MESHSAT-1357, 26 September 2026): the exciter, the gate bias regulator and the T/R relay coil take their 5 V through
a TPS22810 load switch (U21, rail +5V_TX) that is on only while the PTT and EMCON gates' own supply +3V3_D8 is inside the
74LVC1G range (EMCON L4), and the PA's flange temperature is read by a Semitec 103AT-2 NTC on a lead and an ADS1115 at 0x48
on the kit bus (PWR-F15).
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-d-aprs"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from idc_pads import idc   # the IDC land is a per-board measurement (IDC_PADS), not a default: see idc_pads.py
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, esd, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, synth_symbol, text, tps22810, uq, usb_c_recept, wire)
import intent as _intent
# LOADS DECLARED 13 September 2026. This rail carried none, so dc_drop guessed it over eight parts evenly and
# the board read MISSED on a current path nobody designed. The dominant consumer is the SA868 exciter behind
# the ferrite FB1, whose transmit pulses are what the 2 A peak is for; the 3.3 V LDO feeds all the logic, and
# the codec, the headphone amplifier, the bridge and the spare port take the rest. The split apportions the
# declared 1.0 A typical and is a design estimate of where the current goes, not a measurement.

# WHICH OF THIS BOARD'S RAILS CONVERT (16 September 2026, rule THM-001). Three of the four do not: +5V_D8 and
# +3V3 arrive from board A through the mezzanine connectors and +5V_SA is the same 5 V behind a ferrite, so
# their loss is the I2R of this board's own copper, which dc_drop measures. The fourth is a LINEAR regulator
# and that is the case where the efficiency is arithmetic rather than a datasheet reading: a TLV75533 dropping
# 5.0 V to 3.3 V dissipates the difference, so its efficiency is 3.3/5.0 = 0.66 exactly, and the 0.8 W this
# rail carries costs about 0.4 W in one SOT-23-5. That is the largest single dissipator on this board after
# the transmitter, and it is the kind of number this rule exists to surface.
# THE WORKING MAXIMUM OF THIS RAIL, DECLARED (W2 F-IN-01 and S-09 follow-up, 26 September 2026). +5V_D8 is
# board A's +5V_DEV behind the eFuse U23, and +5V_DEV is an AP64500 whose divider is 53.6k over 10k
# (gen_sch_a.py buck5) on a 792 to 808 mV reference (Diodes DS41979, VFB, CCM): 5.088 V nominal and 5.23 V at
# the top of the reference and both 1 percent resistors. The 5.0 V below stays the NOMINAL for the drop budget;
# v_work is what a clamp's stand-off and a capacitor's rating are judged against (intent.rail, derate.py).
# LOADS RE-SPLIT the same day for the hub's own LDO U17 (W6-F5): the hub's 40 mA left U1's rail and U17 carries
# it, so U1's share falls from 0.25 A to 0.17 A (+3V3_D8's new peak) and U17 takes 0.04 A (SLLS413L, ICC).
# EMCON L4, round 8 (26 September 2026): the exciter behind FB1 and the gate bias regulator U15 now draw through the
# load switch U21 (rail +5V_TX, declared below), so their 0.50 A and 0.02 A leave this rail's loads as U21's 0.52 A.
# The sum is unchanged at 0.96 A.
_intent.rail("+5V_D8", 5.0, 1.0, 2.0, "J_PWR1", budget=0.06, share=0.02, always_on=True, converted=False, v_work=5.23,
             always_on_why="it arrives on the mezzanine behind board A's eFuse U23, which is where it is switched; this board consumes it",
             loads={"U21": 0.52, "U1": 0.17, "U17": 0.04, "U6": 0.10, "J_USB3": 0.05, "U7": 0.05, "U3": 0.03}, note="BUDGET FROM THE TIGHTEST CONSUMER'S DATASHEET, 16 September 2026, replacing a number this project had only asserted. The consumers of this rail sit on board D and the tightest of them is the PCM2912A USB codec, whose recommended operating VBUS is 4.35 V minimum (v2/vendor/ti/ti-pcm2912a.pdf, Recommended Operating Conditions); the next is the CP2102N, whose 3.3 V regulator leaves regulation below VREGIN 4.1 V (v2/vendor/silabs/silabs-cp2102n.pdf). The source is board A's eFuse output on the 5.0 V device rail, and at a 2 percent source tolerance its worst case is 4.90 V, so the IR drop that keeps the codec in its recommended range is 550 mV, 11 percent. The declared budget is 6 percent, 300 mV, which leaves the codec at 4.60 V with 250 mV in hand. The 3 percent it replaces was derived from nothing and was tighter than the parts ask for. This board's share is 2 of the 6 points and it measures 0.58. The mezzanine's 5 V from A22. Budget 3 percent, not the 2 percent default: every consumer either regulates this rail or tolerates a wide range (the TLV75533 3.3 V LDO with 1.5 V of headroom, the CP2102N bridge at a 4.0 V minimum, the ESD reference, and the exciter's own boost behind FB1). D10 measures 108 mV at 1.0 A, 2.16 percent, leaving 4.89 V at the tightest consumer (9 September 2026). ONE CONDUCTOR, ONE BUDGET (16 September 2026): this rail starts at board A's eFuse and both boards were measuring their own half against the whole three percent, so the halves could sum past it with both passing. The 3 percent is the rail's, the 1.5 is this board's share of it, and D's own 2.16 percent is over that share: the 108 mV is measured from the connector to the tightest consumer on THIS board, so D owes a widening too, not only A.")
# DECLARED 16 September 2026. These three were not in the intent file, so `signalnets` could not know they
# were rails and the return-path gate judged them as SIGNAL NETS, while `dc_drop` and `derate` could not see
# them at all. A rail that is not declared is not excluded: it is silently checked against the wrong question
# and silently missed by the right one. The currents are design estimates of where the current goes, in the
# same form as the rails above, and every load is named because a rail without loads is not declarable.
# WHAT FEEDS THIS RAIL (20 September 2026, appendix 32.246): `power_path` adds up what a rail's
# converters draw and refuses to let a feeder declare less than its children take. Board A's VBAT
# declared 10 A and its nine converters drew 15.18, and nothing checked it on any board until now.
# W6-F5, 26 September 2026: the hub U4 LEFT this rail for its own +3V4_HUB (below), so its 0.080 A left the
# loads and the declared currents fell by the same amount (typical 0.12 to 0.04 A, peak 0.25 to 0.17 A).
_intent.rail("+3V3_D8", 3.3, 0.04, 0.17, "U1", budget=0.03, always_on=True, converted=True, efficiency=0.66, fed_from="+5V_D8",
             always_on_why="U1 is a TLV75533 whose EN pin is tied to its own input, so this rail follows +5V_D8 and has no switch of its own",
             source_ic="U1 is a TLV75533 LDO in SOT-23-5: pin 5 IS its output power pin",
             # J_HARN1 is NOT on this net: the gated 3.3 V that leaves on the harness is board A's +3V3, and the
             # intent validator said so on the first run, which is what it is for. U1 is the SOURCE of this rail
             # and cannot be a load of its own output, which is the same mistake from the other side.
             # R4T-F9 and RF-002, 26 September 2026: Q6 and Q7 left this rail (KEY and PA_KEY are read back through
             # one-way buffers on +3V3 now) and U18, the buffer that drives the PTT mirror TR_APRS, joined it, so the
             # sum is unchanged at 0.039 A.
             # EMCON L4, round 8: R90 and R91, the divider that tells U21 this rail is inside the gates' range, draw
             # 3.3 V / 21k = 0.16 mA from it (R90 is the part on the net).
             loads={"U7": 0.020, "U9": 0.002, "U10": 0.002, "U11": 0.002, "U12": 0.002,
                    "U13": 0.002, "U14": 0.002, "U18": 0.002, "Q3": 0.001, "Q4": 0.001, "Q5": 0.001,
                    "Q8": 0.001, "Q9": 0.001, "R90": 0.0002},
             note="the local 3.3 V from U1: the six single-gate PTT and inhibit gates, the PTT mirror's buffer U18, "
                  "the level shifters, the headphone amplifier's logic, the indicator LEDs and the pull-ups. "
                  "The USB hub moved to its own +3V4_HUB on 26 September 2026 (W6-F5). "
                  "Budget 3 percent: every consumer is a logic part with a wide supply range")
# THE HUB'S OWN RAIL (W6-F5, 26 September 2026). The hub is now the industrial TUSB2046IBVFR, and TI's
# SLLS413L (Recommended Operating Conditions, page 6) gives the I grade a narrower supply than the commercial B:
# VCC 3.3 V MINIMUM to 3.6 V (the B part is 3.0 to 3.6). U1 is a TLV75533 at +-1 percent (TI SBVS320D,
# -40 to 85 C, DBV), 3.267 V at its low edge before any load or copper drop, so the I part cannot share +3V3_D8.
# U17 is a TLV75801P adjustable LDO (TI SBVS351D: VFB 0.55 V, SOT-23-5 pin 1 IN, 2 GND, 3 EN, 4 FB, 5 OUT) set by
# R80 56.2k over R81 10.7k to 0.55 x (1 + 56.2/10.7) = 3.439 V nominal.
# THE WORST-CASE BAND WITH EVERY TERM (review fix-up of round 4, 26 September 2026). A first draft counted only the
# reference and 1 percent resistors at 25 C (3.348 to 3.532 V) and so claimed margins that did not exist: with the
# 1 percent, 100 ppm/C parts over the envelope the pin could reach 3.274 V after the drop budget, below the I
# grade's 3.3 V minimum, the same criterion that ruled +3V3_D8 out. The terms, from SBVS351D 5.5 and the parts:
#   VFB +-1 percent at -40 to 85 C TJ (its note 1: external resistor tolerances not included);
#   R80, R81 +-0.1 percent and +-25 ppm/C thin film, taken over 65 K from 25 C (so the whole -40 to 85 C range the
#   reference is specified over, wider than the -20 C to inside-air envelope): +-0.2625 percent each;
#   line regulation 7.5 mV maximum (accuracy is specified at VIN = VOUT + 0.5 V and this part runs at about 5 V);
#   load regulation 0.030 V/A typical (no maximum is published) at the hub's 40 mA, 1.2 mV;
#   IFB 0.1 uA maximum through R80, 5.6 mV either way.
# Low corner 0.5445 x (1 + 5.2523 x 0.99476) = 3.389 V, minus 7.5, 1.2 and 5.6 mV = 3.375 V at the LDO; high corner
# 0.5555 x (1 + 5.2523 x 1.00526) = 3.489 V, plus 7.5 and 5.6 mV = 3.502 V. The drop budget is 1 percent, 34 mV,
# which is what dc_drop accepts at layout: the hub's pin stays at or above 3.341 V, 41 mV over SLLS413L 7.3's 3.3 V
# minimum, and at or below 3.502 V, 98 mV under its 3.6 V maximum, which is also its absolute maximum (SLLS413L 7.1).
# With the 1 percent parts the same arithmetic gives 3.297 to 3.584 V at the LDO, which is why R80 and R81 are
# precision parts. Nothing but the hub and its own pull-ups is on this rail.
# TWO MORE TERMS, READ ON THE RE-REVIEW OF ROUND 4 (26 September 2026). Drift: the RT series' test limits for
# endurance (1,000 h at 70 C, rated voltage), damp heat and thermal shock are +-(0.5 percent + 0.05 Ohm) per
# resistor (YAGEO RT V.16 Table 4); stacked on the band above they give 3.347 to 3.531 V at the LDO and 3.312 V at
# the pin, still over 3.3 V and under 3.6 V, so the rail declares v_work 3.54 V rather than the as-supplied 3.51.
# The reference's own window: VFB +-1 percent holds for TJ -40 to 85 C (SBVS351D 5.5). U17 dissipates at most
# (5.23 - 3.375) V x 40 mA = 74 mW, +13 K at the SOT-23-5's 176.9 C/W (SBVS351D 5.4, JEDEC board), so TJ stays near
# 68 C under the envelope's +55 C inside air (pcb_envelope.yaml, itself an estimate); even on the 125 C row, +-1.5
# percent, the as-supplied pin holds 3.324 V.
_intent.rail("+3V4_HUB", 3.44, 0.04, 0.04, "U17", budget=0.01, always_on=True, converted=True, efficiency=0.676, fed_from="+5V_D8", v_work=3.54,
             always_on_why="U17's EN pin is tied to its own input, so this rail follows +5V_D8 and has no switch of its own",
             source_ic="U17 is a TLV75801P LDO in SOT-23-5: pin 5 IS its output power pin",
             loads={"U4": 0.040},
             note="the USB hub's supply: TUSB2046IBVFR, ICC 40 mA maximum in normal operation (SLLS413L 7.5), VCC 3.3 V "
                  "minimum to 3.6 V (SLLS413L 7.3, I grade; 3.6 V is also the absolute maximum, 7.1). U17 TLV75801P with "
                  "R80 56.2k and R81 10.7k, both 0.1 percent 25 ppm/C thin film: 3.439 V nominal, 3.375 to 3.502 V at the "
                  "LDO with every term (VFB +-1 percent, the resistors' tolerance and TCR over 65 K, line regulation 7.5 mV, "
                  "load regulation 1.2 mV, IFB 0.1 uA through R80; SBVS351D 5.5). The 1 percent budget, 34 mV, leaves the "
                  "hub's pin at 3.341 V or more, 41 mV over its minimum. With the resistors' endurance, damp-heat and "
                  "thermal-shock limits added, +-(0.5 percent + 0.05 Ohm) each (YAGEO RT V.16 Table 4), the band is "
                  "3.347 to 3.531 V and the pin 3.312 V or more; v_work 3.54 V covers that top. "
                  "Efficiency is the LDO's arithmetic, 3.44 / 5.09 = 0.676, at the nominal +5V_D8 of 5.088 V")
# EVERY USB LINK ON THIS BOARD IS FULL SPEED, so the 90 ohm differential target does not apply to it
# (16 September 2026, rules STK-001 and PAIR-001; the same reading board C was given on 8 September).
# The hub is a TI TUSB2046x (the I grade, TUSB2046IBVFR, since 26 September 2026: W6-F5), whose own datasheet's first page says "Full-Speed Hub" and "All Downstream Ports
# Support Full-Speed and Low-Speed Operations" at 12 Mb/s (v2/vendor/ti/ti-tusb2046b.pdf); the codec is a
# PCM2912A, "USB revision 2.0, full-speed" (v2/vendor/ti/ti-pcm2912a.pdf); the two CP2102N bridges and the
# spare port are full speed as well. The 90 ohm target of the shared USB class belongs to USB 2.0 HIGH speed
# signalling, and requiring it here is a wrong requirement rather than a strict one: at 12 Mb/s with the
# specification's own 4 to 20 ns edges, a 30 mm pair is electrically short.
# What this changes in the judgement: impedance_check skips a class with no target, so D's /USB1 stops being
# MISSED for having 48 percent of its length coupled, which is what a pair with a series-resistor station at
# each end looks like. The GEOMETRY does not change at all: the pairs stay at 0.30 mm on 0.20 mm as routed,
# and the pre-router still lays them as pairs.
_intent.pair_class("USB")

# THE TRANSMIT CHAIN'S 5 V, SWITCHED BY ITS OWN LOGIC'S SUPPLY (EMCON L4 on board D, round 8, 26 September 2026).
# U21, a TPS22810 load switch, puts +5V_D8 on +5V_TX only while +3V3_D8, the supply of every gate on the KEY, PA_KEY and
# TX_INHIBIT_n paths, is inside the 74LVC1G range. Behind it: the exciter (through FB1 onto +5V_SA), the gate bias
# regulator U15 and the T/R relay coil K1. The arithmetic and the sources are at U21 below. The loads are the peaks
# of the three: the exciter's 1.10 A on a transmit pulse, U15's 0.02 A and the G6K coil's 21.1 mA at 5 V (Omron G6K
# catalogue, the 5 VDC coil row: 21.1 mA, 237 Ohm, must operate 80 percent maximum, must release 10 percent minimum).
_intent.rail("+5V_TX", 5.0, 0.37, 1.15, "U21", budget=0.03, switch="U21", enable_net="TXSUP_EN", converted=False,
             fed_from="+5V_D8", v_work=5.23,
             source_ic="U21 is a TPS22810 load switch in WSON-6: pin 1 VOUT is its pass FET's output and the whole rail's "
                       "current leaves through it (TI SLVSDH0C, pin table); pin 2 QOD reaches the rail only through R95 "
                       "and carries current only while the switch is off",
             loads={"FB1": 1.10, "U15": 0.02, "K1": 0.02},
             note="the transmit chain's 5 V behind the TPS22810 load switch U21 (TI SLVSDH0C): on while +3V3_D8 is "
                  "above 2.23 to 2.78 V (EN/UVLO divider R90 11k over R91 10k, VENR 1.13 to 1.30 V and VENF 1.08 to "
                  "1.18 V, 7.5), off below the switch's own VIN UVLO (VUVR 2.00 to 2.62 V, 7.5). RON at most 105 mOhm "
                  "at 5 V to +85 C (7.5): 0.12 V at the 1.15 A peak. Budget 3 percent for this rail's copper; its "
                  "loads regulate or tolerate a wide range (the exciter 3.3 to 5.5 V behind FB1, U15 only lower in "
                  "dropout, the relay's must-operate 4.0 V, 80 percent of its 5 V coil)")
_intent.rail("+5V_SA", 5.0, 0.35, 1.10, "FB1", budget=0.05, switch="U21", enable_net="TXSUP_EN", converted=False, fed_from="+5V_TX",
             loads={"U2": 1.10},
             note="the exciter's own 5 V behind the 600R ferrite FB1: the SA868 draws about 350 mA receiving "
                  "and up to 1 A on a transmit pulse, which is what the bead and its bulk capacitor are for. "
                  "Budget 5 percent because the module's own range is 3.3 to 5.5 V. Since round 8 (EMCON L4) FB1 "
                  "is fed from +5V_TX, so this rail is switched by U21 with it; what gates the transmitter "
                  "in service is still the PTT chain, and U21 only keeps the exciter unpowered while that "
                  "chain's supply is outside its range")
_intent.rail("+3V3", 3.3, 0.06, 0.10, "J_HARN1", budget=0.03, share=0.0075, always_on=True, converted=False,
             always_on_why="board A's gated 3.3 V arriving over the mezzanine harness; it is switched on board A by U12 and this board only consumes it",
             loads={"U16": 0.060, "U19": 0.002, "U20": 0.002, "U22": 0.0002, "R92": 0.0012},
             note="board A's always-on 3.3 V arriving over the mezzanine harness, which on this board feeds "
                  "the expander U16 with its level stages' far-side pull-ups, and since 26 September 2026 (RF-002) "
                  "the two one-way buffers U19 and U20 that read KEY and PA_KEY back into U16. It is a rail of "
                  "board A and a load of this one. Round 8 (PWR-F15): the flange ADC U22 (ADS1115, 150 uA in "
                  "continuous conversion, TI SBAS444E feature list) and the NTC divider's top R92 (2.0k: 3.3 V over "
                  "2.0k plus the NTC's 0.99k at +100 C is 1.1 mA)")

SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers (as B13/B15)
LIBCACHE = {}

# ----------------------------------------------------------------- synthetic box symbols (parts with no library symbol): odd pins left, even pins right
# NiceRF SA868 (V1.x manual, 18 castellations); TI PCM2912A (SLES230A, TQFP-32); TI TPA6132A2 (SLOS597B, QFN-16, pin 17 the pad; G12 of the decoupling ruling corrected the citation, which read SLOS553); TI TUSB2046I (SLLS413L, LQFP-32 VF:
# the VF pin functions table is shared by the B and I grades, so the map is unchanged by W6-F5 of 26 September 2026);
# Silicon Labs CP2102N QFN28 (as B16)
SA868 = {1: "AUDIO_ON_n", 2: "NC", 3: "AF_OUT", 4: "NC", 5: "PTT_n", 6: "PD", 7: "H/L", 8: "VBAT", 9: "GND", 10: "GND", 11: "NC", 12: "ANT", 13: "NC", 14: "NC", 15: "NC", 16: "RXD", 17: "TXD", 18: "MIC_IN"}
PCM2912A = {1: "BGND", 2: "VBUS", 3: "D-", 4: "D+", 5: "VDD", 6: "DGND", 7: "XTO", 8: "XTI", 9: "FL", 10: "FR", 11: "VCOM1", 12: "VCOM2", 13: "AGND", 14: "NC", 15: "VCCA", 16: "VIN", 17: "MBIAS", 18: "VOUTL",
            19: "VCCL", 20: "HGND", 21: "VCCR", 22: "VOUTR", 23: "MAMP", 24: "POWER", 25: "PGND", 26: "VCCP", 27: "TEST1", 28: "TEST0", 29: "SSPND", 30: "MMUTE", 31: "REC", 32: "PLAY"}
TPA6132A2 = {1: "INL-", 2: "INL+", 3: "INR+", 4: "INR-", 5: "OUTR", 6: "G0", 7: "G1", 8: "HPVSS", 9: "CPN", 10: "PGND", 11: "CPP", 12: "HPVDD", 13: "EN", 14: "VDD", 15: "SGND", 16: "OUTL", 17: "PAD"}
TUSB2046I = {1: "DP0", 2: "DM0", 3: "VCC", 4: "RESET_n", 5: "EECLK", 6: "EEDATA/GANGED", 7: "GND", 8: "BUSPWR", 9: "PWRON1_n", 10: "OVRCUR1_n", 11: "DM1", 12: "DP1", 13: "PWRON2_n", 14: "OVRCUR2_n", 15: "DM2", 16: "DP2",
             17: "PWRON3_n", 18: "OVRCUR3_n", 19: "DM3", 20: "DP3", 21: "PWRON4_n", 22: "OVRCUR4_n", 23: "DM4", 24: "DP4", 25: "VCC", 26: "EXTMEM", 27: "TSTPLL/48MCLK", 28: "GND", 29: "XTAL2", 30: "XTAL1", 31: "TSTMODE", 32: "SUSPND"}
CP2102 = {1:"DCD",2:"RI_CLK",3:"GND",4:"D+",5:"D-",6:"VDD",7:"VREGIN",8:"VBUS",9:"RSTb",10:"NC",11:"SUSPENDb",12:"SUSPEND",13:"CHREN",14:"CHR1",15:"CHR0",16:"GPIO3",17:"GPIO2",18:"GPIO1",19:"GPIO0",20:"GPIO6",21:"GPIO5",22:"GPIO4",23:"CTS",24:"RTS",25:"RXD",26:"TXD",27:"DSR",28:"DTR",29:"GND"}
SYNTH = {"SA868": SA868, "PCM2912A": PCM2912A, "TPA6132A2": TPA6132A2, "TUSB2046I": TUSB2046I, "CP2102N": CP2102}

# ----------------------------------------------------------------- footprints
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "R2010": "Resistor_SMD:R_2010_5025Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C1206": "Capacitor_SMD:C_1206_3216Metric", "C1210": "Capacitor_SMD:C_1210_3225Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
 "XTAL": "Crystal:Crystal_SMD_HC49-SD", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "IDC16": idc("2x08"),
 "TP": "TestPoint:TestPoint_Pad_D1.5mm", "QFN28": "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm", "TQFP32": "Package_QFP:TQFP-32_7x7mm_P0.8mm", "LQFP32": "Package_QFP:LQFP-32_7x7mm_P0.8mm",
 "QFN16": "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm", "VSSOP8": "Package_SO:VSSOP-8_3x3mm_P0.65mm", "TSSOP24": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
 "SA868": "meshsat:NiceRF_SA868", "RELAY": "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y", "SMA": "Connector_Coaxial:SMA_Amphenol_132134_Vertical", "UFL": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
 "L1812": "Inductor_SMD:L_1812_4532Metric", "L0805": "Inductor_SMD:L_0805_2012Metric",
 "FB": "Inductor_SMD:L_0805_2012Metric", "SOD123": "Diode_SMD:D_SOD-123", "SOD323": "Diode_SMD:D_SOD-323", "SMB": "Diode_SMD:D_SMB",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "VSSOP10": "Package_SO:VSSOP-10_3x3mm_P0.5mm",   # round 8: J_FLANGE and U22 (PWR-F15)
 "PH2": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "PH5": "Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical",
 "JP": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
}
kisch.configure(fp=FP, synth=SYNTH)   # the engine needs the tables before the first part
P = kisch.P                           # one list, shared with the engine (not a copy)
def synth(ref, name, value, fp, nets, lcsc=""):
    full = {str(k): nets.get(k, nets.get(str(k), "NC")) for k in SYNTH[name]}
    part(ref, "Connector_Generic", name, value, fp, full, lcsc)
# 13 September 2026: an LED row carried its COLOUR as its value and no part number, so the certification
# could not identify it: "no part number and no value this search understands: 'amber NVMe activity'". The
# colour is the design intent and stays in the value, where the schematic reader wants it; the code is what
# makes the row orderable. Hubei KENTO's 0603 family, every entry read back from JLCPCB with its stock on
# 13 September 2026: red C2286 (BASIC, 3,879,968), yellow/amber C2287 (98,669), green C12624 (113,369),
# blue C2288 (99,839), white C2290 (BASIC, 1,168,521). A colour with no entry gets no code rather than a
# guess, and the certification will say so.
LED_CODE = {"red": "C2286", "amber": "C2287", "yellow": "C2287", "green": "C12624", "blue": "C2288", "white": "C2290"}
# THE TWO "AMBER" ROWS NAME THE PART THAT IS BOUGHT (round 8 of MESHSAT-1357, 26 September 2026; the parts re-take,
# v2/vendor/SOURCES.yaml jlc_retake_45bde541.condition_1_mismatches). C2287 is Hubei KENTO KT-0603Y, and KENTO's own
# specification for it (CITAYL 0603-0.6, revision A.0, 2018-12-06, served by LCSC for C2287; filed as a draft this round)
# says "Color: Yellow light", dominant wavelength 584 to 594 nm at 20 mA; JLCPCB reads it back as "Yellow" (API
# 2026-09-26T21:18Z). LED2 and LED5 are board-local indicators on the mezzanine, not panel semantics (PANEL.md's LED
# rules are board C's), so the recommended option is taken by the session under the owner's standing rule: the value
# text says yellow and the code stays. The "amber" key stays in the table for the day an amber row is a real amber.
def led_code(colour):
    w = (colour or "").strip().split()
    return (LED_CODE.get(w[0].lower()) or "") if w else ""   # "" and not None: part() defaults lcsc to ""
def led(ref, colour, anode, cathode): part(ref, "Device", "LED", colour, "LED", {"2": anode, "1": cathode}, led_code(colour))
def nfet(ref, gate, source, drain, value="2N7002"): part(ref, "Transistor_FET", "2N7002", value, "SOT23", {"1": gate, "2": source, "3": drain}, "C8545")   # 1 G 2 S 3 D (SOT-23 order, appendix 32.36)
def level(ref, rn, far, near, near_rail, far_rail=None, rf=None):
    """Bidirectional 2N7002 stage between a module-domain line (near, pulled up to the module's rail) and the always-on side (far); the module off = gate low, nothing flows."""
    nfet(ref, near_rail, near, far); r(rn, "10k", near, near_rail)
    if far_rail: r(rf, "10k", far, far_rail)
def tps2065(ref, rail, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": rail, "4": en, "1": out, "3": flt, "2": "GND"})
def cp2102(uref, tag, vusb, dp, dm, txd, rxd, rts="NC", dtr="NC", refs=()):
    """CP2102N-A02-GQFN28 bridge: bus sense and regulator input from the slot rail whose hub carries it, its own 3.3 V out (VDD) bypassed, RSTb pulled to VDD."""
    synth(uref, "CP2102N", "CP2102N-A02-GQFN28 USB-UART bridge (%s)" % tag, "QFN28", {3: "GND", 29: "GND", 4: dp, 5: dm, 6: tag + "_3V3", 7: vusb, 8: vusb, 9: tag + "_RST", 25: rxd, 26: txd, 24: rts, 28: dtr}, "C964632")
    rr, c1, c2 = refs
    r(rr, "1k", tag + "_RST", tag + "_3V3"); c(c1, "4.7u", tag + "_3V3", "GND", "C10u"); c(c2, "100n", tag + "_3V3", "GND")


# ================================================================= the design (nets are root-sheet labels; GND is the only power symbol)
# --- harness and power entry (A22 J_MEZZ1 mirror, J_MEZZ_PWR1 5 V behind A22's 2 A eFuse U23)
# 11 September 2026 (MESHSAT-862): USB_D8 sits on pins 1/2, the END row, and the four pins behind it are ground. Measured
# reason: this is a 2x8 at 2.54 mm with 1.70 mm pads, so the channel between the two columns is 0.84 mm, while a 0.30/0.20/0.30
# pair with its class clearance needs 1.20 mm. No coupled pair can leave an INNER row of this header, in any direction or on
# any layer, the pins being through-hole; only an end row escapes into free board. The 10 September move (from the diagonal
# pins 2/3, 3.59 mm apart, to 3/4) fixed the station and left the escape impossible, and the pre-router had been saying so
# ever since: "the legs clear no smoothing of the centreline" with each leg 1.0 mm from a neighbouring pin's pad.
# A22's J_MEZZ1 carries the same map (check_contracts.py compares them).
part("J_HARN1", "Connector_Generic", "Conn_02x08_Odd_Even", "A22 mezzanine harness J_MEZZ1 (IDC 2x8): USB pair, PTT mirror, inhibit, PA rail state, I2C, 3.3 V", "IDC16", {
 "1": "USB_D8_P", "2": "USB_D8_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "TR_APRS", "8": "TX_INHIBIT_n", "9": "PA_EN", "10": "SDA", "11": "SCL", "12": "EXP_INT", "13": "+3V3", "14": "GND", "15": "ZEROIZE_HW", "16": "AB_SPARE"})
part("J_PWR1", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: 5 V from A22 J_MEZZ_PWR1 (behind A22's 2 A eFuse U23): + -", "VH2", {"1": "+5V_D8", "2": "GND"}, "C274411")
# S-09 / A03 / W2 F-IN-01, 26 September 2026: D1 WAS REVERSED AND DRAWN WITHOUT A POLARITY. It had GND on pad 1,
# which on KiCad's Diode_SMD:D_SMB is the cathode (the fab apex and the silk bracket both mark pad 1, read with
# pcbnew by A03), so the one-way clamp was forward-biased across +5V_D8 from power-up: a short limited by board
# A's 2 A eFuse, and no clamp at all for a positive transient. Device:D_TVS is KiCad's BIDIRECTIONAL symbol (pins
# A1/A2), which is why nothing in the schematic showed it. Now the cathode (K, pin 1, pad 1) is on +5V_D8 and the
# anode on GND, drawn with Device:D_Zener, the K/A symbol the shared kisch.tvs() helper of Review D round 4 draws
# for a one-way part (KiCad 9.0.9 has no unidirectional TVS symbol with K/A pins); the helper is used when the
# tree carries it, and the fallback below writes the identical symbol and pin map.
# AND THE PART MOVES UP ONE STAND-OFF, SMBJ5.0A TO SMBJ6.0A: the rail's nominal is 5.088 V and its working maximum
# 5.23 V (declared as v_work above), while an SMBJ5.0A stands off 5.0 V (MDD sheet for C113974: VR 5.0, IR 800 uA
# at VR, VBR 6.40 min), so it sat above its own stand-off in normal service. This is the class board B's three
# slot-rail clamps were moved out of on 16 September (gen_sch_b.py D101/D201/D301, rule CMP-001), missed here
# because this rail was declared at 5.0 V. Littelfuse SMBJ6.0A, LCSC C83270, DO-214AA on the same D_SMB land:
# VR 6.0 V, VBR 6.67 to 7.37 V at 10 mA, VC 10.3 V at 58.3 A, TJ -65 to 150 C (Littelfuse SMBJ series, Revised
# JC.07/04/25; JLC API 2026-09-25T23:09Z, Littelfuse, DO-214AA, stock 5,470).
# WHAT D1 DOES NOT DO (review fix-up of round 4, 26 September 2026): it is a transient clamp, not an overvoltage
# protector. Its breakdown (6.67 to 7.37 V) and clamping voltage (10.3 V), like the SMBJ5.0A's before it (6.40 to
# 7.00 V, 9.2 V), sit above this rail's consumers' absolute maxima: U1 TLV75533 VIN 6.0 V (SBVS320D 5.1), U15 and
# U17 TLV758P VIN 6.5 V (SBVS351D 5.1), U6 PCM2912A VBUS 6.5 V (SLES230A 7.1). A SUSTAINED overvoltage on +5V_D8
# (board A's AP64500 losing regulation) is therefore stopped only by board A's eFuse U23 (TPS259631), whose OVLO
# divider is the 100k over 10k its VBAT siblings carry. With every term (TPS2596 7.5: VOVLO(R) 1.17 to 1.22 V,
# VOVLO(F) 1.08 to 1.13 V, IOVLKG 0.1 uA; both resistors 1 percent and 100 ppm/C over 65 K, the UNI-ROYAL 0603WAF
# parts lcsc_fill fits, C25803 and C25804, the latter read back from JLC at +-100 ppm/C) it trips at 12.48 to
# 13.84 V (the round-4 fix-up's 12.87 to 13.42 V left out the divider's own tolerance), and its pin sits at 0.46 V
# in service, under the 0.5 V bottom of the OVLO pin's range (TPS2596 7.3; round-2 F-SQ-06). An open item for
# board A's generator, not this one, re-derived on the re-review of round 4: the fix-up proposed 38.3k over 10k,
# which with 1 percent 100 ppm/C parts trips at 5.50 to 6.05 V, its top above U1's 6.0 V. No divider of such parts
# can both trip under 6.0 V and re-close above the rail's 5.23 V working maximum: that needs a corner-to-corner
# ratio spread of 1.6 percent, and a 1 percent 100 ppm/C pair at this ratio spreads 5.4 percent. A 0.1 percent
# 25 ppm/C pair, the class of R80 and R81, spreads 0.8 percent: 38.3k over 10k then trips at 5.62 to 5.92 V (80 mV
# under U1's 6.0 V) and re-closes below 5.19 to 5.49 V, so a tripped U23 re-closes at the rail's 5.09 V nominal;
# only a rail above 5.19 V, the top 40 mV of its band, could hold it off, and OVLO reports on D8_FLT (TPS2596
# Table 3). That pin sits at 1.05 V in service, inside the 0.5 to 2 V range.
try:
    from kisch import tvs as _tvs          # r4t's helper (S-09), when the tree carries it
except ImportError:
    _tvs = None
if _tvs:
    _tvs("D1", "SMBJ6.0A (6.0 V standoff on the 5.09 V mezzanine rail)", "+5V_D8", "GND", "SMB", "C83270")
else:
    part("D1", "Device", "D_Zener", "SMBJ6.0A (6.0 V standoff on the 5.09 V mezzanine rail)", "SMB", {"1": "+5V_D8", "2": "GND"}, "C83270")
c("C1", "47u 6.3V X5R 1210", "+5V_D8", "GND", "C1210"); c("C2", "47u 6.3V X5R 1210", "+5V_D8", "GND", "C1210"); c("C3", "10u", "+5V_D8", "GND", "C10u"); c("C4", "100n", "+5V_D8", "GND")
part("FB1", "Device", "FerriteBead", "600R 2A ferrite (the exciter's 1 A transmit pulses)", "FB", {"1": "+5V_TX", "2": "+5V_SA"})   # fed from U21 since round 8 (EMCON L4)
c("C5", "47u 6.3V X5R 1210", "+5V_SA", "GND", "C1210"); c("C6", "100n", "+5V_SA", "GND")
ic("U1", 5, "TLV75533PDBV 3.3 V 500 mA LDO (1 IN 2 GND 3 EN 4 NC 5 OUT)", "SOT235", {"1": "+5V_D8", "2": "GND", "3": "+5V_D8", "4": "NC", "5": "+3V3_D8"})
c("C7", "1u", "+5V_D8", "GND"); c("C8", "1u", "+3V3_D8", "GND"); c("C9", "10u", "+3V3_D8", "GND", "C10u")
led("LED1", "green power", "LED_PWR_A", "GND"); r("R1", "2.2k", "+3V3_D8", "LED_PWR_A")
r("R2", "100k", "TX_INHIBIT_n", "GND"); r("R3", "100k", "PA_EN", "GND")   # a disconnected harness reads inhibited and PA off
# EMCON L4 ON THIS BOARD'S GATES (round 8 of MESHSAT-1357, 26 September 2026; v2/docs/feasibility/EMCON.md, L4 case 2).
# Every gate on the KEY, PA_KEY and TX_INHIBIT_n paths (U9 to U14 and U18) runs on +3V3_D8, and each family is
# specified from VCC 1.65 V to 5.5 V (TECH PUBLIC 74LVC1G08 sheet, page 2; TI SCES214AF 5.3 and SCES295AB 5.3; Diodes
# DS36108, recommended operating conditions), with Ioff specified at VCC = 0 only. Between 0 and 1.65 V their outputs
# are not specified. U1 passes through that band at every power-up (its EN is tied to its input, so it ramps as soon as
# +5V_D8 is up) and stays in it if it fails or is back-fed weakly, and until this round the exciter, the gate bias
# regulator U15 and the relay coil sat on +5V_D8 and were live all the while. An output in the band at up to its own
# supply is above U15's VEN(HI) of 1.0 V (TI SBVS351D 5.5), can reach Q2's 1.0 V minimum gate threshold (JSCJ 2N7002,
# 25 C), and U13 is not specified to leave SA_PTT_n released there.
# THE REMEDY, taken by the session under the owner's standing rule of 26 September 2026: the three things those gates
# control take their 5 V through U21, a TI TPS22810 load switch (SLVSDH0C, December 2016, revised January 2018, held
# at v2/vendor/ti/ti-tps22810-load-switch.pdf; the part boards B and E already carry, TPS22810DRVR, LCSC C527679, JLC
# API 2026-09-26T21:17Z: TI, WSON-6-EP 2x2, stock 29,287), whose EN/UVLO input watches +3V3_D8 itself:
#   ON above VENR, 1.13 to 1.30 V, and OFF below VENF, 1.08 to 1.18 V, both over -40 to +105 C (7.5); and off whatever
#   EN says while VIN is under the switch's own UVLO, VUVR 2.00 to 2.62 V rising with 5 percent hysteresis (7.5):
#   "When VIN exceeds the undervoltage-lockout threshold (VUVR), the device samples the EN/UVLO pin" (9.1).
#   R90 11k over R91 10k (UNI-ROYAL 0603WAF, 1 percent and 100 ppm/C, taken over 65 K as +-1.65 percent each, the
#   convention of this file; JLC API 2026-09-26T21:18Z: C25950 0603WAF1102T5E and C25804 0603WAF1002T5E) give
#   k = 1 + R90/R91 = 2.064 to 2.137, 2.10 nominal. IEN/UVLO is 0.1 uA at most (7.5): 0.5 mV in the 5.2k Thevenin.
#     +3V3_D8 at which U21 turns ON:  1.13 x 2.064 = 2.33 V to 1.30 x 2.137 = 2.78 V;
#     +3V3_D8 at which U21 turns OFF: 1.08 x 2.064 = 2.23 V to 1.18 x 2.137 = 2.52 V.
#   So the transmit chain has its 5 V only while the gates' supply is at least 2.23 V, 0.58 V above the families'
#   1.65 V floor; and U21 is on in service: U1 delivers 3.267 V at its low corner (TI SBVS320D, +-1 percent) and
#   3.168 V at the far end of this rail's 3 percent budget, 0.39 V over the highest turn-on point. No long-term drift
#   of the UNI-ROYAL parts is held; the two margins absorb a ratio drift of +14 and -26 percent.
# WHAT IT CLOSES, at desk (a bench measurement is owed, EMCON.md rows E-01 and E-11): with +3V3_D8 held anywhere from
# 0 to 2.23 V, at any level of +5V_D8, the exciter, the bias regulator and the relay coil are unpowered, so no output
# of U9 to U14 or U18 in its unspecified band can key the exciter, bias the PA or pull in the relay. With +5V_D8 itself
# under 2.00 V U21 is off by its UVLO; at 2.00 to 2.62 V, where it may be on, +5V_TX is under the exciter's 3.3 V floor
# (SA868 v1.3), the relay's 4.0 V must-operate (Omron G6K, 5 VDC coil: 80 percent maximum) and the 4.30 V bottom of the
# VGG band. QOD reaches VOUT through R95 (100 Ohm), the second of 9.3.2's three ways ("QOD pin connected to VOUT pin
# using an external resistor REXT", RQOD = RPD + REXT, equation 1), so when U21 opens the rail is pulled down through
# 350 to 500 Ohm (RPD 250 to 400 Ohm at 5 V, 7.5), about 24 ms into its 48 uF on its own (equation 2) and faster while
# the exciter draws its 350 mA. REXT rather than QOD tied straight to VOUT: the symbol types QOD open-collector and VOUT
# power-output, a pair ERC refuses, and REXT also takes part of the discharge out of the package (9.3.2.2).
# WHAT IT DOES NOT CLOSE: +3V3_D8 falling through 2.23 V to 1.65 V faster than +5V_TX decays (U1 losing regulation
# under load, for example). The gates then pass through their band while the chain's capacitors still hold it up: a
# race between two decays that no held sheet bounds. It is the residual of L4 on this board, OWED to the bench
# (EMCON.md E-11 with +3V3_D8 stepped down while +5V_D8 is up). A +3V3_D8 that stops in the band is closed; one that
# only passes through it is not proven.
# COSTS: 0.12 V at the 1.15 A peak through RON (105 mOhm at 5 V up to +85 C, 7.5) and 0.14 W in the WSON-6 (74.6 C/W,
# 7.4: +10 K). The exciter starts about 1.1 ms after +3V3_D8 is up: CT 10 nF gives SR = 46.62 / 10000 pF = 4.7 mV/us
# (9.3.4, equation 3), an inrush of about 0.22 A into 48 uF. While U21 is off, the CP2102N's TXD (on its own regulator
# from +5V_D8) and the level stages' pull-ups (to +3V3_D8, then under 2.52 V) still reach the unpowered exciter's UART
# and status pins, for which the SA868 sheet gives no injection figure; that state occurs only at power-up and in a
# fault of U1. D-05 is unchanged: under EMCON +3V3_D8 is in range, U21 is on and the exciter keeps listening.
# C69 is an RF bypass on the EN node beside a 30 W transmitter (as C44 and C45), 5 us with the divider's Thevenin.
part("U21", "Power_Management", "TPS22810DRV", "TPS22810DRV load switch, +5V_TX on while +3V3_D8 is above 2.23 to 2.78 V (EN/UVLO divider R90 R91, QOD through R95)", "WSON6",
     {"6": "+5V_D8", "5": "TXSUP_EN", "1": "+5V_TX", "2": "TXSUP_QOD", "3": "TXSUP_CT", "4": "GND", "7": "GND"}, "C527679")
r("R95", "100R 1%", "TXSUP_QOD", "+5V_TX", lcsc="C22775")   # REXT, 9.3.2
r("R90", "11k 1%", "+3V3_D8", "TXSUP_EN", lcsc="C25950"); r("R91", "10k 1%", "TXSUP_EN", "GND", lcsc="C25804")
c("C69", "1n NP0", "TXSUP_EN", "GND", "C0402", lcsc="C113780"); c("C70", "10n", "TXSUP_CT", "GND", lcsc="C57112")
# TXSUP_EN is a sense node, not a power conductor (power_path asks, since R90 is declared a load of +3V3_D8 above)
_intent.node("TXSUP_EN", 2.6, "U21's EN/UVLO tap: +3V3_D8 x R91 / (R90 + R91), 0.16 mA through the divider and nothing else; "
             "at most 2.53 V with +3V3_D8 back-fed to 5.23 V at the resistors' low ratio (5.23 / 2.064), 1.57 V in service; "
             "the pin itself is rated to 20 V (TI SLVSDH0C 7.1)")
c("C71", "1u", "+5V_D8", "GND", lcsc="C15849")   # U21's input capacitor: CIN 1 uF (SLVSDH0C 7.3), "Place ceramic bypass capacitor(s) between this pin and GND" (pin table)
# --- the SA868 exciter (bench-fitted): PD from the expander (default on), H/L pulled low by PA_EN (0.5 W into the pad when the PA rail is up; 2 W to the antenna without the PA)
synth("U2", "SA868", "NiceRF SA868 VHF 2 W exciter, bench-fitted (castellated; VBAT 3.3 to 5.5 V, TX 1 A)", "SA868",
      {1: "SA_AUDIO_ON_n", 3: "AF_OUT", 5: "SA_PTT_n", 6: "SA_PD", 7: "SA_HL", 8: "+5V_SA", 9: "GND", 10: "GND", 12: "RF_SA", 16: "SA_RXD", 17: "SA_TXD", 18: "MIC_IN"})
nfet("Q1", "PA_EN", "GND", "SA_HL", "2N7002 PA_EN -> H/L low (never tie H/L high)")
# THE KEYING PIN HOLDS "RECEIVE" WHATEVER ITS GATE'S SUPPLY DOES (R4T-F9, review of the shared tools, round 4; 26 September
# 2026, corrected on the re-review of round 6 the same day). SA_PTT_n is driven only by U13 on +3V3_D8 from the LDO U1, while
# the SA868 runs on +5V_SA (FB1 from +5V_D8). Until round 6 the pin had no pull at all, so a failed U1 with +5V_D8 up left
# the keying pin of a powered exciter floating. The SA868 v1.3 sheet (v2/vendor/nicerf, pin table) says only that pin 5 is
# a "Module Input" on which "0" forces transmit and "1" receive; it states no internal pull, no input current and no input
# levels. It also warns that another of its pins, H/L, "can NOT be connected to VDD or high level of cmos output", so a pin
# of this module is not shown to take its own VBAT, and a pull straight to +5V_SA is not taken.
# U1 FAILED OPEN IS NOT U1 AT 0 V. With U1's output open, +3V3_D8 is back-fed: through R5 (10k) from the CP2102N's RTS (U3
# pin 24, on the bridge's own regulator SAU_3V3) whenever RTS idles high, and through R66 (10k) from the SA868's AUDIO_ON
# output (pin 1, whose high level the sheet does not state). Its loads (LED1 on R1, LED6 on R51, LED2 and LED3 on R29 and
# R30 only while the codec drives its REC and PLAY pins low, the gates' supply currents) bound nothing, so the rail can sit
# anywhere from 0 V up to its highest back-feed source, and that source is what bounds it (second fix-up of round 6): a
# logic output does not rise above the supply of the part that drives it. RTS sits on the CP2102N's own VDD, 3.1 to 3.6 V
# (Silabs CP2102N Table 3.6; Table 5.1 gives the QFN28 no VIO pin, and Table 3.1 note 3 then makes VIO = VDD), and
# AUDIO_ON on the SA868's only supply, +5V_SA, at most 5.23 V (+5V_D8's v_work; FB1 drops nothing at rest). So the
# back-fed rail is at most 5.23 V, inside the 1.65 to 5.5 V operating range of every gate on it (TECH PUBLIC 74LVC1G08
# page 2; SCES295AB 5.3; SCES214AF 5.3; DS36108, recommended operating conditions).
# A push-pull U13 drives SA_PTT_n to that rail, and no divider overrides an active output.
# SO U13 IS AN OPEN-DRAIN INVERTER, taken by the session under the owner's standing rule of 26 September 2026: TI
# SN74LVC1G06DBVR (SCES295AB, October 2025, held: Table 4-1, DBV: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC; 6.3.1, the output "sink[s]
# current to GND but not ... source[s] current from VCC"; Figure 6-2 gives the output only a clamp diode to GND, so nothing
# joins Y to VCC; VO 0 to 5.5 V at any VCC; Ioff +-10 uA at VCC 0; VOL 0.4 V at 16 mA with VCC 3 V; VIL 0.8 V at VCC 3 to
# 3.6 V; -40 to +125 C). LCSC C840103, JLC API 2026-09-26T11:55Z: Texas Instruments SN74LVC1G06DBVR, SOT-23-5, stock 8,537.
# KEY high pulls SA_PTT_n low (transmit); KEY low releases it, and R88 and R89 alone set it (receive), so while the output
# is off the level on the pin does not depend on +3V3_D8 at all. The output is off:
#   (i) with +3V3_D8 at 0 V (U1's output shorted, or nothing back-feeding): U13 is in Ioff, its output high impedance
#   (SCES295AB 6.3.4); since round 8 the exciter and this divider are also unpowered there, because U21 is off below
#   2.23 V of +3V3_D8 (EMCON L4, at U21);
#   (ii) with +3V3_D8 anywhere in 1.65 to 5.5 V, the operating range of U12 and U13 (TECH PUBLIC 74LVC1G08 sheet, page 2;
#   SCES295AB 5.3), so over the whole back-fed range up to 5.23 V, whenever EMCON is asserted: EMCON's contact holds
#   TX_INHIBIT_n at ground, and U12 holds KEY at or under its VOL of 0.1 V (the 100 uA row, which TECH PUBLIC page 3 gives
#   for VCC 1.65 to 5.5 V; while KEY is low U12 sinks only its readers' input leakage, since R84 and R49 lead to ground).
#   Both inputs are then under every VIL row the sheets tabulate, 0.3 x VCC at 4.5 to 5.5 V included. Between those rows
#   (1.95 to 2.3, 2.7 to 3.0 and 3.6 to 4.5 V) neither sheet tabulates VIL; the EMCON-asserted inputs sit near 0 V there,
#   under a fifth of the lowest VIL either sheet gives anywhere in 1.65 to 5.5 V (0.35 x 1.65 V = 0.58 V), so the
#   conclusion holds there too;
#   (iii) with EMCON released and no PTT asked for, when U12 also drives KEY low; this is shown only with +3V3_D8 at 3.6 V
#   or less (see NOT PROVEN EITHER, below).
# NOT PROVEN until round 8: +3V3_D8 above 0 and below 1.65 V, where no sheet specifies U9 to U14, and R84 holds KEY only
# against their leakage. CLOSED AT DESK IN ROUND 8 (EMCON L4, 26 September 2026) for a rail that stays anywhere under
# 2.23 V: U21 then keeps +5V_TX, and so the exciter, R88 and R89, off (at U21 below), so nothing on SA_PTT_n can key it.
# A rail that only passes through the band while +5V_TX decays is the residual named at U21. What the rail sits at with
# U1 open stays a bench measurement OWED to TEST-PLAN.md, not in it yet. SA_PD at a back-fed level (R76 to +3V3_D8) may
# select power-down or normal work, and the pin table gives transmit to pin 5 at "0" only, so no level on pin 6 keys the
# module.
# NOT PROVEN EITHER (found on the second fix-up of round 6; EMCON released, so not a D-05 case): no PTT asked for with
# +3V3_D8 back-fed above 3.6 V. PTT_SW_n idles where the CP2102N's RTS holds it, toward that part's own VDD (3.1 to 3.6 V,
# Silabs Table 3.6), not at the rail. The sheets tabulate no VIH from 3.6 to 4.5 V, and from 4.5 V their 0.7 x VCC
# (3.15 V at 4.5 V) is already above the CP2102N's 3.1 V floor, so U10 is not shown to read an idle RTS as high there, and
# a software PTT could key the exciter. The rail reaches that band only if AUDIO_ON's high level, which the SA868 sheet
# does not state, is above 3.6 V. The same bench measurement, with EMCON released and RTS idle, decides it; no circuit
# change is made for it in this round.
# THE PULL: a divider from the exciter's own rail, live whenever the exciter is, bounded by the level the pin has been driven
# with in every earlier cut (a 3.3 V output on +3V3_D8, at most 3.333 V from U1's +-1 percent, TI SBVS320D). R88 1.2k from
# +5V_SA over R89 2.0k to ground, 0.625 nominal, UNI-ROYAL 0603WAF at +-1 percent and +-100 ppm/C (JLC API
# 2026-09-26T12:01Z: C22765 and C22975, both BASIC), taken over 65 K as +-1.65 percent each. It was 12k over 20k in the first
# cut of round 6; it now sets the receive level in service as well, and the SA868 states no pin 5 current, so the Thevenin
# comes down tenfold, to 0.76k, where 10 uA moves the pin 7.6 mV instead of 76 mV:
#   top: 5.23 V (+5V_D8's v_work; the ferrite drops nothing at rest) x 0.6327 = 3.309 V, 3.317 V with +-10 uA from U13's
#   output. That term is a STAND-IN: SCES295AB states no off-state output current with VCC applied, and the +-10 uA is
#   Ioff, its VCC = 0 figure, the only one held for this pin, with no sign given (at 0.76k even 100 uA would move the pin
#   only 76 mV);
#   bottom: 4.35 V (the source's 4.90 V less both declared drop budgets, +5V_D8's 6 and +5V_SA's 5 percent, a transmit
#   current worst case, so conservative for the receive state this pull is for) x 0.6172 = 2.685 V, 2.677 V with the same
#   stand-in; nominal 3.18 V at 5.088 V.
#   The 3.333 V ceiling is this design's own choice, the level the pin has always been driven with, not a limit the SA868
#   sheet states. The band carries tolerance and TCR only: no UNI-ROYAL sheet with an endurance drift figure is held, and
#   the top corner sits 16 mV under that ceiling.
# Costs: U13 low (transmit) sinks at most 5.23 V / 1.18k = 4.4 mA, inside the 16 mA at which SCES295AB gives VOL 0.4 V at
# VCC 3 V; R88 then dissipates 23 mW of its 100 mW; the divider draws 1.7 mA from +5V_SA. The census tx_inhibit.py takes
# against a forced "1" is R89's 3.3 V / 1.97k = 1.7 mA, inside its 4 mA.
# WHAT THIS DOES NOT PROVE: the SA868's threshold for "1" and its pin 5 current. The pin reads 2.68 to 3.32 V in every
# state, 3.18 V nominal, where the push-pull U13 of earlier cuts gave 3.17 V or more in service. The level on SA_PTT_n
# with U1 fitted, with U1 unfitted and with U1's output shorted, and that the exciter stays in receive in each (no carrier
# into a dummy load), are a bench measurement OWED to TEST-PLAN.md, not in it yet.
r("R88", "1.2k", "+5V_SA", "SA_PTT_n", lcsc="C22765"); r("R89", "2k", "SA_PTT_n", "GND", lcsc="C22975")
cp2102("U3", "SAU", "+5V_D8", "USB2_P", "USB2_N", "SA_RXD", "SA_TXD", rts="PTT_SW_n", refs=("R4", "C10", "C11"))   # the bridge's TXD into the exciter's RXD; RTS low = software PTT
# PWR-001 (EQ-19, board D stream w3de, 27 September 2026, MESHSAT-1357): THE BRIDGE'S OWN 3.3 V IS A NODE. PWR-001 on the
# committed netlist refused SAU_3V3 as an undeclared power net. Silicon Labs CP2102N data sheet Rev. 1.5 (held at
# v2/vendor/silabs/silabs-cp2102n.pdf): QFN28 pin 6 VDD "Supply Power Input / 5V Regulator Output" (5.1, pin
# definitions); Table 3.6 5V Voltage Regulator: "Output Voltage on VDD" 3.1 / 3.3 / 3.6 V at 1 to 100 mA with VREGIN
# at 4.1 V or more (VREGIN is +5V_D8 here), and "Output current is total regulator output, including any current required
# by the device"; absolute maximum "Voltage on VDD" 4.2 V. The net carries U3's own regulator output, its C10 and C11 and
# R4, the RSTb pull-up (the helper's docstring): no other part's supply pin, so the kind is a NODE (a part's own internal
# regulator output) at the characterised 3.6 V. Session decision under the owner's standing rule of 26 September 2026;
# reverse by a load on SAU_3V3 that is another part's supply.
_intent.node("SAU_3V3", 3.6, "the CP2102N's own regulator output on its VDD pin (pin 6, 'Supply Power Input / 5V Regulator "
             "Output'), fed from VREGIN on +5V_D8: 3.1 / 3.3 / 3.6 V 'Output Voltage on VDD' (Silicon Labs CP2102N Rev. 1.5, "
             "Table 3.6); absolute maximum 4.2 V; it carries U3's own supply, C10, C11 and the RSTb pull-up R4")
r("R5", "10k", "PTT_SW_n", "+3V3_D8")
# --- USB hub TUSB2046I (self-powered, no EEPROM, 6 MHz crystal): upstream from the harness pair, port 1 the codec, port 2 the bridge, port 3 a spare header, port 4 terminated
# W6-F5, 26 September 2026: THE HUB WAS NAMED "TUSB2046BI" IN LQFP-32, WHICH DOES NOT EXIST, AND THE CODE BOUGHT WAS
# COMMERCIAL. TI SLLS413L (June 2017; the copy TI serves on 25 September 2026 is the same revision with the
# 31-Oct-2025 orderable addendum) lists TUSB2046BI only in the RHB VQFN; the LQFP-32 (VF) parts are TUSB2046BVF/BVFR
# (0 to 70 C) and TUSB2046IBVF/IBVFR (-40 to 85 C, marking TUSB2046I). C167642, the code the D11 BOM carried, is the
# TUSB2046BVFR, outside the -20 C envelope. READ FOR DIFFERENCES BEFORE ADOPTING (owner condition 1): one data sheet
# covers both; the VF pin functions table (page 4 and 5) and the electrical characteristics (7.5 to 7.7) are shared
# with no per-grade rows; revision L's only change is "Added device TUSB2046IB". Two rows differ by grade: TA (0 to 70
# against -40 to 85, pages 6 and 7.3) and VCC in 7.3 (B 3.0 / 3.3 / 3.6, I 3.3 MIN / 3.6 MAX). The pin map below is
# the same; the supply is the one difference that touches this board, and it is met by U17 below, which is why the
# hub no longer sits on +3V3_D8. TUSB2046IBVFR is LCSC C702369 (JLC API 2026-09-25T23:09Z: TI, LQFP-32 7x7, -40 to
# +85 C, 3.3 to 3.6 V, stock 16: five boards need five, and the ordering session must re-read the stock).
esd("U5", "USB_D8_P", "USB_D8_N", "+5V_D8")
r("R6", "22", "USB_D8_P", "HUB_DP0"); r("R7", "22", "USB_D8_N", "HUB_DM0"); r("R8", "1.5k", "HUB_DP0", "+3V4_HUB")   # the upstream attach pull-up follows the hub's own supply (W6-F5)
synth("U4", "TUSB2046I", "TUSB2046IBVFR four-port USB 2.0 full-speed hub (TI, LQFP-32 VF, -40 to 85 C, VCC 3.3 to 3.6 from +3V4_HUB; BUSPWR low = self-powered, EXTMEM high, GANGED high, TSTMODE low)", "LQFP32",
      {1: "HUB_DP0", 2: "HUB_DM0", 3: "+3V4_HUB", 25: "+3V4_HUB", 4: "HUB_RST_n", 6: "+3V4_HUB", 7: "GND", 28: "GND", 8: "GND", 10: "HUB_OVRCUR_n", 14: "HUB_OVRCUR_n", 18: "HUB_OVRCUR_n", 22: "HUB_OVRCUR_n",
       11: "HUB_DM1", 12: "HUB_DP1", 15: "HUB_DM2", 16: "HUB_DP2", 19: "HUB_DM3", 20: "HUB_DP3", 23: "HUB_DM4", 24: "HUB_DP4", 26: "+3V4_HUB", 27: "GND", 29: "HUB_XTAL2", 30: "HUB_XTAL1", 31: "GND"}, "C702369")
r("R9", "10k", "HUB_OVRCUR_n", "+3V4_HUB"); r("R10", "10k", "HUB_RST_n", "+3V4_HUB"); c("C12", "1u", "HUB_RST_n", "GND")   # every hub input is tied to the hub's own VCC (SLLS413L 7.3: VI 0 to VCC)
# U17, the hub's LDO (W6-F5, 26 September 2026; the arithmetic is at the +3V4_HUB declaration above). TLV75801PDBVR,
# LCSC C2877852 (JLC API 2026-09-25T23:09Z: TI, SOT-23-5, -40 to 125 C TJ, stock 165,250). EN tied to IN as U1's is.
# C64 is its input capacitor and C65 its own output capacitor, both 1 uF (SBVS351D 5.3: CIN 1 uF, COUT 1 to 220 uF,
# 0.47 uF minimum after derating), so its stability does not depend on where the layout puts the hub's C17.
# R80 + R81 = 66.9k. SBVS351D equation 3 sets R1 + R2 <= VOUT / (100 x IFB) and its text takes IFB = 10 nA, which
# allows 3.44 MOhm; at the 0.1 uA maximum of the table it is 344k, and 66.9k is under both. The IFB error at that
# maximum is carried in the band above (5.6 mV), not assumed away.
# R80 AND R81 ARE PRECISION PARTS (review fix-up of round 4, 26 September 2026): the 1 percent 100 ppm/C UNI-ROYAL
# thick film first drawn (C23080, C22857) let the pin fall below the hub's 3.3 V minimum at the band's low corner.
# YAGEO RT0603BRD0756K2L, LCSC C705784, and RT0603BRD0710K7L, LCSC C861078: RT series thin film, 0603, B = +-0.1
# percent, D = +-25 ppm/C, 1/10 W, 75 V, -55 to +155 C, offered in 0603 at 0.1 percent and 25 ppm from 1 Ohm to 1 MOhm
# (YAGEO RT series product specification V.16, 6 May 2025, ordering code and Table 2). The land is the same
# R_0603_1608Metric (RT0603 1.60 x 0.80 mm). JLC API 2026-09-25T23:51Z: both extended, stock 10,837 and 1,011.
# The capacitors are the 0603 "1u" of lcsc_fill's table, CL10A105KB8NNNC C15849 (50 V X5R).
ic("U17", 5, "TLV75801PDBVR adjustable LDO, +3V4_HUB 3.44 V for the hub (1 IN 2 GND 3 EN 4 FB 5 OUT)", "SOT235", {"1": "+5V_D8", "2": "GND", "3": "+5V_D8", "4": "HUB_FB", "5": "+3V4_HUB"}, "C2877852")
c("C64", "1u", "+5V_D8", "GND", lcsc="C15849"); c("C65", "1u", "+3V4_HUB", "GND", lcsc="C15849")
r("R80", "56.2k 0.1% 25ppm", "+3V4_HUB", "HUB_FB", lcsc="C705784"); r("R81", "10.7k 0.1% 25ppm", "HUB_FB", "GND", lcsc="C861078")
# OWNER DECISION 37, RULED BY THE SESSION 21 SEPTEMBER 2026: A 6 MHz PASSIVE CRYSTAL EXISTS IN ONE PACKAGE AND
# IT IS NOT THE ONE THIS BOARD DREW. Measured against JLCPCB's catalogue: every 6 MHz part in a SMD3225-4P land
# is an ACTIVE OSCILLATOR, which is a property of the blank and not of the catalogue, and the hub's own
# datasheet (TI SLLS413, TUSB2046B clause 8.3.2) says a passive crystal or resonator MUST be used if low-power
# suspend and resume are wanted, which this kit wants. The land is HC-49S-SMD, the part is C252308 (-40 to
# +85 C, CL 20 pF, 80 Ohm, 376 in stock at 0.1333 USD) with C518119 as the second source; the wide-temperature
# range is chosen over the -20/+70 parts because the crystal lives INSIDE a sealed case whose own envelope
# (decision 34) allows +55 C of inside air, not because the ambient asks for it.
# AND Rd IS RE-CHOSEN FOR THE PART THAT IS BOUGHT: TI's figure 6 gives 1.5k for a crystal of at most 50 Ohm and
# every wide-temperature 6 MHz part reads 80, so the damping comes down to the reactance of C2 at 6 MHz, which
# is 1/(2*pi*6e6*27e-12) = 982 Ohm, and 1.0k is that value in a standard resistor. The negative-resistance
# margin (five times ESR, so 400 Ohm) is a BENCH MEASUREMENT at bring-up, the same shape as the 24 MHz
# load-capacitance correction of 16 September. CORRECTED 26 September 2026 (W5-F14): this line said the test "is
# in TEST-PLAN.md" and the plan at 82dd1e4d did not carry it. The measurement is OWED to TEST-PLAN.md: workstream
# W5 drafts it there as row HW10, and until that row lands this comment is its only record in the tree. The part's
# own sheet (SJK 6CS series, P/N 6CS06000F20UCG, the datasheet LCSC links for C252308): 6.000 MHz AT fundamental,
# CL 20 pF, C0 3 pF max, ESR 80 Ohm max, -40 to +85 C, drive 100 uW typical, which is where the 80 and the 400 come from.
part("Y1", "Device", "Crystal", "6 MHz HC-49S-SMD passive (CL 20 pF, 80 Ohm; C1 = C2 = 27 pF and Rd 1.0k, SLLS413 figure 6 re-chosen for this part's ESR)", "XTAL", {"1": "HUB_XTAL1", "2": "HUB_XTAL2R"}, "C252308")
# decision 37: the damping is the reactance of C2 at 6 MHz (982 Ohm), because the part that exists reads
# 80 Ohm of ESR where TI's figure 6 assumes at most 50.
r("R11", "1.0k", "HUB_XTAL2R", "HUB_XTAL2"); c("C13", "27p NP0", "HUB_XTAL1", "GND", "C0402"); c("C14", "27p NP0", "HUB_XTAL2R", "GND", "C0402")
c("C15", "100n", "+3V4_HUB", "GND"); c("C16", "100n", "+3V4_HUB", "GND"); c("C17", "10u", "+3V4_HUB", "GND", "C10u")   # the hub's decoupling, on its own rail since W6-F5 (26 September 2026)
for port, (dp, dm, tp, tm, rs) in {1: ("HUB_DP1", "HUB_DM1", "USB1_P", "USB1_N", 12), 2: ("HUB_DP2", "HUB_DM2", "USB2_P", "USB2_N", 16), 3: ("HUB_DP3", "HUB_DM3", "USB3_P", "USB3_N", 20)}.items():
    r("R%d" % rs, "22", dp, tp); r("R%d" % (rs + 1), "22", dm, tm); r("R%d" % (rs + 2), "15k", tp, "GND"); r("R%d" % (rs + 3), "15k", tm, "GND")
r("R24", "15k", "HUB_DP4", "GND"); r("R25", "15k", "HUB_DM4", "GND")
part("J_USB3", "Connector_Generic", "Conn_01x04", "JST-PH 1x4 socket: spare hub port 3, 5V D- D+ GND (the lead is made up at build)", "PH4", {"1": "+5V_D8", "2": "USB3_N", "3": "USB3_P", "4": "GND"}, "C131334")
# --- USB audio codec PCM2912A (VBUS 5 V, its regulator feeds VDD and the VCC pins: decoupling only; MAMP off = line level, POWER low, TEST1 high, TEST0 low)
r("R26", "33", "USB1_P", "USB1_PR"); r("R27", "33", "USB1_N", "USB1_NR"); r("R28", "1.5k", "USB1_PR", "PCM_VDD")
synth("U6", "PCM2912A", "TI PCM2912A USB audio codec (TQFP-32): mono input from the exciter, stereo output to the headphone amplifier and the transmit sum", "TQFP32",
      {1: "GND", 2: "+5V_D8", 3: "USB1_NR", 4: "USB1_PR", 5: "PCM_VDD", 6: "GND", 7: "PCM_XTO", 8: "PCM_XTI", 11: "PCM_VCOM1", 12: "PCM_VCOM2", 13: "GND", 15: "PCM_VCCA", 16: "PCM_VIN", 18: "PCM_VOUTL",
       19: "PCM_VCCL", 20: "GND", 21: "PCM_VCCR", 22: "PCM_VOUTR", 23: "GND", 24: "GND", 25: "GND", 26: "PCM_VCCP", 27: "PCM_VDD", 28: "GND", 30: "MMUTE", 31: "LED_REC_K", 32: "LED_PLAY_K"})
c("C18", "1u", "+5V_D8", "GND"); c("C19", "1u", "PCM_VDD", "GND"); c("C20", "1u", "PCM_VCCA", "GND"); c("C21", "1u", "PCM_VCCL", "GND"); c("C22", "1u", "PCM_VCCR", "GND"); c("C23", "1u", "PCM_VCCP", "GND")
# PWR-001 (EQ-19, board D stream w3de, 27 September 2026, MESHSAT-1357): THE CODEC'S FIVE REGULATOR OUTPUTS ARE NODES.
# PWR-001 on the committed netlist refused PCM_VDD, PCM_VCCA, PCM_VCCL, PCM_VCCR and PCM_VCCP as undeclared power nets.
# TI SLES230A (held at v2/vendor/ti/ti-pcm2912a.pdf), 9.5.1.6 Internal Regulator (p.23): "All required power sources are
# generated by five internal regulators. Each regulator generates 3.3 V (typical, without load) from VBUS (pin 2). Each
# regulator has an output pin and a ground return pin ...; this pair must be decoupled with an appropriate capacitor";
# Table 6 names the outputs VDD (pin 5), VCCA (15), VCCL (19), VCCR (21) and VCCP (26). Electrical characteristics:
# "Internally-generated power supply voltage" 3.0 / 3.3 / 3.6 V (note 10: pins 5, 15, 19, 21, 26); absolute maximum
# input voltage on the same five pins -0.3 to 4 V. Each net carries U6's own regulator output and its 1 uF (C19 to C23),
# so the kind is a NODE (a part's own internal regulator output), with the characterised 3.6 V as its peak. PCM_VDD also
# carries U6's TEST1 (pin 27, "Must be set to HIGH") and R28, the 1.5k full-speed pull-up to D+ (about 0.2 mA): both are
# the codec's own use of its digital supply, and no other part's supply pin is on the net. Session decision under the
# owner's standing rule of 26 September 2026; reverse by a load on one of these nets that is another part's supply.
for _pcm_net, _pcm_pin, _pcm_what in (("PCM_VDD", 5, "digital"), ("PCM_VCCA", 15, "analog"), ("PCM_VCCL", 19, "L-channel headphone"),
                                      ("PCM_VCCR", 21, "R-channel headphone"), ("PCM_VCCP", 26, "PLL")):
    _intent.node(_pcm_net, 3.6, "the PCM2912A's own %s regulator output (pin %d), generated from VBUS inside the part: 3.0 / 3.3 / "
                 "3.6 V 'Internally-generated power supply voltage' (TI SLES230A electrical characteristics, note 10), "
                 "9.5.1.6 and Table 6 (p.23); absolute maximum 4 V on the pin" % (_pcm_what, _pcm_pin))
c("C24", "10u", "PCM_VCOM1", "GND", "C10u"); c("C25", "10u", "PCM_VCOM2", "GND", "C10u")
# THE CODEC'S CLOCK IS 6 MHz AND ITS OWN DATASHEET CONTRADICTS ITSELF ABOUT IT (read 21 September 2026,
# v2/vendor/ti/ti-pcm2912a.pdf): the feature list says "With Single 6-MHz Clock Source" and the ELECTRICAL
# TABLE says "Input clock frequency, XTI  5.997 / 6.000 / 6.003 MHz", while one application paragraph says the
# device "requires a 12-MHz clock". Two statements against one, and the binding one is the specification
# table, so this board's 6 MHz is right and the 12 MHz sentence is left over from a sibling part. It is
# written down here so that nobody reading section 9 "corrects" a working design.
# Its loads go 18 pF to 27 pF with the land: 27 pF is 2*(CL - Cstray) for the CL 20 pF part decision 37 rules,
# which is the same arithmetic TI's own figure 6 does for the hub.
part("Y2", "Device", "Crystal", "6 MHz HC-49S-SMD passive (codec clock, CL 20 pF; C1 = C2 = 27 pF)", "XTAL", {"1": "PCM_XTI", "2": "PCM_XTO"}, "C252308")
c("C26", "27p NP0", "PCM_XTI", "GND", "C0402"); c("C27", "27p NP0", "PCM_XTO", "GND", "C0402")   # decision 37: 2*(CL - Cstray) for the CL 20 pF part
led("LED2", "yellow record", "LED_REC_A", "LED_REC_K"); r("R29", "1k", "+3V3_D8", "LED_REC_A"); led("LED3", "green playback", "LED_PLAY_A", "LED_PLAY_K"); r("R30", "1k", "+3V3_D8", "LED_PLAY_A")
r("R31", "10k", "AF_OUT", "AF_DIV"); r("R32", "10k", "AF_DIV", "GND"); c("C28", "1u", "AF_DIV", "PCM_VIN")   # 700 mV receive audio halved into the ADC
# mute only when the expander drives it high (the codec pulls it down itself).
# A01 remaining unknown 4, examined 26 September 2026: U16 powers up with every port an INPUT behind its internal
# pull-up (TI SCPS131J 8.1; about 100k in the figure, at least 33k from IIL -100 uA at 0 V), and the codec's MMUTE
# is a TTL-level input with an internal pull-down (TI PCM2912A SLES230A: VIH 2.0, VIL 0.8, IIH 65 typ / 100 max uA at
# 3.3 V, input logic family TTL). With 4.7k in series and 100k to ground, MMUTE sat at 0.8 V with typical parts and
# 1.56 V with a strong pull-up, between VIL and VIH, until the panel firmware first wrote U16.
# RESTATED ON GUARANTEED FIGURES ONLY (review fix-up of round 4, 26 September 2026). The first fix, 1.0k over 4.7k,
# claimed 2.53 V or more when driven high from a 3.15 V output the PCA9555 sheet does not guarantee; its only
# guaranteed P-port figure at this supply is VOH 2.6 V minimum at IOH -8 mA with VCC 3.0 V (SCPS131J 6.5), which
# gave 2.09 V, 92 mV over VIH. R33 is now 470R, a JLC basic part (UNI-ROYAL 0603WAF4700T5E, C23179, JLC API
# 2026-09-25T23:54Z), which balances the two margins on guaranteed numbers:
#   power-up, U16 an input: its pull-up sources at most 100 uA (IIL -100 uA at VI = GND, VCC 2.3 to 5.5 V, and a
#   pull-up sources less at any higher node), so MMUTE <= 100 uA x 4.7k = 0.47 V, the codec's own pull-down ignored:
#   0.33 V under VIL 0.8 V;
#   driven high: U16 sources under 1 mA here, so VOH >= 2.6 V, into 470R over 4.7k in parallel with the codec's
#   pull-down at its strongest (33k, from IIH 100 uA at 3.3 V): MMUTE >= 2.6 x 4.11 / 4.58 = 2.33 V, 0.33 V over VIH;
#   back-drive into an unpowered codec: at most 3.4 V / 470R = 7.2 mA even into a short, under SLES230A's 10 mA
#   input current and with MMUTE's 4 V absolute maximum not referred to its supply.
# THE TWO CONDITIONS THOSE MARGINS STAND ON (re-review of round 4, 26 September 2026): the codec's VIH 2.0 V and
# VIL 0.8 V are specified at TA = 25 C and VBUS = 5 V only (SLES230A 7.5 heading; no over-temperature row is
# published), and U16's VOH 2.6 V holds with its VCC, the harness +3V3 that board A declares at 3.3 V with a 3
# percent drop budget, at 3.0 V or more (SCPS131J 6.5, over the operating free-air range). Outside 25 C the codec's
# thresholds are not published, so the levels at power-up and when driven are a bench measurement OWED to
# TEST-PLAN.md over the envelope, not yet in it.
# So the default is a defined "mute off", as the line above intends, and "mute on" is defined when U16 drives it.
r("R33", "470R", "X_MMUTE", "MMUTE", lcsc="C23179"); r("R34", "4.7k", "MMUTE", "GND")
# --- headphone amplifier TPA6132A2 (G0 high, G1 low = 0 dB): the receive mix (exciter AF_OUT + codec playback L) to both headset earpieces
synth("U7", "TPA6132A2", "TI TPA6132A2 headphone amplifier (QFN-16), receive audio to the two headset leads", "QFN16",
      {1: "AMP_INL_N", 2: "AMP_INL_P", 3: "AMP_INR_P", 4: "AMP_INR_N", 5: "HS2_SPK", 6: "+3V3_D8", 7: "GND", 8: "AMP_HPVSS", 9: "AMP_CPN", 10: "GND", 11: "AMP_CPP", 12: "AMP_HPVDD", 13: "AMP_EN", 14: "+5V_D8", 15: "GND", 16: "HS1_SPK", 17: "GND"})
# G12 OF THE DECOUPLING RULING (round 8 of MESHSAT-1357, 26 September 2026; v2/docs/feasibility/DECOUPLING.md sections 4,
# 6a and 8.3). TI SLOS597B (July 2017, held at v2/vendor/ti/ti-tpa6132a2.pdf, sha256 e8a23e00): "Connect the HPVDD pin only
# to a 2.2 uF, X5R or better, capacitor ... Place both capacitors within 5 mm of their associated pins on the TPA6132A2.
# Ensure that the ground connection of each of the capacitors has a minimum length return path to the device" (9, p.17);
# "Place a 2.2 uF capacitor within 5 mm of the VDD pin ... Use 0402 or smaller size capacitors if possible" (9.1, p.17);
# the pin table asks the same of HPVDD, "Connect to a 2.2uF capacitor. Do not connect to VDD" (5, p.3), and the
# application figures draw both at 2.2 uF (pp.14, 16). C31 (HPVDD) and C32 (VDD) were 1 uF 0603: both become 2.2 uF X5R in
# 0402, Samsung CL05A225KO5NQNC, LCSC C170151 (JLC API 2026-09-26T21:18Z: 16 V, X5R, +-10 percent, 0402, stock 958,326;
# Samsung's own specification page for CL05A225KO5NQN, read 2026-09-26: 2.2 uF, +-10 percent, 16.0 Vdc, X5R, 1.00 x
# 0.50 x 0.50 mm, "Graphs for the item are not supported"). 16 V rather than 10 V because VDD sits on +5V_D8 (5.23 V
# working): the DC-bias loss of an 0402 X5R is least at the highest rating the land takes, and no Samsung bias curve is
# published for it, so the effective capacitance at 5.23 V stays a bench measurement (DECOUPLING.md 5.5, TBD). HPVDD is
# generated inside the part, 1.9 V absolute maximum (SLOS597B 6.1), declared below as a node so derate judges C31's 16 V.
# C33 (10 uF, SLOS597B 9.1: "an additional 10 uF or higher value capacitor ... unnecessary in most applications")
# stays, class B2. The 5 mm seat is the next placement's (G12 without it does not meet SLOS597B: on D12 C31 and C32 sit
# 18.1 and 13.6 mm from their pins).
c("C29", "1u", "AMP_HPVSS", "GND"); c("C30", "1u", "AMP_CPP", "AMP_CPN"); c("C31", "2.2u 16V X5R 0402", "AMP_HPVDD", "GND", "C0402", lcsc="C170151"); c("C32", "2.2u 16V X5R 0402", "+5V_D8", "GND", "C0402", lcsc="C170151"); c("C33", "10u", "+5V_D8", "GND", "C10u")
_intent.node("AMP_HPVDD", 1.9, "the TPA6132A2's internal positive supply for its headphone amplifiers, generated inside the part "
             "and never driven from outside: 'Headphone amplifier supply voltage HPVDD (do not connect to external supply) "
             "-0.3 to 1.9 V' (TI SLOS597B 6.1, Absolute Maximum Ratings); the pin takes only its 2.2 uF (5, 9)")
# PWR-001 (EQ-19, board D stream w3de, 27 September 2026, MESHSAT-1357): THE CHARGE PUMP'S THREE NETS ARE NODES OF THE
# PART'S OWN NEGATIVE SUPPLY. PWR-001 on the committed netlist refused AMP_CPP, AMP_CPN and AMP_HPVSS as undeclared power
# nets (each is a supply pin by its held datasheet row). TI SLOS597B (held at v2/vendor/ti/ti-tpa6132a2.pdf), pin table
# (5, p.3): HPVSS "Charge pump output and negative power supply for output amplifiers; connect 1uF capacitor to GND", CPN
# "Charge pump negative flying cap. Connect to negative side of 1uF capacitor between CPP and CPN", CPP "Charge pump
# positive flying cap. Connect to positive side of 1uF capacitor between CPP and CPN"; 8.1 (p.14): "The charge pump
# generates a negative supply voltage. The charge pump flying capacitor connected between CPP and CPN transfers charge to
# generate the negative supply voltage"; the functional block diagram (7.2, p.10) feeds the charge pump from HPVDD. Each
# net carries U7's own pins and its own capacitor and nothing else, so the kind is a NODE (a part's charge pump, which the
# rule names as a node), not a rail. THE VOLTAGES: the sheet publishes no figure for HPVSS, CPP or CPN. The pump inverts
# HPVDD (block diagram 7.2), whose absolute maximum is 1.9 V (6.1), so CPP swings between ground and HPVDD, CPN between
# HPVSS and ground, and HPVSS sits at about minus HPVDD: -1.9 V at most below ground. That bound is read from the
# block diagram and the HPVDD rating, not a published HPVSS limit, and is stated as such. C30 across CPP and CPN holds
# HPVDD, so CPN rides on CPP at 1.9 V and derate judges C30 against that. Session decision under the owner's standing
# rule of 26 September 2026 (the kind and the bound); reverse by a TI figure for HPVSS that differs.
_intent.node("AMP_CPP", 1.9, "the TPA6132A2's charge pump positive flying-capacitor node (TI SLOS597B pin table p.3, 8.1): it "
             "swings between ground and HPVDD, whose absolute maximum is 1.9 V (6.1)")
_intent.node("AMP_CPN", 0.0, "the TPA6132A2's charge pump negative flying-capacitor node (SLOS597B pin table p.3, 8.1): it "
             "swings between HPVSS and ground; C30 holds HPVDD (at most 1.9 V, 6.1) across CPP and CPN, so it rides on CPP",
             v_min=-1.9, rides_on="AMP_CPP", bias_v=1.9)
_intent.node("AMP_HPVSS", 0.0, "the TPA6132A2's charge pump output, the negative supply of its headphone amplifiers (SLOS597B pin "
             "table p.3: 'Charge pump output and negative power supply for output amplifiers'): the inversion of HPVDD "
             "(block diagram 7.2), so no lower than -1.9 V, HPVDD's absolute maximum (6.1); the sheet gives no HPVSS "
             "figure of its own", v_min=-1.9)
r("R35", "10k", "AF_OUT", "RX_MIX"); c("C34", "1u", "PCM_VOUTL", "PCM_L_AC"); r("R36", "10k", "PCM_L_AC", "RX_MIX"); r("R37", "10k", "RX_MIX", "GND")
c("C35", "1u", "RX_MIX", "AMP_INL_P"); c("C36", "1u", "RX_MIX", "AMP_INR_P"); c("C37", "1u", "AMP_INL_N", "GND"); c("C38", "1u", "AMP_INR_N", "GND")
# --- microphone summing preamplifier TLV9062 (33 dB, both headset microphones; electret bias by solder jumper) into the exciter's MIC_IN with the codec's transmit audio (R)
ic("U8", 8, "TLV9062IDGK dual op amp (1 OUT1 2 IN1- 3 IN1+ 4 V- 5 IN2+ 6 IN2- 7 OUT2 8 V+): A the mic sum, B unused as a follower", "VSSOP8",
   {"1": "MICAMP_OUT", "2": "MICAMP_IN_N", "3": "VREF", "4": "GND", "5": "VREF", "6": "OPB_OUT", "7": "OPB_OUT", "8": "+5V_D8"})
c("C39", "100n", "+5V_D8", "GND"); r("R38", "10k", "+5V_D8", "VREF"); r("R39", "10k", "VREF", "GND"); c("C40", "10u", "VREF", "GND", "C10u")
c("C41", "1u", "HS1_MIC", "HS1_MIC_AC"); r("R40", "4.7k", "HS1_MIC_AC", "MICAMP_IN_N"); c("C42", "1u", "HS2_MIC", "HS2_MIC_AC"); r("R41", "4.7k", "HS2_MIC_AC", "MICAMP_IN_N")
r("R42", "220k", "MICAMP_OUT", "MICAMP_IN_N"); c("C43", "100p NP0", "MICAMP_OUT", "MICAMP_IN_N", "C0402")
part("JP1", "Jumper", "SolderJumper_2_Open", "electret bias headset 1 (close for an electret microphone)", "JP", {"1": "HS1_MIC", "2": "HS1_BIAS_R"}); r("R43", "2.2k", "HS1_BIAS_R", "+5V_D8")
part("JP2", "Jumper", "SolderJumper_2_Open", "electret bias headset 2", "JP", {"1": "HS2_MIC", "2": "HS2_BIAS_R"}); r("R44", "2.2k", "HS2_BIAS_R", "+5V_D8")
# R8D-P1 (round 8, found while choosing the new RF bypasses): the certified row "1n NP0" on C_0402 resolves to C1523, which
# JLCPCB reads back as FH 0402B102K500NT, "1nF 50V X7R" (API 2026-09-26T21:18Z): an X7R part under an NP0 value, a mismatch
# under owner condition 1. Pinned here to YAGEO CC0402JRNPO9BN102, LCSC C113780 (API the same minute: "1nF 50V NP0 +-5%
# 0402", stock 160,278), the NP0 series of the 27 pF parts this board already buys (YAGEO CC general purpose NP0 16 V to
# 250 V, product specification V.21, 14 March 2025: CC 0402 J R NPO 9 BN 102 is 0402, +-5 percent, NP0, 50 V, 1 nF).
c("C44", "1n NP0", "HS1_MIC", "GND", "C0402", lcsc="C113780"); c("C45", "1n NP0", "HS2_MIC", "GND", "C0402", lcsc="C113780")   # RF bypass beside a 30 W transmitter
c("C46", "1u", "MICAMP_OUT", "MICAMP_AC"); r("R45", "10k", "MICAMP_AC", "MIC_SUM"); c("C47", "1u", "PCM_VOUTR", "PCM_R_AC"); r("R46", "10k", "PCM_R_AC", "MIC_SUM"); r("R47", "10k", "MIC_SUM", "GND"); c("C48", "1u", "MIC_SUM", "MIC_IN")
# --- headset leads to the face plate's two U-174/U jacks (JST-PH 1x5): SPK GND MIC GND PTT
part("J_HS1", "Connector_Generic", "Conn_01x05", "JST-PH 1x5 socket: headset 1, SPK GND MIC GND PTT (the lead runs to the face plate U-174/U jack)", "PH5", {"1": "HS1_SPK", "2": "GND", "3": "HS1_MIC", "4": "GND", "5": "PTT_HS1_n"}, "C157993")
part("J_HS2", "Connector_Generic", "Conn_01x05", "JST-PH 1x5 socket: headset 2, SPK GND MIC GND PTT (the lead runs to the face plate U-174/U jack)", "PH5", {"1": "HS2_SPK", "2": "GND", "3": "HS2_MIC", "4": "GND", "5": "PTT_HS2_n"}, "C157993")
c("C49", "100n", "PTT_HS1_n", "GND"); c("C50", "100n", "PTT_HS2_n", "GND")
# OWNER DECISION 31, RULED BY THE SESSION 21 SEPTEMBER 2026: THE SIX HEADSET CONDUCTORS GET BIDIRECTIONAL
# CLAMPS AT THE JACK. Each jack carries a speaker line, a microphone line and a push to talk out of the case to
# a U-174/U on the face plate, and a person plugs a headset into it having walked across a floor. port_protect
# has named all six since the rule was written; decision 34 states the level, IEC 61000-4-2 level 4 at 8 kV
# contact and 15 kV air.
# WHY BIDIRECTIONAL, measured on this board rather than assumed: U7 is a TPA6132A2 DirectPath amplifier with a
# charge pump (C30 across AMP_CPP and AMP_CPN, C29 on the negative AMP_HPVSS), so the speaker conductors are
# GROUND REFERENCED and swing below ground; the microphone conductor carries a 5 V electret bias through JP1
# and R43 from +5V_D8 when that jumper is closed; PTT idles at 3.3 V through R68 into U9 and Q4. A rail-
# referenced array of the USBLC6 kind clamps to its own rail and to ground, so its lower diode would conduct on
# the speaker's negative half.
# WHY SIX SINGLES RATHER THAN FOUR DOUBLES, which is where this started: a two-channel SOT-23 array needs
# 3.4 mm of courtyard and the only ground within five millimetres of these pins is 2.67 mm wide, between U7's
# escape fan and the jack's own barrels, or 2.67 mm between the barrels and the board edge. Seated in the wider
# places the arrays cost U7 six escapes of seventeen (D35P, third run) and sat 2.75 to 4.8 mm from their pins.
# The Nexperia PESD5V0S1BA is the same protection one line at a time in a SOD323 that fits east of the jack's
# own barrels, on the underside this board already assembles: C19224, 59,375 in stock at 0.0858 USD,
# assets.nexperia.com/documents/data-sheet/PESD5V0S1BA.pdf, bidirectional, reverse standoff 5 V, diode
# capacitance 35 pF typical, rated IEC 61000-4-2 contact discharge 30 kV and IEC 61000-4-5 surge 12 A. Six of
# them put EVERY conductor 2.25 mm from its own clamp and cost U7 nothing.
# W7-F3 / W6-F14, 26 September 2026: ONE CLAMP PER CONDUCTOR, CHOSEN AGAINST THAT CONDUCTOR'S OWN WORKING VOLTAGE.
# Decision 31's record names two PESD5V0S2BT per jack; the six singles are the measured substitution argued above
# (and in the appendix), and the ruled dual carries the same 5 V stand-off (Nexperia PESD5V0S2BT product data sheet,
# 23 August 2018: VRWM 5 V), so the ruling's own part had the microphone problem too. Read per conductor:
#   SPEAKER (HS1_SPK, HS2_SPK): U7's outputs swing about ground inside its charge-pump rails, HPVDD 1.9 V absolute
#     maximum (TI SLOS597B, 6.1), so +-1.9 V at most against a 5 V stand-off. PESD5V0S1BA stays (Nexperia v.6,
#     26 April 2024: bidirectional, VRWM 5 V, VBR 5.5 to 9.5 V, Cd 35 pF, VCL 14 V at 12 A, IEC 61000-4-2 30 kV contact).
#   PUSH TO TALK (PTT_HS1_n, PTT_HS2_n): idles at +3V3_D8 through its level stage's 10k (U1, 3.333 V at most).
#     PESD5V0S1BA stays.
#   MICROPHONE (HS1_MIC, HS2_MIC): with JP1 or JP2 closed and no headset, the conductor sits at +5V_D8 through R43 or
#     R44, 5.088 V nominal and 5.23 V at most (the rail's v_work): ABOVE the PESD5V0S1BA's 5 V stand-off in normal
#     service, the class rule CMP-001 exists for. The clamp moves to Nexperia PESD12VL1BA, same SOD-323 land, same
#     bidirectional construction, so the design basis of this block holds: VRWM 12 V, VBR 14.2 to 16.7 V at 5 mA,
#     IRM 50 nA max at 12 V, Cd 19 pF, VCL 20 V at 1 A and 37 V at 5 A, IEC 61000-4-2 30 kV contact and 15 kV air
#     (level 4, decision 34's envelope), Tamb -65 to 150 C (Nexperia PESD12VL1BA product data sheet, 14 April 2023).
#     LCSC C38558, PESD12VL1BA,115 (JLC API 2026-09-25T23:09Z: Nexperia, SOD-323, stock 6,960). The conductor's parts
#     behind the clamp are C44 (1 nF NP0), C41 into 4.7k and R43 to the rail, so the higher let-through lands on a
#     series resistor and a coupling capacitor, not on a pin.
part("D9",  "Device", "D_TVS", "PESD5V0S1BA bidirectional ESD clamp at the jack: headset 1 speaker", "SOD323", {"1": "GND", "2": "HS1_SPK"}, "C19224")
part("D10", "Device", "D_TVS", "PESD12VL1BA bidirectional ESD clamp at the jack: headset 1 microphone, above the electret bias", "SOD323", {"1": "GND", "2": "HS1_MIC"}, "C38558")
part("D11", "Device", "D_TVS", "PESD5V0S1BA bidirectional ESD clamp at the jack: headset 1 push to talk", "SOD323", {"1": "GND", "2": "PTT_HS1_n"}, "C19224")
part("D12", "Device", "D_TVS", "PESD5V0S1BA bidirectional ESD clamp at the jack: headset 2 speaker", "SOD323", {"1": "GND", "2": "HS2_SPK"}, "C19224")
part("D13", "Device", "D_TVS", "PESD12VL1BA bidirectional ESD clamp at the jack: headset 2 microphone, above the electret bias", "SOD323", {"1": "GND", "2": "HS2_MIC"}, "C38558")
part("D14", "Device", "D_TVS", "PESD5V0S1BA bidirectional ESD clamp at the jack: headset 2 push to talk", "SOD323", {"1": "GND", "2": "PTT_HS2_n"}, "C19224")
# PWR-001 (board D stream w3de, 27 September 2026, MESHSAT-1357): THE SIX HEADSET-SIDE LINES THE READING LEFT UNDECIDED
# ARE NODES AT THE WORKING VOLTAGES THIS BLOCK ALREADY STATES. PWR-001 fails closed on a net that carries the mark of a
# supply (a capacitor to ground, a jumper to such a net) when nothing read settles it, and it named HS1_MIC, HS2_MIC,
# HS1_BIAS_R, HS2_BIAS_R, PTT_HS1_n and PTT_HS2_n: a connector, a jumper and a clamp are not read. None supplies a part:
# the microphone lines carry the electret bias through R43 or R44 (2.2k) from +5V_D8 when JP1 or JP2 is closed, and the
# push-to-talk lines idle at +3V3_D8 through their level stage's 10k. Declaring each as a node settles it the way the rule
# says (FLANGE_NTC, below, is the same kind of declaration) and gives CMP-001 the working voltage the clamp comment above
# already derived: 5.23 V on the microphone side (+5V_D8's v_work, above the PESD5V0S1BA's stand-off, the reason D10 and
# D13 are PESD12VL1BA) and 3.333 V on the push-to-talk side (U1's TLV75533 at its +1 percent edge). Session decision under
# the owner's standing rule of 26 September 2026; reverse by a part on one of these lines that draws its supply from it.
for _hs in ("1", "2"):
    _intent.node("HS%s_MIC" % _hs, 5.23, "headset %s's microphone line at the jack: with JP%s closed and no headset it sits at "
                 "+5V_D8 through R%d (2.2k), 5.23 V at most (+5V_D8's v_work); an electret draws a few hundred microamps "
                 "through it and no part takes its supply here" % (_hs, _hs, 43 if _hs == "1" else 44), v_work=5.23)
    _intent.node("HS%s_BIAS_R" % _hs, 5.23, "the electret bias resistor's jumper side (R%d 2.2k from +5V_D8 to JP%s): at most "
                 "+5V_D8's 5.23 V v_work" % (43 if _hs == "1" else 44, _hs), v_work=5.23)
    _intent.node("PTT_HS%s_n" % _hs, 3.333, "headset %s's push-to-talk line: it idles at +3V3_D8 through its level stage's 10k "
                 "(R%d), 3.333 V at most (U1, TLV75533 at +1 percent), and the headset's switch pulls it to ground; U9 and the "
                 "level FET read it and take no supply from it" % (_hs, 68 if _hs == "1" else 70), v_work=3.333)
    # the level stage's far side: once the near side is a declared node the rule marks the FET's other channel net too
    # (the first re-take read X_PTT_HS1_n and X_PTT_HS2_n UNDECIDED), and it is the expander's input behind R69 or R71
    # (10k) to the harness +3V3, so it is declared at +3V3's 3.3 V the same way
    _intent.node("X_PTT_HS%s_n" % _hs, 3.3, "the push-to-talk level stage's far side (Q%s's drain), U16's P-port input pulled "
                 "to the harness +3V3 through R%d (10k): at most +3V3's declared 3.3 V; an input, no supply"
                 % ("4" if _hs == "1" else "5", 69 if _hs == "1" else 71), v_work=3.3)
# --- PTT and EMCON logic (74LVC1G, 3.3 V): KEY = (PTT headset 1 OR 2 OR software) AND TX_INHIBIT_n; the exciter keys on KEY; PA_KEY = KEY AND PA_EN drives the relay and the gate bias switch
# THE FITTED GATES, NAMED (re-review of round 6, 26 September 2026). The certification bought U9, U10, U12 and U14 as TECH
# PUBLIC 74LVC1G08GV (C19829591) and U11 and U13 as MDD 74LVC1G04GV (C53185133), while every figure this file quoted for them
# came from TI's sheets. The 1G08 lines are pinned to the part bought, and its maker's sheet is held (LCSC C19829591, six
# pages, image only, sha256 37d1f4d4: page 1, SOT-23-5 1 A, 2 B, 3 GND, 4 Y, 5 VCC and "power down protection"; page 2, VCC
# 1.65 to 5.5 V and an input transition of 10 ns/V at 3.3 V; page 3, over -40 to +125 C, VIL 0.8 V and VIH 2 V at VCC 3.0 to
# 3.6 V, VOL 0.1 V at 100 uA, 0.55 V at 24 mA at 25 C and 0.8 V over temperature, II +-5 uA, IOFF +-10 uA at VCC 0). No
# maker's sheet is held for the MDD part, and JLC gives none for C53185133, so U11 moves to TI SN74LVC1G04DBVR (C7827, JLC
# API 2026-09-26T11:55Z: Texas Instruments, SOT-23-5, stock 55,684; SCES214AF held: DBV 1 NC, 2 A, 3 GND, 4 Y, 5 VCC, Ioff
# +-10 uA, VIL 0.8 V at VCC 3 to 3.6 V) and U13 to the open-drain SN74LVC1G06DBVR (R4T-F9, at R88 and R89 above).
ic("U9", 5, "74LVC1G08 AND (1 A 2 B 3 GND 4 Y 5 VCC): both headset PTT lines idle high", "SOT235", {"1": "PTT_HS1_n", "2": "PTT_HS2_n", "3": "GND", "4": "PTT_HS_n", "5": "+3V3_D8"}, "C19829591")
ic("U10", 5, "74LVC1G08 AND: headsets AND software PTT (RTS)", "SOT235", {"1": "PTT_HS_n", "2": "PTT_SW_n", "3": "GND", "4": "PTT_ANY_n", "5": "+3V3_D8"}, "C19829591")
ic("U11", 5, "74LVC1G04 inverter (2 A 4 Y): PTT_ANY", "SOT235", {"1": "NC", "2": "PTT_ANY_n", "3": "GND", "4": "PTT_ANY", "5": "+3V3_D8"}, "C7827")
ic("U12", 5, "74LVC1G08 AND: KEY = PTT_ANY AND TX_INHIBIT_n (the panel's hardware EMCON)", "SOT235", {"1": "PTT_ANY", "2": "TX_INHIBIT_n", "3": "GND", "4": "KEY", "5": "+3V3_D8"}, "C19829591")
ic("U13", 5, "74LVC1G06 open-drain inverter (2 A 4 Y): KEY -> SA868 PTT (low = transmit; released = receive, held by R88 and R89)", "SOT235", {"1": "NC", "2": "KEY", "3": "GND", "4": "SA_PTT_n", "5": "+3V3_D8"}, "C840103")
ic("U14", 5, "74LVC1G08 AND: PA_KEY = KEY AND PA_EN (A22's PA rail state)", "SOT235", {"1": "KEY", "2": "PA_EN", "3": "GND", "4": "PA_KEY", "5": "+3V3_D8"}, "C19829591")
# one 100 nF per gate, tied to its gate as data so the decoupling gate measures the loop instead of trusting the schematic order
# (8 Sep 2026: the note below that these six gates carried no bypass capacitor was wrong, the capacitors existed since D8; what was
# missing was the intent entry, so no gate ever measured the distance on the chain that keys a 30 W transmitter)
for _i, _u in enumerate(("U9", "U10", "U11", "U12", "U13", "U14")): c("C%d" % (51 + _i), "100n", "+3V3_D8", "GND", bypass=(_u, "5"))
# NOTHING BUT LOGIC INPUTS AND PASSIVE PULLS ON KEY AND PA_KEY (RF-002, S-02 of the shared-tools review, round 4; owner
# D-05 and appendix 32.50 item 3, 26 September 2026). EMCON holds KEY low through U12 (TX_INHIBIT_n low) and so PA_KEY low
# through U14, but until today two pins that firmware sets shared KEY's conductor, and one shared PA_KEY's:
#   U16 IO0_3 (pin 7, the PCA9555) through the level shifter Q6 (gate on +3V3_D8, source on KEY, drain on X_KEY). With KEY
#   low Q6's channel is on, so U16's pin set as an output and driven high by a firmware error fights U12 through it;
#   board C's U3 pin 35 (an RP2040 GPIO) through R48's 100 Ohm, the harness and boards A and B (TR_APRS);
#   U16 IO0_4 (pin 8) on PA_KEY through Q7, the same shape, on the PA bias path (VGG through U15's EN, and the relay).
# No held figure bounds those fights under the 0.8 V at which U13 and U14 are guaranteed to read low (VIL at VCC 3 to 3.6 V:
# TI SCES295AB for U13, the TECH PUBLIC 74LVC1G08 sheet, page 3, for U14). U12 guarantees its VOL only up to 24 mA, and
# there 0.55 V at 25 C and 0.8 V over -40 to +125 C, which is the VIL itself (the same sheet); the PCA9555's P port
# sources about 43 mA at only 0.7 V under its supply (TI SCPS131J Figure 6-14, VCC 3.3 V, 25 C, typical) and is limited
# only by its 50 mA absolute maximum (6.1); Q6's channel is not bounded at this gate voltage (the JSCJ 2N7002, C8545,
# states RDS(on) only at VGS 5 V and 10 V); and the RP2040's drive into 100 Ohm is not bounded either. So a firmware error
# could lift KEY into the region where U13 may key the SA868 with EMCON asserted: the hardware gate was NOT proven, and
# tx_inhibit.py's RF-002 walk read FAIL for exactly these pins (Q6 to U16 pin 7, and R48 to C's U3 pin 35). It was not a
# tool artefact.
# THE REMEDY, taken by the session under the owner's standing rule of 26 September 2026 (the remedy the shared-tools
# review names for board D: read KEY back through a one-way buffer, drive the mirror through one): three 74LVC1G34 buffers,
# Diodes 74LVC1G34W5-7, proven on their own evidence: the maker's sheet, DS36108 Rev. 10-2, April 2021, held (sha256
# efd2d797: SOT25 pin 1 NC, 2 A, 3 GND, 4 Y, 5 VCC; inputs accept up to 5.5 V at any VCC; IOFF +-10 uA; II +-1 uA at -40 to
# 85 C and +-2 uA to 125 C; IOH and IOL 24 mA at VCC 3 V), and JLC's readback of C526347 as that part (JLC API
# 2026-09-26T12:01Z: Diodes Incorporated 74LVC1G34W5-7, SOT-25, stock 1,944). Its input transition limit is 10 ns/V at VCC
# 3.3 V (DS36108, recommended operating conditions), the limit that moved board C's EMCON buffer off this part in round 4,
# and it is met here: U18, U19 and U20 are driven only by the push-pull outputs of U12 and U14. The only slow edges on KEY
# and PA_KEY follow +3V3_D8 itself, its ramp (when a PTT is held with EMCON released) and its decay through R84 and R85.
# U18 runs on that same rail, so its input moves with its own supply; U19 and U20, on the always-on +3V3, feed only U16
# through 1k, so a slow edge there can at most glitch an expander read.
#   U18 on +3V3_D8 drives the mirror, PTT_MIR, then R48 to TR_APRS. A firmware pin on TR_APRS on A, B or C now meets U18's
#   output, never KEY, and TR_APRS still follows KEY whenever this board's logic is powered. R48 is 220 Ohm since the
#   re-review of round 6 (100 Ohm before): a pin driving TR_APRS against U18 draws at most 3.333 V / 216 Ohm = 15.4 mA,
#   inside the 24 mA U18 is rated for at VCC 3 V (DS36108), where 100 Ohm allowed 34 mA (UNI-ROYAL 0603WAF2200T5E, C22962,
#   JLC API 2026-09-26T11:55Z: BASIC, +-1 percent, +-100 ppm/C);
#   U19 and U20 (below, with the expander) read KEY and PA_KEY into U16 through 1k. Q6, Q7 and their pulls R72 to R75 are
#   gone, so on KEY there are now only U13, U14, U18 and U19 inputs, R49 to the transmit LED, R84 and a test point, and on
#   PA_KEY only U15's EN, U20's input, R50 to the LED, R52 to the relay FET's gate, R85 and a test point.
# AND KEY AND PA_KEY HOLD LOW WITH THEIR OWN GATES UNPOWERED (R4T-F9, same day). U12 and U14 run on +3V3_D8 from U1 while
# U15 and the relay run on +5V_D8, so a U1 whose output is at 0 V leaves both outputs in IOFF with the PA bias regulator
# powered. (Round 8, EMCON L4: U15 and the relay now run on U21's +5V_TX, which is off in that state; the pulls below
# stay, because they are what holds KEY and PA_KEY for the readback U19 and U20 and for the band U21 does not cover.)
# (With U1's output open and the rail back-fed to 1.65 V or more, U12 and U14 drive KEY and PA_KEY by their logic,
# low while EMCON is asserted; under 1.65 V no sheet specifies them: see R4T-F9 at R88 and R89.) At 0 V:
#   PA_KEY: R85 10k to ground, in parallel with R52 and R53 (101k), 9.25k at the resistors' high corner. The leakage it
#   holds is at most 12.1 uA (U14's output unpowered, +-10 uA, TECH PUBLIC IOFF; U20's input, +-2 uA at 125 C (DS36108);
#   Q2's gate, +-80 nA (JSCJ 2N7002); U15's EN, 10 nA typical (TI SBVS351D 5.5, no maximum)), 0.11 V, under the 0.3 V at which U15 is
#   guaranteed OFF (VEN(LO), SBVS351D 5.5). With only R52 and R53 the same leakage could reach 1.2 V, above its 1.0 V
#   VEN(HI), and before today R74 pulled PA_KEY toward the dead rail itself;
#   KEY: R84 10k to ground. At most 42 uA (unpowered at +-10 uA each: U12's output and U14's input, TECH PUBLIC IOFF; U13's
#   input, SCES295AB Ioff; U18's input, DS36108 IOFF; and U19's powered input, +-2 uA), 0.43 V, under U19's 0.8 V VIL, so U16
#   reads "not keyed", which with U13 in Ioff and R88 and R89 on SA_PTT_n is true. With the harness +3V3 down as well,
#   U19's input is in IOFF (+-10 uA, DS36108) instead: 50 uA, 0.51 V, still under 0.8 V, and U19 and U16 are then
#   unpowered and read nothing. The two pull-downs ask U12 and U14 for 0.34 mA each when they drive high.
ic("U18", 5, "74LVC1G34 buffer (1 NC 2 A 3 GND 4 Y 5 VCC): KEY -> PTT_MIR, the one-way driver of the PTT mirror TR_APRS", "SOT235",
   {"1": "NC", "2": "KEY", "3": "GND", "4": "PTT_MIR", "5": "+3V3_D8"}, "C526347")
c("C66", "100n", "+3V3_D8", "GND", bypass=("U18", "5"))
r("R48", "220", "PTT_MIR", "TR_APRS", lcsc="C22962")   # the PTT mirror to A22 (100k pull-down there) and C's TX lamp, through U18; 220 Ohm bounds a fight to 15.4 mA
r("R84", "10k", "KEY", "GND", lcsc="C25804"); r("R85", "10k", "PA_KEY", "GND", lcsc="C25804")
led("LED4", "red transmit", "LED_TX_A", "GND"); r("R49", "1k", "KEY", "LED_TX_A"); led("LED5", "yellow PA keyed", "LED_PA_A", "GND"); r("R50", "1k", "PA_KEY", "LED_PA_A")
led("LED6", "green receive (AUDIO_ON low)", "LED_RX_A", "SA_AUDIO_ON_n"); r("R51", "2.2k", "+3V3_D8", "LED_RX_A")
# --- T/R relay G6K-2F-Y (5 V coil; top view pins 8 7 6 5 over 1 2 3 4: coil 1 (+) 8 (-), pole 3-2-4 and 6-7-5 with 2 and 7 the rest contacts):
#     rest: exciter ANT (3) -> 2 = RX node = 7 -> 6 = antenna SMA (receive, and the exciter's 2 W direct when the PA is off); keyed with the PA: 3 -> 4 = pad -> PA drive, PA output -> LPF -> 5 -> 6
part("K1", "Relay", "G6K-2", "Omron G6K-2F-Y 5 VDC DPDT signal relay, T/R", "RELAY", {"1": "+5V_TX", "8": "RLY_K", "3": "RF_SA", "2": "RF_RX", "4": "RF_PAD_IN", "6": "RF_ANT", "7": "RF_RX", "5": "RF_LPF_OUT"})
nfet("Q2", "RLY_DRV", "GND", "RLY_K", "2N7002 relay coil"); r("R52", "1k", "PA_KEY", "RLY_DRV"); r("R53", "100k", "RLY_DRV", "GND")
# D2 CARRIES ITS ORDER CODE (S-76 and EQ-21's class, stream w4dp, 27 September 2026, MESHSAT-1357). It was a bare "1N4148W"
# that only lcsc_fill.py's MAP turned into a code at the JLC BOM stage, so the schematic named a class and no maker. The code is
# the one that fill already chose and JLC-CERTIFIED.tsv certified on 26 September 2026 (row "1N4148W coil flyback", D_SOD-123):
# LCSC C81598, 1N4148W by SEMTECH ELECTRONICS LTD. (LCSC's brand "ST(Semtech)", not Semtech Corporation), SOD-123, a JLC basic
# part; JLC API 2026-09-27: stock 5,220,610, "150mA 1A 1V@50mA 1uA@75V 400mW 4ns 75V". The maker's sheet as LCSC serves it is
# filed as v2/vendor/power/st-semtech-1n4148w-c81598.pdf (Rev 05, 20/09/2016, sha256 54de8e40, the file grade-sources.yaml
# already read for its 150 C junction). PINS PER THAT SHEET'S PINNING TABLE: 1 cathode, 2 anode (SOD-123, marking W1), which is
# KiCad's Diode:1N4148W (1 K, 2 A) and its D_SOD-123 land (pad 1 the cathode band): the cathode on +5V_TX and the anode on the
# coil's switched end, the flyback orientation. Ratings from the same sheet: VR 75 V, IF(AV) 150 mA, IFSM 1 A for 1 ms,
# VF at most 0.855 V at 10 mA, 1.0 V at 50 mA and 1.25 V at 150 mA (25 C), trr at most 4 ns. The value text is unchanged, so the
# certified row still matches (Comment, Footprint) and no pin, net or land moves: the netlist changes by D2's LCSC field alone.
part("D2", "Diode", "1N4148W", "1N4148W coil flyback", "SOD123", {"1": "+5V_TX", "2": "RLY_K"}, "C81598"); c("C57", "100n", "+5V_TX", "GND")   # the coil, its flyback and its capacitor on U21's +5V_TX since round 8 (EMCON L4)
# PWR-001 (S-76, stream w4dp, 27 September 2026, MESHSAT-1357): RLY_K WAS THE BOARD'S LAST UNDECIDED NET. It is the relay coil's
# switched low end (K1 pin 8, Q2's drain, D2's anode): M3 joins it to +5V_TX through D2 and M4 reads Q2 sinking it to ground,
# and nothing on it takes a supply, so it is declared a node the way the rule's text says (a switch's current path), as the
# stream w3de declared the headset lines. Its voltage: at rest it sits at +5V_TX through the coil, 5.23 V at most (+5V_TX's
# v_work); with Q2 on it is at Q2's drop; at release the coil's current commutates into D2 and the node rises to +5V_TX plus
# D2's forward drop. That current is the coil's own: 21.1 mA at 5 V into 237 ohm (Omron G6K, Cat. No. K106-E1-11, the 5 VDC
# coil row), whose resistance is stated at 23 C +-10 percent; at 5.23 V, -10 percent and the copper's fall to -20 C (about 17
# percent over 43 K, the copper coefficient and not an Omron figure) it is at most about 30 mA. D2's sheet gives VF at most
# 1.0 V at 50 mA and 1.25 V at 150 mA at 25 C and no temperature coefficient, so the node is declared at 5.23 + 1.25 = 6.5 V:
# the 150 mA row bounds a 30 mA current with room for the cold end a silicon junction's drop rises into. Parts on it: Q2
# (2N7002, VDS 60 V), D2 (VR 75 V, reverse-biased at most 5.23 V with Q2 on) and the coil. Session decision under the owner's
# standing rule of 26 September 2026 (W4DP-D2 in drafts/w4dp/); reverse by a part on RLY_K that draws its supply from it.
_intent.node("RLY_K", 6.5, "the T/R relay coil's switched low end (K1 pin 8, Q2 drain, D2 anode): at rest +5V_TX through the "
             "coil (5.23 V at most, +5V_TX's v_work), at release +5V_TX plus D2's forward drop while the coil's current "
             "(at most about 30 mA: Omron G6K 5 VDC coil, 21.1 mA and 237 ohm +-10 percent at 23 C, colder copper lower) "
             "commutates into D2, whose maker states VF at most 1.25 V at 150 mA (SEMTECH ELECTRONICS 1N4148W Rev 05, "
             "LCSC C81598); no part takes its supply here", v_work=5.23)
r("R54", "27 1% 2010", "RF_PAD_IN", "RF_PAD_M", "R2010"); r("R55", "36 1% 2010", "RF_PAD_M", "GND", "R2010"); r("R56", "27 1% 2010", "RF_PAD_M", "RF_DRV", "R2010")   # 10 dB T-pad, 0.5 W in, 50 mW to the PA
part("J_PAIN", "Connector", "Conn_Coaxial", "U.FL socket: PA drive (coax to the RA30H1317M1 input on the plate)", "UFL", {"1": "RF_DRV", "2": "GND"}, "C88373")
part("J_PAOUT", "Connector", "Conn_Coaxial", "SMA jack: PA output (coax from the RA30H1317M1 output on the plate)", "SMA", {"1": "RF_PAOUT", "2": "GND"}, "C3174425")
# THE VOLTAGE ON THE FILTER, DECLARED (16 September 2026, rule CMP-001). Three of this board's nets carry the
# transmitter's whole output and nothing said what that is, so `derate.py` reported them as UNDECLARED and
# judged no part on any of them: it is the one place on the set where a part meets a voltage above 54 V.
# 30 W into a matched 50 ohm load is 38.7 V RMS and 54.8 V peak. Into a MISMATCH it is higher: an open or a
# short at the antenna doubles the standing-wave voltage to about 110 V peak, which is the case the filter's
# capacitors are chosen for, and they are 500 V NP0 parts for that reason. The declared peak is the mismatch
# case, because a field kit's antenna port is exactly where a mismatch happens.
for _rfn in ("RF_PAOUT", "RF_LPF_M", "RF_LPF_OUT"):
    _intent.node(_rfn, 110.0, "the 30 W transmitter's output: 54.8 V peak into a matched 50 ohm load, and about "
                 "110 V peak at the voltage maximum of a standing wave if the antenna port is open or shorted")
_intent.node("GND", 0.0, "the board's reference, so a part between a live net and ground is judged against the "
             "live net rather than reported as sitting on an undeclared one")
# L1 and L2 leave the 1812 land. The IMC1812EB68NK they were drawn as is rated 450 mA and the
# 30 W PA puts about 775 mA RMS through this filter (sqrt(30/50) into a matched load), so the
# part was under-rated for its own job independently of being out of stock, and every other
# 68 nH in 1812 is the same 450 mA family. The Murata LQW2BAN68NG00L is 1.2 A and 2 percent,
# which a fifth-order corner wants, at 120 mW of dissipation in its 200 mOhm. Confirm the
# current under a mismatched antenna when MESHSAT-818 simulates this filter.
c("C58", "22p 500V NP0 1206", "RF_PAOUT", "GND", "C1206"); part("L1", "Device", "L", "68nH 0805 (LPF, 145 MHz 5th order; values to be verified in MESHSAT-818)", "L0805", {"1": "RF_PAOUT", "2": "RF_LPF_M"})
c("C59", "39p 500V NP0 1206", "RF_LPF_M", "GND", "C1206"); part("L2", "Device", "L", "68nH 0805 (LPF)", "L0805", {"1": "RF_LPF_M", "2": "RF_LPF_OUT"}); c("C60", "22p 500V NP0 1206", "RF_LPF_OUT", "GND", "C1206")
part("J_ANT", "Connector", "Conn_Coaxial", "SMA jack: antenna pigtail to A22's VHF jack J_RF1", "SMA", {"1": "RF_ANT", "2": "GND"}, "C3174425")
# PWR-001 (board D stream w3de, 27 September 2026, MESHSAT-1357): RF_ANT, the antenna side of the T/R relay K1, was left
# UNDECIDED (a lead: J_ANT with ground beside it, and a relay nothing reads). It carries the transmitter's output whenever
# K1 is in transmit, from RF_LPF_OUT through K1's contact, so it is declared at the same 110 V peak as the three filter
# nets above and for the same reason (the standing-wave maximum at an open or shorted antenna port). Session decision
# under the owner's standing rule of 26 September 2026; reverse with the filter nets' figure if MESHSAT-818 changes it.
_intent.node("RF_ANT", 110.0, "the antenna side of the T/R relay K1: in transmit it carries the 30 W output from RF_LPF_OUT "
             "through K1's contact, 54.8 V peak into a matched 50 ohm load and about 110 V peak at the voltage maximum of a "
             "standing wave if the antenna port is open or shorted (the declaration of RF_PAOUT, RF_LPF_M and RF_LPF_OUT)")
# W2 F-PR-02, 26 September 2026: THE PA GATE BIAS IS REGULATED BELOW 5 V, NOT SWITCHED FROM THE 5 V RAIL. U15 was a
# TPS22810 load switch putting +5V_D8 on VGG: 5.088 V nominal, 5.23 V at most. The RA30H1317M1 sheet (Mitsubishi,
# October 2011) rates VDD 17 V and Pout 45 W only with "VGG<5V", rates VGG 6 V only with "VDD<12.5V", and says the
# nominal output "becomes available at 4V (typical) and 5V (maximum)"; this PA runs on A's 13.8 V rail, so at the old
# VGG both maxima sat outside their own stated conditions and the drain current was set by nothing the sheet
# characterises. U15 is now a TLV75801P adjustable LDO (TI SBVS351D) in the WSON-6 DRV package, TI drawing
# DRV0006A (4222173/C), the SAME land the TPS22810DRV sat on (its sheet cites the same drawing), so the footprint
# stays and four pad nets move: pin 1 OUT and pin 6 IN keep VGG_SW and +5V_D8, pin 2 NC becomes FB, pin 3 CT becomes
# GND, pin 4 GND becomes EN (PA_KEY), pin 5 EN becomes DNC; the exposed pad stays GND. EN from PA_KEY keeps the key
# discipline (VEN(HI) 1.0 V, VEN 6.0 V max, 74LVC1G08 output at 3.3 V), and the part's active discharge (95 Ohm)
# pulls VGG to ground when PA_KEY falls, where the TPS22810 needed its QOD pin. R82 71.5k over R83 10.0k set
# 0.55 x (1 + 7.15) = 4.48 V nominal.
# THE VGG BAND WITH EVERY TERM (review fix-up of round 4, 26 September 2026; a first draft counted the reference and
# the resistors at 25 C only, 4.36 to 4.61 V): VFB +-1 percent at -40 to 85 C TJ, R82 and R83 +-1 percent and
# +-100 ppm/C (UNI-ROYAL 0603WAF, JLC readback) over 65 K, so +-1.65 percent each, line regulation 7.5 mV maximum,
# IFB 0.1 uA through R82 (7.3 mV), load regulation negligible at the gate's 1 mA (IGG, RA30H1317M1): 4.30 to 4.68 V.
# The top is 0.32 V under the 5 V at which the sheet's VDD 17 V and Pout 45 W ratings hold, at every corner. Long-term
# drift of R82 and R83 is not in that band, because no UNI-ROYAL 0603WAF sheet is held; the 0.32 V absorbs a further
# 7.9 percent in the divider's ratio (about 4 percent on each resistor, in opposite directions) before 5 V. What the
# sheet does NOT promise is nominal output at this VGG from a maximum-case module: it says nominal output becomes
# available at 4 V typical and 5 V maximum, so a module at its 5 V corner may not reach nominal output at 4.30 to
# 4.68 V. That is a bench measurement, not a claim, and it is OWED to TEST-PLAN.md, which does not carry it yet: the
# drain current and Pout at 13.8 V into a dummy load at this VGG, with R82 as the trim (still under 5 V at every
# corner) if the bench wants more.
# THE KEY-UP AND KEY-DOWN ORDER IS NOT BOUNDED BY ANY PUBLISHED LIMIT (re-review of round 4, 26 September 2026; the
# fix-up had said VGG leads the drive at key-up and that the discharge beats K1's release at key-down). PA_KEY starts
# three things at once: U15's start-up, tSTR 500 us TYPICAL with no limit (SBVS351D 5.5; the TPS22810 with its
# 4.7 nF CT took about 1 ms); K1's operate time, 3 ms MAXIMUM with no minimum (Omron G6K, Cat. No. K106-E1-11), the
# exciter's drive reaching the PA input only through K1's contact (RF_SA to RF_PAD_IN); and, through KEY, the
# SA868's own transmit, whose on and off times its v1.3 sheet does not give. On key-down VGG falls through U15's
# pulldown, 95 Ohm TYPICAL with no limit (SBVS351D 5.5; tau by its equation 1, 6.3.2), into C62: tau about 0.2 ms
# with the 2.2 uF nominal and less at bias, against K1's release, 3 ms maximum with no minimum. At each edge one
# side has only a typical figure and the other only a maximum, so neither order follows from the sheets, and the
# first fix-up's two claims are withdrawn. The key-down figure also holds only while
# C62 is the one capacitance on VGG: the RA30H1317M1 sheet's test fixture puts a 4700 pF chip capacitor close to
# the module and 22 uF or more on the gate supply ("Oscillation", and C1 of its test block diagram), and the VGG
# lead carries none today. If W3-F25 (the board A to PA contract) adds that decoupling, tau becomes 95 Ohm x 24.2
# uF, about 2.3 ms, comparable to K1's release; the total stays inside the TLV758P's 1 to 220 uF output range. The
# held RA30H1317M1 sheet states no bias or drive sequence of its own. The scope capture of VGG, K1's contact and
# the exciter's RF on key-up and key-down is a bench measurement OWED to TEST-PLAN.md with the PA item above.
# TLV75801PDRVR, LCSC C2876308 (JLC API 2026-09-25T23:13Z: TI, WSON-6-EP 2x2, -40 to 125 C TJ, stock 10,498).
# C61 was the TPS22810's 4.7 nF slew capacitor on CT, a net that no longer exists; it becomes the LDO's 1 uF input
# capacitor (SBVS351D 5.3, CIN 1 uF), and C62 grows from 100 nF to the 1 uF minimum output capacitor (0.47 uF after
# derating): 2.2 uF 16 V X5R, Samsung CL10A225KO8NNNC, C23630. Its DC-bias retention is NOT a held figure: Samsung's
# data page for CL10A225KO8NNN (read 26 September 2026) says "Graphs for the item are not supported", so the "about
# 1.1 uF at 4.5 V" of the first draft was an estimate. What is required is 0.47 uF, 21 percent of 2.2 uF, at 4.68 V,
# 29 percent of the part's rating; the effective capacitance at bias is a bench measurement OWED to TEST-PLAN.md,
# which does not carry it yet.
ic("U15", 7, "TLV75801PDRVR adjustable LDO, PA gate bias VGG 4.48 V while PA_KEY is high (1 OUT 2 FB 3 GND 4 EN 5 DNC 6 IN 7 pad)", "WSON6",
   {"1": "VGG_SW", "2": "VGG_FB", "3": "GND", "4": "PA_KEY", "5": "NC", "6": "+5V_TX", "7": "GND"}, "C2876308")   # IN on U21's +5V_TX since round 8 (EMCON L4)
c("C61", "1u", "+5V_TX", "GND", lcsc="C15849"); c("C62", "2.2u 16V X5R", "VGG_SW", "GND", lcsc="C23630")
r("R82", "71.5k 1%", "VGG_SW", "VGG_FB", lcsc="C23103"); r("R83", "10.0k 1%", "VGG_FB", "GND", lcsc="C25804")   # UNI-ROYAL 0603WAF7152T5E and 0603WAF1002T5E, JLC API 2026-09-25T23:19Z
# VGG_SW DECLARED (26 September 2026): C62 now states a rating (16 V), and a rated part on a net with no declared
# voltage is a gap derate.py reports rather than a pass; the round-4 box run read "UNDECLARED nets: VGG_SW".
_intent.node("VGG_SW", 4.68, "the PA gate bias from U15, a TLV75801P set by R82 71.5k over R83 10.0k: 0.55 V x "
             "(1 + 7.15) = 4.48 V nominal, 4.30 to 4.68 V with every term (TI SBVS351D 5.5: VFB +-1 percent at -40 "
             "to 85 C, line regulation 7.5 mV, IFB 0.1 uA; both 1 percent 100 ppm/C resistors over 65 K); "
             "0 V while PA_KEY is low (the LDO's active discharge)")
# J_VGG's CODE (round 8, the parts re-take): C5251182 is JST B2B-PH-K-S-GW, a suffix the held JST PH catalogue
# (v2/vendor/connectors/jst-ph-catalogue.pdf) does not list, so it is a mismatch under owner condition 1. The catalogue's
# header table lists B2B-PH-K-S, and C131337 is B2B-PH-K-S(LF)(SN), JST (JLC API 2026-09-26T21:05Z: stock 86,615), the code
# the reconciliation recommends (SOURCES.yaml jst-ph-headers.update_45bde541).
part("J_VGG", "Connector_Generic", "Conn_01x02", "JST-PH 1x2 socket: PA gate bias, VGG GND (the lead runs to the RA30H1317M1 VGG pin)", "PH2", {"1": "VGG_SW", "2": "GND"}, "C131337")
# --- expander PCA9555 0x26 on the kit bus (harness +3V3) with 2N7002 level stages into the mezzanine's 3.3 V domain
part("U16", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x26: COS, PTT states, KEY, PA_KEY in; exciter PD, amplifier EN, codec mute out; eight spares", "TSSOP24", {
 "1": "EXP_INT", "2": "+3V3", "3": "+3V3", "21": "GND", "22": "SCL", "23": "SDA", "24": "+3V3", "12": "GND",
 "4": "X_COS_n", "5": "X_PTT_HS1_n", "6": "X_PTT_HS2_n", "7": "X_KEY", "8": "X_PA_KEY", "9": "X_SA_PD", "10": "X_AMP_EN", "11": "X_MMUTE",
 "13": "EXP_SPARE1", "14": "EXP_SPARE2", "15": "EXP_SPARE3", "16": "EXP_SPARE4", "17": "EXP_SPARE5", "18": "EXP_SPARE6", "19": "EXP_SPARE7", "20": "EXP_SPARE8"})
c("C63", "100n", "+3V3", "GND")
# The stages keep their numbers (Q3 to Q5, Q8, Q9 with R66 to R71 and R76 to R79) so the placement's ranges still name
# them; stages 6 and 7 (Q6 on KEY, Q7 on PA_KEY) became the buffers U19 and U20 below (RF-002, 26 September 2026).
for i, far, near in ((3, "X_COS_n", "SA_AUDIO_ON_n"), (4, "X_PTT_HS1_n", "PTT_HS1_n"), (5, "X_PTT_HS2_n", "PTT_HS2_n"), (8, "X_SA_PD", "SA_PD"), (9, "X_AMP_EN", "AMP_EN")):
    level("Q%d" % i, "R%d" % (60 + 2 * i), far, near, "+3V3_D8", "+3V3", "R%d" % (61 + 2 * i))
# KEY AND PA_KEY ARE READ BACK ONE WAY (RF-002, see the PTT logic above). U19 and U20 run on the harness +3V3, U16's own
# supply, so the read is true in every power state: with +3V3_D8 down, KEY and PA_KEY sit on R84 and R85 and U16 reads
# "not keyed", where Q6 and Q7 had let X_KEY and X_PA_KEY float up to "keyed" on R73 and R75. KEY and PA_KEY at up to
# 3.333 V into a buffer on a lower +3V3 are inside DS36108's 5.5 V input range, and with +3V3 down the inputs are in IOFF.
# R86 and R87 (1k) are for a firmware error that makes IO0_3 or IO0_4 an output: it then fights only a buffer, at most
# 3.7 mA, inside both parts' 50 mA ratings (DS36108; SCPS131J 6.1). Read levels on guaranteed figures: low, U19's VOL 0.1 V
# at 100 uA plus U16's own pull-up (at most 100 uA, IIL, SCPS131J 6.5) across 1k, 0.2 V against U16's VIL of 0.3 x VCC
# (0.9 V at 3.0 V); high, the pull-up only helps, against VIH 0.7 x VCC (SCPS131J 6.3).
# DRAWING ONLY: R86 and R87 are written U16 side first, and R48 is listed with the harness in SECTIONS, so schlayout hangs
# them on U16's and J_HARN1's lanes. Hung on the buffers' output lanes, schlayout's decoupling row (placed beside the part
# without an occupancy check) put its rail bus through the series part's far label, and its own verify refused the drawing
# on the first box run of 26 September 2026, and again when that drawing order was restored on the re-review's generator
# for the record ("schlayout verify: SHORT ['+3V3_D8', 'TR_APRS']: pins [('R48', '2'), ('C66', '1')]" and "SHORT ['+3V3',
# 'X_PA_KEY']: pins [('U16', '8'), ('R87', '2'), ('C68', '1')]"). The pin-to-net map is the same either way; a resistor's
# pin order changes nothing electrical.
ic("U19", 5, "74LVC1G34 buffer (1 NC 2 A 3 GND 4 Y 5 VCC): KEY read back into U16 IO0_3, one way (VCC the harness +3V3)", "SOT235",
   {"1": "NC", "2": "KEY", "3": "GND", "4": "X_KEY_B", "5": "+3V3"}, "C526347")
c("C67", "100n", "+3V3", "GND", bypass=("U19", "5")); r("R86", "1k", "X_KEY", "X_KEY_B", lcsc="C21190")
ic("U20", 5, "74LVC1G34 buffer (1 NC 2 A 3 GND 4 Y 5 VCC): PA_KEY read back into U16 IO0_4, one way (VCC the harness +3V3)", "SOT235",
   {"1": "NC", "2": "PA_KEY", "3": "GND", "4": "X_PA_KEY_B", "5": "+3V3"}, "C526347")
c("C68", "100n", "+3V3", "GND", bypass=("U20", "5")); r("R87", "1k", "X_PA_KEY", "X_PA_KEY_B", lcsc="C21190")
# PWR-F15: THE POWER AMPLIFIER'S FLANGE TEMPERATURE (round 8 of MESHSAT-1357, 26 September 2026;
# v2/docs/feasibility/POWER-THERMAL.md sections 7.2 and 9.3 and its PWR-F15 row). The key-down rules K2 (key on only with
# the flange at most +75 C) and C4 (unkey at +85 C) read a temperature no board carried. Taken by the session under the
# owner's standing rule of 26 September 2026:
#   THE SENSOR: a Semitec 103AT-2 NTC (10.0 kOhm +-1 percent at 25 C, B25/85 3435 K +-1 percent, -50 to +110 C,
#   dissipation factor about 2.0 mW/C, thermal time constant about 15 s, rated 10 mW at 25 C: Semitec catalogue 129M, AT
#   thermistor table, held at v2/vendor/battery/semitec-catalog-129M.pdf), the part board P already uses for its cells,
#   bonded to the module's flange beside a mounting screw and brought to J_FLANGE on a two-wire lead. Its range covers
#   the module's -30 to +100 C case rating (RA30H1317M1 sheet, October 2011, Maximum ratings). It is bench-fitted on the
#   lead and is not a BOM line of this board. The flange is the module's RF ground; the bead's epoxy insulates it.
#   J_FLANGE is a JST XH socket, not the PH of J_VGG beside it, so the two leads are not interchangeable (2.5 against
#   2.0 mm pitch, JST XH and PH catalogues): the gate bias lead on this socket would put the divider's 3.3 V on the PA's
#   gate, and the NTC on J_VGG would take 4.48 V. B2B-XH-A is in the held XH catalogue's header table
#   (v2/vendor/connectors/jst-xh-catalogue.pdf); C158012 is B2B-XH-A(LF)(SN), JST, the code board E's J_TAMP carries
#   (JLC API 2026-09-26T21:18Z: stock 363,732).
#   THE READER, on the kit bus, as the page asks ("read by the panel and the bridge"): U22, a TI ADS1115 (SBAS444E, May
#   2009, revised December 2024; filed as a draft this round): 16 bits, VDD 2.0 to 5.5 V and -40 to +125 C (5.3), on the
#   harness +3V3 beside the expander U16, so it answers whenever the bus is up, whatever +3V3_D8 does. ADDR to GND sets
#   1001000b, 0x48 (7.5.1.1, Table 7-2). The kit bus holds 0x10, 0x20 to 0x26, 0x28, 0x30, 0x34 to 0x36, 0x40, 0x41,
#   0x44 to 0x47, 0x49, 0x5F, 0x60, 0x68 and 0x6B (ARCHITECTURE.md 5.5, read from the netlists), so 0x48 is free; 0x49
#   (ADDR to VDD) would collide with board B's TMP117. It answers the general call reset, 0x06 (7.5.1.2). LCSC C37593,
#   ADS1115IDGSR (JLC API 2026-09-26T21:05Z: TI, VSSOP-10, stock 33,624).
#   RATIOMETRIC: R92 (2.0k 1 percent) runs from +3V3 over the NTC to GND. AIN0 reads the divider through R93 (1k) with C73
#   (100 nF), AIN1 reads +3V3 itself through R94 (1k) with C74 (100 nF), and firmware takes Rntc = R92 x N0 / (N1 - N0):
#   the supply and the ADC's gain drop out (the same PGA on both, FSR +-4.096 V, both inputs at or under VDD as 5.3 asks).
#   The first-order RC is SBAS444E 9.1.5's own advice ("a cutoff frequency set at the output data rate or 10x higher"):
#   (1k plus the divider's 0.84 to 1.67k) x 100 nF gives 0.6 to 0.9 kHz, between 1 and 10 times the 128 SPS default,
#   and the 1k keeps an overdriven input under the 10 mA of 5.1. C72 (1 nF NP0) at J_FLANGE is an RF bypass on a lead
#   that runs beside a 30 W transmitter. AIN2 and AIN3 go to GND and ALERT/RDY stays unconnected, as 9.1.4 allows.
#   THE NUMBERS: the NTC is 1.912k at +75 C and 1.451k at +85 C (the B equation at 3435 K), where the divider moves 23
#   and 22 mV/K, about 175 codes per kelvin at the 125 uV step of FSR +-4.096 V. The worst-case error at +85 C: R92 at
#   +-1.65 percent over 65 K, 0.6 K; R25 +-1 percent, 0.4 K; B +-1 percent, 0.7 K; the offset of 5.5 (3 LSB), under
#   0.1 K; about 1.7 K in all, inside the 10 K between K2 and C4 and the 15 K between C4 and the module's +100 C.
#   Self-heating: at most 1.36 mW in the NTC (when it equals R92), 0.7 K in still air at 2.0 mW/C and less on metal. The
#   bead's offset from the flange is read against a thermocouple at bring-up (PWR-F15's own bench item).
#   A FAILED LEAD IS READABLE: open, N0 equals N1 (the NTC is 248k at -40 C, a ratio of 0.992); shorted to the plate, N0
#   falls under a ratio of 0.22 (the NTC is 554 Ohm at +125 C). The firmware treats both as a failed sensor and keeps
#   the PA from keying (K2); that rule is the W5 contract's to write.
#   NO HARDWARE UNKEY, derived from the page: POWER-THERMAL.md 9.3 makes C4 a firmware guard ("C4, the in-key guard
#   (new, firmware)"), K1 and K2 are firmware too, and the section closes "These are firmware contract items for the
#   panel and bridge (W5 contract), not board changes". The page asks for no path that works without firmware, so none
#   is drawn. What that leaves is recorded, not closed: with the controller hung and a PTT held, nothing limits a
#   key-down's length or the flange's temperature (a finding drafted for the POWER-THERMAL writer this round).
part("J_FLANGE", "Connector_Generic", "Conn_01x02", "JST-XH 1x2 socket: power amplifier flange NTC lead (Semitec 103AT-2 on the flange, bench-fitted): NTC GND", "XH2", {"1": "FLANGE_NTC", "2": "GND"}, "C158012")
r("R92", "2k 1%", "+3V3", "FLANGE_NTC", lcsc="C22975"); c("C72", "1n NP0", "FLANGE_NTC", "GND", "C0402", lcsc="C113780")
r("R93", "1k", "FLANGE_NTC", "FLANGE_AIN0", lcsc="C21190"); c("C73", "100n", "FLANGE_AIN0", "GND", lcsc="C14663")
r("R94", "1k", "+3V3", "FLANGE_REF", lcsc="C21190"); c("C74", "100n", "FLANGE_REF", "GND", lcsc="C14663")
# FLANGE_NTC is a sense node, not a power conductor (power_path asks, since R92 is declared a load of +3V3 above)
_intent.node("FLANGE_NTC", 3.3, "the NTC divider's tap: at most the harness +3V3 (declared 3.3 V) with the flange lead open, "
             "and at most 1.1 mA through R92 into the NTC; read by U22's AIN0 through R93")
# PWR-001 (board D stream w3de, 27 September 2026, MESHSAT-1357): the ADC's two filtered inputs were left UNDECIDED (C73
# and C74 to ground, and U22 has no held pin row). They are the same kind of sense node as FLANGE_NTC: FLANGE_AIN0 is the
# NTC tap behind R93, FLANGE_REF is +3V3 behind R94, each into an ADS1115 analog input with its 100 nF, and neither
# supplies a part. Session decision under the owner's standing rule of 26 September 2026, as FLANGE_NTC's.
_intent.node("FLANGE_AIN0", 3.3, "the NTC tap behind R93 (1k) and C73 into U22's AIN0: at most FLANGE_NTC's 3.3 V (the harness "
             "+3V3 with the flange lead open); an analog input, no supply")
_intent.node("FLANGE_REF", 3.3, "the harness +3V3 behind R94 (1k) and C74 into U22's AIN1, the ratiometric reference reading: at "
             "most +3V3's declared 3.3 V; an analog input, no supply")
ic("U22", 10, "ADS1115IDGSR 16-bit ADC at 0x48 (1 ADDR 2 ALERT/RDY 3 GND 4 AIN0 5 AIN1 6 AIN2 7 AIN3 8 VDD 9 SDA 10 SCL): the flange NTC over +3V3, ratiometric", "VSSOP10",
   {"1": "GND", "2": "NC", "3": "GND", "4": "FLANGE_AIN0", "5": "FLANGE_REF", "6": "GND", "7": "GND", "8": "+3V3", "9": "SDA", "10": "SCL"}, "C37593")
c("C75", "100n", "+3V3", "GND", lcsc="C14663")   # U22's VDD: "Connect a 0.1uF, power-supply decoupling capacitor to GND" (SBAS444E, pin table)
# TP25 on +3V4_HUB (review fix-up of round 4, 26 September 2026): the hub's own supply is to be measured at the
# bench, a measurement OWED to TEST-PLAN.md and not in it yet, so the rail gets a pad of its own. Appended, so TP1
# to TP24 keep their numbers and their seats in gen_pcb_d3.py. TP26 on FLANGE_NTC and TP27 on +5V_TX (round 8) are
# appended the same way: the flange bead's offset against a thermocouple (PWR-F15) and the switched rail's level while
# +3V3_D8 is held in its bands (EMCON.md E-11) are bench readings owed to TEST-PLAN.md.
for i, net in enumerate(("AF_OUT", "MIC_SUM", "KEY", "PA_KEY", "+3V3_D8", "+5V_D8", "VGG_SW", "RX_MIX", "ZEROIZE_HW", "AB_SPARE", "SA_TXD", "SA_RXD", "PTT_SW_n", "SA_PD", "TX_INHIBIT_n", "PA_EN") + tuple("EXP_SPARE%d" % k for k in range(1, 9)) + ("+3V4_HUB", "FLANGE_NTC", "+5V_TX"), 1):
    part("TP%d" % i, "Connector", "TestPoint", net, "TP", {"1": net})
# +3V4_HUB joined the flags with the hub LDO U17 (W6-F5, 26 September 2026)
for i, net in enumerate(("+5V_D8", "+5V_SA", "+3V3_D8", "+3V3", "GND", "PCM_VDD", "SAU_3V3", "+3V4_HUB"), 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
# ----------------------------------------------------------------- emit (as B15)
POWER = {"GND": ("power", "GND")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
byref = {p["ref"]: p for p in P}

def refs_matching(pred): return [p["ref"] for p in P if pred(p["ref"])]
SECTIONS = [("HARNESS, 5 V ENTRY, 3.3 V LDO, EXCITER SUPPLY AND ITS LOAD SWITCH", ["J_HARN1", "R48", "J_PWR1", "D1", "C1", "C2", "C3", "C4", "FB1", "C5", "C6", "U1", "C7", "C8", "C9", "LED1", "R1", "R2", "R3",
                                                                              "U21", "C71", "R90", "R91", "C69", "C70", "R95"]),
            ("SA868 EXCITER, UART BRIDGE, T/R RELAY, 10 dB PAD, LPF, PA LEADS, GATE BIAS REGULATOR", ["U2", "Q1", "R88", "R89", "U3", "R4", "C10", "C11", "R5", "K1", "Q2", "R52", "R53", "D2", "C57", "R54", "R55", "R56", "J_PAIN", "J_PAOUT", "C58", "L1", "C59", "L2", "C60", "J_ANT", "U15", "C61", "C62", "R82", "R83", "J_VGG"]),
            ("USB HUB TUSB2046I AND ITS 3.44 V LDO, PORT TERMINATIONS, SPARE PORT", ["U5", "R6", "R7", "R8", "U4", "R9", "R10", "C12", "U17", "C64", "C65", "R80", "R81", "Y1", "R11", "C13", "C14", "C15", "C16", "C17"] + ["R%d" % k for k in range(12, 26)] + ["J_USB3"]),
            ("USB AUDIO CODEC PCM2912A, HEADPHONE AMPLIFIER, MIC PREAMP, HEADSET LEADS", ["R26", "R27", "R28", "U6"] + ["C%d" % k for k in range(18, 28)] + ["Y2", "LED2", "R29", "LED3", "R30", "R31", "R32", "C28", "R33", "R34", "U7"] + ["C%d" % k for k in range(29, 34)] +
             ["R35", "C34", "R36", "R37", "C35", "C36", "C37", "C38", "U8", "C39", "R38", "R39", "C40", "C41", "R40", "C42", "R41", "R42", "C43", "JP1", "R43", "JP2", "R44", "C44", "C45", "C46", "R45", "C47", "R46", "R47", "C48", "J_HS1", "J_HS2", "C49", "C50", "D9", "D10", "D11", "D12", "D13", "D14"])]
SECTIONS.append(("PA FLANGE TEMPERATURE: NTC LEAD AND ADC 0x48 ON THE KIT BUS (PWR-F15)", ["J_FLANGE", "R92", "C72", "R93", "C73", "R94", "C74", "U22", "C75"]))
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
SECTIONS.append(("PTT AND EMCON LOGIC, PTT MIRROR, LEDS, EXPANDER 0x26 WITH LEVEL STAGES, TEST POINTS, FLAGS", [p["ref"] for p in P if p["ref"] not in placed_refs]))
def layout(page_h):
    global out, pf_n
    out = kisch.reset_body(); placed = set(); COLW = 92.0; x = 20.0; y = 30.0
    for title, refs in SECTIONS:
        hs = []
        for ref in refs:
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"])); hs.append((y1 - y0) + 2 * STUB + 12.0)
        if y + 20 > page_h and y > 30.0: x += COLW; y = 30.0
        text(title, round((x - 15.0) / 1.27) * 1.27, round((y - 4.0) / 1.27) * 1.27); y += 4.0
        for ref, h in zip(refs, hs):
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"]))
            if y + h > page_h: x += COLW; y = 34.0
            cy = y + (y1 + STUB) + 4.0; gx = round((x + 20.0) / 1.27) * 1.27; gy = round(cy / 1.27) * 1.27
            if p["sym"] == "PWR_FLAG": emit_pwr_flag(p, gx, gy)
            else: emit_part(p, gx, gy)
            placed.add(ref); y += h
        y += 8.0
    missing = [p["ref"] for p in P if p["ref"] not in placed]
    if missing: raise SystemExit("unplaced parts: %s" % missing)
    return x + COLW
_intent.bypass("C7", "U1", "1", "+5V_D8")
_intent.bypass("C8", "U1", "5", "+3V3_D8")
_intent.bypass("C9", "U1", "5", "+3V3_D8")
_intent.bypass("C15", "U4", "3", "+3V4_HUB")   # W6-F5, 26 September 2026: the hub's decoupling follows it to +3V4_HUB
_intent.bypass("C16", "U4", "3", "+3V4_HUB")
_intent.bypass("C17", "U17", "5", "+3V4_HUB")   # G14 (round 8): rail bulk, class B1, declared against the regulator that feeds the rail
_intent.bypass("C64", "U17", "1", "+5V_D8")     # the hub LDO's input and output capacitors (SBVS351D 5.3)
_intent.bypass("C65", "U17", "5", "+3V4_HUB")
_intent.bypass("C61", "U15", "6", "+5V_TX")     # W2 F-PR-02: the VGG LDO's input and output capacitors (U15's IN on +5V_TX since round 8)
_intent.bypass("C62", "U15", "1", "VGG_SW")
_intent.bypass("C18", "U6", "2", "+5V_D8")
_intent.bypass("C19", "U6", "5", "PCM_VDD")
_intent.bypass("C20", "U6", "15", "PCM_VCCA")
_intent.bypass("C21", "U6", "19", "PCM_VCCL")
_intent.bypass("C22", "U6", "21", "PCM_VCCR")
_intent.bypass("C23", "U6", "26", "PCM_VCCP")
_intent.bypass("C31", "U7", "12", "AMP_HPVDD")
_intent.bypass("C32", "U7", "14", "+5V_D8")
_intent.bypass("C33", "U7", "14", "+5V_D8")
_intent.bypass("C39", "U8", "8", "+5V_D8")
_intent.bypass("C71", "U21", "6", "+5V_D8")     # round 8 (EMCON L4): the load switch's input capacitor (SLVSDH0C 7.3, pin table)
_intent.bypass("C75", "U22", "8", "+3V3")       # round 8 (PWR-F15): the flange ADC's VDD (SBAS444E pin table)
# G14 OF THE DECOUPLING RULING: EVERY ENTRY DECLARES ITS CLASS AND THE MAKER'S CLAUSE (round 8 of MESHSAT-1357, 26 September
# 2026; v2/docs/feasibility/DECOUPLING.md section 6 for the classes, 6a for the microfarad ones, 8.3 G14). Written into each
# intent entry as "class" and "basis" (and "floor_uF" where a class L maker states a stability floor, "maker_mm" where the
# maker gives a distance, D6), which is what T5 of that page asks intent.bypass to carry; until the tools read them the
# gate keys on the value string as before, so this changes no verdict. A class the page does not define, an entry left
# without a class, or a class given to a capacitor that is not an entry stops the generator.
#   D: a capacitor a maker ties to a supply pin (an LDO's input, the per-pin logic capacitors, the TPA6132A2's VDD);
#   L: a regulator's output, internal or external (TLV755P and TLV758P outputs, the PCM2912A's five internal
#      regulators, the TPA6132A2's HPVDD);
#   B1: rail bulk the maker frees, declared against the regulator that feeds the rail (the TUSB2046B's 10 uF, C17, now
#      declared against U17 pin 5, which feeds +3V4_HUB, and not the hub's VCC pin);
#   B2: a microfarad capacitor no maker places (the TPA6132A2's optional 10 uF).
# One judgement differs from the page's own list, which names the PCM2912A among class D's per-pin parts: TI SLES230A
# 9.5.1.6 says "All required power sources are generated by five internal regulators ... Each regulator has an output pin
# and a ground return pin ... this pair must be decoupled", so VDD and VCCA, VCCL, VCCR and VCCP are internal regulator
# outputs, class L by the page's own definition ("an internal regulator's output"). The seat rules of L and D are the
# same (L1); L adds the maker's stability condition, and SLES230A states none beyond "an appropriate capacitor", so no
# floor is written. Recorded for the DECOUPLING writer, not settled here.
_TLV755 = "TI SBVS320D 7.1.1, p.15"
_TLV758 = "TI SBVS351D 7.1.2"
_LVC = {"U9": "TI SCES217AA 8.3, the family sheet (the fitted TECH PUBLIC 74LVC1G08 sheet states no decoupling)",
        "U10": "TI SCES217AA 8.3, the family sheet (the fitted TECH PUBLIC 74LVC1G08 sheet states no decoupling)",
        "U11": "TI SCES214AF 8.4", "U12": "TI SCES217AA 8.3, the family sheet (the fitted TECH PUBLIC 74LVC1G08 sheet states no decoupling)",
        "U13": "TI SCES295AB 7.3", "U14": "TI SCES217AA 8.3, the family sheet (the fitted TECH PUBLIC 74LVC1G08 sheet states no decoupling)",
        "U18": "Diodes DS36108 states no decoupling; TI SCES217AA 8.3 for the LVC family", "U19": "Diodes DS36108 states no decoupling; TI SCES217AA 8.3 for the LVC family",
        "U20": "Diodes DS36108 states no decoupling; TI SCES217AA 8.3 for the LVC family"}
BYPASS_CLASS = {
    "C7":  ("D", _TLV755 + ": 'Place a 1uF or greater capacitor on the input pin of the LDO'"),
    "C8":  ("L", _TLV755 + ": 'requires an output capacitance of 0.47uF or larger for stability'", 0.47),
    "C9":  ("L", _TLV755 + ": 'requires an output capacitance of 0.47uF or larger for stability'", 0.47),
    "C15": ("D", "TI SLLS413L 11.1.1 item 1, p.18: 'A 0.1-uF should be placed as close as possible on VCC power pin'"),
    "C16": ("D", "TI SLLS413L 11.1.1 item 1, p.18: 'A 0.1-uF should be placed as close as possible on VCC power pin'"),
    "C17": ("B1", "TI SLLS413L 10.1, p.17, bulk 'can be placed anywhere on the power rail', and 11.1.1 item 5, p.18, bulk 'as close as possible to the voltage regulators': declared against U17 pin 5"),
    "C64": ("D", _TLV758 + ": an input capacitor 'is not required for stability' but is good practice; CIN 1 uF (5.3)"),
    "C65": ("L", _TLV758 + ": 'requires an output capacitance of 0.47 uF or larger for stability'", 0.47),
    "C61": ("D", _TLV758 + ": an input capacitor 'is not required for stability' but is good practice; CIN 1 uF (5.3)"),
    "C62": ("L", _TLV758 + ": 'requires an output capacitance of 0.47 uF or larger for stability'", 0.47),
    "C18": ("D", "TI SLES230A p.27: 'The decoupling capacitors must be as close as possible to the PCM2912A pins' (VBUS, the regulators' input)"),
    "C19": ("L", "TI SLES230A 9.5.1.6 and Table 6: VDD is an internal regulator's output pin; p.27 for placement"),
    "C20": ("L", "TI SLES230A 9.5.1.6 and Table 6: VCCA is an internal regulator's output pin; p.27 for placement"),
    "C21": ("L", "TI SLES230A 9.5.1.6 and Table 6: VCCL is an internal regulator's output pin; p.27 for placement"),
    "C22": ("L", "TI SLES230A 9.5.1.6 and Table 6: VCCR is an internal regulator's output pin; p.27 for placement"),
    "C23": ("L", "TI SLES230A 9.5.1.6 and Table 6: VCCP is an internal regulator's output pin; p.27 for placement"),
    "C31": ("L", "TI SLOS597B 9, p.17: 'Connect the HPVDD pin only to a 2.2 uF, X5R or better, capacitor ... within 5 mm'", 2.2, 5.0),
    "C32": ("D", "TI SLOS597B 9.1, p.17: 'Place a 2.2 uF capacitor within 5 mm of the VDD pin'", None, 5.0),
    "C33": ("B2", "TI SLOS597B 9.1, p.17: 'an additional 10 uF or higher value capacitor ... unnecessary in most applications'"),
    "C39": ("D", "TI SBOS839N 8.3: 'Place 0.1uF bypass capacitors close to the power-supply pins'"),
    "C71": ("D", "TI SLVSDH0C pin table: VIN, 'Place ceramic bypass capacitor(s) between this pin and GND'; CIN 1 uF (7.3)"),
    "C75": ("D", "TI SBAS444E pin table: VDD, 'Connect a 0.1uF, power-supply decoupling capacitor to GND'"),
}
for _cap, _u in (("C51", "U9"), ("C52", "U10"), ("C53", "U11"), ("C54", "U12"), ("C55", "U13"), ("C56", "U14"), ("C66", "U18"), ("C67", "U19"), ("C68", "U20")):
    BYPASS_CLASS[_cap] = ("D", _LVC[_u] + ": a 0.1 uF bypass capacitor at VCC, near the supply terminal")
_CLASSES = ("R", "D", "L", "A", "B1", "B2")
_declared = {b["cap"] for b in _intent._I["bypass"]}
_extra = sorted(set(BYPASS_CLASS) - _declared)
if _extra: raise SystemExit("G14: a class is given to %s, which %s no bypass entry" % (_extra, "is" if len(_extra) == 1 else "are"))
for _b in _intent._I["bypass"]:
    _row = BYPASS_CLASS.get(_b["cap"])
    if _row is None: raise SystemExit("G14: bypass entry %s -> %s.%s declares no class" % (_b["cap"], _b["part"], _b["pin"]))
    if _row[0] not in _CLASSES: raise SystemExit("G14: %s's class %r is not one of %s" % (_b["cap"], _row[0], _CLASSES))
    _b["class"], _b["basis"] = _row[0], _row[1]
    if len(_row) > 2 and _row[2] is not None: _b["floor_uF"] = _row[2]
    if len(_row) > 3 and _row[3] is not None: _b["maker_mm"] = _row[3]
import schlayout, time as _time
PAPER, NPAGES, NCOLS, NROWS = schlayout.run(P, SECTIONS, POWER, _intent._I["bypass"], {"date": _time.strftime("%Y-%m-%d")}, os.environ.get("PHASE", ""), 'PCB-D APRS MEZZANINE')   # 15 Sep 2026: one A3 page per block, real wiring (32.196)
out = kisch.out
print("layout: %d A3 pages on a %d x %d sheet -> paper %s" % (NPAGES, NCOLS, NROWS, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper %s)\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-D APRS MEZZANINE") (date "%s")' % _time.strftime("%Y-%m-%d") + ' (rev "A") (company "MeshSat") (comment 1 "Phase ' + (os.environ.get("PHASE") or "?") + ' schematic (SA868 exciter, T/R relay and low-pass filter, the 30 W PA on the face plate, USB audio and control set; appendix 32.56, 32.57, 32.59), generated by tools/gen_sch_d.py"))\n'
hdr += '\t(lib_symbols\n' + "".join("\t\t" + ser(v, 2).replace("\n", "\n\t\t") + "\n" for v in libsyms.values()) + '\t)\n'
body = "".join("\t" + s.replace("\n", "\n\t").rstrip("\t") for s in out)
open(OUT, "w").write(hdr + body + '\t(sheet_instances (path "/" (page "1")))\n)\n')
print("wrote", OUT, "parts:", len(P), "lib symbols:", len(libsyms))
nets = {}
for p in P:
    for num, net in p["nets"].items():
        if net != "NC": nets.setdefault(net, []).append("%s.%s" % (p["ref"], num))
single = [n for n, v in nets.items() if len(v) == 1]
print("nets:", len(nets), "single-pin nets (should be empty or intentional):", single)

# --- decoupling as data (8 Sep 2026, MESHSAT-862 Stage C): which capacitor serves which supply pin, so `intent_checks.py` can measure the
# pad-to-pin distance and the loop instead of trusting that the schematic order means anything. Read out of this file's own order (each
# capacitor sits directly after the part it serves) and filtered to supply pins: crystal loads, reset networks, the codec's VCOM reservoirs
# and the amplifier's charge-pump and input capacitors are not decoupling and are not listed. intent.py refuses an entry whose capacitor is
# not on that pin's net, so a wrong line here stops the generator.
# CORRECTED 8 Sep 2026: an earlier note here said U9 to U14 had no bypass capacitor. They do, C51 to C56, one per gate, and they are
# now declared above with their gate so the proximity rule reaches them; the placement is what has to be judged, not the count.
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
