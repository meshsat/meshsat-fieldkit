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


def _rules(board_path, clearance=0.127, track=0.127, via=0.40, drill=0.20):
    """The board's own manufacturing minimums, written where KiCad keeps them.

    They live in the PROJECT file under board.design_settings.rules, and nothing that is written through the
    SWIG design settings survives a save: KiCad 9 keeps none of them in the .kicad_pcb. A fixture that set them
    that way handed every gate KiCad's defaults (0.5 mm vias, 0.3 mm drills, no clearance floor at all) and
    then asserted about the board's own, which is why the via rule read the fabricator's smallest via as below
    a minimum this project never declared (17 September 2026)."""
    import json as _j
    pro = os.path.splitext(board_path)[0] + ".kicad_pro"
    d = {}
    if os.path.exists(pro):
        try: d = _j.load(open(pro))
        except ValueError: d = {}
    d.setdefault("board", {}).setdefault("design_settings", {})["rules"] = {
        "min_clearance": clearance, "min_track_width": track,
        "min_via_diameter": via, "min_through_hole_diameter": drill}
    _j.dump(d, open(pro, "w"))
    return pro


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

def _signal_board(pcbnew, tmp, name, plane=True, gnd_via=False, via=True, gnd_complete=False):
    """A two-layer board with a signal track on F.Cu and a via, over a B.Cu ground pour or not, with a ground via beside it or not."""
    b = _board(pcbnew)
    b.Add(pcbnew.NETINFO_ITEM(b, "/SIG")); b.Add(pcbnew.NETINFO_ITEM(b, "GND"))
    # A NET ADDED IN PYTHON HAS NO CODE UNTIL THE BOARD BUILDS ITS LIST, AND THE ITEM YOU ADDED IS NOT THE ONE
    # THE BOARD THEN HOLDS (17 September 2026). Both vias of this fixture came back on /SIG, so the rule under
    # test saw two signal vias and no ground via at all, and its own subject, a signal via WITH a ground via
    # beside it, had never once been built. Build the list, then take the nets by name from the board.
    b.BuildListOfNets()
    # AND THE OBJECT GOES STALE AGAIN EVERY TIME THE BOARD'S CONTENTS CHANGE. Adding a footprint rebuilds the
    # net list, so a NETINFO_ITEM fetched once and used later sets the WRONG net: the ground via came back on
    # /SIG whichever way it was fetched, until each use took the net by name at the moment it was used.
    def _net(name): return b.FindNet(name)
    _keep = [b.FindNet("/SIG"), b.FindNet("GND")]          # the proxies stay alive for the board's lifetime
    _code = {n: b.FindNet(n).GetNetCode() for n in ("/SIG", "GND")}
    globals()["LAST_FIXTURE_CODES"] = dict(_code, names=[x.GetNetname() for x in _keep],
                                           all=[b.GetNetInfo().GetNetItem(i).GetNetname()
                                                for i in range(b.GetNetInfo().GetNetCount())])
    def _set(item, name):
        """By CODE, not by the item. A NETINFO_ITEM handed to SetNet goes stale the moment the board's
        contents change, and SetNet then quietly leaves the object on another net: both vias of this fixture
        came back on /SIG whichever way the item was fetched. The code is stable."""
        item.SetNetCode(_code[name]); return item
    assert _net("/SIG") is not None and _net("GND") is not None, "the fixture's own nets are not on its board"
    f1 = _pad_footprint(pcbnew, b, "U1", 5.0, 15.0); _set(f1.Pads()[0], "/SIG")
    f2 = _pad_footprint(pcbnew, b, "U2", 35.0, 15.0); _set(f2.Pads()[0], "/SIG")
    f3 = _pad_footprint(pcbnew, b, "U3", 20.0, 25.0); _set(f3.Pads()[0], "GND")
    t = pcbnew.PCB_TRACK(b); t.SetStart(f1.Pads()[0].GetPosition()); t.SetEnd(f2.Pads()[0].GetPosition()); t.SetWidth(pcbnew.FromMM(0.25)); t.SetLayer(pcbnew.F_Cu); _set(t, "/SIG"); b.Add(t)
    if via:
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(20.0), pcbnew.FromMM(15.0))); v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6)); _set(v, "/SIG"); b.Add(v)
    if gnd_via:
        # OFF THE SIGNAL TRACK. At (21, 15) this via sat ON the run from U1 to U2, which crosses the whole
        # board at y 15, so KiCad's connectivity put it on the track's net and the fixture built two SIGNAL
        # vias and no ground via: the rule's own subject, a signal via WITH a return via beside it, had never
        # been built (17 September 2026). It is 1.0 mm away, across the track rather than along it.
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(20.0), pcbnew.FromMM(16.0))); v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6)); _set(v, "GND"); b.Add(v)
    if gnd_complete:
        # THE GROUND IS COMPLETE: a via in U3's own pad joins the F.Cu pad to the B.Cu pour, so the ratsnest of
        # GND reads zero before the fixer runs and a ground via it lays inside the pour changes nothing it
        # measures (18 September 2026: on the fixture without this via, GND was one F.Cu pad and a pour, the
        # fixer's via changed the unconnected count and it reverted its own work, which was the fixture's
        # shape and not the tool's; that was the declared debt).
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(20.0), pcbnew.FromMM(25.0))); v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6)); _set(v, "GND"); b.Add(v)
    if plane:
        z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); _set(z, "GND"); o = z.Outline(); o.NewOutline()
        for (x, y) in ((1, 1), (39, 1), (39, 29), (1, 29)): o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
        b.Add(z)
    path = os.path.join(tmp, name + ".kicad_pcb"); b.Save(path)
    if plane:
        # A ZONE IS FILLED ON A LOADED BOARD, NEVER ON ONE BUILT IN PYTHON (17 September 2026). KiCad 9.0.9's
        # ZONE_FILLER segfaults on a BOARD constructed here, outline and all, and fills a saved-then-loaded
        # copy of the same board without complaint. Every fixture in this family filled the constructed one,
        # so the whole board-fixture family took the interpreter down at the first fill: on the runner they
        # skip for want of pcbnew and nobody had run them where KiCad is. Save, load, fill, save.
        b = pcbnew.LoadBoard(path); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(path)
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
    r = return_via.judge(b, p)
    seen = [(t.GetNetname(), round(t.GetPosition().x / 1e6, 2)) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    assert r["judged"] == 1 and not r["lacking"], \
        "a ground via 1.0 mm away satisfies the rule: %s; the vias on the board are %s; the fixture's nets are %s" \
        % (r, seen, globals().get("LAST_FIXTURE_CODES"))


def t_the_return_via_fixer_lays_a_ground_via_beside_a_lacking_signal_via_and_keeps_it():
    """THE FIXER'S OWN PROOF (its debt since 17 September, paid 18 September 2026). The judge above says one signal
    via lacks a ground via; the fixer runs on the saved board with its project file beside it (drc.sh refuses a board
    without one), lays a locked GND via inside the pour within 1.5 mm, measures hard and unrouted before and after
    through the finish's own instruments, and KEEPS it because the ground was complete and nothing got worse."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="return-fix-")
    sys.path.insert(0, TOOLS); import return_via
    b, p = _signal_board(pcbnew, tmp, "fixme", plane=True, gnd_via=False, gnd_complete=True)
    _rules(p)
    r0 = return_via.judge(b, p); assert len(r0["lacking"]) == 1, "the fixture does not start with one lacking via: %s" % r0
    rc = return_via.fix(p)
    assert rc == 0, "the fixer reverted or refused on a board whose ground is complete (rc %s)" % rc
    b2 = pcbnew.LoadBoard(p); r1 = return_via.judge(b2, p)
    assert not r1["lacking"], "after the fixer a signal via still lacks a ground via: %s" % r1
    gv = [(round(t.GetPosition().x / 1e6, 2), round(t.GetPosition().y / 1e6, 2)) for t in b2.GetTracks()
          if t.GetClass() == "PCB_VIA" and t.GetNetname() == "GND" and t.IsLocked()]
    near = [v for v in gv if ((v[0] - 20.0) ** 2 + (v[1] - 15.0) ** 2) ** 0.5 <= 1.5 + 1e-6]
    assert near, "no locked GND via within 1.5 mm of the signal via at (20, 15); the locked GND vias are %s" % gv


def t_the_return_via_fixer_reverts_when_its_via_would_change_what_the_board_reads():
    """THE DEFECTIVE CASE the fixer must refuse: the same board with the ground INCOMPLETE (U3's pad alone on F.Cu,
    the pour on B.Cu, no via between them). A ground via laid in the pour changes the unconnected count the finish
    reads, the fixer calls that HURT and puts the board back as it was; a fixer that kept it would be reporting a
    board that does not exist (the 12 September lesson about a trial board at the unconnected cap)."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="return-fix-")
    sys.path.insert(0, TOOLS); import return_via
    b, p = _signal_board(pcbnew, tmp, "hurt", plane=True, gnd_via=False, gnd_complete=False)
    _rules(p)
    before = open(p, "rb").read()
    rc = return_via.fix(p)
    after = open(p, "rb").read()
    assert rc == 1, "the fixer kept a via that changed the board's unconnected count (rc %s)" % rc
    assert before == after, "the fixer said it reverted and left the board changed"


# THE FIXER'S PROOF ABOVE REPLACES THE DEBT DECLARED HERE ON 17 September 2026. Its judge is proved above, both
# ways, on a real board file. The FIXER needs a board whose ground is complete enough for the ratsnest to
# behave as a real one does: on this fixture GND is a single F.Cu pad and a B.Cu pour, so placing the ground
# via the rule asks for CHANGES the unconnected count, the fixer sees its own work as harm and reverts it. That
# is the fixture's shape, not the tool's: on the boards it runs on, the same guard has kept every via it laid.
# The debt is written in tests/test_gate_fixtures.py FIXTURE_DEBT with what it needs.


def t_a_class_below_the_board_minimum_is_refused_and_a_class_at_it_passes():
    """Rule IMP-002. A class number below the board's own manufacturing minimum is a lie the router believes:
    the DSN carries the class, the router lays copper to it, and the DRC finds the violations afterwards. It
    cost A23 twenty-five clearance violations (appendix 32.79) and it was live on board B on 16 September,
    whose project file shipped USB and DIFF100 at 0.10 mm against a 0.127 mm board minimum."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="class-floor-test-")
    b = _board(pcbnew)
    path = os.path.join(tmp, "brd.kicad_pcb"); b.Save(path)
    # THE BOARD'S MINIMUMS LIVE IN THE PROJECT FILE, under board.design_settings.rules, and that is where
    # KiCad reads them from when it loads the board (17 September 2026). Written through the SWIG design
    # settings and saved, they do not survive: KiCad 9 keeps none of them in the .kicad_pcb. This fixture set
    # them that way, so every run judged the classes against KiCad's defaults, the clearance case it exists to
    # prove never fired at all, and the via defaults of 0.5 and 0.3 failed the class that was meant to pass.
    # The real boards were never affected: their generators write the rules into the project file, which is
    # why board B reads a 0.127 mm floor. A fixture that does not build the condition proves nothing.

    def run(clearance):
        pro = os.path.join(tmp, "brd.kicad_pro")
        json.dump({"board": {"design_settings": {"rules": {
                        "min_clearance": 0.127, "min_track_width": 0.127,
                        "min_via_diameter": 0.40, "min_through_hole_diameter": 0.20}}},
                   "net_settings": {"classes": [
            {"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3},
            {"name": "DIFF100", "clearance": clearance, "track_width": 0.2, "via_diameter": 0.4, "via_drill": 0.2}]}},
            open(pro, "w"))
        return subprocess.run([sys.executable, os.path.join(TOOLS, "class_floor.py"), path],
                              cwd=tmp, capture_output=True, text=True)

    p = run(0.10)
    assert p.returncode == 1, "a class at 0.10 mm passed a board whose minimum is 0.127:\n%s" % (p.stdout + p.stderr)[-400:]
    v = json.load(open(os.path.join(tmp, "out", "class_floor.verdict.json")))
    assert v["counts"]["below_floor"] == 1, v
    assert "clearance" in v["evidence"][0], ("the failure must be the CLEARANCE this fixture lowered, not a "
                                             "via default: %s" % v["evidence"])
    p = run(0.127)
    assert p.returncode == 0, "a class AT the board minimum was refused:\n%s" % (p.stdout + p.stderr)[-400:]


def t_a_board_with_no_project_file_is_inconclusive_and_never_a_pass():
    """The classes live in the project file and the router reads them there. A board without one has no class
    to judge, which is the absence case: INCONCLUSIVE, never a silent pass."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="class-floor-none-")
    b = _board(pcbnew); path = os.path.join(tmp, "lonely.kicad_pcb"); b.Save(path)
    # SAVING A BOARD WRITES A PROJECT FILE BESIDE IT (KiCad 9), so a board with none cannot be staged by
    # saving one: this fixture had been handing the tool a board WITH a project file and asserting the
    # answer for a board without, and what it proved was that an empty project file yields one class
    # (17 September 2026). The condition is built by deleting what Save wrote.
    for ext in (".kicad_pro", ".kicad_prl"):
        q = os.path.splitext(path)[0] + ext
        if os.path.exists(q): os.remove(q)
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
    good = os.path.join(tmp, "good.kicad_pcb"); b.Save(good); _rules(good, via=0.40, drill=0.20)
    r = va.audit(good, annular_min=0.20, via_ring_min=0.05)
    assert r["vias"] == 1 and r["plated_holes"] == 1 and r["npth_holes"] == 1, r
    # THE BOARD'S OWN MINIMUMS ARE ONLY IN EFFECT IN A SEPARATE PROCESS. KiCad's standalone python applies a
    # project file's design rules when the board is loaded by a fresh interpreter and not when it is loaded
    # in-process by a caller that has already imported pcbnew, so this half of the audit, which compares a via
    # with the board's own minimum diameter and drill, is exercised through the tool's own command line. The
    # ring half above is pure arithmetic on the board and is judged here directly (17 September 2026).
    rc = subprocess.run([sys.executable, os.path.join(TOOLS, "via_audit.py"), good],
                        cwd=tmp, capture_output=True, text=True)
    v = json.load(open(os.path.join(tmp, "out", "via_audit.verdict.json")))
    assert v["counts"]["below_floor"] == 0, \
        "the fabricator's own via minimum must not be refused: %s\n%s" % (v["evidence"], (rc.stdout + rc.stderr)[-300:])
    assert not r["thin_pads"], r["thin_pads"]

    # the same via against the component-hole row, which is the defect this split removes
    r2 = va.audit(good, annular_min=0.20, via_ring_min=0.20)
    assert r2["bad"], "with the component row applied to the via the refusal is the D12 one, and it is wrong"

    b2 = _board(pcbnew)
    _tht_footprint(pcbnew, b2, "J2", 20.0, 10.0, pad=1.00, drill=0.90)  # 0.05 mm of ring on a component hole
    thin = os.path.join(tmp, "thin.kicad_pcb"); b2.Save(thin); _rules(thin, via=0.40, drill=0.20)
    r3 = va.audit(thin, annular_min=0.20, via_ring_min=0.05)
    assert r3["thin_pads"], "a plated component hole at 0.05 mm of ring must still be refused"


def t_a_board_that_controls_no_impedance_and_says_so_is_a_declared_zero():
    """16 September 2026. Board E5 is a 43 by 26 mm contact interposer with no schematic, no routed track and
    no differential pair, and pcb_board_facts.yaml says so in as many words: `impedance_controlled: false`,
    `pair_classes: []`. Reading only the board FILE, impedance_check found no pair class and answered
    INCONCLUSIVE, which held rule STK-001 open on a board where the question cannot arise. A zero the project
    declares is an answer; a zero nobody declared is not.

    The letter has to come from the facts' own `project` field and not from the board table: when this was
    written E5 had no boards/e5.json at all, so `letter_for` answered '' for it and the one board this branch
    exists for fell straight through on the first attempt. It HAS a table since 17 September, declaring
    `chain: false` and the answers to the rules that ask a board a question, so the lookup would work either
    way now; the facts stay the source, because they are where a board's properties live and the table is where
    its declarations do."""
    import os, sys
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, tools)
    import rules_lib, boardtable
    facts = rules_lib.board_facts() or {}
    assert facts.get("e5", {}).get("impedance_controlled") is False, "board E5's facts no longer declare it"
    import json as _json
    _e5 = os.path.join(tools, "boards", "e5.json")
    if os.path.exists(_e5):
        assert _json.load(open(_e5, encoding="utf-8")).get("chain") is False, \
            "board E5's table no longer declares that it has no chain, and the tests that skip it read that key"
    stem = "pcb-e5-block"
    letter = next((k for k, v in facts.items() if (v or {}).get("project") == stem), "")
    assert letter == "e5", "the facts no longer resolve %s to a letter" % stem
    src = open(os.path.join(tools, "impedance_check.py"), encoding="utf-8").read()
    assert 'get("project") == _stem' in src, "impedance_check resolves the letter some other way again"
    assert 'impedance_controlled") is False' in src, "the declared zero is not read from the facts"


