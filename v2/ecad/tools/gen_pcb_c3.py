#!/usr/bin/env python3
"""PCB-C phase C3: bring the panel netlist into the mechanical board, place the panel items at their MIL-STD-1472 positions,
pack the SMD cluster on the underside, add the GND pours. Usage: gen_pcb_c3.py <board.kicad_pcb> <netlist.net>"""
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
for ref in comps:                                                   # H1..H16 and EPD1 already on the board from gen_pcb_c.py
    if ref in existing: existing[ref].SetValue(comps[ref][0]); placed[ref] = existing[ref]
# ---------------------------------------------------------------- panel layout (case mm), MIL-STD-1472: >= 25 mm switch pitch, labels on the far (+Y) side, 3.5 mm for critical
FIXED = {"SW_MAIN": (-150, 100, 45, False), "SW_PI": (-110, 100, 45, False), "SW_TEST": (-70, 100, 45, False), "SW_LIGHT": (120, 100, 0, False),
         "SW_SOS": (170, 42, 0, False), "SW_EMCON": (170, 0, 0, False), "SW_ZERO": (170, -42, 0, False),
         "R32": (-99, 78, 0, True), "R33": (-59, 78, 0, True), "J_EPD": (95, 100, 90, False), "BZ1": (120, 72, 0, False), "J_PANEL": (208, 75, 90, True), "J_X1202SW": (-150, -110, 0, True), "J_PIJ2": (-125, -110, 0, True)}
LED_COL = -120.0
LEDS = [("D1", 45, "MSTR WARN"), ("D2", 36, "MSTR CAUT"), ("D3", 27, "TX"), ("D4", 18, "SOS ACTIVE"), ("D5", 9, "SAT"), ("D6", 0, "MESH"), ("D7", -9, "LTE"), ("D8", -18, "GPS"), ("D9", -27, "SHORE"), ("D10", -36, "CHARGE"), ("D11", -45, "MSG")]
BAR = [("D12", -82), ("D13", -76), ("D14", -70), ("D15", -64), ("D16", -58)]; BAR_Y = 123.0
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
for ref, y, label in LEDS: placed[ref] = place(ref, LED_COL, y, 0); text(label, LED_COL - 5.0, y, pcbnew.F_SilkS, 2.5, 0.4, halign="right")   # labels west of the LEDs: east runs into the display frame
for ref, x in BAR: placed[ref] = place(ref, x, BAR_Y, 0)
text("BATT %", -88.0, BAR_Y, pcbnew.F_SilkS, 2.0, 0.3, halign="right")
for (ref, x), pct in zip(BAR, ("20", "40", "60", "80", "100")): text(pct, x, BAR_Y + 4.5, pcbnew.F_SilkS, 1.5, 0.25)
for ref, label, size in (("SW_MAIN", "MAIN PWR", 3.5), ("SW_PI", "PI", 3.5), ("SW_TEST", "TEST / ACK", 3.0), ("SW_LIGHT", "LIGHTING", 3.0)):
    x, y = FIXED[ref][0], FIXED[ref][1]; text(label, x, y + 16.5, pcbnew.F_SilkS, size, 0.5)
text("DAY", 120, 92, pcbnew.F_SilkS, 2.0, 0.3); text("NIGHT", 133, 100, pcbnew.F_SilkS, 2.0, 0.3, halign="left"); text("BLACKOUT", 120, 84, pcbnew.F_SilkS, 2.0, 0.3)
for ref, label in (("SW_SOS", "SOS"), ("SW_EMCON", "EMCON"), ("SW_ZERO", "ZEROIZE")):
    x, y = FIXED[ref][0], FIXED[ref][1]; text(label, x, y + 13.0, pcbnew.F_SilkS, 3.5, 0.5); text("guard closed = safe", x, y - 13.0, pcbnew.F_SilkS, 1.5, 0.25)   # 42 mm pitch: 13 mm keeps the label off the neighbour
text("E-PAPER: STATUS / PROVISIONING QR (HOLD TEST 5 s)", 30, 130.0, pcbnew.F_SilkS, 2.0, 0.3)
# ---------------------------------------------------------------- SMD cluster on the underside (packer from gen_pcb_b3, loosened)
REGIONS = [("CLUSTER", (135, 55, 200, 138), [r for r in comps if r not in placed and not r.startswith("H")], True)]
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
def net_for(name):
    n = board.FindNet(name)
    if n is None or n.GetNetCode() <= 0 and name != "": n = pcbnew.NETINFO_ITEM(board, name); board.Add(n)
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
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.3))
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    except Exception: pass
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
pour(pcbnew.F_Cu, "GND", "GND pour F", (-221, -155.5, 221, 155.5)); pour(pcbnew.B_Cu, "GND", "GND pour B", (-221, -155.5, 221, 155.5))
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
cls(ns.GetDefaultNetclass(), 0.15, 0.25, 0.6, 0.3)
PATTERNS = [("+5V", "PWR"), ("LED_RAIL*", "PWR"), ("GND", "PWR")]
try:
    nc = pcbnew.NETCLASS("PWR"); cls(nc, 0.15, 0.5, 0.8, 0.4); ns.SetNetclass("PWR", nc)
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
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.15, 0.25, 0.6, 0.3), C("PWR", 0, 0.15, 0.5, 0.8, 0.4)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None); d["net_settings"].setdefault("netclass_assignments", None)
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied")
