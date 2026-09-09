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
bay on B16 clears the toggle bodies under the left strip."""

# --- frame 1450PF (measured on Peli's STEP, 32.41 and 32.42)
WINDOW = (349.65, 233.83)                 # the opening; everything visible lies inside it, 3 mm in
PLATE = (365.5, 249.5, 3.0)               # the aluminium face, clamped under the frame ring inside its skirt (366.7 x 250.8)
PLATE_R = 12.0
FRAME_BOSSES = [(-139.4, -121.2), (139.4, -121.2), (0.0, -121.2), (-139.4, 121.2), (139.4, 121.2), (0.0, 121.2), (-179.1, -75.9), (179.1, -75.9), (-179.1, 75.9), (179.1, 75.9)]   # M3 into the frame's inserts, from below
BAND = 8.0                                # the plate's band under the frame ring: the PORON gasket ring lives here, nothing else

# --- the stack under the face: B16's outline is X +-165, Y +-100 (32.58); the strips lie over its edge bands, so B16_TALL gates the deep parts
B_OUTLINE = (-165.0, -100.0, 165.0, 100.0)
B_TOP_Z = 49.5                            # B16's top copper above the case floor (32.56; 56.0 until 9 Sep 2026, appendix 32.85: the recessed
                                          # monitor's body bottom is Z 72.74 and the CM5 heatsinks topped at 77.0, so the board drops 6.5 mm.
                                          # The room is there: the tallest thing under B16 is D8's SA868 at Z 27.4 and B16's underside was 54.6.
FACE_TOP_Z = 101.4                        # above the case floor (base 109.4, lip 8)
PLATE_UNDER_Z = FACE_TOP_Z - PLATE[2]
BACKER_GAP = 10.0                         # standoff height between the plate's underside and the backer's top
BACKER_T = 1.6
BACKER_UNDER_Z = PLATE_UNDER_Z - BACKER_GAP - BACKER_T
# B16's tall parts (case mm rect, height above B16's top copper), from gen_pcb_b.py's floor plan (32.58, 32.59): the deep face parts must clear them
# 9 Sep 2026 (appendix 32.85): each CM5 site was ONE 30 mm envelope covering cooler and fan, which is why the recessed monitor read as a
# 13.3 mm collision against all three. The heatsink is 21.0 mm (module 4.62 + 1.24, base 4.0, fins 8.7 from scene.py:288-290) over the whole
# 56 mm site; the fan is the 30 mm part and it only needs to sit NORTH of the monitor's edge at Y +45.745, so it moves from cy 60 to cy 63
# (Y 48 .. 78, clear by 2.255 mm). The no-vent ruling of 7 Sep keeps its fan per cooler; only its position changes.
B16_TALL = [((-93.0, 32.0, -52.0, 88.0), 21.0, "CM5 slot 1 heatsink"), ((-23.0, 32.0, 18.0, 88.0), 21.0, "CM5 slot 2 heatsink"), ((47.0, 32.0, 88.0, 88.0), 21.0, "CM5 slot 3 heatsink"),
            ((-87.5, 48.0, -57.5, 78.0), 30.0, "CM5 slot 1 fan"), ((-17.5, 48.0, 12.5, 78.0), 30.0, "CM5 slot 2 fan"), ((52.5, 48.0, 82.5, 78.0), 30.0, "CM5 slot 3 fan"),
            ((-162.0, 81.0, -142.0, 98.0), 14.0, "J_ETH RJ45"), ((-161.5, 58.5, -142.5, 77.5), 7.0, "T1 magnetics"), ((-137.0, 86.0, -95.0, 98.0), 9.5, "J_PANEL 2x13"),
            ((130.0, -43.0, 161.0, 45.0), 12.0, "LimeSDR Mini in J_LIME"), ((113.0, -99.0, 165.0, -43.0), 21.0, "RockBLOCK 9704 on its bracket"), ((96.0, -100.0, 113.0, -86.0), 7.0, "J_HDMI"),
            ((-152.0, -97.0, -116.0, -69.0), 10.0, "west headers J_54V, J_QMX, F3"), ((144.0, 55.0, 148.0, 67.0), 9.5, "J_CAM header"), ((125.5, 45.5, 162.0, 67.0), 5.0, "radio modules"),
            ((-98.0, -97.0, 94.0, -21.0), 6.0, "slot columns: switches, hubs, rails, M.2 sockets"), ((-35.0, -30.0, 91.0, 31.0), 4.5, "M.2 cards")]

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
BLOCK_NOTCH = (-104.0, -95.0, 104.0, -87.0)  # 9 Sep 2026 (appendix 32.85): was (42, -96, 105, -87), a notch for the connector block alone
# while the monitor lay on the plate. Recessed, the whole 205.15 mm body passes the ring, and its south edge at Y -93.745 runs 5.745 mm past
# the void's edge at -88.0, so the notch spans the body's width. Everything on that strip is south of it: the sounder at X -149, the headset
# jacks at Y -104 (their 16 mm holes reach -96, 1.0 mm clear), the battery bar at Y -101 and the nameplate at Y -108. Only routing width is lost.
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

# --- wall jack lists (32.56 and 32.58): the single source for scene.py, case_wall_cutouts.py and the documents; SMA bulkheads at Z 88
SMA_Z = 88.0
WALL_WEST = [("VHF", -72.0), ("HF", -48.0), ("WIFI 2.4", -24.0), ("GNSS", 24.0), ("SDR", 72.0)]
WALL_EAST = [("5G MAIN", -96.0), ("5G DIV", -72.0), ("IRIDIUM", -48.0), ("LORA", -24.0), ("WIFI P2P A", 48.0), ("WIFI P2P B", 96.0)]

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
        for (x0, y0, x1, y1), h, name in B16_TALL:
            if r[2] <= x0 or r[0] >= x1 or r[3] <= y0 or r[1] >= y1: continue
            out.append((ref, name, round(bottom_z - (B_TOP_Z + h), 1)))
    return out

if __name__ == "__main__":
    for ref, name, clr in clearance_report(): print("%-13s over %-45s clearance %6.1f mm%s" % (ref, name, clr, "" if clr >= 2.0 else "   <-- LESS THAN 2 MM"))
