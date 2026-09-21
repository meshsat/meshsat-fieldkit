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
         "R20": (32.0, 13.6, 0, False), "R21": (32.0, 12.0, 0, False), "R26": (11.5, -9.1, 0, False), "R27": (11.5, -7.5, 0, False),   # 4.4 mm from U6 pad tips: the entry runs of both stations need the room (12:19 CEST)
         # D9: the pull-downs and the codec pull-up of the pair nets on the top layer beside their pairs (a pair net's pad on the back made the router wander three layers);
         # R14 east of R12 and R15 west of R13 in the series row (the P pull-down on the P side, the N one on the N side, so the stubs do not cross the legs; 12:26 CEST)
         # the unused hub port's 15k terminations beside the hub instead of 9 mm away on the back (8 Sep 2026 16:05): the router could not reach U4 pin 23
         # through the crystal and port-4 copper around it, which left HUB_DM4 the one open net of two rounds. They sit north-east of U4 on the FRONT, the
         # pins' own layer, because the gap between U4's courtyard (to x 127.22) and the pull-down column (from x 128.97) is 1.75 mm, too narrow for an 0603
         "R25": (28.3, 20.6, 0, False), "R24": (31.6, 20.6, 0, False),
         "R14": (23.2, 6.3, 90, False), "R15": (18.4, 6.3, 90, False), "R18": (23.5, -0.5, 0, False), "R19": (23.5, -2.1, 0, False), "R22": (30.5, 15.8, 0, False), "R23": (30.5, 10.0, 0, False), "R28": (11.5, -5.8, 180, False),   # R28 north of R27, pad 1 east toward the codec leg (its slot south overlapped the crystal Y2 courtyard, 12:59 CEST)
         # D31 (21 September 2026, 01:40 CEST): the codec's PCM_VCCP decoupling C23 takes a FIXED seat beside U6 pin 26 (case (24.0, -5.34)), east of the
         # pull-up column R18/R19 at x 23.5. D30 round 1 landed hard 0 and ONE open, /PCM_VCCP over 16.1 mm from C23 pad 1 to U6 pad 26, with the capacitor
         # packed in the rows and bypass_place reading it STUCK (no free spot within 3.0 mm); the seat was measured first through FIXED_OVERRIDE on the hub:
         # PREROUTE-DONE OK, hard 0, escapes 68/7 and fanout 92/13 identical to the baseline, place_audit 0 collisions, C23 no longer STUCK.
         "C23": (26.5, -1.6, 0, False),
         # D32 (21 September 2026, 03:05 CEST): D31 ran all 200 passes and landed hard 0 and TWO open of 133, /PCM_VCCL (C21 pad 1 to U6
         # pin 19, 19.2 mm) and /PCM_VIN (C28 pad 2 to U6 pin 16, 18.0 mm), where /PCM_VCCP closed as C23's seat predicted: the same shape,
         # next two parts. C21 is the PCM_VCCL bypass (declared at pin 19) and takes the free front side east of U6 4.8 mm from its pin;
         # C28 is the 1 uF that couples the halved receive audio into the ADC input at pin 16 and was packed in AUDB on the underside
         # eighteen millimetres west, so it keeps the underside and sits 4.2 mm south of pin 16, past the escape fan. Measured through
         # FIXED_OVERRIDE on the hub (/root/dseat31.log): PREROUTE-DONE OK, hard 0, escapes 68/7 as D31, place_audit 0 of 6; a front-side
         # C28 south of the codec (/root/dseat32.log) collides with R30 (courtyards, a mask bridge, a short) and is refused.
         "C21": (31.0, -10.7, 90, False), "C28": (24.8, -17.9, 0, True)}
# 9 Sep 2026 (D10, appendix 32.83): a placement candidate can be swept from the environment instead of edited into the file.
# The D pre-route chain runs in 47 seconds, so where a part goes is a question to MEASURE (pairs laid, pre-route hard),
# not to argue on paper. FIXED_OVERRIDE="R20=35.0,19.5,0;R21=35.0,17.9,0" moves those parts for one run only.
for _ov in filter(None, os.environ.get("FIXED_OVERRIDE", "").split(";")):
    _r, _v = _ov.split("="); _p = [float(t) for t in _v.split(",")]
    FIXED[_r.strip()] = (_p[0], _p[1], _p[2] if len(_p) > 2 else 0, bool(_p[3]) if len(_p) > 3 else False)
    print("gen_pcb_d3: FIXED_OVERRIDE %s -> %s" % (_r.strip(), FIXED[_r.strip()]))
