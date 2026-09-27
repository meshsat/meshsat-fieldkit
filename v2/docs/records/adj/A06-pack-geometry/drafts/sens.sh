#!/usr/bin/env bash
# A06 sensitivity: the fit verdicts under the generous and the pessimistic ends of the TBD allowances
cd /root/r2/A06-pack-geometry
for set in "0 0 0" "0.5 1.0 0" "0.5 1.0 1.37" "0.75 1.5 1.37" "1.0 2.0 1.37"; do
  read w j l <<< "$set"
  echo "=== WRAP $w per side, JOINT $j per section, U.FL lead $l"
  A06_WRAP=$w A06_JOINT=$j A06_LEAD=$l python3 pack_fit.py | sed -n '/SUMMARY/,$p' | grep -v SUMMARY | sed -E 's/\[origin.*worst base/.. worst base/' | cut -c1-260
done
