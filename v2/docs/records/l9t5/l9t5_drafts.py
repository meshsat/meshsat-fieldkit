#!/usr/bin/env python3
"""l9t5_drafts.py: Layer 9 record l9t5, task T5 rounds 2 and 3: I-03's correction (the case row C-DEV rev 1) drafted for boards A
and B, composed, regenerated, mutated and judged on scratch copies (MESHSAT-1357, 4 October 2026). PROTOTYPE DESIGN: nothing in this
kit has been built, bought, powered or measured, nothing is applied to the tree, and no figure printed here is a measurement.

Round 3: record l8r2's round 7 (task T5b, in this tree since the merge at 43c9b49d) lets board B's composition run to its end, so
board B's half is composed, read and judged here as board A's was; and its finding L8R2-F35 for this record is answered: the
declarations are held to their basis, the lead is named, and the return sentence is withdrawn for pin 2.

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256;
  2. each of this record's drafts on a scratch copy: checked, applied once, refused a second time, and refused on the tree's own
     generator (NOT RELEASED); the old texts beside them (round 1's board B draft; round 2's two drafts);
  3. the composition of each board in L4-E9's change-list order (records/l4e9/L4-POWER-ARCHITECTURE.md section 3, with record
     l8r2's round 7 drafts fandec and gndret in board B's round) with this record's draft in its place, first and last; the
     designators each draft adds; d8dec31's mainpb with this record's draft before it and after it;
  4. the regeneration on the runner (record l8p's gen_netlist.py: the generator's own part table, no KiCad): the unpatched
     generators against the committed netlists; each board alone and composed; check_l9t5_netlist.py on each netlist and its
     declaration check on each intent; record l8r2's own check of the return on the composed board B; the old states, each of
     which must stop or FAIL; five mutated netlists, each of which must FAIL;
  5. the declarations the patched generators write (the intent), each beside its basis;
  6. the electrical acceptance on C-DEV rev 1 on the makers' printed figures, each figure labelled PRINTED (a maker's limit),
     TYPICAL, DECLARED (a generator's or a record's declaration), MODEL, ASSUMPTION or SESSION; board A's half, board B's half, and
     what the acceptance does and does not depend on (record l8r2's finding L8R2-F31, the shared return, stays OPEN beside it);
  7. record l8r2's finding L8R2-F35, answered point by point;
  8. the state of I-03 and the findings for other authors; 9. the predicates test_l9t5.py holds.
Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_drafts.py  (l9t5_drafts.out is its output, regenerated with
_bin/regen_out.py after l9t5_case.out). Stdlib, PyYAML and pdftotext; under a minute."""
import ast
import hashlib
import importlib.util
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
sys.path.insert(0, os.path.join(RECS, "l8p"))
import check_l9t5_netlist as CHK  # noqa: E402
import gen_netlist as GN  # noqa: E402

GEN = {b: os.path.join(TOOLS, "gen_sch_%s.py" % b) for b in "ab"}
NET = {b: os.path.join(ROOT, p) for b, p in CHK.COMMITTED.items()}
PROJECT = {"a": "pcb-a-power", "b": "pcb-b-compute"}
MINE = {b: os.path.join(HERE, "apply_gen_sch_%s_iocbuck.py" % b) for b in "ab"}
OLD_R1_B = os.path.join(HERE, "inputs", "apply_gen_sch_b_iocbuck-bdbed9bb.py")
OLD_R2 = {b: os.path.join(HERE, "inputs", "apply_gen_sch_%s_iocbuck-7c28f9da.py" % b) for b in "ab"}
CASE_PY = os.path.join(HERE, "l9t5_case.py")
GNDRET_OUT = os.path.join(RECS, "l8r2", "l8r2_gndret.out")
GNDRET_CHK = os.path.join(RECS, "l8r2", "check_gndret_netlist.py")
# L4-E9's change list for each board's round, in application order (L4-POWER-ARCHITECTURE.md section 3 at set 29's line): board A
# 3a r12, guard, charger; 3b r11; 3c bank; 3d r138; 3e u17; 3g gnd002, hotr1, record l8r2's board A drafts (its d8v3 and vbus20ov in
# its own order, as records l8r2 and l8p compose them, then packrtn, slotlm after the charger, fb01), record l8p's ptc, L4-E11's dd7
# after the ptc; 3h d8dec31's mainpb LAST; then Layer 6's order-free table. Board B: gnd002, record l8r2's fans12 with its round 7
# fandec, panel5v, ph4, rt500 and its round 7 gndret (record l8r2's own order, l8r2_gndret.out section 6: fandec and gndret anywhere
# in the round), then Layer 6's land, table and declarations. This record's draft goes after a board's circuit drafts and before
# the last-taker and the tables (board A: after 3g, before 3h; board B: after gndret, before Layer 6's).
ORDER = {
    "a": [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
          ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("l8r2", "packrtn"), ("l8r2", "slotlm"),
          ("l8r2", "fb01"), ("l8p", "ptc"), ("l4e11", "dd7"), ("d8dec31", "mainpb"), ("l6r2", "lcsc")],
    "b": [("l8gnd", "gnd002"), ("l8r2", "fans12"), ("l8r2", "fandec"), ("l8r2", "panel5v"), ("l8r2", "ph4"), ("l8r2", "rt500"),
          ("l8r2", "gndret"), ("l6r2", "xal_land"), ("l6r2", "lcsc"), ("l6r2", "intent")],
}
SLOT = {"a": 16, "b": 7}
ROUND7 = (("l8r2", "fandec"), ("l8r2", "gndret"))     # record l8r2's round 7 drafts: without them board B's composition is the old state
SHEETS = {"tps62933": "v2/vendor/ti/ti-tps62933.pdf", "vh": "v2/vendor/connectors/jst-vh-catalogue.pdf",
          "xal60": "v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf", "ap2112": "v2/vendor/diodes/diodes-ap2112-ldo.pdf",
          "lm5176": "v2/vendor/ti/lm5176-datasheet.pdf", "h743": "v2/vendor/st/st-stm32h743xi-datasheet.pdf"}
OWN = ["v2/docs/records/l9t5/" + f for f in ("check_l9t5_netlist.py", "apply_gen_sch_a_iocbuck.py", "apply_gen_sch_b_iocbuck.py",
                                              "inputs/apply_gen_sch_b_iocbuck-bdbed9bb.py", "inputs/apply_gen_sch_a_iocbuck-7c28f9da.py",
                                              "inputs/apply_gen_sch_b_iocbuck-7c28f9da.py", "inputs/SOURCES.txt",
                                              "inputs/coordinator-cases-2026-10-04-rev3.md", "l9t5_case.py", "l9t5_case.out")]
ENGINE = ["v2/ecad/tools/kisch.py", "v2/ecad/tools/intent.py", "v2/ecad/tools/idc_pads.py", "v2/docs/records/l8p/gen_netlist.py",
          "v2/docs/records/l8p/check_l8p_netlist.py"]
OTHERS = ["v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/l8r2/l8r2_gndret.out", "v2/docs/records/l8r2/check_gndret_netlist.py",
          "v2/docs/ASSEMBLY.md", "v2/ecad/tools/pcb_interfaces.yaml", "v2/docs/records/rv-pwr/pwr_budget.py"]
# the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
DIV_TOL, DIV_TCR, DIV_DT = 0.001, 25e-6, 65.0    # the divider's parts (stream s99a's pair, as U41) and its temperature span: as U41's record
ETA_DECL = 0.90                                  # U601's declared efficiency (the draft's intent, as U41's): NOT PLOTTED at 5 V out
ETA_SENS = 0.85                                  # a lower bound shown for it (the floor record l9t5 uses for unplotted points)
EXTRA_EN = 1                                     # the TPS62933 EN pins U601 adds to RAIL_EN
RAIL_BUDGET = 0.02                               # +5V_IOC's declared drop budget (both drafts), of 5.0 V: the copper of both boards


def rel(p):
    return os.path.relpath(p, ROOT)


def sha(p, n=16):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l9t5_drafts: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


_PDF = {}


