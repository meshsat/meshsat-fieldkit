#!/usr/bin/env python3
"""l8r2_gndret.py: Layer 8 record l8r2, rounds 7 and 8: board B's ground return, its load basis and its current capacity
reconciled (round 7, task T5b, the owner's review of 4 October 2026, RSM-01), and the return between boards A and B corrected by a
dedicated ground return and verified over every permitted aged-contact combination (round 8, finding L8R2-F31, after the
collaborator's recheck V3, checks/astra-check-t5-recheck-cx41.md) (MESHSAT-1357). PROTOTYPE DESIGN: nothing in this kit has been
built, bought, powered or measured, nothing is applied to the tree, and no figure printed here is a measurement.

It prints, deterministically and without touching the tree:
  0. the inputs, each pinned by sha256;
  1. THE REPRODUCTION: board B's pending drafts applied one by one in L4-E9's change-list order on a scratch copy, first without and
     then with Layer 9's I-03 draft (the copy in inputs/); after each, what the generator hands intent.rail for GND (recorded before
     intent judges it), the sum, the move load by load, and whether the generator runs or stops, in intent's own words;
  2. THE LOAD BASIS: what _GND_LOADS sums and whether that is the return current; the three figures the declaration could hold:
     (i) the sum of the leads' declared peaks, an UPPER BOUND, (ii) the largest state of Layer 9's budget, (iii) what board A's
     stages can deliver; which one it holds and why;
  3. THE CAPACITY BASIS AS DRAWN: every ground conductor between boards A and B read on both netlists; the makers' printed figures;
     the return divided between them by resistance with the WORST CASE FOUND, not sampled: the extreme of each conductor's current
     over the box of contact resistances the makers permit (zero where no minimum is printed, the after-test maximum) lies at a
     vertex, so every vertex is enumerated for every conductor, at both ends of the copper's temperature; round 7's six sampled
     cases beside it and what they missed; the supply pins; the ground copper where the leads enter; Layer 5's rows; the
     corrections compared;
  4. THE JUDGMENT;
  5. THE DRAFTS: round 7's two (the declaration, the cooler step-ups' class row) and round 8's two (the dedicated return's sockets
     on boards A and B) on scratch copies: checked, applied once, refused twice, refused on the tree; both boards composed in
     L4-E9's change-list order with Layer 9's drafts; the regenerated netlists read by check_gndret_netlist.py; the mutations,
     each of which must stop the generator or fail a check;
  6. THE ACCEPTANCE WITH THE DEDICATED RETURN (the recheck's closure criterion): on C-DEV rev 1, on the largest state of Layer 9's
     budget and on the declared upper bound, every VH pin 2, every ribbon conductor, the PoE lead and every conductor and contact
     of the dedicated return at its maximum over every vertex, its own terminations at their limit included, against the rating
     its maker prints, at L4-E12's inside air and at the envelope's cold end; the ground shift against Layer 9's LDO headroom;
  7. what Layer 9's author and the independent check need; 8. findings; 9. the predicates test_l8r2.py holds.
Labels: PRINTED a maker's limit in a held sheet; TYPICAL a maker's typical figure; DECLARED a generator's or a record's declaration;
MODEL this record's arithmetic on labelled inputs; INFERRED derived from printed figures under a stated assumption; ASSUMPTION a
figure no held document gives; BOUND a limit computed on the makers' printed extremes, never taken as the circuit's behaviour.
Run from the repository root:  python3 v2/docs/records/l8r2/l8r2_gndret.py  (l8r2_gndret.out is its output, regenerated with
_bin/regen_out.py). Stdlib, PyYAML and pdftotext; about twenty seconds."""
import ast
import hashlib
import importlib.util
import itertools
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
GEN = {"a": "v2/ecad/tools/gen_sch_a.py", "b": "v2/ecad/tools/gen_sch_b.py"}
PROJECT = {"a": "pcb-a-power", "b": "pcb-b-compute"}
NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
NET_B = "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"
INT_B = "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json"
L4E9_PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
BUDGET = "v2/docs/records/l8r2/inputs/l9pwr_budget-841e6c7e.txt"      # Layer 9's budget at fnd/l9t5's tip: the ONE budget read since round 8
L9T5_OUT = "v2/docs/records/l8r2/inputs/l9t5_drafts-841e6c7e.txt"
L9T5_DRAFT = "v2/docs/records/l8r2/inputs/l9t5-apply_gen_sch_b_iocbuck-841e6c7e.py"
L9T5_DRAFT_A = "v2/docs/records/l8r2/inputs/l9t5-apply_gen_sch_a_iocbuck-841e6c7e.py"
V3 = "v2/docs/records/l8r2/checks/astra-check-t5-recheck-cx41.md"
ENVELOPE = "v2/ecad/tools/pcb_envelope.yaml"
CHAIN = "v2/ecad/tools/pcb_energy_chain.yaml"
MAINPB = "v2/docs/records/d8dec31/apply_gen_sch_a_mainpb.py"
CASES = "v2/docs/records/l8r2/inputs/coordinator-cases-2026-10-04-rev3.md"
L4E12_OUT = "v2/docs/records/l4e12/l4e12_thermal.out"
L9STK_PAGE = "v2/docs/records/l9stk/L9-STACKUPS.md"
ASSEMBLY = "v2/docs/ASSEMBLY.md"
IFACES = "v2/ecad/tools/pcb_interfaces.yaml"
DC_DROP = "v2/ecad/tools/dc_drop.py"
GEN_A = "v2/ecad/tools/gen_sch_a.py"
PACKRTN = "v2/docs/records/l8r2/apply_gen_sch_a_packrtn.py"
SHEETS = {"vh": "v2/vendor/connectors/jst-vh-catalogue.pdf", "cab": "v2/vendor/connectors/wurth-wr-cab-ribbon-63912615521cab.pdf",
          "xt_old": "v2/vendor/battery/amass-xt60-spec-tme.pdf", "xt_new": "v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf",
          "sock": "v2/vendor/connectors/wurth-wr-bhd-idc-socket-61202623021.pdf", "hdr": "v2/vendor/connectors/wurth-wr-bhd-box-header-61202621621.pdf"}
MINE = {"gndret": "v2/docs/records/l8r2/apply_gen_sch_b_gndret.py", "fandec": "v2/docs/records/l8r2/apply_gen_sch_b_fandec.py",
        "gndrtn": "v2/docs/records/l8r2/apply_gen_sch_b_gndrtn.py"}
MINE_A = {"gndrtn_a": "v2/docs/records/l8r2/apply_gen_sch_a_gndrtn.py"}
# board A's round in L4-E9's change-list order (records l8r2 rounds 1 to 6 and l9t5 compose it so): the power drafts, record l8gnd's
# two, this record's five, record l8p's ptc, L4-E11's dd7, then Layer 9's draft; d8dec31's mainpb LAST; Layer 6's table after it
ROUND_A = [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
           ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("l8r2", "packrtn"), ("l8r2", "slotlm"),
           ("l8r2", "fb01"), ("l8p", "ptc"), ("l4e11", "dd7")]
L6_A = "v2/docs/records/l6r2/apply_gen_sch_a_lcsc.py"
DRAFT = {"gnd002": "v2/docs/records/l8gnd/apply_gen_sch_b_gnd002.py", "fans12": "v2/docs/records/l8r2/apply_gen_sch_b_fans12.py",
         "panel5v": "v2/docs/records/l8r2/apply_gen_sch_b_panel5v.py", "ph4": "v2/docs/records/l8r2/apply_gen_sch_b_ph4.py",
         "rt500": "v2/docs/records/l8r2/apply_gen_sch_b_rt500.py", "iocbuck": L9T5_DRAFT,
         "xal_land": "v2/docs/records/l6r2/apply_gen_sch_b_xal_land.py", "lcsc": "v2/docs/records/l6r2/apply_gen_sch_b_lcsc.py",
         "intent": "v2/docs/records/l6r2/apply_gen_sch_b_intent.py", **MINE}
L6_HELP = ["v2/docs/records/l6r2/l6r2_apply.py", "v2/docs/records/l6r2/l6r2_land.py", "v2/docs/records/l6r2/l6r2_intent.py"]
ENGINE = ["v2/ecad/tools/kisch.py", "v2/ecad/tools/intent.py", "v2/ecad/tools/idc_pads.py", "v2/ecad/tools/track_current.py", DC_DROP, ENVELOPE, CHAIN,
          "v2/docs/records/l8p/gen_netlist.py", "v2/docs/records/l8r2/check_l8r2_netlist.py", "v2/docs/records/l8r2/check_gndret_netlist.py",
          "v2/docs/records/l8gnd/check_gnd002_netlist.py",
          "v2/docs/records/l8r2/l8r2_drafts.py"]
# the record's own order of board B's round (rounds 1 to 6, l8r2_drafts.py L8_B, and record l9t5's ORDER): the change list's three rows
# with this record's panel5v and ph4 (Layer 5's findings, no change-list row) between them; Layer 9's draft after the circuit
# drafts; Layer 6's land, table and declarations last
ROUND = ["gnd002", "fans12", "panel5v", "ph4", "rt500"]
L6 = ["xal_land", "lcsc", "intent"]
# the session's choices (authority: SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
T_RATED_RISE = 30.0     # K, ASSUMPTION: the temperature rise at the rated current that JST's 10 A stands for; the held catalogue prints none
CU_ALPHA = 0.00393      # 1/K, ASSUMPTION (ideal copper, as records cx1 and l4e11 take it; no held source)
AB2_MM = None           # J_AB2's ribbon length is TBD in its contract (IF-AB-WALL); taken as J_AB1's, ASSUMPTION
RET_LEAD_MM = None      # the dedicated return's lead length: taken as the 5 V leads' (ASSEMBLY.md section 4), ASSUMPTION until Layer 7 routes it
T_RATING_REF = 25.0     # C: the ambient a current rating is taken to be stated at where its sheet prints none (the ribbon's sheet prints 25 C)
BALLAST_MOHM = 1000.0   # section 3j's approaches D2 and D3: 1 Ohm in series with each ribbon ground conductor (an illustration)
WIRE_FLOOR = 0.82       # ASSUMPTION for section 6's wire sensitivity: a conductor's own wire at 0.82 of the modelled figure (the ribbon's
                        # maker prints a MAXIMUM, 237 Ohm/km; a 7 x 0.127 mm strand at the tree's resistivity is 194 Ohm/km, 0.82 of it)

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
    m = need(t, r"Operating Temperature\s+-(\d+) °C up to \+(\d+) °C", "the ribbon's operating range")
    F["cab_tmin"], F["cab_tmax"] = -float(m.group(1)), float(m.group(2))
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
    m = need(o, r"constant power, [\d.]+ W: ([\d.]+) A at U7's [\d.]+ V \(what leaves U7\) and ([\d.]+) A at U601's own least load voltage", "record l9t5's U601 on the case")
    F["cdev_u601_at_u7"], F["cdev_u601"] = float(m.group(1)), float(m.group(2))
    F["l9_loop_max"] = float(need(o, r"the loop's highest ([\d.]+) A stays under J_5V_DEV's VH 10 A", "record l9t5's loop maximum").group(1))
    m = need(o, r"high-side limit [\d.]+ / [\d.]+ / ([\d.]+) A, low-side\s+[\d.]+ / [\d.]+ / ([\d.]+) A \(PRINTED\)", "record l9t5's U601 limits")
    F["u601_hs"], F["u601_ls"] = float(m.group(1)), float(m.group(2))
    F["u601_out"] = float(need(o, r"the output at most about \([\d.]+ \+ [\d.]+\) / 2 = ([\d.]+) A", "record l9t5's U601 output bound").group(1))
    m = need(o, r"less the ground shift between the boards.*?: ([\d.]+) V, MODEL on PRINTED maxima\): ([\d.]+) V against the AP2112K-3\.3's need ([\d.]+) V",
             "record l9t5's LDO input chain", re.S)
    F["l9_shift_used"], F["l9_ldo_in"], F["l9_ldo_need"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    F["l9_shift_allow"] = float(need(o, r"the input holds while the ground shift between the boards stays under ([\d.]+) V", "record l9t5's ground shift allowance").group(1))
    # the collaborator's recheck V3, as filed: its corner, its total and its allowance (an AI review; each is reproduced or bettered here)
    v = text(V3)
    F["v3_total"] = float(need(v, r"the updated total return is ([\d.]+) A", "V3's total").group(1))
    F["v3_ioc"] = float(need(v, r"J_5V_IOC return is ([\d.]+) A", "V3's corner").group(1))
    F["v3_peak_lead"] = float(need(v, r"the omitted asymmetric-aged lead carries ([\d.]+) A", "V3's corner at the declared peak").group(1))
    F["v3_shift_allow"] = float(need(v, r"The corresponding ground-shift allowance is about ([\d.]+) V", "V3's ground shift allowance").group(1))
    need(v, r"T5 RECHECK: NOT CONFIRMED", "V3's verdict")
    # Amass XT60: the held V1.2 sheet (the pack connector's) and the 2021V1 sheet the distributor serves for the same part
    x = pdf("xt_old")
    cr = set(re.findall(r"XT60-[FM]\s+\u63a5\u89e6\u7535\u963b\s+([\d.]+)m", x)); rc = set(re.findall(r"\u989d\u5b9a\u7535\u6d41\s+(\d+)A", x))
    mc = set(re.findall(r"\u77ac\u65f6\u7535\u6d41\s+(\d+)A", x)); ut = set(re.findall(r"(\d+) TIMES", x)); aw = set(re.findall(r"\s(\d+)AWG", x))
    tr = set(re.findall(r"-(\d+)\S+ to (\d+)", x))
    if not all(len(s) == 1 for s in (cr, rc, mc, ut, aw, tr)) or len(re.findall(r"XT60-[FM]\s+\u63a5\u89e6\u7535\u963b", x)) != 2:
        refuse("the held Amass XT60 sheet (V1.2) no longer reads as one set of figures on its two pages")
    F["xt_r_old"], F["xt_a_old"], F["xt_a_mom"], F["xt_cycles_old"], F["xt_awg"] = float(cr.pop()), float(rc.pop()), float(mc.pop()), int(ut.pop()), int(aw.pop())
    lo, hi = tr.pop(); F["xt_tmin"], F["xt_tmax"] = -float(lo), float(hi)
    x = pdf("xt_new")
    need(x, r"2021V1", "the Amass XT60 sheet's version 2021V1")
    m = need(x, r"\u989d\u5b9a\u7535\u6d41\s+(\d+)A MAX\S(\d+)AWG/\S\S(\d+)", "the 2021V1 rated current row")
    F["xt_a_new"], awg_new, F["xt_rise"] = float(m.group(1)), int(m.group(2)), float(m.group(3))
    F["xt_r_new"] = float(need(x, r"\u63a5\u89e6\u7535\u963b\s+\u2264([\d.]+)m", "the 2021V1 contact resistance limit").group(1))
    F["xt_cycles_new"] = int(need(x, r"\u4f7f\u7528\u5bff\u547d\s+(\d+) ", "the 2021V1 service life").group(1))
    m = need(x, r"\u5de5\u4f5c\u6e29\u5ea6\s+-(\d+)\S+ to (\d+)", "the 2021V1 operating temperature")
    if awg_new != F["xt_awg"] or (-float(m.group(1)), float(m.group(2))) != (F["xt_tmin"], F["xt_tmax"]) or not ("XT60-F" in x and "XT60-M" in x):
        refuse("the two Amass XT60 sheets no longer agree on the wire gauge and the temperature range, or 2021V1 no longer names both halves")
    # the pack lead's conductor as the energy chain declares it: the same 12 AWG the return leads use
    ch = yaml.safe_load(text(CHAIN))
    stages = ch if isinstance(ch, list) else next(v for v in ch.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0])
    pl = [s for s in stages if s.get("id") == "PACK_LEAD"]
    if len(pl) != 1:
        refuse("pcb_energy_chain.yaml no longer carries one PACK_LEAD stage")
    m = need(str(pl[0]["conductor"]["what"]), r"^12 AWG \(([\d.]+) mm2\)", "the pack lead's 12 AWG section")
    F["mm2_12"], F["awg12_a"] = float(m.group(1)), float(pl[0]["conductor"]["rating_a"])
    # the envelope's cold end (ambient in use)
    env = yaml.safe_load(text(ENVELOPE))
    F["t_cold"] = float(env["ambient_c"]["in_use"]["min"])
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
                       kind="series" if kw.get("series_of") else "returns" if kw.get("returns") else "fed" if kw.get("fed_from") else None))
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


