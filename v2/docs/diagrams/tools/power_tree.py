#!/usr/bin/env python3
"""The power tree of the V2 set, from board P's cells to every rail, drawn from the committed netlists and the declared
energy chain (MESHSAT-1357, handover layer 4).

Writes:
  v2/docs/diagrams/src/power-tree.mmd   the Mermaid source (rendered by tools/render.sh)
  v2/docs/diagrams/power-tree.md        every edge with the parts it runs through and its netlist proof, every stage of
                                        v2/ecad/tools/pcb_energy_chain.yaml with its protective element read in the
                                        board's netlist, and the disagreements found between the two

How an edge is established. TREE below names each stage: the board, the net it starts on, the net it ends on, and the
parts it runs through (the controller or converter, the fuse, the series shunt). Which parts make a stage is typed in
TREE; the tool checks that typing against the netlist and refuses the build (exit status 1, nothing written) unless:
  1. a walk from the first net reaches the second through the stage's parts only, never through another rail of TREE
     or a ground: a named FET source to drain; a named controller (an IC, a U reference, driving the gate of a power FET,
     directly or through one series resistor on a private net; a resistor on a gate is never a controller) is not
     crossed itself, only the FETs whose gates it drives are; any other named part between any of its pins; an unnamed
     inductor (a two-pin L reference, LEDs excluded) only on a switching node of those parts;
  2. every named part is required: with it left out (a controller together with the FETs it drives) the walk no longer
     arrives, so a controller is attributed by the gates it drives on the path, not by touching the stage's nets;
  3. a named part whose value text names rails of TREE names the stage's end net among them;
  4. a stage whose description names an enable net in parentheses, "(SLOT_EN1)", has a named IC with a pin on that net
     or on a net joined to it by one series resistor (an enable divider's top leg); the page says which pin;
  5. every negative control is refused: the five wrong entries of the review of 27 September 2026; for every two stages
     of a board, each with its ICs swapped for the other's, its shunts and fuses swapped, and the other's shunts and fuses
     or ICs added; and every stage built on a controller with the controller replaced by each other stage's IC while the
     FETs it drove are named outright (the path still exists, only the attribution is wrong); and every stage with an
     enable label with that label replaced by each other stage's enable net on the board. The count is on the page.
Measured, not refused: every single-part substitution and cut-down of each stage (the method of the second review of 27
September 2026): the ones the check accepts are listed on the page, split into those that still name parts of the
typed stage's own path (a FET or an inductor in place of its controller: fewer parts named, not a different path) and
those that name a part off it (a wrong attribution the check cannot see: a monitor, a feedback resistor or a load
bridging the stage's two nets). The typed attributions are therefore also read by hand at each rebuild.
What stays typed: the stage's name and description (only its enable net is checked), and which parts make it (checked,
never found by the tool); a named
IC is crossed between any of its pins (the walk does not know which pins of an integrated converter, eFuse or LDO carry
the current); a stage may name fewer parts than it crosses (a controller's FETs need not be named: the page lists every
part the walk used). Between boards, each lead is checked by the connector pin on each end.

What it does not show: currents, efficiencies, losses and thermal limits (v2/docs/feasibility/POWER-THERMAL.md), which
converter is enabled in which power state (ARCHITECTURE.md 4.3), the grounds and returns, the CM5 modules' own internal
rails, and anything measured: nothing in this kit has been built or powered.

Stdlib and PyYAML; runner-safe. Usage: python3 v2/docs/diagrams/tools/power_tree.py"""
import os, re, sys
sys.dont_write_bytecode = True   # nothing written into the tree beside the sources read
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist as N

OUT_MMD = os.path.join(N.REPO, "v2/docs/diagrams/src/power-tree.mmd")
OUT_MD = os.path.join(N.REPO, "v2/docs/diagrams/power-tree.md")
CHAIN = "v2/ecad/tools/pcb_energy_chain.yaml"

