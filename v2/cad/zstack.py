#!/usr/bin/env python3
"""Board envelopes and the Z stack of the V2 kit, read from the committed KiCad boards (MESHSAT-1357, 27 Sep 2026).

Why this exists: the stack was "INFERRED until the stack is drawn" (v2/docs/ARCHITECTURE.md 7.1) and every part height the case chains used was a
hand copy (panel1450.B16_TALL, frame_seat.py's tall list). This tool reads what the boards carry instead:
  - each board's file is the one its routeflow profile names (v2/ecad/tools/routeflow/<letter>.json, the rule rules_status.py uses; board E5,
    which has no profile, is v2/ecad/pcb-e5-block/); its sha256 is recorded, so a changed board makes this reading stale (test_case_geometry.py);
  - the outline is the board's Edge.Cuts; the holes are its mounting-hole footprints and bare drilled pads; the thickness is its (general (thickness));
  - every footprint gives its side (F.Cu = top, B.Cu = bottom), its place and its plan rectangle (the courtyard, else the pads), and its height is
    the z extent of the 3D model the footprint itself names, taken from v2/cad/zstack-models.json (the KiCad 9 library at kicad-packages3D tag
    9.0.9, each model's sha256 and bounding box, computed on the CAD box by v2/cad/model_bbox.py). Where the footprint names a model file the
    library does not carry, the same package body's model stands in and is labelled SUBSTITUTE; where there is no model at all the height is
    TBD and the part is listed, never guessed;
  - the boards' Z places come from panel1450.STACK (the spacers are unnamed parts, TBD) and the face from panel1450.FACE_TOP_Z.
Parts that are not on any board (the CM5 modules and coolers, the RockBLOCK, the LimeSDR, the M.2 cards, the fans) keep panel1450.B16_TALL's
envelopes with their stated sources; this tool reports which KiCad parts those envelopes cover and which they do not.

Stdlib only: runs on the runner and anywhere Python 3.8+ runs. Usage:
    python3 v2/cad/zstack.py [--json v2/cad/zstack.json] [--report]
Nothing here establishes a fit: the heights are the library models' (nominal bodies), placement is the committed board's, and a part without a
model is TBD. The prototype has not been built."""
import os, sys, re, json, math, hashlib, glob, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HERE, ".."))
ECAD = os.path.join(V2, "ecad")
TOOLS = os.path.join(ECAD, "tools")
sys.path.insert(0, TOOLS)
import panel1450 as L

MODELS_JSON = os.path.join(HERE, "zstack-models.json")

# ------------------------------------------------------------------ where each board sits in the case frame
# KiCad origin of the case frame per board (the generators' OX, OY), the board's local offset in the case frame, a rotation of the local frame
# into the case frame (degrees, counter-clockwise seen from above) and which Z its bottom surface sits at. Every place but P's is a design fact of
# its generator; P's is the pack group of CASE-MARGINS.md M5 (INFERRED until the hold-down is designed).
def _z_of(name):
    z = 0.0
    for n, t in L.STACK:
        if n == name: return round(z, 3)
        z += t
    raise KeyError(name)
PLACES = {
    "e":  dict(origin=(150.0, 110.0), offset=(0.0, 0.0), rot=0.0, z_bottom=_z_of("board E dock strip"), how="gen_pcb_e.py OX, OY; on the dock strip's VHB pads"),
    "e5": dict(origin=(150.0, 110.0), offset=(0.0, 0.0), rot=0.0, z_bottom=round(_z_of("board E dock strip") + 1.6 + 7.4 - 1.6, 3),
               how="gen_pcb_e5.py: face 7.4 above the dock strip on M3 standoffs (the docstring's figure; a 6 mm standoff and 1.6 board give 7.6, INFERRED)"),
    "a":  dict(origin=(150.0, 110.0), offset=(0.0, 0.0), rot=0.0, z_bottom=_z_of("board A"), how="gen_pcb_a.py OX, OY; on the blind-mate gap spacer"),
    "d":  dict(origin=(100.0, 100.0), offset=L.D_OFFSET, rot=0.0, z_bottom=round(L.A_TOP_Z + L.D_STANDOFF, 3),
               how="gen_pcb_d.py OX, OY; its centre at board A's MEZZ_RECT centre (gen_pcb_a.py:51), on 6 mm standoffs"),
    "b":  dict(origin=(150.0, 110.0), offset=(0.0, 0.0), rot=0.0, z_bottom=_z_of("board B"), how="gen_pcb_b.py OX, OY; on the A-to-B bay spacer"),
    "c":  dict(origin=(297.0, 210.0), offset=(0.0, 0.0), rot=0.0, z_bottom=round(L.BACKER_UNDER_Z, 3), how="gen_pcb_c.py OX, OY; 10 mm standoffs under the face plate"),
    "p":  dict(origin=(100.0, 100.0), offset=(round(L.PACK_WEST_X + L.PACK_BLOCK[0] / 2, 3), round(-L.PACK_GROUP_LEN / 2 + 35.0, 3)), rot=90.0, z_bottom=None,
               how="INFERRED: the south end of the pack group centred in Y (CASE-MARGINS.md M5), its long side along the pack; Z not set until the hold-down is designed"),
}
THICKNESS_FROM_STACK = {"e": "board E dock strip", "a": "board A", "b": "board B"}

