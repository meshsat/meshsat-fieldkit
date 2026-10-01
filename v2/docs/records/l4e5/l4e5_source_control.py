#!/usr/bin/env python3
"""l4e5_source_control.py: layer 4 task L4-E5 (MESHSAT-1357, 1 October 2026). Implementable choice 1, SOURCE CONTROL, of
v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md (finding A-2, "the bus collapses with a fixed IIN_HOST", and its per-source
closure after the power review's L4-R04): how board A's charger U3 (BQ25731), which draws from VBUS20 behind the front end
U2 (LM5176), is kept from collapsing VIN_RAW, onto which board E ORs the panel tracker (LT8705A) and the vehicle and shore
entry (LM5069), while FW-A16 as written caps solar-only charging at about 54 W against the tracker's 93 W (O-33).

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry, rendered page or
HW-FW-CONTRACT.md in the tree is edited (apply_fw_a16.py beside this file is a draft for the coordinator). Every figure carries
its basis: MAKER (document, revision, page), NETLIST (the committed netlists), MODELED (the energy model, through
l4e_replay.py's own functions), INFERRED (method stated), ASSUMPTION (a figure no document gives); INCONCLUSIVE where no
held document gives a figure.

Section 0 proves, before any result (exit 4 otherwise):
  0a l4e4_limits.py, re-run in a child process, reproduces l4e4_limits.out byte for byte;
  0b r11_dep.py, re-run in a child process, reproduces r11_dep.out byte for byte;
  0c l4e4_limits.compute(), run here, renders l4e4_limits.out byte for byte, so the L4-E4 functions used in section 7
     (u3_max, board_max, serv_of, margins_for, tap_rule, band) are the ones that printed the record;
  0d l4e_replay.main(), run here with its locals captured by l4e4_limits.run_main_captured(), prints l4e_replay.out byte for
     byte, so the energy functions used in section 4 (run, meanday, the case table, the candidate panel's trace) are the
     ones that printed the record; its corrected rows are re-run and must give the printed figures.

Run from the repository root:  python3 v2/docs/records/l4e5/l4e5_source_control.py > v2/docs/records/l4e5/l4e5_source_control.out
Needs pdftotext and pdftoppm, PyYAML and Pillow (through the imported records). About three minutes, most of it 0d.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction or a predicate failed."""
import hashlib
import importlib.util
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
L4E4_PY = "v2/docs/records/l4e4/l4e4_limits.py"
L4E4_OUT = "v2/docs/records/l4e4/l4e4_limits.out"
R11_PY = "v2/docs/records/r11dep/r11_dep.py"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
REPLAY_PY = "v2/docs/records/l4e/l4e_replay.py"
REPLAY_OUT = "v2/docs/records/l4e/l4e_replay.out"
CONTRACT = "v2/docs/HW-FW-CONTRACT.md"
GEN_A = "v2/ecad/tools/gen_sch_a.py"
GEN_E = "v2/ecad/tools/gen_sch_e.py"
NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"
BQ = "v2/vendor/ti/bq25731-datasheet.pdf"
LT = "v2/vendor/power/lt8705a.pdf"
HS = "v2/vendor/ti/ti-lm5069.pdf"
ID = "v2/vendor/ti/ti-lm74700-q1.pdf"
L3R2 = "v2/docs/handover/layer3/l3r2.yaml"
ARCH = "v2/docs/ARCHITECTURE.md"
PINS = {
    L4E4_PY: "d4a484439a7b53030423b596769bf748469134a45a46b3c91724e2b80d9e2a42",
    L4E4_OUT: "f68bf6951a6361caf6c41db14d86d735f9e3e9736723984ef61234aa10a80694",
    R11_PY: "c5e9d5713abfcb07a15276c489ce9774a20bff029b11d205a9e9877a21ed2684",
    R11_OUT: "f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209",
    REPLAY_PY: "3de985e2e3e06453d2c9d576311c1f39935149ac1e9b7cff0431a40933bb8734",
    REPLAY_OUT: "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d",
    CONTRACT: "1c211e467d81b8b70546bc4435c65d4bd2dcd0d2fc3606714a746b4d8d0ac1fa",
    GEN_A: "6a136feec6c9cf4e2011ed8c45a1f2e0adc3e263718c355b4b909872ee5d3c4b",
    GEN_E: "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186",
    NET_A: "6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5",
    NET_E: "2ed95a0e8069ebf8ad31f4567a14015e863182a83b6de7b3b13218488d8316d4",
    BQ: "3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973",
    LT: "8f552a0b57677bfa7e4a5d5d0fac56d56fbbd1a6f65a9ee7aaaf8743cd534ec3",
    HS: "d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681",
    ID: "e16b3a8c0023201fafa5825436f5f2dd6f885b92b84e65602b3f50d741c58b6f",
    L3R2: "ee2efadf269994ce90830989714d3d48fecf0868b673e9f43e44b25b48fb091c",
    ARCH: "c883f948f3221e74de47a4e6a4210321cca931b95afab5257600d8d1ff678651",
}
# The few figures this record sets itself (ASSUMPTION or SESSION, each named where it is used):
T_NET = 0.01        # ASSUMPTION: the ILIM_HIZ network's own tolerance on its line, +-1 %; the engineer's resistors replace it
FRESH_S = 3.0       # SESSION: a VIN_MON reading older than 3 s (three of FW-E04's 1 s reports) counts as stale
DIAG_A = 0.3        # SESSION: the diagnostic's allowance over the pin's band before the network counts as failed
DEFICITS = (1.0, 3.0, 10.0)   # W: illustrative power deficits for the collapse time (INFERRED method)
VOLTS = (9.0, 12.0, 24.0, 36.0)
LEVELS = (86.5, 60.0, 50.0, 40.0, 30.0, 20.0, 10.0, 5.0)   # W at VBUS20, illustrative solar levels for the settle table
V_K0 = 8.75         # SESSION: the knee's zero, where the hardware line's target reaches 0 A
T_KNEE = 0.005      # ASSUMPTION: the knee's VIN_RAW thresholds within +-0.5 % (a precision reference; the engineer's choice replaces it)
LATCH_MARGIN = 0.10  # SESSION: the charger must be in HIZ at least 0.1 V above the latch's highest falling threshold


def refuse(code, msg):
    sys.stderr.write("l4e5_source_control: %s; refusing\n" % msg)
    sys.exit(code)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def pg(rel, n, layout=True):
    a = ["pdftotext"] + (["-layout"] if layout else []) + ["-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"]
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


def flat(t):
    return " ".join(t.split())


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def e96(lo):
    """The least IEC 60063 E96 value (by the series' formula) at or above lo, in ohms."""
    dec = 10 ** math.floor(math.log10(lo))
    for k in range(2):
        for i in range(96):
            v = round(10 ** (i / 96.0), 2) * dec * (10 ** k)
            if v >= lo - 1e-9:
                return v
    refuse(4, "no E96 value at or above %.1f" % lo)


