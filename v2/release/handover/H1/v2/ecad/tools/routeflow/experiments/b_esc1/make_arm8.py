#!/usr/bin/env python3
"""make_arm8.py: build the EXPERIMENTAL eight-layer arm of the board B escape trial Q-B-ESC-1 and prove that layer
count is the only thing that changed (v2/docs/B-FEASIBILITY.md section 7).

Usage: make_arm8.py <a6 board.kicad_pcb> <a8 board.kicad_pcb> <report.json>   -> exit 0 when the arms agree, 1 when not

The a8 board is the a6 board with `SetCopperLayerCount(8)`, saved in the trial tree only. KiCad 9 keeps every item on
its own layer id (F.Cu 0, B.Cu 2, In1.Cu 4 ... In4.Cu 10) and enables In5.Cu (12) and In6.Cu (14), which start empty.
No generator, no STACKS row and no reserved line is touched; the arm is a routing-capacity probe and its impedance is
not judged.

The proof, read back from the SAVED a8 file (never from the object that was edited):
  * copper layer count 8, with the enabled copper layers named;
  * for every copper layer of a6: the same number of tracks, vias, pads (by layer set) and zones, and the same
    zone nets, on a8;
  * In5.Cu and In6.Cu carry no track and no zone;
  * the same footprints, pads and nets.
Any difference is printed and the exit is 1: the trial must stop (its variable would not be layers alone)."""
import sys, json, collections, hashlib
import pcbnew


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def census(path):
    b = pcbnew.LoadBoard(path)
    cu = [b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()]
    tracks = collections.Counter(); vias = 0
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            vias += 1
        else:
            tracks[b.GetLayerName(t.GetLayer())] += 1
    zones = collections.Counter(); zone_nets = collections.defaultdict(set)
    for z in b.Zones():
        for l in z.GetLayerSet().CuStack():
            name = b.GetLayerName(l)
            zones[name] += 1
            zone_nets[name].add(z.GetNetname())
    pads = collections.Counter()
    nets = set()
    for p in b.GetPads():
        nets.add(p.GetNetname())
        for l in p.GetLayerSet().CuStack():
            pads[b.GetLayerName(l)] += 1
    return {
        "copper_layers": b.GetCopperLayerCount(), "enabled_copper": cu, "tracks": dict(tracks), "vias": vias,
        "zones": dict(zones), "zone_nets": {k: sorted(v) for k, v in zone_nets.items()},
        "pads_by_layer": dict(pads), "footprints": len(b.GetFootprints()), "nets": len(nets),
    }


def main(a):
    if len(a) < 3:
        print(__doc__)
        return 2
    a6, a8, rep = a[0], a[1], a[2]
    b = pcbnew.LoadBoard(a6)
    if b.GetCopperLayerCount() != 6:
        print("make_arm8: the a6 board has %d copper layers, not 6" % b.GetCopperLayerCount())
        return 1
    b.SetCopperLayerCount(8)
    pcbnew.SaveBoard(a8, b)
    c6, c8 = census(a6), census(a8)
    diffs = []
    if c8["copper_layers"] != 8:
        diffs.append("a8 reads %d copper layers" % c8["copper_layers"])
    for key in ("tracks", "zones", "zone_nets"):
        for lay, v in c6[key].items():
            if c8[key].get(lay) != v:
                diffs.append("%s on %s: a6 %s, a8 %s" % (key, lay, v, c8[key].get(lay)))
    for lay in ("In5.Cu", "In6.Cu"):
        if c8["tracks"].get(lay) or c8["zones"].get(lay):
            diffs.append("%s is not empty on a8" % lay)
    for key in ("vias", "footprints", "nets"):
        if c6[key] != c8[key]:
            diffs.append("%s: a6 %s, a8 %s" % (key, c6[key], c8[key]))
    # a through-hole pad and a through via reach the added layers by definition; every other pad count must hold
    for lay, v in c6["pads_by_layer"].items():
        if c8["pads_by_layer"].get(lay) != v:
            diffs.append("pads on %s: a6 %s, a8 %s" % (lay, v, c8["pads_by_layer"].get(lay)))
    out = {"label": "EXPERIMENTAL (Q-B-ESC-1)", "a6": a6, "a6_sha256": sha256(a6), "a8": a8, "a8_sha256": sha256(a8),
           "a6_census": c6, "a8_census": c8, "differences": diffs, "agree": not diffs}
    json.dump(out, open(rep, "w"), indent=1)
    print("make_arm8: a8 enabled copper %s; %s" % (" ".join(c8["enabled_copper"]),
                                                   "arms agree" if not diffs else "ARMS DIFFER: " + "; ".join(diffs[:8])))
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