def t_a_hole_a_net_punches_in_its_own_reference_is_not_a_break_in_it():
    """Rule RET-002 against RET-003, 17 September 2026. The fill retreats around every barrel, so a net that
    changes layer punches a hole in the very plane it is being judged against, and this measurement counted
    that hole as a break in the reference. It is not one: the reference is continuous either side of it, and
    what the signal needs there is a return transition, which is what RET-003 and RET-004 ask about. Board E's
    only failing net was over its limit by 0.2 mm and every uncovered run was its own via's anti-pad.

    The guard that keeps this from becoming an exemption is that an anti-pad is a hole IN a fill: where there
    is no pour at all, a point near a via is not an anti-pad, it is a net with no reference. Both cases are
    built here, on the same board with one variable."""
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="antipad-")
    sys.path.insert(0, TOOLS); import intent_checks

    def measure(b, path):
        fails = []
        intent_checks.run(b, lambda ok, text: (None if ok else fails.append(text)), path)
        return [f for f in fails if f.startswith("return path")], intent_checks.LAST.get("antipad_mm", 0.0)

    b, p = _signal_board(pcbnew, tmp, "withplane", plane=True, gnd_via=True)
    f, anti = measure(b, p)
    assert not f, "a signal track over a filled pour must still pass: %s" % f
    assert anti > 0.05, ("the hole the signal's own via makes in the pour is not being measured as an "
                         "anti-pad (%.2f mm)" % anti)

    b, p = _signal_board(pcbnew, tmp, "noplaneatall", plane=False, gnd_via=True)
    f, anti = measure(b, p)
    assert f and "SIG" in f[0], "30 mm of track with no reference under it must still fail: %s" % f
    assert anti == 0.0, ("with no pour on the board, a point near a via was called an anti-pad: there is no "
                         "fill for it to be a hole in (%.2f mm)" % anti)


