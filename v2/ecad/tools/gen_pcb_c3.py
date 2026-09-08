#!/usr/bin/env python3
"""PCB-C (C8, 8 Sep 2026, MESHSAT-862: the 1.0 mm RAIL class and the pair pre-router in the chain) phase C7 (MESHSAT-830, 7 Sep 2026): bring the panel netlist into the ring of gen_pcb_c.py, place the panel items at the face sites of tools/panel1450.py,
the LEDs under the plate's light guides, the ribbon under B16's header, the e-paper ZIF and its boost on the top strip's top side, the light sensor under its guide,
the camera mount, then pack the RP2040 controller and the drivers on the underside of the right strip, the test points on the bottom strip, and pour the planes.
Usage: gen_pcb_c3.py <board.kicad_pcb> <netlist.net>. Case-centred frame (origin = case centre, +Y the back wall) as the plate and the scene."""
import sys, re, math, os, pcbnew
from pcbnew import VECTOR2I, FromMM
BOARD, NET = sys.argv[1], sys.argv[2]
OX, OY = 297.0, 210.0
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
for ref in comps:                                                   # H1..H8 already on the board from gen_pcb_c.py
    if ref in existing: existing[ref].SetValue(comps[ref][0]); placed[ref] = existing[ref]
# ---------------------------------------------------------------- panel layout (case mm): the sites of tools/panel1450.py, shared with the face plate
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel1450 as L
FIXED = {}
for ref, (x, y), hole, depth in L.BUTTONS: FIXED[ref] = (x, y, 45, False)           # the four lead lands at 45 degrees clear the neighbours
for ref, (x, y) in L.TOGGLES: FIXED[ref] = (x, y, 0, False)
FIXED[L.LIGHT[0]] = (L.LIGHT[1][0], L.LIGHT[1][1], 0, False)
FIXED[L.SOUNDER[0]] = (L.SOUNDER[1][0], L.SOUNDER[1][1], 90, False)      # lands to the sides (east and west)
for ref, (x, y) in L.HEADSETS: FIXED[ref] = (x, y, 0, False)
FIXED["J_PANEL"] = (L.J_PANEL_POS[0], L.J_PANEL_POS[1], 90, True)      # 2x13 SMD on the underside, along X, straight above B16's J_PANEL
FIXED["J_EPD"] = (L.J_EPD_POS[0], L.J_EPD_POS[1], 0, False)            # the ZIF on the top side (the flex comes down from the glass), its contacts toward the window
FIXED[L.LIGHT_SENSOR[0]] = (L.LIGHT_SENSOR[1][0], L.LIGHT_SENSOR[1][1], 0, False)
FIXED["CAM_H1"] = (L.CAMERA[1][0] - 10.0, L.CAMERA[1][1], 0, False); FIXED["CAM_H2"] = (L.CAMERA[1][0] + 10.0, L.CAMERA[1][1], 0, False)
for ref, (x, y) in L.LEAD_LANDS: FIXED[ref] = (x, y, 0, True)
# panel-mount parts sit at the plate's sites (their bodies pass this board through the footprints' holes and slots): placed by their hole centre, not by their bounding box
PANEL_MOUNT = {"SW_MAIN", "SW_PI", "SW_TEST", "SW_LIGHT", "SW_SOS", "SW_EMCON", "SW_ZERO", "BZ1", "J_HSJ1", "J_HSJ2", "CAM_H1", "CAM_H2"}
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back, centre=ref not in PANEL_MOUNT)
for ref, (x, y), label in L.STATUS_LEDS + L.BAR_LEDS: placed[ref] = place(ref, x, y, 0)   # THT LEDs on the top face, under the plate's light guides; the legends are laser marked on the plate
text("C7 BACKER RING: LEDs under the plate light guides, no face legends here", 0, L.STRIP_B[1] + 12.0, pcbnew.F_SilkS, 1.6, 0.25)
# ---------------------------------------------------------------- packed regions: the controller and drivers on the underside of the right strip, the e-paper boost on the top strip's top side, the spread parts on the bottom strip
EPD_PARTS = ["Q5", "Q6", "L1", "D19", "D20", "D21", "R42", "R43"] + ["C%d" % k for k in range(28, 38)]
SPREAD = lambda r: r.startswith(("TP", "JP", "FB")) or r == "D17"
REGIONS = [("CLUSTER3", L.CLUSTER3, [r for r in EPD_PARTS if r in comps], False),
           ("CLUSTER2", L.CLUSTER2, [r for r in comps if r not in placed and not r.startswith("H") and SPREAD(r)], True),
           ("CLUSTER", L.CLUSTER, [r for r in comps if r not in placed and not r.startswith("H") and not SPREAD(r) and r not in EPD_PARTS], True)]
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
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.3))
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    except Exception: pass
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
# ---------------------------------------------------------------- planes: In1 solid GND (the rule areas of gen_pcb_c.py keep the router off it), GND pours on In2 and both outer layers
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.3))
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    except Exception: pass
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
RING = (L.STRIP_L[0], L.STRIP_B[1], L.STRIP_R[2], L.STRIP_L[3])
for Lr in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu): pour(Lr, "GND", "GND pour %s" % board.GetLayerName(Lr), RING)
pour(pcbnew.In1_Cu, "GND", "GND plane In1", RING)   # the solid In1 ground plane (ruling 5 Sep 2026); it stays in the DSN as a plane (plane_nets GND) so the router reaches it by vias
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
cls(ns.GetDefaultNetclass(), 0.127, 0.25, 0.6, 0.3)   # 0.127: the RP2040's 0.4 mm escape rows (C7)
PATTERNS = [("+5V", "RAIL"), ("+3V3", "RAIL"), ("LED_RAIL*", "PWR"), ("GND", "PWR"), ("EPD_VCC", "PWR"), ("USB_*", "USB")]   # C8: the two rails 0.5 mm (8 Sep 2026 15:09: 1.0 mm strangled the router, and the intent's per-load currents show 0.5 mm meets the 3 percent budget on every leg)
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]
try:
    nc = pcbnew.NETCLASS("PWR"); cls(nc, 0.127, 0.5, 0.8, 0.4); ns.SetNetclass("PWR", nc)
    nr = pcbnew.NETCLASS("RAIL"); cls(nr, 0.127, 0.5, 0.8, 0.4); ns.SetNetclass("RAIL", nr)
    nu = pcbnew.NETCLASS("USB"); cls(nu, 0.127, 0.3, 0.6, 0.3); nu.SetDiffPairWidth(FromMM(0.3)); nu.SetDiffPairGap(FromMM(0.2))   # 8 Sep 2026 (32.71): 0.30/0.20 on the 7628 outer layer computes 89 ohm; the USB pairs stay on F.Cu over the In1 ground; ns.SetNetclass("USB", nu)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
except Exception as e: print("note: net class API:", e)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def C(name, prio, clr, tw, vd, vdr): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=0.3, diff_pair_gap=0.2)
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.127, 0.25, 0.6, 0.3), C("PWR", 0, 0.127, 0.5, 0.8, 0.4), C("USB", 1, 0.127, 0.3, 0.6, 0.3), C("RAIL", 2, 0.127, 0.5, 0.8, 0.4)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    import fnmatch as _fnm
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
    print("net-class assignments written for %d nets" % len(_assign))
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None)
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied")
