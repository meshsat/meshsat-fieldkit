#!/usr/bin/env python3
"""besc1_rows.py <trial dir> <out.json>: read-only, EXPERIMENTAL (Q-B-ESC-1).

Which pads each row of the switch U301 and the hub U302 carries on the trial's INPUT board (A6's
pcb-b-compute.kicad_pcb: placement plus the escape pass, before any routing). A pad's row is the side of the package
it sits on in board coordinates (north = smaller y), from the pad centre against the footprint's position: the larger
of |dx| and |dy| names the axis, and pads within 0.5 mm of the centre on both axes are the exposed pad. For every pad:
number, pin function (empty on this board, whose pads carry none; the page takes pin names from B21's netlist), net, whether it is connected (a net other than none or "unconnected-..."), and whether it
carries an escape on the input board, read two ways: (a) KiCad's connectivity, any track or via joined to the pad (the
reading of besc1_residue.py), and (b) place_audit.py's reading, a locked piece of the pad's net with an end inside the
pad's bounding box grown by 0.05 mm. Writes nothing on the board."""
import sys, json, math
sys.path.insert(0, "/root/besc1/v2/ecad/tools")
import pcbnew

T, OUT = sys.argv[1:3]
b = pcbnew.LoadBoard("%s/a6/pcb-b-compute.kicad_pcb" % T)
b.BuildConnectivity(); conn = b.GetConnectivity()
locked = [t for t in b.GetTracks() if t.IsLocked()]


def pts(t):
    return [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]


res = {"label": "EXPERIMENTAL (Q-B-ESC-1) package rows on the input board", "board": "a6/pcb-b-compute.kicad_pcb", "parts": {}}
for ref in ("U301", "U302"):
    fp = b.FindFootprintByReference(ref)
    c = fp.GetPosition()
    rows = {"north": [], "east": [], "south": [], "west": [], "centre": []}
    for p in fp.Pads():
        q = p.GetPosition(); dx = (q.x - c.x) / 1e6; dy = (q.y - c.y) / 1e6
        if abs(dx) < 0.5 and abs(dy) < 0.5:
            side = "centre"
        elif abs(dy) >= abs(dx):
            side = "north" if dy < 0 else "south"
        else:
            side = "east" if dx > 0 else "west"
        net = p.GetNetname()
        connected = bool(net) and not net.startswith("unconnected-")
        esc_conn = len(list(conn.GetConnectedTracks(p))) > 0
        pb = p.GetBoundingBox(); pb.Inflate(int(0.05e6))
        esc_audit = any(t.GetNetname() == net and any(pb.Contains(v) for v in pts(t)) for t in locked) if connected else False
        bb = p.GetBoundingBox()
        rows[side].append({"pad": p.GetNumber(), "function": p.GetPinFunction(), "net": net, "connected": connected,
                           "escape_connectivity": esc_conn, "escape_place_audit": esc_audit,
                           "at": [round(q.x / 1e6, 3), round(q.y / 1e6, 3)],
                           "tip": {"north": round(bb.GetTop() / 1e6, 3), "south": round(bb.GetBottom() / 1e6, 3),
                                   "west": round(bb.GetLeft() / 1e6, 3), "east": round(bb.GetRight() / 1e6, 3)}.get(side)})
    for side in rows:
        rows[side].sort(key=lambda r: int(r["pad"]) if r["pad"].isdigit() else 0)
    res["parts"][ref] = {"at": [round(c.x / 1e6, 3), round(c.y / 1e6, 3)], "orientation_deg": fp.GetOrientationDegrees(),
                         "rows": rows}
    for side, rr in rows.items():
        con = [r for r in rr if r["connected"]]
        print("%s %-6s pads %3d connected %3d no-escape(conn) %3d no-escape(audit) %3d  pins %s" % (
            ref, side, len(rr), len(con), sum(1 for r in con if not r["escape_connectivity"]),
            sum(1 for r in con if not r["escape_place_audit"]),
            (rr[0]["pad"] + ".." + rr[-1]["pad"]) if rr else "-"))
json.dump(res, open(OUT, "w"), indent=1)
