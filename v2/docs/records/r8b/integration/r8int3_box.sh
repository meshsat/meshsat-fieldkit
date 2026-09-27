#!/usr/bin/env bash
# MESHSAT-1357 round 8 set 3 (board B), integration worker, 27 September 2026. Box 52646493, /root/r8int3 ONLY: the box's
# own /root/gitlab clone is read (git clone --no-local copies through upload-pack) and never written; /root/h1 and every
# other directory are another session's.
# Trees, all from main 84e52461 with its full history (the box clone up to 82dd1e4d plus the incremental bundle):
#   base  = main as committed (main's generator against main's committed board B files)
#   tauth = main + the board B author's commit set as the author left it (gen_sch_b.py, b.json, the hand-written land)
#   tree  = main + the integration's generator set (the author's gen_sch_b.py with U{s}15's value text reworded, b.json,
#           gen_footprints_b16.py with the land folded in, the land), committed as a scratch commit so any file the
#           chain rewrites shows in git status
# Modes: setup | regen | set | suite <bundle-dir> | clean-up
set -uo pipefail
W=/root/r8int3; IN=$W/incoming; OUT=$W/out; R=$W/repo
export TMPDIR=$W/tmp; mkdir -p "$TMPDIR" "$OUT"
MAIN=84e524610bc11c3062f80a29e9d2e61be88d0a68
declare -A DIR=([a]=pcb-a-power-a23 [b]=pcb-b-compute-b19 [c]=pcb-c-display-c8 [d]=pcb-d-aprs-d9 [e]=pcb-e1-dock-e7 [p]=pcb-p-pack-p2)
declare -A STEM=([a]=pcb-a-power [b]=pcb-b-compute [c]=pcb-c-display [d]=pcb-d-aprs [e]=pcb-e1-dock [p]=pcb-p-pack)
log() { echo "r8int3: $*"; }
mode=${1:-}
case "$mode" in
setup)
  exec > >(tee "$OUT/setup.log") 2>&1
  log "setup start $(date -u +%FT%TZ)"; df -h /root | tail -1
  ( cd "$IN" && sha256sum main-inc.bundle overlay.tgz author/* t/* ) | tee "$OUT/incoming.sha256"
  rm -rf "$R" "$W/base" "$W/tauth" "$W/tree"
  git clone -q --no-local --no-checkout /root/gitlab/products/meshsat/meshsat-fieldkit "$R" || { log "STOP clone"; exit 2; }
  git -C "$R" bundle verify "$IN/main-inc.bundle" 2>&1 | tail -1
  git -C "$R" fetch -q "$IN/main-inc.bundle" main:refs/heads/r8main || { log "STOP fetch"; exit 2; }
  [ "$(git -C "$R" rev-parse r8main)" = "$MAIN" ] || { log "STOP r8main is not $MAIN"; exit 2; }
  git -C "$R" remote remove origin
  log "repo r8main $(git -C "$R" rev-parse --short=8 r8main), commits $(git -C "$R" rev-list --count r8main), shallow $(git -C "$R" rev-parse --is-shallow-repository)"
  for t in base tauth tree; do git -C "$R" worktree add -q --detach "$W/$t" r8main || { log "STOP worktree $t"; exit 2; }; done
  ( cd "$W/tree" && tar -xzf "$IN/overlay.tgz" && git add -A && git -c user.name=r8int3-scratch -c user.email=r8int3@scratch commit -q -m "r8int3 scratch: the integration's generator set" ) && log "tree overlay committed $(git -C "$W/tree" rev-parse --short HEAD): $(git -C "$W/tree" show --stat --format= HEAD | tail -1)"
  ( cd "$W/tauth" && tar -xzf "$IN/overlay.tgz" && git checkout -q r8main -- v2/ecad/tools/gen_footprints_b16.py && cp "$IN/author/gen_sch_b.py" v2/ecad/tools/gen_sch_b.py && git add -A && git -c user.name=r8int3-scratch -c user.email=r8int3@scratch commit -q -m "r8int3 scratch: the author's commit set's generator files" ) && log "tauth overlay committed $(git -C "$W/tauth" rev-parse --short HEAD): $(git -C "$W/tauth" show --stat --format= HEAD | tail -1)"
  for t in base tauth tree; do log "$t head $(git -C "$W/$t" rev-parse --short HEAD) status $(git -C "$W/$t" status --porcelain | wc -l)"; done
  df -h /root | tail -1; log "setup done $(date -u +%FT%TZ)"; touch "$W/setup.flag";;
regen)
  exec > >(tee "$OUT/regen.log") 2>&1
  log "regen start $(date -u +%FT%TZ)"; kicad-cli version; python3 --version
  fp () {  # $1 tree, $2 generators: run each into the tree's own meshsat.pretty, serially, once
    local T=$1; shift; : > "$OUT/fp-$(basename "$T").log"
    for g in "$@"; do ( cd "$T/v2/ecad/tools" && python3 "$g" ../meshsat.pretty ) >> "$OUT/fp-$(basename "$T").log" 2>&1 || log "footprint generator $g FAILED in $(basename "$T")"; done
    log "$(basename "$T") footprint generators: $(grep -c . "$OUT/fp-$(basename "$T").log") lines; meshsat.pretty status after them: [$(git -C "$T" status --porcelain -- v2/ecad/meshsat.pretty | tr '\n' ' ')]"
  }
  fp "$W/base" gen_footprints_b16.py gen_footprints_idc.py
  fp "$W/tauth" gen_footprints_b16.py gen_footprints_idc.py
  fp "$W/tree" gen_footprints_b16.py gen_footprints_idc.py gen_footprints_e.py
  regen_one () {  # $1 tree, $2 letter, $3 out dir
    local T=$1 L=$2 O=$3; local E=$T/v2/ecad; local D=$E/${DIR[$L]}; local N=${STEM[$L]}
    mkdir -p "$O/files" "$O/ref"; cd "$D" || return 2
    local LABEL; LABEL=$(grep -m1 -o '(comment 1 "Phase [A-Za-z0-9]*' "$N.kicad_sch" | sed 's/.*Phase //'); echo "$LABEL" > "$O/phase.txt"
    cp "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "$O/ref/"
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "$O/ref/$N-bom.csv" "$N.kicad_sch" > /dev/null 2>&1
    kicad-cli sch erc --severity-all --format json -o "$O/ref/$N-erc.json" "$N.kicad_sch" > /dev/null 2>&1
    python3 "$E/tools/sch_prov.py" read "out/$N.net" "$L" > "$O/prov-before.txt" 2>&1; echo "exit $?" >> "$O/prov-before.txt"
    local GENV; GENV="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])).get('gen_env') or {}; print(' '.join('%s=%s' % (k, v) for k, v in d.items()))" "$E/tools/boards/$L.json")"
    echo "gen_env: [$GENV] PHASE=$LABEL" > "$O/gen_sch.log"
    PHASE="$LABEL" env $GENV python3 ../tools/gen_sch_$L.py "$N.kicad_sch" "$N" >> "$O/gen_sch.log" 2>&1; local GE=$?; echo "gen_sch exit $GE" >> "$O/gen_sch.log"
    [ $GE -ne 0 ] && { echo "STOP generation failed"; tail -20 "$O/gen_sch.log"; return 3; }
    rm -f "out/$N.net" "out/$N-bom.csv" "out/$N.net.prov.json"
    bash ../tools/build_sch.sh . "$N" > "$O/build_sch.log" 2>&1; echo "build_sch exit $?" >> "$O/build_sch.log"
    python3 "$E/tools/sch_prov.py" write "out/$N.net" "$L" > "$O/sch_prov_write.txt" 2>&1; echo "exit $?" >> "$O/sch_prov_write.txt"
    python3 "$E/tools/sch_prov.py" read "out/$N.net" "$L" > "$O/prov-after.txt" 2>&1; echo "exit $?" >> "$O/prov-after.txt"
    for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "out/$N-bom.csv" "out/$N-erc.json" "out/$N-erc.rpt" "out/$N-schematic.pdf"; do
      [ -s "$f" ] && cp "$f" "$O/files/" || echo "missing: $f" >> "$O/missing.txt"; done
    echo "$(basename "$T") $L phase $LABEL $(tail -1 "$O/gen_sch.log") $(tail -1 "$O/build_sch.log") $(date -u +%T)"
  }
  PIDS=""
  ( regen_one "$W/base" b "$OUT/base/b" ) > "$OUT/regen-base-b.log" 2>&1 & PIDS="$PIDS $!"
  ( regen_one "$W/tauth" b "$OUT/tauth/b" ) > "$OUT/regen-tauth-b.log" 2>&1 & PIDS="$PIDS $!"
  for L in a b c d e p; do ( regen_one "$W/tree" $L "$OUT/tree/$L" ) > "$OUT/regen-tree-$L.log" 2>&1 & PIDS="$PIDS $!"; done
  for p in $PIDS; do wait $p; done
  cat "$OUT"/regen-*.log | grep -v "^$" | tail -40
  # determinism: the tree's board B generator a second time, into a throwaway copy of its board directory
  rm -rf "$W/det"; mkdir -p "$W/det" "$OUT/tree/b2"
  cp -a "$W/tree/v2/ecad/pcb-b-compute-b19" "$W/det/pcb-b-compute-b19"; ln -s "$W/tree/v2/ecad/tools" "$W/det/tools"; ln -s "$W/tree/v2/ecad/meshsat.pretty" "$W/det/meshsat.pretty"
  ( cd "$W/det/pcb-b-compute-b19" && PHASE="$(cat "$OUT/tree/b/phase.txt")" python3 ../tools/gen_sch_b.py pcb-b-compute.kicad_sch pcb-b-compute > "$OUT/tree/b2/gen_sch.log" 2>&1; echo "exit $?" >> "$OUT/tree/b2/gen_sch.log"
    rm -f out/pcb-b-compute.net; kicad-cli sch export netlist --format kicadsexpr -o out/pcb-b-compute.net pcb-b-compute.kicad_sch > /dev/null 2>&1
    cp pcb-b-compute.kicad_sch out/pcb-b-compute.net out/pcb-b-compute-intent.json "$OUT/tree/b2/" )
  for f in pcb-b-compute.kicad_sch pcb-b-compute.net pcb-b-compute-intent.json; do log "determinism $f: $(cmp -s "$OUT/tree/b/files/$f" "$OUT/tree/b2/$f" && echo IDENTICAL || echo differs)"; done
  for t in base tauth tree; do log "$t status after regen:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'; done
  df -h /root | tail -1; log "regen done $(date -u +%FT%TZ)"; touch "$W/regen.flag";;
set)
  exec > >(tee "$OUT/set.log") 2>&1
  log "set start $(date -u +%FT%TZ)"
  RC=$W/base/v2/ecad/tools/regen_compare.py; C=$OUT/compare; mkdir -p "$C"
  v () { python3 -c "import json,sys
d=json.load(open(sys.argv[1]))
print(d.get('verdict') or d.get('result') or d.get('status') or '?')" "$1" 2>/dev/null || echo "?"; }
  pair () {  # $1 label $2 kind $3 a $4 b
    python3 "$RC" pair "$2" "$3" "$4" > "$C/$1_$2.json" 2>&1; printf "%-34s %-10s exit %s  %s\n" "$1" "$2" "$?" "$(v "$C/$1_$2.json")"; }
  N=pcb-b-compute
  log "== board B: main's generator against main's committed files (base)"
  for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json provenance:$N.net.prov.json bom:$N-bom.csv erc:$N-erc.json; do
    pair base_vs_committed "${k%%:*}" "$OUT/base/b/ref/${k#*:}" "$OUT/base/b/files/${k#*:}"; done
  log "== board B: the author's commit set regenerated on main (tauth) against the author's files"
  for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json provenance:$N.net.prov.json; do
    pair tauth_vs_author "${k%%:*}" "$IN/author/${k#*:}" "$OUT/tauth/b/files/${k#*:}"; done
  log "== board B: the integration's generator set (tree) against the author's files and against tauth"
  for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json; do
    pair tree_vs_author "${k%%:*}" "$IN/author/${k#*:}" "$OUT/tree/b/files/${k#*:}"
    pair tree_vs_tauth "${k%%:*}" "$OUT/tauth/b/files/${k#*:}" "$OUT/tree/b/files/${k#*:}"; done
  log "== boards A, C, D, E, P regenerated in the tree (the new land and generator in every identity) against main's committed files"
  for L in a c d e p; do M=${STEM[$L]}
    for k in schematic:$M.kicad_sch netlist:$M.net intent:$M-intent.json bom:$M-bom.csv erc:$M-erc.json; do
      pair "tree_${L}_vs_committed" "${k%%:*}" "$OUT/tree/$L/ref/${k#*:}" "$OUT/tree/$L/files/${k#*:}"; done
    log "   $L sidecar before: $(tail -2 "$OUT/tree/$L/prov-before.txt" | tr '\n' ' ' | cut -c1-260)"
    log "   $L sidecar after:  $(tail -2 "$OUT/tree/$L/prov-after.txt" | tr '\n' ' ' | cut -c1-200)"
  done
  log "== the integration's independent netlist comparison (t/indep_cmp.py, its own reader) against the author's per-finding list"
  python3 "$IN/t/indep_cmp.py" "$OUT/base/b/ref/$N.net" "$OUT/tree/b/files/$N.net" --expect "$IN/t/expected_r8b.json" > "$C/indep_committed_vs_tree.txt" 2>&1; log "committed main -> tree exit $?"; head -30 "$C/indep_committed_vs_tree.txt"
  python3 "$IN/t/indep_cmp.py" "$OUT/base/b/files/$N.net" "$OUT/tree/b/files/$N.net" --expect "$IN/t/expected_r8b.json" > "$C/indep_mainregen_vs_tree.txt" 2>&1; log "main regenerated -> tree exit $?"; head -30 "$C/indep_mainregen_vs_tree.txt"
  python3 "$IN/t/indep_cmp.py" "$OUT/base/b/ref/$N.net" "$OUT/tree/b/files/$N.net" --expect "$IN/t/expected_r8b.json" --drop FAB-03:parts_added --drop S-13:parts_added > "$C/indep_dropped.txt" 2>&1; log "with FAB-03 and S-13 parts_added dropped (must refuse) exit $?"; grep -c UNEXPLAINED "$C/indep_dropped.txt"
  python3 "$IN/t/indep_cmp.py" "$IN/author/$N.net" "$OUT/tree/b/files/$N.net" > "$C/indep_author_vs_tree.txt" 2>&1; log "author -> tree (raw differences)"; python3 -c "
import json,sys; t=open(sys.argv[1]).read(); i=t.index('{'); d=json.loads(t[i:]); print(t[:i].strip()); print({k: v for k, v in d.items() if v})" "$C/indep_author_vs_tree.txt"
  log "== gates on the tree's regenerated board B and on base's (VERDICT_DIR under out/)"
  gates () {  # $1 tree, $2 out
    local T=$1 O=$2; local E=$T/v2/ecad; local D=$E/pcb-b-compute-b19; mkdir -p "$O"; cd "$D"
    local NET="out/$N.net" INT="out/$N-intent.json"
    run () { local nm=$1; shift; VERDICT_DIR="$O" timeout 1800 "$@" > "$O/$nm.log" 2>&1; echo "exit $?" >> "$O/$nm.log"; }
    run erc_gate python3 ../tools/erc_gate.py . "$N"
    run port_protect python3 ../tools/port_protect.py "$NET"
    run pin_map_lands python3 ../tools/pin_map_lands.py "$NET" b
    run derate python3 ../tools/derate.py "$NET" --intent "$INT"
    run safe_lines python3 ../tools/safe_lines.py "$NET"
    run power_sequence python3 ../tools/power_sequence.py "$NET" --intent "$INT"
    run power_path python3 ../tools/power_path.py "$NET" --intent "$INT" --out-dir "$O"
    run clock_check python3 ../tools/clock_check.py "$NET"
    run ground_system python3 ../tools/ground_system.py "$NET" --board b
    run review_nets python3 ../tools/review_nets.py "$NET"
    run emc_sheet python3 ../tools/emc_sheet.py --ecad "$E" --board b
    run reliability python3 ../tools/reliability.py --ecad "$E" --board b
    run netlist_board python3 ../tools/netlist_board.py "$N.kicad_pcb" "$NET"
    run netlist_parts python3 ../tools/netlist_parts.py "$N.kicad_pcb" "$NET" --out-dir "$O"
    run intent_rails python3 ../tools/intent_checks.py --netlist "$NET"
    run edge_length python3 ../tools/edge_length.py --netlist "$NET"
    ( cd "$E" && VERDICT_DIR="$O" timeout 1800 python3 tools/check_contracts.py "$E" > "$O/check_contracts.log" 2>&1; echo "exit $?" >> "$O/check_contracts.log" )
    ( cd "$E/tools" && VERDICT_DIR="$O" timeout 1800 python3 energy_chain.py --ecad "$E" > "$O/energy_chain.log" 2>&1; echo "exit $?" >> "$O/energy_chain.log" )
  }
  ( gates "$W/tree" "$OUT/gates/tree" ) & G1=$!; ( gates "$W/base" "$OUT/gates/base" ) & G2=$!; wait $G1; wait $G2
  python3 - "$OUT/gates" <<'PY' > "$OUT/gates.txt" 2>&1
import json, os, sys, glob
O = sys.argv[1]
def read(d):
    r = {}
    for f in sorted(glob.glob(os.path.join(d, "*.verdict.json"))):
        try: j = json.load(open(f))
        except Exception as e: r[os.path.basename(f)] = "unreadable %s" % e; continue
        c = j.get("counts") or {}
        r[os.path.basename(f)[:-13]] = "%s den=%s %s" % (j.get("verdict"), j.get("denominator"), ",".join("%s=%s" % (k, c[k]) for k in sorted(c)))
    return r
b, i = read(os.path.join(O, "base")), read(os.path.join(O, "tree"))
for k in sorted(set(b) | set(i)):
    mark = "  " if b.get(k) == i.get(k) else "* "
    print("%s%-26s base: %s\n%s  %-26s tree: %s" % (mark, k, b.get(k), " " * len(mark), "", i.get(k)))
PY
  cat "$OUT/gates.txt"
  grep -E "RF-002 .*(FAIL|UNDECIDED|PASS)" "$OUT/gates/tree/check_contracts.log" | cut -c1-230 > "$OUT/rf002-tree.txt"; wc -l < "$OUT/rf002-tree.txt"
  for t in base tauth tree; do log "$t status after set:"; git -C "$W/$t" status --porcelain | sed 's/^/    /'; done
  log "set done $(date -u +%FT%TZ)"; touch "$W/set.flag";;
suite)
  # $2: a directory under $IN holding <name>.bundle (incremental on the box clone) and evidence.tgz
  S=$IN/${2:?suite needs a bundle directory}; O=$OUT/suite-$(basename "$S"); T=$W/suite-$(basename "$S"); mkdir -p "$O"
  exec > >(tee -a "$O/suite-run.log") 2>&1
  log "suite start $(date -u +%FT%TZ)"; df -h /root | tail -1
  sha256sum "$S"/* | cut -c1-16
  BR=$(cat "$S/branch.txt"); rm -rf "$T"
  git clone -q --no-local --no-checkout /root/gitlab/products/meshsat/meshsat-fieldkit "$T" || { log "STOP clone"; exit 2; }
  cd "$T"; git bundle verify "$S/inc.bundle" 2>&1 | tail -1
  git fetch -q "$S/inc.bundle" "$BR:refs/heads/$BR" || { log "STOP fetch"; exit 2; }
  git checkout -q "$BR" || { log "STOP checkout"; exit 2; }
  git branch -f main HEAD > /dev/null 2>&1; git branch -f master HEAD > /dev/null 2>&1; git remote remove origin
  log "HEAD $(git rev-parse HEAD) commits $(git rev-list --count HEAD) shallow $(git rev-parse --is-shallow-repository)"
  tar -xzf "$S/evidence.tgz" -C "$T" || { log "STOP evidence"; exit 3; }
  log "evidence files $(tar -tzf "$S/evidence.tgz" | wc -l)"
  git status --porcelain > "$O/status-0.txt"; log "status lines before the suite: $(wc -l < "$O/status-0.txt")"
  ( find v2/ecad/out $(ls -d v2/ecad/pcb-*/out) -type f -print0 | sort -z | xargs -0 sha256sum ) > "$O/evidence-0.sha256"
  cd "$T/v2/ecad/tools/tests"; T0=$(date +%s)
  timeout 7200 python3 run.py > "$O/run_full.log" 2>&1; echo "run.py exit $?" >> "$O/run_full.log"
  log "suite seconds $(( $(date +%s) - T0 ))"
  grep -E "^tests: [0-9]+ passed" "$O/run_full.log" | tail -1 | cut -c1-2000
  grep -E "^tests: .* (FAIL|SKIP)" "$O/run_full.log" | cut -c1-300
  cd "$T"; git status --porcelain > "$O/status-1.txt"
  diff "$O/status-0.txt" "$O/status-1.txt" > "$O/status-delta.txt" && log "suite left the tree status unchanged" || { log "suite changed the tree status:"; cat "$O/status-delta.txt"; }
  ( find v2/ecad/out $(ls -d v2/ecad/pcb-*/out) -type f -print0 | sort -z | xargs -0 sha256sum ) > "$O/evidence-1.sha256"
  cmp -s "$O/evidence-0.sha256" "$O/evidence-1.sha256" && log "evidence untouched through the suite" || { log "evidence moved during the suite:"; diff "$O/evidence-0.sha256" "$O/evidence-1.sha256" | head -30; }
  log "suite done $(date -u +%FT%TZ)"; touch "$W/suite-$(basename "$S").flag";;
clean-up)
  cd /root && rm -rf "$W" && echo "r8int3: removed $W"; df -h /root | tail -1;;
*) echo "usage: $0 setup|regen|set|suite <dir>|clean-up"; exit 2;;
esac
