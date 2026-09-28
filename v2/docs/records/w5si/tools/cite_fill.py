#!/usr/bin/env python3
"""Give every citation of tools/pcb_edge_rates.yaml the sha256/16 of the held file and the page its words are on
(stream w5si, 27 September 2026, MESHSAT-1357). A record of how the fields were written, run once; it is not a tool of
the pipeline. edge_length.py checks every field it writes on each run (the held file's sha256/16, the quoted words on
the page named, an IBIS record's keyword and cell), so a wrong field here reads as a record that decides nothing.

What it does, on the TEXT of the data file (comments and layout kept):
  * a citation written as a flow mapping `{document: <path>, quote: "..."}` gets `sha256_16` and, for a PDF, `page`
    (the first page, as pdftotext counts them, whose words contain the quote, whitespace collapsed); a document that is
    not a PDF gets `where` unless the record already says (an IBIS file: the keyword quoted);
  * a `document:` line written in block style, at any depth, gets `sha256_16:` and `page:` lines after it, the page
    found from the `quote:` of the same mapping (the lines at the same indent); a mapping that carries `clause:`
    keeps it and gets its page as well when the document is a PDF;
  * an `ibis:` mapping gets `sha256_16`, `keyword` and `ramp` from ibis_read.fastest_cite on the held model.
It refuses to run twice (a citation that already carries sha256_16), asserts the text changed, and re-parses the file.

Usage: cite_fill.py <repository root> [--write]      without --write it prints what it would write
"""
import os, re, sys, hashlib, subprocess

def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
def norm(t): return " ".join(re.sub(r"(?m)^\s*>\s?", " ", t).split())
_PAGES = {}
def pages(p):
    if p not in _PAGES:
        out = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=300).stdout
        _PAGES[p] = [norm(x) for x in out.split("\f")]
    return _PAGES[p]
def page_of(p, quote):
    q = norm(quote)
    hits = [i + 1 for i, t in enumerate(pages(p)) if q in t]
    return hits


def main(root, write):
    import yaml
    sys.path.insert(0, os.path.join(root, "v2", "ecad", "tools"))
    import ibis_read
    path = os.path.join(root, "v2", "ecad", "tools", "pcb_edge_rates.yaml")
    text = open(path, encoding="utf-8").read()
    assert "sha256_16" not in text.split("\ninterfaces:", 1)[1], "already applied: a record carries sha256_16"
    log = []

    def fields(doc, quote, has_where):
        p = os.path.join(root, doc)
        assert os.path.isfile(p), "not held: %s" % doc
        f = ['sha256_16: "%s"' % sha16(p)]
        if p.lower().endswith(".pdf"):
            hits = page_of(p, quote)
            assert hits, "the quote %r is on no page of %s" % (quote, doc)
            f.append("page: %d" % hits[0])
            log.append("%s page %d%s: %r" % (doc, hits[0], " (also on %s)" % ", ".join(map(str, hits[1:6])) if hits[1:] else "", quote[:70]))
        elif not has_where:
            assert norm(quote) in norm(open(p, encoding="utf-8", errors="replace").read()), (doc, quote)
            w = ("the keyword quoted" if p.lower().endswith(".ibs") else "the words quoted, found by search: the document has no pages")
            f.append('where: "%s"' % w)
            log.append("%s (%s): %r" % (doc, w, quote[:70]))
        return f

    # 1. flow mappings that cite a document (they never nest, and may run over two lines)
    def flow(m):
        body = m.group(0)
        d = yaml.safe_load(body)
        if not (isinstance(d, dict) and d.get("document") and "quote" in d): return body
        f = fields(d["document"], d["quote"], bool(d.get("where") or d.get("clause")))
        doc = d["document"]
        i = body.index("document: " + doc) + len("document: " + doc)
        return body[:i] + ", " + ", ".join(f) + body[i:]
    text2 = re.sub(r"\{[^{}]*\bdocument:[^{}]*\}", flow, text)

    # 2. a document line in block style, with the quote of the same mapping (the lines at the same indent)
    out, lines, i = [], text2.split("\n"), 0
    def indent(x): return len(x) - len(x.lstrip(" "))
    def key_indent(x):                       # "      - match: ..." opens a mapping whose keys sit two further in
        return indent(x) + 2 if x.lstrip(" ").startswith("- ") else indent(x)
    while i < len(lines):
        ln = lines[i]; out.append(ln)
        m = re.match(r"^( +)document: (\S+)\s*$", ln)
        if m:
            ind, quote, clause = len(m.group(1)), None, False
            def look(x):
                nonlocal quote, clause
                body = x.lstrip(" ")
                if body.startswith("- "): body = body[2:]
                if body.startswith("clause:"): clause = True
                if body.startswith("quote:") and quote is None: quote = yaml.safe_load(body)["quote"]
            k = i - 1
            while k >= 0 and lines[k].strip() and key_indent(lines[k]) >= ind:
                if key_indent(lines[k]) == ind: look(lines[k])
                if lines[k].lstrip(" ").startswith("- ") and indent(lines[k]) < ind: break
                k -= 1
            j = i + 1
            while j < len(lines) and lines[j].strip() and indent(lines[j]) >= ind and not lines[j].lstrip(" ").startswith("- "):
                if indent(lines[j]) == ind: look(lines[j])
                j += 1
            assert quote, "a mapping cites %s and quotes nothing" % m.group(2)
            for f in fields(m.group(2), quote, clause): out.append(" " * ind + f)
        i += 1
    text3 = "\n".join(out)

    # 3. the IBIS models
    raw = yaml.safe_load(text)
    for fam in raw["families"]:
        if fam.get("kind") != "IBIS": continue
        ib = fam["ibis"]; p = os.path.join(root, ib["file"])
        model = ibis_read.load(p)
        if ib.get("selector_add"):
            model = dict(model, selectors=dict(model["selectors"]))
            for sel, extra in ib["selector_add"].items():
                model["selectors"][sel.lower()] = list(model["selectors"].get(sel.lower(), [])) + list(extra)
        kw, cell = ibis_read.fastest_cite(model, ib["component"], ib.get("models"))
        assert kw and cell, fam["id"]
        add = 'sha256_16: "%s", keyword: "%s", ramp: "%s"' % (sha16(p), kw, cell)
        one = "ibis: {file: %s, " % ib["file"]
        blk = "    ibis:\n      file: %s\n" % ib["file"]
        if text3.count(one) == 1:
            text3 = text3.replace(one, one + add + ", ")
        else:
            assert text3.count(blk) == 1, fam["id"]
            text3 = text3.replace(blk, blk + "".join("      %s\n" % x for x in add.split(", ")))
        log.append("%s %s: %s, %s" % (fam["id"], ib["file"], kw, cell))

    assert text3 != text
    d = yaml.safe_load(text3)
    assert [len(d[k]) for k in ("interfaces", "families", "far_ends", "open_drain")] == \
           [len(raw[k]) for k in ("interfaces", "families", "far_ends", "open_drain")]
    for ln in log: print(ln)
    print("%d citation(s) and model(s) given their sha256/16 and place" % len(log))
    if write:
        open(path, "w", encoding="utf-8").write(text3)
        print("written: %s sha256/16 %s" % (path, sha16(path)))


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    main(os.path.abspath(sys.argv[1]), "--write" in sys.argv)
