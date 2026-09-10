#!/usr/bin/env python3
"""PCB-B phase B3 (B16 positions, appendix 32.58): bring the schematic netlist into the B16 mechanical board.
Usage: gen_pcb_b3.py <board.kicad_pcb> <netlist.net>
- reuses footprints already on the board by reference (J_LIME, the slots and holes)
- places the three receptacle pairs, the M.2 sockets, the bay and band connectors at planned case-frame positions, the small parts packed into regions
- creates nets, assigns pads, adds the GND plane (In1), the four 5 V plane zones (In4: one slot rail under each column, the device rail in the bands),
  the board-wide no-track rule areas on In1 and In4, the net classes; saves
"""
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
    name = uq(kids(n, "name")[0][1])
    nets[name] = [(uq(kids(nd, "ref")[0][1]), uq(kids(nd, "pin")[0][1])) for nd in kids(n, "node")]
print("netlist: %d components, %d nets" % (len(comps), len(nets)))

board = pcbnew.LoadBoard(BOARD)
existing = {fp.GetReference(): fp for fp in board.GetFootprints()}
LIBS = "/usr/share/kicad/footprints/"
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
    fp.Reference().SetVisible(ref[0] in "UJT" and not ref.startswith("JP") and not ref.startswith("TP")); fp.Value().SetVisible(False)
    fp.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); fp.Reference().SetTextThickness(FromMM(0.12))
    fp.SetPosition(P(x, y)); board.Add(fp)
    if back: fp.Flip(P(x, y), False)
    fp.SetOrientationDegrees(rot); centre_on(fp, x, y)
    if ref in FIXED:
        bb = fp.GetBoundingBox(False, False)
        print("  %-10s centred at (%.1f, %.1f) size %.1f x %.1f %s" % (ref, (bb.GetLeft() + bb.GetRight()) / 2e6 - OX, OY - (bb.GetTop() + bb.GetBottom()) / 2e6, bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, "BACK" if fp.IsFlipped() else ""))
    return fp
# --- fixed positions (case frame), appendix 32.58: the receptacle pairs 17 mm off each module centre and 2.5 mm south of it; the M.2 sockets at Y 25 with the
#     cards extending south (S2's NVMe along +X at the column's south end because the 3052 5G card takes the height); J_AB1 flipped over A22's header;
#     the bay and band connectors (KiCad horizontal receptacles open toward local +y, the Molex HDMI toward local +x; a positive rotation is counter-clockwise); the HDMI receptacle at the south-east corner opening south, its switches at the north-east;
#     the fan headers west of each module; the flashing USB-C receptacles on the south edge opening south (rot 0)
FIXED = {"U30A": (-89.5, 57.5, 0), "U30B": (-55.5, 57.5, 0), "U31A": (-19.5, 57.5, 0), "U31B": (14.5, 57.5, 0), "U32A": (50.5, 57.5, 0), "U32B": (84.5, 57.5, 0),
         # M.2 sockets: place() centres the socket-plus-card box, so the target sits 13.65 (2230), 19.65 (2242) or 24.65 (3052) mm south of the socket body centre at Y 25
         "J_M2N1": (-85, 5.35, 0), "J_M2C1": (-57, 11.35, 0), "J_M2C2": (-20, 0.35, 0), "J_M2N2": (-9.35, -85, 90), "J_M2N3": (48, 5.35, 0), "J_M2C3": (79, 11.35, 0),
         "J_SIM1": (4.5, 22, 0), "J_SIM2": (4.5, 1, 0),
         "J_FLASH1": (-92.5, -95, 0), "J_FLASH2": (24, -95, 0), "J_FLASH3": (39.5, -95, 0), "J_5V_S1": (-92.5, -84.5, 0), "J_5V_S2": (27, -84, 0), "J_5V_S3": (39.5, -84.5, 0),
         "J_FAN1": (-97.5, 45, 90), "J_FAN2": (-27.5, 45, 90), "J_FAN3": (92.5, 44, 90),
         "J_AB1": (113, -46, 0), "J_ETH": (-152, 89.5, 180), "J_HDMI": (104.5, -93, 270), "J_PANEL": (-116, 92, 90), "T1": (-152, 68, 0),
         "U3": (100.5, 89, 0), "U4": (116.5, 89, 0),   # B17: the HDMI switches at 16 mm pitch (32.65)
         "U12": (111, 47.5, 0), "U13": (133.5, 84, 180), "U14": (154.5, 84, 180), "J_RB9704": (100.5, -56, 0)}
