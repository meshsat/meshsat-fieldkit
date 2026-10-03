#!/usr/bin/env python3
"""l7r2_items.py: Layer 7 record l7r2 (MESHSAT-1357, 3 October 2026, round 2): the Layer 7 items other layers assigned, each judged on
its makers' drawings with the dimension chain where fit is the question:
  1. the sealed RJ45 and its shield path to the connector plate (record l8gnd F01; Layer 5 IF-EXT-ETH);
  2. the bonding strap, its lugs and the stud (record l8gnd F07; IF-A-CHASSIS);
  3. the right-angle SMA plug at the arrestors (CASE-MARGINS M17g, M17x; IF-AE-RF);
  4. the fans' lead terminations (IF-E-FANS, IF-B-FANS), the cooler fan's fit to the backer (record l7pwr F-L7-03) and its bracket;
  5. J_AB2 and the MAIN lead's lengths and W4-F17 (IF-AB-WALL, IF-AC-MAINSW).
PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built or measured. MAKER a printed figure (inputs/makers-drawings-r2-2026-10-03.md
transcribes each with its document's sha256), MODELED this script's arithmetic, INFERRED a reading not printed as such, ASSUMPTION a
stated assumption, NOT READ a figure no held document prints. Every input is pinned by sha256. No generator, CAD file, registry or other
record is edited: the CAD changes are release-guarded drafts beside this script. Output: `python3 v2/docs/records/l7r2/l7r2_items.py`
from the repository root (the committed .out is regenerated only through _bin/regen_out.py)."""
import hashlib
import importlib.util
import itertools
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PINS = {
    "drawings": "v2/docs/records/l7r2/inputs/makers-drawings-r2-2026-10-03.md",
    "prices": "v2/docs/records/l7r2/inputs/findchips-r2-2026-10-03.json",
    "l5r2_tbd": "v2/docs/records/l7r2/inputs/l5r2-tbd-layer7-rows-6902db8f.md",
    "l8gnd": "v2/docs/records/l7r2/inputs/l8gnd-h1-f01-f07-226e9143.md",
    "l8gnd_land": "v2/docs/records/l7r2/inputs/l8gnd-ChassisLug_M4_CHASSIS-226e9143.kicad_mod",
    "l8r2_fan": "v2/docs/records/l7r2/inputs/l8r2-cooler-header-a441651a.md",
    "panel": "v2/ecad/tools/panel1450.py",
    "frame_seat": "v2/vendor/peli/frame_seat.py",
    "gen_a3": "v2/ecad/tools/gen_pcb_a3.py",
    "gen_a": "v2/ecad/tools/gen_pcb_a.py",
    "gen_b3": "v2/ecad/tools/gen_pcb_b3.py",
    "gen_e3": "v2/ecad/tools/gen_pcb_e3.py",
    "gen_sch_e": "v2/ecad/tools/gen_sch_e.py",
    "margins": "v2/docs/CASE-MARGINS.md",
    "assembly": "v2/docs/ASSEMBLY.md",
    "px0833": "v2/vendor/bulgin/bulgin-px0833-sealed-rj45-coupler.pdf",
    "amph_iii": "v2/vendor/d38999/amphenol-d38999-iii-federal.pdf",
    "cutouts": "v2/vendor/d38999/glenair-series-iii-iv-panel-cutouts.pdf",
    "cooler": "v2/vendor/cm5/rpi-cm5-cooler-product-brief-2024-12.pdf",
    "wurth_hdr": "v2/vendor/connectors/wurth-wr-bhd-box-header-61201021621.pdf",
}
T_MACH, T_JACK, MIN_MECH, BAND_MIN = 0.10, 0.30, 1.0, 3.0      # frame_seat.py: machined place, marked hole, rigid minimum; M14m's gasket band
M3_MIN, M4_MIN = 2.874, 3.838                                   # frame_seat.py: the smallest M3 and M4 majors
SW_R = 5.0                                                      # frame_seat.py: the bonded sealing washer 10 across under each plate screw
U51_H, M14E_WORST_LESS = 1.60, 1.07                             # frame_seat.py / CASE-MARGINS M14e: U51's maximum body, M14e's nominal-to-worst
A_INSIDE_TOP = 8.0                                              # panel1450 CONN_ITEMS A: the patch plug body +-8 (INFERRED there)
HOLE_SAW = 32.0                                                 # ASSUMPTION: the wall hole for a shell 17 body (the 1.1875 in thread, 30.16 major, plus float)


def refuse(msg):
    sys.stderr.write("l7r2_items: %s; refusing\n" % msg)
    sys.exit(3)


