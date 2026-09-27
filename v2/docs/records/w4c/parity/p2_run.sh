#!/usr/bin/env bash
# stream w4c pass 2 (W4C-F5, +3V3 covers EPD_VCC): regenerate board C from main 91894cd7 plus the pass-2 generator, compare
# with main and with the pass-1 candidate, and re-take the schematic-phase readings of boards C, A, B and D in scratch.
# Box scratch only (/root/w4c); never /root/gitlab.
set -uo pipefail
W=/root/w4c
cd $W
rm -rf main cand regen-main regen-cand rt-main rt-cand pack pack.tgz extra-main
# a plain clone READS the box's tree (never written); the bundle adds 82dd1e4d..91894cd7
git clone -q --no-hardlinks /root/gitlab/products/meshsat/meshsat-fieldkit main || exit 3
( cd main && git fetch -q $W/main-91894cd7.bundle refs/heads/fnd/w4c && git checkout -q 91894cd7 && git log --oneline -1 ) || exit 4
cp main/v2/ecad/pcb-c-display-c8/out/pcb-c-display.net committed-main.net
cp main/v2/ecad/pcb-c-display-c8/out/pcb-c-display-intent.json committed-main-intent.json
# main's own regeneration (parity of main's chain against main's committed files)
( cd main && python3 v2/ecad/tools/handover_exports.py regen --letters c --out $W/regen-main 2>&1 | tail -1 )
git clone -q main cand && cd cand && git checkout -q -b w4c-cand 91894cd7 && git apply $W/w4c-p2.patch || exit 2
sha256sum v2/ecad/tools/gen_sch_c.py v2/ecad/tools/boards/c.json | cut -c1-16
python3 v2/ecad/tools/handover_exports.py regen --letters c --out $W/regen-cand 2>&1 | tail -1
cd $W
C=cand/v2/ecad/pcb-c-display-c8
sha256sum $C/pcb-c-display.kicad_sch $C/out/pcb-c-display.net $C/out/pcb-c-display.net.prov.json $C/out/pcb-c-display-intent.json | sed 's/^\(.\{16\}\)[^ ]*/\1/'
echo "--- pass-1 candidate files"; sha256sum prev-cand/* | sed 's/^\(.\{16\}\)[^ ]*/\1/'
for f in pcb-c-display.kicad_sch out/pcb-c-display.net; do cmp -s $C/$f prev-cand/$(basename $f) && echo "IDENTICAL to pass 1: $f" || echo "DIFFERS from pass 1: $f"; done
python3 netcmp_w4c.py committed-main.net $C/out/pcb-c-display.net expected-c-netlist.json > w4c-parity-cand.json
python3 netcmp_w4c.py prev-cand/pcb-c-display.net $C/out/pcb-c-display.net expected-empty.json > w4c-parity-cand-vs-pass1.json
python3 netcmp.py committed-main.net $C/out/pcb-c-display.net > w3a-netcmp-cand.json
python3 -c "import json; d=json.load(open('w4c-parity-cand.json')); print('netcmp_w4c vs main', d['expected_change_list']['result'], d['counts'])"
python3 -c "import json; d=json.load(open('w4c-parity-cand-vs-pass1.json')); print('netcmp_w4c vs pass 1', d['expected_change_list']['result'], d['counts'])"
# the intent against main's and against pass 1's
python3 - <<'PY' > intent-diff.json
import json
def diff(a, b):
    out = {}
    for k in sorted(set(a) | set(b)):
        if k == "written" or a.get(k) == b.get(k): continue
        if isinstance(a.get(k), dict) and isinstance(b.get(k), dict):
            out[k] = {"added": sorted(set(b[k]) - set(a[k])), "removed": sorted(set(a[k]) - set(b[k])),
                      "changed": {x: [a[k][x], b[k][x]] for x in sorted(set(a[k]) & set(b[k])) if a[k][x] != b[k][x]}}
        else: out[k] = "changed"
    return out
