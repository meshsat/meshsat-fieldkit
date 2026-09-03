"""
MeshSat Field Kit — FreeCAD Build Script
=========================================

Kyriakos Papadopoulos (AS214304) — 2026

USAGE:
  1. Open FreeCAD
  2. Create new document: File > New (Ctrl+N)
  3. Open macro editor: Macro > Macros... > Create
  4. Paste this entire file into the macro
  5. Execute (F6 or green play button)

  OR from terminal:
    freecad --console
    exec(open('/path/to/field_kit_build.py').read())

  OR run once to generate and save:
    freecadcmd field_kit_build.py

OUTPUT:
  - Complete 3D model of the field kit
  - All three scaffold floors with hole positions
  - All major components placed in their final positions
  - Case outline (approximate) for reference
  - Saves as field_kit.FCStd in the same directory

EDIT DIMENSIONS:
  All dimensions are parameterized in field_kit_config.py.
  Change values there, re-run to regenerate.
"""

import FreeCAD as App
import Part
from FreeCAD import Vector, Rotation, Placement
import os
import sys

# Make field_kit_config.py importable when run as a macro or via freecadcmd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from field_kit_config import *

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def make_box(name, length, width, height, x=0, y=0, z=0, color=(0.5, 0.5, 0.5)):
    """Create a labeled rectangular box at the given position."""
    box = doc.addObject("Part::Box", name)
    box.Length = length
    box.Width = width
    box.Height = height
    box.Placement = Placement(Vector(x, y, z), Rotation())
    box.ViewObject.ShapeColor = color
    return box

def make_cylinder(name, radius, height, x=0, y=0, z=0, color=(0.7, 0.7, 0.7)):
    """Create a labeled cylinder at the given position."""
    cyl = doc.addObject("Part::Cylinder", name)
    cyl.Radius = radius
    cyl.Height = height
    cyl.Placement = Placement(Vector(x, y, z), Rotation())
    cyl.ViewObject.ShapeColor = color
    return cyl

def make_plate_with_holes(name, length, width, thickness, z, hole_positions, color):
    """
    Create a rectangular plate centered in the case, with holes drilled.
    Returns the resulting shape as an object.

    length, width, thickness — plate dimensions
    z — vertical position of plate's bottom surface
    hole_positions — list of (x, y, diameter) tuples in plate-local coords
    """
    # Centre plate on the world origin (case is centred on origin too).
    x = -length / 2.0
    y = -width / 2.0

    plate = Part.makeBox(length, width, thickness, Vector(x, y, z))

    # Cut each hole
    for (hx, hy, hd) in hole_positions:
        hole = Part.makeCylinder(hd / 2.0, thickness + 0.2,
                                  Vector(x + hx, y + hy, z - 0.1))
        plate = plate.cut(hole)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = plate
    obj.ViewObject.ShapeColor = color
    return obj

def plate_rod_holes(plate_length, plate_width):
    """Plate-local (x, y, dia) hole positions matching ROD_POSITIONS.
    Every plate is drilled at the same absolute rod positions, so holes line
    up with the straight rods regardless of the plate's own footprint. The
    model is built in a case-centred frame, so each plate's back-left corner
    sits at (-plate_length/2, -plate_width/2) in world coords."""
    plate_x = -plate_length / 2.0
    plate_y = -plate_width / 2.0
    return [
        (rx - plate_x, ry - plate_y, M3_HOLE_DIAMETER)
        for (rx, ry) in ROD_POSITIONS
    ]

# ============================================================
# DOCUMENT SETUP
# ============================================================

# Get or create document
doc_name = "Field_Kit"
if App.ActiveDocument and App.ActiveDocument.Name == doc_name:
    doc = App.ActiveDocument
    # Clear existing objects
    for obj in list(doc.Objects):
        doc.removeObject(obj.Name)
else:
    doc = App.newDocument(doc_name)

