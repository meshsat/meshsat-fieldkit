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
RF_X = [-100, -84, -26, -12, 70, 92, 103]; RF_JY = [-56, -56, -56, -56, -74, -74, -54]; RF_JX = [-100, -84, -26, -12, 70, 92, 107]; RF_BY = [-66, -66, -66, -66, -66, -66, -64]
FIXED = {"J_AB1": (-72, -73, 90), "J_LEDS1": (-38, -74, 0), "J_MEZZ_PWR1": (-8, -18, 90),
         "J_DOCK": (-124, -70, 0), "J_PRE1": (-151, -70, 0),
         "F3": (-150, -46, 0), "F4": (-125, -46, 0), "F5": (-100, -46, 0), "F2": (-75, -46, 0),
         "U22": (-148, -20, 0), "L2": (-148, -6, 0), "U23": (-116, -20, 0), "L3": (-116, -6, 0), "U24": (-84, -20, 0), "L4": (-84, -6, 0),
         "U20": (-50, -58, 0), "L5": (-40, -58, 0), "U21": (-112, -60, 0), "R52": (-120, -60, 0),
         "J_5V_M1": (-150, 44, 0), "J_5V_M2": (-135, 44, 0), "J_5V_PI": (-120, 44, 0),
         "U25": (-150, 19, 0), "J_MAINSW": (-159, 8, 90), "U26": (-140, 28, 0), "J_HEAT": (-159, 28, 90), "U5": (-150, 4, 0), "L6": (-142, 4, 0),
         "J_WALL1": (-156, 62, 270), "U31": (-45, 41, 0)}   # A20: no hub (U6, Y1)
for k in range(4): FIXED["J_CP%d" % (k + 1)] = (-147 + 4 * k, -73, 0); FIXED["J_CN%d" % (k + 1)] = (-147 + 4 * k, -67, 0)
for k, (x, jx, jy, by) in enumerate(zip(RF_X, RF_JX, RF_JY, RF_BY), 1): FIXED["J_BM%d" % k] = (x, by, 0); FIXED["J_RF%d" % k] = (jx, jy, 0)
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
    return [("M%dI" % n, (ic_x - 14, -30, ic_x - 6, -12), I), ("M%dO" % n, (ic_x + 6, -32, ic_x + 18, 0), O), ("M%dS" % n, (ic_x - 14, -38, ic_x + 4, -30), S)]