BACK = {"J_AB1"}
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
# --- reuse existing footprints (J_LIME comes from the mechanical stage with its slots)
for ref in comps:
    if ref in placed: continue
    if ref in existing:
        fp = existing[ref]; val, fpid = comps[ref]
        if fp.GetFPIDAsString().split(":")[-1] != fpid.split(":")[-1]: print("NOTE %s footprint differs: board %s vs schematic %s" % (ref, fp.GetFPIDAsString(), fpid))
        fp.SetValue(val); placed[ref] = fp
# --- regions for the rest: (x0, y0, x1, y1), refs. Slot refs are numbered 100 s + k (gen_sch_b.py); the column bands of gen_pcb_b.py (S1 -98..-38, S2 -36..32, S3 34..94)
def R(s, k): return "R%d" % (100 * s + k)
def C(s, k): return "C%d" % (100 * s + k)
def Cs(s, a, b): return ["C%d" % (100 * s + k) for k in range(a, b + 1)]
def Rs(s, a, b): return ["R%d" % (100 * s + k) for k in range(a, b + 1)]
COL = {1: (-98, -38), 2: (-36, 32), 3: (34, 94)}
REGIONS = []   # (name, rect, refs, back): decoupling and pull-ups on the UNDERSIDE (B16 is assembled on both sides), never beneath a fine-pitch part whose escapes need the vias
for s in (1, 2, 3):
    x0, x1 = COL[s]; U = lambda k: "U%d" % (100 * s + k); Q = lambda k: "Q%d" % (100 * s + k); L = lambda k: "L%d" % (100 * s + k)
    sw_dec = Cs(s, 35, 48)                                                     # the switch's twelve 100 nF (the exposed pad's fanout via needs the centre, so they sit under the rail band)
    # 9 September 2026 (ARCH-PCB-B-IOHA): the bank's two host-selection switches sit beside the hub they feed, and their
    # decoupling and the two pull-downs that hold the safe state go with the hub's own back-side group.
    sw_b = Cs(s, 59, 60) + Cs(s, 63, 74) + Cs(s, 92, 94) + Rs(s, 41, 47) + Rs(s, 60, 61)   # hub caps, USB coupling, hub straps, the fabric's decoupling and its two safe-state pull-downs
    if s == 1: sw_b += Cs(1, 61, 62)
    straps = Rs(s, 17, 34)
    rail = [U(3), U(4), L(1), L(2), U(5), U(6), L(3), L(4)] + Cs(s, 11, 16) + Cs(s, 18, 23) + Cs(s, 25, 27) + Cs(s, 30, 32) + Cs(s, 49, 49) + Cs(s, 57, 57) + ["LED%d4" % s]
    rail_b = Rs(s, 2, 16) + [C(s, 17), C(s, 24), C(s, 28), C(s, 29), C(s, 33), C(s, 34), C(s, 50), C(s, 58), R(s, 35), R(s, 36)]
    sup = [U(7), "J_RPIBOOT%d" % s, "J_DBG%d" % s, Q(1), Q(2), Q(3), Q(4), Q(5), "D%d" % (100 * s + 1)] + Cs(s, 1, 8) + ["LED%d1" % s, "LED%d7" % s, "LED%d6" % s]
    sup_b = [R(s, 52), R(s, 53), R(s, 1), R(s, 49), R(s, 50), R(s, 48), R(s, 51)] + Rs(s, 54, 58) + Cs(s, 9, 10)
    eth = Cs(s, 75, 82)
    card = {1: ["Q106", "LED15"], 2: ["Q206", "Q207", "Q208", "LED25"], 3: ["Q306", "LED35"]}[s]
    card_b = {1: [R(1, 37), R(1, 38), R(1, 39)], 2: [R(2, 37), R(2, 38), R(2, 40), R(2, 39)] + Cs(2, 86, 91), 3: [R(3, 37), R(3, 38), R(3, 39)]}[s]
    if s == 2:
        REGIONS += [("S2_SWIC", (-36, -57, 10, -30), [U(1), U(2), U(9), U(10)], False),
                    ("S2_SWE", (10, -57, 32, -30), ["Y201"] + card + eth + ["LED22", "LED23"], False), ("S2_SWEB", (-36, -57, 32, -30), sw_b + card_b + sup_b, True),
                    ("S2_RAIL", (-36, -73.4, 32, -57), [r for r in rail if r not in (U(5), U(6), L(3), L(4)) and r not in Cs(2, 25, 27) + Cs(2, 30, 32)], False), ("S2_RAILB", (-36, -73.4, 32, -57), rail_b + straps + sw_dec, True),
                    ("S2_SUP", (12, -30, 32, 28), sup + ["J_USBX", "U36", "J_GNSS2"], False), ("S2_SUP2", (-3, -30, 12, -8), [U(5), U(6), L(3), L(4)] + Cs(2, 25, 27) + Cs(2, 30, 32), False)]
    else:
        REGIONS += [("S%d_SWIC" % s, (x0, -52, x0 + 43, -21), [U(1), U(2), U(9), U(10), "Y%d" % (100 * s + 1)], False),
                    ("S%d_SWE" % s, (x0 + 43, -52, x1, -21), card + eth + ["LED%d2" % s, "LED%d3" % s], False), ("S%d_SWEB" % s, (x0, -52, x1, -21), sw_b + card_b + sup_b, True),
                    ("S%d_RAIL" % s, (x0, -70, x1, -52), rail, False), ("S%d_RAILB" % s, (x0 + 14, -70, x1, -52), rail_b + straps + sw_dec, True),
                    ("S%d_SUP" % s, (x0 + 12, -97, x1, -70), sup + (["J_SPI3"] if s == 3 else []), False)]
