#!/usr/bin/env python3
"""PCB-P PACK BMS P1 (MESHSAT-830, appendix 32.62): bring the netlist onto the mechanical board of gen_pcb_p.py, fix the power path and the connectors, pack the
gauge and its filters, lay the locked 2 oz bands of the power path on both layers, pour the ground on the underside and set the net classes.
Usage: gen_pcb_p3.py <board.kicad_pcb> <netlist.net>. Board frame: origin at the board centre, +X along the pack.
The power path never travels in router tracks (the A21 rule of 32.39): B+ land > blade holder > charge FET > discharge FET > pack + land along the north edge
and B- land > shunt > pack - land along the south edge are 4 mm locked tracks on F.Cu and B.Cu with stitch vias; the router connects the small-signal
pads to them."""
import sys, re, math, os, pcbnew
from pcbnew import VECTOR2I, FromMM
BOARD, NET = sys.argv[1], sys.argv[2]
OX, OY = 100.0, 100.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
def parse(s):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    def rd(i):
        out = []
        while i < len(tok):
            t = tok[i]
            if t == "(": sub, i = rd(i + 1); out.append(sub)
            elif t == ")": return out, i + 1
            else: out.append(t); i += 1
        return out, i
    return rd(0)[0]
def uq(s): return s[1:-1] if s.startswith('"') else s
def kids(n, key): return [e for e in n if isinstance(e, list) and e and e[0] == key]
nl = parse(open(NET).read())[0]
comps = {}
for c in kids(kids(nl, "components")[0], "comp"):
    ref = uq(kids(c, "ref")[0][1]); val = uq(kids(c, "value")[0][1]); fp = uq(kids(c, "footprint")[0][1]) if kids(c, "footprint") else ""
    comps[ref] = (val, fp)
nets = {}
for n in kids(kids(nl, "nets")[0], "net"):
    name = uq(kids(n, "name")[0][1]); nets[name] = [(uq(kids(nd, "ref")[0][1]), uq(kids(nd, "pin")[0][1])) for nd in kids(n, "node")]
print("netlist: %d components, %d nets" % (len(comps), len(nets)))
board = pcbnew.LoadBoard(BOARD)
existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
LIBS = "/usr/share/kicad/footprints/"; MSLIB = os.path.join(os.path.dirname(os.path.abspath(BOARD)), "..", "meshsat.pretty")
def load(fpid):
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(MSLIB if lib == "meshsat" else LIBS + lib + ".pretty", name)
    if fp is None: raise SystemExit("footprint missing: " + fpid)
    return fp
def centre_on(fp, x, y):
    bb = fp.GetBoundingBox(False, False); cx, cy = (bb.GetLeft() + bb.GetRight()) // 2, (bb.GetTop() + bb.GetBottom()) // 2
    t = P(x, y); fp.Move(VECTOR2I(t.x - cx, t.y - cy))
def text(txt, x, y, layer, size=2.5, thick=0.4, angle=0.0, halign="center", mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick)); t.SetTextAngleDegrees(angle)
    t.SetHorizJustify({"center": pcbnew.GR_TEXT_H_ALIGN_CENTER, "left": pcbnew.GR_TEXT_H_ALIGN_LEFT, "right": pcbnew.GR_TEXT_H_ALIGN_RIGHT}[halign])
    if mirror: t.SetMirrored(True)
    board.Add(t); return t
def place(ref, x, y, rot=0.0, back=False, centre=True):
    val, fpid = comps[ref]; fp = load(fpid); fp.SetReference(ref); fp.SetValue(val)
    fp.Reference().SetVisible(ref[0] in "UJ" and not ref.startswith("JP")); fp.Value().SetVisible(False)
    fp.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); fp.Reference().SetTextThickness(FromMM(0.12))
    fp.SetPosition(P(x, y)); board.Add(fp)
    if back: fp.Flip(P(x, y), False)
    fp.SetOrientationDegrees(rot)
    if centre: centre_on(fp, x, y)
    return fp
placed = {}
for ref in comps:                                                   # the holes are already on the board from gen_pcb_e.py
    if ref in existing: existing[ref].SetValue(comps[ref][0]); placed[ref] = existing[ref]
