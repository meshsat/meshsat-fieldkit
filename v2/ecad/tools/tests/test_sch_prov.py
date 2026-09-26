#!/usr/bin/env python3
"""A netlist says which generator wrote it, and a contract judged against an unknown one decides nothing.

16 September 2026. The set-level cross-board verdict failed twelve contracts, all of them naming board B's six
PCIe receive coupling capacitors as absent. They were present: board B's own netlist carried them and board
B's own contract verdict read PASS on 37 of 37. The set verdict had been taken inside board A's sweep tree,
whose copy of board B came from before the capacitors existed, and seven boards carried a FAIL on rule SCH-003
because of it.

The guard that already existed compares a netlist's timestamp with its OWN schematic's, and cannot see this:
in a copied tree both are old together. Age was never the property that mattered. So the netlist carries the
identity of its generator, by content, and a checker running under different content says so.

Fixtures both ways: a netlist written by this tree's generator (expected to be judged) and one written by a
different generator (expected to be refused, as missing rather than as failing, because a comparison against
another design's data is not a result in either direction).
"""
import os, re, sys, json, shutil, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import sch_prov as P


def _tree():
    """A tools tree with a generator in it, so the sha is a property of files rather than of this checkout."""
    d = tempfile.mkdtemp(prefix="prov-")
    open(os.path.join(d, "gen_sch_b.py"), "w").write("# a generator\nprint(1)\n")
    open(os.path.join(d, "kisch.py"), "w").write("# the drawing engine\n")
    open(os.path.join(d, "intent.py"), "w").write("# the rails\n")
    return d


def t_the_generator_identity_is_its_content_not_its_name():
    a = _tree(); b = _tree()
    assert P.generator_sha("b", a) == P.generator_sha("b", b), "two identical trees disagree about the generator"
    open(os.path.join(b, "gen_sch_b.py"), "a").write("# one more line, a different design\n")
    assert P.generator_sha("b", a) != P.generator_sha("b", b), "a changed generator kept its identity"


def t_a_netlist_written_here_is_current_and_one_written_elsewhere_is_not():
    a = _tree(); b = _tree()
    open(os.path.join(b, "gen_sch_b.py"), "a").write("# the capacitors, added at 02:40\n")
    d = tempfile.mkdtemp(prefix="prov-net-"); os.makedirs(os.path.join(d, "out"))
    net = os.path.join(d, "out", "pcb-b-compute.net")
    open(net, "w").write("(export)\n")

    P.write(net, "b", a)                      # ACCEPTABLE fixture: written by tree a
    ok, why = P.current(net, "b", a)
    assert ok, why
    ok, why = P.current(net, "b", b)          # DEFECTIVE fixture: read by tree b, a different design
    assert not ok and "different designs" in why, why


def t_a_netlist_with_no_provenance_is_unknown_and_never_current():
    a = _tree()
    d = tempfile.mkdtemp(prefix="prov-bare-"); os.makedirs(os.path.join(d, "out"))
    net = os.path.join(d, "out", "pcb-b-compute.net"); open(net, "w").write("(export)\n")
    ok, why = P.current(net, "b", a)
    assert not ok and "no provenance" in why, why


def t_the_contract_check_refuses_a_netlist_of_unknown_origin():
    """The end to end shape, at the seam where the twelve failures were produced. check_contracts.py exits at
    module level, so it is RUN rather than imported (importing it would end this test run, which is a trap of
    its own and one this file is not the place to fix)."""
    import subprocess
    d = tempfile.mkdtemp(prefix="prov-cc-")
    prj = os.path.join(d, "pcb-b-compute"); os.makedirs(os.path.join(prj, "out"))
    net = os.path.join(prj, "out", "pcb-b-compute.net")
    open(net, "w").write('(export (version E)\n  (nets\n    (net (code "1") (name "/X")\n'
                         '      (node (ref "U1") (pin "1"))\n    )\n  )\n)\n')

    def run():
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_contracts.py"), d],
                           capture_output=True, text=True, timeout=180, cwd=d)
        return r.stdout + r.stderr

    out = run()          # DEFECTIVE fixture: no provenance beside the netlist
    assert "UNKNOWN GENERATOR for pcb-b-compute" in out, out[-600:]
    assert "B absent" in out or "B," in out or "B " in out, "the board was not counted as unjudged:\n%s" % out[-400:]

    P.write(net, "b", TOOLS)   # ACCEPTABLE fixture: written by this tree's own generator
    out = run()
    assert "UNKNOWN GENERATOR for pcb-b-compute" not in out, out[-600:]