def sha_of(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def text(rel):
    return open(os.path.join(TOP, rel), encoding="utf-8").read()


def need(t, pat, what, flags=re.M | re.S):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s not found" % what)
    return m


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sys.path.insert(0, os.path.dirname(os.path.join(TOP, rel)))
    try:
        sp.loader.exec_module(m)
    finally:
        sys.path.pop(0)
    return m


def pdf(rel):
    import subprocess
    r = subprocess.run(["pdftotext", "-layout", os.path.join(TOP, rel), "-"], capture_output=True, text=True)
    if r.returncode:
        refuse("pdftotext could not read %s" % rel)
    return r.stdout


# ---------------------------------------------------------------- the readings
def readings(R):
    d = " ".join(text(PINS["drawings"]).split())   # whitespace collapsed: the transcription wraps its lines
    D = {}
    D["g_b_max"] = float(need(d, r"\*\*B square 1\.323 \(([\d.]+)\) max", "233-330 B").group(1))
    D["g_holes"] = float(need(d, r"\*\*H holes 0\.136 \(([\d.]+)\)", "233-330 H").group(1))
    D["g_c"] = float(need(d, r"C bsc 1\.062 \(([\d.]+)\)", "233-330 C").group(1))
    D["g_rear"] = float(need(d, r"\*\*\.650 \(([\d.]+)\) / \.600", "233-330 rear").group(1))
    D["g_thread_in"] = float(need(d, r"shell 17 \*\*([\d.]+)-\.1P", "233-330 thread").group(1))
    need(d, r"\*\*Not printed:\*\* a voltage or current rating; whether the RJ45 jacks' shields are joined to the shell", "233-330 gaps")
    D["px_v"] = float(need(d, r"\*\*Voltage Max (\d+)V\*\*", "PX0833 voltage").group(1))
    D["px_ring"] = float(need(d, r"Diameter Over Coupling Ring 38\.1mm", "PX ring") and 38.1)
    need(d, r"Body Material \*\*SS 304\*\*", "PX0888 body")
    D["ltw_v"] = tuple(float(x) for x in need(d, r"\*\*Operating voltage (\d+) ~ (\d+)V\*\*", "LTW voltage").groups())
    D["ltw_panel"] = float(need(d, r"Without Cap: ([\d.]+)\"\*\*", "LTW panel").group(1))
    need(d, r"\*\*Shielded: \"Plastic, Shielded\"\*\*", "LTW shield")
    D["rad_reach"] = float(need(d, r"mating axis to the ferrule's end \*\*([\d.]+)\*\*", "Radiall reach").group(1))
    D["rad_ferrule"] = float(need(d, r"ferrule \*\*diameter ([\d.]+)\*\*", "Radiall ferrule").group(1))
    D["rad_height"] = float(need(d, r"nut's face \*\*([\d.]+)\*\*", "Radiall height").group(1))
    D["rad_axis_nut"] = float(need(d, r"the cable axis \*\*(\d+)\*\* above the nut's face", "Radiall axis").group(1))
    D["rad_axis_ref"] = float(need(d, r"and \*\*([\d.]+)\*\* above the reference plane", "Radiall ref").group(1))
    D["rad_hex"] = float(need(d, r"crimp tool hexagon \*\*([\d.]+)\*\*", "Radiall hex").group(1))
    D["rad_v"] = float(need(d, r"\*\*voltage rating (\d+) Veff maxi\*\*", "Radiall V").group(1))
    r4 = need(d, r"stud #8 / M4: \*\*d2 ([\d.]+), B ([\d.]+), L ([\d.]+), F ([\d.]+)\*\*", "R5.5-4")
    r6 = need(d, r"stud 1/4 / M6: \*\*d2 ([\d.]+), B ([\d.]+), L ([\d.]+), F ([\d.]+)\*\*", "R5.5-6")
    D["r4"] = tuple(float(x) for x in r4.groups()); D["r6"] = tuple(float(x) for x in r6.groups())
    D["lug_t"] = float(need(d, r"\*\*T ([\d.]+)\*\*; 500 per box", "lug T").group(1))
    D["lug_awg"] = need(d, r"applicable wire AWG 12 to 10 \(([\d.]+) to ([\d.]+) mm2\)", "lug wire").groups()
    D["ph_temp"] = tuple(float(x) for x in need(d, r"\*\*temperature range (-?\d+) to \+(\d+) C\*\* \(including", "PH temp").groups())
    D["ph_awg"] = need(d, r"contacts \*\*SPH-002T-P0\.5S AWG #(\d+) to #(\d+)\*\*", "PH awg").groups()
    D["sh_temp"] = tuple(float(x) for x in need(d, r"\*\*temperature range (-?\d+) to \+(\d+) C\*\*; \*\*applicable wire AWG #32 to #28\*\*", "SH temp").groups())
    D["sh_awg"] = ("32", "28")
    D["q17"] = float(need(d, r"\*\*shell 17 1\.406 \(([\d.]+)\)\*\*", "Q17").group(1))
    D["cut_a17"] = float(need(d, r"A dia \(rear panel mount\)\s+\*\*1\.219 \(([\d.]+)\)\*\*", "cutout 17").group(1))
    # the same figures read back from the held sheets in the tree (MAKER), so the transcription cannot drift from them
    amph = pdf(PINS["amph_iii"]); cut = pdf(PINS["cutouts"]); px = pdf(PINS["px0833"])
    need(amph, r"17\s+E\s+1\.1875\s+1\.406\s+17\s+E\s+35\.7", "Amphenol shell 17 Q")
    need(cut, r"E\s+16-17\s+1\.219 \(30\.96\)\s+1\.016 \(25\.81\)", "Glenair cut-out row E")
    need(px, r"Voltage Max:\s+42V", "PX0833 voltage on its sheet")
    need(px, r"Body Material:\s+Polyester \(PET\)", "PX0833 body on its sheet")
    R["D"] = D


# ---------------------------------------------------------------- 1. the connector plate with each RJ45 candidate
def plate(R):
    P = load("panel1450_l7r2", PINS["panel"])
    items = {it["key"]: dict(it) for it in P.CONN_ITEMS}
    plateg = P.CONN_PLATE
    D = R["D"]
    fl = {"A": (3.35 - M3_MIN) / 2, "C": (3.45 - M3_MIN) / 2, "B": 0.30, "E": (10.5 - 9.838) / 2, "D": (3.35 - M3_MIN) / 2,
          "F": (6.4 - 5.794) / 2, "screw": (4.5 - M4_MIN) / 2}

    def shp(it, kind):
        s = it[kind]
        return (s[0], s[1] / 2) if s[0] == "sq" else ("c", s[1] / 2)

    def gap(pa, sa, pb, sb):
        def box(p, h): return (p[0] - h, p[1] - h, p[0] + h, p[1] + h)
        if sa[0] == "sq" and sb[0] == "sq":
            A, B = box(pa, sa[1]), box(pb, sb[1])
            dx = max(B[0] - A[2], A[0] - B[2], 0.0); dz = max(B[1] - A[3], A[1] - B[3], 0.0)
            return math.hypot(dx, dz) if (dx > 0 and dz > 0) else max(B[0] - A[2], A[0] - B[2], B[1] - A[3], A[1] - B[3])
        if sa[0] == "c" and sb[0] == "c":
            return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) - sa[1] - sb[1]
        if sa[0] == "c":
            pa, sa, pb, sb = pb, sb, pa, sa
        A = box(pa, sa[1]); cx = min(max(pb[0], A[0]), A[2]); cz = min(max(pb[1], A[1]), A[3])
        return math.hypot(pb[0] - cx, pb[1] - cz) - sb[1]

    def judge(its, a_float):
        f = dict(fl); f["A"] = a_float
        parts = [(k, it["c"], shp(it, "flange")) for k, it in its.items()] + [("screw%d" % i, tuple(s), ("c", SW_R)) for i, s in enumerate(plateg["screws"])]
        worst = []
        for (ka, pa, sa), (kb, pb, sb) in itertools.combinations(parts, 2):
            g = gap(pa, sa, pb, sb); t = 2 * T_MACH + f[ka[0] if not ka.startswith("screw") else "screw"] + f[kb[0] if not kb.startswith("screw") else "screw"]
            worst.append((g - t, g, ka, kb, "face"))
        mated = [(k, it["c"], shp(it, "mated")) for k, it in its.items()]
        for (ka, pa, sa), (kb, pb, sb) in itertools.combinations(mated, 2):
            g = gap(pa, sa, pb, sb); t = 2 * T_MACH + f[ka] + f[kb]
            worst.append((g - t, g, ka, kb, "mated"))
        bands = []
        for k, it in its.items():
            r = it["wall_hole"] / 2; c = it["c"]
            bands.append((min(c[0] - r - plateg["x0"], plateg["x1"] - c[0] - r, c[1] - r - plateg["z0"], plateg["z1"] - c[1] - r), k))
        a = its["A"]
        m14e = (49.0 - U51_H) - (a["c"][1] + A_INSIDE_TOP)
        return dict(face_mated=sorted(worst)[:4], band=min(bands), m14e=m14e, m14e_worst=m14e - M14E_WORST_LESS)

    base = judge(items, fl["A"])
    # the Glenair 233-330 shell 17 at A's place, every other item as laid out
    g = dict(items); g["A"] = dict(items["A"], flange=("sq", D["g_b_max"]), mated=("c", D["q17"]), wall_hole=HOLE_SAW, cutout=D["cut_a17"])
    g_float = (D["g_holes"] - M3_MIN) / 2
    at_place = judge(g, g_float)
    # the best re-layout of the low row: A, C and B moved in X and Z on a 0.05 mm grid around their places (the high row and the screws kept)
    best = None
    rng = lambda a, b, st: [round(a + k * st, 3) for k in range(int(round((b - a) / st)) + 1)]
    for xa, za, xc, xb, zb in itertools.product(rng(-28.5, -26.5, 0.25), rng(36.6, 37.8, 0.2), rng(5.5, 7.5, 0.25), rng(35.0, 36.5, 0.25), rng(36.6, 37.6, 0.25)):
        gb = dict(g); gb["A"] = dict(g["A"], c=(xa, za)); gb["C"] = dict(items["C"], c=(xc, items["C"]["c"][1])); gb["B"] = dict(items["B"], c=(xb, zb))
        j = judge(gb, g_float)
        m = min(j["face_mated"][0][0] - MIN_MECH, j["band"][0] - BAND_MIN, j["m14e_worst"] - MIN_MECH)
        if best is None or m > best[0] + 1e-9:
            best = (m, dict(A=(xa, za), C=(xc, items["C"]["c"][1]), B=(xb, zb)), j)
    R["plate"] = dict(base=base, at_place=at_place, g_float=g_float, best=best, items=items)
    # PX0833: its coupling ring as the outside envelope at A's place
    px = dict(items); px["A"] = dict(items["A"], flange=("c", D["px_ring"]), mated=("c", D["px_ring"]))
    R["plate"]["px"] = judge(px, fl["A"])


