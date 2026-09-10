#!/usr/bin/env python3
"""kb_verify.py, the enforcers of the datasheet knowledge base (MESHSAT-862, 10 September 2026).

A store like this fails silently. Nothing errors when a document is missing, when a folder's
retirement was never recorded, when the embedding host was swapped for one that produces vectors in
a different space, or when a query that used to find the right page stops finding it: every one of
those looks exactly like "no hits". So each rule the store depends on has a check here, and the
checks are the only reason to believe an answer from it.

  --coverage  every file on disk is a row, every row is chunked or carries a declared reason, every
              file has a declared status, no PDF is blind and undeclared, no current datasheet is
              thin (text so sparse the pages are pictures) without saying so.
  --space     re-embeds stored chunks and compares against what the store holds. The model is the
              contract, not the host: a different model still answers, still returns 768 numbers,
              and quietly ruins every distance. Median cosine must be at least 0.9999.
  --gold      ten real questions with the document that answers each, found mechanically from the
              indexed text. A retrieval that stops working is otherwise indistinguishable from a
              question nobody asked.
  --parts     a listing, not a gate: parts on the shipped BOMs for which this store holds no
              datasheet, which is the honest inventory of what cannot be checked here.

Default runs coverage, space and gold, and writes out/kb_verify.verdict.json with the exit code
equal to the verdict. INCONCLUSIVE when the store or the embedding host is unreachable, which is a
normal state on a host that has no route to either, and is never a pass.

Usage: kb_verify.py [--coverage] [--space] [--gold] [--parts] [--k 6] [--sample 60] [--out-dir out]
"""
import sys, os, json, glob, csv, re, argparse, statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kbdb, kbembed, kbenv, kb_search      # noqa: E402
import verdict                               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "vendor"))
RELEASE = os.path.normpath(os.path.join(HERE, "..", "..", "..", "release"))
GOLD = os.path.join(HERE, "gold.json")
THIN_CHARS_PER_PAGE = 120      # below this a "text" PDF is pictures with page numbers on them
SPACE_MEDIAN_MIN = 0.9999


def _disk_files():
    out = set()
    for d, dirs, fs in os.walk(VENDOR):
        dirs[:] = [x for x in dirs if x not in (".git", "__pycache__")]
        for f in fs:
            out.add(os.path.relpath(os.path.join(d, f), VENDOR))
    return out


