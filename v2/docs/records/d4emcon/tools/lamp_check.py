#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): the hardware EMCON lamp of SD-EMC-6 (CON-021) read back on board C's committed
netlist, with its supply traced onto board B. It PARSES the netlists (tx_inhibit.parse_netlist, the RF-002 instrument's
own reader) and classifies each part with the instrument's own firmware classes (tx_inhibit.software_io and FW_MENTION),
so that the claim "no processor in the lamp's path" is a reading, not a recollection.

What it checks, each an assertion that prints PASS or FAIL with the nodes it read:
  L-1  every net of the lamp's signal path (TX_INHIBIT_n, EMCON_HW, EMCLAMP_Y, EMCLAMP_G, EMCLAMP_K, EMCLAMP_A,
       LED_RAIL_SW) carries no pin of a part whose pins firmware sets;
  L-2  U14 is wired as the NOR its row reads (SN74LVC1G57, SCES414P Figure 7: In1 on GND, In0 and In2 the two lines,
       VCC on +3V3), so its output is high only while both lines read LOW at board C;
  L-3  D22's cathode is sunk by Q7's drain alone and its anode is fed through R47 from LED_RAIL_SW alone, so nothing but
       Q7, whose gate is U14's output through R48 with R49 to GND, can light it;
  L-4  the lamp's supplies need no processor: LED_RAIL_SW is +5V through the LIGHTING toggle; U14's +3V3 comes from the
       LDO U5 whose EN is on its own input; board C's +5V arrives on J_PANEL pins 1 and 2 from board B's PANEL_5V,
       which is +5V_DEV through the polyfuse F1 and nothing that firmware switches;
  L-5  the firmware-set pins one resistor away from the path, listed with the resistor, so their worst effect can be
       stated (they are not on the path).
It writes only the file named by --out (never under v2/ecad). Nothing here is a verdict of the tree.

