#!/usr/bin/env python3
"""The intent gates on a routed board (MESHSAT-862 Stage C, 8 Sep 2026): read out/<stem>-intent.json (intent.py) and the board, and check
  1. return path: every track of EVERY SIGNAL NET (signalnets.classify: not ground, not a net that owns a filled zone, not a rail of the
     intent file, not a power class; owner ruling 15 September 2026 20:15 CEST, "every signal net"; until then only the pair classes with an
     impedance target were judged) has a filled plane (GND or a power net's pour) on the copper layer next to it, sampled every SAMPLE mm; a
     sample with no plane on either neighbouring layer is a gap (an In1 rule-area window around the CM5 receptacles, a plane cut-out, a pour
     the router ate, a two-layer board's back-side track under a front-side track); reported per net as mm of gap, FAIL above the larger of
     GAP_MM or 5 percent of the net's length (via anti-pads and connector ends). A board with tracks and no signal net at all is a FAIL (the
     scope filter swallowed everything); a board with no tracks passes with "0 of 0";
  4. return via: every signal via has a ground via within return_via.RETURN_MM, fine-pitch escape fans exempt (return_via.judge);
  2. decoupling (decision 42, DECOUPLING.md section 6; since 27 September 2026): every bypass entry (capacitor, part, pin) is judged by its
     CLASS, never by its value string (decoupling_rules.limit): its rail pad within the class's screen of the pin's pad (3.0 mm for classes
     R, D and L, 6.0 mm for B2, no distance for A and B1), a maker's own distance as a limit no allowance passes, a capacitor on the side
     opposite its part at its in-plane distance plus the stackup's via allowance and refused inside any escape fan, over a through-hole
     part, on a board assembled on one side and for a part whose maker names the same side; an allowance in bypass-allow.txt names its
     capacitor (`C36: reason`) and makes a JUSTIFIED DEVIATION, which is counted as one and never as a pass; the rail pad reaches a via or
     a pour within 1.5 mm, and a class D or L capacitor's ground pad is asked for a via of its OWN; an entry with no ruled class FAILS;
  3. every rail of the intent file exists on the board with pads on it (a renamed rail is a FAIL, not a silent skip).
A board without an intent file is a FAIL (fail closed). Denominators print on every summary line.
Used as a module by the check_pcb_*.py gates: intent_checks.run(board, check)  or standalone: intent_checks.py <board.kicad_pcb>.

  5. RULE PWR-001 IS JUDGED ON THE NETLIST (26 September 2026, MESHSAT-1357; see rails_on_netlist below): every power net
     of the committed netlist is a declared rail, every declared rail is a net of it and names where its current goes.
     intent_checks.py --netlist <netlist.net> [--intent <intent.json>] [--out-dir DIR]  writes the intent_rails verdict
     alone and needs no KiCad; the board run writes intent_rails from the netlist beside the board when there is one.
     It fails closed: every net carrying the mark of a supply is counted, declared, settled by what the netlist and the
     held datasheets (PIN_ROLES) say, or named as undecided, and the reading records the census of every net."""
import sys, os, math, json, re, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netclass
import intent, signalnets, signal_class
import decoupling_rules as _dr
# THE BOARD HALF NEEDS KiCad AND THE NETLIST HALF DOES NOT (26 September 2026). PWR-001 is a schematic-phase rule and
# its reading is taken on the runner, which has no pcbnew; the board checks below still need it and say so when it is
# missing (run() refuses), rather than failing at import for a caller that never asks for them. Only the absence of
# pcbnew itself is caught: any other import error in these two helpers is a defect and is raised.
try:
    import pcbnew
    import kicad_compat as _kc, return_via
    import fan_select, bypass_search
except ModuleNotFoundError as _e:
    if getattr(_e, "name", "") != "pcbnew": raise
    pcbnew = _kc = return_via = fan_select = bypass_search = None

SAMPLE = 1.0; GAP_MM = 10.0; NEAR_VIA = 1.5

# THE VERDICTS THIS FILE WRITES, one per rule it runs, named at module scope so a reader and the repository
# rule that checks every gate maps to a rule can both see them without executing anything. They were one
# verdict until 16 September, and that meant a single decoupling capacitor 3 mm too far from its pin failed
# the return-path rule as well, on six boards: eighteen rule-board pairs reported as failures of things that
# had passed.
RULE_VERDICTS = ("intent_return_path", "intent_return_via", "intent_decoupling", "intent_rails",
                 "intent_other", "intent_checks")

# The last return-path measurement, for a caller that needs the numbers rather than the sentences. A test that
# captured them by redirecting stdout around this module took KiCad's python down with it (17 September 2026):
# the C++ layer writes to the file descriptor and Python's redirect swaps the object above it, and with the
# process's output on a pipe the two disagreed hard enough to segfault. A measurement worth asserting on is
# worth returning.
LAST = {}
# The decoupling rule's own tally, for the verdict: a justified deviation and a distance that is only recorded
# are neither a pass nor a failure, and `check()` has two answers (decision 42, T6 and T10).
LAST_DECOUPLING = {}

