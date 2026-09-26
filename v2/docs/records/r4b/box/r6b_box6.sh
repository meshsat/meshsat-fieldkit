#!/usr/bin/env bash
# MESHSAT-1357 round 6, board B author (r6b), RUN 6, 26 September 2026: the R4T-F9 pull-downs R514 to R517 on B's four
# EMCON-gate enables, the check_pcb_b.py property that holds them, and the O-18 integration set rebuilt on main faf8c981
# (boards C, D, E and P landed there). Runs on the KiCad box in /root/r6/b only; the box's main clone is read, never written.
# QUESTIONS:
#  (1) tclean: main faf8c981 as committed: rules_render/decisions_render --check and assembly_set --checklist to a
#      scratch path (the reference refusals and the page main's own tool writes), then B regenerated with main's
#      generator, against the committed B files (the base of the netlist diff);
#  (2) t6: main + gen_sch_b.py + check_pcb_b.py: the schematic-phase gates, and check_pcb_b.py with pcbnew on the
#      committed B21 board as this pass, as fix-up pass 3 (720892ae) and as committed;
#  (3) tint: THE INTEGRATION TREE, main + the two files + drafts/sch_pages-popups-r5.patch, B regenerated in place,
#      then assembly_set --checklist (the tree's own page) and rules_render/decisions_render --check with a re-render
#      only where B's regeneration moves a page; the full suite once, with the tree status before and after;
#  (4) parity t6 against tint, and the regenerated netlist against main's committed one and fix-up pass 3's.
# Stop rule: a failing step is recorded and the script moves on; nothing is retried or fixed on the box.
set -uo pipefail
W=/root/r6/b; R=$W/repo; OUT=$W/out6; N=pcb-b-compute; BD=v2/ecad/pcb-b-compute-b19
MAIN=/root/gitlab/products/meshsat/meshsat-fieldkit
rm -rf "$OUT"; mkdir -p "$OUT"
exec > >(tee "$OUT/run.log") 2>&1
echo "r6b6: start $(date -u +%FT%TZ)"; df -h /root | tail -1 | sed "s/^/r6b6: disk /"
git -C "$MAIN" status --porcelain > "$OUT/main-status-before.txt"; git -C "$MAIN" rev-parse HEAD > "$OUT/main-head.txt"
[ -d "$R/.git" ] || git clone -q --shared --no-checkout /root/r4/b/repo "$R"
git -C "$R" fetch -q "$W/main-faf8c981.bundle" main:r6main 2>/dev/null || git -C "$R" fetch -q -f "$W/main-faf8c981.bundle" main:r6main
echo "r6b6: r6main = $(git -C "$R" rev-parse r6main)"
for t in tclean t6 tint; do [ -d "$W/$t" ] && git -C "$R" worktree remove --force "$W/$t"; done
git -C "$R" worktree prune
for t in tclean t6 tint; do git -C "$R" worktree add -q --detach "$W/$t" r6main; done
for t in t6 tint; do cp "$W/gen_sch_b.py" "$W/$t/v2/ecad/tools/gen_sch_b.py"; cp "$W/check_pcb_b.py" "$W/$t/v2/ecad/tools/check_pcb_b.py"; done
( cd "$W/tint" && git apply -p1 "$W/sch_pages-popups-r5.patch" && echo "r6b6: popup patch applied to tint" )
sha256sum "$W/gen_sch_b.py" "$W/check_pcb_b.py" "$W/check_pcb_b.pass3.py" "$W/sch_pages-popups-r5.patch" "$W/pass3.net" "$W/main-faf8c981.bundle" | tee "$OUT/staged.sha256"
for t in tclean t6 tint; do echo "r6b6: $t head $(git -C "$W/$t" rev-parse HEAD) status: $(git -C "$W/$t" status --porcelain | tr '\n' ' ')"; done