# ============================================================
# CASE OUTLINE (reference wireframe, not a solid)
# ============================================================

case_ref = doc.addObject("Part::Feature", "Case_Boundary")
case_ref.Shape = Part.makeBox(CASE_INTERNAL_L, CASE_INTERNAL_W, CASE_INTERNAL_H,
                               Vector(-CASE_INTERNAL_L / 2.0,
                                      -CASE_INTERNAL_W / 2.0,
                                      -CASE_INTERNAL_H / 2.0))
case_ref.ViewObject.ShapeColor = (0.2, 0.2, 0.2)
case_ref.ViewObject.Transparency = 90  # Nearly transparent
case_ref.ViewObject.DisplayMode = "Wireframe"

# ============================================================
# BOTTOM FLOOR (z = 0)
# ============================================================

bottom_holes = plate_rod_holes(BOTTOM_FLOOR_L, BOTTOM_FLOOR_W)
# Bottom plate sits directly on the case floor — no cable pass-through needed.

bottom_plate = make_plate_with_holes(
    "Floor_Bottom",
    BOTTOM_FLOOR_L, BOTTOM_FLOOR_W, FLOOR_THICKNESS,
    Z_BOTTOM,
    bottom_holes,
    color=(0.15, 0.15, 0.15)  # nearly black HDPE
)

# ============================================================
# BOTTOM FLOOR COMPONENTS
# ============================================================

# Plate back-left corner in world coords (case-centred frame → plate centred on origin).
bp_x = -BOTTOM_FLOOR_L / 2.0
bp_y = -BOTTOM_FLOOR_W / 2.0
Z_ON_BOTTOM = Z_BOTTOM + FLOOR_THICKNESS

# X1202 UPS (west side of bottom floor)
x1202 = make_box(
    "X1202_UPS",
    X1202_L, X1202_W, X1202_H,
    x=bp_x + 20,
    y=bp_y + (BOTTOM_FLOOR_W - X1202_W) / 2,
    z=Z_ON_BOTTOM,
    color=(0.3, 0.2, 0.7)  # purple
)

# UV-K5 + AIOC brick (east side)
uvk5 = make_box(
    "UV-K5",
    UVK5_L, UVK5_W, UVK5_H,
    x=bp_x + BOTTOM_FLOOR_L - UVK5_L - 15,
    y=bp_y + (BOTTOM_FLOOR_W - UVK5_W) / 2,
    z=Z_ON_BOTTOM,
    color=(0.55, 0.35, 0.1)  # amber
)

# AIOC plugged into UV-K5 side jacks (sticks out)
aioc = make_box(
    "AIOC",
    AIOC_L, AIOC_W, AIOC_H,
    x=bp_x + BOTTOM_FLOOR_L - 15 + 5,  # extends beyond UV-K5 body
    y=bp_y + (BOTTOM_FLOOR_W - AIOC_W) / 2 + 10,
    z=Z_ON_BOTTOM + 10,
    color=(0.45, 0.25, 0.1)
)

# Sabrent USB hub (southwest corner, near X1202)
hub = make_box(
    "USB_Hub",
    HUB_L, HUB_W, HUB_H,
    x=bp_x + 20,
    y=bp_y + 10,
    z=Z_ON_BOTTOM,
    color=(0.1, 0.5, 0.4)  # teal
)

# GPS puck (southeast)
gps = make_box(
    "GPS",
    GPS_L, GPS_W, GPS_H,
    x=bp_x + BOTTOM_FLOOR_L - GPS_L - 30,
    y=bp_y + 15,
    z=Z_ON_BOTTOM,
    color=(0.4, 0.4, 0.4)  # gray
)

# ============================================================
# MIDDLE FLOOR
# ============================================================

middle_holes = plate_rod_holes(MIDDLE_FLOOR_L, MIDDLE_FLOOR_W)
# Add pass-through
middle_holes.append((MIDDLE_FLOOR_L / 2, MIDDLE_FLOOR_W / 2, 15.0))

