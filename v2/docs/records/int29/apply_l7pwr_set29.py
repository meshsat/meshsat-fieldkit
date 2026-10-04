#!/usr/bin/env python3
"""apply_l7pwr_set29.py: Layer 7's page and mock-up specification restated on the figures its own output prints on set 29's tree
(MESHSAT-1357, integration set 29, 4 October 2026; the coordinator's integration correction, finding F-L7-12).

Record l8r2's round 6 (merged in set 29) restated the coolers' feed: the slot's load row is 0.69 A at 5.0 V (the fan's bounded 2.75 W
envelope over 0.80) where round 2 read 0.47 A (2.0 W over 0.85). `l7pwr_fans_th1.py` reads that row from the tree, so its regenerated
output moved four figures and `test_l7pwr` found the page without them. This script writes the output's figures into the page's
current statements, adds a paragraph under the moved-figures table and finding F-L7-12 (the sums mix the fan's rated power with the
bounded envelope's loss; which basis each use takes is the record's next round's to state). Round 2's table stays as history.
No figure is derived here: each new figure is asserted to be printed by `l7pwr_fans_th1.out` in the tree.

Run from the repository root: apply_l7pwr_set29.py [--check | --write]; each old text must occur exactly once; a second run exits 3."""
import re
import sys

PAGE = "v2/docs/records/l7pwr/L7-FANS-AND-TH1.md"
SPEC = "v2/docs/records/l7pwr/T-H1-MOCKUP-SPEC.md"
OUT = "v2/docs/records/l7pwr/l7pwr_fans_th1.out"
PRINTED = ["0.69 A at 5.0 V (2.8 W of fan over 0.80)", "0.70 W lost in it per running fan", "7.50 W", "the step-up's 0.70 W", "+5.55 W",
           "+0.555 W/K", "12.90 W", "0.500"]

PAGE_EDITS = [
    ("**7.15 W** against the model's 1.950 W (+0.520 W/K on E5's line if run flat out;",
     "**7.50 W** against the model's 1.950 W (+0.555 W/K on E5's line if run flat out;"),
    ("| 9WPA0412P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.471 (a step-up from +5V_Sn) |",
     "| 9WPA0412P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.500 (a step-up from +5V_Sn) |"),
    ("| 9WPA0424P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.471 |",
     "| 9WPA0424P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.500 |"),
    ("the slot's load row 0.47 A at 5.0 V (2.0 W of fan over 0.85), so 0.35 W lost per running fan;",
     "the slot's load row 0.69 A at 5.0 V (2.8 W of fan over 0.80, record l8r2's round 6 envelope; 0.47 A in round 2), so 0.70 W lost per running fan;"),
    ("the hold's fans **7.15 W** (slot 3's cooler 2.0 and its step-up's 0.35, the two mixers 4.08 and U22's 0.72 from L4-E11 18a) against "
     "the model's 1.950 W (+5.20 W; E5's line +0.520 W/K at L4-E12's 0.100 W/K per W); the profile's five fans with their converters 11.85 W "
     "against 2.970 W.",
     "the hold's fans **7.50 W** (slot 3's cooler 2.0 and its step-up's 0.70, the two mixers 4.08 and U22's 0.72 from L4-E11 18a) against "
     "the model's 1.950 W (+5.55 W; E5's line +0.555 W/K at L4-E12's 0.100 W/K per W); the profile's five fans with their converters 12.90 W "
     "against 2.970 W (set 29, on record l8r2's round 6 row; the sums' basis is finding F-L7-12)."),
    ("round 2: with the converters' losses 7.15 W in the hold, 11.85 W in the profile;",
     "set 29: with the converters' losses 7.50 W in the hold, 12.90 W in the profile (round 2: 7.15 and 11.85 W, before record l8r2's "
     "round 6 envelope; the sums' basis is F-L7-12);"),
    ("so U22's and the step-ups' losses (0.72 and 0.35 W at full speed) are",
     "so U22's and the step-ups' losses (0.72 and 0.70 W at full speed) are"),
    ("Not claimed: the converters' efficiency is the drafts' ASSUMPTION (0.85),",
     "Not claimed: the converters' efficiency is the drafts' ASSUMPTION (0.85 for U22, 0.80 for the coolers' step-up since record l8r2's round 6),"),
]
AFTER_TABLE_OLD = "| the dock lead's continuous draw against ECSS's 3.4 A | 38 % | **39 %** | the declared 1.3208 A |\n"
AFTER_TABLE_NEW = AFTER_TABLE_OLD + (
    "\n**At set 29 (4 October 2026; the coordinator's integration correction, finding F-L7-12).** Record l8r2's round 6 restated the\n"
    "coolers' feed (the slot's load row 0.69 A at 5.0 V: the fan's bounded 2.75 W envelope over 0.80), and this record's script reads\n"
    "that row from the tree. Four figures of the table above moved again: the hold's fans' heat **7.50 W** (round 2: 7.15), E5's line\n"
    "shift **+0.555 W/K** (+0.520), the profile's five fans' heat **12.90 W** (11.85) and a cooler fan's slot current **0.69 A** (0.47);\n"
    "the step-up's loss per running fan is 0.70 W (0.35). The other rows stand. The two heat sums now mix two bases: the fan's own\n"
    "power stays the maker's rated 2.0 W while the step-up's loss is taken on the bounded envelope, 2.70 W a cooler chain, against\n"
    "2.50 W on the rated basis alone and 3.45 W on the bounded one. Which basis each use takes is this record's next round's to state\n"
    "(F-L7-12).\n")
