#!/usr/bin/env python3
"""The pack SMBus lead is a connector pair (S-05 of MESHSAT-1357, adjudication A07, 26 September 2026).

Board P's J_SMB is a JST-XH 1x4 at 2.50 mm (SMBC, SMBD, GND, PRES) and board E's was a 1x6 pin header at 2.54 mm
(SDA0, SCL0, SDA1, SCL1, GND, GND). No lead can be made for that pair and a straight one would cross clock and
data. check_contracts.py now holds the lead: family, pitch and count at both ends, pin n's role at both ends, and
P's return on its own negative lead. Each fixture is a two-board tree (P and E) run through the real script."""
import os, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import sch_prov


def _write(ecad, stem, letter, comps, nets):
    d = os.path.join(ecad, stem, "out"); os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s")\n      (value "%s")\n      (footprint "%s")\n      (tstamps "x"))\n' % (r, v, fp)
                for r, (v, fp) in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        n += '    (net (code "%d") (name "/%s")\n%s    )\n' % (
            i, name, "".join('      (node (ref "%s") (pin "%s"))\n' % (r, p) for r, p in nodes))
    p = os.path.join(d, stem + ".net")
    open(p, "w").write('(export (version "E")\n  (components\n%s  )\n  (nets\n%s  )\n)\n' % (c, n))
    sch_prov.write(p, letter, TOOLS)          # this tree's own generator identity, so the netlist is current
    return p


XH4 = "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
PH6 = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"


def _tree(e_shape, p_return="PACK_N", e_map=None, clamp_return=None):
    """clamp_return: None for P's SMBus lines with no clamp, or the net two PESD5V0S1BA clamps return to."""
    ecad = tempfile.mkdtemp(prefix="smb-")
    comps = {"J_SMB": ("SMBus lead (JST-XH 1x4)", XH4), "W_N": ("lead -", "Connector:X"), "W_P": ("lead +", "Connector:X"),
             "R10": ("2m shunt", "R"), "R14": ("PRES pull-down", "R")}
    nets = {"SMBC": [("J_SMB", "1")], "SMBD": [("J_SMB", "2")], "PRES": [("J_SMB", "4"), ("R14", "1")],
            "PACK_N": [("W_N", "1"), ("R10", "2")] + ([("J_SMB", "3")] if p_return == "PACK_N" else []),
            "GND": [("R10", "1"), ("R14", "2")] + ([("J_SMB", "3")] if p_return == "GND" else []),
            "PACK_P": [("W_P", "1")]}
    if clamp_return:
        comps["D2"] = ("PESD5V0S1BA (SMBC ESD clamp)", "D_SOD-323"); comps["D3"] = ("PESD5V0S1BA (SMBD ESD clamp)", "D_SOD-323")
        nets["SMBC"].append(("D2", "1")); nets["SMBD"].append(("D3", "1"))
        nets[clamp_return] += [("D2", "2"), ("D3", "2")]
    _write(ecad, "pcb-p-pack", "p", comps, nets)
    e_map = e_map or ({"1": "SCL0", "2": "SDA0", "3": "GND"} if e_shape == XH4 else
                      {"1": "SDA0", "2": "SCL0", "3": "SDA1", "4": "SCL1", "5": "GND", "6": "GND"})
    nets = {}
    for pin, net in e_map.items(): nets.setdefault(net, []).append(("J_SMB", pin))
    _write(ecad, "pcb-e1-dock", "e", {"J_SMB": ("pack SMBus", e_shape)}, nets)
    return ecad


def _run(ecad):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_contracts.py"), ecad], cwd=ecad,
                       capture_output=True, text=True, timeout=300, env=dict(os.environ, VERDICT_DIR=os.path.join(ecad, "out")))
    lines = [l for l in r.stdout.splitlines() if "J_SMB" in l or "SMBus lead" in l]
    return lines, r.stdout + r.stderr


def _state(lines, needle):
    hit = [l for l in lines if needle in l]
    assert len(hit) == 1, (needle, lines)
    return hit[0].split()[0]


