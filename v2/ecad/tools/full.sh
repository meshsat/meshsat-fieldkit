#!/usr/bin/env bash
# The pre-route chain, once, for every board (MESHSAT-862, 10 September 2026; plan stage 7, report 1 item 5, report 2 H2/H3).
#
# There were twenty one full_*.sh, most of them clones of one another with a board name changed, and the drift between the
# clones is what let the DRC policy split in two. Everything that differs between boards is in tools/boards/<letter>.json now
# and the sequence lives here. The per-phase entry points (full_b19.sh and friends) stay as three-line wrappers that set PHASE
# and call this, so nothing that names them breaks.
#
# Usage: full.sh <project dir> <letter>      PHASE, PAIR_*, PLACE_*, ESCAPE_* from the environment as before.
set -uo pipefail
D="$1"; L="$2"
T="$(cd "$(dirname "$0")" && pwd)"
CFG="$T/boards/$L.json"
[ -s "$CFG" ] || { echo "full.sh: no board file $CFG"; exit 2; }
cfg () { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); v=d.get(sys.argv[2]); print('' if v is None else (' '.join(v) if isinstance(v,list) else ('1' if v is True else ('' if v is False else v))))" "$CFG" "$1"; }
cfg_env () { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(' '.join('%s=%s'%(k,v) for k,v in (d.get('escape_env') or {}).items()))" "$CFG"; }

N="$(cfg name)"; FPGEN="$(cfg footprint_generator)"; EXTRA="$(cfg extra_compile)"
GATE1="$(cfg gate_before_placement)"; BPAFTER="$(cfg bypass_place_after)"
PCLS="$(cfg pair_classes)"; PLAY="$(cfg pair_layers)"; PHOP="$(cfg pair_hop_layers)"; PTAIL="$(cfg pair_tail)"
FANOUT="$(cfg fanout_nets)"; EPRUNE="$(cfg escape_prune_before_audit)"; ESCENV="$(cfg_env)"
cd "$D" || exit 2
mkdir -p out
block () { echo "BLOCK $1" | tee out/preroute-gate.txt >/dev/null; echo "BLOCK $1"; [ -n "${2:-}" ] && tail -5 "$2"; echo PREROUTE-DONE BLOCK; exit 1; }

# The compile pre-check every chain must have: a comment appended to a generator line has swallowed a comma twice, and a
# generator that will not parse used to be found by the placement generator building on the PREVIOUS board (appendix 32.39).
for f in ${FPGEN:+../tools/$FPGEN} ../tools/gen_sch_$L.py ../tools/gen_pcb_$L.py ../tools/gen_pcb_${L}3.py ../tools/check_pcb_$L.py $(for e in $EXTRA; do echo ../tools/$e; done); do
  python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" "$f" || block "compile $f"
done

if [ -n "$FPGEN" ]; then
  python3 "../tools/$FPGEN" ../meshsat.pretty > out/gen_fp.log 2>&1 || block "footprint generator (out/gen_fp.log)" out/gen_fp.log
  grep gen_footprints out/gen_fp.log | cut -c1-120
fi
python3 ../tools/gen_sch_$L.py $N.kicad_sch $N > out/gen_sch.log 2>&1 || block "schematic generator (out/gen_sch.log)" out/gen_sch.log
grep -E 'wrote|single-pin nets' out/gen_sch.log
../tools/build_sch.sh . $N > out/build_sch.log 2>&1; grep -E 'ERC|netlist' out/build_sch.log
[ -s out/$N.net ] || block "no netlist (out/build_sch.log)" out/build_sch.log
rm -f out/$N-erc.status; python3 ../tools/erc_gate.py . $N 2>&1 | tail -6
grep -qE "^(clean|allowed)" out/$N-erc.status 2>/dev/null || block "ERC (out/$N-erc.json, out/$N-erc.status; allow-list erc-allow.txt with a reason per line)"

python3 ../tools/gen_pcb_$L.py $N.kicad_pcb > out/gen_pcb_$L.log 2>&1; grep -E 'saved|WARN|Trace|Error|note|not found' out/gen_pcb_$L.log
grep -q saved out/gen_pcb_$L.log || block "mechanical generator (out/gen_pcb_$L.log)" out/gen_pcb_$L.log
# Phase two of the decoupling placement (owner ruling 9 Sep 2026, 32.74 option 3). The A and B lineages run it before the
# packer because their pockets are laid out by hand; the others after the stackup, which is where their clones had it.
[ "$BPAFTER" = mechanical ] && python3 ../tools/bypass_place.py $N.kicad_pcb 2>&1 | grep -E "bypass_place" | tail -8
[ -n "$GATE1" ] && { python3 ../tools/check_pcb_$L.py $N.kicad_pcb > out/check_${L}1.log 2>&1; grep -E 'FAIL|RESULT' out/check_${L}1.log; }

python3 ../tools/gen_pcb_${L}3.py $N.kicad_pcb out/$N.net > out/gen3.log 2>&1; GEN3=$?
grep -E 'saved|WARN|Trace|Error|overflow|unplaced|missing|SystemExit|zone net|not in the netlist|footprint missing' out/gen3.log
[ "$GEN3" -eq 0 ] || block "placement generator exit $GEN3"
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1   # the JLC stackup in the board file, so the impedance read-back reads the project
[ "$BPAFTER" = stackup ] && python3 ../tools/bypass_place.py $N.kicad_pcb 2>&1 | grep -E "bypass_place" | tail -8
python3 ../tools/check_pcb_$L.py $N.kicad_pcb > out/check_$L.log 2>&1; grep -E 'FAIL|RESULT' out/check_$L.log
grep -q 'RESULT: ALL PASS' out/check_$L.log || block "numeric gate (out/check_$L.log)"

[ -n "${PLACE_JITTER:-}" ] && python3 ../tools/place_jitter.py $N.kicad_pcb "$PLACE_JITTER" 2>&1 | grep place_jitter   # Stage E data campaign
env $ESCENV python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/join_adjacent_pins.py $N.kicad_pcb 2>&1 | grep -E 'join_adjacent_pins|Traceback|Error'

if [ -n "$PCLS" ]; then
  # The placed board with its escapes and BEFORE any pair copper: the only honest input for a pre-router measurement
  # (10 Sep 2026; the -preroute copy is taken after the pre-router and carried the previous pass's 4,969 mm of pair copper).
  cp $N.kicad_pcb out/$N-placed.kicad_pcb
  [ "${PREROUTE_STOP_AFTER_PLACE:-0}" = 1 ] && { echo "PREROUTE-DONE PLACED (out/$N-placed.kicad_pcb)"; exit 0; }
  # THE PAIRS CLAIM THEIR COPPER BEFORE THE FANOUT (9 Sep 2026, D10, appendix 32.83): prefanout reads laid copper as an
  # obstacle and fits around the corridors, while the pre-router has no such freedom.
  PAIR_LAYERS=${PAIR_LAYERS:-$PLAY} PAIR_HOP_LAYERS=${PAIR_HOP_LAYERS:-$PHOP} python3 ../tools/pair_preroute.py $N.kicad_pcb --classes "$PCLS" > out/pair_preroute.log 2>&1; PP=$?
  grep -E "pair_preroute:" out/pair_preroute.log | grep -v "map " | tail -"$PTAIL"
  [ "$PP" -eq 0 ] || [ "${PAIR_GATE:-1}" = 0 ] || block "pair pre-router (out/pair_preroute.log)"
fi

python3 ../tools/prefanout.py $N.kicad_pcb "$FANOUT" fine 2>&1 | grep -E 'fanout:'   # only nets with a plane or pour to land on
if [ -n "$EPRUNE" ]; then
  kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
  python3 ../tools/escape_prune.py $N.kicad_pcb out/$N-preroute-drc.json 2>&1 | grep escape_prune
fi
env $ESCENV python3 ../tools/place_audit.py $N.kicad_pcb --png out/place_audit.png > out/place_audit.log 2>&1; PA=$?
grep -E "FAIL|predicted|decoupling" out/place_audit.log | tail -8
[ "$PA" -eq 0 ] || [ "${PLACE_AUDIT_GATE:-1}" = 0 ] || block "placement predictor (out/place_audit.log, out/place_audit.png)"

cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/hardset.py out/$N-preroute-drc.json pre --gate out/preroute-gate.txt --examples 6 | sed 's/^hardset:/pre-route DRC:/'
python3 ../tools/check_zone_nets.py $N.kicad_pcb > out/zone_nets.log 2>&1; ZN=$?; grep -E "FAIL|zone nets" out/zone_nets.log
[ "$ZN" -eq 0 ] || echo "BLOCK zone-nets (DRC gate said: $(cat out/preroute-gate.txt))" > out/preroute-gate.txt
V=$(cat out/preroute-gate.txt); echo PREROUTE-DONE $V; [ "$V" = OK ] || exit 1   # a chain run by hand used to exit 0 on its own BLOCK
