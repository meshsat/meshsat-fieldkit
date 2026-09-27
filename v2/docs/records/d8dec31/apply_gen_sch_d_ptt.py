#!/usr/bin/env python3
"""Board D, finding D-F1 of the review of decision 31: the two push-to-talk conductors (MESHSAT-1357, worker d8dec31,
28 September 2026). A PROPOSAL for the owner of gen_sch_d.py in the next circuit round; this stream commits nothing
over the generator, the schematic or the netlist.

THE FINDING. On the set 6 netlist (sha256 7a2c0ac2190b141a...) each push-to-talk conductor is ONE net from the jack to
the logic: PTT_HS1_n carries J_HS1.5, the clamp D11, C49 (100 nF), the pull-up R68, U9 pin 1 and Q4's source. Rule
TRN-001 asks that the protection "clamps below the protected part's absolute maximum". It does not, in either
direction, and nothing stands between the clamp and the parts:
  positive  D11 is a PESD5V0S1BA: VBR 5.5 to 9.5 V at 1 mA, VCL 10 V at 1 A and 14 V at 12 A (Nexperia, 26 April 2024,
            Table 6, p.4). U9 is a TECH PUBLIC 74LVC1G08GV: input voltage -0.5 to 6.5 V (its sheet, p.2, read from a
            render: the file has no text layer). The clamp conducts from a voltage that may itself be above the input's
            rating, and C49 holds what the discharge left on it until R68 has taken it away, a millisecond (10 k, 100 nF).
  negative  U9's input clamp conducts from -0.5 V and is rated -50 mA (the same page, IIK); D11 conducts from -5.5 V
            at the earliest. So in a negative discharge the first part to conduct is the gate's own input, with no
            resistance in front of it, and the clamp at the jack is not reached until that input has dropped five volts.

THE CHANGE, per conductor: the jack side (the jack's pin, the clamp and the 100 nF) becomes its own net PTT_HSn_LEAD;
a 1 k resistor joins it to PTT_HSn_n, the logic side (the pull-up, U9 and the level stage, unchanged); and two BAT46W
hold the logic side between this board's ground and its +3V3_D8: cathode on +3V3_D8 and anode on the line, and
cathode on the line and anode on GND (Diodes DS30044 Rev. 20-2, v2/vendor/diodes/diodes-bat46w.pdf; C83152, the part
board A buys seventeen of). With the clamp at its 14 V the resistor passes 10 mA into the rail or 13.5 mA out of
ground, the line stays within a Schottky drop of the rails, and the gate's input stays inside -0.5 to 6.5 V. Pressed,
the line reads 0.30 V (1 k under the 10 k pull-up to 3.3 V), below the gate's low threshold. Six parts, no part number
new to the set; the references are the next free R and D at apply time.

WHAT IT DOES NOT SETTLE: the speaker conductors (finding D-F2, U7's outputs with nothing in series) and the touch
lead J_USB3 (finding D-F3) are recorded in the review as not judged at the desk, with their options.

Usage: apply_gen_sch_d_ptt.py <gen_sch_d.py> <pcb-d-aprs.net> [--check]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genpatch as G

WHAT = "apply_gen_sch_d_ptt"
MARK = "DECISION 31's REVIEW, FINDING D-F1"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2: print(__doc__); return 2
    path, net, dry = args[0], args[1], "--check" in argv
    old = open(path, encoding="utf-8").read()
    G.refuse_second_run(old, MARK, WHAT)
    r1, r2 = G.next_free("R", net, old, 2)
    d1, d2, d3, d4 = G.next_free("D", net, old, 4)
    t = old
    for hs in ("1", "2"):
        t = G.sub_once(t, '"3": "HS%s_MIC", "4": "GND", "5": "PTT_HS%s_n"}, "C157993")' % (hs, hs),
                       '"3": "HS%s_MIC", "4": "GND", "5": "PTT_HS%s_LEAD"}, "C157993")' % (hs, hs), WHAT + " (jack %s)" % hs)
    t = G.sub_once(t, 'c("C49", "100n", "PTT_HS1_n", "GND"); c("C50", "100n", "PTT_HS2_n", "GND")',
                   'c("C49", "100n", "PTT_HS1_LEAD", "GND"); c("C50", "100n", "PTT_HS2_LEAD", "GND")', WHAT + " (C49, C50)")
    t = G.sub_once(t, 'headset 1 push to talk", "SOD323", {"1": "GND", "2": "PTT_HS1_n"}, "C19224")',
                   'headset 1 push to talk", "SOD323", {"1": "GND", "2": "PTT_HS1_LEAD"}, "C19224")', WHAT + " (D11)")
    a = 'headset 2 push to talk", "SOD323", {"1": "GND", "2": "PTT_HS2_n"}, "C19224")\n'
    b = ('headset 2 push to talk", "SOD323", {"1": "GND", "2": "PTT_HS2_LEAD"}, "C19224")\n'
         "# " + MARK + " (28 September 2026, MESHSAT-1357): THE PUSH-TO-TALK CLAMP DID NOT CLAMP BELOW THE GATE BEHIND IT.\n"
         "# The PESD5V0S1BA breaks down between 5.5 and 9.5 V and clamps at 10 to 14 V (Nexperia, 26 April 2024, Table 6); U9's\n"
         "# input is rated -0.5 to 6.5 V and its input clamp -50 mA (TECH PUBLIC 74LVC1G08, p.2), and the jack, the clamp, the\n"
         "# 100 nF and the gate were one net. In a negative discharge the gate's own input conducted first, from -0.5 V, with\n"
         "# nothing in front of it. Now the jack side is PTT_HSn_LEAD (the jack, the clamp, the 100 nF); 1 k joins it to the\n"
         "# logic side PTT_HSn_n; and two BAT46W hold the logic side within a Schottky drop of GND and +3V3_D8 (D_Schottky:\n"
         "# pin 1 K, pin 2 A). At the clamp's 14 V the resistor passes 10 mA into the rail or 13.5 mA out of ground. Pressed,\n"
         "# the line reads 0.30 V. v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md.\n"
         'r("%s", "1k", "PTT_HS1_LEAD", "PTT_HS1_n", lcsc="C21190"); r("%s", "1k", "PTT_HS2_LEAD", "PTT_HS2_n", lcsc="C21190")\n'
         'part("%s", "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (push to talk 1, line to +3V3_D8)", "SOD123", {"1": "+3V3_D8", "2": "PTT_HS1_n"}, "C83152")\n'
         'part("%s", "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (push to talk 1, GND to line)", "SOD123", {"1": "PTT_HS1_n", "2": "GND"}, "C83152")\n'
         'part("%s", "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (push to talk 2, line to +3V3_D8)", "SOD123", {"1": "+3V3_D8", "2": "PTT_HS2_n"}, "C83152")\n'
         'part("%s", "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (push to talk 2, GND to line)", "SOD123", {"1": "PTT_HS2_n", "2": "GND"}, "C83152")\n'
         'for _hs in ("1", "2"):\n'
         '    _intent.node("PTT_HS%%s_LEAD" %% _hs, 3.333, "headset %%s\'s push-to-talk lead at the jack, the jack side of its 1 k: it idles at "\n'
         '                 "+3V3_D8 through the 1 k and the level stage\'s 10 k, 3.333 V at most, and the headset\'s switch pulls it to ground; "\n'
         '                 "the clamp and the 100 nF stand on it and no part takes a supply here" %% _hs, v_work=3.333)\n'
         % (r1, r2, d1, d2, d3, d4))
    t = G.sub_once(t, a, b, WHAT + " (D14 and the new parts)")
    rs, ps = G.first_args(t, "r"), G.first_args(t, "part")
    assert rs.get(r1) == [r1, "1k", "PTT_HS1_LEAD", "PTT_HS1_n"] and rs.get(r2) == [r2, "1k", "PTT_HS2_LEAD", "PTT_HS2_n"], (rs.get(r1), rs.get(r2))
    for d in (d1, d2, d3, d4):
        assert ps.get(d) and ps[d][:3] == [d, "Device", "D_Schottky"] and ps[d][4] == "SOD123" and ps[d][-1] == "C83152", ps.get(d)
    # the logic side keeps its name where the gate and the level stage read it, and the jack side has left it
    assert t.count('"PTT_HS1_n"') == old.count('"PTT_HS1_n"') - 3 + 3 and t.count('"PTT_HS1_LEAD"') == 4, (t.count('"PTT_HS1_n"'), t.count('"PTT_HS1_LEAD"'))
    assert t.count('"PTT_HS2_n"') == old.count('"PTT_HS2_n"') - 3 + 3 and t.count('"PTT_HS2_LEAD"') == 4
    G.finish(path, old, t, MARK, dry, "%s (%s, %s, %s to %s)" % (WHAT, r1, r2, d1, d4))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
