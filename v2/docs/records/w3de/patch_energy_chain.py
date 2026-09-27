#!/usr/bin/env python3
"""DRAFT for the owner of v2/ecad/tools/pcb_energy_chain.yaml and tests/test_energy_chain.py (w3de, 27 September 2026):
the SHORE_INPUT stage carries the vehicle path's figure since F-IN-02, and a test holds the two together.

F-IN-02 (26 September 2026, gen_sch_e.py, R4E-02) set the vehicle and shore entry's current at what its limiter lets
through: the LM5069 U6 with R19 = 10 mOhm limits at VCL / RS, 48.5 / 55 / 61.5 mV (TI SNVS452G), so 4.85 to 6.15 A,
and 6.15 A (VCL max) is what the path carries continuously without ever limiting; board E declares its five vehicle
segments at _VEH_T, _VEH_P = 6.15, 6.15. The chain's SHORE_INPUT stage still said 8.0 A continuous and 10.0 A peak,
the figures of before the hot-swap existed, so BAT-002 and PWR-003 judged F1 at 8.0 A of the 8.0 A the ATOF table
allows at 65 C ("no margin"), a reading about a current the path cannot carry. The stage's note also named an SMCJ33A
behind the fuse; board E's clamps were corrected at faf8c981 (D10 SMCJ40CA at the entry, in front of the ideal-diode
FET; D1 SMCJ40A behind it). A third hunk corrects the DOCK_BLOCK stage's citation of the Mill-Max page, which named
v2/vendor/precidip/ (the Preci-Dip signal contacts); the page is filed at v2/vendor/connectors/.

The test change: the fixture that read "F1 carries 8.0 A where atof287 allows 8.0 A" and "no margin" now reads the
corrected stage (6.15 A, printed "6.2 A" by the gate's %.1f, of 8.0 A: margin left), and a new rule parses board E's
generator (ast, never a text search) for _VEH_T and _VEH_P and holds the stage to them, so the two cannot drift apart
again the way they did for a day. The committed SHORE_INPUT stage was the only thing that exercised energy_chain.py's
at-limit wording ("no margin against the maker's own figure"), so a synthetic FUSED-stage fixture now holds it on both
sides of the 95 percent line (pass 2 of the independent check, 27 September 2026): a 10 A atof287 fuse at 8.0 A and
56 C ambient, which the table reads at its 65 C column as exactly 8.0 A, must carry the wording, and the same fuse at
7.5 A (under 95 percent of 8.0) must not. Deleting the _margin branch fails the first.

Usage: patch_energy_chain.py <tree root holding v2/ecad>"""
import os, sys
root = os.path.join(sys.argv[1], "v2", "ecad", "tools")

def edit(rel, pairs, check=None):
    p = os.path.join(root, rel); s = open(p, encoding="utf-8").read(); o = s
    for old, new in pairs:
        if s.count(old) != 1: raise SystemExit("patch_energy_chain: %s: the old text is not there exactly once: %r" % (rel, old[:90]))
        s = s.replace(old, new)
    assert s != o
    if check: check(s, p)
    open(p, "w", encoding="utf-8").write(s); print("patch_energy_chain: %s edited, %d hunk(s)" % (rel, len(pairs)))

def _yaml_ok(s, p):
    import yaml; y = yaml.safe_load(s)
    st = [x for x in y["stages"] if x["id"] == "SHORE_INPUT"][0]
    assert st["continuous_a"] == 6.15 and st["peak_a"] == 6.15, st

edit("pcb_energy_chain.yaml", [
 ('''   from: "J_DCIN, the vehicle and shore DC inlet"
   to: "VIN_RAW"
   continuous_a: 8.0
   peak_a: 10.0''',
  '''   from: "J_DCIN, the vehicle and shore DC inlet"
   to: "VIN_RAW"
   # F-IN-02 (26 September 2026, gen_sch_e.py _VEH_T and _VEH_P) and this line since 27 September 2026 (w3de): the
   # hot-swap U6 (LM5069, R19 = 10 mOhm) limits the entry at VCL / RS, 4.85 / 5.5 / 6.15 A (TI SNVS452G), and a unit at
   # VCL max carries 6.15 A continuously without limiting, so 6.15 A is the path's continuous AND peak current (its
   # circuit breaker lets up to 13 A through for at most tCB 1.2 us, an edge no thermal or fuse rule reads). It read 8.0
   # and 10.0 A, figures from before the hot-swap existed; tests/test_energy_chain.py holds it to the generator now.
   continuous_a: 6.15
   peak_a: 6.15'''),
 ('''   note: "an ideal-diode FET and an SMCJ33A clamp sit behind this fuse; decision 31 records that the clamp's
     33 V stand-off is wrong against the board's own declared 9 to 36 V input range, which is a part choice
     and not a coordination error"''',
  '''   note: "an ideal-diode FET, the hot-swap and the input filter sit behind this fuse. The clamp decision 31 found
     wrong (an SMCJ33A whose 33 V stand-off sat inside the declared 9 to 36 V input range) was corrected on board E at
     faf8c981: D10 is an SMCJ40CA at the entry, in front of the ideal-diode FET, and D1 an SMCJ40A behind it. Since
     27 September 2026 the stage carries the vehicle path's 6.15 A (F-IN-02), which F1 carries at 77 percent of the
     8.0 A the ATOF table allows at its 65 C column"'''),
 ('''   conductor: {what: "four CELL+ and four return Mill-Max spring pins in parallel", rating_a: 36.0,
               basis: "9 A per pin, four in parallel (appendix 32.22 and the Mill-Max drawing in
                 v2/vendor/precidip/); the block's own copper is 2 oz"}''',
  '''   conductor: {what: "four CELL+ and four return Mill-Max spring pins in parallel", rating_a: 36.0,
               basis: "9 A per pin, four in parallel (appendix 32.22; the maker's page is filed at
                 v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf, 'Rated Current (Free air):
                 Continuous 9 amps @ 10 C temperature rise', 'Contact Resistance: 20 mOhm max'; it had been cited
                 in v2/vendor/precidip/, which holds the Preci-Dip signal contacts only); the block's own copper is 2 oz"}'''),
], _yaml_ok)

