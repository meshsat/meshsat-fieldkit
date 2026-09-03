"""Render field_kit.step to PNG — website-ready hero shots + technical views.

Produces:
  hero_iso.png        perspective iso, whole kit with antennas
  hero_internals.png  iso with the case hidden, shows cable routing
  top.png             orthographic top-down, shows middle-plate layout
  front.png           orthographic front, shows the display + LED row
  side.png            orthographic side, shows the 3-floor stack
  scaffold.png        iso with case + antennas hidden, pure scaffold
  plate_bottom.png    top-down, only bottom plate's devices + cables + labels
  plate_middle.png    top-down, only middle plate's devices + cables + labels

Run under xvfb-run so FreeCAD's GUI can initialise against a virtual display.
"""
import os
import sys
import time

import FreeCAD as App
import FreeCADGui as Gui
import ImportGui

STEP_PATH = "/home/kyriakosp/Downloads/field_kit/field_kit.step"
OUT_DIR   = "/home/kyriakosp/Downloads/field_kit/renders"
W, H      = 2400, 1600

os.makedirs(OUT_DIR, exist_ok=True)

# Enable 8× multisample anti-aliasing so the raster edges aren't jagged.
view_params = App.ParamGet("User parameter:BaseApp/Preferences/View")
view_params.SetInt("AntiAliasing", 4)
view_params.SetBool("UseVBO", True)

# STEP color import
params = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Import/hSTEP")
params.SetBool("UseLinkGroup", False)
params.SetBool("UseBaseName", True)
params.SetBool("ReduceObjects", False)
part_params = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/STEP")
part_params.SetBool("ReadShapeColors", True)

ImportGui.open(STEP_PATH)
doc = App.ActiveDocument
print(f"[render] loaded {STEP_PATH}: {len(doc.Objects)} objects")


def _iter_features(container):
    todo = list(getattr(container, "Group", []) or [])
    while todo:
        obj = todo.pop()
        if obj.TypeId == "Part::Feature":
            yield obj
        elif obj.TypeId == "App::Part":
            todo.extend(getattr(obj, "Group", []) or [])


CASE_LABELS = {
    "Case_Base": 85, "Case_Lid": 85,
    "Latch_1": 20, "Latch_2": 20,
    "Handle": 15, "Pressure_Valve": 20,
}
ANTENNA_PREFIXES = ("Ant_", "SMA_")
# Case-anchored connector hardware — bulkhead bodies + the USB-C internal
# cable. These belong with the case (not the scaffold), so they must hide on
# the pure-scaffold shot. They stay VISIBLE on the front/side shots because
# they live inside the case wall, not extending out like the antenna whips.
CASE_HARDWARE_PREFIXES = ("Bulkhead_", "USBC_Internal_")

def set_group_transparency(labels_to_pct):
    n = 0
    for obj in doc.Objects:
        lbl = getattr(obj, "Label", "")
        if lbl in labels_to_pct and obj.TypeId == "App::Part":
            for c in _iter_features(obj):
                c.ViewObject.Transparency = labels_to_pct[lbl]
                n += 1
    return n

def set_group_visibility(pred, visible):
    n = 0
    for obj in doc.Objects:
        lbl = getattr(obj, "Label", "")
        if pred(lbl) and obj.TypeId == "App::Part":
            for c in _iter_features(obj):
                c.ViewObject.Visibility = visible
                n += 1
    return n

# Always hide the device-face text labels (they're inspection aids, not hero-shot material)
hidden = set_group_visibility(lambda lbl: "_lbl_" in lbl, False)
print(f"[render] hid {hidden} device-label solids")

# Apply case transparency for the shots that include the case
trans = set_group_transparency(CASE_LABELS)
print(f"[render] set transparency on {trans} case solids")

Gui.updateGui()
time.sleep(0.3)

view = Gui.activeDocument().activeView()

def save(name, bg="White", zoom=1.0):
    view.fitAll()
    if zoom != 1.0:
        try: view.zoom(zoom)
        except Exception: pass
    Gui.updateGui()
    time.sleep(0.15)
    out = os.path.join(OUT_DIR, f"{name}.png")
    view.saveImage(out, W, H, bg)
    print(f"[render] wrote {out}")


# === 1. Hero isometric (perspective, everything visible) ===
try: view.setCameraType("Perspective")
except Exception: pass
view.viewIsometric()
save("hero_iso", zoom=1.15)

# === 2. Internals iso — hide the case + lid + hardware ===
hidden_case = set_group_visibility(lambda lbl: lbl in CASE_LABELS, False)
print(f"[render] hiding case for internals shot: {hidden_case} solids")
view.viewIsometric()
save("hero_internals", zoom=1.1)

# === 3. Pure scaffold shot — case + antennas + case-side hardware all hidden ===
hidden_ants = set_group_visibility(
    lambda lbl: lbl.startswith(ANTENNA_PREFIXES + CASE_HARDWARE_PREFIXES), False)
print(f"[render] also hiding antennas + case hardware: {hidden_ants} solids")
view.viewIsometric()
save("scaffold", zoom=1.1)

# Bring antennas + case-side hardware back for the ortho shots
set_group_visibility(
    lambda lbl: lbl.startswith(ANTENNA_PREFIXES + CASE_HARDWARE_PREFIXES), True)
# Leave the case hidden for cleaner ortho views
try: view.setCameraType("Orthographic")
except Exception: pass

# === 4. Top-down ortho — shows the middle-plate layout ===
view.viewTop()
save("top", zoom=1.1)

