#!/usr/bin/env python3
"""kb_ingest.py, the datasheet knowledge base's scanner (MESHSAT-862, 10 September 2026).

Walks v2/vendor/, attaches text PAGE BY PAGE, chunks within the page and embeds. Every stage is
resumable and every stage is logged, because the embedding host is shared and is stopped during
board runs on the VM: an interrupted ingest is a normal state, not an incident.

  scan   upsert one row per file in v2/vendor/ (sha256 change detection; a file that vanished gets
         present=0 and keeps its row, so an absence can never read as "there was never anything")
  text   pdftotext -layout per document, split on the form feeds it writes between pages, so every
         chunk knows the page you re-open to check the claim. Text files are read directly.
         A file with no text is recorded WITH ITS REASON and counted out loud, never dropped: the
         sibling archive lost 107 files holding 5.6 MB that way, present in the manifest, chunked
         nowhere, invisible to search and silent about it.
  embed  chunks lacking an embedding, in batches, tolerating an unreachable host.

A PDF with no text layer (a scanned mechanical drawing) must be declared in v2/vendor/vendor-noindex.txt
with a reason, in the erc-allow.txt idiom of this repository. An undeclared one is BLIND and
`kb_verify.py` fails on it.

Usage: kb_ingest.py [--stage scan|text|embed|all] [--limit N] [--reset-text PATH]
"""
import sys, os, re, argparse, datetime, hashlib, subprocess, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kbdb, kbembed, kbenv          # noqa: E402
import verdict                        # noqa: E402  the one verdict writer

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "vendor"))
NOINDEX = os.path.join(VENDOR, "vendor-noindex.txt")
STATUS = os.path.join(VENDOR, "vendor-status.txt")

TEXT_EXT = {".md", ".adoc", ".txt", ".csv", ".tsv", ".yaml", ".yml", ".json", ".xml", ".html", ".htm"}
SKIP_DIRS = {".git", "__pycache__", ".claude"}
CHUNK_CHARS = 1200
CHUNK_OVERLAP = 200
MIN_PAGE_CHARS = 40      # below this a page is a picture: recorded as an empty page, not as text
RUN_ID = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6]
SOURCES = os.path.join(VENDOR, "sources.txt")

# What a document says about its own revision, in the forms the manufacturers on this estate use.
# Ordered: the most specific first, so TI's literature number beats a bare "Rev".
REV_PATTERNS = [
    r"S[A-Z]{3}\d{3}[A-Z]\b",                    # TI literature number, the letter IS the revision
    r"\bDS\d{4,6}\b[^\n]{0,40}?Rev(?:ision)?\.?\s*[0-9A-Z]{1,3}\b",   # ST, Diodes
    r"\bREVISED\s+[A-Z]+\s+\d{4}",
    r"\bVersion:?\s*[0-9][0-9.]*",
    r"\bRev(?:ision)?\.?\s*[:]?\s*[0-9A-Z]{1,3}\b",
    r"\bDocument\s+\d{3,4}-\d\b",
]


def revision_of(pages):
    """The revision a document declares about itself, from its first two pages, or None."""
    head = "\n".join(pages[:2])
    for pat in REV_PATTERNS:
        m = re.search(pat, head, re.I)
        if m:
            return " ".join(m.group(0).split())[:64]
    return None


def log(db, stage, doc_id, ok, detail=""):
    with db.cursor() as c:
        c.execute("INSERT INTO ingest_log (run_id, started_at, stage, document_id, ok, detail) "
                  "VALUES (%s, NOW(), %s, %s, %s, %s)", (RUN_ID, stage, doc_id, 1 if ok else 0, detail[:1000]))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def declared_sources():
    """relpath or folder -> where the file came from, from v2/vendor/sources.txt."""
    out = {}
    if not os.path.exists(SOURCES):
        return out
    for line in open(SOURCES):
        line = line.strip()
        if not line or line.startswith("#") or "#" not in line:
            continue
        path, src = line.split("#", 1)
        if path.strip() and src.strip():
            out[path.strip()] = src.strip()[:500]
    return out


