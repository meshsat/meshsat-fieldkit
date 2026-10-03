#!/usr/bin/env python3
"""apply_blade_plating_l9stk.py: pins the 25 A MINI blade's terminal plating in v2/vendor/SOURCES.yaml, for the integrator and
Layer 6 (record l9stk, the copper question's revision, MESHSAT-1357, 4 October 2026). NOT APPLIED to the tree by this record.

The check of section 14 (COPPER: NOT CONFIRMED) found the limit of the pack path's bands set by the blade: Littelfuse's MINI 297
sheet (v2/vendor/keystone/littelfuse-297-ficcorp.pdf) prints -40 to +125 C for the silver-plated terminals and -40 to +105 C for
the tin-plated ones, while the entry pack-blade-fuse-holder names the element as "0297025", which does not say which. The sheet's
ordering rows give 0297xxx.WXNV, .U, .H and .L for the silver part and 0297xxx.WXT for the tin one. This draft names
0297025.WXNV (the first silver row; .U, .H and .L are the same part in smaller packs) and the tin part it is not.

The entry covers boards A and P; board E's 25 A F3 and its 10 A F1 have no SOURCES entry (finding L9C-F10, Layer 6).

What a run checks: the entry exists once and its fitted_mpn line is the old text exactly once, or the new text (then nothing is
written and the run exits 0); the result re-parses; every entry reads back identical but this one's fitted_mpn.

Usage: apply_blade_plating_l9stk.py [--check | --write] [--sources PATH]
Exit 0: checked, written or already pinned; 3: refused."""
import copy
import os
import sys

import yaml

NAME = "apply_blade_plating_l9stk"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SOURCES = os.path.join(REPO, "v2", "vendor", "SOURCES.yaml")
ENTRY = "pack-blade-fuse-holder"
OLD = '    fitted_mpn: "Keystone 3568 (holder); Littelfuse 0297025 MINI 297 25 A (fuse, fitted at build)"\n'
NEW_MPN = ("Keystone 3568 (holder); Littelfuse 0297025.WXNV MINI 297 25 A, silver-plated terminals, -40 to +125 C (fuse, fitted "
           "at build; the tin-plated 0297025.WXT is -40 to +105 C and is not this part)")
NEW = '    fitted_mpn: "%s"\n' % NEW_MPN


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def entries(text):
    d = yaml.safe_load(text)
    parts = (d or {}).get("parts")
    if not isinstance(parts, list):
        refuse("SOURCES.yaml does not parse to a parts list")
    return d, parts


def patched(text):
    d, parts = entries(text)
    hits = [p for p in parts if isinstance(p, dict) and p.get("id") == ENTRY]
    if len(hits) != 1:
        refuse("SOURCES.yaml carries %d %s entries" % (len(hits), ENTRY))
    if text.count(NEW) == 1 and not text.count(OLD):
        return text, True
    if text.count(OLD) != 1:
        refuse("the old fitted_mpn line occurs %d times" % text.count(OLD))
    new = text.replace(OLD, NEW)
    d2, parts2 = entries(new)
    if {k: v for k, v in d.items() if k != "parts"} != {k: v for k, v in d2.items() if k != "parts"}:
        refuse("a top-level entry moved")
    for a, b in zip(parts, parts2):
        exp = copy.deepcopy(a)
        if isinstance(a, dict) and a.get("id") == ENTRY:
            exp["fitted_mpn"] = NEW_MPN
        if b != exp:
            refuse("entry %s does not read back as written" % (a.get("id") if isinstance(a, dict) else a))
    return new, False


def main(argv):
    path = SOURCES if "--sources" not in argv else argv[argv.index("--sources") + 1]
    flags = [a for a in argv if a in ("--check", "--write")]
    if len(flags) > 1 or any(a not in ("--check", "--write", "--sources", path) for a in argv):
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    text = open(path, encoding="utf-8").read()
    new, done = patched(text)
    if done:
        print("%s: ALREADY PINNED, nothing to write" % NAME)
        return 0
    if flags != ["--write"]:
        print("%s: CHECK OK, 1 edit, nothing written" % NAME)
        return 0
    open(path, "w", encoding="utf-8").write(new)
    if open(path, encoding="utf-8").read() != new:
        refuse("the written file does not read back")
    entries(new)
    print("%s: WRITTEN, 1 edit" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
