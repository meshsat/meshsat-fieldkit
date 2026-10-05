#!/usr/bin/env bash
# MeshSat enclosure v0.6: rebuild every STL from source and run all checks.
# Run from the package root:  bash validation/build_and_check.sh
# Needs: openscad (2021.01+), python3 with trimesh, numpy, manifold3d, scipy.
set -euo pipefail
SCAD=source/meshsat-enclosure-v0.6.scad
OUT=validation/build; mkdir -p "$OUT" print-stl coupons
cd source; S=$(basename "$SCAD"); cd ..

run() { (cd source && openscad --hardwarnings -q -D "PART=\"$1\"" -o "../$2" "$S"); }

echo "== print parts";  for P in body lid separator membrane plungers retainer molle belt; do run "$P" "print-stl/meshsat-$P.stl"; done
echo "== coupons";      for P in coupon_rimlid coupon_board coupon_rails; do run "$P" "coupons/meshsat-$P.stl"; done
echo "== assembled";    cp print-stl/meshsat-body.stl "$OUT/body.stl"
for P in a_lid a_separator a_membrane a_plungers a_retainer; do run "$P" "$OUT/$P.stl"; done
(cd source && openscad -D 'PART="reg"' -o /tmp/_reg.csg "$S" 2>&1) | grep REGJSON | sed 's/^ECHO: "REGJSON //; s/"$//; s/\\"/"/g' > "$OUT/reg.json"

echo "== self-checks (must be empty, except rail lip)"
for C in chk_groove chk_rearbores chk_topbores chk_lid_body chk_rail_lip; do
  msg=$( (cd source && openscad --hardwarnings -D "PART=\"$C\"" -o "../$OUT/$C.stl" "$S" 2>&1) | grep -E "empty|WARNING|ERROR" || true)
  echo "$C: ${msg:-NON-EMPTY}"
done | tee "$OUT/self_checks.txt"

echo "== clash check vs manufacturer STEP meshes"
python3 validation/clash_check.py "$OUT" reference-cad/meshes "$OUT/reg.json" 2>/dev/null | tee "$OUT/clash_check.txt"
echo "== mesh + printability report"
python3 validation/mesh_report.py print-stl coupons | tee "$OUT/mesh_report.txt"