# ---------------------------------------------------------------- 2. the bonding strap, the lugs, the stud
def bond(R):
    D = R["D"]; a3 = text(PINS["gen_a3"]); ga = text(PINS["gen_a"])
    jd = tuple(float(x) for x in need(a3, r'"J_DOCK": \((-?\d+), (-?\d+), 0\)', "J_DOCK").groups())
    blk = tuple(float(x) for x in need(ga, r"DOCK_BLOCK = \((-?[\d.]+), (-?[\d.]+), (-?[\d.]+), (-?[\d.]+)\)", "DOCK_BLOCK").groups())
    land = text(PINS["l8gnd_land"])
    ring = float(need(land, r'\(pad "1" thru_hole circle \(at 0 0\) \(size ([\d.]+) [\d.]+\) \(drill ([\d.]+)\)', "H1 land").group(1))
    drill = float(need(land, r"\(drill ([\d.]+)\)", "H1 drill").group(1))
    P = load("panel1450_l7r2b", PINS["panel"])
    F = [it for it in P.CONN_ITEMS if it["key"] == "F"][0]
    a_top = round(sum(t for _, t in P.STACK[:4]), 2); b_under = P.B_UNDER_Z
    wall_in_y = 120.07 - 12.0       # CASE-MARGINS 3.3: the stud's inside parts reach Y 120.07 within 12 of the wall: the wall's inner face at 108.07 + 12 (INFERRED)
    # the strap's route (MODELED): from the stud's inside end down the free band between B16's edge (Y 100) and the wall, at Z 30 west
    # along the band to the site's X, then over board A's top at Z 30 (under B16, above A's tallest parts) to the site, then down to A
    def route(site):
        fx, fz = F["c"]; z_run = 30.0
        y_band = 104.0
        legs = [abs(wall_in_y - y_band), abs(fz - z_run), abs(fx - site[0]), abs(y_band - site[1]), abs(z_run - a_top)]
        return sum(legs), legs
    h1_drafted = (jd[0], blk[3] + 6.0 + 7.5)   # beside J_DOCK on the back-wall side (l8gnd F08): north of the dock block's edge, the land's half ring and a 1.5 web
    h1_alt = (F["c"][0], 80.0 - 7.5)            # the alternative: A's north edge under the stud (Layer 8 / 10's choice, F-R2-06)
    L1, legs1 = route(h1_drafted); L2, legs2 = route(h1_alt)
    allow = 1.15                                 # ASSUMPTION: 15 percent for the bends, the lugs' barrels and service
    # the stud's stack (INFERRED class dimensions, ISO 4032 / ISO 7089 / ISO 10511 / DIN 6798 A / DIN 467, standards not held)
    nut, washer, nyloc, serr, knurl = 5.2, 1.6, 6.0, 0.6, 7.5   # the Nyloc a thin ISO 10512 class (6.0, INFERRED): the regular 8.0 takes the stack 0.2 over the 12
    grip = 5.0 + 2.0 + 5.34                      # plate, gasket, wall (frame_seat STACK_OUT less the flange gasket: the stud passes the plate, gasket and wall)
    inside = washer + D["lug_t"] + washer + nyloc
    outside = serr + nut + serr + 3 * D["lug_t"] + washer + knurl
    length = inside + grip + outside + 2.0       # 2.0 of thread past the knurled nut (ASSUMPTION)
    R["bond"] = dict(h1=dict(ring=ring, drill=drill, lug_b=D["r4"][1], lug_d=D["r4"][0], ok=D["r4"][1] <= ring - 1.0 and D["r4"][0] >= drill - 0.0),
                     stud=dict(lug_b=D["r6"][1], lug_d=D["r6"][0], inside=inside, inside_class=12.0, outside=outside, outside_class_dia=24.0, grip=grip, length=length),
                     h1_drafted=h1_drafted, h1_alt=h1_alt, L_drafted=L1 * allow, L_alt=L2 * allow, legs1=legs1, legs2=legs2, a_top=a_top, b_under=b_under, fstud=F["c"])


