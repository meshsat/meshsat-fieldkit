#!/usr/bin/env python3
"""Record l9t5, the P0 round's parts 4b and 4c (Slot A, MESHSAT-1357, 5 October 2026): THE CONNECTED P0 CANDIDATE.

4c (P0-6): boards A, B and D composed with EVERY pending draft in L4-E9's change-list order (records/l4e9/L4-POWER-ARCHITECTURE.md
section 3, with this record's text draft apply_l4e9_changelist_p0.py applied in memory: rows R-220 to R-245 for the drafts V6's
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
import json
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
import check_l8p_fs as L8PFS  # noqa: E402  (record l8p round 9: board A read by pin with the fail-safe delta, L8P-R9-F3)
import l9t5_paloop as PL  # noqa: E402

NET = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
       "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net", "e": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"}
PRJ = {"a": "pcb-a-power", "b": "pcb-b-compute", "d": "pcb-d-aprs", "e": "pcb-e1-dock"}
# the P0 candidate's composition: L4-E9's change list (rows R-01 to R-239, section 3) board by board, then Layer 6's order-free tables
ORDER = {
    "a": ["l4e6/r12", "l4e11/guard", "l4e11/charger", "l4e4/r11", "l4e8/bank", "l4e4/r138", "l4e9/u17", "l8gnd/gnd002", "l8gnd/hotr1",
          "l8r2/d8v3", "l8r2/vbus20ov", "l8r2/packrtn", "l8r2/slotlm", "l8r2/fb01", "l8p/ptc", "l4e11/dd7", "l8p/thguard", "l8p/thgfs",
          "l9t5/iocbuck", "l9t5/iocpre", "l9t5/iocset", "l8r2/gndrtn", "efuse/u23ilm", "l9t5/paloop", "d8dec31/mainpb", "l6r2/lcsc"],
    "b": ["l8gnd/gnd002", "l8r2/fans12", "l8r2/fandec", "l8r2/panel5v", "l8r2/ph4", "l8r2/rt500", "l8r2/gndret", "l8r2/gndrtn",
          "l9t5/iocbuck", "l9t5/iocpre", "l9t5/iocset", "l9t5/canshdn", "l9t5/iocguard", "efuse/u23ilm", "efuse/u24ilm", "l6r2/xal_land", "l6r2/lcsc", "l6r2/intent"],
    "d": ["d8dec31/ptt", "l9t5/paloop", "l6r2/intent", "l6r2/lcsc"],
    # board E (P0-7's round: its C2 sense; route B2 is OUT of the baseline after cx45 Q6 and the owner's part 24, INBOX 20: no step)
    "e": ["l4e9/q1", "l4e7/u5_grade", "l4e7/hold", "l4e7/input_limit", "l4e7/backstop", "l4e9/f1", "l4e9/hotswap", "l4e11/entry",
          "l4e7/solar_guard", "l4e7/p0sol", "l4e11/aux", "l8r2/packrtn", "l8p/enable", "d8dec31/cin", "l6r2/xal_land",
          "l6r2/lcsc"],
}
PROPOSAL = ()                  # route B2 (record l4e7's B2-PRESENCE.md) is out of the baseline: neither composed nor in the change list
P0SOL_PY = "v2/docs/records/l4e7/l4e7_p0sol.py"
ORDER_FREE = ("l6r2",)          # Layer 6's tables: order-free, after every circuit draft (no change-list row; L4-E9 section 3)
L4E9 = "v2/docs/records/l4e9/l4e9_power_path.py"
REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
CL_DRAFT = "v2/docs/records/l9t5/apply_l4e9_changelist_p0.py"   # this record's text draft for the integrator (V6-m11)
CASES = "v2/docs/records/l8r2/inputs/coordinator-cases-2026-10-05-cdev-rev2.md"
OUTS = {"budget": "v2/docs/records/l9pwr/l9pwr_budget.out", "drafts": "v2/docs/records/l9t5/l9t5_drafts.out",
        "efuse": "v2/docs/records/efuse/efuse_check.out", "stk": "v2/docs/records/l9stk/l9stk_protection.out",
        "c4": "v2/docs/records/l8p/l8p_c4.out", "t10": "v2/docs/records/l9t5/l9t5_t10.out", "f01": "v2/docs/records/l9t5/l9t5_f01.out",
        "p0ret": "v2/docs/records/l8r2/l8r2_p0.out", "p0sol": "v2/docs/records/l4e7/l4e7_p0sol.out",
        "dist": "v2/docs/records/l8r2/l8r2_dist.out"}
CX46 = "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"   # the one targeted recheck, filed as received (main 0d5f855e)
# the fault rows the connected verdict depends on (cx46 items 13 and 17): (row, the cx46 classification item that holds it, what it
# removes or weakens). A row is OPEN while cx46 classifies its item NOT CLOSED: the method ended there, so no later check closes it.
FAULT_ROWS = (
    ("the latent rail-trip failure (its monitor dead or OUTB released; V-B23's response against the drafted RC network)", 6,
     "T10's thermal bound and T10-A3's hardware bound"),
    ("the sustained peaks (a periodic load under the trip's average over 125 C)", 7, "the sustained thermal bound, the worst-case margin row"),
    ("L8P-R9-F1 (a latent first failure then the other path; the retry heating after the loss of path 1 unbounded)", 10,
     "C-PROT's protection claim (the guard's row)"),
    ("L9T5-F21 (a TX pin toggled as a GPIO under the limiter's share; a latent share comparator)", 5, "CON-004's quorum service, FW-B22"),
    ("VOS0 under the trip (the controller past its 105 C VOS0 limit below the trip band)", 17, "controller survival, FW-B20 and FW-B22 service"),
    ("V6-B1 (the selected XT60-F lands, the real sites, a justified distributed resistance, each LDO's own shift)", 4,
     "the return's rows, T10-A3's shift with the dedicated return"),
    ("F01's reference loading through Q551's hold and release, and the acceptance limits", 2, "the PA cap's band, C-ALLTX rev 3 at the cap"),
)
SCRIPTS = ["v2/docs/records/l8r2/l8r2_dist.py", "v2/docs/records/l4e7/l4e7_p0sol.py", "v2/docs/records/l9t5/l9t5_t10.py", "v2/docs/records/l9t5/l9t5_drafts.py", "v2/docs/records/l9t5/l9t5_case.py", "v2/docs/records/l8r2/l8r2_p0.py", "v2/docs/records/l8r2/l8r2_gndret.py",
           "v2/docs/records/l9t5/l9t5_paloop.py", "v2/docs/records/efuse/efuse_check.py", "v2/docs/records/l8p/gen_netlist.py",
           "v2/docs/records/l9t5/check_f01_netlist.py", "v2/docs/records/l9t5/check_l9t5_netlist.py", "v2/docs/records/l8p/check_l8p_netlist.py",
           "v2/docs/records/l8r2/check_l8r2_netlist.py", "v2/docs/records/l8r2/check_gndret_netlist.py",
           "v2/docs/records/l8gnd/check_gnd002_netlist.py", "v2/docs/records/l4e11/check_dd7_netlist.py"]
GENS = ["v2/ecad/tools/gen_sch_%s.py" % b for b in "abde"]
T10_PY = "v2/docs/records/l9t5/l9t5_t10.py"     # Slot C's T10 record: its sheets' figures and chain terms, imported for L9T5-F22


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
P0SOL = load(os.path.join(ROOT, "v2", "docs", "records", "l4e7", "l4e7_p0sol.py"), "l4e7_p0sol_for_connected")   # its B2 judge, imported


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
    apply_l4e9_changelist_p0.py applied IN MEMORY (rows R-220 to R-245; the tree's files are not written), its change list from L4-E9's
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
    # board A carries record l8p's fail-safe delta (round 9): its own reader check_l8p_fs.py reads the loop and the guard (L8P-R9-F3;
    # check_l8p_netlist.py's round 8 reader stays as its owner left it, its digest printed by other records)
    fs = L8PFS.judge(L8P.read_netlist(A))
    vs = [v for v, _w in fs.values()]
    out["l8p the loop and the guard with the fail-safe delta, board A"] = (
        "DRAWN" if all(v == "DRAWN" for v in vs) else ("FAIL" if "FAIL" in vs else "NOT DRAWN"),
        ["A %s %s%s" % (k, v, (": " + "; ".join(w_[:2])) if w_ else "") for k, (v, w_) in fs.items()])
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
    if "e" in raws:
        E = raws["e"]
        out["l8p the loop's board E half (J_SMB, J_BLK)"] = L8P.judge("e", L8P.read_netlist(E))
        bad = [s for s, ok in P0SOL.judge(L8P.read_netlist(E)) if not ok]
        out["l4e7 P0-7 the sense on the backstop's bank (C2)"] = ("FAIL" if bad else "DRAWN", bad or ["every predicate of C2 holds"])
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
        ("l8p the loop and the guard with the fail-safe delta, board A", "R260's DOCK_EN_OUT end on GND", "a", mut_pin_on(a, "R260", "DOCK_EN_OUT", "GND")),
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
        ("l8p the loop's board E half (J_SMB, J_BLK)", "J_SMB pin 7 on GND", "e", mut_pin(T["e"], "J_SMB", "7", "GND")),
        ("l4e7 P0-7 the sense on the backstop's bank (C2)", "U23's output off IMON_IN (the regulation's sense lost)", "e",
         mut_pin(T["e"], "U23", "1", "IMON_X")),
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


def f22_chain(nlb):
    """L9T5-F22 judged over the connected circuit (the owner's part 22 item 3) with Slot C's containment composed (round 6, cx45's Q3:
    apply_gen_sch_b_iocguard.py): each LDO's input at the least set point after the rail's copper budget, the lead (three LDOs' current
    on J_5V_IOC's pin 1, hot wire and two contacts), the ground shift between the boards and its own rail trip's sense resistor (read
    from the composed board B by topology, at the top of its printed tolerance), as drawn and with the dedicated return, at the LDO's
    printed full current, at the hardware bound T10-A3 is judged at since round 6 (the rail trip's maximum, l9t5_t10.out 10j (d)) and at
    L9T5-D8's superseded 0.4512 A (for the record); the thermal side per set point without the containment (Slot C's 10i babbling row)
    and with it (the trip's held maximum: Slot C's MODEL at 14.0 k, the other set points INFERRED, scaled by the regulator's drop)"""
    T = load(rel(T10_PY), "l9t5_t10_for_connected")
    D = T.D
    P, DP, G = T.figures(), D.figures(), D.gndret()
    r_sup = G["rhot"] + 2 * DP["vh_r"][1]
    t10 = text(OUTS["t10"])
    need(t10, r"10j\. THE CHECK cx45's Q3", "T10's round 6 (10j)")
    t10j = " ".join(t10.split("10j. THE CHECK cx45's Q3", 1)[1].split("\n11. ", 1)[0].split())
    i_hold = float(need(t10, r"computes for a regulator \(([\d.]+) A, the held B5 row on rev Y", "T10's held current (L9T5-D8)").group(1))
    a3 = need(t10j, r"T10-A3 at the trip's AVERAGE maximum \(L9T5-D8's criterion superseded; .*?\): each LDO's input at ([\d.]+) A, "
                    r"the sense resistor's drop counted: at least ([\d.]+) V against ([\d.]+) V: holds", "T10-A3 at the trip's average maximum (10j (d))")
    i_trip = float(a3.group(1))
    win = need(t10j, r"the average is over the threshold: ([\d.]+) to ([\d.]+) A at the tolerances", "the rail trip's window (10j (b))")
    th = need(t10j, r"a constant current at the trip's average maximum [\d.]+ A reads the LDO's junction ([\d.]+) C at ([\d.]+) C air",
              "the trip's constant-current temperature (10j (e))")
    tj_trip14, air = float(th.group(1)), float(th.group(2))
    cm = need(t10j, r"the junction's periodic peak ([\d.]+) C, OVER 125 C: the universal sustained bound and its positive margin are WITHDRAWN",
              "cx46's periodic countermodel as Slot C reproduces it (10j (e))")
    tj_peak = float(cm.group(1))
    serve = [(m.group(1), float(m.group(2)), float(m.group(3))) for m in re.finditer(
        r"(the bounded state with the limiters' pull-ups|B\w+ with the response|both fabrics faulted, responded|a babbler, the limiters bounding it) "
        r"([\d.]+) A LDO ([\d.]+) C", t10j)]
    if len(serve) < 3:
        refuse("the served states under the containment (10j (e)) are not read")
    bab = need(t10, r"^\s+babbling \(nothing ends it\)\s+V\s+([\d.]+) A\s+125 C \(sustained\)\s+([\d.]+) C (?:FAILS|holds)\s+([\d.]+) C (holds|FAILS)",
               "the babbling row on revision V without the containment (part 22, 10i)")
    # each LDO's own sense resistor on the composed board B: the one resistor joining +5V_IOC to the LDO's input (L9T5-F25)
    sense = []
    for u, _r, _c in L9.LDOS:
        vin = L9.ldo_in(nlb, u)
        refs = [r for r in nlb["pins"] if vin and r.startswith("R") and L9.two(nlb, r) == sorted([L9.IOC, vin])]
        val = L9.value(nlb, refs[0]) if len(refs) == 1 else ""
        m = re.match(r"([\d.]+)R\s+([\d.]+)%", val)
        if not m:
            refuse("%s's sense resistor is not read on the composed board B (%s %r)" % (u, refs, val))
        sense.append((u, refs[0], val, float(m.group(1)) * (1.0 + float(m.group(2)) / 100.0)))
    r_s = max(s[3] for s in sense)

    def drop_at(i):
        if abs(i - 0.6) < 1e-9:
            return P["drop"][600], "PRINTED"
        if i <= 0.3:
            return P["drop"][10] + (P["drop"][300] - P["drop"][10]) * (i - 0.01) / 0.29, "INFERRED between the printed 10 and 300 mA"
        return P["drop"][300] + (P["drop"][600] - P["drop"][300]) * (i - 0.3) / 0.3, "INFERRED between the printed 300 and 600 mA"
    tops = {rb: T.CHK.vout_band(T.R601, rb) for rb in (13.3e3, 13.8e3, 14.0e3)}
    tj = {13.3e3: (float(bab.group(2)), "Slot C's MODEL"), 14.0e3: (float(bab.group(3)), "Slot C's MODEL")}
    h0, h1 = tops[13.3e3][2], tops[14.0e3][2]
    tj[13.8e3] = (tj[13.3e3][0] + (tj[14.0e3][0] - tj[13.3e3][0]) * (tops[13.8e3][2] - h0) / (h1 - h0), "INFERRED, linear in the top")
    d14 = tops[14.0e3][2] - 3.3 * P["vout_lo"]
    tj_trip = {rb: (air + (tj_trip14 - air) * (tops[rb][2] - 3.3 * P["vout_lo"]) / d14,
                    "Slot C's MODEL" if abs(rb - 14.0e3) < 1 else "INFERRED, Slot C's 14.0 k figure scaled by the drop") for rb in tops}
    sh_dist = float(need(text(OUTS["dist"]), r"the AVERAGED ground shift at the supervisors' LDOs on the service cases: at most ([\d.]+) V",
                         "the distributed study's averaged shift").group(1))
    rows = []
    for rb, (lo, nom, hi) in tops.items():
        for ret, shift in (("as drawn", G["shift_drawn_ub"]), ("with the dedicated return", sh_dist)):
            for i, crit in ((0.6, "the rating"), (i_trip, "the hardware bound"), (i_hold, "L9T5-D8, superseded")):
                dr, lab = drop_at(i)
                need_ = 3.3 * (P["vout_hi"] + P["load"] * i) + dr
                at = lo - D.RAIL_BUDGET * nom - 3 * i * r_sup - shift - r_s * i
                rows.append(dict(rb=rb, lo=lo, nom=nom, hi=hi, ret=ret, shift=shift, i=i, crit=crit, need=need_, at=at, lab=lab, ok=at >= need_))
    return dict(rows=rows, i_hold=i_hold, i_trip=i_trip, win=(float(win.group(1)), float(win.group(2))), a3=(float(a3.group(2)), float(a3.group(3))),
                tj=tj, tj_trip=tj_trip, tj_peak=tj_peak, air=air, serve=serve, sense=sense, r_s=r_s, r_sup=r_sup, vin_max=P["vin"][1], i_bab=float(bab.group(1)),
                bab_ok=bab.group(4) == "holds", drop_trip=drop_at(i_trip)[0], tops=tops)


def drop_mv(FC):
    """the INFERRED dropout at the hardware bound, mV"""
    return 1000.0 * FC["drop_trip"]


def fault_rows():
    """[(row, cx46 item, its classification, affected claims, OPEN)] read from the filed cx46 record's JSON (parsed, never grepped)"""
    raw = text(CX46)
    if "```json" not in raw:
        refuse("the filed cx46 record carries no JSON block")
    J = json.loads(raw.split("```json", 1)[1].split("```", 1)[0])
    if not J.get("summary", "").startswith("P0 RECHECK: CORRECTIONS NOT CLOSED"):
        refuse("the filed cx46 record's verdict is not read")
    cls = {}
    for c in J["classification"]:
        m = re.match(r"^(\d+)(?: and \d+)?\. .*: (NOT CLOSED|CLOSED BY THE CORRECTION|CLOSED AS CONDITIONAL)$", c["item"])
        if not m:
            refuse("a cx46 classification item is not read (%s)" % c["item"][:60])
        cls[int(m.group(1))] = m.group(2)
    rows = []
    for row, item, aff in FAULT_ROWS:
        if item not in cls:
            refuse("cx46 has no item %d" % item)
        rows.append((row, item, cls[item], aff, cls[item] == "NOT CLOSED"))
    return rows, J["base_commit"][:8]


def main():
    for p in [CASES, L4E9, REG, PAGE, CL_DRAFT, CX46] + list(OUTS.values()) + SCRIPTS + GENS + list(NET.values()):
        if not os.path.isfile(rel(p)):
            refuse("%s is missing" % p)
    cs = " ".join(text(CASES).split())
    for h in ("## C-ALLTX rev 3", "## C-DEV rev 1", "## C-DEV rev 2", "## C-PROT rev 1", "## C-SHORE rev 1"):
        if h not in text(CASES):
            refuse("the case file lacks %s" % h)
    S = PL.read_sheets()
    FR, cx46_base = fault_rows()
    OPEN = {item: op for _r, item, _c, _a, op in FR}
    RE = "REMAINING ENGINEERING"
    tree_sha = {g: sha(g, 64) for g in GENS}
    out = []
    w = out.append
    w("l9t5_connected: the P0 round's parts 4b and 4c, THE CONNECTED P0 CANDIDATE (record l9t5, Slot A, MESHSAT-1357, 5 October 2026).")
    w("PROTOTYPE DESIGN, DESK ARITHMETIC: nothing built, bought, powered or measured; nothing applied to the tree's generators. A netlist")
    w("reading is not electrical qualification. Labels: PRINTED, TYPICAL, DECLARED, MODEL, ASSUMPTION, INFERRED, MISSING, PROVISIONAL.")
    w("No completion claim: power-design closure and fabrication release stay BLOCKED. After cx46 (P0 RECHECK: CORRECTIONS NOT CLOSED, the")
    w("second negative, which ends the method) the connected electrical verdict reads REMAINING ENGINEERING (section 11), never a positive")
    w("acceptance: every figure below is a MODEL reading on the composed candidate.")
    w("")
    w("0. PINS (sha256/16 path)")
    for p in [CASES, L4E9, REG, PAGE, CL_DRAFT, CX46] + list(OUTS.values()) + SCRIPTS + GENS + list(NET.values()):
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
        w("2. THE COMPOSITION (4c, P0-6, boards A, B and D; board E with P0-7): L4-E9'S CHANGE-LIST ORDER, then Layer 6's order-free tables. The list is L4-E9's register and")
        w("   script, which carry this record's text draft apply_l4e9_changelist_p0.py (V6-m11: rows R-220 to R-245 for the drafts that had none)")
        w("   as the integrator applied it at 7070f106, read from the tree (the draft's applied state), set 31's R-246 with them: %d changes, every" % n_ch)
        w("   order constraint held by L4-E9's own cons_changes; the patched page's section 3 is the patched list: %s; WITHDRAWN: %s" % (
            "yes" if page_ok else "NO", ", ".join(wd) or "none"))
        P0_ = {"the drafted change list carries rows R-220 to R-245 (no R-241: route B2 out), holds every order constraint, its page table is its list, FAN_OK withdrawn":
               page_ok and sorted(wd) == ["R-210", "R-211", "R-212"] and all(("R-%d" % n) in [v[0] for v in pos.values()] for n in range(220, 246) if n != 241)}
        P = dict(P0_)
        T, raws, intents, ok_all = {}, {}, {}, True
        for b in "abde":
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
                rows_.append("%s %s%s" % (k, pos[s][0] if s in pos else ("order-free" if k.split("/")[0] in ORDER_FREE else "NO ROW"),
                                          " (PROPOSAL)" if k in PROPOSAL else ""))
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
        e_same = [tuple(k.split("/")) for k in ORDER["e"]] == [tuple(x) for x in P0SOL.ORDER_E]
        w("   board E is record l4e7's own baseline composition (ORDER_E, imported; no route B2 step: it is out of the baseline): %s" % (
            "the same order" if e_same else "A DIFFERENT ORDER"))
        P["board E composes as record l4e7's baseline composes it (route B2 out of the baseline)"] = e_same
        eo = efuse_orders()
        circ = {b: [k for k in ORDER[b] if k.split("/")[0] not in ORDER_FREE and k.split("/")[0] != "efuse"
                    and k not in ("l9t5/paloop", "d8dec31/mainpb", "l9t5/iocset", "l8p/thgfs", "l9t5/iocguard")] for b in "ab"}
        eo_k = {b: [s.replace("apply_gen_sch_%s_" % b, "").replace(".py", "") for s in eo[b]] for b in "ab"}
        same = all(circ[b] == eo_k[b] for b in "ab")
        w("   record efuse's own composition (efuse_check.py ORDER, read with ast) is this order without its own drafts, the PA cap, T10's")
        w("     set point delta, record l8p's fail-safe delta and the supervisors' containment (later than its round 2) and the last taker: %s" % ("yes, both boards (V6-m3 answered)" if same else "NO: A %s / B %s" % (eo_k["a"], eo_k["b"])))
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
        P["the case's power load set is unchanged: only the PA's value differs (read with ast)"] = same_set
        # the CAN mechanism the supervisors' quorum runs on (cx45 Q7): its service under FW-B21's share with FW-B22's schedule (Slot C's
        # round 6) and under a babbling supervisor with the containment composed
        t10s = text(OUTS["t10"])
        can = {int(m.group(1)): (int(m.group(2)), int(m.group(3)), m.group(4)) for m in re.finditer(
            r"^     at\s+(\d+) kbit/s:\s+\d+ dominant bit times a window:\s+(\d+) frames of 135 bits.*?\n\s+the need (\d+) \((inside|NOT inside)", t10s, re.M)}
        if sorted(can) != [125, 500, 1000]:
            refuse("T10's CAN service rows are not read (%s)" % sorted(can))
        assum = need(t10s, r"The tree defines no CAN message rate; the record ASSUMES\s+1 state frame per supervisor per fabric per 100 ms", "T10's assumed message set")
        t10sj = " ".join(t10s.split("10j. THE CHECK cx45's Q3", 1)[-1].split())
        sch = need(t10sj, r"Its dominant bound, every bit counted dominant plus (\d+) acknowledgements: (\d+) bit-times against FW-B21's (\d+) \(2 % of the "
                          r"window at 500 kbit/s; (\d+) at 1 Mbit/s\): (inside|NOT inside); the bus ([\d.]+) % loaded at 500 kbit/s; a state frame waits at most "
                          r"([\d.]+) ms", "FW-B22's schedule (10j (a))")
        qd = need(t10sj, r"the quorum's 2-of-3 decision reads the three state frames of one window: at most (\d+) ms plus ([\d.]+) ms", "the quorum's decision time (10j (a))")
        t_bab = need(t10sj, r"a CONTROLLER-DRIVEN babbler denies the bus at most for its detection time, (\d+) ms", "the babbler's detection time (10j (c))").group(1)
        bab_open = OPEN[5]          # L9T5-F21: cx46 item 5 NOT CLOSED (the GPIO-toggled TX pin, the latent share comparator)
        w("   the CAN mechanism (the supervisors' quorum; Slot C's T10): round 5's ASSUMED set (l9t5_t10.out 10h: %d frames a window against" % can[500][1])
        w("     FW-B21's %d at 500 kbit/s, %s) is replaced by FW-B22's schedule (Slot C's round 6, 10j (a), drafted in the firmware contract):" % (
            can[500][0], can[500][2]))
        w("     per supervisor and fabric one state frame and at most five event frames a 100 ms window, %s dominant bit-times with %s" % (sch.group(2), sch.group(1)))
        w("     acknowledgements against FW-B21's %s at 500 kbit/s (%s at 1 Mbit/s): %s; the bus %s %% loaded; a state frame waits at most %s ms;" % (
            sch.group(3), sch.group(4), sch.group(5), sch.group(6), sch.group(7)))
        w("     the quorum's decision within %s ms plus %s ms: the service under the bound PROVISIONAL (a drafted schedule; V-B21, V-B22 the" % qd.group(1, 2))
        w("     firmware's to confirm); under a BABBLING supervisor through its FDCAN, with the containment composed here (Slot C's round 6, 10j;")
        w("     CORRECTED IN DRAFT, UNCHECKED): its transceivers silenced in hardware within %s ms, the voters holding the home assignment" % t_bab)
        w("     meanwhile (row 8) and the other two serving after: PROVISIONAL; NOT ESTABLISHED for a TX pin repurposed as a GPIO and toggled")
        w("     under the limiter's least share, and after a latent stuck comparator (V-B22, V-B23): L9T5-F21 %s on those, handed over as" % (
            "OPEN" if bab_open else "NOT READ"))
        w("     remaining engineering. The R602 change moves no CAN rate, share or state; it changes the LDOs' heat only")
        P["the CAN service is stated per state: PROVISIONAL under the bound and under a babbler the containment silences, NOT ESTABLISHED for the toggled TX pin"] = (
            bab_open and assum is not None and sch.group(5) == "inside")
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
        w("     +5V_IOC off U7) board B's lead %.4f A on C-DEV rev 2, the active row (U7's demand is rev 1's: rev 2 changes the supervisors' term" % u7)
        w("     only, which I-03 has taken off U7; l9t5_drafts.out, l8r2_p0.out), under the loop by %.4f A" % (r["lim"] - u7))
        P["U7 with I-03 carries C-DEV rev 2 (the active row) under its loop"] = u7 < r["lim"]
        w("   U601 (+5V_IOC, TPS62933, 3 A PRINTED): %.4f A on C-DEV rev 1 (+5V_IOC %.4f A), %.4f A on rev 2 (+5V_IOC %.4f A; CONDITIONAL on" % (
            u601_1, ioc1, u601_2, ioc2))
        w("     FW-B20 and FW-B21); its declared peak 1.4749 A (DECLARED, the unbounded supervisors)")
        t10c = text(OUTS["t10"])
        bv = need(t10c, r"^     the bounded state \(FW-B20, FW-B21\)\s+V\s+([\d.]+) A", "the bounded state on rev V (10i)").group(1)
        by_ = need(t10c, r"^     the bounded state \(FW-B20, FW-B21\)\s+Y\s+([\d.]+) A", "rev Y's bounded state, rev 2's cover (10i)").group(1)
        bpu = need(" ".join(t10c.split("10j. THE CHECK cx45's Q3", 1)[-1].split()), r"the bounded state with the limiters' pull-ups ([\d.]+) A",
                   "the bounded state with the containment (10j (e))").group(1)
        w("     the containment composed (Slot C's round 6): the limiters' pull-ups raise each supervisor's bounded state to %s A on rev V against" % bpu)
        w("     rev 2's %s A, inside the %s A cover the rev 2 row carries (rev Y's bounded state): no case row changes (10j (e))" % (bv, by_))
        P["U601 stays under its 3 A on both revisions"] = max(u601_1, u601_2, 1.4749) < 3.0 and float(bpu) < float(by_)
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
        nA, nB = GR.read_netlist(raws["a"]), GR.read_netlist(raws["b"])
        lds = GR.leads(nB, intents["b"])
        gcB = GR.ground_conductors(nB)
        vP, _l, whole = GR.judge_pair(nA, nB)
        n_rib = sum(len(v) for v in gcB.values())
        dist = text(OUTS["dist"])
        w("   the return between boards A and B (record l8r2, l8r2_dist.out after cx45's Q2: a STUDY, the sockets placed on the drawn boards on")
        w("     a stand-in XT60-M land, the return solved as a distributed network on assumed sites and fill at the local contact corners; the composed")
        w("     netlists carry %d lead contacts, %d ribbon ground conductors and %d return sockets whole on both boards, the conductors it solves)" % (
            len(lds), n_rib, len(whole)))
        P["the distributed return's conductors are the composed netlists'"] = (len(lds), n_rib, len(whole)) == (6, 17, 3)
        rows_d = re.findall(r"^     ([+-]\d+\.\d\d) C (VH|RIB|RET)\s+(\S+)\s+([\d.]+) A \(.*?\): printed ([\d.]+) A (holds|OVER); least ([\d.]+) A (holds|OVER)$", dist, re.M)
        cases_d = re.findall(r"^   (C-DEV rev 2|C-DEV rev 1|the largest steady state|the declared upper bound)[^:]*: ([\d.]+) A \(", dist, re.M)
        if len(rows_d) != 6 * len(cases_d) or len(cases_d) != 4:
            refuse("l8r2_dist.out's rows are not read (%d rows, %d cases)" % (len(rows_d), len(cases_d)))
        for ci, (lab, tot) in enumerate(cases_d):
            rr_ = rows_d[6 * ci:6 * ci + 6]
            w("     %-26s %s A: %s" % (lab, tot, "; ".join("%s C %s %s A (printed %s %s, least %s %s)" % (
                r_[0], r_[1], r_[3], r_[4], r_[5], r_[6], r_[7]) for r_ in rr_)))
        svc_ok = all(r_[5] == "holds" and r_[7] == "holds" for ci, (lab, _t) in enumerate(cases_d) if lab in ("C-DEV rev 2", "the largest steady state")
                     for r_ in rows_d[6 * ci:6 * ci + 6])
        pr_ok = all(r_[5] == "holds" for r_ in rows_d)
        sh = need(dist, r"the AVERAGED ground shift at the supervisors' LDOs on the service cases: at most ([\d.]+) V", "the distributed ground shift")
        w("     every printed row %s; the service cases (C-DEV rev 2, the largest steady state) %s on the least ratings too; over the INFERRED" % (
            "holds" if pr_ok else "does NOT hold", "hold" if svc_ok else "do NOT hold"))
        w("     least only the declared upper bound at 76.25 C (VH pin 2 with its pin 1, L8R2-F43; the ribbon, L8R2-F44, a placed fourth lead its")
        w("     route, not drafted: L8R2-D11); the AVERAGED ground shift at the supervisors' LDOs at most %s V on the service cases (section 10" % sh.group(1))
        w("     uses it; each LDO's own is not established)")
        v6b1 = need(dist, r"DISPOSITION OF V6-B1 AFTER cx46 \(kept as given; the second negative ends the method\): (OPEN, REMAINING ENGINEERING)",
                    "V6-B1's disposition after cx46").group(1)
        w("     V6-B1: %s for the receiving company (l8r2_dist.out 6; cx46 item 4: %s): the study is evidence toward the route, not a" % (
            v6b1, "NOT CLOSED" if OPEN[4] else "closed"))
        w("     correction. V6-B2's indirect paths bounded with vendor tasks (U.FL, HDMI: MISSING ratings), PROVISIONAL")
        P["the return STUDY holds every printed row and the service cases' least rows (MODEL); V6-B1 reads OPEN, REMAINING ENGINEERING"] = (
            pr_ok and svc_ok and v6b1.startswith("OPEN") and OPEN[4])
        w("")

        # 8. protection coordination
        bands, verdict, rail, lime = efuse_rows()
        c4 = text(OUTS["c4"])
        nt = need(c4, r"10 A held ([\d.]+) C, ([\d.]+) K under ([\d.]+) C; the 18 A service read as held ([\d.]+) C, ([\d.]+) K; the gauge's condition C4 ([\d.]+) C, ([\d.]+) K",
                  "the guard's no-trip margins")
        w("8. THE PROTECTION COORDINATION, ROW BY ROW (cx45 Q7: each trip's band against its demand below and its downstream ratings above,")
        w("   printed and at the inside air; what is NOT established is named in its row)")
        efo = text(OUTS["efuse"])
        coord_ok = True
        for k in sorted(bands):
            lo, nom, hi = bands[k]
            net, setting = rail.get(k, ("?", "?"))
            blk = efo.split("   EFUSE   %s %s   tps2596   %s" % (k[0], k[1], verdict.get(k, "")), 1)[1].split("\n   EFUSE", 1)[0] if verdict.get(k) else ""
            bm = re.search(r"\(b\) PASS: ([\d.]+) A >= ([\d.]+) A", blk)
            cm = re.search(r"\(c\) PASS: ([\d.]+) A <= ([\d.]+) A \(([^)]*)\)", blk)
            air = [l.strip() for l in efo.split("5b. ROUND 2 (V6-m4)", 1)[1].split("\n\n", 1)[0].splitlines() if l.strip().startswith("%s %s " % k)]
            nc = [l.strip() for l in efo.split("5b. ROUND 2 (V6-m4)", 1)[1].split("\n\n", 1)[0].splitlines() if "NOT COVERED" in l]
            w("   eFuse %s %s (%s, %s): band %.4f to %.4f A (PRINTED, range-wide); demand %s A under its least: %s; its top under the printed %s A (%s): %s" % (
                k[0], k[1], net, setting, lo, hi, bm.group(2) if bm else "NOT READ", "yes" if bm else "NOT READ",
                cm.group(2) if cm else "?", (cm.group(3)[:46] if cm else "NOT READ"), "yes" if cm else "NOT READ"))
            coord_ok &= bool(bm and cm)
            for l_ in air:
                w("     at the inside air (efuse_check.out 5b, INFERRED): %s" % l_[len("%s %s " % k):][:160])
        w("     NOT COVERED at 76.25 C (INFERRED deratings, the makers print no curve): J_LIME's VBUS contact against the LimeSDR's demand and")
        w("     U23's top, the RockBLOCK's IDC contact and conductor against U24's top: PROVISIONAL on the efuse record's vendor tasks (V6-m4)")
        w("   board P's breaker C-1 (LM5069, record l9stk; C-PROT rev 1): band %.2f to %.2f A; demand the 18 A service (the true %.4f A, section 5)" % (b_lo, b_hi, Q["i_true"]))
        w("     under its least: yes; its top under C-PROT's 23.93 A, every series part within its limits (record l9stk 15.1, CONFIRMED AS")
        w("     CONDITIONAL) and the cells' 24 A: yes; excursions over its least only under the fault timer's least (E-10, the supplier's bench)")
        w("   the PA cap (U553, PROVISIONAL): band %.4f to %.4f A; demand the 30 W service: NOT ESTABLISHED (B-PA1; the maker's 6.0 A is an" % (L["i_min"], L["i_max"]))
        w("     EXAMPLE); its top under the PRINTED ratings downstream: J_PA's VH 10 A yes, U551's 15 A continuous yes; under J_PA's least at")
        w("     76.25 C (%.4f A, INFERRED): NO (L9T5-F26, L8R2-F43's vendor task); under U13's own least loop %.4f A with R55's other loads: yes," % (
            least_th, L["u13_min"]))
        w("     so the cap acts first and U13's loop is the backstop")
        c10 = " ".join(c4.split("10c. ROUND 9", 1)[-1].split())
        tp = need(c10, r"2\.5 V within ([\d.]+) ms at the tolerances \(round 8: [\d.]+ ms\); path 2 within ([\d.]+) ms", "the two paths' trip times (10c)")
        al = need(c10, r"Allowances taken: (\d+) uA cold, (\d+) uA tripped", "the guard's draw allowances (10c)")
        dr = need(c10, r"([\d.]+) uA with the clamp's gates doubled;.*?([\d.]+) uA with one of its resistors shorted", "the guard's draw (10c)")
        two = "no single failure removes the trip" in c10
        w("   the thermal guard on the battery FETs, in its COMPOSED form (record l8p round 9 after cx45 Q5: TWO PATHS sharing only the pour and")
        w("     the loop, path 1 round 8's guard with the cold clamp, path 2 U62 on VBAT through U63 with its own shunt Q61 on DOCK_EN_OUT; drawn by")
        w("     the delta, section 2, read by check_l8p_fs.py, section 3): no trip at 10 A held (%s C, %s K under %s C), at the 18 A service read" % (
            nt.group(1), nt.group(2), nt.group(3)))
        w("     as held (%s C, %s K) and at the gauge's condition C4 (%s C, %s K) on each switch's PRINTED limits (l8p_c4.out 10c (a)); the trip" % (
            nt.group(4), nt.group(5), nt.group(6), nt.group(7)))
        w("     within %s ms on path 1 and %s ms on path 2 (10c (b)), under the RC hold; the author's reading that %s (10c (2), UNCHECKED); the" % (
            tp.group(1), tp.group(2), "no single failure removes the trip" if two else "the common path NOT READ"))
        w("     FETs' 150 C behind it (DD-2 with Q42, condition C3). NOT established: the double failure after a latent first one and the retry")
        w("     heating after the loss of path 1 (L8P-R9-F1; cx46 item 10 %s): the guard row's C-PROT claim reads %s (section 11);" % (
            "NOT CLOSED" if OPEN[10] else "closed", RE if OPEN[10] else "as the rows show"))
        w("     the guard's DOCK_EN_OUT draw at most %s uA cold and %s uA tripped (PRINTED maxima, the worst single fault; the loop's allowances" % (
            dr.group(1), dr.group(2)))
        w("     %s and %s uA hold) against the 30 uA row of Layer 5 and record l9stk 15.9 (L8P-R9-F2;" % (al.group(1), al.group(2)))
        w("     L4-E11 section 28 restates 20c and 20f on them, record l9stk's re-take owed); V6-m7 and the common path CORRECTED IN DRAFT, UNCHECKED")
        P["each protective row states its band against its demand and its downstream printed rating, and names what is not established"] = coord_ok
        sol = text(OUTS["p0sol"])
        e_parts = need(sol, r"gen_netlist: (\d+) parts, 0 unplaced", "record l4e7's board E composition").group(1)
        d16 = "D-16: CORRECTED on the drafted circuit" in sol
        d10 = re.search(r"D-10 \(B6, L4-F01\): an UNRESOLVED PROTECTION DEFECT in the present model", sol) is not None
        b2_not = ("Route B2 (section 5) is UNSELECTED and WITHDRAWN AS DRAFTED, with no protection credit and no owner item; it does not resolve D-10"
                  in " ".join(sol.split()))                  # the solar author's disposition after cx46 item 18 (4d1d02de)
        w("   the solar entry (P0-7, record l4e7, merged at 5cc9cb9d; l4e7_p0sol.out pinned): board E composed here (section 2) and there in")
        w("     L4-E9's order with P0-7's sense, route B2 out of the baseline (record l4e7's C2 composition %s parts); D-16 %s; D-10 an" % (
            e_parts, "CORRECTED in draft" if d16 else "NOT READ"))
        w("     UNRESOLVED PROTECTION DEFECT in the model (%s: PV_F 321.9 V at 0.30 uH on the 2 V bank parts, 83.48 V at the reference loop" % (
            "record l4e7 reads it so, E-1" if d10 else "NOT READ"))
        w("     over the 80 V recommended row), the receiving company's remaining engineering item E-1; route B2 is UNSELECTED and WITHDRAWN AS")
        w("     DRAFTED (%s), out of the baseline, with no protection credit and no owner item; it does not resolve D-10, and its P2/P3" % (
            "record l4e7 reads it so" if b2_not else "NOT READ"))
        w("     defects are remaining engineering outside the baseline; the solar guard's trip against its demand is")
        w("     record l4e7's reading, not re-traced here")
        P["record l4e7's P0-7 is in the candidate: D-16 corrected in draft, D-10 an unresolved protection defect that B2 does not resolve"] = (
            d16 and d10 and b2_not)
        w("")

        # 9. thermal limits
        t10 = text(OUTS["t10"])
        rows22 = [(m.group(1).strip(), m.group(2), int(m.group(3)), float(m.group(4)), m.group(5)) for m in re.finditer(
            r"^     (\S.*?)\s+(V|Y)\s+[\d.]+ A\s+(125|150) C \((?:sustained|transient)\)\s+[\d.]+ C (?:FAILS|holds)\s+([\d.]+) C (holds|FAILS)$",
            t10, re.M)]                                       # (row, revision, criterion C, TJ at 14.0 k, verdict at 14.0 k)
        if not rows22:
            refuse("T10's part 22 rows are not read")
        v14 = [r for r in rows22 if r[1] == "V"]
        y_fail = [r for r in rows22 if r[1] == "Y" and r[4] == "FAILS"]
        f01 = text(OUTS["f01"])
        ina = need(f01, r"junction ([\d.]+) C at 76\.25 C air", "the INA250's junction")
        fet = need(stk, r"the battery FETs at ([\d.]+) C \(the guard ([\d.]+) to ([\d.]+) K above\)", "the battery FETs at the 18 A service")
        w("9. THE THERMAL LIMITS (each at the air its record reads)")
        b14 = [r for r in v14 if r[0].startswith("the bounded state")][0]
        w("   the supervisors' LDOs at R602 14.0 k (T10, Slot C's part 22 rows; section 10's decision): on revision V (fitted, L9T5-D7) the bounded")
        w("     state %.1f C, every row at most %.1f C (MODEL at 76.25 C on average currents, the drop's worst corner): %s against each row's" % (
            b14[3], max(r[3] for r in v14), "every one holds" if all(r[4] == "holds" for r in v14) else "NOT every one holds"))
        w("     criterion on the MODEL; the acceptance reads %s while the sustained peaks and the latent rail trip are open (section 11) (125 C" % (
            RE if (OPEN[6] or OPEN[7]) else "as the rows show"))
        w("     sustained, 150 C transient); rev Y's rows, the cover for a rev X part, at 14.0 k: %s over (%s): revision X stays HELD with no admission route (round 5's V-B20 route SUPERSEDED, 10j (f))" % (
            len(y_fail), "; ".join("%s %.1f C" % (r[0], r[3]) for r in y_fail)))
        P["every revision V T10 row holds its criterion at the taken set point on the MODEL; its acceptance reads REMAINING ENGINEERING while the peaks and the latent rail trip are open"] = (
            all(r[4] == "holds" for r in v14) and (OPEN[6] or OPEN[7]))
        w("   U551 INA250A2 at the cap's top: junction %s C at 76.25 C air (TYPICAL RthJA; l9t5_f01.out)" % ina.group(1))
        w("   R55 (WSL2512 6 mOhm): %.3f W at the cap's top with R55's other loads, %.1f C at 76.25 C air (MODEL, ASSUMPTION %.0f K/W); U13's least" % (
            L["r55_w"], L["r55_t"], PL.R55_RTH))
        w("     limit is taken at that temperature (printed TCR), so the coordination of section 8 carries R55's own heating")
        w("   the battery FETs at the 18 A service: %s C with the guard %s to %s K above (record l9stk; DD-2 with Q42, condition C3)" % fet.group(1, 2, 3))
        w("")

        # 10. the session decision on L9T5-F22, judged with the containment composed (cx45's Q3, Slot C's round 6)
        FC = f22_chain(L9.read(raws["b"]))
        w("10. L9T5-F22, SLOT C'S SET POINT DELTA (R602 14.0 k, apply_gen_sch_?_iocset.py), JUDGED OVER THE CONNECTED CIRCUIT WITH THE")
        w("   CONTAINMENT (Slot C's round 6, composed in section 2; the owner's part 22 item 3) AND SESSION DECISION L9T5-D9")
        w("   each LDO's input = the pre-regulator's least output (VFB's printed band, R601 56.2k and R602 at 0.1 % and 25 ppm/K) less the rail's")
        w("   2 %% copper budget, the lead (three LDOs' current through J_5V_IOC pin 1: %.2f mOhm, hot wire and two contacts), the ground shift" % (FC["r_sup"] * 1e3))
        w("   between the boards (as drawn: the one-node model without the return, record l8r2; with the dedicated return: the distributed STUDY's")
        w("   AVERAGED probe on the service cases, l8r2_dist.out, PROVISIONAL with V6-B1 OPEN, which replaces the one-node 0.0114 V) and its own")
        w("   rail trip's sense resistor")
        w("   (read on the composed board B by topology: %s; taken at %.4f Ohm, its printed tolerance's top);" % (
            ", ".join("%s %s for %s" % (s[1], s[2], s[0]) for s in FC["sense"]), FC["r_s"]))
        w("   against the AP2112K's need (its VOUT maximum, load regulation and dropout); MODEL on PRINTED terms except where marked. The currents:")
        w("   the LDO's printed 600 mA (its rating, not a demand); the bound T10-A3 is judged at since Slot C's round 6, the rail trip's AVERAGE")
        w("   maximum %.4f A (l9t5_t10.out 10j (d): the trip holds a controller's average at %.4f to %.4f A; PROVISIONAL after cx46: a periodic" % (
            FC["i_trip"], FC["win"][0], FC["win"][1]))
        w("   peak above it is not covered, and a latent rail-trip failure removes it); and L9T5-D8's")
        w("   %.4f A (rev Y's held B5 row, SUPERSEDED in round 6; shown for the record)" % FC["i_hold"])
        for r in FC["rows"]:
            w("   R602 %.1f k (least %.4f V, top %.4f V), return %-25s shift %.4f V, %.4f A a LDO (%s; dropout %s): input %.4f V against %.4f V: %s %+.4f V" % (
                r["rb"] / 1e3, r["lo"], r["hi"], r["ret"], r["shift"], r["i"], r["crit"], r["lab"], r["at"], r["need"], "holds" if r["ok"] else "FAILS",
                r["at"] - r["need"]))

        def row_(rb, ret, i):
            return [r for r in FC["rows"] if abs(r["rb"] - rb) < 1 and r["ret"] == ret and abs(r["i"] - i) < 1e-9][0]
        dr, rt = "as drawn", "with the dedicated return"
        t14 = [row_(14.0e3, x, FC["i_trip"]) for x in (dr, rt)]
        s14 = [row_(14.0e3, x, 0.6) for x in (dr, rt)]
        s13 = [row_(13.3e3, x, 0.6) for x in (dr, rt)]
        s138 = [row_(13.8e3, x, 0.6) for x in (dr, rt)]
        h13 = [row_(13.3e3, x, FC["i_hold"]) for x in (dr, rt)]
        h14 = [row_(14.0e3, x, FC["i_hold"]) for x in (dr, rt)]
        same = abs(t14[0]["at"] - FC["a3"][0]) < 5e-5 and abs(t14[0]["need"] - FC["a3"][1]) < 5e-5
        w("   the composed chain against Slot C's 10j (d) at 14.0 k with the return as drawn: input %.4f V against %.4f V (Slot C: %.4f V against" % (
            t14[0]["at"], t14[0]["need"], FC["a3"][0]))
        w("     %.4f V): %s" % (FC["a3"][1], "the same" if same else "DIFFERENT"))
        w("   the headroom's other side: the pre-regulator's top under the AP2112K's %.1f V input maximum at every set point (%s V)" % (
            FC["vin_max"], ", ".join("%.4f" % FC["tops"][rb][2] for rb in sorted(FC["tops"]))))
        w("   the thermal side on revision V, criterion 125 C (a sustained state):")
        w("     without the containment, the babbling supervisor (%.4f A; Slot C's part 22 rows, l9t5_t10.out 10i): %s" % (FC["i_bab"], "; ".join(
            "R602 %.1f k %.1f C (%s) %s" % (rb / 1e3, FC["tj"][rb][0], FC["tj"][rb][1], "holds" if FC["tj"][rb][0] <= 125.0 else "FAILS") for rb in sorted(FC["tj"]))))
        w("     with the containment composed, a constant current at the trip's average maximum %.4f A (10j (e), %.2f C air; a constant-current" % (
            FC["i_trip"], FC["air"]))
        w("     MODEL, not a bound: the trip holds an average):")
        for rb in sorted(FC["tj_trip"]):
            v_, lab = FC["tj_trip"][rb]
            w("       R602 %.1f k: %.1f C (%s): %s, margin %+.1f K" % (rb / 1e3, v_, lab, "holds" if v_ <= 125.0 else "FAILS", 125.0 - v_))
        w("     cx46's periodic countermodel under the trip (0.50 A for 0.40 s every 1.50 s; Slot C's reproduction, 10j (e)) at 14.0 k: %.2f C," % FC["tj_peak"])
        w("     %s 125 C: the sustained thermal bound WITHDRAWN (Slot C), peak-current containment or a periodic electrothermal solution" % (
            "OVER" if FC["tj_peak"] > 125.0 else "under"))
        w("     REMAINING ENGINEERING")
        tt = FC["tj_trip"]
        w("   DECISION L9T5-D9 (SESSION, under the owner's standing rule of 26 September 2026; ruled_by Slot A; ruled_on 5 October 2026;")
        w("   reversed_by: none; its reasons restated on the containment after cx45): Slot C's set point delta (R602 14.0 k) is TAKEN, composed")
        w("   after iocpre on both boards (section 2; a separate draft, one writer a file). Why, over the connected circuit with the containment:")
        w("   at 14.0 k every LDO's input holds its need at the trip's average maximum with the sense resistor's drop, as drawn (%+.4f V)" % (
            t14[0]["at"] - t14[0]["need"]))
        w("   and with the dedicated return (%+.4f V), and the trip's held average leaves the LDO at %.1f C (%+.1f K); at 13.3 k that held current" % (
            t14[1]["at"] - t14[1]["need"], tt[14.0e3][0], 125.0 - tt[14.0e3][0]))
        w("   puts it at %.1f C (INFERRED, %+.1f K: inside the model's own uncertainty, the LDO's 184 C/W with no board copper), and without the" % (
            tt[13.3e3][0], 125.0 - tt[13.3e3][0]))
        w("   containment the babbling row there is %.1f C, a demonstrated defect; the headroom's top %.4f V stays under the LDO's input maximum." % (
            FC["tj"][13.3e3][0], FC["tops"][14.0e3][2]))
        w("   The ranking stands on any thermal model (the LDO's dissipation falls with its input at every current); the bounds themselves are")
        w("   %s after cx46 (the sustained peaks, item 7; the latent rail trip, item 6; section 11)" % (RE if (OPEN[6] or OPEN[7]) else "as shown"))
        w("   What it costs: with the sense resistor in the path, T10-A3 at the LDO's printed 600 mA fails at every set point (13.3 k %+.4f V," % (
            s13[0]["at"] - s13[0]["need"]))
        w("   %+.4f V; 14.0 k %+.4f V, %+.4f V): 600 mA is the regulator's rating, not a demand; L9T5-D8's superseded %.4f A (rev Y's held B5" % (
            s13[1]["at"] - s13[1]["need"], s14[0]["at"] - s14[0]["need"], s14[1]["at"] - s14[1]["need"], FC["i_hold"]))
        w("   row, the cover for the held revision X) holds at 13.3 k (%+.4f V, %+.4f V) and not at 14.0 k (%+.4f V, %+.4f V): no fitted state" % (
            h13[0]["at"] - h13[0]["need"], h13[1]["at"] - h13[1]["need"], h14[0]["at"] - h14[0]["need"], h14[1]["at"] - h14[1]["need"]))
        w("   reaches it, because a revision X part must stay under the trip's least %.4f A in its bounded state (V-B20, 10j (f)), and a draw over" % FC["win"][0])
        w("   the hardware bound is a fault the trip ends while the other two hold the quorum (Slot C's round 6 restatement, which supersedes")
        w("   SESSION L9T5-D8)")
        w("   ADAPTATION REJECTED: R602 13.8 k was to keep the 600 mA row; with the sense resistor that row fails there too (%+.4f V as drawn," % (
            s138[0]["at"] - s138[0]["need"]))
        w("   %+.4f V with the dedicated return), so 13.8 k only gives up thermal margin (the trip's held maximum at %.1f C, INFERRED)" % (
            s138[1]["at"] - s138[1]["need"], tt[13.8e3][0]))
        w("   PROVISIONAL (amendment 1): the dropout at the hardware bound %.4f A is INFERRED between the printed 10 and 300 mA points (%.0f mV):" % (
            FC["i_trip"], drop_mv(FC)))
        w("   the supplier's validation task V-T10-DROP, restated on the hardware bound: three AP2112K-3.3 specimens of the fitted lot, dropout at")
        w("   %.4f A and TJ 125 C at most %.0f mV (or Diodes' printed statement)" % (FC["i_trip"], drop_mv(FC)))
        w("   L9T5-D7 (revision V fitted) STAYS a constraint, not a fallback: with the containment rev Y's bounded state is over the trip's least")
        w("   current, so revision X stays HELD on V-B20 (Slot C, 10j (f));")
        w("   check_l9t5_netlist.py reads the composed design in its t10s mode (R602 14.0 k; the band 3.87 to 4.18 V, its floor from the superseded")
        w("   L9T5-D8 row as drawn without the sense resistor, stricter than the hardware bound's, kept) and its guard mode (each LDO behind one")
        w("   sense resistor, L9T5-F25 restated)")
        r5 = text("v2/docs/records/l9t5/T10-ROUND5.md")
        renamed = re.search(r"^\| L9T5-D10 \(round 6; renamed from D9, L9T5-F27", r5, re.M) is not None and not re.search(r"^\| L9T5-D9 \(round 6\)", r5, re.M)
        w("   FINDING L9T5-F27 (an identifier, no circuit): Slot C's T10-ROUND5.md section 12 had named its containment decision \"L9T5-D9")
        w("   (round 6)\", the identifier of this SESSION decision on the set point (taken at 06077cee): %s; in this record L9T5-D9 is the set point" % (
            "ANSWERED, Slot C renamed it L9T5-D10 (6b768b1e)" if renamed else "OPEN, the containment's writer renames it"))
        w("   THE FINAL FIGURES ON THE COMPLETE CANDIDATE (the owner's part 23 item 1; R602 14.0 k and the containment composed, section 2): each")
        w("   regulator's temperature against 125 C per served state on revision V (Slot C's MODEL at %.2f C air and the drop's worst corner," % FC["air"])
        w("   10j (e), the limiters' pull-ups counted, AVERAGE currents) and the trip's held average; after cx46 an average bound does not bound a")
        w("   periodic peak (item 7) and a latent rail-trip failure removes it (item 6): every row below is a MODEL reading, PROVISIONAL/OPEN:")
        for lab, i_, t_ in FC["serve"]:
            w("     %-46s %.4f A  sustained  criterion 125 C: %5.1f C (margin %+5.1f K)" % (lab, i_, t_, 125.0 - t_))
        w("     %-46s %.4f A  sustained  criterion 125 C: %5.1f C (margin %+5.1f K)" % ("a constant current at the trip's average maximum", FC["i_trip"],
                                                                                    tt[14.0e3][0], 125.0 - tt[14.0e3][0]))
        w("     %-46s           periodic   criterion 125 C: %6.2f C (margin %+5.1f K)" % ("cx46's countermodel under the trip", FC["tj_peak"], 125.0 - FC["tj_peak"]))
        sv_max = max(t_ for _l, _i, t_ in FC["serve"])
        w("   RESULT, R602 14.0 k on the complete candidate (MODEL; the acceptance %s, section 11): on revision V %+.1f K at a" % (
            RE if (OPEN[6] or OPEN[7]) else "as shown", 125.0 - tt[14.0e3][0]))
        w("     constant current at the trip's average maximum, %+.1f K under cx46's periodic countermodel (the largest served state %+.1f K);" % (
            125.0 - FC["tj_peak"], 125.0 - sv_max))
        w("     rev Y's rows no longer cover a revision X part (its bounded state over the trip's least; HELD on V-B20); the LDO input headroom of T10-A3's chain at the hardware bound %+.4f V with the return as drawn and %+.4f V with the" % (
            t14[0]["at"] - t14[0]["need"], t14[1]["at"] - t14[1]["need"]))
        w("     dedicated return (the return's effect %+.4f V), the top %.4f V under the LDO's %.1f V maximum; the required service unchanged (only" % (
            (t14[1]["at"] - t14[1]["need"]) - (t14[0]["at"] - t14[0]["need"]), FC["tops"][14.0e3][2], FC["vin_max"]))
        w("     U601's set point moves and board B gains the containment: no load, rate, state or transmitter reduced, the supervisors' bounded")
        wc_state = "PROVISIONAL/OPEN" if (OPEN[6] or OPEN[7] or FC["tj_peak"] > 125.0) else "PROVISIONAL"
        w("     state and C-DEV rev 2 as issued). THE WORST-CASE MARGIN ROW: %s (no peak bound established, cx46 item 7; a latent rail-trip" % wc_state)
        w("     failure removes the hardware bound, item 6): %+.1f K at a constant current at the trip's average maximum (rev V, MODEL), %+.1f K" % (
            125.0 - tt[14.0e3][0], 125.0 - FC["tj_peak"]))
        w("     under cx46's periodic countermodel, and %+.4f V (the LDO's" % (t14[0]["at"] - t14[0]["need"]))
        w("     input, as drawn, at the hardware bound on an INFERRED dropout, PROVISIONAL on V-T10-DROP)")
        P["the final R602 figures keep a positive MODEL margin on average currents; the worst-case margin row reads PROVISIONAL/OPEN while the peaks or the latent rail trip are open"] = (
            sv_max < 125.0 and tt[14.0e3][0] < 125.0 and wc_state == ("PROVISIONAL/OPEN" if (OPEN[6] or OPEN[7] or FC["tj_peak"] > 125.0) else "PROVISIONAL"))
        P["L9T5-F27 answered: Slot C's containment decision is L9T5-D10 and L9T5-D9 is this record's set point"] = renamed
        P["L9T5-F22 judged over the connected circuit with the containment: 14.0 k holds T10-A3 at the hardware bound on either return (MODEL), Slot C's figure reproduced"] = (
            all(r["ok"] for r in t14) and same and tt[14.0e3][0] <= 125.0 < FC["tj"][13.3e3][0] and FC["bab_ok"])
        w("")

        # 11. what stays open on this candidate
        any_open = any(r[4] for r in FR)
        verdict = RE if any_open else "THE DESK ROWS AS SHOWN (no independent acceptance)"
        w("11. THE CONNECTED VERDICT AND WHAT THIS CANDIDATE DOES NOT CLOSE (cx46 items 13 and 17; constitution section 2)")
        w("   the fault rows the connected verdict depends on, each with the cx46 item that holds it (the filed record, %s, read as JSON;" % cx46_base)
        w("   a row is OPEN while its item is NOT CLOSED: the method ended at cx46, so no later check closes it):")
        for row, item, cl, aff, op in FR:
            w("     %-4s %s" % ("OPEN" if op else "SHUT", row))
            w("          cx46 item %d: %s; it removes or weakens: %s" % (item, cl, aff))
        w("   THE CONNECTED ELECTRICAL VERDICT: %s. No row of sections 5 to 10 is a positive electrical acceptance: each is a MODEL" % verdict)
        w("     reading on the composed candidate, and every claim that depends on an OPEN row above (the guard's C-PROT row, T10's thermal")
        w("     and headroom rows, the CAN service, the return's rows, the PA cap's band) stays OPEN or PROVISIONAL and passes to the receiving")
        w("     company as remaining engineering with its failed cases, the attempted correction and the affected outputs (never as a")
        w("     qualification-only item)")
        P["the connected electrical verdict reads REMAINING ENGINEERING, never a positive acceptance, while any fault row it depends on is open (cx46 items 13, 17)"] = (
            (verdict == RE) == any_open and len(FR) == len(FAULT_ROWS))
        w("   F01 / D-17: PROVISIONAL (B-PA1 the 30 W service under the cap's least; B-PA2 the loop's dynamics with E-10); L9P-F04 with it; the")
        w("     reference's loading through Q551's hold and release and the acceptance limits REMAINING ENGINEERING (cx46 item 2)")
        w("   the return: V6-B1 OPEN, REMAINING ENGINEERING (7; the distributed study on a stand-in land, assumed sites and fill, an averaged")
        w("     probe); the declared upper bound's INFERRED least rows OPEN on vendor curves (L8R2-F43, L8R2-F44); V6-B2 vendor tasks (Hirose")
        w("     U.FL, Molex HDMI) UNSENT")
        w("   the protection rows NOT established (8): the eFuses' downstream contacts at the inside air (V6-m4), the PA cap's demand (B-PA1) and")
        w("     J_PA at the inside air (L9T5-F26), the guard's double failure and its draw (L8P-R9-F1, L8P-R9-F2; Slot C's); the CAN")
        w("     service for a TX pin toggled as a GPIO and after a latent stuck comparator (5; L9T5-F21, handed over, Slot C's)")
        w("   the reference at its actual load (V-PA-REF, l9t5_f01.out 6) beside B-PA1 and B-PA2")
        w("   T10: L9T5-F06 OPEN pending its independent check; revision X HELD with no admission route (round 5's V-B20 route SUPERSEDED, 10j (f));")
        w("     the containment (Slot C's round 6, composed here) drafted, composed, read by pin and mutated, cx45's Q3 NOT CLOSED (10j, after cx46);")
        w("     its qualification limits (the LDO's resistance and Zth on board B) and the VOS0 residual handed over (10j (e)); L9T5-F27, the decision identifier both records use (10)")
        w("   the guard's two paths (record l8p round 9, composed): the loop's DOCK_EN_OUT allowance against the 30 uA row (L8P-R9-F2: L4-E11")
        w("     section 28 restated, record l9stk 15.9's re-take owed); the double failure after a latent first one (L8P-R9-F1, handed over);")
        w("     check_l8p_netlist.py's round 8 reader does not admit the delta (L8P-R9-F3): the composed board A is read by check_l8p_fs.py (3)")
        w("   VH derating (J_PA, J_5V_DEV): L8R2-F43, JST's curve MISSING; finding L9T5-F26 (Layer 7, Layer 6): J_PA carries up to the cap's top,")
        w("     over the VH's least rating at 76.25 C as record l8r2 infers it; if JST's curve is lower at the PA lead's local air, J_PA becomes")
        w("     a 1x4 VH with two contacts a pole (a harness row and a board A land)")
        w("   the solar entry (P0-7): D-10 an UNRESOLVED PROTECTION DEFECT in the model (E-1, the receiving company's remaining engineering item); route")
        w("     B2 UNSELECTED and WITHDRAWN AS DRAFTED, out of the baseline, no protection credit and no owner item; it does not close D-10")
        w("   L4-E9's change-list rows: drafted here (apply_l4e9_changelist_p0.py), APPLIED by the integrator at set 30's integration commit 7070f106 to L4-E9's")
        w("     register, script and page; applying them accepts no draft (cx46: CORRECTIONS NOT CLOSED; the claims read OPEN or PROVISIONAL as above); L4-E9's generator re-pinned at 2a (bbba3e53), its output regenerated in set 31 with its four cascade pins (l4e10, l4e11, l4e12, L4-E7's P0) at commit 2b's digests, refusing at those pins on a tree without them")
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
