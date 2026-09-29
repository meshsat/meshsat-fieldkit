#!/usr/bin/env python3
"""PWR-001's pin-role table learns the two FETs S-117's finding F1 draws on board A (stream s117, second issue,
MESHSAT-1357, 29 September 2026). DRAFT for the tools owner and the integrator, run with apply_gen_sch_a_fets_s117.py; the
author ran --check only.

Why. intent_checks.PIN_ROLES reads each part's pin roles by the part number that leads its value field; PWR-001 follows a
declared rail's current through a part by those roles (board A's CH_ACN names Q7 as its load). The table knows the SON 5 x
6 mm FETs CSD17570Q5B, CSD18510Q5B and CSD19532Q5B; the regenerated board A carries CSD17578Q5A (Q7) and CSD17577Q5A (Q8 to
Q10), which no row names, so their pins would read with no roles. Both datasheets give the Q5B's pin order for the Q5A
package (1 to 3 source, 4 gate, 5 to 8 drain; SLPS526 and SLPS516, p.1 and 7.1 p.8), which is _SON5X6. Each new row cites
its own datasheet at its held path (v2/vendor/ti/held/, ignored: TI's terms forbid redistribution, v2/vendor/sources.txt);
in a tree without the fetched file the row still gives the roles and the reading records that document with no sha, which
is the table's documented behaviour for a missing file (_sha16 returns None). rules_status's declared inputs for
intent_checks.py are NOT extended here (the instrument limit its own comment states for a new row's document).

A CHANGE TO A WRITER: rules_status reads intent_checks.py as the writer of intent_rails, so every PWR-001 reading is re-taken
after it on every board (the consolidated re-take the integrator runs after the regeneration).

Guards: the CSD18510Q5B row is found once; the new rows are not there before; the result parses (ast); the modified module,
loaded from a temporary copy, gives Q7 = CSD17578Q5A and Q8 = CSD17577Q5A the roles S, S, S, G, D on pins 1 to 5 and still
gives CSD18510Q5B its row; a second run refuses. --check writes nothing.
Usage: python3 apply_intent_checks_s117.py [--check]"""
import argparse, ast, hashlib, importlib.util, os, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2/ecad/tools")
TGT = os.path.join(TOOLS, "intent_checks.py")
ANCHOR = ('    {"part": r"CSD18510Q5B\\b", "document": "v2/vendor/battery/ti-csd18510q5b.pdf", "package": "SON 5x6",\n'
          '     "pins": {p: (n, r, q, None) for p, (n, r, q) in _SON5X6.items()}},\n')
ADD = ('    # stream s117 (S-117 F1, 29 September 2026): board A\'s charger FETs; TI\'s Q5A package with the Q5B\'s pin order.\n'
       '    # The datasheets are held back by TI\'s terms (v2/vendor/sources.txt), fetched by records/s117/fetch_held_back.py.\n'
       '    {"part": r"CSD17578Q5A\\b", "document": "v2/vendor/ti/held/ti-csd17578q5a-slps526.pdf", "package": "SON 5x6",\n'
       '     "pins": {p: (n, r, q, None) for p, (n, r, q) in _SON5X6.items()}},\n'
       '    {"part": r"CSD17577Q5A\\b", "document": "v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf", "package": "SON 5x6",\n'
       '     "pins": {p: (n, r, q, None) for p, (n, r, q) in _SON5X6.items()}},\n')


def refuse(m):
    print("apply_intent_checks_s117: REFUSED: %s" % m)
    sys.exit(2)


def probe(text):
    """Load the modified module from a temporary copy and read the roles it gives the new parts."""
    d = tempfile.mkdtemp(prefix="s117-ic-")
    try:
        p = os.path.join(d, "intent_checks.py")
        open(p, "w", encoding="utf-8").write(text)
        sys.path.insert(0, TOOLS)
        spec = importlib.util.spec_from_file_location("intent_checks_s117_probe", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        roles, docs = m.held_roles({"Q7": "CSD17578Q5A 30 V N-FET", "Q8": "CSD17577Q5A 30 V N-FET", "Q27": "CSD18510Q5B 40 V N-FET"})
        return roles, docs
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t = open(TGT, encoding="utf-8").read()
    if "CSD17578Q5A" in t or "CSD17577Q5A" in t: refuse("the table already names a CSD17578Q5A or CSD17577Q5A (a second run)")
    if t.count(ANCHOR) != 1: refuse("the CSD18510Q5B row occurs %d times, not once" % t.count(ANCHOR))
    out = t.replace(ANCHOR, ANCHOR + ADD)
    ast.parse(out)
    roles, docs = probe(out)
    want = {"1": "S", "2": "S", "3": "S", "4": "G", "5": "D"}
    for ref in ("Q7", "Q8", "Q27"):
        got = {p: roles.get((ref, p), (None, None))[1] for p in want}
        if got != want: refuse("%s reads roles %s" % (ref, got))
    if "v2/vendor/ti/held/ti-csd17578q5a-slps526.pdf" not in docs or "v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf" not in docs:
        refuse("the new rows' documents are not recorded")
    print("apply_intent_checks_s117: intent_checks.py sha256/16 %s -> %s; two PIN_ROLES rows after CSD18510Q5B's; Q7 "
          "(CSD17578Q5A), Q8 (CSD17577Q5A) and Q27 (CSD18510Q5B) read S S S G D on pins 1 to 5 from the modified module"
          % (hashlib.sha256(t.encode()).hexdigest()[:16], hashlib.sha256(out.encode()).hexdigest()[:16]))
    if a.check:
        print("CHECK ONLY: intent_checks.py not written.")
        return 0
    open(TGT, "w", encoding="utf-8").write(out)
    if open(TGT, encoding="utf-8").read() != out: refuse("the written file differs")
    print("APPLIED: v2/ecad/tools/intent_checks.py written once. A writer changed: re-take PWR-001 on every board.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
