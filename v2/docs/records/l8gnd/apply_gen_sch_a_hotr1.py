#!/usr/bin/env python3
"""apply_gen_sch_a_hotr1.py: DRAFT for board A's generator owner (Layer 8 record l8gnd, MESHSAT-1357, 3 October 2026). NOT
APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

What it draws: THE SLOT_EN HOLD, the hardware that keeps SLOT_EN1..3 at their last driven level across a reset of the panel
controller (ARCHITECTURE.md 4.3, adjudication A01 and finding W5-F4: "SLOT_EN powers up OFF and holds its state across a panel
reset"; HW-FW-CONTRACT.md FW-C02: "the hold (ARCHITECTURE.md 4.3) OWED"; IF-BC-PANEL slot_power_semantics: "in no generator";
LAYER-STATUS.md rows 4.5 and 5.6). HOT-R1's own line (S-57, SC-70) is drawn since 27 September 2026 and is not touched: this
draft keeps the hold consistent with the hot stop (CONOPS 4c, FW-C13, FW-C14): the panel still drops the slots by driving the
lines low in H1, the ZEROIZE alarm cut still acts, and H2's PI_KILL removes board A's +3V3 and with it the hold, so a kit that
restarts after H2 has every slot OFF and the panel reads HOT-R1 before raising one.

The circuit: U43, an SN74LVC08APWR (the part board A fits as U26), one AND gate per line with both inputs on the line and its
output back onto the line through 4.7 k (R230, R231, R232): a KEEPER. Its decoupling C240 is declared (decision 42 class D).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: the line that draws R34 (slot 2's pull-down) gains the hold
block after it; the SECTIONS list gains one appended section in front of the `_listed` line. Both anchors are lines no power
draft of L4-E4 to L4-E11 touches; the GND-002 draft of this record anchors the same `_listed` line and the two apply in either
order (the record's l8gnd_drafts.out proves the composition).

Usage:  apply_gen_sch_a_hotr1.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; a designator this draft adds
must not be in use; the result must parse. Exit 0: checked (or written); 3: refused (the target is not the expected text, the
change is already applied, a designator is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_hotr1"
ADDS = ("U43", "R230", "R231", "R232", "C240")   # the designators this draft adds; refused when the target already carries one
NETS = ("SLOT_EN1_K", "SLOT_EN2_K", "SLOT_EN3_K")   # the nets this draft adds (each gate's output before its resistor)

_BLOCK = (
    "# --- THE SLOT_EN HOLD (ARCHITECTURE.md 4.3 adjudication A01 and W5-F4; HW-FW-CONTRACT.md FW-C02 'the hold ... OWED'; IF-BC-PANEL\n"
    "# slot_power_semantics 'in no generator'; drafted by Layer 8 record l8gnd, MESHSAT-1357, 3 October 2026). SLOT_EN1..3 are driven by\n"
    "# the panel controller (board C U3, GPIO13 to 15) over two ribbons and land here on U4, U5 and U6's enables, with R30, R34 and R38\n"
    "# holding an absent line off. The RP2040's pads leave every reset as inputs with the pull-down on (PADS_BANK0 GPIOx: PDE reset 0x1,\n"
    "# PUE 0x0; RP2040 datasheet 2.19.6.3), so a RUN reset, a brownout of the panel's 3.3 V, an SWD reset or the bootloader drops every\n"
    "# running slot (W5-F4); FW-C02's watchdog scope covers the watchdog alone. U43 is a KEEPER on each line: an AND gate with both\n"
    "# inputs on the line and its output back onto the line through 4.7 k (R230 to R232). While the panel DRIVES a line the gate\n"
    "# follows it: the panel sources or sinks at most 3.3 V / 4.7 k = 0.70 mA against the gate's output, inside the pad's 4 mA default\n"
    "# drive (VOH at least 2.62 V, VOL at most 0.5 V at IOVDD 3.3 V and 2, 4, 8 or 12 mA; RP2040 Table 625). When the pad falls back\n"
    "# to its reset state, an input with 50 to 80 k to ground (RPD, Table 625), the gate holds the line where it was. HIGH: the gate's\n"
    "# VOH is VCC - 0.2 V at IOH -100 uA (SN74LVC08A, TI SCAS283W), 3.0 V with +3V3 at 3.2 V; over R230 into the pad's 50 k in\n"
    "# parallel with R30's 100 k the line sits at 3.0 x 33.3 / 38.0 = 2.63 V; the enable pins SOURCE current (AP64500: an internal\n"
    "# 1.5 uA pull-up source, IEN 1 to 2 uA at 1 V and 5.5 uA typical at 1.5 V, DS41979 Rev 5-2; LM5176: 1 to 3 uA at standby and\n"
    "# 2.15 to 4.25 uA of hysteresis current, SNVSAI1D), bounded at 20 uA either way (INFERRED) and taken as a sink for the high, so\n"
    "# at least 2.55 V against the 2.0 V VIH of the gate (2.7 to 3.6 V) and of the RP2040 at 3.3 V, and against the enables'\n"
    "# thresholds (AP64500 VEN_H at most 1.25 V; LM5176 VEN(OP) at most 1.29 V). LOW: VOL 0.2 V at 100 uA over the same divider (the\n"
    "# pad at 80 k the worse) plus the 20 uA sourced through 4.25 k, at most 0.27 V on the line, against VIL 0.8 V, AP64500 VEN_L at\n"
    "# least 1.03 V and LM5176 VEN(STBY) at least 0.55 V. It powers up LOW: R30, R34, R38 and the panel's pad hold each line at 0 V\n"
    "# while +3V3 rises, and an AND gate with both inputs low outputs low at every supply where its transistors conduct (the function;\n"
    "# the sheet prints nothing under 1.65 V, so INFERRED; V-C01's scope row covers every enable from the MAIN press). THE PANEL'S\n"
    "# DRIVE ALWAYS WINS: a gate output stuck at either rail is overridden through 4.7 k, so no failure of U43 can raise a slot the\n"
    "# panel holds low or hold one it drives low. The hold is the LAST DRIVEN LEVEL of each line, kept while +3V3 is up: a panel\n"
    "# reset no longer drops the running slots (A01); the hot stop's H1 and the ZEROIZE cut act as before (the panel drives low and\n"
    "# the keeper follows); H2's PI_KILL drops RAIL_EN and +3V3 and the hold with them, so the kit restarts with every slot OFF and\n"
    "# the panel reads HOT-R1 before raising one (FW-C14). Firmware (FW-C02, text in the record): at boot read GPIO13 to 15 as inputs\n"
    "# and take over the drive at the level read, then FW-C01's order for any slot read low; a wipe pending or ZEROIZE_SW closed at\n"
    "# boot drives all three low first (D-03). Contracts (IF-BC-PANEL, IF-AB-RIBBON cable_out_states, text in the record): with a\n"
    "# ribbon out the slots keep their last level instead of dropping (ribbons are mated with the kit off, SC-61); MAIN still stops the\n"
    "# kit through U1. Session decision under the owner's standing rule of 26 September 2026 (A01 took the hold; its form, a keeper\n"
    "# on this board, is the session's: no control line is free on J_AB1 for a latch enable, and this board's +3V3 is the supply that\n"
    "# falls with PI_KILL). Reverse by removing U43, R230 to R232 and C240, which returns the lines to R30, R34 and R38 alone.\n"
    "ic(\"U43\", 14, \"SN74LVC08APWR quad AND: the SLOT_EN keepers (gates 1 to 3, both inputs on the line, output back through 4.7 k; gate 4 unused)\", \"TSSOP14\", {\n"
    " \"1\": \"SLOT_EN1\", \"2\": \"SLOT_EN1\", \"3\": \"SLOT_EN1_K\", \"4\": \"SLOT_EN2\", \"5\": \"SLOT_EN2\", \"6\": \"SLOT_EN2_K\", \"7\": \"GND\", \"8\": \"SLOT_EN3_K\", \"9\": \"SLOT_EN3\", \"10\": \"SLOT_EN3\", \"11\": \"NC\", \"12\": \"GND\", \"13\": \"GND\", \"14\": \"+3V3\"}, \"C465737\")\n"
    "r(\"R230\", \"4.7k\", \"SLOT_EN1_K\", \"SLOT_EN1\"); r(\"R231\", \"4.7k\", \"SLOT_EN2_K\", \"SLOT_EN2\"); r(\"R232\", \"4.7k\", \"SLOT_EN3_K\", \"SLOT_EN3\")   # the keepers' feedback: the panel's drive wins through them\n"
    "c(\"C240\", \"100n\", \"+3V3\", \"GND\", lcsc=\"C14663\"); _intent.bypass(\"C240\", \"U43\", \"14\", \"+3V3\")\n"
    "_cls(\"C240\", \"D\", \"TI SCAS283W (SN74LVC08A): the maker's sheet ties no value or distance to VCC; class D by role (a supply pin's own decoupling), the generator's own 100 nF (decision 42 D1)\")\n"
)

EDITS = [
    ('r("R34", "100k", "SLOT_EN2", "GND")   # a slot with no controller line stays off (as the AP64500 stage had it)\n',
     'r("R34", "100k", "SLOT_EN2", "GND")   # a slot with no controller line stays off (as the AP64500 stage had it)\n' + _BLOCK),
    ("_listed = {r for _, refs in SECTIONS for r in refs}\n",
     "SECTIONS.append((\"SLOT_EN HOLD: SN74LVC08A KEEPERS ON THE THREE SLOT ENABLES (A01, W5-F4)\", [\"U43\", \"R230\", \"R231\", \"R232\", \"C240\"]))   # Layer 8 record l8gnd\n"
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
