# convert the vendor STEP models (and the parts built on the VM) to STL for Blender (build123d / OCP), one file per part, reporting the bounding box of each
# 5 Sep 2026: the Peli 1450 set (1451-931 bodies, the 1450PF frame), the aluminium face plate and the battery row module built on the VM
import sys, os, time
from build123d import import_step, export_stl
V = os.path.expanduser("~/gitlab/products/meshsat/meshsat-fieldkit/v2")
H = os.path.expanduser("~/render3d")
OUT = H + "/stl"; os.makedirs(OUT, exist_ok=True)
JOBS = {
 "case1450_bottom": V + "/vendor/peli/1450/1451-931-bottom.STEP",
 "case1450_top": V + "/vendor/peli/1450/1451-931-top.STEP",
 "frame1450": V + "/vendor/peli/1450/1450-panel-frame.STEP",
 "td2": V + "/vendor/td2/td2-7inch.step",
 "epaper": V + "/vendor/weact/Hardware/WeAct-EpaperModule-3.7 Board 3D.step",
 "rockblock9704": V + "/vendor/rockblock/RockBLOCK 9704-SMA-2A.step",
 "face_plate": H + "/plate1450/out/face-plate.step",
 "module_base": H + "/battery1450/battery-module-base.step",
 "module_lid": H + "/battery1450/battery-module-lid.step",
 "module_cradle": H + "/battery1450/battery-module-cradle.step",
}
ONLY = sys.argv[1:]
for name, path in JOBS.items():
    if ONLY and name not in ONLY: continue
    t = time.time()
    try:
        shape = import_step(path)
        bb = shape.bounding_box()
        export_stl(shape, os.path.join(OUT, name + ".stl"), tolerance=0.05, angular_tolerance=0.2)
        print("%-16s ok  %.0fs  bbox x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f" % (name, time.time() - t, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z), flush=True)
    except Exception as e:
        print("%-16s FAILED %s" % (name, str(e)[:160]), flush=True)
print("STL-DONE")
