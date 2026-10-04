#!/usr/bin/env python3
"""l8r2_gndret.py: Layer 8 record l8r2, round 7 (task T5b, the owner's review of 4 October 2026, RSM-01): board B's ground return, its
load basis and its current capacity reconciled (MESHSAT-1357). PROTOTYPE DESIGN: nothing in this kit has been built, bought,
powered or measured, nothing is applied to the tree, and no figure printed here is a measurement.

It prints, deterministically and without touching the tree:
  0. the inputs, each pinned by sha256;
  1. THE REPRODUCTION: board B's pending drafts applied one by one in L4-E9's change-list order on a scratch copy, first without and
     then with Layer 9's I-03 draft (the copy in inputs/); after each, what the generator hands intent.rail for GND (recorded before
     intent judges it), the sum, the move load by load, and whether the generator runs or stops, in intent's own words;
  2. THE LOAD BASIS: what _GND_LOADS sums and whether that is the return current (the union of the leads' allocations, what is
     named twice, what is missing); the three figures the declaration could hold: (i) the sum of the leads' declared peaks, an
     UPPER BOUND, (ii) the largest state of Layer 9's budget, (iii) what board A's stages can deliver; which one it holds and why;
  3. THE CAPACITY BASIS: every ground conductor between boards A and B read on both netlists; the makers' printed figures; the
     division of the return between them by resistance over the contact resistances the makers bound; each conductor against its
     printed rating at L4-E12's inside air; the supply pins; board B's and board A's ground copper where the leads enter by
     decision 35's function; Layer 5's contract rows;
  4. THE JUDGMENT;
  5. THE CORRECTION: the two drafts on scratch copies (checked, applied once, refused twice, refused on the tree), the composition
     in every order with Layer 9's draft and Layer 6's, the regenerated netlist read by check_gndret_netlist.py, and the mutations,
     each of which must stop the generator or fail the check;
  6. what Layer 9's author and the independent recheck need: the return each connector carries on C-DEV rev 1;
  7. findings; 8. the predicates test_l8r2.py holds.
Labels: PRINTED a maker's limit in a held sheet; TYPICAL a maker's typical figure; DECLARED a generator's or a record's declaration;
MODEL this record's arithmetic on labelled inputs; ASSUMPTION a figure no held document gives; BOUND a limit computed on the
makers' printed extremes, named as such and never taken as the circuit's behaviour.
Run from the repository root:  python3 v2/docs/records/l8r2/l8r2_gndret.py  (l8r2_gndret.out is its output, regenerated with
_bin/regen_out.py). Stdlib, PyYAML and pdftotext; a few seconds."""
import ast
import hashlib
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
sys.path.insert(0, TOOLS)
import check_gndret_netlist as CK  # noqa: E402
import gen_netlist as GN  # noqa: E402
import l8r2_drafts as R6  # noqa: E402  (rounds 1 to 6: the LM5176's VSNS and the ISNS shunt, with their classes)
import track_current as TC  # noqa: E402  (decision 35's function)
import yaml  # noqa: E402

GEN_B = "v2/ecad/tools/gen_sch_b.py"
NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
NET_B = "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"
INT_B = "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json"
L4E9_PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
BUDGET = "v2/docs/records/l9pwr/l9pwr_budget.out"
BUDGET_L9T5 = "v2/docs/records/l8r2/inputs/l9pwr_budget-f70d3085.txt"
L9T5_OUT = "v2/docs/records/l8r2/inputs/l9t5_drafts-f70d3085.txt"
L9T5_DRAFT = "v2/docs/records/l8r2/inputs/l9t5-apply_gen_sch_b_iocbuck-f70d3085.py"
CASES = "v2/docs/records/l8r2/inputs/coordinator-cases-2026-10-04-rev3.md"
L4E12_OUT = "v2/docs/records/l4e12/l4e12_thermal.out"
L9STK_PAGE = "v2/docs/records/l9stk/L9-STACKUPS.md"
ASSEMBLY = "v2/docs/ASSEMBLY.md"
IFACES = "v2/ecad/tools/pcb_interfaces.yaml"
DC_DROP = "v2/ecad/tools/dc_drop.py"
GEN_A = "v2/ecad/tools/gen_sch_a.py"
PACKRTN = "v2/docs/records/l8r2/apply_gen_sch_a_packrtn.py"
SHEETS = {"vh": "v2/vendor/connectors/jst-vh-catalogue.pdf", "cab": "v2/vendor/connectors/wurth-wr-cab-ribbon-63912615521cab.pdf",
          "sock": "v2/vendor/connectors/wurth-wr-bhd-idc-socket-61202623021.pdf", "hdr": "v2/vendor/connectors/wurth-wr-bhd-box-header-61202621621.pdf"}
MINE = {"gndret": "v2/docs/records/l8r2/apply_gen_sch_b_gndret.py", "fandec": "v2/docs/records/l8r2/apply_gen_sch_b_fandec.py"}
DRAFT = {"gnd002": "v2/docs/records/l8gnd/apply_gen_sch_b_gnd002.py", "fans12": "v2/docs/records/l8r2/apply_gen_sch_b_fans12.py",
         "panel5v": "v2/docs/records/l8r2/apply_gen_sch_b_panel5v.py", "ph4": "v2/docs/records/l8r2/apply_gen_sch_b_ph4.py",
         "rt500": "v2/docs/records/l8r2/apply_gen_sch_b_rt500.py", "iocbuck": L9T5_DRAFT,
         "xal_land": "v2/docs/records/l6r2/apply_gen_sch_b_xal_land.py", "lcsc": "v2/docs/records/l6r2/apply_gen_sch_b_lcsc.py",
         "intent": "v2/docs/records/l6r2/apply_gen_sch_b_intent.py", **MINE}
L6_HELP = ["v2/docs/records/l6r2/l6r2_apply.py", "v2/docs/records/l6r2/l6r2_land.py", "v2/docs/records/l6r2/l6r2_intent.py"]
ENGINE = ["v2/ecad/tools/kisch.py", "v2/ecad/tools/intent.py", "v2/ecad/tools/idc_pads.py", "v2/ecad/tools/track_current.py", DC_DROP,
          "v2/docs/records/l8p/gen_netlist.py", "v2/docs/records/l8r2/check_l8r2_netlist.py", "v2/docs/records/l8r2/check_gndret_netlist.py",
          "v2/docs/records/l8r2/l8r2_drafts.py"]
# the record's own order of board B's round (rounds 1 to 6, l8r2_drafts.py L8_B, and record l9t5's ORDER): the change list's three rows
# with this record's panel5v and ph4 (Layer 5's findings, no change-list row) between them; Layer 9's draft after the circuit
# drafts; Layer 6's land, table and declarations last
ROUND = ["gnd002", "fans12", "panel5v", "ph4", "rt500"]
L6 = ["xal_land", "lcsc", "intent"]
# the session's choices (authority: SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
T_RATED_RISE = 30.0     # K, ASSUMPTION: the temperature rise at the rated current that JST's 10 A stands for; the held catalogue prints none
CU_ALPHA = 0.00393      # 1/K, ASSUMPTION (ideal copper, as records cx1 and l4e11 take it; no held source)
IOC_AWG = 16            # ASSUMPTION: record l9t5's draft names no gauge for J_5V_IOC's lead; taken as the four 5 V leads'
AB2_MM = None           # J_AB2's ribbon length is TBD in its contract (IF-AB-WALL); taken as J_AB1's, ASSUMPTION


def rel(p):
    return os.path.relpath(p, ROOT)


