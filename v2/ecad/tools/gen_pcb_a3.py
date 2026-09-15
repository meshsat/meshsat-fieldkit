#!/usr/bin/env python3
"""PCB-A phase A23 (MESHSAT-862 rule 3, 8 Sep 2026; A22 of MESHSAT-830 before it): bring the schematic netlist into the mechanical board of gen_pcb_a.py,
and lay every rail's current in locked copper (islands, bottom bands, stitch vias) built from the placed pads, judged by dc_drop.py (appendix 32.67, 32.69).
Usage: gen_pcb_b3.py <board.kicad_pcb> <netlist.net>
- reuses footprints already on the board by reference (J_GPIO1, J_RTL1, J_ZB1, J_DCF77)
- places connectors at planned case-frame positions, small parts packed into regions near their connectors
- creates nets, assigns pads, adds GND (In1) and +5V (In2) planes, saves
"""
import sys, re, math, os, pcbnew   # os: `regionfit.record(..., stem=os.path...)` at the region loop uses it, 250 lines before the `import json, os` further down (13 September 2026)
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
import regionfit
regionfit.allowance('a')
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
    regionfit.record(name, (x0, y0, x1, y1), False, len(refs), stem=os.path.splitext(os.path.basename(BOARD))[0])
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
    if cy - rowh < y0 - 0.01: regionfit.note(name, y0 - (cy - rowh))
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
NL_CU = board.GetCopperLayerCount()
if NL_CU >= 6:
    plane(pcbnew.In4_Cu, "GND", "GND plane In4")   # A22 six layers (7 Sep 2026 10:10, appendix 32.61): In4 a second solid ground under B.Cu, In2 and In3 routable; four-layer runs left 4 to 11 opens in the converter zones
# 15 September 2026, MEASURED ON A30's CLOSED BOARD (32.191): the plane's south edge stood at y -44 and F1's pad
# a few millimetres south of it, so the pack's current climbed a 0.500 mm In2 router track from the fuse into
# the plane (ratio 2.25) in parallel with the B.Cu trunk, because that track is the shorter path. The plane
# reaches the fuse now; the rail meets its plane where it is made, and a via field north of that is a second
# route rather than the only one.
plane(pcbnew.In2_Cu, "VBAT", "VBAT plane In2 (west and middle columns)", rect=(-117.5, -48.5, -2, 77.5))
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
for L, nm in ((((pcbnew.In4_Cu, "In4 solid ground: no tracks"),) if NL_CU >= 6 else ())):   # the same rule for In4, which a four-layer board does not have
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
def free_run(x0, x1, y0, y1, net, clear=0.55, want=1.0):
    """The longest stretch of [y0, y1] where the strip x0..x1 carries no pad of ANOTHER net within `clear` mm.

    14 September 2026. The first VBAT via field was written at a y this file could not see was occupied: the
    trunk runs north past U16, the PoE controller, and Q18, and fifteen through vias landed on their pads for
    thirteen hard violations before the pre-router ever ran. A via field belongs where the band is clear, and
    which stretch that is, is a fact about the placed board rather than a number to type. Returns (y, y) of the
    longest free run, or None when nothing of `want` mm is free."""
    bad = []
    for fp in board.GetFootprints():
        for pd in fp.Pads():
            if pd.GetNetname() == net or (pd.GetNetname() or "").lstrip("/") == net.lstrip("/"): continue
            bb = pd.GetBoundingBox()
            px0, px1 = bb.GetLeft() / 1e6 - OX, bb.GetRight() / 1e6 - OX
            py0, py1 = OY - bb.GetBottom() / 1e6, OY - bb.GetTop() / 1e6
            if px1 + clear < x0 or px0 - clear > x1: continue
            bad.append((py0 - clear, py1 + clear))
    bad.sort(); best = None; cur = y0
    for b0, b1 in bad + [(y1, y1)]:
        if b0 > cur and (best is None or b0 - cur > best[1] - best[0]): best = (cur, min(b0, y1))
        cur = max(cur, b1)
        if cur >= y1: break
    if cur < y1 and (best is None or y1 - cur > best[1] - best[0]): best = (cur, y1)
    return best if best and best[1] - best[0] >= want else None
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
PC.keepout("keep tracks off the PA rail head", (pr[0], pr[1], pr[2] + 2.5, pr[3]), pcbnew.F_Cu)   # 15 Sep 2026 (A34): router tracks across the head left its fill at 51 of 102 mm2, under the gate's half
jp = pads_rect(net_pads(pa, ["J_PA"]), 0); yP = (jp[1] + jp[3]) / 2
# 13 September 2026: the east run was 4.5 mm, which IPC gives 7.12 A against this rail's 6.0, and the cell
# measure still read 175.5 A/mm2 at (93.2, -12.2) with nothing of another net within 2.8 mm: the current is
# not spread across the band, it hugs one edge between the head island and the turn. It is 7.0 mm now, and
# the head island gains a third stitch via so the current enters the band over a front rather than at a
# point (32.164: a cell at a via is a funnel). A via further along the run would stand on B.Cu alone, and
# `cleanup_dangling` removes a via whose other end touches nothing.
# 13 September 2026, A25 MEASURED: THE BAND STARTED 15 mm EAST OF THE HEAD IT FEEDS. The B.Cu band began at
# the head island's east end, so the rail's first 15 mm ran on the F.Cu island alone, the router's tracks cut
# that island into two pieces, and the worst pour cell read 132.5 A/mm2 against 82.7 at (167.2, 121.2), ratio
# 1.60, with 3.68 A through one 0.40 mm barrel behind it. B.Cu under the head is empty for 50 mm in every
# direction (drawn and read, not assumed), so the band starts at the shunt's own output pad instead, and two
# vias IN that pad put the rail on 35 um copper at the point it is made. It is the VBUS20 pattern of this
# morning, and the reason it is right here too: a rail should meet its outer copper at its source.
_r55 = pads_rect(net_pads(pa, ["R55"]), 0)                                    # the shunt's output pad: the rail's source
# 14 September 2026, MEASURED ON A28: THE CURRENT CROWDS THE INSIDE OF THE TURN. The east run is 7 mm and
# the north run 4.5, and where they meet the worst pour cell reads 128 A/mm2 against 82.7 (ratio 1.54) at
# (95.2, -9.7), which is the inside corner. A right-angled turn in a band is a neck whatever the two widths
# are, because the shortest path hugs the inside of it; the chamfer block below is 2.5 by 4 mm of copper on
# that corner and it costs nothing anywhere else.
PC.union(pa, "PA rail", [(_r55[0] - 1.0, -15.0, 106.25, -8.0), (101.75, -15.0, 106.25, yP + 2.25), (101.75, yP - 2.25, jp[2] + 0.8, yP + 2.25),
                         (99.25, -15.0, 101.75, -11.0),
                         (jp[0] - 3.0, yP - 4.5, jp[2] + 0.8, yP + 4.5),
                         (85.0, -22.0, 106.25, -15.0)], pcbnew.B_Cu, priority=2)   # 15 Sep 2026, A33 measured: J_AB2's ten through-hole pins stand IN the east run at x 93 to 96, y -6 to -14, and the run's worst cell (ratio 1.61, unchanged by the foot at the pin) is what they leave of it; the run doubles south of them   # one polygon: east, north, pin, the chamfer on the turn, and a foot at the pin (15 Sep 2026: the run's end at J_PA read ratio 1.61)
