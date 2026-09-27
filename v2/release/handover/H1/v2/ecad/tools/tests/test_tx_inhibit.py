#!/usr/bin/env python3
"""RF-002's transmitter instrument (tx_inhibit.py, S-02 of MESHSAT-1357, 26 September 2026).

The rule is about TRANSMITTERS and it was judged on the LINE: board B read PASS of 3 while its Compute Modules'
own radios were disabled only by a software expander. Each fixture below is a netlist written for one question,
with a defective input that must FAIL and an acceptable one that must PASS.

Review fix-up of round 4 (26 September 2026): a push-pull gate or a level shifter on the Compute Module's
WL_nDisable read PASS, and a software pin anywhere on the path but the last net (the asserted line itself, a net
behind a series resistor or a pass FET, a diode) was never looked at. The fixtures after the first block are those
cases, both ways round.

Second fix-up (26 September 2026): the fail-safe states (the panel unplugged or unpowered, the line held by its own
pull-downs against everything that can lift it), a diode from a rail or to ground on a forced net, a series resistor
in front of the anchor pin, the pull a forced net may carry, a resistor feeding a gated rail, a pull-up behind a
series resistor on a Compute Module pin, and RF-002's applicability on every board the walk writes a result for.

Round 6 (26 September 2026): every pin a held net meets passes its sheet's current (II, Ioff, an enable's current, a
module's own pull), and every element on a path is judged with its own supply down (R4T-F9). The fixtures now give
each logic part its supply pin and each gated enable the pull it needs, the way the boards must; the ones at the end
of the file are the new questions, both ways round.

Round 6 seventh pass (26 September 2026, R4T-D51 and R4T-D52): a VBAT pin is tied to the supply its charger runs from
(the STM32H7's to VDD, the Compute Module 5's to its 5V), a tied partner is looked for on the rail's whole conductor, a
supply input whose sibling pins sit on another net is not a load, and a part is read by what it is, not by what its
value mentions; the four fixtures before the last three.

Round 6 eighth pass (26 September 2026, R4T-D53 to R4T-D55): a part whose value or symbol only mentions a firmware family is
named wherever an active pin of it is met, never passed as a load; a supply row's other pins are every pin the maker's
number places in it, whatever the symbol calls them; and an STM32H7's VDD is a load only with its VBAT on the rail, on
ground or nowhere; the three fixtures before the last three.

Round 6 ninth pass (26 September 2026, R4T-D56 to R4T-D59): the mention is searched with the sixth pass's words for the
module ('CM5' with any digits, 'Compute Module'), six cases added to the mention fixture; an STM32H7's VDD is a load only
with VDDA, VDD33USB and VDD50USB also on the rail, on ground or nowhere (DS12110 3.5.1, Figure 3); a logic gate's push-pull
output on a gated rail is a second feed; and a PCA9555's VCC or an RP2040's IOVDD is not a load while a P-port pin or an
ADC input is held elsewhere (TI SCPS131J Figure 8-2, RP2040 Datasheet 2.9.5); the three fixtures before the last three.

Round 6 tenth pass (26 September 2026, R4T-D60 to R4T-D62): an STM32H7's VDD is a load only with its VDDLDO on the rail, on
ground or nowhere (DS12110 Table 24 'VDDLDO <= VDD', Table 9 note 8); a Compute Module 5's 5V only with GPIO_VREF on the
rail, on ground, nowhere or on the module's own CM5_3.3V or CM5_1.8V (CM5 datasheet 2.9 and 3.1); and every other supply
pin of a part on a gated rail is read, excused only by a net fed by the part's own outputs made from the rail or by a
maker's sentence that lets the two fall in that order; the last three fixtures of the file. One case the sixth pass
wrote as ACCEPTABLE, a CP2102N's VBUS held up elsewhere beside its VREGIN on the rail, reads UNDECIDED now (CP2102N Rev 1.5
2.3 states its leakage into the unpowered part) and moved to the last fixture.

Round 6 twelfth pass (27 September 2026, R4T-D70 to R4T-D73; the review of the eleventh pass, its three blocking items closed
as classes): on a gated conductor a pin is a load only where a row of its maker's clears it, and the PASS quotes the row;
every other pin reads UNDECIDED, named. The four fixtures at the end of the file are its three classes both ways (a part in
no class or a protection part, a switch's or a logic part's pin other than its outputs, a pin of the second part that
carries a split module) and the own-output path's maker's sentence; four earlier fixtures changed with it, each marked
where it did (board A's INA226, 'XCM5 filter', the PCA9555's SCL, board B's R111)."""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import tx_inhibit as T


