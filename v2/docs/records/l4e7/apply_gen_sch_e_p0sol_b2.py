#!/usr/bin/env python3
"""apply_gen_sch_e_p0sol_b2.py: DRAFT for board E's generator owner (task P0-7 of MESHSAT-1357, 5 October 2026, route B2 for D-10's
port-level residual, B2-PRESENCE.md). A PROPOSAL: the external interface it rests on (a presence contact pair in the solar
receptacle and at every mating point of the solar lead, make-last and break-first) is an owner item (B2-PRESENCE.md section 2).
NOT APPLIED to the tree; its author ran it only on scratch copies (the tests also write scratch copies).

Why (B2-PRESENCE.md; l4e7_p0sol.out section 5): a stiff source can step onto the solar port with the guard U21 already on only
because the guard stays on after the panel's plug is withdrawn: Q12's body diode and channel keep PV_F at the stage's voltage,
so U21's UVLO and INP stay high for seconds. With INP fed through a presence loop that the plug carries, the plug's withdrawal
pulls INP low (R97, with C80 as its filter) and U21 turns Q12 off before the power contacts part; a source arriving on the next
plug meets Q12 off, OV holding it off above the cut-off (and BST until it charges), and INP rises only when the presence pair
makes, last. The guard-on event is then removed for any source that arrives through a mating point the loop passes.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: R96 (INP's top) from PV_F to PV_PRA, the presence loop's outgoing
side; J_SOLP, a JST-XH 1x2 (B2B-XH-A, C158012, J_TAMP's part) carrying the loop to the inside lead (pin 1 PV_PRA, pin 2 back to
INP, PV_INP); C80, 10 nF C0G 100 V 1206 (C184799, C127's part) from INP to GND; U21's value text; the tracker section's list. U21,
R97 and every other part keep their nets.

ORDER: apply it AFTER apply_gen_sch_e_p0sol.py (it needs R97 24.9k) and so after the solar guard draft it follows; before L4-E11's
aux draft and d8dec31's input capacitor (it names J_SOLP and C80, which no later draft takes, and adds no capacitor above C148).

Usage:  apply_gen_sch_e_p0sol_b2.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a draft it follows
is not applied yet, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_p0sol_b2"
ADDS = ("J_SOLP", "C80")
BLOCK = (
    '# P0-7, ROUTE B2 (MESHSAT-1357, v2/docs/records/l4e7/B2-PRESENCE.md; a PROPOSAL until the owner rules the interface): THE\n'
    '# PRESENCE LOOP. R96, INP\'s top, feeds the solar receptacle\'s presence pair (J_SOLP pin 1, PV_PRA); the plug bridges the pair and\n'
    '# it returns on J_SOLP pin 2 to INP (PV_INP), where R97 holds INP low whenever the loop is open. With the plug withdrawn the guard\n'
    '# turns Q12 off (INP under V(INP_L) within about 0.54 ms, R97 x C80), and a source can only arrive with Q12 off, U21\'s OV holding\n'
    '# it off above the cut-off and BST until it charges; the pair must make last and break first at every mating point it passes\n'
    '# (L4-E9 R-180, the contact requirement). C80 filters INP against what the lead picks up; a broken or shorted presence core can\n'
    '# only hold INP low (the guard off).\n'
    'part("J_SOLP", "Connector_Generic", "Conn_01x02", "JST-XH 1x2 (B2B-XH-A): the solar receptacle\'s presence pair, the inside lead '
    'from the wall receptacle\'s presence contacts; the plug bridges them, make-last and break-first: 1 from R96, 2 to INP", "XH2", '
    '{"1": "PV_PRA", "2": "PV_INP"}, "C158012")\n'
    'c("C80", "10n C0G 5% 100V 1206 (INP filter: the presence loop\'s pickup, P0-7)", "PV_INP", "GND", "C10u50", lcsc="C184799")\n'
)
EDITS = [
    ('r("R96", "100k 0.1% 25ppm (INP top; YAGEO RT0603BRD07100KL, LCSC code owed)", "PV_F", "PV_INP", "R"); ',
     'r("R96", "100k 0.1% 25ppm (INP top, through the presence loop since P0-7 B2; YAGEO RT0603BRD07100KL, LCSC code owed)", "PV_F", "PV_PRA", "R"); '),
    ('"PV_INP", "GND", "R", "C136967")\n',
     '"PV_INP", "GND", "R", "C136967")\n' + BLOCK),
    ('(panel port cut-off): on by 9.16 V, off above',
     '(panel port cut-off): on by 10.05 V with the presence pair closed (P0-7), off above'),
    ('"R96", "R97", "R98"',
     '"R96", "R97", "J_SOLP", "C80", "R98"'),
]
# the texts of the drafts this one follows: P0-7's R97 (24.9k) and the solar guard's R96 and U21
NEEDS = ('r("R97", "24.9k 0.1% 25ppm (INP: high from 10.05 V', 'ic("U21", 20, "TPS48110AQDGXRQ1', 'ic("U23", 5, "INA169NA/3K')


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def first_args(text):
    out = set()
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            out.add(n.args[0].value)
    return out


def patched(text):
    if all(text.count(rep) == 1 for _o, rep in EDITS):
        refuse("already applied (every new text is present)")
    for need_ in NEEDS:
        if need_ not in text:
            refuse("a draft this one follows is not applied (no %s)" % need_.split("(")[0])
    if any(a in first_args(text) for a in ADDS):
        refuse("a reference this draft adds (%s) is already drawn" % ", ".join(a for a in ADDS if a in first_args(text)))
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
    if not all(a in first_args(new) for a in ADDS):
        refuse("the result does not draw J_SOLP and C80")
    return new


# NOT RELEASED: a PROPOSAL of task P0-7 for board E's generator owner, never applied by its author. Writing the repository's own
# gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; P0-7's route B2 waits on the owner's ruling and an accepted check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_e.py", "b/gen_sch_e.py", n=0))
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
