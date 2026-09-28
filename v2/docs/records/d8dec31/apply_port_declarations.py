#!/usr/bin/env python3
"""The port declarations of boards A, D and E, corrected and completed (MESHSAT-1357, worker d8dec31, 28 September
2026; the review of decision 31, v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md).

WHAT IT CHANGES, in v2/ecad/tools/boards/a.json, d.json and e.json (the integrator's files):

  board A  external_ports: the entry J_DOCK pins 1 and 2, which are ground since session choice SC-55 (EQ-16), leaves;
           J_VR1 to J_VR4, the four pins that carry VIN_RAW since, enter; J_MAINSW enters as an off_board entry, its
           protection board C's parts at the MAIN switch, which the review read on board C's netlist; J_BM1 to J_BM11,
           the eleven antenna conductors that cross the board and leave through the dock plug and the end walls, enter
           as off_board entries naming the bulkhead arrestor, whose protection is CLAIMED and NOT JUDGED at the desk
           (the arrestor's sheet states no figure at the ruled level; review section 4.5). port_protect.py believes an
           off_board entry on its text (finding T-3), so TRN-001's PASS on board A after this script believes 12 of its
           18 entries on that text: the eleven antenna conductors and J_MAINSW.
           J_USBW and J_USBC_OUT stay as they are, word for word.
           internal_ports (new): every other connector that carries a supply or a signal, with where its lead goes.
  board D  external_ports unchanged; internal_ports (new).
  board E  external_ports unchanged; internal_ports (new).

`internal_ports` is read by port_protect.py since this stream's change of it (cover()): a connector pin carrying a
supply or a signal that is in neither list makes TRN-001 INCONCLUSIVE, and an entry that names no conductor FAILS it.

It asserts the old text (each board's external_ports as this review read them, and no internal_ports key), asserts the
new text differs, writes each table the way the board tables are written (json.dumps, indent 1, ensure_ascii False, a
final newline), re-parses what it wrote, and refuses a second run. It checks every entry against the board's committed
netlist of the declared phase before it writes: a reference that is not on the netlist, or an entry none of whose pins
carries a supply or a signal, stops it.

Usage: apply_port_declarations.py <tree root> [--check]      --check writes nothing
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netread

GROUND = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|VSS|EARTH|CHASSIS)([_\-].*)?$", re.I)
NETLIST = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
           "e": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"}
ARRESTOR = ("the gas-discharge arrestor that is this port's antenna bulkhead on the end wall's RF entry plate (PolyPhaser "
            "GTH-SFF-AL, v2/vendor/polyphaser; v2/docs/CASE-MARGINS.md C2 and C4; interface contract IF-AE-RF). It is "
            "rated for surge (10 kA) with a 90 V turn-on; its sheet states no IEC 61000-4-2 figure, which the review of "
            "decision 31 records as not judged at the desk")
RF = [("1", "VHF"), ("2", "HF"), ("3", "WIFI 2.4"), ("4", "GNSS"), ("5", "SDR"), ("6", "WIFI P2P A"), ("7", "WIFI P2P B"),
      ("8", "5G MAIN"), ("9", "5G DIV"), ("10", "IRIDIUM"), ("11", "LORA")]

# ------------------------------------------------------------------------------------------------------ board A
A_OLD_DOCK = {"ref": "J_DOCK", "pins": ["1", "2"],
              "why": "shore and vehicle DC arriving over the dock from the wall receptacle; the USB pair and the spare on "
                     "this same connector are board A to board E INSIDE the case and are not external conductors"}


def a_external(old):
    assert [e.get("ref") for e in old] == ["J_DOCK", "J_USBW", "J_USBC_OUT"], [e.get("ref") for e in old]
    assert old[0] == A_OLD_DOCK, "board A's J_DOCK entry is not the text this review read"
    new = [{"ref": "J_VR%d" % k,
            "why": "shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall "
                   "receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 "
                   "September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged "
                   "nothing. D2 (SMCJ40A) sits on these pins' own net"} for k in range(1, 5)]
    new += [old[1], old[2]]
    new.append({"ref": "J_MAINSW",
                "off_board": "board C's parts at the MAIN switch on the face: U10 (USBLC6-2SC6) on both conductors of the "
                             "pair, behind the beads FB1 and FB2 (600 R) with C26 (100 nF) across the pair (board C's "
                             "netlist: SW_MAIN, FB1, FB2, C26, U10, J_MAINSW; board C declares the same lead external). "
                             "Nothing on this board stands between the lead and U1's PB pin: findings A-F2 and X-C1 of "
                             "the review of decision 31",
                "why": "the MAIN button's lead from the panel: a person presses the button on the face, and its contact "
                       "reaches the LTC2954's PB pin on this board"})
    for n, name in RF:
        new.append({"ref": "J_BM%s" % n, "off_board": ARRESTOR,
                    "why": "the %s antenna conductor: it crosses this board from the SMA jack J_RF%s to this blind-mate "
                           "receptacle with no part on it, and leaves through the dock plug and the end wall" % (name, n)})
    return new


A_INTERNAL = (
    [{"ref": "J_RF%s" % n, "why": "the SMA jack of the pigtail to the %s radio inside the case: the same conductor as "
                                  "J_BM%s, which is declared external, and no part of this board is on it" % (name, n)}
     for n, name in RF] +
    [{"ref": "J_DOCK", "why": "signals between board A and board E inside the case, through the dock block E5 (interface "
                              "contract IF-AE-DOCK): SHORE_INHIBIT on pin 8, the sensor controller's USB pair on pins 9 "
                              "and 10, the hot stop line HOT-R1 on pin 12; the other pins are ground"}] +
    [{"ref": "J_CP%d" % k, "why": "the pack's positive over the dock block, from board P by board E's F3, all inside the "
                                  "case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P"}
     for k in range(1, 5)] +
    [{"ref": "J_PRE1", "why": "the pre-charge pin of the pack's positive over the dock block, inside the case: it mates "
                              "first and reaches CELL+ through R1 (10 R)"},
     {"ref": "J_AB1", "why": "the control ribbon to board B above this board, inside the case (IF-AB-RIBBON)"},
     {"ref": "J_AB2", "why": "the wall-port ribbon to board B, inside the case (IF-AB-WALL): it carries the wall USB pair "
                             "on from J_USBW, which is declared external and clamped on this board by U29"},
     {"ref": "J_MEZZ1", "why": "the mezzanine harness to board D, inside the case (IF-AD-HARNESS)"},
     {"ref": "J_MEZZ_PWR1", "why": "board D's 5 V lead behind the eFuse U23, inside the case (IF-AD-HARNESS)"}] +
    [{"ref": r, "why": "a rail lead to board B, inside the case (IF-AB-POWER)"}
     for r in ("J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV")] +
    [{"ref": "J_54V", "why": "the 54 V lead to board B's PoE injector, inside the case (IF-AB-POWER); the conductor that "
                             "leaves the case is board B's Ethernet jack, which board B declares"},
     {"ref": "J_PA", "why": "13.8 V to the power amplifier module on the inside of the face plate (IF-A-PA); the lead "
                            "stays inside the case"},
     {"ref": "J_HF", "why": "12 V to the QMX HF unit in the lid tray, in the lid harness (IF-LID-HF). The lead stays "
                            "inside the case; the unit's own panel is touched by the operator, and what reaches this lead "
                            "through the unit is recorded in the review of decision 31 as not judged at the desk"},
     {"ref": "J_MON", "why": "the supply lead of the Xenarc monitor on the face, behind the eFuse U21 (IF-MON). The lead "
                             "stays inside the case; the monitor's glass and bezel are touched by the operator, and what "
                             "reaches this lead through the monitor is recorded in the review of decision 31 as not judged "
                             "at the desk"},
     {"ref": "J_HEAT", "why": "the pack heater mat in the pack bay, inside the case (IF-A-HEAT)"}])

# ------------------------------------------------------------------------------------------------------ board D
D_INTERNAL = [
    {"ref": "J_HARN1", "why": "the mezzanine harness from board A, inside the case (IF-AD-HARNESS)"},
    {"ref": "J_PWR1", "why": "the 5 V lead from board A's eFuse U23, inside the case (IF-AD-HARNESS)"},
    {"ref": "J_PAIN", "why": "the drive coax to the power amplifier module on the inside of the face plate (IF-A-PA)"},
    {"ref": "J_VGG", "why": "the gate bias lead to the power amplifier module on the inside of the face plate (IF-A-PA)"},
    {"ref": "J_FLANGE", "why": "the thermistor lead of the power amplifier's flange, inside the case (IF-D-FLANGE)"},
    {"ref": "J_USB3", "why": "the touch USB lead of the Xenarc monitor on the face (IF-MON, session choice SC-HF-06). The "
                             "lead stays inside the case; the monitor's glass and bezel are touched by the operator, no "
                             "clamp stands on this pair, and the review of decision 31 records it as finding D-F3, not "
                             "judged at the desk"}]

# ------------------------------------------------------------------------------------------------------ board E
E_INTERNAL = [
    {"ref": "J_BATT", "why": "the pack's power lead from board P on its XT60, inside the case (IF-PE-PACK); the pack's own "
                             "protection is on board P"},
    {"ref": "J_SMB", "why": "the SMBus lead to board P's gauge, inside the case (IF-PE-PACK)"},
    {"ref": "J_BLK", "why": "the twelve signal wires to the dock block E5 and through it to board A, inside the case "
                            "(IF-AE-DOCK): SHORE_INHIBIT, the sensor controller's USB pair and the hot stop line HOT-R1"},
    {"ref": "P_CP", "why": "the pack's positive to the dock block E5 on a 12 AWG wire, inside the case (IF-AE-DOCK)"},
    {"ref": "P_VR", "why": "VIN_RAW to the dock block E5 on a 12 AWG wire, inside the case (IF-AE-DOCK): the bus behind "
                           "this board's own entry protection, which board A declares external at J_VR1 to J_VR4"},
    {"ref": "J_DCF", "why": "the DCF77 receiver module beside this board, inside the case (IF-E-SENSORS)"},
    {"ref": "J_GEIGER", "why": "the Geiger counter module beside this board, inside the case (IF-E-SENSORS)"},
    {"ref": "J_LTG", "why": "the lightning sensor module beside this board, inside the case (IF-E-SENSORS). It shares the "
                            "sensor bus SDA1 and SCL1 with the outside pod J_POD, which is declared external"},
    {"ref": "J_FAN1", "why": "mixer fan 1 under the plate, inside the sealed case (IF-E-FANS)"},
    {"ref": "J_FAN2", "why": "mixer fan 2 under the plate, inside the sealed case (IF-E-FANS)"},
    {"ref": "J_TAMP", "why": "the lid and tamper reed sensor's lead under the frame, inside the case (IF-E-TAMP)"},
    {"ref": "PAD_W1", "why": "water electrode A on the case floor, bare copper under the plate, inside the sealed case "
                             "(IF-E-WATER): fed from +3V3_E6 through R38 (1 M)"},
    {"ref": "PAD_W2", "why": "water electrode B on the case floor, bare copper under the plate, inside the sealed case "
                             "(IF-E-WATER): into the sensor controller's ADC0 past R39 (1 M) and C51 (100 nF)"}]

EXPECT_EXT = {"d": ["J_ANT", "J_PAOUT", "J_HS1", "J_HS2"], "e": ["J_DCIN", "J_SOLAR", "J_POD"]}


def conductor(net):
    n = (net or "").strip()
    return not (n.upper() in ("GND", "GNDA", "AGND", "NC", "") or GROUND.match(n) or n.lower().startswith("unconnected-"))


def check_against_netlist(root, letter, ext, internal):
    comps, _nets = netread.read(os.path.join(root, NETLIST[letter]))
    covered = set()
    for kind, rows in (("external", ext), ("internal", internal)):
        for e in rows:
            ref = e["ref"]
            assert ref in comps, "board %s: %s entry %s is not on %s" % (letter.upper(), kind, ref, NETLIST[letter])
            assert len(e.get("why", "").strip()) >= 20, (letter, ref)
            pins = {p: n for p, n in comps[ref]["pins"].items() if (not e.get("pins") or p in e["pins"])}
            for p in e.get("pins") or []:
                assert p in comps[ref]["pins"] and conductor(comps[ref]["pins"][p]), \
                    "board %s: %s.%s carries no supply or signal" % (letter.upper(), ref, p)
            live = {p for p, n in pins.items() if conductor(n)}
            assert live, "board %s: no pin of %s entry %s carries a supply or a signal" % (letter.upper(), kind, ref)
            assert not (live and {(ref, p) for p in live} & covered), "board %s: %s is declared twice" % (letter.upper(), ref)
            covered |= {(ref, p) for p in live}
    left = [(r, p, n) for r, c in sorted(comps.items()) if re.match(r"^(J|P|PAD|W)(_|\d|$)", r)
            for p, n in sorted(c["pins"].items()) if conductor(n) and (r, p) not in covered]
    assert not left, "board %s: connector pins no entry covers: %s" % (letter.upper(), left)
    return len(covered)


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry = os.path.abspath(argv[0]), "--check" in argv
    plan = []
    for letter, internal in (("a", A_INTERNAL), ("d", D_INTERNAL), ("e", E_INTERNAL)):
        p = os.path.join(root, "v2", "ecad", "tools", "boards", "%s.json" % letter)
        old_text = open(p, encoding="utf-8").read()
        t = json.loads(old_text)
        if "internal_ports" in t:
            raise SystemExit("apply_port_declarations: board %s already declares internal_ports: already applied" % letter.upper())
        assert json.dumps(t, indent=1, ensure_ascii=False) + "\n" == old_text, "board %s's table is not written the way this script writes it" % letter
        ext_old = t.get("external_ports") or []
        if letter == "a":
            ext_new = a_external(ext_old)
        else:
            assert [e.get("ref") for e in ext_old] == EXPECT_EXT[letter], (letter, [e.get("ref") for e in ext_old])
            ext_new = ext_old
        n = check_against_netlist(root, letter, ext_new, internal)
        out = {}
        for k, v in t.items():            # internal_ports goes beside external_ports, the rest keeps its order
            out[k] = ext_new if k == "external_ports" else v
            if k == "external_ports": out["internal_ports"] = internal
        new_text = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
        assert new_text != old_text
        back = json.loads(new_text)
        assert back["internal_ports"] == internal and back["external_ports"] == ext_new
        assert {k: v for k, v in back.items() if k not in ("external_ports", "internal_ports")} == \
               {k: v for k, v in t.items() if k != "external_ports"}, "another key of board %s's table moved" % letter
        plan.append((p, new_text, letter, len(ext_old), len(ext_new), len(internal), n))
    for p, new_text, letter, a, b, c, n in plan:
        if not dry:
            with open(p, "w", encoding="utf-8") as f: f.write(new_text)
            assert json.load(open(p, encoding="utf-8"))["internal_ports"]
        print("apply_port_declarations: board %s external_ports %d -> %d entries, internal_ports %d entries, %d connector "
              "pins covered%s" % (letter.upper(), a, b, c, n, " (checked, not written)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