REGIONS = rail(1, -148) + rail(2, -116) + rail(3, -84) + [
 ("CHGN",  (-64, -54, -31, -46), ["C51", "C52", "C53", "C54", "C55", "C56", "C57", "C63", "R53", "R54", "R55", "R56", "R57", "R58"]),
 ("CHGS",  (-64, -70, -31, -61), ["C58", "C59", "C60", "C61", "C62", "C65", "C64", "C66", "C67", "R59", "R60"]),
 ("GAUGE", (-150, -64, -125, -56), ["C68", "C69", "RT1", "TP16", "TP4", "TP5", "R51"]),
 ("NODE",  (-160, -64, -152, -52), ["C7", "C50"]),
 ("CTRL",  (-154, 9, -130, 17), ["C98", "R67", "R68", "R69", "Q5", "R70"]),
 ("HEAT",  (-134, 22, -120, 34), ["C99", "R71", "R72", "R73", "C100", "F6"]),
 ("BUCK",  (-136, 1, -118, 14), ["C13", "C14", "C15", "C101", "R74", "R75", "D2", "R18"]),
 ("TPS",   (-162, 32, -128, 39.5), ["TP1", "TP2", "TP3", "TP6", "TP7", "TP10", "TP11", "TP12", "TP13", "TP14", "TP15"]),
 ("HUB",   (-104, 45, -30, 77), ["U19", "C107", "R34", "R35", "R36", "R37", "R38", "TP17", "TP18"] + ["TP%d" % k for k in range(29, 37)]),   # A20: the expander and LED drivers alone
 ("WALL",  (-104, 25, -80, 45), ["U28", "R76", "R77", "C104", "R78", "U29", "C105", "C106", "U30"]),
 ("EXP2",  (-78, 25, -32, 35), ["C108", "TP19", "TP20", "TP21", "TP22", "TP23", "TP24", "TP25", "TP26", "TP27"]),
 ("MEZZCH", (-24, -51, 4, -24), ["R39", "TP8", "TP9"]),   # A20: the codec and UART channels are gone
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
# --- planes: In1 GND, In2 +5V
def plane(layer, netname, name, rect=(-167.5, -85, 122.5, 85), priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
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
for k, rect in enumerate(((-108, -74, -76, -58), (-34, -74, -4, -58), (62, -74, 78, -58), (84, -74, 111, -56)), 1): plane(pcbnew.In2_Cu, "GND", "GND island In2 under blind-mate sites, group %d" % k, rect=rect, priority=1)
plane(pcbnew.In2_Cu, "CELL+", "CELL+ pour In2 (node bar under the fuse row, west of the RF islands)", rect=(-160, -56, -116, -44), priority=1)
# A19 node copper as pre-route pours on both outer layers (the router keeps clear of them): CELL+ from the four 9 A pins (Y -73) south to a bar at Y -77,
# up the west edge to a bar at Y -40 above the fuse row, with taps down to each fuse's node pad; CELL_N from the return pins (Y -67) north to the shunt R52.
def outer_pour(netname, name, rect, layers=(pcbnew.F_Cu, pcbnew.B_Cu), priority=2):
    for L in layers:
        z = pcbnew.ZONE(board); z.SetLayer(L); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name + " " + board.GetLayerName(L)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetMinThickness(FromMM(0.5)); z.SetLocalClearance(FromMM(0.3)); o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
        z.SetAssignedPriority(priority); board.Add(z)   # bars 2, taps 3: intersecting zones must carry distinct priorities
outer_pour("CELL+", "node bar south", (-160, -79, -133, -75)); outer_pour("CELL+", "node riser west", (-163, -79, -158, -38.5), priority=1); outer_pour("CELL+", "node bar north", (-163, -42, -50, -38.5))
for k in range(4): outer_pour("CELL+", "pin tap %d" % (k + 1), (-148.5 + 4 * k, -77, -145.5 + 4 * k, -72), priority=3)
for ref in ("F3", "F4", "F5", "F2"):
    fx = placed[ref].Pads()[0].GetPosition().x / 1e6 - OX if ref in placed else None
    for pad in placed[ref].Pads():
        if pad.GetNumber() == "1": fx = pad.GetPosition().x / 1e6 - OX
    outer_pour("CELL+", "fuse tap " + ref, (fx - 1.5, -47, fx + 1.5, -38.5), priority=3)
outer_pour("CELL_N", "return bar", (-149, -66, -121, -60))
# --- A21 (5 Sep 2026, appendix 32.39): the rails and the boost inputs get bottom-side copper bands so the router only closes short stubs into them
#     (the RAIL and BOOST classes at 2.0 and 1.5 mm left 20 connections open; the classes are now 1.0 and 0.8 and these bands carry the current).
#     Rails M2 and PI run from their output capacitors (C96 at (-107, -15), C97 at (-75, -11)) west along the boost row and north to the VH connectors at y 44.5;
#     rail M1 has its In2 plane. Boost inputs: fuse (THT, y -44.3) north to the inductor pad (fanned out to a via). CELL+ gets a tap to the mezzanine fuse F2.
# The bootstrap capacitors go right under their converters after the packer has run (A21 runs 10 and 14: 13 mm away in the compensation row, BST1 and
# BST2 could not cross the boost feed columns; a FIXED entry made a second, netless instance and the DSN export failed in run 16)
for _ref, _xb in (("C38", -148.0), ("C71", -116.0), ("C84", -84.0)):
    if _ref in placed: placed[_ref].SetOrientationDegrees(0); centre_on(placed[_ref], _xb, -24.2)
B = (pcbnew.B_Cu,); I2 = (pcbnew.In2_Cu,)
def K(x0, y0, x1, y1): return (x0 - OX, OY - y1, x1 - OX, OY - y0)      # a rectangle given in the KiCad frame, for outer_pour and track_keepout
def track_keepout(name, rect, layer=pcbnew.B_Cu):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayer(layer); z.SetZoneName("keep tracks off " + name); o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    board.Add(z)
# Rail bands on B.Cu (KiCad frame; converters U22/U23/U24 at x 2.1/34.1/66.1, y 130; inductors L2/L3/L4 pad 1 at x -1.3/30.7/62.7, y 111.5 to 120.5;
# VH connectors J_5V_M2 at (13.2, 65.5) and J_5V_PI at (28.2, 65.5)). Runs 8 and 9 of 5 Sep showed every east-west collector south of the inductor row cut
# by a north-south band of another net, so both collectors run north of the inductors, side by side (M2 at y 109.5 to 112.8, PI at 103.5 to 106.8), each
# with a tap down to its island's stitch vias east of the output capacitors and a riser to its VH pin. Every band has a B.Cu track keep-out (vias allowed,
# so escape.py and prefanout.py ignore it): the router crosses a band on F.Cu, In1 or In2 and cannot slice it.
BANDS = [("+5V_M2", "rail M2 collector", K(10.0, 109.5, 51.5, 112.8), 2), ("+5V_M2", "rail M2 tap", K(47.5, 109.5, 51.5, 128.5), 3), ("+5V_M2", "rail M2 riser", K(10.0, 63.5, 16.0, 112.8), 3),
         ("+5V_PI", "rail PI collector", K(25.0, 103.5, 79.5, 106.8), 2), ("+5V_PI", "rail PI tap", K(70.5, 103.5, 79.5, 124.0), 3), ("+5V_PI", "rail PI riser", K(25.0, 63.5, 31.0, 106.8), 3)]
# (the PI corridor sits 2 mm further north than the M2 one leaves room for: run 12 of 5 Sep left R18 pin 2 (LED_PWR_A, at (25.4, 107.6)) open under the
#  riser's keep-out, since Freerouting places no via inside a wire keep-out and that net has to leave on an inner layer)
for net, name, rect, prio in BANDS: outer_pour(net, name, rect, layers=B, priority=prio); ("tap" not in name) and track_keepout(name, rect)   # the taps sit in the capacitor columns whose GND vias need the room (run 13: BOOST_EN could not via past the M2 tap)
def island(netname, name, pts_k, priority=3, layer=pcbnew.F_Cu):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name + " " + board.GetLayerName(layer))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.15)); o = z.Outline(); o.NewOutline()
    for x, y in pts_k: o.Append(FromMM(x), FromMM(y))
    z.SetAssignedPriority(priority); board.Add(z)
