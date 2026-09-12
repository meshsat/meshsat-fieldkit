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
# WHAT A DRC COSTS. finish.sh calls this twelve times and the project that will not quote a number without
# what it was measured on did not know what its own finish cost (red team round three H3). The seconds and
# the board hash go beside the report, so a stage runner can see where a finish spends its time.
_T0=$(date +%s)
TMP="$R.part"; ERR="$R.err"
rm -f "$R" "$TMP" "$ERR"
# A board file whose .kicad_pro is not beside it under its own stem is judged against the DEFAULT net class, and on
# these boards that is hundreds of false clearance and via violations with nothing saying so. It has cost this
# pipeline twice: a copied project directory on 7 September (B19 read the B15-era file: 396 class assignments
# against None), and on 12 September cont_route.sh's `-before` copy, which printed "before hard 1074" for a board
# the finish had just measured at hard 0. The check belongs at the one place that judges, not in each caller.
if [ "${DRC_REQUIRE_PROJECT:-1}" != 0 ] && [ ! -s "${B%.kicad_pcb}.kicad_pro" ]; then
  echo "drc: no ${B%.kicad_pcb}.kicad_pro beside $B: every net class would be the default one."
  echo "drc: copy the project file under the board's own stem, or set DRC_REQUIRE_PROJECT=0 to judge it that way deliberately."
  exit 1
fi
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

_T1=$(date +%s)
python3 - "$R" "$B" "$((_T1 - _T0))" <<'PY2' 2>/dev/null || true
import sys, json, os, hashlib
rep, board, secs = sys.argv[1], sys.argv[2], int(sys.argv[3])
try:
    v = json.load(open(rep)).get("violations", [])
except Exception:
    v = []
h = hashlib.sha256(open(board, "rb").read()).hexdigest()[:16] if os.path.exists(board) else ""
json.dump({"seconds": secs, "violations": len(v), "board_sha": h, "report": os.path.basename(rep)},
          open(os.path.join(os.path.dirname(rep) or ".", "drc-cost.json"), "w"), indent=1)
print("drc: %d s, %d violation(s), board %s" % (secs, len(v), h))
PY2
