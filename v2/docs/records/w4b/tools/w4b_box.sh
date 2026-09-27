#!/usr/bin/env bash
# MESHSAT-1357 stream w4b (board B: RF-002, the RockBLOCK's I_EN forced low by EMCON and the L4 case (2) enable dividers),
# 27 September 2026. Box 52646493, /root/w4b ONLY: the box's own /root/gitlab clone is read (git clone --no-local) and never
# written; every other /root directory is another stream's. Adapted from v2/docs/records/w3b/tools/w3b_box.sh (same chain,
# board B only), with a re-take stage added (the consolidated re-take driver, board B, verdicts outside the trees).
# Trees, all from main 91894cd7 (the box clone plus an incremental bundle):
#   base = main as committed, regenerated (main's generator against main's committed board B files: parity of the chain)
#   cand = main + stream w4b's gen_sch_b.py and boards/b.json (a scratch commit in the box clone, so any file the chain
#          rewrites shows in git status); after regen its board B schematic-phase files are committed there as a second
#          scratch commit, so the re-take driver reads committed inputs
#   rtb  = main as committed, untouched: the re-take of board B's readings BEFORE the change
# Modes: setup | regen | compare | retake | retake-draft | clean-up
set -uo pipefail
W=/root/w4b; IN=$W/in; OUT=$W/out; R=$W/repo
export TMPDIR=$W/tmp; mkdir -p "$TMPDIR" "$OUT"
MAIN=91894cd7f1966f8030c85ee7341ada1f345c4bfe
N=pcb-b-compute; D=pcb-b-compute-b19
log() { echo "w4b: $*"; }
case "${1:-}" in
setup)
  exec > >(tee "$OUT/setup.log") 2>&1
  log "setup start $(date -u +%FT%TZ)"; df -h /root | tail -1
  ( cd "$IN" && sha256sum main-inc.bundle gen_sch_b.py b.json indep_cmp.py expected_w4b.json ) | tee "$OUT/incoming.sha256"
  rm -rf "$R" "$W/base" "$W/cand" "$W/rtb"
  git clone -q --no-local --no-checkout /root/gitlab/products/meshsat/meshsat-fieldkit "$R" || { log "STOP clone"; exit 2; }
  git -C "$R" bundle verify "$IN/main-inc.bundle" 2>&1 | tail -1
  git -C "$R" fetch -q "$IN/main-inc.bundle" fnd/w4b:refs/heads/w4bmain || { log "STOP fetch"; exit 2; }
  [ "$(git -C "$R" rev-parse w4bmain)" = "$MAIN" ] || { log "STOP w4bmain is not $MAIN"; exit 2; }
  git -C "$R" remote remove origin
  for t in base cand rtb; do git -C "$R" worktree add -q --detach "$W/$t" w4bmain || { log "STOP worktree $t"; exit 2; }; done
  ( cd "$W/cand" && cp "$IN/gen_sch_b.py" v2/ecad/tools/gen_sch_b.py && cp "$IN/b.json" v2/ecad/tools/boards/b.json && git add -A \
    && git -c user.name=w4b-scratch -c user.email=w4b@scratch commit -q -m "w4b scratch: the stream's gen_sch_b.py and boards/b.json" ) \
    && log "cand overlay $(git -C "$W/cand" rev-parse --short HEAD): $(git -C "$W/cand" show --stat --format= HEAD | tail -1)"
  for t in base cand rtb; do log "$t head $(git -C "$W/$t" rev-parse --short HEAD) status $(git -C "$W/$t" status --porcelain | wc -l)"; done
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
  log "== independent netlist comparison (indep_cmp.py) with the w4b expected-change list"
  python3 "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/cand/files/$N.net" --expect "$IN/expected_w4b.json" > "$C/indep_committed_vs_cand.txt" 2>&1; log "committed main -> cand exit $?"; head -14 "$C/indep_committed_vs_cand.txt"
  python3 "$IN/indep_cmp.py" "$OUT/base/files/$N.net" "$OUT/cand/files/$N.net" --expect "$IN/expected_w4b.json" > "$C/indep_mainregen_vs_cand.txt" 2>&1; log "main regenerated -> cand exit $?"; head -14 "$C/indep_mainregen_vs_cand.txt"
  python3 "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/base/files/$N.net" > "$C/indep_committed_vs_mainregen.txt" 2>&1; log "committed main -> main regenerated (raw)"; head -3 "$C/indep_committed_vs_mainregen.txt"
  python3 "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/cand/files/$N.net" > "$C/indep_committed_vs_cand_raw.json" 2>&1
  for dr in W4B-D1:parts_added W4B-D2:nets_changed W4B-D3:parts_removed W4B-D3:nets_changed; do
    python3 "$IN/indep_cmp.py" "$OUT/base/ref/$N.net" "$OUT/cand/files/$N.net" --expect "$IN/expected_w4b.json" --drop "$dr" > "$C/indep_dropped_${dr/:/_}.txt" 2>&1
    log "with $dr dropped (must refuse) exit $? unexplained $(grep -c UNEXPLAINED "$C/indep_dropped_${dr/:/_}.txt")"; done
  for t in base cand; do log "$t status after compare:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'; done
  log "compare done $(date -u +%FT%TZ)"; touch "$W/compare.flag";;
