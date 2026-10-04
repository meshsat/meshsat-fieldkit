#!/usr/bin/env python3
"""Layer 9 item 9.12, record l9stk (MESHSAT-1357, 3 October 2026): the numbers behind one stackup decision per board.

Desk arithmetic on committed files and on dated public price readings. Nothing here was built, routed, bought or quoted.
It computes, from pinned inputs only:

  1. each board's outline from its committed board file (the Edge.Cuts bounding box), its area, the area of the
     project's minimum order (five of each board, the owner's rule) and where the outline sits against the size classes
     the fabricator's public pages print (JLC-5: the 102 x 102 mm special price class and the 650 cm2 large board fee);
  2. the copper: the band widths of every rail at or above 5 A on boards A, E, P and E5 at 1 oz and at 2 oz, on one face
     and shared by two (track_current.width_for_current, decision 35's ruled model, 10 K); the barrels per transition
     (via_current.barrels_for); three bounds stated with their method (board E's cross-section demand, the pack return
     on the inner planes of A and E, and the share of board P's pack return the inner GND planes take, which decides
     P's inner copper weight); the inner width each of board B's 5 V domains needs on In4; C's and D's largest rail;
  3. the fabricator floors at 2 oz as two of its pages print them, and the copper gap of the 0.4 mm pitch parts on
     A, E and P against the 2 oz solder-mask bridge;
  4. the impedance targets each board declares (pcb_interfaces.yaml) and the trace geometry on the decided stack from
     the repository's 2D field solves (layout-constraints/calc/stack_solves.out, atlc 4.6.1), never IPC-2141;
  5. the price readings (inputs/price-readings-2026-10-03.json) per board: what applies, the deltas at the printed
     conditions, and what is NOT READ;
  6. the predicates test_l9stk.py holds.

Run from the repository root: python3 v2/docs/records/l9stk/l9stk_stackups.py
The committed output is regenerated only through _bin/regen_out.py (two identical runs, every pin current). Stdlib plus
the two tool modules; no KiCad, no network, no date, no host name, so a second run prints the same bytes.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import track_current as tc  # noqa: E402
import via_current as vc    # noqa: E402

PINS = {
    "track_current": "v2/ecad/tools/track_current.py",
    "via_current": "v2/ecad/tools/via_current.py",
    "stack_solves": "v2/docs/layout-constraints/calc/stack_solves.out",
    "stackup_write": "v2/ecad/tools/stackup_write.py",
    "interfaces": "v2/ecad/tools/pcb_interfaces.yaml",
    "fab_stackups": "v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md",
    "fab_caps": "v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md",
    "prices": "v2/docs/records/l9stk/inputs/price-readings-2026-10-03.json",
    "fp_rsm0032a": "v2/ecad/meshsat.pretty/Texas_RSM0032A_VQFN-32-1EP_4x4mm_P0.4mm_EP1.4x1.4mm.kicad_mod",
    "board_a": "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb",
    "board_b": "v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb",
    "board_c": "v2/ecad/pcb-c-display-c8/pcb-c-display.kicad_pcb",
    "board_d": "v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_pcb",
    "board_e": "v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb",
    "board_e5": "v2/ecad/pcb-e5-block/pcb-e5-block.kicad_pcb",
    "board_p": "v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb",
    "intent_a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json",
    "intent_b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json",
    "intent_c": "v2/ecad/pcb-c-display-c8/out/pcb-c-display-intent.json",
    "intent_d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json",
    "intent_e": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock-intent.json",
    "intent_p": "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json",
}
BOARDS = ("a", "b", "c", "d", "e", "p", "e5")
NAMES = {"a": "A power and I/O", "b": "B compute", "c": "C panel backer", "d": "D APRS", "e": "E dock strip",
         "p": "P pack BMS", "e5": "E5 dock block"}
QTY = 5                       # the owner's rule: "minimum is 5 of each"
PACK_A = 18.0                 # PWR-F12: 18 A for 60 s, judged as a service current (rail_widths.py, POWER-THERMAL section 10)
BIG_A = 5.0                   # the rails this record sizes at both weights: at or above 5 A typical, or on the pack path
OZ = {"1 oz": 1.0, "2 oz": 2.0}
INNER_HALF_OZ = 0.0152 / 0.035   # JLCPCB's 0.5 oz inner, finished 0.0152 mm (stackup_write.STACKS)
INNER_ONE_OZ = 1.0
DRILL = 0.4
# the pack path's roots per board (rail_widths.py BOARDS, the same list), and the rails a series or return declaration adds
PACK_ROOTS = {"a": ("CELL+", "CELL_FUSED", "VBAT"), "e": ("CELL+", "CELL_F"), "p": ("PACK_P", "CELL4", "FUSED", "SCP_OUT", "PACK_N")}
# the decided or ruled stack per board: (STACKS row, copper layers, the authority behind the row)
STACK = {"a": ("JLC06161H-3313", 6, "count MEASURED (345 open at four); the row is the board file's"),
         "b": ("JLC08161H-2116", 8, "the design input this record takes, conditional on decision 43's route"),
         "c": ("JLC06161H-3313", 6, "owner decision 27"),
         "d": ("JLC04161H-7628", 4, "the board file's row, kept"),
         "e": ("JLC04161H-7628", 4, "the board file's row, kept"),
         "p": ("JLC04162H-7628", 4, "owner decision 28 and ruling 7 (2 oz outer); inner weight this record's"),
         "e5": ("2L-2oz", 2, "owner ruling 7")}


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l9stk_stackups: REFUSED: %s\n" % msg)
    sys.exit(2)


# ------------------------------------------------------------------------------------------------ 1. outlines
def outline(path):
    """The Edge.Cuts bounding box of a board file's top-level graphics (the footprints' own edges excluded)."""
    t = open(rel(path), encoding="utf-8").read()
    xs, ys = [], []
    for m in re.finditer(r"\n\t\(gr_(line|arc|rect|poly|circle)\b", t):
        i, d = m.start() + 1, 0
        while i < len(t):
            if t[i] == "(":
                d += 1
            elif t[i] == ")":
                d -= 1
                if d == 0:
                    break
            i += 1
        blk = t[m.start():i + 1]
        if '"Edge.Cuts"' not in blk:
            continue
        for q in re.finditer(r"\((?:start|end|mid|xy|center) ([-0-9.]+) ([-0-9.]+)\)", blk):
            xs.append(float(q.group(1)))
            ys.append(float(q.group(2)))
    if not xs:
        refuse("%s has no Edge.Cuts outline" % path)
    ncu = len(re.findall(r'^\s+\(\d+ "(?:F|B|In\d+)\.Cu" ', t, re.M))
    return round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), ncu


# ------------------------------------------------------------------------------------------------ 2. copper
def intent(b):
    return json.load(open(rel(PINS["intent_" + b]), encoding="utf-8"))


def pack_path(b, rails):
    roots = set(PACK_ROOTS.get(b, ()))
    out = set(roots)
    for k, v in rails.items():
        for key in ("series_of", "returns"):
            if v.get(key) in roots and float(v.get("amps_typ", 0)) == float(rails[v[key]].get("amps_typ", 0)) \
                    and float(v.get("amps_peak", 0)) == float(rails[v[key]].get("amps_peak", 0)):
                out.add(k)
    return out


def governing(b, k, v, pp):
    return PACK_A if k in pp else float(v.get("amps_typ", 0))


def widths(amps):
    r = {}
    for lab, oz in OZ.items():
        r[lab] = (tc.width_for_current(amps, oz=oz), tc.width_for_current(amps / 2.0, oz=oz))
    return r


def big_rails(b):
    d = intent(b)["rails"]
    pp = pack_path(b, d)
    rows = []
    for k in sorted(d, key=lambda x: (-governing(b, x, d[x], pp), x)):
        g = governing(b, k, d[k], pp)
        if k in pp or g >= BIG_A:
            rows.append((k, float(d[k].get("amps_typ", 0)), float(d[k].get("amps_peak", 0)), g, k in pp))
    return rows


def plane_share(i_total, w_out, faces_out, t_out, w_plane, t_in, planes=2):
    """The share of a return current the inner planes take when they run beside the outer bands over the same path and
    are tied to them at both ends: a one-dimensional parallel-conductor model, the planes' conductance against the
    bands' by cross-section (copper is one material). It neglects current crowding at the via fields and the planes'
    spreading, which a solved mesh (dc_drop on the routed board) reads; it is a bound to choose a row by, not a reading."""
    g_out = faces_out * t_out * w_out
    g_in = planes * t_in * w_plane
    s = g_in / (g_in + g_out)
    per = i_total * s / planes
    rating, model = tc.conservative(t_in * w_plane)       # the internal fits: the inner layers
    return s, per, rating, model


def failing_band(i_total, w_out, faces_out, t_out, t_in, planes=2, step=0.05, top=200.0):
    """The plane widths at which plane_share puts a plane over its rating, scanned in fixed steps (deterministic): the
    share grows with the width and the rating grows sublinearly, so the excess, where there is one, is a band of narrow
    widths (a plane necked to a strip beside the run), never a wide plane. Returns (lowest, highest) or None."""
    bad = []
    n = 1
    while n * step <= top:
        w = round(n * step, 4)
        s, per, r, m = plane_share(i_total, w_out, faces_out, t_out, w, t_in, planes)
        if per > r:
            bad.append(w)
        n += 1
    return (bad[0], bad[-1]) if bad else None


# ------------------------------------------------------------------------------------------------ 3. floors and pitch
def fab_floor_2oz():
    t = open(rel(PINS["fab_stackups"]), encoding="utf-8").read()
    m = re.search(r"Minimum track width and spacing at 2 oz, multilayer: ([0-9.]+) / ([0-9.]+) mm", t)
    b = re.search(r"2 oz ([0-9.]+) mm \(any colour\)", t)
    one = re.search(r"\| 1 oz, multilayer \| ([0-9.]+) / ([0-9.]+) mm", open(rel(PINS["fab_caps"]), encoding="utf-8").read())
    if not (m and b and one):
        refuse("a floor line of the fabricator transcriptions moved")
    pr = json.load(open(rel(PINS["prices"]), encoding="utf-8"))
    guide = [r for r in pr["readings"] if r["id"] == "JLC-6"][0]
    g = re.search(r"2oz Any layer FR4 ([0-9.]+) mm", " ".join(guide["excerpts"]))
    if not g:
        refuse("JLC-6 no longer carries its 2 oz line")
    return {"caps_2oz_track": float(m.group(1)), "guide_2oz_track": float(g.group(1)), "bridge_2oz": float(b.group(1)),
            "track_1oz_multi": float(one.group(1))}


def pad_gap(path, fp_name=None):
    """(reference, pitch, pad width across the pitch, copper gap) from pads "2" and "3" of a footprint."""
    t = open(rel(path), encoding="utf-8").read()
    ref = "footprint file"
    if fp_name:
        m = re.search(r'\(footprint "[^"]*%s[^"]*"' % re.escape(fp_name), t)
        if not m:
            refuse("%s not in %s" % (fp_name, path))
        e = t.find("\n\t(footprint ", m.start() + 10)
        t = t[m.start():e if e > 0 else len(t)]
        r = re.search(r'\(property "Reference" "([^"]+)"', t)
        ref = r.group(1) if r else "?"
    pads = {}
    for q in re.finditer(r'\(pad "(\d+)" smd \w+\s*\(at ([-0-9. ]+)\)\s*\(size ([0-9.]+) ([0-9.]+)\)', t):
        pads.setdefault(q.group(1), ([float(x) for x in q.group(2).split()[:2]], float(q.group(3)), float(q.group(4))))
    a, b = pads["2"], pads["3"]
    dx, dy = abs(a[0][0] - b[0][0]), abs(a[0][1] - b[0][1])
    pitch = round((dx * dx + dy * dy) ** 0.5, 3)
    across = a[2] if dy > dx else a[1]
    return ref, pitch, across, round(pitch - across, 3)


# ------------------------------------------------------------------------------------------------ 4. impedance
def solves():
    """{section: {"grid": {s: [(w, z)]}, "w": {(s, target): w}, "se": w50}} from stack_solves.out."""
    out, cur = {}, None
    for line in open(rel(PINS["stack_solves"]), encoding="utf-8"):
        m = re.match(r"## ([\w-]+): ", line)
        if m:
            cur = m.group(1)
            out[cur] = {"grid": {}, "w": {}, "se": None, "cols": []}
            continue
        if cur is None:
            continue
        m = re.match(r"\s+w \\ s\s+(.*)$", line)
        if m:
            out[cur]["cols"] = [float(x) for x in m.group(1).split()]
            continue
        m = re.match(r"\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*$", line)
        if m and out[cur]["cols"]:
            w = float(m.group(1))
            for s, z in zip(out[cur]["cols"], (float(m.group(2)), float(m.group(3)), float(m.group(4)))):
                out[cur]["grid"].setdefault(s, []).append((w, z))
            continue
        m = re.match(r"\s+gap ([0-9.]+) -> (.*)$", line)
        if m:
            s = float(m.group(1))
            for part in m.group(2).split(";"):
                q = re.match(r"\s*(\d+) ohm: w ([0-9.]+)", part)
                if q:
                    out[cur]["w"][(s, int(q.group(1)))] = float(q.group(2))
            continue
        m = re.match(r"\s+50 ohm single-ended -> w ([0-9.]+)", line)
        if m:
            out[cur]["se"] = float(m.group(1))
    return out


def z_at(sol, sec, w, s):
    pts = sorted(sol[sec]["grid"][s])
    for (w0, z0), (w1, z1) in zip(pts, pts[1:]):
        if w0 <= w <= w1:
            return z0 + (z1 - z0) * (w - w0) / (w1 - w0)
    return None


def z_bilinear(sol, sec, w, s):
    cols = sorted(sol[sec]["grid"])
    for s0, s1 in zip(cols, cols[1:]):
        if s0 <= s <= s1:
            a, b = z_at(sol, sec, w, s0), z_at(sol, sec, w, s1)
            return a + (b - a) * (s - s0) / (s1 - s0)
    return None


# ------------------------------------------------------------------------------------------------ 5. prices
def prices():
    return json.load(open(rel(PINS["prices"]), encoding="utf-8"))


def compute():
    for k, p in PINS.items():
        if not os.path.isfile(rel(p)):
            refuse("pinned input %s (%s) is missing" % (k, p))
    R = {"pins": {k: (p, sha(p)) for k, p in PINS.items()}}
    # 1 outlines
    O = {}
    for b in BOARDS:
        w, h, ncu = outline(PINS["board_" + b])
        a = w * h / 100.0
        O[b] = {"w": w, "h": h, "ncu": ncu, "area_cm2": round(a, 2), "order_m2": round(a * QTY / 1e4, 4),
                "special": w <= 102.0 and h <= 102.0, "large": a > 650.0, "within_100": max(w, h) <= 100.0 and min(w, h) <= 100.0}
    R["outline"] = O
    # 2 copper
    C = {}
    for b in ("a", "e", "p"):
        C[b] = [(k, typ, peak, g, pp, widths(g), vc.barrels_for(max(g, peak), DRILL)) for k, typ, peak, g, pp in big_rails(b)]
    C["e5"] = [("CELL+", 10.0, 18.0, PACK_A, True, widths(PACK_A), vc.barrels_for(PACK_A, DRILL)),
               ("CELL_N", 10.0, 18.0, PACK_A, True, widths(PACK_A), vc.barrels_for(PACK_A, DRILL))]
    R["copper"] = C
    # board E's cross-section demand: every listed conductor side by side, plus the pack path's undeclared return
    e_rows = {k: g for k, typ, peak, g, pp, wd, br in C["e"]}
    chain_pick = ["CELL_F", "VIN_RAW", "TRK_OUT", "DC_IN", "PV_P"]
    for k in chain_pick:
        if k not in e_rows:
            refuse("board E's intent no longer declares %s" % k)
    cs = {}
    for lab, oz in OZ.items():
        one = sum(tc.width_for_current(e_rows[k], oz=oz) for k in chain_pick) + tc.width_for_current(PACK_A, oz=oz)
        two = sum(tc.width_for_current(e_rows[k] / 2.0, oz=oz) for k in chain_pick) + tc.width_for_current(PACK_A / 2.0, oz=oz)
        cs[lab] = (one, two)
    R["e_cross"] = {"rails": chain_pick, "strip_mm": O["e"]["h"], "sum": cs}
    # the pack return on the inner GND planes alone, A (In1 and In4) and E (In1)
    R["return_inner"] = {
        "a": {"planes": 2, "half_oz": tc.width_for_current(PACK_A / 2.0, oz=INNER_HALF_OZ, internal=True),
              "one_oz": tc.width_for_current(PACK_A / 2.0, oz=INNER_ONE_OZ, internal=True), "short_side": O["a"]["h"]},
        "e": {"planes": 1, "half_oz": tc.width_for_current(PACK_A, oz=INNER_HALF_OZ, internal=True),
              "one_oz": tc.width_for_current(PACK_A, oz=INNER_ONE_OZ, internal=True), "short_side": O["e"]["h"]},
    }
    rd = intent("a")["rails"]; ed = intent("e")["rails"]
    R["return_declared"] = {"a": sorted(k for k, v in rd.items() if v.get("returns")), "e": sorted(k for k, v in ed.items() if v.get("returns"))}
    # board P: the inner GND planes' share of the pack return, and the narrowest plane each inner weight holds
    t_out = 0.070
    w2 = tc.width_for_current(PACK_A / 2.0, oz=2.0)
    w1 = tc.width_for_current(PACK_A, oz=2.0)
    P = {"w_two_faces": w2, "w_one_face": w1, "rows": [], "wmin": {}}
    for lab, t_in in (("0.5 oz", 0.0152), ("1 oz", 0.035)):
        for wp in (40.0, 30.0, 20.0):
            for faces, wo in ((2, w2), (1, w1)):
                s, per, r, m = plane_share(PACK_A, wo, faces, t_out, wp, t_in)
                P["rows"].append((lab, wp, faces, wo, s, per, r, m))
        P["wmin"][lab] = failing_band(PACK_A, w2, 2, t_out, t_in)
    s, per, r, m = plane_share(PACK_A, w2, 2, t_out, O["p"]["h"] - 2 * 1.0, 0.0152)
    P["at_board"] = (O["p"]["h"] - 2 * 1.0, s, per, r, m, vc.barrels_for(PACK_A * s, DRILL))
    R["p_planes"] = P
    # board B: each 5 V domain's In4 width at 0.5 oz; C and D: the largest rail
    bd = intent("b")["rails"]
    R["b_in4"] = [(k, float(bd[k]["amps_typ"]), tc.width_for_current(float(bd[k]["amps_typ"]), oz=INNER_HALF_OZ, internal=True))
                  for k in ("+5V_DEV", "+5V_S1", "+5V_S2", "+5V_S3") if k in bd]
    if len(R["b_in4"]) != 4:
        refuse("board B's intent no longer declares the four 5 V domains")
    for b in ("c", "d"):
        dd = intent(b)["rails"]
        k = max(sorted(dd), key=lambda x: float(dd[x].get("amps_typ", 0)))
        R["max_" + b] = (k, float(dd[k]["amps_typ"]), tc.width_for_current(float(dd[k]["amps_typ"]), oz=1.0))
    # 3 floors and pitch
    F = fab_floor_2oz()
    F["pitch"] = {"a": pad_gap(PINS["board_a"], "QFN-32-1EP_4x4mm_P0.4mm"),
                  "e": pad_gap(PINS["board_e"], "QFN-56-1EP_7x7mm_P0.4mm"),
                  "p": ("U1 (RSM0032A)",) + pad_gap(PINS["fp_rsm0032a"])[1:]}
    R["floors"] = F
    # 4 impedance
    S = solves()
    for need in ("6L-out", "8L-out", "8L-in", "se-4L", "se-6L", "se-8L", "6L-in-asis", "6L-A2-In2"):
        if need not in S:
            refuse("stack_solves.out has no section %s" % need)
    imp = {}
    imp["a"] = [("USB2_CM5 ribbon pairs (USB_D8, USB_E6, USB_WALL), F.Cu and B.Cu", 90, "6L-out", S["6L-out"]["w"][(0.127, 90)], 0.127,
                 z_at(S, "6L-out", S["6L-out"]["w"][(0.127, 90)], 0.127)),
                ("RF drops J_RF to J_BM, 50 ohm single-ended, F.Cu", 50, "se-6L", S["se-6L"]["se"], None, None)]
    w90 = max(S["8L-out"]["w"][(0.127, 90)], S["8L-in"]["w"][(0.127, 90)])
    w100 = max(S["8L-out"]["w"][(0.127, 100)], S["8L-in"]["w"][(0.127, 100)])
    imp["b"] = [("class USB: PCIE_CM5, USB3_CM5, USB2_CM5 (90) and PCIE_M2_MODULE (85), outer", 90, "8L-out", w90, 0.127, z_at(S, "8L-out", w90, 0.127)),
                ("class USB, inner (In2, In5)", 90, "8L-in", w90, 0.127, z_at(S, "8L-in", w90, 0.127)),
                ("class DIFF100: ETHERNET_CM5, HDMI_CM5, outer", 100, "8L-out", w100, 0.127, z_at(S, "8L-out", w100, 0.127)),
                ("class DIFF100, inner (In2, In5)", 100, "8L-in", w100, 0.127, z_at(S, "8L-in", w100, 0.127)),
                ("RF 50 ohm single-ended, outer only", 50, "se-8L", S["se-8L"]["se"], None, None)]
    imp["d"] = [("the RF path RF_PAOUT to J_ANT, 50 ohm single-ended, F.Cu over In1", 50, "se-4L", S["se-4L"]["se"], None, None)]
    six = {"in2_90": S["6L-in-asis"]["w"].get((0.127, 90)), "in2_100": S["6L-in-asis"]["w"].get((0.127, 100)),
           "in2_85": S["6L-in-asis"]["w"].get((0.127, 85)), "out_90": S["6L-out"]["w"][(0.127, 90)],
           "out_100": S["6L-out"]["w"][(0.127, 100)], "a2_90": S["6L-A2-In2"]["w"][(0.127, 90)]}
    R["imp"] = imp
    R["six_b"] = six
    R["usb_2oz_ref"] = z_bilinear(S, "6L-out", 0.16, 0.16)
    R["usb_class_a"] = z_bilinear(S, "6L-out", 0.127, 0.13)
    # 5 prices
    PR = prices()
    R["price_ids"] = [r["id"] for r in PR["readings"]]
    R["price_not_read"] = PR["not_read"]
    fig = []
    for r in PR["readings"]:
        for f in r["figures"]:
            fig.append((r["id"], r["vendor"], f))
    R["figures"] = fig
    deltas = []
    for rid, lay_lo, lay_hi in (("JLC-1", 4, 6), ("NXP-1", 2, 4), ("NXP-1", 4, 6)):
        lo = [f for i, v, f in fig if i == rid and f.get("layers") == lay_lo and f.get("usd")]
        hi = [f for i, v, f in fig if i == rid and f.get("layers") == lay_hi and f.get("usd")]
        if lo and hi:
            deltas.append((rid, lay_lo, lay_hi, lo[0]["usd"], hi[0]["usd"], hi[0]["usd"] - lo[0]["usd"]))
    R["deltas"] = deltas
    # 6 predicates
    pr = {}
    pr["every board has an outline from its board file and a stack"] = all(O[b]["w"] > 0 and b in STACK for b in BOARDS)
    pr["B and C exceed the fabricator's 650 cm2 large board threshold; D, P and E5 sit in its 102 x 102 mm class"] = \
        O["b"]["large"] and O["c"]["large"] and not O["a"]["large"] and all(O[b]["special"] for b in ("d", "p", "e5")) \
        and not any(O[b]["special"] for b in ("a", "b", "c", "e"))
    pr["the pack path needs 23.91 mm on one 1 oz face and 11.95 mm on one 2 oz face"] = \
        abs(tc.width_for_current(PACK_A, 1.0) - 23.91) < 0.005 and abs(tc.width_for_current(PACK_A, 2.0) - 11.95) < 0.005
    pr["an inner 0.5 oz layer cannot be the pack path on any board (over 150 mm)"] = tc.width_for_current(PACK_A, oz=INNER_HALF_OZ, internal=True) > 150.0
    pr["board E's listed conductors side by side at 1 oz on one face exceed the strip"] = cs["1 oz"][0] > O["e"]["h"]
    pr["board E's listed conductors at 1 oz shared by two faces take under half the strip"] = cs["1 oz"][1] < O["e"]["h"] / 2.0
    pr["the pack return on board E's In1 alone needs more than the strip at 0.5 oz and at 1 oz"] = \
        R["return_inner"]["e"]["half_oz"] > O["e"]["h"] and R["return_inner"]["e"]["one_oz"] > O["e"]["h"]
    pr["neither A's nor E's intent declares a return of the pack path"] = not R["return_declared"]["a"] and not R["return_declared"]["e"]
    pr["board P's 0.5 oz inner planes hold their parallel share at the board's own width"] = P["at_board"][2] <= P["at_board"][3]
    pr["board P's 0.5 oz inner planes hold at every width over 16 mm beside the return (the model's failing band ends below it)"] = \
        P["wmin"]["0.5 oz"] is not None and P["wmin"]["0.5 oz"][1] < 16.0
    pr["at 1 oz inner the model's failing band ends below 7 mm"] = P["wmin"]["1 oz"] is not None and P["wmin"]["1 oz"][1] < 7.0
    pr["the fabricator's two pages disagree on the 2 oz track floor and the stricter is 0.16 mm"] = \
        F["caps_2oz_track"] != F["guide_2oz_track"] and max(F["caps_2oz_track"], F["guide_2oz_track"]) == 0.16
    pr["the 0.4 mm pitch parts on A, E and P leave a copper gap no wider than the 2 oz solder-mask bridge"] = \
        all(F["pitch"][b][3] <= F["bridge_2oz"] + 1e-9 for b in ("a", "e", "p"))
    pr["on eight layers one width per class meets its target within 2 ohm on outer and inner layers"] = \
        all(abs(z - t) <= 2.0 for _, t, sec, w, s, z in imp["b"] if s)
    pr["the 90 ohm class on eight layers also meets the M.2 module's 85 ohm within 10 percent"] = \
        all(85 * 0.9 <= z <= 85 * 1.1 for _, t, sec, w, s, z in imp["b"] if s and t == 90)
    pr["on six layers as built In2 cannot reach 85 ohm at a 0.127 mm gap and needs 0.208 mm for 90"] = \
        six["in2_85"] is None and six["in2_90"] is not None and six["in2_90"] > 0.2
    pr["every price reading carries a URL, a read time and an excerpt"] = all(r.get("url") and r.get("read_local") and r.get("excerpts") for r in PR["readings"])
    outl = {tuple(sorted((O[b]["w"], O[b]["h"]))) for b in BOARDS}
    pr["no price reading prints a figure at any board's outline"] = not any(
        f.get("size_mm") and tuple(sorted(float(x) for x in f["size_mm"])) in outl for i, v, f in fig)
    R["pred"] = pr
    return R


def f2(x):
    return "%.2f" % x


def render(R):
    L = []
    w = L.append
    w("# l9stk_stackups.out: Layer 9 item 9.12, the numbers behind one stackup decision per board (record l9stk)")
    w("# desk arithmetic on committed files and dated public readings; nothing built, routed, bought or quoted")
    w("")
    w("0. PINS (path  sha256/16)")
    for k in sorted(R["pins"]):
        p, h = R["pins"][k]
        w("   %s  sha256 %s  (%s)" % (p, h, k))
    w("")
    w("1. OUTLINES (the Edge.Cuts bounding box of each committed board file), AREA, AND THE FABRICATOR'S PRINTED SIZE CLASSES")
    w("   quantity per order: %d (the owner's rule); special price class: within 102 x 102 mm (JLC-5); large board fee: one board over 650 cm2 (JLC-5)" % QTY)
    w("   board               outline mm       copper layers in the file  area cm2  order m2  in 102x102 class  over 650 cm2  stack decided or ruled")
    for b in BOARDS:
        o = R["outline"][b]
        w("   %-18s  %7.2f x %6.2f  %d%s  %8.2f  %8.4f  %-16s  %-12s  %s (%d layers; %s)" % (
            NAMES[b], o["w"], o["h"], o["ncu"], " " * 25, o["area_cm2"], o["order_m2"], "yes" if o["special"] else "no",
            "yes" if o["large"] else "no", STACK[b][0], STACK[b][1], STACK[b][2]))
    w("")
    w("2. COPPER (decision 35's model, track_current.width_for_current at 10 K; the pack path at PWR-F12's %.0f A, the rest at their typical current)" % PACK_A)
    w("   barrels: via_current.barrels_for at the larger of the governing and the peak current, %.1f mm drill, 18 um plating (the same at either copper weight)" % DRILL)
    for b in ("a", "e", "p", "e5"):
        w("   board %s (%s):" % (b.upper(), NAMES[b]))
        w("     rail          typ A   peak A  governing A  pack path  1 oz one face  1 oz each of two  2 oz one face  2 oz each of two  barrels 0.4 mm")
        for k, typ, peak, g, pp, wd, br in R["copper"][b]:
            w("     %-12s  %6.2f  %6.2f  %11.2f  %-9s  %13s  %16s  %13s  %16s  %d" % (
                k, typ, peak, g, "yes" if pp else "no", f2(wd["1 oz"][0]), f2(wd["1 oz"][1]), f2(wd["2 oz"][0]), f2(wd["2 oz"][1]), br))
    if True:
        x = R["e_cross"]
        w("   BOUND, board E's cross-section demand (INFERRED: every listed conductor side by side across one section of the strip,")
        w("   which the floor plan may avoid; the pack path's return counted at the pack path's own %.0f A although E's intent declares no return):" % PACK_A)
        w("     conductors: %s and the pack return; strip %.2f mm wide" % (", ".join(x["rails"]), x["strip_mm"]))
        for lab in OZ:
            one, two = x["sum"][lab]
            w("     %s: %s mm of band on one face; %s mm on each face when two faces share (%.0f percent of the strip)" % (lab, f2(one), f2(two), 100.0 * two / x["strip_mm"]))
    ri = R["return_inner"]
    w("   BOUND, the pack path's return on the inner GND planes ALONE (width each plane needs, internal fits, 10 K):")
    w("     board A, In1 and In4 sharing %.0f A: %s mm each at 0.5 oz, %s mm each at 1 oz; the board's short side %.2f mm" % (PACK_A, f2(ri["a"]["half_oz"]), f2(ri["a"]["one_oz"]), ri["a"]["short_side"]))
    w("     board E, In1 alone at %.0f A: %s mm at 0.5 oz, %s mm at 1 oz; the strip %.2f mm" % (PACK_A, f2(ri["e"]["half_oz"]), f2(ri["e"]["one_oz"]), ri["e"]["short_side"]))
    w("     returns declared in the intents: board A %s; board E %s" % (R["return_declared"]["a"] or "none", R["return_declared"]["e"] or "none"))
    P = R["p_planes"]
    w("   BOUND, board P's pack return between R10 and the cell block: the share In1 and In2 (GND) take beside the outer 2 oz bands")
    w("   (plane_share: one-dimensional parallel conductors tied at both ends, by cross-section; no crowding at the via fields)")
    w("     outer bands: %s mm on each of two 2 oz faces, or %s mm on one" % (f2(P["w_two_faces"]), f2(P["w_one_face"])))
    w("     inner     plane mm  outer faces  outer mm  planes' share  per plane A  plane rating A (model)  holds")
    for lab, wp, faces, wo, s, per, r, m in P["rows"]:
        w("     %-8s  %8.1f  %11d  %8s  %13.2f  %11.2f  %15.2f (%s)  %s" % (lab, wp, faces, f2(wo), s, per, r, m, "yes" if per <= r else "NO"))
    for lab in ("0.5 oz", "1 oz"):
        band = P["wmin"][lab]
        w("     %s inner, outer bands at their two-face minimum: a plane is over its rating only when %s" % (
            lab, "necked to %.2f to %.2f mm beside the run (scanned 0.05 to 200 mm in 0.05 mm steps)" % band if band else "never, at any width scanned"))
    wp, s, per, r, m, br = P["at_board"]
    w("     at the board's own short side less 1 mm a side (%.1f mm), 0.5 oz: share %.2f, %.2f A per plane against %.2f A; the planes' share needs %d barrels of 0.4 mm at each end" % (wp, s, per, r, br))
    w("   board B, each 5 V domain on In4 at 0.5 oz (typical current, internal fits): " + "; ".join("%s %.2f A %s mm" % (k, a, f2(x)) for k, a, x in R["b_in4"]))
    for b in ("c", "d"):
        k, a, x = R["max_" + b]
        w("   board %s's largest rail: %s at %.2f A typical, %s mm on one 1 oz face" % (b.upper(), k, a, f2(x)))
    w("")
    F = R["floors"]
    w("3. FABRICATOR FLOORS AT 2 OZ AND THE 0.4 MM PITCH PARTS")
    w("   minimum track and space, multilayer: 1 oz %.2f mm (capability transcription of 16 September 2026); 2 oz %.2f mm (stackup transcription of 25 September 2026) against %.2f mm (JLC-6, the copper weight guide, last updated 9 September 2026, read 3 October 2026): the stricter is %.2f mm" % (
        F["track_1oz_multi"], F["caps_2oz_track"], F["guide_2oz_track"], max(F["caps_2oz_track"], F["guide_2oz_track"])))
    w("   solder-mask bridge at 2 oz: %.2f mm (stackup transcription of 25 September 2026)" % F["bridge_2oz"])
    for b in ("a", "e", "p"):
        ref, pitch, across, gap = F["pitch"][b]
        w("   board %s %s: pitch %.3f mm, pad %.3f mm across the pitch, copper gap %.3f mm: %s" % (
            b.upper(), ref, pitch, across, gap, "a bridge at 2 oz needs the whole gap (no mask expansion at all)" if abs(gap - F["bridge_2oz"]) < 1e-9 else
            ("under the 2 oz bridge" if gap < F["bridge_2oz"] else "over the 2 oz bridge")))
    w("")
    w("4. IMPEDANCE ON THE DECIDED STACKS (atlc 4.6.1 solves in stack_solves.out, masked outer layers, interpolated between solved widths)")
    for b in ("a", "b", "d"):
        w("   board %s on %s:" % (b.upper(), STACK[b][0]))
        for what, t, sec, wdt, s, z in R["imp"][b]:
            if s:
                w("     %-82s target %3d ohm: w %.3f mm at gap %.3f mm reads %.1f ohm (%s)" % (what, t, wdt, s, z, sec))
            else:
                w("     %-82s target %3d ohm: w %.3f mm single-ended (%s)" % (what, t, wdt, sec))
    w("   boards C, E, P and E5: no impedance target declared (pcb_interfaces.yaml: USB_FULL_SPEED on C and E, SMBUS_GAUGE on P, no interface on E5)")
    s6 = R["six_b"]
    w("   board B on six layers as built, for the comparison: outer 90 ohm at w %.3f and 100 ohm at w %.3f (gap 0.127); In2 90 ohm at w %s, 100 ohm at w %s, 85 ohm %s; option A2's In2 90 ohm at w %.3f" % (
        s6["out_90"], s6["out_100"], ("%.3f" % s6["in2_90"]) if s6["in2_90"] else "not reached", ("%.3f" % s6["in2_100"]) if s6["in2_100"] else "not reached",
        ("at w %.3f" % s6["in2_85"]) if s6["in2_85"] else "not reached in the solved widths", s6["a2_90"]))
    w("   board A's USB class 0.127 / 0.13 mm on 1 oz reads %.1f ohm; at the 2 oz floor 0.16 / 0.16 the 1 oz solve reads %.1f ohm (the 2 oz copper and JLCPCB's six-layer 2 oz row are NOT SOLVED)" % (R["usb_class_a"], R["usb_2oz_ref"]))
    w("")
    w("5. PRICES (inputs/price-readings-2026-10-03.json: public pages read 3 October 2026, excerpts only; no login, no quote form, no request)")
    w("   readings: %s" % ", ".join(R["price_ids"]))
    w("   figures as printed (USD):")
    for rid, v, f in R["figures"]:
        parts = []
        for key in ("layers", "size_mm", "qty", "usd", "usd_per_m2", "usd_per_design", "area_cm2", "mm", "fraction", "max_size_mm"):
            if key in f and f[key] is not None:
                parts.append("%s %s" % (key, f[key]))
        w("     %-6s %-8s %-46s %s" % (rid, v, f.get("kind", ""), "; ".join(parts)))
    w("   deltas at the printed conditions only (start prices; not a price at any board's outline):")
    for rid, lo, hi, a, b2, d in R["deltas"]:
        w("     %s: %d layers %.2f, %d layers %.2f, delta %.2f" % (rid, lo, a, hi, b2, d))
    w("   NOT READ:")
    for x in R["price_not_read"]:
        w("     - %s" % x)
    w("")
    w("6. PREDICATES")
    for k in sorted(R["pred"]):
        w("   [%s] %s" % ("TRUE" if R["pred"][k] else "FALSE", k))
    return "\n".join(L) + "\n"


def main():
    R = compute()
    if not all(R["pred"].values()):
        bad = [k for k, v in R["pred"].items() if not v]
        sys.stdout.write(render(R))
        refuse("predicate(s) false: %s" % "; ".join(bad))
    sys.stdout.write(render(R))
    return 0


if __name__ == "__main__":
    sys.exit(main())
