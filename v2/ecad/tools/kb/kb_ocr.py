#!/usr/bin/env python3
"""kb_ocr.py, text for the drawings that have none (MESHSAT-862, 11 September 2026).

Five current vendor PDFs carry no text layer at all and every one is a mechanical drawing: the SMA
bulkhead, two M.2 sockets, the Xenarc dimensional drawing, the LG290P breakout schematic. They are
exactly where package and dimension errors hide, and they are the only documents in this store that
search cannot reach.

They carry no font objects, so their lettering is drawn as vector paths: rasterise and read it.
`pdftoppm` and `tesseract` are on this host, so this needs nothing new.

WHAT AN OCR SIDECAR IS AND IS NOT. It is a searchable index of a drawing, so that asking about the
part finds the drawing. It is NOT a source of numbers. OCR misreads exactly the characters that
matter on a drawing: a decimal point, a tolerance, an H7, a 6 against an 8. So every sidecar says so
at the top, kb_search labels its hits, and the citation always points at the original page. The
sidecar tells you WHICH drawing to open; the drawing tells you the number.

Usage: kb_ocr.py [path ...]      (default: every current PDF with no text and no sidecar)
       kb_ocr.py --list          (what would be done, without doing it)
"""
import sys, os, re, glob, argparse, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "vendor"))
DPI = 300


def needs_ocr(path):
    if not path.lower().endswith(".pdf"):
        return False
    if os.path.exists(os.path.splitext(path)[0] + ".ocr.txt"):
        return False
    out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=300)
    return len("".join(out.stdout.split())) < 40


def ocr_pdf(path):
    """Page by page, so a hit can still say which page to open."""
    pages = []
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png", path, os.path.join(td, "p")],
                       check=True, timeout=900)
        for png in sorted(glob.glob(os.path.join(td, "p*.png"))):
            r = subprocess.run(["tesseract", png, "-", "-l", "eng", "--psm", "11"],
                               capture_output=True, text=True, timeout=300)
            text = re.sub(r"[ \t]+", " ", r.stdout)
            text = "\n".join(l.strip() for l in text.splitlines() if l.strip())
            pages.append(text)
    return pages


def legibility(pages):
    """A rough figure for how much of this came back as words rather than noise.

    It matters and it varies enormously: the Xenarc drawing yields "Physical Resolution: 1024 x 600",
    the Amphenol SMA drawing yields almost nothing because its callouts are rotated. A reader has to be
    told which of the two they are looking at instead of inferring it from the mess."""
    words = re.findall(r"[A-Za-z]{3,}", "\n".join(pages))
    chars = len("".join("".join(pages).split()))
    return len(words), chars


def write_sidecar(path, pages):
    rel = os.path.relpath(path, VENDOR)
    name = os.path.splitext(os.path.basename(rel))[0]
    L = ["OCR of %s, a drawing with no text layer" % rel, ""]
    L.append("Read by tools/kb/kb_ocr.py at %d dpi with tesseract, because this document carries no" % DPI)
    L.append("font objects: its lettering is drawn as vector paths and no text extractor can reach it.")
    L.append("")
    L.append("THIS IS AN INDEX, NOT A SOURCE OF NUMBERS. OCR misreads exactly the characters that matter")
    L.append("on a drawing: a decimal point, a tolerance, an H7, a 6 against an 8. Use this to find WHICH")
    L.append("drawing to open. Then open it:  pdftoppm -r 300 -png -f <page> -l <page> v2/vendor/%s" % rel)
    L.append("Every dimension quoted anywhere in this project must come from the drawing, never from here.")
    L.append("")
    words, chars = legibility(pages)
    if words < 40:
        L.append("LEGIBILITY: POOR. %d word-like tokens in %d characters. This drawing's lettering did not"
                 % (words, chars))
        L.append("survive rasterisation, most likely because its callouts are rotated. Treat the text below")
        L.append("as nothing more than a pointer to the file.")
    else:
        L.append("LEGIBILITY: %d word-like tokens in %d characters." % (words, chars))
    L.append("")
    for i, text in enumerate(pages, 1):
        L.append("--- %s, page %d, as read by OCR ---" % (name, i))
        L.append(text if text.strip() else "(nothing legible on this page)")
        L.append("")
    open(os.path.splitext(path)[0] + ".ocr.txt", "w").write("\n".join(L) + "\n")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    paths = a.paths or sorted(p for p in glob.glob(os.path.join(VENDOR, "**", "*"), recursive=True)
                              if needs_ocr(p))
    if a.list:
        for p in paths:
            print("would OCR: %s" % os.path.relpath(p, VENDOR))
        return 0
    for p in paths:
        try:
            pages = ocr_pdf(p)
        except Exception as e:
            print("kb_ocr: %s failed (%s: %s)" % (os.path.relpath(p, VENDOR), type(e).__name__, e))
            continue
        write_sidecar(p, pages)
        got = sum(1 for t in pages if t.strip())
        print("kb_ocr: %-56s %d page(s), %d legible" % (os.path.relpath(p, VENDOR), len(pages), got))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
