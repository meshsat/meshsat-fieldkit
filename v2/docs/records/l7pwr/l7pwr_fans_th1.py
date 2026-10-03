#!/usr/bin/env python3
"""l7pwr_fans_th1.py: Layer 7 record l7pwr (MESHSAT-1357, 3 October 2026): the three Layer 7 items of L4-E9's prototype
qualification route (L4-POWER-ARCHITECTURE.md section 5d) that do not wait on the solar guard's round:
  1. THE FANS (D-18, register row E11-35 / R-179, R-142, R-150): the five IP68 internal fans of the ruling of 7 September 2026
     (appendix 32.53 item 2), one per CM5 cooler on board B's slot headers and two mixers on board E's sensor controller, judged
     candidate by candidate on the makers' printed rows against the supplies they are drawn on (board E's VSYS_E, 9.494 to
     17.375 V under L4-E11's draft; board B's 5 V slot rail), the start-current limits of L4-E11 17a, the inside air, REQ-043's
     IP68 and -20 C, the tachometer and PWM lines the generators draw, and the mounting the case records give;
  2. THE T-H1 MOCK-UP SPECIFICATION: the complete bill of the empty-case conductance test (records/l4e12/T-H1-PROCEDURE-DRAFT.md),
     each item with a public price read and dated or NOT READ, the totals per currency, and the pass lines restated;
  3. THE DOCK CONTACT AND WIRING PULSE CAPABILITY (E11-38): the dock lead's 24 AWG against the hard short's 566 A for 4.5 us and
     the eFuse's retry duty, on published relations (Onderdonk, Preece, ECSS-Q-ST-30-11C Rev.2 Annex C); the contact's
     capability is the maker's question, drafted beside this script.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. A maker's figure is MAKER, this script's
arithmetic MODELED, a stated assumption ASSUMPTION, a figure no document prints NOT READ. Every input is pinned by sha256 and
every maker row is read from the pinned document (pdftotext), never typed. No generator, registry, interface or other record is
edited: what another layer must change is a FINDING with its row. Output: `python3 v2/docs/records/l7pwr/l7pwr_fans_th1.py`
from the repository root (the integrator regenerates the committed .out with _bin/regen_out.py)."""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

PINS = {
    "sunon_ip": "v2/vendor/fans/sunon-ip56-ip68-gr487-fan-series-239-E-2023-04-07.pdf",
    "sunon_cat": "v2/vendor/fans/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf",
    "sanyo": "v2/vendor/fans/sanyo-denki-splash-proof-fan-pages-2026-10-03.md",
    "samesky": "v2/vendor/fans/samesky-cfm-60bg68-dc-axial-fan-2024-09-12.pdf",
    "cooler": "v2/vendor/cm5/rpi-cm5-cooler-product-brief-2024-12.pdf",
    "precidip": "v2/vendor/precidip/precidip-catalog-slc-2018-03-20.pdf",
    "precidip_x": "v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf",
    "sunon_b6": "v2/docs/records/l7pwr/inputs/sunon-gf60151b6-spec-reading-2026-10-03.md",
    "ecss": "v2/docs/records/l7pwr/inputs/ecss-q-st-30-11c-rev2-wires-annex-c.md",
    "fusing": "v2/docs/records/l7pwr/inputs/fusing-current-sources-2026-10-03.md",
    "prices": "v2/docs/records/l7pwr/inputs/prices-2026-10-03.json",
    "findchips": "v2/docs/records/l7pwr/inputs/findchips-fans-heaters-2026-10-03.json",
    "th1": "v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md",
    "l4e11": "v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md",
    "l4e11_aux": "v2/docs/records/l4e11/apply_gen_sch_e_aux.py",
    "l4e12": "v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md",
    "l4e9": "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
    "gen_e": "v2/ecad/tools/gen_sch_e.py",
    "gen_b": "v2/ecad/tools/gen_sch_b.py",
    "panel": "v2/ecad/tools/panel1450.py",
    "reqs": "v2/ecad/tools/pcb_requirements.yaml",
    "margins": "v2/docs/CASE-MARGINS.md",
    "rta": "v2/docs/reviews/READY-TO-ACT.md",
}

# ---------------------------------------------------------------- constants with their status
R_HEATER_OHM = 6.8            # READY-TO-ACT 5.2: aluminium-housed wirewound resistors, 50 W class, 6.8 ohm (the T-H1 draft's heaters)
BUCK_EFF = 0.90               # ASSUMPTION: the efficiency of a 12.0 V step-down for the mixers (board A's VHEAT buck is a TPS62933; its
                              # curve is not read here); the 5-to-12 V step-up for the coolers is given the same figure
PLAN_MIXER_W = 1.44           # L4-E12 13.3: pwr_budget.py's "two mixer fans" plan figure (W, both), tier R
PLAN_COOLER_W = (0.57, 0.56, 0.55)   # L4-E12 13.3: the three cooler fans in the profile (W), tier R
HOLD_FANS_W = 1.950           # T-H1 draft section 1: the heat stage's and the hold's fans (slot 3's cooler and the two mixers), model
PROFILE_FANS_W = 2.970        # T-H1 draft section 1: the profile's five fans, model
LINE_PER_W = 0.100            # L4-E12 13.3: E5's line moves 0.100 W/K per W into the case
CASE_FREE_M3 = 0.375 * 0.261 * 0.1035   # MODELED: the base's 375 x 261 at Z 15.3 (CASE-MARGINS 2.2) to the plate's underside 103.5,
                                        # the boards' and modules' volume not subtracted (an upper bound of the free air)
AWG24_D_MM = 0.127 * 92 ** ((36 - 24) / 39.0)   # the AWG series' definition (0.5106 mm)
CU_MELT_C = 1083.0            # the fusing note's melting temperature of copper
CU_RHO_PER_M = 0.105          # ECSS-Q-ST-30-11C Rev.2 Table C-1: AWG 24 at 20 C, ohm/m
CU_C_J_KGK = 385.0            # textbook specific heat of copper (ASSUMPTION of the adiabatic rise)
CU_DENS = 8960.0              # textbook density of copper (ASSUMPTION of the adiabatic rise)
PREECE_CU = 10244.0           # the fusing note's Preece constant for copper, d in inches
SHORT_A = 566.0               # L4-E11 17a case (2): the hard short's ceiling through the contact (I)
SHORT_S = 4.5e-6              # L4-E11 17a case (2): at most 4.5 us
SHORT_I2T = 1.441             # L4-E11 17a case (2): A2s (I)
RETRY_A = 1.802               # L4-E11 17a cases (1), (3), (4): the setting's top (G-derived, I)
RETRY_DUTY = 0.75             # L4-E11 17a case (4)
VSYS_E_FLOOR = 9.494          # L4-E11 17a: VSYS_E at the least limit at the supplement floor (V)
VSYS_E_TOP = 17.375           # L4-E11: VSYS's top with the charge held (V)
I_OL_MIN = 1.471              # L4-E11 17a: U42's least limit (A)
START_BOTH = 0.3356           # L4-E11 17a: both fans together, each (A)
START_ONE = 0.5713            # L4-E11 17a: one at a time (A)
U12_A = 0.8                   # gen_sch_e.py: U12's declared load on the auxiliary domain (A)
SLOT_5V = 5.1                 # ASSEMBLY.md: the slot rails at 5.1 V
T_IN_MIN, T_BOARD_MAX, T_HOLD = -20.0, 62.1, 68.65   # REQ-043's floor; L4-E12's board air at the margin; the hold's trigger (mixed air)


def refuse(msg):
    sys.stderr.write("l7pwr_fans_th1: %s; refusing\n" % msg)
    sys.exit(3)


