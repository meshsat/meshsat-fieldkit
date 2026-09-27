"""The face of the MeshSat field kit in the Peli 1450: one source of positions for the aluminium plate (v2/cad/face_plate.py), the C7 backer board
(gen_pcb_c.py, gen_pcb_c3.py, check_pcb_c.py), the case wall template (case_wall_cutouts.py) and the render scene. Case frame: X along the case's long
axis, +Y toward the back (hinge) wall, both from the case centre; the frame window is centred on the case (appendix 32.40 items 4 and 5, 32.42).
Plain Python, no KiCad or CAD imports.

C7 (7 Sep 2026, MESHSAT-830; appendix 32.51, 32.52, 32.56, 32.60): the Xenarc 709GNK monitor sits IN the plate, its glass level with the aluminium face (owner ruling 9 Sep 2026, appendix 32.85) over a cutout for its connector block
(no display aperture, no lens), the Pervasive Displays E2370KS0C1 glass replaces the WeAct module in the same window, two U-174/U headset jacks and
the ambient light guide join the face, a USB camera looks through a sealed window at the top right, the RA30H1317M1 PA flange bolts to the plate's
underside inside the backer's void, and the backer becomes a ring (a fourth strip along the top carries the e-paper flex socket, its boost circuit,
the camera and the ribbon from B16's J_PANEL right below it). B16 is 330 x 200 (X +-165, Y +-100), so the strips sit over its edge bands: the
gate keeps the deep face parts clear of B16's tall parts (B16_TALL). The QMX HF unit left B16 for a lid bracket (32.60) because no 63 x 95 x 25 mm
bay on B16 clears the toggle bodies under the left strip.

C1 to C6 (27 Sep 2026, MESHSAT-1357; v2/docs/CASE-MARGINS.md section 4, the session's choices SC-07 under the owner's standing rule of
26 Sep 2026): the face plate lies ON the 1450PF frame and covers Peli's o-ring (C1), the frame stands on four setting legs referenced to
the case floor (C6), so FACE_TOP_Z is derived here from the legs' pad, the frame's ring and the plate instead of the "base 109.4, lip 8"
datum no Peli file supports; the ruled arrestors are the twelve antenna bulkheads at Z 59 (C2) on one RF entry plate per end wall (C4);
one connector plate between the hinge fairings carries the six ruled back-wall items (C3); the QMX tray moves 1.5 mm west (C5). Every
number of this block is also a row input of v2/vendor/peli/frame_seat.py, which computes the margins; the geometry here is the design
basis only and establishes no fit, seal or alignment (CASE-MARGINS.md section 1, Verdicts)."""

# --- Peli's own figures the arrangement derives from (CASE-MARGINS.md sections 2.2 to 2.4, entity ids there; STEP unit inch x 25.4)
PELI = dict(rim_z=108.97,            # base: floor #1321 to the rim face #1637 (drawing _D_7 108.97)
            shoulder_z=101.04,       # up-facing ledge 0.51 wide at the top of the cavity (#776)
            ring_t=9.39,             # 1450PF ring: top face z 8.76 to the flat underside #1703 at z -0.63
            frame_h=17.52,           # 1450PF #1 .. #5527 (sheet 1453-314-000 rev A: 17.5)
            skirt_below_ring=8.13,   # the skirt below the ring's underside
            lid_z=45.47,             # lid: parting line to the inner ceiling (#712 to #736; drawing _D_6)
            flat_floor=(171.64, 114.49),   # the flat floor's half extents, bounded by the R 15.88 fillet tangents (#1321)
            fillet_r=15.88)          # floor fillet R 0.625 in on all four floor edges (#355 ...)
# the allowances FACE_TOP_Z and the legs' pad are derived with (CASE-MARGINS.md section 1, tolerance model): sheet = Peli's frame sheet
# 1453-314-000 rev A, one-decimal mm (VERIFIED); case_z and floor = that class applied to Peli's case, which publishes none (INFERRED,
# UNSTATED); leg and plate = the kit's own drawing tolerances (the plate's 3.0 by the EN 485-4 class, standard not held, INFERRED)
TOL = dict(sheet=0.76, case_z=0.76, floor=0.76, leg=0.10, plate=0.13, outline=0.10, rebate=0.10, machined=0.10, centring=0.20, locator=0.30)

# --- frame 1450PF (measured on Peli's STEP, 32.41 and 32.42)
WINDOW = (349.65, 233.83)                 # the opening; everything visible lies inside it, 3 mm in
# C1: the plate lies on the frame's top face, covers Peli's o-ring in the channel between the frame and the case wall, and takes ten 6-32 UNC
# x 1/2 in A2 pan heads from above into Peli's brass inserts (Peli's mounting instructions, steps 2 to 4). 377.2 x 263.0 so that the plate
# edge keeps 1.0 to the rim zone at the worst with the plate floating 0.63 on the smallest 6-32 (M8); the band outside REB_IN is rebated
# REBATE from the top (1.0 left) so the edge under the lid's wall sits lower (M2); the underside is flat but for the relief pocket over the
# frame's raised "1450 FRONT" lettering. The PORON ring of the superseded construction is dropped: Peli's o-ring is the intended seal.
PLATE = (377.2, 263.0, 3.0)
PLATE_R = 16.0
REBATE = 2.0                              # depth of the rebated band, from the top face
REB_IN = (368.0, 253.0)                   # the full-thickness face; outside it the plate is 1.0 thick
REBATE_R = 16.0                           # corner radius of the full-thickness face: not below Peli's R 15.88 corners, so each corner keeps at least the side gaps of M2b (INFERRED)
FACE_HOLE = 4.6                           # the ten screw holes (a 4.6 drill): the largest 6-32 (3.505) passes with Peli's insert pattern at +-0.38 per side (M8f)
FACE_SCREW = "6-32 UNC x 1/2 in, A2 pan head (ASME B18.6.3 class, 6.86 across the head at most)"
RELIEF_POCKET = (-110.9, -125.4, -66.9, -116.4, 0.8)   # x0, y0, x1, y1, depth: in the underside over the lettering (X -108.99..-68.80, Y -123.64..-118.32)
# Peli's insert bores through the ring, at the STEP's figures (the sheet's pattern is 358.1 x 242.3, +-0.38 per side); the ten screws of C1
FRAME_BOSSES = [(-139.45, -121.16), (139.45, -121.16), (0.0, -121.16), (-139.45, 121.16), (139.45, 121.16), (0.0, 121.16),
                (-179.07, -75.95), (179.07, -75.95), (-179.07, 75.95), (179.07, 75.95)]