# ---------------------------------------------------------------- fixed parts (board mm, rot, back): the power path along the north edge, the shunt along the south edge, the leads at the edges
FIXED = {"W_BP": (-27, 12.5, 0, False), "F1": (-15.6, 15, 0, False), "Q1": (0, 15, 0, False), "Q2": (8, 15, 180, False), "W_P": (26, 12.5, 0, False),
         "W_BN": (-27, -12.5, 0, False), "R10": (-18, -15, 0, False), "W_N": (-8, -13.5, 0, False),
         "J_CELL": (12, -17.5, 0, False), "J_TS": (30.5, -9, 90, False), "J_SMB": (30.5, 2, 90, False)}
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
for ref, x, y in (("B+", -27, 16.2), ("F1 25A", -15.6, 19.6), ("CHG", 0, 18.6), ("DSG", 8, 18.6), ("PACK+", 26, 16.2), ("B-", -27, -16.2), ("2m", -18, -18.4), ("PACK-", -8, -17.2), ("TAPS", 12, -21.2), ("NTC", 30.5, -15), ("SMB", 30.5, 10.5)):
    text(ref, x, y, pcbnew.F_SilkS, 0.8, 0.14)
# ---------------------------------------------------------------- packed regions (name, rect, refs, back): the gauge and its filters in the middle, the gate networks and ESD east, the test points west
REGIONS = [
 ("GAUGE", (-23, -10, 4, 12), ["U1", "C1"] + ["C%d" % k for k in range(2, 11)] + ["R%d" % k for k in range(1, 10)], False),
 ("SIG",   (4, -10, 22, 12), ["R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "C11", "C12", "D1", "D2"], False),
 ("TPS",   (-33, -12, -25, 8.5), ["TP%d" % k for k in range(1, 11)], False),   # ten test points along the west edge (the cell tap nets are on J_CELL already)
]
rest = [r for r in comps if r not in placed and not r.startswith("H") and not any(r in refs for _, _, refs, _ in REGIONS)]
if rest: REGIONS.append(("REST", (22, -10, 24, 8), rest, False))
GAP = 1.2; FINE_MARGIN = 2.2
def is_fine(fp):
    if re.search(r"SOT-23-[68]", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]; best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
_all = [r for _, _, refs, _ in REGIONS for r in refs] + list(FIXED)
_dups = sorted({r for r in _all if _all.count(r) > 1})
if _dups: raise SystemExit("reference listed twice in the placement (two footprints per reference make the DSN export refuse the board): %s" % _dups)
# 9 September 2026 (owner ruling, appendix 32.74 option 3): every declared decoupling capacitor takes its slot beside the pin it serves
# BEFORE the packer fills the regions. The old order shelf-packed them by reference number and moved afterwards only what still fitted;
# measured across the released set, not one capacitor of any board was inside the 3 mm rule and A22's worst two sat 117 and 121 mm away.
import json as _json, bypass_slots
_ip = os.path.join(os.path.dirname(os.path.abspath(BOARD)), "out", os.path.splitext(os.path.basename(BOARD))[0] + "-intent.json")
_entries = _json.load(open(_ip)).get("bypass", []) if os.path.exists(_ip) else []
RESERVED = bypass_slots.reserve(board, place, lambda v: (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y)), _entries)
for _r in RESERVED: placed[_r] = board.FindFootprintByReference(_r)
REGIONS = [(_n, _rect, [_r for _r in _refs if _r not in RESERVED], _bk) for _n, _rect, _refs, _bk in REGIONS]   # a reserved capacitor is placed already
for name, (x0, y0, x1, y1), refs, back in REGIONS:
    fps = []
    for ref in refs:
        fp = place(ref, 0, 0, back=back); bb = fp.GetBoundingBox(False, False); fine = is_fine(fp); mx = my = 0.0
        if fine:
            nfine = sum(1 for pd in fp.Pads() if pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and min(pd.GetSize().x, pd.GetSize().y) <= FromMM(1.2))
            fm = FINE_MARGIN if nfine >= 16 else 1.4   # the wide margin is for the QFN and QFP rows whose escape vias splay far (U5, U10); a SOT or USON keeps 1.4
            for pd in fp.Pads():
                if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or min(pd.GetSize().x, pd.GetSize().y) > FromMM(1.2): continue
                pbb = pd.GetBoundingBox(); w_, h_ = pbb.GetWidth(), pbb.GetHeight()
                if w_ > h_ * 1.2: mx = 2 * fm
                elif h_ > w_ * 1.2: my = 2 * fm
            if mx == 0.0 and my == 0.0: mx = my = 2 * fm
        fps.append((ref, fp, bb.GetWidth() / 1e6 + GAP + mx, bb.GetHeight() / 1e6 + GAP + my, fine))
    fps.sort(key=lambda t: (not t[4], -(t[2] * t[3])))
    cx, cy, rowh = x0, y1, 0.0
    for ref, fp, w, h, fine in fps:
        if cx + w > x1 + 0.01: cx = x0; cy -= rowh; rowh = 0.0
        centre_on(fp, cx + w / 2, cy - h / 2); placed[ref] = fp; cx += w; rowh = max(rowh, h)
    if cy - rowh < y0 - 0.01: print("WARNING region %s overflows by %.1f mm" % (name, (y0 - (cy - rowh))))
missing = [r for r in comps if r not in placed and not r.startswith("#")]
if missing: raise SystemExit("unplaced: %s" % missing)
# ---------------------------------------------------------------- nets, pours, classes
def net_for(name, create=True):
    """The board's net for a schematic name: a local label lands in the board as "/NAME", a power symbol as "NAME".
    The netlist import creates nets (create=True); a zone must find its net (create=False), because a pour on a name that
    matches nothing would get a phantom net with no pads and dead copper (A19 and B12 rail planes, 4 Sep 2026, 32.33)."""
    for cand in (name, "/" + name):
        n = board.FindNet(cand)
        if n is not None and n.GetNetCode() > 0: return n
    if create:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); return n
    raise SystemExit("zone net %r is not in the netlist (neither %r nor %r): fix the name, do not pour on a phantom" % (name, name, "/" + name))
