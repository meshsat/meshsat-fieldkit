#!/usr/bin/env python3
"""A passing fixture and a failing fixture per gate: the admission rule for the stage catalogue.

Stage 0d of the control-plane programme (MESHSAT-862, 11 September 2026). The reason is the one the record
keeps paying for: a gate that quietly stops refusing looks exactly like a gate that has nothing to refuse.
Two of this project's halts were structurally inert for days (the pair matcher's `if !` tested the wrong
command; the deliverable DRC histogram's pattern was a grep error), and the only thing that would have caught
either is an input that MUST make the gate say no.

So a gate is admitted to the catalogue when both fixtures exist. `t_every_gate_has_both_fixtures` is what
makes that a rule rather than an intention: a gate with no fixture here, and no line in FIXTURE_DEBT saying
why and what it needs, fails this file.

Gates that need a board are in test_board_gates.py and skip where pcbnew is absent. This file holds the ones
that judge a file, a folder or a number, so they run on every host including the runner.
"""
import os, sys, csv, json, zipfile, tempfile, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Gates whose fixtures are owed, each with what it needs. A line here is a declaration, not an excuse: it is
# read by the rule below and printed, so the debt is visible in every test run rather than remembered.
FIXTURE_DEBT = {
    "dc_drop.py": "needs pcbnew and numpy and a board with a rail; belongs in test_board_gates.py",
    "place_audit.py": "needs pcbnew and a board with a fine-pitch part; belongs in test_board_gates.py",
    "intent_checks.py": "needs pcbnew and an intent file beside the board; belongs in test_board_gates.py",
    "pruned_gate.py": "needs pcbnew and a routed board; the no-list path is covered below without it",
    "copper_checks.py": "a library called with the caller's check(), exercised through the board gates",
}

# Gates with fixtures elsewhere, so that this file's rule sees the whole catalogue.
ELSEWHERE = {
    "hardset.py": "test_hardset.py",
    "erc_gate.py": "test_erc_gate.py",
    "check_zone_nets.py": "test_board_gates.py",
    "check_pcb_a.py": "test_board_gates.py", "check_pcb_b.py": "test_board_gates.py",
    "check_pcb_c.py": "test_board_gates.py", "check_pcb_d.py": "test_board_gates.py",
    "check_pcb_e.py": "test_board_gates.py", "check_pcb_p.py": "test_board_gates.py",
}


