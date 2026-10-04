#!/usr/bin/env python3
"""l8p_drafts.py: Layer 8 record l8p, W4DP-F2's breaker drafted for boards P, E and A, proved on scratch copies (MESHSAT-1357,
4 October 2026).

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the generators and the engine, every other draft it composes with, record l9stk's copies
     of 0d72880b, L4-E7's backstop draft of fnd/l4e7r6 at 914a2f5a, the committed netlists, the lands, the makers' sheets read,
     the held OPA187 sheet, this record's own files);
  2. the values: each value the drafts draw found in record l9stk's own text by its section (refused when a phrase no longer
     matches), and this record's SESSION choices;
  3. C-1c's budget: the restart inhibit's window from the record, the NTC's figures from Murata's sheet, the OPA187's offset over
     temperature, bias and offset currents and supply rejection read from TI's held sheet (never typed), the bridge resistors,
     the NTC's own heating and the hysteresis computed for the drawn values, and the remainder left for the pad's gradient;
  4. each draft on a scratch copy: checked, applied once, refused twice, and refused on the tree's own generator (NOT RELEASED);
  5. the composition of each board in L4-E9's change-list order with this record's draft in its place, first and last;
  6. the designators each draft adds, pairwise disjoint, and every literal part call drawn once in the composed generators;
  7. the regeneration on the runner (gen_netlist.py: the generator's own part table, no KiCad): the unpatched generators
     reproduce the committed KiCad netlists pin for pin; the netlist check (check_l8p_netlist.py) on the committed netlists
     (NOT DRAWN), on the three boards with this record's drafts alone and composed in L4-E9's order (DRAWN), and on three
     mutated netlists (FAIL);
  8. the declarations the patched board P generator writes into its intent for the new nets;
  9. the findings for other authors and their state.
Run from the repository root:  python3 v2/docs/records/l8p/l8p_drafts.py  (l8p_drafts.out is its output, regenerated with
_bin/regen_out.py). Nothing here is built or measured: every statement is about generator text, netlists and record text."""
import ast
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
RECS = os.path.join(ROOT, "v2", "docs", "records")
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import check_l8p_netlist as CHK  # noqa: E402
import gen_netlist as GN  # noqa: E402

GEN = {b: os.path.join(TOOLS, "gen_sch_%s.py" % b) for b in "pea"}
NET = {b: os.path.join(ROOT, p) for b, p in CHK.COMMITTED.items()}
PROJECT = {"p": "pcb-p-pack", "e": "pcb-e1-dock", "a": "pcb-a-power"}
MINE = {"p": os.path.join(HERE, "apply_gen_sch_p_breaker.py"), "e": os.path.join(HERE, "apply_gen_sch_e_enable.py"),
        "a": os.path.join(HERE, "apply_gen_sch_a_ptc.py")}
# L4-E9's change list (records/l4e9/L4-POWER-ARCHITECTURE.md section 3) for each board's round, in application order; d8dec31's
# drafts take the board's committed netlist as their second argument; Layer 6's l6r2 drafts are order-independent tables
ORDER = {
    "p": [("l6r2", "intent"), ("l6r2", "lcsc")],
    "e": [("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"), ("l4e9", "f1"),
          ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux"), ("d8dec31", "cin"), ("l6r2", "xal_land"),
          ("l6r2", "lcsc")],
    "a": [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
          ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("d8dec31", "mainpb"), ("l6r2", "lcsc")],
}
# where this record's draft goes in the forward order: after the board's circuit drafts, before the last-taker and the tables
SLOT = {"p": 0, "e": 10, "a": 11}
INPUT_FILES = {"page": "inputs/l9stk-section15-0d72880b.md", "out": "inputs/l9stk_protection-0d72880b.out.txt",
               "constants": "inputs/l9stk_protection-constants-0d72880b.txt"}
SOURCES_SHA = {"inputs/l9stk-section15-0d72880b.md": "a96099193dd92e8eecbb4ea444ee345bd87eb9af3146f005c507f14961f3ac80",
               "inputs/l9stk_protection-0d72880b.out.txt": "d97f94a0fa1f25598a26458276334b53505b065f350eb75a4d01cdfd91716eac",
               "inputs/l9stk_protection-constants-0d72880b.txt": "ed559399fd3b2f2d7c502b16e3296b5266ee5f4d1638b0a235342bde4e5f5c3e",
               "inputs/l4e7r6-apply_gen_sch_e_backstop-914a2f5a.py": "dc560d0de51ac782800eb1be0cc18d8c506b047fc7891ad5efe432b2d72fa544"}
