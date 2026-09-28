#!/usr/bin/env python3
"""Board E, finding E-F1 of the review of decision 31: the ideal diode controller's input capacitor (MESHSAT-1357,
worker d8dec31, 28 September 2026). A PROPOSAL for the owner of gen_sch_e.py in the next circuit round; this stream
commits nothing over the generator, the schematic or the netlist.

THE FINDING. U3 is the LM74700-Q1 of the shore and vehicle entry, its ANODE on DC_F. TI SNOSD17G (v2/vendor/ti/
ti-lm74700-q1.pdf), 10.1.1.2.3, p.17: "Minimum required capacitance for charge pump VCAP and input/output capacitance
are: VCAP: Minimum 0.1 uF is required ... CIN: minimum 22 nF of input capacitance; COUT: minimum 100 nF of output
capacitance". On the set 6 netlist (sha256 56adc9746d61c4e0...) DC_F carries C4 alone, and C4 is the VCAP capacitor
(U3_VCAP to DC_F); C2 (100 nF 100 V) is COUT on DC_P. No capacitor stands between DC_F and the entry's return GND_V.

WHY IT MATTERS TO DECISION 31. With no capacitance on DC_F an electrostatic discharge at the DC pin of the wall
receptacle drives DC_F to D10's clamping voltage in either direction. In the negative direction D10 (SMCJ40CA)
conducts from 44.4 V and clamps at 64.5 V at 23.3 A (Littelfuse SMCJ series, revised 11/20/15, p.2), so Q1 sees the
voltage held on DC_P plus that: above Q1's 60 V (Infineon BSC039N06NS Rev.2.4, p.1) and U3's 75 V CATHODE to ANODE
(SNOSD17G 6.1, p.4), which TI's 10.1.1.3 (p.18) names as the criterion. The generator's own comment records this for
a negative SURGE, which is not claimed (owner ruling D-16); an electrostatic discharge is the ruled level (decision
34). With the capacitor the whole charge of the IEC 61000-4-2 network (150 pF: 1.2 uC at 8 kV, 2.25 uC at 15 kV)
moves DC_F by 1.2 V and 2.25 V at 1 uF nominal, and by ten times that if direct voltage bias left a tenth of it (the
part's bias curve is not held): the clamp is not reached and Q1 stays inside its rating.

THE CHANGE. One capacitor, 1 uF 100 V X7R 1210, with the distributor code C382212. WHERE THE CODE COMES FROM (the
fresh check's item M7): board E's C6 and C7 have the same value text ("1u 100V 1210") and carry NO code in gen_sch_e.py
(line 399); the code is board A's C207's, which gen_sch_a.py fits three times with that value text (lines 665, 729 and
800: PSA FS32X105K101EFG, C382212, "1u 100V 1210"). So the new part is board A's C207, not "the part of C6 and C7";
C6 and C7 are the same value with no code, and whether they should carry this code is board E's owner's. (The code board A's
C207 carries), from DC_F to GND_V, declared at U3's ANODE (pin 6) so the placement seats it at the pin, which is also
at the fuse and the connector. 22 nF is the maker's minimum; 1 uF is taken so that the minimum holds at any bias
derating a class II dielectric can show, and because it is the part already on the bill. It sees a reversed input as
a ceramic does, without polarity. Its reference is the next free C at apply time.

Usage: apply_gen_sch_e_cin.py <gen_sch_e.py> <pcb-e1-dock.net> [--check]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genpatch as G

WHAT = "apply_gen_sch_e_cin"
MARK = "DECISION 31's REVIEW, FINDING E-F1"


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    path, net, dry = argv[0], argv[1], "--check" in argv
    old = open(path, encoding="utf-8").read()
    G.refuse_second_run(old, MARK, WHAT)
    (ref,) = G.next_free("C", net, old)
    t = old
    a = 'ideal_diode("U3", "Q1", "C4", "R1", "DC_F", "DC_P", "GND_V")\n'
    t = G.sub_once(t, a, a +
                   "# " + MARK + " (28 September 2026, MESHSAT-1357): THE IDEAL DIODE HAD NO INPUT CAPACITOR.\n"
                   "# TI SNOSD17G 10.1.1.2.3 (p.17): \"CIN: minimum 22 nF of input capacitance\". DC_F carried the VCAP capacitor C4\n"
                   "# alone, so a discharge at the receptacle's DC pin drove DC_F to D10's clamping voltage, and in the negative\n"
                   "# direction that puts the clamp's 44.4 to 64.5 V plus DC_P's own voltage across Q1 (60 V) and U3 (75 V CATHODE to\n"
                   "# ANODE). 1 uF 100 V X7R 1210, the part of C6 and C7 and of board A's C207 (C382212): the whole charge of the IEC\n"
                   "# 61000-4-2 network moves it 1.2 V at 8 kV and 2.25 V at 15 kV (150 pF), so the clamp is not reached. It returns to\n"
                   "# GND_V, the entry's own return ahead of the choke, as D10 does. v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md.\n"
                   'c("%s", "1u 100V 1210", "DC_F", "GND_V", "C1210", "C382212")\n' % ref, WHAT + " (the part)")
    b = '["J_DCIN", "F1", "U3", "Q1", "C4", "R1", "D1", "C2",'
    t = G.sub_once(t, b, '["J_DCIN", "F1", "U3", "Q1", "C4", "%s", "R1", "D1", "C2",' % ref, WHAT + " (the sheet section)")
    c = '_intent.bypass("C56", "U16", "6", "+5V_E6")'
    t = G.sub_once(t, c, '_intent.bypass("%s", "U3", "6", "DC_F")       # the LM74700-Q1\'s CIN at its ANODE (finding E-F1)\n' % ref + c,
                   WHAT + " (the decoupling declaration)")
    d = "_DEC_CLASS = {\n"
    t = G.sub_once(t, d, d +
                   '    "%s": ("D", "TI LM74700-Q1 SNOSD17G, December 2020 (v2/vendor/ti/ti-lm74700-q1.pdf): 10.1.1.2.3 \\"CIN: minimum 22 nF "\n'
                   '            "of input capacitance\\" (p.17); the controller\'s input capacitor at its ANODE, class D by role; 1 uF is "\n'
                   '            "this generator\'s value, above the maker\'s minimum (the review of decision 31, finding E-F1)"),\n' % ref,
                   WHAT + " (the class)")
    # the calls this edit added are in the syntax tree with the arguments it meant
    caps = G.first_args(t, "c")
    assert caps.get(ref) == [ref, "1u 100V 1210", "DC_F", "GND_V", "C1210", "C382212"], caps.get(ref)
    byp = G.first_args(t, "bypass")
    assert byp.get(ref) == [ref, "U3", "6", "DC_F"], byp.get(ref)
    assert ref in G.string_constants(t) and ref not in G.string_constants(old)
    G.finish(path, old, t, MARK, dry, "%s (%s)" % (WHAT, ref))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
