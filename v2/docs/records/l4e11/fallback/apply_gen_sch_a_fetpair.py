#!/usr/bin/env python3
"""apply_gen_sch_a_fetpair.py: DRAFT for board A's generator owner, the FALLBACK (ii) of L4-E11 round 11 (record l4e11 round FET,
task L4A-70, MESHSAT-1357, 7 October 2026). NOT APPLIED to the tree; its author ran it only on scratch copies (the tests write scratch
copies). It is prepared now so that a negative E-05 needs no new engineering; it is applied ONLY on that trigger.

Why (L4E11-ROUND-FET.md, l4e11_fet.out): the drawn three BUK6Y10-30P (Q39, Q40, Q42) on one BATDRV node are 7.08 nF typical at -15 V and
about 8.61 nF near 0 V against TI's "less than 5 nF" (SLUSE65A p.92), with no Ciss maximum printed; E11-37 stays OPEN on E-05 (TI's
answer to Q-TI-17 stated as a limit, or the bench of block E11-37). The round's search found no set of 16 parts whose gate load is under
5 nF on PRINTED maxima and whose E-1 bar meets 40.78 K/W, so (i)(a) stays selected, CONDITIONAL on E-05. On a NEGATIVE E-05 (TI refuses
three on one BATDRV, or the bench fails supplement entry, the 30 mV ideal-diode regulation or LDO mode with the three) this draft takes
the design to round 11's fallback (ii): the pair Q39 and Q40, Q42 removed.

THE FALLBACK STAYS CONDITIONAL (it is never written as a pass): the pair is under 5 nF only on the maker's TYPICAL at -15 V (4.72 nF;
about 5.74 nF near 0 V, over it; no maximum printed), so it rests on Q-TI-17 (e); and its E-1 bar is the pair's (Zself + Zmut) at most
20.39 K/W with R17 placed apart (record l9stk 15.5), half the three's 40.78 K/W, shown achievable by no printed figure: E11-29's coupon
decides it on the pair, and TP-E11-29's design target with its fixture allowance is restated at that bar before layout (not done here).
A result with the three does not transfer to the pair (E11-37's block).

What it changes in v2/ecad/tools/gen_sch_a.py AFTER apply_gen_sch_a_charger.py (which it requires), and nothing else:
  Q42     removed (the charger draft's third BUK6Y10-30PX): the loop draws Q39 and Q40, "one of two in parallel".
  comment the battery FETs' block restated for the pair: TI's rule against the pair's TYPICAL Ciss, the pair's bar 20.39 K/W, the
          layout (Q39 and Q40 side by side, record l8p's PTC or guard at the two drain tabs' centroid), no figure of the three left.
  intent  CH_BATQ's loads Q39 and Q40 at 5.0 A each (the 10 A typical split over two), its comment and note; VBAT's always_on_why.
  names   the charger's section comment, U3's value text and the sheet group drop Q42.
The pin maps of Q39 and Q40, R17, R149, C236, U42, U46 and every other part of the charger draft are unchanged; no designator is added.

ORDER: after apply_gen_sch_a_charger.py, in either order with every later board A draft of L4-E9's list (none of them names Q42:
record l8p's PTC and thermal guard, this record's DD-7 and the rest were read on the composed generator). check_dd7_netlist.py's
BODY group names Q42 among BATFETS: on adopting this draft its tuple becomes ("Q39", "Q40") (apply_check_dd7_fetpair.py beside this
script; the tests read DD-7 on the pair by setting the tuple in memory).

WHERE IT SITS: records/l4e11/fallback/, outside L4-E9's change list on purpose (l4e9_power_path.py reads every records/l4e*/apply_*.py
as a pending baseline draft and refuses one its list does not name; a fallback is not the baseline, as l4e7's p0sol_b2 is not). On a
negative E-05 its owner adds the row to L4-E9's list and applies it after the charger draft.

Usage:  apply_gen_sch_a_fetpair.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse and must not
name Q42. Exit 0: checked (or written); 3: refused (the charger draft is not applied, the change is already applied, the target is
not the expected text, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_fetpair"
CHARGER_MARK = 'for _qb in ("Q39", "Q40", "Q42"): nfet(_qb, '
_OLD_BLOCK = (
    "# with Ciss under 5 nF (9.2.2, p.92). Three Nexperia BUK6Y10-30P (17 April 2020): 30 V, VGS +-20 V, 175 C, RDSon at most 10\n"
    "# mOhm at -10 V and 25 C, 16 at 175 C, 25 at -4.5 V; Ciss 2.36 nF typical each (7.08 for the three at -15 V, about 8.61 near 0 V:\n"
    "# over TI's 5 nF, OPEN on E11-37 with Q-TI-17 (a) to (f)); ISM 320 A each for 10 us at Tmb 25 C. No printed maximum covers BATDRV's\n"
    "# 8.5 V hot: each is SIZED to an RDS(on) allowance of 21.1 mOhm at 8.5 V and 150 C, which E11-36 confirms or reverses. E11-29 is\n"
    "# the junction limit of record l9stk 15.5 (round 9): the hottest junction at most 150 C held at 23.93 A from 76.25 C with the band\n"
    "# (9.16 K) and R17 (2.86 W) in place, for ANY split of the RDS(on) spread under the allowance (round 11: one FET at half the\n"
    "# others' RDS(on) takes half the current, 9/8 of the even split's loss), so the three's installed (Zself + 2 Zmut) at most\n"
    "# 40.78 K/W with R17 placed apart (record l9stk's even-split 45.88 K/W times 8/9; with Zself and Zmut read apart, 45.88 x\n"
    "# 8 (1 - m)(1 + 2 m) / 9 for m = Zmut / Zself under 1/4) (the pair's fallback 20.39 K/W, the even split its worst; the\n"
    "# pair's former 33.12 K/W target at +70 C air is withdrawn). LAYOUT (Layer 9, board A's PCB generator): Q39, Q40 and Q42\n"
    "# side by side on one CH_BATQ drain pour and one VBAT source pour, the gates from one CH_BATDRV\n"
    "# node by equal branches; R17 off that pour (its coupling into each junction at most 1 K/W, read by heating R17 alone); record\n"
    "# l8p's enable-loop PTC at the three drain tabs' centroid, within 3 mm of each tab's edge; the two pours' largest paths, each from\n"
    "# its current's joint to the FET lands, summed at most 0.1 mOhm at the operating temperature, each junction's worst-split figure\n"
    "# at most 37.59 K/W and R17's coupling at most 0.294 K/W (round 16: the design target with the test fixture's 10 mW lead\n"
    "# allowance, so the limit's lines pass with their uncertainty; the acceptance bars unchanged). The docking pulse is taken whole in\n"
    "# ONE body diode, no sharing credited, and its whole hot waveform is E11-30's (L4-E11 sections 16, 17, 19 and 21).\n")
_NEW_BLOCK = (
    "# with Ciss under 5 nF (9.2.2, p.92). FALLBACK (ii) of L4-E11 round 11, drawn by record l4e11 round FET's apply_gen_sch_a_fetpair.py\n"
    "# on a NEGATIVE answer to Q-TI-17 (E-05) only: TWO Nexperia BUK6Y10-30P (17 April 2020): 30 V, VGS +-20 V, 175 C, RDSon at most 10\n"
    "# mOhm at -10 V and 25 C, 16 at 175 C, 25 at -4.5 V; Ciss 2.36 nF typical each, no maximum printed (4.72 nF typical for the pair at\n"
    "# -15 V, about 5.74 near 0 V): under TI's 5 nF only on the maker's typical at -15 V, so the pair stays CONDITIONAL on Q-TI-17 (e);\n"
    "# ISM 320 A each for 10 us at Tmb 25 C. No printed maximum covers BATDRV's 8.5 V hot: each is SIZED to an RDS(on) allowance of\n"
    "# 21.1 mOhm at 8.5 V and 150 C, which E11-36 confirms or reverses. E11-29 is the junction limit of record l9stk 15.5: the hottest\n"
    "# junction at most 150 C held at 23.93 A from 76.25 C with the band (9.16 K) and R17 (2.86 W) in place, for ANY split of the RDS(on)\n"
    "# spread under the allowance; for two FETs the even split is the worst split at any coupling (round 11, 21b (ii)), so the pair's\n"
    "# installed (Zself + Zmut) at most 20.39 K/W with R17 placed apart (record l9stk 15.5), half the three's 40.78 K/W; no printed figure\n"
    "# shows it achievable: E11-29's coupon decides it on the pair, and TP-E11-29's design target with its fixture allowance is restated\n"
    "# at this bar before layout. LAYOUT (Layer 9, board A's PCB generator): Q39 and Q40 side by side on one CH_BATQ drain pour and one\n"
    "# VBAT source pour, the gates from one CH_BATDRV node by equal branches; R17 off that pour (its coupling into each junction at most\n"
    "# 1 K/W, read by heating R17 alone); record l8p's enable-loop PTC, or its thermal guard, at the two drain tabs' centroid, within 3 mm\n"
    "# of each tab's edge; the two pours' largest paths, each from its current's joint to the FET lands, summed at most 0.1 mOhm at the\n"
    "# operating temperature. The docking pulse is taken whole in ONE body diode, no sharing credited, and its whole hot waveform is\n"
    "# E11-30's (L4-E11 sections 16, 17, 19 and 21; record l4e11 round FET).\n")
EDITS = [
    ("the battery FETs Q39, Q40 and Q42 and RSR between it and the pack, SLUSE65A Figure 9-1",
     "the battery FETs Q39 and Q40 (the pair, L4-E11 round 11's fallback) and RSR between it and the pack, SLUSE65A Figure 9-1"),
    ('"BQ25730RSNR 1 to 5 cell NVDC buck-boost charger (battery FETs Q39, Q40 and Q42), 4S from the 20 V bus, I2C 0x6B"',
     '"BQ25730RSNR 1 to 5 cell NVDC buck-boost charger (battery FETs Q39 and Q40), 4S from the 20 V bus, I2C 0x6B"'),
    (_OLD_BLOCK, _NEW_BLOCK),
    ('for _qb in ("Q39", "Q40", "Q42"): nfet(_qb, "BUK6Y10-30PX 30 V P-FET (the BQ25730\'s battery FET, one of three in parallel: S on VSYS, D toward RSR)"',
     'for _qb in ("Q39", "Q40"): nfet(_qb, "BUK6Y10-30PX 30 V P-FET (the BQ25730\'s battery FET, one of two in parallel: S on VSYS, D toward RSR)"'),
    ("# L4-E11 (the U-04 question for the consolidation; round 9): CH_BATQ, the copper between the BQ25730's battery FETs Q39, Q40 and\n"
     "# Q42 and the RSR shunt R17.",
     "# L4-E11 (the U-04 question for the consolidation; round 9; round FET's fallback): CH_BATQ, the copper between the BQ25730's battery\n"
     "# FETs Q39 and Q40 and the RSR shunt R17."),
    ('loads={"Q39": 3.34, "Q40": 3.33, "Q42": 3.33},', 'loads={"Q39": 5.0, "Q40": 5.0},'),
    ('note="L4-E11: the node between the battery FETs Q39, Q40 and Q42 (drains) and the RSR shunt R17',
     'note="L4-E11: the node between the battery FETs Q39 and Q40 (drains) and the RSR shunt R17'),
    ("the RSR shunt R17 and the battery FETs Q39, Q40 and Q42 (on with the battery alone",
     "the RSR shunt R17 and the battery FETs Q39 and Q40 (on with the battery alone"),
    ('"CHARGER BQ25730: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), BATTERY FETS Q39, Q40 AND Q42 AND RSR TO THE PACK',
     '"CHARGER BQ25730: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), BATTERY FETS Q39 AND Q40 AND RSR TO THE PACK'),
    ('"R17", "Q39", "Q40", "Q42", "C236",', '"R17", "Q39", "Q40", "C236",'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if CHARGER_MARK not in text:
        if 'for _qb in ("Q39", "Q40"): nfet(_qb, ' in text:
            refuse("already applied (the pair is drawn)")
        refuse("the charger draft is not applied: apply apply_gen_sch_a_charger.py first")
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
    if "Q42" in new:
        refuse("the result still names Q42")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: as apply_gen_sch_a_charger.py, writing the repository's own gen_sch_a.py is refused until RELEASE.md beside this script
# reads "released: yes" on its first line and names an accepted check ("check: <repository path whose first line is 'accepted: yes'>").
# The trigger is a negative E-05 on top of that release; a copy elsewhere may be written (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))     # this script sits in records/l4e11/fallback/
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; the fallback waits on a negative E-05 and an accepted check")
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
