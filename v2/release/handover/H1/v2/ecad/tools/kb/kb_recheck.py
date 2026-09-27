#!/usr/bin/env python3
"""kb_recheck.py, currency as a dated check rather than a claim (MESHSAT-862, 11 September 2026).

Nothing offline can prove a datasheet is the current revision. What can be stated is the date it was
last compared against the vendor, and that is a fact rather than a belief. This re-fetches a document
from the URL recorded in v2/vendor/sources.txt, compares the bytes and the revision string, and
records the result and the date.

Four outcomes, and only the first two are answers:

  UNCHANGED   the vendor still serves the same bytes
  CHANGED     the vendor serves something else: the revision moved, or the file was re-issued. This is
              not automatically bad and is never auto-applied; it is a document to look at
  UNREACHABLE the host refuses this runner (st.com, cs.amphenol.com, littelfuse.com and nkkswitches.com
              all do) or the recorded source is a folder-level note rather than a URL. NEVER a pass:
              an unreachable host means unknown, and unknown must not read as verified
  NO URL      the source is recorded in prose, which is true of every document that predates the fetch
              log; those can be re-checked only by hand

Usage: kb_recheck.py [--limit N] [--vendor ti] [--out-dir out]
"""
import sys, os, re, subprocess, tempfile, hashlib, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import kbdb, kbenv, kb_ingest       # noqa: E402
import verdict                       # noqa: E402

URL = re.compile(r"https?://\S+")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def fetch(url):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        path = tf.name
    r = subprocess.run(["curl", "-sL", "--compressed", "-A", UA, "-o", path, "-w", "%{http_code}",
                        "--max-time", "90", url], capture_output=True, text=True, timeout=180)
    code = r.stdout.strip()
    kind = subprocess.run(["file", "-b", "--mime-type", path], capture_output=True, text=True).stdout.strip()
    if kind != "application/pdf" or os.path.getsize(path) < 10000:
        os.unlink(path)
        return None, code
    return path, code


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--vendor")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    try:
        db = kbdb.connect()
    except kbenv.InfraFail as e:
        print(e, file=sys.stderr)
        return verdict.write("kb_recheck", verdict.INCONCLUSIVE, note=str(e), out_dir=a.out_dir)

    # the LIKE pattern goes through as a PARAMETER: a literal '%.pdf' in the SQL string collides with
    # the driver's own %-formatting and raises before the query is ever sent
    sql = ("SELECT id, relpath, sha256, revision, source FROM documents WHERE present=1 "
           "AND source IS NOT NULL AND relpath LIKE %s" + (" AND vendor=%s" if a.vendor else "")
           + " ORDER BY relpath")
    params = ("%.pdf", a.vendor) if a.vendor else ("%.pdf",)
    with db.cursor() as c:
        c.execute(sql, params)
        rows = c.fetchall()
    if a.limit:
        rows = rows[:a.limit]

    counts = {"unchanged": 0, "changed": 0, "unreachable": 0, "no_url": 0}
    changed, unreachable = [], []
    for doc_id, rel, sha, rev, src in rows:
        m = URL.search(src or "")
        if not m:
            counts["no_url"] += 1
            continue
        url = m.group(0).rstrip(").,;")
        path, code = fetch(url)
        if not path:
            counts["unreachable"] += 1
            unreachable.append("%s (http %s) %s" % (rel, code, url[:70]))
            continue
        new_sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        pages = kb_ingest.pdf_pages(path)
        new_rev = kb_ingest.revision_of(pages)
        os.unlink(path)
        same = (new_sha == sha)
        if same:
            counts["unchanged"] += 1
        else:
            counts["changed"] += 1
            changed.append("%s: revision here %r, vendor now serves %r" % (rel, rev, new_rev))
        with db.cursor() as c:
            c.execute("UPDATE documents SET checked_at=NOW() WHERE id=%s", (doc_id,))
        print("%-12s %-56s %s" % ("UNCHANGED" if same else "CHANGED", rel[:56],
                                  ("" if same else "vendor revision %r" % new_rev)))
    for u in unreachable:
        print("UNREACHABLE  %s" % u)
    counts["checked"] = counts["unchanged"] + counts["changed"]
    counts["as_of"] = datetime.date.today().isoformat()
    # CHANGED is information, not a failure: a vendor re-issuing a sheet is normal and the decision to
    # take the new one is a person's. UNREACHABLE is not a pass either, so the verdict is INCONCLUSIVE
    # when nothing could be compared at all.
    res = verdict.PASS if counts["checked"] else verdict.INCONCLUSIVE
    return verdict.write("kb_recheck", res, counts=counts, denominator=len(rows),
                         evidence=(changed + unreachable)[:30], out_dir=a.out_dir,
                         note="%d changed at the vendor, %d unreachable, %d recorded without a URL"
                              % (counts["changed"], counts["unreachable"], counts["no_url"]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
