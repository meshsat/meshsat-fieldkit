#!/usr/bin/env python3
"""A pre-lay group's denominator was KiCad's 499-item cap (21 September 2026).

`full.sh` ran the DRC over the whole placed board and handed the report to `stub_router`, which takes its work
list from `unconnected_items`. KiCad's DRC export lists at most about 499 of them and board A's placed board
is AT that cap, so which of a group's pairs got copper was decided by a truncation. Measured on two arms
launched in the same minute from the same tools, with identical placements (436 footprints at the same
positions, 1,225 tracks, `place_audit` 0 of 19 on both): the switching pre-lay closed **16 of 16 on A99 and
19 of 20 on A99C**, and re-running the DRC on both placed boards gives 499 entries and sixteen switching
pairs on each with `/POE_SW2` absent from both. `prelay_pairs.py` on the same board reports **twenty**, four
for each of the five nets, `/POE_SW2` among them.

The defective fixture here is a board carrying a named net's open pair BEHIND more unconnected items than the
reader is willing to look at, which is the cap in miniature: a truncated report is handed in and the rule
asks whether the pair is still found. The acceptable fixture is a board whose report is not truncated, where
the answer must not change. The board-level rules run only where KiCad is."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)
from harness import Skip                                             # noqa: E402

try:
    import pcbnew
except Exception:                                                    # noqa: BLE001 - the runner has no KiCad
    pcbnew = None


def need(what):
    """The suite's own skip, not a bare exception: a rule that RAISES where KiCad is absent is counted as a
    failure, which is how this file first read 1294 passed and 3 failed on a host that simply has no pcbnew."""
    if pcbnew is None:
        raise Skip("%s needs pcbnew" % what)


def _two_cluster_board(tmp, nets=("A_SW2", "B_SW2"), spread=40.0):
    """A board where every named net has two pads far apart and nothing joining them: one open pair each."""
    b = pcbnew.BOARD()
    for i, n in enumerate(nets):
        net = pcbnew.NETINFO_ITEM(b, "/" + n)
        b.Add(net)
        for k, x in enumerate((10.0, 10.0 + spread)):
            fp = pcbnew.FOOTPRINT(b)
            fp.SetReference("%s%d" % (n[:2], k))
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(10.0 + 5 * i)))
            p = pcbnew.PAD(fp)
            p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0)))
            p.SetLayerSet(pcbnew.LSET.FrontMask())
            p.SetNumber("1")
            p.SetNet(net)
            fp.Add(p)
            b.Add(fp)
    b.BuildConnectivity()
    path = os.path.join(tmp, "fx.kicad_pcb")
    b.Save(path)
    return path


def t_a_named_nets_pair_is_found_when_the_whole_boards_report_would_hide_it():
    """The defective fixture: the report handed in is truncated, as KiCad's own is on board A."""
    need("the pre-lay pair enumeration")
    import tempfile
    import prelay_pairs
    tmp = tempfile.mkdtemp()
    path = _two_cluster_board(tmp)
    rep, kept = prelay_pairs.pairs_from_board(path, ["B_SW2"], keep_dir=tmp)
    nets = set()
    for v in rep.get("unconnected_items", []):
        for it in v.get("items", []):
            t = it.get("description") or ""
            if "[" in t:
                nets.add(t.split("[")[1].split("]")[0].lstrip("/"))
    assert "B_SW2" in nets, "the named net's own open pair was not found: %s" % nets
    assert "A_SW2" not in nets, "a net nobody asked about is in the report, so the cap is still shared: %s" % nets
    assert kept >= 2, "the stripped board kept %d item(s) of the named net" % kept


def t_the_stripped_board_keeps_the_named_nets_geometry():
    """The acceptable fixture: nothing of the group's own copper is moved or dropped."""
    need("the pre-lay pair enumeration")
    import tempfile
    import prelay_pairs
    tmp = tempfile.mkdtemp()
    path = _two_cluster_board(tmp)
    before = pcbnew.LoadBoard(path)
    pos = sorted((p.GetPosition().x, p.GetPosition().y) for fp in before.GetFootprints() for p in fp.Pads()
                 if p.GetNetname().lstrip("/") == "B_SW2")
    out = os.path.join(tmp, "stripped.kicad_pcb")
    prelay_pairs.strip_to(path, ["B_SW2"], out)
    after = pcbnew.LoadBoard(out)
    pos2 = sorted((p.GetPosition().x, p.GetPosition().y) for fp in after.GetFootprints() for p in fp.Pads()
                  if p.GetNetname().lstrip("/") == "B_SW2")
    assert pos == pos2 and len(pos) == 2, "the named net's pads moved or were dropped: %s against %s" % (pos, pos2)


def t_every_other_net_loses_its_net_and_not_its_copper():
    need("the pre-lay pair enumeration")
    import tempfile
    import prelay_pairs
    tmp = tempfile.mkdtemp()
    path = _two_cluster_board(tmp)
    out = os.path.join(tmp, "stripped.kicad_pcb")
    prelay_pairs.strip_to(path, ["B_SW2"], out)
    after = pcbnew.LoadBoard(out)
    pads = [p for fp in after.GetFootprints() for p in fp.Pads()]
    assert len(pads) == 4, "copper was deleted rather than un-netted: %d pad(s) left" % len(pads)
    assert not any(p.GetNetname().lstrip("/") == "A_SW2" for p in pads), "the other net still carries its net"


# ---- the chain has to ASK it, which is the half a tool alone cannot hold ----

def t_both_prelay_stages_take_their_pairs_from_the_board():
    src = open(os.path.join(TOOLS, "full.sh"), encoding="utf-8").read()
    assert src.count("../tools/prelay_pairs.py") >= 2, \
        "a pre-lay stage still takes its work list from the whole board's capped DRC report"
    i = src.find("gstage () {")
    j = src.find("}", src.find("stub_router.py", i))
    assert "prelay_pairs.py" in src[i:j], "the GROUP stage does not ask prelay_pairs"


def t_the_fallback_says_so_rather_than_passing_silently():
    src = open(os.path.join(TOOLS, "full.sh"), encoding="utf-8").read()
    for tag in ("prelay group $GTAG: prelay_pairs refused", "prelay: prelay_pairs refused"):
        assert tag in src, "a fallback to the capped report that says nothing is how this defect lived: %s" % tag


def t_the_tool_warns_when_its_own_report_is_near_the_cap():
    src = open(os.path.join(TOOLS, "prelay_pairs.py"), encoding="utf-8").read()
    assert "still near KiCad's own list cap" in src, \
        "a stripped board can itself reach the cap on a big group and must say so"