# (board, from net, to net, parts the stage runs through, what the stage is)
TREE = [
    ("P", "CELL4", "FUSED", ("F1",), "pack blade fuse"),
    ("P", "FUSED", "SCP_OUT", ("F2",), "chemical fuse"),
    ("P", "SCP_OUT", "PACK_P", ("U1", "Q1", "Q2"), "charge and discharge FETs, the BQ4050 drives their gates"),
    ("E", "CELL+", "CELL_F", ("F3",), "dock strip pack fuse"),
    ("E", "CELL_F", "+5V_E6", ("U12",), "always-on 5 V"),
    ("E", "+5V_E6", "+3V3_E6", ("U13",), "sensor 3.3 V"),
    ("E", "+5V_E6", "+5V_GEIGER", ("U16",), "Geiger load switch"),
    ("E", "DC_IN", "DC_F", ("F1",), "vehicle and shore fuse"),
    ("E", "DC_F", "DC_P", ("Q1", "U3"), "ideal diode"),
    ("E", "DC_P", "DC_HS", ("U6", "R19"), "hot swap, 9 V on, 40 V off"),
    ("E", "DC_HS", "VIN_RAW", ("L2",), "common-mode choke"),
    ("E", "PV_IN", "PV_P", ("F2",), "solar fuse"),
    # set 5 (S-47, stream w3de): R5 senses in the bottom switches' leg (TRK_CS to GND), off the PV_P to TRK_OUT path
    ("E", "PV_P", "TRK_OUT", ("Q3", "U5", "Q6"), "solar tracker (bench-fitted)"),
    ("E", "TRK_OUT", "VIN_RAW", ("Q2", "U4"), "ideal diode OR"),
    ("A", "CELL+", "CELL_FUSED", ("F1",), "power board pack fuse"),
    ("A", "CELL_FUSED", "VBAT", ("R17",), "charge current shunt (loads on the VSYS side)"),
    ("A", "VIN_RAW", "VBUS20", ("Q2", "U2", "R11"), "front end, 20 V bus"),
    ("A", "VBUS20", "VBAT", ("U3", "R16"), "4S charger, no battery FET"),
    ("A", "VBAT", "+5V_S1", ("U4", "R31"), "slot 1 rail (SLOT_EN1)"),
    ("A", "VBAT", "+5V_S2", ("U5", "R35"), "slot 2 rail (SLOT_EN2)"),
    ("A", "VBAT", "+5V_S3", ("U6", "R39"), "slot 3 rail (SLOT_EN3)"),
    ("A", "VBAT", "+5V_DEV", ("U7", "R43"), "device rail (DEV_EN)"),
    ("A", "VBAT", "+3V3", ("U12",), "logic 3.3 V (RAIL_EN)"),
    ("A", "VBAT", "+13V8_PA", ("U13", "R55"), "PA drain rail (PA_EN)"),
    ("A", "VBAT", "+12V_HF", ("U15", "R65"), "HF rail (HF_EN)"),
    ("A", "VBAT", "+54V_POE", ("U16", "R71"), "PoE feed (POE_EN)"),
    ("A", "VBAT", "PD_VPWR", ("U19", "R81"), "USB-C PD supply (PD_EN)"),
    ("A", "PD_VPWR", "PD_VBUS", ("U18", "R138"), "USB-C PD source, power only"),
    ("A", "VBAT", "VMON", ("U21",), "monitor eFuse (MON_EN)"),
    ("A", "VBAT", "VHEAT_IN", ("U22",), "heater eFuse (HEAT_EN)"),
    ("A", "VHEAT_IN", "VHEAT", ("U33",), "heater 12.0 V"),
    # S-99 (decision 55, integration set 9, 29 September 2026): board D's feed has its own buck U41 from VBAT,
    # enabled by RAIL_EN (TPS62933 pin 2, SLUSEA4D Table 7-1), and the eFuse U23 now sits on its output +5V_D8IN.
    ("A", "VBAT", "+5V_D8IN", ("U41",), "board D feed buck 5.0 V (RAIL_EN)"),
    ("A", "+5V_D8IN", "+5V_D8", ("U23",), "board D feed eFuse (D8_EN)"),
    ("A", "+5V_DEV", "VBUS_WALL", ("U32",), "Glenair port VBUS eFuse"),
    ("B", "+5V_S1", "+3V3_S1A", ("U103",), "slot 1 card 3.3 V, WiFi card 1 (S1A_EN, which EMCON_ON1 pulls low)"),
    ("B", "+5V_S1", "+3V3_S1B", ("U104",), "slot 1 NVMe 3.3 V"),
    ("B", "+5V_S1", "+1V0_S1", ("U105",), "slot 1 PCIe switch core"),
    ("B", "+3V3_S1A", "+3V3_M2C1", ("R165",), "card socket shunt"),
    ("B", "+5V_S2", "+3V3_S2A", ("U203",), "slot 2 card 3.3 V, the 5G module (S2A_EN, which EMCON_ON2 pulls low)"),
    ("B", "+5V_S2", "+3V3_S2B", ("U204",), "slot 2 NVMe 3.3 V"),
    ("B", "+5V_S2", "+1V0_S2", ("U205",), "slot 2 PCIe switch core"),
    ("B", "+3V3_S2A", "+3V3_M2C2", ("R265",), "card socket shunt"),
    ("B", "+5V_S3", "+3V3_S3A", ("U303",), "slot 3 card 3.3 V, WiFi card 2 (S3A_EN, which EMCON_ON3 pulls low)"),
    ("B", "+5V_S3", "+3V3_S3B", ("U304",), "slot 3 NVMe 3.3 V"),
    ("B", "+5V_S3", "+1V0_S3", ("U305",), "slot 3 PCIe switch core"),
    ("B", "+3V3_S3A", "+3V3_M2C3", ("R365",), "card socket shunt"),
    ("B", "+5V_DEV", "+1V1_S1", ("U106",), "bank 1 hub core"),
    ("B", "+5V_DEV", "+1V1_S2", ("U206",), "bank 2 hub core"),
    ("B", "+5V_DEV", "+1V1_S3", ("U306",), "bank 3 hub core"),
    ("B", "+5V_DEV", "+3V3_DEV", ("U25",), "shared logic 3.3 V"),
    ("B", "+5V_DEV", "+1V2_KSZ", ("U26",), "Ethernet switch core"),
    ("B", "+3V3_DEV", "+2V5_KSZ", ("U27",), "Ethernet switch analog"),
    ("B", "+5V_DEV", "+3V3_IOCA", ("U40",), "supervisor A"),
    ("B", "+5V_DEV", "+3V3_IOCB", ("U50",), "supervisor B"),
    ("B", "+5V_DEV", "+3V3_IOCC", ("U60",), "supervisor C"),
    ("B", "+5V_DEV", "+5V_LIME", ("U23",), "LimeSDR eFuse"),
    ("B", "+5V_DEV", "+5V_RB", ("U24",), "RockBLOCK eFuse"),
    ("B", "+5V_DEV", "+5V_LORA", ("U21",), "LoRa load switch"),
    ("B", "+3V3_DEV", "+3V3_ZB", ("U22",), "E72 load switch"),
    ("B", "+5V_DEV", "+5V_CAM", ("U28",), "camera switch"),
    ("B", "+5V_DEV", "PANEL_5V", ("F1",), "panel feed polyfuse"),
    ("B", "+5V_DEV", "+5V_HDMI", ("F2",), "HDMI 5 V polyfuse"),
    ("B", "+5V_DEV", "VBUS_QMX", ("F3",), "QMX USB polyfuse"),
    ("C", "+5V", "+3V3", ("U5",), "panel 3.3 V"),
    ("D", "+5V_D8", "+3V3_D8", ("U1",), "board D 3.3 V"),
    ("D", "+5V_D8", "+3V4_HUB", ("U17",), "hub 3.44 V"),
    # round 8 (EMCON L4 on board D, 26 September 2026): the transmit chain draws through U21, on only while +3V3_D8, the
    # supply of the KEY and PA_KEY gates, is above U21's UVLO (R90 and R91 set TXSUP_EN); FB1 and U15 moved onto +5V_TX
    ("D", "+5V_D8", "+5V_TX", ("U21",), "transmit chain 5 V (TXSUP_EN: on while the EMCON gates' +3V3_D8 is in range)"),
    ("D", "+5V_TX", "+5V_SA", ("FB1",), "exciter supply ferrite"),
    ("D", "+5V_TX", "VGG_SW", ("U15",), "PA gate bias (PA_KEY)"),
]
# leads between boards: (board, net, connector ref, board, net, connector ref, what)
LEADS = [
    ("P", "PACK_P", "W_P", "E", "CELL+", "J_BATT", "pack lead, 12 AWG, XT60"),
    ("E", "CELL_F", "P_CP", "A", "CELL+", "J_CP1", "12 AWG to E5, four 9 A spring pins J_CP1..4"),
    # set 5 (EQ-16, stream w3de): VIN_RAW crosses on board E's 12 AWG pad P_VR to E5 and board A's four 9 A pins
    ("E", "VIN_RAW", "P_VR", "A", "VIN_RAW", "J_VR1", "12 AWG to E5, four 9 A spring pins J_VR1..4 (EQ-16)"),
    ("A", "+5V_S1", "J_5V_S1", "B", "+5V_S1", "J_5V_S1", "JST-VH lead, 16 AWG"),
    ("A", "+5V_S2", "J_5V_S2", "B", "+5V_S2", "J_5V_S2", "JST-VH lead, 16 AWG"),
    ("A", "+5V_S3", "J_5V_S3", "B", "+5V_S3", "J_5V_S3", "JST-VH lead, 16 AWG"),
    ("A", "+5V_DEV", "J_5V_DEV", "B", "+5V_DEV", "J_5V_DEV", "JST-VH lead"),
    ("A", "+54V_POE", "J_54V", "B", "+54V_POE", "J_54V", "JST-VH lead"),
    ("A", "+5V_D8", "J_MEZZ_PWR1", "D", "+5V_D8", "J_PWR1", "JST-VH lead"),
    ("A", "+3V3", "J_MEZZ1", "D", "+3V3", "J_HARN1", "harness pin 13"),
    ("B", "PANEL_5V", "J_PANEL", "C", "+5V", "J_PANEL", "panel ribbon pins 1 and 2"),
]
# rails that leave the set to a load off the boards: (board, net, connector, load)
LOADS = [("A", "+13V8_PA", "J_PA", "30 W PA on the face plate"), ("A", "+12V_HF", "J_HF", "QMX HF in the lid"),
         ("A", "VMON", "J_MON", "Xenarc monitor"), ("A", "VHEAT", "J_HEAT", "pack heater mat"),
         ("A", "PD_VBUS", "J_USBC_OUT", "wall USB-C outlet"), ("A", "VBUS_WALL", "J_USBW", "Glenair USB host port"),
         ("B", "+54V_POE", "U5", "wall RJ45 PoE (TPS23861)"), ("E", "CELL_F", "J_FAN1", "mixer fans J_FAN1, J_FAN2")]
SOURCES = [("P", "CELL4", "W_BP", "4S cell block (D-06: 4S3P Samsung 35E)"), ("E", "DC_IN", "J_DCIN", "vehicle or shore, 9 to 36 V"),
           ("E", "PV_IN", "J_SOLAR", "solar panel")]
BOARD_ORDER = ["P", "E", "A", "B", "C", "D"]


