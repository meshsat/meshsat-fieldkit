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


def t_what_orders_is_the_owners_and_the_prose_is_not():
    """OWNER RULING 12 September 2026: the owner will not read the order notes and delegated drafting AND
    approving them, so the BOARDS rows and the per-board prose of make_handoff.py left the floor. What did
    NOT leave it is anything that places an order: the exclusion table, the rotation table, export_jlc.sh
    and the cart. Nothing is ordered and no cart line is touched without the owner, which that ruling did
    not change and this rule holds.
    """
    classes = reserved.load()
    orders = [('make_handoff.py', 'EXCLUDE = {"pcb-a-power": ["TP1"]}'),
              ('make_handoff.py', 'JLC_ROT = {"SOT-23": 180}'),
              ('export_jlc.sh', 'echo "layers, 6, FR-4, ENIG" >> "$NOTES"')]
    for path, line in orders:
        hits = reserved._matches(path, line, classes)
        assert any("order set" in n for n, _ in hits), "not reserved any more and must be: %s | %s" % (path, line)
    prose = [('make_handoff.py', 'BOARDS = [("meshsat-pcb-a-revA-A24", "pcb-a-power")]'),
             ('make_handoff.py', '    notes = "PCB-A POWER, 240 x 160 mm, six layers"')]
    for path, line in prose:
        assert reserved._matches(path, line, classes) == [], \
            "the owner delegated the order prose and it is still refused: %s | %s" % (path, line)


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


def t_every_reserved_pattern_still_matches_its_file():
    """A reserved constant moved or renamed leaves the floor silently (red team round three L5).

    `reserved.json` is a file glob plus a line pattern. If the line it guards is renamed, moved or
    re-indented, the pattern matches nothing and the class quietly stops protecting anything, with no test
    and no message. The floor is only a floor while its patterns still find the lines they were written
    for. Matching here is the same as `reserved._matches`: the glob against the repo-relative path or
    against the basename.
    """
    import os as _os, re as _re, json as _json, fnmatch as _fn
    TOOLS_ = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    REPO_ = _os.path.dirname(_os.path.dirname(_os.path.dirname(TOOLS_)))
    d = _json.load(open(_os.path.join(TOOLS_, "reserved.json")))
    files = []
    for dp, dirs, fs in _os.walk(REPO_):
        dirs[:] = [x for x in dirs if x not in (".git", "__pycache__", "out", "node_modules")]
        for f in fs:
            if f.endswith((".py", ".sh", ".json", ".md", ".txt")):
                files.append(_os.path.join(dp, f))
    dead = []
    for c in d["classes"]:
        if c.get("may_match_nothing"):
            continue          # a class that guards a value which must be ABSENT; the reason is in the file
        for glob_, pat in c["sites"]:
            rx = _re.compile(pat, _re.M)
            hit = False
            for f in files:
                rel = _os.path.relpath(f, REPO_)
                # the same three-way match reserved.py does, or the test and the floor disagree
                if not (_fn.fnmatch(rel, glob_) or _fn.fnmatch(_os.path.basename(rel), glob_)
                        or _fn.fnmatch(rel, "*/" + glob_.lstrip("./"))):
                    continue
                try:
                    if rx.search(open(f, errors="replace").read()):
                        hit = True; break
                except OSError:
                    pass
            if not hit:
                dead.append("%s | %s | %s" % (c["name"], glob_, pat))
    if dead:
        raise AssertionError("%d reserved pattern(s) match no line in any file they name, so the class "
                             "protects nothing:\n  %s" % (len(dead), "\n  ".join(dead)))


def t_a_per_board_exclusion_row_is_reserved_not_only_the_tables_first_line():
    """12 September 2026, found by making the change and asking the floor about it.

    The order class named `^EXCLUDE\\s*=`, which matches the line the table OPENS on and nothing else.
    Every per-board exclusion actually lives on a continuation row, so adding a reference to a board's
    bench-fit list, which is precisely a decision about what JLC places, went past the floor without a
    word. The rule that the 12 September delegation drew stands the other way as well: the FABRICATION
    NOTES rows of the same file open with a list and are prose, and must stay OFF the floor.
    """
    classes = reserved.load()
    ordering = [('make_handoff.py', 'EXCLUDE = {"pcb-a-power": {"J_DOCK"},'),
                ('make_handoff.py', '           "pcb-e1-dock": {"F1", "F2", "J_BATT", "U5"},'),
                ('make_handoff.py', '           "pcb-e5-block": set()}')]
    for path, line in ordering:
        hits = reserved._matches(path, line, classes)
        assert any("order set" in n for n, _ in hits), \
            "a row of the exclusion table is not reserved and must be: %s" % line.strip()[:70]
    prose = ('make_handoff.py', '    "pcb-e1-dock": ["FABRICATION NOTES (E7, the dock strip, appendix 32.125)",')
    assert not reserved._matches(*prose, classes), \
        "the delegated order prose is back on the floor: %s" % prose[1].strip()[:70]