def _island_board(pcbnew, tmp, name, stitch):
    """A board with TWO pours of one net: one with a plated pad of that net inside it and one with nothing.

    The second is the class `pour_stitch` repairs after every route, a filled island that reaches no via and no
    plated pad of its own net, and it is built here without a router because a pour can be born that way.
    """
    b = _board(pcbnew, 60.0, 30.0)
    def _set(x, net):
        ni = b.FindNet(net)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(b, net); b.Add(ni)
        x.SetNet(ni)
    for i, (x0, x1) in enumerate(((2.0, 25.0), (35.0, 58.0))):
        z = pcbnew.ZONE(b); z.SetLayer(pcbnew.F_Cu); _set(z, "GND"); o = z.Outline(); o.NewOutline()
        for (x, y) in ((x0, 2.0), (x1, 2.0), (x1, 28.0), (x0, 28.0)): o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
        z.SetZoneName("pour%d" % i); b.Add(z)
    path = os.path.join(tmp, name + ".kicad_pcb"); b.Save(path)
    b = pcbnew.LoadBoard(path)
    if stitch:                                   # a via of the pour's own net, inside the FIRST pour only
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10.0), pcbnew.FromMM(15.0)))
        v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6))
        ni = b.FindNet("GND")
        if ni is not None: v.SetNet(ni)
        b.Add(v)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(path)
    return path


def t_a_pour_born_with_no_via_of_its_own_net_is_predicted_before_the_route():
    """RULE PLC-002's LAST CLAUSE (17 September 2026). `pour_stitch` repairs a filled island with no via of its
    own net on every board and every round, and the closer register recorded that nothing predicted that class
    before a route was bought. Half of it is predictable on a placed board and half is not: an island the
    ROUTER cuts out of a pour does not exist yet, and `place_audit` says so rather than implying it is clean.

    Two worlds: two pours of one net, one with a via of that net inside it and one with nothing. The bare pour
    must be named with its area and its layer, and the stitched one must not.
    """
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="pour-island-")
    bare = _island_board(pcbnew, tmp, "bare", stitch=True)     # pour0 stitched, pour1 bare
    out = subprocess.run([sys.executable, os.path.join(TOOLS, "place_audit.py"), bare],
                         capture_output=True, text=True, timeout=600,
                         env=dict(os.environ, VERDICT_DIR=tmp)).stdout
    assert "pour island(s) already carry no via" in out, \
        "a pour with no via of its own net was not predicted:\n%s" % out[-900:]
    assert "GND on F.Cu" in out, "the island is named without its net and layer:\n%s" % out[-900:]

    both = _island_board(pcbnew, tmp, "both", stitch=False)    # neither stitched: two islands, not one
    out2 = subprocess.run([sys.executable, os.path.join(TOOLS, "place_audit.py"), both],
                          capture_output=True, text=True, timeout=600,
                          env=dict(os.environ, VERDICT_DIR=tmp)).stdout
    n1 = [l for l in out.splitlines() if "pour island(s) already carry no via" in l]
    n2 = [l for l in out2.splitlines() if "pour island(s) already carry no via" in l]
    assert n1 and n2 and int(n1[0].split("WARN  ")[1].split(" ")[0]) < int(n2[0].split("WARN  ")[1].split(" ")[0]), \
        "the via inside the first pour changed nothing, so the prediction is not reading the vias:\n%s\n%s" % (n1, n2)


_SITE_FIXTURE = r"""
import os, sys, tempfile
sys.path.insert(0, TOOLS)
import pcbnew, return_via

def board(w=40.0, h=30.0):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        sh.SetWidth(pcbnew.FromMM(0.1)); b.Add(sh)
    return b

def aperture(fp, x, y, size=0.6):
    # What KiCad draws over an exposed pad: unnumbered, on F.Paste alone, no net, no copper.
    p = pcbnew.PAD(fp); p.SetNumber(""); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(pcbnew.PAD_SHAPE_RECT)
    p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    ls = pcbnew.LSET.FrontMask(); ls.ClearCopperLayers(); p.SetLayerSet(ls)   # LSET(layer) is not offered here
    assert not p.IsOnCopperLayer(), "the aperture ended up on copper, which is not what KiCad draws"
    fp.Add(p); return p

def smd(b, ref, x, y, number, size, net, code):
    # NEVER REBUILD THE NET LIST HERE: a rebuild prunes a net that has no item on it yet, so the second
    # pad's own net vanished the moment it was asked for and the pad came back on ''. The codes are taken
    # once, after the nets are added, and a pad takes its code directly.
    fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    p = pcbnew.PAD(fp); p.SetNumber(number); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(pcbnew.PAD_SHAPE_RECT)
    p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(size[0]), pcbnew.FromMM(size[1])))
    p.SetPosition(fp.GetPosition()); p.SetLayerSet(pcbnew.LSET.FrontMask())
    fp.Add(p); b.Add(fp); p.SetNetCode(code)
    assert p.GetNetname() == net, "%s.%s is on %r, not on %s" % (ref, number, p.GetNetname(), net)
    return fp, p

tmp = tempfile.mkdtemp(prefix="site-free-")

def build(name, neighbour):
    # EACH FIXTURE IS ITS OWN BOARD. Saving a board prunes the nets nothing sits on and rebuilds the list, so
    # a second pad added to the same board afterwards came back on '' whatever code it was given.
    b = board()
    b.Add(pcbnew.NETINFO_ITEM(b, "GND")); b.Add(pcbnew.NETINFO_ITEM(b, "/OTHER")); b.BuildListOfNets()
    keep = [b.FindNet("GND"), b.FindNet("/OTHER")]             # the proxies stay alive for the board's lifetime
    code = {n: b.FindNet(n).GetNetCode() for n in ("GND", "/OTHER")}
    fp, ep = smd(b, "U1", 20.0, 15.0, "9", (2.29, 3.00), "GND", code["GND"])
    # THE NEIGHBOUR GOES ON BEFORE THE APERTURES. Adding a pad rebuilds the net list, which drops a net that
    # still has no item on it, so the nine unnumbered apertures took /OTHER off the board and the blocking
    # pad then came back on '' with a code that named nothing.
    if neighbour: smd(b, "U2", 20.0 + 0.11 + 0.5 / 2, 15.0, "1", (0.5, 0.5), "/OTHER", code["/OTHER"])
    for dx in (-0.7, 0.0, 0.7):
        for dy in (-1.0, 0.0, 1.0): aperture(fp, 20.0 + dx, 15.0 + dy)
    assert len([p for p in fp.Pads() if p.GetNumber() == ""]) == 9, "the fixture did not get its apertures"
    path = os.path.join(tmp, name + ".kicad_pcb"); b.Save(path)
    return path

# ONE BOARD PER PROCESS. A second BOARD built in the same interpreter after the first was saved came back
# with its pads on no net at all, whatever code they were given, so each fixture gets its own run.
#   argv[1] "plain"     = THE DEFECTIVE FIXTURE: a 2.29 x 3.00 mm ground pad under nine paste apertures,
#                         where the answer must be that a via fits.
#   argv[1] "neighbour" = THE ACCEPTABLE FIXTURE: the same pad with a real copper pad of another net at the
#                         same distance, where the answer must still be no.
WANT = sys.argv[1]
path = build(WANT, WANT == "neighbour")
print("ANSWER", return_via._site_free(pcbnew.LoadBoard(path), 20.0, 15.0, 0.45, 0.127, "GND"))
"""


