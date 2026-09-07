#!/usr/bin/env python3
"""ses_import_lock.py <board.kicad_pcb> <session.ses> <part.json> <group[,group...]> <out.kicad_pcb>
Import a Freerouting session into a copy of the board and lock every track and via whose net belongs to the given groups (the next partition jobs
then see them as fixed wires); the other groups' unlocked tracks and vias that the session may carry are removed. Prints the counts."""
import sys, json, pcbnew
board, ses, pj, groups, out = sys.argv[1:6]
groups = set(groups.split(","))
part = json.load(open(pj))
nets = set(n for g in groups for n in part["groups"].get(g, []))
b = pcbnew.LoadBoard(board)
before = len(b.Tracks())
ok = pcbnew.ImportSpecctraSES(b, ses)
locked = 0; removed = 0
for t in list(b.Tracks()):
    if t.IsLocked(): continue
    if t.GetNetname() in nets: t.SetLocked(True); locked += 1
    else: b.Remove(t); removed += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(out, b)
print("ses_import_lock: import %s, tracks before %d, locked %d of groups %s, removed %d others, after %d" % (ok, before, locked, sorted(groups), removed, len(b.Tracks())))
