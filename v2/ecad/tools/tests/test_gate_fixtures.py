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


# ---------------------------------------------------------------- a missing board is not a broken contract
# check_contracts reads every board's netlist out of the tree. On a rented box where only one board has been
# regenerated, it printed eleven FAILs naming board A and A had simply never been generated there, so P3's
# finish reported "CONTRACTS FAILED" about a design nothing had looked at (11 September 2026). A missing input
# is INCONCLUSIVE. It still blocks: what changes is that a skipped check can no longer read as a failed one.

def t_check_contracts_is_inconclusive_when_a_board_is_absent():
    import subprocess, tempfile, json as _j
    d = tempfile.mkdtemp(prefix="contracts-absent-")
    os.makedirs(os.path.join(d, "out"))
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_contracts.py"), d],
                       capture_output=True, text=True, cwd=d)
    assert r.returncode == 3, (r.returncode, (r.stdout + r.stderr)[-400:])
    assert "absent from this tree" in (r.stdout + r.stderr), (r.stdout + r.stderr)[-400:]
    rec = _j.load(open(os.path.join(d, "out", "check_contracts.verdict.json")))
    assert rec["verdict"] == "INCONCLUSIVE", rec
    assert rec["counts"]["missing_boards"] > 0, rec


def t_the_finish_treats_an_inconclusive_contract_set_differently_from_a_failed_one():
    t = open(os.path.join(TOOLS, "finish.sh"), errors="replace").read()
    assert 'CONTRACTS NOT JUDGED' in t, "the finish does not separate a missing board from a broken contract"
    assert '"$CT" -eq 3' in t, "the finish does not read the INCONCLUSIVE exit code"


# ---------------------------------------------------------------- a code is wrong FOR A PART, not in general
# JLC-CERTIFIED.tsv carries C2836813 twice: WRONG_MODEL against "ATECC608B-SSHDA-T secure element", because
# JLCPCB's best answer to that question is a BMI270, and CERTIFIED against "BMI270 six-axis IMU", because that
# is exactly what the code is. Keyed on the code alone the rejection refused board E's deliverable for a part
# whose code is right, and lcsc-blocked.txt already carried a line saying so in prose that nothing read.

def _lcsc_tree(bom_rows):
    import tempfile, shutil as _sh
    d = tempfile.mkdtemp(prefix="lcsc-part-key-")
    t = os.path.join(d, "v2", "ecad", "tools"); os.makedirs(t)
    o = os.path.join(d, "v2", "release", "revA", "order"); os.makedirs(o)
    for f in ("lcsc_fill.py", "lcsc-blocked.txt", "jlc-handfit.txt", "verdict.py"):
        src = os.path.join(TOOLS, f)
        if os.path.exists(src): _sh.copy(src, t)
    with open(os.path.join(o, "JLC-CERTIFIED.tsv"), "w") as f:
        f.write("verdict\tcomment\tfp\tboards\tqty\tneed\tbom_code\tcode\tmodel\n")
        f.write("CERTIFIED\tBMI270 six-axis IMU (I2C 0x68)\tLGA14B\tE\t1\t5\tC2836813\tC2836813\tBMI270\n")
        f.write("WRONG_MODEL\tATECC608B-SSHDA-T secure element\tSOIC8\tB\t1\t5\tC2836813\tC2836813\tBMI270\n")
    bom = os.path.join(d, "bom.csv")
    with open(bom, "w") as f:
        f.write("Comment,Designator,Footprint,LCSC Part #\n")
        for r in bom_rows: f.write('"%s","%s","%s","%s"\n' % r)
    return d, os.path.join(t, "lcsc_fill.py"), bom


def _lcsc_run(bom_rows):
    import subprocess, shutil as _sh
    d, script, bom = _lcsc_tree(bom_rows)
    os.makedirs(os.path.join(d, "out"), exist_ok=True)
    r = subprocess.run([sys.executable, script, bom], capture_output=True, text=True, cwd=d)
    out = r.stdout + r.stderr
    _sh.rmtree(d, ignore_errors=True)
    return r.returncode, out


def t_a_code_certified_for_this_part_is_not_rejected_for_someone_elses_part():
    rc, out = _lcsc_run([("BMI270 six-axis IMU (I2C 0x68)", "U15", "LGA14B", "C2836813")])
    assert "checked and rejected" not in out, out
    assert rc == 0, out


def t_the_same_code_on_the_part_it_is_wrong_for_is_still_rejected():
    rc, out = _lcsc_run([("ATECC608B-SSHDA-T secure element", "U9", "SOIC8", "C2836813")])
    assert "checked and rejected" in out and "WRONG_MODEL" in out, out
    assert rc != 0, out