col(pa, (_r55[0] + _r55[2]) / 2, (_r55[1] + _r55[3]) / 2 - 1.1, (_r55[1] + _r55[3]) / 2 + 1.1, 2)   # in the shunt's own pad
col(pa, pr[2] + 1.3, -13.4, -9.6, 3)                                          # three vias in the head island, in the band: a via mid-run has no F.Cu copper at its other end and cleanup_dangling would take it
# 3. VIN_RAW: from the dock pins north, west along y -43, north along the west edge into the front end's input FETs and caps
# THE DIVE'S LAYER FOLLOWS THE BOARD (12 September 2026, owner ruling 2: test board A at four layers against six).
# It was the literal In3, which a four-layer A does not have, so a four-layer A could not be GENERATED at all and
# the one layer experiment the P0 asked for had never been run. On six layers In1 and In4 are the solid grounds and
# In2 and In3 route, so the dive takes In3; on four, In1 is the ground by the owner's ruling of 5 September 17:08
# and In2 is the one routing layer left, so the dive takes In2. Reading the count is not setting it: the count is
# on the never-auto floor and stays where gen_pcb_a.py declares it.
DIVE_CU = pcbnew.In3_Cu if board.GetCopperLayerCount() >= 6 else pcbnew.In2_Cu
print("placement: the VIN_RAW dive goes on %s (%d copper layers)" % (board.GetLayerName(DIVE_CU), board.GetCopperLayerCount()))
vr = "VIN_RAW"; vb = "VBAT"; jd = pads_rect(net_pads(vr, ["J_DOCK"]), 0.5)
fe = pads_rect(net_pads(vr, ["Q2", "Q3", "C11", "C12"]), 1.0)
PC.island(vr, "VIN_RAW head", rect_pts((min(fe[0], -118), fe[1] - 4.0, fe[2], fe[3])), pcbnew.F_Cu, priority=3)   # 4.0 north since 15 Sep 2026: the 8 A squeezed along the head's north edge past a foreign pad, ratio 2.69 (32.193)
# 15 September 2026, A33 MEASURED: the head's worst cell (ratio 2.70) sits WEST of Q2's three FE_SW1 pins: the 8 A that
# arrives from the west band's vias had to pass that pin column on F.Cu to reach Q2's drain tab (pad 5, VIN_RAW, 3.8 by
# 3.9 mm). The west band on B.Cu already runs under the tab, so four vias in the tab hand the current up where it is used
# and the F.Cu throat carries only what the capacitors take. Growing the island (4.0 mm, A33) moved nothing.
_q2 = pads_rect(net_pads(vr, ["Q2"]), 0); _q2x, _q2y = (_q2[0] + _q2[2]) / 2, (_q2[1] + _q2[3]) / 2
col(vr, _q2x - 0.8, _q2y - 0.8, _q2y + 0.8, 2); col(vr, _q2x + 0.8, _q2y - 0.8, _q2y + 0.8, 2)   # in the FET's own drain tab
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
# 13 September 2026, A25 MEASURED: the west band stopped at the head island's south edge, so the head, which
# is where 8 A enters the board from the dock, had one layer of copper and the front end's own FE_SW1 escape
# 0.34 mm from it. The worst pour cell read 134.6 A/mm2 against 52.0 there (ratio 2.59). B.Cu under the head
# carries three foreign vias and nothing else, so the band covers the head as well and a second via row joins
# them at the north end, where the neck is: one row at the south edge was the whole join.
_head = (min(fe[0], -118), fe[1] - 2.6, fe[2], fe[3])
PC.union(vr, "VIN_RAW west", [(-118, -46, fx0_ - 0.8, -40), (-118, -46, -112, fe[1] - 0.4), _head], pcbnew.B_Cu, priority=3)
PC.union(vr, "VIN_RAW under the trunk", [(fx0_ - 5.0, -46.5, fx1_ + 5.0, -39.5)] + dock, DIVE_CU, priority=2, keepout=False)   # one In3 polygon from the dive to the dock pins (the pins join the layers)
PC.keepout("keep tracks off VIN_RAW under the trunk", (fx0_ - 5.0, -46.5, fx1_ + 5.0, -39.5), DIVE_CU)
for _r in dock[:2]: PC.keepout("keep tracks off VIN_RAW east", _r, DIVE_CU)
col(vr, fx0_ - 3.2, -45.2, -40.8, 3); col(vr, fx0_ - 1.9, -44.6, -41.4, 2); col(vr, fx1_ + 3.2, -45.2, -40.8, 3); col(vr, fx1_ + 1.9, -44.6, -41.4, 2)
# 14 September 2026, MEASURED ON A28: three vias a row is 3.3 A against this rail's 8. The worst via on the
# board carries 3.25 A through one 0.40 mm barrel at (-113.0, 64.7), which IPC rates at 1.11, and the worst
# pour cell sits a millimetre from it at 171 A/mm2 against 82.7 (ratio 2.06): a cell at a via is a funnel,
# and this one funnels the whole head. Six a row is 6.7 A each and the two rows together carry the rail.
# 15 September 2026 (32.191): the router bridged the head to the front-end FET's escape via with an 8.7 mm
# 0.500 mm track ON In2, which at that place is the VBAT plane. One track, two rails hurt: VIN_RAW at ratio
# 2.54 in it, and a cut through VBAT's plane. The head's footprint on In2 is closed to tracks; the FET escapes
# land on In3 or B.Cu, where VIN_RAW's own copper is.
PC.keepout("keep tracks off the VBAT In2 plane under the VIN_RAW head", (fe[0] - 2.0, fe[1] - 2.0, fe[2] + 2.0, fe[3] + 2.0), pcbnew.In2_Cu)
row(vr, -117.5, -112.5, fe[1] - 1.3, 6)
row(vr, -116.0, -110.0, fe[3] - 3.0, 6)                                        # the head's north end, where the cell measure put the neck
# 4. VBAT: a bottom trunk from F1's pad 2 north to a collector at y 41 under the four slot converters (islands at their VIN pins), and a spur to the PA stage's input FET and caps
f1 = f1_; fx0, fx1 = fx0_, fx1_
# 13 September 2026, MEASURED ON A26: THE COMB FILLS IN TWO PIECES AND THE CUT IS A VIA COLUMN. The trunk
# fills from F1 north to y 100.5 and the collector from y 95.5 south, and in the five millimetres between
# them stands the charger's east escape column: seven 0.45 mm vias at x 57.5 to 57.8 from y 95.6 to 100.4
# (/CELL+, /CH_SRP twice, /CH_SW2, /CH_CELL, /CH_COMP2, /CH_HIDRV2). A 5 mm band cannot pass a via column
# standing in it, so the pack's 10 A went round through the In2 plane and, for 3.29 A of it, through a
# 0.500 mm In3 router track. B.Cu east of that column is EMPTY from x 58 to 70 and y 92 to 104 (measured,
# not assumed), so the comb takes a bay out there and walks round the column on solid copper.
PC.union(vb, "VBAT", [(fx0, f1[1], fx1, 44.5), (fx0, 38.5, -4, 44.5), (fx0, -12.5, -48, -7.5),
                      (fx1 - 0.5, 5.0, fx1 + 5.5, 19.0)], pcbnew.B_Cu, priority=2)   # one comb: the trunk from F1, the collector under the converters, the PA spur, the bay past the charger's via column