def noindex_reasons():
    """path -> reason, from v2/vendor/vendor-noindex.txt. A line with no reason is ignored, exactly
    as erc_gate.py treats erc-allow.txt: a declaration without a reason declares nothing."""
    out = {}
    if not os.path.exists(NOINDEX):
        return out
    with open(NOINDEX) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "#" not in line:
                continue
            path, reason = line.split("#", 1)
            if path.strip() and reason.strip():
                out[path.strip()] = reason.strip()[:250]
    return out


def declared_status():
    """path or folder -> (status, reason), from v2/vendor/vendor-status.txt. A file line overrides
    its folder line. A line without a reason declares nothing, the erc-allow.txt idiom again."""
    out = {}
    if not os.path.exists(STATUS):
        return out
    with open(STATUS) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "#" not in line:
                continue
            head, reason = line.split("#", 1)
            parts = head.split()
            if len(parts) != 2 or not reason.strip():
                continue
            path, st = parts
            if st in ("current", "v1", "retired", "tooling"):
                out[path.strip("/")] = (st, reason.strip()[:250])
    return out


def status_for(rel, declared):
    """A document's status: its own line if it has one, else its folder's, else undeclared. An
    undeclared document is not quietly current; kb_verify.py fails on it."""
    if rel in declared:
        return declared[rel]
    folder = rel.split(os.sep, 1)[0] if os.sep in rel else rel
    if folder in declared:
        return declared[folder]
    return ("undeclared", None)


def stage_scan(db):
    if not os.path.isdir(VENDOR):
        raise kbenv.InfraFail("INFRA_FAIL: %s is not a directory" % VENDOR)
    declared = declared_status()
    seen, new, changed, undeclared = set(), 0, 0, []
    for dirpath, dirs, files in os.walk(VENDOR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, VENDOR)
            seen.add(rel)
            st = os.stat(path)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            sha = sha256_file(path)
            vendor = rel.split(os.sep, 1)[0] if os.sep in rel else "root"
            st_v, st_r = status_for(rel, declared)
            if st_v == "undeclared":
                undeclared.append(rel)
            with db.cursor() as c:
                c.execute("SELECT id, sha256 FROM documents WHERE relpath=%s", (rel,))
                row = c.fetchone()
                if row:
                    if row[1] == sha:
                        # the bytes are unchanged, but a status declaration may have moved
                        c.execute("UPDATE documents SET present=1, status=%s, status_reason=%s WHERE id=%s",
                                  (st_v, st_r, row[0]))
                        continue
                    # the bytes changed: the old chunks describe a document that no longer exists
                    c.execute("UPDATE documents SET sha256=%s, size_bytes=%s, mtime=%s, present=1, "
                              "text_source='none', no_text_reason=NULL, pages=NULL, ingested_at=NULL, "
                              "status=%s, status_reason=%s WHERE id=%s",
                              (sha, st.st_size, mtime, st_v, st_r, row[0]))
                    c.execute("DELETE FROM chunks WHERE document_id=%s", (row[0],))
                    changed += 1
                else:
                    c.execute("INSERT INTO documents (relpath, sha256, size_bytes, mtime, vendor, status, status_reason) "
                              "VALUES (%s,%s,%s,%s,%s,%s,%s)", (rel, sha, st.st_size, mtime, vendor, st_v, st_r))
                    new += 1
    with db.cursor() as c:
        c.execute("SELECT id, relpath FROM documents WHERE present=1")
        gone = [(i,) for i, r in c.fetchall() if r not in seen]
        if gone:
            c.executemany("UPDATE documents SET present=0 WHERE id=%s", gone)
    print("scan: new=%d changed=%d vanished=%d of %d files" % (new, changed, len(gone), len(seen)))
    if undeclared:
        print("scan: %d file(s) have no status in %s, so nothing knows whether they describe this "
              "design or a retired one:" % (len(undeclared), os.path.relpath(STATUS)))
        for r in undeclared[:20]:
            print("   UNDECLARED  %s" % r)
    log(db, "scan", None, not undeclared, "new=%d changed=%d vanished=%d undeclared=%d"
        % (new, changed, len(gone), len(undeclared)))
    return {"new": new, "changed": changed, "vanished": len(gone), "files": len(seen),
            "undeclared": undeclared}


