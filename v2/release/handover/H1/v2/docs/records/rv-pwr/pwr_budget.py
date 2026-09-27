#!/usr/bin/env python3
"""Power and thermal feasibility model for v2/docs/feasibility/POWER-THERMAL.md (MESHSAT-1357, stream PWR, review of
26 September 2026 section 4). PROVISIONAL: nothing in this kit has been built, powered or measured. Stdlib only, runs
in well under a second on the runner.

What it does, and what changed against the W2 round-2 model (`fnd/w2` drafts/_scratch/budget_r2.py, the figures
CONOPS.md section 4a carries on main, unchanged at 01469100):

1. Every load carries THREE values per power state, in watts at the load's own supply pins: LOW (the lowest figure a
   document supports, else the planning value), PLAN (the figure used for the headline), HIGH (the highest figure a
   document supports: a maker's maximum, a port or rail contract, or a declared peak). A tier says what backs PLAN:
     S  a primary document gives the number (datasheet, maker's page), read by this stream or cited with its clause;
     R  a primary document bounds the load and PLAN sits inside the bound by a stated assumption (duty, workload);
     D  a design declaration in a generator (`gen_sch_*.py`), not a document;
     T  a placeholder with no document; its bound, if any, is in HIGH.
2. Conversion is no longer one flat floor per converter. Each converter's efficiency is read off its own datasheet
   plot at the output current the state asks of it (points below, each with its figure), interpolated in input
   voltage between the two plotted VIN curves: LOW uses VIN 12 V, PLAN 14.4 V (the 4S nominal), HIGH 16.8 V (full
   pack, the worst point of the pack range for these bucks). Where the datasheet plots nothing near the operating
   point the generator's declared floor is used and the line says NOT PLOTTED.
3. The loads the W2 table left TBD now carry sourced figures or bounds: AW7915-AED (AsiaRF), LimeSDR Mini v2.4
   (Lime Microsystems), a representative industrial 2242 NVMe (Advantech SQFlash 720-D, Cervoz T405), the fans
   (Sunon catalogue 240-A), the KSZ9897R (Microchip DS00002330D Table 6-1), the TUSB8041 (TI SLLSEE4E 7.7), the
   STM32H743 supervisors (ST DS12110 Rev 10 Table 30), the E72 (Ebyte manual 2.2), the PCIe switch split by rail
   (Diodes DS40068 Rev 5-2 Table 12-8), the RM520N-GL at the table's own 3.7 V condition.
4. The architecture rules W2 did not apply: only one WiFi link card is live (ARCH-PCB-B-IOHA.md line 209 and the
   table at line 324: card 2 is "standby, radio disabled"); the reduced mode's one module is slot 3 because the LoRa
   mesh is on slot 3's SPI (V2-SPEC.md line 32); the mixer fans run in every lid-open state because the fans-on
   conductance of appendix 32.53 assumes them.
5. Second cycle (26 Sep 2026, the checker's two blocking items): PS-BUSY is modelled as a sustained bound; the two
   outlets are loads whose delivered watts leave the enclosure; every allowed-mode row is judged against the declared
   CONTINUOUS pack current (10 A) at every stack voltage down to the gauge's 2.50 V per cell, the 18 A peak, and the
   cells' 60 C discharge and 45 C charge windows with the same pack model as the thermal ceilings; the D-11 rest
   voltages count the distribution drop once (battery W already carries it); the cells' own I2R now heats the inside
   air as well as the cells; and on shore the front end's and charger's loss on the loads' power is counted.
6. Third cycle (26 Sep 2026, the checker's three blocking items): the distribution resistance carries the chemical
   fuse F2 (Eaton SCF9550-30-05, in series on main since faf8c981) at its 2.5 mOhm maximum; the PA keyed on its own
   over PS-IDLE-SPEC and PS-TYP, and the pack heater overlay, are rows of the allowed-mode table; a PA-only floor is
   derived the way D-11's is; and the D-11 basis is also computed with the heater on, to show what the rule that
   turns it off during a key-down protects.
7. Fifth cycle (26 Sep 2026, the checker's blocking item on 32.56; main moved to b69f20db, then 01469100): the record's
   second key-down figure, appendix 32.56 line 2940 ("a 20 s key-down at 45 W warms the local patch about 15 K"),
   is set against the RA30H1317M1's case rating (record d11.pa_case_record_3256); main's pack path since 458b2873
   carries board A's 5 mOhm RSR shunt R17 in the discharge path (S-04), and what that moves is the record
   d11.main_pack_path_R17; the fans-off row carries the fans' own power, which a failed fan does not draw.
   The generator citations are re-anchored at 01469100. Every table is still computed on the boards as generated at
   1f614233 (R_DIST without R17, AP64500 curves for +5V_S2 and +5V_DEV, the unregulated heater mat).

Usage: python3 pwr_budget.py [out.json]   (prints the tables POWER-THERMAL.md quotes)
"""
import json
import math
import sys

# ------------------------------------------------------------------------------------------------ efficiency curves
# Points (output current A, efficiency %) read by this stream off the rendered datasheet pages, TA = 25 C, typical.
CURVES = {
    # Diodes AP64500, DS41979 Rev. 5, Figure 4 (VIN 12 V) and Figure 5 (VIN 24 V), 500 kHz; VOUT 5 V with 3.6 uH.
    "AP64500_5V": {12: [(0.01, 85.0), (0.03, 86.3), (0.1, 86.7), (0.2, 86.3), (0.3, 87.5), (0.5, 89.2), (0.7, 90.5),
                        (1.0, 92.0), (2.0, 94.0), (3.0, 93.5), (5.0, 91.5)],
                   24: [(0.01, 72.6), (0.03, 74.2), (0.1, 74.5), (0.2, 76.5), (0.3, 78.5), (0.5, 83.0), (0.7, 84.0),
                        (1.0, 87.0), (2.0, 89.5), (3.0, 90.0), (5.0, 88.0)]},
    # the same figures, VOUT 3.3 V with 3.3 uH. The slot bucks run from 5.1 V, which is NOT PLOTTED: the VIN 12 V
    # curve is used for every scenario, which is conservative (a buck loses less at a smaller step-down).
    "AP64500_3V3": {12: [(0.01, 80.0), (0.03, 81.7), (0.1, 82.0), (0.2, 82.0), (0.3, 84.5), (0.5, 87.5), (0.7, 88.3),
                         (1.0, 90.0), (2.0, 91.5), (3.0, 91.0), (5.0, 88.0)]},
    # Diodes AP63200/1/3/5, DS41326 Rev. 3, Figure 4 (VIN 12 V) and Figure 5 (VIN 24 V).
    "AP632_5V": {12: [(0.002, 84.0), (0.01, 90.0), (0.03, 90.9), (0.1, 92.0), (0.2, 92.8), (0.3, 93.5), (0.5, 94.4),
                      (0.7, 94.5), (1.0, 93.5), (2.0, 91.0)],
                 24: [(0.002, 74.0), (0.01, 82.0), (0.03, 83.0), (0.1, 84.5), (0.2, 86.0), (0.3, 87.5), (0.5, 89.5),
                      (0.7, 90.5), (1.0, 91.0), (2.0, 87.5)]},
    "AP632_3V3": {12: [(0.002, 79.5), (0.01, 86.0), (0.03, 87.0), (0.1, 88.5), (0.2, 89.8), (0.3, 91.5), (0.5, 92.5),
                       (0.7, 92.7), (1.0, 92.0), (2.0, 88.3)]},       # U25 runs from 5 V: NOT PLOTTED, VIN 12 V used
    # TI LM5176, SNVSAI1D, Figure 6-2 (VOUT 12 V, 300 kHz, 4.7 uH, TI's EVM parts). Below 0.2 A (VIN 12) and 0.4 A
    # (VIN 24) nothing is plotted; the lowest plotted point is used and the line says so.
    "LM5176_12V": {12: [(0.2, 86.0), (0.3, 92.5), (0.5, 95.0), (1.0, 97.0), (2.0, 98.3), (3.0, 98.5), (6.0, 98.6)],
                   24: [(0.4, 80.0), (0.5, 84.0), (0.8, 90.0), (1.0, 92.5), (1.5, 94.5), (2.0, 95.3), (3.0, 96.3),
                        (4.0, 96.8), (6.0, 97.2)]},
}
VIN_OF = {"lo": 12.0, "plan": 14.4, "hi": 16.8}      # pack voltage per scenario (4S: 3.0, 3.6, 4.2 V per cell)
# Cells to VBAT. W2 A10's 20 mOhm (three 2.52 mOhm blades, two 0.69 mOhm FETs, the 2 mOhm shunt VERIFIED; about 9 mOhm
# of lead and contacts INFERRED) predates the chemical fuse F2, Eaton SCF9550-30-05, which is in series between the
# blade and the charge FET on main (gen_sch_p.py lines 64 to 76 and 247 to 289 at 01469100; fuse DCR 1.0 to 2.5 mOhm, ELX1135).
# Third cycle: F2 is carried at its 2.5 mOhm maximum, the conservative direction for every limit this model judges.
R_W2, R_F2 = 0.020, 0.0025
R_DIST = R_W2 + R_F2
# Fifth cycle: on main since 458b2873 (S-04: board A's loads moved to the charger's VSYS) the pack's DISCHARGE
# current also passes board A's RSR shunt R17, "5mOhm 1% 2512", rated 3 W (gen_sch_a.py lines 26 to 37 and 716 to
# 722 at 01469100). Main's pack path is R_DIST + 5 mOhm. Every table here stays at R_DIST (the boards as generated
# at 1f614233); the record d11.main_pack_path_R17 gives what the extra 5 mOhm moves.
R_R17 = 0.005
R_DIST_MAIN = R_DIST + R_R17


def _interp_log(pts, i):
    if i <= pts[0][0]:
        return pts[0][1]
    if i >= pts[-1][0]:
        return pts[-1][1]
    for (a, ea), (b, eb) in zip(pts, pts[1:]):
        if a <= i <= b:
            t = (math.log(i) - math.log(a)) / (math.log(b) - math.log(a))
            return ea + t * (eb - ea)


def eff_curve(name, vin, iout):
    c = CURVES[name]
    if len(c) == 1:
        return _interp_log(list(c.values())[0], iout) / 100.0
    e12, e24 = _interp_log(c[12], iout), _interp_log(c[24], iout)
    t = min(max((vin - 12.0) / 12.0, 0.0), 1.0)
    return (e12 + t * (e24 - e12)) / 100.0


