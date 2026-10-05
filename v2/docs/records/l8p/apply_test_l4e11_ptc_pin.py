#!/usr/bin/env python3
"""apply_test_l4e11_ptc_pin.py: a text draft for the integrator and task L4-E11's author (Layer 8 record l8p, round 6, MESHSAT-1357,
4 October 2026). NOT APPLIED by this record: test_l4e11.py is L4-E11's file.

Why. L4-E11's test pins record l8p's board A PTC draft by sha256 (test_l4e11.py, `L8P3_PTC`, the draft as it stood from round 3 to
round 5: d9c43966...). Round 6 corrected that draft's quote of Murata's sheet in its docstring, in the comment it writes and in RT1's
value text (the coordinator's brief, item 7; L8P-BREAKER.md section 12j), so its sha256 is now cedae4eb.... On a line that holds
both, `test_l4e11.t_round10_dd7_composes_runs_to_its_end_and_reads_drawn_and_its_mutations_fail` stops at that pin with "is not the
one this record composed with". Read on a scratch merge of fnd/l8p2 with fnd/l4e11r11 at ac72e730 (4 October 2026): with the pin
as it is, test_l4e11 68 passed, 1 failed; with this one pin moved, 69 passed, 0 failed. Nothing else in L4-E11's record reads the
draft's bytes from the tree (its script reads record l8p from a commit).

What it changes in v2/ecad/tools/tests/test_l4e11.py, and nothing else: the sha256 in the `L8P3_PTC = (...)` line.

It checks by default and writes only with --write. It refuses unless: the old pin occurs exactly once, on the L8P3_PTC line; the
new pin is not yet there; the tree's v2/docs/records/l8p/apply_gen_sch_a_ptc.py IS the new sha256 (so the pin never moves ahead of
the draft); the result parses. A second run finds the new pin and refuses.
Usage (repository root):  python3 v2/docs/records/l8p/apply_test_l4e11_ptc_pin.py [TARGET] [--write]     exit 0 OK, 3 refused."""
import ast
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
OLD = "d9c43966985172876ad1ea7339b417d31ecf10cd85824da1b983c3b1eb8b73d6"
NEW = "cedae4eb4572a6a5b137dfc151b07d96ac9004e332317dba1c6d703941ce95c0"
LINE = 'L8P3_PTC = ("v2/docs/records/l8p/apply_gen_sch_a_ptc.py", "%s")'


def refuse(msg):
    sys.stderr.write("apply_test_l4e11_ptc_pin: REFUSED: %s\n" % msg)
    return 3


def main(argv):
    write = "--write" in argv
    args = [a for a in argv if a != "--write"]
    target = os.path.abspath(args[0]) if args else os.path.join(ROOT, "v2", "ecad", "tools", "tests", "test_l4e11.py")
    draft = os.path.join(HERE, "apply_gen_sch_a_ptc.py")
    if hashlib.sha256(open(draft, "rb").read()).hexdigest() != NEW:
        return refuse("this tree's apply_gen_sch_a_ptc.py is not the round 6 draft (%s...): the pin is not moved ahead of the draft" % NEW[:8])
    if not os.path.isfile(target):
        return refuse("%s is not there" % target)
    text = open(target, encoding="utf-8").read()
    if LINE % NEW in text:
        return refuse("the new pin is already in %s (a second application)" % os.path.basename(target))
    if text.count(LINE % OLD) != 1 or text.count(OLD) != 1:
        return refuse("%s does not carry the pin d9c43966... once on its L8P3_PTC line (an L4-E11 before its round 10, or a later one)" % os.path.basename(target))
    new = text.replace(LINE % OLD, LINE % NEW)
    assert new != text and new.count(NEW) == 1 and OLD not in new
    ast.parse(new)
    if not write:
        print("apply_test_l4e11_ptc_pin: CHECK OK (%s: one line would change; --write to apply)" % os.path.basename(target))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    ast.parse(open(target, encoding="utf-8").read())
    print("apply_test_l4e11_ptc_pin: WRITTEN (%s: L8P3_PTC's sha256 d9c43966... to cedae4eb...)" % os.path.basename(target))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
