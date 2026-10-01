#!/usr/bin/env python3
"""l4e6_fault_handling.py: layer 4 task L4-E6 (MESHSAT-1357, 1 October 2026). Implementable choice 4, FAULT HANDLING, of
v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md (findings B-1, B-2 and B-4): how board A's front end U2 (LM5176, SNVSAI1D)
survives the highest current its average-current limit permits, at both outcomes of R11 that L4-E4 and L4-E5 leave open
(8 mOhm, highest permitted current 7.262 A; 7 mOhm, 8.300 A, if bench V-A07 fails).

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry, rendered page or
record of L4-E4 or L4-E5 is edited (the draft apply scripts beside this file are for board A's generator owner). Every
figure carries its basis: MAKER (document, revision, page), NETLIST (board A's committed netlist), MODELED, INFERRED (method
stated) or ASSUMPTION (a figure no document gives); INCONCLUSIVE where no held document gives a figure.

Section 0 proves, before any result (exit 4 otherwise):
  0a l4e4_limits.py, 0b l4e5_source_control.py and 0c r11_dep.py, each re-run in a child process, reproduce their committed
     outputs byte for byte;
  0d l4e4_limits.compute(), run here, renders l4e4_limits.out byte for byte, so L4-E4's band(), its chosen R11 and its 7 mOhm
     alternative are the ones that printed the record;
  0e r11_dep.main(), run here with its locals captured by l4e4_limits.run_main_captured(), prints r11_dep.out byte for byte,
     so the stage relations, peak_b(), fet_tj(), Figure 8's readings and the VBUS20 bank's per-can scaling used below are the
     ones that printed that record. r11_dep.py's FET loss relations (lambdas inside its loop, not kept at return) are
     restated here once and checked to reprint all nine of its section 4 FET lines byte for byte.
L4-E5's figures (the pin path's 5.095 A, V-A07's 0.071 A, H3's 9 V and 12 V maxima) are read from its reproduced output, as
l4e4_limits.py reads r11_dep.out's C-1 criterion: its compute() would re-run the energy replay for figures already printed.

Run from the repository root:  python3 v2/docs/records/l4e6/l4e6_fault_handling.py > v2/docs/records/l4e6/l4e6_fault_handling.out
Needs pdftotext, pdftoppm, PyYAML and Pillow (through the imported records). About four minutes, most of it 0b.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction or a predicate failed."""
import hashlib
import importlib.util
import json
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
L4E5_PY = "v2/docs/records/l4e5/l4e5_source_control.py"
L4E5_OUT = "v2/docs/records/l4e5/l4e5_source_control.out"
R11_PY = "v2/docs/records/r11dep/r11_dep.py"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
XAL1510 = "v2/vendor/power/coilcraft-xal1510.pdf"
PINS = {
    L4E4_PY: "d4a484439a7b53030423b596769bf748469134a45a46b3c91724e2b80d9e2a42",
    L4E4_OUT: "f68bf6951a6361caf6c41db14d86d735f9e3e9736723984ef61234aa10a80694",
    R11_PY: "c5e9d5713abfcb07a15276c489ce9774a20bff029b11d205a9e9877a21ed2684",
    R11_OUT: "f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209",
    "v2/vendor/ti/lm5176-datasheet.pdf": None,          # filled from the tree below and printed; the reproduced records pin
    "v2/vendor/power/coilcraft-xal1010.pdf": "c79a8bd74ae55bc8ca60d251b926c15fdb66f02d8dd1f249846fdd4505158990",
    XAL1510: "ccbf7fa97649e098de283ce9c9505201b149443fa34ed771b1e71aa6a8987892",
}
# The few figures this record sets itself (each named where it is used):
C123_TOL = 0.10      # ASSUMPTION: C123's tolerance (the netlist prints "1n" only), carried at its high end into the CS lag
R_TOL_0603 = 0.01    # ASSUMPTION: a 93.1 kOhm MODE resistor at 1 % (for candidate (a) only; the netlist has no such part yet)
VIN_GRID = [round(9.0 + 0.1 * i, 1) for i in range(271)]     # 9.0 to 36.0 V, REQ-015's service range, for the B-1 envelope
CLOSE_VINS = (9.0, 15.1, 36.0)                               # the closure's three voltages (architecture page, B-2)


