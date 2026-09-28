#!/usr/bin/env python3
"""Board E, finding E-F3 of the review of decision 31: the outside pod's 3.3 V conductor (MESHSAT-1357, worker
d8dec31, 28 September 2026). A PROPOSAL for the owner of gen_sch_e.py in the next circuit round; this stream commits
nothing over the generator, the schematic or the netlist.

THE FINDING. J_POD pin 1 is the rail +3V3_E6 itself, out of the case on the pod's lead, with no part between the pin
and the rail. What clamps it is D9's VBUS element, which breaks down at 6 V at the least (ST DS4260 Rev 7, Table 2,
p.2: VBR 6 V minimum between VBUS and GND), above the absolute maximum supply of every part on the rail: SGP41 VDDH
3.6 V (Sensirion, version 1.0, p.7), RP2040 IOVDD 3.63 V (Raspberry Pi, 5.5.3.1), BMI270 4 V (Bosch, rev 1.6, p.16),
BME688 4.25 V (Bosch, rev 1.3, p.15). So the clamp protects none of them, and what bounds the rail in a discharge is
its own capacitance: 4.3 uF on the set 6 netlist (sha256 56adc9746d61c4e0..., sixteen capacitors). THE BOUND, which is
a conservative model's answer and is labelled so: every coulomb of the IEC 61000-4-2 network on the rail and none into
its loads, 1.2 uC at 8 kV and 2.25 uC at 15 kV (150 pF), lifts 4.3 uF by 0.28 V and 0.52 V: from the regulator's
3.333 V maximum (TI SBVS320D p.1, output accuracy 1 percent) to 3.61 V and 3.86 V, above the SGP41's 3.6 V at both
levels and above the RP2040's 3.63 V at the air level.

THE CHANGE. Two capacitors of 10 uF 25 V 1210, the part of C1 and C31 on this board, from +3V3_E6 to GND AT THE HEADER
J_POD. With 24.3 uF the same bound is 0.05 V and 0.09 V: 3.38 V and 3.43 V. The regulator allows it (SBVS320D p.15:
0.47 uF or larger, "a maximum output capacitance value of 200uF"). The references are the next free C at apply time.

WHAT IT DOES NOT SETTLE, and the review says so: nothing limits the current into the outside lead, so a short of the
lead's 3.3 V conductor to its return takes the sensor controller's rail with it (finding E-F4). A series element
there is sized by the pod's supply current, and the pod's part is not picked (interface contract IF-E-POD).

Usage: apply_gen_sch_e_pod.py <gen_sch_e.py> <pcb-e1-dock.net> [--check]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genpatch as G

WHAT = "apply_gen_sch_e_pod"
MARK = "DECISION 31's REVIEW, FINDING E-F3"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2: print(__doc__); return 2
    path, net, dry = args[0], args[1], "--check" in argv
    old = open(path, encoding="utf-8").read()
    G.refuse_second_run(old, MARK, WHAT)
    c1, c2 = G.next_free("C", net, old, 2)
    t = old
    a = 'kisch.esd("D9", "SDA1", "SCL1", "+3V3_E6")\n'
    t = G.sub_once(t, a, a +
                   "# " + MARK + " (28 September 2026, MESHSAT-1357): THE POD'S 3.3 V CONDUCTOR IS THE RAIL ITSELF, AND D9 CLAMPS IT AT\n"
                   "# 6 V OR MORE (ST DS4260 Rev 7, Table 2), above the absolute maximum supply of every part on the rail (SGP41 3.6 V,\n"
                   "# RP2040 3.63 V, BMI270 4 V, BME688 4.25 V). What bounds the rail in a discharge is its capacitance, and 4.3 uF lets\n"
                   "# the whole charge of the IEC 61000-4-2 network lift it 0.28 V at 8 kV and 0.52 V at 15 kV (a conservative bound:\n"
                   "# nothing into the loads). Two 10 uF 25 V 1210, the part of C1 and C31, AT THE HEADER J_POD: 0.05 V and 0.09 V.\n"
                   "# TI SBVS320D p.15 allows up to 200 uF on the regulator. v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md.\n"
                   'c("%s", "10u 25V 1210", "+3V3_E6", "GND", "C1210"); c("%s", "10u 25V 1210", "+3V3_E6", "GND", "C1210")\n' % (c1, c2),
                   WHAT + " (the parts)")
    s = '"R43", "D9", "J_FAN1",'
    t = G.sub_once(t, s, '"R43", "D9", "%s", "%s", "J_FAN1",' % (c1, c2), WHAT + " (the sheet section)")
    caps = G.first_args(t, "c")
    for ref in (c1, c2):
        assert caps.get(ref) == [ref, "10u 25V 1210", "+3V3_E6", "GND", "C1210"], caps.get(ref)
    G.finish(path, old, t, MARK, dry, "%s (%s, %s)" % (WHAT, c1, c2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
