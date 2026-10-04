#!/usr/bin/env python3
"""l9t5_drafts.py: Layer 9 record l9t5, task T5 round 2: I-03's correction (the case row C-DEV rev 1) drafted for boards A and B,
composed, regenerated, mutated and judged on scratch copies (MESHSAT-1357, 4 October 2026). PROTOTYPE DESIGN: nothing in this kit
has been built, bought, powered or measured, nothing is applied to the tree, and no figure printed here is a measurement.

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the generators and the engine, every draft the compositions apply, the committed netlists,
     the makers' sheets read, record l9t5's case script and output, this record's own files);
  2. each of this record's drafts on a scratch copy: checked, applied once, refused a second time, and refused on the tree's own
     generator (NOT RELEASED); board B's round 1 text (fnd/l9t5 at bdbed9bb, kept in inputs/) beside it;
  3. the composition of each board in L4-E9's change-list order (records/l4e9/L4-POWER-ARCHITECTURE.md section 3, set 29's tree)
     with this record's draft in its place, first and last; the designators each draft adds, pairwise disjoint; d8dec31's mainpb
     (which takes "the next free R and C at apply time") with this record's draft before it and after it;
  4. the regeneration on the runner (record l8p's gen_netlist.py: the generator's own part table, no KiCad): the unpatched
     generators against the committed netlists; board A alone and composed; board B's round 1 text alone (the old defect); board
     B alone, composed (BLOCKED: another record's defect, task T5b's) and composed without that draft (diagnostic, no credit);
     check_l9t5_netlist.py on each, and on five mutated netlists, each of which must FAIL;
  5. the declarations the patched generators write (the intent) for the new and the changed rails, and the ground's sources and loads;
  6. the electrical acceptance on C-DEV rev 1 on the makers' printed figures, each figure labelled PRINTED (a maker's limit),
     TYPICAL, DECLARED (a generator's or a record's declaration), MODEL or ASSUMPTION; board A's half judged now, board B's half
     UNCHECKED until T5b lands; the upstream path on C-ALLTX rev 3; what T5b needs (the return current through J_5V_IOC);
  7. the state of I-03, the findings for other authors, and the predicates test_l9t5.py holds.
Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_drafts.py  (l9t5_drafts.out is its output, regenerated with
_bin/regen_out.py after l9t5_case.out). Stdlib, PyYAML and pdftotext; about ten seconds."""
import ast
import hashlib
import importlib.util
import io
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
OLD_B = os.path.join(HERE, "inputs", "apply_gen_sch_b_iocbuck-bdbed9bb.py")
CASE_PY = os.path.join(HERE, "l9t5_case.py")
CASE_OUT = os.path.join(HERE, "l9t5_case.out")
# L4-E9's change list for each board's round, in application order (L4-POWER-ARCHITECTURE.md section 3 at set 29's line): board A
# 3a r12, guard, charger; 3b r11; 3c bank; 3d r138; 3e u17; 3g gnd002, hotr1, record l8r2's board A drafts (its d8v3 and vbus20ov in
# its own order, as records l8r2 and l8p compose them, then packrtn, slotlm after the charger, fb01), record l8p's ptc, L4-E11's dd7
# after the ptc; 3h d8dec31's mainpb LAST; then Layer 6's order-free table. Board B: gnd002, record l8r2's fans12, panel5v, ph4 and
# rt500 (any order), then Layer 6's land, table and declarations. This record's draft goes after a board's circuit drafts and
# before the last-taker and the tables (board A: after 3g, before 3h; board B: before Layer 6's).
ORDER = {
    "a": [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
          ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("l8r2", "packrtn"), ("l8r2", "slotlm"),
          ("l8r2", "fb01"), ("l8p", "ptc"), ("l4e11", "dd7"), ("d8dec31", "mainpb"), ("l6r2", "lcsc")],
    "b": [("l8gnd", "gnd002"), ("l8r2", "fans12"), ("l8r2", "panel5v"), ("l8r2", "ph4"), ("l8r2", "rt500"), ("l6r2", "xal_land"),
          ("l6r2", "lcsc"), ("l6r2", "intent")],
}
SLOT = {"a": 16, "b": 5}
T5B = ("l8r2", "fans12")       # the draft after which board B's composed generator stops on GND's declared peak (T5b's to reconcile)
SHEETS = {"tps62933": "v2/vendor/ti/ti-tps62933.pdf", "vh": "v2/vendor/connectors/jst-vh-catalogue.pdf",
          "xal60": "v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf", "ap2112": "v2/vendor/diodes/diodes-ap2112-ldo.pdf",
          "lm5176": "v2/vendor/ti/lm5176-datasheet.pdf"}