def check_coverage(db):
    """Rows against files, chunks against documents, declarations against reality."""
    fails, counts = [], {}
    disk = _disk_files()
    with db.cursor() as c:
        c.execute("SELECT relpath, status, text_source, no_text_reason, pages, "
                  "(SELECT COUNT(*) FROM chunks WHERE document_id=documents.id) AS n "
                  "FROM documents WHERE present=1")
        rows = c.fetchall()
    have = {r[0] for r in rows}
    counts["files_on_disk"] = len(disk)
    counts["rows_present"] = len(rows)
    for rel in sorted(disk - have):
        fails.append("on disk, not in the store: %s" % rel)
    for rel in sorted(have - disk):
        fails.append("in the store as present, not on disk: %s" % rel)

    noindex = set()
    ni = os.path.join(VENDOR, "vendor-noindex.txt")
    if os.path.exists(ni):
        for line in open(ni):
            line = line.strip()
            if line and not line.startswith("#") and "#" in line:
                path, reason = line.split("#", 1)
                if path.strip() and reason.strip():
                    noindex.add(path.strip())
    counts["declared_noindex"] = len(noindex)

    thin, blind, undeclared, chunked = [], [], [], 0
    for rel, status, src, reason, pages, n in rows:
        if status == "undeclared":
            undeclared.append(rel)
        if n:
            chunked += 1
        ext = os.path.splitext(rel)[1].lower()
        if ext == ".pdf" and not n and rel not in noindex:
            blind.append(rel)
    counts["chunked"] = chunked
    with db.cursor() as c:
        # a current datasheet whose pages carry almost no text is present, searchable and useless;
        # it must be declared like a blind one rather than quietly counted as covered
        c.execute("SELECT d.relpath, d.pages, COALESCE(SUM(CHAR_LENGTH(c.text)),0) FROM documents d "
                  "LEFT JOIN chunks c ON c.document_id=d.id "
                  "WHERE d.present=1 AND d.status='current' AND d.pages IS NOT NULL AND d.pages>0 "
                  "GROUP BY d.id HAVING COALESCE(SUM(CHAR_LENGTH(c.text)),0) < d.pages * %s",
                  (THIN_CHARS_PER_PAGE,))
        for rel, pages, chars in c.fetchall():
            if rel not in noindex:
                thin.append("%s (%d pages, %d chars of text)" % (rel, pages, chars))
    counts["thin_undeclared"] = len(thin)
    counts["blind_undeclared"] = len(blind)
    counts["status_undeclared"] = len(undeclared)
    fails += ["no text layer and no declared reason: %s" % r for r in blind]
    fails += ["current datasheet with almost no extractable text and no declared reason: %s" % r for r in thin]
    fails += ["no declared status (current, v1, retired or tooling): %s" % r for r in undeclared]

    with db.cursor() as c:
        c.execute("SELECT COUNT(*) FROM chunks")
        counts["chunks"] = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM chunk_embeddings")
        counts["embedded"] = c.fetchone()[0]
        c.execute("SELECT sha256, COUNT(*) n, GROUP_CONCAT(relpath SEPARATOR ' = ') FROM documents "
                  "WHERE present=1 GROUP BY sha256 HAVING n > 1")
        dups = c.fetchall()
    counts["duplicate_files"] = len(dups)
    # Duplicates are a FAIL unless declared. Two of the pairs here were created by me on 10 September,
    # fetching documents this tree already held, because the lookup that said they were missing was
    # wrong. A store that quietly accepts the same bytes twice cannot tell you what it holds.
    dup_ok = set()
    dupfile = os.path.join(VENDOR, "duplicates-allowed.txt")
    if os.path.exists(dupfile):
        for line in open(dupfile):
            line = line.strip()
            if line and not line.startswith("#") and "#" in line:
                k, r = line.split("#", 1)
                if k.strip() and r.strip():
                    dup_ok.add(k.strip())
    for sha, n, names in dups:
        if sha not in dup_ok:
            fails.append("the same bytes are filed twice and it is not declared: %s" % names[:150])

    # Provenance and revision. A blank field and a document that declares no revision are different
    # facts, so `unknown` has to be written rather than left null.
    with db.cursor() as c:
        c.execute("SELECT COUNT(*) FROM documents WHERE present=1 AND source IS NULL")
        counts["no_source"] = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM documents WHERE present=1 AND text_source='pdftotext'")
        counts["pdfs_with_text"] = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM documents WHERE present=1 AND text_source='pdftotext' AND revision IS NOT NULL")
        counts["revision_read"] = c.fetchone()[0]
    if counts["no_source"]:
        fails.append("%d document(s) have no recorded source; every one needs a line in "
                     "v2/vendor/sources.txt" % counts["no_source"])
    return fails, counts, []


def check_space(db, sample=60):
    """The model is the contract. Re-embed stored chunks and compare with what is stored."""
    with db.cursor() as c:
        c.execute("SELECT c.id, c.text, VEC_ToText(e.embedding) FROM chunk_embeddings e "
                  "JOIN chunks c ON c.id = e.chunk_id ORDER BY RAND() LIMIT %s", (sample,))
        rows = c.fetchall()
    if not rows:
        return ["no embeddings to verify"], {"sampled": 0}, []
    texts = [r[1][:6000] for r in rows]
    fresh = kbembed.embed_documents(texts)
    cos = []
    for (cid, _t, stored), new in zip(rows, fresh):
        old = json.loads(stored)
        dot = sum(a * b for a, b in zip(old, new))
        na = sum(a * a for a in old) ** 0.5
        nb = sum(b * b for b in new) ** 0.5
        cos.append(dot / (na * nb) if na and nb else 0.0)
    med = statistics.median(cos)
    counts = {"sampled": len(cos), "median_cosine": round(med, 6), "min_cosine": round(min(cos), 6)}
    fails = [] if med >= SPACE_MEDIAN_MIN else [
        "the embedding space has moved: median cosine %.6f against a required %.4f. Every stored "
        "vector was made by a different model or a different prefix, and every distance in this "
        "store is meaningless until they are rebuilt." % (med, SPACE_MEDIAN_MIN)]
    return fails, counts, []


