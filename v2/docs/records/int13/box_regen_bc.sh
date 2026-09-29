#!/usr/bin/env bash
# Integration set 12 (MESHSAT-1357, 29 September 2026): the regeneration of boards B and C after stream d4emcon's FEA-002
# remedies were applied to gen_sch_b.py (B-1 to B-5: back-feed gates for the RockBLOCK, the two E72 and the E22, U543 on the
# RockBLOCK enable, U554 on the 5G card's power-off line) and gen_sch_c.py (D4E-F1: R52 and D23 clamp EMCON_HW). A copy of
# records/int11/box_regen_all.sh (set 10) with the board loop narrowed to B and C; every other step, the parity instrument, the
# driver re-take and the pack are as there. EXPECTED: boards B and C DIFFERENT in schematic, netlist, intent and BOM (a
# circuit change: the parts the scripts name are added or changed, nothing else); A, D, E and P untouched. The integrator
# then runs records/d4emcon/tools/readback_d4e.py --board B and --board C on the regenerated netlists, and proves the
# changes against main by parsed components and net node sets before any pin or record is moved.
# Usage (on the box): box_regen_bc.sh <dir> <commit> <evidence tar> <bundle> <ref in bundle>
# --- set 10's description of the steps follows unchanged
# Integration set 10 (MESHSAT-1357, 29 September 2026): the regeneration of ALL SIX boards with a schematic (A, B, C, D, E, P)
# after stream d6dec changed intent.py and added decoupling_rules.py, both inside every generator's import closure, so every
# netlist's provenance sidecar (sch_prov.py) names a generator this tree no longer has and check_contracts refuses them all
# ("UNKNOWN GENERATOR"). A copy of v2/docs/records/s98/box_regen_ab.sh (set 8) with the board loop widened to six and its
# A-to-B lead report dropped; every other step, the parity instrument and the pack are as there. EXPECTED: every netlist's
# CONTENT identical (parity PARITY_AFTER_NOISE, the export date the noise) and every intent identical (d6dec's run5 found
# the six generators writing intents identical to the committed ones); if parity reads DIFFERENT, STOP and read it.
# The set 8 description below is kept for the steps; where it names boards A and B and the S-98 declarations, read all six
# boards and no declaration change.
# Usage (on the box):  box_regen_ab.sh <dir> <commit> <evidence tar> <bundle> <ref in bundle>
#   <dir>          the box directory name, e.g. s98 (everything under /root/s98, never /tmp)
#   <commit>       the exact commit of the integration line that carries fnd/s98's generators AND the integrator's
#                  apply_contract_i03.py already applied (pcb_interfaces.yaml is a configuration input of interfaces.py:
#                  the re-take must read the rewritten rows, or INT-001 reads CONFIG_CHANGED again after)
#   <evidence tar> main's gitignored evidence as installed in the integration worktree (the tar the re-takes install)
#   <bundle>       a git bundle holding <ref in bundle>, cloned from /root/r8int6/repo plus the bundle
#
# WHAT IT DOES, in order. (1) clone at <commit>, install the evidence, hash the ignored files. (2) For boards A and B, in
# their phase directories read from rules_status.manifest (v2/ecad/pcb-a-power-a23 and v2/ecad/pcb-b-compute-b19 at
# dcf04c90): keep the committed artefacts as `ref/` (schematic, netlist, intent, provenance; kicad-cli's BOM and ERC of
# the committed schematic), run the declared footprint generators, gen_sch_<L>.py with the committed schematic's Phase
# label and the board table's gen_env, build_sch.sh (ERC, netlist, sch_prov write, the paged PDF, the BOM), erc_gate.py
# --run, and regen_compare.py `pair` for schematic, netlist, intent, provenance, bom and erc (the parity instrument of
# the 25 September run). THE SCHEMATIC PHASE ONLY: no placement, no route, no board file is touched. (3) The consolidated
# re-take of every schematic-phase reading, all boards (--run --in-place --routed --json): the set-level contract readings
# (check_contracts, inhibit_chain_<letter>) are copied into EVERY board's routed/, so a run on A and B alone would leave
# the copies in C, D, E, E5 and P's routed/ recording the old intent_a and intent_b; the driver covers INT-001
# (interfaces_<letter>, check_contracts), PWR-001 (intent_rails), SCH-001 (erc_gate) and the rest. (4) reliability.py per
# board and claims_check.py, as the set 6 re-take did. (5) The explicit readings for the report: check_contracts.py and
# interfaces.py into checks/ (VERDICT_DIR), and records/s98/lead_ends.py on the regenerated intents. (6) The pack for
# the way back: tracked.patch (git diff --binary: the regenerated schematic, netlist, provenance and intent of A and B,
# and every routed/ reading the driver re-took), tracked-changed.lst, ignored-readings.tar, MANIFEST, SHA256SUMS, and
# REGEN-SUMMARY.txt. Writes /root/<dir>/done-regen (first field 0 = done, 3 = the clone failed). Install with
# _bin/install_pack.sh <worktree> <dir> <short sha> <scratch dir>.
#
# WHAT CHANGES CLASS AND WHY (stated here so the integrator can check the pack against it):
#   * out/<stem>-intent.json of A and B: the declarations (rails +5V_S2, +5V_DEV, VBAT on A; +5V_S2, +5V_DEV on B) and
#     their notes. Every reading that records intent_a or intent_b by sha (check_contracts on every board,
#     inhibit_chain_<letter>, interfaces_a, interfaces_b, intent_rails, edge_length, port_protect_<letter>, power_sequence,
#     safe_lines_<letter>, switch_list on A and B) is re-taken on the new files; their RESULTS are expected unchanged
#     (the alignment moves figures the tools do not judge against a limit; PWR-001 judges the declaration's form, and
#     dc_drop, which judges copper at the declared current, is a routed-phase reading not taken here).
#   * out/<stem>.net and .net.prov.json of A and B: the netlist CONTENT is expected identical (no part, pin or net moves:
#     parity reads PARITY_AFTER_NOISE, the export date being the noise), but its sha changes with the date, and the
#     provenance sidecar names the new generator sha; every reading bound to the old netlist sha is re-taken by the driver
#     for that reason. If regen_compare reads DIFFERENT for the netlist, STOP and read the report: the generators were
#     meant to change declarations only.
#   * pcb_interfaces.yaml (the integrator's apply_contract_i03.py, applied BEFORE this commit): interfaces_<letter> and
#     interfaces record it as `spec`; they are re-taken and read CURRENT again.
#   * Nothing on boards C, D, E, E5 and P changes but the copies of the set-level readings named above.
set -u
D=/root/$1; C=$D/rtk; E=$C/v2/ecad; T=$E/tools; COMMIT=$2; TAR=$3; BUN=$4; REF=$5; N=$1
export PYTHONDONTWRITEBYTECODE=1
mkdir -p $D; cd $D || exit 2
echo "start $(date -u +%FT%TZ)" > $D/regen-run.txt
kicad-cli version >> $D/regen-run.txt 2>&1
git -C /root/r8int6/repo fetch -q "$BUN" "$REF:refs/heads/box-$N" || { echo "FETCH FAILED" >> $D/regen-run.txt; echo "3 $(date -u +%FT%TZ)" > $D/done-regen; exit 3; }
rm -rf $C && git clone -q /root/r8int6/repo $C && git -C $C checkout -q $COMMIT || { echo "CHECKOUT FAILED" >> $D/regen-run.txt; echo "3 $(date -u +%FT%TZ)" > $D/done-regen; exit 3; }
echo "HEAD $(git -C $C rev-parse HEAD)" >> $D/regen-run.txt
tar xf "$TAR" -C $C
git -C $C status --short > $D/status-after-install.txt
echo "status lines after install: $(wc -l < $D/status-after-install.txt)" >> $D/regen-run.txt
( cd $C && git ls-files -o -i --exclude-standard -- v2 | sort | xargs -d "\n" sha256sum | sort -k2 > $D/ignored-before.sha256 )
# --- the phase directories, read from the manifest (never guessed)
python3 - "$T" > $D/phase-dirs.txt <<'PY'
import sys, os
sys.path.insert(0, sys.argv[1])
import rules_status as S
m = S.manifest()
for L in m["boards"]:
    print(L, os.path.relpath(S._phase_dir(L, m), os.path.dirname(sys.argv[1])), m["boards"][L].get("project", ""))
