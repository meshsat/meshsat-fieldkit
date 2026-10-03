#!/usr/bin/env python3
"""apply_gen_sch_a_gnd002.py: DRAFT for board A's generator owner (Layer 8 record l8gnd, MESHSAT-1357, 3 October 2026). NOT
APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

What it draws (rule GND-002, v2/docs/GROUNDING-AND-SHIELDS.md point 4 and its table of four board changes, the two on board A):
  change 1  a CHASSIS net, brought to a single bonding point near the dock: R229, a 0 Ohm 2512 link from CHASSIS to this
            board's GND, the ONE defined impedance between the connector plate and the boards;
  change 4  a pad for the connector-plate strap: H1, a plated M4 pad on CHASSIS (land meshsat:ChassisLug_M4_CHASSIS, drafted
            beside this script under footprints/), where the strap's ring lug lands under an M4 screw, washer and Nyloc.
Both sit in the dock block's section of the schematic, next to J_DOCK. The land's key LUGM4 joins the footprint table, the
node CHASSIS is declared to the intent, and a section lists the two parts.

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: the footprint table's RS2512 entry gains LUGM4 beside it; the
comment line that opens the LTC2954 block gains the chassis-bond block in front of it; the SECTIONS list gains one appended
section in front of the `_listed` line. Every anchor is a line no power draft of L4-E4 to L4-E11 touches (the record's
l8gnd_drafts.out proves the composition in both orders).

Usage:  apply_gen_sch_a_gnd002.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; a designator this draft adds
must not be in use; the result must parse. Exit 0: checked (or written); 3: refused (the target is not the expected text, the
change is already applied, a designator is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_gnd002"
ADDS = ("H1", "R229")          # the designators this draft adds; refused when the target already carries one
NETS = ("CHASSIS",)            # the net this draft adds; refused when the target already carries it

_BLOCK = (
    "# --- GND-002, THE CHASSIS BOND (v2/docs/GROUNDING-AND-SHIELDS.md points 3 and 4 and its table of four board changes; drafted by\n"
    "# Layer 8 record l8gnd, MESHSAT-1357, 3 October 2026). The case is plastic, so the connector plate is the kit's cable-entry\n"
    "# reference and it meets the boards at ONE point, deliberately, here beside the dock. H1 is the plated M4 pad the plate's bonding\n"
    "# strap lands on (net CHASSIS; land meshsat:ChassisLug_M4_CHASSIS: hole 4.3, ring 12.0 both sides, the strap's ring lug under an\n"
    "# M4 screw, washer and Nyloc), and R229 is the defined impedance between CHASSIS and this board's GND: a 0 Ohm 2512 link (the\n"
    "# part lcsc_fill.py gives board B's POE_P link), ONE component, so the bond is a single named point that a pre-compliance\n"
    "# measurement can open or exchange for an RC without a board change. Nothing else on this board may join CHASSIS to GND (point 4:\n"
    "# a second bond would put every cable's common-mode current through the board between the two). Board B's CHASSIS (the RJ45\n"
    "# shell and the Bob Smith capacitor, Microchip DS00004151A p.10) reaches this pad only through the patch lead's shield, the wall\n"
    "# coupler and the plate. The strap, its lugs and the stud are Layer 7's pick (CASE-MARGINS.md item F, the stud an M6 class): the\n"
    "# land accepts an M4 ring lug up to 11 mm across. Placement: beside J_DOCK on the back-wall side, a layout-entry item\n"
    "# (gen_pcb_a3.py). Session decision under the owner's standing rule of 26 September 2026: the link's 0 Ohm (a bond, not a\n"
    "# filter, until a chamber says otherwise) and M4 (the plate's own screw size). Reverse by removing H1 and R229, which leaves the\n"
    "# plate bonded to the boards only through the antenna leads, the state GROUNDING-AND-SHIELDS.md records as the finding.\n"
    "part(\"H1\", \"Mechanical\", \"MountingHole_Pad\", \"M4 bonding pad: the connector plate's strap lands here on a ring lug (GND-002 point 4)\", \"LUGM4\", {\"1\": \"CHASSIS\"})\n"
    "r(\"R229\", \"0R 2512 (CHASSIS bond link)\", \"CHASSIS\", \"GND\", \"RS2512\")   # GND-002 point 4: the one defined impedance between the plate and the boards\n"
    "_intent.node(\"CHASSIS\", 0.0, \"the connector plate's potential as it arrives on H1 over the bonding strap (GND-002): joined to GND by \"\n"
    "             \"R229 alone, so at this board's reference; it carries cable-borne common-mode and discharge current, never a supply or a return\")\n"
)

EDITS = [
    ('"RS2512": "Resistor_SMD:R_2512_6332Metric", "PIN5"',
     '"RS2512": "Resistor_SMD:R_2512_6332Metric", "LUGM4": "meshsat:ChassisLug_M4_CHASSIS", "PIN5"'),
    ("# --- main power control LTC2954-1 (ltc2954.pdf): the panel MAIN button, EN to every converter's enable (RAIL_EN), INT = shutdown request, KILL from the panel controller through Q1\n",
     _BLOCK +
     "# --- main power control LTC2954-1 (ltc2954.pdf): the panel MAIN button, EN to every converter's enable (RAIL_EN), INT = shutdown request, KILL from the panel controller through Q1\n"),
    ("_listed = {r for _, refs in SECTIONS for r in refs}\n",
     "SECTIONS.append((\"CHASSIS BOND (GND-002): THE CONNECTOR PLATE'S STRAP PAD H1 AND ITS 0 OHM LINK R229 TO GND\", [\"H1\", \"R229\"]))   # Layer 8 record l8gnd\n"
     "_listed = {r for _, refs in SECTIONS for r in refs}\n"),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def in_use(text, ref):
    """A designator is in use when a part call names it: part("X", ic("X", r("X", c("X", tp("X", nfet("X" ...)."""
    return re.search(r'\b(?:part|ic|r|c|tp|nfet|vh2|synth|q|esd|efuse)\(\s*"%s"' % re.escape(ref), text) is not None


def patched(text):
    for ref in ADDS:
        if in_use(text, ref):
            refuse("designator %s is already in use in the target" % ref)
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


# NOT RELEASED: record l8gnd drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do,
# on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
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
