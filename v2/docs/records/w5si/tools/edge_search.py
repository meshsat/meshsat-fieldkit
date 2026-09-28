#!/usr/bin/env python3
"""Every document a BOUND or MODEL record of tools/pcb_edge_rates.yaml cites, searched for the words a published
transition time is written with (stream w5si, 27 September 2026, MESHSAT-1357). A record of a search, run by hand; its
output is filed beside it as readings/edge-search.txt.

WHY. A bound says "the maker publishes no minimum transition for this output". A quote of the part's name proves the
document is held, not that anyone looked (the independent check of 27 September 2026). This lists, per document, every
line that carries one of the words below with its page, so a reader sees what the document does say about edges, and
the documents where none of the words occurs at all.

The lines are the documents' own words with two changes: whitespace is collapsed, and the long dashes a table prints
in an empty cell are written as hyphens (this repository writes no long dash).

Usage: edge_search.py <repository root> [--write]
       --write files the listing as v2/docs/records/w5si/readings/edge-search.txt and writes its path and sha256/16
       into the data file's `search_listing`, which edge_length.py holds every bound's documents against
"""
import os, re, sys, subprocess, hashlib

WORDS = ("rise time", "fall time", "rise/fall", "rise and fall", "transition time", "transition rise", "transition fall",
         "turn-on time", "turn-off time", "switching time", "rise or fall",
         "slew rate", "slew-rate", "output transition", "edge rate")
SYMS = re.compile(r"(?<![A-Za-z])(t[rRfF]|tof|tOF|tfo|t\(F\)|t\(R\)|tRise|tFall|TFR|TFF)(?![A-Za-z])")


LISTING = "v2/docs/records/w5si/readings/edge-search.txt"


def main(root, write=False):
    import yaml, io
    out = io.StringIO()
    def print(*a):                                      # the listing is built whole, then shown or filed
        out.write(" ".join(str(x) for x in a).replace("\u2014", "-").replace("\u2013", "-") + "\n")
    ypath = os.path.join(root, "v2/ecad/tools/pcb_edge_rates.yaml")
    d = yaml.safe_load(open(ypath, encoding="utf-8"))
    docs = {}
    for sect in ("interfaces", "families"):
        for r in d.get(sect) or []:
            if r.get("kind") not in ("BOUND", "MODEL"): continue
            for c in list(r.get("checked") or []) + list(r.get("pin_edges") or []) + [r]:
                if isinstance(c, dict) and c.get("document"): docs.setdefault(c["document"], set()).add(r["id"])
    none = []
    for doc in sorted(docs):
        p = os.path.join(root, doc)
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
        if p.lower().endswith(".pdf"):
            pages = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=300).stdout.split("\f")
        else:
            pages = [open(p, encoding="utf-8", errors="replace").read()]
        hits = []
        for i, t in enumerate(pages, 1):
            for ln in t.splitlines():
                low = ln.lower()
                if any(w in low for w in WORDS) or (SYMS.search(ln) and re.search(r"\b(ns|ps|µs|μs|us)\b", ln)):
                    hits.append((i, " ".join(ln.split())[:170]))
        print("== %s (sha256/16 %s, %d page(s)); cited by %s: %d line(s)" % (doc, sha, len(pages), ", ".join(sorted(docs[doc])), len(hits)))
        if not hits: none.append(doc)
        shown = hits[:40]
        for pg, ln in shown: print("   p.%d  %s" % (pg, ln))
        if len(hits) > len(shown): print("   ... and %d more line(s), on pages %s" % (len(hits) - len(shown), ", ".join(str(x) for x in sorted({h[0] for h in hits[40:]})[:40])))
    print("\nDOCUMENTS IN WHICH NONE OF THE WORDS OCCURS (%d): %s" % (len(none), ", ".join(none)))
    print("words: %s; symbols with a time unit on the line: %s" % (", ".join(WORDS), SYMS.pattern))
    text = out.getvalue()
    if not write:
        sys.stdout.write(text); return
    lp = os.path.join(root, LISTING)
    os.makedirs(os.path.dirname(lp), exist_ok=True)
    open(lp, "w", encoding="utf-8").write(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    y = open(ypath, encoding="utf-8").read()
    line = 'search_listing: {path: %s, sha256_16: "%s"}' % (LISTING, sha)
    if re.search(r"(?m)^search_listing: .*$", y):
        y2 = re.sub(r"(?m)^search_listing: .*$", line, y)
    else:
        anchor = 'written: "2026-09-27"\n'
        assert y.count(anchor) == 1
        y2 = y.replace(anchor, anchor + line + "\n")
    assert yaml.safe_load(y2)["search_listing"] == {"path": LISTING, "sha256_16": sha}
    if y2 != y: open(ypath, "w", encoding="utf-8").write(y2)
    sys.stdout.write("%s: %d document(s), sha256/16 %s; the data file names it%s\n" % (
        LISTING, text.count("\n== ") + text.startswith("== "), sha, "" if y2 != y else " already"))


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.stdout.write(__doc__); sys.exit(2)
    main(os.path.abspath(sys.argv[1]), "--write" in sys.argv)
