#!/usr/bin/env python3
"""Gates that need a board: built here in code, one that must FAIL each rule and one that must PASS.

These skip where `pcbnew` is not importable (the runner), and run where KiCad is (the box, the VM). The point is that a gate
which quietly stopped refusing would show up here rather than in a board that got through (plan stage 8)."""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Skip
import hardset

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pcbnew():
    try:
        import pcbnew; return pcbnew
    except Exception as e:
        raise Skip("no pcbnew here (%s)" % type(e).__name__)


def _board(pcbnew, w=40.0, h=30.0):
    """An empty two-layer board with a rectangular outline on Edge.Cuts."""
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        s.SetWidth(pcbnew.FromMM(0.1)); b.Add(s)
    return b


def _pad_footprint(pcbnew, b, ref, x, y, size=1.0):
    """One SMD pad with a courtyard around it, on F.Cu."""
    fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    p = pcbnew.PAD(fp); p.SetNumber("1"); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(pcbnew.PAD_SHAPE_RECT); p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    p.SetPosition(fp.GetPosition())
    # LSET's list and LSEQ constructors segfault this build's SWIG wrapper; FrontMask is the one that works (KiCad 9.0.9).
    p.SetLayerSet(pcbnew.LSET.FrontMask())
    fp.Add(p); b.Add(fp); return fp


def _drc(pcbnew, b, tmp, name):
    """Save the board and run kicad-cli's DRC on it, returning the parsed report."""
    path = os.path.join(tmp, name + ".kicad_pcb"); b.Save(path)
    rep = os.path.join(tmp, name + "-drc.json")
    r = subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-error", "-o", rep, path],
                       capture_output=True, text=True)
    if not os.path.exists(rep): raise Skip("kicad-cli drc did not run (%s)" % (r.stderr or r.stdout)[:120])
    return hardset.load(rep)


def t_two_pads_too_close_are_a_hard_clearance_violation():
    """The gate must see a clearance violation between two different parts, and must not see one when they are apart."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="board-gate-test-")
    b = _board(pcbnew)
    n = b.GetNetInfo()
    for ref, x in (("U1", 10.0), ("U2", 10.05)):                       # 0.05 mm apart, pads 1 mm wide: overlapping
        _pad_footprint(pcbnew, b, ref, x, 10.0)
    d = _drc(pcbnew, b, tmp, "close")
    c = hardset.counts(d)
    assert c["hard"] > 0, "two pads on top of each other passed the hard set: %s" % c
    b2 = _board(pcbnew)
    for ref, x in (("U1", 10.0), ("U2", 20.0)):
        _pad_footprint(pcbnew, b2, ref, x, 10.0)
    c2 = hardset.counts(_drc(pcbnew, b2, tmp, "apart"))
    assert c2["hard"] == 0, "two pads 10 mm apart were called hard: %s" % c2


def t_a_zone_on_a_net_the_board_does_not_have_is_refused():
    """A pour on a net name that is not in the netlist gets a phantom net and shows only as isolated copper (appendix 32.33)."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="board-gate-test-")
    b = _board(pcbnew)
    _pad_footprint(pcbnew, b, "U1", 10.0, 10.0)
    z = pcbnew.ZONE(b); z.SetLayer(pcbnew.F_Cu)
    o = z.Outline()
    o.NewOutline()
    for (x, y) in ((2, 2), (38, 2), (38, 28), (2, 28)): o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    ni = b.GetNetInfo(); nc = pcbnew.NETINFO_ITEM(b, "/NOT_A_NET"); b.Add(nc); z.SetNet(nc)
    b.Add(z)
    path = os.path.join(tmp, "zone.kicad_pcb"); b.Save(path)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_zone_nets.py"), path], capture_output=True, text=True)
    assert r.returncode != 0, "a zone on a net with no pad was accepted:\n%s" % (r.stdout + r.stderr)


