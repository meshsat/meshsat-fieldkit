#!/usr/bin/env python3
"""Drift checks of the case geometry (MESHSAT-1357, 27 Sep 2026): the readings the case set rests on must agree with the artefacts they were
taken from, so a change on either side is caught the day it lands instead of when a part does not fit. Stdlib only; each check returns a list
of problems (empty = agreement) and never writes anything. v2/ecad/tools/tests/test_case_geometry.py runs them on the tree and on defective
fixtures.

  board_identity(z)         v2/cad/zstack.json names each board file with its sha256: every one must still be the committed file.
  stack_and_outlines(z, L)  panel1450's stack thicknesses and A's, B's and E's outlines are the board files' own.
  b16_coverage(z, env)      every part on board B's top 3.0 mm or taller (by its model or its class) lies inside an envelope of the face gates'
                            list (panel1450.B16_TALL) at least as tall, and every part with no height lies inside some envelope.
  face_basis(out_text, L)   the setting leg's pad top and the face top frame_seat.out was computed with are panel1450's (LEG_TOP_Z, FACE_TOP_Z).
  frame_seat_current()      frame_seat.py, run now, prints exactly the recorded frame_seat.out (the recorded reading is the script's).
  manifest(folder)          every file a release folder's MANIFEST.sha256 names has that sha256 (a release is an immutable copy).
  literal_inputs(src, L)    frame_seat.py's DESIGN names are read from panel1450, not typed (the draft of 27 Sep 2026; it fails on the
                            earlier file, which typed U51's height as an INFERRED class figure and a six-part hand list against B16_TALL).
  maker_maxima(z)           every part the board reading gives a maker's maximum height (zstack.py MAKER_MAX) is the part the maximum was read
                            for: its library model stands at the sheet's typical, never above the maximum.
  worst_case_reads(src)     a worst-case chain of frame_seat.py takes a board part's maker maximum (`height_max`), never its nominal model
                            height (`height`): the second review of 27 Sep 2026 found the draft feeding U51's typical 1.50 into M14e and M14g."""
import os, re, sys, ast, json, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(V2, ".."))
TOOLS = os.path.join(V2, "ecad", "tools")
FRAME_SEAT = os.path.join(V2, "vendor", "peli", "frame_seat.py")
FRAME_SEAT_OUT = os.path.join(V2, "vendor", "peli", "1450", "frame_seat.out")


def _overlap(a, b):
    return a[2] > b[0] and a[0] < b[2] and a[3] > b[1] and a[1] < b[3]


def board_identity(z, repo=REPO):
    probs = []
    for k, b in sorted(z["boards"].items()):
        p = os.path.join(repo, b["file"])
        if not os.path.exists(p):
            probs.append("%s: %s is absent" % (k, b["file"])); continue
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if got != b["sha256"]:
            probs.append("%s: %s is %s, the reading was taken from %s: re-run v2/cad/zstack.py --json v2/cad/zstack.json" % (k, b["file"], got[:12], b["sha256"][:12]))
    return probs


def stack_and_outlines(z, L):
    """panel1450's typed board facts against the board files: each board of the stack is as thick as its file says, and A's, B's and E's
    outlines in panel1450 are the files' Edge.Cuts."""
    probs = []
    names = {"board E dock strip": "e", "board A": "a", "board B": "b"}
    for n, t in L.STACK:
        k = names.get(n)
        if k and abs(z["boards"][k]["thickness"] - t) > 1e-6:
            probs.append("%s: panel1450.STACK %.2f, the board file %.2f" % (n, t, z["boards"][k]["thickness"]))
    for k, o in (("a", L.A_OUTLINE), ("b", L.B_OUTLINE), ("e", L.E_OUTLINE)):
        got = z["boards"][k]["outline"]
        if any(abs(a - b) > 0.01 for a, b in zip(o, got)):
            probs.append("board %s outline: panel1450 %s, the board file %s" % (k, tuple(o), tuple(got)))
    return probs