# 14 September 2026, MEASURED ON A28: THE TRUNK AND THE PLANE ARE THE SAME RAIL AND NOTHING JOINED THEM AT
# THE SOURCE. The B.Cu trunk runs north from F1's pad and the In2 plane covers the same ground from y -44, and
# the only vias between them were the three at each converter island at y 41 to 43.6, eighty millimetres north.
# So the pack's 10 A arrived on B.Cu at F1, and the 51 percent of it the In2 plane carries had to get there
# through whatever the router laid: a 0.500 mm In2 track at (-96.7, -42.6) carrying 1.17 A against IPC's 0.40
# (ratio 2.96) and a single 0.25 mm via at (-95.5, -37.3) carrying 1.57 A against 0.79. Fifteen 0.8/0.4 vias
# across the trunk's full five millimetres hand the rail over on a front instead: IPC gives a 0.4 mm barrel
# 1.11 A, so the field is rated 16 A against the 5 the plane takes. They sit north of y -39.5, clear of the
# VIN_RAW dive's In3 polygon under the trunk, which a through via would otherwise stand in.
_vfield = free_run(fx0 + 0.6, fx1 - 0.6, -38.0, 38.0, vb, want=4.0)
if _vfield:
    _fy0, _fy1 = _vfield[0] + 0.8, _vfield[1] - 0.8
    if _fy1 - _fy0 > 12.0: _fy1 = _fy0 + 12.0
    _fn = max(2, min(5, int((_fy1 - _fy0) / 2.0) + 1))
    for _dx in (0.9, 2.5, 4.1): col(vb, fx0 + _dx, _fy0, _fy1, _fn)
    print("placement: VBAT hands the trunk to the In2 plane at y %.1f to %.1f, %d vias in 3 columns" % (_fy0, _fy1, 3 * _fn))
