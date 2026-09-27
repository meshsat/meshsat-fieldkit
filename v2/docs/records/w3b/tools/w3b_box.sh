#!/usr/bin/env bash
# MESHSAT-1357 stream w3b (board B: PWR-001 declarations, decision 42 classes, W3B-F1), 27 September 2026. Box 52646493,
# /root/w3b ONLY: the box's own /root/gitlab clone is read (git clone --no-local) and never written; every other /root
# directory is another stream's. Adapted from v2/docs/records/r8b/integration/r8int3_box.sh (same chain, board B only).
# Trees, both from main 38dcd764 (the box clone plus an incremental bundle):
#   base = main as committed (main's generator against main's committed board B files: parity of the chain)
#   cand = main + stream w3b's gen_sch_b.py (committed in the box clone as a scratch commit, so any file the chain rewrites
#          shows in git status)
# Modes: setup | regen | compare | gates | clean-up
set -uo pipefail
W=/root/w3b; IN=$W/in; OUT=$W/out; R=$W/repo
export TMPDIR=$W/tmp; mkdir -p "$TMPDIR" "$OUT"
MAIN=38dcd76442a14ef5906d0682aadb1fb8280e3185
N=pcb-b-compute; D=pcb-b-compute-b19
log() { echo "w3b: $*"; }
case "${1:-}" in
setup)
  exec > >(tee "$OUT/setup.log") 2>&1
  log "setup start $(date -u +%FT%TZ)"; df -h /root | tail -1
  ( cd "$IN" && sha256sum main-inc.bundle gen_sch_b.py indep_cmp.py expected_w3b.json ) | tee "$OUT/incoming.sha256"
  rm -rf "$R" "$W/base" "$W/cand"
  git clone -q --no-local --no-checkout /root/gitlab/products/meshsat/meshsat-fieldkit "$R" || { log "STOP clone"; exit 2; }
  git -C "$R" bundle verify "$IN/main-inc.bundle" 2>&1 | tail -1
  git -C "$R" fetch -q "$IN/main-inc.bundle" fnd/w3b:refs/heads/w3bmain || { log "STOP fetch"; exit 2; }
  [ "$(git -C "$R" rev-parse w3bmain)" = "$MAIN" ] || { log "STOP w3bmain is not $MAIN"; exit 2; }
  git -C "$R" remote remove origin
  for t in base cand; do git -C "$R" worktree add -q --detach "$W/$t" w3bmain || { log "STOP worktree $t"; exit 2; }; done
  ( cd "$W/cand" && cp "$IN/gen_sch_b.py" v2/ecad/tools/gen_sch_b.py && git add -A && git -c user.name=w3b-scratch -c user.email=w3b@scratch commit -q -m "w3b scratch: the stream's gen_sch_b.py" ) && log "cand overlay $(git -C "$W/cand" rev-parse --short HEAD): $(git -C "$W/cand" show --stat --format= HEAD | tail -1)"
  for t in base cand; do log "$t head $(git -C "$W/$t" rev-parse --short HEAD) status $(git -C "$W/$t" status --porcelain | wc -l)"; done
  df -h /root | tail -1; log "setup done $(date -u +%FT%TZ)"; touch "$W/setup.flag";;
