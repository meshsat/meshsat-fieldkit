#!/bin/bash
# The stability run of record l9t5's connected P0 candidate (MESHSAT-1357; cx46 item 14): every output of the P0 cascade regenerated in
# dependency order through the coordinator's regen_out.py, whose rules hold for each output: R1 both of its two runs exit 0, R2 the
# output is non-empty and ends with a newline, R3 the two runs are byte-identical, R4 every pin the output prints equals the start of
# that input's sha256; otherwise the committed output is left as it was. The cascade runs twice; the second pass must print "already
# identical" for every output (the stability claim of the README).
# Usage: regen_cascade.sh <worktree> <regen_out.py>     (regen_out.py is the coordinator's tool, outside the tree)
W="$1"; RO="$2"; R=v2/docs/records
for pair in l9stk/l9stk_copper l9stk/l9stk_protection l9pwr/l9pwr_budget l8r2/l8r2_gndret l8r2/l8r2_p0 l8r2/l8r2_dist l9t5/l9t5_case \
            l9t5/l9t5_a1 l9t5/l9t5_drafts l9t5/l9t5_t10 l9t5/l9t5_cm5 l9t5/l9t5_f01 l9t5/l9t5_f01_drafts l8r2/l8r2_drafts efuse/efuse_check \
            l6r2/l6r2_passives l4e7/l4e7_p0sol l9t5/l9t5_connected; do
  nice -n 19 python3 -B "$RO" "$W" $R/$pair.py $R/$pair.out || { echo "FAILED $pair"; exit 1; }
done
echo DONE
