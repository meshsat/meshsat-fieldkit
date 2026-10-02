#!/usr/bin/env python3
"""apply_part_identities_block.py: put the Layer 4 power parts' identity block into v2/ecad/tools/pcb_part_identities.yaml (MESHSAT-1357,
Layer 6 record l6pwr, 3 October 2026), or take it out again.

The block `drafted_identities_l4_power` is rendered by l6pwr_parts.py --identities from the record's parts table, so the yaml and the
record cannot disagree (test_l6pwr.py holds that). It sits OUTSIDE `selections:` because its parts are on no committed netlist (they
live in Layer 4's release-guarded drafts): part_identities.py check reads scope, inputs, selections and counts and never this key, so
the identity check stays as it was. build_table.py (stream w5identc) rewrites the file from its DECISIONS and does not carry this
block: after a regeneration, run this script again.

Usage:  apply_part_identities_block.py [TARGET] [--check | --write | --remove]
  TARGET defaults to the repository's v2/ecad/tools/pcb_part_identities.yaml. --check (default) writes nothing and says what --write
  would do. --write appends the block (refused when it is already there: a second application is refused). --remove takes it out.
  Every write asserts the new text differs, re-parses the file with PyYAML, and asserts `selections` and `counts` are byte-for-byte the
  same mapping as before. Exit 0 checked or written; 3 refused."""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
KEY = "drafted_identities_l4_power"
MARK = "\n# ADDED 3 October 2026 (MESHSAT-1357, Layer 6 record l6pwr)."


def render():
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "l6pwr_parts.py"), "--identities"], cwd=TOP, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr); sys.exit(3)
    return r.stdout


def main(argv):
    import yaml
    args = [a for a in argv if not a.startswith("--")]
    target = args[0] if args else os.path.join(TOP, "v2", "ecad", "tools", "pcb_part_identities.yaml")
    mode = "--write" if "--write" in argv else ("--remove" if "--remove" in argv else "--check")
    old = open(target, encoding="utf-8").read()
    before = yaml.safe_load(old)
    present = KEY in before
    if mode == "--remove":
        if not present:
            print("apply_part_identities_block: %s has no %s block: nothing to remove" % (target, KEY)); return 3
        i = old.index(MARK)
        new = old[:i].rstrip("\n") + "\n"
    else:
        if present:
            print("apply_part_identities_block: %s already carries %s: a second application is refused" % (target, KEY)); return 3
        block = render()
        new = old.rstrip("\n") + "\n" + block
    if new == old:
        print("apply_part_identities_block: the new text does not differ: refused"); return 3
    after = yaml.safe_load(new)
    for k in ("scope", "inputs", "rules", "counts", "selections"):
        if json.dumps(before.get(k), sort_keys=True, default=str) != json.dumps(after.get(k), sort_keys=True, default=str):
            print("apply_part_identities_block: %s would change: refused" % k); return 3
    if mode != "--remove" and KEY not in after:
        print("apply_part_identities_block: the block did not parse in: refused"); return 3
    if mode == "--check":
        print("apply_part_identities_block: --check ok: --write would %s the %s block (%d rows); nothing written"
              % ("append", KEY, len((yaml.safe_load(render()) or {}).get(KEY, {}).get("rows", []))))
        return 0
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(new)
    print("apply_part_identities_block: %s %s in %s" % (KEY, "removed from" if mode == "--remove" else "appended to", target))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
