#!/usr/bin/env python3
"""PCB-A POWER + I/O, phase A22 (MESHSAT-830, 7 Sep 2026): generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_b.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-a-power"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from idc_pads import idc   # the IDC land is a per-board measurement (IDC_PADS), not a default: see idc_pads.py
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, esd, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, text, tps22810, uq, usb_c_recept, wire)
import intent as _intent
# Rails of A22 (appendix 32.55; the record's currents, not measurements): the node from the pack, the 20 V charge bus, the slot rails, the device rail, the PA and HF rails, PoE
# CELL+ CROSSES A AND E AND ITS BUDGET IS SPLIT (20 September 2026). Declaring board E's own CELL+ at 02:16
# made this a cross-board rail, and `check_contracts` said so within the minute: "rail CELL+ crosses A/E and
# its end-to-end budget is not split between them". The split is MEASURED and not guessed: board A's CELL+
# reads a worst drop of 12 mV, 0.08 percent of 14.4 V, and board E's 24 mV, 0.16 percent, so the two boards
# together spend a quarter of a percent of the 2 percent the rail allows. Each declares 0.5 percent, which is
# six times what it measures, and the remaining 1.0 percent (144 mV) belongs to the part nobody has measured:
# the 12 AWG lead, the dock block contacts and the 25 A blade between them. A share is a BAR, so it is set
# from a measurement with margin rather than from an opinion.
_intent.rail("CELL+", 14.4, 10.0, 18.0, "J_CP1", always_on=True, v_work=16.8, converted=False, share=0.005,
             always_on_why="the pack node as it arrives on the dock block contacts; it is switched on board E and in the pack, never here", loads={"F1": 10.0}, note="the pack node on the dock block contacts. S-04, 26 September 2026: the pack current leaves this node through F1, the 25 A blade, into CELL_FUSED and on through the RSR shunt R17 into VBAT, the system node (TI SLUSE66A Figure 10-1). R1 is the 10 R pre-charge trickle and TP14 a test point. Undeclared, dc_drop split the 10 A over every non-passive part on the net and pushed amps through a sense escape, reading 2.21 percent at a 0.5 mm cell and 2.75 at 0.25 against a 2 percent budget: the same correction VIN_RAW carries above, and for the same reason (12 September 2026, A24)")
# S-04, 26 September 2026 (MESHSAT-1357, adjudication A02, W2 F-CH-03): THE LOADS MOVE TO VSYS, TI's own topology
# (SLUSE66A Figure 10-1 and section 10.1). Until today every kit load sat on VBAT behind F1 on the PACK side of
# the charge shunt R17, so the only path from shore to any load ran through the charger's charge-current loop and
# shore could deliver no more than ChargeCurrent into load and pack together: 256 mA at power-on, and nothing a
# crashed host could raise. With the system on the converter side of RSR, the charger's ICHG loop measures the
# pack alone, shore carries the kit up to the input limit without any software, and the 256 mA default is a real
# trickle into the pack. The pack now reaches the system through F1 and R17 in series: CELL_FUSED is the copper
# between them, a series segment of the pack path at the pack's own current.
_intent.rail("CELL_FUSED", 14.4, 10.0, 18.0, "F1", v_work=16.8, converted=False, series_of="CELL+", loads={"R17": 10.0},
             note="S-04, 26 September 2026: the pack node behind the 25 A blade F1 and ahead of the 5 mOhm RSR shunt R17 "
                  "(the BQ25731's battery side, SRN through R148). It carries the pack's charge and discharge current, "
                  "10.0 A typical and 18.0 A peak, and is counted once as a segment of CELL+")
# VBAT IS NOW THE SYSTEM NODE, the BQ25731's VSYS (S-04, 26 September 2026). It is fed from two places: the pack
# through F1 and R17, and the charger's converter through Q10 when shore or vehicle power is present. It is
# declared AFTER CELL_FUSED because a rail that says what feeds it needs that rail declared first (20 September
# 2026, `fed_from`, appendix 32.246). Its declared source is R17 alone, the pack path, because on battery the
# whole load arrives there and that is the worst case for every copper rule that solves this rail; naming Q10 as a
# second source would let dc_drop split the current between two feeds that are never both at full current (and the
# bring-up page printed the list as a Python list). The loads name the power paths that draw from it: two converters are now
# LM5176 stages (F-PR-04), whose input current enters at their buck-side high FETs Q28 and Q32 and not at the
# controllers, and the heater's regulated rail enters at its eFuse U22 (F-PR-06).
_intent.rail("VBAT", 14.4, 10.0, 18.0, "R17", always_on=True, v_work=16.8, converted=False, fed_from="CELL_FUSED",
             always_on_why="the system node (VSYS): nothing on this board switches it. The pack reaches it through the 25 A blade F1 and the RSR shunt R17, opened only by the pack's own BQ4050 FETs and the blade; the charger's converter feeds it from shore through Q10", loads={"U4": 2.0, "Q28": 2.0, "U6": 2.0, "Q32": 2.0, "Q11": 1.5, "U15": 0.3, "U12": 0.2, "U22": 0.65}, note="the 4S system node (VSYS) behind the RSR shunt R17; 10 A continuous, 18 A peak by the pack's rating (32.55)")
# VIN_RAW RECONCILED WITH BOARD E (third fix-up of round 4, 26 September 2026; board E's F-IN-02 on main faf8c981 handed
# this line to this board). Board E declares its VIN_RAW at 6.15 A typical and peak: its LM5069 U6 with R19 = 10 mOhm
# limits the VEHICLE entry at VCL / RS, 4.85 / 5.5 / 6.15 A (ti-lm5069.pdf SNVS452G), and a unit at VCL max passes 6.15 A
# continuously without ever limiting, which is the basis board E uses for both numbers. This board said 8.0 / 10.0 A, a
# figure from before the hot-swap existed, and neither is what reaches the dock. BOARD E ORs ITS PANEL TRACKER ONTO THE
# SAME BUS BEHIND THE HOT-SWAP (ideal diode U4 with Q2, TRK_OUT declared 6.16 A typical and peak: 93 W over 15.1 V), so
# with the panel and the vehicle feeding together the four VIN_RAW contacts of J_DOCK carry both sources, up to
# 6.15 + 6.16 = 12.31 A, and this board's front end can draw it: its 5.7 A ISNS maximum at 20.7 V (VREF and the divider
# at their corners) needs 12.3 A at 10.3 V (efficiency 0.93). Declared on board E's own basis, the most the path carries
# continuously with no limiter acting, from board E's own two declared figures: 12.31 A typical and peak. This TIGHTENS
# the rail against the old 8 / 10 A (the copper of the A32 board was laid for 8 A and is regenerated anyway, O-01), and it
# puts each of the four Preci-Dip 813 contacts at 3.08 A of their "OPERATING CURRENT Max. 3.5 A"
# (v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf) if they share evenly: R4A-N13. Board E's
# own VIN_RAW (L2 to J_BLK) carries the tracker's current on the same copper and declares the vehicle's alone: a board E
# item recorded there (R4A-N12), not changed here. The host's side of the same limit is FW-A16 (IIN_HOST).
_VIN_RAW_A = 6.15 + 6.16
_intent.rail("VIN_RAW", 12.0, _VIN_RAW_A, _VIN_RAW_A, "J_DOCK", loads={"Q2": _VIN_RAW_A - 1.0, "C11": 0.5, "C12": 0.5}, budget=0.02, share=0.015, v_work=36.0, converted=False,
             always_on=True, always_on_why="shore and vehicle input arriving over the dock behind board E's own 10 A blade and ideal diode; this board does not switch it, it consumes it", note="shore, vehicle and panel input from E6 over the dock: board E's vehicle entry (LM5069 U6, 6.15 A at VCL max, 10 A fuse) and its panel tracker (TRK_OUT, 6.16 A) ORed onto one bus, 12.31 A together (third fix-up of round 4, 26 September 2026, reconciled with board E's F-IN-02); the current enters the front end at Q2's drain and the input caps (the LM5176 U2 draws only its bias: a load named U2 put 8 A into two QFN pins and read 3.3 percent, 32.69)")
# LOADS DECLARED 13 September 2026. This rail carried none and dc_drop guessed, putting 6 A into U3, whose
# only pads on this net are the charger's 0.13 and 0.20 mm VBUS SENSE pins. The real path is the whole charge
# current through R16, the 10 mOhm 2512 input-current shunt, and on into the charger; U3's pins sense the bus
# and carry nothing. This is the CELL+ defect of 12 September in a second place.
# THE SOURCE IS THE POWER PATH, NOT THE PART THAT CONTROLS IT (13 September 2026, MESHSAT-862). These three
# rails named their LM5176 CONTROLLER as the source, so `dc_drop` held that chip's pads at 0 V and took the
# rail's whole current out of them. VBUS20's 6 A left through pin 12/13, the output SENSE pins, and 2.90 A of
# it went down a locked 0.200 mm escape stub: ratio 3.90 against IPC, and no copper anywhere would have fixed
# it because the current was never meant to be there. It is the CELL+ defect of 12 September and the VBUS20
# load defect of this morning for a third time, now on the source side. An LM5176 stage's output node is its
# ISNS shunt: the switch node goes through the inductor to the FETs, out through the shunt, and only then is
# it the rail. R11, R65 and R71 are those shunts (R12, R122 and R72 are the CS resistors, which are not).

# WHERE THE EFFICIENCIES COME FROM (16 September 2026, rule THM-001). A converter's loss is the only heat this
# board makes that is not I2R in its own copper, and no rail declared one, so `thermal.py` could put no number
# on the board at all. Every figure below is read off the part's own datasheet at the conditions that datasheet
# states, and every one is taken at or BELOW the low end of what it plots, because a lower efficiency is a
# higher loss and a dissipation figure is only useful as a floor.
#   LM5176 (U2, U13, U15, U19): figures 6-1 and 6-2, VOUT 12 V, 300 kHz, 4.7 uH, IOUT 5 A. The efficiency axis
#   of 6-1 runs 93 to 98 percent over a 5 to 50 V input and 6-2 runs 80 to 96 against load at 9, 12 and 24 V
#   in. Our four buck-boost stages run at that switching frequency into 12 to 20 V at 2 to 6 A, which is
#   inside those conditions, and 0.93 is the low end of the first plot.
#   LM5176 in the PoE stage (U16) is 14.4 V into 54 V, a 3.75 to 1 boost, which is OUTSIDE everything the
#   datasheet plots, so it takes 0.88: the direction is conservative and the number is not read off a curve
#   that does not cover it.
#   AP64500 (U4 to U7): figure 2, VIN 12 V, VOUT 5 V, 3.6 uH, 500 kHz, the plot this board's slot rails sit on
#   almost exactly (14.4 V in, 5.1 V out). Its efficiency axis tops at 90 percent, so 0.90 is taken.
#   TPS62933 (U12): 3.3 V at 0.6 A from the pack node, a small buck at a light load, where the datasheet's own
#   light-load discussion is about PFM. 0.88 is below anything it claims.
# NONE OF THESE IS A MEASUREMENT OF THIS BOARD. They are the parts' published figures used as a floor, and the
# junction temperature this rule really wants needs the envelope's maximum ambient, which is owner decision 34.
_intent.rail("VBUS20", 20.0, 6.0, 8.0, "R11", loads={"R16": 6.0}, switch="U2", efficiency=0.93, fed_from="VIN_RAW", note="the charge bus, BQ25731 up to 8 A; the stage's output is its ISNS shunt R11, not the controller U2")
for _n, _sh in (("1", "R31"), ("2", "R35"), ("3", "R39")):
    # THIS BOARD'S SHARE of a rail that crosses to board B (16 September 2026). The cross-board contract
    # asked for a share on seven rails and no board declared one, so each half was judged against the WHOLE
    # end-to-end budget and the two halves could sum past it with both passing: the +5V_D8 finding of this
    # morning, generalised. This board regulates the rail and its copper runs from the INA226 shunt to the
    # VH header, measured at 0.07 percent of 5.1 V; board B carries it across 245 mm to a module receptacle
    # at 2.5 A and takes the other 1.5 points of the 2 percent.
    _intent.rail("+5V_S%s" % _n, 5.1, 2.5, 5.0, _sh, loads={"J_5V_S%s" % _n: 5.0}, budget=0.02, share=0.005, fed_from="VBAT",
                 switch={"1": "U4", "2": "U5", "3": "U6"}[_n], efficiency=0.90,
                 note="one CM5 slot with its cooler fan; 5 A peak at the module; the rail net starts at the "
                      "INA226 shunt. This board's share of the 2 percent is 0.5 point, measured 0.07")
# F-PR-04, 26 September 2026: the device rail's converter is an LM5176 stage now, not an AP64500. W2 found this
# rail declared at 6.0 A peak on a 5 A part (VERIFIED) and summed its loads to the same 6.0 A (INFERRED); D-12 adds
# the Glenair host port's own eFuse U32 (0.9 A limit) behind it, so the peak is 6.9 A. The LM5176 stage's average
# current loop holds 43 to 57 mV across its 6 mOhm ISNS shunt R43 (SNVSAI1D, VSNS), 7.2 to 9.5 A, above the 6.9 A
# peak and below the JST-VH lead's 10 A. The loads now name board A's own two eFuses as well as the lead to B.
_intent.rail("+5V_DEV", 5.0, 4.0, 6.9, "R43", loads={"J_5V_DEV": 3.2, "U23": 0.5, "U32": 0.3}, budget=0.02, share=0.005, switch="U7", efficiency=0.90, fed_from="VBAT", note="the USB devices, the LimeSDR bay and the RockBLOCK behind their switches, the D8 mezzanine behind U23 and the wall host port behind U32; the net starts at the ISNS shunt R43. 9 September 2026 (ARCH-PCB-B-IOHA): +0.8 A because B16's three hub banks had to leave the slot rails. 26 September 2026 (F-PR-04, D-12): the converter is an LM5176 stage with a 7.2 A minimum average limit, and the Glenair port's 0.9 A takes the peak to 6.9 A.")
# LOADS DECLARED 13 September 2026, apportioning the declared 0.3 A rather than measuring it: this is logic,
# tens of milliamps a part, and the biggest single draw is the gated 3.3 V leaving on the mezzanine harness.
_intent.rail("+3V3", 3.3, 0.3, 0.6, "L7", budget=0.03, share=0.015, switch="U12", efficiency=0.88, fed_from="VBAT",
             loads={"J_MEZZ1": 0.10, "U8": 0.03, "U9": 0.03, "U10": 0.03, "U11": 0.03,
                    "U14": 0.02, "U17": 0.02, "U26": 0.02, "U27": 0.01, "U28": 0.01}, note="this board's logic (two PCA9555, five INA226, the LTC2954, the controllers' VCC pins: tens of mA each; the 1 A of the first intent was a placeholder, 32.69); the net starts at the TPS62933 inductor L7")
_intent.rail("+13V8_PA", 13.8, 5.0, 6.0, "R55", loads={"J_PA": 6.0}, switch="U13", efficiency=0.93, fed_from="VBAT", note="the RA30H1317M1 on the face plate")
_intent.rail("+12V_HF", 12.0, 1.0, 2.0, "R65", budget=0.03, loads={"J_HF": 1.0}, switch="U15", efficiency=0.93, fed_from="VBAT",
             note="the QMX")   # the whole rail leaves at J_HF for the HF unit in the lid tray
_intent.rail("+54V_POE", 54.0, 0.3, 0.6, "R71", loads={"J_54V": 0.3}, budget=0.02, share=0.005, switch="U16", efficiency=0.88, fed_from="VBAT",
             note="the TPS23861 PSE on B16")   # the whole rail leaves at J_54V on the VH lead to B
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers
LIBCACHE = {}

# ----------------------------------------------------------------- the design
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "RS": "Resistor_SMD:R_1206_3216Metric", "C": "Capacitor_SMD:C_0603_1608Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C100u": "Capacitor_SMD:C_1206_3216Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMB", "TVSC": "Diode_SMD:D_SMC",   # SMBJ is DO-214AA (SMB), SMCJ is DO-214AB (SMC): never one key for both
 "F1812": "Fuse:Fuse_1812_4532Metric", "F2920": "Fuse:Fuse_2920_7451Metric",
 "HUB": "Package_SO:SSOP-28_5.3x10.2mm_P0.65mm", "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
 "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT238": "Package_TO_SOT_SMD:SOT-23-8", "SOT23": "Package_TO_SOT_SMD:SOT-23",
 "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
 "IDC18": idc("2x09"), "IDC40": idc("2x20"), "IDC14": idc("2x07"), "IDC16": idc("2x08"),
 "PICO10": "Connector_Molex:Molex_PicoBlade_53047-1010_1x10_P1.25mm_Vertical",
 "USBA": "Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal", "USBC": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "USBCP": "Connector_USB:USB_C_Plug_Molex_105444", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
 "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "JP3": "Jumper:SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm",
 "TP": "TestPoint:TestPoint_Pad_D1.5mm", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "XH10": "Connector_JST:JST_XH_B10B-XH-A_1x10_P2.50mm_Vertical",
 "CELL": "Battery:BatteryHolder_Keystone_1042_1x18650", "XT60": "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical", "POGO": "meshsat:PogoPins_2x4", "FUSE": "Fuse:Fuseholder_Blade_Mini_Keystone_3568", "CHG": "Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm", "PROT": "Package_SON:WSON-6_1.5x1.5mm_P0.5mm",
 "BOOST": "Package_DFN_QFN:Texas_RWU0007A_VQFN-7_2x2mm_P0.5mm", "GAUGE": "Package_SON:Texas_S-PDSO-N12", "SOT223": "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX", "RS10m": "Resistor_SMD:R_2512_6332Metric",
 "QFN11": "Package_DFN_QFN:Texas_VQFN-RNR0011A-11", "L6030": "Inductor_SMD:L_Coilcraft_XAL6030-XXX", "C1210": "Capacitor_SMD:C_1210_3225Metric",
 "RQQ11": "meshsat:Texas_RQQ0011A_VQFN-HR-11_2.5x3mm", "RQM29": "meshsat:Texas_RQM0029A_QFN-29_4x4mm", "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "DSG8": "Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm",
 "TSOT8": "Package_TO_SOT_SMD:TSOT-23-8", "QFN64": "Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm", "L1010": "Inductor_SMD:L_Coilcraft_XAL1010-XXX", "L4030": "Inductor_SMD:L_Coilcraft_XAL4030-XXX",
 "POGO12": "meshsat:PogoPins_2x6", "MMPIN": "meshsat:Mill-Max_0858_power_pin", "SMAV": "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical", "SMPMAX": "meshsat:Radiall_SMPMAX_R222M00720",
}
kisch.configure(fp=FP)   # the engine needs the tables before the first part
P = kisch.P                           # one list, shared with the engine (not a copy)    (ref, lib, symbol, value, footprint, nets{pin: net}, lcsc)

# DECLARED 16 September 2026, the last rail-shaped net on this board that the intent file did not carry. It
# leaves the board, so its only load here is the connector it leaves through; the consumers are board D's and
# are declared there. Without this line the return-path gate judged a 5 V rail as a signal net.
_intent.rail("+5V_D8", 5.0, 1.0, 2.0, "U23", converted=False,
             source_ic="U23 is a TPS2596 eFuse: its OUT pin IS the power path, which is what an eFuse is",
             loads={"J_MEZZ_PWR1": 1.0}, budget=0.06, share=0.04,
             note="BUDGET FROM THE TIGHTEST CONSUMER'S DATASHEET, 16 September 2026, replacing a number this project had only asserted. The consumers of this rail sit on board D and the tightest of them is the PCM2912A USB codec, whose recommended operating VBUS is 4.35 V minimum (v2/vendor/ti/ti-pcm2912a.pdf, Recommended Operating Conditions); the next is the CP2102N, whose 3.3 V regulator leaves regulation below VREGIN 4.1 V (v2/vendor/silabs/silabs-cp2102n.pdf). The source is board A's eFuse output on the 5.0 V device rail, and at a 2 percent source tolerance its worst case is 4.90 V, so the IR drop that keeps the codec in its recommended range is 550 mV, 11 percent. The declared budget is 6 percent, 300 mV, which leaves the codec at 4.60 V with 250 mV in hand. The 3 percent it replaces was derived from nothing and was tighter than the parts ask for. THIS BOARD'S SHARE is 4 of the 6 points, because the long copper is here: the eFuse "
                  "sits at case (90, 66) and the mezzanine header at (-8, -18), about 129 mm apart, and the "
                  "route measures 134 mV at 1.0 A, 2.68 percent. Board D's own half measures 0.58. "
                  "The APRS board's 5 V behind the eFuse U23 (ILM 453R, 2.0 A), leaving on the mezzanine "
                  "JST-VH. Board D declares the same rail with its own consumers. ONE CONDUCTOR, ONE BUDGET "
                  "(16 September 2026): board D declares 3 percent end to end with its reason, and this board "
                  "carries the half from the eFuse to the connector, so its share is 1.5. Until today each "
                  "board measured its own half against the whole, and this half alone reads 2.68 percent, "
                  "which is the finding: A's copper is spending nearly all of a budget it shares with D")
def usb_c_plug(ref, dp, dm, vbus, cc):
    # captive USB-C pigtail (4-wire cable with the Rp resistor in the plug) on a JST-PH 4-pin header: VBUS, D-, D+, GND
    part(ref, "Connector_Generic", "Conn_01x04", "USB-C pigtail header (JST-PH 2.0): VBUS D- D+ GND", "PH4", {"1": vbus, "2": dm, "3": dp, "4": "GND"})
def tps2065(ref, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": "+5V_M1", "4": en, "1": out, "3": flt, "2": "GND"})   # A19: the channels hang on rail M1
def ina219(ref, inp, inn, a0, a1): part(ref, "Sensor_Energy", "INA219AxDCN", "INA219AIDCN", "SOT238", {"1": inp, "2": inn, "3": "GND", "4": "+3V3", "5": "SCL", "6": "SDA", "7": a0, "8": a1}, "C138024")

# ================================================================ A22 (7 Sep 2026, appendix 32.52, 32.55, 32.56): the 14.4 V node of the BB-2590/U, the wide-range front end,
# the BQ25731 charger, per-slot 5 V rails for three CM5, the PA and HF rails, the 54 V PoE rail, the USB-C PD outlet, the monitor and heater switches, hardware EMCON gates,
# eleven blind-mate RF sites, the D8 mezzanine as a USB device set. Every pin number below is read from the sheet filed under v2/vendor/ (ti/, power/) and the LCSC codes from 32.54.
# Nets: CELL+ is the pack node (four 9 A dock pins), VBAT the fused node every converter runs from, VIN_RAW the 9 to 36 V vehicle and shore input up the dock signal contacts,
# VBUS20 the 20 V charge bus, +5V_S1..3 the slot rails, +5V_DEV the USB device rail, +3V3 this board's logic, +13V8_PA, +12V_HF, +54V_POE, VMON, VHEAT, +5V_D8.
FP.update({
 "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "IDC26": idc("2x13"), "IDC16": idc("2x08"), "IDC10": idc("2x05"),
 "HTSSOP28": "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm", "QFN32_04": "Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.65x2.65mm",
 "SO8EP": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", "QFN24": "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm", "SOT583": "Package_TO_SOT_SMD:SOT-583-8", "VSSOP10": "Package_SO:VSSOP-10_3x3mm_P0.5mm", "DDA8": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm",
 "TSSOP24": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "PPAK": "Package_SO:PowerPAK_SO-8_Single",
 "L1010": "Inductor_SMD:L_Coilcraft_XAL1010-XXX", "L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX", "L6030": "Inductor_SMD:L_Coilcraft_XAL6030-XXX", "L4030": "Inductor_SMD:L_Coilcraft_XAL4030-XXX",
 "C1210": "Capacitor_SMD:C_1210_3225Metric", "RS2512": "Resistor_SMD:R_2512_6332Metric", "PIN5": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
 # 26 September 2026 (MESHSAT-1357 round 4): the LM5176 bootstrap diodes (SOD-123, pad 1 the cathode band) and the
 # heater buck's inductor (Coilcraft XAL4040, v2/vendor/coilcraft/coilcraft-xal40xx-series.pdf). Both lands are
 # KiCad 9 library footprints; neither is drawn here.
 "SOD123": "Diode_SMD:D_SOD-123", "L4040": "Inductor_SMD:L_Coilcraft_XAL4040-XXX",
 # round 4 fix-up: the LM5176 stages' local bulk, the hybrid polymer board E already carries (KiCad 9 library land)
 "CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL10": "Capacitor_SMD:CP_Elec_10x10",
 # fourth fix-up (R4A-N15): TI's DSK0010A (TPS37, SNVSBJ1E page 42: 10 x 0.6 x 0.25 mm on a 0.5 mm pitch, 2.3 mm row
 # to row, pad 11 1.2 x 2.0 mm); the KiCad 9 land's pads sit at +-1.2125 mm with the same 1.2 x 2 mm pad 11
 "WSON10": "Package_SON:WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm",
})
def nfet(ref, value, g, d, s, fp="PPAK", lcsc=""):
    """PowerPAK SO-8 single (Vishay 71655; the KiCad land): pads 1, 2, 3 = source, 4 = gate, 5 = the drain tab (five pads named 5). A22 round 1 (7 Sep 2026 05:30)
    found the three-pin Q_NMOS_GDS map putting the gate and drain nets on source pins: the symbol is a five-pin connector so every pad carries its net."""
    part(ref, "Connector_Generic", "Conn_01x05", value, fp, {"1": s, "2": s, "3": s, "4": g, "5": d}, lcsc)
def vh2(ref, value, a, b="GND"): part(ref, "Connector_Generic", "Conn_01x02", value, "VH2", {"1": a, "2": b}, "C274411")
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
# --- pack node over the dock block (32.56): four CELL+ pins, four return pins, the pre-charge pin, then the 25 A blade to VBAT (the 2590 gives 10 A continuous, 18 A peak)
for k in range(1, 5):
    part("J_CP%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, CELL+ (Mill-Max 0858 class, dock block)", "MMPIN", {"1": "CELL+"})
    part("J_CN%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, pack return (Mill-Max 0858 class, dock block)", "MMPIN", {"1": "GND"})
part("J_PRE1", "Connector", "Conn_01x01_Pin", "pre-charge pin, longer, mates first (32.24 AX)", "MMPIN", {"1": "PRECHG"}); r("R1", "10R 2W 2512", "PRECHG", "CELL+", "RS2512")
# S-04, 26 September 2026: the blade now sits between the pack node and the RSR shunt, so VBAT (the system node,
# the charger's VSYS) is reached through F1 and R17 in series. The fuse's position in the pack path is unchanged:
# it is still the first element every pack ampere meets on this board, charge and discharge.
part("F1", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder): pack node to the RSR shunt", "FUSE", {"1": "CELL+", "2": "CELL_FUSED"})
# C1 and C2 are 47 uF, not the 100 uF the node was drawn with. 100 uF 25 V does not exist in a
# 1206 land with stock from any maker (47 uF is the ceiling), so the 200 uF nominal on VBAT was
# never buildable, and after DC-bias derating at 14.4 V neither number was ever close to its
# label. The pair is 94 uF nominal now. If the node needs more real bulk than that it wants an
# SMD aluminium can rather than ceramics, which is a placement change and an owner decision.
# S-04, 26 September 2026: C1, C2 and C3 now sit on the BATTERY side of the charge shunt, CELL_FUSED. TI asks for
# "minimum 20-uF MLCC capacitors after the charge current sense resistor for best stability" (SLUSE66A 10.2.2.5,
# and the 2 x 10 uF plus 0.1 uF at BATT in Figure 10-1), and until today that side was exactly where these three
# were, on the old VBAT. They are about 25 uF effective at 16.8 V. The VSYS side keeps its own 50 uF effective (the
# same section): C23 to C25 at Q10 and the input capacitors of every converter on VBAT. D1 stays on VBAT.
c("C1", "47u 25V", "CELL_FUSED", "GND", "C100u"); c("C2", "47u 25V", "CELL_FUSED", "GND", "C100u"); c("C3", "10u 25V 1210", "CELL_FUSED", "GND", "C1210"); kisch.tvs("D1", "SMCJ18A (VBAT clamp)", "VBAT", "GND", "TVSC", "C374030")   # TRN-001 / S-09 (ts-tvs, 26 Sep 2026): a one-way part, drawn K/A by kisch.tvs() (Device:D_Zener, K pin 1 on VBAT, A pin 2 on GND; direction from the part number, recorded in the intent under "clamps"); nets, value, land and code as before (Littelfuse C374030, v2/vendor/power/littelfuse-smcj-series-tvs.pdf)
part("J_DOCK", "Connector_Generic", "Conn_01x12", "spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1-4 VIN_RAW (9 to 36 V from E6), 5-7 GND, 8 SHORE_INHIBIT, 9-10 USB of E6's sensor controller, 11 GND, 12 spare", "POGO12",
     {"1": "VIN_RAW", "2": "VIN_RAW", "3": "VIN_RAW", "4": "VIN_RAW", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "DOCK_SPARE"})
# --- main power control LTC2954-1 (ltc2954.pdf): the panel MAIN button, EN to every converter's enable (RAIL_EN), INT = shutdown request, KILL from the panel controller through Q1
# S-08, 26 September 2026 (MESHSAT-1357; W2 F-SQ-02 and F-SQ-03, W5-F2, F5, F6, F15, F16, W6-F15). Six changes to
# this block, each against the LTC2954 sheet held at v2/vendor/power/ltc2954.pdf (2954fb):
#  1. THE INDUSTRIAL GRADE. LTC2954CTS8-1 is 0 to 70 C and the envelope is -20 to +40 C; LTC2954ITS8-1 is -40 to
#     85 C, the same TS8 package, the same pin configuration (one TS8 pinout for both grades) and the same marking
#     LTCJH (order information table). LCSC C580654 = LTC2954ITS8-1#TRMPBF, Analog Devices, TSOT-23-8, read back
#     from the JLCPCB parts API on 26 September 2026 (drafts/jlc/jlc-C580654.json), stock 195 against 5 needed.
#  2. KILL WITHIN ITS ABSOLUTE MAXIMUM. KILL is rated -0.3 to 7 V and was pulled to VBAT (up to 16.8 V). R4 now pulls
#     it to +3V3, the rail this controller enables: the sheet's own arrangement ("connect to a low voltage output
#     supply"). +3V3 rises within milliseconds and KILL is blanked for 400 to 650 ms after turn-on, so KILL is high
#     long before the blanking ends; and if +3V3 collapses the kit switches itself off.
#  3. RAIL_EN WITHIN THE TPS62933's EN RATING. U12's EN is rated -0.3 to 6 V (5.5 V recommended, SLUSEA4D 8.1 and
#     8.3) and R2 pulled it to VBAT. R2 over R184 (100k over 39k) puts 4.71 V on it at 16.8 V, 5.05 V at the SMCJ18A's
#     18 V standoff and 2.81 V at 10 V, all above VEN_RISE 1.28 V maximum.
#  4. PDT IS NO LONGER FLOATING. A floating PDT forces the kit off after 52 to 82 ms of MAIN held (tPD,MIN), which an
#     ordinary press reaches. C152 adds tPDT = 6.4 s per uF: 680 nF gives about 4.4 s typical (about 3.3 to 6.0 s over
#     the 2.4 to 3.6 uA PDT current and the 10 percent capacitor), the four-second override convention.
#  5. PI_SHDN_REQ: INT DRIVES THE NET DIRECTLY, AND THE NET HAS ONLY OPEN-DRAIN DRIVERS BY CONTRACT. INT is open
#     drain and active low (2954fb pin functions). R3 is 10 k so the idle level is a clean high against the
#     RP2040's 50 to 80 k reset pull-down. The net is NOT pulled up by R3 alone: board B hangs one 2N7002 level
#     stage per compute slot on it (gen_sch_b.py level(), drain on PI_SHDN_REQ, a 10 k pull-up to the slot's
#     3.3 V on the source side), and each powered slot feeds up to 0.33 mA into a low net through the channel or
#     the body diode. With R3 and three slots INT sinks about 1.2 mA, under the 3 mA at which 2954fb specifies
#     VINT(VOL) 0.11 V typical and 0.4 V maximum, so the net reads 0.4 V at worst against the RP2040's 0.8 V VIL.
#     A 1 k series resistor tried in round 4 (R185) put the net at 0.8 to 1.0 V with two or three slots powered
#     (review A, blocking item 1) and is gone. A series resistor small enough to keep a valid low (about 220 R or
#     less) still lets a panel driving the net high push about 13 mA into INT, and INT has no current rating to
#     hold that against (2954fb absolute maximum ratings list INT only as -0.3 to 10 V). So the protection is the contract, which board C keeps: the
#     panel's GPIO18 is open drain in firmware (output value 0, only the output enable toggles; I-03, FW-A10).
#  6. PI_KILL CANNOT BE LIFTED BY A POWERED SLOT. R5 is 1.0 k, not 100 k: three slots back-driving through board B's
#     level stages (10 k pull-ups and a body diode each, W5-F5) hold the net at about 0.65 to 0.7 V, under Q1's
#     1.0 V minimum threshold. The panel then sources 3.3 mA to kill; Q1 needs only 33 uA through R4 to take KILL low.
ic("U1", 8, "LTC2954ITS8-1 push-button on/off controller, -40 to 85 C", "TSOT8", {"1": "VBAT", "2": "MAIN_PB", "3": "NC", "4": "GND", "5": "PI_SHDN_REQ", "6": "RAIL_EN", "7": "MAIN_PDT", "8": "KILL"}, "C580654")
c("C4", "1u", "VBAT", "GND"); r("R2", "100k", "RAIL_EN", "VBAT"); r("R184", "39k 1%", "RAIL_EN", "GND", lcsc="C23153")
r("R3", "10k", "PI_SHDN_REQ", "+3V3"); r("R4", "100k", "KILL", "+3V3")   # R185 (round 4) removed in the fix-up: see item 5
c("C152", "680n", "MAIN_PDT", "GND", lcsc="C107067")   # YAGEO CC0603KRX7R7BB684, 680 nF 16 V X7R 0603 (JLCPCB API, 26 Sep 2026); PDT is rated 2.7 V
part("Q1", "Transistor_FET", "2N7002", "2N7002: panel controller high = pull KILL low = power off (1 G, 2 S, 3 D)", "SOT23", {"1": "PI_KILL", "2": "GND", "3": "KILL"}); r("R5", "1k", "PI_KILL", "GND")
part("J_MAINSW", "Connector_Generic", "Conn_01x02", "JST-XH 1x2 socket: the MAIN button lead from the panel, PB and GND", "XH2", {"1": "MAIN_PB", "2": "GND"}, "C265283")
# --- LM5176 four-switch buck-boost stages (lm5176-datasheet.pdf, HTSSOP-28 PWP; Vref 0.8 V; pins: 1 EN/UVLO 2 VIN 3 VISNS 4 MODE 5 DITH 6 RT/SYNC 7 SLOPE 8 SS 9 COMP 10 AGND 11 FB 12 VOSNS
#     13 ISNS- 14 ISNS+ 15 CSG 16 CS 17 PGOOD 18 SW2 19 HDRV2 20 BOOT2 21 LDRV2 22 PGND 23 VCC 24 BIAS 25 LDRV1 26 BOOT1 27 HDRV1 28 SW1, pad 29)
# The stages' local bulk (round 4 fix-up, (3) in the helper below): Panasonic ZK series hybrid polymer, one series
# sheet held at v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf (01-Apr-22, "Characteristics list": capacitance
# +-20 percent, ESR maximum at 100 kHz and +20 C, 4000 h at 125 C, -55 to +125 C); codes read back from the JLCPCB
# parts API on 26 September 2026 (drafts/jlc/jlc-<model>.json). Value, land, LCSC code. Each part's RATED RIPPLE
# CURRENT (the same list, 100 kHz and +125 C; the frequency correction is 1.00 from 100 kHz up for 100 uF and more)
# is the second fix-up's check, drafts/scripts/bulk_ripple.py: V101 1.7 A, E151 1.8 A, E471 and V331 2.8 A.
BULK_ZK = {
    "V101": ("100u 35V Panasonic EEHZK1V101XP hybrid polymer (7.7 mm)", "CPOL63", "C454360"),   # ESR 35 mOhm max, D8 6.3 x 7.7; board E carries it
    "E151": ("150u 25V Panasonic EEHZK1E151XP hybrid polymer (7.7 mm)", "CPOL63", "C542453"),   # ESR 30 mOhm max, D8 6.3 x 7.7
    "E471": ("470u 25V Panasonic EEHZK1E471P hybrid polymer (10.2 mm)", "CPOL10", "C242138"),   # ESR 20 mOhm max, G 10 x 10.2
    "V331": ("330u 35V Panasonic EEHZK1V331P hybrid polymer (10.2 mm)", "CPOL10", "C278516"),   # ESR 20 mOhm max, 2.8 A rms, G 10 x 10.2 (the E471's land); stock 6,551 (JLCPCB API, 26 Sep 2026)
}
def lm5176(p, uref, vin, vout, en, rfb_top, lref, lval, fet, fet_lcsc, refs, cs_filter, isns_filter, isns="10m", rcs="5m", bias=None,
           rfb_val="10k 1%", cout="10u 50V X7R 1210", cin="10u 50V X7R 1210", out_budget=None,
           cslope=None, boot_diodes=None, en_div=True, isns_lcsc="", cout_lcsc="", comp=None, bulk=(), bulk_part="V101", cout_extra=(), l_lcsc="",
           bias_cap=None, css=("47n", ""), cout_pre=(), vin_block=None, visns_r=None):
    """one stage with prefix p: refs = (Q_bh, Q_bl, Q_bsl, Q_bsh, R_fb_top, R_fb_bot, R_rt, C_slope, R_comp, C_comp, C_comp2, C_ss, C_vcc, C_boot1, C_boot2, R_isns, R_cs, R_pgood, R_en_top, R_en_bot, Cin1, Cin2, Cout1, Cout2, Cout3, R_mode)
    cslope = (value, lcsc) of the SLOPE capacitor; boot_diodes = (D for BOOT1, D for BOOT2). Both are REQUIRED
    (26 September 2026): a stage without them cannot run, see the comment below. en_div=False drives EN/UVLO
    straight from the enable line (no 62k/10k divider, whose 0.46 V from a 3.3 V logic high never reaches VEN(OP),
    W2 F-SQ-04); R_en_top and R_en_bot are then None.
    comp = ((Rc1 value, lcsc), (Cc1 value, lcsc), (Cc2 value, lcsc)), REQUIRED since the round 4 fix-up of
    26 September 2026: the stage's own compensation (see (3) below). bulk = references of local hybrid-polymer
    bulk capacitors on the output, all of the part BULK_ZK[bulk_part]; cout_extra = references of further output
    ceramics of the stage's own cout part; both only where the stage's loop design (and, since the second fix-up,
    its bulk's ripple current) asks for them. bias_cap = the reference of the BIAS pin's own 0.1 uF bypass, REQUIRED
    since the second fix-up (SNVSAI1D 9.1: "Place the BIAS bypass capacitor close to the controller IC, between the
    BIAS and PGND pins. A 0.1-uF ceramic capacitor is typically used"; no stage had one).
    css = (value, lcsc[, land key]) of the soft-start capacitor, per stage since the third fix-up of 26 September 2026 (the second
    re-review's blocking item 2: one 47 nF for seven stages whatever their output capacitance and whatever feeds them).
    cout_pre = references of output ceramics of the stage's own cout part on <p>_OUT, BEFORE the ISNS shunt (SNVSAI1D
    9.1: "When using the average current loop, divide the overall capacitor (CIN or COUT) between the two sides of
    the sense resistor to ensure small cycle-by-cycle ripple"; Figure 10-1 draws COUT on both sides of RISNS).
    vin_block = (diode ref, capacitor ref, capacitor value, capacitor lcsc, capacitor land key): a series blocking
    diode from the input rail to the VIN pin (pin 2) with the pin's own capacitor after it, REQUIRED where BIAS is not
    the input rail (third fix-up, R4A-N11): SNVSAI1D 7.3.2, "use a series blocking diode between the input supply and
    the VIN pin (Figure 7-1). This prevents VCC from back-feeding into VIN through the body diode of the VCC
    regulator", and 9.1, "When using external BIAS, use a diode between input rails and VIN pins to prevent reverse
    conduction when VIN < VCC". VISNS (pin 3) stays on the power stage's input rail, which is what it senses.
    visns_r = (ref, value, lcsc): a series resistor from the input rail to VISNS (pin 3), for a stage whose input can
    exceed 40 V (fourth fix-up of 26 September 2026, the third re-review's minor item 3): SNVSAI1D 7.3.7, "For
    application where input voltage is higher than 40 V, a 2-kOhm resistor in series with the VISNS pin is required
    as shown in Figure 8-1"; Figure 8-1 draws the 2 k with no capacitor at the pin, so none is declared as pin 3's
    bypass when it is given."""
    qbh, qbl, qsl, qsh, rft, rfb, rrt, csl, rco, cco, cco2, _css_ref, cvcc, cb1, cb2, risns, rcs_, rpg, ret, reb, ci1, ci2, co1, co2, co3, rmd = refs
    # TWO DEFECTS OF THIS HELPER, FOUND 26 September 2026 (MESHSAT-1357 round 4) while building the two new stages
    # of F-PR-04, and fixed here for all seven stages because the helper is one place. Source: TI SNVSAI1D (August
    # 2021), v2/vendor/ti/lm5176-datasheet.pdf.
    # (1) NO BOOTSTRAP DIODES. The LM5176 has none inside: the functional block diagram (7.2) draws BOOT1 and BOOT2
    #     to the gate drivers only, and 7.3.14 says "The CBOOT1 and CBOOT2 capacitors are charged through external
    #     Schottky diodes connected to the VCC pin as shown in Figure 8-1". Without them neither high-side FET is
    #     ever driven: in buck mode HDRV2 "remains continuously on" and HDRV1 switches, both from bootstrap
    #     capacitors that nothing charged. Every LM5176 stage on this board as drawn could not have started. The
    #     diode is a BAT46W-7-F (Diodes Incorporated DS30044 Rev. 20-2, drafts/datasheets/diodes-bat46w.pdf):
    #     100 V, 150 mA continuous, 350 mA repetitive, SOD-123, -55 to +125 C; LCSC C83152 (JLCPCB API 26 Sep 2026).
    #     Its reverse voltage is the switch node's height: at most 54 V on the PoE stage's BOOT2 and 36 V on the
    #     front end's BOOT1, both under 100 V. Its average current is the FET's gate charge times the switching
    #     frequency, about 80 nC x 206 kHz = 16.5 mA for a CSD18510Q5B at the 7.35 V VCC (SLPS632), under 150 mA.
    #     (RT 40.2 k sets 206 kHz by Equation 5, 180 to 232 kHz over the fSW(1) spread; the "300 kHz" this helper
    #     wrote on RT until the round 4 fix-up was TI's example frequency, never this board's.)
    # (2) THE SLOPE PIN HAD A RESISTOR. The pin table says "A capacitor connected between the SLOPE pin and AGND
    #     provides the slope compensation ramp", and 8.2.2.8 sizes it as CSLOPE = gmSLOPE x L / (RSENSE x ACS) with
    #     gmSLOPE 2 uS and ACS 5 (Equation 26). A 30 k resistor turns the adaptive slope current into a DC level,
    #     so no stage had slope compensation, which valley-mode buck below 50 percent duty and peak-mode boost above
    #     it both need against subharmonic oscillation. Each call now names its capacitor: the E12 value at or below
    #     the dead-beat value, which gives a slightly larger ramp, the direction TI's own example takes (220 pF for
    #     a computed 235 pF).
    # (3) ONE COMPENSATION SET FOR SEVEN STAGES (review A, blocking item 2, round 4 fix-up). Every stage carried
    #     Rc1 10 k, Cc1 10 nF and Cc2 100 pF whatever its inductor, sense resistor, output voltage and output
    #     capacitance. Equation 44 solved for the bandwidth puts that set's crossover in the hundreds of kHz on the
    #     5 V stages' local ceramics, against a 206 kHz switching frequency and TI's guidance (8.2.2.14) of the
    #     smaller of fRHP / 3 and Fsw / 20, about 10 kHz. On SNVSAI1D's small-signal model (drafts/scripts/
    #     loop_design.py, which reproduces TI's own worked example at 4.2 kHz), six of the seven stages as built in
    #     round 4 had a NEGATIVE phase margin at their worst corner (-44 to -120 degrees) and the PoE stage 21
    #     degrees with 2.4 dB of gain margin: none was a converter to rely on as drawn. No compensation ALONE fixes
    #     six of them: their ceramics are 15 to 57 uF effective, while the lead and the load's own decoupling add
    #     0 to 300 uF behind 0.08 to 1 uH, an undamped resonance and a capacitance spread no single Rc1/Cc1/Cc2
    #     spans. Each call now names its own set AND the local bulk its design needs, a Panasonic ZK hybrid
    #     polymer (BULK_ZK above: no DC-bias loss, and its ESR damps that resonance), or on the PoE stage two
    #     more of its own 100 V output ceramics. Every design meets, at every corner of its input range, load
    #     range, ceramic DC-bias band, bulk tolerance and ESR life, gm and switching-frequency spread, current-loop
    #     Q from 0.4 to 0.8 at the nominal inductance, and remote capacitance: phase margin 50 degrees or more, gain
    #     margin 10 dB or more, |1 + T| 0.5 or more, every crossover under Fsw / 20 and fRHP / 3, and a closed-loop
    #     output impedance under the rail's bound (5 percent of VOUT for its load step, and Middlebrook's third of
    #     V^2/P for a converter load). THE Q BAND IS NARROWER THAN THE PARTS' TOLERANCES (second fix-up, the
    #     re-review's minor item 1): XAL1010 inductance +-20 percent, ISLOPE 13 / 17 / 21 uA and the C0G slope
    #     capacitor +-5 percent reach a Q of about 1.1 to 1.5. On that widened band (Q 0.4 to 1.5, L 0.8 to 1.2 of
    #     nominal; loop_design.py with LOOP_WIDE=1) the phase margins do not move, and the gain margins fall under
    #     the 10 dB target but stay positive: S2 and SD 9.4 dB, PA 9.9, HF 8.2, PD 9.85, PoE 12.0; the front end,
    #     redesigned in the second fix-up ON the widened band, keeps 10.5 dB. The figures per stage are on each
    #     call. BULK RIPPLE CURRENT (second fix-up, the re-review's blocking item): every bulk part is judged
    #     against its rated ripple current (BULK_ZK above) at the worst corner of its stage, drafts/scripts/
    #     bulk_ripple.py (SNVSAI1D Equation 19's current split harmonic by harmonic between the parts); the worst
    #     per-part figure is on each call. THE FRONT END'S NODE IS JUDGED ON THE DENSE BANDS (third fix-up,
    #     drafts/scripts/ripple_dense.py): bulk_ripple.py's endpoint corners missed a resonance inside its own bands
    #     there; the re-review re-ran the other stages inside their bands and their figures stand. It is a paper design: TI's own words are "Each design should be tuned
    #     in the lab", and the bench reading is FW-A15.
    if not cslope or not boot_diodes:
        raise SystemExit("lm5176 %s: a stage needs its SLOPE capacitor and its two bootstrap diodes (SNVSAI1D pin "
                         "table, 7.3.14, Figure 8-1); none was given" % p)
    if not comp or len(comp) != 3:
        raise SystemExit("lm5176 %s: a stage needs its own compensation (Rc1, Cc1, Cc2), designed for its own power "
                         "stage (SNVSAI1D 8.2.2.14; drafts/scripts/loop_design.py); none was given" % p)
    if not bias_cap:
        raise SystemExit("lm5176 %s: a stage needs its BIAS pin's 0.1 uF bypass (SNVSAI1D 9.1); none was given" % p)
    if (bias or vout) != vin and not vin_block:
        raise SystemExit("lm5176 %s: BIAS is %s, not the input rail %s, so the VIN pin needs its series blocking diode "
                         "(SNVSAI1D 7.3.2 and 9.1); none was given" % (p, bias or vout, vin))
    N = lambda s: p + "_" + s
    ic(uref, 29, "LM5176PWPR buck-boost controller, %s from %s" % (vout, vin), "HTSSOP28", {
        "1": N("EN") if en_div else en, "2": N("VINP") if vin_block else vin, "3": N("VISNS") if visns_r else vin, "4": N("MODE"), "5": "GND", "6": N("RT"), "7": N("SLOPE"), "8": N("SS"), "9": N("COMP"), "10": "GND", "11": N("FB"), "12": vout,
        "13": N("ISNS_N"), "14": N("ISNS_P"), "15": N("CSGF"), "16": N("CSF"), "17": N("PGOOD"), "18": N("SW2"), "19": N("HDRV2"), "20": N("BOOT2"), "21": N("LDRV2"), "22": "GND", "23": N("VCC"),
        "24": bias or vout, "25": N("LDRV1"), "26": N("BOOT1"), "27": N("HDRV1"), "28": N("SW1"), "29": "GND"}, "C442493")
    nfet(qbh, fet, N("HDRV1"), vin, N("SW1"), lcsc=fet_lcsc); nfet(qbl, fet, N("LDRV1"), N("SW1"), N("CS"), lcsc=fet_lcsc)
    nfet(qsl, fet, N("LDRV2"), N("SW2"), N("CS"), lcsc=fet_lcsc); nfet(qsh, fet, N("HDRV2"), N("OUT"), N("SW2"), lcsc=fet_lcsc)
    part(lref, "Device", "L", lval, "L1010", {"1": N("SW1"), "2": N("SW2")}, l_lcsc)
    r(rft, rfb_top + " 1%", vout, N("FB")); r(rfb, rfb_val, N("FB"), "GND"); r(rrt, "40.2k (206 kHz)", N("RT"), "GND")
    c(csl, cslope[0], N("SLOPE"), "GND", lcsc=cslope[1])   # the slope capacitor, 26 September 2026 (see above)
    (_rc1, _rc1c), (_cc1, _cc1c), (_cc2, _cc2c) = comp   # the stage's own compensation, (3) above
    r(rco, _rc1, N("COMP"), N("COMPC"), lcsc=_rc1c); c(cco, _cc1, N("COMPC"), "GND", lcsc=_cc1c); c(cco2, _cc2, N("COMP"), "GND", lcsc=_cc2c); c(_css_ref, css[0], N("SS"), "GND", *(css[2:3] or ("C",)), lcsc=css[1]); c(cvcc, "4.7u", N("VCC"), "GND", "C10u", bypass=(uref, "23"))   # the controller's own VCC
    c(bias_cap, "100n", bias or vout, "GND", bypass=(uref, "24"))   # SNVSAI1D 9.1, the BIAS pin's own bypass (second fix-up); C14663 is 50 V, and BIAS is at most 20 V (VBUS20)
    c(cb1, "100n 25V", N("BOOT1"), N("SW1")); c(cb2, "100n 25V", N("BOOT2"), N("SW2"))
    # The value names no controller: emc_sheet.py reads a part number in a value string as a switching source,
    # and "LM5176" in fourteen diode values made each of them one (the first suite run of 26 September 2026).
    for _d, _boot in zip(boot_diodes, ("BOOT1", "BOOT2")):   # anode on VCC, cathode (pad 1, the band) on BOOT
        part(_d, "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (bootstrap)", "SOD123", {"1": N(_boot), "2": N("VCC")}, "C83152")
    r(risns, isns + "Ohm 1% 2512 (ISNS)", N("OUT"), vout, "RS2512", isns_lcsc); r(rcs_, rcs + "Ohm 1% 2512 (CS)", N("CS"), "GND", "RS2512"); r(rpg, "100k", N("PGOOD"), "+3V3")
    # THE CURRENT-SENSE PAIR IS KELVIN AND FILTERED (18 September 2026, rule ANA-001, lm5176-datasheet.pdf).
    # Two things this helper did not do, on all five stages, and both are in TI's own layout clause 9.1:
    # "Use Kelvin connections to RSENSE for the current sense signals CS and CSG and run lines in parallel from
    # the RSENSE terminals to the IC pins. Avoid crossing noisy areas such as SW1 and SW2 nodes ... Place the
    # filter capacitor for the current sense signal as close to the IC pins as possible", and the pin table's
    # own words for pin 15: "CSG ... Connect directly to the low-side (ground) of the current sense resistor".
    # (1) PIN 15 WAS TIED TO THE GROUND NET, so the sense amplifier's negative input joined the plane wherever
    # the router chose and every millivolt of plane drop between the shunt's ground pad and that point added to
    # a sensed voltage whose own limit threshold is 66 to 94 mV, 80 typical (VCS(BUCK), electrical
    # characteristics, the HTSSOP-28 row, which is the package this board buys). CORRECTED 20 September 2026:
    # this line read "120 to 140 mV (VCS(BUCK))" and those are VCS(BOOST)'s typ and max, a different row of
    # the same table; the buck VALLEY threshold is the smaller of the two, so the same plane drop is a LARGER
    # share of the reading than the comment claimed and the correction is in the strict direction.
    # (2) THERE WAS NO FILTER AT ALL, where section 8.2.2.7 says "For some application circuits, it can be
    # required to add a filter network to attenuate noise in the CS and CSG sense lines ... The filter
    # resistance should not exceed 100 Ohm". 100 R in each line with 1 nF across the pins is 200 ns
    # differential, which is the leading-edge spike and not the signal; the error it costs is the offset
    # current alone (IOFFSET(CS/CSG) 19 uA x 100 R = 1.9 mV, 1.4 percent of the threshold), because the bias
    # current is common to both lines and the two resistors match. Board E's tracker has carried exactly this
    # network since E6 (R6, R7, C16 around the LT8705A); nothing held these five stages to it.
    # The two resistors belong AT the shunt and the capacitor at the IC pins; the placement generator seats
    # them with the stage's low-side FETs, and the declared sensitive nets are the FILTERED pair, never the
    # shunt's own terminals, which are the low-side FETs' common source and a switching conductor.
    _rcsf, _rcsgf, _ccsf = cs_filter
    r(_rcsf, "100R 1% (CS filter, Kelvin from the shunt's top)", N("CS"), N("CSF"))
    r(_rcsgf, "100R 1% (CSG filter, Kelvin from the shunt's ground pad)", "GND", N("CSGF"))
    c(_ccsf, "1n", N("CSF"), N("CSGF"), bypass=(uref, "16"))   # "as close to the IC pins as possible": declared as pin 16's own decoupling so bypass_slots reserves its seat before the packer runs and DEC-001 measures the distance
    # AND THE AVERAGE-CURRENT PAIR GETS THE SAME NETWORK, for a reason that was MEASURED on A54's routed board
    # (20 September 2026). Pins 13 and 14 were wired straight onto the two power rails the ISNS shunt separates,
    # so the tap was not a net at all: `kelvin_check` on that board read ELEVEN of thirteen taps as not Kelvin
    # connections and `PD_ISNS_N` at 215.585 mV of its own 50.0 mV full scale, 431 percent, because what it
    # measures is the drop along /PD_VPWR between the shunt's pad and the pin, on a rail carrying 3 A. That is
    # why the Kelvin ranking is PI-001's ranking: it is the same measurement twice. NOTHING IN A ROUTER CAN FIX
    # IT, because no class and no pre-lay separates a net from itself, and the pair pre-router asked to lay
    # them answered `0 of 0 pairs` and was right.
    # TI's own words, section 7.3.6: the gm amplifier "monitors the voltage across the sense resistor and
    # compares it with an internal 50-mV reference", and "a filter network as shown in Figure 8-1 is often used
    # across the ISNS(+) and ISNS(-) pins to filter the ripple in the average current sense signal". A series
    # resistor in each line is what gives each tap ITS OWN NET, and only then is a Kelvin connection a thing
    # this board can draw or this project can judge. The layout list names CS and CSG for Kelvin connections
    # and not ISNS, which is why these five stages were left out when that clause was answered on 16 September.
    # 100 R matches the CS filter above and costs the offset the bias current makes: the ISNS pins draw 3 uA
    # each (electrical characteristics, `VISNS(+) = VISNS(-) = VIN = 24 V`), so 0.3 mV per line, 0.6 percent of
    # the 50 mV reference, and it is common to both lines where the two resistors match.
    # The nets are named `<stage>_ISNS_P` and `<stage>_ISNS_N` deliberately: that is the pair pre-router's own
    # suffix convention, so a later phase can lay them as a coupled locked pair without any new tool.
    _risnsp, _risnsn, _cisns = isns_filter
    r(_risnsp, "100R 1% (ISNS+ filter, Kelvin from the shunt's output pad)", N("OUT"), N("ISNS_P"))
    r(_risnsn, "100R 1% (ISNS- filter, Kelvin from the shunt's rail pad)", vout, N("ISNS_N"))
    c(_cisns, "1n", N("ISNS_P"), N("ISNS_N"), bypass=(uref, "14"))   # at the pins, as the CS capacitor is: declared as pin 14's own decoupling so bypass_slots reserves its seat before the packer runs
    if en_div:
        r(ret, "62k 1%", en, N("EN")); r(reb, "10k 1%", N("EN"), "GND")
    elif ret or reb:
        raise SystemExit("lm5176 %s: en_div=False takes no EN divider references, and %s/%s were given" % (p, ret, reb))
    r(rmd, "100k (MODE: CCM)", N("MODE"), N("VCC"))
    # OWNER RULING 12 September 2026, decision 10. These five stages asked for `22u 50V X7R 1210` in all 25
    # positions and NO SUCH PART EXISTS: at a 1210 size and 50 V the ceramic tops out near 10 uF, which three
    # queries of JLCPCB's catalogue confirm and the physics explains. The ruling is the largest real part that
    # drops into the existing land, so nothing moves and A24 is re-finished rather than re-routed, with the
    # ripple re-measured before anything is ordered rather than before the folder is cut.
    #
    # The OUTPUT value is per stage because the PoE stage's output is +54V_POE: a 50 V part there is over its
    # rating before any derating or transient, which is wrong at any capacitance, so that stage takes a 100 V
    # part in the same land (C5156756, X7R, 426,107 in stock). The cost of the ruling is capacitance: 20 uF in
    # and 30 uF out per stage against 44 and 66, and X7R derates further under bias, so the ripple and loop
    # margin on a 5 A converter are owed a measurement before the order.
    if vin_block:   # third fix-up (R4A-N11): the VIN pin behind its blocking diode, with its own capacitor at the pin
        _dvb, _cvb, _cvbv, _cvbl, _cvbf = vin_block
        part(_dvb, "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (VIN blocking)", "SOD123", {"1": N("VINP"), "2": vin}, "C83152")
        c(_cvb, _cvbv, N("VINP"), "GND", _cvbf, lcsc=_cvbl, bypass=(uref, "2"))
        c(ci1, cin, vin, "GND", "C1210"); c(ci2, cin, vin, "GND", "C1210", **({} if visns_r else {"bypass": (uref, "3")}))   # the power stage's input capacitors; ci2 serves VISNS unless VISNS sits behind its 2 k
    else:
        c(ci1, cin, vin, "GND", "C1210", bypass=(uref, "2")); c(ci2, cin, vin, "GND", "C1210", **({} if visns_r else {"bypass": (uref, "3")}))   # the two VIN pins
    for cr in (co1, co2, co3) + tuple(cout_extra):
        if cr in cout_pre: continue
        c(cr, cout, vout, "GND", "C1210", lcsc=cout_lcsc)
    for cr in cout_pre:   # before the ISNS shunt, on <p>_OUT (SNVSAI1D 9.1; see the docstring)
        if cr not in (co1, co2, co3) + tuple(cout_extra): raise SystemExit("lm5176 %s: cout_pre %s is not one of the stage's output ceramics" % (p, cr))
        c(cr, cout, N("OUT"), "GND", "C1210", lcsc=cout_lcsc)
    _bv, _bfp, _bl = BULK_ZK[bulk_part]
    if bulk and _intent.net_volts(vout) > 0.8 * float(_bv.split()[1].rstrip("V")):
        raise SystemExit("lm5176 %s: the bulk part %s is rated %s and %s runs at %s V, over 80 percent of it" % (p, bulk_part, _bv.split()[1], vout, _intent.net_volts(vout)))
    for cb in bulk:   # local bulk the stage's loop design asks for, (3) above; pad 1 is the positive terminal
        part(cb, "Device", "C_Polarized", _bv, _bfp, {"1": vout, "2": "GND"}, _bl)
    # THE STAGE'S OWN NON-RAIL NETS, DECLARED HERE AND NOT IN TWENTY HAND-WRITTEN LINES (16 September 2026,
    # rule CMP-001). A buck-boost's two switching nodes are where the highest voltage on the board appears and
    # nothing declared them: `derate.py` reported twenty-nine of board A's nets as UNDECLARED and judged no
    # part on any of them. The numbers come from the topology, which is right here: SW1 is the BUCK side and
    # swings between a diode drop below ground and the input rail; SW2 is the BOOST side and swings to the
    # output rail; each BOOT rides on its own SW at the controller's VCC, which is why the bootstrap
    # capacitors are 25 V parts and why judging them against the node's height above ground would refuse a
    # correct design. VCC is the LM5176's own regulator output, 7.6 V typical (datasheet, electrical
    # characteristics); the CS node is the drop across a 5 mOhm shunt at the stage's peak current.
    _vin_v = _intent.net_volts(vin); _vout_v = _intent.net_volts(vout); _vcc = 7.6
    _why = "LM5176 stage %s, %s to %s: " % (p, vin, vout)
    _intent.node(N("SW1"), _vin_v, _why + "the buck-side switching node reaches the input rail", v_min=-1.0)
    _intent.node(N("SW2"), _vout_v, _why + "the boost-side switching node reaches the output rail", v_min=-1.0)
    _intent.node(N("BOOT1"), _vin_v + _vcc, _why + "the bootstrap rides on SW1 at the controller's 7.6 V VCC",
                 rides_on=N("SW1"), bias_v=_vcc)
    _intent.node(N("BOOT2"), _vout_v + _vcc, _why + "the bootstrap rides on SW2 at the controller's 7.6 V VCC",
                 rides_on=N("SW2"), bias_v=_vcc)
    # <p>_OUT IS A RAIL AND IT WAS A NODE ON ALL FIVE STAGES (20 September 2026, the third to the seventh of
    # the sixteen). It is the conductor between the boost-side high-side FET's drain and the ISNS shunt, and
    # it carries the stage's WHOLE output current: 6 A on FE, 5 on PA, 3 on PD, and `node()` says in its own
    # first line that it describes a net that is NOT a rail, so `dc_drop` solved no potential on any of them
    # and neither PI-001 nor PI-002 ever looked at this copper. It is the same defect that made CH_ACN and
    # CH_SRP invisible, repeated five times by one helper, which is why it is fixed HERE and not in five
    # hand-written lines that could each be wrong in its own way.
    # The current is READ from the rail on the far side of the shunt rather than typed again: a segment of a
    # path carries the path's current by construction, and `rail_amps` makes the two impossible to drift.
    # The source is the FET's own drain tab (a PowerPAK SO-8's pad 5), never the controller, whose pin 14 on
    # this net is the ISNS sense input: naming it would send the whole current down a sense escape, which is
    # the 13 September defect that read 3.90 against IPC on copper that was never carrying it.
    _ot, _op = _intent.rail_amps(vout)
    _intent.rail(N("OUT"), _vout_v, _ot, _op, qsh,
                 loads={risns: _ot}, v_work=_vout_v,
                 **({"budget": out_budget} if out_budget else {}),
                 series_of=vout, converted=False,
                 note=_why + "the output conductor between %s's drain tab and the ISNS shunt %s, at the "
                             "stage's whole output current. It was a node until 20 September 2026, so no "
                             "power rule had ever looked at it." % (qsh, risns))
    _intent.node(N("VCC"), _vcc, _why + "the controller's own regulator output, 7.6 V typical")
    if visns_r:   # SNVSAI1D 7.3.7 and Figure 8-1: 2 k in series with VISNS where the input can pass 40 V
        _vr, _vrv, _vrl = visns_r
        r(_vr, _vrv, vin, N("VISNS"), lcsc=_vrl)
        _rv3 = _intent._I["rails"].get(vin, {})
        _intent.node(N("VISNS"), max(float(_rv3.get(k) or 0) for k in ("volts", "v_work", "v_max")),
                     _why + "the controller's VIN sense pin behind its series 2 k (SNVSAI1D 7.3.7, Figure 8-1): the input "
                     "rail's service maximum; the pin draws microamps, so the resistor drops millivolts")
    if vin_block:   # the worst the input rail declares (its service maximum), which a diode drop only lowers
        _rv = _intent._I["rails"].get(vin, {})
        _intent.node(N("VINP"), max(float(_rv.get(k) or 0) for k in ("volts", "v_work", "v_max")),
                     _why + "the controller's VIN pin behind its series blocking diode (SNVSAI1D 7.3.2, Figure 7-1): the "
                     "input rail's service maximum less a diode drop, never above it")
    _intent.node(N("CS"), 1.0, _why + "the current-sense node: the drop across a %s Ohm shunt, under a volt at any current this stage carries" % rcs)
    _intent.node(N("CSF"), 1.0, _why + "the filtered current-sense input at pin 16, 100 R from the shunt's top")
    _intent.node(N("CSGF"), 1.0, _why + "the filtered current-sense ground at pin 15, 100 R from the shunt's ground pad (the Kelvin return TI's pin table asks for)")
# stage FE: the vehicle and shore input (9 to 36 V after E6's protection and filter) to the 20 V charge bus, 5 A; 60 V FETs
# THE INPUT CAPACITORS OF THIS STAGE ARE 100 V PARTS AND THE CLAMP STANDS OFF 40 (16 September 2026, CMP-001).
# VIN_RAW is the vehicle and shore line: 9 to 36 V in service, and its clamp was an SMCJ33A, which stands off
# 33 V. A suppressor whose standoff is BELOW the line's own working maximum conducts in normal service rather
# than only on a transient, and at 36 V in it would sit there dissipating until it failed short. The same part
# was on board E's two input nets, three places and one defect, found the first time a rule asked a protector
# its own question instead of asking whether it survives the voltage it itself produces.
# The replacement is the same land and the next standard standoff up, SMCJ40A (Littelfuse, C224052, DO-214AB,
# stock 3,987 on 16 September 2026), and it is NOT a free swap: its clamping voltage is 64.5 V at 23.2 A where
# the SMCJ33A's is 53.3, so this stage's input capacitors move from 50 V to the 100 V part the PoE stage's
# output already uses (C5156756, 10 uF 100 V X7R in the same 1210 land, stock 394,648). The other four stages
# sit on VBAT behind an SMCJ18A that clamps at 29.2 V and keep the 50 V part.
lm5176("FE", "U2", "VIN_RAW", "VBUS20", "FE_EN", "240k", "L1", "10uH XAL1010-103ME (Isat 17.5 A)", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6)", "C473333",
       ["Q2", "Q3", "Q4", "Q5", "R6", "R7", "R8", "C147", "R10", "C5", "C6", "C7", "C8", "C9", "C10", "R11", "R12", "R13", None, None, "C11", "C12", "C13", "C14", "C15", "R119"], en_div=False,
       cs_filter=("R150", "R151", "C123"), isns_filter=("R160", "R161", "C128"), cin="10u 100V X7R 1210", l_lcsc="C6358489",
       cslope=("680p", "C30816"), boot_diodes=("D9", "D10"),
       comp=(("15k", "C22809"), ("220n", "C160828"), ("680p", "C30816")), bulk=("C163", "C178", "C179", "C180", "C199", "C200"), bulk_part="V331",
       cout_extra=("C181", "C182", "C183", "C184", "C185", "C186", "C187", "C188", "C189", "C201", "C202", "C203", "C204", "C205", "C206"),
       cout_pre=("C13", "C14", "C15"), css=("4.7u", "C354262", "C10u"), vin_block=("D19", "C207", "1u 100V 1210", "C382212", "C1210"),
       bias_cap="C192", visns_r=("R195", "2k", "C22975"))   # round 4, 26 Sep 2026: CSLOPE dead-beat 2 uS x 10 uH / (5 mOhm x 5) = 800 pF, 680 pF C0G (Samsung CL10C681JB8NNNC); R9 (30k) retired. Third fix-up: see below
# THE FRONT END'S OUTPUT NODE, SIZED FOR ITS RIPPLE CURRENT. SECOND FIX-UP (26 September 2026): SNVSAI1D 8.2.2.5
# Equation 19, ICOUT(RMS) = IOUT x sqrt(VOUT / VIN - 1), is 6.3 A rms at 9 V in and the ISNS loop's 5.7 A maximum (VSNS
# 57 mV over R11's 10 mOhm; the charger can ask for it), and the BQ25731 draws its own input current from this node in
# pulses, SLUSE66A Equation 4, up to 5.7 A rms at D = 0.5; one EEHZK1V101XP carried 8.1 A of its 1.7 A. That pass took
# four EEHZK1V331P and fifteen ceramics and reported 95 percent of the 2.8 A rating "at every corner".
# THIRD FIX-UP (26 September 2026, the second re-review's blocking item 1): THAT FIGURE SAMPLED EACH INFERRED BAND AT ITS
# TWO ENDPOINTS ONLY, and the node has a PARALLEL RESONANCE between the ceramic bank and the cans' ESL, about 0.5 to
# 1.1 MHz over the bands, on which the charger's fundamental and the FE's 3rd to 5th harmonics land for band values
# INSIDE the bands. The switching frequencies were held at their nominal values too, where the BQ25731's own table gives
# FSW 680 / 800 / 920 and 340 / 400 / 460 kHz (SLUSE66A 8.5) and the LM5176's is 180 to 232 kHz. drafts/scripts/
# ripple_dense.py samples every band densely (polymer ESL 1.5 to 3.5 nH in 0.05 nH steps, ceramic C 4 to 7 uF in
# 0.125 uF steps, fsw in 11 steps, fch over both bands in 14, VBAT in 10; the damping bands at their corners), takes the
# exact maximum over the two unsynchronised sources' corners, and reproduces bulk_ripple.fe_case to 1e-15 where the
# networks are the same, the re-review's 2.97 A point included. The second fix-up's node reads 3.43 A, 122 percent,
# and 3.31 A at a 2:1 ESR spread. SNVSAI1D 9.1 also asks for the output capacitance to be divided across the ISNS
# shunt ("When using the average current loop, divide the overall capacitor (CIN or COUT) between the two sides of the
# sense resistor to ensure small cycle-by-cycle ripple", R4A-N14), and doing so takes the stage's own switch current
# off the shunt and out of the bulk. Options (drafts/box/fixup3/ripple: a 120-option screen, then eight on the full
# bands at 5.7 and 5.0 A and at ESR spreads 1.0, 1.5 and 2.0): four to ten cans, 6 to 30 ceramics, 0, 3 or 6 of them
# on FE_OUT. Five cans stay at 98 to 100 percent at a 2:1 spread; six with three ceramics on FE_OUT reach 71 to 80
# percent matched. Taken by the session under the owner's standing rule of 26 Sep 2026: SIX EEHZK1V331P (C163, C178 to
# C180, C199, C200; one part number, as the sheet asks for parallel parts), the stage's C13 to C15 MOVED to FE_OUT before
# R11 (cout_pre), and eighteen ceramics on VBUS20 (C181 to C189, C201 to C206 and the charger's C20 to C22). Worst can
# over the whole bands at 5.7 A: 2.10 A, 75 percent of 2.8 A matched; 2.11 A (75 percent) at a 1.5:1 spread and 2.43 A
# (87 percent) at 2:1; at the declared 5 A 1.85 / 1.86 / 2.14 A (66 / 66 / 76 percent). Worst ceramic 1.09 A on VBUS20
# and 1.55 A on FE_OUT: no MLCC ripple rating is held, and at the band's 5 mOhm ESR that is 12 mW a part (INFERRED).
# THE LOOP ON THE NEW NODE keeps the second fix-up's compensation (loop_verify.py FE 6 V331 15 21, both bands,
# drafts/box/fixup3/loop): Rc1 15 k, Cc1 220 nF, Cc2 680 pF read PM 73.1 degrees, GM 15.7 dB, |1 + T| 0.79, crossover
# 0.71 to 3.6 kHz, 89 mOhm against 1.17 Ohm; on the widened band PM 72.9, GM 14.0 dB, |1 + T| 0.76. The search's own
# pick for the node, 22 k / 220 nF / 470 pF, is faster (1.0 to 5.3 kHz) with less margin (widened GM 10.8 dB), so the
# parts stay. The three FE_OUT ceramics sit behind R11's 10 mOhm, which at the loop's frequencies is nothing beside
# their reactance, so they are counted with the local bank. Equation 9 is unchanged (COMP 2.05 V at 9 V in).
# THE SOFT START, SIZED FOR WHAT FEEDS IT (third fix-up, the second re-review's blocking item 2). C7 was the helper's 47 nF
# for every stage: SNVSAI1D Equation 3, and FB following SS, make the output slew (1 + 240k/10k) x ISS / CSS, so with
# ISS 6.35 uA, CSS at its X7R corner and this node at 2.6 mF it charged 11.7 A, 29 A at 9 V in, against board E's LM5069,
# which limits the vehicle entry at 4.85 to 6.15 A (4.80 A with R19's 1 percent) and, the front end being a constant-
# power load, collapses VIN_RAW to the stage's UVLO (U34's UV since the fourth fix-up) when it limits. drafts/scripts/softstart.py: C7 was 3.3 uF in the third
# fix-up; FOURTH FIX-UP (the third re-review's minor item 4): C7 IS 4.7 uF (YAGEO CC0805KKX7R8BB475, C354262, 25 V X7R
# 0805, the 0805 4.7u this project's lcsc_fill already maps), because 3.3 uF's host-free 99.6 percent at 9 V rested on
# CSS at 0.765 of nominal and X7R's aging after reflow takes it lower: at 0.70 of nominal 3.3 uF reads 100.4 percent and
# 4.7 uF 97.6 (97.0 at 0.765). Ramp 0.41 / 0.75 / 1.29 s; the ramp's own draw (charging plus the controller's BIAS) at
# the end of the ramp is 8.6 percent of the entry's floor at 9 V, 6.5 at 12 V and 5.6 at 13.8 V, every worst corner
# stacked (C +20 percent and unbiased ceramics, ISS maximum, CSS -23.5 percent, VBUS20 20.7 V, efficiency 0.93); the
# figures below are the third fix-up's 3.3 uF ones where not restated. The LOAD AT START is the charger: it converts only after CHRG_OK's
# 50 ms deglitch (SLUSE66A, typical, no minimum given), so on a ramp this long it can be converting before the ramp ends,
# drawing up to IIN_DPM. With the host contract FW-A16 (IIN_HOST at 80 percent of the entry at the present VIN_RAW) the
# total is 91 percent at 9 V and 88 percent at 12 V. With no host having written the charger (POR: RSNS_RAC 1b and
# IIN_HOST 3.2 A against this board's 10 mOhm R16, 1.72 A), the charger alone is 88.6 percent at 9 V and the total 99.6
# percent at 9 V, 89.6 at 10 V and 74.7 at 12 V: under the limit everywhere, and the thin figure at 9 V is the charger's
# steady state (R4A-N10), which no soft start moves (4.7 uF: 97.0 percent at 9 V, 87.3 at 10 V, 72.8 at 12 V; with
# FW-A16 88.6 at 9 V). Below the 9 V service floor, inside the restart guard's enable window (8.0 to 8.5 V release), the
# host-free charger alone passes the entry (109 percent at 8.0 V): E then limits, VIN_RAW falls to the guard's UV and
# the stage waits and restarts; nothing is damaged. THE COST, stated as the re-review asked: the constant-current loop
# acts by discharging CSS from its 1.21 V clamp to VREF with its 1 mS gm (SNVSAI1D 7.3.4, 7.3.6), so an overload now
# holds for 251 ms at 10 mV over VSNS and 335 ms at the charger's largest request (6.45 A over a 57 mV unit; 176 and
# 235 ms with 3.3 uF), against 3 ms with 47 nF; meanwhile the charger's own IIN_DPM bounds the current (L1 16.2 A peak at 9 V and 6.45 A, under its
# 17.5 A) and the cycle-by-cycle limit bounds a fault. The other six stages keep 47 nF: they start from VBAT, where no
# entry limits them (softstart.py: 0.5 to 5.8 A from VBAT for at most 13 ms each).
# THE VIN PIN'S BLOCKING DIODE (third fix-up, R4A-N11 assessed with the soft start, the second re-review's minor item 3):
# BIAS is VBUS20, which now holds 2.6 mF, so when VIN_RAW falls BIAS keeps VCC up for up to a second and SNVSAI1D 7.3.2
# says what follows: "use a series blocking diode between the input supply and the VIN pin (Figure 7-1). This prevents
# VCC from back-feeding into VIN through the body diode of the VCC regulator". D19 (BAT46W, the bootstrap diodes' part,
# 100 V) feeds pin 2 through FE_VINP with C207 at the pin (1 uF 100 V X7R 1210, PSA FS32X105K101EFG, C382212, the part
# board E certifies; VIN_RAW's clamp reaches 64.5 V); VISNS stays on VIN_RAW. PA and HF take the same (their BIAS is
# their own output). FOURTH FIX-UP: VISNS now sits behind R195 (2 k), SNVSAI1D 7.3.7's requirement for an input that can
# pass 40 V (VIN_RAW's clamp does); no capacitor at the pin, as Figure 8-1 draws it. The FE's EN/UVLO is no longer the
# 62k / 10k divider from VIN_RAW: see THE RESTART GUARD below.
kisch.tvs("D2", "SMCJ40A (VIN_RAW clamp behind E6's filter: 40 V standoff on a line specified to 36)", "VIN_RAW", "GND", "TVSC", "C224052")   # TRN-001 / S-09 (ts-tvs, 26 Sep 2026): a one-way part, drawn K/A by kisch.tvs() (Device:D_Zener, K pin 1 on VIN_RAW, A pin 2 on GND; direction from the part number, recorded in the intent under "clamps"); nets, value, land and code as before (Littelfuse C224052, v2/vendor/power/littelfuse-smcj-series-tvs.pdf)
# THE RESTART GUARD (fourth fix-up of 26 September 2026, R4A-N15; the third re-review's blocking item). Taken by the
# session under the owner's standing rule of 26 Sep 2026. drafts/scripts/restart.py, drafts/box/fixup4/restart.
# THE DEFECT. The FE's soft-start capacitor is discharged whenever U2 is disabled (SNVSAI1D 7.3.4: EN/UVLO below its
# threshold, VCC UV, thermal shutdown), and VBUS20 keeps 18.5 to 20.7 V on 1.7 to 2.6 mF for minutes afterwards (the
# charger stops at its VINDPM; the 250 k divider is the only other load). Every VIN_RAW dip under the old 62k / 10k
# UVLO (8.2 to 9.2 V rising), every engine crank, every vehicle reconnection and every retry of board E's LM5069 then
# re-enabled U2 with SS at 0 against a charged output. U2 has no pre-biased start: 7.3.8 "In CCM operation, the
# inductor current can flow in either direction"; 7.3.13 COMP spans 0.3 to 3 V and Equations 7 and 9 put zero current
# at 1.6 V, so COMP's floor commands (1.6 - 0.3) / (ACS 5 x 5 mOhm) = -52 A, and the error amplifier's 280 uA across
# Rc1's 15 k puts COMP on that floor within microseconds; 7.3.5 names no negative limit. Board E's sources sit behind
# ideal diodes, so the bank's 0.36 to 0.56 J could only go into VIN_RAW's 20 to 32 uF and the SMCJ40A. restart.py over
# 48 corners (bank, VIN_RAW capacitance, L1 +-20 percent, restart at 8.2, 12 and 28 V): VIN_RAW 57.8 to 60.1 V (U2's
# absolute maximum on VIN, EN/UVLO, VISNS, ISNS and SW1 is 60 V), L1 at -52 A (Isat 17.5 A; saturation not modelled,
# which only makes it worse), 0.23 to 0.53 J into the clamp at EVERY crank; board E's VIN_MON reads 5.5 V at its ADC.
# A dip that leaves SS partly discharged is no better: a shortfall of 4 to 15 mV under FB already pulls the bank down
# far enough (0.1 to 0.36 V, C x V x dV) to fill VIN_RAW to 36 V, and the sheet does not give SS's discharge rate.
# Neither case is bounded as drawn; the stage's own UVLO could not be the fix, since every UVLO event IS the hazard.
# THE FIX, the reviewer's second example: U2's enable is owned by a supervisor that holds it low from any VIN_RAW
# undervoltage until VBUS20 has been bled under 0.8 V, so every start is a start from an empty bank.
#  U34 TPS37A010122DSKR (TI SNVSBJ1E, drafts/datasheets/ti-tps37.pdf, fetched from ti.com 26 Sep 2026; LCSC C3685740,
#   stock 738): VDD 2.7 to 65 V (70 V absolute) straight from VIN_RAW through R196 / C210, SENSE and RESET pins 65 V
#   graded and independent of VDD, both channels at VIT 0.800 V (0.792 to 0.808) with 2 percent hysteresis, both
#   RESET outputs open drain active low; below VDD's 2.7 V UVLO both outputs are asserted (VPOR 1.4 V).
#  Channel 2 (UV) is the stage's UVLO now: R14 91 k over R15 10 k (the old UVLO pair, re-valued) put VIN_RAW's
#   threshold at 7.86 / 8.08 / 8.31 V falling and 8.01 / 8.24 / 8.48 V rising, under the 9 V service floor; C212
#   100 nF on CTR2 holds the release 79 / 127 / 201 ms (SNVSBJ1E Eq. 1 to 3), a debounce; C211 on SENSE2 as the
#   pin table suggests.
#  Channel 1 (OV type) is the LATCH: SENSE1 sits on VBUS20 through R197 (100 k, 100 nA at most into the pin, 10 mV),
#   and Q36 (2N7002) shorts it to ground while FE_RUN is high. So while the stage runs, channel 1 can never assert;
#   the moment FE_RUN falls, SENSE1 is VBUS20 and channel 1 holds FE_RUN low until VBUS20 is under 0.766 / 0.784 /
#   0.792 V, whatever channel 2 does afterwards. Its state is VBUS20 itself, so it is rebuilt from the bank at every
#   power-up of the supervisor; no memory is lost when VIN_RAW vanishes.
#  FE_RUN (both RESET pins) is pulled to FE_VZ by R198 (100 k); FE_VZ is VIN_RAW through R200 (33 k) clamped by D22
#   (BZT52C12-7-F, Diodes DS18004, 11.4 to 12.7 V; v2/vendor/diodes/diodes-bzt52c-ds18004.pdf): 5.9 V at the UV fall, 0.63
#   mA in the zener at 36 V, 85 mW in R200 at the clamp's 64.5 V. U2's EN/UVLO (60 V, VEN(OP) 1.17 to 1.29 V) takes
#   FE_RUN over R199 (47 k) and R206 (100 k), 0.68 of it, with C213 (2.2 nF) at the pin. Three things rest on that:
#   (a) while held, EN sits at 0.44 V at most (U34's 0.3 V VOL plus the pin's own 7 uA into 32 k), under VEN(STBY)'s
#   0.55 V, so U2 is in shutdown; (b) EN needs at least 44 us to fall through VEN(OP), and channel 1 has latched within
#   18 us of FE_RUN falling (tCTS open 17 us plus Q36), so a supervisor glitch shorter than the latch cannot disable U2
#   without the latch holding it; (c) below U34's VPOR (1.4 V) its outputs are undetermined, and with RESET floating EN
#   reaches VEN(OP)'s 1.17 V minimum only at VIN_RAW 3.28 V, above U34's own 2.7 V UVLO, where both outputs are
#   asserted. (The first draft of this pass fed EN from FE_RUN through 4.7 k alone: with RESET floating EN followed
#   FE_VZ, and FE_VZ follows VIN_RAW under the zener's knee, so a slow ramp through 1.2 to 1.4 V could have enabled
#   U2 against a charged bank before U34 was valid.) Running at the lowest UV fall: FE_VZ 5.4 V, FE_RUN 3.2 V (Q36 and
#   Q37's VGS(th) is 2.5 V at most), EN 2.2 V.
#  THE BLEED: while FE_RUN is low, Q37 (2N7002) lets R201 (100 k) lift FE_BLEED_G to FE_VZ and Q38 (CSD19532Q5B,
#   VGS(th) 3.2 V at most, SLPS414B) connects R202 to R205 (four 510 Ohm 1 W 2512, UNI-ROYAL 25121WJ0511T4E, LCSC
#   C36171) across VBUS20: 121 to 134 Ohm, 1.00 W per part at 22 V and 5 percent low, 0.16 J per part per event; tau
#   0.20 to 0.35 s and 0.64 to 1.17 s to the release level. No pulse rating is needed: the peak is inside the
#   continuous rating. While VIN_RAW is absent nothing is bled and nothing needs to be: U2 cannot start.
#  WHAT IS LEFT: a start from at most 0.792 V is the bank ringing into L1 through the buck low side (14.3 A peak at L1
#   -20 percent and the bank's +20 percent, under Isat 17.5 A; 0.82 mJ, which could lift VIN_RAW to 12.1 V from the
#   release level or 37.1 V from 36 V if every joule of it came back). U2's thermal shutdown (165 C) also discharges
#   SS and is not guarded: the controller's own loss is its gate drive, so it needs a board far outside the envelope.
#   Cost: 21 new parts (one new IC, U34) and the old UVLO pair re-valued; a restart waits for the bleed (0.6 to 1.2 s)
#   plus the soft start (0.4 to 1.3 s), so a dip under 8 V interrupts charging for about 1 to 2.5 s. Rejected: a pre-biased start (SS cannot be raised to FB in
#   the microseconds COMP takes to reach its floor with a 4.7 uF CSS, and a source strong enough would override
#   the CC loop and the chip's own fault discharge); a reverse-blocking element between the stage and the bank (an
#   ideal-diode controller regulates its forward drop, 20 mV on the LM74700-Q1, so at light load it puts a resistance
#   of 20 mV over the load current inside the voltage loop, 0.4 Ohm at the 50 mA BIAS load, and the loop design of
#   B3 would no longer hold; a Schottky costs 2.6 W at 5.7 A in a sealed case).
_GVIN = max(float(_intent._I["rails"]["VIN_RAW"].get(k) or 0) for k in ("volts", "v_work", "v_max"))
_gw = "restart guard (fourth fix-up, R4A-N15): "
ic("U34", 11, "TPS37A010122DSKR 65 V OV/UV supervisor: the FE's enable and its restart latch", "WSON10", {
 "1": "FE_GVDD", "2": "FE_LATCH", "3": "FE_UVS", "4": "FE_RUN", "5": "FE_RUN", "6": "NC", "7": "NC", "8": "NC", "9": "FE_CTR2", "10": "GND", "11": "GND"}, "C3685740")
r("R196", "1k", "VIN_RAW", "FE_GVDD", lcsc="C21190"); c("C210", "1u 100V 1210", "FE_GVDD", "GND", "C1210", lcsc="C382212", bypass=("U34", "1"))   # VDD's own filter: 1 ms keeps a clamp-edge step under SNVSBJ1E's 100 mV/us for its UVLO figures
r("R14", "91k 1%", "VIN_RAW", "FE_UVS", lcsc="C23265"); r("R15", "10k 1%", "FE_UVS", "GND", lcsc="C25804"); c("C211", "10n", "FE_UVS", "GND", lcsc="C57112")   # channel 2 (UV): 8.08 V falling, 8.24 V rising
c("C212", "100n", "FE_CTR2", "GND", lcsc="C14663")   # CTR2: the UV channel's release delay, 79 to 201 ms
r("R197", "100k", "VBUS20", "FE_LATCH", lcsc="C25803")   # channel 1 (the latch) reads VBUS20 itself
part("Q36", "Transistor_FET", "2N7002", "2N7002: FE_RUN high = latch sense held at 0 V (1 G, 2 S, 3 D)", "SOT23", {"1": "FE_RUN", "2": "GND", "3": "FE_LATCH"}, "C8545")
# D22's value names no volts: a zener's voltage is what it DOES, and derate.py would read "12 V" as a rating and judge the
# clamp against the voltage it makes, the circularity that tool already removed for TVS parts (open item O-35).
r("R200", "33k", "VIN_RAW", "FE_VZ", lcsc="C4216"); part("D22", "Device", "D_Zener", "BZT52C12-7-F zener, the restart guard's pull-up clamp", "SOD123", {"1": "FE_VZ", "2": "GND"}, "C124196"); c("C214", "100n", "FE_VZ", "GND", lcsc="C14663")
r("R198", "100k", "FE_VZ", "FE_RUN", lcsc="C25803")   # both RESET pins: FE_RUN is high only when neither channel asserts
r("R199", "47k", "FE_RUN", "FE_EN", lcsc="C25819"); r("R206", "100k", "FE_EN", "GND", lcsc="C25803"); c("C213", "2.2n", "FE_EN", "GND", lcsc="C16033")   # U2 pin 1: 0.68 of FE_RUN, at least 44 us to fall through VEN(OP) against the latch's 18 us
part("Q37", "Transistor_FET", "2N7002", "2N7002: FE_RUN high = bleed off (1 G, 2 S, 3 D)", "SOT23", {"1": "FE_RUN", "2": "GND", "3": "FE_BLEED_G"}, "C8545")
r("R201", "100k", "FE_VZ", "FE_BLEED_G", lcsc="C25803")
nfet("Q38", "CSD19532Q5B 100 V N-FET (the VBUS20 bleed switch)", "FE_BLEED_G", "FE_BLEED", "GND", lcsc="C473333")
for _rb in ("R202", "R203", "R204", "R205"):
    r(_rb, "510R 1W 2512 (VBUS20 bleed)", "VBUS20", "FE_BLEED", "RS2512", lcsc="C36171")
_intent.node("FE_GVDD", _GVIN, _gw + "U34's VDD, VIN_RAW behind R196 (1 k at 2.6 uA: millivolts); the clamp's 64.5 V is inside VDD's 65 V")
_intent.node("FE_UVS", round(_GVIN * 10 / 101, 2), _gw + "SENSE2, VIN_RAW over R14 / R15 (10 / 101 of it)")
_intent.node("FE_LATCH", 20.7, _gw + "SENSE1 on VBUS20 through R197 when Q36 is off (VBUS20's 20.7 V maximum); 0 V while the stage runs")
_intent.node("FE_CTR2", 5.5, _gw + "U34's CTR2 delay capacitor: SNVSBJ1E recommends 0 to 5.5 V on the pin (6 V absolute)")
_intent.node("FE_VZ", 12.7, _gw + "VIN_RAW through R200 clamped by D22, BZT52C12 11.4 to 12.7 V (DS18004)")
_intent.node("FE_RUN", 12.7, _gw + "U34's two open-drain RESET outputs pulled to FE_VZ by R198")
_intent.node("FE_EN", 8.9, _gw + "U2's EN/UVLO pin, FE_RUN (at most FE_VZ's 12.7 V) over R199 / R206, 0.68 of it, plus the pin's own 7 uA into 32 k (0.2 V)")
_intent.node("FE_BLEED_G", 12.7, _gw + "Q38's gate, FE_VZ through R201 while Q37 is off")
_intent.node("FE_BLEED", 20.7, _gw + "Q38's drain, VBUS20 through the four 510 Ohm bleed resistors (VBUS20's 20.7 V while Q38 is off)")
# --- charger BQ25731 (bq25731-datasheet.pdf, QFN-32 RSN; no BATFET, so the system sits on VSYS and the pack on the far side of RSR, SLUSE66A Figure 10-1): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,
#     charge inhibited by pulling ILIM_HIZ low through Q6 (the SHORE_INHIBIT function of PANEL.md section 9 becomes CHG_INHIBIT on the expander); cell count set on CELL_BATPRESZ
ic("U3", 33, "BQ25731RSNR 1 to 5 cell buck-boost charger, 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {
 "1": "VBUS20", "2": "CH_ACN_F", "3": "CH_ACP_F", "4": "CHRG_OK", "5": "GND", "6": "CHG_ILIM", "7": "CH_VDDA", "8": "IADPT", "9": "IBAT", "10": "PSYS", "11": "PROCHOT", "12": "SDA", "13": "SCL",
 "14": "GND", "15": "NC", "16": "CH_COMP1", "17": "CH_COMP2", "18": "CH_CELL", "19": "CH_SRN_F", "20": "CH_SRP_F", "21": "NC", "22": "VBAT", "23": "CH_SW2", "24": "CH_HIDRV2", "25": "CH_BTST2", "26": "CH_LODRV2",
 "27": "GND", "28": "REGN", "29": "CH_LODRV1", "30": "CH_BTST1", "31": "CH_HIDRV1", "32": "CH_SW1", "33": "GND"}, "C2871872")
for _qr, _g, _d, _s in (("Q7", "CH_HIDRV1", "CH_ACN", "CH_SW1"), ("Q8", "CH_LODRV1", "CH_SW1", "GND"), ("Q9", "CH_LODRV2", "CH_SW2", "GND"), ("Q10", "CH_HIDRV2", "VBAT", "CH_SW2")): nfet(_qr, "CSD18510Q5B 40 V N-FET", _g, _d, _s)
part("L2", "Device", "L", "3.3uH XAL6030-332ME (Isat 12.2 A)", "L6060", {"1": "CH_SW1", "2": "CH_SW2"})
r("R16", "10mOhm 1% 2512 (RAC, input current sense)", "VBUS20", "CH_ACN", "RS2512"); r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "VBAT", "CELL_FUSED", "RS2512")
# S-04, 26 September 2026: R17 now carries the pack's DISCHARGE current as well as its charge current, because the
# system is on its converter side. At the pack's 10 A typical it dissipates 0.50 W, at the 18 A peak 1.62 W and at
# the provisional all-transmit-with-outlets 22 A (W2 F-PR-03) 2.42 W, against the 3 W rating of the fitted part
# (LCSC C500739, Milliohm LR2512D-3W-5mR-1%, read back from the JLCPCB API on 26 September 2026; its maker's
# datasheet is not held, an open item). 110 mV at 22 A is inside the SRP-SRN rating, and the charger's own
# discharge-current reading and PROCHOT comparators now see the kit's whole load, which is what TI's topology is for.
# THE SENSE FILTERS THE CHARGER'S OWN DATASHEET ASKS FOR, and did not have (16 September 2026, rule ANA-001).
# The BQ25731's pin table is explicit on both pairs. ACP and ACN: "A RC low-pass filter is required to be
# placed between the sense resistor and the ACN pin to suppress the high frequency noise in the input current
# signal", with section 10.2.2.2 asking for a time constant between 47 and 200 ns and 10 nF differential at a
# 400 kHz switching frequency. SRN: "Connect a 0.1-uF filter cap across battery charging sensing resistor and
# use 10-Ohm contact resistor between SRN pin and battery charging sensing resistor."
# Until today both pairs went straight from the shunt to the pin: the amplifier saw the ringing the datasheet
# warns overwhelms the sensed current, and the note says that can push the average-current loop into
# oscillation. 10 Ohm into each pin with 10 nF across the input pair is 100 ns, inside the window; the charge
# pair takes the 0.1 uF the same page asks for. VSYS (pin 22) stays on the system node itself: it is a voltage
# sense and not part of either current pair.
# The VALUES are bare. A value is the BOM's Comment column and the key both `lcsc_fill.py`'s map and the
# certified table are read with, and "10n (CDIFF across the input sense)" matches the rule `^10n$` in neither:
# the four resistors and two capacitors would have reached the BOM as blank lines and the finish would have
# refused the board for them. "10R", "10n" and "100n" are CERTIFIED already (C22859, C57112, C14663), so the
# filter carries the parts the rest of this board carries. The reasoning is the comment above, not the value.
r("R146", "10R", "CH_ACN", "CH_ACN_F")          # ACN filter, BQ25731 10.2.2.2
r("R147", "10R", "VBUS20", "CH_ACP_F")          # ACP filter, the same RC into the other input sense pin
c("C121", "10n", "CH_ACP_F", "CH_ACN_F")        # CDIFF across the input sense: 100 ns with the 10 R, inside the datasheet's 47 to 200 ns
r("R148", "10R", "CELL_FUSED", "CH_SRN_F")      # the contact resistor the SRN pin's own note asks for; SRN is the battery side (S-04, 26 Sep 2026)
r("R149", "10R", "VBAT", "CH_SRP_F")            # the same on SRP, so the pair sees one filter and not a half; SRP is the system side, VSYS (S-04, 26 Sep 2026)
c("C122", "100n", "CH_SRP_F", "CH_SRN_F")       # the 0.1 uF across the charge sense resistor, BQ25731 pin 19
c("C16", "100n 25V", "CH_BTST1", "CH_SW1"); c("C17", "100n 25V", "CH_BTST2", "CH_SW2"); c("C18", "3.3u", "REGN", "GND", "C10u"); r("R18", "10R", "REGN", "CH_VDDA"); c("C19", "1u", "CH_VDDA", "GND")
# R4A-N8 (second fix-up, 26 September 2026): THE CHARGER'S INPUT CAPACITORS WERE ON THE WRONG SIDE OF RAC. C20 to C22
# sat on CH_ACN, between R16 and the half bridge. SLUSE66A 10.2.2.4: the input capacitor "should be placed in front
# of RAC current sensing and as close as possible to the power stage half bridge MOSFETs", and "Capacitance after
# RAC before power stage half bridge should be limited to 10 nF + 1 nF ... Because too large capacitance after RAC
# could filter out RAC current sensing ripple information"; Figure 10-1 draws 6 x 10 uF at VBUS and Figure 10-3 the
# 10 nF and 1 nF at Q1's drain. With 15 uF behind 10 mOhm and the copper's inductance, the average-current loop that
# 10.2.2.2 says needs the input ripple read a filtered current. C20 to C22 now sit on VBUS20 (with the front end's
# ceramics: the six 10 uF of Figure 10-1 and more, see the FE stage above), and C190 (10 nF) and C191 (1 nF), the
# certified 0603 50 V parts (C57112, C1588), are the half bridge's own decoupling at Q7's drain. A layout item: all
# of them close to the half bridge, C20 to C22 on R16's VBUS20 pad (O-01).
# THE VALUE TEXT NAMES THE PART THAT IS BOUGHT (third fix-up, the re-review's minor item 5): "10u 35V 1210" was mapped by
# lcsc_fill.py to C596319, YAGEO CC1210KKX7R9BB106, a 10 uF 50 V X7R part, so the schematic said 35 V and the board would
# carry 50 V. The text is now the FE stage's own "10u 50V X7R 1210", the same certified code, and the ripple model's
# ceramic band is one band for every ceramic on VBUS20.
for k in range(3): c("C%d" % (20 + k), "10u 50V X7R 1210", "VBUS20", "GND", "C1210")
c("C190", "10n", "CH_ACN", "GND", lcsc="C57112"); c("C191", "1n", "CH_ACN", "GND", lcsc="C1588")
for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "VBAT", "GND", "C1210")   # the charger's VSYS capacitors, at Q10's drain (S-04, 26 Sep 2026)
r("R19", "16.5k 1%", "REGN", "CHG_ILIM"); r("R20", "34.8k 1%", "CHG_ILIM", "GND"); part("Q6", "Transistor_FET", "2N7002", "2N7002: CHG_INHIBIT high = ILIM_HIZ low = charger in HiZ", "SOT23", {"1": "CHG_INHIBIT", "2": "GND", "3": "CHG_ILIM"}); r("R21", "4.7k", "CHG_INHIBIT", "GND")   # S-08, 26 September 2026: 4.7k, see the pull-down note at U26
r("R22", "10k", "CHRG_OK", "+3V3"); r("R23", "10k", "PROCHOT", "+3V3"); r("R24", "10k (PSYS load)", "PSYS", "GND"); r("R25", "10k", "CH_COMP1", "CH_COMP1C"); c("C26", "10n", "CH_COMP1C", "GND"); c("C27", "1n", "CH_COMP2", "GND")
# S-03, 26 September 2026 (W2 F-CH-01, adjudication A02): THE STRAP READ 2S. 60.4k over 40.2k puts CELL_BATPRESZ at
# 39.96 percent of VDDA (39.48 to 40.44 at 1 percent), inside SLUSE66A 8.5's VCELL_2S window of 35 / 40 / 48.5
# percent, so the charger loaded 8.4 V, a 12 V SYSOVP and would latch off against a 4S pack. Swapping the two gives
# 60.04 percent, which is 3S. 13.3k over 40.2k gives 75.14 percent (74.76 to 75.51 at 1 percent), inside VCELL_4S
# 68.4 / 75 / 81.5 percent: ChargeVoltage 16.8 V, SYSOVP and VSYS_MIN at their 4S defaults (Table 9-2). R26 is
# UNI-ROYAL 0603WAF1332T5E, 13.3 k 1 percent 0603, LCSC C25952 (JLCPCB API, 26 September 2026).
r("R26", "13.3k 1% (CELL_BATPRESZ: 4S, 75 percent of VDDA)", "CH_VDDA", "CH_CELL", lcsc="C25952"); r("R27", "40.2k 1%", "CH_CELL", "GND")
# THE CHARGER'S OWN NON-RAIL NETS (16 September 2026, rule CMP-001). Same shape as the LM5176 stages above and
# the same topology: Q7's drain is the input node, Q10's the output node, the two SW nodes swing between them
# and ground, and each BTST rides on its own SW at REGN. The pack ceiling is 16.8 V and not the 14.4 the rail
# declares: VBAT is declared at its NOMINAL voltage, which is the right number for a drop budget and the wrong
# one for a part's rating, and 4S lithium ion terminates at 4.2 V a cell.
_CELL_MAX = 16.8
# CH_ACN IS A SUPPLY AND WAS DECLARED AS A NODE, SO NOTHING SOLVED IT (20 September 2026). `node()` says in
# its own first line that it describes a net that is NOT a rail; this one has a voltage, a current, a source
# and a load, and it carries the charger's whole 6.0 A from R16's far pad to the buck-boost's high-side FET.
# Declared as a node, `dc_drop` solved no potential on it at all, so **a 6 A conductor on this board was
# judged by neither PI-001 nor PI-002**, and `kelvin_check` could not measure the LOW half of the charger's
# input sense either: it reads "the mesh solved no pad of CH_ACN on this board". `derate` reads a rail's
# voltage in preference to a node's, so CMP-001 keeps the same 20 V it had.
_intent.rail("CH_ACN", 20.0, 6.0, 8.0, "R16", loads={"Q7": 6.0}, v_work=20.0, converted=False,
             series_of="VBUS20",
             note="the charger's input node BEHIND the 10 mOhm input shunt R16: the same 20 V charge bus as "
                  "VBUS20 and the same 6.0 A, from the shunt's far pad to the BQ25731's high-side FET Q7 and "
                  "the half bridge's 10 nF and 1 nF (R4A-N8, 26 September 2026: the three 10 uF input capacitors are on "
                  "VBUS20, in front of the shunt, as SLUSE66A 10.2.2.4 asks). VBUS20 is the rail INTO the shunt (source R11, load R16) and "
                  "this is the rail out of it: DIFFERENT COPPER, which is why both need judging, and the SAME "
                  "WATTS, which is why this one is declared a series segment of VBUS20 so the board's power "
                  "total counts the path once. Declared 20 September 2026 because it had been a `node`, which is documented as a "
                  "net that is not a rail, and the consequence was that nothing solved it: no PI-001, no "
                  "PI-002, and no low-side reading for the Kelvin report")
# CH_SRP IS GONE (S-04, 26 September 2026). It was the charger's output node between Q10's drain and the RSR shunt
# R17, declared on 20 September as the second of the sixteen DC conductors that had been nodes. In TI's topology
# that node IS the system node, so Q10's drain, the three 22 uF VSYS capacitors, R17's system pad, R149 and the
# VSYS sense pin 22 are on VBAT now, and the pack's copper between the blade and the shunt is CELL_FUSED, declared
# with the pack rails at the top of this file. Every number the 20 September note carried (10.0 A typical, 18.0 A
# peak, the 4S termination as v_work) is carried by those two declarations.
_intent.node("CH_SW1", 20.0, "BQ25731 buck-side switching node: it reaches the 20 V input bus", v_min=-1.0)
_intent.node("CH_SW2", _CELL_MAX, "BQ25731 boost-side switching node: it reaches the pack", v_min=-1.0)
_intent.node("CH_BTST1", 26.0, "the bootstrap rides on CH_SW1 at REGN, the charger's own 6 V regulator",
             rides_on="CH_SW1", bias_v=6.0)
_intent.node("CH_BTST2", _CELL_MAX + 6.0, "the bootstrap rides on CH_SW2 at REGN",
             rides_on="CH_SW2", bias_v=6.0)
_intent.node("REGN", 6.0, "the BQ25731's own 6 V regulator output, which supplies both gate drivers")
_intent.node("CH_VDDA", 6.0, "the charger's analogue supply, REGN through R18")
_intent.node("GND", 0.0, "the board's reference. It is declared so that a part between a live net and ground "
             "is judged against the live net rather than reported as sitting on an undeclared one")
# --- per-slot 5 V rails: Diodes AP64500SP-13 (diodes/diodes-ap64500.pdf, SO-8 with exposed pad; pins 1 BST 2 VIN 3 EN 4 RT/CLK 5 FB 6 COMP 7 GND 8 SW 9 pad; 3.8 to 40 V in, 5 A,
#     Vref 0.8 V, 5.1 V from 53.6k/10k), enable from the panel controller over J_AB1, INA226 on each output (ti-ina226.pdf, VSSOP-10; pins 1 A1 2 A0 3 ALERT 4 SDA 5 SCL 6 VS 7 GND 8 VBUS 9 IN- 10 IN+)
def buck5(n, uref, en, out, refs, ina, a1, a0):
    L, cb, ci1, ci2, co1, co2, co3, rt, rb, rpg, rsh, rrt, rco, cco = refs
    ic(uref, 9, "AP64500SP-13 5 A buck, 5.1 V rail %s" % out, "SO8EP", {"1": "S%s_BOOT" % n, "2": "VBAT", "3": en, "4": "S%s_RT" % n, "5": "S%s_FB" % n, "6": "S%s_COMP" % n, "7": "GND", "8": "S%s_SW" % n, "9": "GND"}, "C2070920")
    part(L, "Device", "L", "4.7uH XAL6060-472ME (Isat 11 A)", "L6060", {"1": "S%s_SW" % n, "2": "S%s_OUT" % n}); c(cb, "100n", "S%s_BOOT" % n, "S%s_SW" % n)
    c(ci1, "10u 25V 1210", "VBAT", "GND", "C1210", bypass=(uref, "2")); c(ci2, "10u 25V 1210", "VBAT", "GND", "C1210", bypass=(uref, "2"))   # the buck's VIN pin
    for cr in (co1, co2, co3): c(cr, "22u 10V X7R 1210", out, "GND", "C1210")
    r(rt, "53.6k 1%", out, "S%s_FB" % n); r(rb, "10k 1%", "S%s_FB" % n, "GND"); r(rrt, "68k (RT: 500 kHz)", "S%s_RT" % n, "GND"); r(rco, "22k", "S%s_COMP" % n, "S%s_COMPC" % n); c(cco, "3.3n", "S%s_COMPC" % n, "GND")
    r(rsh, "5mOhm 1% 2512 (shunt)", "S%s_OUT" % n, out, "RS2512"); r(rpg, "100k", en, "GND")   # a slot with no controller line stays off
    ic(ina, 10, "INA226 rail monitor %s" % out, "VSSOP10", {"1": a1, "2": a0, "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": out, "9": out, "10": "S%s_OUT" % n}, "C49851")
    # THE FOUR BUCK5 OUTPUTS ARE THE LM5176 HELPER'S DEFECT IN THE OTHER HELPER (20 September 2026, found by
    # `power_path` asking every board mechanically rather than by reading a generator; appendix 32.237).
    # `S<n>_OUT` is the conductor between the inductor and the 5 mOhm shunt, carrying the whole of this
    # stage's 2.50 A (3.80 on the device rail), and it was declared as NOTHING AT ALL, so `dc_drop` solved
    # nothing on it and neither PI-001 nor PI-002 had looked at it. The source is the INDUCTOR, which is where
    # the current really leaves, never the controller, whose pin on this net is a feedback tap.
    # The switching node is declared too, as the node it is: a drop budget in percent means nothing on it,
    # but CMP-001 asks what voltage a part on a net can see and it swings to VBAT.
    _t, _p = _intent.rail_amps(out)
    _intent.rail("S%s_OUT" % n, _intent.rail_volts(out), _t, _p, L, loads={rsh: _t}, series_of=out,
                 converted=False, v_work=_intent.rail_volts(out),
                 note="the AP64500 stage's output between the inductor %s and the 5 mOhm shunt %s, at the "
                      "whole of the rail's own current. Declared 20 September 2026: it had been declared as "
                      "nothing at all" % (L, rsh))
    _intent.node("S%s_SW" % n, _intent.rail_volts("VBAT"),
                 "the AP64500's switching node on the %s stage: it swings to VBAT, the pack node that feeds "
                 "the buck, and a diode drop below ground on the other half of the cycle" % out, v_min=-1.0)
buck5("1", "U4", "SLOT_EN1", "+5V_S1", ["L3", "C28", "C29", "C30", "C31", "C32", "C33", "R28", "R29", "R30", "R31", "R45", "R129", "C112"], "U8", "GND", "GND")        # 0x40
buck5("3", "U6", "SLOT_EN3", "+5V_S3", ["L5", "C40", "C41", "C42", "C43", "C44", "C45", "R36", "R37", "R38", "R39", "R47", "R131", "C114"], "U10", "+3V3", "GND")      # 0x44
# F-PR-04, 26 September 2026 (MESHSAT-1357; W2 F-PR-04): SLOT 2 AND THE DEVICE RAIL LEAVE THE AP64500. The AP64500
# is a 5 A part (Diodes DS41979 Rev 5-2: "5A Continuous Output Current", HS peak limit 6.8 / 8 / 9.2 A, theta-JA
# 45 C/W in SO-8EP). +5V_DEV was declared at 6.0 A peak on it (VERIFIED over rating) and D-12's host port adds
# 0.9 A; slot 2 sums to about 5.8 A in a 5G burst (the RM520N's 4 A peak through B's 3.3 V buck, INFERRED) and to
# 5.0 A with every load at its continuous maximum. Two options were weighed: SPLIT the device rail (W2's first
# recommendation; it needs board B to re-feed three radios from a second lead, and it cannot help slot 2, whose one
# module is the one load), or a BIGGER CONVERTER. The bigger converter is this board's own LM5176 stage, the part
# already certified five times here (C442493, datasheet held, every land in the KiCad library), which needs no
# change on board B and no new footprint. Its average current loop limits at 43 to 57 mV across the ISNS shunt
# (SNVSAI1D VSNS): 7.2 to 9.5 A across 6 mOhm, above both peaks and below the JST-VH lead's 10 A. The 6 mOhm shunt
# is a Vishay WSL25126L000FEA (WSL2512, 1.0 W at 70 C, AEC-Q200, Vishay 30100 rev 23-Nov-2023,
# drafts/datasheets/vishay-wsl.pdf), 0.54 W at the 9.5 A ceiling; LCSC C843882. It is also the INA226's shunt, as
# the 5 mOhm AP64500 shunt was, so the monitor's calibration changes (a firmware item). The FETs are the front end's
# CSD19532Q5B (SLPS414B, held at v2/vendor/power/ti-csd19532q5b-n-fet.pdf; 100 V, 4.6 mOhm at VGS 6 V, 48 nC at
# 10 V; C473333) and not the PA stage's CSD18510Q5B (118 nC typical, 153 nC maximum at 10 V, SLPS632): in buck mode
# two gates switch at 206 kHz (RT 40.2 k, Equation 5) from the LM5176's VCC, whose current limit is 65 mA minimum
# (SNVSAI1D, IVCC), and about 35 nC each at the 7.35 V VCC is about 14 mA where the CSD18510Q5B would take about 41
# (the round-4 text said 300 kHz, 21 and 60 mA; corrected in the fix-up, the conclusion unchanged). The inductor is the
# PA stage's certified XAL1010-682ME (C3911637); the output capacitors are the 25 V 22 uF 1210 the AP64500 stage
# carried (Samwha CS3225X7R226K250NRL, C2918511). EN/UVLO is driven straight from the enable line (en_div
# False): SLOT_EN2 by the panel through B with R34 holding an absent line off, DEV_EN by U27 with R42 now a
# PULL-UP to board A's +3V3 (S-08), so the device rail comes up whenever MAIN has enabled +3V3, whatever the
# PCA9555's internal pull-up does, and the panel can still shed it by driving the pin low.
# R4A-N6, round 4 fix-up (26 September 2026, review A minor 3): BIAS (pin 24) ON VBAT, NOT ON THE 5.1 V OUTPUT. The
# helper ties BIAS to the stage's own output by default, which is TI's arrangement for outputs above 8.5 V
# ("Connecting the BIAS pin to VOUT in applications with VOUT greater than 8.5 V improves the efficiency",
# SNVSAI1D 7.3.2), and 6.3 recommends BIAS at 8 to 36 V when VCC is in regulation. A 5.1 V output is under both.
# With BIAS on VBAT (10 to 16.8 V, 29 V at the SMCJ18A's clamp, under BIAS's 40 V absolute maximum) the VCC
# regulator draws from BIAS, which is the input anyway, and the pin sits inside its recommended range. The PD stage
# at its 5 V profile is the same case and takes the same fix; FE, PA and HF (20, 13.8 and 12 V) keep BIAS on their
# output, and PoE already has it on VBAT (54 V is over BIAS's 40 V rating).
lm5176("S2", "U5", "VBAT", "+5V_S2", "SLOT_EN2", "53.6k", "L4", "6.8uH XAL1010-682ME (Isat 21.8 A)", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6)", "C473333",
       ["Q28", "Q29", "Q30", "Q31", "R32", "R33", "R46", "C133", "R130", "C113", "C134", "C135", "C136", "C34", "C137", "R35", "R170", "R171", None, None, "C35", "C36", "C37", "C38", "C39", "R172"],
       cs_filter=("R173", "R174", "C138"), isns_filter=("R175", "R176", "C139"), isns="6m", isns_lcsc="C843882",
       cout="22u 25V 1210", cout_lcsc="C2918511", cslope=("470p", "C27694"), boot_diodes=("D5", "D6"), en_div=False,
       bias="VBAT", comp=(("2.2k", "C4190"), ("100n", "C14663"), ("1n", "C1588")), bulk=("C164", "C165", "C166"), bulk_part="E151", bias_cap="C193")   # fix-up: BIAS on VBAT (R4A-N6); loop PM 68, GM 15.1 dB, 2.6 to 9.4 kHz, 72 mOhm against 85
# second fix-up (26 Sep 2026): bulk ripple 0.28 A rms per EEHZK1E151XP, 15 percent of 1.8 A (buck only; bulk_ripple.py); on the widened loop band (Q to 1.5, L +-20 percent) PM 68, GM 9.4 dB
r("R34", "100k", "SLOT_EN2", "GND")   # a slot with no controller line stays off (as the AP64500 stage had it)
ic("U9", 10, "INA226 rail monitor +5V_S2", "VSSOP10", {"1": "GND", "2": "+3V3", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "+5V_S2", "9": "+5V_S2", "10": "S2_OUT"}, "C49851")   # 0x41, across the ISNS shunt R35
lm5176("SD", "U7", "VBAT", "+5V_DEV", "DEV_EN", "53.6k", "L6", "6.8uH XAL1010-682ME (Isat 21.8 A)", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6)", "C473333",
       ["Q32", "Q33", "Q34", "Q35", "R40", "R41", "R115", "C140", "R132", "C115", "C141", "C142", "C143", "C46", "C144", "R43", "R177", "R178", None, None, "C47", "C48", "C49", "C50", "C51", "R179"],
       cs_filter=("R180", "R181", "C145"), isns_filter=("R182", "R183", "C146"), isns="6m", isns_lcsc="C843882",
       cout="22u 25V 1210", cout_lcsc="C2918511", cslope=("470p", "C27694"), boot_diodes=("D7", "D8"), en_div=False,
       bias="VBAT", comp=(("2.2k", "C4190"), ("100n", "C14663"), ("1n", "C1588")), bulk=("C167", "C168", "C169"), bulk_part="E151", bias_cap="C194")   # fix-up: BIAS on VBAT (R4A-N6); loop PM 68, GM 15.1 dB, 2.9 to 9.4 kHz, 72 mOhm against 85
# second fix-up (26 Sep 2026): bulk ripple 0.28 A rms per EEHZK1E151XP, 15 percent of 1.8 A (buck only; bulk_ripple.py); on the widened loop band (Q to 1.5, L +-20 percent) PM 68, GM 9.4 dB
r("R42", "100k", "DEV_EN", "+3V3")   # S-08, 26 September 2026 (A01, W2 F-SQ-01): a PULL-UP to board A's +3V3, not a pull-down
ic("U11", 10, "INA226 rail monitor +5V_DEV", "VSSOP10", {"1": "+3V3", "2": "+3V3", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "+5V_DEV", "9": "+5V_DEV", "10": "SD_OUT"}, "C49851")   # 0x45, across the ISNS shunt R43
for n, out in (("1", "+5V_S1"), ("2", "+5V_S2"), ("3", "+5V_S3")): vh2("J_5V_S%s" % n, "slot %s 5.1 V rail to B16 (JST-VH, 16 AWG): + -" % n, out)
vh2("J_5V_DEV", "USB device rail to B16 (JST-VH): + -", "+5V_DEV")
r("R44", "10k", "INA_ALERT", "+3V3")
# --- 3.3 V logic: TPS62933DRLR (ti-tps62933.pdf, SOT-583; pins 1 RT 2 EN 3 VIN 4 GND 5 SW 6 BST 7 SS 8 FB; Vref 0.8 V, 3.3 V from 31.6k/10k)
ic("U12", 8, "TPS62933DRLR 3 A buck, 3.3 V logic", "SOT583", {"1": "NC", "2": "RAIL_EN", "3": "VBAT", "4": "GND", "5": "B33_SW", "6": "B33_BST", "7": "B33_SS", "8": "B33_FB"}, "C3200405")
# B33_SW IS A SWITCHING NODE AND IT SAID NOTHING (20 September 2026, the same sweep). The TPS62933 feeds the
# 3.3 V logic rail straight off VBAT, so its switching node swings to the pack.
_intent.node("B33_SW", _intent.rail_volts("VBAT"),
             "the TPS62933's switching node: it swings to VBAT, the pack node that feeds the 3.3 V buck, and "
             "a diode drop below ground on the other half of the cycle", v_min=-1.0)
part("L7", "Device", "L", "4.7uH XAL4030-472ME", "L4030", {"1": "B33_SW", "2": "+3V3"}); c("C52", "100n", "B33_BST", "B33_SW"); c("C53", "10n", "B33_SS", "GND"); c("C54", "10u 25V 1210", "VBAT", "GND", "C1210")
c("C55", "22u 10V X7R 1210", "+3V3", "GND", "C1210"); c("C56", "22u 10V X7R 1210", "+3V3", "GND", "C1210"); r("R48", "31.6k 1%", "+3V3", "B33_FB"); r("R49", "10k 1%", "B33_FB", "GND")
kisch.tvs("D3", "SMBJ5.0A", "+3V3", "GND", "TVS")   # TRN-001 / S-09 (ts-tvs, 26 Sep 2026): a one-way part, drawn K/A by kisch.tvs() (Device:D_Zener, K pin 1 on +3V3, A pin 2 on GND; direction from the part number, recorded in the intent under "clamps"); nets, value, land and code as before (lcsc_fill fits MDD C113974, v2/vendor/power/mdd-smbj-series-tvs.pdf)
# --- PA rail: LM5176 from VBAT to 13.8 V at 6 A for the RA30H1317M1 on the face plate (32.56), enabled by the hardware EMCON gate AND the software hold (PA_EN from U26); 40 V FETs
# F-PR-01, 26 September 2026 (MESHSAT-1357; W2 F-PR-01): THE PA RAIL GETS A LIMIT NEAR ITS 6 A PEAK. The stage's
# only limits were its average loop at 50 mV across a 2 mOhm ISNS shunt, 25 A, and its cycle limit at 66 to 94 mV
# across the 5 mOhm CS shunt, 13 to 19 A; 32.55's planned 10 A blade was never drawn. Two options: the blade (a
# Keystone 3568 holder and a 10 A mini blade), or the ISNS resistor. The blade does not act near 6 A at all: a
# fuse carries well over its rating for minutes, so it protects the lead against a hard short only, which the
# cycle limit already bounds. A 6 mOhm ISNS shunt makes the stage's own constant-current loop hold 43 to 57 mV,
# 7.2 to 9.5 A (SNVSAI1D VSNS), above the 6.0 A declared peak and the 5.4 A of a 30 W carrier at 40 percent, below
# the JST-VH lead's 10 A, and it recovers by itself when the overload ends. It costs no part and no land: the same
# 2512 position, a Vishay WSL25126L000FEA (1.0 W, 0.54 W at the 9.5 A ceiling; LCSC C843882). The 45 W / 8.2 A
# bound of W2 F-PR-02 now meets the limit and the rail droops rather than the lead heating; the INA226 U14 shares
# this shunt, so its calibration changes (a firmware item).
lm5176("PA", "U13", "VBAT", "+13V8_PA", "PA_EN", "162k", "L8", "6.8uH XAL1010-682ME (Isat 21.8 A)", "CSD18510Q5B 40 V N-FET", "",
       ["Q11", "Q12", "Q13", "Q14", "R50", "R51", "R52", "C148", "R54", "C57", "C58", "C59", "C60", "C61", "C62", "R55", "R56", "R57", "R58", "R59", "C63", "C64", "C65", "C66", "C67", "R120"], cs_filter=("R152", "R153", "C124"), isns_filter=("R162", "R163", "C129"),
       isns="6m", isns_lcsc="C843882", cslope=("470p", "C27694"), boot_diodes=("D11", "D12"),
       comp=(("6.8k", "C23212"), ("100n", "C14663"), ("1.5n", "C37788")), bulk=("C170", "C171"), bulk_part="E471", bias_cap="C195",
       vin_block=("D20", "C208", "1u", "C15849", "C"))   # third fix-up (R4A-N11): BIAS is +13V8_PA, so pin 2 sits behind D20 with C208 (1 uF 50 V X5R 0603, Samsung CL10A105KB8NNNC) at the pin; VBAT's 16.8 V is well inside both. The fix-up loop: PM 65, GM 12.8 dB, 1.5 to 5.4 kHz, 86 mOhm against 127; round 4, 26 Sep 2026: F-PR-01 (ISNS 6 mOhm) and the helper's two defects (CSLOPE 544 pF dead-beat, 470 pF C0G; R53 retired)
# second fix-up (26 Sep 2026): bulk ripple 2.15 A rms per EEHZK1E471P at 10 V in and 6 A, 77 percent of 2.8 A (Equation 19: 3.7 A for the node; bulk_ripple.py); on the widened loop band PM 63.7, GM 9.9 dB
ic("U14", 10, "INA226 PA rail monitor (0x46)", "VSSOP10", {"1": "+3V3", "2": "SDA", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "+13V8_PA", "9": "+13V8_PA", "10": "PA_OUT"}, "C49851")
vh2("J_PA", "13.8 V to the PA module on the face plate (JST-VH, 16 AWG): + -", "+13V8_PA")
# --- HF rail: a fourth LM5176 stage from VBAT to 12.0 V at 2 A for the QMX (never 13.8 V), enabled by the EMCON gate AND the software hold; FB 140k/10k
lm5176("HF", "U15", "VBAT", "+12V_HF", "HF_EN", "140k", "L9", "6.8uH XAL1010-682ME", "CSD18510Q5B 40 V N-FET", "",
       ["Q15", "Q16", "Q23", "Q24", "R60", "R61", "R62", "C149", "R64", "C68", "C69", "C70", "C71", "C72", "C73", "R65", "R122", "R123", "R124", "R125", "C74", "C108", "C109", "C110", "C111", "R126"], cs_filter=("R154", "R155", "C125"), isns_filter=("R164", "R165", "C130"), isns="10m",
       cslope=("470p", "C27694"), boot_diodes=("D13", "D14"),   # 26 Sep 2026: CSLOPE 544 pF dead-beat, 470 pF C0G; R63 retired
       comp=(("3.3k", "C22978"), ("100n", "C14663"), ("1n", "C1588")), bulk=("C172", "C173"), bulk_part="E151", bias_cap="C196",
       vin_block=("D21", "C209", "1u", "C15849", "C"))   # third fix-up (R4A-N11): BIAS is +12V_HF, so pin 2 sits behind D21 with C209 at the pin. The fix-up loop: PM 67, GM 12.7 dB, 2.5 to 9.1 kHz, 134 mOhm against 300
# second fix-up (26 Sep 2026): bulk ripple 0.55 A rms per EEHZK1E151XP at 10 V in, 31 percent of 1.8 A (bulk_ripple.py); on the widened loop band PM 66.2, GM 8.2 dB
vh2("J_HF", "12.0 V to the QMX HF unit in its lid tray (JST-VH, in the lid harness): + -", "+12V_HF")
# --- PoE rail: LM5176 in boost from VBAT to 54 V at 0.6 A for the TPS23861 PSE on B16 (the port magnetics sit beside the switch chip); 100 V FETs; software enable
# R4A-N7, round 4 fix-up (26 September 2026): THE 22 uH INDUCTOR THIS STAGE NAMED DOES NOT EXIST. The held Coilcraft
# XAL1010 sheet (v2/vendor/power/coilcraft-xal1010.pdf, Document 804-1) lists 0.22 to 15 uH and no XAL1010-223ME,
# JLCPCB's catalogue has no XAL1010-223 (drafts/jlc/jlc-XAL1010_223.json), and jlc-handfit.txt already said its
# "Isat 9 A claim [is] unverified". The stage takes the series' largest part, XAL1010-153ME: 15 uH, Isat 15.5 A,
# Irms 9.9 A (20 C rise), DCR 18.6 mOhm maximum, LCSC C2802562 (XAL1010-153MED, stock 1,362, JLCPCB API
# 26 September 2026). At 10 V in and 0.6 A out the inductor carries 3.24 A average and 2.6 A of ripple at 206 kHz,
# 4.6 A peak, under both ratings. The slope capacitor follows it (Equation 26: 2 uS x 15 uH / (10 mOhm x 5) =
# 600 pF, 560 pF C0G, FH 0603CG561J500NT, C43962, stock 2,936), and Equation 9 puts COMP at 2.48 V at 10 V in and
# full load, under the 3 V ceiling (corrected in the second fix-up: the fix-up wrote 2.59 V; drafts/scripts/
# comp9_corners.py). AT THE TOLERANCE CORNERS the headroom is small: L at -20 percent, fSW 180 kHz, the slope current
# at +24 percent and CSLOPE at -5 percent give 2.84 V at 10 V in and 2.89 V at 9 V, 0.11 to 0.16 V under the ceiling
# (the re-review's minor item 3; round 4's 22 uH and 820 pF gave 2.50 V). Its loop is designed with the 15 uH
# (item (3) of the helper).
lm5176("POE", "U16", "VBAT", "+54V_POE", "POE_EN", "665k", "L10", "15uH XAL1010-153ME (Isat 15.5 A)", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6)", "C473333",
       ["Q17", "Q18", "Q19", "Q20", "R66", "R67", "R68", "C150", "R70", "C75", "C76", "C77", "C78", "C79", "C80", "R71", "R72", "R73", "R74", "R75", "C81", "C82", "C83", "C84", "C85", "R121"], cs_filter=("R156", "R157", "C126"), isns_filter=("R166", "R167", "C131"), isns="20m", rcs="10m", bias="VBAT",
       cout="10u 100V X7R 1210",   # +54V_POE: a 50 V part on a 54 V rail is over its rating (decision 10)
       cslope=("560p", "C43962"), boot_diodes=("D15", "D16"), l_lcsc="C2802562",
       comp=(("4.7k", "C23162"), ("100n", "C14663"), ("470p", "C27694")), cout_extra=("C176", "C177"), bias_cap="C197")   # fix-up loop: five output ceramics, PM 65, GM 13.1 dB, 1.5 to 8.6 kHz, 3.8 Ohm against 4.5   # R69 retired 26 Sep 2026; CSLOPE 560 pF for the 15 uH of R4A-N7 (was 820 pF for the 22 uH part that does not exist)
# second fix-up (26 Sep 2026): no bulk; worst output ceramic 0.37 A rms at 10 V in (bulk_ripple.py); on the widened loop band PM 63.6, GM 12.0 dB
ic("U17", 10, "INA226 PoE rail monitor (0x47)", "VSSOP10", {"1": "+3V3", "2": "SCL", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "NC", "9": "+54V_POE", "10": "POE_OUT"}, "C49851")   # VBUS pin open: 54 V exceeds its 36 V range
vh2("J_54V", "54 V to the PoE injector on B16 (JST-VH): + -", "+54V_POE")
# --- USB-C PD outlet: TPS25740A source controller (ti-tps25740.pdf, VQFN-24 RGE; pins 1 VTX 2 CC1 3 CC2 4 GND 5 HIPWR 6 CTL1 7 CTL2 8 EN9V 9 N/C 10 N/C 11 UFP 12 PSEL 13 DVDD 14 PCTRL 15 GD 16 VAUX
#     17 VDD 18 AGND 19 ISNS 20 VPWR 21 VBUS 22 GDNG 23 GDNS 24 DSCG, pad 25) with a fifth LM5176 stage as the power supply: CTL2 and CTL1 (open drain) switch R(FBL2) and R(FBL1) in
#     parallel with the stage's 20k bottom resistor (section 9.1.4 of the sheet): 5 V idle, 9 V and 15 V on request (45 W, 3 A); GDNG drives the VBUS N-FET, DSCG discharges through 43 Ohm
# The PD stage's output is not a rail: it is regulated to 5, 9 or 15 V on the sink's request through the two
# feedback resistors CTL1 and CTL2 switch in, so its ceiling is the 15 V profile and every part on it is judged
# against that (rule CMP-001, 16 September 2026). PD_SW is the same node behind the VBUS N-FET and PD_VBUS is
# the outlet itself, at the same ceiling.
# THE OUTLET'S WHOLE POWER PATH IS FOUR CONDUCTORS AT 3 A AND ALL FOUR WERE NODES (20 September 2026, the
# eighth to the tenth of the sixteen, with PD_OUT inside the stage helper). The path is Q26's drain tab ->
# PD_OUT -> the stage's ISNS shunt R81 -> PD_VPWR -> the VBUS switch Q27 -> PD_SW -> the outlet's ISNS shunt
# R138 -> PD_VBUS -> J_USBC_OUT, and every one of those nets carries the full 3.0 A of a 45 W outlet. As
# nodes, `dc_drop` solved no potential on any of them and neither PI-001 nor PI-002 looked at 45 W of copper.
#
# THE VOLTAGE STAYS 15 V AND THE BUDGET DOES NOT. The 15 V ceiling is what a part on this net can see and it
# is what CMP-001 must judge against, and it is what the stage's own derivations read to place SW2 and BOOT2;
# but the drop budget is a FRACTION of that number, and the outlet delivers its 3 A at the 5 V profile too,
# where the same copper drop costs three times the fraction. A 2 percent budget at 5 V is 100 mV, which is
# 0.67 percent of 15, so the four conductors declare 0.0067 and are judged at the profile that binds. Taking
# the ceiling as the denominator would have produced a 300 mV bar on a 5 V outlet: a wrong declaration is
# worse than a missing one, because it produces a number.
#
# PD_VPWR is the one of the four whose watts are COUNTED, which is the same place every other stage counts
# its own: the rail on the far side of the stage's ISNS shunt. PD_OUT (inside the stage helper), PD_SW and
# PD_VBUS all say `series_of="PD_VPWR"`, so the board's power total carries this outlet's 45 W once and
# every rule that looks at copper still looks at all four conductors.
_PD_A, _PD_V, _PD_BUDGET = 3.0, 15.0, 0.0067
_intent.rail("PD_VPWR", _PD_V, _PD_A, _PD_A, "R81", loads={"Q27": _PD_A}, v_work=_PD_V, budget=_PD_BUDGET,
             switch="U19", efficiency=0.93, fed_from="VBAT",
             note="the PD supply between the stage's ISNS shunt R81 and the VBUS switch Q27, at the "
                  "TPS25740A's highest advertised profile (5, 9 and 15 V at 3 A, 45 W): the LM5176's "
                  "feedback divider is switched by CTL1 and CTL2, so 15 V is the stage's ceiling and the "
                  "voltage every part on this net is judged against")
_intent.rail("PD_SW", _PD_V, _PD_A, _PD_A, "Q27", loads={"R138": _PD_A}, v_work=_PD_V, budget=_PD_BUDGET,
             converted=False, series_of="PD_VPWR",
             note="the PD supply behind Q27, the VBUS switch, on its way to the outlet's own 10 mOhm ISNS "
                  "shunt R138: the same 3 A and the same 15 V ceiling")
_intent.rail("PD_VBUS", _PD_V, _PD_A, _PD_A, "R138", loads={"J_USBC_OUT": _PD_A}, v_work=_PD_V, budget=_PD_BUDGET,
             converted=False, series_of="PD_VPWR",
             note="the USB-C outlet itself, behind the ISNS shunt and out at J_USBC_OUT: the same 3 A and "
                  "the same 15 V ceiling")
# The PD stage states its own output current because its downstream net is a SEGMENT of this path and not
# the rail that counts it: the other four stages read theirs from the rail past their shunt. 0.93 is the
# efficiency the board's other 40 V LM5176 stages declare, same controller, same CSD18510Q5B FETs, same
# output current class; it is an assertion of this project's and it is the number the PA and HF stages are
# already judged on rather than a second figure nobody wrote down.
lm5176("PD", "U19", "VBAT", "PD_VPWR", "PD_EN", "105k", "L11", "6.8uH XAL1010-682ME", "CSD18510Q5B 40 V N-FET", "",
       ["Q21", "Q22", "Q25", "Q26", "R76", "R77", "R78", "C151", "R80", "C86", "C87", "C88", "C89", "C90", "C91", "R81", "R127", "R128", "R133", "R134", "C92", "C116", "C117", "C118", "C119", "R135"], cs_filter=("R158", "R159", "C127"), isns_filter=("R168", "R169", "C132"), isns="10m", rfb_val="20k 1% (R_FBL)",
       out_budget=_PD_BUDGET, cslope=("470p", "C27694"), boot_diodes=("D17", "D18"),
       bias="VBAT", comp=(("3.3k", "C22978"), ("220n", "C160828"), ("1.5n", "C37788")), bulk=("C174", "C175"), bulk_part="E471", bias_cap="C198")   # fix-up: BIAS on VBAT (R4A-N6, the 5 V profile); loop PM 70, GM 15 dB, 0.65 to 8.4 kHz   # 26 Sep 2026: CSLOPE 544 pF dead-beat, 470 pF C0G; R79 retired
# second fix-up (26 Sep 2026): bulk ripple 1.25 A rms per EEHZK1E471P at 10 V in and 15 V 3 A, 45 percent of 2.8 A (bulk_ripple.py); on the widened loop band PM 70.3, GM 9.85 dB
r("R136", "21.0k 1% (R_FBL2: 9 V when CTL2 is low)", "PD_FB", "PD_CTL2"); r("R137", "14.0k 1% (R_FBL1: 15 V when CTL1 is low too)", "PD_FB", "PD_CTL1")
ic("U18", 25, "TPS25740ARGER USB-C PD source controller, 45 W outlet (5, 9, 15 V at 3 A)", "QFN24", {
 "1": "PD_VTX", "2": "PD_CC1", "3": "PD_CC2", "4": "GND", "5": "PD_DVDD", "6": "PD_CTL1", "7": "PD_CTL2", "8": "PD_DVDD", "9": "GND", "10": "GND", "11": "PD_UFP", "12": "PD_DVDD", "13": "PD_DVDD",
 "14": "PD_VAUX", "15": "PD_GD", "16": "PD_VAUX", "17": "+5V_DEV", "18": "GND", "19": "PD_SW", "20": "PD_VPWR", "21": "PD_VBUS", "22": "PD_GDNG", "23": "PD_SW", "24": "PD_DSCG", "25": "GND"}, "C544309")
nfet("Q27", "CSD18510Q5B 40 V N-FET (VBUS switch)", "PD_GDNG", "PD_VPWR", "PD_SW"); r("R138", "10mOhm 1% 2512 (ISNS)", "PD_SW", "PD_VBUS", "RS2512"); r("R139", "43R 1W 2512 (DSCG)", "PD_DSCG", "PD_VBUS", "RS2512")
# R141 is 698k, not the 700k the stage was drawn with: 700k is not an E96 value, JLCPCB carries
# none in 0603, and 0.3 percent on a gate-bias divider is nothing.
r("R140", "1M (GD to VPWR, 9.1.3)", "PD_VPWR", "PD_GD"); r("R141", "698k", "PD_GD", "GND"); r("R142", "10k", "PD_UFP", "+3V3"); r("R143", "4.7k", "PD_SW_EN", "GND")   # S-14 and S-08, 26 Sep 2026: the expander's software hold, ANDed with OUTLET_OK in U26
c("C93", "100n", "PD_VTX", "GND"); c("C94", "220n", "PD_DVDD", "GND"); c("C95", "100n", "PD_VAUX", "GND"); c("C96", "330p", "PD_CC1", "GND"); c("C97", "330p", "PD_CC2", "GND"); c("C120", "10u 25V 1210", "PD_VBUS", "GND", "C1210")
kisch.tvs("D4", "SMBJ18A (VBUS clamp at the outlet)", "PD_VBUS", "GND", "TVS")   # TRN-001 / S-09 (ts-tvs, 26 Sep 2026): a one-way part, drawn K/A by kisch.tvs() (Device:D_Zener, K pin 1 on PD_VBUS, A pin 2 on GND; direction from the part number, recorded in the intent under "clamps"); nets, value, land and code as before (lcsc_fill fits Littelfuse C151256, v2/vendor/power/littelfuse-smbj-series-tvs.pdf)
# D-12, 26 September 2026 (owner ruling): THE USB-C OUTLET IS POWER ONLY. Its data pair used to arrive on J_USBW,
# the pigtail's data side; that path now goes to the sealed Glenair 233-370 (below, at J_USBW), and this header
# carries VBUS, CC1 and CC2 only. The TPS25740A needs no data lines to negotiate: PD runs on CC.
part("J_USBC_OUT", "Connector_Generic", "Conn_01x05", "wall USB-C outlet, power only (pigtail header): VBUS CC1 CC2 GND GND", "PIN5", {"1": "PD_VBUS", "2": "PD_CC1", "3": "PD_CC2", "4": "GND", "5": "GND"})
# D-17, 26 September 2026 (owner ruling): AN EXTERNAL LOW-CAPACITANCE ESD ARRAY ON CC1 AND CC2, AT THE CONNECTOR.
# Decision 31 relied on the TPS25740A's own CC protection (SLVSDG8B 9.1.1, IEC 61000-4-2 8 kV contact, measured
# "based on implementation" on TI's EVM, which a pigtail from a header is not); the owner ruled to remove that
# residual rather than accept it. TI TPD2E2U06QDBZRQ1 (SLLSEJ9E, October 2022, drafts/datasheets/ti-tpd2e2u06-q1.pdf):
# two channels, SOT-23 (DBZ: pin 1 IO1, pin 2 IO2, pin 3 GND), VRWM 5.5 V and breakdown 6.5 to 8.5 V against the
# CC pins' 5.5 V recommended maximum and 6 V absolute maximum (SLVSDG8B 7.1, 7.3), 1.5 pF typical and 1.9 pF
# maximum line capacitance, which leaves C96 and C97 (330 pF) inside the 200 to 600 pF C(RX) window, IEC 61000-4-2
# 25 kV contact, AEC-Q101, -40 to +125 C. LCSC C488151 (JLCPCB API, 26 September 2026). The land is the KiCad
# SOT-23 this board already uses; the part sits at J_USBC_OUT, between the header and anything else, which is a
# placement item for the next board A phase.
ic("U31", 3, "TPD2E2U06QDBZRQ1 low-capacitance ESD array, USB-C CC1 and CC2 at the connector", "SOT23", {"1": "PD_CC1", "2": "PD_CC2", "3": "GND"}, "C488151")
# --- eFuse switches TPS259631DDAR (power/tps2596.pdf, SO PowerPAD-8; pins 1 GND 2 dVdt 3 EN/UVLO 4 IN 5 OUT 6 FLT 7 ILM 8 OVLO, pad 9): the monitor (VMON, 10 to 35 V input, under 1 A),
#     the pack heater mat (VHEAT), D8's 5 V (+5V_D8 from the device rail)
def efuse(uref, vin, vout, en, flt, refs, ilim, ovlo_top="100k 1%", ovlo_lcsc="", ilim_lcsc=""):
    cd, rilm, rflt, rov1, rov2, cin = refs
    ic(uref, 9, "TPS259631DDAR eFuse %s -> %s (%s)" % (vin, vout, ilim), "DDA8", {"1": "GND", "2": uref + "_DVDT", "3": en, "4": vin, "5": vout, "6": flt, "7": uref + "_ILM", "8": uref + "_OVLO", "9": "GND"}, "C2155778")
    # 12 September 2026: the ILM resistor carried the CURRENT as its value ("1.2 A (ILM)"), so its BOM line named
    # an ampere and no resistance and nothing could buy it. TPS2596 equation 7: RILM = 903 / (ILIM + 0.0112) ohms,
    # which the datasheet's own test conditions confirm (1 A at 909 ohm, 2 A at 453 ohm). 750R for 1.2 A, 909R for
    # 1.0 A, 453R for 2.0 A, each keeping its current in the note.
    # OVLO, 26 September 2026 (S-08, W2 F-SQ-06, adjudication A01): the divider was 100k over 10k on every eFuse,
    # which trips U21 and U22 at VBAT 12.87 to 13.42 V (VOVLO(R) 1.17 / 1.20 / 1.22 V, SLVSET8A), so the monitor
    # and the heater were dark over most of the 4S range, and leaves U23's OVLO pin at 0.46 V on a 5.1 V input,
    # under the 0.5 V recommended minimum. The top resistor is now per call; see the calls below.
    c(cd, "10n", uref + "_DVDT", "GND"); r(rilm, ilim, uref + "_ILM", "GND", lcsc=ilim_lcsc); r(rflt, "10k", flt, "+3V3"); r(rov1, ovlo_top, vin, uref + "_OVLO", lcsc=ovlo_lcsc); r(rov2, "10k 1% (OVLO)", uref + "_OVLO", "GND"); c(cin, "100n", vin, "GND")
# U21 and U22 on VBAT: 143k over 10k (A01's proposal, verified here) trips at 1.17 x 15.3 = 17.9 V to 1.22 x 15.3 =
# 18.7 V nominal, and 17.6 to 19.0 V with both resistors at their 1 percent extremes: above the 16.8 V 4S
# termination with 0.8 V in hand, and at or under the TPS2596's 19 V recommended maximum input (21 V absolute).
# It releases at 16.2 to 17.6 V. At 14.4 V the OVLO pin sits at 0.94 V, inside its 0.5 to 2 V range. 143 k is
# UNI-ROYAL 0603WAF1433T5E, 1 percent 0603, LCSC C22877 (JLCPCB API, 26 September 2026).
efuse("U21", "VBAT", "VMON", "MON_EN", "MON_FLT", ["C98", "R90", "R91", "R92", "R93", "C99"], "750R 1% (ILM: 1.2 A)", ovlo_top="143k 1%", ovlo_lcsc="C22877"); vh2("J_MON", "monitor supply lead to the Xenarc (JST-VH): + -", "VMON")
# F-PR-06, 26 September 2026 (W2 F-PR-06): THE HEATER MAT GETS A REGULATED 12 V RAIL. The mat is an RS PRO 245-556,
# "Power Rating 7.5W", "Supply Voltage 12V dc" (rs-pro-245-556-heater-mat-sheet.pdf): 19.2 Ohm, so VBAT drove it at
# 10.8 W at 14.4 V and 14.7 W at 16.8 V, 196 percent of its rating, once the OVLO fix above lets U22 conduct. Three
# options: a firmware duty limit of (12 / VBAT)^2 on HEAT_EN (a crashed panel leaves the mat at 196 percent), a
# series element (7.7 Ohm and 3 W of heat at 16.8 V, or U22 in current limit dissipating the same 3 W until its
# thermal shutdown cycles), or a regulated rail. The regulated rail is the only one that bounds the mat's power in
# hardware at every pack voltage, and it is a part this board already carries: a TPS62933DRLR (SLUSEA4D, held;
# 3.8 to 30 V in, 0.8 to 22 V out, 3 A, SOT-583, LCSC C3200405) behind U22, which keeps the switch, the 1.0 A
# input limit, the fault line and the OVLO. TI's Table 10-2 row for 12 V at 500 kHz: 140 k over 10 k, 12 uH
# typical, 15 uF typical and 10 uF minimum effective output capacitance. Fitted: 140k/10k (12.0 V), a Coilcraft
# XAL4040-153ME, 15 uH (the larger value keeps the current-mode loop's slope margin; Isat 2.9 A against a 0.9 A
# peak), two 22 uF 25 V 1210 (about 18 uF effective at 12 V), RT open (500 kHz, Table 9-1), SS 10 nF (TI's
# minimum is 6.8 nF), and EN on a 100k over 20k divider from VHEAT_IN: it starts at about 7.3 V (VEN_RISE 1.21 V
# typical, 1.28 V maximum, x 6) and sits at 2.8 V at 16.8 V and 3.2 V at the 19 V OVLO ceiling, inside EN's 5.5 V
# recommended maximum (SLUSEA4D 8.3). A floating EN would also enable it (pin table), but a defined enable is what
# the power-sequence rule can read, and it keeps the buck off while the eFuse output is still ramping. Below about 12.9 V of VBAT the buck runs at its maximum duty and the mat
# simply gets less than 7.5 W, which is the safe direction.
efuse("U22", "VBAT", "VHEAT_IN", "HEAT_EN", "HEAT_FLT", ["C100", "R94", "R95", "R96", "R97", "C101"], "909R 1% (ILM: 1.0 A)", ovlo_top="143k 1%", ovlo_lcsc="C22877")
ic("U33", 8, "TPS62933DRLR 3 A buck, 12.0 V heater rail", "SOT583", {"1": "NC", "2": "HT_EN", "3": "VHEAT_IN", "4": "GND", "5": "HT_SW", "6": "HT_BST", "7": "HT_SS", "8": "HT_FB"}, "C3200405")
r("R193", "100k", "VHEAT_IN", "HT_EN"); r("R194", "20k 1%", "HT_EN", "GND")
part("L12", "Device", "L", "15uH XAL4040-153ME (Isat 2.9 A)", "L4040", {"1": "HT_SW", "2": "VHEAT"})
c("C157", "100n", "HT_BST", "HT_SW"); c("C158", "10n", "HT_SS", "GND")
c("C159", "10u 25V 1210", "VHEAT_IN", "GND", "C1210", bypass=("U33", "3")); c("C160", "100n", "VHEAT_IN", "GND")
c("C161", "22u 25V 1210", "VHEAT", "GND", "C1210"); c("C162", "22u 25V 1210", "VHEAT", "GND", "C1210")
r("R191", "140k 1%", "VHEAT", "HT_FB"); r("R192", "10k 1%", "HT_FB", "GND")
part("J_HEAT", "Connector_Generic", "Conn_01x02", "JST-XH 1x2 socket: the pack heater mat (12 V, 7.5 W), fed a regulated 12.0 V: + and -", "XH2", {"1": "VHEAT", "2": "GND"}, "C265283")
_intent.rail("VHEAT_IN", 14.4, 0.58, 0.9, "U22", source_ic="U22 is a TPS2596 eFuse: its OUT pin IS the power path, which is what an eFuse is",
             loads={"U33": 0.58}, fed_from="VBAT", converted=False, v_work=16.8, budget=0.03,
             note="F-PR-06, 26 September 2026: the heater branch between the eFuse U22 and its 12 V buck U33, at VBAT; 7.5 W / 0.9 / 14.4 V = 0.58 A typical, 0.65 A at the 12.9 V edge of regulation (below it the buck is at maximum duty and the mat takes less), under U22's 1.0 A limit")
_intent.rail("VHEAT", 12.0, 0.63, 0.63, "L12", loads={"J_HEAT": 0.63}, switch="U33", efficiency=0.90, fed_from="VHEAT_IN", budget=0.03,
             note="F-PR-06, 26 September 2026: the heater mat's regulated 12.0 V, 0.63 A into its 19.2 Ohm at the mat's own 7.5 W rating")
_intent.node("HT_SW", 16.8, "the heater buck's switching node: it swings to VBAT through U22, and a diode drop below ground", v_min=-1.0)
# U23 on +5V_DEV (S-08, 26 September 2026): 40.2k over 10k trips at 5.87 to 6.12 V nominal and releases at 5.42 to 5.67 V (5.33 V at the 1
# percent extremes), above the 5.09 V rail and its 2 percent, and puts its OVLO pin at 1.01 V, inside the 0.5 to 2 V
# the sheet recommends (the minor half of F-SQ-06). 40.2 k is C12447, certified on this board already.
efuse("U23", "+5V_DEV", "+5V_D8", "D8_EN", "D8_FLT", ["C102", "R98", "R99", "R100", "R101", "C103"], "453R 1% (ILM: 2.0 A)", ovlo_top="40.2k 1%", ovlo_lcsc="C12447"); vh2("J_MEZZ_PWR1", "D8 mezzanine 5 V (JST-VH): + -", "+5V_D8")
# --- hardware EMCON gates: SN74LVC08APWR quad AND (TSSOP-14: 1 1A 2 1B 3 1Y 4 2A 5 2B 6 2Y 7 GND 8 3Y 9 3A 10 3B 11 4Y 12 4A 13 4B 14 VCC).
#     EMCON_HW is active LOW (low silences) and this board only READS it: gate 3 used to drive TX_INHIBIT_n from EMCON_HW, which closed a
#     one-inversion loop through C7's inverter and put a push-pull output on the same net as the panel's mechanical toggle. Deleted 9 September
#     2026 (red team C1); C7 now buffers rather than inverts, so the sense these two gates were always built on is the sense the panel sends.
#     The 10k pull-UP is gone with it: an unplugged ribbon must inhibit, so both lines are pulled DOWN here, as D9 already pulled TX_INHIBIT_n.
# S-14, 26 September 2026 (MESHSAT-1357; W2 F-PR-03, owner ruling D-11): KEYING THE PA DROPS THE PoE AND USB-C
# OUTLETS IN HARDWARE. D-11 lets every radio transmit at once for a declared key-down time above a declared state
# of charge with the outlets at their minimum contract, and asks for a hardware interlock that drops the outlets
# while the PA keys; the thresholds themselves are firmware. The PA keys exactly when board D's PA_KEY = KEY AND
# PA_EN is high (gen_sch_d.py U14), and both halves are on this board: TR_APRS is D's KEY line through 100 R
# (gen_sch_d.py R48, active high, pulled down here by R116) and PA_EN is this board's own gate 1 output. So:
#   U30 (SN74LVC1G00DBVR NAND): OUTLET_OK = NOT (TR_APRS AND PA_EN), low while the PA keys.
#   U26's two spare gates, which were tied off: POE_EN = POE_SW_EN AND OUTLET_OK, PD_EN = PD_SW_EN AND OUTLET_OK.
# The expander bits that were POE_EN and PD_EN are renamed POE_SW_EN and PD_SW_EN, the software hold, as PA_SW_EN
# and HF_SW_EN already are; the LM5176 EN pins keep their net names. An exciter keyed with the PA rail off, or
# board D absent (TR_APRS pulled down), leaves the outlets alone. SN74LVC1G00: TI SCES212AC (revised August 2026,
# drafts/datasheets/ti-sn74lvc1g00.pdf), DBV pin 1 A, 2 B, 3 GND, 4 Y, 5 VCC, 1.65 to 5.5 V, -40 to +125 C; LCSC
# C7826 (JLCPCB API, 26 September 2026); the KiCad SOT-23-5 land. The 74LVC08 pin map is SCAS283W's PW pinout,
# which the comment above U26 already carries.
ic("U26", 14, "SN74LVC08APWR quad AND: EMCON gates for the PA and HF rails, the outlet interlock for PoE and USB-C", "TSSOP14", {
 "1": "EMCON_HW", "2": "PA_SW_EN", "3": "PA_EN", "4": "EMCON_HW", "5": "HF_SW_EN", "6": "HF_EN", "7": "GND", "8": "POE_EN", "9": "POE_SW_EN", "10": "OUTLET_OK", "11": "PD_EN", "12": "PD_SW_EN", "13": "OUTLET_OK", "14": "+3V3"}, "C465737")
ic("U30", 5, "SN74LVC1G00DBVR NAND: OUTLET_OK = NOT (TR_APRS AND PA_EN), the outlet interlock", "SOT235", {"1": "TR_APRS", "2": "PA_EN", "3": "GND", "4": "OUTLET_OK", "5": "+3V3"}, "C7826"); c("C153", "100n", "+3V3", "GND")
# S-08, 26 September 2026 (adjudication A01, W2 F-SQ-07, W5-F1): the pull-downs on the expander-driven enables are
# 4.7 k, not 100 k. The TI PCA9555 pulls every undriven I/O up through about 100 k at power-up (SCPS131J 8.1 and
# Fig 8-2) and specifies IIL only as a maximum of 100 uA, so against 100 k these lines sat at 1.6 to 1.9 V, inside
# the LVC08's 0.8 to 2.0 V band and the 2N7002's 1.0 to 2.5 V threshold. Against 4.7 k the worst case is 0.49 V
# (A01 node_calc: 100 uA x 4.7 k), under every OFF threshold, at 0.71 mA per line driven high. R114 and R143 join
# the list because the interlock above made POE_SW_EN and PD_SW_EN logic inputs where the LM5176's 10 k used to hold
# them.
r("R102", "100k", "EMCON_HW", "GND"); c("C104", "100n", "+3V3", "GND"); r("R103", "4.7k", "PA_SW_EN", "GND"); r("R104", "4.7k", "HF_SW_EN", "GND"); r("R145", "100k", "TX_INHIBIT_n", "GND")   # fail safe: no panel, no transmit
# --- I2C: the kit bus (SDA, SCL) carries the charger, the expanders and the INA226s; no mux since the TPS55288 and TPS25750 left the design (7 Sep 01:50)
# --- expanders: U27 0x21 (outputs: the enables and the charge inhibit; inputs: faults and status), U28 0x24 (power-good lines, spares on test points); PCA9555PW pins as the A21 map
# 26 September 2026: U27 pin 8 is POE_SW_EN (S-14, the software hold ANDed with OUTLET_OK in U26); U28 pin 13 is
# PD_SW_EN (S-14) and its pins 4 and 5, the first two spares, are USBX_EN and USBX_FLT (D-12, the Glenair port's VBUS).
part("U27", "Interface_Expansion", "PCA9555PW", "PCA9555PW (0x21): enables and status", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "21": "+3V3", "2": "GND", "3": "GND",
 "4": "CHG_INHIBIT", "5": "MON_EN", "6": "HEAT_EN", "7": "D8_EN", "8": "POE_SW_EN", "9": "PA_SW_EN", "10": "HF_SW_EN", "11": "DEV_EN",
 "13": "CHRG_OK", "14": "PROCHOT", "15": "MON_FLT", "16": "HEAT_FLT", "17": "D8_FLT", "18": "DOCK_SPARE", "19": "INA_ALERT", "20": "FE_PGOOD"}, "C2864778")
part("U28", "Interface_Expansion", "PCA9555PW", "PCA9555PW (0x24): power-good lines, spares", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "21": "GND", "2": "GND", "3": "+3V3",
 "4": "USBX_EN", "5": "USBX_FLT", "6": "EXP2_SPC", "7": "EXP2_SPD", "8": "PA_PGOOD", "9": "POE_PGOOD", "10": "HF_PGOOD", "11": "PD_PGOOD",
 "13": "PD_SW_EN", "14": "PD_UFP", "15": "EXP2_SP3", "16": "EXP2_SP4", "17": "EXP2_SP5", "18": "EXP2_SP6", "19": "EXP2_SP7", "20": "EXP2_SP8"}, "C2864778")
c("C106", "100n", "+3V3", "GND"); c("C107", "100n", "+3V3", "GND"); r("R110", "10k", "EXP_INT", "+3V3"); r("R111", "4.7k", "MON_EN", "GND"); r("R112", "4.7k", "HEAT_EN", "GND"); r("R113", "4.7k", "D8_EN", "GND"); r("R114", "4.7k", "POE_SW_EN", "GND")   # S-08 and S-14, 26 Sep 2026
for k in range(3, 9): tp("TP%d" % k, "EXP2_SP%d" % k)
for k, nm in enumerate(("USBX_EN", "USBX_FLT", "EXP2_SPC", "EXP2_SPD"), 1): tp("TP%d" % (22 + k), nm)   # D-12, 26 Sep 2026: U28's first two spares now switch and watch the wall host port's VBUS, and keep their test points
# --- the A to B ribbon J_AB1 (2x13, top side, at (-90, 76)) and the D8 mezzanine harness J_MEZZ1 (2x8)
# 10 September 2026 (MESHSAT-862): the ribbon pairs sit in one row of the header, ground pins on both sides (the same change in
# gen_sch_b.py and gen_sch_d.py; the two maps are compared by check_contracts.py). Pins 4/5, 7/8 and 10/11 were diagonal
# neighbours 3.59 mm apart and no pair can be laid into them. AB_SPARE keeps its seat on the D harness only.
# 11 September 2026: the mezzanine harness pair moved once more, to the END row (pins 1/2), because an inner row of a 2.54 mm
# IDC field with 1.70 mm pads leaves a 0.84 mm channel between the columns and a coupled pair needs 1.20 mm. J_AB1 below is NOT
# fixed by that move: it carries THREE pairs and a 2x13 has only two end rows, so one pair cannot escape coupled whatever the
# pin map. That is a connector decision (two headers, a mezzanine stack connector, smaller pads, or an accepted uncoupled fan)
# and it is written up with its arithmetic in v2/docs/OWNER-DECISIONS-2026-09-11.md.
# 12 September 2026 (MESHSAT-862, appendix 32.135): THE WALL PAIR LEAVES J_AB1. Measured with the pre-router honest
# about its own copper: J_AB1 carries three pairs, a 2x13 has two end rows, and the third pair's only escape is the
# 1.14 mm channel between the columns, which EXITS AT THE SAME END the end-row pair leaves from. With USB_WALL laid
# first the tool laid USB_D8 on top of it (0.00 mm, twelve DRC items); with either other order USB_WALL fails for
# want of a corridor. Three pairs do not fit one 2x13 whatever the pin map, so the wall pair takes a ribbon of its
# own: a 2x5 with the pair on pins 1/2 (an end row) and eight grounds behind it. J_AB1's pins 5 and 6 become GND.
part("J_AB1", "Connector_Generic", "Conn_02x13_Odd_Even", "A-B interconnect (IDC 2x13, top side) to B16's underside header", "IDC26", {
 "1": "USB_D8_P", "2": "USB_D8_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "GND", "9": "PI_SHDN_REQ", "10": "PI_KILL", "11": "SDA", "12": "SCL",
 "13": "EXP_INT", "14": "TR_APRS", "15": "EMCON_HW", "16": "TX_INHIBIT_n", "17": "SLOT_EN1", "18": "SLOT_EN2", "19": "SLOT_EN3", "20": "ZEROIZE_HW", "21": "SHORE_INHIBIT", "22": "GND", "23": "GND", "24": "GND", "25": "USB_E6_P", "26": "USB_E6_N"})
part("J_AB2", "Connector_Generic", "Conn_02x05_Odd_Even", "A-B wall-port ribbon (IDC 2x5): the wall USB pair on the END row with eight grounds behind it", "IDC10", {
 "1": "USB_WALL_P", "2": "USB_WALL_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "GND", "9": "GND", "10": "GND"})
part("J_MEZZ1", "Connector_Generic", "Conn_02x08_Odd_Even", "D8 mezzanine harness (IDC 2x8): its USB pair, the PTT mirror, the inhibit, the PA rail state, I2C", "IDC16", {
 "1": "USB_D8_P", "2": "USB_D8_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "TR_APRS", "8": "TX_INHIBIT_n", "9": "PA_EN", "10": "SDA", "11": "SCL", "12": "EXP_INT", "13": "+3V3", "14": "GND", "15": "ZEROIZE_HW", "16": "AB_SPARE"})
r("R116", "100k", "TR_APRS", "GND"); r("R117", "10k", "ZEROIZE_HW", "+3V3"); r("R118", "100k", "SHORE_INHIBIT", "GND")
# D-12, 26 September 2026 (owner ruling): THE WALL DATA PATH GOES TO THE SEALED GLENAIR 233-370. The path itself
# does not change: B16's bank 3 hub, port 3, the pair USB_WALL_P/N on the J_AB2 ribbon (unchanged, so board B's
# side of the interface is untouched). What changes is where it leaves: J_USBW was the data side of the USB-C
# outlet's pigtail and is now the Glenair feed-through's lead. The 233-370 is a USB 2.0 Type A female coupler at
# front and rear (v2/vendor/d38999/glenair-233-370.pdf note 4), so the lead is PH 1x4 to a USB-A plug in the USB
# order VBUS, D-, D+, GND, and a HOST port needs VBUS, which the USB-C outlet's PD supply used to give it. That VBUS
# is U32, a TPS259631DDAR eFuse (the part and helper already on this board) off +5V_DEV, switched by U28's first
# spare (USBX_EN, 4.7 k pull-down: off until the panel turns it on) with its fault on the second (USBX_FLT). ILM
# 1.00 k gives 0.89 A (TPS2596 equation 7), above USB 2.0's 500 mA; OVLO 40.2k over 10k as U23. C156 is a 22 uF
# local bulk; USB 2.0 7.2.4.1's 120 uF per downstream port is an open item for the prototype (one port, one
# eFuse). The USBLC6-2 at the header now takes its VBUS pin from the port's own VBUS.
part("J_USBW", "Connector_Generic", "Conn_01x04", "JST-PH 1x4 socket: the Glenair 233-370 USB host feed-through lead (VBUS D- D+ GND), B16 bank 3 hub port 3", "PH4", {"1": "VBUS_WALL", "2": "USB_WALL_N", "3": "USB_WALL_P", "4": "GND"}, "C131334"); esd("U29", "USB_WALL_P", "USB_WALL_N", "VBUS_WALL")
efuse("U32", "+5V_DEV", "VBUS_WALL", "USBX_EN", "USBX_FLT", ["C154", "R186", "R187", "R188", "R189", "C155"], "1k 1% (ILM: 0.89 A)", ovlo_top="40.2k 1%", ovlo_lcsc="C12447", ilim_lcsc="C21190")
r("R190", "4.7k", "USBX_EN", "GND"); c("C156", "22u 25V 1210", "VBUS_WALL", "GND", "C1210")
_intent.rail("VBUS_WALL", 5.0, 0.5, 0.9, "U32", source_ic="U32 is a TPS2596 eFuse: its OUT pin IS the power path, which is what an eFuse is",
             loads={"J_USBW": 0.9}, fed_from="+5V_DEV", converted=False, budget=0.03,
             note="D-12, 26 September 2026: the Glenair 233-370 host port's VBUS behind the eFuse U32 (limit 0.89 A), out at the J_USBW lead; USB 2.0 asks 4.75 V at the port, so from a 5.09 V source the eFuse and the copper share 340 mV")
# --- eleven blind-mate RF sites (32.56): top-side SMA jack for the device pigtail, bottom-side Radiall R222M00720 receptacle to the dock plug
RF = (("VHF", "RF_VHF"), ("HF", "RF_HF"), ("WIFI24", "RF_WIFI24"), ("GNSS", "RF_GNSS"), ("SDR", "RF_SDR"), ("P2P-A", "RF_P2PA"), ("P2P-B", "RF_P2PB"), ("5G-MAIN", "RF_5G1"), ("5G-DIV", "RF_5G2"), ("IRID", "RF_IRIDIUM"), ("LORA", "RF_LORA"))
for k, (nm, net) in enumerate(RF, 1):
    part("J_RF%d" % k, "Connector", "Conn_Coaxial", "SMA jack, Amphenol 132134-11 vertical (pigtail to the %s device)" % nm, "SMAV", {"1": net, "2": "GND"}, "C3174425")
    part("J_BM%d" % k, "Connector", "Conn_Coaxial", "SMP-MAX slide-on receptacle R222M00720 (underside), %s to the dock plug" % nm, "SMPMAX", {"1": net, "2": "GND"})
# --- test points and flags
for ref, net in (("TP9", "VBAT"), ("TP10", "GND"), ("TP11", "+3V3"), ("TP12", "VBUS20"), ("TP13", "VIN_RAW"), ("TP14", "CELL+"), ("TP15", "EMCON_HW"), ("TP16", "RAIL_EN"), ("TP17", "SDA"), ("TP18", "SCL"), ("TP19", "IADPT"), ("TP20", "IBAT"), ("TP21", "DOCK_SPARE"), ("TP22", "REGN"), ("TP27", "AB_SPARE")): tp(ref, net)   # TP27: AB_SPARE lost its seat on J_AB1 when the ribbon pairs took their columns (10 Sep 2026), and it reaches D alone
for i, net in enumerate(("CELL+", "VBAT", "GND", "+3V3", "VIN_RAW", "VBUS20", "+5V_S1", "+5V_S2", "+5V_S3", "+5V_DEV", "+13V8_PA", "+12V_HF", "+54V_POE", "VMON", "VHEAT", "+5V_D8", "PD_VBUS", "PD_VPWR", "PD_SW", "REGN", "CELL_FUSED", "CH_ACN", "PRECHG", "FE_OUT", "PA_OUT", "HF_OUT", "POE_OUT", "PD_OUT"), 1):
    part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})

# ----------------------------------------------------------------- emit
POWER = {"GND": ("power", "GND"), "+5V": ("power", "+5V"), "+3V3": ("power", "+3V3")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
# power flag symbols connect at their pin; place them wired to a label of the net

# layout: columns, top-down cursor; group order = list order with section titles
def refs_with(prefixes, exclude=()):
    return [p["ref"] for p in P if any(p["ref"] == x or p["ref"].startswith(x) for x in prefixes) and p["ref"] not in exclude]
SECTIONS = [("PACK NODE OVER THE DOCK BLOCK (32.56): 9 A PINS, PRE-CHARGE, 25 A BLADE, DOCK SIGNAL PINS", ["J_CP1", "J_CP2", "J_CP3", "J_CP4", "J_CN1", "J_CN2", "J_CN3", "J_CN4", "J_PRE1", "R1", "F1", "C1", "C2", "C3", "D1", "J_DOCK"]),
            ("MAIN POWER CONTROL LTC2954", ["U1", "C4", "R2", "R184", "R3", "R4", "C152", "Q1", "R5", "J_MAINSW"]),
            ("FRONT END: LM5176 FROM THE 9 TO 36 V INPUT TO THE 20 V CHARGE BUS", ["U2", "Q2", "Q3", "Q4", "Q5", "L1", "R6", "R7", "R8", "C147", "R10", "C5", "C6", "C7", "C8", "C9", "C10", "R11", "R12", "R13", "R14", "R15", "C11", "C12", "C13", "C14", "C15", "R119", "D2", "D9", "D10", "C163", "C178", "C179", "C180"] + ["C%d" % k for k in range(181, 190)] + ["C192", "C199", "C200"] + ["C%d" % k for k in range(201, 207)] + ["D19", "C207"]
             + ["R195", "U34", "R196", "C210", "C211", "C212", "R197", "Q36", "R200", "D22", "C214", "R198", "R199", "R206", "C213", "Q37", "R201", "Q38", "R202", "R203", "R204", "R205"]),   # fourth fix-up: VISNS's 2 k and the restart guard (R4A-N15)
            ("CHARGER BQ25731: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), PACK BEYOND RSR, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "C16", "C17", "C18", "R18", "C19", "C20", "C21", "C22", "C190", "C191", "C23", "C24", "C25", "R19", "R20", "Q6", "R21", "R22", "R23", "R24", "R25", "C26", "C27", "R26", "R27"]),
            ("SLOT RAIL S1: AP64500 5.1 V + INA226 0x40", ["U4", "L3", "C28", "C29", "C30", "C31", "C32", "C33", "R28", "R29", "R30", "R31", "R45", "R129", "C112", "U8", "J_5V_S1"]),
            ("SLOT RAIL S2: LM5176 5.1 V (7.2 A MINIMUM LIMIT) + INA226 0x41", ["U5", "Q28", "Q29", "Q30", "Q31", "L4", "R32", "R33", "R46", "C133", "R130", "C113", "C134", "C135", "C136", "C34", "C137", "D5", "D6", "R35", "R170", "R171", "C35", "C36", "C37", "C38", "C39", "C164", "C165", "C166", "C193", "R172", "R173", "R174", "C138", "R175", "R176", "C139", "R34", "U9", "J_5V_S2"]),
            ("SLOT RAIL S3: AP64500 5.1 V + INA226 0x44", ["U6", "L5", "C40", "C41", "C42", "C43", "C44", "C45", "R36", "R37", "R38", "R39", "R47", "R131", "C114", "U10", "J_5V_S3"]),
            ("DEVICE RAIL: LM5176 5.1 V (7.2 A MINIMUM LIMIT) + INA226 0x45", ["U7", "Q32", "Q33", "Q34", "Q35", "L6", "R40", "R41", "R115", "C140", "R132", "C115", "C141", "C142", "C143", "C46", "C144", "D7", "D8", "R43", "R177", "R178", "C47", "C48", "C49", "C50", "C51", "C167", "C168", "C169", "C194", "R179", "R180", "R181", "C145", "R182", "R183", "C146", "R42", "U11", "J_5V_DEV", "R44"]),
            ("3.3 V LOGIC: TPS62933", ["U12", "L7", "C52", "C53", "C54", "C55", "C56", "R48", "R49", "D3"]),
            ("PA RAIL: LM5176 13.8 V 6 A, EMCON GATED, INA226 0x46", ["U13", "Q11", "Q12", "Q13", "Q14", "L8", "R50", "R51", "R52", "C148", "R54", "C57", "C58", "C59", "C60", "C61", "C62", "R55", "R56", "R57", "R58", "R59", "C63", "C64", "C65", "C66", "C67", "C170", "C171", "C195", "R120", "D11", "D12", "D20", "C208", "U14", "J_PA"]),
            ("HF RAIL: LM5176 12.0 V 2 A, EMCON GATED", ["U15", "Q15", "Q16", "Q23", "Q24", "L9", "R60", "R61", "R62", "C149", "R64", "C68", "C69", "C70", "C71", "C72", "C73", "R65", "R122", "R123", "R124", "R125", "C74", "C108", "C109", "C110", "C111", "C172", "C173", "C196", "R126", "D13", "D14", "D21", "C209", "J_HF"]),
            ("POE RAIL: LM5176 BOOST 54 V 0.6 A, INA226 0x47", ["U16", "Q17", "Q18", "Q19", "Q20", "L10", "R66", "R67", "R68", "C150", "R70", "C75", "C76", "C77", "C78", "C79", "C80", "R71", "R72", "R73", "R74", "R75", "C81", "C82", "C83", "C84", "C85", "C176", "C177", "C197", "R121", "D15", "D16", "U17", "J_54V"]),
            ("USB-C PD OUTLET: TPS25740A + LM5176 5/9/15 V STAGE", ["U19", "Q21", "Q22", "Q25", "Q26", "L11", "R76", "R77", "R78", "C151", "R80", "C86", "C87", "C88", "C89", "C90", "C91", "R81", "R127", "R128", "R133", "R134", "C92", "C116", "C117", "C118", "C119", "C174", "C175", "C198", "R135", "R136", "R137", "U18", "Q27", "R138", "R139", "R140", "R141", "R142", "R143", "C93", "C94", "C95", "C96", "C97", "C120", "D4", "D17", "D18", "J_USBC_OUT", "U31"]),
            ("EFUSES: MONITOR, HEATER (12.0 V BUCK), D8 5 V", ["U21", "C98", "R90", "R91", "R92", "R93", "C99", "J_MON", "U22", "C100", "R94", "R95", "R96", "R97", "C101", "U33", "L12", "C157", "C158", "C159", "C160", "C161", "C162", "R191", "R192", "R193", "R194", "J_HEAT", "U23", "C102", "R98", "R99", "R100", "R101", "C103", "J_MEZZ_PWR1"]),
            ("EMCON GATES 74LVC08, OUTLET INTERLOCK, EXPANDERS 0x21 0x24", ["U26", "U30", "C153", "R102", "C104", "R103", "R104", "U27", "U28", "C106", "C107", "R110", "R111", "R112", "R113", "R114"] + ["TP%d" % k for k in range(3, 9)] + ["TP23", "TP24", "TP25", "TP26"]),
            ("RIBBON J_AB1 2x13, WALL-PORT RIBBON J_AB2 2x5, MEZZANINE HARNESS J_MEZZ1 2x8, GLENAIR WALL USB HOST PORT", ["J_AB1", "J_AB2", "J_MEZZ1", "R116", "R117", "R118", "J_USBW", "U29", "U32", "C154", "R186", "R187", "R188", "R189", "C155", "R190", "C156"] + [p["ref"] for p in P if p["ref"] == "R145"]),
            ("ELEVEN BLIND-MATE RF SITES: SMA JACK (TOP) + SMP-MAX RECEPTACLE (UNDERSIDE)", ["J_RF%d" % k for k in range(1, 12)] + ["J_BM%d" % k for k in range(1, 12)]),
            ("TEST POINTS, FLAGS", ["TP%d" % k for k in range(9, 23)] + ["TP27"] + [p["ref"] for p in P if p["ref"].startswith("#FLG")])]
_listed = {r for _, refs in SECTIONS for r in refs}
_rest = [p["ref"] for p in P if p["ref"] not in _listed]
if _rest: SECTIONS.append(("OTHER PARTS (not in a section list)", _rest))
_intent.bypass("C4", "U1", "1", "VBAT")
_intent.bypass("C19", "U3", "7", "CH_VDDA")
_intent.bypass("C54", "U12", "3", "VBAT")
_intent.bypass("C94", "U18", "5", "PD_DVDD")
_intent.bypass("C104", "U26", "14", "+3V3")
# 20 September 2026: C106 and C107 are the two PCA9555 expanders' own decoupling, written on the line
# below their part() calls, and both were declared against U26 pin 14, the AND gate three parts earlier.
# Measured on A74's placed board: C106 sits 1.70 mm from U27 pin 24 and C107 1.70 mm from U28 pin 24,
# while the old declaration read them at 14.7 and 13.0 mm from a pin neither serves.
_intent.bypass("C106", "U27", "24", "+3V3")
_intent.bypass("C107", "U28", "24", "+3V3")
_intent.bypass("C153", "U30", "5", "+3V3")   # 26 September 2026: the outlet interlock NAND's own decoupling (S-14)
import schlayout, time as _time
PAPER, NPAGES, NCOLS, NROWS = schlayout.run(P, SECTIONS, POWER, _intent._I["bypass"], {"date": _time.strftime("%Y-%m-%d")}, os.environ.get("PHASE", ""), 'PCB-A POWER + I/O')   # 15 Sep 2026: one A3 page per block, real wiring (32.196)
out = kisch.out
print("layout: %d A3 pages on a %d x %d sheet -> paper %s" % (NPAGES, NCOLS, NROWS, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper %s)\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-A POWER + I/O") (date "%s")' % _time.strftime("%Y-%m-%d") + ' (rev "A") (company "MeshSat") (comment 1 "Phase ' + (os.environ.get("PHASE") or "?") + ' schematic (appendix 32.55 and 32.56: the BB-2590/U node, LM5176 front end and PA and PoE rails, BQ25731 charger, per-slot TPS56637 rails, TPS55288 HF and PD stages, hardware EMCON gates, eleven blind-mate sites), generated by tools/gen_sch_a.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-830. Earlier: Phase A20 schematic (appendix 32.35: hub and dongle channels gone to B13, J_AB1 2x9 with I2S, Q5 pin order corrected per 32.36), generated by tools/gen_sch_a.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-709 / MESHSAT-789. A19 (4 Sep 2026 rulings, appendix 32.13 to 32.25): the kit UPS. BQ25792 charger from the dock 12 V, BQ34Z100-G1 gauge, three TPS61288L rails (M1, M2, Pi), LTC2954 main power control, TPS259571 heating-pad switch, USB2517I seven-port hub with the wall host port, PCA9555 0x21 and 0x24, seven SMP-MAX blind-mate sites, 9 A power pins to the floor battery module. No X1202."))\n'
hdr += '\t(lib_symbols\n' + "".join("\t\t" + ser(v, 2).replace("\n", "\n\t\t") + "\n" for v in libsyms.values()) + '\t)\n'
body = "".join("\t" + s.replace("\n", "\n\t").rstrip("\t") for s in out)
tail = '\t(sheet_instances (path "/" (page "1")))\n)\n'
open(OUT, "w").write(hdr + body + tail)
print("wrote", OUT, "parts:", len(P), "lib symbols:", len(libsyms))
nets = {}
for p in P:
    for num, net in p["nets"].items():
        if net != "NC": nets.setdefault(net, []).append("%s.%s" % (p["ref"], num))
single = [n for n, v in nets.items() if len(v) == 1]
print("nets:", len(nets), "single-pin nets (should be empty or intentional):", single)

# the decoupling this file writes outside the converter blocks (which declare their own, 8 Sep 2026, MESHSAT-862 Stage C):
# each capacitor sits directly after the part it serves in this file and is filtered to supply pins, so crystal loads, reset
# networks and reference filters are not listed. intent.py refuses an entry whose capacitor is not on that pin's net.
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