def run_gen(gen, board="b"):
    """One run of a generator copy as record l8p's gen_netlist.py runs it (its stand-in layout, the tree's kisch and intent), with
    every intent.rail call recorded BEFORE intent judges it: dict(stop, calls, table, netlist)."""
    with tempfile.TemporaryDirectory(prefix="l8r2_gnd_") as d:
        g = os.path.join(d, "gen_sch_%s.py" % board); shutil.copy(gen, g); prj = PROJECT[board]
        open(os.path.join(d, "l8p_stub_schlayout.py"), "w", encoding="utf-8").write(GN.STUB)
        open(os.path.join(d, "run.py"), "w", encoding="utf-8").write(RUNNER)
        js, dj = os.path.join(d, "parts.json"), os.path.join(d, "decl.json")
        env = dict(os.environ, PYTHONPATH=TOOLS, L8P_PARTS_JSON=js, L8R2_DECL_JSON=dj, KICAD_SYMBOLS=os.path.join(d, "no-kicad-symbols"),
                   PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, "-B", os.path.join(d, "run.py"), g, os.path.join(d, prj + ".kicad_sch"), prj],
                           capture_output=True, cwd=d, env=env)
        if not os.path.isfile(dj):
            refuse("a generator run died before its record was written: %s" % (r.stderr.decode("utf-8", "replace").strip().splitlines() or ["?"])[-1][:300])
        dec = json.load(open(dj, encoding="utf-8"))
        res = dict(stop=dec["stop"], calls=dec["calls"], table=None, netlist=None, intent=None)
        ij = os.path.join(d, "out", prj + "-intent.json")
        if dec["stop"] is None and os.path.isfile(js) and os.path.isfile(ij):
            res["table"] = json.load(open(js, encoding="utf-8"))
            res["intent"] = json.load(open(ij, encoding="utf-8"))
            res["netlist"] = GN.netlist(res["table"]).encode("utf-8")
    return res