def b16_coverage(z, envelopes):
    probs = []
    for p in z["boards"]["b"]["parts"]:
        if p["side"] != "top" or p.get("klass") in ("BODYLESS", "PANEL", "MATES"): continue
        over = [(h, n) for r, h, n in envelopes if _overlap(p["rect"], r)]
        if p["height"] is None:
            if not over: probs.append("%s (%s): no height and no envelope over it" % (p["ref"], p["lib"]))
        elif p["height"] >= 3.0 and not any(h + 1e-6 >= p["height"] for h, n in over):
            probs.append("%s (%s) %.2f tall: %s" % (p["ref"], p["lib"], p["height"], "taller than %s" % [n for h, n in over] if over else "under no envelope"))
    return probs


def face_basis(out_text, L):
    probs = []
    m = re.search(r"pad top ([\d.]+) = shoulder", out_text)
    f = re.search(r"face top ([\d.]+) nominal", out_text)
    if not m or not f:
        return ["frame_seat.out prints no pad top or face top: the output format moved"]
    if abs(float(m.group(1)) - L.LEG_TOP_Z) > 0.005: probs.append("pad top: frame_seat.out %s, panel1450.LEG_TOP_Z %.2f" % (m.group(1), L.LEG_TOP_Z))
    if abs(float(f.group(1)) - L.FACE_TOP_Z) > 0.005: probs.append("face top: frame_seat.out %s, panel1450.FACE_TOP_Z %.2f" % (f.group(1), L.FACE_TOP_Z))
    return probs


def frame_seat_current(script=FRAME_SEAT, recorded=FRAME_SEAT_OUT):
    got = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
    if got.returncode != 0:
        return ["frame_seat.py exits %d: %s" % (got.returncode, got.stderr.strip()[-300:])]
    rec = open(recorded, encoding="utf-8").read()
    if got.stdout == rec: return []
    a, b = rec.splitlines(), got.stdout.splitlines()
    first = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
    return ["frame_seat.py no longer prints the recorded frame_seat.out: first difference at line %d" % (first + 1)]


def manifest(folder):
    mf = os.path.join(folder, "MANIFEST.sha256")
    if not os.path.exists(mf): return ["%s has no MANIFEST.sha256" % folder]
    probs = []
    for line in open(mf, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        digest, name = line.split(None, 1); name = name.lstrip("*")
        p = os.path.join(folder, name)
        if not os.path.exists(p): probs.append("%s: absent" % name); continue
        if hashlib.sha256(open(p, "rb").read()).hexdigest() != digest: probs.append("%s: changed since the release" % name)
    return probs


def maker_maxima(z):
    """Every part carrying `height_max` (zstack.py MAKER_MAX): the maximum is at least the typical, the typical is the library model's height
    (so the maximum was read for this body), and the source names a file in v2/vendor/ that exists."""
    probs = []
    for k, b in sorted(z["boards"].items()):
        for p in b["parts"]:
            if "height_max" not in p: continue
            hm, ht, h = p["height_max"], p.get("height_typ"), p["height"]
            if ht is None or hm + 1e-9 < ht: probs.append("%s %s: maximum %s under its typical %s" % (k, p["ref"], hm, ht)); continue
            if h is None or abs(h - ht) > 0.01:
                probs.append("%s %s (%s): the model stands %s, the sheet's typical is %s: the maximum was read for another body" % (k, p["ref"], p["lib"], h, ht))
            m = re.search(r"\((v2/vendor/[^)\s]+)\)", p.get("height_max_source", ""))
            if not m or not os.path.exists(os.path.join(REPO, m.group(1))):
                probs.append("%s %s: the maximum's source names no file in v2/vendor/ (%r)" % (k, p["ref"], p.get("height_max_source", "")[:80]))
    return probs


# the names whose chains are WORST-CASE and take a board part's height: they read the maker's maximum, never the model's nominal body
WORST_CASE_HEIGHTS = ("U51_H",)


def worst_case_reads(src):
    """Every assignment in frame_seat.py to a WORST_CASE_HEIGHTS name must subscript a board part with 'height_max'; a read of 'height' (the
    library model, a nominal body) or 'height_typ' under-states the part at the worst."""
    probs = []
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.Assign): continue
        for t in node.targets:
            if not (isinstance(t, ast.Name) and t.id in WORST_CASE_HEIGHTS): continue
            keys = [n.slice.value for n in ast.walk(node.value) if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                    and isinstance(n.slice.value, str)]
            if "height_max" not in keys:
                probs.append("%s reads %s: a worst-case chain takes the maker's maximum ('height_max'), not a nominal body" % (t.id, keys or "no board part"))
    return probs


