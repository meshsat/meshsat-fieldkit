#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): the netlist read-back of the stream's circuit drafts, apply_b_d4e.py (board B, D4E-B B-1 to
B-5) and apply_c_d4e_f1.py (board C, D4E-F1), for the integrator to run on the netlists regenerated on the KiCad box.

It PARSES the netlist with tx_inhibit.parse_netlist (the RF-002 instrument's own reader) and asserts, net by net, every node the
draft makes (MUST) and every old node the draft removes (MUST NOT), each printed PASS or FAIL with the nodes it read. It judges
nothing else: RF-002's walk and the suite are re-taken separately. Run on the committed set 10 netlists it must FAIL every
change (nothing is applied yet), which is the reading filed beside it.

usage: readback_d4e.py --tools <v2/ecad/tools> --board B|C <netlist.net> [--out <file.txt>]"""
import hashlib, os, sys

# net -> (nodes that must be on it, nodes that must not be on it); a node is (ref, pin)
B = {
    # B-1, the RockBLOCK's lines
    "RB_RXD": ({("J_RB9704", "14"), ("U538", "4"), ("R533", "1")}, {("U18", "26")}),
    "RB_RXD_H": ({("U18", "26"), ("U538", "1")}, set()),
    "RB_CTRL": ({("J_RB9704", "6"), ("U539", "4"), ("R534", "1")}, {("U6", "20")}),
    "RB_CTRL_H": ({("U6", "20"), ("U539", "1")}, set()),
    "RB_GO": ({("U537", "4"), ("U538", "2"), ("U539", "2")}, set()),
    "RB_STATUS": ({("J_RB9704", "7"), ("R41", "1"), ("U7", "7"), ("U537", "2")}, set()),
    "RB_XMTG": ({("J_RB9704", "8"), ("R42", "1"), ("U7", "8")}, set()),
    "RB_TXD": ({("J_RB9704", "13"), ("U18", "25"), ("R535", "1")}, set()),
    # B-4, U536's band
    "RB_IEN": ({("J_RB9704", "3"), ("R532", "2"), ("R527", "1"), ("U543", "1"), ("U537", "1")}, {("U536", "4")}),
    "RB_IEN_DRV": ({("U536", "4"), ("R532", "1")}, set()),
    # B-2, the E72s' lines
    "ZBA_RXD": ({("U13", "7"), ("U540", "6"), ("R536", "1")}, {("U16", "26")}),
    "ZBA_RST_n": ({("U13", "24"), ("U540", "4"), ("R28", "1")}, {("U16", "24")}),
    "ZBA_BSL": ({("U13", "10"), ("U541", "6"), ("R30", "1")}, {("U16", "28")}),
    "ZBB_RXD": ({("U14", "7"), ("U542", "6"), ("R537", "1")}, {("U17", "26")}),
    "ZBB_RST_n": ({("U14", "24"), ("U542", "4"), ("R29", "1")}, {("U17", "24")}),
    "ZBB_BSL": ({("U14", "10"), ("U541", "4"), ("R31", "1")}, {("U17", "28")}),
    "+3V3_ZB": ({("R538", "1"), ("R536", "2"), ("R537", "2"), ("U22", "1")}, set()),
    # B-3, the E22's lines
    "LORA_GO": ({("U544", "4"), ("U545", "2"), ("U546", "2"), ("U547", "2"), ("U548", "2"), ("U549", "2"), ("U550", "2")}, set()),
    "E22_EN": ({("U504", "4"), ("U544", "2")}, set()),
    "LORA_RXEN_G": ({("U12", "6"), ("U545", "4"), ("R543", "1")}, set()),
    "LORA_TXEN_G": ({("U12", "7"), ("U546", "4"), ("R542", "1")}, set()),
    "LORA_NRST": ({("U12", "15"), ("U547", "4"), ("R544", "1")}, set()),
    "LORA_MOSI": ({("U12", "17"), ("U548", "4")}, set()),
    "LORA_SCLK": ({("U12", "18"), ("U549", "4")}, set()),
    "LORA_NSS": ({("U12", "19"), ("U550", "4")}, set()),
    "LORA_DIO1": ({("U12", "13"), ("U551", "2"), ("R539", "1")}, set()),
    "LORA_BUSY": ({("U12", "14"), ("U552", "2"), ("R540", "1")}, set()),
    "LORA_MISO": ({("U12", "16"), ("U553", "2"), ("R541", "1")}, set()),
    "LORA_RXEN": ({("U545", "1")}, {("U12", "6")}),
    "LORA_TXEN": ({("U546", "1")}, {("U12", "7")}),
    "SPI3_MISO": ({("U553", "4")}, {("U12", "16")}),
    "SPI3_CE1": ({("U550", "1"), ("R25", "1")}, {("U12", "19")}),
    # B-5, D4E-F2
    "5G_TPR_n": ({("U221", "1"), ("U554", "1"), ("R545", "1")}, set()),
    "5G_PWROFF_n": ({("J_M2C2", "6"), ("U220", "6"), ("U554", "6"), ("R238", "1")}, {("U221", "1")}),
}
# every part a draft adds, with its supply pin's net (what an unpowered-state argument rests on)
B_SUPPLY = {"U537": ("5", "+3V3_DEV"), "U538": ("5", "+3V3_DEV"), "U539": ("5", "+3V3_DEV"), "U540": ("5", "+3V3_DEV"),
            "U541": ("5", "+3V3_DEV"), "U542": ("5", "+3V3_DEV"), "U543": ("6", "+5V_DEV"), "U544": ("5", "+3V3_CM3"),
            "U545": ("5", "+3V3_CM3"), "U550": ("5", "+3V3_CM3"), "U551": ("5", "+3V3_CM3"), "U553": ("5", "+3V3_CM3"),
            "U554": ("5", "+3V3_CM2")}
B_VALUES = {"R41": "2.2k 1%", "R42": "2.2k 1%", "R527": "15k 1%", "R532": "2.2k 1%", "R238": "100k 1%", "R538": "4.7k 1%"}
B_OTHER = [("U543", "5", "+3V3_DEV"), ("R538", "2", "GND"), ("R41", "2", "GND"), ("R42", "2", "GND")]
C = {
    "EMCON_HW_DRV": ({("U9", "4"), ("R52", "1")}, set()),
    "EMCON_HW": ({("R52", "2"), ("D23", "2"), ("J_PANEL", "8")}, {("U9", "4")}),
    "TX_INHIBIT_n": ({("D23", "1"), ("SW_EMCON", "1"), ("U9", "2")}, set()),
}
C_VALUES = {"R52": "330R 1%"}


def main(argv):
    args, pos, it = {}, [], iter(argv)
    for a in it:
        if a.startswith("--"):
            args[a] = next(it, "")
        else:
            pos.append(a)
    if "--tools" not in args or args.get("--board") not in ("B", "C") or len(pos) != 1 or not pos[0].endswith(".net"):
        print(__doc__); return 2
    sys.path.insert(0, args["--tools"])
    import tx_inhibit
    path = os.path.abspath(pos[0])
    board = args["--board"]
    n = tx_inhibit.parse_netlist(path)
    nets = {k: set((x[0], str(x[1])) for x in v) for k, v in n["nets"].items()}
    comps = n["comps"]
    pin_net = {}
    for k, v in nets.items():
        for node in v:
            pin_net[node] = k
    lines = ["The read-back of stream d4emcon's circuit drafts (tools/readback_d4e.py)",
             "  board %s  v2/%s  sha256/16 %s" % (board, path.split("/v2/")[-1],
                                            hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]), ""]
    fails = 0
    table, values = (B, B_VALUES) if board == "B" else (C, C_VALUES)
    for net, (must, mustnot) in table.items():
        have = nets.get(net, set())
        miss = sorted(must - have); bad = sorted(mustnot & have)
        ok = not miss and not bad
        fails += not ok
        lines.append("%s  net %-14s %d nodes; missing %s; must not be on it %s" % ("PASS" if ok else "FAIL", net, len(have),
                     ", ".join("%s.%s" % x for x in miss) or "none", ", ".join("%s.%s" % x for x in bad) or "none"))
    for ref, val in values.items():
        got = (comps.get(ref) or {}).get("value") or ""
        ok = got.startswith(val)
        fails += not ok
        lines.append("%s  value %-5s %r (expected to start with %r)" % ("PASS" if ok else "FAIL", ref, got[:40], val))
    if board == "B":
        for ref, (pin, net) in B_SUPPLY.items():
            got = pin_net.get((ref, pin))
            ok = got == net
            fails += not ok
            lines.append("%s  supply %s pin %s on %s (expected %s)" % ("PASS" if ok else "FAIL", ref, pin, got, net))
        for ref, pin, net in B_OTHER:
            got = pin_net.get((ref, pin))
            ok = got == net
            fails += not ok
            lines.append("%s  pin %s.%s on %s (expected %s)" % ("PASS" if ok else "FAIL", ref, pin, got, net))
    lines += ["", "RESULT: %s" % ("every check holds" if not fails else "%d check(s) fail" % fails)]
    text = "\n".join(lines) + "\n"
    if "--out" in args:
        if "/v2/ecad/" in os.path.abspath(args["--out"]):
            print("refused: the output must not lie under v2/ecad"); return 2
        open(args["--out"], "w").write(text)
    print(text, end="")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
