#!/usr/bin/env python3
"""lcsc_fill.py's own choices meet the identity tool's requirements (MESHSAT-1357, Layer 6 record l6r2 round 3, 3 October 2026).

lcsc_fill.py fills a blank BOM line at finish from its MAP, then from the certified table. On 3 October 2026 the codes it would
have filled failed the requirement the identity tool derives from the netlist and the intent on 170 rows of the six boards
(X5R where rule C-D3 makes an unstated class 2 X7R, an X7R 10 % part on C0G rows, 50 V parts on 100 V rows, a 3 W shunt where
rule R-P asks 5 W, a 5 % part on 1 % lines, a 500 mA ferrite on a 2 A line, an 800 ppm/K shunt where rule R-S1 asks 200), and
no line filled board A's C27, which refuses the finish. The table was corrected the same day (record l6r2, round 3). These are properties, never a list of those rows:

  * for every fitted row of every board's committed netlist that carries no code, the code lcsc_fill.py ITSELF writes (the real
    script, run on a BOM built from the netlist in a scratch directory) meets every deciding requirement of the row's class
    (capacitor, resistor, ferrite, small diode, indicator LED) on the catalogue line read for it (record l6r2's dated JLCPCB
    reading), judged by l6r2_passives.check on part_identities' requirements; the one exception is an X5R fill on a line
    lcsc_fill.py declares under rule C-D3b (CD3B_X5R), which must then meet every other requirement;
  * every code lcsc_fill fills on such a row has a catalogue line in the reading (a fill nobody read is a miss);
  * lcsc_fill leaves no such generic row blank (a blank generic line refuses the board's finish: a missing table line is a miss);
  * lcsc_fill rejects none of the codes it filled itself;
  * a C-D3b declaration names a line of the MAP whose code is X5R on the reading (a declaration that covers nothing is stale);
  * the judge has teeth: a copy of lcsc_fill.py whose 100n line is put back to a 50 V part is caught on a 100 V fixture row.
A row whose requirement is open (no bound on its nets) is counted, not judged: it is a requirement gap, not a fill.
Run: env -C v2/ecad/tools/tests python3 run.py test_lcsc_fill_requirements"""
import ast
import csv
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(REPO, "v2", "docs", "records", "l6r2")
FILL = os.path.join(TOOLS, "lcsc_fill.py")
sys.path.insert(0, TOOLS)
import part_identities as PI  # noqa: E402

GENERIC = ("CAP", "RES", "FERRITE", "SEMI", "LED")
_C = {}


def _M():
    if "m" not in _C:
        p = os.path.join(REC, "l6r2_passives.py")
        if not os.path.exists(p): raise Skip("record l6r2 (the catalogue reading and the checks) is not in the tree")
        sp = importlib.util.spec_from_file_location("l6r2_for_fill", p)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        cat = m.load_catalogue()
        idx = dict(cat["codes"])
        for s in cat["searches"].values():
            for r in s["rows"]: idx.setdefault(r["code"], r)
        _C["m"], _C["idx"] = m, idx
    return _C["m"], _C["idx"]


