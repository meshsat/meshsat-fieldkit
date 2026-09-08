#!/usr/bin/env bash
# PCB-D D8 pre-route chain (MESHSAT-830, 7 Sep 2026): footprints, schematic, netlist, mechanical, placement, gate, escapes, joins, fanout, pre-route DRC
set -uo pipefail
cd "$1"; N=pcb-d-aprs
mkdir -p out
for f in ../tools/gen_sch_d.py ../tools/gen_pcb_d.py ../tools/gen_pcb_d3.py ../tools/check_pcb_d.py; do python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" "$f" || { echo "BLOCK compile $f" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }; done   # 8 Sep 2026: the compile pre-check every chain must have (appendix 32.39 lesson)
mkdir -p out; python3 ../tools/gen_footprints_b16.py ../meshsat.pretty > out/gen_fp.log 2>&1 || { echo 'BLOCK footprint generator (out/gen_fp.log)' | tee out/preroute-gate.txt; tail -3 out/gen_fp.log; echo PREROUTE-DONE BLOCK; exit 1; }   # the SA868 footprint lives in the B16 footprint generator
python3 ../tools/gen_sch_d.py $N.kicad_sch $N > out/gen_sch.log 2>&1 || { echo 'BLOCK schematic generator (out/gen_sch.log)' | tee out/preroute-gate.txt; tail -3 out/gen_sch.log; echo PREROUTE-DONE BLOCK; exit 1; }; grep -E 'wrote|single-pin nets' out/gen_sch.log
../tools/build_sch.sh . $N > out/build_sch.log 2>&1; grep -E 'ERC|netlist' out/build_sch.log
[ -s out/$N.net ] || { echo "BLOCK no netlist (out/build_sch.log)" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
rm -f out/$N-erc.status; python3 ../tools/erc_gate.py . $N 2>&1 | tail -6; grep -qE "^(clean|allowed)" out/$N-erc.status 2>/dev/null || { echo "BLOCK ERC (out/$N-erc.json, out/$N-erc.status; allow-list erc-allow.txt with a reason per line)" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/gen_pcb_d.py $N.kicad_pcb > out/gen_pcb_d.log 2>&1; grep -E 'saved|WARN|Trace|Error|note' out/gen_pcb_d.log; grep -q saved out/gen_pcb_d.log || { echo "BLOCK mechanical generator (out/gen_pcb_d.log)" | tee out/preroute-gate.txt; tail -5 out/gen_pcb_d.log; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/gen_pcb_d3.py $N.kicad_pcb out/$N.net > out/gen3.log 2>&1; GEN3=$?; grep -E 'saved|WARN|Trace|Error|overflow|unplaced|missing|SystemExit|zone net|not in the netlist' out/gen3.log
[ "$GEN3" -eq 0 ] || { echo "BLOCK placement generator exit $GEN3" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1   # 8 Sep 2026 (MESHSAT-862): the JLC stackup in the board file, so the impedance read-back reads the project
python3 ../tools/check_pcb_d.py $N.kicad_pcb > out/check_d.log 2>&1; grep -E 'FAIL|RESULT' out/check_d.log; grep -q 'RESULT: ALL PASS' out/check_d.log || { echo 'BLOCK numeric gate (out/check_d.log)' | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
[ -n "${PLACE_JITTER:-}" ] && python3 ../tools/place_jitter.py $N.kicad_pcb "$PLACE_JITTER" 2>&1 | grep place_jitter   # Stage E data campaign: a jittered neighbour of the placement (the gates below still judge it)
python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/join_adjacent_pins.py $N.kicad_pcb 2>&1 | grep -E 'join_adjacent_pins|Traceback|Error'
# only nets with a plane or pour to land on (7 Sep 2026: a pre-placed via of a net without a plane is one more open for the router)
python3 ../tools/prefanout.py $N.kicad_pcb 'GND' fine 2>&1 | grep -E 'fanout:'
# D9 (8 Sep 2026, MESHSAT-862 rule 1, appendix 32.68): every USB pair laid as locked copper on the class's layers before the router; a pair that cannot be laid blocks (PAIR_GATE=0 to route anyway)
PAIR_LAYERS=${PAIR_LAYERS:-F.Cu} python3 ../tools/pair_preroute.py $N.kicad_pcb --classes USB > out/pair_preroute.log 2>&1; PP=$?; grep -E "pair_preroute:" out/pair_preroute.log | grep -v "map " | tail -14; [ "$PP" -eq 0 ] || [ "${PAIR_GATE:-1}" = 0 ] || { echo "BLOCK pair pre-router (out/pair_preroute.log)" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/place_audit.py $N.kicad_pcb --png out/place_audit.png > out/place_audit.log 2>&1; PA=$?; grep -E "FAIL|predicted|decoupling" out/place_audit.log | tail -8; [ "$PA" -eq 0 ] || [ "${PLACE_AUDIT_GATE:-1}" = 0 ] || { echo "BLOCK placement predictor (out/place_audit.log, out/place_audit.png)" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }   # 8 Sep 2026 (MESHSAT-862 Stage D): after the escapes, the fans are measured, not guessed; a collision is a FAIL before any route is bought
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/hardset.py out/$N-preroute-drc.json pre --gate out/preroute-gate.txt --examples 6 | sed 's/^hardset:/pre-route DRC:/'   # 8 Sep 2026 (MESHSAT-862): one hard set for every gate (tools/hardset.py)
python3 ../tools/check_zone_nets.py $N.kicad_pcb > out/zone_nets.log 2>&1; ZN=$?; grep -E "FAIL|zone nets" out/zone_nets.log; [ "$ZN" -eq 0 ] || echo "BLOCK zone-nets (DRC gate said: $(cat out/preroute-gate.txt))" > out/preroute-gate.txt   # 8 Sep 2026 (MESHSAT-862): the grep always matched the summary line, so the old `|| echo BLOCK` never fired
V=$(cat out/preroute-gate.txt); echo PREROUTE-DONE $V; [ "$V" = OK ] || exit 1   # 8 Sep 2026 (MESHSAT-862): a chain run by hand used to exit 0 on its own BLOCK