# 9 September 2026 (ARCH-PCB-B-IOHA section 6): the I/O control plane goes on the UNDERSIDE, and the three controllers
# go in three SEPARATE pockets rather than one band. Two reasons, both measured on the board. First, a single rect
# across the module bay puts parts under the six CM5 receptacles (0.4 mm rows at Y 47.7 to 67.3, escape vias at the pad
# tips) and over the twelve M2.5 standoff holes at Y 36 and Y 84, which is exactly what the underside rule forbids.
# Second, three controllers in one pocket is one failure domain again: a screw, a crack or a solder wash takes all
# three. The pockets are the two gaps between the module columns (X -52 to -23 and 18 to 47, clear of every socket and
# hole) and the free underside of the QMX bay (X -158 to -129, clear of its four strap slots at Y 20, -40 and -67.5).
# The voters and the small logic sit in the band north of the receptacles and south of the standoff row, Y 69 to 80.5.
def _ioc(k):
    return (["U%d" % (40 + 10 * k + n) for n in range(5)] + ["Y%d" % (2 + k), "LED%d" % (40 + k)]
            + ["C%d" % (400 + 20 * k + n) for n in range(12)]
            + ["R%d" % (63 + 12 * k + n) for n in range(3)])
# The voted logic goes in ONE pocket, with controller A on the free underside of the QMX bay, which is 57 x 56 mm there
# against the 29 x 56 of the two gaps between the module columns. Splitting it three ways (the first attempt) put three
# or four TSSOP-14 quads into each 1624 mm2 pocket beside an LQFP-100 and the predictor answered with 17 collisions,
# most of them the quads' own fans. Concentrating the voters is not a failure-domain regression: the FMEA already
# names them as common mode, and what has to stay separate is the three CONTROLLERS, which it does.
VOTE_PARTS = (["U%d" % n for n in range(70, 80)] + ["U80"] + ["C%d" % n for n in range(470, 480)]
              + ["C480", "C481", "C482", "C483"] + ["R474", "R475", "R476"]
              + ["Q3", "Q4", "Q5", "R477", "R478", "R479"]
              + ["R%d" % n for n in range(480, 501)])
