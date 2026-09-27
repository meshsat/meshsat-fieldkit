#!/usr/bin/env python3
"""A06 (MESHSAT-1357): does any 4S pack plus the P board plus the heater mat fit the east or west pocket under the committed B21?

Every input carries its source and its status in the table below; the obstruction zones come from b_under.py / b_tht.py run on the
committed B21 board (v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb, sha256 2e64b5bf2d9cd3bc, commit f2541bea). Case frame: X along
the long axis, +Y to the hinge wall, Z up from the cavity floor (panel1450.py docstring). The pocket boxes are appendix 32.62's
(east X 120..178, Y -120..120; west X -178..-120, Y -40..120) and their ceiling is B's underside everywhere, as the question frames
the pocket (the extra headroom beyond B's edge at X +-165 and |Y| > 100 is NOT counted; see the notes).

For every configuration (cell count, cross-section of one section, where the P board goes, packaging) the script searches the
placement (0.25 mm in X, 0.5 mm in Y) that maximises the smallest clearance, and prints X spare, Y spare and the Z clearance at
the worst zone the pack lies under. A configuration FITS when all three are >= 0 at the stated base; it is reported at the
nominal base (heater mat 1.4 mm with the VHB pads beside it) and at the worst base (pads stacked on the mat)."""
import math, itertools, sys, os

# ------------------------------------------------------------------ inputs (value, source, status)
B_UNDER = 49.5 - 1.6   # panel1450.py:23 B_TOP_Z 49.5 (VERIFIED); B21 general thickness 1.6 (board file, VERIFIED) -> 47.9
CELLS = {
    "18650": dict(D=18.55, L=65.25, m=50.0, Wh=None, src="Samsung INR18650-35E spec 3.13-3.14, v2/vendor/battery/samsung-35e-akkuzentrum.pdf (VERIFIED)"),
    "21700": dict(D=21.55, L=70.15, m=71.0, Wh=18.0, src="Molicel INR-21700-P50B Product Data Sheet v1.1, molicel.com (VERIFIED; the record names no 21700 cell, this is a representative 5 Ah cell)"),
}
WRAP = float(os.environ.get("A06_WRAP", 0.5))          # per side, PVC shrink plus fish paper: TBD (no sheet); applied to W, H and L of the block
JOINT = float(os.environ.get("A06_JOINT", 1.0))         # per section along Y: nickel 0.15 plus insulator ring and weld tolerance: TBD
BASE = {"best": 1.21, "nom": 1.4, "worst": 2.61}   # VHB 5952 1.1 +-10 % (3m-vhb-tapes-family-2018.pdf, VERIFIED); RS 245-556 mat 0.7+-0.1 (leaflet V9322) to 1.4 (sibling 731-366 sheet), so TBD 0.6..1.4
ENCL = dict(wall=2.0, floor=2.0, lid=2.0, boss=5.0, bay_gap=3.0)   # pack_4s.py:12,16,25 (VERIFIED as the design of record)
P_BOARD = dict(W=44.0, L=70.0, T=1.6)   # appendix 32.62 P1 text; P board file H1..H4 at (+-32, +-19) (VERIFIED)
P_TALL = 7.37 + 8.8   # Keystone 3568 body 7.37 (M65p42.pdf) + Littelfuse MINI 297 head 8.8 (littelfuse-297-ficcorp.pdf): 16.17, INFERRED seating
P_XH = 9.8            # JST XH assembled height (jst-exh.pdf p1, VERIFIED); wires exit upward (top entry)
MIN_MOUNT = 1.0       # stand-off of the P board in the no-enclosure packaging: TBD