def t_a_via_site_inside_an_exposed_pad_is_free_and_one_under_another_nets_copper_is_not():
    """PLC-001, RET-004 and PLC-002 all ask `return_via._site_free` whether a via fits somewhere, and it
    took every pad of every footprint as an obstacle unless the pad carried its own net. A solder paste
    aperture carries no net and sits inside the pad it belongs to, so every exposed pad on every board
    read as fully blocked: board A's three TPS2596 eFuses read `no via site` for their own thermal pads
    over a ground plane that is directly underneath them (17 September 2026, and the same lesson as
    appendix 32.151 in a second tool).

    The defective fixture is that pad, where the answer must be that a via fits. The acceptable fixture is
    what the filter must not free: a real copper pad of ANOTHER net at the same distance, where the answer
    must still be no. IT RUNS IN ITS OWN PROCESS, because a board built in python and left in python took
    the two DRC fixtures of this same file down with it: they read empty reports after it ran."""
    pcbnew = _pcbnew()
    src = "TOOLS = %r\n" % TOOLS + _SITE_FIXTURE
    def _answer(which):
        r = subprocess.run([sys.executable, "-c", src, which], capture_output=True, text=True)
        assert r.returncode == 0, "the %s fixture did not build:\n%s" % (which, (r.stdout + r.stderr)[-900:])
        line = [l for l in r.stdout.split("\n") if l.startswith("ANSWER ")]
        assert line, "the %s fixture printed no answer:\n%s" % (which, r.stdout[-400:])
        return line[0].split()[1]
    assert _answer("plain") == "True", \
        "a via does not fit in the middle of its own 2.29 x 3.00 mm ground pad: the paste apertures block it"
    assert _answer("neighbour") == "False", \
        "a real copper pad of another net 0.11 mm away no longer blocks the site: the filter freed copper"


# ---------------------------------------------------------------- place_audit's plane-pad class (its declared fixture debt, 18 September 2026)

_PLACE_FIXTURE = r"""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, TOOLS)
import pcbnew

def board(w=40.0, h=30.0):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))); sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        sh.SetWidth(pcbnew.FromMM(0.1)); b.Add(sh)
    return b

def pad(fp, num, x, y, w, h):
    p = pcbnew.PAD(fp); p.SetNumber(num); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_RECT)
    p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(w), pcbnew.FromMM(h))); p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    p.SetLayerSet(pcbnew.LSET.FrontMask()); fp.Add(p); return p

KEEPOUT = sys.argv[1] == "keepout"
ROUTED = sys.argv[1] == "routed"
b = board()
for n in ("GND", "/SIG"): b.Add(pcbnew.NETINFO_ITEM(b, n))
b.BuildListOfNets(); keep = [b.FindNet("GND"), b.FindNet("/SIG")]; code = {n: b.FindNet(n).GetNetCode() for n in ("GND", "/SIG")}
# a fine-pitch part: ten pads on a 0.5 mm pitch, so the gate is judged rather than INCONCLUSIVE
fp = pcbnew.FOOTPRINT(b); fp.SetReference("U1"); fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10.0), pcbnew.FromMM(10.0)))
pins = [pad(fp, str(i + 1), 8.0 + 0.5 * i, 10.0, 0.25, 1.0) for i in range(10)]
b.Add(fp)
for i, p in enumerate(pins): p.SetNetCode(code["/SIG"])
# the plane pad: GND on F.Cu, its plane a GND pour on B.Cu, no via anywhere near it
fq = pcbnew.FOOTPRINT(b); fq.SetReference("U2"); fq.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(30.0), pcbnew.FromMM(20.0)))
pg = pad(fq, "1", 30.0, 20.0, 1.0, 1.0); b.Add(fq); pg.SetNetCode(code["GND"])
z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNetCode(code["GND"]); o = z.Outline(); o.NewOutline()
for x, y in ((1, 1), (39, 1), (39, 29), (1, 29)): o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
b.Add(z)
if KEEPOUT:
    k = pcbnew.ZONE(b); k.SetIsRuleArea(True); k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(False); k.SetLayer(pcbnew.F_Cu)
    ko = k.Outline(); ko.NewOutline()
    for x, y in ((27, 17), (33, 17), (33, 23), (27, 23)): ko.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    b.Add(k)
if ROUTED:
    # what a router leaves: hundreds of UNLOCKED segments (a placed board has none of these)
    for i in range(200):
        t = pcbnew.PCB_TRACK(b); t.SetLayer(pcbnew.B_Cu); t.SetWidth(pcbnew.FromMM(0.127)); t.SetNetCode(code["/SIG"])
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(2.0 + 0.15 * i), pcbnew.FromMM(2.0))); t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(2.0 + 0.15 * i), pcbnew.FromMM(4.0))); b.Add(t)
d = tempfile.mkdtemp(prefix="place-audit-"); path = os.path.join(d, "fixture.kicad_pcb"); b.Save(path); os.makedirs(os.path.join(d, "out"), exist_ok=True)
r = subprocess.run([sys.executable, os.path.join(TOOLS, "place_audit.py"), path], cwd=d, capture_output=True, text=True)
v = json.load(open(os.path.join(d, "out", "place_audit.verdict.json")))
print("ANSWER", v["verdict"], json.dumps(v.get("counts")))
print("LINES", [l for l in (r.stdout + r.stderr).split("\n") if "plane pad" in l][:1])
"""


def _place_audit(which):
    src = "TOOLS = %r\n" % TOOLS + _PLACE_FIXTURE
    r = subprocess.run([sys.executable, "-c", src, which], capture_output=True, text=True)
    assert r.returncode == 0, "the %s fixture did not build:\n%s" % (which, (r.stdout + r.stderr)[-900:])
    ans = [l for l in r.stdout.split("\n") if l.startswith("ANSWER ")]
    assert ans, "no answer:\n" + r.stdout[-400:]
    return ans[0].split()[1], r.stdout


def t_a_plane_pad_under_a_track_keepout_with_no_via_fails_the_placement_gate():
    """THE DEFECTIVE FIXTURE for place_audit's plane-pad class (its fixture debt since 11 September): a GND pad on
    F.Cu whose plane is a B.Cu pour, no via within reach, and a track keep-out over it on its own layer, so the
    pad has nowhere to go before the route. A fine-pitch part sits on the board so the gate is judged at all."""
    _pcbnew()
    verdict, out = _place_audit("keepout")
    assert verdict == "FAIL", "a plane pad with nowhere to go passed the placement gate: %s" % out[-300:]
    assert "under a track keep-out" in out, "the failure does not name the keep-out that stops the pad: %s" % out[-300:]


def t_the_same_plane_pad_with_free_via_sites_passes_the_placement_gate():
    """THE ACCEPTABLE FIXTURE: the same board without the keep-out; the site search finds room and the gate passes."""
    _pcbnew()
    verdict, out = _place_audit("free")
    assert verdict == "PASS", "a plane pad with free via sites failed the placement gate: %s" % out[-300:]


# ---------------------------------------------------------------- intent_checks' decoupling item (its declared fixture debt, 18 September 2026)