# Footprints whose file names no model. Each class says what its height is taken as and why; nothing else is given a height. BODYLESS: a land,
# a hole, a slot or a test pad, no body above the copper. CLASS: an upper bound from the package or module class, INFERRED (the maker's sheet is
# the source to read, listed as TBD in the report). MATES: a contact whose height is the mating stack's (the dock and blind-mate windows, which
# the dock tolerance stack owns). PANEL: board C's panel-mount parts, whose bodies hang from the face plate (panel1450.deep_parts, check_pcb_c.py).
# COVERED: a part under a module whose envelope panel1450.B16_MODULES carries (the module's height governs). TBD: none of these.
HEIGHT_CLASSES = [
    (r"^(TestPoint_Pad|MountingHole|Slot_|SolderPad|SolderWire|SolderJumper|LeadLands|WireLands|WireHole|PogoTargets|Mill-Max_0858_target|BackerScrew|FrameScrew|Fiducial)",
     0.0, "BODYLESS", "a land, hole, slot or test pad"),
    (r"^(PowerPAK_SO-8|VSSOP-|Fuse_1812|Texas_R|WQFN-|Skyworks_|nanoSIM|Vishay_VEML7700|Sensirion_DFN|Hirose_FH34)",
     2.0, "CLASS", "SMD package class, 2.0 or less (INFERRED from the package; model not in the library)"),
    (r"^(Ebyte_E22|Ebyte_E72|Quectel_LG290P)", 5.0, "CLASS", "radio module class 5.0 (panel1450's hand envelope 'radio modules', INFERRED; maker drawing TBD)"),
    (r"^Pulse_H5007NL", 7.0, "CLASS", "magnetics 7.0 (panel1450's hand envelope 'T1 magnetics', INFERRED; v2/vendor/pulse/pulse-h5007nl.pdf to read)"),
    (r"^JST_VH_B\dP-VH_.*_Vertical", 16.5, "MAKER", "JST VH catalogue (v2/vendor/connectors/jst-vh-catalogue.pdf, jst-mfg.com eVH.pdf): the top-entry header stands 10.9 "
     "above the board (page 3), 16.5 mated with its VHR housing (page 1); these carry leads, so the mated height counts"),
    (r"^USB_C_Receptacle_HRO_TYPE-C-31-M-12", 3.26, "MAKER", "HRO TYPE-C-31-M-12 drawing rev A (v2/vendor/connectors/hro-type-c-31-m-12.pdf): 3.26 above the board, "
     "unmated (a service port; a mated plug's overmould stands higher, TBD)"),
    (r"^NiceRF_SA868", 3.2, "CLASS", "SA868 module 3.2 (v2/cad/render/scene.py's box, INFERRED)"),
    (r"^M2_[BEM]-Key_Socket", 4.5, "CLASS", "M.2 socket with its card, 4.5 (panel1450's hand envelope 'M.2 cards', INFERRED; the card envelope is derived below)"),
    (r"^(Radiall_SMPMAX|Mill-Max_0858_power_pin|PogoPins)", None, "MATES", "a mating contact: its height is the dock/blind-mate stack's (TBD, not this tool's)"),
    (r"^(PanelSwitch|PanelJack|PanelSounder|ToggleBody|PanelToggle|GuardedToggle)", None, "PANEL", "a panel part hanging from the face plate: panel1450.deep_parts"),
    (r"^(CM5_Conn_|USB3_A_Receptacle)", None, "COVERED", "under a module envelope (the CM5 with its cooler; the LimeSDR Mini)"),
]

# THE MAKER'S MAXIMUM where a WORST-CASE chain reads a part's height (27 Sep 2026, the second review of the case release). `height` above is
# the library model's body, a NOMINAL figure; a tolerance chain that takes it as the part's height at the worst understates the part. Each
# entry here is read off the maker's own sheet in v2/vendor/ (the package table's maximum body height, with its typical beside it), matched
# by the footprint AND the part's value, so another maker's part in the same footprint gets no borrowed figure. frame_seat.py reads
# `height_max` for U51 (M14e and M14g); test_case_geometry.py holds every entry to its board part (the typical equal to the model's height).
# (footprint regex, value regex, maximum, typical, source)
MAKER_MAX = [
    (r"^LQFP-100_14x14mm_P0\.5mm$", r"^STM32H753", 1.60, 1.50,
     "ST DS12117 Rev 9 (STM32H753xI), Table 217 LQFP100 mechanical data, page 322: A typ 1.50, max 1.60 "
     "(v2/vendor/st/st-stm32h753xi-datasheet.pdf)"),
]


