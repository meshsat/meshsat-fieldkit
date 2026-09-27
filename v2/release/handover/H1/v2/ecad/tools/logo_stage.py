#!/usr/bin/env python3
"""Put the MeshSat mark on a board that declares where it goes (MESHSAT-862, 16 September 2026).

The owner's ruling is that the mark is traced from the approved sticker master and never redrawn;
`logo_silk.py` has drawn it since the trace and NO BOARD OF THE SEVEN carried a silkscreen polygon, because
nothing ever chose where it goes and nothing ever called the tool. That is the third "written and never run"
of the day and the reason `closer_audit` now refuses one.

The position is DECLARED, never found at generation time: `logo` in `boards/<letter>.json` with the centre in
the generator's own case coordinates, the width, and the layer. `silk_space.py` reports the free rectangles a
board has, and a person chooses from them, because a position that moves whenever a part moves would rewrite
the board file on every generation and the diff would stop meaning anything.

Usage: logo_stage.py <board.kicad_pcb> <letter> [--ox 150] [--oy 110]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import boardtable as _bt


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    import pcbnew
    from pcbnew import VECTOR2I, FromMM
    import logo_silk
    path, letter = argv[0], argv[1]
    d = _bt.value(letter, "logo") or {}
    if not d:
        print("logo_stage: board %s declares no logo position (boards/%s.json `logo`); nothing drawn"
              % (letter.upper(), letter.lower()))
        return 0
    ox = float(argv[argv.index("--ox") + 1]) if "--ox" in argv else float(d.get("ox", 150.0))
    oy = float(argv[argv.index("--oy") + 1]) if "--oy" in argv else float(d.get("oy", 110.0))
    b = pcbnew.LoadBoard(path)
    lay = getattr(pcbnew, d.get("layer", "F_SilkS").replace(".", "_"), pcbnew.F_SilkS)
    # the same mapping the placement generators use: case x to the right, case y up
    def P(x, y): return VECTOR2I(FromMM(ox + x), FromMM(oy - y))
    # A SECOND RUN MUST NOT DRAW IT TWICE. The chain regenerates the board from the outline every time, so this
    # is belt and braces rather than the usual case, and it costs one pass over the drawings.
    before = [s for s in b.GetDrawings() if s.GetClass() == "PCB_SHAPE" and s.GetShape() == pcbnew.SHAPE_T_POLY
              and s.GetLayer() == lay]
    if len(before) > 4:
        print("logo_stage: %d filled polygon(s) already on %s; not drawing a second mark"
              % (len(before), d.get("layer", "F.SilkS")))
        return 0
    n, h = logo_silk.add_logo(b, P, float(d["cx"]), float(d["cy"]), float(d["width_mm"]), lay,
                              mirror=bool(d.get("mirror")))
    pcbnew.SaveBoard(path, b)
    print("logo_stage: %d polygon(s), %.1f mm wide and %.1f high at case (%.1f, %.1f) on %s [%s]"
          % (n, float(d["width_mm"]), h, float(d["cx"]), float(d["cy"]), d.get("layer", "F.SilkS"),
             str(d.get("why", ""))[:70]))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
