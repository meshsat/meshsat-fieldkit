#!/usr/bin/env python3
"""The gate tests (MESHSAT-862, 10 September 2026; plan stage 8, report 1 item 8 and report 2 H1).

Every gate in this pipeline was written against a board and checked by running it on that board, so a gate that stopped
refusing would have been noticed only by a board getting through. These are fixtures: for each rule, an input that must FAIL
and an input that must PASS. No pytest, because the hosts that must run this (the runner, a rented box, the VM) do not all
have one; a test is a function whose name starts with `t_` in a `test_*.py` beside this file, and it fails by raising.

A test that needs `pcbnew` raises `Skip` when it is not importable, so the set runs on the runner too and the full set runs
where KiCad is.

Usage: run.py [name substring ...]     exit 1 if any test failed."""
import sys, os, glob, traceback, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # the tools directory, so a test can import the tool it tests


from harness import Skip   # one class, shared with the tests


def load(path):
    name = "meshsat_test_" + os.path.basename(path)[:-3]
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def main(a):
    files = sorted(glob.glob(os.path.join(HERE, "test_*.py")))
    ok = fail = skip = 0; bad = []
    for f in files:
        try: mod = load(f)
        except Exception as e:
            print("tests: %-40s LOAD FAILED %s" % (os.path.basename(f), e)); fail += 1; bad.append(os.path.basename(f)); continue
        for nm in sorted(dir(mod)):
            if not nm.startswith("t_"): continue
            label = "%s.%s" % (os.path.basename(f)[:-3], nm)
            if a and not any(s in label for s in a): continue
            try:
                (getattr(mod, nm))(); ok += 1; print("tests: %-56s PASS" % label)
            except Skip as e:
                skip += 1; print("tests: %-56s SKIP %s" % (label, e))
            except Exception as e:
                fail += 1; bad.append(label); print("tests: %-56s FAIL %s" % (label, e))
                traceback.print_exc(limit=3)
    print("tests: %d passed, %d failed, %d skipped%s" % (ok, fail, skip, ("; failed: " + ", ".join(bad)) if bad else ""))
    return 1 if fail else 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
