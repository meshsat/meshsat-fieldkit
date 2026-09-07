#!/usr/bin/env python3
"""ses_merge.py <master.kicad_pcb> <part.json> <out.kicad_pcb> <group>=<session.ses> [...]
Merge the sessions of the partition jobs by net: each session is imported into its own copy of the master (a KiCad session import replaces the
unlocked tracks), then the tracks and vias of that group's nets are copied into the master, which keeps its own (locked) tracks. Prints counts;
the caller runs DRC on the result and reconciles the boundary conflicts."""
import sys, json, os, tempfile, pcbnew
master, pj, out = sys.argv[1:4]
part = json.load(open(pj))
m = pcbnew.LoadBoard(master)
have = set(); base = len(m.Tracks())
for a in sys.argv[4:]:
    g, ses = a.split("=", 1); nets = set(part["groups"].get(g, []))
    c = pcbnew.LoadBoard(master)
    ok = pcbnew.ImportSpecctraSES(c, ses); n = 0
    for t in c.Tracks():
        if t.IsLocked() or t.GetNetname() not in nets: continue
        d = t.Duplicate(); d.SetLocked(False); m.Add(d); n += 1
    print("ses_merge: %s import %s, %d tracks and vias copied" % (g, ok, n)); have |= nets
pcbnew.ZONE_FILLER(m).Fill(m.Zones())
pcbnew.SaveBoard(out, m)
print("ses_merge: master had %d, now %d items; nets merged %d" % (base, len(m.Tracks()), len(have)))