def refuse(code, msg):
    sys.stderr.write("l4e6_fault_handling: %s; refusing\n" % msg)
    sys.exit(code)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def compute():
    PINS["v2/vendor/ti/lm5176-datasheet.pdf"] = PINS.get("v2/vendor/ti/lm5176-datasheet.pdf") or sha("v2/vendor/ti/lm5176-datasheet.pdf")
    for rel, want in PINS.items():
        if sha(rel) != want:
            refuse(2, "%s is not the pinned file" % rel)
    R = {"lm5176_sha": PINS["v2/vendor/ti/lm5176-datasheet.pdf"]}
    # ================================================================== 0: the reproductions
    outs = {rel: open(os.path.join(TOP, rel), "rb").read() for rel in (L4E4_OUT, L4E5_OUT, R11_OUT)}
    R["out_sha"] = {rel: hashlib.sha256(b).hexdigest() for rel, b in outs.items()}
    for key, py, out in (("r0a", L4E4_PY, L4E4_OUT), ("r0b", L4E5_PY, L4E5_OUT), ("r0c", R11_PY, R11_OUT)):
        ch = subprocess.run([sys.executable, "-B", os.path.join(TOP, py)], cwd=TOP, capture_output=True)
        R[key] = ch.returncode == 0 and ch.stdout == outs[out]
        if not R[key]:
            refuse(4, "%s's child re-run does not reproduce %s (exit %d)" % (py, out, ch.returncode))
    L4 = load("l4e4_limits_for_l4e6", L4E4_PY)
    R4 = L4.compute()
    R["r0d"] = ("\n".join(L4.render(R4)) + "\n").encode("utf-8") == outs[L4E4_OUT]
    M = L4.load_r11dep()
    rc, t11, L = L4.run_main_captured(M)
    R["r0e"] = rc == 0 and t11.encode("utf-8") == outs[R11_OUT]
    if not (R["r0d"] and R["r0e"]):
        refuse(4, "an in-process run does not print its record (l4e4 %s, r11_dep %s)" % (R["r0d"], R["r0e"]))
    t45 = outs[L4E5_OUT].decode("utf-8")
    page = M.page

    # r11_dep.py's own relations and figures, taken from its run (not retyped)
    stage, peak_b, fet_tj, k_at = L["stage"], L["peak_b"], L["fet_tj"], L["k_at"]
    VB, ETA, fsw, l_nom = L["v_bus_max"], M.ETA_FE, L["fsw"], L["l_nom"]
    rds, rtja, qoss, t_sw, t_air = L["rds6_max"], L["rtja"], L["qoss"], L["t_sw"], L["t_air"]
    isat, irms40, vcs_boost, vcs_buck = L["isat"], L["irms40"], L["vcs_boost"], L["vcs_buck"]
    can_k, rip_bulk, loads4, k_r = L["can_k"], L["ripple_bulk"], L["loads4"], L["k_r11"]
    ca, pa = L["ca"], L["pa"]
    tol, tcr, dt_env = R4["tol"], R4["tcr"], R4["dt_env"]
    band = R4["fn"]["band"]

    def fet_q(s):
        """r11_dep.py section 4's FET loss relations (RDS(on) max x Figure 8 at TJ; Q4's and the buck switch's transition
        and Qoss terms at fSW max), restated once and checked below to reprint its nine FET lines."""
        d = s["d"]
        if s["mode"] == "boost":
            return {"Q2 (on)": (lambda k: s["rms"] ** 2 * rds * k),
                    "Q4 (boost switch)": (lambda k: s["rms"] ** 2 * d * rds * k + 0.5 * VB * s["i_l"] * t_sw * fsw[2] + 0.5 * qoss * VB * fsw[2]),
                    "Q5 (rectifier)": (lambda k: s["rms"] ** 2 * (1 - d) * rds * k)}
        return {"Q2 (buck switch)": (lambda k: s["rms"] ** 2 * d * rds * k + 0.5 * s["vin"] * s["i_l"] * t_sw * fsw[2] + 0.5 * qoss * s["vin"] * fsw[2]),
                "Q3 (rectifier)": (lambda k: s["rms"] ** 2 * (1 - d) * rds * k),
                "Q5 (on)": (lambda k: s["rms"] ** 2 * rds * k)}

    def fets(s):
        out = []
        for name, f in fet_q(s).items():
            tj, p150 = fet_tj(f)
            out.append(dict(name=name, tj=tj, p=(f(k_at(tj)) if tj is not None else p150), p150=p150, need_rth=(150.0 - t_air) / p150))
        return out

    def fet_line(fs):
        parts = []
        for x in fs:
            if x["tj"] is None:
                parts.append("%s past 150 C (%.2f W at 150 C; needs RthetaJA <= %.0f C/W)" % (x["name"], x["p150"], x["need_rth"]))
            else:
                parts.append("%s %.2f W, TJ %.0f C" % (x["name"], x["p"], x["tj"]))
        return "; ".join(parts)
    fet_lines = [l for l in t11.splitlines() if l.startswith("       FETs (RDS(on) max x Figure 8 at TJ")]
    mine = []
    for lab, _i in L["cases"]:
        for vin in (M.VIN_TRACKER, M.VIN_TREE, M.VIN_MAX):
            mine.append("       FETs (RDS(on) max x Figure 8 at TJ, the maker's RthetaJA %.0f C/W on its 1 in2 pad, not board A's): %s" % (
                rtja, fet_line(fets(L["res"][(lab, vin)]))))
    R["r0f"] = mine == fet_lines and len(fet_lines) == 9
    if not R["r0f"]:
        refuse(4, "the restated FET relations do not reprint r11_dep.out's nine FET lines")

    # ================================================================== 1: the netlist and the makers' rows
    def nets(ref):
        return {p: v["net"] for p, v in pa[ref].items()}
    facts = [
        ("R12 '%s' from FE_CS to GND, U2's cycle-by-cycle sense (lcsc_fill.py C500739, LR2512D-3W-5mR-1%%)" % ca["R12"]["value"],
         ca["R12"]["value"].startswith("5mOhm 1% 2512 (CS)") and nets("R12") == {"1": "FE_CS", "2": "GND"}),
        ("Q3 and Q4 sources (pins 1 to 3) on FE_CS: R12 carries the low-side switches' current",
         all(nets(q)[p] == "FE_CS" for q in ("Q3", "Q4") for p in ("1", "2", "3"))),
        ("the CS filter R150, R151 '100R 1%%' into U2 pins 16 and 15, C123 '%s' across" % ca["C123"]["value"],
         ca["R150"]["value"].startswith("100R 1%") and ca["R151"]["value"].startswith("100R 1%") and nets("C123") == {"1": "FE_CSF", "2": "FE_CSGF"}
         and nets("U2")["16"] == "FE_CSF" and nets("U2")["15"] == "FE_CSGF"),
        ("R119 '%s' from FE_MODE (U2 pin 4) to FE_VCC (pin 23): MODE to VCC" % ca["R119"]["value"],
         nets("R119") == {"1": "FE_MODE", "2": "FE_VCC"} and nets("U2")["4"] == "FE_MODE" and nets("U2")["23"] == "FE_VCC"),
        ("C147 '%s' on FE_SLOPE (the slope capacitor)" % ca["C147"]["value"], ca["C147"]["value"] == "680p" and nets("C147")["1"] == "FE_SLOPE"),
        ("C7 '%s' on FE_SS (the soft start)" % ca["C7"]["value"], ca["C7"]["value"] == "4.7u" and nets("C7")["1"] == "FE_SS"),
        ("L1 '%s'" % ca["L1"]["value"], "XAL1010-103ME" in ca["L1"]["value"]),
        ("U2 is the HTSSOP-28 (LM5176PWPR): the HTSSOP current-limit rows apply", "LM5176PWPR" in ca["U2"]["value"] and "HTSSOP" in ca["U2"]["footprint"]),
    ]
    if not all(ok for _f, ok in facts):
        refuse(3, "a netlist fact does not hold: %s" % [f for f, ok in facts if not ok])
    R["facts"] = [f for f, _ in facts]
    r150 = float(need(ca["R150"]["value"], r"^(\d+)R", "R150's value").group(1)) * 2.0
    c123 = float(need(ca["C123"]["value"], r"^(\d+)n$", "C123's value").group(1)) * 1e-9
    c7 = float(need(ca["C7"]["value"], r"^([\d.]+)u$", "C7's value").group(1)) * 1e-6
    tau_cs = r150 * (1 + 0.01) * c123 * (1 + C123_TOL)       # INFERRED: the differential RC lag of the CS filter
    # the LM5176's rows (MAKER SNVSAI1D, the pages named)
    p3, p5, p6, p7, p13, p16, p17, p20, p24 = (page(M.LM5176, n) for n in (3, 5, 6, 7, 13, 16, 17, 20, 24))
    need(p6 + p7, r"SNVSAI1D", "SNVSAI1D on pp.6 and 7")
    need(page(M.LM5176, 1), r"SNVSAI1D . JUNE 2017 . REVISED AUGUST 2021", "SNVSAI1D's revision on p.1")
    mode_hic = need(p3, r"([\d.]+) V < MODE < ([\d.]+) V: CCM, hiccup enabled \(set RMODE resistor to AGND = ([\d.]+) k", "p.3 MODE hiccup band")
    mode_no = need(p3, r"([\d.]+) V < MODE < VCC: CCM, hiccup disabled", "p.3 MODE no-hiccup band")
    need(p20, r"MODE to VCC", "p.20 MODE to VCC")
    need(p20, r"RMODE to AGND = 93\.1 k\S+\s+Hiccup Enabled", "p.20 93.1 kOhm hiccup enabled")
    need(p20, r"MODE is latched during start-up", "p.20 MODE latched at start-up")
    m17 = need(" ".join(p17.split()), r"In hiccup mode, the controller shuts down after detecting cycle-by-cycle current limiting for (\d+) consecutive cycles"
                                       r" and the soft-start capacitor is discharged\. The soft-start capacitor is automatically released after (\d+) oscillator clock cycles",
               "p.17 the hiccup counts")
    n_trip, n_off = int(m17.group(1)), int(m17.group(2))
    need(" ".join(p17.split()), r"If the drop across the sense resistor is greater than 50 mV, the gm amplifier gradually discharges the soft-start capacitor",
         "p.17 7.3.6 the average limit acts through SS")
    need(" ".join(p16.split()), r"the soft-start capacitor is discharged by the constant current loop transconductance \(gm\) amplifier to limit either input or output current",
         "p.16 7.3.4 the average limit discharges SS")
    need(" ".join(p16.split()), r"If the peak current in the low-side boost switch causes the voltage across CS and CSG to exceed this threshold voltage, the boost switch is turned off for the remainder of the clock cycle",
         "p.16 7.3.5 the boost peak limit")
    need(" ".join(p16.split()), r"The high-side buck switch skips a cycle if the sensed voltage does not fall below this threshold during the buck switch off time",
         "p.16 7.3.5 the buck valley limit")
    need(" ".join(p13.split()), r"The inductor current is sensed through a single sense resistor in series with the low-side MOSFETs\. The sensed current is also monitored for cycle-by-cycle current limit",
         "p.13 the single sense resistor")
    need(" ".join(p13.split()), r"If hiccup mode is disabled through the MODE pin, the controller remains in a cycle-by-cycle current limit condition until the overload is removed",
         "p.13 no hiccup: stays in the cycle-by-cycle limit")
    cs_abs = float(need(p5, r"^\s*CS, CSG\s+\S+\s+([\d.]+)\s+V", "p.5 CS, CSG absolute maximum").group(1))
    iss = tuple(float(x) * 1e-6 for x in need(p6, r"ISS\s+Soft-start pullup current\s+VSS = 0 V\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "p.6 ISS").groups())
    vref = tuple(float(x) for x in need(p6, r"VREF\s+Feedback reference voltage\s+FB = COMP\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "p.6 VREF").groups())
    imode = tuple(float(x) * 1e-6 for x in need(p7, r"IMODE\s+Source current out of MODE pin\s+(\d+)\s+(\d+)\s+(\d+)", "p.7 IMODE").groups())
    v_hic = tuple(float(x) for x in need(p7, r"VCCM_HIC\s+CCM with hiccup threshold\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "p.7 VCCM_HIC").groups())
    v_ccm = tuple(float(x) for x in need(p7, r"VCCM\s+CCM no hiccup threshold\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "p.7 VCCM").groups())
    gm_slope = float(need(p7, r"gmSLOPE\s+Slope compensation amplifier gm\s+([\d.]+)\s+\S+S", "p.7 gmSLOPE").group(1)) * 1e-6
    lines7 = p7.splitlines()
    hdr = [l for l in lines7 if "MIN" in l and "TYP" in l and "MAX" in l][0]
    off_l = [l for l in lines7 if l.lstrip().startswith("IOFFSET(CS/CSG)")][0]
    m_off = re.search(r"(\d+)\s*$", off_l)
    if not m_off or m_off.end() < hdr.index("MAX"):
        refuse(3, "p.7 IOFFSET(CS/CSG) is not in the MAX column")
    i_off = float(m_off.group(1)) * 1e-6
    cs_off = i_off * r150 / 2.0          # INFERRED: the CSG pin's offset current over its own 100 Ohm filter resistor
    m24 = need(p24, r"(\d+)\s+m\S\s+u\s+(\d+)\s+\(26\)", "p.24 Equation 26's example RSENSE and ACS")
    acs = float(m24.group(2))
    need(p24, r"RSENSE\(BOOST\)", "p.24 Equation 24")
    need(p24, r"RSENSE\(BUCK\)", "p.24 Equation 23")
    need(" ".join(p24.split()), r"The current sense resistor between the CS and CSG pins should be selected to ensure that current limit is set high enough for both buck and boost modes of operation",
         "p.24 8.2.2.7")
    need(" ".join(p24.split()), r"Theoretically, a current mode loop is stable with half the .dead-beat. slope", "p.24 8.2.2.8 half the dead-beat slope")
    if abs(gm_slope * l_nom / (M.R12_CS * acs) - L["c_slope"]) > 1e-15:
        refuse(4, "Equation 26 as read does not give r11_dep.py's 800 pF at 5 mOhm")
    # Coilcraft
    x1 = page(M.XAL1010, 1)
    l_tol = float(need(x1, r"±(\d+)%", "XAL1010 inductance tolerance").group(1)) / 100.0
    need(x1, r"5\. DC current at 25°C that causes an inductance drop of 30% \(typ\) from", "XAL1010 note 5: Isat at 25 C")
    need(x1, r"Click for temperature derating information", "XAL1010 the derating as a link")
    need(x1, r"Document 804-1\s+Revised 02/25/26", "XAL1010 Document 804-1 revision")
    xr = page(M.XAL1010, 3)
    need(xr, r"Typical L vs Current", "XAL1010 p.3 typical L vs current")
    derating_held = bool(re.search(r"(?i)isat.{0,40}(?:vs|versus).{0,10}temperature|derating curve", page(M.XAL1010, 1) + xr + page(M.XAL1010, 2)))
    y1 = page(XAL1510, 1)
    my = need(y1, r"XAL1510-103ME_\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(\d+)", "XAL1510 p.1 the 103ME row")
    xal15 = dict(l=float(my.group(1)), dcr_max=float(my.group(3)), isat=float(my.group(5)), irms20=float(my.group(6)), irms40=float(my.group(7)))
    need(y1, r"Document 947-1\s+Revised 05/04/26", "XAL1510 Document 947-1 revision")
    dims10 = tuple(float(x.replace(",", ".")) for x in re.findall(r"(\d+,\d) ±0,50", page(M.XAL1010, 4))[:2])
    dims15 = tuple(float(x.replace(",", ".")) for x in re.findall(r"(\d+,\d) ±0,2\b", page(XAL1510, 3))[:2])
    if len(dims10) != 2 or len(dims15) != 2:
        refuse(3, "the two inductors' outline dimensions not read (XAL1010 p.4, XAL1510 p.3)")
    vds18510 = float(need(page(L4.CSD18510, 1), r"VDS\s+Drain-to-Source Voltage\s+(\d+)\s+V", "SLPS632 p.1 VDS").group(1))
    R.update(n_trip=n_trip, n_off=n_off, mode_hic=(float(mode_hic.group(1)), float(mode_hic.group(2)), float(mode_hic.group(3))),
             mode_no=float(mode_no.group(1)), iss=iss, vref=vref, imode=imode, v_hic=v_hic, v_ccm=v_ccm, gm_slope=gm_slope, acs=acs,
             i_off=i_off, cs_off=cs_off, cs_abs=cs_abs, tau_cs=tau_cs, c7=c7, l_tol=l_tol, derating_held=derating_held, xal15=xal15,
             dims10=dims10, dims15=dims15, vds18510=vds18510, isat=isat, irms40=irms40, vcs_boost=vcs_boost, vcs_buck=vcs_buck, fsw=fsw, rtja=rtja, t_air=t_air, VB=VB, eta=ETA,
             r12_drawn=M.R12_CS, c_slope_drawn=L["c_slope"], rip_bulk=rip_bulk, can_k=can_k)

    # L4-E4 and L4-E5's figures (their own functions, or read from their reproduced outputs)
    out_r11 = {"8": R4["r11"], "7": R4["alt"]["r"]}
    R["outcomes"] = []
    for key, code in (("8", R4["r11_pick"]["code"]), ("7", R4["alt"]["code"])):
        r = out_r11[key]
        R["outcomes"].append(dict(key=key, r11=r, code=code, band=band(r), hi=band(r)[2]))
    if abs(R["outcomes"][0]["hi"] - R4["hi_env"]) > 1e-12:
        refuse(4, "L4-E4's highest permitted current is not its band's maximum")
    pin = need(t45, r"at most ([\d.]+) A in\s+board current, ([\d.]+) A through R11 \(INFERRED with the pin's", "L4-E5 the pin path")
    va07 = float(need(t45, r"if the pin's error at 10 mOhm is at most ([\d.]+) A in that band \(bench V-A07\)", "L4-E5 V-A07's threshold").group(1))
    band45 = tuple(float(x) for x in need(t45, r"between ([\d.]+) and ([\d.]+) V the pin governs", "L4-E5 the crossover band").groups())
    alt45 = need(t45, r"R11 ([\d.]+) mOhm \((C\d+)\): C-1 [\d.]+ mOhm at 25 C, its highest permitted current ([\d.]+) A", "L4-E5 the 7 mOhm consequence")
    h3 = {float(v): float(m) for v, m in re.findall(r"^\s+([\d.]+) V \|.*\| ([\d.]+) A \| [\d.]+ A \(\s*[\d.]+ %\)\s*$", t45, re.M)}
    if sorted(h3) != [9.0, 12.0, 24.0, 36.0]:
        refuse(3, "L4-E5's H3 envelope rows not parsed: %s" % sorted(h3))
    veh = float(need(t11, r"the vehicle entry passes at most its LM5069's ([\d.]+) A", "r11_dep.out the entry's 6.15 A").group(1))
    R["clamp"] = float(need(t45, r"at the clamp's ([\d.]+) V", "L4-E5 the input clamp").group(1))
    if not (abs(float(alt45.group(1)) * 1e-3 - out_r11["7"]) < 1e-12 and alt45.group(2) == R4["alt"]["code"]
            and abs(float(alt45.group(3)) - round(R["outcomes"][1]["hi"], 3)) < 1e-9):
        refuse(4, "L4-E5's 7 mOhm consequence is not L4-E4's alternative")
    R.update(pin_board=float(pin.group(1)), pin_r11=float(pin.group(2)), va07=va07, band45=band45, h3=h3, veh=veh,
             serv44=R4["serv"], setting=R4["setting"])

    # ================================================================== 2: the relations used for every candidate
    l_low = l_nom * (1 - l_tol) * 0.7         # r11_dep.py's note 5: Isat's 30 % drop on top of the -20 % tolerance

    def rip_min(vin):
        """the inductor ripple at the opposite corners of stage()'s: L at +20 %, fSW at its maximum (INFERRED)."""
        return stage(1.0, vin)["ripple"] * (1 - l_tol) / (1 + l_tol) * fsw[0] / fsw[2]

    def lag(vin):
        """the CS filter's lag on the boost on-time ramp, VIN over L at its lowest times the RC (INFERRED)."""
        return vin / l_low * tau_cs

    def cbc(r):
        """U2's cycle-by-cycle limits in amperes of inductor current for a CS resistor r of the HoJLR2512 series (+-1 %,
        50 ppm/K over r11_dep.py's 75 K envelope), the CSG offset added against the limit at each end."""
        k_hi = r * (1 + tol) * (1 + tcr * dt_env)
        k_lo = r * (1 - tol) * (1 - tcr * dt_env)
        return dict(r=r, boost=((vcs_boost[0] - cs_off) / k_hi, vcs_boost[1] / r, (vcs_boost[2] + cs_off) / k_lo),
                    buck=((vcs_buck[0] - cs_off) / k_hi, vcs_buck[1] / r, (vcs_buck[2] + cs_off) / k_lo))

    def regime(hi, vin, lim):
        """The worst continuous fault at VIN with the average limit at hi and the cycle-by-cycle limits lim (None: no
        cycle-by-cycle bound counted). Boost: the inductor average is the lower of the average limit's and the one under
        the peak limit's maximum (its lag in, the ripple at its smallest), with no hiccup credit. Buck: the average limit."""
        s_lim = stage(hi, vin)
        if s_lim["mode"] == "boost" and lim is not None:
            i_cap = lim["boost"][2] + lag(vin) - rip_min(vin) / 2.0
            i_l = min(s_lim["i_l"], i_cap)
            s = stage(i_l * vin * ETA / VB, vin)
            pk = min(peak_b(hi, vin), lim["boost"][2] + lag(vin))
            who = "the cycle-by-cycle limit" if i_cap < s_lim["i_l"] else "the average limit"
        else:
            s, pk, who = s_lim, peak_b(hi, vin), "the average limit"
        rise = 40.0 * (s["rms"] / irms40) ** 2
        return dict(vin=vin, s=s, s_lim=s_lim, peak=pk, who=who, fets=fets(s), i_out=s["i_out"], l1_temp=t_air + rise)

    def b1_env(hi, lim):
        worst = max(VIN_GRID, key=lambda v: regime(hi, v, lim)["peak"])
        return worst, regime(hi, worst, lim)["peak"]

    # ================================================================== 3: candidate (a), hiccup alone (R12 as drawn)
    drawn = cbc(M.R12_CS)     # stacked as the HoJLR2512 series (the drawn LR2512D's own TCR is not held: an ASSUMPTION)
    R["drawn"] = drawn
    for o in R["outcomes"]:
        a = {}
        for vin in CLOSE_VINS:
            g = regime(o["hi"], vin, drawn)
            pk_act = g["s_lim"]["peak"]           # the average limit's own peak, L at -20 % (what the comparator would see)
            if g["s_lim"]["mode"] == "buck":
                hic = "the average limit governs (buck); the valley limit is not reached"
            elif pk_act < drawn["boost"][0]:
                hic = "never: the average limit's peak stays under the peak limit's minimum"
            elif pk_act < drawn["boost"][2]:
                hic = "not guaranteed: between the peak limit's minimum and maximum"
            else:
                hic = "guaranteed"
            a[vin] = dict(g=g, pk_act=pk_act, hic=hic)
        o["a"] = a
        o["a_b1"] = max(a[v]["g"]["peak"] for v in CLOSE_VINS)
        o["a_b2"] = all(f["tj"] is not None for v in CLOSE_VINS for f in a[v]["g"]["fets"])
    R["hiccup_t"] = dict(trip=(n_trip / fsw[2], n_trip / fsw[0]), off=(n_off / fsw[2], n_off / fsw[0]),
                         ss=(c7 * vref[0] / iss[2], c7 * vref[2] / iss[0]))
    R["mode931"] = (imode[0] * 93.1e3 * (1 - R_TOL_0603), imode[2] * 93.1e3 * (1 + R_TOL_0603))

    # ================================================================== 4: candidate (b), rate L1, the FETs and the bank
    for o in R["outcomes"]:
        g9 = o["a"][9.0]["g"]
        o["b_l1_ratio"] = o["a_b1"] / xal15["isat"]
        o["b_need_rth"] = min(f["need_rth"] for f in g9["fets"])

    # ================================================================== 5: the chosen bound, R12 from the held catalogue
    cat = json.load(open(os.path.join(TOP, L4.JLC_SEARCH), encoding="utf-8"))
    svc9 = stage(h3[9.0] + loads4, 9.0)                       # H3's highest 9 V board current plus C-9's loads
    svc12 = stage(h3[12.0] + loads4, 12.0)
    svc_boost_pk = max(svc9["peak"], svc12["peak"])
    svc_boost_pkb = max(peak_b(h3[9.0] + loads4, 9.0), peak_b(h3[12.0] + loads4, 12.0))
    v_lo45 = band45[0]
    svc_valley = R["pin_r11"] - rip_min(v_lo45) / 2.0        # the pin path's valley at the band's low end, ripple smallest
    veh_pk = veh + stage(1.0, 9.0)["ripple"] / 2.0            # the entry's most, all through L1 at 9 V
    rows = []
    for row in cat["rows"]:
        mm = re.fullmatch(r"HoJLR2512-3W-([\d.]+)mR-1%", row["model"])
        if not (mm and row["stock"] and 5.0 <= float(mm.group(1)) <= 20.0):
            continue
        r = float(mm.group(1)) * 1e-3
        lim = cbc(r)
        res = {}
        for o in R["outcomes"]:
            gs = {v: regime(o["hi"], v, lim) for v in CLOSE_VINS}
            wv, wpk = b1_env(o["hi"], lim)
            res[o["key"]] = dict(gs=gs, b1=wpk, b1_v=wv, b2=all(f["tj"] is not None for g in gs.values() for f in g["fets"]))
        ok_b1 = all(x["b1"] <= 0.9 * isat for x in res.values())
        ok_b2 = all(x["b2"] for x in res.values())
        m_boost = lim["boost"][0] - svc_boost_pk
        m_buck = lim["buck"][0] - svc_valley
        cs_v = r * (1 + tol) * max(max(x["b1"] for x in res.values()), lim["boost"][2] + lag(VB))
        g9_ = res["7"]["gs"][9.0]
        rows.append(dict(r=r, code=row["code"], model=row["model"], stock=row["stock"], lim=lim, res=res, ok_b1=ok_b1, ok_b2=ok_b2,
                         l9=g9_["s"]["i_l"], hot9=max(g9_["fets"], key=lambda f: (f["tj"] is None, f["tj"] or 0.0)),
                         m_boost=m_boost, m_buck=m_buck, cs_v=cs_v, ok=ok_b1 and ok_b2 and m_boost > 0 and m_buck > 0 and cs_v < cs_abs))
    rows.sort(key=lambda x: x["r"])
    passing = [x for x in rows if x["ok"]]
    if not passing:
        refuse(4, "no catalogue R12 bounds the fault")
    ch = passing[0]                                           # the smallest passing value: the most service margin
    lim = ch["lim"]
    R.update(cands=rows, chosen=ch, svc9=svc9, svc12=svc12, svc_boost_pk=svc_boost_pk, svc_boost_pkb=svc_boost_pkb,
             svc_valley=svc_valley, veh_pk=veh_pk, m_veh=lim["boost"][0] - veh_pk)
    # the chosen value at each outcome: B-1, B-2, L1's temperature, R12's own dissipation
    for o in R["outcomes"]:
        x = ch["res"][o["key"]]
        o["c"] = x
        o["c_b1"] = x["b1"]
        o["c_l1_temp"] = max(g["l1_temp"] for g in x["gs"].values())
        o["c_derate_need"] = x["b1"] / (0.9 * isat)
        o["c_delay_head"] = (0.9 * isat - x["b1"]) / (VB / l_low)       # the comparator delay the headroom admits at the top of boost
        g9 = x["gs"][9.0]
        p12 = g9["s"]["rms"] ** 2 * g9["s"]["d"] * ch["r"] * (1 + tol)
        g36 = x["gs"][36.0]
        p12b = g36["s"]["rms"] ** 2 * (1 - g36["s"]["d"]) * ch["r"] * (1 + tol)
        o["c_r12"] = (p12, p12b, t_air + max(p12, p12b) * k_r)
    # the boundary above which the average limit, not the peak limit, sets the fault current (boost)
    for o in R["outcomes"]:
        o["v_avg"] = next((v for v in VIN_GRID if regime(o["hi"], v, lim)["who"] == "the average limit"), None)
        o["i_out9"] = regime(o["hi"], 9.0, lim)["i_out"]
    # the slope capacitor (Equation 26) and the loop's first-order consequence
    c_new = gm_slope * l_nom / (ch["r"] * acs)
    R.update(c_slope_new=c_new, c147_new=330e-12, c147_code=L["mp"][(r"^330p$", "C_0603")], loop_scale=M.R12_CS / ch["r"])
    gtxt = " ".join(l_.strip().lstrip("#").strip() for l_ in open(os.path.join(TOP, M.GEN_A), encoding="utf-8").read().splitlines())
    xo = need(gtxt, r"crossover ([\d.]+) to ([\d.]+) kHz, 89 mOhm", "gen_sch_a.py the FE loop's crossover")
    R["xover"] = (float(xo.group(1)), float(xo.group(2)))
    # without L4-E5's line, L4-E4's in-service 4.964 A would meet the chosen peak limit below this VIN
    R["v_no_h3"] = max((v for v in VIN_GRID if stage(R4["serv"], v)["mode"] == "boost" and stage(R4["serv"], v)["peak"] >= lim["boost"][0]), default=None)

    # ================================================================== 6: B-4, the generator's VBUS20 node analysis method
    for o in R["outcomes"]:
        o["b4"] = tuple(k * o["hi"] for k in can_k)
        o["b4_need"] = tuple(rip_bulk / o["hi"] / k for k in can_k)    # the factor each spread's worst can must reach
        o["b4_9v"] = tuple(k * o["i_out9"] for k in can_k)

    # ================================================================== 7: predicates
    o8, o7 = R["outcomes"]
    P = [
        ("0: the three outputs reproduced byte for byte in child processes", R["r0a"] and R["r0b"] and R["r0c"]),
        ("0: l4e4_limits.compute() and r11_dep.main() print their records in-process; the FET relations reprint r11_dep.out's", R["r0d"] and R["r0e"] and R["r0f"]),
        ("(a) hiccup counts cycle-by-cycle limits only; with R12 as drawn it is not guaranteed at 9 V at either outcome",
         all(o["a"][9.0]["hic"] != "guaranteed" for o in R["outcomes"])),
        ("(a) alone leaves B-1 over 90 % of the typical Isat at 9 V at both outcomes", all(o["a_b1"] > 0.9 * isat for o in R["outcomes"])),
        ("(a) alone leaves a FET past 150 C at 9 V at both outcomes on the maker's RthetaJA", not any(o["a_b2"] for o in R["outcomes"])),
        ("the chosen R12 is the smallest catalogue value that closes B-1 (25 C) and B-2 at both outcomes with service margin",
         ch is passing[0] and all(not x["ok"] for x in rows if x["r"] < ch["r"])),
        ("B-1 at 25 C: L1's peak at most 90 % of the typical Isat at both outcomes, 9 to 36 V", all(o["c_b1"] <= 0.9 * isat for o in R["outcomes"])),
        ("B-1 at temperature: INCONCLUSIVE (the held Coilcraft sheet carries no temperature derating)", not derating_held),
        ("B-2: every FET at most 150 C at 9, 15.1 and 36 V at both outcomes (RthetaJA the maker's, an ASSUMPTION for board A)",
         all(f["tj"] is not None and f["tj"] <= 150.0 for o in R["outcomes"] for g in o["c"]["gs"].values() for f in g["fets"])),
        ("B-4 on the drawn bank: NOT met at the 2:1 spread at either outcome; met matched and at 1.5:1 at 8 mOhm only",
         o8["b4"][2] > rip_bulk and o7["b4"][2] > rip_bulk and o8["b4"][0] <= rip_bulk and o8["b4"][1] <= rip_bulk and o7["b4"][0] > rip_bulk),
        ("service: the chosen peak limit's minimum above H3's in-service boost peak; the valley limit's minimum above the pin path's valley",
         R["chosen"]["m_boost"] > 0 and R["chosen"]["m_buck"] > 0),
        ("the chosen R12 needs L4-E5's line first: L4-E4's 4.964 A alone would meet the peak limit below %.1f V" % (R["v_no_h3"] or 0), R["v_no_h3"] is not None and R["v_no_h3"] > 9.0),
        ("the consequence for L4-E4: 8 mOhm supported (B-1, B-2 independent of R11; B-4's gap smaller at 8 mOhm)",
         o8["c_b1"] <= 0.9 * isat and o8["b4"][2] - rip_bulk < o7["b4"][2] - rip_bulk),
    ]
    R["preds"] = P
    if not all(ok for _p, ok in P):
        refuse(4, "a predicate failed: %s" % [p for p, ok in P if not ok])
    return R


def render(R):
    out = []
    P = out.append
    isat, VB = R["isat"], R["VB"]
    o8, o7 = R["outcomes"]
    ch, lim = R["chosen"], R["chosen"]["lim"]
    P("L4-E6: FAULT HANDLING OF BOARD A'S FRONT END U2 (LM5176), FINDINGS B-1, B-2 AND B-4 (l4e6_fault_handling.py, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing bought, built, powered or measured; no generator, registry, rendered page or L4-E4/L4-E5 record")
    P("edited. Basis per figure: MAKER (document, page), NETLIST, MODELED, INFERRED (method stated), ASSUMPTION; INCONCLUSIVE")
    P("where no held document gives the figure.")
    P("")
    P("0. REPRODUCTIONS BEFORE ANY RESULT")
    P("   0a l4e4_limits.py re-run in a child process reproduces l4e4_limits.out byte for byte (sha256/16 %s): %s" % (R["out_sha"][L4E4_OUT][:16], "yes" if R["r0a"] else "NO"))
    P("   0b l4e5_source_control.py re-run in a child process reproduces l4e5_source_control.out byte for byte (sha256/16 %s): %s" % (R["out_sha"][L4E5_OUT][:16], "yes" if R["r0b"] else "NO"))
    P("   0c r11_dep.py re-run in a child process reproduces r11_dep.out byte for byte (sha256/16 %s): %s" % (R["out_sha"][R11_OUT][:16], "yes" if R["r0c"] else "NO"))
    P("   0d l4e4_limits.compute() run here renders l4e4_limits.out byte for byte: %s (band(), R11 8 mOhm and its 7 mOhm alternative taken from it)" % ("yes" if R["r0d"] else "NO"))
    P("   0e r11_dep.main() run here (locals captured by l4e4_limits.run_main_captured) prints r11_dep.out byte for byte: %s" % ("yes" if R["r0e"] else "NO"))
    P("      (stage(), peak_b(), fet_tj(), Figure 8's readings, the generator's VBUS20 bank figures and their per-can scaling taken from it);")
    P("      r11_dep.py's FET loss relations, restated here once, reprint all nine of its section 4 FET lines byte for byte: %s" % ("yes" if R["r0f"] else "NO"))
    P("   L4-E5's figures read from its reproduced output: the pin path %.3f A in board current, %.3f A through R11, between %.2f and" % (R["pin_board"], R["pin_r11"], R["band45"][0]))
    P("   %.2f V; V-A07's threshold %.3f A; H3's highest U3 board current %.3f A at 9 V and %.3f A at 12 V; the 7 mOhm consequence" % (
        R["band45"][1], R["va07"], R["h3"][9.0], R["h3"][12.0]))
    P("   (C2904239, %.3f A) checked equal to L4-E4's alternative. The vehicle entry's %.2f A from r11_dep.out (gen_sch_e.py _VEH_T)" % (o7["hi"], R["veh"]))
    P("   LM5176 sheet sha256/16 %s; Coilcraft XAL1010 (Document 804-1, revised 02/25/26) and XAL1510 (Document 947-1, revised 05/04/26) pinned" % R["lm5176_sha"][:16])
    P("")
    P("1. WHAT BOARD A CARRIES AND WHAT THE MAKERS PRINT")
    for f in R["facts"]:
        P("   NETLIST: %s" % f)
    P("   MAKER SNVSAI1D (LM5176, rev. D, August 2021):")
    P("     p.13: the inductor current is sensed through ONE resistor in series with the low-side MOSFETs (R12) and monitored for the")
    P("       cycle-by-cycle limit; without hiccup the controller stays in that limit until the overload is removed")
    P("     p.16 7.3.5: boost, the low-side switch turns off for the rest of the cycle when CS-CSG exceeds VCS(BOOST); buck, the high-side")
    P("       switch skips a cycle while the sensed valley stays above VCS(BUCK). p.7 (HTSSOP): VCS(BOOST) %.0f / %.0f / %.0f mV, VCS(BUCK)" % tuple(v * 1e3 for v in R["vcs_boost"]))
    P("       %.0f / %.0f / %.0f mV, IOFFSET(CS/CSG) %.0f uA (MAX column), gmSLOPE %.0f uS; p.5: CS, CSG at most %.1f V" % (
        tuple(v * 1e3 for v in R["vcs_buck"]) + (R["i_off"] * 1e6, R["gm_slope"] * 1e6, R["cs_abs"])))
    P("     p.17 7.3.5: hiccup shuts the controller down after %d CONSECUTIVE CYCLE-BY-CYCLE LIMITS and releases SS after %d clock cycles;" % (R["n_trip"], R["n_off"]))
    P("       p.16 7.3.4 and p.17 7.3.6: the AVERAGE limit acts by discharging SS through its gm amplifier, so it never counts as a")
    P("       cycle-by-cycle limit: hiccup does not act on the highest permitted current the average limit sets (INFERRED from the two)")
    P("     p.3 and p.20: %.2f V < MODE < %.2f V selects CCM with hiccup (RMODE %.1f kOhm to AGND); %.1f V < MODE < VCC, or MODE to VCC," % (R["mode_hic"][:2] + (R["mode_hic"][2], R["mode_no"])))
    P("       no hiccup; MODE is latched at start-up. p.7: IMODE %.0f / %.0f / %.0f uA" % tuple(v * 1e6 for v in R["imode"]))
    P("     p.6: ISS %.2f / %.0f / %.2f uA, VREF %.3f / %.3f / %.3f V, fSW %.0f / %.0f / %.0f kHz at RT 40 k" % (
        tuple(v * 1e6 for v in R["iss"]) + R["vref"] + tuple(v / 1e3 for v in R["fsw"])))
    P("     p.24 8.2.2.7: the CS resistor is sized from the application's own currents (Equation 23, 80 mV / IOUT(MAX); Equation 24,")
    P("       120 mV / IL(PEAK)); 8.2.2.8 Equation 26, CSLOPE = gmSLOPE x L1 / (RSENSE x ACS), ACS %.0f (its example): %.0f pF at the drawn" % (R["acs"], R["c_slope_drawn"] * 1e12))
    P("       %.0f mOhm, C147 680 pF; 'a current mode loop is stable with half the dead-beat slope'" % (R["r12_drawn"] * 1e3))
    P("   MAKER Coilcraft XAL1010-103ME (Document 804-1, p.1): Isat %.1f A typical at 25 C (note 5: 30 %% inductance drop), Irms %.1f A at" % (isat, R["irms40"]))
    P("     40 K rise, L +-%.0f %%; temperature derating is a link ('Click for temperature derating information'), and p.3's 'Typical L" % (R["l_tol"] * 100))
    P("     vs Current' is one 25 C curve: Isat at the part's temperature is NOT HELD (C-5) -> %s" % ("held" if R["derating_held"] else "INCONCLUSIVE"))
    x = R["xal15"]
    P("   MAKER Coilcraft XAL1510-103ME (Document 947-1, p.1; board E's tracker inductor): %.0f uH, DCR %.2f mOhm max, Isat %.1f A typical" % (x["l"], x["dcr_max"], x["isat"]))
    P("     at 25 C, Irms %.0f / %.0f A (20 / 40 K); the same derating link, not held" % (x["irms20"], x["irms40"]))
    P("   INFERRED here: the CS filter's lag %.0f ns (R150 + R151 at +1 %%, C123 at +%.0f %%, an ASSUMPTION: the netlist prints '1n');" % (R["tau_cs"] * 1e9, C123_TOL * 100))
    P("     the CSG offset %.1f mV (IOFFSET over one 100 Ohm), added against each end of the limits; the comparator's own delay is NOT" % (R["cs_off"] * 1e3))
    P("     PRINTED (INCONCLUSIVE), so B-1 states the delay its headroom admits")
    P("")
    P("2. THE HIGHEST PERMITTED CURRENT AT EACH R11 OUTCOME (L4-E4's band(), r11_dep.py's stacking)")
    for o in R["outcomes"]:
        P("   R11 %s mOhm (%s): band %.3f / %.3f / %.3f A; the highest permitted current %.3f A" % (o["key"], o["code"], o["band"][0], o["band"][1], o["band"][2], o["hi"]))
    P("   relations (INFERRED, r11_dep.py section 4): VBUS20 at %.3f V, efficiency %.2f DECLARED, L at -20 %% and fSW minimum for the" % (VB, R["eta"]))
    P("   ripple; B-1's peak as r11_dep.py's note 5 (Isat's 30 % drop on the -20 % tolerance); the FETs on RDS(on) max x Figure 8 at TJ")
    P("   and the maker's RthetaJA %.0f C/W on its 1 in2 2 oz pad, used for board A as an ASSUMPTION (board A's own is not known, C-3)" % R["rtja"])
    P("")
    P("3. CANDIDATE (a): HICCUP ALONE (R119 to AGND at 93.1 kOhm; R12 as drawn, %.0f mOhm: peak limit %.2f / %.2f / %.2f A, valley %.2f / %.2f / %.2f A," % (
        (R["r12_drawn"] * 1e3,) + R["drawn"]["boost"] + R["drawn"]["buck"]))
    P("   stacked as the HoJLR2512 series, +-1 % and 50 ppm/K, the drawn LR2512D's own TCR not being held: an ASSUMPTION)")
    P("   MODE at 93.1 kOhm: %.3f to %.3f V (IMODE's band, the resistor at 1 %%, an ASSUMPTION), inside %.2f to %.2f V: hiccup at every corner" % (
        R["mode931"][0], R["mode931"][1], R["mode_hic"][0], R["mode_hic"][1]))
    ht = R["hiccup_t"]
    P("   its timing (INFERRED from p.17, p.6 and C7): trips after %.2f to %.2f ms of consecutive limits, off %.1f to %.1f ms, then a full soft" % (
        ht["trip"][0] * 1e3, ht["trip"][1] * 1e3, ht["off"][0] * 1e3, ht["off"][1] * 1e3))
    P("   start, %.2f to %.2f s (C7 4.7 uF nominal x VREF / ISS); the peak in each burst is the cycle-by-cycle limit's own, the ripple" % ht["ss"])
    P("   per cycle unchanged; only the average falls")
    for o in R["outcomes"]:
        P("   R11 %s mOhm, %.3f A:" % (o["key"], o["hi"]))
        for v in CLOSE_VINS:
            a = o["a"][v]
            g = a["g"]
            P("     %4.1f V (%s): L1 average at the average limit %.2f A, peak %.2f A (L -20 %%); hiccup %s;" % (v, g["s_lim"]["mode"], g["s_lim"]["i_l"], a["pk_act"], a["hic"]))
            P("       continuous (no hiccup credit): L1 %.2f A average, B-1 peak %.2f A (%.1f %% of the typical Isat); FETs: %s" % (
                g["s"]["i_l"], g["peak"], 100 * g["peak"] / isat, "; ".join(
                    ("%s past 150 C (needs RthetaJA <= %.0f C/W)" % (f["name"], f["need_rth"])) if f["tj"] is None else ("%s TJ %.0f C" % (f["name"], f["tj"])) for f in g["fets"])))
        P("     B-1 %.2f A against %.2f A (90 %% of %.1f A): %s; B-2: %s; B-4 unchanged (section 6)" % (
            o["a_b1"], 0.9 * isat, isat, "NOT MET" if o["a_b1"] > 0.9 * isat else "met", "met" if o["a_b2"] else "NOT MET"))
    P("   NOT CHOSEN: the average limit, not the cycle-by-cycle limit, sets the fault current at 9 V, so hiccup cannot be relied on")
    P("   to engage; where it does, it bounds the average, not L1's peak, which stays above Isat")
    P("")
    P("4. CANDIDATE (b): RATE L1, THE FETS AND THE BANK FOR THE HIGHEST PERMITTED CURRENT")
    for o in R["outcomes"]:
        P("   R11 %s mOhm: L1 as XAL1510-103ME, B-1's %.2f A is %.1f %% of its %.1f A typical (25 C; temperature INCONCLUSIVE; its %.1f x %.1f mm" % (
            o["key"], o["a_b1"], 100 * o["b_l1_ratio"], R["xal15"]["isat"], R["dims15"][0], R["dims15"][1]))
        P("     outline, Document 947-1 p.3, against the XAL1010's %.1f x %.1f mm, p.4: board A's placement moves); the FETs at 9 V need" % R["dims10"])
        P("     RthetaJA <= %.0f C/W each, against the maker's %.0f; no 100 V FET with a lower RDS(on) is held (CSD18510Q5B, SLPS632 p.1, is" % (o["b_need_rth"], R["rtja"]))
        P("     %.0f V, under VIN_RAW's %.1f V clamp in L4-E5): INCONCLUSIVE; the bank as section 6" % (R["vds18510"], R["clamp"]))
    P("   NOT CHOSEN: three part changes, a new land, and a thermal figure no held document or measurement supports")
    P("")
    P("5. THE DECISION: BOUND L1 AND THE FETS WITH U2'S OWN CYCLE-BY-CYCLE LIMIT (R12), RATE THE BANK, NO HICCUP")
    P("   the scan (HoJLR2512-3W, JLCPCB's catalogue reading of L4-E4, 1 %, in stock, 5 to 20 mOhm): peak and valley limits stacked;")
    P("   service: H3's highest boost peak %.2f A (9 and 12 V, L -20 %%; %.2f A by note 5), the pin path's valley %.2f A at %.2f V (ripple" % (
        R["svc_boost_pk"], R["svc_boost_pkb"], R["svc_valley"], R["band45"][0]))
    P("   at its smallest); B-1 over 9 to 36 V; B-2 at 9, 15.1 and 36 V, both outcomes; CS within %.1f V" % R["cs_abs"])
    for c in R["cands"]:
        P("     %-22s %s: peak %.2f / %.2f / %.2f A, valley %.2f / %.2f / %.2f A; service %+.2f / %+.2f A; B-1 %.2f / %.2f A; B-2 %s; %s" % (
            c["model"], c["code"], c["lim"]["boost"][0], c["lim"]["boost"][1], c["lim"]["boost"][2], c["lim"]["buck"][0], c["lim"]["buck"][1], c["lim"]["buck"][2],
            c["m_boost"], c["m_buck"], c["res"]["8"]["b1"], c["res"]["7"]["b1"], "met" if c["ok_b2"] else "NOT met", "PASSES" if c["ok"] else "fails"))
        h = c["hot9"]
        P("       at 9 V (7 mOhm): L1 %.2f A average continuous, hottest %s" % (c["l9"], ("%s past 150 C" % h["name"]) if h["tj"] is None else ("%s TJ %.0f C" % (h["name"], h["tj"]))))
    P("   CHOSEN: R12 %.0f mOhm, %s, LCSC %s (stock %d), the smallest value that passes: the most service margin. Its sheet is the" % (
        ch["r"] * 1e3, ch["model"], ch["code"], ch["stock"]))
    P("     held HoJLR2512 series sheet (+-1 %%, 50 ppm/K, 3 W). Peak limit %.2f / %.2f / %.2f A, valley limit %.2f / %.2f / %.2f A" % (lim["boost"] + lim["buck"]))
    P("   C147 to 330 pF C0G (lcsc_fill.py's %s): Equation 26 gives %.0f pF at %.0f mOhm; the drawn 680 pF was the same at-or-below choice" % (
        R["c147_code"], R["c_slope_new"] * 1e12, ch["r"] * 1e3))
    P("     for 800 pF. The current loop's gain per ampere falls to %.3f of the drawn: the voltage loop's crossover, %.2f to %.1f kHz in" % (R["loop_scale"], R["xover"][0], R["xover"][1]))
    P("     gen_sch_a.py, moves toward %.2f to %.1f kHz to first order (INFERRED); the compensation is re-verified by the generator's loop" % (
        R["xover"][0] * R["loop_scale"], R["xover"][1] * R["loop_scale"]))
    P("     check before regeneration (OWED, INCONCLUSIVE here)")
    P("   MODE stays at VCC (no hiccup): the closures below take no hiccup credit; at 9 V the vehicle entry's %.2f A all through L1" % R["veh"])
    P("     peaks at %.2f A, %+.2f A from the chosen peak limit's minimum, so hiccup would turn an entry at its limit into a %.2f to %.2f s" % (
        R["veh_pk"], R["m_veh"], ht["ss"][0], ht["ss"][1]))
    P("     restart with FE_PGOOD down, against V-A08; without it the limit only clips the current")
    P("   ORDER: R12 goes in with L4-E5's line (H3), never before it: IIN_HOST fixed at %.2f A without the line (%.3f A through R11)" % (R["setting"], R["serv44"]))
    P("     would meet the chosen peak limit's minimum in service below %.1f V; under H3 the boost peak stays at %.2f A (section 5's service)" % (R["v_no_h3"], R["svc_boost_pk"]))
    P("   CS pins: R12 at +1 %% times the highest current it carries, %.3f V against the %.1f V absolute maximum (p.5)" % (ch["cs_v"], R["cs_abs"]))
    P("")
    P("   CLOSURES AT EACH OUTCOME (continuous, no hiccup credit; the FETs on the ASSUMED %.0f C/W)" % R["rtja"])
    for o in R["outcomes"]:
        P("   R11 %s mOhm, %.3f A:" % (o["key"], o["hi"]))
        for v in CLOSE_VINS:
            g = o["c"]["gs"][v]
            P("     %4.1f V (%s, set by %s): L1 %.2f A average, %.2f A rms, peak bound %.2f A, L1 at %.0f C; output %.2f A; FETs: %s" % (
                v, g["s"]["mode"], g["who"], g["s"]["i_l"], g["s"]["rms"], g["peak"], g["l1_temp"], g["i_out"], "; ".join(
                    ("%s past 150 C" % f["name"]) if f["tj"] is None else ("%s %.2f W, TJ %.0f C" % (f["name"], f["p"], f["tj"])) for f in g["fets"])))
        P("     B-1: the peak bound over 9 to 36 V %.2f A (at %.1f V), %.1f %% of the typical %.1f A at 25 C: MET at 25 C; it holds at the part's" % (
            o["c_b1"], o["c"]["b1_v"], 100 * o["c_b1"] / isat, isat))
        P("       temperature (at most %.0f C here) if Isat there is at least %.1f %% of its 25 C value, %.2f A: INCONCLUSIVE (C-5); the headroom admits" % (
            o["c_l1_temp"], 100 * o["c_derate_need"], o["c_b1"] / 0.9))
        P("       a comparator delay of %.2f us at the top of boost" % (o["c_delay_head"] * 1e6))
        P("     B-2: every FET at most %.0f C: MET on the ASSUMED RthetaJA; R12 itself %.2f W at 9 V, %.2f W at 36 V, at most %.0f C" % (
            max(f["tj"] for g in o["c"]["gs"].values() for f in g["fets"]), o["c_r12"][0], o["c_r12"][1], o["c_r12"][2]))
        P("     above %.1f V the average limit, not the peak limit, sets the fault current; at 9 V the output is held to %.2f A" % (o["v_avg"], o["i_out9"]))
    P("")
    P("6. B-4, VBUS20'S BANK, BY THE GENERATOR'S NODE ANALYSIS AS r11_dep.py CARRIES IT (gen_sch_a.py's third fix-up figures at 5.7")
    P("   and 5.0 A, the worst can scaled in proportion to the front end's current; the dense script drafts/scripts/ripple_dense.py is")
    P("   not in this tree, so the method is VIN-blind and is applied at the current the fault can hold continuously)")
    for o in R["outcomes"]:
        P("   R11 %s mOhm, %.3f A: worst can %.2f A matched, %.2f A at 1.5:1, %.2f A at 2:1 against %.1f A: %s" % (
            o["key"], o["hi"], o["b4"][0], o["b4"][1], o["b4"][2], R["rip_bulk"], ", ".join(
                "%s %s" % (lab, "met" if v <= R["rip_bulk"] else "NOT MET") for lab, v in zip(("matched", "1.5:1", "2:1"), o["b4"]))))
        P("     the bank's worst can per ampere must be at most %.3f / %.3f / %.3f times today's (matched / 1.5:1 / 2:1); at 9 V, where the peak" % o["b4_need"])
        P("     limit holds the output to %.2f A, it reads %.2f / %.2f / %.2f A" % ((o["i_out9"],) + o["b4_9v"]))
    P("   DECISION for B-4: the bank is rated, not bounded (the average limit holds the highest permitted current above the boundary")
    P("   VIN at both outcomes, and no peak or valley limit compatible with service holds it lower). Closure OWED to the generator owner:")
    P("   the dense node analysis re-run with a re-sized bank (more EEHZK1V331P, one part number, or ceramics moved to FE_OUT) at the")
    P("   chosen current; INCONCLUSIVE until then; bench 7b.8")
    P("")
    P("7. THE CONSEQUENCE FOR L4-E4")
    P("   B-1 and B-2 close at both outcomes by the same R12 (the peak limit does not depend on R11); B-4 does not close on the drawn")
    P("   bank at either, and its gap is %.2f A at 2:1 only at 8 mOhm against %.2f A at all three spreads at 7 mOhm. This decision" % (
        o8["b4"][2] - R["rip_bulk"], o7["b4"][2] - R["rip_bulk"]))
    P("   SUPPORTS R11 8 mOhm (C2904240) with IIN_HOST %.2f A and L4-E5's line; it does not require 7 mOhm. For 8 mOhm to stand, bench" % R["setting"])
    P("   V-A07 must show the pin's error at 10 mOhm at most %.3f A between %.2f and %.2f V (L4-E5's figure, unchanged here: R12 is not" % (
        R["va07"], R["band45"][0], R["band45"][1]))
    P("   in the ISNS path). If it fails, 7 mOhm stands with the same R12 and a larger bank re-size")
    P("")
    P("8. ACCEPTANCE PREDICATES (held by v2/ecad/tools/tests/test_l4e6.py on these computed values)")
    for p, ok in R["preds"]:
        P("   %s: %s" % (p, "yes" if ok else "NO"))
    P("")
    P("END. Desk arithmetic; nothing is measured. B-1 at temperature, the comparator's delay, the loop at the new R12 and the")
    P("re-sized bank stay INCONCLUSIVE until the documents, the generator owner's analyses and the bench rows of L4E6-FAULT-HANDLING.md.")
    return out


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