else:
    print("placement: VBAT found no clear stretch of its trunk for the hand-over vias; the plane keeps the router's")
for n, xL, Lr, Rr, Jr, out in SLOT:
    ur = pads_rect(net_pads(vb, ["U%d" % {"1": 4, "2": 5, "3": 6, "D": 7}[n]]), 0.5, 0.5)   # the converter's VIN pin (pin 2, west side)
    # an L: a via column west of the pin row (the other pins would slice a rectangle to 48 percent fill, 32.69) and a finger into the pin's pad
    PC.island(vb, "VBAT in S%s" % n, [(ur[0] - 2.6, 40.0), (ur[0] - 0.6, 40.0), (ur[0] - 0.6, ur[1]), (ur[2], ur[1]), (ur[2], ur[3]), (ur[0] - 2.6, ur[3])], pcbnew.F_Cu, priority=3)
    # 14 September 2026, MEASURED TWICE AND TAKEN BACK: a track keep-out on the island's via column. The SD island
    # fills 10.7 of 22 mm2 on A30 with 65 mm of other nets' track through it and the gate refuses the board at
    # exactly 50 percent, so the column got the keep-out every band carries. A31 routed the same copper with
    # it: 14 unrouted against A30's 8, the stub router took back all ten of its closures, the finish ended at
    # 13 against A30's 3. Four two-millimetre walls beside the converters' pin rows cost the router six
    # connections and the finish ten. The island keeps its shape and no wall; a coverage bar that a routing
    # channel through an island trips is answered at the island, not by forbidding the channel.
    col(vb, ur[0] - 1.6, 41.0, 43.6, 3)