# ------------------------------------------------------------------------------------------------------- the tree
# name: (kind, parent, vout, param, note). kind: curve (param = curve name), fixed (param = efficiency), ldo, pass.
NODES = {
    "VBAT": ("root", None, 14.4, None, "the 4S system node"),
    "S1": ("curve", "VBAT", 5.1, "AP64500_5V", "slot 1 rail, AP64500 U4 (gen_sch_a.py:106-109 at 01469100)"),
    "S2": ("curve", "VBAT", 5.1, "AP64500_5V", "slot 2 rail, AP64500 U5 at 1f614233 (the curve used); an LM5176 stage on main since 458b2873 (F-PR-04, gen_sch_a.py:873), 5.1 V NOT PLOTTED"),
    "S3": ("curve", "VBAT", 5.1, "AP64500_5V", "slot 3 rail, AP64500 U6"),
    "DEV": ("curve", "VBAT", 5.1, "AP64500_5V", "device rail, AP64500 U7 at 1f614233 (the curve used); an LM5176 stage on main since 458b2873 (F-PR-04, gen_sch_a.py:881)"),
    "A3V3": ("fixed", "VBAT", 3.3, 0.88, "board A logic, TPS62933 U12: 3.3 V NOT PLOTTED (SLUSEA4D plots 5 V), declared floor"),
    "PA": ("curve", "VBAT", 13.8, "LM5176_12V", "+13V8_PA, LM5176 U13 (VOUT 13.8 V against the plotted 12 V)"),
    "HF": ("curve", "VBAT", 12.0, "LM5176_12V", "+12V_HF, LM5176 U15"),
    "MON": ("pass", "VBAT", 14.4, None, "Xenarc behind the TPS259631 eFuse U21 (RON loss ignored)"),
    "E5V": ("curve", "VBAT", 5.0, "AP632_5V", "board E always-on 5 V, AP63205 U12 on CELL_F (gen_sch_e.py:491)"),
    "E3V3": ("ldo", "E5V", 3.3, None, "board E 3.3 V, TLV75533 LDO: Vout/Vin"),
    "EFAN": ("pass", "VBAT", 14.4, None, "mixer fans on CELL_F, low-side PWM (gen_sch_e.py:571)"),
    "D3V3": ("curve", "DEV", 3.3, "AP632_3V3", "+3V3_DEV, AP63203 U25 from 5 V (gen_sch_b.py:833)"),
    "KSZ2V5": ("ldo", "D3V3", 2.5, None, "KSZ AVDDH, AP2112K-2.5 U27 from 3.3 V"),
    "KSZ1V2": ("fixed", "DEV", 1.2, 0.85, "KSZ AVDDL and DVDDL, TPS62933 U26: 1.2 V NOT PLOTTED, declared floor"),
    "HUB1V1": ("fixed", "DEV", 1.1, 0.85, "three hub cores, TPS62933 U106/U206/U306: NOT PLOTTED, declared floor"),
    "IOC": ("ldo", "DEV", 3.3, None, "three supervisor LDOs, AP2112K-3.3 U40/U50/U60 from 5.1 V"),
    "DEVP": ("pass", "DEV", 5.1, None, "eFuses, load switches and polyfuses on +5V_DEV (LimeSDR, RockBLOCK, LoRa, camera, panel, QMX USB, HDMI, D8, bridges)"),
    "ZB": ("pass", "D3V3", 3.3, None, "+3V3_ZB behind TPS22810 U22"),
    # the two accessory outlets: their DELIVERED power leaves the enclosure, their converter loss stays inside
    "POE": ("fixed", "VBAT", 54.0, 0.88, "+54V_POE, LM5176 U16: NOT PLOTTED at 54 V, declared floor (gen_sch_a.py:124)"),
    "PDO": ("fixed", "VBAT", 15.0, 0.93, "USB-C PD outlet stage, LM5176 behind TPS25740A: NOT PLOTTED, declared floor (gen_sch_a.py:978-980)"),
    # the pack heater mat on unregulated VBAT behind the eFuse U22 (at 1f614233: gen_sch_a.py line 528, ILM 1.0 A),
    # enabled by the software expander pin HEAT_EN (U27 pin 6); on main since 458b2873 it is regulated to 12 V
    # (TPS62933 U33, gen_sch_a.py line 1065, behind U22 at line 1064; HEAT_EN at line 1119, all at 01469100)
    "HEAT": ("pass", "VBAT", 14.4, None, "pack heater mat on VBAT behind the eFuse U22 (the unregulated mat of 1f614233)"),
}
for s in (1, 2, 3):
    NODES["S%dA" % s] = ("curve", "S%d" % s, 3.3, "AP64500_3V3", "slot %d card socket 3.3 V, AP64500 U%d03" % (s, s))
    NODES["S%dB" % s] = ("curve", "S%d" % s, 3.3, "AP64500_3V3", "slot %d NVMe and switch 3.3 V, AP64500 U%d04" % (s, s))
    NODES["S%dC" % s] = ("fixed", "S%d" % s, 1.0, 0.85, "slot %d PCIe switch core, TPS62933 U%d05: NOT PLOTTED" % (s, s))

STATES = ["IDLE", "IDLESPEC", "TYP", "BUSY", "RED", "REDB", "EMCON", "ALLTX"]
STATE_NAME = {"IDLE": "PS-IDLE", "IDLESPEC": "PS-IDLE-SPEC", "TYP": "PS-TYP", "BUSY": "PS-BUSY", "RED": "PS-RED",
              "REDB": "PS-RED-b", "EMCON": "PS-EMCON", "ALLTX": "PS-ALLTX"}
LOADS = []   # (name, node, {state: (lo, plan, hi, tier)}, source)
# PS-BUSY (CONOPS.md line 253 at 01469100: "three modules loaded, 5G and WiFi link passing traffic, Iridium and LoRa sending";
# battery W TBD there for want of duty cycles). Added 26 Sep 2026 so that section 7.1 can judge it. Every load is at
# its PS-TYP figure unless it names a BUSY one, and the loads that do are taken at 100 percent duty (a SUSTAINED
# BOUND, not a duty-cycle estimate): each CM5 at board B's declared 1.6 A, each NVMe at the Cervoz active figure,
# the live WiFi card at the top of AsiaRF's average, the 5G module at LTE CA, the RockBLOCK at its maximum and the
# LoRa module transmitting.
OUTSIDE = {"PoE outlet (delivered outside)", "USB-C outlet (delivered outside)"}


def load(name, node, source, **states):
    d = {}
    for st in STATES:
        if st == "BUSY" and "BUSY" not in states:
            v = states.get("TYP", states.get("ALL", (0.0, 0.0, 0.0, "X")))
        else:
            v = states.get(st, states.get("ALL", (0.0, 0.0, 0.0, "X")))
        d[st] = v
    LOADS.append((name, node, d, source))


def same(v, tier):
    return (v, v, v, tier)


def up(v_lo, v_plan, v_hi, tier):
    return (v_lo, v_plan, v_hi, tier)


OFF = (0.0, 0.0, 0.0, "X")

# -------------------------------------------------------------------------------------------------- slot loads
CM5_SRC = "cm5-datasheet.pdf 4.3.3 Table 9 (Release 3): idle 400 mA, operation 900 mA typical at 5 V, no maximum; 8 W = board B's declared 1.6 A (gen_sch_b.py:43)"
FAN_SRC = "Sunon catalogue 240-A p. 16 (30x30x6, 5 V): MF30060V2 0.36 W, MF30060V1 0.56 W, representative (not IP68, not the pick, D-18); declared 0.1 A (gen_sch_b.py:46)"
SW33_SRC = "Diodes DS40068 Rev 5-2 Table 12-8: 3.3 V rails 354.8 mW typ, 390.2 mW max"
SW10_SRC = "Diodes DS40068 Rev 5-2 Table 12-8: 1.0 V rails 269.5 mW typ, 676.4 mW max"
NVME_SRC = "Advantech SQFlash 720-D DS v1.9 section 9: idle 900 mW, read 2.0 to 3.6 W; Cervoz T405 DS Rev 2.0 2.1: idle < 1050 mW, active < 2600 mW (both 3.3 V, Gen3 x4)"
for s in (1, 2, 3):
    slot_on_red = (s == 3)
    load("CM5 slot %d" % s, "S%d" % s, CM5_SRC,
         IDLE=same(2.0, "S"), IDLESPEC=same(2.0, "S"), TYP=same(4.5, "S"), REDB=same(2.0, "S"), EMCON=same(4.5, "S"),
         RED=(up(2.0, 4.5, 4.5, "S") if slot_on_red else OFF), ALLTX=up(4.5, 8.0, 8.0, "D"), BUSY=up(4.5, 8.0, 8.0, "D"))
    fan = up(0.36, 0.51, 0.56, "R")
    load("cooler fan slot %d" % s, "S%d" % s, FAN_SRC, IDLE=fan, IDLESPEC=fan, TYP=fan, REDB=fan, EMCON=fan, ALLTX=fan,
         RED=(fan if slot_on_red else OFF))
    sw33 = up(0.355, 0.355, 0.390, "S")
    sw10 = up(0.270, 0.270, 0.676, "S")
    load("PCIe switch 3.3 V slot %d" % s, "S%dB" % s, SW33_SRC, IDLE=sw33, IDLESPEC=sw33, TYP=sw33, REDB=sw33,
         EMCON=sw33, ALLTX=up(0.355, 0.390, 0.390, "S"), RED=(sw33 if slot_on_red else OFF))
    load("PCIe switch 1.0 V slot %d" % s, "S%dC" % s, SW10_SRC, IDLE=sw10, IDLESPEC=sw10, TYP=sw10, REDB=sw10,
         EMCON=sw10, ALLTX=up(0.270, 0.676, 0.676, "S"), RED=(sw10 if slot_on_red else OFF))
    nv_idle = up(0.90, 0.90, 1.05, "S")
    nv_typ = up(0.90, 1.20, 3.60, "R")
    load("NVMe slot %d" % s, "S%dB" % s, NVME_SRC, IDLE=nv_idle, IDLESPEC=nv_idle, TYP=nv_typ, REDB=nv_idle,
         EMCON=nv_typ, ALLTX=up(2.6, 3.6, 3.6, "S"), RED=(nv_idle if slot_on_red else OFF), BUSY=up(2.6, 2.6, 3.6, "R"))

AW_SRC = ("AsiaRF AW7915-AED product page (fetched 26 Sep 2026): 'maximum is 9W, average is 4 - 8W', supply 3.3 V 3 A "
          "(2.5 A minimum); AW7915-AED_V1.pdf (v1.0, 2023-08-17): 'maximum is 9.1W, average is 7W', 3.5 A (3 A minimum)")