# ---------------------------------------------------------------- 3. the right-angle SMA plug against M17g, M17x and M18
def sma(R):
    D = R["D"]; m = " ".join(text(PINS["margins"]).split())
    need(m, r"It lands at its place with a reach of 13\.58 or less, or with MAIN turned 26\.5 degrees", "M17g's bound")
    need(m, r"It meets the 1\.0 minimum at the worst for an axis 1\.38 or more from the plug's inner end, with a ferrule 2\.58 across or less", "M17x's bound")
    need(m, r"\| M18 \|[^\n]*\| \+7\.63 \| \+3\.36 \| \+5\.85 \| -0\.61 \|", "M18's row")
    axis_z, r_bend, place_z, theta0 = 59.0, 12.5, 50.535, 30.0
    def land(reach, th):
        t = math.radians(th)
        return axis_z - reach * math.sin(t) - r_bend * (1 - math.cos(t))
    reach = D["rad_reach"]; ferr = D["rad_ferrule"]; axis_off = D["rad_height"] - D["rad_axis_nut"]; beyond = D["rad_axis_ref"] + axis_off
    land30 = land(reach, theta0); land16 = land(16.0, theta0)
    # the steepest turn at which MAIN's cable still lands at or above its place (its place at Z 50.535; a cable under it in the outer lower place)
    th_max = max(t / 10.0 for t in range(100, 300) if land(reach, t / 10.0) >= place_z)
    m17x_nom = 3.89 + axis_off - max(0.0, (ferr - 2.58) / 2); m17x_worst = -0.38 + axis_off - max(0.0, (ferr - 2.58) / 2)
    m18_nom = 7.63 - max(0.0, beyond - 10.0); m18_worst = 3.36 - max(0.0, beyond - 10.0)
    R["sma"] = dict(reach=reach, ferrule=ferr, axis_off=axis_off, beyond=beyond, land30=land30, land16=land16, land_place=place_z, th_max=th_max,
                    land_th=land(reach, 26.5), m17g_30=land30 - place_z, m17x_nom=m17x_nom, m17x_worst=m17x_worst, m18_nom=m18_nom, m18_worst=m18_worst,
                    hex=D["rad_hex"], v=D["rad_v"])


