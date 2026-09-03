"""
MeshSat Field Kit — Shared CONFIG

Pure scalar constants. No FreeCAD or build123d dependencies, so both
field_kit_build.py (FreeCAD) and field_kit_step.py (build123d) can import
from it regardless of which Python runtime they're running under.

Edit values here and re-run either script to regenerate the model.

MEASUREMENT STATUS — each dimension tagged:
  [MEASURED]  user-measured / user-confirmed in conversation
  [DATASHEET] from manufacturer datasheet (not verified against the unit)
  [SPEC]      from product listing (less trustworthy than a datasheet)
  [DESIGN]    design choice made here (gaps, tolerances)
  [DERIVED]   computed from other values in this file
  [ESTIMATE]  guess, needs measurement before cutting HDPE

DO NOT CUT MATERIAL until every [ESTIMATE] tag is resolved. As of the last
pass there are no [ESTIMATE] tags left in this file — case internals are
[COMPUTED] from the 152mm external height and the DCF77 is [DATASHEET] for
the ELV DCF-2. Re-verify CASE_INTERNAL_H with a caliper before cutting: if
the real base cavity is shallower than 110mm the stack needs to drop.

Intentionally NOT in this kit (confirmed removed):
  - Samsung 35E 18650 cells (external USB-C DC input instead)
  - Heltec LoRa V4 (LoRa handled externally via T-Echo or similar)
"""

# =============================================================================
# CASE
# =============================================================================
# External 287×220×152mm is [SPEC] from the AliExpress clone listing.
# Interior is not measured; values below are an estimate with ~11mm case-wall
# allowance on each dimension. Lid and base cavities likely differ.
CASE_INTERNAL_L = 260.0      # [DESIGN] TOP opening (= top plate + 5mm all-round);
CASE_INTERNAL_W = 190.0      # [DESIGN] cavity tapers narrower toward the bottom
# Base + lid budget must match the 152mm external height:
#   152 = 110 (base cavity) + 32 (lid cavity) + 3 (base floor) + 3 (lid top) + 4 (gasket seam)
# Typical Pelican 1470-clone proportion is ~77% base / 23% lid. Stack height
# is 108.6mm so the 110mm base leaves ~1.4mm above the display — verify by
# measurement before cutting HDPE; if it's actually closer to 108mm, the
# stack needs to drop or the display protrusion needs to shrink.
CASE_INTERNAL_H = 110.0      # [COMPUTED] base cavity depth from 152mm external
CASE_LID_DEPTH  = 32.0       # [COMPUTED] lid cavity depth from 152mm external

# =============================================================================
# FLOOR PLATES — 3mm HDPE black
# =============================================================================
BOTTOM_FLOOR_L = 240.0       # [MEASURED] case interior is stepped — plates
BOTTOM_FLOOR_W = 160.0       # [MEASURED] are sized to the local cross-section
MIDDLE_FLOOR_L = 245.0       # [MEASURED]
MIDDLE_FLOOR_W = 170.0       # [MEASURED]
TOP_FLOOR_L    = 250.0       # [MEASURED]
TOP_FLOOR_W    = 180.0       # [MEASURED]
FLOOR_THICKNESS = 3.0        # [MEASURED]
PLATE_CORNER_R = 5.0         # [DESIGN] rounded plate corners

# =============================================================================
# STRUCTURAL HARDWARE — defined early so the vertical stack math below can
# use NUT_H to derive plate positions.
# =============================================================================
ROD_DIAMETER = 3.0           # [MEASURED] M3
ROD_INSET    = 12.0          # [MEASURED] from plate edge to rod center
ROD_LENGTH   = 110.0         # [MEASURED] QUARKZMAN M3×110 stainless

M3_HOLE_DIAMETER  = 3.2      # [DERIVED] M3 clearance fit
LED_HOLE_DIAMETER = 8.0      # [MEASURED] Gebildet 8mm panel-mount LEDs
BULKHEAD_SMA_HOLE = 6.5      # [DATASHEET] IP67 SMA bulkhead

