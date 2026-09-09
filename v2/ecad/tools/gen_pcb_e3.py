#!/usr/bin/env python3
"""PCB-E1 DOCK: bring the netlist into the mechanical strip, place the dock contacts and connectors, pack the power entry. Usage: gen_pcb_e3.py <board.kicad_pcb> <netlist.net>"""
import sys, re, math, os, pcbnew
from pcbnew import VECTOR2I, FromMM
BOARD, NET = sys.argv[1], sys.argv[2]
OX, OY = 150.0, 110.0
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
# ---------------------------------------------------------------- dock layout (case mm): the target block under PCB-A's J_DOCK, the DC entry at the port end, the buck in the middle
FIXED = {"J_BLK": (-80, -76.5, 0, False), "P_CP": (-104, -108, 0, False), "P_CN": (-94, -108, 0, False), "PAD_W1": (-84, -108, 0, False), "PAD_W2": (-74, -108, 0, False), "J_BATT": (-138, -108, 0, False), "F3": (-120, -108, 0, False),
         "J_DCIN": (-64, -108, 0, False), "F1": (-48, -108, 0, False), "J_SOLAR": (-22, -108, 0, False), "F2": (-6, -108, 0, False),
         "U5": (32.8, -91, 0, False), "L1": (46, -103, 0, False), "U10": (86, -94, 0, False),
         "J_SMB": (-144, -62, 0, False), "J_POD": (-138, -62, 0, False), "J_LTG": (-132, -62, 0, False), "J_GEIGER": (-126, -62, 0, False), "J_DCF": (-144, -49.3, 0, False), "J_FAN1": (-138, -49.3, 0, False), "J_FAN2": (-132, -49.3, 0, False)}
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
text("PACK", -138, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("F3 25A", -120, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("DC IN", -64, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("F1 10A", -48, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("PV", -22, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("F2 10A", -6, -112.2, pcbnew.F_SilkS, 1.2, 0.2)
# ---------------------------------------------------------------- SMD cluster on the underside (packer from gen_pcb_b3, loosened)
REGIONS = [
 ("MCUR",   (91, -106, 118, -80), ["U11", "Y1", "C36", "C37", "R28", "R29", "R30", "R31", "R32", "JP1"] + ["C%d" % k for k in range(38, 48)] + ["TP10", "TP11", "TP12", "R33", "LED2", "R34", "R35", "R36", "R37"], False),
 ("PACK",   (-146, -104, -118.5, -83.5), ["C1", "D3", "TP8", "TP9", "C31", "U12", "L3", "U13", "C30", "C32", "C33", "C34", "C35", "R48", "TP13", "R42", "R43"], False),
 ("FANS",   (-145, -83.4, -116, -71.5), ["Q9", "Q10", "R44", "R45", "R46", "R47", "D7", "D8", "R49", "R50"], False),
 ("HOTSW",  (-106, -104, -76, -86), ["U6", "R19", "Q7", "R20", "R21", "R22", "R23", "C5", "R24", "R25", "D2", "C8"], False),
 ("ENTRYA", (-76, -103, -44, -87), ["U3", "Q1", "C4", "R1", "D1", "C2", "TP1", "TP2", "Q8", "R26"], False),
 ("ENTRYB", (-44, -103, -26, -81), ["L2", "C6", "C7", "R27", "LED1", "TP3"], False),
 ("TRKIN",  (-26, -103, -2, -81), ["D4", "C11", "C12", "C13", "C14", "C15", "TP5"], False),
 ("TRKW",   (-2, -103, 28, -81), ["Q3", "Q4", "Q5", "Q6", "R5", "R6", "R7", "C16", "C17", "C18", "D5", "D6"], False),
 ("TRKS",   (39.5, -95.5, 56, -80), ["C19", "C20", "C21", "C22", "C23", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17"], False),
 ("TRKOUT", (56, -112, 78, -81), ["C24", "C25", "C26", "C27", "U4", "Q2", "C28", "R18", "TP6"], False),
 ("SENS",   (40, -78, 52, -46), ["U14", "C48", "U15", "R51", "C49", "C50", "R38", "R39", "C51", "R40", "R41"], False),
 ("TPS",    (78, -112, 118, -107), ["TP4", "TP7"], False),
]
rest = [r for r in comps if r not in placed and not r.startswith("H") and not any(r in refs for _, _, refs, _ in REGIONS)]
if rest: REGIONS.append(("REST", (78, -98, 118, -82), rest, False))
GAP = 1.2; FINE_MARGIN = 2.2   # E6 round 4: 1.4 left R14 inside the tracker's escape row and four pads of U5 without escapes
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
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.3))
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    except Exception: pass
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
# E6 (32.57): four layers, one ground domain. In1 is the solid GND plane (rule area: no tracks); In2 carries VIN_RAW from the filter to the block lands, the tracker's PV_P and TRK_OUT pours;
# E6 round 4 (7 Sep 2026): In2 is a power layer in the DSN (no wires; the CELL_F, VIN_RAW, PV_P and TRK_OUT pours are DSN planes the router reaches by vias) and carries no GND pour: overlapping zone outlines would both be planes in the DSN.
# the pack node CELL_F runs on both outer layers from the blade to the pads; GND pours on the outer layers elsewhere; nothing under the float clamps (rule areas of gen_pcb_e.py).
pour(pcbnew.In1_Cu, "GND", "GND plane In1", (-149, -113, 118, -45))
z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
z.SetLayer(pcbnew.In1_Cu); z.SetZoneName("In1 solid ground: no tracks"); o = z.Outline(); o.NewOutline()
for x, y in ((-150, -114), (119, -114), (119, -44), (-150, -44)): p_ = P(x, y); o.Append(p_.x, p_.y)
board.Add(z)
pour(pcbnew.In2_Cu, "VIN_RAW", "VIN_RAW pour In2 (filter to the block lands)", (-92, -100, -26, -80))
pour(pcbnew.In2_Cu, "PV_P", "PV_P pour In2 (panel input)", (-26, -113, -2, -80))
pour(pcbnew.In2_Cu, "TRK_OUT", "TRK_OUT pour In2 (tracker output)", (56, -113, 76, -80))
pour(pcbnew.In2_Cu, "CELL_F", "CELL_F plane In2 (the west end: the pack node to the pack parts, the fans and the monitor divider; a DSN plane on the power layer In2 since E6 round 4)", (-148, -112, -100, -46), priority=1)
pour(pcbnew.F_Cu, "CELL_F", "CELL_F pour F.Cu (blade to the pad)", (-128, -112, -100, -103.5), priority=1)
for L in (pcbnew.F_Cu, pcbnew.B_Cu):
    pour(L, "GND", "GND pour %s" % board.GetLayerName(L), (-149, -113, 118, -45), priority=0)
pour(pcbnew.B_Cu, "CELL_F", "CELL_F band B.Cu (the blade lands and the west end: the pack node to the fans and the monitor divider; E6 route 2 left them open)", (-148, -112, -100, -46), priority=1)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
cls(ns.GetDefaultNetclass(), 0.127, 0.25, 0.6, 0.3)   # 0.127: the 0.4 mm escape rows of the RP2040 (E6 round 4)
PATTERNS = [("DC_*", "PWR"), ("HS_S", "PWR"), ("GND", "PWR"), ("GND_V", "PWR"), ("VIN_RAW", "PWR"), ("PV_*", "PWR"), ("TRK_OUT", "PWR"), ("TRK_SW*", "PWR"), ("TRK_LSENSE", "PWR"), ("+5V_E6", "PWR"), ("E6_SW", "PWR"), ("CELL+", "BANK"), ("CELL_F", "BANK"), ("USB_E6_*", "USB")]
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]   # 5 Sep 2026 (gateway finding, MESHSAT-802): root-sheet labels are "/NAME" on the board and KiCad's pattern matcher does not strip the slash, so every label pattern is emitted in both forms; power symbols (GND, +3V3) have no slash
try:
    nc = pcbnew.NETCLASS("PWR"); cls(nc, 0.15, 0.8, 0.8, 0.4); ns.SetNetclass("PWR", nc)
    nb = pcbnew.NETCLASS("BANK"); cls(nb, 0.3, 3.0, 1.2, 0.6); ns.SetNetclass("BANK", nb)
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
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.127, 0.25, 0.6, 0.3), C("PWR", 0, 0.127, 0.8, 0.8, 0.4), C("BANK", 1, 0.3, 3.0, 1.2, 0.6), C("USB", 2, 0.127, 0.3, 0.6, 0.3)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    # 7 Sep 2026 (A22 round 1 on the box, KiCad 9.0.9): the router's DSN carried every "/NAME" net in kicad_default because the pattern matcher resolved neither
    # "NAME" nor "/NAME" for root-sheet labels; explicit per-net assignments in the project are honoured, so every net gets one from the first matching pattern
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
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None); d["net_settings"].setdefault("netclass_assignments", {})
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied")
