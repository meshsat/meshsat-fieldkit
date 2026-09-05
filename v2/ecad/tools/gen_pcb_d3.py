#!/usr/bin/env python3
"""PCB-D phase D3: bring the schematic netlist into the D1 mechanical board.
Usage: gen_pcb_d3.py <board.kicad_pcb> <netlist.net>
- reuses footprints already on the board by reference (J_GPIO1, J_RTL1, J_ZB1, J_DCF77)
- places connectors at planned case-frame positions, small parts packed into regions near their connectors
- creates nets, assigns pads, adds GND (In1) and +5V (In2) planes, saves
"""
import sys, re, math, pcbnew
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
    name = uq(kids(n, "name")[0][1])
    nets[name] = [(uq(kids(nd, "ref")[0][1]), uq(kids(nd, "pin")[0][1])) for nd in kids(n, "node")]
print("netlist: %d components, %d nets" % (len(comps), len(nets)))

board = pcbnew.LoadBoard(BOARD)
existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
LIBS = "/usr/share/kicad/footprints/"
import os
MSLIB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(BOARD)), "..", "meshsat.pretty"))
def load(fpid):
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(MSLIB if lib == "meshsat" else LIBS + lib + ".pretty", name)
    if fp is None: raise SystemExit("footprint missing: " + fpid)
    return fp
def centre_on(fp, x, y):
    bb = fp.GetBoundingBox(False, False)
    cx, cy = (bb.GetLeft() + bb.GetRight()) // 2, (bb.GetTop() + bb.GetBottom()) // 2
    t = P(x, y); fp.Move(VECTOR2I(t.x - cx, t.y - cy))
def place(ref, x, y, rot=0.0, back=False):
    val, fpid = comps[ref]
    fp = load(fpid); fp.SetReference(ref); fp.SetValue(val)
    fp.Reference().SetVisible(ref[0] in "UJ" and not ref.startswith("JP")); fp.Value().SetVisible(False)   # only ICs and connectors carry a visible reference
    fp.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); fp.Reference().SetTextThickness(FromMM(0.12))
    fp.SetPosition(P(x, y)); board.Add(fp)
    if back: fp.Flip(P(x, y), False)
    fp.SetOrientationDegrees(rot); centre_on(fp, x, y)
    if ref in FIXED:
        bb = fp.GetBoundingBox(False, False)
        print("  %-10s centred at (%.1f, %.1f) size %.1f x %.1f %s" % (ref, (bb.GetLeft() + bb.GetRight()) / 2e6 - OX, OY - (bb.GetTop() + bb.GetBottom()) / 2e6, bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, "BACK" if fp.IsFlipped() else ""))
    return fp
# --- fixed positions (case frame)
FIXED = {}   # D7: no bench header (the module's own USB-C is the bench configuration path)
BACK = set()
placed = {}
for ref, (x, y, rot) in FIXED.items():
    if ref not in comps: print("WARNING not in netlist:", ref); continue
    placed[ref] = place(ref, x, y, rot, back=ref in BACK)
# --- reuse existing footprints
for ref in comps:
    if ref in placed: continue
    if ref in existing:
        fp = existing[ref]; val, fpid = comps[ref]
        if fp.GetFPIDAsString().split(":")[-1] != fpid.split(":")[-1]: print("NOTE %s footprint differs: board %s vs schematic %s" % (ref, fp.GetFPIDAsString(), fpid))
        fp.SetValue(val); placed[ref] = fp