def run(b, check, path=None):
    if pcbnew is None:
        raise SystemExit("intent_checks: the board checks need KiCad's pcbnew, which this host does not have; rule "
                         "PWR-001 alone is judged without it: intent_checks.py --netlist <netlist.net>")
    path = path or b.GetFileName(); it = intent.load(path)
    if not it: check(False, "intent file present (out/<stem>-intent.json from the schematic generator)"); return "intent_checks: no intent file, nothing checked"
    pro = os.path.splitext(path)[0] + ".kicad_pro"; assign = {}
    if os.path.exists(pro): assign = json.load(open(pro)).get("net_settings", {}).get("netclass_assignments", {})
    def cls_of(net): return netclass.class_of(assign, net, "Default")   # KiCad 9 stores the assignment as a list of class names
    targets = {k for k, v in it.get("pair_classes", {}).items() if v}
    cu = list(b.GetEnabledLayers().CuStack())   # KiCad 9: F.Cu 0, In1.Cu 4, In2.Cu 6, ..., B.Cu 2; the stack in order
    if not it.get("rails") and not it.get("bypass") and not it.get("pair_classes"): check(False, "intent file carries at least one rail, bypass entry or pair class (an empty file is not a pass)")
    planes = {}; planes_net = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetFilledArea() <= 0: continue
        n = z.GetNetname().lstrip("/")
        # EVERY filled zone is a reference for the track over it (15 September 2026 23:15 CEST): the list of name prefixes
        # missed E's In2 power pours (VIN_RAW, PV_P, TRK_OUT), so E10 read 18 nets over rule 1 for tracks running over solid
        # copper. A filled zone in this project is ground or a rail (signalnets excludes every zone owner from the signal set
        # on the same ground), so the fill's net name decides nothing here.
        if n:
            pl = z.GetFilledPolysList(z.GetFirstLayer()); planes.setdefault(z.GetFirstLayer(), []).append(pl); planes_net.setdefault((z.GetFirstLayer(), z.GetNetname()), []).append(pl)
    def neighbours(L):
        i = cu.index(L); return [cu[j] for j in (i - 1, i + 1) if 0 <= j < len(cu)]
    # 1. return path, under every signal net (and the pair-class nets, which are signals too but keep their own class in the line)
    signals, _why = signalnets.classify(b, path, it.get("rails", {}).keys())
    # THE HOLE A NET'S OWN VIA MAKES IN ITS REFERENCE IS RET-003's QUESTION, NOT THIS ONE (17 September 2026).
    # The fill retreats around every barrel, so a net that changes layer punches a hole in the very plane it is
    # being judged against, and this measurement counted that hole as a break in the reference. It is not one:
    # the reference is continuous either side of it and what the signal needs THERE is a return transition,
    # which is exactly what RET-003 and RET-004 ask about. On board B's placed board, with the zones filled,
    # the single net over its limit was over it by 0.6 mm and every uncovered run was its own via's anti-pad.
    # The two are separated here: the anti-pad share is measured, reported and handed to the transition rules,
    # and the screen judges what is left, which is a slot, another net's copper, or the fill's own edge.
    _vias = {}
    _VCELL = 2000000       # a 2 mm spatial hash, because the other-net lookup below asks every sample point
    _grid = {}
    for _t in b.GetTracks():
        if _t.GetClass() != "PCB_VIA": continue
        # A via's width is per layer in KiCad 9 and the bare call asserts: kicad_compat.via_width.
        _w = _kc.via_width(_t)
        _p = _t.GetPosition()
        _vias.setdefault(_t.GetNetname(), []).append((_p, _w))
        _grid.setdefault((_p.x // _VCELL, _p.y // _VCELL), []).append((_p, _w, _t.GetNetname()))
    _CLEAR = 300000     # 0.3 mm in KiCad units: the fill's own clearance on these boards, and the larger of the
    # two values any of the seven declares, so this never calls a real slot an anti-pad by being generous.
    def _hole(net, p, Ls):
        """Is this uncovered point a hole in a reference, whose hole is it, or is there no reference at all?

        Returns "own" for a hole around a via of the net being judged, "other" for a hole around ANY other
        conductor's via, and None where the reference is simply not there. The third bucket was added on 18
        September 2026 after board B was measured run by run: of its 675 mm of uncovered signal run over 937
        runs, 884 runs and 601 mm are the anti-pad of ANOTHER net's via, median 0.7 mm and longest 3.0 mm,
        while the reference is genuinely absent for 39 runs and 60 mm. A six-layer board with three compute
        modules has a via field, and this screen was measuring it: its own failure-mode line in the registry
        says so in as many words, "used as a law it refuses good boards (false positives at every via)". The
        return current goes AROUND a 0.7 mm hole; it does not lose its reference. What decides this screen is
        the reference being ABSENT, and both anti-pad shares are reported beside it so that nothing is hidden:
        the own share is RET-003's and RET-004's question, and how perforated a reference may be at all is
        RET-001's, which is owner decision 39.

        An anti-pad is a hole IN a fill. Asking only whether a via of this net is close enough would call
        every point near a via an anti-pad on a board with no pour at all, which is the opposite of the truth
        and would have excused board B's card-slot nets, whose gap is their whole length. So the fill has to
        be there to have a hole in it: the ring just outside the barrel's clearance is sampled, and the point
        counts as an anti-pad only where the reference resumes around it."""
        _own = [(q, w) for q, w in _vias.get(net, ())]
        _near = []
        _cx, _cy = p.x // _VCELL, p.y // _VCELL
        for _i in (-1, 0, 1):
            for _j in (-1, 0, 1):
                for _q, _w, _n in _grid.get((_cx + _i, _cy + _j), ()):
                    if _n != net: _near.append((_q, _w))
        for q, w in [(q, w) for q, w in _own] + _near:
            _whose = "own" if any(q is _q for _q, _w in _own) else "other"
            r = w / 2 + _CLEAR
            dx = q.x - p.x; dy = q.y - p.y
            if dx * dx + dy * dy > r * r: continue
            out = r + 250000          # 0.25 mm beyond the clearance ring: far enough to be off the anti-pad
            # THE FILL MUST RESUME ON BOTH SIDES, along the line from the barrel through this point. Probing
            # four fixed directions and accepting any one of them calls a point an anti-pad when it lies just
            # OUTSIDE a fill's edge with a via of its own net inside it: beyond such a point the reference
            # does not resume, and the gap is real. Asking the two ends of the same line is the difference
            # between a hole and an edge.
            dx = p.x - q.x; dy = p.y - q.y
            m = (dx * dx + dy * dy) ** 0.5
            if m < 1000:
                # THE SAMPLE IS ON THE BARREL ITSELF and there is no line through it to ask about: the point
                # is inside the hole by construction, so the question is only whether a fill surrounds it.
                # Left as a direction of zero this collapsed both probes onto the via's own centre, which is
                # never filled, and every anti-pad on every board came back as a real break (17 September).
                pairs = (((out, 0), (-out, 0)), ((0, out), (0, -out)))
            else:
                ux, uy = dx / m, dy / m
                pairs = (((ux * out, uy * out), (-ux * out, -uy * out)),)
            for pair in pairs:
                if all(any(pl.Contains(pcbnew.VECTOR2I(int(q.x + ox), int(q.y + oy)))
                           for Ln in Ls for pl in planes.get(Ln, []))
                       for ox, oy in pair):
                    return _whose
        return None
    gaps = {}; anti = {}; anti_other = {}; total = {}; n_nets = 0; n_tracks = 0
    for tr in b.GetTracks():
        if tr.GetClass() != "PCB_TRACK": continue
        n_tracks += 1; net = tr.GetNetname()
        if cls_of(net) not in targets and not signalnets.is_signal(net, signals): continue
        L = tr.GetLayer(); length = tr.GetLength() / 1e6; n = max(1, int(length / SAMPLE)); total[net] = total.get(net, 0.0) + length
        for k in range(n + 1):
            u = k / n; p = pcbnew.VECTOR2I(int(tr.GetStart().x + u * (tr.GetEnd().x - tr.GetStart().x)), int(tr.GetStart().y + u * (tr.GetEnd().y - tr.GetStart().y)))
            if not any(pl.Contains(p) for Ln in neighbours(L) for pl in planes.get(Ln, [])):
                _whose_hole = _hole(net, p, neighbours(L))   # not `_w`: that name is a via WIDTH ten lines up
                if _whose_hole == "own": anti[net] = anti.get(net, 0.0) + length / (n + 1)
                elif _whose_hole == "other": anti_other[net] = anti_other.get(net, 0.0) + length / (n + 1)
                else: gaps[net] = gaps.get(net, 0.0) + length / (n + 1)
    if n_tracks and not total: check(False, "return path: the board has %d tracks and not one signal net was found to judge (signalnets.classify excluded every net: %s)" % (n_tracks, ", ".join(sorted(set(_why.values())))))
    if not n_tracks: check(True, "return path: 0 of 0 signal nets, the board has no tracks")
    # WHAT IS ASKED OF A RETURN PATH DEPENDS ON WHAT THE SIGNAL IS (rule RET-001, 16 September 2026, owner
    # instruction of the same day). "A plane under every signal" is a heuristic and this project had made it a
    # law: it refused board E for SHORE_INHIBIT, WATER_SENSE and TRK_INTVCC, an opto inhibit, a sensor input
    # and an LDO output, over anti-pad gaps of one to four millimetres. The governing principle is return-path
    # adequacy FOR THE SIGNAL'S SPECTRAL CONTENT, so each net is judged by its class: a fast net is asked for
    # an ADJACENT reference within a tolerance, a slow one is asked whether a return path EXISTS AT ALL, and a
    # net whose class nothing establishes is held to the STRICTEST bar and named, so that being unclassified
    # can never be the easy way through.
    sig_cls, cls_bad = signal_class.classify(b, path, targets, cls_of)
    for x in cls_bad: check(False, "signal class declaration: %s" % x)
    n_over = 0; worst = ("", 0.0); undeclared = []
    for net in sorted(total):
        n_nets += 1; g = gaps.get(net, 0.0); ap = anti.get(net, 0.0); apo = anti_other.get(net, 0.0)
        if g > worst[1]: worst = (net.lstrip("/"), g)
        sc, basis = sig_cls.get(net, ("UNKNOWN", ""))
        if sc == "UNKNOWN":
            undeclared.append(net.lstrip("/"))
            lim = max(GAP_MM, 0.05 * total[net])        # the strictest bar, held until the board declares it
            if g > lim: n_over += 1
            check(g <= lim, "return path under %s (%s, UNDECLARED so judged at the strictest bar): %.1f of %.1f mm without a plane on a neighbouring layer (limit %.1f)"
                  % (net.lstrip("/"), cls_of(net), g, total[net], lim))
        elif signal_class.QUESTION[sc] == "EXISTS":
            # No edge to speak of, so adjacency is not the question; a return path that EXISTS is. A net with
            # no reference anywhere under any of its copper has a loop the size of the board, whatever its speed.
            covered = total[net] - g
            check(covered > 0, "return path under %s (%s): a reference exists under %.1f of %.1f mm [%s]"
                  % (net.lstrip("/"), sc, covered, total[net], basis[:80]))
            if covered <= 0: n_over += 1
        else:
            lim = signal_class.limit(sc, total[net])
            if g > lim: n_over += 1
            check(g <= lim, "return path under %s (%s, %s): %.1f of %.1f mm without a plane on a neighbouring layer (limit %.1f%s) [%s]"
                  % (net.lstrip("/"), cls_of(net), sc, g, total[net], lim,
                     ((("; %.1f mm more is this net's own via anti-pads, which RET-003 judges" % ap) if ap > 0.05 else "")
                      + (("; %.1f mm more is another conductor's via anti-pad, a hole the return goes around" % apo) if apo > 0.05 else "")),
                     basis[:70]))
    # An undeclared net is not a failure of the copper and must not be reported as one: it is a gap in what this
    # project has written down about its own design, and it is named here so it can be closed.
    if undeclared:
        print("intent_checks: %d signal net(s) carry no declared signal class and were judged at the strictest bar: %s%s"
              % (len(undeclared), ", ".join(undeclared[:12]), " ..." if len(undeclared) > 12 else ""))
    if anti_other:
        print("intent_checks: %.1f mm of signal run across this board sits over ANOTHER conductor's via anti-pad "
              "(%d net(s)); a hole in the reference is not an absent reference and the return goes around it, so "
              "this screen does not judge it. How perforated a reference may be is RET-001's question and its "
              "criterion is owner decision 39" % (sum(anti_other.values()), len(anti_other)))
    LAST.clear(); LAST.update(nets=n_nets, over=n_over, gap_mm=round(sum(gaps.values()), 3),
                              antipad_mm=round(sum(anti.values()), 3),
                              antipad_other_mm=round(sum(anti_other.values()), 3),
                              worst_net=worst[0], worst_mm=round(worst[1], 3))
    print("intent_checks: return path judged on %d signal nets (%d excluded as ground, rail, zone owner or power class), %d over their limit, worst %s at %.1f mm; %.1f mm across the board is the nets' own via anti-pads and is RET-003's question, not this one" % (n_nets, len(_why), n_over, worst[0] or "none", worst[1], sum(anti.values())))
    # 3b. EVERY POWER-SYMBOL NET IS A DECLARED RAIL (16 September 2026). This project writes a rail as a KiCad
    # power symbol, so a net whose name begins with "+" is a rail by the generators' own convention. Board B
    # declared six and has thirty-six; the other thirty were invisible three ways at once: signalnets could not
    # know they were rails, so the return-path rule above judged each as a SIGNAL and measured its reference
    # coverage, which says nothing about a power net; dc_drop computed no drop and no current density for any of
    # them; and derate could not compare one part's rating against them. A rail that is not declared is not
    # excluded: it is asked the wrong question and missed by the right one, and both silently.
    _declared = {r.lstrip("/") for r in (it.get("rails") or {})}
    _power_nets = set()
    _ni = b.GetNetInfo()
    for _code in range(_ni.GetNetCount()):
        _nm = _ni.GetNetItem(_code).GetNetname()
        if _nm and _nm.lstrip("/").startswith("+"): _power_nets.add(_nm.lstrip("/"))
    _undeclared = sorted(_power_nets - _declared)
    # ONE STRING: the board gates' own check() takes a message and nothing else, and passing a third argument
    # crashed the gate AFTER it had printed its result (board E's re-finish, 16 September 2026). A check that
    # raises where it decides is worse than one that decides wrongly, because it leaves no verdict at all.
    check(not _undeclared, "every power-symbol net is a declared rail (%d of %d)%s"
          % (len(_power_nets) - len(_undeclared), len(_power_nets),
             ("; not in the intent file: " + ", ".join(_undeclared[:12])) if _undeclared else ""))
    # 4. return via (rule 2 of the same ruling): a ground via beside every signal via, judged by return_via.py
    rv = return_via.judge(b, path)
    check(not rv["lacking"], "return via: %d of %d signal vias have a ground via within %.1f mm (%d exempt in fine-pitch fans, %d on one reference plane, %d on a net whose declared class has no edge to return); without one: %s" % (
        rv["judged"] - len(rv["lacking"]), rv["judged"], return_via.RETURN_MM, rv["exempt"], rv["same_plane"],
        rv.get("slow", 0), "; ".join(rv["lacking"][:8]) + (" ..." if len(rv["lacking"]) > 8 else "") or "none"))
    # 2. decoupling
    pads = {(f.GetReference(), p.GetNumber()): p for f in b.GetFootprints() for p in f.Pads()}
    vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    def closes(p):
        c = p.GetPosition(); r = int(NEAR_VIA * 1e6)
        if any(v.GetNetname() == p.GetNetname() and math.hypot(v.GetPosition().x - c.x, v.GetPosition().y - c.y) <= r for v in vias): return True
        if any(pl.Contains(c) for L in cu for pl in planes_net.get((L, p.GetNetname()), [])): return True   # the pad lies in a pour of its own net (review of 8 Sep 2026: the `is` on SWIG proxies was always False)
        # 9 Sep 2026 (D10, appendix 32.83): the question this asks is whether the pad REACHES ITS PLANE, and a rail
        # carried by tracks has no plane to reach. Its loop is the pad-to-pin distance, which the check above already
        # measures. D10 failed four capacitors sitting 1.1 to 2.6 mm from their pins because +3V3_D8 and +5V_D8 are
        # track rails on that board and no via of theirs happened to land within 1.5 mm; the ground pads all lay in
        # the pour. A net with no pour anywhere on the board is not asked a question that does not apply to it.
        return not any(planes_net.get((L, p.GetNetname())) for L in cu)
    # AN ALLOWANCE NAMES ITS CAPACITOR (decision 42, T6; 27 September 2026). The file was read as "any line allows every
    # far capacitor", and the line of 8 September that five boards carried passed 33 capacitors on boards B and P as
    # 33 passes (DECOUPLING.md 3.2(f)). A line is `C36: reason` and allows that one; a line that names none allows
    # nothing and is named here; an allowed capacitor is a JUSTIFIED DEVIATION, counted as one, never as a pass.
    allow_p = os.path.join(os.path.dirname(os.path.abspath(path)) if path else ".", "bypass-allow.txt")
    allowed, allow_refused = _dr.parse_allow(open(allow_p, encoding="utf-8", errors="replace").read()) if os.path.exists(allow_p) else ({}, [])
    for _ln, _line, _why in allow_refused:
        print("intent_checks: bypass-allow.txt line %d %s and allows nothing: %s" % (_ln, _why, _line[:70]))
    # the other side (D5, T9): the board's sides are counted WITHOUT the declared capacitors that sit opposite their
    # part, or the first far-side seat on a one-sided board would make the board two-sided and allow itself
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    _far_caps = {e.get("cap") for e in it.get("bypass", []) if e.get("cap") in fps and e.get("part") in fps
                 and fps[e["cap"]].GetLayer() != fps[e["part"]].GetLayer()}
    _f = _bk = 0
    for _g in b.GetFootprints():
        if _g.GetReference() in _far_caps: continue
        _pp = list(_g.Pads())
        if any(q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for q in _pp): continue
        if not any(q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and q.IsOnCopperLayer() for q in _pp): continue
        if _g.GetLayer() == pcbnew.F_Cu: _f += 1
        else: _bk += 1
    two_sided = _dr.two_sided(_f, _bk)
    allow_mm, allow_src = bypass_search.allowance(b, path)
    _skip = fan_select.escape_skip(path)
    fan_boxes = fan_select.fan_boxes(b, _skip); tht_boxes = fan_select.tht_boxes(b)
    def _pad(q, ref=None):
        return {"ref": ref, "num": q.GetNumber(), "xy": (q.GetPosition().x / 1e6, q.GetPosition().y / 1e6), "net": q.GetNetname(),
                "half": (q.GetBoundingBox().GetWidth() / 2e6, q.GetBoundingBox().GetHeight() / 2e6)}
    _vias = [{"xy": (v.GetPosition().x / 1e6, v.GetPosition().y / 1e6), "net": v.GetNetname(), "r": v.GetWidth(pcbnew.F_Cu) / 2e6} for v in vias]
    n_by = 0; tally = {"pass": 0, "justified": 0, "recorded": 0, "fail": 0, "no_own_via": 0, "far_side": 0, "unclassed": 0,
                       "allow_lines_refused": len(allow_refused)}
    RANK = {"pass": 0, "recorded": 1, "justified": 2, "fail": 3}
    for e in it.get("bypass", []):
        n_by += 1
        cap = [p for (ref, num), p in pads.items() if ref == e["cap"]]; pin = pads.get((e["part"], e["pin"]))
        if not cap or pin is None: check(False, "bypass %s -> %s.%s: pads found on the board" % (e["cap"], e["part"], e["pin"])); tally["fail"] += 1; continue
        rail = [p for p in cap if p.GetNetname() == pin.GetNetname()]; gnd = [p for p in cap if p.GetNetname() != pin.GetNetname()]
        if not rail: check(False, "bypass %s -> %s.%s: the capacitor shares the pin's net %s" % (e["cap"], e["part"], e["pin"], pin.GetNetname())); tally["fail"] += 1; continue
        val = next((f.GetValue() for f in b.GetFootprints() if f.GetReference() == e["cap"]), "")
        # THE LIMIT IS THE CLASS'S (T2). It was read off the value string: "10u 25V 1210" got 6.0 mm and a bare
        # "10u" 3.0 (DECOUPLING.md 3.2(c)). An entry with no ruled class has no limit and is refused, never defaulted.
        if e.get("class") not in _dr.CLASSES:
            tally["fail"] += 1; tally["unclassed"] += 1
            check(False, "bypass %s (%s) to %s.%s: %s" % (e["cap"], val, e["part"], e["pin"],
                                                         (_dr.form_problems(e) or ["no ruled class"])[0].split(": ", 1)[-1]))
            continue
        d = math.hypot(rail[0].GetPosition().x - pin.GetPosition().x, rail[0].GetPosition().y - pin.GetPosition().y) / 1e6
        cf, pf = fps[e["cap"]], fps[e["part"]]
        far = cf.GetLayer() != pf.GetLayer(); loop = d; refused = None
        if far:
            tally["far_side"] += 1
            ok_far, why_far = _dr.far_side(e, two_sided, fan_select.courtyard_box(cf), fan_boxes, tht_boxes)
            if ok_far and allow_mm is None: ok_far, why_far = False, "%s: %s" % (e["cap"], allow_src)
            if not ok_far: refused = why_far
            else: loop = _dr.loop_equivalent_mm(d, True, allow_mm)
        if refused:
            # a seat the ruling refuses is refused whatever the allow file says (T9: "refused, never allowed")
            tally["fail"] += 1
            check(False, "bypass %s (%s) to %s.%s: on the side opposite its part and refused, %s" % (e["cap"], val, e["part"], e["pin"], refused.split(": ", 1)[-1]))
            continue
        st, why = _dr.judge(e, loop, allowed.get(e["cap"]))
        side_txt = (" (the other side: %.2f mm in plane plus the %.1f mm via allowance of %s)" % (d, allow_mm, allow_src)) if far else ""
        line = "bypass %s (%s) to %s.%s, class %s: %s%s" % (e["cap"], val, e["part"], e["pin"], e["class"], why.split(": ", 1)[-1], side_txt)
        if st == "fail": tally["fail"] += 1; check(False, line); continue
        # the loop closes through the planes: the rail pad reaches a via or a pour, as before
        if not closes(rail[0]):
            tally["fail"] += 1; check(False, line + "; its rail pad reaches no via or pour within %.1f mm" % NEAR_VIA); continue
        if gnd and e["class"] in ("D", "L"):
            # THE GROUND PAD'S OWN VIA (D2, T10). The reach test accepts any via of the net within 1.5 mm, another
            # part's among them; SCAA082A 2.4 asks the pad "directly with a via to the ground plane". The via is
            # named, whose it is said, and its distance printed; no millimetre is judged, because no maker gives one.
            g = gnd[0]
            others = [_pad(q, ref) for (ref, num), q in pads.items() if q is not g and q.GetNetname() == g.GetNetname()
                      and abs(q.GetPosition().x - g.GetPosition().x) < 4e6 and abs(q.GetPosition().y - g.GetPosition().y) < 4e6]
            ov = _dr.own_via(_pad(g, e["cap"]), _vias, others, NEAR_VIA)
            if ov["via"] is None:
                if not closes(g):
                    tally["fail"] += 1; check(False, line + "; its ground pad reaches no via or pour within %.1f mm" % NEAR_VIA); continue
                st = max(st, "justified", key=lambda k: RANK[k]); tally["no_own_via"] += 1
                line += "; DEVIATION: its ground pad has no via within %.1f mm and returns through a pour" % NEAR_VIA
            elif not ov["own"]:
                st = max(st, "justified", key=lambda k: RANK[k]); tally["no_own_via"] += 1
                line += "; DEVIATION: its ground via, %.2f mm from the pad, is also the landing of %s" % (ov["length_mm"], ", ".join(ov["shared_with"][:3]))
            else:
                line += "; its own ground via %.2f mm from the pad" % ov["length_mm"]
        elif gnd and not closes(gnd[0]):
            tally["fail"] += 1; check(False, line + "; its other pad reaches no via or pour within %.1f mm" % NEAR_VIA); continue
        tally[st] += 1
        check(True, line + ("" if st == "pass" else "; counted as %s, not as a pass" % st.upper()))
    LAST_DECOUPLING.clear(); LAST_DECOUPLING.update(tally, declared=n_by, two_sided=two_sided, allowance_mm=allow_mm, allowance_source=allow_src)
    n_far = tally["justified"]
    # 3. rails exist
    names = {b.GetNetInfo().GetNetItem(k).GetNetname().lstrip("/") for k in range(1, b.GetNetInfo().GetNetCount())}
    for net in it.get("rails", {}): check(net.lstrip("/") in names, "intent rail %s is a net of the board" % net)
    if n_by:
        print("intent_checks: decoupling, %d declared: %d pass, %d justified deviation(s), %d recorded with no distance to judge, %d fail "
              "(%d with no ruled class); %d with no ground via of their own; %d on the side opposite their part (SMD parts %d front, %d "
              "back without them, so the other side is %s)"
              % (n_by, tally["pass"], tally["justified"], tally["recorded"], tally["fail"], tally["unclassed"], tally["no_own_via"],
                 tally["far_side"], _f, _bk, "a seat" if two_sided else "no seat"))
    return "intent_checks: return path on %d nets, return via on %d signal vias, %d bypass entries, %d rails checked" % (n_nets, rv["judged"], n_by, len(it.get("rails", {})))


# ------------------------------------------------------------------------------------------------------------------
# RULE PWR-001 ON THE NETLIST (26 September 2026, MESHSAT-1357; review of 26 September 2026, section 6).
#
# PWR-001 is verified at the SCHEMATIC phase and its registry evidence scope is the schematic. The check above reads
# the BOARD, so its reading could be current only on a layout that carries the netlist, and on every board of the set
# the committed layout does not (SCH-002 is not a current PASS): the rule could never bind before layout entry, which
# is the one thing it has to do. It is judged here on the committed netlist of the declared phase and the intent file
# beside it, both recorded by sha (the netlist by its content identity too, so a regenerated copy with a new export
# date binds by content), in these words of the rule's acceptance:
#
#   "The count of rails in the board's intent declaration equals the count of distinct power nets carrying more than a
#    declared threshold current on the board, and every declared rail names where its current goes."
#
# WHAT A POWER NET IS, read from the netlist, the intent and the held datasheets and nothing else (session decisions of
# 26 September 2026 under the owner's standing rule of that day; the alternatives are in the verdict note and the
# report). A net is a POWER NET when any of these holds:
#   (1) POWER SYMBOL: its name begins with "+". The generators write a leading "+" only through a KiCad power symbol,
#       which is the convention the board check read and the registry's own false-positive analysis names.
#   (2) SUPPLY PIN BY TYPE: it carries a pin its symbol types power_in or power_out. This finds a module-supplied rail
#       with no power symbol, which the rule's false-positive analysis says "is still a rail and is declared with the
#       receptacle as its source".
#   (3) POWER CLASS: the netlist assigns it one of the power classes the generators write (CLASS_POWER: PWR, RAIL,
#       BANK, SW, NODE; the first of a comma list, as netclass reads one). That is the schematic's own statement that
#       the net carries power. Of signalnets.POWER_CLASSES, GNDC is ground copper, and HV is a CLEARANCE class for
#       board B's 54 V domain that holds the PoE port's current path and its gate and reset lines alike, so a net of it
#       is undecided (below) rather than counted.
#   (4) SUPPLY PIN BY NAME, CORROBORATED: it carries a pin whose function names a supply (SUPPLY_TOKEN: the VDD, VCC,
#       VSS and VEE families with their prefixes and suffixes, VIN, VBAT, VBUS, VSYS, VCAP, VREG, BAT, or a voltage such
#       as 3V3), and the netlist or the intent corroborates it: the intent's bypass list decouples a pin on it, a
#       capacitor joins it to ground, or supply-named pins of two or more parts share it. The generators type nearly
#       every supply pin passive (the independent check of 26 September counted A 32 of 34, C 17 of 19, D 16 of 17, P 3
#       of 3), so (2) alone could not see the supplies a part makes for itself or a module is fed from. A VSS or VEE
#       pin on a net that is not ground is a negative supply (board D's TPA6132A2 HPVSS, the charge pump's output).
#   (4b) SUPPLY PIN BY ITS HELD DATASHEET: it carries a pin that PIN_ROLES reads as a supply from the part's own datasheet
#       (a regulator's output or bypass pin, a bootstrap supply, a charge pump's node), whatever the netlist calls it.
#   (5) CURRENT FOLLOWED FROM A DECLARED RAIL: a part the rail names as its source or a load, at more than the threshold
#       by that declaration, passes the current on. A two-terminal part (SERIES_PREFIXES: fuse, resistor, inductor,
#       ferrite, diode, switch, jumper) passes it to its other net. A transistor passes it to its other CHANNEL nets
#       when the rail sits on its channel; a rail on its gate or base only drives it. Its pin roles come from its pin
#       names (G, S, D, B, C, E) or, where the symbol names its pins after their nets, from its held datasheet. A
#       channel net reached this way that the intent does not declare passes the current on again through every
#       transistor whose channel sits on it, because a switched supply stays a supply through its next switch (board
#       C's LED rail: the light switch SW_LIGHT, then the high-side FET Q1). A transistor whose pin roles nothing reads
#       passes the current to one of its other nets without saying which: that is answered when a declared rail among
#       them names the transistor as its source or a load, and refused otherwise (a declared net that names nothing, a
#       gate line declared as a node, does not say which net is the channel).
#   and every declared rail that is a net of the netlist, which carries its own declared current.
#
# UNDECIDED: a net that one of these points at but none of them settles is named and not counted. That is a supply-named
# pin with no corroboration (a USB hub's VBUS detect on its divider, a codec's VIN that is a microphone input), a net of
# the HV clearance class, or a net the intent's bypass list decouples whose pin neither names nor types a supply (a
# current-sense filter, a bootstrap, a backup-supply pin), unless the held datasheets settle it as pass (6) settles a
# net. The reading cannot PASS while one stands: it reads INCONCLUSIVE naming them when nothing fails, and declaring
# the net as a rail or a node settles it.
#
# (6) FAIL CLOSED (third pass, 26 September 2026). Kinds (1) to (5) ADMIT a net only on evidence they can read, and a
# name is not such evidence on these netlists: of the pins that decide, a symbol names some after the maker's datasheet
# (board D's TPA6132A2: HPVSS), names others after the net they sit on (board A's TPS25740: pin 1 reads "PD_VTX"), and
# names the rest by number (board E's LT8705A: "Pin_4" for its 3.3 V regulator output). The first two passes counted a
# net only when some name fell inside a grammar, so a supply whose name fell outside it (HPVSS, VAUX, VTX), echoed the
# net, or was a number went unread and was silently a signal: AMP_HPVSS, TRK_LDO33, PD_VTX and PD_VAUX were in no count
# and no undecided list. That is the general cause, and it is closed by turning the default round: every net that
# carries the physical MARK of a supply is a candidate, and it leaves the candidates only as a counted power net, a
# declared net, or through a reason read from the netlist or a held datasheet that it supplies nothing; otherwise it is
# UNDECIDED. The marks are what a supply cannot be built without on these boards:
#   M1  a capacitor from it to ground: every supply pin of every part is decoupled (each datasheet says so, and rule
#       DEC-001 holds the bypass list to it), and every regulator's output, bootstrap and reference pin is bypassed;
#   M2  a capacitor from it to a power net (a bootstrap across a switch node), or across two pins of the one part that
#       is the only part on either net (a charge pump's flying capacitor, a sense filter across a part's inputs);
#   M3  a two-terminal fuse, inductor, ferrite, diode, switch or jumper joining it to a power net (a supply's own path,
#       a freewheel diode across a switched load), or a resistor of at most MARK_R_SUPPLY_OHM (a link, a filter, a
#       sense element) joining it to one when no integrated circuit is on it; a clamp the intent declares is excluded,
#       it conducts only in a surge. An UNDECIDED net passes M3 on as a power net does, to a fixed point, so a chain of
#       links from a supply nothing reads is marked link by link (board B's antenna feed: VDD_RF, R23, L3);
#   M4  the channel of a transistor whose other channel pin is on a power net that is not ground (a switched supply);
#       where nothing reads the transistor's pin roles, any of its pins shares it with such a net, when the net also
#       reaches a part that is not an integrated circuit, a resistor, a capacitor or a test point (a load that does not
#       carry its own decoupling on the net: a connector, a lamp, a fan, a relay). And the LOW SIDE of a load (fourth
#       pass): the channel of a transistor whose roles are read and whose other channel pins sink to ground, when the
#       net also carries a load that is not an integrated circuit, a resistor, a capacitor, a test point, a transistor
#       or a connector (board P's SCP_HTR, the return of the chemical fuse's heater; board C's TX lamp). A connector is
#       left out so that an open-drain control line into a module's socket is not marked;
#   M5  (fourth pass, 27 September 2026) a LEAD: a connector whose every other pin is on ground or unconnected carries
#       the net and its return and nothing else, and a part that is not a connector, a resistor, a capacitor or a test
#       point is on the net. The third check of 26 September found board A's VMON, the eFuse U21's output, running
#       straight to the monitor's two-pin lead J_MON: its decoupling is on the monitor's side, and a part of three or
#       more pins passes a supply to it with no two-terminal link, so marks M1 to M4 could not reach it. That is the
#       general cause the third check named, and M5 is the mark it lacks; a held row (kind 4b) reads the same output
#       wherever the connector carries other lines too;
#   M6  a netlist class that says the conductor SENSES a supply (MARK_SENSE_CLASSES: SENSE), the schematic's own
#       statement (board P's cell taps CELL1 to CELL3, which gen_sch_p.py also flags as driven).
# A marked net is SETTLED (supplies nothing) when a crystal or resonator is on it (an oscillator net: a part of prefix Y
# whose pins sit on two live nets at most, so an oscillator with a supply pin is read like any part), or when every pin
# on it that is not a resistor's, a capacitor's or a test point's is one of: a pin whose held datasheet role is not a
# supply or a ground; a transistor's gate or base; a transistor's channel pin whose other channel pins are on ground (an
# open-drain sink); a pin of a clamp the intent declares; a pin of a switch or jumper whose other pins are on ground or
# unconnected. A connector, a lamp, a relay, a pad, a part with no held row: none of them is read, so such a net stays
# UNDECIDED. On a net whose only marks are M5 or M6 a connector carries what the board's own pins on it carry, so it
# is passed over when at least one of those pins is read; a lead with nothing read on it stays undecided. The same
# settling is offered to the undecided nets above, so a held datasheet row settles a current-sense filter as well.
#
# THE CENSUS every reading records: each net of the netlist that is not ground or an unconnected pin is exactly one of
# counted, declared node, undecided, settled (with its reason) and unmarked. An UNMARKED net carries no mark and no
# name, type, class, held role or rail current of kinds (1) to (5): under the premises above it reaches no supply pin
# (M1), is no switching or bootstrap node (M2, M3), is no switched supply or switched return (M3, M4), is no lead (M5)
# and senses no supply by its class (M6). What the premises leave out is stated in the coverage note: a supply to a
# part that the design forgot to decouple, a supply that runs from one connector pin to another with nothing between
# them, a supply through a resistor above MARK_R_SUPPLY_OHM to a part with no decoupling of its own on the net (a
# lamp's current-limited feed is such a path, and it is the rail's own load list that states it), and a supply a part
# with NO held row delivers straight to a connector that also carries a line that is not ground (the suite holds every
# power part of the six boards to a held row, tests/test_rails_census.py, so on them that is the design's own gap).
#
# A power net the intent declares as a NODE (a switch node behind a buck's inductor, a part's own internal regulator
# output, a charge pump) is reported and not refused: the declaration states it with its voltage, and its current is
# chopped or runs from one part's pin to its own capacitor, which the drop and density rules this rule feeds do not
# judge. A node that carries the supply pins of two or more parts is refused, because a supply that reaches two parts
# is distributed, and a distributed supply is a rail.
#
# Ground nets are not power nets here unless the intent declares one as a rail (board B declares its GND as the return
# of every rail); a ground's own rule is GND-001.
#
# THE THRESHOLD is 0 A (a session decision, same authority): every conductor the declarations say carries current is a
# power net, and no net is excused for carrying little. A nonzero threshold would excuse a small supply from being
# declared, no board asks for that, and no measurement in this tree says what a safe floor would be. A power net of
# kinds (1) to (4b) has no declared current until it is declared, so it cannot be shown to sit under any threshold and
# must be a rail or a node.
#
# "NAMES WHERE ITS CURRENT GOES" is read as: the rail declares at least one load, and every load and every source it
# names has a pin on that net in the netlist, so the declaration points at parts that are really on it.
#
# WHAT IT DOES NOT JUDGE: whether a declared current is right (PI-001, PI-002 and PI-003 measure copper against it), the
# order rails come up in (PWR-002), and a current path through a part of three or more pins that is not a transistor
# (the dual-winding choke of board E, a regulator from input to output): the rails on both sides of such a part are
# asked of by (1) to (6) and by their own declarations.
# ------------------------------------------------------------------------------------------------------------------
THRESHOLD_A = 0.0
SERIES_PREFIXES = ("F", "R", "L", "FB", "D", "SW", "JP")
SWITCH_PREFIXES = ("Q",)
SUPPLY_PINTYPES = ("power_in", "power_out")
CONTROL_FUNCTIONS = ("G", "B", "GATE", "BASE")
# signalnets.POWER_CLASSES split for this rule (a test holds that the three together are that set, so a class added
# there is placed here by someone who read this): counted, undecided, ground
CLASS_POWER = frozenset({"PWR", "RAIL", "BANK", "SW", "NODE"})
CLASS_UNDECIDED = frozenset({"HV"})
CLASS_GROUND = frozenset({"GNDC"})
# one token of a pin function (split on anything that is not a letter or a digit) that names a supply
SUPPLY_TOKEN = re.compile(r"^(?:[A-Z]{0,4}V(?:DD|CC|SS|EE)[A-Z0-9]*|V(?:IN|BAT|BUS|SYS|CAP|REG)|BAT|\d+V\d*)$")
GROUND = re.compile(r"(^|_)GND[0-9]*$|^GND", re.I)      # the ground test ground_system.py applies (GND-001)
# the ground FAMILY a decoupling capacitor may return to (AGND, PGND, DGND, SGND as well as GND): mark M1 and the
# capacitor corroboration of kind (4) read it, so a supply decoupled to an analogue or power ground is still marked. A
# net of the family that GND-001's test does not name ground is not skipped: it is read like any other net, and a
# return that is not named ground fails closed rather than passing as nothing (no such net is on the six boards today)
GROUND_FAMILY = re.compile(r"(^|_)[A-Z]?GND[0-9]*$|^[A-Z]?GND", re.I)
# pass (6): the parts that carry nothing a supply needs (resistors, thermistors, capacitors, test points), the ones that
# make a net an oscillator's, the two-terminal parts whose link to a power net is mark M3, and the parts a supply's
# decoupling is carried by (an integrated circuit decouples its own supply pins on the net, M1)
MARK_PASSIVE = ("R", "RT", "C", "TP")
MARK_CRYSTAL = ("Y",)
MARK_SERIES = ("F", "L", "FB", "D", "JP")                        # and every two-pin part whose reference begins SW
# a resistor passes a supply when it is a link, a filter or a sense element: at most this many ohms by its value field
# (board B's SIM2_VCC through the 0R eSIM link R272, its GNSS antenna feed through the 10R R23), and when its value is
# not read. A pull-up, a divider or a lamp's current limit is more, and passes no supply (an instrument limit: a supply
# through a larger resistor to a part with no decoupling of its own on the net is not marked)
MARK_R_SUPPLY_OHM = 10.0
MARK_IC = ("U",)
# M6: a netlist class that says the conductor SENSES a supply (a cell tap, a Kelvin lead); the generators write it
MARK_SENSE_CLASSES = frozenset({"SENSE"})

# THE HELD PIN ROLES (third pass, 26 September 2026; completed in the fourth, 27 September). A pin's role as its maker's
# datasheet states it: rows are read from the file each one names under v2/vendor, and each pin carries the words that
# give its number and the words that give its role, which tests/test_rails_census.py finds in the document's own text
# (pdftotext). A part is recognised by its part number at the start of the netlist's value field (never on a
# connector, whose value field names what it carries), and the pin number is the package's own (the row says which
# package's column or drawing it read). A ROW IS COMPLETE: it carries every pin its table types power or ground (P,
# PWR, Power, PI, PO, G, GND, Ground) or describes as a supply, which the same test holds line by line against the
# table; the third check found the TPS2596 row carrying its dVdt pin and not its Power Output, which is how board A's
# VMON went unread. Every power part on the six boards has a row (the power parts no earlier pass held, whose
# documents are filed: the AP2112K, TLV755P and TLV758P regulators, the TPS2065C switch, the TPS23861 PSE controller
# and the LM74700-Q1 ideal-diode controller). Roles:
#   SUPPLY        the datasheet makes the pin a supply: a supply input or output, a regulator's output or bypass pin, a
#                 bootstrap supply, a charge pump's output or flying node, a switch node. The net is a power net, kind
#                 (4b).
#   GROUND        the datasheet makes the pin the part's ground. On a ground net nothing is asked; on a net that is not
#                 a ground the part's return current runs on it, and it is a power net, kind (4b).
#   G S D         a field-effect transistor's gate, source and drain (the package's pin-out drawing), so a power FET
#                 whose symbol names its pins after their nets is read like one whose symbol says G, S and D.
#   anything else a role that supplies nothing (SIGNAL, SENSE, TIMING, COMPENSATION, REFERENCE, RESET, CENTRE_TAP):
#                 it settles the pin in pass (6), and only there; it never uncounts a net (1) to (5) count. A pin the
#                 table types power that the maker describes as a sense input (the BQ25731's ACN, ACP, SRN, SRP and
#                 VSYS) carries the words that say so.
# A part or a pin with no row reads nothing, so a net that needs it stays UNDECIDED. Adding a row is the way a board's
# undecided net is settled without declaring it, and it needs the held document.
ROLE_SUPPLY = "SUPPLY"
ROLE_GROUND = "GROUND"
PART_MAKERS = r"(?:TI|Microchip|Pulse|Nexperia|Diodes|Infineon|ST|Analog Devices|Quectel)"
TRANSISTOR_ROLES = {"G": True, "B": True, "S": False, "D": False, "E": False, "C": False}   # role -> is the control
# the reference prefixes of a connector, a wire land or a pad (rules_lib.ref_prefix: J, J_MON, P_CN, PAD_W, W_BP): its
# value field describes what it carries, and a part number named there is the part at the other end, not this one
# (board B's J_GNSS2 bench header reads "LG290P UART2"); and a pin of one is read by nothing, so it settles nothing
CONNECTOR_PREFIXES = ("J_", "P_", "PAD", "W_")


def is_connector(prefix):
    """Is a reference prefix (rules_lib.ref_prefix) a connector's, a wire land's or a pad's?"""
    return prefix == "J" or prefix.startswith(CONNECTOR_PREFIXES)
_SON5X6 = {"1": ("S", "S", "S 1 8 D"), "2": ("S", "S", "S 2 7 D"), "3": ("S", "S", "S 3 6 D"),
           "4": ("G", "G", "G 4 5 D"), "5": ("D", "D", "G 4 5 D"), "6": ("D", "D", "S 3 6 D"),
           "7": ("D", "D", "S 2 7 D"), "8": ("D", "D", "S 1 8 D")}
# Microchip's KSZ9897R: the pin numbers are the assignment grid's (Table 3-1, "number name"), the roles its
# Power/Ground Pins table's (Table 3-2)
_KSZ_POWER = (("VDDIO", (61, 77, 99), ROLE_SUPPLY, "+3.3/2.5/1.8V VDDIO P +3.3V / +2.5V / +1.8V I/O Power"),
              ("AVDDH", (10, 22, 33, 44, 111, 122, 128), ROLE_SUPPLY, "+2.5V AVDDH P +2.5V Analog Power"),
              ("AVDDL", (3, 14, 19, 30, 36, 41, 114, 119, 124), ROLE_SUPPLY, "+1.2V AVDDL P +1.2V Analog Power"),
              ("DVDDL", (11, 23, 45, 56, 74, 87, 104, 110), ROLE_SUPPLY, "+1.2V DVDDL P +1.2V Digital Power"),
              ("GND", (46, 47, 84, 107, 109, 123), ROLE_GROUND, "Ground GND GND Ground (pins and pad)"))
# Quectel's LG290P ground pins, one cell of Table 6 for all of them
_LG290P_GND = "10, 12, connection to all module GND GND 13, - Ground - GND pins, preferably with 24\u201379"
PIN_ROLES = (
    # pins: {pin: (datasheet name, role, words giving the pin's number, words giving its role or None)}
    {"part": r"TPA6132A2\b", "document": "v2/vendor/ti/ti-tpa6132a2.pdf", "package": "RTE QFN-16",
     "pins": {"1": ("INL-", "SIGNAL", "INL- 1 I Inverting left input", None),
              "4": ("INR-", "SIGNAL", "INR- 4 I Inverting right input", None),
              "8": ("HPVSS", ROLE_SUPPLY, "HPVSS 8 P",
                    "Charge pump output and negative power supply for output amplifiers"),
              "9": ("CPN", ROLE_SUPPLY, "CPN 9 P", "Charge pump negative flying cap"),
              "10": ("PGND", ROLE_GROUND, "PGND 10 P Ground", None),
              "11": ("CPP", ROLE_SUPPLY, "CPP 11 P", "Charge pump positive flying cap"),
              "12": ("HPVDD", ROLE_SUPPLY, "HPVDD 12 P", "Positive power supply for headphone amplifiers."),
              "14": ("VDD", ROLE_SUPPLY, "VDD 14 P Positive power supply for TPA6132A2", None),
              "15": ("SGND", "REFERENCE", "SGND 15 P Amplifier reference voltage.", None)}},
    {"part": r"LT8705A\b", "document": "v2/vendor/power/lt8705a.pdf", "package": "UHF QFN-38 (the first number)",
     "numbering": "Pin Functions (QFN/TSSOP)",
     "pins": {"2": ("CSN", "SENSE", "CSN (Pin 2/Pin 5): The (\u2013) Input to the Inductor Current", None),
              "3": ("CSP", "SENSE", "CSP (Pin 3/Pin 6): The (+) Input to the Inductor Current", None),
              "4": ("LDO33", ROLE_SUPPLY, "LDO33 (Pin 4/Pin 7): 3.3V Regulator Output.", None),
              "8": ("VC", "COMPENSATION", "VC (Pin 8/Pin 11): Error Amplifier Output Pin.", None),
              "9": ("SS", "TIMING", "SS (Pin 9/Pin 12): Soft-Start Pin.", None),
              "13": ("GND", ROLE_GROUND, "GND (Pin 13, Exposed Pad Pin 39/Pin 16, Exposed Pad", None),
              "15": ("GATEVCC", ROLE_SUPPLY, "GATEVCC (Pin 15/Pin 18): Power Supply for Gate Drivers.", None),
              "17": ("BOOST2", ROLE_SUPPLY, "BOOST1, BOOST2 (Pins 23, 17/Pins 28, 20): Boosted", None),
              "19": ("SW2", ROLE_SUPPLY, "SW1, SW2 (Pins 21, 19/Pins 24, 22): Switch Nodes.", None),
              "21": ("SW1", ROLE_SUPPLY, "SW1, SW2 (Pins 21, 19/Pins 24, 22): Switch Nodes.", None),
              "23": ("BOOST1", ROLE_SUPPLY, "BOOST1, BOOST2 (Pins 23, 17/Pins 28, 20): Boosted", None),
              "29": ("EXTVCC", ROLE_SUPPLY, "EXTVCC (Pin 29/Pin 30): External VCC Input.", None),
              "34": ("VIN", ROLE_SUPPLY, "VIN (Pin 34/Pin 38): Main Input Supply Pin.", None),
              "35": ("INTVCC", ROLE_SUPPLY, "INTVCC (Pin 35/Pin 1): Internal 6.35V Regulator Output.", None),
              "39": ("GND", ROLE_GROUND, "GND (Pin 13, Exposed Pad Pin 39/Pin 16, Exposed Pad", None)}},
    {"part": r"TPS25740A?RGER?\b", "document": "v2/vendor/ti/ti-tps25740.pdf", "package": "RGE VQFN-24",
     "pins": {"1": ("VTX", ROLE_SUPPLY, "VTX 1 O Bypass pin for transmit driver supply.", None),
              "4": ("GND", ROLE_GROUND, "GND 4 \u2014 Power ground is associated with power management", None),
              "13": ("DVDD", ROLE_SUPPLY, "DVDD 13 O", "Internally regulated 1.85 V rail for external use up to 35 mA."),
              "14": ("PCTRL", "SIGNAL", "PCTRL 14 I Input pin used to control the power that will be advertised.",
                     None),
              "16": ("VAUX", ROLE_SUPPLY, "VAUX 16 O",
                     "Internally regulated rail for use by the power management circuits."),
              "17": ("VDD", ROLE_SUPPLY, "VDD 17 I Optional input supply.", None),
              "18": ("AGND", ROLE_GROUND, "AGND 18 \u2014 Analog ground associated with monitoring", None),
              "20": ("VPWR", ROLE_SUPPLY, "VPWR 20 I", "Connect to an external voltage as a source of bias power.")}},
    {"part": r"LM5176PWP", "document": "v2/vendor/ti/lm5176-datasheet.pdf", "package": "PWP HTSSOP-28 (the first "
     "number)",
     "pins": {"2": ("VIN", ROLE_SUPPLY, "VIN 2 27 I/P The input supply pin to the IC.", None),
              "7": ("SLOPE", "COMPENSATION", "SLOPE 7 4 I",
                    "A capacitor connected between the SLOPE pin and AGND provides the slope"),
              "8": ("SS", "TIMING", "SS 8 5 I", "Soft-start programming pin."),
              "9": ("COMP", "COMPENSATION", "COMP 9 6 O", "Output of the error amplifier."),
              "10": ("AGND", ROLE_GROUND, "AGND 10 7 G Analog ground of the IC", None),
              "13": ("ISNS(\u2013)", "SENSE", "ISNS(\u2013) 13 10", "Input or output current sense amplifier inputs."),
              "14": ("ISNS(+)", "SENSE", "ISNS(+) 14 11", "Input or output current sense amplifier inputs."),
              "18": ("SW2", ROLE_SUPPLY, "SW2 18 15", "The boost and the buck side switching nodes, respectively."),
              "20": ("BOOT2", ROLE_SUPPLY, "BOOT2 20 17 An external capacitor is required between the BOOT1, BOOT2 "
                     "pins and the SW1, SW2 P BOOT1 26 23", "to provide bias to the high-side MOSFET gate drivers."),
              "22": ("PGND", ROLE_GROUND, "PGND 22 19 G Power ground of the IC.", None),
              "23": ("VCC", ROLE_SUPPLY, "VCC 23 20 I/O/P Output of the VCC bias regulator.", None),
              "24": ("BIAS", ROLE_SUPPLY, "BIAS 24 21 I/P", "Optional input to the VCC bias regulator."),
              "26": ("BOOT1", ROLE_SUPPLY, "BOOT2 20 17 An external capacitor is required between the BOOT1, BOOT2 "
                     "pins and the SW1, SW2 P BOOT1 26 23", "to provide bias to the high-side MOSFET gate drivers."),
              "28": ("SW1", ROLE_SUPPLY, "SW1 28 25", "The boost and the buck side switching nodes, respectively.")}},
    {"part": r"TPS62933DRL", "document": "v2/vendor/ti/ti-tps62933.pdf", "package": "DRL SOT-583",
     "pins": {"3": ("VIN", ROLE_SUPPLY, "VIN 3 P", "Supply input pin to internal LDO and high-side FET."),
              "4": ("GND", ROLE_GROUND, "GND 4 G", "Ground pin. Connected to the source of the low-side FET"),
              "5": ("SW", ROLE_SUPPLY, "SW 5 P", "Switching output of the convertor."),
              "6": ("BST", ROLE_SUPPLY, "BST 6 P", "Bootstrap capacitor connection for high-side FET driver."),
              "7": ("SS/PG", "TIMING", "SS/PG 7", "TPS62932, TPS62933, and TPS62933F soft-start control pin.")}},
    {"part": r"AP64500SP", "document": "v2/vendor/diodes/diodes-ap64500.pdf", "package": "SO-8EP",
     "pins": {"1": ("BST", ROLE_SUPPLY, "BST 1",
                    "BST supplies the drive for the high-side n-channel power MOSFET."),
              "2": ("VIN", ROLE_SUPPLY, "VIN 2 3.8V to 40V power source.",
                    "Power Input. VIN supplies the power to the IC as well as the step-down converter power MOSFETs."),
              "7": ("GND", ROLE_GROUND, "GND 7 Power Ground.", None),
              "8": ("SW", ROLE_SUPPLY, "SW 8", "Power Switching Output. SW is the switching node that supplies power "
                                             "to the output."),
              "9": ("EXPOSED PAD", ROLE_GROUND, "must be 9 PAD connected to the ground plane of the PCB",
                    "The exposed thermal pad must be electrically connected to GND")}},
    {"part": r"AP6320[0-5]WU", "document": "v2/vendor/diodes/diodes-ap63200-series-buck.pdf", "package": "TSOT-26",
     "pins": {"3": ("VIN", ROLE_SUPPLY, "3 VIN to 32V power source.",
                    "Power Input. VIN supplies the power to the IC, as well as the step-down converter switches."),
              "4": ("GND", ROLE_GROUND, "4 GND Power Ground.", None),
              "5": ("SW", ROLE_SUPPLY, "5 SW", "Power Switching Output. SW is the switching node that supplies power "
                                              "to the output."),
              "6": ("BST", ROLE_SUPPLY, "6 BST",
                    "BST supplies the drive for the high-side N-Channel MOSFET.")}},
    {"part": r"TPS25963\dDDA", "document": "v2/vendor/power/tps2596.pdf", "package": "DDA SOIC-8",
     "pins": {"1": ("GND", ROLE_GROUND, "GND 1 Ground Ground", None),
              "2": ("dVdt", "TIMING", "dVdt 2",
                    "A capacitor from this pin to GND sets the output turn on slew rate."),
              "4": ("IN", ROLE_SUPPLY, "IN 4 Power Power Input", None),
              "5": ("OUT", ROLE_SUPPLY, "OUT 5 Power Power Output", None)}},
    {"part": r"LTC2954[CI]TS8", "document": "v2/vendor/power/ltc2954.pdf", "package": "TS8 TSOT-23 (the first "
     "number)", "numbering": "PIN FUNCTIONS (TSOT-23/DFN)",
     "pins": {"1": ("VIN", ROLE_SUPPLY, "VIN (Pin 1/Pin 4): Power Supply Input: 2.7V to 26.4V.", None),
              "2": ("PB", "SIGNAL", "PB (Pin 2/Pin 3): Pushbutton Input.", None),
              "4": ("GND", ROLE_GROUND, "GND (Pin 4/Pin 1): Device Ground.", None),
              "7": ("PDT", "TIMING", "PDT (Pin 7/Pin 6): Power-Down Time Input.", None)}},
    {"part": r"TPS22810DRV", "document": "v2/vendor/ti/ti-tps22810-load-switch.pdf", "package": "DRV WSON-6 (the "
     "second number)",
     "pins": {"1": ("VOUT", ROLE_SUPPLY, "VOUT 6 1 O Switch output", None),
              "3": ("CT", "TIMING", "CT 4 3 O Switch slew rate control.", None),
              "4": ("GND", ROLE_GROUND, "GND 2 4 \u2014 Device ground", None),
              "6": ("VIN", ROLE_SUPPLY, "VIN 1 6 I Switch input. Place ceramic bypass capacitor(s) between this pin "
                     "and GND", None)}},
    {"part": r"LM5069MM", "document": "v2/vendor/ti/ti-lm5069.pdf", "package": "MM VSSOP-10",
     "pins": {"2": ("VIN", ROLE_SUPPLY, "2 VIN I", "Positive supply input: A small ceramic bypass capacitor"),
              "3": ("UVLO", "SIGNAL", "3 UVLO I turnon threshold.", "Undervoltage lockout: An external resistor "
                    "divider from the system input voltage sets the undervoltage"),
              "4": ("OVLO", "SIGNAL", "4 OVLO I turnoff threshold.", "Overvoltage lockout: An external resistor "
                    "divider from the system input voltage sets the overvoltage"),
              "5": ("GND", ROLE_GROUND, "5 GND \u2014 Circuit ground", None),
              "6": ("TIMER", "TIMING", "6 TIMER I/O",
                    "Timing capacitor: An external capacitor connected to this pin sets the insertion time delay"),
              "7": ("PWR", "TIMING", "7 PWR I", "Power limit set: An external resistor connected to this pin")}},
    # ACN, ACP, SRN, SRP and VSYS are typed PWR in the table because they sit on the power path; each is described as
    # a sense amplifier input or a sensing pin, and that is the role read here
    {"part": r"BQ25731RSN", "document": "v2/vendor/ti/bq25731-datasheet.pdf", "package": "RSN WQFN-32",
     "pins": {"1": ("VBUS", ROLE_SUPPLY, "VBUS 1 PWR", "Charger input voltage."),
              "2": ("ACN", "SENSE", "ACN 2 PWR", "Input current sense amplifier negative input."),
              "3": ("ACP", "SENSE", "ACP 3 PWR", "Input current sense amplifier positive input."),
              "7": ("VDDA", ROLE_SUPPLY, "VDDA 7 PWR ceramic capacitor from VDDA to power ground.",
                    "Internal reference bias pin."),
              "17": ("COMP2", "COMPENSATION", "COMP2 17 I", "Buck boost converter compensation pin 2."),
              "19": ("SRN", "SENSE", "SRN 19 PWR", "Charge current sense amplifier negative input."),
              "20": ("SRP", "SENSE", "SRP 20 PWR", "Charge current sense amplifier positive input."),
              "22": ("VSYS", "SENSE", "VSYS 22 PWR Charger system voltage sensing.", None),
              "23": ("SW2", ROLE_SUPPLY, "SW2 23 PWR", "Boost mode switching node."),
              "25": ("BTST2", ROLE_SUPPLY, "BTST2 25 PWR between SW2 and BTST2. The bootstrap diode between REGN and "
                     "BTST2 is integrated.", "Boost mode high-side power MOSFET driver power supply."),
              "27": ("PGND", ROLE_GROUND, "PGND 27 GND Device power ground.", None),
              "28": ("REGN", ROLE_SUPPLY, "REGN 28 PWR", "6-V linear regulator output supplied from VBUS or VSYS."),
              "30": ("BTST1", ROLE_SUPPLY, "BTST1 30 PWR between SW1 and BTST1. The bootstrap diode between REGN and "
                     "BTST1 is integrated.", "Buck mode high-side power MOSFET driver power supply."),
              "32": ("SW1", ROLE_SUPPLY, "SW1 32 PWR", "Buck mode switching node.")}},
    {"part": r"TUSB8041", "document": "v2/vendor/ti/ti-tusb8041.pdf", "package": "RGC VQFN-64",
     "pins": dict({p: ("VDD", ROLE_SUPPLY, "5, 8, 13, 21, VDD PWR 1.1-V power rail 28, 31, 51, 57", None)
                   for p in ("5", "8", "13", "21", "28", "31", "51", "57")},
                  **{p: ("VDD33", ROLE_SUPPLY, "16, 34, VDD33 PWR 3.3-V power rail 52, 63", None)
                     for p in ("16", "34", "52", "63")},
                  **{"48": ("USB_VBUS", "SENSE", "USB_VBUS 48", "USB upstream port power monitor."),
                     "50": ("GRSTz", "RESET", "GRSTz 50", "Global power reset.")})},
    {"part": r"KSZ9897", "document": "v2/vendor/microchip/microchip-ksz9897-datasheet.pdf", "package": "128-pin",
     "pins": dict({str(p): (nm, role, "%d %s" % (p, nm), words) for nm, ps, role, words in _KSZ_POWER for p in ps},
                  **{"96": ("RESET_N", "RESET", "96 RESET_N", "RESET_N IPU Active low system reset.")})},
    # the magnetics' chip-side centre taps: the pin numbers from Pulse's drawing, the role from the PHY maker's own rule
    # for the KSZ9897R these magnetics serve on board B
    {"part": r"H5007NL\b", "document": "v2/vendor/pulse/pulse-h5007nl.pdf", "package": "24-pin SMD",
     "role_document": "v2/vendor/microchip/microchip-ksz9897-datasheet.pdf",
     "pins": {p: ("TCT%d" % i, "CENTRE_TAP", "TCT%d %s" % (i, p),
                  "the four transformer center tap pins on the KSZ9897R chip side should not be connected to any "
                  "power supply source")
              for i, p in ((1, "1"), (2, "4"), (3, "7"), (4, "10"))}},
    {"part": r"BQ4050", "document": "v2/vendor/battery/ti-bq4050.pdf", "package": "RSM VQFN-32",
     "pins": {"1": ("PBI", ROLE_SUPPLY, "PBI 1 P (1) Power supply backup input pin", None),
              "2": ("VC4", "SENSE", "VC4 2 IA", "Sense voltage input pin for the most positive cell"),
              "3": ("VC3", "SENSE", "VC3 3 IA", "Sense voltage input pin for the second most positive cell"),
              "4": ("VC2", "SENSE", "VC2 4 IA", "Sense voltage input pin for the third most positive cell"),
              "5": ("VC1", "SENSE", "VC1 5 IA", "Sense voltage input pin for the least positive cell"),
              "6": ("SRN", "SENSE", "SRN 6 I", "Analog input pin connected to the internal coulomb counter"),
              "8": ("SRP", "SENSE", "SRP 8 I", "Analog input pin connected to the internal coulomb counter"),
              "9": ("VSS", ROLE_GROUND, "VSS 9 P Device ground", None),
              "17": ("DISP", "SIGNAL", "DISP 17 \u2014 Display control for LEDs", None),
              "20": ("LEDCNTLA", "SIGNAL", "LEDCNTLA 20 \u2014", "LED display segment that drives the external LEDs"),
              "21": ("LEDCNTLB", "SIGNAL", "LEDCNTLB 21 \u2014", "LED display segment that drives the external LEDs"),
              "22": ("LEDCNTLC", "SIGNAL", "LEDCNTLC 22 \u2014", "LED display segment that drives the external LEDs"),
              "23": ("PTC", "SENSE", "PTC 23 IA Safety PTC thermistor input pin.", None),
              "26": ("VCC", ROLE_SUPPLY, "VCC 26 P Secondary power supply input", None),
              "27": ("PACK", "SENSE", "PACK 27 IA Pack sense input pin", None),
              "32": ("BAT", ROLE_SUPPLY, "BAT 32 P Primary power supply input pin", None)}},
    {"part": r"BQ77207\d\dDSS", "document": "v2/vendor/battery/ti-bq77207.pdf", "package": "DSS WSON-12",
     "pins": dict({str(p): ("V%d" % v, "SENSE", "%d V%d I Sense input for positive voltage of the %s cell" % (p, v, w),
                            None)
                   for p, v, w in ((2, 7, "seventh"), (3, 6, "sixth"), (4, 5, "fifth"), (5, 4, "fourth"),
                                   (6, 3, "third"), (7, 2, "second"), (8, 1, "first"))},
                  **{"1": ("VDD", ROLE_SUPPLY, "1 VDD P Power supply", None),
                     "9": ("VSS", ROLE_GROUND, "9 VSS P Electrically connected to IC ground", None)})},
    {"part": r"CSD17570Q5B\b", "document": "v2/vendor/battery/ti-csd17570q5b.pdf", "package": "SON 5x6",
     "pins": {p: (n, r, q, None) for p, (n, r, q) in _SON5X6.items()}},
    {"part": r"CSD18510Q5B\b", "document": "v2/vendor/battery/ti-csd18510q5b.pdf", "package": "SON 5x6",
     "pins": {p: (n, r, q, None) for p, (n, r, q) in _SON5X6.items()}},
    {"part": r"CSD19532Q5B\b", "document": "v2/vendor/power/ti-csd19532q5b-n-fet.pdf", "package": "SON 5x6",
     "pins": {p: (n, r, q, None) for p, (n, r, q) in _SON5X6.items()}},
    {"part": r"RP2040\b", "document": "v2/vendor/rp2040/rpi-rp2040-datasheet.pdf", "package": "QFN-56",
     "pins": dict({p: ("IOVDD", ROLE_SUPPLY, "IOVDD 1, 10, 22, 33, 42, 49 IO supply", None)
                   for p in ("1", "10", "22", "33", "42", "49")},
                  **{p: ("DVDD", ROLE_SUPPLY, "DVDD 23, 50 Core supply", None) for p in ("23", "50")},
                  **{"27": ("GPIO16", "SIGNAL", "GPIO16 27 Digital IO (FT)", None),
                     "34": ("GPIO22", "SIGNAL", "GPIO22 34 Digital IO (FT)", None),
                     "38": ("GPIO26 / ADC0", "SIGNAL", "GPIO26 / ADC0 38 Digital IO /", None),
                     "39": ("GPIO27 / ADC1", "SIGNAL", "GPIO27 / ADC1 39 Digital IO /", None),
                     "40": ("GPIO28 / ADC2", "SIGNAL", "GPIO28 / ADC2 40 Digital IO /", None),
                     "43": ("ADC_AVDD", ROLE_SUPPLY, "ADC_AVDD 43 ADC supply", None),
                     "44": ("VREG_VIN", ROLE_SUPPLY, "VREG_VIN 44 Voltage regulator input supply", None),
                     "45": ("VREG_VOUT", ROLE_SUPPLY, "VREG_VOUT 45 Voltage regulator output", None),
                     "48": ("USB_VDD", ROLE_SUPPLY, "USB_VDD 48 USB supply", None),
                     "57": ("GND", ROLE_GROUND, "GND 57 Common ground connection via", None)})},
    {"part": r"PCM2912A\b", "document": "v2/vendor/ti/ti-pcm2912a.pdf", "package": "PJT TQFP-32",
     "pins": {"1": ("BGND", "REFERENCE", "BGND 1 \u2014 Reference for internal regulator", None),
              "2": ("VBUS", ROLE_SUPPLY, "VBUS 2 \u2014 Connect to USB power (VBUS)", None),
              "5": ("VDD", ROLE_SUPPLY, "VDD 5 \u2014 Digital power supply", None),
              "6": ("DGND", ROLE_GROUND, "DGND 6 Digital ground", None),
              "9": ("FL", "SIGNAL", "FL 9 \u2014 External filter pin of L-channel (optional)", None),
              "10": ("FR", "SIGNAL", "FR 10 \u2014 External filter pin of R-channel (optional)", None),
              "11": ("VCOM1", "REFERENCE", "VCOM1 11",
                     "Common voltage for ADC, DAC, and analog front-end (VCCA/2)."),
              "12": ("VCOM2", "REFERENCE", "VCOM2 12", "Common voltage for headphone (VCCA/2)."),
              "13": ("AGND", ROLE_GROUND, "AGND 13 \u2014 Analog ground", None),
              "15": ("VCCA", ROLE_SUPPLY, "VCCA 15 \u2014 Analog power supply", None),
              "16": ("VIN", "SIGNAL", "VIN 16 I ADC microphone input", None),
              "19": ("VCCL", ROLE_SUPPLY, "VCCL 19 \u2014 Analog power supply for headphone amplifier", None),
              "20": ("HGND", ROLE_GROUND, "HGND 20 \u2014 Analog ground for headphone amplifier", None),
              "21": ("VCCR", ROLE_SUPPLY, "VCCR 21 \u2014 Analog power supply for headphone amplifier", None),
              "25": ("PGND", ROLE_GROUND, "PGND 25 \u2014 Analog ground for microphone bias", None),
              "26": ("VCCP", ROLE_SUPPLY, "VCCP 26 \u2014 Analog power supply for PLL", None)}},
    {"part": r"TUSB2046I?B", "document": "v2/vendor/ti/ti-tusb2046b.pdf", "package": "VF LQFP-32",
     "pins": {"3": ("VCC", ROLE_SUPPLY, "VCC 3, 25 3.3-V supply voltage", None),
              "4": ("RESET", "RESET", "RESET 4 I", "RESET is an active low TTL input with hysteresis"),
              "7": ("GND", ROLE_GROUND, "GND 7, 28 GND terminals must be tied to ground", None),
              "8": ("BUSPWR", "SIGNAL", "BUSPWR 8 I", "Power source indicator. BUSPWR is an active-high input that "
                    "indicates whether the downstream ports source their power from the USB cable or a local power "
                    "supply."),
              "25": ("VCC", ROLE_SUPPLY, "VCC 3, 25 3.3-V supply voltage", None),
              "28": ("GND", ROLE_GROUND, "GND 7, 28 GND terminals must be tied to ground", None)}},
    {"part": r"TLV9062IDGK", "document": "v2/vendor/ti/ti-tlv9062-op-amp.pdf", "package": "DGK VSSOP-8",
     "numbering": "Table 5-3. Pin Functions: TLV9062",
     "pins": {"1": ("OUT1", "SIGNAL", "OUT1 1 O Output, channel 1", None),
              "2": ("IN1\u2013", "SIGNAL", "IN1\u2013 2 I Inverting input, channel 1", None),
              "3": ("IN1+", "SIGNAL", "IN1+ 3 I Noninverting input, channel 1", None),
              "4": ("V\u2013", ROLE_SUPPLY, "V\u2013 4 \u2014 Negative (lowest) supply or ground", None),
              "5": ("IN2+", "SIGNAL", "IN2+ 5 I Noninverting input, channel 2", None),
              "8": ("V+", ROLE_SUPPLY, "V+ 8 \u2014 Positive (highest) supply", None)}},
    {"part": r"74LVC86APW\b", "document": "v2/vendor/nexperia/nexperia-74lvc86a.pdf", "package": "PW TSSOP-14",
     "pins": {"2": ("1B", "SIGNAL", "1B, 2B, 3B, 4B 2, 5, 10, 13 data input", None),
              "5": ("2B", "SIGNAL", "1B, 2B, 3B, 4B 2, 5, 10, 13 data input", None),
              "7": ("GND", ROLE_GROUND, "GND 7 ground (0 V)", None),
              "9": ("3A", "SIGNAL", "1A, 2A, 3A, 4A 1, 4, 9, 12 data input", None),
              "14": ("VCC", ROLE_SUPPLY, "VCC 14 supply voltage", None)}},
    {"part": r"LG290P", "document": "v2/vendor/quectel/lg290p03-hardware-design-v1.1.pdf", "package": "LCC",
     "pins": dict({str(p): ("GND", ROLE_GROUND, _LG290P_GND, None) for p in (10, 12, 13) + tuple(range(24, 80))},
                  **{"9": ("VDD_RF", ROLE_SUPPLY, "VDD_RF 9 PO", "Typically used to supply"),
                     "22": ("V_BCKP", ROLE_SUPPLY, "V_BCKP 22 PI", "Power Backup power VImin = 2.0 V connected to "
                            "power supply supply for V_BCKP 22 PI"),
                     "23": ("VCC", ROLE_SUPPLY, "VCC 23 PI", "Main power Requires clean and steady VCC 23 PI VInom = "
                            "3.3 V supply voltage.")})},
    # the power parts whose documents are filed and which no earlier pass held (fourth pass, 27 September 2026): each
    # package's own numbering, read from its own table or pin-out drawing
    {"part": r"AP2112K-", "document": "v2/vendor/diodes/diodes-ap2112-ldo.pdf", "package": "SOT25 (the first number)",
     "pins": {"1": ("VIN", ROLE_SUPPLY, "1 4 8 VIN Input Voltage", None),
              "2": ("GND", ROLE_GROUND, "2 2 6, 7 GND GND", None),
              "3": ("EN", "SIGNAL", "3 5 EN Chip Enable, H \u2013 normal work, L \u2013 shutdown output", None),
              "5": ("VOUT", ROLE_SUPPLY, "5 5 1 VOUT Output Voltage", None)}},
    {"part": r"TLV755\d+PDBV", "document": "v2/vendor/power/ti-tlv755p-ldo.pdf", "package": "DBV SOT-23-5 (the second "
     "number)",
     "pins": {"1": ("IN", ROLE_SUPPLY, "IN 4 1 1 6 I", "Input pin. A capacitor with a value of 1µF or larger"),
              "2": ("GND", ROLE_GROUND, "GND 2 2 2 3 \u2014 Ground pin.", None),
              "3": ("EN", "SIGNAL", "EN 3 3 3 4 I", "Enable pin. Drive EN greater than VHI to turn on the regulator."),
              "5": ("OUT", ROLE_SUPPLY, "OUT 1 5 5 1 O", "Regulated output voltage pin.")}},
    {"part": r"TLV758\d+PDRV", "document": "v2/vendor/ti/ti-tlv758p.pdf", "package": "DRV WSON-6 (Table 4-1)",
     "pins": {"1": ("OUT", ROLE_SUPPLY, "OUT 1 Output", "Regulated output voltage pin."),
              "2": ("FB", "SIGNAL", "FB 2 \u2014", "This pin is used as an input to the control loop error amplifier "
                    "and is used to set the output FB 2 \u2014"),
              "3": ("GND", ROLE_GROUND, "GND 3 \u2014 Ground pin", None),
              "4": ("EN", "SIGNAL", "EN 4 Input", "Enable pin. Drive EN greater than VEN(HI) to turn on the regulator."),
              "6": ("IN", ROLE_SUPPLY, "IN 6 Input", "Input pin. For best transient response")}},
    {"part": r"TLV758\d+PDBV", "document": "v2/vendor/ti/ti-tlv758p.pdf", "package": "DBV SOT-23-5 (Figure 4-2; the "
     "roles from Table 4-1)",
     "pins": {"1": ("IN", ROLE_SUPPLY, "IN 1 5 OUT", "Input pin. For best transient response"),
              "2": ("GND", ROLE_GROUND, "DNC GND 2", "GND 3 \u2014 Ground pin"),
              "3": ("EN", "SIGNAL", "EN 3 4 FB", "Enable pin. Drive EN greater than VEN(HI) to turn on the regulator."),
              "4": ("FB", "SIGNAL", "EN 3 4 FB", "This pin is used as an input to the control loop error amplifier "
                    "and is used to set the output FB 2 \u2014"),
              "5": ("OUT", ROLE_SUPPLY, "IN 1 5 OUT", "Regulated output voltage pin.")}},
    {"part": r"LM74700-Q1", "document": "v2/vendor/ti/ti-lm74700-q1.pdf", "package": "DBV SOT-23-6 (Table 5-1)",
     "pins": {"1": ("VCAP", ROLE_SUPPLY, "1 VCAP O Charge pump output.", None),
              "2": ("GND", ROLE_GROUND, "2 GND G Ground pin", None),
              "3": ("EN", "SIGNAL", "3 EN I Enable pin.", None),
              "4": ("CATHODE", "SENSE", "4 CATHODE I Cathode of the diode.", None),
              "5": ("GATE", "SIGNAL", "5 GATE O Gate drive output.", None),
              "6": ("ANODE", ROLE_SUPPLY, "6 ANODE I", "Anode of the diode and input power.")}},
    {"part": r"TPS2065CDBV", "document": "v2/vendor/ti/ti-tps2065c-slvsau6i.pdf", "package": "DBV SOT-23-5 "
     "(Table 5-2)", "numbering": "Table 5-2. Pin Functions - 5 Pins",
     "pins": {"1": ("OUT", ROLE_SUPPLY, "OUT 1 PWR Power-switch output, connect to load.", None),
              "2": ("GND", ROLE_GROUND, "GND 2 \u2014 Ground connection", None),
              "3": ("FLT", "SIGNAL", "FLT 3 O Active-low open-drain output", None),
              "4": ("EN", "SIGNAL", "EN/ EN 4 I Enable input", None),
              "5": ("IN", ROLE_SUPPLY, "IN 5 PWR Input voltage and power-switch drain;", None)}},
    {"part": r"TPS23861PWR", "document": "v2/vendor/ti/tps23861-datasheet.pdf", "package": "PW TSSOP-28",
     "pins": {"1": ("VDD", ROLE_SUPPLY, "VDD 1 P Digital 3.3-V supply.", None),
              "7": ("DGND", ROLE_GROUND, "DGND 7 P Digital ground.", None),
              "22": ("AGND", ROLE_GROUND, "AGND 22 P Analog ground.", None),
              "28": ("VPWR", ROLE_SUPPLY, "VPWR 28 P Analog 48-V supply.", None)}},
)
_ECAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_netlist(path):
    """({net: {"class": name, "nodes": [(ref, pin, pinfunction, pintype)]}}, {ref: value}) from a KiCad netlist.

    Every net is read, the last one too: KiCad 9.0.9 closes the nets section on the last net's own line, so a net
    ends at the next net or at the end of the file (R4T-F1)."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(?: \(class "([^"]*)"\))?(.*?)(?=\(net \(code|\Z)',
                         txt, re.S):
        nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?'
                           r'(?: \(pintype "([^"]*)"\))?', m.group(3))
        nets[m.group(1).lstrip("/")] = {"class": m.group(2) or "", "nodes": nodes}
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return nets, values


def _shown(path):
    """The path a reading records: relative to v2/ecad where the file is under it, else its directory and name.
    Never absolute, because a reading that records a path under a temporary directory is refused as a fixture's
    (rules_status._temp_input), and a worktree or a box clone may well sit under one."""
    ap = os.path.abspath(path)
    if ap.startswith(_ECAD + os.sep): return os.path.relpath(ap, _ECAD)
    return os.path.join(os.path.basename(os.path.dirname(ap)), os.path.basename(ap))


def _sha16(path):
    try: return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except OSError: return None


def _netlist_input(path):
    """The netlist as a reading records it: path, sha256/16 and the content identity regen_compare computes (no
    export date, path or tool in it), so a copy regenerated with the same design binds by content."""
    rec = {"path": _shown(path), "sha256_16": _sha16(path)}
    try:
        import regen_compare as _rc
        rec["content16"] = _rc.content_hash(open(path, encoding="utf-8", errors="replace").read())
    except Exception as e:                         # the identity is evidence about the reading, never its gate
        rec["content16_absent"] = "%s: %s" % (type(e).__name__, str(e)[:80])
    return rec


def _amps(x):
    """A declared current as a float, or None when it is not a number (bool is not a current)."""
    if isinstance(x, bool) or not isinstance(x, (int, float)): return None
    return float(x)


def _supply_named(fn):
    """True when one token of a pin function names a supply (SUPPLY_TOKEN)."""
    return any(SUPPLY_TOKEN.match(t) for t in re.split(r"[^A-Z0-9]+", str(fn or "").upper()) if t)


def _supply_typed(pt):
    return str(pt or "").split("+")[0] in SUPPLY_PINTYPES


def _is_control(fn, pt):
    """A transistor pin that drives it (gate or base), by the pin's function, or its type where the symbol says input."""
    return str(fn or "").upper() in CONTROL_FUNCTIONS or str(pt or "").split("+")[0] == "input"


def _ohms(value):
    """A resistor's value field in ohms (0R, 10R, 4R7, 0.25R, 10mOhm, 4.7k, 2k2, 1M, R005), or None when not read."""
    t = str(value or "").strip().split()
    if not t: return None
    if len(t) > 1 and re.fullmatch(r"(?i)[kKMR]|m?ohms?|m?\u03a9", t[1]): t = [t[0] + t[1]]    # "10 k", "5 mOhm"
    t = re.sub(r"(?i)ohms?|\u03a9", "R", t[0])
    m = re.match(r"^(\d*\.?\d*)(mR|R|k|K|M|m)?(\d*)$", t)
    if not m or not (m.group(1) or m.group(3)): return None
    num, unit, frac = m.group(1), m.group(2), m.group(3)
    if frac and (not unit or "." in num): return None
    try: x = float((num or "0") + ("." + frac if frac else ""))
    except ValueError: return None
    return x * {None: 1.0, "R": 1.0, "mR": 1e-3, "m": 1e-3, "k": 1e3, "K": 1e3, "M": 1e6}[unit]


def held_roles(values):
    """({(ref, pin): (datasheet name, role, document)}, {document: sha256_16}) for every part whose value field names a
    part number of PIN_ROLES at its start; the first row that matches a part is its row. A connector is no part of a
    row whatever its value field names."""
    import rules_lib as _R
    roles, docs = {}, {}
    for ref, val in sorted((values or {}).items()):
        if is_connector(_R.ref_prefix(ref)): continue
        for row in PIN_ROLES:
            # the part number LEADS the value field, after a maker's name at most: a description further on that
            # mentions another part (board P's PTC thermistor names the gauge it serves) is not that part
            if not re.match(r"(?:%s\s+)?(?:%s)" % (PART_MAKERS, row["part"]), str(val or "")): continue
            for pin, (name, role, _q, _w) in row["pins"].items():
                roles[(ref, pin)] = (name, role, row["document"])
            for d in (row["document"], row.get("role_document")):
                if d and d not in docs: docs[d] = _sha16(os.path.join(os.path.dirname(os.path.dirname(_ECAD)), d))
            break
    return roles, docs


def rails_on_netlist(net_path, intent_path=None, threshold=THRESHOLD_A):
    """Rule PWR-001 on a netlist and its intent file. See the block comment above.

    {checks: [(ok, text)], counts, inputs, power: {net: [why]}, declared_nodes: [text], undecided: {net: why},
     settled: {net: why}, census: {net: disposition}, census_tally: {disposition: count}, missing_input}"""
    stem = os.path.splitext(os.path.basename(net_path))[0]
    intent_path = intent_path or os.path.join(os.path.dirname(os.path.abspath(net_path)), stem + "-intent.json")
    out = {"checks": [], "counts": {}, "power": {}, "declared_nodes": [], "undecided": {}, "missing_input": None,
           "inputs": {"threshold_a": threshold}}
    if not os.path.exists(net_path):
        out["missing_input"] = "no netlist at %s" % _shown(net_path)
        return out
    out["inputs"]["netlist"] = _netlist_input(net_path)
    if not os.path.exists(intent_path):
        out["missing_input"] = "no intent file at %s beside the netlist" % _shown(intent_path)
        return out
    out["inputs"]["intent"] = {"path": _shown(intent_path), "sha256_16": _sha16(intent_path)}
    it = json.load(open(intent_path, encoding="utf-8"))
    nets, values = read_netlist(net_path)
    held, held_docs = held_roles(values)
    for i, d in enumerate(sorted(held_docs), 1):
        # every held datasheet a pin role was read from, by sha, so a corrected or replaced document is seen
        out["inputs"]["document_%d" % i] = {"path": d, "sha256_16": held_docs[d]}
    chk = out["checks"]
    rails = {k.lstrip("/"): v for k, v in (it.get("rails") or {}).items()}
    nodes = {k.lstrip("/") for k in (it.get("nodes") or {})}
    clamps = set((it.get("clamps") or {}).keys())
    if not rails:
        # fail closed, as the board check does: an intent that declares no rail has been compared with nothing
        chk.append((False, "intent file carries at least one rail (%s declares none)" % _shown(intent_path)))
        return out
    bypass = {}                                    # net -> ["cap:part.pin"], the intent's own decoupling statements
    for e in it.get("bypass") or []:
        if isinstance(e, dict) and e.get("net"):
            bypass.setdefault(str(e["net"]).lstrip("/"), []).append("%s:%s.%s" % (e.get("cap"), e.get("part"),
                                                                                 e.get("pin")))
    pins_of = {}                                   # ref -> [(pin, function, type, net)]
    for n, d in nets.items():
        for ref, pin, fn, pt in d["nodes"]:
            pins_of.setdefault(ref, []).append((pin, fn or "", pt or "", n))
    import rules_lib as _R                         # the one place a reference prefix is decided (derate, reliability)

    def skip(n):
        return n.startswith("unconnected-") or bool(GROUND.search(n))

    def held_role(ref, pin):
        return (held.get((ref, pin)) or (None, None, None))[1]

    def ctl(ref, pin, fn, pt):
        """Is this transistor pin its gate or base? The held datasheet's pin-out first, then the pin's own name."""
        r = held_role(ref, pin)
        if r in TRANSISTOR_ROLES: return TRANSISTOR_ROLES[r]
        return _is_control(fn, pt)

    def roles_read(ref):
        return any(ctl(ref, p, f, t) for p, f, t, _n in pins_of.get(ref, []))

    power = {}
    def add(n, why):
        if why not in power.get(n, []): power.setdefault(n, []).append(why)

    def cap_to_ground(n):
        """A capacitor with one pin on n and the other on a ground net: a decoupling capacitor."""
        for ref, _p, _f, _t in nets[n]["nodes"]:
            pp = pins_of.get(ref, [])
            if _R.ref_prefix(ref) == "C" and len(pp) == 2 and any(GROUND_FAMILY.search(x[3]) for x in pp if x[3] != n):
                return ref
        return None

    # (1) to (4b): what the netlist, the intent and the held datasheets say of each net by itself
    for n, d in nets.items():
        if skip(n): continue
        if n.startswith("+"): add(n, "power symbol")
        typed = sorted({"%s.%s" % (r, p) for r, p, _f, pt in d["nodes"] if _supply_typed(pt)})
        if typed: add(n, "supply pin by type (%s)" % ", ".join(typed)[:60])
        cls = str(d["class"] or "").split(",")[0].strip().upper()
        if cls in CLASS_POWER: add(n, "power class %s in the netlist" % cls)
        named = sorted({"%s.%s %s" % (r, p, f) for r, p, f, _pt in d["nodes"] if _supply_named(f)})
        named_parts = {r for r, _p, f, _pt in d["nodes"] if _supply_named(f)}
        if named:
            how = ("the intent's bypass list decouples it (%s)" % ", ".join(bypass[n][:2]) if n in bypass else
                   "capacitor %s joins it to ground" % cap_to_ground(n) if cap_to_ground(n) else
                   "supply pins of %d parts share it" % len(named_parts) if len(named_parts) >= 2 else None)
            if how: add(n, "supply pin by name (%s), and %s" % (", ".join(named)[:60], how))
            elif n not in power:
                out["undecided"][n] = ("supply-named pin %s with no decoupling capacitor, no bypass entry and no "
                                       "second supply pin" % ", ".join(named)[:60])
        sheet = sorted((r, p) for r, p, _f, _pt in d["nodes"] if held_role(r, p) == ROLE_SUPPLY)
        if sheet:
            add(n, "supply pin by its held datasheet (%s: %s)" % (
                ", ".join("%s.%s %s" % (r, p, held[(r, p)][0]) for r, p in sheet)[:60], held[sheet[0]][2]))
        # a pin its datasheet makes the part's GROUND, on a net that is not a ground: the return of the part's supply
        # current runs on it (a gauge's VSS on a sense node, a regulator's GND lifted off the plane), so it is a power
        # net whatever it is called
        earth = sorted((r, p) for r, p, _f, _pt in d["nodes"] if held_role(r, p) == ROLE_GROUND)
        if earth:
            add(n, "supply pin by its held datasheet (a ground pin on a net that is not a ground, %s: %s)" % (
                ", ".join("%s.%s %s" % (r, p, held[(r, p)][0]) for r, p in earth)[:60], held[earth[0]][2]))
        if cls in CLASS_UNDECIDED and n not in power and n not in out["undecided"]:
            out["undecided"][n] = ("class %s in the netlist, a clearance class whose nets carry a supply current or "
                                   "only its control, which the netlist does not tell apart" % cls)
        if n in bypass and n not in power and n not in out["undecided"]:
            out["undecided"][n] = ("the intent's bypass list decouples it (%s), and no pin on it names or types a "
                                   "supply" % ", ".join(bypass[n][:3]))

    # (5): the current a declared rail names, followed through the parts it names
    def passes(ref, frm):
        """(nets a part passes a current arriving on `frm` to, whether its pin roles were read). No nets when the part
        is not one that passes a supply current (a rail on a transistor's gate or base only drives it)."""
        pp = pins_of.get(ref, [])
        pre = _R.ref_prefix(ref)
        if pre in SERIES_PREFIXES and len(pp) == 2:
            return sorted({x[3] for x in pp} - {frm}), True
        if pre in SWITCH_PREFIXES and pp:
            if roles_read(ref):
                mine = [(p, f, t) for p, f, t, n in pp if n == frm]
                if not mine or all(ctl(ref, p, f, t) for p, f, t in mine): return [], True
                return sorted({n for p, f, t, n in pp if not ctl(ref, p, f, t)} - {frm}), True
            return sorted({x[3] for x in pp} - {frm}), False
        return [], True

    def names(rv, ref):
        """Does a rail declaration name this part as its source or one of its loads?"""
        srcs = rv.get("source"); srcs = srcs if isinstance(srcs, (list, tuple)) else ([srcs] if srcs else [])
        return ref in srcs or ref in (rv.get("loads") or {})

    unresolved, seen = [], set()
    def reach(n, why):
        """n carries a current that arrived through a part; an undeclared n passes it on through its switches."""
        if n in rails or skip(n): return
        add(n, why)
        if n in nodes or n in seen: return
        seen.add(n)
        for ref in sorted({r for r, _p, _f, _t in nets[n]["nodes"]}):
            if _R.ref_prefix(ref) not in SWITCH_PREFIXES: continue
            outs, read = passes(ref, n)
            if not read: continue                      # no role to say which net is its channel; n already refused
            for o in outs:
                reach(o, "switch output: the channel of %s from %s, which carries a rail's current" % (ref, n))

    for rn, rv in sorted(rails.items()):
        if rn not in nets: continue
        add(rn, "declared rail")
        srcs = rv.get("source"); srcs = srcs if isinstance(srcs, (list, tuple)) else ([srcs] if srcs else [])
        # a current that is not a number is refused below, where the rail's destination is judged; here it is
        # simply not followed, so a malformed declaration is reported rather than crashing the reading
        flows = [(s, _amps(rv.get("amps_peak")), "source") for s in srcs]
        flows += [(ld, _amps(a), "load") for ld, a in (rv.get("loads") or {}).items()]
        for ref, amps, how in flows:
            if amps is None or amps <= threshold: continue
            outs, read = passes(ref, rn)
            outs = [o for o in outs if not skip(o)]
            if not outs: continue
            if not read:
                # answered only by a declared rail among its other nets that names this switch: a declared net that
                # names nothing (a gate line declared as a node) does not say which of them is the channel
                if not any(o in rails and names(rails[o], ref) for o in outs):
                    unresolved.append((rn, ref, outs, amps))
                continue
            kind = "series conductor" if _R.ref_prefix(ref) in SERIES_PREFIXES else "switch output"
            for o in outs:
                reach(o, "%s: the %s %s of rail %s at %.2f A" % (kind, how, ref, rn, amps))

    # (6) FAIL CLOSED: every net with the mark of a supply is counted, declared, settled by what is read, or undecided
    hot = {n for n in list(power) + list(rails) if n in nets and not skip(n)}

    def only_part(n):
        """The one part whose pins are the only pins on n that are not a resistor's, capacitor's or test point's."""
        parts = {r for r, _p, _f, _t in nets[n]["nodes"] if _R.ref_prefix(r) not in MARK_PASSIVE}
        return next(iter(parts)) if len(parts) == 1 else None

    def two_pin(ref):
        pre, pp = _R.ref_prefix(ref), pins_of.get(ref, [])
        return len(pp) == 2 and (pre in MARK_SERIES or pre.startswith("SW"))

    def marks(n, warm):
        """The marks of a supply n carries. `hot` holds the counted and declared power nets; `warm` adds the undecided
        ones, which may be supplies, so a two-terminal DC link from one of them (M3) marks its neighbour too: board B's
        antenna feed runs from the module's VDD_RF through R23 to GNSS_BIAS and through L3 to GNSS_ANT."""
        m = []
        here = sorted({r for r, _p, _f, _t in nets[n]["nodes"]})
        no_ic = not any(_R.ref_prefix(r) in MARK_IC for r in here)
        for ref in here:
            pre, pp = _R.ref_prefix(ref), pins_of.get(ref, [])
            others = {x[3] for x in pp} - {n}
            if pre == "C" and len(pp) == 2 and others:
                o = next(iter(others))
                if GROUND_FAMILY.search(o): m.append("M1 capacitor %s to ground" % ref)
                elif o in hot: m.append("M2 capacitor %s to the power net %s" % (ref, o))
                elif not skip(o) and only_part(n) and only_part(n) == only_part(o):
                    m.append("M2 capacitor %s across two pins of %s" % (ref, only_part(n)))
            elif two_pin(ref) and (others & warm) and ref not in clamps:
                m.append("M3 %s joins it to the %s net %s" % (ref, "power" if others & hot else "undecided",
                                                               sorted(others & warm)[0]))
            elif pre == "R" and len(pp) == 2 and (others & warm) and no_ic and \
                    (_ohms(values.get(ref)) is None or _ohms(values.get(ref)) <= MARK_R_SUPPLY_OHM):
                # a supply through a resistor no rail names: a part with no decoupling of its own on the far side (a
                # connector, a lamp, an inductor) is fed through it; an integrated circuit fed this way decouples its
                # own supply pin on the net, which is mark M1
                m.append("M3 resistor %s (%s) joins it to the %s net %s, and no integrated circuit is on it"
                         % (ref, values.get(ref, "")[:12], "power" if others & hot else "undecided",
                            sorted(others & warm)[0]))
            elif pre in SWITCH_PREFIXES and pp:
                live = sorted(x for x in others & hot if not GROUND.search(x))
                if roles_read(ref):
                    # the LOW SIDE of a load: this net is the transistor's channel and its other channel pins sink to
                    # ground, and a part on the net is a load that is not an integrated circuit, a resistor, a
                    # capacitor, a test point, a transistor or a connector (a fuse's heater, a lamp, a relay coil): the
                    # load's supply current returns through this net (board P's SCP_HTR, the fuse heater's return)
                    mine = [(p, f, t) for p, f, t, x in pp if x == n]
                    chan = [x for p, f, t, x in pp if x != n and not ctl(ref, p, f, t)]
                    if mine and not all(ctl(ref, p, f, t) for p, f, t in mine) and chan and \
                            all(skip(x) for x in chan):
                        loads = [r for r in here if r != ref and _R.ref_prefix(r) not in
                                 MARK_PASSIVE + MARK_IC + SWITCH_PREFIXES and not is_connector(_R.ref_prefix(r))]
                        if loads:
                            m.append("M4 the switched return of %s: the channel of %s sinks it to ground"
                                     % (", ".join(loads[:3]), ref))
                if not live: continue
                if roles_read(ref):
                    mine = [(p, f, t) for p, f, t, x in pp if x == n]
                    chan = {x for p, f, t, x in pp if not ctl(ref, p, f, t)}
                    if mine and not all(ctl(ref, p, f, t) for p, f, t in mine) and (chan & set(live)):
                        m.append("M4 the channel of %s with the net %s" % (ref, sorted(chan & set(live))[0]))
                else:
                    loads = [r for r in here if r != ref and _R.ref_prefix(r) not in MARK_PASSIVE + MARK_IC]
                    if loads:
                        m.append("M4 %s, whose pin roles nothing reads, with the net %s, and %s on it"
                                 % (ref, live[0], ", ".join(loads[:3])))
            elif is_connector(pre) and pp:
                # M5 A LEAD: a connector whose every other pin is on ground or unconnected carries this net and its
                # return and nothing else, and a part on the board drives or takes it (a supply lead to a monitor, a
                # push-button line); a supply a part of three or more pins delivers off the board straight to a lead
                # carries no decoupling and no two-terminal link on this board (board A's VMON, the eFuse U21's
                # output), so without this mark nothing marks it
                rest = [x[3] for x in pp if x[3] != n]
                feeders = [r for r in here if not is_connector(_R.ref_prefix(r)) and _R.ref_prefix(r) not in MARK_PASSIVE]
                if rest and all(skip(x) for x in rest) and feeders:
                    m.append("M5 a lead: %s carries it with only ground beside it, from %s"
                             % (ref, ", ".join(feeders[:3])))
        cls = {c.strip().upper() for c in str(nets[n]["class"] or "").split(",") if c.strip()}
        if cls & MARK_SENSE_CLASSES:
            m.append("M6 class %s in the netlist: the conductor senses a supply" % "/".join(sorted(cls & MARK_SENSE_CLASSES)))
        return m

    def settle(n, marks=()):
        """Why n supplies nothing, from what is read, or None when something on it is not read."""
        why = []
        for ref, pin, fn, pt in nets[n]["nodes"]:
            # a crystal or resonator: two terminals on nets of their own (a can's other pins on ground); a part of
            # this prefix with a third live net is an oscillator with a supply pin, and that is read like any part
            live = {x[3] for x in pins_of.get(ref, []) if not skip(x[3])}
            if _R.ref_prefix(ref) in MARK_CRYSTAL and len(live) <= 2:
                return "an oscillator net: %s is a crystal or resonator" % ref
        # on a net whose only marks are a lead (M5) or a sense class (M6), a connector carries what the board's own
        # pins on it carry, so it is passed over when one of them is read; on any other mark it is read by nothing
        lead = bool(marks) and all(str(x).startswith(("M5", "M6")) for x in marks)
        passed = []
        for ref, pin, fn, pt in nets[n]["nodes"]:
            pre = _R.ref_prefix(ref)
            if pre in MARK_PASSIVE: continue
            if lead and is_connector(pre):
                passed.append("%s.%s" % (ref, pin)); continue
            h = held.get((ref, pin))
            if h and h[1] not in (ROLE_SUPPLY, ROLE_GROUND) and h[1] not in TRANSISTOR_ROLES:
                why.append("%s.%s %s (%s, %s)" % (ref, pin, h[0], h[1].lower().replace("_", " "),
                                                  os.path.basename(h[2])))
                continue
            if pre in SWITCH_PREFIXES:
                if ctl(ref, pin, fn, pt):
                    why.append("%s.%s the transistor's %s" % (ref, pin, "gate or base")); continue
                chan = [x for p, f, t, x in pins_of.get(ref, []) if p != pin and not ctl(ref, p, f, t)]
                if roles_read(ref) and chan and all(skip(x) for x in chan):
                    why.append("%s.%s a channel that sinks to ground" % (ref, pin)); continue
                return None
            if ref in clamps:
                why.append("%s.%s a clamp the intent declares" % (ref, pin)); continue
            if pre.startswith("SW") or pre == "JP":
                rest = [x for p, f, t, x in pins_of.get(ref, []) if p != pin]
                if rest and all(skip(x) for x in rest):
                    why.append("%s.%s a %s to ground" % (ref, pin, "switch" if pre.startswith("SW") else "jumper"))
                    continue
            return None
        if passed:
            # a lead is settled only by a pin the board reads: a connector with resistors alone says nothing
            if not why: return None
            why.append("the lead %s carries what these pins carry" % ", ".join(passed[:3]))
        return "nothing on it supplies: " + "; ".join(why) if why else "only resistors, capacitors and test points"

    # A DECLARED NODE THAT CARRIES THE MARK OF A SUPPLY IS A POWER NET FOR ITS NEIGHBOURS (fifth pass, 27 September
    # 2026, the fourth independent check's blocking item). `hot` held the counted nets and the declared rails only, so
    # a node kinds (1) to (5) did not count and the board declared (board C's EPD_SW: marked M3 through the boost
    # inductor L1, then declared as a node) passed no mark on: the boost switch Q6 carries the inductor's current from
    # EPD_SW into EPD_RESE and the 0.47R shunt R43 every on-phase, and EPD_RESE read unmarked in every census. A node
    # enters `hot` only when it carries a mark itself (marks(n, hot)); every declared node would also have marked board
    # B's SIM2_CLK, SIM2_IO and SIM2_RST through the eSIM's 0R links, which are over-marks. Measured on the six committed
    # netlists of fc144600: it moves exactly one net, EPD_RESE, from unmarked to undecided.
    hot |= {n for n in nodes if n in nets and not skip(n) and n not in hot and marks(n, hot)}
    settled = {}
    for n in sorted(out["undecided"]):
        if n in power or n in rails or n in nodes: continue
        why = settle(n)
        if why:
            settled[n] = why; del out["undecided"][n]
    # to a fixed point: a net found undecided is warm, and a DC path from it marks the next net
    while True:
        warm = hot | {n for n in out["undecided"] if n not in power and n not in rails and n not in nodes}
        grew = False
        for n in sorted(nets):
            if skip(n) or n in power or n in rails or n in nodes or n in settled or n in out["undecided"]: continue
            m = marks(n, warm)
            if not m: continue
            why = settle(n, m)
            if why: settled[n] = why
            else:
                unread = sorted({"%s.%s" % (r, p) for r, p, _f, _t in nets[n]["nodes"]
                                 if _R.ref_prefix(r) not in MARK_PASSIVE})
                out["undecided"][n] = ("it carries the mark of a supply (%s) and nothing read settles it: %s"
                                       % ("; ".join(m[:2]), ", ".join(unread[:5]) or "no part"))
                grew = True
        if not grew: break
    out["power"] = power
    # a declaration settles an undecided net, and a net that (5) reached is no longer undecided
    out["undecided"] = {n: w for n, w in sorted(out["undecided"].items())
                        if n not in power and n not in rails and n not in nodes}
    out["settled"] = settled
    census = {}
    for n in nets:
        if n.startswith("unconnected-"): census[n] = "unconnected"
        elif GROUND.search(n) and n not in rails: census[n] = "ground"
        elif n in nodes and n not in rails: census[n] = "declared node"
        elif n in power or n in rails: census[n] = "counted"
        elif n in out["undecided"]: census[n] = "undecided"
        elif n in settled: census[n] = "settled"
        else: census[n] = "unmarked"
    out["census"] = census

    # every declared rail: a net of the netlist, and its current goes somewhere on it
    missing, nowhere = [], []
    for rn, rv in sorted(rails.items()):
        if rn not in nets:
            missing.append(rn)
            chk.append((False, "intent rail %s is a net of the netlist (it is not)" % rn)); continue
        here = {r for r, _p, _f, _t in nets[rn]["nodes"]}
        srcs = rv.get("source"); srcs = list(srcs) if isinstance(srcs, (list, tuple)) else ([srcs] if srcs else [])
        loads = dict(rv.get("loads") or {})
        off = sorted(x for x in list(srcs) + list(loads) if x not in here)
        bad_amps = sorted(x for x, a in loads.items() if _amps(a) is None or a < 0)
        ok = bool(loads) and bool(srcs) and not off and not bad_amps
        if not ok: nowhere.append(rn)
        chk.append((ok, "intent rail %s names where its current goes: source %s and %d load(s)%s%s%s" % (
            rn, ", ".join(srcs) or "NONE", len(loads),
            "" if loads else ", and a rail with no load says nowhere",
            ("; not on %s in the netlist: %s" % (rn, ", ".join(off[:8]))) if off else "",
            ("; load current not a non-negative number: %s" % ", ".join(bad_amps[:6])) if bad_amps else "")))
    # every power net of the netlist is a declared rail, or a declared node that supplies one part at most
    undeclared = sorted(n for n in power if n not in rails and n not in nodes)
    for n in undeclared:
        chk.append((False, "power net %s is a declared rail (it is not: %s)" % (n, "; ".join(power[n])[:160])))
    spread = []
    for n in sorted(x for x in power if x in nodes and x not in rails):
        parts = sorted({r for r, p, f, pt in nets[n]["nodes"]
                        if _supply_typed(pt) or _supply_named(f) or held_role(r, p) == ROLE_SUPPLY})
        if len(parts) >= 2:
            spread.append(n)
            chk.append((False, "node %s supplies one part at most (it carries the supply pins of %d: %s; a supply "
                               "that reaches two parts is a rail)" % (n, len(parts), ", ".join(parts[:6]))))
        else:
            out["declared_nodes"].append("%s (%s)" % (n, "; ".join(power[n])[:120]))
    for rn, ref, outs, amps in unresolved:
        chk.append((False, "the %s %s of rail %s at %.2f A passes its current to a declared net (none of %s is a "
                           "declared rail that names it, and nothing reads a gate or base role that says which is its "
                           "channel)" % ("switch" if _R.ref_prefix(ref) in SWITCH_PREFIXES else "part", ref, rn, amps,
                                         ", ".join(outs[:4]))))
    have = sorted(n for n in rails if n in nets)
    kinds = lambda key: sum(1 for w in power.values() if any(x.startswith(key) for x in w))
    counted = [n for n in power if n not in nodes or n in rails]
    chk.append((not undeclared and not missing and not spread and not unresolved,
                "the count of declared rails equals the count of power nets carrying more than %.2f A: %d declared "
                "(%d of them nets of the netlist), %d power nets not declared as nodes (by kind, a net counted under "
                "each that applies: %d power-symbol, %d supply-pin by type, %d power-class, %d supply-pin by name, "
                "%d supply-pin by its held datasheet, %d reached by a rail's current, %d declared rails), %d declared "
                "as nodes%s" % (
                    threshold, len(rails), len(have), len(counted), kinds("power symbol"), kinds("supply pin by type"),
                    kinds("power class"), kinds("supply pin by name"), kinds("supply pin by its held datasheet"),
                    sum(1 for w in power.values() if any(x.startswith(("series conductor", "switch output"))
                                                         for x in w)),
                    kinds("declared rail"), len(out["declared_nodes"]) + len(spread),
                    ("; undeclared: " + ", ".join(undeclared[:14])) if undeclared else "")))
    tally = {k: sum(1 for v in census.values() if v == k)
             for k in ("counted", "declared node", "undecided", "settled", "unmarked", "ground", "unconnected")}
    out["counts"] = {"declared_rails": len(rails), "power_nets": len(counted), "undeclared": len(undeclared),
                     "declared_not_in_netlist": len(missing), "rails_without_destination": len(nowhere),
                     "declared_nodes": len(out["declared_nodes"]), "nodes_supplying_parts": len(spread),
                     "switches_unresolved": len(unresolved), "undecided": len(out["undecided"]),
                     "settled": len(settled), "unmarked": tally["unmarked"],
                     "census_nets": len(census), "held_pin_roles": len(held)}
    out["census_tally"] = tally
    return out


def write_rails_verdict(res, out_dir=None, board=None, quiet=False):
    """Write the intent_rails verdict (rule PWR-001) from rails_on_netlist's result; returns the exit code."""
    import verdict as _v
    checks = res["checks"]
    fails = [t for ok, t in checks if not ok]
    inputs = dict(res.get("inputs") or {})
    if board: inputs["board"] = board
    if res.get("missing_input"):
        return _v.write("intent_rails", _v.INCONCLUSIVE, denominator=0, inputs=inputs, out_dir=out_dir, quiet=quiet,
                        missing_input=res["missing_input"], rules=["PWR-001"],
                        note="PWR-001 is judged on the netlist and its intent file, and one of them is not there")
    und = res.get("undecided") or {}
    settled = res.get("settled") or {}
    result = _v.FAIL if fails else (_v.INCONCLUSIVE if (und or not checks) else _v.PASS)
    tally = res.get("census_tally") or {}
    # verdict.write keeps 50 evidence lines, so the census and every undecided and settled NAME come first, each on
    # one line, and the per-net reasons fill what is left: board B's reading names 28 refusals and 22 undecided nets
    ev = []
    if tally:
        ev.append("census of the %d nets: %s" % (sum(tally.values()),
                                                 ", ".join("%d %s" % (tally[k], k) for k in sorted(tally))))
    if und: ev.append("undecided, named and not counted (%d): %s" % (len(und), ", ".join(sorted(und))))
    if settled: ev.append("settled, they supply nothing (%d): %s" % (len(settled), ", ".join(sorted(settled))))
    ev += fails[:34]
    room = max(0, 50 - len(ev))
    ev += ["undecided, named and not counted: %s: %s" % (n, w) for n, w in sorted(und.items())][:room]
    room = max(0, 50 - len(ev))
    ev += ["declared as a node, not a rail: %s" % x for x in res["declared_nodes"]][:min(room, 10)]
    room = max(0, 50 - len(ev))
    ev += ["settled, it supplies nothing: %s: %s" % (n, w) for n, w in sorted(settled.items())][:room]
    return _v.write("intent_rails", result,
                    counts=dict(res["counts"], fail=len(fails), checks=len(checks)), denominator=len(checks),
                    evidence=ev,
                    inputs=inputs, out_dir=out_dir, quiet=quiet, rules=["PWR-001"],
                    note="PWR-001 on the committed netlist and the intent file beside it: every power net is a "
                         "declared rail, and every declared rail is a net of the netlist whose source and loads are "
                         "on it. A power net is a power-symbol net, a net carrying a pin typed power_in or power_out, "
                         "a net of a power class in the netlist, a net carrying a supply-named pin that a bypass "
                         "entry, a capacitor to ground or a second supply pin corroborates, a net carrying a pin its "
                         "held datasheet makes a supply, or a ground off a ground net (intent_checks.PIN_ROLES, each "
                         "row carrying every power and ground pin of its table, each document recorded by sha), or a "
                         "net a declared rail's current reaches through a two-terminal part or a transistor's channel, "
                         "at a threshold of %.2f A. FAIL CLOSED: every other net carrying the mark of a supply (a "
                         "capacitor to ground, a capacitor to a power net or across one part's pins, a fuse, inductor, "
                         "ferrite, diode, jumper, switch or link resistor to a power net, a transistor channel shared "
                         "with one, the switched low side of a load, a lead whose other pins are all ground, a sense "
                         "class) is settled only by what is read (a crystal, a held non-supply pin role, a gate, a "
                         "sink to ground, a declared clamp, a switch to ground; on a lead or a sense net the "
                         "connector carries what the read pins carry) and is otherwise undecided; an "
                         "undecided net holds the reading at INCONCLUSIVE when nothing fails, and the census names "
                         "every net's disposition. A power net declared as a node is reported, and refused when it "
                         "carries the supply pins of two or more parts. Session decisions of 26 September 2026 under "
                         "the owner's standing rule: the kinds of power net, the fail-closed marks and the undecided "
                         "class, the 0 A threshold, the node rule" % float(inputs.get("threshold_a") or 0.0))


def netlist_main(argv):
    """intent_checks.py --netlist <netlist.net> [--intent <intent.json>] [--out-dir DIR]: rule PWR-001 alone."""
    import verdict as _v, boardtable as _bt
    net = _v.opt(argv, "--netlist")
    if not net: print(__doc__); return 2
    res = rails_on_netlist(net, _v.opt(argv, "--intent"))
    for ok, t in res["checks"]: print(("PASS  " if ok else "FAIL  ") + t)
    for n, w in sorted((res.get("undecided") or {}).items()): print("UNDECIDED  %s: %s" % (n, w))
    for x in res["declared_nodes"]: print("NOTE  declared as a node, not a rail: %s" % x)
    for n, w in sorted((res.get("settled") or {}).items()): print("SETTLED  %s: %s" % (n, w))
    if res.get("census_tally"):
        print("CENSUS  " + ", ".join("%d %s" % (v, k) for k, v in sorted(res["census_tally"].items())))
    if res.get("missing_input"): print("intent_checks: %s" % res["missing_input"])
    return write_rails_verdict(res, out_dir=_v.opt(argv, "--out-dir"), board=_bt.letter_for(net) or None)


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    if "--netlist" in sys.argv:
        import verdict as _vn
        sys.exit(_vn.guard("intent_rails", netlist_main, sys.argv[1:]))
    fails = []; checked = []
    def check(ok, text):
        print(("PASS  " if ok else "FAIL  ") + text)
        checked.append(text)
        if not ok: fails.append(text)
    print(run(pcbnew.LoadBoard(sys.argv[1]), check, sys.argv[1]))
    print("RESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails))
    import os as _osv
    sys.path.insert(0, _osv.path.dirname(_osv.path.abspath(__file__)))
    import verdict as _v

    # ONE VERDICT PER RULE, and the reason is the same one that split dc_drop. This file runs FOUR separate
    # rules: the return path under a signal (RET-001 and its screen RET-002), the return via at a transition
    # (RET-004), the decoupling loop (DEC-001) and whether every power-symbol net is a declared rail (PWR-001).
    # They were sharing one verdict, so ONE decoupling capacitor 3 mm too far from its pin failed the
    # return-path rule on the same board, and on 16 September that single item was failing three rules across
    # six boards: eighteen rule-board pairs reported as failures of things that had passed.
    BUCKETS = (("intent_return_path", ("return path",), "the reference under a signal net, judged per spectral class"),
               ("intent_return_via", ("return via",), "a ground via at a signal's reference change"),
               ("intent_decoupling", ("bypass", "decoupling"), "the loop from a decoupling capacitor to the pin it serves"),
               ("intent_rails", ("is a declared rail", "intent rail", "intent file carries"), "every power-symbol net declared with its loads"))
    # A CHECK BELONGS TO EXACTLY ONE RULE, and the first version decided that by searching the whole message
    # (16 September 2026, evening). Every return-path line QUOTES the net's declared basis in brackets, and
    # board B's three STM32 core-regulator nets are declared as "an internal-supply decoupling node, a local
    # rail": the word decoupling in that quotation put three RETURN-PATH failures into the DECOUPLING verdict,
    # so rule DEC-001 failed on board B for something that is not decoupling and has nothing to do with the
    # loop it measures. The same shape as the composite verdict this bucket split was written to fix, one level
    # down. The evidence quotation is stripped before the keys are matched, and a line that two buckets claim
    # is named rather than counted twice.
    head = lambda t: t.split("[")[0]
    # RULE PWR-001 IS THE NETLIST'S, NOT THE BOARD'S (26 September 2026, MESHSAT-1357). Where the netlist this board
    # was placed from sits beside it (out/<stem>.net, the file netlist_board compares the board with), intent_rails is
    # written from rails_on_netlist and records the netlist by sha and by content, so a run of this gate on a layout
    # that is not the candidate's can never stand in front of the schematic reading or make it wait on a layout. The
    # board's own rail lines (every power-symbol net ON THE BOARD is declared, every rail IS A NET OF THE BOARD) are
    # then a question of whether the layout carries the netlist, which is SCH-002's, and they fall to intent_other,
    # which the finish still blocks on. A board with no netlist (E5, which has no schematic) keeps the board lines.
    _stem = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    _net = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "out", _stem + ".net")
    _nl = rails_on_netlist(_net) if os.path.exists(_net) else None
    if _nl is not None:
        for _ok, _t in _nl["checks"]: print(("PASS  " if _ok else "FAIL  ") + "netlist: " + _t)
    claimed, multi = set(), {}
    for name, keys, note in BUCKETS:
        mine = [t for t in checked if any(k in head(t) for k in keys)]
        if name == "intent_rails" and _nl is not None:
            # the board LETTER, not the board file: this reading judged the netlist and no copper
            import boardtable as _btn
            write_rails_verdict(_nl, quiet=True, board=_btn.letter_for(sys.argv[1]) or None)
            continue                                   # the board's rail lines are left unclaimed: intent_other
        for t in mine: multi.setdefault(t, []).append(name)
        claimed.update(mine)
        bad = [t for t in mine if t in fails]
        counts = {"fail": len(bad), "pass": len(mine) - len(bad)}
        if name == "intent_decoupling" and LAST_DECOUPLING:
            # a justified deviation and a recorded distance are lines that did not fail, and they are not passes
            # (decision 42, T6): the verdict carries them as what they are
            _t = LAST_DECOUPLING
            counts = {"fail": len(bad), "pass": len(mine) - len(bad) - _t["justified"] - _t["recorded"],
                      "justified": _t["justified"], "recorded": _t["recorded"], "no_own_via": _t["no_own_via"],
                      "far_side": _t["far_side"], "unclassed": _t["unclassed"], "allow_lines_refused": _t["allow_lines_refused"]}
        _v.write(name, _v.INCONCLUSIVE if not mine else (_v.FAIL if bad else _v.PASS),
                 counts=counts, denominator=len(mine),
                 evidence=bad[:20], inputs={"board": sys.argv[1]}, quiet=True,
                 note=note if mine else "nothing of this kind was checked on this board")
    # anything this file checks that no bucket claims still has to decide something, or a rule could be added
    # here and silently belong to nothing
    both = sorted(t for t, ns in multi.items() if len(ns) > 1)
    for t in both:
        print("intent_checks: THIS CHECK BELONGS TO %d RULES AND MUST BELONG TO ONE (%s): %s"
              % (len(multi[t]), ", ".join(multi[t]), t[:120]))
    rest = [t for t in checked if t not in claimed] + both
    if rest:
        _v.write("intent_other", _v.FAIL if [t for t in rest if t in fails] else _v.PASS,
                 counts={"fail": len([t for t in rest if t in fails]), "pass": len([t for t in rest if t not in fails])},
                 denominator=len(rest), evidence=[t for t in rest if t in fails][:20],
                 inputs={"board": sys.argv[1]}, quiet=True,
                 note="checks this file makes that no rule bucket claims yet")
    # the whole file counts the netlist's PWR-001 lines too, after intent_other has taken its share, so none of them
    # is counted twice and the composite still says everything this run decided
    if _nl is not None:
        for _ok, _t in _nl["checks"]:
            checked.append("netlist: " + _t)
            if not _ok: fails.append("netlist: " + _t)
    sys.exit(_v.write("intent_checks",
                      _v.INCONCLUSIVE if not checked else (_v.PASS if not fails else _v.FAIL),
                      counts={"fail": len(fails), "pass": len(checked) - len(fails), "unclaimed": len(rest)},
                      denominator=len(checked), evidence=fails, inputs={"board": sys.argv[1]},
                      note=("the whole file; each rule also has its own verdict (intent_return_path, "
                            "intent_return_via, intent_decoupling, intent_rails)" if checked
                            else "the intent file yielded no check")))
