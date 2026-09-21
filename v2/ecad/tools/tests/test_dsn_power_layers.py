#!/usr/bin/env python3
"""A keep-out reaches the router under three spellings and the power-layer drop knew one (21 September 2026).

`route_one.sh` turns a plane layer into a POWER layer in the DSN and removes the board-wide keep-outs there,
because a board-wide wire keep-out on a plane made Freerouting thrash for its whole time limit (the B14 In1
test, B15 run 1). It searched the DSN text for `(wire_keepout`. KiCad writes a rule area that forbids TRACKS
that way, one that forbids VIAS as `(via_keepout`, and one that forbids BOTH as `(keepout`, and
`sense_fence.py`, written this morning, sets both: E38's own DSN carries 34 `(keepout`, 2 `(wire_keepout` and
0 `(via_keepout`, the eleven fence areas among the first kind. Both fencing boards fence F.Cu and B.Cu, so no
arm in flight is touched; the first board to fence an inner plane would hand the router exactly the polygon
that block exists to remove.

`_old()` below is the inline block as it stood, kept in the fixture so the defect is proved here rather than
remembered: it is asserted to leave the defective fixture untouched. The tool tells the three kinds apart.
A wire keep-out on a power layer is dropped (no wire is routed there); a via keep-out STANDS (vias cross a
power layer, so forbidding one is a real instruction); a full keep-out is rewritten to a via keep-out, which
keeps the instruction and removes the polygon that costs the route."""
import os
import re
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import dsn_power_layers as dpl                                          # noqa: E402

HEAD = """(pcb pcb-e1-dock
  (structure
    (layer F.Cu (type signal))
    (layer In1.Cu (type signal))
    (layer B.Cu (type signal))
"""
TAIL = "  )\n)\n"


def _dsn(*blocks):
    return HEAD + "".join("    %s\n" % b for b in blocks) + TAIL


def _area(tok, layer, x=0):
    return '(%s "" (polygon %s 0  %d 0  %d 0  %d 1000  %d 1000))' % (tok, layer, x, x + 1000, x + 1000, x)


def _old(s, layers):
    """The inline block of route_one.sh as it stood before this tool, verbatim in behaviour."""
    for lay in layers:
        s = re.sub(r"(\(layer %s\s*\(type )signal(\))" % re.escape(lay), r"\1power\2", s)
    out, i = [], 0
    while True:
        j = s.find("(wire_keepout", i)
        if j < 0:
            out.append(s[i:])
            break
        depth, k = 0, j
        while k < len(s):
            if s[k] == "(":
                depth += 1
            elif s[k] == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        end = k + 1                                  # the block's own end, never a count of characters
        block = s[j:end]
        if any(("(polygon %s" % lay) in block for lay in layers):
            out.append(s[i:j])
        else:
            out.append(s[i:end])
        i = end
    return "".join(out)


def _run(text, layers):
    d = tempfile.mkdtemp()
    fn = os.path.join(d, "x.dsn")
    open(fn, "w").write(text)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "dsn_power_layers.py"), fn] + layers,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, "the tool exited %d: %s" % (r.returncode, r.stderr[:300])
    return open(fn).read(), r.stdout


# ---- the defective fixture: the sense fence's own spelling, on a plane layer ----

def t_the_old_block_leaves_a_full_keepout_on_a_power_layer_untouched():
    """The proof this was worth writing: run the block as it stood against the fence's own output."""
    before = _dsn(_area("keepout", "In1.Cu"))
    after = _old(before, ["In1.Cu"])
    assert "(keepout" in after and "(polygon In1.Cu" in after, \
        "the old block removed it after all, so the defect is not what this fixture says"
    assert "(type power)" in after, "the old block did not even change the layer type"


def t_a_full_keepout_on_a_power_layer_becomes_a_via_keepout():
    out, log = _run(_dsn(_area("keepout", "In1.Cu")), ["In1.Cu"])
    assert "(via_keepout" in out, "the fence still forbids wires on a plane layer: %s" % out
    assert not re.search(r"\(keepout\b", out), "the full keep-out is still there: %s" % out
    assert "1 full keep-out(s) rewritten" in log, "the rewrite is not reported: %s" % log


def t_the_rewrite_keeps_the_polygon_and_the_layer():
    out, _ = _run(_dsn(_area("keepout", "In1.Cu", x=4000)), ["In1.Cu"])
    assert "(polygon In1.Cu 0  4000 0  5000 0  5000 1000  4000 1000)" in out, \
        "the rewritten keep-out lost its shape: %s" % out


# ---- behaviour that must not move ----

def t_a_wire_keepout_on_a_power_layer_is_still_dropped():
    out, log = _run(_dsn(_area("wire_keepout", "In1.Cu")), ["In1.Cu"])
    assert "keepout" not in out, "B14's and B15's thrashing polygon survived: %s" % out
    assert "1 wire keep-outs dropped" in log, "the drop is not reported: %s" % log


def t_a_via_keepout_on_a_power_layer_stands():
    out, log = _run(_dsn(_area("via_keepout", "In1.Cu")), ["In1.Cu"])
    assert "(via_keepout" in out, "a via keep-out on a plane is a real instruction and it was removed: %s" % out
    assert "1 via keep-out(s) kept" in log, "the keep is not reported: %s" % log


def t_every_kind_on_a_signal_layer_is_untouched():
    """The acceptable fixture: nothing of this is on a power layer."""
    before = _dsn(_area("keepout", "F.Cu"), _area("wire_keepout", "B.Cu"), _area("via_keepout", "B.Cu"))
    out, _ = _run(before, ["In1.Cu"])
    for tok in ("(keepout", "(wire_keepout", "(via_keepout"):
        assert tok in out, "%s on a signal layer was changed: %s" % (tok, out)
    assert out.replace("(type power)", "(type signal)") == before, "a signal-layer block was rewritten"


def t_a_block_over_a_power_and_a_signal_layer_is_left_alone_and_reported():
    mixed = '(keepout "" (polygon In1.Cu 0  0 0) (polygon F.Cu 0  0 0))'
    out, log = _run(_dsn(mixed), ["In1.Cu"])
    assert mixed in out, "a mixed block was rewritten on a guess: %s" % out
    assert "1 block(s) over a power and a signal layer" in log, "the mixed block is not reported: %s" % log


def t_the_layer_type_changes_to_power():
    out, log = _run(_dsn(), ["In1.Cu"])
    assert "(layer In1.Cu (type power))" in out, "the layer type did not change: %s" % out
    assert "(layer F.Cu (type signal))" in out, "a layer nobody named changed type: %s" % out
    assert "1 layer types changed" in log, "the change is not reported: %s" % log


def t_the_summary_line_keeps_the_wording_the_logs_carry():
    """Two months of route logs are read by that sentence; the new counts are a second line."""
    _, log = _run(_dsn(), ["In1.Cu", "In2.Cu"])
    assert log.splitlines()[0].startswith("power layers in the DSN: In1.Cu, In2.Cu (1 layer types changed, "
                                          "0 wire keep-outs dropped)"), log