# L8P-F01 is closed by L4-E7's backstop draft on fnd/l4e7r6 at 914a2f5a (not on main): board E's composition uses that draft,
# copied byte for byte into inputs/, in place of main's
REPLACED = {("l4e7", "backstop", "e"): os.path.join(HERE, "inputs", "l4e7r6-apply_gen_sch_e_backstop-914a2f5a.py")}
OPA187 = os.path.join(ROOT, "v2", "vendor", "ti", "held", "ti-opa187-sbos807e.pdf")
NTC_SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "murata-nxrt15xh103fa1b.pdf")
D4148_SHEET = os.path.join(ROOT, "v2", "vendor", "power", "st-semtech-1n4148w-c81598.pdf")
# C-1c as drawn (apply_gen_sch_p_breaker.py): the bridge, the reference, the hysteresis, and the bounds the budget applies
R_BRIDGE, R_REF_T, R_REF_B, R_HYST = 150e3, 147e3, 1.62e3, 15e6
R_TOL, R_TCR, HYST_TOL = 0.001, 25e-6, 0.01     # the bridge and reference parts: 0.1 %, at most 25 ppm/K; the hysteresis part 1 %
T_RES = (25.0, 101.0)                           # the resistors anywhere between 25 C and the held 101.0 C case (l9stk 15.4)
V_CLAMP = 29.2                                  # BRK_VIN's clamp (l9stk 15.4, the clamps row), the supply span for PSRR
CHECKER_GRADIENT = 0.9                          # the pad-to-NTC gradient the checker asked the split to leave room for, K
SESSION = [
    ("designators", "the free 100 block on board P (U101, U102, Q101 to Q106, D101, D102, RT101, R101 to R117, C101 to C106, TP101 to TP106); RT1 on board A, which carries no RT designator"),
    ("net names", "BRK_VIN (Q2's source, the breaker's input), BRK_SNS, BRK_GATE, BRK_TMR, BRK_PWR, BRK_UVLO, BRK_G2, BRK_H, BRK_HD, BRK_PGD, BRK_CMID, INH_NTC, INH_REF, INH_OUT, INH_G; DOCK_EN_OUT and DOCK_EN_RET on all three boards"),
    ("J_SMB pins", "a JST-XH 1x7 at both ends: 1 to 4 unchanged, 5 DOCK_EN_RET, 6 the return (the ground between), 7 DOCK_EN_OUT at the row's end"),
    ("dock positions", "J_DOCK and J_BLK pins 3 (DOCK_EN_RET) and 5 (DOCK_EN_OUT), pin 4 ground between them; pin 5's neighbours 4, 6 and 11 are all ground"),
    ("input bypass", "C104 and C105, 2.2 uF 50 V X7R in series (1.1 uF) at the sense pair: TI SNVS452G section 10 ('a 1-uF ceramic capacitor to ground close to the drain of the hot swap MOSFET') and 11.1.1; in series as C11 and C12 are (board P's O-12)"),
    ("comparator", "U102, TI OPA187IDBVR, a zero-drift amplifier on BRK_VIN used as the comparator: 4.5 to 36 V, its input range from 0.1 V under its negative rail, its offset over temperature read from the held sheet (section 3); C106 its bypass"),
    ("reference", "R111 147 kOhm over R112 1.62 kOhm (1653.06 ohm against the trip's 1653), R113 15 MOhm of hysteresis, all from BRK_VIN as the NTC's bridge is (ratiometric)"),
    ("PGD gating", "U101's PGD on BRK_PGD at half BRK_VIN (R116, R117 1 MOhm); Q106 holds Q105's gate low while PGD is high; Q105 pulls UVLO; R114 and R115 halve U102's output for Q105's gate"),
    ("test points", "TP101 BRK_VIN, TP102 BRK_UVLO, TP103 DOCK_EN_OUT, TP104 DOCK_EN_RET (E-12); TP105 INH_NTC, TP106 INH_OUT (E-12b)"),
    ("lands", "the VSSOP-10, SMC, SOD-123, SOT-23-5 and 2512 lands the kit already uses; the 7-circuit XH header of the same row; RT1 on board P's 0402; RT101's 10 mm leads on the project's LeadLands_1x02"),
]


# SCRATCH STAND-INS for run-time defects of OTHER records' drafts that stop the composed generators (section 8 lists them as
# findings for their owners). Each is applied to a scratch copy only when its old text is there; none is a draft, none is applied
# anywhere else, and each says only that the generator then runs on, so this record's loop can be judged in the whole composition.
STANDINS = {
    "e": [
          ("L8P-F03", "l4e11's aux draft: +12V_FAN names L4 as its source, which is not on that net",
           '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "L4",', '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "C143",')],
    "a": [("L8P-F02", "l4e11's charger draft: VSYS_DOCK names U42 as its source without source_ic, and is fed from VBAT before VBAT is declared",
           '_intent.rail("VSYS_DOCK", 14.4, 1.32, 1.32, "U42", always_on=True, v_work=17.4, converted=False, fed_from="VBAT",',
           '_intent.rail("VSYS_DOCK", 14.4, 1.32, 1.32, "U42", source_ic="record l8p scratch stand-in", always_on=True, v_work=17.4, converted=False,')],
}


def pdftext(path):
    try:
        r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        refuse("pdftotext could not read %s (%s)" % (rel(path), e))
    return r.stdout.decode("utf-8", "replace")


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its input" % what)
    return m