usage: lamp_check.py --tools <v2/ecad/tools> --ecad <v2/ecad> --out <file.txt>"""
import hashlib, os, sys

NETS = {"C": "pcb-c-display-c8/out/pcb-c-display.net", "B": "pcb-b-compute-b19/out/pcb-b-compute.net"}
PATH_NETS = ["TX_INHIBIT_n", "EMCON_HW", "EMCLAMP_Y", "EMCLAMP_G", "EMCLAMP_K", "EMCLAMP_A", "LED_RAIL_SW"]


def main(argv):
    a = dict(zip(argv[0::2], argv[1::2]))
    tools, ecad, out = a.get("--tools"), a.get("--ecad"), a.get("--out")
    if not (tools and ecad and out):
        print(__doc__); return 2
    if "/v2/ecad/" in os.path.abspath(out) + "/":
        print("refused: --out lies under v2/ecad"); return 2
    sys.path.insert(0, os.path.abspath(tools)); sys.dont_write_bytecode = True
    import tx_inhibit as tx
    nl, sha = {}, {}
    for k, p in NETS.items():
        f = os.path.join(ecad, p)
        nl[k] = tx.parse_netlist(f)
        sha[k] = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
    C, B = nl["C"], nl["B"]
    L, fails = [], []

    def val(n, r):
        return (n["comps"].get(r, {}).get("value") or "")

    def fw(n, r):
        # a connector or a test point is no part whose pins firmware sets: the instrument handles connectors by their
        # reference first, and the far side of each ribbon is read on its own board here (J_PANEL's value on board B
        # names the RP2040 whose USB it carries, which is on board C)
        if r.startswith("J") or r.startswith("TP"): return False
        return bool(tx.software_io(n, r) or tx.FW_MENTION.search(val(n, r)))

    def check(tag, ok, text):
        L.append("%s  %s  %s" % ("PASS" if ok else "FAIL", tag, text))
        if not ok: fails.append(tag)

    def nodes(n, net):
        return sorted(n["nets"].get(net) or [])

    L.append("The hardware EMCON lamp read back on the committed netlists (stream d4emcon, tools/lamp_check.py)")
    for k in sorted(sha): L.append("  board %s  %s  sha256/16 %s" % (k, NETS[k], sha[k]))
    L.append("")
    # L-1
    for net in PATH_NETS:
        nn = nodes(C, net)
        bad = [r for r, p, f in nn if fw(C, r)]
        check("L-1", bool(nn) and not bad, "C net %s: %d nodes, %s; firmware-set pins on it: %s" % (
            net, len(nn), ", ".join("%s.%s" % (r, p) for r, p, f in nn), ", ".join(bad) or "none"))
    # L-2
    pin = lambda n, r, p: n["pin"].get((r, p))
    u14 = {p: pin(C, "U14", p) for p in "123456"}
    ok = (u14["1"] == "GND" and u14["2"] == "GND" and u14["5"] == "+3V3" and u14["4"] == "EMCLAMP_Y"
          and {u14["3"], u14["6"]} == {"TX_INHIBIT_n", "EMCON_HW"} and "LVC1G57" in val(C, "U14").upper())
    check("L-2", ok, "C U14 %s: pins %s (SCES414P Figure 7, In1 held LOW selects Y = NOT(In0 OR In2))" % (
        val(C, "U14")[:40], u14))
    # L-3
    k_nodes, a_nodes = nodes(C, "EMCLAMP_K"), nodes(C, "EMCLAMP_A")
    g_nodes, y_nodes = nodes(C, "EMCLAMP_G"), nodes(C, "EMCLAMP_Y")
    ok = ({(r, p) for r, p, f in k_nodes} == {("D22", "1"), ("Q7", "3")}
          and {(r, p) for r, p, f in a_nodes} == {("D22", "2"), ("R47", "2")}
          and pin(C, "R47", "1") == "LED_RAIL_SW" and pin(C, "Q7", "2") == "GND"
          and {(r, p) for r, p, f in g_nodes} == {("Q7", "1"), ("R48", "2"), ("R49", "1")}
          and pin(C, "R49", "2") == "GND" and pin(C, "R48", "1") == "EMCLAMP_Y"
          and {(r, p) for r, p, f in y_nodes} == {("U14", "4"), ("R48", "1")})
    check("L-3", ok, "D22 K on %s, A on %s; Q7 S on %s, G on %s; R47 %s, R48 %s, R49 %s" % (
        [(r, p) for r, p, f in k_nodes], [(r, p) for r, p, f in a_nodes], pin(C, "Q7", "2"),
        [(r, p) for r, p, f in g_nodes], val(C, "R47"), val(C, "R48"), val(C, "R49")))
    # L-4
    sw = {p: pin(C, "SW_LIGHT", p) for p in "123456"}
    u5 = {p: pin(C, "U5", p) for p in "12345"}
    c5v = [(r, p) for r, p, f in nodes(C, "+5V") if not r.startswith("C")]
    b_pan = pin(B, "J_PANEL", "1"), pin(B, "J_PANEL", "2")
    f1 = pin(B, "F1", "1"), pin(B, "F1", "2")
    pan_nodes = [(r, p) for r, p, f in nodes(B, "PANEL_5V") if not r.startswith("C")]
    ok = (sw["2"] == "+5V" and sw["1"] == "LED_RAIL_SW" and u5["1"] == "+5V" and u5["3"] == "+5V"
          and u5["5"] == "+3V3" and pin(C, "J_PANEL", "1") == "+5V" and pin(C, "J_PANEL", "2") == "+5V"
          and b_pan == ("PANEL_5V", "PANEL_5V") and set(f1) == {"+5V_DEV", "PANEL_5V"}
          and not any(fw(B, r) for r, p in pan_nodes) and not any(fw(C, r) for r, p in c5v))
    check("L-4", ok, "SW_LIGHT pins %s; U5 %s pins %s; C +5V non-capacitor nodes %s; B J_PANEL pins 1, 2 on %s; B F1 %s "
          "pins on %s; B PANEL_5V non-capacitor nodes %s" % (sw, val(C, "U5")[:24], u5, c5v, b_pan, val(B, "F1")[:20], f1,
                                                              pan_nodes))
    # L-5: firmware-set pins one two-pin part away from a path net
    L.append("")
    L.append("L-5  firmware-set pins one two-pin part away from the lamp's path (not on it):")
    seen = set()
    for net in PATH_NETS:
        for r, p, f in nodes(C, net):
            if len([1 for (rr, pp) in C["pin"] if rr == r]) != 2: continue
            other = pin(C, r, "2" if p == "1" else "1")
            if not other or tx.is_ground(other) or other.startswith("+"): continue    # a rail or ground, not a pin
            for r2, p2, f2 in nodes(C, other):
                if fw(C, r2) and (r, r2) not in seen:
                    seen.add((r, r2))
                    L.append("     %s -- %s %s -- %s (%s) pin %s %s" % (net, r, val(C, r), other, val(C, r2)[:30], p2, f2 or ""))
    L.append("")
    L.append("RESULT: %s" % ("every check holds" if not fails else "FAIL: " + ", ".join(sorted(set(fails)))))
    open(out, "w").write("\n".join(L) + "\n")
    print(L[-1])
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
