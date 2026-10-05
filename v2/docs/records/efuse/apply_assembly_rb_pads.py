#!/usr/bin/env python3
"""apply_assembly_rb_pads.py: DRAFT apply script on v2/docs/ASSEMBLY.md (record efuse, round 2, the independent check V6's minor
m5, MESHSAT-1357, 5 October 2026). UNAPPLIED: the integrator runs it; record efuse runs it only on scratch copies.

The build condition: Ground Control's hardware page for the RockBLOCK 9704 (v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-
hardware-20260927.txt, "Charge Current") prints the supercapacitors' default DC input charge current as about 460 mA, "can be
increased to ~800mA" by bridging two pads, and says the module "will not negotiate a lower current limit". Board B's U24 eFuse
(record efuse, EF-F02, R43 1.21 kOhm) holds the module's printed 500 mA maximum with its band's foot at 0.6681 A: it holds only with
the pads OPEN. Bridged, the module asks about 800 mA, over U24's foot, and over the 16-pin input's printed 500 mA. One sentence in
ASSEMBLY.md's RockBLOCK row says so. No circuit changes.
Usage:  apply_assembly_rb_pads.py [TARGET] [--check | --write]   (default TARGET: the tree's v2/docs/ASSEMBLY.md; default --check)
Exit 0: checked (or written); 3: refused (already applied, the anchor missing or not unique, or the row no longer re-parses)."""
import difflib
import os
import sys

NAME = "apply_assembly_rb_pads"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = os.path.join(REPO, "v2", "docs", "ASSEMBLY.md")
ANCHOR = "the 2x8 IDC lead to `J_RB9704`. The fasteners below B16"
NEW = ("the 2x8 IDC lead to `J_RB9704`. Its charge-current pads stay OPEN (Ground Control's hardware page, Charge Current: about "
       "460 mA by default, about 800 mA bridged; board B's U24 holds the module only with them open, record efuse EF-F02 and its "
       "`apply_assembly_rb_pads.py`). The fasteners below B16")


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def row_cells(text):
    rows = [l for l in text.splitlines() if l.startswith("| RockBLOCK 9704 on B16 |")]
    if len(rows) != 1:
        refuse("the RockBLOCK row is not in the file once")
    return len(rows[0].strip().strip("|").split(" | "))


def patched(text):
    if "charge-current pads stay OPEN" in text:
        refuse("the change is already applied")
    if text.count(ANCHOR) != 1:
        refuse("the anchor occurs %d times, not once" % text.count(ANCHOR))
    before = row_cells(text)
    new = text.replace(ANCHOR, NEW)
    if new == text:
        refuse("the result does not differ")
    if row_cells(new) != before:
        refuse("the RockBLOCK row no longer re-parses to its %d cells" % before)
    if chr(0x2013) in NEW or chr(0x2014) in NEW:
        refuse("a long dash in the new text")
    return new


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) > 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = (args[0] if args else TREE), flags == ["--write"]
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/ASSEMBLY.md", "b/ASSEMBLY.md", n=0))
    if not write:
        print("%s: CHECK OK, 1 edit, nothing written" % NAME)
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or row_cells(back) != row_cells(text):
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN, 1 edit" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