# M3 nut — approximated as a short cylinder (real nut is hex).
# Every rod carries 6 nuts: one on each side of each plate (2 × 3 plates).
NUT_OD = 6.0                 # [DATASHEET] M3 nut across-corners ≈ 6.01mm
NUT_H  = 2.4                 # [DATASHEET] M3 nut thickness

# =============================================================================
# CONNECTORS + BEND RADII
# =============================================================================
# Plug overmold dimensions (real-world OEM cable specs). The plug body is
# rendered as a separate solid at every cable endpoint so the cable doesn't
# magically originate inside the device — the plug occupies real volume that
# device placement must clear. (W × H is the plug cross-section, L is the
# tip-to-back-of-overmold length including strain relief.)
USB_A_PLUG_L  = 22.0         # [DATASHEET] compact Type-A male overmold (no
                             # strain-relief boot). Premium boot-included
                             # plugs reach ~30 mm; 22 mm is the common kit
                             # cable. Larger plugs don't fit between X1202
                             # USB-A OUT row (-Y face) and the cavity wall.
USB_A_PLUG_W  = 12.0         # [DATASHEET]
USB_A_PLUG_H  = 16.5         # [DATASHEET]
USB_C_PLUG_L  = 24.0         # [DATASHEET] standard Type-C male, with boot
USB_C_PLUG_W  = 12.0         # [DATASHEET]
USB_C_PLUG_H  = 7.5          # [DATASHEET]
SMA_PLUG_L    = 14.0         # [DATASHEET] male crimp body, post-thread
SMA_PLUG_OD   = 8.0          # [DATASHEET] hex flats
GPIO_HDR_L    = 12.0         # [DESIGN]    Dupont female 2-row back-shell
GPIO_HDR_W    = 10.0         # [DESIGN]
GPIO_HDR_H    = 6.0          # [DESIGN]
DSI_FFC_L     = 5.0          # [DATASHEET] FFC stiffener insert depth
DSI_FFC_W     = 22.0         # [DATASHEET] 22-pin FFC width
DSI_FFC_H     = 1.0          # [DATASHEET]

# Minimum bend radii for static install. The 5×OD static rule (vs the 10×OD
# dynamic rule) is appropriate here: the kit is wired once and not flexed
# repeatedly. Routing must respect both adjacent legs at every corner ≥ this
# value (the validator inside _make_smooth_path_wire enforces it).
USB_BEND_R    = 15.0         # [DESIGN]    static install — between 3× and 5× OD
USB_C_BEND_R  = 15.0         # [DESIGN]    thinner / more flexible, static
SMA_BEND_R    = 12.5         # [DATASHEET] RG-316 minimum (Pasternack)
GPIO_BEND_R   = 12.0         # [DESIGN]    stiff jumper bundle
DSI_BEND_R    = 10.0         # [DESIGN]    FFC ribbon static fold
POWER_BEND_R  = 15.0         # [DESIGN]    USB-A power cable, static

# =============================================================================
# VERTICAL STACK — gaps between plates
# =============================================================================
# Gaps sized to clear the tallest component on each floor with margin:
# bottom: UV-K5 37.5mm + margin.
# middle-to-top gap is dominated by Pi 5 + display-recess stackup — see below.
# AIOC is side-mated to UV-K5 (into audio jacks), so it does not stack height.
# Gap convention: distance from top face of one plate to bottom face of the
# next. Each gap holds two M3 nuts (one above the lower plate, one below the
# upper plate), so the "free air" for components between plates is
# `GAP - 2*NUT_H`. The numbers below are chosen so the 110mm rod fits
# exactly from the nut below the bottom plate to the nut above the top plate:
#   ROD_LENGTH = 2*NUT_H + 3*FLOOR_THICKNESS + BOTTOM_GAP + MIDDLE_GAP
#              = 4.8 + 9 + 45 + 51.2 = 110  ✓
BOTTOM_GAP = 42.3            # [DESIGN] minimum — UV-K5 (37.5) + 2 M3 nuts
                             # (4.8) = 42.3; middle plate dropped as low as
                             # the UV-K5 stack allows
