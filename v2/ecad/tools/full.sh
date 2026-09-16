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
cfg_env () { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(' '.join('%s=%s'%(k,v) for k,v in (d.get(sys.argv[2]) or {}).items()))" "$CFG" "${1:-escape_env}"; }

N="$(cfg name)"; FPGEN="$(cfg footprint_generator)"; EXTRA="$(cfg extra_compile)"
# The phase the silk carries. It lived as a DEFAULT inside each generator (gen_pcb_c.py said C9 while C's
# deliverable is C10) and only one of the six wrappers set it, so a board could be routed for hours and then have
# its deliverable refused for naming another phase, which is what `verify_deliverable` checks and what A24's A18
# silk was (12 September 2026). A caller's own PHASE still wins, which is how an older phase is rebuilt.
export PHASE="${PHASE:-$(cfg phase)}"
[ -n "$PHASE" ] && echo "full.sh: phase $PHASE"
GATE1="$(cfg gate_before_placement)"; BPAFTER="$(cfg bypass_place_after)"
PCLS="$(cfg pair_classes)"; PLAY="$(cfg pair_layers)"; PHOP="$(cfg pair_hop_layers)"; PTAIL="$(cfg pair_tail)"
FANOUT="$(cfg fanout_nets)"; EPRUNE="$(cfg escape_prune_before_audit)"; ESCENV="$(cfg_env escape_env)"
# 12 September 2026: the placement's own environment, the way `escape_env` has always worked. B declares
# PLACE_COUPLE_GAP here with the two placements that measured it (appendix 32.147: 14 of 48 pairs at the packer's
# own gap, 22 at twice it). A caller's own value still wins, which is how the next arm measures it.
PLACEENV="$(cfg_env place_env)"
for _kv in $PLACEENV; do _k="${_kv%%=*}"; [ -n "${!_k:-}" ] || export "$_k"="${_kv#*=}"; done   # a caller's own value wins
[ -n "$PLACEENV" ] && echo "full.sh: placement environment $PLACEENV"
# One line per pair pass, tab separated: classes, layers, hop layers, inner geometry. Empty when the board runs one pass.
PPASSES="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(chr(10).join(chr(9).join((p.get(k) or '') for k in ('classes','layers','hop_layers','inner')) for p in (d.get('pair_passes') or [])))" "$CFG")"
# A board may declare the pair environment it was measured best at (boards/<letter>.json `pair_env`). It never
# overrides what the caller set: an arm has to be able to vary the very thing the board declares, or the next
# sweep measures the declaration instead of the knob (11 September 2026).
PENV="$(python3 -c "import json,sys,os; d=json.load(open(sys.argv[1])).get('pair_env') or {}; print(' '.join('%s=%s' % (k, v) for k, v in d.items() if not os.environ.get(k)))" "$CFG")"
[ -n "$PENV" ] && echo "pair environment declared by the board: $PENV"
# The same for the GENERATORS (`gen_env`), which is where a board declares a land pattern or any other choice it
# was measured best at: IDC_PADS is the first (12 September 2026, the 2.54 mm IDC channel; `idc_pads.py` carries
# the numbers). A caller's own value wins here too, so an arm can vary what the board declares.
GENV="$(python3 -c "import json,sys,os; d=json.load(open(sys.argv[1])).get('gen_env') or {}; print(' '.join('%s=%s' % (k, v) for k, v in d.items() if not os.environ.get(k)))" "$CFG")"
[ -n "$GENV" ] && echo "generator environment declared by the board: $GENV"
cd "$D" || exit 2
mkdir -p out
block () { echo "BLOCK $1" | tee out/preroute-gate.txt >/dev/null; echo "BLOCK $1"; [ -n "${2:-}" ] && tail -5 "$2"; echo PREROUTE-DONE BLOCK; exit 1; }