# C6: four setting legs, 6061-T6 profiles cut from 6.0 plate lying in the X-Z plane, bonded under the frame's ring near its corners (placed by a
# printed locator in each window corner) and standing on Peli's flat floor; the frame is lowered on them, centred by two pairs of printed
# wedges and fixed by Peli's four self-tapping screws. The pad top is the lowest that keeps the plate's underside 0.10 above the highest the
# shoulder can stand, so the rebated band faces the rim zone at every seat (M8z).
LEG = dict(t=6.0, y=(106.4, 112.4),       # the profile's plane: |Y| 106.4 .. 112.4
           col_x=(175.40, 180.17),        # the column under the ring (the ring spans |X| 174.83 .. 182.75 over the leg's Y)
           foot_x=(156.0, 169.0),         # the foot's bearing face on the flat floor (2.64 inside the fillet tangent)
           relief=2.5,                    # the underside beyond the foot follows Peli's R 15.88 fillet at this normal offset
           foot_h=8.0, gusset_z=30.0,     # the foot's height and the gusset joining it to the column below Z 30 (INFERRED shape)
           vhb_pocket=0.9,                # the pad top carries a VHB 5952 pad in a 0.9 pocket, so the aluminium rim meets the ring
           wedge=(0.0, 2.0, 40.0),        # centring wedges: 0 to 2.0 mm over 40 mm, printed, two pairs
           locator_fit=0.30)              # the printed locator places a leg within 0.30 of the window's edges (INFERRED)
LEG_TOP_Z = round(PELI["shoulder_z"] + TOL["case_z"] + 0.10 - PELI["ring_t"] + (TOL["floor"] + TOL["leg"] + TOL["sheet"]), 2)   # 94.13
FRAME_BOTTOM_Z = round(LEG_TOP_Z - PELI["skirt_below_ring"], 2)                                                                   # 86.00

# --- the stack under the face: B16's outline is X +-165, Y +-100 (32.58); the strips lie over its edge bands, so B16_TALL gates the deep parts
B_OUTLINE = (-165.0, -100.0, 165.0, 100.0)
A_OUTLINE = (-120.0, -80.0, 120.0, 80.0)  # gen_pcb_a.py:16-17 (240 x 160, centred)
E_OUTLINE = (-149.0, -113.0, 118.0, -45.0)   # gen_pcb_e.py:15 (267 x 68 along the front wall)
D_OFFSET = (50.0, 0.0)                    # D8's local origin in the case frame: A's MEZZ_RECT (0, -40, 100, 40), gen_pcb_a.py:51
D_STANDOFF = 6.0                          # D8's underside above A's top copper (ASSEMBLY.md section 1; appendix 32.85)
# the rod stack from the floor (C1 follow-on (a): the dock strip's VHB 5952 pads lift the whole stack, ASSEMBLY.md section 1). Each board's
# thickness is its board file's (general (thickness)), which test_case_geometry.py holds this list to; the two spacers are unnamed parts
# (CASE-MARGINS.md section 6, TBD) at the figures of appendix 32.21/32.30 (gap) and ASSEMBLY.md correction 3 (bay)
STACK = [("VHB 5952 pads under the dock strip", 1.1), ("board E dock strip", 1.6), ("blind-mate gap spacer", 13.4),
         ("board A", 1.6), ("A-to-B bay spacer", 31.3), ("board B", 1.6)]
STACK_TOL = dict(vhb=0.11, laminate=0.16, bow=0.30)   # 3M VHB 5952 1.1 +-10 %, JLC 1.6 +-10 % (VERIFIED); B bow over 40 mm (IPC-6012 class, INFERRED)
B_TOP_Z = round(sum(t for _, t in STACK), 2)   # 50.6: B16's top copper above the case floor. It was 49.5 until 27 Sep 2026, without the VHB
                                          # pads (32.56; 56.0 until 9 Sep 2026, appendix 32.85, when the recessed monitor dropped the board 6.5 mm)
