#!/usr/bin/env python3
"""draft_gen_c_c1_c2.py: a DRAFT for board C's generator, not applied by stream w5identc (MESHSAT-1357, round 3, minor 9).

What it answers. gen_sch_c.py draws C1 (+5V) and C2 (+3V3) as "10u" 0805 with the order code C15850, which this tree's
catalogue reading (v2/docs/parts/readings/lcsc-2026-09-27.json) gives as Samsung Electro-Mechanics CL21A106KAYNNNE, X5R,
25 V. The value states no dielectric, so rule C-D3 asks X7R, and the table's identity of the selection (S-6d1de2f8e8) is
YAGEO CC0805KKX7R7BB106, DECODED on YAGEO's V.26 page 2 against that requirement, with the order code C326595 (stream
w5ident's catalogue reading of 27 September 2026; C326595 is NOT in this tree's reading). So the identity is the right
part under the table's rules and the generator's code orders another part (X5R). This draft moves the two rows to
C326595. The other way out is the author's: state X5R in the value with rule C-D3b's hot-spot reasoning.

After it (the integrator's, if taken): regenerate board C on the box, re-read C326595 into the tree's catalogue reading,
re-run v2/docs/records/w5identc/build_table.py and part_identities.py check.
Asserts: the line is present once, the new text differs, the file parses (ast) after, a second run is refused.
Usage: draft_gen_c_c1_c2.py [--apply]   (default: check only, print the change, write nothing)"""
import ast, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "ecad", "tools", "gen_sch_c.py"))
OLD = 'c("C1", "10u", "+5V", "GND", "C10u", "C15850"); c("C2", "10u", "+3V3", "GND", "C10u", "C15850")'
NEW = 'c("C1", "10u", "+5V", "GND", "C10u", "C326595"); c("C2", "10u", "+3V3", "GND", "C10u", "C326595")'


def main(argv):
    src = open(GEN, encoding="utf-8").read()
    assert NEW not in src, "refused: the generator already carries the change (a second run)"
    assert src.count(OLD) == 1, "the line of C1 and C2 is not present exactly once"
    out = src.replace(OLD, NEW)
    assert out != src
    ast.parse(out)
    print("draft_gen_c_c1_c2: %s\n  - %s\n  + %s" % (os.path.relpath(GEN), OLD, NEW))
    if "--apply" not in argv:
        print("draft_gen_c_c1_c2: check only, nothing written"); return 0
    open(GEN, "w", encoding="utf-8").write(out)
    ast.parse(open(GEN, encoding="utf-8").read())
    print("draft_gen_c_c1_c2: written; regenerate board C on the box next")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
