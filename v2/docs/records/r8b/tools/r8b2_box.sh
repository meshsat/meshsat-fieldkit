#!/usr/bin/env bash
# MESHSAT-1357 round 8, board B author (stream b), PASS 2, box script. Works only under /root/r8-b; never touches /root/gitlab,
# /root/besc1 or /root/hpack. Modes:
#   setup  : clone main fc144600 from the uploaded bundle (real history), worktrees tclean (main as committed) and t8 (main +
#            this stream's commit set), main's gitignored evidence into both
#   clean  : tclean: main's generator and build_sch.sh; parity against main's committed B files
#   t8     : t8: the same chain with this stream's files; ERC and the schematic-phase gates into scratch verdict dirs;
#            the independent netlist comparison against main's committed netlist and against tclean's
#   sim    : the break-before-make simulation on main's, the first pass's and this netlist
#   suite  : the full suite once on t8 (exactly the commit set), tree status before and after
#   apply  : t8d = main + the commit set + every draft + the five maker documents filed + the requirements rebound, committed in
#            the scratch clone; generated pages rendered and committed; the full suite once on it; the regenerated patches
#   clean-up: remove /root/r8-b
set -uo pipefail
W=/root/r8-b; IN=$W/incoming; OUT=$W/out; N=pcb-b-compute; BD=v2/ecad/pcb-b-compute-b19
FC=fc144600544c005c280d6614d26a94dfd3f88511
mkdir -p "$OUT"
mode=${1:-}
log() { echo "r8b2: $*"; }
COMMITSET="v2/ecad/tools/gen_sch_b.py v2/ecad/tools/boards/b.json v2/ecad/meshsat.pretty/M2_B-Key_Socket_3052_TE2199119.kicad_mod $BD/$N.kicad_sch $BD/out/$N.net $BD/out/$N-intent.json $BD/out/$N.net.prov.json"
case "$mode" in
setup)
  exec > >(tee "$OUT/setup.log") 2>&1
  log "start $(date -u +%FT%TZ)"; df -h /root | tail -1
  sha256sum "$W/main-fc144600.bundle" | tee "$OUT/bundle.sha256"
  git bundle list-heads "$W/main-fc144600.bundle" | tee "$OUT/bundle.heads"
  rm -rf "$W/repo" "$W/tclean" "$W/t8" "$W/t8d"
  git clone -q --no-checkout "$W/main-fc144600.bundle" "$W/repo" && log "cloned"
  git -C "$W/repo" branch -f r8main $FC
  log "r8main = $(git -C "$W/repo" rev-parse r8main)"
  for t in tclean t8; do git -C "$W/repo" worktree add -q --detach "$W/$t" r8main; done
  for t in tclean t8; do tar xzf "$IN/evidence.tgz" -C "$W/$t"; log "$t head $(git -C "$W/$t" rev-parse HEAD) status $(git -C "$W/$t" status --porcelain | wc -l)"; done
  cp "$IN/gen_sch_b.py" "$W/t8/v2/ecad/tools/gen_sch_b.py"; cp "$IN/b.json" "$W/t8/v2/ecad/tools/boards/b.json"
  cp "$IN/M2_B-Key_Socket_3052_TE2199119.kicad_mod" "$W/t8/v2/ecad/meshsat.pretty/"
  sha256sum "$IN"/gen_sch_b.py "$IN"/b.json "$IN"/*.kicad_mod | tee "$OUT/staged.sha256"
  git -C "$W/t8" status --porcelain | tee "$OUT/t8-status-staged.txt"
  df -h /root | tail -1; log "done $(date -u +%FT%TZ)";;
clean|t8)
  L=$mode; T=$W/$L; O=$OUT/$L; rm -rf "$O"; mkdir -p "$O/regen" "$O/v"
  exec > >(tee "$O/run.log") 2>&1
  [ "$L" = clean ] && T=$W/tclean
  log "$L start $(date -u +%FT%TZ) in $T"
  D=$T/$BD; cd "$D" || exit 2
  : > "$O/regen/gen_fp.log"; for g in gen_footprints_b16.py gen_footprints_idc.py; do python3 "../tools/$g" ../meshsat.pretty >> "$O/regen/gen_fp.log" 2>&1 || log "$L footprint generator $g FAILED"; done
  git -C "$T" status --porcelain -- v2/ecad/meshsat.pretty > "$O/regen/fp-status.txt"; log "$L meshsat.pretty after the generators: $(tr '\n' ' ' < "$O/regen/fp-status.txt")"
  python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" ../tools/gen_sch_b.py && log "$L compiles"
  python3 ../tools/tests/test_swallowed_calls.py ../tools/gen_sch_b.py > "$O/regen/swallowed.log" 2>&1; log "$L swallowed-calls exit $? $(tail -1 "$O/regen/swallowed.log")"
  PHASE=B21 python3 ../tools/gen_sch_b.py "$N.kicad_sch" "$N" > "$O/regen/gen_sch.log" 2>&1; log "$L gen_sch exit $?"; tail -4 "$O/regen/gen_sch.log"
  rm -f "out/$N.net"
  bash ../tools/build_sch.sh . "$N" > "$O/regen/build_sch.log" 2>&1; log "$L build_sch exit $?"; grep -v "Syntax Error" "$O/regen/build_sch.log" | tail -8
  for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "out/$N-bom.csv" "out/$N-erc.json" "out/$N-erc.rpt" "out/$N-schematic.pdf"; do
    [ -s "$f" ] && cp "$f" "$O/regen/" || log "$L missing $f"
  done
  mutool info "$O/regen/$N-schematic.pdf" 2>/dev/null | grep "^Pages" | sed "s/^/r8b2: $L paged schematic /"
  NET="$D/out/$N.net"; INT="$D/out/$N-intent.json"; E=$T/v2/ecad
  VERDICT_DIR="$O/v" python3 ../tools/erc_gate.py . "$N" > "$O/v/erc_gate.log" 2>&1; log "$L SCH-001 erc_gate exit $?"; tail -3 "$O/v/erc_gate.log"
  run() { local name=$1; shift; VERDICT_DIR="$O/v" "$@" > "$O/v/$name.log" 2>&1; log "$L $name exit $?  $(tail -1 "$O/v/$name.log")"; }
  run safe_lines python3 ../tools/safe_lines.py "$NET"
  run pin_map_lands python3 ../tools/pin_map_lands.py "$NET" b
  run derate python3 ../tools/derate.py "$NET" --intent "$INT"
  run power_sequence python3 ../tools/power_sequence.py "$NET" --intent "$INT"
  run power_path python3 ../tools/power_path.py "$NET" --intent "$INT" --out-dir "$O/v"
  run port_protect python3 ../tools/port_protect.py "$NET"
  run clock_check python3 ../tools/clock_check.py "$NET"
  run review_nets python3 ../tools/review_nets.py "$NET"
  run check_contracts python3 ../tools/check_contracts.py "$E"
  run energy_chain python3 ../tools/energy_chain.py --ecad "$E"
  run netlist_board python3 ../tools/netlist_board.py "$N.kicad_pcb" "$NET"
  run netlist_parts python3 ../tools/netlist_parts.py "$N.kicad_pcb" "$NET" --out-dir "$O/v"
  if [ "$L" = clean ]; then
    for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json"; do git -C "$T" show "HEAD:$BD/$f" > "$OUT/committed-$(basename "$f")"; done
    C=$T/v2/ecad/tools/regen_compare.py
    for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json; do kind=${k%%:*}; f=${k#*:}
      python3 "$C" pair "$kind" "$OUT/committed-$f" "$O/regen/$f" > "$OUT/parity_${kind}_committed_clean.json" 2>&1
      log "parity committed vs clean $kind: $(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('result') or d.get('verdict') or d.get('status'))" "$OUT/parity_${kind}_committed_clean.json" 2>/dev/null)"; done
  else
    python3 "$IN/netdiff_r8b.py" "$OUT/committed-$N.net" "$O/regen/$N.net" --out "$OUT/netdiff_committed_t8.json" | sed "s/^/r8b2: committed vs t8 /"
    python3 "$IN/netdiff_r8b.py" "$OUT/clean/regen/$N.net" "$O/regen/$N.net" --out "$OUT/netdiff_clean_t8.json" | sed "s/^/r8b2: clean vs t8 /"
    python3 "$IN/netdiff_r8b.py" "$IN/pass1.net" "$O/regen/$N.net" --out "$OUT/netdiff_pass1_t8.json" | sed "s/^/r8b2: pass-1 vs t8 /"
    python3 "$IN/netdiff_r8b.py" "$OUT/committed-$N.net" "$O/regen/$N.net" --expect "$IN/expected_r8b.json" --out "$OUT/netdiff_expected.json" > "$OUT/netdiff_expected.txt"; log "expected-set comparison exit $?"; head -40 "$OUT/netdiff_expected.txt"
  fi
  git -C "$T" status --porcelain > "$O/tree-status.txt"; log "$L tree status: $(wc -l < "$O/tree-status.txt") entries"; cat "$O/tree-status.txt"
  log "$L done $(date -u +%FT%TZ)";;
sim)
  O=$OUT/sim; mkdir -p "$O"; exec > >(tee "$O/run.log") 2>&1
  log "sim start $(date -u +%FT%TZ)"
  python3 "$IN/bbm_sim_r8b.py" --bounds > "$O/bounds.json"; log "bounds exit $?"; grep -E "min|traversal" "$O/bounds.json"
  for spec in main:$OUT/committed-$N.net pass1:$IN/pass1.net pass2:$OUT/t8/regen/$N.net; do nm=${spec%%:*}; f=${spec#*:}
    for hz in "" "--hazard"; do tag=$nm${hz:+-hazard}
      timeout 3000 python3 "$IN/bbm_sim_r8b.py" "$f" --runs 1500 --seed 27 $hz --json "$O/$tag.json" > "$O/$tag.txt" 2>&1; log "$tag exit $?"; cat "$O/$tag.txt"
    done
  done
  log "sim done $(date -u +%FT%TZ)";;
suite)
  T=$W/t8; O=$OUT/suite; mkdir -p "$O"
  exec > >(tee "$O/run.log") 2>&1
  log "suite start $(date -u +%FT%TZ) head $(git -C "$T" rev-parse HEAD)"
  git -C "$T" status --porcelain > "$O/status-before.txt"; git -C "$T" diff --stat | tail -1
  ( cd "$T/v2/ecad/tools" && timeout 3000 python3 tests/run.py > "$O/suite.log" 2>&1; echo "r8b2: suite exit $?" )
  grep -E "^tests:" "$O/suite.log" | tail -1
  git -C "$T" status --porcelain > "$O/status-after.txt"
  diff "$O/status-before.txt" "$O/status-after.txt" > "$O/status-delta.txt" && log "the suite left the tree status unchanged" || { log "tree status changed:"; cat "$O/status-delta.txt"; }
  log "suite done $(date -u +%FT%TZ)";;
apply)
  T=$W/t8d; O=$OUT/apply; mkdir -p "$O"
  exec > >(tee "$O/apply.log") 2>&1
  log "apply start $(date -u +%FT%TZ)"; df -h /root | tail -1
  [ -d "$T" ] && git -C "$W/repo" worktree remove --force "$T"; git -C "$W/repo" worktree prune
  git -C "$W/repo" worktree add -q --detach "$T" r8main
  for f in $COMMITSET; do cp "$W/t8/$f" "$T/$f"; done
  tar xzf "$IN/evidence.tgz" -C "$T"
  rm -rf "$W/drafts"; mkdir -p "$W/drafts" && tar xzf "$IN/drafts.tgz" -C "$W/drafts"
  cd "$T"
  for p in "$W"/drafts/b/*.patch; do
    case "$(basename "$p")" in pcb_requirements-r8.patch|generated-pages-r8.patch) continue;; esac
    git apply "$p" && log "applied $(basename "$p")" || log "NOT APPLIED $(basename "$p")"
  done
  # the five maker documents, filed where drafts/b/datasheets/SOURCES.txt names them
  python3 - "$W/drafts/b/datasheets" "$T" <<'PY'
import re, shutil, sys, os, hashlib
src, tree = sys.argv[1], sys.argv[2]
sums = dict(l.split()[::-1] for l in open(os.path.join(src, "SHA256SUMS")) if l.strip())
for m in re.finditer(r"^(\S+\.pdf)\s+->\s+(\S+)$", open(os.path.join(src, "SOURCES.txt")).read(), re.M):
    a, b = m.group(1), m.group(2); d = os.path.join(tree, b); os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copyfile(os.path.join(src, a), d)
    h = hashlib.sha256(open(d, "rb").read()).hexdigest()
    print("r8b2: filed %s -> %s sha256 %s %s" % (a, b, h[:16], "matches SHA256SUMS" if sums.get(a) == h else "MISMATCH"))
PY
  python3 "$W/drafts/b/tools/rebind_r8b.py" "$T" | tail -2
  git -C "$T" diff -- v2/ecad/tools/pcb_requirements.yaml > "$O/pcb_requirements-r8.patch"; log "requirements patch $(wc -l < "$O/pcb_requirements-r8.patch") lines"
  cd "$T/v2/ecad/tools"
  python3 rules_lib.py requirements > "$O/requirements.log" 2>&1; log "rules_lib requirements exit $? $(grep -v '^warn' "$O/requirements.log" | tail -1)"
  git -C "$T" add -A && git -C "$T" -c user.name=r8b2-scratch -c user.email=r8b2@scratch commit -q -m "r8b2 scratch: commit set, drafts, maker documents, requirements rebound" && log "inputs committed $(git -C "$T" rev-parse --short HEAD)"
  for i in 1 2 3; do
    python3 rules_status.py > "$O/rules_status.$i.log" 2>&1; log "rules_status pass $i exit $?"
    python3 rules_render.py > "$O/rules_render.$i.log" 2>&1; log "rules_render pass $i exit $?"
    python3 rules_render.py --requirements > "$O/req_render.$i.log" 2>&1; log "rules_render --requirements pass $i exit $?"
    python3 rules_render.py --check > "$O/check.$i.log" 2>&1 && { log "rules_render --check exit 0 after pass $i"; break; } || log "rules_render --check refused after pass $i"
  done
  python3 rules_render.py --requirements --check > "$O/req-check.log" 2>&1; log "rules_render --requirements --check exit $?"
  python3 decisions_render.py --check > "$O/dec-check.log" 2>&1; log "decisions_render --check exit $?"
  git -C "$T" diff -- v2/docs > "$O/generated-pages-r8.patch"; log "generated pages diff $(wc -l < "$O/generated-pages-r8.patch") lines: $(git -C "$T" diff --name-only -- v2/docs | tr '\n' ' ')"
  git -C "$T" add -A && git -C "$T" -c user.name=r8b2-scratch -c user.email=r8b2@scratch commit -q -m "r8b2 scratch: generated pages" && log "pages committed $(git -C "$T" rev-parse --short HEAD)"
  git -C "$T" diff --stat r8main HEAD | tail -1 | sed "s/^/r8b2: candidate against main: /"
  mkdir -p "$O/v"
  VERDICT_DIR="$O/v" python3 check_contracts.py "$T/v2/ecad" > "$O/v/check_contracts.log" 2>&1; log "check_contracts exit $?  $(grep '^verdict' "$O/v/check_contracts.log" | tr '\n' ' ')"
  VERDICT_DIR="$O/v" python3 energy_chain.py --ecad "$T/v2/ecad" > "$O/v/energy_chain.log" 2>&1; log "energy_chain exit $?  $(grep '^verdict' "$O/v/energy_chain.log" | tr '\n' ' ')"
  git -C "$T" status --porcelain > "$O/status-before.txt"
  ( timeout 3000 python3 tests/run.py > "$O/suite.log" 2>&1; echo "r8b2: suite exit $?" )
  grep -E "^tests:" "$O/suite.log" | tail -1
  git -C "$T" status --porcelain > "$O/status-after.txt"
  diff "$O/status-before.txt" "$O/status-after.txt" > "$O/status-delta.txt" && log "the suite left the tree status unchanged" || { log "tree status changed:"; cat "$O/status-delta.txt"; }
  log "apply done $(date -u +%FT%TZ)";;
clean-up)
  rm -rf "$W" && echo "r8b2: removed $W"; df -h /root | tail -1;;
*) echo "usage: $0 setup|clean|t8|sim|suite|apply|clean-up"; exit 2;;
esac
