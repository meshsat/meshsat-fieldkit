#!/usr/bin/env python3
"""scan_printed_pins.py: which committed outputs no longer bind to the tree (MESHSAT-1357, set 28, 3 October 2026; copied unchanged from records/int28b for set 29). An output a record's
reader prints carries the sha of every input it read ("<hex> v2/..." or "v2/... sha256 <hex>"), and _bin/regen_out.py refuses to write
one whose printed pins are not the tree's (its condition R4). This applies R4's own patterns, read from regen_out.py, to every committed
.out under v2/docs and lists each output with the inputs it prints at a sha the tree no longer holds: those are the outputs to regenerate
after a merge. Read only; writes nothing.

Usage: scan_printed_pins.py [<regen_out.py>]   (default: <worktrees>/_bin/regen_out.py beside this worktree)
Exit 0 when every output binds to the tree; 1 when one does not."""
import glob
import hashlib
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()


def main(argv):
    ro = argv[0] if argv else os.path.join(os.path.dirname(TOP), "_bin", "regen_out.py")
    sp = importlib.util.spec_from_file_location("regen_out", ro)
    R = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(R)
    tracked = set(subprocess.run(["git", "ls-files", "v2/docs"], cwd=TOP, capture_output=True, text=True, check=True).stdout.split())
    cache, bad = {}, 0
    for out in sorted(p for p in tracked if p.endswith(".out")):
        text = open(os.path.join(TOP, out), encoding="utf-8", errors="replace").read()
        stale = []
        for path, hx in R.pins(text):
            p = os.path.join(TOP, path)
            if "@" in path or not os.path.isfile(p):
                continue
            if path not in cache:
                cache[path] = hashlib.sha256(open(p, "rb").read()).hexdigest()
            if not cache[path].startswith(hx):
                stale.append((path, hx[:16], cache[path][:16]))
        if stale:
            bad += 1
            print("%s: %d printed pin(s) not the tree's" % (out, len(stale)))
            for path, was, now in sorted(set(stale)):
                print("    %-70s printed %s tree %s" % (path, was, now))
    print("scan_printed_pins: %d committed output(s) do not bind to the tree" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
