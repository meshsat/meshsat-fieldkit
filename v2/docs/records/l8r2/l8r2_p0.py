#!/usr/bin/env python3
"""Record l8r2, P0 round (MESHSAT-1357, 5 October 2026, Slot A of the P0 power closure): the independent check V6's findings on the
dedicated return between boards A and B (L8R2-F31), corrected or disposed of against their failure cases. PROTOTYPE DESIGN, DESK
ARITHMETIC: nothing is built, bought, powered or measured; no figure printed here is a measurement.

  1. the return solver of l8r2_gndret.py (imported unchanged, pinned) with ONE added term: a series resistance Rs shared by the
     dedicated return's bundle (the plane copper between the return sockets' lands and the place the 5 V return enters or leaves,
     on both boards together), checked against the record's own maxima at Rs = 0;
  2. V6-B1: the largest Rs each row tolerates, per case, copper end and rating (V6's figures reproduced), and whether a layout can
     realise it on the boards' declared stackups (record l9stk: board A two ground planes, board B three, 0.5 oz), by the spreading
     model between two lands (MODEL), with the levers (a fourth return lead; 1 oz inner copper, the owner's open copper decision);
  3. V6-B2: the indirect ground paths between the boards (the RF pigtails' shields, the monitor, the QMX, boards C and D), each with
     its least resistance (a labelled ASSUMPTION where no cable sheet is held) and its weakest rating, bounded at its own worst vertex,
     and the counted rows re-judged with the monitor's and the QMX's return shares added to the totals;
  4. V6-m12: F-4b (every source at its bound) disposed of by a SESSION decision with its authority fields;
  5. V6-m8: the XT60 rows labelled against the wire-to-wire rating;
  6. C-DEV rev 2 (conditional on FW-B20 and FW-B21): the supervisors' term and what it changes; 7. the predicates.
Run from the repository root: python3 v2/docs/records/l8r2/l8r2_p0.py (stdlib, pdftotext). Output regenerated only through
_bin/regen_out.py.
"""
import hashlib
import importlib.util
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True

PINS = ["v2/docs/records/l8r2/l8r2_gndret.py", "v2/docs/records/l8r2/l8r2_gndret.out",
        "v2/docs/records/l8r2/inputs/coordinator-cases-2026-10-05-cdev-rev2.md", "v2/docs/records/l9stk/L9-STACKUPS.md",
        "v2/vendor/hirose/hirose-ufl-series-catalogue-2009-02-digikey-copy.pdf", "v2/vendor/connectors/jst-ph-catalogue.pdf",
        "v2/vendor/battery/amass-xt60-spec-tme.pdf", "v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf",
        "v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/pcb_interfaces.yaml"]
# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options. Each text is a
# verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its PDF; _lib/pdftext.py returns it byte
# for byte and refuses when it is absent, so this script never runs pdftotext (the pins print each text's sha256, l8r2_gndret.py's texts with them, since G.figures() reads those here).
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l8r2
PDFTEXT = {
    "v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf": [["-layout"]],
    "v2/vendor/battery/amass-xt60-spec-tme.pdf": [["-layout"]],
    "v2/vendor/connectors/jst-ph-catalogue.pdf": [["-layout"]],
    "v2/vendor/hirose/hirose-ufl-series-catalogue-2009-02-digikey-copy.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)
# the owner's amendment 1 on L8R2-F33a (INBOX 11, 5 October 2026): the condition read against the boards' placement as drawn
BOARD_PCB = {"a": "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb", "b": "v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb"}
PINS += list(BOARD_PCB.values())
ENTRIES = ("J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV", "J_5V_IOC")      # the 5 V leads; J_5V_IOC is record l9t5's I-03 lead
GROUPS = (("J_5V_S1",), ("J_5V_S2", "J_5V_S3"), ("J_5V_DEV", "J_5V_IOC"))   # one return socket a group (SESSION, section 2b)
TH, TC = 76.25, -20.0
CU_ALPHA = 0.00393
OZ = {0.5: 17.5e-6, 1.0: 35.0e-6}          # m: nominal copper thickness per weight (ASSUMPTION: no fabricator's finished thickness held)
THK_TOL = 0.15                             # the finished inner copper's shortfall from nominal at its thin corner (ASSUMPTION)
PLANES = {"a": 2, "b": 3}                  # ground planes: record l9stk (A: In1 and In4; B: S G S G P S G S)
LAND_R = (1.5e-3, 3.0e-3)                  # m: the spreading radius of a return's land group (a 3 mm land; V6's 3 mm), two values shown
RG178_OHM_M = 0.040                        # Ohm/m: an RG-178 outer braid (ASSUMPTION, a typical figure; no cable sheet is held)


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l8r2_p0: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern no longer matches its pinned input" % what)
    return m


def load():
    sp = importlib.util.spec_from_file_location("l8r2_gndret_for_p0", os.path.join(HERE, "l8r2_gndret.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


G = load()


def rows(F, total, T, rs=0.0, n_ret=6):
    """{kind: the conductor's largest current over every vertex} with Rs (mOhm) in series with the return bundle. A non-return
    conductor's extreme is its own contacts low and every other high (the record's monotone argument); the bundle's conductance at
    every contact high is put in series with Rs. A return conductor's extreme is its own contacts low, the rest of the bundle high, the
    bundle in series with Rs. Also returns the network's conductance at every contact high (1/mOhm) for section 3."""
    C = G.classes_of(G.conductors(F, T, True, n_ret=n_ret, poe_awg=16), G.box(F))
    out = {}
    g_hi_non = sum(c["m"] * c["g"][2] for c in C if c["kind"] != "RET")
    g_hi_ret = sum(c["m"] * c["g"][2] for c in C if c["kind"] == "RET")

    def ser(g):
        return 1.0 / (1.0 / g + rs) if rs > 0 else g
    for c in C:
        g0 = c["g"][0]
        if c["kind"] == "RET":
            gb = g0 + (c["m"] - 1) * c["g"][2]
            gr = ser(gb)
            cur = total * gr / (gr + g_hi_non) * g0 / gb
        else:
            gn = g_hi_non - c["g"][2] + g0
            cur = total * g0 / (gn + ser(g_hi_ret))
        out[c["kind"]] = max(out.get(c["kind"], 0.0), cur)
    out["G_all_hi"] = g_hi_non + ser(g_hi_ret)
    return out


def ratings(F, T):
    return {"VH": (F["vh_a16"], G.least_rating(F["vh_a16"], F["vh_tmax"], T)),
            "RIB": (F["cab_a"], G.least_rating(F["cab_a"], F["cab_tmax"], T)),
            "RET": (F["xt_a_new"], min(F["xt_a_new"], G.least_rating(F["xt_a_new"], F["xt_tmax"], T, F["xt_rise"])))}


def bisect(f, lo, hi, n=80):
    if not f(lo):
        return 0.0
    if f(hi):
        return hi
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) else (lo, mid)
    return lo


def r_plane(d, a, n, T, oz, thin=False):
    """MODEL: spreading resistance between two lands of radius a, d apart, on n parallel planes of weight oz (mOhm)"""
    t = OZ[oz] * ((1 - THK_TOL) if thin else 1.0)
    rho = 1.72e-8 * (1 + CU_ALPHA * (T - 20.0))
    return rho / t / (n * math.pi) * math.log(d / a) * 1e3


def d_max(bound, a, T, oz, thin=True):
    """the largest land separation (mm) at which boards A and B together stay under bound (mOhm), the same separation on both"""
    k = r_plane(math.e * a, a, PLANES["a"], T, oz, thin) + r_plane(math.e * a, a, PLANES["b"], T, oz, thin)     # mOhm per unit of ln(d/a)
    return a * math.exp(bound / k) * 1e3


_TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def _tree(text_):
    stack = [[]]
    for tok in _TOK.findall(text_):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            n = stack.pop()
            stack[-1].append(n)
        else:
            stack[-1].append(tok[1:-1] if tok.startswith('"') else tok)
    return stack[0][0]


def _at(node):
    for x in node:
        if isinstance(x, list) and x and x[0] == "at":
            return float(x[1]), float(x[2]), float(x[3]) if len(x) > 3 else 0.0
    return None


def pad_positions(path, refs):
    """{ref: {pad: (x, y, net)}} of the named footprints on a placed board, read by parsing each footprint block (not a grep)"""
    t_ = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'\(footprint "', t_):
        i, j, depth = m.start(), m.start(), 0
        while True:
            c = t_[j]
            if c == '"':
                j += 1
                while t_[j] != '"':
                    j += 2 if t_[j] == "\\" else 1
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = t_[i:j + 1]
        ref = re.search(r'\(property "Reference" "([^"]+)"', blk)
        if not ref or ref.group(1) not in refs:
            continue
        fp = _tree(blk)
        x0, y0, rot = _at(fp)
        a = math.radians(-rot)
        pads = {}
        for x in fp:
            if isinstance(x, list) and x and x[0] == "pad":
                px, py, _r = _at(x)
                net = [y for y in x if isinstance(y, list) and y and y[0] == "net"]
                pads[x[1]] = (x0 + px * math.cos(a) - py * math.sin(a), y0 + px * math.sin(a) + py * math.cos(a), net[0][-1] if net else "")
        out[ref.group(1)] = pads
    return out


def enclosing_radius(pts):
    """the smallest circle containing every point (mm): exact for a few points, over every pair's and triple's circle"""
    if len(pts) <= 1:
        return 0.0, pts[0] if pts else None
    best = None
    cands = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            cx, cy = (pts[i][0] + pts[j][0]) / 2, (pts[i][1] + pts[j][1]) / 2
            cands.append((cx, cy))
            for k in range(j + 1, len(pts)):
                (ax, ay), (bx, by), (qx, qy) = pts[i], pts[j], pts[k]
                d = 2 * (ax * (by - qy) + bx * (qy - ay) + qx * (ay - by))
                if abs(d) > 1e-9:
                    ux = ((ax * ax + ay * ay) * (by - qy) + (bx * bx + by * by) * (qy - ay) + (qx * qx + qy * qy) * (ay - by)) / d
                    uy = ((ax * ax + ay * ay) * (qx - bx) + (bx * bx + by * by) * (ax - qx) + (qx * qx + qy * qy) * (bx - ax)) / d
                    cands.append((ux, uy))
    for cx, cy in cands:
        r = max(math.hypot(px - cx, py - cy) for px, py in pts)
        if best is None or r < best[0] - 1e-12:
            best = (r, (cx, cy))
    return best


def placement(d_need):
    """L8R2-F33a against the placement as drawn: each 5 V lead's ground land (pin 2) per board, one cluster against the split
    arrangement (one socket a group)"""
    res = {}
    for b, p in BOARD_PCB.items():
        pads = pad_positions(os.path.join(ROOT, p), set(ENTRIES))
        land = {}
        for ref in ENTRIES:
            if ref in pads:
                g = [(x, y) for _k, (x, y, n) in pads[ref].items() if n in ("GND", "/GND")]
                if len(g) != 1:
                    refuse("%s on board %s has %d ground pads" % (ref, b, len(g)))
                land[ref] = g[0]
        one = enclosing_radius(list(land.values()))
        groups = []
        for grp in GROUPS:
            pts = [land[r] for r in grp if r in land]
            missing = [r for r in grp if r not in land]
            groups.append((grp, enclosing_radius(pts)[0] if pts else 0.0, missing,
                           max((math.hypot(a[0] - c[0], a[1] - c[1]) for a in pts for c in pts), default=0.0)))
        res[b] = dict(land=land, one=one[0], groups=groups, need=d_need)
    res["met_one"] = all(res[b]["one"] <= d_need for b in BOARD_PCB)
    res["met_split"] = all(g[1] <= d_need for b in BOARD_PCB for g in res[b]["groups"])
    return res


def compute():
    for p in PINS:
        if not os.path.isfile(rel(p)):
            refuse("%s is missing" % p)
    F = G.figures()
    out = open(rel(PINS[1]), encoding="utf-8").read()
    totals = {}
    for lab, key in (("C-DEV rev 1", r"([\d.]+) A: C-DEV rev 1 \(PS-ALLTX, HIGH, the least load voltage\) with Layer 9's draft"),
                     ("the largest steady state (PS-BUSY, HIGH)", r"([\d.]+) A: the largest state of Layer 9's budget \(PS-BUSY, HIGH, the least load voltage\) with Layer 9's draft"),
                     ("the declared upper bound (i)", r"([\d.]+) A: the declared upper bound \(i\) with Layer 9's draft")):
        totals[lab] = float(need(out, key, lab).group(1))
    u601 = float(need(out, r"U7 6\.0359 A and U601 ([\d.]+) A, total", "U601's figure on C-DEV rev 1").group(1))
    cs = " ".join(open(rel(PINS[2]), encoding="utf-8").read().split())
    m = need(cs, r"\+5V_IOC ([\d.]+) A\*\* in place of ([\d.]+) A", "C-DEV rev 2's +5V_IOC")
    ioc2, ioc1 = float(m.group(1)), float(m.group(2))
    need(cs, r"CONDITION: rev 2 holds only with FW-B20 and FW-B21 applied", "C-DEV rev 2's condition")
    u601_2 = ioc2 * u601 / ioc1                         # the same constant-power reading the record took for rev 1
    totals["C-DEV rev 2 (conditional on FW-B20/B21)"] = totals["C-DEV rev 1"] - u601 + u601_2
    R = {"F": F, "totals": totals, "u601": (u601, u601_2, ioc1, ioc2), "pins": [(p, sha(p)) for p in PINS]
         + [(t, h[:16]) for t, h, _held in PT.inputs(ROOT, {k: G.PDFTEXT.get(k, []) + PDFTEXT.get(k, []) for k in set(G.PDFTEXT) | set(PDFTEXT)})]}

    # 1. the solver at Rs = 0 against the record's own extremes
    chk = []
    for lab, tot in totals.items():
        for T in (TH, TC):
            ex, _sh, _n, _raw = G.extremes(tot, G.conductors(F, T, True, n_ret=6, poe_awg=16), G.box(F))
            mine = rows(F, tot, T)
            chk.append(all(abs(mine[k] - ex[k][0]) < 1e-9 * max(1.0, ex[k][0]) for k in ("VH", "RIB", "RET")))
    R["solver_ok"] = all(chk)

    # 2. V6-B1: the largest Rs each row tolerates
    B1 = []
    for lab, tot in totals.items():
        for T in (TC, TH):
            rt = ratings(F, T)
            for kind in ("RIB", "VH"):
                for which, lim in (("printed", rt[kind][0]), ("least", rt[kind][1])):
                    rs = bisect(lambda x: rows(F, tot, T, x)[kind] <= lim, 0.0, 50.0)
                    rs4 = bisect(lambda x: rows(F, tot, T, x, n_ret=8)[kind] <= lim, 0.0, 50.0)
                    B1.append(dict(case=lab, T=T, kind=kind, which=which, lim=lim, rs=rs, rs4=rs4,
                                   d05=[d_max(rs, a, T, 0.5) for a in LAND_R], d10=[d_max(rs, a, T, 1.0) for a in LAND_R],
                                   d05_4=d_max(rs4, LAND_R[0], T, 0.5)))
    R["B1"] = B1

    def pick(case, T, kind, which):
        return [b for b in B1 if b["case"] == case and b["T"] == T and b["kind"] == kind and b["which"] == which][0]
    R["v6"] = {"dp_rib_pr_cold": pick("the declared upper bound (i)", TC, "RIB", "printed")["rs"],
               "cdev_rib_pr_cold": pick("C-DEV rev 1", TC, "RIB", "printed")["rs"],
               "dp_rib_le_hot": pick("the declared upper bound (i)", TH, "RIB", "least")["rs"],
               "cdev_rib_le_hot": pick("C-DEV rev 1", TH, "RIB", "least")["rs"],
               "dp_vh_pr_cold": pick("the declared upper bound (i)", TC, "VH", "printed")["rs"],
               "cdev_vh_pr_cold": pick("C-DEV rev 1", TC, "VH", "printed")["rs"]}
    R["plane50"] = {T: (r_plane(50e-3, 3e-3, 3, T, 0.5), r_plane(50e-3, 3e-3, 2, T, 0.5)) for T in (TC, TH)}

    # 3. V6-B2: the indirect paths, each at its own worst vertex: total / (1 + R_min x G), G the counted network at every contact high
    a = open(rel(PINS[8]), encoding="utf-8").read()
    vmon = float(need(a, r'_intent\.rail\("VMON", [\d.]+, [\d.]+, ([\d.]+), "U21"', "VMON's declared peak").group(1))
    hf = float(need(a, r'_intent\.rail\("\+12V_HF", [\d.]+, [\d.]+, ([\d.]+), "R65"', "+12V_HF's declared peak").group(1))
    ifs = open(rel(PINS[9]), encoding="utf-8").read()
    n_rf = len(re.findall(r"J_RF(?:3|4|5|6|7|8|9|10|11)\b", need(ifs, r"refs: \[(J_RF3, J_RF4[^\]]*)\]", "IF-BA-RF's board A jacks").group(1)))
    ufl = PT.pdf_text(ROOT, PINS[4], ["-layout"], PDFTEXT, "v2/docs/records/l8r2", universal_newlines=True)
    ufl_outer = float(need(ufl, r"Outer : (\d+) m ohms max\.", "U.FL outer contact resistance").group(1)) * 1e-3
    ufl_has_current = bool(re.search(r"Rated current|Current rating", ufl))
    ph = PT.pdf_text(ROOT, PINS[5], ["-layout"], PDFTEXT, "v2/docs/records/l8r2", universal_newlines=True)
    ph_a = float(need(ph, r"Current rating: (\d+) A AC/DC \(AWG #24", "JST PH current rating").group(1))
    paths = [
        ("each RF pigtail's shield, board B's U.FL to board A's SMA jack (%d pigtails, RG-178, 150 mm: IF-BA-RF)" % n_rf,
         0.150 * RG178_OHM_M * (1 + CU_ALPHA * (TC - 20.0)), "the U.FL outer contact: NO CURRENT RATING PRINTED (Hirose catalogue: %.0f mOhm max at a 10 mA test)" % (ufl_outer * 1e3), None),
        ("the monitor: board A's J_MON pin 2, the monitor's ground, its HDMI cable's grounds to board B's J_HDMI (IF-MON)",
         0.020, "the HDMI receptacle's contacts: Molex 208658's sheet NOT HELD (SOURCES.yaml's owed list)", None),
        ("the QMX: board A's J_HF pin 2, the QMX's ground, its USB cable's ground to board B's J_QMX pin 4 (IF-LID-HF)",
         0.500 * 0.2126, "J_QMX, JST PH: PRINTED %.0f A with AWG 24" % ph_a, ph_a),
        ("board C: board A's J_MAINSW pin 2 (JST XH) and board B's J_PANEL ground pins through board C's ground (IF-AC-MAINSW)",
         0.015, "J_MAINSW (XH) and J_PANEL: their ratings to be read with Layer 7's harness rows (not judged here)", None),
        ("board D: board A's J_MEZZ1 grounds and J_MEZZ_PWR1 pin 2, board D's touch USB to the monitor, the monitor's HDMI to board B",
         0.100, "the chain's weakest: the HDMI receptacle (as the monitor's path)", None)]
    B2 = []
    for lab, tot in totals.items():
        eff = tot + vmon + hf
        for T in (TC,):
            g = rows(F, eff, T)["G_all_hi"]
            for name, rmin, rating, ra in paths:
                B2.append(dict(case=lab, total=eff, name=name, rmin=rmin * 1e3, i=eff / (1 + rmin * 1e3 * g), rating=rating, ra=ra))
    R["B2"] = B2
    R["shares"] = (vmon, hf)
    R["ufl_has_current"] = ufl_has_current
    # the counted rows with the shares added, at Rs = 0 and at the C-DEV printed bound
    R["B2_rows"] = []
    for lab, tot in totals.items():
        eff = tot + vmon + hf
        for T in (TC, TH):
            r0 = rows(F, eff, T)
            rt = ratings(F, T)
            R["B2_rows"].append(dict(case=lab, T=T, eff=eff, rib=r0["RIB"], vh=r0["VH"], ret=r0["RET"],
                                     ok_pr=r0["RIB"] <= rt["RIB"][0] and r0["VH"] <= rt["VH"][0] and r0["RET"] <= rt["RET"][0],
                                     ok_le=r0["RIB"] <= rt["RIB"][1] and r0["VH"] <= rt["VH"][1] and r0["RET"] <= rt["RET"][1]))

    # 4. V6-m12: F-4b
    f4b = float(need(out, r"F-4b the sources' deliverable bound \(four loops at 9\.596 A, U601 at 5\.15 A, PoE 0\.60 A\) ([\d.]+) A", "F-4b's total").group(1))
    r4b = rows(F, f4b, TC)
    r4b8 = rows(F, f4b, TC, n_ret=8)
    R["f4b"] = (f4b, r4b["RIB"], r4b8["RIB"])

    # 5. V6-m8: the XT60 rows
    x12 = PT.pdf_text(ROOT, PINS[6], ["-layout"], PDFTEXT, "v2/docs/records/l8r2", universal_newlines=True) \
        + PT.pdf_text(ROOT, PINS[7], ["-layout"], PDFTEXT, "v2/docs/records/l8r2", universal_newlines=True)
    R["xt_pcb_rating"] = bool(re.search(r"(?i)pcb|solder(ed)? (to|on) (a |the )?board|printed circuit", x12))
    R["xt_row"] = max(rows(F, totals["the declared upper bound (i)"], T)["RET"] for T in (TC, TH))
    ls_ = [b for b in B1 if b["case"].startswith("the largest steady") and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    R["place"] = placement(ls_["d05"][0])
    R["pred"] = predicates(R)
    return R


def predicates(R):
    v = R["v6"]
    P = {}
    P["the solver with Rs = 0 reproduces l8r2_gndret's extremes on every case and both copper ends"] = R["solver_ok"]
    P["V6-B1 reproduced: the ribbon's printed row allows 0.354 mOhm at the declared peak and 0.774 mOhm on C-DEV rev 1 (cold)"] = (
        abs(v["dp_rib_pr_cold"] - 0.354) < 0.0015 and abs(v["cdev_rib_pr_cold"] - 0.774) < 0.0015)
    P["V6-B1 reproduced: the least ratings at the inside air allow 0.143 and 0.438 mOhm"] = abs(v["dp_rib_le_hot"] - 0.143) < 0.0015 and abs(v["cdev_rib_le_hot"] - 0.438) < 0.0015
    cd = [b for b in R["B1"] if b["case"] == "C-DEV rev 1" and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    dp = [b for b in R["B1"] if b["case"] == "the declared upper bound (i)" and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    ls = [b for b in R["B1"] if b["case"].startswith("the largest steady") and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    P["the service cases' printed bounds need the return within 15 to 60 mm of the entries at 0.5 oz (spreading MODEL): a tight cluster"] = (
        15.0 < ls["d05"][0] < cd["d05"][0] < 35.0 and cd["d05"][1] < 65.0)
    P["the declared peak's printed bound is NOT realisable at 0.5 oz within 20 mm (spreading MODEL): the finding stays open there"] = dp["d05"][0] < 20.0
    P["a fourth return lead does not make the declared peak's printed bound realisable at 0.5 oz"] = dp["d05_4"] < 25.0
    P["1 oz inner copper lifts the declared peak's printed bound past 20 mm but not past 50 mm (still a layout question)"] = 20.0 < dp["d10"][0] < 50.0
    P["V6-B2: no indirect branch has a held printed current rating at the RF and HDMI contacts (the branches stay PROVISIONAL)"] = not R["ufl_has_current"]
    P["V6-B2: with the monitor's and the QMX's shares added the counted rows hold on the printed ratings at Rs = 0"] = all(r["ok_pr"] for r in R["B2_rows"])
    P["V6-m12: F-4b puts a ribbon over its printed 1 A by under 1 percent; the fourth lead would hold it"] = 1.0 < R["f4b"][1] < 1.01 and R["f4b"][2] < 1.0
    P["V6-m8: neither XT60 sheet names a board-soldered end"] = not R["xt_pcb_rating"]
    pl = R["place"]
    P["L8R2-F33a on the placement as drawn: one cluster of sockets is NOT within reach of every 5 V entry on board B"] = not pl["met_one"]
    P["the group-centre construction is a geometric reading only: each group's centre lies within the reach of its own lands"] = pl["met_split"]
    return P


def render(R):
    F, v = R["F"], R["v6"]
    L = []
    w = L.append
    w("l8r2_p0: record l8r2, P0 round (Slot A, MESHSAT-1357, 5 October 2026): V6's findings on the dedicated return, corrected or disposed")
    w("of. PROTOTYPE DESIGN, DESK ARITHMETIC: nothing built, bought, powered or measured. Labels: PRINTED, TYPICAL, DECLARED, MODEL,")
    w("ASSUMPTION, MISSING, PROVISIONAL (the owner's part 19: a bounded provisional choice with its validation task).")
    w("")
    w("0. PINS (sha256/16  path)")
    for p, s in R["pins"]:
        w("   %s %s" % (s, p))
    w("")
    w("1. THE SOLVER: l8r2_gndret.py's conductors, contact box and monotone vertex, imported unchanged; ONE term added, Rs in series with")
    w("   the dedicated return's bundle. At Rs = 0 it reproduces the record's enumerated extremes on every case and both copper ends: %s" % (
        "yes" if R["solver_ok"] else "NO"))
    w("   the totals (A): " + "; ".join("%s %.4f" % kv for kv in R["totals"].items()))
    u = R["u601"]
    w("   C-DEV rev 2 (conditional on FW-B20/B21, the coordinator's row of 16:00 with its 16:25 clarification): +5V_IOC %.4f A in place of %.4f A," % (u[3], u[2]))
    w("     read by the record's constant-power method as U601 %.4f A in place of %.4f A; U7's device-rail demand is unchanged (6.0359 A: the" % (u[1], u[0]))
    w("     supervisors left +5V_DEV with record l9t5's I-03 drafts); rev 1's figures stay beside it as the labelled scenario")
    w("")
    w("2. V6-B1: THE PLANE COPPER IN SERIES WITH THE RETURN BUNDLE")
    w("   the largest series Rs (mOhm, both boards together) each row tolerates (printed: the maker's rating; least: the least rating")
    w("   consistent with its sheet at the inside air, INFERRED in l8r2_gndret 3b), and the land separation (mm) a layout may have on the")
    w("   declared stackups at the corner's copper temperature, both boards at the same separation, inner copper %.0f %% thin (ASSUMPTION)," % (100 * THK_TOL))
    w("   for a land group of radius %.1f and %.1f mm (spreading MODEL: R = rho / t / (n pi) x ln(d / a) a board; A n = %d, B n = %d)" % (
        LAND_R[0] * 1e3, LAND_R[1] * 1e3, PLANES["a"], PLANES["b"]))
    w("   %-44s %-7s %-4s %-8s %8s %9s %18s %18s %10s" % ("case", "copper", "row", "rating", "limit A", "Rs mOhm", "d 0.5 oz mm", "d 1 oz mm", "4 leads d"))
    def mm(x):
        return "%7.1f" % x if x < 1000.0 else "  >1000"
    for b in R["B1"]:
        if b["T"] == TC and b["which"] == "least":
            continue                                    # at the cold end the least rating is the printed one
        w("   %-44s %+6.2fC %-4s %-8s %8.4f %9.4f %8s / %7s %8s / %7s %10s" % (
            b["case"][:44], b["T"], b["kind"], b["which"], b["lim"], b["rs"], mm(b["d05"][0]), mm(b["d05"][1]), mm(b["d10"][0]), mm(b["d10"][1]), mm(b["d05_4"])))
    w("   V6's figures reproduced: the ribbon's printed row %.4f mOhm (declared peak) and %.4f mOhm (C-DEV rev 1) cold; the least rows %.4f and" % (
        v["dp_rib_pr_cold"], v["cdev_rib_pr_cold"], v["dp_rib_le_hot"]))
    w("     %.4f mOhm hot; a VH pin 2's printed %.4f and %.4f mOhm; V6's scale, 50 mm between 3 mm lands at 0.5 oz: board B %.3f / %.3f and" % (
        v["cdev_rib_le_hot"], v["dp_vh_pr_cold"], v["cdev_vh_pr_cold"], R["plane50"][TC][0], R["plane50"][TH][0]))
    w("     board A %.3f / %.3f mOhm (cold / hot; nominal thickness)" % (R["plane50"][TC][1], R["plane50"][TH][1]))
    cd = [b for b in R["B1"] if b["case"] == "C-DEV rev 1" and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    c2 = [b for b in R["B1"] if b["case"].startswith("C-DEV rev 2") and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    ls = [b for b in R["B1"] if b["case"].startswith("the largest steady") and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    dp = [b for b in R["B1"] if b["case"] == "the declared upper bound (i)" and b["which"] == "printed" and b["kind"] == "RIB" and b["T"] == TC][0]
    w("   READ (the binding row is the ribbon at the cold end on the printed rating, the least rating at the hot end):")
    w("     the service cases on the printed ratings: C-DEV rev 1 tolerates %.4f mOhm, %.0f to %.0f mm at 0.5 oz; C-DEV rev 2 %.4f mOhm, %.0f to" % (
        cd["rs"], cd["d05"][0], cd["d05"][1], c2["rs"], c2["d05"][0]))
    w("       %.0f mm; the largest steady state %.4f mOhm, %.0f to %.0f mm: realisable ON THE MODEL only as a TIGHT CLUSTER, the three return" % (
        c2["d05"][1], ls["rs"], ls["d05"][0], ls["d05"][1]))
    w("       sockets beside the 5 V leads' entries on board B and beside the 5 V stages' outputs on board A, joined solidly (L8R2-F33's")
    w("       widths) on every ground plane; whether the floor plans allow it is a placement question no board here answers yet")
    w("     the declared upper bound (every lead at its declared peak at once) on the printed ratings: %.4f mOhm, %.1f mm at 0.5 oz: NOT" % (dp["rs"], dp["d05"][0]))
    w("       realisable with XT60 and VH bodies (each wider than that); a fourth lead gives %.1f mm (NOT A CORRECTION); 1 oz inner copper gives" % dp["d05_4"])
    w("       %.0f to %.0f mm (a = 1.5 to 3 mm; still a placement question): the copper weight is the owner's open decision (record l9stk 14.7;" % (dp["d10"][0], dp["d10"][1]))
    w("       the surcharge NOT READ); it is a DECLARATION bound (every lead at its declared peak at once), above every state of the budget")
    w("     the least ratings at the inside air (INFERRED derating): not realisable at 0.5 oz for any case (see the table)")
    pl = R["place"]
    w("   2b. L8R2-F33a ON THE PLACEMENT AS DRAWN (the owner's amendment 1, the coordinator's INBOX 11): each 5 V lead's ground land (pin 2)")
    w("     read from the placed boards (pinned above; footprint blocks parsed), the distance a return socket may have: %.1f mm (the largest" % pl["a"]["need"])
    w("     steady state, 0.5 oz, a 1.5 mm land group)")
    for b in ("a", "b"):
        q = pl[b]
        w("     board %s: %s; %s" % (b.upper(), "; ".join("%s (%.2f, %.2f)" % (r, x, y) for r, (x, y) in sorted(q["land"].items())),
                                     "J_5V_IOC not placed (record l9t5's I-03 lead, Layer 10's placement)" if "J_5V_IOC" not in q["land"] else "J_5V_IOC placed"))
        w("       ONE CLUSTER for every entry: the smallest circle holding them has radius %.1f mm: %s" % (q["one"], "within reach" if q["one"] <= q["need"] else "NOT within reach"))
        w("       ONE SOCKET A GROUP: " + "; ".join("%s %.1f mm from a socket at the group's centre (lands %.1f mm apart)%s" % (
            " with ".join(g[0]), g[1], g[3], (", %s to be placed beside it" % ", ".join(g[2])) if g[2] else "") for g in q["groups"]))
    w("     READ: the three sockets as one cluster cannot serve board B's entries (they sit %.0f mm apart at most). The group-centre" % (2 * pl["b"]["one"]))
    w("       construction above (each group's centre at most %.1f mm from its lands) places no footprint, reads no courtyard and solves no" % (
        max(g[1] for b in ("a", "b") for g in pl[b]["groups"])))
    w("       current: it is NOT evidence that the condition is realisable, and round 1 of this section's claim to that effect is WITHDRAWN")
    w("       (the focused check cx45, Q2; SESSION L8R2-D9 withdrawn with it). The sockets placed with their courtyards on both boards and")
    w("       the return studied as a distributed network on a stand-in land, assumed sites and fill: l8r2_dist.out (SESSION L8R2-D10), a")
    w("       STUDY; after cx46 V6-B1 stays OPEN as REMAINING ENGINEERING")
    w("   DISPOSITION (part 19; after cx46 OPEN, REMAINING ENGINEERING for the receiving company): V6-B1 is not closed. The bounded")
    w("     provisional choice: the layout condition L8R2-F33a, each return")
    w("     socket's land within %.0f mm (the largest steady state, the tightest service case) of the 5 V entries it serves on both boards" % ls["d05"][0])
    w("     (one socket a group; placed and studied as a distributed network in l8r2_dist.out, which replaces this condition's form), every")
    w("     ground plane joined solidly; the Layer 10")
    w("     validation task: extract on the routed boards A and B the plane resistance between the return sockets' lands and each lead's and")
    w("     stage's land (a field solver; specimen: the routed board files; limit: the table's Rs for each case). STILL OPEN: the declared")
    w("     upper bound's printed row and every least-rating row at 0.5 oz, which no placement realises; the smallest decision that removes")
    w("     them is not available inside engineering: the owner's copper weight (1 oz inner on boards A and B, cost not read) only shortens")
    w("     the gap, and re-deriving the leads' declared peaks from the budget is Layer 5's and Layer 9's text; the declared upper bound's")
    w("     printed row reads STILL OPEN (a declaration bound, not a service case) and the service cases PROVISIONAL on the layout condition")
    w("")
    w("3. V6-B2: THE INDIRECT GROUND PATHS BETWEEN THE BOARDS (each at its own worst vertex: total / (1 + R_min x G), G the counted network")
    w("   at every contact high; the totals carry the monitor's %.2f A (VMON's declared peak) and the QMX's %.2f A (+12V_HF's) as if every ampere" % R["shares"])
    w("   of their return came back through board B: the conservative share)")
    for lab in R["totals"]:
        rows_ = [b for b in R["B2"] if b["case"] == lab]
        w("   %s (total with the shares %.4f A):" % (lab, rows_[0]["total"]))
        for b in rows_:
            w("     %-128s" % b["name"][:128])
            w("       R_min %.2f mOhm (ASSUMPTION, no cable sheet held; contacts at 0, none prints a minimum): at most %.4f A; %s" % (b["rmin"], b["i"], b["rating"]))
    w("   the counted rows with the shares added, at Rs = 0:")
    for r in R["B2_rows"]:
        w("     %-44s %+6.2fC total %.4f A: a ribbon %.4f A, a VH pin 2 %.4f A, an XT60 contact %.4f A; printed %s, least %s" % (
            r["case"][:44], r["T"], r["eff"], r["rib"], r["vh"], r["ret"], "yes" if r["ok_pr"] else "NO", "yes" if r["ok_le"] else "NO"))
    w("   DISPOSITION: the census is complete for the paths V6 named; the counted rows hold with the shares on the printed ratings. The claim")
    w("     'every branch with a printed rating is inside it' covers the COUNTED branches only. The indirect branches are PROVISIONAL: the")
    w("     RF pigtails' U.FL outer contacts carry up to the figures above with NO printed current rating (vendor task, UNSENT: Hirose, the U.FL")
    w("     outer contact's DC current rating at 85 C), the HDMI receptacle's sheet is NOT HELD (vendor task: Molex 208658), and every R_min is")
    w("     an ASSUMPTION until Layer 7's harness rows name the cables (Layer 7 task: each cable's conductor resistance). If the U.FL rating")
    w("     comes back under the bound, the design change is to break the DC path at board A's RF jacks (an RF ground coupled by capacitors),")
    w("     an RF and EMC design task with the antennas' bias returns traced; it is not drafted here")
    w("")
    f4b, rib, rib8 = R["f4b"]
    w("4. V6-m12: F-4b, EVERY SOURCE AT ITS BOUND AT ONCE (%.4f A): a ribbon conductor %.5f A at -20 C against its printed 1 A (with a fourth lead %.4f A)" % (f4b, rib, rib8))
    w("   DECISION (authority: SESSION; authority_why: a fault-set definition inside engineering, no requirement, money or claim changes;")
    w("   ruled_by: Slot A under the owner's standing rule of 26 September 2026; ruled_on: 5 October 2026; reversed_by: none): the design need")
    w("   not serve F-4b inside the ribbons' printed rating. Reason: F-4b is five independent overloads at once (four stage current limits and")
    w("   U601's), outside the single-failure set the architecture's failure table names (ARCH-PCB-B-IOHA section 12: every row one failure);")
    w("   each single overload (F-4a) holds; the excess is %.2f %% at the cold end at the extreme contact vertex only. Reverse: carry the fourth" % (100 * (rib - 1.0)))
    w("   return lead (%.4f A there)." % rib8)
    w("")
    w("5. V6-m8: THE XT60 ROWS. Neither held XT60 sheet (V1.2: 30 A, no condition; 2021V1: 35 A with 12 AWG, rise under 85 C) names a")
    w("   board-soldered end: %s. The rows' largest XT60 contact current %.4f A is judged against the printed 30 A as the WIRE-TO-WIRE rating, a" % (
        "a board end is named" if R["xt_pcb_rating"] else "none is named", R["xt_row"]))
    w("   %.0f %% margin; the board-soldered end's rating is MISSING (vendor task, UNSENT: Amass, the XT60-F's rating soldered into a board, its" % (
        100 * (1 - R["xt_row"] / 30.0)))
    w("   land and the board's copper), PROVISIONAL with that margin")
    w("")
    w("6. PREDICATES")
    for k, val in R["pred"].items():
        w("   %-132s %s" % (k, "yes" if val else "NO"))
    w("")
    w("l8r2_p0: done")
    return "\n".join(L) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    return 0 if all(R["pred"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
