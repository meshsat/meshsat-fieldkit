#!/usr/bin/env bash
# int7 (MESHSAT-1357, 28 September 2026): the consolidated re-take of every schematic-phase reading on the set 6
# integration line at a4b157f076189abe97cec3822453be5e233df181, whose rules_lib.py changed (the validator's link-or-disposition rule), so every reading of a
# writer that imports it read TOOL_CHANGED. In a throwaway clone /root/int7/rtk on the KiCad box, as retake6 did it:
# the driver (--run --in-place --routed --json), then reliability.py per board and claims_check.py from v2/ecad, then the
# pack for the way back (tracked.patch, ignored-readings.tar, MANIFEST, SHA256SUMS). Writes /root/int7/done-retake.
set -u
D=/root/int7; C=$D/rtk; E=$C/v2/ecad; T=$E/tools; COMMIT=a4b157f076189abe97cec3822453be5e233df181
export PYTHONDONTWRITEBYTECODE=1
cd $D || exit 2
echo "start $(date -u +%FT%TZ)" > $D/retake-run.txt
git -C /root/r8int6/repo fetch -q $D/int7-a4b157f0.bundle fnd/int7:refs/heads/box-int7 || { echo "FETCH FAILED" >> $D/retake-run.txt; echo "3 $(date -u +%FT%TZ)" > $D/done-retake; exit 3; }
rm -rf $C && git clone -q /root/r8int6/repo $C && git -C $C checkout -q $COMMIT || { echo "CHECKOUT FAILED" >> $D/retake-run.txt; echo "3 $(date -u +%FT%TZ)" > $D/done-retake; exit 3; }
echo "HEAD $(git -C $C rev-parse HEAD)" >> $D/retake-run.txt
tar xf $D/int7-evidence-a4b157f0.tar -C $C
git -C $C status --short > $D/status-after-install.txt
echo "status lines after install: $(wc -l < $D/status-after-install.txt)" >> $D/retake-run.txt
( cd $C && git ls-files -o -i --exclude-standard -- v2 | sort | xargs -d "\n" sha256sum | sort -k2 > $D/ignored-before.sha256 )
# --- the driver
( cd $E && python3 tools/retake_schematic_phase.py --run --in-place --routed --json > $D/retake.json 2> $D/retake.log; echo "retake exit $?" >> $D/retake-run.txt )
# --- the other writers: reliability.py per board, claims_check.py from v2/ecad
L=$D/other-writers.log; : > $L
python3 - "$T" > $D/phase-dirs.txt <<'PY'
import sys, os
sys.path.insert(0, sys.argv[1])
import rules_status as S
m = S.manifest()
for L in m["boards"]:
    print(L, os.path.relpath(S._phase_dir(L, m), os.path.dirname(sys.argv[1])))
PY
while read LET PD; do
  P=$E/$PD
  echo "--- reliability board $LET in $PD" >> $L
  ( cd $P && VERDICT_DIR=$P/out timeout 600 python3 $T/reliability.py --ecad "$E" --board $LET >> $L 2>&1; echo "exit $?" >> $L )
  if [ -s $P/out/reliability.verdict.json ] && [ $P/out/reliability.verdict.json -nt $D/phase-dirs.txt ]; then
    cp $P/out/reliability.verdict.json $P/routed/reliability.verdict.json; echo "copied to $PD/routed/" >> $L
  else echo "NO READING WRITTEN for board $LET" >> $L; fi
done < $D/phase-dirs.txt
( cd $E && timeout 600 python3 tools/claims_check.py >> $L 2>&1; echo "claims_check exit $?" >> $L )
# --- the pack
O=$D/pack; rm -rf $O; mkdir -p $O; cd $C
git status --short > $O/status.txt
git diff --name-only | sort > $O/tracked-changed.lst
git diff --binary > $O/tracked.patch
git ls-files -o -i --exclude-standard -- v2 | sort | xargs -d "\n" sha256sum | sort -k2 > $O/ignored-after.sha256
python3 - $D/ignored-before.sha256 $O/ignored-after.sha256 $O/ignored-new-or-changed.lst <<'PY'
import sys
def load(p):
    d = {}
    for line in open(p, encoding="utf-8"):
        line = line.rstrip("\n")
        if line: d[line[66:]] = line[:64]
    return d
b, a = load(sys.argv[1]), load(sys.argv[2])
open(sys.argv[3], "w").write("".join(p + "\n" for p in sorted(a) if b.get(p) != a[p]))
print("ignored before %d, after %d, new or changed %d" % (len(b), len(a), sum(1 for p in a if b.get(p) != a[p])))
PY
grep -v -E '^v2/ecad/out/(rule-audit/|rules_status\.verdict\.json$|rules_complete\.verdict\.json$)|(^|/)__pycache__/|\.pyc$' $O/ignored-new-or-changed.lst > $O/ignored-readings.lst || true
tar cf $O/ignored-readings.tar --owner=0 --group=0 --numeric-owner -T $O/ignored-readings.lst
{ echo "# int7 ignored readings: path, bytes, sha256. Taken in /root/int7/rtk at $COMMIT."; while read f; do printf '%s\t%s\t%s\n' "$f" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -c1-64)"; done < $O/ignored-readings.lst; } > $O/MANIFEST
( cd $O && sha256sum ignored-readings.tar MANIFEST tracked.patch tracked-changed.lst > SHA256SUMS )
echo "end $(date -u +%FT%TZ)" >> $D/retake-run.txt
echo "0 $(date -u +%FT%TZ)" > $D/done-retake