def _nl(comps, nets):
    """Write a KiCad-shaped netlist and read it back through the tool's own parser.
    comps: {ref: (value, footprint, lib)}; nets: {name: [(ref, pin, pinfunction or "")]}"""
    d = tempfile.mkdtemp(prefix="txi-")
    c = "".join('    (comp (ref "%s")\n      (value "%s")\n      (footprint "%s")\n      (libsource (lib "%s") (part "%s") (description ""))\n      (tstamps "x"))\n'
                % (r, v, fp, (lib or "X:Y").split(":")[0], (lib or "X:Y").split(":")[1]) for r, (v, fp, lib) in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s")%s (pintype "passive"))\n'
                       % (r, p, (' (pinfunction "%s")' % f) if f else "") for r, p, f in nodes)
        n += '    (net (code "%d") (name "/%s")\n%s    )\n' % (i, name, body)
    p = os.path.join(d, "x.net")
    open(p, "w").write("(export (version \"E\")\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    return T.parse_netlist(p)


AND1 = ("74LVC1G08 AND: EMCON gate", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")
BUF1 = ("74LVC1G34 buffer", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")
OD1 = ("74LVC1G07 open-drain buffer", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")
INV1 = ("74LVC1G04 inverter", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")
NAND1 = ("74LVC1G00 NAND", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")
OD_INV1 = ("74LVC1G06 open-drain inverter", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")
U17 = ("74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC1G17W5-7)", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")
Q08 = ("SN74LVC08APWR quad AND", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "X:Y")
EXP = ("PCA9555PW 0x20: outputs", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "Interface_Expansion:PCA9555PW")
MCU = ("STM32H753VITx I/O supervisor", "Package_QFP:LQFP-100_14x14mm_P0.5mm", "Connector_Generic:STM32H753VI")
LSW = ("TPS22810DRV", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", "Power_Management:TPS22810DRV")
FET = ("2N7002", "Package_TO_SOT_SMD:SOT-23", "Transistor_FET:2N7002")
LORA = ("Ebyte E22-900M30S 1 W LoRa", "meshsat:Ebyte_E22-900M30S", "Connector_Generic:E22_900M30S")
TOGGLE = ("EMCON locking toggle (closed = TX inhibit)", "Connector:X", "Connector_Generic:Conn_01x02")
TX_POWER = [dict(name="test LoRa", options=[dict(board="B", ref="U12", kind="power")])]
PD = ("100k", "R", "Device:R")                  # the line's own pull-down, 100 kOhm as on boards A, B and D


def _tx(r, name):
    return [x for x in r if x["text"].startswith(name)][0]


def _line(r, name="EMCON_HW"):
    return [x for x in r if x["text"].startswith("the asserted line " + name)][0]


def _power_board(en_drivers, en_pull="10k"):
    """A LoRa module U12 on +5V_X, switched by a TPS22810 whose EN/UVLO (pin 5) is the net LORA_EN; EMCON_HW is
    made on this board by the toggle SW1 closing to ground. The AND runs on +3V3 and LORA_EN carries a pull-down
    (`en_pull`, None for none), so the enable stays low if the AND loses its supply (R4T-F9, round 6)."""
    comps = {"U12": LORA, "U21": LSW, "C1": ("10u", "C", "Device:C"), "SW1": TOGGLE}
    nets = {"+5V_X": [("U12", "9", "VCC"), ("U21", "1", "VOUT"), ("C1", "1", "")],
            "+5V_DEV": [("U21", "6", "VIN")], "GND": [("U12", "1", "GND"), ("U21", "4", "GND"), ("C1", "2", ""), ("SW1", "2", "")],
            "LORA_EN": [("U21", "5", "EN/UVLO")], "EMCON_HW": [("SW1", "1", "")], "SW_EN": []}
    if en_pull:
        comps["R70"] = (en_pull, "R", "Device:R"); nets["LORA_EN"].append(("R70", "1", "")); nets["GND"].append(("R70", "2", ""))
    if "and" in en_drivers:
        comps["U5"] = AND1
        nets["EMCON_HW"].append(("U5", "1", "")); nets["SW_EN"].append(("U5", "2", ""))
        nets["LORA_EN"].append(("U5", "4", "")); nets.setdefault("+3V3", []).append(("U5", "5", "")); nets["GND"].append(("U5", "3", ""))
    if "expander" in en_drivers:
        comps["U6"] = EXP
        nets["LORA_EN"].append(("U6", "4", "IO0_0"))
    if "expander_sw" in en_drivers:
        comps["U6"] = EXP
        nets["SW_EN"].append(("U6", "4", "IO0_0"))
    if "gpio_on_line" in en_drivers:
        comps["U41"] = MCU
        nets["EMCON_HW"].append(("U41", "33", "PC5"))
    return _nl(comps, nets)


def t_a_transmitter_whose_supply_switch_only_software_enables_fails():
    """DEFECTIVE: the enable of the LoRa module's load switch is driven by an I2C expander alone."""
    r = T.judge({"B": _power_board({"expander"})}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    tx = _tx(r, "test LoRa")
    assert tx["ok"] is False, tx
    assert "does not force off" in tx["detail"], tx["detail"]


def t_a_transmitter_whose_supply_switch_emcon_gates_passes():
    """ACCEPTABLE: EMCON AND software into the enable (the pattern boards A and B use), the expander on the AND's
    other input, and nothing but the toggle on the line."""
    r = T.judge({"B": _power_board({"and", "expander_sw"})}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    tx = _tx(r, "test LoRa")
    assert tx["ok"] is True, tx
    assert "U5 AND 1->4" in tx["detail"], tx["detail"]
    assert _line(r)["ok"] is True, _line(r)


def t_an_enable_the_expander_can_also_drive_is_not_a_hardware_gate():
    """DEFECTIVE: the AND drives the enable and the expander is wired to the same net, so the two fight and the
    software side can win. A hardware gate has one driver."""
    r = T.judge({"B": _power_board({"and", "expander"})}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    tx = _tx(r, "test LoRa")
    assert tx["ok"] is False and "U6 pin 4" in tx["detail"] and "firmware" in tx["detail"], tx


def t_a_gpio_on_the_asserted_line_fails_the_line_and_every_path_from_it():
    """DEFECTIVE (boards B and C as generated at main 82dd1e4d): an MCU pin straight on EMCON_HW. The AND gate
    downstream is exactly right, and the line it reads can still be driven by firmware."""
    r = T.judge({"B": _power_board({"and", "expander_sw", "gpio_on_line"})}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    line = _line(r)
    assert line["ok"] is False and "U41 pin 33" in line["detail"] and "firmware" in line["detail"], line
    tx = _tx(r, "test LoRa")
    assert tx["ok"] is False and "its line EMCON_HW" in tx["detail"], tx


def t_an_expander_behind_a_series_resistor_on_an_intermediate_net_fails():
    """DEFECTIVE: EMCON_HW > R9 > net X, which the expander also drives, > AND > the enable. The first version read
    this as a pass because it asked only about the enable net."""
    comps = {"U12": LORA, "U21": LSW, "SW1": TOGGLE, "U5": AND1, "R9": ("1k", "R", "Device:R"), "U6": EXP,
             "R70": ("10k", "R", "Device:R")}
    nets = {"+5V_X": [("U12", "9", "VCC"), ("U21", "1", "VOUT")], "+5V_DEV": [("U21", "6", "VIN")],
            "GND": [("U12", "1", "GND"), ("U21", "4", "GND"), ("SW1", "2", ""), ("U5", "3", ""), ("R70", "2", "")],
            "+3V3": [("U5", "5", "")],
            "EMCON_HW": [("SW1", "1", ""), ("R9", "1", "")], "X": [("R9", "2", ""), ("U5", "1", ""), ("U6", "4", "IO0_0")],
            "SW_EN": [("U5", "2", "")], "LORA_EN": [("U5", "4", ""), ("U21", "5", "EN/UVLO"), ("R70", "1", "")]}
    r = T.judge({"B": _nl(comps, nets)}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    tx = _tx(r, "test LoRa")
    assert tx["ok"] is False and "U6 pin 4" in tx["detail"], tx
    # ACCEPTABLE: the same shape with the expander moved to the AND's other input
    nets["X"] = [("R9", "2", ""), ("U5", "1", "")]; nets["SW_EN"].append(("U6", "4", "IO0_0"))
    assert _tx(T.judge({"B": _nl(comps, nets)}, table=TX_POWER, accessories=[], receivers=[], owed=[]), "test LoRa")["ok"] is True


def _diode_board(anode_on_enable):
    """A BAT54 between an MCU pin and the enable. With its cathode on the enable, the MCU can lift the enable
    EMCON holds low; with its anode there, it can only pull the enable lower, EMCON's way."""
    comps = {"U12": LORA, "U21": LSW, "SW1": TOGGLE, "U5": AND1, "U41": MCU, "R70": ("10k", "R", "Device:R"),
             "D7": ("BAT54 wired-OR", "Package_TO_SOT_SMD:SOT-23", "Device:D_Schottky")}
    k, a = (("MCU_OUT", "LORA_EN") if anode_on_enable else ("LORA_EN", "MCU_OUT"))
    nets = {"+5V_X": [("U12", "9", "VCC"), ("U21", "1", "VOUT")], "+5V_DEV": [("U21", "6", "VIN")],
            "GND": [("U12", "1", "GND"), ("U21", "4", "GND"), ("SW1", "2", ""), ("U5", "3", ""), ("R70", "2", "")],
            "+3V3": [("U5", "5", ""), ("U41", "50", "VDD")],
            "EMCON_HW": [("SW1", "1", ""), ("U5", "1", "")], "SW_EN": [("U5", "2", "")],
            "LORA_EN": [("U5", "4", ""), ("U21", "5", "EN/UVLO"), ("R70", "1", "")], "MCU_OUT": [("U41", "40", "PA3")]}
    nets[k].append(("D7", "1", "K")); nets[a].append(("D7", "2", "A"))
    return _nl(comps, nets)


def t_a_diode_that_can_lift_the_enable_brings_its_mcu_in():
    """DEFECTIVE: the reviewer's case, a BAT54 from an MCU pin onto LORA_EN with its cathode on the enable. The
    first version counted every D* part as a reader."""
    tx = _tx(T.judge({"B": _diode_board(False)}, table=TX_POWER, accessories=[], receivers=[], owed=[]), "test LoRa")
    assert tx["ok"] is False and "U41 pin 40" in tx["detail"] and "D7 diode" in tx["detail"], tx


def t_a_diode_that_can_only_pull_the_enable_low_drives_nothing_and_its_reverse_current_is_undecided():
    """ACCEPTABLE to the driver census: the same diode the other way round can only pull the enable down, which is
    what EMCON does. Round 6: with the AND's own supply down the enable is held by R70 alone, and the diode's REVERSE
    current from the MCU pin (a BAT54's, stated by no held sheet) is then a current nobody bounds, so the path is
    UNDECIDED, never FAIL, and names it. Renamed in round 6's second pass (review minor 6): it was called
    "..._is_no_threat" and has asserted UNDECIDED since round 6."""
    tx = _tx(T.judge({"B": _diode_board(True)}, table=TX_POWER, accessories=[], receivers=[], owed=[]), "test LoRa")
    assert tx["ok"] is None and "D7" in tx["detail"] and "reverse current" in tx["detail"] and "U41 pin 40" not in tx["detail"], tx


def _disable_board(through_shifter=True, extra_driver=False):
    comps = {"J_M2": ("M.2 B-key socket: RM520N-GL", "meshsat:M2", "Connector:Bus_M.2_Socket_B"),
             "SW1": TOGGLE, "R1": ("10k", "R", "Device:R")}
    nets = {"EMCON_HW": [("SW1", "1", "")], "GND": [("SW1", "2", "")],
            "W_DIS_n": [("J_M2", "8", "~{W_DISABLE1}"), ("R1", "1", "")], "+3V3": [("R1", "2", ""), ("J_M2", "2", "3.3V")]}
    if through_shifter:
        comps["Q1"] = FET
        nets["EMCON_HW"].append(("Q1", "3", "D")); nets["W_DIS_n"].append(("Q1", "2", "S")); nets["+3V3"].append(("Q1", "1", "G"))
    if extra_driver:
        comps["U6"] = EXP; nets["W_DIS_n"].append(("U6", "5", "IO0_1"))
    return _nl(comps, nets)


def _rf_table(cite):
    return [dict(name="test 5G", options=[dict(board="B", ref="J_M2", kind="rf_disable", pin="8", func=r"W_DISABLE1",
                                                safe=0, cite=cite, uncited="nobody documents it")])]


def t_a_documented_disable_pin_behind_a_level_shifter_is_accepted_and_the_fet_held_pull_leaves_it_undecided():
    """ACCEPTED as a reader, and UNDECIDED as a whole: the RM520N-GL's W_DISABLE1# is an input its maker documents
    (declared in PIN_READERS, as board B's J_M2C2 pin 8 is), and no drive constraint is stated; what is left is R1's
    pull against a level only the FET's channel holds (R4T-D32). Renamed in round 6's second pass (review minor 6): it
    was called "..._passes" and has asserted UNDECIDED since round 6."""
    saved = list(T.PIN_READERS)
    try:
        T.PIN_READERS.append(dict(board="B", ref="J_M2", pin="8", why="fixture: the maker's pin table says DI"))
        r = T.judge({"B": _disable_board()}, table=_rf_table("maker section 4.4.1"), accessories=[], receivers=[], owed=[])
    finally:
        T.PIN_READERS[:] = saved
    tx = _tx(r, "test 5G")
    # the declared input is accepted; what is left (round 6, review minor 1) is that R1 pulls against a level only a
    # FET's channel holds, at a gate drive of 3.3 V where the JSCJ 2N7002 states no on resistance
    assert tx["ok"] is None and "Q1 level shifter" in tx["detail"] and "a FET forces (Q1)" in tx["detail"] \
        and "no held document shows to be an input" not in tx["detail"], tx


def t_a_module_pin_nobody_documents_behind_a_level_shifter_leaves_the_line_undecided():
    """UNDECIDED, not PASS: a level shifter conducts both ways, so the far end of it is on the line's conductor,
    and here the far end is a socket pin no maker document calls an input (board B's AW7915-AED slots)."""
    r = T.judge({"B": _disable_board()}, table=[], accessories=[], receivers=[], owed=[])
    line = _line(r)
    assert line["ok"] is None and "J_M2 pin 8" in line["detail"], line
    import copy
    saved = copy.deepcopy(T.PIN_READERS)
    try:
        T.PIN_READERS.append(dict(board="B", ref="J_M2", pin="8", why="fixture: the maker calls it DI"))
        assert _line(T.judge({"B": _disable_board()}, table=[], accessories=[], receivers=[], owed=[]))["ok"] is True
    finally:
        T.PIN_READERS[:] = saved


def t_a_disable_pin_no_maker_documents_does_not_count():
    """DEFECTIVE: the AW7915-AED case. EMCON reaches W_DISABLE1#, and nothing says the card acts on it."""
    r = T.judge({"B": _disable_board()}, table=_rf_table(None), accessories=[], receivers=[], owed=[])
    tx = _tx(r, "test 5G")
    assert tx["ok"] is False and "nobody documents it" in tx["detail"], tx


def t_a_disable_pin_emcon_does_not_reach_fails_and_names_its_driver():
    """DEFECTIVE: the Compute Module case. The pin is driven by the expander alone."""
    r = T.judge({"B": _disable_board(through_shifter=False, extra_driver=True)}, table=_rf_table("maker"),
                accessories=[], receivers=[], owed=[])
    tx = _tx(r, "test 5G")
    assert tx["ok"] is False and "does not reach" in tx["detail"] and "U6" in tx["detail"], tx


def _key_board(inverter=True, expander_behind_fet=False, logic_rail="+5V_SA", ptt_pull=None, od=False, divider=None):
    """The SA868 on +5V_SA, keyed through the AND U12 and the inverter U13, both on `logic_rail`. On the exciter's
    own rail they cannot lose their supply while it keeps its own (the acceptable shape of these fixtures); on a rail
    of their own (board D's +3V3_D8) SA_PTT_n is held only by `ptt_pull` = (value, rail) when they do (R4T-F9)."""
    comps = {"U2": ("NiceRF SA868 VHF exciter", "meshsat:NiceRF_SA868", "Connector_Generic:SA868"),
             "U12": AND1, "SW1": TOGGLE}
    nets = {"TX_INHIBIT_n": [("SW1", "1", ""), ("U12", "2", "")], "GND": [("SW1", "2", ""), ("U12", "3", "")],
            "PTT_ANY": [("U12", "1", "")], "+5V_SA": [("U2", "8", "VBAT")]}
    nets.setdefault(logic_rail, []).append(("U12", "5", ""))
    if inverter:
        comps["U13"] = OD_INV1 if od else INV1
        nets["KEY"] = [("U12", "4", ""), ("U13", "2", "")]
        nets["SA_PTT_n"] = [("U13", "4", ""), ("U2", "5", "PTT_n")]
        nets[logic_rail].append(("U13", "5", "")); nets["GND"].append(("U13", "3", ""))
        if ptt_pull:
            comps["R60"] = (ptt_pull[0], "R", "Device:R"); nets["SA_PTT_n"].append(("R60", "1", ""))
            nets.setdefault(ptt_pull[1], []).append(("R60", "2", ""))
        if divider:
            # board D's round-6 shape: R88 from +5V_SA, R89 to ground
            comps["R88"] = (divider[0], "R", "Device:R"); comps["R89"] = (divider[1], "R", "Device:R")
            nets["SA_PTT_n"] += [("R88", "2", ""), ("R89", "1", "")]; nets["+5V_SA"].append(("R88", "1", ""))
            nets["GND"].append(("R89", "2", ""))
    else:
        nets["SA_PTT_n"] = [("U12", "4", ""), ("U2", "5", "PTT_n")]
    if expander_behind_fet:
        # board D's shape at main 82dd1e4d: Q6 (G on +3V3_D8, S on KEY, D on X_KEY) into a PCA9555 pin
        comps["Q6"] = FET; comps["U16"] = EXP
        nets["KEY"].append(("Q6", "2", "S")); nets["+3V3_D8"] = [("Q6", "1", "G")]
        nets["X_KEY"] = [("Q6", "3", "D"), ("U16", "7", "IO0_3")]
    return _nl(comps, nets)


_KEY = [dict(name="test SA868", options=[dict(board="D", ref="U2", kind="key", pin="5", func=r"PTT", safe=1, cite="pin 5 PTT")])]


def t_a_keying_pin_driven_to_receive_passes():
    tx = _tx(T.judge({"D": _key_board()}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is True and "U13 INV" in tx["detail"], tx


def t_a_keying_pin_driven_to_transmit_by_emcon_fails():
    """DEFECTIVE: without the inverter, asserting EMCON pulls an active-low PTT LOW, which KEYS the radio."""
    tx = _tx(T.judge({"D": _key_board(inverter=False)}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is False and "safe level is 1" in tx["detail"], tx


def t_an_expander_behind_a_pass_fet_on_an_intermediate_net_fails():
    """DEFECTIVE (board D's KEY at main 82dd1e4d): KEY reaches a PCA9555 pin through a level-shifter FET. With KEY
    held low the FET is on, so an expander driving high fights the AND gate."""
    tx = _tx(T.judge({"D": _key_board(expander_behind_fet=True)}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is False and "U16 pin 7" in tx["detail"] and "Q6 N-channel" in tx["detail"], tx


# ---------------------------------------------------------------- the Compute Module's pins may only be driven low
def _cm5_board(last, fixed=True, pull_up=False, elem_rail="+3V3_CM1"):
    """WL_nDisable (U30A pin 89) with `last` the element straight before the pin:
       "nand_fet": NAND(EMCON, software) into an N-FET to ground (the S-01 shape);
       "od":       a 74LVC1G07 open-drain buffer from EMCON;
       "and":      a 74LVC1G08 AND of EMCON and software, push-pull, onto the pin;
       "buf":      a 74LVC1G34 buffer from EMCON, push-pull, onto the pin;
       "shifter":  a 2N7002 level shifter (gate on a rail) from EMCON onto the pin.
    `fixed=False` leaves the expander on the pin as well. The element runs on `elem_rail`: the module's own 3.3 V
    output (+3V3_CM1, on U30A pin 84) by default, so it cannot lose its supply while the module keeps its own
    (R4T-F9, round 6)."""
    comps = {"U30A": ("receptacle A; module CM5108064", "meshsat:CM5", "Connector_Generic:CM5A"), "SW1": TOGGLE,
             "U6": EXP}
    nets = {"EMCON_HW": [("SW1", "1", "")], "GND": [("SW1", "2", "")], "WL_CTRL": [("U6", "13", "IO1_0")],
            "WL_nDIS1": [("U30A", "89", "WL_nDisable")], "+3V3_CM1": [("U30A", "84", "+3.3v_(Output)")]}
    if last == "nand_fet":
        comps.update(U40=NAND1, Q40=FET)
        nets["EMCON_HW"].append(("U40", "1", "")); nets["WL_CTRL"].append(("U40", "2", ""))
        nets["WL_GATE"] = [("U40", "4", ""), ("Q40", "1", "G")]; nets["GND"].append(("Q40", "2", "S"))
        nets["WL_nDIS1"].append(("Q40", "3", "D"))
    elif last == "od":
        comps.update(U40=OD1)
        nets["EMCON_HW"].append(("U40", "2", "")); nets["WL_nDIS1"].append(("U40", "4", ""))
    elif last == "and":
        comps.update(U40=AND1)
        nets["EMCON_HW"].append(("U40", "1", "")); nets["WL_CTRL"].append(("U40", "2", "")); nets["WL_nDIS1"].append(("U40", "4", ""))
    elif last == "buf":
        comps.update(U40=BUF1)
        nets["EMCON_HW"].append(("U40", "2", "")); nets["WL_nDIS1"].append(("U40", "4", ""))
    elif last == "shifter":
        comps.update(Q40=FET)
        nets["EMCON_HW"].append(("Q40", "3", "D")); nets["WL_nDIS1"].append(("Q40", "2", "S")); nets["+3V3"] = [("Q40", "1", "G")]
    if "U40" in comps:
        nets.setdefault(elem_rail, []).append(("U40", "5", "")); nets["GND"].append(("U40", "3", ""))
    if not fixed:
        nets["WL_nDIS1"].append(("U6", "14", "IO1_1"))
    if pull_up:
        comps["R40"] = ("10k", "R", "Device:R"); nets["WL_nDIS1"].append(("R40", "1", "")); nets.setdefault("+3V3", []).append(("R40", "2", ""))
    return _nl(comps, nets)


_CM5 = [dict(name="test CM5 WiFi", options=[dict(board="B", ref="U30A", kind="rf_disable", pin="89",
                                                  func=r"WL_nDisable", safe=0, cite="CM5 datasheet 2.1.1", drive="open_drain",
                                                  pin_model=dict(pull=(3.3, 1.8e3)))])]


def _cm5(last, **kw):
    return _tx(T.judge({"B": _cm5_board(last, **kw)}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")


def t_the_s01_open_drain_shape_passes():
    tx = _cm5("nand_fet")
    assert tx["ok"] is True, tx
    assert "U40 NAND" in tx["detail"] and "Q40 switch to ground" in tx["detail"], tx


def t_an_open_drain_buffer_on_the_pin_passes():
    assert _cm5("od")["ok"] is True, _cm5("od")


def t_a_push_pull_and_straight_onto_the_pin_fails():
    """DEFECTIVE (the reviewer's synthetic case): a 74LVC1G08 of EMCON and software drives pin 89 push-pull, so it
    drives the pin HIGH whenever EMCON is released, and the module 'drives it high internally when required'."""
    tx = _cm5("and")
    assert tx["ok"] is False and "push-pull AND" in tx["detail"], tx


def t_a_push_pull_buffer_straight_onto_the_pin_fails():
    tx = _cm5("buf")
    assert tx["ok"] is False and "push-pull buffer" in tx["detail"], tx


def t_a_level_shifter_onto_the_pin_fails():
    """DEFECTIVE: a 2N7002 pass-through level shifter passes EMCON_HW's push-pull drive to the pin."""
    tx = _cm5("shifter")
    assert tx["ok"] is False and "level shifter" in tx["detail"], tx


def t_a_carrier_pull_up_on_the_pin_fails():
    """DEFECTIVE: the pin 'can't be driven high' and the module pulls it up itself through 1.8 kOhm."""
    tx = _cm5("nand_fet", pull_up=True)
    assert tx["ok"] is False and "pulled up on the carrier by R40" in tx["detail"], tx


def t_the_s01_shape_with_the_expander_still_on_the_pin_fails():
    tx = _cm5("nand_fet", fixed=False)
    assert tx["ok"] is False and "U6 pin 14" in tx["detail"], tx


# ---------------------------------------------------------------- the line across the ribbons
def _two_boards(stm32_on_b):
    """Board A's gated rail with its AND on EMCON_HW, which arrives on J_AB1 pin 15 from board B, where the toggle
    stands in for the panel and, optionally, an STM32 pin sits on the line."""
    a = {"U12": LORA, "U21": LSW, "U5": AND1, "J_AB1": ("A-B interconnect", "Connector:X", "Connector_Generic:Conn_02x13"),
         "R102": PD, "R70": ("10k", "R", "Device:R")}
    an = {"+5V_X": [("U12", "9", "VCC"), ("U21", "1", "VOUT")], "+5V_DEV": [("U21", "6", "VIN")],
          "GND": [("U12", "1", "GND"), ("U21", "4", "GND"), ("R102", "2", ""), ("U5", "3", ""), ("R70", "2", "")],
          "+3V3": [("U5", "5", "")],
          "EMCON_HW": [("J_AB1", "15", "Pin_15"), ("U5", "1", ""), ("R102", "1", "")],
          "SW_EN": [("U5", "2", "")], "LORA_EN": [("U5", "4", ""), ("U21", "5", "EN/UVLO"), ("R70", "1", "")]}
    b = {"SW1": TOGGLE, "J_AB1": ("A-B interconnect", "Connector:X", "Connector_Generic:Conn_02x13")}
    bn = {"EMCON_HW": [("SW1", "1", ""), ("J_AB1", "15", "Pin_15")], "GND": [("SW1", "2", "")]}
    if stm32_on_b:
        b["U41"] = MCU; bn["EMCON_HW"].append(("U41", "33", "PC5"))
    return _nl(a, an), _nl(b, bn)


_TX_A = [dict(name="test LoRa", options=[dict(board="A", ref="U12", kind="power")])]


def t_a_software_pin_on_the_line_on_another_board_fails_this_boards_transmitter():
    """DEFECTIVE: board A's gate is right and board B's STM32 sits on the same conductor two ribbons away."""
    a, b = _two_boards(True)
    r = T.judge({"A": a, "B": b}, table=_TX_A, accessories=[], receivers=[], owed=[])
    line = _line(r)
    assert line["ok"] is False and "B U41 pin 33" in line["detail"] and "J_AB1 pin 15 = B J_AB1 pin 15" in line["detail"], line
    assert set(line["boards"]) >= {"A", "B"}, line
    assert _tx(r, "test LoRa")["ok"] is False
    a, b = _two_boards(False)
    assert _tx(T.judge({"A": a, "B": b}, table=_TX_A, accessories=[], receivers=[], owed=[]), "test LoRa")["ok"] is True


def t_a_board_the_line_crosses_and_that_is_absent_is_named_so_the_result_is_not_a_pass():
    """With board B's netlist absent the conductor cannot be followed there; the results name B, which
    check_contracts turns into UNJUDGED on every board they name."""
    a, _b = _two_boards(True)
    r = T.judge({"A": a, "B": None}, table=_TX_A, accessories=[], receivers=[], owed=[])
    assert "B" in _line(r)["boards"] and "B" in _tx(r, "test LoRa")["boards"], r


def _panel(b_comps, b_nets, pull_down="10k", gate="1g", u19_rail="+3V3_DEV"):
    """Board C as the kit has it since main faf8c981 (the toggle SW_EMCON on TX_INHIBIT_n with its pull-up R14, the
    Diodes 74LVC1G17 Schmitt buffer U9 making EMCON_HW, +3V3 made on the board from the ribbon's +5V) and a board B
    that receives both lines on J_PANEL, holds EMCON_HW down with R58 and reads it into an SN74LVC08A gate U19.
    `b_comps` and `b_nets` add to B. `pull_down` is R58's value (None for none); R59 on TX_INHIBIT_n stands for the
    three 100 kOhm the kit has on A, B and D, 33 kOhm together.

    ROUND 6: R58 IS 10 kOhm HERE. With every pin's stated current in the model, U19's input (II 5 uA, SCAS283W) and
    U9's output with the panel unpowered (IOFF 10 uA, Diodes DS35124) put 15 uA on the line, and 100 kOhm leaves it at
    1.5 V: the fixture of the second fix-up passed only because it took both currents as zero.

    ROUND 6 SECOND PASS: U19 IS A 74LVC1G08 ON +3V3_DEV unless `gate="08a"` asks for the quad SN74LVC08A. Every part
    but the reader is now taken powered or unpowered, whichever is worse, and the quad's sheet states no Ioff, so a line
    with it and a second reader on another rail is UNDECIDED whatever its pull-down (the fixtures below show both).
    `u19_rail` is U19's supply: a reader on a rail outside 3 V to 3.6 V is not judged at the LVC VIL."""
    c = {"SW_EMCON": TOGGLE, "R14": ("10k", "R", "Device:R"), "U9": U17, "U1": ("TLV75733PDBV 3.3 V LDO", "SOT-23-5", "X:Y"),
         "J_PANEL": ("panel ribbon", "Connector:X", "Connector_Generic:Conn_02x13")}
    cn = {"TX_INHIBIT_n": [("SW_EMCON", "1", ""), ("R14", "1", ""), ("U9", "2", ""), ("J_PANEL", "11", "")],
          "EMCON_HW": [("U9", "4", ""), ("J_PANEL", "8", "")], "+3V3": [("R14", "2", ""), ("U9", "5", ""), ("U1", "5", "")],
          "+5V": [("J_PANEL", "1", ""), ("U1", "1", "")], "GND": [("SW_EMCON", "2", ""), ("U9", "3", ""), ("U1", "2", "")]}
    b = {"J_PANEL": ("panel ribbon", "Connector:X", "Connector_Generic:Conn_02x13"), "R59": ("33k", "R", "Device:R"),
         "U19": Q08 if gate == "08a" else AND1}
    vcc_pin, gnd_pin = ("14", "7") if gate == "08a" else ("5", "3")
    bn = {"EMCON_HW": [("J_PANEL", "8", ""), ("U19", "1", "")], "TX_INHIBIT_n": [("J_PANEL", "11", ""), ("R59", "1", "")],
          "+5V": [("J_PANEL", "1", "")], "GND": [("R59", "2", ""), ("U19", gnd_pin, "")], "SW_EN": [("U19", "2", "")]}
    bn.setdefault(u19_rail, []).append(("U19", vcc_pin, ""))
    if pull_down:
        b["R58"] = (pull_down, "R", "Device:R"); bn["EMCON_HW"].append(("R58", "1", "")); bn["GND"].append(("R58", "2", ""))
    b.update(b_comps)
    for n, nodes in b_nets.items(): bn.setdefault(n, []).extend(nodes)
    return {"B": _nl(b, bn), "C": _nl(c, cn)}


def _line_of(boards, name="EMCON_HW"):
    return _line(T.judge(boards, table=[], accessories=[], receivers=[], owed=[]), name)


def t_the_panel_pair_as_the_kit_has_it_passes_both_lines():
    """ACCEPTABLE: the lines are driven only by the panel, and with it unplugged or its 3.3 V down the pull-downs
    hold them under the gates' 0.8 V VIL (TI SCAS283W) against the pins' own currents: 15 uA on 10 kOhm, 10.5 kOhm at
    the 5 percent a value that states no tolerance is taken at (R4T-D36), 0.16 V. DEFECTIVE at 100 kOhm, the value on
    boards A and B today: B's one input and C's unpowered buffer alone lift EMCON_HW to 15 uA x 105 kOhm = 1.58 V."""
    b = _panel({}, {})
    assert _line_of(b)["ok"] is True, _line_of(b)
    assert _line_of(b, "TX_INHIBIT_n")["ok"] is True, _line_of(b, "TX_INHIBIT_n")
    line = _line_of(_panel({}, {}, pull_down="100k"))
    assert line["ok"] is False and "rises to 1.58" in line["detail"] and "U19 pin 1 (II" in line["detail"] \
        and "U9 pin 4 unpowered (Ioff" in line["detail"], line


def t_a_reader_on_a_rail_outside_the_lvc_range_is_not_judged_at_its_vil():
    """UNDECIDED, not PASS (round 6 second pass, review minor 3): VIL 0.8 V is the LVC sheets' figure at VCC 3 V to
    3.6 V. The same line with B's gate on +5V (VIL 0.3 VCC there) or on a rail whose name states no voltage."""
    for rail in ("+5V", "+VCC_X"):
        line = _line_of(_panel({}, {}, u19_rail=rail))
        assert line["ok"] is None and "outside 3 V to 3.6 V" in line["detail"] and "U19 pin 1" in line["detail"], (rail, line)


def t_a_line_with_no_pull_down_floats_when_the_panel_is_out():
    """DEFECTIVE: nothing holds EMCON_HW low at B's gate once the panel is unplugged."""
    line = _line_of(_panel({}, {}, pull_down=None))
    assert line["ok"] is False and "floats" in line["detail"] and "B U19 pin 1" in line["detail"], line


def t_a_level_shifter_whose_far_side_is_pulled_up_lifts_the_line_when_the_panel_is_out():
    """DEFECTIVE (board B's Q106, Q206 and Q306 at main 82dd1e4d): a 2N7002 with its drain on EMCON_HW and its source
    pulled up to a slot rail through 10 kOhm. With the panel unplugged or unpowered, the body diode (anode on S, JSCJ
    2N7002 datasheet, Equivalent Circuit) sources the line from the slot rail, and the pull-down cannot hold it under
    0.8 V. While the panel drives, the census passes it: only the fail-safe state shows it."""
    b = _panel({"Q106": FET, "R137": ("10k", "R", "Device:R")},
               {"EMCON_HW": [("Q106", "3", "D")], "+3V3_S1A": [("Q106", "1", "G"), ("R137", "2", "")],
                "WIFI_W_DIS_n": [("Q106", "2", "S"), ("R137", "1", "")]})
    line = _line_of(b)
    assert line["ok"] is False and "rises to" in line["detail"] and "Q106" in line["detail"] \
        and "body diode" in line["detail"] and "R137" in line["detail"], line


def t_the_same_fet_turned_round_still_lifts_the_line_through_its_channel():
    """DEFECTIVE: with its source on EMCON_HW and its gate on the slot rail, the FET's body diode points away from the
    line, but its channel is on whenever the line sits below 3.3 V minus Vth(GS) (1.0 V to 2.5 V on the fitted JSCJ
    2N7002), so the far side's pull-up still lifts the line to as much as 2.3 V."""
    b = _panel({"Q206": FET, "R237": ("10k", "R", "Device:R")},
               {"EMCON_HW": [("Q206", "2", "S")], "+3V3_S2A": [("Q206", "1", "G"), ("R237", "2", "")],
                "5G_W_DIS_n": [("Q206", "3", "D"), ("R237", "1", "")]})
    line = _line_of(b)
    assert line["ok"] is False and "rises to" in line["detail"] and "channel" in line["detail"], line


def t_a_one_way_open_drain_buffer_in_place_of_the_shifter_passes():
    """ACCEPTABLE, the remedy, WITH the smaller pull-down: a 74LVC1G07 with its input on EMCON_HW drives the module
    side low and cannot pass the module side's pull-up back onto the line. Its own input current is counted: read on
    its slot rail +3V3_S1A it passes II 5 uA (SCES296AG), and while U19 reads the line it may be unpowered and pass its
    Ioff 10 uA, as may U19 while the buffer reads (round 6 second pass). At 100 kOhm the buffer that fixes the diode
    lifts the line to 25 uA x 105 kOhm = 2.63 V with U19 and U9. UNDECIDED with the quad SN74LVC08A as U19: it states no
    Ioff, and it may be unpowered while the buffer on its own slot rail reads the line."""
    comps, nets = {"U706": OD1, "R137": ("10k", "R", "Device:R")}, \
        {"EMCON_HW": [("U706", "2", "")], "+3V3_S1A": [("U706", "5", ""), ("R137", "2", "")],
         "GND": [("U706", "3", "")], "WIFI_W_DIS_n": [("U706", "4", ""), ("R137", "1", "")]}
    assert _line_of(_panel(comps, nets))["ok"] is True, _line_of(_panel(comps, nets))
    line = _line_of(_panel(comps, nets, pull_down="100k"))
    assert line["ok"] is False and "rises to 2.63" in line["detail"] and "U706 pin 2 (" in line["detail"], line
    line = _line_of(_panel(comps, nets, gate="08a"))
    assert line["ok"] is None and "U19 pin 1" in line["detail"] and "may be unpowered while the line is read" in line["detail"] \
        and "states no Ioff" in line["detail"], line


def _tap(rval, pd="10k"):
    return _panel({"U41": MCU, "R77": (rval, "R", "Device:R")},
                  {"EMCON_HW": [("R77", "1", "")], "EMCON_SENSE": [("R77", "2", ""), ("U41", "33", "PC5")],
                   "+3V3": [("U41", "50", "VDD")]}, pull_down=pd)


def t_a_declared_sense_tap_counts_only_behind_its_resistor_and_only_if_the_line_survives_it():
    """A controller pin reached through a series resistor is accepted by the census when READER_TAPS declares it with
    the resistor that makes the panel's buffer win, and refused when the resistor on the board is smaller. The fail-safe
    state asks the second question, with the pins' currents (15 uA here) in: with the panel out, a 10 kOhm tap driven
    high by a firmware error (3.3 V plus RAIL_TOL) against 10.5 kOhm lifts the line to about 1.8 V (DEFECTIVE). A
    1 MOhm tap holds it at 0.19 V while the controller runs, and is UNDECIDED all the same (round 6 second pass, review of
    round 6, blocking 2): the controller's rail can be down while U19 reads the line, and no held STM32 sheet states what
    an unpowered pin passes, so the tap cannot PASS until one does. The buffer is the remedy that can."""
    saved = list(T.READER_TAPS)
    try:
        line = _line_of(_tap("10k"))
        assert line["ok"] is False and "U41 pin 33" in line["detail"] and "firmware" in line["detail"], line   # undeclared
        T.READER_TAPS.append(dict(board="B", ref="U41", pin="33", through="R77", r_min=10000,
                                  why="fixture: a 3.3 V pin through 10 kOhm sources 0.33 mA, which the panel's buffer sinks"))
        line = _line_of(_tap("10k"))
        assert line["ok"] is False and "rises to 1.8" in line["detail"] and "U41 pin 33, a pin firmware can drive high" \
            in line["detail"] and "a pin whose direction firmware sets" not in line["detail"], line
        line = _line_of(_tap("100"))
        assert line["ok"] is False and "through a smaller one" in line["detail"], line
        T.READER_TAPS[:] = saved + [dict(board="B", ref="U41", pin="33", through="R77", r_min=1e6,
                                         why="fixture: 1 MOhm against the 10 kOhm pull-down leaves 0.19 V with the pin currents")]
        line = _line_of(_tap("1M"))
        assert line["ok"] is None and "reads 0.19 V" in line["detail"] and "U41 pin 33" in line["detail"] \
            and "possibly unpowered controller pin" in line["detail"], line
    finally:
        T.READER_TAPS[:] = saved


def t_a_second_source_on_a_gated_rail_fails():
    """DEFECTIVE: the rail the switch gates is also fed from +5V_DEV through a diode, so EMCON turning the switch
    off leaves the radio powered."""
    nl = _power_board({"and", "expander_sw"})
    comps = {r: (c["value"], c["fp"], c["lib"]) for r, c in nl["comps"].items()}
    comps["D9"] = ("SS14", "D_SMA", "Device:D_Schottky")
    nets = {n: list(v) for n, v in nl["nets"].items()}
    nets["+5V_X"].append(("D9", "1", "K")); nets["+5V_DEV"].append(("D9", "2", "A"))
    tx = _tx(T.judge({"B": _nl(comps, nets)}, table=TX_POWER, accessories=[], receivers=[], owed=[]), "test LoRa")
    assert tx["ok"] is False and "fed from +5V_DEV through D9" in tx["detail"], tx


def t_a_part_that_names_a_radio_and_is_in_no_list_fails():
    """DEFECTIVE: a radio nobody classified. ACCEPTABLE in the same board: an AND gate whose value names what it
    gates is not a radio."""
    nl = _nl({"U9": ("NiceRF SA868 second exciter", "meshsat:NiceRF_SA868", "X:Y"),
              "U19": ("SN74LVC08APWR quad AND: LimeSDR and RockBLOCK", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "X:Y")},
             {"GND": [("U9", "9", ""), ("U19", "7", "")]})
    r = T.judge({"D": nl}, table=[], accessories=[], receivers=[], owed=[])
    cls = [x for x in r if "names a radio" in x["text"]][0]
    assert cls["ok"] is False and "U9" in cls["detail"] and "U19" not in cls["detail"], cls
    r = T.judge({"D": nl}, table=[], accessories=[dict(board="D", ref="U9", value=r"SA868", why="test")], receivers=[], owed=[])
    assert [x for x in r if "names a radio" in x["text"]][0]["ok"] is True, r


def t_a_declared_accessory_whose_value_changed_is_asked_again():
    nl = _nl({"J_QMX": ("QMX HF transceiver, now on its own DC lead", "Connector:X", "X:Y")}, {"GND": [("J_QMX", "1", "")]})
    r = T.judge({"B": nl}, table=[], accessories=[dict(board="B", ref="J_QMX", value=r"QMX USB lead", why="data")], receivers=[], owed=[])
    cls = [x for x in r if "names a radio" in x["text"]][0]
    assert cls["ok"] is False and "now reads" in cls["detail"], cls


def t_a_declaration_resting_on_an_inference_leaves_its_board_undecided():
    """The QMX's USB lead: the manual gives the DC input's range and does not say USB cannot run the transmitter,
    so the declaration is owed, not proved, and the board reads UNDECIDED rather than PASS."""
    nl = _nl({"J_QMX": ("QMX USB lead (bank 2 hub, port 4)", "Connector:X", "X:Y")}, {"GND": [("J_QMX", "1", "")]})
    r = T.judge({"B": nl}, table=[], accessories=[], receivers=[])
    cls = [x for x in r if "names a radio" in x["text"]][0]
    assert cls["ok"] is None and "owed" in cls["detail"], cls


def t_a_gate_on_a_land_its_pin_map_is_not_for_is_not_walked():
    """A 74LVC1G08 on a six-pin land: the DBV map would be a guess there, so the walk stops and says so."""
    nl = _power_board({"and", "expander_sw"})
    nl["comps"]["U5"]["fp"] = "Package_TO_SOT_SMD:SOT-23-6"
    got, stopped = T.reach(nl)
    assert "LORA_EN" not in got and any("not the package" in s for s in stopped), (got, stopped)


def t_a_family_whose_sheet_is_not_held_is_not_walked():
    """74HC08 is not 74LVC08: its sheet is not held, so the walk does not guess its pin map."""
    nl = _power_board({"and", "expander_sw"})
    nl["comps"]["U5"]["value"] = "74HC08 AND"
    got, _stopped = T.reach(nl)
    assert "LORA_EN" not in got, got


def t_every_transmitter_option_carries_its_basis():
    """The table is data with its sources: a disable or key pin names the maker's document, or says why none
    counts; an accessory, a receiver, an owed declaration, a pin reader and a mate say why."""
    for t in T.TRANSMITTERS:
        for o in t["options"]:
            assert o["kind"] in ("power", "rf_disable", "key"), o
            if o["kind"] in ("rf_disable", "key"):
                assert o.get("cite") or o.get("uncited"), (t["name"], o)
                assert "safe" in o and "func" in o, (t["name"], o)
    for d in T.ACCESSORIES + T.RECEIVE_ONLY + T.OWED:
        assert d.get("why") and d.get("value"), d
    for d in T.OWED: assert d.get("owed"), d
    for d in T.PIN_READERS + T.MATES: assert d.get("why"), d
    for d in T.READER_TAPS: assert d.get("why") and d.get("through") and d.get("r_min"), d
    for fam in T.LOGIC + T.SWITCHES:
        assert fam.get("cite"), fam["name"]
    # round 6: every current and threshold the fail-safe network uses carries its sheet
    for fam in T.LOGIC:
        assert fam.get("ii") and "ioff" in fam and fam.get("leak_cite"), fam["name"]
    for sw in T.SWITCHES:
        # en_leak None is a statement too (round 6 second pass): the sheet bounds no current at the off threshold
        assert sw.get("vin") and sw.get("en_off") and "en_leak" in sw and sw.get("off_cite"), sw["name"]
        assert sw["en_leak"] is not None or "no maximum" in sw["off_cite"], sw["name"]
    for f in T.FETS: assert f.get("cite") and "leak" in f, f
    cm5 = [o for t in T.TRANSMITTERS for o in t["options"] if o["ref"] in ("U30A", "U31A", "U32A")]
    assert len(cm5) == 6 and all(o.get("drive") == "open_drain" for o in cm5), cm5


def t_the_walk_decides_rf002_and_no_contract():
    """RF-002 reads `inhibit_chain_<letter>`, so the transmitter results must land there, and nowhere else: a
    transmitter with no hardware gate is not a connector whose two ends disagree, which is what SCH-003 reads in
    `check_contracts_<letter>` (review fix-up of round 4, 26 September 2026: counted like the contracts, the walk
    failed SCH-003 on A, B, C and D and the set verdict INT-001 reads). The same two-board tree runs through the
    real script twice, once with a radio on board E that no list names: RF-002's verdict must turn, and SCH-003's
    and the set's must not move."""
    import json, subprocess, test_smbus_lead_contract as S

    def run(with_radio):
        ecad = S._tree(S.XH4, p_return="PACK_N", clamp_return="PACK_N")
        comps = {"J_SMB": ("pack SMBus", S.XH4)}
        nets = {"SCL0": [("J_SMB", "1")], "SDA0": [("J_SMB", "2")], "GND": [("J_SMB", "3")]}
        if with_radio:
            comps["U99"] = ("SX1262 LoRa radio nobody listed", "QFN")
            nets["GND"].append(("U99", "1")); nets["RF_EN"] = [("U99", "2")]
        S._write(ecad, "pcb-e1-dock", "e", comps, nets)
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_contracts.py"), ecad], cwd=ecad,
                           capture_output=True, text=True, timeout=300,
                           env=dict(os.environ, VERDICT_DIR=os.path.join(ecad, "out")))

        def v(name):
            rec = json.load(open(os.path.join(ecad, "out", name + ".verdict.json"), encoding="utf-8"))
            return rec["verdict"], rec["counts"], rec.get("evidence") or []
        return v("inhibit_chain_e"), v("check_contracts_e"), v("check_contracts"), r.stdout + r.stderr

    ic0, ce0, cs0, out0 = run(False)
    ic1, ce1, cs1, out1 = run(True)
    assert ic0[0] == "PASS" and ic1[0] == "FAIL" and any("names a radio" in x for x in ic1[2]), (ic0, ic1, out1[-1500:])
    assert [l for l in out1.splitlines() if l.startswith("FAIL") and "unclassified: U99" in l], out1[-1500:]
    assert ce1 == ce0 and cs1[:2] == cs0[:2], ("the walk moved a contract verdict", ce0, ce1, cs0[:2], cs1[:2])
    for rec in (ce1, cs1):
        assert not any("RF-002" in x for x in rec[2]), (rec, out1[-1500:])
    assert "[inhibit only]" in out1 and "RF-002's transmitter walk" in out1, out1[-1500:]

# ---------------------------------------------------------------- second fix-up of round 4 (26 September 2026)
def _edit(nl, comps=None, nets=None, move=None):
    """A parsed fixture with parts added: comps {ref: (value, fp, lib)}, nets {name: [(ref, pin, func)]} appended,
    move {(ref, pin): new net} re-homing a pin."""
    c = {r: (x["value"], x["fp"], x["lib"]) for r, x in nl["comps"].items()}
    n = {k: list(v) for k, v in nl["nets"].items()}
    for (ref, pin), new in (move or {}).items():
        hit = [(k, x) for k, v in n.items() for x in v if x[0] == ref and x[1] == pin]
        for k, x in hit: n[k].remove(x); n.setdefault(new, []).append(x)
    c.update(comps or {})
    for k, v in (nets or {}).items(): n.setdefault(k, []).extend(v)
    return _nl(c, n)


BAT54 = ("BAT54 wired-OR", "Package_TO_SOT_SMD:SOT-23", "Device:D_Schottky")


def _lora(nl):
    return _tx(T.judge({"B": nl}, table=TX_POWER, accessories=[], receivers=[], owed=[]), "test LoRa")


def t_a_diode_from_a_rail_onto_an_enable_emcon_holds_low_fails():
    """DEFECTIVE (the reviewer's probe): a BAT54 with its anode on +3V3_SW and its cathode on LORA_EN, which the AND
    holds low under EMCON. The first fix-up skipped a diode whose far side was a rail before asking which way it
    points. ACCEPTABLE the other way round: cathode on the rail, anode on the enable, a clamp that conducts only
    EMCON's way."""
    base = _power_board({"and", "expander_sw"})
    bad = _edit(base, {"D7": BAT54}, {"LORA_EN": [("D7", "1", "K")], "+3V3_SW": [("D7", "2", "A")]})
    tx = _lora(bad)
    assert tx["ok"] is False and "D7" in tx["detail"] and "+3V3_SW (anode)" in tx["detail"], tx
    good = _edit(base, {"D7": BAT54}, {"LORA_EN": [("D7", "2", "A")], "+3V3_SW": [("D7", "1", "K")]})
    # the census accepts it; with the AND's own supply down (round 6) the diode's reverse current from +3V3_SW,
    # which no held sheet states, is what R70 has to hold against, so the path is UNDECIDED and never a FAIL
    tx = _lora(good)
    assert tx["ok"] is None and "D7" in tx["detail"] and "reverse current" in tx["detail"] and "(anode)" not in tx["detail"], tx


def t_a_diode_whose_drawing_names_no_cathode_to_a_rail_is_undecided():
    """UNDECIDED, not PASS: a diode on A1/A2 pins between the enable and a rail; which way it conducts is not drawn."""
    tx = _lora(_edit(_power_board({"and", "expander_sw"}), {"D7": ("BAT54 wired-OR", "SOT-23", "Device:D_TVS")},
                     {"LORA_EN": [("D7", "1", "A1")], "+3V3_SW": [("D7", "2", "A2")]}))
    assert tx["ok"] is None and "names no cathode" in tx["detail"], tx


def t_a_forward_diode_to_ground_on_a_net_emcon_holds_high_fails():
    """DEFECTIVE (the mirror case): SA_PTT_n is held HIGH by the inverter under EMCON, and a diode from it (anode) to
    ground (cathode) pulls it down against that. ACCEPTABLE: the same diode as a clamp, cathode on the net."""
    bad = _edit(_key_board(), {"D8": BAT54}, {"SA_PTT_n": [("D8", "2", "A")], "GND": [("D8", "1", "K")]})
    tx = _tx(T.judge({"D": bad}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is False and "D8" in tx["detail"] and "pulls it down" in tx["detail"], tx
    good = _edit(_key_board(), {"D8": BAT54}, {"SA_PTT_n": [("D8", "1", "K")], "GND": [("D8", "2", "A")]})
    assert _tx(T.judge({"D": good}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")["ok"] is True


def t_a_series_resistor_in_front_of_a_compute_module_pin_passes():
    """ACCEPTABLE (the reviewer's probe): the S-01 open-drain shape, and a 74LVC1G07, each with a 33 Ohm resistor
    before pin 89. The anchor pin was the target only on the last net, so the census of the net before the resistor
    met pin 89 and called it a pin whose direction firmware sets."""
    for last, drv in (("nand_fet", ("Q40", "3")), ("od", ("U40", "4"))):
        nl = _edit(_cm5_board(last), {"R41": ("33R", "R", "Device:R")},
                   {"WL_X": [("R41", "1", "")], "WL_nDIS1": [("R41", "2", "")]}, move={drv: "WL_X"})
        tx = _tx(T.judge({"B": nl}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")
        assert tx["ok"] is True and "R41 series" in tx["detail"], (last, tx)


def t_a_series_resistor_in_front_of_the_sa868_ptt_passes():
    """ACCEPTABLE (the reviewer's probe): the inverter drives PTT through 100 Ohm; the SA868's pin 5 was read as an
    active pin no document shows to be an input."""
    nl = _edit(_key_board(), {"R9": ("100R", "R", "Device:R")}, {"PTT_X": [("R9", "1", "")], "SA_PTT_n": [("R9", "2", "")]},
               move={("U13", "4"): "PTT_X"})
    tx = _tx(T.judge({"D": nl}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is True and "R9 series" in tx["detail"], tx


def t_a_pull_against_the_forced_level_is_held_to_what_the_gate_can_sink():
    """DEFECTIVE: a 0 Ohm link from +3V3 onto the enable the AND holds low, and a 470 Ohm pull-up (7 mA, above the
    4 mA every held logic sheet still guarantees its low level at). ACCEPTABLE: 10 kOhm, 0.33 mA."""
    base = _power_board({"and", "expander_sw"})
    for val, want, needle in (("0R", False, "0R link"), ("470", False, "7.0 mA"), ("10k", True, "")):
        tx = _lora(_edit(base, {"R50": (val, "R", "Device:R")}, {"LORA_EN": [("R50", "1", "")], "+3V3": [("R50", "2", "")]}))
        assert tx["ok"] is want and needle in tx["detail"], (val, tx)


def t_a_resistor_from_another_rail_onto_a_gated_rail_is_a_second_feed():
    """DEFECTIVE: a 0 Ohm link from +5V_DEV to the rail the switch gates keeps the radio powered with the switch off.
    ACCEPTABLE: a resistor from the gated rail to ground (a bleed) is not a feed."""
    base = _power_board({"and", "expander_sw"})
    tx = _lora(_edit(base, {"R60": ("0R", "R", "Device:R")}, {"+5V_X": [("R60", "1", "")], "+5V_DEV": [("R60", "2", "")]}))
    assert tx["ok"] is False and "joined to +5V_DEV through R60" in tx["detail"], tx
    assert _lora(_edit(base, {"R60": ("10k", "R", "Device:R")}, {"+5V_X": [("R60", "1", "")], "GND": [("R60", "2", "")]}))["ok"] is True


def t_a_compute_module_pull_up_behind_a_series_resistor_or_on_a_vdd_rail_fails():
    """DEFECTIVE (the reviewer's probes): a 10 kOhm pull-up between the open-drain element and a series resistor to
    pin 89, and one on the pin to a supply named VDD_3V3 with no '+'."""
    nl = _edit(_cm5_board("nand_fet"), {"R41": ("33R", "R", "Device:R"), "R40": ("10k", "R", "Device:R")},
               {"WL_X": [("R41", "1", ""), ("R40", "1", "")], "WL_nDIS1": [("R41", "2", "")], "+3V3": [("R40", "2", "")]},
               move={("Q40", "3"): "WL_X"})
    tx = _tx(T.judge({"B": nl}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")
    assert tx["ok"] is False and "pulled up on the carrier by R40" in tx["detail"], tx
    nl = _edit(_cm5_board("nand_fet"), {"R40": ("10k", "R", "Device:R")}, {"WL_nDIS1": [("R40", "1", "")], "VDD_3V3": [("R40", "2", "")]})
    tx = _tx(T.judge({"B": nl}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")
    assert tx["ok"] is False and "pulled up on the carrier by R40" in tx["detail"], tx


def t_resistor_values_read_their_unit_by_its_case():
    assert T._ohms("10k") == 1e4 and T._ohms("4k7") == 4700 and T._ohms("1M") == 1e6 and T._ohms("0R") == 0
    assert abs(T._ohms("2m shunt") - 0.002) < 1e-12 and T._ohms("100") == 100 and T._ohms("31.6k 1%") == 31600


# ---------------------------------------------------------------- RF-002 must read every board the walk writes for
# THE WALK'S RESULTS LANDED WHERE NO RULE READ THEM (review of the first fix-up, 26 September 2026). Since R4T-D22 they
# decide inhibit_chain_<letter> alone, and RF-002 applies where the fact rf_transmit holds, which is boards B and D.
# The 30 W PA and the QMX are judged on board A (their supply gates, J_PA and J_HF), the panel's line on A and C, and
# the classification of every part that names a radio on all six netlists, so a PA gate regressing to software-only
# drive on A would have changed inhibit_chain_a and nothing any rule reads. The registry is not r4t's to write; the
# row below is the change handed to its writer (drafts/r4-coverage-rows.yaml), and the tests prove what it does.
PROPOSED_RF002 = {"boards_affected": ["a", "b", "c", "d", "e", "p"], "condition": {"fact": "has_schematic", "op": "truthy"}}


def _a_tree(pa_gated):
    """A tree holding board A (with the P and E boards the SMBus fixture makes): its PA and QMX rails come from two
    LM5176 whose EN/UVLO pins are driven by the SN74LVC08A U26 from EMCON_HW; with pa_gated=False the PA's enable is
    driven by an I/O expander alone and U26's output is left on a net of its own."""
    import test_smbus_lead_contract as S
    ecad = S._tree(S.XH4, p_return="PACK_N", clamp_return="PACK_N")
    hts = "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm"
    # ROUND 6: the gates are two 74LVC1G08, which state Ioff (SCES217AA), each enable carries a 10 kOhm pull-down (board
    # A's R59 and R125) and the line's pull-down is 10 kOhm, so the good tree passes the pin currents and its gates
    # losing their own supply. Board A itself carries an SN74LVC08A (no Ioff) and R102 at 100 kOhm: see
    # t_board_a_pa_enable_with_its_pull_down and t_the_kit_emcon_line_with_the_shifter_remedy below.
    g1 = ("SN74LVC1G08DBVR AND: EMCON gate", "Package_TO_SOT_SMD:SOT-23-5")
    comps = {"U26A": g1, "U26B": g1,
             "U13": ("LM5176PWPR PA rail", hts), "U15": ("LM5176PWPR HF rail", hts),
             "U6": ("PCA9555PW 0x20", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm"),
             "J_PA": ("PA supply lead", "Connector:X"), "J_HF": ("QMX HF transceiver DC lead", "Connector:X"),
             "R102": ("10k", "R"), "R145": ("100k", "R"), "R59": ("10k", "R"), "R125": ("10k", "R")}
    nets = {"EMCON_HW": [("U26A", "1"), ("U26B", "1"), ("R102", "1")], "TX_INHIBIT_n": [("R145", "1")],
            "GND": [("R102", "2"), ("R145", "2"), ("U26A", "3"), ("U26B", "3"), ("J_PA", "2"), ("J_HF", "2"),
                    ("R59", "2"), ("R125", "2")],
            "+3V3": [("U26A", "5"), ("U26B", "5")], "VBAT": [("U13", "2"), ("U15", "2")],
            "PA_SW": [("U26A", "2"), ("U6", "4")], "HF_SW": [("U26B", "2"), ("U6", "5")],
            "HF_EN": [("U26B", "4"), ("U15", "1"), ("R125", "1")], "+13V8_PA": [("U13", "12"), ("J_PA", "1")],
            "+12V_HF": [("U15", "12"), ("J_HF", "1")]}
    if pa_gated:
        nets["PA_EN"] = [("U26A", "4"), ("U13", "1"), ("R59", "1")]
    else:
        nets["PA_EN"] = [("U13", "1"), ("U6", "6"), ("R59", "1")]; nets["PA_EN_UNUSED"] = [("U26A", "4")]
    S._write(ecad, "pcb-a-power", "a", comps, nets)
    return ecad


def _inhibit_chain_a(ecad):
    import json, subprocess
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_contracts.py"), ecad], cwd=ecad, capture_output=True,
                       text=True, timeout=300, env=dict(os.environ, VERDICT_DIR=os.path.join(ecad, "out")))
    p = os.path.join(ecad, "out", "inhibit_chain_a.verdict.json")
    assert os.path.isfile(p), r.stdout[-2000:] + r.stderr[-2000:]
    return json.load(open(p, encoding="utf-8")), r.stdout


def t_a_pa_gate_failure_on_board_a_decides_rf002_once_its_row_reads_every_board():
    """The reviewer's case, end to end. Board A's PA enable regresses from the EMCON AND gate to software-only drive:
    check_contracts turns inhibit_chain_a from PASS to FAIL. Under the RF-002 row handed to the registry writer,
    rules_lib.rules_for applies RF-002 to board A (and to every board the walk writes for, and to no board without a
    netlist), and rules_status.result_for reads that verdict as RF-002's result for board A: PASS, then FAIL. Under the
    registry at main 82dd1e4d the same failure reaches no rule, which is the gap."""
    import copy, rules_lib as R, rules_status as RS
    reg, facts = R.load(), R.facts()
    patched = copy.deepcopy(reg)
    rf = [r for r in patched["rules"] if r["id"] == "RF-002"][0]
    rf.update(copy.deepcopy(PROPOSED_RF002))
    errs, _w = R.validate(patched)
    assert not [e for e in errs if "RF-002" in e], errs
    letters = sorted(k for k, v in facts.items() if isinstance(v, dict) and not k.startswith("_"))
    reads = {l for l in letters if any(r["id"] == "RF-002" for r, _ in R.rules_for(l, patched, facts))}
    assert reads == {"a", "b", "c", "d", "e", "p"}, reads          # every board with a netlist, and not e5
    now = {l for l in letters if any(r["id"] == "RF-002" for r, _ in R.rules_for(l, reg, facts))}
    good, out_g = _inhibit_chain_a(_a_tree(True))
    bad, out_b = _inhibit_chain_a(_a_tree(False))
    assert good["verdict"] == "PASS", (good, out_g[-2500:])
    assert bad["verdict"] == "FAIL" and any("30 W VHF power amplifier" in x for x in bad.get("evidence") or []), (bad, out_b[-2500:])
    cov, m = RS.coverage(), {"evidence": {"epoch": ""}}
    assert RS.result_for(rf, "a", cov, {"inhibit_chain_a": good}, m, None)["result"] == RS.PASS
    res = RS.result_for(rf, "a", cov, {"inhibit_chain_a": bad}, m, None)
    assert res["result"] == RS.FAIL and "inhibit_chain_a FAIL" in res["why"], res
    if "a" not in now:     # the tree's own registry: the same failure decides nothing until the row lands
        assert not any(r["id"] == "RF-002" for r, _ in R.rules_for("a", reg, facts))


def t_the_tree_registry_applies_rf002_on_every_board_the_walk_writes_for():
    """The guard for the integrated tree: once the RF-002 row is in pcb_rules.yaml this holds; until then it SKIPS and
    says which boards' results decide no rule."""
    import rules_lib as R
    from harness import Skip
    reg, facts = R.load(), R.facts()
    letters = sorted(k for k, v in facts.items() if isinstance(v, dict) and not k.startswith("_"))
    now = {l for l in letters if any(r["id"] == "RF-002" for r, _ in R.rules_for(l, reg, facts))}
    want = set(PROPOSED_RF002["boards_affected"])
    if not want <= now:
        raise Skip("RF-002 applies on %s in this tree's pcb_rules.yaml, and tx_inhibit writes results for %s: the results "
                   "on %s decide no rule until the registry writer applies r4t's RF-002 row (boards_affected %s, "
                   "condition has_schematic)" % (",".join(sorted(now)), ",".join(sorted(want)),
                                                ",".join(sorted(want - now)), PROPOSED_RF002["boards_affected"]))
    assert "e5" not in now or facts.get("e5", {}).get("has_schematic"), now


# ---------------------------------------------------------------- round 6 (26 September 2026): the pins' own currents
# REVIEW OF THE SECOND FIX-UP, BLOCKING 1: the fail-safe model took every CMOS input as drawing no current. The kit's
# EMCON_HW carries six SN74LVC08A inputs on A and B (II 5 uA, SCAS283W 5.7, -40 to +85 C) and the recommended remedy
# adds three 74LVC1G07 (II 5 uA, SCES296AG); board C's buffer, unpowered, passes its IOFF (10 uA, Diodes DS35124).
def _kit(r102, r58, remedy=True, gates="08a"):
    """The kit's two asserted lines as the netlists at main faf8c981 carry them, with board B's shifters replaced by
    three 74LVC1G07 when `remedy` (and its STM32 pins and C's RP2040 pin off the line, as R4T-F4 and F5 ask).
    `gates`: "08a", the quad SN74LVC08A U26 on A and U19 and U20 on B as drawn (two inputs on A, four on B), or "1g",
    one SN74LVC1G08 per input, which states Ioff (round 6 second pass)."""
    idc = ("interconnect", "Connector:X", "Connector_Generic:Conn_02x13")
    a = {"J_AB1": idc, "J_MEZZ1": idc, "R102": (r102, "R", "Device:R"), "R145": PD}
    an = {"EMCON_HW": [("J_AB1", "15", ""), ("R102", "1", "")],
          "TX_INHIBIT_n": [("J_AB1", "16", ""), ("J_MEZZ1", "8", ""), ("R145", "1", "")],
          "+3V3": [], "GND": [("R102", "2", ""), ("R145", "2", "")]}
    b = {"J_AB1": idc, "J_PANEL": idc, "R58": (r58, "R", "Device:R"), "R59": PD}
    bn = {"EMCON_HW": [("J_AB1", "15", ""), ("J_PANEL", "8", ""), ("R58", "1", "")],
          "TX_INHIBIT_n": [("J_AB1", "16", ""), ("J_PANEL", "11", ""), ("R59", "1", "")], "+5V": [("J_PANEL", "1", "")],
          "+3V3_DEV": [], "GND": [("R58", "2", ""), ("R59", "2", "")]}

    def gate_in(comps, nets, rail, quads):
        # quads: {ref: [input pins on EMCON_HW]}, drawn as the quad or as one 1G08 per input
        for ref, pins in quads.items():
            if gates == "08a":
                comps[ref] = Q08; nets[rail].append((ref, "14", "")); nets["GND"].append((ref, "7", ""))
                nets["EMCON_HW"].extend((ref, p_, "") for p_ in pins)
            else:
                for i, _p in enumerate(pins):
                    r1 = "%s%s" % (ref, "ABCD"[i])
                    comps[r1] = AND1; nets[rail].append((r1, "5", "")); nets["GND"].append((r1, "3", ""))
                    nets["EMCON_HW"].append((r1, "1", ""))
    gate_in(a, an, "+3V3", {"U26": ["1", "4"]})
    gate_in(b, bn, "+3V3_DEV", {"U19": ["1", "9", "12"], "U20": ["1"]})
    if remedy:
        for sl in (1, 2, 3):
            u, far, rail = "U%d06" % sl, "W_DIS_%d" % sl, "+3V3_S%dA" % sl
            b[u] = OD1; b["R%d37" % sl] = ("10k", "R", "Device:R")
            bn["EMCON_HW"].append((u, "2", "")); bn.setdefault(far, []).extend([(u, "4", ""), ("R%d37" % sl, "1", "")])
            bn.setdefault(rail, []).extend([(u, "5", ""), ("R%d37" % sl, "2", "")]); bn["GND"].append((u, "3", ""))
    c = {"SW_EMCON": TOGGLE, "R14": ("10k", "R", "Device:R"), "U9": U17, "U1": ("TLV75733PDBV 3.3 V LDO", "SOT-23-5", "X:Y"),
         "J_PANEL": idc}
    cn = {"TX_INHIBIT_n": [("SW_EMCON", "1", ""), ("R14", "1", ""), ("U9", "2", ""), ("J_PANEL", "11", "")],
          "EMCON_HW": [("U9", "4", ""), ("J_PANEL", "8", "")], "+3V3": [("R14", "2", ""), ("U9", "5", ""), ("U1", "5", "")],
          "+5V": [("J_PANEL", "1", ""), ("U1", "1", "")], "GND": [("SW_EMCON", "2", ""), ("U9", "3", ""), ("U1", "2", "")]}
    d = {"J_HARN1": idc, "R2": PD, "U12": AND1}
    dn = {"TX_INHIBIT_n": [("J_HARN1", "8", ""), ("R2", "1", ""), ("U12", "2", "")], "+3V3_D8": [("U12", "5", "")],
          "GND": [("R2", "2", ""), ("U12", "3", "")], "PTT_ANY": [("U12", "1", "")], "KEY": [("U12", "4", "")]}
    return {"A": _nl(a, an), "B": _nl(b, bn), "C": _nl(c, cn), "D": _nl(d, dn)}


def _worst(detail):
    """The highest voltage a line result's detail names."""
    import re as _re
    vs = [float(x) for x in _re.findall(r"(?:rises to|reads) (\d+\.\d+) V", detail)]
    return max(vs) if vs else None


def t_the_kit_emcon_line_with_the_shifter_remedy_needs_smaller_pull_downs():
    """The 74LVC1G07 remedy (three more inputs on B) with each board's pull-down, every other part taken powered or
    unpowered, whichever is worse (round 6 second pass):
    DEFECTIVE at the kit's 100 kOhm: nine inputs and C's IOFF on 52.5 kOhm (100 kOhm at +5 percent, both boards).
    UNDECIDED at 10 kOhm on both boards with the quad SN74LVC08A as drawn (the review of round 6, blocking 1): it states no
    Ioff, and A's U26 can be unpowered while B reads the line (A makes +3V3 apart from the +5V_DEV it hands to B), or
    B's U19 and U20 while A does.
    ACCEPTABLE at 10 kOhm on both with one SN74LVC1G08 per input, but only just: the worst state is J_AB1 unplugged, the
    panel unpowered and one slot rail up, where U106 reads (II 5 uA) while the other two 1G07 and B's four 1G08 pass
    their Ioff (6 x 10 uA) and C's U9 its IOFF (10 uA): 75 uA x 10.5 kOhm = 0.79 V against 0.8 V.
    ACCEPTABLE WITH MARGIN at 4.7 kOhm 1% on B and 10 kOhm on A: 75 uA x 4.75 kOhm = 0.36 V.
    DEFECTIVE when only one board changes: each board's own pull-down holds its own inputs alone with its ribbon out
    (A alone at 100 kOhm: 2 x 5 uA x 105 kOhm = 1.05 V)."""
    line = _line_of(_kit("100k", "100k", gates="1g"))
    assert line["ok"] is False and "U106 pin 2 (" in line["detail"], line
    line = _line_of(_kit("10k", "10k", gates="08a"))
    assert line["ok"] is None and "states no Ioff" in line["detail"] and "may be unpowered while the line is read" \
        in line["detail"], line
    line = _line_of(_kit("10k", "10k", gates="1g"))
    assert line["ok"] is True, line
    fs = T.fail_safe(_kit("10k", "10k", gates="1g"), "EMCON_HW")
    assert not fs["fail"] and not fs["undecided"], fs
    line = _line_of(_kit("10k", "4.7k 1%", gates="1g"))
    assert line["ok"] is True, line
    line = _line_of(_kit("10k", "100k", gates="1g"))
    assert line["ok"] is False and "J_AB1 unplugged" in line["detail"], line
    kit = _kit("100k", "10k", gates="1g")
    assert _line_of(kit)["ok"] is False, _line_of(kit)
    a_alone = T._fs_bound(kit, "EMCON_HW", [("A", "EMCON_HW")], set(), {0}, {})     # J_AB1 (MATES[0]) unplugged
    assert a_alone["ok"] is False and "rises to 1.05 V" in a_alone["text"] and "A's +3V3 up" in a_alone["text"], a_alone


def t_the_bound_covers_every_whole_board_state_the_review_named():
    """DEFECTIVE (review of round 6, blocking 1, probe5): the 47k/22k kit with B's gates as SN74LVC1G08. Round 6 took
    every board but the panel as powered, read 0.67 V at worst and PASSED, while boards B and C unpowered with A powered
    and every ribbon plugged reads 1.05 V (the review's figure, with B's two 1G08 of its probe) and FAILS. The tool now
    FAILS it and names that state. The per-part bound is at least every whole-board state: each subset of the carrier
    boards unpowered, solved exactly, reads no higher than the bound's reading for the same ribbons."""
    kit = _kit("47k", "22k", gates="1g")
    line = _line_of(kit)
    assert line["ok"] is False and "boards B, C unpowered and A powered" in line["detail"], line
    s, cond = "EMCON_HW", [(k, "EMCON_HW") for k in "ABC"]
    src = {(k, ref): why for k, n in cond for ref, why in T._line_sources(kit[k], n)}
    bound = T._fs_bound(kit, s, cond, {"C"}, set(), src)
    assert bound["ok"] is False and bound["v"] > 0.8, bound
    for down in ({"C"}, {"A", "C"}, {"B", "C"}):
        e = T._fs_state(kit, s, cond, down, set(), src)
        assert e["ok"] is False and e["v"] <= bound["v"] + 1e-9, (down, e, bound["v"])
    e = T._fs_state(kit, s, cond, {"B", "C"}, set(), src)
    assert "the whole-board state: boards B, C unpowered and A powered" in e["text"], e
    # the review's own probe5, as it built it: the quads' values changed to 74LVC1G08 on SOT-23-5 with their nets kept,
    # so B keeps two inputs the 1G08 pin map knows (U19 pin 1, U20 pin 1). Round 6 read PASS (worst 0.67 V); the review
    # measured 1.05 V with B and C unpowered and A powered, nominal values; at the adverse tolerance it is 1.10 V.
    k5 = _kit("47k", "22k")
    for ref in ("U19", "U20"):
        k5["B"]["comps"][ref] = {"value": "74LVC1G08 AND", "fp": "Package_TO_SOT_SMD:SOT-23-5", "lib": "X:Y"}
    line = _line_of(k5)
    assert line["ok"] is False and "boards B, C unpowered and A powered 1.10 V" in line["detail"], line
    # THE SAME CLAIM FOR A READER WHOSE SUPPLY NET HAS NO '+' (round 6 third pass, the review of round 6's second pass,
    # blocking 1, probe_bound_vs_exact): with U19 on VCC_X and no pull-down the bound read PASS ("no gate that can be
    # powered reads EMCON_HW") while the whole-board state C unpowered, B powered FAILED (floating). Every whole-board
    # state that fails fails the bound too, and none reads higher than it.
    for pd in (None, "100k"):
        kit = _panel({}, {}, pull_down=pd, u19_rail="VCC_X")
        cond = [(k, s) for k in "BC"]
        src = {(k, ref): why for k, n in cond for ref, why in T._line_sources(kit[k], n)}
        bound = T._fs_bound(kit, s, cond, {"C"}, set(), src)
        assert not bound.get("na") and bound["ok"] is (False if pd is None else None), (pd, bound)
        for down in ({"C"}, {"B", "C"}):
            e = T._fs_state(kit, s, cond, down, set(), src)
            if e.get("na"): continue
            assert e["ok"] is not False or bound["ok"] is False, (pd, down, e, bound)
            assert e.get("v") is None or (bound.get("v") is not None and e["v"] <= bound["v"] + 1e-9), (pd, down, e, bound)


def t_the_kit_emcon_line_as_drawn_fails_on_its_inputs_alone():
    """DEFECTIVE (the reviewer's arithmetic, on the line as drawn with the shifters and the controllers taken off):
    the six SN74LVC08A inputs alone lift EMCON_HW to 30 uA x 52.5 kOhm = 1.58 V with the panel unplugged, before C's
    IOFF."""
    line = _line_of(_kit("100k", "100k", remedy=False))
    assert line["ok"] is False and "rises to" in line["detail"], line
    fs = T.fail_safe(_kit("100k", "100k", remedy=False), "EMCON_HW")
    assert any("J_PANEL unplugged" in x and "rises to 1.58" in x for x in fs["fail"]), fs["fail"]


def t_the_kit_tx_inhibit_line_holds_with_the_pin_currents():
    """ACCEPTABLE: TX_INHIBIT_n's three 100 kOhm (35 kOhm together at +5 percent) hold board D's AND input (5 uA) and
    C's unpowered buffer input (IOFF 10 uA) at 0.53 V, and D alone with the harness out (5 uA on 105 kOhm) at 0.53 V."""
    kit = _kit("10k", "10k")
    assert _line_of(kit, "TX_INHIBIT_n")["ok"] is True, _line_of(kit, "TX_INHIBIT_n")
    line = [(k, n) for k in "ABCD" for n in ("TX_INHIBIT_n",)]
    st = T._fs_state(kit, "TX_INHIBIT_n", line, {"C"}, set(), {("C", "SW_EMCON"): "the toggle", ("C", "U9"): "buffer"})
    assert st["ok"] is True and "reads 0.53 V" in st["text"] and "U12 pin 2 (II" in st["text"] \
        and "U9 pin 2 unpowered (Ioff" in st["text"], st


def t_an_undrawn_orientation_is_not_a_failure_on_its_own():
    """UNDECIDED, not FAIL: a diode on A1/A2 pins from a live rail onto EMCON_HW lifts the line only if it points the
    way its drawing does not say."""
    b = _panel({"D30": ("BAT54 wired-OR", "SOT-23", "Device:D_TVS")},
               {"EMCON_HW": [("D30", "1", "A1")], "+3V3_X": [("D30", "2", "A2")]})
    line = _line_of(b)
    assert line["ok"] is None and "orientation is not drawn" in line["detail"], line


# ---------------------------------------------------------------- R4T-F9: a gate that loses its own supply
def t_board_b_e22_enable_with_no_pull_down_fails_when_its_gate_loses_its_supply():
    """DEFECTIVE (board B's LIME_EN, RB_EN and E22_EN): the AND runs on +3V3 and the load switch takes +5V_DEV, so
    with +3V3 down the enable is held by nothing, which TI's sheet forbids ('This pin cannot be left floating').
    ACCEPTABLE with a 10 kOhm pull-down and a gate that states Ioff: 10.1 uA x 10 kOhm = 0.10 V against VENF 1.08 V."""
    tx = _lora(_power_board({"and", "expander_sw"}, en_pull=None))
    assert tx["ok"] is False and "LORA_EN floats" in tx["detail"] and "U5's supply +3V3 down" in tx["detail"], tx
    tx = _lora(_power_board({"and", "expander_sw"}))
    assert tx["ok"] is True, tx


def t_a_switch_fed_from_the_gates_own_rail_needs_no_pull_down():
    """ACCEPTABLE (board B's E72_EN, U22 on +3V3_DEV): when the switch's own input is the rail the gate loses, the
    radio loses its supply with it and the state is not one it can transmit in."""
    nl = _edit(_power_board({"and", "expander_sw"}, en_pull=None), move={("U21", "6"): "+3V3"})
    assert _lora(nl)["ok"] is True, _lora(nl)


def t_board_a_pa_enable_with_its_pull_down():
    """Board A's PA path: EMCON_HW into an AND on +3V3, its output PA_EN on the LM5176's EN/UVLO (pin 1, VIN on VBAT),
    and R59 10 kOhm to ground. ACCEPTABLE with a gate that states Ioff (SN74LVC1G08, 10 uA; the LM5176 sources at most
    3 uA in standby plus 4.25 uA of dIHYS(OP) while it still counts as on, 7.25 uA at the threshold from above, round 6
    second pass): 17.25 uA x 10.5 kOhm = 0.18 V against VEN(OP) 1.17 V. UNDECIDED with the SN74LVC08A board A carries,
    whose sheet has no Ioff row and so says nothing of what it does unpowered. DEFECTIVE with no R59: PA_EN floats."""
    hts = "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm"

    def tree(gate, r59=True):
        comps = {"SW1": TOGGLE, "R102": ("10k", "R", "Device:R"), "U13": ("LM5176PWPR PA rail", hts, "X:Y"),
                 "J_PA": ("PA supply lead", "Connector:X", "X:Y"), "U6": EXP}
        nets = {"EMCON_HW": [("SW1", "1", ""), ("R102", "1", "")], "GND": [("SW1", "2", ""), ("R102", "2", ""), ("J_PA", "2", "")],
                "PA_SW": [("U6", "4", "IO0_0")], "PA_EN": [("U13", "1", "EN/UVLO")], "VBAT": [("U13", "2", "VIN")],
                "+13V8_PA": [("U13", "12", "VOSNS"), ("J_PA", "1", "")], "+3V3": []}
        if gate == "1g08":
            comps["U26"] = AND1
            nets["EMCON_HW"].append(("U26", "1", "")); nets["PA_SW"].append(("U26", "2", "")); nets["PA_EN"].append(("U26", "4", ""))
            nets["+3V3"].append(("U26", "5", "")); nets["GND"].append(("U26", "3", ""))
        else:
            comps["U26"] = Q08
            nets["EMCON_HW"].append(("U26", "1", "")); nets["PA_SW"].append(("U26", "2", "")); nets["PA_EN"].append(("U26", "3", ""))
            nets["+3V3"].append(("U26", "14", "")); nets["GND"].append(("U26", "7", ""))
        if r59:
            comps["R59"] = ("10k", "R", "Device:R"); nets["PA_EN"].append(("R59", "1", "")); nets["GND"].append(("R59", "2", ""))
        return _nl(comps, nets)
    table = [dict(name="test PA", options=[dict(board="A", ref="J_PA", kind="power")])]
    ok = _tx(T.judge({"A": tree("1g08")}, table=table, accessories=[], receivers=[], owed=[]), "test PA")
    assert ok["ok"] is True, ok
    nl = tree("1g08")
    # the reader's own supply is its input VBAT (R4T-D41; its output +13V8_PA is what EMCON switches)
    assert T._supply_nets(nl, "U13") == ["VBAT"], T._supply_nets(nl, "U13")
    st = dict(rail_up=lambda kk, nn: nn != "+3V3", board_up=lambda kk: True, cut=set(), sources=set(),
              domain=frozenset(("A", r) for r in T._supply_nets(nl, "U13")))
    net = T._network({"A": nl}, [("A", "PA_EN")], 0, st)
    v = T._solve_net(net)[0][("A", "PA_EN")]
    assert abs(v - 17.25e-6 * 10.5e3) < 1e-3 and "A U13 enable (LM5176 buck-boost controller) 7.2 uA" in net["leaks"], (v, net["leaks"])
    und = _tx(T.judge({"A": tree("08a")}, table=table, accessories=[], receivers=[], owed=[]), "test PA")
    assert und["ok"] is None and "states no Ioff" in und["detail"] and "PA_EN sits at" in und["detail"], und
    bad = _tx(T.judge({"A": tree("1g08", r59=False)}, table=table, accessories=[], receivers=[], owed=[]), "test PA")
    assert bad["ok"] is False and "PA_EN floats" in bad["detail"], bad


def t_the_sa868_keying_pin_when_its_logic_loses_its_supply():
    """Board D's SA_PTT_n: U12 and U13 run on +3V3_D8, which the LDO U1 makes, and the SA868 on +5V_SA.
    DEFECTIVE with no pull (board D as drawn): SA_PTT_n floats with the exciter powered. DEFECTIVE with a pull-up on
    +3V3_D8: it dies with the driver. UNDECIDED with a pull-up on +5V_SA: the SA868 v1.3 sheet states neither an input
    current nor a '1' level for PTT. ACCEPTABLE when the keying logic runs on the exciter's own rail."""
    tx = _tx(T.judge({"D": _key_board(logic_rail="+3V3_D8")}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is False and "SA_PTT_n floats" in tx["detail"] and "U13's supply +3V3_D8 down" in tx["detail"], tx
    tx = _tx(T.judge({"D": _key_board(logic_rail="+3V3_D8", ptt_pull=("10k", "+3V3_D8"))}, table=_KEY, accessories=[],
                     receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is False and "SA_PTT_n floats" in tx["detail"], tx
    tx = _tx(T.judge({"D": _key_board(logic_rail="+3V3_D8", ptt_pull=("10k", "+5V_SA"))}, table=_KEY, accessories=[],
                     receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is None and "maker states no input" in tx["detail"], tx
    assert _tx(T.judge({"D": _key_board()}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")["ok"] is True


def t_a_compute_module_pin_whose_element_can_lose_its_supply_fails():
    """DEFECTIVE: the S-01 shapes with the NAND or the open-drain buffer on a carrier rail (+3V3) rather than the
    module's own 3.3 V. With that rail down, the FET's gate floats, or the pin is held only by the module's own
    1.8 kOhm pull-up, which is the pin 'left floating': Wi-Fi on (CM5 datasheet, pin 89)."""
    tx = _tx(T.judge({"B": _cm5_board("nand_fet", elem_rail="+3V3")}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")
    assert tx["ok"] is False and "WL_GATE floats" in tx["detail"], tx
    tx = _tx(T.judge({"B": _cm5_board("od", elem_rail="+3V3")}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")
    assert tx["ok"] is False and "its maker's own pull" in tx["detail"], tx


def t_the_report_does_not_print_pass_for_a_result_that_needed_an_absent_board():
    """Review of the second fix-up, minor 4: a line whose other board's netlist is absent printed PASS."""
    import io, contextlib
    b = _panel({}, {})
    d = tempfile.mkdtemp(prefix="txr-")
    r = T.judge({"B": b["B"], "C": None}, table=[], accessories=[], receivers=[], owed=[])
    line = _line(r)
    assert line.get("absent") == ["C"], line
    buf = io.StringIO()
    import boardtable
    saved = T.parse_netlist, boardtable.letter_for
    try:
        T.parse_netlist = lambda p: b["B"] if p.endswith("b.net") else None
        boardtable.letter_for = lambda n: {"b.kicad_pcb": "b", "c.kicad_pcb": "c"}.get(n)
        with contextlib.redirect_stdout(buf):
            T.report([os.path.join(d, "b.net"), os.path.join(d, "c.net")])
    finally:
        T.parse_netlist, boardtable.letter_for = saved
    out = buf.getvalue()
    assert "UNJUDGED  the asserted line EMCON_HW" in out and "(absent: C)" in out, out[:600]


# ---------------------------------------------------------------- round 6, second pass (26 September 2026)
def t_an_enable_whose_current_at_the_threshold_no_sheet_bounds_is_undecided():
    """UNDECIDED, not PASS (review of round 6, minor 1): the AP64500's IEN is 1 to 2 uA at VEN 1 V and 5.5 uA TYPICAL,
    no maximum, at VEN 1.5 V (Diodes DS41979 Rev. 5-2). An enable dragged down from ON meets the second figure at the
    threshold, so its hold with the gate's supply down is not bounded. The same shape on a TPS22810 PASSES."""
    ap = ("AP64500SP-13 5 A buck", "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm", "X:Y")
    comps = {"U12": LORA, "U21": ap, "L1": ("3.3uH", "L", "Device:L"), "SW1": TOGGLE, "U5": AND1, "U6": EXP,
             "R70": ("10k 1%", "R", "Device:R")}
    nets = {"+5V_X": [("U12", "9", "VCC"), ("L1", "2", "")], "LX": [("U21", "8", "SW"), ("L1", "1", "")],
            "+5V_DEV": [("U21", "2", "VIN")], "GND": [("U12", "1", "GND"), ("U21", "7", "GND"), ("SW1", "2", ""),
                                                      ("U5", "3", ""), ("R70", "2", "")],
            "+3V3": [("U5", "5", "")], "EMCON_HW": [("SW1", "1", ""), ("U5", "1", "")], "SW_EN": [("U5", "2", ""), ("U6", "4", "IO0_0")],
            "LORA_EN": [("U5", "4", ""), ("U21", "3", "EN"), ("R70", "1", "")]}
    tx = _tx(T.judge({"B": _nl(comps, nets)}, table=TX_POWER, accessories=[], receivers=[], owed=[]), "test LoRa")
    assert tx["ok"] is None and "U21 enable (AP64500 buck): its sheet bounds no enable current" in tx["detail"], tx
    assert _lora(_power_board({"and", "expander_sw"}))["ok"] is True


def t_a_level_shifter_whose_far_side_holds_nothing_up_is_undecided_for_its_off_state():
    """UNDECIDED, not PASS (round 6 second pass): a 2N7002 with its source on EMCON_HW, its gate on a slot rail and its
    drain on a net pulled DOWN. With the rail up its channel only joins the line to another pull-down; with the rail
    lost on its own the channel is off and passes an off-state current the JSCJ sheet states at 25 C only. Every
    reader-state of the line is otherwise under VIL. A 74LVC1G07 in its place PASSES."""
    b = _panel({"Q206": FET, "R237": ("10k", "R", "Device:R")},
               {"EMCON_HW": [("Q206", "2", "S")], "+3V3_S2A": [("Q206", "1", "G")],
                "FAR": [("Q206", "3", "D"), ("R237", "1", "")], "GND": [("R237", "2", "")]})
    line = _line_of(b)
    assert line["ok"] is None and "with its gate rail +3V3_S2A lost on its own the channel is off" in line["detail"], line


def t_resistor_tolerance_and_rails_are_taken_the_adverse_way():
    """R4T-D36: a pull to a fixed node at the end of its tolerance that hurts, 5 percent where the value states none,
    and a rail 5 percent high against a net held low. Here one input (5 uA) on a pull-down alone, and a 1 MOhm pull-up
    from +3V3 against 10 kOhm."""
    assert T._tol("10k") == 0.05 and T._tol("62k 1%") == 0.01 and T._tol("5mOhm 1% 2512 (shunt)") == 0.01
    comps = {"U19": AND1, "R58": ("10k 1%", "R", "Device:R"), "R60": ("1M", "R", "Device:R")}
    nets = {"EMCON_HW": [("U19", "1", ""), ("R58", "1", ""), ("R60", "1", "")], "+3V3_DEV": [("U19", "5", "")],
            "+3V3": [("R60", "2", "")], "GND": [("U19", "3", ""), ("R58", "2", "")]}
    nl = _nl(comps, nets)
    st = dict(rail_up=lambda kk, nn: True, board_up=lambda kk: True, cut=set(), sources=set())
    net = T._network({"B": nl}, [("B", "EMCON_HW")], 0, st)
    v = T._solve_net(net)[0][("B", "EMCON_HW")]
    rd, ru, vr = 10e3 * 1.01, 1e6 * 0.95, 3.3 * 1.05
    want = (5e-6 + vr / ru) / (1 / rd + 1 / ru)
    assert abs(v - want) < 1e-6, (v, want)
    # LEVEL 1 (round 6 third pass, the review of round 6's second pass, minor): a net held HIGH, as own_supply() holds
    # SA_PTT_n and a switch-to-ground's gate. Its pull-up toward the held level is taken at +tol (weaker), its pull-down
    # against it at -tol (stronger), the rail 5 percent LOW, and the input's current out of the net: board D's round-6
    # divider, R88 1.2k 1% from +5V_SA and R89 2k (5 percent where the value states none) to ground, with a 74LVC1G08
    # input (II 5 uA) on it.
    comps = {"U14": AND1, "R88": ("1.2k 1%", "R", "Device:R"), "R89": ("2k", "R", "Device:R")}
    nets = {"SA_PTT_n": [("U14", "1", ""), ("R88", "2", ""), ("R89", "1", "")], "+5V_SA": [("R88", "1", "")],
            "+3V3_D8": [("U14", "5", "")], "GND": [("U14", "3", ""), ("R89", "2", "")]}
    net = T._network({"D": _nl(comps, nets)}, [("D", "SA_PTT_n")], 1, st)
    v = T._solve_net(net)[0][("D", "SA_PTT_n")]
    ru, rd, vr = 1.2e3 * 1.01, 2e3 * 0.95, 5.0 * 0.95
    want = (vr / ru - 5e-6) / (1 / ru + 1 / rd)
    assert abs(v - want) < 1e-6, (v, want)


def t_an_open_drain_output_emcon_releases_is_judged_on_what_holds_its_net():
    """Board D's round-6 SA_PTT_n: U13 an open-drain 74LVC1G06 on +3V3_D8, R88 1.2k from +5V_SA and R89 2k to ground.
    Under EMCON, KEY is low and U13 RELEASES the pin, so the divider sets it (3.13 V, receive). The walk used to stop at a
    released output and read "EMCON does not reach it", a false FAIL. Now: UNDECIDED, because the SA868 v1.3 sheet
    states no '1' level for PTT and the LVC1G06 sheet states no off-state output current while powered (only Ioff, at
    VCC 0). DEFECTIVE with nothing pulling the released pin (it is not reached), and with a divider that leaves it
    between VIL and VIH."""
    tx = _tx(T.judge({"D": _key_board(logic_rail="+3V3_D8", od=True, divider=("1.2k", "2k"))}, table=_KEY, accessories=[],
                     receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is None and "U13 INV_OD 2->4 released, held at 3.12 V by R88 1.2k to +5V_SA, R89 2k to GND" \
        in tx["detail"] and "the open-drain U13 is released" in tx["detail"] and "its maker states no input threshold" \
        in tx["detail"] and "EMCON does not reach it" not in tx["detail"], tx
    tx = _tx(T.judge({"D": _key_board(logic_rail="+3V3_D8", od=True)}, table=_KEY, accessories=[], receivers=[], owed=[]),
             "test SA868")
    assert tx["ok"] is False and "EMCON does not reach it" in tx["detail"], tx
    tx = _tx(T.judge({"D": _key_board(logic_rail="+3V3_D8", od=True, divider=("10k", "3.3k"))}, table=_KEY,
                     accessories=[], receivers=[], owed=[]), "test SA868")
    assert tx["ok"] is False and "EMCON does not reach it" in tx["detail"], tx


def t_an_open_drain_output_released_onto_an_enable_with_a_pull_up_turns_the_radio_on():
    """DEFECTIVE: a 74LVC1G07 whose input EMCON holds low drives the enable low; one whose input EMCON holds HIGH
    releases it, and a pull-up then turns the switch ON under EMCON."""
    nl = _power_board({"expander_sw"}, en_pull=None)
    nl = _edit(nl, comps={"U5": OD1, "U7": INV1, "R70": ("10k", "R", "Device:R")},
               nets={"EMCON_HW": [("U7", "2", "")], "INV": [("U7", "4", ""), ("U5", "2", "")],
                     "LORA_EN": [("U5", "4", ""), ("R70", "1", "")], "+3V3": [("U5", "5", ""), ("U7", "5", ""), ("R70", "2", "")],
                     "GND": [("U5", "3", ""), ("U7", "3", "")]})
    tx = _lora(nl)
    assert tx["ok"] is False and "EMCON does not force off" in tx["detail"], tx


# ---------------------------------------------------------------- round 6, third pass (26 September 2026)
# THE REVIEW OF ROUND 6'S SECOND PASS, BLOCKING 1 (R4T-D41, R4T-F14): a part's supply was read only from nets whose names
# start with '+', so a reader running from VBAT, VCC_X or 3V3_DEV was never judged and a line with nothing holding it
# read PASS; and a supply named without '+' was walked as a signal, so a pull-up to it lifted nothing. Each fixture
# below read PASS on the second pass's tool (e88aa46b) and reads as asserted now.
def t_a_reader_whose_supply_net_has_no_plus_is_judged():
    """DEFECTIVE with no pull-down: the review's probe_norail, U19 (a 74LVC1G08) on VCC_X or 3V3_DEV, whose VCC pin
    (pin 5, SCES217AA) is its supply whatever the net is called: EMCON_HW floats at its input with the panel out.
    UNDECIDED, not PASS, with R58 10 kOhm: the line reads 0.16 V, but the LVC VIL of 0.8 V is stated for VCC 3 V to
    3.6 V and the supply's name states no voltage (R4T-D39)."""
    for rail in ("VCC_X", "3V3_DEV"):
        line = _line_of(_panel({}, {}, pull_down=None, u19_rail=rail))
        assert line["ok"] is False and "floats at B U19 pin 1" in line["detail"], (rail, line)
        line = _line_of(_panel({}, {}, pull_down="10k", u19_rail=rail))
        assert line["ok"] is None and "U19 pin 1 (VCC not named)" in line["detail"] \
            and "with B's %s up" % rail in line["detail"], (rail, line)


def t_a_reader_with_no_supply_pin_on_the_netlist_is_its_own_domain():
    """DEFECTIVE with no pull-down, UNDECIDED with 10 kOhm: U19's VCC pin left unconnected on the netlist. The bound
    judges it in a run of its own (R4T-D41) instead of dropping it with the empty domain."""
    for pd, want in ((None, False), ("10k", None)):
        kit = _panel({}, {}, pull_down=pd)
        kit["B"] = _edit(kit["B"], move={("U19", "5"): "unconnected-(U19-VCC-Pad5)"})
        line = _line_of(kit)
        assert line["ok"] is want, (pd, line)
    assert "floats at B U19 pin 1" in _line_of(_panel({}, {}, pull_down=None, u19_rail="unconnected-(U19-VCC-Pad5)"))["detail"]
    assert "with B's U19 powered (none of its supply pins is on the netlist)" in line["detail"], line


def _vbat_switch(pull_down, vin="VBAT", vout="LORA_5V"):
    """The review's probe_e2e: board B with a TPS22810 whose EN/UVLO sits straight on EMCON_HW, its VIN on `vin` and
    its VOUT (`vout`) powering the E22, and board C as the kit has it."""
    comps = {"J_PANEL": ("panel ribbon", "Connector:X", "Connector_Generic:Conn_02x13"), "R59": ("33k", "R", "Device:R"),
             "U21": LSW, "U12": LORA}
    nets = {"EMCON_HW": [("J_PANEL", "8", ""), ("U21", "5", "EN/UVLO")], "TX_INHIBIT_n": [("J_PANEL", "11", ""), ("R59", "1", "")],
            "+5V": [("J_PANEL", "1", "")], "GND": [("R59", "2", ""), ("U21", "4", "GND"), ("U12", "1", "GND")],
            vin: [("U21", "6", "VIN")], vout: [("U21", "1", "VOUT"), ("U12", "9", "VCC")]}
    if pull_down:
        comps["R58"] = (pull_down, "R", "Device:R"); nets["EMCON_HW"].append(("R58", "1", "")); nets["GND"].append(("R58", "2", ""))
    return {"B": _nl(comps, nets), "C": _panel({}, {})["C"]}


def t_a_switch_enable_on_the_line_whose_input_has_no_plus_is_judged():
    """DEFECTIVE: the review's probe_e2e, a TPS22810 on VBAT with VOUT LORA_5V and EN/UVLO on EMCON_HW, no pull-down.
    With the panel out the enable floats, which TI forbids (SLVSDH0C 9.3.1), so the line and the LoRa FAIL. ACCEPTABLE
    with R58 10 kOhm: C's U9 at IOFF (10 uA) and the enable's 0.1 uA on 10.5 kOhm, 0.11 V against VENF 1.08 V."""
    r = T.judge(_vbat_switch(None), table=TX_POWER, accessories=[], receivers=[], owed=[])
    assert _line(r)["ok"] is False and "floats at B U21 enable" in _line(r)["detail"], _line(r)
    assert _tx(r, "test LoRa")["ok"] is False and "its line EMCON_HW fails" in _tx(r, "test LoRa")["detail"], _tx(r, "test LoRa")
    r = T.judge(_vbat_switch("10k"), table=TX_POWER, accessories=[], receivers=[], owed=[])
    assert _line(r)["ok"] is True and _tx(r, "test LoRa")["ok"] is True, (_line(r), _tx(r, "test LoRa"))


def t_a_switch_readers_domain_is_its_input_rail_not_its_output():
    """The review of round 6's second pass, minor: a switch reader's domain was every '+' rail on it, its OUTPUT
    included, so in the run where EMCON holds that output off a part fed only from the output was taken powered (II)
    rather than at the worse of its two states. U21's EN/UVLO reads the line from +5V_DEV; U30, a 74LVC1G08 on U21's
    output +3V3_LORA, is then 'either' (Ioff 10 uA, SCES217AA), not 'on' (II 5 uA)."""
    kit = _panel({"U21": LSW, "U30": AND1},
                 {"EMCON_HW": [("U21", "5", "EN/UVLO"), ("U30", "1", "")], "+5V_DEV": [("U21", "6", "VIN")],
                  "+3V3_LORA": [("U21", "1", "VOUT"), ("U30", "5", "")], "GND": [("U21", "4", "GND"), ("U30", "3", "")]})
    s = "EMCON_HW"; cond = [(k, s) for k in "BC"]
    src = {(k, ref): why for k, n in cond for ref, why in T._line_sources(kit[k], n)}
    base = T._fs_base(kit, cond, {"C"}, set(), src)
    net0 = T._network(kit, cond, 0, dict(base, domain=frozenset()))
    doms = {lab: d for d, items in net0["cands"].items() for _x, lab in items}
    assert doms["B U21 enable"] == frozenset({("B", "+5V_DEV")}), doms
    net = T._network(kit, cond, 0, dict(base, domain=doms["B U21 enable"]))
    assert "B U30 pin 1 (Ioff, 74LVC1G08 AND, powered or not) 10.0 uA" in net["leaks"], net["leaks"]


def t_a_pull_up_to_a_supply_whose_name_has_no_plus_is_not_ignored():
    """UNDECIDED, not PASS: a 10 kOhm pull-up from EMCON_HW to 3V3_AUX (a supply by its name), and one to LOGIC_PWR (a
    supply because a 74LVC1G08's VCC pin sits on it). Both nets used to be walked as signals holding nothing, so the
    pull-up lifted nothing; a supply whose name states no voltage now leaves the line UNDECIDED, in the census and in
    the fail-safe states."""
    for rail, extra_c, extra_n in (("3V3_AUX", {}, {}),
                                   ("LOGIC_PWR", {"U31": AND1}, {"GND": [("U31", "3", "")], "X1": [("U31", "1", "")]})):
        comps = dict({"R60": ("10k", "R", "Device:R")}, **extra_c)
        nets = dict({"EMCON_HW": [("R60", "1", "")], rail: [("R60", "2", "")] + ([("U31", "5", "")] if extra_c else [])}, **extra_n)
        line = _line_of(_panel(comps, nets))
        assert line["ok"] is None and "a pull to %s through R60" % rail in line["detail"] \
            and "ties it to %s, whose voltage its name does not state" % rail in line["detail"], (rail, line)
    # a name that also carries a control word is the signal EMCON drives, not a supply (EN_3V3, PWR_ON_5V), unless a VCC
    # or VIN pin sits on it; a '+' rail is always one
    is_supply = T._supply_test({"B": _panel({}, {})["B"]})
    assert [is_supply("B", n) for n in ("3V3_AUX", "VCC_X", "EN_3V3", "PWR_ON_5V", "+3V3_DEV", "EMCON_HW", "GND")] == \
        [True, True, False, False, True, False, False]
    assert T._supply_test({"B": _panel({}, {}, u19_rail="EN_3V3")["B"]})("B", "EN_3V3") is True


def t_a_link_from_a_supply_whose_name_has_no_plus_onto_a_forced_enable_fails():
    """DEFECTIVE: a 0 Ohm link from 3V3_AUX onto LORA_EN, which the AND forces low under EMCON. It used to be followed
    as a conductor into a net holding nothing and read PASS. UNDECIDED with 10 kOhm there: the pull's voltage is not
    stated, so what it asks of the gate is not known."""
    nl = _edit(_power_board({"and", "expander_sw"}), comps={"R71": ("0R", "R", "Device:R")},
               nets={"LORA_EN": [("R71", "1", "")], "3V3_AUX": [("R71", "2", "")]})
    tx = _lora(nl)
    assert tx["ok"] is False and "a 0R link ties the net to 3V3_AUX" in tx["detail"], tx
    nl = _edit(_power_board({"and", "expander_sw"}), comps={"R71": ("10k", "R", "Device:R")},
               nets={"LORA_EN": [("R71", "1", "")], "3V3_AUX": [("R71", "2", "")]})
    tx = _lora(nl)
    assert tx["ok"] is None and "a pull to 3V3_AUX through R71 whose value or voltage cannot be read" in tx["detail"], tx


def t_a_released_enable_pulled_to_a_supply_whose_name_has_no_plus_is_not_forced_off():
    """DEFECTIVE (the review of round 6's second pass, minor 7): EMCON releases a 74LVC1G07 onto LORA_EN, which a 10 kOhm
    pull-up to 3V3_AUX holds ON against a 100 kOhm pull-down. _released_level skipped the pull it could not read and
    took the net as held at 0 V by the pull-down, so EMCON counted as forcing the switch OFF (UNDECIDED only for the
    released output's own current). Now the level is not known, the enable is not reached, and the result says why."""
    nl = _power_board({"expander_sw"}, en_pull=None)
    nl = _edit(nl, comps={"U5": OD1, "U7": INV1, "R70": ("10k", "R", "Device:R"), "R72": ("100k", "R", "Device:R")},
               nets={"EMCON_HW": [("U7", "2", "")], "INV": [("U7", "4", ""), ("U5", "2", "")],
                     "LORA_EN": [("U5", "4", ""), ("R70", "1", ""), ("R72", "1", "")], "3V3_AUX": [("R70", "2", "")],
                     "+3V3": [("U5", "5", ""), ("U7", "5", "")], "GND": [("U5", "3", ""), ("U7", "3", ""), ("R72", "2", "")]})
    tx = _lora(nl)
    assert tx["ok"] is False and "EMCON does not force off" in tx["detail"] and "EMCON releases the open-drain U5" in tx["detail"] \
        and "pulled to 3V3_AUX through R70, a supply whose name states no voltage" in tx["detail"], tx


# ---------------------------------------------------------------- round 6, fourth pass (26 September 2026)
# THE REVIEW OF THE THIRD PASS, BLOCKING 1 (R4T-D42): census() stopped at a supply known only by its name and, on a net
# EMCON holds HIGH, took any supply as a harmless pull, so a 0 Ohm or 1 kOhm link from SA_PTT_n to VCC_SENSOR, GPS_3V3
# or SIM1_VCC read PASS; and a pull to a '+' rail below the level EMCON holds read PASS whatever its current. BLOCKING 2
# (R4T-D43): _second_sources() read only a '+' rail at a resistor's far end and had no branch for a transistor, so a
# resistor from VBAT (the gated switch's own VIN) and a P-channel FET from +5V_DEV or VBAT around the gated switch read
# PASS. Each DEFECTIVE fixture below reads PASS (or, for the VIL ceiling, UNDECIDED) on the third pass's tool (5aece264)
# and as asserted now; each ACCEPTABLE one passes on both.
CPU = ("RP2040 panel controller", "Package_DFN_QFN:QFN-56", "MCU_RaspberryPi:RP2040")
M2B = ("M.2 B-key 3052 socket", "Connector:M2_BKey", "X:Y")
PFET = ("AO3401A P-FET", "Package_TO_SOT_SMD:SOT-23", "Transistor_FET:AO3401A")
LED1 = ("green LED", "LED_SMD:LED_0603", "Device:LED")


def _key(nl):
    return _tx(T.judge({"D": nl}, table=_KEY, accessories=[], receivers=[], owed=[]), "test SA868")


def _ptt_link(rv, sup, what=None, extra=None):
    """_key_board with a resistor `rv` from SA_PTT_n (EMCON holds it HIGH, receive) to the net `sup`, on which `what`
    puts a modem's SIM supply pin ("m2", an M.2 socket's UIM-PWR, board B's SIM1_VCC shape) or an RP2040 GPIO ("gpio",
    a sensor rail firmware powers)."""
    c = {"R99": (rv, "R", "Device:R")}
    n = {"SA_PTT_n": [("R99", "1", "")], sup: [("R99", "2", "")]}
    if what == "m2": c["J_M2C2"] = M2B; n[sup].append(("J_M2C2", "36", "UIM-PWR"))
    elif what == "gpio": c["U77"] = CPU; n[sup].append(("U77", "10", "GPIO5"))
    for k, v in (extra or {}).items(): n.setdefault(k, []).extend(v)
    return _edit(_key_board(), comps=c, nets=n)


def t_a_link_from_a_net_emcon_holds_high_to_a_supply_no_name_gives_a_voltage_is_not_harmless():
    """DEFECTIVE (the review's probe_level1b): a 0 Ohm or 1 kOhm link from SA_PTT_n to a sensor rail a GPIO powers
    (VCC_SENSOR, GPS_3V3) or to a modem's SIM supply (SIM1_VCC on an M.2 UIM-PWR pin). Firmware can hold either at
    0 V, which keys the active-low PTT under EMCON. Each read PASS on 5aece264. Now a 0 Ohm link FAILS, a 1 kOhm pull is
    UNDECIDED at best (its voltage is not stated), and the name-only supply is walked, so the GPIO on it FAILS the path
    and the M.2 pin leaves it UNDECIDED, named. ACCEPTABLE: a pull-up to +5V_SA, a rail whose name states a voltage at
    or above the level EMCON holds."""
    for rv in ("0R", "1k"):
        for sup in ("VCC_SENSOR", "GPS_3V3", "SIM1_VCC"):
            tx = _key(_ptt_link(rv, sup, "gpio"))
            assert tx["ok"] is False and "U77 pin 10" in tx["detail"] and "a pin whose direction firmware sets" in tx["detail"] \
                and "a supply by its name only" in tx["detail"], (rv, sup, tx)
    tx = _key(_ptt_link("0R", "SIM1_VCC", "m2"))
    assert tx["ok"] is False and "a 0R link ties the net to SIM1_VCC" in tx["detail"], tx
    tx = _key(_ptt_link("1k", "SIM1_VCC", "m2"))
    assert tx["ok"] is None and "a pull to SIM1_VCC through R99" in tx["detail"] and "J_M2C2 pin 36" in tx["detail"], tx
    for rv in ("0R", "1k", "10k"):
        tx = _key(_ptt_link(rv, "+5V_SA"))
        assert tx["ok"] is True, (rv, tx)
    assert _key(_key_board(ptt_pull=("10k", "+5V_SA")))["ok"] is True


def t_a_pull_from_a_net_emcon_holds_high_to_a_lower_rail_is_a_load_on_its_driver():
    """DEFECTIVE (the review's probe_level1, minor 4 folded into blocking 1): a 0 Ohm link from SA_PTT_n to +1V8 ties it
    under the level EMCON holds; a 330 Ohm pull to +1V8 asks 4.5 mA of the inverter, above the 4 mA every held logic
    sheet guarantees its level at; a P-channel FET from +1V8 onto it, gate on a GPIO, is a 0 Ohm link firmware closes.
    All three read PASS on 5aece264. ACCEPTABLE: a 10 kOhm pull to +1V8 (0.15 mA, the driver holds its level), and a
    P-channel FET from +5V_SA, which can only lift the net EMCON's way."""
    tx = _key(_ptt_link("0R", "+1V8"))
    assert tx["ok"] is False and "a 0R link ties the net to +1V8" in tx["detail"], tx
    tx = _key(_ptt_link("330", "+1V8"))
    assert tx["ok"] is False and "4.5 mA" in tx["detail"], tx
    assert _key(_ptt_link("10k", "+1V8"))["ok"] is True
    for src, want in (("+1V8", False), ("+5V_SA", True)):
        nl = _edit(_key_board(), comps={"Q9": PFET, "U77": CPU},
                   nets={"SA_PTT_n": [("Q9", "3", "D")], src: [("Q9", "2", "S")], "BYP_n": [("Q9", "1", "G"), ("U77", "10", "GPIO5")]})
        tx = _key(nl)
        assert tx["ok"] is want, (src, tx)
        if not want: assert "a P-channel switch from +1V8 (1.8 V)" in tx["detail"], tx


def t_a_pull_to_a_supply_known_only_by_its_name_is_walked_for_its_drivers():
    """DEFECTIVE (the review's probe_switched_rail, minor 1): a 100 kOhm pull from LORA_EN, which the AND holds low under
    EMCON, to EPD_VCC, a rail the P-channel Q5 switches from +3V3_DEV with its gate on a GPIO (board C's e-paper supply
    shape); and one to VCC_SENSOR, on which an RP2040 GPIO sits. On 5aece264 the walk stopped at the name and read
    UNDECIDED; now the name-only supply is walked, and the P-channel switch and the GPIO FAIL the path, named.
    ACCEPTABLE: the same 100 kOhm to +3V3_EPD, a rail whose name states its voltage, is a 33 uA pull the AND sinks."""
    base = _power_board({"and", "expander_sw"})
    sw = {"Q5": PFET, "U77": CPU}
    for rail, want in (("EPD_VCC", False), ("+3V3_EPD", True)):
        nl = _edit(base, comps=dict({"R99": ("100k", "R", "Device:R")}, **sw),
                   nets={"LORA_EN": [("R99", "1", "")], rail: [("R99", "2", ""), ("Q5", "3", "D")], "+3V3_DEV": [("Q5", "2", "S")],
                         "EPD_PWR_n": [("Q5", "1", "G"), ("U77", "10", "GPIO5")]})
        tx = _lora(nl)
        assert tx["ok"] is want, (rail, tx)
        if not want:
            assert "Q5 pin 3" in tx["detail"] and "a P-channel switch from +3V3_DEV" in tx["detail"] \
                and "reached through R99 100k to EPD_VCC, a supply by its name only" in tx["detail"], tx
    nl = _edit(base, comps={"R99": ("100k", "R", "Device:R"), "U77": CPU},
               nets={"LORA_EN": [("R99", "1", "")], "VCC_SENSOR": [("R99", "2", ""), ("U77", "10", "GPIO5")]})
    tx = _lora(nl)
    assert tx["ok"] is False and "U77 pin 10" in tx["detail"] and "a pin whose direction firmware sets" in tx["detail"], tx


def t_a_feed_around_the_gated_switch_from_its_own_input_fails():
    """DEFECTIVE (the review's probe_second_feed, blocking 2a): U21's VIN on VBAT (WSON pin 6, SLVSDH0C), and a 0 Ohm or
    100 Ohm resistor from VBAT onto +5V_X, the rail EMCON switches off. VBAT is a supply by the switch's own pin table,
    and the kit has this topology (board A's LM5176 stages run from VBAT). Both read PASS on 5aece264. ACCEPTABLE: the
    same switch on VBAT with no feed, and a bleed from +5V_X to ground."""
    base = _edit(_power_board({"and", "expander_sw"}), move={("U21", "6"): "VBAT"})
    assert _lora(base)["ok"] is True
    for rv in ("0R", "100R"):
        tx = _lora(_edit(base, comps={"R90": (rv, "R", "Device:R")}, nets={"+5V_X": [("R90", "1", "")], "VBAT": [("R90", "2", "")]}))
        assert tx["ok"] is False and "joined to VBAT through R90 (%s), a supply by its maker's pin table" % rv in tx["detail"], (rv, tx)
    assert _lora(_edit(base, comps={"R90": ("10k", "R", "Device:R")}, nets={"+5V_X": [("R90", "1", "")], "GND": [("R90", "2", "")]}))["ok"] is True


def t_a_resistor_from_the_gated_rail_to_a_net_only_named_like_a_supply_is_judged_by_what_is_on_it():
    """ACCEPTABLE (board B's LED_5V_A1 shape): R101 from the gated rail to LED_5V_A1, LED11's anode, whose cathode is on
    ground: everything on that net only takes current, so it is a load and not a feed. DEFECTIVE: the same net also
    carries an RP2040 GPIO, which can drive it high and feed the rail through R101: UNDECIDED, named; and a 100 Ohm
    resistor from the rail to VIN_RAW, a net the name test does not know but a regulator's VIN pin sits on (board A's and
    board E's VIN_RAW at main 458b2873): UNDECIDED, named. Both were silent on 5aece264."""
    base = _power_board({"and", "expander_sw"})
    nets = {"+5V_X": [("R101", "1", "")], "LED_5V_A1": [("R101", "2", ""), ("LED11", "2", "A")], "GND": [("LED11", "1", "K")]}
    comps = {"R101": ("1k", "R", "Device:R"), "LED11": LED1}
    assert _lora(_edit(base, comps=comps, nets=nets))["ok"] is True
    nets2 = dict(nets, LED_5V_A1=nets["LED_5V_A1"] + [("U77", "10", "GPIO5")])
    tx = _lora(_edit(base, comps=dict(comps, U77=CPU), nets=nets2))
    assert tx["ok"] is None and "LED_5V_A1, a supply by its name only, where U77 pin 10" in tx["detail"], tx
    tx = _lora(_edit(base, comps={"R90": ("100R", "R", "Device:R"), "U50": ("LM2596 buck", "Package_TO_SOT_SMD:TO-263-5", "X:Y")},
                     nets={"+5V_X": [("R90", "1", "")], "VIN_RAW": [("R90", "2", ""), ("U50", "1", "VIN")]}))
    assert tx["ok"] is None and "VIN_RAW, a net a supply pin sits on (U50), where U50 pin 1" in tx["detail"], tx


def _lm5176_stage(extra_comps, extra_nets):
    """A 30 W PA's rail as board A has it: an LM5176 (HTSSOP-28) whose EN/UVLO (pin 1) the AND U5 drives from EMCON_HW,
    VIN (pin 2) on VBAT, VOSNS (pin 12) on +13V8_PA, and the PA's lead J_PA on +13V8_PA; PA_EN held by R59 10 kOhm."""
    comps = {"U13": ("LM5176PWPR buck-boost controller", "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm", "X:Y"),
             "U5": AND1, "SW1": TOGGLE, "R59": ("10k 1%", "R", "Device:R"),
             "J_PA": ("13.8 V to the PA module", "Connector:X", "Connector_Generic:Conn_01x02")}
    nets = {"EMCON_HW": [("SW1", "1", ""), ("U5", "1", "")], "GND": [("SW1", "2", ""), ("U5", "3", ""), ("R59", "2", ""), ("J_PA", "2", "Pin_2")],
            "PA_SW_EN": [("U5", "2", "")], "+3V3": [("U5", "5", "")], "PA_EN": [("U5", "4", ""), ("U13", "1", "EN/UVLO"), ("R59", "1", "")],
            "VBAT": [("U13", "2", "VIN")], "+13V8_PA": [("U13", "12", "VOSNS"), ("J_PA", "1", "Pin_1")],
            "PA_HDRV2": [("U13", "19", "HDRV2")], "PA_SW2": [("U13", "18", "SW2")]}
    comps.update(extra_comps)
    for k, v in extra_nets.items(): nets.setdefault(k, []).extend(v)
    return _nl(comps, nets)


_PA = [dict(name="test PA", options=[dict(board="A", ref="J_PA", kind="power")])]


def t_a_transistor_channel_onto_the_gated_rail_is_a_second_feed():
    """DEFECTIVE (the review's probe_second_feed2, blocking 2b): a P-channel FET from +5V_DEV, or from VBAT, onto +5V_X
    with its gate on a GPIO, a firmware bypass of the hardware gate; and a PNP transistor this file has no pin map for
    between +5V_DEV and +5V_X. All three read PASS on 5aece264 (a Q part fell through to the output-pin test, which D, S,
    C and E never match); now the FETs FAIL and the unknown transistor is UNDECIDED. A FET whose gate the gated switch
    drives itself (an LM5176's HDRV2 on a boost-leg FET onto +13V8_PA) is UNDECIDED, since no table here states that its
    gate drive is off with its enable. ACCEPTABLE: an N-channel discharge FET from +5V_X to ground with its gate on a
    GPIO (it can only take current off the rail), and a FET whose GATE sits on the rail (board B's Q106, Q206, Q306)."""
    base = _power_board({"and", "expander_sw"})
    for src in ("+5V_DEV", "VBAT"):
        tx = _lora(_edit(base, comps={"Q9": PFET, "U77": CPU},
                         nets={"+5V_X": [("Q9", "3", "D")], src: [("Q9", "2", "S")], "BYP_n": [("Q9", "1", "G"), ("U77", "10", "GPIO5")]}))
        assert tx["ok"] is False and "fed from %s through Q9's channel (P-channel, gate on BYP_n)" % src in tx["detail"], (src, tx)
    tx = _lora(_edit(base, comps={"Q9": ("MMBT3906", "Package_TO_SOT_SMD:SOT-23", "Transistor_BJT:MMBT3906")},
                     nets={"+5V_X": [("Q9", "3", "C")], "+5V_DEV": [("Q9", "2", "E")], "BYP_n": [("Q9", "1", "B")]}))
    assert tx["ok"] is None and "Q9 pin 3" in tx["detail"] and "cannot read" in tx["detail"], tx
    nfet = {"Q9": FET, "U77": CPU}
    assert _lora(_edit(base, comps=nfet, nets={"+5V_X": [("Q9", "3", "D")], "GND": [("Q9", "2", "S")],
                                                "DIS": [("Q9", "1", "G"), ("U77", "10", "GPIO5")]}))["ok"] is True
    assert _lora(_edit(base, comps={"Q9": FET}, nets={"+5V_X": [("Q9", "1", "G")], "X1": [("Q9", "2", "S")],
                                                      "X2": [("Q9", "3", "D")]}))["ok"] is True
    pa = _tx(T.judge({"A": _lm5176_stage({}, {})}, table=_PA, accessories=[], receivers=[], owed=[]), "test PA")
    assert pa["ok"] is True, pa
    nq = ("CSD18510Q5B N-channel", "Package_SON:VSON-8", "Transistor_FET:Q_NMOS")
    pa = _tx(T.judge({"A": _lm5176_stage({"Q4": nq}, {"+13V8_PA": [("Q4", "3", "D")], "PA_SW2": [("Q4", "2", "S")],
                                                        "PA_HDRV2": [("Q4", "1", "G")]})},
                     table=_PA, accessories=[], receivers=[], owed=[]), "test PA")
    assert pa["ok"] is None and "whose gate PA_HDRV2 is driven by U13, the gated switch itself" in pa["detail"], pa


def t_a_transmitter_supply_whose_name_carries_a_control_word_is_still_its_own():
    """The review of the third pass, minor 5 (R4T-D44): the SA868's supply pin (function VBAT) sits on RF_3V3_SW, which a
    bead joins to +3V3_RF, the keying logic's rail. With +3V3_RF down the exciter is down too, so that state is not
    judged. The third pass filtered the transmitter's supplies by the name test, dropped RF_3V3_SW (its name carries
    SW), and read SA_PTT_n floating: a FAIL of a board that works (5aece264: FAIL). DEFECTIVE: the same keying logic with
    the exciter on +5V_SA, a rail of its own, still FAILS (floating)."""
    kb = _key_board(logic_rail="+3V3_RF")
    nl = _edit(kb, comps={"FB1": ("600R bead", "Inductor_SMD:L_0603", "Device:FerriteBead")},
               nets={"+3V3_RF": [("FB1", "1", "")], "RF_3V3_SW": [("FB1", "2", "")]}, move={("U2", "8"): "RF_3V3_SW"})
    assert _key(nl)["ok"] is True, _key(nl)
    tx = _key(kb)
    assert tx["ok"] is False and "SA_PTT_n floats" in tx["detail"], tx


def t_a_backup_supply_pin_is_not_the_transmitters_own_supply():
    """The guard R4T-D44 adds with minor 5: a pin its maker calls a backup (the Compute Module 5's pin 76, "RTC battery
    input", section 2.12.2) is not a supply whose loss takes the radio down. DEFECTIVE: the open-drain buffer before
    WL_nDisable runs from VBAT, the RTC cell's net, which U30A pin 76 also sits on: with VBAT down the pin is held only
    by the module's own pull-up, Wi-Fi on. With `backup_pins` declared that state is judged and FAILS; without it the
    state would be skipped as one where the module is off, and read PASS."""
    nl = _edit(_cm5_board("od", elem_rail="VBAT"), nets={"VBAT": [("U30A", "76", "VBAT")]})
    tab = [dict(_CM5[0], options=[dict(_CM5[0]["options"][0], backup_pins=("76",))])]
    tx = _tx(T.judge({"B": nl}, table=tab, accessories=[], receivers=[], owed=[]), "test CM5")
    assert tx["ok"] is False and "its maker's own pull" in tx["detail"], tx
    assert _tx(T.judge({"B": nl}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")["ok"] is True
    cm5 = [o for t in T.TRANSMITTERS for o in t["options"] if o["ref"] in ("U30A", "U31A", "U32A")]
    assert all(o.get("backup_pins") == ("76",) and "RTC battery" in o.get("backup_cite", "") for o in cm5), cm5


def t_a_line_at_a_level_no_supply_voltage_reads_as_low_fails_whatever_the_readers_supply():
    """The review of the third pass, minor 2 (R4T-D45): U19 (a 74LVC1G08) on VCC_X, a supply whose name states no
    voltage, reads EMCON_HW at 2.83 V with the panel out (10 kOhm up to +5V_X, 10 kOhm down). No VCC the part allows
    reads that as low (VIL 0.3 x 5.5 V = 1.65 V at most, SCES217AA), so it FAILS; 5aece264 read UNDECIDED. At about
    1.4 V (33 kOhm up) it is still UNDECIDED: some VCC would read it low. But a second reader on the same line that IS on
    a 3.3 V rail FAILS it there. ACCEPTABLE: U19 on +3V3_DEV with nothing lifting the line passes."""
    up = lambda r: ({"R77": (r, "R", "Device:R")}, {"EMCON_HW": [("R77", "1", "")], "+5V_X": [("R77", "2", "")]})
    line = _line_of(_panel(*up("10k"), pull_down="10k", u19_rail="VCC_X"))
    assert line["ok"] is False and "at or above the highest VIL any supply voltage gives" in line["detail"] \
        and "B U19 pin 1 1.65 V" in line["detail"], line
    line = _line_of(_panel(*up("33k"), pull_down="10k", u19_rail="VCC_X"))
    assert line["ok"] is None and "VCC not named" in line["detail"], line
    assert _line_of(_panel({}, {}))["ok"] is True
    # a node with a reader off the range and one in it is judged per reader: at 1.4 V the in-range U30 FAILS the line
    # (5aece264 exempted the whole node and read UNDECIDED); with both readers on +3V3_DEV and nothing lifting it, PASS
    two = lambda rail, extra: _panel(dict({"U30": AND1}, **extra[0]), dict({"EMCON_HW": [("U30", "1", "")] + extra[1].get("EMCON_HW", []),
                                                                         "+3V3_DEV": [("U30", "5", "")], "GND": [("U30", "3", "")]},
                                                                        **{k: v for k, v in extra[1].items() if k != "EMCON_HW"}),
                                     pull_down="10k", u19_rail=rail)
    line = _line_of(two("VCC_X", up("33k")))
    assert line["ok"] is False and "at or above the 0.8 V VIL of the gates that read it (B U30 pin 1" in line["detail"], line
    assert _line_of(two("+3V3_DEV", ({}, {})))["ok"] is True
    # the same ceiling where a gate on the path loses its supply (own_supply's threshold): KEY, which U12 on +3V3_D8
    # holds low, is read by U13 on VCC_X; with +3V3_D8 down a 10 kOhm pull-up to +5V_SA against 10 kOhm down leaves it
    # at 2.83 V (the adverse ends of the two 5 percent values and of the rail), which no VCC reads as low; with the pull-down alone it is UNDECIDED (VCC_X states no voltage)
    for pu, want in ((True, False), (False, None)):
        nl = _key_board(logic_rail="+3V3_D8", ptt_pull=("10k", "+5V_SA"))
        nl = _edit(nl, comps=dict({"R81": ("10k", "R", "Device:R")}, **({"R80": ("10k", "R", "Device:R")} if pu else {})),
                   nets=dict({"KEY": [("R81", "1", "")] + ([("R80", "1", "")] if pu else []), "GND": [("R81", "2", "")]},
                             **({"+5V_SA": [("R80", "2", "")]} if pu else {})),
                   move={("U13", "5"): "VCC_X"})
        tx = _key(nl)
        assert tx["ok"] is want, (pu, tx)
        if pu: assert "no supply voltage reads 1.65 V or more as low" in tx["detail"], tx


# MAIN 458b2873's BOARD B (R4T-D46, R4T-D47): S-01 inverts EMCON_HW once with a 2N7002 (Q11, drain EMCON_ON, R513 10 kOhm
# to +3V3_DEV) and gates each module radio with an SN74LVC32A OR (U111, KILL = OFF OR EMCON_ON) into an open-drain 2N7002
# on the pin; the WiFi cards' supplies reach their sockets through 5 mOhm shunts. The third pass's walk knew neither a
# FET EMCON holds off nor the OR, and stopped at every shunt, so it read all six module radios "EMCON does not reach
# it" and both cards' supplies "no switch this file knows": a description of the tool, not of the board.
OR4 = ("SN74LVC32APWR quad OR: module WiFi kill", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "X:Y")


def _s01_board(inv="fet", pull_rail="+3V3_CM1", or_rail="+3V3_CM1"):
    """U30A's WL_nDisable (pin 89) as board B draws it at main 458b2873: EMCON_ON = NOT EMCON_HW made by `inv` ("fet": Q11,
    a 2N7002 switch to ground with R513 10 kOhm to `pull_rail`; "gate": a 74LVC1G04 on `pull_rail`), KILL = OFF OR
    EMCON_ON by U111 (an SN74LVC32A on `or_rail`, OFF pulled up by R62 and driven by the expander U6), and Q109 pulling
    the pin low, R173 100 kOhm holding KILL low while U111 starts."""
    nl = _cm5_board("od")
    c = {"U111": OR4, "Q109": FET, "R173": ("100k", "R", "Device:R"), "R62": ("10k", "R", "Device:R")}
    c["R58"] = ("10k", "R", "Device:R")                 # EMCON_HW's own pull-down, as board B's R58
    n = {"EMCON_ON": [("U111", "2", "")], "WL_OFF": [("U111", "1", ""), ("R62", "1", ""), ("U6", "13", "IO1_0")],
         "WL_KILL": [("U111", "3", ""), ("Q109", "1", "G"), ("R173", "1", "")], "GND": [("U111", "7", ""), ("Q109", "2", "S"), ("R173", "2", "")],
         "+3V3_DEV": [("R62", "2", "")]}
    n.setdefault(or_rail, []).append(("U111", "14", ""))
    n["GND"].append(("R58", "2", ""))
    if inv == "fet":
        c.update(Q11=FET, R513=("10k", "R", "Device:R"))
        n["EMCON_HW"] = [("Q11", "1", "G"), ("R58", "1", "")]; n["GND"].append(("Q11", "2", "S")); n["EMCON_ON"] += [("Q11", "3", "D"), ("R513", "1", "")]
        n.setdefault(pull_rail, []).append(("R513", "2", ""))
    else:
        c["U11"] = INV1
        n["EMCON_HW"] = [("U11", "2", ""), ("R58", "1", "")]; n["EMCON_ON"].append(("U11", "4", "")); n["GND"].append(("U11", "3", ""))
        n.setdefault(pull_rail, []).append(("U11", "5", ""))
    nl = _edit(nl, move={("U40", "2"): "U40_UNUSED", ("U40", "4"): "U40_Y"}, comps=c, nets=n)
    return _edit(nl, nets={"WL_nDIS1": [("Q109", "3", "D")]})


def t_board_bs_s01_or_gate_and_its_inverter_are_walked():
    """ACCEPTABLE (the OR, R4T-D46): EMCON_ON made by a 74LVC1G04 and the SN74LVC32A OR both on the module's own 3.3 V,
    so neither can lose its supply while the module runs: the walk reaches pin 89 through U111 and Q109, and it PASSES.
    On 5aece264 it read "EMCON does not reach it". The OR's pin map is TI's SCAS286U Table 4-1."""
    tx = _tx(T.judge({"B": _s01_board(inv="gate")}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")
    assert tx["ok"] is True and "U111 OR 2->3" in tx["detail"] and "Q109 switch to ground" in tx["detail"], tx


def t_board_bs_s01_fet_inverter_is_walked_and_judged_on_its_pull_up():
    """Board B's own shape (R4T-D46). DEFECTIVE, the pull-up alone (the review of the fourth pass, blocking 2): Q11's
    pull-up R513 on +3V3_DEV, a rail that can be down while the module runs, and the OR on the module's own +3V3_CM1. With
    +3V3_DEV down Q11 stays off (EMCON_HW, its gate, is up) and EMCON_ON is held by nothing, so the OR reads a floating
    input and the module's radio may be released under EMCON: FAIL, naming the pull-up's rail. That state is R4T-D46's
    (_element gives a FET EMCON holds off the rails its drain is pulled up to): without it this case reads UNDECIDED, so
    this is the case that fails if the state is lost (rv9t/probe_d46_isolation). DEFECTIVE as well, but decided by the OR:
    R513 and the OR both on +3V3_DEV; own_supply() stops at U111's own supply there (KILL at 0 V under Q109's 1 V), so
    that FAIL does not test the pull-up. ACCEPTABLE: the same pull-up and OR on the module's own +3V3_CM1: the path is
    followed (Q11 held off, EMCON_ON released to 3.3 V by R513) and it is UNDECIDED, not PASS, because the fitted 2N7002
    states its off-state channel current at 25 C only (JSCJ, R4T-D28). On 5aece264 all three read "EMCON does not reach
    it"."""
    tx = _tx(T.judge({"B": _s01_board(pull_rail="+3V3_DEV", or_rail="+3V3_CM1")}, table=_CM5, accessories=[], receivers=[],
                     owed=[]), "test CM5")
    assert tx["ok"] is False and "with +3V3_DEV down (the rail Q11's released net is pulled up to" in tx["detail"] \
        and "EMCON_ON floats" in tx["detail"] and "U111's supply" not in tx["detail"], tx
    tx = _tx(T.judge({"B": _s01_board(pull_rail="+3V3_DEV", or_rail="+3V3_DEV")}, table=_CM5, accessories=[], receivers=[],
                     owed=[]), "test CM5")
    assert tx["ok"] is False and "Q11 switch to ground held off G->D released, held at 3.30 V by R513 10k to +3V3_DEV" in tx["detail"] \
        and "+3V3_DEV down" in tx["detail"], tx
    tx = _tx(T.judge({"B": _s01_board()}, table=_CM5, accessories=[], receivers=[], owed=[]), "test CM5")
    assert tx["ok"] is None and "U111 OR 2->3" in tx["detail"] \
        and "a FET EMCON holds off, and its off-state channel current is stated at 25 C only" in tx["detail"], tx
    # DEFECTIVE, and said why: a switch to ground EMCON holds off straight onto a supply switch's enable, pulled up, turns
    # the radio ON under EMCON; pulled to a supply whose name states no voltage, the level is not known and the result
    # names the FET and the pull (on 5aece264 it read only "EMCON does not force off")
    for rail, needle in (("+3V3", "EMCON does not force off"), ("3V3_AUX", "EMCON holds the switch to ground Q20 off and "
                         "leaves LORA_EN to its pulls: pulled to 3V3_AUX through R71, a supply whose name states no voltage")):
        nl = _edit(_power_board(set(), en_pull=None), comps={"Q20": FET, "R71": ("10k", "R", "Device:R")},
                   nets={"EMCON_HW": [("Q20", "1", "G")], "GND": [("Q20", "2", "S")], "LORA_EN": [("Q20", "3", "D"), ("R71", "1", "")],
                         rail: [("R71", "2", "")]})
        tx = _lora(nl)
        assert tx["ok"] is False and needle in tx["detail"], (rail, tx)


def t_a_gated_rail_behind_a_current_sense_shunt_is_traced_to_its_switch():
    """ACCEPTABLE (R4T-D47, board B's card sockets): the LoRa module's supply +5V_XS is +5V_X behind a 5 mOhm shunt; the
    switch is found through it and the rail PASSES (5aece264: "no switch this file knows has its output on +5V_XS").
    DEFECTIVE: a 0 Ohm link from +5V_DEV onto +5V_X, the net between the switch and the shunt, is a second feed of the
    same conductor and FAILS; a 10 Ohm resistor in place of the shunt is not a shunt, and the rail has no known switch."""
    def board(shunt, feed=False):
        nl = _edit(_power_board({"and", "expander_sw"}), move={("U12", "9"): "+5V_XS"},
                   comps={"R65": (shunt, "R", "Device:R")}, nets={"+5V_X": [("R65", "1", "")], "+5V_XS": [("R65", "2", "")]})
        if feed:
            nl = _edit(nl, comps={"R90": ("0R", "R", "Device:R")}, nets={"+5V_X": [("R90", "1", "")], "+5V_DEV": [("R90", "2", "")]})
        return nl
    tx = _lora(board("5mOhm 1% 2512 (Kelvin shunt)"))
    assert tx["ok"] is True and "then through the shunt R65" in tx["detail"], tx
    tx = _lora(board("5mOhm 1% 2512 (Kelvin shunt)", feed=True))
    assert tx["ok"] is False and "+5V_X: joined to +5V_DEV through R90" in tx["detail"], tx
    tx = _lora(board("10R"))
    assert tx["ok"] is False and "no switch this file knows has its output on +5V_XS" in tx["detail"], tx


def t_a_held_off_fets_pull_up_rail_down_floats_the_power_path():
    """The power-path variant of the S-01 split case (the review of the fourth pass, blocking 2; R4T-D46). DEFECTIVE: Q20, a
    2N7002 EMCON_HW holds off, releases INV_N, pulled up by R71 to +3V3_P, a rail of its own; INV_N gates Q21, a 2N7002
    switch to ground on LORA_EN, the load switch's enable (pulled up by R72 to +5V_DEV, the switch's own input). With +3V3_P
    down Q20 is still off (EMCON_HW, its gate, is up), so INV_N is held by nothing, Q21's gate floats and LORA_EN is left to
    R72: FAIL, naming +3V3_P. Without R4T-D46's pull-up-rail state the +3V3_P state is never solved and the case reads
    UNDECIDED (the 2N7002's figures), so this fixture fails if the state is lost. ACCEPTABLE: R71 on +5V_DEV, the switch's
    own input: with that rail down the switch passes nothing, the state is not one in which the radio runs, and the result
    is UNDECIDED (the fitted 2N7002 states its threshold, on resistance and off-state current at 25 C only, R4T-D28), with
    nothing floating."""
    def board(pull_rail):
        nets = {"EMCON_HW": [("Q20", "1", "G"), ("R58", "1", "")], "GND": [("Q20", "2", "S"), ("Q21", "2", "S"), ("R58", "2", "")],
                "INV_N": [("Q20", "3", "D"), ("R71", "1", ""), ("Q21", "1", "G")],
                "LORA_EN": [("Q21", "3", "D"), ("R72", "1", "")], "+5V_DEV": [("R72", "2", "")]}
        nets.setdefault(pull_rail, []).append(("R71", "2", ""))
        return _edit(_power_board(set(), en_pull=None),
                     comps={"Q20": FET, "Q21": FET, "R71": ("10k", "R", "Device:R"), "R72": ("10k", "R", "Device:R"),
                            "R58": ("10k", "R", "Device:R")}, nets=nets)
    tx = _lora(board("+3V3_P"))
    assert tx["ok"] is False and "with +3V3_P down (the rail Q20's released net is pulled up to" in tx["detail"] \
        and "INV_N floats, nothing on it holds it HIGH (the reader: Q21's" in tx["detail"], tx
    tx = _lora(board("+5V_DEV"))
    assert tx["ok"] is None and "Q20 switch to ground held off G->D released, held at 5.00 V by R71 10k to +5V_DEV > Q21 switch " \
        "to ground G->D" in tx["detail"] and "floats" not in tx["detail"], tx


# ROUND 6 FIFTH PASS (R4T-D49; the review of the fourth pass, blocking 1): _second_sources() read a resistor's far end only
# through the three supply tests, so a resistor to any net no test knew was "not a feed": a second load switch's output or
# a P-channel FET behind a 0 Ohm or 1 Ohm link onto X_ALT, and an RP2040 GPIO on the gated rail, read PASS; and a shunt was
# part of the conductor only between the switch and the rail, so board A's power stage node behind its sense resistor
# (PA_OUT behind R55, 6 mOhm, the LM5176 found by its VOSNS pin on the rail) was never read. Each DEFECTIVE fixture below
# reads PASS on the fourth pass's file (b3d645da); each ACCEPTABLE one passes on both.
INA = ("INA226 PA rail monitor (0x46)", "Package_SO:VSSOP-10_3x3mm_P0.5mm", "X:Y")
LM_FB = ("TPS62130 buck", "Package_DFN_QFN:QFN-16", "X:Y")


def t_a_feed_behind_a_link_onto_a_net_no_supply_test_knows_is_read_through():
    """DEFECTIVE (the review's probe_feed_via_link): a 0 Ohm or 1 Ohm resistor from +5V_X, the rail EMCON switches off, to
    X_ALT or LORA_PWR_B, where (a) a second TPS22810 has its output (its EN on an RP2040 GPIO), or (b) an AO3401A P-channel
    FET from +5V_DEV has its drain (its gate on a GPIO). Neither net is a supply by any of the three tests, so the fourth
    pass read the resistor as "not a feed" and all eight read PASS; the same parts on a net named +5V_ALT FAILED. Now the
    0 Ohm link puts the net on the rail's conductor and the 1 Ohm resistor's far net is read with the rail's rules: all
    eight FAIL, naming the link. A feed behind two resistors is still read. ACCEPTABLE: the same 1 Ohm link to a net that
    holds only a bleed to ground and a capacitor, or an LED's anode with its cathode on ground."""
    for alt in ("X_ALT", "LORA_PWR_B"):
        for rv in ("0R", "1R"):
            joined = ("%s, joined to +5V_X through R91 (%s)" % (alt, rv)) if rv == "0R" else ("+5V_X through R91 (%s) to %s" % (rv, alt))
            nl = _edit(_power_board({"and", "expander_sw"}), comps={"U22": LSW, "U77": CPU, "R91": (rv, "R", "Device:R")},
                       nets={alt: [("U22", "1", "VOUT"), ("R91", "2", "")], "+5V_X": [("R91", "1", "")], "+5V_DEV": [("U22", "6", "VIN")],
                             "GND": [("U22", "4", "GND")], "BYP_EN": [("U22", "5", "EN/UVLO"), ("U77", "10", "GPIO5")]})
            tx = _lora(nl)
            assert tx["ok"] is False and joined + ": a second switch output, U22 pin 1" in tx["detail"], (alt, rv, tx)
            nl = _edit(_power_board({"and", "expander_sw"}), comps={"Q9": PFET, "U77": CPU, "R91": (rv, "R", "Device:R")},
                       nets={alt: [("Q9", "3", "D"), ("R91", "2", "")], "+5V_X": [("R91", "1", "")], "+5V_DEV": [("Q9", "2", "S")],
                             "BYP_n": [("Q9", "1", "G"), ("U77", "10", "GPIO5")]})
            tx = _lora(nl)
            assert tx["ok"] is False and joined + ": fed from +5V_DEV through Q9's channel (P-channel, gate on BYP_n)" in tx["detail"], \
                (alt, rv, tx)
    # two resistors in series: +5V_X > R91 1k > X_ALT > R92 1k > X_ALT2, where the second switch's output is
    nl = _edit(_power_board({"and", "expander_sw"}), comps={"U22": LSW, "R91": ("1k", "R", "Device:R"), "R92": ("1k", "R", "Device:R")},
               nets={"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("R92", "1", "")], "X_ALT2": [("R92", "2", ""), ("U22", "1", "VOUT")],
                     "+5V_DEV": [("U22", "6", "VIN")], "GND": [("U22", "4", "GND")], "BYP_EN": [("U22", "5", "EN/UVLO")]})
    tx = _lora(nl)
    assert tx["ok"] is False and "+5V_X through R91 (1k) to X_ALT through R92 (1k) to X_ALT2: a second switch output, U22 pin 1" \
        in tx["detail"], tx
    for extra_c, extra_n in (({"R92": ("100k", "R", "Device:R"), "C9": ("100n", "C", "Device:C")},
                              {"X_ALT": [("R92", "1", ""), ("C9", "1", "")], "GND": [("R92", "2", ""), ("C9", "2", "")]}),
                             ({"LED9": LED1}, {"X_ALT": [("LED9", "2", "A")], "GND": [("LED9", "1", "K")]})):
        nl = _edit(_power_board({"and", "expander_sw"}), comps=dict({"R91": ("1R", "R", "Device:R")}, **extra_c),
                   nets=dict({"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", "")] + extra_n["X_ALT"]}, GND=extra_n["GND"]))
        tx = _lora(nl)
        assert tx["ok"] is True, (sorted(extra_c), tx)


def t_a_firmware_pin_on_the_gated_rail_is_named():
    """DEFECTIVE (the review's probe_gpio_on_rail): an RP2040 GPIO on +5V_X, directly or through a 0 Ohm link, FAILS (the
    census fails the same pin on any net EMCON forces); through 100 Ohm it is UNDECIDED, named, because the resistor bounds
    what firmware can feed and nothing here judges whether that matters. All three read PASS on b3d645da. ACCEPTABLE: the
    RP2040 running from the gated rail, its IOVDD pin on it (a load), passes. A pin whose function is only its net's name
    (a generated symbol) cannot say whether it is the part's supply: UNDECIDED. A pin named after what it measures
    (VIN_MON, board E's RP2040 ADC pin) is not read as a supply pin: it FAILS on the rail."""
    tx = _lora(_edit(_power_board({"and", "expander_sw"}), comps={"U77": CPU}, nets={"+5V_X": [("U77", "10", "GPIO5")]}))
    assert tx["ok"] is False and "+5V_X: U77 pin 10 (RP2040 panel controller, 'GPIO5') is a pin whose direction firmware sets, on " \
        "the rail" in tx["detail"], tx
    tx = _lora(_edit(_power_board({"and", "expander_sw"}), comps={"U77": CPU}, nets={"+5V_X": [("U77", "39", "VIN_MON")]}))
    assert tx["ok"] is False and "U77 pin 39 (RP2040 panel controller, 'VIN_MON') is a pin whose direction firmware sets" in tx["detail"], tx
    for rv, want, needle in (("0R", False, "X_SENSE, joined to +5V_X through R91 (0R): U77 pin 10"),
                             ("100R", None, "+5V_X through R91 (100R) to X_SENSE: U77 pin 10 (RP2040 panel controller, 'GPIO5') "
                                            "is a pin of a part whose pins firmware sets")):
        tx = _lora(_edit(_power_board({"and", "expander_sw"}), comps={"U77": CPU, "R91": (rv, "R", "Device:R")},
                         nets={"+5V_X": [("R91", "1", "")], "X_SENSE": [("R91", "2", ""), ("U77", "10", "GPIO5")]}))
        assert tx["ok"] is want and needle in tx["detail"], (rv, tx)
    tx = _lora(_edit(_power_board({"and", "expander_sw"}), comps={"U77": CPU},
                     nets={"+5V_X": [("U77", "1", "IOVDD"), ("U77", "44", "VREG_VIN")], "GND": [("U77", "57", "GND")]}))
    assert tx["ok"] is True, tx
    tx = _lora(_edit(_power_board({"and", "expander_sw"}), comps={"U77": CPU}, nets={"+5V_X": [("U77", "1", "+5V_X")]}))
    assert tx["ok"] is None and "its function is only its net's name" in tx["detail"], tx


def _pa_sensed(extra_comps, extra_nets):
    """_lm5176_stage with board A's sense and feedback network at main 458b2873: the power stage's node PA_OUT reaches
    +13V8_PA through R55 (6 mOhm), an INA226 reads across it (IN+ on PA_OUT, IN- and VBUS on +13V8_PA), R162 and R163 (100
    Ohm) filter it into the LM5176's ISNS(+) and ISNS(-) (pins 14 and 13), and R50 162 kOhm / R51 10 kOhm set FB (pin 11)."""
    c = {"R55": ("6mOhm 1% 2512 (ISNS)", "R", "Device:R"), "U14": INA, "R162": ("100R 1%", "R", "Device:R"),
         "R163": ("100R 1%", "R", "Device:R"), "C129": ("1n", "C", "Device:C"), "R50": ("162k 1%", "R", "Device:R"),
         "R51": ("10k 1%", "R", "Device:R")}
    n = {"PA_OUT": [("R55", "1", ""), ("U14", "10", "IN+"), ("R162", "1", "")],
         "+13V8_PA": [("R55", "2", ""), ("U14", "9", "IN-"), ("U14", "8", "VBUS"), ("R163", "1", ""), ("R50", "1", "")],
         "PA_ISNS_P": [("R162", "2", ""), ("U13", "14", "ISNS(+)"), ("C129", "1", "")],
         "PA_ISNS_N": [("R163", "2", ""), ("U13", "13", "ISNS(-)"), ("C129", "2", "")],
         "PA_FB": [("R50", "2", ""), ("R51", "1", ""), ("U13", "11", "FB")], "GND": [("R51", "2", ""), ("U14", "7", "GND")],
         "+3V3": [("U14", "6", "VS")]}
    c.update(extra_comps)
    for k, v in extra_nets.items(): n.setdefault(k, []).extend(v)
    return _lm5176_stage(c, n)


def t_a_power_stage_behind_its_sense_shunt_is_read_like_the_rail():
    """Board A's shape at main 458b2873 (R4T-D49, correcting R4T-D47). The LM5176 is found by its VOSNS pin on +13V8_PA, so
    the path from the switch is the rail alone, and the stage's own node PA_OUT sits behind the 6 mOhm R55. DEFECTIVE: the
    boost-leg FET Q4 (gate on PA_HDRV2, U13's pin 19) moved from the rail to PA_OUT reads PASS on b3d645da, where on the
    rail it reads UNDECIDED; now it reads the same behind the shunt, UNDECIDED, naming PA_OUT and R55. Board A's own Q14
    (a CSD18510Q5B whose symbol names its pins after their nets, which fet_of cannot read) is UNDECIDED and names the U13
    pins its other pins share. A P-channel FET from VBAT onto PA_OUT, gate on a GPIO, FAILS. ACCEPTABLE: the sense and
    feedback network alone (the ISNS filter into U13, the FB divider) PASSES. *Changed in the twelfth pass (R4T-D70): the
    INA226 across R55 was part of the ACCEPTABLE network; it is a part in no class, which the eleventh pass read as a load
    without a word (limit (1)), and it reads UNDECIDED now, naming its three pins.*"""
    ina = _tx(T.judge({"A": _pa_sensed({}, {})}, table=_PA, accessories=[], receivers=[], owed=[]), "test PA")
    assert ina["ok"] is None and "U14 pin 10 (INA226 PA rail monitor (0x46), 'IN+') sits on the rail's conductor, and it is a " \
        "pin of a part no class here reads" in ina["detail"] and "U14 pin 8 (INA226 PA rail monitor (0x46), 'VBUS')" in \
        ina["detail"], ina
    base = _pa_sensed({}, {})
    ok = _tx(T.judge({"A": _edit(base, move={("U14", "10"): "unconnected-(U14-IN+-Pad10)", ("U14", "9"): "unconnected-(U14-IN--Pad9)",
                                             ("U14", "8"): "unconnected-(U14-VBUS-Pad8)"})},
                     table=_PA, accessories=[], receivers=[], owed=[]), "test PA")
    assert ok["ok"] is True, ok
    nq = ("CSD18510Q5B N-channel", "Package_SON:VSON-8", "Transistor_FET:Q_NMOS")
    q4 = {"PA_SW2": [("Q4", "2", "S")], "PA_HDRV2": [("Q4", "1", "G")]}
    on_rail = _tx(T.judge({"A": _pa_sensed({"Q4": nq}, dict(q4, **{"+13V8_PA": [("Q4", "3", "D")]}))}, table=_PA, accessories=[],
                          receivers=[], owed=[]), "test PA")
    behind = _tx(T.judge({"A": _pa_sensed({"Q4": nq}, dict(q4, PA_OUT=[("Q4", "3", "D")]))}, table=_PA, accessories=[],
                         receivers=[], owed=[]), "test PA")
    tail = "fed from PA_SW2 through Q4's channel (N-channel), whose gate PA_HDRV2 is driven by U13, the gated switch itself"
    assert on_rail["ok"] is None and "+13V8_PA: " + tail in on_rail["detail"], on_rail
    assert behind["ok"] is None and "PA_OUT, joined to +13V8_PA through R55 (6mOhm 1% 2512 (I): " + tail in behind["detail"], behind
    q14 = ("CSD18510Q5B 40 V N-FET", "Package_SO:PowerPAK_SO-8_Single", "meshsat_ic:Q14")
    a = _tx(T.judge({"A": _pa_sensed({"Q14": q14}, {"PA_SW2": [("Q14", p, "PA_SW2") for p in ("1", "2", "3")],
                                                    "PA_HDRV2": [("Q14", "4", "PA_HDRV2")], "PA_OUT": [("Q14", "5", "PA_OUT")]})},
                    table=_PA, accessories=[], receivers=[], owed=[]), "test PA")
    assert a["ok"] is None and "PA_OUT, joined to +13V8_PA through R55" in a["detail"] and "Q14 pin 5" in a["detail"] \
        and "cannot read" in a["detail"] and "its other pins sit on PA_HDRV2, PA_SW2, where U13, the gated switch itself, has its " \
        "pins 19, 18" in a["detail"], a
    p = _tx(T.judge({"A": _pa_sensed({"Q9": PFET, "U77": CPU}, {"PA_OUT": [("Q9", "3", "D")], "VBAT": [("Q9", "2", "S")],
                                                                "BYP_n": [("Q9", "1", "G"), ("U77", "10", "GPIO5")]})},
                    table=_PA, accessories=[], receivers=[], owed=[]), "test PA")
    assert p["ok"] is False and "PA_OUT, joined to +13V8_PA through R55" in p["detail"] \
        and "fed from VBAT through Q9's channel (P-channel, gate on BYP_n)" in p["detail"], p


# ROUND 6 SIXTH PASS (R4T-D50; the review of the fifth pass, blocking 1): R4T-D49 passed a pin of a part firmware sets as a
# load whenever its NAME matched a supply pattern (_POWER_FN), so a Compute Module 5's CM5_3.3V and CM5_1.8V (regulator
# OUTPUTS of up to 600 mA, CM5 datasheet 3.4 and pins 84, 86, 88, 90 "(Output)"), a CP2102N's VDD with its regulator
# powered (VREGOUT, CP2102N Rev 1.5 Table 3.6 and note 1) and any name merely ENDING in a supply word (GPIO24_VBUS, ADC_VIN,
# SENSE_3V3) read PASS on a gated rail. Now the maker's pin table decides (FW_PIN_TABLES). Each DEFECTIVE fixture below
# reads PASS on the fifth pass's file (bd3e93d5) unless it says otherwise; each ACCEPTABLE one passes on both.
CM5_RA = ("Amphenol 10164227-1004A1RLF receptacle A, slot S1 (CM5 pins 1-100, GPIO side)", "meshsat:CM5",
          "Connector_Generic:CM5A")          # board B's form: the receptacle carries the module's own pin numbers
CP2 = ("CP2102N-A02-GQFN28 USB-UART bridge (ZBA)", "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm", "Connector_Generic:CP2102N")
PI7C = ("Diodes PI7C9X2G404SL PCIe 2.0 switch, slot S1: up = CM5 lane, port 1 NVMe, port 2 card socket",
        "Package_DFN_QFN:QFN-128", "Connector_Generic:PI7C9X2G404SL")
SC16 = ("SC16IS740IPW I2C UART bridge", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", "Interface_UART:SC16IS740IPW")


def _on_rail(comps, nets):
    return _lora(_edit(_power_board({"and", "expander_sw"}), comps=comps, nets=nets))


def t_a_supply_output_of_a_part_firmware_sets_is_a_second_feed():
    """DEFECTIVE (the review's probe_supply_outputs): the Compute Module 5's CM5_3.3V (pin 84) or CM5_1.8V (pin 88) on
    +5V_X, the rail EMCON switches off, directly or through a 0 Ohm link, FAILS as a supply OUTPUT naming the datasheet's
    section 3.4; so does pin 84 when the symbol names it only after its net, because the module's pin number decides (the
    fifth pass read that UNDECIDED). A CP2102N's VDD on +5V_X with its VREGIN on +5V_DEV is its regulator's output and
    FAILS. The RP2040's VREG_VOUT and an STM32H7's VCAP FAIL, now named as outputs (the fifth pass failed them as pins
    firmware can drive); an STM32H7's VREF+ on the rail with its VDDA on +3V3 is the VREFBUF output firmware can enable,
    and FAILS. Behind a 10 Ohm resistor CM5_3.3V is UNDECIDED, like every firmware pin there (on both files). ACCEPTABLE: the Compute Module 5 running from the rail by its 5V input pins (77 to 87 odd), a CP2102N whose
    VREGIN is tied to VDD on the rail (its regulator unused, note 1), with VBUS on the rail, an STM32H7 with VREF+
    and VDDA both on the rail, and a PCA9555 whose VDD is the rail, all PASS. *Changed in the tenth pass (R4T-D62,
    R4T-F35): the same CP2102N with VBUS OFF the rail, on +5V_DEV, was ACCEPTABLE here; CP2102N Rev 1.5 2.3 (page 8) states
    'high VBUS pin leakage current ... while the device is not powered', so it reads UNDECIDED now and is a DEFECTIVE case
    of t_every_other_supply_pin_of_a_part_on_a_gated_rail_is_read.*"""
    for pin, name in (("84", "CM5_3.3V"), ("88", "CM5_1.8V")):
        tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": [("U30A", pin, name)]})
        assert tx["ok"] is False and "+5V_X: U30A pin %s (Amphenol 10164227-1004A1RLF re, %r) is a supply OUTPUT by its " \
            "maker's table (pin %s is %s by its maker's pin number; Compute Module 5, 3.4 'Regulator outputs'" % (
                pin, name, pin, name) in tx["detail"], (pin, tx)
    tx = _on_rail({"U30A": CM5_RA, "R91": ("0R", "R", "Device:R")},
                  {"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("U30A", "84", "CM5_3.3V")]})
    assert tx["ok"] is False and "X_ALT, joined to +5V_X through R91 (0R): U30A pin 84" in tx["detail"] \
        and "is a supply OUTPUT" in tx["detail"], tx
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": [("U30A", "84", "+5V_X")]})
    assert tx["ok"] is False and "pin 84 is CM5_3.3V by its maker's pin number" in tx["detail"], tx
    tx = _on_rail({"U30A": CM5_RA, "R91": ("10R", "R", "Device:R")},
                  {"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("U30A", "84", "CM5_3.3V")]})
    assert tx["ok"] is None and "+5V_X through R91 (10R) to X_ALT: U30A pin 84" in tx["detail"], tx
    tx = _on_rail({"U16": CP2}, {"+5V_X": [("U16", "6", "VDD")], "+5V_DEV": [("U16", "7", "VREGIN"), ("U16", "8", "VBUS")],
                                 "GND": [("U16", "3", "GND")]})
    assert tx["ok"] is False and "U16 pin 6 (CP2102N-A02-GQFN28 USB-UART br, 'VDD') is CP2102N's VDD, the output of its 5 V " \
        "regulator whenever VREGIN is powered (Table 3.6" in tx["detail"] and "its VREGIN is on +5V_DEV, not on the rail" \
        in tx["detail"], tx
    tx = _on_rail({"U77": CPU}, {"+5V_X": [("U77", "45", "VREG_VOUT")], "U77_DVDD": [("U77", "23", "DVDD")]})
    assert tx["ok"] is False and "'VREG_VOUT') is a supply OUTPUT by its maker's table (VREG_VOUT; RP2040" in tx["detail"], tx
    tx = _on_rail({"U41": MCU}, {"+5V_X": [("U41", "48", "VCAP")]})
    assert tx["ok"] is False and "'VCAP') is a supply OUTPUT by its maker's table (VCAP; STM32H7" in tx["detail"], tx
    tx = _on_rail({"U41": MCU}, {"+5V_X": [("U41", "20", "VREF+")], "+3V3": [("U41", "21", "VDDA")]})
    assert tx["ok"] is False and "is STM32H7's VREF+, the output of the voltage reference buffer when firmware enables it" \
        in tx["detail"] and "its VDDA is on +3V3, not on the rail" in tx["detail"], tx
    # ACCEPTABLE
    for comps, nets in (({"U30A": CM5_RA}, {"+5V_X": [("U30A", p, "5V") for p in ("77", "79", "81", "83", "85", "87")]}),
                        ({"U16": CP2}, {"+5V_X": [("U16", "6", "VDD"), ("U16", "7", "VREGIN"), ("U16", "8", "VBUS")],
                                        "GND": [("U16", "3", "GND")]}),
                        ({"U41": MCU}, {"+5V_X": [("U41", "20", "VREF+"), ("U41", "21", "VDDA"), ("U41", "11", "VDD")],
                                        "GND": [("U41", "10", "VSS")]}),
                        ({"U66": EXP}, {"+5V_X": [("U66", "24", "VDD")], "GND": [("U66", "12", "VSS")]})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(comps), tx)


def t_a_pin_is_a_load_only_by_its_makers_row():
    """DEFECTIVE: a pin whose name only ENDS in a supply word is a pin firmware can drive. An RP2040 pin named
    'GPIO24_VBUS', 'GPIO29_VSYS', 'ADC_VIN' or 'SENSE_3V3' on +5V_X FAILS as one (the fifth pass read all four PASS, by the
    '(\\w+_)?' prefix of _POWER_FN). The part's ground on the rail FAILS: it returns the part's supply current onto the rail
    (the fifth pass read a ground as a load). A Compute Module 5 pin the symbol calls '5V' at pin 12, where the maker's
    table has no 5V, is UNDECIDED, not a load. A PCIe switch whose value says 'up = CM5 lane' is not read with the Compute
    Module's pin numbers, so its VDDR at pin 77 is UNDECIDED (no table held for it), not a 5V input; and a part firmware
    sets with no table here (an SC16IS740's VDD) is UNDECIDED. ACCEPTABLE: the RP2040 running from the rail by IOVDD and
    VREG_VIN passes (the fifth pass's own fixture, kept), and so do its DVDD, ADC_AVDD and USB_VDD."""
    for fn in ("GPIO24_VBUS", "GPIO29_VSYS", "ADC_VIN", "SENSE_3V3"):
        tx = _on_rail({"U77": CPU}, {"+5V_X": [("U77", "10", fn)]})
        assert tx["ok"] is False and "U77 pin 10 (RP2040 panel controller, %r) is a pin whose direction firmware sets, on " \
            "the rail" % fn in tx["detail"], (fn, tx)
    tx = _on_rail({"U77": CPU}, {"+5V_X": [("U77", "57", "GND")], "+3V3": [("U77", "1", "IOVDD")]})
    assert tx["ok"] is False and "'GND') is RP2040's ground (GND): a ground pin on the rail returns whatever powers the part " \
        "onto the rail" in tx["detail"], tx
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": [("U30A", "12", "5V")]})
    assert tx["ok"] is None and "names 5V, which Compute Module 5's table gives at pin 77/79/81/83/85/87, not at pin 12" \
        in tx["detail"], tx
    tx = _on_rail({"U101": PI7C}, {"+5V_X": [("U101", "77", "VDDR")]})
    assert T.fw_family(_edit(_power_board(set()), comps={"U101": PI7C}), "U101") is None
    assert tx["ok"] is None and "'VDDR') is a pin of a part whose pins firmware sets, and it names a supply, and no maker's " \
        "pin table held here (FW_PIN_TABLES) covers this part" in tx["detail"], tx
    tx = _on_rail({"U20": SC16}, {"+5V_X": [("U20", "2", "VDD")]})
    assert tx["ok"] is None and "U20 pin 2 (SC16IS740IPW I2C UART bridge, 'VDD')" in tx["detail"], tx
    # ACCEPTABLE
    tx = _on_rail({"U77": CPU}, {"+5V_X": [("U77", "1", "IOVDD"), ("U77", "44", "VREG_VIN"), ("U77", "43", "ADC_AVDD"),
                                           ("U77", "48", "USB_VDD"), ("U77", "23", "DVDD")], "GND": [("U77", "57", "GND")]})
    assert tx["ok"] is True, tx
    # the families are found by the part itself: board B's receptacles, the three bridges' value, the STM32's, the RP2040's
    nl = _edit(_power_board(set()), comps={"U30A": CM5_RA, "U16": CP2, "U41": MCU, "U77": CPU, "U66": EXP, "U101": PI7C})
    assert [(T.fw_family(nl, r) or {}).get("family") for r in ("U30A", "U16", "U41", "U77", "U66", "U101")] == \
        ["Compute Module 5", "CP2102N", "STM32H7", "RP2040", "PCA9555", None]


# ROUND 6 SEVENTH PASS (R4T-D51, R4T-D52; the review of the sixth pass, blocking 1 and 2, and its minors 3, 4, 6 and 9). Each
# DEFECTIVE fixture below reads PASS on the sixth pass's file (4836c42c) unless it says otherwise; each ACCEPTABLE one passes
# on both unless it says otherwise.
H743 = ("STM32H743VIT6 I/O supervisor A: 2-of-3 quorum", "Package_QFP:LQFP-100_14x14mm_P0.5mm", "Connector_Generic:STM32H743VI")
H723 = ("STM32H723VGT6 controller", "Package_QFP:LQFP-100_14x14mm_P0.5mm", "Connector_Generic:STM32H723VG")
CM5_RB = ("Amphenol 10164227-1004A1RLF receptacle B, slot S1 (CM5 pins 101-200, high-speed side)", "meshsat:CM5",
          "Connector_Generic:CM5B")
PI7C_CM5 = ("Diodes PI7C9X2G404SL PCIe 2.0 switch on the Compute Module 5 PCIe lane", "Package_DFN_QFN:QFN-128",
            "Connector_Generic:PI7C9X2G404SL")
KSZ_CM5 = ("Microchip KSZ9897RTXI seven-port Gigabit switch for the Compute Module 5 slots", "Package_DFN_QFN:QFN-128",
           "Connector_Generic:KSZ9897R")
CM5_5V = [("U30A", p, "5V") for p in ("77", "79", "81", "83", "85", "87")]


def t_a_vbat_pin_is_tied_to_the_supply_its_charger_runs_from():
    """DEFECTIVE (the review of the sixth pass, blocking 1): firmware can switch on a charger that drives current OUT of
    each part's VBAT. An STM32H7's VBAT on +5V_X, the rail EMCON switches off, with its VDD and VDDA on +3V3 FAILS, naming
    the charger from VDD (DS12110 Table 95: RBC 5 kOhm with VBRS in PWR_CR3 = 0, 1.5 kOhm with VBRS = 1), for the fixture's
    STM32H753 and for board B's STM32H743; a Compute Module 5's pin 76 on +5V_X with its 5V pins on +5V_S1 FAILS, naming
    the RTC's 3 mA charger and rtc_bbat_vchg; pin 76 alone on the rail (no 5V drawn) is UNDECIDED; an STM32H7's VBAT with
    its VDD on ground is UNDECIDED and says so. Behind a 10 Ohm resistor pin 76 is UNDECIDED, as every firmware pin there
    (on both files). ACCEPTABLE: VBAT with VDD (and VDDA) on the rail, and pin 76 with the module's 5V pins on the rail,
    PASS."""
    for mcu, vdd in ((MCU, "+3V3"), (H743, "+3V3_IOCA")):
        tx = _on_rail({"U41": mcu}, {"+5V_X": [("U41", "6", "VBAT")], vdd: [("U41", "11", "VDD"), ("U41", "21", "VDDA")],
                                     "GND": [("U41", "10", "VSS")]})
        assert tx["ok"] is False and "'VBAT') is STM32H7's VBAT, the far end of the battery charger firmware can switch on " \
            "from VDD (DS12110 6.3.24 Table 95, DS12117 Table 94, 'VBAT charging characteristics': RBC 'Battery charging " \
            "resistor' 5 kOhm with VBRS in PWR_CR3 = 0 and 1.5 kOhm with VBRS = 1" in tx["detail"] \
            and "and its VDD is on %s, not on the rail" % vdd in tx["detail"], (mcu[0], tx)
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": [("U30A", "76", "VBAT")], "+5V_S1": CM5_5V})
    assert tx["ok"] is False and "'VBAT') is Compute Module 5's VBAT, the output of the RTC's battery charger, 'a " \
        "constant-current (3 mA) constant-voltage charger' that firmware switches on from config.txt with rtc_bbat_vchg" \
        in tx["detail"] and "and its 5V is on +5V_S1, not on the rail" in tx["detail"], tx
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": [("U30A", "76", "VBAT")]})
    assert tx["ok"] is None and "unless its 5V is tied to it, and its 5V is not on this netlist" in tx["detail"], tx
    tx = _on_rail({"U41": MCU}, {"+5V_X": [("U41", "6", "VBAT")], "GND": [("U41", "11", "VDD"), ("U41", "10", "VSS")]})
    assert tx["ok"] is None and "unless its VDD is tied to it, and its VDD is on ground (GND)" in tx["detail"], tx
    tx = _on_rail({"U30A": CM5_RA, "R91": ("10R", "R", "Device:R")},
                  {"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("U30A", "76", "VBAT")], "+5V_S1": CM5_5V})
    assert tx["ok"] is None and "+5V_X: joined through R91 (10R) to X_ALT" in tx["detail"], tx
    # ACCEPTABLE
    for comps, nets in (({"U41": MCU}, {"+5V_X": [("U41", "6", "VBAT"), ("U41", "11", "VDD"), ("U41", "21", "VDDA")],
                                        "GND": [("U41", "10", "VSS")]}),
                        ({"U41": H743}, {"+5V_X": [("U41", "6", "VBAT"), ("U41", "11", "VDD")], "GND": [("U41", "10", "VSS")]}),
                        ({"U30A": CM5_RA}, {"+5V_X": [("U30A", "76", "VBAT")] + CM5_5V})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(comps), tx)


def t_a_tied_pin_is_judged_on_the_rails_conductor_and_a_grounded_partner_is_named():
    """The review of the sixth pass, minors 3 and 4 (R4T-D51 (d)). ACCEPTABLE: a CP2102N whose VDD is on +5V_X and whose
    VREGIN is on X_ALT, joined to +5V_X by a 0 Ohm link, is tied (Rev 1.5, note 1) and PASSES; 4836c42c read it FAIL, 'its
    VREGIN is on X_ALT' (a false FAIL, seen). An STM32H7's VREF+ on the rail with its VDDA across a 0 Ohm link no longer
    FAILS as the VREFBUF output; it stays UNDECIDED for the link itself, a 0 Ohm link to a net a supply pin sits on
    (R4T-D49 (c)), where VDDA is not shown to be a load (a limit named in r4-decisions.md section 5). DEFECTIVE in its
    words: a CP2102N's VDD on the rail with its VREGIN on ground is UNDECIDED on both files, and now says the VREGIN is on
    ground (4836c42c said 'unconnected')."""
    tx = _on_rail({"U16": CP2, "R91": ("0R", "R", "Device:R")},
                  {"+5V_X": [("U16", "6", "VDD"), ("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("U16", "7", "VREGIN")],
                   "GND": [("U16", "3", "GND")]})
    assert tx["ok"] is True, tx
    tx = _on_rail({"U41": MCU, "R91": ("0R", "R", "Device:R")},
                  {"+5V_X": [("U41", "20", "VREF+"), ("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("U41", "21", "VDDA")],
                   "GND": [("U41", "10", "VSS")]})
    assert tx["ok"] is None and "the voltage reference buffer" not in tx["detail"] \
        and "+5V_X: joined through R91 (0R) to X_ALT, a net a supply pin sits on (U41)" in tx["detail"], tx
    tx = _on_rail({"U16": CP2}, {"+5V_X": [("U16", "6", "VDD")], "GND": [("U16", "7", "VREGIN"), ("U16", "3", "GND")]})
    assert tx["ok"] is None and "unless its VREGIN is tied to it, and its VREGIN is on ground (GND)" in tx["detail"], tx


def t_a_part_is_read_by_what_it_is_not_by_what_its_value_mentions():
    """DEFECTIVE (the review of the sixth pass, blocking 2): a PI7C9X2G404SL whose value says 'on the Compute Module 5 PCIe
    lane' was read with the module's pin numbers, so its pin 77 'VDDR' and pin 78 'VDD33' on +5V_X passed as the module's
    5V and GPIO_VREF; now it has no table and both are UNDECIDED; so is a KSZ9897 whose value names the Compute Module 5,
    pin 77 'VDDIO'. A receptacle-B symbol numbered 1 to 100 with pin 77 'PCIE_CLK_P' on the rail, a receptacle-A symbol
    whose pin 77 is named 'GPIO5', and one whose pin 76 is named 'PCIE_CLK_P', disagree with the maker's numbering and are
    UNDECIDED, named. ACCEPTABLE: the module's 5V pins named only after the net pass (the pins named '5V' pass in
    t_a_supply_output_of_a_part_firmware_sets_is_a_second_feed). The families, and whether firmware sets a part's pins, are
    found by the part itself (R4T-D52, closing R4T-F22): board B's receptacles, CP2102N, STM32H743 and PCA9555, board E's
    RP2040 by its value (its symbol is meshsat_ic:U10), and the KSZ9897, PI7C9X2G404SL and TUSB8041 by their own part
    numbers; a connector whose value mentions the RP2040 (board B's J_PANEL), a capacitor citing the CM5 datasheet and a
    level shifter 'for the RP2040' are neither, and an STM32H723, whose sheet is not held, has no table (minor 6)."""
    for comps, nets, needle in (
            ({"U101": PI7C_CM5}, {"+5V_X": [("U101", "77", "VDDR")]}, "U101 pin 77 (Diodes PI7C9X2G404SL PCIe 2.0 , 'VDDR') is a "
             "pin of a part whose pins firmware sets, and it names a supply, and no maker's pin table held here"),
            ({"U101": PI7C_CM5}, {"+5V_X": [("U101", "78", "VDD33")]}, "'VDD33') is a pin of a part whose pins firmware sets, "
             "and it names a supply, and no maker's pin table held here"),
            ({"U1": KSZ_CM5}, {"+5V_X": [("U1", "77", "VDDIO")]}, "U1 pin 77 (Microchip KSZ9897RTXI seven-po, 'VDDIO') is a pin "
             "of a part whose pins firmware sets, and it names a supply, and no maker's pin table held here"),
            ({"U30B": CM5_RB}, {"+5V_X": [("U30B", "77", "PCIE_CLK_P")]}, "is pin 77, which Compute Module 5's table gives as 5V "
             "by its maker's pin number, but the symbol calls it 'PCIE_CLK_P', so the maker's number and the symbol's name "
             "disagree and the pin is not taken as 5V"),
            ({"U30A": CM5_RA}, {"+5V_X": [("U30A", "77", "GPIO5")]}, "but the symbol calls it 'GPIO5', so the maker's number "
             "and the symbol's name disagree"),
            ({"U30A": CM5_RA}, {"+5V_X": [("U30A", "76", "PCIE_CLK_P")] + CM5_5V}, "is pin 76, which Compute Module 5's table "
             "gives as VBAT by its maker's pin number, but the symbol calls it 'PCIE_CLK_P'")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx)
    # ACCEPTABLE
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": [("U30A", p, "+5V_X") for p in ("77", "79", "81", "83", "85", "87")]})
    assert tx["ok"] is True, tx
    # the part itself decides
    parts = {"U101": PI7C_CM5, "U1": KSZ_CM5, "U102": ("TI TUSB8041IRGCR four-port USB 3.0 hub, slot S1 (upstream the CM5 "
                                                      "USB3-0 port)", "Package_DFN_QFN:QFN-64", "Connector_Generic:TUSB8041"),
             "U30A": CM5_RA, "U30B": CM5_RB, "U16": CP2, "U41": H743, "U42": H723, "U6": EXP,
             "U10": ("RP2040 sensor controller (USB to B16 through the dock)", "Package_DFN_QFN:QFN-56", "meshsat_ic:U10"),
             "U9": ("CM5 socket", "meshsat:CM5", "Connector_Generic:Conn_02x50"),
             "J_PANEL": ("panel ribbon to PCB-C C7 (IDC 2x13): the RP2040 panel controller's USB", "Connector:IDC",
                         "Connector_Generic:Conn_02x13_Odd_Even"),
             "C151": ("220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)", "Capacitor_SMD:C_0402", "Device:C"),
             "U8": ("TXS0102 level shifter for the RP2040", "Package_SO:VSSOP-8", "Logic_LevelTranslator:TXS0102DCU")}
    nl = _edit(_power_board(set()), comps=parts)
    fam = {r: (T.fw_family(nl, r) or {}).get("family") for r in parts}
    fw = {r for r in parts if T.software_io(nl, r)}
    assert fam == {"U101": None, "U1": None, "U102": None, "U30A": "Compute Module 5", "U30B": "Compute Module 5",
                   "U16": "CP2102N", "U41": "STM32H7", "U42": None, "U6": "PCA9555", "U10": "RP2040",
                   "U9": "Compute Module 5", "J_PANEL": None, "C151": None, "U8": None}, fam
    assert fw == {"U101", "U1", "U102", "U30A", "U30B", "U16", "U41", "U42", "U6", "U10", "U9"}, sorted(fw)


def t_a_supply_input_split_across_nets_is_not_a_load():
    """R4T-D51 (e): a part's pins of one supply are joined inside it. DEFECTIVE: an STM32H753 with its VDD pin 11 on +5V_X
    and its VDD pin 27 on +3V3 carries +3V3 onto the rail through the part; 4836c42c passed pin 11 as a load, now it is
    UNDECIDED, named. An STM32H723, whose sheet is not held here (the H72x and H73x lines add VDDSMPS, VLXSMPS and VFBSMPS),
    has no table: its VDD on the rail is UNDECIDED (4836c42c read it with the H742/H743 rows, PASS). ACCEPTABLE: both VDD
    pins on the rail PASS."""
    tx = _on_rail({"U41": MCU}, {"+5V_X": [("U41", "11", "VDD")], "+3V3": [("U41", "27", "VDD")], "GND": [("U41", "10", "VSS")]})
    assert tx["ok"] is None and "'VDD') is a pin of a part whose pins firmware sets, and it is STM32H7's VDD, and its other " \
        "VDD pins sit on +3V3, off the rail: a part's pins of one supply are joined inside it" in tx["detail"], tx
    tx = _on_rail({"U42": H723}, {"+5V_X": [("U42", "11", "VDD")]})
    assert tx["ok"] is None and "U42 pin 11 (STM32H723VGT6 controller, 'VDD') is a pin of a part whose pins firmware sets, " \
        "and it names a supply, and no maker's pin table held here" in tx["detail"], tx
    # ACCEPTABLE
    tx = _on_rail({"U41": MCU}, {"+5V_X": [("U41", "11", "VDD"), ("U41", "27", "VDD")], "GND": [("U41", "10", "VSS")]})
    assert tx["ok"] is True, tx


# ROUND 6 EIGHTH PASS (R4T-D53 to R4T-D55; the review of the seventh pass, blocking 1 to 3). Each DEFECTIVE fixture below
# reads PASS on the seventh pass's file (7fa144a0) and says what the sixth pass's file (4836c42c) read; each ACCEPTABLE one
# passes on all three unless it says otherwise.
MCU_DESC = ("I/O supervisor STM32H743VIT6", "Package_QFP:LQFP-100_14x14mm_P0.5mm", "meshsat_ic:U41")
CM5_DESC = ("Slot S1 compute: CM5108032", "meshsat:CM5", "meshsat:Module")
CP2_DESC = ("USB-UART bridge CP2102N-A02-GQFN28", "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm", "meshsat_ic:U16")
CPU_DESC = ("Panel controller RP2040", "Package_DFN_QFN:QFN-56", "meshsat_ic:U10")       # board E's own symbol style
EXP_DESC = ("I2C expander PCA9555PW", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "meshsat_ic:U66")
TXS_RP = ("TXS0102 level shifter for the RP2040", "Package_SO:VSSOP-8", "Logic_LevelTranslator:TXS0102DCU")
_NOT_READ = "and the part is not read as one"
CM5_WL = ("Raspberry Pi CM5 8GB/64GB wireless", "meshsat:CM5", "meshsat:Module")     # the V2 device set's own words


def t_a_part_that_only_mentions_a_firmware_family_is_named_and_never_passed():
    """DEFECTIVE (the review of the seventh pass, blocking 1; R4T-F26): R4T-D52 anchored the firmware class to the start of
    the value or of the library symbol's name, and _second_sources() reads no pin of a part outside the classes it knows
    (R4T-F23), so a firmware part whose value begins with a descriptor sat on a gated rail as a silent load. Each of these
    read FAIL on 4836c42c and PASS on 7fa144a0, and now reads UNDECIDED, naming the family its value mentions and saying
    the part is not read as one: an 'I/O supervisor STM32H743VIT6' on a custom symbol (meshsat_ic:U41) with PA0 or VCAP on
    +5V_X, the rail EMCON switches off; 'Slot S1 compute: CM5108032' with pin 84 CM5_3.3V (a 600 mA output, CM5 datasheet
    3.4); a 'USB-UART bridge CP2102N' whose VDD is on the rail with its VREGIN on +5V_DEV (Table 3.6, the regulator's
    output); a 'Panel controller RP2040' on meshsat_ic:U10 (board E's symbol style) with VREG_VOUT or GPIO0; an 'I2C expander
    PCA9555PW' with IO0_0; a 'WeAct STM32H743VIT6 core board' with PA0 and a 'Seeed XIAO ESP32S3' with D0 (4836c42c read
    that one FAIL; its 3V3 pin UNDECIDED). Behind a 10 Ohm resistor the MCU's PA0 is UNDECIDED and named the same way
    (4836c42c: UNDECIDED as a firmware pin; 7fa144a0: PASS). On the gate path the same MCU on EMCON_HW is UNDECIDED and
    named by census() (4836c42c: FAIL; 7fa144a0: UNDECIDED without the family), and the fail-safe network names it too.
    CONTROL: the value led by the part number still FAILS. ACCEPTABLE, and
    outside the firmware class as before (R4T-D52): board B's J_PANEL (a connector, UNDECIDED on a rail as any connector
    that leaves the board), a PCIe coupling capacitor citing the CM5 datasheet (skipped, a capacitor) and a 'TXS0102 level
    shifter for the RP2040', whose pin on a rail is now named (UNDECIDED, 7fa144a0: PASS), never FAILED as a firmware pin."""
    for comps, nets, needle in (
            ({"U41": MCU_DESC}, {"+5V_X": [("U41", "23", "PA0")]}, "U41 pin 23 (I/O supervisor STM32H743VIT6, 'PA0') sits on "
             "the rail's conductor, and its value or library symbol mentions STM32H743VIT6, a family whose pins firmware "
             "sets, " + _NOT_READ + " (its library symbol 'U41' does not begin with a part number of that family"),
            ({"U41": MCU_DESC}, {"+5V_X": [("U41", "48", "VCAP")]}, "U41 pin 48 (I/O supervisor STM32H743VIT6, 'VCAP') sits "
             "on the rail's conductor, and its value or library symbol mentions STM32H743VIT6"),
            ({"U9": CM5_DESC}, {"+5V_X": [("U9", "84", "CM5_3.3V")]}, "U9 pin 84 (Slot S1 compute: CM5108032, 'CM5_3.3V') "
             "sits on the rail's conductor, and its value or library symbol mentions CM5108032, a family whose pins "
             "firmware sets, " + _NOT_READ),
            ({"U16": CP2_DESC}, {"+5V_X": [("U16", "6", "VDD")], "+5V_DEV": [("U16", "7", "VREGIN")]}, "U16 pin 6 (USB-UART "
             "bridge CP2102N-A02-GQ, 'VDD') sits on the rail's conductor, and its value or library symbol mentions "
             "CP2102N-A02-GQFN28"),
            ({"U77": CPU_DESC}, {"+5V_X": [("U77", "45", "VREG_VOUT")]}, "'VREG_VOUT') sits on the rail's conductor, and its "
             "value or library symbol mentions RP2040"),
            ({"U77": CPU_DESC}, {"+5V_X": [("U77", "2", "GPIO0")]}, "'GPIO0') sits on the rail's conductor, and its value or "
             "library symbol mentions RP2040"),
            ({"U66": EXP_DESC}, {"+5V_X": [("U66", "4", "IO0_0")]}, "'IO0_0') sits on the rail's conductor, and its value or "
             "library symbol mentions PCA9555PW"),
            ({"U41": MCU_DESC, "R91": ("10R", "R", "Device:R")},
             {"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("U41", "23", "PA0")]},
             "+5V_X through R91 (10R) to X_ALT: U41 pin 23 (I/O supervisor STM32H743VIT6, 'PA0') sits behind a resistor "
             "from it, and its value or library symbol mentions STM32H743VIT6"),
            ({"U41": ("WeAct STM32H743VIT6 core board", "meshsat:WeAct", "meshsat:WeAct_H743")}, {"+5V_X": [("U41", "23", "PA0")]},
             "'PA0') sits on the rail's conductor, and its value or library symbol mentions STM32H743VIT6"),
            ({"U70": ("Seeed XIAO ESP32S3", "meshsat:XIAO", "meshsat:XIAO_ESP32S3")}, {"+5V_X": [("U70", "1", "D0")]},
             "'D0') sits on the rail's conductor, and its value or library symbol mentions ESP32S3"),
            # ROUND 6 NINTH PASS (R4T-D56, R4T-F29; the review of the eighth pass, blocking 1): the module named without a
            # part number, as the sixth pass's '\bCM5\d*|Compute Module' found it. Each read FAIL on 4836c42c (UNDECIDED
            # behind the resistor) and PASS, silently, on 7fa144a0 and dd584cc9
            ({"U9": CM5_WL}, {"+5V_X": [("U9", "84", "CM5_3.3V")]}, "U9 pin 84 (Raspberry Pi CM5 8GB/64GB wire, 'CM5_3.3V') "
             "sits on the rail's conductor, and its value or library symbol mentions CM5, a family whose pins firmware sets, "
             + _NOT_READ),
            ({"U9": ("CM5", "meshsat:CM5", "meshsat:Module")}, {"+5V_X": [("U9", "84", "CM5_3.3V")]},
             "U9 pin 84 (CM5, 'CM5_3.3V') sits on the rail's conductor, and its value or library symbol mentions CM5, "),
            ({"U9": ("Raspberry Pi Compute Module (8GB)", "meshsat:CM5", "meshsat:Module")}, {"+5V_X": [("U9", "84", "CM5_3.3V")]},
             "'CM5_3.3V') sits on the rail's conductor, and its value or library symbol mentions Compute Module, a family "),
            ({"U9": ("Slot S1 compute: Raspberry Pi CM5 8GB", "meshsat:CM5", "meshsat:Module")},
             {"+5V_X": [("U9", "84", "CM5_3.3V")]}, "'CM5_3.3V') sits on the rail's conductor, and its value or library "
             "symbol mentions CM5, a family whose pins firmware sets, " + _NOT_READ),
            ({"U9": CM5_WL}, {"+5V_X": [("U9", "45", "GPIO17")]}, "U9 pin 45 (Raspberry Pi CM5 8GB/64GB wire, 'GPIO17') sits "
             "on the rail's conductor, and its value or library symbol mentions CM5"),
            ({"U9": CM5_WL, "R91": ("10R", "R", "Device:R")}, {"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", ""),
                                                                                                   ("U9", "45", "GPIO17")]},
             "+5V_X through R91 (10R) to X_ALT: U9 pin 45 (Raspberry Pi CM5 8GB/64GB wire, 'GPIO17') sits behind a resistor "
             "from it, and its value or library symbol mentions CM5")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), nets, tx)
    # the gate path: census() names the family, and so does the fail-safe network, powered and unpowered
    r = T.judge({"B": _edit(_power_board({"and", "expander_sw"}), comps={"U41": MCU_DESC},
                            nets={"EMCON_HW": [("U41", "33", "PC5")]})},
                table=TX_POWER, accessories=[], receivers=[], owed=[])
    ln = _line(r)
    assert ln["ok"] is None and "B U41 pin 33 (I/O supervisor STM32H743VIT6) on EMCON_HW: an active pin no held document " \
        "shows to be an input; its value or library symbol mentions STM32H743VIT6, a family whose pins firmware sets, " \
        + _NOT_READ in ln["detail"], ln
    nl = _edit(_power_board({"and"}), comps={"U41": MCU_DESC}, nets={"EMCON_HW": [("U41", "33", "PC5")]})
    for up, words in ((True, "an active pin no held document bounds"),
                      (False, "an unpowered part whose off-state current no held document bounds")):
        net = T._network({"B": nl}, [("B", "EMCON_HW")], 0, dict(rail_up=lambda k, n: True, board_up=lambda k, up=up: up, cut=set()))
        assert [u for u in net["unsure"] if u.startswith("B U41 pin 33 (I/O supervisor STM32H743VIT6): %s; its value or "
                "library symbol mentions STM32H743VIT6, a family whose pins firmware sets, %s" % (words, _NOT_READ))], net["unsure"]
    # CONTROL: led by the part number, the same pin FAILS as a firmware pin
    tx = _on_rail({"U41": ("STM32H743VIT6", "Package_QFP:LQFP-100_14x14mm_P0.5mm", "meshsat_ic:U41")},
                  {"+5V_X": [("U41", "23", "PA0")]})
    assert tx["ok"] is False and "is a pin whose direction firmware sets, on the rail" in tx["detail"], tx
    # ACCEPTABLE: outside the firmware class, named where active, never failed as firmware
    parts = {"J_PANEL": ("panel ribbon to PCB-C C7 (IDC 2x13): the RP2040 panel controller's USB", "Connector:IDC",
                         "Connector_Generic:Conn_02x13_Odd_Even"),
             "C151": ("220n 16V (PCIe AC coupling, CM5 datasheet 2.3.1)", "Capacitor_SMD:C_0402", "Device:C"),
             "U8": TXS_RP}
    nl = _edit(_power_board(set()), comps=parts)
    # C151's value cites the CM5 datasheet, which FW_MENTION finds since R4T-D56 (the sixth pass's 'CM5'); every walk skips a
    # capacitor by its reference before the mention test, so it still PASSES on a rail, below
    assert {r: (T.software_io(nl, r), T.fw_mention(nl, r)) for r in parts} == \
        {"J_PANEL": (False, "RP2040"), "C151": (False, "CM5"), "U8": (False, "RP2040")}
    # CONTROL (R4T-D56): parts whose values mention the module but begin with their own part numbers stay firmware parts
    # and are never named as a mention
    nl = _edit(_power_board(set()), comps={"U101": PI7C, "U1": KSZ_CM5})
    assert {r: (T.software_io(nl, r), T.fw_mention(nl, r)) for r in ("U101", "U1")} == \
        {"U101": (True, None), "U1": (True, None)}
    tx = _on_rail({"U8": TXS_RP}, {"+5V_X": [("U8", "5", "VCCB")]})
    assert tx["ok"] is None and "U8 pin 5 (TXS0102 level shifter for the , 'VCCB') sits on the rail's conductor, and " \
        "its value or library symbol mentions RP2040" in tx["detail"] and "firmware sets, on the rail" not in tx["detail"], tx
    tx = _on_rail({"C151": parts["C151"]}, {"+5V_X": [("C151", "1", "")]})
    assert tx["ok"] is True, tx


def t_a_supply_rows_pins_are_every_pin_its_maker_numbers_there():
    """DEFECTIVE (the review of the seventh pass, blocking 2; R4T-F27): R4T-D51 (e)'s split check and the tied-partner lookup
    kept only the sibling pins whose symbol name agreed with the maker's pin number, so a sibling misnamed or unnamed on
    another net was dropped and the split read PASS. CM5 datasheet 4.2 Table 4 makes pins 77 to 87 all '5V (Input) ... main
    power input', one supply inside the module. Each of these read PASS on 4836c42c and on 7fa144a0 and is now UNDECIDED,
    naming the pin, its number, the row and the symbol's name: pins 77 and 79 '5V' on +5V_X with 81 to 87 named '+5V' on
    +5V_S1; the same with 81 to 87 unnamed; VBAT (76) and pin 77 '5V' on +5V_X with 79 to 87 named '+5V' on +5V_S1. VBAT on
    the rail with every 5V pin named '+5V' on +5V_S1 is UNDECIDED on both files and now names the pins (7fa144a0 said its
    5V was 'not on this netlist'). ACCEPTABLE: every 5V pin on the rail, alone or with VBAT, PASSES on all three files."""
    for nets, needle in (
            ({"+5V_X": [("U30A", "77", "5V"), ("U30A", "79", "5V")], "+5V_S1": [("U30A", p, "+5V") for p in ("81", "83", "85", "87")]},
             "U30A pin 77 (Amphenol 10164227-1004A1RLF re, '5V') is a pin of a part whose pins firmware sets, and it is "
             "Compute Module 5's 5V, and the maker's pin number puts pin 81 (the symbol calls it '+5V') on +5V_S1, pin 83 "
             "(the symbol calls it '+5V') on +5V_S1, pin 85 (the symbol calls it '+5V') on +5V_S1, pin 87 (the symbol calls "
             "it '+5V') on +5V_S1 in its 5V row, off the rail, and the symbol does not give them that row's name"),
            ({"+5V_X": [("U30A", "77", "5V"), ("U30A", "79", "5V")], "+5V_S1": [("U30A", p, "") for p in ("81", "83", "85", "87")]},
             "and the maker's pin number puts pin 81 (unnamed in the symbol) on +5V_S1, pin 83 (unnamed in the symbol) on "
             "+5V_S1, pin 85 (unnamed in the symbol) on +5V_S1, pin 87 (unnamed in the symbol) on +5V_S1 in its 5V row, off "
             "the rail"),
            ({"+5V_X": [("U30A", "76", "VBAT"), ("U30A", "77", "5V")],
              "+5V_S1": [("U30A", p, "+5V") for p in ("79", "81", "83", "85", "87")]},
             "U30A pin 76 (Amphenol 10164227-1004A1RLF re, 'VBAT') is a pin of a part whose pins firmware sets, and it is "
             "Compute Module 5's VBAT, and the maker's pin number puts pin 79 (the symbol calls it '+5V') on +5V_S1"),
            ({"+5V_X": [("U30A", "76", "VBAT")], "+5V_S1": [("U30A", p, "+5V") for p in ("77", "79", "81", "83", "85", "87")]},
             "the RTC's battery charger, 'a constant-current (3 mA) constant-voltage charger'")):
        tx = _on_rail({"U30A": CM5_RA}, nets)
        row = "in the 5V row it is tied to, off the rail" if "VBAT" in str(nets["+5V_X"]) else "in its 5V row, off the rail"
        assert tx["ok"] is None and needle in tx["detail"] and row in tx["detail"], (nets, tx)
    # ACCEPTABLE
    for nets in ({"+5V_X": CM5_5V}, {"+5V_X": [("U30A", "76", "VBAT")] + CM5_5V}):
        tx = _on_rail({"U30A": CM5_RA}, nets)
        assert tx["ok"] is True, (nets, tx)


def t_an_stm32h7_vdd_is_a_load_only_with_its_vbat_on_the_rail_on_ground_or_nowhere():
    """DEFECTIVE (the review of the seventh pass, blocking 3; R4T-F28): the reverse of R4T-D51's tie. DS12110 Rev 10 Figure
    15 (page 103) draws 'VBAT charging' between the VDD and VBAT pins with no direction marked, Table 95 names it RBC,
    'Battery charging resistor', 5 or 1.5 kOhm by VBRS, and neither held sheet says it opens when VDD falls; so once
    firmware has switched charging on, a cell or a live net on VBAT can feed a gated rail that carries VDD. An STM32H753's
    VDD and VDDA on +5V_X with VBAT on +3V3_AON read PASS on 4836c42c and on 7fa144a0 and are now UNDECIDED, citing Figure
    15 and Table 95 (UNDECIDED and not FAIL, because the direction is not documented); so is board B's STM32H743 with VBAT
    on a cell's net. ACCEPTABLE, PASS on all three files: VDD with VBAT on the rail; VBAT on ground; VBAT unconnected; VBAT
    not drawn."""
    for mcu, cell in ((MCU, "+3V3_AON"), (H743, "+VBAT_CELL")):
        tx = _on_rail({"U41": mcu}, {"+5V_X": [("U41", "11", "VDD"), ("U41", "21", "VDDA")], cell: [("U41", "6", "VBAT")],
                                     "GND": [("U41", "10", "VSS")]})
        assert tx["ok"] is None and "'VDD') is a pin of a part whose pins firmware sets, and it is STM32H7's VDD, and its " \
            "VBAT is on %s, off the rail, and the held sheets draw the battery charger between VDD and VBAT with no " \
            "direction marked (DS12110 Rev 10 Figure 15, page 103, 'VBAT charging', DS12117 Rev 9 Figure 14) and name it a " \
            "resistor (DS12110 Table 95, DS12117 Table 94: RBC 'Battery charging resistor'" % cell in tx["detail"], (mcu[0], tx)
    # ACCEPTABLE
    for nets in ({"+5V_X": [("U41", "11", "VDD"), ("U41", "21", "VDDA"), ("U41", "6", "VBAT")], "GND": [("U41", "10", "VSS")]},
                 {"+5V_X": [("U41", "11", "VDD")], "GND": [("U41", "6", "VBAT"), ("U41", "10", "VSS")]},
                 {"+5V_X": [("U41", "11", "VDD")], "unconnected-(U41-VBAT-Pad6)": [("U41", "6", "VBAT")], "GND": [("U41", "10", "VSS")]},
                 {"+5V_X": [("U41", "11", "VDD")], "GND": [("U41", "10", "VSS")]}):
        tx = _on_rail({"U41": MCU}, nets)
        assert tx["ok"] is True, (nets, tx)


# ROUND 6 NINTH PASS (R4T-D57 to R4T-D59; the review of the eighth pass, blocking 2 and minor 3 and 4). Each DEFECTIVE case
# below read PASS on the sixth, seventh and eighth passes' files (4836c42c, 7fa144a0, dd584cc9) unless it says otherwise;
# each ACCEPTABLE one passes on all four.
_SEQ = ("the maker's power sequence ties VDDA, VDD33USB and VDD50USB to VDD: 'When VDD is below 1 V, other power supplies "
        "(VDDA, VDD33USB, VDD50USB) must remain below VDD + 300 mV'")
_FIG3 = "(DS12110 Rev 10 3.5.1, page 28, and Figure 3, which labels that region 'Invalid supply area'"


def t_an_stm32h7_vdd_is_a_load_only_with_every_supply_its_power_sequence_ties_to_it():
    """DEFECTIVE (the review of the eighth pass, blocking 2; R4T-F30): R4T-D55 read VDD's join to VBAT only. The same section
    it cites, DS12110 Rev 10 3.5.1 (page 28, Figure 3, note 1) and DS12117 Rev 9 3.5.1 (page 27, Figure 2 on page 28), says
    'When VDD is below 1 V, other power supplies (VDDA, VDD33USB, VDD50USB) must remain below VDD + 300 mV', and that 'During
    the power-down phase, VDD can temporarily become lower than other supplies only if the energy provided to the
    microcontroller remains below 1 mJ'; Figure 3 labels the region 'Invalid supply area'. That is what EMCON makes when it
    opens the switch of a rail carrying VDD while any of the three stays up. The review's four probes read PASS with an
    empty detail on all three older files and now read UNDECIDED, naming the partner, its net and 3.5.1: an STM32H753 with
    VDD and VBAT on +5V_X and VDDA on +3V3; an STM32H743VIT6 with VDD on +5V_X, VDDA on +3V3A and VBAT on ground; VDD, VDDA
    and VBAT on +5V_X with VDD33USB on +3V3; the same with VDD50USB on +5V_DEV. NAMED, not a new verdict: VDD33USB on the
    rail read UNDECIDED before as a supply word the table did not list, and now says what 3.5.1 makes it. ACCEPTABLE, PASS on
    all four files: VDD, VDDA and VBAT together on the rail (VDD33USB and VDD50USB not drawn); VDDA alone on the rail with VDD
    and VBAT on +3V3 ('When VDD is above 1 V, all power supplies are independent'); VDD and VDDA on the rail with VBAT on
    ground; and VDD, VDDA and VBAT on the rail with VDD33USB and VDD50USB unconnected."""
    G = [("U41", "10", "VSS")]
    for mcu, nets, partner, where in (
            (MCU, {"+5V_X": [("U41", "11", "VDD"), ("U41", "6", "VBAT")], "+3V3": [("U41", "21", "VDDA")]}, "VDDA", "+3V3"),
            (("STM32H743VIT6", "Package_QFP:LQFP-100_14x14mm_P0.5mm", "meshsat_ic:U41"),
             {"+5V_X": [("U41", "11", "VDD")], "+3V3A": [("U41", "21", "VDDA")], "GND": [("U41", "6", "VBAT")]}, "VDDA", "+3V3A"),
            (MCU, {"+5V_X": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "21", "VDDA")], "+3V3": [("U41", "50", "VDD33USB")]},
             "VDD33USB", "+3V3"),
            (MCU, {"+5V_X": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "21", "VDDA")],
                   "+5V_DEV": [("U41", "49", "VDD50USB")]}, "VDD50USB", "+5V_DEV")):
        nets = dict(nets); nets["GND"] = nets.get("GND", []) + G
        tx = _on_rail({"U41": mcu}, nets)
        assert tx["ok"] is None and "'VDD') is a pin of a part whose pins firmware sets, and it is STM32H7's VDD, and its " \
            "%s is on %s, off the rail, and %s" % (partner, where, _SEQ) in tx["detail"] and _FIG3 in tx["detail"] and \
            "DS12117 Rev 9 3.5.1, page 27, and Figure 2, page 28" in tx["detail"], (mcu[0], nets, tx)
    # NAMED: VDD33USB on the rail says what 3.5.1 makes it (UNDECIDED on the older files too, as an unlisted supply word)
    tx = _on_rail({"U41": MCU}, {"+5V_X": [("U41", "50", "VDD33USB")], "+3V3": [("U41", "11", "VDD"), ("U41", "6", "VBAT")],
                                 "GND": G})
    assert tx["ok"] is None and "it is STM32H7's VDD33USB, which is the output of the USB regulator from VDD50USB or, with " \
        "that regulator bypassed, a 3.3 V supply input" in tx["detail"], tx
    # ACCEPTABLE
    for nets in ({"+5V_X": [("U41", "11", "VDD"), ("U41", "21", "VDDA"), ("U41", "6", "VBAT")], "GND": G},
                 {"+5V_X": [("U41", "21", "VDDA")], "+3V3": [("U41", "11", "VDD"), ("U41", "6", "VBAT")], "GND": G},
                 {"+5V_X": [("U41", "11", "VDD"), ("U41", "21", "VDDA")], "GND": G + [("U41", "6", "VBAT")]},
                 {"+5V_X": [("U41", "11", "VDD"), ("U41", "21", "VDDA"), ("U41", "6", "VBAT")], "GND": G,
                  "unconnected-(U41-VDD33USB-Pad50)": [("U41", "50", "VDD33USB")],
                  "unconnected-(U41-VDD50USB-Pad49)": [("U41", "49", "VDD50USB")]}):
        tx = _on_rail({"U41": MCU}, nets)
        assert tx["ok"] is True, (nets, tx)


def t_a_logic_gates_push_pull_output_on_a_gated_rail_is_a_second_feed():
    """DEFECTIVE (the review of the eighth pass, minor 3; R4T-F31): LOGIC gives every gate's output pin from its maker's pin
    table, and _second_sources() read none, so a plain '74LVC1G34 buffer' (TI SCES519O Table 4-1: Y 4) with Y on +5V_X,
    the rail EMCON switches off, read PASS on all three older files. A push-pull output drives high from the gate's own VCC,
    so on the conductor it now FAILS, naming the gate and its sheet, as an OUTPUT_FN pin does; so does an SN74LVC32A OR's
    1Y (pin 3, SCAS286U Table 4-1). Behind a 10 Ohm resistor it is UNDECIDED, as a firmware pin is. A gate on a land its
    map is not for is UNDECIDED by any pin (census() reads it so). ACCEPTABLE, PASS on all four files: the gate's VCC or
    its input on the rail, and an open-drain 74LVC1G07's Y there (it only ever pulls low); board A's sense network
    (_pa_sensed) is unchanged by t_a_power_stage_behind_its_sense_shunt_is_read_like_the_rail."""
    tx = _on_rail({"U55": BUF1}, {"+5V_X": [("U55", "4", "Y")], "+3V3": [("U55", "5", "VCC")], "GND": [("U55", "3", "GND")]})
    assert tx["ok"] is False and "+5V_X: U55 pin 4 (74LVC1G34 buffer, 'Y') is the push-pull output of a BUF gate (TI " \
        "SN74LVC1G34): driven high it feeds the rail from the gate's own supply with the rail's switch off" in tx["detail"], tx
    tx = _on_rail({"U56": OR4}, {"+5V_X": [("U56", "3", "1Y")], "+3V3": [("U56", "14", "VCC")], "GND": [("U56", "7", "GND")]})
    assert tx["ok"] is False and "U56 pin 3 (SN74LVC32APWR quad OR: module , '1Y') is the push-pull output of an OR gate (TI " \
        "SN74LVC32A" in tx["detail"], tx
    tx = _on_rail({"U55": BUF1, "R91": ("10R", "R", "Device:R")},
                  {"+5V_X": [("R91", "1", "")], "X_ALT": [("R91", "2", ""), ("U55", "4", "Y")], "+3V3": [("U55", "5", "VCC")]})
    assert tx["ok"] is None and "+5V_X through R91 (10R) to X_ALT: U55 pin 4 (74LVC1G34 buffer, 'Y') is the push-pull output " \
        "of a BUF gate (TI SN74LVC1G34), behind a resistor from it" in tx["detail"], tx
    tx = _on_rail({"U55": ("74LVC1G34 buffer", "Package_SO:SOIC-8", "meshsat_ic:U")}, {"+5V_X": [("U55", "4", "Y")]})
    assert tx["ok"] is None and "U55 pin 4 (74LVC1G34 buffer, 'Y') is a pin of a 74LVC1G34 buffer on a land its pin map is " \
        "not for" in tx["detail"], tx
    # ACCEPTABLE
    for comps, nets in (({"U55": BUF1}, {"+5V_X": [("U55", "5", "VCC")], "GND": [("U55", "3", "GND")]}),
                        ({"U55": BUF1}, {"+5V_X": [("U55", "2", "A")], "+3V3": [("U55", "5", "VCC")]}),
                        ({"U57": OD1}, {"+5V_X": [("U57", "4", "Y")], "+3V3": [("U57", "5", "VCC")]})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (comps, nets, tx)


def t_a_supply_pin_its_maker_joins_to_an_io_is_not_a_load_while_that_io_is_held_elsewhere():
    """DEFECTIVE (the review of the eighth pass, minor 4; R4T-F32): the walk read only the pins of a part that sit on the
    gated rail, and a PCA9555's VCC is a load by its row, while TI SCPS131J Figure 8-2 (Simplified Schematic Of P-Port I/Os,
    page 15) draws a 100 kOhm resistor between VCC and every P-port pin (6.5's IIL, -100 uA at VI = GND, page 7, is its
    current): a P-port pin held up by another part feeds VCC, and the rail, once EMCON has opened the rail's switch. The
    same holds for an RP2040's ADC input and IOVDD (RP2040 Datasheet 2.9.5, page 152: 'Voltages greater than IOVDD will
    result in leakage currents through the ESD protection diodes'). Each read PASS on all three older files and now reads
    UNDECIDED, naming the pin, its net and the sheet: a PCA9555PW with VDD on +5V_X and IO0_0 on KSZ_RST pulled up to +3V3;
    the same with IO1_7 driven by a 74LVC1G34's output; an RP2040 with IOVDD on +5V_X and GPIO26_ADC0 on a sensor net an
    op-amp drives. ACCEPTABLE, PASS on all four files: every P-port pin unconnected or on ground; a P-port pin sourcing an
    LED whose cathode is on ground behind nothing else (the P-port drives the LED's anode; the ninth and tenth passes said 'sinking'); a P-port pin on a net that carries only a capacitor and a pull-down;
    and the RP2040's IOVDD with its ADC inputs unconnected."""
    for comps, nets, needle in (
            ({"U66": EXP, "R5": ("10k", "R", "Device:R")},
             {"+5V_X": [("U66", "24", "VDD")], "KSZ_RST": [("U66", "4", "IO0_0"), ("R5", "1", "")], "+3V3": [("R5", "2", "")],
              "GND": [("U66", "12", "VSS")]},
             "U66 pin 24 (PCA9555PW 0x20: outputs, 'VDD') is a pin of a part whose pins firmware sets, and it is PCA9555's VDD, "
             "and its P-port pin IO0_0 (pin 4) is on KSZ_RST, off the rail, where R5 pin 1 (10k) is not shown to be a load; "
             "and TI SCPS131J Figure 8-2 (Simplified Schematic Of P-Port I/Os, page 15) draws a 100 kOhm resistor between VCC "
             "and every P-port pin"),
            ({"U66": EXP, "U55": BUF1},
             {"+5V_X": [("U66", "24", "VDD")], "CTRL": [("U66", "20", "IO1_7"), ("U55", "4", "Y")], "+3V3": [("U55", "5", "VCC")],
              "GND": [("U66", "12", "VSS"), ("U55", "3", "GND")]},
             "its P-port pin IO1_7 (pin 20) is on CTRL, off the rail, where U55 pin 4 (74LVC1G34 buffer) is not shown to be "
             "a load"),
            ({"U77": CPU, "U2": ("TLV9062 sensor amplifier", "Package_SO:VSSOP-8", "X:Y")},
             {"+5V_X": [("U77", "1", "IOVDD")], "VSENSE": [("U77", "38", "GPIO26_ADC0"), ("U2", "1", "OUT1")],
              "GND": [("U77", "57", "GND")]},
             "and it is RP2040's IOVDD, and its ADC input pin GPIO26_ADC0 (pin 38) is on VSENSE, off the rail, where U2 pin 1 "
             "(TLV9062 sensor amplifier) is not shown to be a load; and RP2040 Datasheet 2.9.5 ADC Supply (page 152): 'the "
             "voltage on the ADC analogue inputs must not exceed IOVDD")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), nets, tx)
    # ACCEPTABLE
    led = ("red LED", "LED_SMD:LED_0603", "Device:LED")
    for comps, nets in (
            ({"U66": EXP}, {"+5V_X": [("U66", "24", "VDD")], "GND": [("U66", "12", "VSS"), ("U66", "5", "IO0_1")],
                            "unconnected-(U66-IO0_0-Pad4)": [("U66", "4", "IO0_0")]}),
            ({"U66": EXP, "LED9": led}, {"+5V_X": [("U66", "24", "VDD")], "LED_A": [("U66", "4", "IO0_0"), ("LED9", "2", "A")],
                                         "GND": [("U66", "12", "VSS"), ("LED9", "1", "K")]}),
            ({"U66": EXP, "C9": ("100n", "C", "Device:C"), "R9": ("100k", "R", "Device:R")},
             {"+5V_X": [("U66", "24", "VDD")], "SENSE_IN": [("U66", "4", "IO0_0"), ("C9", "1", ""), ("R9", "1", "")],
              "GND": [("U66", "12", "VSS"), ("C9", "2", ""), ("R9", "2", "")]}),
            ({"U77": CPU}, {"+5V_X": [("U77", "1", "IOVDD")], "GND": [("U77", "57", "GND")],
                            "unconnected-(U77-GPIO26_ADC0-Pad38)": [("U77", "38", "GPIO26_ADC0")]})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(comps), nets, tx)


# ROUND 6 TENTH PASS (R4T-D60 to R4T-D62; the review of the ninth pass, its two items and its suggestion to close the class).
# Each DEFECTIVE case below reads PASS on the ninth pass's file (df382343) and on the sixth, seventh and eighth passes' files
# (4836c42c, 7fa144a0, dd584cc9) unless it says otherwise; each ACCEPTABLE one passes on all five.
_LDO = ("and the held sheets bound VDDLDO by VDD: Table 24 'General operating conditions' gives VDDLDO, 'Supply voltage for "
        "the internal regulator', the operating condition 'VDDLDO <= VDD'")


def t_an_stm32h7_vdd_is_a_load_only_with_its_vddldo_on_the_rail_on_ground_or_nowhere():
    """DEFECTIVE (the review of the ninth pass, item 1; R4T-F33): the ninth pass's header excused VDDLDO beside VDD because
    3.5.1's sequence names VDDA, VDD33USB and VDD50USB, not VDDLDO; the same sheets tie it: DS12110 Rev 10 6.3.1 Table 24
    'General operating conditions' (page 106) gives VDDLDO, 'Supply voltage for the internal regulator', the operating
    condition 'VDDLDO <= VDD', DS12117 Rev 9 Table 23 (page 106) the same row, and DS12110 Table 9 note 8 (page 87): 'When it
    is not available on a package, the VDDLDO pin is internally tied to VDD'. With EMCON opening the switch of a rail that
    carries VDD while VDDLDO stays up, VDDLDO ends above VDD. The review's probes B2-6 (an STM32H753 with VDD, VDDA and VBAT on
    +5V_X and VDDLDO on +3V3) and B2-7 (the STM32H743VIT6 with VDDLDO on +3V3_AON) read PASS with an empty detail on all four
    older files and now read UNDECIDED, naming VDDLDO, Table 24 and Table 23. The row is read by the symbol's pin name, as
    the STM32H7 rows are (limit (6)); pin 75 is the review's number. ACCEPTABLE, PASS on all five files: VDDLDO alone on the
    rail with VDD, VDDA and VBAT on +3V3 (VDDLDO <= VDD holds as VDDLDO falls, and 3.5.1: 'When VDD is above 1 V, all power
    supplies are independent'); VDDLDO on ground; VDDLDO unconnected; all four on the rail."""
    G = [("U41", "10", "VSS")]
    on_rail = [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "21", "VDDA")]
    for mcu, where in ((MCU, "+3V3"), (H743, "+3V3_AON")):
        tx = _on_rail({"U41": mcu}, {"+5V_X": list(on_rail), where: [("U41", "75", "VDDLDO")], "GND": G})
        assert tx["ok"] is None and "'VDD') is a pin of a part whose pins firmware sets, and it is STM32H7's VDD, and its " \
            "VDDLDO is on %s, off the rail, %s" % (where, _LDO) in tx["detail"] and "DS12110 Rev 10 6.3.1 Table 24, page 106; " \
            "DS12117 Rev 9 6.3.1 Table 23, page 106" in tx["detail"] and "Table 9 note 8, page 87" in tx["detail"], (mcu[0], tx)
    # ACCEPTABLE
    for nets in ({"+5V_X": [("U41", "75", "VDDLDO")], "+3V3": list(on_rail), "GND": G},
                 {"+5V_X": list(on_rail), "GND": G + [("U41", "75", "VDDLDO")]},
                 {"+5V_X": list(on_rail), "unconnected-(U41-VDDLDO-Pad75)": [("U41", "75", "VDDLDO")], "GND": G},
                 {"+5V_X": on_rail + [("U41", "75", "VDDLDO")], "GND": G}):
        tx = _on_rail({"U41": MCU}, nets)
        assert tx["ok"] is True, (nets, tx)


_VREF_WORDS = ("off the rail, and the module's maker ties GPIO_VREF to the module's own supplies and bounds any other supply "
               "on it by them: 'GPIO_VREF must be connected to either CM5_3.3v or CM5_1.8v.")
REG25 = ("AP2112K-2.5 GPIO reference", "Package_TO_SOT_SMD:SOT-23-5", "X:Y")


def t_a_compute_modules_5v_is_a_load_only_with_gpio_vref_on_its_own_outputs():
    """DEFECTIVE (the review of the ninth pass, item 2; R4T-F34): the Compute Module 5 datasheet, the file FW_PIN_TABLES
    cites, says in 2.9 (page 11) 'GPIO_VREF must be connected to either CM5_3.3v or CM5_1.8v. It's possible to use 2.5 V
    signalling by supplying an external 2.5 V supply to GPIO_VREF. This external supply must only be active while CM5_1.8v is
    on and must be fully discharged within 1 ms after CM5_1.8v is going low', and in 3.1 (page 15) 'No pins should be powered
    before the 5 V rail is active'. With EMCON opening the switch of a rail that carries the module's 5V (pins 77 to 87 odd),
    CM5_1.8V goes down while an external GPIO_VREF stays up. The review's probes read PASS with an empty detail on the four
    older files and now read UNDECIDED, quoting 2.9 and 3.1: GPIO_VREF (pin 78) on +2V5_EXT with a regulator's output; the
    rv13 probe M6, GPIO_VREF on +1V8_X; and GPIO_VREF on the module's own +3V3_CM1 with pins 84 and 86 where a regulator's
    output feeds that net too. ACCEPTABLE, PASS on all five files: board B's form, GPIO_VREF with pins 84 and 86 on
    +3V3_CM1; GPIO_VREF with pins 88 and 90 on +1V8_CM1; GPIO_VREF on ground, unconnected, or on the rail with the 5V (the
    datasheet's pin 78 row forbids the last two, which is no EMCON question). And on board B's own committed netlist, where
    +3V3_CM1 also carries two capacitors, the LED_nPWR buffer Q101 (a BC857 whose base R149 reaches only the module's pin 95
    and whose collector R150 reaches only LED17 to ground), the gates of Q102 to Q105 and pulls to signal nets: the tenth pass
    read each module's 5V as a load if its slot rail were gated (no option gates one today); *changed in the eleventh pass
    (R4T-D64): the pulls are read through now, and behind six of them sit the fan connector J_FAN1, the TPS62933's enable
    U105 and the level shifters Q102 to Q105, which the reading cannot show unable to feed +3V3_CM1, so each module's 5V
    reads UNDECIDED there, a false UNDECIDED named in limit (3) of the header's list; the LED buffer Q101, the capacitors,
    the FET gates and the LED pull R148 are still read as unable to feed it.*"""
    V5 = [("U30A", p, "5V") for p in ("77", "79", "81", "83", "85", "87")]
    for comps, nets, needle in (
            ({"U30A": CM5_RA, "U70": REG25}, {"+5V_X": list(V5), "+2V5_EXT": [("U30A", "78", "GPIO_VREF"), ("U70", "5", "VOUT")]},
             "its GPIO_VREF is on +2V5_EXT (no supply output of the part itself is on it), "),
            ({"U30A": CM5_RA}, {"+5V_X": list(V5), "+1V8_X": [("U30A", "78", "GPIO_VREF")]},
             "its GPIO_VREF is on +1V8_X (no supply output of the part itself is on it), "),
            ({"U30A": CM5_RA, "U70": REG25},
             {"+5V_X": list(V5), "+3V3_CM1": [("U30A", "78", "GPIO_VREF"), ("U30A", "84", "CM5_3.3V"), ("U30A", "86", "CM5_3.3V"),
                                               ("U70", "5", "VOUT")]},
             "its GPIO_VREF is on +3V3_CM1 (besides its CM5_3.3V, U70 pin 5 (AP2112K-2.5 GPIO reference, 'VOUT'), an output "
             "is not shown to be unable to feed it), ")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and ("U30A pin 77 (Amphenol 10164227-1004A1RLF re, '5V') is a pin of a part whose pins firmware "
                                     "sets, and it is Compute Module 5's 5V, and " + needle + _VREF_WORDS) in tx["detail"] \
            and "(CM5 datasheet 2.9, page 11)" in tx["detail"] and "(3.1 Power-up sequencing, page 15" in tx["detail"], (nets, tx)
    # ACCEPTABLE
    for nets in ({"+5V_X": list(V5), "+3V3_CM1": [("U30A", "78", "GPIO_VREF"), ("U30A", "84", "CM5_3.3V"), ("U30A", "86", "CM5_3.3V")]},
                 {"+5V_X": list(V5), "+1V8_CM1": [("U30A", "78", "GPIO_VREF"), ("U30A", "88", "CM5_1.8V"), ("U30A", "90", "CM5_1.8V")]},
                 {"+5V_X": list(V5), "GND": [("U30A", "78", "GPIO_VREF")]},
                 {"+5V_X": list(V5), "unconnected-(U30A-GPIO_VREF-Pad78)": [("U30A", "78", "GPIO_VREF")]},
                 {"+5V_X": V5 + [("U30A", "78", "GPIO_VREF")]}):
        tx = _on_rail({"U30A": CM5_RA}, nets)
        assert tx["ok"] is True, (nets, tx)
    # board B's own drawing, read from the committed netlist
    import harness
    nl = T.parse_netlist(harness.need(os.path.join(os.path.dirname(TOOLS), "pcb-b-compute-b19", "out", "pcb-b-compute.net"),
                                      "board B's committed netlist"))
    for ref, slot in (("U30A", "1"), ("U31A", "2"), ("U32A", "3")):
        assert nl["pin"][(ref, "78")] == "+3V3_CM%s" % slot and nl["pin"][(ref, "84")] == "+3V3_CM%s" % slot, ref
        v, why = T.fw_pin_role(nl, ref, "77", "5V", nl["pin"][(ref, "77")])
        assert v == "undecided" and ("its GPIO_VREF is on +3V3_CM%s (besides its CM5_3.3V, " % slot) in why \
            and ("a pull to FAN_PWM%s, behind which J_FAN%s pin 4" % (slot, slot)) in why, (ref, v, why[:600])
    src = T._net_sources(nl, "U30A", "+3V3_CM1")
    assert sorted(x.split(" pin ")[0] for x in src) == ["R111", "R151", "R154", "R155", "R156", "R157"], src
    # *changed in the twelfth pass (R4T-D71): behind R111 the AP64500's enable U104 pin 3 is named first now, a current
    # source its maker states (DS41979 3 Enable), which the eleventh pass skipped; the TPS62933 U105 is still named*
    assert "behind which U104 pin 3 (AP64500SP-13 5 A buck" in src[0] and "its maker states a current sourced out of the pin" \
        in src[0] and "U105 pin 2 (TPS62933DRLR" in src[0] and "behind which Q102 pin 2 (2N7002, 'S'), a channel from " \
        "PI_SHDN_REQ" in src[2], src
    assert T._bjt_pins(nl, "Q101") == {"B": "1", "C": "3", "E": "2"}


def t_every_other_supply_pin_of_a_part_on_a_gated_rail_is_read():
    """DEFECTIVE (the review of the ninth pass, its suggestion; R4T-D62, R4T-F35, R4T-F36): the ninth pass read a supply
    input's joins only where a `reverse` or `backfeed` row named them, so each review found one more. Now a supply input on
    the rail is UNDECIDED while ANY other supply pin of the part sits on a live net off the rail's conductor, unless that net
    is fed only by the part's own outputs made from a supply on the rail, or a sentence of the maker's lets the two fall in
    that order. Each of these read PASS on all four older files unless it says otherwise, and reads UNDECIDED now: an
    STM32H7's VDDA on the rail with VREF+ on an external reference (Table 87 and 89: VREF+ at most VDDA); its VDD50USB on the
    rail with VDD33USB on +3V3 and VDD not drawn (3.5.1's independence holds only 'When VDD is above 1 V'); its VDDLDO on the
    rail with VDDA on +3V3 and VDD not drawn; a CP2102N's VREGIN on the rail with its VDD on a net a regulator also feeds
    (the reverse of the tie, limit (3) of the ninth pass); its VREGIN and VDD on the rail with VIO on +1V8 ('Operating
    Supply Voltage on VIO', 1.71 V to VDD, Table 3.1); with VBUS on +5V_DEV (2.3: 'high VBUS pin leakage current ... while
    the device is not powered'; the sixth pass's ACCEPTABLE case, R4T-F35); a Compute Module 5's GPIO_VREF on the rail with
    its 5V on +5V_S1 (the case R4T-D51/D52 limit (4) named and the case table read PASS); its 5V on the rail with a pin 100
    named '+3V3_AUX' on +3V3_AUX, a supply word the table does not place; and its 5V on the rail with its own CM5_3.3V net fed
    by a regulator too. ACCEPTABLE, PASS on all five files: an STM32H7's VDDA alone on the rail with VDD, VBAT and VDDLDO on
    +3V3 and VCAP on its capacitor ('When VDD is above 1 V, all power supplies are independent'); VDD, VDDA, VBAT and VDDLDO
    on the rail with VCAP on its capacitor (VCAP is made from VDDLDO, on the rail); an RP2040's IOVDD, ADC_AVDD and USB_VDD on
    the rail with VREG_VIN on +3V3 and DVDD with VREG_VOUT on +1V1 ('RP2040's power supplies may be powered up or down in
    any order', 2.9.6); a Compute Module 5's 5V on the rail with VBAT on a coin cell, GPIO_VREF with pins 84 and 86 on
    +3V3_CM1 and pins 88 and 90 on +1V8_CM1 (2.12.2 Table 3: VBAT keeps the RTC 'even when the board is off'); a CP2102N's
    VREGIN, VDD and VBUS on the rail; its VREGIN and VDD on the rail with VBUS on a net with only a pull-down and a
    capacitor; and its VREGIN on the rail with VDD on its own net with capacitors (its regulator's output, made from
    VREGIN)."""
    G = [("U41", "10", "VSS")]
    V5 = [("U30A", p, "5V") for p in ("77", "79", "81", "83", "85", "87")]
    CELL = ("CR2032 RTC cell", "Battery:BatteryHolder", "Device:Battery_Cell")
    for comps, nets, needle in (
            ({"U41": MCU}, {"+5V_X": [("U41", "21", "VDDA")], "+2V5_REF": [("U41", "20", "VREF+")],
                            "+3V3": [("U41", "11", "VDD"), ("U41", "6", "VBAT")], "GND": G},
             "and it is STM32H7's VDDA, and its VREF+ is on +2V5_REF, off the rail, and the held sheets bound VREF+ by VDDA: "
             "'VREF+ Positive reference voltage', maximum VDDA (DS12110 Rev 10 6.3.20 Table 87"),
            ({"U41": MCU}, {"+5V_X": [("U41", "49", "VDD50USB")], "+3V3": [("U41", "50", "VDD33USB")], "GND": G},
             "and it is STM32H7's VDD50USB, and its VDD33USB (pin 50) on +3V3, off the rail: both are supplies of one part, "
             "and no held page of its maker's lets its VDD50USB fall while it stays up"),
            ({"U41": MCU}, {"+5V_X": [("U41", "75", "VDDLDO")], "+3V3": [("U41", "21", "VDDA")], "GND": G},
             "and it is STM32H7's VDDLDO, and its VDDA (pin 21) on +3V3, off the rail: both are supplies of one part, "
             "and no held page of its maker's lets its VDDLDO fall while it stays up"),
            ({"U16": CP2, "U70": REG25}, {"+5V_X": [("U16", "7", "VREGIN")], "+3V3_EXT": [("U16", "6", "VDD"), ("U70", "5", "VOUT")],
                                          "GND": [("U16", "3", "GND")]},
             "and it is CP2102N's VREGIN, and its VDD is on +3V3_EXT (besides its VDD, U70 pin 5 (AP2112K-2.5 GPIO reference, "
             "'VOUT'), an output is not shown to be unable to feed it), off the rail, and the output of its 5 V regulator "
             "whenever VREGIN is powered (CP2102N Rev 1.5 Table 3.6, page 12"),
            ({"U16": CP2}, {"+5V_X": [("U16", "6", "VDD"), ("U16", "7", "VREGIN")], "+1V8": [("U16", "5", "VIO")],
                            "GND": [("U16", "3", "GND")]},
             "and it is CP2102N's VREGIN, and its VIO is on +1V8, off the rail, and the held sheet bounds VIO by VDD: "
             "'Operating Supply Voltage on VIO', 1.71 V minimum and VDD maximum (CP2102N Rev 1.5 Table 3.1"),
            ({"U16": CP2}, {"+5V_X": [("U16", "6", "VDD"), ("U16", "7", "VREGIN")], "+5V_DEV": [("U16", "8", "VBUS")],
                            "GND": [("U16", "3", "GND")]},
             "and it is CP2102N's VREGIN, and its VBUS sense input pin VBUS (pin 8) is on +5V_DEV, off the rail, where U21 pin 6 "
             "(TPS22810DRV) is not shown to be a load; and CP2102N Rev 1.5 2.3 USB (page 8)"),
            ({"U30A": CM5_RA}, {"+5V_X": [("U30A", "78", "GPIO_VREF")], "+5V_S1": list(V5),
                                "+3V3_CM1": [("U30A", "84", "CM5_3.3V"), ("U30A", "86", "CM5_3.3V")]},
             "'GPIO_VREF') is a pin of a part whose pins firmware sets, and it is Compute Module 5's GPIO_VREF, and its CM5_3.3V "
             "(pins 84, 86) on +3V3_CM1, off the rail, where its CM5_3.3V is on it, which the part makes from its 5V, not on the "
             "rail: both are supplies of one part, and no held page of its maker's lets its GPIO_VREF fall while it "
             "stays up, so what that net does to the part once EMCON has opened the rail's switch, and whether it leaves "
             "through the GPIO_VREF pins onto the rail, is not known; and its 5V (pins 77, 79, 81, 83, 85, 87) on +5V_S1, off "
             "the rail"),
            ({"U30A": CM5_RA}, {"+5V_X": list(V5), "+3V3_AUX": [("U30A", "100", "+3V3_AUX")]},
             "its pin 100, named '+3V3_AUX', a supply word Compute Module 5's table does not place on +3V3_AUX, off the rail"),
            ({"U30A": CM5_RA, "U70": REG25}, {"+5V_X": list(V5), "+3V3_CM1": [("U30A", "84", "CM5_3.3V"), ("U70", "5", "VOUT")]},
             "and its CM5_3.3V (pin 84) on +3V3_CM1, off the rail, where besides its CM5_3.3V, U70 pin 5 (AP2112K-2.5 GPIO "
             "reference, 'VOUT'), an output is not shown to be unable to feed it: both are supplies of one part")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), nets, tx)
    # ACCEPTABLE
    for comps, nets in (
            ({"U41": MCU, "C48": ("2.2u", "C", "Device:C")},
             {"+5V_X": [("U41", "21", "VDDA")], "+3V3": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "75", "VDDLDO")],
              "VCAP": [("U41", "48", "VCAP"), ("C48", "1", "")], "GND": G + [("C48", "2", "")]}),
            ({"U41": MCU, "C48": ("2.2u", "C", "Device:C")},
             {"+5V_X": [("U41", "11", "VDD"), ("U41", "21", "VDDA"), ("U41", "6", "VBAT"), ("U41", "75", "VDDLDO")],
              "VCAP": [("U41", "48", "VCAP"), ("C48", "1", "")], "GND": G + [("C48", "2", "")]}),
            ({"U77": CPU, "C23": ("1u", "C", "Device:C")},
             {"+5V_X": [("U77", "1", "IOVDD"), ("U77", "43", "ADC_AVDD"), ("U77", "48", "USB_VDD")], "+3V3": [("U77", "44", "VREG_VIN")],
              "+1V1": [("U77", "23", "DVDD"), ("U77", "45", "VREG_VOUT"), ("C23", "1", "")], "GND": [("U77", "57", "GND"), ("C23", "2", "")]}),
            ({"U30A": CM5_RA, "BT1": CELL},
             {"+5V_X": list(V5), "+VBAT_CELL": [("U30A", "76", "VBAT"), ("BT1", "1", "+")],
              "+3V3_CM1": [("U30A", "78", "GPIO_VREF"), ("U30A", "84", "CM5_3.3V"), ("U30A", "86", "CM5_3.3V")],
              "+1V8_CM1": [("U30A", "88", "CM5_1.8V"), ("U30A", "90", "CM5_1.8V")], "GND": [("BT1", "2", "-")]}),
            ({"U16": CP2}, {"+5V_X": [("U16", "6", "VDD"), ("U16", "7", "VREGIN"), ("U16", "8", "VBUS")], "GND": [("U16", "3", "GND")]}),
            ({"U16": CP2, "R8": ("100k", "R", "Device:R"), "C8": ("100n", "C", "Device:C")},
             {"+5V_X": [("U16", "6", "VDD"), ("U16", "7", "VREGIN")], "VBUS_SENSE": [("U16", "8", "VBUS"), ("R8", "1", ""), ("C8", "1", "")],
              "GND": [("U16", "3", "GND"), ("R8", "2", ""), ("C8", "2", "")]}),
            ({"U16": CP2, "C10": ("4.7u", "C", "Device:C"), "C11": ("100n", "C", "Device:C")},
             {"+5V_X": [("U16", "7", "VREGIN")], "ZB_3V3": [("U16", "6", "VDD"), ("C10", "1", ""), ("C11", "1", "")],
              "GND": [("U16", "3", "GND"), ("C10", "2", ""), ("C11", "2", "")]})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(comps), nets, tx)


# ROUND 6 ELEVENTH PASS (R4T-D63 to R4T-D68; the review of the tenth pass, its blocking item and the minors it listed as named
# limits that still read PASS in silence, under the stop rule of the review of 26 September 2026 22:35: a case a held maker
# document says can feed the path is decided from the documents or reads UNDECIDED). Each DEFECTIVE case below reads PASS on
# the tenth pass's file (397331f5) unless it says otherwise; each ACCEPTABLE one passes on both.
_V5 = [("U30A", p, "5V") for p in ("77", "79", "81", "83", "85", "87")]
_OWN = [("U30A", "78", "GPIO_VREF"), ("U30A", "84", "CM5_3.3V"), ("U30A", "86", "CM5_3.3V")]
_R10K = ("10k", "R", "Device:R")
_AMP = ("TLV9062 sensor amplifier", "Package_SO:VSSOP-8", "X:Y")
_CELL = ("CR2032 RTC cell", "Battery:BatteryHolder", "Device:Battery_Cell")
_REG = ("AP2112K-3.3", "Package_TO_SOT_SMD:SOT-23-5", "X:Y")
_CAP = ("4.7u", "C", "Device:C")
_EFUSE = ("TPS259631DDAR eFuse", "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm", "X:Y")
_GATED_5V = ("U30A pin 77 (Amphenol 10164227-1004A1RLF re, '5V') is a pin of a part whose pins firmware sets, and it is "
             "Compute Module 5's 5V, and its GPIO_VREF is on +3V3_CM1 (besides its CM5_3.3V, ")


def t_a_firmware_part_on_a_modules_own_output_is_read_as_on_a_rail():
    """DEFECTIVE (the review of the tenth pass, its blocking item; R4T-F37, R4T-D63): _net_sources() took another firmware
    part's supply input on the Compute Module's own CM5_3.3V net as unable to feed it on its table row alone, without the
    backfeed, reverse and class readings fw_pin_role() applies to the same pin on a gated rail. So a module's 5V on a gated
    rail read PASS with an empty detail while GPIO_VREF's net was held up through a join the part's maker documents: a
    PCA9555 whose P-port is pulled up or driven (SCPS131J Figure 8-2), an RP2040 whose ADC input an op-amp drives (2.9.5), an
    STM32H753 whose VBAT is on a cell (DS12110 Figure 15, Table 95), whose VDDA is on another regulator (3.5.1) or whose
    VDDLDO is on +3V3 (Table 24), and a CP2102N whose own VDD net carries such a PCA9555 or a second CP2102N whose VBUS is
    live (2.3). The review's probes A1 to A8 read PASS on the tenth pass's file and read UNDECIDED now, naming the other
    part's join. ACCEPTABLE, PASS on both files: board B's form (GPIO_VREF with pins 84 and 86 alone on +3V3_CM1, the
    review's C3) and a PCA9555 on +3V3_CM1 with its P-ports unconnected (C4). The review's control holds as well: on A1's
    netlist fw_pin_role() reads the PCA9555's VDD on +3V3_CM1 as undecided, and _net_sources() now names it."""
    C4_EXP = {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U66", "24", "VDD")], "GND": [("U66", "12", "VSS")]}
    for comps, nets, needle in (
            ({"U30A": CM5_RA, "U66": EXP, "R5": _R10K},
             dict(C4_EXP, KSZ_RST=[("U66", "4", "IO0_0"), ("R5", "1", "")], **{"+3V3": [("R5", "2", "")]}),
             _GATED_5V + "U66 pin 24 (PCA9555PW 0x20: outputs, 'VDD'), which is PCA9555's VDD, and its P-port pin IO0_0 "
             "(pin 4) is on KSZ_RST, off the rail, where R5 pin 1 (10k) is not shown to be a load; and TI SCPS131J Figure 8-2"),
            ({"U30A": CM5_RA, "U66": EXP, "U55": BUF1},
             dict(C4_EXP, CTRL=[("U66", "20", "IO1_7"), ("U55", "4", "Y")], GND=[("U66", "12", "VSS"), ("U55", "3", "GND")],
                  **{"+3V3": [("U55", "5", "VCC")]}),
             "which is PCA9555's VDD, and its P-port pin IO1_7 (pin 20) is on CTRL, off the rail, where U55 pin 4 (74LVC1G34 "
             "buffer) is not shown to be a load"),
            ({"U30A": CM5_RA, "U77": CPU, "U2": _AMP},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U77", "1", "IOVDD")], "VSENSE": [("U77", "38", "GPIO26_ADC0"), ("U2", "1", "OUT1")],
              "GND": [("U77", "57", "GND")]},
             _GATED_5V + "U77 pin 1 (RP2040 panel controller, 'IOVDD'), which is RP2040's IOVDD, and its ADC input pin "
             "GPIO26_ADC0 (pin 38) is on VSENSE, off the rail, where U2 pin 1 (TLV9062 sensor amplifier) is not shown to be a load"),
            ({"U30A": CM5_RA, "U41": MCU, "BT1": _CELL},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U41", "11", "VDD")], "+VBAT_CELL": [("U41", "6", "VBAT"), ("BT1", "1", "+")],
              "GND": [("U41", "10", "VSS"), ("BT1", "2", "-")]},
             _GATED_5V + "U41 pin 11 (STM32H753VITx I/O supervisor, 'VDD'), which is STM32H7's VDD, and its VBAT is on "
             "+VBAT_CELL, off the rail, and the held sheets draw the battery charger between VDD and VBAT"),
            ({"U30A": CM5_RA, "U41": MCU, "U70": _REG},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U41", "11", "VDD")], "+3V3_A": [("U41", "21", "VDDA"), ("U70", "5", "VOUT")],
              "GND": [("U41", "10", "VSS")]},
             "which is STM32H7's VDD, and its VDDA is on +3V3_A, off the rail, and the maker's power sequence ties VDDA"),
            ({"U30A": CM5_RA, "U41": MCU},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U41", "11", "VDD")], "+3V3": [("U41", "75", "VDDLDO")], "GND": [("U41", "10", "VSS")]},
             "which is STM32H7's VDD, and its VDDLDO is on +3V3, off the rail, and the held sheets bound VDDLDO by VDD"),
            ({"U16": CP2, "U66": EXP, "R5": _R10K, "C10": _CAP},
             {"+5V_X": [("U16", "7", "VREGIN")], "ZB_3V3": [("U16", "6", "VDD"), ("C10", "1", ""), ("U66", "24", "VDD")],
              "KSZ_RST": [("U66", "4", "IO0_0"), ("R5", "1", "")], "+3V3": [("R5", "2", "")],
              "GND": [("U16", "3", "GND"), ("C10", "2", ""), ("U66", "12", "VSS")]},
             "and it is CP2102N's VREGIN, and its VDD is on ZB_3V3 (besides its VDD, U66 pin 24 (PCA9555PW 0x20: outputs, "
             "'VDD'), which is PCA9555's VDD, and its P-port pin IO0_0 (pin 4) is on KSZ_RST"),
            ({"U16": CP2, "U17": CP2, "C10": _CAP},
             {"+5V_X": [("U16", "7", "VREGIN")], "ZB_3V3": [("U16", "6", "VDD"), ("C10", "1", ""), ("U17", "7", "VREGIN")],
              "U17_VDD": [("U17", "6", "VDD")], "+5V_DEV": [("U17", "8", "VBUS")],
              "GND": [("U16", "3", "GND"), ("C10", "2", ""), ("U17", "3", "GND")]},
             "its VDD is on ZB_3V3 (besides its VDD, U17 pin 7 (CP2102N-A02-GQFN28 USB-UART br, 'VREGIN'), which is CP2102N's "
             "VREGIN, and its VBUS sense input pin VBUS (pin 8) is on +5V_DEV")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    # ACCEPTABLE: the review's C3 and C4
    for comps, nets in (({"U30A": CM5_RA}, {"+5V_X": list(_V5), "+3V3_CM1": list(_OWN)}),
                        ({"U30A": CM5_RA, "U66": EXP}, dict(C4_EXP, **{"unconnected-(U66-IO0_0-Pad4)": [("U66", "4", "IO0_0")]}))):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(comps), tx)
    # the review's control, on A1's netlist
    nl = _edit(_power_board({"and", "expander_sw"}), comps={"U30A": CM5_RA, "U66": EXP, "R5": _R10K},
               nets=dict(C4_EXP, KSZ_RST=[("U66", "4", "IO0_0"), ("R5", "1", "")], **{"+3V3": [("R5", "2", "")]}))
    assert T.fw_pin_role(nl, "U66", "24", "VDD", "+3V3_CM1")[0] == "undecided"
    src = T._net_sources(nl, "U30A", "+3V3_CM1")
    assert len(src) == 1 and src[0].startswith("U66 pin 24 (PCA9555PW 0x20: outputs, 'VDD'), which is PCA9555's VDD"), src


def t_a_pull_from_an_own_output_net_is_read_through():
    """DEFECTIVE (the review of the tenth pass, minor B7 to B9; R4T-F38, R4T-D64): the own-output test did not follow a pull
    to a net no supply test knows, although the second-feed check reads through such a resistor (R4T-D49). So a Compute
    Module's GPIO_VREF net with a 1 kOhm to V2V5 or REF_EXT that a regulator's VOUT drives, or to SIG_X that a push-pull
    74LVC1G34 drives, read PASS with an empty detail. Each reads UNDECIDED now, naming the pull and what is behind it.
    ACCEPTABLE, PASS on both files: a pull to a net whose only other part is an LED's anode with its cathode on ground (board
    B's R148 and LED16), a logic gate's input, a 100 kOhm pull-down, or a pin of the module itself."""
    R1K = ("1k", "R", "Device:R")
    for comps, nets, needle in (
            ({"U30A": CM5_RA, "R6": R1K, "U70": _REG},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("R6", "1", "")], "V2V5": [("R6", "2", ""), ("U70", "5", "VOUT")]},
             _GATED_5V + "R6 pin 1 (1k, ''), a pull to V2V5, behind which U70 pin 5 (AP2112K-3.3, 'VOUT'), an output is not "
             "shown to be unable to feed it)"),
            ({"U30A": CM5_RA, "R6": R1K, "U55": BUF1},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("R6", "1", "")], "SIG_X": [("R6", "2", ""), ("U55", "4", "Y")],
              "+3V3": [("U55", "5", "VCC")], "GND": [("U55", "3", "GND")]},
             "R6 pin 1 (1k, ''), a pull to SIG_X, behind which U55 pin 4 (74LVC1G34 buffer, 'Y'), the push-pull output of "
             "74LVC1G34 buffer"),
            ({"U30A": CM5_RA, "R6": R1K, "U70": _REG},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("R6", "1", "")], "REF_EXT": [("R6", "2", ""), ("U70", "5", "VOUT")]},
             "R6 pin 1 (1k, ''), a pull to REF_EXT, behind which U70 pin 5 (AP2112K-3.3, 'VOUT'), an output")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(nets), tx["ok"], tx["detail"][:900])
    # ACCEPTABLE
    for comps, nets in (
            ({"U30A": CM5_RA, "R6": R1K, "LED6": ("green ACT", "LED_SMD:LED_0603", "Device:LED")},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("R6", "1", "")], "LED_A": [("R6", "2", ""), ("LED6", "2", "A")],
              "GND": [("LED6", "1", "K")]}),
            ({"U30A": CM5_RA, "R6": _R10K, "U56": AND1},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("R6", "1", "")], "SIG_IN": [("R6", "2", ""), ("U56", "1", "A")],
              "+3V3": [("U56", "5", "VCC")], "GND": [("U56", "3", "GND")]}),
            ({"U30A": CM5_RA, "R6": _R10K, "R7": PD},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("R6", "1", "")], "DIV": [("R6", "2", ""), ("R7", "1", "")], "GND": [("R7", "2", "")]}),
            ({"U30A": CM5_RA, "R6": _R10K},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("R6", "1", "")], "GPIO6_PU": [("R6", "2", ""), ("U30A", "30", "GPIO6")]})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(nets), tx)


def t_a_logic_part_or_switch_whose_maker_states_a_path_back_is_read():
    """DEFECTIVE (the review of the tenth pass, minor L1: 'consider naming logic parts and load switches on an own-output net
    explicitly'; R4T-F39, R4T-D65): a part that runs from the gated rail, or from the module's own output, and whose maker
    states a path from its outputs back into that supply, or rates an output by that supply, read PASS in silence, on the
    rail as on the own-output net: an SN74LVC08A (SCAS283W 7.3.3: 'The outputs to this device have both positive and negative
    clamping diodes'; 5.1: 'Output voltage' at most VCC + 0.5 V, no Ioff) with VCC on +5V_X, or on +3V3_CM1, and an output
    pulled up to +3V3; an SN74LVC32A in the same drawing (SCAS286U 5.1: at most VCC + 0.5 V, no Ioff, no power-off rating); a
    TPS22810 (SLVSDH0C 10.4: 'current flow through the body diode from VOUT to VIN') with VIN on +5V_X, or on +3V3_CM1, and
    VOUT on a net a diode from another rail feeds; a TPS2596 eFuse in the TPS22810's drawing (SLVSET8A 7.1: VOUT at most min
    (21, VIN + 0.3) V). Each reads UNDECIDED now, naming the output, what holds it up and the maker's words. ACCEPTABLE,
    PASS on both files: a 74LVC1G08 (Ioff 10 uA, SCES217AA 5.5, and outputs rated to 6.5 V in the power-off state); the
    SN74LVC08A with its output on a net that holds only an LED's anode; the TPS22810 with its VOUT on capacitors only."""
    PULLED = {"Y_OUT": [("U58", "3", "1Y"), ("R9", "1", "")], "+3V3": [("R9", "2", "")]}
    FED = {"+5V_Y": [("U25", "1", "VOUT"), ("D9", "1", "K")], "+5V_DEV": [("D9", "2", "A")]}
    for comps, nets, needle in (
            ({"U58": Q08, "R9": _R10K}, dict(PULLED, **{"+5V_X": [("U58", "14", "VCC")], "GND": [("U58", "7", "GND")]}),
             "+5V_X: U58 pin 14 (SN74LVC08APWR quad AND, 'VCC') sits on the rail's conductor, and it is the supply pin of a "
             "74LVC08 quad AND, its output pin 3 is on Y_OUT, where R9 pin 1 (10k, ''), a resistor from +3V3, a supply is not "
             "shown to be unable to hold it up, and SCAS283W 7.3.3 Clamp Diodes (page 11)"),
            ({"U30A": CM5_RA, "U58": Q08, "R9": _R10K},
             dict(PULLED, **{"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U58", "14", "VCC")], "GND": [("U58", "7", "GND")]}),
             _GATED_5V + "U58 pin 14 (SN74LVC08APWR quad AND, 'VCC'): it is the supply pin of a 74LVC08 quad AND, its output "
             "pin 3 is on Y_OUT"),
            ({"U25": LSW, "D9": BAT54}, dict(FED, **{"+5V_X": [("U25", "6", "VIN")], "GND": [("U25", "4", "GND")]}),
             "+5V_X: U25 pin 6 (TPS22810DRV, 'VIN') sits on the rail's conductor, and it is the supply pin of a TPS22810 load "
             "switch (WSON), its output pin 1 is on +5V_Y, where D9 pin 1 (BAT54 wired-OR, 'K'), a diode from +5V_DEV is not "
             "shown to be unable to hold it up, and SLVSDH0C 10.4 Output Capacitor (page 18)"),
            ({"U58": OR4, "R9": _R10K}, dict(PULLED, **{"+5V_X": [("U58", "14", "VCC")], "GND": [("U58", "7", "GND")]}),
             "U58 pin 14 (SN74LVC32APWR quad OR: module , 'VCC') sits on the rail's conductor, and it is the supply pin of a "
             "74LVC32A quad OR, its output pin 3 is on Y_OUT, where R9 pin 1 (10k, ''), a resistor from +3V3, a supply is not "
             "shown to be unable to hold it up, and SCAS286U 5.1 Absolute Maximum Ratings (page 4)"),
            ({"U26": _EFUSE, "D9": BAT54}, {"+5V_X": [("U26", "4", "IN")], "+5V_Y": [("U26", "5", "OUT"), ("D9", "1", "K")],
                                            "+5V_DEV": [("D9", "2", "A")]},
             "U26 pin 4 (TPS259631DDAR eFuse, 'IN') sits on the rail's conductor, and it is the supply pin of a TPS25963x eFuse, "
             "its output pin 5 is on +5V_Y, where D9 pin 1 (BAT54 wired-OR, 'K'), a diode from +5V_DEV is not shown to be unable "
             "to hold it up, and SLVSET8A 7.1 Absolute Maximum Ratings (page 5)"),
            ({"U30A": CM5_RA, "U25": LSW, "D9": BAT54},
             dict(FED, **{"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U25", "6", "VIN")], "GND": [("U25", "4", "GND")]}),
             _GATED_5V + "U25 pin 6 (TPS22810DRV, 'VIN'): it is the supply pin of a TPS22810 load switch (WSON), its output "
             "pin 1 is on +5V_Y")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    # ACCEPTABLE
    led = ("red LED", "LED_SMD:LED_0603", "Device:LED")
    for comps, nets in (
            ({"U58": AND1, "R9": _R10K}, {"+5V_X": [("U58", "5", "VCC")], "Y_OUT": [("U58", "4", "Y"), ("R9", "1", "")],
                                          "+3V3": [("R9", "2", "")], "GND": [("U58", "3", "GND")]}),
            ({"U58": Q08, "LED9": led}, {"+5V_X": [("U58", "14", "VCC")], "Y_OUT": [("U58", "3", "1Y"), ("LED9", "2", "A")],
                                         "GND": [("U58", "7", "GND"), ("LED9", "1", "K")]}),
            ({"U25": LSW, "C9": _CAP}, {"+5V_X": [("U25", "6", "VIN")], "+5V_Y": [("U25", "1", "VOUT"), ("C9", "1", "")],
                                        "GND": [("U25", "4", "GND"), ("C9", "2", "")]})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(comps), tx)


def t_a_supply_word_with_a_separator_and_a_module_named_after_an_underscore_are_read():
    """DEFECTIVE (the review of the tenth pass, minor B5, and the ninth review's minor it found not carried, probes B1-10 and
    B1-11; R4T-F40, R4T-D66): a module pin a symbol calls 'VDD_IO', an STM32H7 VDDA called 'VDD_A' and a VDD33USB called
    'VDD33_USB' were no supply words because of the underscore, so a part on a gated rail with such a pin on a live net read
    PASS in silence; and FW_MENTION's '\\bCM5' found no module named 'RPi_CM5_8GB' or on the library 'meshsat:RPi_CM5', so
    pin 84 CM5_3.3V (a 600 mA regulator output, CM5 datasheet 3.4) on a gated rail read PASS. Each reads UNDECIDED now.
    ACCEPTABLE, PASS on both files: the same module pin named 'VDD_IO' left unconnected (a supply pin of the part on any live
    net off the rail is read by the class, R4T-D62, whatever else is on that net). *Changed in the twelfth pass (R4T-D70): a
    part whose value has a letter before 'CM5' ('XCM5 filter') is still not read as a mention of the module, and it is a
    part in no class, which reads UNDECIDED now where it read PASS, so the case asserts the first and not a PASS.*"""
    G = [("U41", "10", "VSS")]
    mod = lambda v, lib="meshsat:Module": {"U9": (v, "meshsat:CM5", lib)}
    for comps, nets, needle in (
            ({"U30A": CM5_RA}, {"+5V_X": list(_V5), "+3V3_CM1": list(_OWN), "+1V8_X": [("U30A", "100", "VDD_IO")]},
             "its pin 100, named 'VDD_IO', a supply word Compute Module 5's table does not place on +1V8_X, off the rail"),
            ({"U41": MCU}, {"+5V_X": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "75", "VDDLDO")],
                            "+3V3": [("U41", "21", "VDD_A")], "GND": G},
             "its pin 21, named 'VDD_A', a supply word STM32H7's table does not place on +3V3, off the rail"),
            ({"U41": MCU}, {"+5V_X": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "21", "VDDA"), ("U41", "75", "VDDLDO")],
                            "+3V3": [("U41", "50", "VDD33_USB")], "GND": G},
             "its pin 50, named 'VDD33_USB', a supply word STM32H7's table does not place on +3V3, off the rail"),
            (mod("Compute board 8GB", "meshsat:RPi_CM5"), {"+5V_X": [("U9", "84", "CM5_3.3V")]},
             "U9 pin 84 (Compute board 8GB, 'CM5_3.3V') sits on the rail's conductor, and its value or library symbol mentions "
             "CM5, a family whose pins firmware sets, and the part is not read as one"),
            (mod("RPi_CM5_8GB"), {"+5V_X": [("U9", "84", "CM5_3.3V")]},
             "U9 pin 84 (RPi_CM5_8GB, 'CM5_3.3V') sits on the rail's conductor, and its value or library symbol mentions CM5_8GB, "
             "a family whose pins firmware sets")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    assert T.fw_mention(_nl({"U9": ("RPi_CM5_8GB", "meshsat:CM5", "meshsat:Module")}, {"X": [("U9", "1", "")]}), "U9") == "CM5_8GB"
    # ACCEPTABLE
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": list(_V5), "+3V3_CM1": list(_OWN),
                                     "unconnected-(U30A-VDD_IO-Pad100)": [("U30A", "100", "VDD_IO")]})
    assert tx["ok"] is True, tx
    tx = _on_rail(mod("XCM5 filter"), {"+5V_X": [("U9", "84", "FLT_IN")]})
    assert tx["ok"] is None and "U9 pin 84 (XCM5 filter, 'FLT_IN') sits on the rail's conductor, and it is a pin of a part no " \
        "class here reads" in tx["detail"] and "mentions" not in tx["detail"], tx


def t_an_output_held_from_outside_is_not_excused_and_a_makers_sentence_is_named():
    """DEFECTIVE (the review of the tenth pass, minors B1 and B3; R4T-F41, R4T-D67): a sentence that lets a part's supplies
    fall in any order also excused the part's own supply OUTPUT held up by another regulator, a drawing its maker's held
    pages do not describe: an STM32H753's VDDA on the rail with VDD on +3V3 and VCAP on an external 1.2 V regulator (3.5.1
    gives VCAP only as the internal regulator's output), and an RP2040's VREG_VIN on the rail with DVDD and VREG_VOUT on a
    net another regulator feeds (2.9.7.2: 'the output of on-chip voltage regulator (VREG_VOUT) should be left unconnected').
    Each reads UNDECIDED now. And a PASS that rests on such a sentence says so (the review's B4): a Compute Module 5's 5V on
    the rail with VBAT on a live +3V3 supply is a load by 2.12.2 Table 3, and the PASS names it. ACCEPTABLE, PASS on both
    files: the STM32H753's VDDA alone on the rail with VCAP on its capacitor, whose PASS names 3.5.1; the RP2040's VREG_VIN
    on the rail with DVDD and VREG_VOUT on capacitors only, fed by its own regulator (no sentence needed, no note)."""
    G = [("U41", "10", "VSS")]
    for comps, nets, needle in (
            ({"U41": MCU, "U70": _REG},
             {"+5V_X": [("U41", "21", "VDDA")], "+3V3": [("U41", "11", "VDD"), ("U41", "75", "VDDLDO"), ("U41", "6", "VBAT")],
              "+1V2_CORE": [("U41", "48", "VCAP"), ("U70", "5", "VOUT")], "GND": G},
             "and it is STM32H7's VDDA, and its VCAP (pin 48) on +1V2_CORE, off the rail, where besides its VCAP, U70 pin 5 "
             "(AP2112K-3.3, 'VOUT'), an output is not shown to be unable to feed it: its maker lets its VDDA fall while that "
             "supply stays up"),
            ({"U77": CPU, "U70": _REG},
             {"+5V_X": [("U77", "44", "VREG_VIN")], "+3V3": [("U77", "1", "IOVDD")],
              "+1V1": [("U77", "23", "DVDD"), ("U77", "45", "VREG_VOUT"), ("U70", "5", "VOUT")], "GND": [("U77", "57", "GND")]},
             "and it is RP2040's VREG_VIN, and its VREG_VOUT (pin 45) on +1V1, off the rail, where besides its VREG_VOUT, U70 pin "
             "5 (AP2112K-3.3, 'VOUT'), an output is not shown to be unable to feed it")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    assert "2.9.7.2 External Core Supply (page 153)" in tx["detail"], tx["detail"][:1600]
    # the review's B4: PASS, and the PASS names the maker's sentence
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": list(_V5), "+3V3_CM1": list(_OWN), "+3V3": [("U30A", "76", "VBAT")]})
    assert tx["ok"] is True and "taken on its maker's words: U30A pins 77, 79, 81, 83, 85, 87 (" in tx["detail"] \
        and "a load with its VBAT (pin 76) on +3V3 off the rail" in tx["detail"] and "2.12.2 Table 3" in tx["detail"], tx
    # ACCEPTABLE
    tx = _on_rail({"U41": MCU, "C48": ("2.2u", "C", "Device:C")},
                  {"+5V_X": [("U41", "21", "VDDA")], "+3V3": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "75", "VDDLDO")],
                   "VCAP": [("U41", "48", "VCAP"), ("C48", "1", "")], "GND": G + [("C48", "2", "")]})
    assert tx["ok"] is True and "'When VDD is above 1 V, all power supplies are independent'" in tx["detail"], tx
    tx = _on_rail({"U77": CPU, "C23": ("1u", "C", "Device:C")},
                  {"+5V_X": [("U77", "44", "VREG_VIN")], "+1V1": [("U77", "23", "DVDD"), ("U77", "45", "VREG_VOUT"), ("C23", "1", "")],
                   "GND": [("U77", "57", "GND"), ("C23", "2", "")]})
    assert tx["ok"] is True and "taken on its maker's words" not in tx["detail"], tx


def t_every_io_of_a_firmware_parts_supply_domain_is_read():
    """DEFECTIVE (the stop rule of the review of 26 September 2026 22:35, applied to limit (2) of the tenth pass's list for the
    parts with a table; R4T-F42, R4T-D68): an I/O of a firmware part whose supply is on the gated rail, held up by another
    part, read PASS in silence, while the part's maker bounds what such a pin may carry with the supply off: an RP2040's
    QSPI_SS (Table 622: 'Voltage at IO' at most IOVDD + 0.5 V; not one of Table 614's fault-tolerant pins), an STM32H753's
    PA9 (Table 21 note 4 and Table 22 note 3: the internal pull-up and positive injection), a Compute Module 5's GPIO6 (4.2.1:
    'there must be no external voltage applied to any pin'), a CP2102N's TXD (Table 3.10: at most VIO + 2.5 V), a PCA9555's
    SDA (SCPS131J 6.1: an input/output clamp above VCC, IIOK, that the table does not assign pin by pin). Each is pulled up to
    +3V3 here and reads UNDECIDED now. ACCEPTABLE, PASS on both files: the RP2040's GPIO5, a fault-tolerant pin ('very little
    current flows into the pin whilst it is below 3.63V and IOVDD is 0V', Table 614), pulled up the same way; the STM32H753's
    PA9 on a net that holds only an LED's anode; the module's GPIO6 unconnected. *Changed in the twelfth pass (R4T-D73, the
    review of the eleventh pass, its minor on SCL): a PCA9555's SCL pulled up was ACCEPTABLE on SCPS131J 6.1 alone, while
    6.3 gives SCL a VIH maximum of VCC with note (1), 'For voltages applied above VCC, an increase in ICC will result'; it
    reads UNDECIDED now, and the ACCEPTABLE case is its A0 pulled up (6.3: A2-A0 VIH maximum 5.5 V, no note). The GPIO5 and
    A0 PASSes quote the maker's words that clear the pin.*"""
    PU = {"+3V3": [("R9", "2", "")]}
    for comps, nets, needle in (
            ({"U77": CPU, "R9": _R10K}, dict(PU, **{"+5V_X": [("U77", "1", "IOVDD"), ("U77", "44", "VREG_VIN")],
                                                   "QSPI_SS": [("U77", "56", "QSPI_SS"), ("R9", "1", "")], "GND": [("U77", "57", "GND")]}),
             "and it is RP2040's IOVDD, and its I/O pin 56 (QSPI_SS) is on QSPI_SS, off the rail, where R9 pin 1 (10k, ''), a "
             "resistor from +3V3, a supply is not shown to be unable to hold it up; and RP2040 Datasheet 5.5.3.1 Table 622"),
            ({"U41": MCU, "R9": _R10K}, dict(PU, **{"+5V_X": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "21", "VDDA"),
                                                             ("U41", "75", "VDDLDO")],
                                                   "UART_RX": [("U41", "68", "PA9"), ("R9", "1", "")], "GND": [("U41", "10", "VSS")]}),
             "and it is STM32H7's VDD, and its I/O pin 68 (PA9) is on UART_RX, off the rail, where R9 pin 1 (10k, ''), a "
             "resistor from +3V3, a supply is not shown to be unable to hold it up; and DS12110 Rev 10 6.2 Table 21 (page 104)"),
            ({"U30A": CM5_RA, "R9": _R10K}, dict(PU, **{"+5V_X": list(_V5), "+3V3_CM1": list(_OWN),
                                                       "PI_SHDN": [("U30A", "30", "GPIO6"), ("R9", "1", "")]}),
             "and it is Compute Module 5's 5V, and its I/O pin 30 (GPIO6) is on PI_SHDN, off the rail, where R9 pin 1 (10k, ''), "
             "a resistor from +3V3, a supply is not shown to be unable to hold it up; and CM5 datasheet 4.2.1 (page 23)"),
            ({"U16": CP2, "R9": _R10K}, dict(PU, **{"+5V_X": [("U16", "6", "VDD"), ("U16", "7", "VREGIN"), ("U16", "8", "VBUS")],
                                                   "ZB_RX": [("U16", "26", "TXD"), ("R9", "1", "")], "GND": [("U16", "3", "GND")]}),
             "and it is CP2102N's VREGIN, and its I/O pin 26 (TXD) is on ZB_RX, off the rail, where R9 pin 1 (10k, ''), a "
             "resistor from +3V3, a supply is not shown to be unable to hold it up; and CP2102N Rev 1.5 Table 3.10"),
            ({"U66": EXP, "R9": _R10K}, dict(PU, **{"+5V_X": [("U66", "24", "VDD")], "SDA0": [("U66", "23", "SDA"), ("R9", "1", "")],
                                                   "GND": [("U66", "12", "VSS")]}),
             "and it is PCA9555's VDD, and its I/O pin 23 (SDA) is on SDA0, off the rail, where R9 pin 1 (10k, ''), a resistor "
             "from +3V3, a supply is not shown to be unable to hold it up; and TI SCPS131J 6.1 Absolute Maximum Ratings (page 5)"),
            ({"U66": EXP, "R9": _R10K}, dict(PU, **{"+5V_X": [("U66", "24", "VDD")], "SCL0": [("U66", "22", "SCL"), ("R9", "1", "")],
                                                   "GND": [("U66", "12", "VSS")]}),
             "and it is PCA9555's VDD, and its I/O pin 22 (SCL) is on SCL0, off the rail, where R9 pin 1 (10k, ''), a resistor "
             "from +3V3, a supply is not shown to be unable to hold it up; and TI SCPS131J 6.1 Absolute Maximum Ratings (page 5)")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    # ACCEPTABLE
    led = ("red LED", "LED_SMD:LED_0603", "Device:LED")
    for comps, nets in (
            ({"U77": CPU, "R9": _R10K}, dict(PU, **{"+5V_X": [("U77", "1", "IOVDD"), ("U77", "44", "VREG_VIN")],
                                                   "SHDN": [("U77", "7", "GPIO5"), ("R9", "1", "")], "GND": [("U77", "57", "GND")]})),
            ({"U66": EXP, "R9": _R10K}, dict(PU, **{"+5V_X": [("U66", "24", "VDD")], "ADDR0": [("U66", "21", "A0"), ("R9", "1", "")],
                                                   "GND": [("U66", "12", "VSS")]})),
            ({"U41": MCU, "LED9": led}, {"+5V_X": [("U41", "11", "VDD"), ("U41", "6", "VBAT"), ("U41", "21", "VDDA"), ("U41", "75", "VDDLDO")],
                                         "LED_A": [("U41", "68", "PA9"), ("LED9", "2", "A")], "GND": [("U41", "10", "VSS"), ("LED9", "1", "K")]}),
            ({"U30A": CM5_RA}, {"+5V_X": list(_V5), "+3V3_CM1": list(_OWN), "unconnected-(U30A-GPIO6-Pad30)": [("U30A", "30", "GPIO6")]})):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True, (sorted(comps), tx)
        # R4T-D73: a pin its maker decides, held up, is named in the PASS with those words
        if "SHDN" in nets:
            assert "its I/O pin 7 (GPIO5) is held up on SHDN, and its maker states that pin passes nothing into the part's " \
                "supply then: RP2040 Datasheet 5.5.2 Table 614 (page 612)" in tx["detail"], tx
        if "ADDR0" in nets:
            assert "its I/O pin 21 (A0) is held up on ADDR0" in tx["detail"] and "TI SCPS131J Table 5-1 (page 4): INT 'Interrupt " \
                "output." in tx["detail"], tx


# ROUND 6 TWELFTH PASS (R4T-D70 to R4T-D73; the review of the eleventh pass, its three blocking items closed as classes, not
# case by case, under the session's decision of 27 September 2026 taken under the owner's standing rule of 26 Sep 2026 and
# following the second checkpoint review's findings D and G): on a gated conductor a pin is a load ONLY where a row of its
# maker's clears it, and the PASS carries those words; every other pin reads UNDECIDED, named. Each DEFECTIVE case below is
# one of the review's probes (rv15/probe1.py to probe3.py) or of their class, and reads PASS on the eleventh pass's file
# (ca9d7cb5) unless it says otherwise; each ACCEPTABLE one reads PASS on both files, quoting the row that clears it.
ULC = ("USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", "Power_Protection:USBLC6-2SC6")
HUB = ("TI TUSB8041IRGCR four-port USB 3.0 hub", "Package_DFN_QFN:QFN-64", "Interface_USB:TUSB8041")
AP = ("AP64500SP-13 buck", "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm", "X:Y")
LM = ("LM5176PWPR buck-boost", "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm", "X:Y")
_WORDS = "taken on its maker's words: "


def t_a_pin_of_a_part_in_no_class_or_a_protection_part_is_a_load_only_by_its_row():
    """DEFECTIVE (the review of the eleventh pass, blocking 1; R4T-D70, R4T-D71): a pin of a part in no class on a gated rail
    was a load without a word (limit (1), R4T-F23), board B's USBLC6 U33 among them, whose held sheet joins each I/O to VBUS
    by a diode (DS4260 2.1 and Figure 15). The review's U1 (U33's VBUS on the rail, its I/O on the TUSB8041's DN1 D+ and D-,
    board B's J_LIME form) and U2 (the I/O pulled to +3V3 by 1k5) read UNDECIDED now, naming the I/O and what holds it up;
    so do an INA226's VBUS pin on the rail (no row for it is held), an I/O pin of the USBLC6 on the rail (its row clears only
    VBUS), a three-pin resistor designator (a trimmer) on the rail, and a declared accessory header on the rail (the declaration says what its far end is for, not that nothing there
    feeds the rail; board B's J_ZBDBG1 and J_ZBDBG2 on +3V3_ZB are the case). ACCEPTABLE, a cited row, PASS quoting it: the
    USBLC6's VBUS on the rail with its I/O pins on nets that hold only capacitors (DS4260's topology: nothing else reaches
    VBUS), and a 74LVC1G08's input A on the rail with its VCC on +3V3 (SCES217AA 5.5: II only)."""
    for comps, nets, needle in (
            ({"U33": ULC, "U102": HUB},
             {"+5V_X": [("U33", "5", "VBUS")], "GND": [("U33", "2", "GND")],
              "LIME_DP": [("U33", "1", "I/O1"), ("U33", "6", "I/O1"), ("U102", "1", "USB_DP_DN1")],
              "LIME_DM": [("U33", "3", "I/O2"), ("U33", "4", "I/O2"), ("U102", "2", "USB_DM_DN1")]},
             "+5V_X: U33 pin 5 (USBLC6-2SC6, 'VBUS') sits on the rail's conductor and is the VBUS of U33 (USBLC6-2 ESD "
             "protection), and its I/O pin 1 is on LIME_DP, where U102 pin 1 (TI TUSB8041IRGCR four-port USB, 'USB_DP_DN1'), "
             "a pin of a part whose pins firmware sets is not shown to be unable to hold it up"),
            ({"U33": ULC, "R9": ("1k5", "R", "Device:R")},
             {"+5V_X": [("U33", "5", "VBUS")], "GND": [("U33", "2", "GND")], "DP": [("U33", "1", "I/O1"), ("R9", "1", "")],
              "+3V3": [("R9", "2", "")]},
             "its I/O pin 1 is on DP, where R9 pin 1 (1k5, ''), a resistor from +3V3, a supply is not shown to be unable to hold "
             "it up; and ST DS4260 Rev 7 (v2/vendor/st/st-usblc6-2-esd-protection.pdf), page 1 pinout"),
            ({"U14": INA}, {"+5V_X": [("U14", "8", "VBUS")], "+3V3": [("U14", "6", "VS")], "GND": [("U14", "7", "GND")]},
             "+5V_X: U14 pin 8 (INA226 PA rail monitor (0x46), 'VBUS') sits on the rail's conductor, and it is a pin of a part "
             "no class here reads (no pin map, switch entry, protection row or firmware table of its maker's is held here for "
             "it), so whether it can feed the rail is not known"),
            ({"U33": ULC}, {"+5V_X": [("U33", "1", "I/O1")], "+5V_DEV": [("U33", "5", "VBUS")], "GND": [("U33", "2", "GND")]},
             "U33 pin 1 (USBLC6-2SC6, 'I/O1') sits on the rail's conductor and is pin 1 ('I/O1') of U33 (USBLC6-2 ESD "
             "protection), whose row here clears only its VBUS")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    # the second-feed check reads this file's own ACCESSORIES, so the header is board B's J_ZBDBG1 as declared there
    # a resistor designator with three pins (a trimmer between the rail and another supply) is not placed: UNDECIDED
    tx = _on_rail({"R77": ("10k trimmer", "Potentiometer_SMD:Bourns_3314J", "Device:R_Potentiometer")},
                  {"+5V_X": [("R77", "1", "1")], "+3V3": [("R77", "3", "3")], "WIPER": [("R77", "2", "2")]})
    assert tx["ok"] is None and "+5V_X: R77 pin 1 (10k trimmer) is a resistor with 3 pins, which this file does not read" in \
        tx["detail"], tx
    hdr = ("CC2652P cJTAG ZBA (bench)", "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical", "Connector_Generic:Conn_01x05")
    tx = _on_rail({"J_ZBDBG1": hdr}, {"+5V_X": [("J_ZBDBG1", "1", "Pin_1")]})
    assert tx["ok"] is None and "+5V_X: leaves the board through J_ZBDBG1 pin 1, declared an accessory (a cJTAG bench header " \
        "of an E72, on the gated +3V3_ZB): the declaration says what the far end is for, not that nothing plugged there feeds " \
        "the rail" in tx["detail"], tx
    # ACCEPTABLE: a cited row clears the pin, and the PASS quotes it
    tx = _on_rail({"U33": ULC, "C33": _CAP, "C34": _CAP},
                  {"+5V_X": [("U33", "5", "VBUS")], "GND": [("U33", "2", "GND"), ("C33", "2", ""), ("C34", "2", "")],
                   "DP_X": [("U33", "1", "I/O1"), ("U33", "6", "I/O1"), ("C33", "1", "")],
                   "DM_X": [("U33", "3", "I/O2"), ("U33", "4", "I/O2"), ("C34", "1", "")]})
    assert tx["ok"] is True and _WORDS + "U33 pin 5 (USBLC6-2SC6, 'VBUS') is the VBUS of U33 (USBLC6-2 ESD protection), and " \
        "nothing holds its I/O pins up, while ST DS4260 Rev 7" in tx["detail"] and "Figure 15 (page 10)" in tx["detail"], tx
    tx = _on_rail({"U58": AND1}, {"+5V_X": [("U58", "1", "A")], "+3V3": [("U58", "5", "VCC")], "GND": [("U58", "3", "GND")]})
    assert tx["ok"] is True and _WORDS + "U58 pin 1 (74LVC1G08 AND: EMCON gate, 'A') is an input of U58 (74LVC1G08 AND) by its " \
        "maker's pin map (TI SN74LVC1G08, SCES217AA (August 2026), Pin Functions (DBV, DCK)), whose held sheet states only " \
        "its leakage there: SCES217AA 5.5" in tx["detail"], tx


def t_a_switch_or_logic_pin_other_than_its_outputs_is_a_load_only_by_its_row():
    """DEFECTIVE (the review of the eleventh pass, blocking 2; R4T-D71): on a gated rail every pin of a switch other than its
    outputs and input, and every non-output pin of a logic gate, was a load without a word, and _net_sources() skipped a
    switch's enable outright, including enables whose makers state a current sourced OUT of the pin. Each of the review's
    probes reads UNDECIDED or FAIL now: P1 and P1b, the AP64500's EN on the rail with its VIN on +12V or on VBAT (DS41979 3
    Enable: 'An internal 1.5uA pullup current source'); P1c, the same EN behind 100 kOhm; P2, the LM5176's EN/UVLO (SNVSAI1D
    7.3.3: 'A pullup current IEN(STBY) is sourced out of the EN/UVLO pin'); P3, the LM5176's VCC, a pin its entry does not
    place; P6, the AP64500's EN on a module's own CM5_3.3V; P7, a 74LVC1G08's GND there: UNDECIDED. P4 and P5, a 74LVC1G08's
    GND and a TPS22810's GND on the rail with the part's supply up: FAIL, as a firmware part's ground FAILS (the part's
    supply current returns through it). ACCEPTABLE, a cited row, PASS quoting it: the TPS22810's EN/UVLO on the rail (SLVSDH0C
    7.5: 'EN/UVLO pin input leakage' 0.1 uA), the TPS25963's (SLVSET8A 7.5: IENLKG), the AP64500's EN on the rail with its
    VIN on the rail too (its sources run from VIN, Pin Descriptions), a 74LVC1G07's open-drain output on the rail (SCES296AG
    page 1), a 74LVC1G08's VCC on the rail with its output pulled up (its Ioff row), and the TPS22810's EN/UVLO on a module's
    own CM5_3.3V."""
    G12 = {"+12V": [("U80", "2", "VIN")], "GND": [("U80", "7", "GND")]}
    und = (
        ({"U80": AP}, dict(G12, **{"+5V_X": [("U80", "3", "EN")]}),
         "+5V_X: U80 pin 3 (AP64500SP-13 buck, 'EN') sits on the rail's conductor and is the enable of U80 (AP64500 buck), and "
         "its maker states a current sourced out of the pin: DS41979 Rev. 5-2, 3 Enable (page 11): 'An internal 1.5uA pullup "
         "current source"),
        ({"U80": AP}, {"+5V_X": [("U80", "3", "EN")], "VBAT": [("U80", "2", "VIN")], "GND": [("U80", "7", "GND")]},
         "its input is on VBAT, which stays up"),
        ({"U80": AP, "R80": ("100k", "R", "Device:R")},
         dict(G12, **{"+5V_X": [("R80", "1", "")], "BUCK_EN": [("R80", "2", ""), ("U80", "3", "EN")]}),
         "+5V_X through R80 (100k) to BUCK_EN: U80 pin 3 (AP64500SP-13 buck, 'EN') sits behind a resistor from it and is the "
         "enable of U80 (AP64500 buck)"),
        ({"U81": LM}, {"+5V_X": [("U81", "1", "EN/UVLO")], "+12V": [("U81", "2", "VIN")], "GND": [("U81", "13", "AGND")]},
         "U81 pin 1 (LM5176PWPR buck-boost, 'EN/UVLO') sits on the rail's conductor and is the enable of U81 (LM5176 buck-boost "
         "controller), and its maker states a current sourced out of the pin: SNVSAI1D 7.3.3 Enable/UVLO (page 15)"),
        ({"U81": LM}, {"+5V_X": [("U81", "20", "VCC")], "+12V": [("U81", "2", "VIN")], "GND": [("U81", "13", "AGND")]},
         "U81 pin 20 (LM5176PWPR buck-boost, 'VCC') sits on the rail's conductor and is pin 20 ('VCC') of U81 (LM5176 "
         "buck-boost controller), which its entry here does not place"),
        ({"U30A": CM5_RA, "U80": AP}, dict(G12, **{"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U80", "3", "EN")]}),
         _GATED_5V + "U80 pin 3 (AP64500SP-13 buck, 'EN'), which is the enable of U80 (AP64500 buck), and its maker states a "
         "current sourced out of the pin"),
        ({"U30A": CM5_RA, "U58": AND1, "R9": _R10K},
         {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U58", "3", "GND")], "+3V3": [("U58", "5", "VCC"), ("R9", "2", "")],
          "YO": [("U58", "4", "Y"), ("R9", "1", "")]},
         _GATED_5V + "U58 pin 3 (74LVC1G08 AND: EMCON gate, 'GND'), which is the ground of U58 (74LVC1G08 AND) by its pin's "
         "name, with its supply on +3V3"))
    for comps, nets, needle in und:
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    for comps, nets, needle in (
            ({"U58": AND1, "R9": _R10K}, {"+5V_X": [("U58", "3", "GND")], "+3V3": [("U58", "5", "VCC"), ("R9", "2", "")],
                                          "YO": [("U58", "4", "Y"), ("R9", "1", "")]},
             "+5V_X: U58 pin 3 (74LVC1G08 AND: EMCON gate, 'GND') is the ground of U58 (74LVC1G08 AND) by its pin's name, with "
             "its supply on +3V3: the part's supply current returns through it onto the net whatever the rail's switch does"),
            ({"U25": LSW}, {"+5V_X": [("U25", "4", "GND")], "+5V_DEV": [("U25", "6", "VIN")]},
             "+5V_X: U25 pin 4 (TPS22810DRV, 'GND') is the ground of U25 (TPS22810 load switch (WSON)) by its pin's name, with "
             "its supply on +5V_DEV")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is False and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    # ACCEPTABLE: a cited row clears the pin, and the PASS quotes it
    for comps, nets, needle in (
            ({"U25": LSW}, {"+5V_X": [("U25", "5", "EN/UVLO")], "+5V_DEV": [("U25", "6", "VIN")], "GND": [("U25", "4", "GND")]},
             _WORDS + "U25 pin 5 (TPS22810DRV, 'EN/UVLO') is the enable input of U25 (TPS22810 load switch (WSON)), which its "
             "maker states only leaks: SLVSDH0C 7.5 Electrical Characteristics (page 5): IEN/UVLO 'EN/UVLO pin input leakage'"),
            ({"U26": _EFUSE}, {"+5V_X": [("U26", "3", "EN/UVLO")], "+5V_DEV": [("U26", "4", "IN")]},
             "U26 pin 3 (TPS259631DDAR eFuse, 'EN/UVLO') is the enable input of U26 (TPS25963x eFuse), which its maker states "
             "only leaks: SLVSET8A 7.5 Electrical Characteristics (page 7): IENLKG 'EN leakage current'"),
            ({"U80": AP}, {"+5V_X": [("U80", "3", "EN"), ("U80", "2", "VIN")], "GND": [("U80", "7", "GND")],
                           "unconnected-(U80-SW-Pad8)": [("U80", "8", "SW")]},
             "U80 pin 3 (AP64500SP-13 buck, 'EN') is the enable of U80 (AP64500 buck), whose maker states a current source out "
             "of the pin (DS41979 Rev. 5-2, 3 Enable (page 11)"),
            ({"U57": OD1}, {"+5V_X": [("U57", "4", "Y")], "+3V3": [("U57", "5", "VCC")], "GND": [("U57", "3", "GND")]},
             "U57 pin 4 (74LVC1G07 open-drain buffer, 'Y') is the open-drain output of U57 (74LVC1G07 open-drain buffer), which "
             "only pulls low: SCES296AG, page 1: 'SN74LVC1G07 Single Buffer/Driver With Open-Drain Output'"),
            ({"U58": AND1, "R9": _R10K}, {"+5V_X": [("U58", "5", "VCC")], "Y_OUT": [("U58", "4", "Y"), ("R9", "1", "")],
                                          "+3V3": [("R9", "2", "")], "GND": [("U58", "3", "GND")]},
             "U58 pin 5 (74LVC1G08 AND: EMCON gate, 'VCC') is the supply pin of U58 (74LVC1G08 AND) by its maker's pin table (TI "
             "SN74LVC1G08, SCES217AA (August 2026), Pin Functions (DBV, DCK)), and its maker states Ioff for the "
             "partial-power-down state"),
            ({"U30A": CM5_RA, "U25": LSW},
             {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U25", "5", "EN/UVLO")], "+5V_DEV": [("U25", "6", "VIN")],
              "GND": [("U25", "4", "GND")]},
             "and the readings of the nets it joins rest on: U25 pin 5 (TPS22810DRV, 'EN/UVLO') on +3V3_CM1 is the enable input "
             "of U25 (TPS22810 load switch (WSON)), which its maker states only leaks: SLVSDH0C 7.5")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])


CM5_RB2 = ("Amphenol 10164227-1004A1RLF receptacle B, slot S2 (CM5 pins 101-200, high-speed side)", "meshsat:CM5",
           "Connector_Generic:CM5B")


def t_every_pin_of_a_split_module_is_read_as_the_modules_own():
    """DEFECTIVE (the review of the eleventh pass, blocking 3; R4T-D72): board B draws each Compute Module 5 as two parts, U30A
    for pins 1 to 100 and U30B for pins 101 to 200, and R4T-D68 read the I/O of the part that carries the 5V only, so a pin
    of U30B held up while a gated slot 5V falls read PASS in silence, although the module's maker says of every pin that 'when
    CM5 is powered-down or off, there must be no external voltage applied to any pin' (4.2.1). The review's M1 (U30B pin 109
    pulled to +3V3) and M2 (U30B pin 143 driven by a push-pull 74LVC1G34) read UNDECIDED now, quoting 4.2.1, and so does a
    U30B pin named as a supply ('VDD_IO') on a live net, by the class reading of R4T-D62. ACCEPTABLE, PASS: U30B's pins on
    nothing live; U30B pin 143 on a net that holds only a 74LVC1G08's input, which a cited row clears (the PASS quotes
    SCES217AA 5.5); and a pin of ANOTHER slot's receptacle (U31B) held up, which is no pin of this module. The control M1c
    (U30A pin 30 pulled up) reads UNDECIDED on both files."""
    base = {"+5V_X": list(_V5), "+3V3_CM1": list(_OWN)}
    for comps, nets, needle in (
            ({"U30A": CM5_RA, "U30B": CM5_RB, "R9": _R10K},
             dict(base, PCIE_RST=[("U30B", "109", "PCIE_nRST"), ("R9", "1", "")], **{"+3V3": [("R9", "2", "")]}),
             "and it is Compute Module 5's 5V, and its I/O pin 109 of U30B (PCIE_nRST) is on PCIE_RST, off the rail, where R9 "
             "pin 1 (10k, ''), a resistor from +3V3, a supply is not shown to be unable to hold it up; and CM5 datasheet 4.2.1 "
             "(page 23)"),
            ({"U30A": CM5_RA, "U30B": CM5_RB, "U55": BUF1},
             dict(base, HPD=[("U30B", "143", "HDMI0_HOTPLUG"), ("U55", "4", "Y")], GND=[("U55", "3", "GND")],
                  **{"+3V3": [("U55", "5", "VCC")]}),
             "its I/O pin 143 of U30B (HDMI0_HOTPLUG) is on HPD, off the rail, where U55 pin 4 (74LVC1G34 buffer, 'Y'), the "
             "push-pull output of 74LVC1G34 buffer is not shown to be unable to hold it up; and CM5 datasheet 4.2.1"),
            ({"U30A": CM5_RA, "U30B": CM5_RB},
             dict(base, **{"+1V8_X": [("U30B", "150", "VDD_IO")]}),
             "its pin 150 of U30B, named 'VDD_IO', a supply word Compute Module 5's table does not place on +1V8_X, off the "
             "rail"),
            ({"U30A": CM5_RA, "R9": _R10K},
             dict(base, PI_SHDN=[("U30A", "30", "GPIO6"), ("R9", "1", "")], **{"+3V3": [("R9", "2", "")]}),
             "its I/O pin 30 (GPIO6) is on PI_SHDN, off the rail")):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is None and needle in tx["detail"], (sorted(comps), tx["ok"], tx["detail"][:900])
    assert T._module_refs(_nl({"U30A": CM5_RA, "U30B": CM5_RB, "U31B": CM5_RB2}, {"X": [("U30A", "1", ""), ("U30B", "101", ""),
                                                                                       ("U31B", "101", "")]}),
                          "U30A", T.fw_family(_nl({"U30A": CM5_RA}, {"X": [("U30A", "1", "")]}), "U30A")) == ["U30A", "U30B"]
    # ACCEPTABLE
    for comps, nets, needle in (
            ({"U30A": CM5_RA, "U30B": CM5_RB}, dict(base, **{"unconnected-(U30B-PCIE_nRST-Pad109)": [("U30B", "109", "PCIE_nRST")]}),
             None),
            ({"U30A": CM5_RA, "U30B": CM5_RB, "U56": AND1},
             dict(base, HPD=[("U30B", "143", "HDMI0_HOTPLUG"), ("U56", "1", "A")], GND=[("U56", "3", "GND")],
                  **{"+3V3": [("U56", "5", "VCC")]}),
             "and the readings of the nets it joins rest on: U56 pin 1 (74LVC1G08 AND: EMCON gate, 'A') on HPD is an input of "
             "U56 (74LVC1G08 AND) by its maker's pin map"),
            ({"U30A": CM5_RA, "U30B": CM5_RB, "U31B": CM5_RB2, "R9": _R10K},
             dict(base, PCIE2_RST=[("U31B", "109", "PCIE_nRST"), ("R9", "1", "")], **{"+3V3": [("R9", "2", "")]}), None)):
        tx = _on_rail(comps, nets)
        assert tx["ok"] is True and (needle is None or needle in tx["detail"]), (sorted(comps), tx["ok"], tx["detail"][:900])


def t_a_makers_sentence_on_a_modules_own_output_is_named_in_the_pass():
    """DEFECTIVE (the review of the eleventh pass, its minor on R4T-D67; R4T-D73): _net_sources() dropped the note fw_pin_role()
    returns with a load, so a Compute Module 5's 5V on the rail with an RP2040 on the module's own CM5_3.3V by IOVDD and its
    VREG_VIN on a live +3V3 read PASS without quoting RP2040 2.9.6, the any-order sentence the PASS rests on (the review's N1),
    while the same RP2040 directly on the rail quoted it (N2). Both PASSes quote it now. ACCEPTABLE, both files: the module
    alone on its own outputs PASSes with no maker's sentence to quote."""
    nets = {"+5V_X": list(_V5), "+3V3_CM1": _OWN + [("U77", "1", "IOVDD")], "+3V3": [("U77", "44", "VREG_VIN")],
            "+1V1": [("U77", "23", "DVDD"), ("U77", "45", "VREG_VOUT"), ("C23", "1", "")], "GND": [("U77", "57", "GND"), ("C23", "2", "")]}
    tx = _on_rail({"U30A": CM5_RA, "U77": CPU, "C23": _CAP}, nets)
    assert tx["ok"] is True and _WORDS + "U30A pins 77, 79, 81, 83, 85, 87 (" in tx["detail"] and "U77 pin 1 (RP2040 panel " \
        "controller, 'IOVDD') on +3V3_CM1 is RP2040's IOVDD, a load with" in tx["detail"] and "RP2040 Datasheet 2.9.6 Power " \
        "Supply Sequencing (page 152)" in tx["detail"], tx
    tx = _on_rail({"U30A": CM5_RA}, {"+5V_X": list(_V5), "+3V3_CM1": list(_OWN)})
    assert tx["ok"] is True and "taken on its maker's words" not in tx["detail"], tx


# INTEGRATION OF 27 SEPTEMBER 2026 (MESHSAT-1357 round 8, set 2): board A's round 8 draft for this tool (the SN74AUP1G08
# row and the walk from each asserted line alone), applied by hand onto the twelfth pass's file, and the enable-row fallback
# of the final check's minor. The fixtures the board A author left owed: a line through an AUP input, and a gate both lines
# force whose answer came from the line the queue took first.
AUP1 = ("SN74AUP1G08DBVR AND: EMCON gate", "Package_TO_SOT_SMD:SOT-23-5", "meshsat_ic:U")


def t_a_line_through_an_aup_gate_is_walked_by_its_makers_pin_map():
    """ACCEPTABLE (board A's U35 to U38 since its round 8): EMCON_HW into an SN74AUP1G08 whose output is the load switch's
    enable; SCES502Q Table 4-1 maps it as the 74LVC1G08 (A 1, B 2, Y 4), its II and Ioff are 0.5 and 0.6 uA and its VIL
    0.9 V. The walk crosses it and the transmitter PASSes. DEFECTIVE: without the row (the twelfth pass's file) the walk
    stopped at U5 and the transmitter was not reached; an AUP family whose sheet is not held (74AUP1G32) is still not walked."""
    nl = _power_board({"and", "expander_sw"})
    nl["comps"]["U5"]["value"] = AUP1[0]
    got, _stopped = T.reach(nl)
    assert "LORA_EN" in got, (sorted(got), _stopped)
    r = T.judge({"B": nl}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    tx = _tx(r, "test LoRa")
    assert tx["ok"] is True and "U5 AND 1->4" in tx["detail"], tx
    row = [f for f in T.LOGIC if f["name"] == "74AUP1G08 AND"][0]
    assert row["ii"] == 0.5e-6 and row["ioff"] == 0.6e-6 and row["vil_ceiling"] == 0.9 and "SCES502Q" in row["cite"], row
    nl2 = _power_board({"and", "expander_sw"})
    nl2["comps"]["U5"]["value"] = "SN74AUP1G32DBVR OR"
    got2, _stopped2 = T.reach(nl2)
    assert "LORA_EN" not in got2, got2


def _two_line_gate(emcon_gpio=True, inhibit_gpio=False):
    """Board A's round 8 shape: the load switch's enable is U5 = TX_INHIBIT_n AND EMCON_HW; each line is made by its own
    toggle to ground (SW1, SW2). A firmware pin on a line (U41) fails that line."""
    comps = {"U12": LORA, "U21": LSW, "C1": ("10u", "C", "Device:C"), "SW1": TOGGLE, "SW2": TOGGLE, "U5": AUP1,
             "R70": ("10k", "R", "Device:R")}
    nets = {"+5V_X": [("U12", "9", "VCC"), ("U21", "1", "VOUT"), ("C1", "1", "")], "+5V_DEV": [("U21", "6", "VIN")],
            "GND": [("U12", "1", "GND"), ("U21", "4", "GND"), ("C1", "2", ""), ("SW1", "2", ""), ("SW2", "2", ""),
                    ("U5", "3", ""), ("R70", "2", "")],
            "LORA_EN": [("U21", "5", "EN/UVLO"), ("U5", "4", ""), ("R70", "1", "")], "+3V3": [("U5", "5", "")],
            "TX_INHIBIT_n": [("SW2", "1", ""), ("U5", "1", "")], "EMCON_HW": [("SW1", "1", ""), ("U5", "2", "")]}
    if emcon_gpio or inhibit_gpio:
        comps["U41"] = MCU
    if emcon_gpio: nets["EMCON_HW"].append(("U41", "33", "PC5"))
    if inhibit_gpio: nets["TX_INHIBIT_n"].append(("U41", "34", "PC4"))
    return _nl(comps, nets)


def t_a_gate_both_lines_force_passes_on_the_line_that_holds():
    """DEFECTIVE before the integration (board A's round 8 finding): the walk keeps one path per net, the first it reaches,
    so U5's output inherited EMCON_HW's path (the first of SOURCES) and the transmitter read FAIL on that line's firmware pin
    while TX_INHIBIT_n, which also forces U5 LOW and holds, was never asked. ACCEPTABLE now: the option passes on the line
    that holds, and the result says it was walked from that line alone. With both lines failing, the transmitter FAILS; with
    neither failing, it PASSes on the combined walk, which names no single line."""
    r = T.judge({"B": _two_line_gate()}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    assert _line(r, "EMCON_HW")["ok"] is False, _line(r, "EMCON_HW")
    assert _line(r, "TX_INHIBIT_n")["ok"] is True, _line(r, "TX_INHIBIT_n")
    tx = _tx(r, "test LoRa")
    assert tx["ok"] is True and "(walked from TX_INHIBIT_n alone)" in tx["detail"], tx
    r2 = T.judge({"B": _two_line_gate(inhibit_gpio=True)}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    assert _tx(r2, "test LoRa")["ok"] is False, _tx(r2, "test LoRa")
    r3 = T.judge({"B": _two_line_gate(emcon_gpio=False)}, table=TX_POWER, accessories=[], receivers=[], owed=[])
    tx3 = _tx(r3, "test LoRa")
    assert tx3["ok"] is True and "alone)" not in tx3["detail"], tx3


def t_a_switch_with_no_enable_row_reads_its_enable_undecided_and_does_not_crash():
    """The final check's minor (probe: the TPS22810 row's en_clear removed, its VIN on the rail and its EN pulled to +12V):
    the second-feed read indexed sw['en_clear'] and raised KeyError, where _class_pin reads the same missing row as UNDECIDED.
    DEFECTIVE: with no enable row the input on the rail is UNDECIDED, naming the enable. ACCEPTABLE: with the row, the
    enable clears on its maker's words and the input is a load."""
    comps = {"U25": LSW, "R9": _R10K}
    nets = {"+5V_X": [("U25", "6", "VIN")], "EN_X": [("U25", "5", "EN/UVLO"), ("R9", "1", "")], "+12V": [("R9", "2", "")],
            "GND": [("U25", "4", "GND")]}
    tx = _on_rail(comps, nets)
    assert tx["ok"] is True and "only leaks" in tx["detail"], (tx["ok"], tx["detail"][:600])
    row = [s for s in T.SWITCHES if s is not None and s.get("en_clear") and "TPS22810" in s["name"]]
    assert row, [s["name"] for s in T.SWITCHES]
    saved = [(s, s.pop("en_clear")) for s in row]
    try:
        tx2 = _on_rail(comps, nets)
    finally:
        for s, v in saved: s["en_clear"] = v
    assert tx2["ok"] is None and "no held page of its maker's says what current that enable pin passes" in tx2["detail"], \
        (tx2["ok"], tx2["detail"][:600])
