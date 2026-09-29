#!/usr/bin/env python3
"""Set 12 (MESHSAT-1357, 29 September 2026), a second census declaration: the fourth re-take read board B's intent_rails FAIL on
three undeclared power nets, LED_ACT_A1 to LED_ACT_A3. Stream rf2walk's LED follow-up (apply_b_chk12_led.py) declared each
slot's ACT LED feed resistor as a load of its module rail, so the census followed the rail's current into the LED's anode net.
Each is a signal net: the anode between the feed resistor and the LED, at most the module rail. Declared as a node in the form
of apply_census_nodes_set12.py, per slot, its peak from the rail itself (`_intent.net_volts(cm33)`, never typed). A declaration
only: no part, pin or net changes. Asserts the anchor once, re-parses, refuses a second run."""
import ast, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/gen_sch_b.py")
ANCHOR = '    r(R(48), "1k", cm33, "LED_ACT_A%d" % s); led("LED%d6" % s, "green ACT (LED_nACT sinks)", "LED_ACT_A%d" % s, "LED_nACT%d" % s)\n'
ADD = ('    # LED_ACT_A{s} DECLARED AS A NODE (set 12, records/int13/apply_census_nodes2_set12.py): the feed resistor is a declared load of\n'
       '    # the module rail, so the census followed its current into the anode; the anode is a signal net at most the rail.\n'
       '    _intent.node("LED_ACT_A%d" % s, _intent.net_volts(cm33), "slot %d\'s ACT LED anode between its 1k feed from %s and the LED; "\n'
       '                 "at most the module rail; no part takes its supply from it" % (s, cm33))\n')


def main():
    t = open(P, encoding="utf-8").read()
    if "apply_census_nodes2_set12.py" in t: print("apply_census_nodes2_set12: REFUSED: already applied"); return 2
    if t.count(ANCHOR) != 1: print("apply_census_nodes2_set12: REFUSED: the anchor is not found once"); return 2
    t2 = t.replace(ANCHOR, ANCHOR + ADD)
    ast.parse(t2)
    open(P, "w", encoding="utf-8").write(t2)
    print("apply_census_nodes2_set12: LED_ACT_A1 to LED_ACT_A3 declared as nodes on board B; regenerate board B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
