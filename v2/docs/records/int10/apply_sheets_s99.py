#!/usr/bin/env python3
"""Layout constraint sheet A re-bound to the regenerated candidate of integration set 9 (MESHSAT-1357, 29 September 2026,
S-99, decision 55). The sheets bind to the declared phase's netlist and intent by sha, and their section 2 power tables are
what calc/rail_widths.py prints on the committed intent. S-99 split the D8 mezzanine off board A's +5V_DEV stage onto its own
buck (U41, +5V_D8IN) and corrected the wall port's current limit sign, so board A's rows moved and one row is new: a circuit
change, not a re-export. Board B's sheet is untouched (its inputs did not change). This script takes sheet A exactly as
`constraints_bound.py --emit a --sheet` prints it now (the tool's own text, never typed here), replaces every
"MOVED, explain it" and "NEW ROW, explain it" mark with the reason below, keeping the tool's before-values in the note of a
moved row and dropping the row's superseded earlier note (the reason below states the whole change), writes the sheet, and runs the binding check, which must read PASS on every sheet. It also writes
calc/rail_widths.out as rail_widths.py prints it. Refuses when a mark is left, when a row the tool marks is not one of
those listed, or when the check fails. Run from the repository root: python3 <this file>."""
import os, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2/ecad/tools")
LC = os.path.join(TOP, "v2/docs/layout-constraints")
MARK = "**MOVED, explain it**"
WHY = {
    ("A", "+5V_DEV"): "Moved at integration set 9 by S-99 (decision 55, records/s99a/README.md): the D8 mezzanine left this stage for its own buck U41 on +5V_D8IN, so the declared typical fell from 5.10 to 4.10 A (board B's 3.8 A plus the wall port's 0.3 A) and the peak is 6.9142 A (board B's 6.0 A plus the wall port at U32's corrected 0.9142 A, TPS2596 equation 7, SLVSET8A printed page 28); the widths follow the governing typical current (PI-001).",
    ("A", "SD_OUT"): "Moved with +5V_DEV above (S-99, set 9): the stage's output node carries the rail's declared current.",
    ("A", "+5V_D8IN"): "New at integration set 9 by S-99 (decision 55): the output of the new TPS62933 buck U41 from VBAT, feeding the eFuse U23 and board D's +5V_D8 behind it, declared 1.0 A typical and 2.0 A peak (the mezzanine's own figures) at 5.0 V (5.002 V nominal, 4.872 to 5.133 V over every tolerance); its 2 percent drop budget and the codec floor it bears on are open item S-116 and its layout reading S-115.",
    ("A", "VBUS_WALL"): "Moved at integration set 9: the wall port's peak is U32's current limit read by TPS2596 equation 7 with its true sign, 0.9142 A nominal (the generator had read 0.89 A); the typical is unchanged.",
}


def refuse(m):
    print("apply_sheets_s99: REFUSED: %s" % m)
    sys.exit(2)


def main():
    rw = subprocess.run([sys.executable, "rail_widths.py", "--markdown"], cwd=os.path.join(LC, "calc"), capture_output=True, text=True)
    if rw.returncode: refuse("rail_widths.py failed: %s" % rw.stderr[-300:])
    open(os.path.join(LC, "calc/rail_widths.out"), "w", encoding="utf-8").write(rw.stdout)
    seen = set()
    for L in ("a",):
        U = L.upper()
        em = subprocess.run([sys.executable, "constraints_bound.py", "--emit", L, "--sheet"], cwd=TOOLS, capture_output=True, text=True)
        if em.returncode: refuse("emit %s failed: %s" % (U, em.stderr[-300:]))
        out = []
        for line in em.stdout.split("\n"):
            if MARK in line or "**NEW ROW, explain it**" in line:
                rail = line.split("|")[1].strip()
                key = (U, rail)
                if key not in WHY: refuse("board %s: the tool marks row %s, which this script does not explain" % (U, rail))
                mk = MARK if MARK in line else "**NEW ROW, explain it**"
                i = line.index(mk)
                rest = line[i + len(mk):].rstrip()
                if rest.endswith("|"): rest = rest[:-1].rstrip()
                # the tool writes the mark, then the before-values in balanced parentheses, then the row's previous note;
                # the previous note is superseded by the reason written here, so only the before-values are kept
                rest = rest.strip()
                before = ""
                if mk == MARK and rest.startswith("("):
                    depth = 0
                    for k, ch in enumerate(rest):
                        depth += (ch == "(") - (ch == ")")
                        if depth == 0: break
                    if depth: refuse("board %s, row %s: unbalanced before-values %r" % (U, rail, rest[:80]))
                    before = rest[1:k]
                elif mk == MARK: refuse("board %s, row %s: a moved row without before-values" % (U, rail))
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
    print("apply_sheets_s99: sheet A re-bound with %d moved or new rows explained; rail_widths.out rewritten" % len(seen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