# ------------------------------------------------------------------ pockets and obstruction zones (x0, x1, y0, y1, z_limit, label, status)
def sq(cx, cy, r): return (cx - r, cx + r, cy - r, cy + r)
EAST = dict(name="east", x=(120.0, 178.0), y=(-120.0, 120.0), zones=[
    (121.57, 131.47, -80.68, -59.32, B_UNDER - 9.25, "J_AB2 2x5 box header, B.Cu (9.1+-0.15, Wurth WR-BHD 61201021621 as the DIN 41651 representative)", "VERIFIED position, header height from a representative part"),
    (120.0, 131.47, -80.68, -55.0, 31.0, "J_AB2 mated IDC socket plus ribbon leaving for A's J_AB2 at (95,-11)", "INFERRED (socket 6.9 body, strain relief, ribbon; no mated drawing)"),
    (*sq(123.0, -87.0, 4.0), B_UNDER - 6.0, "H17 GC 9704 bracket fastener (M4 hole; nut or head below B)", "TBD 1.8..6.0 drop, worst used"),
    (*sq(123.0, -55.0, 4.0), B_UNDER - 6.0, "H18 bracket fastener", "TBD, worst used"),
    (*sq(155.0, -87.0, 4.0), B_UNDER - 6.0, "H19 bracket fastener", "TBD, worst used"),
    (*sq(155.0, -55.0, 4.0), B_UNDER - 6.0, "H20 bracket fastener", "TBD, worst used"),
    (132.62, 156.04, -8.70, 9.38, B_UNDER - 2.5 - float(os.environ.get("A06_LEAD", 1.37)), "WIFISW: six U.FL (mated 2.5 max, Hirose U.FL catalogue Sep 2024) plus a 1.37 mm lead", "VERIFIED 2.5; lead crossing INFERRED"),
    (126.2, 129.8, -2.0, 28.0, B_UNDER - 1.5, "LimeSDR tie strap between S_LIME1 and S_LIME2", "INFERRED 1.5"),
    (137.3, 149.5, 48.3, 61.1, B_UNDER - 2.0, "J_ZBDBG1/2, J_CAM pin tails (top-side 1x5/1x4 headers)", "INFERRED 3.0 tail - 1.6 + fillet"),
    (137.7, 153.3, -37.1, -35.1, B_UNDER - 1.0, "J_LIME receptacle pegs", "INFERRED"),
])
WEST = dict(name="west", x=(-178.0, -120.0), y=(-40.0, 120.0), zones=[
    (-157.78, -120.0, -38.95, -4.62, B_UNDER - 1.6, "IOCTRL logic on B.Cu (U41 LQFP-100, U70..U79 TSSOP-14, 0603)", "LQFP-100 1.6 max INFERRED (JEDEC class)"),
    (-139.88, -133.88, 65.47, 69.38, B_UNDER - 3.2, "C33 1n 2kV C1812 on B.Cu", "TBD part height, 1812 upper bound used"),
    (-139.88, -125.45, 62.77, 69.38, B_UNDER - 0.6, "C29, C30, R9, R10 0603 on B.Cu", "INFERRED"),
    (-161.0, -143.0, 86.0, 92.5, B_UNDER - 2.0, "J_ETH RJ45 tails and pegs (Amphenol RJHSE5380)", "INFERRED, drawing held but not read for tail length"),
    (-132.0, -120.0, 90.5, 94.5, B_UNDER - 2.0, "J_PANEL 2x13 tails", "INFERRED"),
])

# ------------------------------------------------------------------ cross-sections: (cells per section, W, H) in cell diameters
def sections(D):
    h_nest = D * math.sqrt(3) / 2
    return {
        "3x2": (6, 3 * D, 2 * D), "2x2": (4, 2 * D, 2 * D), "3x1": (3, 3 * D, D), "2x1": (2, 2 * D, D),
        "nest3+2": (5, 3 * D, D + h_nest), "nest2+2": (4, 2.5 * D, D + h_nest), "nest2+1": (3, 2 * D, D + h_nest),
    }