def P(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(P(p), "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l8r2_gndret: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def text(p):
    return open(P(p), encoding="utf-8").read()


_PDF = {}


def pdf(key):
    if key not in _PDF:
        try:
            r = subprocess.run(["pdftotext", "-layout", P(SHEETS[key]), "-"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            refuse("pdftotext could not read %s (%s)" % (SHEETS[key], e))
        _PDF[key] = r.stdout.decode("utf-8", "replace")
    return _PDF[key]


# ------------------------------------------------------------------------------------------------ the makers' and the tree's figures
def figures():
    F = {}
    t = pdf("vh")
    F["vh_a16"] = float(need(t, r"Current rating: (\d+) A\s+AC/DC\s*\n[^\n]*When using AWG #16 with the standard type header", "JST VH's 10 A row").group(1))
    F["vh_a18"] = float(need(t, r"\n\s*(\d+)\s?A\s+AC/DC\s*\n(?:[^\n]*\n){0,4}[^\n]*When using AWG #18 with the shrouded type header", "JST VH's 7 A row").group(1))
    m = need(t, r"Temperature range: \S?(\d+)\S+ to \+(\d+)", "JST VH's temperature range")
    F["vh_tmax"] = float(m.group(2))
    need(t, r"\(including temperature rise in\s+applying electrical current\)", "JST VH's range includes the rise", re.S)
    F["vh_rc0"] = float(need(t, r"Contact resistance: Initial value/ (\d+) m\S+ max", "JST VH's initial contact resistance").group(1))
    F["vh_rc1"] = float(need(t, r"After test/ (\d+) m\S+ max", "JST VH's contact resistance after test").group(1))
    F["vh_note"] = bool(need(" ".join(t.split()), r"Note: Do not branch in parallel current which exceeds the rated current\. .*?If branched in parallel, "
                             r"current imbalance or other problems may occur\. .*?design the circuits without causing any imbalance and provide extra "
                             r"margin for each circuit\.", "JST VH's note on parallel branching"))
    F["mm2_16"] = float(need(t, r"SVH-41T-P1\.1\s+#20 to #16 \(0\.5 to ([\d.]+)\)", "JST's AWG 16 section").group(1))
    F["mm2_18"] = float(need(t, r"SVH-21T-P1\.1\s+#22 to #18 \(0\.33 to ([\d.]+)\)", "JST's AWG 18 section").group(1))
    t = pdf("cab")
    F["cab_a"] = float(need(t, r"Rated Current\s+IR\s+(\d+)\s+A\s+max", "the ribbon's rated current").group(1))
    F["cab_ohm_km"] = float(need(t, r"Conductor Resistance\s+R\s+1 Kilometer\s+(\d+)\s+\S+\s+max", "the ribbon's conductor resistance").group(1))
    F["cab_awg"] = int(need(t, r"Stranded Wire Section \(AWG\)\s+(\d+) \(AWG\)", "the ribbon's gauge").group(1))
    need(t, r"\(@ 25°C\)", "the ribbon sheet's 25 C rating condition")
    need(t, r"current rating may decrease due to the derating effect at higher temperatures", "the ribbon sheet's derating sentence")
    t = pdf("sock")
    F["sock_a"] = float(need(t, r"Rated Current\s+IR\s+(\d+)\s+A\s+max", "the IDC socket's rated current").group(1))
    F["sock_rc"] = float(need(t, r"Contact Resistance\s+R\s+(\d+)\s+m\S+\s+max", "the IDC socket's contact resistance").group(1))
    t = pdf("hdr")
    F["hdr_a"] = float(need(t, r"Rated Current\s+IR\s+@ 25 °C\s+(\d+)\s+A\s+max", "the box header's rated current").group(1))
    # the tree's copper resistivity, parsed from dc_drop.py (never typed here)
    rho = [n for n in ast.walk(ast.parse(text(DC_DROP))) if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "RHO"]
    if len(rho) != 1:
        refuse("dc_drop.py no longer assigns one RHO")
    F["rho"] = float(ast.literal_eval(rho[0].value))
    # the harness (ASSEMBLY.md section 4)
    a = text(ASSEMBLY)
    m = need(a, r"^\| Slot rails, 3 x .*?\| A22 `J_5V_S1\.\.3` \(VH\) \| B16 `J_5V_S1\.\.3` \(VH\) \| (\d+) AWG, (\d+) mm \|", "the slot leads' row")
    F["slot_awg"], F["lead_mm"] = int(m.group(1)), float(m.group(2))
    m = need(a, r"^\| Device rail .*?\| A22 `J_5V_DEV` \(VH\) \| B16 `J_5V_DEV` \(VH\) \| (\d+) AWG, (\d+) mm \|", "the device lead's row")
    F["dev_awg"], dev_mm = int(m.group(1)), float(m.group(2))
    m = need(a, r"^\| PoE feed \(54 V\) \| A22 `J_54V` \(VH\) \| B16 `J_54V` \(VH\) \| (\d+) AWG, (\d+) mm \|", "the PoE lead's row")
    F["poe_awg"], poe_mm = int(m.group(1)), float(m.group(2))
    if not (dev_mm == poe_mm == F["lead_mm"]):
        refuse("the three lead rows no longer give one length")
    F["ab1_mm"] = float(need(a, r"^\| A to B ribbon \| A22 `J_AB1` \(top\) \| B16 `J_AB1` .*?\| 26-way 1\.27 ribbon, (\d+) mm", "J_AB1's ribbon row").group(1))
    # L4-E12's inside air
    m = need(text(L4E12_OUT), r"E3-O ([\d.]+) C, E5's dwell ([\d.]+) C \(steady", "L4-E12's mixed inside air")
    F["t_e3o"], F["t_e5"] = float(m.group(1)), float(m.group(2))
    # Layer 9's stackup for board B (ground planes and inner weight) and board A
    s = text(L9STK_PAGE)
    m = need(s, r"^\| B compute, [^|]*\| 8, (\S+), [^|]*\| ((?:[SGP] ){7}[SGP]) \(In4 the four 5 V domains\) \| 1 oz / ([\d.]+) oz \|", "board B's stackup row")
    F["b_stack"], F["b_use"], F["b_inner_oz"] = m.group(1), m.group(2), float(m.group(3))
    F["b_gnd_planes"] = m.group(2).split().count("G")
    m = need(s, r"^\| A power and I/O, [^|]*\| 6, \S+, [^|]*\| (F sig and bands, In1 GND, In2 sig, In3 sig, In4 GND, B sig and bands) \| 1 oz / ([\d.]+) oz \|", "board A's stackup row")
    F["a_gnd_planes"], F["a_inner_oz"] = m.group(1).count("GND"), float(m.group(2))
    # the LM5176 5.1 V stages' average loop (rounds 1 to 6 of this record carry the maker's VSNS and the shunt)
    vs, (rs, tol) = R6.V["vsns"], R6.V["isns_r"]
    F["loop_min"], F["loop_max"] = vs[0] / (rs * (1 + tol)), vs[2] / (rs * (1 - tol))
    # record l9t5's output (the copy): the device rail and U601 on C-DEV rev 1
    o = text(L9T5_OUT)
    F["cdev_u7"] = float(need(o, r"\(1\) U7, the device rail, on the case: ([\d.]+) A \(MODEL", "record l9t5's U7 on the case").group(1))
    F["cdev_u7_before"] = float(need(o, r"\(before: ([\d.]+) A,", "record l9t5's U7 before").group(1))
    F["cdev_u601"] = float(need(o, r"\(2\) U601 on the case: ([\d.]+) A \(MODEL", "record l9t5's U601 on the case").group(1))
    F["l9_loop_max"] = float(need(o, r"the loop's highest ([\d.]+) A stays under J_5V_DEV's VH 10 A", "record l9t5's loop maximum").group(1))
    m = need(o, r"high-side limit [\d.]+ / [\d.]+ / ([\d.]+) A, low-side [\d.]+ / [\d.]+ / ([\d.]+) A \(PRINTED\)", "record l9t5's U601 limits")
    F["u601_hs"], F["u601_ls"] = float(m.group(1)), float(m.group(2))
    F["u601_out"] = float(need(o, r"the output at most about \([\d.]+ \+ [\d.]+\) / 2 = ([\d.]+) A", "record l9t5's U601 output bound").group(1))
    # the case rows
    c = text(CASES)
    need(c, r"^## C-DEV rev 1\n.*?the device rail U7 at the least load voltage: 7\.472 A demanded \(4\.9019 V", "C-DEV rev 1", re.M | re.S)
    need(c, r"^## C-ALLTX rev 3 ", "C-ALLTX rev 3")
    return F


def budget(path):
    """{state: {stage: dict(plan, high, least, start)}} from section 5b of Layer 9's budget."""
    t = text(path)
    blk = need(t, r"^5b\. THE LM5176 5\.1 V STAGES SIDE BY SIDE.*?^6\. THE PACK CURRENT", "the budget's section 5b", re.M | re.S).group(0)
    out, st = {}, None
    for line in blk.splitlines():
        m = re.match(r"\s+== (.+)$", line)
        if m:
            st = m.group(1).strip(); out[st] = {}
            continue
        m = re.match(r"\s+(S\d|DEV)\s+LM5176 (U\d+), average loop on \d+ mOhm\s+([\d.]+) A\s+PLAN\s+([\d.]+)\s+HIGH\s+([\d.]+) \([+-][\d.]+\)\s+least V\s+([\d.]+) \([+-][\d.]+\)"
                     r"(?:\s+start\s+([\d.]+) \([+-][\d.]+\))?", line)
        if m and st:
            out[st][m.group(1)] = dict(part=m.group(2), limit=float(m.group(3)), plan=float(m.group(4)), high=float(m.group(5)),
                                       least=float(m.group(6)), start=float(m.group(7)) if m.group(7) else None)
    if not out or any(not v for v in out.values()):
        refuse("the budget's section 5b no longer parses")
    return out


def change_list_b():
    """board B's rows of L4-E9's change list in application order: [(step, register row, apply script or None)]"""
    rows = re.findall(r"^\| (\d+) \| B \| (R-\d+) \| board B, gen_sch_b\.py \| ([^|]+) \|", text(L4E9_PAGE), re.M)
    if not rows:
        refuse("L4-E9's change list carries no board B row")
    return [(int(n), r, s.strip() if s.strip().startswith("apply_") else None) for n, r, s in rows]


# ------------------------------------------------------------------------------------------------ running a generator
RUNNER = '''import importlib.util, json, os, runpy, sys
_here = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("schlayout", os.path.join(_here, "l8p_stub_schlayout.py"))
_m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m); sys.modules["schlayout"] = _m
import intent as _it
_calls = []; _real = _it.rail
def _rec(net, volts, amps_typ, amps_peak, source, loads=None, **kw):
    _calls.append(dict(net=net, typ=amps_typ, peak=amps_peak, source=source, loads=dict(loads or {}),
                       child=bool(kw.get("fed_from") or kw.get("series_of") or kw.get("returns"))))
    return _real(net, volts, amps_typ, amps_peak, source, loads=loads, **kw)
_it.rail = _rec
sys.argv = sys.argv[1:]
_stop = None
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
except SystemExit as e:
    _stop = e.code if isinstance(e.code, str) else (None if e.code in (0, None) else "exit %s" % e.code)
json.dump(dict(calls=_calls, stop=_stop), open(os.environ["L8R2_DECL_JSON"], "w", encoding="utf-8"))
sys.exit(1 if _stop else 0)
'''


def run_gen(gen):
    """One run of a generator copy as record l8p's gen_netlist.py runs it (its stand-in layout, the tree's kisch and intent), with
    every intent.rail call recorded BEFORE intent judges it: dict(stop, calls, table, netlist)."""
    with tempfile.TemporaryDirectory(prefix="l8r2_gnd_") as d:
        g = os.path.join(d, "gen_sch_b.py"); shutil.copy(gen, g)
        open(os.path.join(d, "l8p_stub_schlayout.py"), "w", encoding="utf-8").write(GN.STUB)
        open(os.path.join(d, "run.py"), "w", encoding="utf-8").write(RUNNER)
        js, dj = os.path.join(d, "parts.json"), os.path.join(d, "decl.json")
        env = dict(os.environ, PYTHONPATH=TOOLS, L8P_PARTS_JSON=js, L8R2_DECL_JSON=dj, KICAD_SYMBOLS=os.path.join(d, "no-kicad-symbols"),
                   PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, "-B", os.path.join(d, "run.py"), g, os.path.join(d, "pcb-b-compute.kicad_sch"), "pcb-b-compute"],
                           capture_output=True, cwd=d, env=env)
        if not os.path.isfile(dj):
            refuse("a generator run died before its record was written: %s" % (r.stderr.decode("utf-8", "replace").strip().splitlines() or ["?"])[-1][:300])
        dec = json.load(open(dj, encoding="utf-8"))
        res = dict(stop=dec["stop"], calls=dec["calls"], table=None, netlist=None, intent=None)
        ij = os.path.join(d, "out", "pcb-b-compute-intent.json")
        if dec["stop"] is None and os.path.isfile(js) and os.path.isfile(ij):
            res["table"] = json.load(open(js, encoding="utf-8"))
            res["intent"] = json.load(open(ij, encoding="utf-8"))
            res["netlist"] = GN.netlist(res["table"]).encode("utf-8")
    return res


def apply(name, target, flag="--write"):
    r = subprocess.run([sys.executable, "-B", P(DRAFT[name]), target, flag], capture_output=True)
    last = (r.stderr.decode("utf-8", "replace").strip().splitlines() or r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    return r.returncode, last


def compose(seq, d, tag):
    p = os.path.join(d, tag + ".py"); shutil.copy(P(GEN_B), p)
    for s in seq:
        rc, msg = apply(s, p)
        if rc:
            return p, "%s REFUSED (%s)" % (s, msg)
    return p, None


def call_of(res, net):
    c = [x for x in res["calls"] if x["net"] == net]
    return c[-1] if c else None


def short(msg, n=230):
    msg = " ".join(str(msg).split())
    return msg if len(msg) <= n else msg[:n - 3] + "..."


# ------------------------------------------------------------------------------------------------ the capacity model
def r_wire(mm2, mm, T, F):
    return F["rho"] * (mm / 1000.0) / (mm2 * 1e-6) * (1 + CU_ALPHA * (T - 20.0)) * 1e3            # mOhm


def r_ribbon(mm, T, F):
    return F["cab_ohm_km"] * (mm / 1000.0) * (1 + CU_ALPHA * (T - 20.0))                          # mOhm (Ohm/km x m = mOhm), the maker's maximum at 20 C


def conductors(F, T, ioc):
    """[(name, kind, n conductors, wire mOhm each)]: the ground conductors between boards A and B (section 3a's census)."""
    mm2 = {16: F["mm2_16"], 18: F["mm2_18"]}
    c = [("J_5V_S%d" % s, "VH", 1, r_wire(mm2[F["slot_awg"]], F["lead_mm"], T, F)) for s in (1, 2, 3)]
    c.append(("J_5V_DEV", "VH", 1, r_wire(mm2[F["dev_awg"]], F["lead_mm"], T, F)))
    if ioc:
        c.append(("J_5V_IOC", "VH", 1, r_wire(mm2[IOC_AWG], F["lead_mm"], T, F)))
    c.append(("J_54V", "VH18", 1, r_wire(mm2[F["poe_awg"]], F["lead_mm"], T, F)))
    c.append(("J_AB1", "RIB", 9, r_ribbon(F["ab1_mm"], T, F)))
    c.append(("J_AB2", "RIB", 8, r_ribbon(F["ab1_mm"] if AB2_MM is None else AB2_MM, T, F)))
    return c


def split(total, conds, rc):
    """the return divided by conductance: {name: amps per conductor}, and the return's own drop in mV. rc(name, kind) is the contact
    resistance at EACH end of that conductor, mOhm."""
    g = {n: k / (w + 2.0 * rc(n, kind)) for n, kind, k, w in conds}
    G = sum(g.values())
    return {n: total * g[n] / G / k for n, _kind, k, _w in conds}, total / G


def cases(F):
    v0, v1, i1 = F["vh_rc0"], F["vh_rc1"], F["sock_rc"]
    vh = lambda kind: kind in ("VH", "VH18")
    return [
        ("K0 every contact 0 mOhm (the leads and conductors alone)", "MODEL", lambda n, k: 0.0),
        ("K1 every contact at its printed initial maximum (VH %.0f, IDC %.0f mOhm)" % (v0, i1), "MODEL on PRINTED maxima", lambda n, k: v0 if vh(k) else i1),
        ("K2 VH at the printed after-test maximum %.0f mOhm, IDC %.0f mOhm" % (v1, i1), "MODEL on PRINTED maxima", lambda n, k: v1 if vh(k) else i1),
        ("K3 one 5 V lead's two contacts at 0, every other contact at its initial maximum", "BOUND", lambda n, k: 0.0 if n == "J_5V_DEV" else (v0 if vh(k) else i1)),
        ("K4 every IDC contact 0, every VH contact at its initial maximum", "BOUND", lambda n, k: v0 if vh(k) else 0.0),
        ("K5 every IDC contact 0, every VH contact at its after-test maximum", "BOUND", lambda n, k: v1 if vh(k) else 0.0),
    ]


def hot_rating(F, T):
    """the VH contact's current at air T: its range's top less T is the rise it may add; the rise at the rated current is not printed"""
    room = F["vh_tmax"] - T
    return F["vh_a16"] * min(1.0, math.sqrt(room / T_RATED_RISE)), room


def bisect(f, lo, hi, n=60):
    """the largest x in [lo, hi] with f(x) true, f monotone true-then-false; None if f(lo) is false; hi if f(hi) is true"""
    if not f(lo):
        return None
    if f(hi):
        return hi
    for _ in range(n):
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if f(mid) else (lo, mid)
    return lo


# ------------------------------------------------------------------------------------------------ main
def main():
    w = sys.stdout.write
    F = figures()
    w("l8r2_gndret.py: Layer 8 record l8r2, round 7 (task T5b): board B's ground return, its load basis and its current capacity\n"
      "reconciled (the owner's review of 4 October 2026, RSM-01). PROTOTYPE DESIGN: nothing is built, bought, powered or measured;\n"
      "nothing here is applied to the tree; no figure is a measurement. Case rows cited (inputs/coordinator-cases-2026-10-04-rev3.md):\n"
      "C-DEV rev 1 for the device rail; C-ALLTX rev 3 where a state of it applies; the slots' loads per state as record l9pwr prints them.\n")
    w("\n0. INPUTS (sha256/16)\n")
    ins = [GEN_B, GEN_A, NET_A, NET_B, INT_B, L4E9_PAGE, BUDGET, BUDGET_L9T5, L9T5_OUT, CASES, "v2/docs/records/l8r2/inputs/SOURCES.txt",
           L4E12_OUT, L9STK_PAGE, ASSEMBLY, IFACES, PACKRTN] + ENGINE + sorted(set(DRAFT.values())) + L6_HELP + sorted(SHEETS.values())
    for p in ins:
        w("   %s %s\n" % (sha(p), p))
    w("   the session's choices (authority SESSION, each reversible by editing the constant and regenerating):\n"
      "     T_RATED_RISE %.0f K: the rise at the rated current JST's %.0f A is taken to stand for (ASSUMPTION; the held catalogue prints the range\n"
      "       -40 to +%.0f C 'including temperature rise in applying electrical current' and no rise, no derating curve); it is used only to\n"
      "       label a hot-air figure beside the printed rating, never to pass a row\n"
      "     CU_ALPHA %.5f /K: ideal copper (ASSUMPTION, as records cx1 and l4e11); rho %.3g Ohm m is dc_drop.py's own (parsed)\n"
      "     the J_5V_IOC lead at AWG %d and %.0f mm: record l9t5's draft names no gauge or length (ASSUMPTION, as the four 5 V leads)\n"
      "     J_AB2's ribbon at J_AB1's %.0f mm: its length is TBD in its contract IF-AB-WALL (ASSUMPTION)\n"
      % (T_RATED_RISE, F["vh_a16"], F["vh_tmax"], CU_ALPHA, F["rho"], IOC_AWG, F["lead_mm"], F["ab1_mm"]))

    with tempfile.TemporaryDirectory(prefix="l8r2_gndret_") as d:
        # ---------------------------------------------------------------- 1
        w("\n1. THE REPRODUCTION (scratch copies of %s; each draft applied with --write, the generator run as record l8p's gen_netlist.py runs it)\n" % GEN_B)
        cl = change_list_b()
        w("   L4-E9's change list, board B's rows in application order (%s section 3, parsed):\n" % L4E9_PAGE)
        for n, r, s in cl:
            w("     step %d %s %s\n" % (n, r, s or "none: a missing draft"))
        drafted = [s for _n, _r, s in cl if s]
        want = ["apply_gen_sch_b_%s.py" % x for x in ("gnd002", "fans12", "rt500")]
        w("   its drafted rows are %s: %s; this record's panel5v and ph4 (Layer 5's findings L5R2-F03 and F04, no change-list row) are\n"
          "   composed between them as rounds 1 to 6 and record l9t5 compose them; Layer 9's draft follows the circuit drafts (its own text)\n"
          % (", ".join(drafted), "as this record composes them" if drafted == want else "NOT THE ORDER THIS RECORD COMPOSES"))
        p = os.path.join(d, "stage.py"); shutil.copy(P(GEN_B), p)
        prev, stages, first_stop = None, [], None
        for name in [None] + ROUND + ["iocbuck"]:
            if name:
                rc, msg = apply(name, p)
                if rc:
                    refuse("%s refused a scratch copy in the round's order: %s" % (name, msg))
            res = run_gen(p); g = call_of(res, "GND")
            if g is None:
                refuse("a stage's generator made no GND rail call")
            tot = sum(g["loads"].values())
            w("   %-34s GND handed to intent: %.1f A typical, %.1f A peak, %d sources, %d loads summing %.3f A (limit 1.02 x peak = %.2f A): %s\n"
              % ("as committed" if not name else "+ %s" % os.path.basename(DRAFT[name]).replace("apply_gen_sch_b_", "").replace(".py", ""),
                 g["typ"], g["peak"], len(g["source"]), len(g["loads"]), tot, 1.02 * g["peak"],
                 "RUNS to its end" if res["stop"] is None else "STOPS"))
            if res["stop"]:
                w("       %s\n" % short(res["stop"]))
                first_stop = first_stop or (name, res["stop"])
            if prev is not None:
                gone = {k: v for k, v in prev["loads"].items() if k not in g["loads"]}
                new = {k: v for k, v in g["loads"].items() if k not in prev["loads"]}
                moved = {k: (prev["loads"][k], v) for k, v in g["loads"].items() if k in prev["loads"] and abs(prev["loads"][k] - v) > 1e-12}
                if gone or new or moved:
                    w("       the sum moves %+.3f A: %s\n" % (tot - sum(prev["loads"].values()), "; ".join(
                        ["%s %.3f A leaves" % kv for kv in sorted(gone.items())] + ["%s %.3f A enters" % kv for kv in sorted(new.items())]
                        + ["%s %.3f to %.3f A" % (k, a, b) for k, (a, b) in sorted(moved.items())])))
                    if g["source"] != prev["source"]:
                        w("       sources: %s\n" % ", ".join(g["source"]))
                else:
                    w("       the list does not move\n")
            prev = g; stages.append((name, res, g))
        by = {n: (r, g) for n, r, g in stages}
        fan_delta = sum(by["fans12"][1]["loads"].values()) - sum(by["gnd002"][1]["loads"].values())
        w("   WHICH DRAFT MOVES THE SUM: fans12 alone, by %+.3f A (three slots, each fan header's 0.100 A becoming its step-up's 0.690 A at the\n"
          "   slot rail); Layer 9's draft moves it by %+.3f A (the three LDOs' 0.12 A leave +5V_DEV's list and re-enter as its own)\n"
          % (fan_delta, sum(by["iocbuck"][1]["loads"].values()) - sum(by["rt500"][1]["loads"].values())))
        w("   the stop is reproduced after fans12 and at every later stage, without Layer 9's draft (rt500's line) and with it (iocbuck's line): %s\n"
          % ("yes" if first_stop and first_stop[0] == "fans12" and all(by[n][0]["stop"] and "rail GND declares" in by[n][0]["stop"] for n in ROUND[1:] + ["iocbuck"]) else "NO"))

        # ---------------------------------------------------------------- 2
        w("\n2. THE LOAD BASIS\n")
        base_res = by[None][0]; comp_res = by["rt500"][0]; ioc_res = by["iocbuck"][0]
        w("2a. what _GND_LOADS is: the union of the arriving 5 V rails' own allocations, each at the part its branch returns at (the generator's\n"
          "    comment of 13 September). Read from the recorded calls, composed through rt500 (with Layer 9's draft in brackets):\n")
        tot_c, tot_i = 0.0, 0.0
        arr_c =[c for c in comp_res["calls"] if isinstance(c["source"], str) and c["source"].startswith("J_5V")]
        arr_i = [c for c in ioc_res["calls"] if isinstance(c["source"], str) and c["source"].startswith("J_5V")]
        gi = {c["net"]: c for c in arr_i}
        for c in arr_c:
            s = sum(c["loads"].values()); tot_c += s
            ci = gi.get(c["net"]); si = sum(ci["loads"].values()) if ci else 0.0
            w("      %-8s at %-9s declared %.2f A typical, %.2f A peak; its loads sum %.3f A (%.2f / %.2f A, loads %.3f A)\n"
              % (c["net"], c["source"], c["typ"], c["peak"], s, ci["typ"], ci["peak"], si))
        for c in arr_i:
            if c["net"] not in {x["net"] for x in arr_c}:
                w("      %-8s at %-9s (Layer 9's draft only: %.2f A typical, %.2f A peak, loads %.3f A)\n" % (c["net"], c["source"], c["typ"], c["peak"], sum(c["loads"].values())))
        tot_i = sum(sum(c["loads"].values()) for c in arr_i)
        gc, gI = by["rt500"][1], by["iocbuck"][1]
        w("      the leads' allocations sum to %.3f A (%.3f A); GND's list sums %.3f A (%.3f A): the same amperes, %s\n"
          % (tot_c, tot_i, sum(gc["loads"].values()), sum(gI["loads"].values()),
             "EQUAL" if abs(tot_c - sum(gc["loads"].values())) < 1e-9 and abs(tot_i - sum(gI["loads"].values())) < 1e-9 else "NOT EQUAL"))
        union = {}
        for c in arr_c:
            for k, v in c["loads"].items():
                union[k] = union.get(k, 0.0) + v
        moved = sorted(k for k in union if k not in gc["loads"]); extra = sorted(k for k in gc["loads"] if k not in union)
        w("      keys the return lists at another part than the supply: %s on the supply side, %s on the return side (a polyfuse or an eFuse has\n"
          "      no ground pin that carries its load: PANEL_5V returns at J_PANEL, VBUS_QMX at J_QMX, +5V_HDMI's allocation at U3 and U4)\n"
          % (", ".join(moved) or "none", ", ".join(extra) or "none"))
        w("2b. is it the return current? By Kirchhoff the board's return to board A is the sum of what arrives on its leads; the cables that\n"
          "    leave the board (panel, QMX, camera, LimeSDR, RockBLOCK, HDMI) carry their own return back to this board's ground.\n")
        # the derived rails are declared all over the generator, after the point where the uncorrected one stops: read them from the
        # corrected composition (this round's two drafts in the round, section 5), whose 5 V rails and allocations are the same
        pth5, err5 = compose(["gnd002", "fans12", "fandec", "panel5v", "ph4", "rt500", "gndret"], d, "no_ioc")
        res5 = run_gen(pth5)
        if err5 or res5["stop"]:
            refuse("the corrected composition without Layer 9's draft does not run: %s" % (err5 or res5["stop"]))
        children = [c for c in res5["calls"] if c["child"]]
        twice = sorted({k for c in children for k in c["loads"] if k in gc["loads"]})
        w("    NAMED TWICE: %d of GND's keys are also a load of a rail this board derives (%s). Each is judged: the return's entry is the\n"
          "    5 V allocation of another branch placed at that part (+5V_HDMI's 0.20 A at the two display switches) or the part's own\n"
          "    5 V input, and the derived rail's entry is the part's draw from that rail, already inside its converter's 5 V input. No\n"
          "    ampere is in the return's list twice.\n" % (len(twice), ", ".join(twice) or "none"))
        fan = [c for c in res5["calls"] if c["net"] == "CFAN1_12V"]
        if not fan or "U701" not in gc["loads"] or any(k in gc["loads"] for k in ("U702", "J_FAN1")):
            refuse("the cooler branch is not declared as section 2b states it")
        w("    THE COOLER BRANCH (the brief's example): the return lists the step-up's 5 V input at U701 (%.2f A; 2.75 W of fan over 0.80 at 5.0 V)\n"
          "    and NOT the fan's 12 V current (CFAN1_12V's load U702 %.2f A, CFAN1_V's load J_FAN1): %.2f A leaves at J_FAN1 pin 2 and the\n"
          "    rest of the %.2f A at the step-up's ground. One count.\n"
          % (gc["loads"]["U701"], fan[0]["loads"].get("U702", 0.0), fan[0]["loads"].get("U702", 0.0), gc["loads"]["U701"]))
        poe = call_of(comp_res, "+54V_POE")
        w("    MISSING: the PoE port's return. +54V_POE (%.2f A typical, %.2f A peak) arrives on J_54V, whose pin 2 is on GND on both boards;\n"
          "    the port's current comes back through POE_DRAIN, Q1 and POE_SEN to the sense resistor R12 and enters GND there. The list has\n"
          "    no entry for it and the declaration does not name J_54V. Corrected by this round's draft (R12 at the rail's peak; J_54V a source).\n"
          % (poe["typ"], poe["peak"]))
        w("    RETURNS ELSEWHERE: none found (board B has no second ground and no chassis bond; record l8gnd's GND-002 moves only the\n"
          "    RJ45 shell and C33 to CHASSIS, which carry no supply current).\n")
        w("2c. the three figures the declaration could hold (A; composed through rt500, with Layer 9's draft in brackets):\n")
        pk_c = sum(c["peak"] for c in arr_c) + poe["peak"]; pk_i = sum(c["peak"] for c in arr_i) + poe["peak"]
        ty_c = sum(c["typ"] for c in arr_c) + poe["typ"]; ty_i = sum(c["typ"] for c in arr_i) + poe["typ"]
        pk_0 = sum(c["peak"] for c in base_res["calls"] if isinstance(c["source"], str) and c["source"].startswith("J_5V")) + poe["peak"]
        w("    (i) THE SUM OF THE LEADS' DECLARED PEAKS, an UPPER BOUND (every lead at its own peak at once): %.2f A (%.2f A) with the PoE\n"
          "        lead's %.2f A; %.2f A on the committed generator. The typicals sum to %.2f A (%.2f A). DECLARED.\n"
          % (pk_c, pk_i, poe["peak"], pk_0, ty_c, ty_i))
        B = {"the tree's budget (set 29's candidate)": budget(BUDGET), "Layer 9's rounds 4 and 5 (the copy of fnd/l9t5 at f70d3085)": budget(BUDGET_L9T5)}
        big = {}
        for tag, bud in B.items():
            w("    (ii) LAYER 9'S BUDGET, %s: the four 5.1 V stages' output summed per state (MODEL, record l9pwr section 5b; the PoE\n"
              "         stage is off in every state of that budget):\n" % tag)
            w("         %-28s %8s %8s %12s %14s %16s\n" % ("state", "PLAN", "HIGH", "HIGH least V", "+ one start", "+ every start"))
            best = None
            for st, rows in bud.items():
                plan = sum(r["plan"] for r in rows.values()); high = sum(r["high"] for r in rows.values()); least = sum(r["least"] for r in rows.values())
                adds = sorted((r["start"] - r["least"] for r in rows.values() if r["start"] is not None), reverse=True)
                one = least + (adds[0] if adds else 0.0); allst = least + sum(adds)
                w("         %-28s %8.3f %8.3f %12.3f %14.3f %16.3f\n" % (st, plan, high, least, one, allst))
                if best is None or least > best[1]:
                    best = (st, least, high, plan, one, allst, rows)
            big[tag] = best
            w("         the largest state: %s, %.3f A at HIGH at the least load voltage (%.3f A at 5.1 V, %.3f A at PLAN); with one cooler's\n"
              "         bounded start %.3f A, with every running slot's at once %.3f A (the starts are 100 us averages, record l8r2 round 6)\n"
              % (best[0], best[1], best[2], best[3], best[4], best[5]))
        TREE_B, L9_B = "the tree's budget (set 29's candidate)", "Layer 9's rounds 4 and 5 (the copy of fnd/l9t5 at f70d3085)"
        bt = big[TREE_B]
        rows = B[TREE_B]["PS-ALLTX"]                   # C-DEV rev 1's state: PS-ALLTX at HIGH at the least load voltage
        if abs(rows["DEV"]["least"] - F["cdev_u7_before"]) > 6e-4:
            refuse("the budget's PS-ALLTX device rail (%.3f A) is not record l9t5's figure before its draft (%.4f A)" % (rows["DEV"]["least"], F["cdev_u7_before"]))
        tot6 = rows["S1"]["least"] + rows["S2"]["least"] + rows["S3"]["least"] + F["cdev_u7"] + F["cdev_u601"]
        s3_l9 = B[L9_B]["PS-ALLTX"]["S3"]["least"]
        w("         on C-DEV rev 1 the device rail is %.4f A of that state's figure; with Layer 9's draft composed U7 carries %.4f A and\n"
          "         U601 %.4f A (record l9t5, MODEL), the same %.4f A on two leads: the board's total return does not move\n"
          % (F["cdev_u7_before"], F["cdev_u7"], F["cdev_u601"], F["cdev_u7"] + F["cdev_u601"]))
        n_lm = 4
        src_c = n_lm * F["loop_max"]; src_i = src_c + F["u601_out"]
        w("    (iii) WHAT THE SOURCES CAN DELIVER (a fault bound): each LM5176 5.1 V stage's average loop limits between %.4f and %.4f A (VSNS\n"
          "         %.0f to %.0f mV PRINTED, SNVSAI1D, over the 6 mOhm shunt at 1 %%, DECLARED; record l9t5 prints %.4f A); with this record's\n"
          "         slotlm draft all four leads are such stages: %d x %.3f = %.2f A (with Layer 9's U601 at its output bound %.2f A: %.2f A).\n"
          "         One stage in its limit with the others at the largest state: %.3f A.\n"
          % (F["loop_min"], F["loop_max"], R6.V["vsns"][0] * 1e3, R6.V["vsns"][2] * 1e3, F["l9_loop_max"], n_lm, F["loop_max"], src_c, F["u601_out"], src_i,
             bt[1] - max(r["least"] for r in bt[6].values()) + F["loop_max"]))
        w("    WHICH ONE THE DECLARATION HOLDS, AND WHY: the peak holds (i), named an upper bound in its note; the typical holds the sum of the\n"
          "    leads' typicals; the loads stay the union of the leads' allocations, with the PoE return added.\n"
          "      - (i) is the only figure that is true by construction: the return cannot carry more than its leads are declared to carry,\n"
          "        and those declarations are Layer 5's contract at both ends of each lead. Derived in the generator, it follows a lead\n"
          "        that is declared again; typed, it went stale on 28 September (S-98) and again with fans12.\n"
          "      - (ii) is inside (i) with Layer 9's draft composed: %.3f A with every start at once against %.2f A. Without that draft the\n"
          "        device lead's declared %.1f A peak is under C-DEV rev 1's %.4f A, which is I-03 itself (OPEN, Layer 9's): the return\n"
          "        follows whatever that lead declares and does not paper over it (%.3f A against %.2f A).\n"
          "      - (iii) is a fault current of four independent limits at once; intent.py's own rule puts a fault current in the note,\n"
          "        not in the peak (the barrel rule PI-003 reads the peak). One stage in its limit is inside (i).\n"
          "      - what the peak is NOT: a claim that %.2f A flows. The copper rules solve the return's mesh at the declared loads,\n"
          "        %.3f A with the PoE return; the peak is what a barrel is judged at.\n"
          % (bt[5], pk_i, call_of(comp_res, "+5V_DEV")["peak"], F["cdev_u7_before"], bt[5], pk_c, pk_i, sum(gc["loads"].values()) + poe["peak"]))

        # ---------------------------------------------------------------- 3
        w("\n3. THE CAPACITY BASIS\n")
        nlA = CK.read_netlist(open(P(NET_A), "rb").read()); nlB = CK.read_netlist(open(P(NET_B), "rb").read())
        gA, gB = CK.ground_conductors(nlA), CK.ground_conductors(nlB)
        vhA = sorted(r for r, pp in nlA["pins"].items() if r.startswith(("J_5V_", "J_54V")) and pp.get("2") == "GND")
        vhB = sorted(r for r, pp in nlB["pins"].items() if r.startswith(("J_5V_", "J_54V")) and pp.get("2") == "GND")
        w("3a. THE GROUND CONDUCTORS BETWEEN BOARDS A AND B, read on both committed netlists (%s, %s):\n" % (NET_A, NET_B))
        w("      lead contacts, pin 2 on GND: board A %s; board B %s: %s\n" % (", ".join(vhA), ", ".join(vhB), "the same five" if vhA == vhB and len(vhA) == 5 else "DIFFER"))
        w("      ribbon conductors on GND: J_AB1 pins %s (board A) and %s (board B); J_AB2 pins %s and %s: %d conductors, %s\n"
          % (",".join(gA["J_AB1"]), ",".join(gB["J_AB1"]), ",".join(gA["J_AB2"]), ",".join(gB["J_AB2"]), len(gB["J_AB1"]) + len(gB["J_AB2"]),
             "the same on both boards" if gA == gB else "DIFFER"))
        if not (vhA == vhB and len(vhA) == 5 and gA == gB and len(gB["J_AB1"]) == 9 and len(gB["J_AB2"]) == 8):
            refuse("the netlists' ground conductors are not the model's (five leads, nine and eight ribbon conductors)")
        w("      so the two boards' grounds are ONE net joined by five lead contacts and seventeen ribbon conductors in parallel (six leads\n"
          "      with Layer 9's draft). Nothing makes a lead's pin 2 carry its own rail's current: the return divides by resistance.\n"
          "      NOT IN THE MODEL (each takes current off the conductors below; none has a held resistance): the shields of the GNSS and\n"
          "      LoRa pigtails if board A bonds its jacks to GND, and each board's own plane resistance, taken as one node a board.\n")
        w("3b. THE MAKERS' PRINTED FIGURES\n")
        w("      JST VH (%s, catalogue, revision not printed): %.0f A 'when using AWG #16 with the standard type header' (PRINTED); %.0f A\n"
          "        'when using AWG #18 with the shrouded type header' (PRINTED; the fitted B2P-VH is the standard header, so J_54V's AWG %d lead\n"
          "        has NO STATED RATING, Layer 5's own INCONCLUSIVE); range to +%.0f C including the rise (PRINTED); contact resistance %.0f mOhm\n"
          "        maximum initial, %.0f mOhm after test (PRINTED; NO MINIMUM and no typical); conductors %.2f mm2 (AWG 16) and %.2f mm2 (AWG 18)\n"
          "        (PRINTED). Its note (PRINTED): 'Do not branch in parallel current which exceeds the rated current. If branched in parallel,\n"
          "        current imbalance or other problems may occur. If it is absolutely necessary to branch such a large current in parallel,\n"
          "        design the circuits without causing any imbalance and provide extra margin for each circuit.'\n"
          % (SHEETS["vh"], F["vh_a16"], F["vh_a18"], F["poe_awg"], F["vh_tmax"], F["vh_rc0"], F["vh_rc1"], F["mm2_16"], F["mm2_18"]))
        w("      Wurth WR-CAB ribbon (%s): rated current %.0f A a conductor at 25 C ambient, 'the current rating may decrease due to the derating\n"
          "        effect at higher temperatures' with no curve (PRINTED); conductor resistance %.0f Ohm/km maximum, AWG %d (PRINTED).\n"
          "      Wurth WR-BHD IDC socket (%s): %.0f A a contact, contact resistance %.0f mOhm maximum (PRINTED). Box header: %.0f A at 25 C (PRINTED).\n"
          % (SHEETS["cab"], F["cab_a"], F["cab_ohm_km"], F["cab_awg"], SHEETS["sock"], F["sock_a"], F["sock_rc"], F["hdr_a"]))
        T = F["t_e5"]
        hot, room = hot_rating(F, T)
        w("      THE INSIDE AIR (L4-E12, MODELED): %.2f C in E3-O, %.2f C in E5's dwell. The VH contact may add %.2f K at %.2f C before its range's\n"
          "        top. The catalogue prints no rise at %.0f A and no derating curve: if that rise is %.0f K (ASSUMPTION) the contact carries\n"
          "        %.3f A at %.2f C; the printed %.0f A is what the rows below are judged at, and this figure is shown beside it. The budget's\n"
          "        largest state at E5's air is a conservative pairing: L4-E12's states at that air run less than PS-ALLTX.\n"
          % (F["t_e3o"], T, room, T, F["vh_a16"], T_RATED_RISE, hot, T, F["vh_a16"]))
        w("3c. THE CONDUCTORS' RESISTANCE (MODEL: rho %.3g Ohm m at 20 C from dc_drop.py, the catalogue's sections, %.0f mm leads and the %.0f mm\n"
          "    ribbon from ASSEMBLY.md section 4; at 20 C and at %.2f C):\n" % (F["rho"], F["lead_mm"], F["ab1_mm"], T))
        c20, cT = conductors(F, 20.0, False), conductors(F, T, False)
        for (n, kind, k, r20), (_n, _k, _kk, rT) in zip(c20, cT):
            w("      %-9s %-5s %2d conductor%s  %7.3f mOhm each at 20 C, %7.3f at %.2f C%s\n"
              % (n, {"VH": "AWG%d" % F["slot_awg"], "VH18": "AWG%d" % F["poe_awg"], "RIB": "AWG%d" % F["cab_awg"]}[kind], k, " " if k == 1 else "s", r20, rT, T,
                 "  (the maker's maximum)" if kind == "RIB" else ""))
        w("      a lead's two contacts may add up to %.0f mOhm initial and %.0f mOhm after test, four to sixteen times the lead itself: the\n"
          "      division between the leads is set by the contacts, which the maker bounds from above only.\n"
          % (2 * F["vh_rc0"], 2 * F["vh_rc1"]))
        loads_c = sum(gc["loads"].values()) + poe["peak"]
        totals = [("the declared loads composed, with the PoE return", loads_c, False),
                  ("Layer 9's largest state (the tree's budget, %s, HIGH at the least load voltage)" % bt[0], bt[1], False),
                  ("C-DEV rev 1's state (PS-ALLTX, HIGH, the least load voltage) with Layer 9's draft composed, six leads", tot6, True),
                  ("the upper bound (i), five leads", pk_c, False),
                  ("the upper bound (i) with Layer 9's draft, six leads", pk_i, True)]
        w("3d. THE RETURN DIVIDED BY RESISTANCE (MODEL at %.2f C; A per conductor; 'OVER' against the PRINTED %.0f A of a VH contact with AWG 16\n"
          "    and %.0f A of a ribbon conductor at 25 C; J_54V's AWG %d contact has no stated rating and is shown against the shrouded header's %.0f A\n"
          "    as a comparator only):\n" % (T, F["vh_a16"], F["cab_a"], F["poe_awg"], F["vh_a18"]))
        worst = {"VH": 0.0, "RIB": 0.0, "VH_bal": 0.0, "RIB_bal": 0.0, "VH18_bal": 0.0}
        over_rows, bal_over = [], []
        for tag, tot, ioc in totals:
            conds = conductors(F, T, ioc)
            w("    %s: %.3f A\n" % (tag, tot))
            w("      %-74s %9s %9s %9s %9s %9s  %s\n" % ("contacts", "5 V lead", "(largest)", "J_54V", "a ribbon", "in ribbons", "drop mV"))
            for ctag, lab, rc in cases(F):
                amps, drop = split(tot, conds, rc)
                vh = [amps[n] for n, kind, _k, _w in conds if kind == "VH"]
                rib = max(amps["J_AB1"], amps["J_AB2"]); rib_sum = 9 * amps["J_AB1"] + 8 * amps["J_AB2"]
                flags = []
                if max(vh) > F["vh_a16"] + 1e-9:
                    flags.append("VH OVER")
                if rib > F["cab_a"] + 1e-9:
                    flags.append("RIBBON OVER")
                bal = ctag.startswith(("K0", "K1", "K2"))
                if bal:
                    worst["VH_bal"] = max(worst["VH_bal"], max(vh)); worst["RIB_bal"] = max(worst["RIB_bal"], rib); worst["VH18_bal"] = max(worst["VH18_bal"], amps["J_54V"])
                    if flags:
                        bal_over.append((tag, ctag))
                worst["VH"] = max(worst["VH"], max(vh)); worst["RIB"] = max(worst["RIB"], rib)
                if flags:
                    over_rows.append((tag, ctag, lab))
                w("      %-74s %9.3f %9.3f %9.3f %9.3f %9.3f  %6.1f  %s%s\n"
                  % (ctag, min(vh), max(vh), amps["J_54V"], rib, rib_sum, drop, lab, (": " + ", ".join(flags)) if flags else ""))
        shares = []
        for tag, tot, ioc in totals:
            conds = conductors(F, T, ioc)
            for ctag, lab, rc in cases(F)[:3]:
                amps, _d = split(tot, conds, rc)
                shares.append((9 * amps["J_AB1"] + 8 * amps["J_AB2"]) / tot)
        w("    READ: with every contact at ONE value (K0 to K2, the balanced design) %s: a 5 V lead's\n"
          "    contact carries at most %.3f A of %.0f A (%.3f A at %.2f C on the %.0f K ASSUMPTION), J_54V's at most %.3f A, a ribbon conductor at most\n"
          "    %.3f A of %.0f A at 25 C; but the ribbons then carry %.1f to %.1f %% of the whole return, which their contracts (IF-AB-RIBBON,\n"
          "    IF-AB-WALL: signals, 1 A a contact) never counted, at %.2f C air where the maker prints a derating and no curve. On the makers'\n"
          "    printed extremes (K3 to K5, BOUNDS: no minimum contact resistance is printed) a lead contact reaches %.3f A and a ribbon\n"
          "    conductor %.3f A.\n"
          % ("no conductor passes its printed rating" if not bal_over else "A CONDUCTOR PASSES ITS PRINTED RATING (%d rows)" % len(bal_over),
             worst["VH_bal"], F["vh_a16"], hot, T, T_RATED_RISE, worst["VH18_bal"], worst["RIB_bal"], F["cab_a"],
             100 * min(shares), 100 * max(shares), T, worst["VH"], worst["RIB"]))
        # thresholds
        w("3e. WHAT WOULD HAVE TO BE TRUE OF THE CONTACTS (MODEL at %.2f C; the figures a harness measurement would be judged against):\n" % T)
        for tag, tot, ioc in (totals[1], totals[3], totals[4]):
            conds = conductors(F, T, ioc)
            f1 = lambda c: max(split(tot, conds, lambda n, k: c if k in ("VH", "VH18") else 0.0)[0][h] for h in ("J_AB1", "J_AB2")) <= F["cab_a"]
            f2 = lambda x: split(tot, conds, lambda n, k: 0.0 if n == "J_5V_DEV" else (x if k in ("VH", "VH18") else F["sock_rc"]))[0]["J_5V_DEV"] <= F["vh_a16"]
            c1, c2 = bisect(f1, 0.0, 100.0), bisect(f2, 0.0, 100.0)
            w("      at %.3f A (%s):\n"
              "        a ribbon conductor stays at or under %.0f A with its own contacts at 0 only while every VH contact is at or under %s mOhm\n"
              "        (the maker's limit is %.0f mOhm initial); a 5 V lead whose two contacts are at 0 stays at or under %.0f A only while the\n"
              "        other VH contacts are at or under %s mOhm\n"
              % (tot, tag, F["cab_a"], "%.2f" % c1 if c1 is not None else "none: over at every value", F["vh_rc0"], F["vh_a16"],
                 "%.2f" % c2 if c2 is not None else "none: over at every value"))
        w("3f. THE SUPPLY PINS (pin 1 carries its own rail and nothing else; PRINTED %.0f A with AWG 16; %.3f A at %.2f C on the ASSUMPTION):\n" % (F["vh_a16"], hot, T))
        for n in ("S1", "S2", "S3"):
            w("      J_5V_%s pin 1: %.3f A at the largest state (HIGH, least voltage), %.3f A at its bounded start; declared peak %.1f A: within\n"
              % (n, rows[n]["least"], rows[n]["start"], call_of(comp_res, "+5V_%s" % n)["peak"]))
        w("      J_5V_DEV pin 1: %.4f A on C-DEV rev 1 as committed and composed without Layer 9's draft, over the lead's declared %.1f A peak\n"
          "        (I-03, OPEN, Layer 9's); %.4f A with Layer 9's draft; the stage's loop can hold up to %.4f A, under the contact's %.0f A (PRINTED)\n"
          "        and over %.3f A at %.2f C on the ASSUMPTION: a fault current, named for Layer 9's author\n"
          % (F["cdev_u7_before"], call_of(comp_res, "+5V_DEV")["peak"], F["cdev_u7"], F["loop_max"], F["vh_a16"], hot, T))
        w("      J_5V_IOC pin 1 (Layer 9's draft): %.4f A on the case; J_54V pin 1: %.2f A peak on AWG %d (no stated rating; %.0f A the comparator)\n"
          % (F["cdev_u601"], poe["peak"], F["poe_awg"], F["vh_a18"]))
        w("      THE LEAD: AWG %d, %.0f mm; JST's %.0f A is stated for the crimped contact WITH that gauge, so it is the lead's rating too. The wire\n"
          "      itself (its part, its insulation's temperature class) is named nowhere in the tree: OWED to Layer 7 (finding L8R2-F34).\n"
          % (F["slot_awg"], F["lead_mm"], F["vh_a16"]))
        w("3g. THE GROUND COPPER WHERE THE RETURNS ENTER (decision 35's function, track_current.width_for_current, 10 K, inner layers; Layer 9's\n"
          "    stackup for board B is %s, layer use %s: %d ground planes at %.1f oz; board A's has %d at %.1f oz):\n"
          % (F["b_stack"], F["b_use"], F["b_gnd_planes"], F["b_inner_oz"], F["a_gnd_planes"], F["a_inner_oz"]))
        for lab, amps in (("a 5 V lead's contact at balance, the largest (K0 to K2)", worst["VH_bal"]), ("a lead's declared peak %.1f A (its own rail returning alone)" % call_of(comp_res, "+5V_S1")["peak"], call_of(comp_res, "+5V_S1")["peak"]),
                          ("the contact's printed %.0f A" % F["vh_a16"], F["vh_a16"])):
            wB = TC.width_for_current(amps, F["b_inner_oz"], 10.0, internal=True); wA = TC.width_for_current(amps, F["a_inner_oz"], 10.0, internal=True)
            w("      %-62s %6.3f A: %6.2f mm of %.1f oz plane in all; board B %5.2f mm on each of %d planes (a solid ring at radius %.2f mm),\n"
              "      %-62s           board A %5.2f mm on each of %d (radius %.2f mm)\n"
              % (lab, amps, wB, F["b_inner_oz"], wB / F["b_gnd_planes"], F["b_gnd_planes"], wB / F["b_gnd_planes"] / (2 * math.pi), "", wA / F["a_gnd_planes"], F["a_gnd_planes"], wA / F["a_gnd_planes"] / (2 * math.pi)))
        spB, spA = 4 * 0.5 * F["b_gnd_planes"], 4 * 0.5 * F["a_gnd_planes"]
        least = TC.width_for_current(worst["VH_bal"], F["b_inner_oz"], 10.0, internal=True)
        w("      READ (MODEL: the ruled function applied to the plane's section around the pin): a pin 2 land joined SOLIDLY to every ground\n"
          "      plane has the width within a few millimetres of the pin on either board; four thermal-relief spokes of 0.5 mm on each\n"
          "      plane give %.1f mm on board B and %.1f mm on board A, %s the least row above (%.2f mm). A LAYOUT CONSTRAINT for both boards\n"
          "      (finding L8R2-F33): no thermal relief on the VH leads' pin 2, or spokes summing to the row's width. The routed board's own\n"
          "      reading is dc_drop's, at the declared loads, with the five (six) leads as sources.\n"
          % (spB, spA, "under" if max(spB, spA) < least else "NOT under", least))
        ga = text(GEN_A)
        a_node = '_intent.node("GND"' in ga and '_intent.rail("GND"' not in ga
        pr = text(PACKRTN)
        w("3h. BOARD A'S END. Its committed generator declares GND as a %s; this record's round 3 draft (apply_gen_sch_a_packrtn.py) declares it\n"
          "    a rail returning CELL+ from the dock contacts to the stages' input ends at the pack's %s. Neither says that the 5 V returns\n"
          "    enter at J_5V_S1..3, J_5V_DEV and J_54V pin 2 and at the ribbons and close at each stage's output: intent.rail has one set of\n"
          "    sources and takes no current entering at a load, so the rule set cannot solve that loop on board A as it stands (finding\n"
          "    L8R2-F33: the same currents and the same layout constraint as board B's, stated for board A's layout).\n"
          % ("node, which no copper rule solves" if a_node else "rail", "18.0 A" if "0.0, 10.0, 18.0" in pr else "declared peak"))
        ifc = yaml.safe_load(text(IFACES))

        def find(o, k):
            if isinstance(o, dict):
                if k in o:
                    return o[k]
                for v in o.values():
                    r = find(v, k)
                    if r is not None:
                        return r
            return None
        ifp, ifr, ifw = find(ifc, "IF-AB-POWER"), find(ifc, "IF-AB-RIBBON"), find(ifc, "IF-AB-WALL")
        if not (ifp and ifr and ifw):
            refuse("pcb_interfaces.yaml no longer carries the three A to B contracts")
        says_return = bool(re.search(r"\breturn", json.dumps([ifp.get(k) for k in ("currents", "current", "contact_rating", "harness", "pins_each")]).lower()))
        w("3i. LAYER 5'S CONTRACT ROWS (%s). IF-AB-POWER: harness '%s'; pins '%s'; its currents rows declare each rail lead by lead\n"
          "    (5.0, 5.63 and 6.0 A peaks, INTERIM) and its contact_rating reads the %.0f A as this record does. It carries %s for the return's\n"
          "    division, and IF-AB-RIBBON and IF-AB-WALL declare their ground pins as signal returns at %.0f A a contact. The row texts this\n"
          "    round proposes are in the record's section 7 (Layer 5's files are its own).\n"
          % (IFACES, " ".join(str(ifp.get("harness")).split()), ifp.get("pins_each"), F["vh_a16"], "a row" if says_return else "NO ROW", F["sock_a"]))

        # ---------------------------------------------------------------- 4
        w("\n4. THE JUDGMENT\n")
        w("   (a) THE DECLARATION IS WRONG, and is corrected (section 5). Its peak was a typed sum of the leads' peaks that went stale twice;\n"
          "       its typical %.1f A is under the leads' own %.2f A; its sources omit J_54V. The basis supports: typical %.2f A and peak %.2f A\n"
          "       (%.2f A with Layer 9's draft), derived in the generator from the leads' declarations, the peak an UPPER BOUND.\n"
          % (by["rt500"][1]["typ"], ty_c, ty_c, pk_c, pk_i))
        w("   (b) THE LOAD LIST IS RIGHT IN WHAT IT COUNTS AND MISSED ONE RETURN: no ampere is counted twice and none returns elsewhere; the PoE\n"
          "       port's %.2f A at R12 is added. Against Layer 9's budget the device rail's ALLOCATIONS (%.2f A) and its declared %.1f A peak are\n"
          "       under C-DEV rev 1's %.4f A: that is I-03 (OPEN), corrected by Layer 9's draft, not by this round.\n"
          % (poe["peak"], sum(call_of(comp_res, "+5V_DEV")["loads"].values()), call_of(comp_res, "+5V_DEV")["peak"], F["cdev_u7_before"]))
        w("   (c) THE RETURN PATH IS NOT SHOWN SHORT OF THE LOAD, AND IS NOT SHOWN TO HOLD: finding L8R2-F31, OPEN. With equal contacts every\n"
          "       conductor is inside its printed rating at every total up to the upper bound. But the return is branched in parallel over\n"
          "       contacts whose maker asks for a design 'without causing any imbalance' with 'extra margin for each circuit', the ribbons'\n"
          "       seventeen signal grounds carry a third to a half of it, and the makers bound the contact resistances from above only: on\n"
          "       the printed extremes a lead contact reads %.1f A against %.0f A and a ribbon conductor %.2f A against %.0f A. Those are the\n"
          "       MODEL's answers on printed bounds, not a demonstrated overload; and the balanced reading is not evidence either. What\n"
          "       closes it is in section 7: a design change that takes the dependence away, or the harness measurement of 3e.\n"
          "       NOT raised to make the generator pass: the declaration is derived, the same text reads %.2f A on the committed generator,\n"
          "       and the capacity finding stays OPEN beside it.\n"
          % (worst["VH"], F["vh_a16"], worst["RIB"], F["cab_a"], pk_0))

        # ---------------------------------------------------------------- 5
        w("\n5. THE CORRECTION (two drafts, release-guarded, on scratch copies)\n")
        ok_guard = True
        for name in ("gndret", "fandec"):
            t = os.path.join(d, "g_%s.py" % name); shutil.copy(P(GEN_B), t)
            c_rc, c_msg = apply(name, t, "--check"); same = open(t, "rb").read() == open(P(GEN_B), "rb").read()
            w_rc, w_msg = apply(name, t); a_ok = True
            try:
                ast.parse(open(t, encoding="utf-8").read())
            except SyntaxError:
                a_ok = False
            r_rc, r_msg = apply(name, t); t_rc, t_msg = apply(name, P(GEN_B))
            good = (c_rc, same, w_rc, a_ok, r_rc, t_rc) == (0, True, 0, True, 3, 3)
            ok_guard = ok_guard and good
            w("   %s sha256 %s\n     --check exit %d (target unchanged: %s); --write exit %d (parses: %s); a second --write exit %d (%s);\n"
              "     on the tree's own generator exit %d (%s)\n"
              % (MINE[name], sha(MINE[name]), c_rc, "yes" if same else "NO", w_rc, "yes" if a_ok else "NO", r_rc, short(r_msg, 90), t_rc, short(t_msg, 110)))
        orders = [("the round's order, this record's two in place, Layer 9's draft, Layer 6's", ["gnd002", "fans12", "fandec", "panel5v", "ph4", "rt500", "gndret", "iocbuck"] + L6),
                  ("Layer 9's draft before this record's two", ["gnd002", "fans12", "panel5v", "ph4", "rt500", "iocbuck", "fandec", "gndret"] + L6),
                  ("this record's two first", ["gndret", "fandec", "gnd002", "fans12", "panel5v", "ph4", "rt500", "iocbuck"] + L6),
                  ("the round reversed", ["gndret", "rt500", "ph4", "panel5v", "fandec", "fans12", "gnd002", "iocbuck"] + L6)]
        w("   THE COMPOSITION WITH Layer 9's draft and Layer 6's three (xal_land, lcsc, intent), in four orders:\n")
        gens, runs = [], []
        for i, (tag, seq) in enumerate(orders):
            pth, err = compose(seq, d, "ord%d" % i)
            if err:
                w("     %-76s %s\n" % (tag, err)); gens.append(None); runs.append(None)
                continue
            res = run_gen(pth); gens.append(hashlib.sha256(open(pth, "rb").read()).hexdigest()[:16]); runs.append(res)
            g = (res["intent"] or {}).get("rails", {}).get("GND") if res["intent"] else None
            w("     %-76s generator sha256 %s: %s\n" % (tag, gens[-1], "RUNS to its end, %d parts, GND %.2f A typical, %.2f A peak, loads %.3f A"
                                                         % (len(res["table"]["parts"]), g["amps_typ"], g["amps_peak"], sum(g["loads"].values()))
                                                         if res["stop"] is None else "STOPS: " + short(res["stop"], 150)))
        one_gen = len({x for x in gens}) == 1 and gens[0] is not None
        all_run = all(r is not None and r["stop"] is None for r in runs)
        w("     the four orders give one generator, byte for byte: %s; every order runs to its end: %s\n" % ("yes" if one_gen else "NO", "yes" if all_run else "NO"))
        w("     without Layer 9's draft (this record's round alone): RUNS to its end, %d parts\n" % len(res5["table"]["parts"]))
        pth1, _e = compose(["gndret"], d, "alone"); res1 = run_gen(pth1)
        g1 = res1["intent"]["rails"]["GND"] if res1["intent"] else None
        w("     the gndret draft alone on the committed generator: %s\n"
          % ("RUNS, GND %.2f A typical and %.2f A peak, loads %.3f A: the same text, a smaller figure (nothing typed)" % (g1["amps_typ"], g1["amps_peak"], sum(g1["loads"].values()))
             if g1 else "STOPS: " + short(res1["stop"], 150)))
        w("   THE NETLIST CHECK (check_gndret_netlist.py; the regenerated netlists are the generator's own part tables, no KiCad: the box\n"
          "   export is the reading of record):\n")
        vC, lC = CK.judge(nlB, json.load(open(P(INT_B), encoding="utf-8")))
        w("     the committed netlist and intent (%s sha256 %s): %s\n" % (NET_B, sha(NET_B), vC))
        for l in lC:
            w("       %s\n" % l)
        checks = {}
        for tag, res in (("composed without Layer 9's draft", res5), ("composed with Layer 9's draft and Layer 6's", runs[0])):
            if res is None or res["stop"]:
                w("     %s: NO NETLIST (the generator stops)\n" % tag); checks[tag] = "STOPS"
                continue
            v, lines = CK.judge(CK.read_netlist(res["netlist"]), res["intent"]); checks[tag] = v
            w("     %s (netlist sha256 %s): %s\n" % (tag, hashlib.sha256(res["netlist"]).hexdigest()[:16], v))
            for l in lines:
                w("       %s\n" % l)
        # mutations
        w("   THE MUTATIONS (each must stop the generator or FAIL the check):\n")
        full = ["gnd002", "fans12", "fandec", "panel5v", "ph4", "rt500", "gndret", "iocbuck"]
        muts = []

        def gen_mut(tag, seq, edit=None):
            pth, err = compose(seq, d, "mut%d" % len(muts))
            if err:
                refuse("a mutation's composition refused: %s" % err)
            if edit:
                t0 = open(pth, encoding="utf-8").read(); t1 = edit(t0)
                if t1 == t0:
                    refuse("mutation '%s' changed nothing" % tag)
                open(pth, "w", encoding="utf-8").write(t1)
            res = run_gen(pth)
            if res["stop"]:
                out = "STOPS: " + short(res["stop"], 170); bad = True
            else:
                v, lines = CK.judge(CK.read_netlist(res["netlist"]), res["intent"])
                out = "runs; the check reads %s%s" % (v, (": " + short("; ".join(l for l in lines if l[:2] in ("R1", "R2", "R3", "R4")), 200)) if v != "DRAWN" else "")
                bad = v != "DRAWN"
            muts.append(bad)
            w("     m%d %s\n        %s\n" % (len(muts), tag, out))

        def sub1(old, new):
            def f(t):
                if t.count(old) != 1:
                    refuse("a mutation's anchor occurs %d times: %r" % (t.count(old), old[:50]))
                return t.replace(old, new)
            return f
        gen_mut("the old state: the full composition without the gndret draft", [s for s in full if s != "gndret"])
        gen_mut("the gndret draft without its companion fandec (the second stop behind the first)", [s for s in full if s != "fandec"])
        gen_mut("the typed declaration kept and simply raised: 21.0 written as 30.0 on the old text (the refused outcome)",
                [s for s in full if s != "gndret"], sub1('_intent.rail("GND", 0.0, 10.0, 21.0, ', '_intent.rail("GND", 0.0, 10.0, 30.0, '))
        gen_mut("J_54V dropped from the return's sources in the helper", full, sub1('_srcs = list(leads) + ["J_54V"]', "_srcs = list(leads)"))
        gen_mut("a lead named on the return whose rail is declared on another connector (+5V_S2's source J_5V_S2 written J_5V_S9)", full,
                sub1('6.6, "J_5V_S%d" % _n, loads=_SLOT_LOADS(_n)', '6.6, "J_5V_S%d" % (9 if _n == 2 else _n), loads=_SLOT_LOADS(_n)'))
        gen_mut("a slot's card buck allocation raised from 2.2 to 4.2 A (a lead over its own peak: the derived return must not hide it)", full,
                sub1('    "U%d03" % s: 2.2, ', '    "U%d03" % s: 4.2, '))
        # netlist-level mutations on the composed netlist
        base = runs[0]
        if base is None or base["stop"]:
            refuse("no composed netlist for the netlist mutations")

        def net_mut(tag, f):
            raw = base["netlist"].decode("utf-8"); m = f(raw)
            if m == raw:
                refuse("netlist mutation '%s' changed nothing" % tag)
            v, lines = CK.judge(CK.read_netlist(m.encode("utf-8")), base["intent"])
            muts.append(v == "FAIL")
            w("     m%d %s\n        the check reads %s: %s\n" % (len(muts), tag, v, short("; ".join(l for l in lines if l[:2] in ("R1", "R2", "R3", "R4")), 200)))

        def swap_pins(ref):
            def f(raw):
                a, b, z = '(node (ref "%s") (pin "1"))' % ref, '(node (ref "%s") (pin "2"))' % ref, "\x00"
                if raw.count(a) != 1 or raw.count(b) != 1:
                    refuse("the netlist does not carry %s's two pins once each" % ref)
                return raw.replace(a, z).replace(b, a).replace(z, b)
            return f
        net_mut("J_5V_S2's pins 1 and 2 exchanged on the netlist (the lead reversed)", swap_pins("J_5V_S2"))
        net_mut("R12's pin 2 taken off GND on the netlist (the PoE return's entry gone)", lambda raw: raw.replace(' (node (ref "R12") (pin "2"))', "", 1))
        all_mut = all(muts)
        w("     every mutation stops or fails: %s (%d of %d)\n" % ("yes" if all_mut else "NO", sum(muts), len(muts)))

        # ---------------------------------------------------------------- 6
        w("\n6. FOR LAYER 9'S AUTHOR AND THE INDEPENDENT RECHECK (V3)\n")
        w("   board B's composition in L4-E9's order with Layer 9's draft RUNS TO ITS END once this round's two drafts are in it (section 5):\n"
          "     gnd002, fans12, fandec, panel5v, ph4, rt500, gndret, iocbuck, then Layer 6's three; fandec and gndret anywhere in the round.\n"
          "   the corrected declaration with Layer 9's draft composed (read from the regenerated intent):\n")
        gi2 = runs[0]["intent"]["rails"]["GND"]
        w("     GND: %.2f A typical, %.2f A peak (the UPPER BOUND, DECLARED), sources %s; %d loads summing %.3f A\n"
          % (gi2["amps_typ"], gi2["amps_peak"], ", ".join(gi2["source"]), len(gi2["loads"]), sum(gi2["loads"].values())))
        w("     the load list: _GND_LOADS as Layer 9's draft leaves it (U40, U50 and U60 at 0.12 A each from _IOC_LOADS) plus R12 %.2f A\n" % gi2["loads"]["R12"])
        conds = conductors(F, T, True)
        w("   THE RETURN EACH CONNECTOR CARRIES ON C-DEV rev 1 WITH LAYER 9'S DRAFT COMPOSED (the state PS-ALLTX at HIGH at the least load voltage\n"
          "   4.9019 V; total %.4f A = S1 %.3f + S2 %.3f + S3 %.3f + U7 %.4f + U601 %.4f, MODEL: records l9pwr and l9t5; MODEL at %.2f C):\n"
          % (tot6, rows["S1"]["least"], rows["S2"]["least"], rows["S3"]["least"], F["cdev_u7"], F["cdev_u601"], T))
        pin1 = {"J_5V_S1": rows["S1"]["least"], "J_5V_S2": rows["S2"]["least"], "J_5V_S3": rows["S3"]["least"], "J_5V_DEV": F["cdev_u7"], "J_5V_IOC": F["cdev_u601"], "J_54V": 0.0}
        cs = cases(F)
        sp = [split(tot6, conds, rc)[0] for _t, _l, rc in (cs[0], cs[1], cs[3])]
        w("     %-10s %14s %22s %22s %30s\n" % ("connector", "pin 1 (MODEL)", "pin 2, K0 (MODEL)", "pin 2, K1 (MODEL)", "pin 2, K3 (BOUND, J_5V_DEV at 0)"))
        for n, kind, k, _w in conds:
            if kind == "RIB":
                w("     %-10s %14s %22s %22s %30s\n" % (n, "signals", "%.3f A x %d" % (sp[0][n], k), "%.3f A x %d" % (sp[1][n], k), "%.3f A x %d" % (sp[2][n], k)))
            else:
                w("     %-10s %12.4f A %20.3f A %20.3f A %28.3f A\n" % (n, pin1[n], sp[0][n], sp[1][n], sp[2][n]))
        w("     labels: pin 1 is each rail's own current (J_54V's 0: the PoE stage is off in PS-ALLTX; %.2f A DECLARED peak when the outlet is on);\n"
          "     pin 2 is the SAME total divided by resistance, so J_5V_IOC's pin 2 carries about a sixth of the leads' share whatever U601\n"
          "     supplies, and 'J_5V_DEV's return falls by the same current' (record l9t5's line) holds for pin 1 and not for pin 2. The J_5V_IOC\n"
          "     lead's gauge and length are ASSUMPTIONS here (AWG %d, %.0f mm): record l9t5's draft names neither.\n"
          "     On Layer 9's own rounds 4 and 5 (PS-ALLTX with the standby card off) slot 3 reads %.3f A and the total %.4f A; every row above\n"
          "     scales by %.4f.\n"
          % (poe["peak"], IOC_AWG, F["lead_mm"], s3_l9, tot6 - rows["S3"]["least"] + s3_l9, (tot6 - rows["S3"]["least"] + s3_l9) / tot6))
        w("   CREDIT (the common brief's three criteria) for this round's two drafts: (a) composes in L4-E9's order and the generator runs: %s;\n"
          "   (b) the changed declaration read on the regenerated netlist and intent with mutations that fail: %s; (c) electrical acceptance on\n"
          "   the makers' printed figures: the DECLARATION is supported as an upper bound; the RETURN PATH's capacity is NOT accepted\n"
          "   (L8R2-F31 OPEN). A netlist check is not electrical qualification.\n"
          % ("yes" if all_run else "NO", "yes" if checks.get("composed with Layer 9's draft and Layer 6's") == "DRAWN" and all_mut else "NO"))

        # ---------------------------------------------------------------- 7
        w("\n7. FINDINGS\n")
        w("   L8R2-F30 CORRECTED BY DRAFT (not applied): board B's GND declaration was typed and stale (10.0 A, 21.0 A, four leads, a note of\n"
          "            19.4 A); derived by apply_gen_sch_b_gndret.py; the PoE return and J_54V added. Credit (a) and (b) above; UNCHECKED by\n"
          "            an independent check.\n"
          "   L8R2-F31 OPEN (KNOWN DEFECT of the A to B power interface, boards A and B, Layers 5 and 7): the return is branched in parallel\n"
          "            over five (six) VH contacts and seventeen ribbon conductors with nothing that sets its division. Balanced, every\n"
          "            conductor is inside its printed rating; the ribbons carry %.0f to %.0f %% of it; on the makers' printed extremes a lead\n"
          "            contact reads %.1f A and a ribbon conductor %.2f A (BOUNDS). Section 7 of the page compares the corrections.\n"
          "   L8R2-F32 CORRECTED BY DRAFT (not applied): fans12's two TPS61089 capacitors carried their class at the call, which board B's\n"
          "            decision 42 block does not read; the composed generator stopped there once the ground's stop was gone;\n"
          "            apply_gen_sch_b_fandec.py. Rounds 1 to 6's composition proof never ran the generator: a finding against this record.\n"
          "   L8R2-F33 OPEN (layout constraint, boards A and B; Layer 9's layout-constraints and record l9stk): each VH lead's pin 2 joins its\n"
          "            ground planes without thermal relief (or with spokes of the width section 3g prints); board A's intent has no\n"
          "            declaration that makes a rule solve the 5 V returns' loop.\n"
          "   L8R2-F34 OWED (Layer 7): the leads' wire part and its insulation class at the inside air; J_54V's AWG %d lead on the standard\n"
          "            header has no stated rating and now shares the 5 V return (up to %.3f A balanced): an AWG 16 lead gives it the printed row.\n"
          "   L8R2-F35 FOR LAYER 9'S AUTHOR (record l9t5): its line 'J_5V_DEV's return falls by the same current' holds for the supply pin only;\n"
          "            name J_5V_IOC's lead gauge and length; the device lead's declared %.1f A peak is under its own %.4f A on C-DEV rev 1\n"
          "            at the least load voltage; add fandec and gndret to its board B order.\n"
          "   L8R2-F36 FOR L4-E9 (the change list): two new board B rows in R-190's release (fandec with fans12; gndret); R-190's row says the\n"
          "            slot's budget is re-derived, and the return's was not.\n"
          % (100 * min(shares), 100 * max(shares), worst["VH"], worst["RIB"], F["poe_awg"], worst["VH18_bal"], call_of(ioc_res, "+5V_DEV")["peak"], F["cdev_u7"]))

        # ---------------------------------------------------------------- 8
        w("\n8. PREDICATES\n")
        preds = [
            ("the stop is reproduced after fans12, without and with Layer 9's draft", bool(first_stop and first_stop[0] == "fans12" and by["rt500"][0]["stop"] and by["iocbuck"][0]["stop"])),
            ("fans12 alone moves the sum, by 1.770 A; Layer 9's draft by 0.000 A", abs(fan_delta - 1.77) < 1e-9 and abs(sum(gI["loads"].values()) - sum(gc["loads"].values())) < 1e-9),
            ("the return's list is the union of the leads' allocations (no ampere twice)", abs(tot_c - sum(gc["loads"].values())) < 1e-9),
            ("both netlists carry the same five lead contacts and seventeen ribbon conductors on GND", vhA == vhB and gA == gB and len(gB["J_AB1"]) + len(gB["J_AB2"]) == 17),
            ("each draft checks, applies once, refuses twice and refuses the tree's generator", ok_guard),
            ("the four orders give one generator and each runs to its end", one_gen and all_run),
            ("the composed netlist and intent read DRAWN, the committed ones NOT DRAWN", vC == "NOT DRAWN" and all(v == "DRAWN" for v in checks.values())),
            ("every mutation stops the generator or fails the check", all_mut),
            ("the derived peak equals the leads' sum and is not typed (22.23 A alone, 26.40 A composed, 27.78 A with Layer 9's)",
             g1 is not None and abs(g1["amps_peak"] - pk_0) < 1e-6 and abs(res5["intent"]["rails"]["GND"]["amps_peak"] - pk_c) < 1e-6 and abs(gi2["amps_peak"] - pk_i) < 1e-6),
            ("with Layer 9's draft the upper bound holds the budget's largest state with every start at once", bt[5] <= pk_i),
            ("balanced (K0 to K2) no conductor passes its printed rating at any total", not bal_over),
            ("on the printed extremes (K3 to K5) a conductor passes its rating: the capacity finding stays OPEN", bool(over_rows)),
        ]
        for tag, ok in preds:
            w("   %-118s %s\n" % (tag, "yes" if ok else "NO"))
    w("\nEND\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
