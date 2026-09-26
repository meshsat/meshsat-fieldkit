#!/usr/bin/env python3
"""PCB-P PACK BMS, phase P1 (MESHSAT-830; appendix 32.62: the built 4S smart pack of the kit): generate the KiCad 9 schematic (netlist style:
every pin gets a stub and a net label; GND pins get power symbols). Runs where the KiCad symbol libraries are (the vast.ai box).
Usage: gen_sch_p.py <out.kicad_sch> <project>

THE PACK (D-06, owner ruling of 26 September 2026): one 4S3P block of Samsung INR18650-35E, about 145 Wh, shrink-wrapped in the east
pocket of the Peli 1450 under board B, with this board mounted beside it, SUBJECT TO THE CASE MEASUREMENT (the ruling's own words).
The measurement it names is no longer the owner's: he reversed D-08 at about 09:30 on 26 September 2026 and withdrew the request to
measure a case and build a mock-up, so every case-dependent margin is held against the worst of Peli's own figures for the current 1450
moulding (1451-931 drawing of 2025-01-15, the STEP, the web page; D-08a), and sealing and stack-up are verified on the prototype build
with a new current-moulding case. Adjudication A06 of MESHSAT-1357: no 4S4P fits either pocket and no rigid enclosure fits at all; the
geometry is W4's and v2/cad/pack_4s.py is out of this file's scope. Four series groups of three cells.
Nothing below depends on the parallel count except the per-cell currents, which are the worst case at three.

TI BQ4050 (SMBus 1.1 gas gauge with CEDV gauging, primary protection and internal cell balancing for 1S to 4S; datasheet SLUSC67B in
vendor/battery/ti-bq4050.pdf) in its own RSM0032A VQFN (4 x 4 mm, 0.4 mm pitch, round 4 W6-F2): the cell taps VC1..VC4 through 100 ohm and
0.1 uF, BAT and PACK sense inputs through 100 ohm and 1 kohm, VCC from the pack terminal, the coulomb counter across a 2 mohm 2512 sense
resistor in the negative path (SRP on the cell side, SRN on the pack side, 100 ohm each), FOUR 10k NTCs (Semitec 103AT-2), one per series
group, on TS1 to TS4 through J_TS (round 4 F-PK-02), PRES pulled to VSS (an embedded pack, present) and brought out on the lead through
TI's 1 kohm, no LED display (the panel shows the bar). THE PTC INPUT IS ENABLED (decision 40 / D-15 floor): PTCEN on BAT, a Murata
PRF15BB103RB6RC chip PTC beside the protection FETs from PTC to BAT with 0.1 uF across it (SLUSC67B Figure 21, RT1 and C12).

The high-side protection is two CSD17570Q5B PowerPAK N-FETs in series with common drain (the charge FET's source at the protected cell
terminal, the discharge FET's source at PACK+), 5.1 kohm gate drive and 10 Mohm gate-source each, driven by CHG and DSG. THE SECOND LEVEL
(decision 40 / D-15, round 4): a TI BQ7720700 (BQ77207 family, 3S to 7S, cell over-voltage 4.325 V, cell under-voltage 2.25 V, open wire)
on its own 1 kohm / 0.1 uF tap filters, with its TS pin held by a fixed 10 kohm to VSS (R33, which reads as 25 C), so neither its fixed
70 C over-temperature nor an under-temperature it may carry can ever fire the fuse (fix-up of 26 September 2026, see U2 below: owner
ruling D-02a makes +71 C storage and +55 C operation margins the kit must survive and recover from). Its COUT (over-voltage, open wire,
oscillator fault) and the gauge's FUSE output both drive the gate of an AO3400A that heats an Eaton SCF9550-30-05
self-control fuse (a three-terminal chemical fuse, 30 A, rated for four to five cells, operating -20 to +60 C) in series between the 25 A
blade and the charge FET, through a normally open arming jumper JP1 that is closed at commissioning (after the gauge's golden image is
written and read back, which is the data-flash verification D-15 names). Its DOUT (under-voltage) pulls the discharge FET's gate to
ground through a 2N7002, which turns the discharge switch off in hardware and leaves the charge path open through the discharge FET's
body diode (BQ77207 SLUSEG7D Figure 8-3).

SMBus clock and data leave through 100 ohm with a Nexperia PESD5V0S1BA clamp on each line to the PACK side of the shunt (round 4
F-BP-01: the USBLC6-2SC6 had its VBUS pin on the gauge's VCC, fed from PACK+ through 1 kohm, and held it at 6 V). Connectors: J_CELL
(JST-XH 1x5, the five tap wires), J_TS (JST-PH 1x5: TS1 TS2 TS3 TS4 VSS), J_SMB (JST-XH 1x4: SMBC, SMBD, the pack-side ground, PRES;
round 4 S-05), the pack leads W_P and W_N as 2.5 mm2 solder lands (12 AWG to the XT60 that lands on E6's J_BATT), the blade holder F1
and the chemical fuse F2. The two terminal capacitors C11 and C12 sit in SERIES across PACK+ and PACK- (TI's pair, SLUSC67B 8.2.2.1.5),
so one shorted capacitor cannot short the terminals. Copper and layers per decision 28; the power path in locked bands (gen_pcb_p3.py).
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-p-pack"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from idc_pads import idc   # the IDC land is a per-board measurement (IDC_PADS), not a default: see idc_pads.py
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine is one module now, not a copy per board. What stays in this
# file is this board: its part tables, its nets and its sheet layout. `ic()` is strict again: every pin of an IC is listed.
import kisch
from kisch import (parse, ser, find_sym, flatten_raw, flatten, rename_units, lib_tree, pins_of, extents, synth_symbol,
                   ensure, part, ic, c, r, esd, noconn, q, uq, U, tps22810, usb_c_recept, emit_pwr_flag,
                   place_symbol, wire, label, text, emit_part)
import intent as _intent
_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", loads={"Q2": 10.0}, switch="U1", enable_net="DSG_R", v_work=16.8, converted=False,   # the GAUGE's own pin; R18, 5.1k, sits between it and the FET gate DSG_G
             note="the pack lead. THE SWITCH IS THE GAUGE: Q2 is the discharge FET and the BQ4050 drives its gate on DSG_G, so the pack terminal is live only while the gauge allows it, which is the first stage of the energy chain")
_intent.rail("CELL4", 14.4, 10.0, 18.0, "W_BP", always_on=True, converted=False, loads={"F1": 10.0},
             always_on_why="the cell block itself: there is nothing upstream of it to switch, which is why everything downstream is protected rather than enabled",
             note="the top cell node from the block strip")
# WHAT FEEDS THIS RAIL (20 September 2026, appendix 32.246): `power_path` adds up what a rail's
# converters draw and refuses to let a feeder declare less than its children take. Board A's VBAT
# declared 10 A and its nine converters drew 15.18, and nothing checked it on any board until now.
_intent.rail("FUSED", 14.4, 10.0, 18.0, "F1", loads={"F2": 10.0}, always_on=True, converted=False, fed_from="CELL4",
             always_on_why="the cell node after the 25 A blade: a fuse is protection and not a switch",
             note="after the blade fuse, into the chemical fuse F2 (round 4, 26 September 2026: it fed Q1 directly until then)")
# 26 September 2026 (decision 40 / D-15): the chemical fuse F2 sits between the blade and the charge FET, as TI places it (SLUSC67B
# Figure 21), so the cell node splits into FUSED (blade to chemical fuse) and SCP_OUT (chemical fuse to Q1's source). THE NAME HAS AN
# ODD NUMBER OF CHARACTERS ON PURPOSE: drawn as "FUSED2" (and as "PROT" or "CFUSED" in a test on the box), the label on Q1's three source
# pins put the whole Q1 symbol 0.635 mm off the 1.27 mm grid (eight endpoint_off_grid ERC warnings), while "SCP_OUT", "FUSED_C", "F_SCP"
# and "FUSEC" left it on the grid; a schlayout.py matter for its owner, recorded in the round-4 drafts. D-06: the block
# is 4S3P, so the 18 A peak is 6 A per cell against the Samsung 35E's 8 A continuous rating (pcb_pack_protection.yaml, 3.8).
_intent.rail("SCP_OUT", 14.4, 10.0, 18.0, "F2", loads={"Q1": 10.0}, always_on=True, converted=False, fed_from="FUSED",
             always_on_why="the cell node after the chemical fuse: a fuse is protection and not a switch, and the heater that opens it is "
                           "driven only by a protection event",
             note="after the SCF9550-30-05 chemical fuse, into the charge FET's source")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers (as B13/B15)
LIBCACHE = {}

# ----------------------------------------------------------------- synthetic box symbols (parts with no library symbol): odd pins left, even pins right
# NiceRF SA868 (V1.x manual, 18 castellations); TI PCM2912A (SLES230A, TQFP-32); TI TPA6132A2 (SLOS553, QFN-16, pin 17 the pad); TI TUSB2046B (SLLS413L, LQFP-32);
# Silicon Labs CP2102N QFN28 (as B16)
SA868 = {1: "AUDIO_ON_n", 2: "NC", 3: "AF_OUT", 4: "NC", 5: "PTT_n", 6: "PD", 7: "H/L", 8: "VBAT", 9: "GND", 10: "GND", 11: "NC", 12: "ANT", 13: "NC", 14: "NC", 15: "NC", 16: "RXD", 17: "TXD", 18: "MIC_IN"}
PCM2912A = {1: "BGND", 2: "VBUS", 3: "D-", 4: "D+", 5: "VDD", 6: "DGND", 7: "XTO", 8: "XTI", 9: "FL", 10: "FR", 11: "VCOM1", 12: "VCOM2", 13: "AGND", 14: "NC", 15: "VCCA", 16: "VIN", 17: "MBIAS", 18: "VOUTL",
            19: "VCCL", 20: "HGND", 21: "VCCR", 22: "VOUTR", 23: "MAMP", 24: "POWER", 25: "PGND", 26: "VCCP", 27: "TEST1", 28: "TEST0", 29: "SSPND", 30: "MMUTE", 31: "REC", 32: "PLAY"}
TPA6132A2 = {1: "INL-", 2: "INL+", 3: "INR+", 4: "INR-", 5: "OUTR", 6: "G0", 7: "G1", 8: "HPVSS", 9: "CPN", 10: "PGND", 11: "CPP", 12: "HPVDD", 13: "EN", 14: "VDD", 15: "SGND", 16: "OUTL", 17: "PAD"}
TUSB2046B = {1: "DP0", 2: "DM0", 3: "VCC", 4: "RESET_n", 5: "EECLK", 6: "EEDATA/GANGED", 7: "GND", 8: "BUSPWR", 9: "PWRON1_n", 10: "OVRCUR1_n", 11: "DM1", 12: "DP1", 13: "PWRON2_n", 14: "OVRCUR2_n", 15: "DM2", 16: "DP2",
             17: "PWRON3_n", 18: "OVRCUR3_n", 19: "DM3", 20: "DP3", 21: "PWRON4_n", 22: "OVRCUR4_n", 23: "DM4", 24: "DP4", 25: "VCC", 26: "EXTMEM", 27: "TSTPLL/48MCLK", 28: "GND", 29: "XTAL2", 30: "XTAL1", 31: "TSTMODE", 32: "SUSPND"}
CP2102 = {1:"DCD",2:"RI_CLK",3:"GND",4:"D+",5:"D-",6:"VDD",7:"VREGIN",8:"VBUS",9:"RSTb",10:"NC",11:"SUSPENDb",12:"SUSPEND",13:"CHREN",14:"CHR1",15:"CHR0",16:"GPIO3",17:"GPIO2",18:"GPIO1",19:"GPIO0",20:"GPIO6",21:"GPIO5",22:"GPIO4",23:"CTS",24:"RTS",25:"RXD",26:"TXD",27:"DSR",28:"DTR",29:"GND"}
BQ4050 = {1: "PBI", 2: "VC4", 3: "VC3", 4: "VC2", 5: "VC1", 6: "SRN", 7: "NC", 8: "SRP", 9: "VSS", 10: "TS1", 11: "TS2", 12: "TS3", 13: "TS4", 14: "NC", 15: "BTP_INT", 16: "PRES",
          17: "DISP", 18: "SMBD", 19: "SMBC", 20: "LEDCNTLA", 21: "LEDCNTLB", 22: "LEDCNTLC", 23: "PTC", 24: "PTCEN", 25: "FUSE", 26: "VCC", 27: "PACK", 28: "DSG", 29: "NC", 30: "PCHG", 31: "CHG", 32: "BAT", 33: "PAD"}   # SLUSC67B pin table, RSM package, 33 = the thermal pad
# TI BQ77207 (SLUSEG7D, Rev. D, May 2026, section 5, 12-pin WSON DSS): the pin table has twelve pins; pad 13 is the exposed pad of the
# DSS0012B land (page 27), soldered "for thermal and mechanical performance" and tied to VSS here as TI ties the same family's pad
# (the BQ2947's EP to GND in SLUSC67B Figure 21). 26 September 2026, decision 40 / D-15.
BQ77207 = {1: "VDD", 2: "V7", 3: "V6", 4: "V5", 5: "V4", 6: "V3", 7: "V2", 8: "V1", 9: "VSS", 10: "COUT", 11: "DOUT", 12: "TS", 13: "EP"}
SYNTH = {"SA868": SA868, "PCM2912A": PCM2912A, "TPA6132A2": TPA6132A2, "TUSB2046B": TUSB2046B, "CP2102N": CP2102, "BQ4050": BQ4050, "BQ77207": BQ77207}

# ----------------------------------------------------------------- footprints
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "R2010": "Resistor_SMD:R_2010_5025Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C1206": "Capacitor_SMD:C_1206_3216Metric", "C1210": "Capacitor_SMD:C_1210_3225Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
 "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "IDC16": idc("2x08"),
 "TP": "TestPoint:TestPoint_Pad_D1.5mm", "QFN28": "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm", "TQFP32": "Package_QFP:TQFP-32_7x7mm_P0.8mm", "LQFP32": "Package_QFP:LQFP-32_7x7mm_P0.8mm",
 "QFN16": "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm", "VSSOP8": "Package_SO:VSSOP-8_3x3mm_P0.65mm", "TSSOP24": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
 "SA868": "meshsat:NiceRF_SA868", "RELAY": "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y", "SMA": "Connector_Coaxial:SMA_Amphenol_132134_Vertical", "UFL": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
 "L1812": "Inductor_SMD:L_1812_4532Metric", "FB": "Inductor_SMD:L_0805_2012Metric", "SOD123": "Diode_SMD:D_SOD-123", "SMB": "Diode_SMD:D_SMB",
 "PH2": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "PH5": "Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical",
 "JP": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
 # W6-F2, 26 September 2026: THE GAUGE SAT ON THE WRONG LAND. The BQ4050RSMR is TI's RSM0032A VQFN, 4 x 4 mm on a 0.4 mm pitch with a
 # 1.4 mm exposed pad (SLUSC67B pages 1, 47 and 51 to 52), and it was placed on KiCad's QFN-32 5 x 5 mm, 0.5 mm pitch land with a 3.1 mm
 # pad, so every board P route and DRC result around U1 was taken on a land the part does not fit (including decision 28's P8 arm).
 # KiCad 9.0.9 has no 4 x 4 mm, 0.4 mm land with a 1.4 mm pad (its two carry 2.65 and 2.9 mm pads), so the land is built from TI's own
 # example board layout (drawing 4219107/A) in meshsat.pretty. Its pad spacing is 0.4 - 0.2 = 0.20 mm, EXACTLY JLCPCB's 2 oz solder
 # mask bridge floor (vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md: "solder mask bridge, 2 oz | 0.20 mm pad spacing").
 "RSM32": "meshsat:Texas_RSM0032A_VQFN-32-1EP_4x4mm_P0.4mm_EP1.4x1.4mm", "PPAK": "Package_SO:PowerPAK_SO-8_Single", "RS2512": "Resistor_SMD:R_2512_6332Metric",
 # Round 4, 26 September 2026: the second level and the SMBus clamps. DSS12 is KiCad's own land for TI's DSS0012B (pads 0.5 x 0.25 on a
 # 0.5 mm pitch in rows 1.9 apart, pad 13 1.0 x 2.65: SLUSEG7D page 27, compared pad for pad on the box). SCF is the Eaton SCF9550 land
 # (fix-up of 26 September 2026, replacing the Dexerials SFK land of the first round-4 pass), drawn from Eaton's OWN recommended pad
 # layout (Technical Data ELX1135, page 3). It is in the project library (v2/ecad/meshsat.pretty/Eaton_SCF9550_9.5x5.0mm.kicad_mod),
 # written by the round-4 fix-up with its land review note in the land's own description (every pad against page 3's numbers).
 "DSS12": "Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65", "SOD323": "Diode_SMD:D_SOD-323", "SCF": "meshsat:Eaton_SCF9550_9.5x5.0mm", "R0402": "Resistor_SMD:R_0402_1005Metric",
 "FUSE": "Fuse:Fuseholder_Blade_Mini_Keystone_3568", "XH5": "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
 "WIRE": "Connector_Wire:SolderWire-2.5sqmm_1x01_D2.4mm_OD3.6mm", "R1206": "Resistor_SMD:R_1206_3216Metric",
}
kisch.configure(fp=FP, synth=SYNTH)   # the engine needs the footprint table before the first part
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


# ================================================================= the design (nets are root-sheet labels; GND = the cell block's negative, the only power symbol)
def pfet5(ref, value, g, d, sv, lcsc=""): part(ref, "Connector_Generic", "Conn_01x05", value, "PPAK", {"1": sv, "2": sv, "3": sv, "4": g, "5": d}, lcsc)   # PowerPAK SO-8: 1-3 source, 4 gate, 5 the drain tab (A22 lesson, 32.57)
# --- cell taps, the gauge and its filters
part("J_CELL", "Connector_Generic", "Conn_01x05", "cell tap sense wires from the 4S block (JST-XH 1x5): B- C1 C2 C3 B+; the current leaves through W_BP and W_BN", "XH5", {"1": "GND", "2": "CELL1", "3": "CELL2", "4": "CELL3", "5": "CELL4"})
# U1 is on its own RSM0032A land (W6-F2, see the footprint table). PTC and PTCEN are no longer tied to VSS: decision 40 / D-15 makes the
# PTC input part of the session floor, so PTCEN goes to BAT and the PTC element RT1 sits between PTC and BAT (SLUSC67B pin table:
# "PTCEN ... Connect to BAT"; Figure 21, RT1 and C12). 26 September 2026.
synth("U1", "BQ4050", "BQ4050RSMR: SMBus 1.1 gas gauge, primary protection, 4S balancing (SLUSC67B), RSM0032A VQFN 4x4 0.4 mm", "RSM32", {
 1: "PBI", 2: "VC4_F", 3: "VC3_F", 4: "VC2_F", 5: "VC1_F", 6: "SRN_F", 7: "GND", 8: "SRP_F", 9: "GND", 10: "TS1", 11: "TS2", 12: "TS3", 13: "TS4", 14: "GND", 15: "BTP_INT", 16: "PRES",
 17: "DISP", 18: "SMBD_I", 19: "SMBC_I", 20: "NC", 21: "NC", 22: "NC", 23: "PTC", 24: "BAT_F", 25: "FUSE", 26: "VCC_F", 27: "PACK_F", 28: "DSG_G", 29: "GND", 30: "NC", 31: "CHG_G", 32: "BAT_F", 33: "GND"}, "C157570")
c("C1", "2.2u", "PBI", "GND", "C10u")                                                                       # the backup supply capacitor on PBI
for k in (1, 2, 3, 4): r("R%d" % k, "100R", "CELL%d" % k, "VC%d_F" % k); c("C%d" % (k + 1), "100n", "VC%d_F" % k, "GND")   # cell sense filters (R1..R4, C2..C5)
r("R5", "100R", "CELL4", "BAT_F"); c("C6", "100n", "BAT_F", "GND")                                             # BAT, the primary supply
r("R6", "1k", "PACK_P", "PACK_F"); c("C7", "100n", "PACK_F", "GND")                                             # PACK sense
r("R7", "1k", "PACK_P", "VCC_F"); c("C8", "100n", "VCC_F", "GND")                                               # VCC, the secondary supply from the pack terminal (wakes a shut-down pack from the charger)
r("R8", "100R", "GND", "SRP_F"); r("R9", "100R", "PACK_N", "SRN_F"); c("C9", "100n", "SRP_F", "SRN_F")          # the coulomb counter across the sense resistor
# PACK_N IS THE BIGGEST CURRENT IN THE KIT AND IT WAS A NODE UNTIL 20 SEPTEMBER 2026.
#
# It is the pack's negative terminal from the 12 AWG lead land W_N to the 2 mOhm coulomb-counting shunt R10,
# on the far side of which is the board's own ground. Its own potential is 50 mV at the 25 A the counter is
# scaled for, which is why it was declared a NODE on 16 September: a reference rather than a voltage a part
# has to withstand. But it carries the pack's whole 10.0 A typical and 18.0 A peak, and `intent.node()` says
# in its own first line that it describes a net that is NOT a rail, so `dc_drop` solved nothing on it and
# neither PI-001 nor PI-002 had ever looked at the largest current on any board of this set.
#
# It could not be declared on 20 September at 00:45 and the reason was a gap in the RULE SET rather than a
# missing line here: `dc_drop` judges a drop as a percentage of the net's own voltage, so a 2 percent budget
# on 50 mV is a bar of ONE MILLIVOLT, and declaring `volts` as the pack's 14.4 to get a sensible bar would
# make `derate` judge R9, the 100 R sense resistor sitting on this net, against 14.4 V instead of the 50 mV it
# sees. `returns` closes that gap: the net keeps its own 50 mV, which is what CMP-001 uses, and the DROP is
# judged against the rail it returns, which is what PI-002 needs. The capacity half needed no bar at all and
# is measured on the copper either way.
# PWR-002 ASKED WHAT SWITCHES THIS AND THE ANSWER IS NOTHING, BY DESIGN (20 September 2026). Both
# protection FETs are in the POSITIVE path (Q1 the charge switch on FUSED, Q2 the discharge switch on
# PACK_P, their common drain SW), so the pack's NEGATIVE runs straight from the 12 AWG lead land through
# the coulomb-counting shunt to the board's ground with nothing in it: C11, C12, D1, R9, TP8 and R10 and
# not one switching part. (26 September 2026, round 4: J_SMB pin 3 and the two SMBus clamps D2 and D3 join it,
# S-05 and F-BP-01, still with no switching part; C11 now reaches it through C12, the series pair of O-12.) High-side protection means the return is permanently connected, which is a
# property of this pack worth writing down rather than a gap in the declaration.
_intent.rail("PACK_N", 0.05, 10.0, 18.0, "W_N", loads={"R10": 10.0}, returns="PACK_P", converted=False,
             v_work=0.05, always_on=True,
             always_on_why="both protection FETs are in the positive path (Q1 on FUSED, Q2 on PACK_P), so "
                           "nothing on this board is in series with the pack's negative: it runs from the "
                           "lead land W_N through the 2 mOhm shunt R10 to ground with no switching part in "
                           "it, which is what high-side protection means",
             note="the pack negative from the 12 AWG lead land W_N to the 2 mOhm coulomb-counting shunt R10, "
                  "at the pack's own 10.0 A typical and 18.0 A peak. Its own potential is 50 mV at 25 A, "
                  "which is what a part on it is judged against; its DROP is judged against PACK_P, the rail "
                  "it returns, because a percentage of 50 mV is not a bar anybody could state")
_intent.node("GND", 0.0, "the board's reference, so a part between a live net and ground is judged against "
             "the live net rather than reported as sitting on an undeclared one")
r("R10", "2m 2512 2W (sense)", "GND", "PACK_N", "RS2512")                                                       # 25 A gives 50 mV, inside the counter's range
# F-PK-02 (round 4, 26 September 2026): ONE THERMISTOR COVERED THE WHOLE BLOCK. TS2 to TS4 were fixed 10k resistors, so twelve cells
# (sixteen in the old 4S4P reading) were judged by one 103AT on TS1, and the pack protection record listed "10k NTC x4" against a
# reference (R10) that is the shunt. The gauge has four thermistor inputs and TI's application schematic fits all four (SLUSC67B
# Figure 21, RT2 to RT5, 10k NTC, each from TSx to VSS with nothing else on the line; the EVM bill of materials SLUUBF9 Table 5 names
# them "103AT-2, Semitec"), so the pack gets four: one per SERIES GROUP of the 4S3P block (D-06), taped to the middle cell of its three,
# which is the one with the least surface to lose heat through. Each input's 18 kohm pull-up is internal (SLUSC67B 6.22, RNTC(PU)), so
# the lead carries four sense wires and one common return to VSS. The old C10 (100 nF on TS1 alone) is removed with the fixed
# resistors: TI's circuit and EVM carry no capacitor on any TS input, the settling limit for one would be in the technical reference
# manual (SLUUAQ3, not held), and one filtered input beside three unfiltered ones was not a design anybody chose.
# The socket is JST B5B-PH-K-S(LF)(SN), LCSC C157993 (JLC API 26 September 2026: JST, stock 161,968), the five-way member of the
# PH family whose two-way B2B-PH-K-S-GW (C5251182) this board already buys; KiCad's JST_PH_B5B-PH-K land is drawn for it.
part("J_TS", "Connector_Generic", "Conn_01x05", "JST-PH 1x5 socket for the four cell thermistors (Semitec 103AT-2, one per series group of the 4S3P block): TS1 TS2 TS3 TS4 VSS", "PH5",
     {"1": "TS1", "2": "TS2", "3": "TS3", "4": "TS4", "5": "GND"}, "C157993")
r("R14", "10k", "PRES", "GND"); r("R15", "10k", "DISP", "GND")                                                  # embedded pack: present; no LED display
# S-05 (round 4, 26 September 2026): PRES leaves the board on the SMBus lead (J_SMB pin 4), so it takes TI's series resistor: "An
# integrated ESD protection on the PRES device pin reduces the external protection requirement to just R29 for an 8-kV ESD contact
# rating" (SLUSC67B 8.2.2.2.3, Figures 29 and 30: R29 1k between the pin and J3). R14 keeps the pin low on this board either way.
r("R22", "1k", "PRES_J", "PRES")
# THE PTC INPUT (decision 40 / D-15 floor, 26 September 2026). SLUSC67B 6.23: the gauge biases PTC with 200 to 350 nA and trips when
# PTCEN - PTC exceeds 200 to 890 mV, which is an element resistance of 1.2 to 3.95 Mohm. TI's bq40z50 EVM guide (SLUUAV7C 4.5) says of
# the same interface that the element "must have a 10-kOhm typical resistance over the normal operating temperature range and the
# resistance must be greater than 1.2 MOhm at the PTC trip temperature" and names a Murata PRF18 part. Murata's PRF series data sheet
# (DM-SA16-E056 Rev.1, 2016, page 4) lists the 10 kohm types by the temperature at which they REACH 4.7 Mohm, which is above the gauge's
# 3.95 Mohm maximum, so the trip is guaranteed rather than typical. It sits beside the protection FETs as TI's Figure 21 note 2 says
# ("Place RT1 close to Q2 and Q3"), with C13 across it (Figure 21, C12 0.1 uF). A trip is the gauge's PTC permanent failure ("It can only
# be cleared by a POR", SLUSC67B 8.2.2.3.6), which drives FUSE when the golden image enables it.
# FIX-UP OF 26 SEPTEMBER 2026: THE FIRST PICK, PRF15BE103RB6RC (4.7 Mohm at 100 +-3 C), IS NOT ORDERABLE. Digi-Key's page (read 26
# September 2026) says "This product is obsolete and no longer manufactured" and names PRF15BB103RB6RC as its substitute; JLCPCB holds 0
# and LCSC says "Not available now". The part taken is that substitute, checked against the same Murata data sheet, same page: 1005/0402,
# two terminals (the same R0402 land), 10 kohm +-50 percent at 25 C, 100 kohm not before 110 C, 4.7 Mohm at 130 +-3 C, 32 V, operating
# -20 to +140 C (the -20 C floor of D-02a's -20 to +40 C use envelope, stated as a rating). So the gauge's PTC trip moves from at most 103 C to between about
# 110 and 133 C at the element: still a guaranteed trip on a failing FET (the CSD17570Q5B's junction limit is 150 C), and nowhere near
# the +71 C storage margin of D-02a. LCSC C443668, JLC API 26 September 2026: Murata, stock 5,388, 0.126 USD.
part("RT1", "Device", "Thermistor_PTC", "PRF15BB103RB6RC chip PTC 10k, 4.7M at 130 C (Murata): the BQ4050 PTC element beside Q1 and Q2", "R0402", {"1": "PTC", "2": "BAT_F"}, "C443668")
c("C13", "100n", "PTC", "BAT_F")
# --- the high-side protection: fuse, chemical fuse, charge FET, discharge FET (common drain), gate networks
part("F1", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder): the pack's fuse", "FUSE", {"1": "CELL4", "2": "FUSED"})
# THE CHEMICAL FUSE (decision 40 / D-15, 26 September 2026). SLUSC67B 8.2.2.1.2: "The chemical fuse (Dexerials, Uchihashi, and so on) is
# ignited under command from either the bq294700 secondary voltage protection IC or from the FUSE pin of the gas gauge", placed between
# the cells and the charge FET (Figure 21, F1 SFDxxxx between 4P and Q2), so its heater is fed from the cells whatever the FETs are
# doing. FIX-UP OF 26 SEPTEMBER 2026: THE PART IS THE EATON SCF9550-30-05, NOT THE DEXERIALS SFK-1830A OF THE FIRST PASS. Both have the
# same electrical figures (4 to 5 cells, 30 A, heater 4.8 to 8.0 ohm, heater operating voltage 10.5 to 23.5 V, fuse 1.0 to 2.5 mohm, 80 A
# breaking), but Dexerials publishes neither an operating temperature range nor a land pattern (SFK series datasheet of 2025/10/8 and its
# Rev-14 of 2014: curves from -20 C only, "the temperature at which we have confirmed reliability is 100 degrees Celsius"; its FAQ and
# product page carry nothing more), and JLCPCB has no code for it. Eaton's Technical Data ELX1135 (SCF9550, effective January 2022;
# eaton.com copy of 5 May 2025, byte-identical to LCSC's) states "Operating temperature: -20 C to +60 C", reliability runs at +105 C for
# 1000 h and -40 C for 500 h, cURus recognition E19180, 100 percent of rating for 1 hour minimum, 200 percent opens within 60 s, and the
# heater opens it within 60 s at its operating voltage; page 3 gives the maker's recommended pad layout, from which the land is drawn.
# So the -20 C floor of D-02a's -20 to +40 C use envelope is met by a stated rating, and the land is the maker's. The +60 C operating ceiling sits above the
# -20 to +40 C use envelope plus the ruled internal rise with one module above +35 C (D-02b); at the +55 C operating margin of TEST-PLAN
# E3 the part is beyond its operating rating and inside its +105 C reliability run (D-02a: survive and recover). The heater's 10.5 V
# floor is 2.63 V per cell, so a 4S block below that may not open it: the reason the second level's under-voltage holds the discharge FET
# instead of firing the fuse (U2 below). PINS PER ELX1135 PAGE 1: 1 and 2 are the fuse ends on the two long edges (the element runs
# across the body), 3 the heater on the short edge. LCSC C3670061 (JLC API 26 September 2026: Eaton, stock 0, 1.09 USD); Digi-Key
# 283-SCF9550-30-05CT-ND, active, 907 in stock, 5.82 USD (read 26 September 2026): the hand-fit route until JLC stocks it (O-3).
# ELX1135's other temperature line, "Storage temperature: -10 C to +40 C < 90% RH, Storage duration: 1 year", is read by this session as
# the shelf condition of the reeled part before assembly (a one-year duration fits nothing else), not a limit on the mounted part,
# whose endurance is the +105 C 1000 h and -40 C 500 h runs of the same page: those bracket TEST-PLAN E3's +71 C and E4's -33 C
# storage. Eaton publishes no current derating against temperature (ELX1135 has no derating curve), EVEN INSIDE THE USE ENVELOPE:
# the 50 C that the ruled rise gives (40 C ambient plus about 10 K with one module) counts the air, not the part, and at the 18 A
# peak F2 dissipates 18 x 18 x 1.0 to 2.5 mohm (ELX1135 fuse DCR) = 0.32 to 0.81 W in its own body on top of that. At 60 percent
# of its 30 A the risk is judged low, not proven; at E3's +55 C operating margin the part sits at about 65 to 71 C before its own
# heating, above its 60 C operating rating (a recorded residual, drafts/r4-decisions.md O-8).
# BREAKING CAPACITY: 80 A (ELX1135 page 2, the same figure as the SFK-1830A, so no regression), against a prospective fault of 240
# to 480 A at this node (pcb_energy_chain.yaml, stage PACK_CELLS). F2 is not meant to clear a hard short. The gauge's short circuit
# in discharge opens the FETs after its programmed delay (SLUSC67B 6.32: tSCD1 0 to 915 us, or to 1850 us with SCDDx2, plus at most
# 160 us detection; the setting is the golden image's, O-10), inside F1's melting time; if the FETs have failed closed, the 25 A ATOF
# blade F1 in series (1000 A interrupting at 32 VDC, I2t 1000 A2s, melting in 4.3 to 17 ms over that range, the same yaml stage) must
# open before F2's element does. ELX1135 publishes no melting I2t for F2, so neither order is proven for F2: an energy-chain entry
# for F2 (O-13) and the D-09 battery-and-protection review packet.
part("F2", "Connector_Generic", "Conn_01x03", "SCF9550-30-05 self-control fuse (Eaton, 30 A, 4-5 cells): 1 and 2 the fuse, 3 the heater", "SCF",
     {"1": "FUSED", "2": "SCP_OUT", "3": "SCP_HTR"}, "C3670061")
pfet5("Q1", "CSD17570Q5B 30 V N-FET, charge switch", "CHG_G", "SW", "SCP_OUT", "C529279"); pfet5("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "PACK_P", "C529279")
r("R16", "5.1k", "CHG_G", "CHG_R"); r("R17", "10M", "CHG_G", "SCP_OUT"); r("R18", "5.1k", "DSG_G", "DSG_R"); r("R19", "10M", "DSG_G", "PACK_P")   # R17 follows Q1's source to SCP_OUT
# the gauge drives the gates through the 5.1k: rename the gauge pins onto the resistor side
for p_ in P:
    if p_["ref"] == "U1": p_["nets"]["31"] = "CHG_R"; p_["nets"]["28"] = "DSG_R"
# O-12 (round 4, fixed at the fix-up of 26 September 2026): THE TWO TERMINAL CAPACITORS WERE IN PARALLEL, so one cracked or shorted
# part shorted PACK+ to PACK- behind the protection FETs. TI's words for this pair: "A pair of series 0.1-uF ceramic capacitors is
# placed across the PACK+ and PACK- terminals to help in the mitigation of external electrostatic discharges. The two devices in series
# ensure continued operation of the pack if one of the capacitors becomes shorted" (SLUSC67B 8.2.2.1.5). They are in series now through
# PACK_MID, the same two parts and codes as before: 50 nF across the terminals, each 50 V part seeing about 8.4 V at 16.8 V and the
# whole 16.8 V if its partner shorts. Taken by the session under the owner's standing rule of 26 September 2026 (drafts/r4-decisions.md RP-22).
c("C11", "100n 50V", "PACK_P", "PACK_MID"); c("C12", "100n 50V", "PACK_MID", "PACK_N", "C1206")                  # ESD across the terminals, in series
# PACK_MID is declared so CMP-001 still judges the pair (it judged C11 and C12 against PACK_P before the split, and an undeclared
# midpoint dropped them from the check on the first fix-up run): its worst case is the WHOLE pack, 16.8 V at full charge, which is
# what the surviving capacitor sees once its partner has shorted, the very case the pair exists for.
_intent.node("PACK_MID", 16.8, "the midpoint of the series terminal pair (SLUSC67B 8.2.2.1.5): about half the pack in normal "
             "operation, and the whole of it, 16.8 V at 4.20 V per cell, across one capacitor when the other has shorted")
# S-09 / A03 / W2 F-IN-01, 26 September 2026: D1 WAS REVERSED AND DRAWN WITHOUT A POLARITY. The SMBJ20A is UNIDIRECTIONAL (the A
# suffix with no C; MDD SMBJ20A, LCSC C364296, the part the P4 BOM filled), and it had PACK_N on pad 1, which on KiCad's Diode_SMD:D_SMB
# is the cathode (A03 read the fab apex and the silk bracket at pad 1 with pcbnew), so the clamp was a forward-biased diode across the
# pack terminals from the first connection. Device:D_TVS is KiCad's BIDIRECTIONAL symbol (pins A1/A2), which is why no drawing showed
# it. Now the cathode (K, pin 1, pad 1) is on PACK_P and the anode on PACK_N, drawn with Device:D_Zener, the K/A symbol Review D round 4
# uses for a one-way clamp (kisch.tvs() when the tree carries it; the fallback writes the identical symbol and pin map). The fix is proven
# by the netlist (D1.1, the cathode, on PACK_P), not by TRN-001, which judged no port on this board.
# FIX-UP OF 26 SEPTEMBER 2026: D1 CARRIES ITS CODE IN THE GENERATOR NOW. lcsc_fill.py filled it from JLC-CERTIFIED.tsv, which is keyed on
# the exact (Comment, Footprint) pair ("SMBJ20A", D_SMB: C364296, CERTIFIED), and the new value text matched no row and no MAP rule, so
# the order set would have been refused for a blank. C364296 is MDD SMBJ20A, DO-214AA(SMB), JLC API 26 September 2026: stock 165,282.
# F-BP-01 (round 4, 26 September 2026): THE SMBUS CLAMP HELD THE GAUGE'S VCC AT ITS OWN BREAKDOWN. The USBLC6-2SC6 had its VBUS pin 5 on
# VCC_F, which R7 feeds from PACK_P through 1 kohm: ST DS4260 Rev 7 Table 2 gives VRM 5.25 V and VBR 6 V minimum between VBUS and GND,
# so at 12 to 16.8 V about 5 to 11 mA ran continuously through R7 into the clamp (0.06 to 0.18 W of pack drain whenever DSG is on,
# adjudication A07's arithmetic)
# and VCC sat at the clamp's breakdown rather than the pack's voltage. There is no rail on this board the VBUS pin could legitimately
# sit on, so the part goes. TI's own answer for these two lines is a clamp and a series resistor per line to the pack side of the
# shunt (SLUSC67B 8.2.2.2.4: "adding a Zener diode (D2 and D3) and series resistor (R24 and R26) provides more robust ESD performance";
# Figure 21, MM3Z5V6C to CHGND). The clamp taken is Nexperia's PESD5V0S1BA, bidirectional, VRWM 5 V, IRM 5 nA typical, Cd 35 pF typical
# and 45 pF maximum, 14 V clamping at 12 A, -55 to +150 C (Nexperia v.6, 26 April 2024; LCSC C19224, a copy with its source in the
# round-4 drafts/datasheets), rather than TI's MM3Z5V6 zener (onsemi MM3Z5V6T1G, 200 pF maximum at 0 V): the SMBus rise time is 1000 ns
# maximum (SLUSC67B 6.33, tR 10 to 90 percent) and board E pulls these lines up through 4.7 kohm (A07 evidence, gen_sch_e.py R34 and
# R35), so 200 pF per line plus about 45 pF of lead and pins is 2.2 x 4.7k x 245 pF = 2.5 us of rise at zero bias, where the
# PESD5V0S1BA's 45 pF gives about 0.9 us. R20 and R21 (100 ohm) stay as the series resistors.
# A RECORDED DEVIATION FROM TI'S REFERENCE (fix-up of 26 September 2026): SLUSC67B Figure 30 puts 200 ohm between the gauge pin and the
# clamp and 100 ohm between the clamp and the connector; this board keeps one 100 ohm (R20, R21) between the pin and the clamp and none
# to the connector, and its PESD5V0S1BA clamps higher than TI's 5.6 V zener. It is kept because the SMBC and SMBD pins carry their own
# integrated high-voltage ESD protection (SLUSC67B 8.2.2.2.4) and a second series resistor would add to the rise time the clamp choice
# was made for; the ESD level it gives is a test item (TEST-PLAN M7), not a claim.
try:
    from kisch import tvs as _tvs          # the shared helper of round 4 (S-09), when the tree carries it
except ImportError:
    _tvs = None
if _tvs:
    _tvs("D1", "SMBJ20A (pack terminal clamp, unidirectional: cathode on PACK_P)", "PACK_P", "PACK_N", "SMB", "C364296")
    _tvs("D2", "PESD5V0S1BA (SMBC ESD clamp to the pack side of the shunt)", "SMBC", "PACK_N", "SOD323", "C19224")
    _tvs("D3", "PESD5V0S1BA (SMBD ESD clamp to the pack side of the shunt)", "SMBD", "PACK_N", "SOD323", "C19224")
else:
    part("D1", "Device", "D_Zener", "SMBJ20A (pack terminal clamp, unidirectional: cathode on PACK_P)", "SMB", {"1": "PACK_P", "2": "PACK_N"}, "C364296")
    part("D2", "Device", "D_TVS", "PESD5V0S1BA (SMBC ESD clamp to the pack side of the shunt)", "SOD323", {"1": "SMBC", "2": "PACK_N"}, "C19224")
    part("D3", "Device", "D_TVS", "PESD5V0S1BA (SMBD ESD clamp to the pack side of the shunt)", "SOD323", {"1": "SMBD", "2": "PACK_N"}, "C19224")
part("W_P", "Connector", "Conn_01x01_Pin", "pack lead + (12 AWG to the XT60 on E6 J_BATT pin 2)", "WIRE", {"1": "PACK_P"})
part("W_N", "Connector", "Conn_01x01_Pin", "pack lead - (12 AWG to the XT60 on E6 J_BATT pin 1)", "WIRE", {"1": "PACK_N"})
part("W_BP", "Connector", "Conn_01x01_Pin", "cell block B+ (12 AWG from the block's positive strip)", "WIRE", {"1": "CELL4"})
part("W_BN", "Connector", "Conn_01x01_Pin", "cell block B- (12 AWG from the block's negative strip)", "WIRE", {"1": "GND"})
# --- the second-level protector, decision 40 / D-15 (26 September 2026)
#
# THE OWNER'S RULING (D-15, 26 September 2026): "use a 4S secondary protector that also covers under-voltage, if one can be sourced near
# the OV-only part's cost; otherwise accept firmware UV with a data-flash verification at commissioning. The OV secondary protector,
# chemical fuse, BQ4050 FUSE output and PTC input are the session floor." One was found. TI BQ7720700DSSR, the BQ77207 family (SLUSEG7D
# Rev. D, May 2026): 3S to 7S, cell over-voltage 4.325 V +-20 mV from 0 to 60 C with 100 mV hysteresis and a 1 s delay, cell under-voltage
# 2.25 V +-50 mV with a 1 s delay, open-wire detection, over-temperature 70 C on an external NTC, active-high 6 V outputs, -40 to 110 C
# (device comparison table, section 4), 12-pin WSON DSS 3 x 2 mm, LCSC C3681715. At JLCPCB on 26 September 2026 it lists at 2.12 USD
# against 1.30 to 1.59 USD for the OV-only BQ7718 parts at a comparable threshold (BQ771806DPJR 4.35 V, C2876137; BQ771818DPJR 4.30 V,
# C3682730): about 0.5 to 0.8 USD more per pack, which is near. JLC shows 3 in stock against 5 boards: an ordering-session item.
# WHY THIS VARIANT: the Samsung 35E charges to 4.20 V, so the secondary must sit above the gauge's own over-voltage trip (4.25 V in
# pcb_pack_protection.yaml), or the fuse opens before the primary acts: the 4.275 V variants (00701, 00702, 00704, 00705) can trip as low
# as 4.225 V at the extremes of their +-50 mV accuracy, BELOW that trip, while 4.325 V trips no lower than 4.275 V; 00706 has no
# under-voltage at all; and no standard variant has its over-temperature disabled (70, 75, 80 or 83 C). THE COST OF THE CHOICE: 2.25 V +-50 mV under-voltage
# sits below the gauge's 2.50 V and above the cell maker's 2.00 V BMS shut-down voltage, but up to 100 mV BELOW the Pack Design
# Guideline's 2.30 V "min. voltage of over-discharging protection" that pcb_pack_protection.yaml quotes. As a backstop behind the gauge's
# 2.50 V it is accepted and recorded (drafts/r4-decisions.md); TI lists custom BQ77207xy thresholds (under-voltage 1.0 to 3.5 V in 50 mV
# steps) as "contact TI", which is the route to a 4.325 V / 2.35 V part.
# THE CIRCUIT IS TI'S (SLUSEG7D 8.1 and Figure 8-3): every cell input through RIN = 1 kohm (the part is calibrated at 1 kohm, Table 8-1
# 900 to 1100 ohm) with CIN = 0.1 uF as a LADDER, each capacitor across its own cell and the lowest to VSS (Figure 8-3); the unused inputs
# V5, V6 and V7 tied to the top cell's input at the pin (Figure 8-3 ties V6 and V7 to V5 for five cells); VDD from the top of the stack
# through RVD = 300 ohm (Table 8-1: 100 to 1k, 300 nominal) with CVD = 0.1 uF.
# THE TS PIN SEES A FIXED 10 KOHM TO VSS, SO THE SECOND LEVEL HAS NO TEMPERATURE FUNCTION (fix-up of 26 September 2026, the
# reviewer's blocking finding; taken by the session under the owner's standing rule of 26 September 2026, drafts/r4-decisions.md RP-17).
# The first pass put its own 103AT-2 on TS through a socket J_TS2 (70 C threshold 2195 ohm against the 103AT-2's 2.228 kohm at 70 C).
# But SLUSEG7D Table 7-1 drives BOTH outputs on an over-temperature, and COUT fires the chemical fuse on this board: the 70 C +-5 C trip
# (TOT_ACC) would open F2 for good at TEST-PLAN E3's +71 C storage and within reach of its +55 C operation with the ruled +10 to +16 K
# rise, where owner ruling D-02a asks the kit to survive AND RECOVER. No standard variant disables over-temperature (the highest
# threshold, 83 C, belongs to 00704, which has a 4.275 V OV and an open-drain COUT); a custom BQ77207xy is "contact TI".
# WHY A RESISTOR AND NOT THE OPEN PIN THE DATA SHEET ALLOWS ("TS ... Temperature sensor input. If not used, leave it NC", section 5):
# an open NTC input reads as an infinite resistance, the coldest possible, and the same data sheet lists an UNDER-temperature
# protection (6.5: TUT -30 to 0 C, RUT_EXT_NTC 26.7 to 111.1 kohm) that drives BOTH outputs (7.1: "If an undertemperature,
# overtemperature, or open-wire fault is detected, then both the DOUT and COUT are triggered"), while the device comparison table
# (section 4) has no UT column for any variant, so whether the 00700 carries it is not stated. With TS open and UT enabled, COUT would
# be active from power-up and the fuse would open the moment JP1 is closed. 10 kohm (the 103AT's value at 25 C, ratiometric against
# the internal 20 kohm RTC) sits a factor 4.6 above the 00700's own OT resistance (2195 ohm, 70 C), 3.5 above the highest of any
# option (2850 ohm, 62 C), and a factor 2.7 below the lowest UT resistance listed (26.7 kohm, about 0 C on a 103AT; the others are
# 42.2, 68.9 and 111.1 kohm), so it reads as neither fault whatever the silicon carries: the design is indifferent to the unknown
# instead of relying on a commissioning check to find it. A resistor on TS is within the pin's use (the NTC case with a constant
# temperature); TI's note against an external CAPACITOR on TS (7.3.3, CTS at most 200 pF) is kept, there is none. A TS-to-VSS short
# (a solder bridge at R33, or pin 12 to the exposed pad) would read as over-temperature and fire the fuse once armed; JP1 is closed only
# after TP11 has been read low with the cells on (O-9), which finds it. Over-temperature stays with the gauge's four NTCs (recoverable
# FET action and its own permanent failures, set by the golden image, O-10) and the PTC element beside the FETs. R33 is MAP's "10k"
# (C25804, the code R14 and R15 already use).
synth("U2", "BQ77207", "BQ7720700DSSR: second-level cell OV 4.325 V / UV 2.25 V / open wire, TS on a fixed 10k, 3S-7S (SLUSEG7D)", "DSS12",
      {1: "SEC_VDD", 2: "SEC_V4", 3: "SEC_V4", 4: "SEC_V4", 5: "SEC_V4", 6: "SEC_V3", 7: "SEC_V2", 8: "SEC_V1", 9: "GND", 10: "SEC_COUT", 11: "SEC_DOUT", 12: "TS_SEC", 13: "GND"}, "C3681715")
r("R33", "10k", "TS_SEC", "GND")                                                                            # TS held at the 25 C reading
# R23 carries its code (fix-up of 26 September 2026): no lcsc_fill MAP rule reads "300R". UNI-ROYAL 0603WAF3000T5E, 300 ohm 1 percent
# 0603, LCSC C23025, a JLC basic part (JLC API 26 September 2026: stock 1,671,357).
r("R23", "300R", "CELL4", "SEC_VDD", lcsc="C23025"); c("C14", "100n", "SEC_VDD", "GND")                        # RVD and CVD
for k, (net, tap) in enumerate((("SEC_V1", "CELL1"), ("SEC_V2", "CELL2"), ("SEC_V3", "CELL3"), ("SEC_V4", "CELL4"))):
    r("R%d" % (24 + k), "1k", tap, net)                                                                         # RIN (R24..R27)
for k, (hi, lo) in enumerate((("SEC_V1", "GND"), ("SEC_V2", "SEC_V1"), ("SEC_V3", "SEC_V2"), ("SEC_V4", "SEC_V3"))):
    c("C%d" % (15 + k), "100n", hi, lo)                                                                         # CIN ladder (C15..C18)
# OPEN WIRE STILL FIRES THE FUSE, AND THAT IS KEPT ON PURPOSE (fix-up of 26 September 2026). Table 7-1 drives COUT on an open wire too:
# a J_CELL tap that stays open for the 4 s tOW_DELAY (6.6), counted from the moment the 50 uA, 128 us every 128 ms detection pulses
# (7.3.2) have pulled its filtered node 200 mV below its neighbour, opens F2 permanently. An open tap blinds the second level on that
# cell, so the fuse is the conservative answer, and the only variants with open wire disabled (00705, 00706) fail on OV or UV above. A
# contact bounce shorter than the delay resets the timer (7.3.2). The consequence for TEST-PLAN E1 and E2: a tap lead that backs out and
# stays out opens the fuse, and the functional check after the test finds it; the tap harness retention is a pack-build item (O-9).
# THE FUSE DRIVE (SLUSC67B 8.2.2.2.5 and Figure 31): the gauge's FUSE pin and the second level's output meet at the gate of the fuse FET,
# which sinks the heater current from F2's pin 3; the gauge's FUSE pin is also an input that reads the second level's state (VIH 1.5 to
# 2.5 V, 6.20). TI divides a 7 V protector output with 5.1 kohm and 51 kohm and a sub-volt-threshold FET (Si1406DH). Here the protector
# branch is 20 kohm instead: the BQ77207's inactive output SINKS 0.3 to 3 mA (6.5, IOUT_AH_L), so with 5.1 kohm on both branches the
# gauge alone would reach only 2.15 V at the gate at its own weakest (VOH 6 V through 3.2 kohm).
# THE NUMBERS, CORRECTED AT THE FIX-UP OF 26 SEPTEMBER 2026 (review minor m1): the first pass left out R32, which sits in parallel with
# R31 once JP1 is closed, and at 100 kohm it pulled the protector's current past the 100 uA its 6 V minimum is specified at. R32 is
# 1 Mohm now (the gate's own leakage, IGSS 100 nA at most, drops 0.1 V across it; C19 is the gate's low impedance once JP1 is closed). With
# JP1 closed, R31 || R32 = 48.5 kohm, and:
#   the gauge alone (COUT inactive, so R29 is 20 kohm to ground): 6 x (48.5 || 20 = 14.2) / (3.2 + 5.1 + 14.2) = 3.78 V at the gate;
#   the protector alone (the FUSE pin an input, 150 to 330 nA of internal pull-up, 6.20): 6 x 48.5 / 68.5 = 4.25 V, at 88 uA, inside the
#   100 uA its VOH of at least 6 V is specified at (6.5, VOUT_AH);
#   and the gauge's FUSE pin reads that 4.25 V through R30 as a second-level trip (VIH 2.5 V at most).
# Both are above the AO3400A's 1.45 V maximum threshold with room for its RDS(on) figure at 2.5 V. The FET is an Alpha and Omega AO3400A
# (datasheet Rev 3.1, July 2023: 30 V, VGS +-12 V, VGS(th) 0.65 to 1.45 V, RDS(on) under 48 mohm at 2.5 V and 32 mohm at 4.5 V, -55 to
# 150 C; LCSC C20917, a JLC basic part), which carries the SCF9550-30-05's heater (4.8 to 8.0 ohm, 1.3 to 3.5 A across the pack's range,
# for the 60 s at most Eaton gives the heater to open it: about 0.5 W in the SOT-23 at 3.5 A and 40 mohm).
# JP1, THE ARMING JUMPER, IS OPEN AS BUILT: TI's own EVM ships the fuse unfitted (SLUUBF9 Table 5, F1 DNP) and warns that the second-level
# protector "could blow the fuse" during cell connection (2.5.2), and the BQ77207 datasheet says the same of cell attachment (8.1.2.1).
# It is closed with solder at commissioning, after the cell leads are on and the gauge's golden image is written and read back, which
# is the data-flash verification D-15 names. R32 holds the gate low while it is open. JP1 is copper on this board, not a bought part,
# so it is left out of the bill of materials (in_bom False, as the test points are), where the other boards' solder jumpers are
# allow-listed instead; closing it is verified by continuity from TP11 (FUSE_G) to TP14 (FUSE_GQ), which the fix-up adds.
# THE CHECK HAS A POLARITY (second fix-up of 26 September 2026, re-review): the meter's COM (black) lead goes on TP14 and the red lead
# on TP11, cells connected. The fault the check exists for is a closure that did not wet. The meter's source then sees one path: TP11,
# R31 (51 kohm) || R29 (20 kohm into COUT's inactive sink) to GND, then R32 (1 Mohm) back up to TP14. About 98.6 percent of its
# open-circuit voltage (2 to 3.3 V on a handheld DMM) lands across R32, which is Q3's gate against its source. With COM on TP14 the gate
# goes NEGATIVE and Q3 stays off. With the red lead there the gate would sit at +2 to +3.3 V, above the AO3400A's VGS(th) of 0.65 to
# 1.45 V (AOS Rev 3.1), and the heater would draw 1.3 to 3.5 A from the cells for as long as the probes stayed on; ELX1135 gives the
# heater up to 60 s to open the fuse for good, on a pack with no fault, and a meter that reads open invites a second try. On a digital
# meter the red lead is the positive source on the ohms and continuity ranges (an analogue ohmmeter reverses it), so the procedure
# confirms the source's polarity and open-circuit voltage on the range used first (a second meter across the leads in DC volts); the
# open-circuit voltage must stay under the gate's +-12 V rating. Closed: about 0 ohm, no voltage anywhere. Open: about 1 Mohm, shown as
# open on a continuity range, with Q3's gate held negative and FUSE_G a few tens of millivolts positive. The other measurement that tells the two
# apart, TP14 to TP8 (PACK_N; the board has no GND test point) with COM on TP14, is NOT used: with JP1 closed it drives FUSE_G below
# VSS, and through R30 and R29 that risks taking the gauge's FUSE pin and the protector's COUT past their -0.3 V absolute minimum
# (SLUSC67B 6.1, SLUSEG7D 6.1). The check taken drives only JP1's FET side (R32 and Q3's gate) negative in the open state and puts
# no voltage anywhere in the closed state, so no IC pin goes below VSS in either. TP14 is at the west end of TPS2 with only TP11 beside it
# (gen_pcb_p3.py), so a slipped probe lands on FUSE_G, which the step before has read low, and never on SCP_OUT (TP13).
# R29 and R31 carry their codes (fix-up of 26 September 2026): no lcsc_fill MAP rule reads a bare "20k" or "51k". UNI-ROYAL
# 0603WAF2002T5E, 20 kohm 1 percent, C4184, and 0603WAF5102T5E, 51 kohm 1 percent, C23196, both JLC basic parts (JLC API 26 September
# 2026: stock 8,361,114 and 3,074,745). R32's "1M" is MAP's C22935.
r("R29", "20k", "SEC_COUT", "FUSE_G", lcsc="C4184"); r("R30", "5.1k", "FUSE", "FUSE_G"); r("R31", "51k", "FUSE_G", "GND", lcsc="C23196"); c("C19", "100n", "FUSE_G", "GND")
part("JP1", "Jumper", "SolderJumper_2_Open", "fuse arming jumper: open as built, closed at commissioning", "JP", {"1": "FUSE_G", "2": "FUSE_GQ"}, in_bom=False)
r("R32", "1M", "FUSE_GQ", "GND")
# KiCad's Transistor_FET:AO3400A is Q_NMOS_GSD (pin 1 gate, 2 source, 3 drain), the JEDEC TO-236 order AOS draws (drain alone on one side).
part("Q3", "Transistor_FET", "AO3400A", "AO3400A 30 V N-FET, chemical fuse heater switch", "SOT23", {"1": "FUSE_GQ", "2": "GND", "3": "SCP_HTR"}, "C20917")
# UNDER-VOLTAGE IN HARDWARE: DOUT turns the DISCHARGE switch off, it does not blow the fuse. An under-voltage is recoverable by charging,
# and the SCF9550-30-05's heater is only rated from 10.5 V, which a block with one cell at 2.25 V may already be below. The BQ77207 datasheet's
# own arrangement for this output is an N-channel FET that pulls the main FET's gate line (8.2: "its COUT and DOUT are controlling two
# N-CH FETs to jointly control the CHG and DSG FETs with the monitoring device"; Figure 8-3, RDOUT the gate pull-down). Q5 pulls DSG_G
# to VSS, so the discharge FET's gate sits at or below its source whatever PACK_P does: off, with its body diode still passing charge
# current into the block. Its gate then sees minus PACK_P, at most the charger's 16.8 V against the CSD17570Q5B's +-20 V (TI datasheet,
# VGS). The gauge's DSG pin is then loaded by R18 into ground; its drive is a charge pump whose rise time TI specifies into 4.7 nF
# through 5.1 kohm (SLUSC67B 6.18), and its behaviour held against a resistive load is not specified: a bench item, not a claim.
# A DEPARTURE FROM THE FIGURE IT CITES, RECORDED AT THE FIX-UP OF 26 SEPTEMBER 2026: SLUSEG7D Figure 8-1 pulls down the gate of a
# discharge FET whose source is on the CELL side, so its gate never goes below its source. Q2's source is PACK_P, so under a UV hold
# VGS(Q2) = -V(PACK_P), set by whatever drives the terminal and not by the cells. The margin is 3.2 V at the charger's 16.8 V; a charger
# fault above 20 V during a UV hold exceeds Q2's gate rating, and D1 (VBR 22.2 V minimum, 32.4 V clamping) does not prevent it. The
# barrier is whatever drives the terminal staying under 20 V (the regulation and protection of the kit's charge path on the other
# boards); a gate-source clamp on Q2 would load the gauge's charge pump with a leakage nobody has specified, so it is not added and the
# case is recorded (drafts/r4-decisions.md RP-02, O-9).
# Q5'S OWN LEAKAGE (second fix-up of 26 September 2026, re-review): with DSG on, Q5's drain sits at DSG_G, the charge pump's output
# above PACK_P, and its off-state leakage adds to R19's roughly 1 uA on that pump: IDSS 80 nA maximum at 25 C and 60 V (JCET 2N7002
# datasheet, J Sep 2016, drafts/datasheets/lcsc-C8545.pdf), with no figure above 25 C, and a MOSFET's leakage rises with temperature.
# SLUSC67B specifies the DSG drive only into its 10 Mohm test load, so DSG_G with DSG on is measured at E3's +55 C operating phase
# (O-9), not claimed.
r("R28", "100k", "SEC_DOUT", "GND")
nfet("Q5", "SEC_DOUT", "GND", "DSG_G", "2N7002 60 V N-FET: the second level's under-voltage holds the discharge FET off")
# --- SMBus out, test points, flags
r("R20", "100R", "SMBC_I", "SMBC"); r("R21", "100R", "SMBD_I", "SMBD")
# S-05 (round 4, 26 September 2026, adjudication A07): THE LEAD'S GROUND RAN PARALLEL TO THE SHUNT. Pin 3 was the cell-side GND,
# upstream of R10, so the SMBus lead's ground wire (26 AWG, 350 mm, about 47 mohm) sat in parallel with the 2 mohm shunt and the
# 12 AWG return and took 5 to 8 percent of the pack current (1.0 to 1.4 A at 18 A) that the coulomb counter never saw. TI puts the
# SMBus connector's VSS on the PACK side of the sense resistor (SLUSC67B Figure 21, J2 pin 1 on CHGND). Pin order unchanged,
# as the round-4 brief fixes it for both ends: 1 SMBC, 2 SMBD, 3 GND (the pack side), 4 PRES (now through R22).
# WHAT THIS DOES AND DOES NOT DO (fix-up of 26 September 2026): both returns now sit on the load side of the shunt, so the coulomb
# counter sees every ampere. The lead's ground is STILL in parallel with the 12 AWG return between board P and board E: about 60 mohm
# of 26 AWG and crimps against about 2.5 mohm of 12 AWG and XT60, so it carries roughly 4 percent of the return, about 0.7 A at 18 A.
# That is a harness matter for board E's author and the harness owner (O-5), not a counting error.
part("J_SMB", "Connector_Generic", "Conn_01x04", "SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND(pack side of the shunt) PRES", "XH4", {"1": "SMBC", "2": "SMBD", "3": "PACK_N", "4": "PRES_J"})
for i, net in enumerate(("BTP_INT", "FUSE", "CHG_R", "DSG_R", "SW", "FUSED", "PACK_P", "PACK_N", "SMBC", "SMBD", "FUSE_G", "SEC_DOUT", "SCP_OUT", "FUSE_GQ"), 1): part("TP%d" % i, "Connector", "TestPoint", net, "TP", {"1": net})   # TP11 to TP13 (round 4): the fuse gate, the second level's UV output and the protected cell node, for the commissioning checks; TP14 (fix-up, 26 September 2026): the FET side of JP1, so the arming is verified by continuity TP11 to TP14, COM (black) on TP14 (see JP1)
for i, net in enumerate(("CELL4", "CELL1", "CELL2", "CELL3", "PACK_P", "PACK_N", "FUSED", "SCP_OUT", "SW", "GND"), 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
# ----------------------------------------------------------------- emit (as B15)
POWER = {"GND": ("power", "GND")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's, by reference
STUB = 5.08
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic and independent of the output path: a board regenerates byte for byte (10 Sep 2026)
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
byref = {p["ref"]: p for p in P}

def refs_matching(pred): return [p["ref"] for p in P if pred(p["ref"])]
SECTIONS = [("CELL TAPS, GAUGE BQ4050, SENSE AND SUPPLY FILTERS, THERMISTORS, PTC", ["J_CELL", "U1", "C1"] + ["R%d" % k for k in range(1, 10)] + ["C%d" % k for k in range(2, 10)] + ["R10", "J_TS", "R14", "R15", "R22", "RT1", "C13"]),
            ("FUSE, CHEMICAL FUSE, PROTECTION FETS, GATE NETWORKS, TERMINAL ESD, PACK LEADS", ["W_BP", "W_BN", "F1", "F2", "Q1", "Q2", "R16", "R17", "R18", "R19", "C11", "C12", "D1", "W_P", "W_N"]),
            ("SECOND-LEVEL PROTECTOR BQ77207, FUSE DRIVE, UNDER-VOLTAGE HOLD", ["U2", "R33", "R23", "C14"] + ["R%d" % k for k in range(24, 28)] + ["C%d" % k for k in range(15, 19)] + ["R29", "R30", "R31", "C19", "JP1", "R32", "Q3", "R28", "Q5"]),
           ]
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
SECTIONS.append(("SMBUS OUT, TEST POINTS, FLAGS", [p["ref"] for p in P if p["ref"] not in placed_refs]))
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
_intent.bypass("C1", "U1", "1", "PBI")        # the backup supply on PBI
_intent.bypass("C6", "U1", "32", "BAT_F")     # BAT, the primary supply
_intent.bypass("C8", "U1", "26", "VCC_F")     # VCC, the secondary supply from the pack terminal
_intent.bypass("C14", "U2", "1", "SEC_VDD")   # the second level's VDD filter (CVD, SLUSEG7D Table 8-1), 26 September 2026
import schlayout, time as _time
PAPER, NPAGES, NCOLS, NROWS = schlayout.run(P, SECTIONS, POWER, _intent._I["bypass"], {"date": _time.strftime("%Y-%m-%d")}, os.environ.get("PHASE", ""), 'PCB-P PACK BMS')   # 15 Sep 2026: one A3 page per block, real wiring (32.196)
out = kisch.out
print("layout: %d A3 pages on a %d x %d sheet -> paper %s" % (NPAGES, NCOLS, NROWS, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper %s)\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-P PACK BMS") (date "%s")' % _time.strftime("%Y-%m-%d") + ' (rev "A") (company "MeshSat") (comment 1 "Phase ' + (os.environ.get("PHASE") or "?") + ' schematic (BQ4050 SMBus gauge and protection for the built 4S pack; appendix 32.62), generated by tools/gen_sch_p.py"))\n'
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
# --- decoupling as data (8 Sep 2026, MESHSAT-862 Stage C): the pack board had one active part, so its whole decoupling was the gauge's three
# supply pins (26 September 2026: plus U2's VDD, C14). The cell sense RCs (C2 to C5), the PACK and coulomb-counter filters (C7, C9), U2's CIN ladder (C15 to C18),
# the PTC capacitor (C13), the fuse gate capacitor (C19) and the terminal ESD capacitors (C11, C12) are not decoupling and are not listed (the
# thermistor filter C10 is gone since round 4, F-PK-02); `intent.write` refuses an entry whose capacitor is not on that pin's net.
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
