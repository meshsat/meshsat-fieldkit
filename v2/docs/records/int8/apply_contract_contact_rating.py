#!/usr/bin/env python3
"""IF-AB-POWER's contact_rating line in tools/pcb_interfaces.yaml said the JST VH document was not held (MESHSAT-1357,
set 7, 28 September 2026; the Codex pilot's correction item M8 and its check). The catalogue is held at
v2/vendor/connectors/jst-vh-catalogue.pdf: page 1 states 10 A per contact when using AWG 16 with the standard header and
7 A when using AWG 18 with the shrouded header; page 3 lists the fitted B2P-VH standard header. So the AWG 18 lead of
J_54V on the standard header carries no stated rating (INCONCLUSIVE, as the pilot's record says). The contract file is
a configuration input of interfaces.py (INT-001), so INT-001 is re-taken with the set's box re-take. Asserts the old
line once, parses the file after, refuses a second run. Run from the repository root: python3 <this file>."""
import os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/pcb_interfaces.yaml")
OLD = '      contact_rating: "JST-VH is a 10 A class family per the generator descriptions; datasheet not held (TBD)"\n'
NEW = ('      contact_rating: "JST VH catalogue held (v2/vendor/connectors/jst-vh-catalogue.pdf, page 1): 10 A per contact when\n'
       '        using AWG 16 with the standard header, which the four 5 V leads are; 7 A is stated for AWG 18 with the shrouded\n'
       '        header only, so the fitted B2P-VH standard header with AWG 18 on J_54V carries no stated rating (INCONCLUSIVE;\n'
       '        v2/docs/records/cx1/ANALYSIS.md)"\n')


def main():
    t = open(P, encoding="utf-8").read()
    if t.count(OLD) != 1:
        print("apply_contract_contact_rating: REFUSED: the old line occurs %d time(s) (a second run?)" % t.count(OLD)); return 2
    before = yaml.safe_load(t)
    out = t.replace(OLD, NEW)
    after = yaml.safe_load(out)
    def find(d):
        for c in d["contracts"] if isinstance(d, dict) and "contracts" in d else []:
            if c.get("id") == "IF-AB-POWER": return c
    b, a = find(before), find(after)
    if b is None or a is None:
        # the file's shape may differ: fall back to a whole-document comparison
        diffs = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
        if not diffs: print("apply_contract_contact_rating: REFUSED: nothing changed"); return 2
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: print("REFUSED: re-parse differs"); return 2
    print("apply_contract_contact_rating: IF-AB-POWER contact_rating rewritten from the held catalogue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