PY
# --- (2) the regeneration of A and B, the schematic phase only
S=$D/REGEN-SUMMARY.txt; : > $S
for LET in ${REGEN_BOARDS:-b c}; do
  read -r _ PD STEM < <(awk -v l=$LET '$1 == l' $D/phase-dirs.txt)
  P=$E/$PD; O=$D/regen/$LET; mkdir -p $O/ref $O/v
  cd $P || { echo "no phase dir for $LET" >> $S; continue; }
  LABEL=$(grep -m1 -o '(comment 1 "Phase [A-Za-z0-9]*' $STEM.kicad_sch | sed 's/.*Phase //'); echo "$LABEL" > $O/phase.txt
  GENV="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])).get('gen_env') or {}; print(' '.join('%s=%s' % (k, v) for k, v in d.items()))" $T/boards/$LET.json)"
  FPG="$(python3 -c "import json,sys; print(' '.join(json.load(open(sys.argv[1])).get('footprint_generator') or []))" $T/boards/$LET.json)"
  # the committed artefacts, and kicad-cli's exports of the COMMITTED schematic (regen_compare's `ref` side)
  for f in $STEM.kicad_sch out/$STEM.net out/$STEM-intent.json out/$STEM.net.prov.json; do git -C $C show "$COMMIT:v2/ecad/$PD/$f" > $O/ref/$(basename $f); done
  kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o $O/ref/$STEM-bom.csv $STEM.kicad_sch > /dev/null 2>&1
  kicad-cli sch erc --severity-all --format json -o $O/ref/$STEM-erc.json $STEM.kicad_sch > /dev/null 2>&1
  sha256sum ../tools/gen_sch_$LET.py ../tools/kisch.py ../tools/intent.py ../tools/schlayout.py > $O/generator.sha256
  : > $O/gen_fp.log; for g in $FPG; do python3 ../tools/$g ../meshsat.pretty >> $O/gen_fp.log 2>&1 || echo "footprint generator $g FAILED" >> $O/gen_fp.log; done
  echo "gen_env: [$GENV] PHASE=$LABEL footprint generators: [$FPG]" > $O/gen_sch.log
  PHASE="$LABEL" env $GENV python3 ../tools/gen_sch_$LET.py $STEM.kicad_sch $STEM >> $O/gen_sch.log 2>&1; GE=$?; echo "gen_sch exit $GE" >> $O/gen_sch.log
  if [ $GE -ne 0 ]; then echo "board $LET: STOP generation failed (regen/$LET/gen_sch.log)" | tee -a $S; tail -20 $O/gen_sch.log >> $S; continue; fi
  rm -f out/$STEM.net out/$STEM-bom.csv out/$STEM.net.prov.json
  bash ../tools/build_sch.sh . $STEM > $O/build_sch.log 2>&1; echo "build_sch exit $?" >> $O/build_sch.log
  [ -s out/$STEM.net ] || { echo "board $LET: STOP no netlist (regen/$LET/build_sch.log)" | tee -a $S; continue; }
  rm -f out/$STEM-erc.status out/erc_gate.verdict.json
  python3 ../tools/erc_gate.py . $STEM --run > $O/erc_gate.log 2>&1; echo "erc_gate exit $?" >> $O/erc_gate.log
  # parity, kind by kind: the committed artefact against the regenerated one
  for k in schematic netlist intent provenance bom erc; do
    case $k in schematic) a=$O/ref/$STEM.kicad_sch; b=$STEM.kicad_sch;; netlist) a=$O/ref/$STEM.net; b=out/$STEM.net;; intent) a=$O/ref/$STEM-intent.json; b=out/$STEM-intent.json;;
      provenance) a=$O/ref/$STEM.net.prov.json; b=out/$STEM.net.prov.json;; bom) a=$O/ref/$STEM-bom.csv; b=out/$STEM-bom.csv;; erc) a=$O/ref/$STEM-erc.json; b=out/$STEM-erc.json;; esac
    python3 ../tools/regen_compare.py pair $k "$a" "$b" > $O/parity-$k.json 2>&1; echo "parity $k exit $?" >> $O/parity.txt
  done
  python3 ../tools/sch_prov.py read out/$STEM.net $LET > $O/prov-after.txt 2>&1
  for f in $STEM.kicad_sch out/$STEM.net out/$STEM-intent.json out/$STEM.net.prov.json out/$STEM-bom.csv out/$STEM-erc.json out/$STEM-erc.rpt; do [ -s $f ] && cp $f $O/ || echo "missing: $f" >> $O/missing.txt; done
  { echo "board $LET phase $LABEL in $PD: $(grep -m1 '^wrote' $O/gen_sch.log); $(grep -m1 '^lands' $O/gen_sch.log); $(tail -1 $O/gen_sch.log); $(tail -1 $O/build_sch.log); erc_gate $(tail -1 $O/erc_gate.log)";
    for k in schematic netlist intent provenance bom erc; do printf '  parity %-10s %s\n' $k "$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('result') or d.get('verdict') or d)" $O/parity-$k.json 2>/dev/null | cut -c1-160)"; done; } >> $S
