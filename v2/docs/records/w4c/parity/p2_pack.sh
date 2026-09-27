#!/usr/bin/env bash
# stream w4c pass 2, second half: main's regeneration had rewritten main's own board C files in its scratch clone, so the
# re-take of main's board C refused them (inputs not committed); restore them from the commit, re-take main's C, then pack.
set -uo pipefail
W=/root/w4c
cd $W
git -C $W/main checkout -q -- v2/ecad/pcb-c-display-c8 && git -C $W/main status --short | head -3
rm -rf rt-main/pcb-c-display-c8
(cd $W/main && python3 v2/ecad/tools/retake_schematic_phase.py --run --board c --verdict-dir $W/rt-main --json > $W/rt-main-c.json 2> $W/rt-main-c.log); echo "retake main c exit $?"
tail -3 $W/rt-main-c.log
for t in power_path power_sequence safe_lines; do
  (cd $W/main/v2/ecad/pcb-c-display-c8 && VERDICT_DIR=$W/extra-main python3 $W/main/v2/ecad/tools/$t.py out/pcb-c-display.net > $W/extra-main/$t.log 2>&1); grep -E "^verdict|declares" $W/extra-main/$t.log | cut -c1-170 | sed "s/^/main $t: /"
done
N=""; for d in pcb-a-power-a23/out/pcb-a-power.net pcb-b-compute-b19/out/pcb-b-compute.net pcb-c-display-c8/out/pcb-c-display.net pcb-d-aprs-d9/out/pcb-d-aprs.net pcb-e1-dock-e7/out/pcb-e1-dock.net pcb-p-pack-p2/out/pcb-p-pack.net; do N="$N $W/main/v2/ecad/$d"; done
(cd main/v2/ecad/tools && python3 tx_inhibit.py $N > $W/walk-main.txt 2>&1)
C=cand/v2/ecad/pcb-c-display-c8
rm -rf pack pack.tgz
mkdir -p pack/readings/before-main-91894cd7 pack/readings/after-candidate pack/parity
for L in a b c d; do p=$(basename $(ls -d rt-main/pcb-$L-*)); for f in rt-main/$p/out/*.verdict.json; do cp $f pack/readings/before-main-91894cd7/$L-$(basename $f); done
  for f in rt-cand/$p/out/*.verdict.json; do cp $f pack/readings/after-candidate/$L-$(basename $f); done; done
for t in power_path power_sequence safe_lines; do cp extra-main/$t.verdict.json pack/readings/before-main-91894cd7/c-$t.verdict.json 2>/dev/null; cp extra-cand/$t.verdict.json pack/readings/after-candidate/c-$t.verdict.json 2>/dev/null
  cp extra-main/$t.log pack/readings/before-main-91894cd7/c-$t.log; cp extra-cand/$t.log pack/readings/after-candidate/c-$t.log; done
cp walk-main.txt pack/readings/before-main-91894cd7/walk-tx_inhibit-report.txt; cp walk-cand.txt pack/readings/after-candidate/walk-tx_inhibit-report.txt
python3 fs_levels.py $W/main TX_INHIBIT_n > pack/readings/before-main-91894cd7/fail-safe-states-TX_INHIBIT_n.txt 2>&1
python3 fs_levels.py $W/cand TX_INHIBIT_n > pack/readings/after-candidate/fail-safe-states-TX_INHIBIT_n.txt 2>&1
python3 rt_table.py > pack/readings/retake-table-main-vs-candidate.txt
for s in main cand; do for b in a b c d; do cp rt-$s-$b.log pack/readings/retake-driver-$s-$b.log; done; done
cp w4c-parity-cand.json w4c-parity-cand-vs-pass1.json w3a-netcmp-cand.json intent-diff.json expected-c-netlist.json expected-empty.json netcmp_w4c.py fs_levels.py rt_table.py p2_run.sh p2_pack.sh pack/parity/
cp regen-main/c/regen.json pack/parity/regen-main.json; cp regen-cand/c/regen.json pack/parity/regen-candidate.json
for k in schematic netlist intent bom erc; do cp regen-main/c/parity_$k.json pack/parity/regen-main-parity_$k.json 2>/dev/null; cp regen-cand/c/parity_$k.json pack/parity/regen-candidate-parity_$k.json 2>/dev/null; done
mkdir -p pack/cand-files; cp $C/pcb-c-display.kicad_sch $C/out/pcb-c-display.net $C/out/pcb-c-display.net.prov.json $C/out/pcb-c-display-intent.json pack/cand-files/
grep -A1 "^\*" pack/readings/retake-table-main-vs-candidate.txt | head -60
head -3 pack/readings/after-candidate/fail-safe-states-TX_INHIBIT_n.txt
tar czf pack.tgz pack; echo P2-RUN-DONE