# --- regions for the rest: (x0, y0, x1, y1), refs
REGIONS = [
 ("N_TOP_W", (-17, 18.6, -7, 30.4), ["X1", "C38", "C7", "C8"], False),
 ("N_TOP_E", (7, 18.6, 30, 30.4), ["FB1", "C9", "C10", "U7", "C39", "R3", "D1", "R15", "R42", "R43", "R44", "R45", "R46", "R48"], False),
 # the MCU core sits on the TOP side under the module since D4 (module 11 mm up on sockets and standoffs; its back-side parts hang 5 mm, so 6 mm remain):
 # the free field between the two socket rows (Y -18.6 .. 14.6) and clear of the two M2.5 standoff holes at (-15.8, -18.6) and (36.8, 14.4)
 ("CORE_W", (-13.5, -17.5, 5.0, 13.5), ["C17", "C18", "R10", "R11", "Q1", "Q2", "R12", "R13", "Q3", "Q4", "R37", "R38", "R39", "R40", "R41", "C32", "R8", "R9", "U8", "C40", "R47"], False),
 ("CORE_C", (5.5, -17.5, 19.0, 13.5), ["U5", "C33", "C34", "C35", "C36", "C37"], False),
 ("CORE_E", (19.5, -17.5, 34.0, 13.5), ["R2", "R4", "C13", "C14"], False),
 ("BOOST_W", (-27, -30.4, -18, 30.4), ["L1", "U1", "C23", "C24", "C26", "C27", "C28", "C29", "C20", "C21", "C22", "C25", "C30", "R30", "R31", "R32", "R33", "R34", "R35"], False),
 ("BENCH_BOT", (-30, -30.4, 19, -22.6), ["R36", "R49", "R50", "R51", "R52", "TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7", "TP8", "TP9", "TP10", "TP11", "TP12", "TP13", "TP14", "TP15"], True),
]
GAP = 1.2                      # between any two packed parts (0.7 left fine-pitch ICs wall to wall with passives)
FINE_MARGIN = 1.4              # extra on the pin sides of a fine-pitch IC so its escapes (escape.py) keep a via lane
import re as _re, math
def is_fine(fp):
    if _re.search(r"SOT-23-[68]", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
for name, (x0, y0, x1, y1), refs, back in REGIONS:
    fps = []
    for ref in refs:
        if ref not in comps: print("WARNING %s not in netlist" % ref); continue
        fp = place(ref, 0, 0, back=back); bb = fp.GetBoundingBox(False, False); fine = is_fine(fp); mx = my = 0.0
        if fine:                                                   # margin only on the sides that carry pins (a pin pad is elongated along its escape axis)
            for pd in fp.Pads():
                if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or min(pd.GetSize().x, pd.GetSize().y) > FromMM(1.2): continue
                pbb = pd.GetBoundingBox(); w_, h_ = pbb.GetWidth(), pbb.GetHeight()
                if w_ > h_ * 1.2: mx = 2 * FINE_MARGIN
                elif h_ > w_ * 1.2: my = 2 * FINE_MARGIN
            if mx == 0.0 and my == 0.0: mx = my = 2 * FINE_MARGIN
        fps.append((ref, fp, bb.GetWidth() / 1e6 + GAP + mx, bb.GetHeight() / 1e6 + GAP + my, fine))
    fps.sort(key=lambda t: (not t[4], -(t[2] * t[3])))   # fine-pitch ICs first, then by size
    cx, cy, rowh = x0, y1, 0.0
    for ref, fp, w, h, fine in fps:
        if cx + w > x1 + 0.01:
            cx = x0; cy -= rowh; rowh = 0.0
        centre_on(fp, cx + w / 2, cy - h / 2); placed[ref] = fp
        cx += w; rowh = max(rowh, h)
    if cy - rowh < y0 - 0.01: print("WARNING region %s overflows by %.1f mm" % (name, (y0 - (cy - rowh))))
missing = [r for r in comps if r not in placed and not r.startswith("#")]
if missing: raise SystemExit("unplaced: %s" % missing)
# --- nets
ni = board.GetNetInfo()
def net_for(name):
    n = board.FindNet(name)
    if n is None or n.GetNetCode() <= 0 and name != "":
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n)
    return n
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
for pad in placed["U1"].Pads():
    if pad.GetNetCode() <= 0: pad.SetNet(net_for("GND")); print("  U1 pad %s (EP) -> GND" % pad.GetNumber())
# module pins are through-hole sockets since D4 (the module sits 11 mm above the board on standoffs): the GND pins reach the planes directly, no vias needed
# --- planes: In1 GND, In2 +5V
def plane(layer, netname, name, rect=(-40, -31, 40, 31), priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.3))
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    except Exception: pass
    o = z.Outline(); o.NewOutline()
    x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority)
    board.Add(z); return z
plane(pcbnew.In1_Cu, "GND", "GND plane In1"); plane(pcbnew.In2_Cu, "+3V3", "+3V3 plane In2")
# --- net classes (API first; the project JSON is re-applied after the save because SaveBoard rewrites it)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr, dpw, dpg):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr)); nc.SetDiffPairWidth(FromMM(dpw)); nc.SetDiffPairGap(FromMM(dpg)); nc.SetDiffPairViaGap(FromMM(0.25))
cls(ns.GetDefaultNetclass(), 0.14, 0.25, 0.7, 0.3, 0.2, 0.15)   # D6: 0.14 (Freerouting left one D5 clearance 2.6 um short of 0.15; at 0.127 it packed tracks inside the 0.25 hole clearance of the escape vias)
CLASSES = {"USB": (0.14, 0.2, 0.7, 0.3, 0.2, 0.15), "PWR": (0.14, 0.4, 0.8, 0.4, 0.4, 0.25), "CELL": (0.2, 1.2, 1.0, 0.5, 1.2, 0.3)}   # CELL: the 5 A boost loop
PATTERNS = [("USB_*", "USB"), ("VIN_CELL", "CELL"), ("SW", "CELL"), ("V8", "CELL"), ("+5V_USB", "PWR"), ("+3V3", "PWR"), ("+3.3VA", "PWR"), ("VIN_LDO", "PWR"), ("LDO_A", "PWR"), ("GND", "PWR")]
try:
    for name, vals in CLASSES.items():
        nc = pcbnew.NETCLASS(name); cls(nc, *vals); ns.SetNetclass(name, nc)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
    print("net classes set via API")
except Exception as e:
    print("note: net class API:", e)
# placeholder USB-C plug footprints have 0.12 mm pad gaps: local clearance so DRC reports the real issues (part is an open BOM item)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json, os
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def C(name, prio, clr, tw, vd, vdr, dpw, dpg): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=dpw, diff_pair_gap=dpg)
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.14, 0.25, 0.7, 0.3, 0.2, 0.15), C("USB", 0, 0.14, 0.2, 0.7, 0.3, 0.2, 0.15), C("PWR", 1, 0.14, 0.4, 0.8, 0.4, 0.4, 0.25), C("CELL", 2, 0.2, 1.2, 1.0, 0.5, 1.2, 0.3)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None); d["net_settings"].setdefault("netclass_assignments", None)
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied")