B_UNDER_Z = round(B_TOP_Z - STACK[-1][1], 2)
A_TOP_Z = round(sum(t for _, t in STACK[:4]), 2)
FACE_TOP_Z = round(LEG_TOP_Z + PELI["ring_t"] + PLATE[2], 2)   # 106.52 above the case floor (C1 on C6); 101.4 until 27 Sep 2026 on "base 109.4, lip 8"
FACE_TOP_TOLS = [("floor under the leg", TOL["floor"]), ("leg height", TOL["leg"]), ("ring 9.39", TOL["sheet"]), ("plate 3.0", TOL["plate"])]
PLATE_UNDER_Z = FACE_TOP_Z - PLATE[2]
BACKER_GAP = 10.0                         # standoff height between the plate's underside and the backer's top
BACKER_T = 1.6
BACKER_UNDER_Z = PLATE_UNDER_Z - BACKER_GAP - BACKER_T
# B16's tall parts (case mm rect, height above B16's top copper): what the face gates (check_pcb_c.py, z_budget.py) hold the deep face parts to.
# Since 27 Sep 2026 (MESHSAT-1357) the list is READ, not typed: v2/cad/zstack.py reads the committed board B file (its routeflow profile's
# board, sha256 recorded) and every part 3.0 mm or taller by its library model or its declared class, adds the M.2 cards over the committed
# sockets, and writes them with the module envelopes below into v2/cad/zstack.json, which this file loads. The hand list of 9 Sep 2026 it
# replaces (kept in zstack.py as LEGACY_B16_TALL) had drifted from B21: J_ETH was 14.0 where the RJ45's model stands 15.5, nine 2.54 mm pin
# headers of 8.54 and six XAL6060 inductors of 6.10 sat under 6.0 envelopes, and the E22/E72/LG290P modules, slot 1's M.2 cards, the fan
# headers, J_RB9704 and BT1 lay under no envelope at all. test_case_geometry.py holds zstack.json to the committed board's sha256.
# The modules are not parts of any board file, so their envelopes stay here, each with its source; zstack.py reports whether each one's anchor
# (its connectors or bracket holes on the committed board) lies inside it.
# 9 Sep 2026 (appendix 32.85): each CM5 site was ONE 30 mm envelope covering cooler and fan, which is why the recessed monitor read as a
# 13.3 mm collision against all three. The heatsink is 21.0 mm (module 4.62 + 1.24, base 4.0, fins 8.7 from scene.py:288-290) over the whole
# 56 mm site; the fan is the 30 mm part and it only needs to sit NORTH of the monitor's edge at Y +45.745, so it moves from cy 60 to cy 63
# (Y 48 .. 78, clear by 2.255 mm). The no-vent ruling of 7 Sep keeps its fan per cooler; only its position changes.
B16_MODULES = [
    ((-93.0, 32.0, -52.0, 88.0), 21.0, "CM5 slot 1 heatsink", "CM5 on U30A/U30B with its cooler: 21.0 from the render scene, TBD a Raspberry Pi drawing (CASE-MARGINS.md section 6)"),
    ((-23.0, 32.0, 18.0, 88.0), 21.0, "CM5 slot 2 heatsink", "CM5 on U31A/U31B with its cooler: as slot 1"),
    ((47.0, 32.0, 88.0, 88.0), 21.0, "CM5 slot 3 heatsink", "CM5 on U32A/U32B with its cooler: as slot 1"),
    ((-87.5, 48.0, -57.5, 78.0), 30.0, "CM5 slot 1 fan", "30 mm class fan on the cooler (appendix 32.85; the fan part is open, W4-F9)"),
    ((-17.5, 48.0, 12.5, 78.0), 30.0, "CM5 slot 2 fan", "as slot 1"),
    ((52.5, 48.0, 82.5, 78.0), 30.0, "CM5 slot 3 fan", "as slot 1"),
    ((130.0, -43.0, 161.0, 45.0), 12.0, "LimeSDR Mini in J_LIME", "LimeSDR Mini 2.x in J_LIME (appendix 32.58, 32.59; maker drawing v2/vendor/limesdr/ to read)"),
    ((113.0, -99.0, 165.0, -43.0), 21.0, "RockBLOCK 9704 on its bracket", "RockBLOCK 9704 on the bracket over H17..H20 (appendix 32.58; v2/vendor/rockblock/)")]
# THE BOARD READING IS REQUIRED, NEVER REPLACED (27 Sep 2026, MESHSAT-1357 layer 7, the second review of the case release). The first
# version of this loader fell back to B16_MODULES alone, with one line on stderr, when v2/cad/zstack.json was absent: 8 envelopes where the
# reading has 59, so J_ETH, T1, J_PANEL, the west headers, J_CAM, the radio modules and the M.2 cards dropped out and board C's gate
# (check_pcb_c.py, MEC-001) still printed PASS under the same code bundle. A missing file is a realistic case (a chain tree staged without
# v2/cad/), so the reading is now loaded on first use and a missing, unreadable or malformed file raises ZstackMissing: the gates that need
# B16_TALL crash, and their crash hook writes INCONCLUSIVE, never a PASS on a weaker list. Everything else here (the plate, the legs, the
# stack, the walls) needs no board reading, so the generators and the CAD that import this file are unaffected, and v2/cad/zstack.py, which
# writes the reading and imports this file, can always run. B16_FROM_BOARD names what was read: the board B file and its sha256, and the
# reading's own path and sha256 (first 16), which check_pcb_c.py records in its verdict's inputs (drafts/hc7/check_pcb_c.py.patch).
import os as _os
ZSTACK_JSON = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "cad", "zstack.json"))


class ZstackMissing(RuntimeError):
    """v2/cad/zstack.json is absent, unreadable or not a board reading: B16_TALL cannot be given, and no weaker list stands in for it."""


_B16_CACHE = {}


