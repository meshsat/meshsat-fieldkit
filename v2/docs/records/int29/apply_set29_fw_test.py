#!/usr/bin/env python3
"""apply_set29_fw_test.py: the panel firmware's contract test reads FW-C05's row as Layer 5's F-15 follow-up words it (MESHSAT-1357,
integration set 29, 4 October 2026; the coordinator's integration correction).

`test_fw_panel.t_contract_f14_one_slot_fault_rule` was written on the firmware's round 4 line against Layer 5's round 4 at `0b3c058c`.
Layer 5's follow-up `3758328f` then answered the firmware's own findings F-15 and S-37 and reworded the row's last clause: the spent
retry and the left-off state are kept BESIDE the wipe-pending record (never inside its journal) and cleared only on a power-on
reset, read as CHIP_RESET HAD_POR set and the watchdog's REASON zero. The test still held the first wording as one literal, so it
failed on the merged tree with the rule's figures unchanged. The basis for the changed expectation is the contract row itself;
the measured figures and every other assertion of the test are untouched.

Run from the repository root: apply_set29_fw_test.py [--check | --write]; a second run exits 3."""
import ast
import sys

PATH = "v2/ecad/tools/tests/test_fw_panel.py"
OLD = ('    keep = ("keep the spent retry and the left-off state with the wipe-pending record across a watchdog, RUN or SWD reset, "\n'
       '            "cleared only by a power-on reset")\n'
       '    rearm = "each act re-arming the retry" in row\n'
       '    assert lost and rule and keep in row and rearm, (\n')
NEW = ('    # the row as Layer 5\'s F-15 follow-up words it (3758328f): kept beside the wipe record, cleared only on a power-on reset\n'
       '    keep = ("keep the spent retry and the left-off state beside the wipe-pending record",\n'
       '            "across a watchdog, RUN or SWD reset; clear them only on a power-on reset",\n'
       '            "read as CHIP_RESET HAD_POR set and the watchdog\'s REASON zero")\n'
       '    rearm = "each act re-arming the retry" in row\n'
       '    assert lost and rule and all(k in row for k in keep) and rearm, (\n')


def main(argv):
    t = open(PATH, encoding="utf-8").read()
    if NEW in t:
        sys.stderr.write("apply_set29_fw_test: already applied\n")
        return 3
    if t.count(OLD) != 1:
        sys.stderr.write("apply_set29_fw_test: REFUSED: %d occurrence(s) of the old text\n" % t.count(OLD))
        return 1
    t = t.replace(OLD, NEW)
    ast.parse(t)
    if "--write" in argv:
        open(PATH, "w", encoding="utf-8").write(t)
    print("apply_set29_fw_test: %s" % ("WRITTEN" if "--write" in argv else "CHECK OK"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