def chunk_page(text):
    """Char windows with overlap, preferring a blank line then a line break. A datasheet page is
    mostly a table, so the window is small enough that one hit is one readable excerpt."""
    out, pos = [], 0
    while pos < len(text):
        end = min(pos + CHUNK_CHARS, len(text))
        if end < len(text):
            brk = text.rfind("\n\n", pos + CHUNK_CHARS // 2, end)
            if brk == -1:
                brk = text.rfind("\n", pos + CHUNK_CHARS // 2, end)
            if brk != -1:
                end = brk
        piece = text[pos:end].strip()
        if piece:
            out.append(piece)
        if end >= len(text):
            break
        pos = max(end - CHUNK_OVERLAP, pos + 1)
    return out


def pdf_pages(path):
    """Pages of a PDF, in order. pdftotext writes a form feed between pages, so one process gives
    every page with its number, which is the citation the reader needs."""
    out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError("pdftotext exit %d: %s" % (out.returncode, out.stderr.strip()[:200]))
    pages = out.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def stage_text(db, limit=None):
    reasons = noindex_reasons()
    srcs = declared_sources()
    with db.cursor() as c:
        c.execute("SELECT id, relpath FROM documents WHERE present=1 AND text_source='none' ORDER BY id"
                  + (" LIMIT %d" % int(limit) if limit else ""))
        todo = c.fetchall()
    done = blind = 0
    undeclared = []
    for doc_id, rel in todo:
        path = os.path.join(VENDOR, rel)
        ext = os.path.splitext(rel)[1].lower()
        pages, src, reason = [], "none", None
        try:
            if ext == ".pdf":
                pages = pdf_pages(path)
                if sum(len(p.strip()) for p in pages) < MIN_PAGE_CHARS * max(1, len(pages)) // 4:
                    reason = reasons.get(rel) or "PDF with no text layer"
                    if rel not in reasons:
                        undeclared.append(rel)
                    pages = []
                else:
                    src = "pdftotext"
            elif ext in TEXT_EXT:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    pages = [fh.read()]
                src = "direct"
            else:
                reason = "not a text document (%s)" % (ext or "no extension")
        except Exception as e:
            log(db, "text", doc_id, False, "%s: %s" % (type(e).__name__, e))
            reason = "text extraction failed: %s" % type(e).__name__
        rows = []
        for pno, ptext in enumerate(pages, start=1 if ext == ".pdf" else 0):
            if len(ptext.strip()) < MIN_PAGE_CHARS:
                continue                     # a drawing page inside a text PDF: no chunk, no pretence
            for i, piece in enumerate(chunk_page(ptext)):
                rows.append((doc_id, pno, i, piece, len(piece) // 4))
        rev = revision_of(pages) if pages else None
        folder = rel.split(os.sep, 1)[0] if os.sep in rel else rel
        source = srcs.get(rel) or srcs.get(folder)
        with db.cursor() as c:
            if rows:
                c.executemany("INSERT IGNORE INTO chunks (document_id, page, seq, text, token_est) "
                              "VALUES (%s,%s,%s,%s,%s)", rows)
            c.execute("UPDATE documents SET text_source=%s, no_text_reason=%s, pages=%s, revision=%s, "
                      "source=%s, ingested_at=NOW() WHERE id=%s",
                      (src, reason, len(pages) or None, rev, source, doc_id))
        if src == "none":
            blind += 1
        else:
            done += 1
    print("text: %d documents chunked, %d carry no text" % (done, blind))
    if undeclared:
        print("text: %d PDF(s) have NO TEXT LAYER and are not declared in %s:" % (len(undeclared), os.path.relpath(NOINDEX)))
        for r in undeclared[:20]:
            print("   BLIND  %s" % r)
    log(db, "text", None, not undeclared, "chunked=%d blind=%d undeclared=%d" % (done, blind, len(undeclared)))
    return {"chunked": done, "no_text": blind, "undeclared": undeclared}


def stage_embed(db, limit=None, batch=32):
    with db.cursor() as c:
        c.execute("SELECT c.id, c.text FROM chunks c LEFT JOIN chunk_embeddings e ON e.chunk_id=c.id "
                  "WHERE e.chunk_id IS NULL ORDER BY c.id" + (" LIMIT %d" % int(limit) if limit else ""))
        todo = c.fetchall()
    done = 0
    for i in range(0, len(todo), batch):
        ids = [r[0] for r in todo[i:i + batch]]
        texts = [r[1][:6000] for r in todo[i:i + batch]]
        try:
            embs = kbembed.embed_documents(texts)
        except kbenv.InfraFail as e:
            log(db, "embed", None, False, str(e))
            print("embed: %s; stopping at %d of %d, resume later" % (e, done, len(todo)), file=sys.stderr)
            break
        params = [(cid, kbembed.vec_literal(v)) for cid, v in zip(ids, embs)]
        with db.cursor() as c:
            c.executemany("INSERT IGNORE INTO chunk_embeddings (chunk_id, embedding) VALUES (%s, VEC_FromText(%s))", params)
        done += len(ids)
        if done % 640 == 0:
            print("embed: %d/%d" % (done, len(todo)), flush=True)
    print("embed: %d of %d" % (done, len(todo)))
    log(db, "embed", None, done == len(todo), "embedded=%d of %d" % (done, len(todo)))
    return {"embedded": done, "pending": len(todo) - done}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["scan", "text", "embed", "all"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    try:
        db = kbdb.connect()
    except kbenv.InfraFail as e:
        return verdict.write("kb_ingest", verdict.INCONCLUSIVE, note=str(e), out_dir=a.out_dir)
    counts = {}
    for s in (["scan", "text", "embed"] if a.stage == "all" else [a.stage]):
        counts.update({("%s_%s" % (s, k)): v for k, v in
                       {"scan": lambda: stage_scan(db),
                        "text": lambda: stage_text(db, a.limit),
                        "embed": lambda: stage_embed(db, a.limit)}[s]().items()})
    blind = list(counts.pop("text_undeclared", []))          # a PDF with no text layer and no reason
    unstatused = list(counts.pop("scan_undeclared", []))     # a file with no current/retired status
    undeclared = blind + unstatused
    with db.cursor() as c:
        c.execute("SELECT (SELECT COUNT(*) FROM documents WHERE present=1), (SELECT COUNT(*) FROM chunks), "
                  "(SELECT COUNT(*) FROM chunk_embeddings)")
        docs, chunks, embs = c.fetchone()
    counts.update({"documents": docs, "chunks": chunks, "embedded": embs,
                   "undeclared_blind": len(blind), "undeclared_status": len(unstatused)})
    res = verdict.FAIL if undeclared else (verdict.PASS if embs == chunks else verdict.INCONCLUSIVE)
    note = "; ".join(x for x in [
        ("%d PDF(s) with no text layer and no declared reason" % len(blind)) if blind else "",
        ("%d file(s) with no declared status" % len(unstatused)) if unstatused else "",
        ("" if embs == chunks else "%d chunks are not embedded yet (resumable)" % (chunks - embs))] if x)
    return verdict.write("kb_ingest", res, counts=counts, denominator=docs,
                         evidence=undeclared[:20], note=note, out_dir=a.out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