# The compile pre-check every chain must have: a comment appended to a generator line has swallowed a comma twice, and a
# generator that will not parse used to be found by the placement generator building on the PREVIOUS board (appendix 32.39).
FPGENS=""; for g in $FPGEN; do FPGENS="$FPGENS ../tools/$g"; done   # a board may declare more than one (12 September 2026: the IDC lands beside the board's own footprints)
for f in $FPGENS ../tools/gen_sch_$L.py ../tools/gen_pcb_$L.py ../tools/gen_pcb_${L}3.py ../tools/check_pcb_$L.py $(for e in $EXTRA; do echo ../tools/$e; done); do
  python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" "$f" || block "compile $f"
  # Compiling is not enough: a comment appended mid-line swallows the calls after it and the file
  # still compiles, so the part simply stops existing. 11 Sep 2026, twice in one session.
  python3 ../tools/tests/test_swallowed_calls.py "$f" > /dev/null 2>&1 || { python3 ../tools/tests/test_swallowed_calls.py "$f"; block "a comment swallows calls in $f"; }
done

if [ -n "$FPGEN" ]; then
  : > out/gen_fp.log
  for g in $FPGEN; do python3 "../tools/$g" ../meshsat.pretty >> out/gen_fp.log 2>&1 || block "footprint generator $g (out/gen_fp.log)" out/gen_fp.log; done
  grep gen_footprints out/gen_fp.log | cut -c1-120
fi
env $GENV python3 ../tools/gen_sch_$L.py $N.kicad_sch $N > out/gen_sch.log 2>&1 || block "schematic generator (out/gen_sch.log)" out/gen_sch.log
grep -E 'wrote|single-pin nets' out/gen_sch.log
# The netlist is an OUTPUT, not a file that happens to be there (10 September 2026; round-two red teams, report 1 P1). This
# did not check build_sch.sh's status and did not delete the old netlist first, so a failed export with yesterday's netlist on
# disk let the whole chain place a board from stale connectivity. Centralising the chains made one correction protect six boards.
rm -f out/$N.net
../tools/build_sch.sh . $N > out/build_sch.log 2>&1; BSCH=$?; grep -E 'ERC|netlist' out/build_sch.log
[ "$BSCH" -eq 0 ] || block "the schematic build exited $BSCH (out/build_sch.log)" out/build_sch.log
[ -s out/$N.net ] || block "no netlist (out/build_sch.log)" out/build_sch.log
rm -f out/$N-erc.status out/erc_gate.verdict.json
python3 ../tools/erc_gate.py . $N > out/erc_gate.log 2>&1; ERCG=$?; tail -6 out/erc_gate.log
# 11 Sep 2026 (MESHSAT-862, stage 0a): the gate's own exit code decides, not a grep of a status file it also writes.
# 3 is INCONCLUSIVE (no ERC output at all) and blocks exactly like 1, which the status-file grep also did but silently.
[ "$ERCG" -eq 0 ] || block "ERC (out/$N-erc.json, out/erc_gate.verdict.json; allow-list erc-allow.txt with a reason per line)" out/erc_gate.log
# The netlist-level review: decoupling, floating control pins, ESD on the USB pairs, the I2C address map, connector mates.
# It has existed since the early phases and no chain ever ran it (report 2 L2). It reports and never blocks, because it reads
# intent that the board gates read from the intent file; what it is for is the class of mistake no numeric gate looks for.
python3 ../tools/review_nets.py out/$N.net 2>&1 | grep -E "^(==|I2C|issues|  )" | tail -12

