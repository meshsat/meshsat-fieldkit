#!/usr/bin/env python3
"""apply_check_dd7_fetpair.py: DRAFT, the companion of apply_gen_sch_a_fetpair.py (record l4e11 round FET, task L4A-70, MESHSAT-1357,
7 October 2026). NOT APPLIED; applied together with the fallback only, on a negative E-05.

check_dd7_netlist.py's BODY group (round 12) reads the charger draft's three battery FETs; once the fallback (ii) draws the pair, its
tuple BATFETS must name Q39 and Q40, or DD-7's check reads FAIL on a board that is right. This script makes that one change: the old
line must occur exactly once, the new text must differ and must not occur yet, and the result must parse.

Usage:  apply_check_dd7_fetpair.py TARGET [--check | --write]     (default --check; TARGET is a copy of check_dd7_netlist.py, or the
tree's own file once RELEASE.md beside this script releases the fallback as apply_gen_sch_a_fetpair.py reads it)
Exit 0: checked (or written); 3: refused."""
import ast
import os
import sys

NAME = "apply_check_dd7_fetpair"
OLD = 'BATFETS = ("Q39", "Q40", "Q42")       # the charger draft\'s three battery FETs (round 12\'s BODY group)\n'
NEW = ('BATFETS = ("Q39", "Q40")              # the battery FETs: the pair of record l4e11 round FET\'s fallback (ii), Q42 removed\n'
       '                                      # (apply_gen_sch_a_fetpair.py); round 12\'s BODY group reads each\n')
HERE = os.path.dirname(os.path.abspath(__file__))
TREE_CHECK = os.path.join(os.path.dirname(HERE), "check_dd7_netlist.py")     # records/l4e11/


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_CHECK):
        sp = __import__("importlib.util").util.spec_from_file_location("fetpair", os.path.join(HERE, "apply_gen_sch_a_fetpair.py"))
        m = __import__("importlib.util").util.module_from_spec(sp)
        sp.loader.exec_module(m)
        m.released()
    text = open(target, encoding="utf-8").read()
    if text.count(NEW) != 0:
        refuse("already applied")
    if text.count(OLD) != 1:
        refuse("the old line occurs %d times, not once" % text.count(OLD))
    new = text.replace(OLD, NEW)
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    if not write:
        print("%s: CHECK OK, 1 edit, nothing written" % NAME)
        return 0
    open(target, "w", encoding="utf-8").write(new)
    if open(target, encoding="utf-8").read() != new:
        refuse("the written file does not read back")
    print("%s: WRITTEN, 1 edit" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
