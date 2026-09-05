#!/usr/bin/env bash
# VM side (root@nllei01gpu01): the Peli 1450 render set. Waits for the C6 chain (C6-EXIT in ~/c6.log) and for the go flag ~/render3d/GO (set after the
# preview audit), exports the six boards as GLB with their case-frame origins, converts the STEP set, renders every view with the GPU, stamps a title
# strip on each image, then prints RENDER-EXIT. The service group must be stopped before this runs (the chain scripts do that) and is started at the end.
R=/root/gitlab/products/meshsat/meshsat-fieldkit; E=$R/v2/ecad; H=~/render3d; OUT=$H/out1450; export KICAD9_3DMODEL_DIR=$H/3dmodels
until grep -a -q "C6-EXIT" ~/c6.log 2>/dev/null && [ -f $H/GO ]; do sleep 30; done; date; echo "render set starting"
~/meshsat-services.sh stop 2>&1 | tail -1
mkdir -p $H/glb $OUT
for spec in "pcb-a-power:150x110:pcb-a-power" "pcb-b-compute:150x110:pcb-b-compute" "pcb-c-display:297x210:pcb-c6-backer" "pcb-d-aprs:100x100:pcb-d-aprs" "pcb-e1-dock:150x110:pcb-e1-dock" "pcb-e5-block:150x110:pcb-e5-block"; do
  IFS=: read -r proj org name <<< "$spec"; dir=$E/$proj; [ "$proj" = pcb-e5-block ] && dir=$E/pcb-e1-dock
  board=$(ls $dir/$proj.kicad_pcb 2>/dev/null || ls $dir/*.kicad_pcb | head -1)
  kicad-cli pcb export glb --subst-models --include-pads --user-origin "${org}mm" -o $H/glb/$name.glb "$board" >/dev/null 2>&1 && echo "glb $name from $(basename $board)" || echo "GLB FAILED $name"
done
~/.venv-cad/bin/python3 $H/step2stl.py 2>&1 | grep -v "^$" | tail -12
cd $H && CYCLES_GPU=1 SAMPLES=${SAMPLES:-256} RESPCT=${RESPCT:-100} ~/blender/blender -b -P $H/scene.py -- $OUT all 2>&1 | grep -a -E "RENDERED|SCENE-DONE|MISSING|STL |Error|Traceback|cycles on" | cut -c1-200
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
    d.text((18, h + 8), "MeshSat field kit V2 concept, Peli 1450 (411 x 329 x 154 mm)   view: " + view, fill=(240, 240, 235), font=font)
    d.text((18, h + 42), "rulers in mm, 10 mm ticks, numerals every 50; floor grid 50 mm; prototype design, nothing built; 5 Sep 2026", fill=(180, 180, 175), font=small)
    canvas.save(fn); n += 1
print("title strips on", n, "images")
PY
ls $OUT/*.png | wc -l; ~/meshsat-services.sh start 2>&1 | tail -1; date; echo RENDER-EXIT