def board_file(letter):
    """The board file the board's routeflow profile names (the rule of rules_status._phase_dir); E5 has no profile."""
    if letter == "e5":
        return os.path.join(ECAD, "pcb-e5-block", "pcb-e5-block.kicad_pcb")
    pf = os.path.join(TOOLS, "routeflow", "%s.json" % letter)
    p = json.load(open(pf, encoding="utf-8"))
    d = os.path.join(ECAD, os.path.basename(str(p["project"]).rstrip("/")))
    return os.path.join(d, p["board"] + ".kicad_pcb")


def rel(path):
    return os.path.relpath(path, os.path.normpath(os.path.join(V2, ".."))).replace(os.sep, "/")


# ------------------------------------------------------------------ a small S-expression reader (KiCad 9 board files)
_TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
def sexp(text):
    stack, cur = [], []
    for m in _TOK.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        elif t[0] == '"':
            cur.append(t[1:-1].replace('\\"', '"'))
        else:
            cur.append(t)
    return cur[0]

def kids(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]

def kid(node, name):
    k = kids(node, name)
    return k[0] if k else None

def fnum(x):
    return float(x)


# ------------------------------------------------------------------ geometry helpers
def rot_local(lx, ly, deg):
    """KiCad: a footprint rotated by deg (counter-clockwise on screen, y down) maps local (lx, ly) to board offsets."""
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return lx * c + ly * s, -lx * s + ly * c

def to_case(letter, x, y):
    pl = PLACES[letter]; ox, oy = pl["origin"]
    lx, ly = x - ox, oy - y                      # the board's own frame, Y up
    a = math.radians(pl["rot"]); c, s = math.cos(a), math.sin(a)
    return round(lx * c - ly * s + pl["offset"][0], 4), round(lx * s + ly * c + pl["offset"][1], 4)

def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))

def overlap(a, b):
    return a[2] > b[0] and a[0] < b[2] and a[3] > b[1] and a[1] < b[3]


def model_z_extent(entry, mdl):
    """z range of a library model after the footprint's model scale and rotation (about x and y) and its z offset, mm."""
    lo, hi = entry["min"], entry["max"]
    sc = [1.0, 1.0, 1.0]; rt = [0.0, 0.0, 0.0]; of = [0.0, 0.0, 0.0]
    for k, arr in (("scale", sc), ("rotate", rt), ("offset", of)):
        n = kid(mdl, k)
        if n is not None and kid(n, "xyz") is not None:
            arr[:] = [fnum(v) for v in kid(n, "xyz")[1:4]]
    zs = []
    for x in (lo[0], hi[0]):
        for y in (lo[1], hi[1]):
            for z in (lo[2], hi[2]):
                x1, y1, z1 = x * sc[0], y * sc[1], z * sc[2]
                ax = math.radians(rt[0]); y2, z2 = y1 * math.cos(ax) - z1 * math.sin(ax), y1 * math.sin(ax) + z1 * math.cos(ax)
                ay = math.radians(rt[1]); x3, z3 = x1 * math.cos(ay) + z2 * math.sin(ay), -x1 * math.sin(ay) + z2 * math.cos(ay)
                zs.append(z3 + of[2])
    return min(zs), max(zs)


