#!/usr/bin/env python3
"""The placement instrument (MESHSAT-862 Stage D, 8 Sep 2026, appendix 32.64 W3; rewritten 02:20 after the first calibration attempt):
a minute-scale predictor of where the router will fail, run on the placed board AFTER the escape pass (escape.py, join_adjacent_pins.py,
prefanout.py) and before any route is bought. Until 8 Sep the loop closed only through a full route (A22's INA226 fans at 8 mm pitch after
run 10, B16's HDMI switches at 9.6 mm after a 3 h 20 min route).

No fitted constant: the escape pass itself is the measurement. Its output on the board is the locked copper (stubs, knees, vias) of every
fine-pitch part, so the predictor reads:
  1. fine-pitch pads without an escape: a part with none (excluded by ESCAPE_SKIP, or escape.py placed none) within NEAR mm of another
     fine-pitch part is a FAIL (the router must fan a crowded row itself: B16's HDMI switches, A22's INA226 row of run 10); a part missing
     at least 3 and 30 percent of its escapes is a FAIL (the fan could not be placed); 1 or 2 missing pads are a WARN (the clean released
     boards carry those and routed);
  2. escape envelopes (the bounding box of each part's locked pieces within REACH mm) are reported as a Stage E feature only: on every clean
     released board neighbouring fans overlap in bounding box with their vias interleaved, so the overlap is not a verdict; the escape pass
     and the pre-route DRC (0 hard) are the proof that the fans fit;
  3. escapes that the pre-route DRC found in a hard violation (out/<name>-pruned.txt from escape_prune.py, when present): FAIL per pad.
Also reported: pin density per 20 mm tile, the HPWL of every net over its pad centres, and the decoupling loop lengths from the intent file
before the route (3 mm rule, FAIL beyond it). A PNG (--png) shows the envelopes, red where they collide.

Usage: place_audit.py <board.kicad_pcb> [--png out.png] [--near 6] [--reach 5] [--skip REF,REF]   -> exit 1 on a predicted collision."""
import sys, os, math, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

NEAR = 6.0; REACH = 5.0

