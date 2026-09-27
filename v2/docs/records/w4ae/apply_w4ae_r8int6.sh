#!/bin/bash
# r8int6: stream w4ae onto the integration worktree in its own integration order (integrate.sh), with the registry and
# document drafts in their r8int6 re-derivations; the drafts folder is filed as records by the integrator afterwards
# (hot_r1_trace.py, which the registry binds, is placed first). Idempotent.
# Usage: apply_w4ae_r8int6.sh <worktree root> <stream worktree root>
set -e
W=$1; S=$2; K=$(dirname "$(readlink -f "$0")")
export PYTHONDONTWRITEBYTECODE=1
for f in v2/ecad/tools/gen_sch_a.py v2/ecad/tools/gen_sch_e.py v2/ecad/tools/boards/a.json v2/ecad/tools/boards/e.json \
         v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_sch v2/ecad/pcb-a-power-a23/out/pcb-a-power.net \
         v2/ecad/pcb-a-power-a23/out/pcb-a-power.net.prov.json v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json \
         v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_sch v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net \
         v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net.prov.json v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock-intent.json \
         v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf; do
  mkdir -p "$W/$(dirname "$f")"; cp "$S/$f" "$W/$f"
done
mkdir -p "$W/v2/docs/records/w4ae"; cp "$K/hot_r1_trace.py" "$W/v2/docs/records/w4ae/hot_r1_trace.py"
python3 "$K/derive_w4ae_r8int6.py" "$K"
if [ ! -f "$W/v2/docs/records/w4ae/ids.json" ]; then python3 "$K/apply_registry_r8int6.py" "$W"; fi
cp "$W/v2/docs/records/w4ae/ids.json" "$K/ids.json"
# CONOPS is not edited (the definition restructure at a9f212c7: a circuit correction updates DEFINITION-STATUS.md and
# the records it names, never the baseline), so the conops group of edit_docs is left out
python3 "$K/edit_docs_r8int6.py" "$W" --only=hwfw,panel,interfaces,sources,grade,eq
( cd "$W" && python3 "$K/post_docs_registry_r8int6.py" "$W" )
python3 "$K/fixes_w4ae_r8int6.py" "$W"
