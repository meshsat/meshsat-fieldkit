#!/usr/bin/env python3
"""The interface contract IF-AC-MAINSW after finding A-F2's change (MESHSAT-1357, worker d8dec31, 28 September 2026;
the fresh check's item M6). The integrator runs it on v2/ecad/tools/pcb_interfaces.yaml, its file, AFTER
apply_gen_sch_a_mainpb.py has been applied and board A's generator re-run on the KiCad host.

apply_gen_sch_a_mainpb.py moves board A's J_MAINSW pin 1 from MAIN_PB to the new net MAIN_PB_LEAD (the 5.1 k resistor
of ADI 2954fb p.12 and p.13 then joins MAIN_PB_LEAD to MAIN_PB at U1's PB pin). IF-AC-MAINSW maps board A's pin 1 to
MAIN_PB and cites gen_sch_a.py:278; without this change the contract describes a net the lead no longer lands on.

It REFUSES while board A's declared-phase netlist in the tree still carries J_MAINSW.1 on MAIN_PB (the contract is
changed only once the circuit has), asserts the old line once, asserts the new text differs, re-parses the file and
checks the end it changed, and refuses a second run. The `src` line number is left as the generator owner's to correct
after the re-run (the script cannot know where the line lands); the note says so.

Usage: apply_interfaces_mainsw.py <tree root> [--check] [--force-netlist]     --force-netlist skips the netlist check
"""
import os, re, sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netread

OLD = '''        - {board: a, ref: J_MAINSW, pins: {1: MAIN_PB, 2: GND}, src: "v2/ecad/tools/gen_sch_a.py:278"}
'''
NEW = '''        - {board: a, ref: J_MAINSW, pins: {1: MAIN_PB_LEAD, 2: GND}, src: "v2/ecad/tools/gen_sch_a.py:278 (the line of the
            J_MAINSW connector; since finding A-F2 of the review of decision 31 pin 1 lands on MAIN_PB_LEAD and reaches
            U1's PB pin MAIN_PB through a 5.1 k resistor, with 100 nF at the pin: v2/docs/records/d8dec31/apply_gen_sch_a_mainpb.py)"}
'''
NETLIST = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry, force = os.path.abspath(argv[0]), "--check" in argv, "--force-netlist" in argv
    p = os.path.join(root, "v2", "ecad", "tools", "pcb_interfaces.yaml")
    old = open(p, encoding="utf-8").read()
    if "pins: {1: MAIN_PB_LEAD, 2: GND}" in old:
        raise SystemExit("apply_interfaces_mainsw: already applied")
    assert old.count(OLD) == 1, "IF-AC-MAINSW's board A end is not the line this script expects"
    if not force:
        comps, _nets = netread.read(os.path.join(root, NETLIST))
        on = comps.get("J_MAINSW", {}).get("pins", {}).get("1")
        if on != "MAIN_PB_LEAD":
            raise SystemExit("apply_interfaces_mainsw: board A's netlist has J_MAINSW.1 on %s, not MAIN_PB_LEAD: apply "
                             "apply_gen_sch_a_mainpb.py and re-run the generator first (or --force-netlist to write the "
                             "contract ahead of the circuit, which makes the contract wrong until then)" % on)
    new = old.replace(OLD, NEW)
    assert new != old
    d = yaml.safe_load(new)
    ends = d["board_to_board"]["contracts"]["IF-AC-MAINSW"]["ends"]
    a = [e for e in ends if e.get("board") == "a"][0]
    assert a["pins"] == {1: "MAIN_PB_LEAD", 2: "GND"}, a
    d_old = yaml.safe_load(old)
    assert d_old["board_to_board"]["contracts"].keys() == d["board_to_board"]["contracts"].keys()
    assert {k: v for k, v in d_old["board_to_board"]["contracts"].items() if k != "IF-AC-MAINSW"} == \
           {k: v for k, v in d["board_to_board"]["contracts"].items() if k != "IF-AC-MAINSW"}, "another contract moved"
    if not dry:
        with open(p, "w", encoding="utf-8") as f: f.write(new)
        yaml.safe_load(open(p, encoding="utf-8"))
    print("apply_interfaces_mainsw: IF-AC-MAINSW board A pin 1 MAIN_PB -> MAIN_PB_LEAD%s" % (" (checked, not written)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