# The FET pin maps the walk relies on, each from a maker's sheet held in v2/vendor/.
CSD_SHEETS = ("v2/vendor/power/ti-csd19532q5b-n-fet.pdf, v2/vendor/battery/ti-csd18510q5b.pdf and "
              "v2/vendor/battery/ti-csd17570q5b.pdf (top view: pins 1 to 3 S, 4 G, 5 to 8 D; the symbols join 5 to 8 as pin 5)")
# The review of 27 September 2026 ran the earlier walk on these five wrong entries (another stage's controller with this
# stage's shunt) and it accepted all five; the walk below must refuse each of them on every build.
REVIEW_WRONG = [("A", "VBAT", "+5V_DEV", ("U4", "R43")), ("A", "VBAT", "+13V8_PA", ("U15", "R55")),
                ("A", "VBAT", "+54V_POE", ("U19", "R71")), ("A", "VBAT", "PD_VPWR", ("U16", "R81")),
                ("A", "VBAT", "+5V_S2", ("U7", "R35"))]


def is_ground(net):
    return net.lstrip("/").startswith("GND") or net.startswith("unconnected")


def gate_pin(nl, ref):
    """The gate pin of a FET, or None when the part is not a FET whose gate the netlist identifies: the pin the symbol
    names G (the SOT-23 and TDSON-8 symbols), else pin 4 of a TI CSD part in PowerPAK SO-8 (CSD_SHEETS)."""
    if not ref.startswith("Q"):
        return None
    g = [p for p in nl.pins.get(ref, {}) if nl.fn.get((ref, p)) == "G"]
    if len(g) == 1:
        return g[0]
    if nl.value(ref).startswith("CSD") and "PowerPAK" in nl.parts[ref]["footprint"] and len(nl.pins[ref]) == 5:
        return "4"
    return None


def is_pass_fet(nl, ref):
    """A FET in a power package (five pins or more) with an identified gate: the only kind a converter stage passes current
    through without naming it."""
    return gate_pin(nl, ref) is not None and len(nl.pins.get(ref, {})) >= 5


def is_inductor(nl, ref):
    return ref.startswith("L") and not ref.startswith("LED") and len(nl.pins.get(ref, {})) == 2


def is_ic(ref):
    """A controller must be an integrated circuit: a U reference. A resistor or capacitor on a FET's gate drives nothing."""
    return ref.startswith("U")


def drivers(nl, fet, rails):
    """The parts that drive a FET's gate: every part with a pin on the gate net, or with a pin on a private net joined to
    the gate by one series resistor (that net carries only the resistor, the driver and test points; never a rail, a
    ground or the FET's own source or drain)."""
    g = nl.pins[fet][gate_pin(nl, fet)]
    chan = {n for p, n in nl.pins[fet].items() if p != gate_pin(nl, fet)}
    out = {d["ref"] for d in nl.nets[g] if d["ref"] != fet}
    for d in nl.nets[g]:
        r = d["ref"]
        if not r.startswith("R") or len(nl.pins.get(r, {})) != 2:
            continue
        far = [n for p, n in nl.pins[r].items() if p != d["pin"]][0]
        if far in rails or far in chan or is_ground(far):
            continue
        others = [x["ref"] for x in nl.nets[far] if x["ref"] != r and not x["ref"].startswith("TP")]
        if len(others) == 1:
            out.add(others[0])
    return out


def stage_graph(nl, via, rails, blocked):
    """The parts a stage may pass current through, as {ref: the pins it may be crossed between}.
    - a named FET: source to drain, never its gate;
    - a named controller (an IC that drives the gate of a power-package FET, directly or through one series resistor):
      never crossed itself; the FETs it drives are crossed source to drain;
    - any other named part (a fuse, a shunt, an integrated converter, eFuse, load switch or LDO): between any of its pins;
    - an unnamed two-pin inductor: only when one of its nets is a switching node, i.e. not a rail of the table and not a
      ground, and carries a pin of a named part or of a FET crossed above.
    Parts in `blocked` are left out, and a blocked controller takes the FETs it drives with it."""
    fets = [q for q in nl.pins if is_pass_fet(nl, q)]
    drv = {q: drivers(nl, q, rails) for q in fets}
    ctrl = {r for r in via if gate_pin(nl, r) is None and is_ic(r) and any(r in drv[q] for q in fets)}
    live = [r for r in via if r not in blocked]
    cross = {}
    for r in live:
        if gate_pin(nl, r) is not None:
            cross[r] = [p for p in nl.pins[r] if p != gate_pin(nl, r)]
        elif r not in ctrl:
            cross[r] = list(nl.pins[r])
    for q in fets:
        if q in blocked or q in cross:
            continue
        if drv[q] & (set(live) & ctrl):
            cross[q] = [p for p in nl.pins[q] if p != gate_pin(nl, q)]
    for r in via:                        # a blocked controller's FETs go with it, named or not
        if r in blocked and r in ctrl:
            for q in fets:
                if r in drv[q] and not (drv[q] & (set(live) & ctrl)):
                    cross.pop(q, None)
    touch = {nl.pins[r][p] for r, ps in cross.items() for p in ps} | {n for r in live if r in ctrl for n in nl.pins[r].values()}
    for l in nl.pins:
        if l in blocked or l in cross or not is_inductor(nl, l):
            continue
        if any(n in touch and n not in rails and not is_ground(n) for n in nl.pins[l].values()):
            cross[l] = list(nl.pins[l])
    return cross, ctrl, drv


def reach(nl, f, t, cross, rails):
    seen, todo, used = {f}, [f], set()
    while todo:
        n = todo.pop()
        if n == t:
            continue
        for d in nl.nets.get(n, []):
            r = d["ref"]
            if r not in cross or d["pin"] not in cross[r]:
                continue
            for p in cross[r]:
                m = nl.pins[r][p]
                if m == n or is_ground(m) or (m in rails and m != t):
                    continue
                used.add(r)
                if m not in seen:
                    seen.add(m); todo.append(m)
    return t in seen, used


def named_rails(nl, ref, rails):
    """The rails of the table that a part's value text names, as whole net names."""
    v = nl.value(ref)
    return {r.lstrip("/") for r in rails if re.search(r"(?<![\w+])%s(?![\w])" % re.escape(r.lstrip("/")), v)}


def enable_label(nl, what):
    """The enable net a stage's description names in parentheses, as the netlist spells it, or None."""
    m = re.search(r"\(([A-Z][A-Z0-9_+]*)[:;,)]", what or "")
    return nl.net(m.group(1))[0] if m else None


def enable_pin(nl, via, en):
    """Where a named IC of the stage meets the enable net: 'U4 pin 3' on the net itself, or 'U13 pin 1 through R58' on a
    net joined to it by one two-pin resistor whose pins sit on two nets. None when no named IC meets it."""
    for r in via:
        if not is_ic(r):
            continue
        for p, n in sorted(nl.pins.get(r, {}).items()):
            if n == en:
                return "%s pin %s (%s)" % (r, p, nl.fn.get((r, p)) or "")
    for d in nl.nets.get(en, []):
        rr = d["ref"]
        if rr.startswith("R") and len(nl.pins.get(rr, {})) == 2:
            far = [n for p, n in nl.pins[rr].items() if p != d["pin"]][0]
            if far == en or is_ground(far):
                continue
            for r in via:
                if not is_ic(r):
                    continue
                for p, n in sorted(nl.pins.get(r, {}).items()):
                    if n == far:
                        return "%s pin %s (%s) through %s" % (r, p, nl.fn.get((r, p)) or "", rr)
    return None


