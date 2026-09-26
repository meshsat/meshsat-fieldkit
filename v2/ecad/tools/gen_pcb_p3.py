#!/usr/bin/env python3
"""PCB-P PACK BMS P1 (MESHSAT-830, appendix 32.62): bring the netlist onto the mechanical board of gen_pcb_p.py, fix the power path and the connectors, pack the
gauge and its filters, lay the locked 2 oz bands of the power path on both layers, pour the ground on the underside and set the net classes.
Usage: gen_pcb_p3.py <board.kicad_pcb> <netlist.net>. Board frame: origin at the board centre, +X along the pack.
The power path never travels in router tracks (the A21 rule of 32.39): B+ land > blade holder > chemical fuse (round 4) > charge FET > discharge FET > pack + land along the north edge
and B- land > shunt > pack - land along the south edge are 4 mm locked tracks on F.Cu and B.Cu with stitch vias; the router connects the small-signal
pads to them."""
import sys, re, math, os, pcbnew
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
# ---------------------------------------------------------------- fixed parts (board mm, rot, back): the power path along the north edge, the shunt along the south edge, the leads at the edges
# ROUND 4 OF REVIEW D (MESHSAT-1357, 26 September 2026). Four things moved, each forced by a schematic change, and check_pcb_p.py's SITES
# table (not this author's file) still names the old numbers, so its Q1, Q2 and J_TS lines fail until its owner follows:
#   * F2, the chemical fuse (decision 40 / D-15), goes where TI puts it, between the blade and the charge FET (SLUSC67B Figure 21). Its
#     fuse element runs ACROSS the 9.5 x 5.0 mm body, so it is turned 90 degrees and costs 6.4 mm of the path: F2 at x -3.9, Q1 from x 0
#     to 5.3 and Q2 from 8 to 13.3 (their 8 mm spacing kept), W_P where it was. Q1's source tracks and their six barrels now sit between
#     F2 and Q1. FIX-UP OF 26 SEPTEMBER 2026: F2 is the Eaton SCF9550-30-05 on Eaton's own recommended pad layout (ELX1135 page 3), whose
#     pins are 1 and 2 the fuse ends and 3 the heater: pin 1 west on FUSED, pin 2 east on SCP_OUT, the heater pin 3 south towards Q3.
#     Its heater land reaches 1.2 mm past the body, so its courtyard is 11.35 mm long where the Dexerials draft's was 10.4: the courtyard
#     is centred at y 16.05 (10.375 to 21.725, clear of GAUGE's C2 at 10.22 and F1 at x -7.31); SEC's top edge is 5.7, below the
#     fixed Q3 (fix-up of 26 September 2026; 10.3 in the first fix-up draft, 10.6 in the first pass).
#   * J_TS is a five-way socket (F-PK-02: four thermistors and their return), 13 mm long, which fits neither the east edge between J_SMB
#     and H2's keep-out nor its old site, so it lies along the south-east at (26.8, -12.7). (J_TS2, the second level's own thermistor
#     socket of the first pass, is gone at the fix-up: U2's TS pin is held by the fixed 10 kohm R33, gen_sch_p.py.)
#   * RT1, the PTC element, and its capacitor C13 are FIXED under the gap between Q1 and Q2, because TI's note 2 asks for the element
#     "close to Q2 and Q3" (the protection FETs) and the region packer places by size, not by neighbour.
#   * Q3, the heater switch, and R32, its gate pull-down, are FIXED directly under F2 (fix-up of 26 September 2026). Q3 is turned 90
#     degrees so its drain pad faces north and sits about 1 mm below F2's heater pad. What that measures is ONE segment of the heater
#     loop, SCP_HTR from F2's pin 3 to Q3's drain (pin 3), about 1 mm pad to pad instead of about 10 mm when the packer set Q3 below
#     U2 (second fix-up of 26 September 2026, re-review: the first wording called it the loop). The heater current, 1.3 to 3.5 A for
#     up to 60 s while the SCF opens, returns from Q3's source (pin 2, GND, on F.Cu) to the B.Cu ground and on to W_BN, and that
#     return is the router's: this board has no top-side ground pour, and the ground class would give it one 0.6/0.3 mm via. The
#     route brief (drafts/r4-decisions.md O-11 and O-14) asks for at least five 0.3 mm or four 0.4 mm barrels at Q3's source, the
#     tree's own via_current.barrels_for(3.5 A) at 10 K and 18 um plating (steady state, so conservative for a 60 s pulse). It also
#     takes Q3, the largest part in SEC, out of the packer, which put it between U2 and U2's own filters (the review's point below).
FIXED = {"W_BP": (-27, 12.5, 0, False), "F1": (-15.6, 15, 0, False), "F2": (-3.9, 16.05, 90, False), "Q1": (5.3, 15, 0, False), "Q2": (13.3, 15, 180, False), "W_P": (26, 12.5, 0, False),
         "W_BN": (-27, -12.5, 0, False), "R10": (-18, -15, 0, False), "W_N": (-8, -13.5, 0, False),
         "J_CELL": (12, -17.5, 0, False), "J_TS": (26.8, -12.7, 0, False), "J_SMB": (30.5, 2, 90, False),
         "RT1": (9.3, 11.0, 0, False), "C13": (12.0, 11.0, 0, False),
         "Q3": (-2.3, 7.9, 90, False), "R32": (1.6, 8.3, 0, False)}
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
for ref, x, y in (("B+", -27, 16.2), ("F1 25A", -15.6, 19.6), ("CHG", 5.3, 18.6), ("DSG", 13.3, 18.6), ("PACK+", 26, 16.2), ("B-", -27, -16.2), ("2m", -18, -18.4), ("PACK-", -8, -17.2), ("TAPS", 12, -21.2), ("NTC", 26.8, -9.3), ("SMB", 30.5, 10.5)):
    text(ref, x, y, pcbnew.F_SilkS, 0.8, 0.14)