_INTENT_FIXTURE = r"""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, TOOLS)
import pcbnew

def board(w=40.0, h=30.0):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))); sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        sh.SetWidth(pcbnew.FromMM(0.1)); b.Add(sh)
    return b

def part(b, ref, x, y, nets, code, value=""):
    fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref); fp.SetValue(value); fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    pads = []
    for i, n in enumerate(nets):
        p = pcbnew.PAD(fp); p.SetNumber(str(i + 1)); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8))); p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x + 1.0 * i), pcbnew.FromMM(y)))
        p.SetLayerSet(pcbnew.LSET.FrontMask()); fp.Add(p); pads.append((p, n))
    b.Add(fp)
    for p, n in pads: p.SetNetCode(code[n])
    return fp

FAR = sys.argv[1] == "far"
b = board()
for n in ("+3V3", "GND"): b.Add(pcbnew.NETINFO_ITEM(b, n))
b.BuildListOfNets(); keep = [b.FindNet("+3V3"), b.FindNet("GND")]; code = {n: b.FindNet(n).GetNetCode() for n in ("+3V3", "GND")}
part(b, "U1", 10.0, 10.0, ["+3V3", "GND"], code, "the part")
part(b, "C1", 20.0 if FAR else 11.5, 10.0, ["+3V3", "GND"], code, "100n")
d = tempfile.mkdtemp(prefix="intent-fixture-"); os.makedirs(os.path.join(d, "out")); path = os.path.join(d, "fixture.kicad_pcb"); b.Save(path)
json.dump({"bypass": [{"cap": "C1", "part": "U1", "pin": "1", "net": "+3V3"}], "rails": {}, "nodes": {}, "pair_classes": {}},
          open(os.path.join(d, "out", "fixture-intent.json"), "w"))
r = subprocess.run([sys.executable, os.path.join(TOOLS, "intent_checks.py"), path], cwd=d, capture_output=True, text=True)
v = json.load(open(os.path.join(d, "out", "intent_decoupling.verdict.json")))
print("ANSWER", v["verdict"], json.dumps(v.get("counts")))
print("LINES", [l for l in (r.stdout + r.stderr).split("\n") if "bypass C1" in l][:1])
"""


def _intent(which):
    src = "TOOLS = %r\n" % TOOLS + _INTENT_FIXTURE
    r = subprocess.run([sys.executable, "-c", src, which], capture_output=True, text=True)
    assert r.returncode == 0, "the %s fixture did not build:\n%s" % (which, (r.stdout + r.stderr)[-900:])
    ans = [l for l in r.stdout.split("\n") if l.startswith("ANSWER ")]
    assert ans, "no answer:\n" + r.stdout[-400:]
    return ans[0].split()[1], r.stdout


def t_a_declared_decoupling_capacitor_ten_millimetres_from_its_pin_fails_the_loop_rule():
    """THE DEFECTIVE FIXTURE for intent_checks' decoupling item (its fixture debt since 11 September): C1 is declared
    as U1 pin 1's bypass and sits 10 mm away against the 3 mm loop of a 100 nF part."""
    _pcbnew()
    verdict, out = _intent("far")
    assert verdict == "FAIL", "a capacitor 10 mm from its pin passed the decoupling rule: %s" % out[-300:]
    assert "bypass C1" in out, "the failure does not name the capacitor: %s" % out[-300:]


def t_the_same_capacitor_within_three_millimetres_passes_the_loop_rule():
    """THE ACCEPTABLE FIXTURE: the same declaration with C1 1.5 mm from the pin."""
    _pcbnew()
    verdict, out = _intent("near")
    assert verdict == "PASS", "a capacitor 1.5 mm from its pin failed the decoupling rule: %s" % out[-300:]

_RAIL_FIXTURE = r"""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, TOOLS)
import pcbnew

def board(w=90.0, h=30.0):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))); sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        sh.SetWidth(pcbnew.FromMM(0.1)); b.Add(sh)
    return b

def part(b, ref, x, y, nets, code):
    # two pads 4 mm apart down the board, so a wide rail track past pad 1 never touches pad 2
    fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref); fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    pads = []
    for i, n in enumerate(nets):
        p = pcbnew.PAD(fp); p.SetNumber(str(i + 1)); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.5), pcbnew.FromMM(1.5))); p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y + 4.0 * i)))
        p.SetLayerSet(pcbnew.LSET.FrontMask()); fp.Add(p); pads.append((p, n))
    b.Add(fp)
    for p, n in pads: p.SetNetCode(code[n])
    return fp

WIDE = sys.argv[1] == "wide"
b = board()
for n in ("VRAIL", "GND"): b.Add(pcbnew.NETINFO_ITEM(b, n))
b.BuildListOfNets(); keep = [b.FindNet("VRAIL"), b.FindNet("GND")]; code = {n: b.FindNet(n).GetNetCode() for n in ("VRAIL", "GND")}
part(b, "J1", 7.5, 10.0, ["VRAIL", "GND"], code)     # the connector the rail enters on: the source
part(b, "U1", 82.5, 10.0, ["VRAIL", "GND"], code)    # the one load
# the rail's only copper: one 75 mm F.Cu track, 0.2 mm (0.11 ohm, 0.33 V at 3 A, 6.6 percent of 5 V) or 2.0 mm (0.66 percent)
t = pcbnew.PCB_TRACK(b); t.SetLayer(pcbnew.F_Cu); t.SetWidth(pcbnew.FromMM(2.0 if WIDE else 0.2))
t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(7.5), pcbnew.FromMM(10.0))); t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(82.5), pcbnew.FromMM(10.0)))
t.SetNetCode(code["VRAIL"]); b.Add(t)
d = tempfile.mkdtemp(prefix="rail-fixture-"); os.makedirs(os.path.join(d, "out")); path = os.path.join(d, "fixture.kicad_pcb"); b.Save(path)
json.dump({"bypass": [], "nodes": {}, "pair_classes": {},
           "rails": {"VRAIL": {"volts": 5.0, "amps_typ": 3.0, "amps_peak": 3.0, "source": "J1", "loads": {"U1": 3.0},
                               "note": "fixture rail", "budget": 0.02}}},
          open(os.path.join(d, "out", "fixture-intent.json"), "w"))
r = subprocess.run([sys.executable, os.path.join(TOOLS, "dc_drop.py"), path], cwd=d, capture_output=True, text=True)
v = json.load(open(os.path.join(d, "out", "dc_drop.verdict.json")))
print("ANSWER", v["verdict"], json.dumps(v.get("counts")))
print("LINES", [l for l in (r.stdout + r.stderr).split("\n") if "VRAIL" in l][:2])
"""


def _rail(which):
    src = "TOOLS = %r\n" % TOOLS + _RAIL_FIXTURE
    r = subprocess.run([sys.executable, "-c", src, which], capture_output=True, text=True)
    assert r.returncode == 0, "the %s fixture did not build:\n%s" % (which, (r.stdout + r.stderr)[-900:])
    ans = [l for l in r.stdout.split("\n") if l.startswith("ANSWER ")]
    assert ans, "no answer:\n" + r.stdout[-400:]
    return ans[0].split()[1], r.stdout


def t_a_rail_whose_only_copper_is_a_thin_track_drops_past_its_budget_and_fails():
    """THE DEFECTIVE FIXTURE for dc_drop (its fixture debt since 11 September, paid 17 September 2026): a 5 V rail
    declared at 3 A from connector J1 into U1 over 75 mm of 0.2 mm F.Cu, 0.11 ohm at 1 oz, which is 0.33 V and
    6.6 percent of the rail against a 2 percent budget. The rasteriser reads a track narrower than its cell as
    the FRACTION of the cell (line 138 of the tool), so the number is the track's and not the cell's."""
    _pcbnew()
    verdict, out = _rail("thin")
    assert verdict == "FAIL", "a 0.2 mm track carrying 3 A over 75 mm passed the drop rule: %s" % out[-400:]
    assert "VRAIL" in out, "the failure does not name the rail: %s" % out[-300:]


def t_the_same_rail_on_a_two_millimetre_track_is_inside_its_budget_and_passes():
    """THE ACCEPTABLE FIXTURE: the same declaration with the track at 2.0 mm (0.011 ohm, 0.66 percent), which is
    also inside IPC-2221's 10 K external current for 2 mm at 1 oz (about 3.9 A), so neither verdict has a
    reason to refuse it."""
    _pcbnew()
    verdict, out = _rail("wide")
    assert verdict == "PASS", "a 2.0 mm track carrying 3 A over 75 mm failed the drop rule: %s" % out[-400:]

