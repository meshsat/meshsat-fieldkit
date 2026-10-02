#!/usr/bin/env python3
"""apply_gen_sch_a_u17.py: DRAFT for board A's generator owner (task L4-E9 round 2, MESHSAT-1357, 2 October 2026). NOT
APPLIED to the tree by L4-E9; it was run only on scratch copies (the tests write scratch copies).

Why (finding HF-F02, open item S-60). U17, the INA226 that monitors the PoE stage, has IN+ on POE_OUT and IN- on +54V_POE:
54 V against the INA226's 40 V absolute maximum on IN+ and IN- (TI SBOS547C 5.1, read at the copy byte-identical to ti.com
on 2 October 2026), so in normal operation the monitor is outside its rating and a damaged part can hold the kit bus.

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else (five edits on disjoint lines):
  1. a rail POE_VIN, declared ahead of +54V_POE: the PoE stage's input behind a new sense resistor, at the pack's 14.4 V
     nominal and 16.8 V work voltage, 1.28 A typical (0.3 A at 54 V over 0.88 from 14.4 V) and 3.68 A peak (0.6 A at 54 V
     over 0.88 from the 10.0 V stack), written as those expressions;
  2. +54V_POE fed from POE_VIN rather than VBAT;
  3. R227, 5 mOhm 1 % 2512 (Milliohm HoJLR2512-3W-5mR-1%, LCSC C2903482, the part L4-E4 chose for R138), from VBAT to
     POE_VIN, ahead of the stage's call;
  4. the PoE stage U16 takes POE_VIN as its input and its BIAS (the helper refuses a BIAS rail other than the input
     without a blocking diode);
  5. U17's IN+ (pin 10) on VBAT, IN- (pin 9) and VBUS (pin 8) on POE_VIN; its address pins unchanged (0x47); and R227 in the
     PoE sheet section.
R71 stays the LM5176's own ISNS shunt on the 54 V side, so U16's average limit does not move. The monitor's pins then sit at
VBAT, at most 20.135 V (the charger's SYSOVP maximum 20.0 V; the pack-open bound 20.135 V) and 29.2 V at the VBAT clamp D1's rated pulse, against 36 V of common
mode and VBUS range and 40 V absolute; the stage's input at its fault bound, U16's boost peak limit over R72 10 mOhm, drops
at most 72.38 mV across R227 at its +1 % (14.33 A), inside the 81.92 mV full scale (l4e9_power_path.out section 11).

Order (DOWNSTREAM-REGISTER.md): step 3e, after L4-E6's R12 and C147, L4-E4's R11, L4-E8's ballasts and Cc2 and L4-E4's R138;
its lines are disjoint from all of them, so it applies in any order (test_l4e9 composes it with each).

Usage:  apply_gen_sch_a_u17.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; R227 must be unused; the
result must parse. Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already
applied, a designator is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_u17"
NEW_REF = "R227"
POE_VIN = ('_intent.rail("POE_VIN", 14.4, round(0.3 * 54.0 / 0.88 / 14.4, 2), round(0.6 * 54.0 / 0.88 / 10.0, 2), "R227", '
           'loads={"Q17": round(0.3 * 54.0 / 0.88 / 14.4, 2)}, v_work=16.8, budget=0.02, converted=False, fed_from="VBAT",\n'
           '             note="L4-E9 (MESHSAT-1357, HF-F02): the PoE stage\'s input behind R227, the 5 mOhm sense resistor U17 reads; '
           '0.3 A typical and 0.6 A peak at 54 V over 0.88, from 14.4 V and from the 10.0 V stack (v2/docs/records/l4e9/)")\n')
EDITS = [
    ('_intent.rail("+54V_POE", 54.0, 0.3, 0.6, "R71", loads={"J_54V": 0.3}, budget=0.02, share=0.005, switch="U16", efficiency=0.88, fed_from="VBAT",',
     POE_VIN +
     '_intent.rail("+54V_POE", 54.0, 0.3, 0.6, "R71", loads={"J_54V": 0.3}, budget=0.02, share=0.005, switch="U16", efficiency=0.88, fed_from="POE_VIN",'),
    ('lm5176("POE", "U16", "VBAT", "+54V_POE",',
     '# L4-E9 (MESHSAT-1357, HF-F02): U17 reads the PoE stage on its 14.4 V input through R227, not on the 54 V rail it was\n'
     '# rated 40 V against (TI SBOS547C 5.1); R71 stays U16\'s ISNS shunt. v2/docs/records/l4e9/L4E9-ENTRY-PROPOSALS.md, U17.\n'
     'r("R227", "5mOhm 1% 2512 (PoE input sense, U17)", "VBAT", "POE_VIN", "RS2512", lcsc="C2903482")\n'
     'lm5176("POE", "U16", "POE_VIN", "+54V_POE",'),
    ('isns="20m", rcs="10m", bias="VBAT",',
     'isns="20m", rcs="10m", bias="POE_VIN",'),
    ('ic("U17", 10, "INA226 PoE rail monitor (0x47)", "VSSOP10", {"1": "+3V3", "2": "SCL", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "NC", "9": "+54V_POE", "10": "POE_OUT"}, "C49851")   # VBUS pin open: 54 V exceeds its 36 V range',
     'ic("U17", 10, "INA226 PoE stage input monitor (0x47)", "VSSOP10", {"1": "+3V3", "2": "SCL", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "POE_VIN", "9": "POE_VIN", "10": "VBAT"}, "C49851")   # L4-E9 (HF-F02): IN+ on VBAT, IN- and VBUS on POE_VIN behind R227, at most 20.0 V against 36 V'),
    ('("POE RAIL: LM5176 BOOST 54 V 0.6 A, INA226 0x47", ["U16",',
     '("POE RAIL: LM5176 BOOST 54 V 0.6 A, INA226 0x47 ON ITS INPUT", ["U16", "R227",'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if re.search(r'"%s"' % NEW_REF, text):
        refuse("%s is already used in the target" % NEW_REF)
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
    if new.find('_intent.rail("POE_VIN"') > new.find('_intent.rail("+54V_POE"'):
        refuse("POE_VIN is not declared ahead of the rail it feeds")
    return new


# NOT RELEASED: task L4-E9 drafts this change for board A's generator owner and never applies it. Writing the repository's
# own gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E9 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E9's change waits on an accepted check")
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