# THE In2 PLANE IS A CONDUCTOR AND THE ROUTER WAS CUTTING IT (13 September 2026, appendix 32.164). VBAT's
# worst cell read 428 A/mm2 against 52 at (-58.3, 0.8) in the case frame, with `+3V3` 0.62 mm away and
# `/PA_HDRV1` 1.01 mm away: two signal tracks the router laid ACROSS the plane, leaving an isthmus about
# 1.5 mm wide, which IPC gives 1.02 A, carrying about 3.7 A. This board's own rule since 32.39 is that every
# band carries a track keep-out on its layer with vias allowed, and the plane that carries 51 percent of a
# 10 A rail had none. The keep-out is the neighbourhood of the neck rather than the whole plane, because an
# In1 keep-out over a whole layer left A19 with 83 unrouted nets and that lesson is in section 8.
PC.keepout("keep tracks off the VBAT In2 plane at the neck", (-70.0, -11.0, -46.0, 13.0), pcbnew.In2_Cu)
# 15 September 2026 (32.193): the four converters' VIN islands sit east of the In2 plane's edge at x -2, so the pack's
# current reached them through the plane's corner and the router's tracks. A tongue of the plane under the converter
# row, above the GND plane there (In1 and In4 carry the return), puts the islands' via columns on the plane itself.
_urs = [pads_rect(net_pads(vb, ["U%d" % k]), 0.5, 0.5) for k in (4, 5, 6, 7)]
# 15 September 2026, A33 MEASURED: with the tongues in place VBAT's worst pour cell moved to (60.2, 55.7), which is the In2
# plane threading U2's escape-via fan (the front-end controller's east pin column at x 58.9, 0.65 mm pitch): 0.5 oz copper
# between vias carrying what the B.Cu collector beside it should. The plane keeps off U2's fan on In2, tracks and vias
# untouched, so the rail takes the band there and the plane resumes past the fan.
_u2b = board.FindFootprintByReference("U2").GetBoundingBox(); _u2a, _u2c = case_xy(pcbnew.VECTOR2I(_u2b.GetLeft(), _u2b.GetBottom())), case_xy(pcbnew.VECTOR2I(_u2b.GetRight(), _u2b.GetTop()))
PC.nopour("VBAT plane keeps off U2's escape fan", (_u2a[0] - 2.5, _u2a[1] - 2.5, _u2c[0] + 2.5, _u2c[1] + 2.5), pcbnew.In2_Cu)
plane(pcbnew.In2_Cu, "VBAT", "VBAT plane In2 (tongue under the converter row)", rect=(-2.5, 36.0, max(u[2] for u in _urs) + 2.0, min(77.5, max(u[3] for u in _urs) + 3.0)), priority=2)
qr = pads_rect(net_pads(vb, ["Q11", "C63", "C64"]), 1.0)
PC.island(vb, "VBAT PA head", rect_pts((qr[0] - 3.5, min(qr[1], -12.0), qr[2], qr[3])), pcbnew.F_Cu, priority=3)
# 15 September 2026, A32 MEASURED (32.193): VBAT's worst pour cell sits at the In2 plane's EAST EDGE at (-8.8, -25.3),
# ratio 1.42, because the PA head's vias stand just inside x -2 and the whole 6 A of the PA converter's input funnels
# through the plane's corner to reach them. In2 east of -2 is a GND plane on a board whose In1 and In4 are solid
# ground; a VBAT tongue at a higher priority takes the strip under the PA head, so the rail meets its head on a front.
if qr[2] > -4.0:
    plane(pcbnew.In2_Cu, "VBAT", "VBAT plane In2 (tongue under the PA head)", rect=(-2.5, min(qr[1], -12.0) - 3.0, qr[2] + 1.0, qr[3] + 3.0), priority=2)
col(vb, qr[0] - 1.9, -11.6, -8.4, 2)
# 5. VBUS20, the 20 V charge bus: IT HAD NO POWER COPPER (13 September 2026, appendix 32.164). The router
# carried 4.91 A of its 6 on a 0.500 mm F.Cu track for 11.8 mm, ratio 3.39 against IPC, on a dog-leg west to
# the feedback divider and back. The stage's output is R11's pad 2 (the ISNS shunt, not the controller U2:
# naming U2 as the rail's source is what put 2.90 A through a 0.200 mm sense escape in the measurement
# before this one). From R11 the current goes through the three output capacitors to R16, the charger's
# input-current shunt. An island over those pads with a band of the same rectangle under it, which is the
# slot rails' pattern, and a 3.0 mm run south to R16. IPC wants 3.56 mm at 6 A on one outer layer; F.Cu and
# B.Cu together carry it with margin.
vbs = "VBUS20"
vbr = pads_rect(net_pads(vbs, ["R11", "C13", "C14", "C15"]), 1.4, 1.2)
_r16 = pads_rect(net_pads(vbs, ["R16"]), 1.0, 1.0); _r16x = (_r16[0] + _r16[2]) / 2
# ONE F.Cu island in the shape of the path, and nothing else. The first attempt added a B.Cu band under it
# with stitch vias along the row, and that bought two hard items and no current: two same-net B.Cu zones at
# one priority that touch are `zones_intersect`, and a stitch row across a strip of 2512 and 1210 lands has
# to miss every pad of every OTHER net between them. The island alone is 5.4 mm tall where IPC wants 3.56 mm
# for 6 A on one outer layer, and the leg to the charger's input shunt is 4.5 mm, so the copper is there
# without a single via. Every pad of this net joins it solid (RAIL_NETS below).
_leg = 4.0   # 15 September 2026: 2.25 gave a 4.5 mm column on 0.5 oz In3 that carried the rail alone once F.Cu was cut; ratio 2.41 at its corner (32.193)
_vbus_poly = [(vbr[0], vbr[1]), (_r16x - _leg, vbr[1]), (_r16x - _leg, _r16[1]), (_r16x + _leg, _r16[1]),
              (_r16x + _leg, vbr[1]), (vbr[2], vbr[1]), (vbr[2], vbr[3]), (vbr[0], vbr[3])]
