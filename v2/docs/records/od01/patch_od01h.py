#!/usr/bin/env python3
"""The integrator's answers to check 8 of the OD-01 package (MESHSAT-1357, 29 September 2026; `checks/check-8.md`, the
re-check of patch_od01g.py by check 7's checker). C1: in the patch runs the shutdown switches nothing, yet section 3's
trip list and section 8's table said TS3 holds H1's edge over the o-ring; CH4 stayed about 240 mm from the resistor and the
band nearest it may pass 70 C in an 83 W pulse (the check's estimate, INFERRED). Now CH4 moves to the band nearest the
resistor with its 70 C stop, the pulse stops at it, and the trip list and the table say which limits TS1 to TS4 hold (the
steady-state steps) and which the operator holds (the patch runs). s1: the leads laid clear of the screws in item 7, before
H1 clamps them. s2: the box path check 7 quotes is generalised; the patch scripts' literals stay as they ran (records of
their runs; the path names a directory on the rented box, no host). Old texts matched with any whitespace between words,
each exactly once; refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OD = "v2/docs/records/od01/"
DASHES = ("—", "–")


def refuse(m):
    print("patch_od01h: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    pat = r"\s+".join(re.escape(w) for w in old.split())
    hits = list(re.finditer(pat, t))
    if len(hits) != 1: refuse("%s: expected once, found %d: %r" % (where, len(hits), old[:70]))
    if any(d in new for d in DASHES): refuse("%s: a dash character in the new text" % where)
    m = hits[0]
    return t[:m.start()] + new + t[m.end():]


def edit(path, pairs):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = t
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if t2 == t or any(d in t2 for d in DASHES): refuse("%s unchanged or a dash" % path)
    open(p, "w", encoding="utf-8").write(t2)


def main():
    if os.path.exists(os.path.join(TOP, OD, "checks/check-8.md")): refuse("already applied (check-8 filed)")
    edit(OD + "TEST-PROCEDURE.md", [
        ("TS3 holds H1 at or under 63 C, and so its edge",
         "in the steady-state steps (not the patch runs, whose\nlimits are the operator's, section 6) TS3 holds H1 at or under 63 C, and so its edge"),
        ("(section 3, wiring item 2). Photograph it.",
         "(section 3, wiring item 2). Lay every lead at least 10 mm from the ten screw holes (sheet H1-1). Photograph it."),
        ("tape CH3, CH5, CH6 and CH8 on H1's top face now; keep CH1, CH2 and CH4)",
         "tape CH3, CH5, CH6 and CH8 on H1's top face now; move CH4 to the band nearest the resistor; keep CH1 and CH2)"),
        ("| CH3 | H1's top face directly over the resistor's centre, X -45.0, Y 70.0 | none |",
         "| CH3 | H1's top face directly over the resistor's centre, X -45.0, Y 70.0 | none |\n"
         "| CH4 | H1's edge over the o-ring nearest the resistor: the top face of the rebated band at X -45.0, Y +129.0 | **70 C** |"),
        ("**Switch off at once if CH7 reaches 110 C**", "**Switch off at once if CH7 reaches 110 C or CH4 reaches 70 C**"),
        ("| H1's edge over the o-ring (CH4) | 70 C | TS3 on H1 (opens by 63 C) |",
         "| H1's edge over the o-ring (CH4) | 70 C | TS3 on H1 (opens by 63 C) in the steady-state steps; in the patch runs the attending operator (CH4 on the band nearest the resistor) |"),
        ("At a limit or a trip: supply off;",
         "TS1 to TS4 act only in the steady-state steps: in the patch runs the heaters are off and the shutdown switches nothing\n(section 6), so every limit there is the operator's.\n\nAt a limit or a trip: supply off;"),
    ])
    edit(OD + "TEST-BRIEF.md", [
        ("stopped at once at 110 C on the resistor's body.",
         "stopped at once at 110 C on the resistor's body or 70 C on\n  H1's edge over the o-ring nearest it (CH4)."),
    ])
    edit(OD + "checks/check-7.md", [
        ("`checks/check-5.md` line 96 quotes the box path `/root/od01b`.",
         "`checks/check-5.md` line 96 quotes the box path (generalised on filing)."),
    ])
    print("patch_od01h: C1, s1 and s2 answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