def compute():
    for rel, want in PINS.items():
        if sha(rel) != want:
            refuse(2, "%s is not the pinned file" % rel)
    R = {}
    # ================================================================== 0: the reproductions
    out4 = open(os.path.join(TOP, L4E4_OUT), "rb").read()
    out11 = open(os.path.join(TOP, R11_OUT), "rb").read()
    outr = open(os.path.join(TOP, REPLAY_OUT), "rb").read()
    c4 = subprocess.run([sys.executable, "-B", os.path.join(TOP, L4E4_PY)], cwd=TOP, capture_output=True)
    R["r0a"] = c4.returncode == 0 and c4.stdout == out4
    c11 = subprocess.run([sys.executable, "-B", os.path.join(TOP, R11_PY)], cwd=TOP, capture_output=True)
    R["r0b"] = c11.returncode == 0 and c11.stdout == out11
    if not (R["r0a"] and R["r0b"]):
        refuse(4, "a child re-run does not reproduce its record (l4e4 %s, r11 %s)" % (R["r0a"], R["r0b"]))
    L4 = load("l4e4_limits_for_l4e5", L4E4_PY)
    R4 = L4.compute()
    R["r0c"] = ("\n".join(L4.render(R4)) + "\n").encode("utf-8") == out4
    RP = load("l4e_replay_for_l4e5", REPLAY_PY)
    rc, text, LR = L4.run_main_captured(RP)
    R["r0d"] = rc == 0 and text.encode("utf-8") == outr
    if not (R["r0c"] and R["r0d"]):
        refuse(4, "an in-process run does not print its record (l4e4 %s, replay %s)" % (R["r0c"], R["r0d"]))
    fn = R4["fn"]

    # ================================================================== 1: the inputs as drawn and as written
    sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
    import netlist_sexp as N
    a, e = N.load(os.path.join(TOP, NET_A)), N.load(os.path.join(TOP, NET_E))

    def nets(d, ref):
        return {p: v["net"] for p, v in d["pins"][ref].items()}

    def val(d, ref):
        return d["components"][ref]["value"]

    def members(d, net):
        return sorted({r for r, pins in d["pins"].items() for v in pins.values() if v["net"] == net})
    nc = lambda d, ref, p: nets(d, ref)[p].startswith("unconnected-")
    facts = [
        ("E: VIN_MON = R40 100k over R41 10k, U10 pin 39", val(e, "R40").startswith("100k 1%") and nets(e, "R40") == {"1": "VIN_RAW", "2": "VIN_MON"}
         and val(e, "R41").startswith("10k 1%") and nets(e, "R41") == {"1": "VIN_MON", "2": "GND"} and nets(e, "U10")["39"] == "VIN_MON"),
        ("E: DCIN_PGD = U6 (LM5069) pin 8 to U10 pin 15, R25 10k to +3V3_E6", nets(e, "U6")["8"] == "DCIN_PGD" and nets(e, "U10")["15"] == "DCIN_PGD"
         and nets(e, "R25") == {"1": "DCIN_PGD", "2": "+3V3_E6"}),
        ("E: U6 VIN pin 2 on DC_P, SENSE pin 1 on HS_S, OUT pin 9 on DC_HS", [nets(e, "U6")[k] for k in ("2", "1", "9")] == ["DC_P", "HS_S", "DC_HS"]),
        ("E: Q7 the hot-swap pass FET, source pins 1-3 on DC_HS, drain pin 5 on HS_S", "CSD19532Q5B" in val(e, "Q7")
         and [nets(e, "Q7")[k] for k in ("1", "2", "3", "4", "5")] == ["DC_HS", "DC_HS", "DC_HS", "HS_GATE", "HS_S"]),
        ("E: L2 passes DC_HS (pad 1) to VIN_RAW (pad 3)", nets(e, "L2")["1"] == "DC_HS" and nets(e, "L2")["3"] == "VIN_RAW"),
        ("E: R19 10 mOhm between DC_P and HS_S", val(e, "R19").startswith("10mOhm") and set(nets(e, "R19").values()) == {"DC_P", "HS_S"}),
        ("E: the vehicle's ideal diode U3 (LM74700) DC_F to DC_P, the tracker's U4 TRK_OUT to VIN_RAW",
         nets(e, "U3")["6"] == "DC_F" and nets(e, "U3")["4"] == "DC_P" and nets(e, "U4")["6"] == "TRK_OUT" and nets(e, "U4")["4"] == "VIN_RAW"),
        ("E: LT8705A U5 pins 25 to 28 (SRVO_FBIN, SRVO_IIN, SRVO_IOUT, SRVO_FBOUT) unconnected", all(nc(e, "U5", p) for p in ("25", "26", "27", "28"))),
        ("E: U10 pins 31, 32 (GPIO20, 21) and 41 (GPIO29, ADC3) unconnected", all(nc(e, "U10", p) for p in ("31", "32", "41"))),
        ("E: the tracker's FBOUT divider R10 115k over R11 10.0k", val(e, "R10").startswith("115k 1%") and nets(e, "R10") == {"1": "TRK_OUT", "2": "TRK_FBOUT"}
         and val(e, "R11").startswith("10.0k 1%") and nets(e, "R11") == {"1": "TRK_FBOUT", "2": "GND"} and nets(e, "U5")["6"] == "TRK_FBOUT"),
        ("A: U3 (BQ25731) pin 6 ILIM_HIZ on CHG_ILIM, R19 16.5k from REGN, R20 34.8k to GND, Q6 drain", nets(a, "U3")["6"] == "CHG_ILIM"
         and members(a, "CHG_ILIM") == ["Q6", "R19", "R20", "U3"] and nets(a, "R19") == {"1": "REGN", "2": "CHG_ILIM"} and val(a, "R19").startswith("16.5k")
         and nets(a, "R20") == {"1": "CHG_ILIM", "2": "GND"} and val(a, "R20").startswith("34.8k") and nets(a, "Q6")["3"] == "CHG_ILIM"),
        ("A: U3 pin 1 (VBUS) on VBUS20", nets(a, "U3")["1"] == "VBUS20"),
        ("A: FE_PGOOD on U27 pin 20, CHRG_OK on U27 pin 13, U27 INT on EXP_INT", [nets(a, "U27")[k] for k in ("20", "13", "1")] == ["FE_PGOOD", "CHRG_OK", "EXP_INT"]),
        ("A: no IC pin on VIN_RAW, FE_UVS or FE_RUN reaches a controller (no reading of VIN_RAW on board A)",
         not [r for r in members(a, "VIN_RAW") if r.startswith("U")] and members(a, "FE_UVS") == ["C211", "R14", "R15", "U34"]
         and [r for r in members(a, "FE_RUN") if r.startswith("U")] == ["U34"]),
    ]
    bad = [f for f, ok in facts if not ok]
    if bad:
        refuse(3, "a netlist fact does not hold: %s" % bad)
    R["facts"] = [f for f, _ in facts]
    R["vin_raw_a"], R["vin_raw_e"] = members(a, "VIN_RAW"), members(e, "VIN_RAW")

    def cap_uF(v):
        m = re.match(r"([\d.]+)u\b", v)
        return float(m.group(1)) if m else None
    caps = []
    for d, side, net in ((a, "A", "VIN_RAW"), (e, "E", "VIN_RAW"), (e, "E", "TRK_OUT")):
        for r in members(d, net):
            if r.startswith("C") and set(nets(d, r).values()) == {net, "GND"}:
                caps.append((side, r, net, cap_uF(val(d, r)), val(d, r)))
    if any(c[3] is None for c in caps):
        refuse(3, "a capacitor value on VIN_RAW or TRK_OUT does not parse")
    R["caps"] = caps
    R["c_bus"] = sum(c[3] for c in caps) * 1e-6
    r10 = float(re.match(r"([\d.]+)k", val(e, "R10")).group(1)) * 1e3
    r11e = float(re.match(r"([\d.]+)k", val(e, "R11")).group(1)) * 1e3
    rtol = float(re.search(r"(\d+)%", val(e, "R10")).group(1)) / 100.0

    # HW-FW-CONTRACT.md: FW-A16 and FW-E04 as written
    ct = open(os.path.join(TOP, CONTRACT), encoding="utf-8").read()
    row16 = need(ct, r"^\| FW-A16 \|.*$", "the FW-A16 row").group(0)
    m = need(row16, r"IIN_HOST at or below ([\d.]+) x ([\d.]+) A x ([\d.]+) x VIN_RAW / ([\d.]+) V \(([\d.]+) A at 9 V, ([\d.]+) A at 12 V, ([\d.]+) A at 24 V\)",
             "FW-A16's rule")
    k80, i_ent, eta, vbus_max = (float(m.group(i)) for i in (1, 2, 3, 4))
    printed = tuple(float(m.group(i)) for i in (5, 6, 7))
    slope = k80 * i_ent * eta / vbus_max
    if tuple(round(slope * v, 2) for v in (9.0, 12.0, 24.0)) != printed:
        refuse(4, "FW-A16's line does not reproduce its own printed figures")
    o33 = need(row16, r"caps charge at about (\d+) W against the tracker's (\d+) W, a recorded reduction \(O-33\)", "O-33 in FW-A16")
    need(row16, r"the charger resets it to 3\.25 A at every adapter removal, SLUSE66A 9\.3\.6", "FW-A16 (b)")
    vindpm = float(need(row16, r"write VINDPM to about ([\d.]+) V", "FW-A16 (c)").group(1))
    e04 = float(need(ct, r"^\| FW-E04 \|.*Report both over USB at (\d+) s for FW-A16", "FW-E04's period").group(1))
    need(ct, r"^\| FW-A01 \|.*write ChargeOption1 RSNS_RAC = 0b FIRST", "FW-A01")
    need(ct, r"^\| FW-C12 \| the panel's USB device on bank 1", "FW-C12 (the panel's only link to the modules)")
    need(open(os.path.join(TOP, ARCH), encoding="utf-8").read(), r"USB to B bank 3 port 2", "ARCHITECTURE.md: board E's USB to B bank 3")
    R.update(k80=k80, i_ent=i_ent, eta=eta, vbus_max=vbus_max, printed=printed, slope=slope, o33=(float(o33.group(1)), float(o33.group(2))),
             vindpm=vindpm, e04=e04)
    # the generators' own statements
    ga = re.sub(r"\n\s*#\s*", " ", open(os.path.join(TOP, GEN_A), encoding="utf-8").read())
    lt3 = need(ga, r"threshold at ([\d.]+) / ([\d.]+) / ([\d.]+) V falling and ([\d.]+) / ([\d.]+) / ([\d.]+) V rising", "gen_sch_a.py U34's UV thresholds")
    latch = tuple(float(lt3.group(i)) for i in (1, 2, 3))
    ent = need(ga, r"limits the vehicle entry at ([\d.]+) to ([\d.]+) A \(([\d.]+) A with R19's 1 percent\)", "gen_sch_a.py the entry's limit")
    ent_lim = (float(ent.group(1)), float(ent.group(2)), float(ent.group(3)))
    rst = need(ga, r"a dip under 8 V interrupts charging for about ([\d.]+) to ([\d.]+) s", "gen_sch_a.py the restart's interruption")
    clamp = float(need(ga, r"VIN_RAW's clamp reaches ([\d.]+) V", "gen_sch_a.py VIN_RAW's clamp").group(1))
    xo = need(ga, r"crossover ([\d.]+) to ([\d.]+) kHz", "gen_sch_a.py the front end's loop crossover")
    R["fe_xo"] = (float(xo.group(1)), float(xo.group(2)))
    if abs(ent_lim[2] - i_ent) > 1e-9:
        refuse(4, "FW-A16's entry figure is not gen_sch_a.py's")
    l3 = open(os.path.join(TOP, L3R2), encoding="utf-8").read()
    req015 = need(l3, r"REQ-015: '(A 9 to 36 V vehicle and shore input runs the kit and charges the pack)'", "REQ-015's text").group(1)
    R.update(latch=latch, ent_lim=ent_lim, restart=(float(rst.group(1)), float(rst.group(2))), clamp=clamp, req015=req015)

    # the makers
    b6 = flat(pg(BQ, 6))
    pin = need(b6, r"V\(ILIM_HIZ\) = (\d) V \+ (\d+) \u00d7 IDPM \u00d7 Rac", "SLUSE66A p.6 the ILIM_HIZ equation")
    pin_off, pin_gain = float(pin.group(1)), float(pin.group(2))
    need(b6, r"the input current limit used by the charger is the lower setting of ILIM_HIZ pin and IIN_HOST register", "p.6 the lower of the two")
    need(b6, r"The ILIM_HIZ pin voltage is continuous read and used for updating current limit setting", "p.6 continuous read")
    need(b6, r"When the pin voltage is below 0\.4 V, the device enters high impedance \(HIZ\) mode", "p.6 HIZ below 0.4 V")
    b17 = pg(BQ, 17)
    hiz_rise = float(need(b17, r"VHIZ_ LO\s+ILIM_HIZ pin rising\s+([\d.]+)\s+V", "p.17 VHIZ_LO").group(1))
    hiz_fall = float(need(b17, r"VHIZ_ HIGH\s+ILIM_HIZ pin falling\s+([\d.]+)\s+V", "p.17 VHIZ_HIGH").group(1))
    need(flat(pg(BQ, 27, False)), r"In order to exit HIZ mode, ILIM_HIZ pin voltage has to be higher than 0\.8 V and EN_HIZ bit has to be set to 0b\.",
         "p.27 the HIZ exit, the pin and EN_HIZ")
    need(pg(BQ, 64), r"Table 9-32\. ChargeOption3 Register \(I2C address = 35h\) Field Descriptions\s+BIT\s+FIELD\s+TYPE\s+RESET\s+DESCRIPTION\s+"
                     r"7\s+EN_HIZ\s+R/W\s+0b\s+Device HIZ Mode Enable", "p.64 EN_HIZ, REG0x35 bit 7, reset 0b")
    b10 = pg(BQ, 10)
    need(b10, r"5-m[\u03a9\u2126] RAC sensing\s+VILIM_HIZ = 1\.2 V", "p.10 the ILIM_HIZ rows are for the 5 mOhm RAC")
    rows = re.findall(r"VILIM_HIZ = ([\d.]+) V\s+(\d+)\s+(\d+)\s+(\d+)\s+mA", b10)
    if len(rows) != 4:
        refuse(3, "SLUSE66A p.10 the four ILIM_HIZ accuracy rows not parsed")
    err5 = max(max(float(ty) - float(lo), float(hi) - float(ty)) for _v, lo, ty, hi in rows) * 1e-3
    rng = need(b10, r"VIREG_DPM_RNG_ILIM\s+([\d.]+)\s+([\d.]+)\s+V", "p.10 the pin's regulation range")
    pin_rng = (float(rng.group(1)), float(rng.group(2)))
    r16_nom = float(re.match(r"(\d+)mOhm", R4["r16"]).group(1)) * 1e-3
    err10 = err5 * 0.005 / r16_nom        # INFERRED: the same error at the pin, in amps at R16's 10 mOhm
    b25, b26 = flat(pg(BQ, 25)), flat(pg(BQ, 26))
    host_clamp = float(need(b25, r"the maximum IIN_HOST setting is clamped at ([\d.]+) A", "p.25 the 10 mOhm clamp").group(1))
    need(b26, r"The actual input current limit being adopted by the device is the lower setting of IIN_DPM and ILIM_HIZ pin\.", "p.26 9.3.6")
    need(b26, r"when adapter is removed IIN_HOST will be reset one time to 3\.25 A, under battery only host is still able to overwrite IIN_HOST register with a new value\. "
              r"If the adapter plug back in and CHRG_OK is pulled up, IIN_HOST will not be reset again\.", "p.26 the reset and the overwrite")
    need(b26, r"The voltage regulation loop of the charger regulates the input voltage to prevent the input adapter collapsing", "p.26 VINDPM on VBUS")
    b62, b63, b80 = pg(BQ, 62), pg(BQ, 63), flat(pg(BQ, 80))
    need(b62, r"9\.6\.12 ChargeOption2 Register \(I2C address = 33/32h\) \[reset = 00B7\]", "p.62 ChargeOption2's reset")
    need(b63, r"Table 9-31\. ChargeOption2 Register \(I2C address = 32h\) Field Descriptions\s+BIT\s+FIELD\s+TYPE\s+RESET\s+DESCRIPTION\s+7\s+EN_EXTILIM\s+R/W\s+1b",
         "p.63 EN_EXTILIM, REG0x32 bit 7, reset 1b")
    need(b80, r"In order to disable ILIM_HIZ pin, the host can write EN_EXTILIM=0b to disable ILIM_HIZ pin, or pull ILIM_HIZ pin above 4\.0 V\.", "p.80 the pin's disable")
    need(b80, r"IIN_HOST Register \(I2C address = 0F/0Eh\) \[reset = 4100h\]", "p.80 IIN_HOST's figure annotation 4100h")
    need(b80, r"9\.6\.22 IIN_HOST Register \(I2C address = 0F/0Eh\) \[reset = 2000h\]", "p.80 IIN_HOST's heading annotation 2000h")
    need(b80, r"The default nominal input current limit is 3\.25 A\. Upon adapter removal, the input current limit is reset to the default value of 3\.25 A\.",
         "p.80 the 10 mOhm default and its removal reset")
    need(b80, r"The default current limit is 3\.2 A\.", "p.80 the 5 mOhm default")
    t9 = pg(BQ, 80) + pg(BQ, 81)
    bits = re.findall(r"^\s*(\d)\s+Input Current set by host, bit (\d)\s+R/W\s+([01])b\s+0 = Adds 0 mA of input current\.\s+1 = Adds (\d+) mA", t9, re.M)
    if [int(b_[0]) for b_ in bits] != [6, 5, 4, 3, 2, 1, 0] or any(b_[0] != b_[1] for b_ in bits):
        refuse(3, "SLUSE66A Table 9-50's seven IIN_HOST bits not parsed (pp.80 and 81)")
    w5 = {int(b_[0]): float(b_[3]) * 1e-3 for b_ in bits}
    reset_bits = sum(1 << int(b_[0]) for b_ in bits if b_[2] == "1")

    def reg5(hi_byte):                             # the register's current in the 5 mOhm table's terms (RSNS_RAC = 1b at POR)
        return sum(w5[k] for k in range(7) if hi_byte >> k & 1)
    b8 = pg(BQ, 8)
    amax = float(need(b8, r"CELL_BATPRESZ, ILIM_HIZ,\s+LODRV1, LODRV2, VDDA, COMP2, CMPIN, CMPOUT,OTG/VAP/\s+\u20130\.3\s+(\d+)", "p.8 ILIM_HIZ absolute maximum").group(1))
    rmax = float(need(b8, r"CELL_BATPRESZ, ILIM_HIZ,\s+0\s+([\d.]+)", "p.8 ILIM_HIZ recommended maximum").group(1))
    por = {"2000h (p.80 heading)": 0x20, "4100h (p.80 figure)": 0x41}
    R["por"] = {k: (reg5(v), reg5(v) * 0.005 / float(re.match(r"(\d+)mOhm", R4["r16"]).group(1)) * 1e3) for k, v in por.items()}
    R["por_table_code"] = reset_bits
    R.update(hiz=(hiz_fall, hiz_rise), pin_off=pin_off, pin_gain=pin_gain, err5=err5, err10=err10, pin_rng=pin_rng, r16_nom=r16_nom, host_clamp=host_clamp,
             pin_amax=amax, pin_rmax=rmax, ilim_rows=[(float(v), float(lo), float(ty), float(hi)) for v, lo, ty, hi in rows])
    l4 = pg(LT, 4)
    fbo = need(l4, r"Regulation Voltage for FBOUT\s+VC = 1\.2V \(LT8705AE, LT8705AI\)\s+l\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V\s+"
                   r"VC = 1\.2V \(LT8705AH, LT8705AMP\)\s+l\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "8705af p.4 FBOUT")
    fbout = (min(float(fbo.group(1)), float(fbo.group(4))), float(fbo.group(2)), max(float(fbo.group(3)), float(fbo.group(6))))
    sfb = need(l4, r"SRVO_FBIN Activation Threshold \(Note 5\)\s+\(VFBIN Falling\) \u2013 \(Regulation Voltage for FBIN\),\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "p.4 SRVO_FBIN threshold")
    l11, l19 = flat(pg(LT, 11, False)), flat(pg(LT, 19, False))
    need(l11, r"SRVO_FBIN \(Pin 25 QFN Only\): Open-Drain Logic Output\. This pin is pulled to ground when the input voltage feedback loop is active\.", "p.11 SRVO_FBIN")
    need(l11, r"SRVO_FBOUT \(Pin 28 QFN Only\): Open-Drain Logic Output\. This pin is pulled to ground when the output voltage feedback loop is active\.", "p.11 SRVO_FBOUT")
    need(l19, r"SRVO_FBIN is pulled low when FBIN is near or lower than its regulation voltage", "p.19 SRVO pins")
    R.update(fbout=fbout, srvo_fbin=tuple(float(sfb.group(i)) for i in (1, 2, 3)), r10=r10, r11e=r11e, rtol=rtol)
    h3, h6, h12 = flat(pg(HS, 3, False)), pg(HS, 6), flat(pg(HS, 12, False))
    need(h3, r"When the external MOSFET VDS decreases below 1\.25 V, the PGD indicator is active \(high\)\. When the external MOSFET VDS increases above 2\.5 V the PGD", "SNVS452G p.3 PGD")
    need(h12, r"When the voltage at OUT increases to within 1\.25 V of the SENSE pin \(VDS <1\.25 V\), PGD switches high\. PGD switches low if the VDS of Q1 increases above 2\.5 V", "p.12 8.3.6")
    need(h6, r"SNVS452G", "SNVS452G on p.6")
    tm = need(h6, r"VTMRH\s+Upper threshold\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "p.6 VTMRH")
    ti = need(h6, r"Fault detection current\s+(\d+)\s+(\d+)\s+(\d+)\s+\u00b5A", "p.6 the fault timer current")
    ct5 = val(e, "C5")
    if not (ct5.startswith("100n") and nets(e, "C5") == {"1": "HS_TIMER", "2": "GND_V"} and nets(e, "U6")["6"] == "HS_TIMER"):
        refuse(3, "board E's C5 is not the 100 nF timer capacitor")
    c_t = 100e-9
    t_fault = (c_t * float(tm.group(1)) / (float(ti.group(3)) * 1e-6), c_t * float(tm.group(2)) / (float(ti.group(2)) * 1e-6),
               c_t * float(tm.group(3)) / (float(ti.group(1)) * 1e-6))
    i12 = flat(pg(ID, 12, False))
    need(i12, r"The LM74700-Q1 ideal diode controller has all the features necessary to implement an efficient and fast reverse polarity protection circuit "
              r"or be used in an ORing configuration", "SNOSD17G p.12")
    R.update(t_fault=t_fault)

    # ================================================================== 2: the timescales (INFERRED)
    v_trk_nom = fbout[1] * (1 + r10 / r11e)
    v_trk = (fbout[0] * (1 + r10 * (1 - rtol) / (r11e * (1 + rtol))), v_trk_nom, fbout[2] * (1 + r10 * (1 + rtol) / (r11e * (1 - rtol))))
    e_col = 0.5 * R["c_bus"] * (v_trk_nom ** 2 - latch[2] ** 2)
    R.update(v_trk=v_trk, e_col=e_col, t_col=[(dp, e_col / dp) for dp in DEFICITS])

    # ================================================================== 3: the candidates' envelopes
    lsb, setting, u3max_host = R4["lsb"], R4["setting"], R4["u3max"]
    r16_lo, r16_hi, loads4, req = R4["r16_lo"], R4["r16_hi"], R4["loads4"], R4["req"]
    u3tol = RP.U3_TOL

    def line(v):
        return slope * v

    def reg_a(v):                       # FW-A16 (a) as written: the register code at or below the line, under the clamp
        return min(math.floor(round(line(v) / lsb, 9)) * lsb, math.floor(round(host_clamp / lsb, 9)) * lsb)

    def pin_hi(v):
        return line(v) * (1 + T_NET) + err10

    def pin_lo(v):
        return max(0.0, line(v) * (1 - T_NET) - err10)

    vk1 = float(need(req015, r"A (\d+) to (\d+) V", "REQ-015's floor").group(1))
    g_pin = pin_gain * r16_nom                     # V at the pin per A at the nominal RAC
    s_k = g_pin * line(vk1) / (vk1 - V_K0)        # the knee's slope at the pin, V per V of VIN_RAW

    def vpin_h3(v):                                # H3's nominal pin voltage: FW-A16's line from REQ-015's floor, the knee below
        return pin_off + g_pin * line(v) if v >= vk1 else pin_off + s_k * (v - V_K0)

    def tgt_h3(v):
        return max(0.0, (vpin_h3(v) - pin_off) / g_pin)
    def v_at_pin(vp):                              # VIN_RAW at which H3's nominal knee puts the pin at vp (below the 9 V floor)
        return V_K0 - (pin_off - vp) / s_k
    band = lambda v: (v * (1 - T_KNEE), v, v * (1 + T_KNEE))
    v_hiz = v_at_pin(hiz_fall)
    v_unhiz = v_at_pin(hiz_rise)
    v_rng = v_at_pin(pin_rng[0])
    v_hiz_lo = band(v_hiz)[0]                      # HIZ certain below this (the pin under 0.4 V at the network's low corner)
    v_unhiz_hi = band(v_unhiz)[2]                  # out of HIZ above this with EN_HIZ = 0 (the pin over 0.8 V at the high corner)
    R["knee"] = dict(zero=band(V_K0), entry=band(v_hiz), exit=band(v_unhiz), rng=band(v_rng),
                     table=[(v, vpin_h3(v)) for v in (8.40, round(v_hiz_lo, 3), round(v_hiz, 3), 8.60, round(v_unhiz, 3), 8.70,
                                                      round(v_unhiz_hi, 3), V_K0, round(v_rng, 3), 9.0)])
    k0h, k1h = V_K0 * (1 + T_KNEE), vk1 * (1 + T_KNEE)
    floor_min = max(0.0, line(k1h) * (vk1 - k0h) / (k1h - k0h) * (1 - T_NET) - err10)
    if not (v_hiz_lo >= latch[2] + LATCH_MARGIN and floor_min > 0 and V_K0 * (1 + T_KNEE) < vk1):
        refuse(4, "the knee does not fit between the latch and REQ-015's floor")
    R.update(vk1=vk1, s_k=s_k, v_hiz=v_hiz, v_hiz_lo=v_hiz_lo, v_unhiz=v_unhiz, v_unhiz_hi=v_unhiz_hi, floor_min=floor_min, g_pin=g_pin)

    def board_max_h(v):                 # the hardware line under the 4.70 A ceiling: the lower TARGET governs, with its own error
        return (pin_hi(v) / r16_lo) if line(v) < setting else fn["board_max"](setting)

    def fe_in(board, v):                # the front end's input current at VBUS20's maximum and FW-A16's efficiency
        return (board + loads4) * vbus_max / (eta * v)
    env = []
    for v in VOLTS:
        ra = reg_a(v)
        env.append(dict(v=v, line=line(v), reg_a=ra, fe_a=fe_in(fn["board_max"](ra), v), u3a=ra,
                        reg_b=min(ra, setting), fe_b=fe_in(fn["board_max"](min(ra, setting)), v),
                        pin_v=pin_off + pin_gain * r16_nom * line(v), pin_hi=pin_hi(v), pin_lo=pin_lo(v),
                        eff=min(line(v), setting), board_h=board_max_h(v), fe_h=fe_in(board_max_h(v), v)))
    R["env"] = env
    R["fe_h_max"] = max(fe_in(board_max_h(v / 10.0), v / 10.0) for v in range(90, 361))
    R["fe_h_max_v"] = max(range(90, 361), key=lambda v: fe_in(board_max_h(v / 10.0), v / 10.0)) / 10.0
    R["fe_a_max"] = max(fe_in(fn["board_max"](reg_a(v / 10.0)), v / 10.0) for v in range(90, 361))
    # the efficiency at 9 V that would put the hardware line's front-end current at the entry's FW-A16 basis (INFERRED)
    R["eta_at_basis"] = (board_max_h(9.0) + loads4) * vbus_max / (i_ent * 9.0)
    R["v_cross"] = setting / slope
    R["band_x"] = ((u3max_host - err10) / (1 + T_NET) / slope, setting / slope)   # the line's band where the pin's max passes U3's own max
    R["pin_v_36"] = pin_off + pin_gain * r16_nom * line(36.0) * (1 + T_NET)
    R["pin_v_clamp"] = pin_off + pin_gain * r16_nom * line(clamp) * (1 + T_NET)
    R["v_pin_disable"] = (4.0 - pin_off) / (pin_gain * r16_nom * slope)
    # (a) on the tracker's nominal VIN_RAW; the per-source solar setting of (b); the tracker ceiling H2 needs
    R["reg_a_trk"] = reg_a(v_trk_nom)
    R["o33_nom_w"] = line(v_trk_nom) * vbus_max
    lim_need = (req * r16_hi + err10) / (1 - T_NET)        # the pin's nominal line at which its minimum covers the window
    v_need = lim_need / slope
    r10_min = r11e * (1 + rtol) / (1 - rtol) * (v_need / fbout[0] - 1)
    r10_new = e96(r10_min)
    v_trk2 = (fbout[0] * (1 + r10_new * (1 - rtol) / (r11e * (1 + rtol))), fbout[1] * (1 + r10_new / r11e),
              fbout[2] * (1 + r10_new * (1 + rtol) / (r11e * (1 - rtol))))
    if not (v_trk2[0] >= v_need and v_trk2[2] <= 36.0):
        refuse(4, "the raised tracker ceiling is not inside REQ-015's 36 V with its minimum above the window's need")
    R.update(lim_need=lim_need, v_need=v_need, r10_min=r10_min, r10_new=r10_new, v_trk2=v_trk2)
    # the tracker's output parts against the raised ceiling (NETLIST values, their rated volts)
    trk_parts = []
    for side, r, net, uf, v_ in caps:
        if net == "TRK_OUT":
            rated = float(re.search(r"\s(\d+)V\b", v_).group(1))
            trk_parts.append((r, v_, rated, v_trk2[2] / rated))
    R["trk_parts"] = trk_parts
    # the low-light bounds of H1 and H2: the power at VBUS20 under which the bus settles below the latch, and below 12 V
    thr = (pin_hi(latch[2]) / r16_lo + loads4) * vbus_max
    thr_nom = (line(latch[2]) + loads4) * vbus_max
    thr12 = (pin_hi(12.0) / r16_lo + loads4) * vbus_max
    thr12_nom = (line(12.0) + loads4) * vbus_max
    R.update(thr=thr, thr_nom=thr_nom, thr12=thr12, thr12_nom=thr12_nom)
    v_min, v_nom, win = LR["v_min"], LR["v_nom"], LR["win_req016"]
    def solve(i_b, f):
        """VIN_RAW at which the increasing board-current target f(v) meets i_b (bisection); None if above 40 V."""
        lo_, hi_ = 7.0, 40.0
        if f(hi_) < i_b or f(lo_) >= i_b:
            return None                            # above 40 V, or no settle at all above the knee: HIZ cycling
        for _ in range(80):
            mid = 0.5 * (lo_ + hi_)
            if f(mid) < i_b:
                lo_ = mid
            else:
                hi_ = mid
        return hi_
    f_nom = tgt_h3
    f_hi = lambda v: (tgt_h3(v) * (1 + T_NET) + err10) / r16_lo
    f_lo = lambda v: max(0.0, tgt_h3(v) * (1 - T_NET) - err10) / r16_hi
    settle = []
    for p in LEVELS:
        settle.append((p, solve(max(0.0, p / v_nom - loads4), f_nom), solve(max(0.0, p / vbus_max - loads4), f_hi),
                       solve(max(0.0, p / v_min - loads4), f_lo), p / v_min - loads4))
    R["settle"] = settle
    R["thr_h3"] = (err10 / r16_lo + loads4) * vbus_max     # under it the pin's own error may hold U3 above the stage: HIZ cycling

    # B3 (check astra-check-l4e5-1): a source-blind line held at H3's 9 V target up to 12 V, then rising with the same slope
    def tgt_flat(v):
        return tgt_h3(v) if v < vk1 else (line(vk1) if v < 12.0 else line(vk1) + slope * (v - 12.0))
    fh_flat = lambda v: (tgt_flat(v) * (1 + T_NET) + err10) / r16_lo
    b12 = lambda f12: (f12 + loads4) * vbus_max        # the solar power that settles the bus at 12 V = the charge power admitted at 12 V
    v_need_flat = 12.0 + (lim_need - line(vk1)) / slope
    r10f = e96(r11e * (1 + rtol) / (1 - rtol) * (v_need_flat / fbout[0] - 1))
    trk_f = (fbout[0] * (1 + r10f * (1 - rtol) / (r11e * (1 + rtol))), fbout[1] * (1 + r10f / r11e),
             fbout[2] * (1 + r10f * (1 + rtol) / (r11e * (1 - rtol))))
    fe_flat = max(fe_in(min(fh_flat(v / 10.0), fn["board_max"](setting) if tgt_flat(v / 10.0) >= setting else fh_flat(v / 10.0)), v / 10.0)
                  for v in range(90, 361))
    R["flat"] = dict(b12=b12(fh_flat(12.0)), b12_h3=b12(f_hi(12.0)), s40=solve(40.0 / vbus_max - loads4, fh_flat),
                     s40_h3=solve(40.0 / vbus_max - loads4, f_hi), at=[(v, tgt_flat(v), line(v)) for v in (9.0, 12.0, 24.0)],
                     p12=(tgt_flat(12.0) * v_nom, line(12.0) * v_nom), fe_max=fe_flat, v_need=v_need_flat, r10=r10f, trk=trk_f,
                     c35=max(trk_f[2] / rt for _r, _v, rt, _f in trk_parts if rt > 30))
    R["load0"] = LR["load0"]
    if not (abs(R["flat"]["b12"] - 38.748) < 0.01 and R["flat"]["fe_max"] <= R["fe_h_max"] + 1e-12):
        refuse(4, "the check's counter-example does not reproduce (%.3f W)" % R["flat"]["b12"])
    # the offset variant, rejected: a line through zero just above the latch, slope bounded at 36 V
    v0 = 8.4
    k_off = slope / (1 - v0 / 36.0)
    R["offset"] = dict(v0=v0, k=k_off, at=[(v, k_off * (v - v0), line(v)) for v in (9.0, 12.0, 24.0)],
                       trk=v0 + lim_need / k_off)

    # ================================================================== 4: the energy each gives up (MODELED, the replay's own functions)
    run, meanday, CASES, we = LR["run"], LR["meanday"], LR["CASES"], LR["we"]
    LID = RP.LID_A
    p_pin_min_drawn = pin_lo(v_trk[0])
    keys = {
        "A": ("FW-A16 as written (a)", R["reg_a_trk"] - u3tol),
        "B": ("per-source firmware (b), solar at 4.70 A", setting - u3tol),
        "H1": ("hardware line, tracker as drawn (c, H1)", min(setting - u3tol, p_pin_min_drawn)),
        "H2": ("hardware line, tracker ceiling raised (c, H2)", min(setting - u3tol, pin_lo(v_trk2[0]))),
        "H3": ("H2 with the knee into HIZ (c, H3, CHOSEN)", min(setting - u3tol, pin_lo(v_trk2[0]))),
    }
    for k, (_lab, iin) in keys.items():
        CASES["L4E5-" + k] = (v_min, iin, we(v_min, 6.1))
    R["keys"] = {k: (lab, iin, iin * v_min) for k, (lab, iin) in keys.items()}
    traces = {"screen": dict(base=LR["prof0"], gser=None, wp=RP.WP_TRACE, ratio=None),
              "cand": dict(base=LR["gs"](LR["tr_nom"]), gser=LR["gs"](LR["tr_nom"]), wp=100.0, ratio=1.0)}

    def kw(t, series="base"):
        return dict(gser=(t["gser"] if series == "base" else series), wp=t["wp"], ratio=t["ratio"])
    ER = {}
    for tk, t in traces.items():
        hours = [run("A2", "WE", LID, "TYP", h, 1, win, **kw(t))["acct"]["bus_avail"] for h in range(24)]
        ref = run("A2", "WE", LID, "TYP", 0, 24, win, **kw(t))["acct"]
        if abs(sum(hours) - ref["bus_avail"]) > 1e-9 or ref["not_taken"] > 1e-9:
            refuse(4, "the hour-by-hour availability does not close on the day (%s)" % tk)
        zero = [g if hours[h] >= thr else 0.0 for h, g in enumerate(t["base"])]
        zero3 = [g if hours[h] >= R["thr_h3"] else 0.0 for h, g in enumerate(t["base"])]

        def svc(key, col, series="base"):
            out_ = []
            for hh in (48, 72):
                s = meanday("A2", key, LID, "TYP", hh, win, collapse=col, **kw(t, series))
                out_.append(max(s["uns"]))
            return out_

        def day(key, col, series="base"):
            a_ = run("A2", key, LID, "TYP", 0, 24, win, collapse=col, **kw(t, series))["acct"]
            return a_["bus_avail"] - a_["not_taken"]
        res = {"avail": ref["bus_avail"], "hours": hours, "peak": max(hours), "ref_svc": svc("WE", False),
               "n_below": sum(1 for x in hours if 0 < x < thr), "e_below": sum(x for x in hours if x < thr),
               "n_mid": sum(1 for x in hours if thr <= x < thr12), "n_up": sum(1 for x in hours if x >= thr12),
               "n_h3": sum(1 for x in hours if 0 < x < R["thr_h3"]), "e_h3": sum(x for x in hours if x < R["thr_h3"])}
        for k in keys:
            if k in ("A", "B"):
                up, lo = (day("L4E5-" + k, False), svc("L4E5-" + k, False)), (day("L4E5-" + k, True), svc("L4E5-" + k, True))
            else:
                zz = zero3 if k == "H3" else zero
                up, lo = (day("L4E5-" + k, False), svc("L4E5-" + k, False)), (day("L4E5-" + k, False, zz), svc("L4E5-" + k, False, zz))
            res[k] = dict(up=up, lo=lo)
        ER[tk] = res
    # the reproduction of the replay's corrected rows by these calls
    rpo = outr.decode("utf-8")
    w48 = re.search(r"A2 CORRECTED, U3 6\.1 A minimum \(the drafted 6\.2 A setting\)\s+unserved ([\d.]+) / ([\d.]+) Wh at 48 / 72 h", rpo)
    c12 = re.search(r"CORRECTED, WE; O-2 nominal \([\d.]+ V, [\d.]+ A\): [\d.]+ Wh a day into the stage\n\s+A1:.*\n\s+A2: first interruption h [\d/]+; "
                    r"unserved ([\d.]+) / ([\d.]+) at 48 h, ([\d.]+) / ([\d.]+) at 72 h", rpo)
    if not (w48 and c12):
        refuse(3, "l4e_replay.out's corrected A2 rows not parsed")
    R["repro"] = dict(screen=(float(w48.group(1)), float(w48.group(2))), cand=(max(float(c12.group(1)), float(c12.group(2))), max(float(c12.group(3)), float(c12.group(4)))))
    for tk in ("screen", "cand"):
        mine = tuple(round(x, 1) for x in ER[tk]["ref_svc"])
        if mine != R["repro"][tk]:
            refuse(4, "the replay's corrected A2 row on %s is not reproduced: %s against %s" % (tk, mine, R["repro"][tk]))
    R["ER"] = ER

    # ================================================================== 6: the chosen rule's contract predicates
    writes = {"at POR, RSNS_RAC = 1b, board current (the larger annotation)": max(v_[1] for v_ in R["por"].values()),
              "after every adapter removal (one-time reset, p.26, p.80)": 3.25, "firmware ceiling (FW-A16 restated)": setting}
    fb = {v: min(reg_a(v), setting) for v in VOLTS}
    R["diag"] = dict(trip12=board_max_h(12.0) + DIAG_A, pin_off_board=fn["board_max"](setting), fallback=fb, stale=reg_a(9.0),
                     max_fallback=max(list(fb.values()) + [reg_a(9.0)]))
    R["writes"] = writes
    R["max_written"] = max(writes.values())
    R["code"], R["word"] = R4["code"], R4["word"]

    # ================================================================== 7: the consequence for L4-E4
    r11 = R4["r11"]
    tap25 = R4["r11_pick"]["tap"][2]
    R["l4e4"] = dict(setting=setting, u3max=u3max_host, serv=R4["serv"], per_t=[(t["t"], t["m_alone"], t["m_kel"], t["m_full"]) for t in R4["per_t"]],
                     r11=r11, tap25=tap25, c1_prior=R4["c1_prior"])
    serv_x = (setting * (1 + T_NET) + err10) / r16_lo + loads4          # the pin governing just under the crossover
    mx = fn["margins_for"](serv_x, r11, tap25)
    trx = fn["tap_rule"](r11, serv_x)
    R["cross"] = dict(board=(setting * (1 + T_NET) + err10) / r16_lo, serv=serv_x,
                      per_t=[(t["t"], t["m_alone"], t["m_kel"], t["m_full"]) for t in mx], tap=trx,
                      ok_alone=all(t["m_alone"] > 0 for t in mx), ok_kel=all(t["m_kel"] > 0 for t in mx), ok_full=all(t["m_full"] > 0 for t in mx),
                      tap_ok=trx[2] >= R4["c1_prior"] and fn["band"](r11)[0] > serv_x,
                      err_allow=(u3max_host - setting * (1 + T_NET)))
    elx = [c for c in R4["cands"] if fn["band"](c["r"])[0] > serv_x and fn["tap_rule"](c["r"], serv_x)[2] >= R4["c1_prior"]]
    bx = max(elx, key=lambda c: c["r"]) if elx else None
    R["cross"]["r11_ok"] = (bx["r"], bx["code"], fn["band"](bx["r"])[2], fn["tap_rule"](bx["r"], serv_x)[2]) if bx else None
    R["cross"]["hi_now"] = fn["band"](r11)[2]
    # candidate (a)'s highest register, re-run through L4-E4's own functions
    s_a = reg_a(36.0)
    serv_a = fn["serv_of"](s_a)
    ma = fn["margins_for"](serv_a, r11, tap25)
    elig = [c for c in R4["cands"] if fn["band"](c["r"])[0] > serv_a and fn["tap_rule"](c["r"], serv_a)[2] >= R4["c1_prior"]]
    R["cand_a"] = dict(s=s_a, serv=serv_a, worst=min(t["m_alone"] for t in ma), r11_ok=(max(elig, key=lambda c: c["r"]) if elig else None),
                       v_over=min(v / 10.0 for v in range(90, 361) if reg_a(v / 10.0) > setting))
    R.update(v_min=v_min, v_nom=v_nom, win=win, u3tol=u3tol, lsb=lsb, setting=setting, u3max_host=u3max_host, r16_lo=r16_lo, r16_hi=r16_hi,
             loads4=loads4, req=req)
    R["t_fault_ratio"] = e04 / t_fault[0]
    return R


def render(R):
    o = []
    P = o.append
    P("L4-E5: SOURCE CONTROL FOR BOARD A'S CHARGER ON THE ORED BUS (l4e5_source_control.py, MESHSAT-1357). PROTOTYPE DESIGN:")
    P("nothing bought, built, powered or measured; no generator, registry, rendered page or HW-FW-CONTRACT.md in the tree edited.")
    P("Basis per figure: MAKER (document, page), NETLIST, MODELED (l4e_replay.py's functions), INFERRED (method stated),")
    P("ASSUMPTION; INCONCLUSIVE where no held document gives the figure.")
    P("")
    P("0. REPRODUCTIONS BEFORE ANY RESULT")
    P("   0a l4e4_limits.py re-run in a child process reproduces l4e4_limits.out byte for byte: %s" % ("yes" if R["r0a"] else "NO"))
    P("   0b r11_dep.py re-run in a child process reproduces r11_dep.out byte for byte: %s" % ("yes" if R["r0b"] else "NO"))
    P("   0c l4e4_limits.compute() run here renders l4e4_limits.out byte for byte: %s" % ("yes" if R["r0c"] else "NO"))
    P("   0d l4e_replay.main() run here (locals captured by l4e4_limits.run_main_captured) prints l4e_replay.out byte for byte: %s"
      % ("yes" if R["r0d"] else "NO"))
    P("   and its corrected A2 rows re-run by this script give the printed unserved figures: 100 W screening %.1f / %.1f Wh," % R["repro"]["screen"])
    P("   candidate panel %.1f / %.1f Wh (48 / 72 h, the worse start)" % R["repro"]["cand"])
    P("")
    P("1. WHAT THE BOARDS CARRY (NETLIST, read from the committed netlists)")
    for f in R["facts"]:
        P("   - %s" % f)
    P("   board A's VIN_RAW members: %s" % ", ".join(R["vin_raw_a"]))
    P("   board E's VIN_RAW members: %s" % ", ".join(R["vin_raw_e"]))
    P("   FW-A16 as written (HW-FW-CONTRACT.md): IIN_HOST at or below %.2f x %.2f A x %.2f x VIN_RAW / %.1f V = %.6f A/V x VIN_RAW;" % (
        R["k80"], R["i_ent"], R["eta"], R["vbus_max"], R["slope"]))
    P("   its own figures %.2f / %.2f / %.2f A at 9 / 12 / 24 V reproduced; O-33: about %.0f W against the tracker's %.0f W" % (R["printed"] + R["o33"]))
    P("   FW-E04 reports VIN_MON over USB every %.0f s; board E's USB goes to board B's bank 3, the panel controller (the charger's" % R["e04"])
    P("   only host, on the kit bus) is a USB device on bank 1 (FW-C12): VIN_RAW reaches the charger's host only through a running")
    P("   compute module's bridge. Board A has no reading of VIN_RAW at all.")
    P("   REQ-015 (l3r2.yaml): \"%s\"" % R["req015"])
    P("   the front end's restart guard U34 (gen_sch_a.py): UV falling %.2f / %.2f / %.2f V; a dip under 8 V interrupts charging for" % R["latch"])
    P("   %.1f to %.1f s; the vehicle entry's LM5069 limits at %.2f to %.2f A (%.2f A with R19's 1 %%); VIN_RAW's clamp %.1f V" % (
        R["restart"] + R["ent_lim"] + (R["clamp"],)))
    P("")
    P("2. WHY THE SOURCES CANNOT BE TOLD APART, AND HOW FAST THE BUS COLLAPSES")
    P("   - VIN_MON's value: REQ-015 admits every voltage from 9 to 36 V, the tracker's whole output range included (as drawn")
    P("     %.2f / %.2f / %.2f V: FBOUT %.3f / %.3f / %.3f V, MAKER 8705af p.4, every grade; R10 and R11 at %.0f %%): no voltage band is" % (
        R["v_trk"] + R["fbout"] + (100 * R["rtol"],)))
    P("     the tracker's alone (INFERRED).")
    P("   - DCIN_PGD: the LM5069 raises PGD when OUT is within 1.25 V of SENSE (MAKER SNVS452G p.3 and p.12, 8.3.6). Q7's source")
    P("     is on DC_HS and its drain on HS_S, so the tracker feeds DC_P back through Q7's body diode whenever it holds VIN_RAW over")
    P("     the 9 V UVLO; the LM5069 then starts with OUT above SENSE and PGD reads high with no vehicle connected (INFERRED from")
    P("     the netlist and the maker's PGD rule). The vehicle's own ideal diode U3 blocks the back-feed at DC_F (MAKER SNOSD17G")
    P("     p.12), so nothing on board E sees whether a vehicle is plugged in while the tracker holds the bus.")
    P("   - The LT8705A's SRVO_FBIN and SRVO_FBOUT (pins 25 and 28, open drain, pulled low while the input or output voltage loop")
    P("     is active; MAKER 8705af p.11 and p.19; SRVO_FBIN asserts %.0f / %.0f / %.0f mV above FBIN's regulation, p.4) would tell" % R["srvo_fbin"])
    P("     'the panel limits' from 'the tracker regulates'; both are unconnected (NETLIST).")
    P("   - The collapse: VIN_RAW and TRK_OUT hold %.0f uF nominal (NETLIST: %s)." % (
        R["c_bus"] * 1e6, ", ".join("%s %s %.0fu" % (c[0], c[1], c[3]) for c in R["caps"])))
    P("     From the tracker's %.2f V to the latch's highest %.2f V that is %.2f mJ, so a constant-power deficit empties it in" % (
        R["v_trk"][1], R["latch"][2], 1e3 * R["e_col"]))
    P("     %s (INFERRED: energy over deficit; nominal estimates pending evidence of the effective capacitance)." % ", ".join("%.1f ms at %.0f W" % (1e3 * t, dp) for dp, t in R["t_col"]))
    P("   - The vehicle entry: C5 100 nF on TIMER (NETLIST) with VTMRH %s V and 51 / 85 / 120 uA (MAKER SNVS452G p.6) gives a" % "3.76 / 4 / 4.16")
    P("     fault timeout of %.2f / %.2f / %.2f ms before Q7 turns off (INFERRED, C x V / I)." % tuple(1e3 * t for t in R["t_fault"]))
    P("   - FW-E04's %.0f s period is %.0f times the entry's shortest fault timeout: no firmware rule fed by VIN_MON can act inside a" % (
        R["e04"], R["t_fault_ratio"]))
    P("     source step. Steady state and transients are therefore separate acceptances, as A-2 asks.")
    P("")
    P("3. THE CANDIDATES' PER-SOURCE ENVELOPES (vehicle and shore at the entry's FW-A16 basis %.2f A, the front end at %.2f and" % (R["i_ent"], R["eta"]))
    P("   VBUS20 at its %.1f V maximum; U3's and the pin's maxima in board current with R16 at its low corner, L4-E4's rules;" % R["vbus_max"])
    P("   VBUS20's other loads %.6f A)" % R["loads4"])
    P("   VIN_RAW | FW-A16 line | (a) register, FE input | (b) register, FE input | H pin V | pin target lo/hi | H effective max | H FE input")
    for r in R["env"]:
        P("   %5.1f V | %6.3f A    | %4.2f A, %5.3f A (%5.1f %%) | %4.2f A, %5.3f A (%5.1f %%) | %5.3f V | %5.3f / %5.3f A | %5.3f A | %5.3f A (%5.1f %%)" % (
            r["v"], r["line"], r["reg_a"], r["fe_a"], 100 * r["fe_a"] / R["i_ent"], r["reg_b"], r["fe_b"], 100 * r["fe_b"] / R["i_ent"],
            r["pin_v"], r["pin_lo"], r["pin_hi"], r["board_h"], r["fe_h"], 100 * r["fe_h"] / R["i_ent"]))
    P("   (a)'s register passes L4-E4's %.2f A from %.1f V and reaches %.2f A at 36 V (U3's clamp %.2f A, MAKER SLUSE66A p.25)." % (
        R["setting"], R["cand_a"]["v_over"], R["cand_a"]["s"], R["host_clamp"]))
    P("   The hardware line (H): V(ILIM_HIZ) = %.0f V + %.0f x IDPM x RAC (MAKER SLUSE66A p.6), the lower of the pin and IIN_HOST" % (R["pin_off"], R["pin_gain"]))
    P("   governs (p.6, p.26 9.3.6), the pin read continuously (p.6). Its line: %.3f V + %.6f V/V x VIN_RAW at R16 %.0f mOhm." % (
        R["pin_off"], R["pin_gain"] * R["r16_nom"] * R["slope"], 1e3 * R["r16_nom"]))
    P("   The pin's accuracy is printed only for a 5 mOhm RAC: +-%.3f A at every row (%s; p.10); at R16's 10 mOhm" % (
        R["err5"], ", ".join("%.1f V %.1f/%.1f/%.1f A" % (v, lo / 1e3, ty / 1e3, hi / 1e3) for v, lo, ty, hi in R["ilim_rows"])))
    P("   INFERRED +-%.3f A (the same error at the pin); INCONCLUSIVE until measured. The network's own tolerance +-%.0f %% (ASSUMPTION)." % (
        R["err10"], 100 * T_NET))
    P("   H's highest front-end input current over 9 to 36 V: %.3f A at %.1f V, %.1f %% of %.2f A, under the entry's %.2f A minimum;" % (
        R["fe_h_max"], R["fe_h_max_v"], 100 * R["fe_h_max"] / R["i_ent"], R["i_ent"], R["ent_lim"][0]))
    P("   it reaches %.2f A only if the front end's efficiency at 9 V falls to %.3f (C-8: undocumented)." % (R["i_ent"], R["eta_at_basis"]))
    P("   The pin stays inside its range: %.3f V at 36 V, %.3f V at the clamp's %.1f V (recommended %.1f V, absolute %.0f V, p.8);" % (
        R["pin_v_36"], R["pin_v_clamp"], R["clamp"], R["pin_rmax"], R["pin_amax"]))
    P("   it disables itself above 4.0 V (p.80) only above %.1f V of VIN_RAW, outside service, where IIN_HOST still holds." % R["v_pin_disable"])
    P("   Solar under (a): the tracker's nominal %.2f V reads as %.2f A, %.1f W at %.1f V (O-33); under H1 the same line in" % (
        R["v_trk"][1], R["reg_a_trk"], R["o33_nom_w"], R["vbus_max"]))
    P("   hardware, %.3f A at the tracker's lowest ceiling. H2 raises the tracker's ceiling so the line's MINIMUM covers the window:" % (
        R["keys"]["H1"][1]))
    P("   the window's %.3f A at the lowest bus (l4e_replay.out 8, MODELED; L4-E4's need) needs the line at %.3f A, VIN_RAW %.2f V;" % (
        R["req"], R["lim_need"], R["v_need"]))
    P("   R10 at least %.0f k, so E96 %.0f k: ceiling %.2f / %.2f / %.2f V (INFERRED, the sheet's FBOUT rows, R10 and R11 at 1 %%)," % (
        (R["r10_min"] / 1e3, R["r10_new"] / 1e3) + tuple(R["v_trk2"])))
    P("   inside REQ-015's 36 V. TRK_OUT's parts at that ceiling's maximum: %s" % "; ".join(
        "%s %s at %.0f %% of its %.0f V" % (r, v.split(" (")[0], 100 * f, rt) for r, v, rt, f in R["trk_parts"]))
    P("   Low light under H1 and H2: the bus settles below the latch, and the front end restarts, when the power at VBUS20 is under")
    P("   %.1f W (nominal %.1f W); under H1 to H3 it settles below 12 V under %.1f W (nominal %.1f W) (INFERRED: the pin's band at %.2f V and 12 V)." % (
        R["thr"], R["thr_nom"], R["thr12"], R["thr12_nom"], R["latch"][2]))
    P("   H3 adds a knee under REQ-015's %.0f V floor: the pin falls from the line at %.2f V to 1 V (no current) at %.2f V (SESSION)" % (
        R["vk1"], R["vk1"], V_K0))
    K = R["knee"]
    P("   and on down. The pin's thresholds are TI's, the network's +-%.1f %% (ASSUMPTION) carried through each (nominal, low to high):" % (100 * T_KNEE))
    P("     zero-current target, the pin at 1.0 V (p.6's equation at IDPM 0): VIN_RAW %.3f V (%.3f to %.3f V)" % (K["zero"][1], K["zero"][0], K["zero"][2]))
    P("     HIZ entry, the pin falling to %.1f V (p.17 VHIZ_HIGH; p.6 'below 0.4 V'): VIN_RAW %.3f V (%.3f to %.3f V)" % (
        R["hiz"][0], K["entry"][1], K["entry"][0], K["entry"][2]))
    P("     HIZ exit, the pin rising to %.1f V (p.17 VHIZ_LO; p.6 'above 0.8 V'; p.27): VIN_RAW %.3f V (%.3f to %.3f V)" % (
        R["hiz"][1], K["exit"][1], K["exit"][0], K["exit"][2]))
    P("     the printed regulation range starting at %.2f V on the pin (p.10): VIN_RAW %.3f V (%.3f to %.3f V)" % (
        R["pin_rng"][0], K["rng"][1], K["rng"][0], K["rng"][2]))
    P("   So U3 is certainly in HIZ below %.3f V of VIN_RAW, %.3f V above the latch's highest, and out of HIZ (with EN_HIZ = 0," % (
        R["v_hiz_lo"], R["v_hiz_lo"] - R["latch"][2]))
    P("   REG0x35 bit 7, reset 0b, p.64; p.27) above %.3f V; between them the state depends on the sweep's direction and the" % R["v_unhiz_hi"])
    P("   comparator's unprinted spread. Out of HIZ is not proven conversion: TI specifies regulation by the pin only from %.2f V on" % R["pin_rng"][0])
    P("   the pin (p.10), VIN_RAW %.3f V at the band's top; from HIZ release to there the switching and the input current are" % R["knee"]["rng"][2])
    P("   recorded, not asserted (V-A09).")
    P("   The pin along the knee: %s." % ", ".join("%.3f V at %.3f V" % (vp, v) for v, vp in K["table"]))
    P("   At the %.0f V floor U3 still gets at least %.3f A (REQ-015's \"charges\"). TI's +-0.4 A row is the current loop's accuracy," % (
        R["vk1"], R["floor_min"]))
    P("   not the HIZ comparator's, so it is not carried into the HIZ thresholds.")
    P("   The knee's slope at the pin is %.3f V/V against the line's %.4f V/V: it needs a gain stage, not a divider (OWED)." % (
        R["s_k"], R["g_pin"] * R["slope"]))
    P("   H3's settle point on the solar hold (the stage at FBIN, the pin taking what the panel gives; VBUS20 nominal %.3f V," % R["v_nom"])
    P("   the extremes over the pin's band and VBUS20 %.3f to %.1f V):" % (R["v_min"], R["vbus_max"]))
    fv = lambda x: "HIZ cycling" if x is None else "%.2f V" % x
    for p, vn, lo, hi, i_ in R["settle"]:
        P("     %5.1f W at VBUS20: VIN_RAW %s nominal (%s to %s), U3 up to %.3f A" % (p, fv(vn), fv(lo), fv(hi), i_))
    P("   Under %.1f W at VBUS20 the pin's own error alone can ask more than the stage gives: U3 cycles in and out of HIZ" % R["thr_h3"])
    P("   above the latch (INFERRED), and the front end never restarts.")
    FL = R["flat"]
    P("   B3 of the check: a source-blind line held at H3's %.0f V target up to 12 V, then rising with H3's slope (the knee kept)." % R["vk1"])
    P("   For ANY source-blind line the solar power that settles the bus at 12 V is the charge power the line admits from a 12 V")
    P("   source (the same pin target at the same VIN_RAW; INFERRED). H3: %.3f W; the example: %.3f W. At 40 W the example's" % (FL["b12_h3"], FL["b12"]))
    P("   lowest settle is %.3f V against H3's %.3f V. Its price: at 12 V %.2f A (%.1f W at VBUS20 nominal) against H3's %.2f A (%.1f W)," % (
        FL["s40"], FL["s40_h3"], FL["at"][1][1], FL["p12"][0], FL["at"][1][2], FL["p12"][1]))
    P("   at 24 V %.2f A against %.2f A, against the profile's %.1f W at the pack terminals; and its window needs the tracker's ceiling" % (
        FL["at"][2][1], FL["at"][2][2], R["load0"]))
    P("   at %.2f V at the least (R10 %.0f k: %.2f / %.2f / %.2f V), the 35 V polymer then at %.0f %%. Its front end's highest input %.3f A." % (
        (FL["v_need"], FL["r10"] / 1e3) + tuple(FL["trk"]) + (100 * FL["c35"], FL["fe_max"])))
    off = R["offset"]
    P("   Rejected variant, an offset through zero at %.1f V (slope %.5f A/V bounded at 36 V): %s; the tracker would sit at %.1f V." % (
        off["v0"], off["k"], ", ".join("%.0f V %.2f A against %.2f A" % x for x in off["at"]), off["trk"]))
    P("")
    P("4. THE SOLAR ENERGY EACH GIVES UP AGAINST THE UNCAPPED TRACKER (MODELED: l4e_replay.py's run() and meanday(), architecture")
    P("   A2, the corrected path WE, the lowest bus %.3f V, U3 at its minimum; per hour, the charge path takes min(available, cap)," % R["v_min"])
    P("   upper bound, or its collapse bound; H1's and H2's lower bound takes nothing in an hour under %.1f W at VBUS20, H3's under" % R["thr"])
    P("   %.1f W, its HIZ cycling counted as nothing)" % R["thr_h3"])
    for k, (lab, iin, w) in R["keys"].items():
        P("   %-3s %-47s U3 minimum %.3f A, cap %.1f W at VBUS20" % (k, lab, iin, w))
    for tk, tl in (("screen", "the 100 W screening case (SC-37's mean September day, 400 Wp clipped to 100 W, TYP)"),
                   ("cand", "the candidate panel's trace (SPR-E-Flex-100, O-2 nominal, section 12 of l4e_replay.out)")):
        E = R["ER"][tk]
        P("   %s:" % tl)
        P("     %.1f Wh a day at VBUS20, peak %.1f W; hours under %.1f W %d (%.1f Wh), %.1f to %.1f W %d, at or above %d; under %.1f W %d (%.1f Wh)" % (
            E["avail"], E["peak"], R["thr"], E["n_below"], E["e_below"], R["thr"], R["thr12"], E["n_mid"], E["n_up"], R["thr_h3"], E["n_h3"], E["e_h3"]))
        P("     uncapped (WE): A2 unserved %.1f / %.1f Wh at 48 / 72 h" % tuple(E["ref_svc"]))
        for k in R["keys"]:
            up, lo = E[k]["up"], E[k]["lo"]
            P("     %-3s taken %6.1f to %6.1f Wh a day, given up %6.1f to %6.1f Wh; A2 unserved %.1f to %.1f Wh (48 h), %.1f to %.1f Wh (72 h)" % (
                k, lo[0], up[0], E["avail"] - up[0], E["avail"] - lo[0], up[1][0], lo[1][0], up[1][1], lo[1][1]))
    P("")
    P("5. THE DECISION (engineering, the session's; the reasons are on the page)")
    P("   H3: U3's input-current limit made a function of VIN_RAW in hardware, on its own ILIM_HIZ pin: FW-A16's line from REQ-015's")
    P("   %.0f V floor up, a knee into HIZ below it; the tracker's output ceiling raised (R10 %.0f k) so the line admits the window;" % (
        R["vk1"], R["r10_new"] / 1e3))
    P("   firmware holds IIN_HOST at L4-E4's %.2f A ceiling and no longer reads VIN_RAW for control." % R["setting"])
    P("")
    P("6. THE CHOSEN RULE'S CONTRACT VALUES")
    P("   values U3's IIN_HOST ever holds under H3: %s; highest %.2f A (code %d, 0x%04X)" % (
        "; ".join("%s %.2f A" % kv for kv in R["writes"].items()), R["max_written"], R["code"], R["word"]))
    P("   the pin's line crosses IIN_HOST at %.2f V; between %.2f and %.2f V the pin governs and its maximum passes U3's own %.3f A" % (
        R["v_cross"], R["band_x"][0], R["band_x"][1], R["u3max_host"]))
    for k, (r5, b) in R["por"].items():
        P("   POR, IIN_HOST %s: %.2f A in the 5 mOhm table's terms (Table 9-50, pp.80 and 81; its reset bits read 0x%02X), %.3f A of" % (
            k, r5, R["por_table_code"], b))
        P("   board current at RSNS_RAC = 1b over R16 (INFERRED); recorded raw by V-A09, kept apart from the removal reset")
    P("   stale or missing VIN_MON (older than %.0f s): no setting changes; the line is hardware. Diagnostic only: a fresh VIN_MON" % FRESH_S)
    P("   with the charger's input reading over the pin's band by %.1f A in three readings falls back to FW-A16's old rule." % DIAG_A)
    D = R["diag"]
    P("   V-A10's values: the trip at 12 V %.3f A of board current; with the pin lifted above 4.0 V U3 can reach %.3f A, over it;" % (
        D["trip12"], D["pin_off_board"]))
    P("   the fallback's registers %s; stale %.2f A; the highest %.2f A, at or under %.2f A" % (
        ", ".join("%.0f V %.2f A" % kv for kv in D["fallback"].items()), D["stale"], D["max_fallback"], R["setting"]))
    P("")
    P("7. THE CONSEQUENCE FOR L4-E4 (its own functions, from compute() above)")
    L = R["l4e4"]
    P("   L4-E4's setting %.2f A, U3's maximum %.3f A, through R11 %.3f A; R11 %.0f mOhm, C-1 %.4f mOhm at 25 C. Its margins:" % (
        L["setting"], L["u3max"], L["serv"], 1e3 * L["r11"], 1e3 * L["tap25"]))
    for t, m1, m2, m3_ in L["per_t"]:
        P("     %6.1f C: R11 alone %+.3f A, kelvin_check's 1 %% taps %+.3f A, C-1's full taps %+.3f A" % (t, m1, m2, m3_))
    X = R["cross"]
    P("   H3 writes nothing above %.2f A, so every register path holds. The pin path just under the crossover: at most %.3f A in" % (
        R["max_written"], X["board"]))
    P("   board current, %.3f A through R11 (INFERRED with the pin's +-%.3f A and the network's %.0f %%):" % (X["serv"], R["err10"], 100 * T_NET))
    for t, m1, m2, m3_ in X["per_t"]:
        P("     %6.1f C: R11 alone %+.3f A, kelvin_check's 1 %% taps %+.3f A, C-1's full taps %+.3f A" % (t, m1, m2, m3_))
    P("   R11 alone %s, with kelvin_check's taps %s, with C-1's full 0.38 mOhm %s. L4-E4's tap rule at %.3f A gives %.4f mOhm at 25 C" % (
        "holds" if X["ok_alone"] else "FAILS", "holds" if X["ok_kel"] else "FAILS", "holds" if X["ok_full"] else "FAILS", X["serv"], 1e3 * X["tap"][2]))
    P("   (C-1's accepted criterion %.4f mOhm: %s)." % (1e3 * L["c1_prior"], "met, so 8 mOhm still qualifies" if X["tap_ok"] else "NOT met"))
    P("   What would change: nothing, if the pin's error at 10 mOhm is at most %.3f A in that band (bench V-A07); otherwise, by" % X["err_allow"])
    if X["r11_ok"]:
        P("   L4-E4's own rule, R11 %.1f mOhm (%s): C-1 %.4f mOhm at 25 C, its highest permitted current %.3f A against 8 mOhm's %.3f A," % (
            1e3 * X["r11_ok"][0], X["r11_ok"][1], 1e3 * X["r11_ok"][3], X["r11_ok"][2], X["hi_now"]))
        P("   carried to item 4 (fault handling).")
    else:
        P("   no catalogue R11 in L4-E4's family coordinates the pin path.")
    ca = R["cand_a"]
    P("   For comparison, (a) as written: %.2f A at 36 V, %.3f A through R11, worst margin %+.3f A with R11 alone; %s" % (
        ca["s"], ca["serv"], ca["worst"], ("the largest catalogue R11 that would coordinate: %.1f mOhm" % (1e3 * ca["r11_ok"]["r"])) if ca["r11_ok"]
        else "no catalogue R11 in L4-E4's family coordinates"))
    P("")
    P("END. Desk arithmetic; nothing is measured. The hardware line and the raised ceiling are not drawn (OWED); the transient")
    P("behaviour of every candidate is INCONCLUSIVE until the bench rows of L4E5-SOURCE-CONTROL.md are run.")
    return o


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
