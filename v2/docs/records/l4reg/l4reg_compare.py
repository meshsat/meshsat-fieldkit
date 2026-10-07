#!/usr/bin/env python3
"""l4reg_compare.py: Layer 4 task L4A-56 as re-scoped by W135's CHANGE-METHOD (record l4lim, fnd/l4lim aa6704b2), the ledger's RE-6 and
RE-7: the supervisors' regulator stage compared over at most three materially different approaches, the selection, and its draft on
board B composed, read and mutated (MESHSAT-1357, 7 October 2026, W138). PROTOTYPE DESIGN: nothing in this kit has been built,
bought, powered or measured; no figure printed here is a measurement. It closes no cx46 item and moves no state: cx46 CORRECTIONS NOT
CLOSED and Layer 4's DESK gate NOT PASSED stand.

The approaches (constitution section 4, an unresolved design choice):
  A. the limiter W135 selected (TI TPS2553-1 at RILIM 49.9 kOhm) with a REPLACEMENT regulator found on printed figures;
  B. K1, a buck per supervisor (board B's own AP63203WU-7, record l9t5 T10 section 8), its area, efficiency and thermal on printed figures;
  C. the regulator's own printed current limit as the containment, no separate limiter (one part; materially different from A).
Each is judged on the same rows: the window against every served and fault row (TCAN334's 180 mA PRINTED, rows (f1) and (f2), IOHA
row 7), the regulator's junction at 76.25 C air on PRINTED thermal figures, the output short, T10-A3's headroom, parts, area on board
B's floor plan, new failure modes, and HO-E's interaction.

What it does, deterministically and without touching the tree (every composition in a temporary directory):
  1. the inputs, pinned by sha256 (record l9t5's output and pages, the floor plan, W135's screen and W137's draft as copied into
     inputs/, the makers' sheets and their committed or held texts through v2/docs/records/_lib/pdftext.py);
  2. the rows, parsed from record l9t5's T10 output (never typed), and W135's figures reproduced from its copied output;
  3. the makers' printed rows of every part read, with page and table;
  4. to 6. the three approaches, row by row;
  7. the comparison and the SESSION selection with its authority fields and end condition;
  8. the acceptance judge on the selected stage, with its failing mutations (a typical value used as a limit; the AP2112K at the new
     current; the legacy-silicon order code; the thermal resistance one step over the requirement);
  9. the draft apply_gen_sch_b_regstage.py composed in L4-E9's order after record l9t5's iocguard (and with W137's canmb in either
     order), regenerated with record l8p's gen_netlist.py, read by pin, mutated, and its refusals;
 10. findings for other authors; 11. the predicates.
Run from the repository root:  python3 v2/docs/records/l4reg/l4reg_compare.py  (l4reg_compare.out is its output, regenerated with
_bin/regen_out.py). Labels: PRINTED (a maker's guaranteed limit or tested row), TYPICAL, DESCRIBED (the maker's prose, no limit),
DECLARED, MODEL (arithmetic on labelled inputs), INFERRED, ASSUMPTION, SESSION. A TYPICAL figure is never used as a limit."""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
REL = "v2/docs/records/l4reg"
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "l9t5"))
import l9t5_t10 as T  # noqa: E402  (record l9t5's T10: the AP2112, TCAN334 and H743 rows, the 14.0k set point, the drafts)
D = T.D
CHK = D.CHK
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)

# every maker's PDF this script reads as text (W34's rule: a generator never runs pdftotext; the texts are taken by
# v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4reg; the four TI sheets are held back, fetch_held_back.py beside this file)
PDFTEXT = {
    "v2/vendor/ti/held/ti-tps737-sbvs067w.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tlv757p-sbvs322c.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps7a37-sbvs220b.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps2553-slvs841f.pdf": [["-layout"]],
    "v2/vendor/diodes/diodes-ap63200-series-buck.pdf": [["-layout"]],
}
SHEET = {"tps737": "v2/vendor/ti/held/ti-tps737-sbvs067w.pdf", "tlv757p": "v2/vendor/ti/held/ti-tlv757p-sbvs322c.pdf",
         "tps7a37": "v2/vendor/ti/held/ti-tps7a37-sbvs220b.pdf", "tps2553": "v2/vendor/ti/held/ti-tps2553-slvs841f.pdf",
         "ap63200": "v2/vendor/diodes/diodes-ap63200-series-buck.pdf"}
T10_OUT = "v2/docs/records/l9t5/l9t5_t10.out"
DOCS = {"t10py": "v2/docs/records/l9t5/l9t5_t10.py", "drafts": "v2/docs/records/l9t5/l9t5_drafts.py",
        "ioha": "v2/docs/ARCH-PCB-B-IOHA.md", "rem": "v2/docs/records/l4close/REMAINING-ENGINEERING.md",
        "floor": "v2/ecad/tools/gen_pcb_b3.py", "gen_b": "v2/ecad/tools/gen_sch_b.py",
        "guard": "v2/docs/records/l9t5/apply_gen_sch_b_iocguard.py", "draft": "v2/docs/records/l9t5/apply_gen_sch_b_regstage.py",
        "lim_page": REL + "/inputs/l4lim-L4LIM-SCREEN-a45673da.md", "lim_out": REL + "/inputs/l4lim-l4lim_screen-d26c5d67.out",
        "canmb": REL + "/inputs/l9t5-apply_gen_sch_b_canmb-9367f3ab.py", "fetch": REL + "/fetch_held_back.py"}
SOURCES = {"lim_page": "fnd/l4lim aa6704b2 v2/docs/records/l4lim/L4LIM-SCREEN.md (W135)",
           "lim_out": "fnd/l4lim aa6704b2 v2/docs/records/l4lim/l4lim_screen.out (W135)",
           "canmb": "fnd/l4canmb 31de4bbc v2/docs/records/l9t5/apply_gen_sch_b_canmb.py (W137's checkpoint)"}
DRAFT = os.path.join(ROOT, DOCS["draft"])
CANMB = os.path.join(ROOT, DOCS["canmb"])

# the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
R_TOL = 0.01            # RILIM at 1 % (the maker's recommended range is stated for 1 % parts)
R_ILIM = 49.9           # kOhm: the tested row W135 selected (SLVS841F 7.5)
VDO_SCALE = "linear"    # the dropout at a current under the printed 1 A row: the printed maximum times I / 1 A (INFERRED, the pass device
                        # in dropout is a resistance: TPS737 prints ZO(DO) 0.25 ohm TYPICAL; TI's TLV758P sheet in the tree says VDO
                        # scales approximately with output current, 7.1.3); record l9t5 inferred the AP2112's between its printed points
ETA_K1 = T.ETA_K1       # K1's efficiency, record l9t5's DECLARED 0.88 (U25's), the 5 V curve NOT PLOTTED: a TYPICAL, never a bound
EN_DASH = chr(0x2013)
RAILS = {"+5V_IOC", "GND", "+3V3_IOCA", "+3V3_IOCB", "+3V3_IOCC"}   # the power nets two drafts may both attach parts to
ADMIT = {"PRINTED"}     # the labels a LIMIT may carry; INFERRED only where a row declares it (the dropout's scaling), never TYPICAL


def refuse(msg):
    sys.stderr.write("l4reg_compare: REFUSED: %s\n" % msg)
    sys.exit(2)


def sha(relpath, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, relpath), "rb").read()).hexdigest()[:n]


def text(relpath):
    return open(os.path.join(ROOT, relpath), encoding="utf-8").read()


def pdf(key):
    return PT.pdf_text(ROOT, SHEET[key], ["-layout"], PDFTEXT, REL)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def page(t, m):
    return t[:m.start()].count("\f") + 1


def line(t, m):
    return t[:m.start()].count("\n") + 1


def F(v, label, where):
    """a labelled figure: (value, label, where it is printed or how it is derived)"""
    return (v, label, where)


# --------------------------------------------------------------------------------------------------------------- 2. the rows
def rows():
    """record l9t5's T10 output, parsed: every figure with its line (the regular expressions are W135's, l4lim_screen.py edges())."""
    t = text(T10_OUT)
    E = {}

    def get(key, pat, what, n=1, flags=re.M):
        m = need(t, pat, what, flags)
        E[key] = (float(m.group(n)), line(t, m))
        return m
    get("air", r"THE JUNCTION TEMPERATURE at L4-E12's inside air, ([\d.]+) C", "the inside air (section 4)")
    get("mcu125", r"its junction reaches 125 C at ([\d.]+) A", "the H743's 125 C current (section 4)")
    get("theta", r"SOT25 junction to ambient (\d+) C/W, no heat sink \(p\.3\)", "the AP2112K's junction to ambient (section 7)")
    m = need(t, r"R602 14\.0k, ([\d.]+) V\s*\n\s*nominal, ([\d.]+) to ([\d.]+) V; the drop at its worst corner ([\d.]+) V, ([\d.]+) K/A",
             "the 14.0k set point and its corner (10i)")
    for k, g in (("nom14", 1), ("lo14", 2), ("hi14", 3), ("drop", 4), ("kpa", 5)):
        E[k] = (float(m.group(g)), line(t, m))
    get("foldback", r"foldback short current (\d+) mA \(TYPICAL\)", "the AP2112's foldback (section 7)")
    m = need(t, r"against U601's (\d+) A \(PRINTED\) and the VH's (\d+) A", "U601's and the lead's ratings (section 9 (2))")
    E["u601"], E["vh"] = (float(m.group(1)), line(t, m)), (float(m.group(2)), line(t, m))
    get("share", r"the two transceivers at FW-B21's share \(10d\): ([\d.]+) A each", "the transceivers' share average (10c)")
    get("can_fault", r"dominant with a bus\s*\n\s*fault (\d+) mA maximum", "the TCAN334's bus-fault row (section 5)")
    get("f1", r"\(f1\) one fabric faulted.*?: ([\d.]+) A, junction", "row (f1) (section 8)", flags=re.S)
    get("f2", r"\(f2\) both fabrics faulted, both transceivers driving into their faults: ([\d.]+) A", "row (f2) (section 8)")
    get("both_v", r"rev V: held ([\d.]+) A, [\d.]+ C \(OVER 150 C\)", "both fabrics held, rev V (10e)")
    get("bab_v", r"^\s+babbling \(nothing ends it\)\s+V\s+([\d.]+) A", "the babbling row, rev V (10i)")
    get("vos0", r"105 C VOS0 limit from ([\d.]+) A \(MODEL\)", "HO-E's VOS0 current (10j (c))")
    m = need(t, r"each LDO's input at ([\d.]+) A, the sense\s*\n\s*resistor's drop counted: at least ([\d.]+) V against ([\d.]+) V: holds",
             "T10-A3 at the trip's average maximum (10j (d))")
    for k, g in (("a3_i", 1), ("a3_at", 2), ("a3_need", 3)):
        E[k] = (float(m.group(g)), line(t, m))
    m = need(t, r"Every served state is under the trip's least ([\d.]+) A \(the largest\s*\n\s*([\d.]+) A\): none trips", "the served rows (10j (e))")
    E["trip_lo"], E["s1"] = (float(m.group(1)), line(t, m)), (float(m.group(2)), line(t, m))
    m = need(t, r"([\d.]+) to ([\d.]+) A at the tolerances", "the rail trip's band (10j (b))")
    E["trip"] = ((float(m.group(1)), float(m.group(2))), line(t, m))
    held = {}
    for fault in ("B1", "B2", "B3", "B4", "B5", "B6", "B7a", "B7b"):
        m = need(t, r"^\s+%s\s+V\s+([\d.]+) A\s+[\d.]+ C" % fault, "the held row %s, rev V (10e)" % fault)
        held[fault] = (float(m.group(1)), line(t, m))
    E["held"] = held
    return E


