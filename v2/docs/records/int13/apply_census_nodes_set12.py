#!/usr/bin/env python3
"""Set 12 (MESHSAT-1357, 29 September 2026): four signal nets declared as nodes so PWR-001's rail census reads them as what
they are. The third re-take moved two readings against main: board A's intent_rails PASS to INCONCLUSIVE (S-117's C233 on
IADPT and C234 on CH_COMP1 are capacitors to ground, the census's mark of a supply, and nothing settled the two nets) and
board B's PASS to FAIL (the check's minor M5 declared R536 and R537 as loads of +3V3_ZB, so the census followed the rail's
current into ZBA_RXD and ZBB_RXD and counted them as undeclared power nets). Each is a signal line: IADPT and COMP1 are U3's
analog pins (TI SLUSE66A, PDF page 8: IADPT, IBAT, COMP1 absolute maximum -0.3 to 3.6 V, recommended 0 to 3.3 V; PDF page 12:
the IADPT output clamp 3.1 to 3.3 V); ZBA_RXD and ZBB_RXD are the E72s' RX lines, U540's and U542's open-drain outputs pulled
up to the gated +3V3_ZB. Declared in the form EMCON_HW's node has (apply_emcon_hw_node_c.py), each peak from its source
(the datasheet's 3.3 V for U3's pins; `_intent.net_volts("+3V3_ZB")` for the RX lines, never typed). Declarations only: no
part, pin or net changes. Asserts each anchor once, re-parses both generators, refuses a second run."""
import ast, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
EDITS = (
    ("v2/ecad/tools/gen_sch_a.py", 'c("C234", "33p", "CH_COMP1", "GND")\n',
     "# IADPT AND CH_COMP1 DECLARED AS NODES (set 12, records/int13/apply_census_nodes_set12.py): C233 and C234 to ground are the\n"
     "# census's mark of a supply; both are U3's analog pins.\n"
     "_intent.node(\"IADPT\", 3.3, \"U3's adapter current monitor and inductance-programming pin: recommended 0 to 3.3 V and the \"\n"
     "             \"output clamp at most 3.3 V (TI SLUSE66A PDF pages 8 and 12); no part takes its supply from it\")\n"
     "_intent.node(\"CH_COMP1\", 3.3, \"U3's buck-boost compensation pin 1: recommended 0 to 3.3 V, absolute maximum 3.6 V (TI \"\n"
     "             \"SLUSE66A PDF page 8); no part takes its supply from it\")\n"),
    ("v2/ecad/tools/gen_sch_b.py", 'r("R536", "4.7k 1%", "ZBA_RXD", "+3V3_ZB", lcsc="C23162"); r("R537", "4.7k 1%", "ZBB_RXD", "+3V3_ZB", lcsc="C23162")\n',
     "# ZBA_RXD AND ZBB_RXD DECLARED AS NODES (set 12, records/int13/apply_census_nodes_set12.py): R536 and R537 are loads of\n"
     "# +3V3_ZB, so the census followed the rail's current into the E72s' RX lines; each is a signal line at most the rail.\n"
     "_intent.node(\"ZBA_RXD\", _intent.net_volts(\"+3V3_ZB\"), \"ZBA's RX line: U540's open-drain output pulled up to the gated \"\n"
     "             \"+3V3_ZB through R536 (SD-EMC-2, D4E-B); at most the rail; no part takes its supply from it\")\n"
     "_intent.node(\"ZBB_RXD\", _intent.net_volts(\"+3V3_ZB\"), \"ZBB's RX line: U542's open-drain output pulled up to the gated \"\n"
     "             \"+3V3_ZB through R537 (SD-EMC-2, D4E-B); at most the rail; no part takes its supply from it\")\n"),
)


def main():
    new = {}
    for rel, anchor, add in EDITS:
        p = os.path.join(TOP, rel)
        t = open(p, encoding="utf-8").read()
        if "apply_census_nodes_set12.py" in t: print("apply_census_nodes_set12: REFUSED: already applied to %s" % rel); return 2
        if t.count(anchor) != 1: print("apply_census_nodes_set12: REFUSED: the anchor in %s is not found once" % rel); return 2
        t2 = t.replace(anchor, anchor + add)
        ast.parse(t2)
        new[p] = t2
    for p, t2 in new.items():
        open(p, "w", encoding="utf-8").write(t2)
    print("apply_census_nodes_set12: IADPT and CH_COMP1 declared on board A, ZBA_RXD and ZBB_RXD on board B; regenerate both")
    return 0


if __name__ == "__main__":
    sys.exit(main())
