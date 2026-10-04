#!/usr/bin/env python3
"""apply_layer_status_set29b.py: two rows of LAYER-STATUS.md's "After set 29" tables stated as the verdicts read (MESHSAT-1357, integration
set 29, 4 October 2026; the owner's execution constitution, section 6: a coordinator's verification never reads as acceptance beside
an independent rejection; and the owner's instruction of the same day: FAN_OK rejected).

  Row 4.10: L9P-F02's coordinator check was printed alone ("CLOSED AS CONDITIONAL"); the collaborator's two verdicts (NOT CONFIRMED,
            then NOT CLOSED, filed in records/l8r2/checks/) are restated beside it, and the coordinator's check is named for what it is.
  Row 4.13 to 4.18: D-17's design-out (the fans' supplies off while the PA keys, FAN_OK) was printed as CONDITIONAL on R-213; it is
            REJECTED: the collaborator's advisory challenge of 4 October 2026 found it not supported as proposed, and the owner kept it
            rejected. D-17 stays OPEN; its correction is T5 of the plan of 4 October.
Run from the repository root: apply_layer_status_set29b.py [--check | --write]; each old text once; a second run exits 3."""
import re
import sys

PATH = "v2/docs/handover/LAYER-STATUS.md"
EDITS = [
    ("CONDITIONAL on C4-1 to C4-6, the coordinator's closing check CLOSED AS CONDITIONAL (`records/l8r2/checks/check-l9pf02-coordinator.md`), "
     "OPEN in the register until the drafts are applied and C4-1 to C4-6 pass.",
     "CONDITIONAL on C4-1 to C4-6. The collaborator's focused check read NOT CONFIRMED and its targeted recheck NOT CLOSED "
     "(`records/l8r2/checks/astra-check-l9pf02-1.md` and `-2.md`, AI reviews); each item was corrected afterwards and no independent "
     "check has read the corrections, so the correction is UNVERIFIED; the coordinator's own reading (`records/l8r2/checks/check-l9pf02-coordinator.md`, "
     "not an independent check) finds the items answered, CONDITIONAL on C4-1 to C4-6. OPEN in the register until the drafts are applied "
     "and C4-1 to C4-6 pass."),
    ("(L4-E9 round 8 withdrew round 7's raised floor; its one design-out attempt, the five fans' supplies off while the PA keys, CONDITIONAL "
     "on the 60 s fan-stop test R-213);",
     "(L4-E9 round 8 withdrew round 7's raised floor; its one design-out attempt, the five fans' supplies off while the PA keys (FAN_OK), is "
     "REJECTED: the collaborator's advisory challenge of 4 October 2026 found it not supported as proposed and the owner kept it rejected; "
     "the correction is the plan's T5 on the all-transmit case as REQ-018 and CONOPS define it);"),
]


def main(argv):
    t = open(PATH, encoding="utf-8").read()
    if "is REJECTED: the collaborator's advisory challenge" in t:
        sys.stderr.write("apply_layer_status_set29b: already applied\n")
        return 3
    for old, new in EDITS:
        if t.count(old) != 1:
            sys.stderr.write("apply_layer_status_set29b: REFUSED: %d occurrence(s) of %r\n" % (t.count(old), old[:70]))
            return 1
        assert new != old
        t = t.replace(old, new)
    if re.search("[–—]", t):
        sys.stderr.write("apply_layer_status_set29b: REFUSED: a dash character\n")
        return 1
    if "--write" in argv:
        open(PATH, "w", encoding="utf-8").write(t)
    print("apply_layer_status_set29b: %s, %d edit(s)" % ("WRITTEN" if "--write" in argv else "CHECK OK", len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