middle_plate = make_plate_with_holes(
    "Floor_Middle",
    MIDDLE_FLOOR_L, MIDDLE_FLOOR_W, FLOOR_THICKNESS,
    Z_MIDDLE,
    middle_holes,
    color=(0.15, 0.15, 0.15)
)

# ============================================================
# MIDDLE FLOOR COMPONENTS
# ============================================================

mp_x = -MIDDLE_FLOOR_L / 2.0
mp_y = -MIDDLE_FLOOR_W / 2.0
Z_ON_MIDDLE = Z_MIDDLE + FLOOR_THICKNESS

# LilyGO T-Call (SW corner)
tcall = make_box(
    "LilyGO_TCall_A7670E",
    TCALL_L, TCALL_W, TCALL_H,
    x=mp_x + 15,
    y=mp_y + 15,
    z=Z_ON_MIDDLE,
    color=(0.6, 0.2, 0.1)  # red-orange
)

# RTL-SDR V4 (center-east, opposite diagonal from T-Call)
rtlsdr = make_box(
    "RTL_SDR_V4",
    RTLSDR_L, RTLSDR_W, RTLSDR_H,
    x=mp_x + MIDDLE_FLOOR_L / 2 + 20,
    y=mp_y + MIDDLE_FLOOR_W / 2 - RTLSDR_W / 2,
    z=Z_ON_MIDDLE,
    color=(0.6, 0.2, 0.35)  # pink
)

# XIAO ZigBee (NW)
xiao = make_box(
    "XIAO_ZigBee",
    XIAO_L, XIAO_W, XIAO_H,
    x=mp_x + 15,
    y=mp_y + MIDDLE_FLOOR_W - XIAO_W - 15,
    z=Z_ON_MIDDLE,
    color=(0.1, 0.4, 0.7)  # blue
)

# DCF77 + ferrite (N, E-W orientation)
dcf77 = make_box(
    "DCF77_Ferrite",
    DCF77_L, DCF77_W, DCF77_H,
    x=mp_x + (MIDDLE_FLOOR_L - DCF77_L) / 2,
    y=mp_y + MIDDLE_FLOOR_W - DCF77_W - 15,
    z=Z_ON_MIDDLE,
    color=(0.25, 0.45, 0.1)  # green
)

# RockBLOCK 9603 (SE)
rockblock = make_box(
    "RockBLOCK_9603",
    ROCKBLOCK_L, ROCKBLOCK_W, ROCKBLOCK_H,
    x=mp_x + MIDDLE_FLOOR_L - ROCKBLOCK_L - 15,
    y=mp_y + 15,
    z=Z_ON_MIDDLE,
    color=(0.55, 0.2, 0.1)  # coral
)

# ============================================================
# TOP FLOOR
# ============================================================

top_holes = plate_rod_holes(TOP_FLOOR_L, TOP_FLOOR_W)

# LED holes (5× 8mm in a row on top edge strip)
led_spacing = 20  # mm between LED centers
led_y = TOP_FLOOR_W - 15  # 15mm from top edge
led_x_start = (TOP_FLOOR_L - (4 * led_spacing)) / 2
for i in range(5):
    top_holes.append((led_x_start + i * led_spacing, led_y, LED_HOLE_DIAMETER))

# DSI ribbon pass-through for Pi underneath
top_holes.append((TOP_FLOOR_L / 2 - 20, TOP_FLOOR_W / 2 + 10, 20.0))

top_plate = make_plate_with_holes(
    "Floor_Top",
    TOP_FLOOR_L, TOP_FLOOR_W, FLOOR_THICKNESS,
    Z_TOP,
    top_holes,
    color=(0.15, 0.15, 0.15)
)

# ============================================================
# TOP FLOOR — DISPLAY (above plate) AND Pi 5 (below plate)
# ============================================================

tp_x = -TOP_FLOOR_L / 2.0
tp_y = -TOP_FLOOR_W / 2.0

