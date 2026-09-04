#!/usr/bin/env python3
"""PCB-A phase A3: bring the schematic netlist into the B1 mechanical board.
Usage: gen_pcb_b3.py <board.kicad_pcb> <netlist.net>
- reuses footprints already on the board by reference (J_GPIO1, J_RTL1, J_ZB1, J_DCF77)
- places connectors at planned case-frame positions, small parts packed into regions near their connectors
- creates nets, assigns pads, adds GND (In1) and +5V (In2) planes, saves
"""
import sys, re, math, pcbnew
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
    name = uq(kids(n, "name")[0][1])
    nets[name] = [(uq(kids(nd, "ref")[0][1]), uq(kids(nd, "pin")[0][1])) for nd in kids(n, "node")]
print("netlist: %d components, %d nets" % (len(comps), len(nets)))

board = pcbnew.LoadBoard(BOARD)
existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
LIBS = "/usr/share/kicad/footprints/"
import os as _os
MSLIB = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(sys.argv[1])), "..", "meshsat.pretty"))
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
RF_X = [-100, -84, 8, 24, 40, 66, 96]
FIXED = {"J_AB1": (-72, -73, 90), "J_LEDS1": (-44, -74, 0), "J_MEZZ_PWR1": (-8, -18, 90),
         "J_DOCK": (-124, -70, 0), "J_PRE1": (-149, -70, 0),
         "F3": (-150, -46, 0), "F4": (-125, -46, 0), "F5": (-100, -46, 0), "F2": (-75, -46, 0),
         "U22": (-148, -20, 0), "L2": (-148, -6, 0), "U23": (-116, -20, 0), "L3": (-116, -6, 0), "U24": (-86, -20, 0), "L4": (-86, -6, 0),
         "U20": (-50, -58, 0), "L5": (-40, -58, 0), "U21": (-112, -60, 0), "R52": (-130, -60, 0),
         "J_5V_M1": (-150, 44, 0), "J_5V_M2": (-135, 44, 0), "J_5V_PI": (-120, 44, 0),
         "U25": (-150, 18, 0), "J_MAINSW": (-159, 10, 90), "U26": (-140, 28, 0), "J_HEAT": (-159, 28, 90), "U5": (-150, 4, 0), "L6": (-142, 4, 0),
         "J_WALL1": (-156, 62, 270), "U6": (-70, 52, 0), "Y1": (-60, 60, 0), "U31": (-45, 40, 0)}
for k in range(4): FIXED["J_CP%d" % (k + 1)] = (-145 + 4 * k, -73, 0); FIXED["J_CN%d" % (k + 1)] = (-145 + 4 * k, -67, 0)
for k, x in enumerate(RF_X, 1): FIXED["J_BM%d" % k] = (x, -66, 0); FIXED["J_RF%d" % k] = (x, -56, 0)
BACK = {"J_DOCK", "J_PRE1"} | {"J_CP%d" % k for k in range(1, 5)} | {"J_CN%d" % k for k in range(1, 5)} | {"J_BM%d" % k for k in range(1, 8)}
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
def rail(n, ic_x):
    """regions of one converter: input caps west of the IC, output caps east, small parts south (above the fuse row)"""
    I = ["C42", "C43", "C44"] if n == 1 else (["C75", "C76", "C77"] if n == 2 else ["C88", "C89", "C90"])
    O = (["C45", "C46", "C47", "C48", "C49", "C70", "C95"] if n == 1 else (["C78", "C79", "C80", "C81", "C82", "C83", "C96"] if n == 2 else ["C91", "C92", "C93", "C94", "C97"]))
    S = (["C38", "C39", "R44", "C40", "C41", "R47", "R48"] if n == 1 else (["C71", "C72", "R61", "C73", "C74", "R62", "R63"] if n == 2 else ["C84", "C85", "R64", "C86", "C87", "R65", "R66"]))
    return [("M%dI" % n, (ic_x - 14, -30, ic_x - 4, -12), I), ("M%dO" % n, (ic_x + 4, -32, ic_x + 18, 0), O), ("M%dS" % n, (ic_x - 14, -38, ic_x + 4, -30), S)]
