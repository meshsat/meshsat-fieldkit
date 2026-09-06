#!/usr/bin/env bash
# The Peli 1450 render set on the render box: every view of scene.py with Cycles on every GPU (OptiX where the card has RT cores, else CUDA), then the title
# strips. Inputs under /root/render3d (scene.py, panel1450.py, stl/, glb/, 3dmodels/, epaper.png, ui.png) placed by rsync from the runner. Log /root/render.log,
# marker RENDER-EXIT. Usage: run_render_box.sh [views | all]   SAMPLES and RESPCT as in the VM script (defaults 256 and 100).
H=/root/render3d; OUT=$H/out1450; mkdir -p $OUT; export KICAD9_3DMODEL_DIR=$H/3dmodels LANG=C.UTF-8
date; nvidia-smi --query-gpu=name --format=csv,noheader | sort | uniq -c
cd $H && CYCLES_GPU=1 SAMPLES=${SAMPLES:-256} RESPCT=${RESPCT:-100} /root/blender/blender -b -P $H/scene.py -- $OUT ${1:-all} 2>&1 | grep -a -E "RENDERED|SCENE-DONE|MISSING|STL |Error|Traceback|cycles on" | cut -c1-200
python3 - "$OUT" <<'PY'
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; n = 0
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30); small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
except Exception: font = small = ImageFont.load_default()
for fn in sorted(glob.glob(os.path.join(out, "meshsat-1450-*.png"))):
    im = Image.open(fn).convert("RGB"); w, h = im.size; strip = 64
    canvas = Image.new("RGB", (w, h + strip), (24, 24, 28)); canvas.paste(im, (0, 0)); d = ImageDraw.Draw(canvas)
    view = os.path.basename(fn)[len("meshsat-1450-"):-4]
    d.text((18, h + 8), "MeshSat field kit V2 concept in the Peli 1450 (catalogue 411 x 329 mm)   view: " + view, fill=(240, 240, 235), font=font)
    d.text((18, h + 42), "rulers in mm, 10 mm ticks, numerals every 50; floor grid 50 mm; prototype design, nothing built; 6 Sep 2026", fill=(180, 180, 175), font=small)
    canvas.save(fn); n += 1
print("title strips on", n, "images")
PY
ls $OUT | wc -l; date; echo RENDER-EXIT