# ---------------------------------------------------------------- packed regions (name, rect, refs, back): the gauge and its filters in the middle, the gate networks and ESD east, the test points west
# ROUND 4 (26 September 2026): the regions are redrawn around the new parts, which is a floor-plan change on the reserved list
# (reserved.json, "region definitions in the packer") taken by the session under the owner's standing rule of 26 September 2026 and
# recorded in drafts/r4-decisions.md with the room each region had before and has now. Each rectangle is sized in whole rows of the
# packer's own cells (an 0603 is a 4.25 x 2.75 mm cell with the 1.2 mm gap; U1's RSM land with its 2.2 mm fan margin a 10.8 mm square),
# so none overflows, and each is clear of the fixed parts' courtyards: W_BP and W_BN at x -24.4, F1 above y 11.3, F2 above 10.9, W_N
# right of x -5.45 below -10.95, J_CELL right of x 4.0 below -14.1, J_TS and J_SMB, and H1 and H2's keep-outs.
#   GAUGE  the gauge and its filters (U1, C1..C9, R1..R9): 19.65 wide for U1, C1 and one 0603 in the first row and four 0603 in the next four
#   SEC    the second level with ALL of its RC filters (U2, RVD R23 and CVD C14, RIN R24..R27 and the CIN ladder C15..C18) and its TS
#          resistor R33, a column from under the fixed Q3 to the south edge. The list is in the order the pairs should sit under U2
#          (VDD first, then V4 to V1, R33 last): the packer sorts by size and keeps list order among equals, so each RC pair lands in
#          the rows directly below U2 (about 5 to 16 mm from it in this 8.5 mm column; the pin-adjacent placement is the 4-layer
#          regeneration's, open item O-11). FIX-UP OF 26 SEPTEMBER 2026 (review minor): the first pass
#          put RIN and RVD in EAST, 20 to 25 mm from U2, where SLUSEG7D 8.4.1 asks for "the RC filters for the Vn and VDD pins ... as
#          close as possible to the target terminal"; they swap places with the fuse divider, which has no layout rule of its own
#          (SLUSC67B 8.2.2.2.5 keeps C19 only for RFI immunity) and whose inputs are slow logic levels.
#   SIG    the gate networks, the terminal and SMBus clamps, the under-voltage hold (Q5, R28) and PRES
#   EAST   the fuse divider (R29, R30, R31, C19) and the arming jumper JP1, and PRES's series resistor R22 by the SMBus socket. So
#          FUSE_GQ runs from JP1 in the east to Q3 and R32 (north centre) and to TP14 (south-west), a board-crossing gate net held
#          only by R32's 1 Mohm while JP1 is open, and C19, the gate's RFI capacitor once JP1 is closed, sits at the far end of it.
#          SLUSC67B 8.2.2.2.5 lets that capacitor go because the fuse is slow, so this is no function risk, but it undoes the purpose
#          TI gives it: JP1 and C19 move beside Q3 when the regions are next redrawn, at the 4-layer regeneration (O-11).
#   TPS    ten test points along the west edge, as before; TPS2 four more under R10 and W_N (TP11 to TP14; TP14 on FUSE_GQ added at the
#          fix-up of 26 September 2026, so the arming jumper's closure is measured; TP13 moved here from SEC at the same fix-up; TPS2
#          runs east under W_N's courtyard, which ends at y -16.0, to x -4.55, GAUGE's east edge, clear of SEC)
#          THE ORDER IS A SAFETY CHOICE (second fix-up of 26 September 2026, re-review). The packer lays equal sizes in list order, west
#          to east, at a 3.75 mm pitch with 1.5 mm pads, so neighbours are 2.25 mm apart and a slipped probe bridges them. The fix-up's
#          order (TP11, TP12, TP13, TP14) put TP14, Q3's gate, beside TP13, the cell node at 10 to 16.8 V: a bridge there fires F2 with
#          JP1 open and puts up to 16.8 V on a +-12 V gate, in the very row the TP11-to-TP14 arming check probes. Now it is TP14, TP11,
#          TP12, TP13. TP14 is at the west end and its only test-point neighbour is TP11, the other side of JP1: a bridge there is a
#          closure, harmless once TP11 has been read low (the commissioning order, gen_sch_p.py JP1), and the check's two probes sit
#          side by side. With four in a row and TP11 beside TP14, one of that pair must have TP12 or TP13 as its other neighbour; here
#          it is TP11, which reaches Q3's gate only through a closed JP1, and its neighbour is TP12 (SEC_DOUT), which sits at VSS unless
#          the second level holds an under-voltage or sees an open wire, never TP13. TP13 takes the east end, beside TP12 only: a bridge
#          there puts at most 16.8 V on DOUT (rated to 45 V, SLUSEG7D 6.1) and on Q5's gate (+-20 V, JCET 2N7002), which turns Q5 on and
#          holds the discharge FET off, a recoverable state. Measured on the placed board (drafts/scripts/tps2_neighbours.py, pad
#          polygons edge to edge): TP14's nearest exposed pad outside the row is R10.1 (GND) at 1.72 mm, harmless for a gate; TP13's
#          is W_N (PACK_N) at 2.83 mm, where the third position gives 2.41 mm to R10.2 (PACK_N), so this order does not bring the cell
#          node closer to ground. The ground stitch vias nearer the two ends (0.73 mm from TP13, 0.93 mm from TP14) are tented (board
#          setup: tenting front and back), so under mask. A probe on TP13 is a probe on the cells: a slip onto W_N shorts them through
#          F1 and F2 (commissioning note, drafts/r4-decisions.md O-9).
REGIONS = [
 ("GAUGE", (-24.2, -10.9, -4.55, 10.8), ["U1", "C1"] + ["C%d" % k for k in range(2, 10)] + ["R%d" % k for k in range(1, 10)], False),
 ("SEC",   (-4.35, -21.3, 4.15, 5.7), ["U2", "C14", "R23", "C18", "R27", "C17", "R26", "C16", "R25", "C15", "R24", "R33"], False),
 ("SIG",   (4.35, -13.6, 19.8, 10.0), ["R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R28", "C11", "C12", "D1", "D2", "D3", "Q5"], False),
 ("EAST",  (20.0, -9.6, 26.9, 9.7), ["R22", "R29", "R30", "R31", "C19", "JP1"], False),
 ("TPS",   (-33, -12, -25, 8.5), ["TP%d" % k for k in range(1, 11)], False),   # ten test points along the west edge (the cell tap nets are on J_CELL already)
 ("TPS2",  (-21.9, -21.3, -4.55, -17.2), ["TP14", "TP11", "TP12", "TP13"], False),   # west to east; the order is a safety choice, see TPS2 above
]
rest = [r for r in comps if r not in placed and not r.startswith("H") and not any(r in refs for _, _, refs, _ in REGIONS)]
if rest: REGIONS.append(("REST", (22, -10, 24, 8), rest, False))
GAP = 1.2; FINE_MARGIN = 2.2
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
regionfit.allowance('p')
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
# ---------------------------------------------------------------- the power path in locked 2 oz bands on both layers, stitched; the underside ground pour
def pad_at(ref, num):
    for pd in placed[ref].Pads():
        if pd.GetNumber() == num: return pd.GetPosition()
    raise SystemExit("pad %s.%s not found" % (ref, num))
