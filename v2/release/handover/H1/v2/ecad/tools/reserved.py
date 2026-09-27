#!/usr/bin/env python3
"""The never-auto floor: which changes are the owner's, checked against a diff (MESHSAT-862, 11 September 2026).

Territory Grounder's floor sits ABOVE its posture check, so a floor-class operation is refused identically in Shadow
and in Full-auto. That ordering is the point: a floor that a mode can lift is not a floor. This does the same, and
`t_the_floor_is_checked_before_the_mode` holds it there.

The classes are data, in `reserved.json`, and each is a file pattern plus the pattern that identifies the reserved
LINES in it. File level would be useless: `gen_pcb_b3.py` holds the net classes and the region packer and most of the
placement, and only the first two are reserved.

Usage:
  reserved.py --diff [<git range>]     the working tree, or a range; exit 1 if a reserved line changed
  reserved.py --files a.py b.py        whole files, for a caller that has no diff
  reserved.py --list                   the floor, so it can be read without running anything

A refusal is not a failure to be worked around: it means the change is the owner's to make. Under unattended
operation the caller writes it to the decisions file with its evidence and carries on with everything else.
"""
import os, re, sys, json, fnmatch, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR = os.path.join(HERE, "reserved.json")


def load():
    d = json.load(open(FLOOR))
    return [(c["name"], c["why"], [(g, re.compile(p)) for g, p in c["sites"]]) for c in d["classes"]]


def _matches(rel, line, classes):
    """Every reserved class this changed line belongs to."""
    out = []
    for name, why, sites in classes:
        for glob, pat in sites:
            # A GLOB WITH A DIRECTORY IN IT MUST STILL MATCH. `git diff` gives repo-relative paths
            # (v2/ecad/tools/boards/b.json), and matching only the whole path or the basename meant
            # `boards/*.json` and `../docs/...` matched NOTHING: three reserved classes had never once
            # fired (red team round three L5, found by the test that asks whether each pattern still
            # matches a line). The glob is tried against the path, its basename, and as a suffix.
            if (fnmatch.fnmatch(rel, glob) or fnmatch.fnmatch(os.path.basename(rel), glob)
                    or fnmatch.fnmatch(rel, "*/" + glob.lstrip("./"))):
                if pat.search(line): out.append((name, why)); break
    return out


def changed_lines(rng=None):
    """[(path, line)] of every ADDED or REMOVED line, from the working tree or a range.

    A PURELY ADDED SECTION OF THE DESIGN RECORD IS NOT A CHANGE TO IT (16 September 2026). The design-record
    class says what it means in its own words: "the appendix is the record of what was ruled and measured; a
    machine may ADD a measurement section, never change a number in one". The check could not tell the two
    apart, because a new heading is an added line like any other, so every night's own record entry was
    refused by the floor that permits it. An added line is dropped only when the file REMOVED nothing that
    matches the same class: rewrite a section, or delete one, and both the removal and the replacement are
    hits again. Every other class keeps both signs, and so does this one the moment anything is taken away.
    """
    argv = ["git", "-C", HERE, "diff", "-U0"] + ([rng] if rng else [])
    txt = subprocess.run(argv, capture_output=True, text=True, timeout=120).stdout
    if not txt.strip():
        txt = subprocess.run(["git", "-C", HERE, "diff", "-U0", "--cached"], capture_output=True, text=True, timeout=120).stdout
    out, cur = [], None
    for line in txt.splitlines():
        if line.startswith("+++ b/"): cur = line[6:]; continue
        if line.startswith("--- ") or line.startswith("diff ") or line.startswith("@@"): continue
        if cur and (line.startswith("+") or line.startswith("-")):
            out.append((cur, line[1:], line[0]))
    return out


ADDITIVE = ("the design record",)   # classes whose own words permit a machine to ADD, never to edit


def drop_pure_additions(pairs, classes):
    """Remove added lines of an ADDITIVE class from a file that removed none of that class's lines."""
    removed = set()
    for rel, line, sign in pairs:
        if sign != "-": continue
        for name, _why in _matches(rel, line, classes):
            removed.add((rel, name))
    keep = []
    for rel, line, sign in pairs:
        if sign == "+":
            names = [n for n, _w in _matches(rel, line, classes)]
            if names and all(n in ADDITIVE and (rel, n) not in removed for n in names): continue
        keep.append((rel, line))
    return keep


def whole_files(paths):
    out = []
    for p in paths:
        try: out += [(p, l) for l in open(p, errors="replace").read().splitlines()]
        except Exception: pass
    return out


def main(a):
    classes = load()
    if "--list" in a:
        for name, why, sites in classes:
            print("  %s\n     %s\n     %s" % (name, why, ", ".join("%s: %s" % (g, p.pattern) for g, p in sites)))
        return 0
    if "--files" in a: pairs = whole_files(a[a.index("--files") + 1:]); what = "%d file(s)" % len(a[a.index("--files") + 1:])
    else:
        rng = a[a.index("--diff") + 1] if "--diff" in a and len(a) > a.index("--diff") + 1 else None
        pairs = drop_pure_additions(changed_lines(rng), classes); what = rng or "the working tree"
    hits, seen = [], set()
    for path, line in pairs:
        rel = path.replace("v2/ecad/tools/", "")
        for name, why in _matches(rel, line, classes):
            k = (name, rel, line.strip()[:90])
            if k in seen: continue
            seen.add(k); hits.append("%s | %s | %s" % (name, rel, line.strip()[:90]))
    for h in hits[:40]: print("reserved: OWNER  " + h)
    print("reserved: %d reserved line(s) changed in %s, over %d class(es)" % (len(hits), what, len(classes)))
    if hits:
        print("reserved: this change is the owner's to make. Write it to the decisions file with its evidence")
        print("reserved: and carry on with the work that does not touch it; do not work around the floor.")
    # Nothing examined is not a clean bill: "0 reserved lines of 0" is what a clean tree, a broken diff and a
    # wrong range all produce identically, which is the shape this pipeline spent stage 0 removing.
    if not pairs:
        print("reserved: nothing to examine in %s, so nothing was judged" % what)
        return verdict.write("reserved", verdict.INCONCLUSIVE, counts={"classes": len(classes)}, denominator=0,
                             note="no changed line in %s: a clean tree and a broken diff look the same here" % what)
    return verdict.write("reserved", verdict.PASS if not hits else verdict.FAIL,
                         counts={"reserved_lines": len(hits), "classes": len(classes), "lines_examined": len(pairs)},
                         denominator=len(pairs), evidence=hits,
                         note="the floor is checked before any mode or posture, as Territory Grounder orders it")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