m = json.load(open("committed-main-intent.json")); p = json.load(open("prev-cand/pcb-c-display-intent.json"))
c = json.load(open("cand/v2/ecad/pcb-c-display-c8/out/pcb-c-display-intent.json"))
print(json.dumps({"candidate_vs_main_91894cd7": diff(m, c), "candidate_vs_pass1_candidate": diff(p, c)}, indent=1))
PY
python3 -c "
import json; d=json.load(open('intent-diff.json'))['candidate_vs_pass1_candidate']
for k,v in d.items():
    print('intent vs pass 1:', k, {x:(y if not isinstance(y,dict) else sorted(y)) for x,y in (v.items() if isinstance(v,dict) else [('all',v)])})
r=json.load(open('cand/v2/ecad/pcb-c-display-c8/out/pcb-c-display-intent.json'))['rails']['+3V3']; print('+3V3', r['amps_typ'], r['amps_peak'])"
cd cand && git add -A v2/ecad/tools/gen_sch_c.py v2/ecad/tools/boards/c.json v2/ecad/pcb-c-display-c8 && git -c user.name=w4c-scratch -c user.email=scratch@invalid commit -q -m "scratch: w4c pass 2 candidate (throwaway clone on the box, never pushed)"
cd $W/main && git -c user.name=w4c-scratch -c user.email=scratch@invalid checkout -q -b w4c-main 2>/dev/null; cd $W
for s in main cand; do for b in c a b d; do
  (cd $W/$s && python3 v2/ecad/tools/retake_schematic_phase.py --run --board $b --verdict-dir $W/rt-$s --json > $W/rt-$s-$b.json 2> $W/rt-$s-$b.log); echo "retake $s $b exit $?"
done; done
for s in main cand; do
  mkdir -p $W/extra-$s
  for t in power_path power_sequence safe_lines; do
    (cd $W/$s/v2/ecad/pcb-c-display-c8 && VERDICT_DIR=$W/extra-$s python3 $W/$s/v2/ecad/tools/$t.py out/pcb-c-display.net > $W/extra-$s/$t.log 2>&1); grep -E "^verdict|declares" $W/extra-$s/$t.log | cut -c1-170 | sed "s/^/$s $t: /"
  done
done
N=""; for d in pcb-a-power-a23/out/pcb-a-power.net pcb-b-compute-b19/out/pcb-b-compute.net pcb-c-display-c8/out/pcb-c-display.net pcb-d-aprs-d9/out/pcb-d-aprs.net pcb-e1-dock-e7/out/pcb-e1-dock.net pcb-p-pack-p2/out/pcb-p-pack.net; do N="$N $W/cand/v2/ecad/$d"; done
(cd cand/v2/ecad/tools && python3 tx_inhibit.py $N > $W/walk-cand.txt 2>&1)
N=""; for d in pcb-a-power-a23/out/pcb-a-power.net pcb-b-compute-b19/out/pcb-b-compute.net pcb-c-display-c8/out/pcb-c-display.net pcb-d-aprs-d9/out/pcb-d-aprs.net pcb-e1-dock-e7/out/pcb-e1-dock.net pcb-p-pack-p2/out/pcb-p-pack.net; do N="$N $W/main/v2/ecad/$d"; done
(cd main/v2/ecad/tools && python3 tx_inhibit.py $N > $W/walk-main.txt 2>&1)
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
cp w4c-parity-cand.json w4c-parity-cand-vs-pass1.json w3a-netcmp-cand.json intent-diff.json expected-c-netlist.json expected-empty.json netcmp_w4c.py fs_levels.py rt_table.py p2_run.sh pack/parity/
cp regen-main/c/regen.json pack/parity/regen-main.json; cp regen-cand/c/regen.json pack/parity/regen-candidate.json
for k in schematic netlist intent bom erc; do cp regen-main/c/parity_$k.json pack/parity/regen-main-parity_$k.json 2>/dev/null; cp regen-cand/c/parity_$k.json pack/parity/regen-candidate-parity_$k.json 2>/dev/null; done
mkdir -p pack/cand-files; cp $C/pcb-c-display.kicad_sch $C/out/pcb-c-display.net $C/out/pcb-c-display.net.prov.json $C/out/pcb-c-display-intent.json pack/cand-files/
grep -A1 "^\*" pack/readings/retake-table-main-vs-candidate.txt | head -60
head -3 pack/readings/after-candidate/fail-safe-states-TX_INHIBIT_n.txt
tar czf pack.tgz pack; echo P2-RUN-DONE