def mm(v): return (v.x / 1e6 - OX, OY - v.y / 1e6)
def track(netname, a, b, w, L):
    t = pcbnew.PCB_TRACK(board); t.SetStart(P(*a)); t.SetEnd(P(*b)); t.SetWidth(FromMM(w)); t.SetLayer(L); t.SetNet(net_for(netname, create=False)); t.SetLocked(True); board.Add(t)
def band(netname, a, b, w=3.0, vias=20, layers=(pcbnew.F_Cu, pcbnew.B_Cu)):
    """A locked band on both outer layers between two board-frame points, stitched by locked 1.0/0.6 vias.

    13 September 2026 (MESHSAT-862): THE BARRELS WERE THE NECK AND NOTHING HAD EVER JUDGED THEM. Three
    0.8/0.4 vias stitched a band carrying 10 A, and the barrel measure added that day found one of them
    taking 2.67 A where IPC-2221 gives a 0.4 mm barrel's 0.0314 mm2 of wall 1.11 A at a 10 K rise. The
    project's own rule of thumb, about 2.5 A per 0.4 mm hole, was more than twice optimistic.
    A 0.6 mm drill has 0.0471 mm2 of wall and carries 1.48 A, and the spacing rather than a count of three
    now decides how many there are: one per 1.6 mm of band, which leaves 1.0 mm hole to hole. Six of them
    carry 8.90 A against the three's 3.32.
    """
    for L in layers: track(netname, a, b, w, L)
    net = net_for(netname, create=False)
    if len(layers) < 2: return        # one layer, nothing to stitch: no crossing means no barrel to size
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, min(vias, int((L - 4.4) / 1.0) + 1)) if L >= 4.4 else 1
    # AND THEY GO ACROSS THE BAND, NOT ONLY ALONG IT. Spacing them along the band took the worst barrel from
    # 2.67 A to 2.16 against its 1.48, and a pair at 1.6 mm along took PACK_P's to 1.85 and left FUSED's at
    # 2.59, because the current does not divide evenly over a line of vias. The crossing happens where the
    # current has to change layer, and that is at ONE end: the FET's source pads are SMD and F.Cu only, so
    # everything arriving on B.Cu crosses at the vias nearest them. THREE across at 1.0 mm along is what
    # spreads it: on a 2.8 mm band they sit at the centre and 0.9 mm either side, 0.3 mm hole to hole at a
    # TWO THINGS THAT DID NOT WORK, kept here because the next person will think of both. Widening these
    # bands to 3.6 mm made the barrels WORSE, not better (PACK_P 1.45 to 1.83, while the conductors fell to
    # 0.60 and 0.76): a wider band on both layers gives B.Cu a larger share and every ampere of that share
    # has to CROSS at the FET end, where the source pads are SMD and on one layer. And dropping B.Cu
    # altogether, which would remove the crossing, is refused by check_pcb_p, which requires a locked band of
    # each rail on B.Cu: that is this board's own invariant for a 10 A rail and not something to edit around.
    # So the width goes back to 2.8 and the vias go WHERE THE CROSSING IS, in the FET's own source tracks.
    # 0.5 mm drill, and the outer bodies stop 0.15 mm INSIDE the band's edge. At 0.9 mm across with a 0.6 mm
    # drill they reached the edge exactly, and the measure then showed one barrel still taking the whole
    # 2.44 A while its two neighbours took nothing: a via tangent to the copper it is meant to join is not
    # joined to it. A 0.5 mm drill has 0.0393 mm2 of wall and carries 1.30 A, three of them 3.90 A.
    # A band shorter than 4.4 mm gets ONE station, which is why FUSED had three barrels where PACK_P had 27.
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    across = [(-0.8, 0.0, 0.8)] if w >= 2.4 else [(0.0,)]
    for k in range(n):
        d = L / 2 if n == 1 else 2.2 + k * (L - 4.4) / (n - 1); f = d / L   # every via at least 2.2 mm from a band end (the wire lands' 2.4 mm holes, hole-to-hole 0.3)
        for off in across[0]:
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(P(a[0] + (b[0] - a[0]) * f - uy * off, a[1] + (b[1] - a[1]) * f + ux * off))
            v.SetWidth(FromMM(0.9)); v.SetDrill(FromMM(0.5)); v.SetNet(net); v.SetLocked(True); board.Add(v)
