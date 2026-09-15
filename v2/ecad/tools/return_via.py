#!/usr/bin/env python3
"""A ground via beside every signal via (rule 2 of the owner ruling of 15 September 2026 20:15 CEST, MESHSAT-862).

The return current of a signal follows the reference plane under it; where the signal changes layer through a via, the
return has to change plane too, and it does so through the nearest ground via. A signal via with no ground via near it
sends its return the long way round, which is the loop that radiates and picks up. Freerouting places the signal via and
nothing placed a return via beside it, on any board of this set, until this tool.

judge(board, path): every PCB_VIA whose net is a SIGNAL (signalnets.classify: not ground, not a zone owner, not an intent
rail, not a power class) is judged; a via within FAN_MM of a footprint whose finest SMD pad pitch is FAN_PITCH_MM or under
(the CM5 receptacles, the M.2 sockets, 0.4 and 0.5 mm QFNs) is EXEMPT (owner scope answer 3: there is no room for a second
via in such a fan, and the fan sits over solid ground with stitch rows beside it); the rest are satisfied by a GND via or a
plated GND pad whose centre lies within RETURN_MM. Returns {"judged", "exempt", "lacking": [text per via], "positions"}.

fix (return_via.py <board.kicad_pcb>): for each lacking via, candidates on rings of RINGS mm in eight directions; a locked
ground via of the board's stitch size (max(0.6, the board's via minimum) / max(0.3, its drill minimum), as pour_stitch.py)
goes at the first candidate that (a) keeps the class clearance from every pad, track and via of another net on every
layer (a through via spans them all) and (b) lies inside a filled GND zone on at least one layer (a ground via that lands
in no ground copper connects nothing). All placements go on at once, one DRC judges them, a new via that appears in a
hard violation is removed and its signal via tries its next candidate, ROUNDS rounds at most. The stage is judged like
every copper stage of the finish: kept only if neither the hard count nor the unrouted count rose against the board it
was handed, otherwise the board is put back as it was.

--check: judge only, write out/return_via.verdict.json (PASS with nothing lacking, FAIL otherwise, INCONCLUSIVE when the
board has tracks and not one signal via to judge), exit 0/1/3.

Usage: return_via.py <board.kicad_pcb> [--check] [--dry] [--radius=1.5]"""
import sys, os, math, json, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, signalnets, intent, hardset
import boardorder

RETURN_MM = 1.5          # centre to centre, signal via to its ground via
FAN_PITCH_MM = 0.5       # a footprint whose finest SMD pad pitch is this or under is a fine-pitch fan
FAN_MM = 2.2             # a via this close to such a footprint's pads is inside its fan
RINGS = (1.0, 1.25, 1.5) # candidate distances for the ground via
ROUNDS = 3
TOOLS = os.path.dirname(os.path.abspath(__file__))
mm = lambda v: v / 1e6


def _min_pitch(fp):
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]; best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return mm(best)


def _fine_pads(b):
    """The SMD pad centres of every fine-pitch footprint, in mm."""
    out = []
    for fp in b.GetFootprints():
        if _min_pitch(fp) <= FAN_PITCH_MM:
            out += [(mm(p.GetPosition().x), mm(p.GetPosition().y)) for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    return out


def _gnd_points(b):
    """Every ground via and every plated ground pad centre, in mm."""
    pts = [(mm(t.GetPosition().x), mm(t.GetPosition().y)) for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname().lstrip("/") == "GND"]
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname().lstrip("/") == "GND" and p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH,) and p.GetDrillSize().x > 0:
                pts.append((mm(p.GetPosition().x), mm(p.GetPosition().y)))
    return pts


def _near(pt, pts, r):
    x, y = pt
    return any(abs(px - x) <= r and abs(py - y) <= r and math.hypot(px - x, py - y) <= r for px, py in pts)


def judge(b, path=None, radius=RETURN_MM):
    path = path or b.GetFileName(); it = intent.load(path) or {}
    signals, _ = signalnets.classify(b, path, it.get("rails", {}).keys())
    fine = _fine_pads(b); gnd = _gnd_points(b)
    judged = exempt = 0; lacking = []; positions = []
    for t in boardorder.tracks(b):   # this loop DECIDES which via gets the first candidate site; board order follows a random uuid
        if t.GetClass() != "PCB_VIA": continue
        net = t.GetNetname()
        if not signalnets.is_signal(net, signals): continue
        pt = (mm(t.GetPosition().x), mm(t.GetPosition().y))
        if _near(pt, fine, FAN_MM): exempt += 1; continue
        judged += 1
        if not _near(pt, gnd, radius):
            lacking.append("%s at (%.2f, %.2f)" % (net.lstrip("/"), pt[0], pt[1])); positions.append((t, pt))
    return {"judged": judged, "exempt": exempt, "lacking": lacking, "positions": positions, "signals": len(signals)}