def prove(nl, frm, to, via, what=None, en_override=None):
    """Accept a stage only when (1) the walk from `frm` reaches `to` through the stage's parts as stage_graph() allows them,
    never through another rail of the table; (2) every named part is required: with it left out (a controller together
    with the FETs it drives) `to` is no longer reached; and (3) a named part whose value text names rails of the table
    names `to` among them; (4) an enable net named in the description (or `en_override`, for the negative controls) is met
    by a named IC, directly or through one series resistor. Returns (ok, detail dict, why)."""
    rails = {"/" + n.lstrip("/") for (b, f, t, _, _) in TREE if b == nl.board for n in (f, t)}
    rails = {nl.net(r)[0] or r for r in rails}
    f, t = nl.net(frm)[0], nl.net(to)[0]
    if not f or not t:
        return False, {}, "net %s or %s is not in the netlist" % (frm, to)
    for r in via:
        if r not in nl.parts:
            return False, {}, "part %s is not in the netlist" % r
        if r.startswith("Q") and gate_pin(nl, r) is None:
            return False, {}, "named FET %s has no gate pin the netlist or a held sheet identifies" % r
    cross, ctrl, drv = stage_graph(nl, via, rails, set())
    ok, used = reach(nl, f, t, cross, rails)
    det = dict(used=sorted(used), ctrl={r: sorted(q for q in drv if r in drv[q] and q in used) for r in ctrl},
               text={}, required=[])
    if not ok:
        return False, det, "did not reach %s" % to
    for r in via:
        c2, _, _ = stage_graph(nl, via, rails, {r})
        still, _ = reach(nl, f, t, c2, rails)
        if still:
            return False, det, "%s is not required: %s is reached without it%s" % (
                r, to, " and the FETs it drives" if r in ctrl else "")
        det["required"].append(r)
    for r in via:
        nr = named_rails(nl, r, rails)
        if nr:
            det["text"][r] = sorted(nr)
            if to.lstrip("/") not in nr:
                return False, det, "%s's value text names %s, not %s" % (r, ", ".join(sorted(nr)), to)
    for r, qs in det["ctrl"].items():
        if not qs:
            return False, det, "controller %s drives no FET on the path" % r
    en = en_override or enable_label(nl, what)
    if en:
        pin = enable_pin(nl, via, en)
        det["enable"] = "%s: %s" % (N.short(en), pin or "no named IC")
        if not pin:
            return False, det, "the description names enable %s, which no named IC of the stage meets" % N.short(en)
    return True, det, "reached through %s" % ", ".join(det["used"])


NEG_CLASSES = ("the review's five", "ICs swapped", "shunts and fuses swapped", "shunts and fuses added", "ICs added",
               "controller replaced, its FETs named", "enable label swapped")


def negative_controls(nls):
    """Wrong entries every build must refuse, as (board, from, to, parts, class, what): the review's five; for every two
    stages of one board, each with its ICs replaced by the other's, with its shunts and fuses replaced by the other's, with
    the other's shunts or fuses added and with the other's ICs added (parts the path does not need); and every stage
    built on a controller with that controller replaced by each other stage's IC while the FETs it drove are named
    outright, so the path is still there and only the attribution is wrong."""
    out = [(b, f, t, v, NEG_CLASSES[0], "review of 27 Sep 2026", None) for b, f, t, v in REVIEW_WRONG]
    for i, (b, f, t, v, _) in enumerate(TREE):
        for j, (b2, f2, t2, v2, _) in enumerate(TREE):
            if i == j or b != b2:
                continue
            for cls, key in (("U", NEG_CLASSES[1]), ("RF", NEG_CLASSES[2])):
                mine = [r for r in v if r[0] in cls]; theirs = [r for r in v2 if r[0] in cls]
                if mine and theirs and set(mine) != set(theirs):
                    out.append((b, f, t, tuple([r for r in v if r[0] not in cls] + theirs), key, "from the %s to %s stage" % (f2, t2), None))
            for cls, key in (("RF", NEG_CLASSES[3]), ("U", NEG_CLASSES[4])):
                extra = [r for r in v2 if r[0] in cls and r not in v]
                if extra:
                    out.append((b, f, t, tuple(list(v) + extra), key, "from the %s to %s stage" % (f2, t2), None))
    for b, f, t, v, what in TREE:
        ok, det, _ = prove(nls[b], f, t, v, what)
        if not ok or not det["ctrl"]:
            continue
        fets = sorted({q for qs in det["ctrl"].values() for q in qs} - set(v))
        base = [r for r in v if r not in det["ctrl"]] + fets
        for b2, f2, t2, v2, _ in TREE:
            if b2 != b or (f2, t2) == (f, t):
                continue
            for r2 in v2:
                if r2[0] == "U" and r2 not in v:
                    out.append((b, f, t, tuple(base + [r2]), NEG_CLASSES[5], "%s of the %s to %s stage" % (r2, f2, t2), None))
    for b, f, t, v, what in TREE:                  # the enable label check must tell one stage's enable from another's
        en = enable_label(nls[b], what)
        if not en:
            continue
        for b2, f2, t2, v2, what2 in TREE:
            en2 = enable_label(nls[b2], what2) if b2 == b else None
            if en2 and en2 != en and not enable_pin(nls[b], v, en2):
                out.append((b, f, t, v, NEG_CLASSES[6], "the enable of the %s to %s stage, %s" % (f2, t2, N.short(en2)), en2))
    return out


SWEEP_SKIP = ("TP", "C", "J", "H", "MH")      # never a stage's part: test points, capacitors, connectors, holes


def substitution_sweep(nls):
    """The second review's sweep of 27 September 2026, run on every build: each stage with one named part replaced by a
    part on the nets its walk touched, and each stage cut down to one such part. Nothing is refused; the accepted ones are
    returned as (board, from, to, typed parts, tried parts, walk, 'same path' or 'off the path'), where 'same path' means
    every part put in was already crossed by the typed stage's own walk (fewer or other parts of the same path named)
    and 'off the path' means a part the typed walk does not cross made the stage pass (a wrong attribution)."""
    tried, acc = 0, []
    for b, f, t, v, what in TREE:
        nl = nls[b]
        ok, det, _ = prove(nl, f, t, v, what)
        fN, tN = nl.net(f)[0], nl.net(t)[0]
        used = set(det.get("used", []))
        nets = {x for x in ({fN, tN} | {nl.pins[r][p] for r in used for p in nl.pins[r]}) if x and not is_ground(x)}
        cands = [c for c in sorted({d["ref"] for x in nets for d in nl.nets.get(x, [])} - set(v)) if not c.startswith(SWEEP_SKIP)]
        tries = {(c,) for c in cands} | {tuple(v[:i]) + (c,) + tuple(v[i + 1:]) for i in range(len(v)) for c in cands}
        for via in sorted(tries):
            tried += 1
            ok2, det2, _ = prove(nl, f, t, via, what)
            if ok2:
                new = [x for x in via if x not in v]
                acc.append((b, f, t, v, via, det2.get("used", []), "same path" if set(new) <= used else "off the path"))
    return tried, acc


def netlist_findings(nls):
    """Two-pin parts whose two pins sit on one net, on every board read: a part that does nothing as drawn."""
    out = []
    for b in BOARD_ORDER:
        nl = nls[b]
        for r, ps in sorted(nl.pins.items()):
            if len(ps) == 2 and len(set(ps.values())) == 1 and not r.startswith(("TP", "J")):
                out.append("board %s: %s (%s) has both pins on %s" % (b, r, nl.value(r)[:40], N.short(list(ps.values())[0])))
    return out


# Which edges are drawn orange ("a fuse or polyfuse"): decided by what the netlist says each named part is, never by its
# designator. The earlier rule, a reference starting with F, drew board D's FB1 (a 600R ferrite bead) as a fuse and so
# claimed overcurrent protection on the exciter supply that board D does not have (independent check of 27 September
# 2026, pass 2). KiCad's two fuse symbols, plus the one fuse the netlists draw on a generic symbol, checked by its value
# text: board P's F2, the Eaton SCF9550 self-control fuse on a three-pin connector symbol.
FUSE_LIBS = ("Device:Fuse", "Device:Polyfuse")
FUSE_BY_VALUE = {("P", "F2"): "self-control fuse"}
FUSE_WORD = re.compile(r"\b(poly)?fuse\b", re.I)   # an "eFuse" is not a fuse: no word boundary before its F