python3 ../tools/gen_pcb_$L.py $N.kicad_pcb > out/gen_pcb_$L.log 2>&1; grep -E 'saved|WARN|Trace|Error|note|not found' out/gen_pcb_$L.log
grep -q saved out/gen_pcb_$L.log || block "mechanical generator (out/gen_pcb_$L.log)" out/gen_pcb_$L.log
# Phase two of the decoupling placement (owner ruling 9 Sep 2026, 32.74 option 3). The A and B lineages run it before the
# packer because their pockets are laid out by hand; the others after the stackup, which is where their clones had it.
[ "$BPAFTER" = mechanical ] && python3 ../tools/bypass_place.py $N.kicad_pcb 2>&1 | grep -E "bypass_place" | tail -8
[ -n "$GATE1" ] && { python3 ../tools/check_pcb_$L.py $N.kicad_pcb > out/check_${L}1.log 2>&1; grep -E 'FAIL|RESULT' out/check_${L}1.log; }

python3 ../tools/gen_pcb_${L}3.py $N.kicad_pcb out/$N.net > out/gen3.log 2>&1; GEN3=$?
grep -E 'saved|WARN|Trace|Error|overflow|unplaced|missing|SystemExit|zone net|not in the netlist|footprint missing' out/gen3.log
python3 ../tools/jumper_clearance.py $N.kicad_pcb 2>&1 | grep -E 'jumper_clearance'   # a solder jumper's zero pad clearance would be handed to the router (D12, 15 Sep 2026)
python3 ../tools/class_floor.py $N.kicad_pcb > out/class_floor.log 2>&1; CF=$?
grep -E 'class_floor:|FAIL' out/class_floor.log
[ "$CF" -eq 0 ] || block "a net class is below the board's own minimum (rule IMP-002, out/class_floor.log)" out/class_floor.log
[ "$GEN3" -eq 0 ] || block "placement generator exit $GEN3"
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1   # the JLC stackup in the board file, so the impedance read-back reads the project
[ "$BPAFTER" = stackup ] && python3 ../tools/bypass_place.py $N.kicad_pcb 2>&1 | grep -E "bypass_place" | tail -8
rm -f out/check_pcb_$L.verdict.json
python3 ../tools/check_pcb_$L.py $N.kicad_pcb > out/check_$L.log 2>&1; GATE=$?; grep -E 'FAIL|RESULT|^verdict:' out/check_$L.log
[ "$GATE" -eq 0 ] || block "numeric gate: $(python3 ../tools/verdict.py read out/check_pcb_$L.verdict.json 2>&1 | tail -1)" out/check_$L.log
# The board against the netlist it was just placed from (round-two M4, 11 Sep 2026). Nothing compared the two,
# so a board placed from a STALE netlist passed every gate, and this chain has produced exactly that twice.
python3 ../tools/netlist_board.py $N.kicad_pcb out/$N.net > out/netlist_board.log 2>&1; NB=$?; tail -3 out/netlist_board.log
[ "$NB" -eq 0 ] || block "the board does not match its netlist: $(python3 ../tools/verdict.py read out/netlist_board.verdict.json 2>&1 | tail -1)" out/netlist_board.log
# RULE CMP-001: a part's own rating against the rail it is soldered to. It runs HERE, on the netlist, because
# it needs no copper and a part rated below its rail is a schematic defect: catching it after a route is a
# re-route. Board A shipped twenty-five 50 V capacitors on a 54 V output and a person found them by reading a
# value string while doing something else (12 September 2026).
python3 ../tools/derate.py out/$N.net > out/derate.log 2>&1; DR=$?; grep -E 'derate:|FAIL|UNDECLARED' out/derate.log | head -8
[ "$DR" -eq 1 ] && block "a part is rated below the rail it sits on (rule CMP-001, out/derate.log)" out/derate.log

[ -n "${PLACE_JITTER:-}" ] && python3 ../tools/place_jitter.py $N.kicad_pcb "$PLACE_JITTER" 2>&1 | grep place_jitter   # Stage E data campaign
env $ESCENV python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/join_adjacent_pins.py $N.kicad_pcb 2>&1 | grep -E 'join_adjacent_pins|Traceback|Error'