def t_the_lead_as_designed_on_25_september_fails_every_contract():
    """DEFECTIVE: board E's 1x6 pin header against board P's XH 1x4, clock and data crossed, P's return on the
    cell-side GND upstream of the shunt."""
    lines, out = _run(_tree(PH6, p_return="GND"))
    assert _state(lines, "has a J_SMB at both ends") == "PASS", lines
    assert _state(lines, "same connector family, pitch and pin count") == "FAIL", lines
    assert _state(lines, "pin n carries the same role") == "FAIL", lines
    assert _state(lines, "return is the pack's own negative lead") == "FAIL", lines


def t_the_lead_of_the_a07_fix_passes_every_contract():
    """ACCEPTABLE: A07's sketch. E's J_SMB is a JST-XH 1x4 with SCL0 on 1, SDA0 on 2, GND on 3 and pin 4 open;
    P's pin 3 is PACK_N, the net its own negative lead W_N lands on."""
    lines, out = _run(_tree(XH4, p_return="PACK_N"))
    for needle in ("has a J_SMB at both ends", "same connector family, pitch and pin count",
                   "pin n carries the same role", "return is the pack's own negative lead"):
        assert _state(lines, needle) == "PASS", (needle, lines, out[-1500:])


def t_the_host_may_ground_the_presence_pin_as_ti_draws_it():
    """ACCEPTABLE (review fix-up of round 4, 26 September 2026): TI SLUSC67B 8.2.2.2.3, "In the host system, this
    pin is grounded". E grounding P's PRES on pin 4 is TI's own arrangement, and E leaving it open is A07's."""
    lines, out = _run(_tree(XH4, e_map={"1": "SCL0", "2": "SDA0", "3": "GND", "4": "GND"}))
    assert _state(lines, "pin n carries the same role") == "PASS", (lines, out[-1200:])


def t_the_host_may_not_drive_the_presence_pin_with_a_signal():
    """DEFECTIVE: a data line on the presence pin is a role mismatch, grounded or open being the only answers."""
    lines, out = _run(_tree(XH4, e_map={"1": "SCL0", "2": "SDA0", "3": "GND", "4": "SDA1"}))
    assert _state(lines, "pin n carries the same role") == "FAIL", lines


def t_the_smbus_clamps_return_to_the_packs_own_negative_lead():
    """DEFECTIVE (board P at main 82dd1e4d): the lines' ESD clamps return to the cell-side GND, so their current
    crosses the shunt. ACCEPTABLE: they return to PACK_N, W_N's net (TI SLUSC67B Figure 30)."""
    lines, out = _run(_tree(XH4, clamp_return="GND"))
    assert _state(lines, "every clamp on the SMBus lead's clock and data lines") == "FAIL", lines
    lines, out = _run(_tree(XH4, clamp_return="PACK_N"))
    assert _state(lines, "every clamp on the SMBus lead's clock and data lines") == "PASS", (lines, out[-800:])
    lines, out = _run(_tree(XH4))
    assert _state(lines, "every clamp on the SMBus lead's clock and data lines") == "FAIL", lines   # no clamp at all


def t_the_right_connector_with_clock_and_data_crossed_still_fails():
    """DEFECTIVE: the same XH 1x4 at both ends, and E wired SDA0 on pin 1 as its old header had it."""
    lines, out = _run(_tree(XH4, e_map={"1": "SDA0", "2": "SCL0", "3": "GND"}))
    assert _state(lines, "same connector family, pitch and pin count") == "PASS", lines
    assert _state(lines, "pin n carries the same role") == "FAIL", lines


def t_the_return_on_the_cell_side_ground_fails_even_with_the_right_connector():
    lines, out = _run(_tree(XH4, p_return="GND"))
    assert _state(lines, "pin n carries the same role") == "PASS", lines
    assert _state(lines, "return is the pack's own negative lead") == "FAIL", lines


def t_the_shape_is_read_from_the_footprint_name():
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    ns = {"re": __import__("re")}
    i, j = src.index("def _conn_shape(fp):"), src.index("_SMB_ROLES = ")
    exec(src[i:j], ns)
    assert ns["_conn_shape"](XH4) == ("JST XH", 2.5, 4)
    assert ns["_conn_shape"](PH6) == ("PinHeader", 2.54, 6)
    assert ns["_conn_shape"]("Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical") == ("JST PH", 2.0, 2)
    assert ns["_conn_shape"]("") is None
