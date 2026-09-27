#!/usr/bin/env bash
# The golden schematic test (10 September 2026, MESHSAT-862, red team C2): every board regenerates to the same file, and a
# change of the engine changes no board. Two properties, both cheap, both of which the project had no way to check before:
#   1. determinism: two runs of one generator are byte identical (kisch seeds its uuids from the project name);
#   2. no drift: the generated schematic matches the one committed beside the board, uuids aside.
# A change that is meant to alter a schematic makes this fail once; commit the new schematic and it passes again.
# Usage: tests/golden_sch.sh [board letters, default a b c d e p]   (runs where the KiCad symbol libraries are)
set -uo pipefail
T="$(cd "$(dirname "$0")/.." && pwd)"; E="$(dirname "$T")"; W="$(mktemp -d)"; RC=0
norm () { sed -E 's/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/UUID/g' "$1"; }
for k in ${*:-a b c d e p}; do
  case $k in a) P=pcb-a-power;; b) P=pcb-b-compute;; c) P=pcb-c-display;; d) P=pcb-d-aprs;; e) P=pcb-e1-dock;; p) P=pcb-p-pack;; *) echo "unknown board $k"; RC=2; continue;; esac
  ( cd "$E/$P" && python3 "$T/gen_sch_$k.py" "$W/$k-1.kicad_sch" "$P" > "$W/$k.log" 2>&1 && python3 "$T/gen_sch_$k.py" "$W/$k-2.kicad_sch" "$P" >> "$W/$k.log" 2>&1 ) || { echo "FAIL $P: the generator refused (see $W/$k.log)"; tail -3 "$W/$k.log"; RC=1; continue; }
  cmp -s "$W/$k-1.kicad_sch" "$W/$k-2.kicad_sch" || { echo "FAIL $P: two runs differ (the uuids are not deterministic)"; RC=1; }
  norm "$E/$P/$P.kicad_sch" > "$W/$k-committed.norm"; norm "$W/$k-1.kicad_sch" > "$W/$k-new.norm"
  if diff -q "$W/$k-committed.norm" "$W/$k-new.norm" >/dev/null; then echo "PASS $P: deterministic, and identical to the committed schematic"
  else echo "FAIL $P: $(diff "$W/$k-committed.norm" "$W/$k-new.norm" | grep -c '^[<>]') lines differ from the committed schematic"; RC=1; fi
done
echo "golden_sch: $( [ $RC -eq 0 ] && echo "every board matches" || echo "see the FAIL lines above" ) (work dir $W)"
exit $RC