_PRUNED_FIXTURE = r"""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, TOOLS)
import pcbnew

def board(w=40.0, h=30.0):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))); sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        sh.SetWidth(pcbnew.FromMM(0.1)); b.Add(sh)
    return b

REACHED = sys.argv[1] == "reached"
b = board()
for n in ("GND", "/SIG"): b.Add(pcbnew.NETINFO_ITEM(b, n))
b.BuildListOfNets(); keep = [b.FindNet("GND"), b.FindNet("/SIG")]; code = {n: b.FindNet(n).GetNetCode() for n in ("GND", "/SIG")}
fp = pcbnew.FOOTPRINT(b); fp.SetReference("U1"); fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10.0), pcbnew.FromMM(10.0)))
p = pcbnew.PAD(fp); p.SetNumber("7"); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_RECT)
p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.25), pcbnew.FromMM(1.0))); p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10.0), pcbnew.FromMM(10.0)))
p.SetLayerSet(pcbnew.LSET.FrontMask()); fp.Add(p); b.Add(fp); p.SetNetCode(code["/SIG"])
# the router's work: a /SIG track ending on the pad, or (the defective case) a track of the same net 3 mm away
t = pcbnew.PCB_TRACK(b); t.SetLayer(pcbnew.F_Cu); t.SetWidth(pcbnew.FromMM(0.127)); t.SetNetCode(code["/SIG"])
t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(20.0), pcbnew.FromMM(10.0)))
t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(10.0 if REACHED else 13.0), pcbnew.FromMM(10.0))); b.Add(t)
d = tempfile.mkdtemp(prefix="pruned-fixture-"); os.makedirs(os.path.join(d, "out")); path = os.path.join(d, "fixture.kicad_pcb"); b.Save(path)
lst = os.path.join(d, "out", "fixture-pruned.txt")
# the list in escape_prune's own SEVEN-column form (net, ref, pad, x, y, violation, what it collided with)
open(lst, "w").write("# net\tref\tpad\tx\ty\tviolation\twhat it collided with\n/SIG\tU1\t7\t10.000\t10.000\thole_clearance\tPad 1 [GND] of C1 on B.Cu\n")
r = subprocess.run([sys.executable, os.path.join(TOOLS, "pruned_gate.py"), path, lst], cwd=d, capture_output=True, text=True)
v = json.load(open(os.path.join(d, "out", "pruned_gate.verdict.json")))
print("ANSWER", v["verdict"], json.dumps(v.get("counts")))
print("LINES", [l for l in (r.stdout + r.stderr).split("\n") if "U1.7" in l or "Error" in l][:2])
"""


def _pruned(which):
    src = "TOOLS = %r\n" % TOOLS + _PRUNED_FIXTURE
    r = subprocess.run([sys.executable, "-c", src, which], capture_output=True, text=True)
    assert r.returncode == 0, "the %s fixture did not build:\n%s" % (which, (r.stdout + r.stderr)[-900:])
    ans = [l for l in r.stdout.split("\n") if l.startswith("ANSWER ")]
    assert ans, "no answer:\n" + r.stdout[-400:]
    return ans[0].split()[1], r.stdout


def t_a_pruned_pad_the_router_never_reached_fails_the_pruned_gate():
    """THE DEFECTIVE FIXTURE for pruned_gate (its fixture debt since 11 September, paid 18 September 2026): U1 pad 7
    is on the pruned list and the only /SIG copper ends 3 mm from it. The list is in escape_prune's own seven-column
    form, which is what found the gate unpacking five fields: it would have raised inside the first finish that
    reached it with a real list (B22's has seven rows)."""
    _pcbnew()
    verdict, out = _pruned("unreached")
    assert verdict == "FAIL", "a pruned pad with no track on it passed: %s" % out[-400:]
    assert "U1.7" in out, "the failure does not name the pad: %s" % out[-300:]


def t_a_pruned_pad_with_a_track_of_its_net_ending_on_it_passes_the_pruned_gate():
    """THE ACCEPTABLE FIXTURE: the same list, the /SIG track ends on the pad."""
    _pcbnew()
    verdict, out = _pruned("reached")
    assert verdict == "PASS", "a pruned pad the router reached failed: %s" % out[-400:]


def t_the_placement_predictor_declines_a_routed_board_and_names_the_input_it_wants():
    """THE WRONG ARTEFACT (18 September 2026): the plane-pad fixture with two hundred unlocked router segments on it
    is a routed board; the predictor reads INCONCLUSIVE with `missing_input` naming the placed snapshot, so it never
    replaces the placed board's own reading (sweep 26 wrote 19 collisions over B21's 10 that way)."""
    _pcbnew()
    verdict, out = _place_audit("routed")
    assert verdict == "INCONCLUSIVE", "the predictor judged a routed board: %s" % out[-400:]
    assert "unlocked_segments" in out, "the refusal does not count the router's own copper: %s" % out[-300:]

_VIA_PARALLEL_FIXTURE = r"""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, TOOLS)
import pcbnew

def board(w=70.0, h=30.0):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))); sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        sh.SetWidth(pcbnew.FromMM(0.1)); b.Add(sh)
    return b

def part(b, ref, x, y, nets, code):
    fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref); fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    pads = []
    for i, n in enumerate(nets):
        p = pcbnew.PAD(fp); p.SetNumber(str(i + 1)); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.5), pcbnew.FromMM(1.5))); p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y + 6.0 * i)))
        p.SetLayerSet(pcbnew.LSET.FrontMask()); fp.Add(p); pads.append((p, n))
    b.Add(fp)
    for p, n in pads: p.SetNetCode(code[n])
    return fp

def track(b, L, x1, y1, x2, y2, w, nc):
    t = pcbnew.PCB_TRACK(b); t.SetLayer(L); t.SetWidth(pcbnew.FromMM(w)); t.SetNetCode(nc)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))); t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))); b.Add(t)

def via(b, x, y, nc):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))); v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNetCode(nc); b.Add(v)

b = board()
for n in ("VRAIL", "GND"): b.Add(pcbnew.NETINFO_ITEM(b, n))
b.BuildListOfNets(); keep = [b.FindNet("VRAIL"), b.FindNet("GND")]; code = {n: b.FindNet(n).GetNetCode() for n in ("VRAIL", "GND")}
part(b, "J1", 7.5, 10.0, ["VRAIL", "GND"], code)
part(b, "U1", 62.5, 10.0, ["VRAIL", "GND"], code)
# the rail: 1 mm F.Cu from J1 to a single via at x 30, 1 mm B.Cu to a single via at x 45, 1 mm F.Cu on to U1:
# two layer transitions of ONE 0.3 mm barrel each under 2 A, against 0.90 A a barrel at 10 K
track(b, pcbnew.F_Cu, 7.5, 10.0, 30.0, 10.0, 1.0, code["VRAIL"]); via(b, 30.0, 10.0, code["VRAIL"])
track(b, pcbnew.B_Cu, 30.0, 10.0, 45.0, 10.0, 1.0, code["VRAIL"]); via(b, 45.0, 10.0, code["VRAIL"])
track(b, pcbnew.F_Cu, 45.0, 10.0, 62.5, 10.0, 1.0, code["VRAIL"])
d = tempfile.mkdtemp(prefix="via-parallel-"); os.makedirs(os.path.join(d, "out")); path = os.path.join(d, "fixture.kicad_pcb"); b.Save(path)
pro = os.path.join(d, "fixture.kicad_pro")
pd = json.load(open(pro)) if os.path.exists(pro) else {}
pd.setdefault("board", {}).setdefault("design_settings", {})["rules"] = {"min_clearance": 0.127, "min_track_width": 0.127, "min_via_diameter": 0.4, "min_through_hole_diameter": 0.2}
json.dump(pd, open(pro, "w"))
json.dump({"bypass": [], "nodes": {}, "pair_classes": {},
           "rails": {"VRAIL": {"volts": 5.0, "amps_typ": 2.0, "amps_peak": 2.0, "source": "J1", "loads": {"U1": 2.0}, "note": "fixture rail", "budget": 0.05}}},
          open(os.path.join(d, "out", "fixture-intent.json"), "w"))
subprocess.run([sys.executable, os.path.join(TOOLS, "dc_drop.py"), path], cwd=d, capture_output=True, text=True)
subprocess.run([sys.executable, os.path.join(TOOLS, "via_current.py"), path], cwd=d, capture_output=True, text=True)
before = json.load(open(os.path.join(d, "out", "via_current.verdict.json")))
r = subprocess.run([sys.executable, os.path.join(TOOLS, "via_parallel.py"), path], cwd=d, capture_output=True, text=True)
after = json.load(open(os.path.join(d, "out", "via_current.verdict.json")))
b2 = pcbnew.LoadBoard(path)
nv = sum(1 for t in b2.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() == "VRAIL")
print("ANSWER", before["verdict"], after["verdict"], nv, r.returncode)
print("LINES", [l for l in (r.stdout + r.stderr).split("\n") if l.startswith("via_parallel:")][:6])
"""