# the design names frame_seat.py uses and the panel1450 value each must equal; a name frame_seat READS (not a literal) passes by construction
def design_names(L):
    return {"PLATE": L.PLATE, "REBATE": L.REBATE, "REB_IN": L.REB_IN, "FACE_HOLE": L.FACE_HOLE, "LEG_Y": L.LEG["y"], "LEG_X": L.LEG["col_x"],
            "FOOT_X": L.LEG["foot_x"], "RELIEF": L.LEG["relief"], "B_UNDER": L.B_UNDER_Z, "B_TOP": L.B_TOP_Z, "A_EDGE_Y": L.A_OUTLINE[3],
            "AX_Z": L.SMA_Z, "SITES_E": [tuple(x) for x in L.WALL_EAST], "SITES_W": [tuple(x) for x in L.WALL_WEST],
            "SCREWS": [tuple(x) for x in L.CONN_PLATE["screws"]], "RFP_SCREWS": [tuple(x) for x in L.RF_PLATE["screws"]],
            "U51_H": "READ", "tall": "READ"}


def literal_inputs(src, L):
    """Every assignment in frame_seat.py's source to a design name whose value is a literal (a constant, a tuple or list of constants, or
    arithmetic on them) must equal panel1450's; U51_H and the tall list must not be literals at all (they are the board's)."""
    want = design_names(L); probs = []
    for node in ast.walk(ast.parse(src)):
        targets = []
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name): targets.append((t.id, node.value))
                elif isinstance(t, ast.Tuple) and isinstance(node.value, ast.Tuple) and len(t.elts) == len(node.value.elts):
                    targets += [(e.id, v) for e, v in zip(t.elts, node.value.elts) if isinstance(e, ast.Name)]
        for name, val in targets:
            if name not in want: continue
            try:
                lit = ast.literal_eval(val) if not isinstance(val, ast.BinOp) else eval(compile(ast.Expression(val), "x", "eval"), {"__builtins__": {}})
            except Exception:
                continue     # not a literal: read from somewhere, which is what the rule asks
            if want[name] == "READ":
                probs.append("%s is typed (%r); it is the committed board's (v2/cad/zstack.json)" % (name, lit if not isinstance(lit, list) else "a list of %d" % len(lit)))
            else:
                w = want[name]
                norm = lambda v: [tuple(x) if isinstance(x, (list, tuple)) else x for x in v] if isinstance(v, list) else (tuple(v) if isinstance(v, tuple) else v)
                if isinstance(lit, (int, float)) and isinstance(w, (int, float)):
                    if abs(lit - w) > 1e-6: probs.append("%s typed %r, panel1450 %r" % (name, lit, w))
                elif norm(lit) != norm(w):
                    probs.append("%s typed %r, panel1450 %r" % (name, lit, w))
    return probs


if __name__ == "__main__":
    sys.path.insert(0, TOOLS)
    import panel1450 as L
    z = json.load(open(os.path.join(HERE, "zstack.json"), encoding="utf-8"))
    rep = dict(board_identity=board_identity(z), stack_and_outlines=stack_and_outlines(z, L), b16_coverage=b16_coverage(z, L.B16_TALL),
               face_basis=face_basis(open(FRAME_SEAT_OUT, encoding="utf-8").read(), L), frame_seat_current=frame_seat_current(),
               literal_inputs=literal_inputs(open(FRAME_SEAT, encoding="utf-8").read(), L), maker_maxima=maker_maxima(z),
               worst_case_reads=worst_case_reads(open(FRAME_SEAT, encoding="utf-8").read()))
    rel = os.path.join(V2, "release", "case-2026-09-27")
    if os.path.isdir(rel): rep["manifest"] = manifest(rel)
    for k, v in rep.items(): print("%-20s %s" % (k, "OK" if not v else "; ".join(v)))
    sys.exit(0 if not any(v for k, v in rep.items() if k not in ("literal_inputs", "worst_case_reads")) else 1)
