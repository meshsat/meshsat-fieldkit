#!/usr/bin/env bash
# MESHSAT-1357 round 8 stream d, phase 2: parity, every difference traced, the gate tables of both trees and the
# cross-board readings. /root/r8-d ONLY; reads the trees phase 1 left, writes only under out/.
set -uo pipefail
W=/root/r8-d; IN=$W/incoming; T=$W/repo; B=$W/base; OUT=$W/out
export TMPDIR=$W/tmp; mkdir -p "$TMPDIR"
exec > >(tee -a "$OUT/set.log") 2>&1
echo "r8d-set: start $(date -u +%FT%TZ)"
N=pcb-d-aprs; DD=pcb-d-aprs-d9
git -C "$T" status --porcelain > "$OUT/tree-status-before-set.txt"
RC=$B/v2/ecad/tools/regen_compare.py; C=$OUT/compare; mkdir -p "$C"
v () { python3 -c "import json,sys
d=json.load(open(sys.argv[1]))
print(d.get('verdict') or d.get('result') or d.get('status') or '?')" "$1" 2>/dev/null || echo "?"; }
R=$OUT/base/ref
for S in base new; do F=$OUT/$S/files
  for k in "schematic $R/$N.kicad_sch $F/$N.kicad_sch" "netlist $R/$N.net $F/$N.net" "intent $R/$N-intent.json $F/$N-intent.json" \
           "provenance $R/$N.net.prov.json $F/$N.net.prov.json" "bom $R/$N-bom.csv $F/$N-bom.csv" "erc $R/$N-erc.json $F/$N-erc.json"; do
    set -- $k; o="$C/${S}_vs_committed_$1.json"
    python3 "$RC" pair "$1" "$2" "$3" > "$o" 2>&1; ec=$?
    printf "%-18s %-10s exit %s  %s\n" "${S}_vs_committed" "$1" "$ec" "$(v "$o")"
  done
done
for k in schematic:$N.kicad_sch netlist:$N.net intent:$N-intent.json provenance:$N.net.prov.json bom:$N-bom.csv erc:$N-erc.json; do
  o="$C/new_vs_base_${k%%:*}.json"; python3 "$RC" pair "${k%%:*}" "$OUT/base/files/${k#*:}" "$OUT/new/files/${k#*:}" > "$o" 2>&1; ec=$?
  printf "%-18s %-10s exit %s  %s\n" new_vs_base "${k%%:*}" "$ec" "$(v "$o")"
done
for S in base new; do printf "bytes %-4s schematic %s  netlist %s  intent %s\n" "$S" \
  "$(cmp -s "$R/$N.kicad_sch" "$OUT/$S/files/$N.kicad_sch" && echo IDENTICAL || echo differs)" \
  "$(cmp -s "$R/$N.net" "$OUT/$S/files/$N.net" && echo IDENTICAL || echo differs)" \
  "$(cmp -s "$R/$N-intent.json" "$OUT/$S/files/$N-intent.json" && echo IDENTICAL || echo differs)"; done
python3 "$IN/t/r8d_par.py" "$OUT" "$T/v2/ecad/tools" > "$OUT/par.txt" 2>&1; echo "r8d_par exit $?" >> "$OUT/par.txt"
grep -E "^PAIR|^TOTAL|r8d_par exit" "$OUT/par.txt"
for S in base new; do RR=$([ $S = base ] && echo "$B" || echo "$T")
  printf "sidecar %-4s " "$S"; ( cd "$RR/v2/ecad" && python3 tools/sch_prov.py read "$DD/out/$N.net" d ) | cut -c1-240
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print('   generator_sha', d.get('generator_sha'), 'files', d.get('generator_file_sha'), 'schematic_sha256', d.get('schematic_sha256'))" "$RR/v2/ecad/$DD/out/$N.net.prov.json"
done
python3 - "$OUT" <<'PY' > "$OUT/gates.txt" 2>&1
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
b, i = read(os.path.join(O, "base", "v")), read(os.path.join(O, "new", "v"))
for k in sorted(set(b) | set(i)):
    mark = "  " if b.get(k) == i.get(k) else "* "
    print("%s%-28s base: %s\n%s  %-28s new : %s" % (mark, k, b.get(k), " " * len(mark), "", i.get(k)))
PY
cat "$OUT/gates.txt"
for S in base new; do RR=$([ $S = base ] && echo "$B" || echo "$T"); O=$OUT/cross/$S; mkdir -p "$O"
  ( cd "$RR/v2/ecad" && VERDICT_DIR="$O" python3 tools/check_contracts.py "$RR/v2/ecad" > "$O/check_contracts.log" 2>&1; echo "exit $?" >> "$O/check_contracts.log" )
  ( cd "$RR/v2/ecad/tools" && VERDICT_DIR="$O" python3 energy_chain.py --ecad "$RR/v2/ecad" > "$O/energy_chain.log" 2>&1; echo "exit $?" >> "$O/energy_chain.log" )
  echo "r8d: $S check_contracts: $(grep -vE '^(PASS|FAIL|UNDECIDED|UNJUDGED)  ' "$O/check_contracts.log" | tail -4 | tr '\n' ' ' | cut -c1-400)"
  echo "r8d: $S energy_chain: $(tail -3 "$O/energy_chain.log" | tr '\n' ' ' | cut -c1-300)"
  for f in "$O"/check_contracts*.verdict.json "$O"/inhibit_chain*.verdict.json "$O"/energy_chain*.verdict.json; do
    [ -e "$f" ] && python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print('   ', sys.argv[1].split('/')[-1][:-13], d.get('verdict'), d.get('denominator'), d.get('counts'))" "$f"
  done
done
diff <(grep -E "^(PASS|FAIL|UNDECIDED|UNJUDGED) " "$OUT/cross/base/check_contracts.log" | sort) <(grep -E "^(PASS|FAIL|UNDECIDED|UNJUDGED) " "$OUT/cross/new/check_contracts.log" | sort) > "$OUT/cross/check_contracts.diff"; echo "check_contracts line diff (base -> new): $(wc -l < "$OUT/cross/check_contracts.diff") lines"; head -40 "$OUT/cross/check_contracts.diff"
for S in base new; do printf "erc %s: %s\n" "$S" "$(grep -m1 -E '^verdict|^ERC|clean|BLOCK|allowed' "$OUT/$S/v/erc_gate.log" | cut -c1-200)"; done
python3 - "$OUT" <<'PY'
import json, sys, collections
O = sys.argv[1]
for s in ("base", "new"):
    d = json.load(open("%s/%s/files/pcb-d-aprs-erc.json" % (O, s)))
    v = [x for sh in d.get("sheets", []) for x in sh.get("violations", [])] + d.get("violations", [])
    c = collections.Counter((x.get("type"), x.get("severity")) for x in v)
    print("erc %s: %d violations %s" % (s, len(v), dict(sorted(c.items()))))
PY
( cd "$OUT/new/files" && sha256sum * ) | sed "s#^#new #"; ( cd "$OUT/base/files" && sha256sum * ) | sed "s#^#base #"
git -C "$T" status --porcelain > "$OUT/tree-status-after-set.txt"
cmp -s "$OUT/tree-status-before-set.txt" "$OUT/tree-status-after-set.txt" && echo "r8d: tree status untouched by phase 2" || { echo "r8d: WARNING tree status changed in phase 2"; diff "$OUT/tree-status-before-set.txt" "$OUT/tree-status-after-set.txt"; }
echo "r8d-set: done $(date -u +%FT%TZ)"
touch "$W/set.flag"