def read_board(letter, models):
    path = board_file(letter)
    raw = open(path, "rb").read()
    root = sexp(raw.decode("utf-8"))
    gen = kid(root, "general"); thick = fnum(kid(gen, "thickness")[1])
    # the outline: every Edge.Cuts graphic's points (arcs by their three points and their bulge)
    pts = []
    for g in root:
        if not (isinstance(g, list) and g and g[0] in ("gr_line", "gr_arc", "gr_rect", "gr_circle", "gr_poly")): continue
        lay = kid(g, "layer")
        if not lay or lay[1] != "Edge.Cuts": continue
        if g[0] == "gr_circle":
            c = kid(g, "center"); e = kid(g, "end"); cx, cy = fnum(c[1]), fnum(c[2]); r = math.hypot(fnum(e[1]) - cx, fnum(e[2]) - cy)
            pts += [(cx - r, cy - r), (cx + r, cy + r)]
        elif g[0] == "gr_poly":
            for xy in kids(kid(g, "pts"), "xy"): pts.append((fnum(xy[1]), fnum(xy[2])))
        else:
            for k in ("start", "mid", "end"):
                n = kid(g, k)
                if n: pts.append((fnum(n[1]), fnum(n[2])))
    case_pts = [to_case(letter, x, y) for x, y in pts]
    outline = bbox(case_pts)
    parts, holes, tbd = [], [], []
    for fp in kids(root, "footprint"):
        lib = fp[1]; side = "top" if kid(fp, "layer")[1] == "F.Cu" else "bottom"
        at = kid(fp, "at"); fx, fy = fnum(at[1]), fnum(at[2]); frot = fnum(at[3]) if len(at) > 3 else 0.0
        ref = val = ""
        for pr in kids(fp, "property"):
            if pr[1] == "Reference": ref = pr[2]
            elif pr[1] == "Value": val = pr[2]
        # plan: the courtyard, else the pads
        cy = []
        for g in fp:
            if not (isinstance(g, list) and g and g[0] in ("fp_line", "fp_rect", "fp_poly", "fp_circle", "fp_arc")): continue
            lay = kid(g, "layer")
            if not lay or not lay[1].endswith("CrtYd"): continue
            if g[0] == "fp_poly":
                for xy in kids(kid(g, "pts"), "xy"): cy.append((fnum(xy[1]), fnum(xy[2])))
            elif g[0] == "fp_circle":
                c = kid(g, "center"); e = kid(g, "end"); r = math.hypot(fnum(e[1]) - fnum(c[1]), fnum(e[2]) - fnum(c[2]))
                cy += [(fnum(c[1]) - r, fnum(c[2]) - r), (fnum(c[1]) + r, fnum(c[2]) + r)]
            else:
                for k in ("start", "mid", "end"):
                    n = kid(g, k)
                    if n: cy.append((fnum(n[1]), fnum(n[2])))
        pads = []
        for pd in kids(fp, "pad"):
            pa = kid(pd, "at"); sz = kid(pd, "size"); px, py = fnum(pa[1]), fnum(pa[2]); w, h = fnum(sz[1]), fnum(sz[2])
            r = max(w, h) / 2
            pads += [(px - r, py - r), (px + r, py + r)]
            dr = kid(pd, "drill")
            if dr is not None and pd[2] in ("np_thru_hole",) or (dr is not None and lib.startswith("MountingHole")):
                d = [x for x in dr[1:] if not isinstance(x, list) and x != "oval"]
                if d:
                    ox_, oy_ = rot_local(px, py, frot); hx, hy = to_case(letter, fx + ox_, fy + oy_)
                    holes.append(dict(ref=ref, x=hx, y=hy, drill=fnum(d[0]), what=val))
        local = cy or pads
        if not local: continue
        corners = []
        for x, y in [(min(p[0] for p in local), min(p[1] for p in local)), (max(p[0] for p in local), min(p[1] for p in local)),
                     (max(p[0] for p in local), max(p[1] for p in local)), (min(p[0] for p in local), max(p[1] for p in local))]:
            dx, dy = rot_local(x, y, frot); corners.append(to_case(letter, fx + dx, fy + dy))
        rect = [round(v, 3) for v in bbox(corners)]
        mdl_nodes = kids(fp, "model")
        height = None; src = None; tail = 0.0; model = None
        for mdl in mdl_nodes:
            mp = mdl[1].replace("${KICAD9_3DMODEL_DIR}/", "")
            e = models.get(mp)
            if not e: continue
            if "error" in e:
                model = mp; src = "TBD: " + e["error"].split(":")[0]; continue
            zlo, zhi = model_z_extent(e, mdl)
            if height is None or zhi > height:
                height, model = round(zhi, 3), mp
                src = "SUBSTITUTE %s" % e["substitute"] if "substitute" in e else "model"
                tail = round(max(0.0, -zlo - thick), 3)      # a through-hole lead standing out of the far side
        klass = None
        if height is None:
            for pat, h, k, why in HEIGHT_CLASSES:
                if re.match(pat, lib):
                    klass = k; height = h
                    src = "%s: %s" % (k, why) if src is None else "%s; %s: %s" % (src, k, why)
                    break
            if src is None: src = "TBD: no 3D model in the footprint"
            if height is None and klass not in ("MATES", "PANEL", "COVERED"): tbd.append(ref)
        parts.append(dict(ref=ref, lib=lib, value=val[:60], side=side, rect=rect, rot=frot, height=height, far_tail=tail, source=src, model=model,
                          klass=klass or ("MODEL" if model and not str(src).startswith("TBD") else "TBD")))
        for pat_lib, pat_val, h_max, h_typ, why in MAKER_MAX:
            if re.match(pat_lib, lib) and re.match(pat_val, val):
                parts[-1].update(height_max=h_max, height_typ=h_typ, height_max_source=why)
                break
    return dict(letter=letter, file=rel(path), sha256=hashlib.sha256(raw).hexdigest(), thickness=thick, outline=[round(v, 3) for v in outline],
                holes=sorted(holes, key=lambda h: (h["x"], h["y"])), parts=parts, tbd=tbd)