# The placed board with its escapes and BEFORE any pair copper: the only honest input for a pre-router measurement
# (10 Sep 2026; the -preroute copy is taken after the pre-router and carried the previous pass's 4,969 mm of pair copper).
# Both of these lines sat INSIDE the "does this board have pairs" test until 11 September 2026, so E and P wrote no placed
# board at all and PREROUTE_STOP_AFTER_PLACE=1 silently ran their whole chain instead of stopping. A flag that does nothing
# on two of six boards and says nothing about it is the shape stage 0 exists to remove; the snapshot is one file copy.
cp $N.kicad_pcb out/$N-placed.kicad_pcb

# THE CHEAP GATE RUNS BEFORE THE EXPENSIVE STAGE (12 September 2026, red team round three C2). The first DRC
# of the placed board used to be at the far side of the pair passes, which are about nineteen minutes on B,
# and only on the branch the pair gate takes when it refuses. So B's whole pair programme, every arm in
# arms/, was measured on a placement carrying 150 hard violations that nothing had read (appendix 32.149). A
# one-minute DRC belongs in front of a nineteen-minute pass, and a board that is already illegal is not a
# board to measure a pre-router on. The allowance is ZERO unless the board declares one with its number and
# the appendix section that measured it (`placed_hard_allowance` in boards/<letter>.json).
PLACED_ALLOW="$(cfg placed_hard_allowance)"; PLACED_ALLOW="${PLACED_ALLOW:-0}"
# A DRC THAT DID NOT RUN IS NOT A CLEAN BOARD (16 September 2026, red team report 1 P1: this line swallowed
# drc.sh's exit status with `|| true` and the branch below then printed "UNMEASURED" and carried on into a
# five-hour route. A cheap gate that fails open is not a gate; the subprocess's failure is the chain's.)
rm -f out/$N-placed-drc.json out/placed-counts.txt
bash ../tools/drc.sh $N.kicad_pcb out/$N-placed-drc.json >/dev/null 2>&1; DRCRC=$?
[ "$DRCRC" -eq 0 ] || block "the placed-board DRC did not run (drc.sh exit $DRCRC): its legality is UNMEASURED and the route below is not a measurement"
[ -s "out/$N-placed-drc.json" ] || block "the placed-board DRC wrote no report: its legality is UNMEASURED"
if [ -s "out/$N-placed-drc.json" ]; then
  python3 ../tools/hardset.py out/$N-placed-drc.json pre --counts out/placed-counts.txt --label placed >/dev/null 2>&1; HSRC=$?
  [ "$HSRC" -eq 0 ] || block "hardset could not read the placed-board DRC report (exit $HSRC)"
  [ -s out/placed-counts.txt ] || block "hardset wrote no counts for the placed board"
  PLACED_HARD="$(cut -d' ' -f1 out/placed-counts.txt 2>/dev/null || echo 0)"
  echo "placed board: hard $PLACED_HARD of the fifteen types, allowance $PLACED_ALLOW"
  if [ "${PLACED_HARD:-0}" -gt "$PLACED_ALLOW" ]; then
    echo "BLOCK the placed board carries $PLACED_HARD hard violation(s) against an allowance of $PLACED_ALLOW."
    echo "      Nothing measured on it is a measurement of the pre-router: fix the placement, or declare the"
    echo "      allowance in boards/<letter>.json as placed_hard_allowance with its number and its section."
    echo "      The hard set is in out/$N-placed-drc.json and out/hardset-placed.verdict.json."
    exit 1
  fi
else
  block "the placed-board DRC report is empty: the board's legality is UNMEASURED and nothing below it is a measurement"
fi

[ "${PREROUTE_STOP_AFTER_PLACE:-0}" = 1 ] && { echo "PREROUTE-DONE PLACED (out/$N-placed.kicad_pcb)"; exit 0; }

