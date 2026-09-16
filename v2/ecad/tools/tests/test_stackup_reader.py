#!/usr/bin/env python3
"""The stackup a board declares, read whichever way KiCad wrote it (MESHSAT-862, 13 September 2026).

`read_stackup` parsed the block LINE BY LINE, with a regex that wanted `(layer "F.Cu" (type "copper")
(thickness 0.07))` all on one line. KiCad 9 saves it with every field on its own line, so a board that has
been through `SaveBoard` matched nothing and the reader returned an empty stackup, silently.

Nothing said so, because both readers of it have a fallback that is right for most of this set: `dc_drop`
falls back to 0.035 mm outer and 0.0152 inner, which IS what the four and six layer boards carry. It showed
on P3, which owner ruling 7 orders at **2 oz**: the committed board still carries the older one-line form and
reads 2 of 3 rails MET, and a freshly REGENERATED one was judged at half its copper and read 0 of 3, with
IPC's figure for a 0.500 mm track falling from 2.39 A to 1.45.

So the two forms must give the same answer, and a declared stackup must never be silently replaced by a
default. The reader walks brackets now.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)

ONE = '''  (stackup
    (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
    (layer "F.Cu" (type "copper") (thickness 0.07))
    (layer "dielectric 1" (type "core") (thickness 1.44) (material "FR4 core") (epsilon_r 4.6) (loss_tangent 0.02))
    (layer "B.Cu" (type "copper") (thickness 0.07))
  )
'''
MANY = '''\t\t(stackup
\t\t\t(layer "F.Mask"
\t\t\t\t(type "Top Solder Mask")
\t\t\t\t(thickness 0.01)
\t\t\t)
\t\t\t(layer "F.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.07)
\t\t\t)
\t\t\t(layer "dielectric 1"
\t\t\t\t(type "core")
\t\t\t\t(thickness 1.44)
\t\t\t\t(material "FR4 core")
\t\t\t\t(epsilon_r 4.6)
\t\t\t)
\t\t\t(layer "B.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.07)
\t\t\t)
\t\t)
'''


def _read(txt):
    from impedance_check import read_stackup
    with tempfile.NamedTemporaryFile("w", suffix=".kicad_pcb", delete=False) as fh:
        fh.write(txt); p = fh.name
    try: return read_stackup(p)
    finally: os.unlink(p)


def t_both_forms_give_the_same_stackup():
    a, b = _read(ONE), _read(MANY)
    assert a == b, "the same stackup read two ways gives two answers:\n  one line:   %s\n  many lines: %s" % (a, b)


def t_the_multi_line_form_is_not_empty():
    """The failure as it happened: the reader returned nothing and the caller's default took over."""
    b = _read(MANY)
    assert b, "a board saved by KiCad 9 reads as having no stackup at all"
    cu = [x for x in b if x[1] == "copper"]
    assert len(cu) == 2 and all(abs(t - 0.07) < 1e-9 for _, _, t, _ in cu), \
        "the 2 oz copper of owner ruling 7 did not survive the read: %s" % cu


def t_a_dielectric_without_epsilon_still_carries_none():
    """The old parser's one deliberate property: no default epsilon, because a dielectric without one is
    refused rather than guessed. It must survive the rewrite."""
    txt = ONE.replace(' (epsilon_r 4.6)', '')
    core = [x for x in _read(txt) if x[1] == "core"]
    assert core and core[0][3] is None, "a dielectric with no epsilon_r came back with one: %s" % core


