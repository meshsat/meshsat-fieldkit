#!/usr/bin/env bash
# retake6, step 3 (MESHSAT-1357): the consolidated re-take of every schematic-phase reading on the set 6 netlists,
# in the throwaway clone /root/retake6/rtk at 73ae2f21 on the KiCad box, as REGENERATE.md section 9 writes it.
# Run under nohup; writes /root/retake6/done-retake when it ends, whatever the exit status.
set -u
D=/root/retake6; C=$D/rtk
export PYTHONDONTWRITEBYTECODE=1
cd $C/v2/ecad || exit 2
{ echo "HEAD $(git -C $C rev-parse HEAD)"; echo "status lines before: $(git -C $C status --short | wc -l)"; echo "start $(date -u +%FT%TZ)"; } > $D/retake-run.txt
python3 tools/retake_schematic_phase.py --run --in-place --routed --json > $D/retake.json 2> $D/retake.log
RC=$?
{ echo "retake exit $RC"; echo "end $(date -u +%FT%TZ)"; echo "HEAD $(git -C $C rev-parse HEAD)"; } >> $D/retake-run.txt
git -C $C status --short > $D/retake-status-after.txt
echo "$RC $(date -u +%FT%TZ)" > $D/done-retake