padmap = {}
for ref, fp in placed.items():
    for pad in fp.Pads(): padmap.setdefault(ref, {}).setdefault(pad.GetNumber(), []).append(pad)
unassigned = []
for name, nodes in nets.items():
    if name.startswith("unconnected-"): continue
    n = net_for(name)
    for ref, pin in nodes:
        pads = padmap.get(ref, {}).get(pin)
        if not pads: unassigned.append((ref, pin, name)); continue
        for pad in pads: pad.SetNet(n)
if unassigned: print("WARNING pads not found for nodes:", unassigned[:12])
# ---------------------------------------------------------------- the power path in locked 2 oz bands on both layers, stitched; the underside ground pour
def pad_at(ref, num):
    for pd in placed[ref].Pads():
        if pd.GetNumber() == num: return pd.GetPosition()
    raise SystemExit("pad %s.%s not found" % (ref, num))
def mm(v): return (v.x / 1e6 - OX, OY - v.y / 1e6)
def track(netname, a, b, w, L):
    t = pcbnew.PCB_TRACK(board); t.SetStart(P(*a)); t.SetEnd(P(*b)); t.SetWidth(FromMM(w)); t.SetLayer(L); t.SetNet(net_for(netname, create=False)); t.SetLocked(True); board.Add(t)
def band(netname, a, b, w=3.0, vias=3):
    """A locked band on both outer layers between two board-frame points, stitched by locked 0.8/0.4 vias; the ends stop 0.8 mm short of a pad centre when told."""
    for L in (pcbnew.F_Cu, pcbnew.B_Cu): track(netname, a, b, w, L)
    net = net_for(netname, create=False)
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, min(vias, int((L - 4.4) / 1.6) + 1)) if L >= 4.4 else 1
    for k in range(n):
        d = L / 2 if n == 1 else 2.2 + k * (L - 4.4) / (n - 1); f = d / L   # every via at least 2.2 mm from a band end (the wire lands' 2.4 mm holes, hole-to-hole 0.3)
        v = pcbnew.PCB_VIA(board); v.SetPosition(P(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
        v.SetWidth(FromMM(0.8)); v.SetDrill(FromMM(0.4)); v.SetNet(net); v.SetLocked(True); board.Add(v)
def short_of(a, b, d=0.8):
    """the point d mm before b on the way from a"""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); return (b[0] - (b[0] - a[0]) / L * d, b[1] - (b[1] - a[1]) / L * d)
# the PowerPAK SO-8 land: pins 1-3 (source) at x -2.67, y +1.91, +0.64, -0.64; pin 4 (gate) at y -1.91; the tab centred at x +0.69; Q2 is rotated 180
q1, q2 = FIXED["Q1"][:2], FIXED["Q2"][:2]
f1a, f1b, r10a, r10b = mm(pad_at("F1", "1")), mm(pad_at("F1", "2")), mm(pad_at("R10", "1")), mm(pad_at("R10", "2"))
wbp, wp, wbn, wn = mm(pad_at("W_BP", "1")), mm(pad_at("W_P", "1")), mm(pad_at("W_BN", "1")), mm(pad_at("W_N", "1"))
band("CELL4", short_of(f1a, wbp), short_of(wbp, f1a))                                                    # B+ land to the blade holder
q1_src = (q1[0] - 4.6, q1[1] + 0.64); band("FUSED", short_of(q1_src, f1b), q1_src, w=2.8)                   # the blade to the charge FET's source side
for dy in (1.91, 0.64, -0.64): track("FUSED", (q1[0] - 2.67, q1[1] + dy), (q1_src[0], q1[1] + dy), 0.6, pcbnew.F_Cu)
band("SW", (q1[0] + 0.69, q1[1]), (q2[0] - 0.69, q2[1]))                                  # tab to tab
q2_src = (q2[0] + 4.6, q2[1] - 0.64); band("PACK_P", q2_src, short_of(q2_src, wp), w=2.8)  # the discharge FET's source side to the pack + land
for dy in (-1.91, -0.64, 0.64): track("PACK_P", (q2[0] + 2.67, q2[1] + dy), (q2_src[0], q2[1] + dy), 0.6, pcbnew.F_Cu)
band("GND", short_of(r10a, wbn), short_of(wbn, r10a, 0.5)); band("PACK_N", short_of(wn, r10b, 0.5), short_of(r10b, wn))   # B- land, shunt, pack - land
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25)); z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.4))
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
pour(pcbnew.B_Cu, "GND", "GND pour B.Cu", (-35, -22, 35, 22))
# P2 (8 Sep 2026, MESHSAT-862; 32.66: the P1 pour was 874 of 3080 mm2 in 15 pieces, 4 loose, once the router had used the underside): a locked ground via grid
# on 5 mm, wherever 1.6 mm from every pad, band and hole, so each piece the router leaves is anchored to the top-side ground
_gnd = net_for("GND", create=False); _n = 0
_obst = [(pd.GetPosition(), 1.6) for f in board.GetFootprints() for pd in f.Pads()]
def _seg_d(p_, a_, b_):
    dx_, dy_ = b_.x - a_.x, b_.y - a_.y; l2 = dx_ * dx_ + dy_ * dy_
    t_ = 0 if l2 == 0 else max(0, min(1, ((p_.x - a_.x) * dx_ + (p_.y - a_.y) * dy_) / l2))
    return math.hypot(p_.x - (a_.x + t_ * dx_), p_.y - (a_.y + t_ * dy_))
