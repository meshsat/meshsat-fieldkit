"""
MeshSat Field Kit — STEP File Generator
========================================

Generates field_kit.step using build123d.
This STEP file opens in FreeCAD, Fusion 360, SolidWorks, OnShape,
SolvEspace, or any modern CAD tool.

USAGE:
  python3 field_kit_step.py

OUTPUT:
  field_kit.step — portable 3D model file
"""

import os
import sys

# Make field_kit_config.py importable regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from field_kit_config import *

from build123d import (
    BuildPart, BuildSketch, Box, Cylinder, Sphere, Align, Mode, Location, Locations,
    export_step, Compound, Color, Text, extrude, Plane, Axis, Vector,
    RectangleRounded, Edge, Wire, Circle, sweep, Transition,
)

# NOTE on placement: in build123d, Box(...).locate(Location(...)) inside a
# BuildPart context is silently discarded — the .locate() return value isn't
# added back to the builder. Use `with Locations(Location((x, y, z))):` blocks
# around every primitive that needs to sit off-origin.

# NOTE on coordinate frame: the model is built in a case-centred frame —
# case centre at world origin, X in [-L/2, +L/2], Y in [-W/2, +W/2], Z in
# [-H/2, +H/2]. Every plate/component position is derived from that centre.
# This is what makes `freecad field_kit.step` open with the model visible
# instead of the camera landing on the back-left-bottom corner. Do NOT
# translate the final assembly after the fact — that drops per-part labels
# during STEP export (exporter writes generic "SOLID"/"ASSEMBLY" entries).

# ============================================================
# COLORS — assigned per part, written into STEP via styled_item
# ============================================================

CLR_HDPE      = Color(0.15, 0.15, 0.15)   # near-black scaffold plates
CLR_CASE      = Color(0.22, 0.22, 0.22)   # case shell
CLR_ROD       = Color(0.70, 0.70, 0.75)   # stainless silver
CLR_X1202     = Color(0.30, 0.20, 0.70)   # purple
CLR_UVK5      = Color(0.55, 0.35, 0.10)   # amber
CLR_HUB       = Color(0.10, 0.50, 0.40)   # teal
CLR_GPS       = Color(0.40, 0.40, 0.40)   # gray
CLR_TCALL     = Color(0.60, 0.20, 0.10)   # red-orange
CLR_RTLSDR    = Color(0.60, 0.20, 0.35)   # pink
CLR_XIAO      = Color(0.10, 0.40, 0.70)   # blue — XIAO Meshtastic
CLR_SONOFF    = Color(0.90, 0.90, 0.90)   # white plastic — Sonoff ZBDongle shell
CLR_DCF77     = Color(0.25, 0.45, 0.10)   # green
CLR_ROCKBLOCK = Color(0.55, 0.20, 0.10)   # coral
CLR_PI5       = Color(0.06, 0.43, 0.34)   # teal green
CLR_DISPLAY   = Color(0.05, 0.15, 0.30)   # dark blue
CLR_NUT       = Color(0.50, 0.50, 0.55)   # slightly darker silver than rods
CLR_LABEL     = Color(0.95, 0.95, 0.95)   # near-white text, contrasts components
CLR_LATCH     = Color(0.70, 0.70, 0.72)   # chrome
CLR_HANDLE    = Color(0.10, 0.10, 0.10)   # black rubber grip
CLR_VALVE     = Color(0.18, 0.18, 0.20)   # dark plastic
CLR_ANTENNA   = Color(0.08, 0.08, 0.08)   # black rubber whip
CLR_SMA       = Color(0.75, 0.70, 0.40)   # brass SMA connector
CLR_RF_CABLE  = Color(0.05, 0.05, 0.05)   # black RG-316/RG-174 pigtail
CLR_DSI       = Color(0.85, 0.78, 0.55)   # cream/tan FFC ribbon
CLR_USB_CABLE   = Color(0.12, 0.12, 0.12)   # black USB cable jacket
CLR_GPIO_CABLE  = Color(0.85, 0.55, 0.10)   # orange jumper/GPIO bundle
CLR_POWER_CABLE = Color(0.55, 0.10, 0.10)   # red X1202 power output
CLR_WIFI        = Color(0.20, 0.20, 0.20)   # matte black WiFi stick shell


# ============================================================
# DEVICE FACE LABELS (extruded text on all 6 faces per device)
# ============================================================
# Implementation: build the text once on the default XY plane (letters with
# +X reading, +Y up, extruded in +Z), then apply explicit shape-level
# transforms to orient it onto each face. For the ±Y faces, aligning the
# text frame to (viewer_right, viewer_up, outward_normal) requires a
# reflection (determinant = -1), so we pre-mirror the shape with
# `Shape.mirror(Plane.XZ)` (flips the text's Y) before rotating. ±X and ±Z
# face mappings are pure right-handed rotations.
#
# Per-face spec: (suffix, mirror_before_rotate, (axis, angle_deg) rotations
# applied in order, center_frac, w_idx, h_idx).
_LABEL_DEPTH = 0.3
_LABEL_PADDING = 0.85            # fraction of face used by text
_LABEL_REF_FONT = 10.0           # arbitrary reference size for bbox probe

_FACE_SPECS = [
    # suffix, needs_y_flip, rotations [(axis, angle_deg), ...], center_frac, w_idx, h_idx
    # Viewer right-hand conventions (when facing that face from outside):
    #   +Y face: viewer at +Y facing -Y → right = -X (facing south, right is west)
    #   -Y face: viewer at -Y facing +Y → right = +X
    #   +X face: viewer at +X facing -X → right = +Y (facing west, right is north)
    #   -X face: viewer at -X facing +X → right = -Y
    #   +Z face: viewer above looking down, up=+Y → right = +X
    #   -Z face: viewer below looking up, up=+Y → right = +X (flip via X axis)
    # Target: text (X,Y,Z) → world (viewer_right, viewer_up, outward_normal).
    # All six transforms turn out to be pure right-handed rotations.
    # +Y face: text (X,Y,Z) → world (-X, Z, Y). 180° about (0,1,1).
    ("pY", False, [((0, 1, 1), 180)],                   (0.5, 1.0, 0.5), 0, 2),
    # -Y face: text (X,Y,Z) → world (X, Z, -Y). R(X, +90).
    ("nY", False, [(Axis.X, 90)],                       (0.5, 0.0, 0.5), 0, 2),
    # +X face: text (X,Y,Z) → world (Y, Z, X). 120° about (1,1,1).
    ("pX", False, [((1, 1, 1), 120)],                   (1.0, 0.5, 0.5), 1, 2),
    # -X face: text (X,Y,Z) → world (-Y, Z, -X). 120° about (1,-1,-1).
    ("nX", False, [((1, -1, -1), 120)],                 (0.0, 0.5, 0.5), 1, 2),
    # +Z face: text (X,Y,Z) → world (X, Y, Z). Identity.
    ("pZ", False, [],                                   (0.5, 0.5, 1.0), 0, 1),
    # -Z face: text (X,Y,Z) → world (X, -Y, -Z). R(X, 180).
    ("nZ", False, [(Axis.X, 180)],                      (0.5, 0.5, 0.0), 0, 1),
]


def _fit_font_size(text, face_w, face_h):
    """Build a probe sketch at a reference font size, measure its bbox, and
    return the font size that makes the text fill `_LABEL_PADDING` of the
    given face dims."""
    with BuildSketch() as probe:
        Text(text, font_size=_LABEL_REF_FONT, align=(Align.CENTER, Align.CENTER))
    bb = probe.sketch.bounding_box()
    tw, th = bb.size.X, bb.size.Y
    if tw <= 0 or th <= 0:
        return _LABEL_REF_FONT
    scale = min(face_w * _LABEL_PADDING / tw,
                face_h * _LABEL_PADDING / th)
    return _LABEL_REF_FONT * scale


def _apply_rotations(shape, rotations):
    for axis_spec, angle in rotations:
        if isinstance(axis_spec, tuple):
            axis = Axis((0, 0, 0), axis_spec)
        else:
            axis = axis_spec
        shape = shape.rotate(axis, angle)
    return shape


def _add_device_labels(name, L, W, H, x, y, z):
    """Append 6 extruded-text label parts (one per face) for a device whose
    MIN corner is at (x, y, z) and extents are (L, W, H)."""
    dims = (L, W, H)
    for suffix, needs_y_flip, rotations, (fx, fy, fz), wi, hi in _FACE_SPECS:
        face_w, face_h = dims[wi], dims[hi]
        font_size = _fit_font_size(name, face_w, face_h)
        if font_size < 0.2:
            continue  # would render as noise

        # Build text on default XY plane, extrude +Z
        with BuildPart() as tp:
            with BuildSketch() as sk:
                Text(name, font_size=font_size,
                     align=(Align.CENTER, Align.CENTER))
            extrude(amount=_LABEL_DEPTH)
        shape = tp.part

        # Pre-mirror for faces that need a reflection component
        if needs_y_flip:
            shape = shape.mirror(Plane.XZ)  # flip Y in text frame

        # Apply rotations to orient text onto target face
        shape = _apply_rotations(shape, rotations)

        # Translate to face centre
        world_center = (x + L * fx, y + W * fy, z + H * fz)
        shape = shape.translate(Vector(*world_center))

        shape.label = f"{name}_lbl_{suffix}"
        shape.color = CLR_LABEL
        parts.append(shape)

# ============================================================
# BUILD
# ============================================================

parts = []

# ---- Floors ----
# Each FLOORS entry: (name, length, width, z_base, extra_holes)
# extra_holes is a list of (x_plate_local, y_plate_local, diameter) — in
# addition to the 4 corner M3 clearance holes every floor gets.

# Top plate: 5× 8mm LED holes in a row near top edge, plus a 20mm DSI slot
_top_led_spacing = 20.0
_top_led_y       = TOP_FLOOR_W - 15.0
_top_led_x_start = (TOP_FLOOR_L - 4 * _top_led_spacing) / 2.0
_top_extras = [
    (_top_led_x_start + i * _top_led_spacing, _top_led_y, LED_HOLE_DIAMETER)
    for i in range(5)
]
_top_extras.append((TOP_FLOOR_L / 2 - 20, TOP_FLOOR_W / 2 + 10, 20.0))  # DSI ribbon

FLOORS = [
    ("bottom", BOTTOM_FLOOR_L, BOTTOM_FLOOR_W, Z_BOTTOM, []),  # bottom plate sits
                                                               # directly on case
                                                               # floor — no pass-through
    ("middle", MIDDLE_FLOOR_L, MIDDLE_FLOOR_W, Z_MIDDLE, [
        (MIDDLE_FLOOR_L / 2, MIDDLE_FLOOR_W / 2, 15.0),    # center pass-through
    ]),
    ("top",    TOP_FLOOR_L,    TOP_FLOOR_W,    Z_TOP,    _top_extras),
]

