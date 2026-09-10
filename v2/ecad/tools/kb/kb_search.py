#!/usr/bin/env python3
"""kb_search.py, retrieval over the vendor documents (MESHSAT-862, 10 September 2026).

WHAT THIS IS. A way to find WHICH PAGE of which vendor document to read. Two signals over the
store, merged by reciprocal rank fusion and optionally reranked: MariaDB's native vector distance
over nomic-embed-text embeddings, and InnoDB full text over the same chunks, because a part number
is a token that a dense embedding blurs and an exact match finds.

WHAT THIS IS NOT, and the three things that keep it that way:

  1. It never decides. A retrieved passage is model-selected evidence, so it is capped at 0.75
     confidence, below the action cutoff the sibling projects on this estate enforce, and the cap
     is a CHECK constraint on the store's own `lookups` table rather than a habit. Every hit is
     printed with the command that re-reads its page, because the answer is the page, not this.
  2. It never runs on a verdict path. No gate, no check_pcb_*, no finish script may import it, and
     tests/test_kb_isolation.py fails if one does. The topology says the same thing: the boards are
     built and judged on a rented box that has no route to this store at all.
  3. It never presents a retired part as current. Every hit carries the status of its vendor folder
     from v2/vendor/vendor-status.txt, a retired or V1-only document is pushed down the ranking and
     labelled in capitals, and an undeclared one says so.

Usage:
  kb_search.py "TPS2065 DBV package pin count" [--k 6] [--json] [--all] [--vendor ti] [--no-rerank]

  --all includes retired and V1 documents in the ranking (they are labelled either way; without
  this flag they are still shown when nothing current matches, so an empty result is never faked).
"""
import sys, os, re, json, argparse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kbdb, kbembed, kbenv          # noqa: E402

RRF_K = 60
TRUTH_CAP = 0.75                     # agora invariant 5 / logos invariant 5: a model-derived signal
                                     # sits below the action threshold, structurally unable to decide
STATUS_WEIGHT = {"current": 1.0, "tooling": 0.6, "v1": 0.45, "retired": 0.30, "undeclared": 0.5}
STATUS_LABEL = {"current": "", "tooling": "  [TOOLING]", "v1": "  [V1 KITS ONLY]",
                "retired": "  [RETIRED]", "undeclared": "  [STATUS UNDECLARED]"}
# A vendor folder's README is our own curation, not the manufacturer's word, and it names every part
# in the folder, so it matches almost any question about any of them. It stays searchable and stays
# labelled, and it does not outrank the sheet it describes.
NOTE_EXT = (".md", ".adoc", ".html", ".htm", ".txt", ".yaml", ".yml", ".json", ".xml", ".csv", ".tsv")
# `.geom.txt` is a measurement taken from a vendor CAD model by geom_probe.py, not our commentary, so
# it keeps full weight. Without this it lost to the READMEs by the note factor and a question about a
# module's hole pattern came back with a different module's.
MEASURED_SUFFIX = ".geom.txt"
# An OCR sidecar is a searchable index of a drawing that has no text layer. It is never a source of
# numbers: OCR misreads exactly the characters that matter on a drawing, a decimal point, a tolerance,
# an H7, a 6 against an 8. It is labelled in every hit and it points at the original page.
OCR_SUFFIX = ".ocr.txt"
OCR_WEIGHT = 0.8
NOTE_WEIGHT = 0.55
PER_DOC_CAP = 2      # six passages of one datasheet are one piece of evidence, not six.
                     # Two, not three: with the exact-token pool added, one document could
                     # still take half of a k=6 answer, and it did, crowding the RockBLOCK
                     # datasheet out with three chunks of its own geometry sidecar.


def _rows(db, sql, params):
    with db.cursor() as c:
        c.execute(sql, params)
        return c.fetchall()


SELECT = ("SELECT c.id, d.relpath, c.page, d.status, d.status_reason, c.text ")
JOIN = "FROM chunks c JOIN documents d ON d.id = c.document_id "


def vector_hits(db, query, k, vendor=None):
    qv = kbembed.vec_literal(kbembed.embed_query(query))
    sql = (SELECT + ", VEC_DISTANCE_COSINE(e.embedding, VEC_FromText(%s)) AS dist "
           "FROM chunk_embeddings e JOIN chunks c ON c.id = e.chunk_id "
           "JOIN documents d ON d.id = c.document_id WHERE d.present=1 "
           + ("AND d.vendor=%s " if vendor else "") + "ORDER BY dist LIMIT %s")
    params = (qv, vendor, k * 10) if vendor else (qv, k * 10)
    return _rows(db, sql, params)


def fulltext_hits(db, query, k, vendor=None):
    sql = (SELECT + ", MATCH(c.text) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score " + JOIN +
           "WHERE d.present=1 AND MATCH(c.text) AGAINST (%s IN NATURAL LANGUAGE MODE) "
           + ("AND d.vendor=%s " if vendor else "") + "ORDER BY score DESC LIMIT %s")
    params = (query, query, vendor, k * 10) if vendor else (query, query, k * 10)
    return _rows(db, sql, params)