for ref, (x, y, rot, back) in FIXED.items(): placed[ref] = place(ref, x, y, rot, back)
# 9 September 2026 (owner ruling, appendix 32.74 option 3): every declared decoupling capacitor takes its slot beside the pin it serves
# BEFORE the packer fills the regions. The old order shelf-packed them by reference number and `bypass_place.py` then moved what still
# fitted, which on D9 was nine of sixteen; measured across the released set, not one capacitor of any board was inside the 3 mm rule.
import json as _json, os as _osx, bypass_slots
import regionfit
regionfit.allowance('d')
_ip = _osx.path.join(_osx.path.dirname(_osx.path.abspath(BOARD)), "out", _osx.path.splitext(_osx.path.basename(BOARD))[0] + "-intent.json")
_entries = _json.load(open(_ip)).get("bypass", []) if _osx.path.exists(_ip) else []
RESERVED = set() if _osx.environ.get("BYPASS_SLOTS") == "0" else bypass_slots.reserve(board, place, lambda v: (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y)), _entries)
for _r in RESERVED: placed[_r] = board.FindFootprintByReference(_r)
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
 ("HUBB", (4, 0, 43, 16), ["R4"] + ["R%d" % k for k in (8, 9, 10, 11)] + ["C12", "C15", "C16", "C17"], True),
 ("AUD",  (4, -22, 43, -15.2), ["C%d" % k for k in range(19, 28)] + ["C39", "C40", "LED2", "LED3", "R29", "R30", "JP1", "JP2"], False),   # D9: the strip south of the codec
 ("AUD2", (29, -15, 43, 0), ["U8"], False),
 # C28 left this list for a FIXED seat beside U6 pin 16 at D32 (21 September 2026)
 ("AUDB", (4, -22, 43, -8), ["R%d" % k for k in range(31, 48)] + ["C18", "C34"] + ["C%d" % k for k in range(41, 49)], True),
 ("CTRL", (-37, -21.5, -5, -4.5), ["U16", "C63"] + ["U%d" % k for k in range(9, 15)] + ["LED4", "LED5", "LED6", "Q1"], False),
 ("CTRLB", (-24, -21.5, -5, -4.5), ["C%d" % k for k in range(51, 57)] + ["R48", "R49", "R50", "R51", "R5", "D2", "C57"], True),
 ("RLYD", (-26, -37, -8, -31.5), ["Q2", "R52", "R53"], False),
]
REGIONS = [(_n, _rect, [_r for _r in _refs if _r not in RESERVED], _bk) for _n, _rect, _refs, _bk in REGIONS]   # a reserved capacitor is placed already