def boxes_for(cell, n_cells, sec, bms, pack, base):
    """Component boxes (dx0, dx1, dy0, dy1, ztop) relative to the pack origin, as a tuple of placement variants (the board at either end
    or either side), plus the overall W and L. Packaging: 'enclosure' = pack_4s.py's one-height printed box (2 mm walls, floor, lid, board
    on 5 mm bosses); 'stepped' = the same walls but the board bay only as tall as the board needs; 'minimal' = shrink-wrapped block and a
    separately mounted board, no rigid box (the most generous physical bound)."""
    c = CELLS[cell]; k, W, H = sections(c["D"])[sec]
    n_sec = math.ceil(n_cells / k)
    Lb = n_sec * (c["L"] + JOINT) + 2 * WRAP; Wb = W + 2 * WRAP; Hb = H + 2 * WRAP
    info = dict(n_sec=n_sec, Lb=Lb, Wb=Wb, Hb=Hb)
    if pack in ("enclosure", "stepped"):
        w, fl, lid, boss, gap = ENCL["wall"], ENCL["floor"], ENCL["lid"], ENCL["boss"], ENCL["bay_gap"]
        bay_H = boss + P_BOARD["T"] + P_TALL
        if bms == "end":
            OW = max(Wb, P_BOARD["W"]) + 2 * w
            Lcell = Lb + 2 * w; Lbay = P_BOARD["L"] + 2 * gap
            OL = Lcell + Lbay
            if pack == "enclosure":
                zt = base + max(Hb, bay_H) + fl + lid
                v = (((0, OW, 0, OL, zt),),)
                info["ztop"] = zt; return v, OW, OL, info
            zc = base + Hb + fl + lid; zbay = base + bay_H + fl + lid
            bw = P_BOARD["W"] + 2 * w
            v1 = ((0, Wb + 2 * w, 0, Lcell, zc), (0, bw, Lcell, OL, zbay))            # bay north
            v2 = ((0, bw, 0, Lbay, zbay), (0, Wb + 2 * w, Lbay, OL, zc))              # bay south
            info["ztop"] = max(zc, zbay); return (v1, v2), OW, OL, info
        if bms == "side":
            OW = Wb + 1.0 + P_BOARD["T"] + P_TALL + 2 * w; OL = max(Lb, P_BOARD["L"]) + 2 * w
            zt = base + max(Hb, MIN_MOUNT + P_BOARD["W"]) + fl + lid
            info["ztop"] = zt; return (((0, OW, 0, OL, zt),),), OW, OL, info
        return None
    zb = base + Hb
    if bms == "end":
        bw = P_BOARD["W"]; zt = base + MIN_MOUNT + P_BOARD["T"] + P_TALL
        OW = max(Wb, bw); OL = Lb + 2.0 + P_BOARD["L"]
        v1 = ((0, Wb, 0, Lb, zb), (0, bw, Lb + 2.0, OL, zt))                          # board north of the block
        v2 = ((0, bw, 0, P_BOARD["L"], zt), (0, Wb, P_BOARD["L"] + 2.0, OL, zb))       # board south of the block
        v3 = ((0, Wb, 0, Lb, zb), (OW - bw, OW, Lb + 2.0, OL, zt))
        v4 = ((OW - bw, OW, 0, P_BOARD["L"], zt), (0, Wb, P_BOARD["L"] + 2.0, OL, zb))
        info["ztop"] = max(zb, zt); return (v1, v2, v3, v4), OW, OL, info
    if bms == "side":
        th = P_BOARD["T"] + P_TALL; zt = base + MIN_MOUNT + P_BOARD["W"]
        OW = Wb + 1.0 + th; OL = max(Lb, P_BOARD["L"])
        vs = []
        for board_west in (False, True):
            bx0, bx1 = (0, th) if board_west else (Wb + 1.0, OW)
            kx0, kx1 = (th + 1.0, OW) if board_west else (0, Wb)
            for j in range(0, int(max(0.0, OL - P_BOARD["L"]) / 2.0) + 1):
                y0 = min(j * 2.0, OL - P_BOARD["L"])
                vs.append(((kx0, kx1, 0, Lb, zb), (bx0, bx1, y0, y0 + P_BOARD["L"], zt)))
        info["ztop"] = max(zb, zt); return tuple(vs), OW, OL, info
    if bms == "top":
        zt = zb + 0.5 + P_BOARD["T"] + P_TALL
        OW = max(Wb, P_BOARD["W"]); OL = Lb
        vs = tuple(((0, Wb, 0, Lb, zb), (0, P_BOARD["W"], y0, y0 + P_BOARD["L"], zt)) for y0 in (0.0, Lb - P_BOARD["L"]))
        info["ztop"] = max(zb, zt); return vs, OW, OL, info
    return None