# (1a) the reference readings on main as committed, before anything is regenerated there
O=$OUT/tclean; mkdir -p "$O/v"
( cd "$W/tclean/v2/ecad/tools"
  VERDICT_DIR="$O/v" python3 rules_render.py --check > "$O/rules_render_check.log" 2>&1; echo "r6b6: tclean rules_render --check exit $?"; tail -4 "$O/rules_render_check.log"
  VERDICT_DIR="$O/v" python3 decisions_render.py --check > "$O/decisions_render_check.log" 2>&1; echo "r6b6: tclean decisions_render --check exit $?"; tail -3 "$O/decisions_render_check.log"
  VERDICT_DIR="$O/v" python3 assembly_set.py --checklist "$O/ROTATION-CHECKLIST.clean.md" > "$O/assembly_set.log" 2>&1; echo "r6b6: tclean assembly_set --checklist exit $?"; tail -1 "$O/assembly_set.log" )
cmp -s "$O/ROTATION-CHECKLIST.clean.md" "$W/tclean/v2/release/revA/order/ROTATION-CHECKLIST.md" && echo "r6b6: main's tool rewrites main's committed checklist byte for byte" || echo "r6b6: WARNING main's tool does not reproduce main's checklist"
git -C "$W/tclean" status --porcelain > "$O/status-after-checks.txt"; echo "r6b6: tclean status after the checks: $(tr '\n' ' ' < "$O/status-after-checks.txt")"

regen() {  # $1 = tree label: footprint generators, gen_sch_b.py, build_sch.sh, artefacts copied to $OUT/<label>/regen
  local L=$1 E=$W/$1/v2/ecad; local D=$E/pcb-b-compute-b19 O=$OUT/$1; mkdir -p "$O/regen" "$O/v"
  cd "$D" || { echo "r6b6: $L no board dir"; return; }
  : > "$O/regen/gen_fp.log"; for g in gen_footprints_b16.py gen_footprints_idc.py; do python3 "../tools/$g" ../meshsat.pretty >> "$O/regen/gen_fp.log" 2>&1 || echo "r6b6: $L footprint generator $g FAILED"; done
  git -C "$W/$L" status --porcelain -- v2/ecad/meshsat.pretty > "$O/regen/fp-status.txt"; echo "r6b6: $L meshsat.pretty after the footprint generators: $(wc -l < "$O/regen/fp-status.txt") changed"
  python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" ../tools/gen_sch_b.py && echo "r6b6: $L compiles"
  python3 ../tools/tests/test_swallowed_calls.py ../tools/gen_sch_b.py > "$O/regen/swallowed.log" 2>&1; echo "r6b6: $L swallowed-calls exit $?"
  PHASE=B21 python3 ../tools/gen_sch_b.py "$N.kicad_sch" "$N" > "$O/regen/gen_sch.log" 2>&1; echo "r6b6: $L gen_sch exit $?"; tail -3 "$O/regen/gen_sch.log"
  rm -f "out/$N.net"
  bash ../tools/build_sch.sh . "$N" > "$O/regen/build_sch.log" 2>&1; echo "r6b6: $L build_sch exit $?"; grep -v "Syntax Error" "$O/regen/build_sch.log"; grep -c "Syntax Error" "$O/regen/build_sch.log" | sed "s/^/r6b6: $L poppler errors: /"
  for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "out/$N-bom.csv" "out/$N-erc.json" "out/$N-erc.rpt" "out/$N-schematic.pdf"; do
    [ -s "$f" ] && cp "$f" "$O/regen/" || echo "r6b6: $L missing $f"
  done
  mutool info "$O/regen/$N-schematic.pdf" 2>/dev/null | grep "^Pages" | sed "s/^/r6b6: $L paged schematic /"
}
gates() {  # $1 = tree label: the schematic-phase gates, verdicts outside the tree
  local L=$1 E=$W/$1/v2/ecad; local D=$E/pcb-b-compute-b19 O=$OUT/$1
  cd "$D" || return
  local NET="$D/out/$N.net" INT="$D/out/$N-intent.json"
  VERDICT_DIR="$O/v" python3 ../tools/erc_gate.py . "$N" > "$O/v/erc_gate.log" 2>&1; echo "r6b6: $L SCH-001 erc_gate exit $?"; tail -1 "$O/v/erc_gate.log"
  run() { local name=$1; shift; VERDICT_DIR="$O/v" "$@" > "$O/v/$name.log" 2>&1; echo "r6b6: $L $name exit $?"; tail -1 "$O/v/$name.log"; }
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
}

