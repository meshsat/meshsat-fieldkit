#!/usr/bin/env bash
# retake6, step 6 on the box (MESHSAT-1357): what the re-take changed, packed for the way back.
#   tracked.patch          git diff --binary of the clone against 73ae2f21 (readings under routed/, the generated pages,
#                          the two rebinds); tracked-changed.lst names the files
#   ignored-readings.tar   every gitignored file under v2 that is new or changed against the restored candidate evidence
#                          (ignored-before.sha256), EXCEPT the audit's own outputs (v2/ecad/out/rule-audit/, and
#                          rules_status and rules_complete beside it), which rules_status re-takes in whichever tree
#                          the pages are judged in and which name verdicts by this clone's absolute paths
#   MANIFEST               path, bytes, sha256 of every file in the tar
#   audit-box.tar          the clone's audit as the pages here were rendered from it: for comparison, never installed
set -eu
D=/root/retake6; C=$D/rtk; O=$D/pack; rm -rf $O; mkdir -p $O
cd $C
test "$(git rev-parse HEAD)" = "73ae2f2104c98bc39e5194f82a31e8862e12dbb5"
git status --short > $O/status.txt
test -z "$(grep -v '^ M ' $O/status.txt || true)"          # nothing untracked, staged, deleted or renamed
git diff --name-only | sort > $O/tracked-changed.lst
git diff --binary > $O/tracked.patch
git ls-files -o -i --exclude-standard -- v2 | sort > $O/ignored-after.lst
xargs -d "\n" sha256sum < $O/ignored-after.lst | sort -k2 > $O/ignored-after.sha256
cp $D/ignored-before.sha256 $O/ignored-before.sha256
# compared by a parser of the two sha256sum listings (a first version used comm on lists sorted by another key, which
# comm refuses to compare, and named 820 of 910 files as changed)
python3 - $O/ignored-before.sha256 $O/ignored-after.sha256 $O/ignored-new-or-changed.lst $O/ignored-gone.lst <<'PY'
import sys
def load(p):
    d = {}
    for line in open(p, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line: continue
        sha, path = line[:64], line[66:]
        assert len(sha) == 64 and line[64:66] == "  " and path not in d, line
        d[path] = sha
    return d
b, a = load(sys.argv[1]), load(sys.argv[2])
open(sys.argv[3], "w", encoding="utf-8").write("".join(p + "\n" for p in sorted(a) if b.get(p) != a[p]))
open(sys.argv[4], "w", encoding="utf-8").write("".join(p + "\n" for p in sorted(b) if p not in a))
print("ignored before %d, after %d, new %d, changed %d, gone %d" % (len(b), len(a), sum(1 for p in a if p not in b),
      sum(1 for p in a if p in b and b[p] != a[p]), sum(1 for p in b if p not in a)))
PY
grep -v -E '^v2/ecad/out/(rule-audit/|rules_status\.verdict\.json$|rules_complete\.verdict\.json$)|(^|/)__pycache__/|\.pyc$' $O/ignored-new-or-changed.lst > $O/ignored-readings.lst || true
grep -E '^v2/ecad/out/(rule-audit/|rules_status\.verdict\.json$|rules_complete\.verdict\.json$)' $O/ignored-new-or-changed.lst > $O/audit-box.lst || true
# none of them tracked, all of them ignored
test -z "$(git ls-files -- $(cat $O/ignored-readings.lst))"
test "$(git check-ignore $(cat $O/ignored-readings.lst) | wc -l)" = "$(wc -l < $O/ignored-readings.lst)"
tar cf $O/ignored-readings.tar --owner=0 --group=0 --numeric-owner -T $O/ignored-readings.lst
tar cf $O/audit-box.tar --owner=0 --group=0 --numeric-owner -T $O/audit-box.lst
{ echo "# retake6 ignored readings: path, bytes, sha256. Taken in /root/retake6/rtk at 73ae2f21 on 27 September 2026."
  while read f; do printf '%s\t%s\t%s\n' "$f" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -c1-64)"; done < $O/ignored-readings.lst; } > $O/MANIFEST
( cd $O && sha256sum ignored-readings.tar MANIFEST tracked.patch tracked-changed.lst audit-box.tar > SHA256SUMS )
wc -l $O/*.lst; cat $O/SHA256SUMS; ls -la $O
date -u +%FT%TZ > $D/done-pack
