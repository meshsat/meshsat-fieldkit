#!/usr/bin/env python3
"""The board's own rules against the fabricator's capability (rule RTE-001, MESHSAT-862, 16 September 2026).

Every gate in this project judges the COPPER against the board's rules. None of them judged the RULES, and
board P was designed to 0.127 mm track width and clearance on a TWO-LAYER 2 oz build whose capability rows
read 0.16 for both. Heavier copper needs more room to etch, not less, so the 1 oz figure it had borrowed was
not even conservative. Five items, on a board that had passed everything.

These run on synthetic boards written as text, so they need no KiCad: the tool reads the stackup and the
project file, and both are files.
"""
import os, sys, json, tempfile, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import fab_limits


def _board(d, copper_mm, layers, rules, classes):
    """A board file carrying only a stackup, plus its project file. Enough for this tool and nothing else."""
    os.makedirs(d, exist_ok=True)
    inner = "".join('    (layer "In%d.Cu" (type "copper") (thickness 0.0175))\n' % i for i in range(1, layers - 1))
    txt = ('(kicad_pcb (version 20240108)\n  (setup\n    (stackup\n'
           '    (layer "F.Cu" (type "copper") (thickness %s))\n%s'
           '    (layer "B.Cu" (type "copper") (thickness %s))\n    )\n  )\n)\n' % (copper_mm, inner, copper_mm))
    p = os.path.join(d, "brd.kicad_pcb"); open(p, "w").write(txt)
    json.dump({"board": {"design_settings": {"rules": rules}}, "net_settings": {"classes": classes}},
              open(os.path.join(d, "brd.kicad_pro"), "w"))
    return p


def _run(p, cwd):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "fab_limits.py"), p], cwd=cwd,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def t_a_two_layer_two_ounce_board_designed_to_the_one_ounce_numbers_is_refused():
    """Board P's own defect, as a fixture."""
    d = tempfile.mkdtemp(prefix="fab-2oz-")
    p = _board(d, "0.07", 2, {"min_track_width": 0.127, "min_clearance": 0.127,
                              "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3},
               [{"name": "Default", "clearance": 0.127, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3}])
    rc, out = _run(p, d)
    assert rc == 1, "a 2 oz two-layer board at 0.127 mm passed:\n%s" % out[-500:]
    v = json.load(open(os.path.join(d, "out", "fab_limits.verdict.json")))
    assert v["counts"]["under_capability"] >= 3, v
    assert any("0.160" in e for e in v["evidence"]), v["evidence"]


def t_the_same_numbers_pass_on_a_one_ounce_multilayer_board():
    """The same rules are perfectly buildable at 1 oz on four layers, where the row reads 0.09. A rule that
    refused them everywhere would be a rule about nothing."""
    d = tempfile.mkdtemp(prefix="fab-1oz-")
    p = _board(d, "0.035", 4, {"min_track_width": 0.127, "min_clearance": 0.127,
                               "min_via_diameter": 0.4, "min_through_hole_diameter": 0.2},
               [{"name": "Default", "clearance": 0.127, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3}])
    rc, out = _run(p, d)
    assert rc == 0, "a 1 oz four-layer board at 0.127 mm was refused:\n%s" % out[-500:]


def t_a_board_with_no_stackup_is_inconclusive_and_never_a_pass():
    """Boards A and B are in this case today: their committed board files carry no stackup at all, so there is
    no way to know which capability row applies, and guessing one would be the whole defect in a new place."""
    d = tempfile.mkdtemp(prefix="fab-nostack-")
    p = os.path.join(d, "brd.kicad_pcb"); open(p, "w").write("(kicad_pcb (version 20240108)\n)\n")
    json.dump({"board": {"design_settings": {"rules": {"min_track_width": 0.1}}}, "net_settings": {"classes": []}},
              open(os.path.join(d, "brd.kicad_pro"), "w"))
    rc, out = _run(p, d)
    assert rc == 3, "a board with no stackup did not come out INCONCLUSIVE:\n%s" % out[-400:]


def t_the_copper_weight_comes_from_the_stackup_and_not_from_a_literal():
    d = tempfile.mkdtemp(prefix="fab-oz-")
    assert fab_limits.copper_oz(_board(d, "0.035", 2, {}, [])) == 1.0
    d2 = tempfile.mkdtemp(prefix="fab-oz2-")
    assert fab_limits.copper_oz(_board(d2, "0.07", 2, {}, [])) == 2.0
    d3 = tempfile.mkdtemp(prefix="fab-oz3-")
    p = os.path.join(d3, "brd.kicad_pcb"); open(p, "w").write("(kicad_pcb)\n")
    assert fab_limits.copper_oz(p) is None


def t_every_capability_number_in_the_tool_is_in_the_document_it_cites():
    """A limit in the code that is not in the document is a limit this project invented, which is the whole
    thing the registry exists to stop."""
    # TOOLS is v2/ecad/tools, so v2 is two directories up and the vendor tree is beside ecad
    doc = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "vendor", "fabricator",
                       "jlcpcb-pcb-capabilities-2026-09-16.md")
    assert os.path.exists(doc), "the capability document the tool cites is not in the tree: %s" % doc
    txt = open(doc, encoding="utf-8").read()
    missing = []
    for (oz, multi), (t, sp) in sorted(fab_limits.TRACK.items()):
        for v in (t, sp):
            if ("%.2f" % v) not in txt and ("%g" % v) not in txt: missing.append("%.1f oz %s: %s" % (oz, multi, v))
    for v in (fab_limits.MIN_VIA_HOLE, fab_limits.MIN_VIA_DIAM, fab_limits.MIN_NPTH) + fab_limits.VIA_IN_PAD:
        if ("%.2f" % v) not in txt and ("%g" % v) not in txt: missing.append(str(v))
    assert not missing, "numbers in the tool that the cited document does not contain: %s" % missing


def t_every_dielectric_constant_the_stackup_writes_is_in_the_capability_document():
    """The stackup's Dk values decide every impedance this project computes, so each one has to be the
    fabricator's own figure rather than a number from somewhere.

    16 September 2026: the two-layer stacks carried 4.6 for their core, taken from the fabricator's IMPEDANCE
    page on 8 September, which is a different page about the multilayer cores; the capability document states
    4.5 for a 2-layer board. Neither two-layer board carries an impedance target, so nothing computed moved,
    which is exactly when a number is easiest to leave wrong.
    """
    import re as _re
    # BOTH fabricator documents: the capability page carries the FR-4 rows and the impedance page carries the
    # two controlled stackups. A number in the stackup table has to be in one of them.
    fab = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "vendor", "fabricator")
    txt = ""
    for f in sorted(os.listdir(fab)):
        if f.endswith(".md"): txt += open(os.path.join(fab, f), encoding="utf-8").read()
    src = open(os.path.join(TOOLS, "stackup_write.py"), encoding="utf-8").read()
    m = _re.search(r"^STACKS\s*=\s*\{(.*?)^\}", src, _re.S | _re.M)
    assert m, "stackup_write no longer has a STACKS table"
    dks = sorted({d for d in _re.findall(r',\s*(4\.\d+)\)', m.group(1))})
    assert dks, "no dielectric constant found in the stackup table"
    missing = [d for d in dks if d not in txt]
    assert not missing, ("dielectric constants in the stackup that neither fabricator document states: %s"
                         % missing)
