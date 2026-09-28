#!/usr/bin/env python3
"""Board A, finding A-F2 of the review of decision 31: the maker's network at the LTC2954's PB pin (MESHSAT-1357,
worker d8dec31, 28 September 2026). A PROPOSAL for the owner of gen_sch_a.py in the next circuit round; this stream
commits nothing over the generator, the schematic or the netlist.

THE FINDING. The MAIN button is on the face (board C's SW_MAIN, a C&K ATP19) and its lead, made up at build, runs to
board A's J_MAINSW and from there straight to U1 pin 2: on the set 6 netlist (sha256 0a2b59087bcc2678...) the net
MAIN_PB carries J_MAINSW.1 and U1.2 and nothing else. The maker says what goes there for a button that is not beside
the chip. ADI (Linear Technology) 2954fb (v2/vendor/power/ltc2954.pdf), p.12: "if the pushbutton switch is physically
located far from the LTC2954 PB pin, parasitic capacitances may couple onto the high impedance PB input.
Additionally, parasitic series inductance may cause unpredictable ringing at the PB pin. Placing a 5.1k resistor from
the PB pin to the pushbutton switch would mitigate parasitic inductance problems. Placing a 0.1uF capacitor on the PB
pin would lessen the impact of parasitic capacitive coupling"; p.13, PB Pin in a Noisy Environment: "place an R-C
network close to the PB pin. A 5.1k resistor and a 0.1uF capacitor should suffice for most noisy applications".

WHY IT MATTERS TO DECISION 31. The clamp that serves this conductor is on board C, at the switch (U10, behind FB1,
FB2 and C26). Between that clamp and U1 there is the lead and nothing: what the clamp lets through, and what couples
onto the lead inside the case (it runs past the power stages of this board), arrives at the PB pin, whose own rating
is a human body model figure ("+-10kV ESD HBM on PB Input", 2954fb p.1), not the ruled IEC 61000-4-2 level. The series
resistor is what stands between the clamp and the protected part; the capacitor returns the residue to this board's
ground at the pin.

THE CHANGE. J_MAINSW pin 1 moves to a new net MAIN_PB_LEAD; a 5.1 k resistor joins MAIN_PB_LEAD to MAIN_PB; 100 nF
stands from MAIN_PB to GND at U1 pin 2. Both nets are declared as nodes at 2.0 V, the PB pin's open-circuit maximum
(2954fb p.3, VPB(VOC) 1 to 2 V at -1 uA). With the button pressed the PB pin sits at 5.1 k times its own source
current above the switch: 77 mV at the 15 uA maximum the sheet gives at 0.6 V (p.3), against a falling threshold of
0.6 V minimum. The references are the next free R and C at apply time.

ALSO OWED WITH IT, in v2/ecad/tools/boards/a.json (the integrator's file): the signal class entry whose pattern is
MAIN_PB covers the new net only as MAIN_PB*; this script changes it when given the table's path.

AND THE INTERFACE CONTRACT (the fresh check's item M6): v2/ecad/tools/pcb_interfaces.yaml IF-AC-MAINSW maps board A's
J_MAINSW pin 1 to MAIN_PB and cites gen_sch_a.py:278; after this change pin 1 is on MAIN_PB_LEAD, so the contract goes
stale (judged_by none, so no gate trips). The contract's change is delivered as apply_interfaces_mainsw.py beside this
script, for the integrator, to run AFTER this script has been applied and the generator re-run; it refuses while the
netlist still carries J_MAINSW.1 on MAIN_PB.

NOT CHANGED HERE, and said so: board C's U10 is a rail-referenced array on a line that is live while its rail is off
(finding X-C1 of the review). That is board C's generator and its owner's.

Usage: apply_gen_sch_a_mainpb.py <gen_sch_a.py> <pcb-a-power.net> [<boards/a.json>] [--check]
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genpatch as G

WHAT = "apply_gen_sch_a_mainpb"
MARK = "DECISION 31's REVIEW, FINDING A-F2"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2: print(__doc__); return 2
    path, net, dry = args[0], args[1], "--check" in argv
    table = args[2] if len(args) > 2 else None
    old = open(path, encoding="utf-8").read()
    G.refuse_second_run(old, MARK, WHAT)
    (rref,) = G.next_free("R", net, old)
    (cref,) = G.next_free("C", net, old)
    t = old
    a = ('part("J_MAINSW", "Connector_Generic", "Conn_01x02", "JST-XH 1x2 socket: the MAIN button lead from the panel, PB and GND", '
         '"XH2", {"1": "MAIN_PB", "2": "GND"}, "C158012")\n')
    b = ('part("J_MAINSW", "Connector_Generic", "Conn_01x02", "JST-XH 1x2 socket: the MAIN button lead from the panel, PB and GND", '
         '"XH2", {"1": "MAIN_PB_LEAD", "2": "GND"}, "C158012")\n'
         "# " + MARK + " (28 September 2026, MESHSAT-1357): THE BUTTON IS ON THE FACE AND ITS LEAD RAN STRAIGHT TO THE PB PIN.\n"
         "# ADI 2954fb p.12 and p.13 (v2/vendor/power/ltc2954.pdf): for a pushbutton \"physically located far from the LTC2954 PB\n"
         "# pin\", \"place an R-C network close to the PB pin. A 5.1k resistor and a 0.1uF capacitor should suffice\". The clamp\n"
         "# of this lead is board C's U10 at the switch; the resistor is what stands between that clamp and U1, and the\n"
         "# capacitor returns what is left to this board's ground at the pin. Pressed, the pin sits 77 mV above the switch\n"
         "# (5.1 k at the 15 uA the sheet gives at 0.6 V, p.3) against a 0.6 V threshold. Both at U1 pin 2.\n"
         'r("%s", "5.1k", "MAIN_PB_LEAD", "MAIN_PB"); c("%s", "100n", "MAIN_PB", "GND")\n'
         '_intent.node("MAIN_PB", 2.0, "the LTC2954\'s PB pin behind %s: its own current source holds it at its open-circuit "\n'
         '             "voltage, 1 to 2 V (2954fb p.3, VPB(VOC)), and the button pulls it to ground; no part takes a supply here", v_work=2.0)\n'
         '_intent.node("MAIN_PB_LEAD", 2.0, "the MAIN button\'s lead at J_MAINSW, the switch side of %s: the same 2 V at most", v_work=2.0)\n'
         % (rref, cref, rref, rref))
    t = G.sub_once(t, a, b, WHAT + " (the parts)")
    s = '["U1", "C4", "R2", "R184", "R3", "R4", "C152", "Q1", "R5", "J_MAINSW"]'
    t = G.sub_once(t, s, '["U1", "C4", "R2", "R184", "R3", "R4", "C152", "Q1", "R5", "J_MAINSW", "%s", "%s"]' % (rref, cref),
                   WHAT + " (the sheet section)")
    assert G.first_args(t, "r").get(rref) == [rref, "5.1k", "MAIN_PB_LEAD", "MAIN_PB"], G.first_args(t, "r").get(rref)
    assert G.first_args(t, "c").get(cref) == [cref, "100n", "MAIN_PB", "GND"], G.first_args(t, "c").get(cref)
    nodes = G.first_args(t, "node")
    assert "MAIN_PB" in nodes and "MAIN_PB_LEAD" in nodes and "MAIN_PB_LEAD" not in G.string_constants(old)
    plan = None
    if table:
        told = open(table, encoding="utf-8").read()
        d = json.loads(told)
        assert json.dumps(d, indent=1, ensure_ascii=False) + "\n" == told, "the table is not written the way this script writes it"
        hits = [e for e in d["signal_classes"] if e.get("pattern") == "MAIN_PB"]
        assert len(hits) == 1, "the table's MAIN_PB signal class entry is not there exactly once"
        hits[0]["pattern"] = "MAIN_PB*"
        hits[0]["basis"] = hits[0]["basis"] + "; and its lead from the panel, MAIN_PB_LEAD, the switch side of %s" % rref
        tnew = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
        assert tnew != told and json.loads(tnew)["signal_classes"] == d["signal_classes"]
        plan = (table, tnew)
    G.finish(path, old, t, MARK, dry, "%s (%s, %s)" % (WHAT, rref, cref))
    if plan:
        if not dry:
            with open(plan[0], "w", encoding="utf-8") as f: f.write(plan[1])
            json.load(open(plan[0], encoding="utf-8"))
        print("%s: %s, the MAIN_PB signal class now covers MAIN_PB_LEAD%s" % (WHAT, os.path.basename(plan[0]), " (checked, not written)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