edit("tests/test_energy_chain.py", [
 ('''def t_the_shore_inlet_passes_on_the_maker_s_figure_and_says_it_has_no_margin():
    """The acceptable fixture AND the honest reading: 8.0 A against the 8.0 A the maker allows at 65 C is a
    pass with nothing left, and it must not read like a pass at 40 percent."""
    import subprocess, sys, os
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "energy_chain.py")],
                       capture_output=True, text=True, cwd=TOOLS)
    out = r.stdout
    assert "SHORE_INPUT: F1 carries 8.0 A where atof287 allows 8.0 A at its 65 C column" in out, out[-1500:]
    assert "no margin against the maker's own figure" in out, out[-1500:]''',
  '''def t_the_shore_inlet_is_judged_on_the_maker_s_figure_and_says_what_is_left():
    """The honest reading of the stage as it is: since F-IN-02 the vehicle path carries 6.15 A (the hot-swap's VCL max
    over its 10 mOhm), printed 6.2 A by the gate's one decimal, against the 8.0 A the ATOF table allows at its 65 C
    column: a pass with margin, which must not read "no margin" (the reading of the 8.0 A stage before 27 September
    2026). The no-margin wording itself is held on a synthetic stage by
    t_a_fuse_at_the_whole_of_its_column_says_it_has_no_margin, below."""
    import subprocess, sys, os, re
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "energy_chain.py")],
                       capture_output=True, text=True, cwd=TOOLS)
    out = r.stdout
    assert "SHORE_INPUT: F1 carries 6.2 A where atof287 allows 8.0 A at its 65 C column" in out, out[-1500:]
    line = [l for l in out.splitlines() if "SHORE_INPUT: F1 carries" in l]
    assert line and "no margin against the maker's own figure" not in line[0], line


def t_the_shore_stage_carries_the_vehicle_path_figure_board_e_declares():
    """27 September 2026 (w3de): F-IN-02 moved board E's vehicle entry to 6.15 A on 26 September and this chain kept
    8.0 and 10.0 A for a day, so two BLOCKER rules judged a fuse at a current its path cannot carry. The stage is held
    to the generator's own _VEH_T and _VEH_P, read by parsing gen_sch_e.py (the tree's rule for detectors: parse,
    never grep)."""
    import ast, yaml
    tree = ast.parse(open(os.path.join(TOOLS, "gen_sch_e.py"), encoding="utf-8").read())
    got = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple) \\
           and isinstance(node.value, ast.Tuple):
            for t, v in zip(node.targets[0].elts, node.value.elts):
                if isinstance(t, ast.Name) and t.id in ("_VEH_T", "_VEH_P") and isinstance(v, ast.Constant):
                    got[t.id] = float(v.value)
    assert set(got) == {"_VEH_T", "_VEH_P"}, "board E's generator no longer states _VEH_T and _VEH_P as a pair: %r" % got
    chain = yaml.safe_load(open(os.path.join(TOOLS, "pcb_energy_chain.yaml"), encoding="utf-8"))
    st = [s for s in chain["stages"] if s["id"] == "SHORE_INPUT"]
    assert st, "the chain has no SHORE_INPUT stage"
    assert float(st[0]["continuous_a"]) == got["_VEH_T"] and float(st[0]["peak_a"]) == got["_VEH_P"], \\
        (st[0]["continuous_a"], st[0]["peak_a"], got)


AT_THE_LIMIT = (FUSED.replace("continuous_a: 10.0", "continuous_a: 8.0\\n   derating: {table: atof287, ambient_c: 56}")
                     .replace("peak_a: 18.0", "peak_a: 8.0")
                     .replace('what: "25 A blade", rating_a: 25.0', 'what: "10 A blade", rating_a: 10.0'))


def t_a_fuse_at_the_whole_of_its_column_says_it_has_no_margin():
    """A PASS AT THE LIMIT IS NOT A PASS WITH ROOM, held on a synthetic stage (27 September 2026, w3de). Until F-IN-02's
    correction the committed SHORE_INPUT stage (8.0 A of a 10 A fuse at the 65 C column) was the only reading that
    carried this wording, so correcting the stage left energy_chain.py's at-limit branch with no fixture. A 10 A atof287
    fuse at 8.0 A continuous and 56 C ambient is read at the 65 C column (never interpolated), which allows exactly
    8.0 A: a pass, judged as one, that must say it has no margin. The same fuse at 7.5 A, under 95 percent of 8.0 A,
    is a pass with room and must not."""
    r = _run(AT_THE_LIMIT)
    assert not r["derate_fails"] and not r["stage_fails"], (r["derate_fails"], r["stage_fails"])
    at = [n for n in r["notes"] if "F1 carries 8.0 A where atof287 allows 8.0 A at its 65 C column" in n]
    assert len(at) == 1, r["notes"]
    assert "no margin against the maker's own figure" in at[0], at[0]
    room = _run(AT_THE_LIMIT.replace("continuous_a: 8.0", "continuous_a: 7.5"))
    assert not room["derate_fails"], room["derate_fails"]
    under = [n for n in room["notes"] if "F1 carries 7.5 A where atof287 allows 8.0 A at its 65 C column" in n]
    assert len(under) == 1, room["notes"]
    assert "no margin" not in under[0], under[0]'''),
], lambda s, p: compile(s, p, "exec"))