def _srcvia(netname, pts):
    """A locked 0.9/0.5 via at each point: the crossing at a FET's SMD source pads into the B.Cu band."""
    net = net_for(netname, create=False)
    for x, y in pts:
        v = pcbnew.PCB_VIA(board); v.SetPosition(P(x, y))
        v.SetWidth(FromMM(0.9)); v.SetDrill(FromMM(0.5)); v.SetNet(net); v.SetLocked(True); board.Add(v)

def short_of(a, b, d=0.8):
    """the point d mm before b on the way from a"""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); return (b[0] - (b[0] - a[0]) / L * d, b[1] - (b[1] - a[1]) / L * d)
# the PowerPAK SO-8 land: pins 1-3 (source) at x -2.67, y +1.91, +0.64, -0.64; pin 4 (gate) at y -1.91; the tab centred at x +0.69; Q2 is rotated 180
q1, q2 = FIXED["Q1"][:2], FIXED["Q2"][:2]
f2a, f2c = mm(pad_at("F2", "1")), mm(pad_at("F2", "2"))                                              # the chemical fuse's two ends (round 4; pins 1 and 2 on the Eaton land of the fix-up)
print("F2 pads: 1 at (%.2f, %.2f), 2 at (%.2f, %.2f), heater 3 at (%.2f, %.2f)" % (f2a + f2c + mm(pad_at("F2", "3"))))
f1a, f1b, r10a, r10b = mm(pad_at("F1", "1")), mm(pad_at("F1", "2")), mm(pad_at("R10", "1")), mm(pad_at("R10", "2"))
wbp, wp, wbn, wn = mm(pad_at("W_BP", "1")), mm(pad_at("W_P", "1")), mm(pad_at("W_BN", "1")), mm(pad_at("W_N", "1"))
band("CELL4", short_of(f1a, wbp), short_of(wbp, f1a))                                                    # B+ land to the blade holder
# 13 September 2026: 3.6 mm, not 2.8. IPC-2221 gives 2.8 mm at 2 oz 8.34 A on ONE outer layer against this
# rail's 10, so the band needs both layers and therefore needs the current to CROSS, and the crossing is what
# the barrels were failing on: four attempts at the vias took PACK_P's worst from 2.67 A to 1.88 against its
# 1.30 and left FUSED's at 2.25. At 3.6 mm one layer carries 10.01 A, which is the rail exactly, so either
# layer can take the whole of it and the crossing becomes whatever the copper decides rather than something
# the barrels have to force. It is not margin on one layer; it is margin on the pair of them.
q1_src = (q1[0] - 4.6, q1[1] + 0.64)
# ROUND 4 (26 September 2026): the blade no longer feeds the charge FET directly. FUSED runs from the blade to F2's pin 1 and SCP_OUT from
# F2's pin 2 (pin 3 on the first pass's Dexerials draft) to the charge FET's source side, both at the 2.8 mm the old FUSED band had, on
# both layers and stitched as before.
band("FUSED", short_of(f2a, f1b), f2a, w=2.8)                                                                # the blade to the chemical fuse
band("SCP_OUT", f2c, q1_src, w=2.8)                                                                           # the chemical fuse to the charge FET's source side
# 13 September 2026 (MESHSAT-862, appendix 32.164): THE PACK CURRENT ENTERS THE BAND THROUGH THESE THREE
# TRACKS AND THEY WERE 0.6 mm. IPC-2221 gives 0.6 mm at 2 oz 2.73 A, and the measure found 4.16 A in one of
# PACK_P's three (ratio 1.52) and 2.09 A in one of FUSED's: the 10 A does not divide evenly over three
# parallel runs, the one nearest the band's own entry takes the most. 1.2 mm carries 4.51 A each. The pads
# sit on a 1.27 mm pitch so the three nearly merge, which is what is wanted, and they are all the same net;
# the gate pad is 1.27 mm beyond the outermost source pin and keeps 0.37 mm of clearance at this width.
for dy in (1.91, 0.64, -0.64): track("SCP_OUT", (q1[0] - 2.67, q1[1] + dy), (q1_src[0], q1[1] + dy), 1.2, pcbnew.F_Cu)   # SCP_OUT since round 4: Q1's source is after F2
# A VIA IN EACH SOURCE TRACK, which is the one place the current has to change layer: the FET's source pads
# are SMD on F.Cu and the band's other half is on B.Cu. Five attempts at the band's own stations moved the
# worst barrel from 2.67 A to 1.88 because they were all downstream of this point. Each track is 1.93 mm long
# and 1.2 mm wide. One via per track took PACK_P's worst barrel from 1.83 A to 1.51 against its 1.30 and
# FUSED's to 1.82, so each track takes TWO, at 3.15 and 4.05 mm from the FET: 0.9 mm apart along the track,
# which is 0.4 mm hole to hole, and 0.15 mm to each edge across it. Six barrels per FET where there were
# three, and the three tracks are 1.27 mm apart, 0.77 mm hole to hole.
_srcvia("SCP_OUT", [(q1[0] - x, q1[1] + dy) for dy in (1.91, 0.64, -0.64) for x in (3.15, 4.05)])
band("SW", (q1[0] + 0.69, q1[1]), (q2[0] - 0.69, q2[1]))                                  # tab to tab
q2_src = (q2[0] + 4.6, q2[1] - 0.64); band("PACK_P", q2_src, short_of(q2_src, wp), w=2.8)  # the discharge FET's source side to the pack + land
for dy in (-1.91, -0.64, 0.64): track("PACK_P", (q2[0] + 2.67, q2[1] + dy), (q2_src[0], q2[1] + dy), 1.2, pcbnew.F_Cu)
_srcvia("PACK_P", [(q2[0] + x, q2[1] + dy) for dy in (-1.91, -0.64, 0.64) for x in (3.15, 4.05)])
band("GND", short_of(r10a, wbn), short_of(wbn, r10a, 0.5)); band("PACK_N", short_of(wn, r10b, 0.5), short_of(r10b, wn))   # B- land, shunt, pack - land
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25)); z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.4))
    # 9 Sep 2026 (appendix 32.85 and its correction): written for readability, not for effect. ISLAND_REMOVAL_MODE_ALWAYS
    # is 0 and is KiCad's default, so P's pours were already removing their unconnected islands without this line.
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    except Exception: pass
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
pour(pcbnew.B_Cu, "GND", "GND pour B.Cu", (-35, -22, 35, 22))
# P2 (8 Sep 2026, MESHSAT-862; 32.66: the P1 pour was 874 of 3080 mm2 in 15 pieces, 4 loose, once the router had used the underside): a locked ground via grid
# on 5 mm, wherever 1.6 mm from every pad, band and hole, so each piece the router leaves is anchored to the top-side ground
_gnd = net_for("GND", create=False); _n = 0
_obst = [(pd.GetPosition(), 1.6) for f in board.GetFootprints() for pd in f.Pads()]
# FIX-UP OF 26 SEPTEMBER 2026: 1.6 mm FROM A PAD'S CENTRE IS NOT A CLEARANCE ONCE THE PAD IS LARGE. The SCF9550's heater land is 3.0 x
# 2.15 mm, and a grid via at (-2, 11) passed the centre test at 2.0 mm while its barrel stood 0.10 mm from the pad's edge, where the
# heater net's PWR class asks 0.30 (the one DRC clearance error of the first fix-up run). Every pad's outline is now kept at the same
# distance the tracks are kept below: the via's radius, the PWR clearance and a margin.
_obst_bb = [pd.GetBoundingBox() for f in board.GetFootprints() for pd in f.Pads()]
def _rect_d(p_, bb_):
    return math.hypot(max(bb_.GetLeft() - p_.x, 0, p_.x - bb_.GetRight()), max(bb_.GetTop() - p_.y, 0, p_.y - bb_.GetBottom()))