PC.island(vbs, "VBUS20", _vbus_poly, pcbnew.F_Cu, priority=3)
# THE F.Cu ISLAND ALONE WAS CUT AND THE CURRENT FOUND AN INNER TRACK. Measured on the first route with this
# copper: the island fills (208 mm2) and 35 percent of the rail still travels on In2, with 5.36 A in a 1.0 mm
# inner stub beside U2, because signal tracks crossing the island on F.Cu break it into pieces and an In2
# track bridges them. It is VBAT's In2 neck in miniature and it has the same two answers, a second layer and
# a keep-out. The second layer is taken here because the keep-out would have to cover a 31 by 18 mm field of
# the front end's own gate drives and sense lines: B.Cu carries the same polygon, and the two are tied at the
# two places the current enters and leaves, inside the shunts' own 2512 lands, where nothing else can be.
# THE SECOND LAYER GOES ON In3, NOT B.Cu, AND THAT IS VBAT'S 10 A (13 September 2026, measured on A25).
# On B.Cu this polygon is 27.5 by 20 mm at (48.5, 65.2) to (76.0, 85.2), and VBAT's trunk from F1 runs north
# at x 53.5 to 58.5 straight through it to the collector under the four converters. Two bands of different
# nets never cross on one layer (32.39) and this one was drawn this morning without reading what was already
# there: the trunk filled as far as y 100.5 and stopped, the collector filled from x 76.1 east, and VBAT's
# comb was in TWO PIECES with the pack's 10 A left to find its way through the In2 plane's cut-up sheet and,
# for 3.29 A of it, through a 0.500 mm In3 router track (ratio 8.34, the worst number on the board).
# In3 is a pure routing layer here with no power copper within 40 mm, so VBUS20's second layer goes there: at
# 15.2 um it is 0.43 of B.Cu, and the F.Cu island alone is already 5.4 mm tall where IPC wants 3.56 at 6 A,
# so the second layer is bridging cuts rather than carrying the rail. On four layers there is no In3 and In2
# is the VBAT plane, so the second layer is not drawn at all and the four-layer board says so.
if NL_CU >= 6:
    # 15 September 2026 (32.191): with keepout=False the router laid a 13.4 mm 0.500 mm In2 track from the pad
    # row straight down to R16's own vias, and the solver put 3.4 A of the rail's 6 through it (ratio 8.61)
    # because the F.Cu leg and this polygon were both cut where other nets cross. A keep-out on the DIVE layer
    # forbids nobody's joins, there being no pad on it, and it is the rule every band has carried since 32.39.
    PC.union(vbs, "VBUS20 under", [(vbr[0], vbr[1], vbr[2], vbr[3]), (_r16x - _leg, _r16[1], _r16x + _leg, vbr[3]),
                                   (_r16x - _leg - 3.0, vbr[3] - 3.0, _r16x + _leg + 3.0, vbr[3] + 3.0)],   # a foot where the column leaves the bar: the inside corner was the worst cell (32.193)
             DIVE_CU, priority=2, keepout=True)
else:
    print("placement: VBUS20 gets no second layer on a %d layer board (In3 does not exist, In2 is the VBAT plane and B.Cu is VBAT's trunk)" % NL_CU)
_r11 = pads_rect(net_pads(vbs, ["R11"]), 0)
col(vbs, (_r11[0] + _r11[2]) / 2, (_r11[1] + _r11[3]) / 2 - 1.65, (_r11[1] + _r11[3]) / 2 + 1.65, 4)   # in the ISNS shunt's own pad (four since 15 Sep 2026: two carried 3.69 A each, ratio 3.07)
col(vbs, _r16x, (_r16[1] + _r16[3]) / 2 - 1.65, (_r16[1] + _r16[3]) / 2 + 1.65, 4)                      # and in the charger's input shunt
# the keep-out stops 2.5 mm short of R16: the shunt's own sense escapes (/CH_SRP, /CH_SRN) leave its pads along that edge
# and the placed board carried two `items_not_allowed` on them at the first try (15 Sep 2026)
_ends = sorted((vbr[1], _r16[1])); _ry = (_r16[1] + _r16[3]) / 2
if abs(_ends[1] - _ry) < abs(_ends[0] - _ry): _ends[1] -= 3.0   # the end nearer R16's centre is shortened, whichever way the frame runs
else: _ends[0] += 3.0
_klo, _khi = _ends
# The leg is not free of foreign pads after all: three GND pads with their fanout stubs sit across it at one y, and a
# track keep-out over them is three `items_not_allowed` before the route (15 Sep 2026). The keep-out is the leg minus
# a 1.8 mm band around every foreign pad's row, so the fanout keeps its stubs and the rail keeps the rest of the leg.
_bands = []
for _f in board.GetFootprints():
    for _p in _f.Pads():
        _cx, _cy = case_xy(_p.GetPosition())
        if _p.GetNetname().lstrip("/") != vbs and _r16x - _leg - 0.6 <= _cx <= _r16x + _leg + 0.6 and _klo <= _cy <= _khi: _bands.append((_cy - 1.8, _cy + 1.8))
_bands.sort(); _cuts = []
for _b0, _b1 in _bands:
    if _cuts and _b0 <= _cuts[-1][1]: _cuts[-1] = (_cuts[-1][0], max(_cuts[-1][1], _b1))
    else: _cuts.append((_b0, _b1))
