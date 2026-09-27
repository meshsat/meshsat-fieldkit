#!/bin/bash
# r8int6: stream w4r onto the integration worktree (idempotent: each step checks whether it is already applied).
# Usage: apply_w4r_r8int6.sh <worktree root> <stream worktree root>
set -e
W=$1; S=$2; K=$(dirname "$(readlink -f "$0")")
T=v2/ecad/tools
for f in $T/block_contract.py $T/tests/test_block_contract.py $T/tests/test_per_board_contract_verdict.py; do
  cp "$S/$f" "$W/$f"
done
# the coverage map is merged, never copied: main changed other rows (ENV-001's verified_sha) since 91894cd7
if ! grep -q "verdict_by_board: {e5:" "$W/$T/pcb_rules_coverage.yaml"; then
  git -C "$W" show 91894cd7:$T/pcb_rules_coverage.yaml > /tmp/.r8int6_cov_base.$$
  git merge-file -p "$W/$T/pcb_rules_coverage.yaml" /tmp/.r8int6_cov_base.$$ "$S/$T/pcb_rules_coverage.yaml" > /tmp/.r8int6_cov_out.$$
  mv /tmp/.r8int6_cov_out.$$ "$W/$T/pcb_rules_coverage.yaml"; rm -f /tmp/.r8int6_cov_base.$$
fi
grep -q "verdict_by_board" "$W/$T/rules_status.py"            || python3 "$K/patch_rules_status.py" "$W"
grep -q '"pcbnew"' "$W/$T/retake_schematic_phase.py"          || python3 "$K/patch_retake_schematic_phase.py" "$W"
grep -q "verdict_by_board" "$W/$T/rules_render.py"            || python3 "$K/patch_rules_render_coverage_page.py" "$W"
grep -q "2026 (stream w4r): block_contract.py reads board A" "$W/$T/pcb_rules_coverage.yaml" || python3 "$K/patch_coverage_sch003.py" "$W"
grep -q "Since stream w4r (27 September 2026)" "$W/$T/pcb_requirements.yaml" || python3 "$K/apply_registry.py" "$W"
python3 "$K/fixes_w4r_r8int6.py" "$W"
