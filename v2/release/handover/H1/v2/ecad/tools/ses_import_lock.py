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
import ses_via_drill; ses_via_drill.restore_board(b, ses)   # drills from the session's padstack names (18 September 2026)
# TWO SHORT LISTS OFF THE LIVE CONTAINER, NEVER `list(b.Tracks())` HELD ACROSS A REMOVE (18 September 2026, A46): with
# every track's proxy alive in one list while the other groups' tracks were removed, KiCad 9's SWIG handed back a bare
# SwigPyObject for b.Tracks() afterwards and the fill segfaulted in Zones(); the same removal from a list that holds only
# the items being removed leaves the board whole (measured three ways on board A's GLOBAL import). B22's GLOBAL session
# carried no other group's tracks, so its import removed nothing and never met this.
to_lock = [t for t in b.Tracks() if not t.IsLocked() and t.GetNetname() in nets]
to_remove = [t for t in b.Tracks() if not t.IsLocked() and t.GetNetname() not in nets]
for t in to_lock: t.SetLocked(True)
for t in to_remove: b.Remove(t)
locked, removed = len(to_lock), len(to_remove)
# THE FILL RUNS ON A SAVED-THEN-LOADED COPY, NEVER ON THE BOARD ITEMS WERE JUST REMOVED FROM (18 September 2026, A46):
# ZONE_FILLER segfaulted inside Zones() on board A's GLOBAL import after `b.Remove(t)` had taken the other groups'
# tracks off (B22's GLOBAL session carried none, so it never showed there); the whole partition then ran on a board
# that did not exist and reported 999999. Save, load, fill, save: the 17 September fixture lesson, applied here.
pcbnew.SaveBoard(out, b)
b = pcbnew.LoadBoard(out); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(out, b)
print("ses_import_lock: import %s, tracks before %d, locked %d of groups %s, removed %d others, after %d" % (ok, before, locked, sorted(groups), removed, len(b.Tracks())))
