#!/usr/bin/env python3
"""UNEXECUTED APPLICATION DRAFT: INTERIM alignment; mode figure INCONCLUSIVE.

Prototype design, AI review. See CORRECTION.md B1/B2 and ANALYSIS.md.
Only --check is authorised in this job. It validates in memory and writes
nothing: no generator, marker, cache or other file. The application path is
for the generator owners after review and the integrating session's decision.
The +5V_DEV converter peak recommendation is pending, not applied here.
"""
import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# INTERIM source-derived S2 4.2/5.63 A, not a verified PS-ALLTX demand.
# Keep the 7.28 A all-peak conditional bound against the 7.10 to 7.17 A
# LM5176 loop minimum (+1% / nominal shunt), CORRECTION.md B1.
CHANGES = [
    {
        "id": "B1-A-S2",
        "file": "v2/ecad/tools/gen_sch_a.py",
        "old": '    _intent.rail("+5V_S%s" % _n, 5.1, 2.5, 5.0, _sh, loads={"J_5V_S%s" % _n: 5.0},',
        "new": '    # INTERIM I-03: S2 aligned to B; PS-ALLTX current INCONCLUSIVE.\n'
               '    # S2 all-peak conditional bound 7.28 A vs loop minimum 7.10 to 7.17 A.\n'
               '    _intent.rail("+5V_S%s" % _n, 5.1, 4.2 if _n == "2" else 2.5, 5.63 if _n == "2" else 5.0, _sh, loads={"J_5V_S%s" % _n: 5.63 if _n == "2" else 5.0},',
    },
    {
        "id": "B1-A-Q28",
        "file": "v2/ecad/tools/gen_sch_a.py",
        # 5.63*5.1/(0.90*14.4) = 2.215509 A -> 2.22; nominal-input allocation.
        "old": '"Q28": 2.0, "U6": 2.0',
        "new": '"Q28": 2.22, "U6": 2.0',
    },
    {
        "id": "B1-B-S2",
        "file": "v2/ecad/tools/gen_sch_b.py",
        "old": '    _intent.rail("+5V_S%d" % _n, 5.1, 4.2 if _n == 2 else 2.5, 5.0, "J_5V_S%d" % _n,',
        "new": '    # INTERIM I-03: S2 5.63 A coincidence; PS-ALLTX current INCONCLUSIVE.\n'
               '    # All-peak conditional bound 7.28 A vs loop minimum 7.10 to 7.17 A.\n'
               '    _intent.rail("+5V_S%d" % _n, 5.1, 4.2 if _n == 2 else 2.5, 5.63 if _n == 2 else 5.0, "J_5V_S%d" % _n,',
    },
    {
        "id": "B2-A-DEV",
        "file": "v2/ecad/tools/gen_sch_a.py",
        # 3.8 from B + D8 declared 1.0 + parent wall allocation 0.3 = 5.1 A.
        # U23 follows D8's typical so the parent load map also sums to 5.1 A.
        # Peak 6.9 stays pending SESSION decision: recommend 8.9 A coincident
        # bound (7.9 A with D8 typical), with LM5176 average-loop fold-back.
        "old": '_intent.rail("+5V_DEV", 5.0, 4.0, 6.9, "R43", loads={"J_5V_DEV": 3.2, "U23": 0.5, "U32": 0.3},',
        "new": '# INTERIM I-03: typical 3.8 B + 1.0 D8 + 0.3 wall; PS-ALLTX INCONCLUSIVE.\n'
               '# Peak 6.9 A is stale: SESSION decision owed on 8.9 A coincident bound\n'
               '# (7.9 A with D8 typical) and LM5176 average-loop fold-back risk.\n'
               '_intent.rail("+5V_DEV", 5.0, 5.1, 6.9, "R43", loads={"J_5V_DEV": 3.8, "U23": 1.0, "U32": 0.3},',
    },
]
ALLOWED = {"v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/gen_sch_b.py"}
MARKER = Path(__file__).with_name("apply_declarations_draft.applied")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = parser.parse_args()
    if MARKER.exists():
        raise SystemExit("Refused: this draft has already been applied or attempted.")
    if not CHANGES:
        raise SystemExit("Refused: no sourced replacement currents; empty draft writes nothing.")
    originals = {}
    results = {}
    messages = []
    for change in CHANGES:
        name, old, new = change["file"], change["old"], change["new"]
        assert name in ALLOWED, name
        assert old and new != old, "Replacement must change nonempty old text"
        if name not in originals:
            originals[name] = (ROOT / name).read_text()
            results[name] = originals[name]
        assert originals[name].count(old) == 1, (name, "old text must occur exactly once in original")
        assert results[name].count(old) == 1, (name, "old text must occur exactly once at replacement")
        results[name] = results[name].replace(old, new, 1)
        messages.append(f"PASS {change['id']}: {name}: exact old text occurs once")
    for name, result in results.items():
        assert result != originals[name], (name, "no effective change")
        ast.parse(result, filename=name)
        assert (ROOT / name).read_text() == originals[name], (name, "file changed during validation")
        messages.append(f"PASS AST: {name}: replaced text parses")
    if args.check:
        print("\n".join(messages))
        print(f"CHECK ONLY: {len(CHANGES)} entries, {len(results)} generators; no writes, no marker.")
        return
    # Exclusive creation refuses every second run, including recovery from a partial write.
    # An owner would investigate a partial write; this draft never silently retries it.
    with MARKER.open("x") as marker:
        marker.write("Draft attempted. Do not run again.\n")
    for name, result in results.items():
        (ROOT / name).write_text(result)


if __name__ == "__main__":
    main()