def t_a_zone_on_a_real_net_passes():
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="board-gate-test-")
    b = _board(pcbnew)
    fp = _pad_footprint(pcbnew, b, "U1", 10.0, 10.0)
    net = pcbnew.NETINFO_ITEM(b, "GND"); b.Add(net)
    fp.Pads()[0].SetNet(net)
    z = pcbnew.ZONE(b); z.SetLayer(pcbnew.F_Cu); z.SetNet(net)
    o = z.Outline(); o.NewOutline()
    for (x, y) in ((2, 2), (38, 2), (38, 28), (2, 28)): o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    b.Add(z)
    path = os.path.join(tmp, "zone-ok.kicad_pcb"); b.Save(path)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_zone_nets.py"), path], capture_output=True, text=True)
    assert r.returncode == 0, "a zone on a net with a pad was refused:\n%s" % (r.stdout + r.stderr)


# ---------------------------------------------------------------- the return-current rules (15 September 2026, appendix 32.198)

def _signal_board(pcbnew, tmp, name, plane=True, gnd_via=False, via=True):
    """A two-layer board with a signal track on F.Cu and a via, over a B.Cu ground pour or not, with a ground via beside it or not."""
    b = _board(pcbnew)
    sig = pcbnew.NETINFO_ITEM(b, "/SIG"); b.Add(sig); gnd = pcbnew.NETINFO_ITEM(b, "GND"); b.Add(gnd)
    f1 = _pad_footprint(pcbnew, b, "U1", 5.0, 15.0); f1.Pads()[0].SetNet(sig)
    f2 = _pad_footprint(pcbnew, b, "U2", 35.0, 15.0); f2.Pads()[0].SetNet(sig)
    f3 = _pad_footprint(pcbnew, b, "U3", 20.0, 25.0); f3.Pads()[0].SetNet(gnd)
    t = pcbnew.PCB_TRACK(b); t.SetStart(f1.Pads()[0].GetPosition()); t.SetEnd(f2.Pads()[0].GetPosition()); t.SetWidth(pcbnew.FromMM(0.25)); t.SetLayer(pcbnew.F_Cu); t.SetNet(sig); b.Add(t)
    if via:
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(20.0), pcbnew.FromMM(15.0))); v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6)); v.SetNet(sig); b.Add(v)
    if gnd_via:
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(21.0), pcbnew.FromMM(15.0))); v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6)); v.SetNet(gnd); b.Add(v)
    if plane:
        z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(gnd); o = z.Outline(); o.NewOutline()
        for (x, y) in ((1, 1), (39, 1), (39, 29), (1, 29)): o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
        b.Add(z); pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    path = os.path.join(tmp, name + ".kicad_pcb"); b.Save(path)
    os.makedirs(os.path.join(tmp, "out"), exist_ok=True)
    json.dump({"rails": {}, "bypass": [], "pair_classes": {"USB": None}}, open(os.path.join(tmp, "out", name + "-intent.json"), "w"))
    return pcbnew.LoadBoard(path), path


def t_a_signal_track_with_no_plane_under_it_fails_the_return_path_rule_and_passes_over_a_pour():
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="return-rule-")
    sys.path.insert(0, TOOLS); import intent_checks
    def judge(b, path):
        fails = []
        intent_checks.run(b, lambda ok, text: (None if ok else fails.append(text)), path)
        return [f for f in fails if f.startswith("return path")]
    b, p = _signal_board(pcbnew, tmp, "noplane", plane=False, gnd_via=True)
    f = judge(b, p); assert f and "SIG" in f[0], "30 mm of signal track with no plane under it must fail rule 1: %s" % f
    b, p = _signal_board(pcbnew, tmp, "plane", plane=True, gnd_via=True)
    f = judge(b, p); assert not f, "a signal track over a filled ground pour must pass rule 1: %s" % f


