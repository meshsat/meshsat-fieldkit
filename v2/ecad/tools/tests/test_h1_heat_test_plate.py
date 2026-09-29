"""H1, the heat-test face plate blank (MESHSAT-1357, stream od01b, 29 Sep 2026): its own definition, read from C1's source.

The owner's instruction of 29 September 2026 (R6) asked for H1 as a distinct manufacturing definition generated from the same
source geometry as C1, not typed. These rules hold that on properties, not on today's numbers:
  * every feature H1 shares with C1 is panel1450's value (outline, rebate, relief, the ten screw holes at Peli's inserts);
  * the patch fixing is the HS100's pattern with G along the plate's X and F along its Y, centred on panel1450.PA_MOUNT;
  * the nuts sit in the full-thickness face and the resistor's footprint inside the 1450PF window;
  * neither H1 script types a design number panel1450 holds (case_geometry_check.literal_inputs, which parses);
  * the released folder still carries the digests its own MANIFEST names.
Plain Python: no ezdxf or build123d needed (features() is pure data)."""
import os, sys, math, copy, ast

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
V2 = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, os.path.join(V2, "cad"))
from harness import need


def _feats(P, layer):
    return [p for lay, kind, p in P.features() if lay == layer]


def t_h1_shares_c1s_source_features():
    import panel1450 as L, h1_heat_test_plate as P
    (outline,) = _feats(P, "OUTLINE")
    xs = [q[0] for q in outline]; ys = [q[1] for q in outline]
    assert abs(max(xs) - min(xs) - L.PLATE[0]) < 1e-6 and abs(max(ys) - min(ys) - L.PLATE[1]) < 1e-6, (max(xs) - min(xs), max(ys) - min(ys))
    (reb,) = _feats(P, "REBATE_2MM_TOP")
    assert abs(max(q[0] for q in reb) * 2 - L.REB_IN[0]) < 1e-6 and abs(max(q[1] for q in reb) * 2 - L.REB_IN[1]) < 1e-6
    (rel,) = _feats(P, "RELIEF_0.8MM_UNDERSIDE")
    rx0, ry0, rx1, ry1, _ = L.RELIEF_POCKET
    assert sorted(rel) == sorted([(rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1)]), rel
    screws = sorted(_feats(P, "THROUGH"))
    assert screws == sorted((x, y, L.FACE_HOLE) for x, y in L.FRAME_BOSSES), screws


def t_h1_patch_fixing_is_the_hs100_pattern_g_along_x():
    import panel1450 as L, h1_heat_test_plate as P
    pem = _feats(P, "PEM_S_M3")
    assert len(pem) == 4, pem
    xs = sorted(set(round(p[0], 6) for p in pem)); ys = sorted(set(round(p[1], 6) for p in pem))
    assert len(xs) == 2 and len(ys) == 2, (xs, ys)
    assert abs((xs[1] - xs[0]) - P.HS100["G"]) < 1e-6 and abs((ys[1] - ys[0]) - P.HS100["F"]) < 1e-6, (xs, ys)
    cx, cy = L.PA_MOUNT["c"]
    assert abs((xs[0] + xs[1]) / 2 - cx) < 1e-6 and abs((ys[0] + ys[1]) / 2 - cy) < 1e-6
    # the M3 screw passes the HS100's smallest mounting hole with the pattern and H1's position tolerance together
    assert (P.HS100["L_hole"] - P.HS100["L_tol"] - 3.0) / 2 > P.HS100["FG_tol"] / 2 + 0.10, P.HS100


def t_h1_nuts_in_the_full_face_and_resistor_inside_the_window():
    import panel1450 as L, h1_heat_test_plate as P
    for x, y, d in _feats(P, "PEM_S_M3"):
        assert abs(x) + d / 2 < L.REB_IN[0] / 2 and abs(y) + d / 2 < L.REB_IN[1] / 2, (x, y)
    x0, y0, x1, y1 = P.PATCH_RECT
    assert max(abs(x0), abs(x1)) < L.WINDOW[0] / 2 and max(abs(y0), abs(y1)) < L.WINDOW[1] / 2, P.PATCH_RECT
    for bx, by in L.FRAME_BOSSES:
        dx = max(x0 - bx, 0, bx - x1); dy = max(y0 - by, 0, by - y1)
        assert math.hypot(dx, dy) > L.FACE_HOLE / 2, (bx, by)


def t_h1_follows_its_source_when_the_source_moves():
    """A property, not today's number: move the PA flange site in panel1450 and H1's nuts move with it."""
    import importlib, panel1450 as L, h1_heat_test_plate as P
    saved = copy.deepcopy(L.PA_MOUNT)
    try:
        L.PA_MOUNT["c"] = (saved["c"][0] + 10.0, saved["c"][1] - 5.0)
        importlib.reload(P)
        xs = sorted(set(round(p[0], 6) for p in _feats(P, "PEM_S_M3")))
        assert abs((xs[0] + xs[1]) / 2 - L.PA_MOUNT["c"][0]) < 1e-6, xs
    finally:
        L.PA_MOUNT.clear(); L.PA_MOUNT.update(saved); importlib.reload(P)


def _plate_numbers(L):
    """The figures H1 shares with C1, as panel1450 holds them (and the pattern spans the sheet prints)."""
    nums = set(L.PLATE[:2]) | set(L.REB_IN) | {L.FACE_HOLE} | set(abs(v) for v in L.RELIEF_POCKET[:4])
    for x, y in L.FRAME_BOSSES: nums |= {abs(x), abs(y), 2 * abs(x), 2 * abs(y)}
    return set(round(v, 2) for v in nums if v)


def _typed(src, nums):
    """Every numeric constant, and every number written inside a string constant, that equals one of nums (the AST is parsed;
    docstrings are documentation, not inputs, and are left out)."""
    import re
    hits, tree = [], ast.parse(src)
    docs = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr) \
                and isinstance(n.body[0].value, ast.Constant) and isinstance(n.body[0].value.value, str):
            docs.add(id(n.body[0].value))
        if isinstance(n, ast.keyword) and n.arg in ("fontsize", "fs", "lw", "linespacing", "pad", "dpi") and isinstance(n.value, ast.Constant):
            docs.add(id(n.value))      # a font size or a line width is typography, not a design number
    for node in ast.walk(tree):
        if id(node) in docs: continue
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if round(abs(float(node.value)), 2) in nums: hits.append(node.value)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            hits += [t for t in re.findall(r"\d+\.\d+", node.value) if round(float(t), 2) in nums]
    return hits


def t_h1_scripts_type_no_design_number():
    import case_geometry_check as C, panel1450 as L
    nums = _plate_numbers(L)
    for f in ("h1_heat_test_plate.py", "h1_heat_test_plate_drawing.py"):
        src = open(os.path.join(V2, "cad", f), encoding="utf-8").read()
        assert not C.literal_inputs(src, L), (f, C.literal_inputs(src, L))
        assert not _typed(src, nums), (f, _typed(src, nums))
    # the control: a script that types the plate or a pattern span is found
    assert _typed("W, H = 377.2, 263.0\nK.dim_v(ax, 0, 0, 1, '242.32')\n", nums) == [377.2, 263.0, "242.32"], _typed("W, H = 377.2, 263.0\nK.dim_v(ax, 0, 0, 1, '242.32')\n", nums)


def t_h1_release_folder_is_immutable():
    import case_geometry_check as C
    d = need(os.path.join(V2, "release", "case-2026-09-27", "h1-heat-test-plate"), "the H1 release folder")
    probs = C.manifest(d)
    assert not probs, probs