def _b16_from_board():
    """(B16_TALL, B16_FROM_BOARD) from the reading v2/cad/zstack.py wrote from the committed board B; raises ZstackMissing otherwise."""
    if "tall" in _B16_CACHE: return _B16_CACHE["tall"], _B16_CACHE["from"]
    import json as _json, hashlib as _hl
    f = ZSTACK_JSON
    try:
        raw = open(f, "rb").read()
    except OSError as e:
        raise ZstackMissing("%s cannot be read (%s): B16_TALL is the committed board B's reading and nothing stands in for it; run "
                            "python3 v2/cad/zstack.py --json v2/cad/zstack.json in a full checkout" % (f, e.__class__.__name__))
    try:
        z = _json.loads(raw.decode("utf-8"))
        b = z["boards"]["b"]
        tall = [(tuple(float(v) for v in e["rect"]), float(e["h"]), str(e["name"])) for e in z["b16_envelopes"]]
        frm = dict(file=str(b["file"]), sha256=str(b["sha256"]), zstack=f, zstack_sha256_16=_hl.sha256(raw).hexdigest()[:16])
    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as e:
        raise ZstackMissing("%s is not a board reading (%s: %s)" % (f, e.__class__.__name__, e))
    mods = {n for _, _, n, _ in B16_MODULES}
    if not tall or not mods <= {n for _, _, n in tall} or len(tall) <= len(mods):
        raise ZstackMissing("%s carries %d envelopes, not the modules plus board B's parts: a reading of nothing is not a reading" % (f, len(tall)))
    _B16_CACHE.update(tall=tall, **{"from": frm})
    return tall, frm


def b16_tall():
    """B16's tall parts (case mm rect, height above B16's top copper, name): the board reading. Raises ZstackMissing without it."""
    return _b16_from_board()[0]


def __getattr__(name):
    # PEP 562: panel1450.B16_TALL and panel1450.B16_FROM_BOARD are read on first use, so importing this module never needs the board reading
    if name == "B16_TALL": return _b16_from_board()[0]
    if name == "B16_FROM_BOARD": return _b16_from_board()[1]
    raise AttributeError("module 'panel1450' has no attribute %r" % name)

# --- the face elements (centre X, centre Y in the case frame)
XENARC = dict(c=(0.0, -24.0), body=(205.15, 139.49), height=28.66, bezel=16.0, active=(153.6, 90.0), vesa=50.0, vesa_hole=4.5,
              block=(73.65, -72.2, 57.85, 43.12), cutout=(73.65, -72.2, 60.0, 46.0, 3.0), block_depth=19.0,
              # 9 September 2026 (appendix 32.85), the FRONT PROFILE, read off the side view of xenarc-709gnk-dimensional-drawing-v3.pdf
              # at 400 dpi because the record had never captured it: the body is STEPPED. A front bezel flange 10.66 mm thick carries the
              # full 205.15 x 139.49 outline, and behind it a smaller rear shell 18.00 mm deep (10.66 + 18.00 = 28.66); the shell's bottom
              # face runs 16.16 mm back from the front before it curves away. The bezel opening is 173.15 x 117.55 (borders 16.0 either
              # side, 11.0 top, 10.94 bottom) and the 153.6 x 90 active area sits inside it with the OSD keys in the bottom band.
              bezel_depth=10.66, shell_depth=18.00, shell_bottom_flat=16.16, glass=(173.15, 117.55), border=(16.0, 16.0, 11.0, 10.94),
              # RECESSED since 9 September 2026 by owner ruling: the glass surface is level with the plate's top face (appendix 14.6,
              # 2 September 2026 21:50, "the glass surface and the top shelf must be at the same level"). The 3 mm plate cannot pocket a
              # 10.66 mm flange, so the plate carries a full-body window and a rear frame takes the 1.2 kg on the VESA 50 pattern.
              recess=True, window=(205.75, 140.09), window_r=15.0, fit=0.3,   # window = body + 0.3 mm per side
              # the rear frame's four M4 in the side bands between the window edge (X +-102.875) and the strips (X +-120): the bottom band
              # is taken by the headset jacks, whose 16 mm holes a corner hole would have fouled by 2.9 mm
              frame_holes=((-110.875, 16.0), (110.875, 16.0), (-110.875, -64.0), (110.875, -64.0)))
EPAPER = dict(c=(0.0, 83.0), window=(94.19, 53.6), lens=(107.19, 66.6), lens_r=3.0, module=(92.99, 53.0), pocket_depth=1.0, depth_below=3.0, tail_side="-X", tail_len=43.9,
              # 9 Sep 2026 (appendix 32.85): the lens was 2.0 mm UV polycarbonate on a 0.4 mm VHB frame in a 1.0 mm pocket, so it stood
              # 1.0 mm proud in the code and about 1.4 as built, against the 0.5 to 0.8 mm of the owner's ruling 14.6. The ruling covers
              # EVERY display surface, so the e-paper takes the C2 recipe of that same section: a 1.0 mm lens on 0.05 mm acrylic transfer
              # tape (3M 467MP or 9495LE) in the same 1.0 mm pocket, which ends 0.05 mm proud. Foam anywhere here breaks the limit.
              lens_t=1.0, tape_t=0.05)   # PDi E2370KS0C1 (32.49 item 11): the same glass size as the WeAct 3.7 (92.99 x 53.0 x 0.85), taped under the lens, its 24-way flex leaves the left short edge toward J_EPD on the top strip. CENTRE Y 78 -> 83 on 9 Sep 2026 (appendix 32.84): at 78 the lens ran from Y 44.700 and the Xenarc body reaches Y 45.745, so the two overlapped by 1.045 mm across the lens' full 107.19 mm width. Both stand proud of the plate (the monitor 28.66 mm, the lens about 2 mm on its tape frame), so they collided; the gap is 3.955 mm now