# Show the case again (transparent) for the front / side shots
set_group_visibility(lambda lbl: lbl in CASE_LABELS, True)
# Hide antennas for the face shots so the case isn't dwarfed
set_group_visibility(lambda lbl: lbl.startswith(ANTENNA_PREFIXES), False)

# === 5. Front face — the case after 180° rotation has the LED/USB-C face
#        on its Rear in FreeCAD's coord system ===
view.viewRear()
save("front", zoom=1.15)

# === 6. Side view — shows the 3-floor stack ===
view.viewLeft()
save("side", zoom=1.15)

# === 7 & 8. Per-plate detail — top-down ortho focused on a single plate ===
# Show only that plate's floor, its devices, the bulkheads its cables run to,
# the on-plate top-face labels, and any cable whose endpoint touches a device
# on this plate (cable trails to other plates are kept so the wiring layout is
# complete). Side-face labels (_lbl_pX/nX/pY/nY/nZ) are left hidden — in a
# top-down ortho they project as edge-on slivers that just add noise.

BOTTOM_DEVICES = ("UV-K5_AIOC", "USB_Hub", "GPS", "WiFi_Adapter")
BOTTOM_BULKHEADS = ("Bulkhead_SMA_UHF", "Bulkhead_SMA_WiFi")
BOTTOM_CABLE_PFX = (
    "USB_AIOC_to_Hub", "USB_GPS_to_Hub",
    "USB_RTL_SDR_to_Hub", "USB_Sonoff_to_Hub",
    "USB_Hub_to_Pi5", "USB_WiFi_Adapter_to_Pi5",
    "USB_X1202_to_UVK5", "USB_X1202_to_Sabrent_Hub",
    "RF_Cable_UVK5", "RF_Cable_WiFi",
)

MIDDLE_DEVICES = ("LilyGO_TCall", "RTL_SDR_V4", "XIAO_Meshtastic",
                  "Sonoff_ZBDongle", "DCF77", "RockBLOCK_9603",
                  "X1202_UPS", "Pi5_under")
MIDDLE_BULKHEADS = ("Bulkhead_SMA_SDR", "Bulkhead_SMA_LTE",
                    "Bulkhead_SMA_Iridium", "Bulkhead_SMA_LoRa",
                    "Bulkhead_USBC")
MIDDLE_CABLE_PFX = (
    "USB_RTL_SDR_to_Hub", "USB_Sonoff_to_Hub",
    "USB_Hub_to_Pi5", "USB_WiFi_Adapter_to_Pi5",
    "USB_XIAO_to_Pi5", "USB_TCall_to_Pi5",
    "USB_X1202_to_UVK5", "USB_X1202_to_Sabrent_Hub",
    "GPIO_to_Iridium_Modem", "GPIO_to_DCF77",
    "USBC_Internal_Cable", "DSI_Ribbon",
    "RF_Cable_RTL_SDR", "RF_Cable_TCall",
    "RF_Cable_RockBLOCK", "RF_Cable_LoRa",
)

def matches_plate(label, plate, devices, bulkheads, cable_prefixes):
    if label == f"Floor_{plate}":
        return True
    if label in devices or label in bulkheads:
        return True
    if any(label == f"{d}_lbl_pZ" for d in devices):
        return True
    for p in cable_prefixes:
        # The cable solid itself, plus its two overmold bodies
        # (Plug_<cable>_a / Plug_<cable>_b), all share the cable label root.
        if label.startswith(p) or label.startswith(f"Plug_{p}"):
            return True
    return False

# Two-pass to avoid the top assembly container ("Field_Kit") clobbering its
# descendants: hide everything first, then turn on matching containers. This
# is order-independent — iterating the assembly during the hide pass just
# re-hides leaves that the show pass will explicitly enable.
def show_only(predicate):
    for obj in doc.Objects:
        if obj.TypeId == "App::Part":
            for c in _iter_features(obj):
                c.ViewObject.Visibility = False
    n_visible = 0
    for obj in doc.Objects:
        if obj.TypeId == "App::Part" and predicate(getattr(obj, "Label", "")):
            for c in _iter_features(obj):
                c.ViewObject.Visibility = True
            n_visible += 1
    return n_visible

n = show_only(lambda lbl: matches_plate(lbl, "bottom",
                                        BOTTOM_DEVICES, BOTTOM_BULKHEADS,
                                        BOTTOM_CABLE_PFX))
print(f"[render] plate_bottom: {n} parts visible")
# Two updateGui+fitAll cycles are needed under flatpak FreeCAD 1.1 — a single
# viewTop() doesn't fully settle camera state before save, leaving fitAll
# operating on stale geometry and producing blank PNGs.
Gui.updateGui()
time.sleep(0.3)
view.viewTop()
Gui.updateGui()
time.sleep(0.3)
view.fitAll()
Gui.updateGui()
time.sleep(0.3)
save("plate_bottom", zoom=1.2)

n = show_only(lambda lbl: matches_plate(lbl, "middle",
                                        MIDDLE_DEVICES, MIDDLE_BULKHEADS,
                                        MIDDLE_CABLE_PFX))
print(f"[render] plate_middle: {n} parts visible")
Gui.updateGui()
time.sleep(0.3)
view.viewTop()
Gui.updateGui()
time.sleep(0.3)
view.fitAll()
Gui.updateGui()
time.sleep(0.3)
save("plate_middle", zoom=1.2)

App.closeDocument(doc.Name)
print("[render] done")
sys.exit(0)