live = up(4.0, 4.0, 8.0, "R")          # link up, idle or light traffic: the maker's average range, no idle figure
load("WiFi link card 1 (live)", "S1A", AW_SRC,
     IDLE=live, IDLESPEC=live, TYP=up(4.0, 6.0, 8.0, "R"), REDB=live, EMCON=up(0.0, 4.0, 9.1, "T"),
     ALLTX=up(9.1, 9.1, 9.1, "S"), RED=OFF, BUSY=up(4.0, 8.0, 9.1, "R"))
stby = up(0.0, 1.0, 9.1, "T")          # radio disabled by the voted select; no maker figure; 0 if held unpowered
load("WiFi link card 2 (standby)", "S3A", AW_SRC + "; standby role ARCH-PCB-B-IOHA.md line 324",
     IDLE=stby, IDLESPEC=stby, TYP=stby, REDB=stby, EMCON=stby, ALLTX=stby, RED=OFF)
RM_SRC = ("Quectel RM520N series HD v1.1 Table 43 (RM520N-GL, typ, at VCC 3.7 V, Table 42): idle 60 mA, RF disabled "
          "4.7 mA, LTE CA 1512 mA; watts taken at 3.7 V")
load("5G RM520N-GL", "S2A", RM_SRC,
     IDLE=same(0.222, "S"), IDLESPEC=same(0.222, "S"), REDB=same(0.222, "S"), TYP=up(0.222, 1.5, 5.59, "R"),
     EMCON=same(0.017, "S"), ALLTX=same(5.59, "S"), RED=OFF, BUSY=up(1.5, 5.59, 5.59, "S"))

# ----------------------------------------------------------------------------------------------- device-rail loads
LIME_SRC = ("LimeSDR Mini v2 documentation v2.4, Introduction (fetched 26 Sep 2026): 'Maximum Power 4.5 W, USB 3.0 "
            "power limit', 'Power consumption depends on configuration'; Hardware Setup: host supplies 5 V 900 mA")
load("LimeSDR Mini 2.4", "DEVP", LIME_SRC, TYP=up(3.0, 3.0, 4.5, "T"), ALLTX=same(4.5, "S"))
load("RockBLOCK 9704", "DEVP", "rb9704-datasheet-RB9704-001-JUN26.pdf: '60mW Idle, 1.4W Max'",
     IDLE=same(0.06, "S"), IDLESPEC=same(0.06, "S"), REDB=same(0.06, "S"), RED=same(0.06, "S"),
     TYP=up(0.06, 0.1, 1.4, "R"), ALLTX=same(1.4, "S"), BUSY=up(0.1, 1.4, 1.4, "S"))
load("LoRa E22-900M30S", "DEVP", "ebyte-e22-900m30s-user-manual-en-v1.20.pdf 2.2: TX 650 mA, RX 14 mA at 5 V",
     IDLE=same(0.07, "S"), IDLESPEC=same(0.07, "S"), REDB=same(0.07, "S"), RED=up(0.07, 0.3, 3.25, "R"),
     TYP=up(0.07, 0.3, 3.25, "R"), ALLTX=same(3.25, "S"), BUSY=up(0.3, 3.25, 3.25, "S"))
load("camera (part TBD)", "DEVP", "no part; bounded by its port contract 0.5 A at 5 V (gen_sch_b.py:233)",
     TYP=up(0.0, 1.0, 2.5, "T"), EMCON=up(0.0, 1.0, 2.5, "T"), ALLTX=up(1.0, 2.5, 2.5, "T"))
load("panel board C", "DEVP", "declared PANEL_5V 0.6 A typical, 1.0 A peak (gen_sch_b.py:82; board C intent)",
     IDLE=up(1.5, 1.5, 5.0, "D"), IDLESPEC=up(1.5, 1.5, 5.0, "D"), TYP=up(3.0, 3.0, 5.0, "D"), RED=up(1.5, 1.5, 5.0, "D"),
     REDB=up(1.5, 1.5, 5.0, "D"), EMCON=up(3.0, 3.0, 5.0, "D"), ALLTX=same(5.0, "D"))
load("QMX USB and HDMI 5 V", "DEVP", "declared F3 0.3 A and F2 0.2 A peaks (gen_sch_b.py:83,87); W2 0.3 W",
     ALL=up(0.3, 0.3, 2.5, "D"), RED=up(0.1, 0.1, 2.5, "D"))
load("board D (SA868 and logic)", "DEVP", "nicerf-sa868-datasheet-v1.3.pdf: RX 60 mA, TX low 450 to 550 mA at 5 V; rest declared (W2)",
     IDLE=same(0.6, "D"), IDLESPEC=same(0.6, "D"), TYP=same(0.8, "D"), RED=same(0.6, "D"), REDB=same(0.6, "D"),
     EMCON=same(0.6, "D"), ALLTX=up(3.0, 3.3, 3.3, "D"))
load("four CP2102N bridges", "DEVP", "declared 0.02 A each (gen_sch_b.py:90)", ALL=same(0.4, "D"))
KSZ = "Microchip KSZ9897R DS00002330D Table 6-1 (TA 25 C, typ): full 1000 Mbps all ports 100 %: AVDDH 330 mA, VDDIO 80 mA, AVDDL 460 mA, DVDDL 750 mA; energy detect 20/30/30/150 mA"
ksz_state = dict(IDLE=0, IDLESPEC=0, TYP=0, BUSY=0, REDB=0, EMCON=0, ALLTX=0, RED=0)
load("KSZ9897R AVDDH 2.5 V", "KSZ2V5", KSZ, ALL=up(0.050, 0.825, 0.825, "S"))
load("KSZ9897R VDDIO 3.3 V", "D3V3", KSZ, ALL=up(0.099, 0.264, 0.264, "S"))
load("KSZ9897R AVDDL+DVDDL 1.2 V", "KSZ1V2", KSZ, ALL=up(0.216, 1.452, 1.452, "S"))
HUB = "TI TUSB8041 SLLSEE4E 7.7 (TA 25 C, typ): disconnected 2.3/28 mA; 2.0 host 4 HS 76/86 mA; 1 SS U0 + 1 HS 85/395 mA; 4 SS U0 49/778 mA (VDD33/VDD1.1)"
hub33 = {"disc": 0.0076, "hs4": 0.251, "ss1hs1": 0.281, "ss4": 0.162}
hub11 = {"disc": 0.031, "hs4": 0.095, "ss1hs1": 0.435, "ss4": 0.856}
def hubs(kind_plan):
    lo33, lo11 = 3 * hub33["disc"], 3 * hub11["disc"]
    hi33, hi11 = 3 * hub33["hs4"], 3 * hub11["ss4"]       # VDD33 highest row is 2 SS + 2 HS 99 mA; 4 SS 49 mA
    hi33 = 3 * 0.327                                        # 99 mA x 3.3 V, the highest VDD33 row
    p33 = sum(hub33[k] for k in kind_plan)
    p11 = sum(hub11[k] for k in kind_plan)
    return (up(lo33, p33, hi33, "R"), up(lo11, p11, hi11, "R"))
for st, kinds in (("IDLE", ("hs4",) * 3), ("IDLESPEC", ("hs4",) * 3), ("REDB", ("hs4",) * 3),
                  ("TYP", ("ss1hs1", "hs4", "hs4")), ("BUSY", ("ss1hs1", "hs4", "hs4")), ("EMCON", ("hs4",) * 3),
                  ("ALLTX", ("ss1hs1", "hs4", "hs4")),
                  ("RED", ("hs4", "hs4", "disc"))):
    ksz_state[st] = hubs(kinds)
load("three TUSB8041 hubs VDD33", "D3V3", HUB, **{k: v[0] for k, v in ksz_state.items()})
load("three TUSB8041 hubs VDD 1.1 V", "HUB1V1", HUB, **{k: v[1] for k, v in ksz_state.items()})
H7 = ("ST STM32H743 DS12110 Rev 10 Table 30: Run from ITCM, 200 MHz VOS3 peripherals off 33 mA typ; 400 MHz VOS1 "
      "peripherals off 71 mA typ; 400 MHz all peripherals on 165 mA typ, 400 mA max at TJ 85 C; plus 0.06 A declared "
      "per supervisor for its other parts (gen_sch_b.py:222)")
load("three STM32H743 supervisors and their parts", "IOC", H7,
     ALL=up(3 * (0.033 + 0.06) * 3.3, 3 * (0.071 + 0.06) * 3.3, 3 * (0.400 + 0.06) * 3.3, "R"))
load("E72 x2 (Zigbee, Thread)", "ZB", "ebyte-e72-2g4m20s1e-user-manual.pdf 2.2: RX 7.3 mA, TX 106 mA at 20 dBm, 3.3 V",
     IDLE=same(0.048, "S"), IDLESPEC=same(0.048, "S"), TYP=same(0.048, "S"), REDB=same(0.048, "S"),
     RED=same(0.048, "S"), ALLTX=same(0.70, "S"))
load("LG290P GNSS", "D3V3", "lg290p03-hardware-design-v1.1.pdf: 99 mA, 326.7 mW", ALL=same(0.327, "S"))
load("other +3V3_DEV logic", "D3V3", "declared: PoE controller, expanders, muxes, voters, secure element, clock, TMP117 (gen_sch_b.py:95-108), 0.395 A",
     ALL=up(0.5, 1.30, 1.30, "D"))

# ------------------------------------------------------------------------------------------------ board A, D, E
load("board A logic", "A3V3", "declared +3V3 0.3 / 0.6 A (gen_sch_a.py:118)", ALL=up(0.5, 0.5, 1.0, "D"),
     ALLTX=up(0.5, 1.0, 1.0, "D"))
PA_SRC = ("RA30H1317M1 datasheet: Pout > 30 W at total efficiency > 40 % (VDD 12.5 V), so <= 75 W at 30 W out; at "
          "13.8 V the drain current is 5.4 to 8.2 A (W2 F-PR-02, INFERRED: 30 W to the 45 W output rating at 40 %), "
          "113 W; board D regulates VGG to 4.30 to 4.68 V on main since 458b2873 (gen_sch_d.py lines 624 to 645 at "
          "01469100), inside the sheet's VGG < 5 V condition, and the drain at 13.8 V stays a bench item")
load("VHF PA 30 W", "PA", PA_SRC, IDLESPEC=up(0.1, 0.9, 0.9, "T"), ALLTX=up(75.0, 75.0, 113.0, "R"))
load("QMX HF", "HF", "qmx-operating-manual-1_04_004.pdf: receive 'as low as 80mA' at 12 V; transmit 0.7 to 1.1 A (appendix 32.51 line 2816)",
     TYP=same(0.96, "S"), ALLTX=up(8.4, 12.0, 13.2, "R"))