def ioha():
    t = text(DOCS["ioha"])
    out = {}
    for k, pat in (("row3", r"^\| 3 \| One I/O supervisor dies or is unpowered \| n/a[^|]*\| (the other two are a majority and ownership is unaffected) \|"),
                   ("row7", r"^\| 7 \| One CAN fabric breaks or a transceiver fails dominant \| n/a[^|]*\| (quorum continues on the other fabric) \|"),
                   ("row8", r"^\| 8 \| Both CAN fabrics break \| n/a[^|]*\| (no controller can form a majority; [^|]*?) \|"),
                   ("area", r"(the control plane needs roughly 2,400 mm2: about (\d+) mm2 per controller)")):
        m = need(t, pat, "IOHA %s" % k, re.M | re.I)
        out[k] = (m.group(1), line(t, m))
    out["per_ctrl"] = (float(re.search(r"about (\d+) mm2", out["area"][0]).group(1)), out["area"][1])
    return out


def floor_plan():
    """board B's floor plan (gen_pcb_b3.py REGIONS, read with ast): the three controller pockets"""
    import ast
    src = text(DOCS["floor"])
    P = {}
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Tuple) and len(node.elts) >= 2 and isinstance(node.elts[0], ast.Constant) \
                and node.elts[0].value in ("IOCA", "IOCB", "IOCC") and isinstance(node.elts[1], ast.Tuple):
            x0, y0, x1, y1 = (float(ast.literal_eval(e)) for e in node.elts[1].elts)
            P[node.elts[0].value] = ((x0, y0, x1, y1), abs(x1 - x0) * abs(y1 - y0), node.lineno)
    if set(P) != {"IOCA", "IOCB", "IOCC"}:
        refuse("gen_pcb_b3.py's three controller pockets no longer read")
    return P


def w135():
    """W135's figures, parsed from its output as copied into inputs/ (fnd/l4lim aa6704b2): the ones this record reproduces"""
    t = text(DOCS["lim_out"])
    W = {}
    W["i125"] = float(need(t, r"SOT25 \(AP2112K\)\s+theta 184\.0 C/W\s+I125 ([\d.]+) A", "W135's I125").group(1))
    W["s3p"] = float(need(t, r"largest ([\d.]+) A \(B5", "W135's S3' largest").group(1))
    m = need(t, r"C1 TPS2553-1 at 49\.9 kOhm: the PRINTED row 0\.475 to 0\.565 A with the resistor's 1 % through the exponents: IOS ([\d.]+) to ([\d.]+) A",
             "W135's companion band")
    W["ios"] = (float(m.group(1)), float(m.group(2)))
    W["theta_need"] = float(need(t, r"the LDO must hold 125 C at [\d.]+ A: theta at most ([\d.]+) C/W\s*\n\s*\(the tested row governs",
                                 "W135's theta requirement").group(1))
    m = need(t, r"companion, C1 at 49\.9 kOhm\s+[\d.]+ A: ([\d.]+) V against ([\d.]+) V", "W135's T10-A3 at the companion's maximum")
    W["a3"] = (float(m.group(1)), float(m.group(2)))
    W["vdo_need"] = float(need(t, r"dropout at [\d.]+ A must be at most [\d.]+ - [\d.]+ = ([\d.]+) V", "W135's dropout requirement").group(1))
    need(t, r"CHANGE-METHOD", "W135's line")
    return W


