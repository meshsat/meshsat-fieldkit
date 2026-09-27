#!/bin/bash
# r8int6: apply one stream onto the integration worktree, file its records, render the pages twice and validate.
# Usage: stream_r8int6.sh <stream>
set -e
SP=$SP
R=$SP/r8int6; W=$SP/wt/r8int6; s=$1; K=$R/kit/$s
$R/kitprep_r8int6.sh $s
"$K/apply_${s}_r8int6.sh" "$W" "$SP/wt/$s"
case $s in
  w4b|w4c) python3 $R/common/record_ids_r8int6.py $s "$W" "$K" ;;
  w4ae|w4dp) python3 $R/common/record_ids_r8int6.py $s "$W" "$K" README.md ;;
esac
cd "$W"
python3 $R/common/file_stream_r8int6.py "$K" $s "$(cat $R/rows/$s.row)" "$(cat $R/rows/$s.cited)" $(cat $R/rows/$s.excl)
cd "$W/v2/ecad/tools" && python3 rules_render.py > /dev/null 2>&1; python3 rules_render.py 2>&1 | grep -v "^rules_render: wrote" || true
$R/validate.sh
