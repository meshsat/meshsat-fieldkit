#!/usr/bin/env python3
"""Record l9t5, the P0 round's parts 4b and 4c (Slot A, MESHSAT-1357, 5 October 2026): THE CONNECTED P0 CANDIDATE.

4c (P0-6): boards A, B and D composed with EVERY pending draft in L4-E9's change-list order (records/l4e9/L4-POWER-ARCHITECTURE.md
section 3, with this record's text draft apply_l4e9_changelist_p0.py applied in memory: rows R-220 to R-239 for the drafts V6's
V6-m11 found without a row), regenerated without KiCad (record
l8p's gen_netlist.py), every record netlist check read in its composed mode, and one mutation per check that must not read DRAWN.
4b: the connected re-trace on that candidate: the case rows' loads, every converter's input current, the feed and return conductors
against their printed ratings, the protection coordination, the thermal limits and the required service, every figure labelled and
every case row cited; no figure stacked from mutually exclusive states.

PROTOTYPE DESIGN, DESK ARITHMETIC: nothing is built, bought, powered or measured, nothing is applied to the tree's generators. A
netlist reading is not electrical qualification. Labels: PRINTED (a maker's printed limit), TYPICAL, DECLARED (an intent
declaration), MODEL (this tree's arithmetic on its stated inputs), ASSUMPTION, INFERRED (a reading between printed points), MISSING,
PROVISIONAL (amendment 1: a bounded choice with the supplier's validation task).

Run from the repository root: python3 v2/docs/records/l9t5/l9t5_connected.py (stdlib, PyYAML, pdftotext; about two minutes, one
process). The committed output is regenerated only through _bin/regen_out.py. Every generator is a copy in a temporary directory; the
tree's generators are checked unchanged at the end.
"""
import ast
import copy
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REC = os.path.join(ROOT, "v2", "docs", "records")
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.dont_write_bytecode = True
for _d in (HERE, os.path.join(REC, "l8p"), os.path.join(REC, "l8r2"), os.path.join(REC, "l8gnd"), os.path.join(REC, "l4e11")):
    sys.path.insert(0, _d)
import check_f01_netlist as F01  # noqa: E402
import check_l9t5_netlist as L9  # noqa: E402
import check_l8p_netlist as L8P  # noqa: E402
import check_l8r2_netlist as L8R2  # noqa: E402
import check_gndret_netlist as GR  # noqa: E402
import check_gnd002_netlist as GND  # noqa: E402
import check_dd7_netlist as DD7  # noqa: E402
import l9t5_paloop as PL  # noqa: E402

NET = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
       "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net"}
PRJ = {"a": "pcb-a-power", "b": "pcb-b-compute", "d": "pcb-d-aprs"}
# the P0 candidate's composition: L4-E9's change list (rows R-01 to R-239, section 3) board by board, then Layer 6's order-free tables
ORDER = {
    "a": ["l4e6/r12", "l4e11/guard", "l4e11/charger", "l4e4/r11", "l4e8/bank", "l4e4/r138", "l4e9/u17", "l8gnd/gnd002", "l8gnd/hotr1",
          "l8r2/d8v3", "l8r2/vbus20ov", "l8r2/packrtn", "l8r2/slotlm", "l8r2/fb01", "l8p/ptc", "l4e11/dd7", "l8p/thguard",
          "l9t5/iocbuck", "l9t5/iocpre", "l8r2/gndrtn", "efuse/u23ilm", "l9t5/paloop", "d8dec31/mainpb", "l6r2/lcsc"],
    "b": ["l8gnd/gnd002", "l8r2/fans12", "l8r2/fandec", "l8r2/panel5v", "l8r2/ph4", "l8r2/rt500", "l8r2/gndret", "l8r2/gndrtn",
          "l9t5/iocbuck", "l9t5/iocpre", "l9t5/canshdn", "efuse/u23ilm", "efuse/u24ilm", "l6r2/xal_land", "l6r2/lcsc", "l6r2/intent"],
    "d": ["d8dec31/ptt", "l9t5/paloop", "l6r2/intent", "l6r2/lcsc"],
}
ORDER_FREE = ("l6r2",)          # Layer 6's tables: order-free, after every circuit draft (no change-list row; L4-E9 section 3)
L4E9 = "v2/docs/records/l4e9/l4e9_power_path.py"
REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
CL_DRAFT = "v2/docs/records/l9t5/apply_l4e9_changelist_p0.py"   # this record's text draft for the integrator (V6-m11)
CASES = "v2/docs/records/l8r2/inputs/coordinator-cases-2026-10-05-cdev-rev2.md"
OUTS = {"budget": "v2/docs/records/l9pwr/l9pwr_budget.out", "drafts": "v2/docs/records/l9t5/l9t5_drafts.out",
        "efuse": "v2/docs/records/efuse/efuse_check.out", "stk": "v2/docs/records/l9stk/l9stk_protection.out",
        "c4": "v2/docs/records/l8p/l8p_c4.out", "t10": "v2/docs/records/l9t5/l9t5_t10.out", "f01": "v2/docs/records/l9t5/l9t5_f01.out",
        "p0ret": "v2/docs/records/l8r2/l8r2_p0.out"}
SCRIPTS = ["v2/docs/records/l9t5/l9t5_case.py", "v2/docs/records/l8r2/l8r2_p0.py", "v2/docs/records/l8r2/l8r2_gndret.py",
           "v2/docs/records/l9t5/l9t5_paloop.py", "v2/docs/records/efuse/efuse_check.py", "v2/docs/records/l8p/gen_netlist.py",
           "v2/docs/records/l9t5/check_f01_netlist.py", "v2/docs/records/l9t5/check_l9t5_netlist.py", "v2/docs/records/l8p/check_l8p_netlist.py",
           "v2/docs/records/l8r2/check_l8r2_netlist.py", "v2/docs/records/l8r2/check_gndret_netlist.py",
           "v2/docs/records/l8gnd/check_gnd002_netlist.py", "v2/docs/records/l4e11/check_dd7_netlist.py"]
