#!/usr/bin/env python3
"""Every layout constraint sheet re-bound to the netlists set 10 regenerated (MESHSAT-1357, 29 September 2026). The sheets bind
their inputs (netlist, intent, board file, chain) by sha and name the commit each last changed in. The regeneration moved the
netlists' sha (their export date) and nothing a sheet's tables are computed from, so a sheet as `constraints_bound.py --emit`
prints it now may differ from the committed one ONLY on the bound block's input lines and its `read` line. The script emits
each sheet, refuses any other difference (a moved or new row would carry the tool's mark and is not explained here), writes the
sheets and runs the binding check, which must read PASS. Refuses a second run (nothing to move). Run from the repository root."""
import os, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2/ecad/tools")
sys.path.insert(0, TOOLS)
import constraints_bound as CB
LC = os.path.join(TOP, "v2/docs/layout-constraints")
ALLOWED = set(CB.INPUT_ROLES) | {"read"}


def refuse(m):
    print("apply_sheets_int11: REFUSED: %s" % m); sys.exit(2)


def rail_widths():
    """calc/rail_widths.out as rail_widths.py prints it now; only its input lines and the intents' written dates may move."""
    rw = subprocess.run([sys.executable, "rail_widths.py", "--markdown"], cwd=os.path.join(LC, "calc"), capture_output=True, text=True)
    if rw.returncode: refuse("rail_widths.py failed: %s" % rw.stderr[-300:])
    p = os.path.join(LC, "calc/rail_widths.out")
    a, b = open(p, encoding="utf-8").read().split("\n"), rw.stdout.split("\n")
    if len(a) != len(b): refuse("rail_widths.out: %d lines against %d" % (len(b), len(a)))
    for x, y in zip(a, b):
        if x != y and not (x.split()[:1] in (["netlist"], ["intent"]) or x.startswith("Intent written ")):
            refuse("rail_widths.out: a difference beyond the inputs and dates: %r" % x[:120])
    open(p, "w", encoding="utf-8").write(rw.stdout)


def main():
    rail_widths()
    moved = []
    for letter, name in sorted(CB.SHEETS.items()):
        em = subprocess.run([sys.executable, "constraints_bound.py", "--emit", letter, "--sheet"], cwd=TOOLS, capture_output=True, text=True)
        if em.returncode: refuse("emit %s failed: %s" % (letter, em.stderr[-300:]))
        new = em.stdout
        p = os.path.join(LC, name)
        old = open(p, encoding="utf-8").read()
        a, b = old.split("\n"), new.split("\n")
        if len(a) != len(b): refuse("%s: the emitted sheet has %d lines, the committed %d" % (name, len(b), len(a)))
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        bad = [(x, y) for x, y in diff if not (x.split()[:1] and x.split()[0] in ALLOWED and y.split()[:1] == x.split()[:1])]
        if bad: refuse("%s: a difference outside the bound block: %r" % (name, bad[0]))
        if [x for x, y in diff if x.split()[0] != "read"]:
            open(p, "w", encoding="utf-8").write(new); moved.append(name)
    if not moved: refuse("no sheet's inputs moved (a second run)")
    chk = subprocess.run([sys.executable, "constraints_bound.py", "--no-git"], cwd=TOOLS, capture_output=True, text=True)
    for l in chk.stdout.split("\n"):
        if l.startswith("constraints_bound:"): print(l)
    if chk.returncode: refuse("the binding check does not pass")
    print("apply_sheets_int11: %d sheet(s) re-bound, their tables unchanged: %s" % (len(moved), ", ".join(moved)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
