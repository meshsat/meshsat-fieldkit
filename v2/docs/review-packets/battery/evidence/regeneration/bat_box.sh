#!/usr/bin/env bash
# Review stream BAT (MESHSAT-1357, 26 September 2026): board P's schematic regenerated on the rented KiCad box, in /root/rv/bat only.
# base = main 1f614233 regenerated (parity against the committed pcb-p-pack-p2 files); new = base plus the overlay (gen_sch_p.py:
# the second level's TS network). Schematic-phase gates only. No placement, no escape, no Freerouting. /root/gitlab is never read.
# Adapted from wt/r4p/drafts/scripts/r5p2_box.sh (the round-4 board P author's driver).
set -uo pipefail
SRC=/root/rv/bat; W=/root/rv/bat/run; OUT=$W/out
rm -rf "$W"; mkdir -p "$W/base" "$W/new" "$OUT"
exec > >(tee "$OUT/run.log") 2>&1
echo "bat: start $(date -u +%FT%TZ)"
for T in base new; do tar xzf "$SRC/base.tgz" -C "$W/$T" || { echo "bat: STOP base extract $T"; exit 2; }; done
tar xzf "$SRC/overlay.tgz" -C "$W/new" || { echo "bat: STOP overlay"; exit 2; }
{ echo "kicad-cli: $(kicad-cli version 2>&1)"; dpkg-query -W kicad kicad-symbols kicad-footprints poppler-utils 2>&1; python3 --version; echo "mutool: $(mutool -v 2>&1 | head -1)"; } > "$OUT/env.txt"
cat "$OUT/env.txt"
tar tzf "$SRC/overlay.tgz" | sort > "$OUT/overlay-files.txt"; sha256sum "$W/new/v2/ecad/tools/gen_sch_p.py" "$W/base/v2/ecad/tools/gen_sch_p.py" > "$OUT/generator-sha256.txt"
N=pcb-p-pack; DIR=pcb-p-pack-p2
LABEL=$(grep -m1 -o '(comment 1 "Phase [A-Za-z0-9]*' "$W/base/v2/ecad/$DIR/$N.kicad_sch" | sed 's/.*Phase //')
echo "bat: committed phase label $LABEL"
# the committed files, as git archive gave them, before anything is regenerated over them
mkdir -p "$OUT/committed"; for f in "$N.kicad_sch" "out/$N.net" "out/$N-intent.json" "out/$N.net.prov.json"; do cp "$W/base/v2/ecad/$DIR/$f" "$OUT/committed/" 2>/dev/null || echo "bat: committed file missing $f"; done
( cd "$W/base/v2/ecad/$DIR" && kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "$OUT/committed/$N-bom.csv" "$N.kicad_sch" > /dev/null 2>&1; kicad-cli sch erc --severity-all --format json -o "$OUT/committed/$N-erc.json" "$N.kicad_sch" > /dev/null 2>&1 )
for T in base new; do
  E="$W/$T/v2/ecad"; D="$E/$DIR"; V="$OUT/$T/v"; mkdir -p "$V" "$OUT/$T/files"
  cd "$D" || { echo "bat: $T no project dir"; continue; }
  echo "bat: ===== $T $(date -u +%T)"
  python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" ../tools/gen_sch_p.py && echo "compile ok" || echo "bat: $T COMPILE FAIL"
  python3 ../tools/tests/test_swallowed_calls.py ../tools/gen_sch_p.py > /dev/null 2>&1 && echo "swallowed-calls ok" || echo "bat: $T SWALLOWED CALLS"
  : > "$OUT/$T/gen_fp.log"; python3 ../tools/gen_footprints_idc.py ../meshsat.pretty >> "$OUT/$T/gen_fp.log" 2>&1 || echo "bat: $T footprint generator FAILED"
  PHASE="$LABEL" python3 ../tools/gen_sch_p.py "$N.kicad_sch" "$N" > "$OUT/$T/gen_sch.log" 2>&1; echo "gen_sch exit $?" >> "$OUT/$T/gen_sch.log"; tail -6 "$OUT/$T/gen_sch.log"
  rm -f "out/$N.net" "out/$N-bom.csv" "out/$N-schematic.pdf" "out/$N-schematic-sheet.pdf"
  bash ../tools/build_sch.sh . "$N" > "$OUT/$T/build_sch.log" 2>&1; echo "build_sch exit $?" >> "$OUT/$T/build_sch.log"; tail -6 "$OUT/$T/build_sch.log"
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
  [ -s "out/$N-bom.csv" ] || { kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "out/$N-bom.csv" "$N.kicad_sch" > /dev/null 2>&1 && echo "bat: $T BOM exported by hand"; }
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
    [ -s "$f" ] && cp "$f" "$OUT/$T/files/" || echo "bat: $T output missing: $f"
  done
done
cd "$W"; RC="$W/base/v2/ecad/tools/regen_compare.py"; C="$OUT/committed"; B="$OUT/base/files"; X="$OUT/new/files"
echo "bat: ===== parity of main's committed P files against main's generator"
python3 "$RC" pair schematic "$C/$N.kicad_sch" "$B/$N.kicad_sch" > "$OUT/parity_sch.json"; echo "schematic exit $?"
python3 "$RC" pair netlist "$C/$N.net" "$B/$N.net" > "$OUT/parity_net.json"; echo "netlist exit $?"
python3 "$RC" pair bom "$C/$N-bom.csv" "$B/$N-bom.csv" > "$OUT/parity_bom.json"; echo "bom exit $?"
python3 "$RC" pair erc "$C/$N-erc.json" "$B/$N-erc.json" > "$OUT/parity_erc.json"; echo "erc exit $?"
python3 "$RC" pair intent "$C/$N-intent.json" "$B/$N-intent.json" > "$OUT/parity_intent.json" 2>&1; echo "intent exit $?"
echo "bat: ===== the change: base regenerated against new"
python3 "$RC" pair netlist "$B/$N.net" "$X/$N.net" > "$OUT/change_net.json"; echo "netlist (expected DIFFERENT) exit $?"
python3 "$RC" pair bom "$B/$N-bom.csv" "$X/$N-bom.csv" > "$OUT/change_bom.json"; echo "bom (expected DIFFERENT) exit $?"
python3 "$RC" pair erc "$B/$N-erc.json" "$X/$N-erc.json" > "$OUT/change_erc.json"; echo "erc exit $?"
python3 "$SRC/bin/netdiff.py" "$B/$N.net" "$X/$N.net" > "$OUT/netlist_diff.txt" 2>&1; echo "netdiff exit $?"
python3 "$SRC/bin/netdiff.py" "$C/$N.net" "$X/$N.net" > "$OUT/netlist_diff_vs_committed.txt" 2>&1; echo "netdiff vs committed exit $?"
diff <(python3 -c "import csv,sys;[print(r) for r in sorted(map(tuple,csv.reader(open(sys.argv[1]))))]" "$B/$N-bom.csv") <(python3 -c "import csv,sys;[print(r) for r in sorted(map(tuple,csv.reader(open(sys.argv[1]))))]" "$X/$N-bom.csv") > "$OUT/bom_diff.txt"; echo "bom diff lines $(wc -l < "$OUT/bom_diff.txt")"
sha256sum "$B"/* "$X"/* "$C"/* > "$OUT/sha256.txt"
echo "bat: done $(date -u +%FT%TZ)"
