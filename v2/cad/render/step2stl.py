# convert the vendor STEP models to STL for Blender (build123d / OCP), one file per part, reporting the bounding box of each
import sys, os, time
from build123d import import_step, export_stl
V = os.path.expanduser("~/gitlab/products/meshsat/meshsat-fieldkit/v2")
OUT = os.path.expanduser("~/render3d/stl"); os.makedirs(OUT, exist_ok=True)
JOBS = {
 "case_base": V + "/vendor/peli/1520/1521-931 Bottom PID 7-24-2025.STEP",
 "case_lid": V + "/vendor/peli/1520/1521-931 Top PID 7-24-2025.STEP",
 "panel_frame": V + "/vendor/peli/1520/1523-PF.STEP",
 "td2": V + "/vendor/td2/td2-7inch.step",
 "epaper": V + "/vendor/weact/Hardware/WeAct-EpaperModule-3.7 Board 3D.step",
 "rockblock9704": V + "/vendor/rockblock/RockBLOCK 9704-SMA-2A.step",
 "wio": V + "/vendor/wio/wio-sx1262.step",
 "module_base": V + "/release/revA/module/battery-module-base.step",
 "module_lid": V + "/release/revA/module/battery-module-lid.step",
 "module_cradle": V + "/release/revA/module/battery-module-cradle.step",
}
cm5 = os.path.expanduser("~/render3d/cm5.step")
if os.path.exists(cm5): JOBS["cm5"] = cm5
for name, path in JOBS.items():
    t = time.time()
    try:
        shape = import_step(path)
        bb = shape.bounding_box()
        export_stl(shape, os.path.join(OUT, name + ".stl"), tolerance=0.05, angular_tolerance=0.2)
        print("%-14s ok  %.0fs  bbox x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f" % (name, time.time() - t, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z), flush=True)
    except Exception as e:
        print("%-14s FAILED %s" % (name, str(e)[:120]), flush=True)
print("STL-DONE")