def check_gold(k=6):
    """Ten real questions, the document that answers each. Also checks the gold set itself: a path
    that no longer exists makes a check that can never fail, which is worse than no check."""
    g = json.load(open(GOLD))
    fails, missing, hitn = [], 0, 0
    for q in g["questions"]:
        for a in q["accept"]:
            if not os.path.exists(os.path.join(VENDOR, a)):
                fails.append("the gold set names a document that is not in the tree: %s" % a)
                missing += 1
        hits, _note, _missing = kb_search.search(q["q"], k=k, caller="kb_verify")
        got = [h["relpath"] for h in hits]
        if not any(a in got for a in q["accept"]):
            fails.append("%r did not return %s in the top %d (returned: %s)"
                         % (q["q"], " or ".join(q["accept"]), k, ", ".join(got[:k]) or "nothing"))
        else:
            hitn += 1
    return fails, {"questions": len(g["questions"]), "answered": hitn, "gold_paths_missing": missing}, []


def list_parts(db):
    """Parts on the shipped BOMs with no datasheet in the store. A listing, not a gate: a missing
    vendor document is research owed, not a code defect. It is the inventory of what cannot be
    checked here, which is the one thing a retrieval tool must never leave implicit."""
    parts = {}
    for bom in glob.glob(os.path.join(RELEASE, "*", "boards", "*", "*bom*.csv")):
        try:
            with open(bom, newline="", encoding="utf-8", errors="replace") as fh:
                for row in csv.DictReader(fh):
                    val = (row.get("Comment") or row.get("comment") or "").strip()
                    if re.fullmatch(r"[A-Z0-9][A-Z0-9._/-]{4,24}", val) and any(ch.isdigit() for ch in val):
                        parts.setdefault(val, set()).add(os.path.basename(os.path.dirname(bom)))
        except Exception:
            continue
    out = []
    for val in sorted(parts):
        token = re.split(r"[-_/]", val)[0]
        if len(token) < 5:
            token = val[:8]
        with db.cursor() as c:
            c.execute("SELECT COUNT(*) FROM chunks c JOIN documents d ON d.id=c.document_id "
                      "WHERE d.present=1 AND c.page>0 AND c.text LIKE %s", ("%" + token + "%",))
            if not c.fetchone()[0]:
                out.append("%-24s on %s" % (val, ", ".join(sorted(parts[val]))[:60]))
    return out, len(parts)


def main(argv):
    ap = argparse.ArgumentParser()
    for f in ("coverage", "space", "gold", "parts"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--sample", type=int, default=60)
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    run = {"coverage": a.coverage, "space": a.space, "gold": a.gold}
    if not any(run.values()) and not a.parts:
        run = {"coverage": True, "space": True, "gold": True}
    try:
        db = kbdb.connect()
    except kbenv.InfraFail as e:
        print(e, file=sys.stderr)
        return verdict.write("kb_verify", verdict.INCONCLUSIVE, note=str(e), out_dir=a.out_dir)

    if a.parts:
        rows, total = list_parts(db)
        print("kb_verify: %d of %d BOM part values have no datasheet page in this store" % (len(rows), total))
        for r in rows:
            print("   NO SHEET  %s" % r)
        if not any(run.values()):
            return 0

    fails, counts, notes = [], {}, []
    try:
        for name, fn in (("coverage", lambda: check_coverage(db)),
                         ("space", lambda: check_space(db, a.sample)),
                         ("gold", lambda: check_gold(a.k))):
            if not run[name]:
                continue
            f, c, n = fn()
            fails += ["[%s] %s" % (name, x) for x in f]
            counts.update({("%s_%s" % (name, k)): v for k, v in c.items()})
            notes += n
    except kbenv.InfraFail as e:
        print(e, file=sys.stderr)
        return verdict.write("kb_verify", verdict.INCONCLUSIVE, counts=counts, note=str(e), out_dir=a.out_dir)

    for n in notes:
        print("kb_verify: note: %s" % n)
    for f in fails:
        print("kb_verify: FAIL %s" % f)
    denom = counts.get("coverage_files_on_disk") or counts.get("gold_questions")
    return verdict.write("kb_verify", verdict.FAIL if fails else verdict.PASS, counts=counts,
                         denominator=denom, evidence=fails[:30], out_dir=a.out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