def t_the_netlist_export_writes_the_sidecar():
    """The producer side: build_sch.sh must write it, or nothing ever has provenance and every contract is
    INCONCLUSIVE for ever."""
    src = open(os.path.join(TOOLS, "build_sch.sh"), encoding="utf-8").read()
    i = src.index("export netlist")
    j = src.index("sch_prov.py")
    assert i < j, "the sidecar is written before the netlist it describes"
    assert '"$N"' in src[i:src.index("\n", j)], "the stem must be passed whole; sch_prov resolves the letter"


def t_the_letter_comes_from_the_board_table_and_not_from_the_stems_spelling():
    """The first run of the one-tree sweep, 16 September 2026: board E's netlist is `pcb-e1-dock.net`, the
    second field of the stem is `e1`, and taking it verbatim asked for a `gen_sch_e1.py` that does not exist.
    The provenance was written with no generator sha and every contract naming board E read UNKNOWN GENERATOR,
    which is the false-INCONCLUSIVE twin of the false-FAIL this whole change exists to remove."""
    assert P.letter_for("pcb-e1-dock") == "e", "board E's stem was not resolved through the board table"
    assert P.generator_sha(P.letter_for("pcb-e1-dock")) is not None, "board E has no generator identity"
    for stem, want in (("pcb-a-power", "a"), ("pcb-b-compute", "b"), ("pcb-c-display", "c"),
                       ("pcb-d-aprs", "d"), ("pcb-p-pack", "p")):
        assert P.letter_for(stem) == want, (stem, P.letter_for(stem))
    # a stem the table does not carry keeps its field verbatim: the bare dock block is not board E
    assert P.letter_for("pcb-e5-block") == "e5"
    assert P.generator_sha("e5") is None, "a board with no schematic generator claimed one"


# ---------------------------------------------------------------- the identity covers every input (26 September 2026)
# Finding W7-F4 (MESHSAT-1357): the identity hashed gen_sch_<x>.py, kisch.py and intent.py only. Commit c26f6a22
# (15 September) rewrote all six schematics while changing only schlayout.py and gen_sch_b.py, so for the five
# boards other than B every sidecar kept reading CURRENT over a schematic its generator identity did not describe.
# schlayout.py writes the connectivity-bearing wires; idc_pads.py picks the IDC land; the footprint generators and
# meshsat.pretty are the lands the netlist names; boards/<x>.json carries the generator environment (gen_env).

def _full_tree():
    """A tools tree beside its own footprint library, shaped like v2/ecad: <root>/tools and <root>/meshsat.pretty."""
    root = tempfile.mkdtemp(prefix="prov-full-")
    t = os.path.join(root, "tools"); os.makedirs(os.path.join(t, "boards"))
    open(os.path.join(t, "gen_sch_b.py"), "w").write("import kisch, schlayout, idc_pads\nfrom intent import rails\n")
    open(os.path.join(t, "kisch.py"), "w").write("import intent\n")
    open(os.path.join(t, "intent.py"), "w").write("# the rails\n")
    open(os.path.join(t, "schlayout.py"), "w").write("import kisch\n# the wires\n")
    open(os.path.join(t, "idc_pads.py"), "w").write("# the IDC land\n")
    open(os.path.join(t, "gen_footprints_idc.py"), "w").write("# writes meshsat.pretty/IDC.kicad_mod\n")
    open(os.path.join(t, "route_one.sh"), "w").write("# a router launcher the schematic never reads\n")
    open(os.path.join(t, "check_pcb_b.py"), "w").write("# a board gate the schematic never reads\n")
    open(os.path.join(t, "boards", "b.json"), "w").write('{"name": "pcb-b-compute", "gen_env": {"IDC_PADS": "smd"}}\n')
    open(os.path.join(t, "boards", "c.json"), "w").write('{"name": "pcb-c-display"}\n')
    os.makedirs(os.path.join(root, "meshsat.pretty"))
    open(os.path.join(root, "meshsat.pretty", "IDC.kicad_mod"), "w").write("(footprint \"IDC\")\n")
    return t