# ------------------------------------------------------------------ the stack and its bays
def z_surfaces(b):
    pl = PLACES[b["letter"]]
    if pl["z_bottom"] is None: return None, None
    return pl["z_bottom"], round(pl["z_bottom"] + b["thickness"], 3)

def tallest(b, side, region=None):
    best = None
    for p in b["parts"]:
        if p["side"] != side or p["height"] is None: continue
        if region and not overlap(p["rect"], region): continue
        if best is None or p["height"] > best["height"]: best = p
    return best

def facing(lower, upper, gap, region, note, mates=()):
    """Every overlapping pair of a lower board's top parts and an upper board's bottom parts inside region: the tightest clearances."""
    lo = [p for p in lower["parts"] if p["side"] == "top" and p["height"] is not None and overlap(p["rect"], region)] if lower else []
    up = [p for p in upper["parts"] if p["side"] == "bottom" and p["height"] is not None and overlap(p["rect"], region)] if upper else []
    rows = []
    for a in lo:
        for b in up:
            if not overlap(a["rect"], b["rect"]): continue
            mate = any(a["ref"].startswith(m[0]) and b["ref"].startswith(m[1]) for m in mates)
            rows.append(dict(lower=a["ref"], lower_h=a["height"], upper=b["ref"], upper_h=b["height"], clearance=round(gap - a["height"] - b["height"], 3), mate=mate))
    rows.sort(key=lambda r: r["clearance"])
    one_side = []
    for p in lo:
        one_side.append((round(gap - p["height"], 3), p["ref"], "lower top", p["height"]))
    for p in up:
        one_side.append((round(gap - p["height"], 3), p["ref"], "upper bottom", p["height"]))
    one_side.sort()
    return dict(gap=round(gap, 3), region=[round(v, 3) for v in region], note=note, pairs=rows[:12], n_pairs=len(rows),
                tightest_single=[dict(clearance=c, ref=r, where=w, height=h) for c, r, w, h in one_side[:6]])


# panel1450.B16_TALL as it stood from 9 to 27 September 2026 (hand-typed from the 7 to 9 Sep floor plan, appendix 32.58, 32.59, 32.85). Kept only
# so the report can show what the board reading corrected; nothing reads it for a verdict.
LEGACY_B16_TALL = [((-93.0, 32.0, -52.0, 88.0), 21.0, "CM5 slot 1 heatsink"), ((-23.0, 32.0, 18.0, 88.0), 21.0, "CM5 slot 2 heatsink"), ((47.0, 32.0, 88.0, 88.0), 21.0, "CM5 slot 3 heatsink"),
    ((-87.5, 48.0, -57.5, 78.0), 30.0, "CM5 slot 1 fan"), ((-17.5, 48.0, 12.5, 78.0), 30.0, "CM5 slot 2 fan"), ((52.5, 48.0, 82.5, 78.0), 30.0, "CM5 slot 3 fan"),
    ((-162.0, 81.0, -142.0, 98.0), 14.0, "J_ETH RJ45"), ((-161.5, 58.5, -142.5, 77.5), 7.0, "T1 magnetics"), ((-137.0, 86.0, -95.0, 98.0), 9.5, "J_PANEL 2x13"),
    ((130.0, -43.0, 161.0, 45.0), 12.0, "LimeSDR Mini in J_LIME"), ((113.0, -99.0, 165.0, -43.0), 21.0, "RockBLOCK 9704 on its bracket"), ((96.0, -100.0, 113.0, -86.0), 7.0, "J_HDMI"),
    ((-152.0, -97.0, -116.0, -69.0), 10.0, "west headers J_54V, J_QMX, F3"), ((144.0, 55.0, 148.0, 67.0), 9.5, "J_CAM header"), ((125.5, 45.5, 162.0, 67.0), 5.0, "radio modules"),
    ((-98.0, -97.0, 94.0, -21.0), 6.0, "slot columns: switches, hubs, rails, M.2 sockets"), ((-35.0, -30.0, 91.0, 31.0), 4.5, "M.2 cards")]