# ---------------------------------------------------------------- 4. the fans: terminations, the cooler fan's fit, the bracket, the leads
def fans(R):
    D = R["D"]; P = load("panel1450_l7r2c", PINS["panel"]); b3 = text(PINS["gen_b3"]); e3 = text(PINS["gen_e3"]); se = text(PINS["gen_sch_e"])
    l8 = text(PINS["l8r2_fan"])
    need(l8, r"J_FANs  pin 1 FANs_V \(12 V\), 2 GND, 3 FANs_TACH, 4 FANs_PWM; the JST-SH land and code unchanged\.", "board B's drafted header")
    need(se, r'"PH4": "Connector_PinHeader_2\.54mm:PinHeader_1x04_P2\.54mm_Vertical"', "board E's PH4 key")
    jb = {int(k): (float(x), float(y)) for k, x, y in re.findall(r'"J_FAN(\d)": \((-?[\d.]+), (-?[\d.]+), 90\)', b3)}
    je = {int(k): (float(x), float(y)) for k, x, y in re.findall(r'"J_FAN(\d)": \((-?[\d.]+), (-?[\d.]+), 0, False\)', e3)}
    if sorted(jb) != [1, 2, 3] or sorted(je) != [1, 2]:
        refuse("the fan headers' places were not read")
    deep = {r: (c, d) for r, c, d in P.deep_parts()}
    pa_rect = P.deep_part_rect("PA", deep["PA"][0], deep["PA"][1]); pa_bottom = P.FACE_TOP_Z - deep["PA"][1]
    xen = P.deep_part_rect("XENARC_BODY", deep["XENARC_BODY"][0], deep["XENARC_BODY"][1])
    strip_t0 = P.STRIP_T[1]
    ep = P.EPAPER; ep_rect = (ep["c"][0] - ep["module"][0] / 2, ep["c"][1] - ep["module"][1] / 2, ep["c"][0] + ep["module"][0] / 2, ep["c"][1] + ep["module"][1] / 2)
    ep_bottom = P.PLATE_UNDER_Z - ep["depth_below"]
    stack, cooler, gap_b, fan = 5.86, 12.7, 1.0, 20.0       # panel1450's module stack (4.62 + 1.24); the brief's 12.7; the bracket's 1.0 frame; the fan's 20
    top = P.B_TOP_Z + stack + cooler + gap_b + fan
    y0 = xen[3] + 1.0; y1 = y0 + 40.0                       # the fan's south edge 1.0 north of the Xenarc body's north edge
    slots = {}
    for s, (cx_lo, cx_hi) in ((1, (-93.0, -52.0)), (2, (-23.0, 18.0)), (3, (47.0, 88.0))):
        cx = (cx_lo + cx_hi) / 2; r = (cx - 20.0, y0, cx + 20.0, y1)
        over = []
        def ov(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
        if ov(r, pa_rect): over.append(("the PA's underside", pa_bottom))
        if ov(r, ep_rect): over.append(("the e-paper module", ep_bottom))
        over.append(("the plate's underside", P.PLATE_UNDER_Z))
        lim = min(o[1] for o in over)
        hdr = jb[s]
        lead = math.hypot(hdr[0] - cx, hdr[1] - (y0 + y1) / 2) + (top - fan / 2 - (P.B_TOP_Z + 6.0)) + 40.0   # plan + rise + 40 service loop (ASSUMPTION)
        slots[s] = dict(rect=r, over=over, clear=lim - top, lead=lead, header=hdr, strip_gap=strip_t0 - y1, xen_gap=y0 - xen[3])
    R["fans"] = dict(top=top, slots=slots, y=(y0, y1), stack=stack, je=je, jb=jb, ph_temp=D["ph_temp"], sh_temp=D["sh_temp"], ph_awg=D["ph_awg"], sh_awg=D["sh_awg"],
                     backer_under=P.BACKER_UNDER_Z, strip_t0=strip_t0)


# ---------------------------------------------------------------- 5. J_AB2, the MAIN lead and W4-F17
def leads(R):
    P = load("panel1450_l7r2d", PINS["panel"]); a3 = text(PINS["gen_a3"]); b3 = text(PINS["gen_b3"]); ga = text(PINS["gen_a"])
    a_ab2 = tuple(float(x) for x in need(a3, r'"J_AB2": \((-?\d+), (-?\d+), 180\)', "A J_AB2").groups())
    b_ab2 = tuple(float(x) for x in need(b3, r'"J_AB2": \((-?\d+), (-?\d+), 0\)', "B J_AB2").groups())
    a_main = tuple(float(x) for x in need(a3, r'"J_MAINSW": \((-?\d+), (-?\d+), 0\)', "A J_MAINSW").groups())
    c_main = [c for r, c in P.LEAD_LANDS if r == "J_MAINSW"][0]
    mezz = tuple(float(x) for x in need(ga, r"MEZZ_RECT = \(([\d.]+), (-?[\d.]+), ([\d.]+), ([\d.]+)\)", "MEZZ_RECT").groups())
    hdr_h = float(need(text(PINS["assembly"]), r"Its body is about ([\d.]+) mm tall", "J_AB2's height").group(1))
    a_top = round(sum(t for _, t in P.STACK[:4]), 2); d_under = a_top + P.D_STANDOFF; b_under = P.B_UNDER_Z
    intrude = a_top + hdr_h - d_under
    inside = mezz[0] <= a_ab2[0] <= mezz[2] and mezz[1] <= a_ab2[1] <= mezz[3]
    # J_AB2 ribbon (MODELED): up from A's header through its socket to Z under B16's underside, the plan distance, down into B's header
    ab2_plan = math.hypot(b_ab2[0] - a_ab2[0], b_ab2[1] - a_ab2[1]); ab2 = (b_under - a_top) + ab2_plan + 2 * 15.0   # two 15 mm folds and socket exits (ASSUMPTION)
    # MAIN (MODELED): from C7's land under the backer's south strip down outside B16's south edge to A's top, north along X -10 (west of D8)
    # to Y 75, east to J_MAINSW; plus 15 percent and the XH crimp
    route = [abs(P.BACKER_UNDER_Z - a_top), abs(c_main[1] - (-78.0)), abs(c_main[0] - (-10.0)), abs(75.0 - (-78.0)), abs(a_main[0] - (-10.0))]
    main = sum(route) * 1.15
    R["leads"] = dict(a_ab2=a_ab2, b_ab2=b_ab2, a_main=a_main, c_main=c_main, mezz=mezz, hdr_h=hdr_h, a_top=a_top, d_under=d_under, intrude=intrude, inside=inside,
                      ab2=ab2, ab2_plan=ab2_plan, main=main, main_route=route, b_under=b_under)


def prices(R):
    fc = json.load(open(os.path.join(TOP, PINS["prices"]), encoding="utf-8"))["parts"]
    def first(part, dist, tier=None):
        for r in fc[part]:
            if r["distributor"] == dist and r["price_breaks"]:
                pb = sorted(r["price_breaks"]) if tier is None else [p for p in r["price_breaks"] if p[0] == tier]
                if pb:
                    return (r["sku"], r["stock"], pb[0])
        return None
    R["prices"] = {k: v for k, v in (
        ("RCP-5SPFFH-SCM7001", first("RCP-5SPFFH-SCM7001", "Farnell")), ("PX0833", first("PX0833", "Farnell")),
        ("PX0888", first("PX0888", "Heilind Europe")), ("R125.172.001", first("R125.172.001", "Richardson RFPD")),
        ("R5.5-4", first("R5.5-4", "RS")), ("R5.5-6", first("R5.5-6", "TME")), ("B4B-PH-K-S", first("B4B-PH-K-S", "Farnell")),
        ("PHR-4", first("PHR-4", "Farnell")), ("SPH-002T-P0.5S", first("SPH-002T-P0.5S", "Farnell")))}
    R["prices"]["233-330"] = None if not fc["233-330"] else fc["233-330"]


def compute():
    R = {"pins": {k: sha_of(v) for k, v in PINS.items()}}
    readings(R); plate(R); bond(R); sma(R); fans(R); leads(R); prices(R)
    pl, b, s, f, l = R["plate"], R["bond"], R["sma"], R["fans"], R["leads"]
    R["pred"] = {
        "the shell 15 class reproduces CASE-MARGINS' M14j/M14k tightest worst within 0.02 (1.11 to 1.13)": abs(pl["base"]["face_mated"][0][0] - 1.11) < 0.02,
        "the PX0833 is rated under the PoE feed's 57 V": R["D"]["px_v"] < 57.0,
        "the Glenair 233-330 shell 17 at A's place fails the plate": min(pl["at_place"]["face_mated"][0][0] - MIN_MECH, pl["at_place"]["band"][0] - BAND_MIN) < 0,
        "no re-laid low row fits the 233-330 shell 17 (the least spare under 0)": pl["best"][0] < 0,
        "the LTW receptacle prints the PoE range": R["D"]["ltw_v"] == (44.0, 57.0),
        "the M4 lug fits H1's 12.0 ring with 1.0 to spare or more": b["h1"]["ok"],
        "the strap at the drafted H1 site is over 250 mm, the alternative under 100 mm": b["L_drafted"] > 250.0 and b["L_alt"] < 100.0,
        "the Radiall plug's cable axis meets M17x's 1.38": s["axis_off"] >= 1.38 and s["m17x_worst"] >= MIN_MECH,
        "the Radiall plug at 30 degrees lands MAIN's cable below its place": s["m17g_30"] < 0,
        "MAIN turned 26.5 degrees lands at or above its place": s["land_th"] >= s["land_place"],
        "the Radiall plug's crimp ferrule exceeds 2.58": s["ferrule"] > 2.58,
        "the Radiall plug's inner end lies beyond the class's 10.0 and M18 fails at the worst": s["beyond"] > 10.0 and s["m18_worst"] < MIN_MECH,
        "the stud's inside stack keeps within the 12 of the wall": b["stud"]["inside"] <= b["stud"]["inside_class"],
        "JST PH covers -40 C and AWG 24, SH stops at AWG 28 and -25 C": f["ph_temp"][0] <= -40 and f["ph_awg"][1] == "24" and f["sh_awg"][1] == "28" and f["sh_temp"][0] == -25,
        "every cooler fan clears what hangs above it by 2.0 or more on the cooler's own height": all(v["clear"] >= 2.0 for v in f["slots"].values()),
        "the cooler fan sits between the Xenarc and the top strip with under 1.5 on a side": all(0 < v["strip_gap"] < 1.5 and 0 < v["xen_gap"] < 1.5 for v in f["slots"].values()),
        "J_AB2 on board A stands inside D's rectangle and into D's underside": l["inside"] and l["intrude"] > 0,
    }
    return R


def render(R):
    out = []; P = out.append
    D, pl, b, s, f, l = R["D"], R["plate"], R["bond"], R["sma"], R["fans"], R["leads"]
    P("L7R2 (MESHSAT-1357): THE LAYER 7 ITEMS OTHER LAYERS ASSIGNED, ROUND 2. Prototype design, desk arithmetic: nothing bought, built or measured.")
    P("MAKER a printed figure (inputs/makers-drawings-r2-2026-10-03.md), MODELED this script's arithmetic, INFERRED a reading not printed as such,")
    P("ASSUMPTION a stated assumption, NOT READ a figure no held document prints.")
    P("")
    P("0. INPUTS (sha256/16)")
    for k, v in PINS.items():
        P("   %-11s %s  sha256 %s" % (k, v, R["pins"][k][:16]))
    P("")
    P("1. THE SEALED RJ45 AND ITS SHIELD PATH (record l8gnd F01; IF-EXT-ETH)")
    P("   the need: a coupler whose body or backshell carries the patch cable's shield to the connector plate (GND-002 point 3), rated for the PoE feed")
    P("   (+54V_POE, the PSE range to 57 V), inside the plate's item A envelope (MIL-DTL-38999 shell 15 class: flange 31.29 square, mated 32.51, wall hole 29)")
    P("   the shell 15 class as laid out (panel1450 CONN_ITEMS), this script's pair method (frame_seat.py's floats, two machined places a pair):")
    for w, g, a, bb, k in pl["base"]["face_mated"][:3]:
        P("      %-5s %s / %s: %.2f nominal, %.2f at the worst" % (k, a, bb, g, w))
    P("   candidate 1, Bulgin PX0833 with the PX0888 backshell: the PX0888 (SS 304) carries the coupler's shield to the panel (MAKER, Bulgin's page);")
    P("      the PX0833 is rated %.0f V maximum (MAKER, its sheet) against the PoE feed's 57 V: NOT ELIGIBLE; its %.1f coupling ring at A's place: worst pair %.2f (%s / %s)"
      % (D["px_v"], D["px_ring"], pl["px"]["face_mated"][0][0], pl["px"]["face_mated"][0][2], pl["px"]["face_mated"][0][3]))
    a = pl["at_place"]
    P("   candidate 2, Glenair 233-330 (aluminium shell, external dimensions as D38999/20 /24 /26 by the maker, shell 17 or 19 only): flange %.2f square max, mated shell 17 plug %.1f" % (D["g_b_max"], D["q17"]))
    P("      (Amphenol's D38999/26 table), M3 holes %.2f max (float %.3f), %.2f behind the flange, rear thread %.4f in (%.2f); a wall hole of %.1f (ASSUMPTION) and the plate cut-out %.2f"
      % (D["g_holes"], pl["g_float"], D["g_rear"], D["g_thread_in"], D["g_thread_in"] * 25.4, HOLE_SAW, D["cut_a17"]))
    P("      (Glenair's rear-mount A dia, INFERRED: the rear thread passes the plate); its voltage rating and its jacks' shield-to-shell bond NOT READ")
    P("      at A's place: worst pair %.2f (%s / %s %s), gasket band %.2f (%s) against 3.0, M14e %.2f nominal, %.2f at the worst: DOES NOT FIT"
      % (a["face_mated"][0][0], a["face_mated"][0][2], a["face_mated"][0][3], a["face_mated"][0][4], a["band"][0], a["band"][1], a["m14e"], a["m14e_worst"]))
    bm, bp, bj = pl["best"]
    P("      the best re-laid low row (A, C and B moved on a 0.25 mm grid, the high row and the screws kept): A at (%.2f, %.2f), C at (%.2f, %.2f), B at (%.2f, %.2f):"
      % (bp["A"][0], bp["A"][1], bp["C"][0], bp["C"][1], bp["B"][0], bp["B"][1]))
    P("      worst pair %.2f (%s / %s %s), gasket band %.2f (%s), M14e at the worst %.2f: the least spare over the three rows %.2f mm"
      % (bj["face_mated"][0][0], bj["face_mated"][0][2], bj["face_mated"][0][3], bj["face_mated"][0][4], bj["band"][0], bj["band"][1], bj["m14e_worst"], bm))
    P("   candidate 3, Amphenol LTW RCP-5SPFFH-SCM7001 (middle size, screw thread, 13/16-28 UNS nut, front fasten): operating voltage %.0f to %.0f V (MAKER);"
      % D["ltw_v"])
    P("      'Plastic, Shielded' (MAKER): its shield's bond to the panel NOT READ; panel thickness %.2f max without the cap against the plate's 5.0 (a 3.0 spot" % D["ltw_panel"])
    P("      face from the plate's back would be needed); its drawing is behind the maker's download form (NOT READ)")
    P("   prices read (FindChips, 3 Oct 2026 14:48 UTC; indicators): PX0833 %s; PX0888 %s; RCP-5SPFFH-SCM7001 %s; 233-330 no row served (NOT READ)"
      % (R["prices"]["PX0833"], R["prices"]["PX0888"], R["prices"]["RCP-5SPFFH-SCM7001"]))
    P("")
    P("2. THE BONDING STRAP, ITS LUGS AND THE STUD (record l8gnd F07; IF-A-CHASSIS)")
    P("   H1's land (l8gnd's ChassisLug_M4_CHASSIS): ring %.1f, drill %.1f; JST R5.5-4 (M4): d2 %.1f, B %.1f, L %.1f, T %.1f, wire %s to %s mm2: fits with %.1f of ring to spare"
      % (b["h1"]["ring"], b["h1"]["drill"], D["r4"][0], D["r4"][1], D["r4"][2], D["lug_t"], D["lug_awg"][0], D["lug_awg"][1], b["h1"]["ring"] - D["r4"][1]))
    P("   the stud F: JST R5.5-6 (M6): d2 %.1f, B %.1f (the inside washer class 12): the inside stack (washer, lug, washer, thin Nyloc, INFERRED ISO classes) %.1f against"
      % (D["r6"][0], D["r6"][1], b["stud"]["inside"]))
    P("   CASE-MARGINS' 'within 12 of the wall' %.1f; the grip (plate 5.0, gasket 2.0, wall 5.34) %.2f; the outside (serrated washer, nut, serrated washer, three lugs,"
      % (b["stud"]["inside_class"], b["stud"]["grip"]))
    P("   washer, knurled nut) %.1f; the stud's length %.1f (MODELED): an M6 A4 threaded stud of %d (the next DIN 976-1 length, INFERRED)" % (b["stud"]["outside"], b["stud"]["length"], min(x for x in (40, 45, 50, 55, 60) if x >= b["stud"]["length"])))
    P("   the strap's route (MODELED; free band Y 100 to 108 at the wall, Z 30 over board A's top under B16 at %.2f, board A's top %.2f):" % (b["b_under"], b["a_top"]))
    P("      to H1 as drafted (beside J_DOCK on the back-wall side, l8gnd F08: about (%.0f, %.1f)): legs %s, %.0f mm with 15 percent (ASSUMPTION)"
      % (b["h1_drafted"][0], b["h1_drafted"][1], " + ".join("%.1f" % x for x in b["legs1"]), b["L_drafted"]))
    P("      to an H1 at board A's north edge under the stud (about (%.1f, %.1f)): legs %s, %.0f mm" % (b["h1_alt"][0], b["h1_alt"][1], " + ".join("%.1f" % x for x in b["legs2"]), b["L_alt"]))
    P("   prices (indicators): R5.5-4 %s; R5.5-6 %s" % (R["prices"]["R5.5-4"], R["prices"]["R5.5-6"]))
    P("")
    P("3. THE RIGHT-ANGLE SMA PLUG (M17g, M17x; IF-AE-RF)")
    P("   Radiall R125.172.001 (crimp, RG 316): reach (mating axis to the ferrule's end) %.1f; ferrule %.3f (crimp hexagon %.2f); cable axis %.1f below the plug's"
      % (s["reach"], s["ferrule"], s["hex"], s["axis_off"]))
    P("   inner end; the inner end %.1f beyond the reference plane; %d Veff (MAKER, the drawing read off its dimension lines)" % (s["beyond"], s["v"]))
    P("   M17g (MAIN's cable onto its place, Z %.3f): at 30 degrees the class's 16.0 lands at %.2f, this plug at %.2f (%.2f, below its place); MAIN turned 26.5"
      % (s["land_place"], s["land16"], s["land30"], s["m17g_30"]))
    P("   degrees lands at %.2f (%.2f above); the steepest turn landing at or above the place %.1f degrees" % (s["land_th"], s["land_th"] - s["land_place"], s["th_max"]))
    P("   M17x by CASE-MARGINS' own relation (worst -0.38 + the axis offset, less half the ferrule's excess over 2.58): %.2f nominal, %.2f at the worst: MET"
      % (s["m17x_nom"], s["m17x_worst"]))
    P("   the inner upper place beside MAIN's ferrule needs 2.58 or less: %.3f does not: IRIDIUM to the back bundle (CASE-MARGINS' lever), so no passing cable needs it" % s["ferrule"])
    P("   M18 (the plug's inner end to the RockBLOCK's box): the class took 10.0 beyond the jack's end; this plug %.1f beyond its reference plane (the jack's end, INFERRED):"
      % s["beyond"])
    P("      %.2f nominal, %.2f at the worst against 1.0: a FINDING at the 5G MAIN site: a plug %.2f or less beyond its reference plane meets it at the worst"
      % (s["m18_nom"], s["m18_worst"], 10.0 + 3.36 - 1.0))
    P("   price (indicator): %s" % (R["prices"]["R125.172.001"],))
    P("")
    P("4. THE FANS: TERMINATIONS, THE COOLER FAN'S FIT AND ITS BRACKET, THE LEADS")
    P("   board B's J_FAN (l8r2's draft keeps JST-SH BM04B-SRSS-TB): SH takes AWG %s to %s at %d to +%d C (MAKER); board E's J_FAN key PH4 is a 2.54 mm unkeyed pin header"
      % (f["sh_awg"][0], f["sh_awg"][1], f["sh_temp"][0], f["sh_temp"][1]))
    P("   JST PH (B4B-PH-K-S, PHR-4, SPH-002T-P0.5S): AWG %s to %s, %d to +%d C, 2 A, 100 V (MAKER); the fans' lead gauge and length NOT READ (Sanyo's manual)"
      % (f["ph_awg"][0], f["ph_awg"][1], f["ph_temp"][0], f["ph_temp"][1]))
    P("   prices (indicators): B4B-PH-K-S %s; PHR-4 %s; SPH-002T-P0.5S %s" % (R["prices"]["B4B-PH-K-S"], R["prices"]["PHR-4"], R["prices"]["SPH-002T-P0.5S"]))
    P("   the cooler fan on its bracket over each cooler: board B's top %.2f + the module stack %.2f + the cooler 12.7 + the bracket's frame 1.0 + the fan 20: top %.2f"
      % (R["fans"]["top"] - 5.86 - 12.7 - 1.0 - 20.0, f["stack"], f["top"]))
    P("   its plan: Y %.3f to %.3f (1.0 north of the Xenarc body's edge, %.3f south of the backer's top strip at Y %.1f), X at the cooler's centre" % (f["y"][0], f["y"][1], f["strip_t0"] - f["y"][1], f["strip_t0"]))
    for k, v in f["slots"].items():
        P("      slot %d: X %.1f to %.1f, over it %s: clearance %.2f; its lead to J_FAN%d at (%.1f, %.1f): %.0f mm (MODELED, with a 40 service loop)"
          % (k, v["rect"][0], v["rect"][2], ", ".join("%s at Z %.2f" % o for o in v["over"]), v["clear"], k, v["header"][0], v["header"][1], v["lead"]))
    P("   the mixers' headers on board E: J_FAN1 (%.1f, %.1f), J_FAN2 (%.1f, %.1f) on the dock strip; the mixers' sites 'at the stack's ends' are not drawn (NOT READ)"
      % (f["je"][1][0], f["je"][1][1], f["je"][2][0], f["je"][2][1]))
    P("")
    P("5. J_AB2, THE MAIN LEAD AND W4-F17")
    P("   W4-F17: board A's J_AB2 at (%.0f, %.0f) inside D's rectangle %s: %s; the header %.1f tall from A's top %.2f reaches %.2f, D's underside %.2f: %.2f into D (before the socket)"
      % (l["a_ab2"][0], l["a_ab2"][1], l["mezz"], "yes" if l["inside"] else "no", l["hdr_h"], l["a_top"], l["a_top"] + l["hdr_h"], l["d_under"], l["intrude"]))
    P("   the J_AB2 ribbon from A (%.0f, %.0f) to B (%.0f, %.0f): plan %.1f, rise %.2f, two folds 15 each (ASSUMPTION): %.0f mm, conditional on W4-F17's move"
      % (l["a_ab2"][0], l["a_ab2"][1], l["b_ab2"][0], l["b_ab2"][1], l["ab2_plan"], l["b_under"] - l["a_top"], l["ab2"]))
    P("   the MAIN lead from C7's land (%.1f, %.1f) under the backer to A's J_MAINSW (%.0f, %.0f): legs %s, with 15 percent %.0f mm (MODELED route, section 5 of the page)"
      % (l["c_main"][0], l["c_main"][1], l["a_main"][0], l["a_main"][1], " + ".join("%.1f" % x for x in l["main_route"]), l["main"]))
    P("")
    P("6. PREDICATES")
    for k, v in R["pred"].items():
        P("   %-120s %s" % (k, "yes" if v else "NO"))
    return "\n".join(out) + "\n"


def main():
    sys.stdout.write(render(compute()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
