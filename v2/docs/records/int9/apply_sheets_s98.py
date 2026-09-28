#!/usr/bin/env python3
"""Layout constraint sheets A and B re-bound to the regenerated candidate of integration set 8 (MESHSAT-1357, 28 September 2026,
S-98). The sheets bind to the declared phase's netlist and intent by sha, and their section 2 power tables are what
calc/rail_widths.py prints on the committed intent. S-98 raised declared currents (board A's +5V_S2 and +5V_DEV typical, board
B's +5V_S2 peak), so the widths moved: a real consequence of the change, not a re-export. This script takes each sheet exactly
as `constraints_bound.py --emit <letter> --sheet` prints it now (the tool's own text, never typed here), replaces every
"MOVED, explain it" mark the tool leaves with the reason below, keeping the tool's before-values in the note, writes the
sheet, and runs the binding check, which must read PASS on every sheet. It also writes calc/rail_widths.out as rail_widths.py
prints it. Refuses when a mark is left, when a row the tool marks is not one of those listed, or when the check fails.
Run from the repository root: python3 <this file>."""
import os, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2/ecad/tools")
LC = os.path.join(TOP, "v2/docs/layout-constraints")
MARK = "**MOVED, explain it**"
WHY = {
    ("A", "+5V_S2"): "Moved at integration set 8 by S-98 (finding I-03, INTERIM alignment of the A to B leads, records/cx1/CORRECTION.md B1, records/s98): the declared typical rose from 2.50 to 4.20 A and the peak from 5.00 to 5.63 A, board B's figures derived from held maker pages; the widths follow the governing typical current (PI-001). The PS-ALLTX mode current stays INCONCLUSIVE (I-03's adequacy, the bench).",
    ("A", "S2_OUT"): "Moved with +5V_S2 above (S-98, set 8): the converter output node carries the rail's declared current.",
    ("A", "+5V_DEV"): "Moved at integration set 8 by S-98 (records/cx1/CORRECTION.md B2): the declared typical rose from 4.00 to 5.10 A (board B's 3.8 A arriving at J_5V_DEV plus the D8 mezzanine's 1.0 A plus the wall port's 0.3 A); the 6.90 A peak is held pending S-99 (the D8 split, set 9, lowers it). The widths follow the governing typical current (PI-001).",
    ("A", "SD_OUT"): "Moved with +5V_DEV above (S-98, set 8): the converter output node carries the rail's declared current.",
    ("B", "+5V_S2"): "Moved at integration set 8 by S-98: board B's own peak call now declares the 5.63 A coincident peak its comment derived (5.00 before), and both ends of the lead declare 4.20 A typical and 5.63 A peak (IF-AB-POWER AGREE, INTERIM); the widths are unchanged (governing typical 4.20 A), the barrel counts follow the larger peak.",
}


def refuse(m):
    print("apply_sheets_s98: REFUSED: %s" % m)
    sys.exit(2)


def main():
    rw = subprocess.run([sys.executable, "rail_widths.py", "--markdown"], cwd=os.path.join(LC, "calc"), capture_output=True, text=True)
    if rw.returncode: refuse("rail_widths.py failed: %s" % rw.stderr[-300:])
    open(os.path.join(LC, "calc/rail_widths.out"), "w", encoding="utf-8").write(rw.stdout)
    seen = set()
    for L in ("a", "b"):
        U = L.upper()
        em = subprocess.run([sys.executable, "constraints_bound.py", "--emit", L, "--sheet"], cwd=TOOLS, capture_output=True, text=True)
        if em.returncode: refuse("emit %s failed: %s" % (U, em.stderr[-300:]))
        out = []
        for line in em.stdout.split("\n"):
            if MARK in line:
                rail = line.split("|")[1].strip()
                key = (U, rail)
                if key not in WHY: refuse("board %s: the tool marks row %s, which this script does not explain" % (U, rail))
                i = line.index(MARK)
                rest = line[i + len(MARK):].rstrip()
                if rest.endswith("|"): rest = rest[:-1].rstrip()
                before = rest.strip()
                if before.startswith("(") and before.endswith(")"): before = before[1:-1]
                line = line[:i] + WHY[key] + (" Before: " + before + "." if before else "") + " |"
                seen.add(key)
            out.append(line)
        text = "\n".join(out)
        if MARK in text or "**NEW ROW, explain it**" in text: refuse("a mark is left on sheet %s" % U)
        if "—" in text or "–" in text: refuse("a dash character on sheet %s" % U)
        open(os.path.join(LC, U + ".md"), "w", encoding="utf-8").write(text)
    if seen != set(WHY): refuse("explained rows %s, expected %s" % (sorted(seen), sorted(WHY)))
    chk = subprocess.run([sys.executable, "constraints_bound.py", "--no-git"], cwd=TOOLS, capture_output=True, text=True)
    last = [l for l in chk.stdout.split("\n") if l.startswith("constraints_bound:")]
    for l in last: print(l)
    if chk.returncode: refuse("the binding check does not pass")
    print("apply_sheets_s98: sheets A and B re-bound with %d moved rows explained; rail_widths.out rewritten" % len(seen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