def token_hits(db, query, k, vendor=None):
    """A third signal: documents that contain the query's part-number tokens verbatim.

    A part number is the highest-precision term a question can carry and it is exactly what a dense
    embedding blurs: "what package and pin count does H5007NL have" embeds mostly as "package and pin
    count", and the pool fills with datasheets that discuss packages. Measured over the whole
    inventory, that cost about a tenth of all recall, so the exact token gets its own pool and the
    fusion weighs it beside the other two rather than trusting either alone."""
    toks = [t for t in PART_TOKEN.findall(query) if len(t) >= 5]
    if not toks:
        return []
    rows = []
    for t in toks:
        # the manufacturer's own document first, then our probes and sidecars: a token match in a
        # geometry sidecar is real but it is not the datasheet the question wanted
        sql = (SELECT + " , 0 AS score " + JOIN +
               "WHERE d.present=1 AND (c.text LIKE %s OR LOWER(d.relpath) LIKE %s) "
               + ("AND d.vendor=%s " if vendor else "") +
               "ORDER BY (d.status='current') DESC, (LOWER(d.relpath) LIKE %s) DESC, c.page LIMIT %s")
        params = ("%" + t + "%", "%" + t.lower() + "%") + ((vendor,) if vendor else ()) + ("%.pdf", k * 4)
        rows += _rows(db, sql, params)
    return rows


def rerank(query, cands, timeout=20):
    """Optional. When the rerank service is down the fused order stands and says so; a reranker that
    quietly disappears must not look like a reranker that agreed."""
    try:
        url = kbenv.get("MESHSAT_KB_RERANK_URL", "").rstrip("/")
        if not url:
            return cands, "not configured"
        payload = json.dumps({"query": query, "documents": [c["text"][:2000] for c in cands],
                              "top_k": len(cands)}).encode()
        req = urllib.request.Request(url + "/rerank", data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        for item in data.get("ranked", []):
            if 0 <= item["index"] < len(cands):
                cands[item["index"]]["rerank"] = float(item["score"])
        if any("rerank" in c for c in cands):
            cands.sort(key=lambda c: (c.get("rerank", -1e9), c["rrf"]), reverse=True)
            return cands, "applied"
        return cands, "no scores returned"
    except Exception as e:
        return cands, "unavailable (%s)" % e


def search(query, k=6, vendor=None, include_retired=False, use_rerank=True, caller=None):
    db = kbdb.connect()
    scores, meta = {}, {}
    for pool in (vector_hits(db, query, k, vendor), fulltext_hits(db, query, k, vendor),
                 token_hits(db, query, k, vendor)):
        # The cap is applied while the pools are FUSED, not only to the final list. A large model's
        # probe file carries dozens of near identical hole lines and filled both pools by itself, so a
        # question about one module answered with another module's holes even though the right file
        # was indexed. Ranking is untouched; what changes is how many rows one document may occupy.
        seen_doc = {}
        for rank, row in enumerate(pool):
            cid, relpath, page, status, reason, text = row[:6]   # the pools carry a score column too
            # `tooling` is ALWAYS excluded, even with --all: those are this store's own bookkeeping
            # files (PARTS.md, family-matches.txt, the status and source lists) and they name every
            # part number in the design, so the exact-token pool ranked them above the datasheets they
            # are indexes of. They are never an answer about a part.
            if status == "tooling":
                continue
            if not include_retired and status in ("retired", "v1"):
                continue
            n_doc = seen_doc.get(relpath, 0)
            if n_doc >= PER_DOC_CAP:
                continue
            seen_doc[relpath] = n_doc + 1
            # The status penalty exists to keep a retired part out of a default answer. Once --all is
            # given the caller has asked for those documents by name, so the penalty is dropped and
            # only the label remains: otherwise asking about the WeAct module, which IS retired,
            # returned three other modules' hole patterns and never its own.
            w = 1.0 if include_retired else STATUS_WEIGHT.get(status, 0.5)
            if relpath.endswith(OCR_SUFFIX):
                w *= OCR_WEIGHT
            elif os.path.splitext(relpath)[1].lower() in NOTE_EXT and not relpath.endswith(MEASURED_SUFFIX):
                w *= NOTE_WEIGHT
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (RRF_K + rank + 1)) * w
            meta[cid] = {"chunk_id": cid, "relpath": relpath, "page": page, "status": status,
                         "status_reason": reason, "text": text}
    fallback = ""
    if not scores and not include_retired:
        # Nothing current matched. Saying "no hits" here would be a lie of omission: the store holds
        # the retired documents and the honest answer names them, labelled.
        fallback = "no current document matched; the hits below are retired or V1-only"
        deep = search(query, k, vendor, True, use_rerank, caller)
        return deep[0], fallback, deep[2]
    ranked = sorted(scores, key=scores.get, reverse=True)[: k * 2]
    cands = [dict(meta[cid], rrf=round(scores[cid], 6)) for cid in ranked]
    cands, rr = rerank(query, cands, ) if (use_rerank and cands) else (cands, "skipped")
    hits, per_doc = [], {}
    for h in cands:                       # keep the ranking, spread the evidence over documents
        n = per_doc.get(h["relpath"], 0)
        if n >= PER_DOC_CAP:
            continue
        per_doc[h["relpath"]] = n + 1
        hits.append(h)
        if len(hits) >= k:
            break
    missing = absent_tokens(db, query, hits)
    try:
        with db.cursor() as c:
            c.execute("INSERT INTO lookups (asked_at, query, hits, top_chunk_id, confidence, advisory, caller) "
                      "VALUES (NOW(), %s, %s, %s, %s, 1, %s)",
                      (query[:1000], len(hits), hits[0]["chunk_id"] if hits else None, TRUTH_CAP, caller))
    except Exception:
        pass                       # the record of a lookup must never be able to break the lookup
    return hits, (fallback or ("rerank " + rr)), missing