_y = _klo; _n = 0; _pcs = []
for _b0, _b1 in _cuts + [(_khi, _khi)]:
    if _b0 - _y >= 1.0: PC.keepout("keep tracks off the VBUS20 F.Cu leg to R16", (_r16x - _leg, _y, _r16x + _leg, _b0), pcbnew.F_Cu); _n += 1; _pcs.append((_y, _b0))
    _y = max(_y, _b1)
# 15 September 2026, A33 MEASURED: with the leg at 8 mm the worst cell fell from 2.41 to 1.73 and moved to R16's via
# column, where four vias still carry the whole crossing between F.Cu and In3. A row of five across the leg on the
# keep-out piece nearest R16 (VBUS20 copper on both layers there, no foreign pad) spreads the crossing over a front.
if _pcs:
    _pc = min(_pcs, key=lambda q: min(abs(q[0] - _ry), abs(q[1] - _ry))); _yr = (_pc[0] + _pc[1]) / 2
    row(vbs, _r16x - _leg + 1.2, _r16x + _leg - 1.2, _yr, 5)
    print("placement: VBUS20 via row across the leg at y %.2f" % _yr)
print("placement: the VBUS20 leg keep-out runs y %.2f to %.2f in %d piece(s), %d foreign pad row(s) left free (R16 at %.2f)" % (_klo, _khi, _n, len(_cuts), _ry))
# 14 September 2026, MEASURED ON A28: FOUR VIAS CARRY A SIX AMP RAIL BETWEEN ITS TWO LAYERS. The F.Cu island
# and the In3 polygon under it are tied only inside the two shunts' pads, two vias each, and IPC gives a
# 0.4 mm barrel 1.11 A: four of them are rated 4.4 A against the rail's 6. The measurement says where the
# current went instead, In3 carrying 78 percent of it with a 0.500 mm router track at (-95.2, 37.1) taking
# 1.28 A against IPC's 0.40 (ratio 3.23) and the worst pour cell at 158 A/mm2 against 52 (ratio 3.04).
# Six more vias stand in the island's own copper between the three output capacitors, where the only pads are
# this net's; and the island gets the track keep-out every BAND on this board has carried since 32.39 and no
# island ever has, because the island being cut into pieces by the router's signal tracks is what sent the
# current down to In3 in the first place (the comment above predicted it and the first route confirmed it).
# THE GAP BETWEEN TWO OF THESE CAPACITORS IS THE NEXT ONE'S GND PAD (14 September 2026). These are 1210
# lands lying along x: C13's VBUS20 pad is at x 62.4 and its GND pad at 65.3, which is exactly the midpoint
# between C13 and C14's VBUS20 pads, so a via "between the capacitors" stands in a ground pad and a keep-out
# across the row forbids the three locked joins `join_adjacent_pins` lays between those pads. The vias go
# where R11's and R16's already do, INSIDE this net's own pads, two per 1210 land along its 2.70 mm axis.
for _c in ("C13", "C14", "C15"):
    _cr = pads_rect(net_pads(vbs, [_c]), 0)
    _cy = (_cr[1] + _cr[3]) / 2
    col(vbs, (_cr[0] + _cr[2]) / 2, _cy - 0.55, _cy + 0.55, 2)