def is_fuse(nl, b, ref):
    p = nl.parts[ref]
    if p["lib"] in FUSE_LIBS:
        return True
    need = FUSE_BY_VALUE.get((b, ref))
    return need is not None and need in p["value"]


def fuse_problem(nls, b, via, what):
    """None when the edge's colour and its typed description agree: every named part a fuse by the netlist exactly when
    the description calls the stage a fuse or polyfuse. A typed fuse whose value text moved is a refusal too."""
    for (fb, r), need in FUSE_BY_VALUE.items():
        if fb == b and r in via and need not in nls[b].parts[r]["value"]:
            return "%s %s is typed a fuse by its value text '%s'; the netlist's value reads '%s'" % (b, r, need, nls[b].value(r))
    fuse = all(is_fuse(nls[b], b, r) for r in via)
    if fuse != bool(FUSE_WORD.search(what)):
        return "%s %s ('%s'): the description %s a fuse and the netlist's parts (%s) %s" % (
            b, "+".join(via), what, "names" if FUSE_WORD.search(what) else "does not name",
            ", ".join("%s %s" % (r, nls[b].parts[r]["lib"]) for r in via), "are all fuses" if fuse else "are not all fuses")
    return None


def ohms(v):
    m = re.match(r"\s*([0-9.]+)\s*([kKM]?)", v or "")
    return float(m.group(1)) * {"": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}[m.group(2)] if m else None


def enable_census(nl, b, family="LM5176"):
    """How each `family` converter's EN/UVLO pin (pin 1 of the LM5176, SNVSAI1D pin table) is driven, read from the
    netlist: [(ref, rail it makes, kind, text, details)]. 'divider' when the pin's net carries only resistors and capacitors, one
    resistor to another net X and resistors to GND: the pin takes Rb/(Rt+Rb) of X. 'direct' otherwise: the pin sits on
    the enable net itself, which other parts drive."""
    out = []
    refs = [r for r in nl.parts if (nl.value(r) or "").startswith(family)]
    for u in sorted(refs, key=lambda r: int(re.sub(r"\D", "", r) or 0)):
        en = nl.pins[u].get("1")
        rail = [t for tb, _, t, via, _ in TREE if tb == b and u in via]
        members = sorted((r, p) for r, ps in nl.pins.items() if r != u for p, n in ps.items() if n == en)
        rc = sorted({r for r, _ in members if r[0] in "RC" and not r.startswith("CON")})
        drivers_ = ["%s.%s" % (r, p) for r, p in members if r not in rc]
        legs = []
        for r in rc:
            nets = list(nl.pins[r].values())
            other = [n for n in nets if n != en]
            legs.append((r, N.short(other[0]) if other else None))
        tops = [(r, o) for r, o in legs if r.startswith("R") and o not in (None, "GND")]
        bots = [(r, o) for r, o in legs if r.startswith("R") and o == "GND"]
        caps = ["%s %s to %s" % (r, nl.value(r), o) for r, o in legs if r.startswith("C") and o]
        selfs = [r for r, o in legs if o is None]
        if not drivers_ and len(tops) == 1 and len(bots) == 1 and not selfs:
            (rt, x), (rb, _) = tops[0], bots[0]
            k = ohms(nl.value(rb)) / (ohms(nl.value(rt)) + ohms(nl.value(rb)))
            text = "takes %s of %s: %s %s from %s to %s over %s %s to GND%s" % (
                ("%.2f" % k).rstrip("0"), x, rt, nl.value(rt), x, N.short(en), rb, nl.value(rb),
                (", " + ", ".join(caps)) if caps else "")
            out.append((u, rail[0] if rail else "?", "divider", text, dict(top=rt, bottom=rb, of=x, k=("%.2f" % k).rstrip("0"))))
        else:
            res = ["%s %s to %s" % (r, nl.value(r), o) for r, o in legs if r.startswith("R") and o] + caps
            res += ["%s %s with both pins on %s" % (r, nl.value(r), N.short(en)) for r in selfs]
            text = "sits on %s directly (the net's other pins: %s)%s" % (
                N.short(en), ", ".join(drivers_) or "none", (": " + "; ".join(res)) if res else "")
            out.append((u, rail[0] if rail else "?", "direct", text, dict(net=N.short(en), selfs=selfs,
                                                                          res=[r for r, o in legs if o],
                                                                          pulls=[(r, o) for r, o in legs if o and r.startswith("R")])))
    return out


def board_a_enable_note(nl):
    """Board A's R4T-F3 paragraph. The census lines are read from the netlist on every build; the comparison sentence
    typed at the rebuild of 27 September 2026 is printed only while the census still says what it says."""
    cen = {u: (rail, kind, text, d) for u, rail, kind, text, d in enable_census(nl, "A")}
    def both(x, y): return x if x == y else "%s and %s" % (x, y)
    def is_div(u, top): return u in cen and cen[u][1] == "divider" and cen[u][3]["top"] == top
    def is_dir(u, dead, pull):
        """direct on its enable net, `dead` the only part with both pins there, one resistor to GND ('down') or elsewhere ('up')"""
        if u not in cen or cen[u][1] != "direct" or cen[u][3]["selfs"] != ([dead] if dead else []) or len(cen[u][3]["pulls"]) != 1:
            return False
        return (cen[u][3]["pulls"][0][1] == "GND") == (pull == "down")
    L = []
    if is_div("U13", "R58") and is_div("U15", "R124") and is_dir("U16", "R74", "down") and is_dir("U19", "R133", "down") \
            and is_dir("U5", None, "down") and is_dir("U7", None, "up") and "U2" in cen:
        L.append("Board A's R74 (on POE_EN) and R133 (on PD_EN) are the half of R4T-F3 (`v2/docs/records/r4t/r4-decisions.md`) "
                 "that round 8 did not close. Round 8 closed the other half on the PA and HF converters (EMCON L4): R58 and "
                 "R124 (%s) are now the top legs of U13's and U15's enable dividers over R59 and R125 (%s) to GND, %s of "
                 "PA_EN and HF_EN. R74 and R133 each "
                 "have both pins on one net and do nothing, so the PoE and USB-C PD converters U16 and U19 sit on POE_EN and "
                 "PD_EN directly, with %s and %s (%s) as their pull-downs: the way U5 and U7 are driven by design "
                 "(`en_div=False` in `gen_sch_a.py`, read at this rebuild), U5 with a pull-down and U7 with a pull-up (S-08). "
                 "U2's enable is its own supervisor network (`gen_sch_a.py`, the front end). R4T-F3 records that the 62k over "
                 "10k divider, had it been formed as drawn, would have held U16 and U19 in standby. For the board A author; "
                 "nothing here changes it." % (
                     both(nl.value("R58"), nl.value("R124")), both(nl.value("R59"), nl.value("R125")),
                     both(cen["U13"][3]["k"], cen["U15"][3]["k"]),
                     cen["U16"][3]["res"][0], cen["U19"][3]["res"][0],
                     both(nl.value(cen["U16"][3]["res"][0]), nl.value(cen["U19"][3]["res"][0]))))
    else:
        L.append("Board A's R74 (on POE_EN) and R133 (on PD_EN) are the half of R4T-F3 (`v2/docs/records/r4t/r4-decisions.md`) "
                 "that round 8 did not close. The comparison with the other LM5176 stages typed at the rebuild of 27 September "
                 "2026 no longer matches this netlist, so it is not printed; the lines below are read from the netlist. For "
                 "the board A author; nothing here changes it.")
    L += ["", "How each LM5176 on board A has its EN/UVLO pin (pin 1, SNVSAI1D) driven, read from netlist `%s` on this "
          "build:" % nl.sha, ""]
    L += ["- %s (%s) %s" % (u, rail, text) for u, (rail, kind, text, d) in cen.items()]
    return L


