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
import os, sys, json, shutil, tempfile

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
    assert "cut -d- -f2" in src, "the letter must come from the stem, not from a table that can drift"