XEN = "xenarc-709gnk-product-manual-v2.pdf and xenarc.com/709GNK.html: 'Power Consumption: <= 10W'; no typical figure"
load("Xenarc 709GNK", "MON", XEN, IDLE=up(4.0, 4.0, 10.0, "T"), IDLESPEC=up(6.0, 6.0, 10.0, "T"),
     TYP=up(6.0, 6.0, 10.0, "T"), EMCON=up(6.0, 6.0, 10.0, "T"), ALLTX=same(10.0, "S"))
load("board E controller and sensors", "E3V3", "declared +5V_E6 0.30 A (gen_sch_e.py:34, 89); W2 0.8 W",
     ALL=up(0.3, 0.5, 1.0, "D"))
load("Geiger module", "E5V", "declared +5V_GEIGER 0.10 A (gen_sch_e.py:142); RadiationD-v1.1 class (open-picks.txt:22), no sheet",
     ALL=up(0.1, 0.3, 0.5, "D"))
MIX = ("Sunon catalogue 240-A p. 38 (60x60x15 IP68, 12 V): GF60151B9 0.39 W to GF60151B6 1.50 W; declared 0.1 A each "
       "on CELL_F (gen_sch_e.py:34); PWM duty TBD")
load("two mixer fans", "EFAN", MIX, ALL=up(0.78, 1.44, 3.0, "R"))
# The outlets are off in every state and switched on only by the section 7.1 variants. Contracts: PoE 0.6 A at 54 V
# (gen_sch_a.py:124 declares 0.3 A typical, 0.6 A peak), USB-C 15 V at 3 A, 45 W (gen_sch_a.py:977, the TPS25740A's
# highest advertised profile). Lines at 01469100.
load("PoE outlet (delivered outside)", "POE", "PoE contract 0.6 A at 54 V, 32.4 W (gen_sch_a.py:124)")
load("USB-C outlet (delivered outside)", "PDO", "USB-C PD contract 15 V at 3 A, 45 W (gen_sch_a.py:977-982)")
POE_ON = up(32.4, 32.4, 32.4, "D")
PD_ON = up(45.0, 45.0, 45.0, "D")
# The pack heater (cold overlay only, off in every state). RS PRO 245-556: 7.5 W at 12 V dc (the mat's sheet), so
# 19.2 Ohm; on 1f614233's unregulated VBAT it takes V^2 / 19.2: 7.5 W at 12 V, 10.8 W at 14.4 V, 14.7 W at 16.8 V.
# A constant-power figure at every stack voltage overstates its current below the scenario's voltage (conservative).
# On main since 458b2873 it is regulated to 12 V: 7.5 W plus the buck's loss (TPS62933 declared floor 0.88, NOT
# PLOTTED), less than the unregulated figure the tables carry, so the tables overstate the heater on main.
R_HEAT = 12.0 ** 2 / 7.5
HEAT_SRC = ("RS PRO 245-556 heater mat sheet (v2/vendor/battery/heater/): 12 V dc, 7.5 W, so 19.2 Ohm; on 1f614233's "
            "unregulated VBAT V^2/19.2; main regulates it to 12 V since 458b2873 (F-PR-06)")
load("pack heater mat (cold overlay)", "HEAT", HEAT_SRC)
HEAT_ON = up(12.0 ** 2 / R_HEAT, 14.4 ** 2 / R_HEAT, 16.8 ** 2 / R_HEAT, "S")
# The VHF PA keyed on its own (third cycle): the PA at the RA30H1317M1's 75 W (Pout 30 W at > 40 % total efficiency)
# or at W2 F-PR-02's 113 W (5.4 to 8.2 A at 13.8 V with VGG hard), and board D's SA868 transmitting (its PS-ALLTX
# figure); every other load at the base state's own figure; outlets and heater off.
PA_75 = {"VHF PA 30 W": up(75.0, 75.0, 113.0, "R"), "board D (SA868 and logic)": up(3.0, 3.3, 3.3, "D")}
PA_113 = {"VHF PA 30 W": up(113.0, 113.0, 113.0, "R"), "board D (SA868 and logic)": up(3.0, 3.3, 3.3, "D")}

TIER_ORDER = "SRDTX"


# ------------------------------------------------------------------------------------------------- computation
def children(node):
    return [n for n, v in NODES.items() if v[1] == node]


def node_power(node, st, scen, cache):
    """Input power of `node` (W) and its output current, for state st and scenario lo/plan/hi."""
    key = (node, st, scen)
    if key in cache:
        return cache[key]
    idx = {"lo": 0, "plan": 1, "hi": 2}[scen]
    p_out = sum(v[st][idx] for (_, nd, v, _) in LOADS if nd == node)
    for ch in children(node):
        p_out += node_power(ch, st, scen, cache)[0]
    kind, parent, vout, param, _ = NODES[node]
    if kind == "root":
        res = (p_out, p_out / vout, 1.0)
    else:
        vin = VIN_OF[scen] if parent in ("VBAT",) else NODES[parent][2]
        if kind == "curve":
            eta = eff_curve(param, vin, p_out / vout) if p_out > 0 else 1.0
        elif kind == "fixed":
            eta = param
        elif kind == "ldo":
            eta = vout / NODES[parent][2]
        else:
            eta = 1.0
        res = (p_out / eta if p_out > 0 else 0.0, p_out / vout, eta)
    cache[key] = res
    return res


def battery_side(p_vbat, vpack, r=None):
    r = R_DIST if r is None else r
    pb = p_vbat
    for _ in range(60):
        pb = p_vbat + (pb / vpack) ** 2 * r
    return pb


def state_totals(st, scen):
    cache = {}
    p_vbat = node_power("VBAT", st, scen, cache)[0]
    idx = {"lo": 0, "plan": 1, "hi": 2}[scen]
    p_load = sum(v[st][idx] for (_, _, v, _) in LOADS)
    pb = battery_side(p_vbat, 14.4)
    return p_load, pb, cache


def with_overrides(st, overrides):
    """Swap the state-st figures of the named loads; returns what to restore."""
    saved = []
    for i, (name, nd, v, src) in enumerate(LOADS):
        if name in (overrides or {}):
            saved.append((i, LOADS[i]))
            nv = dict(v)
            nv[st] = overrides[name]
            LOADS[i] = (name, nd, nv, src)
    return saved


def restore(saved):
    for i, old in saved:
        LOADS[i] = old


def state_full(st, scen, overrides=None):
    """p_load (W at the load pins), p_vbat (W at VBAT, converter losses included), pb (battery W: VBAT plus the
    R_DIST distribution I2R at 14.4 V, 22.5 mOhm since the third cycle) and outside (W delivered out of the
    enclosure by the outlets)."""
    saved = with_overrides(st, overrides)
    try:
        cache = {}
        p_vbat = node_power("VBAT", st, scen, cache)[0]
        idx = {"lo": 0, "plan": 1, "hi": 2}[scen]
        p_load = sum(v[st][idx] for (_, _, v, _) in LOADS)
        outside = sum(v[st][idx] for (n, _, v, _) in LOADS if n in OUTSIDE)
        pb = battery_side(p_vbat, 14.4)
    finally:
        restore(saved)
    return {"p_load": p_load, "p_vbat": p_vbat, "pb": pb, "outside": outside}


def pack_current(p_vbat, v_stack, r=None):
    """Pack current (A) when the cell stack under load stands at v_stack: v_stack * I = p_vbat + I^2 * R_DIST.
    The distribution drop (fuses, FETs, shunt, leads) is counted here once. r overrides R_DIST (fifth cycle)."""
    r = R_DIST if r is None else r
    disc = v_stack * v_stack - 4.0 * r * p_vbat
    if disc < 0:
        return float("inf")
    return (v_stack - math.sqrt(disc)) / (2.0 * r)


def load_battery_share(st, scen="plan"):
    """Battery-side watts per load: each load divided by the efficiency chain its node sees in this state."""
    _, pb, cache = state_totals(st, scen)
    idx = {"lo": 0, "plan": 1, "hi": 2}[scen]
    out = []
    for (name, nd, v, src) in LOADS:
        p = v[st][idx]
        eta, n = 1.0, nd
        while NODES[n][0] != "root":
            eta *= cache[(n, st, scen)][2] if (n, st, scen) in cache else 1.0
            n = NODES[n][1]
        out.append((name, p, p / eta if eta else 0.0, v[st][3]))
    tot = sum(x[2] for x in out)
    scale = pb / tot if tot else 1.0          # distribute the I2R share proportionally
    return [(a, b, c * scale, d) for a, b, c, d in out], pb


# ------------------------------------------------------------------------------------------------ cell model
C_MIN, V_NOM, RESERVE = 3.35, 3.60, 0.05          # INR18650-35E Ver. 1.1: 3.1, 7.2 (min 3,350 mAh), 3.3; reserve INFERRED
RATE = [(0.68, 1.00), (3.4, 0.97), (6.8, 0.95), (8.0, 0.92)]   # 7.8
R_CELL = {"lo": 0.035, "plan": 0.05, "hi": 0.06}   # 7.4 gives AC 1 kHz <= 35 mOhm; DC higher, INFERRED range
COLD_LO = 0.41                                     # 7.5: 40 % at -10 C against 97 % at 23 C, 3.4 A


def rate_f(i):
    if i <= RATE[0][0]:
        return 1.0
    for (a, fa), (b, fb) in zip(RATE, RATE[1:]):
        if i <= b:
            return fa + (fb - fa) * (i - a) / (b - a)
    return RATE[-1][1]


def usable(pb, p=3, age=1.0, f_t=1.0, r=0.05):
    i = pb / (4 * V_NOM) / p
    chain = [("12 cells x 3.35 Ah x 3.60 V (spec minimum, 0.2C, 2.65 V, 23 C)", 4 * p * C_MIN * V_NOM)]
    e = chain[-1][1] * rate_f(i)
    chain.append(("x rate factor %.3f at %.2f A per cell (7.8)" % (rate_f(i), i), e))
    e = e * (V_NOM - i * r) / V_NOM
    chain.append(("x average voltage (3.60 - %.2f x %.3f) / 3.60 (sag, INFERRED)" % (i, r), e))
    e = e * f_t
    chain.append(("x temperature factor %.2f" % f_t, e))
    e = e * age
    chain.append(("x ageing %.2f" % age, e))
    e = e * (1 - RESERVE)
    chain.append(("x (1 - 5 percent shutdown reserve, INFERRED)", e))
    return e, i, chain


