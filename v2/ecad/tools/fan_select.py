#!/usr/bin/env python3
"""Which parts the escape pass escapes and which get an escape fan: ONE selection (decision 42, T1; MESHSAT-1357).

Until 27 September 2026 three files each decided this for themselves. `escape.py` escaped every part whose land
name holds SOT-23-6 or SOT-23-8 or whose closest two SMD pads are 0.7 mm apart or less; `bypass_slots._needs_fan`
fanned every part of eight or more SMD pads 1.0 mm apart or less; `bypass_place.py` borrowed the second. So a
SOT-23-6 was escaped and had no fan, and a SOIC-8-1EP at 1.27 mm had a fan because KiCad draws its four paste
apertures as pads (DECOUPLING.md 3.2(a), 3.2(g)). The decisions are `decoupling_rules.escaped`, `copper_fanned`
and `fanned`, which take coordinates; this file is the only place that turns a KiCad footprint into them.

`escape.py` loads a board and lays copper when it is imported, so nothing can import IT; it imports this.

    fan_select.is_escaped(fp, skip)      what escape.py escapes (its old `is_fine` and two exemptions, unchanged)
    fan_select.is_fanned(fp, skip)       the fan set T1 rules: escaped, or eight copper pads at 1.0 mm or less
    fan_select.escape_skip(board_path)   the board's ESCAPE_SKIP: the caller's environment, else the board table
    fan_select.fan_boxes(board, skip)    [(reference, box in mm)] for every fanned part of a board"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoupling_rules as _dr

BOARDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boards")


def _pcbnew():
    import pcbnew
    return pcbnew


def smd_points(fp):
    """Every pad of attribute SMD, as escape.py has always counted them: a paste aperture is one of them."""
    pcbnew = _pcbnew()
    return [(p.GetPosition().x, p.GetPosition().y) for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]


def copper_points(fp):
    """The NUMBERED SMD pads that carry copper: a pin, not an aperture."""
    pcbnew = _pcbnew()
    out = []
    for p in fp.Pads():
        if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or not str(p.GetNumber()).strip(): continue
        if not any(pcbnew.IsCopperLayer(L) for L in p.GetLayerSet().Seq()): continue
        out.append((p.GetPosition().x, p.GetPosition().y))
    return out


def min_pitch(fp):
    """escape.py's `min_pitch`: the closest two SMD pads, in KiCad's units."""
    return _dr.min_pitch_nm(smd_points(fp))


def is_fine(fp):
    return _dr.is_fine(fp.GetFPIDAsString(), smd_points(fp))


def is_escaped(fp, skip=()):
    return _dr.escaped(fp.GetReference(), fp.GetFPIDAsString(), smd_points(fp), skip)


def is_fanned(fp, skip=()):
    return _dr.fanned(fp.GetReference(), fp.GetFPIDAsString(), smd_points(fp), copper_points(fp), skip)[0]


def _split(text):
    return set(filter(None, str(text or "").split(",")))


def escape_skip(board_path=None, environ=None):
    """The references the escape pass leaves to the router on this board.

    The caller's own ESCAPE_SKIP wins, which is how `full.sh` hands it to escape.py and how an arm varies it. A
    placer is not run under that environment, so without one the board table is read: the table whose `name` is
    the board file's own name, its `escape_env`. A board with no table has no skip list, and that is said."""
    env = os.environ if environ is None else environ
    if env.get("ESCAPE_SKIP") is not None: return _split(env.get("ESCAPE_SKIP"))
    stem = os.path.splitext(os.path.basename(str(board_path or "")))[0]
    if not stem: return set()
    try: names = sorted(os.listdir(BOARDS))
    except OSError: return set()
    for n in names:
        if not n.endswith(".json"): continue
        try: d = json.load(open(os.path.join(BOARDS, n), encoding="utf-8"))
        except (OSError, ValueError): continue
        if d.get("name") == stem:
            return _split((d.get("escape_env") or {}).get("ESCAPE_SKIP"))
    return set()


def courtyard_box(fp):
    """A footprint's courtyard on its own side as (x0, y0, x1, y1) in mm, or its bounding box when it draws none."""
    pcbnew = _pcbnew()
    bb = None
    try:
        c = fp.GetCourtyard(pcbnew.F_CrtYd if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd); b = c.BBox()
        if b.GetWidth() > 0: bb = b
    except Exception: bb = None
    if bb is None: bb = fp.GetBoundingBox(False, False)
    return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def fan_boxes(board, skip=(), fan=_dr.FAN_MM):
    """[(reference, (x0, y0, x1, y1) in mm)]: the courtyard of every fanned part grown by the fan, whichever side
    the part is on, because an escape via comes through the board."""
    out = []
    for fp in board.GetFootprints():
        if is_fanned(fp, skip):
            x0, y0, x1, y1 = courtyard_box(fp)
            out.append((fp.GetReference(), (x0 - fan, y0 - fan, x1 + fan, y1 + fan)))
    return out


def tht_boxes(board):
    """[(reference, courtyard box in mm)] of every part that carries a plated hole."""
    pcbnew = _pcbnew(); out = []
    for fp in board.GetFootprints():
        if any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in fp.Pads()):
            out.append((fp.GetReference(), courtyard_box(fp)))
    return out


def smd_sides(board):
    """(SMD footprints on the front, on the back): a footprint is SMD when it carries a copper SMD pad and no
    plated hole (DECOUPLING.md 3.3)."""
    pcbnew = _pcbnew(); f = b = 0
    for fp in board.GetFootprints():
        pads = list(fp.Pads())
        if any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in pads): continue
        if not any(p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and any(pcbnew.IsCopperLayer(L) for L in p.GetLayerSet().Seq())
                   for p in pads): continue
        if fp.GetLayer() == pcbnew.F_Cu: f += 1
        else: b += 1
    return f, b