# Display on top of top plate
display = make_box(
    "Pi_Touch_Display_2",
    DISPLAY_L, DISPLAY_W, DISPLAY_THICKNESS,
    x=tp_x + (TOP_FLOOR_L - DISPLAY_L) / 2,
    y=tp_y + (TOP_FLOOR_W - DISPLAY_W) / 2 - 10,  # shift south
    z=Z_TOP + FLOOR_THICKNESS + DISPLAY_PROTRUSION - DISPLAY_THICKNESS,
    color=(0.05, 0.15, 0.3)  # dark blue
)

# Pi 5 on underside of top plate (face down)
pi5 = make_box(
    "Pi5_underside",
    PI5_L, PI5_W, PI5_H,
    x=tp_x + (TOP_FLOOR_L - PI5_L) / 2,
    y=tp_y + (TOP_FLOOR_W - PI5_W) / 2 - 10,
    z=Z_TOP - PI5_STANDOFF_H - PI5_H,  # hangs below top plate via standoffs
    color=(0.06, 0.43, 0.34)  # teal green
)

# ============================================================
# M3 RODS (4 corners, spanning from bottom to top plate)
# ============================================================

for i, (rx, ry) in enumerate(ROD_POSITIONS):
    rod = make_cylinder(
        f"M3_Rod_{i+1}",
        ROD_DIAMETER / 2, ROD_LENGTH,
        x=rx, y=ry, z=Z_CASE_FLOOR,
        color=(0.7, 0.7, 0.75)  # stainless silver
    )

# ============================================================
# M3 NUTS — 2 per plate per rod (one on each face), 24 total
# ============================================================
# Each rod carries 6 nuts (below/above each of 3 plates). Nut is a short
# cylinder of diameter NUT_OD (real nut is hex; cylinder is adequate for
# bounding-box visualisation). Color matches ROD but slightly darker so
# nuts read as distinct elements.
_NUT_STACK = [
    (Z_CASE_FLOOR,                "P1B"),  # below bottom plate
    (Z_BOTTOM + FLOOR_THICKNESS,  "P1A"),  # above bottom plate
    (Z_MIDDLE - NUT_H,            "P2B"),  # below middle plate
    (Z_MIDDLE + FLOOR_THICKNESS,  "P2A"),  # above middle plate
    (Z_TOP    - NUT_H,            "P3B"),  # below top plate
    (Z_TOP    + FLOOR_THICKNESS,  "P3A"),  # above top plate
]
for i, (rx, ry) in enumerate(ROD_POSITIONS):
    for z_base, pos_code in _NUT_STACK:
        make_cylinder(
            f"M3_Nut_R{i+1}_{pos_code}",
            NUT_OD / 2.0, NUT_H,
            x=rx, y=ry, z=z_base,
            color=(0.5, 0.5, 0.55)
        )

# ============================================================
# FINALIZE
# ============================================================

doc.recompute()

# Fit view to entire model
try:
    import FreeCADGui as Gui
    Gui.SendMsgToActiveView("ViewFit")
    Gui.activeDocument().activeView().viewIsometric()
except Exception:
    pass  # Running headless

# Save to disk
save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "field_kit.FCStd")
try:
    doc.saveAs(save_path)
    print(f"✓ Saved model to: {save_path}")
except Exception as e:
    print(f"Could not save: {e}")
    print("Manually save via File > Save As")

print("✓ Field kit model generated")
# Heights are measured from the case interior floor (Z = Z_BOTTOM in the
# centred frame); not absolute Z.
stack_height = (Z_TOP + FLOOR_THICKNESS + DISPLAY_THICKNESS) - Z_BOTTOM
print(f"  Total stack height: {stack_height:.1f}mm (top of display above case floor)")
print(f"  Case interior: {CASE_INTERNAL_H}mm")
print(f"  Headroom: {CASE_INTERNAL_H - stack_height:.1f}mm")