def t_a_barrel_over_its_rating_gets_parallel_barrels_and_the_judge_then_passes():
    """PI-003's fixer, proved on the shape that failed four boards (18 September 2026): a 2 A rail crossing two
    layer transitions of one 0.3 mm barrel each. Before: via_current FAIL (2.0 A against 0.90). After
    via_parallel: at least two more barrels at each transition, joined on both layers, the DRC clean, the mesh
    re-solved, and via_current PASS on the same board."""
    _pcbnew()
    src = "TOOLS = %r\n" % TOOLS + _VIA_PARALLEL_FIXTURE
    r = subprocess.run([sys.executable, "-c", src], capture_output=True, text=True)
    assert r.returncode == 0, "the fixture did not build:\n%s" % (r.stdout + r.stderr)[-1200:]
    ans = [l for l in r.stdout.split("\n") if l.startswith("ANSWER ")]
    assert ans, "no answer:\n" + r.stdout[-400:]
    before, after, nv, rc = ans[0].split()[1:5]
    assert before == "FAIL", "the fixture does not start with an over-current barrel: %s" % r.stdout[-600:]
    assert rc == "0", "via_parallel reverted or refused (rc %s): %s" % (rc, r.stdout[-800:])
    assert int(nv) >= 6, "fewer than six VRAIL vias after the fixer (two transitions, each wanting two more): %s" % r.stdout[-600:]
    assert after == "PASS", "the judge still fails after the parallel barrels: %s" % r.stdout[-800:]


# copper_checks: the pour-integrity library every board gate calls. Its fixture debt (declared 8 September 2026 as
# "exercised through the board gates") is paid here with the two boards the rule asks about: a ground pour with a via
# of its net in it, and the same pour with nothing of its net touching it, which is an island the fill should have
# removed and the check must refuse.
def _copper_fails(pcbnew, b):
    import copper_checks
    fails = []
    def check(ok, msg):
        if not ok: fails.append(msg)
    note = copper_checks.run(b, check)
    return fails, note


def t_a_power_pour_with_no_pad_or_via_of_its_net_is_a_loose_piece_and_fails():
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="copper-")
    b, p = _signal_board(pcbnew, tmp, "loose", plane=True, gnd_via=False, gnd_complete=False)
    fails, note = _copper_fails(pcbnew, b)
    assert any("loose" in f and "GND" in f for f in fails), (fails, note)


def t_the_same_pour_anchored_by_a_via_of_its_net_passes_the_copper_checks():
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="copper-")
    b, p = _signal_board(pcbnew, tmp, "anchored", plane=True, gnd_via=False, gnd_complete=True)
    fails, note = _copper_fails(pcbnew, b)
    assert not fails, (fails, note)


# ANA-001's subject: a declared sensitive node must be the node the controller's amplifier sees, behind its
# filter, and never a terminal of the switching loop. Board E declared the inductor's own pad and board A the
# five low-side FET source nodes (18 September 2026), so both boards read failures that were about the
# declaration rather than the copper. The fixtures are one board with a transistor pad on the declared net and
# the same board with the declaration moved behind the filter.
def _sense_board(pcbnew, tmp, name, declare):
    """A board with a 'switching' net SW1, a FET Q1 whose source pad is on CS, and a filtered node CSF."""
    b = _board(pcbnew)
    for nm in ("SW1", "CS", "CSF"): b.Add(pcbnew.NETINFO_ITEM(b, nm))
    b.BuildListOfNets()
    code = {n: b.FindNet(n).GetNetCode() for n in ("SW1", "CS", "CSF")}
    fq = _pad_footprint(pcbnew, b, "Q1", 10.0, 10.0); fq.Pads()[0].SetNetCode(code["CS"])
    fr = _pad_footprint(pcbnew, b, "R1", 14.0, 10.0); fr.Pads()[0].SetNetCode(code["CSF"])
    fs = _pad_footprint(pcbnew, b, "U1", 18.0, 10.0); fs.Pads()[0].SetNetCode(code["SW1"])
    path = os.path.join(tmp, name + ".kicad_pcb"); b.Save(path)
    sens = os.path.join(tmp, name + "-sensitive.yaml")
    json.dump({"boards": {"x": {"switch_nets": ["SW1"],
                                "nodes": [{"net": declare, "what": "the fixture's sense node",
                                           "filter": "100 R and 1 nF", "kelvin_with": None, "keep_mm": 0.5}]}}},
              open(sens, "w"))
    return path, sens


def t_a_sensitive_node_declared_on_a_transistor_pad_is_refused():
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="ana-")
    import sensitive_nodes
    path, sens = _sense_board(pcbnew, tmp, "raw", "CS")
    r = sensitive_nodes.judge(path, "x", sens)
    assert any("POWER TERMINAL" in f and "Q1" in f for f in r["fails"]), r["fails"]


def t_the_same_node_declared_behind_its_filter_passes():
    pcbnew = _pcbnew(); tmp = tempfile.mkdtemp(prefix="ana-")
    import sensitive_nodes
    path, sens = _sense_board(pcbnew, tmp, "filtered", "CSF")
    r = sensitive_nodes.judge(path, "x", sens)
    assert not any("POWER TERMINAL" in f for f in r["fails"]), r["fails"]


def _examine_fixture(tmp, cases):
    """A board directory carrying `ref_change`'s per-via reading, and the screen's own flagged list beside it."""
    import json as _j
    os.makedirs(os.path.join(tmp, "out"), exist_ok=True)
    path = os.path.join(tmp, "brd.kicad_pcb")
    if cases is not None:
        _j.dump({"board": "brd.kicad_pcb", "vias": cases},
                open(os.path.join(tmp, "out", "brd-ref-change.json"), "w", encoding="utf-8"))

    class _T:
        def __init__(self, n): self.n = n
        def GetNetname(self): return self.n
    r = {"lacking": ["SDA0 at (10.00, 10.00)", "PCIE1_CLK_P at (20.00, 20.00)", "HB2 at (30.00, 30.00)"],
         "positions": [(_T("/SDA0"), (10.0, 10.0)), (_T("/PCIE1_CLK_P"), (20.0, 20.0)), (_T("/HB2"), (30.0, 30.0))]}
    return path, r


def t_a_flagged_via_whose_reference_never_changes_is_examined_and_not_failed():
    """THE DEFECTIVE CASE (18 September 2026). Rule RET-004's own requirement is that a via beyond the screening
    distance is EXAMINED against RET-003 rather than failed outright, and its failure-mode section says that used
    as a law it demands vias where the reference never changed. The gate failed five boards on the screen's raw
    count with nothing looking at a single flagged transition. Here two of the three flagged vias reference the
    same conductor before and after, or change between two different NETS where a ground via cannot help at all,
    and neither is this screen's to fail."""
    _pcbnew()
    import return_via
    with tempfile.TemporaryDirectory() as tmp:
        path, r = _examine_fixture(tmp, [dict(x=10.0, y=10.0, net="SDA0", case="same"),
                                         dict(x=20.0, y=20.0, net="PCIE1_CLK_P", case="to_power"),
                                         dict(x=30.0, y=30.0, net="HB2", case="other_gnd")])
        still, buckets, missing = return_via.examine(path, r)
        assert missing is None, missing
        assert len(buckets["same_reference"]) == 1 and len(buckets["to_power"]) == 1, buckets
        assert still == ["HB2 at (30.00, 30.00)"], \
            "the examination did not take the two vias RET-003 answers out of this screen's failure: %s" % still


def t_a_via_that_moves_between_two_ground_planes_stands_and_so_does_one_nobody_classified():
    """THE ACCEPTABLE CASE, and the half that keeps this from becoming an exemption mechanism. A move between two
    GROUND planes is exactly what a ground via beside the transition is for, so it stands; and a via the
    examination could not classify stands too, because an unexamined via is not an examined one. With no reading
    beside the board at all the screen declares its missing input, which the verdict writer turns into
    INCONCLUSIVE: failing a via the rule says must be examined first is the defect, not the remedy."""
    _pcbnew()
    import return_via
    with tempfile.TemporaryDirectory() as tmp:
        path, r = _examine_fixture(tmp, [dict(x=10.0, y=10.0, net="SDA0", case="other_gnd"),
                                         dict(x=20.0, y=20.0, net="PCIE1_CLK_P", case="unknown")])
        still, buckets, missing = return_via.examine(path, r)
        assert missing is None and len(still) == 3, (still, missing)
        assert len(buckets["unclassified"]) == 1, buckets
    with tempfile.TemporaryDirectory() as tmp:
        path, r = _examine_fixture(tmp, None)
        still, buckets, missing = return_via.examine(path, r)
        assert missing and "ref_change" in missing, missing
        assert still == r["lacking"], "a screen with no examination beside it quietly dropped a via"