BUTTONS = [("SW_MAIN", (150.0, 60.0), 19.2, 30.0), ("SW_PI", (150.0, 10.0), 16.2, 28.0), ("SW_TEST", (150.0, -33.0), 16.2, 28.0)]   # ref, centre, plate hole, depth behind the face (C&K ATP19/ATP16 sheets); SW_TEST up 7 mm since C7: its body cleared B16's RockBLOCK bracket by -5 mm at Y -40 (32.60)
TOGGLES = [("SW_SOS", (-150.0, 60.0)), ("SW_EMCON", (-150.0, 18.0)), ("SW_ZERO", (-150.0, -24.0))]                              # APEM 5636ADKB-2V: 6.5 hole with a 2.70 x 1.10 keyway toward the operator (-Y), about 26 deep
TOGGLE_HOLE, TOGGLE_KEY = 6.5, (2.70, 1.10)
LIGHT = ("SW_LIGHT", (-150.0, -66.0))                                                                                              # NKK M2044SD3A01: D hole 6.5 with the 5.8 flat toward +X, about 19 deep
LIGHT_HOLE, LIGHT_FLAT = 6.5, 5.8
SOUNDER = ("BZ1", (-149.0, -97.0), 28.6, 30.0)   # in the corner where the left and bottom strips meet: its body passes the backer there; Floyd Bell MC-09-530-Q class: 28.6 hole, its 61663 gasket, about 30 deep
HEADSETS = [("J_HSJ1", (-118.0, -104.0)), ("J_HSJ2", (-92.0, -104.0))]                                                              # two U-174/U panel jacks in the bottom strip (32.50 items 9 and 16b): 16.0 hole (Amphenol Nexus drawing owed, laptop list), about 30 deep, five leads to D8's J_HS1/J_HS2
HEADSET_HOLE, HEADSET_DEPTH = 16.0, 30.0
STATUS_LEDS = [("D%d" % (k + 1), (128.0, 45.0 - 9.0 * k), name) for k, name in enumerate(["MSTR WARN", "MSTR CAUT", "TX", "SOS ACTIVE", "SAT", "MESH", "LTE", "GPS", "SHORE", "CHARGE", "MSG"])]   # the status column beside the buttons
BAR_LEDS = [("D%d" % (12 + k), (-20.0 + 6.0 * k, -101.0), "BAT%d" % (k + 1)) for k in range(5)]                                     # the battery bar in the bottom strip
LED_HOLE = 2.6                                                                                                                       # Mentor 1282.5004 IP68 front-panel light guide (sheet ll14-14, v2/vendor/mentor/): 2.5 mm shaft pressed into a 2.6 H7 hole, 3.2 mm spherical head on the face, A 7.5 mm reaches 0.2 mm over the 3 mm
LIGHT_SENSOR = ("U_LIGHT", (128.0, 63.0))                                                                                            # VEML7700 on the right strip's top side under its own Mentor light guide (32.50 item 8: the ambient light for blackout and NVG lighting)
CAMERA = ("CAM1", (150.0, 100.0), 8.0, 25.0)                                                                                         # USB camera module (25 x 25 mm board class, sheet owed) on the top strip's top side behind an 8 mm sealed window (32.52: a USB camera behind a plate window on slot 1's hub)
PA_MOUNT = dict(c=(-45.0, 70.0), size=(67.0, 19.4), height=9.9, holes=60.0, hole_d=3.26)                                             # RA30H1317M1 flange on the plate's underside (32.56). 9 Sep 2026 (appendix 32.85): moved from Y 20 to Y 70. It sat dead centre of the
# monitor's footprint, which was harmless while the monitor lay ON the plate and is a 15.8 mm collision now that the body hangs below it.
# It keeps its X and its two PEM S-M3 nuts 60 mm apart, and stays over the ring's open middle (a plate-mounted flange over a backer strip
# would foul the backer, 0.1 mm apart). It now sits 9.0 mm above the CM5 fans: the harness length to D8 and the fan intake are open items.
NAMEPLATE = (78.0, -108.0, 76.0, 26.0)     # laser marked: centre X, centre Y, width, height
LOGO = ((-150.0, 96.0), 36.0)             # laser marked, top of the left strip

# 9 September 2026 (appendix 32.84): the headset jacks moved from Y -101 to -104 and the nameplate from -101 to -108
# because the DISPLAY GREW. The Touch Display 2 this face was laid out around was 189.32 x 120.24 with its bottom edge
# at Y -84.12; the Xenarc 709GNK is 205.15 x 139.49 and its bottom edge sits at Y -93.745, 9.625 mm further south, and
# it stands ON the plate instead of behind an aperture. Nothing re-spaced the furniture around it: J_HSJ2's 16 mm hole
# ran 0.745 mm UNDER the monitor body (the box would have rested over an open hole and broken the face seal) and
# 5.745 mm of the nameplate's marking was hidden beneath it. The bottom band is 31.00 mm now, so this strip is full.