def _seg_d(p_, a_, b_):
    dx_, dy_ = b_.x - a_.x, b_.y - a_.y; l2 = dx_ * dx_ + dy_ * dy_
    t_ = 0 if l2 == 0 else max(0, min(1, ((p_.x - a_.x) * dx_ + (p_.y - a_.y) * dy_) / l2))
    return math.hypot(p_.x - (a_.x + t_ * dx_), p_.y - (a_.y + t_ * dy_))
_rules = [z for z in board.Zones() if z.GetIsRuleArea()]
for _gx in range(-32, 33, 5):
    for _gy in range(-19, 20, 5):
        _p = P(_gx, _gy)
        if not all(math.hypot(_p.x - o.x, _p.y - o.y) > FromMM(r) for o, r in _obst): continue
        if not all(_rect_d(_p, bb_) > FromMM(0.3 + 0.3 + 0.15) for bb_ in _obst_bb): continue
        if not all(_seg_d(_p, t.GetStart(), t.GetEnd()) > t.GetWidth() / 2 + FromMM(0.3 + 0.3 + 0.15) for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"): continue   # the PWR class clearance 0.3 plus the via
        if any(z.Outline().Contains(_p) for z in _rules): continue
        if board.GetBoardEdgesBoundingBox().Contains(_p):
            v = pcbnew.PCB_VIA(board); v.SetPosition(_p); v.SetDrill(FromMM(0.3)); v.SetWidth(FromMM(0.6)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(_gnd); v.SetLocked(True); board.Add(v); _n += 1
print("ground stitch grid: %d locked vias" % _n)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
DEFAULT = (0.16, 0.25, 0.6, 0.3); cls(ns.GetDefaultNetclass(), *DEFAULT)
# EVERY CLEARANCE ON THIS BOARD IS 0.16 mm, not 0.127: two layers at 2 oz, and the fabricator's own capability
# for that combination is 0.16 for both track width and spacing (rule RTE-001, 16 September 2026). The widths
# stay as they are, because every one of them is already above 0.16.
# ROUND 4 (26 September 2026): SCP_OUT, the cell node after the chemical fuse, is a 10 A power net like FUSED; SCP_HTR is the fuse heater's
# return to Q3, 1.3 to 3.5 A for up to the 60 s the SCP needs to open (Eaton ELX1135; the fix-up of 26 September 2026 replaced the
# SFK-1830A with the SCF9550-30-05, the same heater figures), and a default 0.25 mm track at 2 oz fuses at about 5 A in
# one second, so it takes the PWR class's 0.5 mm (held for the full 60 s at 3.5 A, a 0.5 mm 2 oz outer track rises about 25 K by
# IPC-2221A, fix-up of 26 September 2026). A reserved line (net classes), changed by the session under the owner's standing rule
# of 26 September 2026 and recorded in drafts/r4-decisions.md.
PATTERNS = [("CELL4", "PWR"), ("FUSED", "PWR"), ("SCP_OUT", "PWR"), ("SCP_HTR", "PWR"), ("SW", "PWR"), ("PACK_P", "PWR"), ("PACK_N", "PACK"), ("GND", "GNDC"), ("CELL1", "SENSE"), ("CELL2", "SENSE"), ("CELL3", "SENSE")]
# SENSE: every net pcb_sensitive.yaml declares for this board, in a class of its own with the default geometry, listed ahead
# of the table so a sensitive net wins over a pattern that also names it; the DSN class-pair clearance of route_one.sh
# (FR_CLASS_CLEAR, appendix 32.222) is what reads it (17 September 2026, rule ANA-001).
try:
    import yaml as _yaml, os as _os
    _sens = ((_yaml.safe_load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "pcb_sensitive.yaml"))) or {}).get("boards") or {}).get("p") or {}
    _sens_nets = [n["net"] for n in (_sens.get("nodes") if isinstance(_sens, dict) else _sens) or []]
