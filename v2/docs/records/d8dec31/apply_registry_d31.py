#!/usr/bin/env python3
"""The open items of the review of decision 31, into the requirements registry (MESHSAT-1357, worker d8dec31, 28
September 2026). The integrator runs it on v2/ecad/tools/pcb_requirements.yaml, its file.

It appends the items below to `open_items`, each at the next free S- number at apply time (read by the same regex the
earlier registry scripts of this programme use), class SESSION, status OPEN, in the registry's own shape; it asserts
the review is in the tree, asserts the new text differs, re-parses the file, checks the ids it took are there once
each, and refuses a second run by a marker. It writes the ids it took beside itself as ids-registry.json.

The items (the finding ids are the review's, v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md):
  A-F2   board A: the maker's network at the LTC2954's PB pin (apply_gen_sch_a_mainpb.py)
  X-C1   board C: the MAIN button's clamp refers to a rail that is off while the button is live
  D-F1   board D: the push-to-talk clamp does not clamp below the gate behind it (apply_gen_sch_d_ptt.py)
  D-F2   board D: the speaker conductors, not judged at the desk
  D-F3   board D: the touch lead J_USB3 carries no clamp and none of the hub maker's port parts
  D-F4   board D: C41 and C42 carry no voltage in their value text on a conductor whose clamp reaches 37 V
  E-F1   board E: the ideal diode controller's input capacitor (apply_gen_sch_e_cin.py)
  E-F2   board E: F1 is rated 32 V DC on a line specified to 36 V
  E-F3   board E: the pod's 3.3 V conductor, by a bound (apply_gen_sch_e_pod.py)
  E-F4   board E: the pod's lead has no series element and shares the bus with four parts inside
  D-N1   the arrestor's turn-on against the antenna conductor's transmit peak: a question for the maker
  A-N1 and E-N2   the clamps' rated pulse against U2's and U3's ratings: for R-PWR
  T-2    boards B and C read INCONCLUSIVE under the changed tool until their tables name their internal connectors
  T-3    an off_board entry is believed on its text

Usage: apply_registry_d31.py <tree root> [--check]
"""
import json, os, re, sys

import yaml

MARK = "the review of decision 31 (stream d8dec31, 28 September 2026)"
REVIEW = "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"

