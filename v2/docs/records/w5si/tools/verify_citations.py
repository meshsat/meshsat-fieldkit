#!/usr/bin/env python3
"""Hold an evidence file of this stream to the documents it quotes (stream w5si, 27 September 2026, MESHSAT-1357).

An evidence file is YAML with `parts`, each naming one held document (`document`, `sha256_16`) and quoting it
(`quotes` and `edge.quotes`: page and words). This checks, with edge_length.py's own check of a citation, that every
document is held, is the file cited, and carries the quoted words on the page named. It writes nothing.

Usage: verify_citations.py <repository root> <evidence.yaml>      exit 1 if a citation does not hold
"""
import os, sys


def main(root, path):
    import yaml
    sys.path.insert(0, os.path.join(root, "v2", "ecad", "tools"))
    import edge_length as E
    d = yaml.safe_load(open(path, encoding="utf-8"))
    n = bad = 0
    for p in d["parts"]:
        for q in list(p.get("quotes") or []) + list((p.get("edge") or {}).get("quotes") or []):
            rec = {"checked": [{"document": p["document"], "sha256_16": p["sha256_16"], "page": q["page"], "quote": q["quote"]}]}
            assert E._cite_shape(rec) is None, (p["id"], E._cite_shape(rec))
            why = E._quotes_hold(rec, root)
            n += 1
            if why: bad += 1; print("DOES NOT HOLD %s p.%s: %s" % (p["id"], q["page"], why))
    print("%s: %d citation(s) of %d document(s), %d do not hold" % (os.path.basename(path), n, len(d["parts"]), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 3: print(__doc__); sys.exit(2)
    sys.exit(main(os.path.abspath(sys.argv[1]), sys.argv[2]))
