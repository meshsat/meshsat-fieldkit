"""The face of the MeshSat field kit in the Peli 1450: one source of positions for the aluminium plate (v2/cad/face_plate.py), the C6 backer board
(gen_pcb_c.py, gen_pcb_c3.py, check_pcb_c.py) and the render scene. Case frame: X along the case's long axis, +Y toward the back (hinge) wall, both
from the case centre; the frame window is centred on the case (appendix 32.40 items 4 and 5, 32.42). Plain Python, no KiCad or CAD imports."""

# --- frame 1450PF (measured on Peli's STEP, 32.41 and 32.42)
WINDOW = (349.65, 233.83)                 # the opening; everything visible lies inside it, 3 mm in
PLATE = (365.5, 249.5, 3.0)               # the aluminium face, clamped under the frame ring inside its skirt (366.7 x 250.8)
PLATE_R = 12.0
FRAME_BOSSES = [(-139.4, -121.2), (139.4, -121.2), (0.0, -121.2), (-139.4, 121.2), (139.4, 121.2), (0.0, 121.2), (-179.1, -75.9), (179.1, -75.9), (-179.1, 75.9), (179.1, 75.9)]   # M3 into the frame's inserts, from below
BAND = 8.0                                # the plate's band under the frame ring: the PORON gasket ring lives here, nothing else

# --- the stack under the face (v2/cad/stack-heightmap.json): PCB-B's outline is X +-122.5, Y +-85; deep parts stay outside it
B_OUTLINE = (-122.5, -85.0, 122.5, 85.0)
FACE_TOP_Z = 101.4                        # above the case floor (base 109.4, lip 8)
PLATE_UNDER_Z = FACE_TOP_Z - PLATE[2]
BACKER_GAP = 10.0                         # standoff height between the plate's underside and the backer's top
BACKER_T = 1.6

# --- the face elements (centre X, centre Y in the case frame)
DISPLAY = dict(c=(0.0, -24.0), glass=(189.32, 120.24), aperture=(169.35, 100.51), aperture_r=1.5, pocket_depth=1.0, depth_below=7.0)     # Touch Display 2, the aperture of 32.34 (body + 0.4)
EPAPER = dict(c=(0.0, 70.0), window=(94.19, 53.6), lens=(107.19, 66.6), lens_r=3.0, module=(105.79, 53.80), pocket_depth=1.0, depth_below=12.0)  # WeAct 3.7 under a 2 mm lens, its board on the module's back
BUTTONS = [("SW_MAIN", (150.0, 60.0), 19.2, 30.0), ("SW_PI", (150.0, 10.0), 16.2, 28.0), ("SW_TEST", (150.0, -40.0), 16.2, 28.0)]   # ref, centre, plate hole, depth behind the face (C&K ATP19/ATP16 sheets)
TOGGLES = [("SW_SOS", (-150.0, 60.0)), ("SW_EMCON", (-150.0, 18.0)), ("SW_ZERO", (-150.0, -24.0))]                              # APEM 5636ADKB-2V: 6.5 hole with a 2.70 x 1.10 keyway toward the operator (-Y), about 26 deep
TOGGLE_HOLE, TOGGLE_KEY = 6.5, (2.70, 1.10)
LIGHT = ("SW_LIGHT", (-150.0, -66.0))                                                                                              # NKK M2044SD3A01: D hole 6.5 with the 5.8 flat toward +X, about 19 deep
LIGHT_HOLE, LIGHT_FLAT = 6.5, 5.8
SOUNDER = ("BZ1", (-112.0, -97.0), 28.6, 30.0)                                                                                     # Floyd Bell MC-09-530-Q class: 28.6 hole, its 61663 gasket, about 30 deep
STATUS_LEDS = [("D%d" % (k + 1), (128.0, 45.0 - 9.0 * k), name) for k, name in enumerate(["MSTR WARN", "MSTR CAUT", "TX", "SOS ACTIVE", "SAT", "MESH", "LTE", "GPS", "SHORE", "CHARGE", "MSG"])]   # the status column beside the buttons
BAR_LEDS = [("D%d" % (12 + k), (-20.0 + 6.0 * k, -101.0), "BAT%d" % (k + 1)) for k in range(5)]                                     # the battery bar in the bottom strip
LED_HOLE = 4.0                                                                                                                       # press-fit 3 mm light pipe (IP67 part to be named from its sheet)
NAMEPLATE = (78.0, -101.0, 76.0, 26.0)     # laser marked: centre X, centre Y, width, height
LOGO = ((-150.0, 100.0), 40.0)             # laser marked, top of the left strip

# --- the backer board C6: a U in the strips outside PCB-B's outline, open over the display and the e-paper
STRIP_L = (-172.0, -114.0, -126.0, 114.0)  # left strip (toggles)
STRIP_B = (-172.0, -114.0, 172.0, -88.0)   # bottom strip (sounder, battery bar)
STRIP_R = (126.0, -114.0, 172.0, 114.0)    # right strip (buttons, status LEDs, the drivers, the ribbon)
STANDOFFS = [(-150.0, 108.0), (150.0, 108.0), (-150.0, -108.0), (150.0, -108.0), (-40.0, -101.0), (20.0, -101.0)]   # M3 self-clinching standoffs in the plate, 10 mm, the backer's screws from below
CLUSTER = (128.0, -114.0, 172.0, -52.0)    # the driver electronics on the underside of the right strip, below SW_TEST
J_PANEL_POS = (150.0, 100.0)               # the ribbon from PCB-B's J_PANEL at (82 to 91, 51 to 85), right-angle IDC toward -Y
J_EPD_POS = (130.0, 112.0)                 # the e-paper's own 8-pin lead from the module at the top centre
LEAD_LANDS = [("J_MAINSW", (-100.0, -108.0)), ("J_PIJ2", (-80.0, -108.0))]

def deep_parts():
    """(ref, centre, depth below the face) for the parts whose bodies hang below the backer's level: every one must sit outside PCB-B's outline."""
    out = [(r, c, d) for r, c, h, d in BUTTONS] + [(r, c, 26.0) for r, c in TOGGLES] + [(LIGHT[0], LIGHT[1], 19.0), (SOUNDER[0], SOUNDER[1], SOUNDER[3])]
    return out