rest = [r for r in comps if r not in placed and not r.startswith("H") and not any(r in refs for _, _, refs, _ in REGIONS)]
if rest: REGIONS.append(("REST", (-46, -30, -38, -22), rest, False))
# OWNER RULING 9 (13 September 2026): keep the 1.2 mm PWR class and make the room by rearranging parts.
# D's regions are not the constraint (two overflow by 0.2 mm against a declared 0.5), the DENSITY is: 211
# footprints on 100 by 80 mm with almost every region boxed by its siblings, and a 1.2 mm rail needs a
# 1.2 mm channel. PLACE_GAP is the packer's own spacing and is the one lever that widens every channel at
# once without touching a region rectangle, which is the owner's. MEASURED 13 September 2026 and it does
# NOT answer the ruling: 1.8 overflows six regions worst 3.8 mm and 2.4 overflows thirteen worst 7.6 mm, both
# against D's declared 0.5 mm allowance, so neither value reaches a route and neither can be compared with the
# twelve opens the 1.2 mm width leaves. The knob stays, at the packer's own 1.2, because the arm is reproducible
# and the next lever has to be measured against it. What the WIDTH itself costs is measured separately, by
# routing the same placement at 0.5 mm under the same router call.
GAP = float(os.environ.get("PLACE_GAP", "1.2")); FINE_MARGIN = 2.2   # E6 round 4: 1.4 left R14 inside the tracker's escape row and four pads of U5 without escapes
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
# ---------------------------------------------------------------- planes: In1 solid GND (no tracks), GND pours on In2 and both outer layers (the RF section is coplanar over the plane)
def pour(layer, netname, name, rect, priority=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net_for(netname, create=False)); z.SetZoneName(name)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25)); z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.4))
    # 9 Sep 2026 (D10, appendix 32.85 and its correction): this file defined pour() TWICE and the second one, the one
    # that actually runs, did not set the island removal. The duplicate was a real trap and is gone. The setting itself
    # changes NOTHING: ISLAND_REMOVAL_MODE_ALWAYS is 0, which is KiCad's default, so every zone on every board has always
    # removed its unconnected islands and the token never even reaches the file. It is written explicitly now so the
    # intent is readable, not because it fixes anything. D10's last open is a different thing: two areas of one pour that
    # are each connected to a pad but not to each other, which is pour_stitch.py's job.
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    except Exception: pass
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    z.SetAssignedPriority(priority); board.Add(z); return z
pour(pcbnew.In1_Cu, "GND", "GND plane In1", (-50, -40, 50, 40))
z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
z.SetLayer(pcbnew.In1_Cu); z.SetZoneName("In1 solid ground: no tracks"); o = z.Outline(); o.NewOutline()
for x, y in ((-51, -41), (51, -41), (51, 41), (-51, 41)): p_ = P(x, y); o.Append(p_.x, p_.y)
board.Add(z)
# ------------------------------------------------------------------ OWNER RULING 15 (13 September 2026)
# "The PWR class goes back to 0.5 mm and the rail is carried at 1.2 mm on the INNER layers as locked
# pre-routed copper, board A's power_copper.py pattern. This is ruling 9 implemented where it was actually
# put." Ruling 9 asked for the width on the inner layers, and a KiCad class carries one width for EVERY
# layer, so as a class it put 1.2 mm tracks on pads narrower than that: 191 of the 230 pads on these nets, on
# 124 parts, the narrowest 0.25 mm, and the nine hard items of that arm all sat at one SOD-123 with 0.90 mm
# pads. As locked copper it goes exactly where it was meant to and touches no pad's width.
#
# WHERE THE CURRENT ACTUALLY GOES, from the rail's own declared loads rather than from its total: the source
# is J_PWR1 at (-42.55, -17.76) and the load is 1.0 A, but it divides at once. FB1 takes 0.50 A and U1 0.25,
# both in the north-west corner; U6, J_USB3, U7, U3 and U15 take 0.25 A between them across the whole east
# half. So the TRUNK carries 1.0 A and the west branch 0.75, while the east branch's 0.25 A is inside what
# the 0.5 mm class carries (0.44 A) and needs no locked copper at all. On 0.5 oz inner copper IPC-2221 gives
# 1.7 mm 1.06 A and 1.5 mm 0.97 A at a 10 K rise, so the trunk is 1.7 and the west branch 1.5.
#
# In1 is the solid ground plane and takes no tracks, so the inner layer this can go on is In2. The band is
# declared BEFORE the ground pours, which fill around it at their own priority 0.
from power_copper import PowerCopper as _PC
_pc = _PC(board, net_for, P)
# WHERE IT RUNS, and the first attempt is why this is written down. A trunk straight north from J_PWR1's pad
# at x -42.5 goes through **J_HARN1's pin field**: that connector is a through-hole 2x8 with its columns at
# x -42.75 and -40.21, so its pads exist on In2 and the band filled 36 of its 92 mm2. The clear corridor is
# x -37.5: 1.11 mm from the nearer pin column's pad edge, and the only other thing near it is C7, a bypass
# capacitor of this same rail. So the band jogs east along y -17.8 from the source pad, runs north at
# x -37.25, and REACHES C7's own pad at y 23.9. Stopping 0.69 mm short of it, as the first version did, left
# that pad with no copper of its net on any layer it could reach: its nearest +5V_D8 via was 2.77 mm away and
# the decoupling gate refused the board for it. A pad of the band's own net that the band overlaps is
# connected to it, so no via is needed at all. C7's GROUND pad ends at x -38.30 and the band starts at
# -38.10, which is 0.20 mm of clearance against the 0.15 the fill wants.
_pc.union("+5V_D8", "+5V_D8 trunk In2", [(-43.4, -18.6, -36.4, -16.9),    # east from J_PWR1's pad, clear of its GND pin at y -13.8
                                         (-38.1, -18.6, -36.4, 23.9),      # north in the corridor between J_HARN1's pins and C7, 1.7 mm
                                         (-38.1, 21.4, -29.4, 22.9),       # east to FB1's pad and over U1's upper pad, 1.5 mm
                                         (-36.3, 19.6, -34.6, 22.4)],      # the stub down to U1's lower pad
          pcbnew.In2_Cu, priority=2, min_width=0.25, clearance=0.15)
