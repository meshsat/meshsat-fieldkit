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
         # THE KELVIN RESISTORS SIT AT THE SHUNT (18 September 2026, rule ANA-001). On E17 the packer put R6 and
         # R7 at x 21.0 and 25.2 while the shunt R5 is at 2.46 and the controller at 32.99, so the FILTERED pair
         # ran 11 to 15 mm through the switching neighbourhood and read 0.142 and 0.276 mm from TRK_SW1 and
         # TRK_SW2. A series resistor attenuates line pickup only at the SOURCE end, which is the shunt, and the
         # capacitor belongs at the amplifier (C16 is declared as U5 pin 3's decoupling, so the bypass pass seats
         # it there). These two seats are the same row as R5, three millimetres apart, clear of C17 and C18 at
         # y -101.3 and of Q6 at (14.8, -91.4).
         # FIRST SEATS REFUSED BY THE BOARD (E18, 12:03 UTC): x 6.0 overlapped the shunt's own courtyard, which a
         # 2512 carries out to about 5.7, and x 9.0 sat on D5 where the packer had put it. The row below is clear:
         # C18 is at x 0.1 and nothing else stands between there and D5, and R5's courtyard ends about y -99.5.
         "R6": (3.6, -101.3, 0, False), "R7": (6.6, -101.3, 0, False),
         "J_SMB": (-144, -62, 0, False), "J_POD": (-138, -62, 0, False), "J_LTG": (-132, -62, 0, False), "J_GEIGER": (-126, -62, 0, False), "J_DCF": (-144, -49.3, 0, False), "J_FAN1": (-138, -49.3, 0, False), "J_FAN2": (-132, -49.3, 0, False),
         # OWNER DECISION 31, RULED 21 SEPTEMBER 2026: the pod clamp sits AT the pod connector, which is
         # Nexperia's and ST's own layout clause 1 and the whole point of the part. Measured on the
         # committed board before the seat was written, and the FIRST seat was wrong because it was
         # measured from the footprint's ORIGIN, which on one of these headers is PIN 1: D9 landed on
         # J_POD's own pad 4 and the placed DRC named the short (E42P, 21 September 2026). Read off the
         # PADS instead: J_POD's four pins run SOUTH from y -58.19 at 2.54 mm, so the column ends at
         # -65.81; J_LTG's column is 6 mm east at x -132 and J_SMB's 6 mm west; D7 and D8 sit at y -74.4.
         # THE LANE BETWEEN TWO CONNECTOR COLUMNS WAS MEASURED FROM THE PADS AND IT IS THE COURTYARDS THAT
         # DECIDE: the pads leave 3.7 mm between J_POD and J_LTG and the courtyards leave 2.46, where this
         # part needs 3.0, so that seat came back as two courtyards_overlap (E42P, second run). Board E is a
         # single-sided assembly, so the underside is not available either. The seat is SOUTH of the pod
         # column, in the 4.5 mm band between J_POD's courtyard (ending y -67.58) and D7's (starting
         # -72.12): 4.0 mm to pin 4 (SCL1), 6.5 to pin 3 (SDA1) and 11.6 to pin 1 (+3V3_E6), which is the
         # best this row allows and is recorded rather than glossed. The two conductors that carry the
         # strike from outside are the near ones; the rail's clamp is the one that sits far.
         "D9": (-138, -69.8, 0, False)}