# --- the backer board C7: a ring of four strips outside the monitor and the e-paper window, open in the middle
STRIP_L = (-172.0, -114.0, -120.0, 114.0)  # left strip (toggles); the inner edge at 120 keeps the status LED column at X 128 (4.8 mm courtyard) 5.6 mm from the board edge (C6 run 2 lesson)
STRIP_B = (-172.0, -114.0, 172.0, -88.0)   # bottom strip (sounder, headset jacks, battery bar, the monitor's block notch)
STRIP_R = (120.0, -114.0, 172.0, 114.0)    # right strip (buttons, status LEDs, the light sensor, the drivers)
STRIP_T = (-172.0, 88.0, 172.0, 114.0)     # top strip (C7): the e-paper flex socket and boost, the camera, J_PANEL over B16's header
BLOCK_NOTCH = (-104.0, -94.2, 104.0, -87.0)  # 9 Sep 2026 (appendix 32.85): was (42, -96, 105, -87), a notch for the connector block alone
# while the monitor lay on the plate. Recessed, the whole 205.15 mm body passes the ring, and its south edge at Y -93.745 runs 5.745 mm past
# the void's edge at -88.0, so the notch spans the body's width. Everything on that strip is south of it: the sounder at X -149, the headset
# jacks at Y -104 (their courtyards reach -94.66, 0.46 mm clear of the notch; the notch is only 0.155 mm deeper than the plate window at -94.045, which is all the body needs), the battery bar at Y -101 and the nameplate at Y -108. Only routing width is lost.
STANDOFFS = [(-160.0, 108.0), (160.0, 108.0), (-165.0, -108.0), (165.0, -108.0), (-40.0, -101.0), (20.0, -101.0), (-75.0, 108.0), (75.0, 108.0)]   # M3 self-clinching standoffs in the plate, 10 mm, the backer's screws from below
CLUSTER = (120.0, -114.0, 172.0, -56.0)    # the driver electronics (ICs, transistors, resistors, capacitors) on the underside of the right strip, below SW_TEST's lands
CLUSTER2 = (40.0, -113.0, 116.0, -97.0)    # test points, solder jumpers, ferrites on the underside of the bottom strip, below the block notch
CLUSTER3 = (-116.0, 89.0, -82.0, 113.0)    # C7: the e-paper boost circuit west of the flex socket and the standoff H7, top side of the top strip
J_PANEL_POS = (-116.0, 96.0)              # the ribbon from B16's J_PANEL (2x13 at X -137 to -95, Y 86.5 to 97.5) straight up to the top strip's underside
J_EPD_POS = (-72.0, 94.0)                  # Hirose FH34SRJ-24S ZIF on the top strip's top side, within the flex's 43.9 mm reach from the glass's left edge at (-46.5, 78)
LEAD_LANDS = [("J_MAINSW", (-62.0, -108.0)), ("J_PIJ2", (-44.0, -108.0))]   # moved east of the headset jacks (C7)

TOGGLE_BODY = (15.0, 22.0)                 # slot through the backer for the APEM body
LIGHT_BODY = (15.0, 12.0)                  # slot through the backer for the NKK body
BUTTON_BODY = {"SW_MAIN": 19.2, "SW_PI": 16.2, "SW_TEST": 16.2}   # the C&K bodies pass their own bushing holes (17.4 and 15 wide)
HEADSET_BODY = 17.0                        # hole through the backer for the jack's threaded bushing
CUTOUT_KEEPOUT = 0.6                       # router keep-out around every cut-out (Freerouting ignores the edge clearance of inner cut-outs)

# --- wall jack lists: the single source for scene.py, case_wall_cutouts.py, the case CAD (v2/cad/) and the documents.
# C2 (27 Sep 2026, CASE-MARGINS.md C2 and 3.4): the twelve bulkheads ARE the ruled PolyPhaser GTH-SFF-AL arrestors, bodies outside, axis at
# Z 59, a 31 mm pitch, five on the east wall (the three 5G jacks of D-07, IRIDIUM, LORA) and seven on the west (the WIFI P2P pair moved there
# so that every jumper has a planned route past the pack and the legs). Until 27 Sep 2026: eleven Amphenol 132170 couplers at Z 88.
SMA_Z = 59.0
WALL_WEST = [("VHF", -93.0), ("HF", -62.0), ("WIFI 2.4", -31.0), ("GNSS", 0.0), ("SDR", 31.0), ("WIFI P2P A", 62.0), ("WIFI P2P B", 93.0)]
WALL_EAST = [("5G MAIN", -62.0), ("5G DIV", -31.0), ("5G ANT3", 0.0), ("IRIDIUM", 31.0), ("LORA", 62.0)]
ARRESTOR = dict(part="PolyPhaser GTH-SFF-AL", thread="5/8-24 UNEF-2A", thread_len=0.47 * 25.4, body=(55.0, 23.0, 31.0),
                o_ring_free=0.63, nut_class=(24.0, 5.0))   # sheet and drawing rev B (v2/vendor/polyphaser/, every dimension "for reference only")

# C4: one RF entry plate per end wall, outside, on a 2.0 closed-cell gasket of the same outline; the same outline and screw pattern on both
# walls, five arrestor holes on the east plate and seven on the west. Each arrestor hole 16.3 through, spot-faced SPOT on the plate's BACK so the
# nut and lock washer sit 1.5 lower on the thread (M13); the wall takes a 27 mm hole-saw hole at each site and 5.0 holes at the eight screws.
RF_PLATE = dict(y=110.1, z0=34.55, z1=83.45, t=6.0, gasket=2.0, hole=16.3, spot=(26.0, 1.5), wall_hole=27.0, wall_screw_hole=5.0,
                material="6061-T6 or 5052-H32 aluminium, 6.0 (EN 485 class)", corner_r=3.0,
                screws=[(y, z) for y in (-100.0, -45.0, 45.0, 100.0) for z in (40.65, 77.35)],   # tapped M4 through the plate
                screw="M4 x 12 A2 ISO 7380 button head from inside, on a rubber-faced sealing washer 10 x 1.5 (face 8.0 or more across)")

# C3: one connector plate outside the back wall between the hinge fairings (bases from |X| 58.93), centred at X 0, on a 2.0 closed-cell gasket
# of the same outline; it carries the six ruled items. Centres are case X and Z; each item is laid out as the class its pick must meet
# (CASE-MARGINS.md 3.3 and section 6): 'sq' = a square flange of that side, 'c' = a round body of that diameter.
CONN_PLATE = dict(x0=-57.0, x1=57.0, z0=18.3, z1=86.6, t=5.0, gasket=2.0, corner_r=3.0,
                  material="5052-H32 or 6061-T6 aluminium, 5.0",
                  screws=[(-51.1, 24.2), (-51.1, 50.1), (-51.1, 76.0), (51.1, 24.2), (51.1, 50.1), (51.1, 76.0)],
                  screw_hole=4.5, screw="M4 x 25 A2, a bonded sealing washer 10 across under the head, a plain washer 9.0 and a Nyloc inside")
