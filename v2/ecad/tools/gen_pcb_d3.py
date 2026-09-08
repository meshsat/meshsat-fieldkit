#!/usr/bin/env python3
"""PCB-D APRS mezzanine D9 (MESHSAT-862 rules 1 and 2; D8 of MESHSAT-830 before it): bring the netlist onto the mechanical board of gen_pcb_d.py, fix the connectors, the RF chain
and the USB cluster (hub, bridge, ESD, codec, crystals and every pair's series resistors side by side on the top layer beside the pins they serve, appendix 32.68), pack the rest,
pour the planes and set the net classes. Usage: gen_pcb_d3.py <board.kicad_pcb> <netlist.net>. Board frame: origin at the board centre (case (50, 0)), +X east, +Y north.
The RF chain is placed by hand along the south edge in signal order (antenna SMA, T/R relay, 10 dB pad, PA drive U.FL, 5-element LPF, PA output SMA) so the
50 ohm tracks stay short; everything else is packed per region: the power entry and the expander's level stages along the north edge, the PTT logic under the
exciter, the hub east of the exciter, the audio set south-east, the passives of the audio network on the underside where no fine-pitch part sits above."""
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
# ---------------------------------------------------------------- fixed parts (board mm, rot, back): connectors on the edges, the exciter, the RF chain in signal order
FIXED = {"J_HARN1": (-42, 8, 0, False), "J_PWR1": (-42, -16, 90, False), "J_HS1": (46.5, 12, 90, False), "J_HS2": (46.5, -12, 90, False), "J_USB3": (46, 24, 90, False),
         "U2": (-15, 8, 0, False),
         "J_ANT": (-31, -33, 0, False), "K1": (-14, -26, 0, False), "R54": (-5, -29, 0, False), "R55": (-1, -34, 270, False), "R56": (3, -29, 0, False), "J_PAIN": (9, -29, 0, False),
         "C60": (13, -34.5, 90, False), "L2": (17, -29, 0, False), "C59": (21, -34.5, 90, False), "L1": (25, -29, 0, False), "C58": (28.5, -35, 90, False), "J_PAOUT": (35, -30, 0, False), "J_VGG": (43.5, -22.5, 0, False),
         # D9 (8 Sep 2026, 32.68): the USB cluster on the top layer. The hub U4 (LQFP-32, pins 1 to 8 down the west side, 9 to 16 along the south, 17 to 24 up the east):
         # the upstream pair through the ESD U5 (west) and R6/R7 into pins 1, 2; port 1 (pins 11, 12) through R12/R13 south to the codec U6 with R26/R27 at its pins 3, 4;
         # port 2 (pins 15, 16) through R16/R17 lying in line with the bridge U3's D+/D- pins 3 mm to their east (a straight pair, no corner); port 3 (pins 19, 20) through R20/R21 east to J_USB3.
         # Every pair's two resistors sit side by side, 1.6 mm apart, pads across the pair axis, within 4 mm of the pins (the D8 rows 4.2 mm apart broke the pair pre-router).
         "U4": (22, 14, 0, False), "U5": (9, 16.2, 0, False), "U3": (30, 3, 0, False), "U6": (22, -9.5, 0, False), "Y1": (21, 21.5, 0, False), "Y2": (13, -13.5, 0, False),
         "R6": (13.5, 16.8, 0, False), "R7": (13.5, 15.2, 0, False),
         "R12": (21.6, 6.3, 270, False), "R13": (20.0, 6.3, 270, False), "R16": (23.5, 3.25, 0, False), "R17": (23.5, 1.65, 0, False),   # port 2: in line with the bridge U3's D+/D- pins 3 mm east, pad 2 (the pair) east: a straight pair; pad 1 (the hub side) north for port 1
         "R20": (30.5, 13.6, 0, False), "R21": (30.5, 12.0, 0, False), "R26": (11.5, -9.1, 0, False), "R27": (11.5, -7.5, 0, False),   # 4.4 mm from U6 pad tips: the entry runs of both stations need the room (12:19 CEST)
         # D9: the pull-downs and the codec pull-up of the pair nets on the top layer beside their pairs (a pair net's pad on the back made the router wander three layers);
         # R14 east of R12 and R15 west of R13 in the series row (the P pull-down on the P side, the N one on the N side, so the stubs do not cross the legs; 12:45 CEST)
         "R14": (23.2, 6.3, 90, False), "R15": (18.4, 6.3, 90, False), "R18": (23.5, -0.5, 0, False), "R19": (23.5, -2.1, 0, False), "R22": (30.5, 15.8, 0, False), "R23": (30.5, 10.0, 0, False), "R28": (11.5, -11.1, 0, False)}
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
for ref, x, y in (("J_HARN1", -42, 20.5), ("J_PWR1", -42, -9.5), ("J_ANT", -31, -37.5), ("J_PAIN", 9, -25.5), ("J_PAOUT", 35, -37.5), ("J_VGG", 43.5, -18.5), ("J_HS1", 46.5, 19), ("J_HS2", 46.5, -5), ("J_USB3", 46, 30.5)):
    text(ref, x, y, pcbnew.F_SilkS, 0.9, 0.15)
