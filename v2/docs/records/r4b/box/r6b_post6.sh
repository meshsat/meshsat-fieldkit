#!/usr/bin/env bash
# MESHSAT-1357 round 6, board B (r6b): runner-side reading of box run 6 (drafts/box/r6-run6, fetched from
# /root/r6/b/out6). Pure Python on the netlists, sub-second each: the netlist differences with my own differ, the gate's
# net section emulated on the committed, pass 3 and round 6 netlists, and the two mutation controls.
set -uo pipefail
D=$(cd "$(dirname "$0")/.." && pwd); B=$D/box; R=$B/r6-run6; N=pcb-b-compute
G=$D/../v2/ecad/tools/check_pcb_b.py; P3=$R/pass3-9b85ada8.net; NEW=$R/tint/regen/$N.net; COM=$R/committed-$N.net
cd "$D"
( cd "$R" && sha256sum -c --quiet SHA256SUMS && echo "r6b-post: SHA256SUMS verified" ) || echo "r6b-post: WARNING SHA256SUMS mismatch"
python3 netdiff.py "$COM" "$NEW" "$B/netdiff-r6b.json"
python3 netdiff_report.py "$B/netdiff-r6b.json" "$B/netdiff-r6b.txt" "Committed B21 netlist (main faf8c981, equal to 82dd1e4d's) against round 6 (generator 6e3d8809..., box/r6-run6/tint/regen)"
python3 netdiff.py "$P3" "$NEW" "$B/netdiff-r6b-round6.json"
python3 netdiff_report.py "$B/netdiff-r6b-round6.json" "$B/netdiff-r6b-round6.txt" "Fix-up pass 3 netlist (generator 9b85ada8..., box/r6-run4/t29/regen) against round 6 (generator 6e3d8809..., box/r6-run6/tint/regen)"
python3 netdiff.py "$R/t6/regen/$N.net" "$NEW"
mkdir -p "$R/check_pcb_b"
for k in committed:$COM pass3:$P3 round6:$NEW; do
  python3 check_pcb_b_emul.py "$G" "${k#*:}" > "$R/check_pcb_b/emul-r6-gate-on-${k%%:*}.txt" 2>&1; tail -1 "$R/check_pcb_b/emul-r6-gate-on-${k%%:*}.txt"
  python3 check_pcb_b_emul.py "$B/check_pcb_b.pass3-720892ae.py" "${k#*:}" > "$R/check_pcb_b/emul-pass3-gate-on-${k%%:*}.txt" 2>&1 || true; tail -1 "$R/check_pcb_b/emul-pass3-gate-on-${k%%:*}.txt"
done
python3 check_pcb_b_en_mutations.py "$G" "$NEW" > "$R/check_pcb_b/en-mutations.txt" 2>&1; echo "r6b-post: enable mutations exit $?"; grep "^==\|^#\|WRONG" "$R/check_pcb_b/en-mutations.txt"
python3 check_pcb_b_emcon_mutations.py "$G" "$NEW" > "$R/check_pcb_b/emcon-mutations.txt" 2>&1; echo "r6b-post: EMCON mutations exit $?"; grep "^==\|^#" "$R/check_pcb_b/emcon-mutations.txt"