def _run(argv, cwd=None, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run([sys.executable] + argv, cwd=cwd, capture_output=True, text=True, timeout=300, env=e)
    return p.returncode, p.stdout + p.stderr


def _verdict(d, tool):
    return json.load(open(os.path.join(d, "out", "%s.verdict.json" % tool)))


# ---------------------------------------------------------------- verify_deliverable

def _deliverable(d, name="brd", ncu=2, break_item=None):
    """A minimal two-layer deliverable that satisfies every property the gate asserts."""
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(d, "meshsat.pretty"), exist_ok=True)
    open(os.path.join(d, "meshsat.pretty", "X.kicad_mod"), "w").write("(footprint)")
    for it in ("README-fab.txt", "%s-drc.rpt" % name, "%s-schematic.pdf" % name, "%s-render-top.png" % name,
               "%s-render-bottom.png" % name, "%s-1to1-top.pdf" % name, "%s-1to1-bottom-mirrored.pdf" % name,
               "%s.kicad_pcb" % name, "%s.kicad_sch" % name, "%s.kicad_pro" % name, "%s-bom.status" % name):
        open(os.path.join(d, it), "w").write("x\n")
    z = zipfile.ZipFile(os.path.join(d, "%s-gerbers.zip" % name), "w")
    for tag in ("F_Cu.gtl", "B_Cu.gbl", "F_Mask.gts", "B_Mask.gbs", "F_Paste.gtp", "B_Paste.gbp",
                "F_Silkscreen.gto", "B_Silkscreen.gbo", "Edge_Cuts.gm1"):
        z.writestr("%s-%s" % (name, tag), "G04*\n")
    z.writestr("%s.drl" % name, "M48\n"); z.writestr("%s-drl_map.gbr" % name, "G04*\n"); z.close()
    with open(os.path.join(d, "%s-cpl.csv" % name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerow(["R1", "1.0mm", "2.0mm", "Top", "0"]); w.writerow(["C1", "3.0mm", "4.0mm", "Bottom", "90"])
    with open(os.path.join(d, "%s-bom.csv" % name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        w.writerow(["10k", "R1", "R_0603", "C25804"]); w.writerow(["100n", "C1", "C_0603", "C14663"])
    if break_item: os.remove(os.path.join(d, break_item % name if "%s" in break_item else break_item))
    return d


def t_verify_deliverable_passes_a_complete_folder():
    d = _deliverable(tempfile.mkdtemp(prefix="vd-pass-"))
    rc, out = _run([os.path.join(TOOLS, "verify_deliverable.py"), d, "brd", "2"], cwd=d)
    assert rc == 0, out
    v = _verdict(d, "verify_deliverable")
    assert v["verdict"] == "PASS" and v["denominator"] > 20, v


def t_verify_deliverable_refuses_a_folder_missing_one_item():
    d = _deliverable(tempfile.mkdtemp(prefix="vd-fail-"), break_item="%s-drc.rpt")
    rc, out = _run([os.path.join(TOOLS, "verify_deliverable.py"), d, "brd", "2"], cwd=d)
    assert rc == 1, out
    v = _verdict(d, "verify_deliverable")
    assert v["verdict"] == "FAIL" and v["counts"]["fail"] >= 1, v
    assert any("drc.rpt" in e for e in v["evidence"]), v["evidence"]


def t_verify_deliverable_refuses_a_gerber_zip_short_of_a_copper_layer():
    """The 3 September defect the gate was written for: the exporter dropped In1 and In2 and the zip still
    looked like a zip. Declaring four copper layers against a two-layer zip must fail."""
    d = _deliverable(tempfile.mkdtemp(prefix="vd-cu-"))
    rc, out = _run([os.path.join(TOOLS, "verify_deliverable.py"), d, "brd", "4"], cwd=d)
    assert rc == 1, out
    assert any("copper layers" in e for e in _verdict(d, "verify_deliverable")["evidence"]), out


def t_verify_deliverable_refuses_a_blocked_lcsc_code():
    d = _deliverable(tempfile.mkdtemp(prefix="vd-blk-"))
    blocked = [l.split()[0] for l in open(os.path.join(TOOLS, "lcsc-blocked.txt"))
               if l.strip() and not l.startswith("#")]
    if not blocked: raise Skip("lcsc-blocked.txt is empty on this tree")
    with open(os.path.join(d, "brd-bom.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        w.writerow(["10k", "R1", "R_0603", blocked[0]]); w.writerow(["100n", "C1", "C_0603", "C14663"])
    rc, out = _run([os.path.join(TOOLS, "verify_deliverable.py"), d, "brd", "2"], cwd=d)
    assert rc == 1, out
    assert any("proved wrong" in e for e in _verdict(d, "verify_deliverable")["evidence"]), out


# ---------------------------------------------------------------- lcsc_fill

def _bom(d, rows, allow=None):
    os.makedirs(os.path.join(d, "out", "jlc"), exist_ok=True)
    p = os.path.join(d, "out", "jlc", "brd-bom.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"]); w.writerows(rows)
    if allow is not None: open(os.path.join(d, "lcsc-allow.txt"), "w").write(allow)
    return p


def t_lcsc_fill_passes_a_bom_whose_codes_are_all_good():
    d = tempfile.mkdtemp(prefix="lf-pass-")
    p = _bom(d, [["10k", "R1", "R_0603", "C25804"], ["100n", "C1", "C_0603", "C14663"]], allow="")
    rc, out = _run([os.path.join(TOOLS, "lcsc_fill.py"), p], cwd=d)
    assert rc == 0, out
    v = _verdict(d, "lcsc_fill")
    assert v["verdict"] == "PASS" and v["denominator"] == 2, v


def t_lcsc_fill_refuses_a_code_the_record_has_rejected():
    """This is the gate that could not fire until 11 September 2026: lcsc_fill only ever filled BLANKS and
    never looked at a code that was already there, which is how all 23 blocked codes reached shipped BOMs."""
    d = tempfile.mkdtemp(prefix="lf-blk-")
    blocked = [l.split()[0] for l in open(os.path.join(TOOLS, "lcsc-blocked.txt"))
               if l.strip() and not l.startswith("#")]
    if not blocked: raise Skip("lcsc-blocked.txt is empty on this tree")
    p = _bom(d, [["something", "U1", "SOIC-8", blocked[0]]], allow="")
    rc, out = _run([os.path.join(TOOLS, "lcsc_fill.py"), p], cwd=d)
    assert rc == 1, out
    v = _verdict(d, "lcsc_fill")
    assert v["verdict"] == "FAIL" and v["counts"]["rejected_code"] == 1, v


def t_lcsc_fill_refuses_a_blank_that_the_project_has_not_allowed():
    d = tempfile.mkdtemp(prefix="lf-blank-")
    p = _bom(d, [["a part nobody mapped", "U9", "QFN-99", ""]], allow="")
    rc, out = _run([os.path.join(TOOLS, "lcsc_fill.py"), p], cwd=d)
    assert rc == 1, out
    assert _verdict(d, "lcsc_fill")["counts"]["blank_over_allowance"] == 1, out


def t_lcsc_fill_accepts_a_blank_the_project_explains():
    d = tempfile.mkdtemp(prefix="lf-allow-")
    p = _bom(d, [["a bench-fitted module", "U9", "QFN-99", ""]],
             allow="bench-fitted   # fitted on the bench, never by JLC\n")
    rc, out = _run([os.path.join(TOOLS, "lcsc_fill.py"), p], cwd=d)
    assert rc == 0, out
    v = _verdict(d, "lcsc_fill")
    assert v["verdict"] == "PASS" and v["counts"]["blank_over_allowance"] == 0, v


# ---------------------------------------------------------------- impedance_check (the analytic core)

def t_impedance_selftest_passes():
    rc, out = _run([os.path.join(TOOLS, "impedance_check.py"), "--selftest"])
    assert rc == 0, out
    assert "PASS" in out, out


def t_impedance_refuses_a_board_with_no_stackup():
    """INCONCLUSIVE, not FAIL: no stackup means no geometry was judged. It still blocks (exit 3)."""
    try: import pcbnew  # noqa: F401
    except Exception as e: raise Skip("no pcbnew here (%s)" % type(e).__name__)
    d = tempfile.mkdtemp(prefix="imp-")
    b = os.path.join(d, "brd.kicad_pcb")
    open(b, "w").write('(kicad_pcb (version 20240108) (generator "test"))\n')
    rc, out = _run([os.path.join(TOOLS, "impedance_check.py"), b], cwd=d)
    assert rc == 3, (rc, out)
    assert _verdict(d, "impedance_check")["verdict"] == "INCONCLUSIVE", out


# ---------------------------------------------------------------- pruned_gate, the path that needs no board

def t_pruned_gate_is_inconclusive_when_the_prune_step_did_not_run():
    """escape_prune.py always writes that file, "# none pruned" included. Its absence used to return 0."""
    d = tempfile.mkdtemp(prefix="pg-")
    rc, out = _run([os.path.join(TOOLS, "pruned_gate.py"), os.path.join(d, "brd.kicad_pcb"),
                    os.path.join(d, "absent-pruned.txt")], cwd=d)
    assert rc == 3, (rc, out)
    v = _verdict(d, "pruned_gate")
    assert v["verdict"] == "INCONCLUSIVE" and v["denominator"] == 0, v


# ---------------------------------------------------------------- check_contracts

def _netlist(path, nets):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = ["(export (version \"E\")", "  (nets"]
    for i, (name, nodes) in enumerate(nets.items(), 1):
        body.append('    (net (code "%d") (name "%s")' % (i, name))
        for ref, pin in nodes: body.append('      (node (ref "%s") (pin "%s"))' % (ref, pin))
        body.append("    )")
    body += ["  )", ")"]
    open(path, "w").write("\n".join(body) + "\n")


def t_check_contracts_is_inconclusive_with_no_netlist_at_all():
    """A contract set that evaluated nothing has found nothing wrong, which is not agreement."""
    d = tempfile.mkdtemp(prefix="cc-")
    rc, out = _run([os.path.join(TOOLS, "check_contracts.py"), d], cwd=d)
    v = _verdict(d, "check_contracts")
    assert rc in (1, 3), (rc, out)
    assert v["denominator"] == v["counts"]["fail"] + v["counts"]["pass"], v


def t_check_contracts_counts_every_contract_it_evaluated():
    """The denominator is the point: 0 FAIL of 37 and 0 FAIL of 0 used to print the same way."""
    d = tempfile.mkdtemp(prefix="cc2-")
    _netlist(os.path.join(d, "pcb-d-aprs", "out", "pcb-d-aprs.net"),
             {"TX_INHIBIT_n": {("Q3", "1"), ("J_MEZZ1", "4")}, "GND": {("Q3", "2")}})
    rc, out = _run([os.path.join(TOOLS, "check_contracts.py"), d], cwd=d)
    v = _verdict(d, "check_contracts")
    assert v["denominator"] > 0, v
    assert v["counts"]["fail"] + v["counts"]["pass"] == v["denominator"], v


# ---------------------------------------------------------------- the admission rule itself

def t_every_gate_has_both_fixtures():
    """A gate is in the catalogue when an input that must fail it and an input that must pass it both exist.

    This reads the test files rather than a list of intentions: a gate named by no test, and not declared in
    FIXTURE_DEBT with what it needs, fails here. That is what stops the catalogue from growing a gate nobody
    ever proved can say no."""
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import test_verdict_channel as tvc
    covered = set()
    for fn in sorted(os.listdir(here)):
        if not (fn.startswith("test_") and fn.endswith(".py")): continue
        body = open(os.path.join(here, fn), errors="replace").read()
        for g in tvc.GATES:
            stem = g[:-3]
            # a mention inside FIXTURE_DEBT or ELSEWHERE is a declaration, not a fixture
            if stem in body.replace("FIXTURE_DEBT", "").replace("ELSEWHERE", ""): covered.add(g)
    missing = [g for g in tvc.GATES if g not in covered and g not in FIXTURE_DEBT]
    assert not missing, "these gates have no fixture and no declared debt: %s" % missing
    for g, why in sorted(FIXTURE_DEBT.items()):
        print("       fixture owed: %-22s %s" % (g, why))


# ---------------------------------------------------------------- the pre-router's own preconditions

def t_the_pre_router_refuses_a_board_whose_pair_classes_it_cannot_read():
    """A pre-router that finds no pairs and reports success is a silent pass, and it is easy to hit.

    Measured on the VM, 11 September 2026: run on `out/<name>-placed.kicad_pcb`, which has no project file beside it,
    the tool printed "0 of 0 pairs laid" and exited 0 in one map mode and died with an AttributeError in the other.
    The pair classes live in the project file; a board without one has no pairs BY CONSTRUCTION, which is not the same
    as having laid them all."""
    try: import pcbnew  # noqa: F401
    except Exception as e: raise Skip("no pcbnew here (%s)" % type(e).__name__)
    import json as _json
    d = tempfile.mkdtemp(prefix="pp-")
    b = os.path.join(d, "brd.kicad_pcb")
    open(b, "w").write('(kicad_pcb (version 20240108) (generator "test"))\n')

    rc, out = _run([os.path.join(TOOLS, "pair_preroute.py"), b, "--classes", "USB"], cwd=d)
    assert rc != 0, (rc, out)
    assert "no project file" in out, out
    assert "0 of 0 pairs laid" not in out, "it must refuse, not report an empty success"

    _json.dump({"net_settings": {"classes": [], "netclass_assignments": None}}, open(os.path.join(d, "brd.kicad_pro"), "w"))
    rc, out = _run([os.path.join(TOOLS, "pair_preroute.py"), b, "--classes", "USB"], cwd=d)
    assert rc != 0, (rc, out)
    assert "no netclass_assignments" in out, out