text("SA868 (bench fit)", -15, 19.5, pcbnew.F_SilkS, 0.9, 0.15); text("T/R", -14, -21, pcbnew.F_SilkS, 0.9, 0.15); text("10 dB", -1, -24.5, pcbnew.F_SilkS, 0.8, 0.14); text("LPF 145 MHz", 21, -24.5, pcbnew.F_SilkS, 0.8, 0.14)
# ---------------------------------------------------------------- packed regions (name, rect, refs, back)
REGIONS = [
 ("PWR",  (-37, 19, -20, 34), ["D1", "C1", "C2", "C5", "FB1", "U1", "LED1"], False),
 ("PWRB", (-37, 19, -20, 34), ["C3", "C4", "C6", "C7", "C8", "C9", "R1", "R2", "R3"], True),
 ("EXP",  (-20, 19, 4, 34), ["Q%d" % k for k in range(3, 10)], False),
 ("EXPB", (-20, 19, 4, 34), ["R%d" % k for k in range(66, 80)], True),
 ("TPS",  (4, 28.5, 40, 38.5), ["TP%d" % k for k in range(1, 17)], False),
 ("TPS2", (-40, 34.5, 4, 38.5), ["TP%d" % k for k in range(17, 25)], False),
 ("HUB",  (4, 20, 43, 28), ["C10", "C11", "C13", "C14"] + ["C%d" % k for k in range(29, 34)] + ["C35", "C36", "C37", "C38"], False),   # D9: the strip north of the fixed USB cluster
 ("HUB2", (35, 0, 43, 20), ["U7", "U15", "C61", "C62"], False),   # D9: east of the bridge
 ("HUBB", (4, 0, 43, 16), ["R4"] + ["R%d" % k for k in (8, 9, 10, 11, 24, 25)] + ["C12", "C15", "C16", "C17"], True),
 ("AUD",  (4, -22, 43, -15.2), ["C%d" % k for k in range(19, 28)] + ["C39", "C40", "LED2", "LED3", "R29", "R30", "JP1", "JP2"], False),   # D9: the strip south of the codec
 ("AUD2", (29, -15, 43, 0), ["U8"], False),
 ("AUDB", (4, -22, 43, -8), ["R%d" % k for k in range(31, 48)] + ["C18", "C28", "C34"] + ["C%d" % k for k in range(41, 49)], True),
 ("CTRL", (-37, -21.5, -5, -4.5), ["U16", "C63"] + ["U%d" % k for k in range(9, 15)] + ["LED4", "LED5", "LED6", "Q1"], False),
 ("CTRLB", (-24, -21.5, -5, -4.5), ["C%d" % k for k in range(51, 57)] + ["R48", "R49", "R50", "R51", "R5", "D2", "C57"], True),
 ("RLYD", (-26, -37, -8, -31.5), ["Q2", "R52", "R53"], False),
]
rest = [r for r in comps if r not in placed and not r.startswith("H") and not any(r in refs for _, _, refs, _ in REGIONS)]
if rest: REGIONS.append(("REST", (-46, -30, -38, -22), rest, False))
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
for name, (x0, y0, x1, y1), refs, back in REGIONS:
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
    if cy - rowh < y0 - 0.01: print("WARNING region %s overflows by %.1f mm" % (name, (y0 - (cy - rowh))))
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
# ---------------------------------------------------------------- planes: In1 solid GND (no tracks), GND pours on In2 and both outer layers (the RF section is coplanar over the plane)
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25)); z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.4))
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
pour(pcbnew.In1_Cu, "GND", "GND plane In1", (-50, -40, 50, 40))
z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
z.SetLayer(pcbnew.In1_Cu); z.SetZoneName("In1 solid ground: no tracks"); o = z.Outline(); o.NewOutline()
for x, y in ((-51, -41), (51, -41), (51, 41), (-51, 41)): p_ = P(x, y); o.Append(p_.x, p_.y)
board.Add(z)
for L in (pcbnew.In2_Cu, pcbnew.F_Cu, pcbnew.B_Cu): pour(L, "GND", "GND pour %s" % board.GetLayerName(L), (-50, -40, 50, 40), priority=0)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
cls(ns.GetDefaultNetclass(), 0.127, 0.25, 0.6, 0.3)
PATTERNS = [("+5V_*", "PWR"), ("+3V3*", "PWR"), ("VGG_SW", "PWR"), ("GND", "PWR"), ("RF_*", "RF"), ("USB*", "USB"), ("HUB_D*", "USB")]
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]   # 5 Sep 2026 (gateway finding, MESHSAT-802): root-sheet labels are "/NAME" on the board and KiCad's pattern matcher does not strip the slash, so every label pattern is emitted in both forms; power symbols (GND, +3V3) have no slash
try:
    nc = pcbnew.NETCLASS("PWR"); cls(nc, 0.127, 0.5, 0.8, 0.4); ns.SetNetclass("PWR", nc)
    nr = pcbnew.NETCLASS("RF"); cls(nr, 0.3, 0.35, 0.6, 0.3); ns.SetNetclass("RF", nr)
    nu = pcbnew.NETCLASS("USB"); cls(nu, 0.127, 0.3, 0.6, 0.3); nu.SetDiffPairWidth(FromMM(0.3)); nu.SetDiffPairGap(FromMM(0.2))   # 8 Sep 2026 (32.71): 0.30/0.20 on the 7628 outer layer computes 89 ohm; the USB pairs stay on F.Cu over the In1 ground; ns.SetNetclass("USB", nu)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
except Exception as e: print("note: net class API:", e)
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
import json
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    d = json.load(open(pro))
    base = dict(bus_width=12, line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)", schematic_color="rgba(0, 0, 0, 0.000)", wire_width=6, diff_pair_via_gap=0.25)
    def C(name, prio, clr, tw, vd, vdr): return dict(base, name=name, priority=prio, clearance=clr, track_width=tw, via_diameter=vd, via_drill=vdr, diff_pair_width=0.3, diff_pair_gap=0.2)
    d.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.127, 0.25, 0.6, 0.3), C("PWR", 0, 0.127, 0.5, 0.8, 0.4), C("RF", 1, 0.3, 0.35, 0.6, 0.3), C("USB", 2, 0.127, 0.3, 0.6, 0.3)]
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