done
cd $D
# --- (3) the driver, every board (the set-level readings are copied to every board's routed/)
( cd $E && python3 tools/retake_schematic_phase.py --run --in-place --routed --json > $D/retake.json 2> $D/retake.log; echo "retake exit $?" >> $D/regen-run.txt )
# --- (4) the other writers: reliability.py per board, claims_check.py from v2/ecad
L=$D/other-writers.log; : > $L
while read LET PD STEM; do
  P=$E/$PD
  echo "--- reliability board $LET in $PD" >> $L
  ( cd $P && VERDICT_DIR=$P/out timeout 600 python3 $T/reliability.py --ecad "$E" --board $LET >> $L 2>&1; echo "exit $?" >> $L )
  if [ -s $P/out/reliability.verdict.json ] && [ $P/out/reliability.verdict.json -nt $D/phase-dirs.txt ]; then
    cp $P/out/reliability.verdict.json $P/routed/reliability.verdict.json; echo "copied to $PD/routed/" >> $L
  else echo "NO READING WRITTEN for board $LET" >> $L; fi
done < $D/phase-dirs.txt
( cd $E && timeout 600 python3 tools/claims_check.py >> $L 2>&1; echo "claims_check exit $?" >> $L )
# --- (5) the explicit readings for the report, into checks/ (never the tree's out/)
K=$D/checks; mkdir -p $K
( cd $K && VERDICT_DIR=$K timeout 600 python3 $T/check_contracts.py $E > $K/contracts.txt 2>&1; echo "check_contracts exit $?" >> $K/contracts.txt )
( cd $K && VERDICT_DIR=$K timeout 600 python3 $T/interfaces.py > $K/interfaces.txt 2>&1; echo "interfaces exit $?" >> $K/interfaces.txt )
{ echo "== check_contracts"; grep -E "ALL PASS|FAIL|MISSING|verdict:" $K/contracts.txt | head -12; echo "== interfaces"; head -3 $K/interfaces.txt; echo "== driver"; tail -12 $D/retake.log; } >> $S
# --- (6) the pack
O=$D/pack; rm -rf $O; mkdir -p $O; cd $C
git status --short > $O/status.txt
git diff --name-only | sort > $O/tracked-changed.lst
git diff --binary > $O/tracked.patch
git ls-files -o -i --exclude-standard -- v2 | sort | xargs -d "\n" sha256sum | sort -k2 > $O/ignored-after.sha256
python3 - $D/ignored-before.sha256 $O/ignored-after.sha256 $O/ignored-new-or-changed.lst <<'PY'
import sys
def load(p):
    d = {}
    for line in open(p, encoding="utf-8"):
        line = line.rstrip("\n")
        if line: d[line[66:]] = line[:64]
    return d