def budget(page):
    """C-1c's window from the record, the parts' figures from their makers' sheets, and the split of the +-1.95 K."""
    N = r"([0-9.]+)"
    W = {}
    W["allow"] = float(need(page, r"Allow\s+from\s+%s\s+C" % N, "the allow edge").group(1))
    W["block"] = float(need(page, r"block\s+from\s+%s\s+C\." % N, "the block edge").group(1))
    m = need(page, r"trip\s+is\s+%s\s+C\s+plus\s+or\s+minus\s+%s\s+K,\s+with\s+the\s+NTC\s+at\s+%s\s+ohm" % (N, N, N), "the trip")
    W["trip"], W["half"], W["r_trip"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    W["ntc_k"] = float(need(page, r"The\s+NTC\s+takes\s+plus\s+or\s+minus\s+%s\s+K" % N, "the NTC's share").group(1))
    W["rest"] = float(need(page, r"leaves\s+plus\s+or\s+minus\s+%s\s+K\s+for\s+the\s+comparator" % N, "the budget left").group(1))
    W["air"] = float(need(page, r"L4-E12's\s+%s\s+C" % N, "the inside air").group(1))
    m = need(page, r"the\s+pack\s+%s\s+to\s+%s\s+V" % (N, N), "the pack's range")
    W["vmin"], W["vmax"] = float(m.group(1)), float(m.group(2))
    W["case_held"] = float(need(page, r"case\s+%s\s+C\s+with\s+both\s+losses\s+through\s+one\s+pad" % N, "the held case").group(1))
    need(page, r"PGD\s+is\s+low:\s+the\s+breaker\s+off,\s+starting\s+or\s+in\s+a\s+fault\s+\(VDS\s+over\s+1\.62\s+to\s+3\.4\s+V\)", "the PGD gate")
    nt = pdftext(NTC_SHEET)
    W["r25"] = float(need(nt, r"Resistance \(25\u2103\)\s+(\d+)k\u03a9", "the NTC's R25").group(1)) * 1e3
    W["b85"] = float(need(nt, r"B-Constant\(25/85\u2103\)\s+(\d+)K", "the NTC's B25/85").group(1))
    W["imax"] = float(need(nt, r"Maximum Operating Current\s+([0-9.]+)mA", "the NTC's current").group(1)) * 1e-3
    W["delta"] = float(need(nt, r"Typical Dissipation Constant\s+([0-9.]+)mW/\u2103", "the NTC's dissipation constant").group(1)) * 1e-3
    need(nt, r"Lead Shape\s+Lead Wire type", "the NTC's leads"); need(nt, r"Size Code \(in mm\)\s+010", "the NTC's 10 mm leads")
    need(nt, r"Reference Value", "B25/85 printed as a reference value")
    op = pdftext(OPA187)
    U = "\u03bc"
    need(op, r"SBOS807E", "the OPA187 sheet's revision")
    W["vos"] = float(need(op, r"\u00b11\s+\u00b1(10)\s+%sV" % U, "the OPA187's VOS").group(1)) * 1e-6
    W["drift"] = float(need(op, r"TA = \u201340\u00b0C to \+125\u00b0C\s+\u00b10\.001\s+\u00b1([0-9.]+)\s+%sV/\u00b0C" % U, "its drift").group(1)) * 1e-6
    W["ib"] = float(need(op, r"TA = \u201340\u00b0C to \+125\u00b0C\s+\u00b1([0-9.]+)\s+nA\n\s+\u00b1100\s+\u00b1500\s+pA", "its IB").group(1)) * 1e-9
    W["ios"] = float(need(op, r"IOS\s+Input offset current\n\s+TA = \u201340\u00b0C to \+125\u00b0C\s+\u00b1([0-9.]+)\s+nA", "its IOS").group(1)) * 1e-9
    W["psrr"] = float(need(op, r"\u00b10\.01\s+\u00b1([0-9.]+)\s+%sV/V" % U, "its PSRR").group(1)) * 1e-6
    m = need(op, r"^\(V\+\) \u2013 \(V\u2013\)\s+Supply voltage\s+([0-9.]+) \(\u00b12\.25\)\s+(\d+) \(\u00b118\)\s+V", "its supply range")
    W["vs"] = (float(m.group(1)), float(m.group(2)))
    W["vs_abs"] = float(need(op, r"Supply, VS = \(V\+\) \u2013 \(V\u2013\)\s+(\d+)", "its absolute supply").group(1))
    need(op, r"\(V\u2013\) \u2013 0\.1\s+\(V\+\) \u2013 2\s+V", "its input range from under its negative rail")
    need(op, r"protected from excessive differential voltage with back-to-back diodes", "its input diodes")
    need(op, r"Low-ESR, 0\.1-\u00b5F ceramic bypass capacitors must be connected between each supply pin and ground", "its bypass clause")
    W["tj_max_spec"] = 125.0 if re.search(r"All versions are specified for\s+operation from \u201340\u00b0C to \+125\u00b0C", op) else refuse("its specified range")
    # the arithmetic
    tk = W["trip"] + 273.15
    sens = W["b85"] / tk ** 2                                          # d(ln R)/dT at the trip, per K (B25/85, the record's)
    rt = W["r_trip"]
    vn = W["vmin"] * rt / (R_BRIDGE + rt)                              # the NTC's node at the trip and the least VIN
    slope = vn * sens * R_BRIDGE / (R_BRIDGE + rt)                     # V per K there
    rsrc_n = R_BRIDGE * rt / (R_BRIDGE + rt)
    rsrc_r = 1.0 / (1.0 / R_REF_T + 1.0 / R_REF_B + 1.0 / R_HYST)
    v_op = (W["vos"] + W["drift"] * (W["tj_max_spec"] - 25.0) + W["ios"] * max(rsrc_n, rsrc_r) + W["ib"] * abs(rsrc_n - rsrc_r)
            + W["psrr"] * (V_CLAMP - W["vmin"]))
    W.update(sens=sens, vn=vn, slope=slope, v_op=v_op, k_op=v_op / slope)

    def x_eq(rt_, rb_, rf_, vo):
        g = 1.0 / rt_ + 1.0 / rb_ + 1.0 / rf_
        r = (1.0 / rt_ + vo / rf_) / g
        return R_BRIDGE * r / (1.0 - r)
    x_low = x_eq(R_REF_T, R_REF_B, R_HYST, 0.0)
    W["x_low"] = x_low
    W["k_nominal"] = math.log(rt / x_low) / sens                      # positive: the drawn trip sits hotter than the record's
    W["hyst_nom"] = math.log(x_eq(R_REF_T, R_REF_B, R_HYST, 1.0) / x_low) / sens
    W["hyst_max"] = max(math.log(x_eq(R_REF_T * a, R_REF_B * b, R_HYST * (1 - HYST_TOL), 1.0) / x_eq(R_REF_T * a, R_REF_B * b, R_HYST * (1 - HYST_TOL), 0.0)) / sens
                        for a in (1 - R_TOL, 1 + R_TOL) for b in (1 - R_TOL, 1 + R_TOL))
    e = R_TOL + R_TCR * (T_RES[1] - T_RES[0])
    worst = 0.0
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            for s3 in (-1, 1):
                rb_, rr_t, rr_b = R_BRIDGE * (1 + s1 * e), R_REF_T * (1 + s2 * e), R_REF_B * (1 + s3 * e)
                g = 1.0 / rr_t + 1.0 / rr_b + 1.0 / R_HYST
                r = (1.0 / rr_t) / g
                worst = max(worst, abs(math.log((rb_ * r / (1.0 - r)) / x_low)) / sens)
    W["k_res"], W["res_e"] = worst, e
    i_br = W["vmax"] / (R_BRIDGE + rt)
    W["i_bridge"] = i_br
    W["k_self"] = i_br * i_br * rt / W["delta"]                        # the NTC reads hotter by its own heating
    allow_used = W["k_op"] + W["k_res"] + W["k_self"] + W["hyst_max"] + max(0.0, -W["k_nominal"])
    block_used = W["k_op"] + W["k_res"] + max(0.0, W["k_nominal"])
    W.update(allow_used=allow_used, block_used=block_used, grad_allow=W["rest"] - allow_used, grad_block=W["rest"] - block_used)
    W["closes"] = W["grad_allow"] >= CHECKER_GRADIENT and W["grad_block"] >= CHECKER_GRADIENT and W["hyst_max"] <= 0.5 and W["k_op"] <= 0.47
    # the record prints each figure to two decimals, so the window's sums agree within two of their last digits
    W["window_ok"] = abs(W["trip"] - W["half"] - W["allow"]) <= 0.02 and abs(W["trip"] + W["half"] - W["block"]) <= 0.02 \
        and abs(W["half"] - W["ntc_k"] - W["rest"]) <= 0.02
    W["lockout"] = W["allow"] - W["air"]
    return W


def rel(p):
    return os.path.relpath(p, ROOT)


def sha(p, n=16):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l8p_drafts: REFUSED: %s\n" % msg)
    sys.exit(2)


def draft(rec, name, board):
    return REPLACED.get((rec, name, board)) or os.path.join(RECS, rec, "apply_gen_sch_%s_%s.py" % (board, name))


def run(script, target, board):
    """(returncode, the last line it printed): d8dec31's drafts take the committed netlist, the others --write."""
    args = [script, target, NET[board]] if "/d8dec31/" in script.replace(os.sep, "/") else [script, target, "--write"]
    r = subprocess.run([sys.executable, "-B"] + args, capture_output=True)
    out = (r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])[-1] if r.returncode == 0 else \
        (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    return r.returncode, out


def scrub(s, d):
    return s.replace(d, "<scratch>")


def compose(board, seq, d, tag):
    p = os.path.join(d, tag + "_gen_sch_%s.py" % board)
    shutil.copy(GEN[board], p)
    res = []
    for s in seq:
        rc, msg = run(s, p, board)
        name = os.path.relpath(s, RECS)
        res.append((name, "OK" + (" (%s)" % msg if "/d8dec31/" in s.replace(os.sep, "/") and "mainpb" in s else "") if rc == 0 else "REFUSED (%s)" % scrub(msg, d)))
        if rc:
            break
    return p, res


STMT = re.compile(r'^\s*(ic|part|c|r|tp|nfet|vh2|synth|q|esd|efuse|pfet5|ph|_tvs)\(\s*"([A-Z#][A-Z0-9_]*)"')
TOKEN = re.compile(r"\b(RT\d{1,3}|[RCDLQUHF]\d{1,3}|J_[A-Z0-9]+|TP\d{1,3}|W_[A-Z0-9]+)\b(?!-)")


def strip_comments(s):
    return "\n".join("" if l.lstrip().startswith("#") else l.split("#")[0] for l in s.splitlines())


def literal_calls(text):
    out = []
    for line in strip_comments(text).splitlines():
        for stmt in line.split(";"):
            m = STMT.match(stmt)
            if m:
                out.append(m.groups())
    return out


def tokens(text):
    """Designator strings where the generator DRAWS or LISTS a part: a call's first argument, or an element of a list or tuple,
    read with ast; prose and dict keys count for nothing."""
    out = set()
    for n in ast.walk(ast.parse(text)):
        cands = []
        if isinstance(n, ast.Call) and n.args:
            cands.append(n.args[0])
        elif isinstance(n, (ast.List, ast.Tuple)):
            cands.extend(n.elts)
        for c in cands:
            if isinstance(c, ast.Constant) and isinstance(c.value, str) and TOKEN.fullmatch(c.value):
                out.add(c.value)
    return out


def declared_adds(script):
    import importlib.util
    try:
        sp = importlib.util.spec_from_file_location("adds_" + re.sub(r"\W", "_", script), script)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        return set(getattr(m, "ADDS", ()))
    except Exception:
        return set()


def added(before, after, script):
    cb = {r for _h, r in literal_calls(before)}; ca = {r for _h, r in literal_calls(after)}
    return (ca - cb) | (tokens(after) - tokens(before)) | declared_adds(script)


def _draws(node):
    """{designator: count} of the literal part calls under an ast node; the two branches of an `if _tvs:` (the generators' one
    clamp drawn either by kisch.tvs or by its fallback) are alternatives, so a designator counts once across them."""
    from collections import Counter
    if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "_tvs":
        a, b = Counter(), Counter()
        for x in node.body:
            a += _draws(x)
        for x in node.orelse:
            b += _draws(x)
        return a | b
    c = Counter()
    if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        f = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
        if f in ("ic", "part", "c", "r", "tp", "nfet", "pfet5", "ph", "q", "esd", "efuse", "synth", "vh2", "_tvs", "tvs") and TOKEN.fullmatch(node.args[0].value):
            c[node.args[0].value] += 1
    for ch in ast.iter_child_nodes(node):
        c += _draws(ch)
    return c


def duplicates(text):
    return sorted(r for r, n in _draws(ast.parse(text)).items() if n > 1)


def pins_of(nl):
    return {(r, p): n for r, d in nl["pins"].items() for p, n in d.items()}


def netlist_text(board, generator, d, tag):
    """(rc, netlist path or the generator's last line, table)."""
    out = os.path.join(d, "%s_%s.net" % (tag, board))
    rc, log, table = GN.run(generator, out, PROJECT[board])
    if rc:
        return rc, scrub((log.strip().splitlines() or [""])[-1], d), None
    return 0, out, table


def mutate(path, d, tag, swaps):
    """A copy of a netlist with the nets of two (ref, pin) nodes exchanged."""
    raw = open(path, encoding="utf-8").read()
    for (ra, pa), (rb, pb) in swaps:
        a = '(node (ref "%s") (pin "%s"))' % (ra, pa); b = '(node (ref "%s") (pin "%s"))' % (rb, pb)
        if raw.count(a) != 1 or raw.count(b) != 1:
            refuse("the mutation's nodes are not in the netlist once: %s %s" % (a, b))
        raw = raw.replace(a, "\0A").replace(b, a).replace("\0A", b)
    p = os.path.join(d, tag + ".net")
    open(p, "w", encoding="utf-8").write(raw)
    return p


def main():
    w = sys.stdout.write
    w("l8p_drafts: Layer 8 record l8p, W4DP-F2's breaker, its make-last dock enable loop and its restart inhibit drafted for boards P, E and A (MESHSAT-1357)\n")
    w("prototype design; nothing built, bought or measured; nothing applied to the tree; the values are record l9stk's (fnd/l9stk at 0d72880b)\n\n")
    # 1. inputs
    others = [draft(r, n, b) for b in "pea" for r, n in ORDER[b]]
    inputs = [GEN["p"], GEN["e"], GEN["a"], os.path.join(TOOLS, "kisch.py"), os.path.join(TOOLS, "intent.py"), os.path.join(TOOLS, "idc_pads.py")]
    inputs += others + [NET["p"], NET["e"], NET["a"]]
    inputs += [os.path.join(HERE, f) for f in sorted(SOURCES_SHA)] + [os.path.join(HERE, "inputs", "SOURCES.txt")]
    inputs += [os.path.join(CHK.PRETTY, l + ".kicad_mod") for l in sorted(set(CHK.LANDS.values()) | {"LeadLands_1x02"})]
    inputs += [os.path.join(ROOT, "v2", "vendor", "ti", "ti-lm5069.pdf"), NTC_SHEET, D4148_SHEET, OPA187, os.path.join(HERE, "fetch_held_back.py")]
    inputs += [MINE["p"], MINE["e"], MINE["a"], os.path.join(HERE, "check_l8p_netlist.py"), os.path.join(HERE, "gen_netlist.py")]
    w("1. INPUTS, pinned by sha256\n")
    for p in inputs:
        if not os.path.isfile(p):
            refuse("input %s is missing%s" % (rel(p), " (TI's held sheet: python3 v2/docs/records/l8p/fetch_held_back.py)" if p == OPA187 else ""))
        w("   %s %s\n" % (sha(p), rel(p)))
    for f, full in sorted(SOURCES_SHA.items()):
        if sha(os.path.join(HERE, f), 64) != full:
            refuse("the copy %s is not the file SOURCES.txt pins" % f)
    w("   record l9stk's and L4-E7's copies equal the sha256 SOURCES.txt pins: yes\n\n")
    # 2. the values
    texts = {k: open(os.path.join(HERE, v), encoding="utf-8").read() for k, v in INPUT_FILES.items()}
    w("2. THE VALUES, each found in record l9stk's own text (fnd/l9stk at 0d72880b), and this record's SESSION choices\n")
    for b, ref, pre, src, pat, key in CHK.VALUES:
        if not re.search(CHK.phrase_rx(pat), texts[key]):
            refuse("record l9stk no longer reads the %s value (%s)" % (ref, src))
        w("   %s %-5s %-16s l9stk %s\n" % (b.upper(), ref, pre, src))
    for pat, what in (("**IF-6** the gauge's PACK and VCC taps stay on Q2's source node, and the clamp and the controller return to PACK_N", "IF-6"),
                      ("OVLO to ground", "the controller row: OVLO to ground"),
                      ("SELECTED: the -1 (latch-off).", "15.4b: the -1, latch-off, selected"),
                      ("a ground contact between them in J_SMB and on the block", "condition C2: the ground between, in J_SMB and on the block"),
                      ("crosses the dock on two contacts 1 mm short of the power pins", "C-1b: two contacts 1 mm short (Layer 7's)"),
                      ("makes that **0.110 to 0.907 s after the enable mates**", "C-1b: the hold, 0.110 to 0.907 s"),
                      ("**0.41 ms in all**", "C-1b: the undocking, 0.41 ms"),
                      ("**C-1c SELECTED: a restart inhibit on the breaker pad**", "15.4b: C-1c selected"),
                      ("It is gated so that it acts only while PGD is low", "C-1c: gated by PGD"),
                      ("its designator L4-E11's", "15.5: the third battery FET's designator is L4-E11's"),
                      ("In the enable loop on the battery FETs' copper", "15.5: the PTC on the battery FETs' copper (board A)")):
        if not re.search(CHK.phrase_rx(pat), texts["page"]):
            refuse("record l9stk no longer reads %s" % what)
        w("   l9stk reads: %s\n" % what)
    if not re.search(r"R_E1, R_E2 = 10e3, 22e3", texts["constants"]) or not re.search(r"R_DIS = 150\.0", texts["constants"]) \
            or not re.search(r"R_U = 200e3", texts["constants"]):
        refuse("l9stk_protection.py's constants no longer read R_E1, R_E2, R_DIS and R_U as the page states them")
    w("   l9stk_protection.py's constants agree with the page: R_E1 10 kOhm, R_E2 22 kOhm, R_DIS 150 ohm, R_U 200 kOhm; R_G 1 MOhm\n")
    for k, v in SESSION:
        w("   SESSION %-15s %s\n" % (k, v))
    w("\n")
    # 3. C-1c's budget
    B = budget(texts["page"])
    w("3. C-1c'S BUDGET (DD-8): the window from l9stk 15.4b, the NTC from Murata's sheet, the comparator from TI's held OPA187 sheet (SBOS807E)\n")
    w("   the window: allow from %.2f C, block from %.2f C, trip %.2f C +-%.2f K with the NTC at %.0f ohm; the NTC's +-%.2f K and +-%.2f K left: %s\n" % (
        B["allow"], B["block"], B["trip"], B["half"], B["r_trip"], B["ntc_k"], B["rest"], "consistent" if B["window_ok"] else "INCONSISTENT"))
    w("   the NTC (Murata NXRT15XH103FA1B010): R25 %.0f ohm, B25/85 %.0f K printed as a reference value, %.2f mA at most, %.1f mW/K, 10 mm leads;\n" % (
        B["r25"], B["b85"], B["imax"] * 1e3, B["delta"] * 1e3))
    w("     its tolerance at 80 C (the record's +-%.2f K) is ASSUMED from the product search sheet: to be confirmed by Murata's approval sheet or E-15\n" % B["ntc_k"])
    w("   the bridge at the trip: R110 %.0f kOhm over the NTC, %.4f V at the pack's least %.1f V, %.3f mV/K there (B/T^2 %.5f per K); %.3f mA at %.1f V\n" % (
        R_BRIDGE / 1e3, B["vn"], B["vmin"], B["slope"] * 1e3, B["sens"], B["i_bridge"] * 1e3, B["vmax"]))
    w("   the reference: R111 %.0f kOhm over R112 %.2f kOhm with R113 %.0f MOhm at the output low: %.2f ohm against %.0f (%+.3f K); hysteresis %.3f K nominal, %.3f K at most\n" % (
        R_REF_T / 1e3, R_REF_B / 1e3, R_HYST / 1e6, B["x_low"], B["r_trip"], B["k_nominal"], B["hyst_nom"], B["hyst_max"]))
    w("   the comparator, U102 OPA187 (read, high-voltage table): VOS %.0f uV, drift %.3f uV/K to %.0f C, IB %.1f nA and IOS %.1f nA over temperature, PSRR %.0f uV/V;\n" % (
        B["vos"] * 1e6, B["drift"] * 1e6, B["tj_max_spec"], B["ib"] * 1e9, B["ios"] * 1e9, B["psrr"] * 1e6))
    w("     supply %.1f to %.0f V (absolute %.0f V) against BRK_VIN's %.1f V clamp; input range from 0.1 V under its negative rail; at most %.1f uV in all: %.3f K\n" % (
        B["vs"][0], B["vs"][1], B["vs_abs"], V_CLAMP, B["v_op"] * 1e6, B["k_op"]))
    w("   the bridge and reference resistors: %.1f %% and at most %.0f ppm/K between %.0f and %.1f C, each at %.3f %%, the worst of all signs: %.3f K\n" % (
        R_TOL * 100, R_TCR * 1e6, T_RES[0], T_RES[1], B["res_e"] * 100, B["k_res"]))
    w("   the NTC's own heating at %.3f mA: %.3f K (it reads hot)\n" % (B["i_bridge"] * 1e3, B["k_self"]))
    w("   THE SPLIT OF +-%.2f K: allow side %.3f K used (comparator, resistors, own heating, hysteresis, nominal), %.3f K left for the pad-to-NTC gradient;\n" % (
        B["rest"], B["allow_used"], B["grad_allow"]))
    w("     block side %.3f K used, %.3f K left; the checker's split asked about %.1f K for the gradient, the comparator at most 0.47 K, the hysteresis at most 0.5 K: %s\n" % (
        B["block_used"], B["grad_block"], CHECKER_GRADIENT, "the split closes" if B["closes"] else "THE SPLIT DOES NOT CLOSE"))
    w("   THE LOCKOUT AT THE ALLOW EDGE: a unit tripping at %.2f C needs its pad within %.2f K of the %.2f C inside air before it restarts; at that air the cells' hot stop has already shut the kit down\n" % (
        B["allow"], B["lockout"], B["air"]))
    w("   E-10 gains: VDS under 1.62 V during current-limit excursions (PGD stays high, so the inhibit stays gated)\n\n")
    if not (B["closes"] and B["window_ok"]):
        refuse("C-1c's split does not close or the window is inconsistent")
    with tempfile.TemporaryDirectory(prefix="l8p_") as d:
        # 4. each draft alone
        w("4. EACH DRAFT ON A SCRATCH COPY (check, apply once, refuse twice, refuse the tree's own generator)\n")
        before = {b: sha(GEN[b], 64) for b in "pea"}
        for b in "pea":
            s = MINE[b]
            t = os.path.join(d, "alone_gen_sch_%s.py" % b); shutil.copy(GEN[b], t); pre = sha(t, 64)
            r1 = subprocess.run([sys.executable, "-B", s, t], capture_output=True)
            ok1 = r1.returncode == 0 and b"CHECK OK" in r1.stdout and sha(t, 64) == pre
            r2 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            ok2 = r2.returncode == 0 and b"WRITTEN" in r2.stdout
            r3 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            r4 = subprocess.run([sys.executable, "-B", s, GEN[b], "--write"], capture_output=True)
            w("   %s: check %s; applied %s; second application %s; the tree's gen_sch_%s.py %s\n" % (
                os.path.basename(s), "OK" if ok1 else "FAILED", "OK" if ok2 else "FAILED",
                "refused" if r3.returncode == 3 else "NOT REFUSED", b, "refused (NOT RELEASED)" if r4.returncode == 3 and b"NOT RELEASED" in r4.stderr else "NOT REFUSED"))
        if any(sha(GEN[b], 64) != before[b] for b in "pea"):
            refuse("a draft wrote into the tree")
        w("   the tree's generators are unchanged: yes\n\n")
        # 5. composition
        w("5. COMPOSITION IN L4-E9'S CHANGE-LIST ORDER (records/l4e9/L4-POWER-ARCHITECTURE.md section 3)\n")
        composed = {}
        for b in "pea":
            seq = [draft(r, n, b) for r, n in ORDER[b]]
            fwd = seq[:SLOT[b]] + [MINE[b]] + seq[SLOT[b]:]
            p, res = compose(b, fwd, d, "fwd")
            composed[b] = p if all(v.startswith("OK") for _s, v in res) and len(res) == len(fwd) else None
            w("   board %s, this record's draft in its place:\n" % b.upper())
            for s, v in res:
                w("     %-44s %s\n" % (s, v))
            _p, res = compose(b, [MINE[b]] + seq, d, "rev")
            w("   board %s, this record's draft first, then the order: %s\n" % (b.upper(), "every step OK" if all(v.startswith("OK") for _s, v in res) and len(res) == len(seq) + 1
                                                                      else "; ".join("%s %s" % x for x in res if not x[1].startswith("OK"))))
            _p, res = compose(b, seq + [MINE[b]], d, "last")
            w("   board %s, the order, then this record's draft last: %s\n" % (b.upper(), "every step OK" if all(v.startswith("OK") for _s, v in res) and len(res) == len(seq) + 1
                                                                       else "; ".join("%s %s" % x for x in res if not x[1].startswith("OK"))))
        w("\n")
        # 6. designators
        w("6. DESIGNATORS EACH DRAFT ADDS (the forward order; part calls, listed tokens and each draft's declared ADDS)\n")
        for b in "pea":
            seq = [draft(r, n, b) for r, n in ORDER[b]]
            fwd = seq[:SLOT[b]] + [MINE[b]] + seq[SLOT[b]:]
            p = os.path.join(d, "desig_gen_sch_%s.py" % b); shutil.copy(GEN[b], p)
            before_t = open(p, encoding="utf-8").read(); adds = {}
            for s in fwd:
                if run(s, p, b)[0] != 0:
                    break
                after_t = open(p, encoding="utf-8").read()
                adds[os.path.relpath(s, RECS)] = added(before_t, after_t, s)
                before_t = after_t
            mine = adds.get(os.path.relpath(MINE[b], RECS), set())
            w("   board %s, this record's: %s\n" % (b.upper(), ", ".join(sorted(mine, key=lambda x: (re.sub(r"\d", "", x), int(re.sub(r"\D", "", x) or 0)))) or "none (nets only)"))
            meets = {k: sorted(v & mine) for k, v in adds.items() if k != os.path.relpath(MINE[b], RECS) and v & mine}
            w("   board %s, this record's against every other draft's: %s\n" % (b.upper(), "DISJOINT" if not meets else "MEETS %s" % meets))
            dup = duplicates(before_t)
            w("   board %s, literal part calls drawn twice in the composed generator: %s\n" % (b.upper(), ", ".join(dup) if dup else "none"))
        w("\n")
        # 7. regeneration and the netlist check
        w("7. REGENERATION ON THE RUNNER (gen_netlist.py: the generator's own part table, no KiCad) AND THE NETLIST CHECK\n")
        for b in "pea":
            rc, path, _t = netlist_text(b, GEN[b], d, "base")
            if rc:
                refuse("board %s's own generator did not run: %s" % (b, path))
            a, k = CHK.read_netlist(open(path, "rb").read()), CHK.read_netlist(open(NET[b], "rb").read())
            pa, pk = pins_of(a), pins_of(k)
            diff = [x for x in sorted(set(pa) | set(pk)) if pa.get(x) != pk.get(x)]
            nc = [x for x in diff if pa.get(x) is None and str(pk.get(x)).startswith("unconnected-")]
            fpd = [r for r in sorted(set(a["comps"]) | set(k["comps"])) if a["comps"].get(r, {}).get("footprint") != k["comps"].get(r, {}).get("footprint")]
            w("   board %s unpatched: %d connected pins against the committed KiCad netlist's %d; differences %d, all KiCad's names for "
              "open pins: %s; footprints differing: %d\n" % (b.upper(), len(pa), len(pk), len(diff), "yes" if len(nc) == len(diff) else "NO", len(fpd)))
        w("   the netlist check on the committed netlists:\n")
        buf = io.StringIO(); kit, _v = CHK.run(NET, ROOT, buf)
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        alone = {}
        for b in "pea":
            t = os.path.join(d, "regen_gen_sch_%s.py" % b); shutil.copy(GEN[b], t)
            if run(MINE[b], t, b)[0] != 0:
                refuse("this record's board %s draft refused a clean copy" % b)
            rc, path, table = netlist_text(b, t, d, "mine")
            if rc:
                refuse("board %s's generator with this record's draft did not run: %s" % (b, path))
            alone[b] = (path, table)
            w("   board %s with this record's draft alone: the generator ran to its end (%d parts, %d unplaced, intent written: %s)\n"
              % (b.upper(), len(table["parts"]), len(table["unplaced"]), "yes" if table["intent_written"] else "NO"))
        buf = io.StringIO(); CHK.run({b: alone[b][0] for b in "pea"}, ROOT, buf, label=lambda x: "regenerated board %s, this record's draft alone" % x.upper())
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        comp = {}
        for b in "pea":
            if not composed[b]:
                w("   board %s composed in L4-E9's order: the composition refused (section 4), not regenerated\n" % b.upper())
                continue
            rc, path, table = netlist_text(b, composed[b], d, "composed")
            if rc == 0:
                comp[b] = path
                w("   board %s composed in L4-E9's order: the generator ran to its end (%d parts, intent written: %s)\n"
                  % (b.upper(), len(table["parts"]), "yes" if table["intent_written"] else "NO"))
                continue
            w("   board %s composed in L4-E9's order: the generator refused: %s\n" % (b.upper(), path))
            # the same composition without this record's draft: the refusal is the other drafts' (a finding for their owners)
            seq = [draft(r, n, b) for r, n in ORDER[b]]
            q, res = compose(b, seq, d, "without")
            rc2, line2, _t2 = netlist_text(b, q, d, "without")
            w("     without this record's draft the same composition's generator %s\n" % (
                "refuses with the same line: the refusal is another draft's (section 8)" if rc2 and line2 == path else
                "runs" if rc2 == 0 else "refuses otherwise: %s" % line2))
            # scratch stand-ins for the other drafts' run-time defects (never drafts, never applied), so this record's loop is
            # judged in the whole composition
            s = os.path.join(d, "standin_gen_sch_%s.py" % b); shutil.copy(composed[b], s)
            txt = open(s, encoding="utf-8").read(); used = []
            for fid, why, old, rep in STANDINS.get(b, ()):
                if txt.count(old) == 1:
                    txt = txt.replace(old, rep); used.append(fid)
            open(s, "w", encoding="utf-8").write(txt)
            rc3, path3, table3 = netlist_text(b, s, d, "standin")
            w("     with scratch stand-ins for %s (never drafts, never applied): %s\n" % (", ".join(used) or "none",
              "the generator ran to its end (%d parts, intent written: %s)" % (len(table3["parts"]), "yes" if table3["intent_written"] else "NO") if rc3 == 0 else "still refused: %s" % path3))
            if rc3 == 0:
                comp[b] = path3
        if comp:
            buf = io.StringIO(); CHK.run(comp, ROOT, buf, label=lambda x: "regenerated board %s, composed in L4-E9's order%s" % (x.upper(), "" if "standin" not in comp[x] else " with the stand-ins"))
            w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m1 = mutate(alone["p"][0], d, "mut_p", [(("J_SMB", "6"), ("J_SMB", "7"))])
        buf = io.StringIO(); CHK.run({"p": m1}, ROOT, buf, label=lambda x: "mutated board P (J_SMB pins 6 and 7 exchanged)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m2 = mutate(alone["a"][0], d, "mut_a", [(("J_DOCK", "3"), ("J_DOCK", "4"))])
        buf = io.StringIO(); CHK.run({"a": m2}, ROOT, buf, label=lambda x: "mutated board A (J_DOCK pins 3 and 4 exchanged)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m3 = mutate(alone["p"][0], d, "mut_p2", [(("Q106", "1"), ("Q105", "1"))])
        buf = io.StringIO(); CHK.run({"p": m3}, ROOT, buf, label=lambda x: "mutated board P (Q105's and Q106's gates exchanged: the inhibit no longer gated by PGD)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        w("\n")
        # 8. intent
        w("8. THE INTENT THE PATCHED BOARD P GENERATOR WRITES FOR THE NEW NETS\n")
        it = alone["p"][1]["intent"]
        for n in ("PACK_P", "BRK_VIN", "BRK_SNS", "VCC_F"):
            r = it["rails"].get(n) or {}
            w("   rail %-8s source %s, loads %s, switch %s on %s%s%s\n" % (n, r.get("source"), json.dumps(r.get("loads"), sort_keys=True), r.get("switch", "-"),
                                                                      r.get("enable_net", "-"), ", series of %s" % r["series_of"] if r.get("series_of") else "",
                                                                      ", fed from %s" % r["fed_from"] if r.get("fed_from") else ""))
        for n in ("BRK_GATE", "BRK_UVLO", "BRK_H", "BRK_HD", "BRK_G2", "BRK_PGD", "BRK_CMID", "INH_NTC", "INH_REF", "INH_OUT", "INH_G", "DOCK_EN_OUT", "DOCK_EN_RET"):
            r = it["nodes"].get(n) or {}
            w("   node %-11s v_max %s V%s\n" % (n, r.get("v_max"), ", rides on %s by %s V" % (r["rides_on"], r["bias_v"]) if r.get("rides_on") else ""))
        cl = it.get("clamps", {}).get("D101") or {}
        w("   clamp D101: %s, protected %s, return %s\n" % (cl.get("direction"), cl.get("protected"), cl.get("return")))
        bp = [b_ for b_ in it.get("bypass", []) if b_.get("cap") == "C106"]
        w("   decoupling C106: %s\n" % ("class %s at %s.%s on %s" % (bp[0].get("class"), bp[0].get("part"), bp[0].get("pin"), bp[0].get("net")) if bp else "ABSENT"))
    w("\n9. FINDINGS FOR OTHER AUTHORS (run-time refusals of the composed generators that no text-level composition test reads)\n")
    w("   L8P-F01 board E: l4e7's backstop draft: C66, C67 and C68 carried no G14 decoupling class: CLOSED by L4-E7's fnd/l4e7r6 at 914a2f5a\n")
    w("     (class D with each maker's clause); board E's composition above uses that draft, copied byte for byte into inputs/, and needs no stand-in for it\n")
    for b in "ea":
        for fid, why, _o, _r in STANDINS[b]:
            w("   %s board %s: %s\n" % (fid, b.upper(), why))
    w("\nl8p_drafts: done\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