def zclear(pocket, boxes, ox, oy):
    worst = 1e9; who = "B underside (bare)"
    for (x0, x1, y0, y1, zt) in boxes:
        X0, X1, Y0, Y1 = ox + x0, ox + x1, oy + y0, oy + y1
        c = B_UNDER - zt
        if c < worst: worst, who = c, "B underside (bare)"
        for (zx0, zx1, zy0, zy1, zl, lab, st) in pocket["zones"]:
            if X1 > zx0 and X0 < zx1 and Y1 > zy0 and Y0 < zy1:
                c = zl - zt
                if c < worst: worst, who = c, lab
    return worst, who

CHASE = {"east": (120.0, 126.0, -75.0, -57.0), "west": None}   # INFERRED: the floor-level exit for the east-wall RF leads to the clamps at Y -66 under A (E's RF_SITES, gen_pcb_e.py:16), beside J_AB2
def channel(pocket, boxes, ox, oy):
    """RF/harness path left by a placement: free Y at the south and north ends of the pocket, and whether the east chase is free."""
    ys0 = min(oy + b[2] for b in boxes); ys1 = max(oy + b[3] for b in boxes)
    south, north = ys0 - pocket["y"][0], pocket["y"][1] - ys1
    ch = CHASE.get(pocket["name"])
    chase_free = True
    if ch:
        for (x0, x1, y0, y1, zt) in boxes:
            if ox + x1 > ch[0] and ox + x0 < ch[1] and oy + y1 > ch[2] and oy + y0 < ch[3]: chase_free = False
    return south, north, chase_free

def place(pocket, variants, OW, OL):
    (px0, px1), (py0, py1) = pocket["x"], pocket["y"]
    sx, sy = (px1 - px0) - OW, (py1 - py0) - OL
    if sx < 0 or sy < 0: return dict(fit_xy=False, sx=sx, sy=sy)
    best = None; best_ch = None
    for boxes in variants:
        nx, ny = int(sx / 0.25) + 1, int(sy / 0.5) + 1
        for i in range(nx):
            ox = px0 + i * 0.25
            for j in range(ny):
                oy = py0 + j * 0.5
                z, who = zclear(pocket, boxes, ox, oy)
                if best is None or z > best[0]: best = (z, who, ox, oy, boxes)
                s, n, cf = channel(pocket, boxes, ox, oy)
                if (cf or s >= 12.0 or n >= 12.0) and (best_ch is None or z > best_ch[0]): best_ch = (z, who, ox, oy, boxes, s, n, cf)
    s, n, cf = channel(pocket, best[4], best[2], best[3])
    out = dict(fit_xy=True, sx=sx, sy=sy, z=best[0], who=best[1], ox=best[2], oy=best[3], boxes=best[4], south=s, north=n, chase=cf)
    if best_ch: out.update(zc=best_ch[0], whoc=best_ch[1], oxc=best_ch[2], oyc=best_ch[3], southc=best_ch[5], northc=best_ch[6], chasec=best_ch[7])
    else: out.update(zc=None)
    return out