def _moves(edit):
    """Does `edit(tools_dir)` move board B's generator identity?"""
    t = _full_tree(); before = P.generator_sha("b", t); edit(t); return P.generator_sha("b", t) != before


def t_a_layout_engine_change_moves_the_identity():
    """DEFECTIVE before the fix: schlayout.py was outside the identity (the c26f6a22 shape)."""
    assert _moves(lambda t: open(os.path.join(t, "schlayout.py"), "a").write("# a wire moved\n")), \
        "a change to schlayout.py, which writes the wires, left the generator identity where it was"


def t_the_idc_land_chooser_moves_the_identity():
    assert _moves(lambda t: open(os.path.join(t, "idc_pads.py"), "a").write("# THT now\n")), \
        "a change to idc_pads.py left the generator identity where it was"


def t_a_footprint_generator_or_a_library_land_moves_the_identity():
    assert _moves(lambda t: open(os.path.join(t, "gen_footprints_idc.py"), "a").write("# pitch\n")), \
        "a change to a footprint generator left the generator identity where it was"
    assert _moves(lambda t: open(os.path.join(os.path.dirname(t), "meshsat.pretty", "IDC.kicad_mod"), "a")
                  .write("(pad 1)\n")), "a change to a land in meshsat.pretty left the generator identity where it was"


def t_the_board_table_moves_its_own_board_s_identity_and_not_another_s():
    assert _moves(lambda t: open(os.path.join(t, "boards", "b.json"), "w").write('{"name": "pcb-b-compute", "gen_env": {"IDC_PADS": "tht"}}\n')), \
        "a change to boards/b.json (the generator environment) left board B's identity where it was"
    assert not _moves(lambda t: open(os.path.join(t, "boards", "c.json"), "w").write('{"name": "pcb-c-display", "x": 1}\n')), \
        "board C's table moved board B's identity"


def t_a_routing_only_edit_of_the_board_table_leaves_the_identity_alone():
    """DEFECTIVE in the first widened identity: the WHOLE boards/b.json was hashed, so the layer decisions of
    25 September (copper_layers, stackup, return reach) staled every sidecar although no generator reads them.
    ACCEPTABLE: the same edit now leaves the identity where it was; a gen_env edit still moves it (above)."""
    assert not _moves(lambda t: open(os.path.join(t, "boards", "b.json"), "w").write(
        '{"name": "pcb-b-compute", "gen_env": {"IDC_PADS": "smd"}, "copper_layers": 8, "phase": "B22"}\n')), \
        "a routing-only edit of boards/b.json moved board B's schematic identity"
    assert not _moves(lambda t: open(os.path.join(t, "boards", "b.json"), "w").write(
        '{"gen_env": {"IDC_PADS": "smd"},   "name": "pcb-b-compute"}\n')), "a re-spelling of the same table moved it"
    assert _moves(lambda t: open(os.path.join(t, "boards", "b.json"), "w").write('{"name": ')), \
        "a board table that does not parse read as an empty environment"


def _closure(letter):
    return [f for f in P.generator_files(letter) if f.endswith(".py")]