MIDDLE_GAP = 53.9            # [DESIGN] BOTTOM_GAP + MIDDLE_GAP must sum to
                             # 96.2 (rod length math); all extra mm went
                             # here to fit the Pi 5 + X1202 stack

# Case interior floor at Z = -CASE_INTERNAL_H/2 — the rod rests on it. The
# bottom plate floats NUT_H above the floor so the nut below the bottom
# plate has somewhere to sit. Built in a case-centred frame so the STEP's
# raw geometry lands around world origin (FreeCAD's default camera is at
# world origin — keeps `freecad field_kit.step` opening on the model
# rather than the back-left-bottom corner).
Z_CASE_FLOOR = -CASE_INTERNAL_H / 2.0                        # [DERIVED]
Z_BOTTOM     = Z_CASE_FLOOR + NUT_H                          # [DERIVED]
Z_MIDDLE     = Z_BOTTOM + FLOOR_THICKNESS + BOTTOM_GAP       # [DERIVED]
Z_TOP        = Z_MIDDLE + FLOOR_THICKNESS + MIDDLE_GAP       # [DERIVED]

# =============================================================================
# ROD POSITIONS — single source of truth, case-centred frame
# =============================================================================
# The four M3 rods are straight, so all three plates must be drilled at the
# same absolute (X, Y). Anchored to the middle floor's corner inset: the rods
# sit at the middle plate's actual corners — inside the smaller bottom plate
# and inside the larger top plate. Expressed in the case-centred frame (plates
# are centred on the case, which is centred on world origin).
_MP_HX = MIDDLE_FLOOR_L / 2.0
_MP_HY = MIDDLE_FLOOR_W / 2.0
ROD_POSITIONS = [                                            # [DERIVED]
    (-_MP_HX + ROD_INSET, -_MP_HY + ROD_INSET),
    (+_MP_HX - ROD_INSET, -_MP_HY + ROD_INSET),
    (-_MP_HX + ROD_INSET, +_MP_HY - ROD_INSET),
    (+_MP_HX - ROD_INSET, +_MP_HY - ROD_INSET),
]

# =============================================================================
# DISPLAY — Pi Touch Display 2
# =============================================================================
DISPLAY_L           = 189.32 # [DATASHEET] 7" variant outer length (mm)
DISPLAY_W           = 120.24 # [DATASHEET] 7" variant outer width (mm)
DISPLAY_THICKNESS   = 14.92  # [DATASHEET] max rear depth (central hump); front→deepest feature
# The display is NOT a uniform slab. Per the product brief side profile:
#   - Outer flange (full L×W footprint): only ~2 mm thick (glass + bezel)
#   - Central rear hump (smaller footprint): extends to 14.92 mm depth
# This matters here because the Pi 5 + X1202 stack hangs close to the top
# plate, and its top corner sits where the display would be — but only the
# hump is deep enough to collide. The flange zone is thin enough to clear.
DISPLAY_FLANGE_THICKNESS = 2.0   # [DATASHEET] thin outer bezel/glass zone
DISPLAY_HUMP_L           = 100.0 # [DATASHEET] central PCB/mount hump (long)
DISPLAY_HUMP_W           = 70.0  # [DATASHEET] central PCB/mount hump (short)
DISPLAY_HUMP_THICKNESS   = DISPLAY_THICKNESS - DISPLAY_FLANGE_THICKNESS  # [DERIVED]
# Display is recessed into a cutout in the top plate: only the bezel/glass
# sticks above the plate surface. The PCB/connector body hangs below.
DISPLAY_PROTRUSION  = 1.0    # [DESIGN] mm of display above the top plate surface

# =============================================================================
# COMPONENT BOUNDING BOXES
# Visualization placeholders, not detailed geometry.
# =============================================================================

# --- Bottom floor ---------------------------------------------------------
# Geekworm X1202 — UPS HAT + 4× 18650 battery stack (pogo-pin mounted under Pi 5)
X1202_L = 97.0               # [DATASHEET] geekworm.com
X1202_W = 85.0               # [DATASHEET]
X1202_H = 25.0               # [DESIGN] PCB + battery holder stack (was 12 = PCB only)

