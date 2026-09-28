#!/usr/bin/env python3
"""The eight registry records bound to board A's netlist (four also to gen_sch_a.py), rebound after S-99's circuit change
(MESHSAT-1357, integration set 9, 29 September 2026). apply_rebind_after_circuit.py computes the change from the parsed
netlists (ten parts added: U41, L13, C227 to C232, R217, R218; U23's input moved from +5V_DEV to +5V_D8IN with C103 and
R100; the printed current limits of U32/R186 and U39/R209 re-read by TPS2596 equation 7's true sign, same parts and
values; U41's pins on VBAT, RAIL_EN and GND) and refuses every record that names a changed part or net unless a reason
is given. Each reason below was written after reading the record's statement, acceptance and evidence against that
change. U41's pin functions are TI's (SLUSEA4D Table 7-1: pin 2 EN, pin 3 VIN, pin 4 GND), not the netlist's pin
names, which the generator sets equal to the nets. Run from the repository root after the re-take: python3 <this file>."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
H2 = ("U39 and R209 appear only in an earlier rebind entry that lists the H2 differences; both are the same parts with the "
      "same values, and only the generator's printed limit for R209 moved from 0.18 to 0.20 A by TPS2596 equation 7's true "
      "sign (SLVSET8A printed page 28)")
WHY = {
    "CON-019": "its subject is the PA-keyed interlock on the PoE and USB-C outlets; no part of that path and none of its nets "
               "changed; " + H2,
    "CON-018": "its subject is the ESD array on board A's USB-C CC pins by the connector, which the change does not touch; " + H2,
    "CFL-005": "its subject is the pull direction of EMCON_HW and SLOT_EN1 to SLOT_EN3 on a panel-less kit; neither net "
               "changed; " + H2,
    "CON-010": "its subject is the PA's VGG gate and board D's KEY logic; no part of that path and none of its nets changed "
               "(the added parts sit on VBAT, RAIL_EN, GND and the new nets D8B_BST, D8B_FB, D8B_SS, D8B_SW and +5V_D8IN); " + H2,
    "REQ-077": "its shed path names RAIL_EN on U12's EN; the new buck U41 has its EN (TPS62933 pin 2) on RAIL_EN too, so the "
               "D8 rail now falls with the same kill as U12 and the path the record states is unchanged; the panel controller "
               "still takes +5V_DEV through board B's F1; the added GND and VBAT nodes are U41's return and input",
    "CFL-016": "its subject is the published contracts against faf8c981, 458b2873 and d90f30e4, none of which is this change; "
               "VBAT is named only in a netlist diff of an earlier change; " + H2,
    "CFL-014": "its one sentence on VBAT says the loads on VBAT are the charger's system side with the pack beyond the shunt; "
               "that still holds, since U41 takes VBAT at its VIN (TPS62933 pin 3) on the system side of R17 and is enabled "
               "by RAIL_EN; " + H2,
    "CON-016": "its subject is the orientation of clamps and rectifiers; the ten added parts include no diode, clamp or "
               "rectifier; " + H2,
}


def main():
    args = [sys.executable, os.path.join(HERE, "apply_rebind_after_circuit.py"), "a",
            "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "--gen", "v2/ecad/tools/gen_sch_a.py"]
    args += ["%s=%s" % (k, v) for k, v in WHY.items()]
    return subprocess.run(args).returncode


if __name__ == "__main__":
    sys.exit(main())
