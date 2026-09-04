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
for ref in comps:                                                   # H1..H16 and EPD1 already on the board from gen_pcb_c.py
    if ref in existing: existing[ref].SetValue(comps[ref][0]); placed[ref] = existing[ref]
# ---------------------------------------------------------------- dock layout (case mm): the target block under PCB-A's J_DOCK, the DC entry at the port end, the buck in the middle
FIXED = {"U1": (29, -70, 90, False), "J_BLK": (-135, -88, 0, False), "P_CP": (-133, -96, 0, False), "P_CN": (-121, -96, 0, False), "J_BATT": (-150, -103, 0, False),
         "J_DCIN": (-104, -106, 0, False), "F1": (-88, -106, 0, False), "J_SOLAR": (-64, -106, 0, False), "F2": (-46, -106, 0, False),
         "U5": (2, -92, 0, False), "L1": (16, -102, 0, False), "J_TS": (66, -104, 0, False), "J_KS": (78, -104, 0, False)}
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
text("DC IN", -105, -52.5, pcbnew.F_SilkS, 2.0, 0.3); text("F1 7.5A", -80, -52.5, pcbnew.F_SilkS, 2.0, 0.3); text("12V AUX", 111, -64.5, pcbnew.F_SilkS, 1.6, 0.25); text("SHORE", 60, -75, pcbnew.F_SilkS, 2.0, 0.3)
# ---------------------------------------------------------------- SMD cluster on the underside (packer from gen_pcb_b3, loosened)
REGIONS = [
 ("ENTRY",  (-112, -101, -68, -82), ["U3", "Q1", "C4", "R1", "D1", "C1", "C2", "C3", "D3", "R2", "LED1", "R3", "R4", "U2", "TP1", "TP2", "TP3", "TP4"], False),
 ("TRKIN",  (-60, -102, -30, -81), ["D4", "C11", "C12", "C13", "C14", "C15", "TP5"], False),
 ("TRKW",   (-30, -108, -4, -82), ["Q3", "Q4", "Q5", "Q6", "R5", "R6", "R7", "C16", "C17", "C18", "D5", "D6"], False),
 ("TRKS",   (7, -93, 30, -84), ["C19", "C20", "C21", "C22", "C23", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17"], False),
 ("TRKOUT", (32, -108, 60, -84), ["C24", "C25", "C26", "C27", "U4", "Q2", "C28", "R18", "TP6"], False),
 ("TPS",    (90, -108, 116, -100), ["TP7", "TP8", "TP9"], False),
]
rest = [r for r in comps if r not in placed and not r.startswith("H") and not any(r in refs for _, _, refs, _ in REGIONS)]
if rest: REGIONS.append(("REST", (90, -98, 124, -82), rest, False))
GAP = 1.2; FINE_MARGIN = 1.4
def is_fine(fp):
    if re.search(r"SOT-23-[68]", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]; best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
for name, (x0, y0, x1, y1), refs, back in REGIONS:
    fps = []
    for ref in refs:
        fp = place(ref, 0, 0, back=back); bb = fp.GetBoundingBox(False, False); fine = is_fine(fp); mx = my = 0.0
        if fine:
            for pd in fp.Pads():
                if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or min(pd.GetSize().x, pd.GetSize().y) > FromMM(1.2): continue
                pbb = pd.GetBoundingBox(); w_, h_ = pbb.GetWidth(), pbb.GetHeight()
                if w_ > h_ * 1.2: mx = 2 * FINE_MARGIN
                elif h_ > w_ * 1.2: my = 2 * FINE_MARGIN
            if mx == 0.0 and my == 0.0: mx = my = 2 * FINE_MARGIN
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
# E4 (appendix 32.25): four layers. In1 carries the two ground domains side by side: DC_N (the isolated shore and panel side) under the entry, the tracker and the
# converter, GND (the kit side) under the block lands and the east end. In2 carries the entry and tracker power pours. Outer layers: GND pours only on the kit side.
# The module nets CELL_P_MOD / CELL_N_MOD run as bars between J_BATT and the lands (fix_e4_node.py) and touch no ground (32.24 AZ). Nothing under the float clamps (rule areas).
pour(pcbnew.In1_Cu, "DC_N", "DC_N plane In1 (isolated side)", (-115, -111, 62, -51))
pour(pcbnew.In1_Cu, "GND", "GND plane In1 west (kit side, block lands)", (-160, -111, -116, -51))
pour(pcbnew.In1_Cu, "GND", "GND plane In1 east (kit side)", (63, -111, 118, -51))
pour(pcbnew.In2_Cu, "PV_P", "PV_P pour In2 (panel input)", (-60, -111, -8, -80))
pour(pcbnew.In2_Cu, "TRK_OUT", "TRK_OUT pour In2 (tracker output)", (30, -111, 60, -80))
pour(pcbnew.In2_Cu, "SHORE_12V", "SHORE_12V pour In2 (converter output to the block lands)", (-116, -100, 4, -82))
pour(pcbnew.F_Cu, "DC_N", "DC_N pour F (isolated side)", (-115, -111, 62, -80), priority=0); pour(pcbnew.B_Cu, "DC_N", "DC_N pour B (isolated side)", (-115, -111, 62, -51), priority=0)
pour(pcbnew.F_Cu, "GND", "GND pour F west", (-160, -111, -116, -51)); pour(pcbnew.B_Cu, "GND", "GND pour B west", (-160, -111, -116, -51))
pour(pcbnew.F_Cu, "GND", "GND pour F east", (63, -111, 118, -51)); pour(pcbnew.B_Cu, "GND", "GND pour B east", (63, -111, 118, -51))
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
cls(ns.GetDefaultNetclass(), 0.15, 0.25, 0.6, 0.3)
PATTERNS = [("DC_*", "PWR"), ("SHORE_12V", "PWR"), ("GND", "PWR"), ("PV_*", "PWR"), ("TRK_OUT", "PWR"), ("TRK_SW*", "PWR"), ("TRK_LSENSE", "PWR"), ("CELL_*_MOD", "BANK")]
try:
    nc = pcbnew.NETCLASS("PWR"); cls(nc, 0.15, 0.8, 0.8, 0.4); ns.SetNetclass("PWR", nc)
    nb = pcbnew.NETCLASS("BANK"); cls(nb, 0.3, 4.0, 1.2, 0.6); ns.SetNetclass("BANK", nb)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
except Exception as e: print("note: net class API:", e)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def C(name, prio, clr, tw, vd, vdr): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=0.2, diff_pair_gap=0.15)
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.15, 0.25, 0.6, 0.3), C("PWR", 0, 0.15, 0.8, 0.8, 0.4), C("BANK", 1, 0.3, 4.0, 1.2, 0.6)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None); d["net_settings"].setdefault("netclass_assignments", None)
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied")
