#!/usr/bin/env python3
"""DRAFT for the owner of v2/ecad/tools/rules_status.py (stream w4r, MESHSAT-1357, 27 September 2026).

WHY. The coverage map now names, for board E5 alone, the readings that decide INT-001 there
(`verification.verdict_by_board: {e5: "interfaces_<letter>, check_contracts_<letter>"}`, pcb_rules_coverage.yaml, this
stream's own file). rules_status.py reads a row's verdict names in two places and neither knows that field, and the
writer of the per-board reading, block_contract.py, is not declared in CONFIG_INPUTS, so every reading of it is
CONFIG_UNDECLARED whatever it records. Two edits, nothing else:

  1. `_names(c, letter)` reads `verification.verdict_by_board[letter]` where the row carries one, else `verdict` as
     before, and `result_for` asks `_names` instead of parsing `verdict` itself. evidence_class, retake_projection and
     the re-take driver already ask `_names`, so every reader of the map reads one list for a board and a reading
     cannot be decided from one verdict and bound from another. A row without the field reads exactly as before.
  2. CONFIG_INPUTS["block_contract.py"]: the land glob meshsat.pretty/*.kicad_mod (the J_DOCK land the reading records
     by sha; the glob is conservative, as pin_map_lands.py's is). Its other reads are artefacts recorded by sha (E5's
     board file, board A's netlist, the latter by content16 too) or the coverage map it reads to name the rules it
     decides, as verdict.py does for every writer.

rules_status.py is imported by jlc_certify.py, so this edit moves jlc_certify's code bundle: its readings read
TOOL_CHANGED until re-taken (network; the parts stream) or vouched by a `kind: tool` compatibility entry. The edit does
not touch anything jlc_certify calls (_names, result_for and CONFIG_INPUTS are not reached from it); say so in the
entry if one is written.

Reverse: restore the two functions and drop the entry; E5's INT-001 then reads the set verdict and UNBOUND again.

Usage: patch_rules_status.py <tree root holding v2/ecad>"""
import os, sys

p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "rules_status.py")
s = open(p, encoding="utf-8").read(); o = s


def swap(old, new):
    global s
    if s.count(old) != 1: raise SystemExit("patch_rules_status: expected exactly one of %r, found %d" % (old[:70], s.count(old)))
    s = s.replace(old, new)


# 1a. result_for asks _names
swap('''    raw = (c.get("verification") or {}).get("verdict")
    if not raw:
        return dict(result=INCONCLUSIVE, why="the coverage map names no verdict for an enforced rule", evidence=None)
''', '''    names = _names(c, letter)
    if not names:
        return dict(result=INCONCLUSIVE, why="the coverage map names no verdict for an enforced rule", evidence=None)
''')
swap('''    names = [n.strip().replace("<letter>", letter) for n in str(raw).split(",") if n.strip()]
''', '''    # `names` above: _names, which reads a board's own readings where the row names them (verdict_by_board).
''')
# 1b. _names reads verdict_by_board
swap('''def _names(c, letter):
    raw = (c.get("verification") or {}).get("verdict")
    return [n.strip().replace("<letter>", letter) for n in str(raw or "").split(",") if n.strip()]
''', '''def _names(c, letter):
    """The verdict names a coverage row reads on one board, `<letter>` expanded.

    A ROW MAY NAME, FOR ONE BOARD, THE READINGS THAT DECIDE IT THERE (27 September 2026, MESHSAT-1357, stream w4r):
    `verification.verdict_by_board: {<letter>: "<names>"}`. Board E5 has no netlist, so the set verdict check_contracts,
    which judges the contracts between the six boards that have one, reads nothing of it and can never be bound to E5's
    design; E5's INT-001 is decided by its own contract reading, check_contracts_e5 (block_contract.py). Every reader of
    the map asks here (result_for, evidence_class, retake_projection, retake_schematic_phase.py), so a rule on a board is
    never decided from one list of readings and bound from another. A row without the field reads `verdict` as before."""
    v = c.get("verification") or {}
    per = v.get("verdict_by_board")
    raw = per[letter] if isinstance(per, dict) and letter in per else v.get("verdict")
    return [n.strip().replace("<letter>", letter) for n in str(raw or "").split(",") if n.strip()]
''')
# 2. CONFIG_INPUTS["block_contract.py"]
swap('''    "ground_system.py": ("tools/boards/{letter}.json",),
}
''', '''    "ground_system.py": ("tools/boards/{letter}.json",),
    # block_contract.py (27 September 2026, MESHSAT-1357 stream w4r; functions of that stream's file): board E5's
    # contract reading check_contracts_e5, which decides SCH-003 and, on E5, INT-001. `judge` reads E5's board file and
    # board A's declared phase netlist (`a_netlist_for`, phase_artefacts.netlist, which finds it through the manifest and
    # the routeflow profile: finding an artefact, not configuration), both recorded by sha by `inputs_for`, the netlist by
    # content16 too; `land_file` and `dock_offsets` read the land that netlist names for J_DOCK, recorded by sha as
    # dock_land (a meshsat land; a land of the host's KiCad library would not be in this tree, an instrument limit, as for
    # pin_map_lands). The glob is conservative. DOCK_MOUNT and POWER_KINDS are code in the tool; `decides` reads the
    # coverage map to name the rules the reading answers, as verdict.py does for every writer, which says which rules a
    # reading decides and not what it measures.
    "block_contract.py": ("meshsat.pretty/*.kicad_mod",),
}
''')
assert s != o
compile(s, p, "exec")
open(p, "w", encoding="utf-8").write(s)
print("patch_rules_status: %s edited (_names reads verdict_by_board, result_for asks _names, block_contract.py declared)" % p)