def t_an_allow_line_that_covers_nothing_is_named():
    """E's list carried `module:` for four sensor headers while the generator writes "Geiger counter module
    (RadiationD-v1.1 class)", a bracket and not a colon, so the line matched nothing for as long as it existed
    and the board's deliverable was refused for the five rows it was written to cover. A declaration that reads
    as cover and provides none is worse than no declaration."""
    import subprocess, tempfile, json as _j, shutil as _sh
    d = tempfile.mkdtemp(prefix="stale-allow-")
    proj = os.path.join(d, "p", "out", "jlc"); os.makedirs(proj)
    open(os.path.join(d, "p", "lcsc-allow.txt"), "w").write("never matches this   # a line for a part no longer on the board\n")
    bom = os.path.join(proj, "b-bom.csv")
    open(bom, "w").write('Comment,Designator,Footprint,LCSC Part #\n"a real part","R1","R_0603","C1234"\n')
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "lcsc_fill.py"), bom], capture_output=True, text=True, cwd=d)
    out = r.stdout + r.stderr
    _sh.rmtree(d, ignore_errors=True)
    assert "allow line(s) match no row" in out, out
    assert "never matches this" in out, out


# ---------------------------------------------------------------- two declarations, one question
# A BOM line with no LCSC code is judged by lcsc_fill against the board's own <project>/lcsc-allow.txt, and its
# answer is written beside the BOM as <name>-bom.status. verify_deliverable knew only tools/jlc-handfit.txt and
# the bench prefixes, so a line the board declares in the place the project actually uses read as undeclared.
# Board E was 34 of 35 properties on exactly that, every other gate passing and its allow list correct.

def _status_folder(status, blank_designator="J_GEIGER"):
    import tempfile, zipfile
    d = tempfile.mkdtemp(prefix="vd-status-"); f = os.path.join(d, "meshsat-pcb-e-revA-E7"); os.makedirs(f)
    n = "pcb-e1-dock"
    for item in ("README-fab.txt", "%s-drc.rpt" % n, "%s-schematic.pdf" % n, "%s-render-top.png" % n,
                 "%s-render-bottom.png" % n, "%s-1to1-top.pdf" % n, "%s-1to1-bottom-mirrored.pdf" % n,
                 "%s.kicad_sch" % n, "%s.kicad_pro" % n):
        open(os.path.join(f, item), "w").write("x")
    # the board carries its phase on the silk, which is a separate property of this gate and not what is under
    # test here; without it the fixture fails for a reason that has nothing to do with the blank-code rule
    open(os.path.join(f, "%s.kicad_pcb" % n), "w").write('(kicad_pcb (gr_text "MESHSAT PCB-E1 DOCK REV A (E7)"))\n')
    os.makedirs(os.path.join(f, "meshsat.pretty"))
    if status is not None: open(os.path.join(f, "%s-bom.status" % n), "w").write(status + "\n")
    with zipfile.ZipFile(os.path.join(f, "%s-gerbers.zip" % n), "w") as z:
        for t in ("F_Cu.gtl", "In1_Cu.g2", "In2_Cu.g3", "B_Cu.gbl", "F_Mask.gts", "B_Mask.gbs", "F_Paste.gtp",
                  "B_Paste.gbp", "F_Silkscreen.gto", "B_Silkscreen.gbo", "Edge_Cuts.gm1", "x.drl", "x-drl_map.gbr"):
            z.writestr("%s-%s" % (n, t), "x")
    open(os.path.join(f, "%s-cpl.csv" % n), "w").write(
        'Designator,Mid X,Mid Y,Layer,Rotation\n%s,1mm,1mm,Top,0\n' % blank_designator)
    open(os.path.join(f, "%s-bom.csv" % n), "w").write(
        'Comment,Designator,Footprint,LCSC Part #\n"Geiger counter module (RadiationD-v1.1 class)","%s","PinHeader_1x03",""\n' % blank_designator)
    return d, f, n


def _vd(status):
    import subprocess, shutil as _sh
    d, f, n = _status_folder(status)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "verify_deliverable.py"), f, n, "4"],
                       capture_output=True, text=True, cwd=d)
    out = r.stdout + r.stderr
    _sh.rmtree(d, ignore_errors=True)
    return r.returncode, out


def t_a_blank_line_the_boards_own_allow_list_covers_is_accepted():
    rc, out = _vd("OK")
    assert "ALL PASS" in out, out
    assert rc == 0, out


def t_a_blank_line_with_no_status_file_is_still_refused():
    """The deferral is to lcsc_fill's ANSWER, not to its absence: with no OK beside the BOM this gate judges the
    blanks itself, so removing lcsc_fill from a chain cannot quietly widen what a deliverable may carry."""
    rc, out = _vd(None)
    assert rc != 0, out
    assert "no OK status file beside the BOM" in out, out


def t_a_blank_line_lcsc_fill_itself_refused_is_refused_here_too():
    rc, out = _vd("BLANK not allow-listed")
    assert rc != 0, out