if [ -n "$PCLS" ] || [ -n "$PPASSES" ]; then
  # THE PAIRS CLAIM THEIR COPPER BEFORE THE FANOUT (9 Sep 2026, D10, appendix 32.83): prefanout reads laid copper as an
  # obstacle and fits around the corridors, while the pre-router has no such freedom.
  #
  # A BOARD MAY NEED MORE THAN ONE PASS, WITH A DIFFERENT LAYER SET PER CLASS (10 September 2026, appendix 32.103; round-two
  # red team H3). B19's two pair classes do not want the same layers: the 100 ohm class hits its target on In2 and In3 with a
  # NARROWER gap than it uses outside, and the 90 ohm class does not, so the first takes four layers and the second takes two.
  # The pre-router has no per-class layer list and does not need one: the second pass reads the first pass's locked copper as
  # an obstacle, so a list of passes in the board file is the per-class layer set. Measured: 23 + 37 = 60 of 113 in that
  # order, 39 + 17 = 56 in the other, against 56 for one pass on two layers. The class that gains the layers goes first.
  # This lived in a session driver until now, so the chain laid 56 and any floor-plan work would have been measured against
  # the wrong baseline.
  # A board may name the order its pairs are laid in (`pair_order` in boards/<letter>.json). The pass is greedy
  # and never rips up, so whichever pair goes first takes the room, and "longest first" is the wrong rule where
  # one pair has far less freedom than the others: A's three ribbon pairs went 2 of 3 to 3 of 3 when the one on
  # an INNER row of the header, which can only leave through the channel between the columns, was laid before
  # the two on the end rows, which have the open board in front of them (12 September 2026, appendix 32.134).
  PORD="$(python3 -c "import json,sys; print('\n'.join(json.load(open(sys.argv[1])).get('pair_order') or []))" "$CFG")"
  if [ -n "$PORD" ]; then printf '%s\n' "$PORD" > out/pair-order.txt; PENV="$PENV PAIR_ORDER_FILE=$PWD/out/pair-order.txt"; echo "pair order: $(printf '%s' "$PORD" | tr '\n' ' ')first in the list, then the longest of the rest"; fi
  PP=0; PIDX=0
  if [ -n "$PPASSES" ]; then
    while IFS=$'\t' read -r pcls play phop pinner; do
      [ -z "$pcls" ] && continue
      PIDX=$((PIDX + 1))
      echo "pair pass $PIDX: classes $pcls on ${play:-$PLAY}${pinner:+ , inner $pinner}"
      env $PENV PAIR_LAYERS="${play:-$PLAY}" PAIR_HOP_LAYERS="${phop:-$PHOP}" PAIR_INNER="$pinner"         python3 ../tools/pair_preroute.py $N.kicad_pcb --classes "$pcls" > out/pair_preroute-$PIDX.log 2>&1; rc=$?
      [ "$rc" -eq 0 ] || PP=$rc
      grep -E "pair_preroute:" out/pair_preroute-$PIDX.log | grep -v "map " | tail -"$PTAIL"
    done <<< "$PPASSES"
    cat out/pair_preroute-*.log > out/pair_preroute.log
  else
    env $PENV PAIR_LAYERS=${PAIR_LAYERS:-$PLAY} PAIR_HOP_LAYERS=${PAIR_HOP_LAYERS:-$PHOP} python3 ../tools/pair_preroute.py $N.kicad_pcb --classes "$PCLS" > out/pair_preroute.log 2>&1; PP=$?
    grep -E "pair_preroute:" out/pair_preroute.log | grep -v "map " | tail -"$PTAIL"
  fi
  echo "pair pre-router: $(grep -h "pairs laid," out/pair_preroute*.log | sed 's/^pair_preroute: //' | paste -sd'; ')"
  # 15 September 2026: the pair copper is put to the DRC HERE, on every board, and a pair the DRC refuses comes off
  # whole before the fanout and the escapes are laid around it (pair_prune.py). B19's pre-route board carried 64 hard
  # items of the pre-router's own making and would have routed six hours towards a refused finish. A pruned pair
  # holds a board that declares no coupled fraction, exactly as an unlaid one does.
  ../tools/drc.sh $N.kicad_pcb out/$N-pairs-drc.json >/dev/null 2>&1 || true
  if [ -s out/$N-pairs-drc.json ]; then
    VERDICT_ADVISORY=1 python3 ../tools/hardset.py out/$N-pairs-drc.json pre --examples 4 --label 'pre-route DRC on the pair copper' | sed 's/^hardset:/pre-route DRC (pair copper):/' || true   # a measurement: the prune acts on it, the chain's own DRC below decides
    python3 ../tools/pair_prune.py $N.kicad_pcb out/$N-pairs-drc.json 2>&1 | grep -E "pair_prune|Traceback|Error"; PRUNE=${PIPESTATUS[0]}
    [ "$PRUNE" -ne 2 ] || [ "$PP" -ne 0 ] || PP=2
  fi
  # 12 September 2026: the DRC before the block, not after it. A board that fails the pair gate stopped here, so
  # the copper the pre-router DID lay was never put to a DRC at all: B19 has laid pairs since 9 September and has
  # never once been asked whether they are legal, which is how A's shorting fan survived a night. The gate still
  # blocks; what changes is that the evidence exists when it does.
  if [ "$PP" -ne 0 ] && [ "${PAIR_GATE:-1}" != 0 ]; then
    ../tools/drc.sh $N.kicad_pcb out/$N-preroute-drc.json >/dev/null 2>&1 || true
    [ -s out/$N-preroute-drc.json ] && VERDICT_ADVISORY=1 python3 ../tools/hardset.py out/$N-preroute-drc.json pre --examples 4 --label 'pre-route DRC on the refused board' | sed 's/^hardset:/pre-route DRC (refused board):/' || true
  fi
  # 15 September 2026, owner ruling 02:40 CEST (decision 24 delegated to the session, option 2 taken): a board that
  # declares pair_coupled_fraction is held only while the pre-router lays FEWER than that fraction of its pairs;
  # the impedance gate judges the coupled length on the routed board against the same number. A board that
  # declares nothing is held until every pair is laid, the 10 September rule.
  PCF="$(cfg pair_coupled_fraction)"
  if [ "$PP" -ne 0 ] && [ -n "$PCF" ]; then
    # The ruling's number is a LENGTH fraction on the routed board, which only impedance_check can measure; a
    # count of pairs laid before the route is not that number (62 of 113 pairs is 55 percent by count and
    # nobody has measured what it is by length). So a board that declares the fraction is not held here at
    # all: it routes, and the impedance gate judges the copper that was laid. What is printed is the count,
    # for the record, beside the bar it is NOT compared with.
    echo "pair gate: $(grep -h "pairs laid," out/pair_preroute*.log | sed 's/^pair_preroute: //' | paste -sd'; ') on a board that declares a coupled fraction of $PCF; the routed board's impedance gate judges it by length, so the chain proceeds"; PP=0
  fi
  [ "$PP" -eq 0 ] || [ "${PAIR_GATE:-1}" = 0 ] || block "pair pre-router (out/pair_preroute.log)"
