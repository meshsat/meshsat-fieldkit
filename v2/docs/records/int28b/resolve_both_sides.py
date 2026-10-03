#!/usr/bin/env python3
"""resolve_both_sides.py: resolve a merge conflict in which both sides APPENDED at the same place by keeping both sides, ours first
(MESHSAT-1357, set 28, 3 October 2026: fnd/l6pwr and fnd/l7pwr both appended to v2/vendor/sources.txt and v2/docs/parts/PROCUREMENT.md),
or, with --ours, a conflict between two PIN lines of a Layer 4 reader by keeping ours (set 28's integration of 3 October 2026, int28b:
the frozen set 27 chain's pins against the superseded int28 preparation's; the re-pin script then reads every pin from the tree).

  resolve_both_sides.py <file> [--md | --ours]

Every conflict block (<<<<<<< ... ======= ... >>>>>>>) is replaced by its OURS lines followed by its THEIRS lines; with --md one
empty line separates the two (a Markdown heading needs it); with --ours by its OURS lines alone (only for a block whose lines are all
pins, `"<key>": ("v2/...", "<64 hex>"),`: refused otherwise). Without --ours no line of either side is dropped or changed. Refuses (exit 3) when the
file carries no conflict markers (already resolved), when a block is malformed, or when the new text does not differ. After writing it
re-reads the file and asserts no marker is left and that every OURS and THEIRS line is present in order. Exit 0 written."""
import os
import sys

sys.dont_write_bytecode = True
MARK = ("<<<<<<< ", "=======", ">>>>>>> ")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__); return 2
    path, md, ours_only = args[0], "--md" in argv, "--ours" in argv
    import re
    pin = re.compile(r'^\s+"[A-Za-z0-9_]+": \("v2/[^"]+", "[0-9a-f]{64}"\),\s*$')
    old = open(path, encoding="utf-8").read()
    lines = old.split("\n")
    out, kept, i, blocks = [], [], 0, 0
    while i < len(lines):
        if lines[i].startswith(MARK[0]):
            j = i + 1
            ours = []
            while j < len(lines) and lines[j] != MARK[1]:
                ours.append(lines[j]); j += 1
            if j >= len(lines):
                print("resolve_both_sides: %s: a block has no ======= line: refused" % path); return 3
            k = j + 1
            theirs = []
            while k < len(lines) and not lines[k].startswith(MARK[2]):
                theirs.append(lines[k]); k += 1
            if k >= len(lines):
                print("resolve_both_sides: %s: a block has no >>>>>>> line: refused" % path); return 3
            if ours_only:
                if not all(pin.match(l) for l in ours + theirs):
                    print("resolve_both_sides: %s: --ours is for pin blocks only and this block holds other lines: refused" % path); return 3
                out += ours
                kept += ours
            else:
                out += ours + ([""] if md and ours and theirs else []) + theirs
                kept += ours + theirs
            blocks += 1
            i = k + 1
            continue
        out.append(lines[i]); i += 1
    if blocks == 0:
        print("resolve_both_sides: %s carries no conflict markers: already resolved, nothing written" % path); return 3
    new = "\n".join(out)
    if new == old:
        print("resolve_both_sides: the new text does not differ: refused"); return 3
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new)
    back = open(path, encoding="utf-8").read().split("\n")
    assert not any(l.startswith(MARK[0]) or l == MARK[1] or l.startswith(MARK[2]) for l in back), "a marker is left"
    pos = 0
    for l in kept:
        pos = back.index(l, pos) + 1
    print("resolve_both_sides: %s: %d block(s) resolved, %d line(s) of %s kept in order%s"
          % (path, blocks, len(kept), "ours (pins)" if ours_only else "both sides", ", one empty line between the sides" if md else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