PART_TOKEN = re.compile(r"\b(?=[A-Za-z]*[0-9])(?=[0-9]*[A-Za-z])[A-Za-z][A-Za-z0-9]{4,}\b")


def absent_tokens(db, query, hits):
    """The most dangerous answer this tool can give is a confident page about a DIFFERENT part.

    Ask it for the TMUXHS4212 when no TMUXHS4212 datasheet was ever fetched and it returns the
    LT8705A's exposed-pad note and a TI mux's pin table: both real pages, both about something else,
    and nothing in the output says so. So every part-number-shaped token in the question is checked
    twice: against the returned passages, and against the whole store. `not_in_hits` means the pages
    above are not about it; `not_in_store` means no vendor document here mentions it at all, which
    is a fact about our documents and is worth saying in those words."""
    toks = {t for t in PART_TOKEN.findall(query) if len(t) >= 5}
    if not toks:
        return [], []
    body = " ".join(h["text"] for h in hits).upper()
    not_in_hits = sorted(t for t in toks if t.upper() not in body)
    not_in_store = []
    for t in not_in_hits:
        with db.cursor() as c:
            c.execute("SELECT COUNT(*) FROM chunks c JOIN documents d ON d.id=c.document_id "
                      "WHERE d.present=1 AND c.text LIKE %s", ("%" + t + "%",))
            if not c.fetchone()[0]:
                not_in_store.append(t)
    return not_in_hits, not_in_store


def cite(hit):
    """The command that re-reads the page. The page is the answer; this tool only points at it."""
    if hit["page"]:
        return "pdftotext -layout -f %d -l %d v2/vendor/%s -" % (hit["page"], hit["page"], hit["relpath"])
    return "sed -n '1,120p' v2/vendor/%s" % hit["relpath"]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--vendor")
    ap.add_argument("--all", action="store_true", help="include retired and V1-only documents")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-rerank", action="store_true")
    ap.add_argument("--caller", default=None)
    a = ap.parse_args(argv)
    try:
        hits, note, (not_in_hits, not_in_store) = search(a.query, a.k, a.vendor, a.all,
                                                         not a.no_rerank, a.caller)
    except kbenv.InfraFail as e:
        print(e, file=sys.stderr)
        return 3                    # INFRA_FAIL, never an empty result
    if a.json:
        print(json.dumps({"query": a.query, "note": note, "advisory": True, "confidence_cap": TRUTH_CAP,
                          "tokens_not_in_hits": not_in_hits, "tokens_not_in_store": not_in_store,
                          "hits": [{k: v for k, v in h.items() if k != "text"} |
                                   {"snippet": h["text"][:400], "reread": cite(h)} for h in hits]},
                         indent=1, ensure_ascii=False))
        return 0
    print("kb: %d hit(s) for %r  (%s; advisory only, confidence capped at %.2f)"
          % (len(hits), a.query, note, TRUTH_CAP))
    for i, h in enumerate(hits, 1):
        page = ("p.%d" % h["page"]) if h["page"] else "(no pages)"
        note = ("  [PROBED FROM THE CAD MODEL]" if h["relpath"].endswith(MEASURED_SUFFIX)
                else "  [OCR OF A DRAWING, NOT A SOURCE OF NUMBERS]" if h["relpath"].endswith(OCR_SUFFIX)
                else ("  [REPO NOTE]" if os.path.splitext(h["relpath"])[1].lower() in NOTE_EXT else ""))
        print("\n[%d] v2/vendor/%s  %s%s%s" % (i, h["relpath"], page, STATUS_LABEL.get(h["status"], ""), note))
        if h["status"] != "current" and h["status_reason"]:
            print("    why it is %s: %s" % (h["status"], h["status_reason"]))
        print("    read it:  %s" % cite(h))
        body = " ".join(h["text"].split())
        print("    %s" % body[:360])
    if not hits:
        print("\n    Nothing matched. That is a statement about this store, not about the part.")
    for t in not_in_store:
        print("\n    !! NO DOCUMENT IN THIS STORE MENTIONS %s. Nothing above is about it. Whatever "
              "you need to know about that part is not here: fetch the sheet into v2/vendor/ and "
              "re-run kb_ingest.py." % t)
    for t in not_in_hits:
        if t not in not_in_store:
            print("\n    !! none of the pages above contains %s, though the store holds documents "
                  "that mention it: narrow the question or pass --vendor." % t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
