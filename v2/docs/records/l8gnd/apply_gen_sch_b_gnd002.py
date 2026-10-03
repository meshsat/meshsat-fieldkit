#!/usr/bin/env python3
"""apply_gen_sch_b_gnd002.py: DRAFT for board B's generator owner (Layer 8 record l8gnd, MESHSAT-1357, 3 October 2026). NOT
APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

What it draws (rule GND-002, v2/docs/GROUNDING-AND-SHIELDS.md point 4 and its table of four board changes, the two on board B):
  change 2  the 1 nF 2 kV common-node capacitor C33 moved from GND to CHASSIS: Microchip's checklist for this switch (DS00004151A
            p.10, voltage-mode drivers) terminates the line-side centre taps through 75 Ohm to a common node "then connected to
            chassis ground through a 1000 pF, 2 kV capacitor"; as generated the capacitor returns to signal ground;
  change 3  the RJ45 shell J_ETH SH moved from GND to CHASSIS: the same page, "The metal case shield of the RJ45 connector is also
            tied to chassis ground", and the shell is the patch lead's shield, a cable shield by definition (point 5).
No part is added. Board B's CHASSIS has no DC bond to GND on this board: it reaches the kit's single bond (board A's R229 at the
plate's strap pad) only through the patch lead's shield, the wall coupler and the connector plate, which is what GND-002 point 4
asks (one point, on board A). The node CHASSIS is declared to the intent.

What it changes in v2/ecad/tools/gen_sch_b.py, and nothing else: the magnetics comment line gains the GND-002 block after it;
C33's call returns to CHASSIS; J_ETH's SH pin reads CHASSIS and the node declaration follows the part. No other draft targets
board B (L4-E4 to L4-E13 draft boards A and E only), so there is no composition order to keep.

Usage:  apply_gen_sch_b_gnd002.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_gnd002"
NETS = ("CHASSIS",)            # the net this draft adds; refused when the target already carries it

_BLOCK = (
    "# GND-002, THE CABLE-SHIELD SIDE OF THE CHASSIS BOND (v2/docs/GROUNDING-AND-SHIELDS.md points 3 to 5 and its table of four board\n"
    "# changes; drafted by Layer 8 record l8gnd, MESHSAT-1357, 3 October 2026). Microchip's hardware design checklist for this switch\n"
    "# (KSZ989x/KSZ956x/KSZ9477, DS00004151A p.10, the voltage-mode driver points) terminates every line-side centre tap through 75 Ohm\n"
    "# to a common node, 'The common node is then connected to chassis ground through a 1000 pF, 2 kV capacitor', and 'The metal case\n"
    "# shield of the RJ45 connector is also tied to chassis ground'. Until this draft both returned to SIGNAL ground, and no board had a\n"
    "# chassis net at all (the grounding census of 21 September 2026). The net CHASSIS here is the cable-shield reference: C33's cold\n"
    "# end and J_ETH's shield tabs (Amphenol RJHSE-5380, 'Shield: Stainless Steel with tin dipped tails'). It has NO bond to GND on this\n"
    "# board, by design: the kit's one chassis-to-board bond is board A's R229 at the plate's strap pad (point 4), and this board's\n"
    "# CHASSIS reaches the plate over the patch lead's shield and the sealed wall coupler, whose shield continuity to the plate is the\n"
    "# wall RJ45 pick's obligation (Layer 7: the Bulgin PX0833 as held has a plastic body and needs its PX0888 backshell for that).\n"
    "# A cable's common-mode current therefore leaves on the shield to the plate and never through this board's ground (point 5).\n"
    "# Session decision under the owner's standing rule of 26 September 2026 (the clause's own arrangement, no option open). Reverse\n"
    "# by returning C33 and the SH pin to GND, which is the state the census recorded as the one mismatch with the clause.\n"
)

EDITS = [
    ("# magnetics: chip side centre taps to ground through separate 100 nF (voltage-mode PHY, KSZ9897 section 7); MDI side to the RJ45, PoE on the pair 1-2 and 3-6 centre taps\n",
     "# magnetics: chip side centre taps to ground through separate 100 nF (voltage-mode PHY, KSZ9897 section 7); MDI side to the RJ45, PoE on the pair 1-2 and 3-6 centre taps\n"
     + _BLOCK),
    ('c("C33", "1n 2kV", "BOB", "GND", "C1812")',
     'c("C33", "1n 2kV", "BOB", "CHASSIS", "C1812")   # GND-002 change 2: the common node\'s 2 kV capacitor returns to CHASSIS (DS00004151A p.10)'),
    ('"7": "MDI_D_P", "8": "MDI_D_N", "SH": "GND"})\n',
     '"7": "MDI_D_P", "8": "MDI_D_N", "SH": "CHASSIS"})   # GND-002 change 3: the shield tabs are the patch lead\'s shield, on CHASSIS with C33\n'
     '_intent.node("CHASSIS", 0.0, "the cable-shield reference on this board (GND-002): the RJ45 shell J_ETH SH and the Bob Smith capacitor C33 "\n'
     '             "sit on it, and it is joined to the kit\'s ground ONLY on board A (R229 at the plate\'s strap pad); no part on this board joins "\n'
     '             "it to GND, so a cable\'s common-mode current leaves on the patch lead\'s shield to the wall coupler and the plate")\n'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), text):
            refuse("net %s already exists in the target" % net)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8gnd drafts this change for board B's generator owner and never applies it. Writing the repository's own
# gen_sch_b.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do,
# on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_b.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8gnd's drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_b.py", "b/gen_sch_b.py", n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