def t_no_generator_reads_the_board_table_except_through_gen_env():
    """The identity takes one field of boards/<x>.json because that field is the only channel from the table to a
    schematic. This holds it: no module in any real generator's import closure names the table as a path (a string
    that is exactly "boards", or a whole string shaped like boards/<x>.json), read by parsing, never by grep, so a
    sentence that mentions the table in a rail's note is not a read of it."""
    import ast, glob, re
    shape = re.compile(r"(?:\.\./)?(?:tools/)?boards/[\w%{}<>.-]*\.json")
    bad = []
    for gen in sorted(glob.glob(os.path.join(TOOLS, "gen_sch_*.py"))):
        letter = os.path.basename(gen)[len("gen_sch_"):-3]
        for f in _closure(letter):
            for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and (n.value == "boards" or shape.fullmatch(n.value)):
                    bad.append("%s (in %s's closure) line %s: %r" % (os.path.basename(f), letter, n.lineno, n.value))
    assert not bad, "a schematic input reads the board table directly, so gen_env alone is not its channel: " + "; ".join(bad[:6])


def t_every_driver_that_regenerates_a_schematic_hands_it_gen_env():
    """full.sh has handed the generator the table's gen_env since 12 September; gate_sweep.sh regenerated without
    it (26 September 2026, latent: no board declares one). Read as the shell reads the command: the words of the
    line that runs gen_sch_$L.py must include `env $GENV`, and GENV must be read from the table's gen_env."""
    import shlex
    for drv in ("full.sh", "gate_sweep.sh"):
        src = open(os.path.join(TOOLS, drv), encoding="utf-8").read().replace("\\\n", " ")   # continuation lines
        runs = [ln for ln in src.splitlines() if "gen_sch_$L.py" in ln and not ln.lstrip().startswith(("#", "for "))]
        assert runs, "%s runs no schematic generator this test can read" % drv
        for ln in runs:
            w = shlex.split(ln, comments=True)
            assert "env" in w and w[w.index("env") + 1] == "$GENV", "%s runs the generator without gen_env: %s" % (drv, ln.strip())
        sets = [ln for ln in src.splitlines() if re.search(r"GENV=\"\$\(python3", ln)]
        assert sets and all("gen_env" in ln for ln in sets), "%s does not read GENV from the board table's gen_env" % drv


def t_a_tool_the_schematic_never_reads_leaves_the_identity_alone():
    """ACCEPTABLE, before and after: the identity is the inputs of the schematic, not the whole tools tree."""
    assert not _moves(lambda t: open(os.path.join(t, "route_one.sh"), "a").write("# a router flag\n"))
    assert not _moves(lambda t: open(os.path.join(t, "check_pcb_b.py"), "a").write("# a gate threshold\n"))


def t_a_stale_sidecar_names_the_input_that_moved():
    t = _full_tree()
    d = tempfile.mkdtemp(prefix="prov-why-"); os.makedirs(os.path.join(d, "out"))
    net = os.path.join(d, "out", "pcb-b-compute.net"); open(net, "w").write("(export)\n")
    P.write(net, "b", t)
    ok, why = P.current(net, "b", t)
    assert ok, why
    open(os.path.join(t, "schlayout.py"), "a").write("# a wire moved\n")
    ok, why = P.current(net, "b", t)
    assert not ok and "schlayout.py" in why, why


def t_a_sidecar_written_under_the_narrow_identity_is_not_current_and_says_so():
    """The six committed sidecars were written under the three-file identity. They say nothing about schlayout.py,
    so they cannot be current under the wider one; the message says what to do rather than only 'different'."""
    t = _full_tree()
    d = tempfile.mkdtemp(prefix="prov-old-"); os.makedirs(os.path.join(d, "out"))
    net = os.path.join(d, "out", "pcb-b-compute.net"); open(net, "w").write("(export)\n")
    import json as _j
    _j.dump({"letter": "b", "netlist": "pcb-b-compute.net", "generator_sha": "da28353cb4d2526f",
             "generator_files": ["gen_sch_b.py", "kisch.py", "intent.py"]}, open(P.path_for(net), "w"))
    ok, why = P.current(net, "b", t)
    assert not ok and "three-file identity" in why, why
