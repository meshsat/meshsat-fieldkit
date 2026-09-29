#!/usr/bin/env python3
"""SI-001's routed half (edge_length.routed_main, verdict edge_length_routed) on C24's routed lengths, without KiCad (stream
csi, 29 September 2026, for the independent check's B1). The runner has no pcbnew, so the board is a stub that carries,
per net, one straight track of the length tools/board_c_layout.py measures on the board file; the classes are the board
table's own (signal_class.declarations), the stack the tool's own. What it shows is the routed half's decision on these
lengths, not a routed reading of C24 (a box run of edge_length.py on the board file is that).
Usage: routed_c24.py <board.kicad_pcb> <scratch dir>      prints the verdict, counts and evidence"""
import fnmatch, json, os, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "ecad", "tools"))
sys.path.insert(0, HERE); sys.path.insert(0, TOOLS)
import board_c_layout as BL
import signal_class as SC


def main(board_path, scratch):
    L, _V, _Ly, _pads = BL.board(open(board_path, encoding="utf-8").read())
    allow = json.load(open(os.path.join(TOOLS, "boards", "c.json"), encoding="utf-8"))["edge_allow"]
    decls = SC.declarations("c")[0]
    nets = []
    for n, mm in sorted(L.items()):
        nm = (n or "").lstrip("/")
        if not any(fnmatch.fnmatch(nm, e["pattern"]) for e in allow): continue
        cls = next((c for p, c, _b in decls if fnmatch.fnmatchcase(nm, p)), "UNKNOWN")
        nets.append((nm, mm, cls))
    class P_:
        def __init__(s, x, y): s.x, s.y = x, y
    class Tr:
        def __init__(s, net, mm): s.net, s.mm = net, mm
        def GetClass(s): return "PCB_TRACK"
        def GetNetname(s): return s.net
        def GetStart(s): return P_(0, 0)
        def GetEnd(s): return P_(int(s.mm * 1e6), 0)
        def GetLayer(s): return 0
    class Board:
        def GetTracks(s): return [Tr("/" + n, mm) for n, mm, _c in nets]
        def GetFootprints(s): return []
    m = types.ModuleType("pcbnew"); m.LoadBoard = lambda p: Board(); m.F_Cu, m.B_Cu = 0, 2; sys.modules["pcbnew"] = m
    m = types.ModuleType("intent"); m.load = lambda p: {}; sys.modules["intent"] = m
    m = types.ModuleType("signalnets"); m.classify = lambda b, p, r: (set(), None); m.is_signal = lambda n, s: True; sys.modules["signalnets"] = m
    m = types.ModuleType("impedance_check"); m.read_stackup = lambda p: [("core1", "core", 0.2, 4.3)]; sys.modules["impedance_check"] = m
    m = types.ModuleType("signal_class"); m.classify = lambda b, p, t, x: ({"/" + n: (c, "table") for n, _mm, c in nets},); sys.modules["signal_class"] = m
    import edge_length as E
    d = os.path.join(scratch, "c24-stub"); os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "pcb-c-display.kicad_pcb"); open(path, "w").write("(kicad_pcb)\n")
    E.routed_main([path])
    v = json.load(open(os.path.join(d, "out", "edge_length_routed.verdict.json")))
    print("RESULT", v["verdict"], json.dumps(v["counts"], sort_keys=True))
    for e in v["evidence"]: print("  " + e)


if __name__ == "__main__":
    if len(sys.argv) != 3: print(__doc__); sys.exit(2)
    main(sys.argv[1], sys.argv[2])
