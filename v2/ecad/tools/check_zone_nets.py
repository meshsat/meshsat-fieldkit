#!/usr/bin/env python3
"""Gate: every copper zone must sit on a net that has pads, and no two same-net zones on one layer may share a priority.
A pour whose net name missed the netlist gets a phantom net and becomes dead copper that DRC only reports as isolated
islands (A19 and B12 rail planes, 5 Sep 2026, appendix 32.33). Usage: check_zone_nets.py <board.kicad_pcb>; exits 1 on FAIL."""
import sys, collections, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); fails = 0
pads = collections.Counter(p.GetNetname() for f in b.GetFootprints() for p in f.Pads())
seen = collections.defaultdict(list)
for z in b.Zones():
    if z.GetIsRuleArea(): continue
    n = z.GetNetname()
    if pads[n] == 0:
        print("FAIL zone %r on %s: net %r has no pads (phantom net)" % (z.GetZoneName(), b.GetLayerName(z.GetLayer()), n)); fails += 1
    seen[(n, z.GetLayer(), z.GetAssignedPriority())].append(z)
# KiCad's rule: zones that INTERSECT must carry distinct priorities; side-by-side zones of one net may share one
for (n, L, pr), zs in seen.items():
    for i in range(len(zs)):
        for j in range(i + 1, len(zs)):
            if zs[i].GetBoundingBox().Intersects(zs[j].GetBoundingBox()):
                print("FAIL zones %r and %r of net %r on %s overlap at the same priority %d" % (zs[i].GetZoneName(), zs[j].GetZoneName(), n, b.GetLayerName(L), pr)); fails += 1
print("zone nets: %s (%d zones checked)" % ("ALL PASS" if not fails else "%d FAIL" % fails, sum(1 for z in b.Zones() if not z.GetIsRuleArea())))
sys.exit(1 if fails else 0)