def t_a_signal_via_without_a_ground_via_beside_it_fails_the_return_via_rule_and_the_fixer_places_one():
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="return-rule-")
    sys.path.insert(0, TOOLS); import return_via
    b, p = _signal_board(pcbnew, tmp, "novia", plane=True, gnd_via=False)
    r = return_via.judge(b, p); assert r["judged"] == 1 and len(r["lacking"]) == 1, "one signal via with no ground via within 1.5 mm must be reported: %s" % r
    b, p = _signal_board(pcbnew, tmp, "withvia", plane=True, gnd_via=True)
    r = return_via.judge(b, p); assert r["judged"] == 1 and not r["lacking"], "a ground via 1.0 mm away satisfies the rule: %s" % r
    b, p = _signal_board(pcbnew, tmp, "fixme", plane=True, gnd_via=False)
    pro = os.path.splitext(p)[0] + ".kicad_pro"; json.dump({"board": {}, "net_settings": {"classes": [], "netclass_assignments": {}}}, open(pro, "w"))
    rc = subprocess.run([sys.executable, os.path.join(TOOLS, "return_via.py"), p], capture_output=True, text=True)
    if "kicad-cli" in (rc.stdout + rc.stderr) and "not found" in (rc.stdout + rc.stderr): raise Skip("no kicad-cli for the fixer's DRC")
    r = return_via.judge(pcbnew.LoadBoard(p), p)
    assert not r["lacking"], "the fixer must place a ground via beside the lone signal via:\n%s" % (rc.stdout + rc.stderr)[-800:]


def t_a_class_below_the_board_minimum_is_refused_and_a_class_at_it_passes():
    """Rule IMP-002. A class number below the board's own manufacturing minimum is a lie the router believes:
    the DSN carries the class, the router lays copper to it, and the DRC finds the violations afterwards. It
    cost A23 twenty-five clearance violations (appendix 32.79) and it was live on board B on 16 September,
    whose project file shipped USB and DIFF100 at 0.10 mm against a 0.127 mm board minimum."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="class-floor-test-")
    b = _board(pcbnew)
    ds = b.GetDesignSettings()
    ds.m_MinClearance = pcbnew.FromMM(0.127); ds.m_TrackMinWidth = pcbnew.FromMM(0.127)
    ds.m_ViasMinSize = pcbnew.FromMM(0.40); ds.m_MinThroughDrill = pcbnew.FromMM(0.20)
    path = os.path.join(tmp, "brd.kicad_pcb"); b.Save(path)

    def run(clearance):
        pro = os.path.join(tmp, "brd.kicad_pro")
        json.dump({"net_settings": {"classes": [
            {"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3},
            {"name": "DIFF100", "clearance": clearance, "track_width": 0.2, "via_diameter": 0.4, "via_drill": 0.2}]}},
            open(pro, "w"))
        return subprocess.run([sys.executable, os.path.join(TOOLS, "class_floor.py"), path],
                              cwd=tmp, capture_output=True, text=True)

    p = run(0.10)
    assert p.returncode == 1, "a class at 0.10 mm passed a board whose minimum is 0.127:\n%s" % (p.stdout + p.stderr)[-400:]
    v = json.load(open(os.path.join(tmp, "out", "class_floor.verdict.json")))
    assert v["counts"]["below_floor"] == 1, v
    p = run(0.127)
    assert p.returncode == 0, "a class AT the board minimum was refused:\n%s" % (p.stdout + p.stderr)[-400:]


def t_a_board_with_no_project_file_is_inconclusive_and_never_a_pass():
    """The classes live in the project file and the router reads them there. A board without one has no class
    to judge, which is the absence case: INCONCLUSIVE, never a silent pass."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="class-floor-none-")
    b = _board(pcbnew); path = os.path.join(tmp, "lonely.kicad_pcb"); b.Save(path)
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "class_floor.py"), path],
                       cwd=tmp, capture_output=True, text=True)
    assert p.returncode == 3, "a board with no project file did not come out INCONCLUSIVE:\n%s" % (p.stdout + p.stderr)[-300:]


