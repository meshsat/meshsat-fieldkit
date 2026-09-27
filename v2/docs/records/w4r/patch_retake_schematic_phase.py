#!/usr/bin/env python3
"""DRAFT for the owner of v2/ecad/tools/retake_schematic_phase.py (stream w4r, MESHSAT-1357, 27 September 2026).

WHY. With the coverage map naming check_contracts_e5 for board E5's INT-001 (verdict_by_board) and rules_status._names
reading it (patch_rules_status.py), the driver plans E5's INT-001 by that name. `_writer_for` finds no
WRITERS_NO_NETLIST entry for check_contracts_<letter> and falls back to WRITERS, which runs check_contracts.py: that tool
writes nothing for E5 (check_contracts.py:742, `if _bd == "E5": continue`), so the step would end "NOT WRITTEN" and the
run fail. Board E5's contract reading is block_contract.py's, run as gate_sweep.sh:226 runs it but without board A's
board file: the tool reads board A's declared phase netlist from the tree (read-only, as the set-level writers read
every board's committed netlist) and the J_DOCK land from the tree's meshsat.pretty.

It needs KiCad's pcbnew (it loads E5's board file and the land), which is not kicad-cli: a new `needs` value "pcbnew"
makes a run on a host without it a SKIP ("a skip is not a pass, run it on the box"), as a step needing kicad-cli is,
rather than a reading that declares its input absent.

Three edits: the WRITERS_NO_NETLIST entry, the "pcbnew" skip in run() and the plan's note in render_plan.
Reverse: delete them; E5's check_contracts_e5 is then planned against check_contracts.py and the run says NOT WRITTEN.

Usage: patch_retake_schematic_phase.py <tree root holding v2/ecad>"""
import os, sys

p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "retake_schematic_phase.py")
s = open(p, encoding="utf-8").read(); o = s


def swap(old, new):
    global s
    if s.count(old) != 1: raise SystemExit("patch_retake: expected exactly one of %r, found %d" % (old[:70], s.count(old)))
    s = s.replace(old, new)


swap('''    "derate":                ("derate.py", ["{T}/derate.py", "{N}.kicad_pcb", "--no-components", E5_DERATE_WHY], None),
''', '''    "derate":                ("derate.py", ["{T}/derate.py", "{N}.kicad_pcb", "--no-components", E5_DERATE_WHY], None),
    # BOARD E5's CONTRACT READING (27 September 2026, stream w4r): block_contract.py writes check_contracts_e5 (SCH-003,
    # and INT-001 on E5 by the coverage map's verdict_by_board); check_contracts.py writes nothing for E5. As
    # gate_sweep.sh:226 runs it, without board A's board file: the tool reads board A's declared phase netlist and the
    # J_DOCK land from the tree, read-only. It loads E5's board file and the land with pcbnew ("pcbnew" below).
    "check_contracts_<letter>": ("block_contract.py", ["{T}/block_contract.py", "{N}.kicad_pcb"], "pcbnew"),
''')
swap('''            if st["needs"] == "kicad" and not have_kicad:
                sr["skipped"] = "kicad-cli is not on this host; a skip is not a pass, run it on the box"
                res["ok"] = False; continue
''', '''            if st["needs"] == "kicad" and not have_kicad:
                sr["skipped"] = "kicad-cli is not on this host; a skip is not a pass, run it on the box"
                res["ok"] = False; continue
            if st["needs"] == "pcbnew" and not have_pcbnew():
                sr["skipped"] = "KiCad's pcbnew is not importable on this host; a skip is not a pass, run it on the box"
                res["ok"] = False; continue
''')
swap('''            if st["needs"] == "kicad" and not have_kicad: note = "   [kicad-cli absent here: SKIPPED on --run]"
''', '''            if st["needs"] == "kicad" and not have_kicad: note = "   [kicad-cli absent here: SKIPPED on --run]"
            elif st["needs"] == "pcbnew" and not have_pcbnew(): note = "   [pcbnew absent here: SKIPPED on --run]"
''')
swap('''def _canon(name, letter):
''', '''def have_pcbnew():
    """Can this interpreter import KiCad's pcbnew? Asked without importing it (the driver itself never needs it)."""
    import importlib.util
    try: return importlib.util.find_spec("pcbnew") is not None
    except (ImportError, ValueError): return False


def _canon(name, letter):
''')
swap('''# `needs`: "netlist" = the board's committed out/<stem>.net; "kicad" = the netlist, the schematic and kicad-cli.
''', '''# `needs`: "netlist" = the board's committed out/<stem>.net; "kicad" = the netlist, the schematic and kicad-cli;
# "pcbnew" = KiCad's Python module (block_contract.py on board E5, which has no netlist).
''')
assert s != o
compile(s, p, "exec")
open(p, "w", encoding="utf-8").write(s)
print("patch_retake_schematic_phase: %s edited (E5's check_contracts_<letter> is block_contract.py's, needs pcbnew)" % p)
