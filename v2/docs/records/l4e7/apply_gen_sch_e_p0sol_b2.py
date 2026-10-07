#!/usr/bin/env python3
"""apply_gen_sch_e_p0sol_b2.py: DRAFT for board E's generator owner (task P0-7 of MESHSAT-1357, 5 October 2026, route B2 for D-10's
port-level residual, B2-PRESENCE.md). UNSELECTED and WITHDRAWN AS DRAFTED (Astra's cx45 and cx46, Q6; the owner's reviews,
parts 24 and 25): kept as the record of the route and for its separate check only (SESSION L4E7-D1, 7 October 2026: no presence-pair route is taken up, so the tree's generator is refused whatever RELEASE.md says). No owner item rests on it; the approved
interface stands (the panel on the shore plug's second pair, no presence pair). NOT APPLIED to the tree; its author ran it only on
scratch copies (the tests also write scratch copies).

Why (B2-PRESENCE.md; l4e7_p0sol.out section 5): a stiff source can step onto the solar port with the guard U21 already on
because the guard stays on after the panel's plug is withdrawn: Q12's body diode and channel keep PV_F at the stage's voltage,
so U21's UVLO and INP stay high. With INP fed through a presence loop that the plug carries, the plug's withdrawal pulls INP low
(R97, with C80 as its filter) and U21 turns Q12 off at most 0.544 ms after the pair opens. The INTENT is that a source arriving
on the next plug meets Q12 off; that is NOT PROVEN and the cold-connection guarantee is WITHDRAWN (cx45, Q6): no sequenced
connector is chosen, no worst-case contact and control timing is bounded (a 1 mm lead is 0.5 ms at 2 m/s, under the turn-off;
bounce; BST stays charged from the back-fed VS, TI SLUSEE5E p.17), and the complete enable path is not simulated. The pair's
faults are NOT fail-safe (l4e7_p0sol.out section 5f): the two cores shorted together defeat the loop silently, and a core
shorted to a positive core of the lead puts INP over its 20 V absolute maximum (P2, P3: REMAINING ENGINEERING outside the
baseline, owed by any presence-pair route taken up again). No protection credit is taken for this draft.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: R96 (INP's top) from PV_F to PV_PRA, the presence loop's outgoing
side; J_SOLP, a JST-XH 1x2 (B2B-XH-A, C158012, J_TAMP's part) carrying the loop to the inside lead (pin 1 PV_PRA, pin 2 back to
INP, PV_INP); C80, 10 nF C0G 100 V 1206 (C184799, C127's part) from INP to GND; U21's value text; the tracker section's list. U21,
R97 and every other part keep their nets.

ORDER: NOT in L4-E9's change list and not part of the baseline (the owner's review, part 24: the baseline does not depend on an
unapproved proposal). Only for the separate check (l4e7_p0sol.py ORDER_E_B2): AFTER apply_gen_sch_e_p0sol.py (it needs R97
24.9k) and so after the solar guard draft it follows; before L4-E11's aux draft and d8dec31's input capacitor (it names J_SOLP and
C80, which no later draft takes, and adds no capacitor above C148).

Usage:  apply_gen_sch_e_p0sol_b2.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a draft it follows
is not applied yet, or the repository's own generator is named, which is refused always since SESSION L4E7-D1)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_p0sol_b2"
ADDS = ("J_SOLP", "C80")
BLOCK = (
    '# P0-7, ROUTE B2 (MESHSAT-1357, v2/docs/records/l4e7/B2-PRESENCE.md; UNSELECTED, WITHDRAWN AS DRAFTED, no protection\n'
    '# credit, never part of the baseline): THE PRESENCE LOOP. R96, INP\'s top, feeds the solar receptacle\'s presence pair (J_SOLP pin 1,\n'
    '# PV_PRA); the plug bridges the pair and it returns on J_SOLP pin 2 to INP (PV_INP), where R97 holds INP low whenever the loop\n'
    '# is open. With the plug withdrawn the guard turns Q12 off (INP under V(INP_L) within about 0.54 ms, R97 x C80). Whether a\n'
    '# source then arrives with Q12 off is NOT proven (no chosen sequenced connector, no contact and control timing proof, BST kept\n'
    '# charged from the back-fed VS): the cold-connection guarantee is withdrawn (cx45). The pair\'s faults are not fail-safe: the two\n'
    '# cores shorted together defeat the loop silently (INP about 0.2 x PV_F), and a core shorted to a positive core of the lead puts\n'
    '# INP at PV_F, over its 20 V absolute maximum: REMAINING ENGINEERING outside the baseline (B2-PRESENCE.md 5b).\n'
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


# NOT RELEASED: a WITHDRAWN draft of task P0-7 (route B2, unselected), never applied by its author. Writing the repository's own
# gen_sch_e.py is refused ALWAYS (SESSION L4E7-D1, 7 October 2026, B2-PRESENCE.md section 8: no presence-pair route is taken up),
# whatever record l4e7's RELEASE.md says (it releases the record's other drafts). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    """SESSION L4E7-D1 (7 October 2026, B2-PRESENCE.md section 8): no presence-pair route is taken up, so this WITHDRAWN draft is
    never released onto the repository's own generator. Record l4e7's RELEASE.md releases the record's other drafts and is not
    read here: before L4E7-D1 a RELEASE.md written for the baseline's C2 sense (R-240) would have released this draft too.
    The separate check composes the draft on scratch copies only (l4e7_p0sol.py ORDER_E_B2), which this function never gates.
    Before L4E7-D1 this function read RELEASE.md's first line ("released: yes") and one accepted check named in it; that guard is
    kept in the history of this file (its commit before stream l4small's apply script), not as a route. To reverse: reverse
    L4E7-D1 first (a presence-pair route taken up as a new route with its own check, B2-PRESENCE.md section 5b's detection and
    INP protection drafted, composed and mutated), then restore the RELEASE.md guard from this file's history; until then every
    call of this function on the repository's own generator ends the run with exit 3 and the message below, so no route B2
    edit can reach gen_sch_e.py through this script.
    """
    refuse("NOT RELEASED: route B2 is UNSELECTED and WITHDRAWN AS DRAFTED and no presence-pair route is taken up "
           "(SESSION L4E7-D1, B2-PRESENCE.md section 8): no RELEASE.md releases this draft onto the tree's generator")


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