_pc.stitch("+5V_D8", [(-31.4, 22.15), (-34.9, 22.15), (-35.46, 20.1)])    # one via per load pad, beside it and inside the band
# ---------------------------------------------- PI-003 ON +5V_SA: THREE BARRELS WHERE THE MESH PUTS 1.10 A (18 Sep 2026)
# The rule's one failure on board D is a LAYER TRANSITION, and it is one barrel, measured rather than assumed. On the
# committed D12 board `via_current` reads exactly one rail over its weakest transition: a 0.40 mm barrel at case
# (-28.59, 25.81) carrying 1.10 A of dc_drop's solved mesh against 0.90 A for its own wall at 10 K with the
# fabricator's 18 um plating, ratio 1.22. Two answers were measured before this one and both are refused: the PWR
# class via at 1.2/0.6 cost NINE connections of 133 (D14, and its via-cost round came back ten), and `via_parallel`,
# which lays a parallel barrel in the finish, found no linkable site within 6 mm of it because the neighbourhood is
# FB1, C5, R3 and LED1 with their ground pads. What is left is the generator, which does not have to search: it knows
# where the parts are, and the corridor between the ferrite's output pad and its own bulk capacitor is empty.
#
# WHAT IS DRAWN, in the board's own coordinates, all of it locked so the router keeps it: FB1 pad 2 (the ferrite's
# output, x -28.65 to -27.78, y 21.73 to 22.93) is joined to C5 pad 1 (the 47 uF bulk, x -30.28 to -29.13, y 24.68 to
# 27.38) by a 0.5 mm F.Cu run north then west, THREE through barrels are stitched into that run 0.8 mm apart, and a
# 0.5 mm B.Cu run joins the three on the other side. Three barrels between the same two nodes are in parallel, so the
# 1.10 A divides: about 0.37 A each against the 0.90 A one barrel is rated for. 0.5 mm carries 1.1 A with margin on
# outer copper (IPC-2221 asks 0.35 mm at 10 K), and the clearances were read off the board before the line was drawn:
# 0.64 mm to C5's ground pad, 0.67 mm to C5 pad 1's east edge, 0.60 mm to R3's ground pad, against the 0.127 mm class.
# It is not a keep-out and not a band: a locked track adds no rule area, so unlike the 1.2 mm class via this costs the
# router nothing it can measure. Judged on the routed board by `via_current` (PI-003) with `dc_drop` beside it.
_pc.spine("+5V_SA", -28.21, 22.33, -28.21, 25.40, 0.5, pcbnew.F_Cu)     # north out of FB1 pad 2, between C5's two pads
_pc.spine("+5V_SA", -28.21, 25.40, -29.60, 25.40, 0.5, pcbnew.F_Cu)     # west into C5 pad 1, clear of R3's ground pad by 0.60 mm
_pc.spine("+5V_SA", -28.21, 23.60, -28.21, 25.20, 0.5, pcbnew.B_Cu)     # the other side of the three barrels
_pc.stitch("+5V_SA", [(-28.21, 23.60), (-28.21, 24.40), (-28.21, 25.20)], amps=1.10)   # 0.8 mm apart: 0.4 mm hole to hole against the 0.3 floor; amps= makes the count self-checking (1.10 A of solved mesh needs two 0.40 mm barrels, three are laid)
print("D11 power copper: the +5V_D8 trunk and west branch on In2, %d zone(s) and keep-out(s)" % len(_pc.made))
for L in (pcbnew.In2_Cu, pcbnew.F_Cu, pcbnew.B_Cu): pour(L, "GND", "GND pour %s" % board.GetLayerName(L), (-50, -40, 50, 40), priority=0)
ds = board.GetDesignSettings(); ns = ds.m_NetSettings
def cls(nc, clr, tw, vd, vdr):
    nc.SetClearance(FromMM(clr)); nc.SetTrackWidth(FromMM(tw)); nc.SetViaDiameter(FromMM(vd)); nc.SetViaDrill(FromMM(vdr))
