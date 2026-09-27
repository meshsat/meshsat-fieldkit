"""Read-only survey: every exposed pad on a board, and whether anything carries its heat to the planes.

A modern power part's thermal pad is its heat path. escape.py lays thermal vias only inside a FINE-PITCH
footprint, so a PowerPAD SOIC, a DDA8 or any coarse part with an exposed pad is never asked. This counts them.
Usage: thermal_pads.py <board.kicad_pcb>
"""
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
rows = []
for fp in b.GetFootprints():
    pads = [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and p.IsOnCopperLayer()]
    if not pads: continue
    # the exposed pad: an SMD pad whose area is at least four times the median of its siblings and over 1.5 mm2
    areas = sorted(pcbnew.ToMM(p.GetSize().x) * pcbnew.ToMM(p.GetSize().y) for p in pads)
    if len(areas) < 3: continue
    med = areas[len(areas) // 2]
    for p in pads:
        a = pcbnew.ToMM(p.GetSize().x) * pcbnew.ToMM(p.GetSize().y)
        if a < 1.5 or a < 4 * med: continue
        c = p.GetCenter(); hx, hy = p.GetSize().x / 2.0, p.GetSize().y / 2.0
        inside = sum(1 for v in vias if abs(v.GetPosition().x - c.x) <= hx and abs(v.GetPosition().y - c.y) <= hy
                     and v.GetNetname() == p.GetNetname())
        near = min([math.hypot(v.GetPosition().x - c.x, v.GetPosition().y - c.y) / 1e6
                    for v in vias if v.GetNetname() == p.GetNetname()] or [-1])
        rows.append((fp.GetReference(), p.GetNumber(), p.GetNetname().lstrip("/"), a, inside, near,
                     str(fp.GetFPID().GetLibItemName())))
rows.sort(key=lambda r: (r[4], -r[3]))
print("%-6s %-4s %-10s %7s %6s %9s  %s" % ("ref", "pad", "net", "mm2", "in-pad", "nearest", "footprint"))
for r in rows:
    print("%-6s %-4s %-10s %7.2f %6d %9s  %s" % (r[0], r[1], r[2], r[3], r[4],
          ("%.2f" % r[5]) if r[5] >= 0 else "none", r[6][:44]))
print("exposed pads: %d, of which %d have no via of their own net inside them" % (len(rows), sum(1 for r in rows if r[4] == 0)))