def pdf(key):
    if key not in _PDF:
        try:
            r = subprocess.run(["pdftotext", "-layout", os.path.join(ROOT, SHEETS[key]), "-"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            refuse("pdftotext could not read %s (%s)" % (SHEETS[key], e))
        _PDF[key] = r.stdout.decode("utf-8", "replace")
    return _PDF[key]


def flat(t):
    return " ".join(t.split())


def text(relpath):
    return open(os.path.join(ROOT, relpath), encoding="utf-8").read()


# ------------------------------------------------------------------------------------------------ the makers' figures, read
def figures():
    P = {}
    t = pdf("tps62933")
    P["tps_rev"] = need(t, r"(SLUSEA4D)", "the TPS62933 sheet's number").group(1)
    P["tps_a"] = float(need(flat(t), r"(\d)-A \(TPS62933 and TPS62933x\)", "the TPS62933's rating").group(1))
    m = need(t, r"TPS62933 and TPS62933x\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\n\s*IHS_LIMIT\s+High-side MOSFET current limit", "IHS_LIMIT")
    P["ihs"] = tuple(float(x) for x in m.groups())
    m = need(t, r"TPS62933 and TPS62933x\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\n\s*ILS_LIMIT\s+Low-side MOSFET current limit", "ILS_LIMIT")
    P["ils"] = tuple(float(x) for x in m.groups())
    m = need(t, r"TJ = \u201340°C to 150°C\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "VFB over TJ -40 to 150 C")
    P["vfb"] = tuple(float(x) / 1000.0 for x in m.groups())
    P["ifb"] = float(need(t, r"IFB\s+Input leakage current\s+VFB = 0\.8 V\s+([\d.]+)\s+μA", "IFB").group(1)) * 1e-6
    P["ven_rise"] = float(need(t, r"VEN_RISE\s+Enable threshold\s+Rising enable threshold\s+[\d.]+\s+([\d.]+)\s+V", "VEN_RISE").group(1))
    P["ip"] = float(need(t, r"Ip\s+EN pullup current\s+VEN = 1\.0 V\s+([\d.]+)\s+µA", "Ip").group(1)) * 1e-6
    P["ih"] = float(need(t, r"Ih\s+EN pullup hysteresis current\s+VEN = 1\.5 V\s+([\d.]+)\s+µA", "Ih").group(1)) * 1e-6
    P["en_rec"] = float(need(t, r"^\s+EN\s+\u20130\.1\s+([\d.]+)\s*$", "EN's recommended maximum (8.3)").group(1))
    P["en_abs"] = float(need(t, r"Input voltage\s+EN\s+\u20130\.3\s+([\d.]+)", "EN's absolute maximum (8.1)").group(1))
    need(t, r"Hiccup mode is also incorporated for sustained short circuits\.", "the hiccup clause (9.3.12)")
    need(t, r"IHS _ LIMIT \+ILS _ LIMIT\s*\n\s*IOMAX \|", "Equation 11")
    need(t, r"TPS62933 Efficiency, VOUT = 3\.3 V", "the TPS62933's plotted efficiency points")
    P["eff_5v_variants"] = "TPS62932, TPS62933F and TPS62933O" if all(
        re.search(r"%s Efficiency, VOUT = 5 V" % v, t) for v in ("TPS62932", "TPS62933F", "TPS62933O")) else refuse("the 5 V curves")
    P["eff_5v_own"] = bool(re.search(r"TPS62933 Efficiency, VOUT = 5 V", t))
    t = pdf("vh")
    P["vh_a"] = float(need(t, r"Current rating: (\d+) A", "the VH's rating").group(1))
    P["vh_awg"] = int(need(t, r"When using AWG #(\d+) with the standard type header", "the VH rating's wire").group(1))
    m = need(t, r"Contact resistance: Initial value/ (\d+) m\S max\.\s*\n\s*After test/ (\d+) m\S max\.", "the VH's contact resistance")
    P["vh_r"] = (float(m.group(1)) * 1e-3, float(m.group(2)) * 1e-3)
    need(t, r"Do not branch in parallel current which exceeds the rated current\.", "the VH's note on parallel branching")
    m = need(pdf("xal60"), r"XAL6060-682ME_\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "XAL6060-682's row")
    P["l_isat"] = float(m.group(5))
    need(pdf("xal60"), r"DC current at 25°C that causes an inductance drop of 30% \(typ\)", "Coilcraft's definition of Isat (note 5)")
    t = pdf("ap2112")
    P["ap_rev"] = need(t, r"Document number: (DS39724 Rev\. 2 - 2)", "the AP2112 sheet's number").group(1)
    sec = need(t, r"AP2112-3\.3 Electrical Characteristics.*?ISHORT", "the AP2112-3.3 table", re.S).group(0)
    P["ap_vout_hi"] = float(need(sec, r"VOUT\s+VOUT\s*\n.*?\n.*?\*([\d.]+)%\s+\*([\d.]+)%", "VOUT's band", re.S).group(2)) / 100.0
    P["ap_imax"] = float(need(sec, r"IOUT\(MAX\)\s+Maximum Output Current\s+VIN = 4\.3V, VOUT = [\d.]+V to [\d.]+V\s+(\d+)", "IOUT(MAX)").group(1)) / 1000.0
    P["ap_drop"] = float(need(sec, r"IOUT = 600mA\s+\u2014\s+250\s+(\d+)", "the dropout at 600 mA").group(1)) / 1000.0
    P["ap_vin_max"] = float(need(t, r"VIN\s+Supply Voltage\s+([\d.]+)\s+([\d.]+)\s+V", "VIN's range").group(2))
    # the supervisors' current: ST DS12110 Rev 10 Table 30 (p.111), 400 MHz, VOS1, all peripherals enabled: typ, max at TJ 25, 85, 105, 125 C
    t = pdf("h743")
    need(t, r"DS12110 Rev 10", "the H743 sheet's revision")
    need(t, r"Table 30\. Typical and maximum current consumption in Run mode, code with data processing\s*\n\s*running from ITCM, regulator ON", "Table 30")
    m = need(t, r"^\s+400\s+(\d+)\s+(\d+)\(3\)\s+(\d+)\s+(\d+)\(3\)\s+(\d+)\s*$", "Table 30's 400 MHz row with all peripherals enabled")
    P["h7"] = tuple(float(x) / 1000.0 for x in m.groups())          # typ, 25 C, 85 C, 105 C, 125 C
    rv = text("v2/docs/records/rv-pwr/pwr_budget.py")
    m = need(rv, r"400 MHz all peripherals on 165 mA typ, (\d+) mA max at TJ 85 C; plus ([\d.]+) A declared", "rv-pwr's supervisors' HIGH")
    P["rv_h7"], P["rv_other"] = float(m.group(1)) / 1000.0, float(m.group(2))
    # the leads' make: ASSEMBLY.md section 4 and the contract's harness row
    m = need(text("v2/docs/ASSEMBLY.md"), r"\| Device rail .*?\| A22 `J_5V_DEV` \(VH\) \| B16 `J_5V_DEV` \(VH\) \| (\d+) AWG, (\d+) mm \| VH crimp both ends \|", "ASSEMBLY.md's device lead row")
    P["lead"] = (int(m.group(1)), int(m.group(2)))
    m = need(flat(text("v2/ecad/tools/pcb_interfaces.yaml")), r'harness: "JST-VH pairs, (\d+) AWG on the four 5 V leads and 18 AWG on J_54V, (\d+) mm \(cable; ASSEMBLY\.md section 4\)"', "IF-AB-POWER's harness row")
    if (int(m.group(1)), int(m.group(2))) != P["lead"]:
        refuse("IF-AB-POWER's harness row and ASSEMBLY.md's device lead row disagree")
    return P


def gndret():
    """record l8r2's round 7 output in this tree (parsed, never typed): the lead's conductor, the return's division at C-DEV rev 1 with
    this record's draft composed (six leads) and at the declared upper bound, and L8R2-F31's state."""
    t = open(GNDRET_OUT, encoding="utf-8").read()
    G = {}
    m = need(t, r"J_5V_DEV\s+AWG16\s+1 conductor\s+([\d.]+) mOhm each at 20 C,\s+([\d.]+) at ([\d.]+) C", "l8r2's lead conductor (3c)")
    G["r20"], G["rhot"], G["t_hot"] = float(m.group(1)) * 1e-3, float(m.group(2)) * 1e-3, float(m.group(3))
    row = re.compile(r"^\s+(K\d)\s.*?\s([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(MODEL|BOUND)(.*)$", re.M)

    def block(pat, what):
        m_ = need(t, pat, what, re.M | re.S)
        rows = {k: dict(lead=float(a), largest=float(b), j54=float(c), ribbon=float(d_), ribbons=float(e), mv=float(f), label=(lab + tail).strip())
                for k, a, b, c, d_, e, f, lab, tail in row.findall(m_.group(2))}
        if sorted(rows) != ["K0", "K1", "K2", "K3", "K4", "K5"]:
            refuse("%s: its six rows no longer read" % what)
        return float(m_.group(1)), rows
    G["cdev_total"], G["cdev"] = block(r"C-DEV rev 1's state \(PS-ALLTX, HIGH, the least load voltage\) with Layer 9's draft composed, six leads: ([\d.]+) A\n(.*?)\n\s+the upper bound \(i\), five leads",
                                       "l8r2's division at C-DEV rev 1 with six leads (3d)")
    G["ub_total"], G["ub"] = block(r"the upper bound \(i\) with Layer 9's draft, six leads: ([\d.]+) A\n(.*?)\n\s+READ\.", "l8r2's division at the upper bound with six leads (3d)")
    m = need(t, r"total ([\d.]+) A = S1 ([\d.]+) \+ S2 ([\d.]+) \+ S3 ([\d.]+) \+ U7 ([\d.]+) \+ U601 ([\d.]+), MODEL", "l8r2's C-DEV total (6)")
    G["total"], G["parts"] = float(m.group(1)), tuple(float(x) for x in m.groups()[1:])
    G["vh_hot"] = float(need(t, r"([\d.]+) A at 76\.25 C; the printed 10 A is what the rows below are judged at", "l8r2's comparator at the inside air (3b)").group(1))
    need(t, r"L8R2-F31 OPEN \(KNOWN DEFECT of the A to B power interface", "L8R2-F31's state")
    need(t, r"L8R2-F35 FOR LAYER 9'S AUTHOR \(record l9t5\)", "L8R2-F35")
    return G


def case_module():
    sp = importlib.util.spec_from_file_location("l9t5_case_for_drafts", CASE_PY)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ drafts and compositions
def draft(rec, name, board):
    return os.path.join(RECS, rec, "apply_gen_sch_%s_%s.py" % (board, name))


def run(script, target, board):
    """(returncode, the last line it printed): d8dec31's drafts take the committed netlist, the others --write."""
    args = [script, target, NET[board]] if "/d8dec31/" in script.replace(os.sep, "/") else [script, target, "--write"]
    r = subprocess.run([sys.executable, "-B"] + args, capture_output=True)
    lines = (r.stdout if r.returncode == 0 else r.stderr).decode("utf-8", "replace").strip().splitlines()
    return r.returncode, (lines[-1] if lines else "")


def scrub(s, d):
    return s.replace(d, "<scratch>")


def seq_of(board, mine_at=None, skip=(), mine=None):
    seq = [draft(r, n, board) for r, n in ORDER[board] if (r, n) not in skip]
    if mine_at is None:
        return seq
    at = SLOT[board] if mine_at == "slot" else (0 if mine_at == "first" else len(seq))
    if skip and mine_at == "slot":
        at -= sum(1 for x in ORDER[board][:SLOT[board]] if x in skip)
    return seq[:at] + [mine or MINE[board]] + seq[at:]


def compose(board, seq, d, tag):
    p = os.path.join(d, tag + "_gen_sch_%s.py" % board)
    shutil.copy(GEN[board], p)
    res = []
    for s in seq:
        rc, msg = run(s, p, board)
        res.append((os.path.relpath(s, RECS), "OK" if rc == 0 else "REFUSED (%s)" % scrub(msg, d), msg))
        if rc:
            break
    ok = len(res) == len(seq) and all(v == "OK" for _s, v, _m in res)
    return p, res, ok


STMT_F = ("ic", "part", "c", "r", "tp", "nfet", "pfet5", "ph", "q", "esd", "efuse", "synth", "vh2", "_tvs", "tvs")
TOKEN = re.compile(r"\b(RT\d{1,3}|[RCDLQUHF]\d{1,3}|J_[A-Z0-9_]+|TP\d{1,3}|W_[A-Z0-9]+)\b(?!-)")


def drawn(text_):
    """{designator: count} of the literal part calls (a call's first argument a constant designator), read with ast."""
    from collections import Counter
    c = Counter()
    for n in ast.walk(ast.parse(text_)):
        if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            f = n.func.id if isinstance(n.func, ast.Name) else n.func.attr if isinstance(n.func, ast.Attribute) else ""
            if f in STMT_F and TOKEN.fullmatch(n.args[0].value):
                c[n.args[0].value] += 1
    return c


def declared_adds(script):
    sp = importlib.util.spec_from_file_location("adds_" + re.sub(r"\W", "_", os.path.relpath(script, ROOT)), script)
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
    except Exception:
        return set()
    return set(getattr(m, "ADDS", ()))


def adds_per_draft(board, seq, d):
    p = os.path.join(d, "adds_gen_sch_%s.py" % board)
    shutil.copy(GEN[board], p)
    before = open(p, encoding="utf-8").read()
    out = {}
    for s in seq:
        rc, msg = run(s, p, board)
        if rc:
            break
        after = open(p, encoding="utf-8").read()
        out[os.path.relpath(s, RECS)] = (set(drawn(after)) - set(drawn(before))) | declared_adds(s)
        before = after
    return out, before


def mainpb_takes(msg):
    m = re.search(r"\((R\d+), (C\d+)\)", msg)
    return m.groups() if m else None


# ------------------------------------------------------------------------------------------------ netlists
def netlist(board, generator, d, tag):
    out = os.path.join(d, "%s_%s.net" % (tag, board))
    rc, log, table = GN.run(generator, out, PROJECT[board])
    if rc:
        return rc, scrub((log.strip().splitlines() or [""])[-1], d), None
    return 0, out, table


def pins_of(nl):
    return {(r, p): n for r, d in nl["pins"].items() for p, n in d.items()}


def mutate(path, d, tag, swaps):
    raw = open(path, encoding="utf-8").read()
    for (ra, pa), (rb, pb) in swaps:
        a = '(node (ref "%s") (pin "%s"))' % (ra, pa)
        b = '(node (ref "%s") (pin "%s"))' % (rb, pb)
        if raw.count(a) != 1 or raw.count(b) != 1:
            refuse("the mutation's nodes are not in the netlist once: %s %s" % (a, b))
        raw = raw.replace(a, "\0A").replace(b, a).replace("\0A", b)
    p = os.path.join(d, tag + ".net")
    open(p, "w", encoding="utf-8").write(raw)
    return p


def check(paths, label):
    buf = io.StringIO()
    kit, verdicts = CHK.run(paths, ROOT, buf, label=label)
    return kit, verdicts, buf.getvalue()


def loads_sum(intent, net):
    r = CHK.rails_of(intent).get(net) or {}
    return math.fsum((r.get("loads") or {}).values())


def decl_line(letter, intent, basis):
    v, why = CHK.decl(letter, intent, basis)
    return v, "%s DECL %s%s" % (letter.upper(), v, (": " + "; ".join(why[:3])) if why else "")


# ------------------------------------------------------------------------------------------------ the record
def main():
    out = []
    w = out.append
    P = figures()
    G = gndret()
    cm = case_module()
    R = cm.compute()
    C, case = R["C"], R["case"]
    # the basis of the declarations (C-DEV rev 1's own method: Layer 9's budget at HIGH, every load at constant power at the rail's least
    # load voltage), computed here, never typed
    lo, nom, hi = CHK.vout_band(56.2e3, 10.7e3, DIV_TOL, DIV_TCR, DIV_DT, P["ifb"])
    if abs(P["vfb"][0] - CHK.VFB[0]) > 1e-9 or abs(P["vfb"][2] - CHK.VFB[2]) > 1e-9:
        refuse("the checker's VFB is not the sheet's")
    dev_w = C["i_least"] * C["v_least"]
    lead_w = dev_w - C["ioc_in_w"]
    ioc_v_least = lo - RAIL_BUDGET * 5.0
    ioc_bound = C["ioc_in_w"] / ioc_v_least
    if abs(lead_w / C["v_least"] - C["b_i_least"]) > 1e-9:
        refuse("the device lead's case current is not record l9t5's out 5 figure")
    w("l9t5_drafts: Layer 9 record l9t5, task T5 rounds 2 and 3: I-03 (C-DEV rev 1) drafted for boards A and B, composed, regenerated, mutated and judged (MESHSAT-1357)")
    w("prototype design; nothing built, bought, powered or measured; nothing applied to the tree; every statement is about generator text, netlists and the makers' sheets")
    w("")
    # 1. inputs
    w("1. INPUTS, pinned by sha256")
    others = sorted({draft(r, n, b) for b in "ab" for r, n in ORDER[b]})
    inputs = [GEN["a"], GEN["b"]] + [os.path.join(ROOT, p) for p in ENGINE] + others + [NET["a"], NET["b"]]
    inputs += [os.path.join(ROOT, p) for p in SHEETS.values()] + [os.path.join(ROOT, p) for p in OWN] + [os.path.join(ROOT, p) for p in OTHERS]
    for p in inputs:
        if not os.path.isfile(p):
            refuse("input %s is missing" % rel(p))
        w("   %s %s" % (sha(p), rel(p)))
    src = open(os.path.join(HERE, "inputs", "SOURCES.txt"), encoding="utf-8").read()
    for f in ("apply_gen_sch_b_iocbuck-bdbed9bb.py", "apply_gen_sch_a_iocbuck-7c28f9da.py", "apply_gen_sch_b_iocbuck-7c28f9da.py", "coordinator-cases-2026-10-04-rev3.md"):
        if ("%s sha256 %s" % (f, sha(os.path.join(HERE, "inputs", f), 64))) not in src:
            refuse("SOURCES.txt does not name inputs/%s at its sha256" % f)
    w("   the four copies filed in rounds 2 and 3 equal the sha256 SOURCES.txt names: yes")
    w("")
    tree_before = {b: sha(GEN[b], 64) for b in "ab"}
    PICKS = {}
    with tempfile.TemporaryDirectory(prefix="l9t5_") as d:
        # 2. each draft alone
        w("2. EACH DRAFT ON A SCRATCH COPY (check, apply once, refuse a second time, refuse the tree's own generator)")
        STEP2 = []
        for b in "ab":
            s = MINE[b]
            t = os.path.join(d, "alone_gen_sch_%s.py" % b)
            shutil.copy(GEN[b], t)
            pre = sha(t, 64)
            r1 = subprocess.run([sys.executable, "-B", s, t], capture_output=True)
            ok1 = r1.returncode == 0 and b"CHECK OK" in r1.stdout and sha(t, 64) == pre
            r2 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            n_ed = re.search(rb"WRITTEN, (\d+) edit", r2.stdout)
            r3 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            r4 = subprocess.run([sys.executable, "-B", s, GEN[b], "--write"], capture_output=True)
            STEP2.append(ok1 and r2.returncode == 0 and bool(n_ed) and r3.returncode == 3 and r4.returncode == 3 and b"NOT RELEASED" in r4.stderr)
            w("   %s: check %s; applied %s (%s edits); second application %s; the tree's gen_sch_%s.py %s" % (
                os.path.basename(s), "OK" if ok1 else "FAILED", "OK" if r2.returncode == 0 and n_ed else "FAILED", n_ed.group(1).decode() if n_ed else "?",
                "refused" if r3.returncode == 3 else "NOT REFUSED", b,
                "refused (NOT RELEASED)" if r4.returncode == 3 and b"NOT RELEASED" in r4.stderr else "NOT REFUSED"))
        OLD = {}
        for tag, b, s, what in (("r1b", "b", OLD_R1_B, "board B's round 1 text (bdbed9bb)"), ("r2a", "a", OLD_R2["a"], "board A's round 2 text (7c28f9da)"),
                                ("r2b", "b", OLD_R2["b"], "board B's round 2 text (7c28f9da)")):
            t = os.path.join(d, "%s_gen_sch_%s.py" % (tag, b))
            shutil.copy(GEN[b], t)
            r = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            n_old = re.search(rb"WRITTEN, (\d+) edit", r.stdout)
            OLD[tag] = (b, t, r.returncode)
            w("   %s, inputs/%s: applied %s (%s edits); section 4 regenerates it as an old state" % (
                what, os.path.basename(s), "OK" if r.returncode == 0 else "FAILED", n_old.group(1).decode() if n_old else "?"))
        if any(sha(GEN[b], 64) != tree_before[b] for b in "ab"):
            refuse("a draft wrote into the tree")
        w("   the tree's generators are unchanged: yes")
        w("")
        # 3. composition
        w("3. COMPOSITION IN L4-E9'S CHANGE-LIST ORDER (records/l4e9/L4-POWER-ARCHITECTURE.md section 3, with record l8r2's round 7 drafts fandec and")
        w("   gndret in board B's round; this record's draft after the board's circuit drafts, before the last-taker and the tables)")
        comp = {}
        ORDERS_OK = {}
        for b in "ab":
            p, res, ok = compose(b, seq_of(b, "slot"), d, "fwd")
            comp[b] = (p, ok)
            ORDERS_OK[b] = [ok]
            w("   board %s, this record's draft in its place:" % b.upper())
            for s, v, _m in res:
                w("     %-46s %s" % (s, v))
            for tag, at in (("first", "first"), ("last", "last")):
                _p, res2, ok2 = compose(b, seq_of(b, at), d, tag)
                ORDERS_OK[b].append(ok2)
                w("   board %s, this record's draft %s: %s" % (b.upper(), "first, then the order" if at == "first" else "after the whole order",
                                                            "every step OK" if ok2 else "; ".join("%s %s" % (s, v) for s, v, _m in res2 if v != "OK")))
        # mainpb's picks
        _p, res_slot, _ok = compose("a", seq_of("a", "slot"), d, "mp1")
        _p, res_base, _ok = compose("a", seq_of("a"), d, "mp0")
        picks = {k: mainpb_takes(dict((s, m) for s, _v, m in rs).get("d8dec31/apply_gen_sch_a_mainpb.py", "")) for k, rs in (("with", res_slot), ("without", res_base))}
        _p, res_last, _ok = compose("a", seq_of("a", "last"), d, "mp2")
        picks["after"] = mainpb_takes(dict((s, m) for s, _v, m in res_last).get("d8dec31/apply_gen_sch_a_mainpb.py", ""))
        row33 = need(text("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"),
                     r"LAST in board A's round, after 3a to 3g, where it takes (R\d+) and (C\d+)", "L4-E9's row 33").groups()
        PICKS.update(picks, row33=row33)
        w("   d8dec31's mainpb (the next free R and C at apply time): without this record's draft it takes %s and %s on this tree (L4-E9's row 33" % picks["without"])
        w("     names %s and %s: stale already, the later drafts took those);" % row33)
        w("     with this record's draft before it, %s and %s; with this record's draft after it, %s and %s (finding L9T5-F02)" % (picks["with"] + picks["after"]))
        w("")
        w("   THE DESIGNATORS EACH DRAFT ADDS (the forward order; part calls read with ast, and each draft's declared ADDS)")
        DISJ = {}
        for b in "ab":
            adds, final = adds_per_draft(b, seq_of(b, "slot"), d)
            mine = adds.get(os.path.relpath(MINE[b], RECS), set())
            meets = {k: sorted(v & mine) for k, v in adds.items() if k != os.path.relpath(MINE[b], RECS) and v & mine}
            dup = sorted(r for r, n in drawn(final).items() if n > 1)
            DISJ[b] = not meets and not dup
            w("   board %s, this record's: %s" % (b.upper(), ", ".join(sorted(mine, key=lambda x: (re.sub(r"\d", "", x), int(re.sub(r"\D", "", x) or 0))))))
            w("   board %s, against every other draft's: %s; literal part calls drawn twice in the composed generator: %s" % (
                b.upper(), "DISJOINT" if not meets else "MEETS %s" % meets, ", ".join(dup) if dup else "none"))
        w("")
        # 4. regeneration
        w("4. REGENERATION ON THE RUNNER (record l8p's gen_netlist.py: the generator's own part table, no KiCad), THE NETLIST CHECK AND THE DECLARATION CHECK")
        for b in "ab":
            rc, path, table = netlist(b, GEN[b], d, "base")
            if rc:
                refuse("board %s's own generator did not run: %s" % (b, path))
            a_, k_ = CHK.read(open(path, "rb").read()), CHK.read(open(NET[b], "rb").read())
            pa, pk = pins_of(a_), pins_of(k_)
            diff = [x for x in sorted(set(pa) | set(pk)) if pa.get(x) != pk.get(x)]
            nc = [x for x in diff if pa.get(x) is None and str(pk.get(x)).startswith("unconnected-")]
            w("   board %s unpatched: %d connected pins against the committed KiCad netlist's %d; differences %d, all KiCad's names for open pins: %s" % (
                b.upper(), len(pa), len(pk), len(diff), "yes" if len(nc) == len(diff) else "NO"))
        kit0, _v, txt = check({b: NET[b] for b in "ab"}, lambda x: "committed board %s (KiCad's export)" % x.upper())
        w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        # the wall port's limit, read from the composed board A's own declaration below; the basis for both checks
        rc, path_ac, table_ac = netlist("a", comp["a"][0], d, "composed")
        if rc or not comp["a"][1]:
            refuse("board A's composition did not regenerate: %s" % path_ac)
        ia = table_ac["intent"]
        wall = CHK.rails_of(ia).get("VBUS_WALL") or {}
        if wall.get("fed_from") != "+5V_DEV" or not wall.get("amps_peak"):
            refuse("board A's wall port rail no longer reads")
        basis = {"dev_lead": C["b_i_least"], "ioc": ioc_bound, "wall": float(wall["amps_peak"])}
        hot = float(need(CHK.rails_of(ia)["+5V_DEV"]["note"], r"or ([\d.]+) A with the assumed 50 K shunt temperature change", "the note's conditional minimum").group(1))
        alone, V_ALONE = {}, {}
        for b in "ab":
            t = os.path.join(d, "regen_gen_sch_%s.py" % b)
            shutil.copy(GEN[b], t)
            if run(MINE[b], t, b)[0] != 0:
                refuse("this record's board %s draft refused a clean copy" % b)
            rc, path, table = netlist(b, t, d, "alone")
            if rc:
                refuse("board %s with this record's draft alone did not run: %s" % (b, path))
            alone[b] = (path, table)
            w("   board %s with this record's draft alone: the generator ran to its end (%d parts, %d unplaced, intent written: %s)" % (
                b.upper(), len(table["parts"]), len(table["unplaced"]), "yes" if table["intent_written"] else "NO"))
        kit_alone, V_ALONE, txt = check({b: alone[b][0] for b in "ab"}, lambda x: "board %s, this record's draft alone" % x.upper())
        w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        D_ALONE = {}
        for b in "ab":
            D_ALONE[b], line = decl_line(b, alone[b][1]["intent"], basis)
            w("       %s" % line)
        w("   board A composed in L4-E9's order:")
        w("     the generator ran to its end (%d parts, %d unplaced, intent written: %s)" % (len(table_ac["parts"]), len(table_ac["unplaced"]), "yes" if table_ac["intent_written"] else "NO"))
        w("   board B composed in L4-E9's order with record l8r2's round 7 drafts:")
        rc_bc, path_bc, table_bc = netlist("b", comp["b"][0], d, "composed")
        if rc_bc or not comp["b"][1]:
            refuse("board B's composition did not regenerate: %s" % path_bc)
        ib = table_bc["intent"]
        w("     the generator ran to its end (%d parts, %d unplaced, intent written: %s)" % (len(table_bc["parts"]), len(table_bc["unplaced"]), "yes" if table_bc["intent_written"] else "NO"))
        kit_c, V_COMP, txt = check({"a": path_ac, "b": path_bc}, lambda x: "board %s composed in L4-E9's order" % x.upper())
        w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        D_COMP = {}
        for b, it in (("a", ia), ("b", ib)):
            D_COMP[b], line = decl_line(b, it, basis)
            w("       %s" % line)
        ij = os.path.join(d, "composed_b_intent.json")
        json.dump(ib, open(ij, "w", encoding="utf-8"))
        rg = subprocess.run([sys.executable, "-B", GNDRET_CHK, path_bc, ij], capture_output=True)
        GND_CHK = rg.returncode
        w("     record l8r2's own check of the return's declaration (check_gndret_netlist.py) on the same netlist and intent: %s" % (
            "DRAWN (exit 0)" if rg.returncode == 0 else "exit %d: %s" % (rg.returncode, scrub((rg.stdout + rg.stderr).decode("utf-8", "replace").strip().splitlines()[-1], d))))
        w("   THE OLD STATES (each must stop or FAIL)")
        b_, t_, _rc = OLD["r1b"]
        rc_o1, line_o1, _t = netlist(b_, t_, d, "old_r1b")
        w("     O1 board B, round 1's text alone: %s" % ("the generator ran (NOT EXPECTED)" if rc_o1 == 0 else "the generator refused: %s" % line_o1))
        O2 = {}
        for tag in ("r2a", "r2b"):
            b_, t_, _rc = OLD[tag]
            rc_o, path_o, table_o = netlist(b_, t_, d, "old_" + tag)
            if rc_o:
                refuse("round 2's board %s text no longer regenerates: %s" % (b_, path_o))
            O2[b_], line = decl_line(b_, table_o["intent"], basis)
            w("     O2 board %s, round 2's text alone (the netlist DRAWN as before): %s" % (b_.upper(), line))
        q, _r, _ok = compose("b", seq_of("b", "slot", skip=ROUND7), d, "pre_t5b")
        rc_o3, line_o3, _t = netlist("b", q, d, "pre_t5b")
        w("     O3 board B composed without record l8r2's round 7 drafts (the tree before T5b): %s" % (
            "the generator ran (NOT EXPECTED)" if rc_o3 == 0 else "the generator refused: %s" % line_o3))
        w("   THE MUTATIONS (each must FAIL)")
        muts = [("a", path_ac, "J_5V_IOC's pins 1 and 2 exchanged on board A (the lead reversed)", [(("J_5V_IOC", "1"), ("J_5V_IOC", "2"))]),
                ("a", path_ac, "U601's EN and SS exchanged (the buck no longer on RAIL_EN)", [(("U601", "2"), ("U601", "7"))]),
                ("a", path_ac, "R601's +5V_IOC end and R602's ground end exchanged (the divider inverted: 0.95 V out)", [(("R601", "1"), ("R602", "2"))]),
                ("b", path_bc, "U50's VIN and D1's cathode exchanged (controller B's LDO back on +5V_DEV)", [(("U50", "1"), ("D1", "1"))]),
                ("b", path_bc, "J_5V_IOC's pins 1 and 2 exchanged on board B (the lead reversed)", [(("J_5V_IOC", "1"), ("J_5V_IOC", "2"))])]
        MUT = []
        for i, (b, src_, what, sw) in enumerate(muts, 1):
            mp = mutate(src_, d, "mut%d_%s" % (i, b), sw)
            kitm, _v, txt = check({b: mp}, lambda x, what=what, i=i: "mutation %d, board %s composed: %s" % (i, x.upper(), what))
            MUT.append(kitm)
            w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        w("")
        # 5. the intent
        w("5. THE DECLARATIONS THE PATCHED GENERATORS WRITE (their intent, from the two compositions), EACH BESIDE ITS BASIS")
        q0, _r, _ok = compose("a", seq_of("a"), d, "a_without")
        rc, _p0, t0 = netlist("a", q0, d, "a_without")
        ia0 = t0["intent"] if rc == 0 else refuse("board A's composition without this record's draft did not regenerate")
        ra, ra0 = CHK.rails_of(ia), CHK.rails_of(ia0)
        r_ = ra["+5V_IOC"]
        w("   board A, rail +5V_IOC: %.1f V, %.2f A typical, %.4f A peak, source %s, switch %s, fed from %s, efficiency %s, v_work %s, budget %s share %s, loads %s" % (
            r_["volts"], r_["amps_typ"], r_["amps_peak"], r_["source"], r_.get("switch"), r_.get("fed_from"), r_.get("efficiency"), r_.get("v_work"),
            r_.get("budget"), r_.get("share"), ", ".join("%s %.2f" % kv for kv in sorted(r_["loads"].items()))))
        w("     the peak's basis: rv-pwr's HIGH for the supervisors, %.4f W at the LDOs' inputs, at constant power at %.4f V (U601's least %.4f V less" % (C["ioc_in_w"], ioc_v_least, lo))
        w("     the rail's %.0f %%): %.6f A, rounded up to %.4f A (MODEL on DECLARED loads)" % (RAIL_BUDGET * 100, ioc_bound, CHK.ceil4(ioc_bound)))
        dv, dv0 = ra["+5V_DEV"], ra0["+5V_DEV"]
        w("   board A, rail +5V_DEV: typical %.2f A (%.2f without this draft), peak %.4f A (%.4f), loads %s" % (
            dv["amps_typ"], dv0["amps_typ"], dv["amps_peak"], dv0["amps_peak"], ", ".join("%s %.2f" % kv for kv in sorted(dv["loads"].items()))))
        w("     the peak's basis: stream s99's construction, board B's lead %.4f A plus the wall port's %.4f A (VBUS_WALL's declared peak, U32's nominal limit)" % (
            CHK.ceil4(basis["dev_lead"]), basis["wall"]))
        vb, vb0 = loads_sum(ia, "VBAT"), loads_sum(ia0, "VBAT")
        w("   board A, rail VBAT: its declared loads sum to %.2f A (%.2f without this draft): Q32 %.2f (%.2f), U601 %.2f; peak %.1f A" % (
            vb, vb0, ra["VBAT"]["loads"]["Q32"], ra0["VBAT"]["loads"]["Q32"], ra["VBAT"]["loads"]["U601"], ra["VBAT"]["amps_peak"]))
        for n in ("IOCB_SW", "IOCB_BST"):
            x = ia["nodes"].get(n) or {}
            w("   board A, node %-8s v_max %s V%s" % (n, x.get("v_max"), ", rides on %s by %s V" % (x["rides_on"], x["bias_v"]) if x.get("rides_on") else ""))
        q1, _r, _ok = compose("b", seq_of("b"), d, "b_without")
        rc, _p1, t1 = netlist("b", q1, d, "b_without")
        ib0 = t1["intent"] if rc == 0 else refuse("board B's composition without this record's draft did not regenerate")
        rb, rb0 = CHK.rails_of(ib), CHK.rails_of(ib0)
        r_ = rb["+5V_IOC"]
        w("   board B, rail +5V_IOC: %.2f A typical, %.4f A peak, source %s, always on: %s, budget %s share %s, loads %s" % (
            r_["amps_typ"], r_["amps_peak"], r_["source"], "yes" if r_.get("always_on") else "NO", r_.get("budget"), r_.get("share"),
            ", ".join("%s %.2f" % kv for kv in sorted(r_["loads"].items()))))
        w("   board B, the three +3V3_IOCx rails fed from: %s" % ", ".join("%s %s" % (n, rb[n].get("fed_from")) for n in ("+3V3_IOCA", "+3V3_IOCB", "+3V3_IOCC")))
        dv, dv0 = rb["+5V_DEV"], rb0["+5V_DEV"]
        w("   board B, rail +5V_DEV (the device lead): typical %.2f A (%.2f without), its loads sum %.2f A (%.2f), peak %.4f A (%.4f without)" % (
            dv["amps_typ"], dv0["amps_typ"], loads_sum(ib, "+5V_DEV"), loads_sum(ib0, "+5V_DEV"), dv["amps_peak"], dv0["amps_peak"]))
        w("     the peak's basis: Layer 9's budget for this lead on C-DEV rev 1 with the draft, (%.4f - %.4f) W = %.4f W at %.4f V: %.6f A, rounded up" % (
            dev_w, C["ioc_in_w"], lead_w, C["v_least"], basis["dev_lead"]))
        w("     to %.4f A (MODEL); without the draft the lead's own case is %.4f A against the %.1f A declared (I-03 itself)" % (
            CHK.ceil4(basis["dev_lead"]), C["i_least"], dv0["amps_peak"]))
        g, g0 = rb["GND"], rb0["GND"]
        GND_ADD = loads_sum(ib, "GND") - loads_sum(ib0, "GND")
        GND = (g["amps_typ"], g["amps_peak"], g0["amps_peak"], loads_sum(ib, "GND"))
        w("   board B, rail GND (derived in the generator by record l8r2's gndret draft): sources %s;" % ", ".join(g["source"]))
        w("     %.2f A typical, %.4f A peak, the sum of the leads' declared peaks, an UPPER BOUND (%.4f A without this draft); its loads sum %.3f A" % (
            g["amps_typ"], g["amps_peak"], g0["amps_peak"], loads_sum(ib, "GND")))
        w("     (%.3f A without, %+.3f A: the three allocations leave +5V_DEV's derived ground loads and return as _IOC_LOADS)" % (loads_sum(ib0, "GND"), GND_ADD))
        bp = [x for x in ib.get("bypass", []) if x.get("cap") in ("C400", "C420", "C440")]
        w("   board B, the LDO input capacitors' bypass entries: %s" % "; ".join("%s at %s.%s on %s" % (x.get("cap"), x.get("part"), x.get("pin"), x.get("net")) for x in bp))
        nl_b = CHK.read(open(path_bc, "rb").read())
        on_dev = sorted(u for u, _r2, _c2 in CHK.LDOS if CHK.pin(nl_b, u, "1") == "+5V_DEV")
        dev_alloc = sorted(u for u, _r2, _c2 in CHK.LDOS if u in (dv.get("loads") or {}))
        w("")
    if any(sha(GEN[b], 64) != tree_before[b] for b in "ab"):
        refuse("the tree's generators changed during the run")

    # 6. electrical acceptance
    w("6. THE ELECTRICAL ACCEPTANCE ON C-DEV REV 1 (record l9t5 out 5 for the case figures; the makers' sheets read here)")
    w("   labels: PRINTED a maker's limit; TYPICAL a maker's typical figure; DECLARED a generator's or a record's declaration; MODEL this record's or another")
    w("   record's arithmetic; ASSUMPTION a figure no held document gives; SESSION a choice this record takes")
    w("   BOARD A'S HALF (U601, its network, its enable, the device rail's stage)")
    e1 = C["b_margin"] > 0
    w("   (1) U7, the device rail, on the case: %.4f A (MODEL: every load at constant power at %.4f V, the loads at rv-pwr's HIGH) against its" % (C["b_i_least"], C["v_least"]))
    w("       average loop's least %.4f A (PRINTED VSNS %.0f mV, LM5176 SNVSAI1D p.7; R43 %.0f mOhm at +%.0f %%, DECLARED): margin %+.4f A: %s" % (
        C["lim_min"], C["vsns"][0] * 1000, C["rs"] * 1000, C["tol"] * 100, C["b_margin"], "HOLDS" if e1 else "FAILS"))
    w("       (before: %.4f A, %+.4f A); the loop's highest %.4f A stays under J_5V_DEV's VH %.0f A (PRINTED): U7, R43 and its lead unchanged;" % (
        C["i_least"], C["lim_min"] - C["i_least"], C["lim_max"], P["vh_a"]))
    w("       with the draft U7's case no longer carries the supervisors at all, whatever they draw")
    s1 = basis["dev_lead"] + basis["wall"]
    w("       LABELLED SCENARIO, not the case (stream s99's declared tier: the wall host port at U32's nominal limit %.4f A as well; the case carries" % basis["wall"])
    w("       no wall port load): %.4f A against %.4f A, %+.4f A; against the note's conditional %.6f A (an assumed 50 K at the shunt), %+.4f A" % (
        s1, C["lim_min"], C["lim_min"] - s1, hot, hot - s1))
    ldo_i = 3 * (P["rv_h7"] + P["rv_other"])
    if abs(P["rv_h7"] - P["h7"][2]) > 1e-9 or abs(ldo_i - C["ioc_i_ldo"]) > 1e-9:
        refuse("rv-pwr's supervisors' HIGH is not Table 30's TJ 85 C figure")
    e2 = ioc_bound < P["tps_a"]
    w("   (2) U601 on the case: the three LDOs' own current %.4f A = 3 x (%.3f + %.3f): each H743 at %.0f mA, the maximum at TJ 85 C at 400 MHz with all" % (
        ldo_i, P["rv_h7"], P["rv_other"], P["rv_h7"] * 1000))
    w("       peripherals enabled (PRINTED, ST DS12110 Rev 10 Table 30 p.111; rv-pwr's HIGH) plus %.0f mA of its other parts (DECLARED); by the case's" % (P["rv_other"] * 1000))
    w("       method, constant power, %.4f W: %.4f A at U7's %.4f V (what leaves U7) and %.4f A at U601's own least load voltage %.4f V (MODEL," % (
        C["ioc_in_w"], C["b_buck_a"], C["v_least"], ioc_bound, ioc_v_least))
    w("       a bound: an LDO draws its output current, not constant power); the largest against U601's %.0f A rating (PRINTED, %s): %s" % (P["tps_a"], P["tps_rev"], "HOLDS" if e2 else "FAILS"))
    s2 = 3 * (P["h7"][4] + P["rv_other"])
    w("       LABELLED SCENARIO, not the case (Table 30's last column, TJ 125 C: %.0f mA): %.2f A of LDO current, under U601's %.0f A, but %.0f mA an LDO" % (
        P["h7"][4] * 1000, s2, P["tps_a"], (P["h7"][4] + P["rv_other"]) * 1000))
    w("       against the AP2112K's %.0f mA (PRINTED IOUT(MAX) minimum): the LDO bounds it first, with or without this draft (finding L9T5-F06)" % (P["ap_imax"] * 1000))
    iomax = (P["ihs"][2] + P["ils"][2]) / 2.0
    e3 = P["ihs"][2] < P["vh_a"] and iomax < P["vh_a"]
    w("   (3) U601's limit against J_5V_IOC's VH %.0f A (PRINTED, with AWG %d on the standard header): high-side limit %.1f / %.1f / %.1f A, low-side" % (
        P["vh_a"], P["vh_awg"], *P["ihs"]))
    w("       %.1f / %.1f / %.1f A (PRINTED); the output at most about (%.1f + %.1f) / 2 = %.2f A (Equation 11, approximate, on PRINTED maxima), hiccup" % (
        *P["ils"], P["ihs"][2], P["ils"][2], iomax))
    w("       on a sustained short (9.3.12): %s" % ("HOLDS" if e3 else "FAILS"))
    e4 = P["l_isat"] > P["ihs"][2]
    w("   (4) L601 XAL6060-682ME: Isat %.1f A (TYPICAL: Coilcraft's table, the current for a 30 %% inductance drop, typical, at 25 C) over the part's" % P["l_isat"])
    w("       %.1f A highest high-side limit (PRINTED): %s (round 2 labelled the Isat PRINTED; it is a typical figure)" % (P["ihs"][2], "HOLDS" if e4 else "FAILS"))
    e5 = 4.8 < lo and hi < P["ap_vin_max"]
    w("   (5) +5V_IOC's set point: 56.2k over 10.7k at 0.1 %% and %.0f ppm/K over %.0f K (DECLARED, stream s99a's pair, as U41), VFB %.3f to %.3f V over TJ" % (
        DIV_TCR * 1e6, DIV_DT, P["vfb"][0], P["vfb"][2]))
    w("       -40 to 150 C and IFB %.2f uA either way (PRINTED, its sign not printed): %.3f V nominal, %.4f to %.4f V; under the AP2112K's %.1f V input" % (
        P["ifb"] * 1e6, nom, lo, hi, P["ap_vin_max"]))
    w("       maximum (PRINTED): %s (the LDOs' least input is board B's item B3)" % ("HOLDS" if e5 else "FAILS"))
    rth = 100e3 * 39e3 / (100e3 + 39e3)
    n_en = 2 + EXTRA_EN
    v_en = {v: 39e3 / 139e3 * v + rth * n_en * (P["ip"] + P["ih"]) for v in (10.0, 16.8, 18.0)}
    e6 = v_en[18.0] < P["en_rec"] and v_en[10.0] > P["ven_rise"]
    w("   (6) RAIL_EN with U601's EN on it (R2 100k over R184 39k, DECLARED; the TPS62933's EN pull-up Ip %.1f uA and Ih %.1f uA, TYPICAL only, no limit" % (
        P["ip"] * 1e6, P["ih"] * 1e6))
    w("       printed; %d TPS62933 EN pins on the net, U12, U41 and U601): %.3f V at 10 V, %.3f V at 16.8 V, %.3f V at the SMCJ18A's 18 V standoff; U601" % (
        n_en, v_en[10.0], v_en[16.8], v_en[18.0]))
    w("       adds %.4f V; against VEN_RISE %.2f V maximum and EN's %.1f V recommended (%.0f V absolute) maximum (PRINTED): %s" % (
        rth * EXTRA_EN * (P["ip"] + P["ih"]), P["ven_rise"], P["en_rec"], P["en_abs"], "HOLDS" if e6 else "FAILS"))
    w("   (7) the enable relation (netlist, section 4 EN): +5V_DEV is up only while +3V3 is (U7's EN DEV_EN pulled to +3V3 by R42, driven by U27),")
    w("       +3V3 only while RAIL_EN is high (U12), and U601 is on RAIL_EN: the supervisors are up whenever the device rail is (record l9t5 out 5's condition)")
    nodes = case["nodes"]
    ioc_in = nodes["IOC"][0]
    eta_dev = nodes["DEV"][3]
    d_p = ioc_in * (1.0 / ETA_SENS - 1.0 / eta_dev)
    w("   (8) the upstream path: U601 on VBAT beside U41 (C603, C604 at its VIN, as C229, C230 at U41's); VBAT's declared loads unchanged in sum (section 5);")
    w("       on C-ALLTX rev 3 (record l9t5 out 1, at the case's VBAT %.3f V) the supervisors take %.4f W at their typical: through U7 at its declared %.2f" % (
        case["vbat"], ioc_in, eta_dev))
    w("       or through U601 at its declared %.2f (DECLARED, as U41; the TPS62933's own 5 V curve is %s; the %s are plotted) the case is unchanged" % (
        ETA_DECL, "plotted" if P["eff_5v_own"] else "NOT PLOTTED", P["eff_5v_variants"]))
    w("       (%.4f V); with U601 at %.2f (a bound shown, ASSUMPTION) the case's input rises %.4f W, about %+.4f V of rest voltage at %.0f A (MODEL, first order)" % (
        case["need"], ETA_SENS, d_p, d_p / case["i"], case["i"]))
    acc_a = e1 and e2 and e3 and e4 and e5 and e6 and D_COMP["a"] == "DRAWN"
    w("   BOARD A'S HALF: %s on its case (C-DEV rev 1) on the printed figures, with the TYPICAL EN currents and Isat and the DECLARED figures labelled above" % ("HOLDS" if acc_a else "DOES NOT HOLD"))
    w("")
    w("   BOARD B'S HALF (the LDOs on +5V_IOC, the lead J_5V_IOC, the device lead's declaration)")
    b1 = not on_dev and not dev_alloc and V_COMP.get("b") == "DRAWN"
    w("   (B1) the move is drawn in the composed netlist: U40, U50 and U60 take their input, their EN pull-up and their input capacitor from +5V_IOC;")
    w("        LDOs still on +5V_DEV: %s; still allocated on the device lead: %s; so item (1)'s %.4f A is U7's case with this board composed: %s" % (
        ", ".join(on_dev) or "none", ", ".join(dev_alloc) or "none", C["b_i_least"], "HOLDS" if b1 else "FAILS"))
    b2 = D_COMP["b"] == "DRAWN" and rb["+5V_DEV"]["amps_peak"] + 1e-9 >= basis["dev_lead"] and rb["+5V_IOC"]["amps_peak"] + 1e-9 >= ioc_bound
    w("   (B2) the declarations stand on their basis (section 5; L8R2-F35): the device lead %.4f A declared against its own %.6f A on the case; +5V_IOC" % (
        rb["+5V_DEV"]["amps_peak"], basis["dev_lead"]))
    w("        %.4f A against %.6f A: %s (round 2 declared 6.0 A and 1.38 A: O2 above)" % (rb["+5V_IOC"]["amps_peak"], ioc_bound, "HOLDS" if b2 else "FAILS"))
    r_sup = G["rhot"] + 2 * P["vh_r"][1]
    scale = (G["total"] - G["parts"][4] + ioc_bound) / G["total"]
    shift = max(r["mv"] for r in G["cdev"].values()) * 1e-3 * scale
    v_ldo = lo - RAIL_BUDGET * 5.0 - ioc_bound * r_sup - shift
    ldo_need = 3.3 * P["ap_vout_hi"] + P["ap_drop"]
    b3 = v_ldo > ldo_need
    w("   (B3) the LDOs' input at the least: U601's %.4f V, less the rail's whole %.0f %% copper budget on both boards (%.3f V, DECLARED), less the" % (
        lo, RAIL_BUDGET * 100, RAIL_BUDGET * 5.0))
    w("        lead's supply side at %.4f A (its conductor %.3f mOhm at %.2f C, MODEL, record l8r2 3c for this make of lead; two VH contacts at the" % (
        ioc_bound, G["rhot"] * 1e3, G["t_hot"]))
    w("        after-test %.0f mOhm, PRINTED): %.4f V, less the ground shift between the boards (record l8r2 3d at the case's total with six leads," % (
        P["vh_r"][1] * 1e3, ioc_bound * r_sup))
    w("        its largest row: %.4f V, MODEL on PRINTED maxima): %.4f V against the AP2112K-3.3's need %.3f V (VOUT +%.1f %% and dropout %.0f mV" % (
        shift, v_ldo, ldo_need, (P["ap_vout_hi"] - 1) * 100, P["ap_drop"] * 1000))
    w("        at 600 mA, PRINTED, %s): %+.4f V: %s; each LDO at HIGH %.2f A under its %.0f mA (PRINTED)" % (
        P["ap_rev"], v_ldo - ldo_need, "HOLDS" if b3 else "FAILS", P["rv_h7"] + P["rv_other"], P["ap_imax"] * 1000))
    w("        the input holds while the ground shift between the boards stays under %.3f V, so it does not depend on how the return is corrected" % (v_ldo - ldo_need + shift))
    b4 = ioc_bound < P["vh_a"] and iomax < P["vh_a"] and P["lead"][0] == P["vh_awg"]
    w("   (B4) the lead J_5V_IOC, named: %d AWG, %d mm, VH crimp both ends, the device lead's make (SESSION; ASSEMBLY.md section 4's device lead row" % P["lead"])
    w("        and IF-AB-POWER's harness row for the 5 V leads); its pin 1 carries +5V_IOC and nothing else: %.4f A at most on the case (MODEL), %.2f A" % (ioc_bound, iomax))
    w("        at U601's limit, against the VH's %.0f A with AWG %d on the standard header (PRINTED, JST VH catalogue p.1): %s" % (P["vh_a"], P["vh_awg"], "HOLDS" if b4 else "FAILS"))
    eq = [G["cdev"][k]["lead"] * scale for k in ("K0", "K1", "K2")]
    worst2 = max(r["largest"] for r in G["cdev"].values()) * scale
    ub_worst = max(r["largest"] for r in G["ub"].values())
    b5 = worst2 < P["vh_a"]
    w("   (B5) its pin 2 is NOT its own rail's return: boards A and B share one ground, and the whole A to B return divides by resistance over six VH")
    w("        contacts and seventeen ribbon conductors (record l8r2 round 7). Its division on the case, read from l8r2_gndret.out (%.3f A in all there," % G["cdev_total"])
    w("        scaled by %.4f for this round's %.4f A at J_5V_IOC, a linear network; MODEL at %.2f C, the leads of one make): equal contacts %.3f, %.3f" % (
        scale, ioc_bound, G["t_hot"], eq[0], eq[1]))
    w("        and %.3f A a lead (K0, K1, K2); the largest any one lead's pin 2 carries in its rows, %.3f A (K3, a BOUND: that lead's two contacts" % (eq[2], worst2))
    w("        at 0, every other at its initial maximum), against the VH's %.0f A (PRINTED): %s on the case (record l8r2's comparator at the inside" % (P["vh_a"], "within it" if b5 else "OVER"))
    w("        air, %.3f A on its 30 K ASSUMPTION, shown beside it: %s)" % (G["vh_hot"], "also within" if worst2 < G["vh_hot"] else "over that comparator"))
    w("        at the declared upper bound with this draft (%.2f A there, every lead at its own peak at once) the same row reads %.3f A: OVER, and a" % (G["ub_total"], ub_worst))
    rib_over = [k for k in sorted(G["ub"]) if G["ub"][k]["ribbon"] > 1.0]
    w("        ribbon conductor passes its 1 A in %s: that is record l8r2's finding L8R2-F31, OPEN, with or without this draft" % ", ".join(rib_over))
    acc_b = b1 and b2 and b3 and b4 and b5
    w("   BOARD B'S HALF: %s on its case (C-DEV rev 1) for the draft's own parts and path, on the printed figures with the labels above" % ("HOLDS" if acc_b else "DOES NOT HOLD"))
    w("")
    w("   WHAT THIS ACCEPTANCE DEPENDS ON, AND WHAT IT DOES NOT")
    w("   it depends on: the LM5176's printed VSNS and R43's declared tolerance; the TPS62933's printed rating and limits; the VH's printed %.0f A at AWG %d" % (P["vh_a"], P["vh_awg"]))
    w("     for the supply pin; the AP2112K's printed dropout; rv-pwr's HIGH loads (DECLARED where no maker prints a maximum); the lead as %d AWG at %d mm" % P["lead"])
    w("     (SESSION); record l8r2's model of the return's division for pin 2 and for the ground shift (MODEL, its assumptions its own)")
    w("   it does NOT depend on, and does not close: record l8r2's finding L8R2-F31 (the A to B return is branched in parallel with nothing that sets its")
    w("     division; JST's note forbids parallel branching above the rating). The draft adds a sixth VH contact to that return and no load to it")
    w("     (section 5: %+.3f A); on the case every row of l8r2's division keeps J_5V_IOC's pin 2 inside the VH's printed rating, and the LDOs' input holds" % GND_ADD)
    w("     for any ground shift under %.3f V. Whatever corrects L8R2-F31 (its selected direction is a dedicated ground return, not drafted) changes" % (v_ldo - ldo_need + shift))
    w("     pin 2's share and the ribbons'; it does not change items (1) to (8) or (B1) to (B4). L8R2-F31 stays OPEN beside this result and is not this record's")
    w("")
    # 7. L8R2-F35
    w("7. RECORD l8r2'S FINDING L8R2-F35, ANSWERED")
    w("   (a) 'J_5V_DEV's return falls by the same current' (round 2's line): WITHDRAWN for pin 2. It holds for pin 1 only: J_5V_DEV's pin 1 falls by")
    w("       %.4f A on the case and J_5V_IOC's pin 1 carries the supervisors' rail; pin 2 of each carries a share of the whole return (item B5)" % C["b_buck_a"])
    w("   (b) J_5V_IOC's lead: %d AWG, %d mm, VH crimp both ends (SESSION: the device lead's make, so the VH's printed rating applies and the return's" % P["lead"])
    w("       model has leads of one make; source of the make: v2/docs/ASSEMBLY.md section 4 and IF-AB-POWER's harness row); named in both drafts; its")
    w("       ASSEMBLY.md row and its contract row are their owners' (findings L9T5-F07 and L9T5-F08); record l8r2 assumed the same lead")
    w("   (c) the device lead's declaration: board B declared a typed 6.0 A peak, under the lead's own %.4f A on the case with the draft. Corrected from" % basis["dev_lead"])
    w("       its basis, not to a passing number: the peak is the case's own figure for the lead (Layer 9's budget at HIGH, every load at constant power")
    w("       at the least load voltage, the supervisors gone), rounded up to 0.1 mA, %.4f A, and check_l9t5_netlist.py's decl() refuses any other" % CHK.ceil4(basis["dev_lead"]))
    w("       figure; board A's rail follows by stream s99's own construction (the lead plus the wall port's limit): %.4f A, %+.4f A to U7's least" % (
        ra["+5V_DEV"]["amps_peak"], C["lim_min"] - ra["+5V_DEV"]["amps_peak"]))
    w("       loop limit; +5V_IOC's peak by the same method at its own least load voltage: %.4f A (it was 1.38 A, the LDOs' own current)" % rb["+5V_IOC"]["amps_peak"])
    w("       consequence for record l8r2 (reported, its files not edited): the return's derived upper bound reads %.4f A with this round's drafts" % GND[1])
    w("       (l8r2_gndret.out composes round 2's copy and prints %.2f A)" % G["ub_total"])
    w("   (d) fandec and gndret are in board B's order (section 3)")
    w("")
    # 8. state, findings
    w("8. THE STATE OF I-03 (L9P-F03, the case row C-DEV rev 1)")
    w("   credit criteria (common brief), per board:")
    w("   board A: (a) composes in L4-E9's order and the generator runs: YES; (b) the changed nets read with mutations that fail: YES (three FAIL);")
    w("            (c) the electrical acceptance on C-DEV rev 1: HOLDS" if acc_a else "            (c) DOES NOT HOLD")
    w("   board B: (a) composes in L4-E9's order with record l8r2's round 7 drafts and the generator runs: YES; (b) the changed nets read with")
    w("            mutations that fail: YES (two FAIL; the tree before T5b stops); (c) the electrical acceptance on C-DEV rev 1: %s for the draft's own" % ("HOLDS" if acc_b else "DOES NOT HOLD"))
    w("            parts and path; the shared return (L8R2-F31) is OPEN beside it and is record l8r2's")
    w("   I-03 STAYS OPEN: both halves are checked drafts by their author only; the independent recheck V3 has not read them; nothing is applied")
    w("   negative checks of this solution: one (round 1's board B text refused alone, a missed edit, corrected in round 2); round 3 corrects two")
    w("   declarations and one sentence on record l8r2's finding, which was not a check of the solution; the loop is not closed")
    w("   physical conditions (open): U601 as drawn is a copy of U41's network; its 5 V efficiency, thermal rise, start-up into the LDOs' input")
    w("   capacitance, the lead's resistance and the return's division are bench items; the netlist check is not electrical qualification")
    w("")
    w("   FINDINGS FOR OTHER AUTHORS")
    w("   L9T5-F01 CLOSED BY RECORD l8r2's ROUND 7 DRAFTS (T5b): board B's composed generator stopped on GND's declared 21.0 A peak; with fandec and")
    w("     gndret it runs (O3 keeps the old state as a regression)")
    w("   L9T5-F02 (d8dec31's mainpb owner, R-194; L4-E9's row 33): with this record's draft before mainpb, mainpb takes %s and %s, not %s and %s;" % (
        PICKS["with"] + PICKS["without"]))
    w("     no collision either way (both orders compose); row 33's text names %s and %s, which this tree already moves: R-194's fixed" % PICKS["row33"])
    w("     references would remove the dependency")
    w("   L9T5-F03 (board B's generator owner, cosmetic): U40, U50 and U60's value text still reads \"its own branch off the device rail\"; left")
    w("     unchanged because the z-stack tables key on value texts; the comment and the net are corrected by the draft")
    w("   L9T5-F04 (C-PROT rev 1's consumers): the gauge's uncalibrated error against the breaker's 0.32 A gap: L9T5-CASES.md section 0, unchanged")
    w("   L9T5-F05 (record l8r2's author): on this merged tree l8r2_gndret.out is regenerated (it reads the tree's budget, now Layer 9's rounds 4 and")
    w("     5): its page's section 3g still prints the earlier tree's figures; and its copy of this record's draft is round 2's (the upper bound")
    w("     %.2f A there, %.4f A with round 3's declarations); L8R2-F31's state is unchanged" % (G["ub_total"], GND[1]))
    w("   L9T5-F06 (Layer 5, the supervisors' firmware contract; board B's owner): the supervisors' HIGH is Table 30's TJ 85 C figure (%.0f mA); the same" % (P["rv_h7"] * 1000))
    w("     row prints %.0f mA at TJ 125 C, over each AP2112K's %.0f mA: what bounds the H743's junction temperature, clock and peripheral state is" % (P["h7"][4] * 1000, P["ap_imax"] * 1000))
    w("     not stated in a record read here; independent of this draft (U7's case no longer carries the supervisors)")
    w("   L9T5-F07 (Layer 7, ASSEMBLY.md section 4): a row for the new lead: A22 J_5V_IOC (VH) to B16 J_5V_IOC (VH), %d AWG, %d mm, VH crimp both ends" % P["lead"])
    w("   L9T5-F08 (Layer 5, IF-AB-POWER): the contract gains J_5V_IOC (+5V_IOC %.2f A typical, %.4f A peak on both ends) and the device rail's rows" % (rb["+5V_IOC"]["amps_typ"], rb["+5V_IOC"]["amps_peak"]))
    w("     restate (A: 3.74 A typical, %.4f A peak, 3.44 A apportioned to J_5V_DEV; B: 3.44 A typical, %.4f A peak arriving); with record l8r2's rows" % (
        ra["+5V_DEV"]["amps_peak"], rb["+5V_DEV"]["amps_peak"]))
    w("")
    pred = {}
    pred["each draft applies once on a scratch copy and refuses a second time and the tree's generator"] = len(STEP2) == 2 and all(STEP2)
    pred["both boards compose in L4-E9's order with this draft in its place, first and last, and their designators are disjoint"] = (
        all(ORDERS_OK["a"]) and all(ORDERS_OK["b"]) and all(DISJ.values()))
    pred["the committed netlists read NOT DRAWN; each draft alone and both compositions read DRAWN, the pair included"] = (
        kit0 == "NOT DRAWN" and kit_alone == "DRAWN" and kit_c == "DRAWN" and V_COMP.get("pair") == "DRAWN")
    pred["the declarations read DRAWN on their basis alone and composed, on both boards"] = all(v == "DRAWN" for v in list(D_ALONE.values()) + list(D_COMP.values()))
    pred["record l8r2's check of the return reads DRAWN on the composed board B"] = GND_CHK == 0
    pred["O1: board B's round 1 text refuses alone on the LDO input capacitor's bypass entry"] = rc_o1 != 0 and "bypass C400 -> U40.1" in line_o1
    pred["O2: round 2's texts FAIL the declaration check on both boards"] = O2 == {"a": "FAIL", "b": "FAIL"}
    pred["O3: board B without record l8r2's round 7 drafts stops on GND's declared peak"] = rc_o3 != 0 and "rail GND declares a 21.00 A peak" in line_o3
    pred["every mutation FAILS"] = all(k == "FAIL" for k in MUT) and len(MUT) == 5
    pred["the draft adds nothing to board B's GND declared loads, and board A's VBAT declared loads are unchanged in sum"] = abs(GND_ADD) < 1e-9 and abs(vb - vb0) < 1e-9
    pred["C-DEV rev 1: board A's half holds on the printed figures"] = acc_a
    pred["C-DEV rev 1: board B's half holds for the draft's own parts and path; L8R2-F31 is read OPEN in record l8r2's output"] = acc_b
    w("9. THE PREDICATES")
    for k, v in pred.items():
        w("   %-126s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l9t5_drafts: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 4


if __name__ == "__main__":
    sys.exit(main())
