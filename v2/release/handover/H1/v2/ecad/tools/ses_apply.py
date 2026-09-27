#!/usr/bin/env python3
"""Import a session into a board the way route_one.sh does, and say so (20 September 2026).

It is NOT `ses_import_lock.py`, which is the PARTITION importer and wants a part.json and a group list: the
first snapshot read passed it two arguments of five, it raised, NOTHING was imported, and the board that was
then read was the PLACED one at KiCad's 499 unconnected cap, which looks exactly like a result. A cap is
never a denominator.

Usage: ses_apply.py <board.kicad_pcb> <session.ses>
"""
import os, sys
import pcbnew

def main(a):
    board, ses = a[0], a[1]
    b = pcbnew.LoadBoard(board)
    ok = os.path.exists(ses) and pcbnew.ImportSpecctraSES(b, ses)
    print("SES import:", ok)
    if not ok:
        return 4
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import ses_via_drill
    ses_via_drill.restore_board(b, ses)      # the importer leaves every via's drill UNDEFINED
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(board, b)
    print("tracks:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]),
          "vias:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
