#!/usr/bin/env python3
"""OD-01 after check 11 (`checks/check-11.md`, acceptable yes, MESHSAT-1357, 29 September 2026): its wording items n1 to n3
in the applicability table. n1: the RFQ cuts C4-W only at the build (its line: "rest at build"), so the row does not call
it a mock-up plate; n2: T6 also offers the west plate's footprint, which the west RF re-plan may change; n3: the west
block is in addition to the east one (the pockets are 240 mm apart), not beside it. Text only; not re-checked (wording,
no figure, gate or step changed). Old texts matched with any whitespace between words, each exactly once; refuses a
second run. Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/docs/records/od01/TEST-PROCEDURE.md")


def refuse(m):
    print("patch_od01l: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new):
    pat = r"\s+".join(re.escape(w) for w in old.split())
    hits = list(re.finditer(pat, t))
    if len(hits) != 1: refuse("expected once, found %d: %r" % (len(hits), old[:70]))
    m = hits[0]
    return t[:m.start()] + new + t[m.end():]


def main():
    t = open(P, encoding="utf-8").read()
    if "in addition to the east one" in t: refuse("already applied")
    t2 = once(t, "a second 4S3P block in the west pocket beside the east one,",
              "a second 4S3P block in the west pocket in addition to the east one (the pockets are about 240 mm apart),")
    t2 = once(t2, "| C4-W (west entry plate) for the mock-up | no, as the kit's plate |",
              "| C4-W (west entry plate) | no, as drawn |")
    t2 = once(t2, "C4-W as drawn is a mock-up plate; C4-E is unchanged |",
              "C4-W as drawn waits on that re-plan (the RFQ cuts it only at the build); C4-E is unchanged |")
    t2 = once(t2, "so T6's open-lid reading at Peli's stop bounds Option A(i) unless T-A1-3 finds otherwise |",
              "so T6's open-lid reading at Peli's stop bounds Option A(i) unless T-A1-3 finds otherwise; T6's offer of the west\nentry plate's footprint waits on the west RF re-plan |")
    if any(d in t2 for d in ("—", "–")): refuse("a dash")
    open(P, "w", encoding="utf-8").write(t2)
    print("patch_od01l: n1 to n3 answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
