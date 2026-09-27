#!/bin/bash
# r8int6: the independent netlist comparison of every board the set changed, the base's committed netlist against the
# integration head's, each held against the expected-change list of the one stream that changed that board, with that
# stream's own comparator (records/w3de/net_compare.py for A, E, D and P; records/r8b/integration/indep_cmp.py for B;
# records/w4c/parity/netcmp_w4c.py for C). A comparator that finds anything unexplained exits non-zero.
# Usage: indep_r8int6.sh <base commit> <out dir>   (run from the worktree root)
set -u
BASE=$1; O=$2; mkdir -p "$O"
R=v2/docs/records
declare -A NET=([a]=v2/ecad/pcb-a-power-a23/out/pcb-a-power.net [b]=v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net
                [c]=v2/ecad/pcb-c-display-c8/out/pcb-c-display.net [d]=v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net
                [e]=v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net [p]=v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net)
rc_all=0
for l in a b c d e p; do
  git show "$BASE:${NET[$l]}" > "$O/base-$l.net"
  case $l in
    a) cmd=(python3 $R/w3de/net_compare.py "$O/base-$l.net" "${NET[$l]}" --expect $R/w4ae/parity/expected-a-netlist.json) ;;
    e) cmd=(python3 $R/w3de/net_compare.py "$O/base-$l.net" "${NET[$l]}" --expect $R/w4ae/parity/expected-e-netlist.json) ;;
    d) cmd=(python3 $R/w3de/net_compare.py "$O/base-$l.net" "${NET[$l]}" --expect $R/w4dp/parity/expected-d-netlist.json) ;;
    p) cmd=(python3 $R/w3de/net_compare.py "$O/base-$l.net" "${NET[$l]}" --expect $R/w4dp/parity/expected-p-netlist.json) ;;
    b) cmd=(python3 $R/r8b/integration/indep_cmp.py "$O/base-$l.net" "${NET[$l]}" --expect $R/w4b/expected_w4b.json) ;;
    c) cmd=(python3 $R/w4c/parity/netcmp_w4c.py "$O/base-$l.net" "${NET[$l]}" $R/w4c/parity/expected-c-netlist.json) ;;
  esac
  "${cmd[@]}" > "$O/cmp-$l.txt" 2>&1; rc=$?
  echo "board $l: exit $rc; $(printf '%q ' "${cmd[@]}")" | tee -a "$O/summary.txt"
  tail -3 "$O/cmp-$l.txt" | sed 's/^/    /' | tee -a "$O/summary.txt"
  [ $rc -ne 0 ] && rc_all=1
done
exit $rc_all