def part_text(nl, ref):
    """A part as the drawing names it: the designator and its MPN; a fuse with its rating words, a resistor its value."""
    v = nl.value(ref)
    if ref.startswith("F"):
        return "%s %s" % (ref, re.split(r"[(:]", v)[0].strip())
    if ref.startswith(("L", "FB")):
        return "%s %s" % (ref, " ".join(v.split()[:2]))
    toks = v.split()
    if ref.startswith("R") and len(toks) > 1 and re.fullmatch(r"[0-9.]+", toks[0]):
        return "%s %s %s" % (ref, toks[0], toks[1])      # "5 mOhm ...": the number and its unit
    return "%s %s" % (ref, toks[0].rstrip(":,;") if toks else "")


def build():
    nls = N.load_all(tuple(BOARD_ORDER))
    chain = yaml.safe_load(open(os.path.join(N.REPO, CHAIN), encoding="utf-8"))
    rows, problems, notes = [], [], []
    for b, frm, to, via, what in TREE:
        ok, det, why = prove(nls[b], frm, to, via, what)
        ctrl = "; ".join("%s drives %s" % (r, ", ".join(q)) for r, q in sorted(det.get("ctrl", {}).items())) or "-"
        text = "; ".join("%s: %s" % (r, ", ".join(n)) for r, n in sorted(det.get("text", {}).items())) or "names no rail"
        rows.append((b, frm, to, ", ".join(part_text(nls[b], r) for r in via), what, ", ".join(det.get("used", [])) or "-",
                     ctrl, ", ".join(det.get("required", [])) or "-", text, det.get("enable", "-"), "yes" if ok else "NO: " + why))
        if not ok:
            problems.append("%s %s to %s through %s: %s" % (b, frm, to, via, why))
        fp = fuse_problem(nls, b, via, what)
        if fp:
            problems.append("edge colour: " + fp)
    negs = []
    whats = {(b, f, t): w for b, f, t, _, w in TREE}
    for b, frm, to, via, key, what, en in negative_controls(nls):
        ok, _, why = prove(nls[b], frm, to, via, whats.get((b, frm, to)), en)
        negs.append((b, frm, to, via, key, what, ok, why))
        if ok:
            problems.append("negative control ACCEPTED, the check does not discriminate: %s %s to %s through %s (%s, %s)" % (
                b, frm, to, via, key, what))
    lead_rows = []
    for ba, na, ra, bb, nb, rb, what in LEADS:
        pa = [d["pin"] for d in nls[ba].net(na)[1] if d["ref"] == ra]
        pb = [d["pin"] for d in nls[bb].net(nb)[1] if d["ref"] == rb]
        ok = bool(pa) and bool(pb)
        lead_rows.append((ba, na, "%s.%s" % (ra, ",".join(pa) or "-"), bb, nb, "%s.%s" % (rb, ",".join(pb) or "-"), what, "yes" if ok else "NO"))
        if not ok:
            problems.append("lead %s %s %s to %s %s %s: a connector end is not on its net" % (ba, na, ra, bb, nb, rb))
    for b, net, ref, _ in LOADS + SOURCES:
        if not [d for d in nls[b].net(net)[1] if d["ref"] == ref]:
            problems.append("%s %s is not on %s" % (b, ref, net))
    # the energy chain's stages against the netlists
    stage_rows = []
    for s in chain.get("stages", []):
        prot = s.get("protection") or {}
        ref = prot.get("ref")
        boards = [c for c in re.findall(r"\b([A-Z])\d?\b", str(s.get("board", ""))) if c in nls]
        found = [(b, nls[b].value(ref)) for b in boards if ref in nls[b].parts]
        rated = [(b, v) for b, v in found if prot.get("rating_a") and "%g A" % prot["rating_a"] in v]
        found = rated or found          # the same designator on two boards: keep the one carrying the stage's rating
        stage_rows.append((s["id"], str(s.get("board")), str(s.get("from", ""))[:60], str(s.get("to", ""))[:60],
                           "%s / %s" % (s.get("continuous_a"), s.get("peak_a")), "%s %s A" % (ref, prot.get("rating_a")),
                           "; ".join("%s: %s" % (b, v[:60]) for b, v in found) or "NOT FOUND on %s" % "/".join(boards)))
        if not found:
            notes.append("stage %s names protection %s, which no netlist of board %s carries" % (s["id"], ref, s.get("board")))
    # disagreements this reading found (each is read from the two artefacts, not asserted)
    a = nls["A"]
    if "AP64500" in str([st for st in chain["stages"] if st["id"] == "B_PANEL_5V"]) and a.value("U7").startswith("LM5176"):
        notes.append("pcb_energy_chain.yaml stages B_PANEL_5V, B_HDMI_5V and B_QMX_5V take their prospective fault current from "
                     "'board A's AP64500 buck U7' (IPEAK_LIMIT 6.8 to 9.2 A); board A's netlist makes +5V_DEV with U7 = %s, "
                     "whose limit is its own current loop (ARCHITECTURE.md 4.1: 7.2 to 9.5 A)" % a.value("U7").split(",")[0])
    p = nls["P"]
    if "F2" in p.parts and not [st for st in chain["stages"] if (st.get("protection") or {}).get("ref") == "F2" and st.get("board") == "P"]:
        notes.append("board P's netlist puts F2 (%s) in series between FUSED and SCP_OUT; pcb_energy_chain.yaml has no F2 stage "
                     "and runs PACK_FETS from FUSED (PWR-F12, the re-declaration drafted in "
                     "v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml)" % part_text(p, "F2").split(" ", 1)[1])
    pc = [st for st in chain["stages"] if st["id"] == "PACK_CELLS"]
    if pc and "4S4P" in str(pc[0].get("from")):
        notes.append("pcb_energy_chain.yaml PACK_CELLS still reads '%s'; owner ruling D-06 made the pack one 4S3P block of "
                     "Samsung 35E (about 145 Wh)" % pc[0]["from"])
    e = nls["E"]
    si = [st for st in chain["stages"] if st["id"] == "SHORE_INPUT"]
    if si and "SMCJ33A" in str(si[0].get("note")) and "SMCJ33A" not in " ".join(e.value(r) for r in e.parts):
        notes.append("pcb_energy_chain.yaml SHORE_INPUT's note names an SMCJ33A clamp; board E's netlist carries none "
                     "(its clamps are %s)" % ", ".join("%s %s" % (r, e.value(r).split(" ")[0]) for r in sorted(e.parts)
                                                        if e.value(r).startswith("SMCJ")))
    b = nls["B"]
    if "/VBAT" in b.nets:
        notes.append("board B's net VBAT is the CR2032 backup (BT1) for the modules' RTCs, the LG290P and the DS3231, "
                     "not board A's VBAT: the same name on two boards, never joined")
    sweep = substitution_sweep(nls)
    return nls, chain, rows, lead_rows, stage_rows, problems, notes, negs, sweep, netlist_findings(nls)


def nid(b, net):
    return "%s_%s" % (b, re.sub(r"[^A-Za-z0-9]", "_", net))