# Each item: its centre (case X, Z); its flange or body on the plate's face ('sq', side) or ('c', diameter); its mated plug's envelope; the plate
# cut-out; the wall hole; the flange screw pattern (square, hole) on M3 tapped in the plate, or None; how far its inside part stands above
# its centre (the row input of M14a) with what sets it; whether the part is picked. `label` is v2/vendor/peli/frame_seat.py's row label.
CONN_ITEMS = [
    dict(key="A", label="A sealed RJ45 (38999 shell 15 class)", what="sealed RJ45, PoE out: MIL-DTL-38999 shell 15 wall-mount class, 54 V or more (PICK OPEN: the PX0833 fails both)",
         c=(-28.5, 36.6), flange=("sq", 31.29), mated=("c", 32.51), cutout=23.01, wall_hole=29.0, screws=(24.61, 3.35), inside_top=8.0,
         inside_note="patch plug body +-8 (INFERRED)", status="OPEN"),
    dict(key="C", label="C shore DC D38999/20 sh 13", what="shore DC: Glenair D38999/20 shell 13 wall mount, round holes (D0)",
         c=(4.2, 34.0), flange=("sq", 28.9), mated=("c", 29.4), cutout=19.05, wall_hole=22.0, screws=(23.01, 3.45), inside_top=5.0,
         inside_note="cores within the insert +-5 (INFERRED)", status="picked"),
    dict(key="B", label="B sealed USB-C (4000 series class)", what="sealed USB-C 45 W outlet, power only: Bulgin 4000 series rear-panel class (PXP4043/C panel drawing OPEN)",
         c=(33.7, 36.6), flange=("c", 25.67), mated=("c", 26.0), cutout=19.2, wall_hole=29.0, screws=None, inside_top=3.5,
         inside_note="lead 7.0 (INFERRED)", status="OPEN"),
    dict(key="E", label="E pod over the M8 receptacle", what="outside sensor pod on its M8 receptacle (binder 86 6618 1121 00004 recommended, sheet not held)",
         c=(-30.0, 70.0), flange=("sq", 28.0), mated=("sq", 28.0), cutout=10.5, wall_hole=18.0, screws=None, inside_top=5.0,
         inside_note="M8 rear body 10 (INFERRED)", status="OPEN"),
    dict(key="D", label="D USB 233-370 sh 15", what="USB host (console, key fill): Glenair 233-370 shell 15 (D0)",
         c=(4.6, 67.0), flange=("sq", 31.29), mated=("c", 32.51), cutout=23.01, wall_hole=29.0, screws=(24.61, 3.35), inside_top=14.5,
         inside_note="rear body within the 29 hole", status="picked"),
    dict(key="F", label="F ground stud M6", what="ground stud, M6 class: the external earth lead and both RF entry plates' leads outside, the one bonding strap inside",
         c=(34.6, 64.5), flange=("c", 24.0), mated=("c", 24.0), cutout=6.4, wall_hole=8.0, screws=None, inside_top=6.0,
         inside_note="nut and washer 12 (INFERRED)", status="OPEN")]
CONN_B_FLAT = 9.05                        # the 4000 series cut-out: round 18.9/19.2 with one flat 9.0/9.1 from the centre (PXP4043 sheet), the flat toward -Z (INFERRED)

# C5: the QMX tray under the lid's flat ceiling (v2/cad/lid_bracket_qmx.py is the part), 1.5 mm west of its 9 Sep place
QMX_TRAY_X = (102.0, 171.0)

# --- floor items (adjudication A06, CASE-MARGINS.md 3.2 rows M4a to M6): the 4S3P 18650 block, shrink-wrapped, in the east pocket
PACK_BLOCK = (56.65, 133.5, 38.1)         # wrapped, X across the pocket, Y along it, Z up
PACK_WEST_X = 122.0                       # 2.0 from board A's east edge (X 120)
PACK_GROUP_LEN = 205.5                    # block + board P (70) + 2.0, centred in Y between the east legs (M5)

def deep_parts():
    """(ref, centre, depth below the face) for the parts whose bodies hang below the backer's level; check_pcb_c.py gates each against B16_TALL."""
    out = [(r, c, d) for r, c, h, d in BUTTONS] + [(r, c, 26.0) for r, c in TOGGLES] + [(LIGHT[0], LIGHT[1], 19.0), (SOUNDER[0], SOUNDER[1], SOUNDER[3])]
    out += [(r, c, HEADSET_DEPTH) for r, c in HEADSETS]
    if XENARC.get("recess"):
        # 9 Sep 2026 (appendix 32.85): recessed, the whole body hangs below the face and the block is part of it. It is a deep
        # part like any other now, so clearance_report() answers the question a render had to answer for two days.
        out.append(("XENARC_BODY", XENARC["c"], XENARC["height"]))
    else:
        out.append(("XENARC_BLOCK", (XENARC["block"][0], XENARC["block"][1]), PLATE[2] + XENARC["block_depth"]))
    out.append(("PA", PA_MOUNT["c"], PLATE[2] + PA_MOUNT["height"]))
    return out

