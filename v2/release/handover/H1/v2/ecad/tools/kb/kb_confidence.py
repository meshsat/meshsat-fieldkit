#!/usr/bin/env python3
"""kb_confidence.py, the answer to "are you confident", regenerated rather than written.

On 10 September this store reported zero parts without a document and I said I was confident. Asked to
check rather than assert, the number was wrong within a minute. The lesson is not that the number was
bad; it is that a number produced by one heuristic and vouched for in prose is worth nothing.

So the confidence statement is a command. It reads the verdict JSONs the gates wrote, and every figure
in it is one of theirs. Nothing here computes anything: if a gate did not run, its line says so, and a
gate that did not run is never reported as a pass.

Usage: kb_confidence.py [--out-dir out]
"""
import sys, os, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import verdict      # noqa: E402

GATES = [("kb_inventory", "the inventory"), ("kb_verify", "the store"),
         ("kb_recall", "retrieval"), ("kb_recheck", "currency"), ("kb_ingest", "the index")]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    recs, worst = {}, 0
    print("The vendor knowledge base, as its own gates last reported it")
    print("=" * 78)
    for tool, label in GATES:
        path = os.path.join(a.out_dir, "%s.verdict.json" % tool)
        rec, code = verdict.read(path)
        recs[tool] = rec
        worst = max(worst, code)
        c = rec.get("counts") or {}
        print("%-14s %-12s %s" % (label, rec.get("verdict", "?"), rec.get("ts", "")))
        if rec.get("verdict") == verdict.INCONCLUSIVE:
            print("               %s" % (rec.get("note") or "this gate has not run here"))
        for k in sorted(c):
            print("               %-24s %s" % (k, c[k]))
    inv = (recs.get("kb_inventory") or {}).get("counts") or {}
    rc = (recs.get("kb_recall") or {}).get("counts") or {}
    ch = (recs.get("kb_recheck") or {}).get("counts") or {}
    print("=" * 78)
    print("%s items enumerated from three sources that must agree: %s with a document naming the exact"
          % (inv.get("items", "?"), inv.get("documented", "?")))
    print("part, %s covered by a family document with a declared reason, %s open picks with no part"
          % (inv.get("family", "?"), inv.get("open_pick", "?")))
    print("chosen yet, and %s uncovered." % inv.get("uncovered", "?"))
    r = [v for k, v in rc.items() if k.startswith("recall_at_")]
    print("Retrieval: recall %s over %s questions on %s parts, %s adversarial failures."
          % (r[0] if r else "not measured", rc.get("questions", "?"), rc.get("parts", "?"),
             rc.get("adversarial_failures", "?")))
    print("Currency: %s documents compared against their vendor as of %s, %s changed, %s unreachable,"
          % (ch.get("checked", "?"), ch.get("as_of", "?"), ch.get("changed", "?"), ch.get("unreachable", "?")))
    print("%s recorded with a folder-level source rather than a URL and checkable only by hand."
          % ch.get("no_url", "?"))
    print()
    print("Every figure above is a gate's own, and the exit code is the worst of them. What this does")
    print("NOT say: that a document is the current revision (only that its bytes still match the")
    print("vendor's on the date shown), that an OCR sidecar's numbers are right (they are an index,")
    print("never a source), or that the open picks are decided (they are not, and they are listed).")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
