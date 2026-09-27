#!/usr/bin/env bash
# MESHSAT-1357 round 8, stream d (board D circuit corrections), 26 September 2026. Box 52646493, /root/r8-d ONLY.
# Two trees, both from a clone of the public mirror (github.com/meshsat/meshsat-fieldkit) at main fc144600, with real history:
#   base = /root/r8-d/base (a worktree at fc144600, untouched: main's generator against main's committed files, condition 5)
#   tree = /root/r8-d/repo (fc144600 + this stream's gen_sch_d.py)
# Main's gitignored evidence (v2/ecad/out and every pcb-*/out/routeflow, copied from the main checkout) is laid into both.
# Board D only: declared footprint generators, gen_sch_d.py with the committed schematic's Phase label, build_sch.sh,
# sch_prov.py write, erc_gate and every schematic-phase gate with VERDICT_DIR under /root/r8-d/out. No routing, no placement.
set -uo pipefail
W=/root/r8-d; IN=$W/incoming; T=$W/repo; B=$W/base; OUT=$W/out
mkdir -p "$OUT"; export TMPDIR=$W/tmp; mkdir -p "$TMPDIR"
exec > >(tee -a "$OUT/regen.log") 2>&1
echo "r8d-regen: start $(date -u +%FT%TZ)"
( cd "$IN" && sha256sum evidence.tgz gen_sch_d.py r8d_*.sh t/* ) | tee "$OUT/incoming-sha256.txt"
kicad-cli version; python3 --version
# ONLY=new re-runs the tree's side alone (the base side's outputs in out/base stand); the tree is first put back to
# fc144600's files for board D, so every regeneration starts from main's committed artefacts.
if [ "${ONLY:-}" = new ]; then TREES="$T"; git -C "$T" checkout -- v2/ecad/pcb-d-aprs-d9 v2/ecad/tools/gen_sch_d.py; rm -rf "$OUT/new" "$OUT/new2"; else TREES="$T $B"; fi
for R in $TREES; do
  [ "$(git -C "$R" rev-parse HEAD)" = fc144600544c005c280d6614d26a94dfd3f88511 ] || { echo "STOP $R HEAD is not fc144600"; exit 2; }
  [ -z "$(git -C "$R" status --porcelain)" ] || { echo "STOP $R is not clean"; git -C "$R" status --porcelain | head; exit 2; }
  ( cd "$R" && tar -xzf "$IN/evidence.tgz" ) || { echo "STOP evidence $R"; exit 3; }
  ( cd "$R" && find v2/ecad/out $(ls -d v2/ecad/pcb-*/out/routeflow) -type f -print0 | sort -z | xargs -0 sha256sum ) > "$OUT/evidence-$(basename $R)-0.sha256"
  echo "r8d: $(basename $R) HEAD $(git -C "$R" rev-parse --short=8 HEAD), commits $(git -C "$R" rev-list --count HEAD), evidence files $(wc -l < "$OUT/evidence-$(basename $R)-0.sha256")"