ITEMS = [
    ("A-F2", "Board A: the MAIN button's lead runs from the face to the LTC2954's PB pin with nothing on this board "
             "(the net is J_MAINSW.1 and U1.2). ADI 2954fb p.12 and p.13 ask for 5.1 k and 0.1 uF at the pin for a button "
             "far from the chip; the lead's clamp is board C's U10 at the switch. Finding A-F2 of %s, section 4.3; the "
             "change is v2/docs/records/d8dec31/apply_gen_sch_a_mainpb.py, for board A's generator owner in the next "
             "circuit round. Closed by the parts on board A's netlist and a re-review on it."),
    ("X-C1", "Board C: U10 (USBLC6-2SC6), the clamp of the MAIN button's pair, has its rail pin on board C's +3V3, "
             "which is off while the kit is off and the PB conductor is live at 1 to 2 V from a source of 1 to 15 uA "
             "(2954fb p.3). If the array's upper diode holds under the PB threshold (0.6 to 1.0 V) at those currents, "
             "the LTC2954 reads a pressed button while the kit is off. Not judged at the desk: ST gives the forward "
             "voltage at 10 mA only (DS4260 Table 2). Finding X-C1 of %s, section 4.4; the same question stands for "
             "U11 on the PI button's pair. For board C's owner: the array's characteristic at microamps from ST, or a "
             "bench measurement, or a clamp that refers to no rail (a substitution to prove)."),
    ("D-F1", "Board D: the push-to-talk clamps D11 and D14 (PESD5V0S1BA, VBR 5.5 to 9.5 V, VCL 10 to 14 V) stand on "
             "the same net as U9's inputs (74LVC1G08GV, -0.5 to 6.5 V, IIK -50 mA) and Q4, Q5's sources with nothing in "
             "series: positive, the clamp does not clamp below the gate's rating and C49, C50 hold what it left for a "
             "millisecond; negative, the gate's own input conducts first. Finding D-F1 of %s, section 5.3; the change is "
             "v2/docs/records/d8dec31/apply_gen_sch_d_ptt.py (1 k and two BAT46W per line), for board D's generator "
             "owner. Closed by the parts on board D's netlist and a re-review on it."),
    ("D-F2", "Board D: the speaker clamps D9 and D12 stand on U7's outputs (TPA6132A2) with nothing in series; the "
             "amplifier's output conducts from about 2.5 V, before the clamp's 5.5 V, and TI gives the outputs a human "
             "body model figure only (SLOS597B p.4). Not judged at the desk. Finding D-F2 of %s, section 5.3. Decided "
             "by TI's IEC 61000-4-2 figure for these outputs or by test M7; removed by a series element between the "
             "jack's clamp and the output, sized by the headset's impedance, which is board D's owner's."),
    ("D-F3", "Board D: J_USB3 is the touch lead of the monitor on the face (SC-HF-06) and carries no clamp on its pair "
             "and none of the port parts its hub's maker asks for (TI SLLS413L p.17: 22 uF on the port's VBUS, a bead "
             "with 100 nF on the connector side). Not judged at the desk, the lead staying inside the case. Finding "
             "D-F3 of %s, section 5.3. Removed by the USBLC6-2SC6 the set already buys at the header and the maker's two "
             "port parts, for board D's owner, with HF-F06's port limit."),
    ("D-F4", "Board D: C41 and C42 (value '1u', no code) stand on the microphone conductors behind D10 and D13, whose "
             "clamp reaches 37 V at 5 A and whose breakdown is 16.7 V at most, and their value text states no voltage. "
             "Finding D-F4 of %s, section 5.3. Closed by a value text naming 50 V or more, so the bill carries it."),
    ("E-F1", "Board E: U3 (LM74700-Q1) has no input capacitor; TI SNOSD17G 10.1.1.2.3 (p.17) requires 22 nF at the "
             "least, and DC_F carries only the VCAP capacitor C4. With none, a negative discharge at the receptacle "
             "drives DC_F to D10's clamping voltage and puts that plus DC_P's voltage across Q1 (60 V) and U3 (75 V), "
             "TI's own criterion (10.1.1.3, p.18). Finding E-F1 of %s, section 6.3; the change is "
             "v2/docs/records/d8dec31/apply_gen_sch_e_cin.py (1 uF 100 V, the part of C6, C7 and board A's C207), for "
             "board E's generator owner. Closed by the part on board E's netlist and a re-review on it."),
    ("E-F2", "Board E: F1 is a MINI blade of the class the Keystone 3568 holder takes, and the series the record holds "
             "(Littelfuse 297) is rated 32 V DC with an interrupting rating of 1000 A at 32 V DC, on a line specified to "
             "36 V whose hot swap admits 40 V. Finding E-F2 of %s, section 6.3. Closed by a fuse of the same form rated "
             "above 40 V, with its maker's sheet filed: the 58 V MINI series is the candidate and its sheet is not held "
             "(littelfuse.com answered 403; the Internet Archive held no copy at the addresses tried on 27 September "
             "2026); that its series number is 997 is INFERRED. For board E's owner and R-PWR."),
    ("E-F3", "Board E: J_POD.1 is the rail +3V3_E6 out of the case; D9's VBUS element breaks down at 6 V at the least, "
             "above the absolute maximum supply of every part on the rail (SGP41 3.6 V, RP2040 3.63 V, BMI270 4 V, "
             "BME688 4.25 V), and the rail's 4.3 uF lets the whole charge of the IEC 61000-4-2 network lift it to 3.61 V "
             "at 8 kV and 3.86 V at 15 kV from the regulator's 3.333 V maximum (a conservative bound: nothing into the "
             "loads). Finding E-F3 of %s, section 6.3; the change is v2/docs/records/d8dec31/apply_gen_sch_e_pod.py "
             "(two 10 uF 25 V at the header), for board E's generator owner. Closed by the parts on board E's netlist "
             "and a re-review on it, or by a measurement under test M7 that reads the rail under the ratings."),
    ("E-F4", "Board E: the pod's lead has no series element, so a short of its 3.3 V conductor outside takes the sensor "
             "controller's rail and the hot stop line with it, and SDA1 and SCL1 run from the pod's pins to five parts "
             "inside with D9 on them and nothing in series. Not judged at the desk. Finding E-F4 of %s, section 6.3. "
             "Options: series resistors between D9 and the bus inside, or the pod on a bus of its own; a series element "
             "on the feed, sized by the pod's supply current, which waits for the pod's part (IF-E-POD). For board E's "
             "owner."),
    ("D-N1", "The antenna bulkheads' arrestor (PolyPhaser GTH-SFF-AL) is rated for surge (10 kA, no waveform stated) "
             "with a 90 V turn-on and a 60 V DC operating maximum, and its sheet states no IEC 61000-4-2 figure and no "
             "let-through; the VHF conductor's transmit peak with the wave wholly reflected is the intent's own 110 V. "
             "Eleven antenna conductors of board A and board D's antenna path are therefore not judged at the desk "
             "(%s, sections 4.5 and 5.3). The question for the maker is prepared in section 9.3 and not sent; sending "
             "it is the owner's. Decided by the maker's answer, by each radio's antenna-port rating, or by test M7."),
    ("A-N1", "For R-PWR: at their rated pulse the VIN_RAW clamps (SMCJ40A, 64.5 V at 23.3 A) carry board A's front-end "
             "controller U2 (LM5176, VIN and VISNS rated 60 V) outside its rating, and board E's D10 carries U3's ANODE "
             "(65 V) to within 0.5 V; no surge level is ruled (D-16), so nothing fails, and the coordination of board E's "
             "hot swap (stops above 40 V) with the four SMCJ40 parts between the receptacle and U2 is the qualified "
             "power review's to compute. Notes A-N1 and E-N2 of %s, sections 4.3 and 6.3."),
    ("T-2", "With port_protect.py's change of stream d8dec31 (a connector pin carrying a supply or a signal that no "
            "entry of the declaration covers makes TRN-001 INCONCLUSIVE), boards B and C read INCONCLUSIVE until their "
            "tables carry `internal_ports` naming where each internal lead goes: 290 connector pins on board B and 39 "
            "on board C in the scratch reading (%s, section 10). For the owners of boards/b.json and boards/c.json; the "
            "shape is boards/a.json, d.json and e.json after apply_port_declarations.py."),
    ("T-3", "port_protect.py believes an `off_board` entry on its text: it cannot ask what the part named in the wall "
            "is rated for, so an arrestor rated for surge answers a rule about electrostatic discharge. A declaration "
            "form that names the part, its document and the level it is rated to, read by the tool, is owed (%s, "
            "section 10, T-3). For the tools stream."),
]