def spine(netname, x0, y0, x1, y1, w=0.4, layer=pcbnew.F_Cu):
    """a locked track inside an island: the router keeps its clearance from a fixed track, which it does not from a plane outline
    (run 21: a BST3 track along U24's island edge made the fill retreat and cut the neck off the body)"""
    t = pcbnew.PCB_TRACK(board); t.SetStart(VECTOR2I(FromMM(x0), FromMM(y0))); t.SetEnd(VECTOR2I(FromMM(x1), FromMM(y1))); t.SetWidth(FromMM(w)); t.SetLayer(layer)
    t.SetNet(net_for(netname, create=False)); t.SetLocked(True); board.Add(t)
def stitch(netname, pts_k):
    for x, y in pts_k:
        v = pcbnew.PCB_VIA(board); v.SetPosition(VECTOR2I(FromMM(x), FromMM(y))); v.SetDrill(FromMM(0.4)); v.SetWidth(FromMM(0.8)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetNet(net_for(netname, create=False)); v.SetLocked(True); board.Add(v)
# Boost feeds (up to 9.5 A into the Pi converter at a 3.0 V node): JLC's 4-layer stack has 0.5 oz inner copper, so a 6 mm In2 column alone is good for
# about 3 A at 10 K. Each feed is therefore an In2 column from the blade fuse's BOOST pad (pin 2, x 5/30/55, y 154.3 and 157.7, plated through, so the
# column starts in the pad itself) north to the inductor row, widened to a 19 mm foot on In2 and In1 where it passes under the CELL+ node bar (y 148.5 to 152),
# and a B.Cu column of the same width in parallel on both sides of the bar (fuse pad to the bar, bar to the inductor jog), tied to the In2 column by
# locked 0.8/0.4 vias at both ends of the bar and by the six inductor tap vias at its north end. Run 9's B.Cu feed bands were centred on the fuses' CELL+ pads and cut by the node bar.
BOOST = [("BOOST1_IN", 1, 4.1, 9.5, (-3.5, 9.5), (-2.0, 17.0)),     # column x, jog x (west to the L2 tap), foot x (between the CELL+ pad rings of F3 and F4)
         ("BOOST2_IN", 2, 27.0, 33.0, None, (23.0, 42.0)),          # L3's tap sits in the column
         ("BOOST3_IN", 3, 52.0, 58.0, (52.0, 64.5), (48.0, 67.0))]  # jog east to the L4 tap
I1 = (pcbnew.In1_Cu,)
for net, n, cx0, cx1, jog, foot in BOOST:
    col = K(cx0, 121.0, cx1, 158.5); ft = K(foot[0], 147.5, foot[1], 153.0); bot = K(cx0, 121.0, cx1, 148.2); south = K(cx0, 152.3, cx1, 158.5)
    outer_pour(net, "boost %d column" % n, col, layers=I2, priority=2); track_keepout("boost %d column" % n, col, layer=pcbnew.In2_Cu)
    outer_pour(net, "boost %d foot" % n, ft, layers=I2, priority=3); track_keepout("boost %d foot" % n, ft, layer=pcbnew.In2_Cu)          # under the node bar only (y 148.5 to 152)
    outer_pour(net, "spare foot boost %d" % n, ft, layers=I1, priority=3)                                                                # In1 in parallel, best effort: no keep-out, not gated
    outer_pour(net, "boost %d bottom" % n, bot, layers=B, priority=2); track_keepout("boost %d bottom" % n, bot)                        # north of the node bar
    outer_pour(net, "boost %d bottom south" % n, south, layers=B, priority=2); track_keepout("boost %d bottom south" % n, south)        # from the fuse pad to the node bar
    if jog:
        jg = K(jog[0], 120.5, jog[1], 124.5)
        outer_pour(net, "boost %d jog" % n, jg, layers=I2, priority=4); track_keepout("boost %d jog" % n, jg, layer=pcbnew.In2_Cu)
        outer_pour(net, "boost %d bottom jog" % n, jg, layers=B, priority=3); track_keepout("boost %d bottom jog" % n, jg)
    stitch(net, [(cx0 + 1.2, 146.0), (cx1 - 1.2, 146.0), (cx0 + 1.2, 147.5), (cx1 - 1.2, 147.5)])   # In2 to B.Cu north of the bar
    stitch(net, [(cx0 + 0.6, 152.6), (cx1 - 0.6, 152.6)])                                          # In2 and In1 feet to the B.Cu south segment, at the column edges: the fuse pin sits on the column axis 1.7 mm south (hole to hole 0.3)
# --- A21 output islands (5 Sep 2026, appendix 32.39): the TPS61288L VOUT pin is a 1.25 x 0.40 mm pad with its neighbours 0.25 mm away, so no 1.0 mm track
#     can leave it (the six opens of the 14:20 run, every one at pad 5 of U22/U23/U24) and the escape scheme had given each rail one 0.2 mm stub and one
#     0.45/0.25 via as its whole current path. Each converter gets a top-side copper island: a 0.5 mm neck over the east end of pad 5 (between pad 6 and the
#     package edge), widening east of the escape vias over the output capacitor group, stitched to the rail's bottom tap (M2, PI) or the In2 plane (M1) by six
#     locked 0.8/0.4 vias. The RAIL class is the link width only (0.5 mm); the islands, bands and planes carry the current. Coordinates in the KiCad frame,
#     relative to the part.
for ref, net, vias in (("U22", "+5V_M1", [(14.88, -6.0), (16.38, -6.0), (14.88, -4.4), (16.38, -4.4), (14.88, -2.8), (16.38, -2.8)]),      # into the In2 plane, south of C70, between the boost 1 and 2 columns
                       ("U23", "+5V_M2", [(13.88, -6.0), (15.38, -6.0), (16.88, -6.0), (13.88, -4.4), (15.38, -4.4), (16.88, -4.4)]),      # into the M2 tap (B.Cu, KiCad x 47.5 to 51.5)
                       ("U24", "+5V_PI", [(5.13 + 1.5 * k, -7.0) for k in range(6)])):                                                  # into the PI tap (B.Cu, KiCad x 70.5 to 79.5, y 105.5 to 124)
    x0 = placed[ref].GetPosition().x / 1e6; y0 = placed[ref].GetPosition().y / 1e6
    island(net, "VOUT island " + ref, [(x0 + 1.4, y0 - 0.05), (x0 + 3.6, y0 - 0.05), (x0 + 3.6, y0 - 15.4), (x0 + 17.5, y0 - 15.4), (x0 + 17.5, y0 + 4.0), (x0 + 3.6, y0 + 4.0), (x0 + 3.6, y0 + 0.45), (x0 + 1.4, y0 + 0.45)])
    stitch(net, [(x0 + dx, y0 + dy) for dx, dy in vias])
    spine(net, x0 + 1.5, y0 + 0.2, x0 + 5.2, y0 + 0.2)   # pad 5 east end, through the neck and 1.6 mm into the body
# Inductor tap islands: over the south end of pad 1 (2.38 x 9.0 mm, y 111.5 to 120.5) and 3.5 mm beyond it, six 0.8/0.4 vias down to the In2 and B.Cu feeds
for ref, net in (("L2", "BOOST1_IN"), ("L3", "BOOST2_IN"), ("L4", "BOOST3_IN")):
    pad = [p for p in placed[ref].Pads() if p.GetNumber() == "1"][0]; px, py = pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6
    island(net, "inductor tap " + ref, [(px - 2.0, py + 3.8), (px + 2.0, py + 3.8), (px + 2.0, py + 8.0), (px - 2.0, py + 8.0)])
    stitch(net, [(px + dx, py + dy) for dx in (-1.0, 0.0, 1.0) for dy in (5.6, 7.0)])   # six vias: 9.5 A at 2.5 A per 0.4 mm hole with margin
    spine(net, px, py + 4.2, px, py + 7.4, w=0.8)   # from the pad's south end through the middle via column
for k in range(4): outer_pour("CELL_N", "return tap %d" % (k + 1), (-148.0 + 4 * k, -68, -146.0 + 4 * k, -60), priority=3)
# The inner layers stay open to the router. Banning tracks there (tried 4 Sep) leaves Freerouting two layers for 148 nets and 279
# footprints, and the best of four attempts came back with 83 nets unrouted; A17 routed on all four and the plane fill simply
# carves clearance around the inner tracks (the isolated_copper notes, cosmetic).
# --- net classes (API first; the project JSON is re-applied after the save because SaveBoard rewrites it)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr, dpw, dpg):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr)); nc.SetDiffPairWidth(FromMM(dpw)); nc.SetDiffPairGap(FromMM(dpg)); nc.SetDiffPairViaGap(FromMM(0.25))
cls(ns.GetDefaultNetclass(), 0.15, 0.25, 0.7, 0.3, 0.2, 0.15)
CLASSES = {"USB": (0.15, 0.2, 0.7, 0.3, 0.2, 0.15), "PWR": (0.15, 0.4, 0.8, 0.4, 0.4, 0.25), "BANK": (0.15, 0.6, 1.2, 0.6, 0.5, 0.25), "BOOST": (0.15, 0.8, 1.0, 0.5, 0.8, 0.3), "RAIL": (0.15, 0.5, 1.0, 0.5, 0.5, 0.3), "RF": (0.3, 0.35, 0.7, 0.3, 0.2, 0.15)}   # pack node: 4 mm tracks, up to 10 A peaks   # 0.4 mm enters 0.65-pitch pads; the In2 plane carries the bulk 5 V
PATTERNS = [("USB_*", "USB"), ("5V_*", "PWR"), ("SW_*", "PWR"), ("GND", "PWR"), ("SHORE_12V", "PWR"), ("HEAT_*", "PWR"), ("PMID", "PWR"), ("SYS_CHG", "PWR"), ("SW*_CHG", "PWR"), ("CELL+", "BANK"), ("CELL_N", "PWR"), ("MEZZ_CELL", "BANK"), ("BOOST*_IN", "BOOST"), ("SW1", "BOOST"), ("SW2", "BOOST"), ("SW3", "BOOST"), ("+5V_M1", "RAIL"), ("+5V_M2", "RAIL"), ("+5V_PI", "RAIL"), ("RF_*", "RF")]
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]   # 5 Sep 2026 (gateway finding, MESHSAT-802): root-sheet labels are "/NAME" on the board and KiCad's pattern matcher does not strip the slash, so every label pattern is emitted in both forms; power symbols (GND, +3V3) have no slash
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
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.15, 0.25, 0.7, 0.3, 0.2, 0.15), C("USB", 0, 0.15, 0.2, 0.7, 0.3, 0.2, 0.15), C("PWR", 1, 0.15, 0.4, 0.8, 0.4, 0.4, 0.25), C("BANK", 2, 0.15, 0.6, 1.2, 0.6, 0.5, 0.25), C("BOOST", 3, 0.15, 0.8, 1.0, 0.5, 0.8, 0.3), C("RAIL", 4, 0.15, 0.5, 1.0, 0.5, 0.5, 0.3), C("RF", 5, 0.3, 0.35, 0.7, 0.3, 0.2, 0.15)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None); d["net_settings"].setdefault("netclass_assignments", None)
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.127
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied")
