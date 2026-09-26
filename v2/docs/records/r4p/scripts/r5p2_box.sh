#!/usr/bin/env bash
# Board P, Review D round 4, SECOND FIX-UP after the re-review (MESHSAT-1357), 26 September 2026. Runs on the rented KiCad box in
# /root/r5/p/f2 only, reading /root/r5/p (base.tgz = git archive of main 82dd1e4d, cert.tgz = JLC-CERTIFIED.tsv of 82dd1e4d, bin/ = the
# helper scripts, out/ = the first fix-up's outputs) and /root/r4/p (the round-4 baseline); /root/gitlab is never read or written.
#   base = 82dd1e4d regenerated again (parity); new = base plus the overlay (gen_sch_p.py, gen_pcb_p.py, gen_pcb_p3.py, two lands).
# The same steps as r5p_box.sh (schematic-phase gates, JLC BOM and lcsc_fill, placement, placed-board checks, DRC, land read-back),
# plus the netlist against the first fix-up's and the TPS2 neighbour gaps. No escape, no fanout, no Freerouting.
set -uo pipefail
SRC=/root/r5/p; W=/root/r5/p/f2; OUT=$W/out
rm -rf "$W/base" "$W/new" "$OUT"; mkdir -p "$W/base" "$W/new" "$OUT"
exec > >(tee "$OUT/run.log") 2>&1
echo "r5p2: start $(date -u +%FT%TZ)"
for T in base new; do tar xzf "$SRC/base.tgz" -C "$W/$T" && tar xzf "$SRC/cert.tgz" -C "$W/$T" || { echo "r5p2: STOP base extract $T"; exit 2; }; done
tar xzf "$W/overlay.tgz" -C "$W/new" || { echo "r5p2: STOP overlay"; exit 2; }
{ echo "kicad-cli: $(kicad-cli version 2>&1)"; dpkg-query -W kicad kicad-symbols kicad-footprints poppler-utils 2>&1; python3 --version; echo "mutool: $(mutool -v 2>&1 | head -1)"; } > "$OUT/env.txt"
cat "$OUT/env.txt"
tar tzf "$W/overlay.tgz" | sort > "$OUT/overlay-files.txt"
N=pcb-p-pack; DIR=pcb-p-pack-p2
LABEL=$(grep -m1 -o '(comment 1 "Phase [A-Za-z0-9]*' "$W/base/v2/ecad/$DIR/$N.kicad_sch" | sed 's/.*Phase //')
echo "r5p2: committed phase label $LABEL"
for T in base new; do
  E="$W/$T/v2/ecad"; D="$E/$DIR"; V="$OUT/$T/v"; mkdir -p "$V" "$OUT/$T/files"
  cd "$D" || { echo "r5p2: $T no project dir"; continue; }
  echo "r5p2: ===== $T $(date -u +%T)"
  for f in ../tools/gen_sch_p.py ../tools/gen_pcb_p.py ../tools/gen_pcb_p3.py; do
    python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" "$f" && echo "compile ok $f" || echo "r5p2: $T COMPILE FAIL $f"
    python3 ../tools/tests/test_swallowed_calls.py "$f" > /dev/null 2>&1 && echo "swallowed-calls ok $f" || echo "r5p2: $T SWALLOWED CALLS $f"
  done
  : > "$OUT/$T/gen_fp.log"; python3 ../tools/gen_footprints_idc.py ../meshsat.pretty >> "$OUT/$T/gen_fp.log" 2>&1 || echo "r5p2: $T footprint generator FAILED"
  PHASE="$LABEL" python3 ../tools/gen_sch_p.py "$N.kicad_sch" "$N" > "$OUT/$T/gen_sch.log" 2>&1; echo "gen_sch exit $?" >> "$OUT/$T/gen_sch.log"; tail -6 "$OUT/$T/gen_sch.log"
  rm -f "out/$N.net" "out/$N-bom.csv"
  bash ../tools/build_sch.sh . "$N" > "$OUT/$T/build_sch.log" 2>&1; echo "build_sch exit $?" >> "$OUT/$T/build_sch.log"; tail -4 "$OUT/$T/build_sch.log"
  rm -f "out/$N-erc.status" out/erc_gate.verdict.json
  VERDICT_DIR="$V" python3 ../tools/erc_gate.py . "$N" > "$V/erc_gate.log" 2>&1; echo "erc_gate exit $?" >> "$V/erc_gate.log"; tail -4 "$V/erc_gate.log"
  NET="$D/out/$N.net"; INT="$D/out/$N-intent.json"
  VERDICT_DIR="$V" python3 ../tools/port_protect.py "$NET" p > "$V/port_protect.log" 2>&1; echo "TRN-001 port_protect exit $?" | tee -a "$V/port_protect.log"
  VERDICT_DIR="$V" python3 ../tools/pin_map_lands.py "$NET" p > "$V/pin_map_lands.log" 2>&1; echo "SCH-005 pin_map_lands exit $?" | tee -a "$V/pin_map_lands.log"
  VERDICT_DIR="$V" python3 ../tools/derate.py "$NET" --intent "$INT" --out-dir "$V" > "$V/derate.log" 2>&1; echo "CMP-001 derate exit $?" | tee -a "$V/derate.log"
  VERDICT_DIR="$V" python3 ../tools/power_path.py "$NET" --intent "$INT" --out-dir "$V" > "$V/power_path.log" 2>&1; echo "power_path exit $?" | tee -a "$V/power_path.log"
  VERDICT_DIR="$V" python3 ../tools/pack_protection.py --netlist "$NET" > "$V/pack_protection.log" 2>&1; echo "BAT-001 pack_protection exit $?" | tee -a "$V/pack_protection.log"
  ( cd "$E/tools" && VERDICT_DIR="$V" python3 check_contracts.py "$E" > "$V/check_contracts.log" 2>&1; echo "check_contracts exit $?" | tee -a "$V/check_contracts.log" )
  ( cd "$E/tools" && VERDICT_DIR="$V" python3 energy_chain.py --ecad "$E" > "$V/energy_chain.log" 2>&1; echo "energy_chain exit $?" | tee -a "$V/energy_chain.log" )
  python3 ../tools/review_nets.py "$NET" > "$V/review_nets.log" 2>&1; echo "review_nets exit $?" >> "$V/review_nets.log"
  [ -s "out/$N-bom.csv" ] || { kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "out/$N-bom.csv" "$N.kicad_sch" > /dev/null 2>&1 && echo "r5p2: $T BOM exported by hand"; }
  # the JLC BOM exactly as export_jlc.sh writes it from the schematic BOM, then lcsc_fill.py on it (it resolves lcsc-allow.txt from
  # out/jlc/ three levels up and JLC-CERTIFIED.tsv from the tree's v2/release)
  mkdir -p out/jlc
  python3 - "$N" <<'PY'