fi

python3 ../tools/prefanout.py $N.kicad_pcb "$FANOUT" fine 2>&1 | grep -E 'fanout:'   # only nets with a plane or pour to land on
# A GROUND-VIA GRID before the route where the board declares one (15 September 2026, rule 2 of the return-current ruling by
# construction: the fixer after the route found no site for 47 of D12's 185 signal vias, every candidate on other-net copper).
GG="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])).get('gnd_grid'); print(d.get('pitch', 2.1) if isinstance(d, dict) else '')" "$CFG")"
[ -n "$GG" ] && { python3 ../tools/gnd_grid.py $N.kicad_pcb --pitch "$GG" 2>&1 | grep -E 'gnd_grid:'; }
if [ -n "$EPRUNE" ]; then
  ../tools/drc.sh $N.kicad_pcb out/$N-preroute-drc.json
  python3 ../tools/escape_prune.py $N.kicad_pcb out/$N-preroute-drc.json 2>&1 | grep escape_prune
fi
# PRE-LAY: a long net the router will not take, laid before the router runs (14 September 2026, board C).
# `prelay_nets` in boards/<letter>.json names them and `prelay_layers` gives the layers to search. On the
# ROUTED board there is no lane left for C's `/EPD_SDA`, 249 mm from J_EPD pin 14 to U3 pad 5 across a panel
# that is a ring: four routes in a row left it, or left another net exactly like it, because the strips are
# the only corridors and whoever reaches them first takes them. On the PLACED board those strips are empty.
# The board is kept only if the hard count does not rise, judged on the board itself, and the search is the
# same stub router the finish uses, restricted to the named nets by STUB_NETS.
PRELAY="$(cfg prelay_nets)"
if [ -n "$PRELAY" ]; then
  # under the one guard (tools/guarded.sh, 15 September 2026): hard AND unrouted against the board handed in, on the
  # pre-route basis (a placed board is not judged on its opens)
  T=../tools; . ../tools/guarded.sh
  prelay_stage () {
    ../tools/drc.sh $N.kicad_pcb out/$N-prelay-in.json
    env STUB_NETS="$PRELAY" STUB_LAYERS="$(cfg prelay_layers)" STUB_GRID="${PRELAY_GRID:-0.1}" STUB_WIN_SCALE="${PRELAY_WIN:-25}" STUB_MAXN="${PRELAY_MAXN:-200000000}" \
      timeout "${PRELAY_TIMEOUT_S:-3600}" nice -n 10 python3 -u ../tools/stub_router.py $N.kicad_pcb out/$N-prelay-in.json > out/$N-prelay.log 2>&1
    grep -aE "stub_router:|closed |FAILED|NOT CLOSED" out/$N-prelay.log | tail -8
  }
  GUARD_MODE=pre guarded prelay prelay_stage