DEFAULT = (0.127, 0.25, 0.6, 0.3); cls(ns.GetDefaultNetclass(), *DEFAULT)
PATTERNS = [("+5V_*", "PWR"), ("+3V3*", "PWR"), ("VGG_SW", "PWR"), ("GND", "PWR"), ("RF_*", "RF"), ("USB*", "USB"), ("HUB_D*", "USB")]
# SENSE: every net pcb_sensitive.yaml declares for this board, in a class of its own with the default geometry, listed ahead
# of the table so a sensitive net wins over a pattern that also names it; the DSN class-pair clearance of route_one.sh
# (FR_CLASS_CLEAR, appendix 32.222) is what reads it (17 September 2026, rule ANA-001).
try:
    import yaml as _yaml, os as _os
    _sens = ((_yaml.safe_load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "pcb_sensitive.yaml"))) or {}).get("boards") or {}).get("d") or {}
    _sens_nets = [n["net"] for n in (_sens.get("nodes") if isinstance(_sens, dict) else _sens) or []]
except BaseException as _e:
    _sens_nets = []; print("SENSE class: pcb_sensitive.yaml not read (%s), no sensitive net moves class" % type(_e).__name__)
PATTERNS = [(n, "SENSE") for n in _sens_nets] + PATTERNS
print("SENSE class: %d declared sensitive net(s) take it" % len(_sens_nets))
PATTERNS += [("/" + pat, cls) for pat, cls in PATTERNS if not pat.startswith("/")]   # 5 Sep 2026 (gateway finding, MESHSAT-802): root-sheet labels are "/NAME" on the board and KiCad's pattern matcher does not strip the slash, so every label pattern is emitted in both forms; power symbols (GND, +3V3) have no slash
try:
    # OWNER RULING 12 September 2026, decision 9: PWR goes from 0.5 mm to 1.2 mm. `+5V_D8` carries 1 A and a
    # 0.5 mm inner-layer track is rated 0.44 A by IPC-2221 at a 10 K rise, so the board was over the published
    # limit by more than a factor of two on a rail that feeds the exciter and the 30 W amplifier. 1.2 mm carries
    # 1 A with margin. The board is re-routed and its deliverable re-cut; the alternative considered and not
    # taken was accepting five millivolts over budget on the grounds that the radio only draws it while
    # transmitting, which is a coherent position on a duty-cycled rail and not one to buy boards on.
    CLASSES = [("SENSE", 0.127, 0.25, 0.7, 0.3),   # 0.7/0.3: a 0.20 mm ring, the annular floor this board declares; 0.6/0.3 left E12 with ten annular_width violations (18 September 2026)
    # THE POWER CLASS VIA IS 1.2/0.6 SINCE D13 (18 September 2026, rule PI-003): D12's +5V_SA crosses layers through
    # ONE router via at each of two transitions, 1.10 A of the solved mesh through a 0.4 mm drill rated 0.90 A at
    # 10 K with the fabricator's 18 um plating (via_current, both barrels beside FB1); a 0.6 mm drill is rated
    # 1.19 A, so the class via answers it at the source where via_parallel found a site for only one of the two.
               # THE POWER VIA IS BACK AT 0.8/0.4 AND HERE IS WHAT THE WIDE ONE COST (18 September 2026, D14).
               # D13 was credited with answering PI-003 through a 1.2/0.6 class via and never carried it: its
               # project file still held the hand-typed table, so its DSN exported Via[0-3]_800:400_um. D14 is the
               # first D route whose DSN really carries 1.2/0.6, and it landed 0 hard with NINE open of 133 nets
               # where D12 at 0.8/0.4 routed 0 and 0; its second round with the via-cost remedy came back ten, so
               # round one's nine stands and the closers took none of them (the stub router closed 0 of 9).
               # PI-003 is ADVISORY (via_current measures and does not bar), and the two barrels it names on
               # +5V_SA carry 1.10 A against 0.90: paying nine connections on a 133-net board to answer an
               # advisory rule is not a trade. The answer PI-003 wants is locked copper at the transition, board D's
               # own +5V_D8 pattern, and it IS DRAWN now: three parallel barrels between FB1 pad 2 and C5 pad 1 (see
               # the +5V_SA block above), which divides the 1.10 A the mesh measures instead of widening one hole.
               ("PWR", 0.127, 0.5, 0.8, 0.4),
               ("RF", 0.3, 0.35, 0.6, 0.3),
               ("USB", 0.127, 0.3, 0.6, 0.3)]   # ONE table for the board's classes AND the project file's (18 September 2026): a second hand-written copy in the project file had drifted (D's PWR via 1.2/0.6 on the board, 0.8/0.4 in the file the router reads; SENSE absent from the file on D, E and P; SENSE 0.6/0.3 on P), the defect B fixed for itself on 8 September
    for _nm, *_v in CLASSES:
        _nc = pcbnew.NETCLASS(_nm); cls(_nc, *_v)
        if _nm == "USB": _nc.SetDiffPairWidth(FromMM(0.3)); _nc.SetDiffPairGap(FromMM(0.2))   # 8 Sep 2026 (32.71): 0.30/0.20 on the 7628 outer layer computes 89 ohm
        ns.SetNetclass(_nm, _nc)
    for pat, name in PATTERNS: ns.SetNetclassPatternAssignment(pat, name)