# ------------------------------------------------------------------------------------------------------- 3. the makers' rows
def sheets():
    S = {}
    # --- TI TPS2553-1, SLVS841F (the limiter W135 selected; its patterns are W135's, l4lim_screen.py sheets())
    t = pdf("tps2553")
    need(t, r"SLVS841F", "the TPS255x sheet's number")
    m = need(t, r"RILIM = 49\.9 kΩ\s*\n\s*connected to GND\s+\S40°C ≤TJ ≤125°C\s+(\d+)\s+(\d+)\s+(\d+)", "IOS at 49.9 kOhm over TJ")
    S["ios49"] = F(tuple(float(x) / 1000 for x in m.groups()), "PRINTED", "SLVS841F 7.5 p.%d (min / typ / max, -40 to 125 C TJ)" % page(t, m))
    eq = {}
    for k in ("max", "nom", "min"):
        m = need(t, r"(\d+)V\s*\n\s*IOS%s \(mA\) =\s*\n\s*RILIM([\d.]+)kW" % k, "the IOS%s equation" % k)
        eq[k] = (float(m.group(1)), float(m.group(2)))
    S["ios_eq"] = F(eq, "PRINTED", "SLVS841F 9.5.1 p.%d (the maker's equations)" % page(t, m))
    m = need(t, r"DBV package, \S40°C ≤TJ ≤125°C\s+(\d+)", "rDS(on) DBV over TJ")
    S["ron"] = F(float(m.group(1)) / 1000, "PRINTED", "SLVS841F 7.5 p.%d (maximum, -40 to 125 C TJ)" % page(t, m))
    m = need(t, r"FAULT assertion or de-assertion due to overcurrent condition\s+(\d+)\s+([\d.]+)\s+(\d+)\s+ms", "the overcurrent deglitch")
    S["tlatch"] = F(tuple(float(x) / 1000 for x in m.groups()), "PRINTED", "SLVS841F 7.5 p.%d (min / typ / max)" % page(t, m))
    m = need(t, r"the TPS255x-1 limits the current to IOS until the overload condition is removed or the internal deglitch time\s*\nis reached "
             r"and the device is latched off\.", "the latch-off sentence (9.3.1)")
    S["latch_p"] = page(t, m)
    m = need(t, r"RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "RthJA (7.4)")
    S["lim_rja"] = F(float(m.group(3)), "PRINTED", "SLVS841F 7.4 p.%d (TPS2553 DBV)" % page(t, m))
    m = need(t, r"Continuous output current,\s+%s40 °C ≤ TJ ≤ 125 °C\s+0\s+([\d.]+)" % EN_DASH, "the continuous output current (7.3)")
    S["lim_iout"] = F(float(m.group(1)), "PRINTED", "SLVS841F 7.3 p.%d (-40 to 125 C TJ)" % page(t, m))
    m = need(t, r"tr\s+Rise time, output\s*\n.*?VIN = 2\.5 V\s+([\d.]+)\s+([\d.]+)", "the output rise time (7.5)", re.S)
    m2 = need(t, r"CL = 1 µF, RL = 100 Ω,\s+VIN = 6\.5 V\s+([\d.]+)\s+([\d.]+)\s*\ntr\s+Rise time, output", "the rise time at 6.5 V (7.5)")
    S["tr"] = F(max(float(m.group(2)), float(m2.group(2))) / 1000, "PRINTED", "SLVS841F 7.5 p.%d (maximum, CL 1 uF, RL 100 ohm)" % page(t, m2))
    m = need(t, r"Fast Overcurrent Response - (\d+) µs \(Typical\)", "the overcurrent response (typical)")
    S["tios"] = F(float(m.group(1)) * 1e-6, "TYPICAL", "SLVS841F p.%d (Features; 7.5 tIOS typical only)" % page(t, m))
    m = need(t, r"The device remains\s*\noff until power is cycled or the device enable is toggled\.", "the latch's exit (9.3.1)")
    S["exit_p"] = page(t, m)
    m = need(t, r"Device Information\(1\)\s*\n\s*PART NUMBER\s+PACKAGE\s+BODY SIZE \(NOM\)\s*\n.*?SOT-23 \(6\)\s+([\d.]+) mm x ([\d.]+) mm",
             "the DBV body size", re.S)
    S["dbv_body"] = F((float(m.group(1)), float(m.group(2))), "PRINTED", "SLVS841F p.%d (body, nominal)" % page(t, m))

    # --- TI TPS737, SBVS067W (the regulator)
    t = pdf("tps737")
    need(t, r"SBVS067W %s JANUARY 2006 %s REVISED AUGUST 2025" % (EN_DASH, EN_DASH), "the TPS737 sheet's number")
    m = need(t, r"5\.4 Thermal Information\s*\n\s*TPS737 New silicon\s*\n.*?DRB \(VSON\)\s+DCQ \(SOT-223\)\s+DRV \(WSON\).*?RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
             "the new silicon's thermal table (5.4)", re.S)
    S["rja_new"] = F({"DRB": float(m.group(1)), "DCQ": float(m.group(2)), "DRV": float(m.group(3))}, "PRINTED",
                     "SBVS067W 5.4 p.%d (new silicon; JEDEC high-K, JESD51-7)" % page(t, m))
    m = need(t, r"5\.5 Thermal Information\s*\n\s*TPS737 Legacy silicon\(2\)\s*\n.*?RθJA\s+Junction-to-ambient thermal resistance\(4\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
             "the legacy silicon's thermal table (5.5)", re.S)
    S["rja_leg"] = F({"DRB": float(m.group(1)), "DCQ": float(m.group(2)), "DRV": float(m.group(3))}, "PRINTED", "SBVS067W 5.5 p.%d (legacy silicon)" % page(t, m))
    m = need(t, r"DCQ: The exposed pad is connected to the PCB ground layer through a (\dx\d|\d×\d) thermal via array", "the DCQ simulation's vias (5.5 note 2)")
    S["dcq_vias"] = (m.group(1), page(t, m))
    m = need(t, r"VDO\s+IOUT = 1A, legacy silicon\s+(\d+)\s+(\d+)\s+mV", "the legacy dropout (5.6)")
    S["vdo_leg"] = F(float(m.group(2)) / 1000, "PRINTED", "SBVS067W 5.6 p.%d (maximum at 1 A, legacy silicon)" % page(t, m))
    S["vdo_leg_typ"] = F(float(m.group(1)) / 1000, "TYPICAL", "SBVS067W 5.6 p.%d (typical at 1 A, legacy silicon)" % page(t, m))
    m = need(t, r"VDO\s+IOUT = 1A, new silicon\s+(\d+)\s+(\d+)\s+mV", "the new dropout (5.6)")
    S["vdo_new"] = F(float(m.group(2)) / 1000, "PRINTED", "SBVS067W 5.6 p.%d (maximum at 1 A, new silicon)" % page(t, m))
    S["vdo_new_typ"] = F(float(m.group(1)) / 1000, "TYPICAL", "SBVS067W 5.6 p.%d (typical at 1 A, new silicon)" % page(t, m))
    m = need(t, r"5\.5V; 10mA ≤ IOUT ≤ 1A,\s+%s(\d+)\s+±0\.5\s+(\d+)\s*\n\s*legacy silicon" % EN_DASH, "the legacy accuracy (5.6)")
    S["acc_leg"] = F(float(m.group(2)) / 100, "PRINTED", "SBVS067W 5.6 p.%d (over VIN, IOUT and T; VOUT + 0.5 V <= VIN <= 5.5 V)" % page(t, m))
    m = need(t, r"5\.5V; 10mA ≤ IOUT ≤ 1A, new\s+%s([\d.]+)\s+±0\.5\s+([\d.]+)\s*\n\s*silicon" % EN_DASH, "the new accuracy (5.6)")
    S["acc_new"] = F(float(m.group(2)) / 100, "PRINTED", "SBVS067W 5.6 p.%d (over VIN, IOUT and T; VOUT + 0.5 V <= VIN <= 5.5 V)" % page(t, m))
    m = need(t, r"VOUT \+ 0\.5V ≤ VIN ≤\s*\n\s*5\.5V; 10mA ≤ IOUT ≤ 1A, new", "the accuracy's input condition (5.6)")
    S["acc_head"] = F(0.5, "PRINTED", "SBVS067W 5.6 p.%d (the accuracy row's condition VIN >= VOUT + 0.5 V)" % page(t, m))
    m = need(t, r"ICL\s+Output current limit\s+VOUT = 0\.9 × VOUT\(nom\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "the current limit (5.6)")
    S["icl"] = F(tuple(float(x) for x in m.groups()), "PRINTED", "SBVS067W 5.6 p.%d (min / typ / max)" % page(t, m))
    m = need(t, r"IGND\s+Ground pin current\s+IOUT = 1A, new silicon\s+(\d+)\s+µA", "the ground current at 1 A (5.6)")
    S["ignd"] = F(float(m.group(1)) * 1e-6, "TYPICAL", "SBVS067W 5.6 p.%d (typical only, new silicon, 1 A)" % page(t, m))
    m = need(t, r"ISC\s+Short-circuit current\s+VOUT = 0V, new silicon\s+(\d+)\s+mA", "the short-circuit current (5.6)")
    S["isc"] = F(float(m.group(1)) / 1000, "TYPICAL", "SBVS067W 5.6 p.%d (typical only, new silicon)" % page(t, m))
    m = need(t, r"VIN\s+Input supply voltage\s+([\d.]+)\s+([\d.]+)\s+V", "the input range (5.3)")
    S["vin"] = F((float(m.group(1)), float(m.group(2))), "PRINTED", "SBVS067W 5.3 p.%d" % page(t, m))
    m = need(t, r"IOUT\s+Output current\s+0\s+(\d+)\s+A", "the output current (5.3)")
    S["iout"] = F(float(m.group(1)), "PRINTED", "SBVS067W 5.3 p.%d" % page(t, m))
    m = need(t, r"TJ\s+Operating junction temperature\s+%s40\s+(\d+)\s+°C" % EN_DASH, "the operating junction (5.3)")
    S["tj_op"] = F(float(m.group(1)), "PRINTED", "SBVS067W 5.3 p.%d" % page(t, m))
    m = need(t, r"Output short-circuit duration\s+(Indefinite)", "the short-circuit duration (5.1)")
    S["short_dur"] = F(m.group(1), "PRINTED", "SBVS067W 5.1 p.%d (Absolute Maximum Ratings)" % page(t, m))
    m = need(t, r"VEN\(high\)\s+EN pin high \(enabled\)\s+([\d.]+)\s+VIN\s+V", "EN high (5.6)")
    S["ven_hi"] = F(float(m.group(1)), "PRINTED", "SBVS067W 5.6 p.%d (1.7 V to VIN)" % page(t, m))
    m = need(t, r"VEN\(low\)\s+EN pin low \(shutdown\)\s+0\s+([\d.]+)\s+V", "EN low (5.6)")
    S["ven_lo"] = F(float(m.group(1)), "PRINTED", "SBVS067W 5.6 p.%d" % page(t, m))
    m = need(t, r"M3 is a suffix designator for devices that only use the latest manufacturing flow \(CSO: RFB\)\.\s*\n\s*Devices without this suffix can ship "
             r"with the legacy silicon \(CSO: DLN\) or the new silicon", "the M3 suffix (Table 8-1)")
    S["m3_p"] = page(t, m)
    m = need(t, r"^\s+TPS73733DCQRM3\s+Active\s+Production\s+SOT-223 \(DCQ\) \| 6", "the order code TPS73733DCQRM3 (addendum)")
    S["code_p"] = page(t, m)
    m = need(t, r"TPS737\s+DCQ \(SOT-223, 6\)\s+([\d.]+)mm × ([\d.]+)mm", "the DCQ package size")
    S["dcq_size"] = F((float(m.group(1)), float(m.group(2))), "PRINTED", "SBVS067W p.%d (package size, nominal, includes pins)" % page(t, m))
    m = need(t, r"When shutdown capability is not required, EN can be connected to VIN\. However, the pass transistor can\s*\npossibly not be discharged",
             "EN connected to VIN (6.3.3)")
    S["en_vin_p"] = page(t, m)
    need(t, r"for VIN ramp times slower than a few\s*\nmilliseconds, the output can overshoot upon power up\.", "the overshoot sentence (6.3.3)")
    m = need(t, r"Foldback current limit helps\s*\nprotect the regulator from damage during output short-circuit conditions by reducing current limit when VOUT\s*\n"
             r"drops below 0\.5 V\.", "the foldback (6.3.2)")
    S["fold_p"] = page(t, m)
    m = need(t, r"Current limit foldback can prevent device start-up under some conditions\.", "the start-up note (6.3.3)")
    S["start_p"] = page(t, m)
    m = need(t, r"Output capacitor\s*\n[^\n]*?must be ³ 1\.0mF\.", "the output capacitor floor (7.2)")
    S["cout_p"] = page(t, m)
    m = need(t, r"Optional input capacitor\.\s*\n\s*May improve source\s+Output capacitor", "the optional input capacitor (7.2)")
    S["cin_p"] = page(t, m)

    # --- TI TLV757P, SBVS322C (screened)
    t = pdf("tlv757p")
    need(t, r"SBVS322C", "the TLV757P sheet's number")
    m = need(t, r"JEDEC\s*$", "the JEDEC block (5.4)")
    m = need(t, r"RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+°C/W\s*\n\s*RθJC\(top\)", "the JEDEC RthJA row (5.4)")
    S["tlv_rja"] = F({"DYD": float(m.group(1)), "DBV": float(m.group(2)), "DRV": float(m.group(3))}, "PRINTED", "SBVS322C 5.4 p.%d (JEDEC 2s2p)" % page(t, m))
    blk = t[t.index("IOUT = 1A,\n", t.index("2.5V ≤ VOUT < 3.3V, DYD package")) - 2000:]
    m = need(blk, r"%s40°C ≤ TJ ≤ \+125°C.*?3\.3V ≤ VOUT < 5\.0V\s+(\d+)\s*\n\s*3\.3V ≤ VOUT < 5\.0V, DYD package\s+(\d+)" % EN_DASH, "the 3.3 V dropout over 125 C", re.S)
    S["tlv_vdo"] = F({"DBV/DRV": float(m.group(1)) / 1000, "DYD": float(m.group(2)) / 1000}, "PRINTED", "SBVS322C 5.5 (maximum at 1 A, -40 to 125 C TJ)")
    m = need(t, r"ICL\s+Output current limit\s+VIN = VOUT \+ VDO\(MAX\) \+ 0\.25V\s+VOUT = 0\.9 x VOUT,\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "TLV757P ICL")
    S["tlv_icl"] = F(tuple(float(x) for x in m.groups()), "PRINTED", "SBVS322C 5.5 p.%d" % page(t, m))
    need(t, r"TLV75733PDYDR", "the order code TLV75733PDYDR")

    # --- TI TPS7A37, SBVS220B (the adjustable alternate)
    t = pdf("tps7a37")
    need(t, r"SBVS220B", "the TPS7A37 sheet's number")
    m = need(t, r"RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)\s+°C/W", "TPS7A37 RthJA (6.4)")
    S["a37_rja"] = F(float(m.group(1)), "PRINTED", "SBVS220B 6.4 p.%d (DRV)" % page(t, m))
    m = need(t, r"VDO\s+IOUT = 1 A\s+(\d+)\s+(\d+)\s+mV", "TPS7A37 dropout (6.5)")
    S["a37_vdo"] = F(float(m.group(2)) / 1000, "PRINTED", "SBVS220B 6.5 p.%d (maximum at 1 A)" % page(t, m))
    m = need(t, r"Tolerance of external resistors not included in this specification\.", "TPS7A37 note 4")
    S["a37_note_p"] = page(t, m)
    need(t, r"TPS7A3701DRVR", "the order code TPS7A3701DRVR")

    # --- Diodes AP63200 series, DS41326 (K1's part, U25's)
    t = pdf("ap63200")
    m = need(t, r"VIN\s+Supply Voltage\s+([\d.]+)\s+(\d+)\s+V", "AP63203's input range (recommended)")
    S["k1_vin"] = F((float(m.group(1)), float(m.group(2))), "PRINTED", "DS41326 Recommended Operating Conditions p.%d" % page(t, m))
    m = need(t, r"VIN Under Voltage Threshold \(Rising\)\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "AP63203's UVLO rising")
    S["k1_uvlo"] = F(tuple(float(x) for x in m.groups()), "PRINTED", "DS41326 Electrical Characteristics p.%d" % page(t, m))
    m = need(t, r"RDS\(ON\)1\s+High-Side Switch On-Resistance \(Note 8\)\s+\S+\s+\S+\s+(\d+)\s+\S+\s+m\S", "AP63203's high-side RDS(on)")
    S["k1_rhs"] = F(float(m.group(1)) / 1000, "TYPICAL", "DS41326 p.%d (typical only, no limit printed)" % page(t, m))
    m = need(t, r"RDS\(ON\)2\s+Low-Side Switch On-Resistance \(Note 8\)\s+\S+\s+\S+\s+(\d+)\s+\S+\s+m\S", "AP63203's low-side RDS(on)")
    S["k1_rls"] = F(float(m.group(1)) / 1000, "TYPICAL", "DS41326 p.%d (typical only)" % page(t, m))
    m = need(t, r"IPEAK_LIMIT\s+HS Peak Current Limit \(Note 8\)\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "AP63203's peak limit")
    S["k1_ipk"] = F(tuple(float(x) for x in m.groups()), "PRINTED", "DS41326 p.%d (min / typ / max, Note 8)" % page(t, m))
    m = need(t, r"θJA\s+Junction to Ambient\s+TSOT26\s+(\d+)\s+°C/W", "AP63203's theta JA")
    S["k1_rja"] = F(float(m.group(1)), "PRINTED", "DS41326 p.%d" % page(t, m))
    m = need(t, r"If Q1 consistently hits the peak current limit for (\d+)ms, the buck converter enters hiccup mode and shuts\s*\n"
             r"down\. After (\d+)ms of off time, the buck converter restarts powering up\.", "AP63203's hiccup")
    S["k1_hiccup"] = F((float(m.group(1)) / 1000, float(m.group(2)) / 1000), "DESCRIBED", "DS41326 p.%d (the description, no min or max)" % page(t, m))
    m = need(t, r"Figure 4\. Efficiency vs\. Output Current, VIN = 12V", "AP63200's efficiency curve (typical)")
    S["k1_eff_p"] = page(t, m)
    return S


# ------------------------------------------------------------------------------------------------------- the arithmetic
def band_row(row, eq, tol):
    """W135's: a tested row at its nominal resistor, the resistor's tolerance through the equations' exponents (MODEL on PRINTED)."""
    return row[0] * (1 + tol) ** -eq["min"][1], row[2] * (1 - tol) ** -eq["max"][1]


def band_of(r_k, S):
    """the limiter's band for a resistor value: the tested row when it is 49.9 kOhm, else the maker's equations (both with the 1 %)"""
    eq = S["ios_eq"][0]
    if abs(r_k - R_ILIM) < 1e-9:
        return band_row(S["ios49"][0], eq, R_TOL)
    (cmin, emin), (cmax, emax) = eq["min"], eq["max"]
    return cmin / (r_k * (1 + R_TOL)) ** emin / 1000.0, cmax / (r_k * (1 - R_TOL)) ** emax / 1000.0


def path(E, P, DP, G):
    """record l9t5's supply path, exactly as T10 and W135 compute it: avail(i_self, i_lead, r_ser) at the LDO's input"""
    lo14, nom14, hi14 = T.CHK.vout_band(T.R601, T.R602_SET)
    r_sup = G["rhot"] + 2 * DP["vh_r"][1]
    fixed = lo14 - D.RAIL_BUDGET * nom14 - G["shift_drawn_ub"]
    return (lambda i_self, i_lead, r_ser: fixed - i_lead * r_sup - r_ser * i_self), (lo14, nom14, hi14), r_sup, fixed


def need_ap(P, i):
    """T10-A3's requirement for the AP2112, exactly as T10 writes it (the dropout INFERRED between its printed points)"""
    d = P["drop"][10] + (P["drop"][300] - P["drop"][10]) * (i - 0.01) / 0.29 if i <= 0.3 else P["drop"][300] + (P["drop"][600] - P["drop"][300]) * (i - 0.3) / 0.3
    return 3.3 * (P["vout_hi"] + P["load"] * i) + d


def need_reg(reg, i):
    """T10-A3's requirement for a regulator of this record: its PRINTED output maximum plus its dropout at i, INFERRED as the PRINTED
    maximum at 1 A times i / 1 A (VDO_SCALE)"""
    return 3.3 * (1 + reg["acc"][0]) + reg["vdo1a"][0] * i


# ----------------------------------------------------------------------------------------------------- 8. the acceptance judge
def judge(st, R):
    """The selected stage's electrical acceptance on its rows. st: {name: (value, label, where)}; a figure used as a LIMIT must carry an
    admitted label (ADMIT), the dropout's scaling the only declared INFERRED step; one that does not FAILS the judge at J0 (the figure
    is refused, whatever its value). Returns (verdict, [(criterion, holds, text)]).
    Criteria: J1 no served state limited (IOSmin over every served peak); J2 the regulator at 125 C or less at the limiter's maximum
    from the corner; J3 the limiter's own junction in service at its maximum; J4 T10-A3 at the limiter's maximum on all three; J5 the
    regulator rated for the limiter's maximum (output, current limit, input); J6 the output short bounded (a printed timer and latch,
    and the regulator's printed short-circuit duration); J7 three limiters at their maximum inside U601's and the lead's ratings."""
    bad = [k for k in ("ios_lo", "ios_hi", "rja", "vdo1a", "acc", "iout", "icl_min", "vin_max", "t_latch", "lim_rja", "ron")
           if st[k][1] not in ADMIT]
    if bad:
        return "FAILS", [("J0", False, "REFUSED: a limit carried a non-admitted label: %s" % ", ".join(
            "%s %s (%s)" % (k, st[k][0], st[k][1]) for k in bad))]
    lo, hi = st["ios_lo"][0], st["ios_hi"][0]
    res = []
    peak = max(R["served"].values())
    res.append(("J1", lo >= peak, "IOSmin %.4f A against the largest served peak %.4f A (%s): %+.4f A" % (lo, peak, max(R["served"], key=R["served"].get), lo - peak)))
    tj = R["air"] + st["rja"][0] * R["drop"] * hi
    res.append(("J2", tj <= R["tj"], "regulator junction %.1f C at %.4f A on %.1f C/W (%s) from the corner drop %.4f V, output in regulation, against %.0f C" % (
        tj, hi, st["rja"][0], st["rja"][1], R["drop"], R["tj"])))
    tjl = R["air"] + st["lim_rja"][0] * st["ron"][0] * hi * hi
    res.append(("J3", tjl <= R["tj"], "limiter junction %.1f C at %.4f A (%.3f ohm, %.1f C/W) in service" % (tjl, hi, st["ron"][0], st["lim_rja"][0])))
    at = R["avail"](hi, 3 * hi, st["ron"][0])
    nd = 3.3 * (1 + st["acc"][0]) + st["vdo1a"][0] * hi
    res.append(("J4", at >= nd, "T10-A3 at %.4f A on all three: %.4f V against %.4f V (output %.4f V PRINTED, dropout %.4f V INFERRED from %.3f V at 1 A): %+.4f V" % (
        hi, at, nd, 3.3 * (1 + st["acc"][0]), st["vdo1a"][0] * hi, st["vdo1a"][0], at - nd)))
    res.append(("J5", st["iout"][0] >= hi and st["icl_min"][0] >= hi and st["vin_max"][0] >= R["hi14"],
                "rated output %.2f A, current limit at least %.2f A, input to %.2f V, against %.4f A and the pre-regulator's top %.4f V" % (
                    st["iout"][0], st["icl_min"][0], st["vin_max"][0], hi, R["hi14"])))
    e = R["hi14"] * hi * st["t_latch"][0]
    res.append(("J6", st["t_latch"][0] > 0 and st["short"][0] == "Indefinite",
                "a short drawing the limit latches within %.0f ms (%.1f mJ at most, MODEL); the regulator's output short-circuit duration %s (%s)" % (
                    st["t_latch"][0] * 1e3, e * 1e3, st["short"][0], st["short"][1])))
    res.append(("J7", 3 * hi <= R["u601"] and 3 * hi <= R["vh"], "three limiters at their maximum %.4f A against U601's %.0f A and the lead's %.0f A" % (
        3 * hi, R["u601"], R["vh"])))
    return ("HOLDS" if all(h for _c, h, _t in res) else "FAILS"), res


# ------------------------------------------------------------------------------------------------------- 9. the netlist reading
LIM_PINS = {"1": "+5V_IOC", "2": "GND", "3": "IOC%s_LIM_EN", "5": "IOC%s_ILIM", "6": "IOC%s_LDO_IN"}
REG_PINS = {"1": "IOC%s_LDO_IN", "2": "+3V3_IOC%s", "3": "GND", "5": "IOC%s_LDO_EN", "6": "GND"}


def regstage_check(nl, S):
    """the draft read on a board B netlist by pin and value. Returns (verdict, why)."""
    why = []
    for tag, k in (("A", 0), ("B", 1), ("C", 2)):
        u_reg, u_lim = "U%d" % (40 + 10 * k), "U%d" % (45 + 10 * k)
        r_ilim, r_en, r_ldoen = "R%d" % (601 + 20 * k), "R%d" % (602 + 20 * k), "R%d" % (66 + 12 * k)
        c_in, c_lim = "C%d" % (400 + 20 * k), "C%d" % (940 + 10 * k)
        ldo_in, ldo_en = "IOC%s_LDO_IN" % tag, "IOC%s_LDO_EN" % tag
        why += CHK.rows(nl, [(u_lim, p, n % tag if "%s" in n else n) for p, n in LIM_PINS.items()])
        why += CHK.rows(nl, [(u_reg, p, n % tag if "%s" in n else n) for p, n in REG_PINS.items()])
        if not CHK.value(nl, u_reg).startswith("TPS73733DCQRM3"):
            why.append("%s is %r, not the TPS73733DCQRM3 (new silicon only)" % (u_reg, CHK.value(nl, u_reg)[:30]))
        if not CHK.value(nl, u_lim).startswith("TPS2553-1"):
            why.append("%s is %r, not the TPS2553-1 (latch-off)" % (u_lim, CHK.value(nl, u_lim)[:30]))
        if CHK.two(nl, r_ilim) != sorted(["IOC%s_ILIM" % tag, "GND"]):
            why.append("%s on %s, wanted ILIM to GND" % (r_ilim, CHK.two(nl, r_ilim)))
        else:
            try:
                rk = CHK.kohm(CHK.value(nl, r_ilim)) / 1e3
            except (ValueError, IndexError):
                rk = float("nan")
            lo, hi = band_of(rk, S) if rk == rk else (0.0, 0.0)
            want = band_of(R_ILIM, S)
            if abs(lo - want[0]) > 1e-9 or abs(hi - want[1]) > 1e-9:
                why.append("%s is %r: IOS %.4f to %.4f A, not the selected %.4f to %.4f A" % (r_ilim, CHK.value(nl, r_ilim), lo, hi, want[0], want[1]))
        if CHK.two(nl, r_en) != sorted(["+5V_IOC", "IOC%s_LIM_EN" % tag]):
            why.append("%s on %s, wanted +5V_IOC to the limiter's EN" % (r_en, CHK.two(nl, r_en)))
        if CHK.two(nl, r_ldoen) != sorted([ldo_in, ldo_en]):
            why.append("%s on %s, wanted the LDO's input to its EN" % (r_ldoen, CHK.two(nl, r_ldoen)))
        if CHK.two(nl, c_in) != sorted([ldo_in, "GND"]) or CHK.two(nl, c_lim) != sorted(["+5V_IOC", "GND"]):
            why.append("%s on %s and %s on %s" % (c_in, CHK.two(nl, c_in), c_lim, CHK.two(nl, c_lim)))
        if sorted(CHK.members(nl, ldo_in)) != sorted(["%s.1" % u_reg, "%s.6" % u_lim, "%s.1" % c_in, "%s.1" % r_ldoen]):
            why.append("%s reaches %s, not the LDO, the limiter's OUT, the input capacitor and the EN pull-up alone" % (ldo_in, CHK.members(nl, ldo_in)))
        if sorted(m.split(".")[0] for m in CHK.members(nl, ldo_en)) != sorted([u_reg, r_ldoen, "J_IOCOFF_%s" % tag]):
            why.append("%s reaches %s" % (ldo_en, CHK.members(nl, ldo_en)))
        for gone in ("R%d" % (600 + 20 * k), "U%d" % (46 + 10 * k), "C%d" % (941 + 10 * k), "C%d" % (942 + 10 * k)):
            if gone in nl["pins"] or gone in nl["comps"]:
                why.append("%s, a part of round 6's rail trip, is still drawn" % gone)
    return ("FAIL" if why else "DRAWN"), why


def set_value(path, d, tag, ref, value):
    raw = open(path, encoding="utf-8").read()
    m = re.search(r'\(comp \(ref "%s"\) \(value "([^"]*)"\)' % re.escape(ref), raw)
    if not m:
        refuse("the value mutation's part %s is not in the netlist" % ref)
    raw = raw[:m.start(1)] + value + raw[m.end(1):]
    p = os.path.join(d, tag + ".net")
    open(p, "w", encoding="utf-8").write(raw)
    return p


def pins_by_ref(nl):
    return {r: dict(p) for r, p in nl["pins"].items()}


def changed(a, b):
    """(refs whose pins or value differ, nets whose members differ) between two netlists"""
    ra = set(a["pins"]) | set(a["comps"])
    rb = set(b["pins"]) | set(b["comps"])
    refs = {r for r in ra | rb if a["pins"].get(r) != b["pins"].get(r) or CHK.value(a, r) != CHK.value(b, r)}
    na = {}
    nb = {}
    for nl, acc in ((a, na), (b, nb)):
        for r, d in nl["pins"].items():
            for p, n in d.items():
                acc.setdefault(n, set()).add("%s.%s" % (r, p))
    nets = {n for n in set(na) | set(nb) if na.get(n) != nb.get(n)}
    return refs, nets


# ------------------------------------------------------------------------------------------------------------------- main
def main():
    out = []
    w = out.append
    E, IO, FP, W = rows(), ioha(), floor_plan(), w135()
    S = sheets()
    P, DP, G = T.figures(), D.figures(), D.gndret()
    avail, (lo14, nom14, hi14), r_sup, fixed = path(E, P, DP, G)
    air, tjg = E["air"][0], T.TJ_GOAL
    drop = hi14 - 3.3 * P["vout_lo"]
    if abs(drop - E["drop"][0]) > 5e-5 or abs(air - P["air"]) > 1e-9 or abs(P["theta_ldo"] - E["theta"][0]) > 1e-9:
        refuse("the corner, the air or the AP2112K's row no longer reproduce from record l9t5's modules as its output prints them")
    a3_repro = (need_ap(P, E["a3_i"][0]), avail(E["a3_i"][0], 3 * E["a3_i"][0], 0.3 * 1.01))
    if abs(a3_repro[0] - E["a3_need"][0]) > 5e-5 or abs(a3_repro[1] - E["a3_at"][0]) > 5e-5:
        refuse("T10-A3 no longer reproduces from record l9t5's modules as its output prints it")
    s_v = {f: v[0] for f, v in E["held"].items()}
    share, dom = E["share"][0], P["can_dom_hi"]
    s3p = {f: s_v[f] - share + dom for f in ("B1", "B2", "B3", "B4", "B5")}     # W135-3: the healthy fabric's transceiver dominant in the same bit
    served = {"S1 the largest sustained served state": E["s1"][0], "S2 both transceivers dominant (normal service's peak)": E["bab_v"][0],
              "(f1) one fabric faulted, the 180 mA row (round 4's cover)": E["f1"][0]}
    served.update({"S3' %s with the healthy fabric's bit" % f: v for f, v in s3p.items()})
    lo1, hi1 = band_of(R_ILIM, S)
    i125 = lambda theta: (tjg - air) / (theta * drop)                       # noqa: E731
    theta_need = (tjg - air) / (drop * hi1)
    reproduced = (abs(i125(P["theta_ldo"]) - W["i125"]) < 5e-5 and abs(max(s3p.values()) - W["s3p"]) < 5e-5 and abs(lo1 - W["ios"][0]) < 5e-5
                  and abs(hi1 - W["ios"][1]) < 5e-5 and abs(round(theta_need, 1) - W["theta_need"]) < 1e-9
                  and abs(avail(hi1, 3 * hi1, S["ron"][0]) - W["a3"][0]) < 5e-5 and abs(need_ap(P, hi1) - W["a3"][1]) < 5e-5)
    if not reproduced:
        refuse("W135's figures (inputs/%s) no longer reproduce from record l9t5's modules and the makers' rows" % os.path.basename(DOCS["lim_out"]))
    R = dict(air=air, tj=tjg, drop=drop, served=served, avail=avail, hi14=hi14, u601=E["u601"][0], vh=E["vh"][0])

    w("l4reg_compare: Layer 4 task L4A-56 re-scoped by W135's CHANGE-METHOD (RE-6, RE-7): the supervisors' regulator stage; three approaches")
    w("compared, the SESSION selection and its draft on board B (MESHSAT-1357, W138, 7 October 2026)")
    w("prototype design; nothing built, bought, powered or measured; nothing applied to the tree; it closes no cx46 item and moves no state")
    w("(cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand); the selection is a desk design on printed figures, unchecked")
    w("")
    w("1. INPUTS, pinned by sha256")
    for rel in [T10_OUT] + list(DOCS.values()):
        w("   %s %s%s" % (sha(rel), rel, ("  (copy of %s)" % SOURCES[[k for k, v in DOCS.items() if v == rel][0]]) if rel in (DOCS["lim_page"], DOCS["lim_out"], DOCS["canmb"]) else ""))
    for key in ("tps737", "tlv757p", "tps7a37", "tps2553", "ap63200"):
        w("   %s %s%s" % (sha(SHEET[key]), SHEET[key], "  (held back; %s)" % DOCS["fetch"] if PT.held(SHEET[key]) else ""))
    for t_rel, digest, held in PT.inputs(ROOT, PDFTEXT):
        w("   %s %s%s" % ((digest or "ABSENT          ")[:16], t_rel, "  (held back with its sheet)" if held else ""))
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 2
    w("2. THE ROWS, from record l9t5's T10 output (%s; line numbers of that file), revision V (fitted, L9T5-D7), the 14.0k set point" % T10_OUT)
    w("   the corner: inside air %.2f C (line %d); the pre-regulator %.4f to %.4f V, the LDO's least output %.4f V, its worst drop %.4f V (line %d);" % (
        air, E["air"][1], lo14, hi14, 3.3 * P["vout_lo"], drop, E["drop"][1]))
    w("   criterion 125 C for every sustained state, 150 C the absolute maximum and never an operating target (the owner's part 22, T10's)")
    w("   the states the design serves, each regulator's total (controller, auxiliaries, both transceivers; MODEL on PRINTED rows, T10's):")
    for lab, v in served.items():
        w("     %-62s %.4f A" % (lab, v))
    w("     (S1 line %d; S2 line %d; (f1) line %d; S3' = T10's held rev V rows, lines %d to %d, less the %.4f A share plus the %.3f A dominant row, W135-3)" % (
        E["s1"][1], E["bab_v"][1], E["f1"][1], E["held"]["B1"][1], E["held"]["B5"][1], share, dom))
    w("   the TCAN334's bus-fault row: %.0f mA a transceiver, PRINTED (SLLSEQ7F 5.5; T10 line %d), inside (f1)" % (E["can_fault"][0], E["can_fault"][1]))
    w("   the fault rows the design must survive (IOHA row 8, 'nothing moves'): (f2) %.4f A (line %d), rev V held %.4f A (line %d)" % (
        E["f2"][0], E["f2"][1], E["both_v"][0], E["both_v"][1]))
    w("   IOHA (%s): row 3 '%s' (line %d); row 7 '%s' (line %d); row 8 '%s' (line %d)" % (
        DOCS["ioha"], IO["row3"][0], IO["row3"][1], IO["row7"][0], IO["row7"][1], IO["row8"][0][:60] + "...", IO["row8"][1]))
    w("   HO-E for reference: the H743 reaches its 105 C VOS0 limit from %.4f A (line %d, MODEL), its own 125 C at %.3f A (line %d, MODEL on its PRINTED 45 C/W)" % (
        E["vos0"][0], E["vos0"][1], E["mcu125"][0], E["mcu125"][1]))
    w("   W135's figures reproduced from record l9t5's modules and the makers' rows (its output copied, %s):" % DOCS["lim_out"])
    w("     the AP2112K's 125 C current %.4f A; S3' largest %.4f A; TPS2553-1 at 49.9 kOhm IOS %.4f to %.4f A; theta at most %.1f C/W; T10-A3 %.4f V" % (
        i125(P["theta_ldo"]), max(s3p.values()), lo1, hi1, theta_need, avail(hi1, 3 * hi1, S["ron"][0])))
    w("     against %.4f V on the AP2112's rows: %s" % (need_ap(P, hi1), "EQUAL to W135's printed figures" if reproduced else "DIFFERENT"))
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 3
    w("3. THE MAKERS' ROWS READ (each with its label, page and table)")
    for k in ("ios49", "ios_eq", "ron", "tlatch", "lim_rja", "lim_iout", "tr", "tios", "dbv_body"):
        v, lab, where = S[k]
        w("   TPS2553-1 %-9s %-38s %-8s %s" % (k, str(v)[:38], lab, where))
    for k in ("rja_new", "rja_leg", "vdo_new", "vdo_new_typ", "vdo_leg", "acc_new", "acc_leg", "acc_head", "icl", "isc", "ignd", "vin", "iout", "tj_op",
              "short_dur", "ven_hi", "ven_lo", "dcq_size"):
        v, lab, where = S[k]
        w("   TPS737    %-11s %-36s %-8s %s" % (k, str(v)[:36], lab, where))
    w("   TPS737    the M3 suffix ships the new silicon only (CSO: RFB); without it legacy (CSO: DLN) or new may ship (Table 8-1, p.%d);" % S["m3_p"])
    w("             TPS73733DCQRM3 is an active order code (Package Option Addendum, p.%d); the DCQ simulation's exposed pad on a %s via array (5.5 note 2, p.%d)" % (
        S["code_p"], S["dcq_vias"][0], S["dcq_vias"][1]))
    w("             'EN can be connected to VIN' with its overshoot note for VIN ramps slower than a few milliseconds (6.3.3, p.%d, DESCRIBED);" % S["en_vin_p"])
    w("             foldback under VOUT 0.5 V (6.3.2, p.%d); 'Current limit foldback can prevent device start-up under some conditions' (6.3.3, p.%d);" % (
        S["fold_p"], S["start_p"]))
    w("             the output capacitor at least 1.0 uF, the input capacitor optional (7.2, p.%d)" % S["cout_p"])
    for k in ("tlv_rja", "tlv_vdo", "tlv_icl"):
        v, lab, where = S[k]
        w("   TLV757P   %-11s %-36s %-8s %s" % (k, str(v)[:36], lab, where))
    for k in ("a37_rja", "a37_vdo"):
        v, lab, where = S[k]
        w("   TPS7A37   %-11s %-36s %-8s %s" % (k, str(v)[:36], lab, where))
    w("   TPS7A37   offered as TPS7A3701 (adjustable), 3721 and 3725 only (no 3.3 V fixed); 'Tolerance of external resistors not included' (p.%d)" % S["a37_note_p"])
    for k in ("k1_vin", "k1_uvlo", "k1_rhs", "k1_rls", "k1_ipk", "k1_rja", "k1_hiccup"):
        v, lab, where = S[k]
        w("   AP63203   %-11s %-36s %-9s %s" % (k, str(v)[:36], lab, where))
    w("   AP63203   efficiency: TYPICAL curves only (Figure 4 on, p.%d; record l9t5: the 5 V input curve NOT PLOTTED); K1's figure %.2f is DECLARED" % (
        S["k1_eff_p"], ETA_K1))
    w("   the AP2112K (record l9t5, DS39724 Rev. 2-2): %.0f C/W SOT25 'no heat sink' PRINTED; dropout 200 / 400 mV at 300 / 600 mA PRINTED; output +-1.5 %%" % P["theta_ldo"])
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 4
    w("4. APPROACH A: THE LIMITER W135 SELECTED WITH A REPLACEMENT REGULATOR FOUND ON PRINTED FIGURES")
    w("   the limiter: TI TPS2553-1 (DBV), RILIM %.1f kOhm 1 %%: IOS %.4f to %.4f A (MODEL: the PRINTED row %.3f to %.3f A, the resistor's 1 %% through" % (
        R_ILIM, lo1, hi1, S["ios49"][0][0], S["ios49"][0][2]))
    w("     the equations' exponents, W135's band); latch-off after %.0f to %.0f ms (PRINTED); response %.0f us TYPICAL only (never used as a limit)" % (
        S["tlatch"][0][0] * 1e3, S["tlatch"][0][2] * 1e3, S["tios"][0] * 1e6))
    w("   the regulator's requirements at the 14.0k corner (W135's, reproduced): junction-to-ambient at most %.1f C/W; output and current limit" % theta_need)
    w("     at least %.4f A; input to at least %.4f V; dropout at %.4f A that keeps T10-A3 with its own output band (below)" % (hi1, hi14, hi1))
    regs = [
        ("AP2112K-3.3 (SOT25), as drawn", P["theta_ldo"], "PRINTED", None, "AP2112: piecewise", P["vout_hi"] - 1, P["imax"], None, 6.0, "ap"),
        ("TPS73733DCQRM3 (SOT-223, new silicon)", S["rja_new"][0]["DCQ"], "PRINTED", S["vdo_new"][0], "250 mV at 1 A", S["acc_new"][0], S["iout"][0],
         S["icl"][0][0], S["vin"][0][1], "sel"),
        ("TPS73733DCQR (no M3: legacy may ship)", max(S["rja_new"][0]["DCQ"], S["rja_leg"][0]["DCQ"]), "PRINTED", S["vdo_leg"][0], "500 mV at 1 A",
         S["acc_leg"][0], S["iout"][0], S["icl"][0][0], S["vin"][0][1], "leg"),
        ("TPS73701DRBRM3 (VSON-8, adjustable, M3)", S["rja_new"][0]["DRB"], "PRINTED", S["vdo_new"][0], "250 mV at 1 A", S["acc_new"][0] + 0.002, S["iout"][0],
         S["icl"][0][0], S["vin"][0][1], "drb"),
        ("TLV75733PDYDR (SOT-23-5 DYD)", S["tlv_rja"][0]["DYD"], "PRINTED", S["tlv_vdo"][0]["DYD"], "500 mV at 1 A", 0.015, 1.0, S["tlv_icl"][0][0], 5.5, "tlv"),
        ("TLV75733PDRVR (WSON-6 DRV)", S["tlv_rja"][0]["DRV"], "PRINTED", S["tlv_vdo"][0]["DBV/DRV"], "475 mV at 1 A", 0.015, 1.0, S["tlv_icl"][0][0], 5.5, "tlv2"),
        ("TPS7A3701DRVR (WSON-6, adjustable)", S["a37_rja"][0], "PRINTED", S["a37_vdo"][0], "200 mV at 1 A", 0.010 + 0.002, 1.0, S["icl"][0][0], 5.5, "a37"),
    ]
    w("   the regulators read, each at the limiter's maximum %.4f A from the corner (MODEL on the PRINTED rows; the dropout INFERRED linear from 1 A):" % hi1)
    w("     %-42s %7s %9s %9s %10s %10s  %s" % ("part", "C/W", "TJ (C)", "VDO (V)", "A3 need", "A3 margin", "verdict"))
    at_hi = avail(hi1, 3 * hi1, S["ron"][0])
    reg_rows = {}
    for name, rja, _lab, vdo1, _vdo_t, acc, iout, iclmin, vinmax, key in regs:
        tj = air + rja * drop * hi1
        if key == "ap":
            nd = need_ap(P, hi1)
            vdo = nd - 3.3 * (P["vout_hi"] + P["load"] * hi1)
        else:
            vdo = vdo1 * hi1
            nd = 3.3 * (1 + acc) + vdo
        ok = tj <= tjg and at_hi >= nd and iout >= hi1 and (iclmin is None or iclmin >= hi1) and vinmax >= hi14
        reg_rows[key] = (name, tj, nd, at_hi - nd, ok, rja)
        w("     %-42s %7.1f %9.1f %9.4f %10.4f %+10.4f  %s" % (name, rja, tj, vdo, nd, at_hi - nd, "QUALIFIES" if ok else "FAILS"))
    w("     (the supply at the LDO's input at %.4f A on all three: %.4f V, record l9t5's path with the limiter's %.3f ohm PRINTED; the adjustable parts carry" % (
        hi1, at_hi, S["ron"][0]))
    w("     a 0.1 % divider's 0.2 % beside the maker's band, an ASSUMPTION: their sheets exclude the resistors; TLV757P's band is printed at 1 mA only)")
    sel = reg_rows["sel"]
    w("   SELECTED within A: TPS73733DCQRM3. Its junction at the limiter's maximum %.1f C (%.1f K under 125 C; it holds to %.1f C/W, %.0f %% over the" % (
        sel[1], tjg - sel[1], theta_need, 100 * (theta_need / sel[5] - 1)))
    w("     printed %.1f C/W); the M3 order code fixes the new silicon, whose dropout and band qualify where the legacy silicon's do not" % sel[5])
    w("     the alternate within A: TPS73701DRBRM3 (VSON-8 3 x 3 mm, %.1f C/W) with a 0.1 %% divider, if board B's pocket refuses the SOT-223" % S["rja_new"][0]["DRB"])
    # the rows, for the selected regulator
    REG = dict(acc=S["acc_new"], vdo1a=S["vdo_new"], rja=(S["rja_new"][0]["DCQ"], "PRINTED", S["rja_new"][2]))
    w("   A, row by row (the selected pair; MODEL on PRINTED unless labelled):")
    w("   (1) THE WINDOW: IOSmin %.4f A over every served state (largest S3' %.4f A: %+.4f A; (f1) %.4f A: %+.4f A; S2 %.4f A; S1 %.4f A): no served" % (
        lo1, max(s3p.values()), lo1 - max(s3p.values()), E["f1"][0], lo1 - E["f1"][0], E["bab_v"][0], E["s1"][0]))
    w("       state is limited, so no bridging capacitance and no timer restart is relied on; the TCAN334's %.0f mA row is inside (f1). Row 8's" % E["can_fault"][0])
    w("       (f2) %.4f A and rev V's held %.4f A lie inside the band (%.4f to %.4f A): a supervisor there MAY be limited and latched off after" % (
        E["f2"][0], E["both_v"][0], lo1, hi1))
    w("       %.0f to %.0f ms, before FW-B21's 100 ms response; row 8's accepted outcome ('nothing moves', the voters at the home assignment) is" % (
        S["tlatch"][0][0] * 1e3, S["tlatch"][0][2] * 1e3))
    w("       the same with it, and the supervisor returns only when EN or power is cycled (a new failure mode, (7))")
    w("   (2) THE REGULATOR'S JUNCTION at %.2f C air on its PRINTED %.1f C/W: at the limiter's maximum %.4f A, %.1f C (holds 125 C for every waveform" % (
        air, REG["rja"][0], hi1, sel[1]))
    w("       under the limit: a constant-power bound, the cx46 countermodel's periodic peaks included); at S1 %.4f A, %.1f C; the realisation of the" % (
        E["s1"][0], air + REG["rja"][0] * drop * E["s1"][0]))
    w("       printed figure on board B's copper is a Layer 10 means (JEDEC 2s2p, %s vias under the tab): read at E-17's coupon, never assumed" % S["dcq_vias"][0])
    tjl = air + S["lim_rja"][0] * S["ron"][0] * hi1 ** 2
    w("       its ground current (%.0f uA TYPICAL at 1 A, no maximum printed) is outside the bound: %.1f mW at the top input, %.2f K on the printed" % (
        S["ignd"][0] * 1e6, hi14 * S["ignd"][0] * 1e3, REG["rja"][0] * hi14 * S["ignd"][0]))
    w("       theta (MODEL on a TYPICAL), against the %.1f K margin" % (tjg - sel[1]))
    w("       the limiter's own junction in service at %.4f A: %.1f C (%.3f ohm, %.1f C/W, PRINTED); its continuous rating %.1f A to 125 C TJ PRINTED" % (
        hi1, tjl, S["ron"][0], S["lim_rja"][0], S["lim_iout"][0]))
    e_short = hi14 * hi1 * S["tlatch"][0][2]
    w("   (3) THE OUTPUT SHORT: (i) a short above the regulator's foldback draws the limit and latches within %.0f ms (PRINTED): at most %.1f mJ (MODEL);" % (
        S["tlatch"][0][2] * 1e3, e_short * 1e3))
    w("       (ii) a hard short folds the TPS737 back to its own short-circuit current, %.3f A TYPICAL only, which may sit under IOSmin: the limiter" % S["isc"][0])
    w("       may not act; W135-2's exclusion carried (SESSION W138-3): the supervisor on a shorted rail is lost (IOHA row 3), the other two keep")
    w("       their supply (each branch at most IOSmax), and the regulator's survival rests on its PRINTED 'Output short-circuit duration: %s'" % S["short_dur"][0])
    w("       (SBVS067W 5.1), not on a typical shutdown; its junction during (i) is not computed (no transient thermal impedance printed)")
    w("       the same exclusion covers a partial short on the supervisor's own 3.3 V that pulls its output out of regulation while drawing under")
    w("       IOSmin (the drop then exceeds the corner's): (2)'s bound is stated for the output in regulation, every served state's case")
    A3 = {}
    A3["a"] = (avail(E["a3_i"][0], 3 * E["a3_i"][0], S["ron"][0]), need_reg(REG, E["a3_i"][0]))
    A3["b"] = (at_hi, need_reg(REG, hi1))
    A3["c"] = (avail(E["s1"][0], hi1 + 2 * E["s1"][0], S["ron"][0]), need_reg(REG, E["s1"][0]))
    s3m = max(s3p.values())
    A3["e"] = (avail(s3m, 3 * s3m, S["ron"][0]), need_reg(REG, s3m))
    w("   (4) T10-A3 with the limiter's %.3f ohm and the TPS737's PRINTED band (+%.1f %%) and dropout (%.3f V at 1 A, INFERRED linear):" % (
        S["ron"][0], 100 * REG["acc"][0], REG["vdo1a"][0]))
    for k, lab in (("a", "at T10's point %.4f A on all three" % E["a3_i"][0]), ("b", "at the limiter's maximum %.4f A on all three" % hi1),
                   ("c", "S1 %.4f A at the other two, one at the limiter's maximum" % E["s1"][0]), ("e", "S3' %.4f A on all three in one bit" % s3m)):
        w("       (%s) %-50s %.4f V against %.4f V: %+.4f V, %s" % (k, lab, A3[k][0], A3[k][1], A3[k][0] - A3[k][1], "holds" if A3[k][0] >= A3[k][1] else "FAILS"))
    keep = avail(hi1, 3 * hi1, S["ron"][0] + 0.3 * 1.01)
    w("       (f) with round 6's 0.3 ohm sense (+1 %%) kept in series, at the limiter's maximum: %.4f V against %.4f V: %+.4f V, %s (SESSION W138-2)" % (
        keep, need_reg(REG, hi1), keep - need_reg(REG, hi1), "holds" if keep >= need_reg(REG, hi1) else "FAILS"))
    w("       (d) U601 and the lead's pin 1 at three maxima: %.4f A against %.0f A and %.0f A (PRINTED, T10 line %d): %s" % (
        3 * hi1, E["u601"][0], E["vh"][0], E["u601"][1], "holds" if 3 * hi1 <= E["u601"][0] else "FAILS"))
    head = 3.3 * (1 + REG["acc"][0]) + S["acc_head"][0]
    w("       the band's own condition: the TPS737's +-%.1f %% is PRINTED for VIN >= VOUT + %.1f V (5.6); the input here is %.4f to %.4f V at the served" % (
        100 * REG["acc"][0], S["acc_head"][0], A3["e"][0], fixed))
    w("       currents, under %.4f V: the band between VOUT + VDO and VOUT + 0.5 V is INFERRED (the AP2112's was tested at 4.3 V, T10's same gap):" % head)
    w("       V-T10-DROP extended (finding L4REG-F2)")
    w("   (5) PARTS AND AREA (MODEL on the makers' package outlines; board B's floor plan gen_pcb_b3.py):")
    AREA = {"SOT223": S["dcq_size"][0][0] * S["dcq_size"][0][1], "SOT23": 2.9 * 2.8, "0603": 1.6 * 0.8, "0805": 2.0 * 1.25, "XAL4020": 4.0 * 4.0}
    a_guard = 2.0 * 1.25 + AREA["SOT23"] * 2 + AREA["0603"] * 4 + AREA["0603"]           # R600 0805, U45, U46, R601, R602, C941, C942, C940
    a_A_vs_base = (AREA["SOT223"] - AREA["SOT23"]) + AREA["SOT23"] + 3 * AREA["0603"]       # the LDO's growth; U45, C940, R601, R602
    a_A_vs_guard = a_A_vs_base - a_guard
    a_K1 = AREA["XAL4020"] + AREA["0603"] + (AREA["0805"] - AREA["0603"]) + 2 * AREA["0805"]  # L, BST, 10u for 1u in, two 22u out; TSOT for SOT25
    pk = FP["IOCB"][1]
    w("       per supervisor, A against the tree: the LDO's land %.1f to %.1f mm2 and one SOT-23-6 with two 0603 resistors and one 0603 capacitor:" % (
        AREA["SOT23"], AREA["SOT223"]))
    w("       %+.1f mm2; against round 6's drafted state (the rail trip's eight parts, %.1f mm2, removed): %+.1f mm2. Pocket IOCB/IOCC %.0f mm2 (gen_pcb_b3.py" % (
        a_A_vs_base, a_guard, a_A_vs_guard, pk))
    w("       line %d), IOHA's estimate about %.0f mm2 a controller (line %d): %.1f %% of the pocket, %.1f %% of the estimate; placement is Layer 10's" % (
        FP["IOCB"][2], IO["per_ctrl"][0], IO["per_ctrl"][1], 100 * a_A_vs_base / pk, 100 * a_A_vs_base / IO["per_ctrl"][0]))
    w("       (the region lists carry no part of any P0 draft yet, round 6's included: finding L4REG-F6). Parts: two ICs and three passives a")
    w("       supervisor in place of round 6's two ICs and six passives; order codes owed (finding L4REG-F4)")
    w("   (6) HO-E: unchanged by A. The H743's VOS0 105 C current %.4f A and its 125 C current %.3f A depend on its own %.0f C/W and the air, not" % (
        E["vos0"][0], E["mcu125"][0], P["theta_mcu"]))
    w("       on the regulator; IOSmin %.4f A sits over both, so no current limit of this stage holds the controller (W127 finding 2, L4A-59):" % lo1)
    w("       the largest served S1 %.4f A against VOS0's %.4f A is a %.1f %% band no limiter's printed tolerance reaches; A neither narrows nor widens it" % (
        E["s1"][0], E["vos0"][0], 100 * (E["vos0"][0] / E["s1"][0] - 1)))
    w("   (7) NEW FAILURE MODES: a latched limiter (row 8, or any overload over IOSmin for 5 ms) leaves its supervisor dark until EN or power is")
    w("       cycled (nothing in this draft drives EN: the peers' restart is L4A-54's or L4A-58's, finding L4REG-F3); the limiter's latent loss of")
    w("       its limit (HO-D, L4A-58: FAULT asserts only while limiting); the legacy silicon fitted under a code without M3 (T10-A3 then fails at")
    w("       the limiter's maximum: Layer 6 and Layer 12 identity rows, finding L4REG-F4); the TPS737's start-up into foldback and its overshoot")
    w("       note (DESCRIBED; INFERRED not triggered: the limiter's output rises within %.1f ms PRINTED at its test load, the start-up load is the" % (S["tr"][0] * 1e3))
    w("       controller in reset; first-article items, finding L4REG-F2); and the given-up average bound of round 6's rail trip on the controller's")
    w("       own current (%.4f to %.4f A, PROVISIONAL, its response withdrawn): a firmware outside FW-B20 is bounded by no hardware (finding L4REG-F7)" % E["trip"][0])
    vA, rA = judge(dict(ios_lo=(lo1, "PRINTED", "row"), ios_hi=(hi1, "PRINTED", "row"), rja=REG["rja"], vdo1a=REG["vdo1a"], acc=REG["acc"],
                        iout=S["iout"], icl_min=(S["icl"][0][0], "PRINTED", S["icl"][2]), vin_max=(S["vin"][0][1], "PRINTED", S["vin"][2]),
                        t_latch=(S["tlatch"][0][2], "PRINTED", S["tlatch"][2]), lim_rja=S["lim_rja"], ron=S["ron"], short=S["short_dur"]), R)
    w("   A's verdict on its rows: %s (the judge of section 8)" % vA)
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 5
    w("5. APPROACH B: K1, A BUCK PER SUPERVISOR (board B's AP63203WU-7, as U25; record l9t5 T10 section 8)")
    k1_vmin = S["k1_vin"][0][0]
    w("   (1) THE INPUT: the AP63203's recommended input starts at %.1f V (PRINTED), UVLO rising %.2f to %.2f V; at the 14.0k set point its input" % (
        k1_vmin, S["k1_uvlo"][0][0], S["k1_uvlo"][0][2]))
    w("       is at most %.4f V even with no current (the pre-regulator's least %.4f V, the rail's budget and the return's shift): UNDER the" % (fixed, lo14))
    w("       recommended range. K1 needs R602 back to 10.7 k (I-03's 4.87 to 5.13 V band): board A's iocpre and iocset withdrawn, Slot A's")
    w("       L9T5-D9 reversed, a cross-board change")
    p_s = 3.3 * s3m
    loss = p_s * (1 / ETA_K1 - 1)
    w("   (2) THE THERMAL: the AP63203 prints %.0f C/W (PRINTED) but no maximum on-resistance (%.0f and %.0f mOhm TYPICAL, Note 8) and no guaranteed" % (
        S["k1_rja"][0], S["k1_rhs"][0] * 1e3, S["k1_rls"][0] * 1e3))
    w("       efficiency (curves only): its loss has no printed bound. On the DECLARED %.2f at S3' %.4f A: %.3f W lost, junction %.1f C (MODEL on a" % (
        ETA_K1, s3m, loss, air + S["k1_rja"][0] * loss))
    w("       TYPICAL: NOT a bound). K1 holds no served state limited (no limit under %.1f A, PRINTED peak minimum), so the window is every row" % S["k1_ipk"][0][0])
    w("   (3) THE OUTPUT SHORT: hiccup, %.0f ms at the peak limit then %.0f ms off (DESCRIBED, no limits), %.1f to %.1f A peak (PRINTED): a periodic" % (
        S["k1_hiccup"][0][0] * 1e3, S["k1_hiccup"][0][1] * 1e3, S["k1_ipk"][0][0], S["k1_ipk"][0][2]))
    w("       waveform of up to %.1f A at the switch drawn from +5V_IOC, shared with the other two: no printed containment per branch without a" % S["k1_ipk"][0][2])
    w("       limiter ahead of it (A's limiter added to K1: the buck's input transients against a latch-off limit, not computed)")
    w("   (4) T10-A3: replaced by the buck's own input range ((1)): FAILS at 14.0k, holds at 10.7 k")
    w("   (5) AREA: %+.1f mm2 a supervisor against the tree (MODEL: XAL4020 inductor, bootstrap, input and two output capacitors; %.1f %% of the" % (
        a_K1, 100 * a_K1 / pk))
    w("       pocket), %+.1f mm2 with A's limiter for containment; switching ripple on each controller's VDD and VDDA, not computed" % (
        a_K1 + AREA["SOT23"] + 3 * AREA["0603"]))
    w("   (6) HO-E: unchanged (no current limit at the controller's currents)")
    w("   (7) NEW FAILURE MODES: the hiccup's periodic waveform; the switch node beside the CAN transceivers and the crystal; board A's set point")
    w("       reversed; the controller's 125 C current %.3f A covered by nothing, as in A" % E["mcu125"][0])
    w("   B's verdict: NOT SUPPORTED ON PRINTED FIGURES (its thermal rests on a TYPICAL efficiency; its input is under the recommended range at the")
    w("     drafted set point; no printed per-branch containment); kept as the fallback W135 named")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 6
    w("6. APPROACH C: THE REGULATOR'S OWN PRINTED CURRENT LIMIT AS THE CONTAINMENT (no separate limiter; one part, no latch)")
    icl = S["icl"][0]
    tjc = air + S["rja_new"][0]["DCQ"] * drop * icl[2]
    tjc_drb = air + S["rja_new"][0]["DRB"] * drop * icl[2]
    w("   the best thermal path read, the TPS737 (%.1f C/W DCQ, %.1f C/W DRB, PRINTED), prints its limit %.2f to %.2f A (5.6): at the limit's maximum" % (
        S["rja_new"][0]["DCQ"], S["rja_new"][0]["DRB"], icl[0], icl[2]))
    w("   the junction reads %.1f C (DCQ) and %.1f C (DRB) from the corner's drop alone (the limit is printed at VOUT 90 %% of nominal, a larger drop):" % (
        tjc, tjc_drb))
    w("   OVER 150 C. A part would need a printed maximum under %.3f A (DRB) with a minimum over S3' %.4f A, a %.1f %% band; and its output short" % (
        i125(S["rja_new"][0]["DRB"]), s3m, 100 * (i125(S["rja_new"][0]["DRB"]) / s3m - 1) / (i125(S["rja_new"][0]["DRB"]) / s3m + 1)))
    w("   rests on a foldback printed TYPICAL only (%.3f A), with no printed timer: unbounded. TLV757P likewise (%.2f to %.2f A, its best %.1f C/W)" % (
        S["isc"][0], S["tlv_icl"][0][0], S["tlv_icl"][0][2], S["tlv_rja"][0]["DYD"]))
    w("   C's verdict: FAILS (2) and (3) on printed figures; not taken")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 7
    w("7. THE COMPARISON AND THE SELECTION")
    w("   row                       A (TPS2553-1 + TPS73733DCQRM3)         B (K1, AP63203 per supervisor)        C (the LDO's own limit)")
    w("   window, served rows       none limited (IOSmin %+.4f A)          none limited                          none limited" % (lo1 - s3m))
    w("   regulator junction        %.1f C at the limit, PRINTED theta      no printed bound (TYPICAL efficiency)  %.1f C at its limit: FAILS" % (sel[1], tjc))
    w("   output short              latch %.0f ms PRINTED; (ii) W138-3      hiccup DESCRIBED; no branch limit      foldback TYPICAL: FAILS" % (S["tlatch"][0][2] * 1e3))
    w("   T10-A3                    %+.4f V at the limit (INFERRED VDO)    FAILS at 14.0k (input range)           as A's regulator" % (A3["b"][0] - A3["b"][1]))
    w("   area a supervisor         %+.1f mm2 (tree), %+.1f mm2 (round 6)    %+.1f mm2 (tree)                       %+.1f mm2 (tree)" % (
        a_A_vs_base, a_A_vs_guard, a_K1, AREA["SOT223"] - AREA["SOT23"]))
    w("   board A                   unchanged (R602 14.0k kept)              R602 back to 10.7 k                    unchanged")
    w("   HO-E                      not covered (L4A-59)                     not covered                            not covered")
    w("   SELECTED (SESSION W138-1): A, TI TPS2553-1 (DBV) at RILIM 49.9 kOhm with TI TPS73733DCQRM3 (SOT-223-6, new silicon only), in place")
    w("     of round 6's rail trip; drafted as apply_gen_sch_b_regstage.py (section 9)")
    w("     authority: SESSION; authority_why: an engineering selection among approaches on printed figures inside the drafted circuit: no")
    w("       requirement, protected class, case row, purchase or publication changes; the owner's ruling of 21 September 2026 leaves it to the")
    w("       session (one option stands after the measurement: B and C fail on printed figures)")
    w("     ruled_by: W138 (Claude), MESHSAT-1357; ruled_on: 7 October 2026; reversed_by: none")
    w("     to reverse: take the alternate within A (TPS73701DRBRM3 with a 0.1 % divider), or B at R602 10.7 k, or W135's second-source limiter")
    w("     END CONDITION: the method ends if E-17's coupon (or the first article) reads the regulator's junction-to-ambient over %.1f C/W at a" % theta_need)
    w("       U40, U50 or U60 site in still air at %.2f C; or V-T10-DROP reads its output outside 3.0 to 3.6 V between VOUT + VDO and VOUT + 0.5 V" % air)
    w("       at up to %.4f A; or two negative independent checks of this selection" % hi1)
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 8
    w("8. THE ACCEPTANCE JUDGE ON THE SELECTED STAGE, AND ITS FAILING MUTATIONS")
    for c, h, t_ in rA:
        w("   %s %-5s %s" % (c, "holds" if h else "FAILS", t_))
    base = dict(ios_lo=(lo1, "PRINTED", "row"), ios_hi=(hi1, "PRINTED", "row"), rja=REG["rja"], vdo1a=REG["vdo1a"], acc=REG["acc"],
                iout=S["iout"], icl_min=(S["icl"][0][0], "PRINTED", S["icl"][2]), vin_max=(S["vin"][0][1], "PRINTED", S["vin"][2]),
                t_latch=(S["tlatch"][0][2], "PRINTED", S["tlatch"][2]), lim_rja=S["lim_rja"], ron=S["ron"], short=S["short_dur"])
    muts = [
        ("the limiter's maximum taken at its TYPICAL %.3f A" % S["ios49"][0][1], dict(ios_hi=(S["ios49"][0][1], "TYPICAL", S["ios49"][2]))),
        ("the regulator's dropout taken at its TYPICAL %.3f V at 1 A" % S["vdo_new_typ"][0], dict(vdo1a=S["vdo_new_typ"])),
        ("the AP2112K (SOT25, %.0f C/W PRINTED, its rows) at the new current" % P["theta_ldo"],
         dict(rja=(P["theta_ldo"], "PRINTED", "DS39724 p.3"), vdo1a=((need_ap(P, hi1) - 3.3 * (P["vout_hi"] + P["load"] * hi1)) / hi1, "PRINTED", "DS39724 p.8, INFERRED"),
              iout=(P["imax"], "PRINTED", "DS39724"), icl_min=(P["imax"], "PRINTED", "DS39724"), acc=(P["vout_hi"] - 1 + P["load"] * hi1, "PRINTED", "DS39724"),
              vin_max=(P["vin"][1], "PRINTED", "DS39724"))),
        ("the code without M3 (legacy silicon may ship: %.3f V at 1 A, +-%.0f %%)" % (S["vdo_leg"][0], 100 * S["acc_leg"][0]),
         dict(vdo1a=S["vdo_leg"], acc=S["acc_leg"], rja=(max(S["rja_new"][0]["DCQ"], S["rja_leg"][0]["DCQ"]), "PRINTED", "5.4, 5.5"))),
        ("the regulator's junction-to-ambient one step over the requirement, %.1f C/W" % (round(theta_need, 1) + 0.1),
         dict(rja=(round(theta_need, 1) + 0.1, "PRINTED", "a mutation"))),
    ]
    mres = []
    for lab, ch in muts:
        st = dict(base)
        st.update(ch)
        v, rr = judge(st, R)
        mres.append((lab, v))
        failing = [c for c, h, _t in rr if not h]
        w("   mutated, %-74s %s%s" % (lab + ":", v, (" (" + ", ".join(failing) + ")") if failing else ""))
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 9
    w("9. THE DRAFT COMPOSED (apply_gen_sch_b_regstage.py; release-guarded by record l9t5's RELEASE-T10.md; None is APPLIED)")
    with tempfile.TemporaryDirectory(prefix="l4reg_") as d:
        seq = D.seq_of("b", "slot")
        at = seq.index(D.MINE["b"]) + 1
        pre = seq[:at] + [T.PRE["b"], T.SHDN, T.SET % "b", T.GUARD_B]
        comps = {}
        for tag, extra in (("guard", []), ("reg", [DRAFT]), ("canmb", [CANMB]), ("canreg", [CANMB, DRAFT]), ("regcan", [DRAFT, CANMB])):
            p, res, ok = D.compose("b", pre + extra + seq[at:], d, tag)
            if not ok:
                refuse("board B with %s did not compose: %s" % (tag, [r for r in res if r[1] != "OK"]))
            rc, net, _t = D.netlist("b", p, d, tag)
            if rc:
                refuse("board B with %s did not regenerate: %s" % (tag, net))
            comps[tag] = (p, net, CHK.read(open(net, "rb").read()), len(pre + extra + seq[at:]))
        v_reg, why_reg = regstage_check(comps["reg"][2], S)
        v_old, why_old = regstage_check(comps["guard"][2], S)
        v_cr, _w = regstage_check(comps["canreg"][2], S)
        v_rc, _w = regstage_check(comps["regcan"][2], S)
        same = pins_by_ref(comps["canreg"][2]) == pins_by_ref(comps["regcan"][2]) and \
            {r: CHK.value(comps["canreg"][2], r) for r in comps["canreg"][2]["comps"]} == {r: CHK.value(comps["regcan"][2], r) for r in comps["regcan"][2]["comps"]}
        refs_r, nets_r = changed(comps["guard"][2], comps["reg"][2])
        refs_c, nets_c = changed(comps["guard"][2], comps["canmb"][2])
        net_r = comps["reg"][1]
        mut = [("the limiter bypassed (the LDO's IN on +5V_IOC)", [(("U40", "1"), ("U45", "1"))]),
               ("the LDO's IN and OUT exchanged", [(("U40", "1"), ("U40", "2"))]),
               ("the LDO's EN on its ground pin", [(("U40", "5"), ("U40", "3"))]),
               ("the limiter's EN on its ground pin", [(("U45", "3"), ("U45", "2"))]),
               ("RILIM's ground end on the EN pull-up's rail end", [(("R601", "2"), ("R602", "1"))])]
        vm = []
        for i, (lab, sw) in enumerate(mut):
            q = D.mutate(net_r, d, "m%d" % i, sw)
            vm.append((lab, regstage_check(CHK.read(open(q, "rb").read()), S)[0]))
        for i, (lab, ref, val) in enumerate((("RILIM at 102 kOhm (W135's band under the AP2112K)", "R601", "102k 1%"),
                                             ("the AP2112K back on U40", "U40", "AP2112K-3.3 LDO: the private 3.3 V of controller A"),
                                             ("U40 ordered without M3 (TPS73733DCQR)", "U40", "TPS73733DCQR 1 A LDO"))):
            q = set_value(net_r, d, "v%d" % i, ref, val)
            vm.append((lab, regstage_check(CHK.read(open(q, "rb").read()), S)[0]))
        bare = os.path.join(d, "bare_gen_sch_b.py")
        shutil.copy(D.GEN["b"], bare)
        r_bare = subprocess.run([sys.executable, "-B", DRAFT, bare, "--write"], capture_output=True)
        r_tree = subprocess.run([sys.executable, "-B", DRAFT, D.GEN["b"], "--write"], capture_output=True)
        r_twice = subprocess.run([sys.executable, "-B", DRAFT, comps["reg"][0], "--write"], capture_output=True)
        l9chk = CHK.checks_b(comps["reg"][2])
    refused = (r_bare.returncode == 3, r_tree.returncode == 3 and b"NOT RELEASED" in r_tree.stderr, r_twice.returncode == 3)
    w("   board B composed in L4-E9's order with record l9t5's iocbuck, iocpre, canshdn, iocset and iocguard, then this draft (%d drafts): every" % comps["reg"][3])
    w("     step OK; the generator ran to its end (record l8p's gen_netlist.py); read by pin and value: %s%s" % (v_reg, (": " + "; ".join(why_reg[:3])) if why_reg else ""))
    w("   the state before it (iocguard's rail trip, no regstage): %s (%s)" % (v_old, "; ".join(why_old[:2])[:150]))
    for lab, v in vm:
        w("     mutated, %-60s %s" % (lab + ":", v))
    w("   with W137's canmb (its checkpoint at fnd/l4canmb 31de4bbc, copied to inputs/): canmb then regstage %s; regstage then canmb %s; the two" % (v_cr, v_rc))
    shared_nets = sorted(nets_r & nets_c)
    ctrl = sorted(r for r in refs_r if r in ("U41", "U51", "U61"))
    w("     orders' netlists identical: %s. Shared: designators %s; signal nets %s; the rails both attach parts to %s; controller pins %s" % (
        "yes" if same else "NO", sorted(refs_r & refs_c) or "none", sorted(set(shared_nets) - RAILS) or "none",
        sorted(set(shared_nets) & RAILS) or "none", ctrl or "none (this draft maps no H743 pin)"))
    w("     regstage changes %d parts and %d nets against iocguard's state; canmb %d parts and %d nets" % (len(refs_r), len(nets_r), len(refs_c), len(nets_c)))
    w("   the draft on a generator without record l9t5's drafts: %s; a second time: %s; on the tree's own generator: %s" % (
        "refused" if refused[0] else "NOT REFUSED", "refused" if refused[2] else "NOT REFUSED", "refused (NOT RELEASED)" if refused[1] else "NOT REFUSED"))
    w("   record l9t5's own I-03 check (Slot A's check_l9t5_netlist.py) on this composition: LDO %s, LEAD %s (it expects round 6's sense resistor" % (
        l9chk.get("LDO", ("?",))[0], l9chk.get("LEAD", ("?",))[0]))
    w("     and EN on pin 3 with R66 from +5V_IOC: its entry is Slot A's to restate when this delta is taken, finding L4REG-F1)")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 10
    w("10. FINDINGS FOR OTHER AUTHORS")
    w("   L4REG-F1 (Slot A, record l9t5's check_l9t5_netlist.py): its board B LDO entry reads round 6's sense resistor, EN on pin 3 and R66 from")
    w("     +5V_IOC; with this delta the LDO's input is joined to +5V_IOC by the limiter U45 (IN pin 1, OUT pin 6), EN is pin 5 and R66 runs from")
    w("     IOC_LDO_IN: to restate when the delta is taken (as L9T5-F25 did for round 6)")
    w("   L4REG-F2 (Layer 5 V rows and the receiving company; V-T10-DROP extended): the TPS73733DCQRM3's output between VOUT + VDO and VOUT + 0.5 V")
    w("     at 0.01 to %.4f A and -40 to 125 C TJ (the band's printed condition is VIN >= VOUT + 0.5 V); its start-up into the controller in reset" % hi1)
    w("     (foldback) and its power-up overshoot with EN from its input: specimen three first-article board B supervisors, pass limit 3.0 to 3.6 V")
    w("   L4REG-F3 (L4A-54, L4A-58): each limiter's EN (IOC_LIM_EN, 100 kOhm to +5V_IOC) is the node for the peers' restart of a latched")
    w("     supervisor and the in-service over-limit test; FAULT (pin 4) is open for L4A-58 to read; a restart must bound its own rate (W135 row 3)")
    w("   L4REG-F4 (Layer 6 and Layer 12): order codes owed for the TPS2553-1 (DBV, latch-off) and TPS73733DCQRM3; the M3 suffix is the identity")
    w("     row (Table 8-1: without it the legacy silicon, whose dropout fails T10-A3 at the limit, may ship); the reel label's CSO RFB at inspection")
    w("   L4REG-F5 (Layer 10): the land id Package_TO_SOT_SMD:SOT-223-6 is this draft's ASSUMPTION (kisch's land check runs only where KiCad is);")
    w("     the regulator's printed %.1f C/W assumes JEDEC 2s2p copper with %s vias under the tab: the site's copper is the means, E-17 the reading" % (
        REG["rja"][0], S["dcq_vias"][0]))
    w("   L4REG-F6 (Layer 10, gen_pcb_b3.py): the controller pockets' region lists carry no part of any P0 draft (round 6's rail trip and share")
    w("     limiters included); this delta adds no designator, it changes U40/U50/U60's land and U45/U55/U65's part")
    w("   L4REG-F7 (L4A-59, HO-E): round 6's rail trip held each controller's AVERAGE at %.4f to %.4f A, under its 125 C current %.3f A (PROVISIONAL);" % (
        E["trip"][0][0], E["trip"][0][1], E["mcu125"][0]))
    w("     with it removed nothing in hardware bounds a firmware outside FW-B20 (T10 10h (3)'s systematic-firmware obligation returns): H-2's")
    w("     watchdog proof should cover every state outside FW-B20, not VOS0 alone")
    w("   L4REG-F8 (the coordinator): pdftext.FETCH lists the TPS2553 sheet for record l4reg; when record l4lim (fnd/l4lim) is merged its fetch")
    w("     script lists it too, and the entry becomes ('l4lim', 'l4reg') (test_pdftext_input's W37 map)")
    w("   L4REG-F9 (the coordinator, L4-E9's change list): apply_gen_sch_b_regstage.py needs its row on board B after record l9t5's iocguard")
    w("     (and W137's canmb, either order), as V6-m11 asked of canshdn; the register's rows L4A-56 and L4A-57 read this record's selection")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- 11
    preds = [
        ("record l9t5's corner and T10-A3 reproduce from its modules; W135's figures reproduce from them and the makers' rows", reproduced),
        ("every served state is under the selected limiter's minimum; row 8's currents lie inside its band (may latch)", lo1 >= s3m and lo1 <= E["f2"][0] <= hi1),
        ("no AP2112 package and no screened TLV757P qualifies; the TPS73733DCQRM3 qualifies; the code without M3 does not",
         (not reg_rows["ap"][4]) and reg_rows["sel"][4] and not reg_rows["leg"][4] and not reg_rows["tlv"][4] and not reg_rows["tlv2"][4]),
        ("the selected regulator holds 125 C at the limiter's maximum on its printed theta", sel[1] <= tjg),
        ("T10-A3 holds at the limiter's maximum, at T10's point, for the other two and at S3' (INFERRED dropout)", all(a >= n for a, n in A3.values())),
        ("K1's input is under its recommended range at 14.0k; its loss has no printed bound", fixed < k1_vmin and S["k1_rhs"][1] == "TYPICAL"),
        ("the regulator's own limit (C) passes 150 C at its printed maximum", tjc > 150.0),
        ("the judge holds on the selected stage", vA == "HOLDS"),
        ("each mutation of the judge FAILS (a typical as a limit refused at J0, the AP2112K, no M3, theta over)", all(v == "FAILS" for _l, v in mres)),
        ("the draft composes after iocguard, reads DRAWN by pin and value, and the state before it FAILS", v_reg == "DRAWN" and v_old == "FAIL"),
        ("every netlist and value mutation FAILS", all(v == "FAIL" for _l, v in vm)),
        ("with canmb in either order the draft reads DRAWN, the netlists are identical; no part, signal net or controller pin is shared",
         v_cr == "DRAWN" and v_rc == "DRAWN" and same and not (refs_r & refs_c) and set(shared_nets) <= RAILS and not ctrl),
        ("the draft refuses a generator without iocguard, a second application and the tree's generator", all(refused)),
    ]
    w("11. THE PREDICATES")
    for lab, ok in preds:
        w("   %-128s %s" % (lab, "yes" if ok else "NO"))
    w("")
    w("l4reg_compare: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(ok for _l, ok in preds) else 1


if __name__ == "__main__":
    sys.exit(main())
