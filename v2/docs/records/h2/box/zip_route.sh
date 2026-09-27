#!/usr/bin/env bash
# REGENERATE.md sections 2 to 7 (the ZIP route) and 1a, run as written with V=H2, only under /root/h2/zr (MESHSAT-1357)
set -u
V=H2
Z=/root/h2/zr
rm -rf $Z && mkdir -p $Z && cp /root/h2/$V.zip /root/h2/$V.zip.sha256 $Z/ && cd $Z
exec > $Z/route.log 2>&1
step() { echo; echo "=== $* ($(date -u +%T))"; }
step "section 2"
export PYTHONDONTWRITEBYTECODE=1
sha256sum -c $V.zip.sha256
unzip -q $V.zip
cd $V
HO="$PWD"
python3 v2/ecad/tools/handover_pack.py verify .
python3 v2/ecad/tools/sch_prov.py read v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net p
step "section 3"
mkdir -p "$HO/../committed-p"
cp v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_sch v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net.prov.json "$HO/../committed-p/"
cd v2/ecad/pcb-p-pack-p2
python3 ../tools/gen_footprints_idc.py ../meshsat.pretty
PHASE=P4 python3 ../tools/gen_sch_p.py pcb-p-pack.kicad_sch pcb-p-pack
rm -f out/pcb-p-pack.net
bash ../tools/build_sch.sh . pcb-p-pack
VERDICT_DIR="$HO/../verdicts" python3 ../tools/erc_gate.py . pcb-p-pack --run
python3 ../tools/regen_compare.py pair netlist "$HO/../committed-p/pcb-p-pack.net" out/pcb-p-pack.net
python3 ../tools/regen_compare.py pair schematic "$HO/../committed-p/pcb-p-pack.kicad_sch" pcb-p-pack.kicad_sch
python3 ../tools/regen_compare.py pair intent "$HO/../committed-p/pcb-p-pack-intent.json" out/pcb-p-pack-intent.json
python3 ../tools/regen_compare.py pair provenance "$HO/../committed-p/pcb-p-pack.net.prov.json" out/pcb-p-pack.net.prov.json
sha256sum pcb-p-pack.kicad_sch "$HO/../committed-p/pcb-p-pack.kicad_sch"
grep schematic_sha256 out/pcb-p-pack.net.prov.json "$HO/../committed-p/pcb-p-pack.net.prov.json"
python3 ../tools/regen_compare.py pair bom "$HO/v2/release/handover/_generated/pcb-p-pack-p2/NOT_FOR_FAB-pcb-p-pack-bom.csv" out/pcb-p-pack-bom.csv
python3 ../tools/regen_compare.py pair erc "$HO/v2/release/handover/_generated/pcb-p-pack-p2/pcb-p-pack-erc.json" out/pcb-p-pack-erc.json
cd "$HO"
python3 v2/ecad/tools/handover_pack.py verify .
step "section 4"
cd "$HO/.."
mkdir -p rg
unzip -q $V.zip -d rg
cd rg/$V
python3 v2/ecad/tools/handover_exports.py regen --out "$HO/../rg-out" --letters a,b,c,d,e,p
echo "regen exit $?"
step "section 5"
cd "$HO/.."
mkdir -p ex
unzip -q $V.zip -d ex
cd ex/$V
python3 v2/ecad/tools/handover_exports.py exports --out "$HO/../ex-out" --commit "$(sed -n 's/^commit: //p' SOURCE.txt)"
echo "exports exit $?"
for b in pcb-a-power-a23 pcb-b-compute-b19 pcb-c-display-c8 pcb-d-aprs-d9 pcb-e1-dock-e7 pcb-p-pack-p2; do for f in v2/release/handover/_generated/$b/NOT_FOR_FAB-*.csv; do cmp "$f" "$HO/../ex-out/$b/$(basename "$f")" && echo "same: $b/$(basename "$f")"; done; done
step "section 6"
cd "$HO/v2/ecad/tools"
VERDICT_DIR="$HO/../verdicts" python3 energy_chain.py --ecad ..
echo "energy_chain exit $?"
for b in a b e e5 p; do python3 -c "import json,sys; j=json.load(open(sys.argv[1])); print(sys.argv[1].split('/')[-1], j.get('verdict'), j.get('counts'))" "$HO/../verdicts/energy_chain_$b.verdict.json" 2>/dev/null; done
step "section 7, validator from the extraction"
cd "$HO/.."
mkdir -p val
unzip -q $V.zip -d val
(cd val/$V/v2/ecad && python3 tools/rules_lib.py requirements 2>&1 | tail -25)
(cd val/$V && python3 v2/ecad/tools/rules_render.py --requirements --check 2>&1 | tail -3)
(cd val/$V && python3 v2/docs/review-packets/battery/evidence/check_manifest.py 2>&1 | tail -5)
(cd val/$V && VERDICT_DIR="$HO/../verdicts-cc" python3 v2/ecad/tools/check_contracts.py v2/ecad 2>&1 | tail -3)
(cd val/$V && python3 v2/docs/records/rv-pwr/pwr_budget.py > "$HO/../pwr_budget.out" 2>&1; cmp "$HO/../pwr_budget.out" v2/docs/records/rv-pwr/pwr_budget.json && echo "pwr_budget: byte-identical to pwr_budget.json")
step "section 7, suite"
cd "$HO/.."
mkdir -p suite
unzip -q $V.zip -d suite
cd suite/$V/v2/ecad/tools/tests
python3 run.py > "$HO/../suite.log" 2>&1
echo "suite exit $?"
tail -n 1 "$HO/../suite.log"
grep -E '^(FAIL|  FAIL|failed)|FAILED' "$HO/../suite.log" | head -60
step "section 1a"
cd "$HO/.."
mkdir -p ra
unzip -q $V.zip -d ra
cd ra/$V
REF=62f26a44
fetch() { for p in "$@"; do
  b=$(awk -F'\t' -v p="$p" '$1==p{print $2}' REFERENCED-SOURCES.tsv)
  [ -n "$b" ] || { echo "NOT LISTED $p"; continue; }
  mkdir -p "$(dirname "$p")"
  curl -fsSL -o "$p" "https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/$REF/$p" || { echo "FETCH FAILED $p"; continue; }
  got=$( (printf 'blob %s\0' "$(stat -c%s "$p")"; cat "$p") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$b" ] && echo "OK $p" || echo "DIFFERS $p"
done; }
fetch $(awk -F'\t' 'NR>1 && $1 ~ /^v2\/vendor\/st\//{print $1}' REFERENCED-SOURCES.tsv)
fetch $(python3 v2/docs/review-packets/battery/evidence/check_manifest.py | awk '$1=="MISSING"{print $2}')
fetch v2/docs/handover/candidates/r8b.patch
python3 v2/docs/review-packets/battery/evidence/check_manifest.py | tail -3
(cd v2/ecad && python3 tools/rules_lib.py requirements | tail -3)
python3 v2/ecad/tools/rules_render.py --requirements --check
step "done"
date -u +%FT%TZ > /root/h2/zr.done