except BaseException as _e:
    _sens_nets = []; print("SENSE class: pcb_sensitive.yaml not read (%s), no sensitive net moves class" % type(_e).__name__)
PATTERNS = [(n, "SENSE") for n in _sens_nets] + PATTERNS
print("SENSE class: %d declared sensitive net(s) take it" % len(_sens_nets))
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]
try:
    # (a first SENSE class at 0.25 mm was defined here and overwritten two lines below; removed 18 September 2026)
    CLASSES = [("PWR", 0.3, 0.5, 0.8, 0.4),   # P2 (8 Sep 2026): the current runs in the locked 2 oz bands; the class width is for the sense, gate and test-point runs
               ("SENSE", 0.16, 0.4, 0.7, 0.3),   # 0.7/0.3: a 0.20 mm ring, the annular floor this board declares; 0.6/0.3 left E12 with ten annular_width violations (18 September 2026)
               # PACK: the pack RETURN alone, and it is board P's one measured failure with nothing in front
               # of it (20 September 2026, 06:10, PI-001 at 1.03 of its limit). It carries 2.47 A on a
               # 0.500 mm conductor of outer 2 oz, rated 2.392 A at 10 K where IPC asks 0.523 mm. THE WIDTH
               # IS BOUND FROM ABOVE BY THE PADS, which is board D's ruling 9 in miniature: the narrowest pad
               # on ANY net of the shared PWR class is 0.610 mm, so that class cannot go past 0.600 and
               # 2.73 A without a track spilling past a pad edge, while **PACK_N's OWN narrowest pad is
               # 0.800 mm**, so a class of its own carries 3.36 A and leaves the other four nets exactly as
               # they are. The clearance stays this board's 0.16 and the via its 0.8/0.4.
               ("PACK", 0.16, 0.8, 0.8, 0.4),
               ("GNDC", 0.16, 0.5, 0.6, 0.3)]   # ONE table for the board's classes AND the project file's (18 September 2026): a second hand-written copy in the project file had drifted (D's PWR via 1.2/0.6 on the board, 0.8/0.4 in the file the router reads; SENSE absent from the file on D, E and P; SENSE 0.6/0.3 on P), the defect B fixed for itself on 8 September
    for _nm, *_v in CLASSES:
        _nc = pcbnew.NETCLASS(_nm); cls(_nc, *_v); ns.SetNetclass(_nm, _nc)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
except Exception as e: print("note: net class API:", e)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json, fnmatch as _fnm
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def C(name, prio, clr, tw, vd, vdr): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=0.2, diff_pair_gap=0.15)
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, *DEFAULT)] + [C(_nm, _i, *_v) for _i, (_nm, *_v) in enumerate(CLASSES)]
    d["net_settings"]["netclass_patterns"] = [{"netclass": n, "pattern": p} for p, n in PATTERNS]
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
    d["net_settings"].setdefault("meta", {"version": 4}); d["net_settings"].setdefault("net_colors", None)
    # 0.16 HERE TOO, and this is the line that decides (17 September 2026). The board's own minimum was moved
    # to 0.16 in gen_pcb_p.py on 16 September for the fabricator's 2 oz two-layer rows, and these two lines
    # were missed: the SWIG default class above and this one, which is the PROJECT file's minimum and the one
    # KiCad enforces (a board's minimums live in the project file; nothing set through the SWIG design
    # settings survives a save). So the board said 0.16 and was built to 0.127, which is what fab_limits
    # reports on P4 as five items under the fabricator's capability.
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.16
    json.dump(d, open(pro, "w"), indent=2); print("project net classes re-applied, %d assignments" % len(_assign))
