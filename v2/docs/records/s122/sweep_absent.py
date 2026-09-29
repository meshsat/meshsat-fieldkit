#!/usr/bin/env python3
"""Stream s122, round 3 (S-122, MESHSAT-1357): the sweep of check-s122-2's B1 class. Reads a `verdicts.out` (the file
committed at a git revision, or a path) and counts the sentences of CONOPS.md that state something is absent, owed, not
drawn or not connected (the words of `verdicts.ABSENT`), by verdict, and lists them. Run:
python3 sweep_absent.py [<revision> | <path>] (default: the working file)."""
import collections, os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402

REL = "v2/docs/records/s122/verdicts.out"


def load(arg):
    if arg is None: return open(os.path.join(HERE, "verdicts.out"), encoding="utf-8").read()
    if os.path.exists(arg): return open(arg, encoding="utf-8").read()
    return subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (arg, REL)], capture_output=True, text=True, check=True).stdout


def sweep(txt):
    out, cur = [], None
    for line in txt.splitlines():
        m = re.match(r"^CONOPS\.md#(\S+) \[([0-9a-f]{10})\] (TRUE|STALE|BASELINE|NOT DERIVABLE|UNJUDGED)$", line)
        if m:
            cur = [m.group(1), m.group(2), m.group(3), None]
            continue
        if cur and cur[3] is None and line.startswith("    "):
            cur[3] = line.strip()
            if V.ABSENT.search(cur[3]): out.append(tuple(cur))
            cur = None
    return out


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    rows = sweep(load(arg))
    c = collections.Counter(r[2] for r in rows)
    print("CONOPS.md sentences stating something absent, owed, not drawn or not connected (%s): %d; %s" % (
        arg or "working verdicts.out", len(rows), ", ".join("%s %d" % (k, c[k]) for k in
                                                          ("TRUE", "STALE", "BASELINE", "NOT DERIVABLE", "UNJUDGED"))))
    for sid, d, v, s in rows:
        print("  %s [%s] %s: %s" % (sid, d, v, s[:160]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