M2_CARD_LEN = {"2242": 42.0, "2230": 30.0, "3052": 52.0}   # the M.2 form factor in each socket's name (card width 22, 30 for 3052)
def m2_cards(b):
    """The M.2 card over each socket: from the socket's courtyard centre along the direction the card lies at the socket's rotation (at 0 the
    card lies toward case -Y, as panel1450's hand envelope 'M.2 cards' has it), 22 wide (30 for 3052), height 4.5 (the hand class)."""
    out = []
    for p in b["parts"]:
        m = re.match(r"M2_([BEM])-Key_Socket_(\d{4})", p["lib"])
        if not m or p["side"] != "top": continue
        size = m.group(2); L_ = M2_CARD_LEN[size]; W_ = 30.0 if size == "3052" else 22.0
        cx, cy = (p["rect"][0] + p["rect"][2]) / 2, (p["rect"][1] + p["rect"][3]) / 2
        rot = p.get("rot", 0.0) % 360
        dx, dy = {0.0: (0, -1), 90.0: (1, 0), 180.0: (0, 1), 270.0: (-1, 0)}.get(round(rot, 0), (0, -1))
        if dx == 0:
            r = (cx - W_ / 2, min(cy, cy + dy * L_), cx + W_ / 2, max(cy, cy + dy * L_))
        else:
            r = (min(cx, cx + dx * L_), cy - W_ / 2, max(cx, cx + dx * L_), cy + W_ / 2)
        out.append(dict(rect=[round(v, 3) for v in r], h=4.5, name="M.2 card in %s (%s)" % (p["ref"], size),
                        source="card over the committed socket %s; height the hand class 4.5 (INFERRED)" % p["ref"], status="CLASS"))
    return out


def b16_envelopes(b):
    """What stands on B's top side, for the face gates (check_pcb_c.py through panel1450.B16_TALL): the module envelopes panel1450.B16_MODULES
    carries (anchored by hand; the report checks their anchors), the M.2 cards over the committed sockets, and every part of the committed board
    3.0 mm or taller by its model or its class. Parts with no height (TBD) are listed apart and are not in the list."""
    out = [dict(rect=list(r), h=h, name=n, source=src, status="MODULE") for r, h, n, src in L.B16_MODULES]
    out += m2_cards(b)
    for p in b["parts"]:
        if p["side"] != "top" or p["height"] is None or p["height"] < 3.0: continue
        out.append(dict(rect=p["rect"], h=p["height"], name="%s %s" % (p["ref"], p["lib"]), source=p["source"] if p["source"] != "model" else "model %s" % p["model"],
                        status=p["klass"]))
    return out


def envelope_check(b, envelopes):
    """B's top parts against an envelope list [(rect, h, name)]: every part 3.0 mm or taller must lie inside an envelope at least as tall, and
    every part with no height (TBD) inside some envelope; the verdict per part."""
    out = []
    for p in b["parts"]:
        if p["side"] != "top" or p["klass"] in ("BODYLESS", "PANEL", "MATES"): continue
        cover = [(h, n) for r, h, n in envelopes if overlap(p["rect"], r)]
        if p["height"] is None:
            out.append(dict(ref=p["ref"], lib=p["lib"], height=None, covered_by=[n for h, n in cover],
                            verdict="TBD height, inside an envelope" if cover else "TBD height, NO envelope covers it"))
        elif p["height"] >= 3.0:
            ok = any(h + 1e-6 >= p["height"] for h, n in cover)
            out.append(dict(ref=p["ref"], lib=p["lib"], height=p["height"], covered_by=[n for h, n in cover],
                            verdict="enveloped" if ok else ("TALLER than every envelope over it" if cover else "NO envelope covers it")))
    return out


def anchors(b):
    """Each module envelope of panel1450.B16_MODULES against the committed parts that carry it."""
    want = {"CM5 slot 1": ("U30A", "U30B"), "CM5 slot 2": ("U31A", "U31B"), "CM5 slot 3": ("U32A", "U32B"), "LimeSDR": ("J_LIME",), "RockBLOCK": ("H17", "H18", "H19", "H20")}
    byref = {p["ref"]: p for p in b["parts"]}; out = []
    for r, h, n, src in L.B16_MODULES:
        for key, refs in want.items():
            if not n.startswith(key): continue
            if n.endswith(" fan"):
                ps = [byref.get(x) for x in refs]
                if None in ps: out.append(dict(module=n, ref="+".join(refs), verdict="ANCHOR ABSENT on the board")); continue
                cx = sum((p["rect"][0] + p["rect"][2]) / 2 for p in ps) / len(ps); cy = sum((p["rect"][1] + p["rect"][3]) / 2 for p in ps) / len(ps)
                inside = r[0] <= cx <= r[2] and r[1] <= cy <= r[3]
                out.append(dict(module=n, ref="midpoint of %s" % "+".join(refs), centre=[round(cx, 2), round(cy, 2)],
                                verdict="anchor inside" if inside else "ANCHOR OUTSIDE the envelope"))
                continue
            for ref in refs:
                p = byref.get(ref)
                if p is None: out.append(dict(module=n, ref=ref, verdict="ANCHOR ABSENT on the board")); continue
                cx, cy = (p["rect"][0] + p["rect"][2]) / 2, (p["rect"][1] + p["rect"][3]) / 2
                inside = r[0] <= cx <= r[2] and r[1] <= cy <= r[3]
                out.append(dict(module=n, ref=ref, centre=[round(cx, 2), round(cy, 2)], verdict="anchor inside" if inside else "ANCHOR OUTSIDE the envelope"))
    return out