for name, length, width, z_base, extra_holes in FLOORS:
    # Plate centred on world origin. plate_origin_{x,y} is the plate's
    # back-left corner in world coords — used to translate plate-local
    # extra-hole positions (LEDs, DSI) into world coords.
    plate_origin_x = -length / 2.0
    plate_origin_y = -width / 2.0

    with BuildPart() as floor:
        with BuildSketch(Plane.XY.offset(z_base)) as _s:
            RectangleRounded(length, width, PLATE_CORNER_R)
        extrude(amount=FLOOR_THICKNESS)

        # M3 rod clearance holes — every plate uses the shared absolute
        # ROD_POSITIONS so holes line up with the rods on every floor.
        for hx, hy in ROD_POSITIONS:
            with Locations(Location((hx, hy, z_base - 0.5))):
                Cylinder(radius=M3_HOLE_DIAMETER / 2.0, height=FLOOR_THICKNESS + 1,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)

        # Extra holes (LEDs, cable/DSI pass-throughs) in plate-local coords
        for (lx, ly, diameter) in extra_holes:
            with Locations(Location((plate_origin_x + lx, plate_origin_y + ly, z_base - 0.5))):
                Cylinder(radius=diameter / 2.0, height=FLOOR_THICKNESS + 1,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)

    floor.part.label = f"Floor_{name}"
    floor.part.color = CLR_HDPE
    parts.append(floor.part)

# ---- Case (Pelican-style, rounded, lid rendered open at a hinge) ----
# External 287×220×152 from the AliExpress listing. Split into a base
# (_CASE_BASE_EXT_H tall) and a lid (remainder). Hinge axis runs along +X
# at the back-top edge (-Y side of the base). Lid is built in its closed
# orientation, then rotated about the hinge so the interior cavity is
# visible when the file opens.
_CASE_EXT_L = 287.0                                          # [SPEC]
_CASE_EXT_W = 220.0                                          # [SPEC]
_CASE_EXT_H = 152.0                                          # [SPEC] total
_CASE_BASE_EXT_H = 122.0                                     # [DESIGN]
_CASE_LID_EXT_H  = _CASE_EXT_H - _CASE_BASE_EXT_H            # = 30
_CASE_CORNER_R   = 10.0
_CASE_INNER_R    = 8.0
_CASE_FLOOR_WALL = 5.0                                       # material below scaffold
_BASE_Z_MIN = -CASE_INTERNAL_H / 2.0 - _CASE_FLOOR_WALL      # -62.5
_BASE_Z_MAX = _BASE_Z_MIN + _CASE_BASE_EXT_H                 # +59.5
_LID_Z_MIN  = _BASE_Z_MAX                                    # +59.5
_LID_Z_MAX  = _LID_Z_MIN + _CASE_LID_EXT_H                   # +89.5
_LID_OPEN_ANGLE = 100.0                                      # degrees past closed

# Bulkhead Z position — raised from 0 to +25 so the 6 SMAs and the USB-C
# inlet land in the upper half of the cavity, reachable from above when the
# top plate is tilted back during the interim screen-tilt service procedure.
_BULK_Z = 25.0                                               # [DESIGN]