F11_START = "| F-L7-11 | Layer 6 (records/l6pwr) |"
F12 = ("| F-L7-12 | this record's next round, with L4-E12 (R-150) | set 29: the cooler chain's heat is summed on two bases (the fan at the "
       "maker's rated 2.0 W, the step-up's loss on record l8r2's bounded 2.75 W envelope): 2.70 W a fan, against 2.50 W on the rated basis "
       "and 3.45 W on the bounded one; the hold's 7.50 W and the profile's 12.90 W carry that mix. One basis per use is owed: the plan's "
       "duty on the rated figure, the bound on the envelope |\n")
SPEC_EDITS = [
    ("and 0.35 W at full speed (record l7pwr section 11, round 2):",
     "and 0.70 W at full speed (record l7pwr section 11; 0.35 W before record l8r2's round 6):"),
]


def refuse(msg):
    sys.stderr.write("apply_l7pwr_set29: REFUSED: %s\n" % msg)
    sys.exit(1)


def once(t, old, new, where):
    if t.count(old) != 1:
        refuse("%s: %d occurrence(s) of %r" % (where, t.count(old), old[:70]))
    assert new != old
    return t.replace(old, new)


def main(argv):
    write = "--write" in argv
    page = open(PAGE, encoding="utf-8").read()
    if "F-L7-12" in page:
        sys.stderr.write("apply_l7pwr_set29: already applied\n")
        return 3
    out = " ".join(open(OUT, encoding="utf-8").read().split())
    for f in PRINTED:
        if f not in out:
            refuse("the output does not print %r: regenerate it first" % f)
    for old, new in PAGE_EDITS:
        page = once(page, old, new, PAGE)
    page = once(page, AFTER_TABLE_OLD, AFTER_TABLE_NEW, PAGE)
    rows = [l for l in page.split("\n") if l.startswith(F11_START)]
    if len(rows) != 1:
        refuse("%d F-L7-11 row(s)" % len(rows))
    page = once(page, rows[0] + "\n", rows[0] + "\n" + F12, PAGE)
    spec = open(SPEC, encoding="utf-8").read()
    for old, new in SPEC_EDITS:
        spec = once(spec, old, new, SPEC)
    for t in (page, spec):
        if re.search("[–—]", t):
            refuse("a dash character would be written")
    if write:
        open(PAGE, "w", encoding="utf-8").write(page)
        open(SPEC, "w", encoding="utf-8").write(spec)
    print("apply_l7pwr_set29: %s, %d page edit(s), the set 29 paragraph, finding F-L7-12, %d specification edit(s)"
          % ("WRITTEN" if write else "CHECK OK", len(PAGE_EDITS), len(SPEC_EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
