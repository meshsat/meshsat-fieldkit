#!/usr/bin/env python3
"""No two placement regions of one board may overlap, because the packer fills each to its edge.

12 September 2026 (MESHSAT-862, appendix 32.135). A's `CHQ` ended at y 30.5 and `FES` began at 30, so the two
rectangles overlapped by half a millimetre and the packer put the charger's CSD18510Q5B FETs (a 7.19 x 5.59 mm
courtyard) under the front end's resistor row: four `courtyards_overlap` on the PLACED board, before the
pre-router touched it, which nothing read until the pre-route DRC ran after the pairs were laid.

The rule reads the `REGIONS` table out of each placement generator's source, because that table is where the
floor plan lives and a rectangle is either clear of its neighbours or it is not."""
import ast, os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _regions(src):
    """[(name, (x0, y0, x1, y1))] from a generator's REGIONS list, by parsing the file rather than importing it
    (importing needs pcbnew and a board)."""
    s = open(os.path.join(TOOLS, src), errors="replace").read()
    m = re.search(r"^REGIONS = \[", s, re.M)
    if not m: return []
    i = m.end() - 1
    depth, j = 0, i
    while j < len(s):
        if s[j] == "[": depth += 1
        elif s[j] == "]":
            depth -= 1
            if depth == 0: break
        j += 1
    out = []
    for el in ast.parse("X = " + s[i:j + 1], mode="exec").body[0].value.elts:
        if not isinstance(el, ast.Tuple) or len(el.elts) < 2: continue
        name = el.elts[0].value if isinstance(el.elts[0], ast.Constant) else "?"
        rect = el.elts[1]
        if not isinstance(rect, ast.Tuple) or len(rect.elts) != 4: continue
        # a board assembled on both sides declares the side as a fourth element (D), and two regions on
        # opposite sides may share the same rectangle: they are different copper
        back = False
        if len(el.elts) >= 4 and isinstance(el.elts[3], ast.Constant): back = bool(el.elts[3].value)
        try: out.append((name, tuple(ast.literal_eval(c) for c in rect.elts), back))
        except Exception: pass
    return out


def t_no_two_regions_of_a_board_overlap():
    bad = []
    for src in sorted(f for f in os.listdir(TOOLS) if re.match(r"gen_pcb_\w+3\.py$", f)):
        rs = _regions(src)
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                (na, a, ba), (nb, c, bb) = rs[i], rs[j]
                if ba != bb: continue   # opposite sides of the board
                if not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1]):
                    ox = min(a[2], c[2]) - max(a[0], c[0]); oy = min(a[3], c[3]) - max(a[1], c[1])
                    bad.append("%s: %s and %s overlap by %.2f x %.2f mm" % (src, na, nb, ox, oy))
    assert not bad, "placement regions overlap:\n  " + "\n  ".join(bad)


def t_the_rule_reads_a_real_table():
    """A rule that silently finds no regions passes on anything; this one says how many it read."""
    total = sum(len(_regions(f)) for f in os.listdir(TOOLS) if re.match(r"gen_pcb_\w+3\.py$", f))
    assert total >= 20, "only %d region(s) parsed out of the placement generators; the parser has drifted" % total
