#!/usr/bin/env python3
"""After a Specctra session import, every via's drill is what the session's padstack says (18 September 2026).

`pcbnew.ImportSpecctraSES` re-creates the board's vias from the session and leaves their drill UNDEFINED, which
KiCad then resolves to the NET CLASS's via drill. A via the pre-router laid at the board's small size (E12:
prefanout's 0.6/0.3 on CELL_F, whose class BANK carries a 1.2/0.6 via) came back as 0.6 mm wide with a 0.6 mm
drill, a ring of nothing, and the routed board carried ten annular_width violations that no tool of ours had laid:
E12 was refused at its routed-board gate for them and would have been a route campaign of remedies about a fact
of the importer. The session names every via's padstack ("Via[0-3]_600:300_um": 600 um wide, 300 um drill) at
its position, so the drill is not lost, only unread. This reads it back and sets it on the via at that position;
a via the session does not name (a locked one KiCad kept as it was) is left alone.

Usage: ses_via_drill.py <board.kicad_pcb> <route.ses>   -> prints how many drills were restored; exit 0."""
import sys, os, re


def session_vias(ses_path):
    """{(x_mm, y_mm): (width_mm, drill_mm)} from the session's via lines, in the session's own resolution."""
    s = open(ses_path, encoding="utf-8", errors="replace").read()
    m = re.search(r"\(resolution\s+(\w+)\s+(\d+)\)", s)
    unit, per = (m.group(1), int(m.group(2))) if m else ("um", 10)
    scale = {"um": 1e-3, "mm": 1.0, "mil": 0.0254, "inch": 25.4}.get(unit, 1e-3) / per
    out = {}
    for v in re.finditer(r'\(via\s+"?Via\[[^\]]*\]_(\d+):(\d+)(?:_um)?"?\s+(-?\d+)\s+(-?\d+)', s):
        w, d = int(v.group(1)) / 1000.0, int(v.group(2)) / 1000.0        # the name carries um
        x, y = int(v.group(3)) * scale, -int(v.group(4)) * scale         # session y points up, the board's points down
        out[(round(x, 3), round(y, 3))] = (w, d)
    return out


def restore_board(b, ses_path, tol_mm=0.01):
    """Set every via's drill on a LOADED board from the session; returns (vias, named, fixed). The caller saves."""
    want = session_vias(ses_path); fixed = 0; seen = 0; unnamed = 0
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA": continue
        seen += 1
        x, y = round(t.GetPosition().x / 1e6, 3), round(t.GetPosition().y / 1e6, 3)
        hit = want.get((x, y))
        if hit is None:
            hit = next((v for (px, py), v in want.items() if abs(px - x) <= tol_mm and abs(py - y) <= tol_mm), None)
        if hit is None: unnamed += 1; continue
        w, d = hit
        if t.GetDrill() < 0 or abs(t.GetDrillValue() / 1e6 - d) > 1e-4:
            t.SetDrill(int(round(d * 1e6))); fixed += 1
    print("ses_via_drill: %d via(s) on the board, %d named by the session, %d drill(s) restored from the session's padstack names"
          % (seen, seen - unnamed, fixed))
    return seen, seen - unnamed, fixed


def restore(board_path, ses_path, tol_mm=0.01):
    import pcbnew
    b = pcbnew.LoadBoard(board_path); _, _, fixed = restore_board(b, ses_path, tol_mm)
    if fixed: pcbnew.SaveBoard(board_path, b)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    sys.exit(restore(sys.argv[1], sys.argv[2]))
