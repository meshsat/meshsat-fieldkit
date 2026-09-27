#!/usr/bin/env bash
# The schematic-phase readings w3de took on boards D and E (MESHSAT-1357, 27 September 2026), on a tree root given as
# $1 and into the verdict directory $2, never the tree's own evidence (safe_lines and erc_gate also write beside the
# netlist in the tree they are pointed at, which is why $1 is always a scratch extraction). Every gate here reads a netlist and its intent
# file (no pcbnew); check_contracts reads every board's committed netlist in the tree it is pointed at.
#   run_gates.sh <tree root holding v2/ecad> <verdict dir>
set -uo pipefail
T="$1/v2/ecad"; V="$2"; mkdir -p "$V"; cd "$T" || exit 2
export VERDICT_DIR="$V" PYTHONDONTWRITEBYTECODE=1
D=pcb-d-aprs-d9/out/pcb-d-aprs; E=pcb-e1-dock-e7/out/pcb-e1-dock
for x in "d $D" "e $E"; do set -- $x; L=$1; N=$2
  mkdir -p "$V/$L"
  echo "== $L intent_rails (PWR-001)"; python3 tools/intent_checks.py --netlist $N.net --intent $N-intent.json --out-dir "$V/$L" | grep -E '^(FAIL|UNDECIDED|CENSUS|verdict)' | cut -c1-260
  echo "== $L power_path";      python3 tools/power_path.py $N.net --intent $N-intent.json --out-dir "$V/$L" | grep -E 'SHORT|NOT DECLARED|verdict' | cut -c1-260
  echo "== $L power_sequence";  VERDICT_DIR="$V/$L" python3 tools/power_sequence.py $N.net --intent $N-intent.json --out-dir "$V/$L" 2>&1 | grep -E 'unresolved|deadlock|verdict|rail\(s\)' | cut -c1-260
  echo "== $L derate";          VERDICT_DIR="$V/$L" python3 tools/derate.py $N.net --intent $N-intent.json --out-dir "$V/$L" 2>&1 | grep -E '^(FAIL|verdict)|UNDECLARED' | cut -c1-260
  echo "== $L safe_lines";      VERDICT_DIR="$V/$L" python3 tools/safe_lines.py $N.net $L 2>&1 | grep -E 'FAIL|verdict' | cut -c1-260
  echo "== $L port_protect";    VERDICT_DIR="$V/$L" python3 tools/port_protect.py $N.net $L 2>&1 | grep -E 'FAIL|verdict' | cut -c1-260
  P=$(dirname $(dirname $N)); S=$(basename $N)
  echo "== $L erc_gate";        (cd $P && VERDICT_DIR="$V/$L" python3 ../tools/erc_gate.py . $S 2>&1 | grep -E 'erc_gate|verdict' | cut -c1-260)
done
echo "== check_contracts (the set, and every board's and inhibit chain's verdict it writes)"
mkdir -p "$V/set"; VERDICT_DIR="$V/set" python3 tools/check_contracts.py "$T" > "$V/set/check_contracts.log" 2>&1
grep -E '^FAIL' "$V/set/check_contracts.log" | grep -v 'RF-002' | cut -c1-300
echo "   (RF-002 FAIL lines: $(grep -cE '^FAIL.*RF-002' "$V/set/check_contracts.log"), board B's, recorded in the log)"
echo "== energy_chain"; VERDICT_DIR="$V/set" python3 tools/energy_chain.py > "$V/set/energy_chain.log" 2>&1
grep -E 'SHORE_INPUT|^verdict' "$V/set/energy_chain.log" | cut -c1-300
python3 - "$V" <<'PY'
import json, glob, os, sys
for f in sorted(glob.glob(os.path.join(sys.argv[1], "**", "*.verdict.json"), recursive=True)):
    d = json.load(open(f)); rel = os.path.relpath(f, sys.argv[1])
    print("VERDICT %-44s %-13s %s" % (rel, d.get("verdict") or d.get("result"), json.dumps(d.get("counts"))[:150]))
PY