# FOURTEEN DECOUPLING CAPACITORS AT THE PINS THEY SERVE (20 September 2026, appendix 32.312 and 32.313).
# `bypass_slots` has never reserved a slot on any board of the set, because the 3 mm limit meets the
# 2.2 mm escape-fan exclusion at every fine-pitch pin, so board E's eighteen declared capacitors were
# wherever the packer had room: median 11.8 mm from their pin and the worst 28.4. Each seat below was
# measured by `bypass_seats.py` on the board this generator makes, outside every courtyard, escape fan,
# part-forbidding rule area, packer region rectangle, piece of laid copper and the board edge, and held
# as it was handed out. Proved through the chain: placed board hard 0, 174 escapes and 5 pads skipped,
# `netlist_board` 818 of 818, every number the baseline's, and the distances median 11.8 to 6.4 mm,
# worst 28.4 to 9.6, total 239 to 110.
FIXED.update({
    "C16": (30.05, -83.57, 0, False), "C38": (82.75, -86.60, 0, False), "C39": (82.75, -101.40, 0, False), "C40": (86.74, -101.42, 0, False),
    "C41": (88.88, -86.53, 0, False), "C42": (88.39, -84.41, 0, False), "C43": (84.76, -84.48, 0, False), "C44": (96.25, -78.85, 0, False),
    "C45": (87.32, -103.51, 0, False), "C46": (80.91, -84.51, 0, False), "C47": (87.66, -82.29, 0, False), "C48": (37.58, -51.05, 0, False),
    "C49": (38.12, -48.59, 0, False), "C50": (37.45, -46.53, 0, False),
})
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
text("PACK", -138, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("F3 25A", -120, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("DC IN", -64, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("F1 10A", -48, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("PV", -22, -112.2, pcbnew.F_SilkS, 1.2, 0.2); text("F2 10A", -6, -112.2, pcbnew.F_SilkS, 1.2, 0.2)
# ---------------------------------------------------------------- SMD cluster on the underside (packer from gen_pcb_b3, loosened)
REGIONS = [
 ("MCUR",   (91, -106, 118, -80), ["U11", "Y1", "C36", "C37", "R28", "R29", "R30", "R31", "R32", "JP1"] + ["C%d" % k for k in range(38, 48)] + ["TP10", "TP11", "TP12", "R33", "LED2", "R34", "R35", "R36", "R37"], False),
 ("PACK",   (-146, -104, -118.5, -83.5), ["C1", "D3", "TP8", "TP9", "C31", "U12", "L3", "U13", "C30", "C32", "C33", "C34", "C35", "R48", "TP13", "R42", "R43"], False),
 ("FANS",   (-145, -83.4, -116, -71.5), ["Q9", "Q10", "R44", "R45", "R46", "R47", "D7", "D8", "R49", "R50"], False),
 # E35 (21 September 2026, 04:17 CEST): THE INPUT SIDE IN THE ORDER THE CURRENT FLOWS. Until E34 the hot-swap block sat WEST of
 # the entry block and the choke EAST of it, so the shore current went J_DCIN east to F1, west to Q1, west again to R19 and
 # Q7, then 64 mm east to L2 and 44 mm back west to J_BLK: about 172 mm in six pieces, four of them too narrow at 8 A
 # (20 September 2026, PI-001), the DC_HS band the longest generator-laid conductor on the board. The three regions are
 # re-split along the strip so the path runs one way: J_DCIN and F1 on the south row, the entry block above them, the
 # hot-swap block west of it, the choke west of that under J_BLK, and VIN_RAW's clamp and capacitor in their own pocket
 # beyond: about 113 mm, the DC_HS band 26 mm. Measured through the whole chain on the hub eight times before this
 # (/root/erc10 to erc18): the first refusal was the pad guard on VIN_RAW's ten source barrels typed at the choke's OLD
 # seat, which is why every piece of this side's copper is derived from the placed pads below; then L2's courtyard on H5,
 # then ENTRYB overflowing by 5.4, 2.7 and 1.7 mm (the choke needs HEIGHT, not width), then D2 on H6 three ways, then
 # ENTRYB overflowing again with D2 and C8 in it. The last two runs end PREROUTE-DONE OK at hard 0, escapes 174/5 as E33,
 # place_audit 0 of 8, pre-route hard 0. The mounting holes at y -83 (H5 at x -104, H6 at -66) cap every region that
 # contains one at y -87; a region between them may reach -82.
 ("RAWC",   (-118, -102, -100, -88), ["D2", "C8"], False),                                   # the raw bus clamp and its capacitor, west of the choke under H5
 ("ENTRYB", (-99, -105, -80, -82), ["L2", "C6", "C7", "R27", "LED1", "TP3"], False),          # the choke west under J_BLK, east of H5's column
 ("HOTSW",  (-80, -104, -54, -87), ["U6", "R19", "Q7", "R20", "R21", "R22", "R23", "C5", "R24", "R25"], False),   # under H6's keep-out
 ("ENTRYA", (-54, -103, -26, -83), ["U3", "Q1", "C4", "R1", "D1", "D10", "C2", "TP1", "TP2", "Q8", "R26"], False),   # D10: owner decision 31, the inlet clamp at the entry (its distance to F1 is read off the placed board)
 ("TRKIN",  (-26, -103, -2, -81), ["D4", "C11", "C12", "C13", "C14", "C15", "TP5"], False),
 ("TRKW",   (-2, -103, 28, -81), ["Q3", "Q4", "Q5", "Q6", "R5", "C16", "C17", "C18", "D5", "D6"], False),   # R6 and R7 left this list for fixed seats at the shunt (18 September 2026)
 ("TRKS",   (39.5, -95.5, 56, -80), ["C19", "C20", "C21", "C22", "C23", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17"], False),
 ("TRKOUT", (56, -112, 78, -81), ["C24", "C25", "C26", "C27", "U4", "Q2", "C28", "R18", "TP6"], False),
 ("SENS",   (40, -78, 52, -46), ["U14", "C48", "U15", "R51", "C49", "C50", "R38", "R39", "C51", "R40", "R41"], False),
 ("TPS",    (78, -112, 118, -107), ["TP4", "TP7"], False),
]

_SEATED = {"C16", "C38", "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50"}   # the fourteen above are placed by hand and must not also be packed
REGIONS = [tuple([_r[0], _r[1], [_x for _x in _r[2] if _x not in _SEATED]] + list(_r[3:])) for _r in REGIONS]
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
import json as _json, os as _osx, bypass_slots
import regionfit
regionfit.allowance('e')
_ip = _osx.path.join(_osx.path.dirname(_osx.path.abspath(BOARD)), "out", _osx.path.splitext(_osx.path.basename(BOARD))[0] + "-intent.json")
_entries = _json.load(open(_ip)).get("bypass", []) if _osx.path.exists(_ip) else []
RESERVED = set() if _osx.environ.get("BYPASS_SLOTS") == "0" else bypass_slots.reserve(board, place, lambda v: (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y)), _entries)
for _r in RESERVED: placed[_r] = board.FindFootprintByReference(_r)
REGIONS = [(_n, _rect, [_r for _r in _refs if _r not in RESERVED], _bk) for _n, _rect, _refs, _bk in REGIONS]   # a reserved capacitor is placed already
for name, (x0, y0, x1, y1), refs, back in REGIONS:
    regionfit.record(name, (x0, y0, x1, y1), back, len(refs), stem=os.path.splitext(os.path.basename(BOARD))[0])
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
    if cy - rowh < y0 - 0.01: regionfit.note(name, y0 - (cy - rowh))
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
# 13 September 2026, owner ruling 16 and 22. The conductor measure found 4.89 A of this 8 A rail going through
# a LOCKED 0.400 mm escape stub and a single 0.45/0.25 mm escape via at L2 pad 2, the choke that is the rail's
# own source, against IPC's 1.23 A for that track. The pour existed and the current was not in it, for two
# reasons this line and the block below fix: the pour stopped at y -80 while the block lands it feeds sit at
# y -75.2, so the last 5 mm was router track; and a 4.50 x 2.15 mm source pad reached the pour through one
# signal via. This is the CELL+ lesson in another place: a rail's current finding geometry meant for signals.
# 13 September 2026, SECOND READING on E8's routed board: the pour's north edge ran along the heads of the
# ten power vias it was given. The vias sit at y -74.7 and -75.7 with 0.45 mm of radius, so each one's
# clearance ate into a strip 0.25 mm wide, and the worst pour cell clear of any via read 59.3 A/mm2 against
# 52.0 (ratio 1.14) a millimetre south-east of them. In2 is EMPTY from y -71 to -74 across this whole span
# (measured: three of this net's own vias and one GND via in 66 by 4 mm), so the pour takes that room and
# the current spreads round the via heads instead of squeezing past them.
# E35 (21 September 2026): the input side's copper is DERIVED from the placed pads it serves, so the regions can move. The
# VIN_RAW island and its ten source barrels sit in L2's pad 2 wherever the packer puts L2, the In2 pour spans from the
# choke to the block lands, and the DC_HS band runs from Q7's source pads to L2 pin 1 as an L of two rectangles.
def _padc(ref, num):
    """case (x, y) of a placed pad's centre"""
    for _q in placed[ref].Pads():
        if str(_q.GetNumber()) == str(num):
            _c = _q.GetPosition(); return (_c.x / 1e6 - OX, OY - _c.y / 1e6)
    raise SystemExit("no pad %s on %s" % (num, ref))
_L2S = _padc("L2", "2"); _L2I = _padc("L2", "1")          # the choke's source pad (VIN_RAW) and its input pad (DC_HS)
_BLKX = [_padc("J_BLK", str(_k))[0] for _k in (1, 2, 3, 4)]
_Q7S = [_padc("Q7", str(_k)) for _k in (1, 2, 3)]         # the hot-swap FET's three source pads (DC_HS)
pour(pcbnew.In2_Cu, "VIN_RAW", "VIN_RAW pour In2 (filter to the block lands, north to the lands themselves)",
     (min(_L2S[0], min(_BLKX)) - 8.0, -100, max(_L2S[0], max(_BLKX)) + 8.0, -71), priority=1)
# The rail's 8 A leaves L2's pad 2 and 2.23 A of it was measured on the LOCKED 0.400 mm escape stub beside the
# pad, which IPC gives 1.23 A: the rail has copper on In2 and none on the layer its source pad is on, so that
# stub is a lone conductor with nothing beside it. A small F.Cu island over the pad and the stub's own run
# gives the current somewhere to go, and the conductor test then judges the island's cells rather than a
# 0.4 mm track, which is what the pour bar is for.
pour(pcbnew.F_Cu, "VIN_RAW", "VIN_RAW island F.Cu at the source pad", (_L2S[0] - 3.0, _L2S[1] - 2.25, _L2S[0] + 3.0, _L2S[1] + 2.25), priority=1)
pour(pcbnew.In2_Cu, "PV_P", "PV_P pour In2 (panel input)", (-26, -113, -2, -80), priority=1)
pour(pcbnew.In2_Cu, "TRK_OUT", "TRK_OUT pour In2 (tracker output)", (56, -113, 76, -80), priority=1)
pour(pcbnew.In2_Cu, "CELL_F", "CELL_F plane In2 (the west end: the pack node to the pack parts, the fans and the monitor divider; a DSN plane on the power layer In2 since E6 round 4)", (-148, -112, -100, -46), priority=1)
pour(pcbnew.F_Cu, "CELL_F", "CELL_F pour F.Cu (blade to the pad)", (-128, -112, -100, -103.5), priority=1)
# 15 September 2026 (decision 27, appendix 32.198): In2 carries a GROUND fill under everything its four power pours do not
# cover (they take priority 1, the fill 0). Measured before this: 88 percent of E's back-side signal track ran over bare
# dielectric on In2 with In1's plane a core away, 59 of 76 signal nets over the return-path limit. The router already
# treats In2 as a power layer, so the fill is one more DSN plane and costs no routing room.
for L in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu):
    pour(L, "GND", "GND pour %s" % board.GetLayerName(L), (-149, -113, 118, -45), priority=0)
pour(pcbnew.B_Cu, "CELL_F", "CELL_F band B.Cu (the blade lands and the west end: the pack node to the fans and the monitor divider; E6 route 2 left them open)", (-148, -112, -100, -46), priority=1)
# ---------------------------------------------------------------- power vias where the 8 A leaves its pads
# A 0.8/0.4 mm via carries about 2.5 A, so three at the source and one per block land cover 8 A with margin.
# Checked against the placement before they are drawn: a via that would sit on another net's pad is a short,
# and drawing one blind is how this would go wrong.
import power_copper as _pcmod
# 13 September 2026 (appendix 32.166): three vias in the source pad left 1.29 A of the rail's 8 on the LOCKED
# 0.400 mm escape stub beside them, which IPC gives 1.23 A: ratio 1.05, and the In2 pour's worst cell clear of
# every via read 1.21. The current divides between the stub and the barrels by conductance, so a second row of
# three lowers the barrel path's resistance and draws current off both. L2 pad 2 is 4.50 x 2.15 mm: two rows
# 1.1 mm apart put a 0.8 mm via 0.13 mm inside the pad's own edge at the worst corner, and the self-check
# below refuses any of them that lands on another net's pad.
# 13 September 2026, SECOND READING: the barrels are the neck here too. The measure that judges a via on its
# own wall found each J_BLK land's single 0.4 mm via carrying 2.16 A where IPC gives that 0.0314 mm2 of wall
# 1.11 A, ratio 1.95. The lands are 2.00 mm pogo targets: TWO vias fit side by side at 1.0 mm apart, and a
# 0.5 mm drill has 0.0393 mm2 of wall and carries 1.30 A, so a pair carries 2.60 A against the 2 A each land
# takes of the rail's 8. Hole to hole is 0.5 mm and each via's 0.9 mm body sits 0.05 mm inside the pad edge.
# THIRD READING, same day: with two rows of THREE in the source pad, the worst barrel there still carried
# 1.69 A against that 1.30. L2's pad 2 is 4.50 x 2.15 mm, which takes FIVE columns at 0.8 mm and two rows at
# 1.1, so ten barrels carry 13.0 A against the rail's 8 and the worst should take about a tenth of it. Hole
# to hole is 0.30 mm across the columns and 0.60 between the rows, and each 0.9 mm body sits 0.2 mm inside
# the pad's own edge. Everything else on that rail is now under its bar: the conductor reads 0.55 and the
# pour, clear of every via, exactly 1.00.
VIN_VIAS = [(_L2S[0] + 0.8 * _k, _L2S[1] + 0.55) for _k in (-2, -1, 0, 1, 2)] + \
           [(_L2S[0] + 0.8 * _k, _L2S[1] - 0.55) for _k in (-2, -1, 0, 1, 2)] + [
            (-86.35, -74.73), (-83.81, -74.73), (-81.27, -74.73), (-78.73, -74.73),   # two per J_BLK land,
            (-86.35, -75.73), (-83.81, -75.73), (-81.27, -75.73), (-78.73, -75.73)]   # 1.0 mm apart across it
if _osx.environ.get("PLACE_VIN_VIAS", "1") not in ("0", ""):
    _hits = []
    for _vx, _vy in VIN_VIAS:
        for _ref, _fp in placed.items():
            for _pd in _fp.Pads():
                if _pd.GetNetname() in ("VIN_RAW", "/VIN_RAW"): continue
                _bb = _pd.GetBoundingBox()
                _dx = max(_bb.GetLeft() / 1e6 - OX - _vx, 0, _vx - (_bb.GetRight() / 1e6 - OX))
                _dy = max((OY - _bb.GetBottom() / 1e6) - _vy, 0, _vy - (OY - _bb.GetTop() / 1e6))
                if (_dx * _dx + _dy * _dy) ** 0.5 - 0.4 < 0.35:
                    _hits.append("via at (%+.2f, %+.2f) touches %s.%s [%s]" % (_vx, _vy, _ref, _pd.GetNumber(), _pd.GetNetname() or "-"))
    if _hits:
        raise SystemExit("power vias: %d of them sit on another net's pad:\n  %s" % (len(_hits), "\n  ".join(_hits[:10])))
    # THE DRILL IS 0.7 AND NOT 0.5 SINCE 18 SEPTEMBER 2026, and the number comes off E18's own finished board.
    # These eight barrels ARE sharing (dc_drop's solved mesh gives them 0.78 to 1.39 A each, so the parallel path
    # the comment above intends is real), and each one is still over its own wall: a 0.50 mm barrel of the
    # fabricator's 18 um plating is rated 1.05 A at a 10 K rise and the worst reads 1.387, ratio 1.32, which is
    # rule PI-003's failure on this board. There is no room for a third row of vias (J_BLK's second pin row sits
    # at y -77.77 and its 2.0 mm lands reach -76.77, so a row at -76.73 would touch USB_E6_N's pad), so the answer
    # is the barrel and not the count: 0.70 mm of hole is rated about 1.47 A, and 1.1 mm of pad keeps the 0.20 mm
    # ring this board declares. Measured again on the next E board by via_current; barrel_sites.py is the map.
    # AND THE WIDER HOLE IS THE BLOCK'S ALONE, which the gate said before any router saw it (18 September 2026).
    # VIN_VIAS is two clusters: ten at the SOURCE pad on a 0.8 mm pitch and eight at the block lands on 2.54 mm.
    # At 0.5 mm of drill the source cluster sits at 0.30 mm hole to hole, one hundredth above this board's own
    # 0.2995 floor; at 0.7 mm it is 0.10 and the placed board came back with EIGHT hole_to_hole violations. The
    # source cluster does not need the wider hole anyway: the solved mesh gives its barrels 0.86 to 0.98 A
    # against the 1.05 a 0.5 mm barrel carries, and it is the block's eight that read 1.32 of their rating.
    _pcv = _pcmod.PowerCopper(board, net_for, P)
    _pcv.stitch("VIN_RAW", VIN_VIAS[:10], drill=0.5, width=0.9)     # the source pad, 0.8 mm pitch: 0.30 mm hole to hole
    _pcv.stitch("VIN_RAW", VIN_VIAS[10:], drill=0.7, width=1.1)     # the block lands, 2.54 mm pitch: 1.84 mm hole to hole
    print("power copper: %d VIN_RAW power via(s), 10 at the source pad at 0.5 mm and %d at the block lands at 0.7 mm"
          % (len(VIN_VIAS), len(VIN_VIAS) - 10))

# ------------------------------------------------- CELL_F's own layer transition, in parallel barrels (18 Sep 2026)
# The other half of PI-003 on this board, read off E18's finished copper with barrel_sites.py: ONE 0.30 mm barrel at
# case (-113.4, -104.11) carries 1.091 A of the solved mesh against 0.738 A for its own wall, ratio 1.48, while the
# rest of this rail's eighteen barrels carry 0.5 A and less. It is the pack rail crossing layers at the fuse, and the
# fixer that lays a parallel barrel after the route found no site for it, which is board D's case exactly (D12, and
# D15 is the answer): the generator does not have to search, because the neighbourhood is EMPTY. barrel_sites reports
# no pad of any other net within 6 mm of it, and F3's own pad 2 copper 2.74 mm away. So two more barrels go beside it
# on this net's own copper, 0.9 mm either side along the land, at the 0.5 mm drill the block vias use (1.05 A each):
# 1.09 A over three barrels is about 0.36 A apiece. If the fill does not reach one of them the pre-route DRC says so
# and the reading moves it; that is cheaper than leaving a 1.48 ratio on the rail that carries the pack.
if _osx.environ.get("PLACE_CELLF_VIAS", "1") not in ("0", ""):
    # the count comes from the current, not from a hand count: cluster() asks via_current what 1.091 A needs at
    # 0.5 mm (two barrels of 1.05 A) and places them centred on the transition, so the router's own via there
    # keeps its copper and the spread is along x, which barrel_sites reports as the clear direction.
    # 19 September 2026, MEASURED ON E21's ROUTED BOARD and corrected here: `amps=1.091` was E18's WORST
    # BARREL, used as the SITE's total, which is the attribution mistake of 16 September in a new place. The
    # solved mesh on E21 puts 1.198 A and 0.611 A through the two barrels this call placed, so the site passes
    # 1.809 A and shares it about two to one (skew 1.325 against an even split). Sized on those two numbers the
    # count is THREE, and `cluster(skew=)` is where the second one goes; `boards/e.json`
    # `_cellf_cluster_measured` carries the reading and states the model's assumption.
    # 21 September 2026, RE-MEASURED ON E36's LANDED ROUND-1 BOARD, which is what the model asked for: the
    # three barrels this call now places carry 1.23, 0.62 and 0.29 A of the solved mesh, so the site passes
    # 2.14 A and its worst share is 1.72 times an even one, where the number above says 1.325. The skew is a
    # property of the geometry and it moved when the count did, which is the assumption the comment above
    # states, so the number is the newer measurement's. IT COSTS NOTHING HERE and that is checked rather than
    # assumed: via_current.barrels_for at 0.5 mm reads THREE barrels for 1.809 * 1.325 = 2.397 A and THREE for
    # 1.809 * 1.72 = 3.111 A, one barrel carrying 1.051 A at a 10 K rise and 18 um of plating.
    _cf = _pcmod.PowerCopper(board, net_for, P).cluster("CELL_F", (-113.4, -104.11), amps=1.809, skew=1.72, drill=0.5, width=0.9, axis="x")
    print("power copper: %d CELL_F barrel(s) at the fuse transition that reads 1.48 of its rating on E18" % len(_cf))

# ---------------------------------------------------------------- PI-003's generator answer, all of it (20 September 2026)
# `barrel_sites --suggest` on E17, the board sweep 32 judged: THIRTY-TWO barrels over their own rating across
# eleven measured nets at 10 K and 18 um of plating. TEN of them are a new cluster and these are the ten, each
# line and each number printed by the tool rather than typed, with the axis it reports as the clear one. The
# other thirteen are the generator's OWN locked vias, where a cluster centred on the site would land 0.30 to
# 0.35 mm from a hole that is already there; those are points added to the calls that placed them and are a
# separate change, listed in `boards/e.json` `_board_es_pi003_work_list_is_ten_cluster_lines_and_thirteen_raised_calls`.
#
# THE WORST ARE THE INPUT SIDE AND THEY ARE THE CONDUCTORS 32.249 ALREADY NAMED: `DC_F` and `DC_P` each put
# 8.00 A through ONE 0.40 mm barrel rated 0.90 A, ratio 8.89, and `TRK_OUT` 6.160 A through one at 6.85. So
# board E's five input rails are one floor-plan item read two ways, too narrow as conductors and worst as
# barrels, and this half is the one a generator can answer on its own.
#
# A site that cannot be placed says so and the run carries on: `cluster` refuses a lattice that would break
# hole-to-hole, and a site still short afterwards is a placement question with a number, which is the rule
# board A's eleven sites were answered under on 20 September at 00:10.
if _osx.environ.get("PLACE_E_BARRELS", "1") not in ("0", ""):
    _pcE = _pcmod.PowerCopper(board, net_for, P)
    # E36 (21 September 2026, 06:0x CEST): FOUR OF THE FIVE TYPED SITES WERE IN EMPTY BOARD ON E35's FLOOR PLAN.
    # The five coordinates below were typed from barrel_sites --suggest on E29's placement; E35 re-split the input
    # side and TRKOUT moved, and on E35's pre-route board (/root/erc18) the DC_HS, both DC_P and the TRK_OUT clusters
    # (3, 7, 7 and 7 barrels) sat with NO pad of any net within 3 mm: twenty-four barrels of dead copper laid where
    # the parts used to be, which the pad guard cannot see (it refuses a barrel in ANOTHER net's pad, not one in
    # nothing) and the judge does not count (they are outside every land's window). A typed coordinate is a claim
    # about a placement that was true once; every site here is DERIVED from the placed pad now, the way VIN_RAW's
    # island and barrels are since E35. The FET source lands take islands and clusters below; DC_P reads carrying
    # on E35's judge without a typed site and takes none.
    _E_SITES = [
        # E39, 21 September 2026: the skew is MEASURED now rather than assumed even. On E37's finished
        # round-1 board this cluster's five barrels pass 5.07 A with 1.747 A through ONE of them, a worst
        # share of 1.72 times an even split, so the count comes from `amps * skew` the way CELL_F's has
        # since 19 September: 2.968 * 1.72 = 5.10 A is SEVEN barrels at 0.30 mm where an even split asks
        # five. The model's assumption travels with it: a skew is a property of the geometry and it falls
        # as barrels are added and spread, so this is re-measured on the arm that carries it and never
        # treated as a constant of the site. `cluster` refuses a lattice that breaks hole-to-hole and the
        # run carries on, which is what says whether the room is there.
        ("PV_P", _padc("Q3", "5"), 2.968, 0.30, "y", 1.72),   # the tracker input FET's drain tab; worst 2.02 on E29
    ]
    _e_laid, _e_refused = 0, []
    # THE BASIS OF EVERY SKEW BELOW, beside the call that uses it (test_cluster_skew_basis): a skew is a
    # measurement on ONE routed board and goes stale like a typed coordinate. The only row above an even
    # split today is PV_P's 1.72, read on E37's FINISHED round-1 board on 21 September 2026 (sha
    # 246563debc363acd): its five barrels pass 5.07 A with 1.747 A through one of them, so the worst share
    # is 1.72 times an even one and `barrels_for(2.968 * 1.72)` is seven at 0.30 mm where five were laid.
    # boards/e.json `_e39_is_one_line_because_the_room_and_not_the_need_sets_the_other_three_counts`
    # carries the reading and what it does NOT change; re-measure it on the arm that carries it.
    for _n, _at, _a, _d, _ax, _sk in _E_SITES:
        try:
            _got = _pcE.cluster(_n, _at, amps=_a, drill=_d, axis=_ax, skew=_sk)
        except Exception as _e:
            _e_refused.append("%s at %s: %s" % (_n, _at, _e)); continue
        _e_laid += len(_got or [])
    print("power copper: %d barrel(s) placed over %d PI-003 site(s) on board E%s"
          % (_e_laid, len(_E_SITES), ("; REFUSED: " + "; ".join(_e_refused)) if _e_refused else ""))

# ---------------------------------------------------------------- the hot-swap output, in locked copper (E14, 18 September 2026)
# DC_HS is the LM5069's output: Q7's three source pads at the west edge of HOTSW to L2 pin 1 and C6 in ENTRYB, 64 mm
# east, and it carries the shore and vehicle current (8 A typical, 10 peak, the same conductor VIN_RAW is on the far
# side of the choke). E11 routed it on Q7's WRONG pins (32.219); with the source pads carrying it E12 and E13 left it
# open (E13: 0 hard, this one connection), the board-wide stub router finds no lane for a 0.8 mm conductor across the
# strip at all, and 0.8 mm is under the density bar for that current anyway. So it is the generator's, the way board
# A's rails are: a B.Cu band (5.5 mm, IPC-2221's 5.3 at 8 A and 10 K, 1 oz) east along y -97 under the HS_S tab and
# R19, north at x -60 through ENTRYA, and east at y -86 into L2 pin 1, 4.5 mm there because VIN_RAW's ten source
# vias sit 3 mm south of that pad and a wider band would put them inside it. Every band is a wire keep-out on B.Cu,
# so the parts above it lose B.Cu via sites under the band; the route says what that costs. Three stitch vias at
# each end; the Q7 end's vias land on the source pads themselves.
if _osx.environ.get("PLACE_DCHS_BAND", "1") not in ("0", ""):
    _pc = _pcmod.PowerCopper(board, net_for, P)
    # no end vias from rail_run (a corner via at x -60 could land on a top part's pad of another net); the vias are
    # placed where the copper is this net's own: one in each of Q7's three source pads, three inside L2 pin 1
    # ONE zone from the three rectangles (E14's first placement read two zones_intersect: three same-net bands at one
    # priority meeting at their corners, which KiCad refuses, and union() is the 8 September answer to exactly that)
    _qx = _Q7S[0][0]; _qy = sum(_p[1] for _p in _Q7S) / 3.0        # the source pads' column and its middle
    _lx, _ly = _L2I                                                # L2 pin 1
    _run = (min(_qx, _lx) - 2.75, _qy - 2.75, max(_qx, _lx) + 2.75, _qy + 2.75)      # along the source pads' y, 5.5 mm
    _leg = (_lx - 2.25, min(_qy, _ly) - 2.25, _lx + 2.25, max(_qy, _ly) + 2.25)      # up L2 pin 1's column, 4.5 mm
    _pc.union("DC_HS", "DC_HS band B.Cu, Q7 to L2", [_run, _leg])
    _pc.stitch("DC_HS", [_p for _p in _Q7S] + [(_lx - 1.0, _ly), (_lx, _ly), (_lx + 1.0, _ly)])
    print("power copper: DC_HS band from Q7's source pads at (%.1f, %.1f) to L2 pin 1 at (%.1f, %.1f)" % (_qx, _qy, _lx, _ly))
    print("power copper: DC_HS in three locked B.Cu bands from Q7's source pads to L2 pin 1")

# ---------------------------------------------------------------- the FET source lands (E36, 21 September 2026)
# rail_crossings under the one-land judge (03:50 CEST) declines four sites as busbar-class: six to ten amps enter a
# FET on three small source pads with ONE 0.20 mm fanout via each (DC_F at Q1, DC_HS at Q7, TRK_OUT at Q2, PV_P at
# U5), and fifteen barrels of the fanout's drill beside a 0.85 by 0.50 mm pad is a busbar. Board A's rail shape is
# the answer: an F.Cu ISLAND over the land (so the pad's current has copper beside it, which is what the conductor
# test judges) and a CLUSTER of the generator's own 0.5 mm drill (1.05 A a barrel at 10 K) in two rows west of the
# source column, inside the judge's window (half the land plus 1.0 mm from its centre). Q1 and Q2 are TDSON-8s
# (pads 1 to 3 at 1.27 mm, 0.85 by 0.50, the drain tab 4 mm east) and Q7 a PowerPAK SO-8 (1.27 by 0.61, the
# band's three 0.4 mm vias already in the pads). U5's PV_P land is pins 32 to 34 of a 0.5 mm QFN inside its
# own escape fan and its pockets have 0.0 mm of room (region_room, 20 September; E34's six open pins at U5):
# that site is the placement item E34 named and takes no copper here. Every site goes through stitch's own
# hole-to-hole and pad guards and a refusal is printed rather than raised, the E_SITES rule.
if _osx.environ.get("PLACE_FET_SOURCE_LANDS", "1") not in ("0", ""):
    _pcF = _pcmod.PowerCopper(board, net_for, P)
    _FET_LANDS = [
        # ref, net, amps typical/peak the land carries, barrels owed at 0.5 mm (barrels_for is asked below)
        ("Q1", "DC_F", 8.0), ("Q7", "DC_HS", 10.0), ("Q2", "TRK_OUT", 6.16),
    ]
    for _ref, _net, _amps in _FET_LANDS:
        try:
            _ps = [_padc(_ref, str(_k)) for _k in (1, 2, 3)]
            _cx = _ps[0][0]; _my = sum(_q[1] for _q in _ps) / 3.0
            # ONE column of up to five, 1.15 mm west of the source column at 0.85 mm pitch, which is INSIDE the judge's
            # window (each pad's half-size plus 1.0 mm from its centre; a second column 2.0 mm out is counted by
            # nothing, which the first probe measured: 'TRK_OUT at Q2: 3 there' with six laid). What the column
            # does not hold, rail_barrels lays in its own lattice inside the same window, site by site under the
            # chain's DRC (it topped Q2 up with three on that probe), so the count here is the room and not the need.
            _n = min(_pcF.barrels_for(_amps, 0.5), 5)
            _span = (_n - 1) * 0.85
            _pts = [(_cx - 1.15, _my - _span / 2.0 + 0.85 * _i) for _i in range(_n)]
            pour(pcbnew.F_Cu, _net, "%s island F.Cu at %s's source land" % (_net, _ref),
                 (_cx - 2.7, _my - 1.9, _cx + 0.7, _my + 1.9), priority=1)
            _pcF.stitch(_net, _pts, drill=0.5, width=0.9)
            print("power copper: %s island and %d barrel(s) of 0.5 mm at %s's source land (%.2f, %.2f) for %.2f A (%d owed at this drill)"
                  % (_net, len(_pts), _ref, _cx, _my, _amps, _pcF.barrels_for(_amps, 0.5)))
        except Exception as _e:
            print("power copper: %s at %s's source land REFUSED: %s" % (_net, _ref, _e))

ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
DEFAULT = (0.127, 0.25, 0.6, 0.3); cls(ns.GetDefaultNetclass(), *DEFAULT)   # 0.127: the 0.4 mm escape rows of the RP2040 (E6 round 4)
PATTERNS = [("DC_*", "PWR"), ("HS_S", "PWR"), ("GND", "PWR"), ("GND_V", "PWR"), ("VIN_RAW", "PWR"), ("PV_*", "PWR"), ("TRK_OUT", "PWR"), ("TRK_SW*", "SW"), ("TRK_LSENSE", "PWR"), ("+5V_E6", "PWR"), ("E6_SW", "SW"), ("CELL+", "BANK"), ("CELL_F", "BANK"), ("USB_E6_*", "USB")]
# SENSE: every net pcb_sensitive.yaml declares for this board, in a class of its own with the default geometry, listed ahead
# of the table so a sensitive net wins over the power pattern that also names it (TRK_LSENSE sat in PWR beside TRK_SW2, the net
# ANA-001 asks it to keep 0.50 mm from, and a class cannot be kept away from itself). The DSN class-pair clearance of
# route_one.sh (FR_CLASS_CLEAR, appendix 32.222) is what reads it (17 September 2026).
try:
    import yaml as _yaml, os as _os
    _sens = ((_yaml.safe_load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "pcb_sensitive.yaml"))) or {}).get("boards") or {}).get("e") or {}
    _sens_nets = [n["net"] for n in (_sens.get("nodes") if isinstance(_sens, dict) else _sens) or []]
except BaseException as _e:
    _sens_nets = []; print("SENSE class: pcb_sensitive.yaml not read (%s), no sensitive net moves class" % type(_e).__name__)
PATTERNS = [(n, "SENSE") for n in _sens_nets] + PATTERNS
print("SENSE class: %d declared sensitive net(s) take it" % len(_sens_nets))
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]   # 5 Sep 2026 (gateway finding, MESHSAT-802): root-sheet labels are "/NAME" on the board and KiCad's pattern matcher does not strip the slash, so every label pattern is emitted in both forms; power symbols (GND, +3V3) have no slash
try:
    CLASSES = [("PWR", 0.15, 0.8, 0.8, 0.4),
               ("BANK", 0.3, 3.0, 1.2, 0.6),
               ("SENSE", 0.127, 0.25, 0.7, 0.3),   # 0.7/0.3: a 0.20 mm ring, the annular floor this board declares; 0.6/0.3 left E12 with ten annular_width violations (18 September 2026)
               ("SW", 0.15, 0.8, 0.8, 0.4),   # the tracker's switching nodes, PWR's geometry in a class of their own so the SENSE class-pair rule names them and not the rail
               ("USB", 0.127, 0.3, 0.6, 0.3)]   # ONE table for the board's classes AND the project file's (18 September 2026): a second hand-written copy in the project file had drifted (D's PWR via 1.2/0.6 on the board, 0.8/0.4 in the file the router reads; SENSE absent from the file on D, E and P; SENSE 0.6/0.3 on P), the defect B fixed for itself on 8 September
    for _nm, *_v in CLASSES:
        _nc = pcbnew.NETCLASS(_nm); cls(_nc, *_v)
        if _nm == "USB": _nc.SetDiffPairWidth(FromMM(0.3)); _nc.SetDiffPairGap(FromMM(0.2))   # 8 Sep 2026 (32.71): 0.30/0.20 on the 7628 outer layer computes 89 ohm
        ns.SetNetclass(_nm, _nc)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
except Exception as e: print("note: net class API:", e)
# THE BARRELS REMEMBER THE LINE THAT PLACED THEM (20 September 2026). `barrel_sites --suggest` answers a
# site the generator already owns with "add N points to the call that placed it", and without this it can
# only give a coordinate: board E has THIRTEEN such sites and each call's arguments are expressions. The map
# is a sidecar beside the board, judged by nothing, and its absence costs a reader the line and nothing else.
_pcmod.PowerCopper(board, net_for, P).write_provenance(BOARD)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def C(name, prio, clr, tw, vd, vdr): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=0.3, diff_pair_gap=0.2)
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, *DEFAULT)] + [C(_nm, _i, *_v) for _i, (_nm, *_v) in enumerate(CLASSES)]
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
