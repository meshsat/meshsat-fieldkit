#!/usr/bin/env python3
"""A via site is judged against a pad's COPPER, never against a circle of its size (MESHSAT-862, 20 Sep 2026).

Board D's chain ended `PREROUTE-DONE BLOCK 1` for days on one `clearance` violation: `Pad 2 [/+5V_D8] of D1`
against a locked `Via [GND]` at (70.925, 67.604999), 0.1115 mm where the PWR class asks 0.1270. Two
attributions were wrong before a per-stage DRC named the stage, and both were wrong for the same reason, a
count over a window with TWO writers in it: board D declares `fanout_nets = "GND"`, so `prefanout` lays a via
per ground pad and `gnd_grid` lays its lattice, and the 1,378 vias between the placed board and the pre-lay
snapshot are the sum of the two.

Run one at a time with a DRC after each, the stage names itself: placed hard 2 (two same-part mask items),
prefanout hard 3 with the clearance, gnd_grid hard 4 and the clearance UNCHANGED, so the grid neither laid it
nor should have removed it (`_own_hard` only offers the vias gnd_grid itself placed, which is correct).

THE CAUSE: both in-pad fallbacks measured CENTRE TO CENTRE against `qr + VIA_D / 2 + INPAD_CLR` with `qr =
max(size.x, size.y) / 2` used as a CIRCLE radius. A circle of the long half-dimension does not contain a
rectangle's corners, so a via approaching a land ALONG ITS DIAGONAL passes while its copper does not, and it
is too STRICT along the short axis for the same reason. D1 is a 2.500 x 2.300 SMB land and the via sits in
C9 pad 2, 1.9313 mm away on the diagonal against a demand of 1.6750: accepted, and the real gap from the
ring to that copper is 0.1137 mm. The same file's `_crosses` has judged against the polygon since this
morning, for this reason, on the other half of the tool.

MEASURED, one variable, the same placed board: fanout **90 vias (5 in the pad) and 15 pads skipped becomes
93 (8 in the pad) and 12 skipped**, and the hard set **3 {solder_mask_bridge 2, clearance 1} becomes 2
{solder_mask_bridge 2}**. It gains three plane vias because the circle was wrong in BOTH directions, and C9
pad 2 declines itself with `no room for a fanout via`.

The fifth instance this week of one shape: a guard whose question is cheaper than the fact it guards."""
import os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip   # one class, shared with the runner (a second copy makes every skip read as a failure)


def _src():
    return open(os.path.join(TOOLS, "prefanout.py"), encoding="utf-8").read()


def t_no_via_site_is_judged_by_a_circle_of_the_pads_own_size():
    """THE DEFECT ITSELF. Fails on the tree this rule was written against, where the second in-pad fallback
    read `all(math.hypot(c.x - qp.x, c.y - qp.y) >= qr + VIA_D / 2 + INPAD_CLR ...)`."""
    s = _src()
    for m in re.finditer(r"hypot\([^)]*\)\s*>=\s*qr\s*\+", s):
        raise AssertionError("a via site is still judged against a circle of the pad's own size: %s"
                             % s[max(0, m.start() - 60):m.end() + 40].replace("\n", " "))
    assert "_other_net_clear" in s, "prefanout has no polygon-based clearance test for a via site"


def t_the_polygon_test_is_asked_by_both_in_pad_fallbacks():
    """There are TWO of them and only one had any other-net test at all. The `skip_fp` branch, which gives a
    fine part's exposed pad its plane via, asked ONLY whether a via was already within `VIA_D + 0.35`: no
    pads, no tracks, no rule areas, no board edge. It never caused board D's item (C9 is an 0805 and
    `is_fine` is false for it) and it is the same hole one branch along."""
    s = _src()
    assert s.count("_other_net_clear(c, pad.GetNetname()") == 2, \
        "the polygon test is asked by %d in-pad fallback(s), not 2" % s.count("_other_net_clear(c, pad.GetNetname()")
    head = s.split("if skip_fp:")[1][:900]
    assert "_other_net_clear" in head, "the fine-part exposed-pad branch still lays a via with no other-net test"
    assert "_seg_dist(c, a_, e_)" in head, "the fine-part exposed-pad branch still ignores laid tracks"


def t_the_cheap_circle_survives_only_as_a_pre_filter():
    """A polygon call per pad per candidate is a SWIG call per pad per candidate, which is why the tool
    carried a circle in the first place. The reach the tuple already carries bounds how far a pad's copper
    can be from its centre, so the polygon is asked only of pads that could possibly be close, and the
    pre-filter can only ever ADMIT a pad to the real test."""
    s = _src()
    fn = s.split("def _other_net_clear(")[1].split("\ndef ")[0]
    assert "qreach + need" in fn, "the polygon test has no cheap pre-filter and runs a SWIG call per pad"
    assert "continue" in fn and "Collide(c, int(need))" in fn, \
        "the pre-filter does not fall through to the polygon, so it is deciding on its own"


def t_the_measurement_is_recorded_where_the_next_reader_looks():
    """A tool change without its number is a claim. Board D's file carries the before and after."""
    d = open(os.path.join(TOOLS, "boards", "d.json"), encoding="utf-8").read()
    assert "90 vias" in d and "93" in d, "board D's file does not carry the fanout count before and after"
    assert "0.1137" in d or "0.1115" in d, "board D's file does not carry the gap that was accepted"