def pitch_of(fp):
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = None
    for i in range(len(pads)):
        for j in range(i + 1, min(len(pads), i + 8)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if d > 0 and (best is None or d < best): best = d
    return best / 1e6 if best else None

def fine_pitch(fp):
    if re.search(r"SOT-23-[68]|SOT-583|TSOT-23-6|SOT23-6", fp.GetFPIDAsString()): return True
    p = pitch_of(fp); return p is not None and p <= 0.65

def pts(t): return [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]

def escape_envelopes(b, fine, reach=REACH, locked=None):
    """{ref: (x0, y0, x1, y1) mm of the part's locked escape pieces} and {ref: (pads with an escape, [pads without])} from the board after escape.py."""
    locked = [t for t in b.GetTracks() if t.IsLocked()] if locked is None else locked
    env = {}; escaped = {}
    for f in fine:
        bb = f.GetBoundingBox(False, False); nets = {p.GetNetname() for p in f.Pads() if p.GetNetCode() > 0}
        box = (bb.GetLeft() - int(reach * 1e6), bb.GetTop() - int(reach * 1e6), bb.GetRight() + int(reach * 1e6), bb.GetBottom() + int(reach * 1e6))
        mine = [t for t in locked if t.GetNetname() in nets and any(box[0] <= q.x <= box[2] and box[1] <= q.y <= box[3] for q in pts(t))]
        if mine:
            xs = [q.x for t in mine for q in pts(t)]; ys = [q.y for t in mine for q in pts(t)]
            env[f.GetReference()] = (min(xs) / 1e6, min(ys) / 1e6, max(xs) / 1e6, max(ys) / 1e6)
        got = 0; miss = []
        for p in f.Pads():
            if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or p.GetNetCode() <= 0: continue
            pb = p.GetBoundingBox(); pb.Inflate(int(0.05e6))
            if any(t.GetNetname() == p.GetNetname() and any(pb.Contains(q) for q in pts(t)) for t in mine): got += 1
            else: miss.append(p.GetNumber())
        escaped[f.GetReference()] = (got, miss)
    return env, escaped

def overlap(a, b): return max(0.0, min(a[2], b[2]) - max(a[0], b[0])), max(0.0, min(a[3], b[3]) - max(a[1], b[1]))

def main(a):
    if not a: print(__doc__); return 2
    near = float(a[a.index("--near") + 1]) if "--near" in a else NEAR; reach = float(a[a.index("--reach") + 1]) if "--reach" in a else REACH
    skip = set(a[a.index("--skip") + 1].split(",")) if "--skip" in a else set(os.environ.get("ESCAPE_SKIP", "").split(",")) - {""}
    b = pcbnew.LoadBoard(a[0]); lines = []; coll = 0
    fps = list(b.GetFootprints()); fine = [f for f in fps if fine_pitch(f)]
    locked = [t for t in b.GetTracks() if t.IsLocked()]
    env, escaped = escape_envelopes(b, fine, reach, locked)
    # 1. unescaped pads
    for f in fine:
        r = f.GetReference(); got, miss = escaped[r]
        if r in skip or got == 0:
            others = [g.GetReference() for g in fine if g is not f and math.hypot(g.GetPosition().x - f.GetPosition().x, g.GetPosition().y - f.GetPosition().y) / 1e6 <= near + (f.GetBoundingBox(False, False).GetWidth() + g.GetBoundingBox(False, False).GetWidth()) / 2e6]
            if others: lines.append("FAIL  %s has no escapes (%s) and stands within %.0f mm of %s: the router has to fan a crowded row itself" % (r, "excluded by ESCAPE_SKIP" if r in skip else "escape.py placed none", near, ", ".join(others[:4]))); coll += 1
            else: lines.append("WARN  %s has no escapes (%s), nothing fine-pitch near it" % (r, "excluded by ESCAPE_SKIP" if r in skip else "escape.py placed none"))
        elif miss and len(miss) >= max(3, int(0.3 * (got + len(miss)))):   # the clean released boards carry 1 to 2 skipped pads per part and routed; a fan mostly missing is the INA226 case
            lines.append("FAIL  %s: %d of %d fine-pitch pads without an escape (pads %s): the fan could not be placed" % (r, len(miss), got + len(miss), ",".join(miss[:8]))); coll += 1
        elif miss:
            lines.append("WARN  %s: %d of %d fine-pitch pads without an escape (pads %s): the router's job, pruned_gate-style check after the route" % (r, len(miss), got + len(miss), ",".join(miss[:8])))
    # 2. envelope overlaps: the bounding boxes of neighbouring fans overlap on every clean board (interleaved vias), so this is a feature for Stage E, not a verdict
    refs = sorted(env); ov_area = 0.0; ov_n = 0
    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            ox, oy = overlap(env[refs[i]], env[refs[j]])
            if ox > 0.3 and oy > 0.3: ov_area += ox * oy; ov_n += 1
    lines.append("INFO  escape envelopes: %d overlapping pairs, %.0f mm2 (a Stage E feature; the escape pass and the pre-route DRC already proved the fans fit)" % (ov_n, ov_area))
    # 3. pruned escapes
    pr = os.path.join(os.path.dirname(os.path.abspath(a[0])), "out", os.path.splitext(os.path.basename(a[0]))[0] + "-pruned.txt")
    if os.path.exists(pr):
        rows = [l.split("\t") for l in open(pr).read().splitlines() if l and not l.startswith("#")]
        for row in rows: lines.append("FAIL  the escape of %s.%s (%s) sat in a hard violation and was pruned: the pad is the router's" % (row[1], row[2], row[0])); coll += 1
    # pin density and HPWL
    edge = b.GetBoardEdgesBoundingBox(); ex0, ey0, ex1, ey1 = edge.GetLeft() / 1e6, edge.GetTop() / 1e6, edge.GetRight() / 1e6, edge.GetBottom() / 1e6
    tiles = {}
    for f in fps:
        for p in f.Pads():
            k = (int((p.GetPosition().x / 1e6 - ex0) // 20), int((p.GetPosition().y / 1e6 - ey0) // 20)); tiles[k] = tiles.get(k, 0) + 1
    busiest = sorted(tiles.items(), key=lambda kv: -kv[1])[:5]
    lines.append("INFO  pin density: busiest 20 mm tiles (pads per cm2): %s" % ", ".join("(%d,%d) %.0f" % (k[0], k[1], n / 4.0) for k, n in busiest))
    nets = {}
    for f in fps:
        for p in f.Pads():
            if p.GetNetCode() > 0: nets.setdefault(p.GetNetname(), []).append((p.GetPosition().x / 1e6, p.GetPosition().y / 1e6))
    hp = {n: (max(x for x, y in q) - min(x for x, y in q)) + (max(y for x, y in q) - min(y for x, y in q)) for n, q in nets.items() if len(q) > 1}
    top = sorted(hp.items(), key=lambda kv: -kv[1])[:10]
    lines.append("INFO  HPWL: %.0f mm over %d nets; longest %s" % (sum(hp.values()), len(hp), ", ".join("%s %.0f" % (n.lstrip("/"), v) for n, v in top)))
    try:
        import intent; it = intent.load(a[0])
    except Exception: it = None
    if it and it.get("bypass"):
        pads = {(f.GetReference(), p.GetNumber()): p for f in fps for p in f.Pads()}; far = 0
        for e in it["bypass"]:
            pin = pads.get((e["part"], e["pin"])); cap = [p for (ref, num), p in pads.items() if ref == e["cap"] and pin is not None and p.GetNetname() == pin.GetNetname()]
            if pin is None or not cap: continue
            d = math.hypot(cap[0].GetPosition().x - pin.GetPosition().x, cap[0].GetPosition().y - pin.GetPosition().y) / 1e6
            if d > 3.0: far += 1; lines.append("FAIL  bypass %s sits %.1f mm from %s.%s before the route (3 mm rule)" % (e["cap"], d, e["part"], e["pin"]))
        lines.append("INFO  decoupling: %d of %d bypass capacitors within 3 mm of their pin" % (len(it["bypass"]) - far, len(it["bypass"]))); coll += far
    else: lines.append("INFO  decoupling: 0 of 0 bypass entries (no intent file or none listed)")
    n_esc = sum(1 for r in env); lines.append("INFO  escapes measured on %d of %d fine-pitch parts (%d parts, %d locked pieces on the board)" % (n_esc, len(fine), len(fps), len(locked)))
    for l in lines: print("place_audit: " + l)
    print("place_audit: %d predicted collision(s) among %d fine-pitch parts of %d; %s" % (coll, len(fine), len(fps), "FAIL" if coll else "ALL PASS"))
    if "--png" in a:
        try:
            import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; from matplotlib.patches import Rectangle
            fig, ax = plt.subplots(figsize=(14, 9)); ax.add_patch(Rectangle((ex0, ey0), ex1 - ex0, ey1 - ey0, fill=False, lw=1.5))
            for f in fps:
                bb = f.GetBoundingBox(False, False); ax.add_patch(Rectangle((bb.GetLeft() / 1e6, bb.GetTop() / 1e6), bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, fill=True, alpha=0.15, color="gray", lw=0))
            for r, (x0, y0, x1, y1) in env.items():
                bad = any(l.startswith("FAIL") and (" %s " % r in l or " %s:" % r in l or "%s." % r in l or " %s," % r in l) for l in lines)
                ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, color="red" if bad else "green", lw=0.8)); ax.text(x0, y0, r, fontsize=5, color="red" if bad else "green")
            ax.set_xlim(ex0 - 5, ex1 + 5); ax.set_ylim(ey1 + 5, ey0 - 5); ax.set_aspect("equal"); ax.set_title("place_audit: %s, %d predicted collisions (red)" % (os.path.basename(a[0]), coll))
            fig.savefig(a[a.index("--png") + 1], dpi=130); print("place_audit: image", a[a.index("--png") + 1])
        except ImportError: print("place_audit: no matplotlib, no image")
    return 1 if coll else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
