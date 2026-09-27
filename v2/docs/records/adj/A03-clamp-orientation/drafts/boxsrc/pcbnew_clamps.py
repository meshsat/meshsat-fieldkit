# pcbnew read of the committed phase boards: every diode/clamp footprint, its pads' nets and board positions,
# and which pad the footprint's own cathode marks point at, computed in BOARD coordinates (rotation and flip
# included): (1) the F/B.Fab diode glyph apex (the endpoint shared by three or more fab segments), (2) the
# length-weighted centroid of the silk segments (the closed side of the bracket). Nearest pad wins.
import pcbnew, json, re, sys, hashlib, math
WANT = re.compile(r"TVS|Schottky|SMBJ|SMCJ|PESD|USBLC|BAT54|SS14|SS2040|1N4148|ESD", re.I)
boards = sys.argv[1:]
out = {}
for path in boards:
    b = pcbnew.LoadBoard(path)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    rec = {"sha256_16": sha, "parts": {}}
    for fp in b.GetFootprints():
        ref = fp.GetReference(); val = fp.GetValue(); fpid = str(fp.GetFPID().GetUniStringLibId())
        if re.match(r"^(J|R|C|L)", ref) or not WANT.search(val + " " + fpid): continue
        side = "B" if fp.IsFlipped() else "F"
        pads = {}
        for p in fp.Pads():
            pos = p.GetPosition(); pads.setdefault(p.GetNumber(), dict(net=p.GetNetname(), x=pcbnew.ToMM(pos.x), y=pcbnew.ToMM(pos.y)))
        fab_pts = {}; silk = []
        for it in fp.GraphicalItems():
            ly = b.GetLayerName(it.GetLayer())
            if not isinstance(it, pcbnew.PCB_SHAPE): continue
            if it.GetShape() != pcbnew.SHAPE_T_SEGMENT: continue
            s = it.GetStart(); e = it.GetEnd()
            s = (round(pcbnew.ToMM(s.x), 3), round(pcbnew.ToMM(s.y), 3)); e = (round(pcbnew.ToMM(e.x), 3), round(pcbnew.ToMM(e.y), 3))
            if ly.endswith(".Fab") or ly.endswith(".Fabrication"):
                for q in (s, e): fab_pts[q] = fab_pts.get(q, 0) + 1
            if ly.endswith(".SilkS") or ly.endswith(".Silkscreen"): silk.append((s, e))
        def nearest(pt):
            best = None
            for n, pd in pads.items():
                d = math.hypot(pd["x"] - pt[0], pd["y"] - pt[1])
                if best is None or d < best[1]: best = (n, round(d, 3))
            return best
        apex = [q for q, k in fab_pts.items() if k >= 3]
        r = dict(fpid=fpid, value=val, side=side, orientation_deg=fp.GetOrientationDegrees(),
                 pos=[pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)], pads=pads,
                 fab_apex=[list(a) for a in apex], fab_apex_nearest_pad=[nearest(a) for a in apex])
        if silk:
            L = sum(math.hypot(e[0] - s[0], e[1] - s[1]) for s, e in silk)
            cx = sum(((s[0] + e[0]) / 2) * math.hypot(e[0] - s[0], e[1] - s[1]) for s, e in silk) / L
            cy = sum(((s[1] + e[1]) / 2) * math.hypot(e[0] - s[0], e[1] - s[1]) for s, e in silk) / L
            r["silk_centroid"] = [round(cx, 3), round(cy, 3)]; r["silk_centroid_nearest_pad"] = nearest((cx, cy))
        rec["parts"][ref] = r
    out[path] = rec
json.dump(out, open("/root/r2/A03-clamp-orientation/out/pcbnew_clamps.json", "w"), indent=1)
for path, rec in out.items():
    print("==", path, rec["sha256_16"])
    for ref, r in sorted(rec["parts"].items()):
        print(" ", ref, r["fpid"], r["side"], r["orientation_deg"], {n: p["net"] for n, p in sorted(r["pads"].items())},
              "fab-apex->pad", [a[0] for a in r["fab_apex_nearest_pad"]], "silk->pad", (r.get("silk_centroid_nearest_pad") or [None])[0])