retake)
  # board B's schematic-phase readings re-taken by main's driver (v2/ecad/tools/retake_schematic_phase.py --verdict-dir):
  # before in rtb (main as committed), after in cand with its regenerated board B files committed as a scratch commit
  exec > >(tee "$OUT/retake.log") 2>&1
  log "retake start $(date -u +%FT%TZ)"
  if [ -n "$(git -C "$W/cand" status --porcelain -- "v2/ecad/$D")" ]; then
    git -C "$W/cand" add "v2/ecad/$D/$N.kicad_sch" "v2/ecad/$D/out/$N.net" "v2/ecad/$D/out/$N-intent.json" "v2/ecad/$D/out/$N.net.prov.json" 2>&1
    git -C "$W/cand" -c user.name=w4b-scratch -c user.email=w4b@scratch commit -q -m "w4b scratch: board B regenerated by the candidate generator" 2>&1; log "cand regen commit exit $?"
  fi
  log "cand head $(git -C "$W/cand" log --oneline -3 | tr '\n' '|')"
  log "cand status before retake (untracked build outputs only expected):"; git -C "$W/cand" status --porcelain | sed 's/^/    /'
  for t in ${RT_TREES:-rtb cand}; do
    rm -rf "$W/rt-$t" "$OUT/rt-$t"; mkdir -p "$W/rt-$t"
    ( cd "$W/$t" && timeout 3000 python3 v2/ecad/tools/retake_schematic_phase.py --run --board b --verdict-dir "$W/rt-$t" --json > "$OUT/retake-$t.json" 2> "$OUT/retake-$t.err" ); log "$t retake exit $?"
    tail -5 "$OUT/retake-$t.err"
    mkdir -p "$OUT/rt-$t"; cp "$W/rt-$t/$D/out/"*.verdict.json "$OUT/rt-$t/" 2>/dev/null; ls "$OUT/rt-$t" | wc -l
  done
  for t in rtb cand; do log "$t status after retake:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'; done
  log "retake done $(date -u +%FT%TZ)"; touch "$W/retake.flag";;
retake-draft)
  # the same re-take with stream w4b's DRAFT for tx_inhibit.py (drafts/w4b/tools/apply_tx_inhibit_w4b.py) applied, on main as
  # committed (mt) and on the candidate with its regenerated board B (ct): what the tool rows alone move, and what the circuit
  # and the rows move together. The draft is the tools author's to adopt; these readings are labelled with it.
  exec > >(tee "$OUT/retake-draft.log") 2>&1
  log "retake-draft start $(date -u +%FT%TZ)"
  CAND=$(git -C "$W/cand" rev-parse HEAD)
  rm -rf "$W/mt" "$W/ct"; git -C "$R" worktree prune
  git -C "$R" worktree add -q --detach "$W/mt" w4bmain; git -C "$R" worktree add -q --detach "$W/ct" "$CAND"
  for t in mt ct; do
    ( cd "$W/$t" && python3 "$IN/apply_tx_inhibit_w4b.py" v2/ecad/tools/tx_inhibit.py && git add v2/ecad/tools/tx_inhibit.py \
      && git -c user.name=w4b-scratch -c user.email=w4b@scratch commit -q -m "w4b scratch: the tx_inhibit.py draft" ) 2>&1 | tail -2
    log "$t head $(git -C "$W/$t" log --oneline -3 | tr '\n' '|')"
    rm -rf "$W/rt-$t" "$OUT/rt-$t"; mkdir -p "$W/rt-$t"
    ( cd "$W/$t" && timeout 3000 python3 v2/ecad/tools/retake_schematic_phase.py --run --board b --verdict-dir "$W/rt-$t" --json > "$OUT/retake-$t.json" 2> "$OUT/retake-$t.err" ); log "$t retake exit $?"
    tail -3 "$OUT/retake-$t.err"
    mkdir -p "$OUT/rt-$t"; cp "$W/rt-$t/$D/out/"*.verdict.json "$OUT/rt-$t/" 2>/dev/null; ls "$OUT/rt-$t" | wc -l
    log "$t status after retake:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'
  done
  log "retake-draft done $(date -u +%FT%TZ)"; touch "$W/retake-draft.flag";;
clean-up)
  cd /root && rm -rf "$W" && echo "w4b: removed $W"; df -h /root | tail -1;;
*) echo "usage: $0 setup|regen|compare|retake|retake-draft|clean-up"; exit 2;;
esac