# ------------------------------------------------------------------------------------------------ thermal model
# Conductance inside air to ambient (W/K), W4's independent lumped bound (fnd/w4 drafts/w4-scratch-thermal.py,
# carried in ARCHITECTURE.md section 8.2 on fnd/i3), and appendix 32.53's own figures.
G = {"open_fans": (1.22, 2.85), "closed_fans": (1.06, 2.49), "open_still": (0.77, 1.57), "closed_still": (0.70, 1.45)}
# 32.53 (appendix line 2860, lid open): "total about 2.1 W/K still, about 3.0 to 3.3 W/K with fans"; lid closed "about
# 1.5 to 2 W/K with fans". CORRECTED in the fourth cycle: the still-air (fans off) figure was left out and the page
# called it "not stated"; 32.53 gives no lid-closed still-air figure.
G_3253 = {"open_fans": (3.0, 3.3), "closed_fans": (1.5, 2.0), "open_still": (2.1, 2.1)}
ENCL = {"IDLE": "open_fans", "IDLESPEC": "open_fans", "TYP": "open_fans", "BUSY": "open_fans", "EMCON": "open_fans",
        "REDB": "closed_fans", "RED": "closed_fans", "ALLTX": "open_fans"}
# The pack block, shrink-wrapped, 56.65 x 133.5 x 38.1 mm (adjudication A06), film coefficient 5 to 15 W/m2K
# (INFERRED): its conductance to the air around it.
A_BLK = 2 * (0.05665 * 0.1335 + 0.05665 * 0.0381 + 0.1335 * 0.0381)
G_BLK = (A_BLK * 5.0, A_BLK * 15.0)
# The pack current contract as declared on main (1f614233, unchanged at 01469100).
I_CONT = 10.0     # pcb_pack_protection.yaml:28 declared_continuous_a; pcb_energy_chain.yaml continuous_a, every stage
I_PEAK = 18.0     # pcb_pack_protection.yaml:29 declared_peak_a; no duration in either YAML (32.53: "minutes")
I_OCD = 20.0      # pcb_pack_protection.yaml:110, 2 s
V_CUV = 10.0      # pcb_pack_protection.yaml:101, 2.50 V per cell: the lowest stack voltage the gauge lets the kit run at
# The charge path (S-20, fnd/r4a drafts/r4-decisions.md: ChargeCurrent at most 3.0 A for 4S3P) and its efficiencies: BQ25731 SLUSE66A Figure
# 8-4 (VIN 20 V, VOUT 14.8 V, 2 to 6 A: about 98 %); the LM5176 front end to 20 V is NOT PLOTTED (Figure 6-2, VOUT
# 12 V, gives 96 to 97 % at 3 to 6 A from 24 V), taken 0.95 to 0.97 (INFERRED).
ICHG, ETA_CHG, ETA_FE = 3.0, 0.98, (0.95, 0.97)


def pack_i2r(pb, r=None, v=14.4):
    """The cells' own I2R (W) at the discharge current of battery W pb at stack voltage v (the nominal 14.4 V is the
    run's average; the end of discharge is higher)."""
    r = R_CELL["plan"] if r is None else r
    return 12 * (pb / v / 3) ** 2 * r


def charge_heat(pb_loads, eta_fe):
    """Heat (W) added inside while charging at ICHG on shore: the charge path's loss on the power into the pack,
    and the front end's and charger's loss on the loads' own power, which comes from shore through them (main's
    VSYS topology since 458b2873, S-04; at 1f614233 the loads sat behind the charge shunt, which passed them through
    the same stages)."""
    p_into = ICHG * 15.5
    chg = p_into / ETA_CHG - p_into + (p_into / ETA_CHG) * (1 / eta_fe - 1)
    path = pb_loads / (ETA_CHG * eta_fe) - pb_loads
    return chg + path


def cell_temp(amb, q_in, p_pack, g_encl, g_blk):
    """Cell surface (C): inside air rises by ALL the heat inside, the pack's own I2R included, over the enclosure's
    conductance; the cells sit above that air by their own I2R over the pack block's conductance."""
    return amb + (q_in + p_pack) / g_encl + p_pack / g_blk


def ceiling(limit, q_in, p_pack, g_encl, g_blk):
    """Highest ambient (C) at which the limit holds."""
    return limit - (q_in + p_pack) / g_encl - p_pack / g_blk


