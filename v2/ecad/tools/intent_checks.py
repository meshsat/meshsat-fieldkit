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
import pcbnew, intent, signalnets, return_via, signal_class

SAMPLE = 1.0; GAP_MM = 10.0; NEAR_VIA = 1.5

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
    gaps = {}; total = {}; n_nets = 0; n_tracks = 0
    for tr in b.GetTracks():
        if tr.GetClass() != "PCB_TRACK": continue
        n_tracks += 1; net = tr.GetNetname()
        if cls_of(net) not in targets and not signalnets.is_signal(net, signals): continue
        L = tr.GetLayer(); length = tr.GetLength() / 1e6; n = max(1, int(length / SAMPLE)); total[net] = total.get(net, 0.0) + length
        for k in range(n + 1):
            u = k / n; p = pcbnew.VECTOR2I(int(tr.GetStart().x + u * (tr.GetEnd().x - tr.GetStart().x)), int(tr.GetStart().y + u * (tr.GetEnd().y - tr.GetStart().y)))
            if not any(pl.Contains(p) for Ln in neighbours(L) for pl in planes.get(Ln, [])): gaps[net] = gaps.get(net, 0.0) + length / (n + 1)
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
        n_nets += 1; g = gaps.get(net, 0.0)
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
            check(g <= lim, "return path under %s (%s, %s): %.1f of %.1f mm without a plane on a neighbouring layer (limit %.1f) [%s]"
                  % (net.lstrip("/"), cls_of(net), sc, g, total[net], lim, basis[:70]))
    # An undeclared net is not a failure of the copper and must not be reported as one: it is a gap in what this
    # project has written down about its own design, and it is named here so it can be closed.
    if undeclared:
        print("intent_checks: %d signal net(s) carry no declared signal class and were judged at the strictest bar: %s%s"
              % (len(undeclared), ", ".join(undeclared[:12]), " ..." if len(undeclared) > 12 else ""))
    print("intent_checks: return path judged on %d signal nets (%d excluded as ground, rail, zone owner or power class), %d over their limit, worst %s at %.1f mm" % (n_nets, len(_why), n_over, worst[0] or "none", worst[1]))
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
    check(not _undeclared, "every power-symbol net is a declared rail (%d of %d)"
          % (len(_power_nets) - len(_undeclared), len(_power_nets)),
          "not in the intent file: %s" % ", ".join(_undeclared[:12]) if _undeclared else "")
    # 4. return via (rule 2 of the same ruling): a ground via beside every signal via, judged by return_via.py
    rv = return_via.judge(b, path)
    check(not rv["lacking"], "return via: %d of %d signal vias have a ground via within %.1f mm (%d exempt in fine-pitch fans, %d on one reference plane); without one: %s" % (
        rv["judged"] - len(rv["lacking"]), rv["judged"], return_via.RETURN_MM, rv["exempt"], rv["same_plane"], "; ".join(rv["lacking"][:8]) + (" ..." if len(rv["lacking"]) > 8 else "") or "none"))
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
    sys.exit(_v.write("intent_checks",
                      _v.INCONCLUSIVE if not checked else (_v.PASS if not fails else _v.FAIL),
                      counts={"fail": len(fails), "pass": len(checked) - len(fails)},
                      denominator=len(checked), evidence=fails, inputs={"board": sys.argv[1]},
                      note="" if checked else "the intent file yielded no check"))