done
cp "$IN/gen_sch_d.py" "$T/v2/ecad/tools/gen_sch_d.py"
cmp -s "$IN/gen_sch_d.py" "$T/v2/ecad/tools/gen_sch_d.py" && echo "r8d: overlay gen_sch_d.py in place, sha256 $(sha256sum "$IN/gen_sch_d.py" | cut -c1-16)"
git -C "$T" status --porcelain | tee "$OUT/tree-status-0.txt"
df -h /root | tail -1
N=pcb-d-aprs; DD=pcb-d-aprs-d9; L=d
regen_one () {  # $1 tree root, $2 out dir, $3 "ref" to keep the committed artefacts and kicad-cli's exports of the COMMITTED schematic
  local R=$1 O=$2; local E=$R/v2/ecad; local D=$E/$DD
  mkdir -p "$O/v" "$O/files"
  cd "$D" || { echo "r8d: no $D"; return 2; }
  local LABEL; LABEL=$(grep -m1 -o '(comment 1 "Phase [A-Za-z0-9]*' "$N.kicad_sch" | sed 's/.*Phase //'); echo "$LABEL" > "$O/phase.txt"
  if [ "${3:-}" = ref ]; then
    mkdir -p "$O/ref"; cp "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "$O/ref/"
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "$O/ref/$N-bom.csv" "$N.kicad_sch" > /dev/null 2>&1
    kicad-cli sch erc --severity-all --format json -o "$O/ref/$N-erc.json" "$N.kicad_sch" > /dev/null 2>&1
  fi
  python3 "$E/tools/sch_prov.py" read "out/$N.net" "$L" > "$O/prov-before.txt" 2>&1; echo "exit $?" >> "$O/prov-before.txt"
  sha256sum ../tools/gen_sch_$L.py ../tools/kisch.py ../tools/intent.py ../tools/schlayout.py > "$O/generator.sha256"
  : > "$O/gen_fp.log"
  for g in $(python3 -c "import json;print(' '.join(json.load(open('$E/tools/boards/$L.json')).get('footprint_generator') or []))"); do
    python3 "../tools/$g" ../meshsat.pretty >> "$O/gen_fp.log" 2>&1 || echo "footprint generator $g FAILED" >> "$O/gen_fp.log"
  done
  local GENV; GENV="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])).get('gen_env') or {}; print(' '.join('%s=%s' % (k, v) for k, v in d.items()))" "$E/tools/boards/$L.json")"
  echo "gen_env: [$GENV] PHASE=$LABEL" > "$O/gen_sch.log"
  PHASE="$LABEL" env $GENV python3 ../tools/gen_sch_$L.py "$N.kicad_sch" "$N" >> "$O/gen_sch.log" 2>&1; local GE=$?; echo "gen_sch exit $GE" >> "$O/gen_sch.log"
  if [ $GE -ne 0 ]; then echo "r8d: STOP generation failed in $(basename $R)"; tail -20 "$O/gen_sch.log"; return 3; fi
  rm -f "out/$N.net" "out/$N-bom.csv" "out/$N.net.prov.json"
  bash ../tools/build_sch.sh . "$N" > "$O/build_sch.log" 2>&1; echo "build_sch exit $?" >> "$O/build_sch.log"
  if [ ! -s "out/$N-bom.csv" ]; then
    echo "BOM exported by hand (build_sch.sh stopped before its BOM line)" >> "$O/build_sch.log"
    kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "out/$N-bom.csv" "$N.kicad_sch" >> "$O/build_sch.log" 2>&1
  fi
  python3 "$E/tools/sch_prov.py" write "out/$N.net" "$L" > "$O/sch_prov_write.txt" 2>&1; echo "exit $?" >> "$O/sch_prov_write.txt"
  python3 "$E/tools/sch_prov.py" read "out/$N.net" "$L" > "$O/prov-after.txt" 2>&1; echo "exit $?" >> "$O/prov-after.txt"
  local NET="out/$N.net" INT="out/$N-intent.json"
  run () { local nm=$1; shift; VERDICT_DIR="$O/v" timeout 1800 "$@" > "$O/v/$nm.log" 2>&1; echo "exit $?" >> "$O/v/$nm.log"; }
  run erc_gate python3 ../tools/erc_gate.py . "$N"
  run port_protect python3 ../tools/port_protect.py "$NET"
  run pin_map_lands python3 ../tools/pin_map_lands.py "$NET" "$L"
  run derate python3 ../tools/derate.py "$NET" --intent "$INT"
  run safe_lines python3 ../tools/safe_lines.py "$NET"
  run power_sequence python3 ../tools/power_sequence.py "$NET" --intent "$INT"
  run power_path python3 ../tools/power_path.py "$NET" --intent "$INT" --out-dir "$O/v"
  run clock_check python3 ../tools/clock_check.py "$NET"
  run ground_system python3 ../tools/ground_system.py "$NET" --board "$L"
  run review_nets python3 ../tools/review_nets.py "$NET"
  run emc_sheet python3 ../tools/emc_sheet.py --ecad "$E" --board "$L"
  run reliability python3 ../tools/reliability.py --ecad "$E" --board "$L"
  run switch_list python3 ../tools/switch_list.py "$NET" "$N.kicad_pcb" "$INT" --board "$L"
  run netlist_board python3 ../tools/netlist_board.py "$N.kicad_pcb" "$NET"
  run netlist_parts python3 ../tools/netlist_parts.py "$N.kicad_pcb" "$NET" --out-dir "$O/v"
  run interfaces python3 ../tools/interfaces.py "$N.kicad_pcb" --board "$L"
  for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "out/$N-bom.csv" "out/$N-erc.json" "out/$N-erc.rpt" "out/$N-schematic.pdf"; do
    [ -s "$f" ] && cp "$f" "$O/files/" || echo "missing: $f" >> "$O/missing.txt"
  done
  echo "r8d: $(basename "$R") phase $LABEL gen:$(tail -1 "$O/gen_sch.log") build:$(tail -1 "$O/build_sch.log") $(date -u +%T)"
}
if [ "${ONLY:-}" != new ]; then ( regen_one "$B" "$OUT/base" ref ) > "$OUT/regen-base.log" 2>&1 & PB=$!; fi
( regen_one "$T" "$OUT/new" ) > "$OUT/regen-new.log" 2>&1 &
PN=$!
[ "${ONLY:-}" != new ] && wait $PB; wait $PN
cat "$OUT/regen-base.log" "$OUT/regen-new.log"
# determinism: the tree's generator a second time, into a throwaway copy of the board directory
mkdir -p "$OUT/new2"; rm -rf "$W/det"; mkdir -p "$W/det"
cp -a "$T/v2/ecad/$DD" "$W/det/$DD"; ln -s "$T/v2/ecad/tools" "$W/det/tools"; ln -s "$T/v2/ecad/meshsat.pretty" "$W/det/meshsat.pretty"
( cd "$W/det/$DD" && PHASE="$(cat "$OUT/new/phase.txt")" python3 ../tools/gen_sch_d.py "$N.kicad_sch" "$N" > "$OUT/new2/gen_sch.log" 2>&1; echo "exit $?" >> "$OUT/new2/gen_sch.log"
  rm -f "out/$N.net"; kicad-cli sch export netlist --format kicadsexpr -o "out/$N.net" "$N.kicad_sch" > /dev/null 2>&1
  cp "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "$OUT/new2/" )
for f in $N.kicad_sch $N.net $N-intent.json; do printf "determinism %s: %s\n" "$f" "$(cmp -s "$OUT/new/files/$f" "$OUT/new2/$f" && echo IDENTICAL || echo differs)"; done
git -C "$T" status --porcelain > "$OUT/tree-status-1.txt"; echo "== tree status"; cat "$OUT/tree-status-1.txt"
git -C "$B" status --porcelain > "$OUT/base-status-1.txt"; echo "== base status"; cat "$OUT/base-status-1.txt"
for R in $TREES; do ( cd "$R" && find v2/ecad/out $(ls -d v2/ecad/pcb-*/out/routeflow) -type f -print0 | sort -z | xargs -0 sha256sum ) > "$OUT/evidence-$(basename $R)-1.sha256"
  cmp -s "$OUT/evidence-$(basename $R)-0.sha256" "$OUT/evidence-$(basename $R)-1.sha256" && echo "r8d: $(basename $R) evidence untouched by the regeneration and its gates" || { echo "r8d: WARNING $(basename $R) evidence moved:"; diff "$OUT/evidence-$(basename $R)-0.sha256" "$OUT/evidence-$(basename $R)-1.sha256" | head -20; }; done
df -h /root | tail -1
echo "r8d-regen: done $(date -u +%FT%TZ)"
touch "$W/regen.flag"
