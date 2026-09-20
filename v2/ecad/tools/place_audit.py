#!/usr/bin/env python3
"""The placement instrument (MESHSAT-862 Stage D, 8 Sep 2026, appendix 32.64 W3; rewritten 02:20 after the first calibration attempt):
a minute-scale predictor of where the router will fail, run on the placed board AFTER the escape pass (escape.py, join_adjacent_pins.py,
prefanout.py) and before any route is bought. Until 8 Sep the loop closed only through a full route (A22's INA226 fans at 8 mm pitch after
run 10, B16's HDMI switches at 9.6 mm after a 3 h 20 min route).

No fitted constant: the escape pass itself is the measurement. Its output on the board is the locked copper (stubs, knees, vias) of every
fine-pitch part, so the predictor reads:
  1. fine-pitch pads without an escape: a part with none (excluded by ESCAPE_SKIP, or escape.py placed none) within NEAR mm of another
     fine-pitch part is a FAIL (the router must fan a crowded row itself: B16's HDMI switches, A22's INA226 row of run 10); a part missing
     at least 3 and 30 percent of its escapes is a FAIL (the fan could not be placed); 1 or 2 missing pads are a WARN (the clean released
     boards carry those and routed);
  2. escape envelopes (the bounding box of each part's locked pieces within REACH mm) are reported as a Stage E feature only: on every clean
     released board neighbouring fans overlap in bounding box with their vias interleaved, so the overlap is not a verdict; the escape pass
     and the pre-route DRC (0 hard) are the proof that the fans fit;
  3. escapes that the pre-route DRC found in a hard violation (out/<name>-pruned.txt from escape_prune.py): a WARN per pad (pruned_gate.py
     judges them after the route; B16's generation prunes six), a FAIL from twelve pads on.
Also reported: pin density per 20 mm tile, the HPWL of every net over its pad centres, and the decoupling loop lengths from the intent file
before the route (3 mm rule, FAIL beyond it). A PNG (--png) shows the envelopes, red where they collide.

Usage: place_audit.py <board.kicad_pcb> [--png out.png] [--near 6] [--reach 5] [--skip REF,REF]   -> exit 1 on a predicted collision."""
import sys, os, math, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import return_via   # the free-site test of the return-via fixer, one answer to "can a via go here"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

NEAR = 6.0; REACH = 5.0

