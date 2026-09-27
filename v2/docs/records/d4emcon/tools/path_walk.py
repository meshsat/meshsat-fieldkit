#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): the hardware inhibit path of every transmitter of the kit, walked on the committed
netlists pin by pin, across the board-to-board connectors.

Each path is DECLARED below as a chain of hops and then PROVED on the netlists: every hop names a part, the pin the path
enters by and the pin it leaves by, and the script refuses the path unless the entering pin sits on the net the path is
on and the leaving pin on the net the path goes on to; a connector hop is refused unless the same pin number of the
mated connector (tx_inhibit.MATES, which check_contracts proves map-identical) carries the next net on the other board.
Every node of every net on the path is then printed, with the part's value, so that nothing on a net is left unread.

It reads; it writes only the file named by --out (never under v2/ecad). Nothing here is a verdict.

usage: path_walk.py --tools <v2/ecad/tools> --ecad <v2/ecad> --out <file.txt>"""
import hashlib, os, re, sys

NETLISTS = {"A": "pcb-a-power-a23/out/pcb-a-power.net", "B": "pcb-b-compute-b19/out/pcb-b-compute.net",
            "C": "pcb-c-display-c8/out/pcb-c-display.net", "D": "pcb-d-aprs-d9/out/pcb-d-aprs.net",
            "E": "pcb-e1-dock-e7/out/pcb-e1-dock.net", "P": "pcb-p-pack-p2/out/pcb-p-pack.net"}

# The shared conductors, from the operator's contact to each board. A hop is (board, ref, pin in, pin out, what it is).
# "J" hops cross a ribbon: (board, connector, pin, other board, other connector).
TXI_TO_C = [("C", "TX_INHIBIT_n")]
TXI_TO_B = TXI_TO_C + [("J", "C", "J_PANEL", "11", "B", "J_PANEL"), ("B", "TX_INHIBIT_n")]
TXI_TO_A = TXI_TO_B + [("J", "B", "J_AB1", "16", "A", "J_AB1"), ("A", "TX_INHIBIT_n")]
TXI_TO_D = TXI_TO_A + [("J", "A", "J_MEZZ1", "8", "D", "J_HARN1"), ("D", "TX_INHIBIT_n")]
EH_TO_C = TXI_TO_C + [("P", "C", "U9", "2", "4", "Schmitt buffer, EMCON_HW = TX_INHIBIT_n"), ("C", "EMCON_HW")]
EH_TO_B = EH_TO_C + [("J", "C", "J_PANEL", "8", "B", "J_PANEL"), ("B", "EMCON_HW")]
EH_TO_A = EH_TO_B + [("J", "B", "J_AB1", "15", "A", "J_AB1"), ("A", "EMCON_HW")]


def _slot(s):
    m = 29 + s
    return dict(
        wl=EH_TO_B + [("P", "B", "U%d12" % s, "2", "4", "inverter on the module's own 3.3 V, EMCON_ON = NOT EMCON_HW"),
                      ("B", "EMCON_ON%d" % s),
                      ("P", "B", "U%d13" % s, "1", "6", "open-drain inverter, channel 1"),
                      ("B", "WL_nDIS%d" % s), ("T", "B", "U%dA" % m, "89", "the module's WL_nDisable")],
        bt=EH_TO_B + [("P", "B", "U%d12" % s, "2", "4", "inverter on the module's own 3.3 V, EMCON_ON = NOT EMCON_HW"),
                      ("B", "EMCON_ON%d" % s),
                      ("P", "B", "U%d13" % s, "3", "4", "open-drain inverter, channel 2"),
                      ("B", "BT_nDIS%d" % s), ("T", "B", "U%dA" % m, "91", "the module's BT_nDisable")],
        card=EH_TO_B + [("P", "B", "U%d16" % s, "1", "4", "AND on the slot's own 5 V, S%dA_EN = EMCON_HW AND PCIE_PWR_EN%d" % (s, s)),
                        ("B", "S%dA_EN" % s),
                        ("S", "B", "U%d03" % s, "3", "8", "buck converter, EN to its switch node"),
                        ("B", "S%dA_SW" % s), ("P", "B", "L%d01" % s, "1", "2", "the buck's inductor"),
                        ("B", "+3V3_S%dA" % s), ("P", "B", "R%d65" % s, "1", "2", "Kelvin shunt, 5 mOhm"),
                        ("B", "+3V3_M2C%d" % s),
                        ("T", "B", "J_M2C%d" % s, "2", "the card socket's 3.3 V pins")])


PATHS = [
    ("1", "SA868 VHF exciter (board D, U2): keying pin forced to receive",
     TXI_TO_D + [("P", "D", "U12", "2", "4", "AND, KEY = PTT_ANY AND TX_INHIBIT_n"), ("D", "KEY"),
                 ("P", "D", "U13", "2", "4", "open-drain inverter: KEY low releases SA_PTT_n"),
                 ("D", "SA_PTT_n"), ("T", "D", "U2", "5", "the SA868's PTT")]),
    ("2b", "RA30H1317M1 30 W PA, path (b): gate bias off on board D",
     TXI_TO_D + [("P", "D", "U12", "2", "4", "AND, KEY = PTT_ANY AND TX_INHIBIT_n"), ("D", "KEY"),
                 ("P", "D", "U14", "1", "4", "AND, PA_KEY = KEY AND PA_EN"), ("D", "PA_KEY"),
                 ("S", "D", "U15", "4", "1", "adjustable LDO, EN to OUT: the PA's gate bias"),
                 ("D", "VGG_SW"), ("T", "D", "J_VGG", "1", "the lead to the PA module's VGG pin")]),
    ("2b-relay", "RA30H1317M1 30 W PA, path (b): the T/R relay at rest",
     TXI_TO_D + [("P", "D", "U12", "2", "4", "AND, KEY = PTT_ANY AND TX_INHIBIT_n"), ("D", "KEY"),
                 ("P", "D", "U14", "1", "4", "AND, PA_KEY = KEY AND PA_EN"), ("D", "PA_KEY"),
                 ("P", "D", "R52", "1", "2", "gate resistor"), ("D", "RLY_DRV"),
                 ("P", "D", "Q2", "1", "3", "N-channel FET, gate to drain: the relay coil's low side"),
                 ("D", "RLY_K"), ("T", "D", "K1", "8", "the relay coil")]),
    ("2a", "RA30H1317M1 30 W PA, path (a): drain supply off on board A, from TX_INHIBIT_n",
     TXI_TO_A + [("P", "A", "U35", "1", "4", "AND, PA_TXOK = TX_INHIBIT_n AND EMCON_HW"), ("A", "PA_TXOK"),
                 ("P", "A", "U36", "1", "4", "AND, PA_EN = PA_TXOK AND PA_HOLD"), ("A", "PA_EN"),
                 ("P", "A", "R58", "1", "2", "upper leg of the enable divider"), ("A", "PA_UVLO"),
                 ("S", "A", "U13", "1", "12", "buck-boost controller, EN/UVLO; VOSNS sits on the rail"),
                 ("A", "+13V8_PA"), ("T", "A", "J_PA", "1", "the PA module's drain supply")]),
    ("2a-hw", "RA30H1317M1 30 W PA, path (a): the same gate from EMCON_HW",
     EH_TO_A + [("P", "A", "U35", "2", "4", "AND, PA_TXOK = TX_INHIBIT_n AND EMCON_HW"), ("A", "PA_TXOK")]),
    ("3", "QMX HF transceiver (board A, J_HF): DC input removed, from TX_INHIBIT_n",
     TXI_TO_A + [("P", "A", "U37", "1", "4", "AND, HF_TXOK = TX_INHIBIT_n AND EMCON_HW"), ("A", "HF_TXOK"),
                 ("P", "A", "U38", "1", "4", "AND, HF_EN = HF_TXOK AND HF_HOLD"), ("A", "HF_EN"),
                 ("P", "A", "R124", "1", "2", "upper leg of the enable divider"), ("A", "HF_UVLO"),
                 ("S", "A", "U15", "1", "12", "buck-boost controller, EN/UVLO; VOSNS sits on the rail"),
                 ("A", "+12V_HF"), ("T", "A", "J_HF", "1", "the QMX's DC input")]),
    ("3-hw", "QMX HF transceiver: the same gate from EMCON_HW",
     EH_TO_A + [("P", "A", "U37", "2", "4", "AND, HF_TXOK = TX_INHIBIT_n AND EMCON_HW"), ("A", "HF_TXOK")]),
    ("4", "RockBLOCK 9704 (board B, J_RB9704): supply removed",
     EH_TO_B + [("P", "B", "U503", "1", "4", "AND, RB_EN = EMCON_HW AND RB_SW_EN"), ("B", "RB_EN"),
                ("P", "B", "R530", "1", "2", "upper leg of the enable divider"), ("B", "RB_UVLO"),
                ("S", "B", "U24", "3", "5", "eFuse, EN/UVLO to OUT"), ("B", "+5V_RB"),
                ("T", "B", "J_RB9704", "15", "the RockBLOCK's V_IN+")]),
    ("4-en", "RockBLOCK 9704: the module's ENABLE forced low",
     EH_TO_B + [("P", "B", "U536", "1", "4", "AND, RB_IEN = EMCON_HW AND RB_SW_IEN"), ("B", "RB_IEN"),
                ("T", "B", "J_RB9704", "3", "the RockBLOCK's I_EN")]),
    ("5", "RM520N-GL 5G module (board B, J_M2C2): supply removed at once", _slot(2)["card"]),
    ("5-off", "RM520N-GL: FULL_CARD_POWER_OFF# low at once",
     EH_TO_B + [("P", "B", "U212", "2", "4", "inverter on the module's own 3.3 V"), ("B", "EMCON_ON2"),
                ("P", "B", "U220", "1", "6", "open-drain inverter"), ("B", "5G_PWROFF_n"),
                ("T", "B", "J_M2C2", "6", "the module's FULL_CARD_POWER_OFF#")]),
    ("5-wd", "RM520N-GL: W_DISABLE1# low at once (firmware-mediated, not counted)",
     EH_TO_B + [("P", "B", "U212", "2", "4", "inverter on the module's own 3.3 V"), ("B", "EMCON_ON2"),
                ("P", "B", "U215", "1", "6", "open-drain inverter"), ("B", "5G_W_DIS_n"),
                ("T", "B", "J_M2C2", "8", "the module's W_DISABLE1#")]),
    ("5-dchg", "RM520N-GL: the socket rail discharged and held through 15 Ohm",
     EH_TO_B + [("P", "B", "U212", "2", "4", "inverter on the module's own 3.3 V"), ("B", "EMCON_ON2"),
                ("P", "B", "Q212", "1", "3", "N-channel FET, gate to drain"), ("B", "5G_DCHG"),
                ("P", "B", "R295", "2", "1", "15 Ohm 1 W"), ("B", "+3V3_M2C2"),
                ("T", "B", "J_M2C2", "2", "the card socket's 3.3 V pins")]),
    ("6", "AW7915-AED WiFi card, slot 1 (board B, J_M2C1): supply removed", _slot(1)["card"]),
    ("7", "AW7915-AED WiFi card, slot 3 (board B, J_M2C3): supply removed", _slot(3)["card"]),
    ("8", "CM5 slot 1 WiFi (U30A pin 89)", _slot(1)["wl"]),
    ("9", "CM5 slot 2 WiFi (U31A pin 89)", _slot(2)["wl"]),
    ("10", "CM5 slot 3 WiFi (U32A pin 89)", _slot(3)["wl"]),
    ("11", "CM5 slot 1 Bluetooth (U30A pin 91)", _slot(1)["bt"]),
    ("12", "CM5 slot 2 Bluetooth (U31A pin 91)", _slot(2)["bt"]),
    ("13", "CM5 slot 3 Bluetooth (U32A pin 91)", _slot(3)["bt"]),
    ("14", "E22-900M30S LoRa (board B, U12): supply removed",
     EH_TO_B + [("P", "B", "U504", "1", "4", "AND, E22_EN = EMCON_HW AND LORA_ON"), ("B", "E22_EN"),
                ("P", "B", "R531", "1", "2", "upper leg of the enable divider"), ("B", "E22_UVLO"),
                ("S", "B", "U21", "5", "1", "load switch, EN/UVLO to VOUT"), ("B", "+5V_LORA"),
                ("T", "B", "U12", "9", "the E22's VCC")]),
    ("15", "E72 CC2652P Zigbee coordinator (board B, U13): supply removed",
     EH_TO_B + [("P", "B", "U505", "1", "4", "AND, E72_EN = EMCON_HW AND ZB_ON"), ("B", "E72_EN"),
                ("S", "B", "U22", "5", "1", "load switch, EN/UVLO to VOUT"), ("B", "+3V3_ZB"),
                ("T", "B", "U13", "20", "the E72's VCC")]),
    ("16", "E72 CC2652P OpenThread RCP (board B, U14): supply removed",
     EH_TO_B + [("P", "B", "U505", "1", "4", "AND, E72_EN = EMCON_HW AND ZB_ON"), ("B", "E72_EN"),
                ("S", "B", "U22", "5", "1", "load switch, EN/UVLO to VOUT"), ("B", "+3V3_ZB"),
                ("T", "B", "U14", "20", "the E72's VCC")]),
    ("17", "LimeSDR Mini 2.4 (board B, J_LIME): USB VBUS removed",
     EH_TO_B + [("P", "B", "U501", "1", "4", "AND, LIME_EN_A = EMCON_HW AND LIME_HW_EN"), ("B", "LIME_EN_A"),
                ("P", "B", "U502", "1", "4", "AND, LIME_EN = LIME_EN_A AND LIME_SW_EN"), ("B", "LIME_EN"),
                ("P", "B", "R529", "1", "2", "upper leg of the enable divider"), ("B", "LIME_UVLO"),
                ("S", "B", "U23", "3", "5", "eFuse, EN/UVLO to OUT"), ("B", "+5V_LIME"),
                ("T", "B", "J_LIME", "1", "the LimeSDR's USB VBUS")]),
    ("lamp", "The hardware EMCON lamp (board C, D22; SD-EMC-6, CON-021)",
     TXI_TO_C + [("P", "C", "U14", "3", "4", "configurable gate wired NOR(TX_INHIBIT_n, EMCON_HW)"), ("C", "EMCLAMP_Y"),
                 ("P", "C", "R48", "1", "2", "gate resistor"), ("C", "EMCLAMP_G"),
                 ("P", "C", "Q7", "1", "3", "N-channel FET, gate to drain: the lamp's sink"), ("C", "EMCLAMP_K"),
                 ("T", "C", "D22", "1", "the lamp's cathode")]),
    ("lamp-hw", "The EMCON lamp's second input",
     EH_TO_C + [("P", "C", "U14", "6", "4", "configurable gate wired NOR(TX_INHIBIT_n, EMCON_HW)"), ("C", "EMCLAMP_Y")]),
]
TRANSMITTER_ROWS = ["1", "2b", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17"]


def main(argv):
    tools = ecad = out = None
    while argv:
        if argv[0] == "--tools": tools = argv[1]
        elif argv[0] == "--ecad": ecad = argv[1]
        elif argv[0] == "--out": out = argv[1]
        else: print(__doc__); return 2
        argv = argv[2:]
    if not (tools and ecad and out): print(__doc__); return 2
    if "/v2/ecad/" in os.path.abspath(out): print("refused: --out lies under v2/ecad"); return 2
    sys.path.insert(0, os.path.abspath(tools)); sys.dont_write_bytecode = True
    import tx_inhibit as tx
    nls, shas = {}, {}
    for k, p in NETLISTS.items():
        path = os.path.join(ecad, p)
        nls[k] = tx.parse_netlist(path)
        shas[k] = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    mates = {}
    for m in tx.MATES:
        mates[m["a"]] = m["b"]; mates[m["b"]] = m["a"]
    lines, bad = [], []
    lines.append("The hardware inhibit paths of the kit's 17 transmitters, walked on the committed netlists (stream d4emcon)")
    for k in sorted(shas): lines.append("  board %s  %s  sha256/16 %s" % (k, NETLISTS[k], shas[k]))
    lines.append("")

    def val(k, ref): return (nls[k]["comps"].get(ref) or {}).get("value", "")

    def net_dump(k, n):
        nodes = nls[k]["nets"].get(n)
        if nodes is None:
            bad.append("board %s has no net %s" % (k, n)); return ["      NO SUCH NET"]
        o = []
        for r, p, f in sorted(nodes, key=lambda x: (re.sub(r"\d+", "", x[0]), len(x[0]), x[0], len(x[1]), x[1])):
            far = ""
            ps = tx.pins_of(nls[k], r)
            if re.match(r"^(R|C|L|FB|D)\d", r) and len(ps) == 2:
                far = "  -> %s" % nls[k]["pin"].get((r, ps[1] if ps[0] == p else ps[0]), "?")
            o.append("      %-9s pin %-4s %-16s %s%s" % (r, p, (f or "-")[:16], val(k, r)[:88], far))
        return o

    for pid, title, hops in PATHS:
        lines.append("=" * 118)
        lines.append("PATH %s  %s" % (pid, title))
        cur = pending = None
        for h in hops:
            if len(h) == 2:                                        # a net: (board, name)
                k, n = h
                if pending is not None and pending != (k, n):
                    bad.append("path %s: the hop before left on %s and the path declares %s" % (pid, pending, (k, n)))
                pending = None
                cur = (k, n)
                lines.append("  [%s] net %s  (%d nodes)" % (k, n, len(nls[k]["nets"].get(n) or [])))
                lines += net_dump(k, n)
            elif h[0] == "J":
                _j, ka, ja, pin, kb, jb = h
                if mates.get((ka, ja)) != (kb, jb):
                    bad.append("path %s: %s %s and %s %s are not a mated pair in tx_inhibit.MATES" % (pid, ka, ja, kb, jb))
                na = nls[ka]["pin"].get((ja, pin))
                nb = nls[kb]["pin"].get((jb, pin))
                if cur != (ka, na): bad.append("path %s: %s %s pin %s is on %s, the path is on %s" % (pid, ka, ja, pin, na, cur))
                lines.append("  >> ribbon: board %s %s pin %s (%s)  ==  board %s %s pin %s (%s)" % (ka, ja, pin, na, kb, jb, pin, nb))
                cur = (kb, nb)
                pending = cur
            elif h[0] in ("P", "S"):
                _t, k, ref, pi, po, what = h
                ni, no = nls[k]["pin"].get((ref, pi)), nls[k]["pin"].get((ref, po))
                if cur != (k, ni): bad.append("path %s: %s %s pin %s is on %s, the path is on %s" % (pid, k, ref, pi, ni, cur))
                lines.append("  >> %s %s: in by pin %s (%s, %r), out by pin %s (%s, %r): %s" % (
                    k, ref, pi, ni, nls[k]["func"].get((ref, pi)), po, no, nls[k]["func"].get((ref, po)), what))
                lines.append("       %s [%s]" % (val(k, ref)[:150], (nls[k]["comps"].get(ref) or {}).get("fp", "").split(":")[-1]))
                sup = tx._supply_nets(nls[k], ref)
                if sup: lines.append("       runs from %s" % ", ".join(sup))
                cur = (k, no)
                pending = cur
            elif h[0] == "T":
                _t, k, ref, pin, what = h
                n = nls[k]["pin"].get((ref, pin))
                if cur != (k, n): bad.append("path %s: the target %s %s pin %s is on %s, the path is on %s" % (pid, k, ref, pin, n, cur))
                lines.append("  == TARGET %s %s pin %s (%r) on %s: %s" % (k, ref, pin, nls[k]["func"].get((ref, pin)), n, what))
                lines.append("       %s" % val(k, ref)[:150])
        lines.append("")
    lines.append("=" * 118)
    lines.append("paths declared: %d; transmitter rows covered: %s" % (len(PATHS), ", ".join(TRANSMITTER_ROWS)))
    lines.append("RESULT: %s" % ("every declared hop holds on the netlists" if not bad else "%d hop(s) REFUSED" % len(bad)))
    for b in bad: lines.append("  REFUSED: " + b)
    open(out, "w").write("\n".join(lines) + "\n")
    print(lines[-1 - len(bad)])
    for b in bad: print("  REFUSED: " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
