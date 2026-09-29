#!/usr/bin/env python3
"""Set 12 (MESHSAT-1357, 29 September 2026): board C declares EMCON_HW as a node. D4E-F1's D23 (anode EMCON_HW, cathode
TX_INHIBIT_n) joins the line to TX_INHIBIT_n, which board C declares as a node; PWR-001's census (intent_rails) then read
EMCON_HW as a net that "carries the mark of a supply" with nothing declared to settle it, and moved board C's reading from
PASS to INCONCLUSIVE, a new layout-entry reason. EMCON_HW is U9's output line: the declaration states what it is, in the form
TX_INHIBIT_n's has (its peak from U9's supply, the TLV75533's 1 percent; no part takes its supply from it). A declaration only:
no part, pin or net changes. Asserts the anchor once, re-parses, refuses a second run. Run from the repository root."""
import ast, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/gen_sch_c.py")
ANCHOR = ("part takes its supply from it (U9, U14 and the far gates read it)\", v_work=3.333)\n")
ADD = ("# EMCON_HW DECLARED AS A NODE (set 12, MESHSAT-1357, 29 September 2026): D4E-F1's D23 joins it to TX_INHIBIT_n, so PWR-001's\n"
       "# census read it as a possible supply with nothing to settle it; it is U9's output line, declared here in TX_INHIBIT_n's form.\n"
       "_intent.node(\"EMCON_HW\", 3.333, \"the hardware EMCON line as board C drives it: U9 (74LVC1G17, rail-to-rail on +3V3) through \"\n"
       "             \"R52 (330R 1 percent), clamped by D23 (BAT46W) to TX_INHIBIT_n; at most +3V3 at the TLV75533's 1 percent (TI \"\n"
       "             \"SBVS320D, 'Output accuracy: 1%'), and no part takes its supply from it (U13, U14 and board B's gates read it)\", v_work=3.333)\n")


def main():
    t = open(P, encoding="utf-8").read()
    if '_intent.node("EMCON_HW"' in t: print("apply_emcon_hw_node_c: REFUSED: already applied"); return 2
    if t.count(ANCHOR) != 1: print("apply_emcon_hw_node_c: REFUSED: the anchor is not found once"); return 2
    t2 = t.replace(ANCHOR, ANCHOR + ADD)
    ast.parse(t2)
    open(P, "w", encoding="utf-8").write(t2)
    print("apply_emcon_hw_node_c: EMCON_HW declared as a node on board C; regenerate board C next")
    return 0


if __name__ == "__main__":
    sys.exit(main())
