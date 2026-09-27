#!/usr/bin/env python3
"""kb_recall.py, retrieval measured over the whole inventory (MESHSAT-862, 11 September 2026).

The gold set is twelve questions and it passes twelve of twelve, which says nothing about the other
two hundred items. Twelve questions written by the person who indexed the documents is a smoke test:
it proves the pipeline runs, not that it finds things.

This asks a question about EVERY part in the inventory that has a document, in the form a session
actually asks it, and requires that part's own document back. The generated set cannot flatter the
store, because it is generated from what the design uses rather than from what I know is indexed.

  recall@k   the share of parts whose own document is in the top k
  adversarial  three questions the store must get RIGHT BY REFUSING: a part that is not in the design
               at all must say so; a retired part must come back labelled; a near-miss order code must
               not be answered with its neighbour's sheet

Usage: kb_recall.py [--k 6] [--limit N] [--floor 0.9] [--out-dir out]
"""
import sys, os, json, random, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import kbdb, kbenv, kb_search, kb_inventory, kb_parts as K       # noqa: E402
import verdict                                     # noqa: E402

# The two questions a session actually asks about a part it is placing, which is the point: a store
# that only answers when you already quote the datasheet's own words is not answering.
# Two forms that suit ANY part. The first version asked "%s supply voltage and current", which is a
# meaningless question about an RF connector or a TVS diode, and the misses it produced were the
# question's fault rather than the store's. A recall figure has to measure retrieval, not my choice of
# phrasing, so the bare order code is the honest test and the package question is the common one.
FORMS = ["%s", "what package and pin count does %s have"]

ADVERSARIAL = [
    ("LM317T voltage regulator package",
     "not_in_design", "a part this design does not use; the store must say no document mentions it"),
    ("Touch Display 2 mounting hole spacing",
     "retired_labelled", "a retired part asked for by name: with retired documents included, its own "
                         "must come back and they must be labelled retired"),
    ("TPS2560DRC package and pin count",
     "near_miss", "a real TI part from a neighbouring family that this design does not use; it must "
                  "not be answered as though its order code were ours"),
]


def covering_docs(db, part):
    """Every document that names this part or its declared family, which is what "covered" means."""
    out = set()
    for v in K.variants(part):
        with db.cursor() as c:
            c.execute("SELECT DISTINCT d.relpath FROM chunks c JOIN documents d ON d.id=c.document_id "
                      "WHERE d.present=1 AND c.text LIKE %s", ("%" + v + "%",))
            out |= {r[0] for r in c.fetchall()}
            c.execute("SELECT relpath FROM documents WHERE present=1 AND LOWER(relpath) LIKE %s",
                      ("%" + v.lower() + "%",))
            out |= {r[0] for r in c.fetchall()}
        # no break: a part is covered by its exact code AND by its family, and stopping at the first
        # variant that hit anything said LG290P03AAMD was covered by one document when four cover it
    # our own declaration files mention part numbers; they are not documents about the part
    return {r for r in out if not r.endswith(("family-matches.txt", "open-picks.txt", "not-used.txt",
                                              "PARTS.md", "sources.txt", "vendor-status.txt"))}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--floor", type=float, default=0.90)
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    try:
        db = kbdb.connect()
    except kbenv.InfraFail as e:
        print(e, file=sys.stderr)
        return verdict.write("kb_recall", verdict.INCONCLUSIVE, note=str(e), out_dir=a.out_dir)

    items, _dropped = kb_inventory.build(db)
    targets = sorted((t, r) for t, r in items.items()
                     if r["state"] in ("DOCUMENTED", "FAMILY") and r.get("doc"))
    if a.limit:
        random.seed(0)                      # a sample, but the SAME sample every run, so a change in
        targets = random.sample(targets, min(a.limit, len(targets)))   # the number means a real change
    asked = hit = 0
    misses = []
    for part, rec in targets:
        # ANY document that covers the part counts, not the one lookup() happened to pick first.
        # LG290P03AAMD is covered by a protocol specification, a module specification and two hardware
        # design guides; requiring the first of those measured the lookup's arbitrary choice and called
        # a better answer a miss.
        want_set = covering_docs(db, part) or {rec["doc"]}
        want = rec["doc"]
        for form in FORMS:
            q = form % part
            try:
                hits, _n, _m = kb_search.search(q, k=a.k, include_retired=True, caller="kb_recall")
            except kbenv.InfraFail as e:
                return verdict.write("kb_recall", verdict.INCONCLUSIVE, note=str(e), out_dir=a.out_dir)
            asked += 1
            if any(h["relpath"] in want_set for h in hits):
                hit += 1
            else:
                misses.append("%s: %r returned none of its %d covering document(s) (got %s)"
                              % (part, q, len(want_set), ", ".join(h["relpath"] for h in hits[:3]) or "nothing"))
    recall = (hit / asked) if asked else 0.0

    adv_fail = []
    for q, kind, why in ADVERSARIAL:
        hits, note, (not_in_hits, not_in_store) = kb_search.search(q, k=a.k, caller="kb_recall")
        if kind == "not_in_design" and not not_in_store:
            adv_fail.append("%r answered without saying the part is not in the store (%s)" % (q, why))
        if kind == "retired_labelled":
            deep, _n2, _m2 = kb_search.search(q, k=a.k, include_retired=True, caller="kb_recall")
            if not any(h["status"] != "current" for h in deep):
                adv_fail.append("%r returned no retired document even with them included (%s)" % (q, why))
        if kind == "near_miss" and not (not_in_hits or not_in_store):
            adv_fail.append("%r was answered as though the order code were ours (%s)" % (q, why))

    for m in misses[:20]:
        print("MISS  %s" % m)
    for f in adv_fail:
        print("ADVERSARIAL FAIL  %s" % f)
    print("kb_recall: recall@%d = %.3f over %d questions on %d parts (floor %.2f)"
          % (a.k, recall, asked, len(targets), a.floor))
    counts = {"parts": len(targets), "questions": asked, "found": hit,
              "recall_at_%d" % a.k: round(recall, 4), "floor": a.floor,
              "adversarial_failures": len(adv_fail)}
    ok = recall >= a.floor and not adv_fail
    return verdict.write("kb_recall", verdict.PASS if ok else verdict.FAIL, counts=counts,
                         denominator=asked, evidence=(misses[:20] + adv_fail), out_dir=a.out_dir,
                         note="" if ok else "recall %.3f against a floor of %.2f" % (recall, a.floor))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