def wrap(text, indent=6, width=118):
    words, lines, cur = text.split(), [], " " * indent
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip(): lines.append(cur); cur = " " * indent + w
        else: cur = (cur + " " + w) if cur.strip() else cur + w
    lines.append(cur)
    return "\n".join(lines) + "\n"


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry = os.path.abspath(argv[0]), "--check" in argv
    reg = os.path.join(root, "v2", "ecad", "tools", "pcb_requirements.yaml")
    if not os.path.exists(os.path.join(root, REVIEW)):
        raise SystemExit("apply_registry_d31: %s is not in the tree" % REVIEW)
    old = open(reg, encoding="utf-8").read()
    if MARK in old:
        raise SystemExit("apply_registry_d31: already applied (its marker is in the file)")
    d0 = yaml.safe_load(old)
    top = max(int(m) for m in re.findall(r"\n  - id: S-(\d+)\n", old))
    ids = ["S-%d" % (top + 1 + k) for k in range(len(ITEMS))]
    assert not any(x.get("id") in ids for x in d0["open_items"] + d0["closed_items"])
    block = ""
    for sid, (fid, title) in zip(ids, ITEMS):
        block += "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n" % sid + wrap(
            "%s: " % fid + (title % MARK) + " (finding %s)" % fid if fid not in title else "%s: " % fid + (title % MARK))
    head = "\n# Items that left the open list, and what closed each"
    assert old.count(head) == 1, "the open list's end is not where this script expects it"
    t = old.replace(head, block.rstrip("\n") + "\n" + head)
    assert t != old
    d1 = yaml.safe_load(t)
    got = {x["id"]: x for x in d1["open_items"]}
    for sid in ids:
        assert sid in got and got[sid]["status"] == "OPEN" and got[sid]["class"] == "SESSION", sid
        assert sum(1 for x in d1["open_items"] if x["id"] == sid) == 1
    assert len(d1["open_items"]) == len(d0["open_items"]) + len(ITEMS)
    assert d1["closed_items"] == d0["closed_items"] and d1["records"] == d0["records"]
    if not dry:
        with open(reg, "w", encoding="utf-8") as f: f.write(t)
        yaml.safe_load(open(reg, encoding="utf-8"))
        json.dump({fid: sid for sid, (fid, _t) in zip(ids, ITEMS)},
                  open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ids-registry.json"), "w"), indent=1)
    print("apply_registry_d31: %d open items, %s to %s%s" % (len(ITEMS), ids[0], ids[-1], " (checked, not written)" if dry else ""))
    for sid, (fid, _t) in zip(ids, ITEMS): print("   %s  %s" % (sid, fid))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
