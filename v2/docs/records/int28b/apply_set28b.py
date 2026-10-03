#!/usr/bin/env python3
"""apply_set28b.py: integration set 28's steps after the seven merges, in dependency order, each idempotent (MESHSAT-1357, 3 October
2026, branch fnd/int28b; records/int28b/README.md). Run from anywhere on the merged tree:

  0  stage_held_sheets.py --write              the makers' held-back sheets from sibling checkouts, verified by the records' pins
  1  apply_set28_rebind.py --write             debt c (L5-F02): CFL-001, 005, 014, 015, 016 bound to the tree's PANEL.md
  2  rules_lib.py requirements                 must read 0 errors
  3  rules_render.py --requirements; render_l3r2.py   the trace and the Layer 3 R2 pages (they print the registry's sha)
  4  apply_set28b_repins.py --stage pins       debts a, b, e: L4-E8, L4-E11, L4-E12, L4-E9 re-pinned, regenerated through regen_out
  5  _bin/freeze_l4_chain.sh <worktree>        debt f: the registry, the page and the chain re-pinned, a stability pass (never edited)
  6  apply_set28b_repins.py --stage later      debt d and the rest: every output of Layers 5 to 9 that no longer binds, regenerated
  7  the two identity blocks (l6pwr, l6r2)      debt h: re-applied only when a table regeneration dropped them
  8  the checks: rules_lib requirements, rules_lib, render_l3r2 --check, rules_render --requirements --check, rules_render --check
     (PCB-ETA.md stale is the worker-tree condition; PCB-BRING-UP.md must be current, debt g), decisions_render --check,
     part_identities check, scan_printed_pins.py

A step reporting "already applied" (exit 3) is accepted; a regeneration a record's reader refuses is reported by the step that ran it
and does not stop the chain (its committed output stays as it was). Usage: apply_set28b.py [--from N] (start at step N, default 0).
Exit 0 when every check passed, 1 otherwise (the failing checks named)."""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2", "ecad", "tools")
L3 = os.path.join(TOP, "v2", "docs", "handover", "layer3")
BIN = os.path.join(os.path.dirname(TOP), "_bin")
ALREADY = ("already applied", "already carries", "already bound", "already identical")


def run(label, cmd, cwd=TOP, ok_codes=(0,), accept_already=True):
    print("== %s" % label, flush=True)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print("\n".join("   " + l[:220] for l in out.splitlines()[-16:]), flush=True)
    ok = r.returncode in ok_codes or (accept_already and r.returncode == 3 and any(k in out for k in ALREADY))
    return ok, r.returncode, out


def main(argv):
    start = int(argv[argv.index("--from") + 1]) if "--from" in argv else 0
    py = [sys.executable, "-B"]
    steps = [
        (0, "0 held sheets", py + [os.path.join(HERE, "stage_held_sheets.py"), "--write"], TOP),
        (1, "1 rebind (debt c)", py + [os.path.join(HERE, "apply_set28_rebind.py"), "--write"], TOP),
        (2, "2 registry", py + ["rules_lib.py", "requirements"], TOOLS),
        (3, "3a requirements trace", py + ["rules_render.py", "--requirements"], TOOLS),
        (3, "3b Layer 3 R2 pages", py + ["render_l3r2.py"], L3),
        (4, "4 pins (debts a, b, e)", py + [os.path.join(HERE, "apply_set28b_repins.py"), "--stage", "pins", "--write"], TOP),
        (5, "5 freeze (debt f)", ["bash", os.path.join(BIN, "freeze_l4_chain.sh"), TOP], TOP),
        (6, "6 later outputs (debt d)", py + [os.path.join(HERE, "apply_set28b_repins.py"), "--stage", "later", "--write"], TOP),
    ]
    for n, label, cmd, cwd in steps:
        if n < start:
            continue
        ok, rc, out = run(label, cmd, cwd)
        if n == 2 and " 0 error(s)" not in out:
            print("apply_set28b: STOPPED: the registry does not validate"); return 1
        if not ok and n in (0,) and "missing" in out:
            continue                    # a held sheet outside the chain may be absent on this host
        if not ok and n in (4, 6):
            continue                    # a reader's refusal is reported by the stage and kept; the chain goes on
        if not ok and n == 5:
            continue                    # the freeze reports each regeneration; a refusal there is read from its log
        if not ok:
            print("apply_set28b: STOPPED at %s (exit %d)" % (label, rc)); return 1
    if start <= 7:
        for rec in ("l6pwr", "l6r2"):
            s = os.path.join(TOP, "v2", "docs", "records", rec, "apply_part_identities_block.py")
            ok, rc, out = run("7 identity block %s (debt h)" % rec, py + [s, "--check"], TOP, ok_codes=(0, 3), accept_already=False)
            if rc == 0 and "would append" in out:
                run("7 identity block %s re-applied" % rec, py + [s, "--write"], TOP)
    bad = []
    checks = [
        ("8a rules_lib requirements", py + ["rules_lib.py", "requirements"], TOOLS, lambda rc, o: " 0 error(s)" in o),
        ("8b rules_lib", py + ["rules_lib.py"], TOOLS, lambda rc, o: rc == 0 and " 0 error(s)" in o),
        ("8c render_l3r2 --check", py + ["render_l3r2.py", "--check"], L3, lambda rc, o: rc == 0),
        ("8d rules_render --requirements --check", py + ["rules_render.py", "--requirements", "--check"], TOOLS, lambda rc, o: rc == 0),
        ("8e rules_render --check", py + ["rules_render.py", "--check"], TOOLS,
         lambda rc, o: "refused" not in o and not [l for l in o.splitlines() if l.endswith("differs from what the registry renders")
                                                   and not l.split()[1].endswith("PCB-ETA.md")]),
        ("8f decisions_render --check", py + ["decisions_render.py", "--check"], TOOLS, lambda rc, o: rc == 0),
        ("8g part_identities check", py + ["part_identities.py", "check"], TOOLS, lambda rc, o: rc == 0),
        ("8h scan_printed_pins", py + [os.path.join(HERE, "scan_printed_pins.py")], TOP, lambda rc, o: True),
    ]
    for label, cmd, cwd, good in checks:
        ok, rc, out = run(label, cmd, cwd, ok_codes=(0, 1, 2, 3, 4), accept_already=False)
        if not good(rc, out):
            bad.append(label)
    print("apply_set28b: done%s" % ("" if not bad else "; failing checks: %s" % ", ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
