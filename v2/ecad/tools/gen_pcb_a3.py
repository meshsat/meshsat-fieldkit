#!/usr/bin/env python3
"""PCB-A phase A22 (MESHSAT-830, 7 Sep 2026): bring the schematic netlist into the mechanical board of gen_pcb_a.py.
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
# --- fixed positions (case frame), appendix 32.56
RF_X = [-52, -38, -24, -10, 4, 18, 32, 60, 74, 88, 100]
FIXED = {"J_AB1": (113, -46, 0), "J_MEZZ_PWR1": (-8, -18, 90),
         "J_DOCK": (-76, -70, 0), "J_PRE1": (-103, -70, 0), "F1": (-97, -52, 0), "J_MAINSW": (98, 75, 0),
         "U2": (-94, 56, 0), "L1": (-78, 58, 0), "U3": (-96, 12, 0), "L2": (-80, 16, 0), "U16": (-96, -26, 0), "L10": (-78, -24, 0),
         "U4": (-60, 66, 0), "U5": (-44, 66, 0), "U6": (-28, 66, 0), "U7": (-12, 66, 0), "L3": (-58, 54, 0), "L4": (-42, 54, 0), "L5": (-26, 54, 0), "L6": (-10, 54, 0), "U8": (-64, 28, 0), "U9": (-56, 28, 0), "U10": (-48, 28, 0), "U11": (-40, 28, 0), "U14": (-32, 28, 0),
         "J_5V_S1": (-56, 75, 0), "J_5V_S2": (-44, 75, 0), "J_5V_S3": (-32, 75, 0), "J_5V_DEV": (-20, 75, 0),
         "U13": (-44, 6, 0), "L8": (-26, 4, 0), "U15": (-36, -27, 0), "L9": (-22, -27, 0), "U12": (-64, 10.5, 0), "L7": (-58, 10.5, 0), "U1": (-49, -28, 0),
         "U26": (-58, -28, 0), "U27": (-50, -19, 0), "U28": (-62, -19, 0),
         "U18": (10, 65, 0), "U19": (36, 64, 0), "L11": (56, 65, 0), "U21": (70, 66, 0), "U22": (80, 66, 0), "U23": (90, 66, 0),
         "J_PA": (110, 62, 90), "J_MON": (110, 50, 90), "J_HEAT": (110, 38, 90), "J_USBC_OUT": (110, 26, 90), "J_HF": (110, 12, 90), "J_54V": (110, 0, 90), "J_USBW": (110, -12, 90)}
for k in range(4): FIXED["J_CP%d" % (k + 1)] = (-99 + 4 * k, -73, 0); FIXED["J_CN%d" % (k + 1)] = (-99 + 4 * k, -67, 0)
for k, x in enumerate(RF_X, 1): FIXED["J_BM%d" % k] = (x, -66, 0); FIXED["J_RF%d" % k] = (x, -56, 0)
BACK = {"J_DOCK", "J_PRE1"} | {"J_CP%d" % k for k in range(1, 5)} | {"J_CN%d" % k for k in range(1, 5)} | {"J_BM%d" % k for k in range(1, 12)}
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
# --- regions for the rest: (x0, y0, x1, y1), refs (appendix 32.56 zones)
def lm5176_refs(qs, rs, cs): return list(qs) + list(rs) + list(cs)
REGIONS = [
 ("NODE",  (-118, -68, -106, -44), ["C1", "C2", "C3", "D1", "R1", "TP14", "TP9"]),
 ("FEQ",   (-118, 34, -70, 46), ["Q2", "Q3", "Q4", "Q5", "R11", "R12", "C11", "C12", "D2"]),
 ("FES",   (-118, 46, -100, 66), ["R6", "R7", "R8", "R9", "R10", "C5", "C6", "C7", "C8", "C9", "C10", "R13", "R14", "R15", "R119", "C13", "C14", "C15", "TP12", "TP13"]),
 ("CHQ",   (-118, 22, -70, 34), ["Q7", "Q8", "Q9", "Q10", "R16", "R17", "C20", "C21", "C22", "C23", "C24", "C25"]),
 ("CHS",   (-115, -6, -70, 6), ["C16", "C17", "C18", "R18", "C19", "R19", "R20", "Q6", "R21", "R22", "R23", "R24", "R25", "C26", "C27", "R26", "R27", "TP19", "TP20", "TP22"]),
 ("POQ",   (-118, -44, -46, -32), ["Q17", "Q18", "Q19", "Q20", "R71", "R72", "C81", "C82", "C83", "C84", "C85"]),
 ("POS",   (-115, -17, -70, -6), ["R66", "R67", "R68", "R69", "R70", "C75", "C76", "C77", "C78", "C79", "C80", "R73", "R74", "R75", "R121", "U17"]),
 ("R1S",   (-66, 34, -50, 50), ["C28", "C31", "C32", "C33", "R28", "R29", "R30", "R45", "R129", "C112"]),
 ("VC1",   (-66, 58, -54, 63), ["C29", "C30"]), ("VC2", (-50, 58, -38, 63), ["C35", "C36"]), ("VC3", (-34, 58, -22, 63), ["C41", "C42"]), ("VC4", (-18, 58, -6, 63), ["C47", "C48"]),
 ("R2S",   (-50, 34, -34, 50), ["C34", "C37", "C38", "C39", "R32", "R33", "R34", "R46", "R130", "C113"]),
 ("R3S",   (-34, 34, -18, 50), ["C40", "C43", "C44", "C45", "R36", "R37", "R38", "R47", "R131", "C114"]),
 ("RDS",   (-18, 34, -2, 50), ["C46", "C49", "C50", "C51", "R40", "R41", "R42", "R44", "R115", "R132", "C115"]),
 ("SHUNT", (-66, 20, -14, 25.5), ["R31", "R35", "R39", "R43", "R56"]),
 ("PAQ",   (-66, -14, -16, -2), ["Q11", "Q12", "Q13", "Q14", "R55", "C63", "C64", "C65", "C66", "C67", "C54", "D3"]),
 ("PAS",   (-66, 13, -16, 20), ["R50", "R51", "R52", "R53", "R54", "C57", "C58", "C59", "C60", "C61", "C62", "R57", "R58", "R59", "R120"]),
 ("HFQ",   (-46, -48, -16, -34), ["Q15", "Q16", "Q23", "Q24", "R65", "R122"]),
 ("HFS",   (-16, -50, -2, -23), ["R60", "R61", "R62", "R63", "R64", "C68", "C69", "C70", "C71", "C72", "C73", "R123", "R124", "R125", "R126", "C74", "C108", "C109", "C110", "C111"]),
 ("B33",   (-66, -2, -48, 8), ["C52", "C53", "C55", "C56", "R48", "R49"]),
 ("CTL",   (52, -38, 90, -24), ["C4", "R2", "R3", "R4", "Q1", "R5", "R102", "C104", "R103", "R104", "C106", "C107", "R110", "R111", "R112", "R113", "R114"]),
 ("TPS",   (10, -38, 50, -24), ["TP%d" % k for k in range(3, 9)] + ["TP10", "TP11", "TP15", "TP16", "TP17", "TP18", "TP21", "TP23", "TP24", "TP25", "TP26", "R116", "R117", "R118", "U29"]),
 ("PDS",   (0, 44, 30, 62), ["C93", "C94", "C95", "C96", "C97", "C120", "D4", "R136", "R137", "R138", "R139", "R140", "R141", "R142", "R143", "Q27"]),
 ("PDQ",   (30, 44, 84, 58), ["Q21", "Q22", "Q25", "Q26", "R81", "R127", "C92", "C116", "C117", "C118", "C119", "R76", "R77", "R78", "R79", "R80", "C86", "C87", "C88", "C89", "C90", "C91", "R128", "R133", "R134", "R135"]),
 ("EFS",   (84, 44, 100, 62), ["C98", "R90", "R91", "R92", "R93", "C99", "C100", "R94", "R95", "R96", "R97", "C101", "C102", "R98", "R99", "R100", "R101", "C103"]),
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
# --- planes: In1 GND (solid, the 5 Sep ruling), In2 VBAT over the converter columns with GND islands under the blind-mate sites; the pack node as locked outer pours
def plane(layer, netname, name, rect=(-117.5, -77.5, 117.5, 77.5), priority=0):
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
plane(pcbnew.In1_Cu, "GND", "GND plane In1")
plane(pcbnew.In2_Cu, "VBAT", "VBAT plane In2 (west and middle columns)", rect=(-117.5, -44, -2, 77.5))
plane(pcbnew.In2_Cu, "GND", "GND plane In2 (east)", rect=(-2, -77.5, 117.5, 77.5))
plane(pcbnew.In2_Cu, "GND", "GND island In2 under the blind-mate row", rect=(-60, -77.5, 110, -48), priority=1)
def outer_pour(netname, name, rect, layers=(pcbnew.F_Cu, pcbnew.B_Cu), priority=2):
    for L in layers:
        z = pcbnew.ZONE(board); z.SetLayer(L); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name + " " + board.GetLayerName(L)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetMinThickness(FromMM(0.5)); z.SetLocalClearance(FromMM(0.3)); o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
        z.SetAssignedPriority(priority); board.Add(z)
# the pack node: CELL+ from the four 9 A pins (Y -73) up to F1's pad 1 (Y -46), and the charger's RSR at the CHQ region; the return pins are GND (the In1 plane)
outer_pour("CELL+", "node bar", (-104, -77, -86, -70), priority=2); outer_pour("CELL+", "node riser", (-104, -70, -98, -47), priority=3)
# rule area for In1: tracks forbidden, vias allowed (the 5 Sep 2026 ruling; A22 has no fine-pitch window to open)
z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
z.SetLayer(pcbnew.In1_Cu); z.SetZoneName("In1 solid ground: no tracks"); o = z.Outline(); o.NewOutline()
for x, y in ((-119, -79), (119, -79), (119, 79), (-119, 79)): p = P(x, y); o.Append(p.x, p.y)
board.Add(z)
# --- net classes (API first; the project JSON is re-applied after the save because SaveBoard rewrites it)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr, dpw, dpg):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr)); nc.SetDiffPairWidth(FromMM(dpw)); nc.SetDiffPairGap(FromMM(dpg)); nc.SetDiffPairViaGap(FromMM(0.25))
cls(ns.GetDefaultNetclass(), 0.127, 0.25, 0.7, 0.3, 0.2, 0.15)
# clearances at the board minimum (7 Sep 2026: with the explicit net-class assignments the DRC enforces them, and a class clearance above a fine-pitch pad gap of 0.2 fails inside the LM5176 and TPS23861 pads); HV 0.18 for the 54 V nodes
CLASSES = {"USB": (0.127, 0.2, 0.7, 0.3, 0.2, 0.15), "PWR": (0.127, 0.4, 0.8, 0.4, 0.4, 0.25), "NODE": (0.127, 0.5, 0.8, 0.4, 0.5, 0.25), "SW": (0.127, 0.5, 1.0, 0.5, 0.8, 0.3), "RAIL": (0.127, 0.4, 1.0, 0.5, 0.5, 0.3), "RF": (0.18, 0.35, 0.7, 0.3, 0.2, 0.15), "HV": (0.18, 0.4, 0.8, 0.4, 0.4, 0.25)}
PATTERNS = [("USB_*", "USB"), ("PD_CC*", "USB"), ("CELL+", "NODE"), ("VBAT", "NODE"), ("PRECHG", "PWR"), ("VIN_RAW", "NODE"), ("VBUS20", "NODE"), ("CH_ACN", "NODE"), ("CH_SRP", "NODE"), ("CH_SW*", "SW"), ("FE_SW*", "SW"), ("FE_OUT", "NODE"), ("FE_CS", "SW"),
            ("PA_SW*", "SW"), ("PA_OUT", "NODE"), ("PA_CS", "SW"), ("HF_SW*", "SW"), ("HF_OUT", "PWR"), ("PD_SW*", "SW"), ("PD_OUT", "PWR"), ("PD_PPHV", "PWR"), ("PD_VBUS", "PWR"), ("S?_SW", "SW"), ("SD_SW", "SW"), ("S?_OUT", "RAIL"), ("SD_OUT", "RAIL"), ("PD_VPWR", "PWR"), ("PD_SW", "PWR"),
            ("+5V_*", "RAIL"), ("+13V8_PA", "RAIL"), ("+12V_HF", "RAIL"), ("VMON", "PWR"), ("VHEAT", "PWR"), ("GND", "PWR"), ("+3V3", "PWR"), ("B33_SW", "SW"), ("RF_*", "RF"), ("POE_SW*", "HV"), ("POE_OUT", "HV"), ("+54V_POE", "HV"), ("POE_CS", "SW")]
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
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.127, 0.25, 0.7, 0.3, 0.2, 0.15)] + [C(nm, i, *v) for i, (nm, v) in enumerate(CLASSES.items())]
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