_rules = [z for z in board.Zones() if z.GetIsRuleArea()]
for _gx in range(-32, 33, 5):
    for _gy in range(-19, 20, 5):
        _p = P(_gx, _gy)
        if not all(math.hypot(_p.x - o.x, _p.y - o.y) > FromMM(r) for o, r in _obst): continue
        if not all(_seg_d(_p, t.GetStart(), t.GetEnd()) > t.GetWidth() / 2 + FromMM(0.3 + 0.3 + 0.15) for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"): continue   # the PWR class clearance 0.3 plus the via
        if any(z.Outline().Contains(_p) for z in _rules): continue
        if board.GetBoardEdgesBoundingBox().Contains(_p):
            v = pcbnew.PCB_VIA(board); v.SetPosition(_p); v.SetDrill(FromMM(0.3)); v.SetWidth(FromMM(0.6)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(_gnd); v.SetLocked(True); board.Add(v); _n += 1
print("ground stitch grid: %d locked vias" % _n)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
cls(ns.GetDefaultNetclass(), 0.127, 0.25, 0.6, 0.3)
PATTERNS = [("CELL4", "PWR"), ("FUSED", "PWR"), ("SW", "PWR"), ("PACK_P", "PWR"), ("PACK_N", "PWR"), ("GND", "GNDC"), ("CELL1", "SENSE"), ("CELL2", "SENSE"), ("CELL3", "SENSE")]
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]
try:
    nc = pcbnew.NETCLASS("PWR"); cls(nc, 0.3, 0.5, 0.8, 0.4); ns.SetNetclass("PWR", nc)   # P2 (8 Sep 2026): the current runs in the locked 2 oz bands; the class width is for the sense, gate and test-point links the router lays (1.0 mm left three of them open)
    nsn = pcbnew.NETCLASS("SENSE"); cls(nsn, 0.127, 0.4, 0.6, 0.3); ns.SetNetclass("SENSE", nsn)
    ng = pcbnew.NETCLASS("GNDC"); cls(ng, 0.127, 0.5, 0.6, 0.3); ns.SetNetclass("GNDC", ng)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
except Exception as e: print("note: net class API:", e)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json, fnmatch as _fnm
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def C(name, prio, clr, tw, vd, vdr): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=0.2, diff_pair_gap=0.15)
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.127, 0.25, 0.6, 0.3), C("PWR", 0, 0.3, 0.5, 0.8, 0.4), C("SENSE", 1, 0.127, 0.4, 0.6, 0.3), C("GNDC", 2, 0.127, 0.5, 0.6, 0.3)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    def _class_of(netname):
        bare = netname.lstrip("/")
        for pat, cl in PATTERNS:
            if not pat.startswith("/") and _fnm.fnmatchcase(bare, pat): return cl
        return None
    _assign = {}
    for _name, _net in board.GetNetInfo().NetsByName().items():
        _cl = _class_of(str(_name))
        if _cl: _assign[str(_name)] = _cl
    d["net_settings"]["netclass_assignments"] = _assign
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None)
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied, %d assignments" % len(_assign))