# ---------------------------------------------------------------------------------------------------------
# THE PER-REFERENCE DEBUG KNOB (21 September 2026, D34). D33's finished round-1 board is one connection short
# and the connection is U6 pad 20, a codec ground pin with no fanout via; this tool's only word about it was
# `no room for a fanout via at U6 pad 20 (GND)`, which names the pad and not the obstacle, so the record could
# say no more than "prefanout's refusal to read". `escape.py` has had DEBUG_REF since 5 September. The reason
# is written by the predicate that refuses, never by a second copy of it.

def _pcbnew():
    try:
        import pcbnew; return pcbnew
    except Exception as e:
        raise Skip("no pcbnew here (%s)" % type(e).__name__)


def _walled_in(pcbnew, tmp):
    """One ground pad with other nets' pads all around it, close enough that no stub and no in-pad via fits.

    The neighbours are 1.0 mm away edge to edge on a 0.6 mm pad, which is inside the 0.5 mm exit lane `clear`
    keeps from another net's pad for a 0.45 mm via, and the pad itself is too small to hold one."""
    import os
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, 20, 0), (20, 0, 20, 20), (20, 20, 0, 20), (0, 20, 0, 0)):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))); s.SetWidth(pcbnew.FromMM(0.1)); b.Add(s)
    for n in ("GND", "/OTH"): b.Add(pcbnew.NETINFO_ITEM(b, n))
    b.BuildListOfNets()
    def _pad(fp, x, y, net, size=0.6):
        p = pcbnew.PAD(fp); p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
        p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetLayerSet(pcbnew.LSET.FrontMask())
        p.SetNumber("20" if net == "GND" else "1"); p.SetNet(b.FindNet(net)); fp.Add(p); return p
    fp = pcbnew.FOOTPRINT(b); fp.SetReference("U6")
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(10)))
    # 0.45 mm, which is SMALLER than this board's own via plus the tenth of a millimetre the in-pad allowance
    # asks for (a 2-layer board floors the via at 0.5), so the fallback is refused as well and the pad is
    # served by nothing: that is the state U6 pad 20 is in on board D and the state this fixture is about.
    _pad(fp, 10, 10, "GND", size=0.45); b.Add(fp)
    for k, (dx, dy) in enumerate(((1.0, 0), (-1.0, 0), (0, 1.0), (0, -1.0),
                                  (0.75, 0.75), (-0.75, 0.75), (0.75, -0.75), (-0.75, -0.75))):
        g = pcbnew.FOOTPRINT(b); g.SetReference("R%d" % (k + 1))
        g.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10 + dx), pcbnew.FromMM(10 + dy)))
        _pad(g, 10 + dx, 10 + dy, "/OTH"); b.Add(g)
    path = os.path.join(tmp, "walled.kicad_pcb"); pcbnew.SaveBoard(path, b); return path


def _run(path, ref=None, tool=None):
    import subprocess
    env = dict(os.environ)
    if ref: env["DEBUG_REF"] = ref
    else: env.pop("DEBUG_REF", None)
    return subprocess.run([sys.executable, tool or os.path.join(TOOLS, "prefanout.py"), path, "GND"],
                          capture_output=True, text=True, env=env).stdout


def t_the_debug_knob_names_the_test_that_refused_and_its_counterparty():
    """THE DEFECTIVE FIXTURE: a pad the tool cannot serve, and the question is WHY.

    Without the knob the tool says `no room for a fanout via at U6 pad 20 (GND)` and stops, which is where
    D34's item sat for a day. With it every candidate says which test refused it and against what, and the
    in-pad fallback says which of its four conditions failed. Fails on the tree this rule was written against,
    where `prefanout.py` reads no DEBUG_REF at all."""
    import tempfile
    p = _pcbnew()
    with tempfile.TemporaryDirectory() as tmp:
        out = _run(_walled_in(p, tmp), ref="U6")
        assert "no room for a fanout via at U6 pad 20" in out, out[-800:]
        assert "fanout DEBUG U6 pad 20" in out, "the knob printed nothing for the reference it was given: %s" % out[-800:]
        assert "refused," in out, out[-800:]
        assert "mm from a pad of /OTH" in out, "the refusal does not name the counterparty: %s" % out[-800:]
        assert "the in-pad via is refused too" in out, out[-800:]


def t_the_debug_knob_is_off_unless_a_reference_is_named():
    """THE ACCEPTABLE FIXTURE: the same board with no DEBUG_REF prints the summary and the pad, and not one
    candidate line. A probe that is on by default is noise in every chain log on every board, and this project
    reads those logs with a grep."""
    import tempfile
    p = _pcbnew()
    with tempfile.TemporaryDirectory() as tmp:
        path = _walled_in(p, tmp)
        quiet, loud = _run(path), _run(path, ref="U6")
        assert "fanout DEBUG" not in quiet, quiet[-800:]
        assert "no room for a fanout via at U6 pad 20" in quiet, quiet[-800:]
        assert "fanout: 0 vias added (0 in the pad), 1 pads skipped" in quiet, quiet[-800:]
        # the knob CHANGES NOTHING BUT THE PRINTING: the summary is the same line either way
        assert [l for l in quiet.splitlines() if l.startswith("fanout:")] == \
               [l for l in loud.splitlines() if l.startswith("fanout:")], (quiet[-400:], loud[-400:])
