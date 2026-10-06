#!/usr/bin/env python3
"""W42 (MESHSAT-1357, set 32, 6 October 2026): one sentence for the supplier entry page's section 0e, item 1.

The page `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md` is the integrator's file. On main it carries section 0e ("How to
reproduce set 30's figures"), whose item 1 gives the fetch of the makers' sheets held back by their terms; on branch
`fnd/w34pdftext` W37 added the held-back text's re-take to section 7, item 2 (the branch's lines 154 to 162), which section 0e does
not mention. This script adds one sentence at the end of section 0e's item 1 that points to that step. It names no path and states
no result. It runs on the integrated tree, after the branch is merged into main's lineage:

    python3 v2/docs/records/w42cite/apply_supplier_0e_pointer.py [<repository root>]

It refuses (exit 2, the page unchanged) when the page has no section 0e, when the old words are not found exactly once inside
section 0e, when section 7 does not carry the re-take step it points to, or when the sentence is already there (a second run). It
writes the page only when the new text differs, keeps every line where it was (the sentence goes inside an existing line, so a
citation of the page by line still finds its text), and re-reads the page after writing.
"""
import os
import sys

PAGE = "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md"
HEAD_0E = "### 0e. How to reproduce"
HEAD_7 = "## 7. How to check the claims"
RETAKE = "retake_pdf_text.py"                   # the step section 7, item 2 gives (W37, fnd/w34pdftext 82e1e1c6)
OLD = "the sheets land in gitignored `held/` folders, are checked by sha256 and are never committed."
SENTENCE = ("Where a record reads a held-back sheet as its extracted text rather than as the PDF, that text is held back with the "
            "sheet and is re-taken after the fetch, before the record's script runs; section 7, item 2 gives the command and the "
            "tool versions it needs.")
NEW = OLD + " " + SENTENCE
DASHES = (chr(0x2013), chr(0x2014))


class Refused(Exception):
    pass


def _section(text, head):
    """The text from the heading `head` to the next heading of the same or a higher level, or None."""
    i = text.find("\n" + head)
    if i < 0:
        return None
    level = head.split(" ")[0]
    j, stops = len(text), ["\n## "] if level == "##" else ["\n## ", "\n### "]
    for s in stops:
        k = text.find(s, i + 1 + len(head))
        if 0 <= k < j:
            j = k
    return i + 1, j


def apply(text):
    """The page with the sentence added, or Refused with the reason."""
    if SENTENCE in text:
        raise Refused("the sentence is already on the page (a second run)")
    span = _section(text, HEAD_0E)
    if span is None:
        raise Refused("the page has no section 0e (%r)" % HEAD_0E)
    a, b = span
    if text.count(OLD) != 1 or not (a <= text.find(OLD) < b):
        raise Refused("the old words are not found exactly once inside section 0e: %r" % OLD)
    s7 = _section(text, HEAD_7)
    if s7 is None or RETAKE not in text[s7[0]:s7[1]]:
        raise Refused("section 7 does not carry the re-take step (%s) the sentence points to" % RETAKE)
    new = text.replace(OLD, NEW, 1)
    assert new != text
    assert new.count("\n") == text.count("\n"), "a line was added or removed"
    heads = [ln for ln in text.split("\n") if ln.startswith("#")]
    assert [ln for ln in new.split("\n") if ln.startswith("#")] == heads, "a heading changed"
    for d in DASHES:
        assert d not in SENTENCE
    return new


def main(argv):
    root = os.path.abspath(argv[1]) if len(argv) > 1 else \
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    path = os.path.join(root, PAGE)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        new = apply(text)
    except Refused as e:
        print("REFUSED: %s; %s unchanged" % (e, PAGE))
        return 2
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    with open(path, encoding="utf-8") as f:
        back = f.read()
    assert back == new and SENTENCE in back and back.count(NEW) == 1
    print("APPLIED: section 0e, item 1 of %s carries the pointer to section 7, item 2 (%d lines, unchanged)"
          % (PAGE, back.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