def deep_part_rect(ref, c, d):
    """The body footprint of a deep part in the case frame (rect) for the clearance check."""
    if ref.startswith("SW_") and ref in BUTTON_BODY: r = BUTTON_BODY[ref] / 2 + 1.0; return (c[0] - r, c[1] - r, c[0] + r, c[1] + r)
    if ref in [t[0] for t in TOGGLES]: w, h = TOGGLE_BODY; return (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)
    if ref == LIGHT[0]: w, h = LIGHT_BODY; return (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)
    if ref == SOUNDER[0]: r = SOUNDER[2] / 2; return (c[0] - r, c[1] - r, c[0] + r, c[1] + r)
    if ref.startswith("J_HSJ"): r = HEADSET_BODY / 2; return (c[0] - r, c[1] - r, c[0] + r, c[1] + r)
    if ref == "XENARC_BLOCK": _, _, w, h = XENARC["block"]; return (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)
    if ref == "XENARC_BODY": w, h = XENARC["body"]; return (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)
    if ref == "PA": w, h = PA_MOUNT["size"]; return (c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)
    return (c[0] - 5, c[1] - 5, c[0] + 5, c[1] + 5)

# the monitor occupies its window, so the WINDOW is the face item: listing the body as well made the two report themselves
FACE_ITEMS = [("XENARC_WINDOW", XENARC["c"], XENARC["window"], "hw")] \
             + [("XFRAME_%d" % k, c, (4.5 + 6.0, 4.5 + 6.0), "hw") for k, c in enumerate(XENARC["frame_holes"], 1)] \
             + [("EPAPER_LENS", EPAPER["c"], EPAPER["lens"], "hw"),
              ("NAMEPLATE", NAMEPLATE[:2], NAMEPLATE[2:], "mark"), ("LOGO", LOGO[0], (LOGO[1], LOGO[1] / 3.0), "mark")] \
             + [(r, c, (d + 6.0, d + 6.0), "hw") for r, c, d, _ in BUTTONS] \
             + [(r, c, (TOGGLE_HOLE + 12.0, TOGGLE_HOLE + 12.0), "hw") for r, c in TOGGLES] \
             + [(LIGHT[0], LIGHT[1], (LIGHT_HOLE + 10.0, LIGHT_HOLE + 10.0), "hw"), (SOUNDER[0], SOUNDER[1], (SOUNDER[2] + 4.0, SOUNDER[2] + 4.0), "hw"),
                (CAMERA[0], CAMERA[1], (CAMERA[2] + 6.0, CAMERA[2] + 6.0), "hw")] \
             + [(r, c, (HEADSET_HOLE, HEADSET_HOLE), "hw") for r, c in HEADSETS] \
             + [(r, c, (LED_HOLE + 1.4, LED_HOLE + 1.4), "hw") for r, c, _ in STATUS_LEDS + BAR_LEDS]
# 9 Sep 2026 (appendix 32.84): everything the FACE carries, as its plan footprint with the collar its part needs
# (a switch bezel, a light guide head, the sounder gasket). clearance_report() above answers a different question,
# a deep face part against a tall board part UNDER the plate, and nothing asked whether two things ON the plate can
# both be there. The monitor and the e-paper lens overlapped by 1.045 mm for two days and only a render showed it.
# The headset jacks carry their documented 16.0 mm hole and NO nut collar: the Amphenol Nexus drawing is still owed
# (32.50 item 9), and their front hardware is the open question of the bottom strip, not something to guess at here.
# "mark" items are laser marking with no height: they cannot collide, they can only be hidden, and are reported apart.

PROUD_LIMIT = 0.8   # owner ruling, appendix 14.6 (2 Sep 2026 21:50): a display surface is level with the plate, at most 0.5 to 0.8 mm proud

def proud_report():
    """How far every DISPLAY surface stands above the plate's top face: (name, mm). The ruling of 14.6 is about the glass the
    operator touches, not about switch bezels or light-guide heads, so only the display surfaces are listed and gated."""
    out = [("XENARC_GLASS", 0.0 if XENARC.get("recess") else XENARC["height"]),
           ("EPAPER_LENS", round(EPAPER["lens_t"] + EPAPER["tape_t"] - EPAPER["pocket_depth"], 3))]
    return [(n, h) for n, h in out if h > PROUD_LIMIT + 1e-9]

def face_overlap_report(want="hw"):
    """Face items overlapping in plan: (a, b, x overlap mm, y overlap mm). want="hw" is the gate (two solid things
    cannot share the plate), want="hidden" reports marking a part covers, want="all" is everything."""
    out = []
    for i in range(len(FACE_ITEMS)):
        an, ac, (aw, ah), ak = FACE_ITEMS[i]
        for j in range(i + 1, len(FACE_ITEMS)):
            bn, bc, (bw, bh), bk = FACE_ITEMS[j]
            ox = min(ac[0] + aw / 2, bc[0] + bw / 2) - max(ac[0] - aw / 2, bc[0] - bw / 2)
            oy = min(ac[1] + ah / 2, bc[1] + bh / 2) - max(ac[1] - ah / 2, bc[1] - bh / 2)
            if ox <= 0 or oy <= 0: continue
            marks = (ak == "mark") + (bk == "mark")
            if want == "hw" and marks: continue
            if want == "hidden" and marks != 1: continue
            out.append((an, bn, round(ox, 3), round(oy, 3)))
    return out

def clearance_report():
    """Every deep part against every tall B16 part it overlaps in plan: (ref, tall name, clearance mm). Negative = collision."""
    out = []
    for ref, c, d in deep_parts():
        bottom_z = FACE_TOP_Z - d; r = deep_part_rect(ref, c, d)
        for (x0, y0, x1, y1), h, name in b16_tall():
            if r[2] <= x0 or r[0] >= x1 or r[3] <= y0 or r[1] >= y1: continue
            out.append((ref, name, round(bottom_z - (B_TOP_Z + h), 1)))
    return out

if __name__ == "__main__":
    for ref, name, clr in clearance_report(): print("%-13s over %-45s clearance %6.1f mm%s" % (ref, name, clr, "" if clr >= 2.0 else "   <-- LESS THAN 2 MM"))
