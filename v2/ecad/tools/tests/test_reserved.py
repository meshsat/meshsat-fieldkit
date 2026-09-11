#!/usr/bin/env python3
"""The never-auto floor: the short written list of decisions no band may take.

MESHSAT-862, 11 September 2026. Territory Grounder's floor sits ABOVE its posture check, so a floor-class operation
is refused identically in Shadow and in Full-auto, and the older prose that puts the mode check first is the thing
not to copy. A floor a mode can lift is not a floor.

The classes are data with a pattern per site, because file level would be useless: `gen_pcb_b3.py` holds the net
classes and the region packer and most of the placement, and only the first two are the owner's.
"""
import os, re, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import reserved


def _run(argv):
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "reserved.py")] + argv,
                       capture_output=True, text=True, timeout=120, cwd=tempfile.mkdtemp(prefix="rs-"))
    return p.returncode, p.stdout + p.stderr


def t_every_class_says_why_and_has_at_least_one_site():
    for name, why, sites in reserved.load():
        assert len(why) > 40, "%s is reserved without a reason worth reading: %r" % (name, why)
        assert sites, "%s reserves nothing" % name


def t_a_changed_impedance_target_is_the_owners():
    hits = reserved._matches("intent.py", 'Z_DEFAULT = {"USB": {"z_diff": 85.0}}', reserved.load())
    assert any("impedance" in n for n, _ in hits), hits


def t_a_changed_layer_count_is_the_owners():
    hits = reserved._matches("gen_pcb_a.py", "    board.SetCopperLayerCount(4)", reserved.load())
    assert any("layer count" in n for n, _ in hits), hits


def t_a_changed_fab_minimum_is_the_owners():
    hits = reserved._matches("gen_pcb_b.py", '        ("m_ViasMinSize", FromMM(0.35)),', reserved.load())
    assert any("fab rules" in n for n, _ in hits), hits


def t_a_changed_order_set_membership_is_the_owners():
    hits = reserved._matches("make_handoff.py", 'BOARDS = [("meshsat-pcb-a-revA-A24", "pcb-a-power")]', reserved.load())
    assert any("order set" in n for n, _ in hits), hits


def t_ordinary_work_in_the_same_file_is_not_reserved():
    """The rule has to let the work through or it will be worked around, which is worse than not having it."""
    classes = reserved.load()
    for path, line in (("gen_pcb_b3.py", "    fp = place(ref, x, y, rot, back)"),
                       ("gen_pcb_b3.py", "    for ref, fp in placed.items():"),
                       ("gen_pcb_a.py", "    b.SetFileName(out)"),
                       ("intent.py", "def pair_class(name, z_diff=None, z_se=None):")):
        assert reserved._matches(path, line, classes) == [], (path, line, reserved._matches(path, line, classes))


def t_nothing_examined_is_inconclusive_not_a_pass():
    """0 reserved lines of 0 is what a clean tree, a broken diff and a wrong range all produce identically."""
    rc, out = _run(["--files"])
    assert rc == 3, (rc, out)
    assert "nothing was judged" in out, out


def t_a_file_carrying_a_reserved_line_is_refused():
    d = tempfile.mkdtemp(prefix="rs2-")
    f = os.path.join(d, "gen_pcb_a.py")
    open(f, "w").write("import pcbnew\nboard.SetCopperLayerCount(6)\n")
    rc, out = _run(["--files", f])
    assert rc == 1, (rc, out)
    assert "OWNER" in out and "layer count" in out, out
    assert "do not work around the floor" in out, out