def _site_free(b, x, y, vd, clr, own):
    """The class clearance from every pad, track and via of another net, on every layer (a through via spans them all)."""
    X, Y = x * 1e6, y * 1e6; need = (vd / 2 + clr) * 1e6
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == own: continue
            bb = p.GetBoundingBox(); c = bb.GetCenter()
            dx = max(0.0, abs(X - c.x) - bb.GetWidth() / 2.0); dy = max(0.0, abs(Y - c.y) - bb.GetHeight() / 2.0)
            if math.hypot(dx, dy) < need: return False
    for t in b.GetTracks():
        if t.GetNetname() == own: continue
        if t.GetClass() == "PCB_VIA":
            if math.hypot(t.GetPosition().x - X, t.GetPosition().y - Y) < need + t.GetWidth() / 2.0: return False
        else:
            ax, ay, bx, by = t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
            L2 = (bx - ax) ** 2 + (by - ay) ** 2
            u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((X - ax) * (bx - ax) + (Y - ay) * (by - ay)) / L2))
            if math.hypot(X - (ax + u * (bx - ax)), Y - (ay + u * (by - ay))) < need + t.GetWidth() / 2.0: return False
    return True


def _in_gnd_fill(b, x, y):
    p = pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6))
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname().lstrip("/") != "GND": continue
        for L in z.GetLayerSet().Seq():
            try:
                if z.GetFilledPolysList(L).Contains(p): return True
            except Exception: pass
    return False


def _measure(path):
    """(hard, unrouted) of the saved board through drc.sh and hardset, the finish's own instruments."""
    od = os.path.join(os.path.dirname(os.path.abspath(path)), "out"); os.makedirs(od, exist_ok=True)
    rep = os.path.join(od, os.path.basename(os.path.splitext(path)[0]) + "-return_via-drc.json")
    subprocess.run([os.path.join(TOOLS, "drc.sh"), path, rep], capture_output=True, text=True)
    d = hardset.load(rep); c = hardset.counts(d)
    return c["hard"], c["unrouted"], d


def _own_hard(d, new_pts, tol=0.01):
    """The (x, y) of the new vias that appear in a hard violation of the report."""
    hit = set()
    for v in d.get("violations", []):
        if v.get("type") not in hardset.HARD_POST: continue
        for i in v.get("items", []):
            p = i.get("pos") or {}
            for pt in new_pts:
                if abs(p.get("x", 1e9) - pt[0]) <= tol and abs(p.get("y", 1e9) - pt[1]) <= tol: hit.add(pt)
    return hit