# (1b) main's own generator on main: the base the netlist diff is taken against
regen tclean
C=$W/tclean/v2/ecad/tools/regen_compare.py
pair() { python3 "$C" pair "$1" "$2" "$3" > "$4" 2>&1; echo "r6b6: $5 $1 exit $? $(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('verdict') or d.get('status') or list(d)[:4])" "$4" 2>/dev/null)"; }
for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json"; do git -C "$W/tclean" show "HEAD:$BD/$f" > "$OUT/committed-$(basename "$f")"; done
for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json; do
  kind=${k%%:*}; f=${k#*:}; pair "$kind" "$OUT/committed-$f" "$OUT/tclean/regen/$f" "$OUT/parity_${kind}_committed_tclean.json" "main's generator on faf8c981 against the committed B21 files"
done
git -C "$W/tclean" status --porcelain > "$O/status-after-regen.txt"

# (2) this pass on main: the gates, and the board gate with pcbnew on the committed B21 board
regen t6; gates t6
O=$OUT/t6; T=$W/t6/v2/ecad/tools
cd "$W/t6/$BD" && {
  git -C "$W/t6" show HEAD:v2/ecad/tools/check_pcb_b.py > "$O/v/check_pcb_b.committed.py"
  cp "$O/v/check_pcb_b.committed.py" "$T/check_pcb_b_committed_r6b.py"; cp "$W/check_pcb_b.pass3.py" "$T/check_pcb_b_pass3_r6b.py"
  git -C "$W/t6" show "HEAD:$BD/$N.kicad_pcb" | cmp -s - "$N.kicad_pcb" && echo "r6b6: t6 board file = committed B21"
  mkdir -p "$O/v/cpb-edited" "$O/v/cpb-committed" "$O/v/cpb-pass3"
  VERDICT_DIR="$O/v/cpb-edited" python3 ../tools/check_pcb_b.py "$N.kicad_pcb" > "$O/v/check_pcb_b.edited.log" 2>&1; echo "r6b6: t6 check_pcb_b (this pass) on B21 exit $?"; tail -2 "$O/v/check_pcb_b.edited.log"
  VERDICT_DIR="$O/v/cpb-pass3" python3 ../tools/check_pcb_b_pass3_r6b.py "$N.kicad_pcb" > "$O/v/check_pcb_b.pass3.log" 2>&1; echo "r6b6: t6 check_pcb_b (pass 3) on B21 exit $?"; tail -2 "$O/v/check_pcb_b.pass3.log"
  VERDICT_DIR="$O/v/cpb-committed" python3 ../tools/check_pcb_b_committed_r6b.py "$N.kicad_pcb" > "$O/v/check_pcb_b.committed.log" 2>&1; echo "r6b6: t6 check_pcb_b (committed) on B21 exit $?"; tail -2 "$O/v/check_pcb_b.committed.log"
  rm -f "$T/check_pcb_b_committed_r6b.py" "$T/check_pcb_b_pass3_r6b.py"
  for k in edited pass3 committed; do grep "^FAIL" "$O/v/check_pcb_b.$k.log" | sort > "$O/v/fails.$k.txt"; done
  comm -13 "$O/v/fails.pass3.txt" "$O/v/fails.edited.txt" > "$O/v/new_vs_pass3.txt"; comm -23 "$O/v/fails.pass3.txt" "$O/v/fails.edited.txt" > "$O/v/lost_vs_pass3.txt"
  comm -23 "$O/v/fails.committed.txt" "$O/v/fails.edited.txt" > "$O/v/lost_vs_committed.txt"
  wc -l "$O/v/fails.edited.txt" "$O/v/fails.pass3.txt" "$O/v/fails.committed.txt" "$O/v/new_vs_pass3.txt" "$O/v/lost_vs_pass3.txt" "$O/v/lost_vs_committed.txt" | sed "s/^/r6b6: /"
}
git -C "$W/t6" status --porcelain > "$O/tree-status.txt"

# (3) the integration tree: regenerated in place, then the generated pages, then the suite once
regen tint
O=$OUT/tint
for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json provenance:$N.net.prov.json bom:$N-bom.csv erc:$N-erc.json; do
  kind=${k%%:*}; f=${k#*:}; pair "$kind" "$OUT/t6/regen/$f" "$OUT/tint/regen/$f" "$OUT/parity_${kind}_t6_tint.json" "parity t6 vs tint"
done
cp "$W/pass3.net" "$OUT/pass3-9b85ada8.net"
pair netlist "$OUT/committed-$N.net" "$OUT/tint/regen/$N.net" "$OUT/regen_compare_committed_new.json" "committed B21 (faf8c981) vs this pass (DIFFERENT is intended)"
pair netlist "$OUT/pass3-9b85ada8.net" "$OUT/tint/regen/$N.net" "$OUT/regen_compare_pass3_new.json" "fix-up pass 3 vs this pass"
git -C "$W/tint" status --porcelain > "$O/status-0-after-regen.txt"; echo "r6b6: tint after regen: $(tr '\n' ' ' < "$O/status-0-after-regen.txt")"
( cd "$W/tint/v2/ecad/tools"
  VERDICT_DIR="$O/v" python3 assembly_set.py --checklist > "$O/assembly_set_checklist.log" 2>&1; echo "r6b6: tint assembly_set --checklist exit $?"; tail -1 "$O/assembly_set_checklist.log"
  VERDICT_DIR="$O/v" python3 rules_render.py --check > "$O/rules_render_check.log" 2>&1; echo "r6b6: tint rules_render --check exit $?"; tail -4 "$O/rules_render_check.log"
  VERDICT_DIR="$O/v" python3 decisions_render.py --check > "$O/decisions_render_check.log" 2>&1; echo "r6b6: tint decisions_render --check exit $?"; tail -3 "$O/decisions_render_check.log" )
diff <(grep -iv "verdict:" "$OUT/tclean/rules_render_check.log") <(grep -iv "verdict:" "$O/rules_render_check.log") > "$O/rules_render_check.delta" && echo "r6b6: rules_render --check reads the same on tint as on clean main" || { echo "r6b6: rules_render --check differs from clean main:"; cat "$O/rules_render_check.delta"; }
# a page tint refuses and clean main does not is moved by B's regeneration and is re-rendered (--no-refresh, as the
# round-5 integrator did for C, D, E and P); a page clean main refuses as well is not this round's and goes back to HEAD
_pages() { grep -o "docs/[A-Za-z0-9_.-]*\.md differs" "$1" | sed "s/ differs//" | sort -u; }
_mine=$(comm -13 <(_pages "$OUT/tclean/rules_render_check.log") <(_pages "$O/rules_render_check.log"))
if [ -n "$_mine" ]; then
  echo "r6b6: pages B's regeneration moves: $(echo $_mine)"
  ( cd "$W/tint/v2/ecad/tools" && VERDICT_DIR="$O/v" python3 rules_render.py --no-refresh > "$O/rules_render_write.log" 2>&1; echo "r6b6: tint rules_render --no-refresh exit $?"; cat "$O/rules_render_write.log" )
  for p in $(git -C "$W/tint" diff --name-only -- v2/docs); do
    echo "$_mine" | grep -qx "${p#v2/}" || { git -C "$W/tint" checkout -q -- "$p"; echo "r6b6: $p restored to HEAD (clean main refuses it too, not this round's)"; }
  done
  git -C "$W/tint" diff -- v2/docs > "$O/docs-rerender.diff"; git -C "$W/tint" diff --stat -- v2/docs | sed "s/^/r6b6: /"
  ( cd "$W/tint/v2/ecad/tools" && VERDICT_DIR="$O/v" python3 rules_render.py --check > "$O/rules_render_recheck.log" 2>&1; echo "r6b6: tint rules_render --check after the re-render exit $?"; cat "$O/rules_render_recheck.log" )
fi
diff <(grep -iv "verdict:" "$OUT/tclean/decisions_render_check.log") <(grep -iv "verdict:" "$O/decisions_render_check.log") > "$O/decisions_render_check.delta" && echo "r6b6: decisions_render --check reads the same on tint as on clean main" || { echo "r6b6: decisions_render --check differs from clean main:"; cat "$O/decisions_render_check.delta"; }
git -C "$W/tint" diff -- v2/release/revA/order/ROTATION-CHECKLIST.md > "$O/rotation-checklist.diff"; echo "r6b6: checklist diff:"; cat "$O/rotation-checklist.diff"
git -C "$W/tint" status --porcelain > "$O/status-1-before-suite.txt"; echo "r6b6: tint before the suite: $(tr '\n' ' ' < "$O/status-1-before-suite.txt")"
git -C "$W/tint" diff --stat | tail -1 | sed "s/^/r6b6: tint tracked diff /"
( cd "$W/tint/v2/ecad/tools" && timeout 2400 python3 tests/run.py > "$O/suite.log" 2>&1; echo "r6b6: suite tint exit $?" ); grep -E "^tests:" "$O/suite.log" | tail -1
grep -E " FAIL| ERROR|^FAIL|^ERROR" "$O/suite.log" | grep -v "^verdict:" | head -20
grep -iE "skip" "$O/suite.log" | head -20 > "$O/suite-skips.txt"
git -C "$W/tint" status --porcelain > "$O/status-2-after-suite.txt"
diff "$O/status-1-before-suite.txt" "$O/status-2-after-suite.txt" > "$O/status-suite-delta.txt" && echo "r6b6: the suite left the tint tree status unchanged" || { echo "r6b6: the suite changed the tint tree status:"; cat "$O/status-suite-delta.txt"; }
git -C "$W/tint" diff > "$O/tint-tracked.diff"; git -C "$W/tint" diff --stat > "$O/tint-tracked.stat"
for f in "$BD/$N.kicad_sch" "$BD/out/$N.net" "$BD/out/$N-intent.json" "$BD/out/$N.net.prov.json" v2/release/revA/order/ROTATION-CHECKLIST.md v2/ecad/tools/gen_sch_b.py v2/ecad/tools/check_pcb_b.py v2/ecad/tools/build_sch.sh v2/ecad/tools/sch_pages.py v2/ecad/tools/tests/test_schematic_pages.py; do
  mkdir -p "$O/set/$(dirname "$f")"; cp "$W/tint/$f" "$O/set/$f"
done
( cd "$O/set" && find . -type f -print0 | sort -z | xargs -0 sha256sum > ../set.sha256 ); echo "r6b6: integration set:"; cat "$O/set.sha256"

git -C "$MAIN" status --porcelain > "$OUT/main-status-after.txt"
cmp -s "$OUT/main-status-before.txt" "$OUT/main-status-after.txt" && echo "r6b6: main clone untouched" || echo "r6b6: WARNING main clone status changed"
( cd "$OUT" && find . -type f ! -name SHA256SUMS ! -name "*.pdf" ! -name run.log -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS )
df -h /root | tail -1 | sed "s/^/r6b6: disk /"
echo "r6b6: done $(date -u +%FT%TZ)"