def sha_of(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def text_of(rel):
    return open(os.path.join(TOP, rel), encoding="utf-8").read()


def pdf_text(rel, first=None, last=None):
    cmd = ["pdftotext", "-layout"]
    if first:
        cmd += ["-f", str(first), "-l", str(last or first)]
    r = subprocess.run(cmd + [os.path.join(TOP, rel), "-"], capture_output=True, text=True)
    if r.returncode != 0:
        refuse("pdftotext could not read %s" % rel)
    return r.stdout


def need(text, pat, what, flags=re.M | re.S):
    m = re.search(pat, text, flags)
    if not m:
        refuse("%s not parsed" % what)
    return m


def f(x, n=3):
    return ("%%.%df" % n) % x


# ---------------------------------------------------------------- the readings
def read_sites(R):
    ge = text_of(PINS["gen_e"]); gb = text_of(PINS["gen_b"]); aux = text_of(PINS["l4e11_aux"])
    need(ge, r'ph\("J_FAN%s" % n, 3, "mixer fan %s under the plate \(12 V class fan on the pack node, low-side PWM, tachometer\)" % n, \{"1": "CELL_F", "2": "FAN%s_SW" % n, "3": "FAN%s_TACH" % n\}\)', "board E's mixer header")
    need(ge, r'"2N7002 fan %s low-side switch', "board E's low-side FET")
    need(ge, r'r\("R%s" % \("46" if n == "1" else "47"\), "10k", "FAN%s_TACH" % n, "\+3V3_E6"\)', "board E's tach pull-up")
    need(ge, r'"11": "FAN1_PWM", "12": "FAN2_PWM", "13": "FAN1_TACH", "14": "FAN2_TACH"', "U10's fan pins")
    need(ge, r'"SS14 flyback across fan %s" % n, "SMB", \{"1": "CELL_F", "2": "FAN%s_SW" % n\}', "board E's flyback diodes")
    need(ge, r'loads=\{"P_CP": 9.0, "U12": 0.8, "J_FAN1": 0.1, "J_FAN2": 0.1\}', "CELL_F's declared fan loads")
    need(aux, r'J_FAN1 and J_FAN2 pin 1 and the flyback diodes D7 and D8 on VSYS_E', "L4-E11's draft moving the fans to VSYS_E")
    need(aux, r'loads=\{"U12": 0.8, "J_FAN1": 0.1, "J_FAN2": 0.1\}', "VSYS_E's drafted loads")
    mb = need(gb, r'part\("J_FAN%d" % s, "Connector_Generic", "Conn_01x04", "IP68 cooler fan of S%d \(JST-SH 1.0\): 5V GND TACHO PWM" % s, "SH4", \{"1": n5, "2": "GND", "3": "FAN_TACHO%d" % s, "4": "FAN_PWM%d" % s, "MP": "NC"\}, "(C\d+)"\)', "board B's cooler header")
    need(gb, r'"J_FAN%d" % s: 0.1,\s+# the slot\'s IP68 cooler fan', "board B's declared cooler fan current")
    need(gb, r'n5 = "\+5V_S%d" % s', "the slot rail's net")
    R["sites"] = {
        "mixers": "board E J_FAN1, J_FAN2: 3 pins (1 CELL_F, 2 FANn_SW, 3 FANn_TACH); the low side chopped by Q9/Q10 (2N7002) from U10's FAN1_PWM/FAN2_PWM (GPIO8, 9), the tach pulled to +3V3_E6 by 10k into GPIO10, 11; SS14 flyback D7/D8; 0.1 A declared each; L4-E11's draft apply_gen_sch_e_aux.py moves pin 1 and the diodes to VSYS_E",
        "coolers": "board B J_FAN1..3: JST-SH 1.0 4 pins (1 +5V_Sn, 2 GND, 3 FAN_TACHOn, 4 FAN_PWMn) to the module's Fan_Tacho (1.8k pull-up to CM5_3.3V) and Fan_PWM (open drain); 0.1 A declared on the slot's 5.1 V rail; the header code %s" % mb.group(1),
    }
    l4 = text_of(PINS["l4e11"])
    for s in ("9.494 V", "17.375 V", "0.3356 A", "0.5713 A", "1.471 A", "E11-39"):
        need(l4, re.escape(s), "L4-E11's %s" % s)
    rq = text_of(PINS["reqs"])
    m = need(rq, r"^  - id: REQ-043\n(?:    .*\n)*?    acceptance: >-\n((?:      .*\n)+)", "REQ-043's acceptance", flags=re.M)
    R["req043"] = " ".join(m.group(1).split())
    th = text_of(PINS["th1"])
    need(th, r"a current-moulding Peli 1450 with the 1450PF frame and a 3 mm aluminium plate blank", "T-H1's configuration")
    need(th, r"Same Sky\s+CFM-6025BG68, 12 V, the -22 variant", "T-H1's stand-in mixers")


def read_candidates(R):
    """Every maker row from the pinned document (MAKER). Fields the document does not print are None (NOT READ)."""
    ip = pdf_text(PINS["sunon_ip"])
    cat = pdf_text(PINS["sunon_cat"])
    ss = pdf_text(PINS["samesky"])
    b6 = text_of(PINS["sunon_b6"])
    sanyo = text_of(PINS["sanyo"])

    def sunon_ip_row(model):
        m = need(ip, re.escape(model) + r"\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "Sunon brochure row " + model)
        return dict(v=float(m.group(1)), rpm=float(m.group(2)), cfm=float(m.group(3)), inh2o=float(m.group(4)), dba=float(m.group(5)), g=float(m.group(6)))

    def sunon_cat_row(model):
        m = need(cat, re.escape(model) + r"\s+(\d+)\s+(\d+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "Sunon catalogue row " + model)
        return dict(v=float(m.group(1)), ma=float(m.group(2)), w=float(m.group(3)), rpm=float(m.group(4)), cfm=float(m.group(5)), inh2o=float(m.group(6)), dba=float(m.group(7)), g=float(m.group(8)))

    def sanyo_row(model):
        m = need(sanyo, r"^\| " + re.escape(model) + r" \(([^)]+)\) \| ([0-9a-f]{16}) \| ([^|]+) \| (\d+) \| ([\d.]+) to ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| (\d+) \| ([\d.]+), ([\d.]+) \| (\d+), ([\d.]+) \| (\d+) \| (-?\d+) to \+(\d+) \| (\d+)/60 C \((\d+)/40 C\) \| (\d+) \| ([^|]+) \|$", "Sanyo row " + model)
        return dict(family=m.group(1), sha=m.group(2), frame=m.group(3).strip(), v=float(m.group(4)), vlo=float(m.group(5)), vhi=float(m.group(6)), a=float(m.group(7)), w=float(m.group(8)), rpm=float(m.group(9)),
                    m3min=float(m.group(10)), cfm=float(m.group(11)), pa=float(m.group(12)), inh2o=float(m.group(13)), dba=float(m.group(14)), tlo=float(m.group(15)), thi=float(m.group(16)),
                    life60=float(m.group(17)), life40=float(m.group(18)), g=float(m.group(19)), io=m.group(20).strip())

    # Same Sky: the family sheet's rows
    ssm = need(ss, r"12 Vdc input models\s+10\.8\s+12\s+13\.2\s+Vdc", "Same Sky 12 V input range")
    need(ss, r"24 Vdc input models\s+21\.6\s+24\s+26\.4\s+Vdc", "Same Sky 24 V input range")
    need(ss, r"operating temperature\s+-10\s+70\s+", "Same Sky operating temperature")
    need(ss, r"life expectancy\s+at 40.C, 65% RH, 90% confidence level\s+70,000\s+hours", "Same Sky life")
    need(ss, r"IP level\s+IP68", "Same Sky IP level")
    need(ss, r"soft start\s+on all models", "Same Sky soft start")
    m135 = need(ss, r"CFM-6025BG68-135-253\s+12\s+10\.8~13\.2\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d,]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "Same Sky -135-253 row")
    # Sunon GF60151B6 sheet reading (the family's ranges)
    need(b6, r"\| Operating voltage range \| 4\.5 to 13\.8 VDC \|", "Sunon B6 range")
    need(b6, r"\| Operating temperature range \| -10 to \+70 deg\. C \|", "Sunon B6 temperature")
    need(b6, r"\| Life expectancy \| 70,000 hours at 40 deg\. C", "Sunon B6 life")
    need(b6, r"\| Starting current \| not printed \|", "Sunon B6 starting current")

    C = {}
    s = sanyo_row("9WL0612P4H001"); C["9WL0612P4H001"] = dict(maker="Sanyo Denki", site="mixer", size="60 x 60 x 25, aluminium frame", **s, ip="IP68", io_note="pulse sensor and PWM (4 wires)", doc="the maker's product-database page, transcribed (sanyo-denki-splash-proof-fan-pages-2026-10-03.md)", start_a=None)
    s = sanyo_row("9WL0612P4J001"); C["9WL0612P4J001"] = dict(maker="Sanyo Denki", site="mixer", size="60 x 60 x 25, aluminium frame", **s, ip="IP68", io_note="pulse sensor and PWM", doc="as above", start_a=None)
    s = sanyo_row("9WL0624P4H001"); C["9WL0624P4H001"] = dict(maker="Sanyo Denki", site="mixer (24 V class)", size="60 x 60 x 25, aluminium frame", **s, ip="IP68", io_note="pulse sensor and PWM", doc="as above", start_a=None)
    s = sanyo_row("9WPA0412P6G001"); C["9WPA0412P6G001"] = dict(maker="Sanyo Denki", site="cooler", size="40 x 40 x 20, plastic frame, ribbed", **s, ip="IP68", io_note="pulse sensor and PWM (4 wires)", doc="as above", start_a=None)
    s = sanyo_row("9WPA0424P6G001"); C["9WPA0424P6G001"] = dict(maker="Sanyo Denki", site="cooler (24 V class)", size="40 x 40 x 20, plastic frame, ribbed", **s, ip="IP68", io_note="pulse sensor and PWM", doc="as above", start_a=None)
    r7 = sunon_ip_row("GF60151B7-1E00U-AE9"); c7 = sunon_cat_row("GF60151B7-1E000-AE9")
    C["GF60151B7-1E00U-AE9"] = dict(maker="Sunon", site="mixer", size="60 x 60 x 15, 2-ball", v=12.0, vlo=4.5, vhi=13.8, a=c7["ma"] / 1000.0, w=c7["w"], rpm=r7["rpm"], cfm=r7["cfm"], m3min=r7["cfm"] * 0.3048 ** 3,
                                    pa=r7["inh2o"] * 249.089, inh2o=r7["inh2o"], dba=r7["dba"], tlo=-10.0, thi=70.0, life60=None, life40=70000.0, g=r7["g"], ip="IP68", io_note="two lead wires: no tachometer, no PWM",
                                    doc="the maker's brochure 239-E (2023/04/07) row and the catalogue 240-A extract's power column; range, temperature and life INFERRED from the GF60151B6 specification for approval (the family), a distributor-hosted Sunon document, not filed", start_a=None, range_inferred=True)
    r3 = sunon_ip_row("GF40282B3-1000U-SEP")
    C["GF40282B3-1000U-SEP"] = dict(maker="Sunon", site="cooler (24 V class)", size="40 x 40 x 28, 2-ball", v=24.0, vlo=None, vhi=None, a=None, w=None, rpm=r3["rpm"], cfm=r3["cfm"], m3min=r3["cfm"] * 0.3048 ** 3, pa=r3["inh2o"] * 249.089, inh2o=r3["inh2o"],
                                    dba=r3["dba"], tlo=None, thi=None, life60=None, life40=None, g=r3["g"], ip="IP68", io_note="not printed in the brochure", doc="the maker's brochure 239-E (2023/04/07) row only; its specification sheet was not found on sunon.com from this host", start_a=None)
    C["CFM-6025BG68-135-253-22"] = dict(maker="Same Sky", site="mixer", size="60 x 60 x 25, ball", v=12.0, vlo=10.8, vhi=13.2, a=float(m135.group(2)), w=float(m135.group(4)), rpm=float(m135.group(5).replace(",", "")), cfm=float(m135.group(6)),
                                        m3min=float(m135.group(6)) * 0.3048 ** 3, inh2o=float(m135.group(7)), pa=float(m135.group(7)) * 249.089, dba=float(m135.group(8)), tlo=-10.0, thi=70.0, life60=None, life40=70000.0, g=None, ip="IP68",
                                        io_note="tachometer and PWM (the -22 suffix); soft start on all models (the start current itself not printed)", doc="the maker's series sheet CFM-60BG68 of 09/12/2024 (filed)", start_a=None,
                                        a_typ=float(m135.group(1)), w_typ=float(m135.group(3)))
    R["cands"] = C
    # the CM5 cooler and the Preci-Dip pages
    cb = pdf_text(PINS["cooler"])
    need(cb, r"passive heatsink", "the cooler is passive")
    need(cb, r"56 mm . 41 mm . 12\.7 mm", "the cooler's form factor")
    need(cb, r"List price:\s+\$5", "the cooler's list price")
    pd_ = pdf_text(PINS["precidip"])
    need(pd_, r"OPERATING CURRENT\s+Max\. 3\.5 A / 7A peak", "Preci-Dip's SMD series peak row")
    need(pd_, r"813-S1-NNN-10-XXX101", "Preci-Dip's 813 ordering row")
    need(pd_, r"OPERATING CURRENT\s+Max\. 3\.5 A\s+CONTACT RESISTANCE\s+10 m. \(static measurement, halfway position\)", "Preci-Dip's 813 current and resistance")
    need(pd_, r"-55 \.\.\. \+125 .C \(-55 .. \+85 .C with music wire spring\)", "Preci-Dip's temperature line")


def judge(R):
    """Each candidate against the site's supply, REQ-043, the air and the lines the generators draw."""
    J = {}
    for k, c in R["cands"].items():
        site = "mixer" if c["site"].startswith("mixer") else "cooler"
        if site == "mixer":
            lo, hi = VSYS_E_FLOOR, VSYS_E_TOP
        else:
            lo, hi = SLOT_5V, SLOT_5V
        rng = None if c["vlo"] is None else (c["vlo"] <= lo and c["vhi"] >= hi)
        temp = None if c["tlo"] is None else (c["tlo"] <= T_IN_MIN and c["thi"] >= T_BOARD_MAX)
        hold = None if c["thi"] is None else (c["thi"] >= T_HOLD)
        J[k] = dict(site=site, supply=(lo, hi), range_ok=rng, temp_ok=temp, hold_ok=hold, ip68=(c["ip"] == "IP68"), tach=("tach" in c["io_note"] or "pulse" in c["io_note"]),
                    pwm=("PWM" in c["io_note"]), life_at_60=c["life60"] is not None, start_read=c["start_a"] is not None,
                    # the fan at 12.0 V behind a step-down (mixers) or step-up (coolers) from the site's supply, at full speed (MODELED, BUCK_EFF an ASSUMPTION)
                    i_at_floor=None if c["w"] is None else c["w"] / (BUCK_EFF * lo))
    R["judge"] = J
    # none covers the supply directly
    R["no_direct_fan"] = all(v["range_ok"] is not True for v in J.values())
    R["sel"] = {"mixer": "9WL0612P4H001", "cooler": "9WPA0412P6G001"}
    R["alt"] = {"mixer": "GF60151B7-1E00U-AE9", "cooler": "GF40282B3-1000U-SEP"}
    m = R["cands"][R["sel"]["mixer"]]; c = R["cands"][R["sel"]["cooler"]]
    i_each = m["w"] / (BUCK_EFF * VSYS_E_FLOOR)
    i_both = 2 * i_each
    i_plan = PLAN_MIXER_W / (BUCK_EFF * VSYS_E_FLOOR)
    R["down"] = dict(
        mixer_w_each=m["w"], mixer_w_both=2 * m["w"], i_mixer_each_full=i_each, i_mixer_both_full=i_both,
        vsys_e_total_full=U12_A + i_both, vsys_e_total_plan=U12_A + i_plan, i_mixers_plan=i_plan,
        pct_of_least=100.0 * (U12_A + i_both) / I_OL_MIN, over_declared=U12_A + i_both - 1.0,
        each_under_both_limit=i_each <= START_BOTH, each_under_one_limit=i_each <= START_ONE,
        cooler_w_each=c["w"], cooler_i_slot_full=c["w"] / (BUCK_EFF * SLOT_5V), cooler_i_12v=c["a"],
        heat_hold_full=c["w"] + 2 * m["w"], heat_hold_plan=HOLD_FANS_W, heat_prof_full=3 * c["w"] + 2 * m["w"], heat_prof_plan=PROFILE_FANS_W,
        line_shift_hold=LINE_PER_W * (c["w"] + 2 * m["w"] - HOLD_FANS_W),
        flow_mixers_m3s=2 * m["m3min"] / 60.0, flow_coolers_m3s=3 * c["m3min"] / 60.0, case_m3=CASE_FREE_M3,
        changes_per_s=2 * m["m3min"] / 60.0 / CASE_FREE_M3,
        rep_mixers_m3min=(2 * R["cands"]["GF60151B7-1E00U-AE9"]["m3min"]),
    )
    # the model's representatives (L4-E12 13.2): GF60151B9 10.6 CFM and B6 21.3 CFM for the mixers, MF30060V2 3.7 CFM for the coolers
    cat = pdf_text(PINS["sunon_cat"])
    b9 = need(cat, r"GF60151B9-1E000-AE9\s+12\s+32\s+0\.39\s+2300\s+([\d.]+)", "B9 flow"); b6 = need(cat, r"GF60151B6-1E000-AE9\s+12\s+125\s+1\.50\s+4500\s+([\d.]+)", "B6 flow")
    mf = need(cat, r"MF30060V2-10000-A99\s+5\s+72\s+0\.36\s+7100\s+([\d.]+)", "MF30060V2 flow")
    R["rep"] = dict(mixers_cfm=(float(b9.group(1)), float(b6.group(1))), cooler_cfm=float(mf.group(1)))


def mounting(R):
    p = text_of(PINS["panel"])
    stack = need(p, r'STACK = \[\("VHB 5952 pads under the dock strip", ([\d.]+)\), \("board E dock strip", ([\d.]+)\), \("blind-mate gap spacer", ([\d.]+)\),\s+\("board A", ([\d.]+)\), \("A-to-B bay spacer", ([\d.]+)\), \("board B", ([\d.]+)\)\]', "panel1450's stack")
    b_top = round(sum(float(stack.group(i)) for i in range(1, 7)), 2)
    face = float(need(p, r"FACE_TOP_Z = round\(LEG_TOP_Z \+ PELI\[\"ring_t\"\] \+ PLATE\[2\], 2\)\s+# ([\d.]+) above the case floor", "FACE_TOP_Z's printed value").group(1))
    gap = float(need(p, r"BACKER_GAP = ([\d.]+)", "BACKER_GAP").group(1)); bt = float(need(p, r"BACKER_T = ([\d.]+)", "BACKER_T").group(1))
    strip_t = need(p, r"STRIP_T = \((-?[\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\)", "STRIP_T")
    hs = need(p, r"The heatsink is ([\d.]+) mm \(module ([\d.]+) \+ ([\d.]+), base ([\d.]+), fins ([\d.]+) from scene\.py", "panel1450's heatsink note")
    fan = need(p, r'\(\(-87\.5, (48\.0), -57\.5, (78\.0)\), (30\.0), "CM5 slot 1 fan"', "panel1450's fan envelope")
    mon = float(need(p, r"NORTH of the monitor's edge at Y \+([\d.]+)", "the monitor's north edge").group(1))
    plate_under = face - 3.0
    backer_under = plate_under - gap - bt
    module_stack = float(hs.group(2)) + float(hs.group(3))
    cooler_h = 12.7
    fan_t = 20.0
    R["mount"] = dict(b_top=b_top, face=face, plate_under=plate_under, backer_under=backer_under, strip_t_y=float(strip_t.group(2)), env_hs=float(hs.group(1)), module_stack=module_stack,
                      cooler_h=cooler_h, fan_t=fan_t, top_on_cooler=b_top + module_stack + cooler_h + fan_t, top_on_env=b_top + float(hs.group(1)) + fan_t, env_fan_y=(float(fan.group(1)), float(fan.group(2))), env_fan_h=float(fan.group(3)),
                      mon_edge=mon, fan_y=(48.0, 88.0), fan_x_slot1=(-72.5 - 20.0, -72.5 + 20.0), cooler_x_slot1=(-93.0, -52.0))
    R["mount"]["clear_backer_cooler"] = backer_under - R["mount"]["top_on_cooler"]
    R["mount"]["clear_backer_env"] = backer_under - R["mount"]["top_on_env"]
    R["mount"]["clear_plate_cooler"] = plate_under - R["mount"]["top_on_cooler"]
    R["mount"]["fan_in_cooler_width"] = (R["mount"]["fan_x_slot1"][0] >= -93.0 and R["mount"]["fan_x_slot1"][1] <= -52.0)


def th1(R):
    th = text_of(PINS["th1"])
    rows = []
    for m in re.finditer(r"^\| (M[^|]+?) \| ([^|]+?) \| ([\d.]+) W \| ([\d.]+) W \(([\d.]+) W\) \| ([^|]+?) \|$", th, re.M):
        pt, mode, q, qh, qf, setting = m.groups()
        n_h = 2 if setting.startswith("two") else 1
        v = math.sqrt(float(qh) / n_h * R_HEATER_OHM)
        vp = float(need(setting, r"([\d.]+) V", "a heater setting").group(1))
        rows.append(dict(point=pt.strip(), mode=mode.strip(), q=float(q), q_heaters=float(qh), q_fans=float(qf), n_heaters=n_h, v_printed=vp, v_computed=v, agree=abs(v - vp) < 0.006))
    if len(rows) != 7:
        refuse("T-H1's heater table has %d rows" % len(rows))
    places = []
    for m in re.finditer(r"^\| (board [^|]+?|the front end[^|]+?|the pack[^|]+?) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", th, re.M):
        places.append([x.strip() for x in m.groups()])
    if len(places) != 7:
        refuse("T-H1's places table has %d rows" % len(places))
    sec6 = th[th.index("## 6."):th.index("## 7.")]
    lines = []
    for ln in sec6.splitlines():
        if ln.startswith("| M") or ln.startswith("| fans off") or ln.startswith("| channel 5"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) != 4:
                refuse("a pass-line row has %d cells" % len(cells))
            lines.append(cells)
    if len(lines) != 10:
        refuse("T-H1's pass-line table has %d rows" % len(lines))
    chans = re.findall(r"^\| (\d+(?: to \d+)?|\d+, \d+) \| ([^|]+?) \|$", th[th.index("## 3."):th.index("## 4.")], re.M)
    if len(chans) != 10:
        refuse("T-H1's channel table has %d rows" % len(chans))
    R["th1"] = dict(rows=rows, places=places, lines=lines, chans=chans)


def bill(R):
    pr = json.load(open(os.path.join(TOP, PINS["prices"]), encoding="utf-8"))
    fc = json.load(open(os.path.join(TOP, PINS["findchips"]), encoding="utf-8"))
    P = {i["id"]: i for i in pr["items"]}

    def fc_row(part, dist, sku=None):
        for r in fc["parts"][part]:
            if r["distributor"] == dist and (sku is None or r["sku"] == sku):
                return r
        refuse("no FindChips row %s %s" % (part, dist))

    def tier1(row):
        for q, cur, v in row["price_breaks"]:
            if q == 1:
                return cur, v
        return None, None

    per_m2 = P["metaalshopper-alu-3mm"]["price"]["EUR_per_m2_excl_vat"]; per_pc = P["metaalshopper-alu-3mm"]["price"]["EUR_per_piece_cut"]; handling = P["metaalshopper-alu-3mm"]["price"]["EUR_handling_per_order"]
    # the plate blank at CASE-MARGINS C1's outline and the dummy board blanks at the boards' outlines (3 mm, the same sheet)
    mg = text_of(PINS["margins"])
    need(mg, r"C1: the face plate 0\.2 narrower, 377\.2 \(M8x\)", "the plate's width")
    need(mg, r"chosen 377\.2 x 263\.0 against the rim zone", "the plate's outline")
    blanks = [("the face plate blank 377.2 x 263.0 (CASE-MARGINS C1's outline; its ten 4.6 mm holes and R16 corners are not in the shop's price)", 0.3772 * 0.263),
              ("board B's blank 330 x 200 (B16's outline, panel1450 B_OUTLINE)", 0.330 * 0.200), ("board A's blank 240 x 160 (A_OUTLINE)", 0.240 * 0.160),
              ("board E's blank 267 x 68 (E_OUTLINE)", 0.267 * 0.068), ("board D's blank 100 x 80 (gen_pcb_d.py BOARD_L x BOARD_W)", 0.100 * 0.080),
              ("board C's U, 344 x 228 outer less the 240 x 176 window (panel1450's strips)", 0.344 * 0.228 - 0.240 * 0.176)]
    blank_rows = [(name, a, per_m2 * a + per_pc) for name, a in blanks]
    hs = fc_row("HS50 6R8 J", "RS", "160922"); hs_cur, hs_1 = tier1(hs)
    hs_f = fc_row("HS50 6R8 J", "Farnell", "4044345"); hsf_cur, hsf_1 = tier1(hs_f)
    cool = fc_row("9WPA0412P6G001", "RS"); cool_cur, cool_1 = tier1(cool)
    mix = fc_row("9WL0612P4H001", "Sager"); mix_cur, mix_1 = tier1(mix)
    alt = fc_row("GF60151B7-1E00U-AE9", "RS"); alt_cur, alt_1 = tier1(alt)
    korad = P["korad-ka3005p"]["price"]; korad_ex = round(korad["EUR_incl_19pct_vat"] / 1.19, 2)
    items = [
        # (group, item, qty, unit, currency, source, availability or lead, status)
        ("case", "Peli 1450 Protector case, current moulding (T1's identity check on receipt)", 1, P["peli-1450"]["price"]["EUR_excl_vat"], "EUR", "flight-cases.eu (Guardique), read 3 Oct 2026, excl. VAT (211.13 incl.)", P["peli-1450"]["availability"], "READ"),
        ("case", "Peli 1450PF Special Application Panel Frame Kit (frame, o-ring, 10 inserts, 4 screws)", 1, P["peli-1450pf"]["price"]["EUR_excl_vat"], "EUR", "flight-cases.eu, read 3 Oct 2026, a special price excl. VAT (regular 32.96)", "stock not shown", "READ"),
    ]
    for name, a, cost in blank_rows:
        items.append(("plate and blanks", "3 mm aluminium EN AW-5754, cut to size: " + name, 1, round(cost, 2), "EUR", "metaalshopper.nl, 278.07 EUR/m2 excl. VAT plus 0.44 per piece, read 3 Oct 2026; the piece price is this record's arithmetic over %.4f m2" % a, "shipped within 6 working days", "MODELED"))
    items.append(("plate and blanks", "the metal shop's handling charge, once per order", 1, handling, "EUR", "metaalshopper.nl, read 3 Oct 2026", "", "READ"))
    items.append(("heat", "Arcol HS50 6R8 J aluminium-housed wirewound resistor, 6.8 ohm 50 W (the draft's heaters; three give 21.2 W each at 12.0 V)", 3, hs_1, hs_cur,
                  "RS (stock number 160922, stock %s) through the FindChips reading of 3 Oct 2026; Farnell 4044345 at %s %.2f (stock %s)" % (hs["stock"], hsf_cur, hsf_1, hs_f["stock"]), "in stock at RS per the reading", "READ"))
    items.append(("heat", "dummy pack block: an aluminium block at the pack's outline (FEA-008's dummy pack; channel 16)", 1, None, "EUR", "no cut-to-size block seller read; a metal shop's quote", "", "NOT READ"))
    items.append(("fans", "Sanyo Denki 9WL0612P4H001 San Ace 60W IP68 (the picked mixer fan), with its two leads to J_FAN1/J_FAN2", 2, mix_1, mix_cur,
                  "Sager (a US distributor, stock %s) through the FindChips reading of 3 Oct 2026; no EU distributor row was served: an EU price is NOT READ" % mix["stock"], "stock 0 at the one distributor read", "READ (USD)"))
    items.append(("fans", "Sanyo Denki 9WPA0412P6G001 San Ace 40W IP68 (the picked cooler fan)", 3, cool_1, cool_cur, "RS (stock number 101593, stock %s) through the FindChips reading of 3 Oct 2026; Farnell 4218284 at 76.83 (stock 0)" % cool["stock"], "in stock at RS per the reading", "READ"))
    items.append(("fans", "Raspberry Pi Cooler for Compute Module 5 (the passive heatsink the cooler fans sit on; the fans' mount in the mock-up)", 3, P["rpi-cm5-cooler"]["price"]["EUR_excl_vat"], "EUR", "kiwi-electronics.com KW-3425, read 3 Oct 2026, excl. VAT (5.43 incl.)", P["rpi-cm5-cooler"]["availability"], "READ"))
    items.append(("fans", "fan brackets (the cooler fans over the heatsinks, the mixers at the stack's ends): printed or bent parts, the Layer 7 CAD finding", 5, None, "EUR", "a part to draw first", "", "NOT READ"))
    items.append(("instruments", "Pico Technology PicoLog TC-08 thermocouple data logger (8 channels plus CJC); two for the sixteen channels", 2, P["pico-tc-08"]["price"]["GBP"], "GBP", "picotech.com, read 3 Oct 2026, VAT treatment not stated", P["pico-tc-08"]["availability"], "READ"))
    items.append(("instruments", "Pico SE000 type K thermocouple, exposed tip, PTFE, 1 m (sixteen channels and two spares)", 18, P["pico-se000"]["price"]["GBP"], "GBP", "picotech.com, read 3 Oct 2026, VAT treatment not stated", "listed with the TC-08", "READ"))
    items.append(("supplies", "KORAD KA3005P 0 to 30 V, 0 to 5 A programmable supply with USB/RS232 logging (one for the heaters, one for the fans: P is both supplies' V x I)", 2, korad_ex, "EUR",
                  "reichelt.com, 89.00 incl. 19 %% VAT read 3 Oct 2026 (list 109.00); %.2f excl. VAT is this record's arithmetic" % korad_ex, P["korad-ka3005p"]["availability"], "READ"))
    items.append(("consumables", "thermal compound, M2.5 and M3 hardware, standoffs, JST SH 1.0 and 24 AWG leads, insulating tape for the junctions", 1, None, "EUR", "consumables; no page read", "", "NOT READ"))
    items.append(("room", "the ambient: still room air, shaded, 0.5 m clear around the case (the draft's configuration); an optional confirming chamber point at +40 C or +60 C", 1, None, "EUR", "a laboratory's service if the owner wants the chamber point", "", "NOT READ"))
    totals = {}
    for g, it, q, u, cur, src, lead, st in items:
        if u is not None:
            totals[cur] = totals.get(cur, 0.0) + q * u
    R["bill"] = dict(items=items, totals=totals, n_not_read=sum(1 for i in items if i[3] is None), alt_mixer=(alt_cur, alt_1, alt["stock"]), cooler_stock=cool["stock"], heater_stock=hs["stock"])


def dock(R):
    d_mm = AWG24_D_MM
    a_mm2 = math.pi / 4 * d_mm ** 2
    cmil = (d_mm / 0.0254) ** 2
    sqmil = a_mm2 / (0.0254 ** 2)

    def onderdonk(t_s, ta_c, plus=True):
        den = (234.0 + ta_c) if plus else (234.0 - ta_c)
        return cmil * math.sqrt(math.log10((CU_MELT_C - ta_c) / den + 1.0) / (t_s * 33.0))

    # the note's worked example: 2581 cmil, 5 s, 25 C, with its own (234 - Ta) spelling, 178 A
    ex = 2581.0 * math.sqrt(math.log10((1083.0 - 25.0) / (234.0 - 25.0) + 1.0) / (5.0 * 33.0))
    fus = {ta: onderdonk(SHORT_S, ta) for ta in (25.0, 70.0, 85.0)}
    fus_minus = onderdonk(SHORT_S, 70.0, plus=False)
    i2t_cap_70 = fus[70.0] ** 2 * SHORT_S
    # adiabatic rise from the pulse's I2t over the ECSS resistance per metre and copper's heat capacity per metre
    mass_per_m = a_mm2 * 1e-6 * CU_DENS
    rise = SHORT_I2T * CU_RHO_PER_M / (mass_per_m * CU_C_J_KGK)
    preece = PREECE_CU * (d_mm / 25.4) ** 1.5
    ecss_isw = 3.4
    ecss = text_of(PINS["ecss"])
    need(ecss, r"the AWG 24 column: \*\*ISW 3\.4 A\*\*", "the ECSS AWG 24 rating")
    need(ecss, r"resistance at 20 C \*\*105 mOhm/m\*\*", "the ECSS AWG 24 resistance")
    fz = text_of(PINS["fusing"])
    need(fz, r"\(234 \+ Tambient\)", "the note's Onderdonk form")
    retry_rms = RETRY_A * math.sqrt(RETRY_DUTY)
    R["dock"] = dict(d_mm=d_mm, a_mm2=a_mm2, cmil=cmil, sqmil=sqmil, fus=fus, fus_minus=fus_minus, example=ex, i2t_cap_70=i2t_cap_70, pulse_pct_70=100.0 * SHORT_A / fus[70.0], i2t_ratio=i2t_cap_70 / SHORT_I2T,
                     rise_k=rise, preece=preece, ecss_isw=ecss_isw, retry_pct=100.0 * RETRY_A / ecss_isw, retry_rms=retry_rms, retry_rms_pct=100.0 * retry_rms / ecss_isw,
                     cont_pct=100.0 * 1.0 / ecss_isw, cont_full_pct=100.0 * R["down"]["vsys_e_total_full"] / ecss_isw, fifty_k_rule="the maker's maximum rating of the fitted wire is not named in ASSEMBLY.md (24 AWG only)")


def compute():
    R = {"pins": {k: sha_of(v) for k, v in PINS.items()}}
    read_sites(R)
    read_candidates(R)
    judge(R)
    mounting(R)
    th1(R)
    bill(R)
    dock(R)
    J, D, M, K = R["judge"], R["down"], R["mount"], R["dock"]
    sel_m, sel_c = R["cands"][R["sel"]["mixer"]], R["cands"][R["sel"]["cooler"]]
    R["pred"] = {
        "no candidate's printed range covers VSYS_E 9.494 to 17.375 V": R["no_direct_fan"],
        "no 5 V IP68 40 mm fan was read in the makers' lines": all(c["v"] in (12.0, 24.0) for c in R["cands"].values()),
        "the picked mixer covers -20 C and prints a life at 60 C": J["9WL0612P4H001"]["temp_ok"] is True and J["9WL0612P4H001"]["life_at_60"],
        "the picked cooler fan covers -20 C and prints a life at 60 C": J["9WPA0412P6G001"]["temp_ok"] is True and J["9WPA0412P6G001"]["life_at_60"],
        "the alternatives fail REQ-043's -20 C or print no range": J["GF60151B7-1E00U-AE9"]["temp_ok"] is False and J["GF40282B3-1000U-SEP"]["temp_ok"] is None,
        "no candidate prints a starting current": not any(v["start_read"] for v in J.values()),
        "each picked mixer at full speed behind a 12 V buck draws under L4-E11's both-start limit at the floor": D["each_under_both_limit"],
        "both mixers at full speed plus U12 exceed the declared 1.0 A but stay under U42's least limit": D["vsys_e_total_full"] > 1.0 and D["vsys_e_total_full"] < I_OL_MIN,
        "the picked fans at full speed add heat over the plan's fan figures": D["heat_hold_full"] > D["heat_hold_plan"] and D["heat_prof_full"] > D["heat_prof_plan"],
        "the 40 x 40 x 20 fan on the cooler clears the backer's underside by under 3 mm (a fit finding)": 0.0 < M["clear_backer_cooler"] < 3.0,
        "every T-H1 heater setting is sqrt(P x 6.8) to 0.01 V": all(r["agree"] for r in R["th1"]["rows"]),
        "the bill's EUR total is over 600 and under 700": 600.0 < R["bill"]["totals"]["EUR"] < 700.0,
        "the bill has items with no read price": R["bill"]["n_not_read"] >= 4,
        "the Onderdonk form reproduces the note's worked example (178 A) within 1 A": abs(K["example"] - 178.0) < 1.0,
        "the hard short is under 3 percent of the 24 AWG fusing current at 4.5 us and 70 C": K["pulse_pct_70"] < 3.0,
        "the pulse's adiabatic rise in the 24 AWG is under 1 K": K["rise_k"] < 1.0,
        "the retry setting is under the ECSS single-wire rating": RETRY_A < K["ecss_isw"],
    }
    return R


def render(R):
    out = []
    P = out.append
    J, D, M, K, B = R["judge"], R["down"], R["mount"], R["dock"], R["bill"]
    P("L7PWR (MESHSAT-1357): THE FANS (D-18, E11-35), THE T-H1 MOCK-UP BILL AND THE DOCK LEAD'S PULSE CAPABILITY (E11-38). Prototype design,")
    P("desk arithmetic: nothing bought, built, powered or measured. MAKER a printed figure, MODELED this script's arithmetic, ASSUMPTION a stated")
    P("assumption, INFERRED a reading carried from a sibling document, NOT READ a figure no document prints.")
    P("")
    P("0. INPUTS (sha256/16)")
    for k, v in PINS.items():
        P("   %-11s %s  sha256 %s" % (k, v, R["pins"][k][:16]))
    P("")
    P("1. THE SITES AND THEIR SUPPLIES (read from the generators and L4-E11)")
    P("   mixers:  " + R["sites"]["mixers"])
    P("   coolers: " + R["sites"]["coolers"])
    P("   VSYS_E under L4-E11's draft: %.3f V at U42's least limit at the supplement floor to %.3f V with the charge held; the start limits %.4f A each (both)" % (VSYS_E_FLOOR, VSYS_E_TOP, START_BOTH))
    P("   and %.4f A one at a time (the other at 0.1 A), under U42's least limit %.3f A with U12's %.1f A (L4-E11 17a); E11-39 staggers the starts with a PWM ramp" % (START_ONE, I_OL_MIN, U12_A))
    P("   the slot rails: %.1f V (ASSEMBLY.md), the cooler fan 0.1 A declared on each" % SLOT_5V)
    P("   REQ-043's acceptance (pcb_requirements.yaml): " + R["req043"])
    P("   the inside air the fans must cover: REQ-043's %.0f C floor; the board air at the margin %.1f C (L4-E12); the hold's trigger %.2f C of mixed air" % (T_IN_MIN, T_BOARD_MAX, T_HOLD))
    P("")
    P("2. THE CANDIDATES, ROW BY ROW (MAKER unless marked)")
    P("   %-24s %-12s %-30s %6s %-12s %7s %7s %6s %6s %6s %6s %-12s %-20s %-8s %s" % ("model", "maker", "size", "V", "range (V)", "A", "W", "rpm", "CFM", "Pa", "dBA", "temp (C)", "life (h)", "IP", "lines"))
    for k in ("9WL0612P4H001", "9WL0612P4J001", "GF60151B7-1E00U-AE9", "CFM-6025BG68-135-253-22", "9WL0624P4H001", "9WPA0412P6G001", "GF40282B3-1000U-SEP", "9WPA0424P6G001"):
        c = R["cands"][k]
        rng = "NOT READ" if c["vlo"] is None else "%.1f to %.1f%s" % (c["vlo"], c["vhi"], " (INF)" if c.get("range_inferred") else "")
        tmp = "NOT READ" if c["tlo"] is None else "%.0f to +%.0f%s" % (c["tlo"], c["thi"], " (INF)" if c.get("range_inferred") else "")
        life = "NOT READ" if (c["life60"] is None and c["life40"] is None) else ("%d at 60 C" % c["life60"] if c["life60"] else "%d at 40 C%s" % (c["life40"], " (INF)" if c.get("range_inferred") else ""))
        P("   %-24s %-12s %-30s %6.0f %-12s %7s %7s %6.0f %6.1f %6.0f %6.1f %-12s %-20s %-8s %s" % (k, c["maker"], c["size"], c["v"], rng, "NOT READ" if c["a"] is None else "%.2f" % c["a"], "NOT READ" if c["w"] is None else "%.2f" % c["w"],
                                                                                              c["rpm"], c["cfm"], c["pa"], c["dba"], tmp, life, c["ip"], c["io_note"]))
    P("   documents: Sanyo Denki rows from the maker's product-database pages (transcribed, each page's sha256 in the file); Sunon rows from the maker's brochure 239-E and the")
    P("   catalogue 240-A extract (the GF60151 family's range, temperature and life from the GF60151B6 specification for approval as a distributor hosts it, INFERRED for B7);")
    P("   Same Sky rows from the maker's series sheet CFM-60BG68 (09/12/2024, filed; its A and W columns are the row's maxima, typical 0.06 A and 0.72 W). Starting current: not printed by")
    P("   any maker (NOT READ); Same Sky prints a soft start on all models. Pa is MODELED (inch-H2O x 249.089) where a maker prints inch-H2O only. Every maximum operating temperature read")
    P("   is +70 C: 1.35 K over the hold's %.2f C trigger on the mixed air, so the fans run at their printed limit when the hold acts (L4-E12 keeps the fans running in E5)." % T_HOLD)
    P("")
    P("   THE JUDGEMENT (the site's supply as drawn, REQ-043's -20 C and IP68, the inside air, the lines the generator draws)")
    P("   %-24s %-8s %-22s %-10s %-10s %-10s %-6s %-6s %-6s %-9s %s" % ("model", "site", "supply as drawn (V)", "range", "-20..62.1", "hold 68.65", "IP68", "tach", "PWM", "life@60", "I at the floor behind a 12 V converter, full speed (A, MODELED)"))
    for k, j in J.items():
        def yn(v):
            return "NOT READ" if v is None else ("yes" if v else "NO")
        P("   %-24s %-8s %-22s %-10s %-10s %-10s %-6s %-6s %-6s %-9s %s" % (k, j["site"], "%.3f to %.3f" % j["supply"], yn(j["range_ok"]), yn(j["temp_ok"]), yn(j["hold_ok"]), yn(j["ip68"]), yn(j["tach"]), yn(j["pwm"]), yn(j["life_at_60"]),
                                                                            "NOT READ" if j["i_at_floor"] is None else "%.3f" % j["i_at_floor"]))
    P("   No candidate's printed operating range covers VSYS_E's %.3f to %.3f V: every 12 V class stops at 13.2 or 13.8 V and every 24 V class starts at 21.6 V: %s" % (VSYS_E_FLOOR, VSYS_E_TOP, "yes" if R["no_direct_fan"] else "no"))
    P("   No 5 V IP68 40 mm fan exists in the lines read (Sunon's IP68 GF series is 12 and 24 V; Sanyo Denki's 40 mm splash-proof models are 12 and 24 V; Delta's 40 mm IP68 part numbers are")
    P("   served by script and did not reach this host): the cooler fans cannot run from the slot's %.1f V as drawn. Both sites therefore need a 12.0 V fan feed (section 3)." % SLOT_5V)
    P("")
    P("   SELECTED (authority: SESSION, D-18 settled under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026)")
    sm = R["cands"][R["sel"]["mixer"]]; sc = R["cands"][R["sel"]["cooler"]]; am = R["cands"][R["alt"]["mixer"]]; ac = R["cands"][R["alt"]["cooler"]]
    P("   mixers (2, board E):  %s %s, %s, %.0f V (%.1f to %.1f V), %.2f A, %.2f W, %.0f rpm, %.1f CFM (%.2f m3/min), %.0f Pa, %.0f dB(A), %.0f to +%.0f C, %d h at 60 C (%d at 40 C), %s, %s, %.0f g"
      % (sm["maker"], R["sel"]["mixer"], sm["size"], sm["v"], sm["vlo"], sm["vhi"], sm["a"], sm["w"], sm["rpm"], sm["cfm"], sm["m3min"], sm["pa"], sm["dba"], sm["tlo"], sm["thi"], sm["life60"], sm["life40"], sm["ip"], sm["io_note"], sm["g"]))
    P("      why: the only 60 mm IP68 candidate that prints -20 C (REQ-043's floor) AND a life at 60 C AND a tachometer (FW-E07/V-E07's stalled-fan report) AND a PWM input; the lowest-power")
    mix_item = [i for i in B["items"] if i[1].startswith("Sanyo Denki 9WL0612P4H001")][0]; cool_item = [i for i in B["items"] if i[1].startswith("Sanyo Denki 9WPA0412P6G001")][0]
    P("      model of its family (H), 2.04 W against the plan's 0.72 W per mixer at full speed, the controls' duty deciding the running power. Price indicator: %s %.2f at 1 (Sager, a US" % (mix_item[4], mix_item[3]))
    P("      distributor; stock 0); an EU price NOT READ. Alternative: %s %s, 12 V, 4.5 to 13.8 V, %.2f W, %.1f CFM, IP68, 2-ball, %.0f g, %s; it prints -10 C (fails REQ-043's -20 C) and has no" % (am["maker"], R["alt"]["mixer"], am["w"], am["cfm"], am["g"], am["io_note"]))
    P("      tachometer; EUR %.2f at 1 (RS, stock %s). Same Sky's CFM-6025BG68-135-253-22 (0.72 W typical, 0.86 W maximum, tach and PWM) also prints -10 C." % (B["alt_mixer"][1], B["alt_mixer"][2]))
    P("   coolers (3, board B): %s %s, %s, %.0f V (%.1f to %.1f V), %.2f A, %.1f W, %.0f rpm, %.1f CFM (%.2f m3/min), %.0f Pa, %.0f dB(A), %.0f to +%.0f C, %d h at 60 C (%d at 40 C), %s, %s, %.0f g"
      % (sc["maker"], R["sel"]["cooler"], sc["size"], sc["v"], sc["vlo"], sc["vhi"], sc["a"], sc["w"], sc["rpm"], sc["cfm"], sc["m3min"], sc["pa"], sc["dba"], sc["tlo"], sc["thi"], sc["life60"], sc["life40"], sc["ip"], sc["io_note"], sc["g"]))
    P("      why: the only 40 mm IP68 fan with a maker's page reached from this host (12 V class; the maker lists no lower speed under this frame, and the 9WP0412H6001 distributors")
    P("      name answers 404 on the maker's database); it prints -20 C, 40,000 h at 60 C, a pulse sensor and a PWM input for the module's Fan_Tacho and Fan_PWM pins. Its 2.0 W at full")
    P("      speed is 3.5 times the plan's 0.57 W per cooler fan: the module's PWM duty decides the running power. Price indicator: %s %.2f at 1 (RS, stock %s). Alternative: %s %s," % (cool_item[4], cool_item[3], B["cooler_stock"], ac["maker"], R["alt"]["cooler"]))
    P("      24 V IP68 40 x 40 x 28, %.1f CFM, %.0f dB(A): its range, temperature and life NOT READ (brochure row only), 28 mm thick against the 20 of the pick (section 4), a 24 V feed." % (ac["cfm"], ac["dba"]))
    P("   Reverse either pick by a fan whose maker prints a range covering the site's supply as drawn, -20 C and a life at or over 60 C; or by the owner changing REQ-043's IP68 statement openly.")
    P("")
    P("3. WHAT THE PICKS CHANGE DOWNSTREAM (MODELED on the makers' full-speed figures; a converter efficiency of %.2f is an ASSUMPTION)" % BUCK_EFF)
    P("   the mixers' feed: a regulated 12.0 V rail on board E from VSYS_E (the fans' printed range is 10.8 to 13.2 V; VSYS_E runs 12.054 to %.3f V in service, over the range most of the time," % VSYS_E_TOP)
    P("   and to %.3f V at the floor); J_FAN1/J_FAN2 become 4-wire (12 V, GND, PWM, TACH): the low-side chopping of Q9/Q10 and the SS14 flybacks D7/D8 are retired, the FETs re-used as" % VSYS_E_FLOOR)
    P("   open-drain PWM drivers (the fan's PWM input level NOT READ: the maker's manual is behind a form), the tach stays on the 10k pull-up to +3V3_E6 (FINDING for board E's generator owner;")
    P("   rows R-177/E11-33 and the register's R-179). With the fans on a switched low side the tachometer's open-collector return would ride the switched node: a 4-wire fan removes it.")
    P("   the mixers' current on VSYS_E at the floor %.3f V behind the 12 V buck: %.3f A each at full speed (the fan's %.2f W), %.3f A both; the plan's %.2f W for both is %.3f A." % (VSYS_E_FLOOR, D["i_mixer_each_full"], D["mixer_w_each"], D["i_mixer_both_full"], PLAN_MIXER_W, D["i_mixers_plan"]))
    P("   against L4-E11 17a: %.3f A each is %s the %.4f A both-start limit and %s the %.4f A one-at-a-time limit (if the start current were the rated current: it is NOT READ, so E11-35's bench row stands);" % (D["i_mixer_each_full"], "under" if D["each_under_both_limit"] else "OVER", START_BOTH, "under" if D["each_under_one_limit"] else "OVER", START_ONE))
    P("   VSYS_E's total with U12's %.1f A: %.3f A at full speed, %.1f %% of U42's least limit %.3f A and %.3f A OVER the 1.0 A L4-E11 declared (FINDING for R-177 and R-181: declare the fans at their" % (U12_A, D["vsys_e_total_full"], D["pct_of_least"], I_OL_MIN, D["over_declared"]))
    P("   full-speed draw or bound the duty in firmware); at the plan's duty the total is %.3f A, under 1.0 A." % D["vsys_e_total_plan"])
    P("   the dock feed's current (E11-35): unchanged in kind (one 813 contact), its declared value moves from 1.0 A to at most %.3f A at full speed; the contact at %.1f %% of its 3.5 A." % (D["vsys_e_total_full"], 100.0 * D["vsys_e_total_full"] / 3.5))
    P("   the coolers' feed: 12.0 V on board B for J_FAN1..3 (no 12 V rail exists there; the slot rails are %.1f V): a per-slot step-up from +5V_Sn at %.3f A each at full speed (keeps 'an empty slot" % (SLOT_5V, D["cooler_i_slot_full"]))
    P("   stays off'), or a 12 V feed from board A over the bay harness (board A's VHEAT and +12V_HF are switched for other loads); the header's 5V pin becomes the 12 V pin (FINDING for board B's")
    P("   generator owner, the J_FAN rows and the slot rail budgets of gen_sch_b.py's comments; Layer 5's bay harness rows). The module's Fan_PWM (open drain) and Fan_Tacho (1.8k to 3.3 V) stay.")
    P("   the firmware stagger (E11-39, R-188): kept; the PWM ramp now drives the fan's PWM input, not a chopped supply; a 4-wire fan's own soft start is NOT READ for Sanyo (Same Sky prints one).")
    P("   the heat into the case at full speed: the hold's fans (slot 3's cooler and the two mixers) %.2f W against the model's %.3f W (+%.2f W, E5's line +%.3f W/K at 0.100 W/K per W); the profile's" % (D["heat_hold_full"], D["heat_hold_plan"], D["heat_hold_full"] - D["heat_hold_plan"], D["line_shift_hold"]))
    P("   five fans %.2f W against %.3f W. The controls set the duty (R-150: the picked fans' power at the duty the controls set replaces pwr_budget.py's rows); T-H1 logs the fans' real draw." % (D["heat_prof_full"], D["heat_prof_plan"]))
    P("   the airflow the picks would deliver (free air, MAKER): the two mixers %.4f m3/s (%.2f m3/min against the representatives' %.2f to %.2f m3/min, GF60151B9 to B6), the three cooler fans %.4f m3/s;" % (D["flow_mixers_m3s"], 2 * sm["m3min"], 2 * R["rep"]["mixers_cfm"][0] * 0.3048 ** 3, 2 * R["rep"]["mixers_cfm"][1] * 0.3048 ** 3, D["flow_coolers_m3s"]))
    P("   over the case's free air of about %.4f m3 (MODELED, the boards not subtracted) the mixers' free-air flow is %.1f case volumes a second, an upper bound: the delivered flow in the sealed" % (CASE_FREE_M3, D["changes_per_s"]))
    P("   case sits on the fan curve below its %.0f Pa maximum and no system curve is held. L4-E12's bound credits this flow at zero; T-H1's reading with these fans replaces the credit." % sm["pa"])
    P("   the cooler fan's flow over the module: %.2f m3/min free air against the representative MF30060V2's %.1f CFM (%.2f m3/min); L4-E12 takes half the free-air flow through the heatsink (ASSUMPTION there)." % (sc["m3min"], R["rep"]["cooler_cfm"], R["rep"]["cooler_cfm"] * 0.3048 ** 3))
    P("")
    P("4. MOUNTING (the case records; FINDING for v2/cad's owner)")
    P("   the CM5 cooler: Raspberry Pi's Cooler for Compute Module 5 is a PASSIVE heatsink, 56 x 41 x 12.7 mm, four M2.5 x 8 screws from below the carrier (the product brief RP-008184-DS-1,")
    P("   December 2024; list price USD 5): the 'cooler fan' is a fan added over it, not part of it. ASSEMBLY.md's 'coolers clipped on with their fan leads' and panel1450.py's 30 x 30 x %.0f envelope" % M["env_fan_h"])
    P("   describe a fan the maker does not supply.")
    P("   the pick, 40 x 40 x 20, flat over the fins at the cooler's north end: X %.1f to %.1f on slot 1 (the cooler's %.0f to %.0f: inside its 41 mm width: %s), Y %.0f to %.0f (north of the monitor's" % (M["fan_x_slot1"][0], M["fan_x_slot1"][1], M["cooler_x_slot1"][0], M["cooler_x_slot1"][1], "yes" if M["fan_in_cooler_width"] else "NO", M["fan_y"][0], M["fan_y"][1]))
    P("   edge at Y +%.3f by %.3f mm as panel1450 places the fan envelope, and up to the backer's top strip at Y %.0f)." % (M["mon_edge"], M["fan_y"][0] - M["mon_edge"], M["strip_t_y"]))
    P("   Z: board B's top %.2f; module and receptacle %.2f; the cooler %.1f; the fan %.0f: top at %.2f (on the cooler's own height) or %.2f (on panel1450's %.1f mm heatsink envelope); the backer's" % (M["b_top"], M["module_stack"], M["cooler_h"], M["fan_t"], M["top_on_cooler"], M["top_on_env"], M["env_hs"]))
    P("   underside %.2f (face %.2f, plate 3.0, standoffs %.1f, backer 1.6): clearance %.2f mm (cooler height) or %.2f mm (envelope) where the backer's strip reaches; the plate's underside %.2f" % (M["backer_under"], M["face"], 10.0, M["clear_backer_cooler"], M["clear_backer_env"], M["plate_under"]))
    P("   (%.2f mm) over the open window. The fan's hole pattern (NOT READ: the maker's CAD is behind a form; the 40 mm class standard is 32.0 mm on 4.3 mm holes) and a bracket to the cooler's" % M["clear_plate_cooler"])
    P("   M2.5 screws or the module's standoffs are to draw; the mixers' sites 'at the stack's ends' (ASSEMBLY.md) are not drawn (CASE-MARGINS section 7's owed positions): both Layer 7 CAD items.")
    P("")
    P("5. THE T-H1 MOCK-UP BILL (prices read 3 October 2026 from the pages inputs/prices-2026-10-03.json and inputs/findchips-fans-heaters-2026-10-03.json name; indicators, never quotes; nothing bought)")
    P("   %-14s %3s %-130s %10s %-4s %-9s %s" % ("group", "qty", "item", "unit", "cur", "status", "source and lead"))
    for g, it, q, u, cur, src, lead, st in B["items"]:
        P("   %-14s %3d %-130s %10s %-4s %-9s %s%s" % (g, q, it[:130], "NOT READ" if u is None else "%.2f" % u, cur, st, src, ("; " + lead) if lead else ""))
    for cur in sorted(B["totals"]):
        P("   TOTAL of the prices read, %s: %.2f" % (cur, B["totals"][cur]))
    P("   The three currencies are not converted (no rate was read). EUR figures are excl. VAT where the page states it; the GBP figures' VAT treatment is not stated by the maker's page.")
    P("   Items with no read price: %d (the dummy pack block, the fan brackets, the consumables, the optional chamber point); plus an EU price for the 60 mm Sanyo Denki fan." % B["n_not_read"])
    P("   Lead times printed: the case 'Normal in stock'; the plate and blanks 'shipped within 6 working days'; the loggers 'Currently In Stock'; the supplies 'Available on 10/9/2026' as printed;")
    P("   the cooler heatsinks 75 in stock; the cooler fans RS stock 51 and the heaters RS stock 921 by the aggregator's reading; the 60 mm fan stock 0 at the one distributor read.")
    P("")
    P("6. THE SPECIMEN, AND THE PASS LINES RESTATED (from T-H1-PROCEDURE-DRAFT.md as revised for L4-E12's section 17)")
    P("   The specimen: an empty current-moulding Peli 1450 with the 1450PF frame and the 3 mm aluminium plate blank in the face's place, on its feet in still room air, shaded; no boards:")
    P("   resistive heaters on 3 mm aluminium blanks at the boards' outlines on the kit's standoffs, set per point to the mode's heat less the fans' MEASURED draw; the five picked fans in their")
    P("   places (three over the cooler heatsinks on board B's blank, two mixers at the stack's ends) on their own logged supply; sixteen type K channels on two TC-08 loggers.")
    P("   What it represents: the sealed case's conductance between the mixed inside air and the ambient, per heat, lid state and fan state, with the frame, plate and fans as built.")
    P("   What transfers to the final kit: that conductance, fully (the case, frame, plate and fans are the kit's own parts); the plate, wall and floor fractions; the hold reference's offset.")
    P("   What does not transfer: the boards' local temperatures, the cells' rise in the pocket, the junctions, the parts' local air (T-H2, THM-001, U-01 keep their own evidence); lid-closed and")
    P("   fans-off states each need their own point; the room-to-+40 C translation is a model (L4-E12 16.4), not a validation.")
    P("   The heaters per point (the draft's table; this record recomputes each setting as sqrt(P_heater x %.1f ohm)):" % R_HEATER_OHM)
    for r in R["th1"]["rows"]:
        P("   %-18s %-78s heat %7.3f W = heaters %7.3f W (model's fans %.3f W): %d heater(s) at %.2f V (recomputed %.2f V, %s)" % (r["point"], r["mode"][:78], r["q"], r["q_heaters"], r["q_fans"], r["n_heaters"], r["v_printed"], r["v_computed"], "agrees" if r["agree"] else "DIFFERS"))
    P("   The heaters' places (W, plan; the fans real): %s" % "; ".join("%s: %s" % (pl[0].split(" (")[0], "/".join(pl[1:])) for pl in R["th1"]["places"]))
    P("   The sixteen channels: %s" % "; ".join("%s %s" % (c[0], c[1]) for c in R["th1"]["chans"]))
    P("   Pass per point: the reading less its expanded uncertainty (k = 2) at or over the line's need; fail under it; inconclusive when the endpoint is not met or a supply, a fan or the ambient drifts.")
    P("   %-44s %-72s %-56s %s" % ("point (lid open, fans on unless named)", "governing line as ruled: need, pass at a reading of at least", "under CFL-002's C, A or B", "decides"))
    for ln in R["th1"]["lines"]:
        P("   %-44s %-72s %-56s %s" % (ln[0][:44], ln[1][:72], ln[2][:56], ln[3]))
    P("   The owner's purchase decision and the test's decision on one page: v2/docs/records/l7pwr/T-H1-MOCKUP-SPEC.md carries sections 5 and 6 together.")
    P("")
    P("7. THE DOCK LEAD'S PULSE AND DUTY CAPABILITY (E11-38's wiring half; the 813 contact is the maker's question, clarification/preci-dip-813.txt)")
    P("   the lead: 60 mm of 24 AWG from board E's J_BLK to the dock block's land (ASSEMBLY.md section 4), copper d = %.4f mm (the AWG definition), A = %.4f mm2 = %.1f circular mils = %.1f square mils;" % (K["d_mm"], K["a_mm2"], K["cmil"], K["sqmil"]))
    P("   ECSS-Q-ST-30-11C Rev.2 Table C-1: %.0f mOhm/m at 20 C, minimum diameter 0.8 mm (the insulated wire)." % (CU_RHO_PER_M * 1000))
    P("   Onderdonk (the note's general form, I = A sqrt(log10(1 + (Tm - Ta)/(234 + Ta)) / (33 t)), A in circular mils, t in s, Tm %.0f C); the form reproduces the note's worked example at %.1f A" % (CU_MELT_C, K["example"]))
    P("   (178 A printed, with the note's own '234 - Ta' spelling; this record uses 234 + Ta, the smaller and conservative figure: %.0f against %.0f A at 70 C)." % (K["fus"][70.0], K["fus_minus"]))
    P("   the fusing current of the 24 AWG at the short's %.1f us: %.0f A from 25 C, %.0f A from 70 C, %.0f A from 85 C (the spring's limit); the short's %.0f A is %.2f %% of the 70 C figure," % (SHORT_S * 1e6, K["fus"][25.0], K["fus"][70.0], K["fus"][85.0], SHORT_A, K["pulse_pct_70"]))
    P("   its %.3f A2s is 1/%.0f of the wire's %.0f A2s to melt at that time; the adiabatic rise of the copper from the pulse: %.3f K (ECSS's resistance per metre over copper's %.0f J/kgK and %.0f kg/m3)." % (SHORT_I2T, K["i2t_ratio"], K["i2t_cap_70"], K["rise_k"], CU_C_J_KGK, CU_DENS))
    P("   the eFuse's retry duty (cases (3) and (4) of L4-E11 17a): at most %.3f A for at most 1.5 s then off at least 0.5 s, a duty of at most %.2f: %.3f A is %.0f %% of ECSS Annex C's %.1f A single-wire" % (RETRY_A, RETRY_DUTY, RETRY_A, K["retry_pct"], K["ecss_isw"]))
    P("   rating of AWG 24 (a 70 C environment, 150 C wire, radiation alone, in vacuum), the duty's rms %.3f A is %.0f %%; Preece's steady fusing current of the bare wire %.1f A." % (K["retry_rms"], K["retry_rms_pct"], K["preece"]))
    P("   the continuous draw: 1.0 A declared (%.0f %% of 3.4 A), %.3f A with the picked mixers at full speed (%.0f %%). The 50 K rule of 6.32.4a cannot be applied: %s." % (K["cont_pct"], D["vsys_e_total_full"], K["cont_full_pct"], K["fifty_k_rule"]))
    P("   So the wiring is not the limiting element of the branch on these published relations; the 813 contact's pulse capability (the piston-to-barrel interface, the gold plating, the spring)")
    P("   is printed nowhere (3.5 A operating, 10 mOhm static; the SMD series alone prints a 7 A peak) and stays E11-38's bench item and the drafted question.")
    P("")
    P("8. PREDICATES (the tests read these)")
    for k, v in R["pred"].items():
        P("   %-110s %s" % (k, "yes" if v else "NO"))
    return "\n".join(out) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    return 0


if __name__ == "__main__":
    sys.exit(main())
