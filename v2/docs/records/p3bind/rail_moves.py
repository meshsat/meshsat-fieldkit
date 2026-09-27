#!/usr/bin/env python3
"""Which rows of each board's power table moved between three candidates (p3bind, MESHSAT-1357, 27 September 2026).

The layout constraint sheets mark and explain every row that moved. This is how the moves were found: each input of
`v2/docs/layout-constraints/calc/rail_widths.py` (the intent file and the netlist of each board, board E5's board file
and the energy chain) is read out of git at three commits, written into a temporary tree, and the CURRENT calculation
is run on each. So the comparison is of the inputs alone: the model, the pack-path rule and the output's format are the
same in the three runs, and a difference is a difference of a declaration.

  e3aedb25  the commit the sheets were first written against
  ef144760  the H2 line the sheets were re-bound to by hand (ecfe5414)
  760d7f41  the set 6 candidate this binding is read on

It writes nothing in the tree: it prints. Usage: rail_moves.py [--json]
"""
import os, sys, json, shutil, tempfile, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "v2", "ecad", "tools"))
import constraints_bound as CB

COMMITS = (("e3aedb25", "as first written"), ("ef144760", "the H2 line"), ("760d7f41", "set 6"))


def show(commit, rel):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def tree_at(commit, RW):
    d = tempfile.mkdtemp(prefix="p3bind-%s-" % commit)
    rels = []
    for letter in RW.ORDER:
        if letter in RW.NO_INTENT:
            rels += [RW.NO_INTENT[letter]["board_file"], RW.NO_INTENT[letter]["chain"]]
        else:
            rels += [RW.BOARDS[letter][0], RW.BOARDS[letter][0].replace("-intent.json", ".net")]
    missing = []
    for rel in rels:
        raw = show(commit, rel)
        if raw is None: missing.append(rel); continue
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f: f.write(raw)
    return d, missing


def main(argv):
    RW = CB.load_calc()
    runs = {}
    for commit, _what in COMMITS:
        d, missing = tree_at(commit, RW)
        try:
            runs[commit] = {"missing": missing, "boards": {}}
            for letter in RW.ORDER:
                try: t = RW.rows(letter, d)
                except (OSError, SystemExit, ValueError, KeyError) as e:
                    runs[commit]["boards"][letter] = {"error": "%s: %s" % (type(e).__name__, e)}; continue
                rows = {c[0]: c for c in (RW.cells(r) for r in t["rows"])}
                sized = {c[0]: c for c in (RW.cells_sized(r) for r in t["sized"])}
                runs[commit]["boards"][letter] = {"inputs": t["inputs"], "rows": rows, "sized": sized,
                                                  "order": list(rows)}
        finally:
            shutil.rmtree(d)
    if "--json" in argv:
        print(json.dumps(runs, indent=1)); return 0
    for letter in RW.ORDER:
        print("## Board %s" % letter.upper())
        print()
        for commit, what in COMMITS:
            b = runs[commit]["boards"][letter]
            if "error" in b: print("- `%s` (%s): the calculation could not be run: %s" % (commit, what, b["error"])); continue
            print("- `%s` (%s): %s; %d row(s)" % (commit, what, "; ".join("%s %s" % (r, s) for r, _p, s in b["inputs"]), len(b["rows"])))
        print()
        for (c0, w0), (c1, w1) in zip(COMMITS, COMMITS[1:]):
            a, b = runs[c0]["boards"][letter], runs[c1]["boards"][letter]
            if "error" in a or "error" in b: continue
            new = [r for r in b["order"] if r not in a["rows"]]
            gone = [r for r in a["order"] if r not in b["rows"]]
            moved = [r for r in b["order"] if r in a["rows"] and a["rows"][r] != b["rows"][r]]
            print("From `%s` to `%s` (%s): %d new, %d gone, %d moved, %d the same." % (
                c0, c1, w1, len(new), len(gone), len(moved), len(b["order"]) - len(new) - len(moved)))
            for r in new: print("  - NEW   %s" % " | ".join(b["rows"][r]))
            for r in gone: print("  - GONE  %s" % " | ".join(a["rows"][r]))
            for r in moved:
                print("  - MOVED %s" % r)
                for k, h in enumerate(RW.HEAD):
                    if k and a["rows"][r][k] != b["rows"][r][k]:
                        print("      %s: %s -> %s" % (h, a["rows"][r][k], b["rows"][r][k]))
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