fi

PAOFF=""; { [ "${PLACE_AUDIT_GATE:-1}" = 0 ] || [ -n "$(cfg place_audit_gate_off)" ]; } && PAOFF="VERDICT_ADVISORY=1"   # a declared report writes an advisory verdict, so the supervisor reads what the chain reads
env $PAOFF $ESCENV python3 ../tools/place_audit.py $N.kicad_pcb --png out/place_audit.png > out/place_audit.log 2>&1; PA=$?
grep -E "FAIL|predicted|decoupling" out/place_audit.log | tail -8
# 15 September 2026: a board may declare the predictor's verdict as a report rather than a block (B19: its nine predicted
# collisions are the fine-pitch stations of 32.146, the router resolves or leaves them and the routed-board gate decides).
[ "$PA" -eq 0 ] || [ "${PLACE_AUDIT_GATE:-1}" = 0 ] || [ -n "$(cfg place_audit_gate_off)" ] || block "placement predictor (out/place_audit.log, out/place_audit.png)"

cp $N.kicad_pcb out/$N-preroute.kicad_pcb
../tools/drc.sh $N.kicad_pcb out/$N-preroute-drc.json
python3 ../tools/hardset.py out/$N-preroute-drc.json pre --gate out/preroute-gate.txt --examples 6 --label 'pre-route DRC' | sed 's/^hardset:/pre-route DRC:/'
python3 ../tools/check_zone_nets.py $N.kicad_pcb > out/zone_nets.log 2>&1; ZN=$?; grep -E "FAIL|zone nets" out/zone_nets.log
[ "$ZN" -eq 0 ] || echo "BLOCK zone-nets (DRC gate said: $(cat out/preroute-gate.txt))" > out/preroute-gate.txt
V=$(cat out/preroute-gate.txt); echo PREROUTE-DONE $V; [ "$V" = OK ] || exit 1   # a chain run by hand used to exit 0 on its own BLOCK