# each CAN fabric is terminated at its two PHYSICAL ends, which are controller A in the west pocket and controller C in
# the east one; a bus terminated once, in the middle, reflects off both ends (caught reading the placement, 9 Sep 2026)
REGIONS += [("IOCA", (-160.0, -60.0, -103.0, -4.0), _ioc(0) + VOTE_PARTS + ["R470", "R471", "R472", "R473", "C460", "C461"], True),
            ("IOCB", (-52.0, 32.0, -23.0, 88.0), _ioc(1), True),
            ("IOCC", (18.0, 32.0, 47.0, 88.0), _ioc(2) + ["R504", "R505", "R506", "R507", "C506", "C507"], True),

            ("WIFISW", (132.0, -20.0, 159.0, 10.0),
             ["U82", "U83", "J_W1A", "J_W3A", "J_WOA", "J_W1B", "J_W3B", "J_WOB", "R510", "Q10"] + ["C%d" % n for n in range(500, 506)], True)]
REGIONS = [(_n, _rect, [_r for _r in _refs if _r in comps or not _n.startswith("IO")], _bk) for _n, _rect, _refs, _bk in REGIONS]
REGIONS += [
 ("NORTH1", (-94, 88.5, -52, 97.5), ["TP%d" % k for k in range(1, 21)], False),
 ("NORTH2", (-23, 88.5, 18, 97.5), ["TP%d" % k for k in range(21, 32)] + ["LED6", "LED7", "LED8", "LED9"], False),
 ("NORTH3", (47, 88.5, 88, 97.5), ["TP%d" % k for k in range(41, 52)], False),
 ("ETH",   (-162, 30, -122, 59), ["U1", "Y1", "C14", "C15", "R3", "R57"] + ["C%d" % k for k in range(17, 29)], False),
 ("POE",   (-140.5, 59, -122, 86), ["U5", "Q1", "R12", "R13", "C31", "C32"], False),
 ("POEB",  (-140.5, 59, -122, 70), ["C33", "R9", "R10", "C29", "C30"], True),
 ("WNE",   (-121, 29, -102, 68), ["U25", "L1", "C3", "C4", "C5", "C6", "U26", "L2", "C7", "C8", "C9", "C10", "C11", "R1", "R2", "U27", "C12", "C13", "J_5V_DEV"], False),
 ("GAP12", (-50, 33, -32, 97), ["U6", "U7", "U19", "U20", "U29", "U37", "C65", "C66", "C67", "C68", "R49", "R50", "R51", "R52", "R53", "R58", "R59", "R60", "R61", "R62", "R54", "R55", "R56", "F1", "R5", "R6", "R7", "R8", "LED1", "LED2", "LED3", "LED4", "Q2", "R4", "C16"], False),
 ("GAP23", (19, 33, 44, 97), ["BT1", "U11", "R21", "R22", "R23", "L3", "C40", "C41", "C42", "J_GNSS1", "U8", "U9", "U10", "C69", "C70", "C71"], False),
 ("WMIDS", (-152, -97, -116, -69), ["U35", "D1", "D2", "J_54V", "J_QMX", "F3", "C34", "C35", "C1", "C2", "C36", "R11"], False),
 ("NEX",   (96, 78, 123, 82), ["R14", "R15", "R16", "C37", "C38"], False),   # B17 (8 Sep 2026, 32.65): the two HDMI switches U3 and U4 are FIXED at 16 mm pitch above this strip (9.6 mm in the packed row collided their escape fans)
 ("SEX",   (96, -85, 112, -78), ["F2", "C39"], False),
 ("SEXB",  (96, -85, 112, -78), ["R17", "R18", "R19", "R20"], True),
 ("RADE",  (125.5, 45.5, 162, 67), ["R25", "R28", "R29", "R30", "R31", "R32", "R33", "R34", "R35", "J_ZBDBG1", "J_ZBDBG2", "J_LORA1", "U28", "U34", "J_CAM"], False),
 ("RBX2",  (96, -44, 110, -26), ["C45", "C46", "C47", "C52", "C53", "C54", "C55", "F4", "C64", "R47", "R48"], False),
 ("RBX",   (96, -25, 126, 27), ["U23", "C56", "R36", "R37", "R38", "R39", "C57", "C58", "U33", "U24", "C61", "R43", "R44", "R45", "R46", "C62", "C63", "U18", "R40", "C59", "C60", "R41", "R42", "U15", "U16", "U17", "R24", "C43", "C44", "R26", "C48", "C49", "R27", "C50", "C51", "U21", "U22"], False),
]
GAP = 1.2
# 10 September 2026: the room the packer leaves around a fine-pitch part is a knob, because place_audit's own envelope
# (2.2 mm plus 0.12 per pad on a side) wants about 5 mm at a 99-pad QFN and this gives 1.6, which is why B19's audit
# reports a third of the pads of U301, U201 and U101 with no escape at all. PLACE_FINE_MARGIN measures the trade against
# the region overflow the gate refuses.
FINE_MARGIN = float(os.environ.get("PLACE_FINE_MARGIN", "1.6"))
import re as _re
def is_fine(fp):
    if _re.search(r"SOT-23-[68]|SOT-583|TSOT-23-6", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
_all = [r for _, _, refs, _ in REGIONS for r in refs] + list(FIXED)
_dups = sorted({r for r in _all if _all.count(r) > 1})
if _dups: raise SystemExit("reference listed twice in the placement (two footprints per reference make the DSN export refuse the board): %s" % _dups)
# --- a differential pair's two series parts are packed as a couple (8 Sep 2026, MESHSAT-862; the D9 rule of 32.68). The shelf packer put
# them in a row 3.1 mm apart, so the pre-router had to splay a 0.27 mm pair to 3.1 mm at the station and 63 of B17's 76 pair failures were
# exactly that. A couple is two two-pad passives whose nets are each other's _P and _N counterparts, so it is read from the netlist and
# needs no table: they land one above the other at the packer's own gap, pads across the pair axis, and the pair enters both pad 1s.
_pins_of = {}
for _n, _nodes in nets.items():
    for _r, _pin in _nodes: _pins_of.setdefault(_r, {})[_pin] = _n
_twopad = {r: tuple(sorted(v.values())) for r, v in _pins_of.items() if len(v) == 2 and r[:1] in ("C", "R", "L")}
COUPLE = {}
_byn = {}
for _r, _nn in _twopad.items(): _byn.setdefault(_nn, []).append(_r)
for _r, _nn in _twopad.items():
    if _r in COUPLE or not all(x.endswith("_P") for x in _nn): continue
    _want = tuple(sorted(x[:-2] + "_N" for x in _nn))
    for _o in _byn.get(_want, []):
        if _o != _r: COUPLE[_r] = _o; COUPLE[_o] = _r; break
print("placement: %d differential-pair couples packed side by side" % (len(COUPLE) // 2))

REGIONS = [(_n, _rect, [_r for _r in _refs if _r not in RESERVED], _bk) for _n, _rect, _refs, _bk in REGIONS]   # a reserved capacitor is placed already
for name, (x0, y0, x1, y1), refs, back in REGIONS:
    fps = []
    for ref in refs:
        if ref not in comps: print("WARNING %s not in netlist" % ref); continue
        if ref in placed: print("WARNING %s listed twice" % ref); continue
        fp = place(ref, 0, 0, back=back); bb = fp.GetBoundingBox(False, False); fine = is_fine(fp); mx = my = 0.0
        if fine:
            # 10 September 2026: the wide margin is for the QFN and QFP rows whose escape vias splay far (the PCIe switches,
            # the hubs, the supervisors); a SOT or a USON keeps 1.4, which is the rule gen_pcb_c3.py and gen_pcb_e3.py already
            # had and this generator did not. Measured on B19 by counting the pads place_audit finds with no escape at all:
            # a flat 1.6 leaves 194 of them, a flat 2.6 leaves 69, a flat 3.0 leaves 164 (the packer spills into other regions).
            nfine = sum(1 for pd in fp.Pads() if pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and min(pd.GetSize().x, pd.GetSize().y) <= FromMM(1.2))
            fm = FINE_MARGIN if nfine >= 16 else 1.4
            for pd in fp.Pads():
                if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or min(pd.GetSize().x, pd.GetSize().y) > FromMM(1.2): continue
                pbb = pd.GetBoundingBox(); w_, h_ = pbb.GetWidth(), pbb.GetHeight()
                if w_ > h_ * 1.2: mx = 2 * fm
                elif h_ > w_ * 1.2: my = 2 * fm
            if mx == 0.0 and my == 0.0: mx = my = 2 * fm
        fps.append((ref, fp, bb.GetWidth() / 1e6 + GAP + mx, bb.GetHeight() / 1e6 + GAP + my, fine))
    # merge each couple whose two parts are both in this region into one unit, stacked, before the shelf packer sees them
    _here = {t[0]: t for t in fps}; units = []; _done = set()
    for ref, fp, w, h, fine in fps:
        if ref in _done: continue
        o = COUPLE.get(ref)
        if o and o in _here and o not in _done:
            _, fp2, w2, h2, f2 = _here[o]; _done.add(ref); _done.add(o)
            units.append(([(ref, fp, h), (o, fp2, h2)], max(w, w2), h + h2, fine or f2))
        else:
            _done.add(ref); units.append(([(ref, fp, h)], w, h, fine))
    units.sort(key=lambda t: (not t[3], -(t[1] * t[2])))
    cx, cy, rowh = x0, y1, 0.0
    for members, w, h, fine in units:
        if cx + w > x1 + 0.01:
            cx = x0; cy -= rowh; rowh = 0.0
        dy = 0.0
        for ref, fp, hi in members:
            centre_on(fp, cx + w / 2, cy - dy - hi / 2); placed[ref] = fp; dy += hi
        cx += w; rowh = max(rowh, h)
    if cy - rowh < y0 - 0.01: print("WARNING region %s overflows by %.1f mm" % (name, (y0 - (cy - rowh))))
missing = [r for r in comps if r not in placed and not r.startswith("#")]
if missing: raise SystemExit("unplaced: %s" % missing)
# --- nets
ni = board.GetNetInfo()
def net_for(name, create=True):
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
# --- planes: In1 GND; In4 the four 5 V rails (one slot rail under each column and its module, the device rail in the bands); nothing on the outer layers
def plane(layer, netname, name, rect, priority=0):
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
plane(pcbnew.In1_Cu, "GND", "GND plane In1", (-165, -100, 165, 100))
plane(pcbnew.In4_Cu, "+5V_S1", "+5V_S1 plane In4 (column S1)", (-100, -100, -37, 100))
plane(pcbnew.In4_Cu, "+5V_S2", "+5V_S2 plane In4 (column S2)", (-35, -100, 33, 100))
plane(pcbnew.In4_Cu, "+5V_S3", "+5V_S3 plane In4 (column S3)", (35, -100, 96, 100))
plane(pcbnew.In4_Cu, "+5V_DEV", "+5V_DEV plane In4 (west band)", (-165, -100, -102, 100))
plane(pcbnew.In4_Cu, "+5V_DEV", "+5V_DEV plane In4 (east band)", (98, -100, 165, 100))
_bb = board.GetBoardEdgesBoundingBox()
for _L, _label in ((pcbnew.In1_Cu, "In1 (solid ground plane)"), (pcbnew.In4_Cu, "In4 (5 V planes)")):
    _z = pcbnew.ZONE(board); _z.SetIsRuleArea(True); _z.SetDoNotAllowTracks(True); _z.SetDoNotAllowVias(False); _z.SetDoNotAllowCopperPour(False); _z.SetDoNotAllowPads(False); _z.SetDoNotAllowFootprints(False)
    _z.SetLayer(_L); _z.SetZoneName("keep tracks off " + _label); _o = _z.Outline(); _o.NewOutline()
    for _x, _y in ((_bb.GetLeft(), _bb.GetTop()), (_bb.GetRight(), _bb.GetTop()), (_bb.GetRight(), _bb.GetBottom()), (_bb.GetLeft(), _bb.GetBottom())): _o.Append(_x, _y)
    board.Add(_z)
print("track keep-outs over the whole board on In1 and In4 (planes); In2 and In3 route")
# --- net classes (API first; the project JSON is re-applied after the save because SaveBoard rewrites it)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr, dpw, dpg):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr)); nc.SetDiffPairWidth(FromMM(dpw)); nc.SetDiffPairGap(FromMM(dpg)); nc.SetDiffPairViaGap(FromMM(0.25))
cls(ns.GetDefaultNetclass(), 0.127, 0.25, 0.7, 0.3, 0.2, 0.15)
CLASSES = {"USB": (0.127, 0.127, 0.7, 0.3, 0.127, 0.13), "DIFF100": (0.127, 0.127, 0.7, 0.3, 0.127, 0.20),   # 8 Sep 2026 (32.71): on the 3313 outer layers 0.127/0.127 computes 94 ohm and 0.127/0.20 computes 101 ohm; the pairs run on F.Cu and B.Cu over the In1 and In4 grounds
            "PWR": (0.127, 0.4, 0.8, 0.4, 0.4, 0.25), "HV": (0.18, 0.5, 0.8, 0.4, 0.5, 0.5)}   # HV 0.18: above the 0.2 pad gap of the TSSOP-28 PoE controller it fails inside the part
PATTERNS = [("USB*", "USB"), ("HUB*", "USB"), ("LIME_SS*", "USB"), ("LIME_D*", "USB"), ("CAM_D*", "USB"), ("QMX_D*", "USB"), ("HOST*", "USB"), ("BANK*", "USB"), ("MUX*", "USB"), ("SW?_O*", "USB"), ("SW?_IN", "USB"), ("W?*_CARD", "USB"), ("W?_ANT", "USB"), ("GNSS_D*", "USB"), ("ZBA_D*", "USB"), ("ZBB_D*", "USB"), ("RB_D*", "USB"),
            ("PCIE*", "USB"), ("NVME*_RX_*", "USB"), ("NVME*_TX_*", "USB"), ("NVME*_CLK_*", "USB"), ("CARD*_RX_*", "USB"), ("CARD*_TX_*", "USB"), ("CARD*_CLK_*", "USB"),
            ("HDMI*_D*", "DIFF100"), ("HDMI*_CK_*", "DIFF100"), ("ETH*", "DIFF100"), ("SWP*", "DIFF100"),
            ("MDI_*", "HV"), ("POE_*", "HV"), ("+54V_POE", "HV"),
            ("+5V_*", "PWR"), ("+3V3_*", "PWR"), ("+1V*", "PWR"), ("+2V5*", "PWR"), ("PANEL_5V", "PWR"), ("VBUS*", "PWR"), ("GND", "PWR"), ("*_SW", "PWR"), ("VBAT", "PWR")]
PATTERNS += [("/" + pat, cls_) for pat, cls_ in PATTERNS if not pat.startswith("/")]
# A net class clearance below the board minimum never applies: KiCad enforces the minimum as a floor while the router takes the class value
# from the DSN, so every pair laid at that spacing is a violation (A23, 25 of them, 9 Sep 2026 02:10; MESHSAT-862).
_minclr = board.GetDesignSettings().m_MinClearance / 1e6
_bad = {n: v[0] for n, v in CLASSES.items() if v[0] < _minclr - 1e-9}
if _bad: raise SystemExit("net class clearance below the board minimum %.3f mm: %s" % (_minclr, _bad))
try:
    for name, vals in CLASSES.items():
        nc = pcbnew.NETCLASS(name); cls(nc, *vals); ns.SetNetclass(name, nc)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
    print("net classes set via API")
except Exception as e:
    print("note: net class API:", e)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def Cc(name, prio, clr, tw, vd, vdr, dpw, dpg): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=dpw, diff_pair_gap=dpg)
    d.setdefault("net_settings", {})["classes"] = [Cc("Default", 2147483647, 0.127, 0.25, 0.7, 0.3, 0.2, 0.15), Cc("USB", 0, 0.10, 0.127, 0.7, 0.3, 0.127, 0.127), Cc("DIFF100", 1, 0.10, 0.127, 0.7, 0.3, 0.127, 0.20), Cc("PWR", 2, 0.127, 0.4, 0.8, 0.4, 0.4, 0.25), Cc("HV", 3, 0.18, 0.5, 0.8, 0.4, 0.5, 0.5)]
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