def build():
    models = json.load(open(MODELS_JSON, encoding="utf-8"))["models"]
    boards = {k: read_board(k, models) for k in ("e", "e5", "a", "d", "b", "c", "p")}
    for k, b in boards.items():
        z0, z1 = z_surfaces(b); b["z_bottom"], b["z_top"] = z0, z1; b["place"] = PLACES[k]["how"]
        b["tallest_top"] = tallest(b, "top"); b["tallest_bottom"] = tallest(b, "bottom")
    A, B, D, E, E5 = boards["a"], boards["b"], boards["d"], boards["e"], boards["e5"]
    d_region = D["outline"]
    bays = {
        "floor under E (E's underside parts on the VHB pads)": facing(None, E, E["z_bottom"], E["outline"], "E's bottom parts against the case floor"),
        "E to A (blind-mate gap)": facing(E, A, A["z_bottom"] - E["z_top"], A["outline"], "13.4 gap; the SMP-MAX plugs and the E5 block mate across it",
                                           mates=(("J_BM", "J_BM"),)),
        "E5 to A (dock contacts)": facing(E5, A, A["z_bottom"] - E5["z_top"], E5["outline"], "the block's targets under A's J_DOCK spring pins (mate)"),
        "A to D (mezzanine standoffs)": facing(A, D, D["z_bottom"] - A["z_top"], d_region, "6.0 standoffs; J_AB2 is W4-F17"),
        "A to B outside D (bay)": facing(A, B, B["z_bottom"] - A["z_top"], A["outline"], "31.3 bay (parts under D's outline are the next two rows)"),
        "D to B": facing(D, B, B["z_bottom"] - D["z_top"], d_region, "above the mezzanine"),
        "B to C backer ring": facing(B, boards["c"], boards["c"]["z_bottom"] - B["z_top"], boards["c"]["outline"], "check_pcb_c.py gates this with B16_TALL"),
    }
    # the parts on B's top inside the monitor's footprint, against the monitor body's bottom (the KiCad side of M1; the heatsinks are modules)
    X = L.XENARC; gx, gy = X["c"]; bw, bh = X["body"]; foot = (gx - bw / 2, gy - bh / 2, gx + bw / 2, gy + bh / 2)
    body_bottom = L.FACE_TOP_Z - X["height"]
    under_mon = sorted([(round(body_bottom - (B["z_top"] + p["height"]), 3), p["ref"], p["height"]) for p in B["parts"]
                        if p["side"] == "top" and p["height"] is not None and overlap(p["rect"], foot)])[:6]
    # B's underside over the east pack pocket (M6's subject)
    pocket = (L.PACK_WEST_X, -L.PACK_GROUP_LEN / 2, L.PACK_WEST_X + L.PACK_BLOCK[0], L.PACK_GROUP_LEN / 2)
    over_pack = tallest(B, "bottom", pocket)
    out = dict(
        what="MeshSat V2 board envelopes and Z stack, read from the committed KiCad boards by v2/cad/zstack.py (MESHSAT-1357). Nominal library-model "
             "bodies at the committed placements; nothing here establishes a fit.",
        panel1450=dict(sha256=hashlib.sha256(open(os.path.join(TOOLS, "panel1450.py"), "rb").read()).hexdigest(),
                       FACE_TOP_Z=L.FACE_TOP_Z, B_TOP_Z=L.B_TOP_Z, STACK=L.STACK, LEG_TOP_Z=L.LEG_TOP_Z),
        models=dict(file=rel(MODELS_JSON), sha256=hashlib.sha256(open(MODELS_JSON, "rb").read()).hexdigest()),
        boards=boards, bays=bays,
        monitor=dict(body_bottom_z=round(body_bottom, 3), footprint=foot, b_parts_under=[dict(clearance=c, ref=r, height=h) for c, r, h in under_mon]),
        pack_pocket=dict(region=pocket, b_underside_tallest=over_pack, lowest_z=round(B["z_bottom"] - over_pack["height"], 3) if over_pack else None),
        b16_envelopes=b16_envelopes(B),
        b16_module_anchors=anchors(B))
    out["b16_check"] = envelope_check(B, [(tuple(e["rect"]), e["h"], e["name"]) for e in out["b16_envelopes"]])
    out["b16_legacy_check"] = envelope_check(B, LEGACY_B16_TALL)
    return out


