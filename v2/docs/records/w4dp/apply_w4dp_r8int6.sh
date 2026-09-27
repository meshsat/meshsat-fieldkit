#!/bin/bash
# r8int6: stream w4dp onto the integration worktree in its own order (its files, the TEST-PLAN draft, the registry LAST
# among the registry writers, the coverage notes, the vendor index), each draft in its r8int6 re-derivation. Idempotent.
# Usage: apply_w4dp_r8int6.sh <worktree root> <stream worktree root>
set -e
W=$1; S=$2; K=$(dirname "$(readlink -f "$0")")
for f in v2/ecad/tools/gen_sch_d.py v2/ecad/tools/gen_sch_p.py v2/ecad/tools/pcb_pack_protection.yaml \
         v2/ecad/tools/tests/test_pack_protection.py v2/vendor/power/st-semtech-1n4148w-c81598.pdf \
         v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_sch v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net \
         v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net.prov.json v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json \
         v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_sch v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net \
         v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net.prov.json v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json; do
  cp "$S/$f" "$W/$f"
done
python3 "$K/derive_w4dp_r8int6.py" "$K"
grep -q "second level cell over voltage" "$W/v2/docs/TEST-PLAN.md" || python3 "$K/patch_test_plan_r8int6.py" "$W"
if ! grep -q "stream w4dp, S-45" "$W/v2/ecad/tools/pcb_requirements.yaml" && [ ! -f "$K/ids.json" ]; then
  python3 "$K/apply_registry_r8int6.py" "$W"
fi
grep -q "THE TABLE DESCRIBES THE DRAWN CIRCUIT" "$W/v2/ecad/tools/pcb_rules_coverage.yaml" || python3 "$K/patch_coverage_r8int6.py" "$W"
grep -q "st-semtech-1n4148w-c81598.pdf" "$W/v2/vendor/sources.txt" || python3 "$K/patch_vendor_index.py" "$W"
python3 "$K/fixes_w4dp_r8int6.py" "$W" "$K"
