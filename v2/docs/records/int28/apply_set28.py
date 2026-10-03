#!/usr/bin/env python3
"""apply_set28.py: the set 28 preparation's steps after the three merges, in their dependency order, each idempotent (MESHSAT-1357,
3 October 2026; records/int28/README.md explains the set). Run from anywhere after fnd/l5pwr, fnd/l6pwr and fnd/l7pwr are merged
(the conflicts of sources.txt and PROCUREMENT.md resolved with resolve_both_sides.py), on this branch or on it re-based onto set 27:

  0  stage_held_sheets.py --write           the makers' held-back sheets from sibling checkouts on this host, verified by the pins
                                            (the L4 readers refuse without them; nothing fetched)
  1  apply_set28_rebind.py --write          L5-F02: CFL-001, CFL-005, CFL-014, CFL-015, CFL-016 rebound to the merged PANEL.md
  2  rules_lib.py requirements              must read 0 errors
  3  rules_render.py --requirements         REQUIREMENTS-TRACE.md re-rendered (it prints the five entries)
  4  apply_set28_repins.py --write          L5-F01: L4-E5, L4-E11, L4-E9 re-pinned (reqs included) and regenerated through regen_out.py
  5  l6pwr/apply_part_identities_block.py   the identity block present in pcb_part_identities.yaml (refused as already there is fine)
  6  the checks: rules_render.py --check, rules_render.py --requirements --check, decisions_render.py --check, part_identities.py check

The rebind comes before the re-pins because L4-E9 and L4-E11 pin pcb_requirements.yaml. A step that reports "already applied" (exit 3)
is accepted and the next runs; any other refusal stops here with the step named. Usage: apply_set28.py [--skip-regen]"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2", "ecad", "tools")
L6 = os.path.join(TOP, "v2", "docs", "records", "l6pwr", "apply_part_identities_block.py")


def run(label, args, cwd=TOP, ok_already=("already applied", "already carries", "already bound", "already identical"), must=None):
    print("== %s" % label)
    r = subprocess.run([sys.executable, "-B"] + args, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print("\n".join("   " + l for l in out.splitlines()[-12:]))
    if r.returncode == 0:
        if must and must not in out:
            print("apply_set28: STOPPED at %s: %r not in its output" % (label, must)); sys.exit(1)
        return out
    if r.returncode == 3 and any(k in out for k in ok_already):
        return out
    print("apply_set28: STOPPED at %s (exit %d)" % (label, r.returncode))
    sys.exit(1)


def main(argv):
    skip = "--skip-regen" in argv
    run("0 held sheets", [os.path.join(HERE, "stage_held_sheets.py"), "--write"], ok_already=("missing",))   # a sheet outside the chain may be absent here
    run("1 rebind (L5-F02)", [os.path.join(HERE, "apply_set28_rebind.py"), "--write"])
    run("2 registry", ["rules_lib.py", "requirements"], cwd=TOOLS, must=" 0 error(s)")
    run("3 requirements trace", ["rules_render.py", "--requirements"], cwd=TOOLS)
    run("4 re-pins and regeneration (L5-F01)", [os.path.join(HERE, "apply_set28_repins.py"), "--write"] + (["--no-regen"] if skip else []))
    run("5 identity block", [L6, "--check"])
    run("6a rules_render --check", ["rules_render.py", "--check"], cwd=TOOLS, ok_already=())
    run("6b requirements trace --check", ["rules_render.py", "--requirements", "--check"], cwd=TOOLS, ok_already=())
    run("6c decisions_render --check", ["decisions_render.py", "--check"], cwd=TOOLS, ok_already=())
    r = subprocess.run([sys.executable, "-B", "part_identities.py", "check"], cwd=TOOLS, capture_output=True, text=True)
    print("== 6d part_identities check (exit %d)\n   %s" % (r.returncode, (r.stdout.strip().splitlines() or [""])[-1]))
    print("apply_set28: done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
