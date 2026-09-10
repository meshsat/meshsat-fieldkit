#!/usr/bin/env bash
# kicad-cli's DRC with a contract (10 September 2026; round-two red teams, report 1 P0/P1). The first version of this file
# deleted the target first, which was the point, and then described a command it does not run: it said kicad-cli returns
# non-zero when it finds violations, which KiCad documents only for `--exit-code-violations`. Without that option a non-zero
# status is a TOOL failure, and this wrapper was ignoring it whenever a non-empty file happened to be there.
#
# The contract is report-generation only (the reviewers' Model A), because `hardset.py` owns every policy decision in this
# pipeline and KiCad's own severity count is not the gate:
#
#   the process must exit 0            a non-zero status is an infrastructure failure, never "the board is dirty"
#   the report must be newly written   into a temporary path, so a failed run can never leave the previous one in place
#   it must parse as JSON              and carry a `violations` list, or the gate downstream is reading something else
#   only then is it renamed            so a reader never sees a half-written or stale report
#
# Violations are not a failure here: they are what `hardset.py <report>` is for.
# Usage: drc.sh <board.kicad_pcb> <report.json> [extra kicad-cli arguments]
set -uo pipefail
B="$1"; R="$2"; shift 2
TMP="$R.part"; ERR="$R.err"
rm -f "$R" "$TMP" "$ERR"
kicad-cli pcb drc --severity-all --format json -o "$TMP" "$@" "$B" > "$ERR" 2>&1; X=$?
fail () { echo "drc: $1 for $B"; [ -s "$ERR" ] && { echo "drc: kicad-cli said:"; sed 's/^/drc:   /' "$ERR" | tail -12; }; rm -f "$TMP"; exit 1; }
[ "$X" -eq 0 ] || fail "kicad-cli exited $X"
[ -s "$TMP" ] || fail "kicad-cli wrote no report"
python3 - "$TMP" <<'PY' || fail "the report is not a DRC report"
import json, sys
d = json.load(open(sys.argv[1]))
if not isinstance(d, dict) or "violations" not in d: raise SystemExit(1)
PY
mv -f "$TMP" "$R"; rm -f "$ERR"
exit 0