def main(out_path):
    res = {"states": {}, "shares": {}, "efficiency": {}, "runtime": {}, "d11": {}, "thermal": {}, "reconcile": {}}
    print("== battery-side power per state (W): low / plan / high; at the loads (plan)")
    for st in STATES:
        row = {}
        for scen in ("lo", "plan", "hi"):
            pl, pb, cache = state_totals(st, scen)
            row[scen] = {"load_W": round(pl, 2), "battery_W": round(pb, 2)}
        shares, pb = load_battery_share(st, "plan")
        tiers = {t: round(sum(x[2] for x in shares if x[3] == t), 2) for t in TIER_ORDER}
        row["tiers_plan_battery_W"] = tiers
        res["states"][st] = row
        res["shares"][st] = [(a, round(b, 3), round(c, 3), d) for a, b, c, d in shares if b > 0]
        print("%-12s load %6.1f | battery %6.1f / %6.1f / %6.1f | S %5.1f R %5.1f D %5.1f T %5.1f"
              % (STATE_NAME[st], row["plan"]["load_W"], row["lo"]["battery_W"], row["plan"]["battery_W"],
                 row["hi"]["battery_W"], tiers["S"], tiers["R"], tiers["D"], tiers["T"]))

    # variants
    def variant(st, overrides, scen="plan"):
        saved = []
        for i, (name, nd, v, src) in enumerate(LOADS):
            if name in overrides:
                saved.append((i, LOADS[i]))
                nv = dict(v)
                nv[st] = overrides[name]
                LOADS[i] = (name, nd, nv, src)
        out = {s: round(state_totals(st, s)[1], 2) for s in ("lo", "plan", "hi")}
        for i, old in saved:
            LOADS[i] = old
        return out
    no_link = {"WiFi link card 1 (live)": OFF, "WiFi link card 2 (standby)": OFF}
    res["variants"] = {
        "IDLESPEC_link_off": variant("IDLESPEC", no_link),
        "IDLE_link_off": variant("IDLE", no_link),
        "TYP_standby_card_off": variant("TYP", {"WiFi link card 2 (standby)": OFF}),
        "ALLTX_standby_card_off": variant("ALLTX", {"WiFi link card 2 (standby)": OFF}),
        "ALLTX_non_tx_at_typical": variant("ALLTX", {**{"CM5 slot %d" % s: same(4.5, "S") for s in (1, 2, 3)},
                                                     **{"NVMe slot %d" % s: up(0.9, 1.2, 3.6, "R") for s in (1, 2, 3)},
                                                     "WiFi link card 2 (standby)": OFF}),
    }
    print("== variants (battery W lo/plan/hi):", json.dumps(res["variants"]))

    print("== converter efficiency by state (plan scenario, VIN 14.4 V where the parent is the pack)")
    for st in ("IDLE", "TYP", "BUSY", "RED", "ALLTX"):
        _, _, cache = state_totals(st, "plan")
        _, _, cache_hi = state_totals(st, "hi")
        _, _, cache_lo = state_totals(st, "lo")
        rows = []
        for n in NODES:
            if NODES[n][0] in ("root", "pass"):
                continue
            pin, iout, eta = cache.get((n, st, "plan"), (0, 0, 1))
            if pin <= 0:
                continue
            eta_hi = cache_hi.get((n, st, "hi"), (0, 0, 1))[2]
            eta_lo = cache_lo.get((n, st, "lo"), (0, 0, 1))[2]
            rows.append((n, round(iout, 3), round(eta, 3), round(eta_hi, 3), round(eta_lo, 3), round(pin * (1 - eta), 2)))
        res["efficiency"][st] = rows
        print(st, rows)

    print("== runtime, 4S3P, +20 C (factor 1.00): hours new / aged 80 % / aged 60 %; cold bracket new")
    for st in STATES:
        rr = {}
        for scen in ("lo", "plan", "hi"):
            pb = res["states"][st][scen]["battery_W"]
            e_new, i, chain = usable(pb, 3, 1.0, 1.0, R_CELL["plan"])
            e_80, _, chain80 = usable(pb, 3, 0.8, 1.0, R_CELL["plan"])
            e_60, _, _ = usable(pb, 3, 0.6, 1.0, R_CELL["plan"])
            e_cold, _, _ = usable(pb, 3, 1.0, COLD_LO, R_CELL["plan"])
            rr[scen] = {"battery_W": pb, "I_cell": round(i, 2), "new_h": round(e_new / pb, 2),
                        "aged80_h": round(e_80 / pb, 2), "aged60_h": round(e_60 / pb, 2),
                        "cold_new_h_low_end": round(e_cold / pb, 2), "usable_new_Wh": round(e_new, 1),
                        "usable_aged80_Wh": round(e_80, 1)}
            if scen == "plan" and st in ("IDLESPEC", "TYP"):
                rr["chain_new"] = [(a, round(b, 1)) for a, b in chain]
                rr["chain_aged80"] = [(a, round(b, 1)) for a, b in chain80]
        res["runtime"][st] = rr
        print("%-12s" % STATE_NAME[st], {k: (v["new_h"], v["aged80_h"], v["aged60_h"]) for k, v in rr.items() if k in ("lo", "plan", "hi")})
    for st in ("IDLESPEC", "TYP"):
        print(st, "derating chain (plan, new):", res["runtime"][st]["chain_new"])
        print(st, "derating chain (plan, aged 80):", res["runtime"][st]["chain_aged80"])
    for k, v in res["variants"].items():
        e80, _, _ = usable(v["plan"], 3, 0.8)
        en, _, _ = usable(v["plan"], 3, 1.0)
        print("variant %s: plan %.1f W -> %.2f h new, %.2f h aged" % (k, v["plan"], en / v["plan"], e80 / v["plan"]))
        res["variants"][k]["new_h"] = round(en / v["plan"], 2)
        res["variants"][k]["aged80_h"] = round(e80 / v["plan"], 2)

    # ------------------------------------------------------------ D-11: the pack current contract and the floor
    # CORRECTED 26 Sep 2026 (checker, cycle 2): battery W already carries the R_DIST distribution I2R, so battery W
    # over 18 A is already the cell-stack voltage under load, and the first version added 18 A x R_DIST on top of it
    # (0.36 V counted twice). Here the loaded voltage is taken at VBAT (p_vbat / 18 A) and the distribution drop is
    # added ONCE, at 18 A. The first version's figure is kept in the output as `V_rest_pack_prev_method` so the
    # correction can be read.
    FLOOR = 15.5
    typ_nontx = {**{"CM5 slot %d" % s: same(4.5, "S") for s in (1, 2, 3)},
                 **{"NVMe slot %d" % s: up(0.9, 1.2, 3.6, "R") for s in (1, 2, 3)},
                 "WiFi link card 2 (standby)": OFF}
    print("== D-11: stack voltage under load that keeps all-transmit at %.0f A, and the rest voltage that gives it" % I_PEAK)
    d11 = {"floor_V": FLOOR}
    for label, st, ov, scen in (("ALLTX plan", "ALLTX", None, "plan"), ("ALLTX high", "ALLTX", None, "hi"),
                                ("ALLTX, non-transmit loads typical, standby card off (plan)", "ALLTX", typ_nontx, "plan"),
                                ("ALLTX, non-transmit loads typical, standby card off (high)", "ALLTX", typ_nontx, "hi")):
        f = state_full(st, scen, ov)
        pv, pb = f["p_vbat"], f["pb"]
        v_vbat = pv / I_PEAK
        v_stack = v_vbat + I_PEAK * R_DIST
        rows = {}
        for rk, r in R_CELL.items():
            r_pack = 4 * r / 3
            v_rest = v_stack + I_PEAK * r_pack
            rows[rk] = {"R_cell": r, "V_rest_pack": round(v_rest, 2), "V_rest_cell": round(v_rest / 4, 3),
                        "feasible_at_full_charge": v_rest / 4 <= 4.2,
                        # the first cycle's figure, reproduced with its own 20 mOhm (before F2 was carried)
                        "V_rest_pack_prev_method": round(battery_side(pv, 14.4, R_W2) / I_PEAK + I_PEAK * (r_pack + R_W2), 2)}
        r_max = (FLOOR - v_stack) * 3.0 / (4.0 * I_PEAK)
        cur = {str(v): round(pack_current(pv, v), 1) for v in (16.8, 14.4, 12.0, 10.6, V_CUV)}
        d11[label] = {"battery_W": round(pb, 2), "vbat_W": round(pv, 2), "V_vbat_at_18A": round(v_vbat, 2),
                      "V_stack_at_18A": round(v_stack, 2), "by_R_cell": rows, "I_at_V_stack": cur,
                      "R_cell_max_that_15V5_covers": round(r_max, 4),
                      "V_stack_at_I": {str(i): round(pv / i + i * R_DIST, 2) for i in (I_CONT, I_PEAK, I_OCD, 25.0)},
                      "margin_V_at_R_hi": round(FLOOR - rows["hi"]["V_rest_pack"], 2)}
        print(label, json.dumps(d11[label]))
    # THIRD CYCLE: the basis row with the heater ON, to show what the rule "heater off during any PA key-down" protects.
    # 1f614233: the mat on unregulated VBAT takes VBAT^2 / 19.2, so VBAT at 18 A solves VBAT^2 / R_HEAT - 18 VBAT + pv
    # = 0; main since 458b2873: 7.5 W regulated through the TPS62933 at its declared 0.88.
    basis = d11["ALLTX, non-transmit loads typical, standby card off (high)"]
    pv_b = basis["vbat_W"]
    heat_cases = {}
    for tag in ("1f614233, unregulated mat", "main since 458b2873, regulated 12 V"):
        if tag.startswith("1f614233"):
            v_vbat = (I_PEAK - math.sqrt(I_PEAK ** 2 - 4 * pv_b / R_HEAT)) * R_HEAT / 2
            p_heat = v_vbat ** 2 / R_HEAT
        else:
            p_heat = 7.5 / 0.88
            v_vbat = (pv_b + p_heat) / I_PEAK
        v_stack = v_vbat + I_PEAK * R_DIST
        heat_cases[tag] = {"heater_W": round(p_heat, 2), "V_vbat_at_18A": round(v_vbat, 2),
                           "V_stack_at_18A": round(v_stack, 2),
                           "V_rest_pack": {rk: round(v_stack + I_PEAK * 4 * r / 3, 2) for rk, r in R_CELL.items()},
                           "R_cell_max_that_15V5_covers": round((FLOOR - v_stack) * 3.0 / (4.0 * I_PEAK), 4)}
    d11["basis_high_with_heater_on"] = heat_cases
    print("D-11 basis with the heater on:", json.dumps(heat_cases))

    # THIRD CYCLE: the PA keyed on its own (the other transmitters idle, outlets and heater off). The same arithmetic
    # as D-11 gives the rest voltage below which such a key-down would pass 18 A.
    PA_FLOOR = 12.4
    pa_only = {"PA_floor_V": PA_FLOOR}
    for label, st, ov, scen in (("PA alone over PS-TYP, PA at 75 W (plan)", "TYP", PA_75, "plan"),
                                ("PA alone over PS-TYP, PA at 113 W, the rest at plan", "TYP", PA_113, "plan"),
                                ("PA alone over PS-TYP, every load at its maximum", "TYP", PA_75, "hi"),
                                ("PA alone over PS-IDLE-SPEC, PA at 113 W, the rest at plan", "IDLESPEC", PA_113, "plan")):
        f = state_full(st, scen, ov)
        pv = f["p_vbat"]
        v_stack = pv / I_PEAK + I_PEAK * R_DIST
        pa_only[label] = {"battery_W": round(f["pb"], 2), "vbat_W": round(pv, 2), "V_stack_at_18A": round(v_stack, 2),
                          "V_rest_pack": {rk: round(v_stack + I_PEAK * 4 * r / 3, 2) for rk, r in R_CELL.items()},
                          "R_cell_max_that_PA_floor_covers": round((PA_FLOOR - v_stack) * 3.0 / (4.0 * I_PEAK), 4),
                          "V_stack_at_I": {str(i): round(pv / i + i * R_DIST, 2) for i in (I_CONT, I_PEAK, I_OCD)},
                          "I_at_V_stack": {str(v): round(pack_current(pv, v), 1) for v in (16.8, 14.4, 12.0, V_CUV)}}
        print(label, json.dumps(pa_only[label]))
    res["pa_only"] = pa_only

    # FIFTH CYCLE: main's pack path since 458b2873 carries board A's 5 mOhm RSR shunt R17 in the discharge path (S-04).
    # The floors' bases re-solved at R_DIST_MAIN; R17's own dissipation.
    mp = {"R_DIST_ohm": round(R_DIST, 4), "R_DIST_main_ohm": round(R_DIST_MAIN, 4), "R17_ohm": R_R17,
          "R17_W_at_A": {str(i): round(i * i * R_R17, 2) for i in (I_CONT, I_PEAK, I_OCD)},
          "rest_voltage_shift_V_at_18A": round(I_PEAK * R_R17, 3)}
    pa113 = pa_only["PA alone over PS-TYP, PA at 113 W, the rest at plan"]["vbat_W"]
    for tag, pv, fl in (("all-transmit basis: non-transmit typical, standby card off, high", pv_b, FLOOR),
                        ("the same with main's regulated heater on", pv_b + 7.5 / 0.88, FLOOR),
                        ("PA alone over PS-TYP, PA at 113 W, the rest at plan", pa113, PA_FLOOR)):
        v_stack = pv / I_PEAK + I_PEAK * R_DIST_MAIN
        rest = {rk: round(v_stack + I_PEAK * 4 * r / 3, 2) for rk, r in R_CELL.items()}
        mp[tag] = {"vbat_W": round(pv, 2), "floor_V": fl, "V_stack_at_18A": round(v_stack, 2), "V_rest_pack": rest,
                   "margin_V_at_R_hi": round(fl - rest["hi"], 2),
                   "R_cell_max_that_floor_covers": round((fl - v_stack) * 3.0 / (4.0 * I_PEAK), 4)}
    d11["main_pack_path_R17"] = mp
    print("main's pack path with R17 (S-04):", json.dumps(mp))

    # key-down time from the gauge's discharge window (60 C) and from the PA case limit (100 C)
    CP_LO, CP_HI = 0.8, 1.1                  # J/gK, 18650 Li-ion, INFERRED (no Samsung figure)
    M_CELLS = 12 * 50.0                      # g, 3.10 "50 g max"
    kd = {}
    for rk, r in R_CELL.items():
        p_i2r = 12 * (I_PEAK / 3) ** 2 * r
        kd[rk] = {"pack_I2R_W_at_18A": round(p_i2r, 1),
                  "K_per_min_adiabatic": (round(p_i2r * 60 / (M_CELLS * CP_HI), 2), round(p_i2r * 60 / (M_CELLS * CP_LO), 2))}
    d11["cell_heating_at_18A"] = kd
    # 3.10 gives only a MAXIMUM cell mass, so the rise above is the smallest the sheet allows; the cell mass at which the
    # worst 60 s rise would use the whole 5 K between the 55 C gate and the 60 C window:
    worst = kd["hi"]["K_per_min_adiabatic"][1]
    d11["cell_mass_g_that_uses_the_5K"] = round(50.0 * worst / 5.0, 1)
    d11["pa_plate"] = {"heat_W": 45.0, "plate_J_per_K": 403.0, "K_per_min": round(45.0 * 60 / 403.0, 1),
                       "case_limit_C": 100.0}
    # The design record's own key-down figure (32.53, appendix line 2860): "The 200 W peak (PA key-down) lasts minutes
    # and goes into about 8 to 10 kJ/K of thermal mass, about +10 K transient." Read literally, with all 200 W as heat
    # and no loss to ambient: the lumped rise per minute, and the time the +10 K implies. Against it, the 12 cells' own
    # heat capacity (600 g at 0.8 to 1.1 J/gK) and the time their own I2R at 18 A takes to use the 5 K between K2's
    # +55 C gate and the 60 C window (fourth cycle).
    rec_lo, rec_hi = 8000.0, 10000.0
    c_cells = (M_CELLS * CP_LO, M_CELLS * CP_HI)
    d11["record_3253"] = {
        "peak_W": 200.0, "mass_J_per_K": (rec_lo, rec_hi), "stated_rise_K": 10.0,
        "K_per_min_lumped": (round(200.0 * 60 / rec_hi, 2), round(200.0 * 60 / rec_lo, 2)),
        "s_to_plus_10K_lumped": (round(10.0 * rec_lo / 200.0), round(10.0 * rec_hi / 200.0)),
        "cells_J_per_K": (round(c_cells[0]), round(c_cells[1])),
        "cells_share_of_record_mass_pct": (round(100 * c_cells[0] / rec_hi, 1), round(100 * c_cells[1] / rec_lo, 1)),
        "s_to_use_5K_cells_at_18A": (round(5.0 * 60 / kd["hi"]["K_per_min_adiabatic"][1]),
                                     round(5.0 * 60 / kd["lo"]["K_per_min_adiabatic"][0]))}
    # FIFTH CYCLE: the design record's SECOND key-down figure, appendix 32.56 line 2940 (7 Sep 2026 01:17): "the plate
    # is the heatsink (3 mm, 0.7 kg, 660 J/K: a 20 s key-down at 45 W warms the local patch about 15 K; the average at
    # APRS duty is a few watts)". The RA30H1317M1's copper flange bolts to that patch (same line). Its maker rates the
    # case at -30 to +100 C in operation (Maximum ratings, Tcase(OP)) and says "it is best to keep the module case
    # temperature (Tcase) below 90 C" for long-term reliability (Thermal Design of the Heat Sink); it publishes no
    # contact resistance for the flange-to-heat-sink interface (Mounting: "A thermal compound ... is recommended").
    # Taken here: the patch's heat capacity the record's figure implies; the PA's heat at the record's 45 W (30 W out
    # at the sheet's 40 % minimum, also the sheet's own worked example, 45.05 W), at 68 W (W2 F-PR-02's 113 W in with
    # the 45 W output rating at 40 %), and at 83 W (113 W in at 30 W out, outside the sheet's 40 % condition: the
    # drain rising without the output); the plate under the flange at key-on at K2's worst, +50 C inside air, taken
    # as the plate's temperature (shaded, as 32.53 requires, and with no earlier key-down's heat left in it, which K2
    # does not check); the rise LINEAR in time, the upper reading of the record's patch model (spreading into the
    # rest of the plate and loss to ambient lower it, by an amount no held document gives). The interface is TBD, so
    # every case figure below is the patch's, before the interface's own rise.
    C_PATCH = 45.0 * 20.0 / 15.0             # J/K, INFERRED from 32.56's own figure
    T_KEYON, T_REL, T_RATED = 50.0, 90.0, 100.0
    T_GATE, T_CUT = 75.0, 85.0               # K2's flange gate and C4's flange cut (section 7.2, fifth cycle)
    pa_heat = (("45 W: 30 W out at the sheet's 40 % minimum (32.52 item 6, 32.56)", 45.0),
               ("68 W: F-PR-02's 113 W in, 45 W out at 40 %", 113.0 - 45.0),
               ("83 W: 113 W in at 30 W out, outside the sheet's 40 % condition", 113.0 - 30.0))
    pc = {"patch_J_per_K": C_PATCH, "record": "32.56 line 2940: 20 s at 45 W, +15 K at the local patch",
          "T_keyon_C": T_KEYON, "T_case_reliability_C": T_REL, "T_case_rated_C": T_RATED,
          "T_flange_gate_C": T_GATE, "T_flange_cut_C": T_CUT, "by_heat": {}}
    for lbl, q in pa_heat:
        k_s = q / C_PATCH
        pc["by_heat"][lbl] = {
            "heat_W": q, "K_per_s_patch_linear": round(k_s, 3),
            "patch_C_after_s": {str(t): round(T_KEYON + k_s * t, 1) for t in (20, 30, 60)},
            "s_from_keyon_to": {"cut_85C": round((T_CUT - T_KEYON) / k_s, 1), "reliability_90C": round((T_REL - T_KEYON) / k_s, 1),
                                "rated_100C": round((T_RATED - T_KEYON) / k_s, 1)},
            "s_from_gate_to_cut": round((T_CUT - T_GATE) / k_s, 1),
            "whole_plate_K_per_60s": {"W4_403_J_per_K": round(q * 60 / 403.0, 1), "record_660_J_per_K": round(q * 60 / 660.0, 1)}}
    d11["pa_case_record_3256"] = pc
    res["d11"] = d11
    print("key-down heating:", json.dumps(kd), json.dumps(d11["pa_plate"]))
    print("the record's key-down (32.53 line 2860) against the cells:", json.dumps(d11["record_3253"]))
    print("the record's plate patch (32.56 line 2940) against the PA's case:", json.dumps(d11["pa_case_record_3256"]))

    # ------------------------------------------------------------ thermal: inside air per state
    # CORRECTED 26 Sep 2026: the heat inside now includes the cells' own I2R (the first version added it only to the
    # cells' rise over their surrounding air, not to that air), and while charging on shore the front end's and the
    # charger's loss on the LOADS' power as well as on the power into the pack.
    print("== thermal: inside-air rise (K) per state = (battery W + pack I2R) / conductance")
    th = {"pack_block": {"area_m2": round(A_BLK, 4), "G_W_per_K": (round(G_BLK[0], 3), round(G_BLK[1], 3))}}
    for st in STATES:
        enc = ENCL[st]
        glo, ghi = G[enc]
        pp = res["states"][st]["plan"]["battery_W"]
        ph = res["states"][st]["hi"]["battery_W"]
        qp = pp + pack_i2r(pp)
        qh = ph + pack_i2r(ph, R_CELL["hi"])
        g32 = G_3253.get(enc)
        th[st] = {"enclosure": enc, "G_bound": (glo, ghi), "heat_plan_W": round(qp, 1), "heat_high_W": round(qh, 1),
                  "pack_I2R_plan_W": round(pack_i2r(pp), 2),
                  "rise_plan_K": (round(qp / ghi, 1), round(qp / glo, 1)), "rise_worst_K": round(qh / glo, 1),
                  "rise_3253_G_plan_K": (round(qp / g32[1], 1), round(qp / g32[0], 1)) if g32 else None}
        print(STATE_NAME[st], enc, json.dumps(th[st]))
    # section 9.1's fans-off row (a fan failure): PS-TYP's heat on the still-air conductances, W4's bound and 32.53's
    # 2.1 W/K (fourth cycle; the row's W4 figures were hand arithmetic before)
    t = th["TYP"]
    glo, ghi = G["open_still"]
    g32 = G_3253["open_still"]
    th["TYP_fans_off"] = {"enclosure": "open_still", "G_bound": (glo, ghi), "G_3253": g32,
                          "heat_plan_W": t["heat_plan_W"], "heat_high_W": t["heat_high_W"],
                          "rise_plan_K": (round(t["heat_plan_W"] / ghi, 1), round(t["heat_plan_W"] / glo, 1)),
                          "rise_worst_K": round(t["heat_high_W"] / glo, 1),
                          "rise_3253_G_plan_K": (round(t["heat_plan_W"] / g32[1], 1), round(t["heat_plan_W"] / g32[0], 1))}
    # fifth cycle: the row keeps the fans' own power inside PS-TYP's heat, but a failed fan draws nothing. The fans'
    # battery-side watts, and the inside air and cells at +20 C on 32.53's 2.1 W/K with and without them (all the
    # fans stopped; the pack block at its mid conductance, as section 9.2's bracket).
    fan_w = {}
    for scen in ("plan", "hi"):
        shares_f, _ = load_battery_share("TYP", scen)
        fan_w[scen] = sum(c for (n, _, c, _) in shares_f if "fan" in n)
    pb_typ = res["states"]["TYP"]["plan"]["battery_W"]
    gmid = sum(G_BLK) / 2
    def air_cells(pb_):
        i2r = pack_i2r(pb_)
        air = 20.0 + (pb_ + i2r) / g32[0]
        return round(air, 1), round(air + i2r / gmid, 1)
    th["TYP_fans_off"]["fans_own_battery_W"] = (round(fan_w["plan"], 2), round(fan_w["hi"], 2))
    th["TYP_fans_off"]["overstatement_K_3253"] = (round(fan_w["plan"] / g32[0], 1), round(fan_w["hi"] / g32[0], 1))
    th["TYP_fans_off"]["overstatement_K_W4"] = (round(fan_w["plan"] / ghi, 1), round(fan_w["plan"] / glo, 1))
    th["TYP_fans_off"]["air_cells_20C_3253_fans_counted"] = air_cells(pb_typ)
    th["TYP_fans_off"]["air_cells_20C_3253_fans_drawing_nothing"] = air_cells(pb_typ - fan_w["plan"])
    print("PS-TYP, lid open, fans off", json.dumps(th["TYP_fans_off"]))
    th["charge_overlay"] = {"I_charge_A": ICHG, "P_into_pack_W": ICHG * 15.5,
                            "charge_path_heat_W": (round(charge_heat(0.0, ETA_FE[1]), 1), round(charge_heat(0.0, ETA_FE[0]), 1)),
                            "pack_I2R_W": (round(12 * (ICHG / 3) ** 2 * R_CELL["lo"], 2), round(12 * (ICHG / 3) ** 2 * R_CELL["hi"], 2))}
    print("charge overlay:", json.dumps(th["charge_overlay"]))

    OUT_POE = {"PoE outlet (delivered outside)": POE_ON}
    OUT_PD = {"USB-C outlet (delivered outside)": PD_ON}
    OUT_BOTH = {**OUT_POE, **OUT_PD}
    g_blk_mid = sum(G_BLK) / 2

    def case_heat(st, ov, charging, eta_fe, scen="plan"):
        f = state_full(st, scen, ov)
        q = f["pb"] - f["outside"]
        if charging:
            return f, q + charge_heat(f["pb"], eta_fe), 12 * (ICHG / 3) ** 2 * R_CELL["plan"]
        return f, q, pack_i2r(f["pb"])

    # ------------------------------------------------------------ ceilings per limit and case (section 9.2)
    LIMITS = [("SGP41 (battery-bay VOC), absolute operating max", 55.0, "air"),
              ("cells, charge (cell surface)", 45.0, "cell_chg"),
              ("cells, discharge (cell surface)", 60.0, "cell"),
              ("AW7915-AED WiFi card (inside air only; own rise TBD)", 70.0, "air"),
              ("LimeSDR Mini v2.4 (inside air only; own rise TBD)", 70.0, "air"),
              ("SA868 VHF module (inside air only)", 70.0, "air"),
              ("Xenarc 709GNK (inside air only)", 70.0, "air"),
              ("RM520N-GL 3GPP range (inside air only; own rise TBD)", 75.0, "air"),
              ("commercial NVMe 0 to 70 C (inside air only)", 70.0, "air")]
    CASES = [("IDLESPEC", None, "open_fans", "PS-IDLE-SPEC, lid open, fans"),
             ("TYP", None, "open_fans", "PS-TYP, lid open, fans"),
             ("TYP", None, "open_still", "PS-TYP, lid open, fans off"),
             ("TYP", OUT_BOTH, "open_fans", "PS-TYP plus both outlets, lid open, fans"),
             ("BUSY", None, "open_fans", "PS-BUSY, lid open, fans"),
             ("EMCON", None, "open_fans", "PS-EMCON, lid open, fans"),
             ("RED", None, "closed_fans", "PS-RED, lid closed, fans"),
             ("RED", None, "open_fans", "PS-RED, lid open, fans"),
             ("REDB", None, "closed_fans", "PS-RED-b, lid closed, fans")]
    ceilings = {}
    for st, ov, enc, label in CASES:
        glo, ghi = G[enc]
        g32 = G_3253.get(enc)
        rows = []
        for lname, lim, kind in LIMITS:
            if kind == "cell_chg" and ov:
                rows.append((lname, lim, None, None, None, "not charging: the outlets take the input's headroom"))
                continue
            chg = (kind == "cell_chg")
            _, q_b, p_b = case_heat(st, ov, chg, ETA_FE[1])
            _, q_w, p_w = case_heat(st, ov, chg, ETA_FE[0])
            _, q_m, p_m = case_heat(st, ov, chg, sum(ETA_FE) / 2)
            if kind == "air":
                best = lim - (q_b + p_b) / ghi
                worst = lim - (q_w + p_w) / glo
                r3253 = (round(lim - (q_m + p_m) / g32[0], 1), round(lim - (q_m + p_m) / g32[1], 1)) if g32 else None
            else:
                best = ceiling(lim, q_b, p_b, ghi, G_BLK[1])
                worst = ceiling(lim, q_w, p_w, glo, G_BLK[0])
                r3253 = (round(ceiling(lim, q_m, p_m, g32[0], g_blk_mid), 1),
                         round(ceiling(lim, q_m, p_m, g32[1], g_blk_mid), 1)) if g32 else None
            rows.append((lname, lim, round(worst, 1), round(best, 1), r3253, ""))
        ceilings[label] = rows
    th["ceilings"] = ceilings
    for k, rows in ceilings.items():
        print("ambient ceilings (worst, best on the W4 bound; 32.53 G):", k)
        for r in rows:
            print("     ", r)

    # ------------------------------------------------------------ allowed simultaneous modes (section 7.1)
    # Every row judged against: the declared CONTINUOUS pack current (10 A) at every stack voltage down to the
    # gauge's under-voltage trip (10.0 V), the declared peak (18 A) and the gauge's 20 A / 2 s trip, and the cells'
    # discharge (60 C) or charge (45 C) window at +20 C ambient (the runtime requirement's own condition), with the
    # same pack model as section 9.2.
    MODES = [("PS-IDLE", "IDLE", None, "open_fans", False),
             ("PS-IDLE-SPEC", "IDLESPEC", None, "open_fans", False),
             ("PS-EMCON", "EMCON", None, "open_fans", False),
             ("PS-RED, lid closed", "RED", None, "closed_fans", False),
             ("PS-RED-b, lid closed", "REDB", None, "closed_fans", False),
             ("PS-TYP", "TYP", None, "open_fans", False),
             ("PS-TYP plus PoE", "TYP", OUT_POE, "open_fans", False),
             ("PS-TYP plus USB-C", "TYP", OUT_PD, "open_fans", False),
             ("PS-TYP plus both outlets", "TYP", OUT_BOTH, "open_fans", False),
             ("PS-BUSY", "BUSY", None, "open_fans", False),
             ("PS-BUSY plus both outlets", "BUSY", OUT_BOTH, "open_fans", False),
             ("PS-TYP while charging on shore at 3 A", "TYP", None, "open_fans", True),
             # third cycle: the PA keyed on its own, and the heater overlay
             ("PA keyed alone over PS-IDLE-SPEC, PA at 75 W", "IDLESPEC", PA_75, "open_fans", False),
             ("PA keyed alone over PS-IDLE-SPEC, PA at 113 W", "IDLESPEC", PA_113, "open_fans", False),
             ("PA keyed alone over PS-TYP, PA at 75 W", "TYP", PA_75, "open_fans", False),
             ("PA keyed alone over PS-TYP, PA at 113 W", "TYP", PA_113, "open_fans", False),
             ("PS-TYP plus the heater (cold overlay)", "TYP", {"pack heater mat (cold overlay)": HEAT_ON}, "open_fans", False),
             ("PS-RED plus the heater (cold overlay), lid closed", "RED", {"pack heater mat (cold overlay)": HEAT_ON}, "closed_fans", False)]
    KD_S = 60.0                               # the key-down bound of section 7.2, per key-down
    modes = {}
    print("== allowed modes: pack current (A) at stack 16.8 / 14.4 / 12.0 / 10.0 V, plan and high; heat; cells at +20 C")
    for label, st, ov, enc, charging in MODES:
        glo, ghi = G[enc]
        g32 = G_3253[enc]
        lim = 45.0 if charging else 60.0
        f_p = state_full(st, "plan", ov)
        f_h = state_full(st, "hi", ov)
        row = {"battery_W_plan": round(f_p["pb"], 1), "battery_W_high": round(f_h["pb"], 1),
               "outside_W": round(f_p["outside"], 1), "enclosure": enc, "limit_C": lim}
        if not charging:
            row["I_plan"] = {str(v): round(pack_current(f_p["p_vbat"], v), 1) for v in (16.8, 14.4, 12.0, V_CUV)}
            row["I_high"] = {str(v): round(pack_current(f_h["p_vbat"], v), 1) for v in (16.8, 14.4, 12.0, V_CUV)}
            # the stack voltage below which the current passes a limit: V = p_vbat / I + I x R_DIST
            for tag, f in (("plan", f_p), ("high", f_h)):
                for nm, ilim in (("cont", I_CONT), ("peak", I_PEAK)):
                    v_x = f["p_vbat"] / ilim + ilim * R_DIST
                    row["V_below_which_over_%s_%s" % (nm, tag)] = round(v_x, 2)
        _, q_b, p_b = case_heat(st, ov, charging, ETA_FE[1])
        _, q_w, p_w = case_heat(st, ov, charging, ETA_FE[0])
        _, q_m, p_m = case_heat(st, ov, charging, sum(ETA_FE) / 2)
        row["heat_inside_plan_W"] = round(q_m + p_m, 1)
        row["pack_I2R_W"] = round(p_m, 2)
        row["cells_20C_W4"] = (round(cell_temp(20, q_b, p_b, ghi, G_BLK[1]), 1), round(cell_temp(20, q_w, p_w, glo, G_BLK[0]), 1))
        row["cells_20C_3253"] = (round(cell_temp(20, q_m, p_m, g32[1], g_blk_mid), 1), round(cell_temp(20, q_m, p_m, g32[0], g_blk_mid), 1))
        row["ceiling_W4"] = (round(ceiling(lim, q_w, p_w, glo, G_BLK[0]), 1), round(ceiling(lim, q_b, p_b, ghi, G_BLK[1]), 1))
        row["ceiling_3253"] = (round(ceiling(lim, q_m, p_m, g32[0], g_blk_mid), 1), round(ceiling(lim, q_m, p_m, g32[1], g_blk_mid), 1))
        if label.startswith("PA keyed alone"):
            # a burst: the cells' adiabatic rise over one 60 s key-down at the highest current the row reaches, capped
            # at the 18 A the in-key guard C4 allows, on 600 g of cells at 0.8 to 1.1 J/gK (as section 7.2)
            i_max = min(max(row["I_plan"].values()), I_PEAK)
            rise = [round(12 * (i_max / 3) ** 2 * R_CELL[rk] * KD_S / (12 * 50.0 * cp), 2)
                    for rk, cp in (("lo", 1.1), ("hi", 0.8))]
            row["key_down_I_max_A"] = round(i_max, 1)
            row["key_down_rise_K_per_60s"] = rise
        if "heater" in label:
            # cold overlay: the air round the pack at the envelope's -20 C, all the heat (the mat's included) into it
            row["air_at_minus20C_W4"] = (round(-20 + (q_w + p_w) / glo, 1), round(-20 + (q_b + p_b) / ghi, 1))
            row["air_at_minus20C_3253"] = (round(-20 + (q_m + p_m) / g32[0], 1), round(-20 + (q_m + p_m) / g32[1], 1))
        modes[label] = row
        print(label, json.dumps(row))
    res["modes"] = modes
    # FIFTH CYCLE: the largest shift main's R17 (5 mOhm more in the pack path) makes in the rows above that discharge
    # the pack, and in the eight power states of section 4: battery W at 14.4 V, the pack current at the gauge's 10.0 V where it is finite, and the inside air
    # (so the cells) on the lowest conductance of the row's enclosure, W4's and 32.53's. The "stack voltage below
    # which" figures move up by I x 5 mOhm: 0.05 V at 10 A, 0.09 V at 18 A.
    dm = {"battery_W": 0.0, "I_at_10V_A": 0.0, "air_K_W4_lowest_G": 0.0, "air_K_3253_lowest_G": 0.0,
          "V_below_which_shift_V": {"10 A": round(I_CONT * R_R17, 3), "18 A": round(I_PEAK * R_R17, 3)}}
    for label, st, ov, enc, charging in MODES + [(STATE_NAME[x], x, None, ENCL[x], False) for x in STATES]:
        if charging:
            continue
        for scen in ("plan", "hi"):
            f = state_full(st, scen, ov)
            d_pb = battery_side(f["p_vbat"], 14.4, R_DIST_MAIN) - f["pb"]
            i0, i1 = pack_current(f["p_vbat"], V_CUV), pack_current(f["p_vbat"], V_CUV, R_DIST_MAIN)
            dm["battery_W"] = max(dm["battery_W"], round(d_pb, 2))
            if i1 != float("inf"):
                dm["I_at_10V_A"] = max(dm["I_at_10V_A"], round(i1 - i0, 2))
            dm["air_K_W4_lowest_G"] = max(dm["air_K_W4_lowest_G"], round(d_pb / G[enc][0], 2))
            dm["air_K_3253_lowest_G"] = max(dm["air_K_3253_lowest_G"], round(d_pb / G_3253[enc][0], 2))
    res["d11"]["main_pack_path_R17"]["largest_shift_in_sections_4_and_7_1"] = dm
    print("main's R17, the largest shift in section 7.1's discharge rows and the power states:", json.dumps(dm))
    # the cells at +20 C ambient in PS-TYP (discharge): the runtime requirement's own condition
    th["cells_TYP_20C"] = modes["PS-TYP"]["cells_20C_W4"] + (modes["PS-TYP"]["pack_I2R_W"],)
    print("cells in PS-TYP at +20 C ambient, lid open, fans (C, best, worst, pack I2R W):", th["cells_TYP_20C"])
    res["thermal"] = th

    # ------------------------------------------------------------ reconciliation of the idle figures
    rec = {}
    for st in ("IDLE", "IDLESPEC"):
        shares, pb = load_battery_share(st, "plan")
        rec[st] = {"battery_W": round(pb, 2), "load_W": res["states"][st]["plan"]["load_W"]}
    res["reconcile"] = rec
    print("reconcile:", json.dumps(rec))

    # every load, plan state shares for PS-IDLE-SPEC and PS-TYP (battery-side)
    for st in ("IDLESPEC", "TYP", "ALLTX"):
        print("== shares", STATE_NAME[st])
        for a, b, c, d in sorted(res["shares"][st], key=lambda x: -x[2]):
            print("   %-44s load %6.2f  battery %6.2f  %s" % (a, b, c, d))
    json.dump(res, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "pwr_budget.json")