def pitch_of(fp):
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = None
    for i in range(len(pads)):
        for j in range(i + 1, min(len(pads), i + 8)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if d > 0 and (best is None or d < best): best = d
    return best / 1e6 if best else None

def fine_pitch(fp):
    if re.search(r"SOT-23-[68]|SOT-583|TSOT-23-6|SOT23-6", fp.GetFPIDAsString()): return True
    p = pitch_of(fp); return p is not None and p <= 0.65

def pts(t): return [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]

def escape_envelopes(b, fine, reach=REACH, locked=None):
    """{ref: (x0, y0, x1, y1) mm of the part's locked escape pieces} and {ref: (pads with an escape, [pads without])} from the board after escape.py."""
    locked = [t for t in b.GetTracks() if t.IsLocked()] if locked is None else locked
    env = {}; escaped = {}
    for f in fine:
        bb = f.GetBoundingBox(False, False); nets = {p.GetNetname() for p in f.Pads() if p.GetNetCode() > 0}
        box = (bb.GetLeft() - int(reach * 1e6), bb.GetTop() - int(reach * 1e6), bb.GetRight() + int(reach * 1e6), bb.GetBottom() + int(reach * 1e6))
        mine = [t for t in locked if t.GetNetname() in nets and any(box[0] <= q.x <= box[2] and box[1] <= q.y <= box[3] for q in pts(t))]
        if mine:
            xs = [q.x for t in mine for q in pts(t)]; ys = [q.y for t in mine for q in pts(t)]
            env[f.GetReference()] = (min(xs) / 1e6, min(ys) / 1e6, max(xs) / 1e6, max(ys) / 1e6)
        got = 0; miss = []
        for p in f.Pads():
            if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or p.GetNetCode() <= 0: continue
            pb = p.GetBoundingBox(); pb.Inflate(int(0.05e6))
            if any(t.GetNetname() == p.GetNetname() and any(pb.Contains(q) for q in pts(t)) for t in mine): got += 1
            else: miss.append(p.GetNumber())
        escaped[f.GetReference()] = (got, miss)
    return env, escaped

def overlap(a, b): return max(0.0, min(a[2], b[2]) - max(a[0], b[0])), max(0.0, min(a[3], b[3]) - max(a[1], b[1]))

def main(a):
    if not a: print(__doc__); return 2
    near = float(verdict.opt(a, "--near", NEAR)); reach = float(verdict.opt(a, "--reach", REACH))
    skip = (set(str(verdict.opt(a, "--skip", "")).split(",")) - {""}) if "--skip" in a else set(os.environ.get("ESCAPE_SKIP", "").split(",")) - {""}
    b = pcbnew.LoadBoard(a[0]); lines = []; coll = 0
    fps = list(b.GetFootprints()); fine = [f for f in fps if fine_pitch(f)]
    locked = [t for t in b.GetTracks() if t.IsLocked()]
    # A PLACEMENT RULE JUDGED ON A ROUTED BOARD IS JUDGED ON THE WRONG ARTEFACT (18 September 2026, sweep 26).
    # This predictor's subject is the PLACED board after the escape pass: which fans will collide, which pads have
    # no escape. On a routed board the router has covered escapes and the closers have pruned dangling ones, so
    # the same predictor read 19 collisions on B21 where its placed board read 10, and the sweep wrote that over
    # the placed reading. A placed board's tracks are locked to the last one (escapes, joins, pre-laid pairs,
    # spines); a routed board carries thousands the router laid unlocked (B21 12,739 of 17,361, A32 3,928 of
    # 4,854). Such a board is not this rule's input: INCONCLUSIVE with the input named, which never replaces the
    # placed snapshot's reading. `--on-routed` is for a person who wants the number anyway.
    _segs = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
    _unlocked = [t for t in _segs if not t.IsLocked()]
    if "--on-routed" not in a and len(_unlocked) > 100 and len(_unlocked) > 0.2 * len(_segs):
        print("place_audit: INCONCLUSIVE this is a ROUTED board (%d of %d track segments unlocked, laid by the router): the "
              "placement predictor is judged on the placed snapshot, not here (--on-routed to force)" % (len(_unlocked), len(_segs)))
        return verdict.write("place_audit", verdict.INCONCLUSIVE,
                             counts={"unlocked_segments": len(_unlocked), "segments": len(_segs), "fine_pitch": len(fine), "footprints": len(fps)},
                             denominator=0, inputs={"board": a[0]},
                             missing_input="the placed board: this one is routed (%d of %d segments unlocked), and the escapes the "
                                           "router covered or the closers pruned are not what this rule predicts" % (len(_unlocked), len(_segs)))
    env, escaped = escape_envelopes(b, fine, reach, locked)
    # 1. unescaped pads
    for f in fine:
        r = f.GetReference(); got, miss = escaped[r]
        if r in skip or got == 0:
            others = [g.GetReference() for g in fine if g is not f and math.hypot(g.GetPosition().x - f.GetPosition().x, g.GetPosition().y - f.GetPosition().y) / 1e6 <= near + (f.GetBoundingBox(False, False).GetWidth() + g.GetBoundingBox(False, False).GetWidth()) / 2e6]
            if others: lines.append("FAIL  %s has no escapes (%s) and stands within %.0f mm of %s: the router has to fan a crowded row itself" % (r, "excluded by ESCAPE_SKIP" if r in skip else "escape.py placed none", near, ", ".join(others[:4]))); coll += 1
            else: lines.append("WARN  %s has no escapes (%s), nothing fine-pitch near it" % (r, "excluded by ESCAPE_SKIP" if r in skip else "escape.py placed none"))
        elif miss and len(miss) >= max(3, int(0.3 * (got + len(miss)))):   # the clean released boards carry 1 to 2 skipped pads per part and routed; a fan mostly missing is the INA226 case
            lines.append("FAIL  %s: %d of %d fine-pitch pads without an escape (pads %s): the fan could not be placed" % (r, len(miss), got + len(miss), ",".join(miss[:8]))); coll += 1
        elif miss:
            lines.append("WARN  %s: %d of %d fine-pitch pads without an escape (pads %s): the router's job, pruned_gate-style check after the route" % (r, len(miss), got + len(miss), ",".join(miss[:8])))
    # 2. envelope overlaps: the bounding boxes of neighbouring fans overlap on every clean board (interleaved vias), so this is a feature for Stage E, not a verdict
    refs = sorted(env); ov_area = 0.0; ov_n = 0
    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            ox, oy = overlap(env[refs[i]], env[refs[j]])
            if ox > 0.3 and oy > 0.3: ov_area += ox * oy; ov_n += 1
    lines.append("INFO  escape envelopes: %d overlapping pairs, %.0f mm2 (a Stage E feature; the escape pass and the pre-route DRC already proved the fans fit)" % (ov_n, ov_area))
    # 3. pruned escapes
    pr = os.path.join(os.path.dirname(os.path.abspath(a[0])), "out", os.path.splitext(os.path.basename(a[0]))[0] + "-pruned.txt")
    if os.path.exists(pr):
        rows = [l.split("\t") for l in open(pr).read().splitlines() if l and not l.startswith("#")]
        # a pad whose escape was pruned but which now carries locked copper of its own net is SERVED, not a disagreement: the pair
        # pre-router lays into the pads of its classes and the escape it displaced was redundant. B17 counted 84 such pads as a
        # failure while every one of them belongs to a pre-laid Ethernet or switch pair (8 Sep 2026 18:05).
        locked_ends = {}
        for t in b.GetTracks():
            if t.GetClass() == "PCB_TRACK" and t.IsLocked():
                locked_ends.setdefault(t.GetNetname(), []).append((t.GetStart(), t.GetEnd()))
        served = []; orphan = []
        for row in rows:
            f = b.FindFootprintByReference(row[1]); pad = next((q for q in f.Pads() if q.GetNumber() == row[2]), None) if f else None
            ok = False
            if pad is not None:
                pb = pad.GetBoundingBox(); pb.Inflate(int(0.05e6))
                for a_, b_ in locked_ends.get(pad.GetNetname(), []):
                    if pb.Contains(a_) or pb.Contains(b_): ok = True; break
            (served if ok else orphan).append(row)
        for row in orphan: lines.append("WARN  the escape of %s.%s (%s) sat in a hard violation and was pruned: the pad is the router's; pruned_gate.py checks it after the route" % (row[1], row[2], row[0]))
        if served: lines.append("INFO  %d of %d pruned escapes are on pads that pre-laid copper of their own net already reaches" % (len(served), len(rows)))
        # WHAT the escape collided with decides whether this is a placement fault (8 Sep 2026 23:10, MESHSAT-862; escape_prune.py records it).
        # A counterparty PAD means two parts sit too close for the escape to exist at all: the placement has to change and that is a FAIL here.
        # Anything else (a track or a via) is copper this pipeline laid itself, the fanout vias and the pre-routed pairs, which took the lane
        # the escape wanted; the router can still serve the pad on another layer and `pruned_gate.py` refuses the board after the route if it
        # did not. On B17 that split is 6 against 28, and blocking the chain on the 28 would be blocking it on our own pre-route.
        # ...and only when that pad belongs to ANOTHER part. An escape that shorts a neighbouring pad of its OWN connector is a fault of the
        # escape geometry for that footprint, not of the placement, and moving parts cannot fix it; on B17 seven of the sixteen were
        # J_HDMI against J_HDMI and J_LIME against J_LIME (9 Sep 2026 00:45). They are counted and named on their own line.
        def _other_ref(r):
            m = re.search(r" of ([A-Za-z_][A-Za-z0-9_]*)", r[6]) if len(r) > 6 else None
            return m.group(1) if m else None
        pad_rows = [r for r in orphan if len(r) > 6 and r[6].strip().startswith("Pad")]
        own_pad = [r for r in pad_rows if _other_ref(r) == r[1]]
        by_pad = [r for r in pad_rows if _other_ref(r) != r[1]]
        if own_pad: lines.append("INFO  %d pruned escapes shorted another pad of their OWN part: the escape geometry for that footprint, not the placement (%s)" % (len(own_pad), ", ".join(sorted({r[1] for r in own_pad}))))
        displaced = len(orphan) - len(by_pad)
        if displaced: lines.append("INFO  %d of %d pruned escapes were displaced by copper this pipeline laid (fanout vias, pre-routed pairs), not by the placement" % (displaced, len(orphan)))
        if len(by_pad) >= 12: lines.append("FAIL  %d escapes pruned against another part's PAD: the placement cannot carry the escape at that many pads (%d more were displaced by our own pre-route copper)" % (len(by_pad), displaced)); coll += 1
        elif len(orphan) >= 12: lines.append("NOTE  %d escapes pruned, %d of them against a pad; the rest are the router's to close and pruned_gate.py judges them after the route" % (len(orphan), len(by_pad)))
    # pin density and HPWL
    edge = b.GetBoardEdgesBoundingBox(); ex0, ey0, ex1, ey1 = edge.GetLeft() / 1e6, edge.GetTop() / 1e6, edge.GetRight() / 1e6, edge.GetBottom() / 1e6
    tiles = {}
    for f in fps:
        for p in f.Pads():
            k = (int((p.GetPosition().x / 1e6 - ex0) // 20), int((p.GetPosition().y / 1e6 - ey0) // 20)); tiles[k] = tiles.get(k, 0) + 1
    busiest = sorted(tiles.items(), key=lambda kv: -kv[1])[:5]
    lines.append("INFO  pin density: busiest 20 mm tiles (pads per cm2): %s" % ", ".join("(%d,%d) %.0f" % (k[0], k[1], n / 4.0) for k, n in busiest))
    nets = {}
    for f in fps:
        for p in f.Pads():
            if p.GetNetCode() > 0: nets.setdefault(p.GetNetname(), []).append((p.GetPosition().x / 1e6, p.GetPosition().y / 1e6))
    hp = {n: (max(x for x, y in q) - min(x for x, y in q)) + (max(y for x, y in q) - min(y for x, y in q)) for n, q in nets.items() if len(q) > 1}
    top = sorted(hp.items(), key=lambda kv: -kv[1])[:10]
    lines.append("INFO  HPWL: %.0f mm over %d nets; longest %s" % (sum(hp.values()), len(hp), ", ".join("%s %.0f" % (n.lstrip("/"), v) for n, v in top)))
    try:
        import intent; it = intent.load(a[0])
    except Exception: it = None
    # a declared decoupling capacitor too far from its pin is a real defect and blocks, unless the project carries `bypass-allow.txt`
    # with a reason line, the same idiom as erc-allow.txt and lcsc-allow.txt: known, written down, and still counted in the report
    # (8 Sep 2026: declaring the D board's sixteen capacitors blocked a board that was one connection from clean, on a finding whose
    # fix is a floor-plan change across the whole set and an owner decision, so it is recorded rather than hidden or silently passed)
    allow = os.path.join(os.path.dirname(os.path.abspath(a[0])) or ".", "bypass-allow.txt")
    allowed = [l.strip() for l in open(allow).read().splitlines() if l.strip() and not l.startswith("#")] if os.path.exists(allow) else []
    if it and it.get("bypass"):
        pads = {(f.GetReference(), p.GetNumber()): p for f in fps for p in f.Pads()}; far = 0
        for e in it["bypass"]:
            pin = pads.get((e["part"], e["pin"])); cap = [p for (ref, num), p in pads.items() if ref == e["cap"] and pin is not None and p.GetNetname() == pin.GetNetname()]
            if pin is None or not cap: continue
            d = math.hypot(cap[0].GetPosition().x - pin.GetPosition().x, cap[0].GetPosition().y - pin.GetPosition().y) / 1e6
            if d > 3.0:
                far += 1
                lines.append("%s  bypass %s sits %.1f mm from %s.%s before the route (3 mm rule)%s" % ("ALLOW" if allowed else "FAIL ", e["cap"], d, e["part"], e["pin"], (" [" + allowed[0][:60] + "]") if allowed else ""))
        lines.append("INFO  decoupling: %d of %d bypass capacitors within 3 mm of their pin%s" % (len(it["bypass"]) - far, len(it["bypass"]), " (%d allowed by bypass-allow.txt)" % far if allowed and far else ""))
        if not allowed: coll += far
    else: lines.append("INFO  decoupling: 0 of 0 bypass entries (no intent file or none listed)")
    # 5. two classes A's phases A33 to A35 found only after a five-hour route (15 September 2026, red team round four M1):
    #    a PLANE PAD with no path to its plane (no via of its net within reach, not inside a fill of its net on its own
    #    layer, no locked copper leaving it), which the fanout skipped for want of room and the router then had to reach
    #    by a wire; and a RAIL POUR on an outer layer with no track keep-out on its layer, which the router slices (A34's
    #    PA head island filled 51 of 102 mm2). The first is a FAIL, the second a WARN (A's VIN_RAW dock top is drawn
    #    without a keep-out on purpose: the header's signal pins escape there).
    try:
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    except Exception: pass
    zone_nets = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetFilledArea() <= 0: continue
        zone_nets.setdefault(z.GetNetname(), []).append(z)
    vias_by_net = {}
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA": vias_by_net.setdefault(t.GetNetname(), []).append(t.GetPosition())
    locked_starts = set()
    for t in locked:
        if t.GetClass() == "PCB_TRACK": locked_starts.add((t.GetStart().x, t.GetStart().y)); locked_starts.add((t.GetEnd().x, t.GetEnd().y))
    # A PAD WITH COPPER ON IT IS REACHED, WHOEVER LAID THE COPPER (17 September 2026). The locked set above is
    # the pre-router's and the generator's; a ROUTED board also has the router's tracks, and this class was
    # reading a routed board as though it were a placed one. Board D's PLC-001 failed on U6.2 and C3.1, two
    # +5V_D8 pads with no free via site within 1.5 mm, ON A BOARD THAT ROUTES 0 HARD AND 0 UNROUTED: the router
    # answered the prediction with a track and the predictor did not look. The rule this tool exists for is
    # that a pad have SOMEWHERE to go; copper already there is the strongest form of that.
    track_ends = {}
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK": continue
        track_ends.setdefault(t.GetNetname(), []).append((t.GetStart(), t.GetEnd(), t.GetLayer()))
    unreached = []
    track_keepouts = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowTracks()]
    ds = b.GetDesignSettings(); via_d = max(0.4, ds.m_ViasMinSize / 1e6); clr = max(0.127, ds.m_MinClearance / 1e6)
    for f in fps:
        for p in f.Pads():
            n = p.GetNetname()
            if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or n not in zone_nets or p.GetNetCode() <= 0: continue
            c = p.GetPosition()
            if any(math.hypot(v.x - c.x, v.y - c.y) <= 1.5e6 for v in vias_by_net.get(n, [])): continue
            if (c.x, c.y) in locked_starts: continue
            _r = max(p.GetSize().x, p.GetSize().y) / 2.0
            if any(lay == (pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
                   and (math.hypot(e0.x - c.x, e0.y - c.y) <= _r or math.hypot(e1.x - c.x, e1.y - c.y) <= _r)
                   for e0, e1, lay in track_ends.get(n, [])): continue
            L = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            if any(z.GetFirstLayer() == L and z.GetFilledPolysList(L).Contains(c) for z in zone_nets[n]): continue
            # The pad has no connection YET, which is the normal state of a plane pad before the route (A36's placed board
            # had 244 such pads and the first form of this class refused the board for them, 15 September 2026 20:04 UTC:
            # a hypothesis about the data). The A33 to A35 class is narrower: the pad has NOWHERE to go, no free via site
            # within 1.5 mm at the board's own via and clearance, or a track keep-out on its own layer over its centre.
            cx, cy = c.x / 1e6, c.y / 1e6
            if any(k.IsOnLayer(L) and k.Outline().Contains(c) for k in track_keepouts): unreached.append("%s.%s (%s, under a track keep-out)" % (f.GetReference(), p.GetNumber(), n.lstrip("/"))); continue
            if any(return_via._site_free(b, round(cx + r * math.cos(k * math.pi / 8), 3), round(cy + r * math.sin(k * math.pi / 8), 3), via_d, clr, n) for r in (0.6, 1.0, 1.5) for k in range(16)): continue
            unreached.append("%s.%s (%s, no via site)" % (f.GetReference(), p.GetNumber(), n.lstrip("/")))
    if unreached:
        lines.append("FAIL  %d plane pad(s) with no path to their plane before the route (no via within 1.5 mm, not in their own fill, no locked copper, and no free via site within 1.5 mm or a track keep-out over the pad): %s" % (len(unreached), ", ".join(unreached[:12]) + (" ..." if len(unreached) > 12 else ""))); coll += 1
    else:
        lines.append("INFO  every plane pad reaches its plane before the route (a via, its own fill, or locked copper)")
    keepouts = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowTracks()]
    bare = []
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetFirstLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu) or z.GetNetname().lstrip("/") == "GND": continue
        bb = z.GetBoundingBox(); c = bb.GetCenter()
        if not any(k.GetFirstLayer() == z.GetFirstLayer() and k.Outline().Contains(c) for k in keepouts): bare.append("%s (%s on %s)" % (z.GetZoneName()[:30], z.GetNetname().lstrip("/"), b.GetLayerName(z.GetFirstLayer())))
    if bare: lines.append("WARN  %d rail pour(s) on an outer layer with no track keep-out on their layer, which the router may slice (A34's PA head): %s" % (len(bare), "; ".join(bare[:8]) + (" ..." if len(bare) > 8 else "")))
    # 6. THE POUR-ISLAND CLASS, PREDICTED AS FAR AS A PLACED BOARD CAN (17 September 2026, rule PLC-002's last
    # remaining clause). `pour_stitch` repairs a filled island that carries no via of its own net, on every
    # board and every round, and the closer register recorded that nothing predicts it before the route is
    # bought. Half of it can be seen here and half cannot, and the half that cannot is said out loud rather
    # than implied: an island the ROUTER cuts out of a pour does not exist yet on a placed board, and no
    # reading of this board can produce it. What does exist is a pour that is born islanded, which is a
    # generator fact and the cheaper half to fix, because it needs no route to find and no route to prove.
    # It reads the fill the board already carries and never refills: a stage that runs in every chain must not
    # buy a minute of zone filling, and a board whose zones are unfilled is told so instead of being passed.
    # AND IT NEVER TAKES A CHAIN DOWN WITH IT. This stage blocks every placement, so a reading it cannot take
    # is reported as a reading it cannot take: the KiCad 9 geometry calls below are the ones that differ most
    # between builds, and a gate that raises here would refuse a board for a reason that has nothing to do with
    # the board.
    _isl, _padonly, _unfilled, _zones = [], [], 0, 0
    try:
      for z in b.Zones():
         if z.GetIsRuleArea(): continue
         _zones += 1
         _net = z.GetNetname().lstrip("/")
         _lay = z.GetFirstLayer()
         try: _polys = z.GetFilledPolysList(_lay)
         except BaseException: _polys = None
         if _polys is None or _polys.OutlineCount() == 0:
             _unfilled += 1; continue
         _sites = [t.GetPosition() for t in b.GetTracks()
                   if t.GetClass() == "PCB_VIA" and t.GetNetname().lstrip("/") == _net]
         _sites += [pad.GetPosition() for f in fps for pad in f.Pads()
                    if pad.GetNetname().lstrip("/") == _net and pad.GetDrillSizeX() > 0]
         # A SITE ON THE ISLAND'S OWN BOUNDARY IS ON THE ISLAND (21 September 2026, D31). One run of board D's chain
         # was refused here for a 1 mm2 piece of the F.Cu ground pour between R15 and R13 whose one connection is
         # R15's ground pad with the fanout's via IN it, both at (118.4, 92.875), which is the island's top edge to
         # the micrometre: PointInside answers False for a point exactly on the outline, KiCad's own fill had
         # already answered IsIsland False for the same polygon, and the run before had passed on the same seat
         # because its fanout (not deterministic) had drawn the piece a hair differently. A via or a pad centre
         # within 0.1 mm of the outline counts as on it; KiCad's PointInside takes that as its accuracy argument.
         # AND AN ISLAND WHOSE ONLY SITE IS A SURFACE PAD OF ITS OWN NET IS REPORTED, NOT REFUSED: the pad is the
         # router's to connect (a fanout-skipped pad, which pruned_gate reads after the route), so the copper is
         # reached by whatever reaches the pad. Board A's six F.Cu load bank islands of A87 to A92 read that way
         # (their vias had been renamed, their rail pads had not), and the refusal there is the VBAT In2 piece and
         # the In3 runs, which carry NO pad of their net; power_copper's pad guard now refuses the rename at the
         # stitch, so this judge is the second line and not the first.
         _smd = [pad.GetPosition() for f in fps for pad in f.Pads()
                 if pad.GetNetname().lstrip("/") == _net and pad.GetDrillSizeX() == 0 and pad.IsOnLayer(_lay)]
         _ON = 100000                                   # 0.1 mm: a site on the outline is on the island
         for _i in range(_polys.OutlineCount()):
             _o = _polys.Outline(_i)
             _a = abs(_o.Area()) / 1e12
             if _a < 1.0: continue                     # under a square millimetre is not a pour, it is a sliver
             if any(_o.PointInside(pcbnew.VECTOR2I(int(pt.x), int(pt.y)), _ON) for pt in _sites): continue
             _c = _o.BBox().Centre()
             _line = "%s on %s, %.0f mm2 at (%.1f, %.1f)" % (_net or "no net", b.GetLayerName(_lay), _a, _c.x / 1e6, _c.y / 1e6)
             if any(_o.PointInside(pcbnew.VECTOR2I(int(pt.x), int(pt.y)), _ON) for pt in _smd):
                 _padonly.append(_line); continue
             _isl.append(_line)
    except BaseException as _e:
        lines.append("INFO  the pour-island prediction could not be taken on this board (%s: %s); nothing is "
                     "claimed about that class here" % (type(_e).__name__, str(_e)[:80]))
    if _unfilled:
        lines.append("INFO  %d of %d zone(s) carry no fill on this board, so the pour-island class was not "
                     "predicted for them (fill the board before this stage to have it read)" % (_unfilled, _zones))
    if _padonly:
        lines.append("WARN  %d pour island(s) reach only a surface pad of their own net and no via or plated pad, "
                     "which is a pad the fanout skipped and the router has to connect (read by pruned_gate after "
                     "the route): %s" % (len(_padonly), "; ".join(_padonly[:6]) + (" ..." if len(_padonly) > 6 else "")))
    if _isl:
        # A POUR BORN WITHOUT A VIA IS COPPER THE GENERATOR MEANT TO CONNECT AND DID NOT, AND IT REFUSES THE
        # BOARD NOW (21 September 2026). This line was a WARN, and it named board A's defect on every chain from
        # A87 to A92: each rail's In3 run ended in a column that KiCad had renamed to GND because it sat in the
        # load capacitor's ground pad, so the six load bank islands carried no via of their own net BEFORE any
        # route and the run dead-ended a layer below them. The WARN was printed six times, read by nobody, and
        # the arms routed for a night with no variable in them. Measured across the set before the bar moved:
        # the count is ZERO on every clean chain (A85, A86, A93, B23, C24, D27, D30, E30, P9) and 6 to 9 on
        # exactly the defective arms, with one VBAT In2 piece on A69 and A70, so a refusal fires on the defect
        # and on nothing else. Re-measured with the boundary accuracy and the surface-pad class above (21
        # September, 01:45): A89's pre-route board reads its six load bank islands as WARN and ONE refusal, the
        # 131 mm2 VBAT In2 piece; D31's chain-end board, refused before, reads no refusal. The allow idiom of erc-allow.txt applies: `pour-island-allow.txt` beside the
        # board names a NET whose islanded pour is known and says why, and such an island is reported ALLOW and
        # still counted in the report. The islands a ROUTER cuts out of a pour are the other half of this class
        # and stay pour_stitch's, because they do not exist yet on a placed board.
        _pallow = os.path.join(os.path.dirname(os.path.abspath(a[0])) or ".", "pour-island-allow.txt")
        _pal = [l.strip() for l in open(_pallow).read().splitlines() if l.strip() and not l.startswith("#")] if os.path.exists(_pallow) else []
        _refused = [i for i in _isl if not any(i.split(" on ")[0] == l.split()[0].lstrip("/") for l in _pal)]
        _allowed = [i for i in _isl if i not in _refused]
        if _allowed:
            lines.append("ALLOW %d pour island(s) with no via or plated pad of their own net are declared in "
                         "pour-island-allow.txt: %s" % (len(_allowed), "; ".join(_allowed[:6])))
        if _refused:
            lines.append("FAIL  %d pour island(s) already carry no via or plated pad of their own net BEFORE any "
                         "route: the generator laid copper nothing reaches, and a rail run that ends in one has "
                         "reached nothing (board A's In3 runs, A87 to A92); name the net in pour-island-allow.txt "
                         "with its reason or connect it: %s"
                         % (len(_refused), "; ".join(_refused[:6]) + (" ..." if len(_refused) > 6 else "")))
            coll += 1
    elif _zones and not _unfilled and not _padonly:
        lines.append("INFO  every filled pour on this board reaches a via or a plated pad of its own net; the "
                     "islands a ROUTER cuts out of a pour cannot be predicted from a placed board and are the "
                     "other half of this class")
    n_esc = sum(1 for r in env); lines.append("INFO  escapes measured on %d of %d fine-pitch parts (%d parts, %d locked pieces on the board)" % (n_esc, len(fine), len(fps), len(locked)))
    for l in lines: print("place_audit: " + l)
    print("place_audit: %d predicted collision(s) among %d fine-pitch parts of %d; %s" % (coll, len(fine), len(fps), "FAIL" if coll else "ALL PASS"))
    if "--png" in a:
        try:
            import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; from matplotlib.patches import Rectangle
            fig, ax = plt.subplots(figsize=(14, 9)); ax.add_patch(Rectangle((ex0, ey0), ex1 - ex0, ey1 - ey0, fill=False, lw=1.5))
            for f in fps:
                bb = f.GetBoundingBox(False, False); ax.add_patch(Rectangle((bb.GetLeft() / 1e6, bb.GetTop() / 1e6), bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, fill=True, alpha=0.15, color="gray", lw=0))
            for r, (x0, y0, x1, y1) in env.items():
                bad = any(l.startswith("FAIL") and (" %s " % r in l or " %s:" % r in l or "%s." % r in l or " %s," % r in l) for l in lines)
                ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, color="red" if bad else "green", lw=0.8)); ax.text(x0, y0, r, fontsize=5, color="red" if bad else "green")
            ax.set_xlim(ex0 - 5, ex1 + 5); ax.set_ylim(ey1 + 5, ey0 - 5); ax.set_aspect("equal"); ax.set_title("place_audit: %s, %d predicted collisions (red)" % (os.path.basename(a[0]), coll))
            _png = str(verdict.opt(a, "--png", "place_audit.png"))
            fig.savefig(_png, dpi=130); print("place_audit: image", _png)
        except ImportError: print("place_audit: no matplotlib, no image")
    # The denominator is the fine-pitch parts the predictor could measure: a board where escape.py placed nothing
    # has zero of them, and "0 predicted collisions" there is the absence of a prediction, not a good placement.
    return verdict.write("place_audit",
                         verdict.INCONCLUSIVE if not fine else (verdict.PASS if not coll else verdict.FAIL),
                         counts={"collisions": coll, "fine_pitch": len(fine), "measured": len(env), "footprints": len(fps)},
                         denominator=len(fine),
                         evidence=[l for l in lines if l.startswith("FAIL")][:30],
                         inputs={"board": a[0]},
                         note="" if fine else "no fine-pitch part on this board, so nothing was predicted")

if __name__ == "__main__":
    import verdict as _vg   # a gate that crashes writes INCONCLUSIVE, never nothing (18 September 2026)
    sys.exit(_vg.guard("place_audit", main, sys.argv[1:]))