def mermaid(nls, chain, head, n_neg, n_off, n_tried):
    stage_of = {}
    for s in chain.get("stages", []):
        ref = (s.get("protection") or {}).get("ref")
        stage_of.setdefault((str(s.get("board")), ref), []).append(s)
    L = ["---", "title: \"Power tree read from the netlists named in each board's box and pcb_energy_chain.yaml sha256/16 %s (design diagram of an unbuilt prototype)\"" % N.sha16(CHAIN),
         "---", "flowchart LR"]
    rails = {}
    for b, frm, to, via, what in TREE:
        rails.setdefault(b, []).extend([frm, to])
    for ba, na, ra, bb, nb, rb, what in LEADS:
        rails.setdefault(ba, []).append(na); rails.setdefault(bb, []).append(nb)
    for b in BOARD_ORDER:
        nl = nls[b]
        L.append("  subgraph brd%s[\"%s, netlist %s at %s\"]" % (b, N.BOARD_TITLES[b], nl.sha, nl.commit))
        for r in dict.fromkeys(rails.get(b, [])):
            L.append("    %s([\"%s\"]):::rail" % (nid(b, r), r))
        for src_b, net, ref, what in SOURCES:
            if src_b == b:
                L.append("    src_%s_%s[\"%s: %s\"]:::source" % (b, ref, ref, what))
        for lb, net, ref, what in LOADS:
            if lb == b:
                L.append("    load_%s_%s[\"%s: %s\"]:::load" % (b, ref, ref, what))
        L.append("  end")
    L.append("  E5[\"E5 dock block: no schematic, its board names the nets\"]:::lead")
    styles = []
    for src_b, net, ref, what in SOURCES:
        L.append("  src_%s_%s --> %s" % (src_b, ref, nid(src_b, net))); styles.append("src")
    for b, frm, to, via, what in TREE:
        nl = nls[b]
        parts = " + ".join(part_text(nl, r) for r in via)
        st = [s for r in via for s in stage_of.get((b, r), [])]
        tag = (" [chain %s: %s A cont., %s A peak]" % ("/".join(s["id"] for s in st), st[0].get("continuous_a"), st[0].get("peak_a"))) if st else ""
        L.append("  %s -->|\"%s: %s%s\"| %s" % (nid(b, frm), what, parts.replace('"', "'"), tag, nid(b, to)))
        styles.append("chain" if st else ("fuse" if all(is_fuse(nl, b, r) for r in via) else "conv"))
    for ba, na, ra, bb, nb, rb, what in LEADS:
        if ra in ("P_CP", "P_VR", "J_BLK"):
            L.append("  %s ---|\"%s %s\"| E5" % (nid(ba, na), ra, what)); L.append("  E5 --> %s" % nid(bb, nb))
            styles += ["lead", "lead"]
        else:
            L.append("  %s ==>|\"%s to %s: %s\"| %s" % (nid(ba, na), ra, rb, what, nid(bb, nb))); styles.append("lead")
    for lb, net, ref, what in LOADS:
        L.append("  %s --> load_%s_%s" % (nid(lb, net), lb, ref)); styles.append("load")
    colour = {"chain": "#c62828", "fuse": "#e65100", "conv": "#37474f", "lead": "#1565c0", "load": "#6d4c41", "src": "#2e7d32"}
    for i, s in enumerate(styles):
        L.append("  linkStyle %d stroke:%s,stroke-width:%s" % (i, colour[s], "3px" if s in ("chain", "lead") else "1.5px"))
    L += ["  classDef rail fill:#fffde7,stroke:#827717,color:#000",
          "  classDef source fill:#e8f5e9,stroke:#2e7d32,color:#000",
          "  classDef load fill:#efebe9,stroke:#6d4c41,color:#000",
          "  classDef lead fill:#e3f2fd,stroke:#1565c0,color:#000",
          "  classDef note fill:#f5f5f5,stroke:#9e9e9e,color:#333,stroke-dasharray:3 3",
          "  NOTE[\"Rounded nodes are nets as the netlists name them (each board's own names: board B's VBAT_RTC is its CR2032 net, VBAT until W3B-R1). "
          "Red edges are stages of pcb_energy_chain.yaml with its declared continuous and peak current; orange, a fuse or "
          "polyfuse (as the netlist gives the part, never by its designator); grey, any other series stage: a converter, load "
          "switch, eFuse, ideal diode, hot swap, current shunt, ferrite bead or choke; blue, a lead between boards. Which parts make each stage (the part names on "
          "each edge) is typed in tools/power_tree.py, not found by it; every build checks that typing against the netlist: "
          "the path runs only through the named parts, the FETs a named controller IC drives and the inductors on their "
          "switching nodes, each named part is required, a controller counts only through the FET gates it drives on the "
          "path, an enable named in brackets is met by a named IC, and %d wrong entries (swapped controllers, shunts and "
          "enables among them) are refused. The attribution check is not complete: a part bridging a stage's two nets "
          "(a monitor, a feedback resistor, a load) passes in place of the stage's own part (%d of %d substitutions tried "
          "at this build), so the parts named were also read by hand. It does not check that a "
          "stage works; power-tree.md has the method and its limits. NOT SHOWN: "
          "currents drawn, losses and heat (POWER-THERMAL.md), which rail is on in which power state, "
          "grounds and returns, the CM5 modules' internal rails, clamps and bulk capacitors. The chain file does not yet carry "
          "PWR-F12's F2 stage (its pack follows D-06 since r8int4): see power-tree.md. Nothing here is built, powered or measured.\"]:::note" % (n_neg, n_off, n_tried)]
    return "\n".join(L) + "\n"