def apply_p(path, target, flag="--write"):
    r = subprocess.run([sys.executable, "-B", path if os.path.isabs(path) else P(path), target, flag], capture_output=True)
    last = (r.stderr.decode("utf-8", "replace").strip().splitlines() or r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    return r.returncode, last


def apply(name, target, flag="--write"):
    return apply_p(DRAFT[name], target, flag)


def compose(seq, d, tag):
    p = os.path.join(d, tag + ".py"); shutil.copy(P(GEN_B), p)
    for s in seq:
        rc, msg = apply(s, p)
        if rc:
            return p, "%s REFUSED (%s)" % (s, msg)
    return p, None


def compose_a(paths, d, tag):
    """board A: the drafts in order, then d8dec31's mainpb (which takes the next free R and C against the committed netlist) LAST,
    then Layer 6's table"""
    p = os.path.join(d, tag + ".py"); shutil.copy(P(GEN["a"]), p)
    for s in paths:
        rc, msg = apply_p(s, p)
        if rc:
            return p, "%s REFUSED (%s)" % (os.path.basename(s), msg)
    r = subprocess.run([sys.executable, "-B", P(MAINPB), p, P(NET_A)], capture_output=True)
    if r.returncode:
        return p, "mainpb REFUSED (%s)" % (r.stderr.decode("utf-8", "replace").strip().splitlines() or r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    rc, msg = apply_p(L6_A, p)
    if rc:
        return p, "Layer 6's lcsc REFUSED (%s)" % msg
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


def conductors(F, T, ioc, n_ret=0, poe_awg=None, vh_ground=True, vh_open=0):
    """[(name, kind, n conductors, wire mOhm each)]: the ground conductors between boards A and B. ioc: Layer 9's sixth lead;
    n_ret: the dedicated return's conductors (two a lead: an XT60 contact, a 12 AWG conductor, an XT60 contact); poe_awg: the PoE
    lead's gauge (18 as drawn); vh_ground False takes the leads' pin 2 off the return (section 3j's third approach); vh_open: that
    many 5 V leads with pin 2 open (a fault case of section 6g)."""
    mm2 = {16: F["mm2_16"], 18: F["mm2_18"]}
    c = []
    if vh_ground:
        c = [("J_5V_S%d" % s, "VH", 1, r_wire(mm2[F["slot_awg"]], F["lead_mm"], T, F)) for s in (1, 2, 3)]
        c.append(("J_5V_DEV", "VH", 1, r_wire(mm2[F["dev_awg"]], F["lead_mm"], T, F)))
        if ioc:
            c.append(("J_5V_IOC", "VH", 1, r_wire(mm2[F["dev_awg"]], F["lead_mm"], T, F)))
        c = c[:len(c) - vh_open]
        awg = F["poe_awg"] if poe_awg is None else poe_awg
        c.append(("J_54V", "VH" if awg == 16 else "VH18", 1, r_wire(mm2[awg], F["lead_mm"], T, F)))
    c.append(("J_AB1", "RIB", 9, r_ribbon(F["ab1_mm"], T, F)))
    c.append(("J_AB2", "RIB", 8, r_ribbon(F["ab1_mm"] if AB2_MM is None else AB2_MM, T, F)))
    if n_ret:
        c.append(("J_GR", "RET", n_ret, r_wire(F["mm2_12"], F["lead_mm"] if RET_LEAD_MM is None else RET_LEAD_MM, T, F)))
    return c


def box(F, ret_hi=None, ballast=0.0):
    """{kind: (lo, hi)}: the contact resistance at EACH end of a conductor, mOhm. lo is the printed minimum where one is printed and
    zero where none is (none is, for any of these parts); hi is the after-test maximum (JST VH), the printed maximum (Wurth IDC) or
    the printed limit (Amass XT60, 2021V1, which prints no separate after-test figure; ret_hi overrides it to find how far a
    termination may age past it). ballast adds a series resistance to each ribbon conductor (half at each end, both lo and hi)."""
    return {"VH": (0.0, F["vh_rc1"]), "VH18": (0.0, F["vh_rc1"]), "RIB": (ballast / 2.0, F["sock_rc"] + ballast / 2.0),
            "RET": (0.0, F["xt_r_new"] if ret_hi is None else ret_hi)}


def classes_of(conds, bx):
    """conductors with one wire resistance and one box are interchangeable: [(names, kind, m, [g both lo, g one of each, g both hi])]"""
    cl = {}
    for n, kind, k, wres in conds:
        lo, hi = bx[kind]
        key = (kind if kind != "VH18" else "VH18", round(wres, 12), lo, hi)
        if key not in cl:
            cl[key] = dict(names=[], kind=kind, m=0, w=wres, lo=lo, hi=hi, g=[1.0 / (wres + 2 * lo), 1.0 / (wres + lo + hi), 1.0 / (wres + 2 * hi)])
        cl[key]["names"].append(n); cl[key]["m"] += k
    return list(cl.values())


def enumerate_vertices(total, C):
    """EVERY vertex of the contact-resistance box: each conductor has two contacts, each at its low or its high end. Conductors of a
    class are interchangeable, so a vertex is, per class, how many conductors have both contacts low (a) and how many one of each
    (b). For every such state the return's conductance and each class's largest conductor current are computed; returned per class:
    (the maximum over every vertex, the state it occurs at), then the largest ground shift (mV), the states visited and the raw
    vertices they stand for (4 to the power of the conductors)."""
    states = [[(a, b) for a in range(c["m"] + 1) for b in range(c["m"] + 1 - a)] for c in C]
    best = [(0.0, None)] * len(C); gmin = None; n = 0
    for st in itertools.product(*states):
        G = 0.0; top = []
        for (a, b), c in zip(st, C):
            g = c["g"]
            G += a * g[0] + b * g[1] + (c["m"] - a - b) * g[2]
            top.append(g[0] if a else (g[1] if b else g[2]))
        n += 1
        if gmin is None or G < gmin:
            gmin = G
        for i, g in enumerate(top):
            cur = total * g / G
            if cur > best[i][0]:
                best[i] = (cur, st)
    return best, total / gmin, n, 4 ** sum(c["m"] for c in C)


def analytic(total, C, wire_floor=1.0):
    """the same maxima from the monotone argument: a conductor's current rises as its own contacts fall and as every other contact
    rises, so its extreme is the vertex with its own two contacts low and every other contact high; the shift's is every contact high.
    wire_floor scales the conductor's OWN wire resistance (section 6d's sensitivity; 1.0 is the modelled figure)."""
    out = []
    for i, c in enumerate(C):
        g0 = 1.0 / (wire_floor * c["w"] + 2 * c["lo"])
        G = sum((cc["m"] - (1 if j == i else 0)) * cc["g"][2] for j, cc in enumerate(C)) + g0
        out.append(total * g0 / G)
    return out, total / sum(cc["m"] * cc["g"][2] for cc in C)


def extremes(total, conds, bx):
    """{kind: (maximum per conductor A, names)}, the largest ground shift mV, the states and the raw vertices: enumerated, and refused
    unless the enumeration agrees with the monotone argument and occurs at the vertex it names"""
    C = classes_of(conds, bx)
    best, shift, n, raw = enumerate_vertices(total, C)
    an, shift_a = analytic(total, C)
    for i, c in enumerate(C):
        want = tuple((1, 0) if j == i else (0, 0) for j in range(len(C)))
        if abs(best[i][0] - an[i]) > 1e-9 * max(1.0, an[i]) or (best[i][1] != want and c["g"][0] != c["g"][2]):
            refuse("the enumerated maximum of %s (%.6f A at %s) is not the monotone argument's vertex (%.6f A)" % (c["names"], best[i][0], best[i][1], an[i]))
    if abs(shift - shift_a) > 1e-9:
        refuse("the enumerated ground shift is not the all-high vertex's")
    out = {}
    for c, (cur, _st) in zip(C, best):
        k = c["kind"]
        if k in out:
            out[k] = (max(out[k][0], cur), out[k][1] + c["names"])
        else:
            out[k] = (cur, list(c["names"]))
    return out, shift, n, raw


def sampled_round7(total, conds, F):
    """round 7's six sampled cases (K0 to K5), kept as the old state the regression holds: {kind: the largest it found}"""
    v0, v1, i1 = F["vh_rc0"], F["vh_rc1"], F["sock_rc"]

    def mk(vh_r, idc_r, zero=None):
        return lambda n, k: 0.0 if n == zero else (vh_r if k in ("VH", "VH18") else idc_r)
    out = {}
    for rc in (mk(0.0, 0.0), mk(v0, i1), mk(v1, i1), mk(v0, i1, zero="J_5V_DEV"), mk(v0, 0.0), mk(v1, 0.0)):
        g = {n: k / (wres + 2.0 * rc(n, kind)) for n, kind, k, wres in conds}
        G = sum(g.values())
        for n, kind, k, _w in conds:
            out[kind] = max(out.get(kind, 0.0), total * g[n] / G / k)
    return out


def least_rating(printed, t_max, T, rise_at_rating=None):
    """the least current rating consistent with a sheet at air T: the part may add (t_max - T) K before its range's top; if its rise at
    the printed rating is rise_at_rating K (printed for the XT60; otherwise the whole span from T_RATING_REF to the range's top, the
    most severe reading the sheet allows) the rating falls with the square root of the rise left (heating as the current squared)"""
    span = (t_max - T_RATING_REF) if rise_at_rating is None else rise_at_rating
    return printed * min(1.0, math.sqrt(max(0.0, t_max - T) / span))


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
    w("l8r2_gndret.py: Layer 8 record l8r2, rounds 7 and 8: board B's ground return, its load basis and its current capacity reconciled\n"
      "(round 7, the owner's review of 4 October 2026, RSM-01), and the return between boards A and B corrected by a dedicated ground\n"
      "return and verified over every permitted aged-contact combination (round 8, finding L8R2-F31, after the collaborator's recheck\n"
      "V3, NOT CONFIRMED). PROTOTYPE DESIGN: nothing is built, bought, powered or measured; nothing here is applied to the tree; no\n"
      "figure is a measurement; no independent check has read round 8. Case rows cited (inputs/coordinator-cases-2026-10-04-rev3.md):\n"
      "C-DEV rev 1 for the device rail; C-ALLTX rev 3 where a state of it applies; the slots' loads per state as record l9pwr prints them.\n")
    w("\n0. INPUTS (sha256/16)\n")
    ins = [GEN_B, GEN_A, NET_A, NET_B, INT_B, L4E9_PAGE, BUDGET, L9T5_OUT, L9T5_DRAFT_A, V3, CASES, "v2/docs/records/l8r2/inputs/SOURCES.txt",
           L4E12_OUT, L9STK_PAGE, ASSEMBLY, IFACES, PACKRTN, MAINPB, L6_A] + ENGINE + sorted(set(DRAFT.values()) | set(MINE_A.values())) + L6_HELP \
        + sorted(SHEETS.values()) + ["v2/docs/records/%s/apply_gen_sch_a_%s.py" % rn for rn in ROUND_A]
    for p in ins:
        w("   %s %s\n" % (sha(p), p))
    w("   the session's choices (authority SESSION, each reversible by editing the constant and regenerating):\n"
      "     T_RATED_RISE %.0f K: round 7's reading of JST's %.0f A (a %.0f K rise at the rating; the held catalogue prints the range -40 to\n"
      "       +%.0f C 'including temperature rise in applying electrical current' and no rise, no ambient, no derating curve); shown beside the\n"
      "       stricter reading T_RATING_REF %.0f C (the rating taken at that ambient with the contact at its range's top); neither passes a row\n"
      "       that the printed rating fails\n"
      "     CU_ALPHA %.5f /K: ideal copper (ASSUMPTION, as records cx1 and l4e11); rho %.3g Ohm m is dc_drop.py's own (parsed)\n"
      "     J_AB2's ribbon at J_AB1's %.0f mm: its length is TBD in its contract IF-AB-WALL (ASSUMPTION)\n"
      "     the dedicated return's leads at the 5 V leads' %.0f mm (ASSUMPTION until Layer 7 routes them; a shorter lead lowers every row)\n"
      "     WIRE_FLOOR %.2f: section 6's sensitivity of a conductor's own wire resistance (ASSUMPTION; no wire part is named in the tree)\n"
      "     BALLAST_MOHM %.0f: the series resistance of approaches D2 and D3 in section 3j (an illustration)\n"
      % (T_RATED_RISE, F["vh_a16"], T_RATED_RISE, F["vh_tmax"], T_RATING_REF, CU_ALPHA, F["rho"], F["ab1_mm"], F["lead_mm"], WIRE_FLOOR, BALLAST_MOHM))

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
        seg = sorted({k for c in res5["calls"] if c["kind"] in ("series", "returns") for k in c["loads"] if k in gc["loads"]})
        conv = sorted({k for c in res5["calls"] if c["kind"] == "fed" for k in c["loads"] if k in gc["loads"]} - set(seg))
        if seg != ["J_PANEL", "J_QMX"] or conv != ["U3", "U4"]:
            refuse("the keys named twice (%s; %s) are not the ones section 2b judges" % (seg, conv))
        hd = [c for c in res5["calls"] if c["net"] == "+5V_HDMI"]
        w("    NAMED TWICE, each judged: %s are loads of a series segment of the device rail (PANEL_5V, VBUS_QMX), the same current further\n"
          "    along its own path, listed once in the return, where it comes back. %s are also loads of a rail this board converts (+3V3_DEV,\n"
          "    %.2f A each, inside U25's 5 V input); the return's entries at those two parts are the %.2f A allocation of the polyfuse F2\n"
          "    (+5V_HDMI) split in two, another branch's amperes. No ampere is in the return's list twice. (A LOCATION only: +5V_HDMI\n"
          "    declares its own load at %s, so that return comes back at the HDMI connector, not at the switches: finding L8R2-F37.)\n"
          % (" and ".join(seg), " and ".join(conv), call_of(res5, "+3V3_DEV")["loads"]["U3"], call_of(comp_res, "+5V_DEV")["loads"]["F2"],
             ", ".join(sorted(hd[0]["loads"])) if hd else "?"))
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
        pk5_c, pk5_i = pk_c - poe["peak"], pk_i - poe["peak"]          # the 5 V leads alone, for a like-for-like reading against the budget
        w("    (i) THE SUM OF THE LEADS' DECLARED PEAKS, an UPPER BOUND (every lead at its own peak at once): %.4f A (%.4f A) with the PoE\n"
          "        lead's %.2f A; %.2f A on the committed generator. The typicals sum to %.2f A (%.2f A). DECLARED.\n"
          % (pk_c, pk_i, poe["peak"], pk_0, ty_c, ty_i))
        bud = budget(BUDGET)
        w("    (ii) LAYER 9'S BUDGET (the copy of fnd/l9t5 at 841e6c7e, its rounds 4 to 6: PS-ALLTX with the standby card off; the ONE budget\n"
          "         this record reads since round 8): the four 5.1 V stages' output summed per state, before Layer 9's draft moves the\n"
          "         supervisors (MODEL, record l9pwr section 5b; the PoE stage is off in every state of that budget):\n")
        w("         %-28s %8s %8s %12s %14s %16s\n" % ("state", "PLAN", "HIGH", "HIGH least V", "+ one start", "+ every start"))
        bt = None
        for st, rows_ in bud.items():
            plan = sum(r["plan"] for r in rows_.values()); high = sum(r["high"] for r in rows_.values()); least = sum(r["least"] for r in rows_.values())
            adds = sorted((r["start"] - r["least"] for r in rows_.values() if r["start"] is not None), reverse=True)
            one = least + (adds[0] if adds else 0.0); allst = least + sum(adds)
            w("         %-28s %8.3f %8.3f %12.3f %14.3f %16.3f\n" % (st, plan, high, least, one, allst))
            if bt is None or least > bt[1]:
                bt = (st, least, high, plan, one, allst, rows_)
        rows = bud["PS-ALLTX"]                   # C-DEV rev 1's state: PS-ALLTX at HIGH at the least load voltage
        if abs(rows["DEV"]["least"] - F["cdev_u7_before"]) > 6e-4:
            refuse("the budget's PS-ALLTX device rail (%.3f A) is not record l9t5's figure before its draft (%.4f A)" % (rows["DEV"]["least"], F["cdev_u7_before"]))
        d_ioc = F["cdev_u601"] - F["cdev_u601_at_u7"]          # what the move adds to a state's total: U601's rail at its own least voltage
        tot_cdev = rows["S1"]["least"] + rows["S2"]["least"] + rows["S3"]["least"] + F["cdev_u7"] + F["cdev_u601"]
        tot_big = bt[1] + d_ioc; tot_big_starts = bt[5] + d_ioc
        w("         the largest state: %s, %.3f A at HIGH at the least load voltage (%.3f A at 5.1 V, %.3f A at PLAN); with one cooler's\n"
          "         bounded start %.3f A, with every running slot's at once %.3f A (the starts are 100 us averages, record l8r2 round 6)\n"
          % (bt[0], bt[1], bt[2], bt[3], bt[4], bt[5]))
        w("         WITH LAYER 9'S DRAFT COMPOSED (record l9t5 round 3, MODEL): the supervisors' %.4f A leaves U7 and U601 carries %.4f A at its\n"
          "         own least load voltage, %+.4f A on a state's total: the largest state %.4f A (%.4f A with every start); on C-DEV rev 1\n"
          "         (PS-ALLTX, HIGH, the least load voltage) U7 %.4f A and U601 %.4f A, total %.4f A (the recheck V3 prints %.6f A from the\n"
          "         budget's unrounded figures)\n"
          % (F["cdev_u601_at_u7"], F["cdev_u601"], d_ioc, tot_big, tot_big_starts, F["cdev_u7"], F["cdev_u601"], tot_cdev, F["v3_total"]))
        if abs(tot_cdev - F["v3_total"]) > 2e-3:
            refuse("C-DEV rev 1's total (%.4f A) is not the recheck's (%.6f A)" % (tot_cdev, F["v3_total"]))
        n_lm = 4
        src_c = n_lm * F["loop_max"]; src_i = src_c + F["u601_out"]
        w("    (iii) WHAT THE SOURCES CAN DELIVER (a fault bound): each LM5176 5.1 V stage's average loop limits between %.4f and %.4f A (VSNS\n"
          "         %.0f to %.0f mV PRINTED, SNVSAI1D, over the 6 mOhm shunt at 1 %%, DECLARED; record l9t5 prints %.4f A); with this record's\n"
          "         slotlm draft all four leads are such stages: %d x %.3f = %.2f A (with Layer 9's U601 at its output bound %.2f A: %.2f A).\n"
          "         One stage in its limit with the others at the largest state: %.3f A.\n"
          % (F["loop_min"], F["loop_max"], R6.V["vsns"][0] * 1e3, R6.V["vsns"][2] * 1e3, F["l9_loop_max"], n_lm, F["loop_max"], src_c, F["u601_out"], src_i,
             bt[1] - max(r["least"] for r in bt[6].values()) + F["loop_max"]))
        dev_big = bt[6]["DEV"]["least"]
        w("    WHICH ONE THE DECLARATION HOLDS, AND WHY: the peak holds (i), named an upper bound in its note; the typical holds the sum of the\n"
          "    leads' typicals; the loads stay the union of the leads' allocations, with the PoE return added.\n"
          "      - (i) is the only figure that is true by construction: the return cannot carry more than its leads are declared to carry,\n"
          "        and those declarations are Layer 5's contract at both ends of each lead. Derived in the generator, it follows a lead\n"
          "        that is declared again; typed, it went stale on 28 September (S-98) and again with fans12.\n"
          "      - (ii) against (i), like for like (the PoE stage is off in the budget, so the 5 V leads alone): with Layer 9's draft composed\n"
          "        the largest state with every start at once is %.3f A against %.4f A: %s. Without that draft it is %.3f A against\n"
          "        %.2f A: %s by %.3f A, because the device lead declares %.1f A where the budget has %.3f A in that state (%.4f A on\n"
          "        C-DEV rev 1). That is I-03 itself (OPEN, Layer 9's): the return follows what that lead declares and does not paper over it.\n"
          "      - (iii) is a fault current of four independent limits at once; intent.py's own rule puts a fault current in the note,\n"
          "        not in the peak (the barrel rule PI-003 reads the peak). One stage in its limit is inside (i).\n"
          "      - what the peak is NOT: a claim that %.2f A flows. The copper rules solve the return's mesh at the declared loads,\n"
          "        %.3f A with the PoE return; the peak is what a barrel is judged at.\n"
          % (tot_big_starts, pk5_i, "inside" if tot_big_starts <= pk5_i else "OVER", bt[5], pk5_c, "inside" if bt[5] <= pk5_c else "OVER", abs(bt[5] - pk5_c),
             call_of(comp_res, "+5V_DEV")["peak"], dev_big, F["cdev_u7_before"], pk_i, sum(gc["loads"].values()) + poe["peak"]))

        # ---------------------------------------------------------------- 3
        w("\n3. THE CAPACITY BASIS AS DRAWN\n")
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
        TH, TL = F["t_e5"], F["t_cold"]
        vh_assume = F["vh_a16"] * min(1.0, math.sqrt((F["vh_tmax"] - TH) / T_RATED_RISE))
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
          "        effect at higher temperatures' with no curve, operating to +%.0f C, 'the operating temperature is comprised of ambient\n"
          "        temperature and temperature rise of the component' (PRINTED); conductor resistance %.0f Ohm/km maximum, AWG %d (PRINTED).\n"
          "      Wurth WR-BHD IDC socket (%s): %.0f A a contact, contact resistance %.0f mOhm maximum, NO MINIMUM (PRINTED). Box header: %.0f A at 25 C.\n"
          % (SHEETS["cab"], F["cab_a"], F["cab_tmax"], F["cab_ohm_km"], F["cab_awg"], SHEETS["sock"], F["sock_a"], F["sock_rc"], F["hdr_a"]))
        w("      Amass XT60 (the pack connector's make, J_BATT on board E; XT60-F and XT60-M). The held specification V1.2 (%s):\n"
          "        rated current %.0f A, momentary %.0f A, contact resistance %.2f mOhm (no limit sign), %d AWG, %d uses, %.0f to %.0f C (PRINTED).\n"
          "        The specification 2021V1 the distributor serves for the same part (%s, filed this round):\n"
          "        %.0f A MAX with %d AWG at a temperature rise under %.0f C, contact resistance at most %.1f mOhm, service life %d times, the same\n"
          "        range (PRINTED). Neither prints a contact resistance after test, a minimum or a derating curve. The rows below take the\n"
          "        LOWER rated current (%.0f A), the HIGHER contact resistance (%.1f mOhm, a printed limit, taken as the contact's maximum over\n"
          "        its printed life: INFERRED, the sheet does not say so) and the SHORTER life.\n"
          % (SHEETS["xt_old"], F["xt_a_old"], F["xt_a_mom"], F["xt_r_old"], F["xt_awg"], F["xt_cycles_old"], F["xt_tmin"], F["xt_tmax"], SHEETS["xt_new"],
             F["xt_a_new"], F["xt_awg"], F["xt_rise"], F["xt_r_new"], F["xt_cycles_new"], min(F["xt_a_old"], F["xt_a_new"]), max(F["xt_r_old"], F["xt_r_new"])))
        w("      THE COPPER'S TEMPERATURE, both ends: %.2f C, the inside air in E5's dwell (L4-E12, MODELED; %.2f C in E3-O), and %.0f C, the\n"
          "        envelope's cold end in use (%s ambient_c.in_use.min: the harness at ambient at a cold start). A conductor's largest\n"
          "        share falls as the copper warms (its own resistance is copper, the others' is mostly contact) and the ground shift rises:\n"
          "        each maximum is at one end, so both ends are enumerated. The budget's largest states at either end are conservative pairings.\n"
          % (TH, F["t_e3o"], TL, ENVELOPE))
        w("      THE RATINGS AT THE INSIDE AIR. No maker here prints a derating curve. Beside each PRINTED rating the rows carry the LEAST\n"
          "        rating consistent with its sheet at that air (INFERRED): the part may add (range top - air) K, and heating goes as the\n"
          "        current squared (ASSUMPTION). The ribbon: its %.0f A is printed at 25 C and its range ends at +%.0f C, so its rise at %.0f A is\n"
          "        at most %.0f K and at %.2f C it carries at least %.4f A. The XT60: %.0f A at a rise under %.0f K and a range to %.0f C give\n"
          "        %.2f A at %.2f C. The VH: no ambient is printed for its %.0f A; taken at %.0f C (ASSUMPTION) the same rule gives %.3f A (with a\n"
          "        %.0f K rise at the rating, round 7's ASSUMPTION, %.3f A). At the cold end every printed rating applies as printed.\n"
          % (F["cab_a"], F["cab_tmax"], F["cab_a"], F["cab_tmax"] - T_RATING_REF, TH, least_rating(F["cab_a"], F["cab_tmax"], TH),
             F["xt_a_new"], F["xt_rise"], F["xt_tmax"], least_rating(F["xt_a_new"], F["xt_tmax"], TH, F["xt_rise"]), TH,
             F["vh_a16"], T_RATING_REF, least_rating(F["vh_a16"], F["vh_tmax"], TH), T_RATED_RISE, vh_assume))
        allow = min(F["l9_shift_allow"], F["v3_shift_allow"])
        w("      THE GROUND SHIFT LAYER 9'S LDOS ALLOW: record l9t5 (round 3, the copy) prints the LDOs' input %.4f V against the AP2112K's need\n"
          "        %.3f V with %.4f V of shift taken, and holds 'while the ground shift between the boards stays under %.3f V'; the recheck V3\n"
          "        adds the regulator's line and load regulation and prints about %.4f V. The rows below are judged at the smaller, %.4f V.\n"
          % (F["l9_ldo_in"], F["l9_ldo_need"], F["l9_shift_used"], F["l9_shift_allow"], F["v3_shift_allow"], allow))

        def rating(kind, Tx):
            """(printed A or None, least A consistent with the sheet at air Tx, the part)"""
            if kind == "VH":
                return F["vh_a16"], least_rating(F["vh_a16"], F["vh_tmax"], Tx), "a VH pin 2 with AWG 16"
            if kind == "VH18":
                return None, None, "J_54V's pin 2 with AWG 18"
            if kind == "RIB":
                return F["cab_a"], least_rating(F["cab_a"], F["cab_tmax"], Tx), "a ribbon conductor"
            pr = min(F["xt_a_old"], F["xt_a_new"])
            return pr, min(pr, least_rating(F["xt_a_new"], F["xt_tmax"], Tx, F["xt_rise"])), "an XT60 contact and its 12 AWG conductor"

        def verdict(cur, kind, Tx):
            pr, le, _what = rating(kind, Tx)
            if pr is None:
                return "NO RATING PRINTED"
            if cur <= le + 1e-12:
                return "HOLDS"
            return "holds on the printed rating, NOT on the least at this air" if cur <= pr + 1e-12 else "DOES NOT HOLD"

        w("3c. THE CONDUCTORS' RESISTANCE (MODEL: rho %.3g Ohm m at 20 C from dc_drop.py; the JST catalogue's sections; 12 AWG at %.2f mm2\n"
          "    from the energy chain's pack lead row; %.0f mm leads and the %.0f mm ribbon from ASSEMBLY.md section 4; mOhm a conductor):\n"
          % (F["rho"], F["mm2_12"], F["lead_mm"], F["ab1_mm"]))
        cC, cH = conductors(F, TL, True, 2), conductors(F, TH, True, 2)
        for (n, kind, k, rc_), (_n, _k, _kk, rh_) in zip(cC, cH):
            lo, hi = box(F)[kind]
            w("      %-9s %-6s %2s  %7.3f at %.0f C, %7.3f at %.2f C; each of its two contacts 0 to %.1f mOhm%s\n"
              % ({"J_GR": "J_GR1.."}.get(n, n), {"VH": "AWG%d" % F["slot_awg"], "VH18": "AWG%d" % F["poe_awg"], "RIB": "AWG%d" % F["cab_awg"], "RET": "AWG%d" % F["xt_awg"]}[kind],
                 "x%d" % k if kind == "RIB" else ("x2 a lead" if kind == "RET" else ""), rc_, TL, rh_, TH, hi,
                 {"RIB": " (the wire's figure is its maker's maximum)", "RET": " (round 8's dedicated return, section 3j)"}.get(kind, "")))
        w("      a lead's two contacts may add up to %.0f mOhm after test, sixteen to twenty-three times the lead itself: the division between\n"
          "      the leads is set by the contacts, which the maker bounds from above only.\n" % (2 * F["vh_rc1"]))

        # the three totals, on the merged figures, with Layer 9's sixth lead
        totals = [("C-DEV rev 1 (PS-ALLTX, HIGH, the least load voltage) with Layer 9's draft", tot_cdev),
                  ("the largest state of Layer 9's budget (%s, HIGH, the least load voltage) with Layer 9's draft" % bt[0], tot_big),
                  ("the declared upper bound (i) with Layer 9's draft", pk_i)]
        TEMPS = [(TH, "%.2f C" % TH), (TL, "%.0f C" % TL)]
        w("3d. THE RETURN DIVIDED BY RESISTANCE AS DRAWN, THE WORST CASE FOUND (MODEL; six leads, J_54V at AWG %d, seventeen ribbon conductors,\n"
          "    no dedicated return). Each conductor's current is largest at a vertex of the box of contact resistances (every contact at 0\n"
          "    or at its after-test or printed maximum), so EVERY vertex is enumerated for every conductor and the largest kept; the\n"
          "    enumeration is refused unless it lands on the vertex the monotone argument names (the conductor's own two contacts low,\n"
          "    every other contact high). A per conductor; the largest ground shift is the vertex with every contact high.\n" % F["poe_awg"])
        w("      %-30s %-8s %24s %22s %24s %10s %s\n" % ("total", "copper", "a 5 V lead's pin 2", "J_54V's pin 2", "a ribbon conductor", "shift mV", "vertices"))
        DR = {}
        for ti, (tag, tot) in enumerate(totals):
            for Tx, tl in TEMPS:
                ext, shift, nst, raw = extremes(tot, conductors(F, Tx, True), box(F)); DR[(ti, Tx)] = (ext, shift)
                w("      %-30s %-8s %8.4f %-15s %8.4f %-13s %8.4f %-15s %10.2f %d states = 4^%d\n"
                  % ("%.4f A" % tot, tl, ext["VH"][0], verdict(ext["VH"][0], "VH", Tx)[:15], ext["VH18"][0], "no rating", ext["RIB"][0], verdict(ext["RIB"][0], "RIB", Tx)[:15],
                     shift, nst, round(math.log(raw, 4))))
        for ti, (tag, tot) in enumerate(totals):
            w("      %.4f A: %s\n" % (tot, tag))
        v3_here = DR[(0, TH)][0]["VH"][0]; v3_peak = DR[(2, TH)][0]["VH"][0]
        w("    THE RECHECK'S CORNER, REPRODUCED: on C-DEV rev 1 at %.2f C, J_5V_IOC's two contacts at 0 with every other VH contact at %.0f mOhm\n"
          "    and every IDC contact at %.0f mOhm: %.4f A in its pin 2 (V3: %.4f A), over the printed %.0f A; at the declared upper bound %.4f A\n"
          "    (V3: %.4f A). It is the same vertex for each 5 V lead: they are one make. At %.0f C the same corner reads %.4f A.\n"
          % (TH, F["vh_rc1"], F["sock_rc"], v3_here, F["v3_ioc"], F["vh_a16"], v3_peak, F["v3_peak_lead"], TL, DR[(0, TL)][0]["VH"][0]))
        if abs(v3_here - F["v3_ioc"]) > 2e-3 or abs(v3_peak - F["v3_peak_lead"]) > 2e-3:
            refuse("the enumeration does not reproduce the recheck's corner")
        drawn_over = sorted({(k, ti) for (ti, Tx), (ext, _s) in DR.items() for k in ("VH", "RIB") if ext[k][0] > rating(k, Tx)[0]})
        w("    READ: as drawn, over the contact resistances the makers permit, a 5 V lead's pin 2 reaches %.3f A against its printed %.0f A and\n"
          "    a ribbon conductor %.3f A against its printed %.0f A, on C-DEV rev 1 already (the worse copper end of each): DOES NOT HOLD.\n"
          % (max(DR[(0, Tx)][0]["VH"][0] for Tx, _l in TEMPS), F["vh_a16"], max(DR[(0, Tx)][0]["RIB"][0] for Tx, _l in TEMPS), F["cab_a"]))
        w("3e. WHAT ROUND 7'S SAMPLING MISSED (the old state; the recheck's material blocker). Round 7 took six cases (K0 to K5): every contact\n"
          "    at one value, ONE lead low against peers at the INITIAL maximum, and every IDC contact low together. At %.2f C:\n" % TH)
        missed = []
        for ti, (tag, tot) in enumerate(totals):
            old = sampled_round7(tot, conductors(F, TH, True), F); new = DR[(ti, TH)][0]
            missed.append((old, new))
            w("      %.4f A: a 5 V lead's pin 2: sampled %.4f A, the maximum %.4f A; a ribbon conductor: sampled %.4f A, the maximum %.4f A;\n"
              "        J_54V's pin 2: sampled %.4f A, the maximum %.4f A\n"
              % (tot, old["VH"], new["VH"][0], old["RIB"], new["RIB"][0], old["VH18"], new["VH18"][0]))
        w("    The sampled list had no vertex with one lead low against peers at the AFTER-TEST maximum, and none with ONE ribbon conductor low\n"
          "    against every other contact high (its K4 and K5 put all seventeen low at once, which shares the current among them). The\n"
          "    'maximum' it printed was not a maximum: round 7's 3d, 3e and 3j and Layer 9's acceptance of J_5V_IOC's pin 2 on it are WITHDRAWN.\n")

        vh_least = least_rating(F["vh_a16"], F["vh_tmax"], TH)
        w("3f. THE SUPPLY PINS (pin 1 carries its own rail and nothing else). Rating: PRINTED %.0f A with AWG 16 on the standard header; at\n"
          "    %.2f C at least %.4f A if the rating is stated at %.0f C (ASSUMPTION, the severest reading of a sheet that prints no ambient and\n"
          "    no derating), %.3f A on round 7's %.0f K rise (ASSUMPTION):\n" % (F["vh_a16"], TH, vh_least, T_RATING_REF, vh_assume, T_RATED_RISE))
        pin1_rows = [("J_5V_S1", rows["S1"]["least"]), ("J_5V_S2", rows["S2"]["least"]), ("J_5V_S3", max(rows["S3"]["least"], bt[6]["S3"]["least"])),
                     ("J_5V_DEV", F["cdev_u7"]), ("J_5V_IOC", F["cdev_u601"])]
        pin1_over = []
        for n_, cur in pin1_rows:
            vd = "inside the printed rating and the least" if cur <= vh_least else ("inside the printed rating; OVER the severest least reading by %.4f A" % (cur - vh_least) if cur <= F["vh_a16"] else "OVER the printed rating")
            if cur > vh_least:
                pin1_over.append(n_)
            w("      %-9s pin 1: %.4f A steady at HIGH at the least load voltage (C-DEV rev 1 or the largest state, the larger): %s\n" % (n_, cur, vd))
        w("      the slots' bounded starts (%.3f A, a 100 us average, record l8r2 round 6) and declared peaks (%.1f A) are transients inside the\n"
          "      printed %.0f A; the device stage's loop can hold up to %.4f A in a fault, under the printed %.0f A; as committed (no Layer 9 draft)\n"
          "      J_5V_DEV's pin 1 carries %.4f A on C-DEV rev 1 (I-03, OPEN, Layer 9's). J_54V pin 1: %.2f A peak on AWG %d: NO RATING PRINTED\n"
          "      (%.0f A for the shrouded header, a comparator).\n"
          % (max(r["start"] for r in bt[6].values() if r["start"]), call_of(comp_res, "+5V_S1")["peak"], F["vh_a16"], F["loop_max"], F["vh_a16"],
             F["cdev_u7_before"], poe["peak"], F["poe_awg"], F["vh_a18"]))
        w("      THE LEAD: AWG %d, %.0f mm; JST's %.0f A is stated for the crimped contact WITH that gauge, so it is the lead's rating too. The wire\n"
          "      itself (its part, its insulation's temperature class) is named nowhere in the tree: OWED to Layer 7 (finding L8R2-F34).\n"
          % (F["slot_awg"], F["lead_mm"], F["vh_a16"]))
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
          "    round proposes are in the record's section 3g (Layer 5's files are its own).\n"
          % (IFACES, " ".join(str(ifp.get("harness")).split()), ifp.get("pins_each"), F["vh_a16"], "a row" if says_return else "NO ROW", F["sock_a"]))
        # ---- 3j: the corrections compared
        def design(n_ret, poe_awg=16, ballast=0.0, vh_ground=True, ret_hi=None, tot_list=None, enum=False, vh_open=0, wire_floor=1.0):
            """rows of a design over a list of totals (the three of 3d unless given) and both copper ends: [(index of the total, T, kind,
            names, current, printed, least, verdict)], the largest ground shift, and whether every row with a printed rating holds on it
            and on the least rating. enum: every vertex enumerated (extremes); otherwise the monotone argument's vertex (the same
            figure, which extremes() itself refuses to differ from)."""
            out, smax = [], 0.0
            for ti, (_tg, tot_) in enumerate(totals if tot_list is None else tot_list):
                for Tx, _tl in TEMPS:
                    conds = conductors(F, Tx, True, n_ret, poe_awg, vh_ground, vh_open); bx = box(F, ret_hi, ballast)
                    if enum:
                        ext, shift, _n, _raw = extremes(tot_, conds, bx)
                    else:
                        C = classes_of(conds, bx); an, shift = analytic(tot_, C, wire_floor); ext = {}
                        for c, cur in zip(C, an):
                            ext[c["kind"]] = (max(ext.get(c["kind"], (0.0, []))[0], cur), ext.get(c["kind"], (0.0, []))[1] + c["names"])
                    smax = max(smax, shift)
                    for kind in ("VH", "VH18", "RIB", "RET"):
                        if kind in ext:
                            pr, le, _wh = rating(kind, Tx)
                            out.append((ti, Tx, kind, ext[kind][1], ext[kind][0], pr, le, verdict(ext[kind][0], kind, Tx)))
            rated = [r for r in out if r[5] is not None]
            return dict(rows=out, shift=smax, printed=all(r[4] <= r[5] + 1e-12 for r in rated) and smax <= allow * 1e3,
                        least=all(r[4] <= r[6] + 1e-12 for r in rated) and smax <= allow * 1e3, unrated=[r for r in out if r[5] is None])

        def worst(dg, kind, ti=None, Tx=None):
            r = [x[4] for x in dg["rows"] if x[2] == kind and (ti is None or x[0] == ti) and (Tx is None or x[1] == Tx)]
            return max(r) if r else 0.0
        N_DRAFT = {n: importlib.util.spec_from_file_location("gr_" + n, P(pth)) for n, pth in (("b", MINE["gndrtn"]), ("a", MINE_A["gndrtn_a"]))}
        n_drafted = {}
        for n, sp_ in N_DRAFT.items():
            md = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(md); n_drafted[n] = md.N_RETURN
        w("3j. THE CORRECTIONS COMPARED (three approaches; every row is a conductor's maximum over every vertex, at both copper ends, on C-DEV\n"
          "    rev 1, the largest state and the declared upper bound; J_54V's lead at AWG 16 in each, so that its pin 2 has a printed rating):\n")
        w("    D1 A DEDICATED GROUND RETURN between the two boards' grounds: n conductors, two a lead; a lead is an Amass XT60 pair with both\n"
          "       contacts on GND and two %d AWG conductors of %.0f mm; each termination from 0 to the printed %.1f mOhm:\n"
          % (F["xt_awg"], F["lead_mm"] if RET_LEAD_MM is None else RET_LEAD_MM, F["xt_r_new"]))
        w("       %-12s %12s %14s %16s %10s  %s\n" % ("conductors", "a VH pin 2", "a ribbon", "an XT60 contact", "shift mV", "every row holds"))
        D1 = {}
        for n in (0, 2, 4, 6, 8):
            D1[n] = design(n)
            w("       %-12s %10.3f A %12.3f A %14.3f A %10.2f  on the printed ratings: %s; on the least ratings at the inside air: %s\n"
              % ("%d (%d lead%s)" % (n, n // 2, "" if n == 2 else "s") if n else "none (as drawn)", worst(D1[n], "VH"), worst(D1[n], "RIB"), worst(D1[n], "RET"), D1[n]["shift"],
                 "yes" if D1[n]["printed"] else "NO", "yes" if D1[n]["least"] else "NO"))
        n_printed = min((n for n in (2, 4, 6, 8) if D1[n]["printed"]), default=None); n_least = min((n for n in (2, 4, 6, 8) if D1[n]["least"]), default=None)
        if n_printed is None or n_least is None:
            refuse("no dedicated return of up to four leads holds every row: section 3j cannot select D1")
        D2 = design(2, ballast=BALLAST_MOHM); D3 = design(2, ballast=BALLAST_MOHM, vh_ground=False)
        w("    D2 ONE RETURN LEAD AND THE RIBBONS' GROUND CONDUCTORS BALLASTED (%.0f Ohm in series with each, a resistor's printed tolerance being a\n"
          "       printed minimum): a VH pin 2 %.3f A, a ribbon conductor %.3f A, an XT60 contact %.3f A, shift %.2f mV; every row on the printed\n"
          "       ratings: %s; on the least ratings: %s. Thirty-four more parts on a board and an impedance in every ribbon signal's return\n"
          "       (RET-001 to RET-003 re-read) for one lead fewer than D1: REJECTED.\n"
          % (BALLAST_MOHM / 1000.0, worst(D2, "VH"), worst(D2, "RIB"), worst(D2, "RET"), D2["shift"], "yes" if D2["printed"] else "NO", "yes" if D2["least"] else "NO"))
        w("    D3 ONE RETURN LEAD AS THE ONLY RETURN (the VH leads' pin 2 taken off the ground, the ribbons ballasted as D2): an XT60 contact\n"
          "       %.3f A, a ribbon conductor %.3f A, shift %.2f mV; every row on the printed ratings: %s; on the least ratings: %s. No VH contact\n"
          "       is left in the return, but every rail's return leaves its supply lead (the loops the leads' pairs close are opened), and one\n"
          "       open return lead puts the whole return on the ballasted ribbons: REJECTED.\n"
          % (worst(D3, "RET"), worst(D3, "RIB"), D3["shift"], "yes" if D3["printed"] else "NO", "yes" if D3["least"] else "NO"))
        w("    SELECTED (authority SESSION): D1 with %d conductors, %d leads. %d conductors (%d leads) are the least that hold every row on the\n"
          "       makers' printed ratings; %d (%d leads) are the least that also hold every row at the inside air on the least rating\n"
          "       consistent with each sheet, where no maker prints a derating curve, and they keep every printed-rating row with one lead\n"
          "       unmated (section 6). Reason: the design is then indifferent to the unprinted derating, to the VH and IDC contact\n"
          "       resistances, and to one lead. DRAFTED this round on boards A and B (section 5): %d sockets a board. To reverse: drop a\n"
          "       socket in both drafts (N_RETURN) and regenerate; the rows of section 6 then say what no longer holds.\n"
          % (n_least, n_least // 2, n_printed, n_printed // 2, n_least, n_least // 2, n_drafted["b"]))
        if not (n_drafted["a"] == n_drafted["b"] == n_least // 2):
            refuse("the drafts draw %s sockets a board and the selection is %d leads" % (n_drafted, n_least // 2))
        SEL = D1[n_least]

        # ---------------------------------------------------------------- 4
        w("\n4. THE JUDGMENT\n")
        w("   (a) THE DECLARATION IS WRONG, and is corrected (round 7, section 5). Its peak was a typed sum of the leads' peaks that went stale\n"
          "       twice; its typical %.1f A is under the leads' own %.2f A; its sources omit J_54V. The basis supports: typical %.2f A and peak\n"
          "       %.2f A (%.4f A with Layer 9's draft), derived in the generator from the leads' declarations, the peak an UPPER BOUND.\n"
          % (by["rt500"][1]["typ"], ty_c, ty_c, pk_c, pk_i))
        w("   (b) THE LOAD LIST IS RIGHT IN WHAT IT COUNTS AND MISSED ONE RETURN: no ampere is counted twice and none returns elsewhere; the PoE\n"
          "       port's %.2f A at R12 is added. The device rail's shortfall against C-DEV rev 1 is I-03 (Layer 9's draft, which now declares\n"
          "       the device lead's peak from its basis, %.4f A).\n" % (poe["peak"], F["cdev_u7"]))
        w("   (c) THE RETURN PATH AS DRAWN DOES NOT HOLD: a circuit defect of the A to B interface, finding L8R2-F31, OPEN. With every vertex of\n"
          "       the permitted contact resistances enumerated (round 7 had sampled six and missed the worst), on C-DEV rev 1 a 5 V lead's pin 2\n"
          "       reaches %.3f A against its printed %.0f A and a ribbon conductor %.3f A against its printed %.0f A (3d). These are the MODEL's\n"
          "       answers on the makers' printed limits: no harness exists and no contact has been measured.\n"
          "   (d) THE CORRECTION IS DRAFTED, NOT ACCEPTED: a dedicated ground return of %d XT60 leads (%d conductors of %d AWG) between the two\n"
          "       boards, drawn on both generators (section 5) and verified over every vertex with its own terminations at their printed\n"
          "       limit (section 6), on the declared upper bound: a VH pin 2 at most %.3f A against JST's printed %.0f A (AWG 16, standard\n"
          "       header); a ribbon conductor at most %.3f A against Wurth's printed %.0f A at 25 C (%.3f A at the inside air against at least\n"
          "       %.4f A there, INFERRED); an XT60 contact at most %.3f A against Amass's printed %.0f A (V1.2) and %.0f A MAX with %d AWG at a\n"
          "       rise under %.0f C (2021V1), at least %.2f A at the inside air (INFERRED); the ground shift at most %.2f mV against %.4f V.\n"
          "       L8R2-F31 STAYS OPEN until an independent check has read the changed design; what the rows rest on that no maker prints\n"
          "       is listed in 6d and is not hidden by this arithmetic.\n"
          "   NOT RAISED TO MAKE THE GENERATOR PASS: the declaration is derived, the same text reads %.2f A on the committed generator, a lead\n"
          "       declared lower lowers it.\n"
          % (max(DR[(0, Tx)][0]["VH"][0] for Tx, _l in TEMPS), F["vh_a16"], max(DR[(0, Tx)][0]["RIB"][0] for Tx, _l in TEMPS), F["cab_a"],
             n_least // 2, n_least, F["xt_awg"], worst(SEL, "VH"), F["vh_a16"], worst(SEL, "RIB"), F["cab_a"], worst(SEL, "RIB", Tx=TH),
             least_rating(F["cab_a"], F["cab_tmax"], TH), worst(SEL, "RET"), F["xt_a_old"], F["xt_a_new"], F["xt_awg"], F["xt_rise"],
             least_rating(F["xt_a_new"], F["xt_tmax"], TH, F["xt_rise"]), SEL["shift"], allow, pk_0))

        # ---------------------------------------------------------------- 5
        w("\n5. THE DRAFTS (four, release-guarded, on scratch copies)\n")
        ok_guard = True
        for name, board, pre in (("gndret", "b", []), ("fandec", "b", []), ("gndrtn", "b", ["gndret"]), ("gndrtn_a", "a", [])):
            pth_d = dict(MINE, **MINE_A)[name]
            t = os.path.join(d, "g_%s.py" % name); shutil.copy(P(GEN[board]), t)
            for pre_ in pre:
                if apply(pre_, t)[0]:
                    refuse("%s refused a copy ahead of %s" % (pre_, name))
            before = open(t, "rb").read()
            c_rc, c_msg = apply_p(pth_d, t, "--check"); same = open(t, "rb").read() == before
            w_rc, w_msg = apply_p(pth_d, t); a_ok = True
            try:
                ast.parse(open(t, encoding="utf-8").read())
            except SyntaxError:
                a_ok = False
            r_rc, r_msg = apply_p(pth_d, t); t_rc, t_msg = apply_p(pth_d, P(GEN[board]))
            good = (c_rc, same, w_rc, a_ok, r_rc, t_rc) == (0, True, 0, True, 3, 3)
            ok_guard = ok_guard and good
            w("   %s sha256 %s (board %s%s)\n     --check exit %d (target unchanged: %s); --write exit %d (parses: %s); a second --write exit %d (%s);\n"
              "     on the tree's own generator exit %d (%s)\n"
              % (pth_d, sha(pth_d), board.upper(), ", after gndret" if pre else "", c_rc, "yes" if same else "NO", w_rc, "yes" if a_ok else "NO", r_rc, short(r_msg, 90), t_rc, short(t_msg, 110)))
        t = os.path.join(d, "g_noret.py"); shutil.copy(P(GEN_B), t); o_rc, o_msg = apply("gndrtn", t)
        w("   the board B return draft on a generator WITHOUT gndret: exit %d (%s)\n" % (o_rc, short(o_msg, 150)))
        ok_guard = ok_guard and o_rc == 3
        orders = [("the round's order, this record's three in place, Layer 9's draft, Layer 6's", ["gnd002", "fans12", "fandec", "panel5v", "ph4", "rt500", "gndret", "gndrtn", "iocbuck"] + L6),
                  ("Layer 9's draft before this record's three", ["gnd002", "fans12", "panel5v", "ph4", "rt500", "iocbuck", "fandec", "gndret", "gndrtn"] + L6),
                  ("this record's three first", ["gndret", "gndrtn", "fandec", "gnd002", "fans12", "panel5v", "ph4", "rt500", "iocbuck"] + L6),
                  ("the round reversed", ["gndret", "gndrtn", "rt500", "ph4", "panel5v", "fandec", "fans12", "gnd002", "iocbuck"] + L6)]
        w("   BOARD B COMPOSED with Layer 9's draft (the copy at 841e6c7e) and Layer 6's three (xal_land, lcsc, intent), in four orders:\n")
        gens, runs = [], []
        for i, (tag, seq) in enumerate(orders):
            pth, err = compose(seq, d, "ord%d" % i)
            if err:
                w("     %-76s %s\n" % (tag, err)); gens.append(None); runs.append(None)
                continue
            res = run_gen(pth); gens.append(hashlib.sha256(open(pth, "rb").read()).hexdigest()[:16]); runs.append(res)
            g = (res["intent"] or {}).get("rails", {}).get("GND") if res["intent"] else None
            w("     %-76s generator sha256 %s: %s\n" % (tag, gens[-1], "RUNS to its end, %d parts, %d unplaced, GND %.2f A typical, %.4f A peak, loads %.3f A"
                                                         % (len(res["table"]["parts"]), len(res["table"]["unplaced"]), g["amps_typ"], g["amps_peak"], sum(g["loads"].values()))
                                                         if res["stop"] is None else "STOPS: " + short(res["stop"], 150)))
        one_gen = len({x for x in gens}) == 1 and gens[0] is not None
        all_run = all(r is not None and r["stop"] is None and not r["table"]["unplaced"] for r in runs)
        w("     the four orders give one generator, byte for byte: %s; every order runs to its end: %s\n" % ("yes" if one_gen else "NO", "yes" if all_run else "NO"))
        pth7, err7 = compose(["gnd002", "fans12", "fandec", "panel5v", "ph4", "rt500", "gndret", "iocbuck"] + L6, d, "round7"); res7 = run_gen(pth7)
        w("     round 7's state (without the return draft): %s; without Layer 9's draft and the return draft: RUNS to its end, %d parts\n"
          % ("RUNS to its end, %d parts" % len(res7["table"]["parts"]) if not err7 and res7["stop"] is None else "STOPS", len(res5["table"]["parts"])))
        pth1, _e = compose(["gndret"], d, "alone"); res1 = run_gen(pth1)
        g1 = res1["intent"]["rails"]["GND"] if res1["intent"] else None
        w("     the gndret draft alone on the committed generator: %s\n"
          % ("RUNS, GND %.2f A typical and %.2f A peak, loads %.3f A: the same text, a smaller figure (nothing typed)" % (g1["amps_typ"], g1["amps_peak"], sum(g1["loads"].values()))
             if g1 else "STOPS: " + short(res1["stop"], 150)))
        # board A
        w("   BOARD A COMPOSED in L4-E9's change-list order (r12, guard, charger, r11, bank, r138, u17; record l8gnd's two; this record's five\n"
          "   of rounds 1 to 6; record l8p's ptc; L4-E11's dd7), Layer 9's draft (the copy at 841e6c7e), d8dec31's mainpb LAST, then Layer 6's table:\n")
        round_a = [P("v2/docs/records/%s/apply_gen_sch_a_%s.py" % rn) for rn in ROUND_A] + [P(L9T5_DRAFT_A)]
        runs_a, gens_a = [], []
        for tag, seq in (("the return draft after Layer 9's (the round's order)", round_a + [P(MINE_A["gndrtn_a"])]),
                         ("the return draft first", [P(MINE_A["gndrtn_a"])] + round_a),
                         ("round 7's state (without the return draft)", round_a)):
            pth, err = compose_a(seq, d, "a%d" % len(runs_a))
            if err:
                w("     %-56s %s\n" % (tag, err)); runs_a.append(None); gens_a.append(None)
                continue
            res = run_gen(pth, "a"); runs_a.append(res); gens_a.append(hashlib.sha256(open(pth, "rb").read()).hexdigest()[:16])
            w("     %-56s generator sha256 %s: %s\n" % (tag, gens_a[-1], "RUNS to its end, %d parts, %d unplaced, netlist sha256 %s"
                                                         % (len(res["table"]["parts"]), len(res["table"]["unplaced"]), hashlib.sha256(res["netlist"]).hexdigest()[:16])
                                                         if res["stop"] is None else "STOPS: " + short(res["stop"], 150)))
        a_run = all(r is not None and r["stop"] is None and not r["table"]["unplaced"] for r in runs_a)
        a_same_net = a_run and runs_a[0]["netlist"] == runs_a[1]["netlist"]
        w("     the return draft first or last gives the same netlist: %s (the generator text differs in the order of two SECTIONS.insert\n"
          "     lines, this draft's and another's: a schematic page's order, no net)\n" % ("yes" if a_same_net else "NO"))
        w("   THE NETLIST CHECKS (check_gndret_netlist.py; the regenerated netlists are the generators' own part tables, no KiCad: the box\n"
          "   export is the reading of record):\n")
        vC, lC = CK.judge(nlB, json.load(open(P(INT_B), encoding="utf-8")))
        vPc, lPc, _wh = CK.judge_pair(nlA, nlB)
        w("     the committed board B netlist and intent (%s sha256 %s): %s; the dedicated return on the committed boards: %s\n" % (NET_B, sha(NET_B), vC, vPc))
        for l in lC:
            w("       %s\n" % l)
        if not all_run or not a_run:
            refuse("a composition does not run: no netlist to check")
        nB, nA = CK.read_netlist(runs[0]["netlist"]), CK.read_netlist(runs_a[0]["netlist"])
        vB, lB = CK.judge(nB, runs[0]["intent"]); vP, lP, whole = CK.judge_pair(nA, nB)
        w("     board B composed (netlist sha256 %s): the return's declaration %s\n" % (hashlib.sha256(runs[0]["netlist"]).hexdigest()[:16], vB))
        for l in lB:
            w("       %s\n" % l)
        w("     boards A and B composed: the dedicated return %s\n" % vP)
        for l in lP:
            w("       %s\n" % l)
        v7, _l7 = CK.judge(CK.read_netlist(res7["netlist"]), res7["intent"]); vP7, _lP7, whole7 = CK.judge_pair(CK.read_netlist(runs_a[2]["netlist"]), CK.read_netlist(res7["netlist"]))
        w("     round 7's state: the declaration %s, the dedicated return %s\n" % (v7, vP7))
        _sp = importlib.util.spec_from_file_location("l8gnd_check", P("v2/docs/records/l8gnd/check_gnd002_netlist.py"))
        g2 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(g2)
        v8, l8 = CK._rd.judge("b", CK._rd.read_netlist(runs[0]["netlist"])); v8a, l8a = CK._rd.judge("a", CK._rd.read_netlist(runs_a[0]["netlist"]))
        vg, _lg = g2.judge("b", g2.read_netlist(runs[0]["netlist"])); vga, _lga = g2.judge("a", g2.read_netlist(runs_a[0]["netlist"]))
        w("     the same composed netlists under the checks of the drafts they carry: check_l8r2_netlist.py (rounds 1 to 6) board B %s (%s),\n"
          "       board A %s (%s); record l8gnd's check_gnd002_netlist.py board B %s, board A %s\n"
          % (v8, "; ".join(" ".join(x.split()) for x in l8), v8a, "; ".join(" ".join(x.split()) for x in l8a), vg, vga))
        # mutations
        w("   THE MUTATIONS (each must stop the generator or FAIL a check):\n")
        full = ["gnd002", "fans12", "fandec", "panel5v", "ph4", "rt500", "gndret", "gndrtn", "iocbuck"]
        muts = []

        def gen_mut(tag, seq, edit=None, pair=False):
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
                nm = CK.read_netlist(res["netlist"])
                v, lines = CK.judge(nm, res["intent"])
                out = "runs; the declaration reads %s%s" % (v, (": " + short("; ".join(l for l in lines if l[:2] in ("R1", "R2", "R3", "R4")), 200)) if v != "DRAWN" else "")
                bad = v != "DRAWN"
                if pair:
                    vp, lp, _w2 = CK.judge_pair(nA, nm)
                    out += "; the dedicated return reads %s%s" % (vp, (": " + short("; ".join(lp[1:]), 160)) if vp != "DRAWN" else "")
                    bad = bad or vp != "DRAWN"
            muts.append(bad)
            w("     m%d %s\n        %s\n" % (len(muts), tag, out))

        def sub1(old, new):
            def f(t):
                if t.count(old) != 1:
                    refuse("a mutation's anchor occurs %d times: %r" % (t.count(old), old[:50]))
                return t.replace(old, new)
            return f
        gen_mut("the old state: the composition without the gndret draft (and so without the return draft, which needs it)", [s for s in full if s not in ("gndret", "gndrtn")])
        gen_mut("the gndret draft without its companion fandec (the second stop behind the first)", [s for s in full if s != "fandec"])
        gen_mut("the typed declaration kept and simply raised: 21.0 written as 30.0 on the old text (the refused outcome)",
                [s for s in full if s not in ("gndret", "gndrtn")], sub1('_intent.rail("GND", 0.0, 10.0, 21.0, ', '_intent.rail("GND", 0.0, 10.0, 30.0, '))
        gen_mut("J_54V dropped from the return's sources in the helper", full, sub1('_srcs = list(leads) + ["J_54V"]', "_srcs = list(leads)"))
        gen_mut("a lead named on the return whose rail is declared on another connector (+5V_S2's source J_5V_S2 written J_5V_S9)", full,
                sub1('6.6, "J_5V_S%d" % _n, loads=_SLOT_LOADS(_n)', '6.6, "J_5V_S%d" % (9 if _n == 2 else _n), loads=_SLOT_LOADS(_n)'))
        gen_mut("a slot's card buck allocation raised from 2.2 to 4.2 A (a lead over its own peak: the derived return must not hide it)", full,
                sub1('    "U%d03" % s: 2.2, ', '    "U%d03" % s: 4.2, '))
        base = runs[0]

        def net_mut(tag, f, pair=False, board="b"):
            src = base if board == "b" else runs_a[0]
            raw = src["netlist"].decode("utf-8"); m = f(raw)
            if m == raw:
                refuse("netlist mutation '%s' changed nothing" % tag)
            nm = CK.read_netlist(m.encode("utf-8"))
            if board == "b":
                v, lines = CK.judge(nm, base["intent"]); vp, lp, wm = CK.judge_pair(nA, nm)
            else:
                v, lines = vB, []; vp, lp, wm = CK.judge_pair(nm, nB)
            bad = v == "FAIL" or (pair and vp == "FAIL")
            muts.append(bad)
            w("     m%d %s\n        the declaration reads %s%s; the dedicated return reads %s%s\n"
              % (len(muts), tag, v, (": " + short("; ".join(l for l in lines if l[:2] in ("R1", "R2", "R3", "R4")), 170)) if v == "FAIL" else "",
                 vp, (": " + short("; ".join(lp[1:]), 170)) if vp == "FAIL" else ""))
            return wm

        def swap_pins(ref):
            def f(raw):
                a, b, z = '(node (ref "%s") (pin "1"))' % ref, '(node (ref "%s") (pin "2"))' % ref, "\x00"
                if raw.count(a) != 1 or raw.count(b) != 1:
                    refuse("the netlist does not carry %s's two pins once each" % ref)
                return raw.replace(a, z).replace(b, a).replace(z, b)
            return f

        def drop_part(ref):
            def f(raw):
                out_ = re.sub(r' \(node \(ref "%s"\) \(pin "[^"]+"\)\)' % re.escape(ref), "", raw)
                return re.sub(r'    \(comp \(ref "%s"\)[^\n]*\n' % re.escape(ref), "", out_)
            return f
        net_mut("J_5V_S2's pins 1 and 2 exchanged on board B's netlist (the lead reversed)", swap_pins("J_5V_S2"))
        net_mut("R12's pin 2 taken off GND on board B's netlist (the PoE return's entry gone)", lambda raw: raw.replace(' (node (ref "R12") (pin "2"))', "", 1))
        # round 8: the return removed, landed on the wrong net, one termination dropped, a socket the declaration does not name
        acc_removed = design(2 * len(whole7), poe_awg=F["poe_awg"], enum=True)
        muts.append(vP7 != "DRAWN" and not acc_removed["printed"])
        w("     m%d THE RETURN REMOVED (both boards composed without the two return drafts: round 7's state)\n"
          "        the dedicated return reads %s; the acceptance on that census (%d return conductors): a VH pin 2 %.3f A, a ribbon conductor\n"
          "        %.3f A: every row on the printed ratings: %s\n"
          % (len(muts), vP7, 2 * len(whole7), worst(acc_removed, "VH"), worst(acc_removed, "RIB"), "yes" if acc_removed["printed"] else "NO"))
        gen_mut("THE RETURN LANDED ON THE WRONG NET: J_GR2's pin 1 drawn on +5V_DEV on board B", full,
                sub1('ground return 2 to A22 J_GR2 (lead: XT60-M both ends, 2 x 12 AWG, 150 mm)", "XT60F", {"1": "GND", "2": "GND"})',
                     'ground return 2 to A22 J_GR2 (lead: XT60-M both ends, 2 x 12 AWG, 150 mm)", "XT60F", {"1": "+5V_DEV", "2": "GND"})'), pair=True)
        wm = net_mut("ONE TERMINATION DROPPED: J_GR3 absent on board B's netlist (the lead plugged at board A only)", drop_part("J_GR3"), pair=True)
        acc_dropped = design(2 * len(wm), poe_awg=F["poe_awg"], enum=True)
        w("        the acceptance on the sockets left whole on both boards (%d conductors): every row on the printed ratings: %s; on the least\n"
          "        ratings at the inside air: %s (the third lead's margin is gone)\n"
          % (2 * len(wm), "yes" if acc_dropped["printed"] else "NO", "yes" if acc_dropped["least"] else "NO"))
        net_mut("ONE TERMINATION DROPPED on board A: J_GR1's pin 2 absent on board A's netlist", lambda raw: raw.replace(' (node (ref "J_GR1") (pin "2"))', "", 1), pair=True, board="a")
        gen_mut("a return socket the declaration does not name: J_GR3 left out of the helper's list", full,
                sub1('_rets = ["J_GR1", "J_GR2", "J_GR3"]', '_rets = ["J_GR1", "J_GR2"]'))
        all_mut = all(muts)
        w("     every mutation stops or fails: %s (%d of %d)\n" % ("yes" if all_mut else "NO", sum(muts), len(muts)))

        # ---------------------------------------------------------------- 6
        w("\n6. THE ACCEPTANCE WITH THE DEDICATED RETURN (the recheck's closure criterion; every current is a MODEL maximum over every vertex of\n"
          "   the contact-resistance box, enumerated; no figure is a measurement)\n")
        L_c = CK.leads(nB, runs[0]["intent"]); gcB, gcA = CK.ground_conductors(nB), CK.ground_conductors(nA)
        leadsA = sorted(r for r, pp in nA["pins"].items() if r.startswith(("J_5V_", "J_54V")) and pp.get("2") == "GND")
        n_ret = 2 * len(whole)
        w("6a. THE CENSUS, read on the composed netlists of both boards (not assumed): lead contacts with pin 2 on GND: board B %s; board A %s;\n"
          "    ribbon conductors on GND: %d on board B, %d on board A; return sockets whole on both boards: %s, two contacts and two %d AWG\n"
          "    conductors each: %d return conductors\n"
          % (", ".join(r for r, _n in L_c), ", ".join(leadsA), sum(len(v) for v in gcB.values()), sum(len(v) for v in gcA.values()), ", ".join(whole) or "none",
             F["xt_awg"], n_ret))
        if not (sorted(r for r, _n in L_c) == leadsA and len(L_c) == 6 and gcA == gcB and len(gcB["J_AB1"]) == 9 and len(gcB["J_AB2"]) == 8 and len(whole) == n_drafted["b"]):
            refuse("the composed netlists' ground conductors are not the model's (six leads, seventeen ribbon conductors, %d return sockets)" % n_drafted["b"])
        ACC = design(n_ret, poe_awg=F["poe_awg"], enum=True)
        hot_xt = least_rating(F["xt_a_new"], F["xt_tmax"], TH, F["xt_rise"])
        COND = {"VH": "PRINTED %.0f A, JST VH 'when using AWG #16 with the standard type header' (the fitted B2P-VH, the leads' gauge); no ambient and no derating printed" % F["vh_a16"],
                "VH18": "NO RATING PRINTED for AWG %d on the standard header (%.0f A is printed for the shrouded header: a comparator only)" % (F["poe_awg"], F["vh_a18"]),
                "RIB": "PRINTED %.0f A a conductor at 25 C ambient (the cable; the IDC socket %.0f A a contact); a derating stated, no curve printed" % (F["cab_a"], F["sock_a"]),
                "RET": "PRINTED %.0f A (V1.2, no condition) and %.0f A MAX with %d AWG at a rise under %.0f C (2021V1); range %.0f to %.0f C; no derating curve.\n"
                       "              The %d AWG conductor: the gauge both sheets name for the rating; no wire sheet is held (the energy chain DECLARES %.0f A for the pack lead's)"
                       % (F["xt_a_old"], F["xt_a_new"], F["xt_awg"], F["xt_rise"], F["xt_tmin"], F["xt_tmax"], F["xt_awg"], F["awg12_a"])}
        WHO = {"VH": "each 5 V lead's pin 2 (%s)", "VH18": "the PoE lead's pin 2 (%s)", "RIB": "each ribbon conductor (%s: 9 and 8)",
               "RET": "each XT60 contact of the return and its 12 AWG conductor (%s: " + "%d sockets, 2 each)" % len(whole)}
        w("6b. EVERY BRANCH AT ITS WORST VERTEX, against the rating its maker prints under the applicable condition. The vertex of each row: the\n"
          "    branch's own two contacts at 0 mOhm (no maker prints a minimum), every other contact at its maximum (VH %.0f mOhm after test, IDC\n"
          "    %.0f mOhm, XT60 %.1f mOhm), found by enumeration. 'least' is the least rating consistent with the sheet at that air (INFERRED, 3b).\n"
          % (F["vh_rc1"], F["sock_rc"], F["xt_r_new"]))
        for kind in ("VH", "VH18", "RIB", "RET"):
            names = next(r[3] for r in ACC["rows"] if r[2] == kind)
            w("    %s\n      rating: %s\n" % (WHO[kind] % ", ".join(sorted(set(names))), COND[kind]))
            w("      %-12s %-9s %10s %10s %10s %10s  %s\n" % ("total", "copper", "maximum", "printed", "least", "margin", "verdict"))
            for ti, Tx, k_, _names, cur, pr, le, vd in ACC["rows"]:
                if k_ == kind:
                    w("      %-12s %-9s %8.4f A %10s %10s %10s  %s\n"
                      % ("%.4f A" % totals[ti][1], "%.2f C" % Tx, cur, "%.0f A" % pr if pr else "none", "%.4f A" % le if le else "none",
                         "%+.1f %%" % (100 * (pr - cur) / pr) if pr else "", vd))
        for ti, (tag, tot) in enumerate(totals):
            w("    %.4f A: %s\n" % (tot, tag))
        rated = [r for r in ACC["rows"] if r[5] is not None]
        acc_printed = all(r[4] <= r[5] + 1e-12 for r in rated); acc_least = all(r[4] <= r[6] + 1e-12 for r in rated)
        w("    READ: every branch that has a printed rating is inside it at every vertex, at both copper ends, on all three totals: %s; inside the\n"
          "    least rating consistent with its sheet at the inside air: %s. J_54V's pin 2 carries at most %.4f A and has NO printed rating as\n"
          "    drawn (AWG %d on the standard header): its row is NOT covered until its lead is AWG 16 (6e).\n"
          "    P0 ROUND (V6-B2, 5 October 2026): this READ covers the COUNTED branches only (the leads, the ribbons and the return); the\n"
          "    indirect paths between the boards (the RF pigtails' shields, the monitor, the QMX, boards C and D) are bounded in l8r2_p0.out\n"
          "    section 3, PROVISIONAL on their contacts' ratings, which no held sheet prints.\n"
          % ("yes" if acc_printed else "NO", "yes" if acc_least else "NO", worst(ACC, "VH18"), F["poe_awg"]))
        w("6c. THE GROUND SHIFT between the boards, every contact at its maximum: at most %.2f mV (as drawn: %.2f mV) against the %.4f V the LDOs'\n"
          "    input allows (the smaller of Layer 9's %.3f V and the recheck's %.4f V): inside by a factor of %.0f.\n"
          % (ACC["shift"], max(s for (_e, s) in DR.values()), allow, F["l9_shift_allow"], F["v3_shift_allow"], allow * 1e3 / ACC["shift"]))
        # what the rows rest on that no maker prints
        a_pr = bisect(lambda x: design(n_ret, poe_awg=F["poe_awg"], ret_hi=x)["printed"], F["xt_r_new"], 100.0)
        a_le = bisect(lambda x: design(n_ret, poe_awg=F["poe_awg"], ret_hi=x)["least"], F["xt_r_new"], 100.0)
        WF = design(n_ret, poe_awg=F["poe_awg"], wire_floor=WIRE_FLOOR)
        wf_printed = all(r[4] <= r[5] + 1e-12 for r in WF["rows"] if r[5] is not None); wf_least = all(r[4] <= r[6] + 1e-12 for r in WF["rows"] if r[5] is not None)
        w("6d. WHAT THE ROWS REST ON THAT NO MAKER PRINTS, each named with its dependence:\n"
          "    - the plane copper in series with the return bundle (P0 round, V6-B1, 5 October 2026): every row takes each board as one node;\n"
          "      the plane resistance between the return sockets' lands and the 5 V entries is a NAMED CONDITION, L8R2-F33a, with the bound\n"
          "      each case tolerates and the land separation a layout may have on the declared stackups in l8r2_p0.out section 2\n"
          "      (PROVISIONAL on the routed boards' extraction). After the focused check cx45 (Q2) the sockets are PLACED with their\n"
          "      courtyards on both boards and the return studied as a distributed network (l8r2_dist.out) on a stand-in XT60-M land,\n"
          "      assumed sites and fill and an averaged LDO probe: every printed row holds there and the service cases hold on the least\n"
          "      ratings, a STUDY, not a correction; after cx46 V6-B1 stays OPEN as REMAINING ENGINEERING (the selected XT60-F lands, the\n"
          "      real source and load sites, a justified distributed resistance with tolerance coverage, each LDO's own shift).\n"
          "    - the XT60's contact resistance after ageing. Amass prints one limit (%.1f mOhm, 2021V1) with a %d-cycle life and no separate\n"
          "      after-test figure. Every row still holds on the printed ratings while each XT60 contact stays at or under %s mOhm, and on\n"
          "      the least ratings at or under %s mOhm (%.1f and %.1f times the printed limit). Beyond that a row fails: a four-wire reading of the\n"
          "      return leads at assembly and in service is what would show it.\n"
          "    - the contacts' minimum resistance: none is printed, so every row takes the branch's own contacts at 0 (the most adverse).\n"
          "    - the derating at the inside air: none is printed, so every row carries the least rating consistent with its sheet beside\n"
          "      the printed one (3b); the VH's rests on the ASSUMPTION that its rating is stated at %.0f C.\n"
          "    - the wires' own resistance: MODEL figures from nominal sections and lengths (no wire part is named, L8R2-F34), and the ribbon's\n"
          "      is its maker's MAXIMUM. With each branch's own wire at %.2f of its figure (ASSUMPTION, WIRE_FLOOR) the maxima become: a VH\n"
          "      pin 2 %.4f A, a ribbon conductor %.4f A (%.4f A at the inside air against at least %.4f A), an XT60 contact %.4f A: every\n"
          "      row on the printed ratings: %s; on the least ratings: %s.\n"
          "    - the lengths: the return leads at %.0f mm and J_AB2's ribbon at %.0f mm are ASSUMPTIONS (Layer 7 routes them).\n"
          % (F["xt_r_new"], F["xt_cycles_new"], "%.2f" % a_pr if a_pr else "no value", "%.2f" % a_le if a_le else "no value",
             (a_pr or 0) / F["xt_r_new"], (a_le or 0) / F["xt_r_new"], T_RATING_REF, WIRE_FLOOR, worst(WF, "VH"), worst(WF, "RIB"), worst(WF, "RIB", Tx=TH),
             least_rating(F["cab_a"], F["cab_tmax"], TH), worst(WF, "RET"),
             "yes" if wf_printed else "NO", "yes" if wf_least else "NO", F["lead_mm"] if RET_LEAD_MM is None else RET_LEAD_MM, F["ab1_mm"] if AB2_MM is None else AB2_MM))
        ACC16 = design(n_ret, poe_awg=16, enum=True)
        w("6e. THE PoE LEAD AT AWG 16 (a harness row for Layer 7, part of this correction; no generator text changes): J_54V's pin 2 is then one\n"
          "    more VH contact of the 5 V leads' make with the printed %.0f A: a VH pin 2 at most %.4f A, a ribbon conductor %.4f A, an XT60\n"
          "    contact %.4f A; every row on the printed ratings: %s; on the least ratings: %s; no row is left without a printed rating: %s.\n"
          % (F["vh_a16"], worst(ACC16, "VH"), worst(ACC16, "RIB"), worst(ACC16, "RET"), "yes" if ACC16["printed"] else "NO", "yes" if ACC16["least"] else "NO",
             "yes" if not ACC16["unrated"] else "NO"))
        w("6f. THE GROUND COPPER WHERE THE RETURN ENTERS (decision 35's function, track_current.width_for_current, 10 K, inner layers; Layer 9's\n"
          "    stackup for board B is %s, layer use %s: %d ground planes at %.1f oz; board A's has %d at %.1f oz). A LAYOUT CONSTRAINT for both\n"
          "    boards (finding L8R2-F33), not a judged layout: no board is routed with these parts.\n"
          % (F["b_stack"], F["b_use"], F["b_gnd_planes"], F["b_inner_oz"], F["a_gnd_planes"], F["a_inner_oz"]))
        spB, spA = 4 * 0.5 * F["b_gnd_planes"], 4 * 0.5 * F["a_gnd_planes"]
        for lab, amps in (("an XT60 contact's land at its worst vertex", worst(ACC, "RET")), ("a VH pin 2's land at its worst vertex", worst(ACC, "VH")),
                          ("a VH pin 2's land at the contact's printed %.0f A" % F["vh_a16"], F["vh_a16"])):
            wB = TC.width_for_current(amps, F["b_inner_oz"], 10.0, internal=True); wA = TC.width_for_current(amps, F["a_inner_oz"], 10.0, internal=True)
            w("      %-52s %7.3f A: %6.2f mm of %.1f oz plane in all; board B %5.2f mm on each of %d planes; board A %5.2f mm on each of %d\n"
              % (lab, amps, wB, F["b_inner_oz"], wB / F["b_gnd_planes"], F["b_gnd_planes"], wA / F["a_gnd_planes"], F["a_gnd_planes"]))
        w("      four thermal-relief spokes of 0.5 mm on each plane give %.1f mm on board B and %.1f mm on board A, under every row: the return\n"
          "      sockets' and the VH leads' pin 2 lands join their ground planes SOLIDLY (no thermal relief), or with spokes of the row's width.\n" % (spB, spA))

        # the fault cases
        tot_src = src_i + poe["peak"]
        w("6g. THE FAULT CASES (the owner's instruction: each with its currents, what protects or reveals it, whether it is tolerated inside the\n"
          "    ratings and whether it is latent). Every figure is the maximum over every vertex at both copper ends; 'printed' and 'least' say\n"
          "    whether every branch with a printed rating stays inside it and inside the least rating at the inside air.\n")
        w("      %-66s %-12s %9s %9s %9s %9s %8s  %s\n" % ("case", "total", "VH pin 2", "J_54V", "a ribbon", "an XT60", "shift mV", "printed / least"))
        FC = []

        def fault(tag, dg_fn, tot_list, note):
            for tg, tot in tot_list:
                dg = dg_fn([(tg, tot)])
                FC.append((tag, tot, dg))
                w("      %-66s %-12s %9.4f %9.4f %9.4f %9.4f %8.2f  %s / %s\n"
                  % (tag, "%.4f A" % tot, worst(dg, "VH"), worst(dg, "VH18"), worst(dg, "RIB"), worst(dg, "RET"), dg["shift"], "yes" if dg["printed"] else "NO", "yes" if dg["least"] else "NO"))
            w("        %s\n" % note)
        two = [totals[0], totals[2]]
        fault("F-0 no fault (the design)", lambda tl: design(n_ret, poe_awg=F["poe_awg"], tot_list=tl, enum=True), two, "the rows of 6b.")
        fault("F-1 one return lead absent or open (%d conductors left)" % (n_ret - 2), lambda tl: design(n_ret - 2, poe_awg=F["poe_awg"], tot_list=tl, enum=True), two,
              "Nothing interrupts and nothing signals: the kit runs as before. LATENT. Revealed only by a four-wire reading between the two\n"
              "        boards' grounds or by looking (an assembly and service check, OWED: finding L8R2-F39).")
        fault("F-2 one XT60 contact of one return lead open (%d conductors left)" % (n_ret - 1), lambda tl: design(n_ret - 1, poe_awg=F["poe_awg"], tot_list=tl, enum=True), two,
              "As F-1 with one conductor more: LATENT, revealed the same way.")
        fault("F-3 one 5 V lead's pin 2 open (its pin 1 still supplies its rail)", lambda tl: design(n_ret, poe_awg=F["poe_awg"], tot_list=tl, enum=True, vh_open=1), two,
              "The rail's return finds the other conductors and the rail works: LATENT. With the dedicated return in place the other\n"
              "        branches barely move; as drawn (no dedicated return) the same fault is worse than 3d's rows, which already do not hold.")
        tot_one = tot_big - max(r["least"] for r in bt[6].values()) + F["loop_max"]
        fault("F-4a one 5.1 V stage in its current limit (%.3f A) beside the largest state" % F["loop_max"],
              lambda tl: design(n_ret, poe_awg=F["poe_awg"], tot_list=tl, enum=True), [("one stage in its limit", tot_one)],
              "A single overload: the stage's average current loop bounds it (PRINTED VSNS %.0f mV maximum over the DECLARED 6 mOhm shunt) and\n"
              "        does not interrupt. The rail's INA226 on board A shows it to the panel controller; what firmware then does is Layer 5's\n"
              "        slot-fault rule, not re-read here: NOT LATENT by design intent, not verified." % (R6.V["vsns"][2] * 1e3))
        fault("F-4b the sources' deliverable bound (four loops at %.3f A, U601 at %.2f A, PoE %.2f A)" % (F["loop_max"], F["u601_out"], poe["peak"]),
              lambda tl: design(n_ret, poe_awg=F["poe_awg"], tot_list=tl, enum=True), [("the sources' bound", tot_src)],
              "Every source at its bound at once: four independent overloads and U601's. A ribbon conductor then reads %.4f A at %.0f C against its\n"
              "        printed %.0f A (over by %.2f %%) at its extreme vertex; every other branch stays inside its printed rating. A fourth return\n"
              "        lead would read %.4f A there; it is not drafted for a four-fault bound. Revealed as F-4a."
              % (worst(design(n_ret, poe_awg=F["poe_awg"], tot_list=[("s", tot_src)]), "RIB"), TL, F["cab_a"],
                 100 * (worst(design(n_ret, poe_awg=F["poe_awg"], tot_list=[("s", tot_src)]), "RIB") - F["cab_a"]) / F["cab_a"],
                 worst(design(n_ret + 2, poe_awg=F["poe_awg"], tot_list=[("s", tot_src)]), "RIB")))
        fault("F-5 every return lead absent (the board as drawn today)", lambda tl: design(0, poe_awg=F["poe_awg"], tot_list=tl, enum=True), two,
              "Section 3d's rows: DOES NOT HOLD. LATENT in the same way. It is the state the correction exists to remove.")
        fc = {t_[0].split()[0]: [] for t_ in FC}
        for t_ in FC:
            fc[t_[0].split()[0]].append(t_)
        tol_pr = sorted(k for k, v in fc.items() if all(x[2]["printed"] for x in v)); tol_le = sorted(k for k, v in fc.items() if all(x[2]["least"] for x in v))
        w("    TOLERATED inside every printed rating: %s; inside the least ratings at the inside air as well: %s; NOT tolerated: %s.\n"
          "    LATENT (nothing protects against it and nothing reveals it in service): F-1, F-2, F-3 and F-5. The design does not make them\n"
          "    visible; it makes F-1 to F-3 harmless inside the printed ratings. A detect line on the return is not drafted (L8R2-F39).\n"
          "    F-1 with the return at its extreme vertex is over the ribbon's LEAST rating at the inside air on the upper bound, inside its\n"
          "    printed rating: with one lead out the third lead's margin against the unprinted derating is gone, which is what it was for.\n"
          % (", ".join(tol_pr) or "none", ", ".join(tol_le) or "none", ", ".join(sorted(k for k in fc if k not in tol_pr)) or "none"))

        # ---------------------------------------------------------------- 7
        w("\n7. FOR LAYER 9'S AUTHOR AND THE INDEPENDENT CHECK\n")
        w("   board B's and board A's compositions in L4-E9's order with Layer 9's drafts run to their ends with this round's two return drafts\n"
          "   in them (section 5); on board B the return draft follows gndret.\n")
        gi2 = runs[0]["intent"]["rails"]["GND"]
        w("   the declaration with Layer 9's draft composed (read from the regenerated intent): GND %.2f A typical, %.4f A peak (the UPPER BOUND,\n"
          "   DECLARED), sources %s; %d loads summing %.3f A\n"
          % (gi2["amps_typ"], gi2["amps_peak"], ", ".join(gi2["source"]), len(gi2["loads"]), sum(gi2["loads"].values())))
        w("   THE RETURN EACH CONNECTOR CARRIES ON C-DEV rev 1 (%.4f A in all; pin 1 is the rail's own current, MODEL: records l9pwr and l9t5; pin 2\n"
          "   is the maximum over every vertex, MODEL on PRINTED limits, at %.2f C and at %.0f C):\n" % (tot_cdev, TH, TL))
        pin1 = {"J_5V_S1": rows["S1"]["least"], "J_5V_S2": rows["S2"]["least"], "J_5V_S3": rows["S3"]["least"], "J_5V_DEV": F["cdev_u7"], "J_5V_IOC": F["cdev_u601"], "J_54V": 0.0}
        w("     %-10s %12s %26s %30s %12s\n" % ("connector", "pin 1", "pin 2 as drawn (hot, cold)", "pin 2 with the return (hot, cold)", "printed"))

        def at(dg, kind, Tx):
            return max(r[4] for r in dg["rows"] if r[2] == kind and r[0] == 0 and r[1] == Tx)
        for n_ in ("J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV", "J_5V_IOC"):
            w("     %-10s %10.4f A %12.4f A %10.4f A %14.4f A %12.4f A %10.0f A\n"
              % (n_, pin1[n_], DR[(0, TH)][0]["VH"][0], DR[(0, TL)][0]["VH"][0], at(ACC, "VH", TH), at(ACC, "VH", TL), F["vh_a16"]))
        w("     %-10s %10.4f A %12.4f A %10.4f A %14.4f A %12.4f A %12s\n"
          % ("J_54V", pin1["J_54V"], DR[(0, TH)][0]["VH18"][0], DR[(0, TL)][0]["VH18"][0], at(ACC, "VH18", TH), at(ACC, "VH18", TL), "none"))
        w("     %-10s %12s %12.4f A %10.4f A %14.4f A %12.4f A %10.0f A\n"
          % ("a ribbon", "signals", DR[(0, TH)][0]["RIB"][0], DR[(0, TL)][0]["RIB"][0], at(ACC, "RIB", TH), at(ACC, "RIB", TL), F["cab_a"]))
        w("     %-10s %12s %12s %12s %14.4f A %12.4f A %10.0f A\n" % ("an XT60", "none", "not drawn", "", at(ACC, "RET", TH), at(ACC, "RET", TL), min(F["xt_a_old"], F["xt_a_new"])))
        w("   J_5V_IOC's pin 2 on the case: %.4f A as drawn at %.2f C (the recheck's corner, over the printed %.0f A) and %.4f A with the dedicated\n"
          "   return; Layer 9's acceptance of that pin and of the LDOs' input depends on this correction, and on nothing else of this record.\n"
          % (DR[(0, TH)][0]["VH"][0], TH, F["vh_a16"], at(ACC, "VH", TH)))
        w("   CREDIT (the common brief's three criteria) for round 8's two return drafts: (a) they compose in L4-E9's order on both boards and\n"
          "   the generators run: %s; (b) the changed nets are read on the regenerated netlists with mutations that fail: %s; (c) the\n"
          "   electrical acceptance on the makers' printed figures: every branch with a printed rating inside it at every vertex: %s; the\n"
          "   conditions of 6d and J_54V's unrated pin stay. NOT CLOSED: L8R2-F31 is OPEN until an independent check has read this.\n"
          % ("yes" if all_run and a_run else "NO", "yes" if vB == "DRAWN" and vP == "DRAWN" and all_mut else "NO", "yes" if acc_printed else "NO"))
        w("   WHAT THE INDEPENDENT CHECK SHOULD READ: (1) enumerate_vertices(), analytic() and extremes() in this script against its own\n"
          "   arithmetic for one corner (3d reproduces the recheck's); (2) box(): each contact's low and high end against the makers' sheets, the\n"
          "   XT60's two specifications above all (3b); (3) the census of 6a on the regenerated netlists; (4) each row of 6b against its\n"
          "   rating and condition, and 6d's four dependences; (5) the two drafts apply_gen_sch_a_gndrtn.py and apply_gen_sch_b_gndrtn.py and\n"
          "   their land (NOT READ on this host); (6) the fault table 6g, and whether three latent faults without a detect line are acceptable.\n")

        # ---------------------------------------------------------------- 8
        w("\n8. FINDINGS\n")
        w("   L8R2-F30 CORRECTED BY DRAFT (round 7, not applied): board B's typed, stale GND declaration; apply_gen_sch_b_gndret.py.\n"
          "   L8R2-F31 OPEN (KNOWN DEFECT of the A to B power interface): the return divided over VH contacts and signal ribbons with nothing\n"
          "            setting its division; as drawn a 5 V lead's pin 2 reaches %.3f A and a ribbon conductor %.3f A on C-DEV rev 1 (every\n"
          "            vertex). CORRECTION DRAFTED in round 8 (three XT60 return leads, both boards), credit (a) and (b), acceptance (c) on\n"
          "            the conditions of 6d; UNCHECKED: it stays OPEN until an independent check has read the changed design.\n"
          "   L8R2-F32 CORRECTED BY DRAFT (round 7, not applied): fans12's TPS61089 capacitors' class; apply_gen_sch_b_fandec.py.\n"
          "   L8R2-F33 OPEN (layout constraint, boards A and B; Layer 9): the return sockets' and the VH leads' pin 2 lands join their ground\n"
          "            planes solidly or with spokes of 6f's widths; board A's intent cannot express the 5 V returns' loop.\n"
          "   L8R2-F34 OWED (Layer 7): the leads' wire parts and insulation classes; J_54V's lead at AWG 16 (its pin 2 has no printed rating\n"
          "            at AWG 18 and carries up to %.3f A of the return); the three return leads' row (XT60-M both ends, 2 x %d AWG, their length).\n"
          "   L8R2-F35 ANSWERED by Layer 9's round 3 (the lead named, the peaks from their basis, the pin 2 sentence withdrawn); its acceptance\n"
          "            of J_5V_IOC's pin 2 on round 7's sampled rows is WITHDRAWN with them (3e) and now rests on this correction.\n"
          "   L8R2-F36 FOR L4-E9 (the change list): board B rows for fandec, gndret and gndrtn (gndrtn after gndret), a board A row for gndrtn,\n"
          "            one release; a register row for L8R2-F31.\n"
          "   L8R2-F37 MINOR (board B's generator owner): the return places +5V_HDMI's 0.20 A at U3 and U4; the rail declares J_HDMI.\n"
          "   L8R2-F38 CORRECTED (this record's own defect, found by the recheck V3): round 7's return calculation sampled six cases and\n"
          "            called the largest a maximum; every vertex is now enumerated and checked against the monotone argument.\n"
          "   L8R2-F39 OPEN (commissioning and service, Layer 12; Layer 5): an absent or open return lead, an open XT60 contact and an open VH\n"
          "            pin 2 are LATENT (6g). Tolerated inside the printed ratings, not revealed. Next action: a four-wire bond reading\n"
          "            between the boards' grounds in the assembly and service procedures, or a detect line (not drafted).\n"
          "   L8R2-F40 FOR LAYER 7 AND LAYER 6: the return sockets are XT60-F so that the pack lead (XT60-F) cannot enter them; a return lead's\n"
          "            free XT60-M end could still be mated to the pack lead by hand: mark the leads. The XT60-F's land (KiCad's\n"
          "            Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical) is NOT READ on this host and no LCSC code is carried.\n"
          "   L8R2-F41 FOR LAYER 5: IF-AB-POWER gains the three return leads and the return's division (row texts in the page's section 3g).\n"
          "   L8R2-F42 NOTED: the XT60's printed range starts at %.0f C, the envelope's cold end in use (%.0f C): no margin (the pack connector's\n"
          "            source entry says the same).\n"
          "   L8R2-F43 FOR LAYER 9 AND LAYER 5 (the supply pins, not the return): JST prints no ambient and no derating for the VH's %.0f A. On the\n"
          "            severest reading of its sheet (the rating at %.0f C, the contact at its range's top) a pin 1 may carry %.4f A at the\n"
          "            inside air; %s is over that reading on its steady HIGH figure and inside the printed rating. A question for JST\n"
          "            (the rise at the rated current, or a derating curve) is drafted in the page and UNSENT.\n"
          % (max(DR[(0, Tx)][0]["VH"][0] for Tx, _l in TEMPS), max(DR[(0, Tx)][0]["RIB"][0] for Tx, _l in TEMPS), worst(ACC, "VH18"), F["xt_awg"], F["xt_tmin"], TL,
             F["vh_a16"], T_RATING_REF, vh_least, ", ".join(pin1_over) if pin1_over else "no pin 1"))

        # ---------------------------------------------------------------- 9
        w("\n9. PREDICATES\n")
        f1 = [x for x in FC if x[0].startswith("F-1")]; f4a = [x for x in FC if x[0].startswith("F-4a")]; f4b = [x for x in FC if x[0].startswith("F-4b")]
        f5 = [x for x in FC if x[0].startswith("F-5")]; f23 = [x for x in FC if x[0].startswith(("F-2", "F-3"))]
        preds = [
            ("the stop is reproduced after fans12, without and with Layer 9's draft", bool(first_stop and first_stop[0] == "fans12" and by["rt500"][0]["stop"] and by["iocbuck"][0]["stop"])),
            ("fans12 alone moves the sum, by 1.770 A; Layer 9's draft by 0.000 A", abs(fan_delta - 1.77) < 1e-9 and abs(sum(gI["loads"].values()) - sum(gc["loads"].values())) < 1e-9),
            ("the return's list is the union of the leads' allocations (no ampere twice)", abs(tot_c - sum(gc["loads"].values())) < 1e-9),
            ("both committed netlists carry the same five lead contacts and seventeen ribbon conductors on GND", vhA == vhB and gA == gB and len(gB["J_AB1"]) + len(gB["J_AB2"]) == 17),
            ("the derived peak equals the leads' sum and is not typed (22.23 A alone, 26.40 A composed, 27.9108 A with Layer 9's)",
             g1 is not None and abs(g1["amps_peak"] - pk_0) < 1e-6 and abs(res5["intent"]["rails"]["GND"]["amps_peak"] - pk_c) < 1e-6 and abs(gi2["amps_peak"] - pk_i) < 1e-6),
            ("with Layer 9's draft the 5 V leads' declared peaks hold the budget's largest state with every start at once", tot_big_starts <= pk5_i),
            ("the recheck's corner is reproduced: J_5V_IOC's pin 2 on C-DEV rev 1 as drawn, over its printed 10 A", abs(v3_here - F["v3_ioc"]) < 2e-3 and v3_here > F["vh_a16"]),
            ("round 7's sampled maximum is under the true one for a VH pin 2 and for a ribbon conductor, on every total",
             all(old["VH"] < new["VH"][0] - 1e-6 and old["RIB"] < new["RIB"][0] - 1e-6 for old, new in missed)),
            ("as drawn the return does not hold on C-DEV rev 1: a VH pin 2 and a ribbon conductor pass their printed ratings", bool(drawn_over) and all((k, 0) in drawn_over for k in ("VH", "RIB"))),
            ("each of the four drafts checks, applies once, refuses twice and refuses the tree; the return draft refuses without gndret", ok_guard),
            ("board B: the four orders give one generator and each runs to its end with no part unplaced", one_gen and all_run),
            ("board A composes in L4-E9's order with the return draft first or last, to one netlist", a_run and a_same_net),
            ("composed: the declaration DRAWN and the dedicated return DRAWN on both boards; committed: NOT DRAWN and NOT DRAWN", (vB, vP, vC, vPc) == ("DRAWN", "DRAWN", "NOT DRAWN", "NOT DRAWN")),
            ("the composed netlists also read DRAWN under check_l8r2_netlist.py and check_gnd002_netlist.py, both boards", (v8, v8a, vg, vga) == ("DRAWN",) * 4),
            ("every mutation stops the generator or fails a check (the return removed, on the wrong net, one termination dropped among them)", all_mut and len(muts) >= 13),
            ("the census of the composed netlists is the model's: six leads, seventeen ribbon conductors, %d return conductors" % n_ret, n_ret == n_least and len(L_c) == 6),
            ("WITH THE RETURN every branch with a printed rating is inside it at every vertex, both copper ends, all three totals", acc_printed),
            ("and inside the least rating consistent with its sheet at the inside air", acc_least),
            ("the ground shift is inside the LDOs' allowance", ACC["shift"] <= allow * 1e3),
            ("J_54V's pin 2 has no printed rating as drawn (AWG 18) and has one with an AWG 16 lead, which every row then holds", bool(ACC["unrated"]) and not ACC16["unrated"] and ACC16["printed"]),
            ("the XT60 contacts may age past their printed limit before a printed-rating row fails", a_pr is not None and a_pr > F["xt_r_new"]),
            ("one return lead absent is tolerated inside the printed ratings and is latent (6g F-1)", all(x[2]["printed"] for x in f1)),
            ("one open XT60 contact and one open VH pin 2 are tolerated inside the printed and the least ratings (6g F-2, F-3)", all(x[2]["least"] for x in f23)),
            ("one stage in its current limit is tolerated inside the printed ratings (6g F-4a)", all(x[2]["printed"] for x in f4a)),
            ("every source at its bound at once is NOT tolerated: a ribbon conductor passes its printed rating (6g F-4b)", not any(x[2]["printed"] for x in f4b)),
            ("every return lead absent is not tolerated (6g F-5, the board as drawn)", not any(x[2]["printed"] for x in f5)),
            ("the selection is the least number of leads that holds the least ratings, and the drafts draw it", n_drafted["a"] == n_drafted["b"] == n_least // 2),
        ]
        for tag, ok in preds:
            w("   %-134s %s\n" % (tag, "yes" if ok else "NO"))
    w("\nEND\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
