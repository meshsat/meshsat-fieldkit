#!/usr/bin/env python3
"""apply_gen_sch_c_pibtn.py: DRAFT for board C's generator owner (Layer 8 record l8r2, item 4, the panel firmware's finding F-01,
MESHSAT-1357, 3 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies.

The defect (F-01, fnd/fw-panel at 42c27369, copied in inputs/): the PI button reaches no controller pin. SW_PI's contacts (PIJ2_A,
PIJ2_B) pass FB3 and FB4 to J_PIJ2's two lands (PIJ2_A2, PIJ2_B2) and U11's clamps only: no RP2040 GPIO, no expander input, neither
line on GND, and no other board carries a mating lead. PANEL.md section 5 ("The PI button: short press = PI_SHDN_REQ (clean shutdown
of every module), hold 8 s = PI_KILL") and HW-FW-CONTRACT FW-C03 have the controller read it, and only the controller can tell a short
press from an 8 s hold; ASSEMBLY.md's leads table agrees ("the panel controller reads it; nothing leaves the backer"). The
generator's own note (PIJ2_A2 as the LTC2954's INT on board A) is the stale statement: no lead carries it there, and if one did, the
press would pull PI_SHDN_REQ, which the controller reads as a MAIN tap (FW-A10), so the 8 s hold could not be told apart.

The correction: the button's sense PIJ2_A2 on U1's P1.3 (pin 16, until now SPARE1 with a test point), the inputs port beside
LIGHT_DAY_n and LIGHT_NIGHT_n; R57 10 k to +3V3 (UNI-ROYAL C25804, the pull-up the board's other switch inputs carry); the button's
return PIJ2_B2 tied to this board's GND (FB4, C27, J_PIJ2 pin 2 and U11's second channel on GND), so a press pulls PIJ2_A2 low through
FB3; C27 (100 nF, now from PIJ2_A2 to GND) with R57 is the debounce, tau 1.0 ms (the board's other inputs: 10 k with 10 nF). The
expander raises EXP_INT on the change (TI SCPS131J 8.4.1), the controller's GPIO24, which it already services. SPARE1's test point
moves to PIJ2_A2, so the button keeps test access. The J_PIJ2 lands are kept (the switch's lead lands, ASSEMBLY.md); U11's clamp
stays on the A line. The expander bit is named PI_BTN_n (low = pressed) for PANEL.md section 4 and the firmware's hal.h (texts for
their owners in the record, section 4).

What it changes in v2/ecad/tools/gen_sch_c.py, and nothing else: U1's value and pin 16; FB4's pin 2, C27, J_PIJ2's pin 2 and its
value, U11's second channel; the generator's note on the leads; the test-point tuple's SPARE1; R57 after J_PIJ2. Composed with Layer
6's apply_gen_sch_c_lcsc.py (fnd/l6r2 at 7633ae0a, copied in inputs/ with its helper l6r2_apply.py), the only other board C draft,
in either order (l8r2_drafts.out).

Usage:  apply_gen_sch_c_pibtn.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_c_pibtn"
GEN = "gen_sch_c.py"
ADDS = ("R57",)
NETS = ()

EDITS = [
    ('"PCA9555PW 0x22: LED sinks, light mode inputs"', '"PCA9555PW 0x22: LED sinks, light mode inputs, the PI button on P1.3 (PI_BTN_n)"'),
    ('"16": "SPARE1", "17": "SPARE2"', '"16": "PIJ2_A2", "17": "SPARE2"'),
    ('part("FB4", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_B", "2": "PIJ2_B2"}, "C1002")',
     'part("FB4", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_B", "2": "GND"}, "C1002")'),
    ('c("C27", "100n", "PIJ2_A2", "PIJ2_B2", "C", "C14663")',
     'c("C27", "100n", "PIJ2_A2", "GND", "C", "C14663")   # with R57 the PI button\'s debounce, tau 1.0 ms (record l8r2, F-01)'),
    ('part("J_PIJ2", "Connector_Generic", "Conn_01x02", "PI button lead: two solder lands on the underside (the controller reads it as the module shutdown request)", "XH2", {"1": "PIJ2_A2", "2": "PIJ2_B2"})\n',
     'part("J_PIJ2", "Connector_Generic", "Conn_01x02", "PI button lead: two solder lands on the underside (the switch\'s lead; U1 P1.3 reads PIJ2_A2, PI_BTN_n)", "XH2", {"1": "PIJ2_A2", "2": "GND"})\n'
     "# F-01 (the panel firmware, fnd/fw-panel at 42c27369), drafted by Layer 8 record l8r2 (MESHSAT-1357, 3 October 2026): THE PI BUTTON\n"
     "# REACHED NO CONTROLLER PIN. PANEL.md section 5 and FW-C03 have the controller tell a short press (PI_SHDN_REQ) from an 8 s hold\n"
     "# (PI_KILL), and only the controller can: PIJ2_A2 is now U1's P1.3 (PI_BTN_n, low = pressed) with R57 10 k to +3V3, the button's\n"
     "# return PIJ2_B2 is this board's GND, and C27 (100 nF to GND) with R57 debounces it (tau 1.0 ms); EXP_INT tells the controller.\n"
     'r("R57", "10k", "PIJ2_A2", "+3V3", "R", "C25804")   # the PI button\'s pull-up (F-01)\n'),
    ('esd("U11", "PIJ2_A2", "PIJ2_B2", "+3V3")', 'esd("U11", "PIJ2_A2", "GND", "+3V3")'),
    ("# rides at about 1.6 V and is shorted to its return when the button is pressed; PIJ2_A2 is the same part's\n"
     "# open-drain INT output, held at +3V3 by R3 on board A. The B line of each pair is the lead's own return and\n"
     "# is GND at the far end, so its diode to this board's ground is what gives the discharge somewhere to go that\n"
     "# is not the lead.",
     "# rides at about 1.6 V and is shorted to its return when the button is pressed. PIJ2_A2 is the PI button's\n"
     "# sense on U1 P1.3, held at +3V3 by R57 on this board (record l8r2, F-01; it was described as the LTC2954's INT\n"
     "# on board A, a lead no board carries). MAINSW_B2 is the MAIN lead's own return, GND at the far end, and the PI\n"
     "# button's return is this board's GND, so each clamp's diode to ground gives the discharge somewhere to go that\n"
     "# is not the lead."),
    ('"ZEROIZE_HW", "SPARE1", "SPARE2"', '"ZEROIZE_HW", "PIJ2_A2", "SPARE2"'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def in_use(text, ref):
    return re.search(r'(?:part|ic|r|c|tp|nfet|vh2|synth|q|esd|efuse)\(\s*"%s"' % re.escape(ref), text) is not None


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


# NOT RELEASED: record l8r2 drafts this change for the board's generator owner and never applies it. Writing the repository's own
# generator is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check of
# this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", GEN)
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8r2's drafts wait on an accepted check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/" + GEN, "b/" + GEN, n=0))
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