def _fanout_board(pcbnew, tmp, amps):
    """A board with one rail pad, one via on it, and an intent file declaring what the rail carries."""
    b = _board(pcbnew, 20.0, 20.0)
    net = pcbnew.NETINFO_ITEM(b, "/+5V_X"); b.Add(net)
    fp = pcbnew.FOOTPRINT(b); fp.SetReference("U1")
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(10)))
    pad = pcbnew.PAD(fp); pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
    pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(10)))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD); pad.SetLayerSet(pcbnew.LSET.FrontMask()); pad.SetNumber("1")   # LSET(layer) is not offered by this build (KiCad 9.0.9)
    pad.SetNet(net); fp.Add(pad); b.Add(fp)
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(10)))
    v.SetDrill(pcbnew.FromMM(0.25)); v.SetWidth(pcbnew.FromMM(0.45)); v.SetNet(net); v.SetLocked(True); b.Add(v)
    path = os.path.join(tmp, "fan.kicad_pcb"); pcbnew.SaveBoard(path, b)
    os.makedirs(os.path.join(tmp, "out"), exist_ok=True)
    json.dump({"rails": {"/+5V_X": {"volts": 5.0, "amps_peak": amps, "source": "U1", "loads": {}}}},
              open(os.path.join(tmp, "out", "fan-intent.json"), "w"))
    return path


def t_a_rail_crossing_with_fewer_barrels_than_its_current_needs_is_named_at_generation_time():
    """THE DEFECTIVE FIXTURE (18 September 2026). Every PI-003 failure this project has found has one shape: a
    rail crosses layers through ONE barrel. Board B is three slot rails at 2.20 A through a single 0.25 mm
    barrel sitting inside that slot's bulk capacitor pad, which is this very stage's via-in-pad. The solved mesh
    finds them after a route; at the pad of a rail's declared SOURCE the whole rail current crosses, so the
    barrels it needs are arithmetic and the fanout can say so before anything is routed."""
    p = _pcbnew()
    with tempfile.TemporaryDirectory() as tmp:
        path = _fanout_board(p, tmp, 2.2)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "prefanout.py"), path, "+5V_X"],
                           capture_output=True, text=True)
        assert "fanout:   +5V_X at U1 pad 1" in r.stdout, \
            "the detail line does not carry the tool's name, so the chain's own grep drops it: %s" % r.stdout[-600:]
        assert "which needs 4 at a 10 K rise" in r.stdout, r.stdout[-600:]


def t_a_crossing_that_carries_what_it_should_says_nothing_about_being_short():
    """THE ACCEPTABLE FIXTURE. The same board and the same one barrel, with the rail declaring 0.30 A: a 0.25 mm
    barrel is rated 0.65 A at a 10 K rise, so one is enough and the stage says the crossings are carried. A
    report that fires on every board would be noise and the next person would stop reading it."""
    p = _pcbnew()
    with tempfile.TemporaryDirectory() as tmp:
        path = _fanout_board(p, tmp, 0.30)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "prefanout.py"), path, "+5V_X"],
                           capture_output=True, text=True)
        assert "fewer barrels" not in r.stdout, r.stdout[-600:]
        assert "carry the barrels their current needs" in r.stdout, r.stdout[-600:]


def _perforated_board(pcbnew, tmp, name, holes=15, plane_to_mm=79.0):
    """A signal run over a ground plane that ANOTHER net's vias perforate.

    `plane_to_mm` shortens the plane so part of the run has no reference at all, which is the other half of the
    pair: a hole in a reference and an absent reference must not read the same."""
    b = _board(pcbnew, 80.0, 30.0)     # long enough that the vias sit 4 mm apart and the fill plainly resumes
    for n in ("/SIG", "GND", "/OTH"):
        b.Add(pcbnew.NETINFO_ITEM(b, n))
    b.BuildListOfNets()
    code = {n: b.FindNet(n).GetNetCode() for n in ("/SIG", "GND", "/OTH")}
    def _set(item, n): item.SetNetCode(code[n]); return item
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(5.0), pcbnew.FromMM(15.0)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(75.0), pcbnew.FromMM(15.0)))
    t.SetWidth(pcbnew.FromMM(0.25)); t.SetLayer(pcbnew.F_Cu); _set(t, "/SIG"); b.Add(t)
    for k in range(holes):
        # BESIDE the run, never on it (the fixture's own version of the 17 September lesson): a via at the
        # track's own centre line is joined to it by KiCad's connectivity when the board is loaded, and the
        # whole fixture then judges ONE net with a via field of its own. At 0.5 mm the via's anti-pad (0.3 mm
        # of barrel plus the fill's 0.3 mm clearance) still covers the track's centre, which is what perforates
        # the reference, and its copper stays 0.2 mm clear of the track's edge.
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(8.0 + 4.0 * k), pcbnew.FromMM(15.5)))
        v.SetDrill(pcbnew.FromMM(0.3)); v.SetWidth(pcbnew.FromMM(0.6)); _set(v, "/OTH"); b.Add(v)
    z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); _set(z, "GND"); o = z.Outline(); o.NewOutline()
    for (x, y) in ((1, 1), (plane_to_mm, 1), (plane_to_mm, 29), (1, 29)): o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))  # plane_to_mm shortens it
    b.Add(z)
    path = os.path.join(tmp, name + ".kicad_pcb"); b.Save(path)
    b = pcbnew.LoadBoard(path); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(path)   # never fill a python-built board
    os.makedirs(os.path.join(tmp, "out"), exist_ok=True)
    json.dump({"rails": {}, "bypass": [], "pair_classes": {"USB": None}},
              open(os.path.join(tmp, "out", name + "-intent.json"), "w"))
    return pcbnew.LoadBoard(path), path


def t_a_reference_perforated_by_another_nets_vias_is_not_an_absent_reference():
    """THE ACCEPTABLE FIXTURE (18 September 2026). Measured on board B run by run: of 675 mm of uncovered signal
    run over 937 runs, 884 runs and 601 mm are the anti-pad of ANOTHER conductor's via, median 0.7 mm and
    longest 3.0 mm, while the reference is genuinely absent for 39 runs and 60 mm. A six-layer board with three
    compute modules has a via field and this screen was measuring it, which is the false positive its own
    registry entry predicts in as many words. The return current goes around a 0.7 mm hole; it does not lose its
    reference. The millimetres are still counted and printed, because a share that disappears is a share nobody
    can argue about."""
    pcbnew = _pcbnew(); sys.path.insert(0, TOOLS)
    import intent_checks
    with tempfile.TemporaryDirectory() as tmp:
        b, p = _perforated_board(pcbnew, tmp, "perf")
        fails = []
        intent_checks.run(b, lambda ok, text: (None if ok else fails.append(text)), p)
        rp = [f for f in fails if f.startswith("return path")]
        assert not rp, "a run over a reference perforated by another net's vias was failed as unreferenced: %s" % rp
        assert intent_checks.LAST.get("antipad_other_mm", 0) > 1.0, \
            "the other-net anti-pad millimetres are not counted: %s" % intent_checks.LAST


def t_an_absent_reference_still_fails_under_the_same_vias():
    """THE DEFECTIVE FIXTURE, and the half that keeps the change from being a loosening: the same board and the
    same via field, with the plane stopping at 40 mm so half the run has no reference at all. That
    is an absent reference, not a hole in one, and the screen must still refuse it."""
    pcbnew = _pcbnew(); sys.path.insert(0, TOOLS)
    import intent_checks
    with tempfile.TemporaryDirectory() as tmp:
        b, p = _perforated_board(pcbnew, tmp, "gap", plane_to_mm=40.0)
        fails = []
        intent_checks.run(b, lambda ok, text: (None if ok else fails.append(text)), p)
        rp = [f for f in fails if f.startswith("return path")]
        assert rp, "a run with 35 mm of no reference at all passed: %s" % intent_checks.LAST
