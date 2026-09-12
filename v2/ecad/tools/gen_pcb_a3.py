#!/usr/bin/env python3
"""PCB-A phase A23 (MESHSAT-862 rule 3, 8 Sep 2026; A22 of MESHSAT-830 before it): bring the schematic netlist into the mechanical board of gen_pcb_a.py,
and lay every rail's current in locked copper (islands, bottom bands, stitch vias) built from the placed pads, judged by dc_drop.py (appendix 32.67, 32.69).
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
# run 11 (7 Sep 2026): the INA226 row U8, U9, U10, U11 at 12 mm pitch (the 0.5 mm MSOP fans of two neighbours at 8 mm collided and U10 got no escape at all)
FIXED = {"J_AB1": (113, -46, 0), "J_MEZZ_PWR1": (-8, -18, 90),
         # 12 September 2026: the wall pair's own ribbon. The east strip is full (the gate refused (113, -62) for the
         # rod nut at (110.5, -73), correctly), and the FIXED position is PIN 1 with the rows running north, so this
         # puts the body in the free window at case (99, -20). Its pair sits on the END row (appendix 32.135).
         # rot 180 because the twist is a presentation, not a distance: at rot 0 J_AB2 and U29 (the wall port's ESD)
         # put the pair's pads on opposite sides of the line between them, the legs must cross once, and the dive at
         # the pad field left one crossing behind. Turning the connector round removes the twist at its source.
         "J_AB2": (95, -11, 180),
         # 12 September 2026: U29 is the wall port's ESD and the packer had it in the test-point region at x 14, so the
         # pair ran 86 mm west to the diode and 96 mm back to its connector at x 109. A protection part belongs AT the
         # connector it protects (the D9 lesson of 32.73: a driver belongs at the part it drives). Beside J_USBW now,
         # ten millimetres from J_AB2, which is what makes the wall pair layable at all.
         "U29": (103, -15, 90),
         # 12 September 2026: L2's box runs to y 19.7 and CHQ's floor is 18.5, so the packer, filling from the floor,
         # put the charger's two switching-node capacitors on the inductor (two courtyard overlaps that survived every
         # region move). They are L2's own capacitors: they are placed at it, 0.45 mm clear of its courtyard.
         "C24": (-82.8, 21.8, 0), "C25": (-76.9, 21.8, 0),
         "J_DOCK": (-76, -70, 0), "J_PRE1": (-103, -70, 0), "F1": (-97, -52, 0), "J_MAINSW": (98, 75, 0),
         "U2": (-94, 56, 0), "L1": (-78, 58, 0), "U3": (-96, 12, 0), "L2": (-80, 16, 0), "U16": (-96, -26, 0), "L10": (-78, -24, 0),
         # A23: the converters south of their inductors, the rail column runs north to the connector
         "U4": (-60, 47, 0), "U5": (-44, 47, 0), "U6": (-28, 47, 0), "U7": (-12, 47, 0), "L3": (-58, 54, 0), "L4": (-42, 54, 0), "L5": (-26, 54, 0), "L6": (-10, 54, 0), "U8": (-62, 67, 0), "U9": (-46, 67, 0), "U10": (-30, 67, 0), "U11": (-14, 67, 0), "U14": (20, -4.5, 0),
         "J_5V_S1": (-51, 75, 0), "J_5V_S2": (-35, 75, 0), "J_5V_S3": (-19, 75, 0), "J_5V_DEV": (-3, 75, 0),   # A23: pin 1 (the rail) at x = inductor + 5, over the shunt's column
         "R31": (-53, 66, 90), "R35": (-37, 66, 90), "R39": (-21, 66, 90), "R43": (-5, 66, 90),   # A23: the slot shunts (inductor x + 5) stand in their rail columns between the output caps and the connector
         "R55": (4, -11.5, 0), "C65": (11, -11.5, 90), "C66": (14.5, -11.5, 90), "C67": (18, -11.5, 90),   # A23: the PA shunt R55 (the LM5176 ISNS resistor; R56 is the CS resistor) and output caps at the head of the PA band
         "Q2": (-108, 64.5, 0), "Q3": (-108, 57, 0), "C11": (-115, 64.5, 90), "C12": (-115, 59, 90),   # A23: the front end's input FETs and caps at the head of the VIN_RAW band (Q2 clear of the rod nut at (-110.5, 73))
         "Q11": (-60, -8, 0), "C63": (-54, -8, 90), "C64": (-50.5, -8, 90),   # A23: the PA stage's input FET and caps at the end of the VBAT spur
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
# 9 September 2026 (owner ruling, appendix 32.74 option 3): every declared decoupling capacitor takes its slot beside the pin it serves
# BEFORE the packer fills the regions. The old order shelf-packed them by reference number and moved afterwards only what still fitted;
# measured across the released set, not one capacitor of any board was inside the 3 mm rule and A22's worst two sat 117 and 121 mm away.
import json as _json, os as _osx, bypass_slots
_ip = _osx.path.join(_osx.path.dirname(_osx.path.abspath(BOARD)), "out", _osx.path.splitext(_osx.path.basename(BOARD))[0] + "-intent.json")
_entries = _json.load(open(_ip)).get("bypass", []) if _osx.path.exists(_ip) else []
RESERVED = set() if _osx.environ.get("BYPASS_SLOTS") == "0" else bypass_slots.reserve(board, place, lambda v: (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y)), _entries)
for _r in RESERVED: placed[_r] = board.FindFootprintByReference(_r)
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
 ("FEQ",   (-118, 46, -100, 54), ["Q4", "Q5"]),   # A23: Q2, Q3 and the input caps are FIXED at the VIN_RAW band head; the region stays clear of the rod nut   # run 11: the FETs beside the controller U2 (-94, 56), their gate drives no longer cross the support passives (FE_HDRV1 and FE_BOOT1 open in runs 6 to 10)
 # 12 September 2026: FES moves UP rather than CHQ moving down. Taking 1.5 mm off CHQ's height instead pushed its
 # output capacitors onto the FIXED inductor L2 (box y 12.3 to 19.7), which is the packer filling a shorter region
 # from its floor: two courtyard overlaps, two mask bridges and two shorting items, all of them mine.
 ("FES",   (-118, 31.5, -66, 44.5), ["R6", "R7", "R8", "R9", "R10", "C5", "C6", "C7", "C8", "C9", "C10", "R13", "R14", "R15", "R119", "C13", "C14", "C15", "TP12", "TP13", "R11", "R12", "D2"]),
 # 12 September 2026: CHQ ended at y 30.5 and FES begins at 30, so the two rectangles OVERLAPPED by half a millimetre
 # and the packer duly put the charger's CSD18510Q5B FETs (a 7.19 x 5.59 mm courtyard) under the front end's resistor row:
 # four `courtyards_overlap` on the PLACED board, before the pre-router touched it, and no gate read them until the
 # pre-route DRC (appendix 32.135). The region moves down into free board (CHS ends at y 6, PAS starts at x -66).
 ("CHQ",   (-118, 18.5, -70, 30), ["Q7", "Q8", "Q9", "Q10", "R16", "R17", "C20", "C21", "C22", "C23"]),   # C24 and C25 are FIXED at L2
 ("CHS",   (-115, -6, -70, 6), ["C16", "C17", "C18", "R18", "C19", "R19", "R20", "Q6", "R21", "R22", "R23", "R24", "R25", "C26", "C27", "R26", "R27", "TP19", "TP20", "TP22"]),
 # 12 September 2026: POQ started at x -118 and ran under NODE (-118, -68, -106, -44), a 12 x 4 mm overlap the
 # packer never happened to fill. It starts clear of the pack node's column now; 58 x 16 mm still holds its eleven parts.
 ("POQ",   (-104, -48, -46, -32), ["Q17", "Q18", "Q19", "Q20", "R71", "R72", "C81", "C82", "C83", "C84", "C85"]),
 ("POS",   (-115, -17, -70, -6), ["R66", "R67", "R68", "R69", "R70", "C75", "C76", "C77", "C78", "C79", "C80", "R73", "R74", "R75", "R121", "U17"]),
 ("R1S",   (-61, 24, -49, 44), ["C28", "C31", "C32", "C33", "R28", "R29", "R30", "R45", "R129", "C112"]),
 ("VC1",   (-66, 58, -54, 63), ["C29", "C30"]), ("VC2", (-50, 58, -38, 63), ["C35", "C36"]), ("VC3", (-34, 58, -22, 63), ["C41", "C42"]), ("VC4", (-18, 58, -6, 63), ["C47", "C48"]),
 ("R2S",   (-45, 24, -33, 44), ["C34", "C37", "C38", "C39", "R32", "R33", "R34", "R46", "R130", "C113"]),
 ("R3S",   (-29, 24, -17, 44), ["C40", "C43", "C44", "C45", "R36", "R37", "R38", "R47", "R131", "C114"]),
 ("RDS",   (-13, 24, -1, 44), ["C46", "C49", "C50", "C51", "R40", "R41", "R42", "R44", "R115", "R132", "C115"]),
 ("PAQ",   (-46, -15, -16, -2), ["Q12", "Q13", "Q14", "R56", "C54", "D3"]),   # A23: Q11, C63, C64 at the VBAT spur, C65 to C67 at the PA band
 ("PAS",   (-66, 13, -16, 20), ["R50", "R51", "R52", "R53", "R54", "C57", "C58", "C59", "C60", "C61", "C62", "R57", "R58", "R59", "R120"]),
 ("HFQ",   (-46, -48, -16, -34), ["Q15", "Q16", "Q23", "Q24", "R65", "R122"]),
 ("HFS",   (-16, -50, -2, -23), ["R60", "R61", "R62", "R63", "R64", "C68", "C69", "C70", "C71", "C72", "C73", "R123", "R124", "R125", "R126", "C74", "C108", "C109", "C110", "C111"]),
 ("B33",   (-66, -2, -48, 8), ["C52", "C53", "C55", "C56", "R48", "R49"]),
 ("CTL",   (52, -38, 90, -24), ["C4", "R2", "R3", "R4", "Q1", "R5", "R102", "C104", "R103", "R104", "R145", "C106", "C107", "R110", "R111", "R112", "R113", "R114"]),
 ("TPS",   (10, -39, 52, -23), ["TP%d" % k for k in range(3, 9)] + ["TP10", "TP11", "TP15", "TP16", "TP17", "TP18", "TP21", "TP23", "TP24", "TP25", "TP26", "TP27", "R116", "R117", "R118"]),   # U29 is FIXED beside J_USBW since 12 September 2026   # TP27: the spare ribbon line, which lost its seat on J_AB1 when the pairs took their columns (10 Sep 2026)
 ("PDS",   (0, 44, 30, 62), ["C93", "C94", "C95", "C96", "C97", "C120", "D4", "R136", "R137", "R138", "R139", "R140", "R141", "R142", "R143", "Q27"]),
 ("PDQ",   (30, 44, 84, 58), ["Q21", "Q22", "Q25", "Q26", "R81", "R127", "C92", "C116", "C117", "C118", "C119", "R76", "R77", "R78", "R79", "R80", "C86", "C87", "C88", "C89", "C90", "C91", "R128", "R133", "R134", "R135"]),
 ("EFS",   (84, 44, 100, 62), ["C98", "R90", "R91", "R92", "R93", "C99", "C100", "R94", "R95", "R96", "R97", "C101", "C102", "R98", "R99", "R100", "R101", "C103"]),
]
GAP = 1.2                      # between any two packed parts (was 0.7: fine-pitch ICs ended wall to wall with passives)
FINE_MARGIN = float(_os.environ.get("PLACE_FINE_MARGIN", "1.6"))   # extra all round a fine-pitch IC so every side keeps a via lane for its escapes; a knob since 10 Sep 2026, when 1.6 to 2.6 on B19 took the pads with no escape at all from 194 to 69
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
REGIONS = [(_n, _rect, [_r for _r in _refs if _r not in RESERVED]) for _n, _rect, _refs in REGIONS]   # a reserved capacitor is placed already
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
plane(pcbnew.In4_Cu, "GND", "GND plane In4")   # A22 six layers (7 Sep 2026 10:10, appendix 32.61): In4 a second solid ground under B.Cu, In2 and In3 routable; four-layer runs left 4 to 11 opens in the converter zones
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
for L, nm in ((pcbnew.In4_Cu, "In4 solid ground: no tracks"),):   # the same rule for In4 (six layers)
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayer(L); z.SetZoneName(nm); o = z.Outline(); o.NewOutline()
    for x, y in ((-119, -79), (119, -79), (119, 79), (-119, 79)): p = P(x, y); o.Append(p.x, p.y)
    board.Add(z)
# --- A23 power copper (MESHSAT-862 rule 3, 8 Sep 2026): every rail's current in locked copper built from the placed pads; judged by dc_drop.py on the filled board
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from power_copper import PowerCopper
PC = PowerCopper(board, net_for, P)
def case_xy(pos): return pos.x / 1e6 - OX, OY - pos.y / 1e6
def net_pads(net, refs):
    out = []
    for r in refs:
        fp = placed.get(r)
        if fp is None: print("WARNING power copper: %s not placed" % r); continue
        for pd in fp.Pads():
            if pd.GetNetname() in (net, "/" + net): out.append(pd)
    if not out: raise SystemExit("power copper: no pad of %s on %s" % (net, refs))
    return out
def pads_rect(pads, gx, gy=None):
    gy = gx if gy is None else gy; xs, ys = [], []
    for pd in pads:
        bb = pd.GetBoundingBox(); xs += [bb.GetLeft() / 1e6 - OX, bb.GetRight() / 1e6 - OX]; ys += [OY - bb.GetBottom() / 1e6, OY - bb.GetTop() / 1e6]
    return (min(xs) - gx, min(ys) - gy, max(xs) + gx, max(ys) + gy)
def rect_pts(r): return [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
def row(net, x0, x1, y, n=3): PC.stitch(net, [(x0 + (x1 - x0) * k / (n - 1) if n > 1 else (x0 + x1) / 2, y) for k in range(n)])
def col(net, x, y0, y1, n=3): PC.stitch(net, [(x, y0 + (y1 - y0) * k / (n - 1) if n > 1 else (y0 + y1) / 2) for k in range(n)])
# 1. the four slot rails: converter output island (inductor OUT pad, output caps, shunt pad 1) with a bottom band; the rail after the shunt (shunt pad 2, connector pin 1) the same
SLOT_CAPS = {"1": ["C29", "C30"], "2": ["C35", "C36"], "3": ["C41", "C42"], "D": ["C47", "C48"]}
SLOT = [("1", -58, "L3", "R31", "J_5V_S1", "+5V_S1"), ("2", -42, "L4", "R35", "J_5V_S2", "+5V_S2"), ("3", -26, "L5", "R39", "J_5V_S3", "+5V_S3"), ("D", -10, "L6", "R43", "J_5V_DEV", "+5V_DEV")]
for n, xL, Lr, Rr, Jr, out in SLOT:
    so = "S%s_OUT" % n
    net_pads(so, [Lr, Rr] + SLOT_CAPS[n])                                   # the parts exist and carry the net (a refusal otherwise)
    ir = (xL - 8.7, 50.5, xL + 6.8, 64.9)                                    # the converter output: inductor, output caps, the shunt's pad 1; below the INA226's pin row (65.5)
    PC.island(so, "S%s output" % n, rect_pts(ir), pcbnew.F_Cu, priority=3)
    PC.band(so, "S%s output" % n, (xL + 1.5, 50.5, xL + 6.8, 64.9), (pcbnew.B_Cu,), priority=2)
    row(so, xL + 2.0, xL + 6.2, 58.2, 4)                                     # between the inductor's north edge (57) and the caps' first row (59.3)
    col(so, xL + 3.0, 60.0, 62.0, 2)                                         # beside the shunt's pad 1, east of the caps (to xL + 0.8)
    orr = pads_rect(net_pads(out, [Rr, Jr]), 2.6, 1.0)                       # the rail: shunt pad 2 and the connector's rail pin
    PC.island(out, "%s rail" % out, rect_pts(orr), pcbnew.F_Cu, priority=3)
    PC.band(out, "%s rail" % out, orr, (pcbnew.B_Cu,), priority=2)
    row(out, xL + 3.1, xL + 6.5, 72.6, 3)                                    # under the connector body, 2.4 mm from its pins
# 2. the PA rail: the shunt's pad 2 and the output caps in an island at the head of a 4.5 mm bottom band east along y -11.5, north at x 104, into J_PA's pin 1
pa = "+13V8_PA"; pr = pads_rect(net_pads(pa, ["R55", "C65", "C66", "C67"]), 1.2, 1.0)
PC.island(pa, "PA rail head", rect_pts((pr[0], pr[1], pr[2] + 2.5, pr[3])), pcbnew.F_Cu, priority=3)
jp = pads_rect(net_pads(pa, ["J_PA"]), 0); yP = (jp[1] + jp[3]) / 2
PC.union(pa, "PA rail", [(pr[2] - 0.5, -13.75, 106.25, -9.25), (101.75, -13.75, 106.25, yP + 2.25), (101.75, yP - 2.25, jp[2] + 0.8, yP + 2.25)], pcbnew.B_Cu, priority=2)   # one polygon: east, north, pin
col(pa, pr[2] + 1.3, -12.6, -10.4, 2)                                         # two vias in the head island, in the band
# 3. VIN_RAW: from the dock pins north, west along y -43, north along the west edge into the front end's input FETs and caps
vr = "VIN_RAW"; vb = "VBAT"; jd = pads_rect(net_pads(vr, ["J_DOCK"]), 0.5)
fe = pads_rect(net_pads(vr, ["Q2", "Q3", "C11", "C12"]), 1.0)
PC.island(vr, "VIN_RAW head", rect_pts((min(fe[0], -118), fe[1] - 2.6, fe[2], fe[3])), pcbnew.F_Cu, priority=3)
# the west run crosses the VBAT trunk (x fx0 to fx1): two bands of different nets never cross on one layer (32.39), so VIN_RAW dives to In3 under the trunk on five vias a side;
# each side of the dive is ONE polygon (the dock riser with the east run, the west run with the west riser): abutting same-net zones with priorities read as separate pieces (32.69)
f1_ = pads_rect(net_pads(vb, ["F1"]), 0.5); f1c_ = (f1_[0] + f1_[2]) / 2; fx0_, fx1_ = f1c_ - 4.5, f1c_ + 0.5   # the trunk on the west half of F1's pad 2, clear of the dock pins' riser
# the dock header's second row (GND, SHORE_INHIBIT, the E6 USB pair) sits between the VIN_RAW row and the band: the riser through it fills as two pieces
# (the mesh of 8 Sep 2026 12:35: "7 of 7 load pads not connected", the router's 0.4 mm In2 track was the only bridge, 3.1 percent), so the copper goes round the row's
# west end: 2 mm of copper south of the VIN_RAW row, the passage between J_CP4 and pin 1, and the field west of the header up to the CELL+ node bar, on B.Cu, F.Cu and In3
cp4 = pads_rect(net_pads("CELL+", ["J_CP4"]), 0.5); jd_s = jd[1] - 2.0
dock = [(jd[0], jd_s, jd[2], -40), (fx1_ + 0.8, -46, jd[2], -40), (fx1_ + 0.8, -69.7, jd[0] + 0.1, -40), (cp4[2], jd_s, jd[0] + 0.1, -69.6)]
# the keep-out goes on the two band runs only, never on the two rectangles that wrap the header (8 Sep 2026 17:15: with a track
# keep-out over them the header's second row, GND, SHORE_INHIBIT and the E6 USB pair, had no layer to escape on and the router
# ran out its two and four hour limits without writing a session, twice; the keep-out exists to stop a track cutting the band)
PC.union(vr, "VIN_RAW east", dock, pcbnew.B_Cu, priority=4, keepout=False)   # from the four dock pins themselves (a band that missed them left the link to a 0.4 mm In2 track: 667 A/mm2, 32.69); priority 4 over the VBAT plane's corner
for _r in dock[:2]: PC.keepout("keep tracks off VIN_RAW east", _r, pcbnew.B_Cu)
PC.union(vr, "VIN_RAW dock top", dock, pcbnew.F_Cu, priority=4, keepout=False, min_width=0.25, clearance=0.15)   # no track keep-out on top: the header's signal pins escape there
PC.union(vr, "VIN_RAW west", [(-118, -46, fx0_ - 0.8, -40), (-118, -46, -112, fe[1] - 0.4)], pcbnew.B_Cu, priority=3)
PC.union(vr, "VIN_RAW under the trunk", [(fx0_ - 5.0, -46.5, fx1_ + 5.0, -39.5)] + dock, pcbnew.In3_Cu, priority=2, keepout=False)   # one In3 polygon from the dive to the dock pins (the pins join the layers)
PC.keepout("keep tracks off VIN_RAW under the trunk", (fx0_ - 5.0, -46.5, fx1_ + 5.0, -39.5), pcbnew.In3_Cu)
for _r in dock[:2]: PC.keepout("keep tracks off VIN_RAW east", _r, pcbnew.In3_Cu)
col(vr, fx0_ - 3.2, -45.2, -40.8, 3); col(vr, fx0_ - 1.9, -44.6, -41.4, 2); col(vr, fx1_ + 3.2, -45.2, -40.8, 3); col(vr, fx1_ + 1.9, -44.6, -41.4, 2)
row(vr, -117, -113, fe[1] - 1.3, 3)
# 4. VBAT: a bottom trunk from F1's pad 2 north to a collector at y 41 under the four slot converters (islands at their VIN pins), and a spur to the PA stage's input FET and caps
f1 = f1_; fx0, fx1 = fx0_, fx1_
PC.union(vb, "VBAT", [(fx0, f1[1], fx1, 44.5), (fx0, 38.5, -4, 44.5), (fx0, -12.5, -48, -7.5)], pcbnew.B_Cu, priority=2)   # one comb: the trunk from F1, the collector under the converters, the PA spur
for n, xL, Lr, Rr, Jr, out in SLOT:
    ur = pads_rect(net_pads(vb, ["U%d" % {"1": 4, "2": 5, "3": 6, "D": 7}[n]]), 0.5, 0.5)   # the converter's VIN pin (pin 2, west side)
    # an L: a via column west of the pin row (the other pins would slice a rectangle to 48 percent fill, 32.69) and a finger into the pin's pad
    PC.island(vb, "VBAT in S%s" % n, [(ur[0] - 2.6, 40.0), (ur[0] - 0.6, 40.0), (ur[0] - 0.6, ur[1]), (ur[2], ur[1]), (ur[2], ur[3]), (ur[0] - 2.6, ur[3])], pcbnew.F_Cu, priority=3)
    col(vb, ur[0] - 1.6, 41.0, 43.6, 3)
qr = pads_rect(net_pads(vb, ["Q11", "C63", "C64"]), 1.0)
PC.island(vb, "VBAT PA head", rect_pts((qr[0] - 3.5, min(qr[1], -12.0), qr[2], qr[3])), pcbnew.F_Cu, priority=3)
col(vb, qr[0] - 1.9, -11.6, -8.4, 2)
# every pad of a rail net joins its pour solid (no thermal spokes): a through-hole pin's four spokes are the neck of an 8 A path, and the mesh judge sees them as no connection
RAIL_NETS = {"VBAT", "CELL+", "VIN_RAW", "+5V_S1", "+5V_S2", "+5V_S3", "+5V_DEV", "+13V8_PA", "S1_OUT", "S2_OUT", "S3_OUT", "SD_OUT"}
_solid = 0
for fp in board.GetFootprints():
    for pd in fp.Pads():
        if pd.GetNetname().lstrip("/") in RAIL_NETS: pd.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL); _solid += 1
print("A23 power copper: %d zones and keep-outs; %d rail pads joined solid" % (len(PC.made), _solid))
# --- net classes (API first; the project JSON is re-applied after the save because SaveBoard rewrites it)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr, dpw, dpg):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr)); nc.SetDiffPairWidth(FromMM(dpw)); nc.SetDiffPairGap(FromMM(dpg)); nc.SetDiffPairViaGap(FromMM(0.25))
cls(ns.GetDefaultNetclass(), 0.127, 0.25, 0.7, 0.3, 0.2, 0.15)
# clearances at the board minimum (7 Sep 2026: with the explicit net-class assignments the DRC enforces them, and a class clearance above a fine-pitch pad gap of 0.2 fails inside the LM5176 and TPS23861 pads); HV 0.18 for the 54 V nodes
CLASSES = {"USB": (0.127, 0.127, 0.7, 0.3, 0.127, 0.13),   # 8 Sep 2026 (32.71): 0.127/0.127 on the 3313 outer layer computes 94 ohm; the pairs run on F.Cu and B.Cu over the In1 and In4 grounds; clearance 0.10 so the gap keeps a margin
            "PWR": (0.127, 0.4, 0.8, 0.4, 0.4, 0.25), "NODE": (0.127, 0.5, 0.8, 0.4, 0.5, 0.25), "SW": (0.127, 0.5, 1.0, 0.5, 0.8, 0.3), "RAIL": (0.127, 0.4, 1.0, 0.5, 0.5, 0.3), "RF": (0.18, 0.35, 0.7, 0.3, 0.2, 0.15), "HV": (0.18, 0.4, 0.8, 0.4, 0.4, 0.25)}
PATTERNS = [("USB_*", "USB"), ("PD_CC*", "USB"), ("CELL+", "NODE"), ("VBAT", "NODE"), ("PRECHG", "PWR"), ("VIN_RAW", "NODE"), ("VBUS20", "NODE"), ("CH_ACN", "NODE"), ("CH_SRP", "NODE"), ("CH_SW*", "SW"), ("FE_SW*", "SW"), ("FE_OUT", "NODE"), ("FE_CS", "SW"),
            ("PA_SW*", "SW"), ("PA_OUT", "NODE"), ("PA_CS", "SW"), ("HF_SW*", "SW"), ("HF_OUT", "PWR"), ("PD_SW*", "SW"), ("PD_OUT", "PWR"), ("PD_PPHV", "PWR"), ("PD_VBUS", "PWR"), ("S?_SW", "SW"), ("SD_SW", "SW"), ("S?_OUT", "RAIL"), ("SD_OUT", "RAIL"), ("PD_VPWR", "PWR"), ("PD_SW", "PWR"),
            ("+5V_*", "RAIL"), ("+13V8_PA", "RAIL"), ("+12V_HF", "RAIL"), ("VMON", "PWR"), ("VHEAT", "PWR"), ("GND", "PWR"), ("+3V3", "PWR"), ("B33_SW", "SW"), ("RF_*", "RF"), ("POE_SW*", "HV"), ("POE_OUT", "HV"), ("+54V_POE", "HV"), ("POE_CS", "SW")]
# A net class clearance below the board minimum is not a tighter rule, it is a rule that never applies: KiCad enforces the board minimum as a
# floor, the router takes the class value from the DSN, and every pair it lays at that spacing is a violation. A23's route came back with 25
# clearance violations reading "board minimum clearance 0.1270 mm; actual 0.1017 mm", all of them between the two legs of a pair, because the
# USB class said 0.10 (9 Sep 2026 02:10, MESHSAT-862). Refuse it here instead of discovering it after three hours of routing.
_minclr = board.GetDesignSettings().m_MinClearance / 1e6
_bad = {n: v[0] for n, v in CLASSES.items() if v[0] < _minclr - 1e-9}
if _bad: raise SystemExit("net class clearance below the board minimum %.3f mm: %s (KiCad enforces the minimum, so the class value is a lie the router believes)" % (_minclr, _bad))
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
