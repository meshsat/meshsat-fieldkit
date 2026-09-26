#!/usr/bin/env python3
"""PCB-E1 DOCK, phase E6 (MESHSAT-830, 7 Sep 2026): generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_e.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-e1-dock"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, text, uq, wire)
import intent as _intent
# LOADS DECLARED 13 September 2026. Until today this rail carried none, and dc_drop does not leave such a rail
# unsolved: it guesses, over every U and J footprint on the net. Here the guess was J_FAN1, J_FAN2 and U12,
# and it MISSED the load that carries almost all of the current, because `P_CP` starts with a P. Nearly the
# whole pack node leaves this board through that 12 AWG solder pad to the block's CELL+ targets and on to
# board A; what stays here is the local 5 V buck and the two mixer fans. The split apportions the declared
# 10 A typical: it is a design estimate of where the current goes, not a measurement of what it is.

# THE EFFICIENCIES, AND WHICH RAILS CONVERT AT ALL (16 September 2026, rule THM-001). CELL_F arrives from the
# pack on a wire behind a fuse and VIN_RAW is switched by a hot-swap FET: neither converts, and their loss is
# the I2R their own copper carries, which dc_drop measures. The other two are made here and take their figures
# from their own parts' datasheets, at or below the low end of what those plot, because a lower efficiency is
# a higher loss and a dissipation figure is only useful as a floor.
#   AP63205 (U12, the 5 V 2 A buck feeding the controller, the Geiger module and the fans' logic): 0.88 at the
#   0.3 to 0.5 A this rail actually draws, which is a light load for a 2 A part and the region where a small
#   buck is least efficient.
#   U13's 3.3 V (0.35 to 0.6 A from the 5 V rail): 0.85, a small step-down at a light load.
# Neither is a measurement of this board, and the junction temperature this rule really wants needs the
# envelope's maximum ambient, which is owner decision 34.
_intent.rail("CELL_F", 14.4, 10.0, 18.0, "F3", always_on=True, v_work=16.8, converted=False,
             always_on_why="the pack node after this board's 25 A blade: a fuse is protection and not a switch, and what opens this node is the pack's own gauge two stages upstream",
             loads={"P_CP": 9.0, "U12": 0.8, "J_FAN1": 0.1, "J_FAN2": 0.1},
             note="the pack node after the 25 A blade F3, to the block pads")
# CELL+ IS THE OTHER SIDE OF THE SAME FUSE AND IT WAS DECLARED AS NOTHING AT ALL (20 September 2026, found
# by `power_path` asking every board mechanically; appendix 32.237). It is the conductor from the XT60
# J_BATT pin 2 to the blade F3, carrying the pack's whole 10.0 A typical and 18.0 A peak into this board,
# and it was neither a rail nor a node, so `dc_drop` solved nothing on it and neither PI-001 nor PI-002 had
# looked at ten amps of copper. It is board P's `PACK_N` on the other side of the same wire: the pack's two
# terminals, one of them measured at 02:05 tonight and this one invisible until 02:11.
# It is a SEGMENT of CELL_F's path, which is the rail the board's power is counted at, so its watts are not
# counted twice; everything that judges copper judges it exactly as it judges CELL_F's.
# CELL+ CROSSES A AND E AND ITS BUDGET IS SPLIT (20 September 2026). Declaring board E's own CELL+ at 02:16
# made this a cross-board rail, and `check_contracts` said so within the minute: "rail CELL+ crosses A/E and
# its end-to-end budget is not split between them". The split is MEASURED and not guessed: board A's CELL+
# reads a worst drop of 12 mV, 0.08 percent of 14.4 V, and board E's 24 mV, 0.16 percent, so the two boards
# together spend a quarter of a percent of the 2 percent the rail allows. Each declares 0.5 percent, which is
# six times what it measures, and the remaining 1.0 percent (144 mV) belongs to the part nobody has measured:
# the 12 AWG lead, the dock block contacts and the 25 A blade between them. A share is a BAR, so it is set
# from a measurement with margin rather than from an opinion.
_intent.rail("CELL+", 14.4, 10.0, 18.0, "J_BATT", loads={"F3": 10.0}, series_of="CELL_F", v_work=16.8,
             share=0.005,
             converted=False, always_on=True,
             always_on_why="the pack node BEFORE this board's 25 A blade: nothing on this board can open it, "
                           "which is the same reason CELL_F gives one line up",
             note="the pack lead from the XT60 J_BATT pin 2 to the blade F3, at the pack's own 10.0 A "
                  "typical and 18.0 A peak. Declared 20 September 2026: it had been declared as nothing at "
                  "all, so no power rule had ever looked at it")
# LOADS DECLARED 13 September 2026. The guess for this one was J_BLK and U4 at 4 A each, and U4 is the ideal
# diode that ORs the tracker output INTO this bus: it is a SOURCE, so half the rail's current was being pulled
# backwards through it. The whole of this bus leaves through the block lands J_BLK pins 1 to 4 for board A's
# front end to regulate; the monitor divider R40 and the indicator LED1 are microamps and milliamps.
# F-IN-02, 26 September 2026 (MESHSAT-1357 round 4, corrected in the same round after review R4E-02): THE PATH IS
# RATED FOR WHAT THE LIMITER LETS THROUGH, AND THE DECLARATION SAYS SO. This rail said 8.0 A typical and 10.0 A peak.
# The hot-swap U6 (LM5069-2) with R19 = 10 mOhm limits at VCL / RS, and VCL is 48.5 min, 55 typ, 61.5 max mV
# (ti-lm5069.pdf SNVS452G, electrical characteristics), so 4.85 to 6.15 A, then it retries: the 8 A was never
# deliverable. Two numbers come out of that and they answer two different questions:
#   - 6.15 A (VCL max / RS) is what the path must CARRY CONTINUOUSLY: a unit whose VCL sits at 61.5 mV passes 6.15 A
#     without ever entering current limit, and only board A's IIN_HOST bounds it. It is the declared typical AND
#     peak here, because `dc_drop` judges a conductor's steady rise at the typical. (The circuit breaker, VCB 80 to
#     130 mV, lets up to 13 A through for at most tCB 1.2 us before it pulls the gate: a sub-microsecond edge that
#     no thermal rule reads, recorded and not declared.)
#   - 4.85 A (VCL min / RS) is what the path is GUARANTEED to pass, so it sets what the host may ask: at the W2 front
#     end efficiency of 0.93, about 40.6 W on VBUS20 at a 9 V input (IIN_HOST at or below about 2.0 A at 20 V), about
#     54 W at 12 V (IIN_HOST at or below about 2.7 A), and the front end's own 100 W at 24 V (116 W available).
# THE FIRST VERSION OF THIS CORRECTION MISREAD THE CHOKE. It quoted the SRF1260-4R7Y at 7.18 A Irms and 9.71 A Isat,
# which are the datasheet's PARALLEL columns (both windings sharing one current). L2 is wired with winding 1 in the
# positive line and winding 2 in the return, so EACH winding carries the whole line current, and the thermal
# equivalent is the SERIES column (bourns-srf1260-common-mode-choke.pdf: "Parallel Rating ... Series Rating";
# 4R7Y series 18.8 uH, 0.0479 Ohm, 3.59 A Irms, 4.86 A Isat; "Temperature Rise .... 40 C at rated Irms"; operating
# -40 to +105 C with the rise included). At 4.85 A the 4R7Y dissipates about 1.13 W against the 0.62 W of its 40 C
# rise, about 73 K of rise: over the 105 C limit at the 51 C inside-air bar. The fix is L2 (see the part below):
# the SRF1260-1R5Y of the same family, land and pin map, 6.89 A Irms and 9.15 A Isat in the series column: about
# 32 K of rise at 6.15 A continuous (83 C at the 51 C bar) and about 20 K at 4.85 A. The other route, R19 to 18 mOhm
# (2.69 to 3.42 A), was refused: at a 12 V vehicle it guarantees about 30 W on VBUS20, which is the kit's idle (W2
# PS-IDLE 29.4 W at the battery) with nothing left to charge, where D-06 makes vehicle and solar input the way a
# mission outlasts the pack. The rest of the path is rated
# above 6.15 A: F1 10 A blade (8 A at 65 C, pcb_fuse_derating.yaml), J_DCIN JST-VH 10 A, Q1 BSC039N06NS, R19 2512
# (0.38 W at 6.15 A), Q7 CSD19532Q5B. Taken by the session under the owner's standing rule of 26 September 2026
# (drafts/r4-decisions.md, R4E-02). Board A's own VIN_RAW declaration (gen_sch_a.py) still reads 8/10 A and is
# that board author's item, as is the IIN_HOST rule in the host contract.
_VIN_T, _VIN_P = 6.15, 6.15
_intent.rail("VIN_RAW", 12.0, _VIN_T, _VIN_P, "L2", switch="U6", enable_net="HS_UVLO", v_work=36.0, converted=False,
             # the hot-swap controller IS the switch and its enable is the UVLO divider: the rail comes
             # up when the input passes 9 V and drops out above 40 V, which is the LM5069's own gate.

             loads={"J_BLK": _VIN_T}, budget=0.02, share=0.005,
             note="shore and vehicle entry after the filter choke, 10 A fuse. Declared at the hot-swap's current "
                  "limit (F-IN-02, 26 September 2026): 6.15 A, U6's maximum limit with its 10 mOhm sense, as both "
                  "the typical and the peak, because a unit at VCL max passes it continuously without limiting; "
                  "4.85 A (VCL min) is only what the entry is guaranteed to pass, which bounds the host's IIN_HOST "
                  "and not the conductors. THIS BOARD'S SHARE is 0.5 of the "
                  "rail's 2 percent (16 September 2026): the entry, the choke and the dock block are a short run on "
                  "this strip and measured 0.16 percent at the old 8 A, while board A carries the same current from "
                  "the dock across the power board to its front end and measured 0.86, so the 1.5 points go there")
# DECLARED 16 September 2026. These two were not in the intent file, so `signalnets` could not know they were
# rails and the return-path gate judged them as SIGNALS: +3V3_E6 came back 194.7 of 502.0 mm without an
# adjacent reference, which is what a power net looks like and says nothing about signal integrity. A rail that
# is not declared is not excluded, and the same omission would have hidden its drop and its current density.
_intent.rail("+3V3_E6", 3.3, 0.35, 0.60, "U13", always_on=True, converted=True, efficiency=0.85,
             always_on_why="U13 is a TLV75533 whose EN pin is tied to its own input, so this rail follows the 5 V the AP63205 makes and has no switch of its own",
             source_ic="U13 is a TLV75533 LDO in a SOT-23-5: pin 5 IS its output power pin and the whole rail "
                       "current really does leave through it, which is what source_ic is for",
             # U17 (S-10, 26 September 2026): the SGP41's hotplate supply VDDH sits on this rail, 3.4 mA maximum in
             # measurement at 3.3 V plus 20 percent for 5 ms after each command (SGP41 datasheet v1.0, Table 2)
             loads={"U10": 0.06, "U11": 0.05, "U14": 0.04, "U15": 0.04, "U17": 0.005,
                    "J_DCF": 0.03, "J_LTG": 0.03, "J_POD": 0.10},
             budget=0.03,
             note="the sensor controller's own 3.3 V from U13: the RP2040, the sensors and the three sealed "
                  "sensor headers. A logic rail at a third of an amp over long thin tracks is fine at 3 percent")
# The source is the INDUCTOR, not the chip. U12 is an AP63205 buck and its output current leaves through L3;
# naming the controller would hold its SOT-23-6 pin at 0 V and pull 0.3 A down a pin that never carries it,
# which is the defect board A's VBUS20 had (2.90 A of 6 down a 0.200 mm escape, 13 September 2026).
_intent.rail("+5V_E6", 5.0, 0.30, 0.50, "L3", always_on=True, converted=True, efficiency=0.88,
             always_on_why="U12 is an AP63205 whose EN pin is tied to CELL_F, the pack node it runs from, so this rail follows the pack and has no switch of its own",
             # F-BP-02, 26 September 2026: the Geiger header is fed through the load switch U16 now, so the
             # load on this rail is U16's input pin and not the header
             loads={"U13": 0.20, "U16": 0.10},
             note="the local 5 V buck U12: the 3.3 V regulator's input and, through the load switch U16, the "
                  "Geiger tube's high-voltage supply on its own header")
# F-BP-02, 26 September 2026 (MESHSAT-1357 round 4): THE GEIGER MODULE COMES OFF THE ALWAYS-ON DOMAIN. With the pack
# connected and the kit off, U12 (EN tied to CELL_F) keeps +5V_E6 up and the Geiger header was on it directly: its
# declared 0.10 A at 5 V is 0.5 W, about 0.57 W from the pack through the buck, and it was the largest single drain
# of the kit-off state W2 measured at 0.37 to 1.87 W (a pack at 30 percent flat in 1 to 6 days). A Geiger tube's
# high-voltage converter has no sleep of its own, so a switch is the only way to stop it. U16 is the TPS22810DRV the
# set already buys for board B's LoRa and Zigbee rails and board D's VGG (LCSC C527679; TI SLVSDH0C, WSON-6 DRV:
# 1 VOUT, 2 QOD, 3 CT, 4 GND, 5 EN/UVLO, 6 VIN, exposed pad GND; 2.7 to 18 V in, 3 A, -40 to +105 C ambient,
# shutdown current 0.5 uA typical and 2.3 uA maximum at 5 V). Its EN is the sensor controller's GPIO18 through
# GEIGER_EN with R56 100k to ground, because the datasheet says EN must not float and the tube must stay off while
# U10 is in reset or unprogrammed. QOD is left open (quick discharge disabled), as boards B and D do.
_intent.rail("+5V_GEIGER", 5.0, 0.10, 0.10, "U16", converted=False, fed_from="+5V_E6", switch="U16",
             enable_net="GEIGER_EN",
             source_ic="U16 is a TPS22810 load switch: its OUT pin IS the power path, which is what it is for",
             loads={"J_GEIGER": 0.10},
             note="the Geiger module's 5 V behind its load switch (F-BP-02, 26 September 2026), off whenever the "
                  "sensor controller does not ask for it, so the kit-off state no longer carries the tube's "
                  "high-voltage supply")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers
LIBCACHE = {}

# ----------------------------------------------------------------- the design
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C10u50": "Capacitor_SMD:C_1206_3216Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMC", "SO8": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOD123": "Diode_SMD:D_SOD-123",
 "FUSE": "Fuse:Fuseholder_Blade_Mini_Keystone_3568", "BUCK": "Converter_DCDC:Converter_DCDC_TRACO_TEN40-110xxWIRH_THT", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "OPTO": "Package_SO:SOP-4_3.8x4.1mm_P2.54mm",
 "POGO_T": "meshsat:PogoTargets_2x4", "POGO_T6": "meshsat:PogoTargets_2x6", "TP": "TestPoint:TestPoint_Pad_D1.5mm", "TDSON8": "Package_TO_SOT_SMD:TDSON-8-1", "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "QFN38": "Package_DFN_QFN:WQFN-38-1EP_5x7mm_P0.5mm_EP3.15x5.15mm", "L1510": "Inductor_SMD:L_Coilcraft_XAL1510-103", "RS2512": "Resistor_SMD:R_2512_6332Metric", "CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL8": "Capacitor_SMD:CP_Elec_8x6.7", "XT60": "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical", "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "PAD86": "meshsat:SolderPad_8x6",
}
kisch.configure(fp=FP)   # the engine needs the tables before the first part
P = kisch.P                           # one list, shared with the engine (not a copy)
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
# ================================================================ E6 (7 Sep 2026, appendix 32.55 to 32.57, MESHSAT-830): the dock strip of the A22 generation. It carries the BB-2590/U cable entry
# and its 25 A blade to the raised block, the vehicle and shore entry (10 A blade, LM74700 ideal diode, LM5069 hot-swap with under and over-voltage limits, the input filter) to the
# raw 9 to 36 V bus that climbs the dock contacts into A22's LM5176 front end, the LT8705A panel tracker of E4 (bench-fitted part, 32.54) ORed into the same bus, eleven float clamps,
# and the kit's sensor controller (the S1 board of the plan folded in, 32.57): an RP2040 on USB through two dock contacts with the inside climate sensor, the IMU, the floor water
# electrodes, the two mixer fan drivers, the pack's SMBus, and headers for the Geiger module, the DCF77 receiver, the lightning sensor module and the outside sensor pod. One ground
# domain (the vehicle return joins the kit ground through the filter's second winding); the isolated TRACO converter of E4 is gone.
FP.update({"QFN56": "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm", "USON8": "Package_SON:Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm", "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
           "LGA8B": "Package_LGA:Bosch_LGA-8_3x3mm_P0.8mm_ClockwisePinNumbering", "LGA14B": "Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm", "TSOT6": "Package_TO_SOT_SMD:TSOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5",
           "L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX", "L1010": "Inductor_SMD:L_Coilcraft_XAL1010-XXX", "CMC": "Inductor_SMD:L_CommonModeChoke_Bourns_SRF1260", "VSSOP10": "Package_SO:VSSOP-10_3x3mm_P0.5mm",
           "PPAK": "Package_SO:PowerPAK_SO-8_Single", "PH3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "PH4": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
           "PH5": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical", "PH6": "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", "C1210": "Capacitor_SMD:C_1210_3225Metric",
           "C0805": "Capacitor_SMD:C_0805_2012Metric", "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "SMB": "Diode_SMD:D_SMB"})
# 26 September 2026 (MESHSAT-1357 round 4): the lands of this round's parts. XH4 is board P's own J_SMB land (S-05);
# WSON6 is the land boards A, B, D and P already use for the TPS22810 (F-BP-02); DFN6S is the SGP41's DFN-6, which
# KiCad 9's libraries do not carry and which is drawn from Sensirion's Figure 18 by the round-4 draft generator
# (drafts/footprints/gen_footprint_sgp41.py) until it is added to meshsat.pretty (S-10).
FP.update({"XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
           "DFN6S": "meshsat:Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm"})
def nfet(ref, value, g, d, s, fp="PPAK", lcsc=""):
    """PowerPAK SO-8 single / TI 5x6 SON: pads 1, 2, 3 = SOURCE, 4 = GATE, 5 = the DRAIN tab (the tab and the four
    right-hand pins all carry the number 5). Until 17 September 2026 this wrote the three-pin Q_NMOS_GDS map, so the
    GATE net and the DRAIN net landed on two SOURCE pins and the real gate and the whole drain tab carried nothing:
    board E's Q7, the hot-swap pass FET on the shore and vehicle DC entry, would have tied HS_GATE, HS_S and DC_HS
    together through its own source metal with no gate drive at all, and the LM5069's inrush and overcurrent
    protection would not have existed. Board A met the same trap on 7 September 2026 (appendix 32.36) and fixed its
    own helper; nothing held the two together until kisch judged every map against its land."""
    part(ref, "Connector_Generic", "Conn_01x05", value, fp, {"1": s, "2": s, "3": s, "4": g, "5": d}, lcsc)
def ph(ref, n, value, nets): part(ref, "Connector_Generic", "Conn_01x%02d" % n, value, "PH%d" % n, nets)
# --- pack entry: the BTA-70762-2 cable of the BB-2590/U (both 14.4 V sections in parallel) on an XT60, the 25 A blade, the 12 AWG pads to the block; the pack's two SMBus sections on J_SMB
part("J_BATT", "Connector_Generic", "Conn_01x02", "Amass XT60-M: the BB-2590/U pack cable BTA-70762-2 (pin 2, the pad nearer the fuse F3, is +; pin 1 is the return; the pack's own protection is inside it. E6 run 11: a 3 mm CELL+ track could not pass the return pad to reach pin 1)", "XT60", {"1": "GND", "2": "CELL+"}, "C98733")
part("F3", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder): pack to the block", "FUSE", {"1": "CELL+", "2": "CELL_F"})
part("P_CP", "Connector", "Conn_01x01_Pin", "solder pad, 12 AWG wire to the block board CELL+ targets", "PAD86", {"1": "CELL_F"})
part("P_CN", "Connector", "Conn_01x01_Pin", "solder pad, 12 AWG wire to the block board return targets", "PAD86", {"1": "GND"})
# S-05 / A07, 26 September 2026 (MESHSAT-1357 round 4): THE PACK SMBUS LEAD MATES NOW. J_SMB was a 2.54 mm 1x6 pin
# header left from the withdrawn BB-2590/U (1 SDA0, 2 SCL0, 3 SDA1, 4 SCL1, 5 GND, 6 GND) while board P's end is a
# JST-XH 1x4 (1 SMBC, 2 SMBD, 3 GND, 4 PRES), so a straight lead put the clock on data, P's ground on the sensor bus
# data line and PRES on the sensor clock (adjudication A07). It is the same part as P's now, JST B4B-XH-A (LCSC
# C594232; JST XH catalogue eXH: 2.5 mm pitch, 3 A, -25 to +85 C, 9.8 mm high), pin for pin P's order, so a straight
# XH-to-XH four-way lead is correct. The two pack nets are renamed from SDA0/SCL0 to SMBD/SMBC, P's own names,
# because the old names said I2C0 on pins that are the RP2040's I2C1 (GPIO2 SDA, GPIO3 SCL, rpi-rp2040-datasheet
# Table 279): the roles were right and the index was not. The sensor controller U10 is the gauge's only SMBus host
# (the BQ25731 on board A has no conductor to board P, A07). The second SMBus section and the spare ground go with
# the BB-2590/U: SDA1/SCL1 is this board's own sensor bus and keeps every other device it carries.
# PRES (pin 4) reaches GPIO17 through R54 1k with R55 1M to +3V3_E6 on the GPIO side. P holds PRES down with its own
# R14 10k (system present, SLUSC67B 8.2.2.2.3: 20 k or lower), so the controller reads LOW with the lead in and HIGH
# with it out (3.3 V less the RP2040's 1 uA maximum pin leakage through 1M: 2.3 V against its 2.0 V VIH),
# and the gauge still sees 3.3 x 10k/1.01M = 0.03 V plus its own 10 to 20 uA sampling pulse into 10k: 0.21 V against
# its 0.55 V VIL. The GPIO can also drive it: high then low is the BQ4050's SHUTDN high-to-low edge (SLUUAQ3A
# 5.4.4.1, only if the gauge's data flash enables EMSHUT), which is a firmware choice and not the storage path of
# record (that is the SMBus MAC Shutdown 0x0010 through SMBC/SMBD, F-BP-02). At reset the RP2040's pad pull-down and
# P's 10k keep the line low, so no power-up can make an edge. The same pull-down (about 50 k) swamps R55 1M, so the
# firmware turns GPIO17's pad pull-down OFF before it reads PRES, or a lead that is out reads as a lead that is in
# (review of round 4; drafts/r4-decisions.md open item 10). And the reading is only right while board P keeps its
# own R14 10k to ground on PRES: that belongs in the J_SMB contract between P and E (open item 8).
part("J_SMB", "Connector_Generic", "Conn_01x04", "SMBus lead to board P, JST-XH 1x4 (B4B-XH-A), P's pin order: 1 SMBC, 2 SMBD, 3 GND, 4 PRES", "XH4",
     {"1": "SMBC", "2": "SMBD", "3": "GND", "4": "PRES_LEAD"}, "C594232")
# S-09 / A03 / F-IN-01, 26 September 2026: THE PACK NODE CLAMP POINTED THE WRONG WAY. An SMCJ18A is UNIDIRECTIONAL
# (the A suffix; CA is the bidirectional part, Littelfuse SMCJ series rev 11/20/15), and on the D_SMC land pad 1 is the
# cathode (A03 read the fab glyph and the silk bracket on every committed board). D3 had GND on pad 1 and CELL_F on
# pad 2, so it was forward-biased across the pack node from the moment the pack was connected. The cathode goes to
# the rail. The symbol is Device:D_Zener (pin 1 K, pin 2 A) instead of Device:D_TVS, which KiCad draws as a
# BIDIRECTIONAL suppressor with pins A1 and A2: a one-way part needs a symbol whose netlist names its cathode, or no
# check can read the orientation (KiCad's own unidirectional TVS symbols, Diode:SM6T*A and 1.5SMCxxA, name their
# pins A1 and A2 as well). D3 also gets the part code board A's D1 already carries for the same SMCJ18A: Littelfuse,
# LCSC C374030 (it had none).
c("C1", "10u 25V 1210", "CELL_F", "GND", "C1210"); part("D3", "Device", "D_Zener", "SMCJ18A (pack node clamp, unidirectional: cathode on CELL_F)", "TVS", {"1": "CELL_F", "2": "GND"}, "C374030")
# --- vehicle and shore entry 9 to 36 V: J_DCIN -> F1 10 A -> LM74700 ideal diode (reverse polarity) -> LM5069 hot-swap (UVLO 9 V, OVLO 40 V, current limit, power limit) -> the filter
#     (SRF1260 dual-winding choke on both lines, X capacitors, transient clamp) -> VIN_RAW to the block lands. Vehicle-side ground GND_V joins the kit ground GND through the choke's second winding.
part("J_DCIN", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: vehicle and shore DC in 9 to 36 V (lead from the D38999 wall receptacle DC pair): + -", "VH2", {"1": "DC_IN", "2": "GND_V"}, "C274411")
part("F1", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): vehicle input", "FUSE", {"1": "DC_IN", "2": "DC_F"})
# THE INPUT SIDE'S OWN NETS (16 September 2026, rule CMP-001). Fourteen of this board's nets carried a rated
# part and no declared voltage, so `derate.py` judged four parts on the whole board. The numbers here are the
# design's own: the input range is 9 to 36 V, the LM5069's over-voltage lockout turns the pass FET off at 40 V,
# and the SMCJ40A clamps a transient at about 64.5 V, which is the number a part on this net has to survive.
# 16 September 2026 (rule CMP-001): the clamp was an SMCJ33A on a line specified to 36 V, so it stood off LESS
# than the line's own working maximum and would have conducted in normal service at the top of the range. The
# same part sat on VIN_RAW here and on board A, three places and one defect. The replacement is the next
# standard standoff in the same land (Littelfuse SMCJ40A, C224052, stock 3,987), and it clamps 11 V higher, so
# this board's 50 V bus capacitor C8 moves to the 100 V part the set already buys (C5156756).
# THE VEHICLE AND SHORE ENTRY IS FIVE CONDUCTORS IN SERIES AT 8 A AND ALL FIVE WERE NODES (20 September 2026,
# appendix 32.249 and 32.251). The chain is J_DCIN -> DC_IN -> the 10 A blade F1 -> DC_F -> the LM74700 ideal
# diode Q1 -> DC_P -> the 10 mOhm hot-swap sense R19 -> HS_S -> the pass FET Q7 -> DC_HS -> the SRF1260
# choke L2 -> VIN_RAW, and every one of them carries VIN_RAW's own current (then declared 8.0 A typical and 10.0 A
# peak; 6.15 A for both since F-IN-02, 26 September 2026, the hot-swap's maximum limit). `HS_S` was
# not declared at all; the other four were `node`s, so `dc_drop` solved none of them and PI-001 and PI-002
# had never looked at this board's input side. `power_path` did not find them either, because L2 is a
# DUAL-WINDING choke on a four-pin land and its pass-through test knows a two-terminal part and a transistor.
#
# THE VOLTAGE IS THE PART THAT NEEDED CARE AND IT IS WHY THIS WAS NOT DONE IN THE SAME BREATH AS THE CHARGER'S.
# The node declared 53.3 V, which is the SMCJ40A clamping a transient at about 64.5 V at its peak pulse
# current, and `derate` judges a part against the WORST of everything declared about its net. Converting a
# node to a rail REMOVES the node, so declaring `volts=12.0` with `v_work=36.0`, the service maximum, would
# have left every 100 V ceramic on this line judged against 36 V where it is judged against 53.3 today: a
# LOOSENING, which is the shape 20 September 00:40 caught inside `derate` itself. THE FIRST VERSION OF THIS
# PUT THE CLAMP'S 53.3 IN `v_work` AND `derate` REFUSED THE SMCJ40A WITHIN MINUTES, for standing off 40 V on
# a line it had just been told runs to 53.3 V in normal service: a true sentence about a false input. The two
# numbers are two different facts and they go in two fields, which is why `rail()` gained `v_max`: `v_work`
# is the 36 V SERVICE maximum, which is what the protector is judged against, and `v_max` is the clamp's
# let-through, which is what every other part on the line is rated for. `derate` takes the worst of `volts`,
# `v_max` and `v_work` for a rating and reads `v_work` alone for the standoff rule.
#
# They are SEGMENTS of VIN_RAW's path, so the board's power total counts this input once.
# F-IN-02, 26 September 2026: their currents follow VIN_RAW's restated declaration (6.15 A typical and peak, the
# LM5069's maximum limit with R19 = 10 mOhm, which a unit at VCL max passes continuously); they were 8.0 and 10.0,
# which U6 never lets through.
_DC_V, _DC_T, _DC_P_, _DC_VW, _DC_VMAX = 12.0, _VIN_T, _VIN_P, 36.0, 53.3
_DC_NOTE = ("the vehicle and shore input: 9 to 36 V in normal use, the LM5069's over-voltage lockout off at "
            "40 V, and the SMCJ40 clamps (D10 SMCJ40CA at the entry, D1 SMCJ40A behind the ideal diode) "
            "clamping a transient at about 64.5 V at their peak pulse current, which is "
            "why the parts on this line are 100 V ceramics and why `v_work` is 53.3 and not the 36 V service "
            "maximum. It carries VIN_RAW's own current, this being one conductor run in five pieces")
for _dcn, _src, _load in (("DC_IN", "J_DCIN", "F1"), ("DC_F", "F1", "Q1"), ("DC_P", "Q1", "R19"),
                          ("HS_S", "R19", "Q7"), ("DC_HS", "Q7", "L2")):
    _intent.rail(_dcn, _DC_V, _DC_T, _DC_P_, _src, loads={_load: _DC_T}, v_work=_DC_VW, v_max=_DC_VMAX,
                 series_of="VIN_RAW", converted=False, note=_DC_NOTE)
_intent.node("GND_V", 0.0, "the vehicle-side return. It joins the kit ground through the choke's second "
             "winding and is NOT an isolation barrier, which is what boards/e.json declares to the ground "
             "system gate; it is a reference, and it is declared so a part across it is judged")
_intent.node("GND", 0.0, "the board's reference, so a part between a live net and ground is judged against "
             "the live net rather than reported as sitting on an undeclared one")
def ideal_diode(uref, qref, cref, rref, anode, cathode, gnd):
    """LM74700-Q1 (ti/ti-lm74700-q1.pdf, SOT-23-6: 1 VCAP, 2 GND, 3 EN, 4 CATHODE, 5 GATE, 6 ANODE) driving an N-FET (source at the anode, drain at the cathode)"""
    part(uref, "Connector_Generic", "Conn_01x06", "LM74700-Q1 ideal-diode controller: 1 VCAP 2 GND 3 EN 4 CATHODE 5 GATE 6 ANODE", "SOT236", {"1": uref + "_VCAP", "2": gnd, "3": anode, "4": cathode, "5": qref + "_G", "6": anode}, "C2941042")
    part(qref, "Transistor_FET", "IRF7404", "BSC039N06NS 60 V 3.9 mOhm N-FET (PG-TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8", {"1": anode, "2": anode, "3": anode, "4": qref + "_G", "5": cathode, "6": cathode, "7": cathode, "8": cathode}, "C534330")
    c(cref, "100n 50V", uref + "_VCAP", anode, "C", "C14663"); r(rref, "100k", qref + "_G", anode, "R", "C25803")
    # The VCAP capacitor sits between VCAP and the ANODE and both ends move together, so it sees the charge
    # pump's own bias and not the anode's height above ground: the same shape as a bootstrap capacitor, and the
    # same reason it is a 50 V part rather than something larger (16 September 2026, rule CMP-001).
    _intent.node(uref + "_VCAP", _intent.net_volts(anode) + 10.0,
                 "LM74700-Q1 VCAP: the internal charge pump sits about 10 V above the anode %s" % anode,
                 rides_on=anode, bias_v=10.0)
ideal_diode("U3", "Q1", "C4", "R1", "DC_F", "DC_P", "GND_V")
# S-09 / A03 / F-IN-01, 26 September 2026: D1 and D2 are unidirectional SMCJ40A (Littelfuse, LCSC C224052, the A
# suffix; SMCJ40CA is the two-way part) and both had the RETURN on pad 1, which is the cathode of the D_SMC land:
# each was forward-biased across its line, a short behind the fuse from the first connection and no clamp at all for
# a positive surge. The cathode goes to the line, the anode to its own return, and the symbol names them (D_Zener,
# pin 1 K, pin 2 A; see D3 above for why not D_TVS). Both sit BEHIND the ideal diode Q1 (D1 on DC_P, D2 on VIN_RAW),
# where a reversed input never arrives, so one-way parts are right there. D10, in FRONT of Q1, is a two-way part:
# see its own note below. The E17 board carries neither D10 nor the corrected D1 and D2.
part("D1", "Device", "D_Zener", "SMCJ40A (input surge: 40 V standoff on a line specified to 36 V, clamping 64.5 V; unidirectional, cathode on DC_P)", "TVS", {"1": "DC_P", "2": "GND_V"}, "C224052"); c("C2", "100n 100V", "DC_P", "GND_V", "C0805")
# LM5069 (ti/ti-lm5069.pdf, VSSOP-10: 1 SENSE 2 VIN 3 UVLO 4 OVLO 5 GND 6 TIMER 7 PWR 8 PGD 9 OUT 10 GATE); the -2 variant restarts after a fault; sense resistor 10 mOhm, pass FET 60 V
ic("U6", 10, "LM5069MM-2 hot-swap controller: 9 V on, 40 V off, current and power limit", "VSSOP10", {"1": "HS_S", "2": "DC_P", "3": "HS_UVLO", "4": "HS_OVLO", "5": "GND_V", "6": "HS_TIMER", "7": "HS_PWR", "8": "DCIN_PGD", "9": "DC_HS", "10": "HS_GATE"}, "C111822")
r("R19", "10mOhm 1% 2512 (hot-swap sense)", "DC_P", "HS_S", "RS2512"); nfet("Q7", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6), hot-swap pass", "HS_GATE", "HS_S", "DC_HS", lcsc="C473333")
r("R20", "100k 1%", "DC_P", "HS_UVLO"); r("R21", "38.3k 1% (UVLO: 9 V)", "HS_UVLO", "GND_V"); r("R22", "100k 1%", "DC_P", "HS_OVLO"); r("R23", "6.65k 1% (OVLO: 40 V)", "HS_OVLO", "GND_V")
c("C5", "100n (TIMER)", "HS_TIMER", "GND_V"); r("R24", "20k (PWR: power limit)", "HS_PWR", "GND_V"); r("R25", "10k", "DCIN_PGD", "+3V3_E6")
part("Q8", "Transistor_FET", "2N7002", "2N7002: SHORE_INHIBIT high pulls UVLO low = input off (1 G, 2 S, 3 D)", "SOT23", {"1": "SHORE_INHIBIT", "2": "GND_V", "3": "HS_UVLO"}); r("R26", "100k", "SHORE_INHIBIT", "GND")
# L2 IS A PASS-THROUGH AND NO SHAPE TEST CAN SEE IT (20 September 2026, appendix 32.253). Four pads, four
# nets, two windings: the line and the return. `power_path` knows a two-terminal part and a power transistor
# and reads this as a four-pin connector, which is why board E's whole input side was invisible to it while
# carrying 8 A. The heuristic widening was swept across six boards and refused, so the generator says it.
# R4E-09 (found while changing L2 for F-IN-02, 26 September 2026): THE CHOKE'S PIN MAP SHORTED BOTH LINES. The map
# was {1 DC_HS, 2 VIN_RAW, 3 GND_V, 4 GND} on the reading "winding 1 pins 1-2, winding 2 pins 3-4". The Bourns sheet
# (bourns-srf1260-common-mode-choke.pdf, sha256 93b2dc75..., "Electrical Schematic", read on the rendered page)
# draws N1 between pins 1 and 3 and N2 between pins 2 and 4, dots on 1 and 2; its PARALLEL drawing joins 1 to 2
# and 3 to 4, which would short a winding if the windings were 1-2 and 3-4; its land puts 1 and 2 across the
# 1.28 mm gap and 1 and 3 on the diagonal. On KiCad's L_CommonModeChoke_Bourns_SRF1260 land (pads 1 (-4.25,-1.7),
# 2 (-4.25,1.7), 3 (4.25,1.7), 4 (4.25,-1.7), 4.5 x 2.15 each, read from the KiCad 9.0.9 library on the box) the
# winding ends are again the DIAGONALS 1-3 and 2-4, and a diagonal stays a diagonal under any rotation or mirror
# of the part. So the old map put DC_HS and GND_V on one winding and VIN_RAW and GND on the other: a few mOhm
# across the vehicle input behind the hot-swap and across the raw bus, on this generator and on the committed E17
# board (pads read there: 1 DC_HS, 2 VIN_RAW, 3 GND_V, 4 GND). The map is now input side on pads 1 and 2
# (DC_HS, GND_V) and output side on pads 3 and 4 (VIN_RAW, GND): winding 1-3 carries the positive line and
# winding 2-4 the return, and in both ways the part can sit on this land (dots on pads 1 and 2, or on 3 and 4)
# the line current and the return current pass their windings in opposite senses, so the differential flux cancels
# and the part is a common-mode choke, as boards/e.json and pcb_emc.yaml describe it.
# F-IN-02 (26 September 2026, R4E-02): THE PART IS THE SRF1260-1R5Y. Each winding carries the whole line current,
# so the rating is the SERIES column: 1R5Y 6 uH series (1.5 uH per winding), 0.0302 Ohm, 6.89 A Irms (40 C rise),
# 9.15 A Isat, -40 to +105 C with the rise included. At 6.15 A continuous about 32 K of rise (83 C at the 51 C
# inside-air bar), at 4.85 A about 20 K. The 4R7Y it replaces is 3.59 A in that column. Same family, same sheet,
# same land and pin map. LCSC C7320434 (LCSC and JLC records 26 September 2026, drafts/lcsc/, drafts/jlc/: JLC stock 0,
# as the 4R7Y's C3273444 also reads), so the part stays hand-fitted like its predecessor (vendor/PARTS.md HAND_FIT)
# and the BOM field stays empty rather than name a code JLC cannot place. The cost is common-mode inductance, 1.5 uH
# per winding where 4.7 was; no filter number in this tree rests on it, and D-04 claims no EMC performance.
_intent.pass_through("L2", "the SRF1260 dual-winding choke in its common-mode connection: winding 1-3 carries "
                     "the positive line from DC_HS (pad 1) to VIN_RAW (pad 3) and winding 2-4 the return from "
                     "GND_V (pad 2) to GND (pad 4), so it is two pass-throughs in one four-pin package and no "
                     "shape test can tell it from a connector")
part("L2", "Connector_Generic", "Conn_01x04", "Bourns SRF1260-1R5Y dual-winding choke, common-mode connection (each winding carries the line current: 6.89 A Irms and 9.15 A Isat in the series column, 1.5 uH per winding): winding pins 1-3 on the positive line, winding pins 2-4 on the return (Bourns electrical schematic, N1 1-3 and N2 2-4)", "CMC", {"1": "DC_HS", "2": "GND_V", "3": "VIN_RAW", "4": "GND"})
c("C6", "1u 100V 1210 (X, input side)", "DC_HS", "GND_V", "C1210"); c("C7", "1u 100V 1210 (X, bus side)", "VIN_RAW", "GND", "C1210"); c("C8", "10u 100V X7R 1210", "VIN_RAW", "GND", "C1210")
part("D2", "Device", "D_Zener", "SMCJ40A (bus clamp: 40 V standoff on the 9 to 36 V bus; unidirectional, cathode on VIN_RAW)", "TVS", {"1": "VIN_RAW", "2": "GND"}, "C224052")
# OWNER DECISION 31, RULED 21 SEPTEMBER 2026: THE INLET'S CLAMP WAS BEHIND ITS OWN PASS FET. Read off this
# board's netlist the chain is J_DCIN.1 -> DC_IN -> F1 -> DC_F -> Q1 (the BSC039N06NS ideal diode, source pins
# 1 to 3, drain tab 5 to 8) -> DC_P -> D1, so the FIRST semiconductor a strike from the wall receptacle meets is
# the FET and the clamp sits one part behind it. Accepting that means accepting the FET's own rating for an 8 kV
# contact discharge, and a power FET publishes a human-body-model figure, which is a DIFFERENT TEST: Nexperia's
# PESD5V0S2BT sheet carries both for one part, 30 kV IEC 61000-4-2 contact against 10 kV MIL-STD-883 HBM, so
# one cannot be read as the other, and Infineon publishes the BSC039N06NS as a scan with no text layer and no
# ESD row to read either way. D10 goes on DC_F: AFTER the fuse, so a sustained overvoltage blows F1 rather than the
# clamp, and at the entry, which is where this project's own vendor sheets put it (Nexperia layout clause 1: place
# the device as close to the input terminal or connector as possible).
# S-09 / R4E-01, corrected 26 September 2026 after review: D10 IS A TWO-WAY PART, THE SMCJ40CA. DC_F is the ANODE side
# of the LM74700-Q1 ideal diode U3/Q1, the side a reversed input reaches. A one-way SMCJ40A there is a short in one
# polarity or the other: cathode on GND_V (as committed) it conducts on a correctly connected input; cathode on DC_F
# (this round's first correction) it is forward-biased on a REVERSED input, DC_IN -> F1 -> D10 -> GND_V, which blows
# the 10 A blade from a vehicle battery or cooks the SMC part on a current-limited supply below 10 A, and defeats the
# ideal diode's -65 V reverse rating. TI says what goes there (ti-lm74700-q1.pdf, SNOSD17G, 10.1.1.3): "a
# bi-directional TVS diode is used to protect from positive and negative transient voltages" and "The breakdown
# voltage of TVS- should be beyond than maximum reverse battery voltage ... so that the TVS- is not damaged due to
# long time exposure to reverse connected battery". Littelfuse SMCJ40CA (littelfuse-smcj-series-tvs.pdf rev
# 11/20/15, the SMCJ40A/SMCJ40CA row, marking BFR): VR 40 V, VBR 44.40 min / 49.10 max at 1 mA, VC 64.5 V at 23.3 A,
# IR 1 uA at VR, 1500 W 10/1000 us, TJ -65 to +150 C, DO-214AB, the same D_SMC land; LCSC C80273 (Littelfuse,
# stock 4,960, LCSC and JLC records of 26 September 2026 in drafts/lcsc/ and drafts/jlc/). Its 44.4 V minimum
# breakdown in the negative direction is above the 36 V service maximum, so a reversed input up to 36 V finds no
# path through D10 and the LM74700 blocks it as designed. NOT CLAIMED (D-16, no surge claim): a negative surge. At
# the negative clamp (64.5 V at 23.3 A) Q1's drain to source is that plus the voltage held on DC_P (76.5 V on a 12 V
# input), above Q1's 60 V and the LM74700's 75 V CATHODE-to-ANODE maximum; TI's Figure 10-3 shape for a 24 V
# system (two one-way parts back to back with a low-breakdown TVS-) cannot be met with a 36 V reverse input and a
# 60 V FET either.
# The symbol is Device:D_TVS, KiCad's two-way suppressor (pins A1/A2): for this part either pad may take either net.
# The value names the datasheet row "SMCJ40" as well as the part number because derate.py reads a suppressor's
# standoff with the pattern SM[ABC]J<NN>A? and a word boundary, which does not accept the C of a two-way part
# number (a tool defect, drafts/r4-decisions.md open items); the row carries the same 40 V standoff for both parts.
part("D10", "Device", "D_TVS", "SMCJ40CA (bidirectional, Littelfuse SMCJ40 row: 40 V standoff and 44.4 V minimum breakdown each way, clamping 64.5 V at 23.3 A; shore inlet clamp at the entry, in front of the ideal-diode FET, so a reversed input stays blocked)", "TVS", {"1": "DC_F", "2": "GND_V"}, "C80273")
r("R27", "2.2k", "VIN_RAW", "LED_A", "R", "C4190"); part("LED1", "Device", "LED", "green: vehicle input present", "LED", {"2": "LED_A", "1": "GND"})
# --- panel tracker stage (power/lt8705a.pdf, E4's design kept: LT8705A buck-boost, input regulated at the panel's maximum-power voltage (FBIN 17.6 V), output 15.1 V ORed into the bus; bench-fitted, 32.54)
part("J_SOLAR", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: bare panel in (lead from the D38999 spare pair; a 36-cell 12 V class panel, up to about 22 V open circuit, 100 W): + -", "VH2", {"1": "PV_IN", "2": "GND"}, "C274411")
part("F2", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): panel input", "FUSE", {"1": "PV_IN", "2": "PV_P"})
# THE PANEL SIDE. A 36-cell 12 V class panel is about 22 V open circuit at 25 degC and about 25 V cold, which
# is the steady peak a part on this net sees and what it is judged against.
# THE CLAMP ON THIS NET WAS GUARDING NOTHING, and it is fixed here (16 September 2026). The bulk capacitors
# are 100 uF 35 V polymer and the SMCJ33A that guarded them does not begin to conduct until 36.7 V at worst
# case: a sustained over-voltage between 35 and 36.7 V sat on the capacitors with the clamp doing nothing at
# all about it. `derate` judges the DECLARED STEADY voltage and cannot raise that, which is why it is written
# here rather than found by a gate. The answer is the lower standoff: an SMCJ28A (Littelfuse C224047, stock
# 6,072) stands off 28 V, which is still above the 25 V a cold 36-cell panel reaches open circuit, and begins
# to conduct at 31.1 V, which is BELOW the capacitors' rating. Its clamping voltage at the full 22 A pulse is
# 45.4 V and no clamp in this class is under 35, so a fast high-current surge still passes the capacitors more
# than their steady rating for microseconds; what has changed is that a slow over-voltage no longer can.
# PV_P FIRST, because PV_IN declares itself a segment of it and a rail that names another needs that one
# declared (the same ordering CELL+ and VBAT needed on board A at 03:05).
for _pvn in ("PV_P", "PV_IN"):
    # THE PANEL ENTRY IS A CONDUCTOR AND ITS CURRENT IS IN THE DESIGN'S OWN WORDS (20 September 2026,
    # appendix 32.251 named these as owed and said their currents were written down nowhere; they are, in the
    # line above that draws J_SOLAR). The panel is "a 36-cell 12 V class panel, up to about 22 V open
    # circuit, 100 W" and the tracker regulates its input at the maximum-power point, 17.6 V (R8 and R9, the
    # FBIN divider). So the maximum-power current is 100 / 17.6 = 5.68 A and the SHORT-CIRCUIT current of a
    # panel of that class is about 1.1 times it, 6.25 A, which is the most this conductor can ever carry and
    # is what `amps_peak` means. The 10 A blade F2 is protection and not a rating.
    # The VOLTAGE keeps both of the node's numbers: `volts` is the 17.6 V the tracker holds the panel at,
    # which is what the drop is judged as a fraction of, and `v_max` is the 25 V a cold panel reaches open
    # circuit, which is what a part on this net has to withstand. Putting the 25 in `volts` would have made
    # the drop bar 40 percent looser on a conductor that never runs there.
    _intent.rail(_pvn, 17.6, 5.68, 6.25, "J_SOLAR" if _pvn == "PV_IN" else "F2",
                 loads={"F2" if _pvn == "PV_IN" else "U5": 5.68}, v_work=25.0, v_max=25.0,
                 converted=False, **({"series_of": "PV_P"} if _pvn == "PV_IN" else
                                    {"always_on": True,
                                     "always_on_why": "a photovoltaic panel produces whenever there is light "
                                     "on it and nothing on this board is between the connector and the fuse, "
                                     "so there is no part whose enable pin could switch this rail. The "
                                     "tracker downstream decides how much of it is drawn, not whether it is "
                                     "present"}),
                 note="the bare panel entry: a 36-cell 12 V class panel at 100 W, about 22 V open circuit at "
                      "25 degC and about 25 V cold, held at its 17.6 V maximum-power point by the LT8705A's "
                      "FBIN divider. 5.68 A at that point and about 6.25 A into a short, which is the most "
                      "the conductor can carry")
# S-09 / A03 / F-IN-01, 26 September 2026: D4 is a unidirectional SMCJ28A (Littelfuse, LCSC C224047) and had GND on
# its cathode pad 1, forward-biased across the panel input. Cathode to PV_P, anode to GND, K/A symbol as D1 to D3.
part("D4", "Device", "D_Zener", "SMCJ28A (panel surge: 28 V standoff, conducting from 31.1 V, below the 35 V bulk capacitors; unidirectional, cathode on PV_P)", "TVS", {"1": "PV_P", "2": "GND"}, "C224047")
for k in range(1, 3): part("C%d" % (10 + k), "Device", "C_Polarized", "100u 35V Panasonic EEHZK1V101XP hybrid polymer (7.7 mm)", "CPOL63", {"1": "PV_P", "2": "GND"}, "C454360")
c("C13", "10u 50V", "PV_P", "GND", "C10u50"); c("C14", "10u 50V", "PV_P", "GND", "C10u50"); c("C15", "4.7u 50V", "PV_P", "GND", "C10u50")
part("U5", "Connector_Generic", "Conn_02x20_Odd_Even", "LT8705A buck-boost controller, 38-lead QFN 5x7 (pin 39 = exposed pad GND, pin 40 unused); bench-fitted", "QFN38", {
 "1": "TRK_SHDN", "2": "TRK_CSN", "3": "TRK_CSP", "4": "TRK_LDO33", "5": "TRK_FBIN", "6": "TRK_FBOUT", "7": "TRK_IMONO", "8": "TRK_VC", "9": "TRK_SS", "10": "NC", "11": "GND", "12": "TRK_RT", "13": "GND",
 "14": "TRK_BG1", "15": "TRK_INTVCC", "16": "TRK_BG2", "17": "TRK_BOOST2", "18": "TRK_TG2", "19": "TRK_SW2", "20": "NC", "21": "TRK_SW1", "22": "TRK_TG1", "23": "TRK_BOOST1", "24": "NC",
 "25": "NC", "26": "NC", "27": "NC", "28": "NC", "29": "TRK_OUT", "30": "TRK_OUT", "31": "TRK_OUT", "32": "PV_P", "33": "PV_P", "34": "PV_P", "35": "TRK_INTVCC", "36": "TRK_INTVCC", "37": "GND", "38": "TRK_IMONI", "39": "GND", "40": "NC"}, "C674164")
part("Q3", "Transistor_FET", "IRF7404", "BSC028N06NS 60 V 2.8 mOhm N-FET, M1 buck top (TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8", {"1": "TRK_SW1", "2": "TRK_SW1", "3": "TRK_SW1", "4": "TRK_TG1", "5": "PV_P", "6": "PV_P", "7": "PV_P", "8": "PV_P"}, "C148250")
part("Q4", "Transistor_FET", "IRF7404", "BSC039N06NS 60 V N-FET, M2 buck bottom", "TDSON8", {"1": "GND", "2": "GND", "3": "GND", "4": "TRK_BG1", "5": "TRK_SW1", "6": "TRK_SW1", "7": "TRK_SW1", "8": "TRK_SW1"}, "C534330")
part("Q5", "Transistor_FET", "IRF7404", "BSC028N06NS 60 V N-FET, M3 boost bottom", "TDSON8", {"1": "GND", "2": "GND", "3": "GND", "4": "TRK_BG2", "5": "TRK_SW2", "6": "TRK_SW2", "7": "TRK_SW2", "8": "TRK_SW2"}, "C148250")
part("Q6", "Transistor_FET", "IRF7404", "BSC039N06NS 60 V N-FET, M4 boost top", "TDSON8", {"1": "TRK_SW2", "2": "TRK_SW2", "3": "TRK_SW2", "4": "TRK_TG2", "5": "TRK_OUT", "6": "TRK_OUT", "7": "TRK_OUT", "8": "TRK_OUT"}, "C534330")
part("L1", "Device", "L", "10uH Coilcraft XAL1510-103MED (Isat 26 A, 10.0 mm tall)", "L1510", {"1": "TRK_SW1", "2": "TRK_LSENSE"}, "C3911782")
part("R5", "Device", "R", "5 mOhm 1% 3 W 2512 RSENSE (RALEC LR2512-23R005F4)", "RS2512", {"1": "TRK_LSENSE", "2": "TRK_SW2"}, "C154688")
r("R6", "100R", "TRK_LSENSE", "TRK_CSP"); r("R7", "100R", "TRK_SW2", "TRK_CSN"); c("C16", "1n", "TRK_CSP", "TRK_CSN", bypass=("U5", "3"))
# THE FILTER CAPACITOR BELONGS AT THE PINS AND THE TWO RESISTORS AT THE SHUNT (18 September 2026, rule ANA-001).
# R6 and R7 are the Kelvin series resistors of the tracker's current sense and C16 is the pair's filter; on E17 they
# sit 15 to 20 mm from the shunt R5 and 11 to 15 mm from U5, so the filtered pair itself runs beside the switching
# nodes (TRK_CSP 0.276 mm from TRK_SW2 over 5.55 mm, TRK_CSN 0.142 from TRK_SW1 over 9.33, both entirely outside the
# shared part's courtyard). The series resistor attenuates line pickup only when it sits at the SOURCE end and the
# capacitor at the amplifier, which is what every current-sense layout clause asks for, so C16 is declared as U5 pin
# 3's own decoupling here (bypass_slots reserves its seat before the packer runs) and the next E placement pass seats
# R6 and R7 against R5. The pair is then a short tight run and a pre-lay candidate.
c("C17", "470n 25V", "TRK_BOOST1", "TRK_SW1"); c("C18", "470n 25V", "TRK_BOOST2", "TRK_SW2")
part("D5", "Device", "D_Schottky", "BAT54 boost diode INTVCC -> BOOST1", "SOD123", {"1": "TRK_BOOST1", "2": "TRK_INTVCC"}); part("D6", "Device", "D_Schottky", "BAT54 boost diode INTVCC -> BOOST2", "SOD123", {"1": "TRK_BOOST2", "2": "TRK_INTVCC"})
c("C19", "4.7u 25V", "TRK_INTVCC", "GND", "C10u50"); c("C20", "1u", "TRK_LDO33", "GND")
r("R8", "102k 1% (RFBIN1: panel point 17.6 V)", "PV_P", "TRK_FBIN"); r("R9", "7.50k 1% (RFBIN2)", "TRK_FBIN", "GND")
r("R10", "115k 1% (RFBOUT1: 15.1 V)", "TRK_OUT", "TRK_FBOUT"); r("R11", "10.0k 1% (RFBOUT2)", "TRK_FBOUT", "GND")
# THE TRACKER'S OWN NETS. An LT8705A is a four-switch buck-boost like the LM5176 stages on board A, and the
# same reading applies: SW1 is the buck side and reaches the panel, SW2 is the boost side and reaches the
# regulated output, and each BOOST capacitor rides on its own SW at INTVCC, which is why they are small parts.
# TRK_OUT IS THE TRACKER'S OUTPUT CONDUCTOR AND IT WAS A NODE (20 September 2026). It carries the whole of
# the panel's power into the pack bus through the ideal diode U4, and as a node `dc_drop` solved nothing on
# it. Its current follows from the panel's own 100 W and this board's declared efficiency: 100 W times 0.93
# over 15.1 V is 6.16 A, and the peak is the same number because the panel's power is what bounds it, not its
# short-circuit current (at Isc the panel's voltage collapses and its power with it).
# 0.93 is the same assertion board A's five LM5176 stages make and is this project's, not a measurement; the
# LT8705A is working close to unity ratio here (17.6 V in, 15.1 out), which is its best point, so this is the
# conservative end of what such a stage does.
# THE LOAD IS THE PASS FET, NOT ITS CONTROLLER (21 September 2026, 03:16 CEST). This line declared U4, the LM74700
# whose pads on TRK_OUT are EN and ANODE, sense pins carrying microamps, so rail_crossings asked five barrels at each
# of two SOT-23-6 pads for 3.08 A apiece and declined both for want of room, twice a night, and via_current would
# attribute 6.16 A to a fanout via at a sense pin as it did HS_S at U6 pin 1 on 20 September. Q2, the TDSON-8 whose
# source pads 1 to 3 are on TRK_OUT and drain pads 5 to 8 on VIN_RAW, is what the current goes through.
_intent.rail("TRK_OUT", 15.1, 6.16, 6.16, "Q6", loads={"Q2": 6.16}, fed_from="PV_P", efficiency=0.93,
             # PWR-002 COULD NOT RESOLVE THIS RAIL AND THE REASON IS THE SYMBOL (20 September 2026).
             # U5 is drawn as a generic 40-pin connector because this library has no LT8705A symbol, so
             # every pinfunction in the netlist reads `Pin_NN` and no pattern over pin names can find the
             # controller's shutdown pin. Its pin 1 IS the enable and the net is named: the tool takes a
             # named enable net ahead of the pattern for exactly this case, as board P's BQ4050 does
             # through DSG_G. Nothing about the copper changes.
             switch="U5", enable_net="TRK_SHDN", converted=True,
             note="the LT8705A tracker's regulated output, set by R10 and R11 (115k over 10.0k), carrying "
                  "the panel's 100 W into the pack bus through the ideal diode U4")
_intent.node("TRK_SW1", 25.0, "LT8705A buck-side switching node: it reaches the panel", v_min=-1.0)
_intent.node("TRK_SW2", 15.1, "LT8705A boost-side switching node: it reaches the regulated output", v_min=-1.0)
_intent.node("TRK_INTVCC", 6.35, "the LT8705A's own INTVCC regulator, which supplies both gate drivers")
_intent.node("TRK_BOOST1", 25.0 + 6.35, "the bootstrap rides on TRK_SW1 at INTVCC",
             rides_on="TRK_SW1", bias_v=6.35)
_intent.node("TRK_BOOST2", 15.1 + 6.35, "the bootstrap rides on TRK_SW2 at INTVCC",
             rides_on="TRK_SW2", bias_v=6.35)
r("R12", "215k 1% (RT: 202 kHz)", "TRK_RT", "GND"); r("R13", "10k", "TRK_VC", "TRK_VCC1"); c("C21", "4.7n", "TRK_VCC1", "GND"); c("C22", "100p", "TRK_VC", "GND"); c("C23", "100n", "TRK_SS", "GND")
r("R14", "100k 1%", "PV_P", "TRK_SHDN"); r("R15", "15.0k 1% (SHDN: enable above about 9.5 V)", "TRK_SHDN", "GND")
r("R16", "10k", "TRK_IMONI", "GND"); r("R17", "10k", "TRK_IMONO", "GND")
for k in range(1, 3): part("C%d" % (23 + k), "Device", "C_Polarized", "39u 35V Panasonic 35SVPF39M polymer (6.9 mm)", "CPOL8", {"1": "TRK_OUT", "2": "GND"}, "C189474")
c("C26", "10u 25V", "TRK_OUT", "GND", "C10u50"); c("C27", "10u 25V", "TRK_OUT", "GND", "C10u50")
ideal_diode("U4", "Q2", "C28", "R18", "TRK_OUT", "VIN_RAW", "GND")   # tracker output ORed into the raw bus that A22's front end regulates
# --- the block lands (mirror of A22's J_DOCK, 32.57): 1-4 VIN_RAW, 5-7 GND, 8 SHORE_INHIBIT (from A22, into the hot-swap UVLO), 9-10 the controller's USB, 11 GND, 12 spare
part("J_BLK", "Connector_Generic", "Conn_01x12", "solder lands for the 12 signal wires to the block board underside (mirror of A22 J_DOCK): 1-4 VIN_RAW, 5-7 GND, 8 SHORE_INHIBIT, 9 USB D+, 10 USB D-, 11 GND, 12 spare", "POGO_T6",
     {"1": "VIN_RAW", "2": "VIN_RAW", "3": "VIN_RAW", "4": "VIN_RAW", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "BLK_SPARE"})
# --- controller power: AP63205 5 V 2 A buck from the pack node (diodes/diodes-ap63205.pdf, TSOT-26: 1 FB 2 EN 3 VIN 4 GND 5 SW 6 BST; fixed 5 V, FB is the output sense), TLV75533 3.3 V LDO (SOT-23-5: 1 IN 2 GND 3 EN 4 NC 5 OUT)
ic("U12", 6, "AP63205WU-7 5 V 2 A buck for the controller, the Geiger module and the fans' logic", "TSOT6", {"1": "+5V_E6", "2": "CELL_F", "3": "CELL_F", "4": "GND", "5": "E6_SW", "6": "E6_BST"}, "C2071056")
# E6_SW IS A SWITCHING NODE AND IT SAID NOTHING (20 September 2026, the same sweep). A node is not a rail and
# a drop budget in percent means nothing on it, but it must be DECLARED, because CMP-001 asks what voltage a
# part on a net can see and this one swings from about a diode drop below ground to the pack node that feeds
# the AP63205. Board A's five LM5176 stages have declared theirs since 16 September; this board declared none.
_intent.node("E6_SW", 16.8, "the AP63205's switching node: it swings to CELL_F, which is the pack at its 4S "
             "termination of 16.8 V, and a diode drop below ground on the other half of the cycle", v_min=-1.0)
part("L3", "Device", "L", "4.7uH XAL4030-472ME", "L4020", {"1": "E6_SW", "2": "+5V_E6"}); c("C30", "100n", "E6_BST", "E6_SW"); c("C31", "10u 25V 1210", "CELL_F", "GND", "C1210"); c("C32", "22u 10V X7R 1210", "+5V_E6", "GND", "C1210"); c("C33", "22u 10V X7R 1210", "+5V_E6", "GND", "C1210")
ic("U13", 5, "TLV75533PDBVR 3.3 V LDO", "SOT235", {"1": "+5V_E6", "2": "GND", "3": "+5V_E6", "4": "NC", "5": "+3V3_E6"}, "C404027"); c("C34", "1u", "+5V_E6", "GND"); c("C35", "1u", "+3V3_E6", "GND")
# --- RP2040 (rp2040/rpi-rp2040-datasheet.pdf, QFN-56; the minimal design of the hardware design guide: 12 MHz crystal with 15 pF loads and a 1k series on XOUT, W25Q16 QSPI flash, 27 Ohm USB series,
#     RUN pull-up, BOOTSEL by a solder jumper on QSPI_SS). GPIO: 2 SMBD 3 SMBC (the pack gauge's SMBus, the RP2040's I2C1), 4 SDA1 5 SCL1 (the sensor bus, the RP2040's
#     I2C0: BME688, BMI270, SGP41, pod, lightning module), 6 DCF77 pulse, 7 Geiger pulse,
#     8 and 9 fan PWM, 10 and 11 fan tachometers, 12 input power good, 13 IMU interrupt, 14 lightning interrupt, 15 SHORE_INHIBIT read-back, 16 lid and tamper switch (S-11),
#     17 pack PRES (S-05), 18 Geiger supply enable (F-BP-02), 25 status LED, 26 water electrodes (ADC0), 27 bus voltage (ADC1), 28 pack voltage (ADC2).
#     26 September 2026 (MESHSAT-1357 round 4): the pack pair was written "2 SDA0 3 SCL0 (pack section A)" and "section B" on the sensor bus, the BB-2590/U's two
#     SMBus sections; the RP2040's own peripheral map (datasheet Table 279) puts GPIO2/3 on I2C1 and GPIO4/5 on I2C0, and the status LED is GPIO25 (pin 37), not 21.
ic("U10", 57, "RP2040 sensor controller (USB to B16 through the dock)", "QFN56", {
 "1": "+3V3_E6", "2": "NC", "3": "NC", "4": "SMBD", "5": "SMBC", "6": "SDA1", "7": "SCL1", "8": "DCF_PULSE", "9": "GEIGER_IN", "10": "+3V3_E6", "11": "FAN1_PWM", "12": "FAN2_PWM", "13": "FAN1_TACH", "14": "FAN2_TACH",
 "15": "DCIN_PGD", "16": "IMU_INT1", "17": "LTG_IRQ", "18": "SHORE_INHIBIT", "19": "GND", "20": "XIN", "21": "XOUT_R", "22": "+3V3_E6", "23": "E6_DVDD", "24": "SWCLK", "25": "SWDIO", "26": "E6_RUN",
 "27": "TAMPER_IO", "28": "PRES_IO", "29": "GEIGER_EN", "30": "NC", "31": "NC", "32": "NC", "33": "+3V3_E6", "34": "NC", "35": "NC", "36": "NC", "37": "LED_STAT", "38": "WATER_SENSE", "39": "VIN_MON", "40": "CELL_MON", "41": "NC",
 "42": "+3V3_E6", "43": "+3V3_E6", "44": "+3V3_E6", "45": "E6_DVDD", "46": "USB_DM_R", "47": "USB_DP_R", "48": "+3V3_E6", "49": "+3V3_E6", "50": "E6_DVDD", "51": "QSPI_D3", "52": "QSPI_SCLK", "53": "QSPI_D0",
 "54": "QSPI_D2", "55": "QSPI_D1", "56": "QSPI_SS", "57": "GND"}, "C2040")
ic("U11", 9, "W25Q16JVUXIQ 16 Mbit QSPI flash (USON-8: 1 CS 2 DO/IO1 3 WP/IO2 4 GND 5 DI/IO0 6 CLK 7 HOLD/IO3 8 VCC, pad)", "USON8", {"1": "QSPI_SS", "2": "QSPI_D1", "3": "QSPI_D2", "4": "GND", "5": "QSPI_D0", "6": "QSPI_SCLK", "7": "QSPI_D3", "8": "+3V3_E6", "9": "GND"}, "C2843335")
part("Y1", "Device", "Crystal_GND24", "12 MHz ABM8-272-T3 (3225): 1 XIN, 3 XOUT, 2 and 4 GND", "XTAL", {"1": "XIN", "2": "GND", "3": "XOUT", "4": "GND"}, "C20625731")
c("C36", "15p", "XIN", "GND"); c("C37", "15p", "XOUT", "GND"); r("R28", "1k", "XOUT_R", "XOUT")
r("R29", "27R", "USB_DP_R", "USB_E6_P"); r("R30", "27R", "USB_DM_R", "USB_E6_N"); r("R31", "10k", "E6_RUN", "+3V3_E6"); r("R32", "1k (BOOTSEL)", "QSPI_SS", "BOOT_J"); part("JP1", "Jumper", "SolderJumper_2_Open", "BOOTSEL: short while powering to enter the USB bootloader", "JP2", {"1": "BOOT_J", "2": "GND"})
for k in range(38, 45): c("C%d" % k, "100n", "+3V3_E6", "GND")
c("C45", "1u", "E6_DVDD", "GND"); c("C46", "1u", "E6_DVDD", "GND"); c("C47", "1u", "+3V3_E6", "GND")
tp("TP10", "SWCLK"); tp("TP11", "SWDIO"); tp("TP12", "E6_RUN")
r("R33", "1k", "LED_STAT", "LED_STAT_A"); part("LED2", "Device", "LED", "status (GPIO25)", "LED", {"2": "LED_STAT_A", "1": "GND"})
r("R34", "4.7k", "SMBD", "+3V3_E6"); r("R35", "4.7k", "SMBC", "+3V3_E6"); r("R36", "4.7k", "SDA1", "+3V3_E6"); r("R37", "4.7k", "SCL1", "+3V3_E6")
# S-05, 26 September 2026: the pack's PRES pin from J_SMB.4 to GPIO17 (the reasoning and the thresholds are at J_SMB above)
r("R54", "1k", "PRES_LEAD", "PRES_IO", "R", "C21190"); r("R55", "1M", "PRES_IO", "+3V3_E6", "R", "C22935")
# S-11 / D-02b / D-03.2, 26 September 2026 (MESHSAT-1357 round 4): THE LID AND TAMPER SWITCH. Appendix 32.50 item 6
# approved "one sealed switch under the frame" and the E6 floor plan (32.51 item 4) put its input on this board; no
# generator ever drew it (W1-F04, W5-F11). The owner's D-02b makes the lid state the reduced mode's trigger and
# D-03.2 rules that it LOGS ONLY: it never reaches ZEROIZE, the panel or any supervisor. So it goes to the sensor
# controller alone, which is on the always-on domain (U12's EN is tied to CELL_F) and logs a lid opening with the
# kit off; the RP2040 wakes from DORMANT on a GPIO edge (rpi-rp2040-datasheet 2.11.3), which is what makes that log
# cheap. The switch is a reed sensor, Littelfuse 59140-1-S-05-A (normally open, hermetically sealed, IP67, -40 to
# +105 C, 1000 mm tinned leads, activation 9 to 16 mm and release 10 to 17 mm with the matching AlNiCo actuator
# 57140-000 in the lid; Littelfuse 59140 datasheet revised 03/25/22, drafts/datasheets), mounted under the frame
# and closed by the magnet when the lid is shut: it needs no hole in any seal and works through the aluminium face
# (the datasheet lists aluminium among the non-ferrous materials it operates through). NORMALLY OPEN is the tamper-
# evident choice: lid shut is contact closed and a LOW input, so a cut or unplugged lead reads as a lid OPEN and is
# logged, where a normally-closed contact would read a cut lead as a shut lid. The lead lands on a JST-XH 1x2
# (B2B-XH-A, LCSC C158012, -25 to +85 C). R52 100k pulls the lead up (33 uA while the lid is shut), R53 10k and C52
# 100 nF filter the 1 m lead at the pin (1 ms falling, 11 ms rising), because the lead runs past a 30 W VHF stage.
# The lead stays inside the sealed case, so it is not an external port for rule TRN-001.
part("J_TAMP", "Connector_Generic", "Conn_01x02", "JST-XH 1x2 (B2B-XH-A): lid and tamper reed sensor lead, Littelfuse 59140-1-S-05-A normally open under the frame, 57140-000 magnet in the lid: 1 lead, 2 GND", "XH2",
     {"1": "TAMPER_LEAD", "2": "GND"}, "C158012")
r("R52", "100k", "TAMPER_LEAD", "+3V3_E6", "R", "C25803"); r("R53", "10k", "TAMPER_LEAD", "TAMPER_IO", "R", "C25804"); c("C52", "100n", "TAMPER_IO", "GND", "C", "C14663")
# --- sensors on the strip: BME688 inside climate and gas (bosch/bosch-bme688.pdf, LGA-8: 1 GND 2 CSB 3 SDI 4 SCK 5 SDO 6 VDDIO 7 GND 8 VDD; I2C 0x76 with SDO low), BMI270 IMU for shock, tilt and
#     motion (bosch/bosch-bmi270.pdf, LGA-14; I2C 0x68 with SDO low; CSB and the unused OIS and aux pins tied per the sheet's I2C column); the magnetometer sits in the outside pod (32.57)
ic("U14", 8, "BME688 inside climate: temperature, humidity, pressure, gas index (I2C 0x76)", "LGA8B", {"1": "GND", "2": "+3V3_E6", "3": "SDA1", "4": "SCL1", "5": "GND", "6": "+3V3_E6", "7": "GND", "8": "+3V3_E6"}, "C3664478"); c("C48", "100n", "+3V3_E6", "GND")
ic("U15", 14, "BMI270 six-axis IMU (I2C 0x68): shock and tilt log, motion wake", "LGA14B", {"1": "GND", "2": "GND", "3": "GND", "4": "IMU_INT1", "5": "+3V3_E6", "6": "GND", "7": "GND", "8": "+3V3_E6", "9": "NC", "10": "NC", "11": "NC", "12": "IMU_CSB", "13": "SCL1", "14": "SDA1"}, "C2836813"); r("R51", "0R (CSB high: I2C mode; its own net keeps the pin joiner off the diagonal)", "+3V3_E6", "IMU_CSB"); c("C49", "100n", "+3V3_E6", "GND"); c("C50", "100n", "+3V3_E6", "GND")
# S-10 / C-05, 26 September 2026 (MESHSAT-1357 round 4): THE BATTERY-BAY GAS SENSOR APPENDIX 32.54 PICKED. The pick was
# a BME688 inside, one in the pod AND "the Sensirion SGP41 (C3659325) in the battery bay", and no generator ever fitted
# the SGP41 (W1-F05, C-05). It goes on this board because this board is where the bay's air is: the pack sits in the
# east pocket at X 120 to 178 (adjudication A06) and this strip ends at X 118, so the placement puts U17 at the strip's
# east end, south of PCB-A's edge (about X 110 to 117, Y -105 to -90), with the sensor opening facing up and the mixer
# fans moving the sealed case's air past it; the placement generator is regenerated at layout entry, not now.
# SGP41-D-R4 (Sensirion, LCSC C3659325, JLC stock 2,572 on 26 Sep 2026), DFN-6 2.44 x 2.44 x 0.85 mm, datasheet
# version 1.0 December 2021 (v2/vendor/sensirion/sgp41-datasheet.pdf): Table 6 pins 1 VDD, 2 VSS, 3 SDA, 4 n/a
# ("connect to ground"), 5 VDDH, 6 SCL, die pad ground; VDD and VDDH 1.7 to 3.6 V from ONE supply; I2C address 0x59
# (section 4.2), which no other device on SDA1/SCL1 uses (BME688 0x76, BMI270 0x68). Figure 6 is copied: VDD through
# 4.7 Ohm with 1 uF at the pin (R57, C57), VDDH straight from the rail with 1 uF (C58), the bus pull-ups are R36 and
# R37. Absolute operating range -20 to +55 C (Table 5); the gas specification holds at -10 to +50 C (Table 4), which
# is W6-P7's point and is recorded, not designed around. Its humidity compensation takes U14's reading. The package
# is not in KiCad's libraries: its land is Sensirion's Figure 18, drawn by drafts/footprints/gen_footprint_sgp41.py.
# Assembly: the sensor opening must stay free of conformal coating and the board is not washed after it is placed
# (datasheet 5.4); board E is declared conformally coated, so the coating mask is a work instruction.
ic("U17", 7, "SGP41-D-R4 VOC and NOx gas sensor, battery-bay air (I2C 0x59; DFN-6: 1 VDD 2 VSS 3 SDA 4 n/a to GND 5 VDDH 6 SCL, 7 die pad GND)", "DFN6S",
   {"1": "SGP_VDD", "2": "GND", "3": "SDA1", "4": "GND", "5": "+3V3_E6", "6": "SCL1", "7": "GND"}, "C3659325")
r("R57", "4.7R", "+3V3_E6", "SGP_VDD", "R", "C23164"); c("C57", "1u", "SGP_VDD", "GND", "C", "C15849"); c("C58", "1u", "+3V3_E6", "GND", "C", "C15849")
# --- water electrodes (two exposed pads on the strip's underside edge, 1 mm above the floor on the VHB pads), fans, headers
part("PAD_W1", "Connector", "Conn_01x01_Pin", "water electrode A (bare copper, +3.3 V through 1 M)", "PAD86", {"1": "WATER_A"}); r("R38", "1M", "+3V3_E6", "WATER_A")
part("PAD_W2", "Connector", "Conn_01x01_Pin", "water electrode B (bare copper, to ADC0)", "PAD86", {"1": "WATER_SENSE"}); r("R39", "1M", "WATER_SENSE", "GND"); c("C51", "100n", "WATER_SENSE", "GND")
r("R40", "100k 1%", "VIN_RAW", "VIN_MON"); r("R41", "10k 1% (ADC1: 0.091 x bus)", "VIN_MON", "GND"); r("R42", "100k 1%", "CELL_F", "CELL_MON"); r("R43", "22k 1% (ADC2: 0.18 x pack)", "CELL_MON", "GND")
for n in ("1", "2"):
    ph("J_FAN%s" % n, 3, "mixer fan %s under the plate (12 V class fan on the pack node, low-side PWM, tachometer)" % n, {"1": "CELL_F", "2": "FAN%s_SW" % n, "3": "FAN%s_TACH" % n})
    part("Q%s" % ("9" if n == "1" else "10"), "Transistor_FET", "2N7002", "2N7002 fan %s low-side switch (1 G, 2 S, 3 D)" % n, "SOT23", {"1": "FAN%s_G" % n, "2": "GND", "3": "FAN%s_SW" % n})
    r("R%s" % ("44" if n == "1" else "45"), "100R", "FAN%s_PWM" % n, "FAN%s_G" % n); r("R%s" % ("46" if n == "1" else "47"), "10k", "FAN%s_TACH" % n, "+3V3_E6")
    part("D%s" % ("7" if n == "1" else "8"), "Device", "D_Schottky", "SS14 flyback across fan %s" % n, "SMB", {"1": "CELL_F", "2": "FAN%s_SW" % n})
# F-BP-02, 26 September 2026: the Geiger header takes its 5 V from the load switch U16 (declared at +5V_GEIGER above).
# kisch.tps22810 is the same pin map boards B and D use (6 VIN, 5 EN, 1 VOUT, 2 QOD open, 3 CT, 4 GND, 7 pad GND).
kisch.tps22810("U16", "+5V_E6", "GEIGER_EN", "+5V_GEIGER", "GEIGER_CT")
r("R56", "100k", "GEIGER_EN", "GND", "R", "C25803"); c("C53", "1n", "GEIGER_CT", "GND", "C", "C1588")
c("C54", "10u 25V", "+5V_GEIGER", "GND", "C10u50", "C89632"); c("C55", "100n", "+5V_GEIGER", "GND", "C", "C14663"); c("C56", "1u", "+5V_E6", "GND", "C", "C15849")
ph("J_GEIGER", 3, "Geiger counter module (RadiationD-v1.1 class): 5 V switched by U16, GND, pulse", {"1": "+5V_GEIGER", "2": "GND", "3": "GEIGER_PULSE"})
ph("J_DCF", 3, "DCF77 receiver module: 3.3 V, GND, pulse", {"1": "+3V3_E6", "2": "GND", "3": "DCF_PULSE"})
ph("J_LTG", 5, "AS3935 lightning sensor module (CJMCU-3935 class): 3.3 V, GND, SDA, SCL, IRQ", {"1": "+3V3_E6", "2": "GND", "3": "SDA1", "4": "SCL1", "5": "LTG_IRQ"})
ph("J_POD", 4, "outside sensor pod on the connector plate (M8 sealed lead): 3.3 V, GND, SDA, SCL", {"1": "+3V3_E6", "2": "GND", "3": "SDA1", "4": "SCL1"})
# OWNER DECISION 31, RULED BY THE SESSION 21 SEPTEMBER 2026. The pod's three conductors leave the case through
# an M8 sealed receptacle on the connector plate and reach the RP2040 with nothing between them: port_protect
# named J_POD.1, .3 and .4 on every reading since the rule was written. Decision 34 states the level, IEC
# 61000-4-2 level 4 at 8 kV contact and 15 kV air, and the USBLC6-2SC6's own datasheet
# (v2/vendor/st/st-usblc6-2-esd-protection.pdf) guarantees exactly that level: two data lines clamped to the
# rail and the rail itself clamped to ground, which is the pod's own shape, in a part this project already buys
# five times on board B and once on board P. No new part number and no new footprint.
kisch.esd("D9", "SDA1", "SCL1", "+3V3_E6")
# 9 Sep 2026 (E7, appendix 32.83): U10 pin 9 was on GEIGER_PULSE, so R48 sat in series with NOTHING: the module's pulse reached the
# RP2040 pin directly and GEIGER_IN went only to TP13. Pin 9 is GEIGER_IN now and the resistor is in the path it was drawn for.
# (This comment is on its OWN line: appended to the code line it swallowed tp("TP13") and R49 and R50, the trap CLAUDE.md section 8 names.)
r("R48", "22R (pulse input series)", "GEIGER_PULSE", "GEIGER_IN"); tp("TP13", "GEIGER_IN"); r("R49", "10k", "DCF_PULSE", "+3V3_E6"); r("R50", "10k", "LTG_IRQ", "+3V3_E6")
tp("TP1", "DC_IN"); tp("TP2", "DC_P"); tp("TP3", "VIN_RAW"); tp("TP4", "GND"); tp("TP5", "PV_P"); tp("TP6", "TRK_OUT"); tp("TP7", "BLK_SPARE"); tp("TP8", "CELL_F"); tp("TP9", "+5V_E6")
for i, net in enumerate(("DC_IN", "DC_F", "DC_P", "DC_HS", "GND_V", "GND", "VIN_RAW", "PV_IN", "PV_P", "TRK_OUT", "TRK_INTVCC", "TRK_LDO33", "CELL+", "CELL_F", "+5V_E6", "+3V3_E6", "E6_DVDD"), 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})

# ----------------------------------------------------------------- emit
POWER = {"GND": ("power", "GND"), "+5V": ("power", "+5V"), "+3V3": ("power", "+3V3")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
# power flag symbols connect at their pin; place them wired to a label of the net

# layout: columns, top-down cursor; group order = list order with section titles
SECTIONS = [("PACK ENTRY: PACK CABLE ON XT60, 25 A BLADE, PADS TO THE BLOCK, PACK SMBUS LEAD (JST-XH 1x4)", ["J_BATT", "F3", "P_CP", "P_CN", "J_SMB", "C1", "D3"]),
            ("VEHICLE AND SHORE ENTRY 9-36 V: F1, LM74700 IDEAL DIODE, LM5069 HOT-SWAP, SRF1260 FILTER, CLAMPS", ["J_DCIN", "F1", "U3", "Q1", "C4", "R1", "D1", "C2", "U6", "R19", "Q7", "R20", "R21", "R22", "R23", "C5", "R24", "R25", "Q8", "R26", "L2", "D10", "C6", "C7", "C8", "D2", "R27", "LED1"]),
            ("PANEL TRACKER: J_SOLAR, F2, LT8705A BUCK-BOOST (FBIN 17.6 V, FBOUT 15.1 V, 202 kHz), ORed INTO THE RAW BUS", ["J_SOLAR", "F2", "D4", "C11", "C12", "C13", "C14", "C15", "U5", "Q3", "Q4", "Q5", "Q6", "L1", "R5", "R6", "R7", "C16", "C17", "C18", "D5", "D6", "C19", "C20", "R8", "R9", "R10", "R11", "R12", "R13", "C21", "C22", "C23", "R14", "R15", "R16", "R17", "C24", "C25", "C26", "C27", "U4", "Q2", "C28", "R18"]),
            ("BLOCK LANDS (MIRROR OF A22 J_DOCK)", ["J_BLK"]),
            ("SENSOR CONTROLLER: 5 V BUCK, 3.3 V LDO, RP2040, QSPI FLASH, CRYSTAL, USB, BOOTSEL, PULL-UPS", ["U12", "L3", "C30", "C31", "C32", "C33", "U13", "C34", "C35", "U10", "U11", "Y1", "C36", "C37", "R28", "R29", "R30", "R31", "R32", "JP1"] + ["C%d" % k for k in range(38, 48)] + ["TP10", "TP11", "TP12", "R33", "LED2", "R34", "R35", "R36", "R37", "R54", "R55"]),
            ("SENSORS, WATER ELECTRODES, MONITORS, FANS, HEADERS, LID SWITCH, GEIGER SUPPLY", ["U14", "C48", "U15", "R51", "C49", "C50", "U17", "R57", "C57", "C58", "J_TAMP", "R52", "R53", "C52", "PAD_W1", "R38", "PAD_W2", "R39", "C51", "R40", "R41", "R42", "R43", "D9", "J_FAN1", "Q9", "R44", "R46", "D7", "J_FAN2", "Q10", "R45", "R47", "D8", "U16", "R56", "C53", "C54", "C55", "C56", "J_GEIGER", "J_DCF", "J_LTG", "J_POD", "R48", "TP13", "R49", "R50"]),
            ("TEST POINTS, FLAGS", ["TP%d" % k for k in range(1, 10)] + ["#FLG%02d" % k for k in range(1, 18)])]
_listed = {r for _, refs in SECTIONS for r in refs}
_rest = [p["ref"] for p in P if p["ref"] not in _listed]
if _rest: SECTIONS.append(("OTHER PARTS (not in a section list)", _rest))
for _i, _pin in enumerate((1, 10, 22, 33, 42, 49)): _intent.bypass("C%d" % (38 + _i), "U10", _pin, "+3V3_E6")   # the RP2040's six IOVDD pins
_intent.bypass("C44", "U11", "8", "+3V3_E6")     # the QSPI flash's VCC
_intent.bypass("C45", "U10", "23", "E6_DVDD"); _intent.bypass("C46", "U10", "50", "E6_DVDD")
_intent.bypass("C47", "U10", "44", "+3V3_E6")    # VREG_VIN
_intent.bypass("C31", "U12", "2", "CELL_F")      # the 5 V buck's input capacitor, the loop that matters on a switcher
# THE BOOTSTRAP CAPACITOR IS A DECOUPLING CAPACITOR OF ITS OWN PIN (18 September 2026, E16). The AP63205's BST to SW
# capacitor C30 sat 17.6 mm from pin 6 in the PACK region's packer rows, and /E6_BST is the net that stayed open on E7
# (closed by the stub router then), E14 and E16 (17.6 mm apart after the closers). The datasheet puts it at the pin; a
# declared slot puts it there before the packer runs, which is the same answer the input capacitor C31 already has.
_intent.bypass("C30", "U12", "6", "E6_BST")
_intent.bypass("C34", "U13", "1", "+5V_E6"); _intent.bypass("C35", "U13", "5", "+3V3_E6")   # the LDO's input and output
_intent.bypass("C48", "U14", "8", "+3V3_E6")     # BME688 VDD
_intent.bypass("C49", "U15", "8", "+3V3_E6"); _intent.bypass("C50", "U15", "5", "+3V3_E6")  # BMI270 VDD and VDDIO
_intent.bypass("C57", "U17", "1", "SGP_VDD"); _intent.bypass("C58", "U17", "5", "+3V3_E6")   # SGP41 VDD and VDDH (Figure 6), S-10 26 September 2026
_intent.bypass("C56", "U16", "6", "+5V_E6")      # TPS22810 VIN (SLVSDH0C: 1 uF input capacitor), F-BP-02 26 September 2026
import schlayout, time as _time
PAPER, NPAGES, NCOLS, NROWS = schlayout.run(P, SECTIONS, POWER, _intent._I["bypass"], {"date": _time.strftime("%Y-%m-%d")}, os.environ.get("PHASE", ""), 'PCB-E1 DOCK')   # 15 Sep 2026: one A3 page per block, real wiring (32.196)
out = kisch.out
print("layout: %d A3 pages on a %d x %d sheet -> paper %s" % (NPAGES, NCOLS, NROWS, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper %s)\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-E1 DOCK") (date "%s")' % _time.strftime("%Y-%m-%d") + ' (rev "A (E6)") (company "MeshSat") (comment 1 "Phase ' + (os.environ.get("PHASE") or "?") + ' schematic (MESHSAT-830, appendix 32.55 to 32.57), generated by tools/gen_sch_e.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "E6: BB-2590/U cable entry and 25 A blade to the raised block; vehicle input 9-36 V through LM74700, LM5069 hot-swap and the SRF1260 filter to the raw bus up the dock contacts; LT8705A panel tracker ORed into the bus; RP2040 sensor controller on USB (BME688, BMI270, water electrodes, fans, pack SMBus, Geiger, DCF77, lightning and pod headers); eleven float clamps."))\n'
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
# --- decoupling as data (8 Sep 2026, MESHSAT-862 Stage C): the pin each capacitor serves, so the loop gate measures a distance instead of
# counting parts. The tracker's compensation and soft-start networks (C16 to C23), the boost and bootstrap capacitors (C17, C18, C30), the
# hot-swap timer (C5), the crystal loads and the sense filters are not decoupling and are not listed. `intent.write` refuses an entry whose
# capacitor is not on that pin's net, so a wrong line here stops the generator.
# The dock strip's only differential pair is the sensor controller's own USB port, and the RP2040 is USB 1.1 FULL SPEED. The shared USB
# class targets 90 ohm, which belongs to USB 2.0 high speed; requiring it here is a wrong requirement, not a strict one, so this board
# declares the class with no impedance target and `impedance_check.py` skips it (9 September 2026, the same as C9).
_intent.pair_class("USB")

_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