b, a = load(sys.argv[1]), load(sys.argv[2])
open(sys.argv[3], "w").write("".join(p + "\n" for p in sorted(a) if b.get(p) != a[p]))
print("ignored before %d, after %d, new or changed %d" % (len(b), len(a), sum(1 for p in a if b.get(p) != a[p])))
PY
grep -v -E '^v2/ecad/out/(rule-audit/|rules_status\.verdict\.json$|rules_complete\.verdict\.json$)|(^|/)__pycache__/|\.pyc$' $O/ignored-new-or-changed.lst > $O/ignored-readings.lst || true
tar cf $O/ignored-readings.tar --owner=0 --group=0 --numeric-owner -T $O/ignored-readings.lst
{ echo "# $N ignored readings: path, bytes, sha256. Taken in $C at $COMMIT."; while read f; do printf '%s\t%s\t%s\n' "$f" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -c1-64)"; done < $O/ignored-readings.lst; } > $O/MANIFEST
cp $S $O/REGEN-SUMMARY.txt; cp -r $D/regen $O/regen; cp -r $K $O/checks
( cd $O && sha256sum ignored-readings.tar MANIFEST tracked.patch tracked-changed.lst REGEN-SUMMARY.txt > SHA256SUMS )
echo "tracked files changed: $(wc -l < $O/tracked-changed.lst); not readings: $(grep -v -E 'routed/.*\.verdict\.json$' $O/tracked-changed.lst | tr '\n' ' ')" >> $S
echo "end $(date -u +%FT%TZ)" >> $D/regen-run.txt
echo "0 $(date -u +%FT%TZ)" > $D/done-regen