# Quansheng UV-K5 — handheld ham
UVK5_L = 120.0               # [MEASURED]
UVK5_W = 65.0                # [MEASURED]
UVK5_H = 37.5                # [DATASHEET] — NEED MEASURED HEIGHT WITH AIOC MATED

# AIOC — audio interface mated to UV-K5 audio jacks
AIOC_L = 35.0                # [MEASURED]
AIOC_W = 28.0                # [MEASURED]
AIOC_H = 12.0                # [DATASHEET] AIOC GitHub PCB dims

# Sabrent HB-UM43 USB hub
HUB_L = 86.0                 # [DATASHEET] sabrent.com
HUB_W = 36.0                 # [DATASHEET]
HUB_H = 15.0                 # [DATASHEET]

# GPS puck (generic USB model)
GPS_L = 40.0                 # [MEASURED]
GPS_W = 26.0                 # [MEASURED]
GPS_H = 18.0                 # [DATASHEET] generic u-blox puck — verify against the specific unit

# --- Middle floor ---------------------------------------------------------
# LilyGO T-Call A7670E — cellular
TCALL_L = 75.0               # [MEASURED]
TCALL_W = 30.0               # [MEASURED]
TCALL_H = 15.0               # [DATASHEET] LilyGO spec (check if SIM holder adds)

# RTL-SDR V4
RTLSDR_L = 69.0              # [DATASHEET] rtl-sdr.com
RTLSDR_W = 27.0              # [DATASHEET]
RTLSDR_H = 13.0              # [DATASHEET]

# Seeed XIAO — Meshtastic node (XIAO ESP32-S3 / nRF52 + SX1262 LoRa)
XIAO_L = 25.0                # [MEASURED]
XIAO_W = 20.0                # [MEASURED]
XIAO_H = 5.0                 # [DATASHEET] Seeed XIAO

# Sonoff ZBDongle-E / ZBDongle-P — ZigBee coordinator USB stick
SONOFF_L = 80.0              # [DATASHEET] sonoff zbdongle-e typical
SONOFF_W = 24.0              # [DATASHEET]
SONOFF_H = 12.0              # [DATASHEET]

# USB WiFi adapter — TP-Link Archer T3U Plus (dual-band AC1300 with RP-SMA).
WIFI_L = 97.6                # [DATASHEET] TP-Link Archer T3U Plus
WIFI_W = 25.5                # [DATASHEET]
WIFI_H = 11.7                # [DATASHEET]

# DCF77 receiver (ELV DCF-2 module: small PCB + soldered-on 60mm ferrite
# antenna; PCB tail adds ~10mm of extra length, giving 70mm total).
DCF77_L = 70.0               # [DATASHEET] ELV DCF-2 module (ferrite + PCB tail)
DCF77_W = 15.0               # [DATASHEET]
DCF77_H = 10.0               # [DATASHEET]

# RockBLOCK 9603 — Iridium SBD
ROCKBLOCK_L = 45.0           # [DATASHEET] Ground Control
ROCKBLOCK_W = 45.0           # [DATASHEET]
ROCKBLOCK_H = 16.0           # [DATASHEET]

# --- Top floor ------------------------------------------------------------
# Raspberry Pi 5 + Active Cooler (mounted on underside of top plate)
PI5_L = 85.0                 # [DATASHEET] raspberrypi.com
PI5_W = 56.0                 # [DATASHEET]
PI5_H = 25.0                 # [DATASHEET] includes active cooler
# Standoff height between top plate underside and Pi 5 PCB top. The Pi 5 is
# pogo-mounted on the X1202 UPS (X1202 below, Pi 5 on top). The 2-board
# stack hangs tight to the top plate (PI5_STANDOFF_H = 1mm). The stack is
# shifted in XY to one side of the display — see Pi5_under / X1202_UPS
# placement in field_kit_step.py.
PI5_STANDOFF_H = 1.0         # [DESIGN] stack hangs tight to top plate