OWN = ["v2/docs/records/l9t5/" + f for f in ("check_l9t5_netlist.py", "apply_gen_sch_a_iocbuck.py", "apply_gen_sch_b_iocbuck.py",
                                              "inputs/apply_gen_sch_b_iocbuck-bdbed9bb.py", "inputs/SOURCES.txt",
                                              "inputs/coordinator-cases-2026-10-04-rev3.md", "l9t5_case.py", "l9t5_case.out")]
ENGINE = ["v2/ecad/tools/kisch.py", "v2/ecad/tools/intent.py", "v2/ecad/tools/idc_pads.py", "v2/docs/records/l8p/gen_netlist.py",
          "v2/docs/records/l8p/check_l8p_netlist.py"]
# the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
DIV_TOL, DIV_TCR, DIV_DT = 0.001, 25e-6, 65.0    # the divider's parts (stream s99a's pair, as U41) and its temperature span: as U41's record
ETA_DECL = 0.90                                  # U601's declared efficiency (the draft's intent, as U41's): NOT PLOTTED at 5 V out
ETA_SENS = 0.85                                  # a lower bound shown for it (the floor record l9t5 uses for unplotted points)
EXTRA_EN = 1                                     # the TPS62933 EN pins U601 adds to RAIL_EN


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
    P["vh_a"] = float(need(pdf("vh"), r"Current rating: (\d+) A", "the VH's rating").group(1))
    m = need(pdf("xal60"), r"XAL6060-682ME_\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "XAL6060-682's row")
    P["l_isat"] = float(m.group(5))
    t = pdf("ap2112")
    P["ap_rev"] = need(t, r"Document number: (DS39724 Rev\. 2 - 2)", "the AP2112 sheet's number").group(1)
    sec = need(t, r"AP2112-3\.3 Electrical Characteristics.*?ISHORT", "the AP2112-3.3 table", re.S).group(0)
    P["ap_vout_hi"] = float(need(sec, r"VOUT\s+VOUT\s*\n.*?\n.*?\*([\d.]+)%\s+\*([\d.]+)%", "VOUT's band", re.S).group(2)) / 100.0
    P["ap_imax"] = float(need(sec, r"IOUT\(MAX\)\s+Maximum Output Current\s+VIN = 4\.3V, VOUT = [\d.]+V to [\d.]+V\s+(\d+)", "IOUT(MAX)").group(1)) / 1000.0
    P["ap_drop"] = float(need(sec, r"IOUT = 600mA\s+\u2014\s+250\s+(\d+)", "the dropout at 600 mA").group(1)) / 1000.0
    P["ap_vin_max"] = float(need(t, r"VIN\s+Supply Voltage\s+([\d.]+)\s+([\d.]+)\s+V", "VIN's range").group(2))
    return P


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


def seq_of(board, mine_at=None, skip=()):
    seq = [draft(r, n, board) for r, n in ORDER[board] if (r, n) not in skip]
    if mine_at is None:
        return seq
    at = SLOT[board] if mine_at == "slot" else (0 if mine_at == "first" else len(seq))
    if skip and mine_at == "slot":
        at -= sum(1 for x in ORDER[board][:SLOT[board]] if x in skip)
    return seq[:at] + [MINE[board]] + seq[at:]


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


def drawn(text):
    """{designator: count} of the literal part calls (a call's first argument a constant designator), read with ast."""
    from collections import Counter
    c = Counter()
    for n in ast.walk(ast.parse(text)):
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
    r = intent["rails"].get(net) or {}
    return math.fsum((r.get("loads") or {}).values())


# ------------------------------------------------------------------------------------------------ the record
def main():
    out = []
    w = out.append
    P = figures()
    cm = case_module()
    R = cm.compute()
    C, case = R["C"], R["case"]
    w("l9t5_drafts: Layer 9 record l9t5, task T5 round 2: I-03 (C-DEV rev 1) drafted for boards A and B, composed, regenerated, mutated and judged (MESHSAT-1357)")
    w("prototype design; nothing built, bought, powered or measured; nothing applied to the tree; every statement is about generator text, netlists and the makers' sheets")
    w("")
    # 1. inputs
    w("1. INPUTS, pinned by sha256")
    others = sorted({draft(r, n, b) for b in "ab" for r, n in ORDER[b]})
    inputs = [GEN["a"], GEN["b"]] + [os.path.join(ROOT, p) for p in ENGINE] + others + [NET["a"], NET["b"]]
    inputs += [os.path.join(ROOT, p) for p in SHEETS.values()] + [os.path.join(ROOT, p) for p in OWN]
    inputs += [os.path.join(RECS, "l4e9", "L4-POWER-ARCHITECTURE.md")]
    for p in inputs:
        if not os.path.isfile(p):
            refuse("input %s is missing" % rel(p))
        w("   %s %s" % (sha(p), rel(p)))
    src = open(os.path.join(HERE, "inputs", "SOURCES.txt"), encoding="utf-8").read()
    for f in ("apply_gen_sch_b_iocbuck-bdbed9bb.py", "coordinator-cases-2026-10-04-rev3.md"):
        if ("%s sha256 %s" % (f, sha(os.path.join(HERE, "inputs", f), 64))) not in src:
            refuse("SOURCES.txt does not name inputs/%s at its sha256" % f)
    w("   the two copies filed this round equal the sha256 SOURCES.txt names: yes")
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
        t = os.path.join(d, "old_gen_sch_b.py")
        shutil.copy(GEN["b"], t)
        r = subprocess.run([sys.executable, "-B", OLD_B, t, "--write"], capture_output=True)
        n_old = re.search(rb"WRITTEN, (\d+) edit", r.stdout)
        w("   board B's round 1 text (inputs/apply_gen_sch_b_iocbuck-bdbed9bb.py): applied %s (%s edits); its text lacks the edit to the LDO input" % (
            "OK" if r.returncode == 0 else "FAILED", n_old.group(1).decode() if n_old else "?"))
        w("     capacitor's explicit bypass entry (_intent.bypass(C_(0), U_(0), \"1\", \"+5V_DEV\")); section 4 regenerates it")
        if any(sha(GEN[b], 64) != tree_before[b] for b in "ab"):
            refuse("a draft wrote into the tree")
        w("   the tree's generators are unchanged: yes")
        w("")
        # 3. composition
        w("3. COMPOSITION IN L4-E9'S CHANGE-LIST ORDER (records/l4e9/L4-POWER-ARCHITECTURE.md section 3; this record's draft after the board's")
        w("   circuit drafts, before the last-taker and the tables)")
        comp = {}
        for b in "ab":
            p, res, ok = compose(b, seq_of(b, "slot"), d, "fwd")
            comp[b] = (p, ok)
            w("   board %s, this record's draft in its place:" % b.upper())
            for s, v, _m in res:
                w("     %-46s %s" % (s, v))
            for tag, at in (("first", "first"), ("last", "last")):
                _p, res2, ok2 = compose(b, seq_of(b, at), d, tag)
                w("   board %s, this record's draft %s: %s" % (b.upper(), "first, then the order" if at == "first" else "after the whole order",
                                                            "every step OK" if ok2 else "; ".join("%s %s" % (s, v) for s, v, _m in res2 if v != "OK")))
        # mainpb's picks
        _p, res_slot, _ok = compose("a", seq_of("a", "slot"), d, "mp1")
        _p, res_base, _ok = compose("a", seq_of("a"), d, "mp0")
        picks = {k: mainpb_takes(dict((s, m) for s, _v, m in rs).get("d8dec31/apply_gen_sch_a_mainpb.py", "")) for k, rs in (("with", res_slot), ("without", res_base))}
        _p, res_last, _ok = compose("a", seq_of("a", "last"), d, "mp2")
        picks["after"] = mainpb_takes(dict((s, m) for s, _v, m in res_last).get("d8dec31/apply_gen_sch_a_mainpb.py", ""))
        row33 = need(open(os.path.join(RECS, "l4e9", "L4-POWER-ARCHITECTURE.md"), encoding="utf-8").read(),
                     r"LAST in board A's round, after 3a to 3g, where it takes (R\d+) and (C\d+)", "L4-E9's row 33").groups()
        PICKS.update(picks, row33=row33)
        w("   d8dec31's mainpb (the next free R and C at apply time): without this record's draft it takes %s and %s on set 29's tree (L4-E9's row 33" % picks["without"])
        w("     names %s and %s: stale already, the later drafts took those);" % row33)
        w("     with this record's draft before it, %s and %s; with this record's draft after it, %s and %s (finding L9T5-F02)" % (picks["with"] + picks["after"]))
        w("")
        w("   THE DESIGNATORS EACH DRAFT ADDS (the forward order; part calls read with ast, and each draft's declared ADDS)")
        for b in "ab":
            adds, final = adds_per_draft(b, seq_of(b, "slot"), d)
            mine = adds.get(os.path.relpath(MINE[b], RECS), set())
            meets = {k: sorted(v & mine) for k, v in adds.items() if k != os.path.relpath(MINE[b], RECS) and v & mine}
            dup = sorted(r for r, n in drawn(final).items() if n > 1)
            w("   board %s, this record's: %s" % (b.upper(), ", ".join(sorted(mine, key=lambda x: (re.sub(r"\d", "", x), int(re.sub(r"\D", "", x) or 0))))))
            w("   board %s, against every other draft's: %s; literal part calls drawn twice in the composed generator: %s" % (
                b.upper(), "DISJOINT" if not meets else "MEETS %s" % meets, ", ".join(dup) if dup else "none"))
        w("")
        # 4. regeneration
        w("4. REGENERATION ON THE RUNNER (record l8p's gen_netlist.py: the generator's own part table, no KiCad) AND THE NETLIST CHECK")
        base = {}
        for b in "ab":
            rc, path, table = netlist(b, GEN[b], d, "base")
            if rc:
                refuse("board %s's own generator did not run: %s" % (b, path))
            base[b] = (path, table)
            a_, k_ = CHK.read(open(path, "rb").read()), CHK.read(open(NET[b], "rb").read())
            pa, pk = pins_of(a_), pins_of(k_)
            diff = [x for x in sorted(set(pa) | set(pk)) if pa.get(x) != pk.get(x)]
            nc = [x for x in diff if pa.get(x) is None and str(pk.get(x)).startswith("unconnected-")]
            w("   board %s unpatched: %d connected pins against the committed KiCad netlist's %d; differences %d, all KiCad's names for open pins: %s" % (
                b.upper(), len(pa), len(pk), len(diff), "yes" if len(nc) == len(diff) else "NO"))
        kit, _v, txt = check({b: NET[b] for b in "ab"}, lambda x: "committed board %s (KiCad's export)" % x.upper())
        w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        alone = {}
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
        t = os.path.join(d, "old_gen_sch_b.py")
        rc_old, line_old, _t = netlist("b", t, d, "old")
        R_OLD = (rc_old, line_old)
        w("   board B with round 1's text alone (the old defect): %s" % ("the generator ran (NOT EXPECTED)" if rc_old == 0 else "the generator refused: %s" % line_old))
        kit_alone, V_ALONE, txt = check({b: alone[b][0] for b in "ab"}, lambda x: "board %s, this record's draft alone" % x.upper())
        w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        w("   board A composed in L4-E9's order:")
        rc, path_ac, table_ac = netlist("a", comp["a"][0], d, "composed")
        if rc or not comp["a"][1]:
            refuse("board A's composition did not regenerate: %s" % path_ac)
        w("     the generator ran to its end (%d parts, %d unplaced, intent written: %s)" % (len(table_ac["parts"]), len(table_ac["unplaced"]), "yes" if table_ac["intent_written"] else "NO"))
        kit_a, _v, txt = check({"a": path_ac}, lambda x: "board A composed in L4-E9's order")
        w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        w("   board B composed in L4-E9's order:")
        rc_bc, line_bc, _t = netlist("b", comp["b"][0], d, "composed")
        q, _r, _ok = compose("b", seq_of("b"), d, "without")
        rc_bw, line_bw, _t = netlist("b", q, d, "without")
        R_BC = (rc_bc, line_bc, rc_bw, line_bw)
        w("     the generator %s" % ("ran (NOT EXPECTED while T5b is open)" if rc_bc == 0 else "refused: %s" % line_bc))
        w("     without this record's draft the same composition's generator %s" % (
            "refuses with the same line: the stop is not this record's" if rc_bw and line_bw == line_bc else "runs" if rc_bw == 0 else "refuses otherwise: %s" % line_bw))
        _q, res_t5b, _ok = compose("b", seq_of("b", None, skip=(T5B,)), d, "upto")
        w("     BLOCKED BY T5b: record l8r2's %s draft adds the coolers' step-ups to board B's return; GND's declared 21.0 A peak (gen_sch_b.py,"
          % T5B[1])
        w("       _intent.rail(\"GND\", ...)) is not this record's to raise (task T5b reconciles it on its own branch): board B's I-03 draft stays UNCHECKED")
        q2, res_nf, ok_nf = compose("b", seq_of("b", "slot", skip=(T5B,)), d, "nofans")
        rc, path_bn, table_bn = netlist("b", q2, d, "nofans")
        w("   board B composed without record l8r2's %s draft (DIAGNOSTIC ONLY, no credit: the composition criterion is not met):" % T5B[1])
        w("     every other draft %s; the generator %s" % ("OK" if ok_nf else "REFUSED", "ran to its end (%d parts, intent written: %s)" % (
            len(table_bn["parts"]), "yes" if table_bn["intent_written"] else "NO") if rc == 0 else "refused: %s" % path_bn))
        if rc:
            refuse("board B's diagnostic composition did not regenerate")
        kit_bn, _v, txt = check({"a": path_ac, "b": path_bn}, lambda x: "board %s, %s" % (x.upper(), "composed in L4-E9's order" if x == "a" else "composed without l8r2's fans12 (diagnostic)"))
        w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        w("   THE MUTATIONS (each must FAIL)")
        muts = [("a", path_ac, "J_5V_IOC's pins 1 and 2 exchanged on board A (the lead reversed)", [(("J_5V_IOC", "1"), ("J_5V_IOC", "2"))]),
                ("a", path_ac, "U601's EN and SS exchanged (the buck no longer on RAIL_EN)", [(("U601", "2"), ("U601", "7"))]),
                ("a", path_ac, "R601's +5V_IOC end and R602's ground end exchanged (the divider inverted: 0.95 V out)", [(("R601", "1"), ("R602", "2"))]),
                ("b", alone["b"][0], "U50's VIN and D1's cathode exchanged (controller B's LDO back on +5V_DEV)", [(("U50", "1"), ("D1", "1"))]),
                ("b", alone["b"][0], "J_5V_IOC's pins 1 and 2 exchanged on board B (the lead reversed)", [(("J_5V_IOC", "1"), ("J_5V_IOC", "2"))])]
        MUT = []
        for i, (b, src_, what, sw) in enumerate(muts, 1):
            mp = mutate(src_, d, "mut%d_%s" % (i, b), sw)
            kitm, _v, txt = check({b: mp}, lambda x, what=what: "mutation %d, board %s: %s" % (i, x.upper(), what))
            MUT.append(kitm)
            w("".join("     " + l + "\n" for l in txt.splitlines()).rstrip("\n"))
        w("")
        # 5. the intent
        w("5. THE DECLARATIONS THE PATCHED GENERATORS WRITE (their intent)")
        ia, ia0 = table_ac["intent"], None
        q0, _r, _ok = compose("a", seq_of("a"), d, "a_without")
        rc, _p0, t0 = netlist("a", q0, d, "a_without")
        ia0 = t0["intent"] if rc == 0 else refuse("board A's composition without this record's draft did not regenerate")
        r_ = ia["rails"]["+5V_IOC"]
        w("   board A, rail +5V_IOC: %.1f V, %.2f A typical, %.2f A peak, source %s, switch %s, fed from %s, efficiency %s, v_work %s, loads %s" % (
            r_["volts"], r_["amps_typ"], r_["amps_peak"], r_["source"], r_.get("switch"), r_.get("fed_from"), r_.get("efficiency"), r_.get("v_work"),
            ", ".join("%s %.2f" % kv for kv in sorted(r_["loads"].items()))))
        dv, dv0 = ia["rails"]["+5V_DEV"], ia0["rails"]["+5V_DEV"]
        w("   board A, rail +5V_DEV: typical %.2f A (%.2f without this draft), peak %.4f A (%.4f), loads %s" % (
            dv["amps_typ"], dv0["amps_typ"], dv["amps_peak"], dv0["amps_peak"], ", ".join("%s %.2f" % kv for kv in sorted(dv["loads"].items()))))
        vb, vb0 = loads_sum(ia, "VBAT"), loads_sum(ia0, "VBAT")
        w("   board A, rail VBAT: its declared loads sum to %.2f A (%.2f without this draft): Q32 %.2f (%.2f), U601 %.2f; peak %.1f A" % (
            vb, vb0, ia["rails"]["VBAT"]["loads"]["Q32"], ia0["rails"]["VBAT"]["loads"]["Q32"], ia["rails"]["VBAT"]["loads"]["U601"], ia["rails"]["VBAT"]["amps_peak"]))
        for n in ("IOCB_SW", "IOCB_BST"):
            x = ia["nodes"].get(n) or {}
            w("   board A, node %-8s v_max %s V%s" % (n, x.get("v_max"), ", rides on %s by %s V" % (x["rides_on"], x["bias_v"]) if x.get("rides_on") else ""))
        ib = table_bn["intent"]
        _q, _r, _ok = compose("b", seq_of("b", None, skip=(T5B,)), d, "b_without")
        rc, _p1, t1 = netlist("b", _q, d, "b_without")
        ib0 = t1["intent"] if rc == 0 else refuse("board B's diagnostic composition without this record's draft did not regenerate")
        r_ = ib["rails"]["+5V_IOC"]
        w("   board B (diagnostic composition), rail +5V_IOC: %.2f A typical, %.2f A peak, source %s, always on: %s, loads %s" % (
            r_["amps_typ"], r_["amps_peak"], r_["source"], "yes" if r_.get("always_on") else "NO", ", ".join("%s %.2f" % kv for kv in sorted(r_["loads"].items()))))
        w("   board B, the three +3V3_IOCx rails fed from: %s" % ", ".join("%s %s" % (n, ib["rails"][n].get("fed_from")) for n in ("+3V3_IOCA", "+3V3_IOCB", "+3V3_IOCC")))
        dv, dv0 = ib["rails"]["+5V_DEV"], ib0["rails"]["+5V_DEV"]
        w("   board B, rail +5V_DEV: typical %.2f A (%.2f without), its loads sum %.2f A (%.2f), peak %.1f A (%.1f)" % (
            dv["amps_typ"], dv0["amps_typ"], loads_sum(ib, "+5V_DEV"), loads_sum(ib0, "+5V_DEV"), dv["amps_peak"], dv0["amps_peak"]))
        g, g0 = ib["rails"]["GND"], ib0["rails"]["GND"]
        GND_ADD = loads_sum(ib, "GND") - loads_sum(ib0, "GND")
        w("   board B, rail GND: sources %s (without: %s); its loads sum %.2f A (%.2f without, %+.2f A); declared peak %.1f A" % (
            ", ".join(g["source"]), ", ".join(g0["source"]), loads_sum(ib, "GND"), loads_sum(ib0, "GND"), GND_ADD, g["amps_peak"]))
        bp = [x for x in ib.get("bypass", []) if x.get("cap") in ("C400", "C420", "C440")]
        w("   board B, the LDO input capacitors' bypass entries: %s" % "; ".join("%s at %s.%s on %s" % (x.get("cap"), x.get("part"), x.get("pin"), x.get("net")) for x in bp))
        w("")
    if any(sha(GEN[b], 64) != tree_before[b] for b in "ab"):
        refuse("the tree's generators changed during the run")

    # 6. electrical acceptance
    w("6. THE ELECTRICAL ACCEPTANCE ON C-DEV REV 1 (record l9t5 out 5 for the case figures; the makers' sheets read here)")
    w("   labels: PRINTED a maker's limit; TYPICAL a maker's typical figure; DECLARED a generator's or a record's declaration; MODEL this record's arithmetic")
    e1 = C["b_margin"] > 0
    w("   (1) U7, the device rail, on the case: %.4f A (MODEL: every load at constant power at %.4f V, the loads at rv-pwr's HIGH) against its" % (C["b_i_least"], C["v_least"]))
    w("       average loop's least %.4f A (PRINTED VSNS %.0f mV, LM5176 SNVSAI1D; R43 %.0f mOhm at +%.0f %%, DECLARED): margin %+.4f A: %s" % (
        C["lim_min"], C["vsns"][0] * 1000, C["rs"] * 1000, C["tol"] * 100, C["b_margin"], "HOLDS" if e1 else "FAILS"))
    w("       (before: %.4f A, %+.4f A); the loop's highest %.4f A stays under J_5V_DEV's VH %.0f A (PRINTED): U7, R43 and its lead unchanged" % (
        C["i_least"], C["lim_min"] - C["i_least"], C["lim_max"], P["vh_a"]))
    e2 = C["b_buck_a"] < P["tps_a"]
    w("   (2) U601 on the case: %.4f A (MODEL, constant power; %.4f A as the LDOs' own current = 3 x (0.400 + 0.060), each H743 at rv-pwr's HIGH" % (C["b_buck_a"], C["ioc_i_ldo"]))
    w("       400 mA, which rv-pwr cites as DS12110 Rev 10's maximum, not re-read here, plus 60 mA DECLARED) against its %.0f A rating (PRINTED, %s): %s" % (
        P["tps_a"], P["tps_rev"], "HOLDS" if e2 else "FAILS"))
    iomax = (P["ihs"][2] + P["ils"][2]) / 2.0
    e3 = P["ihs"][2] < P["vh_a"] and iomax < P["vh_a"]
    w("   (3) U601's limit against J_5V_IOC's VH %.0f A (PRINTED): high-side limit %.1f / %.1f / %.1f A, low-side %.1f / %.1f / %.1f A (PRINTED);" % (
        P["vh_a"], *P["ihs"], *P["ils"]))
    w("       the output at most about (%.1f + %.1f) / 2 = %.2f A (Equation 11, approximate, on PRINTED maxima), hiccup on a sustained short (9.3.12): %s" % (
        P["ihs"][2], P["ils"][2], iomax, "HOLDS" if e3 else "FAILS"))
    e4 = P["l_isat"] > P["ihs"][2]
    w("   (4) L601 XAL6060-682ME: Isat %.1f A (PRINTED, Coilcraft) over the part's %.1f A highest high-side limit: %s" % (P["l_isat"], P["ihs"][2], "HOLDS" if e4 else "FAILS"))
    lo, nom, hi = CHK.vout_band(56.2e3, 10.7e3, DIV_TOL, DIV_TCR, DIV_DT, P["ifb"])
    if abs(P["vfb"][0] - CHK.VFB[0]) > 1e-9 or abs(P["vfb"][2] - CHK.VFB[2]) > 1e-9:
        refuse("the checker's VFB is not the sheet's")
    ldo_need = 3.3 * P["ap_vout_hi"] + P["ap_drop"]
    budget = 0.02 + 0.015
    at_ldo = lo * (1 - budget)
    e5 = at_ldo > ldo_need and hi < P["ap_vin_max"]
    w("   (5) +5V_IOC's set point: 56.2k over 10.7k at 0.1 %% and %.0f ppm/K over %.0f K (DECLARED, stream s99a's pair, as U41), VFB %.3f to %.3f V over TJ" % (
        DIV_TCR * 1e6, DIV_DT, P["vfb"][0], P["vfb"][2]))
    w("       -40 to 150 C and IFB %.2f uA (PRINTED): %.3f V nominal, %.3f to %.3f V; at the LDOs after board A's 2 %% and board B's 1.5 %% drop budgets" % (
        P["ifb"] * 1e6, nom, lo, hi))
    w("       (DECLARED) at least %.3f V against the AP2112K-3.3's need %.3f V (VOUT +%.1f %% and dropout %.0f mV at 600 mA, PRINTED, %s), and at most" % (
        at_ldo, ldo_need, (P["ap_vout_hi"] - 1) * 100, P["ap_drop"] * 1000, P["ap_rev"]))
    w("       %.3f V against its %.1f V input maximum (PRINTED): %s; each LDO at HIGH 0.46 A under its %.0f mA (PRINTED)" % (
        hi, P["ap_vin_max"], "HOLDS" if e5 else "FAILS", P["ap_imax"] * 1000))
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
    acc_a = e1 and e2 and e3 and e4 and e5 and e6
    w("   BOARD A'S HALF: %s on its case (C-DEV rev 1) on the printed figures, with the TYPICAL EN currents and the DECLARED budgets labelled above" % ("HOLDS" if acc_a else "DOES NOT HOLD"))
    w("   BOARD B'S HALF: UNCHECKED. Its draft is read in the netlist alone and in the diagnostic composition (section 4: DRAWN, two mutations FAIL),")
    w("     but its composition in L4-E9's order stops on T5b's line; the electrical figures above are board B's too (the LDOs' input, the lead)")
    w("   WHAT T5b NEEDS (the return current this draft adds to board B's ground):")
    w("     the lead J_5V_IOC: pin 1 +5V_IOC, pin 2 GND (board B's return to board A); the three LDOs' current returns through pin 2 instead of J_5V_DEV's")
    w("     typical: %.2f A (DECLARED: the three 0.12 A allocations, unchanged); at C-DEV: %.4f A (MODEL, constant power at %.4f V) or %.4f A" % (
        0.36, C["b_buck_a"], C["v_least"], C["ioc_i_ldo"]))
    w("     (the LDOs' own current at rv-pwr's HIGH); at C-ALLTX rev 3: %.4f A (the case's typical, %.4f W at 5.1 V)" % (ioc_in / 5.1, ioc_in))
    w("     GND's declared loads change by %+.2f A (section 5: the three allocations leave +5V_DEV's derived ground loads and return as _IOC_LOADS);" % GND_ADD)
    w("     J_5V_DEV's return falls by the same current; GND gains J_5V_IOC as a fifth source; the draft does not touch the 21.0 A declaration")
    w("")
    # 7. state, findings, predicates
    w("7. THE STATE OF I-03 (L9P-F03, the case row C-DEV rev 1)")
    w("   credit criteria (common brief): (a) composition and generator run: board A YES, board B BLOCKED by T5b; (b) the changed nets read with")
    w("   mutations that fail: board A YES (three FAIL), board B YES alone and in the diagnostic composition (two FAIL), not in the full composition;")
    w("   (c) the electrical acceptance on C-DEV rev 1: board A's half HOLDS, board B's half UNCHECKED. I-03 stays OPEN: board A's half is a checked")
    w("   draft, board B's is UNCHECKED until T5b's branch lands; then this script's section 4 runs the full composition again (no other change)")
    w("   negative checks of this solution: one (board B's round 1 text refused alone: a missed edit, corrected in round 2); the loop is not closed")
    w("   physical conditions (open): U601 as drawn is a copy of U41's network; its 5 V efficiency, thermal rise, start-up into the LDOs' input")
    w("   capacitance and the lead's resistance are bench items; the netlist check is not electrical qualification")
    w("")
    w("   FINDINGS FOR OTHER AUTHORS")
    w("   L9T5-F01 (T5b, record l8r2's line): board B's composed generator stops on GND's declared 21.0 A peak after l8r2's fans12; this record's")
    w("     draft adds 0.00 A to GND's declared loads and a fifth source (above); the same stop without this record's draft")
    w("   L9T5-F02 (d8dec31's mainpb owner, R-194; L4-E9's row 33): with this record's draft before mainpb, mainpb takes %s and %s, not %s and %s;" % (
        PICKS["with"] + PICKS["without"]))
    w("     no collision either way (both orders compose); row 33's text names %s and %s, which set 29's tree already moves: R-194's fixed" % PICKS["row33"])
    w("     references would remove the dependency")
    w("   L9T5-F03 (board B's generator owner, cosmetic): U40, U50 and U60's value text still reads \"its own branch off the device rail\"; left")
    w("     unchanged because the z-stack tables key on value texts; the comment and the net are corrected by the draft")
    w("")
    pred = {}
    pred["each draft applies once on a scratch copy and refuses a second time and the tree's generator"] = len(STEP2) == 2 and all(STEP2)
    pred["board A composes in L4-E9's order with this draft in its place, first and last, and its generator runs to its end"] = comp["a"][1] and kit_a == "DRAWN"
    pred["board B's round 1 text refuses alone on the LDO input capacitor's bypass entry (the old defect)"] = R_OLD[0] != 0 and "bypass C400 -> U40.1" in R_OLD[1]
    pred["board B with round 2's draft alone runs and reads DRAWN"] = V_ALONE.get("b") == "DRAWN"
    pred["board B's full composition stops on GND's declared peak with and without this draft (T5b's)"] = (
        R_BC[0] != 0 and "rail GND declares a 21.00 A peak" in R_BC[1] and R_BC[2] != 0 and R_BC[3] == R_BC[1])
    pred["board B's diagnostic composition reads DRAWN with board A's composition (the pair)"] = kit_bn == "DRAWN"
    pred["every mutation FAILS"] = all(k == "FAIL" for k in MUT) and len(MUT) == 5
    pred["the draft adds nothing to board B's GND declared loads"] = abs(GND_ADD) < 1e-9
    pred["board A's VBAT declared loads are unchanged in sum"] = abs(vb - vb0) < 1e-9
    pred["C-DEV board A's half holds on the printed figures"] = acc_a
    w("8. THE PREDICATES")
    for k, v in pred.items():
        w("   %-118s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l9t5_drafts: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 4


if __name__ == "__main__":
    sys.exit(main())