REGIONS = rail(1, -148) + rail(2, -116) + rail(3, -86) + [
 ("CHGW",  (-70, -71, -54, -47), ["C51", "C52", "C53", "C54", "C55", "C63", "C65", "R53", "R54", "R55", "R56", "R57", "R58", "R59"]),
 ("CHGE",  (-36, -71, -30, -47), ["C56", "C57", "C58", "C59", "C60", "C61", "C62", "C64", "C66", "C67", "R60"]),
 ("GAUGE", (-118, -64, -104, -52), ["C68", "C69", "RT1", "TP16", "TP4", "TP5", "R51"]),
 ("NODE",  (-160, -64, -152, -52), ["C7", "C50"]),
 ("CTRL",  (-162, 12, -130, 16), ["C98", "R67", "R68", "R69", "Q5", "R70"]),
 ("HEAT",  (-134, 22, -120, 34), ["C99", "R71", "R72", "R73", "C100", "F6"]),
 ("BUCK",  (-136, -2, -120, 10), ["C13", "C14", "C15", "C101", "R74", "R75", "D2", "R18"]),
 ("TPS",   (-162, 36, -130, 42), ["TP1", "TP2", "TP3", "TP6", "TP7", "TP10", "TP11", "TP12", "TP13", "TP14", "TP15"]),
 ("HUB",   (-104, 45, -30, 77), ["C16", "C17", "R19", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "R20", "R21", "R22", "R23", "R25", "R79", "U27", "U19", "C107", "R34", "R35", "R36", "R37", "R38", "TP17", "TP18"]),
 ("WALL",  (-104, 25, -80, 45), ["U28", "R76", "R77", "C104", "R78", "U29", "C105", "C106", "U30"]),
 ("EXP2",  (-78, 25, -32, 38), ["C108", "TP19", "TP20", "TP21", "TP22", "TP23", "TP24", "TP25", "TP26", "TP27"]),
 ("WIFI",  (-28, 44, 4, 70), ["U7", "R26", "R40", "C34", "R27", "U8", "C28", "C29", "U9"]),
 ("GPS",   (5, -61, 22, -36), ["U10", "R28", "R41", "C35", "R29"]),
 ("GPS2",  (24, -44, 48, -33), ["U11", "C30", "C31", "U12"]),
 ("MEZZCH", (-24, -51, 4, -24), ["U13", "R30", "R42", "C36", "R31", "U14", "C32", "C33", "U15", "U16", "R32", "R43", "C37", "R33", "U17", "C102", "C103", "U18", "R39", "TP8", "TP9", "TP28", "R24"]),
]
GAP = 1.2                      # between any two packed parts (was 0.7: fine-pitch ICs ended wall to wall with passives)
FINE_MARGIN = 1.6              # extra all round a fine-pitch IC so every side keeps a via lane for its escapes
import re as _re
def is_fine(fp):
    """Fine-pitch: minimum SMD pad centre distance <= 0.7 mm, or a SOT-23-6/8."""
    if _re.search(r"SOT-23-[68]", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
for name, (x0, y0, x1, y1), refs in REGIONS:
    fps = []
    for ref in refs:
        if ref not in comps: print("WARNING %s not in netlist" % ref); continue
        fp = place(ref, 0, 0); bb = fp.GetBoundingBox(False, False); fine = is_fine(fp); m = 2 * FINE_MARGIN if fine else 0.0
        fps.append((ref, fp, bb.GetWidth() / 1e6 + GAP + m, bb.GetHeight() / 1e6 + GAP + m, fine))
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
# --- planes: In1 GND, In2 +5V
def plane(layer, netname, name, rect=(-167.5, -85, 122.5, 85), priority=0):
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
plane(pcbnew.In1_Cu, "GND", "GND plane In1"); plane(pcbnew.In2_Cu, "+5V_M1", "+5V_M1 plane In2 (A19 rail M1: logic, hub, channels)")
for k, x in enumerate(RF_X, 1): plane(pcbnew.In2_Cu, "GND", "GND island In2 under blind-mate site %d" % k, rect=(x - 8, -74, x + 8, -58), priority=1)
plane(pcbnew.In2_Cu, "CELL+", "CELL+ pour In2 (node bar from the dock block to the fuse row)", rect=(-160, -64, -60, -44), priority=1)
# --- net classes (API first; the project JSON is re-applied after the save because SaveBoard rewrites it)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr, dpw, dpg):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr)); nc.SetDiffPairWidth(FromMM(dpw)); nc.SetDiffPairGap(FromMM(dpg)); nc.SetDiffPairViaGap(FromMM(0.25))
cls(ns.GetDefaultNetclass(), 0.15, 0.25, 0.7, 0.3, 0.2, 0.15)
CLASSES = {"USB": (0.15, 0.2, 0.7, 0.3, 0.2, 0.15), "PWR": (0.15, 0.4, 0.8, 0.4, 0.4, 0.25), "BANK": (0.3, 4.0, 1.2, 0.6, 0.5, 0.25), "BOOST": (0.2, 1.5, 1.0, 0.5, 1.2, 0.3), "RAIL": (0.2, 2.0, 1.0, 0.5, 1.2, 0.3), "RF": (0.3, 0.35, 0.7, 0.3, 0.2, 0.15)}   # pack node: 4 mm tracks, up to 10 A peaks   # 0.4 mm enters 0.65-pitch pads; the In2 plane carries the bulk 5 V
PATTERNS = [("USB_*", "USB"), ("5V_*", "PWR"), ("SW_*", "PWR"), ("*_FUSED", "PWR"), ("GND", "PWR"), ("SHORE_12V", "PWR"), ("HEAT_*", "PWR"), ("PMID", "PWR"), ("SYS_CHG", "PWR"), ("SW*_CHG", "PWR"), ("CELL*", "BANK"), ("MEZZ_CELL", "BANK"), ("BOOST*_IN", "BOOST"), ("SW1", "BOOST"), ("SW2", "BOOST"), ("SW3", "BOOST"), ("+5V_M1", "RAIL"), ("+5V_M2", "RAIL"), ("+5V_PI", "RAIL"), ("RF_*", "RF")]
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
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.15, 0.25, 0.7, 0.3, 0.2, 0.15), C("USB", 0, 0.15, 0.2, 0.7, 0.3, 0.2, 0.15), C("PWR", 1, 0.15, 0.4, 0.8, 0.4, 0.4, 0.25), C("BANK", 2, 0.15, 0.5, 0.9, 0.5, 0.5, 0.25), C("BOOST", 3, 0.2, 1.5, 1.0, 0.5, 1.2, 0.3), C("RAIL", 4, 0.2, 2.0, 1.0, 0.5, 1.2, 0.3), C("RF", 5, 0.3, 0.35, 0.7, 0.3, 0.2, 0.15)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None); d["net_settings"].setdefault("netclass_assignments", None)
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied")
