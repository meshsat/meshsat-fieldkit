#!/usr/bin/env python3
"""PCB-B COMPUTE, phase B16 (MESHSAT-830, appendix 32.52 fabric, 32.58 floor plan): generate the KiCad 9 schematic (netlist style: every pin gets a
stub and a net label; GND pins get power symbols). Runs where the KiCad symbol libraries are (the vast.ai box). Usage: gen_sch_b.py <out.kicad_sch> <project>

Three identical slot columns S1, S2, S3, each a Compute Module 5 on two Amphenol 10164227 receptacles (U30A/B, U31A/B, U32A/B) with, per slot:
a Diodes PI7C9X2G404SL one-to-three PCIe switch (upstream the module's Gen 2 lane; port 1 an NVMe M.2 M-key 2242 socket, port 2 the slot's card
socket: S1 the WiFi link card on an M.2 E-key 2230, S2 the 5G module on an M.2 B-key 3052 with two nano-SIM holders, S3 the second WiFi link card on an M.2 E-key 2230), a TI
TUSB8041I four-port USB 3 hub on the module's USB3-0 port, the module's Ethernet pairs into the shared KSZ9897R switch through coupling capacitors,
the module's HDMI0 into the shared two-stage TS3DV642 display switch, the slot's 5 V lead from A22 (J_5V_Sx), two AP64500 3.3 V bucks (A: the card
socket rail on PCIE_PWR_EN; B: switch, hub and NVMe, following the module's 3.3 V), TPS62933 bucks for the switch core (1.0 V) and the hub core
(1.1 V), the flashing USB-C, fan header, LEDs, bench headers and 2N7002 level stages on every line that crosses into the module domain.
Shared: KSZ9897R (ports 1-3 the modules, port 4 the wall RJ45 through Pulse H5007NL magnetics with the TPS23861 PoE injector on the 54 V lead), the
HDMI type A receptacle for the monitor, the LG290P GNSS, the E22-900M30S 1 W LoRa module on S3's SPI, two E72 CC2652P radios, four CP2102N bridges,
the LimeSDR USB 3 receptacle and the RockBLOCK 9704 header behind TPS259631 eFuses, the QMX, camera and spare USB headers, two PCA9555, the
ATECC608B secure element, DS3231MZ holdover clock, TMP117, the hardware EMCON gates (74LVC08), the panel ribbon J_PANEL (2x13) and the A22 ribbon
J_AB1 (2x13, underside). Every radio is a USB device of one hub; the kit I2C bus (SDA/SCL from the panel controller) reaches A22 over J_AB1.
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-b-compute"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from idc_pads import idc   # the IDC land is a per-board measurement (IDC_PADS), not a default: see idc_pads.py
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, esd, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, synth_symbol, text, tps22810, uq, usb_c_recept, wire)
import intent as _intent
# ------------------------------------------------------------------ the rails, with where their current goes
# LOADS DECLARED 13 September 2026 (MESHSAT-862). Undeclared, `dc_drop` splits a rail's current evenly over
# every U and J footprint on it, and that guess has decided boards: it put 10 A through a SENSE pin on A24's
# CELL+ and 6 A through one on VBUS20. Each figure below is a branch of the rail apportioned to its own
# documented draw where a document gives one, and otherwise to the part's rating; the sum is held under the
# rail's declared peak. What it buys is that the copper is judged at the current each branch really carries.
#
# THE MODULE'S OWN DRAW IS 0.9 A, NOT 5. The note this line used to carry said "the CM5 draws up to 5 A",
# which is the datasheet's INPUT capability ("Single 5 V power input with USB power delivery support for up
# to 5 A at 5 V", CM5 datasheet section 1.3): that 5 A is what a carrier may feed a CM5 for itself AND its
# peripherals. The module's own figure is Table 9, current consumption: idle 400 mA, operation 900 mA
# typical, no maximum given. Ours is declared at 1.6 A, which is the typical with headroom for the SoC under
# stress, and it leaves the slot rail's 5 A to the three converters that share it, which the old reading did
# not: at 5 A for the module alone there was nothing left for the card socket, the NVMe or the switch core.
_SLOT_LOADS = lambda s: {
    "U3%dA" % (s - 1): 1.6,          # the Compute Module 5 on its receptacle: 0.9 A typical (Table 9) plus stress headroom
    "U%d03" % s: 2.2,                # buck S%dA -> the M.2 card socket's 3.3 V: the RM520N asks for 3.0 A continuous at 3.3 V (Quectel hardware design v1.1 section 3.3.1), which is 2.2 A here
    "U%d04" % s: 0.7,                # buck S%dB -> the NVMe socket and the PCIe switch's 3.3 V
    "U%d05" % s: 0.15,               # buck S%dC -> the PI7C9X2G404SL's 1.0 V core
    "J_FAN%d" % s: 0.1,              # the slot's IP68 cooler fan
}
for _n in (1, 2, 3):

# WHICH OF THIS BOARD'S RAILS CONVERT, AND WHAT THE CONVERSION COSTS (16 September 2026, rule THM-001). This is
# the kit's largest heat source: three compute modules, three PCIe switches, three hubs, a five-port Ethernet
# switch and the radios, in a sealed case with no vent anywhere (owner ruling 7 September). Nothing had ever
# put a watt figure on it. Every rail says here whether it converts, and no figure is inferred from anything.
#   NOT a conversion: the three slot rails and the device rail arrive from board A through JST-VH headers;
#   +5V_HDMI is behind a fuse; +54V_POE arrives on a header; the modules' own +3V3_CM and +1V8_CM come OUT of
#   the CM5 receptacles; and the five eFuses and load switches (U21, U22, U23, U24, U28) are pass elements
#   whose loss is I2R in one part, not a conversion. Their copper loss is dc_drop's business.
#   AP63203 and AP63205 synchronous bucks (U25 for +3V3_DEV, the twelve per-slot rails, +1V2_KSZ): 0.88 for a
#   3.3 V output and 0.85 for a 1.0 to 1.2 V one, because a buck's efficiency falls with its output voltage
#   and both are below anything those parts claim. Taken low on purpose: a lower efficiency is a higher loss.
#   AP2112K LDOs (U27's 2.5 V from 3.3, and the three controllers' private 3.3 V from the 5 V device rail):
#   a linear regulator's efficiency is arithmetic, Vout/Vin, so 2.5/3.3 = 0.76 and 3.3/5.0 = 0.66 exactly.
    # F-PR-05, 26 September 2026: slot 2's continuous current rises with its 5G module's 3.0 A at 3.3 V. power_path
    # adds up what the slot's three converters draw at their declared typical currents (3.05 A on slot 2, 2.21 of it
    # the card buck), and with the module's own 0.9 A (CM5 datasheet Table 9) and the fan's 0.1 A that is 4.05 A,
    # against the 2.5 A this line declared for every slot. The peak stays the source's 5.0 A (board A's AP64500).
    # Fix-up, 26 September 2026: whether the socket's two 220 uF carry the 5G burst so that +5V_S2 stays under that
    # 5.0 A is NOT computed here; the coincident worst case is open item I-03 on board A (drafts/r4-interfaces.md).
    # O-17, 26 September 2026 (fix-up pass 2): the card buck now sets 3.456 V, so its 3.0 A draws 2.31 A at 5.1 V
    # (3.0 x 3.456 / 0.88 / 5.1) and the three converters 3.16 A; with the module and the fan that is 4.16 A, so the
    # typical is 4.2 A. The coincident peak with the module at 4 A becomes 5.63 A (I-03).
    _intent.rail("+5V_S%d" % _n, 5.1, 4.2 if _n == 2 else 2.5, 5.0, "J_5V_S%d" % _n, loads=_SLOT_LOADS(_n), budget=0.02, share=0.015, converted=False,
                 always_on=True, always_on_why="it arrives from board A over the JST-VH lead; board A switches it and this board consumes it",
                 note="slot rail from A22 (JST-VH): the module, the two 3.3 V bucks, the 1.0 V switch core and the fan. "
                      "THIS BOARD'S SHARE is 1.5 of the rail's 2 percent (16 September 2026): board A regulates it and "
                      "measures 0.07 percent from its shunt to the header, and the long copper is this side, from the "
                      "VH header across the board to a module receptacle carrying 2.5 A")
_DEV_LOADS = {"U23": 1.2,            # eFuse -> +5V_LIME, the LimeSDR Mini 2.4 (the eFuse's ILM is 3.0 A)
              "U25": 0.90,           # the AP63203 buck -> +3V3_DEV, 1.4 A at 3.3 V through it
              "U21": 0.60,           # load switch -> +5V_LORA, the E22-900M30S at 1 W transmit
              "F1": 0.60,            # polyfuse -> PANEL_5V, board C's own 5 V rail (its intent declares 0.6 A)
              "U24": 0.45,           # eFuse -> +5V_RB, the RockBLOCK 9704 on a transmit burst
              "F3": 0.30,            # polyfuse -> VBUS_QMX, the HF unit in the lid tray
              "U28": 0.25,           # TPS2065 -> +5V_CAM
              "F2": 0.20,            # polyfuse -> +5V_HDMI, the two TS3DV642 display switches
              "U26": 0.15,           # TPS62933 -> the KSZ9897R's 1.2 V core
              "U106": 0.10, "U206": 0.10, "U306": 0.10,   # the three 1.1 V hub cores, always on: a bank outlives its module
              "U40": 0.05, "U50": 0.05, "U60": 0.05,      # the three controllers' private 3.3 V LDOs
              "U15": 0.02, "U16": 0.02, "U17": 0.02, "U18": 0.02}   # the four CP2102N bridges
_intent.rail("+5V_DEV", 5.0, 3.8, 6.0, "J_5V_DEV", loads=_DEV_LOADS, budget=0.02, share=0.015, converted=False,
             always_on=True, always_on_why="it arrives from board A over the JST-VH lead; board A switches it and this board consumes it",
             note="the device rail from A22; +0.8 A since the three hubs and their cores moved off the slot rails (ARCH-PCB-B-IOHA)")
# THE PEAK IS THE SOURCE PART'S RATING. This rail declared 5.0 A peak behind U25, an AP63203 whose rating is
# 2 A: a peak the source cannot deliver is not a peak, and the density verdict would have judged the copper
# against a current that can never flow in it. 2.0 A is what the part gives; the loads below sum to 1.38 A.
_3V3_LOADS = {"U1": 0.25,            # KSZ9897R seven-port switch, its 3.3 V I/O
              "U22": 0.25,           # load switch -> +3V3_ZB, the two E72 radios
              "U27": 0.15,           # AP2112K -> the switch's 2.5 V analog rail
              "U11": 0.05,           # LG290P GNSS
              "U5": 0.02,            # TPS23861 PoE controller
              "U6": 0.01, "U7": 0.01,            # the two PCA9555
              "U3": 0.01, "U4": 0.01,            # the two TS3DV642 display switches
              "U19": 0.01, "U20": 0.01, "U80": 0.01,   # the EMCON gates and the break-before-make XOR
              "U8": 0.005, "U9": 0.005, "U10": 0.005}  # the secure element, the holdover clock, the temperature sensor
for _n in (1, 2, 3):
    _3V3_LOADS["U%d02" % _n] = 0.10  # the TUSB8041 hub's VDD33: 99 mA on its sheet
    _3V3_LOADS["U%d09" % _n] = 0.05  # TMUXHS4212 SuperSpeed host select
    _3V3_LOADS["U%d10" % _n] = 0.01  # TS3USB221A USB2 host select
for _v in ("U70", "U71", "U72", "U73", "U74", "U75", "U76", "U77", "U78", "U79"): _3V3_LOADS[_v] = 0.01   # the voted logic
# The source is L1, the buck's inductor, not U25: the AP63203's pin 1 on this net is its feedback sense, and
# the current leaves through DEV_SW and the inductor. Naming the chip sends 1.4 A out of a sense pin.
# WHAT FEEDS EACH OF THESE (20 September 2026, appendix 32.246). The buck calls name their input
# explicitly: the A, B and C stages of each slot run from that slot's own 5 V rail and the D stage
# and the Ethernet switch core from the device rail, so `power_path` can add up what each feeder is
# asked for. Board A's VBAT declared 10 A while its nine converters drew 15.18, and nothing checked
# that on any board until tonight. The LDOs and load switches on this board are not declared yet:
# their inputs need reading off the schematic part by part and a wrong `fed_from` makes a wrong sum.
_intent.rail("+3V3_DEV", 3.3, 1.2, 2.0, "L1", loads=_3V3_LOADS, always_on=True, converted=True, efficiency=0.88,
             fed_from="+5V_DEV",
             always_on_why="U25 is an AP63203 whose EN pin is tied to its own input, so the shared logic rail follows the device rail: the hubs and bridges on it must outlive any one module",
             note="shared logic, the KSZ IO, the three hub VDD33 (99 mA each), the muxes, the three supervisor LDOs; U25 is a 2 A part and that is this rail's peak")
# THE GROUND HAS FOUR SOURCES AND THE DECLARATION SAID ONE. Holding only J_5V_S1 at 0 V would have returned
# all 21 A through one connector's ground pin and measured a board that does not exist; `source` takes a list
# since 13 September. The return is declared at each branch's own converter or connector rather than at the
# leaf parts behind it: a branch's parts sit beside the converter that feeds them and return into the same
# local ground copper, so this puts the current within a few millimetres of where it really enters the plane.
# THE RETURN IS NOT ALWAYS AT THE SAME PART AS THE SUPPLY, and the schematic generator refused this rail
# until it said so: `rail GND names load F1, which is not on that net`. F1, F2 and F3 are polyfuses, two-pin
# parts with no ground pin at all, and what they feed leaves the board. Their current returns where it comes
# back: F1 feeds PANEL_5V over the panel ribbon, so its return is at J_PANEL; F3 feeds the QMX unit over a
# lead, so its return is at J_QMX; F2 feeds +5V_HDMI, which is the two display switches U3 and U4, and those
# are on this board with ground pins of their own.
_GND_LOADS = {k: v for k, v in _DEV_LOADS.items() if k not in ("F1", "F2", "F3")}
_GND_LOADS["J_PANEL"] = _DEV_LOADS["F1"]
_GND_LOADS["J_QMX"] = _DEV_LOADS["F3"]
_GND_LOADS["U3"] = _GND_LOADS.get("U3", 0.0) + _DEV_LOADS["F2"] / 2
_GND_LOADS["U4"] = _GND_LOADS.get("U4", 0.0) + _DEV_LOADS["F2"] / 2
for _n in (1, 2, 3): _GND_LOADS.update(_SLOT_LOADS(_n))
# THE THIRTY RAILS THIS FILE DID NOT DECLARE (16 September 2026). Six rails were in the intent file and this
# board has thirty-six. The other thirty were invisible three ways at once: `signalnets` could not know they
# were rails, so the return-path gate judged each of them as a SIGNAL NET and measured its reference coverage,
# which says nothing about a power net; `dc_drop` never computed a drop or a current density for any of them;
# and `derate` could not compare a single part's rating against them. A rail that is not declared is not
# excluded, it is silently asked the wrong question and silently missed by the right one.
#
# THE SOURCE IS THE POWER PATH, NOT THE PART THAT CONTROLS IT: each buck names its INDUCTOR, and a part whose
# output pin really is a power pin (an LDO, an eFuse, a load switch, a polyfuse) says so with source_ic.
# The currents are design estimates of where the current goes, in the same form as the rails above.
for _s in (1, 2, 3):
    # F-PR-05, 26 September 2026: slot 2's socket carries the RM520N-GL, whose maker asks for "3.0 A at least"
    # continuous and "4 A at least" peak (HD v1.1 3.3.1); it was declared at 0.5 and 1.5 A, the AW7915's figures.
    # W5 TESTACCESS-B, the same day: the socket is fed through the Kelvin shunt R{s}65, so the buck side is this rail
    # and the socket side is +3V3_M2C{s}, a series segment of it.
    _ta, _pk = (3.0, 4.0) if _s == 2 else (0.5, 1.5)
    # O-17, 26 September 2026: slot 2's card buck is set to 3.456 V (R202 33.2 k, see slot()), inside the RM520N's
    # 3.135 to 4.4 V; the rail keeps its name and declares the voltage it is set to.
    _v2a = 3.456 if _s == 2 else 3.3
    _intent.rail("+3V3_S%dA" % _s, _v2a, _ta, _pk, "L%d01" % _s, switch="U%d03" % _s, converted=True, efficiency=0.88,
                 fed_from="+5V_S%d" % _s,
                 loads={"R%d65" % _s: _pk},
                 note=("slot %d's card-socket %s V from the AP64500 buck U%d03 through L%d01, out through the 5 mOhm "
                       "Kelvin shunt R%d65 to the socket: " % (_s, "3.456" if _s == 2 else "3.3", _s, _s, _s)) +
                      ("the Quectel RM520N-GL, 3.0 A continuous and 4 A peak (HD v1.1 3.3.1)" if _s == 2 else
                       "the AsiaRF AW7915-AED, 1.5 A"))
    _intent.rail("+3V3_M2C%d" % _s, _v2a, _ta, _pk, "R%d65" % _s, converted=False, series_of="+3V3_S%dA" % _s,
                 source_ic="R%d65 is the socket's Kelvin shunt: its pad on this net IS the power path" % _s,
                 loads={"J_M2C%d" % _s: _pk},
                 note="slot %d's card socket past its Kelvin shunt (W5 TESTACCESS-B, 26 September 2026): the same "
                      "current as +3V3_S%dA, a series segment of it" % (_s, _s))
    _intent.rail("+3V3_S%dB" % _s, 3.3, 0.9, 1.8, "L%d02" % _s, switch="U%d04" % _s, converted=True, efficiency=0.88,
                 fed_from="+5V_S%d" % _s,
                 loads={"J_M2N%d" % _s: 1.2, "U%d01" % _s: 0.55},
                 note="slot %d's NVMe socket and the PCIe switch's own 3.3 V from U%d04 through L%d02" % (_s, _s, _s))
    _intent.rail("+1V0_S%d" % _s, 1.0, 0.8, 1.2, "L%d03" % _s, switch="U%d05" % _s, converted=True, efficiency=0.85,
                 fed_from="+5V_S%d" % _s,
                 loads={"U%d01" % _s: 0.8},
                 note="slot %d's PCIe switch core from the AP63200 buck U%d05 through L%d03" % (_s, _s, _s))
    _intent.rail("+1V1_S%d" % _s, 1.1, 0.4, 0.7, "L%d04" % _s, always_on=True, converted=True, efficiency=0.85,
                 fed_from="+5V_DEV",
                 always_on_why="U%d06's EN pin is tied to the device rail on purpose: the hub core must outlive the module whose bank it serves, which is the whole point of the I/O high-availability layer" % _s,
                 loads={"U%d02" % _s: 0.4},
                 note="slot %d's USB hub core from U%d06 through L%d04, on the DEVICE rail and always on: the "
                      "bank outlives the module it is failing away from" % (_s, _s, _s))
    _intent.rail("+3V3_CM%d" % _s, 3.3, 0.10, 0.20, "U3%dA" % (_s - 1), always_on=True, converted=False,
                 always_on_why="the module's OWN 3.3 V output on its receptacle: this board consumes it and cannot switch it",
                 source_ic="the module GENERATES this rail and hands it out on its receptacle: the pin IS the source",
                 loads={"U3%dA" % (_s - 1): 0.10},
                 note="slot %d's module-supplied 3.3 V. This board only decouples it and level-shifts against "
                      "it; nothing on the carrier draws from it beyond its own bypass network" % _s)
    _intent.rail("+1V8_CM%d" % _s, 1.8, 0.02, 0.05, "U3%dA" % (_s - 1), always_on=True, converted=False,
                 always_on_why="the module's OWN 1.8 V output on its receptacle",
                 source_ic="the module GENERATES this rail and hands it out on its receptacle",
                 loads={"U3%dA" % (_s - 1): 0.02},
                 note="slot %d's module-supplied 1.8 V, a reference for its GPIO bank and nothing else here" % _s)
for _t, _u, _n in (("A", "U40", ("U41", "U42", "U43", "U44")), ("B", "U50", ("U51", "U52", "U53", "U54")),
                   ("C", "U60", ("U61", "U62", "U63", "U64"))):
    _intent.rail("+3V3_IOC%s" % _t, 3.3, 0.12, 0.25, _u, budget=0.03, always_on=True, converted=True, efficiency=0.66,
                 fed_from="+5V_DEV",   # U40/U50/U60 pins 1 and 3 are both /+5V_DEV in the netlist
                 always_on_why="each controller's private LDO has its EN pulled to its own input through 100 k, so it follows the device rail and the controller is up whenever the kit is; only the bench jumper J_IOCOFF_x holds it off, for IOHA A4 and A6 (26 September 2026)",
                 source_ic="%s is an AP2112K-3.3 LDO in SOT-23-5: pin 5 IS its output power pin" % _u,
                 loads=dict([(_n[0], 0.060), (_n[1], 0.020), (_n[2], 0.020), (_n[3], 0.020)]),
                 note="controller %s's private 3.3 V, its own branch off the device rail so that one "
                      "controller's fault cannot pull the other two down. Budget 3 percent: logic only" % _t)
_intent.rail("+1V2_KSZ", 1.2, 0.5, 0.8, "L2", always_on=True, converted=True, efficiency=0.85, fed_from="+5V_DEV",
             always_on_why="U26's EN pin is tied to the device rail it runs from, so the Ethernet switch core follows it",
             loads={"U1": 0.5},
             note="the Ethernet switch's core from the AP63200 buck U26 through L2")
_intent.rail("+2V5_KSZ", 2.5, 0.15, 0.25, "U27", budget=0.03, always_on=True, converted=True, efficiency=0.76,
             fed_from="+3V3_DEV",   # U27 pins 1 and 3 are both /+3V3_DEV in the netlist
             always_on_why="U27 is an AP2112K whose EN is tied to its own input: the switch's analogue rail comes up with the switch",
             source_ic="U27 is an AP2112K-2.5 LDO in SOT-23-5: pin 5 IS its output power pin",
             loads={"U1": 0.15},
             note="the Ethernet switch's analogue 2.5 V. Budget 3 percent: the switch's own range is wider")
_intent.rail("+3V3_ZB", 3.3, 0.10, 0.30, "U22", converted=False, fed_from="+3V3_DEV",  # U22 pin 6 IN
             source_ic="U22 is a TPS22810 load switch: its OUT pin IS the power path, which is what it is for",
             loads={"U13": 0.04, "U14": 0.04, "J_ZBDBG1": 0.01, "J_ZBDBG2": 0.01},
             note="the two CC2652P radios behind their load switch, plus the two bench debug headers. 0.3 A "
                  "peak is both radios transmitting at once, which the fabric never asks for but the copper must carry")
_intent.rail("+5V_LORA", 5.0, 0.15, 0.70, "U21", converted=False, fed_from="+5V_DEV",  # U21 pin 6 IN
             source_ic="U21 is a TPS22810 load switch: its OUT pin IS the power path",
             loads={"U12": 0.70},
             note="the 1 W LoRa module behind its load switch: 0.7 A on a transmit burst at 30 dBm, milliamps between")
_intent.rail("+5V_LIME", 5.0, 1.2, 3.0, "U23", converted=False, fed_from="+5V_DEV",  # U23 pin 4 IN
             source_ic="U23 is a TPS2596 eFuse: its OUT pin IS the power path, which is what an eFuse is",
             loads={"J_LIME": 3.0},
             note="the software-defined radio bay behind the eFuse U23 (ILM 301R, 3.0 A): a LimeSDR Mini 2.4 "
                  "on USB 3 draws about 1.2 A and peaks higher while its FPGA configures")
_intent.rail("+5V_RB", 5.0, 0.15, 2.00, "U24", converted=False, fed_from="+5V_DEV",  # U24 pin 4 IN
             source_ic="U24 is a TPS2596 eFuse: its OUT pin IS the power path",
             loads={"J_RB9704": 2.00},
             note="the satellite modem behind the eFuse U24 (ILM 301R, 3.0 A): the RockBLOCK 9704's burst "
                  "current on a transmit attempt is the number the copper has to carry, not its average")
_intent.rail("+5V_CAM", 5.0, 0.25, 0.50, "U28", converted=False, fed_from="+5V_DEV",  # U28 pin 5 IN
             source_ic="U28 is a TPS2065 switch: its OUT pin IS the power path",
             loads={"J_CAM": 0.50},
             note="the camera lead behind its switch, a USB 2.0 device at its port's own 500 mA limit")
_intent.rail("+5V_HDMI", 5.0, 0.10, 0.50, "F2", always_on=True, converted=False, fed_from="+5V_DEV",  # F2 pin 1
             always_on_why="a polyfuse is protection and not a switch: the connector's 5 V follows the device rail, which is what the standard asks a source to supply",
             source_ic="F2 is a polyfuse in series with the rail: the part IS the power path",
             loads={"J_HDMI": 0.50},
             note="the HDMI connector's own 5 V behind the 0.5 A polyfuse F2, which is what the standard asks a source to supply")
_intent.rail("+54V_POE", 54.0, 0.30, 0.60, "J_54V", budget=0.02, share=0.015, converted=False,
             always_on=True, always_on_why="it arrives from board A over the JST-VH lead; board A switches it and this board consumes it",
             loads={"U5": 0.60},
             note="the Power over Ethernet feed arriving from board A's own +54V_POE stage, into the TPS23861 "
                  "injector U5. It is a rail of board A and a load of this one")

_intent.rail("GND", 0.0, 10.0, 21.0, ["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV"], loads=_GND_LOADS, converted=False,
             always_on=True, always_on_why="the return, which nothing switches",
             note="the return of every rail: the three slot rails and the device rail, 19.4 A with all four at their declared peak")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers (as B13/B15)
LIBCACHE = {}

# ----------------------------------------------------------------- synthetic box symbols (parts with more pins than any library symbol): odd pins left, even pins right
CM5_PINS = {1:"GND",2:"GND",3:"Ethernet_Pair3_P",4:"Ethernet_Pair1_P",5:"Ethernet_Pair3_N",6:"Ethernet_Pair1_N",7:"GND",8:"GND",9:"Ethernet_Pair2_N",10:"Ethernet_Pair0_N",11:"Ethernet_Pair2_P",12:"Ethernet_Pair0_P",13:"GND",14:"GND",15:"Ethernet_nLED3",16:"Fan_Tacho",17:"Ethernet_nLED2",18:"Ethernet_SYNC_OUT",19:"Fan_PWM",20:"EEPROM_nWP",21:"LED_nACT",22:"GND",23:"GND",24:"GPIO26",25:"GPIO21",26:"GPIO19",27:"GPIO20",28:"GPIO13",29:"GPIO16",30:"GPIO6",31:"GPIO12",32:"GND",33:"GND",34:"GPIO5",35:"ID_SC",36:"ID_SD",37:"GPIO7",38:"GPIO11",39:"GPIO8",40:"GPIO9",41:"GPIO25",42:"GND",43:"GND",44:"GPIO10",45:"GPIO24",46:"GPIO22",47:"GPIO23",48:"GPIO27",49:"GPIO18",50:"GPIO17",51:"GPIO15",52:"GND",53:"GND",54:"GPIO4",55:"GPIO14",56:"GPIO3",57:"SD_CLK",58:"GPIO2",59:"GND",60:"GND",61:"SD_DAT3",62:"SD_CMD",63:"SD_DAT0",64:"SD_DAT5",65:"GND",66:"GND",67:"SD_DAT1",68:"SD_DAT4",69:"SD_DAT2",70:"SD_DAT7",71:"GND",72:"SD_DAT6",73:"SD_VDD_OVERRIDE",74:"GND",75:"SD_PWR_ON",76:"VBAT",77:"5V",78:"GPIO_VREF",79:"5V",80:"SCL0",81:"5V",82:"SDA0",83:"5V",84:"CM5_3.3V",85:"5V",86:"CM5_3.3V",87:"5V",88:"CM5_1.8V",89:"WL_nDisable",90:"CM5_1.8V",91:"BT_nDisable",92:"PWR_Button",93:"nRPIBOOT",94:"CC1",95:"LED_nPWR",96:"CC2",97:"CAM_GPIO0",98:"GND",99:"PMIC_Enable",100:"CAM_GPIO1",101:"USB_OTG_ID",102:"PCIe_CLK_nREQ",103:"USB_N",104:"PCIE_nWAKE",105:"USB_P",106:"PCIE_PWR_EN",107:"GND",108:"GND",109:"PCIe_nRST",110:"PCIe_CLK_P",111:"VBUS_EN",112:"PCIe_CLK_N",113:"GND",114:"GND",115:"MIPI0_D0_N",116:"PCIe_RX_P",117:"MIPI0_D0_P",118:"PCIe_RX_N",119:"GND",120:"GND",121:"MIPI0_D1_N",122:"PCIe_TX_P",123:"MIPI0_D1_P",124:"PCIe_TX_N",125:"GND",126:"GND",127:"MIPI0_C_N",128:"USB3-0-RX_N",129:"MIPI0_C_P",130:"USB3-0-RX_P",131:"GND",132:"GND",133:"MIPI0_D2_N",134:"USB3-0-DP",135:"MIPI0_D2_P",136:"USB3-0-DM",137:"GND",138:"GND",139:"MIPI0_D3_N",140:"USB3-0-TX_N",141:"MIPI0_D3_P",142:"USB3-0-TX_P",143:"HDMI1_HOTPLUG",144:"GND",145:"HDMI1_SDA",146:"HDMI1_TX2_P",147:"HDMI1_SCL",148:"HDMI1_TX2_N",149:"HDMI1_CEC",150:"GND",151:"HDMI0_CEC",152:"HDMI1_TX1_P",153:"HDMI0_HOTPLUG",154:"HDMI1_TX1_N",155:"GND",156:"GND",157:"USB3-1-RX_N",158:"HDMI1_TX0_P",159:"USB3-1-RX_P",160:"HDMI1_TX0_N",161:"GND",162:"GND",163:"USB3-1-DP",164:"HDMI1_CLK_P",165:"USB3-1-DM",166:"HDMI1_CLK_N",167:"GND",168:"GND",169:"USB3-1-TX_N",170:"HDMI0_TX2_P",171:"USB3-1-TX_P",172:"HDMI0_TX2_N",173:"GND",174:"GND",175:"MIPI1_D0_N",176:"HDMI0_TX1_P",177:"MIPI1_D0_P",178:"HDMI0_TX1_N",179:"GND",180:"GND",181:"MIPI1_D1_N",182:"HDMI0_TX0_P",183:"MIPI1_D1_P",184:"HDMI0_TX0_N",185:"GND",186:"GND",187:"MIPI1_C_N",188:"HDMI0_CLK_P",189:"MIPI1_C_P",190:"HDMI0_CLK_N",191:"GND",192:"GND",193:"MIPI1_D2_N",194:"MIPI1_D3_N",195:"MIPI1_D2_P",196:"MIPI1_D3_P",197:"GND",198:"GND",199:"HDMI0_SDA",200:"HDMI0_SCL"}
# Diodes PI7C9X2G404SL, 128-LQFP, DS40068 rev 5-2 section 4.1 (pin 129 = exposed pad)
PI7C = {1:'VDDR',2:'VSS',3:'VDDC',4:'VSS',5:'DWNRST_L1',6:'DWNRST_L2',7:'DWNRST_L3',8:'VDDR',9:'TEST1',10:'PERST_L',11:'VSS',12:'VSS',13:'VDDCAUX',14:'VDDCAUX',15:'VAUX',16:'TEST2',17:'TEST3',18:'VC1_EN',19:'PRSNT1',20:'PRSNT2',21:'PRSNT3',22:'TEST4',23:'VDDC',24:'RXPOLINV_DIS',25:'TEST5',26:'SMBCLK',27:'SMBDATA',28:'PWR_SAV',29:'VDDC',30:'VSS',31:'VDDC',32:'VSS',33:'SLOTCLK',34:'VSS',35:'GPIO1',36:'GPIO0',37:'GPIO2',38:'GPIO3',39:'GPIO4',40:'VDDC',41:'VSS',42:'GPIO5',43:'GPIO6',44:'GPIO7',45:'SLOT_IMP1',46:'SLOT_IMP2',47:'SLOT_IMP3',48:'NC',49:'VDDR',50:'VSS',51:'TEST6',52:'NC',53:'PL_512B',54:'NC',55:'VDDC',56:'VSS',57:'NC',58:'NC',59:'NC',60:'CLKBUF_PD',61:'VSS',62:'VDDC',63:'VSS',64:'VDDR',65:'VDDC',66:'VSS',67:'PORTSTATUS0',68:'PORTSTATUS1',69:'PORTSTATUS2',70:'EECLK',71:'EEPD',72:'SCAN_EN',73:'REFCLKI_N',74:'REFCLKI_P',75:'REFCLKO_N3',76:'REFCLKO_P3',77:'REFCLKO_N2',78:'REFCLKO_P2',79:'CVDDR',80:'REFCLKO_N1',81:'REFCLKO_P1',82:'CVDDR',83:'REFCLKO_N0',84:'CVDDR',85:'REFCLKO_P0',86:'IREF',87:'VSS',88:'TDO',89:'TCK',90:'VSS',91:'VDDC',92:'TMS',93:'TDI',94:'TRST_L',95:'VSS',96:'VDDR',97:'PERP1',98:'PERN1',99:'AVDD',100:'PETP1',101:'PETN1',102:'PERP2',103:'PERN2',104:'VSS',105:'AVDD',106:'PETP2',107:'PETN2',108:'AVDD',109:'CGND',110:'REFCLKP',111:'REFCLKN',112:'CGND',113:'AVDDH',114:'NC',115:'REXT_GND',116:'REXT',117:'PETN3',118:'PETP3',119:'AVDD',120:'VSS',121:'PERN3',122:'PERP3',123:'PETN0',124:'PETP0',125:'AVDD',126:'VSS',127:'PERN0',128:'PERP0',129:'E_PAD'}
# TI TUSB8041I, 64-QFN (RGC), SLLSEE4E pin functions (pin 65 = thermal pad)
TUSB = {1:"USB_DP_DN1",2:"USB_DM_DN1",3:"USB_SSTXP_DN1",4:"USB_SSTXM_DN1",5:"VDD",6:"USB_SSRXP_DN1",7:"USB_SSRXM_DN1",8:"VDD",9:"USB_DP_DN2",10:"USB_DM_DN2",11:"USB_SSTXP_DN2",12:"USB_SSTXM_DN2",13:"VDD",14:"USB_SSRXP_DN2",15:"USB_SSRXM_DN2",16:"VDD33",17:"USB_DP_DN3",18:"USB_DM_DN3",19:"USB_SSTXP_DN3",20:"USB_SSTXM_DN3",21:"VDD",22:"USB_SSRXP_DN3",23:"USB_SSRXM_DN3",24:"USB_DP_DN4",25:"USB_DM_DN4",26:"USB_SSTXP_DN4",27:"USB_SSTXM_DN4",28:"VDD",29:"USB_SSRXP_DN4",30:"USB_SSRXM_DN4",31:"VDD",32:"PWRCTL4",33:"PWRCTL3",34:"VDD33",35:"PWRCTL2",36:"PWRCTL1",37:"SDA",38:"SCL",39:"SMBUSz",40:"FULLPWRMGMTz",41:"PWRCTL_POL",42:"GANGED",43:"OVERCUR4z",44:"OVERCUR3z",45:"AUTOENz",46:"OVERCUR1z",47:"OVERCUR2z",48:"USB_VBUS",49:"TEST",50:"GRSTz",51:"VDD",52:"VDD33",53:"USB_DP_UP",54:"USB_DM_UP",55:"USB_SSTXP_UP",56:"USB_SSTXM_UP",57:"VDD",58:"USB_SSRXP_UP",59:"USB_SSRXM_UP",60:"NC",61:"XO",62:"XI",63:"VDD33",64:"USB_R1",65:"GND"}
# TI TS3DV642, 42-WQFN (pin 43 = pad); Microchip KSZ9897R 128-TQFP-EP (129 = pad)
TS3 = {1:"VCC",2:"EN",3:"SCL",4:"SDA",5:"D0P",6:"D0N",7:"D1P",8:"D1N",9:"NC",10:"D2P",11:"D2N",12:"D3P",13:"D3N",14:"HPD",15:"CEC",16:"SEL1",17:"SEL2",18:"CEC_A",19:"HPD_A",20:"CEC_B",21:"HPD_B",22:"D3N_B",23:"D3P_B",24:"D2N_B",25:"D2P_B",26:"D1N_B",27:"D1P_B",28:"D0N_B",29:"D0P_B",30:"NC",31:"D3N_A",32:"D3P_A",33:"D2N_A",34:"D2P_A",35:"D1N_A",36:"D1P_A",37:"D0N_A",38:"D0P_A",39:"SDA_B",40:"SCL_B",41:"SDA_A",42:"SCL_A",43:"GND"}
KSZ = {1:'TXRX1P_A',2:'TXRX1M_A',3:'AVDDL',4:'TXRX1P_B',5:'TXRX1M_B',6:'TXRX1P_C',7:'TXRX1M_C',8:'TXRX1P_D',9:'TXRX1M_D',10:'AVDDH',11:'DVDDL',12:'TXRX2P_A',13:'TXRX2M_A',14:'AVDDL',15:'TXRX2P_B',16:'TXRX2M_B',17:'TXRX2P_C',18:'TXRX2M_C',19:'AVDDL',20:'TXRX2P_D',21:'TXRX2M_D',22:'AVDDH',23:'DVDDL',24:'TXRX3P_A',25:'TXRX3M_A',26:'TXRX3P_B',27:'TXRX3M_B',28:'TXRX3P_C',29:'TXRX3M_C',30:'AVDDL',31:'TXRX3P_D',32:'TXRX3M_D',33:'AVDDH',34:'TXRX4P_A',35:'TXRX4M_A',36:'AVDDL',37:'TXRX4P_B',38:'TXRX4M_B',39:'TXRX4P_C',40:'TXRX4M_C',41:'AVDDL',42:'TXRX4P_D',43:'TXRX4M_D',44:'AVDDH',45:'DVDDL',46:'GND',47:'GND',48:'TX_CLK6',49:'TX_EN6',50:'TX_ER6',51:'COL6',52:'TXD6_3',53:'TXD6_2',54:'TXD6_1',55:'TXD6_0',56:'DVDDL',57:'RX_CLK6',58:'RX_DV6',59:'RX_ER6',60:'CRS6',61:'VDDIO',62:'RXD6_3',63:'RXD6_2',64:'RXD6_1',65:'RXD6_0',66:'TX_CLK7',67:'TX_EN7',68:'TX_ER7',69:'COL7',70:'TXD7_3',71:'TXD7_2',72:'TXD7_1',73:'TXD7_0',74:'DVDDL',75:'RX_CLK7',76:'RX_DV7',77:'VDDIO',78:'RX_ER7',79:'CRS7',80:'RXD7_3',81:'RXD7_2',82:'RXD7_1',83:'RXD7_0',84:'GND',85:'LED4_0',86:'LED4_1',87:'DVDDL',88:'LED3_0',89:'LED3_1',90:'NC',91:'LED2_0',92:'LED2_1',93:'PME_N',94:'INTRP_N',95:'CLKO_25_125',96:'RESET_N',97:'SDO',98:'SDI_SDA',99:'VDDIO',100:'SCS_N',101:'SCL_MDC',102:'LED5_0',103:'LED5_1',104:'DVDDL',105:'LED1_0',106:'LED1_1',107:'GND',108:'NC',109:'GND',110:'DVDDL',111:'AVDDH',112:'TXRX5P_A',113:'TXRX5M_A',114:'AVDDL',115:'TXRX5P_B',116:'TXRX5M_B',117:'TXRX5P_C',118:'TXRX5M_C',119:'AVDDL',120:'TXRX5P_D',121:'TXRX5M_D',122:'AVDDH',123:'GND',124:'AVDDL',125:'XO',126:'XI',127:'ISET',128:'AVDDH',129:'E_PAD'}
# Quectel LG290P (hardware design Table 6; 25-79 the ground matrix), Ebyte E22-900M30S (manual 3.3), Pulse H5007NL (HC500), TI TPS23861 TSSOP-28, Silicon Labs CP2102N QFN28
LG = {1:"RESERVED",2:"RESERVED",3:"1PPS",4:"EVENT",5:"RESERVED",6:"TXD2",7:"RXD2",8:"RESET_N",9:"VDD_RF",10:"GND",11:"RF_IN",12:"GND",13:"GND",14:"RTK_STAT_ANT_ON",15:"RXD3",16:"TXD3",17:"RESERVED",18:"I2C_SDA",19:"I2C_SCL",20:"TXD1",21:"RXD1",22:"V_BCKP",23:"VCC",24:"GND"}
LG.update({n: "GND" for n in range(25, 80)})
E22P = {1:"GND",2:"GND",3:"GND",4:"GND",5:"GND",6:"RXEN",7:"TXEN",8:"DIO2",9:"VCC",10:"VCC",11:"GND",12:"GND",13:"DIO1",14:"BUSY",15:"NRST",16:"MISO",17:"MOSI",18:"SCK",19:"NSS",20:"GND",21:"ANT",22:"GND"}
H5007 = {1:"TCT1",2:"TD1P",3:"TD1N",4:"TCT2",5:"TD2P",6:"TD2N",7:"TCT3",8:"TD3P",9:"TD3N",10:"TCT4",11:"TD4P",12:"TD4N",13:"MX4N",14:"MX4P",15:"MCT4",16:"MX3N",17:"MX3P",18:"MCT3",19:"MX2N",20:"MX2P",21:"MCT2",22:"MX1N",23:"MX1P",24:"MCT1"}
TPS23861 = {1:"VDD",2:"RESET",3:"SCL",4:"SDAI",5:"SDAO",6:"INT",7:"DGND",8:"SEN3",9:"DRAIN3",10:"GATE3",11:"KSENSB",12:"SEN4",13:"DRAIN4",14:"GATE4",15:"SEN1",16:"DRAIN1",17:"GATE1",18:"KSENSA",19:"SEN2",20:"DRAIN2",21:"GATE2",22:"AGND",23:"A3",24:"SHTDWN",25:"AIN",26:"AOUT",27:"NC",28:"VPWR"}
CP2102 = {1:"DCD",2:"RI_CLK",3:"GND",4:"D+",5:"D-",6:"VDD",7:"VREGIN",8:"VBUS",9:"RSTb",10:"NC",11:"SUSPENDb",12:"SUSPEND",13:"CHREN",14:"CHR1",15:"CHR0",16:"GPIO3",17:"GPIO2",18:"GPIO1",19:"GPIO0",20:"GPIO6",21:"GPIO5",22:"GPIO4",23:"CTS",24:"RTS",25:"RXD",26:"TXD",27:"DSR",28:"DTR",29:"GND"}
# TI TMUXHS4212, SLASEP7A rev May 2022, Table 5-1: two-channel differential 2:1 mux, port A is the common side and SEL
# low sends A to B, high sends A to C. OEn is active low, L = normal. RSVD1 and RSVD2 are tied to VCC. 20-pin VQFN.
TMUXHS = {1: "RSVD1", 2: "OEn", 3: "A0p", 4: "A0n", 5: "GND", 6: "VCC", 7: "A1p", 8: "A1n", 9: "SEL", 10: "RSVD2",
          11: "GND", 12: "C1n", 13: "C1p", 14: "C0n", 15: "C0p", 16: "B1n", 17: "B1p", 18: "B0n", 19: "B0p", 20: "GND",
          21: "EPAD"}
# TI TS3USB221A, SCDS277C rev Oct 2024, Table 4-1: USB 2.0 high-speed 1:2 mux, D+/D- is the common port, S selects
# port 1 or port 2, OE is active low. 10-pin uQFN. It exists because the TMUXHS4212 cannot carry USB2: its common-mode
# range is 0 to 1.8 V and its I/O absolute maximum is 2.4 V, against USB2's 3.3 V single-ended swing.
TS3USB = {1: "1Dp", 2: "1Dn", 3: "2Dp", 4: "2Dn", 5: "GND", 6: "OEn", 7: "Dn", 8: "Dp", 9: "S", 10: "VCC"}
# STM32H743VIT6, LQFP-100 14 x 14 mm 0.5 mm pitch (D-13, 26 September 2026: the part bought, JLCPCB C114409; owner
# ruling D-13 accepts it: software-verified boot on the supervisors is the prototype floor, so the H753's crypto and
# secure access mode are not required). The table was transcribed from KiCad's MCU_ST_STM32H7 STM32H753VITx symbol and
# is re-proven for BOTH parts by drafts/pin_parity.py against DS12110 Rev 10 Figure 5 (STM32H743) and DS12117 Rev 9
# Figure 4 (STM32H753): 100 of 100 pins agree on both (W6 found the same on 25 September). Alternate functions used,
# read in DS12110 Rev 10 Tables 11 and 13: FDCAN1 PD0/PD1 and FDCAN2 PB12/PB13 (AF9); I2C1 on PB6/PB7 (AF4, below).
H743 = {1: "PE2", 2: "PE3", 3: "PE4", 4: "PE5", 5: "PE6", 6: "VBAT", 7: "PC13", 8: "PC14", 9: "PC15", 10: "VSS", 11: "VDD", 12: "PH0", 13: "PH1", 14: "NRST", 15: "PC0", 16: "PC1", 17: "PC2_C", 18: "PC3_C", 19: "VSSA", 20: "VREF+", 21: "VDDA", 22: "PA0", 23: "PA1", 24: "PA2", 25: "PA3", 26: "VSS", 27: "VDD", 28: "PA4", 29: "PA5", 30: "PA6", 31: "PA7", 32: "PC4", 33: "PC5", 34: "PB0", 35: "PB1", 36: "PB2", 37: "PE7", 38: "PE8", 39: "PE9", 40: "PE10", 41: "PE11", 42: "PE12", 43: "PE13", 44: "PE14", 45: "PE15", 46: "PB10", 47: "PB11", 48: "VCAP", 49: "VSS", 50: "VDD", 51: "PB12", 52: "PB13", 53: "PB14", 54: "PB15", 55: "PD8", 56: "PD9", 57: "PD10", 58: "PD11", 59: "PD12", 60: "PD13", 61: "PD14", 62: "PD15", 63: "PC6", 64: "PC7", 65: "PC8", 66: "PC9", 67: "PA8", 68: "PA9", 69: "PA10", 70: "PA11", 71: "PA12", 72: "PA13", 73: "VCAP", 74: "VSS", 75: "VDD", 76: "PA14", 77: "PA15", 78: "PC10", 79: "PC11", 80: "PC12", 81: "PD0", 82: "PD1", 83: "PD2", 84: "PD3", 85: "PD4", 86: "PD5", 87: "PD6", 88: "PD7", 89: "PB3", 90: "PB4", 91: "PB5", 92: "PB6", 93: "PB7", 94: "BOOT0", 95: "PB8", 96: "PB9", 97: "PE0", 98: "PE1", 99: "VSS", 100: "VDD"}
SYNTH = {"CM5A": {k: v for k, v in CM5_PINS.items() if k <= 100}, "CM5B": {k: v for k, v in CM5_PINS.items() if k > 100},
         "PI7C9X2G404SL": PI7C, "TUSB8041": TUSB, "TS3DV642": TS3, "KSZ9897R": KSZ, "LG290P": LG, "E22_900M30S": E22P, "H5007NL": H5007, "TPS23861": TPS23861, "CP2102N": CP2102, "TMUXHS4212": TMUXHS, "TS3USB221A": TS3USB, "STM32H743VI": H743}

# ----------------------------------------------------------------- footprints
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "RS": "Resistor_SMD:R_1206_3216Metric", "R2512": "Resistor_SMD:R_2512_6332Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C100u": "Capacitor_SMD:C_1206_3216Metric", "C1210": "Capacitor_SMD:C_1210_3225Metric", "C1812": "Capacitor_SMD:C_1812_4532Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMB", "F1812": "Fuse:Fuse_1812_4532Metric",
 "QFN64": "Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm", "WQFN42": "Package_DFN_QFN:WQFN-42-1EP_3.5x9mm_P0.5mm_EP2.05x7.55mm", "QFN28": "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm",
 "LQFP100": "Package_QFP:LQFP-100_14x14mm_P0.5mm", "VQFN20": "meshsat:Texas_RKS0020A_VQFN-20_2.5x4.5mm", "UQFN10": "meshsat:Texas_RSE0010A_UQFN-10_1.5x2mm", "MLPD6": "meshsat:Skyworks_SKY13351_MLPD-6_1x1mm",
 "SOT353": "Package_TO_SOT_SMD:SOT-353_SC-70-5", "SOIC14": "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", "SOT23_8": "Package_TO_SOT_SMD:SOT-23-8",
 "LQFP128EP": "meshsat:LQFP-128_14x14mm_P0.4mm_EP6.0", "TQFP128EP": "meshsat:TQFP-128_14x14mm_P0.4mm_EP10.0",
 "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "TSSOP28": "Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm", "SOIC8": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
 "DDA8": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", "SO8EP": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", "PPAK": "Package_SO:PowerPAK_SO-8_Single",
 "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT23": "Package_TO_SOT_SMD:SOT-23", "TSOT6": "Package_TO_SOT_SMD:TSOT-23-6", "SOT583": "Package_TO_SOT_SMD:SOT-583-8",
 "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
 "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX", "L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX", "L0402": "Inductor_SMD:L_0402_1005Metric",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "VH4": "Connector_JST:JST_VH_B4P-VH_1x04_P3.96mm_Vertical",
 "SH4": "Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
 "IDC16": idc("2x08"), "IDC26": idc("2x13"), "IDC10": idc("2x05"),
 "PH1x2": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "PH1x2S": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left", "PH1x3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "PH1x4": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
 "PH1x5": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical", "PH1x5S": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical_SMD_Pin1Left", "PH1x5S": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical_SMD_Pin1Left", "PH2x5": "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical",
 "USBC": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "USB3A": "Connector_USB:USB3_A_Receptacle_Wuerth_692122030100", "HDMI": "Connector_Video:HDMI_A_Molex_208658-1001_Horizontal",
 "RJ45": "Connector_RJ:RJ45_Amphenol_RJHSE5380", "TP": "TestPoint:TestPoint_Pad_D1.5mm", "UFL": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", "CR2032": "Battery:BatteryHolder_Keystone_3034_1x20mm",
 "NANOSIM": "Connector_Card:nanoSIM_GCT_SIM8060-6-0-14-00",
 "CPT3528": "Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B",   # 26 September 2026 (F-PR-05): the RM520N's two 220 uF, KEMET T520B case B
 # B16 sites (gen_footprints_b16.py and the B13/B14 files in meshsat.pretty)
 "CM5A": "meshsat:CM5_Conn_A_10164227", "CM5B": "meshsat:CM5_Conn_B_10164227", "M2E": "meshsat:M2_E-Key_Socket_2230", "M2M": "meshsat:M2_M-Key_Socket_2242", "M2B": "meshsat:M2_B-Key_Socket_3052",
 "LG290P": "meshsat:Quectel_LG290P", "E22": "meshsat:Ebyte_E22-900M30S", "E72": "meshsat:Ebyte_E72-2G4M20S1E", "H5007": "meshsat:Pulse_H5007NL",
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
def efuse(uref, vin, vout, en, flt, refs, ilim):
    cd, rilm, rflt, rov1, rov2, cin = refs
    ic(uref, 9, "TPS259631DDAR eFuse %s -> %s (%s)" % (vin, vout, ilim), "DDA8", {"1": "GND", "2": uref + "_DVDT", "3": en, "4": vin, "5": vout, "6": flt, "7": uref + "_ILM", "8": uref + "_OVLO", "9": "GND"}, "C2155778")
    c(cd, "10n", uref + "_DVDT", "GND"); r(rilm, ilim, uref + "_ILM", "GND"); r(rflt, "10k", flt, "+3V3_DEV"); r(rov1, "100k 1%", vin, uref + "_OVLO"); r(rov2, "10k 1% (OVLO)", uref + "_OVLO", "GND"); c(cin, "100n", vin, "GND")
def buck33(uref, tag, vin, en, out, refs, rt_val="31.6k 1%", rt_lcsc="", rco_val="22k", rco_lcsc="", c6=None):
    """AP64500SP-13 5 A buck (A22 buck5 recipe) set to 3.32 V: 31.6k/10k on the 0.8 V reference, 3.3 uH XAL6060, meant
    for 500 kHz; but the 68k RT sets 1.47 MHz (DS41979 Rev 5-2 Eq. 7, RT[kOhm] = 100000 / fsw[kHz]), open item O-20.
    rt_val/rco_val/c6 (26 September 2026, O-17): a rail whose output capacitance differs from the recipe's 3 x 22 uF
    takes its own set point and compensation (DS41979 Eq. 6 and 17 to 19); c6 is (ref, value, lcsc) from COMP to GND."""
    L, cb, ci1, ci2, co1, co2, co3, rt, rb, rrt, rco, cco = refs
    ic(uref, 9, "AP64500SP-13 5 A buck, 3.3 V rail %s" % out, "SO8EP", {"1": tag + "_BOOT", "2": vin, "3": en, "4": tag + "_RT", "5": tag + "_FB", "6": tag + "_COMP", "7": "GND", "8": tag + "_SW", "9": "GND"}, "C2070920")
    # A SWITCHING NODE MUST BE DECLARED, AND THIS BOARD DECLARED NONE (20 September 2026, found by
    # `power_path` asking every board mechanically; appendix 32.237). It is not a rail and a drop budget in
    # percent means nothing on it, but CMP-001 asks what voltage a part on a net can see, and a buck's
    # switching node swings to its INPUT rail and a diode drop below ground on the other half of the cycle.
    # Fourteen of them on this board said nothing at all, where board A's five LM5176 stages have declared
    # theirs since 16 September. The input's own declared voltage is what it swings to, read from the intent
    # rather than typed, so the two cannot drift.
    _intent.node(tag + "_SW", _intent.net_volts(vin),
                 "the %s buck's switching node: it swings to %s, the rail that feeds it, and a diode drop "
                 "below ground on the other half of the cycle" % (out, vin), v_min=-1.0)
    part(L, "Device", "L", "3.3uH XAL6030-332ME", "L6060", {"1": tag + "_SW", "2": out}); c(cb, "100n", tag + "_BOOT", tag + "_SW")
    c(ci1, "22u 10V X7R 1210", vin, "GND", "C1210", bypass=(uref, "2")); c(ci2, "22u 10V X7R 1210", vin, "GND", "C1210", bypass=(uref, "2"))   # the buck's VIN pin
    for cr in (co1, co2, co3): c(cr, "22u 10V X7R 1210", out, "GND", "C1210")
    r(rt, rt_val, out, tag + "_FB", "R", rt_lcsc); r(rb, "10k 1%", tag + "_FB", "GND"); r(rrt, "68k (RT: 500 kHz)", tag + "_RT", "GND"); r(rco, rco_val, tag + "_COMP", tag + "_COMPC", "R", rco_lcsc); c(cco, "3.3n", tag + "_COMPC", "GND")
    if c6:
        c(c6[0], c6[1], tag + "_COMP", "GND", "C0402", c6[2])
        _intent.node(tag + "_COMP", _intent.net_volts(vin),
                     "the %s buck's COMP pin (its error amplifier's output), which carries C6 to ground: it cannot rise "
                     "above the IC's own supply %s (DS41979 Rev 5-2 absolute maximum 6.0 V), so it is declared at that "
                     "rail, read from the intent" % (out, vin))
def buck_small(uref, tag, vin, en, out, refs, rb_val, note):
    """TPS62933 3 A buck (SOT-583: 1 RT 2 EN 3 VIN 4 GND 5 SW 6 BST 7 SS/PG 8 FB; 0.8 V reference, RT floating = 500 kHz): 10k top, rb_val bottom."""
    L, ci, co1, co2, cb, css, rt, rb = refs
    ic(uref, 8, "TPS62933DRLR buck %s" % note, "SOT583", {"1": "NC", "2": en, "3": vin, "4": "GND", "5": tag + "_SW", "6": tag + "_BST", "7": tag + "_SS", "8": tag + "_FB"}, "C3200405")   # the code A22 already buys this part with
    # A SWITCHING NODE MUST BE DECLARED, AND THIS BOARD DECLARED NONE (20 September 2026, found by
    # `power_path` asking every board mechanically; appendix 32.237). It is not a rail and a drop budget in
    # percent means nothing on it, but CMP-001 asks what voltage a part on a net can see, and a buck's
    # switching node swings to its INPUT rail and a diode drop below ground on the other half of the cycle.
    # Fourteen of them on this board said nothing at all, where board A's five LM5176 stages have declared
    # theirs since 16 September. The input's own declared voltage is what it swings to, read from the intent
    # rather than typed, so the two cannot drift.
    _intent.node(tag + "_SW", _intent.net_volts(vin),
                 "the %s buck's switching node: it swings to %s, the rail that feeds it, and a diode drop "
                 "below ground on the other half of the cycle" % (out, vin), v_min=-1.0)
    part(L, "Device", "L", "2.2uH XAL4020-222ME", "L4020", {"1": tag + "_SW", "2": out}); c(ci, "10u", vin, "GND", "C10u", bypass=(uref, "3")); c(co1, "22u 6.3V", out, "GND", "C10u"); c(co2, "22u 6.3V", out, "GND", "C10u")
    c(cb, "100n", tag + "_BST", tag + "_SW"); c(css, "10n", tag + "_SS", "GND"); r(rt, "10k 1%", out, tag + "_FB"); r(rb, rb_val, tag + "_FB", "GND")
def cp2102(uref, tag, vusb, dp, dm, txd, rxd, rts="NC", dtr="NC", refs=()):
    """CP2102N-A02-GQFN28 bridge: bus sense and regulator input from the slot rail whose hub carries it, its own 3.3 V out (VDD) bypassed, RSTb pulled to VDD."""
    synth(uref, "CP2102N", "CP2102N-A02-GQFN28 USB-UART bridge (%s)" % tag, "QFN28", {3: "GND", 29: "GND", 4: dp, 5: dm, 6: tag + "_3V3", 7: vusb, 8: vusb, 9: tag + "_RST", 25: rxd, 26: txd, 24: rts, 28: dtr}, "C964632")
    rr, c1, c2 = refs
    r(rr, "1k", tag + "_RST", tag + "_3V3"); c(c1, "4.7u", tag + "_3V3", "GND", "C10u"); c(c2, "100n", tag + "_3V3", "GND")

# 26 September 2026 (round 4): parts that belong to a slot's column but whose reference is outside the slot's
# 100s block (its test pads and the 5G socket's power and SIM parts), so the schematic sections still group them.
SLOT_EXTRA = {1: set(), 2: set(), 3: set()}
def _TP(num, net, slot=None):
    """A test pad on `net` (the value is the net, as every other pad on this board)."""
    part("TP%d" % num, "Connector", "TestPoint", net, "TP", {"1": net})
    if slot: SLOT_EXTRA[slot].add("TP%d" % num)
# ================================================================= the three slot columns
GPIO_FIXED = {6: "PI_SHDN_REQ_CM%d", 7: "SPI%d_CE1", 8: "SPI%d_CE0", 9: "SPI%d_MISO", 10: "SPI%d_MOSI", 11: "SPI%d_SCLK", 14: "UART0_TX%d", 15: "UART0_RX%d", 16: "HB_CM%d", 17: "PI_KILL_CM%d",
              22: "GNSS_PPS_CM%d", 23: "SPI%d_IO23", 24: "SPI%d_IO24", 26: "SPI%d_IO26", 2: "SDA_CM%d", 3: "SCL_CM%d"}
HUB_PORT = {1: (1, 2, 3, 4, 6, 7), 2: (9, 10, 11, 12, 14, 15), 3: (17, 18, 19, 20, 22, 23), 4: (24, 25, 26, 27, 29, 30)}   # DP DM SSTXP SSTXM SSRXP SSRXM
def slot(s):
    n5 = "+5V_S%d" % s; cm33 = "+3V3_CM%d" % s; cm18 = "+1V8_CM%d" % s; a33 = "+3V3_S%dA" % s; b33 = "+3V3_S%dB" % s; v10 = "+1V0_S%d" % s; v11 = "+1V1_S%d" % s
    R = lambda k: "R%d" % (100 * s + k); C = lambda k: "C%d" % (100 * s + k); U = lambda k: "U%d" % (100 * s + k); Q = lambda k: "Q%d" % (100 * s + k); L = lambda k: "L%d" % (100 * s + k)
    # --- the module
    CM5 = {}
    for n, nm in CM5_PINS.items():
        if nm == "GND": CM5[n] = "GND"
        elif nm == "5V": CM5[n] = n5
        elif nm == "CM5_3.3V": CM5[n] = cm33
        elif nm == "CM5_1.8V": CM5[n] = cm18
        elif nm.startswith("GPIO") and nm[4:].isdigit():
            g = int(nm[4:]); CM5[n] = GPIO_FIXED[g] % s if g in GPIO_FIXED else "NC"
        else: CM5[n] = "NC"
    if s < 3:
        for g in (7, 8, 9, 10, 11, 23, 24, 26): CM5[{7: 37, 8: 39, 9: 40, 10: 44, 11: 38, 23: 47, 24: 45, 26: 24}[g]] = "NC"   # the SPI0 breakout exists on S3 only (the E22)
    CM5.update({54: "LORA_TXEN" if s == 3 else "NC", 34: "LORA_RXEN" if s == 3 else "NC",   # GPIO4, GPIO5: the E22's T/R switch lines on S3
                16: "FAN_TACHO%d" % s, 19: "FAN_PWM%d" % s, 20: "NC", 21: "LED_nACT%d" % s, 76: "VBAT", 78: cm33, 89: "WL_nDIS%d" % s, 91: "BT_nDIS%d" % s, 92: "NC",
                93: "nRPIBOOT%d" % s, 95: "LED_nPWR%d" % s, 99: "NC", 103: "USB_OTG_N%d" % s, 105: "USB_OTG_P%d" % s,
                3: "ETH%d_P3_P" % s, 5: "ETH%d_P3_N" % s, 4: "ETH%d_P1_P" % s, 6: "ETH%d_P1_N" % s, 9: "ETH%d_P2_N" % s, 11: "ETH%d_P2_P" % s, 10: "ETH%d_P0_N" % s, 12: "ETH%d_P0_P" % s,
                102: "PCIE%d_CLKREQ_n" % s, 104: "PCIE%d_nWAKE" % s, 106: "PCIE_PWR_EN%d" % s, 109: "PCIE%d_nRST" % s, 110: "PCIE%d_CLK_P" % s, 112: "PCIE%d_CLK_N" % s,
                116: "PCIE%d_RX_P" % s, 118: "PCIE%d_RX_N" % s, 122: "PCIE%d_TX_P" % s, 124: "PCIE%d_TX_N" % s,
                128: "HOST%d_0RX_N" % s, 130: "HOST%d_0RX_P" % s, 134: "HOST%d_0D_P" % s, 136: "HOST%d_0D_N" % s, 140: "HOST%d_0TX_N" % s, 142: "HOST%d_0TX_P" % s,
                157: "HOST%d_1RX_N" % s, 159: "HOST%d_1RX_P" % s, 163: "HOST%d_1D_P" % s, 165: "HOST%d_1D_N" % s, 169: "HOST%d_1TX_N" % s, 171: "HOST%d_1TX_P" % s,
                170: "HDMI%d_D2_P" % s, 172: "HDMI%d_D2_N" % s, 176: "HDMI%d_D1_P" % s, 178: "HDMI%d_D1_N" % s, 182: "HDMI%d_D0_P" % s, 184: "HDMI%d_D0_N" % s, 188: "HDMI%d_CK_P" % s, 190: "HDMI%d_CK_N" % s,
                151: "HDMI%d_CEC" % s, 153: "HDMI%d_HPD" % s, 199: "HDMI%d_SDA" % s, 200: "HDMI%d_SCL" % s})
    ra, rb = "U3%dA" % (s - 1), "U3%dB" % (s - 1)
    part(ra, "Connector_Generic", "CM5A", "Amphenol 10164227-1004A1RLF receptacle A, slot S%d (CM5 pins 1-100, GPIO side); module CM5108064 bench-fitted" % s, "CM5A", {str(k): v for k, v in CM5.items() if k <= 100}, "C7435219")
    part(rb, "Connector_Generic", "CM5B", "Amphenol 10164227-1004A1RLF receptacle B, slot S%d (CM5 pins 101-200, high-speed side)" % s, "CM5B", {str(k): v for k, v in CM5.items() if k > 100}, "C7435219")
    # --- the slot rail: J_5V_Sx from A22 (AP64500 5.1 V, 32.55), bulk at the lead and at the module's 5 V pins
    part("J_5V_S%d" % s, "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: 5 V slot rail S%d from A22 J_5V_S%d, 16 AWG lead: + -" % (s, s), "VH2", {"1": n5, "2": "GND"}, "C274411")
    # 16 September 2026, rule CMP-001: an SMBJ5.0A stands off 5.0 V and this rail is regulated to 5.1, so the
    # clamp sat above its own stand-off voltage in normal service and leaked there for ever (up to 800 uA a
    # part at VWM, three of them). The next standard stand-off up is the right part: SMBJ6.0A (Littelfuse
    # C83270, DO-214AA, stock 5,910) stands off 6.0 V and breaks down at 6.67 V minimum. Neither part
    # protects the module from a surge, whose clamping voltage is 9 to 10 V either way; what a stand-off
    # above the rail buys is that the protector is not a load on the rail it protects.
    part("D%d" % (100 * s + 1), "Device", "D_TVS", "SMBJ6.0A (6.0 V standoff on the 5.1 V slot rail)", "TVS", {"1": n5, "2": "GND"}, "C83270")
    for k in (1, 2, 3, 4): c(C(k), "100u 10V", n5, "GND", "C100u")
    for k in (5, 6, 7, 8): c(C(k), "10u", n5, "GND", "C10u")
    c(C(9), "10u", cm33, "GND", "C10u"); c(C(10), "100n", cm33, "GND")
    r(R(1), "1k", n5, "LED_5V_A%d" % s); led("LED%d1" % s, "green 5 V S%d" % s, "LED_5V_A%d" % s, "GND")
    _intent.node("LED_5V_A%d" % s, 5.0, "the slot %s indicator's anode, behind its 1k series resistor from "
                 "the 5 V rail: it can only reach that rail" % s)
    # --- 3.3 V bucks: A the card socket (PCIE_PWR_EN, as the B14 WiFi rail), B the switch, hub and NVMe (follows the module's 3.3 V); the two cores from TPS62933 on the 5 V rail
    # S-01 (owner ruling D-05, radios dark), 26 September 2026: on slots 1 and 3 the card socket carries an AW7915-AED
    # whose W_DISABLE1# effect no maker's document states, so its SUPPLY is what EMCON removes: the buck's enable
    # S{s}A_EN follows PCIE_PWR_EN through a 10 k series resistor R{s}64, and Q{s}11 (gate EMCON_ON, the board's one
    # inverted copy of EMCON_HW) pulls it to ground while EMCON is asserted; the module pin only ever sees 10 k and
    # R{s}06, never a driven voltage. Slot 2's 5G module keeps
    # PCIE_PWR_EN alone: Quectel documents W_DISABLE1# as airplane mode ("the RF function is invalid", HD v1.1
    # 3.1 and 3.1.2) and forbids cutting VCC before the module has turned off ("To avoid corrupting the data in the
    # internal flash, DO NOT cut off the power supply", 3.3.2), so its hardware RF disable is W_DISABLE1#, as wired.
    # O-17, 26 September 2026 (round-4 review, minor; taken in the fix-up under the owner's standing rule): SLOT 2'S CARD
    # BUCK GETS ITS OWN SET POINT AND COMPENSATION. The recipe's 22 k / 3.3 nF was sized for 3 x 22 uF, and F-PR-05
    # put two 220 uF polymer capacitors on this rail. AP64500 DS41979 Rev 5-2 Eq. 17, R5 = 4.67e3 x fc x VOUT x COUT
    # (gm 0.15 mS, RT 0.089 V/A): with COUT about 0.50 mF (3 x 22 uF X7R at its bias, the socket's 22 uF, 2 x 220 uF)
    # the old 22 k crosses over at about 2.8 kHz, a mid-band output impedance 1/(2 pi fc COUT) of about 0.11 Ohm, so a
    # 3 A burst step would sag about 0.34 V. R205 = 120 k puts fc at 14.7 kHz (12 to 18 kHz over COUT 0.41 to
    # 0.62 mF; DS41979's own example is 15 kHz, below fsw/10), about 21 mOhm. C5 = VOUT x COUT / (IOUT x R5) (Eq. 18) =
    # 3.6 nF at 4 A, so C217 stays 3.3 nF (zero 402 Hz on the 365 Hz load pole). C6 = max(RC x COUT / R5,
    # 1 / (pi x fsw x R5)) (Eq. 19): the first term, RC 12.5 to 20 mOhm (two 25 mOhm polymers, the shunt and copper), is
    # 52 to 84 pF and the second 1.8 pF, so C298 = 68 pF, a pole at 19.5 kHz on the ESR zero. FREQUENCY (fix-up pass 3,
    # the re-review's minor): the recipe's RT, 68 k, sets fsw = 100000 / 68 = 1.47 MHz (DS41979 Eq. 7), not the 500 kHz
    # its label says (500 kHz is RT = 200 k in the electrical table). fc is far below fsw/10 at either frequency and
    # the second term is 5.3 pF at 500 kHz, so these values hold at both; the frequency itself is open item O-20 on
    # boards A and B. SET POINT: R202 = 33.2 k gives 0.8 x 4.32 = 3.456 V, worst case 3.369 to 3.545 V (VFB 792 to 808 mV,
    # 1 percent resistors), inside the RM520N's 3.135 to 4.4 V (HD v1.1 3.3.1, nominal 3.7 V) and at nominal inside
    # the M.2 3.3 V + 5 percent. A 4 A step from idle at the worst set point: 3.369 V - 20 mV shunt - 50 mV ESR step -
    # 86 mV loop sag = 3.213 V, 78 mV above the module's minimum for the copper.
    _s2a = dict(rt_val="33.2k 1%", rt_lcsc="C23003", rco_val="120k 1%", rco_lcsc="C25808", c6=(C(98), "68p 50V C0G", "C107009")) if s == 2 else {}
    buck33(U(3), "S%dA" % s, n5, ("S%dA_EN" % s) if s != 2 else ("PCIE_PWR_EN%d" % s), a33, [L(1), C(11), C(12), C(13), C(14), C(15), C(16), R(2), R(3), R(4), R(5), C(17)], **_s2a); r(R(6), "100k", "PCIE_PWR_EN%d" % s, "GND")
    if s != 2:
        r(R(64), "10k", "PCIE_PWR_EN%d" % s, "S%dA_EN" % s)   # the AP64500's EN sources 1.5 uA: 15 mV across this, and R{s}06 holds both low with the module off
        nfet(Q(11), "EMCON_ON", "GND", "S%dA_EN" % s, "2N7002: EMCON removes the WiFi card's supply (S-01)")
    buck33(U(4), "S%dB" % s, n5, "EN33_S%d" % s, b33, [L(2), C(18), C(19), C(20), C(21), C(22), C(23), R(7), R(8), R(9), R(10), C(24)])
    r(R(11), "100k", cm33, "EN33_S%d" % s); r(R(12), "100k", "EN33_S%d" % s, "GND")   # 1.65 V when the module's 3.3 V is up
    buck_small(U(5), "S%dC" % s, n5, "EN33_S%d" % s, v10, [L(3), C(25), C(26), C(27), C(28), C(29), R(13), R(14)], "40.2k 1%", "1.0 V PCIe switch core S%d" % s)
    buck_small(U(6), "S%dD" % s, "+5V_DEV", "+5V_DEV", v11, [L(4), C(30), C(31), C(32), C(33), C(34), R(15), R(16)], "26.7k 1%", "1.1 V hub core S%d (on the device rail and always on: the bank outlives its module)" % s)
    # --- PCIe switch PI7C9X2G404SL: upstream port 0 to the module, port 1 the NVMe socket, port 2 the card socket, port 3 unused; the integrated clock buffer fans the module's 100 MHz to the switch core and both sockets
    m = {}
    for n, nm in PI7C.items():
        if nm in ("VDDR", "CVDDR", "VAUX", "AVDDH"): m[n] = b33
        elif nm in ("VDDC", "VDDCAUX", "AVDD"): m[n] = v10
        elif nm in ("VSS", "CGND", "E_PAD", "REXT_GND"): m[n] = "GND"
        else: m[n] = "NC"
    # PINS 123/124 ARE THE SWITCH'S TRANSMIT (PETN0/PETP0) AND THEY DRIVE THE MODULE'S RECEIVE, which needs a
    # series AC coupling capacitor that this design did not have. Raspberry Pi, Compute Module 5 datasheet,
    # section 2.3: "CM5 includes on-board AC coupling capacitors for the PCIe_TX signals. However, external AC
    # coupling capacitors are required for PCIe_RX signals, close to the driving source (the peripheral's TX)",
    # and 2.3.1: "Ensure each receive (PCIe-Rx) line has an AC coupling capacitor (220 nF) before it enters the
    # IC" (v2/vendor/cm5/cm5-datasheet.pdf). The TX and RX pairs ARE correctly swapped for a direct IC
    # connection, which the same clause requires; only the capacitors were missing. Found 16 September 2026 by
    # reading the host vendor's own document under rule INT-001, on a board that had passed every gate.
    # W3-F01, 26 September 2026: THE DOWNSTREAM LINKS ARE NAMED FROM THE DEVICE'S SIDE AND EACH SWITCH TRANSMITTER
    # GETS ITS 220 nF. The switch's PETP1/PETN1 (100/101) and PETP2/PETN2 (106/107) are type O "transmit" and
    # PERP1/PERN1 (97/98) and PERP2/PERN2 (102/103) type I "receive" (DS40068 Rev 5-2 section 3.1). A socket's pins
    # are named from the HOST'S side (CM5 datasheet 2.3.1: "the signals are labelled from the host's point of view";
    # KiCad's own M.2 symbols: PETp0/PETn0 at 49/47 on keys M and B and at 35/37 on key E, PERp0/PERn0 at 43/41 and
    # 41/43). So the switch's transmitter goes through a series capacitor to the socket's PETp0/PETn0 and the
    # socket's PERp0/PERn0 come straight back to the switch's receiver. The capacitor sits at the transmitter, as
    # the upstream pair already does: Quectel RM520N series HD v1.1 section 4.3.3 puts 220 nF on the host's TX
    # "close to the host" and says the module's own TX capacitors are inside the module; the CM5 datasheet 2.3 says
    # PCIe and NVMe cards carry their own TX capacitors. Net names: *_RX_SW_* is the switch side of the capacitor,
    # *_RX_* the socket side (what the device receives), *_TX_* what the device transmits.
    # W3-F03, 26 September 2026: REFCLKP/REFCLKN (110/111) "must be delivered to the clock buffer cell through an
    # AC-coupled interface ... It is recommended that a 0.1uF be used" (DS40068 section 3.1; Table 8-2 note 4, the
    # PHY rebuilds its own common mode), so REFCLKO0 (85/83) reaches them through two 100 nF, C{s}95 and C{s}96 below.
    # W3-F03 fix-up, 26 September 2026 (round-4 review, blocking): the three used REFCLKO pairs are TERMINATED at the
    # source. They are "external differential HCSL clock outputs" whose current is set by IREF ("External resistor (475
    # Ohm +/- 1%) connection to set the differential reference clock output current", DS40068 Rev 5-2 section 3.1), and
    # a current-mode output only develops its swing across a resistor to ground; Table 8-1 note 1 gives the load its
    # numbers are measured into: "Test configuration is Rs=33.2 Ohm, Rp=49.9 Ohm, and 2pF". Without Rp, REFCLKO0 had no
    # DC path at all behind C{s}95/C{s}96, so the PHY had no clock and no link in any bank could train. So each pin now
    # carries *_SRC_x to a 33.2 Ohm series resistor, and the line after it (PCIE{s}_RCLK0_x, NVME{s}_CLK_x,
    # CARD{s}_CLK_x, the names the long runs already had) carries 49.9 Ohm to ground, both at the switch.
    m.update({5: "PCIE%d_RST1_n" % s, 6: "PCIE%d_RST2_n" % s, 10: "PCIE%d_nRST" % s, 123: "PCIE%d_RXSW_N" % s, 124: "PCIE%d_RXSW_P" % s, 127: "PCIE%d_TX_N" % s, 128: "PCIE%d_TX_P" % s,
              100: "NVME%d_RX_SW_P" % s, 101: "NVME%d_RX_SW_N" % s, 97: "NVME%d_TX_P" % s, 98: "NVME%d_TX_N" % s, 106: "CARD%d_RX_SW_P" % s, 107: "CARD%d_RX_SW_N" % s, 102: "CARD%d_TX_P" % s, 103: "CARD%d_TX_N" % s,
              73: "PCIE%d_CLK_N" % s, 74: "PCIE%d_CLK_P" % s, 83: "PCIE%d_RCLK0_SRC_N" % s, 85: "PCIE%d_RCLK0_SRC_P" % s, 110: "PCIE%d_RCLKIN_P" % s, 111: "PCIE%d_RCLKIN_N" % s,
              80: "NVME%d_CLK_SRC_N" % s, 81: "NVME%d_CLK_SRC_P" % s, 77: "CARD%d_CLK_SRC_N" % s, 78: "CARD%d_CLK_SRC_P" % s,
              86: "S%d_IREF" % s, 116: "S%d_REXT" % s, 33: "S%d_SLOTCLK" % s, 45: "S%d_SLOTIMP" % s, 46: "S%d_SLOTIMP" % s, 19: "GND", 20: "GND", 21: "S%d_PRSNT3" % s, 28: "S%d_PWRSAV" % s,
              9: "S%d_TEST1" % s, 16: "S%d_TESTL" % s, 17: "S%d_TESTL" % s, 22: "S%d_TESTL" % s, 25: "S%d_TESTL" % s, 51: "S%d_TESTL" % s, 18: "S%d_TESTL" % s, 26: "S%d_SMBCLK" % s, 27: "S%d_SMBDAT" % s,
              71: "S%d_EEPD" % s, 89: "S%d_JTAGL" % s, 92: "S%d_JTAGL" % s, 93: "S%d_JTAGL" % s, 94: "S%d_JTAGL" % s, 67: "S%d_PST0" % s, 68: "S%d_PST1" % s})
    synth(U(1), "PI7C9X2G404SL", "Diodes PI7C9X2G404SL PCIe 2.0 switch, slot S%d: up = CM5 lane, port 1 NVMe, port 2 card socket" % s, "LQFP128EP", m, "C500767")
    c(C(51), "220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)", "PCIE%d_RXSW_P" % s, "PCIE%d_RX_P" % s, "C0402")
    c(C(52), "220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)", "PCIE%d_RXSW_N" % s, "PCIE%d_RX_N" % s, "C0402")
    # The six coupling capacitors sit between two PCIe receive lanes and nothing declared what either side
    # carries, so `derate.py` reported twelve of this board's nets as UNDECLARED (16 September 2026, CMP-001).
    # A PCIe Gen 2 receiver pair is a differential signal of about 1.2 V peak to peak on a common mode below
    # 3.6 V; the capacitors are 16 V parts, which is the class the switch vendor's own reference uses.
    for _pn in ("PCIE%d_RXSW_P" % s, "PCIE%d_RXSW_N" % s, "PCIE%d_RX_P" % s, "PCIE%d_RX_N" % s):
        _intent.node(_pn, 3.6, "a PCIe receive lane: about 1.2 V peak to peak of differential signal on a "
                     "common mode the specification holds below 3.6 V, which is what an AC coupling "
                     "capacitor on it has to stand off")
    # W3-F01, 26 September 2026: the two downstream transmit pairs, each through its own 220 nF at the switch.
    for _k, _dev in ((53, "NVME"), (55, "CARD")):
        c(C(_k), "220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)", "%s%d_RX_SW_P" % (_dev, s), "%s%d_RX_P" % (_dev, s), "C0402")
        c(C(_k + 1), "220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)", "%s%d_RX_SW_N" % (_dev, s), "%s%d_RX_N" % (_dev, s), "C0402")
        for _pn in ("%s%d_RX_SW_P" % (_dev, s), "%s%d_RX_SW_N" % (_dev, s), "%s%d_RX_P" % (_dev, s), "%s%d_RX_N" % (_dev, s)):
            _intent.node(_pn, 3.6, "a PCIe downstream transmit lane of the switch (W3-F01): a differential signal on a "
                         "common mode below 3.6 V, which is what its AC coupling capacitor has to stand off")
    # W3-F03, 26 September 2026: the reference clock's own AC coupling, REFCLKO0 to REFCLKP/N.
    c(C(95), "100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)", "PCIE%d_RCLK0_P" % s, "PCIE%d_RCLKIN_P" % s, "C0402")
    c(C(96), "100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)", "PCIE%d_RCLK0_N" % s, "PCIE%d_RCLKIN_N" % s, "C0402")
    for _pn in ("PCIE%d_RCLK0_P" % s, "PCIE%d_RCLK0_N" % s, "PCIE%d_RCLKIN_P" % s, "PCIE%d_RCLKIN_N" % s):
        _intent.node(_pn, 3.6, "the switch's 100 MHz HCSL reference clock (W3-F03): at most 1.15 V high per DS40068 "
                     "Table 8-1, declared at the 3.6 V ceiling of the switch's own I/O supply as the worst case")
    # W3-F03 fix-up, 26 September 2026: the HCSL source termination of Table 8-1 note 1 on REFCLKO0 (to the switch's
    # own REFCLKP/N), REFCLKO1 (the NVMe socket) and REFCLKO2 (the card socket); REFCLKO3 (75/76) stays unused and
    # open. Rs in series at the pin, Rp from the line side of Rs to ground, both placed at the switch (O-02 seats).
    # Parts: UNI-ROYAL 0603WAF332JT5E (33.2 Ohm 1%, 1/10 W, -55 to +155 C, JLCPCB C23004) and 0603WAF499JT5E
    # (49.9 Ohm 1%, JLCPCB C23185, a basic part); the series datasheet decodes "332J" and "499J" as 33.2 and 49.9 Ohm
    # (UNI-ROYAL thick film chip resistor datasheet, 2.4.3, drafts/datasheets). Worst case from Table 8-1's VHIGH of
    # at most 1.15 V held continuously: 23 mA, so 26.5 mW in Rp and 17.6 mW in Rs, against 100 mW each.
    for _k, (_src, _line) in enumerate((("PCIE%d_RCLK0_SRC" % s, "PCIE%d_RCLK0" % s), ("NVME%d_CLK_SRC" % s, "NVME%d_CLK" % s),
                                        ("CARD%d_CLK_SRC" % s, "CARD%d_CLK" % s))):
        for _j, _h in enumerate(("P", "N")):
            r(R(75 + 4 * _k + _j), "33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)", "%s_%s" % (_src, _h), "%s_%s" % (_line, _h), "R", "C23004")
            r(R(77 + 4 * _k + _j), "49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03)", "%s_%s" % (_line, _h), "GND", "R", "C23185")
            for _pn in ("%s_%s" % (_src, _h),) + ((("%s_%s" % (_line, _h)),) if _k else ()):
                _intent.node(_pn, 3.6, "a 100 MHz HCSL reference clock output of the switch into its Table 8-1 load "
                             "(33.2 Ohm series, 49.9 Ohm to ground): at most 1.15 V high per DS40068 Table 8-1, "
                             "declared at the 3.6 V ceiling of the switch's own I/O supply as the worst case (W3-F03)")
    r(R(17), "475 1% (IREF)", "S%d_IREF" % s, "GND"); r(R(18), "1.43k 1% (REXT)", "S%d_REXT" % s, "GND"); r(R(19), "5.1k", "S%d_SLOTCLK" % s, b33); r(R(20), "5.1k", "S%d_SLOTIMP" % s, b33)
    r(R(21), "5.1k", "S%d_PRSNT3" % s, b33); r(R(22), "330", "S%d_PWRSAV" % s, "GND"); r(R(23), "5.1k", "S%d_TEST1" % s, b33); r(R(24), "330", "S%d_TESTL" % s, "GND"); r(R(25), "5.1k", "S%d_SMBCLK" % s, b33)
    r(R(26), "5.1k", "S%d_SMBDAT" % s, b33); r(R(27), "4.7k", "S%d_EEPD" % s, "GND"); r(R(28), "330", "S%d_JTAGL" % s, "GND"); r(R(29), "1k", "PCIE%d_CLKREQ_n" % s, "GND")   # the switch cannot forward CLKREQ: the module's clock is always requested
    r(R(30), "1k", b33, "LED_PST0_A%d" % s); led("LED%d2" % s, "green NVMe link (PORTSTATUS0)", "LED_PST0_A%d" % s, "S%d_PST0" % s)
    r(R(31), "1k", b33, "LED_PST1_A%d" % s); led("LED%d3" % s, "green card link (PORTSTATUS1)", "LED_PST1_A%d" % s, "S%d_PST1" % s)
    r(R(32), "10k", "PCIE%d_nWAKE" % s, b33); r(R(33), "10k", "NVME%d_CLKREQ_n" % s, b33); r(R(34), "10k", "CARD%d_CLKREQ_n" % s, a33)
    for k in range(35, 41): c(C(k), "100n", b33, "GND")
    for k in range(41, 47): c(C(k), "100n", v10, "GND")
    c(C(47), "10u", b33, "GND", "C10u"); c(C(48), "10u", v10, "GND", "C10u")
    # --- NVMe socket (M.2 M-key 2242, Amphenol MDT420M02001) on switch port 1; the card sockets below on port 2
    # The land's three mechanical pads, none of which the library symbol carries a pin for: S1 and S2 are the
    # socket's retention tabs and M1 the plated M2.5 standoff hole. Declared NC (17 September 2026, found by judging
    # every map against its land); tying the standoff to ground is the M.2 convention and is an item for the phase
    # that draws the socket through a symbol carrying the pad.
    _M2_MECH = {"M1": "NC", "S1": "NC", "S2": "NC"}
    M = {n: "NC" for n in range(1, 76) if not 59 <= n <= 66}
    M.update({n: b33 for n in (2, 4, 12, 14, 16, 18, 70, 72, 74)}); M.update({n: "GND" for n in (1, 3, 9, 15, 21, 27, 33, 39, 45, 51, 57, 71, 73, 75)})
    # W3-F01, 26 September 2026: 47/49 are PETn0/PETp0 (the host's transmit, the drive's receive) and 41/43 PERn0/PERp0
    # (the drive's transmit); they were the other way round, transmitter to transmitter, and no link could train.
    M.update({41: "NVME%d_TX_N" % s, 43: "NVME%d_TX_P" % s, 47: "NVME%d_RX_N" % s, 49: "NVME%d_RX_P" % s, 53: "NVME%d_CLK_N" % s, 55: "NVME%d_CLK_P" % s, 50: "PCIE%d_RST1_n" % s, 52: "NVME%d_CLKREQ_n" % s,
              54: "PCIE%d_nWAKE" % s, 38: "NVME%d_DEVSLP" % s, 10: "NVME%d_nLED" % s})
    part("J_M2N%d" % s, "Connector", "Bus_M.2_Socket_M", "M.2 M-key 2242 socket, Amphenol MDT420M02001, M2.5 standoff: NVMe drive of slot S%d (k3s replicated storage)" % s, "M2M", dict(M, **_M2_MECH), "C2927698")
    r(R(35), "10k", "NVME%d_DEVSLP" % s, "GND"); r(R(36), "1k", b33, "LED_NV_A%d" % s); led("LED%d4" % s, "amber NVMe activity", "LED_NV_A%d" % s, "NVME%d_nLED" % s)
    c(C(49), "22u 6.3V", b33, "GND", "C10u"); c(C(50), "100n", b33, "GND")
    # W5 TESTACCESS-B, 26 September 2026: the card socket's current is measured. A 5 mOhm Kelvin shunt R_65 (the
    # LR2512D-3W-5mR-1% board A already buys, C500739) sits between the buck's output capacitors and the socket, so
    # +3V3_S{s}A is the buck side (its feedback divider senses there) and +3V3_M2C{s} the socket side. TP_02 and
    # TP_03 are the two Kelvin pads, TP_01 the slot column's ground pad. At the 5G module's 4 A peak the shunt drops
    # 20 mV (Quectel HD v1.1 3.3.1: 3.135 V minimum at the module); slot 2's budget with it is in the O-17 note above.
    m2c = "+3V3_M2C%d" % s
    r(R(65), "5mOhm 1% 2512 (Kelvin shunt: card socket current, W5 TESTACCESS-B)", a33, m2c, "R2512", "C500739")
    _TP(100 * s + 1, "GND", s); _TP(100 * s + 2, a33, s); _TP(100 * s + 3, m2c, s)
    # EMCON REACHES W_DISABLE1# THROUGH AN OPEN DRAIN FROM EMCON_ON, NEVER THROUGH A STAGE ON EMCON_HW (MESHSAT-1357 round 4,
    # fix-up pass 3, 26 September 2026, the round-5 re-review's blocking item; taken by the session under the owner's
    # standing rule of 26 September 2026). From B14 on, each card's W_DISABLE1# came from a bidirectional 2N7002 stage:
    # gate on the card rail a33, source on W_DISABLE1# with R{s}37 10 k up to a33, drain on EMCON_HW. The body diode of
    # an N-channel MOSFET has its anode at the source (CJ 2N7002 datasheet, VSD 0.55 to 1.2 V at 115 mA). So whenever a
    # card rail was up and EMCON_HW was held only by its pull-downs (panel ribbon out, or board C's buffer U9 unpowered),
    # each stage sourced current into the line: up to 0.35 mA into a line held at 0 V (3.456 V / 10 k), and about 50 uA
    # against the 50 k that held it ((3.456 - 0.5) V / 60 k), which lifted it to about 2.3 to 2.5 V. That is a HIGH (SN74LVC08A VIH
    # 2.0 V, SCAS283W 5.4) at U19, U20, Q11 and board A's U26, so "EMCON released" with no panel. Slot 2's card rail is
    # not EMCON-gated and comes up with its module, so the 5G rail alone was enough to do it.
    # Now Q{s}06 is an open drain: gate EMCON_ON (high = EMCON asserted, Q11 and R513 below), source GND, drain on
    # W_DISABLE1#, R{s}37 kept to the card rail. EMCON asserted: Q{s}06 on and W_DISABLE1# low (on slots 1 and 3 the card's
    # supply is off as well, Q{s}11). EMCON released: Q{s}06 off and R{s}37 holds the pin at the card rail. No resistor,
    # channel or body diode joins a card rail to EMCON_HW any more, and check_pcb_b.py asserts it. The cost:
    # W_DISABLE1# now depends on +3V3_DEV (R513), as the module kill gates already do, which is open item O-14's class.
    if s == 1:   # WiFi link card AW7915-AED on an E-key 2230 (B14 wiring); W_DISABLE1# pulled low by EMCON_ON through the open drain Q106
        E = {n: "NC" for n in list(range(1, 24)) + list(range(32, 76))}
        E.update({n: "GND" for n in (1, 7, 18, 33, 39, 45, 51, 57, 63, 69, 75)}); E.update({n: m2c for n in (2, 4, 72, 74)})
        # W3-F01, 26 September 2026: E-key 35/37 are PETp0/PETn0 (the host transmits, the card receives) and 41/43 PERp0/PERn0.
        E.update({3: "NC", 5: "NC", 35: "CARD1_RX_P", 37: "CARD1_RX_N", 41: "CARD1_TX_P", 43: "CARD1_TX_N", 47: "CARD1_CLK_P", 49: "CARD1_CLK_N", 52: "PCIE1_RST2_n", 53: "CARD1_CLKREQ_n",
                  55: "PCIE1_nWAKE", 56: "WIFI_W_DIS_n", 54: "WIFI_W_DIS2_n", 6: "WIFI_nLED"})
        part("J_M2C1", "Connector", "Bus_M.2_Socket_E", "M.2 E-key 2230 socket, TE 2199230-4, M2.5 standoff: AsiaRF AW7915-AED WiFi 6 link card (two MHF4 leads to A22's P2P jacks)", "M2E", dict(E, **_M2_MECH), "C2977809")
        r(R(37), "10k", "WIFI_W_DIS_n", a33); r(R(38), "10k", "WIFI_W_DIS2_n", a33); nfet(Q(6), "EMCON_ON", "GND", "WIFI_W_DIS_n", "2N7002: EMCON_ON pulls W_DISABLE1# low (open drain)")
        r(R(39), "1k", a33, "LED_WIFI_A"); led("LED15", "blue WiFi link", "LED_WIFI_A", "WIFI_nLED")
    elif s == 2:   # 5G module RM520N-GL on a B-key 3052 (M.2 WWAN socket 2 pinout); SIM 1 on the UIM pins, SIM 2 on the module's USIM2 pins 40 to 48
        B = {n: "NC" for n in range(1, 76) if not 12 <= n <= 19}
        B.update({n: "GND" for n in (3, 5, 11, 27, 33, 39, 45, 51, 57, 71, 73)}); B.update({n: m2c for n in (2, 4, 70, 72, 74)})
        # W3-F01, 26 September 2026: the RM520N's own pin table (HD v1.1 Table 18) is 41 PCIE_TX_M, 43 PCIE_TX_P (AO) and
        # 47 PCIE_RX_M, 49 PCIE_RX_P (AI), so the switch's transmitter reaches 47/49 through its 220 nF and 41/43 return.
        # S-13, 26 September 2026: SIM 2 on the module's own pins, 40 USIM2_DET, 42 USIM2_DATA, 44 USIM2_CLK, 46 USIM2_RST
        # and 48 USIM2_VDD (HD v1.1 Figure 2 and Table 15; the old map had CLK on 40, IO on 42, RST on 44, VCC on 46 and
        # left 48 open). The GCT SIM8060-6 holder has no card-detect switch, so both DET pins (40 and 66) stay unconnected,
        # which is what HD 4.1.5 asks when hot-plug is not used.
        B.update({7: "USB_5G_P", 9: "USB_5G_N", 41: "CARD2_TX_N", 43: "CARD2_TX_P", 47: "CARD2_RX_N", 49: "CARD2_RX_P", 53: "CARD2_CLK_N", 55: "CARD2_CLK_P", 50: "PCIE2_RST2_n", 52: "CARD2_CLKREQ_n",
                  54: "PCIE2_nWAKE", 6: "5G_PWROFF_n", 8: "5G_W_DIS_n", 67: "5G_RST_n", 30: "SIM1_RST", 32: "SIM1_CLK", 34: "SIM1_IO", 36: "SIM1_VCC",
                  40: "NC", 42: "SIM2_IO", 44: "SIM2_CLK", 46: "SIM2_RST", 48: "SIM2_VCC", 10: "5G_nLED"})
        # S-12 (adjudication A08), 26 September 2026: TE 1-2199119-5 (C574849) is KEY M and the RM520N-GL is key B only
        # (HD v1.1 "standard M.2 Key-B WWAN module", pins 12 to 19 the notch). TE customer drawing C-2199119 rev F sheet 2:
        # 2199119-3 is KEY ID B, 15u" gold, the same 3.2 mm height and 67 positions; JLCPCB C590866 reads "2199119-3, TE
        # Connectivity, -40 to +80 C" (26 Sep 2026 01:15 CEST). Its land (sheet 3) is the M2B footprint's pad field, checked pad by pad in
        # drafts/r4-decisions.md, EXCEPT the two locating holes (dia 1.1 datum Y at X -10, dia 1.6 datum X at X +10, on the
        # line 4.5 mm below the odd row), which gen_footprints_b16.py does not draw: a mismatch until that land carries them.
        # ANTENNAS (D-07): the socket carries no RF; the module's own IPEX 20579-001E receptacles (HD 5.2.1) take pigtails,
        # ANT0 and ANT2 always and ANT3 as the third jack when the case measurement (D-08) confirms board A's site at X +46.
        part("J_M2C2", "Connector", "Bus_M.2_Socket_B", "M.2 B-key 3052 socket, TE 2199119-3, M2.5 standoff: Quectel RM520N-GL 5G module (PCIe or USB 2.0; pigtails from the module's ANT0, ANT2 and, subject to D-08, ANT3 to board A's 5G jacks)", "M2B", dict(B, **_M2_MECH), "C590866")
        r(R(37), "10k", "5G_W_DIS_n", a33); nfet(Q(6), "EMCON_ON", "GND", "5G_W_DIS_n", "2N7002: EMCON_ON pulls W_DISABLE1# low (open drain)")
        r(R(38), "10k", "5G_PWROFF_n", a33); nfet(Q(7), "5G_OFF", "GND", "5G_PWROFF_n", "2N7002 expander -> FULL_CARD_POWER_OFF#")
        # O-15, 26 September 2026 (round-4 review, minor; taken in the round-4 fix-up under the owner's standing rule):
        # RESET# (pin 67) is a 1.8 V input "internally pulled up to 1.8 V" (HD v1.1 Table 12, Figure 12: a 1.5 uA
        # source), and "Voltage at Digital Pins" is at most 2.3 V absolute (HD v1.1 Table 50). The 10 k pull-up to this
        # 3.3 V rail that stood here (R240) held the pin above that limit whenever the module ran, so it is removed:
        # Quectel's own circuit is an open collector or drain on the pin and nothing else ("An open collector/drain
        # driver or a button can be used to control RESET#", HD 3.6). Q208's off-state leakage is at most 80 nA at
        # VDS 60 V (CJ 2N7002 datasheet, IDSS, JLCPCB C8545), against the module's 1.5 uA pull-up; R62 holds its gate low.
        nfet(Q(8), "5G_RESET", "GND", "5G_RST_n", "2N7002 expander -> RESET# (open drain, no pull-up: HD Figure 12)")
        r(R(39), "1k", a33, "LED_5G_A"); led("LED25", "amber 5G network", "LED_5G_A", "5G_nLED")
        # F-PR-05, 26 September 2026: "Ensure the continuous current capability of the power supply is 3.0 A at least and
        # the peak current capability ... is 4 A at least ... two bypass capacitors of 220 uF with low ESR ... and a
        # multi-layer ceramic chip capacitor (MLCC) array" (HD v1.1 3.3.1, Figure 6: 220 uF, 100 nF, 6.8 nF, 220 pF,
        # 68 pF at the PMU pins 2/4; 220 uF, 100 nF, 220 pF, 68 pF, 15 pF, 9.1 pF, 4.7 pF at the APT pins 70/72/74; "a
        # TVS with working peak reverse voltage of 5 V"). The buck is a 5 A AP64500, so 4 A is inside its rating; the rail
        # declaration above carries 3.0 A and 4.0 A. Bulk: KEMET T520B227M006ATE025 (220 uF 6.3 V polymer tantalum, 25 mOhm,
        # EIA 3528-21, -55 to +105 C on KEMET's part sheet, JLCPCB C212684); ceramics YAGEO CC0402 (the family this board already buys).
        _5g = []
        def _c5(ref, val, lcsc, pin, fp="C0402"):
            c(ref, val, m2c, "GND", fp, lcsc, bypass=("J_M2C2", pin)); _5g.append(ref)
        for _ref, _pin in (("C520", "2"), ("C521", "70")):
            part(_ref, "Device", "C_Polarized", "220u 6.3V KEMET T520B227M006ATE025 polymer tantalum 25 mOhm (RM520N HD 3.3.1 bulk)", "CPT3528", {"1": m2c, "2": "GND"}, "C212684")
            _intent.bypass(_ref, "J_M2C2", _pin, m2c); _5g.append(_ref)
        _c5("C522", "6.8n 50V X7R", "C93654", "2"); _c5("C523", "220p 50V C0G", "C107001", "2"); _c5("C524", "68p 50V C0G", "C107009", "2")
        _c5("C525", "100n", "", "70"); _c5("C526", "220p 50V C0G", "C107001", "70"); _c5("C527", "68p 50V C0G", "C107009", "70")
        _c5("C528", "15p 50V C0G", "C106997", "70"); _c5("C529", "9.1p 50V C0G", "C526972", "70"); _c5("C530", "4.7p 50V C0G", "C325453", "70")
        part("D520", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": m2c, "2": "GND"}, "C113974"); _5g.append("D520")   # HD 3.3.1's 5 V TVS; pin 1 on the rail is pad 1, the cathode (A03)
        # S-13, 26 September 2026: each SIM per HD v1.1 Figure 18 (a 6-pin holder without hot-plug): 22 Ohm in series in
        # RST, CLK and DATA, 10 pF on each at the holder, 100 nF on VCC. SIM 2 also follows Figure 19's compatible design:
        # four 0 Ohm links at the module (RST, CLK, DATA, VDD) are the removable parts, so an eSIM-fitted module
        # variant ("pins 40, 42, 44, 46 and 48 of the module must be kept open") is built by leaving them off. Module
        # side SIMk_*, holder side SIMCk_*. The TVS array the HD asks for (at most 10 pF) is an open item in drafts.
        # Fix-up, 26 September 2026 (round-4 review, minor): Figure 19 draws BOTH, five 0 Ohm "near the module" and the
        # 22 Ohm near the holder, and one part cannot sit in both places. A 22 Ohm left off at the holder would leave the
        # whole run hanging on the eSIM's pins. So SIM 2's RST, CLK and DATA now carry a 0 Ohm at the module, R287 to
        # R289, before the 22 Ohm at the holder (module side SIM2_x, the run SIMR2_x, the holder SIMC2_x), and R272 is
        # the fourth link, on VDD, also at the module. DET (pin 40) stays open. An eSIM build leaves the four 0 Ohm off.
        for k in (1, 2):
            md = lambda x: "SIM%d_%s" % (k, x); cd = lambda x: "SIMC%d_%s" % (k, x)
            vcc = md("VCC") if k == 1 else cd("VCC")
            if k == 2: r(R(72), "0R (eSIM option link at the module, HD 4.1.6 Figure 19)", md("VCC"), cd("VCC"), "R", "C21189")
            for j, x in enumerate(("RST", "CLK", "IO")):
                if k == 2:
                    r(R(87 + j), "0R (eSIM option link at the module, HD 4.1.6 Figure 19)", md(x), "SIMR2_%s" % x, "R", "C21189")
                    r(R(63 + 3 * k + j), "22R", "SIMR2_%s" % x, cd(x))
                    _intent.node("SIMR2_%s" % x, 3.3, "SIM 2's line between the module's 0 Ohm link and the holder's 22 Ohm, "
                                 "swinging to USIM2_VDD (1.8 or 3.0 V, HD v1.1 pin table); declared at 3.3 V like the holder side")
                else:
                    r(R(63 + 3 * k + j), "22R", md(x), cd(x))
            part("J_SIM%d" % k, "Connector", "SIM_Card_Shielded", "nano-SIM push-push GCT SIM8060 (SIM %d)" % k, "NANOSIM", {"1": vcc, "2": cd("RST"), "3": cd("CLK"), "5": "GND", "6": "NC", "7": cd("IO"), "SH": "GND"}, "C6296715")
            c(C(83 + 3 * k), "100n", vcc, "GND"); c(C(84 + 3 * k), "10p 50V C0G", cd("IO"), "GND", "C0402", "C106199"); c(C(85 + 3 * k), "10p 50V C0G", cd("CLK"), "GND", "C0402", "C106199")
            c(C(82 + k), "10p 50V C0G", cd("RST"), "GND", "C0402", "C106199")
            for x in ("RST", "CLK", "IO"):
                _intent.node(cd(x), 3.3, "a SIM card line at the holder, swinging to USIM%d_VDD, which the module sets to 1.8 or "
                             "3.0 V (HD v1.1 pin table: 1.8/3.0 V, Class B and C cards); declared at 3.3 V for the 50 V capacitor on it" % k)
        SLOT_EXTRA[2].update(_5g)
    else:   # 9 September 2026 (ARCH-PCB-B-IOHA ruling 3): the spare M-key drive slot carries a SECOND WiFi card instead.
            # The mesh link is the one bearer with no second path in the kit, and the card is single-homed to slot 1's
            # PCIe switch, so losing slot 1 lost the kit-to-kit link entirely. A second identical card on slot 3 fixes
            # that; the two share the EXISTING pair of P2P antennas through the passive changeover of the plane below,
            # because under the no-vent ruling every case penetration is a seal and two more jacks would be a case change.
            # What is given up is a fourth drive slot, which k3s does not need with three replicas.
        E3 = {n: "NC" for n in list(range(1, 24)) + list(range(32, 76))}
        E3.update({n: "GND" for n in (1, 7, 18, 33, 39, 45, 51, 57, 63, 69, 75)}); E3.update({n: m2c for n in (2, 4, 72, 74)})
        # W3-F01, 26 September 2026: as slot 1, 35/37 PETp0/PETn0 carry what the card receives and 41/43 what it transmits.
        E3.update({3: "NC", 5: "NC", 35: "CARD3_RX_P", 37: "CARD3_RX_N", 41: "CARD3_TX_P", 43: "CARD3_TX_N", 47: "CARD3_CLK_P", 49: "CARD3_CLK_N", 52: "PCIE3_RST2_n", 53: "CARD3_CLKREQ_n",
                   55: "PCIE3_nWAKE", 56: "WIFI2_W_DIS_n", 54: "WIFI2_W_DIS2_n", 6: "WIFI2_nLED"})
        part("J_M2C3", "Connector", "Bus_M.2_Socket_E", "M.2 E-key 2230 socket, TE 2199230-4, M2.5 standoff: the second AsiaRF AW7915-AED (two MHF4 leads to the antenna changeover U82 and U83)", "M2E", dict(E3, **_M2_MECH), "C2977809")
        r(R(37), "10k", "WIFI2_W_DIS_n", a33); r(R(38), "10k", "WIFI2_W_DIS2_n", a33); nfet(Q(6), "EMCON_ON", "GND", "WIFI2_W_DIS_n", "2N7002: EMCON_ON pulls W_DISABLE1# low (open drain)")
        r(R(39), "1k", a33, "LED_WIFI2_A"); led("LED35", "blue WiFi link, card 2", "LED_WIFI2_A", "WIFI2_nLED")
    c(C(57), "22u 6.3V", m2c, "GND", "C10u"); c(C(58), "100n", m2c, "GND")   # the socket's own decoupling, on the socket side of the shunt
    # S-01 (owner ruling D-05, radios dark), 26 September 2026: THE MODULE'S OWN WIFI AND BLUETOOTH ON THE EMCON LINE.
    # WL_nDisable (89) and BT_nDisable (91) "may only be driven low; it can't be driven high" and are "internally
    # pulled up through 1.8 kOhm to CM5_3.3V" (CM5 datasheet release 3, 2.1.1, 2.1.2 and the pin table), and "No pins
    # should be powered before the 5 V rail is active" (3.1). They used to sit straight on U6, a push-pull PCA9555
    # output with its own internal pull-up to +3V3_DEV, which drove them high and powered them with the module off.
    # Now each is an OPEN DRAIN: a 2N7002 with its source on ground and its drain on the module pin, so the pin is
    # only ever pulled low (a pull-down is not a powered pin, and the datasheet allows "driven or tied low"), and the
    # module's own internal driver never meets a driven high on our side. Its gate is U{s}11 (SN74LVC32A, the OR
    # the voters already use): KILL = OFF OR EMCON_ON, so the radio is released only when U6 asks for it AND EMCON
    # is not asserted. U6's two requests per slot are active HIGH = radio off, with a 10 k pull-up each, so from
    # power-on until the panel firmware writes U6 the module radios are dark by design, not by the expander's
    # internal pull-up (A01). A 100 k on each gate holds it defined while U{s}11 starts.
    # Fix-up, 26 September 2026 (round-4 review, minor): that 100 k goes to GND, so if +3V3_DEV is lost while a slot is
    # up, KILL sits at 0 and the module's radios are RELEASED (fail open), as they were with U6 driving the pins before
    # round 4. The review's remedy, the 100 k up to +3V3_CM{s}, was not taken: in the normal power-on default (requests
    # high, KILL high) with the module off it feeds 33 uA per line into the module's unpowered 3.3 V output (CM5
    # datasheet 3.1, "No pins should be powered before the 5 V rail is active"). Open item O-14 carries the remedy.
    part(U(11), "Connector_Generic", "Conn_01x14", "SN74LVC32APWR quad OR, slot S%d: module WiFi and BT kill (request OR EMCON); gates 3 and 4 spare" % s, "TSSOP14",
         {"7": "GND", "14": "+3V3_DEV", "1": "WL_nDIS%d_OFF" % s, "2": "EMCON_ON", "3": "WL_nDIS%d_KILL" % s,
          "4": "BT_nDIS%d_OFF" % s, "5": "EMCON_ON", "6": "BT_nDIS%d_KILL" % s,
          "9": "GND", "10": "GND", "8": "NC", "12": "GND", "13": "GND", "11": "NC"}, "C352974")
    c(C(97), "100n", "+3V3_DEV", "GND")
    nfet(Q(9), "WL_nDIS%d_KILL" % s, "GND", "WL_nDIS%d" % s, "2N7002: pulls WL_nDisable low only (S-01)")
    nfet(Q(10), "BT_nDIS%d_KILL" % s, "GND", "BT_nDIS%d" % s, "2N7002: pulls BT_nDisable low only (S-01)")
    r(R(62), "10k", "WL_nDIS%d_OFF" % s, "+3V3_DEV"); r(R(63), "10k", "BT_nDIS%d_OFF" % s, "+3V3_DEV")
    r(R(73), "100k", "WL_nDIS%d_KILL" % s, "GND"); r(R(74), "100k", "BT_nDIS%d_KILL" % s, "GND")
    # --- USB 3 hub TUSB8041I on the module's USB3-0 port; downstream ports per the fabric of 32.58
    # 9 September 2026 (ARCH-PCB-B-IOHA): the hub and the two host-selection switches run on the DEVICE rail, not on
    # this slot's. They used to sit on +3V3_S{s}B, whose buck is enabled by the module's own 3.3 V, so a bank died with
    # the module it was supposed to fail away from and the whole ring was decoration. Read off the rail tree, not the
    # topology drawing. The PCIe switch and the NVMe socket stay on the slot rail on purpose: they are the module's.
    h = {}
    for n, nm in TUSB.items():
        if nm == "VDD": h[n] = v11
        elif nm == "VDD33": h[n] = "+3V3_DEV"
        elif nm == "GND": h[n] = "GND"
        else: h[n] = "NC"
    h.update({53: "BANK%d_UPD_P" % s, 54: "BANK%d_UPD_N" % s, 55: "BANK%d_UPRX_P" % s, 56: "BANK%d_UPRX_N" % s, 58: "BANK%d_UPTX_P" % s, 59: "BANK%d_UPTX_N" % s, 50: "HUB%d_RST_n" % s, 64: "HUB%d_R1" % s,
              48: "HUB%d_VBUS" % s, 61: "HUB%d_XO" % s, 62: "HUB%d_XI" % s, 49: "GND", 39: "HUB%d_SMBUS_n" % s, 41: "HUB%d_PWRPOL" % s})
    # 9 September 2026 (ARCH-PCB-B-IOHA): bank 3's port 4 was a spare header and now carries the 5G module's USB. Two things
    # made that necessary and useful. The failover ring needs every module's USB3-1 D+/D- for the neighbour bank it adopts,
    # and slots 1 and 2 were spending those pins on their M.2 card's USB2 link. On slot 1 that link was already dead copper:
    # the AW7915-AED is an MT7915, WiFi only, with no Bluetooth companion to use it. On slot 2 the 5G module does use it, for
    # firmware and AT access, so rather than lose it the link becomes a device on a hub, which also gives it the bank's failover.
    # W3-F02, 26 September 2026: the LimeSDR's SuperSpeed pairs were crossed. A Standard-A receptacle is named from the
    # HOST'S side (KiCad USB3_A: 5 SSRX-, 6 SSRX+, 8 SSTX-, 9 SSTX+; TI's own Figure 6 in SLLSEE4E puts USB_SSTXP_DN1
    # through 0.1 uF to the connector's SSTXP and brings its SSRXP straight to USB_SSRXP_DN1). So the hub's receiver
    # (6/7) takes LIME_SSRX from J_LIME 6/5 and its transmitter (3/4) reaches J_LIME 9/8 through C161/C162.
    PORTS = {1: {1: ("LIME_DP", "LIME_DM", "HUB1_D1TX_P", "HUB1_D1TX_N", "LIME_SSRX_P", "LIME_SSRX_N"), 2: ("USB_PNL_P", "USB_PNL_N"), 3: ("CAM_DP", "CAM_DM"), 4: ("RB_DP", "RB_DM")},
             2: {1: ("GNSS_DP", "GNSS_DM"), 2: ("ZBA_DP", "ZBA_DM"), 3: ("ZBB_DP", "ZBB_DM"), 4: ("QMX_DP", "QMX_DM")},
             3: {1: ("USB_D8_P", "USB_D8_N"), 2: ("USB_E6_P", "USB_E6_N"), 3: ("USB_WALL_P", "USB_WALL_N"), 4: ("USB_5G_P", "USB_5G_N")}}[s]
    for port, nets in PORTS.items():
        dp, dm, txp, txm, rxp, rxm = HUB_PORT[port]
        h[dp] = nets[0]; h[dm] = nets[1]
        if len(nets) == 6: h[txp], h[txm], h[rxp], h[rxm] = nets[2], nets[3], nets[4], nets[5]
    if s == 1: h[36] = "LIME_HW_EN"; h[46] = "LIME_FLT"
    synth(U(2), "TUSB8041", "TI TUSB8041IRGCR four-port USB 3.0 hub, slot S%d (upstream the CM5 USB3-0 port)" % s, "QFN64", h, "C544686")
    c(C(59), "100n", "BANK%d_UPRX_P" % s, "MUX%d_A1P" % s, "C0402"); c(C(60), "100n", "BANK%d_UPRX_N" % s, "MUX%d_A1N" % s, "C0402")   # AC coupling on the hub's transmit pair, hub side of the mux so it serves either host
    if s == 1: c(C(61), "100n", "HUB1_D1TX_P", "LIME_SSTX_P", "C0402"); c(C(62), "100n", "HUB1_D1TX_N", "LIME_SSTX_N", "C0402")   # W3-F02: to the receptacle's SSTX
    r(R(41), "10k", "HUB%d_RST_n" % s, "+3V3_DEV"); c(C(63), "1u", "HUB%d_RST_n" % s, "GND"); r(R(42), "9.53k 1%", "HUB%d_R1" % s, "GND"); r(R(43), "90.9k 1%", "+5V_DEV", "HUB%d_VBUS" % s); r(R(44), "10k 1%", "HUB%d_VBUS" % s, "GND")
    r(R(45), "10k", "HUB%d_SMBUS_n" % s, "+3V3_DEV"); r(R(46), "10k", "HUB%d_PWRPOL" % s, "+3V3_DEV")
    part("Y%d" % (100 * s + 1), "Device", "Crystal_GND24", "24 MHz 3225", "XTAL", {"1": "HUB%d_XI" % s, "3": "HUB%d_XO" % s, "2": "GND", "4": "GND"})
    c(C(64), "18p", "HUB%d_XI" % s, "GND", "C0402"); c(C(65), "18p", "HUB%d_XO" % s, "GND", "C0402"); r(R(47), "1M", "HUB%d_XI" % s, "HUB%d_XO" % s)
    for k in range(66, 70): c(C(k), "100n", v11, "GND")
    for k in range(70, 74): c(C(k), "100n", "+3V3_DEV", "GND")
    c(C(74), "10u", v11, "GND", "C10u")
    # --- the host-selection fabric for this bank (ARCH-PCB-B-IOHA section 4). The bank's upstream is a 2:1 selection
    # between its HOME module, this slot's USB3-0, and one NEIGHBOUR module's spare USB3-1. The ring is bank s home s,
    # failover (s mod 3) + 1, so every module uses both of its host ports and any single module loss moves exactly one
    # bank to a neighbour that has a port free. Port A of the TMUXHS4212 is the common side and faces the hub.
    # A 2:1 mux cannot connect two hosts at once by construction, so the voted control of section 5 is there to stop a
    # single wedged controller MOVING ownership, not to prevent contention, which the topology already makes impossible.
    f = s % 3 + 1
    mx = {1: "+3V3_DEV", 10: "+3V3_DEV", 5: "GND", 11: "GND", 20: "GND", 21: "GND", 6: "+3V3_DEV", 2: "BOE%d_n" % s, 9: "BSEL%d" % s,
          3: "BANK%d_UPTX_P" % s, 4: "BANK%d_UPTX_N" % s, 7: "MUX%d_A1P" % s, 8: "MUX%d_A1N" % s,
          19: "HOST%d_0TX_P" % s, 18: "HOST%d_0TX_N" % s, 17: "HOST%d_0RX_P" % s, 16: "HOST%d_0RX_N" % s,
          15: "HOST%d_1TX_P" % f, 14: "HOST%d_1TX_N" % f, 13: "HOST%d_1RX_P" % f, 12: "HOST%d_1RX_N" % f}
    synth(U(9), "TMUXHS4212", "TI TMUXHS4212 SuperSpeed 2:1 host select, bank %d: B = slot %d USB3-0 (home), C = slot %d USB3-1 (failover)" % (s, s, f), "VQFN20", mx, "C3656912")
    c(C(92), "100n", "+3V3_DEV", "GND"); c(C(93), "1u", "+3V3_DEV", "GND")
    u2 = {10: "+3V3_DEV", 5: "GND", 6: "BOE%d_n" % s, 9: "BSEL%d" % s,
          8: "BANK%d_UPD_P" % s, 7: "BANK%d_UPD_N" % s,
          1: "HOST%d_0D_P" % s, 2: "HOST%d_0D_N" % s, 3: "HOST%d_1D_P" % f, 4: "HOST%d_1D_N" % f}
    synth(U(10), "TS3USB221A", "TI TS3USB221A USB2 2:1 host select, bank %d: port 1 = slot %d (home), port 2 = slot %d (failover)" % (s, s, f), "UQFN10", u2, "C128396")
    c(C(94), "100n", "+3V3_DEV", "GND")
    # Safe state with the control plane dark: SEL low is port A to port B on the TMUXHS4212 and port 1 on the TS3USB221A,
    # both of which are the HOME module, and OEn low is normal operation on both. So an unpowered or absent control plane
    # leaves each bank connected to its own module, which is exactly the board's behaviour before this fabric existed.
    r(R(60), "100k", "BSEL%d" % s, "GND"); r(R(61), "100k", "BOE%d_n" % s, "GND")
    # --- module support: LEDs, fan, flashing port, bench headers, the SPI breakout, the domain-boundary stages
    r(R(48), "1k", cm33, "LED_ACT_A%d" % s); led("LED%d6" % s, "green ACT (LED_nACT sinks)", "LED_ACT_A%d" % s, "LED_nACT%d" % s)
    part(Q(1), "Transistor_BJT", "BC857", "BC857: LED_nPWR must be buffered (datasheet Table 4)", "SOT23", {"1": "Q%dB" % s, "2": cm33, "3": "Q%dC" % s})
    r(R(49), "10k", "LED_nPWR%d" % s, "Q%dB" % s); r(R(50), "1k", "Q%dC" % s, "LED_PWR_A%d" % s); led("LED%d7" % s, "red PWR", "LED_PWR_A%d" % s, "GND")
    part("J_FAN%d" % s, "Connector_Generic", "Conn_01x04", "IP68 cooler fan of S%d (JST-SH 1.0): 5V GND TACHO PWM" % s, "SH4", {"1": n5, "2": "GND", "3": "FAN_TACHO%d" % s, "4": "FAN_PWM%d" % s, "MP": "NC"}, "C160390"); r(R(51), "10k", "FAN_PWM%d" % s, cm33)   # J_FAN: JST BM04B-SRSS-TB(LF)(SN), the part this line names (JLCPCB stock 70,953 on 14 Sep 2026). R151/R251/R351: the fan PWM pull-up, swallowed by this comment 14 to 15 Sep 2026 (test_swallowed_calls).
    # MP: the JST-SH land's two mechanical retention tabs. They are declared NC rather than tied to ground: the tab is
    # a strain relief that solders to its own pad and carries no current, and giving it a net would put copper of that
    # net under the connector body (17 September 2026, found by judging every pin map against its land).
    usb_c_recept("J_FLASH%d" % s, "USB_OTG_P%d" % s, "USB_OTG_N%d" % s, "VBUS_FLASH%d" % s, "CC1_F%d" % s, "CC2_F%d" % s); r(R(52), "5.1k", "CC1_F%d" % s, "GND"); r(R(53), "5.1k", "CC2_F%d" % s, "GND")
    esd(U(7), "USB_OTG_P%d" % s, "USB_OTG_N%d" % s, "VBUS_FLASH%d" % s)
    part("J_RPIBOOT%d" % s, "Connector_Generic", "Conn_01x02", "nRPIBOOT jumper S%d: fit to flash the eMMC over J_FLASH%d" % (s, s), "PH1x2", {"1": "nRPIBOOT%d" % s, "2": "GND"})
    # B16: the EEPROM_nWP, PMIC_Enable and PWR_Button bench jumpers of B15 are gone (the module pins stay unconnected; the panel controller owns power control over SLOT_ENx)
    part("J_DBG%d" % s, "Connector_Generic", "Conn_01x05", "console UART0 and the module I2C of S%d (3.3 V, bench): GND TX RX SDA SCL" % s, "PH1x5", {"1": "GND", "2": "UART0_TX%d" % s, "3": "UART0_RX%d" % s, "4": "SDA_CM%d" % s, "5": "SCL_CM%d" % s})
    if s == 3: part("J_SPI3", "Connector_Generic", "Conn_02x05_Odd_Even", "SPI0 breakout of S3 (2x5): 3V3 GND MISO MOSI SCLK CE0 CE1 IO23 IO24 IO26; the E22 LoRa module hangs on these nets", "PH2x5",
                    {"1": b33, "2": "GND", "3": "SPI3_MISO", "4": "SPI3_MOSI", "5": "SPI3_SCLK", "6": "SPI3_CE0", "7": "SPI3_CE1", "8": "SPI3_IO23", "9": "SPI3_IO24", "10": "SPI3_IO26"})
    level(Q(2), R(54), "PI_SHDN_REQ", "PI_SHDN_REQ_CM%d" % s, cm33)
    level(Q(3), R(55), "PI_KILL", "PI_KILL_CM%d" % s, cm33)
    level(Q(4), R(56), "GNSS_PPS", "GNSS_PPS_CM%d" % s, cm33)
    level(Q(5), R(57), "HB%d" % s, "HB_CM%d" % s, cm33, "+3V3_DEV", R(58))
    # --- Ethernet: the module's four pairs into switch port s through 100 nF (PHY to PHY, no magnetics)
    for k, x in ((0, "A"), (1, "B"), (2, "C"), (3, "D")):
        c(C(75 + 2 * k), "100n", "ETH%d_P%d_P" % (s, k), "SWP%d_%s_P" % (s, x), "C0402"); c(C(76 + 2 * k), "100n", "ETH%d_P%d_N" % (s, k), "SWP%d_%s_N" % (s, x), "C0402")
for s in (1, 2, 3): slot(s)

_SEC_MARKS = []   # 15 Sep 2026: the shared parts are sectioned by the headings below, in the order they are registered
# ================================================================= shared: power
_SEC_MARKS.append(('SHARED: POWER', len(P)))
part("J_5V_DEV", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: USB device rail from A22 J_5V_DEV: + -", "VH2", {"1": "+5V_DEV", "2": "GND"}, "C274411")
part("D1", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_DEV", "2": "GND"}); c("C1", "100u 10V", "+5V_DEV", "GND", "C100u"); c("C2", "100u 10V", "+5V_DEV", "GND", "C100u")
ic("U25", 6, "AP63203WU-7 3.3 V 2 A buck: the shared logic (+3V3_DEV)", "TSOT6", {"1": "+3V3_DEV", "2": "+5V_DEV", "3": "+5V_DEV", "4": "GND", "5": "DEV_SW", "6": "DEV_BST"}, "C780769")   # TSOT-23-6, 12,477 in stock
# DEV_SW is the one buck on this board written out rather than through a helper, so it gets its line here
# (20 September 2026, the same sweep): the AP63203 runs the shared logic rail off +5V_DEV.
_intent.node("DEV_SW", _intent.net_volts("+5V_DEV"),
             "the AP63203's switching node for +3V3_DEV: it swings to +5V_DEV, the rail that feeds it, and a "
             "diode drop below ground on the other half of the cycle", v_min=-1.0)
part("L1", "Device", "L", "4.7uH XAL4030-472ME", "L4020", {"1": "DEV_SW", "2": "+3V3_DEV"}); c("C3", "100n", "DEV_BST", "DEV_SW"); c("C4", "10u", "+5V_DEV", "GND", "C10u"); c("C5", "22u 6.3V", "+3V3_DEV", "GND", "C10u"); c("C6", "22u 6.3V", "+3V3_DEV", "GND", "C10u")
buck_small("U26", "KSZC", "+5V_DEV", "+5V_DEV", "+1V2_KSZ", ["L2", "C7", "C8", "C9", "C10", "C11", "R1", "R2"], "20.0k 1%", "1.2 V Ethernet switch core")
# U27's code is the Diodes part itself (2.5 V 600 mA, 2,997 in stock); the only other hit for it is a
# house-brand relabel, which is what the 11 September certification pass refused for the M.2 sockets.
ic("U27", 5, "AP2112K-2.5 LDO: the switch's 2.5 V analog rail", "SOT235", {"1": "+3V3_DEV", "2": "GND", "3": "+3V3_DEV", "4": "NC", "5": "+2V5_KSZ"}, "C176945"); c("C12", "1u", "+2V5_KSZ", "GND"); c("C13", "1u", "+3V3_DEV", "GND")
part("BT1", "Device", "Battery_Cell", "CR2032 holder Keystone 3034: VBAT for the three modules' RTCs, the LG290P backup and the DS3231", "CR2032", {"1": "VBAT", "2": "GND"})
# ================================================================= Ethernet switch KSZ9897R: ports 1-3 the modules, port 4 the wall RJ45 through the magnetics with the PoE injector
_SEC_MARKS.append(('ETHERNET SWITCH KSZ9897R: PORTS 1-3 THE MODULES, PORT 4 THE WALL RJ45 THROUGH THE..', len(P)))
k = {}
for n, nm in KSZ.items():
    if nm == "VDDIO": k[n] = "+3V3_DEV"
    elif nm == "AVDDH": k[n] = "+2V5_KSZ"
    elif nm in ("AVDDL", "DVDDL"): k[n] = "+1V2_KSZ"
    elif nm in ("GND", "E_PAD"): k[n] = "GND"
    elif nm.startswith("TXRX") and nm[4] in "123":
        s_ = nm[4]; pol = "P" if nm[5] == "P" else "N"; k[n] = "SWP%s_%s_%s" % (s_, nm[-1], pol)
    elif nm.startswith("TXRX4"):
        k[n] = "SWP4_%s_%s" % (nm[-1], "P" if nm[5] == "P" else "N")
    else: k[n] = "NC"
k.update({125: "KSZ_XO", 126: "KSZ_XI", 127: "KSZ_ISET", 96: "KSZ_RST_n", 94: "EXP_INT", 98: "SDA", 101: "SCL", 105: "KSZ_LED1", 91: "KSZ_LED2", 88: "KSZ_LED3", 85: "KSZ_LED4", 86: "KSZ_STRAP_I2C"})
synth("U1", "KSZ9897R", "Microchip KSZ9897RTXI seven-port Gigabit switch: ports 1-3 the CM5 slots (PHY to PHY), port 4 the wall RJ45; I2C management on the kit bus", "TQFP128EP", k, "C638299")
part("Y1", "Device", "Crystal_GND24", "25 MHz 3225", "XTAL", {"1": "KSZ_XI", "3": "KSZ_XO", "2": "GND", "4": "GND"}, "C164047"); c("C14", "18p", "KSZ_XI", "GND", "C0402"); c("C15", "18p", "KSZ_XO", "GND", "C0402")
r("R57", "1k (strap [LED4_1, LED3_1] = 01: I2C management, Table 3-3)", "KSZ_STRAP_I2C", "GND"); r("R3", "6.04k 1% (ISET)", "KSZ_ISET", "GND"); r("R4", "10k", "KSZ_RST_n", "+3V3_DEV"); c("C16", "10u", "KSZ_RST_n", "GND", "C10u"); nfet("Q2", "KSZ_RST", "GND", "KSZ_RST_n", "2N7002 expander -> switch reset")
for i, nm in enumerate(("KSZ_LED1", "KSZ_LED2", "KSZ_LED3", "KSZ_LED4"), 1):
    r("R%d" % (4 + i), "1k", "+3V3_DEV", "LED_KSZ_A%d" % i); led("LED%d" % i, "green Ethernet port %d link" % i, "LED_KSZ_A%d" % i, nm)
for i in range(17, 27): c("C%d" % i, "100n", ("+3V3_DEV", "+1V2_KSZ", "+2V5_KSZ")[(i - 17) % 3], "GND")
c("C27", "10u", "+1V2_KSZ", "GND", "C10u"); c("C28", "10u", "+2V5_KSZ", "GND", "C10u")
# magnetics: chip side centre taps to ground through separate 100 nF (voltage-mode PHY, KSZ9897 section 7); MDI side to the RJ45, PoE on the pair 1-2 and 3-6 centre taps
t = {1: "TCT1", 4: "TCT2", 7: "TCT3", 10: "TCT4", 2: "SWP4_A_P", 3: "SWP4_A_N", 5: "SWP4_B_P", 6: "SWP4_B_N", 8: "SWP4_C_P", 9: "SWP4_C_N", 11: "SWP4_D_P", 12: "SWP4_D_N",
     23: "MDI_A_P", 22: "MDI_A_N", 20: "MDI_B_P", 19: "MDI_B_N", 17: "MDI_C_P", 16: "MDI_C_N", 14: "MDI_D_P", 13: "MDI_D_N", 24: "POE_P", 21: "POE_DRAIN", 18: "MCT3", 15: "MCT4"}
synth("T1", "H5007NL", "Pulse H5007NL 1000BASE-T magnetics (switch port 4 to the wall RJ45)", "H5007", t, "C6384935")
for i, nm in enumerate(("TCT1", "TCT2", "TCT3", "TCT4"), 29): c("C%d" % i, "100n", nm, "GND")
r("R9", "75", "MCT3", "BOB"); r("R10", "75", "MCT4", "BOB"); c("C33", "1n 2kV", "BOB", "GND", "C1812")
part("J_ETH", "Connector", "RJ45_Shielded", "RJ45 jack (Amphenol RJHSE5380): patch lead to the sealed wall RJ45; PoE out on 1-2 (+) and 3-6", "RJ45",
     {"1": "MDI_A_P", "2": "MDI_A_N", "3": "MDI_B_P", "4": "MDI_C_P", "5": "MDI_C_N", "6": "MDI_B_N", "7": "MDI_D_P", "8": "MDI_D_N", "SH": "GND"})
# PoE injector TPS23861 (one port used; unused ports per section 8.2.2: SEN grounded, GATE floating, DRAIN open); 54 V from A22's LM5176 boost over J_54V
part("J_54V", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: 54 V PoE feed from A22 J_54V: + -", "VH2", {"1": "+54V_POE", "2": "GND"}, "C274411")
part("D2", "Device", "D_TVS", "SMBJ58A", "TVS", {"1": "+54V_POE", "2": "GND"}, "C135085"); c("C34", "100n 100V", "+54V_POE", "GND", "C10u", "C106243")
# C35 WAS A PART NOBODY SELLS, in the shape of owner ruling 10's twenty-five capacitors: 10 uF 100 V in an
# 1812 land, and JLCPCB's only exact match is a SANYEAR part at stock ZERO, everything else in 1812 at 100 V
# topping out at 2.2 uF. It exists in the SMALLER 1210 land: Murata GRM32EC72A106KE05L, X7S, 243,928 in
# stock. So the land changes and the value does not, which needs no ruling: the design still gets its 10 uF
# at 100 V on the 54 V rail, in less board area than before.
c("C35", "10u 100V", "+54V_POE", "GND", "C1210", "C576517")
synth("U5", "TPS23861", "TI TPS23861PWR PoE PSE controller, port 1 to the wall RJ45 (802.3at), I2C on the kit bus", "TSSOP28",
      {1: "+3V3_DEV", 2: "POE_RST_n", 3: "SCL", 4: "SDA", 5: "SDA", 6: "EXP_INT", 7: "GND", 22: "GND", 28: "+54V_POE", 15: "POE_SEN", 16: "POE_DRAIN", 17: "POE_GATE", 18: "GND", 11: "GND", 8: "GND", 12: "GND", 19: "GND"}, "C93245")
r("R11", "10k", "POE_RST_n", "+3V3_DEV"); c("C36", "100n", "+3V3_DEV", "GND")
part("Q1", "Connector_Generic", "Conn_01x05", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6), PoE port switch (1-3 source, 4 gate, 5 drain tab)", "PPAK", {"1": "POE_SEN", "2": "POE_SEN", "3": "POE_SEN", "4": "POE_GATE", "5": "POE_DRAIN"}, "C473333")
# R12 is 250 mOhm, not the 255 mOhm TI specifies for the TPS23861 sense: JLCPCB stocks 255 mOhm
# only in 0805 at 333 mW and this land is 2512 at 2 W, so every port current reads 2 percent
# high, which is inside the classification margins.
r("R12", "0.25R 1% 2512", "POE_SEN", "GND", "R2512"); r("R13", "0R 2512 (POE_P link)", "+54V_POE", "POE_P", "R2512")   # 9 September 2026 (red team C2): this was 24.9 ohm on an 0603 land, and POE_P is the
# positive centre tap of the port magnetics, that is, the feed to the powered device. At 802.3at (about 600 mA) it dropped 15 V, leaving 39 V against a
# 44 V minimum, and dissipated 9 W in a part rated for 0.1 W. Detection and classification are the TPS23861's own pins; nothing belongs in the feed.
# A 0 ohm 2512 link keeps a place to open the path on the bench and carries the port current.
# ================================================================= display switch: two TS3DV642 in cascade to the HDMI receptacle; SEL2 chooses the slot (SEL1 high = all channels), selects from the panel controller
_SEC_MARKS.append(('DISPLAY SWITCH: TWO TS3DV642 IN CASCADE TO THE HDMI RECEPTACLE; SEL2 CHOOSES THE SLOT..', len(P)))
def ts3(ref, a, b, cmn, sel):
    d = {1: "+3V3_DEV", 2: "HDMI_SW_EN", 16: "HDMI_SW_EN", 17: sel, 9: "NC", 30: "NC", 43: "GND",
         5: cmn + "_D0_P", 6: cmn + "_D0_N", 7: cmn + "_D1_P", 8: cmn + "_D1_N", 10: cmn + "_D2_P", 11: cmn + "_D2_N", 12: cmn + "_CK_P", 13: cmn + "_CK_N", 3: cmn + "_SCL", 4: cmn + "_SDA", 14: cmn + "_HPD", 15: cmn + "_CEC",
         38: a + "_D0_P", 37: a + "_D0_N", 36: a + "_D1_P", 35: a + "_D1_N", 34: a + "_D2_P", 33: a + "_D2_N", 32: a + "_CK_P", 31: a + "_CK_N", 42: a + "_SCL", 41: a + "_SDA", 19: a + "_HPD", 18: a + "_CEC",
         29: b + "_D0_P", 28: b + "_D0_N", 27: b + "_D1_P", 26: b + "_D1_N", 25: b + "_D2_P", 24: b + "_D2_N", 23: b + "_CK_P", 22: b + "_CK_N", 40: b + "_SCL", 39: b + "_SDA", 21: b + "_HPD", 20: b + "_CEC"}
    synth(ref, "TS3DV642", "TI TS3DV642A0RUAR HDMI 2:1 switch (%s / %s -> %s)" % (a, b, cmn), "WQFN42", d, "C157482")
ts3("U3", "HDMI1", "HDMI2", "HDMIM", "HDMI_SEL1"); ts3("U4", "HDMIM", "HDMI3", "HDMIO", "HDMI_SEL2")
r("R14", "10k", "HDMI_SW_EN", "+3V3_DEV"); r("R15", "100k", "HDMI_SEL1", "GND"); r("R16", "100k", "HDMI_SEL2", "GND"); c("C37", "100n", "+3V3_DEV", "GND"); c("C38", "100n", "+3V3_DEV", "GND")
part("J_HDMI", "Connector", "HDMI_A", "HDMI type A receptacle (Molex 208658-1001): cable to the monitor pass-through on the face plate", "HDMI",
     {"1": "HDMIO_D2_P", "3": "HDMIO_D2_N", "4": "HDMIO_D1_P", "6": "HDMIO_D1_N", "7": "HDMIO_D0_P", "9": "HDMIO_D0_N", "10": "HDMIO_CK_P", "12": "HDMIO_CK_N", "2": "GND", "5": "GND", "8": "GND", "11": "GND",
      "13": "HDMIO_CEC", "14": "NC", "15": "HDMIO_SCL", "16": "HDMIO_SDA", "17": "GND", "18": "+5V_HDMI", "19": "HDMIO_HPD_IN", "SH": "GND"}, "C916313")
part("F2", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+5V_DEV", "2": "+5V_HDMI"}); c("C39", "10u", "+5V_HDMI", "GND", "C10u")
r("R17", "2.2k", "HDMIO_SCL", "+5V_HDMI"); r("R18", "2.2k", "HDMIO_SDA", "+5V_HDMI")   # source-side DDC pull-ups as the CM5IO board (2.2k)
r("R19", "15k", "HDMIO_HPD_IN", "HDMIO_HPD"); r("R20", "22k", "HDMIO_HPD", "GND")   # the monitor's 5 V hot-plug level down to 3 V for the module pins
# ================================================================= GNSS LG290P on a CP2102N bridge (bank 2 hub, port 1; a BANK is not a slot since the I/O HA work: bank s is hosted by slot s or by its neighbour); 1PPS to the three slots through level stages; active antenna bias from VDD_RF
_SEC_MARKS.append(('GNSS LG290P ON A CP2102N BRIDGE (BANK 2 HUB, PORT 1; A BANK IS NOT A SLOT SINCE THE I/O..', len(P)))
g = {n: "GND" for n, nm in LG.items() if nm == "GND"}
g.update({23: "+3V3_DEV", 22: "VBAT", 20: "GNSS_TXD", 21: "GNSS_RXD", 3: "GNSS_PPS", 8: "GNSS_RST_n", 9: "GNSS_VDD_RF", 11: "GNSS_RF_IN", 6: "GNSS_TXD2", 7: "GNSS_RXD2"})
synth("U11", "LG290P", "Quectel LG290P03AAMD GNSS RTK module: UART1 to the bridge, 1PPS to every slot, active antenna on the west-wall GNSS jack", "LG290P", g, "C29781241")
r("R21", "10k", "GNSS_RST_n", "+3V3_DEV"); c("C40", "100n", "+3V3_DEV", "GND"); c("C41", "10u", "+3V3_DEV", "GND", "C10u"); r("R22", "10k", "GNSS_PPS", "GND")
r("R23", "10R", "GNSS_VDD_RF", "GNSS_BIAS"); part("L3", "Device", "L", "27nH 0402 (antenna bias tee)", "L0402", {"1": "GNSS_BIAS", "2": "GNSS_ANT"}, "C12669"); c("C42", "47p", "GNSS_ANT", "GNSS_RF_IN", "C0402")
part("J_GNSS1", "Connector", "Conn_Coaxial", "U.FL socket: pigtail to A22's GNSS jack J_RF4", "UFL", {"1": "GNSS_ANT", "2": "GND"}, "C88373")
part("J_GNSS2", "Connector_Generic", "Conn_01x03", "LG290P UART2 (bench): GND TX RX", "PH1x3", {"1": "GND", "2": "GNSS_TXD2", "3": "GNSS_RXD2"})
cp2102("U15", "GNSS", "+5V_DEV", "GNSS_DP", "GNSS_DM", "GNSS_RXD", "GNSS_TXD", refs=("R24", "C43", "C44"))
# ================================================================= LoRa E22-900M30S on S3's SPI0, 5 V through a TPS22810 gated by EMCON; antenna pad to a U.FL for A22's LoRa jack
_SEC_MARKS.append(("LORA E22-900M30S ON S3'S SPI0, 5 V THROUGH A TPS22810 GATED BY EMCON; ANTENNA PAD TO A..", len(P)))
e22 = {n: "GND" for n, nm in E22P.items() if nm == "GND"}
e22.update({9: "+5V_LORA", 10: "+5V_LORA", 6: "LORA_RXEN", 7: "LORA_TXEN", 8: "NC", 13: "SPI3_IO24", 14: "SPI3_IO23", 15: "SPI3_IO26", 16: "SPI3_MISO", 17: "SPI3_MOSI", 18: "SPI3_SCLK", 19: "SPI3_CE1", 21: "LORA_ANT"})
synth("U12", "E22_900M30S", "Ebyte E22-900M30S 1 W LoRa (SX1262) on S3 SPI0 CE1: TXEN GPIO4, RXEN GPIO5, DIO1 GPIO24, BUSY GPIO23, NRST GPIO26; EU power cap in meshtasticd", "E22", e22, "C411294")
tps22810("U21", "+5V_DEV", "E22_EN", "+5V_LORA", "E22_CT"); c("C45", "1n", "E22_CT", "GND"); c("C46", "10u", "+5V_LORA", "GND", "C10u"); c("C47", "100n", "+5V_LORA", "GND"); r("R25", "10k", "SPI3_CE1", "+3V3_S3B")
part("J_LORA1", "Connector", "Conn_Coaxial", "U.FL socket: pigtail to A22's LoRa jack J_RF11", "UFL", {"1": "LORA_ANT", "2": "GND"}, "C88373")
# ================================================================= two E72 CC2652P radios (Zigbee coordinator, Thread RCP) on CP2102N bridges (bank 2 hub, ports 2 and 3), 3.3 V through one TPS22810 gated by EMCON
_SEC_MARKS.append(('TWO E72 CC2652P RADIOS (ZIGBEE COORDINATOR, THREAD RCP) ON CP2102N BRIDGES (BANK 2 HUB,..', len(P)))
for i, (tag, uref, ub, refs) in enumerate((("ZBA", "U13", "U16", ("R26", "C48", "C49")), ("ZBB", "U14", "U17", ("R27", "C50", "C51"))), 1):
    E72 = {n: "GND" for n in (1, 11, 12, 19, 23, 34)}
    E72.update({2: tag + "_LED_R", 3: tag + "_LED_G", 7: tag + "_RXD", 8: tag + "_TXD", 10: tag + "_BSL", 13: tag + "_TMSC", 14: tag + "_TCKC", 20: "+3V3_ZB", 24: tag + "_RST_n"})
    part(uref, "Connector_Generic", "Conn_01x34", "Ebyte E72-2G4M20S1E CC2652P (%s): 7 DIO_12 RX, 8 DIO_13 TX, 10 DIO_15 BSL, 24 RESET_N; PCB antenna to the north edge" % ("Zigbee coordinator" if i == 1 else "OpenThread RCP for Matter"), "E72", {str(n): E72.get(n, "NC") for n in range(1, 35)})
    r("R%d" % (27 + i), "10k", tag + "_RST_n", "+3V3_ZB"); r("R%d" % (29 + i), "10k", tag + "_BSL", "+3V3_ZB")
    r("R%d" % (31 + i), "1k", tag + "_LED_R", "LED_%sR_A" % tag); led("LED%d" % (5 + 2 * i - 1), "red %s (DIO_7)" % tag, "LED_%sR_A" % tag, "GND")
    r("R%d" % (33 + i), "1k", tag + "_LED_G", "LED_%sG_A" % tag); led("LED%d" % (5 + 2 * i), "green %s (DIO_8)" % tag, "LED_%sG_A" % tag, "GND")
    part("J_ZBDBG%d" % i, "Connector_Generic", "Conn_01x05", "CC2652P cJTAG %s (bench): 3V3 GND TMSC TCKC RESET" % tag, "PH1x5", {"1": "+3V3_ZB", "2": "GND", "3": tag + "_TMSC", "4": tag + "_TCKC", "5": tag + "_RST_n"})
    cp2102(ub, tag, "+5V_DEV", tag + "_DP", tag + "_DM", tag + "_RXD", tag + "_TXD", rts=tag + "_RST_n", dtr=tag + "_BSL", refs=refs)
tps22810("U22", "+3V3_DEV", "E72_EN", "+3V3_ZB", "E72_CT"); c("C52", "1n", "E72_CT", "GND"); c("C53", "10u", "+3V3_ZB", "GND", "C10u"); c("C54", "100n", "+3V3_ZB", "GND"); c("C55", "100n", "+3V3_ZB", "GND")
# ================================================================= LimeSDR Mini receptacle (bank 1 hub, port 1, USB 3) and the RockBLOCK 9704 header (bank 1 hub, port 4, through a CP2102N), both behind TPS259631 eFuses
_SEC_MARKS.append(('LIMESDR MINI RECEPTACLE (BANK 1 HUB, PORT 1, USB 3) AND THE ROCKBLOCK 9704 HEADER (BANK..', len(P)))
# W3-F02, 26 September 2026: the receptacle's names are the HOST'S: LIME_SSTX on 8/9 is what the hub transmits (through
# C161/C162), LIME_SSRX on 5/6 what it receives from the LimeSDR.
part("J_LIME", "Connector", "USB3_A", "USB 3.0 type A receptacle (Wuerth 692122030100 land): the LimeSDR Mini 2.4 in its bay", "USB3A",
     {"1": "+5V_LIME", "2": "LIME_DM", "3": "LIME_DP", "4": "GND", "5": "LIME_SSRX_N", "6": "LIME_SSRX_P", "7": "GND", "8": "LIME_SSTX_N", "9": "LIME_SSTX_P", "10": "GND"}, "C5355286")
esd("U33", "LIME_DP", "LIME_DM", "+5V_LIME")
efuse("U23", "+5V_DEV", "+5V_LIME", "LIME_EN", "LIME_FLT", ["C56", "R36", "R37", "R38", "R39", "C57"], "301R 1% (ILM: 3.0 A)"); c("C58", "22u 6.3V", "+5V_LIME", "GND", "C10u")
part("J_RB9704", "Connector_Generic", "Conn_02x08_Odd_Even", "RockBLOCK 9704 16-pin (IDC 2x8) on the Ground Control bracket", "IDC16", {
 "1": "GND", "2": "NC", "3": "RB_IEN", "4": "GND", "5": "NC", "6": "RB_CTRL", "7": "RB_STATUS", "8": "RB_XMTG", "9": "NC", "10": "GND", "11": "NC", "12": "NC", "13": "RB_TXD", "14": "RB_RXD", "15": "+5V_RB", "16": "GND"})
cp2102("U18", "RB", "+5V_DEV", "RB_DP", "RB_DM", "RB_RXD", "RB_TXD", refs=("R40", "C59", "C60"))
r("R41", "10k", "RB_STATUS", "+3V3_DEV"); r("R42", "10k", "RB_XMTG", "+3V3_DEV")
efuse("U24", "+5V_DEV", "+5V_RB", "RB_EN", "RB_FLT", ["C61", "R43", "R44", "R45", "R46", "C62"], "301R 1% (ILM: 3.0 A)"); c("C63", "22u 6.3V", "+5V_RB", "GND", "C10u")
# ================================================================= camera, QMX and spare USB headers, the wall USB pair (bank 3 hub, port 3) with its ESD
_SEC_MARKS.append(('CAMERA, QMX AND SPARE USB HEADERS, THE WALL USB PAIR (BANK 3 HUB, PORT 3) WITH ITS ESD', len(P)))
# S-08 (adjudication A01), 26 September 2026: R48 is 4.7 k, not 100 k. The fitted TI PCA9555 pulls every pin up
# through its own resistor after power-on reset (SCPS131J Fig 8-2, IIL up to -100 uA), and against 100 k the enable
# sat near 1.7 V, inside the TPS2065's undefined band; 4.7 k holds it at 0.49 V or less, a defined OFF.
tps2065("U28", "+5V_DEV", "CAM_EN", "+5V_CAM", "CAM_FLT"); r("R47", "10k", "CAM_FLT", "+3V3_DEV"); r("R48", "4.7k", "CAM_EN", "GND"); c("C64", "10u", "+5V_CAM", "GND", "C10u")
part("J_CAM", "Connector_Generic", "Conn_01x04", "camera lead (USB 2.0, bank 1 hub, port 3): 5V D- D+ GND", "PH1x4", {"1": "+5V_CAM", "2": "CAM_DM", "3": "CAM_DP", "4": "GND"}); esd("U34", "CAM_DP", "CAM_DM", "+5V_CAM")
part("F3", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+5V_DEV", "2": "VBUS_QMX"})
# VBUS_QMX IS A CONDUCTOR AND IT WAS DECLARED AS NOTHING AT ALL (20 September 2026; appendix 32.237). It is
# the 5 V that leaves this board for the HF unit in the lid tray, behind its own 0.5 A polyfuse, and +5V_DEV
# already declares F3 as a 0.30 A load, so this is the same 0.30 A on the other side of the fuse: a SERIES
# SEGMENT of +5V_DEV, whose watts are counted there and whose copper every rule judges here.
_intent.rail("VBUS_QMX", 5.0, 0.30, 0.30, "F3", loads={"J_QMX": 0.30}, series_of="+5V_DEV", converted=False,
             note="the QMX unit's 5 V behind the 0.5 A polyfuse F3, out at the J_QMX pigtail")
part("J_QMX", "Connector_Generic", "Conn_01x04", "QMX USB lead (bank 2 hub, port 4): VBUS D- D+ GND; pigtail to the unit's USB-C", "PH1x4", {"1": "VBUS_QMX", "2": "QMX_DM", "3": "QMX_DP", "4": "GND"}); esd("U35", "QMX_DP", "QMX_DM", "VBUS_QMX")
# the QMX 12 V lead runs from A22's J_HF straight to the unit's DC jack (no B16 part)
# 9 September 2026 (ARCH-PCB-B-IOHA): the spare USB header and its fuse are withdrawn. Bank 3's port 4 now carries the 5G
# module's management link, which had to leave the CM5's USB3-1 pins so the failover ring could use them. The 5G module
# takes its VBUS from its own socket rail, so no fuse is needed here.
esd("U29", "USB_WALL_P", "USB_WALL_N", "+3V3_DEV")
# ================================================================= hardware EMCON gates (74LVC08APW: 1 1A 2 1B 3 1Y 4 2A 5 2B 6 2Y 7 GND 8 3Y 9 3A 10 3B 11 4Y 12 4A 13 4B 14 VCC); EMCON_HW low silences every transmitter on this board
_SEC_MARKS.append(('HARDWARE EMCON GATES (74LVC08APW: 1 1A 2 1B 3 1Y 4 2A 5 2B 6 2Y 7 GND 8 3Y 9 3A 10 3B..', len(P)))
part("U19", "Connector_Generic", "Conn_01x14", "SN74LVC08APWR quad AND: LimeSDR (hub port power AND EMCON AND software), RockBLOCK (EMCON AND software), LoRa (EMCON AND software)", "TSSOP14",
     {"1": "EMCON_HW", "2": "LIME_HW_EN", "3": "LIME_EN_A", "4": "LIME_EN_A", "5": "LIME_SW_EN", "6": "LIME_EN", "7": "GND", "8": "RB_EN", "9": "EMCON_HW", "10": "RB_SW_EN", "11": "E22_EN", "12": "EMCON_HW", "13": "LORA_ON", "14": "+3V3_DEV"}, "C465737")
part("U20", "Connector_Generic", "Conn_01x14", "SN74LVC08APWR quad AND: E72 radios (EMCON AND software); spare gates grounded", "TSSOP14",
     {"1": "EMCON_HW", "2": "ZB_ON", "3": "E72_EN", "4": "GND", "5": "GND", "6": "NC", "7": "GND", "8": "NC", "9": "GND", "10": "GND", "11": "NC", "12": "GND", "13": "GND", "14": "+3V3_DEV"}, "C465737")
# S-08 (adjudication A01), 26 September 2026: R50 to R53 are 4.7 k for the same reason as R48: with 100 k against the
# expander's internal pull-up these four software enables read about 1.9 V, inside the LVC08's 0.8 to 2.0 V undefined
# band, until the panel firmware writes U6. R49 stays 100 k: LIME_HW_EN is the hub's PWRCTL1 output, not an expander pin.
c("C65", "100n", "+3V3_DEV", "GND"); c("C66", "100n", "+3V3_DEV", "GND"); r("R49", "100k", "LIME_HW_EN", "GND"); r("R50", "4.7k", "LIME_SW_EN", "GND"); r("R51", "4.7k", "RB_SW_EN", "GND"); r("R52", "4.7k", "LORA_ON", "GND"); r("R53", "4.7k", "ZB_ON", "GND")
# AN EMCON GATE THAT LOSES ITS OWN SUPPLY MUST STILL LEAVE ITS TRANSMITTER OFF (MESHSAT-1357 round 4, R4T-F9, ruled in
# scope by the round-5 tools re-review; taken by the session under the owner's standing rule of 26 September 2026).
# LIME_EN, RB_EN and E22_EN were driven by U19 alone and carried no pull. U19 runs on +3V3_DEV, while the three switches
# it enables take their input from +5V_DEV (U23 and U24 pin 4, U21 pin 6), so a lost +3V3_DEV (U25 or L1 failed) or an
# open U19 pin 14 leaves +5V_DEV up and the three EN pins floating. Both makers forbid that: TPS2596 (SLVSET8A, pin
# table) "Do not leave floating", TPS22810 (SLVSDH0C 9.3.3) "EN/UVLO terminal must not be left floating". E72_EN (U20)
# takes the same pull: U22's input is +3V3_DEV itself, so a lost rail is safe there, but an open U20 pin 14 is not.
# THE UNPOWERED GATE'S OUTPUT: SCAS283W gives the SN74LVC08A no Ioff (it has no partial-power-down feature) and 7.3.3
# says its outputs carry clamp diodes to VCC and to GND. With VCC at 0 V the output can only sink (into the dead rail
# through the upper clamp, at VO > VCC + about 0.5 V), and its inputs, with only a negative clamp, cannot reach it; with
# VCC open nothing in the part can source it either. What remains is leakage the sheet does not bound, so the sizing
# takes the Ioff that the SN74LVC1G08 (SCES217AA, the same family, a part that has the feature) guarantees, 10 uA at
# VCC 0 V and VO 0 to 5.5 V, plus the EN pin's own leakage, 0.1 uA on both makers' sheets (SLVSET8A IENLKG, SLVSDH0C
# IEN/UVLO). 10.1 uA into 10 k is 0.10 V. THE THRESHOLDS: the TPS259631 turns its FET off below VUVLO(F), 1.08 V
# minimum, and reaches its lowest shutdown current below VSD, 0.53 V minimum (SLVSET8A 7.5); the TPS22810 turns off
# below VENF, 1.08 V minimum, and shuts down below VSHUTF, 0.5 V minimum (SLVSDH0C 7.5). So 10 k holds every EN pin
# in full shutdown until the leakage reaches 50 uA, five times the family Ioff, and OFF until 108 uA. THE COST when
# the gate drives high: 3.3 V / 10 k = 0.33 mA per output, inside the SN74LVC08A's VOH of 2.4 V minimum at 12 mA
# (SCAS283W 5.7, VCC 3 V), far above VUVLO(R) 1.22 V and VENR 1.3 V maximum. 10 k and not the 4.7 k of S-08: the
# leakage here is 10 uA, not the PCA9555's 100 uA pull-up, and 10 k is already on this board's BOM (R58, R513).
r("R514", "10k", "LIME_EN", "GND"); r("R515", "10k", "RB_EN", "GND"); r("R516", "10k", "E22_EN", "GND"); r("R517", "10k", "E72_EN", "GND")
# 9 September 2026 (ARCH-PCB-B-IOHA section 2, defect 3): three expander-driven FET gates had no pull-down, so they float
# through the PCA9555's power-on reset, when its ports come up as high-impedance inputs. KSZ_RST holds the Ethernet switch
# in reset for the whole kit if it floats high; 5G_OFF and 5G_RESET do the same to the cellular module. The six gates around
# them have carried a 100k pull-down since the board was drawn; these three were simply missed.
# S-08, 26 September 2026 (A01's optional item, taken by the session): these three were "nominally asserted" by the
# expander's pull-up against 100 k, a gate at about 1.7 V against the 2N7002's 1.0 to 2.5 V threshold. At 4.7 k each
# is a defined OFF at power-up: the Ethernet switch out of reset and the 5G module neither held off nor in reset,
# which is the M.2 default and leaves EMCON to W_DISABLE1#, which is independent of this expander.
r("R60", "4.7k", "KSZ_RST", "GND"); r("R61", "4.7k", "5G_OFF", "GND"); r("R62", "4.7k", "5G_RESET", "GND")
# Fail safe on the two panel lines (9 September 2026, red team C1): with the panel ribbon out, EMCON_HW and TX_INHIBIT_n must read LOW here,
# which silences every transmitter on this board and, through J_AB1, on A22 and D9 as well. C7 holds TX_INHIBIT_n up with 10k when the
# panel is present, which wins over these three boards' 100k pull-downs in parallel (2.5 V, a solid high), so R59 stays 100k.
# R58 IS 10 k SINCE 26 SEPTEMBER 2026 (MESHSAT-1357 round 4, fix-up pass 3, open item O-08; taken by the session under the
# owner's standing rule of 26 September 2026). No resistor holds EMCON_HW up: C7 drives it with the push-pull buffer U9
# (74LVC1G34, since 9 September), so nothing needs this pull-down to be weak. With the panel absent the line is held only
# by the pull-downs, 100 k here and R102's 100 k on board A, 50 k together, against the leakage of every input that reads
# it. At the datasheet maxima (-40 to +85 C) that is six SN74LVC08A inputs at +-5 uA (SCAS283W 5.7: U19 three, U20 one,
# board A's U26 two), three powered STM32H743 TT_a inputs at +-250 nA (DS12110 Rev 10 Table 60) and Q11's gate at 80 nA
# (CJ 2N7002 IGSS), 30.8 uA. At 50 k that is 1.54 V, above the LVC08's VIL of 0.8 V (5.4), so the panel-absent LOW was not
# proven. At 10 k (9.09 k with R102) it is 0.28 V, and the line reaches 0.8 V only at 88 uA. An unpowered board C cannot
# lift it (its U9 and R14 sit on a dead +3V3). The cost is 0.33 mA from U9 while EMCON is released.
r("R58", "10k", "EMCON_HW", "GND"); r("R59", "100k", "TX_INHIBIT_n", "GND")
# S-01, 26 September 2026: EMCON_ON is EMCON_HW inverted once for the board (high = EMCON asserted), so the three module
# radio gates, the two WiFi card supply switches and (since fix-up pass 3) the three W_DISABLE1# open drains Q{s}06 add
# one FET gate to EMCON_HW rather than eight logic inputs. With the panel absent R58 holds EMCON_HW low, Q11 is off (its
# threshold is at least 1.0 V, CJ 2N7002) and R513 holds EMCON_ON high: asserted, which is the safe state.
nfet("Q11", "EMCON_HW", "GND", "EMCON_ON", "2N7002: EMCON_ON = NOT EMCON_HW (S-01)"); r("R513", "10k", "EMCON_ON", "+3V3_DEV")
# ================================================================= expanders, secure element, holdover clock, temperature (kit I2C bus, mastered by the panel controller over J_PANEL)
_SEC_MARKS.append(('EXPANDERS, SECURE ELEMENT, HOLDOVER CLOCK, TEMPERATURE (KIT I2C BUS, MASTERED BY THE..', len(P)))
# S-01, 26 September 2026: U6's module radio outputs are REQUESTS now (WL_nDISx_OFF, BT_nDISx_OFF, high = radio off,
# 10 k pull-ups so the power-on state is off), each into its slot's gate U{s}11 and never onto a module pin. S-16, the same day: slot 1's module is the one on the WIFI 2.4 jack
# (ASSEMBLY.md: "one Compute Module's antenna-kit lead (slot 1)", A's J_RF3, dtparam=ant2); slots 2 and 3 keep their
# radios dark (WL_nDIS2/3_OFF and BT_nDIS2/3_OFF high) unless the panel firmware moves the local WiFi to them after losing slot 1.
part("U6", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x20: outputs (switch reset, rail enables, module radio off requests into the EMCON gates, 5G control)", "EXP", {
 "24": "+3V3_DEV", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "GND", "21": "GND", "3": "GND",
 "4": "KSZ_RST", "5": "LIME_SW_EN", "6": "RB_SW_EN", "7": "LORA_ON", "8": "ZB_ON", "9": "CAM_EN", "10": "5G_OFF", "11": "5G_RESET",
 "13": "WL_nDIS1_OFF", "14": "WL_nDIS2_OFF", "15": "WL_nDIS3_OFF", "16": "BT_nDIS1_OFF", "17": "BT_nDIS2_OFF", "18": "BT_nDIS3_OFF", "19": "RB_IEN", "20": "RB_CTRL"}, "C2864778")
part("U7", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x25: inputs (faults, RockBLOCK status) and spares", "EXP", {
 "24": "+3V3_DEV", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "GND", "21": "+3V3_DEV", "3": "+3V3_DEV",
 "4": "LIME_FLT", "5": "RB_FLT", "6": "CAM_FLT", "7": "RB_STATUS", "8": "RB_XMTG", "9": "EXP_SPARE1", "10": "EXP_SPARE2", "11": "EXP_SPARE3",
 "13": "EXP_SPARE4", "14": "EXP_SPARE5", "15": "EXP_SPARE6", "16": "EXP_SPARE7", "17": "EXP_SPARE8", "18": "EXP_SPARE9", "19": "EXP_SPARE10", "20": "EXP_SPARE11"}, "C2864778")
c("C67", "100n", "+3V3_DEV", "GND"); c("C68", "100n", "+3V3_DEV", "GND"); r("R54", "2.2k", "SDA", "+3V3_DEV"); r("R55", "2.2k", "SCL", "+3V3_DEV"); r("R56", "10k", "EXP_INT", "+3V3_DEV")
for i in range(1, 12): part("TP%d" % (40 + i), "Connector", "TestPoint", "EXP_SPARE%d" % i, "TP", {"1": "EXP_SPARE%d" % i})
ic("U8", 8, "ATECC608B-SSHDA-T secure element (I2C 0x60): keys behind ZEROIZE", "SOIC8", {"1": "NC", "2": "NC", "3": "NC", "7": "NC", "4": "GND", "5": "SDA", "6": "SCL", "8": "+3V3_DEV"}, "C1518769"); c("C69", "100n", "+3V3_DEV", "GND")
ic("U9", 8, "DS3231MZ+ holdover clock (I2C 0x68), CR2032 backed", "SOIC8", {"1": "NC", "4": "NC", "2": "+3V3_DEV", "3": "EXP_INT", "5": "GND", "6": "VBAT", "7": "SDA", "8": "SCL"}, "C9866"); c("C70", "100n", "+3V3_DEV", "GND")
# U10 through ic() since 17 Sep 2026: the library TMP117xxDRV symbol has no pin 7, so the "7": "GND" this line always
# carried reached no wire and the thermal pad floats on B19. A numbered connector symbol carries every pad of the land.
ic("U10", 7, "TMP117AIDRVR board temperature under the coolers (I2C 0x49; WSON-6: 1 SCL 2 GND 3 ALERT 4 V+ 5 ADD0 6 SDA 7 thermal pad)", "WSON6", {"1": "SCL", "2": "GND", "3": "EXP_INT", "4": "+3V3_DEV", "5": "+3V3_DEV", "6": "SDA", "7": "GND"}, "C699536"); c("C71", "100n", "+3V3_DEV", "GND")
# ================================================================= the panel ribbon J_PANEL (2x13) to C7's controller and the A22 ribbon J_AB1 (2x13, underside)
_SEC_MARKS.append(("THE PANEL RIBBON J_PANEL (2X13) TO C7'S CONTROLLER AND THE A22 RIBBON J_AB1 (2X13,..", len(P)))
part("F1", "Device", "Polyfuse", "2A hold 1812", "F1812", {"1": "+5V_DEV", "2": "PANEL_5V"})
# PANEL_5V IS THE SAME SHAPE AND IT IS THE ONE PWR-003 IS ABOUT (20 September 2026). It is the 5 V that
# leaves over the panel ribbon for board C, behind a 2.0 A hold, 3.5 A trip polyfuse; +5V_DEV declares F1 as
# a 0.60 A load, so this is that 0.60 A past the fuse. It carries its own 0.8 mm PANEL class because a 0.4 mm
# track is rated 1.23 A at 10 K and the fuse does not trip until 3.5, which is the 17 September finding.
_intent.rail("PANEL_5V", 5.0, 0.60, 0.60, "F1", loads={"J_PANEL": 0.60}, series_of="+5V_DEV", converted=False,
             note="the panel's 5 V behind the 2 A polyfuse F1, out over the panel ribbon at J_PANEL pins 1 "
                  "and 2 to board C")
part("J_PANEL", "Connector_Generic", "Conn_02x13_Odd_Even", "panel ribbon to PCB-C C7 (IDC 2x13): the RP2040 panel controller's USB, the kit I2C, EMCON/ZEROIZE/TX_INHIBIT, HDMI selects, heartbeats, slot enables, power control lines", "IDC26", {
 "1": "PANEL_5V", "2": "PANEL_5V", "3": "GND", "4": "SDA", "5": "SCL", "6": "EXP_INT", "7": "TR_APRS", "8": "EMCON_HW", "9": "GND", "10": "ZEROIZE_HW", "11": "TX_INHIBIT_n", "12": "HDMI_SEL1", "13": "HDMI_SEL2",
 "14": "GND", "15": "USB_PNL_P", "16": "USB_PNL_N", "17": "GND", "18": "HB1", "19": "HB2", "20": "HB3", "21": "SLOT_EN1", "22": "SLOT_EN2", "23": "SLOT_EN3", "24": "PI_SHDN_REQ", "25": "PI_KILL", "26": "SHORE_INHIBIT"})
esd("U37", "USB_PNL_P", "USB_PNL_N", "+3V3_DEV")
# 10 September 2026 (MESHSAT-862): EVERY DIFFERENTIAL PAIR SITS IN ONE COLUMN OF THE HEADER, with ground pins on both sides.
# The three USB pairs were on pins 4/5, 7/8 and 10/11, which on a 2x13 odd-even footprint are DIAGONAL neighbours 3.59 mm
# apart: the pre-router reports "J_AB1 and J_AB1 are 3.6 mm apart" for USB_WALL and cannot lay it, and the two legs would
# be unequal and return-less through the ribbon. An odd pin and the even pin beside it are 2.54 mm apart across the rows,
# which is the geometry J_PANEL already had for USB_PNL. The spare line AB_SPARE loses its seat here (it stays on the A to
# D harness) and B's test point for it goes with it; SHORE_INHIBIT keeps its seat, being a cross-board contract.
# 12 September 2026 (MESHSAT-862, appendix 32.135): THE WALL PAIR LEAVES J_AB1. Measured with the pre-router honest
# about its own copper: J_AB1 carries three pairs, a 2x13 has two end rows, and the third pair's only escape is the
# 1.14 mm channel between the columns, which EXITS AT THE SAME END the end-row pair leaves from. With USB_WALL laid
# first the tool laid USB_D8 on top of it (0.00 mm, twelve DRC items); with either other order USB_WALL fails for
# want of a corridor. Three pairs do not fit one 2x13 whatever the pin map, so the wall pair takes a ribbon of its
# own: a 2x5 with the pair on pins 1/2 (an end row) and eight grounds behind it. J_AB1's pins 5 and 6 become GND.
part("J_AB1", "Connector_Generic", "Conn_02x13_Odd_Even", "A-B interconnect (IDC 2x13, underside, mates A22's J_AB1 at the same case XY)", "IDC26", {
 "1": "USB_D8_P", "2": "USB_D8_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "GND", "9": "PI_SHDN_REQ", "10": "PI_KILL", "11": "SDA", "12": "SCL",
 "13": "EXP_INT", "14": "TR_APRS", "15": "EMCON_HW", "16": "TX_INHIBIT_n", "17": "SLOT_EN1", "18": "SLOT_EN2", "19": "SLOT_EN3", "20": "ZEROIZE_HW", "21": "SHORE_INHIBIT", "22": "GND", "23": "GND", "24": "GND", "25": "USB_E6_P", "26": "USB_E6_N"})
# D-12 (owner ruling, 26 September 2026): the wall data path, bank 3 hub port 3 (USB_WALL), goes to the sealed Glenair
# 233-370 USB receptacle and the USB-C outlet becomes power only. Nothing changes on this board: the pair still leaves
# on J_AB2 pins 1 and 2 with U29 at its hub end, and board A routes it to the Glenair pigtail (drafts/r4-interfaces.md).
part("J_AB2", "Connector_Generic", "Conn_02x05_Odd_Even", "A-B wall-port ribbon (IDC 2x5): the wall USB pair (bank 3 hub port 3) on the END row with eight grounds behind it, to board A's pigtail for the sealed Glenair 233-370 (D-12)", "IDC10", {
 "1": "USB_WALL_P", "2": "USB_WALL_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "GND", "9": "GND", "10": "GND"})
for i, net in enumerate(("+5V_DEV", "+3V3_DEV", "+1V2_KSZ", "+2V5_KSZ", "VBAT", "EMCON_HW", "ZEROIZE_HW", "GNSS_PPS", "SDA", "SCL", "+54V_POE", "POE_DRAIN", "+5V_LIME", "+5V_RB", "+5V_LORA", "+3V3_ZB", "HDMI_SEL1", "HDMI_SEL2",
                        "+3V3_S1A", "+3V3_S1B", "+1V0_S1", "+1V1_S1", "+3V3_S2A", "+3V3_S2B", "+1V0_S2", "+1V1_S2", "+3V3_S3A", "+3V3_S3B", "+1V0_S3", "+1V1_S3"), 2):
    part("TP%d" % i, "Connector", "TestPoint", net, "TP", {"1": net})
# ================================================================= the I/O high-availability control plane (ARCH-PCB-B-IOHA)
_SEC_MARKS.append(('THE I/O HIGH-AVAILABILITY CONTROL PLANE (ARCH-PCB-B-IOHA)', len(P)))
# Three equivalent supervisors. They decide which module owns each bank and never carry a byte of peripheral traffic:
# no USB, no PCIe and no Ethernet payload passes through one. Their decisions reach the fabric only through the 2-of-3
# majority voters below, so a controller wedged in any state is outvoted by the other two and no firmware is trusted.
# Watchdog and brownout are the H743's own IWDG and BOR. That is deliberate: an internal watchdog cannot save a core
# that has wedged with its outputs in the wrong state, and the thing that protects the system from that is the voter,
# not a supervisor chip. Each controller still has its own regulator, its own reset and its own SWD access so it is a
# failure domain of its own, and a shorted controller cannot pull the other two down through a shared rail.
for _tag, _k in (("A", 0), ("B", 1), ("C", 2)):
    U_ = lambda n, _k=_k: "U%d" % (40 + 10 * _k + n)
    R_ = lambda n, _k=_k: "R%d" % (63 + 12 * _k + n)
    C_ = lambda n, _k=_k: "C%d" % (400 + 20 * _k + n)   # the slots take C101 to C394 (100 * s + n), so every global capacitor of this plane lives at 400 and above
    v33 = "+3V3_IOC%s" % _tag
    # W5 TESTACCESS-B (IOHA A4 and A6), 26 September 2026: the LDO's EN is no longer tied to its input. It is pulled up
    # to the device rail through 100 k (AP2112 DS39724 Rev 2-2: VIH 1.5 to 6.0 V, a 3 MOhm internal pull-down, so it sits
    # at about 4.8 V) and a two-pin bench jumper J_IOCOFF_x shorts it to ground: fitted, the controller is unpowered
    # (VIL 0.4 V; the 60 Ohm output discharge empties its rail), removed, it runs. Not fitted in service.
    # Fix-up, 26 September 2026 (round-4 review, minor): the jumper's land is the SMD 1x02 (PH1x2S), for the reason the
    # SWD land below records on 17 September 2026 (a through-hole header in these pockets cost 29 hard violations).
    # In the fitted state EMCON_HW (PC5), HB1 (PA6), HB2 (PA7) and HB3 (PC4) still sit at up to 3.3 V on an H743 whose
    # VDD is then 0 (the round-4 review's O-16). DS12110 Rev 10 answers it: Table 21 gives the input voltage on TT_xx
    # pins an ABSOLUTE maximum of 4.0 V, not a VDD-relative one (FT_xxx: Min(VDD, ...) + 4.0 V, so 4.0 V unpowered),
    # and Table 22 note 3 says "Positive injection is not possible on these I/Os and does not occur for input voltages
    # lower than the specified maximum value", so nothing back-feeds the dark controller. The VDD + 0.3 V of Table 24
    # is an operating condition of a powered part. PA4 and PA5 (HUBRST2/3, IINJ 0/0) are outputs, 100 k to GND.
    ic(U_(0), 5, "AP2112K-3.3 LDO: the private 3.3 V of controller %s, its own branch off the device rail" % _tag, "SOT235",
       {"1": "+5V_DEV", "2": "GND", "3": "IOC%s_LDO_EN" % _tag, "4": "NC", "5": v33})
    r(R_(3), "100k", "+5V_DEV", "IOC%s_LDO_EN" % _tag)
    part("J_IOCOFF_%s" % _tag, "Connector_Generic", "Conn_01x02", "bench jumper, controller %s: fit to hold its LDO off (IOHA A4, A6); not fitted in service" % _tag, "PH1x2S", {"1": "IOC%s_LDO_EN" % _tag, "2": "GND"})
    c(C_(0), "1u", "+5V_DEV", "GND"); c(C_(1), "10u", v33, "GND", "C10u")
    for _n in range(2, 7): c(C_(_n), "100n", v33, "GND")
    m = {}
    for _p, _nm in H743.items():
        if _nm == "VDD": m[_p] = v33
        elif _nm in ("VSS", "VSSA"): m[_p] = "GND"
        elif _nm == "VDDA": m[_p] = v33
        elif _nm == "VREF+": m[_p] = v33
        elif _nm == "VBAT": m[_p] = v33
        elif _nm == "VCAP": m[_p] = "IOC%s_VCAP" % _tag
        else: m[_p] = "NC"
    m.update({14: "IOC%s_RST_n" % _tag, 94: "IOC%s_BOOT0" % _tag,
              12: "IOC%s_XI" % _tag, 13: "IOC%s_XO" % _tag,
              72: "IOC%s_SWDIO" % _tag, 76: "IOC%s_SWCLK" % _tag,
              81: "IOC%s_CAN1_RX" % _tag, 82: "IOC%s_CAN1_TX" % _tag,
              51: "IOC%s_CAN2_RX" % _tag, 52: "IOC%s_CAN2_TX" % _tag,
              22: "SEL1_%s" % _tag, 23: "SEL2_%s" % _tag, 24: "SEL3_%s" % _tag,
              25: "HUBRST1_%s" % _tag, 28: "HUBRST2_%s" % _tag, 29: "HUBRST3_%s" % _tag,
              30: "HB1", 31: "HB2", 32: "HB3",
              # W5-F3 / W6-F4, 26 September 2026: the kit I2C status path (IOHA section 6) sat on pins 35/36, PB1/PB2,
              # which have no I2C function on the H743 or the H753. It moves to pins 92/93, PB6 = I2C1_SCL and PB7 =
              # I2C1_SDA (AF4, DS12110 Rev 10 Table 11), both FT_f/FT_fa (5 V tolerant, Fm+), free on this map.
              33: "EMCON_HW", 34: "IOC%s_LED_A" % _tag, 92: "SCL", 93: "SDA",
              37: "WSEC_%s" % _tag,
              # read-back of the voted bits: without it a voter stuck at one value is invisible to the plane, and the
              # FMEA had no detection for that row. Four inputs, no parts, and the outputs are push-pull already.
              38: "BSEL1", 39: "BSEL2", 40: "BSEL3", 41: "WIFI_SEC"})
    # D-13, 26 September 2026: the symbol, the value and the order line name the part bought, STM32H743VIT6 (C114409).
    synth(U_(1), "STM32H743VI", "STM32H743VIT6 I/O supervisor %s: 2-of-3 quorum on two CAN-FD fabrics, bank ownership and hub reset" % _tag, "LQFP100", m, "C114409")
    c(C_(7), "2.2u", "IOC%s_VCAP" % _tag, "GND"); c(C_(8), "2.2u", "IOC%s_VCAP" % _tag, "GND")
    r(R_(0), "10k", "IOC%s_RST_n" % _tag, v33); c(C_(9), "100n", "IOC%s_RST_n" % _tag, "GND")
    r(R_(1), "10k", "IOC%s_BOOT0" % _tag, "GND")
    part("Y%d" % (2 + _k), "Device", "Crystal_GND24", "25 MHz 3225 (CAN-FD bit timing needs a crystal, not the HSI)", "XTAL",
         {"1": "IOC%s_XI" % _tag, "3": "IOC%s_XO" % _tag, "2": "GND", "4": "GND"}, "C164047")
    c(C_(10), "18p", "IOC%s_XI" % _tag, "GND", "C0402"); c(C_(11), "18p", "IOC%s_XO" % _tag, "GND", "C0402")
    r(R_(2), "1k", v33, "IOC%s_LED_K" % _tag); led("LED%d" % (40 + _k), "green IOCTRL %s alive" % _tag, "IOC%s_LED_A" % _tag, "IOC%s_LED_K" % _tag)
    # A THROUGH-HOLE HEADER ON THE UNDERSIDE IS A KEEP-OUT ON THE FRONT THAT NOTHING DECLARES (17 September
    # 2026): at a 2.0 mm fine-pitch margin the packer put five front parts over these five pins, 29 hard
    # violations, and the schematic calls them SWD PADS. A surface-mount land is what the words already said.
    ic(U_(2), 5, "SWD pads, controller %s: 3V3 SWDIO SWCLK NRST GND" % _tag, "PH1x5S",
       {"1": v33, "2": "IOC%s_SWDIO" % _tag, "3": "IOC%s_SWCLK" % _tag, "4": "IOC%s_RST_n" % _tag, "5": "GND"})
    # two CAN-FD transceivers on two INDEPENDENT fabrics, so neither a broken bus nor a failed transceiver can take both
    # heartbeat paths from a controller. TI TCAN334D, 3.3 V, CAN FD to 5 Mbps: https://www.ti.com/product/TCAN334
    for _f, _rx, _tx, _un in (("A", "IOC%s_CAN1_RX" % _tag, "IOC%s_CAN1_TX" % _tag, 3), ("B", "IOC%s_CAN2_RX" % _tag, "IOC%s_CAN2_TX" % _tag, 4)):
        _seg = "1" if _tag == "A" else ""   # controller A sits on its own segment, behind the break links below
        ic(U_(_un), 8, "TCAN334D CAN-FD transceiver, controller %s on heartbeat fabric %s" % (_tag, _f), "SOIC8",
           {"1": _tx, "2": "GND", "3": v33, "4": _rx, "5": "NC", "6": "CANL_%s%s" % (_f, _seg), "7": "CANH_%s%s" % (_f, _seg), "8": "GND"}, "C2871143")
# Each fabric is terminated at BOTH physical ends, which are controller A's pocket and controller C's: a bus terminated
# once, in the middle, reflects off both ends. Split termination (two 60R4 to a 4.7 nF) at each end, so 120.8 ohm twice.
# The two fabrics keep separate termination so a shorted terminator on one cannot load the other.
# the slots take R101 to R394 (100 * s + n), so the plane's shared passives live at 470 and above
# W5 TESTACCESS-B (IOHA A7, "cut fabric A, then fabric B"), 26 September 2026: each fabric has a break link between
# controller A's pocket and the rest, two 0 Ohm per fabric (CANH and CANL). Removed, controller A and its end's
# termination are cut off that fabric; fitted, the bus is as before. Controller A's segment is CANH_x1/CANL_x1 and
# keeps the west termination R470 to R473; B, C and the east termination R504 to R507 stay on CANH_x/CANL_x.
r("R470", "60R4 1%", "CANH_A1", "CANT_A"); r("R471", "60R4 1%", "CANT_A", "CANL_A1"); c("C460", "4.7n", "CANT_A", "GND")
r("R472", "60R4 1%", "CANH_B1", "CANT_B"); r("R473", "60R4 1%", "CANT_B", "CANL_B1"); c("C461", "4.7n", "CANT_B", "GND")
for _r0, _f in (("R508", "A"), ("R511", "B")):
    r(_r0, "0R (break link: remove to cut fabric %s between controller A and B/C, IOHA A7)" % _f, "CANH_%s1" % _f, "CANH_%s" % _f, "R", "C21189")
    r("R%d" % (int(_r0[1:]) + 1), "0R (break link: remove to cut fabric %s between controller A and B/C, IOHA A7)" % _f, "CANL_%s1" % _f, "CANL_%s" % _f, "R", "C21189")
r("R504", "60R4 1%", "CANH_A", "CANT2_A"); r("R505", "60R4 1%", "CANT2_A", "CANL_A"); c("C506", "4.7n", "CANT2_A", "GND")
r("R506", "60R4 1%", "CANH_B", "CANT2_B"); r("R507", "60R4 1%", "CANT2_B", "CANL_B"); c("C507", "4.7n", "CANT2_B", "GND")

# ----------------------------------------------------------------- the 2-of-3 majority voters
_SEC_MARKS.append(('THE 2-OF-3 MAJORITY VOTERS', len(P)))
# One voter per control bit: out = AB + BC + CA, three AND gates and two OR gates. A controller stuck high or low is a
# minority of one and cannot move the bit, which is what makes the split-brain guarantee a property of the circuit and
# not of firmware. 74LVC08 and 74LVC32 share a pinout and the EMCON chain already uses the 08, so this adds no new
# family. The bank select and the hub reset are voted. The mux output enable is NOT: it is generated from a select
# transition by the edge detector below, so break-before-make is hardware too.
# The hub reset is voted through a FET, not driven directly. A voter output is push-pull and its inputs sit low when the
# control plane is dark, so wiring it straight to the active-low HUB{s}_RST_n would hold every hub in reset whenever the
# controllers are absent, which is the opposite of a safe state. The voted signal instead gates a 2N7002 that pulls the
# reset down, exactly as KSZ_RST is done on this board, so the existing RC holds each hub OUT of reset by default and a
# controller majority can still recycle a wedged one. Read back from the netlist before this was noticed.
VOTED = [("BSEL1", "SEL1"), ("BSEL2", "SEL2"), ("BSEL3", "SEL3"),
         ("HUBRST1_VOTE", "HUBRST1"), ("HUBRST2_VOTE", "HUBRST2"), ("HUBRST3_VOTE", "HUBRST3"),
         ("WIFI_SEC", "WSEC")]
GATE = [(1, 2, 3), (4, 5, 6), (10, 9, 8), (13, 12, 11)]   # (inA, inB, out) of the four gates in a 14-pin quad
_pkg = {}
def _gate(kind):
    """Hand out the next free gate of `kind`, opening a new quad package when the current one is full."""
    n = _gate.n.setdefault(kind, 0); _gate.n[kind] = n + 1
    base = 70 if kind == "AND" else 76
    ref = "U%d" % (base + n // 4)
    d = _pkg.setdefault(ref, {"7": "GND", "14": "+3V3_DEV", "_kind": kind})
    return ref, GATE[n % 4]
_gate.n = {}
for out, src in VOTED:
    a, b, cc = ("%s_A" % src, "%s_B" % src, "%s_C" % src)
    ab, bc, ca = ("%s_AB" % src, "%s_BC" % src, "%s_CA" % src)
    o1 = "%s_O1" % src
    for ins, o in ((( a, b), ab), ((b, cc), bc), ((cc, a), ca)):
        ref, (pa, pb, py) = _gate("AND")
        _pkg[ref].update({str(pa): ins[0], str(pb): ins[1], str(py): o})
    for ins, o in (((ab, bc), o1), ((o1, ca), out)):
        ref, (pa, pb, py) = _gate("OR")
        _pkg[ref].update({str(pa): ins[0], str(pb): ins[1], str(py): o})
for ref in sorted(_pkg, key=lambda r: int(r[1:])):
    d = _pkg[ref]; kind = d.pop("_kind")
    for pin in [str(p) for g in GATE for p in g]:
        d.setdefault(pin, "GND" if pin in ("1", "2", "4", "5", "10", "9", "13", "12") else "NC")
    part(ref, "Connector_Generic", "Conn_01x14",
         "SN74LVC%sAPWR quad 2-input %s: the 2-of-3 majority voters of the I/O control plane" % ("08" if kind == "AND" else "32", kind),
         "TSSOP14", d, "C465737" if kind == "AND" else "C352974")
    c("C%d" % (470 + int(ref[1:]) - 70), "100n", "+3V3_DEV", "GND")
for _b in (1, 2, 3):
    nfet("Q%d" % (2 + _b), "HUBRST%d_VOTE" % _b, "GND", "HUB%d_RST_n" % _b, "2N7002: a voted majority pulls the bank's hub into reset")
    r("R%d" % (476 + _b), "100k", "HUBRST%d_VOTE" % _b, "GND")
# Every controller output that reaches a voter is pulled down, so a controller that is absent, unpowered or still in
# reset presents its GPIOs as high impedance and the voter reads a definite NO rather than an undefined CMOS input.
CTRL_BITS = ("SEL1", "SEL2", "SEL3", "HUBRST1", "HUBRST2", "HUBRST3", "WSEC")
for _j, _bit in enumerate(CTRL_BITS):
    for _i, _t in enumerate(("A", "B", "C")):
        r("R%d" % (480 + 3 * _j + _i), "100k", "%s_%s" % (_bit, _t), "GND")
# W5 TESTACCESS-B, 26 September 2026: the pads the IOHA kill tests need (ARCH-PCB-B-IOHA section 13). A ground pad in
# each controller pocket (every scope reading, A10); the voted lines and the mux enables (A8 forces a voter output,
# A10 scopes BOE against BSEL); every controller's own seven outputs (A5 pulls a held controller's GPIOs the wrong way);
# CANH and CANL of each fabric on the B/C segment (A7 scopes it, or shorts it to take the fabric down).
_tp = 501
for _net in (["GND"] * 3 + ["BSEL1", "BSEL2", "BSEL3", "BOE1_n", "BOE2_n", "BOE3_n", "WIFI_SEC", "HUBRST1_VOTE", "HUBRST2_VOTE", "HUBRST3_VOTE"]
             + ["%s_%s" % (_bit, _t) for _bit in CTRL_BITS for _t in ("A", "B", "C")] + ["CANH_A", "CANL_A", "CANH_B", "CANL_B"]):
    _TP(_tp, _net); _tp += 1

# Break before make, in hardware. Any change of a voted select charges an RC through an exclusive-or against the
# undelayed select, which raises the mux output enable for the RC time and drops it again once both sides agree. The
# muxes are therefore disconnected across every transition without the firmware having to sequence anything, and with
# no transition in progress the enable sits low, which is normal operation.
part("U80", "Connector_Generic", "Conn_01x14", "74LVC86APW quad exclusive-or: break-before-make on each bank's select", "TSSOP14",
     {"7": "GND", "14": "+3V3_DEV", "1": "BSEL1", "2": "BSEL1_D", "3": "BOE1_n", "4": "BSEL2", "5": "BSEL2_D", "6": "BOE2_n",
      "10": "BSEL3", "9": "BSEL3_D", "8": "BOE3_n", "13": "GND", "12": "GND", "11": "NC"}, "C350562")
c("C480", "100n", "+3V3_DEV", "GND")
for _b in (1, 2, 3):
    r("R%d" % (473 + _b), "10k", "BSEL%d" % _b, "BSEL%d_D" % _b); c("C%d" % (480 + _b), "10n", "BSEL%d_D" % _b, "GND")

# ----------------------------------------------------------------- the shared WiFi antennas and their changeover
_SEC_MARKS.append(('THE SHARED WIFI ANTENNAS AND THEIR CHANGEOVER', len(P)))
# The two AW7915-AED cards (slot 1 and slot 3) feed the SAME pair of P2P antennas through two Skyworks SKY13351-378LF
# SPDT switches, one per antenna chain. Data sheet 201132I: 20 MHz to 6.0 GHz, insertion loss 0.35 dB typical below
# 3 GHz and 0.50 dB typical from 3 to 6 GHz, isolation 24 dB, IP0.5dB +30 dBm at VCTL 2.7 V against the card's +20 dBm,
# control 0 V and 1.8 to 5.0 V on VCTL1 or VCTL2, and every RF port must be DC blocked, which is what the 22 pF do.
# Only one radio is live at a time, which is what failover needs; this buys redundancy, not capacity.
# The safe state is the primary card: WIFI_SEC is a VOTED bit and sits low with the control plane dark, so VCTL2 is low
# while VCTL1 is held high by its pull-up through the open Q10, and the switch rests on OUTPUT1, the slot 1 card.
r("R510", "10k", "WIFI_PRI", "+3V3_DEV")
nfet("Q10", "WIFI_SEC", "GND", "WIFI_PRI", "2N7002: the changeover's complement, so a voted WIFI_SEC moves both chains at once")
for _ch, _u, _c0 in (("A", "U82", 500), ("B", "U83", 503)):
    part("J_W1%s" % _ch, "Connector", "Conn_Coaxial", "U.FL: MHF4 pigtail from the slot 1 WiFi card, chain %s" % _ch, "UFL", {"1": "W1%s_CARD" % _ch, "2": "GND"}, "C434808")
    part("J_W3%s" % _ch, "Connector", "Conn_Coaxial", "U.FL: MHF4 pigtail from the slot 3 WiFi card, chain %s" % _ch, "UFL", {"1": "W3%s_CARD" % _ch, "2": "GND"}, "C434808")
    part("J_WO%s" % _ch, "Connector", "Conn_Coaxial", "U.FL: pigtail to A22's P2P jack, chain %s" % _ch, "UFL", {"1": "W%s_ANT" % _ch, "2": "GND"}, "C434808")
    c("C%d" % _c0, "22p", "W1%s_CARD" % _ch, "SW%s_O1" % _ch, "C0402")
    c("C%d" % (_c0 + 1), "22p", "W3%s_CARD" % _ch, "SW%s_O2" % _ch, "C0402")
    c("C%d" % (_c0 + 2), "22p", "W%s_ANT" % _ch, "SW%s_IN" % _ch, "C0402")
    ic(_u, 6, "SKY13351-378LF SPDT antenna changeover, chain %s: OUTPUT1 the slot 1 card, OUTPUT2 the slot 3 card" % _ch, "MLPD6",
       {"1": "SW%s_O1" % _ch, "2": "GND", "3": "SW%s_O2" % _ch, "4": "WIFI_SEC", "5": "SW%s_IN" % _ch, "6": "WIFI_PRI"}, "C129189")

RAILS = ["+5V_DEV", "+3V3_DEV", "+1V2_KSZ", "+2V5_KSZ", "VBAT", "+54V_POE", "+5V_LIME", "+5V_RB", "+5V_LORA", "+3V3_ZB", "+5V_HDMI", "+5V_CAM", "VBUS_QMX", "PANEL_5V", "GND", "POE_P", "POE_DRAIN", "GNSS_3V3", "ZBA_3V3", "ZBB_3V3", "RB_3V3"]
for s in (1, 2, 3): RAILS += ["+5V_S%d" % s, "+3V3_S%dA" % s, "+3V3_S%dB" % s, "+1V0_S%d" % s, "+1V1_S%d" % s, "+3V3_CM%d" % s, "+1V8_CM%d" % s, "VBUS_FLASH%d" % s,
                               "+3V3_M2C%d" % s]   # 26 September 2026: the socket side of the Kelvin shunt feeds the socket's power pins
for i, net in enumerate(RAILS, 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})

# ----------------------------------------------------------------- emit (as B15)
POWER = {"GND": ("power", "GND")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
byref = {p["ref"]: p for p in P}
def refs_matching(pred): return [p["ref"] for p in P if pred(p["ref"])]
SECTIONS = [("SHARED POWER: DEVICE RAIL, +3V3_DEV, KSZ CORE RAILS, CR2032", ["J_5V_DEV", "D1", "C1", "C2", "U25", "L1", "C3", "C4", "C5", "C6", "U26", "L2", "C7", "C8", "C9", "C10", "C11", "R1", "R2", "U27", "C12", "C13", "BT1"] + ["TP%d" % k for k in range(2, 32)] + ["TP%d" % k for k in range(41, 52)] + ["#FLG%02d" % k for k in range(1, len(RAILS) + 1)])]
for s in (1, 2, 3):
    mine = lambda ref, s=s: (ref[0] in "RCLQDUY" and ref[1:].isdigit() and 100 * s <= int(ref[1:]) < 100 * (s + 1)) or ref in ("U3%dA" % (s - 1), "U3%dB" % (s - 1)) or ref.startswith("LED%d" % s) and len(ref) == 5 or ref.endswith("%d" % s) and ref.startswith(("J_5V_S", "J_FAN", "J_FLASH", "J_RPIBOOT", "J_DBG", "J_SPI", "J_M2N", "J_M2C")) or (s == 2 and ref in ("J_SIM1", "J_SIM2")) or ref in SLOT_EXTRA[s]
    SECTIONS.append(("SLOT S%d: COMPUTE MODULE 5, PCIe SWITCH, USB 3 HUB, M.2 SOCKETS, RAILS, SUPPORT" % s, refs_matching(mine)))
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
for _k, (_t, _s) in enumerate(_SEC_MARKS):   # one section per heading of the shared area, the parts registered under it
    _e = _SEC_MARKS[_k + 1][1] if _k + 1 < len(_SEC_MARKS) else len(P)
    _refs = [p["ref"] for p in P[_s:_e] if p["ref"] not in placed_refs]
    if _refs: SECTIONS.append(("SHARED: " + _t, _refs))
_rest = [p["ref"] for p in P if p["ref"] not in {r for _, rs in SECTIONS for r in rs}]
if _rest: SECTIONS.append(("SHARED: THE REST", _rest))
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
_intent.bypass("C4", "U25", "2", "+5V_DEV")
_intent.bypass("C5", "U25", "1", "+3V3_DEV")
_intent.bypass("C6", "U25", "1", "+3V3_DEV")
_intent.bypass("C12", "U27", "5", "+2V5_KSZ")
_intent.bypass("C13", "U27", "1", "+3V3_DEV")
_intent.bypass("C36", "U5", "1", "+3V3_DEV")
_intent.bypass("C37", "U5", "1", "+3V3_DEV")
_intent.bypass("C38", "U5", "1", "+3V3_DEV")
_intent.bypass("C69", "U8", "8", "+3V3_DEV")
_intent.bypass("C70", "U9", "2", "+3V3_DEV")
_intent.bypass("C71", "U9", "2", "+3V3_DEV")
import schlayout, time as _time
PAPER, NPAGES, NCOLS, NROWS = schlayout.run(P, SECTIONS, POWER, _intent._I["bypass"], {"date": _time.strftime("%Y-%m-%d")}, os.environ.get("PHASE", ""), 'PCB-B COMPUTE')   # 15 Sep 2026: one A3 page per block, real wiring (32.196)
out = kisch.out
print("layout: %d A3 pages on a %d x %d sheet -> paper %s" % (NPAGES, NCOLS, NROWS, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper %s)\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-B COMPUTE") (date "%s")' % _time.strftime("%Y-%m-%d") + ' (rev "A") (company "MeshSat") (comment 1 "Phase ' + (os.environ.get("PHASE") or "?") + ' schematic (three CM5 slots on a PCIe/USB/Ethernet/HDMI fabric, appendix 32.52 and 32.58), generated by tools/gen_sch_b.py. Netlist style: every pin carries a stub and a label; GND pins carry power symbols."))\n'
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

# the decoupling written outside the converter blocks, which declare their own (8 Sep 2026, MESHSAT-862 Stage C):
# each capacitor sits directly after the part it serves and is filtered to supply pins; intent.py refuses a wrong entry.
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
