#!/usr/bin/env bash
# MESHSAT-1357 round 8 stream d, phase 3: the tree holds EXACTLY this stream's commit set (gen_sch_d.py and board D's
# regenerated schematic, netlist, intent and sidecar) on main fc144600 with its real history; the generated pages are
# re-rendered to SEE what they would move (kept as drafts, then put back: they are not this stream's files); then
# rules_render/decisions_render --check and the full suite once. /root/r8-d ONLY.
set -uo pipefail
W=/root/r8-d; T=$W/repo; B=$W/base; OUT=$W/out; O=$OUT/suite; mkdir -p "$O/v" "$O/vb"
export TMPDIR=$W/tmp; mkdir -p "$TMPDIR"
exec > >(tee -a "$O/suite-run.log") 2>&1
echo "r8d-suite: start $(date -u +%FT%TZ)"
git -C "$B" checkout -- v2/ecad/pcb-d-aprs-d9 && echo "base: board D put back to main's committed files"; git -C "$B" status --porcelain
cd "$T"
git status --porcelain > "$O/status-0.txt"; cat "$O/status-0.txt"
EXPECT="v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net.prov.json v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_sch v2/ecad/tools/gen_sch_d.py"
[ "$(git status --porcelain | awk '{print $2}' | sort | tr '\n' ' ')" = "$(echo $EXPECT | tr ' ' '\n' | sort | tr '\n' ' ')" ] && echo "commit set: exactly the five files" || { echo "STOP: the tree is not exactly the commit set"; exit 2; }
for f in $EXPECT; do sha256sum "$f"; done | tee "$O/commit-set.sha256"
( cd "$B/v2/ecad/tools" && VERDICT_DIR="$O/vb" python3 rules_render.py --check > "$O/base_rules_render_check.log" 2>&1; echo "exit $?" >> "$O/base_rules_render_check.log" )
( cd "$B/v2/ecad/tools" && VERDICT_DIR="$O/vb" python3 decisions_render.py --check > "$O/base_decisions_render_check.log" 2>&1; echo "exit $?" >> "$O/base_decisions_render_check.log" )
echo "== base (clean main) rules_render --check: $(tail -3 "$O/base_rules_render_check.log" | tr '\n' ' ' | cut -c1-300)"
echo "== base decisions_render --check: $(tail -2 "$O/base_decisions_render_check.log" | tr '\n' ' ')"
( cd v2/ecad/tools && VERDICT_DIR="$O/v" python3 rules_render.py --check > "$O/rules_render_check_pre.log" 2>&1; echo "exit $?" >> "$O/rules_render_check_pre.log" )
echo "== tree rules_render --check before any render: $(tail -3 "$O/rules_render_check_pre.log" | tr '\n' ' ' | cut -c1-300)"
( cd v2/ecad/tools && VERDICT_DIR="$O/v" python3 assembly_set.py --checklist > "$O/assembly_set_checklist.log" 2>&1; echo "exit $?" >> "$O/assembly_set_checklist.log" ); tail -2 "$O/assembly_set_checklist.log"
( cd v2/ecad/tools && VERDICT_DIR="$O/v" python3 rules_render.py --no-refresh > "$O/rules_render_write.log" 2>&1; echo "exit $?" >> "$O/rules_render_write.log" ); tail -2 "$O/rules_render_write.log"
git status --porcelain > "$O/status-1-after-render.txt"; cat "$O/status-1-after-render.txt"
mkdir -p "$O/page-drafts"
for f in $(git status --porcelain | awk '{print $2}'); do
  case " $EXPECT " in *" $f "*) continue;; esac
  git diff -- "$f" > "$O/page-drafts/$(echo $f | tr / _).diff"; git checkout -- "$f" 2>/dev/null || rm -f "$f"; echo "not this stream's file: its re-render kept as a draft and put back: $f ($(wc -l < "$O/page-drafts/$(echo $f | tr / _).diff") diff lines)"
done
git status --porcelain > "$O/status-2-before-suite.txt"; cmp -s "$O/status-0.txt" "$O/status-2-before-suite.txt" && echo "tree back to exactly the commit set" || { echo "WARNING tree status moved"; diff "$O/status-0.txt" "$O/status-2-before-suite.txt"; }
( cd v2/ecad && find out $(ls -d pcb-*/out/routeflow) -type f -print0 | sort -z | xargs -0 sha256sum ) > "$O/evidence-pre-suite.sha256"
git diff --binary > "$O/commit-set.diff"
cd "$T/v2/ecad/tools/tests"
T0=$(date +%s)
timeout 7200 python3 run.py > "$O/run_full.log" 2>&1; echo "run.py exit $?" >> "$O/run_full.log"
echo "suite seconds $(( $(date +%s) - T0 ))"
grep -E "^tests: [0-9]+ passed" "$O/run_full.log" | tail -1 | cut -c1-800; tail -2 "$O/run_full.log"
grep -E " (FAIL|SKIP)" "$O/run_full.log" | cut -c1-300
cd "$T"
git status --porcelain > "$O/status-3-after-suite.txt"
diff "$O/status-2-before-suite.txt" "$O/status-3-after-suite.txt" > "$O/status-suite-delta.txt" && echo "suite left the tree status unchanged" || { echo "suite changed the tree status:"; cat "$O/status-suite-delta.txt"; }
git diff --binary > "$O/tree-final.diff"; cmp -s "$O/commit-set.diff" "$O/tree-final.diff" && echo "tree diff after the suite equals the commit set byte for byte" || echo "WARNING tree diff moved during the suite"
( cd v2/ecad && find out $(ls -d pcb-*/out/routeflow) -type f -print0 | sort -z | xargs -0 sha256sum ) > "$O/evidence-post-suite.sha256"
cmp -s "$O/evidence-pre-suite.sha256" "$O/evidence-post-suite.sha256" && echo "evidence untouched through the suite" || { echo "evidence moved during the suite:"; diff "$O/evidence-pre-suite.sha256" "$O/evidence-post-suite.sha256" | head -20; }
echo "r8d-suite: done $(date -u +%FT%TZ)"
touch "$W/suite.flag"