import csv, sys, re
N = sys.argv[1]
rows = list(csv.DictReader(open("out/%s-bom.csv" % N)))
with open("out/jlc/%s-bom.csv" % N, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for r in rows:
        refs = []
        for x in r["Reference"].split(","):
            x = x.strip().rstrip("?")
            m = re.match(r"^([A-Za-z_]+)(\d+)-\1?(\d+)$", x)
            refs += ["%s%d" % (m.group(1), k) for k in range(int(m.group(2)), int(m.group(3)) + 1)] if m else [x]
        refs = [x for x in refs if x and not x.startswith(("H", "S_", "TP", "#"))]
        if not refs: continue
        w.writerow([r["Value"], ",".join(refs), r["Footprint"].split(":")[-1], r.get("LCSC", "")])
PY
  cp "out/jlc/$N-bom.csv" "$OUT/$T/files/$N-jlc-bom.before-fill.csv"
  VERDICT_DIR="$V" python3 ../tools/lcsc_fill.py "out/jlc/$N-bom.csv" > "$V/lcsc_fill.log" 2>&1; echo "lcsc_fill exit $?" | tee -a "$V/lcsc_fill.log"; grep -a "lcsc_fill:" "$V/lcsc_fill.log" | head -4
  cp "out/jlc/$N-bom.csv" "$OUT/$T/files/$N-jlc-bom.filled.csv"
  for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json" "out/$N-bom.csv" "out/$N-erc.json" "out/$N-erc.rpt" "out/$N-schematic.pdf" "out/$N-schematic-sheet.pdf"; do
    [ -s "$f" ] && cp "$f" "$OUT/$T/files/" || echo "r5p2: $T output missing: $f"
  done
done
# ------------------------------------------------------------------ the netlist difference, and the baselines' parity
cd "$W"
R4BASE=/root/r4/p/out/base/files/$N.net
tar xzf "$SRC/base.tgz" -O "v2/ecad/$DIR/out/$N.net" > "$W/base.committed.net" 2>/dev/null
python3 "$SRC/bin/regen_compare.py" pair netlist "$W/base.committed.net" "$OUT/base/files/$N.net" > "$OUT/base_regen_vs_committed.json" 2>&1; echo "r5 base regen vs committed netlist exit $?"
python3 "$SRC/bin/regen_compare.py" pair netlist "$R4BASE" "$OUT/base/files/$N.net" > "$OUT/r5base_vs_r4base.json" 2>&1; echo "r5 base vs r4 base netlist exit $?"
python3 "$SRC/bin/regen_compare.py" pair netlist "$R4BASE" "$OUT/new/files/$N.net" > "$OUT/netlist_compare.json" 2>&1; echo "regen_compare (r4 base vs new) exit $?"
python3 "$SRC/bin/netdiff.py" "$R4BASE" "$OUT/new/files/$N.net" > "$OUT/netlist_diff.txt" 2>&1; echo "netdiff (r4 base vs new) exit $?"
F1NET=/root/r5/p/out/new/files/$N.net
python3 "$SRC/bin/regen_compare.py" pair netlist "$F1NET" "$OUT/new/files/$N.net" > "$OUT/netlist_compare_vs_fixup1.json" 2>&1; echo "regen_compare (fix-up 1 new vs new) exit $?"
python3 "$SRC/bin/netdiff.py" "$F1NET" "$OUT/new/files/$N.net" > "$OUT/netlist_diff_vs_fixup1.txt" 2>&1; echo "netdiff (fix-up 1 vs fix-up 2) exit $?"
diff <(grep -v "(date\|(source\|(tool" "$F1NET") <(grep -v "(date\|(source\|(tool" "$OUT/new/files/$N.net") > "$OUT/netlist_text_diff_vs_fixup1.txt"; echo "text diff vs fix-up 1 exit $?"
[ -f /root/r4/p/out/new/files/$N.net ] && { python3 "$SRC/bin/netdiff.py" /root/r4/p/out/new/files/$N.net "$OUT/new/files/$N.net" > "$OUT/netlist_diff_vs_round4_pass.txt" 2>&1; echo "netdiff (round-4 first pass vs fix-up) exit $?"; }
sha256sum "$R4BASE" "$F1NET" "$W/base.committed.net" "$OUT/base/files/$N.net" "$OUT/new/files/$N.net" > "$OUT/netlist-sha256.txt"
# ------------------------------------------------------------------ the land read-back (new tree's library)
cd "$W/new/v2/ecad/$DIR" || exit 2
python3 "$SRC/bin/landcheck.py" ../meshsat.pretty Texas_RSM0032A_VQFN-32-1EP_4x4mm_P0.4mm_EP1.4x1.4mm Eaton_SCF9550_9.5x5.0mm > "$OUT/landcheck.txt" 2>&1; echo "landcheck exit $?"; cat "$OUT/landcheck.txt" | grep -v "^   pad [0-9][0-9]* at" | head -30
grep -a "pad 1 \|pad 2 \|pad 3 \|pad 33" "$OUT/landcheck.txt" | head -12
# ------------------------------------------------------------------ placement, new tree only
P="$OUT/new/place"; mkdir -p "$P"
PHASE="$LABEL" python3 ../tools/gen_pcb_p.py "$N.kicad_pcb" > "$P/gen_pcb_p.log" 2>&1; echo "gen_pcb_p exit $?" >> "$P/gen_pcb_p.log"; tail -2 "$P/gen_pcb_p.log"
python3 ../tools/gen_pcb_p3.py "$N.kicad_pcb" "out/$N.net" > "$P/gen3.log" 2>&1; echo "gen_pcb_p3 exit $?" >> "$P/gen3.log"
grep -aE 'saved|WARN|overflow|unplaced|missing|SystemExit|F2 pads|ground stitch|Traceback|Error|exit' "$P/gen3.log" | grep -v 'memory leak'
python3 ../tools/jumper_clearance.py "$N.kicad_pcb" > "$P/jumper_clearance.log" 2>&1; echo "jumper_clearance exit $?" >> "$P/jumper_clearance.log"; tail -3 "$P/jumper_clearance.log"
python3 ../tools/class_floor.py "$N.kicad_pcb" > "$P/class_floor.log" 2>&1; echo "class_floor exit $?" >> "$P/class_floor.log"; tail -3 "$P/class_floor.log"
VERDICT_DIR="$P" python3 ../tools/check_pcb_p.py "$N.kicad_pcb" > "$P/check_pcb_p.log" 2>&1; echo "check_pcb_p exit $?" >> "$P/check_pcb_p.log"; grep -aE 'FAIL|RESULT|exit' "$P/check_pcb_p.log"
VERDICT_DIR="$P" python3 ../tools/netlist_board.py "$N.kicad_pcb" "out/$N.net" > "$P/netlist_board.log" 2>&1; echo "netlist_board exit $?" >> "$P/netlist_board.log"; tail -3 "$P/netlist_board.log"
kicad-cli pcb drc --severity-all --format json -o "$P/drc.json" "$N.kicad_pcb" > "$P/drc.log" 2>&1; echo "drc exit $?" >> "$P/drc.log"
python3 "$SRC/bin/drc_summary.py" "$P/drc.json" > "$P/drc_summary.txt" 2>&1; cat "$P/drc_summary.txt" | head -40
python3 "$SRC/bin/place_report.py" "$N.kicad_pcb" > "$P/place_report.txt" 2>&1; head -100 "$P/place_report.txt"
python3 "$W/tps2_neighbours.py" "$N.kicad_pcb" > "$P/tps2_neighbours.txt" 2>&1; echo "tps2_neighbours exit $?"; cat "$P/tps2_neighbours.txt"
cp "$N.kicad_pcb" "$P/" ; cp out/*-regions.json "$P/" 2>/dev/null; cat "$P"/*-regions.json 2>/dev/null
( cd "$OUT" && find . -type f ! -name SHA256SUMS ! -name run.log -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS )
echo "r5p2: done $(date -u +%FT%TZ)"