CONFIGS = [("4S3P 18650", "18650", 12), ("4S4P 18650", "18650", 16), ("4S2P 21700", "21700", 8), ("4S3P 21700", "21700", 12)]
rows = []
for (label, cell, n) in CONFIGS:
    for pack in ("enclosure", "stepped", "minimal"):
        for bms in ("end", "side", "top"):
            for sec in sections(CELLS[cell]["D"]):
                k = sections(CELLS[cell]["D"])[sec][0]
                if bms == "top" and sec not in ("3x1", "2x1"): continue
                for bname in ("nom", "worst"):
                    r = boxes_for(cell, n, sec, bms, pack, BASE[bname])
                    if r is None: continue
                    variants, OW, OL, info = r
                    for pk in (EAST, WEST):
                        res = place(pk, variants, OW, OL)
                        rows.append(dict(cfg=label, cell=cell, n=n, pack=pack, bms=bms, sec=sec, k=k, base=bname, pocket=pk["name"], OW=OW, OL=OL, **info, **res))

def fmt(r):
    s = "%-11s %-9s %-4s %-8s base=%-5s %-4s  pack %6.2f x %6.2f (block %d sec, W %.2f L %.2f H %.2f, top Z %.2f)  X spare %6.2f  Y spare %7.2f" % (
        r["cfg"], r["pack"], r["bms"], r["sec"], r["base"], r["pocket"], r["OW"], r["OL"], r["n_sec"], r["Wb"], r["Lb"], r["Hb"], r["ztop"], r["sx"], r["sy"])
    if r["fit_xy"]:
        s += "  Z clear %6.2f at %s  [origin X %.2f Y %.2f]" % (r["z"], r["who"][:60], r["ox"], r["oy"])
        s += "  => %s" % ("FITS" if r["z"] >= 0 else "NO (height)")
        s += " | ends free S %.1f N %.1f chase %s" % (r["south"], r["north"], "free" if r["chase"] else "blocked")
        if r.get("zc") is not None: s += " | with an RF path kept: Z clear %.2f at %s [X %.2f Y %.2f, S %.1f N %.1f chase %s]" % (r["zc"], r["whoc"][:40], r["oxc"], r["oyc"], r["southc"], r["northc"], "free" if r["chasec"] else "blocked")
        else: s += " | no placement keeps an RF path"
    else:
        s += "  => NO (%s)" % ("width" if r["sx"] < 0 else "length")
    return s

if __name__ == "__main__":
    print("B underside Z %.2f; bases %s; wrap %.2f/side; joint %.2f/section; P tallest %.2f (fuse fitted), XH mated %.1f" % (B_UNDER, BASE, WRAP, JOINT, P_TALL, P_XH))
    for r in rows: print(fmt(r))
    print("\nSUMMARY: best result per configuration, packaging and pocket (nominal base)")
    for (label, cell, n) in CONFIGS:
        for pack in ("enclosure", "stepped", "minimal"):
            for pk in ("east", "west"):
                cand = [r for r in rows if r["cfg"] == label and r["pack"] == pack and r["pocket"] == pk and r["base"] == "nom"]
                fits = [r for r in cand if r["fit_xy"] and r["z"] >= 0]
                if fits:
                    b = max(fits, key=lambda r: min(r["z"], r["sx"], r["sy"]))
                    wr = [r for r in rows if r["cfg"] == label and r["pack"] == pack and r["pocket"] == pk and r["base"] == "worst" and r["sec"] == b["sec"] and r["bms"] == b["bms"]][0]
                    print("  %-11s %-9s %-4s FITS: %s  | worst base: %s" % (label, pack, pk, fmt(b)[120:], ("Z clear %.2f" % wr["z"]) if wr["fit_xy"] else "NO"))
                else:
                    near = [r for r in cand if r["fit_xy"]]
                    if near:
                        b = max(near, key=lambda r: r["z"]); print("  %-11s %-9s %-4s NO: best height %.2f (%s %s at %s)" % (label, pack, pk, b["z"], b["sec"], b["bms"], b["who"][:50]))
                    else:
                        b = max(cand, key=lambda r: min(r["sx"], r["sy"])); print("  %-11s %-9s %-4s NO: nearest %s %s X spare %.2f Y spare %.2f" % (label, pack, pk, b["sec"], b["bms"], b["sx"], b["sy"]))
