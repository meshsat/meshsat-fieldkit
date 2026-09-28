#!/usr/bin/env python3
"""Which cited document states its own revision, edition or date (worker d6rel, MESHSAT-1357, 28 September 2026).

READ ONLY. For every document pcb_reliability.yaml cites (a class's `source` or `looked_in`), the text layer is read
with pdftotext and the lines that look like a revision marking are printed, for a PERSON to read: a line printed here
is a candidate, and only a marking that names itself a revision, an edition, an issue or a date of the document is
carried into the list as `revision:`. A document with no such line keeps the stream's open item. An HTML capture is
dated by its capture (the file name and v2/vendor/sources.txt), and a PDF with no text layer says so.

Usage: revision_scan.py <repository root>
"""
import os, re, sys, subprocess

MARK = re.compile(r"(revis|\brev\b\.?|edition|\bissued?\b|(?:19|20)\d\d[./-]\d\d?|\d\d?/\d\d?/\d\d(?:\d\d)?"
                  r"|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,? +(?:19|20)\d\d|©|cat\. ?no|doc\w* ?no)", re.I)


def main(argv):
    root = os.path.abspath(argv[0])
    sys.path.insert(0, os.path.join(root, "v2", "ecad", "tools"))
    import yaml
    d = yaml.safe_load(open(os.path.join(root, "v2", "ecad", "tools", "pcb_reliability.yaml"), encoding="utf-8"))
    docs = set()
    for b in d["boards"].values():
        for c in b["classes"]:
            s = c.get("source")
            for x in (s if isinstance(s, list) else ([s] if s else [])) + ((c.get("no_figure") or {}).get("looked_in") or []):
                docs.add(x["document"])
    for doc in sorted(docs):
        p = os.path.join(root, doc)
        if not p.endswith(".pdf"):
            print("-- %s\n      (an HTML capture: dated by its capture, see the file name and sources.txt)" % doc); continue
        t = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout
        if len(t.strip()) < 40:
            print("-- %s\n      (no text layer: %d characters; render the page to read it)" % (doc, len(t.strip()))); continue
        hits = []
        for ln in t.split("\n"):
            s = " ".join(ln.split())
            if 2 < len(s) < 130 and MARK.search(s) and s not in hits: hits.append(s)
        print("-- %s" % doc)
        for h in hits[:6]: print("      %s" % h[:140])
        if not hits: print("      (no line that looks like a revision marking)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