def t_every_check_call_in_the_rules_passes_one_message():
    """A check that RAISES where it decides leaves no verdict at all, which is worse than deciding wrongly.

    16 September 2026: board E's re-finish printed "return path judged on 75 signal nets, 0 over their limit",
    the best reading that board has ever had, and then died with `check() takes 2 positional arguments but 3
    were given` on the very next line. The gate wrote no verdict, the finish read INCONCLUSIVE, and the good
    result existed only in a log. The board gates' check() takes a message and nothing else; a detail belongs
    inside that string.
    """
    import ast as _ast
    src = open(os.path.join(TOOLS, "intent_checks.py")).read()
    tree = _ast.parse(src)
    bad = []
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name) and n.func.id == "check":
            if len(n.args) != 2 or n.keywords:
                bad.append("line %d: check() called with %d argument(s)" % (n.lineno, len(n.args)))
    assert not bad, ("the board gates' check() takes (ok, message) and nothing else: " + "; ".join(bad))


def _via(pcbnew, b, x, y, dia, drill, net=None):
    """One through via at (x, y) with an explicit diameter and drill, both in mm."""
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    v.SetWidth(pcbnew.FromMM(dia)); v.SetDrill(pcbnew.FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    b.Add(v); return v


def _tht_footprint(pcbnew, b, ref, x, y, pad=1.6, drill=0.9, plated=True):
    """One through-hole pad: a plated component hole unless plated is False, when it is a mounting hole."""
    fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    p = pcbnew.PAD(fp); p.SetNumber("1")
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH if plated else pcbnew.PAD_ATTRIB_NPTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(pad), pcbnew.FromMM(pad)))
    p.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(drill), pcbnew.FromMM(drill)))
    p.SetPosition(fp.GetPosition())
    fp.Add(p); b.Add(fp); return fp


def t_a_via_is_judged_by_the_via_rows_and_a_component_hole_by_the_annular_row():
    """The fabricator states two floors and they are not interchangeable (rule VIA-002, 16 September 2026).

    Board D12 routed 0 hard and 0 unrouted on 16 September and was refused for ONE via, a 0.45/0.20 through via
    with 0.125 mm of copper per side, against the 0.20 mm PTH ANNULAR RING row. That row cannot be about vias:
    the same document's smallest via is 0.25 mm of copper on a 0.15 mm hole, which is 0.05 mm per side, so a
    floor of 0.20 would refuse the fabricator's own minimum via. This fixture holds the split in place from
    both sides: the via that was refused must pass, and a plated component hole genuinely under the annular
    row must still fail."""
    pcbnew = _pcbnew()
    import importlib
    va = importlib.import_module("via_audit")

    b = _board(pcbnew)
    _via(pcbnew, b, 10.0, 10.0, 0.45, 0.20)          # D12's via: 0.125 mm of ring
    _tht_footprint(pcbnew, b, "J1", 20.0, 10.0, pad=1.60, drill=0.90)   # 0.35 mm of ring, a fine component hole
    _tht_footprint(pcbnew, b, "H1", 30.0, 10.0, pad=3.20, drill=3.20, plated=False)  # a mounting hole, no ring
    tmp = tempfile.mkdtemp(prefix="via-ring-test-")
    good = os.path.join(tmp, "good.kicad_pcb"); b.Save(good)
    r = va.audit(good, annular_min=0.20, via_ring_min=0.05)
    assert r["vias"] == 1 and r["plated_holes"] == 1 and r["npth_holes"] == 1, r
    assert not r["bad"], "the fabricator's own via minimum must not be refused: %s" % r["bad"]
    assert not r["thin_pads"], r["thin_pads"]

    # the same via against the component-hole row, which is the defect this split removes
    r2 = va.audit(good, annular_min=0.20, via_ring_min=0.20)
    assert r2["bad"], "with the component row applied to the via the refusal is the D12 one, and it is wrong"

    b2 = _board(pcbnew)
    _tht_footprint(pcbnew, b2, "J2", 20.0, 10.0, pad=1.00, drill=0.90)  # 0.05 mm of ring on a component hole
    thin = os.path.join(tmp, "thin.kicad_pcb"); b2.Save(thin)
    r3 = va.audit(thin, annular_min=0.20, via_ring_min=0.05)
    assert r3["thin_pads"], "a plated component hole at 0.05 mm of ring must still be refused"