def fix(path, dry=False, radius=RETURN_MM):
    if dry:   # work on a copy beside the board, with its project file, so the DRC judges it against the right classes
        tmp = os.path.splitext(path)[0] + "-return_via-dry.kicad_pcb"; shutil.copy(path, tmp)
        for e in (".kicad_pro", ".kicad_prl"):
            if os.path.exists(os.path.splitext(path)[0] + e): shutil.copy(os.path.splitext(path)[0] + e, os.path.splitext(tmp)[0] + e)
        path = tmp; print("return_via: dry run on %s" % tmp)
    b = pcbnew.LoadBoard(path); ds = b.GetDesignSettings()
    VD, VDR = max(0.6, mm(ds.m_ViasMinSize)), max(0.3, mm(ds.m_MinThroughDrill))
    # the board's own minimum clearance (KiCad 9's BOARD_DESIGN_SETTINGS has no GetDefault(); the first run on C18 died here)
    clr = max(mm(ds.m_MinClearance), 0.127)
    gnd_net = b.FindNet("GND")
    if gnd_net is None: print("return_via: the board has no GND net; nothing placed"); return 0
    before = judge(b, path, radius)
    print("return_via: %d signal vias judged, %d exempt in fine-pitch fans, %d without a ground via within %.1f mm (%d signal nets)" % (before["judged"], before["exempt"], len(before["lacking"]), radius, before["signals"]))
    if not before["lacking"]: return 0
    keep = path + ".return_via.bak"; shutil.copy(path, keep)
    h0, u0, _ = _measure(path)
    todo = {pt: [] for _, pt in before["positions"]}
    for pt in todo:
        cands = []
        for r in RINGS:
            for k in range(8):
                a = k * math.pi / 4; cands.append((round(pt[0] + r * math.cos(a), 3), round(pt[1] + r * math.sin(a), 3)))
        todo[pt] = cands
    placed = {}; refused = {}
    for rnd in range(1, ROUNDS + 1):
        b = pcbnew.LoadBoard(path); new = []
        for pt, cands in todo.items():
            if pt in placed: continue
            spot = None
            while cands:
                c = cands.pop(0)
                if _site_free(b, c[0], c[1], VD, clr, "GND") and _in_gnd_fill(b, c[0], c[1]): spot = c; break
            if spot is None: refused[pt] = "no candidate site free of other-net copper inside a ground fill"; continue
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(int(spot[0] * 1e6), int(spot[1] * 1e6)))
            v.SetDrill(int(VDR * 1e6)); v.SetWidth(int(VD * 1e6)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(gnd_net); v.SetLocked(True)
            b.Add(v); new.append((pt, spot))
        if not new: break
        pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(path, b)
        h, u, d = _measure(path); bad = _own_hard(d, [s for _, s in new])
        b = pcbnew.LoadBoard(path)
        for t in list(b.GetTracks()):
            if t.GetClass() == "PCB_VIA" and (round(mm(t.GetPosition().x), 3), round(mm(t.GetPosition().y), 3)) in bad and t.GetNetname().lstrip("/") == "GND" and t.IsLocked(): b.Remove(t)
        pcbnew.SaveBoard(path, b)
        for pt, spot in new:
            if spot in bad: continue
            placed[pt] = spot
        print("return_via: round %d placed %d, %d refused by the DRC and retried" % (rnd, len([1 for _, s in new if s not in bad]), len(bad)))
        if not bad: break
    b = pcbnew.LoadBoard(path); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(path, b)
    h1, u1, _ = _measure(path); after = judge(b, path, radius)
    if h1 > h0 or u1 > u0:
        print("return_via: HURT (hard %d -> %d, unrouted %d -> %d): reverting every ground via" % (h0, h1, u0, u1)); shutil.copy(keep, path); os.remove(keep); return 1
    os.remove(keep)
    left = [t for t in after["lacking"]]
    print("return_via: placed %d ground vias, %d signal vias still without one (hard %d -> %d, unrouted %d -> %d)%s" % (len(placed), len(left), h0, h1, u0, u1, "" if not left else ": " + "; ".join(left[:12]) + (" ..." if len(left) > 12 else "")))
    for pt, why in list(refused.items())[:12]: print("return_via:   (%.2f, %.2f): %s" % (pt[0], pt[1], why))
    return 0


def check(path, radius=RETURN_MM):
    import verdict
    b = pcbnew.LoadBoard(path); r = judge(b, path, radius)
    n_tracks = sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_TRACK")
    res = verdict.INCONCLUSIVE if (n_tracks and not r["judged"] and not r["exempt"]) else (verdict.PASS if not r["lacking"] else verdict.FAIL)
    print("return_via: %d signal vias judged, %d exempt in fine-pitch fans, %d without a ground via within %.1f mm" % (r["judged"], r["exempt"], len(r["lacking"]), radius))
    for l in r["lacking"][:20]: print("return_via:   " + l)
    return verdict.write("return_via", res, counts={"judged": r["judged"], "exempt": r["exempt"], "lacking": len(r["lacking"])}, denominator=r["judged"],
                         evidence=r["lacking"][:200], inputs={"board": path},
                         note="" if res != verdict.INCONCLUSIVE else "the board has tracks and no signal via at all: the scope filter is suspect",
                         out_dir=os.path.join(os.path.dirname(os.path.abspath(path)), "out"))


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    rad = float(next((a.split("=", 1)[1] for a in sys.argv[2:] if a.startswith("--radius=")), RETURN_MM))
    if "--check" in sys.argv: sys.exit(check(sys.argv[1], rad))
    sys.exit(fix(sys.argv[1], dry="--dry" in sys.argv, radius=rad))