def t_the_stackup_is_written_after_the_last_pcbnew_save_in_each_chain():
    """The stackup goes into the board as TEXT, and every pcbnew save after it drops the block.

    16 September 2026: full.sh wrote it at line 99, right after the placement generator, and then ran
    bypass_place, escape.py, join_adjacent_pins and the pair pre-router, each of which loads and saves the
    board. Boards A and B reached the router with NO STACKUP AT ALL while their own pre-route log said
    "stackup_write: JLC06161H-3313 (6 copper layers) written". The impedance check, the fabricator-limit check
    and the order notes' copper weight all read the stackup, and all three were reading nothing on the two
    six-layer boards for as long as those boards have existed.

    So: in each chain, no tool that saves a board may run after the LAST stackup_write.
    """
    import os as _os, re as _re
    TOOLSDIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    # tools that load a board with pcbnew and save it again
    SAVERS = ("bypass_place.py", "escape.py", "join_adjacent_pins.py", "pair_preroute.py", "prefanout.py",
              "cleanup_dangling.py", "stub_router.py", "pour_stitch.py", "zone_pad_via.py", "straighten.py",
              "return_via.py", "gnd_grid.py", "rail_prune.py", "stitch_prune.py", "direct_close.py")
    bad = []
    for chain in ("full.sh", "finish.sh"):
        p = _os.path.join(TOOLSDIR, chain)
        if not _os.path.exists(p): continue
        lines = open(p, errors="replace").read().splitlines()
        last = max([i for i, l in enumerate(lines) if "stackup_write.py" in l and not l.strip().startswith("#")] or [-1])
        if last < 0: bad.append("%s never writes a stackup" % chain); continue
        for i, l in enumerate(lines[last + 1:], last + 2):
            if l.strip().startswith("#"): continue
            for t in SAVERS:
                if t in l:
                    bad.append("%s line %d runs %s AFTER the last stackup_write, which drops the block" % (chain, i, t))
    assert not bad, "; ".join(bad)


def t_the_pre_route_chain_refuses_a_board_with_no_stackup():
    """Writing it last is the fix; this is what proves it happened rather than trusting that it did."""
    import os as _os
    TOOLSDIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    src = open(_os.path.join(TOOLSDIR, "full.sh"), errors="replace").read()
    assert "the board carries no stackup" in src, "full.sh does not check that the stackup survived"
    assert "no stackup (rule STK-001)" in src, "the refusal does not name the rule it serves"


def t_a_stackup_written_across_several_lines_reads_the_same_as_one_written_on_one():
    """16 September 2026. KiCad writes a stackup layer on ONE line when a tool writes the block and across
    SEVERAL when pcbnew saves the file itself, so a board that has been through SaveBoard since its stackup was
    written does not match a single-line expression. Three places carried one, and on boards A, D and E, whose
    files are in the expanded form, all three read 'no stackup at all': fab_limits reported rules RTE-001 and
    STK-001 as unanswerable on three boards that carry a stackup, export_jlc.sh would have sent the fabricator
    an order note saying the copper weight was NOT DECLARED, and this file's own sibling rule would have failed
    on the same folders. One reader now, and both forms are the same board."""
    import os, sys
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, tools)
    import stackup_read
    one = '(layer "F.Cu" (type "copper") (thickness 0.035))\n(layer "B.Cu" (type "copper") (thickness 0.035))\n'
    multi = ('(layer "F.Cu"\n  (type "copper")\n  (thickness 0.035)\n)\n'
             '(layer "B.Cu"\n  (type "copper")\n  (thickness 0.035)\n)\n')
    assert stackup_read.outer_copper_mm(one) == 0.035, stackup_read.outer_copper_mm(one)
    assert stackup_read.outer_copper_mm(multi) == 0.035, "the expanded form still reads as no stackup"
    assert stackup_read.outer_copper_oz(one) == stackup_read.outer_copper_oz(multi) == 1.0
    # two ounces, and the thickness must come from the layer's OWN block and never the next one's
    mixed = ('(layer "F.Cu"\n  (type "copper")\n  (thickness 0.070)\n)\n'
             '(layer "dielectric 1"\n  (type "prepreg")\n  (thickness 0.2104)\n)\n')
    assert stackup_read.outer_copper_mm(mixed) == 0.070, stackup_read.outer_copper_mm(mixed)
    # a board with no stackup says so rather than guessing
    assert stackup_read.outer_copper_oz("(kicad_pcb)\n") is None
    # and the three call sites use it rather than their own expression
    for f in ("fab_limits.py", "export_jlc.sh"):
        src = open(os.path.join(tools, f), encoding="utf-8").read()
        assert "stackup_read" in src, "%s does not use the one reader" % f
        assert '(type "copper")\\) \\(thickness' not in src, "%s still carries the single-line expression" % f
