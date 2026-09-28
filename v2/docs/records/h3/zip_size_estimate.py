#!/usr/bin/env python3
"""An estimate of the size of a handover ZIP built from a commit, before it is built (MESHSAT-1357, 27 September 2026).

Written by the H3 pages worker. `handover_pack.py build` exits 3 when the ZIP is over `pack.yaml`'s `max_zip_bytes`
(52,428,800), and H2 was 51,894,737 bytes, 534,063 under it. H3 carries more pages, reviews and records than H2, so
whether it fits has to be known before the integrator builds it. This script does not build a snapshot and writes
nothing: it classifies the commit with the packer's own `plan` (so `pack.yaml` of THAT commit decides what is
included) and adds up what each included file would take in the ZIP.

How each file's compressed size is found:
  - a file whose git blob is the one H2.MANIFEST.tsv names for the same path takes the size H2.zip's own directory
    gives for it (exact: the packer compresses with deflate at level 9 and the bytes are the same);
  - any other file is compressed here with zlib at level 9, raw deflate, as `zipfile` does (exact to a few bytes);
  - the four files the packer generates at build time (MANIFEST.tsv, EXCLUDED.tsv, REFERENCED-SOURCES.tsv, SOURCE.txt)
    do not exist before the build: each is ESTIMATED as its size in H2.zip scaled by the count of rows it lists
    (included, excluded and referenced files; SOURCE.txt by the count of commit ids the handover pages name). That
    is the part of the total that is an estimate, and the script prints it apart;
  - per entry the ZIP adds 76 bytes and twice the entry's name, and 22 bytes once (it reproduces H2's 397,604 bytes of
    overhead exactly, which the script asserts).

It ends with the estimate, the cap, the margin, and the largest files that are new or changed since H2.

Usage (from the repository root): python3 v2/docs/records/h3/zip_size_estimate.py [commit, default HEAD] [version name]
"""
import csv, os, re, subprocess, sys, zipfile, zlib

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
sys.path.insert(0, os.path.join(ROOT, "v2", "ecad", "tools"))
sys.dont_write_bytecode = True
import handover_pack as hp                                   # noqa: E402  (the packer's own plan and rules)

AT = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
VERSION = sys.argv[2] if len(sys.argv) > 2 else "H3"
H2ZIP = os.path.join(ROOT, "v2", "release", "handover", "H2.zip")
H2MAN = os.path.join(ROOT, "v2", "release", "handover", "H2.MANIFEST.tsv")


def deflated(data):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    n = len(c.compress(data)) + len(c.flush())
    return min(n, len(data)) if False else n              # zipfile keeps the deflated stream even when it is longer


