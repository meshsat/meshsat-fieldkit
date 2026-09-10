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