GENS = ["v2/ecad/tools/gen_sch_%s.py" % b for b in "abd"]
SOLAR_P0 = "v2/docs/records/l4e7/l4e7_p0sol.out"   # P0-7, the third author's: composed here only once merged


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def text(p):
    return open(rel(p), encoding="utf-8").read()


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def refuse(msg):
    sys.stderr.write("l9t5_connected: %s; refusing\n" % msg)
    sys.exit(3)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s is not read (%s)" % (what, pat[:60]))
    return m


GN = load(os.path.join(REC, "l8p", "gen_netlist.py"), "gn_for_connected")


# ------------------------------------------------------------------------------------------------ composition
def script_of(board, key):
    rec, name = key.split("/")
    return os.path.join(REC, rec, "apply_gen_sch_%s_%s.py" % (board, name))


def apply(board, key, gen):
    script = script_of(board, key)
    args = [script, gen, rel(NET[board])] if key.startswith("d8dec31/") else [script, gen, "--write"]
    r = subprocess.run([sys.executable, "-B"] + args, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    last = ((r.stderr if r.returncode else r.stdout).decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    return r.returncode, last


def compose(board, d, keys, tag):
    gen = os.path.join(d, "%s-gen_sch_%s.py" % (tag, board))
    shutil.copy(rel("v2/ecad/tools/gen_sch_%s.py" % board), gen)
    steps = []
    for k in keys:
        rc, last = apply(board, k, gen)
        steps.append((k, rc, last))
        if rc:
            break
    return gen, steps


def regen(board, gen, d, tag):
    out = os.path.join(d, "%s-%s.net" % (tag, PRJ[board]))
    rc, log, table = GN.run(gen, out, PRJ[board])
    if rc != 0:
        return None, rc, ([l for l in (log or "").strip().splitlines() if l.strip()][-1:] or [""])[0], None
    return open(out, "rb").read(), 0, "", table


def change_list_order():
    """{apply script basename: (row, position in L4-E9's change list)}: L4-E9's register and script with this record's text draft
    apply_l4e9_changelist_p0.py applied IN MEMORY (rows R-220 to R-239; the tree's files are not written), its change list from L4-E9's
    own cons_changes, which refuses a list that misses an implementation row or breaks an order constraint"""
    dr = load(rel(CL_DRAFT), "l4e9_changelist_draft_for_connected")
    tree_before = {p: sha(p, 64) for p in (L4E9, REG, PAGE)}
    files, ch, m = dr.patch_all(ROOT)
    if any(sha(p, 64) != h for p, h in tree_before.items()):
        refuse("the draft wrote the tree")
    page = files[rel(PAGE)]
    page_ok = m.md_table(page, "| # | Step | Row |") == [["%d" % c[0]] + [str(x) for x in c[1:]] for c in ch]
    pos = {}
    for i, _step, rid, _bg, script, _dep, _g, _what, state in ch:
        for s in re.findall(r"apply_[a-z0-9_]+\.py", script):
            pos[s] = (rid, i, state)
    wd = [c[2] for c in ch if c[8].startswith("WITHDRAWN")]
    return pos, len(ch), m, page_ok, wd


def efuse_orders():
    """record efuse's own composition order, read with ast (its ORDER literal)"""
    tree = ast.parse(text("v2/docs/records/efuse/efuse_check.py"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ORDER" for t in node.targets):
            return ast.literal_eval(node.value)
    refuse("efuse_check.py's ORDER is not read")


def subseq(small, big):
    it = iter(big)
    return all(x in it for x in small)


# ------------------------------------------------------------------------------------------------ the record checks, composed mode
def part(table, ref):
    for p in table["parts"]:
        if p["ref"] == ref:
            return p
    return None


def mut_pin(table, ref, pin, net):
    t = copy.deepcopy(table)
    p = part(t, ref)
    if p is None or pin not in p["nets"]:
        return None
    p["nets"][pin] = net
    return t


def mut_pin_on(table, ref, old_net, net):
    p = part(table, ref)
    pins = [k for k, v in (p or {}).get("nets", {}).items() if v == old_net]
    return mut_pin(table, ref, sorted(pins, key=lambda x: (len(x), x))[0], net) if pins else None


def mut_val(table, ref, value):
    t = copy.deepcopy(table)
    p = part(t, ref)
    if p is None:
        return None
    p["value"] = value
    return t


def mut_drop(table, ref):
    t = copy.deepcopy(table)
    n = len(t["parts"])
    t["parts"] = [p for p in t["parts"] if p["ref"] != ref]
    return t if len(t["parts"]) == n - 1 else None


def raw_of(table):
    return GN.netlist(table).encode("utf-8")


def first(lines):
    """the first line that is not a DRAWN group's (the reason), else the first"""
    ls = [" ".join(str(l).split()) for l in (lines or [])]
    bad = [l for l in ls if re.search(r"\b(FAIL|NOT DRAWN)\b", l)]
    return ((bad or ls or [""])[0])[:150]


def checks(raws, intents, S):
    """{name: (verdict, first line)} for every record netlist check that applies to the composed boards"""
    A, B, D = raws["a"], raws["b"], raws["d"]
    out = {}
    out["l8gnd GND-002, board A"] = GND.judge("a", GND.read_netlist(A))
    out["l8gnd GND-002, board B"] = GND.judge("b", GND.read_netlist(B))
    out["l8r2 rounds 1 to 6, board A"] = L8R2.judge("a", L8R2.read_netlist(A))
    out["l8r2 rounds 1 to 7, board B"] = L8R2.judge("b", L8R2.read_netlist(B))
    out["l8p the loop and the guard, board A"] = L8P.judge("a", L8P.read_netlist(A))
    out["L4-E11 DD-7 (round 17, with the guard), board A"] = DD7.judge(A)
    out["l8r2 the ground return, board B"] = GR.judge(GR.read_netlist(B), intents["b"])
    v, lines, _w = GR.judge_pair(GR.read_netlist(A), GR.read_netlist(B))
    out["l8r2 the dedicated return, boards A and B"] = (v, lines)
    out["l9t5 I-03 / T10, board A (automatic mode)"] = L9.judge("a", L9.read(A))
    out["l9t5 I-03, board B"] = L9.judge("b", L9.read(B))
    out["l9t5 J_5V_IOC pair"] = L9.check_pair(L9.read(A), L9.read(B))
    st, msgs, _i = F01.check_a(L8P.read_netlist(A), S)
    out["l9t5 F01 the PA cap, board A"] = (st, msgs)
    st, msgs, _i = F01.check_d(L8P.read_netlist(D), S)
    out["l9t5 F01 the PA cap, board D"] = (st, msgs)
    pa, pd = F01.pin(L8P.read_netlist(A), "J_MEZZ1", "16"), F01.pin(L8P.read_netlist(D), "J_HARN1", "16")
    out["l9t5 F01 the harness pair J_MEZZ1.16 / J_HARN1.16"] = ("DRAWN" if pa == pd == "PA_ILIM" else "FAIL", ["%s / %s" % (pa, pd)])
    return out


def mutations(T):
    """(check name, label, board, mutated table) on the composed tables; each must not read DRAWN"""
    a, b, d = T["a"], T["b"], T["d"]
    c33 = [k for k, v in part(b, "C33")["nets"].items() if v == "CHASSIS"] if part(b, "C33") else []
    m0 = DD7.MAP[0]
    p0 = sorted(m0[2])[0]
    return [
        ("l8gnd GND-002, board A", "R229's ground pin moved to CHASSIS (the one bond lost)", "a", mut_pin(a, "R229", "2", "CHASSIS")),
        ("l8gnd GND-002, board B", "C33's cold end back on GND", "b", mut_pin(b, "C33", c33[0], "GND") if c33 else None),
        ("l8r2 rounds 1 to 6, board A", "U44's input (pin 4) on GND", "a", mut_pin(a, "U44", "4", "GND")),
        ("l8r2 rounds 1 to 7, board B", "U901's input (pin 4) on GND", "b", mut_pin(b, "U901", "4", "GND")),
        ("l8p the loop and the guard, board A", "R260's DOCK_EN_OUT end on GND", "a", mut_pin_on(a, "R260", "DOCK_EN_OUT", "GND")),
        ("L4-E11 DD-7 (round 17, with the guard), board A", "%s.%s moved off %s" % (m0[0], p0, m0[2][p0]), "a",
         mut_pin(a, m0[0], p0, "GND" if m0[2][p0] != "GND" else "+3V3")),
        ("l8r2 the ground return, board B", "J_GR1 pin 2 on +5V_DEV (V6's)", "b", mut_pin(b, "J_GR1", "2", "+5V_DEV")),
        ("l8r2 the dedicated return, boards A and B", "J_GR2 removed from board A (V6's)", "a", mut_drop(a, "J_GR2")),
        ("l9t5 I-03 / T10, board A (automatic mode)", "R602 at 12.0k (neither I-03's nor T10's divider)", "a", mut_val(a, "R602", "12.0k 0.1%")),
        ("l9t5 I-03, board B", "C900 from +5V_IOC to +5V_DEV", "b", mut_pin_on(b, "C900", "+5V_IOC", "+5V_DEV")),
        ("l9t5 J_5V_IOC pair", "board B's J_5V_IOC pin 1 on +5V_DEV", "b", mut_pin(b, "J_5V_IOC", "1", "+5V_DEV")),
        ("l9t5 F01 the PA cap, board A", "J_PA back on +13V8_PA (the sense bypassed)", "a", mut_pin_on(a, "J_PA", "+13V8_PAJ", "+13V8_PA")),
        ("l9t5 F01 the PA cap, board D", "R57 into VGG_SW (U15's output, not its feedback)", "d", mut_pin_on(d, "R57", "VGG_FB", "VGG_SW")),
        ("l9t5 F01 the harness pair J_MEZZ1.16 / J_HARN1.16", "J_HARN1 pin 16 back on AB_SPARE", "d", mut_pin(d, "J_HARN1", "16", "AB_SPARE")),
    ]


# ------------------------------------------------------------------------------------------------ the connected re-trace (4b)
def budget_alltx():
    t = text(OUTS["budget"])
    blk = need(t, r"^   == PS-ALLTX\n((?:      .*\n)+)", "the budget's PS-ALLTX block").group(1)
    rows = {}
    for m in re.finditer(r"^      (S1|S2|S3|DEV)\s+LM5176 (U\d+), average loop on 6 mOhm\s+([\d.]+) A\s+PLAN\s+([\d.]+)\s+HIGH\s+([\d.]+) \(([+-][\d.]+)\)"
                         r"\s+least V\s+([\d.]+) \(([+-][\d.]+)\)", blk, re.M):
        rows[m.group(1)] = dict(u=m.group(2), lim=float(m.group(3)), plan=float(m.group(4)), high=float(m.group(5)),
                                least=float(m.group(7)), m_least=float(m.group(8)))
    if sorted(rows) != ["DEV", "S1", "S2", "S3"]:
        refuse("the budget's PS-ALLTX block lacks a stage (%s)" % sorted(rows))
    return rows


def efuse_rows():
    t = text(OUTS["efuse"])
    bands = {}
    for m in re.finditer(r"^   EFUSE   ([AB]) (U\d+)\s+tps2596\s+([\d.]+) / ([\d.]+) / ([\d.]+) A\s+PRINTED", t, re.M):
        bands[(m.group(1), m.group(2))] = tuple(float(x) for x in m.group(3, 4, 5))
    verdict = {(m.group(1), m.group(2)): m.group(3) for m in re.finditer(r"^   EFUSE   ([AB]) (U\d+)\s+tps2596\s+(PASS|FAIL|[A-Z ]+?)\s*$", t, re.M)}
    rail = {(m.group(1), m.group(2)): (m.group(3), m.group(4)) for m in re.finditer(
        r"^   EFUSE   ([AB]) (U\d+)\s+TPS259631DDAR.*?-> (\+5V_\w+); setting (R\d+ [\w.]+ 1%)", t, re.M)}
    lime = [l.strip() for l in t.splitlines() if "J_LIME" in l and ("NOT COVERED" in l or "PROVISIONAL" in l)][:2]
    return bands, verdict, rail, lime


def service_unchanged(tree):
    """(True, keys) when the statements that build R["P01"] in l9t5_case.py copy the case's load set whole (v8 = dict(vals)) and
    replace only the PA's entry before R["P01"] is computed: read with ast, the body that assigns R["P01"]"""
    def is_p01(st):
        return (isinstance(st, ast.Assign) and any(isinstance(t_, ast.Subscript) and isinstance(t_.value, ast.Name) and t_.value.id == "R"
                                                   and isinstance(t_.slice, ast.Constant) and t_.slice.value == "P01" for t_ in st.targets))
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            continue
        idx = [i for i, st in enumerate(body) if is_p01(st)]
        if not idx:
            continue
        end = idx[0]
        starts = [i for i, st in enumerate(body[:end]) if isinstance(st, ast.Assign) and any(isinstance(t_, ast.Name) and t_.id == "v8" for t_ in st.targets)]
        if not starts:
            return False, []
        st0 = body[starts[-1]]
        copy_ok = (isinstance(st0.value, ast.Call) and getattr(st0.value.func, "id", "") == "dict" and len(st0.value.args) == 1
                   and getattr(st0.value.args[0], "id", "") == "vals")
        keys = []
        for st in body[starts[-1] + 1:end]:
            for n in ast.walk(st):
                if isinstance(n, ast.Assign):
                    for t_ in n.targets:
                        if isinstance(t_, ast.Subscript) and isinstance(t_.value, ast.Name) and t_.value.id == "v8":
                            keys.append(t_.slice.value if isinstance(t_.slice, ast.Constant) else "?")
        return copy_ok and keys == ["VHF PA 30 W"], keys
    return False, []


def main():
    for p in [CASES, L4E9, REG, PAGE, CL_DRAFT] + list(OUTS.values()) + SCRIPTS + GENS + list(NET.values()):
        if not os.path.isfile(rel(p)):
            refuse("%s is missing" % p)
    cs = " ".join(text(CASES).split())
    for h in ("## C-ALLTX rev 3", "## C-DEV rev 1", "## C-DEV rev 2", "## C-PROT rev 1", "## C-SHORE rev 1"):
        if h not in text(CASES):
            refuse("the case file lacks %s" % h)
    S = PL.read_sheets()
    tree_sha = {g: sha(g, 64) for g in GENS}
    out = []
    w = out.append
    w("l9t5_connected: the P0 round's parts 4b and 4c, THE CONNECTED P0 CANDIDATE (record l9t5, Slot A, MESHSAT-1357, 5 October 2026).")
    w("PROTOTYPE DESIGN, DESK ARITHMETIC: nothing built, bought, powered or measured; nothing applied to the tree's generators. A netlist")
    w("reading is not electrical qualification. Labels: PRINTED, TYPICAL, DECLARED, MODEL, ASSUMPTION, INFERRED, MISSING, PROVISIONAL.")
    w("No completion claim: power-design closure and fabrication release stay BLOCKED (the open items of section 9).")
    w("")
    w("0. PINS (sha256/16 path)")
    for p in [CASES, L4E9, REG, PAGE, CL_DRAFT] + list(OUTS.values()) + SCRIPTS + GENS + list(NET.values()):
        w("   %s %s" % (sha(p), p))
    w("")
    w("1. THE CASE ROWS (the coordinator's, the copy above; cited, never restated)")
    w("   C-ALLTX rev 3: REQ-018 with CONOPS 4a, every transmitter keyed, fans running, the standby WiFi card off, the other loads typical, a")
    w("     60 s key-down from a 15.5 V rest, cells at most +55 C; the pack at the gauge's indicated 18 A")
    w("   C-DEV rev 1 and rev 2: the device rail U7 at the least load voltage on PS-ALLTX (rev 2: the supervisors' bounded term, CONDITIONAL on")
    w("     FW-B20 and FW-B21)")
    w("   C-PROT rev 1: 10 A held and 18 A for 60 s never interrupted; the breaker's band 18.32 to 23.93 A; start at L4-E12's 76.25 C air")
    w("   C-SHORE rev 1: 7.136 A held by the input breaker from 76.25 C air (DD-3, a source present): NOT stacked with C-ALLTX (the pack alone")
    w("     at rest), which is a different state; each figure below names its row")
    w("")

    tmp = tempfile.mkdtemp(prefix="l9t5_connected_")
    try:
        # 2. composition
        pos, n_ch, L4m, page_ok, wd = change_list_order()
        w("2. THE COMPOSITION (4c, P0-6): L4-E9'S CHANGE-LIST ORDER, then Layer 6's order-free tables. The list is L4-E9's register and")
        w("   script with this record's text draft apply_l4e9_changelist_p0.py applied in memory (V6-m11: rows R-220 to R-239 for the drafts")
        w("   that had none; the tree's files unchanged until the integrator applies it with the re-takes the draft names): %d changes, every" % n_ch)
        w("   order constraint held by L4-E9's own cons_changes; the patched page's section 3 is the patched list: %s; WITHDRAWN: %s" % (
            "yes" if page_ok else "NO", ", ".join(wd) or "none"))
        P0_ = {"the drafted change list carries rows R-220 to R-239, holds every order constraint, its page table is its list, FAN_OK withdrawn":
               page_ok and sorted(wd) == ["R-210", "R-211", "R-212"] and all(("R-%d" % n) in [v[0] for v in pos.values()] for n in range(220, 240))}
        P = dict(P0_)
        T, raws, intents, ok_all = {}, {}, {}, True
        for b in "abd":
            gen, steps = compose(b, tmp, ORDER[b], "full")
            raw, rc, tail, table = regen(b, gen, tmp, "full")
            ok = all(s[1] == 0 for s in steps) and len(steps) == len(ORDER[b]) and raw is not None
            ok_all &= ok
            refs = [p["ref"] for p in (table or {}).get("parts", []) if not p["ref"].startswith("#")]
            dup = sorted({r for r in refs if refs.count(r) > 1})
            w("   board %s: %d drafts, %s; regenerated rc %d: %s parts, %s unplaced, intent written %s, designators %s" % (
                b.upper(), len(steps), "every one applied" if all(s[1] == 0 for s in steps) else "REFUSED at %s: %s" % (steps[-1][0], steps[-1][2][:100]),
                rc, len(refs) if table else "-", len(table["unplaced"]) if table else "-", bool(table and table.get("intent_written")),
                "unique" if not dup else "REPEATED %s" % dup))
            rows_ = []
            for k in ORDER[b]:
                s = os.path.basename(script_of(b, k))
                rows_.append("%s %s" % (k, pos[s][0] if s in pos else ("order-free" if k.split("/")[0] in ORDER_FREE else "NO ROW")))
            w("     " + "; ".join(rows_))
            seq = [pos[os.path.basename(script_of(b, k))][1] for k in ORDER[b] if os.path.basename(script_of(b, k)) in pos]
            in_order = seq == sorted(seq)
            no_row = [k for k in ORDER[b] if os.path.basename(script_of(b, k)) not in pos and k.split("/")[0] not in ORDER_FREE]
            tail_free = all(k.split("/")[0] in ORDER_FREE for k in ORDER[b][len(ORDER[b]) - sum(1 for k in ORDER[b] if k.split("/")[0] in ORDER_FREE):])
            w("     the composition follows the change list's positions: %s; every circuit draft has a row: %s; Layer 6's tables last: %s" % (
                "yes" if in_order else "NO", "yes" if not no_row else "NO (%s)" % ", ".join(no_row), "yes" if tail_free else "NO"))
            P["board %s composes in L4-E9's change-list order with every draft, every one with a row, and regenerates" % b.upper()] = (
                ok and in_order and not no_row and tail_free and not dup and table and not table["unplaced"] and table.get("intent_written"))
            T[b], raws[b], intents[b] = table, raw, (table or {}).get("intent")
        eo = efuse_orders()
        circ = {b: [k for k in ORDER[b] if k.split("/")[0] not in ORDER_FREE and k.split("/")[0] != "efuse" and k not in ("l9t5/paloop", "d8dec31/mainpb")]
                for b in "ab"}
        eo_k = {b: [s.replace("apply_gen_sch_%s_" % b, "").replace(".py", "") for s in eo[b]] for b in "ab"}
        same = all(circ[b] == eo_k[b] for b in "ab")
        w("   record efuse's own composition (efuse_check.py ORDER, read with ast) is this order without its own drafts, the PA cap and the")
        w("     last taker: %s" % ("yes, both boards (V6-m3 answered)" if same else "NO: A %s / B %s" % (eo_k["a"], eo_k["b"])))
        P["record efuse composes boards A and B in the same order"] = same
        if T["a"]:
            mp = [r for r in ("R603", "C607") if part(T["a"], r) and "MAIN_PB" in " ".join(part(T["a"], r)["nets"].values())]
            w("   d8dec31's mainpb, the last next-free taker: %s on MAIN_PB (V6 read R603 and C607; the register's R-193 text names R233 and C241" % (
                ", ".join(mp) or "NOT FOUND"))
            w("     for the round without the later drafts: R-194, its fixed references, stays a MISSING DRAFT for d8dec31's owner)")
            P["mainpb takes R603 and C607 on the full composition (V6's reading)"] = mp == ["R603", "C607"]
        if T["d"]:
            ptt = sorted(p["ref"] for p in T["d"]["parts"]
                         if (p["ref"][0] == "R" and any(str(v).endswith("_LEAD") for v in p["nets"].values())
                             and any(str(v).startswith("PTT_HS") and str(v).endswith("_n") for v in p["nets"].values()))
                         or (p["ref"][0] == "D" and "BAT46" in p["value"] and any(str(v).startswith("PTT_HS") for v in p["nets"].values())))
            w("   d8dec31's ptt on board D: its next-free picks (the 1 k series parts and the BAT46W) %s; the PA cap's fixed R57, R58, C76: %s" % (
                ", ".join(ptt), all(part(T["d"], r) for r in ("R57", "R58", "C76"))))
        w("")

        # 3. the record checks
        w("3. EVERY RECORD NETLIST CHECK IN ITS COMPOSED MODE (the regenerated netlists; V6's two breaking checks first)")
        C = checks(raws, intents, S) if ok_all else {}
        for k, (v, lines) in C.items():
            w("   %-62s %s  %s" % (k, v, first(lines)))
        P["every record check reads DRAWN on the composed candidate (DD-7 with the guard, V6-m2; l9t5 in its automatic mode, V6-m1)"] = (
            bool(C) and all(v == "DRAWN" for v, _l in C.values()))
        w("   not netlist checks, read from their records' outputs on this candidate (pinned above): the efuse record (section 6), T10's")
        w("     SHDN nets (l9t5_t10.out 10f), the breaker on board P (record l8p; board P is outside this composition, R-206)")
        w("")

        # 4. mutations
        w("4. ONE MUTATION PER CHECK, ON THE COMPOSED TABLES (each must not read DRAWN)")
        nfail, M = 0, mutations(T) if ok_all else []
        for name, label, b, tm in M:
            if tm is None:
                w("   %-62s %s: the anchor is not on the composed board: NOT RUN" % (name, label))
                continue
            r2 = dict(raws)
            r2[b] = raw_of(tm)
            i2 = dict(intents)
            v, lines = checks(r2, i2, S)[name]
            nfail += v != "DRAWN"
            w("   %-62s %s: %s  %s" % (name, label, v, first(lines)[:90]))
        w("   %d of %d mutations do not read DRAWN" % (nfail, len(M)))
        P["every mutation fails its check"] = bool(M) and nfail == len(M) == len(C)
        w("")

        # 5. the case and the converters
        case = load(rel("v2/docs/records/l9t5/l9t5_case.py"), "l9t5_case_for_connected")
        RC = case.compute()
        Q = RC["P01"]
        L = Q["L"]
        stk = text(OUTS["stk"])
        brk = need(stk, r"current limit ([\d.]+) / ([\d.]+) / ([\d.]+) A \(VCL", "the breaker's band")
        b_lo, b_typ, b_hi = (float(x) for x in brk.group(1, 2, 3))
        tmr = need(stk, r"fault timer: 10 nF \(\+-10 %\): ([\d.]+) to ([\d.]+) ms", "the breaker's fault timer")
        w("5. THE PACK AND THE CASE AT THE CAP (C-ALLTX rev 3; l9t5_case.py section 8, the PA's row the only one changed)")
        w("   the need at the indicated 18 A with the gauge's uncalibrated bound and the dock contacts at their maximum: %.4f V (MODEL on PRINTED" % Q["bnd"])
        w("     bounds; nominal %.4f V) against REQ-018's 15.5 V rest: %s, margin %.4f V; F01 / D-17 PROVISIONAL (B-PA1, B-PA2)" % (
            Q["nom"], "MEETS" if Q["bnd"] < RC["V"] else "NOT MET", RC["V"] - Q["bnd"]))
        w("   the pack's true current at the indicated 18 A: %.4f A (MODEL: the gauge's uncalibrated %.4f A); C-PROT rev 1's breaker band %.2f /" % (
            Q["i_true"], RC["U"]["gauge_uncal"], b_lo))
        w("     %.2f / %.2f A (PRINTED, record l9stk): the least limit %.4f A over the true current and %.2f A over the indicated 18 A service;" % (
            b_typ, b_hi, b_lo - Q["i_true"], b_lo - 18.0))
        w("     excursions over the least limit only under the fault timer's least %.3f ms (E-10, the supplier's bring-up bench)" % float(tmr.group(1)))
        P["the case at the cap meets 15.5 V (MODEL, PROVISIONAL) and the breaker's least limit stays over the 18 A service"] = (
            Q["bnd"] < RC["V"] and b_lo > 18.0 > Q["i_true"])
        # the service unchanged: the P01 load set is the case's own with only the PA's value replaced (read with ast)
        same_set, keys8 = service_unchanged(ast.parse(text("v2/docs/records/l9t5/l9t5_case.py")))
        w("   the required service unchanged: the case's load set copied whole (v8 = dict(vals)) and only %s replaced, by the cap's top %.2f W" % (
            ", ".join(repr(k) for k in keys8), L["p_max"]))
        w("     (no transmitter, fan or load reduced; the loop's own %.3f W added): %s" % (Q["loop_w"], "yes (read with ast)" if same_set else "NO"))
        P["the required service is unchanged: only the PA's value differs (read with ast)"] = same_set
        w("")
        bud = budget_alltx()
        dr = text(OUTS["drafts"])
        u7 = float(need(dr, r"board B's lead ([\d.]+) A plus the wall port", "U7's lead on C-DEV rev 1").group(1))
        P0R = load(rel("v2/docs/records/l8r2/l8r2_p0.py"), "l8r2_p0_for_connected")
        RR = P0R.compute()
        u601_1, u601_2, ioc1, ioc2 = RR["u601"]
        w("6. EVERY CONVERTER ON THE CONNECTED PATH (its input or loop current against its limit; the case each row is read on)")
        w("   U13 (the PA rail, LM5176 average loop on R55): the cap's top %.4f A plus R55's other loads %.4f A against U13's least %.4f A with R55" % (
            L["i_max"], L["r55_other"], L["u13_min"]))
        w("     hot (MODEL on PRINTED: VSNS 43 mV, WSL2512 TCR): %.4f A of room; C-ALLTX rev 3" % (L["u13_min"] - L["i_max"] - L["r55_other"]))
        P["U13 carries the cap's top and R55's other loads under its own least limit"] = L["i_max"] + L["r55_other"] < L["u13_min"]
        for k in ("S1", "S2", "S3"):
            r = bud[k]
            w("   %s %s (a slot's 5.1 V stage): HIGH %.3f A, at the least load voltage %.3f A, against its loop's %.4f A (record l9pwr 5b, PS-ALLTX)" % (
                k, r["u"], r["high"], r["least"], r["lim"]))
        P["the slot stages carry PS-ALLTX under their loops"] = all(bud[k]["least"] < bud[k]["lim"] for k in ("S1", "S2", "S3"))
        r = bud["DEV"]
        w("   U7 (the device rail): before I-03 %.3f A at the least load voltage against %.4f A (C-DEV rev 1's demand, OVER); with I-03 (U601 takes" % (
            r["least"], r["lim"]))
        w("     +5V_IOC off U7) board B's lead %.4f A (C-DEV rev 1, l9t5_drafts.out), under the loop by %.4f A" % (u7, r["lim"] - u7))
        P["U7 with I-03 carries C-DEV rev 1 under its loop"] = u7 < r["lim"]
        w("   U601 (+5V_IOC, TPS62933, 3 A PRINTED): %.4f A on C-DEV rev 1 (+5V_IOC %.4f A), %.4f A on rev 2 (+5V_IOC %.4f A; CONDITIONAL on" % (
            u601_1, ioc1, u601_2, ioc2))
        w("     FW-B20 and FW-B21); its declared peak 1.4749 A (DECLARED, the unbounded supervisors)")
        P["U601 stays under its 3 A on both revisions"] = max(u601_1, u601_2, 1.4749) < 3.0
        w("   every other converter: the case's own load set (section 5), unchanged by this round")
        w("")

        # 7. the feed and return conductors
        F = RR["F"]
        G = P0R.G
        least_th = G.least_rating(F["vh_a16"], F["vh_tmax"], P0R.TH)
        t_hold = F["vh_tmax"] - (F["vh_tmax"] - G.T_RATING_REF) * (L["i_max"] / F["vh_a16"]) ** 2
        w("7. THE FEED AND RETURN CONDUCTORS AGAINST THEIR PRINTED RATINGS")
        w("   J_PA and its 16 AWG lead (JST VH) at the cap's top %.4f A: under the PRINTED %.0f A; against the least rating the sheet allows at" % (L["i_max"], F["vh_a16"]))
        w("     C-PROT's 76.25 C air, %.4f A (INFERRED: the whole span to the %.0f C range top, l8r2's reading), %s by %.4f A; it holds to a" % (
            least_th, F["vh_tmax"], "OVER" if L["i_max"] > least_th else "under", abs(L["i_max"] - least_th)))
        w("     local air of %.2f C. PROVISIONAL with L8R2-F43's vendor task (JST's derating for VH at 16 AWG); it was the case's 8.19 A before" % t_hold)
        w("     the cap. Desk route if JST's curve is lower: two contacts a pole (a 1x4 VH), a Layer 7 harness row (finding below)")
        P["J_PA's cap-top current is under the VH's printed rating"] = L["i_max"] < F["vh_a16"]
        w("   J_5V_DEV pin 1 at board B's lead %.4f A: the same VH row (%.4f A INFERRED at 76.25 C), L8R2-F43, PROVISIONAL" % (u7, least_th))
        w("   the dock's four Mill-Max pins on the pack path: at their PRINTED maximum contact resistance inside the case's bound (section 5)")
        w("   the return between boards A and B (record l8r2, l8r2_p0.out; the solver on the composed design: the conductors the composed netlists")
        nA, nB = GR.read_netlist(raws["a"]), GR.read_netlist(raws["b"])
        lds = GR.leads(nB, intents["b"])
        gcB = GR.ground_conductors(nB)
        vP, _l, whole = GR.judge_pair(nA, nB)
        n_rib = sum(len(v) for v in gcB.values())
        w("     carry: %d lead contacts, %d ribbon ground conductors, %d return sockets whole on both boards, the solver's 6 lead, 17 ribbon and 3" % (
            len(lds), n_rib, len(whole)))
        w("     socket conductors: %s)" % ("the same" if (len(lds), n_rib, len(whole)) == (6, 17, 3) else "DIFFERENT"))
        P["the return solver's conductors are the composed netlists'"] = (len(lds), n_rib, len(whole)) == (6, 17, 3)
        for lab, tot in RR["totals"].items():
            for Tt in (P0R.TH, P0R.TC):
                rr = P0R.rows(F, tot, Tt)
                rt = P0R.ratings(F, Tt)
                w("     %-46s %7.4f A at %+6.2f C: VH %.4f A (printed %.1f, least %.4f), ribbon %.4f A (printed %.2f, least %.4f), XT60 %.4f A (%.0f)" % (
                    lab, tot, Tt, rr["VH"], rt["VH"][0], rt["VH"][1], rr["RIB"], rt["RIB"][0], rt["RIB"][1], rr["RET"], rt["RET"][0]))
        w("     on the one-node model (MODEL): every row under its printed rating; V6-B1's plane term PROVISIONAL on layout condition L8R2-F33a (the")
        w("     return's lands within 17 mm at 0.5 oz on the largest steady state; l8r2_p0.out), the declared upper bound's printed row and the")
        w("     least rows STILL OPEN; V6-B2's indirect paths bounded with vendor tasks (U.FL, HDMI: MISSING ratings), PROVISIONAL")
        w("")

        # 8. protection coordination
        bands, verdict, rail, lime = efuse_rows()
        c4 = text(OUTS["c4"])
        nt = need(c4, r"10 A held ([\d.]+) C, ([\d.]+) K under ([\d.]+) C; the 18 A service read as held ([\d.]+) C, ([\d.]+) K; the gauge's condition C4 ([\d.]+) C, ([\d.]+) K",
                  "the guard's no-trip margins")
        w("8. THE PROTECTION COORDINATION (each trip over its demand and under its downstream rating, with tolerances)")
        for k in sorted(bands):
            lo, nom, hi = bands[k]
            net, setting = rail.get(k, ("?", "?"))
            w("   eFuse %s %s (%s, %s): band %.4f / %.4f / %.4f A (PRINTED, range-wide), efuse_check.out: %s" % (k[0], k[1], net, setting, lo, nom, hi, verdict.get(k, "NOT READ")))
        for l in lime:
            w("     " + l[:150])
        P["the eFuse settings read PASS on the candidate (record efuse)"] = sorted(verdict) == sorted(bands) and all(v == "PASS" for v in verdict.values())
        w("   board P's breaker C-1 (LM5069, record l9stk; C-PROT rev 1): %.2f to %.2f A against the 18 A service and the true %.4f A (section 5);" % (b_lo, b_hi, Q["i_true"]))
        w("     its top %.2f A under the cells' 24 A (record l9stk E-9, the supplier's bench)" % b_hi)
        w("   the PA cap against U13's own loop: the cap acts first (its top %.4f A under U13's least %.4f A), so U13's loop is not the PA's limiter" % (L["i_max"], L["u13_min"]))
        w("   the thermal guard on the battery FETs (record l8p round 9, C-PROT rev 1): no trip at 10 A held (%s C, %s K under %s C), at the 18 A" % (nt.group(1), nt.group(2), nt.group(3)))
        w("     service read as held (%s C, %s K) and at the gauge's condition C4 (%s C, %s K) (PRINTED switch limits; l8p_c4.out)" % (nt.group(4), nt.group(5), nt.group(6), nt.group(7)))
        sol = os.path.isfile(rel(SOLAR_P0))
        w("   the solar guard (P0-7, the third author's): %s" % ("composed (see %s)" % SOLAR_P0 if sol else "NOT IN THIS CANDIDATE: P0-7 is in progress on its own branch; "
                                                               "board E is outside this composition"))
        w("")

        # 9. thermal limits
        t10 = text(OUTS["t10"])
        rv = need(t10, r"^\s+V\s+L4-E12 E5 mixed 76\.25 C\s+([\d.]+) A \(([\d.]+) C\)\s+([\d.]+) A\s+([\d.]+) C\s+holds", "T10's rev V row")
        f01 = text(OUTS["f01"])
        ina = need(f01, r"junction ([\d.]+) C at 76\.25 C air", "the INA250's junction")
        fet = need(stk, r"the battery FETs at ([\d.]+) C \(the guard ([\d.]+) to ([\d.]+) K above\)", "the battery FETs at the 18 A service")
        w("9. THE THERMAL LIMITS (each at the air its record reads)")
        w("   the supervisors' LDOs (T10, Slot C's round 5): %s C at the bounded state on rev V's rows at 76.25 C (MODEL; rev V fitted, L9T5-D7)," % rv.group(4))
        w("     under 125 C; rev Y's cover for a rev X part 125.2 C, PROVISIONAL on V-B20 (0.2318 A)")
        w("   U551 INA250A2 at the cap's top: junction %s C at 76.25 C air (TYPICAL RthJA; l9t5_f01.out)" % ina.group(1))
        w("   R55 (WSL2512 6 mOhm): %.3f W at the cap's top with R55's other loads, %.1f C at 76.25 C air (MODEL, ASSUMPTION %.0f K/W); U13's least" % (
            L["r55_w"], L["r55_t"], PL.R55_RTH))
        w("     limit is taken at that temperature (printed TCR), so the coordination of section 8 carries R55's own heating")
        w("   the battery FETs at the 18 A service: %s C with the guard %s to %s K above (record l9stk; DD-2 with Q42, condition C3)" % fet.group(1, 2, 3))
        w("")

        # 10. the session decision on L9T5-F22
        w("10. SESSION DECISION L9T5-D8 (under the owner's standing rule of 26 September 2026; authority SESSION; reversed_by: none)")
        w("   L9T5-F22 (R602 at 14.0 k, Slot C's scenario) is NOT taken in this candidate; L9T5-D7 (rev V fitted) stands as the PROVISIONAL")
        w("   choice with V-B20 the supplier's task for a rev X lot. Why: F22 admits rev X only by restating T10-A3 from the LDO's full 600 mA")
        w("   to 0.4512 A, with a dropout INFERRED between the printed 300 and 600 mA points, 35 mV over its requirement (3.7004 V against 3.6652 V):")
        w("   it trades a vendor reading for an unprinted figure and a narrowed acceptance, and the candidate would need the T10 chain re-run and")
        w("   its independent check again. To reverse: if the procurement read finds rev X lots only (L9T5-F23), draft R602 14.0 k with")
        w("   T10-A3 restated on a printed dropout (TI's) and re-take T10.")
        w("")

        # 11. what stays open on this candidate
        w("11. WHAT THIS CANDIDATE DOES NOT CLOSE (each with its route; constitution section 2)")
        w("   F01 / D-17: PROVISIONAL (B-PA1 the 30 W service under the cap's least; B-PA2 the loop's dynamics with E-10); L9P-F04 with it")
        w("   the return: V6-B1 PROVISIONAL on L8R2-F33a (Layer 10's extraction), the declared bound's printed row and the least rows OPEN; V6-B2")
        w("     vendor tasks (Hirose U.FL, Molex HDMI) UNSENT")
        w("   T10: L9T5-F06 OPEN pending its independent check; rev X on V-B20")
        w("   VH derating (J_PA, J_5V_DEV): L8R2-F43, JST's curve MISSING; finding L9T5-F24 (Layer 7, Layer 6): J_PA carries up to the cap's top,")
        w("     over the VH's least rating at 76.25 C as record l8r2 infers it; if JST's curve is lower at the PA lead's local air, J_PA becomes")
        w("     a 1x4 VH with two contacts a pole (a harness row and a board A land)")
        w("   the solar guard (P0-7): not in this candidate")
        w("   L4-E9's change-list rows: drafted (apply_l4e9_changelist_p0.py), applied by the integrator with the re-takes it names (L4-E11's")
        w("     and L4-E10's pins of the page, Layer 6's l6r2_passives compositions); L4-E9's own output refuses on this tree at its L4-E11 pin")
        w("")
        w("12. THE PREDICATES")
        for k, v in P.items():
            w("   %-125s %s" % (k, "yes" if v else "NO"))
        for g in GENS:
            if sha(g, 64) != tree_sha[g]:
                refuse("the tree's %s changed during the run" % g)
        w("")
        w("l9t5_connected: done")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(P.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
