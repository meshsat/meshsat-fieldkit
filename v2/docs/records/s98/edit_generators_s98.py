#!/usr/bin/env python3
"""Stream s98 (MESHSAT-1357, 28 September 2026): the note and comment rewrites in the two generators this stream owns,
made AFTER v2/docs/records/cx1/apply_declarations_draft.py was applied (its four entries carry the interim figures).
Kept as the byte-exact account of every change beyond the draft's, and runnable once on a tree that carries the draft:
each replacement asserts its old text occurs exactly once, the result must parse (ast), and a tree that already carries
the new text is refused. Prototype design, AI engineering work; nothing built, ordered or measured.

What it changes and why (the record's README.md carries the sources):
  gen_sch_a.py
    A1  the slot rails' intent note said "5 A peak at the module" for every slot; slot 2's converter has been an LM5176
        stage since F-PR-04 and its figures are the interim 4.2 / 5.63 A. The note is per slot now: slot 2 carries the
        INTERIM statement (source pages, the INCONCLUSIVE mode current, the 7.28 A bound against the loop minimum);
        slots 1 and 3 keep 5 A and name it as the AP64500's rating.
    A2  the draft's three comment lines above the +5V_DEV call said the 6.9 A peak is stale and a decision is owed;
        the registry gives that decision to S-99 (stream s99), so the comment says the peak is held as is and why.
    A3  the +5V_DEV intent note ended "the Glenair port's 0.9 A takes the peak to 6.9 A"; it now says what the figures
        are (INTERIM typical 5.1 A, the mode current INCONCLUSIVE, the 6.9 A peak held pending S-99).
  gen_sch_b.py
    B1  three comment lines above the slot-rail call still said the peak stays 5.0 A and I-03 is open.
    B2  the shared note said the receptacle carries 2.5 A; slot 2 carries 4.2 A typical.
    B3  M7: U25's branch comment said 1.4 A at 3.3 V; the allocation 0.90 A is the declared 1.2 A typical converted.
    B4  M7: U21's branch (the LoRa module at 1 W transmit) 0.60 -> 0.70 A, the child rail's declared burst, which
        bounds Ebyte's 650 mA typical instantaneous TX current (no maximum stated).
    B5  M7: U40, U50, U60 (the AP2112K-3.3 LDOs) 0.05 -> 0.12 A each, the child rails' declared typical; the sheet's
        tables give the quiescent current at no load only (55 uA typical, 80 uA maximum).
    B6  the +3V3_DEV comment said its loads sum to 1.38 A; they sum to 1.58 A since round 8 and w3b.
"""
import ast, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
A = os.path.join(ROOT, "v2/ecad/tools/gen_sch_a.py")
B = os.path.join(ROOT, "v2/ecad/tools/gen_sch_b.py")

