#!/usr/bin/env python3
"""OD-01, the owner's review of the export at 32345b84 (29 September 2026, MESHSAT-1357): one local correction. The T6 row of
TEST-PROCEDURE.md section 1's applicability table read "yes, as a bound (INFERRED)" while its own text deferred the west entry
plate's footprint, and a physical newline split the row, so under GitHub Flavored Markdown (spec section 4.10) its last words
became a separate row. The row is replaced by one physical line: T6 is PARTLY; its unchanged parts, the west footprint that
waits on the west RF re-plan, and the lid clearance that stays INFERRED and uncredited until T-A1-3 or a recorded geometric
argument are distinguished. Nothing else changes. Refuses a second run. Run: python3 <this file>."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/docs/records/od01/TEST-PROCEDURE.md")
OLD = ("| Test B: T6 | yes, as a bound (INFERRED) | the lid pack is inside the lid and leaves its outer skin unchanged; the stay "
       "stops the lid at 100 degrees, short of Peli's stop, so T6's open-lid reading at Peli's stop bounds Option A(i) unless "
       "T-A1-3 finds otherwise; T6's offer of the west\nentry plate's footprint waits on the west RF re-plan |")
NEW = ("| Test B: T6 | partly | unchanged: the connector plate's and the east entry plate's footprints and Peli's four frame "
       "screws against the outside features; waits on the west RF re-plan: the west entry plate's footprint; INFERRED and not "
       "credited: the open lid clear of the mated plugs with the lid pack in the lid, until T-A1-3 measures the lid's stop and "
       "hinge axis or a geometric argument is recorded (the lid pack is inside the lid and leaves its outer skin unchanged, and "
       "the proposed stay would stop the lid at 100 degrees, short of Peli's stop; neither is a measured clearance) |")


def main():
    t = open(P, encoding="utf-8").read()
    if NEW in t: print("patch_od01m: REFUSED: already applied"); return 2
    if t.count(OLD) != 1: print("patch_od01m: REFUSED: the T6 row is not found once"); return 2
    t2 = t.replace(OLD, NEW)
    if "\n" in NEW or any(d in t2 for d in ("—", "–")): print("patch_od01m: REFUSED: a newline or a dash"); return 2
    open(P, "w", encoding="utf-8").write(t2)
    print("patch_od01m: the T6 row is one physical line and reads partly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