# Base: rounded outer shell, stepped scaffold cavity, stabiliser ribs on underside.
# The cavity is 3-stepped: narrower at the bottom, wider toward the rim, so each
# measured plate (240/160, 245/170, 250/180) has a uniform 5mm clearance to the
# cavity wall at its own height. Steps happen at Z_MIDDLE and Z_TOP (the plate
# z-bases), leaving small internal ledges where the cavity widens.
with BuildPart() as case_base:
    with BuildSketch(Plane.XY.offset(_BASE_Z_MIN)) as _s:
        RectangleRounded(_CASE_EXT_L, _CASE_EXT_W, _CASE_CORNER_R)
    extrude(amount=_CASE_BASE_EXT_H)
    # Bottom cavity section: fits BOTTOM plate + 5mm all round.
    with BuildSketch(Plane.XY.offset(Z_CASE_FLOOR)) as _s:
        RectangleRounded(BOTTOM_FLOOR_L + 10, BOTTOM_FLOOR_W + 10, _CASE_INNER_R)
    extrude(amount=Z_MIDDLE - Z_CASE_FLOOR, mode=Mode.SUBTRACT)
    # Middle cavity section: fits MIDDLE plate + 5mm.
    with BuildSketch(Plane.XY.offset(Z_MIDDLE)) as _s:
        RectangleRounded(MIDDLE_FLOOR_L + 10, MIDDLE_FLOOR_W + 10, _CASE_INNER_R)
    extrude(amount=Z_TOP - Z_MIDDLE, mode=Mode.SUBTRACT)
    # Top cavity section: fits TOP plate + 5mm; extends through the rim (+15mm)
    # to cleanly open the top of the base.
    with BuildSketch(Plane.XY.offset(Z_TOP)) as _s:
        RectangleRounded(TOP_FLOOR_L + 10, TOP_FLOOR_W + 10, _CASE_INNER_R)
    extrude(amount=15, mode=Mode.SUBTRACT)
    # Gasket groove on the top rim (a shallow ring channel)
    with BuildSketch(Plane.XY.offset(_BASE_Z_MAX - 2)) as _s:
        RectangleRounded(CASE_INTERNAL_L + 6, CASE_INTERNAL_W + 6, _CASE_INNER_R + 3)
        RectangleRounded(CASE_INTERNAL_L + 2, CASE_INTERNAL_W + 2, _CASE_INNER_R + 1,
                         mode=Mode.SUBTRACT)
    extrude(amount=3, mode=Mode.SUBTRACT)
    # External pass-throughs to match the real Flexfield kit photo:
    # 4 SMA bulkheads (2 per short side) for the antennas, 5 LEDs on the
    # front (-Y) face low band, and a USB-C power inlet on the front face.
    # All cutouts pass all the way through the wall into the interior cavity.
    # --- 4 SMA bulkheads on ±X short sides (symmetric core set) ---
    _SMA_Y_OFFSETS = (-25.0, +25.0)
    _SMA_Z = _BULK_Z
    for _side in (-1, +1):
        for _y_off in _SMA_Y_OFFSETS:
            with Locations(Location((_side * _CASE_EXT_L / 2.0, _y_off, _SMA_Z))):
                Cylinder(radius=BULKHEAD_SMA_HOLE / 2.0, height=40,
                         align=(Align.CENTER, Align.CENTER, Align.CENTER),
                         rotation=(0, 90, 0),
                         mode=Mode.SUBTRACT)
    # --- 2 additional SMA bulkheads for LoRa (XIAO Meshtastic) + WiFi ---
    # Placed asymmetrically: after the 180° case rotation these land at world
    # (-143.5, +60) [LoRa, close to XIAO at world (-95,+60)] and (+143.5, +50)
    # [WiFi, close to WiFi_Adapter at world (+70,+52)]. See ANTENNAS section
    # below for the corresponding antennas + pigtails.
    for _x, _y in ((+_CASE_EXT_L / 2.0, -60.0),   # → world (-143.5, +60) after rotation
                   (-_CASE_EXT_L / 2.0, -50.0)):  # → world (+143.5, +50) after rotation
        with Locations(Location((_x, _y, _SMA_Z))):
            Cylinder(radius=BULKHEAD_SMA_HOLE / 2.0, height=40,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER),
                     rotation=(0, 90, 0),
                     mode=Mode.SUBTRACT)
    # --- 5 LEDs on front face, low band below the handle ---
    # Placed at +Y in source (same side as latches/handle); the whole-case
    # 180° Z rotation at the tail of the script flips them to the front -Y.
    _LED_Z = -35.0
    _LED_SPACING = 22.0
    for _i in range(5):
        _x_led = (_i - 2) * _LED_SPACING
        with Locations(Location((_x_led, +_CASE_EXT_W / 2.0, _LED_Z))):
            Cylinder(radius=LED_HOLE_DIAMETER / 2.0, height=60,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER),
                     rotation=(90, 0, 0),
                     mode=Mode.SUBTRACT)
    # --- USB-C power input on front face, at bulkhead height ---
    # Aligned at Z=_BULK_Z (same as SMA bulkheads) so the panel-mount IP67
    # USB-C feedthrough is reachable from above with the top plate tilted
    # back during the interim screen-tilt service procedure.
    with Locations(Location((-100.0, +_CASE_EXT_W / 2.0, _BULK_Z))):
        Box(12.5, 60, 7,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT)
    # Stabiliser ribs under the case (5 bars along Y, spaced along X)
    for _i in range(5):
        _rx = -110 + _i * 55
        with Locations(Location((_rx, 0, _BASE_Z_MIN - 3))):
            Box(6, _CASE_EXT_W * 0.82, 3,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
case_base.part.label = "Case_Base"
case_base.part.color = CLR_CASE
parts.append(case_base.part)

# Lid: built closed, then rotated about the back-top hinge
with BuildPart() as case_lid:
    with BuildSketch(Plane.XY.offset(_LID_Z_MIN)) as _s:
        RectangleRounded(_CASE_EXT_L, _CASE_EXT_W, _CASE_CORNER_R)
    extrude(amount=_CASE_LID_EXT_H)
    # Cavity opens downward; leaves 4mm of lid material above
    with BuildSketch(Plane.XY.offset(_LID_Z_MIN - 1)) as _s:
        RectangleRounded(CASE_INTERNAL_L, CASE_INTERNAL_W, _CASE_INNER_R)
    extrude(amount=_CASE_LID_EXT_H - 4, mode=Mode.SUBTRACT)
    # Lid-edge lip that seats into the base gasket groove (small downward skirt)
    with BuildSketch(Plane.XY.offset(_LID_Z_MIN - 1)) as _s:
        RectangleRounded(CASE_INTERNAL_L + 4, CASE_INTERNAL_W + 4, _CASE_INNER_R + 2)
        RectangleRounded(CASE_INTERNAL_L + 1, CASE_INTERNAL_W + 1, _CASE_INNER_R,
                         mode=Mode.SUBTRACT)
    extrude(amount=2)  # 2mm skirt hanging below lid base
_HINGE = Axis((0, -_CASE_EXT_W / 2.0, _BASE_Z_MAX), (1, 0, 0))
_lid_open = case_lid.part.rotate(_HINGE, _LID_OPEN_ANGLE)
_lid_open.label = "Case_Lid"
_lid_open.color = CLR_CASE
parts.append(_lid_open)

# Two front latches on the +Y face of the base (opposite the hinge)
for _i, _lx in enumerate([-80, 80]):
    with BuildPart() as _latch:
        # Mount bracket (embedded into the case +Y wall)
        with Locations(Location((_lx, _CASE_EXT_W / 2.0 - 2, _BASE_Z_MAX - 40))):
            Box(46, 10, 16, align=(Align.CENTER, Align.MIN, Align.MIN))
        # Arm sticking out
        with Locations(Location((_lx, _CASE_EXT_W / 2.0 + 3, _BASE_Z_MAX - 32))):
            Box(36, 6, 36, align=(Align.CENTER, Align.MIN, Align.MIN))
        # Hook catching the lid lip
        with Locations(Location((_lx, _CASE_EXT_W / 2.0 + 1, _BASE_Z_MAX))):
            Box(36, 10, 6, align=(Align.CENTER, Align.MIN, Align.MIN))
    _latch.part.label = f"Latch_{_i+1}"
    _latch.part.color = CLR_LATCH
    parts.append(_latch.part)

# Carry handle on the +Y face of the base (between the latches)
with BuildPart() as _handle:
    _HG_L, _HG_POST_H, _HG_POST_W = 140.0, 26.0, 12.0
    _HG_GRIP_D, _HG_GRIP_H = 18.0, 12.0
    _HG_Y = _CASE_EXT_W / 2.0
    for _sign in (-1, +1):
        with Locations(Location((_sign * _HG_L / 2.0, _HG_Y, _BASE_Z_MAX - _HG_POST_H))):
            Box(_HG_POST_W, _HG_GRIP_D, _HG_POST_H,
                align=(Align.CENTER, Align.MIN, Align.MIN))
    # Grip bar spanning the posts
    with Locations(Location((0, _HG_Y + _HG_GRIP_D - 8, _BASE_Z_MAX - _HG_POST_H))):
        Box(_HG_L, 9, _HG_GRIP_H,
            align=(Align.CENTER, Align.MIN, Align.MIN))
_handle.part.label = "Handle"
_handle.part.color = CLR_HANDLE
parts.append(_handle.part)

# Pressure-relief valve on the -X side wall, near the top of the base
with BuildPart() as _valve_body:
    Cylinder(radius=10, height=8,
             align=(Align.CENTER, Align.CENTER, Align.MIN))
_valve_final = _valve_body.part.rotate(Axis.Y, -90).translate(
    Vector(-_CASE_EXT_L / 2.0, 0, _BASE_Z_MAX - 35))
_valve_final.label = "Pressure_Valve"
_valve_final.color = CLR_VALVE
parts.append(_valve_final)


# ---- Helper for component placement ----
def _component(name, L, W, H, x, y, z, color):
    with BuildPart() as c:
        with Locations(Location((x, y, z))):
            Box(L, W, H, align=(Align.MIN, Align.MIN, Align.MIN))
    c.part.label = name
    c.part.color = color
    parts.append(c.part)
    _add_device_labels(name, L, W, H, x, y, z)


# In the case-centred frame, each plate's back-left corner is at (-L/2, -W/2)
# and its centre is at (0, 0). bp_/mp_/tp_ are plate-back-left in world coords.
# Component positions below were originally written against the back-left-
# bottom frame as `bp_x + offset` etc.; they keep that structure unchanged
# (offsets from the plate's back-left corner) so the math is readable, with
# bp_x etc. just computed from the centred origin instead.

# ---- Bottom floor components ----
# X1202 UPS was moved to the top plate (stacked under the Pi 5 via GPIO).
Z_ON_BOTTOM = Z_BOTTOM + FLOOR_THICKNESS
bp_x = -BOTTOM_FLOOR_L / 2.0
bp_y = -BOTTOM_FLOOR_W / 2.0

_component("UV-K5_AIOC", UVK5_L,  UVK5_W,  UVK5_H,
           bp_x + BOTTOM_FLOOR_L - UVK5_L - 15, -UVK5_W / 2.0,   Z_ON_BOTTOM, CLR_UVK5)
# USB Hub rotated 90° about Z: long axis (HUB_L=86) now runs north-south.
# Real Sabrent HB-UM43 has its 4 USB-A receptacles on a long edge; this
# orientation puts the ports on +X face where they can fan out to the rest
# of the bottom plate without crossing the hub body. Captive upstream USB-A
# cable exits the north end of +X face. Hub spans X=-110..-74, Y=-70..+16.
_component("USB_Hub",    HUB_W,   HUB_L,   HUB_H,
           bp_x + 10,                           bp_y + 10,       Z_ON_BOTTOM, CLR_HUB)
_component("GPS",        GPS_L,   GPS_W,   GPS_H,
           bp_x + BOTTOM_FLOOR_L - GPS_L - 30,  bp_y + 15,       Z_ON_BOTTOM, CLR_GPS)
# USB WiFi adapter — sits on the bottom plate above the UV-K5, between it
# and the plate's +Y edge.
_component("WiFi_Adapter", WIFI_L, WIFI_W, WIFI_H,
           bp_x + BOTTOM_FLOOR_L - WIFI_L - 15, +UVK5_W / 2.0 + 7.0,
           Z_ON_BOTTOM, CLR_WIFI)

# ---- Middle floor components ----
Z_ON_MIDDLE = Z_MIDDLE + FLOOR_THICKNESS
mp_x = -MIDDLE_FLOOR_L / 2.0
mp_y = -MIDDLE_FLOOR_W / 2.0

_component("LilyGO_TCall",   TCALL_L,     TCALL_W,     TCALL_H,
           +32.5,                                    mp_y + 100,                            Z_ON_MIDDLE, CLR_TCALL)
_component("RTL_SDR_V4",     RTLSDR_L,    RTLSDR_W,    RTLSDR_H,
           mp_x + MIDDLE_FLOOR_L / 2.0 + 20,         -RTLSDR_W / 2.0,                       Z_ON_MIDDLE, CLR_RTLSDR)
_component("XIAO_Meshtastic", XIAO_L,     XIAO_W,      XIAO_H,
           mp_x + 15,                                mp_y + MIDDLE_FLOOR_W - XIAO_W - 15,   Z_ON_MIDDLE, CLR_XIAO)
# Sonoff ZBDongle-E — ZigBee coordinator USB stick, mounted flat on middle plate.
_component("Sonoff_ZBDongle", SONOFF_L,    SONOFF_W,    SONOFF_H,
           -40.0,                                    -55.0,                                 Z_ON_MIDDLE, CLR_SONOFF)
_component("DCF77",          DCF77_L,     DCF77_W,     DCF77_H,
           -DCF77_L / 2.0,                           mp_y + MIDDLE_FLOOR_W - DCF77_W - 15,  Z_ON_MIDDLE, CLR_DCF77)
_component("RockBLOCK_9603", ROCKBLOCK_L, ROCKBLOCK_W, ROCKBLOCK_H,
           mp_x + MIDDLE_FLOOR_L - ROCKBLOCK_L - 15, mp_y + 15,                             Z_ON_MIDDLE, CLR_ROCKBLOCK)

# ---- Middle-floor stack: X1202 UPS + Pi 5 (pogo-stacked, resting on plate) ----
# Stack rotated 90° about Z (long axis of each PCB now runs in Y) so the
# Pi 5's short side faces the display — moves the Pi 5 footprint out of the
# display's rear-hump XY zone. Stack rests directly on the middle plate
# (X1202 bottom = middle-plate top), so Pi 5 top sits as low as possible
# to leave headroom below the display rear.
Z_ON_TOP    = Z_TOP + FLOOR_THICKNESS
Z_ON_MIDDLE = Z_MIDDLE + FLOOR_THICKNESS
_STACK_X_CENTRE = -78.5    # pushed west so Pi 5 east edge is flush with the display hump's west face (X=-50)
_STACK_Y_CENTRE = 0.0
_Z_X1202_BOT = Z_ON_MIDDLE                       # X1202 sits on the middle plate
_Z_PI5_BOT   = _Z_X1202_BOT + X1202_H            # Pi 5 pogo-stacked on top of X1202

# Rotated footprints: what was _L is now extent in Y; what was _W is extent in X.
_component("X1202_UPS",  X1202_W,   X1202_L,   X1202_H,
           _STACK_X_CENTRE - X1202_W / 2.0,         _STACK_Y_CENTRE - X1202_L / 2.0,
           _Z_X1202_BOT, CLR_X1202)
_component("Pi5_under",  PI5_W,     PI5_L,     PI5_H,
           _STACK_X_CENTRE - PI5_W / 2.0,           _STACK_Y_CENTRE - PI5_L / 2.0,
           _Z_PI5_BOT, CLR_PI5)
# Display = stepped solid (outer flange + central rear hump), not a flat slab.
# See DISPLAY_FLANGE_THICKNESS / DISPLAY_HUMP_* in field_kit_config.py.
# Z layout (display is front-up):
#   flange top    = Z_ON_TOP + DISPLAY_PROTRUSION                 (above top plate)
#   flange bottom = flange_top - DISPLAY_FLANGE_THICKNESS         (hump starts here)
#   hump bottom   = flange_top - DISPLAY_THICKNESS                (deepest point)
_DISP_X = -DISPLAY_L / 2.0
_DISP_Y = -DISPLAY_W / 2.0 - 10
_DISP_FLANGE_TOP = Z_ON_TOP + DISPLAY_PROTRUSION
_DISP_FLANGE_BOT = _DISP_FLANGE_TOP - DISPLAY_FLANGE_THICKNESS
_DISP_HUMP_BOT   = _DISP_FLANGE_TOP - DISPLAY_THICKNESS
# Hump is centred within the display footprint (centred in L, centred in W).
_DISP_HUMP_X = _DISP_X + (DISPLAY_L - DISPLAY_HUMP_L) / 2.0
_DISP_HUMP_Y = _DISP_Y + (DISPLAY_W - DISPLAY_HUMP_W) / 2.0
with BuildPart() as _display:
    with Locations(Location((_DISP_X, _DISP_Y, _DISP_FLANGE_BOT))):
        Box(DISPLAY_L, DISPLAY_W, DISPLAY_FLANGE_THICKNESS,
            align=(Align.MIN, Align.MIN, Align.MIN))
    with Locations(Location((_DISP_HUMP_X, _DISP_HUMP_Y, _DISP_HUMP_BOT))):
        Box(DISPLAY_HUMP_L, DISPLAY_HUMP_W, DISPLAY_HUMP_THICKNESS,
            align=(Align.MIN, Align.MIN, Align.MIN))
_display.part.label = "Pi_Touch_Display_2"
_display.part.color = CLR_DISPLAY
parts.append(_display.part)
# Labels are sized against the outer envelope — flange L×W is the full display footprint.
_add_device_labels("Pi_Touch_Display_2", DISPLAY_L, DISPLAY_W, DISPLAY_THICKNESS,
                   _DISP_X, _DISP_Y, _DISP_HUMP_BOT)

# ---- M3 rods — same absolute positions every plate was drilled to ----
# Rod sits on the case interior floor (below the bottom plate, which is
# lifted by NUT_H to make room for the below-plate nut). Its top ends
# flush with the nut above the top plate — no rod sticking past the stack.
for i, (rx, ry) in enumerate(ROD_POSITIONS):
    with BuildPart() as rod:
        with Locations(Location((rx, ry, Z_CASE_FLOOR))):
            Cylinder(radius=ROD_DIAMETER / 2.0, height=ROD_LENGTH,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    rod.part.label = f"M3_Rod_{i+1}"
    rod.part.color = CLR_ROD
    parts.append(rod.part)

# ---- M3 nuts — 2 per plate per rod (one on each face), clamping the plate ----
# 6 nuts per rod × 4 rods = 24 nuts. Each nut bottoms at (plate face) and
# extends NUT_H into the adjacent gap (or outside the stack for the
# outer-most two, which is what the 4.8mm "missing" rod length carries).
_NUT_STACK = [
    (Z_CASE_FLOOR,                       "P1B"),  # below bottom plate
    (Z_BOTTOM + FLOOR_THICKNESS,         "P1A"),  # above bottom plate
    (Z_MIDDLE - NUT_H,                   "P2B"),  # below middle plate
    (Z_MIDDLE + FLOOR_THICKNESS,         "P2A"),  # above middle plate
    (Z_TOP    - NUT_H,                   "P3B"),  # below top plate
    (Z_TOP    + FLOOR_THICKNESS,         "P3A"),  # above top plate
]
for i, (rx, ry) in enumerate(ROD_POSITIONS):
    for z_base, pos_code in _NUT_STACK:
        with BuildPart() as nut:
            with Locations(Location((rx, ry, z_base))):
                Cylinder(radius=NUT_OD / 2.0, height=NUT_H,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
        nut.part.label = f"M3_Nut_R{i+1}_{pos_code}"
        nut.part.color = CLR_NUT
        parts.append(nut.part)

# ============================================================================
# ANTENNAS + CABLES
# ============================================================================
# Antennas & cables are drawn in the source/world frame and are NOT rotated
# with the case. The 4 SMA bulkheads are at (±_CASE_EXT_L/2, ±25, 0); under
# the 180° whole-case Z rotation this set maps to itself (symmetric), so a
# whip drawn in source frame still lands on a real bulkhead after rotation.
# Scaffold radios aren't rotated either, so internal pigtails connect fixed
# points in the world frame without having to track the case rotation.

import math

# ============================================================================
# Cable + plug rendering — sweep-based with arc-rounded corners
# ============================================================================
# Every cable in the kit is rendered as:
#   - Two plug overmold bodies (one at each cable endpoint), modelled as
#     real-volume primitives that occupy the space the cable physically can
#     not pass through. Box for USB-A/C/GPIO, cylinder for SMA.
#   - A swept circle along a build123d Wire whose interior corners are
#     tangent-arc filleted to the cable's minimum bend radius. Straight legs
#     between corners are validated to be ≥ bend radius — short legs raise
#     a build error rather than producing geometry the cable physically
#     can't take.
#
# This replaces the prior "cylinder polyline + sphere bulb" approach which
# placed point-corners at zero bend radius and zero connector volume.
# Empirically the previous renders looked plausible but the kit could not be
# wired to match.

# Plug spec: (kind, dims, color)  where kind ∈ {"BOX", "CYL"}
PLUG_SPECS = {
    "USB_A": ("BOX", (USB_A_PLUG_W, USB_A_PLUG_H, USB_A_PLUG_L), Color(0.10, 0.10, 0.10)),
    "USB_C": ("BOX", (USB_C_PLUG_W, USB_C_PLUG_H, USB_C_PLUG_L), Color(0.10, 0.10, 0.10)),
    "SMA":   ("CYL", (SMA_PLUG_OD,  SMA_PLUG_L),                  CLR_SMA),
    "GPIO":  ("BOX", (GPIO_HDR_W,   GPIO_HDR_H,   GPIO_HDR_L),    Color(0.05, 0.05, 0.05)),
    "DSI":   ("BOX", (DSI_FFC_W,    DSI_FFC_H,    DSI_FFC_L),     CLR_DSI),
}


def _plug_length(plug_type):
    kind, dims, _color = PLUG_SPECS[plug_type]
    return dims[-1]   # last dim is always the long axis


def _add_plug_body(face, exit_dir, plug_type, label):
    """Place a connector overmold at `face`, oriented along `exit_dir`.

    The plug's long axis aligns with exit_dir; its base sits flush with the
    device port face. So a USB-A plug pointing in +X starts at (X=face_x,
    Y=face_y, Z=face_z) and extends to X = face_x + USB_A_PLUG_L.
    """
    kind, dims, color = PLUG_SPECS[plug_type]
    exit_v = Vector(*exit_dir)
    if exit_v.length < 1e-9:
        return
    exit_n = exit_v.normalized()
    # Plane whose +Z = exit direction; profile lies in this plane at `face`,
    # plug extrudes along +Z (i.e. away from the device).
    plug_plane = Plane(origin=Vector(*face), z_dir=(exit_n.X, exit_n.Y, exit_n.Z))
    with BuildPart() as plug:
        with Locations(plug_plane.location):
            if kind == "BOX":
                Box(*dims, align=(Align.CENTER, Align.CENTER, Align.MIN))
            else:  # CYL
                od, length = dims
                Cylinder(radius=od / 2.0, height=length,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    plug.part.label = label
    plug.part.color = color
    parts.append(plug.part)


def _make_smooth_path_wire(points, bend_radius, label):
    """Build a build123d Wire from a polyline by inserting tangent arcs at
    every interior corner. Tangent points sit `bend_radius` along each leg
    from the corner; arc edges are constructed with `Edge.make_tangent_arc`
    so they match the leg directions exactly at the seam.

    Validates that every straight leg between two adjacent bend tangent
    points is ≥ bend_radius. Short legs raise ValueError with a clear
    locator (cable label + corner index), so route bugs surface in the
    build, not as garbled OCC errors deep in the sweep call.
    """
    if len(points) < 2:
        raise ValueError(f"{label}: need at least 2 polyline points, got {len(points)}")

    pts = [Vector(*p) for p in points]
    n = len(pts)

    # Pass 1: compute tangent points at each interior corner.
    interior = [None] * n
    for i in range(1, n - 1):
        d_in_full = pts[i] - pts[i - 1]
        d_out_full = pts[i + 1] - pts[i]
        len_in, len_out = d_in_full.length, d_out_full.length
        if len_in < 1e-6 or len_out < 1e-6:
            continue
        d_in = d_in_full / len_in
        d_out = d_out_full / len_out
        cosine = d_in.dot(d_out)
        if cosine > 0.99999:
            # Collinear, no bend. Treat as a single straight leg.
            continue
        if cosine < -0.99999:
            raise ValueError(
                f"{label}: 180° turn at waypoint {i} — cable can't fold back on itself")
        t_in = pts[i] - d_in * bend_radius
        t_out = pts[i] + d_out * bend_radius
        interior[i] = (t_in, t_out, d_in, d_out, len_in, len_out)

    # Pass 2: validate leg lengths.
    # Leg i is the straight section from (last tangent_out OR pts[0]) to
    # (next tangent_in OR pts[-1]). Each interior corner consumes
    # bend_radius from each side; the actual straight section between two
    # consecutive corners is leg_len - 2 * bend_radius.
    for i in range(1, n - 1):
        if interior[i] is None:
            continue
        _, _, _, _, len_in, len_out = interior[i]
        # Subtract bend allowance contributed by corner at i-1 (if any) and
        # corner at i+1 (if any).
        prev_consumes = bend_radius if (i >= 2 and interior[i - 1] is not None) else 0.0
        next_consumes = bend_radius if (i <= n - 3 and interior[i + 1] is not None) else 0.0
        # Leg coming into corner i: length len_in, with prev_consumes used
        # at its far end (for corner i-1) and bend_radius used at its near
        # end (for corner i).
        free_in = len_in - prev_consumes - bend_radius
        if free_in < -0.001:
            raise ValueError(
                f"{label}: leg into waypoint {i} is {len_in:.1f} mm — needs "
                f">= {prev_consumes + bend_radius:.1f} mm for bend radii "
                f"({bend_radius:.1f} mm each side)")
        # The outgoing leg (from corner i to i+1) is checked when we hit
        # i+1, so don't double-check here.
    # Final leg (from last interior corner to last point), and first leg
    # (from first point to first interior corner) — checked above as in/out
    # of the relevant corner.

    # Pass 3: build the edges.
    edges = []
    cursor = pts[0]
    for i in range(1, n - 1):
        if interior[i] is None:
            continue
        t_in, t_out, d_in, d_out, _, _ = interior[i]
        # Straight from current cursor to t_in
        if (t_in - cursor).length > 1e-6:
            edges.append(Edge.make_line(cursor, t_in))
        # Tangent arc from t_in (with tangent direction = d_in) to t_out
        edges.append(Edge.make_tangent_arc(t_in, d_in, t_out))
        cursor = t_out
    # Final straight to last point
    if (pts[-1] - cursor).length > 1e-6:
        edges.append(Edge.make_line(cursor, pts[-1]))

    if not edges:
        raise ValueError(f"{label}: degenerate polyline produced no edges")

    return Wire(edges)


_BEND_RADIUS_VIOLATIONS = []


def _add_cable(face_a, dir_a, plug_a, face_b, dir_b, plug_b,
               via, cable_radius, bend_radius, label, color):
    """Render a cable with plug bodies at both ends and a swept circle along
    a polyline with arc-rounded corners.

    face_a/b:  (x, y, z) — device port face on each end
    dir_a/b:   (dx, dy, dz) — outward exit direction (unit-ish, normalised here)
    plug_a/b:  plug type key into PLUG_SPECS ("USB_A", "USB_C", "SMA", "GPIO", "DSI")
    via:       list of (x, y, z) waypoints between the two plug backs
    """
    # 1) plug bodies
    _add_plug_body(face_a, dir_a, plug_a, f"Plug_{label}_a")
    _add_plug_body(face_b, dir_b, plug_b, f"Plug_{label}_b")

    # 2) cable polyline = back-of-plug-A → via... → back-of-plug-B
    dir_a_n = Vector(*dir_a).normalized()
    dir_b_n = Vector(*dir_b).normalized()
    end_a = Vector(*face_a) + dir_a_n * _plug_length(plug_a)
    end_b = Vector(*face_b) + dir_b_n * _plug_length(plug_b)
    polyline = [(end_a.X, end_a.Y, end_a.Z)]
    polyline.extend(via)
    polyline.append((end_b.X, end_b.Y, end_b.Z))

    # 3) wire with arc-filleted corners, validating bend radius. In bulk-fix
    # mode (DRY_RUN_CABLES=True) we collect all violations instead of
    # stopping at the first; final build then re-runs without the env var.
    try:
        wire = _make_smooth_path_wire(polyline, bend_radius, label)
    except ValueError as _e:
        if os.environ.get("DRY_RUN_CABLES"):
            _BEND_RADIUS_VIOLATIONS.append(str(_e))
            return
        raise

    # 4) sweep a circle profile along the wire
    start_tangent = wire.tangent_at(0.0)
    profile_plane = Plane(origin=Vector(*polyline[0]), z_dir=start_tangent)
    with BuildPart() as cable:
        with BuildSketch(profile_plane):
            Circle(cable_radius)
        sweep(path=wire, transition=Transition.TRANSFORMED, is_frenet=False)
    cable.part.label = label
    cable.part.color = color
    parts.append(cable.part)

    # 5) cable length sanity log (helpful when iterating routes)
    total = 0.0
    for i in range(len(polyline) - 1):
        a = Vector(*polyline[i]); b = Vector(*polyline[i + 1])
        total += (b - a).length
    # Bend radii subtract a tiny amount from straight-line approximation
    # but the polyline length is the dominant term. Print at end of build.
    _CABLE_LENGTHS.append((label, total))


_CABLE_LENGTHS = []


def _add_zip_tie(position, cable_axis, cable_radius, label):
    """Short black ring around a cable at the given position; cable_axis is
    the cable's direction vector through that point. Kept for explicit
    strain-relief markers; the new _add_cable doesn't auto-place ties."""
    _mag = math.sqrt(sum(_a * _a for _a in cable_axis))
    if _mag < 1e-6:
        return
    _axis_n = tuple(_a / _mag for _a in cable_axis)
    with BuildPart() as _zt:
        with Locations(Plane(origin=position, z_dir=_axis_n)):
            Cylinder(radius=cable_radius * 1.8, height=2.5,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER))
    _zt.part.label = label
    _zt.part.color = CLR_ANTENNA  # black nylon
    parts.append(_zt.part)


# ---- Bulkhead body geometry (case-anchored connector hardware) ----
# Each SMA bulkhead is a brass jack-jack: a threaded barrel through the case
# wall with a female SMA receptacle on each face. The external whip's male
# SMA threads onto the outside; the internal pigtail's male SMA threads onto
# the inside. These bodies stay with the case when the scaffold lifts out.
_BULK_BODY_R       = 4.0
_BULK_BODY_LEN     = 16.0
_WALL_MID_X        = (_CASE_EXT_L + CASE_INTERNAL_L) / 4.0     # 136.75
_BULK_INNER_FACE_X = _WALL_MID_X - _BULK_BODY_LEN / 2.0        # 128.75

# Bulkhead positions in WORLD frame — match each Ant_<role>'s world position
# so each bulkhead body, antenna, and pigtail are co-located.
_BULKHEAD_POSITIONS = [
    (+1, +25.0, "UHF"),      # UV-K5 handheld
    (+1, -25.0, "SDR"),      # RTL-SDR
    (-1, +25.0, "LTE"),      # LilyGO T-Call
    (-1, -25.0, "Iridium"),  # RockBLOCK
    (-1, +60.0, "LoRa"),     # XIAO Meshtastic (asymmetric)
    (+1, +50.0, "WiFi"),     # WiFi adapter (asymmetric)
]
for _side, _y, _blabel in _BULKHEAD_POSITIONS:
    _bulk_x = _side * _WALL_MID_X
    with BuildPart() as _bulk:
        with Locations(Location((_bulk_x, _y, _BULK_Z))):
            Cylinder(radius=_BULK_BODY_R, height=_BULK_BODY_LEN,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER),
                     rotation=(0, 90, 0))
    _bulk.part.label = f"Bulkhead_SMA_{_blabel}"
    _bulk.part.color = CLR_SMA
    parts.append(_bulk.part)

# ---- External antennas: SMA stub → 90° joint → vertical whip ----
_ANT_SMA_R    = 3.2    # SMA connector + outer nut
_ANT_SMA_OUT  = 10.0   # SMA body protrusion beyond case wall
_ANT_WHIP_R   = 4.0    # rubber whip
_ANT_JOINT_H  = 8.0    # joint bulb height

_ANTENNAS = [
    # (source_side_x, y_off, whip_length, role_label)
    # Source positions are chosen so the antenna's SOURCE position matches its
    # BULKHEAD's WORLD position after the 180° case rotation — for the
    # symmetric core 4 bulkheads this is automatic, for the 2 asymmetric LoRa/
    # WiFi bulkheads the source pos of the antenna is chosen to land where
    # the bulkhead lands (see Case_Base cutouts).
    (+1, +25.0, 210.0, "Ant_UHF"),       # UV-K5 handheld band
    (+1, -25.0, 180.0, "Ant_SDR"),       # RTL-SDR scanner
    (-1, +25.0, 170.0, "Ant_LTE"),       # cellular
    (-1, -25.0, 100.0, "Ant_Iridium"),   # short sat stub
    (-1, +60.0, 180.0, "Ant_LoRa"),      # XIAO Meshtastic (868/915 MHz)
    (+1, +50.0,  90.0, "Ant_WiFi"),      # WiFi adapter (2.4/5 GHz dual-band)
]

for _side, _y, _whip_len, _alabel in _ANTENNAS:
    _wall_x    = _side * _CASE_EXT_L / 2.0
    _sma_mid_x = _wall_x + _side * _ANT_SMA_OUT / 2.0
    _joint_x   = _wall_x + _side * _ANT_SMA_OUT
    # Horizontal SMA body (brass)
    with BuildPart() as _sma:
        with Locations(Location((_sma_mid_x, _y, _BULK_Z))):
            Cylinder(radius=_ANT_SMA_R, height=_ANT_SMA_OUT,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER),
                     rotation=(0, 90, 0))
    _sma.part.label = f"SMA_{_alabel}"
    _sma.part.color = CLR_SMA
    parts.append(_sma.part)
    # 90° bend joint — small vertical cylinder the whip rises from
    with BuildPart() as _joint:
        with Locations(Location((_joint_x, _y, _BULK_Z))):
            Cylinder(radius=_ANT_SMA_R + 1.3, height=_ANT_JOINT_H,
                     align=(Align.CENTER, Align.CENTER, Align.CENTER))
    _joint.part.label = f"SMA_Joint_{_alabel}"
    _joint.part.color = CLR_SMA
    parts.append(_joint.part)
    # Vertical whip rising from top of joint
    with BuildPart() as _whip:
        with Locations(Location((_joint_x, _y, _BULK_Z + _ANT_JOINT_H / 2.0))):
            Cylinder(radius=_ANT_WHIP_R, height=_whip_len,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    _whip.part.label = _alabel
    _whip.part.color = CLR_ANTENNA
    parts.append(_whip.part)

# RF pigtails are now defined alongside all other cables in the unified
# port-aware cable block below the USB-C bulkhead body section. Each pigtail
# is a swept circle along a tangent-arc-filleted wire with SMA plug bodies
# at both ends (bulkhead inner face and radio jack). Bend radii honored.

# ============================================================================
# USB-C panel feedthrough — case-anchored body + internal cable to X1202
# ============================================================================
# Hardware spec: 30 cm USB-C IP67 panel-mount feedthrough — Female (outside)
# to Male (inside, captive cable). Type-C 3.1, USB 2.0 data (480 Mbps), 24/28
# AWG bare copper, PVC sheath + black PU outer cover. The panel-mount body
# stays anchored in the case wall; the captive cable's male plug is what the
# X1202 USB-C-IN port mates with.
#
# Bulkhead lives at Z = _BULK_Z (= +25, same as the SMA bulkheads) so it is
# reachable from above when the top plate is tilted back during the interim
# screen-tilt service procedure. At this Z the front wall sits in the middle
# cavity step (inner Y face at -90, not the top-band -95).
CLR_USBC_BODY  = Color(0.10, 0.10, 0.10)   # black plastic (panel-mount body)
CLR_USBC_CABLE = Color(0.05, 0.05, 0.05)   # black PU outer cover (per spec)

_USBC_BULK_X       = +100.0
_USBC_BULK_Y_OUTER = -_CASE_EXT_W / 2.0              # -110 (front wall outer)
_USBC_BULK_Y_INNER = -(MIDDLE_FLOOR_W + 10) / 2.0    # -90  (middle-band inner wall)
_USBC_BULK_Y_MID   = (_USBC_BULK_Y_OUTER + _USBC_BULK_Y_INNER) / 2.0   # -100.0
_USBC_BULK_Z       = _BULK_Z
_USBC_BULK_LEN     = 25.0    # spans wall thickness + flange protrusion both sides
_USBC_INNER_FACE_Y = _USBC_BULK_Y_MID + _USBC_BULK_LEN / 2.0   # -87.5

with BuildPart() as _usbc_bulk:
    with Locations(Location((_USBC_BULK_X, _USBC_BULK_Y_MID, _USBC_BULK_Z))):
        Box(12.0, _USBC_BULK_LEN, 7.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER))
_usbc_bulk.part.label = "Bulkhead_USBC"
_usbc_bulk.part.color = CLR_USBC_BODY
parts.append(_usbc_bulk.part)

# ============================================================================
# CABLES — port-aware, plug bodies + sweep-arc rendering
# ============================================================================
# Every cable is defined as a swept circle along a tangent-arc-filleted wire,
# with overmold plug bodies at each end. Routes start at real port positions
# (not generic device-center exits) and respect spec'd minimum bend radii at
# every corner. The validator inside _make_smooth_path_wire raises if any leg
# is too short for the bend allowance.

# Port spec: (face_xyz, exit_dir_xyz, plug_type)
# For each device, port_id → spec. Bulkheads use a single "INNER" port at
# the cavity-side face of the bulkhead body.
_X1202_USBC_R = 1.75   # captive USB-C internal cable radius (~3.5mm OD)
_USB_R   = 2.0         # generic USB-A / USB-C cable radius
_PIGTAIL_R = 1.25      # RG-316 pigtail radius (~2.5mm OD)
_GPIO_R   = 2.2        # jumper bundle
_POWER_R  = 2.0        # USB-A power cable
_DSI_R    = 1.5        # FFC ribbon (modeled as cylinder; visualisation only)

_PORTS = {
    # ---- Bottom-plate devices ----
    "UV-K5_AIOC": {
        # USB-C charge mod on +Y long edge mid-X, mid-Z. Cable approaches from +Y.
        "USB_C_charge": ((+45.0, +UVK5_W / 2.0, Z_ON_BOTTOM + UVK5_H / 2.0),
                         (0, +1, 0), "USB_C"),
        # AIOC USB-C exits +Z (top of AIOC, which sits on top of UV-K5 head).
        # AIOC perched at the head end of UV-K5 (X near 0). Z = top of UV-K5
        # + half AIOC height = -12.1 + 6 = -6.1.
        "AIOC_USB_C":   ((-15.0 + 15.0, 0.0, Z_ON_BOTTOM + UVK5_H + AIOC_H / 2.0),
                         (0, 0, +1), "USB_C"),
        # Antenna SMA: real UV-K5 has SMA on the head short edge; for routing
        # cleanliness in this model the SMA exits +Z from the radio top center.
        "Antenna_SMA":  ((+45.0, 0.0, Z_ON_BOTTOM + UVK5_H),
                         (0, 0, +1), "SMA"),
    },
    "USB_Hub": {
        # Hub rotated 90°: 36×86×15 at (bp_x+10, bp_y+10) = (-110, -70).
        # 4 USB-A receptacles on +X face spread along Y; captive upstream
        # cable exits +X face at the north end; X1202 power input on the
        # -Y short face (the south end).
        "P1": ((bp_x + 10 + HUB_W,  bp_y + 10 + 15.0,  Z_ON_BOTTOM + HUB_H / 2.0),
               (+1, 0, 0), "USB_A"),
        "P2": ((bp_x + 10 + HUB_W,  bp_y + 10 + 33.0,  Z_ON_BOTTOM + HUB_H / 2.0),
               (+1, 0, 0), "USB_A"),
        "P3": ((bp_x + 10 + HUB_W,  bp_y + 10 + 51.0,  Z_ON_BOTTOM + HUB_H / 2.0),
               (+1, 0, 0), "USB_A"),
        "P4": ((bp_x + 10 + HUB_W,  bp_y + 10 + 69.0,  Z_ON_BOTTOM + HUB_H / 2.0),
               (+1, 0, 0), "USB_A"),
        # POWER_IN modeled as a 5th USB-A on +X face at the south end. (Real
        # HB-UM43 is bus-powered via upstream cable; we model a separate
        # power input here to reflect the kit's X1202 power injection plan.)
        "POWER_IN": ((bp_x + 10 + HUB_W, bp_y + 10, Z_ON_BOTTOM + HUB_H / 2.0),
                     (+1, 0, 0), "USB_A"),
        # Captive upstream cable: exits +Y short face at the north end.
        "UPSTREAM": ((bp_x + 10 + HUB_W / 2.0, bp_y + 10 + HUB_L,  Z_ON_BOTTOM + HUB_H / 2.0),
                     (0, +1, 0), "USB_A"),
    },
    "GPS": {
        "USB_A": ((bp_x + BOTTOM_FLOOR_L - GPS_L - 30, bp_y + 15 + GPS_W / 2.0,
                   Z_ON_BOTTOM + GPS_H / 2.0),
                  (-1, 0, 0), "USB_A"),
    },
    "WiFi_Adapter": {
        # T3U Plus has USB-A and RP-SMA on opposite short ends. The +X end of
        # the adapter is at X=+105 — only 20 mm from cavity wall at +125, not
        # enough for a 30 mm USB-A plug body. So USB-A on -X end (X=+7.4)
        # facing west; antenna SMA on +X end (only 14 mm plug, fits).
        "USB_A": ((bp_x + BOTTOM_FLOOR_L - WIFI_L - 15,
                   +UVK5_W / 2.0 + 7.0 + WIFI_W / 2.0,
                   Z_ON_BOTTOM + WIFI_H / 2.0),
                  (-1, 0, 0), "USB_A"),
        "Antenna_SMA": ((bp_x + BOTTOM_FLOOR_L - 15,
                         +UVK5_W / 2.0 + 7.0 + WIFI_W / 2.0,
                         Z_ON_BOTTOM + WIFI_H / 2.0),
                        (+1, 0, 0), "SMA"),
    },
    # ---- Middle-plate devices ----
    "LilyGO_TCall": {
        "USB_C": ((+32.5, mp_y + 100 + TCALL_W / 2.0, Z_ON_MIDDLE + TCALL_H / 2.0),
                  (-1, 0, 0), "USB_C"),
        # Antenna SMA on +Z top center for routing cleanliness.
        "Antenna_SMA": ((+32.5 + TCALL_L / 2.0, mp_y + 100 + TCALL_W / 2.0,
                         Z_ON_MIDDLE + TCALL_H),
                        (0, 0, +1), "SMA"),
    },
    "RTL_SDR_V4": {
        # USB-A male built into -X short edge. Antenna SMA on +Z top center.
        "USB_A": ((mp_x + MIDDLE_FLOOR_L / 2.0 + 20, 0.0,
                   Z_ON_MIDDLE + RTLSDR_H / 2.0),
                  (-1, 0, 0), "USB_A"),
        "Antenna_SMA": ((mp_x + MIDDLE_FLOOR_L / 2.0 + 20 + RTLSDR_L / 2.0, 0.0,
                         Z_ON_MIDDLE + RTLSDR_H),
                        (0, 0, +1), "SMA"),
    },
    "XIAO_Meshtastic": {
        # XIAO is at X=-107.5..-82.5 — its -X face is only 20 mm from the
        # case wall at X=-127.5, no room for a 24 mm USB-C plug body. So
        # USB-C on +X short edge (toward Pi 5 stack); antenna on -Y face.
        "USB_C": ((mp_x + 15 + XIAO_L,
                   mp_y + MIDDLE_FLOOR_W - XIAO_W - 15 + XIAO_W / 2.0,
                   Z_ON_MIDDLE + XIAO_H / 2.0),
                  (+1, 0, 0), "USB_C"),
        "Antenna_SMA": ((mp_x + 15 + XIAO_L / 2.0,
                         mp_y + MIDDLE_FLOOR_W - XIAO_W - 15,    # -Y face
                         Z_ON_MIDDLE + XIAO_H / 2.0),
                        (0, -1, 0), "SMA"),
    },
    "Sonoff_ZBDongle": {
        # USB-A male built into +X short edge.
        "USB_A": ((-40.0 + SONOFF_L, -55.0 + SONOFF_W / 2.0,
                   Z_ON_MIDDLE + SONOFF_H / 2.0),
                  (+1, 0, 0), "USB_A"),
    },
    "DCF77": {
        # 3-pin signal/power header on +X short edge (PCB tail).
        "GPIO": ((+DCF77_L / 2.0,
                  mp_y + MIDDLE_FLOOR_W - DCF77_W - 15 + DCF77_W / 2.0,
                  Z_ON_MIDDLE + DCF77_H / 2.0),
                 (+1, 0, 0), "GPIO"),
    },
    "RockBLOCK_9603": {
        # SMA antenna on top center; ribbon header on +Y face mid-X mid-Z.
        "Antenna_SMA": ((mp_x + MIDDLE_FLOOR_L - ROCKBLOCK_L - 15 + ROCKBLOCK_L / 2.0,
                         mp_y + 15 + ROCKBLOCK_W / 2.0,
                         Z_ON_MIDDLE + ROCKBLOCK_H),
                        (0, 0, +1), "SMA"),
        "GPIO": ((mp_x + MIDDLE_FLOOR_L - ROCKBLOCK_L - 15 + ROCKBLOCK_L / 2.0,
                  mp_y + 15 + ROCKBLOCK_W,
                  Z_ON_MIDDLE + ROCKBLOCK_H / 2.0),
                 (0, +1, 0), "GPIO"),
    },
    "Pi5_under": {
        # USB-A row on +X face (4 receptacles in 2×2 grid, simplified to 4
        # distinct Y positions at mid-Z). GPIO header on -Y face top edge.
        # DSI connector on +Z top face near +X edge.
        "USB_A_1": ((_STACK_X_CENTRE + PI5_W / 2.0, _STACK_Y_CENTRE - 26.0,
                     _Z_PI5_BOT + PI5_H / 2.0),
                    (+1, 0, 0), "USB_A"),
        "USB_A_2": ((_STACK_X_CENTRE + PI5_W / 2.0, _STACK_Y_CENTRE - 9.0,
                     _Z_PI5_BOT + PI5_H / 2.0),
                    (+1, 0, 0), "USB_A"),
        "USB_A_3": ((_STACK_X_CENTRE + PI5_W / 2.0, _STACK_Y_CENTRE + 9.0,
                     _Z_PI5_BOT + PI5_H / 2.0),
                    (+1, 0, 0), "USB_A"),
        "USB_A_4": ((_STACK_X_CENTRE + PI5_W / 2.0, _STACK_Y_CENTRE + 26.0,
                     _Z_PI5_BOT + PI5_H / 2.0),
                    (+1, 0, 0), "USB_A"),
        "GPIO":    ((_STACK_X_CENTRE, _STACK_Y_CENTRE - PI5_L / 2.0,
                     _Z_PI5_BOT + PI5_H - 4.0),
                    (0, -1, 0), "GPIO"),
        # DSI is a horizontal-exit FFC connector on the Pi 5 PCB top, near
        # the +Y long edge — the FFC extends parallel to the PCB.
        "DSI":     ((_STACK_X_CENTRE + PI5_W / 2.0 - 5.0,
                     _STACK_Y_CENTRE + PI5_L / 2.0,
                     _Z_PI5_BOT + PI5_H - 2.0),
                    (0, +1, 0), "DSI"),
    },
    "X1202_UPS": {
        # Real X1202: USB-C IN + 2 USB-A OUT all lined up on one short edge.
        # In rotated stack this is the -Y face (Y = -X1202_L/2 = -48.5).
        "USB_C_IN":    ((_STACK_X_CENTRE - 26.0,
                         _STACK_Y_CENTRE - X1202_L / 2.0,
                         _Z_X1202_BOT + X1202_H / 2.0),
                        (0, -1, 0), "USB_C"),
        "USB_A_OUT_1": ((_STACK_X_CENTRE,
                         _STACK_Y_CENTRE - X1202_L / 2.0,
                         _Z_X1202_BOT + X1202_H / 2.0),
                        (0, -1, 0), "USB_A"),
        "USB_A_OUT_2": ((_STACK_X_CENTRE + 26.0,
                         _STACK_Y_CENTRE - X1202_L / 2.0,
                         _Z_X1202_BOT + X1202_H / 2.0),
                        (0, -1, 0), "USB_A"),
    },
    # ---- Case-anchored bulkheads (inner-face ports) ----
    # Bulkhead bodies are placed in WORLD frame above; pigtails terminate at
    # the cavity-side face of each body.
    "Bulkhead_SMA_UHF":     {"INNER": ((+_BULK_INNER_FACE_X, +25.0, _BULK_Z), (-1, 0, 0), "SMA")},
    "Bulkhead_SMA_SDR":     {"INNER": ((+_BULK_INNER_FACE_X, -25.0, _BULK_Z), (-1, 0, 0), "SMA")},
    "Bulkhead_SMA_LTE":     {"INNER": ((-_BULK_INNER_FACE_X, +25.0, _BULK_Z), (+1, 0, 0), "SMA")},
    "Bulkhead_SMA_Iridium": {"INNER": ((-_BULK_INNER_FACE_X, -25.0, _BULK_Z), (+1, 0, 0), "SMA")},
    "Bulkhead_SMA_LoRa":    {"INNER": ((-_BULK_INNER_FACE_X, +60.0, _BULK_Z), (+1, 0, 0), "SMA")},
    "Bulkhead_SMA_WiFi":    {"INNER": ((+_BULK_INNER_FACE_X, +50.0, _BULK_Z), (-1, 0, 0), "SMA")},
    "Bulkhead_USBC":        {"INNER": ((_USBC_BULK_X, _USBC_INNER_FACE_Y, _USBC_BULK_Z),
                                       (0, +1, 0), "USB_C")},
    # ---- Display (DSI input on rear) ----
    "Display": {
        "DSI": ((_DISP_HUMP_X + DISPLAY_HUMP_L / 2.0 - 10,
                 _DISP_HUMP_Y + DISPLAY_HUMP_W / 2.0,
                 _DISP_HUMP_BOT),
                (0, 0, -1), "DSI"),
    },
}


def _p(device, port_id):
    return _PORTS[device][port_id]


def _cable(label, color, port_a, port_b, via, cable_radius, bend_radius):
    """Convenience wrapper that resolves two _PORTS entries and calls _add_cable."""
    fa, da, pa = port_a
    fb, db, pb = port_b
    _add_cable(fa, da, pa, fb, db, pb, via, cable_radius, bend_radius, label, color)


# =========================================================================
# RF pigtails (6) — bulkhead inner face ↔ radio antenna SMA
# =========================================================================
# All radio antennas exit +Z (top of device); pigtails route up to bulkhead Z
# (+25), then horizontally to the bulkhead, with diagonal segments where the
# Z gap between radio top and bulkhead is too tight for axis-aligned bends.

# UV-K5 → UHF bulkhead (+X side, +25Y). UV-K5 top at -12.1.
_cable("RF_Cable_UVK5", CLR_RF_CABLE,
       _p("UV-K5_AIOC", "Antenna_SMA"),
       _p("Bulkhead_SMA_UHF", "INNER"),
       via=[
           (+45.0, 0.0, +25.0),                    # rise to bulkhead Z
           (+45.0, +25.0, +25.0),                  # north to bulkhead Y
       ],
       cable_radius=_PIGTAIL_R, bend_radius=SMA_BEND_R)

# RTL-SDR → SDR bulkhead (+X side, -25Y). RTL top at +8.7.
_cable("RF_Cable_RTL_SDR", CLR_RF_CABLE,
       _p("RTL_SDR_V4", "Antenna_SMA"),
       _p("Bulkhead_SMA_SDR", "INNER"),
       via=[
           (+54.5, 0.0, +48.0),                    # rise high above device top
           (+54.5, -25.0, +48.0),                  # south to bulkhead Y
           (+95.0, -25.0, +25.0),                  # diagonal down to bulkhead Z while moving toward bulkhead X
       ],
       cable_radius=_PIGTAIL_R, bend_radius=SMA_BEND_R)

# T-Call → LTE bulkhead (-X side, +25Y). TCall top at +10.7.
_cable("RF_Cable_TCall", CLR_RF_CABLE,
       _p("LilyGO_TCall", "Antenna_SMA"),
       _p("Bulkhead_SMA_LTE", "INNER"),
       via=[
           (+70.0, +30.0, +48.0),                  # rise high above plate
           (-100.0, +30.0, +48.0),                 # west across cavity
           (-100.0,  0.0, +25.0),                  # diagonal down (ΔY=-30, ΔZ=-23)
           (-100.0, +25.0, +25.0),                 # north to bulkhead Y row
       ],
       cable_radius=_PIGTAIL_R, bend_radius=SMA_BEND_R)

# RockBLOCK → Iridium bulkhead (-X side, -25Y). RockBLOCK top at +11.7.
_cable("RF_Cable_RockBLOCK", CLR_RF_CABLE,
       _p("RockBLOCK_9603", "Antenna_SMA"),
       _p("Bulkhead_SMA_Iridium", "INNER"),
       via=[
           (+85.0, -47.5, +48.0),                  # rise
           (-100.0, -47.5, +48.0),                 # west
           (-100.0, -25.0, +25.0),                 # diagonal in to bulkhead
       ],
       cable_radius=_PIGTAIL_R, bend_radius=SMA_BEND_R)

# XIAO Meshtastic → LoRa bulkhead (-X side, +60Y). XIAO antenna exits -Y
# (south) — cable swings far south to avoid the close-quarters routing
# problem (bulkhead is only 19.75 mm west of XIAO, can't fit a clean U-turn).
_cable("RF_Cable_LoRa", CLR_RF_CABLE,
       _p("XIAO_Meshtastic", "Antenna_SMA"),
       _p("Bulkhead_SMA_LoRa", "INNER"),
       via=[
           (-95.0,   0.0, Z_ON_MIDDLE + XIAO_H / 2.0),    # south
           (-95.0,   0.0, +25.0),                         # rise to bulkhead Z
           (-95.0, +60.0, +25.0),                         # north to bulkhead Y row
       ],
       cable_radius=_PIGTAIL_R, bend_radius=SMA_BEND_R)

# WiFi adapter → WiFi bulkhead (+X side, +50Y). WiFi antenna exits -X (the
# adapter's RP-SMA is on the end opposite the USB-A plug). Cable goes -X off
# the adapter, then north along the bottom plate, up to bulkhead Z, then east
# along the +50 Y row to the bulkhead.
_cable("RF_Cable_WiFi", CLR_RF_CABLE,
       _p("WiFi_Adapter", "Antenna_SMA"),
       _p("Bulkhead_SMA_WiFi", "INNER"),
       via=[
           (-30.0, +UVK5_W / 2.0 + 7.0 + WIFI_W / 2.0,
            Z_ON_BOTTOM + WIFI_H / 2.0),                            # -X across plate
           (-30.0, +80.0, Z_ON_BOTTOM + WIFI_H / 2.0),               # +Y to clear UVK5
           (-30.0, +80.0, +25.0),                                    # rise to bulkhead Z
           (+95.0, +80.0, +25.0),                                    # +X across to near-bulkhead
           (+95.0, +50.0, +25.0),                                    # -Y to bulkhead row
       ],
       cable_radius=_PIGTAIL_R, bend_radius=SMA_BEND_R)

# =========================================================================
# USB-C internal cable (1) — case bulkhead → X1202 USB-C IN
# =========================================================================
# Bulkhead inner face at (+100, -87.5, +25) exits +Y; X1202 USB-C IN at
# (-104.5, -48.5, +8.2) exits -Y. Cable runs north off the bulkhead to clear
# the case wall, descends diagonally to X1202 Z (only 16.8 mm Z gap means a
# pure -Z bend won't fit USB-C bend radius of 20 mm), then west to the X1202.
# Bulkhead inner face (+100, -87.5, +25) plug exits +Y; X1202 USB-C-IN on -Y
# face of stack at (-104.5, -48.5, +8.2) plug exits -Y. Both tangents are +Y
# at their respective polyline endpoints, so the cable has to U-curve south
# along the front-wall corridor before approaching the X1202 from below.
# Route: north off bulkhead → diagonal west+down → south to clear X1202 →
# west across to under-X1202 → north into the X1202 plug. ~340 mm route.
_cable("USBC_Internal_Cable", CLR_USBC_CABLE,
       _p("Bulkhead_USBC", "INNER"),
       _p("X1202_UPS", "USB_C_IN"),
       via=[
           (+100.0, -45.0, +25.0),                                       # +Y from bulkhead
           (+50.0,  -45.0, _Z_X1202_BOT + X1202_H / 2.0),                 # diagonal -X & -Z
           (+50.0,  -88.0, _Z_X1202_BOT + X1202_H / 2.0),                 # -Y to corridor
           (-104.5, -88.0, _Z_X1202_BOT + X1202_H / 2.0),                 # -X across cavity
       ],
       cable_radius=_X1202_USBC_R, bend_radius=USB_C_BEND_R)

# =========================================================================
# DSI ribbon (1) — Pi 5 DSI connector → display rear
# =========================================================================
# FFC route: exits Pi 5 +Y, climbs up to clear top plate (which has a 20 mm
# DSI cutout at world (-20, +10) but our route is west of that), bends west
# and south through the cutout area, and folds up into the display rear DSI.
_cable("DSI_Ribbon", CLR_DSI,
       _p("Pi5_under", "DSI"),
       _p("Display", "DSI"),
       via=[
           (_STACK_X_CENTRE + PI5_W / 2.0 - 5.0, _STACK_Y_CENTRE + PI5_L / 2.0 + 18.0, _Z_PI5_BOT + PI5_H - 2.0),
           (_STACK_X_CENTRE + PI5_W / 2.0 - 5.0, _STACK_Y_CENTRE + PI5_L / 2.0 + 18.0, +20.0),
           (-20.0, _STACK_Y_CENTRE + PI5_L / 2.0 + 18.0, +20.0),
           (-20.0, +10.0, +20.0),
       ],
       cable_radius=_DSI_R, bend_radius=DSI_BEND_R)

# =========================================================================
# USB cables on the bottom plate (4) — into the hub +X face
# =========================================================================
# All hub-side cables enter +X face ports P1..P4. Other end depends on which
# device they're for. AIOC is on top of UV-K5 (USB-C plug entering +Z); GPS,
# RTL-SDR, Sonoff are USB-A male built into device short edges.

# AIOC → Hub P3
_cable("USB_AIOC_to_Hub", CLR_USB_CABLE,
       _p("UV-K5_AIOC", "AIOC_USB_C"),
       _p("USB_Hub", "P3"),
       via=[
           (0.0, 0.0, Z_ON_BOTTOM + UVK5_H + 60.0),    # rise high off AIOC
           (-50.0, 0.0, Z_ON_BOTTOM + UVK5_H + 60.0),  # west
           (-50.0, -19.0, Z_ON_BOTTOM + HUB_H / 2.0),  # drop diagonally toward hub P3
       ],
       cable_radius=_USB_R, bend_radius=USB_C_BEND_R)

# GPS → Hub P4
_cable("USB_GPS_to_Hub", CLR_USB_CABLE,
       _p("GPS", "USB_A"),
       _p("USB_Hub", "P4"),
       via=[
           (-30.0, bp_y + 15 + GPS_W / 2.0,  Z_ON_BOTTOM + GPS_H / 2.0),
           (-30.0, bp_y + 10 + 69.0,         Z_ON_BOTTOM + GPS_H / 2.0),
       ],
       cable_radius=_USB_R, bend_radius=USB_BEND_R)

# RTL-SDR → Hub P1 — RTL on middle plate, hub on bottom plate.
_cable("USB_RTL_SDR_to_Hub", CLR_USB_CABLE,
       _p("RTL_SDR_V4", "USB_A"),
       _p("USB_Hub", "P1"),
       via=[
           (mp_x + 30.0, 0.0, Z_ON_MIDDLE + RTLSDR_H / 2.0),
           (mp_x + 30.0, bp_y - 5.0, Z_ON_MIDDLE + RTLSDR_H / 2.0),
           (mp_x + 30.0, bp_y - 5.0, Z_ON_BOTTOM + HUB_H / 2.0),
           (-50.0, bp_y - 5.0, Z_ON_BOTTOM + HUB_H / 2.0),
           (-50.0, bp_y + 10 + 15.0, Z_ON_BOTTOM + HUB_H / 2.0),
       ],
       cable_radius=_USB_R, bend_radius=USB_BEND_R)

# Sonoff → Hub P2 — Sonoff on middle plate.
_cable("USB_Sonoff_to_Hub", CLR_USB_CABLE,
       _p("Sonoff_ZBDongle", "USB_A"),
       _p("USB_Hub", "P2"),
       via=[
           (+90.0, -55.0 + SONOFF_W / 2.0, Z_ON_MIDDLE + SONOFF_H / 2.0),
           (+90.0, bp_y - 5.0, Z_ON_MIDDLE + SONOFF_H / 2.0),
           (+90.0, bp_y - 5.0, Z_ON_BOTTOM + HUB_H / 2.0),
           (-30.0, bp_y - 5.0, Z_ON_BOTTOM + HUB_H / 2.0),
           (-30.0, bp_y + 10 + 33.0, Z_ON_BOTTOM + HUB_H / 2.0),
       ],
       cable_radius=_USB_R, bend_radius=USB_BEND_R)

# =========================================================================
# Direct-to-Pi5 USB cables (4) — XIAO, T-Call, Hub upstream, WiFi adapter
# =========================================================================

# XIAO Meshtastic → Pi 5 USB_A_4. XIAO USB-C now exits +X (toward Pi 5),
# both plugs face away from each other so cable U-turns over the top.
_cable("USB_XIAO_to_Pi5", CLR_USB_CABLE,
       _p("XIAO_Meshtastic", "USB_C"),
       _p("Pi5_under", "USB_A_4"),
       via=[
           (mp_x + 15 + XIAO_L + 40.0, +60.0, Z_ON_MIDDLE + XIAO_H / 2.0),
           (mp_x + 15 + XIAO_L + 40.0, +60.0, _Z_PI5_BOT + PI5_H / 2.0),
           (+0.0, +60.0, _Z_PI5_BOT + PI5_H / 2.0),
           (+0.0, _STACK_Y_CENTRE + 26.0, _Z_PI5_BOT + PI5_H / 2.0),
       ],
       cable_radius=_USB_R, bend_radius=USB_C_BEND_R)

# LilyGO T-Call → Pi 5 USB_A_2. T-Call USB-C is at +30 Y, only 4 mm from
# the closest Pi 5 USB at Y=+26 — too tight for a between-corner leg.
# Re-routed via Pi 5 USB_A_2 (Y=-7) with a service detour over the top.
_cable("USB_TCall_to_Pi5", CLR_USB_CABLE,
       _p("LilyGO_TCall", "USB_C"),
       _p("Pi5_under", "USB_A_2"),
       via=[
           (-7.0, +30.0, Z_ON_MIDDLE + TCALL_H / 2.0),
           (-7.0, +30.0, _Z_PI5_BOT + PI5_H / 2.0),
           (-7.0, +60.0, _Z_PI5_BOT + PI5_H / 2.0),
           (+25.0, +60.0, _Z_PI5_BOT + PI5_H / 2.0),
           (+25.0, _STACK_Y_CENTRE - 7.0, _Z_PI5_BOT + PI5_H / 2.0),
       ],
       cable_radius=_USB_R, bend_radius=USB_C_BEND_R)

# Hub upstream → Pi 5 USB_A_1 — hub on bottom, Pi 5 on middle stack
_cable("USB_Hub_to_Pi5", CLR_USB_CABLE,
       _p("USB_Hub", "UPSTREAM"),
       _p("Pi5_under", "USB_A_1"),
       via=[
           (bp_x + 10 + HUB_W / 2.0, bp_y + 10 + HUB_L + 50.0,
            Z_ON_BOTTOM + HUB_H / 2.0),
           (bp_x + 10 + HUB_W / 2.0, bp_y + 10 + HUB_L + 50.0,
            _Z_PI5_BOT + PI5_H / 2.0),
           (_STACK_X_CENTRE + PI5_W / 2.0 + 30.0,
            bp_y + 10 + HUB_L + 50.0,
            _Z_PI5_BOT + PI5_H / 2.0),
           (_STACK_X_CENTRE + PI5_W / 2.0 + 30.0,
            _STACK_Y_CENTRE - 26.0,
            _Z_PI5_BOT + PI5_H / 2.0),
       ],
       cable_radius=_USB_R + 0.25, bend_radius=USB_BEND_R)

# WiFi adapter → Pi 5 USB_A_3. WiFi USB-A now exits -X (USB-A end is on the
# adapter's -X short edge) — cable goes west off the adapter, then up and
# over to Pi 5 USB row.
_cable("USB_WiFi_Adapter_to_Pi5", CLR_USB_CABLE,
       _p("WiFi_Adapter", "USB_A"),
       _p("Pi5_under", "USB_A_3"),
       via=[
           (-30.0, +UVK5_W / 2.0 + 7.0 + WIFI_W / 2.0,
            Z_ON_BOTTOM + WIFI_H / 2.0),
           (-30.0, +UVK5_W / 2.0 + 7.0 + WIFI_W / 2.0,
            _Z_PI5_BOT + PI5_H / 2.0),
           (-30.0, _STACK_Y_CENTRE + 9.0, _Z_PI5_BOT + PI5_H / 2.0),
       ],
       cable_radius=_USB_R, bend_radius=USB_BEND_R)

# =========================================================================
# GPIO cables (2) — Pi 5 GPIO header → DCF77 + RockBLOCK
# =========================================================================
# Pi 5 GPIO header on -Y face: cables exit -Y, then route to each module.

# GPIO → RockBLOCK 9603 (Iridium). Pi 5 GPIO header is on the -Y face of
# the rotated stack (Y=-42.5). RockBLOCK GPIO is on its +Y face at
# (+85, mp_y+15+ROCKBLOCK_W=-25, Z_ON_MIDDLE+ROCKBLOCK_H/2=+3.7), exit +Y.
# Both ports want cable to come from "south" (in -Y or out-of-Pi5 -Y) — but
# RockBLOCK +Y means cable approaches RockBLOCK from +Y side (north). So
# route loops east along south side, then comes back north into RockBLOCK.
_cable("GPIO_to_Iridium_Modem", CLR_GPIO_CABLE,
       _p("Pi5_under", "GPIO"),
       _p("RockBLOCK_9603", "GPIO"),
       via=[
           (_STACK_X_CENTRE, -75.0, _Z_PI5_BOT + PI5_H - 4.0),
           (mp_x + MIDDLE_FLOOR_L - ROCKBLOCK_L - 15 + ROCKBLOCK_L / 2.0,
            -75.0, _Z_PI5_BOT + PI5_H - 4.0),
           (mp_x + MIDDLE_FLOOR_L - ROCKBLOCK_L - 15 + ROCKBLOCK_L / 2.0,
            -75.0, Z_ON_MIDDLE + ROCKBLOCK_H / 2.0),
       ],
       cable_radius=_GPIO_R, bend_radius=GPIO_BEND_R)

# GPIO → DCF77: Pi 5 GPIO header -Y face → south of stack → east → north to
# DCF77 +X-edge header. Last leg in +X direction approaching DCF77 plug.
_cable("GPIO_to_DCF77", CLR_GPIO_CABLE,
       _p("Pi5_under", "GPIO"),
       _p("DCF77", "GPIO"),
       via=[
           (_STACK_X_CENTRE, -75.0, _Z_PI5_BOT + PI5_H - 4.0),
           (+30.0, -75.0, _Z_PI5_BOT + PI5_H - 4.0),
           (+30.0, +62.5, _Z_PI5_BOT + PI5_H - 4.0),
           (+30.0, +62.5, Z_ON_MIDDLE + DCF77_H / 2.0),
       ],
       cable_radius=_GPIO_R, bend_radius=GPIO_BEND_R)

# =========================================================================
# X1202 power-output cables (2) — UV-K5 charge + Hub bus power
# =========================================================================
# X1202 has 3 power ports lined up on its -Y face: USB-C IN (charging input),
# USB-A OUT 1 (UV-K5 charge), USB-A OUT 2 (Hub power input). Cables exit -Y
# and route around plate edges down to bottom-plate destinations through the
# middle-plate central pass-through.

# X1202 USB-A OUT 1 → UV-K5 USB-C charge. With USB_A_PLUG_L=22, X1202 -Y
# plug_back is at Y=-70.5 (4 mm clearance to cavity wall at Y=-90 in the
# middle band). First leg -Y must be ≥ 15 — go to Y=-87. Cable then runs
# east at corridor-Y, descends to bottom-plate Z, continues east to UV-K5,
# then takes a +Y leg up to the charge port (last leg -Y into the +Y port).
_cable("USB_X1202_to_UVK5", CLR_POWER_CABLE,
       _p("X1202_UPS", "USB_A_OUT_1"),
       _p("UV-K5_AIOC", "USB_C_charge"),
       via=[
           (_STACK_X_CENTRE, -87.0, _Z_X1202_BOT + X1202_H / 2.0),
           (0.0, -87.0, _Z_X1202_BOT + X1202_H / 2.0),
           (0.0, -87.0, Z_ON_BOTTOM + UVK5_H / 2.0),
           (0.0, +75.0, Z_ON_BOTTOM + UVK5_H / 2.0),
           (+45.0, +75.0, Z_ON_BOTTOM + UVK5_H / 2.0),
       ],
       cable_radius=_POWER_R, bend_radius=POWER_BEND_R)

# X1202 USB-A OUT 2 → Hub POWER_IN (5th +X-face port at hub south end).
_cable("USB_X1202_to_Sabrent_Hub", CLR_POWER_CABLE,
       _p("X1202_UPS", "USB_A_OUT_2"),
       _p("USB_Hub", "POWER_IN"),
       via=[
           (_STACK_X_CENTRE + 26.0, -87.0, _Z_X1202_BOT + X1202_H / 2.0),
           (+30.0, -87.0, _Z_X1202_BOT + X1202_H / 2.0),
           (+30.0, -87.0, Z_ON_BOTTOM + HUB_H / 2.0),
           (-30.0, bp_y + 10, Z_ON_BOTTOM + HUB_H / 2.0),
       ],
       cable_radius=_POWER_R, bend_radius=POWER_BEND_R)

# =========================================================================
# Cable-length report (post-build sanity)
# =========================================================================
print("Cable length report:")
for _label, _length in _CABLE_LENGTHS:
    print(f"  {_label:<32s}: {_length:6.1f} mm")

if _BEND_RADIUS_VIOLATIONS:
    print("\nBEND RADIUS VIOLATIONS (DRY_RUN_CABLES mode):")
    for _v in _BEND_RADIUS_VIOLATIONS:
        print(f"  - {_v}")

# ---- Rotate the case shell 180° about Z (insides stay put) ----
# Net of "rotate whole model" + "rotate insides back" — the case rotates
# while the scaffold keeps its original orientation. Result: hinge ends up
# on +Y, latches/handle/valve move to -Y/+X respectively, and the display
# (on the scaffold's original -Y side) ends up on the same face as the
# latches — i.e. what FreeCAD's "Front" view shows on open.
_CASE_LABELS = {"Case_Base", "Case_Lid", "Latch_1", "Latch_2",
                "Handle", "Pressure_Valve"}
_rotated = []
for _p in parts:
    if _p.label in _CASE_LABELS:
        _r = _p.rotate(Axis.Z, 180)
        _r.label = _p.label
        _r.color = _p.color
        _rotated.append(_r)
    else:
        _rotated.append(_p)
parts = _rotated

# ---- Export ----
assembly = Compound(children=parts, label="Field_Kit")

output_path = "field_kit.step"
export_step(assembly, output_path)

# Heights are measured from the case interior floor (Z = Z_BOTTOM in the
# centred frame); not absolute Z.
stack_height = (Z_ON_TOP + DISPLAY_PROTRUSION) - Z_BOTTOM
print(f"✓ Exported STEP file: {output_path}")
print(f"  Total parts: {len(parts)} (incl. base + lid + 2 latches + handle + valve + 3 floors + 4 rods + 24 nuts + 66 labels)")
print(f"  Stack height: {stack_height}mm (top of display above case floor)")
print(f"  Case height:  {CASE_INTERNAL_H}mm")
print(f"  Headroom:     {CASE_INTERNAL_H - stack_height}mm")