def _parse(path, name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return ast.literal_eval(n.value)
    return {}


def run_fill(script, rows):
    """lcsc_fill.py itself on a one-line-per-reference BOM of the rows (Comment, Designator, Footprint, LCSC Part #, as
    export_jlc.sh writes them), in a scratch directory with its own verdict folder and an empty allow list. Returns the code per
    designator after the fill and the designators it rejected (its 'carry a code this project has checked and rejected' lines)."""
    with tempfile.TemporaryDirectory(prefix="lcsc-fill-req-") as td:
        os.makedirs(os.path.join(td, "out", "jlc"))
        p = os.path.join(td, "out", "jlc", "board-bom.csv")
        open(os.path.join(td, "allow.txt"), "w").close()
        with open(p, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
            for r in rows: w.writerow([r["value"], r["ref"], r["land"], r["generator_lcsc"]])
        out = subprocess.run([sys.executable, "-B", script, p], cwd=td, capture_output=True, text=True,
                             env=dict(os.environ, VERDICT_DIR=os.path.join(td, "verdicts"), LCSC_ALLOW=os.path.join(td, "allow.txt")))
        filled = {row["Designator"]: (row["LCSC Part #"] or "").strip() for row in csv.DictReader(open(p))}
    rejected = set()
    for line in out.stdout.splitlines():
        m = re.match(r"\s+(\S+) (C\d+)[: ]", line)
        if m and "carry a code" not in line: rejected.add(m.group(1))
    return filled, rejected


def judge(rows, filled, rejected, cd3b, m, idx):
    """The misses: (designator, value, code, the failing checks). Counts the rows judged and the open ones."""
    MAP = None
    misses, judged, opened = [], 0, 0
    for r in rows:
        if r["generator_lcsc"]: continue
        code = filled.get(r["ref"])
        d = dict(kind=r["kind"], prefix=r["prefix"], requirements=dict(r["requirements"]), values=[r["value"]], lands=[r["land"]], refs=[r["ref"]])
        d["cls"], _why = m.classify(d)
        if d["cls"] == "OPEN":
            if code: opened += 1
            continue
        if d["cls"] not in GENERIC: continue
        judged += 1
        if not code:
            misses.append((r["ref"], r["value"], "", "lcsc_fill leaves a generic line blank (no table line fills it)")); continue
        if r["ref"] in rejected:
            misses.append((r["ref"], r["value"], code, "lcsc_fill rejects the code it filled")); continue
        row = idx.get(code)
        if row is None:
            misses.append((r["ref"], r["value"], code, "no catalogue line read for the code")); continue
        ok, lines, _g = m.check(d, row)
        if not ok and d["cls"] == "CAP" and any(re.match(vre, r["value"]) and fsub in r["land"] for (vre, fsub) in cd3b):
            d2 = dict(d); d2["requirements"] = dict(d["requirements"], dielectric="X5R")
            ok, lines, _g = m.check(d2, row)
        if not ok:
            misses.append((r["ref"], r["value"], code, "; ".join("%s %s (read %s)" % (x[0], x[3], x[2]) for x in lines if x[3] != "MEETS")))
    return misses, judged, opened


def t_lcsc_fills_only_codes_that_meet_the_requirements_on_every_board():
    m, idx = _M()
    cd3b = _parse(FILL, "CD3B_X5R")
    total, opened, bad = 0, 0, []
    for b in m.ORDER:
        rows, _ = PI.rows(boards=[b])
        filled, rejected = run_fill(FILL, rows)
        mis, n, o = judge(rows, filled, rejected, cd3b, m, idx)
        total += n; opened += o
        bad += ["%s %s [%s] %s: %s" % (b.upper(), x[0], x[1][:40], x[2], x[3]) for x in mis]
    assert total > 1000, "only %d rows judged: the judge does not see the boards" % total
    assert not bad, "lcsc_fill.py fills %d code(s) that miss the identity tool's requirements:\n  %s" % (len(bad), "\n  ".join(bad[:40]))


def t_every_c_d3b_declaration_covers_a_map_line_whose_code_is_x5r():
    m, idx = _M()
    MAP, cd3b = _parse(FILL, "MAP"), _parse(FILL, "CD3B_X5R")
    for key, why in cd3b.items():
        assert key in MAP, "CD3B_X5R names %r, which is not a MAP line" % (key,)
        row = idx.get(MAP[key])
        assert row and m.diel_of((row.get("attributes") or {}).get("Temperature Coefficient")) == "X5R", \
            "CD3B_X5R declares %r but its code %s is not an X5R part on the reading" % (key, MAP[key])
        assert why.strip(), "a declaration without its reason"


def t_the_judge_catches_a_line_put_back_to_a_part_that_misses():
    m, idx = _M()
    if "C14663" not in idx or "C113803" not in idx: raise Skip("the reading lacks the fixture's codes")
    src = open(FILL, encoding="utf-8").read()
    old = '(r"^100n", "C_0603"): "C113803",'
    assert src.count(old) == 1, "the fixture expects the corrected 100n line once"
    row = dict(ref="C900", prefix="C", kind="capacitor", value="100n", land="C_0603_1608Metric", generator_lcsc="",
               requirements=dict(value="100nF", package="0603", construction="MLCC", dielectric="X7R", v_rating_min=100.0, tolerance_max_pct=10.0))
    with tempfile.TemporaryDirectory(prefix="lcsc-fill-teeth-") as td:
        for f in ("lcsc_fill.py", "verdict.py", "lcsc-blocked.txt", "jlc-mismatch.yaml", "jlc_certify.py"):
            if os.path.exists(os.path.join(TOOLS, f)): shutil.copy(os.path.join(TOOLS, f), td)
        bad_src = src.replace(old, '(r"^100n", "C_0603"): "C14663",')
        open(os.path.join(td, "lcsc_fill.py"), "w", encoding="utf-8").write(bad_src)
        f_bad, r_bad = run_fill(os.path.join(td, "lcsc_fill.py"), [row])
        f_good, r_good = run_fill(FILL, [row])
    mis_bad, n_bad, _ = judge([row], f_bad, r_bad, {}, m, idx)
    mis_good, n_good, _ = judge([row], f_good, r_good, {}, m, idx)
    assert n_bad == 1 and mis_bad and "rated voltage FAILS" in mis_bad[0][3], "a 50 V fill on a 100 V row was not caught: %s" % mis_bad
    assert n_good == 1 and not mis_good, "the corrected line misses the fixture row: %s" % mis_good
