#!/usr/bin/env python3
"""Run test_reliability.py's fixture tests against the UNFIXED reliability.py, to show which of them it fails.

Worker set6fix, MESHSAT-1357, 27 September 2026. The unfixed tool is written outside the tree with
`git show a76a246e:v2/ecad/tools/reliability.py > <dir>/reliability.py`; it is put in `sys.modules` under the
name the test file imports, so the test file itself is the one in the tree, unchanged. Only the fixture tests
are run (each builds its own temporary tree); the test that reads the committed boards is run as well, with the
old tool's paths pointed at this tree's list, netlists and vendor folder. Nothing is written under `v2/ecad`.

Usage: tests_against_old_tool.py <tools dir> <dir holding the unfixed reliability.py>
"""
import os, sys, hashlib, importlib.util


def main(argv):
    tools, old_dir = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    sys.path.insert(0, tools)
    p = os.path.join(old_dir, "reliability.py")
    spec = importlib.util.spec_from_file_location("reliability", p)
    old = importlib.util.module_from_spec(spec); sys.modules["reliability"] = old; spec.loader.exec_module(old)
    # the unfixed tool resolves its defaults beside its own file, which is outside the tree: point them at the tree
    old.ECAD = os.path.dirname(tools)
    old.VENDOR = os.path.normpath(os.path.join(old.ECAD, "..", "vendor"))
    old.REL = os.path.join(tools, "pcb_reliability.yaml")
    t = os.path.join(tools, "tests", "test_reliability.py")
    sp = importlib.util.spec_from_file_location("test_reliability_on_old", t)
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
    assert mod.REL is old, "the test file did not take the unfixed tool"
    print("tool under test: %s sha16 %s, carries identity(): %s"
          % (p, hashlib.sha256(open(p, "rb").read()).hexdigest()[:16], hasattr(old, "identity")))
    ok = bad = 0
    for nm in sorted(dir(mod)):
        if not nm.startswith("t_"): continue
        try:
            getattr(mod, nm)(); ok += 1; print("PASS %s" % nm)
        except Exception as e:
            bad += 1; print("FAIL %s\n     %s: %s" % (nm, type(e).__name__, e))
    print("on the unfixed tool: %d passed, %d failed" % (ok, bad))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
