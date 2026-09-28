#!/usr/bin/env bash
# Regenerate the QMX lid tray r2 set (MESHSAT-1357, S-63; second pass of 27 to 28 Sep 2026): <out dir>/lid-tray-qmx-r2/ with the tray, its
# retaining frame and the lid plate (STEP, STL, DXF), the check record (sections A to E and the checks on the solids) and sheets 14r2-1 to
# 14r2-3, plus the three page images for the read-back in <out dir>/.lid-tray-qmx-r2-readback/. Needs the CAD venv of
# v2/cad/requirements-cad.lock (PY, default .venv-cad/bin/python). Nothing here reads or writes outside the clone and <out dir>; no KiCad,
# no network. The folder's README.md is hand-written, not generated; its MANIFEST.sha256 is written last, by v2/cad/case_manifest.py.
set -euo pipefail
OUT="${1:?usage: build_lid_tray_r2.sh <out dir>}"
PY="${PY:-.venv-cad/bin/python}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p "$OUT/lid-tray-qmx-r2" "$OUT/.lid-tray-qmx-r2-readback"
export CASE_BASE_COMMIT="${CASE_BASE_COMMIT:-$(git rev-parse --short=8 HEAD 2>/dev/null || echo unknown)}"
"$PY" v2/vendor/qrp-labs/measure_qmx_figures.py "$OUT/.lid-tray-qmx-r2-readback/qmx-figures.out" > /dev/null
cmp "$OUT/.lid-tray-qmx-r2-readback/qmx-figures.out" v2/vendor/qrp-labs/qmx-figures.out   # the scaled figures the tray is built on
"$PY" v2/cad/lid_tray_qmx_r2.py "$OUT/lid-tray-qmx-r2"
"$PY" v2/cad/lid_tray_qmx_r2_check.py --solids "$OUT/lid-tray-qmx-r2/lid-tray-qmx-r2-check.out" > /dev/null   # exit 1 on a clearance under its minimum, a row NOT MET, a control that passes or a failed solid check
"$PY" v2/cad/lid_tray_qmx_r2_drawing.py "$OUT/.lid-tray-qmx-r2-readback"
mv "$OUT/.lid-tray-qmx-r2-readback/lid-tray-qmx-r2-drawing.pdf" "$OUT/lid-tray-qmx-r2/"
echo "LID-TRAY-R2-BUILT $OUT/lid-tray-qmx-r2 (read the three PNGs in .lid-tray-qmx-r2-readback/ before releasing; then the README.md and case_manifest.py)"
