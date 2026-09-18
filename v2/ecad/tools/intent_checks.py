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
  2. decoupling: every bypass entry (capacitor, part, pin) has its capacitor's rail pad within LOOP_MM of the pin's pad centre (3.0 mm for 100 nF
     and smaller, 6.0 mm for bulk), and both the capacitor's rail pad and its ground pad reach a via or a pour within 1.5 mm (the loop closes
     through the planes, not across the board); reported per entry, FAIL on distance;
  3. every rail of the intent file exists on the board with pads on it (a renamed rail is a FAIL, not a silent skip).
A board without an intent file is a FAIL (fail closed). Denominators print on every summary line.
Used as a module by the check_pcb_*.py gates: intent_checks.run(board, check)  or standalone: intent_checks.py <board.kicad_pcb>."""
import sys, os, math, json
import netclass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import kicad_compat as _kc, intent, signalnets, return_via, signal_class

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

def run(b, check, path=None):
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
    # the same recorded-exception idiom as erc-allow.txt: a decoupling distance may stand only if the board's own
    # bypass-allow.txt gives a reason, and the report still names every entry and its distance (8 Sep 2026 18:25)
    allow_p = os.path.join(os.path.dirname(os.path.abspath(path)) if path else ".", "bypass-allow.txt")
    allowed = [l.strip() for l in open(allow_p).read().splitlines() if l.strip() and not l.startswith("#")] if os.path.exists(allow_p) else []
    n_by = 0; n_far = 0
    for e in it.get("bypass", []):
        n_by += 1
        cap = [p for (ref, num), p in pads.items() if ref == e["cap"]]; pin = pads.get((e["part"], e["pin"]))
        if not cap or pin is None: check(False, "bypass %s -> %s.%s: pads found on the board" % (e["cap"], e["part"], e["pin"])); continue
        rail = [p for p in cap if p.GetNetname() == pin.GetNetname()]; gnd = [p for p in cap if p.GetNetname() != pin.GetNetname()]
        if not rail: check(False, "bypass %s -> %s.%s: the capacitor shares the pin's net %s" % (e["cap"], e["part"], e["pin"], pin.GetNetname())); continue
        d = math.hypot(rail[0].GetPosition().x - pin.GetPosition().x, rail[0].GetPosition().y - pin.GetPosition().y) / 1e6
        val = next((f.GetValue() for f in b.GetFootprints() if f.GetReference() == e["cap"]), "")
        loop = 6.0 if any(u in val.lower() for u in ("u ", "uf", "u,", "µ")) and not val.lower().startswith(("0.1u", "0.01u")) else 3.0
        if d > loop and allowed:
            n_far += 1
            check(True, "bypass %s (%s) to %s.%s: %.2f mm pad to pin, allowed by bypass-allow.txt [%s]" % (e["cap"], val, e["part"], e["pin"], d, allowed[0][:56]))
        else:
            check(d <= loop, "bypass %s (%s) to %s.%s: %.2f mm pad to pin (limit %.1f)" % (e["cap"], val, e["part"], e["pin"], d, loop))
        if d > loop and allowed: continue                  # a capacitor that far away has no loop worth measuring
        check(closes(rail[0]) and (not gnd or closes(gnd[0])), "bypass %s: rail and ground pads reach a via or pour within %.1f mm" % (e["cap"], NEAR_VIA))
    # 3. rails exist
    names = {b.GetNetInfo().GetNetItem(k).GetNetname().lstrip("/") for k in range(1, b.GetNetInfo().GetNetCount())}
    for net in it.get("rails", {}): check(net.lstrip("/") in names, "intent rail %s is a net of the board" % net)
    if n_far: print("intent_checks: %d of %d bypass entries are past their limit and allowed by bypass-allow.txt" % (n_far, n_by))
    return "intent_checks: return path on %d nets, return via on %d signal vias, %d bypass entries, %d rails checked" % (n_nets, rv["judged"], n_by, len(it.get("rails", {})))

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
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
    claimed, multi = set(), {}
    for name, keys, note in BUCKETS:
        mine = [t for t in checked if any(k in head(t) for k in keys)]
        for t in mine: multi.setdefault(t, []).append(name)
        claimed.update(mine)
        bad = [t for t in mine if t in fails]
        _v.write(name, _v.INCONCLUSIVE if not mine else (_v.FAIL if bad else _v.PASS),
                 counts={"fail": len(bad), "pass": len(mine) - len(bad)}, denominator=len(mine),
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
    sys.exit(_v.write("intent_checks",
                      _v.INCONCLUSIVE if not checked else (_v.PASS if not fails else _v.FAIL),
                      counts={"fail": len(fails), "pass": len(checked) - len(fails), "unclaimed": len(rest)},
                      denominator=len(checked), evidence=fails, inputs={"board": sys.argv[1]},
                      note=("the whole file; each rule also has its own verdict (intent_return_path, "
                            "intent_return_via, intent_decoupling, intent_rails)" if checked
                            else "the intent file yielded no check")))
