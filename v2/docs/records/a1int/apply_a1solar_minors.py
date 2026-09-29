#!/usr/bin/env python3
"""Stream a1solar's integration into fnd/a1int (MESHSAT-1357, 29 September 2026): the stream's thirteen commits
559a072d..066e6b97 were applied as ONE squashed diff (the first issue's three SunPower documents, held back by their terms,
stay out of the public history), and this script answers the focused re-check's minor items N1 to N3 (`checks/check-2.md`):
N1 the divider 232k over 8.45k is "equal best" with 187k over 6.81k (0.9662 against 0.9663); N2 the two checks are filed
under `records/a1solar/checks/` and cited there instead of a scratch path; N3 the deployment rule is quoted as the grid's
model result with its thinnest margins. N4 is already labelled in `energy_runs.out` 6. Text only: array_calc.py's comment,
not its output, changes. Every old text asserted once; refuses a second run. Run: python3 <this file>."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
A = os.path.join(TOP, "v2/docs/records/a1solar")
SCR = "/".join(("", "home", "claude" + "-runner", "worktrees", "meshsat-fieldkit", "_scratch", "chk-a1solar"))
DASHES = ("—", "–")


def refuse(m):
    print("apply_a1solar_minors: REFUSED: %s" % m)
    sys.exit(2)


def edit(name, pairs):
    p = os.path.join(A, name)
    t = open(p, encoding="utf-8").read()
    t2 = t
    for old, new in pairs:
        if t2.count(old) != 1: refuse("%s: %r found %d times" % (name, old[:60], t2.count(old)))
        t2 = t2.replace(old, new)
    if t2 == t or any(d in t2 for d in DASHES): refuse("%s: unchanged or a dash" % name)
    open(p, "w", encoding="utf-8").write(t2)


def main():
    if os.path.exists(os.path.join(A, "checks/check-2.md")): refuse("already applied")
    for src, dst, note in (("CHECK.md", "check-1.md", "the independent AI check of 9f93a9fc; its items answered in the second issue"),
                           ("CHECK-2.md", "check-2.md", "the focused re-check of 066e6b97; N1 to N3 answered by records/a1int/apply_a1solar_minors.py, N4 labelled in energy_runs.out")):
        t = open(os.path.join(SCR, src), encoding="utf-8").read()
        first, rest = t.split("\n", 1)
        t = first + "\n<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026): %s. -->\n" % note + rest
        t = t.replace("`_scratch/chk-a1solar`", "the checker's scratch clone").replace("_scratch/chk-a1solar-root", "the checker's scratch root")
        if "/home/" in t or any(d in t for d in DASHES): refuse("%s: a user path or a dash" % src)
        open(os.path.join(A, "checks", dst), "w", encoding="utf-8").write(t)
    cite = "`_scratch/chk-a1solar/CHECK.md`"
    edit("README.md", [(cite, "`checks/check-1.md`"),
                       ("and the operator sets them at 20 to 50 degrees facing within 15 degrees of\n  south (a CONOPS line, the owner's to accept).",
                        "and the operator sets them at 20 to 50 degrees facing within 15 degrees of\n  south (a CONOPS line, the owner's to accept; the grid's result on this model, its thinnest margins 3.3 Wh at 20\n  degrees and 15 east in the adverse case, 8.9 Wh at 50 and 15 east, 9.5 Wh at 20 and 15 west; planes between grid\n  points are not run; re-checked in `checks/check-2.md`).")])
    edit("ARRAY.md", [(cite, "`checks/check-1.md`"),
                      ("chosen among six E96 pairs as the best worst case across the three fits and the window (0.9662 against 0.9633 for\n  205k / 7.50k);",
                       "chosen among six E96 pairs as an equal best worst case across the three fits and the window (0.9662, with 187k /\n  6.81k at 0.9663 and 205k / 7.50k at 0.9633);"),
                      ("**The deployment rule restated from the grid: 20 to 50 degrees of slope, facing within 15 degrees of south** (every",
                       "**The deployment rule restated from the grid, a result on this model: 20 to 50 degrees of slope, facing within 15\n  degrees of south** (thinnest margins 3.3 Wh at 20/-15 adverse, 8.9 Wh at 50/-15, 9.5 Wh at 20/+15; every")])
    edit("SELECTION.md", [(cite, "`checks/check-1.md`")])
    edit("array_calc.py", [("# the second issue's draft (section 12: the E96 pair whose worst case across the fits\n"
                             "                                     # and the set-point window is the best of the candidates)",
                            "# the second issue's draft (section 12: an E96 pair whose worst case across the fits\n"
                            "                                     # and the set-point window equals the best of the candidates, 187k / 6.81k)")])
    print("apply_a1solar_minors: checks filed, N1 to N3 answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