EDITS = {
    A: [
        ("A1",
         '                 note="one CM5 slot with its cooler fan; 5 A peak at the module; the rail net starts at the "\n'
         '                      "INA226 shunt. This board\'s share of the 2 percent is 0.5 point, measured 0.07")\n',
         '                 note=("one CM5 slot with its cooler fan and the 5G module on the M.2 socket. INTERIM (S-98, finding I-03, "\n'
         '                       "28 September 2026): 4.2 A typical and 5.63 A peak, aligned to board B\'s derivation from the held maker "\n'
         '                       "pages (the CM5\'s 0.9 A typical, release 3 Table 9, no maximum published; the RM520N-GL\'s 3 A continuous "\n'
         '                       "and 4 A peak supply capability, Hardware Design v1.0 and v1.1); the PS-ALLTX mode current is INCONCLUSIVE, "\n'
         '                       "no held document decides it (v2/docs/records/cx1/ANALYSIS.md, CORRECTION.md B1); the all-peak conditional "\n'
         '                       "bound, 7.28 A, sits above the LM5176 stage\'s average loop minimum of 7.10 to 7.17 A (SNVSAI1D VSNS 43 mV "\n'
         '                       "over the 6 mOhm ISNS shunt at +1 percent and nominal). The rail net starts at the INA226 shunt. This "\n'
         '                       "board\'s share of the 2 percent is 0.5 point, measured 0.07" if _n == "2" else\n'
         '                       "one CM5 slot with its cooler fan; 5 A peak at the module, the AP64500\'s rating (DS41979 p.1); the rail "\n'
         '                       "net starts at the INA226 shunt. This board\'s share of the 2 percent is 0.5 point, measured 0.07"))\n'),
        ("A2",
         '# INTERIM I-03: typical 3.8 B + 1.0 D8 + 0.3 wall; PS-ALLTX INCONCLUSIVE.\n'
         '# Peak 6.9 A is stale: SESSION decision owed on 8.9 A coincident bound\n'
         '# (7.9 A with D8 typical) and LM5176 average-loop fold-back risk.\n',
         '# INTERIM I-03 (S-98, 28 September 2026): typical 5.1 A = board B\'s 3.8 A arriving at J_5V_DEV + the D8 mezzanine\'s 1.0 A\n'
         '# behind U23 + the wall port\'s 0.3 A allocation behind U32; the PS-ALLTX mode current is INCONCLUSIVE (records/cx1).\n'
         '# The 6.9 A peak is HELD AS IS: open item S-99 (stream s99) decides it. It is board B\'s 6.0 A plus the wall port\'s 0.9 A\n'
         '# with the D8 mezzanine at zero; the coincident figures are 7.9 A (D8 at its 1.0 A typical) and 8.9 A (every declared\n'
         '# limit), both above the LM5176 average loop\'s 7.10 A minimum (the ISNS shunt at +1 percent), which is S-99\'s question.\n'),
        ("A3",
         ' 26 September 2026 (F-PR-04, D-12): the converter is an LM5176 stage with a 7.2 A minimum average limit, and the '
         'Glenair port\'s 0.9 A takes the peak to 6.9 A.")\n',
         ' 26 September 2026 (F-PR-04, D-12): the converter is an LM5176 stage with a 7.2 A minimum average limit (7.10 A with '
         'the ISNS shunt at +1 percent, 7.17 A nominal: SNVSAI1D VSNS 43 mV over 6 mOhm), and the declared peak became 6.9 A, '
         'board B\'s 6.0 A plus the Glenair port\'s 0.9 A with the D8 mezzanine at zero. 28 September 2026 (S-98, finding I-03, '
         'INTERIM): the typical is 5.1 A, board B\'s 3.8 A at J_5V_DEV plus the D8 mezzanine\'s 1.0 A behind U23 plus the wall '
         'port\'s 0.3 A allocation behind U32; the PS-ALLTX mode current is INCONCLUSIVE (v2/docs/records/cx1/CORRECTION.md B2). '
         'The 6.9 A peak is held pending S-99: the coincident figures are 7.9 A with D8 at its typical and 8.9 A at every '
         'declared limit, both above the loop\'s minimum.")\n'),
    ],
    B: [
        ("B1",
         '    # against the 2.5 A this line declared for every slot. The peak stays the source\'s 5.0 A (board A\'s AP64500).\n'
         '    # Fix-up, 26 September 2026: whether the socket\'s two 220 uF carry the 5G burst so that +5V_S2 stays under that\n'
         '    # 5.0 A is NOT computed here; the coincident worst case is open item I-03 on board A (drafts/r4-interfaces.md).\n',
         '    # against the 2.5 A this line declared for every slot. The peak stayed the source\'s 5.0 A (board A\'s AP64500 on slots\n'
         '    # 1 and 3; slot 2\'s converter on board A has been an LM5176 stage since F-PR-04, and its peak is 5.63 A since S-98).\n'
         '    # Fix-up, 26 September 2026: whether the socket\'s two 220 uF carry the 5G burst so that +5V_S2 stays under 5.0 A\n'
         '    # is NOT computed here; the coincident worst case was open item I-03 on board A (drafts/r4-interfaces.md), answered\n'
         '    # INTERIM by S-98 (28 September 2026): slot 2 declares the 5.63 A coincidence as its peak at both ends of the lead,\n'
         '    # the PS-ALLTX mode current INCONCLUSIVE, no held document decides it (v2/docs/records/cx1/ANALYSIS.md).\n'),
        ("B1b",
         '    # typical is 4.2 A. The coincident peak with the module at 4 A becomes 5.63 A (I-03).\n',
         '    # typical is 4.2 A. The coincident peak with the module at 4 A becomes 5.63 A (I-03), the peak this line declares for\n'
         '    # slot 2 since S-98.\n'),
        ("B2",
         '                      "VH header across the board to a module receptacle carrying 2.5 A")\n',
         '                      "VH header across the board to a module receptacle carrying 2.5 A (4.2 A typical on slot 2)")\n'),
        ("B3",
         '              "U25": 0.90,           # the AP63203 buck -> +3V3_DEV, 1.4 A at 3.3 V through it\n',
         '              "U25": 0.90,           # the AP63203 buck -> +3V3_DEV: its declared 1.2 A typical at 3.3 V through 0.88 from 5.0 V\n'
         '                                     # (1.2 x 3.3 / 0.88 / 5.0 = 0.90 A). S-98 M7: this comment said 1.4 A, an older sum of that\n'
         '                                     # rail\'s loads, against the declared 1.2 A; the allocation matched the declaration and stands.\n'),
        ("B4",
         '              "U21": 0.60,           # load switch -> +5V_LORA, the E22-900M30S at 1 W transmit\n',
         '              "U21": 0.70,           # load switch -> +5V_LORA, the E22-900M30S at 1 W transmit: the child rail\'s declared 0.70 A\n'
         '                                     # burst, which bounds Ebyte\'s 650 mA typical instantaneous TX current, no maximum stated\n'
         '                                     # (E22-900M30S user manual v1.20, 2.2, PDF p.3); was 0.60 (S-98 M7, 28 September 2026)\n'),
        ("B5",
         '              "U40": 0.05, "U50": 0.05, "U60": 0.05,      # the three controllers\' private 3.3 V LDOs\n',
         '              "U40": 0.12, "U50": 0.12, "U60": 0.12,      # the three controllers\' private 3.3 V LDOs (AP2112K-3.3): each child rail\n'
         '                                     # +3V3_IOCx declares 0.12 A typical and 0.25 A peak, and an LDO\'s input is its output plus\n'
         '                                     # its ground current; the sheet\'s tables give that at no load only, 55 uA typical and 80 uA\n'
         '                                     # maximum (Diodes DS39724 Rev. 2-2, pp.4 to 6), so 0.12 A each holds for any ground current\n'
         '                                     # under 5 mA at 0.12 A out, a figure the tables do not state; were 0.05 (S-98 M7)\n'),
        ("B6",
         '# against a current that can never flow in it. 2.0 A is what the part gives; the loads below sum to 1.38 A.\n',
         '# against a current that can never flow in it. 2.0 A is what the part gives; the loads below summed to 1.38 A when this\n'
         '# was written and sum to 1.58 A since round 8 and w3b (U11 0.165, the thirty-six single gates; S-98 M7, 28 September 2026).\n'),
    ],
}


def main():
    changed = 0
    for path, edits in EDITS.items():
        t = open(path, encoding="utf-8").read()
        out = t
        for tag, old, new in edits:
            assert old != new, tag
            if out.count(old) != 1:
                if out.count(new) == 1 and out.count(old) == 0:
                    raise SystemExit("edit_generators_s98: REFUSED: %s is already applied in %s" % (tag, os.path.basename(path)))
                raise SystemExit("edit_generators_s98: REFUSED: %s: old text occurs %d time(s) in %s" % (tag, out.count(old), os.path.basename(path)))
            out = out.replace(old, new, 1)
        assert out != t, path
        ast.parse(out, filename=path)
        open(path, "w", encoding="utf-8").write(out)
        ast.parse(open(path, encoding="utf-8").read(), filename=path)
        changed += 1
        print("edit_generators_s98: %s: %d edit(s) applied, parses" % (os.path.basename(path), len(edits)))
    print("edit_generators_s98: %d file(s) changed" % changed)


if __name__ == "__main__":
    main()