def report(z):
    lines = []
    w = lines.append
    w("Z STACK FROM THE COMMITTED BOARDS (case frame, mm above the cavity floor)")
    for k in ("e", "e5", "a", "d", "b", "c", "p"):
        b = z["boards"][k]
        tt, tb = b["tallest_top"], b["tallest_bottom"]
        w("  %-2s %-38s sha %s  outline X %.1f..%.1f Y %.1f..%.1f  t %.2f  Z %s..%s" % (
            k.upper(), b["file"], b["sha256"][:12], b["outline"][0], b["outline"][2], b["outline"][1], b["outline"][3], b["thickness"],
            "%.2f" % b["z_bottom"] if b["z_bottom"] is not None else "TBD", "%.2f" % b["z_top"] if b["z_top"] is not None else "TBD"))
        w("      tallest top %s, tallest bottom %s; %d parts, %d TBD heights, %d holes" % (
            "%s %.2f (%s)" % (tt["ref"], tt["height"], tt["lib"]) if tt else "none", "%s %.2f (%s)" % (tb["ref"], tb["height"], tb["lib"]) if tb else "none",
            len(b["parts"]), len(b["tbd"]), len(b["holes"])))
    w("\nBAYS (clearance = gap - lower part - upper part, where their plan rectangles overlap)")
    for name, bay in z["bays"].items():
        w("  %s: gap %.2f (%s)" % (name, bay["gap"], bay["note"]))
        for r in bay["pairs"][:4]:
            w("     %-10s %6.2f  under %-10s %6.2f  clearance %+7.2f%s" % (r["lower"], r["lower_h"], r["upper"], r["upper_h"], r["clearance"], "  (mate)" if r["mate"] else ""))
        for s in bay["tightest_single"][:2]:
            w("     single: %-10s %-12s h %6.2f  leaves %+7.2f" % (s["ref"], s["where"], s["height"], s["clearance"]))
    m = z["monitor"]
    w("\nB's top parts in the monitor's footprint against its body bottom Z %.2f: %s" % (m["body_bottom_z"], ", ".join("%s h %.2f %+.2f" % (x["ref"], x["height"], x["clearance"]) for x in m["b_parts_under"])))
    pp = z["pack_pocket"]
    if pp["b_underside_tallest"]:
        w("B's underside over the east pack pocket: tallest %s %.2f, lowest Z %.2f" % (pp["b_underside_tallest"]["ref"], pp["b_underside_tallest"]["height"], pp["lowest_z"]))
    w("\nB16_TALL (the face gates' list) against B's own parts: %d envelopes (%d modules, %d M.2 cards, %d board parts 3.0 mm or taller)" % (
        len(z["b16_envelopes"]), sum(1 for e in z["b16_envelopes"] if e["status"] == "MODULE"), sum(1 for e in z["b16_envelopes"] if e["name"].startswith("M.2 card")),
        sum(1 for e in z["b16_envelopes"] if e["status"] not in ("MODULE",) and not e["name"].startswith("M.2 card"))))
    bad = [r for r in z["b16_check"] if r["verdict"] not in ("enveloped", "TBD height, inside an envelope")]
    for r in bad: w("  %-10s %-44s %s  %s" % (r["ref"], r["lib"][:44], "h %.2f" % r["height"] if r["height"] is not None else "h TBD", r["verdict"]))
    w("  %s" % ("every part 3.0 mm or taller is enveloped, every TBD part lies inside an envelope" if not bad else "%d parts NOT covered" % len(bad)))
    for a in z["b16_module_anchors"]:
        if a["verdict"] != "anchor inside": w("  module %s: %s %s" % (a["module"], a["ref"], a["verdict"]))
    w("  module anchors: %d of %d inside their envelopes" % (sum(1 for a in z["b16_module_anchors"] if a["verdict"] == "anchor inside"), len(z["b16_module_anchors"])))
    w("\nThe hand list of 9 Sep 2026 (LEGACY_B16_TALL) against the same board, for the record:")
    for r in z["b16_legacy_check"]:
        if r["verdict"] not in ("enveloped", "TBD height, inside an envelope"):
            w("  %-10s %-44s %s  %s" % (r["ref"], r["lib"][:44], "h %.2f" % r["height"] if r["height"] is not None else "h TBD", r["verdict"]))
    w("\nTBD heights (no model, no class) per board:")
    for k in ("e", "e5", "a", "d", "b", "c", "p"):
        b = z["boards"][k]
        if b["tbd"]: w("  %s: %s" % (k.upper(), ", ".join("%s (%s)" % (p["ref"], p["lib"]) for p in b["parts"] if p["ref"] in b["tbd"])))
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    z = build()
    if a.json:
        open(a.json, "w", encoding="utf-8").write(json.dumps(z, indent=1, sort_keys=True) + "\n")
    if a.report or not a.json:
        print(report(z))