except Exception as e: print("note: net class API:", e)
# --- PI-003's generator answer for board D (20 September 2026). `barrel_sites --suggest` on the board sweep
#     32 judged reports the WHOLE of board D's PI-003 as TWO barrels, both `+5V_SA` and both at ratio 1.22:
#     the rail crosses layers twice and each crossing is a single 0.40 mm barrel carrying 1.10 A against the
#     0.90 A its own wall holds at 10 K. That is 18 September's finding, where `via_current` reported each
#     rail's WORST barrel and the record said "one" all day.
#
#     Each wants two barrels and the room differs: the site at (-28.59, 25.81) has 0.57 mm to the nearest
#     pad's COPPER on its clear axis and the one at (-31.15, 17.96) has 1.20. A two-barrel lattice at the
#     0.80 mm pitch needs about 0.70 from the centre, so the second fits with margin and the first is
#     MARGINAL BY THE TOOL'S OWN NUMBER. Board E's `DC_F` was refused at exactly this and the chain is what
#     said so, three runs of it, so both are offered here and the chain decides: a site that comes back with
#     a clearance item is declined with its number, the way `DC_F` and board A's `VBUS20` busbar site are.
if os.environ.get("PLACE_D_BARRELS", "1") not in ("0", ""):
    _d_refused = []
    # AND THE MARGINAL ONE IS REFUSED, WHICH D20 MEASURED. The site at (-28.59, 25.81) had 0.57 mm to the
    # nearest pad's copper where a two-barrel lattice at 0.80 mm pitch needs about 0.70, and the chain came
    # back `hole_to_hole` at 0.0342 mm: the second barrel lands on a hole that is already there. Declined
    # with its number, which is board E's `DC_F` and board A's `VBUS20` busbar site for the third time, and
    # the room figure predicted it, which is what that number was corrected for this morning.
    for _n, _at, _a, _d, _ax in [("+5V_SA", (-31.15, 17.96), 1.100, 0.40, "y")]:
        try: _pc.cluster(_n, _at, amps=_a, drill=_d, axis=_ax)
        except Exception as _e: _d_refused.append("%s at %s: %s" % (_n, _at, _e))
    print("power copper: board D's two +5V_SA layer transitions clustered%s"
          % ("; REFUSED: " + "; ".join(_d_refused) if _d_refused else ""))
_pc.write_provenance(BOARD)
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
