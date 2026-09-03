# MeshSat Field Kit — FreeCAD Model

FreeCAD 3D model of the MeshSat Field Kit (TESSERACT / PARALLAX builds), generated from a Python script.

## What you get

- Case interior wireframe (265 × 195 × 115mm reference envelope)
- Three HDPE scaffold plates:
  - Bottom (240 × 160mm) with 4× M3 corner holes + pass-through
  - Middle (245 × 170mm) with 4× M3 corner holes + pass-through
  - Top (250 × 180mm) with 4× M3 corner holes + 5× LED holes + DSI pass-through
- 4× M3 × 110mm stainless threaded rods (stylized as silver cylinders)
- Components positioned in final layout:
  - Bottom floor: X1202 UPS, UV-K5 + AIOC brick, Sabrent hub, GPS
  - Middle floor: T-Call, RTL-SDR, XIAO ZigBee, DCF77, RockBLOCK 9603
  - Top floor: Pi Touch Display 2 (above), Pi 5 (below, underside-mounted)

## How to use

### Method 1: GUI (easiest)

1. Open FreeCAD (you already installed it)
2. Menu: **Macro → Macros...**
3. Click **Create** — name it `field_kit_build`
4. In the editor that opens, paste the entire contents of `field_kit_build.py`

5. Save the macro (Ctrl+S)
6. Press **F6** (or click the green play icon) to execute
7. The model generates in a new document
8. File → Save As... → `field_kit.FCStd`

### Method 2: Direct script execution

```bash
freecad field_kit_build.py
```

FreeCAD opens, runs the script, leaves you with the 3D model.

### Method 3: Headless / batch generation

```bash
freecadcmd field_kit_build.py
```

Runs without GUI, saves `.FCStd` file directly.

## Tweaking dimensions

Open `field_kit_config.py` in any editor — it holds every dimension as a named
constant, shared between both the FreeCAD script (`field_kit_build.py`) and the
STEP generator (`field_kit_step.py`):

```python
BOTTOM_FLOOR_L = 240.0
BOTTOM_FLOOR_W = 160.0
# etc.
```

Change a value, re-run either script, regenerate. This is the power of parametric CAD.

## Navigation in FreeCAD

- **Zoom**: mouse wheel
- **Pan**: middle-button drag (or Shift + right-click drag)
- **Rotate**: hold middle-button + left-button (or press `V, O` for axonometric)
- **View presets**: top (numpad `2`), front (`1`), side (`3`), iso (`0`)
- **Fit to window**: `V, F`

## Model coordinate system

- **Origin** at the back-left-bottom corner of the case interior
- **X axis**: runs along the long side of the case (front-to-back, 265mm)
- **Y axis**: runs along the short side (left-to-right, 195mm)
- **Z axis**: vertical (up, 0mm at case floor)

## What's approximate

- **Case outline** is a reference box only (no lid, no hinges, no latches)
- **Components** are simple colored rectangles — not detailed 3D models
- **M3 rods** span the full height at the middle floor's corner positions (actual rod placement depends on your drilling)
- **Cabling** is not modeled

## Next steps once you have the model

- **Verify fit**: use the case wireframe to check everything clears
- **Export drawings**: TechDraw workbench → create 2D drill templates
- **Refine components**: replace simple boxes with STEP files from manufacturers
  - Pi 5: https://github.com/raspberrypi/usbboot (STEP available)
  - RockBLOCK 9603: available as STEP on GrabCAD
  - X1202: request from Geekworm
- **Generate cut files**: export each plate's 2D profile to DXF for laser cutting

## Troubleshooting

**"Module FreeCAD not found"** — you're running with regular Python, not FreeCAD's
Python. Use `freecad` or `freecadcmd` to run the script.

**Script runs but nothing visible** — press **View → Fit All** or `V, F` after
execution.

**Plates look misaligned** — the case coordinate system and plate centering may
conflict. Edit `CASE_INTERNAL_L` / `W` to match your actual measured case.

**Want to edit after generation** — you can manually select and move any object
in FreeCAD's tree view. Changes won't propagate back to the script.

## Where this lives now (3 September 2026)

Moved from the laptop `Team Shared Root/Projects/MeshSat/Field Kit/CAD/` into the `meshsat-fieldkit` repository as `v1/cad/`. The Python virtualenv was not carried over: the scripts import FreeCAD (system install) and `build123d`, so recreate it with `python3 -m venv .venv && .venv/bin/pip install build123d` (`.venv/` is gitignored). `field_kit.step` is stored with Git LFS.