regen)
  exec > >(tee "$OUT/regen.log") 2>&1
  log "regen start $(date -u +%FT%TZ)"; kicad-cli version; python3 --version
  fp () {  # the footprint generators of main's chain, into the tree's own meshsat.pretty, once
    local T=$1; : > "$OUT/fp-$(basename "$T").log"
    for g in gen_footprints_b16.py gen_footprints_idc.py; do ( cd "$T/v2/ecad/tools" && python3 "$g" ../meshsat.pretty ) >> "$OUT/fp-$(basename "$T").log" 2>&1 || log "footprint generator $g FAILED in $(basename "$T")"; done
    log "$(basename "$T") footprint generators: meshsat.pretty status after them: [$(git -C "$T" status --porcelain -- v2/ecad/meshsat.pretty | tr '\n' ' ')]"
  }
  fp "$W/base"; fp "$W/cand"
  regen_one () {  # $1 tree, $2 out dir
    local T=$1 O=$2; local E=$T/v2/ecad; mkdir -p "$O/files" "$O/ref"; cd "$E/$D" || return 2
    local LABEL; LABEL=$(grep -m1 -o '(comment 1 "Phase [A-Za-z0-9]*' "$N.kicad_sch" | sed 's/.*Phase //'); echo "$LABEL" > "$O/phase.txt"
    cp "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "$O/ref/"
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "$O/ref/$N-bom.csv" "$N.kicad_sch" > /dev/null 2>&1
    kicad-cli sch erc --severity-all --format json -o "$O/ref/$N-erc.json" "$N.kicad_sch" > /dev/null 2>&1
    python3 "$E/tools/sch_prov.py" read "out/$N.net" b > "$O/prov-before.txt" 2>&1; echo "exit $?" >> "$O/prov-before.txt"
    local GENV; GENV="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])).get('gen_env') or {}; print(' '.join('%s=%s' % (k, v) for k, v in d.items()))" "$E/tools/boards/b.json")"
    echo "gen_env: [$GENV] PHASE=$LABEL" > "$O/gen_sch.log"
    PHASE="$LABEL" env $GENV python3 ../tools/gen_sch_b.py "$N.kicad_sch" "$N" >> "$O/gen_sch.log" 2>&1; local GE=$?; echo "gen_sch exit $GE" >> "$O/gen_sch.log"
    [ $GE -ne 0 ] && { echo "STOP generation failed"; tail -20 "$O/gen_sch.log"; return 3; }
    rm -f "out/$N.net" "out/$N-bom.csv" "out/$N.net.prov.json"
    bash ../tools/build_sch.sh . "$N" > "$O/build_sch.log" 2>&1; echo "build_sch exit $?" >> "$O/build_sch.log"
    python3 "$E/tools/sch_prov.py" write "out/$N.net" b > "$O/sch_prov_write.txt" 2>&1; echo "exit $?" >> "$O/sch_prov_write.txt"
    python3 "$E/tools/sch_prov.py" read "out/$N.net" b > "$O/prov-after.txt" 2>&1; echo "exit $?" >> "$O/prov-after.txt"
    for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "out/$N-bom.csv" "out/$N-erc.json" "out/$N-erc.rpt" "out/$N-schematic.pdf"; do
      [ -s "$f" ] && cp "$f" "$O/files/" || echo "missing: $f" >> "$O/missing.txt"; done
    echo "$(basename "$T") b phase $LABEL $(tail -1 "$O/gen_sch.log") $(tail -1 "$O/build_sch.log") $(date -u +%T)"
  }
  ( regen_one "$W/base" "$OUT/base" ) > "$OUT/regen-base.log" 2>&1 & P1=$!
  ( regen_one "$W/cand" "$OUT/cand" ) > "$OUT/regen-cand.log" 2>&1 & P2=$!
  wait $P1; wait $P2; cat "$OUT"/regen-base.log "$OUT"/regen-cand.log
  # determinism: the candidate generator a second time, into a throwaway copy of its board directory
  rm -rf "$W/det"; mkdir -p "$W/det" "$OUT/cand2"
  cp -a "$W/cand/v2/ecad/$D" "$W/det/$D"; ln -s "$W/cand/v2/ecad/tools" "$W/det/tools"; ln -s "$W/cand/v2/ecad/meshsat.pretty" "$W/det/meshsat.pretty"
  ( cd "$W/det/$D" && PHASE="$(cat "$OUT/cand/phase.txt")" python3 ../tools/gen_sch_b.py "$N.kicad_sch" "$N" > "$OUT/cand2/gen_sch.log" 2>&1; echo "exit $?" >> "$OUT/cand2/gen_sch.log"
    rm -f "out/$N.net"; kicad-cli sch export netlist --format kicadsexpr -o "out/$N.net" "$N.kicad_sch" > /dev/null 2>&1
    cp "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "$OUT/cand2/" )
  for f in "$N.kicad_sch" "$N.net" "$N-intent.json"; do log "determinism $f: $(cmp -s "$OUT/cand/files/$f" "$OUT/cand2/$f" && echo IDENTICAL || echo differs)"; done
  for t in base cand; do log "$t status after regen:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'; done
  df -h /root | tail -1; log "regen done $(date -u +%FT%TZ)"; touch "$W/regen.flag";;
compare)
  exec > >(tee "$OUT/compare.log") 2>&1
  log "compare start $(date -u +%FT%TZ)"
  RC=$W/base/v2/ecad/tools/regen_compare.py; C=$OUT/compare; mkdir -p "$C"
  v () { python3 -c "import json,sys
d=json.load(open(sys.argv[1]))
print(d.get('verdict') or d.get('result') or d.get('status') or '?')" "$1" 2>/dev/null || echo "?"; }
  pair () { python3 "$RC" pair "$2" "$3" "$4" > "$C/$1_$2.json" 2>&1; printf "%-24s %-10s exit %s  %s\n" "$1" "$2" "$?" "$(v "$C/$1_$2.json")"; }
  log "== main's generator against main's committed board B files (base)"
  for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json provenance:$N.net.prov.json bom:$N-bom.csv erc:$N-erc.json; do
    pair base_vs_committed "${k%%:*}" "$OUT/base/ref/${k#*:}" "$OUT/base/files/${k#*:}"; done
  log "== the candidate against main regenerated (cand vs base)"
  for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json bom:$N-bom.csv erc:$N-erc.json; do
    pair cand_vs_base "${k%%:*}" "$OUT/base/files/${k#*:}" "$OUT/cand/files/${k#*:}"; done
  log "== independent netlist comparison (indep_cmp.py) with the w3b expected-change list"
  python3 "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/cand/files/$N.net" --expect "$IN/expected_w3b.json" > "$C/indep_committed_vs_cand.txt" 2>&1; log "committed main -> cand exit $?"; head -12 "$C/indep_committed_vs_cand.txt"
  python3 "$IN/indep_cmp.py" "$OUT/base/files/$N.net" "$OUT/cand/files/$N.net" --expect "$IN/expected_w3b.json" > "$C/indep_mainregen_vs_cand.txt" 2>&1; log "main regenerated -> cand exit $?"; head -12 "$C/indep_mainregen_vs_cand.txt"
  python3 "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/base/files/$N.net" > "$C/indep_committed_vs_mainregen.txt" 2>&1; log "committed main -> main regenerated (raw)"; head -3 "$C/indep_committed_vs_mainregen.txt"
  python3 "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/cand/files/$N.net" --expect "$IN/expected_w3b.json" --drop W3B-F1:parts_added > "$C/indep_dropped.txt" 2>&1; log "with W3B-F1 parts_added dropped (must refuse) exit $? unexplained $(grep -c UNEXPLAINED "$C/indep_dropped.txt")"
  for t in base cand; do log "$t status after compare:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'; done
  log "compare done $(date -u +%FT%TZ)"; touch "$W/compare.flag";;
gates)
  # the gates that need KiCad, on both trees, every verdict under out/gates-box (VERDICT_DIR): the ERC gate, and the board-mode
  # intent_checks, whose intent_decoupling (DEC-001) is taken on the committed B19 placement against each tree's intent: NOT
  # evidence for the candidate (the placement predates round 8), recorded to show what the rule reads today
  exec > >(tee "$OUT/gates.log") 2>&1
  O=$OUT/gates-box; mkdir -p "$O"
  for t in base cand; do mkdir -p "$O/$t"; cd "$W/$t/v2/ecad/$D" || exit 2
    VERDICT_DIR="$O/$t" timeout 600 python3 ../tools/erc_gate.py . "$N" > "$O/$t/erc_gate.log" 2>&1; echo "erc_gate exit $?" >> "$O/$t/erc_gate.log"
    VERDICT_DIR="$O/$t" timeout 900 python3 ../tools/intent_checks.py "$N.kicad_pcb" > "$O/$t/intent_board.log" 2>&1; echo "intent_checks board exit $?" >> "$O/$t/intent_board.log"
    log "$t: $(grep '^verdict: erc_gate' "$O/$t/erc_gate.log" | cut -c1-160)"; done
  python3 "$IN/rename_check.py" "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/cand/files/$N.net" > "$OUT/compare/rename_check.txt" 2>&1; log "rename check exit $?: $(tail -1 "$OUT/compare/rename_check.txt")"
  for t in base cand; do log "$t status after gates:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'; done
  log "gates done $(date -u +%FT%TZ)"; touch "$W/gates.flag";;
clean-up)
  cd /root && rm -rf "$W" && echo "w3b: removed $W"; df -h /root | tail -1;;
*) echo "usage: $0 setup|regen|compare|gates|clean-up"; exit 2;;
esac