def main():
    z = zipfile.ZipFile(H2ZIP)
    h2 = {i.filename.split("/", 1)[1]: i for i in z.infolist()}
    h2_over = os.path.getsize(H2ZIP) - sum(i.compress_size for i in h2.values())
    calc = 76 * len(h2) + 2 * sum(len(("H2/" + k).encode()) for k in h2) + 22
    assert calc == h2_over, (calc, h2_over)
    man = {r["path"]: r for r in csv.DictReader(open(H2MAN, encoding="utf-8"), delimiter="\t")}

    git = hp.Git(ROOT)
    try:
        commit = git.commit(AT)
        pl = hp.plan(git, commit)
        tree, spec, got = pl["tree"], pl["spec"], pl["got"]
        if pl["loose"]:
            print("zip_size_estimate: %d file(s) unclassified, first %s: the build would be refused" %
                  (len(pl["loose"]), pl["loose"][0]))
            return 2
        files = {p: tree[p][1] for p, r in got.items() if r["action"] == "include"}       # path -> blob sha
        for pg in spec.get("pages") or []:
            if pg in tree:
                files[pg.rsplit("/", 1)[-1]] = tree[pg][1]
        n = {"include": 0, "exclude": 0, "reference": 0}
        for p, r in got.items():
            n[r["action"]] += 1
        total = reused = fresh = 0
        changed = []
        for p, sha in sorted(files.items()):
            if p in man and man[p]["git_blob_sha"] == sha and p in h2:
                total += h2[p].compress_size; reused += 1
            else:
                data = git.blob(sha)
                c = deflated(data)
                total += c; fresh += 1
                was = h2[p].compress_size if p in h2 else 0
                changed.append((c - was, c, was, len(data), p))
        gone = sorted(p for p in h2 if p not in files and p not in hp.META)
        texts = [git.blob(tree[p][1]).decode("utf-8", "replace") for p in sorted(tree)
                 if p.startswith("v2/docs/handover/") and p.endswith(".md")]
        ids = set()
        for t in texts:
            ids |= {m.group(1) for m in hp.COMMIT_ID.finditer(t)}
        h2_src = z.read("H2/SOURCE.txt").decode("utf-8", "replace")
        h2_ids = len(re.findall(r"^  [0-9a-f]{8}  \d{4}-\d\d-\d\d", h2_src, re.M))
    finally:
        git.close()

    n_h2 = {"include": 2224, "exclude": 4682, "reference": 483}     # H2's counts, from its snapshot commit's message
    meta = {
        "MANIFEST.tsv": h2["MANIFEST.tsv"].compress_size * (len(files) + 4) / float(len(h2)),
        "EXCLUDED.tsv": h2["EXCLUDED.tsv"].compress_size * n["exclude"] / float(n_h2["exclude"]),
        "REFERENCED-SOURCES.tsv": h2["REFERENCED-SOURCES.tsv"].compress_size * n["reference"] / float(n_h2["reference"]),
        "SOURCE.txt": h2["SOURCE.txt"].compress_size * max(1.0, len(ids) / float(h2_ids or 1)),
    }
    meta_total = int(round(sum(meta.values())))
    names = list(files) + list(meta)
    over = 76 * len(names) + 2 * sum(len(("%s/%s" % (VERSION, k)).encode()) for k in names) + 22
    est = total + meta_total + over
    cap = int(spec.get("max_zip_bytes") or 0)

    print("zip_size_estimate: commit %s (%s), version name %s" % (AT, commit[:8], VERSION))
    print("plan: %d included, %d excluded, %d referenced (H2: %d, %d, %d)" % (
        n["include"], n["exclude"], n["reference"], n_h2["include"], n_h2["exclude"], n_h2["reference"]))
    print("entries in the ZIP: %d files and root pages, and the 4 generated files (H2: %d entries)" % (len(files), len(h2)))
    print("files whose blob is H2's: %d, sizes taken from H2.zip; new or changed: %d, compressed here" % (reused, fresh))
    print("files of H2 that the commit's plan no longer includes: %d%s" % (len(gone), (" (%s)" % ", ".join(gone[:6])) if gone else ""))
    print("compressed file data: %d bytes" % total)
    print("the 4 generated files, ESTIMATED from H2's by row counts: %d bytes (%s); commit ids the pages name: %d (H2's "
          "timeline: %d)" % (meta_total, ", ".join("%s %d" % (k, round(v)) for k, v in meta.items()), len(ids), h2_ids))
    print("ZIP structure: %d bytes" % over)
    print("ESTIMATE: %d bytes; H2 was %d; cap %d; margin %d bytes (%s)" % (
        est, os.path.getsize(H2ZIP), cap, cap - est, "UNDER the cap" if est <= cap else "OVER THE CAP"))
    print("the estimate's uncertain part is the 4 generated files; were they 25 percent larger than estimated the ZIP "
          "would be %d bytes (%s)" % (est + meta_total // 4, "under" if est + meta_total // 4 <= cap else "OVER"))
    print("\nthe 30 files that add most to the ZIP since H2 (added bytes, compressed, compressed in H2, raw, path):")
    for d, c, was, raw, p in sorted(changed, reverse=True)[:30]:
        print("  %8d %8d %8d %9d  %s" % (d, c, was, raw, p))
    print("sum of what the new or changed files add: %d bytes" % sum(d for d, _, _, _, _ in changed))
    return 0 if est <= cap else 3


if __name__ == "__main__":
    sys.exit(main())
