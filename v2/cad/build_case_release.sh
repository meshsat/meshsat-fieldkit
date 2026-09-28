#!/usr/bin/env bash
# Regenerate the MeshSat V2 case set (MESHSAT-1357, 27 Sep 2026) into <out dir>, from a clone of this repository.
# Needs the CAD venv of v2/cad/requirements-cad.lock (PY, default .venv-cad/bin/python) and, only with REFETCH_MODELS=1, the network.
# Nothing here reads or writes outside the clone and <out dir>; no KiCad, no Blender, no GPU. See v2/cad/README.md.
#   v2/cad/build_case_release.sh /tmp/case-out            # regenerate from the committed zstack-models.json
#   REFETCH_MODELS=1 v2/cad/build_case_release.sh /tmp/x  # also re-fetch the KiCad library models and recompute their boxes
set -euo pipefail
OUT="${1:?usage: build_case_release.sh <out dir>}"
PY="${PY:-.venv-cad/bin/python}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p "$OUT"/{face-plate,frame-legs,connector-plate,rf-entry-plates,lid-tray-qmx,templates,drawings,zstack,margins}
export CASE_BASE_COMMIT="${CASE_BASE_COMMIT:-$(git rev-parse --short=8 HEAD 2>/dev/null || echo unknown)}"
if [ "${REFETCH_MODELS:-0}" = "1" ]; then
  "$PY" v2/cad/model_bbox.py "$OUT/.3dmodels" > v2/cad/zstack-models.json
fi
python3 v2/cad/zstack.py --json v2/cad/zstack.json --report > "$OUT/zstack/zstack-report.txt"   # stdlib: the board reading
cp v2/cad/zstack.json v2/cad/zstack-models.json "$OUT/zstack/"
python3 v2/ecad/tools/z_budget.py > "$OUT/zstack/z-budget.txt" || true                         # prints the face budget; exit 1 only below 2.0 at the worst
"$PY" v2/cad/face_plate.py "$OUT/face-plate"
"$PY" v2/cad/frame_leg.py "$OUT/frame-legs"
"$PY" v2/cad/connector_plate.py "$OUT/connector-plate"
"$PY" v2/cad/rf_entry_plate.py "$OUT/rf-entry-plates"
"$PY" v2/cad/lid_bracket_qmx.py "$OUT/lid-tray-qmx"                                      # the QMX lid tray (C5); its place is sheet 14
PY="$PY" bash v2/cad/build_lid_tray_r2.sh "$OUT"                                          # the QMX lid tray r2 (27 Sep 2026), which supersedes the line above and sheet 14
"$PY" v2/cad/plate_drawing.py "$OUT/face-plate/face-plate.dxf" "$OUT/drawings/face-plate-drawing.pdf"
"$PY" v2/cad/case_drawings.py "$OUT/drawings"
"$PY" v2/ecad/tools/case_wall_cutouts.py "$OUT/templates/case-templates-1to1.pdf" --face "$OUT/face-plate/face-plate.dxf" "$OUT/templates/face-plate-1to1-A3.pdf"
cp v2/vendor/peli/1450/frame_seat.out v2/docs/CASE-FIT-UNCERTAINTIES.md "$OUT/margins/"                 # the margins the drawings label
python3 v2/cad/case_manifest.py "$OUT"   # write the folder's README.md first when there is one, or re-run this line after it
echo "CASE-RELEASE-BUILT $OUT"