def markdown(nls, rows, lead_rows, stage_rows, problems, notes, negs, sweep, findings, head, dirty):
    L = ["# Power tree: the netlist reading behind the diagram", "",
         "Generated by `v2/docs/diagrams/tools/power_tree.py`; do not edit by hand. Design diagram of an unbuilt prototype: no V2 "
         "board has been fabricated, ordered or powered, and no current or voltage below is measured. The diagram is "
         "`svg/power-tree.svg` (source `src/power-tree.mmd`).", "",
         N.tree_line(head, dirty) + " Energy chain `%s` sha256/16 `%s` (last changed `%s`)." % (CHAIN, N.sha16(CHAIN), N.last_commit(CHAIN)), "",
         "| Board | Netlist | sha256/16 | Last changed |", "|---|---|---|---|"]
    for b in BOARD_ORDER:
        nl = nls[b]; L.append("| %s | `%s` | `%s` | `%s` |" % (b, nl.path, nl.sha, nl.commit))
    L += ["", "## Disagreements between the energy chain and the netlists", ""]
    L += ["- %s" % n for n in notes] or ["- none"]
    L += ["", "## Netlist findings on the boards read (not disagreements with the chain)", ""]
    L += ["- %s" % n for n in findings] or ["- none"]
    if any(" R74 " in n or " R133 " in n for n in findings):
        L += [""] + board_a_enable_note(nls["A"])
    L += ["", "## Stages, typed in the tool and checked against the netlists", "",
          "Which parts make each stage is typed in `TREE` in `tools/power_tree.py`. The build accepts a stage only when all of these "
          "hold in the netlist, and refuses to write anything otherwise:", "",
          "1. **Path.** A walk from the first net reaches the second through the stage's parts only, never through another rail "
          "of the table or a ground. A named FET is crossed source to drain, never through its gate (gate pins as each symbol "
          "names them, or pin 4 of a TI CSD part in PowerPAK SO-8 per %s). A named controller, an IC (a U reference) that drives "
          "the gate of a power FET directly or through one series resistor on a private net, is never crossed itself; only "
          "the FETs it drives are; a resistor or capacitor on a gate is never a controller. Any other named part is crossed between any of its pins. An unnamed inductor is crossed only when one "
          "of its nets is a switching node (not a rail, not a ground) carrying a pin of those parts." % CSD_SHEETS,
          "   Two rules came in with the rebuild of 27 September 2026 at round 8, closing the second review's classes (1) "
          "and (3): the controller must be an IC, and a two-pin reference starting with LED is never taken as an inductor.",
          "2. **Each named part required.** With the part left out, and a controller together with the FETs it drives, the walk "
          "no longer arrives. So a controller is attributed by the FET gates it drives on the path, not by touching the stage's nets.",
          "3. **Value text.** A named part whose value text names rails of the table must name the stage's end net among them.",
          "4. **Enable label.** A stage whose description names an enable net in parentheses must have a named IC with a pin "
          "on that net, or on a net joined to it by one series resistor (an enable divider's top leg); the 'Enable' column "
          "names the pin. The pin's name there is the generator's; that each such pin is the part's enable pin was read "
          "against the maker's pin table by hand at the rebuild (`v2/docs/diagrams/README.md`).",
          "5. **Negative controls.** %d wrong entries are refused on every build (listed below by class): the five entries the "
          "review of 27 September 2026 found the earlier walk accepted; for every two stages of one board, each with its "
          "ICs swapped for the other's, its shunts and fuses swapped, and the other's shunts and fuses or ICs added; and "
          "every stage built on a controller with that controller replaced by each other stage's IC while the FETs it drove "
          "are named outright, so the path is still there and only the attribution is wrong; and every stage with an enable "
          "label with it replaced by each other stage's enable net on the board." % len(negs), "",
          "**Limits, stated plainly.** The stage names and descriptions are typed, and so is which parts make each stage: the "
          "tool checks that typing, it does not find the parts itself. A named IC (an integrated converter, eFuse, load switch "
          "or LDO) is crossed between any of its pins: the walk does not know which of its pins carry the current, only that "
          "the stage needs the part. A stage may name fewer parts than its path crosses (a controller's FETs need not be named); "
          "the 'Walk crossed' and 'Controller drives' columns below list every part the walk used. The check says nothing about "
          "whether a stage works, its ratings or its components' values; that is the circuit reviews' and "
          "`v2/docs/feasibility/POWER-THERMAL.md`'s work."
          " **Its attribution check is not complete.** The listed negative-control classes are refused, but a part that "
          "bridges the stage's two nets (a current monitor, a feedback resistor, a load's supply pins) is accepted in place of "
          "the stage's own part, because a named IC is crossed between any of its pins. The sweep below measures that on "
          "every build: %d single-part substitutions and cut-downs tried, %d accepted, %d of them naming a part off the typed "
          "stage's path (wrong attributions the check cannot see) and %d naming only parts of the typed stage's own path. "
          "(The second review of 27 September 2026, an AI review, ran the same sweep at `e3aedb25`: 3822 tried, 27 accepted, "
          "18 distinct wrong attributions; the controller and LED rules above closed its classes (1) and (3).) Which parts "
          "make each stage therefore also rests on a reading by hand of every named part's value text against the stage, "
          "redone at each rebuild (`v2/docs/diagrams/README.md` names the last one)." % (
              sweep[0], len(sweep[1]), len([a for a in sweep[1] if a[6] == "off the path"]),
              len([a for a in sweep[1] if a[6] == "same path"])), "",
          "| Board | From | To | Named parts | Stage | Walk crossed | Controller drives | Required | Value text names | Enable | Accepted |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| %s |" % " | ".join(x.replace("|", "/") for x in r))
    from collections import Counter
    why = Counter()
    for b, f, t, v, key, what, ok, w in negs:
        why[(key, "accepted" if ok else "refused")] += 1
    L += ["", "### Negative controls", "", "| Class | Refused | Accepted |", "|---|---|---|"]
    for key in NEG_CLASSES:
        L.append("| %s | %d | %d |" % (key, why[(key, "refused")], why[(key, "accepted")]))
    L += ["", "The review's five, each with the reason it is refused now:", ""]
    for b, f, t, v, key, what, ok, w in negs:
        if key == NEG_CLASSES[0]:
            L.append("- %s %s to %s through %s: %s" % (b, f, t, " + ".join(v), "ACCEPTED" if ok else "refused, " + w))
    L += ["", "One example of each other class, with the reason it is refused:", ""]
    for cls in NEG_CLASSES[1:]:
        ex = [n for n in negs if n[4] == cls]
        if ex:
            b, f, t, v, key, what, ok, w = ex[0]
            L.append("- %s: %s %s to %s through %s (%s): %s" % (cls, b, f, t, " + ".join(v), what, "ACCEPTED" if ok else "refused, " + w))
    L += ["", "### The substitution sweep: what the check accepts that is not the typed stage", "",
          "Each stage with one named part replaced by a part on a net its walk touched (test points, capacitors, connectors "
          "and holes left out), and each stage cut down to one such part: %d entries, %d accepted. 'Same path' names only "
          "parts the typed stage's own walk crosses (a FET or an inductor in place of the controller that drives it: fewer "
          "parts named, the same conductor); 'off the path' makes the stage pass through a part the typed walk does not "
          "cross, a wrong attribution." % (sweep[0], len(sweep[1])), "",
          "| Board | From | To | Typed parts | Accepted in their place | Walk | Kind |", "|---|---|---|---|---|---|---|"]
    for b, f, t, v, via, used, kind in sweep[1]:
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (b, f, t, " + ".join(v), " + ".join(
            part_text(nls[b], x).replace("|", "/") if x not in v else x for x in via), ", ".join(used), kind))
    L += ["", "## Leads between boards", "", "| Board | Net | Connector.pins | Board | Net | Connector.pins | Lead | Both ends on the net |",
          "|---|---|---|---|---|---|---|---|"]
    for r in lead_rows:
        L.append("| %s |" % " | ".join(r))
    L += ["", "## The stages of `pcb_energy_chain.yaml`, their protective element read in the netlist", "",
          "| Stage | Board | From | To | Continuous / peak A | Protection | In the netlist |", "|---|---|---|---|---|---|---|"]
    for r in stage_rows:
        L.append("| %s |" % " | ".join(x.replace("|", "/").replace("\n", " ") for x in r))
    L += ["", "Problems: %s" % ("none" if not problems else "")] + ["- %s" % p for p in problems]
    L += ["", "## What this reading does not show", "",
          "- Currents, efficiencies, losses and thermal limits: `v2/docs/feasibility/POWER-THERMAL.md` (PROVISIONAL).",
          "- Which converter runs in which power state: `v2/docs/ARCHITECTURE.md` section 4.3 and `CONOPS.md` section 4a.",
          "- Grounds and returns, clamps, bulk and decoupling capacitors, the CM5 modules' internal rails.",
          "- Board E5: no schematic; its board file passes CELL_F, VIN_RAW and the signals to board A's spring pins."]
    return "\n".join(L) + "\n"


def main():
    head, dirty = N.git_rev([N.BOARDS[b] for b in BOARD_ORDER] + [CHAIN])
    nls, chain, rows, lead_rows, stage_rows, problems, notes, negs, sweep, findings = build()
    if problems:
        print("power-tree: REFUSED, the netlists do not support:"); [print("  " + p) for p in problems]
        return 1
    n_off = len([a for a in sweep[1] if a[6] == "off the path"])
    open(OUT_MMD, "w", encoding="utf-8").write(mermaid(nls, chain, head, len(negs), n_off, sweep[0]))
    open(OUT_MD, "w", encoding="utf-8").write(markdown(nls, rows, lead_rows, stage_rows, problems, notes, negs, sweep, findings, head, dirty))
    print("power-tree: %d stages and %d leads checked against the netlists, %d negative controls refused; %d disagreements "
          "with the energy chain; substitution sweep %d tried, %d accepted (%d off the path); %d netlist findings" % (
              len(rows), len(lead_rows), len(negs), len(notes), sweep[0], len(sweep[1]), n_off, len(findings)))
    for n in notes + findings:
        print("  " + n)
    for a in sweep[1]:
        print("  sweep accepted (%s): %s %s to %s, %s in place of %s" % (a[6], a[0], a[1], a[2], " + ".join(a[4]), " + ".join(a[3])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