# NO KEEP-OUT ON THIS ISLAND, and the two attempts at one are why (14 September 2026). Drawn at the island's
# own rectangle it forbade the three locked joins `join_adjacent_pins` lays between the output capacitors'
# ground pads; drawn as the two strips above and below the pad row plus the leg, it forbade a GND track
# crossing the leg. The leg is 4.5 mm of a board whose front side is the front end's own gate drives and
# sense lines, and a keep-out there is a wall across other people's routing. The six vias above are the
# change with a physical argument behind them: they are barrel, and barrel is what the rail was short of.
# If the island is still cut into pieces on the next route, the answer is a wider island or a second layer,
# not a wall.
# 6. +12V_HF: ALSO NO POWER COPPER, and the whole rail travelled 75.6 mm on one 0.400 mm In3 track, which
# IPC gives 0.37 A against the rail's 1.0. That is not a marginal number: solving I = k dT^0.44 A^0.725 for
# the rise gives about 93 K on that track. The band follows the corridor the ROUTER found, which is the
# proof that the space is free: the caps east, north past the mezzanine, east under the PA band and north
# into J_HF. It goes on In3, which on a six-layer A is a pure routing layer with no plane on it.
# ON FOUR LAYERS THERE IS NO In3, and the only layers left are In2, where a 100 mm band would cut the east
# GND plane, and B.Cu, where it would cross the PA rail's band (two bands of different nets never cross on
# one layer, 32.39). So the four-layer board is generated WITHOUT this copper and says so: its +12V_HF will
# read MISSED, and that is a true cost of four layers for the layer P0 to carry, not something to hide.
hf = "+12V_HF"
# 0.5 mm of growth, not 1.2: at 1.2 the island reached into the HF stage's own gate drive and the router
# came back with EIGHT shorting_items between /HF_HDRV1 and /HF_SW1, which are the FET gate and the switch
# node of this very converter. Power copper that squeezes its own stage's drive is not power copper.
hfr = pads_rect(net_pads(hf, ["R65", "C109", "C110", "C111"]), 0.5, 0.5)
# 14 September 2026, MEASURED ON A28: THE HEAD ISLAND IS THE BOUNDING BOX OF FOUR SCATTERED PADS AND MOST OF
# WHAT IS INSIDE IT BELONGS TO SOMEBODY ELSE. R65 sits at (120.2, 153.3) and the three output capacitors at
# (135.5 to 141.3, 139.7 to 144.1), fifteen millimetres apart, so the rectangle is 23.3 by 17.7 mm and it
# swallows the whole HF stage: L9, Q16, Q23, R60 to R64, C69 to C71 and every gate drive and sense line they
# carry. It fills **70 of 412 mm2 in three pieces**, and `check_pcb_a` refuses the board for it, which is the
# only failure in 835 checks. The comment below has known it fills in pieces since the 13th and answered the
# electrical half with two vias in the shunt's own pad; this is the other half. The island is the capacitor
# column alone, which is copper this net's own pads sit in, and R65 meets the rail at the band through those
# vias, where it is made. The In3 band is unchanged: it carries 95 percent of this rail and reads MET.
hfr_head = pads_rect(net_pads(hf, ["C109", "C110", "C111"]), 0.5, 0.5)
PC.island(hf, "HF rail head", rect_pts(hfr_head), pcbnew.F_Cu, priority=3)
if NL_CU >= 6:
    _jh = pads_rect(net_pads(hf, ["J_HF"]), 0.8)
    # 13 September 2026, A25 MEASURED: the east run passed THROUGH J_AB2's pin field. The 4.0 mm run at y 115
    # to 119 crosses the ribbon header's ten through-hole pads at x 243.2 and 245.8, y 115.9 to 126.1, and the
    # fill retreats round every one of them: the worst pour cell read 105.3 A/mm2 against 52.0 (ratio 2.02) in
    # the isthmus between two pads. A pour does not pass a pin field, it threads it. The run steps north of the
    # header's top pin instead, where In3 is empty from x 232 to 252, and rejoins the north run above it.
    PC.union(hf, "HF rail", [(hfr[0], hfr[1] - 0.5, hfr[2] + 2.0, hfr[3]),      # the head, over the shunt and the caps
                             (hfr[2] - 2.0, -9.0, hfr[2] + 2.0, hfr[3]),        # north out of the head
                             (hfr[2] - 2.0, -9.0, 86.0, -5.0),                  # east under the PA band's own run, on another layer
                             (82.0, -9.0, 86.0, 0.0),                           # north, clear of J_AB2's west pin column
                             (82.0, -4.0, 102.0, 0.0),                          # east above the header's top pin (its pads end at y 115.9)
                             (98.0, -9.0, 102.0, _jh[3]),                        # north past J_54V, west of the PA band's north run
                             (98.0, _jh[1], _jh[2], _jh[3])],                    # east into J_HF
             pcbnew.In3_Cu, priority=2)
    col(hf, hfr_head[2] - 0.6, hfr_head[1] + 1.0, hfr_head[3] - 1.0, 3)          # the head island to the band
    # AND THE SOURCE MEETS THE BAND AT THE SHUNT. The head island fills in four pieces, because the converter's
    # own parts (L9, Q16, Q23, the output capacitors) stand in the rectangle, and the piece that holds R65, the
    # shunt the rail is measured at, is not the piece the three vias above are in: 0.71 A of this 1.0 A rail was
    # crossing on a 0.400 mm In2 router track, ratio 2.10. Two vias inside the shunt's own output pad put the
    # current on the band where it is made, which is the answer the record already reached for VBUS20's shunts.
    _r65 = pads_rect(net_pads(hf, ["R65"]), 0)
    col(hf, (_r65[0] + _r65[2]) / 2, (_r65[1] + _r65[3]) / 2 - 1.1, (_r65[1] + _r65[3]) / 2 + 1.1, 2)
    # NO stitch vias at J_HF: it is a JST-VH, its pins are through-hole and already join every layer, and a
    # via placed inside its land is `hole_to_hole` against those pins (four of them, first attempt).
else:
    print("placement: +12V_HF gets NO power copper on a %d layer board (In3 does not exist; In2 would cut the east GND plane and B.Cu would cross the PA band). Its density will read MISSED, which is a real cost of four layers." % NL_CU)
# every pad of a rail net joins its pour solid (no thermal spokes): a through-hole pin's four spokes are the neck of an 8 A path, and the mesh judge sees them as no connection
RAIL_NETS = {"VBAT", "CELL+", "VIN_RAW", "+5V_S1", "+5V_S2", "+5V_S3", "+5V_DEV", "+13V8_PA", "S1_OUT", "S2_OUT", "S3_OUT", "SD_OUT", "VBUS20", "+12V_HF"}
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
