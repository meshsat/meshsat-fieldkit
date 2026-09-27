#!/usr/bin/env python3
"""Read every rendered diagram back (MESHSAT-1357, handover layer 4): the check that a rendered file shows what it claims.

For each SVG in v2/docs/diagrams/svg/: it must parse as XML, carry no <foreignObject> (so any SVG viewer, not only a
browser, shows its text), and state in its own text that it is a design diagram of an unbuilt prototype. Each SVG is then
rasterised in a headless Chromium (Playwright) to <out>/<name>.png, the image a reader's browser shows, for a person or
an agent to look at. Each PDF in pdf/ is rasterised with pdftoppm to <out>/<name>-pdf-1.png, READBACK_MAX_PX on its long
side like the SVGs, and its page is measured with pdfinfo against the SVG's natural size: a PDF printed smaller than
0.9 of the drawing's natural size is a problem (the review of 27 September 2026 found the Mermaid PDFs fitted to a
600 pt page, their text at 1 to 2 pt). Each check's figures are printed, so the output is the record of the readback.

Usage: python3 v2/docs/diagrams/tools/readback.py [out_dir]   (default: a new temporary directory, printed)
Needs: python3 with playwright and a Chromium it can launch (CHROME_BIN to name one); pdftoppm and pdfinfo (poppler) for
the PDF checks, which are reported as not run when poppler is missing."""
import glob, os, re, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
PHRASE = "unbuilt prototype"
MAX_PX = int(os.environ.get("READBACK_MAX_PX", "2400"))


def natural_pt(root):
    """The drawing's natural width and height in points: Mermaid writes width="100%" over a viewBox in CSS pixels
    (0.75 pt each); matplotlib writes width and height in pt over a viewBox in pt."""
    vb = [float(x) for x in (root.get("viewBox") or "0 0 0 0").replace(",", " ").split()]
    w = root.get("width") or ""
    if w.endswith("pt"):
        return float(w[:-2]), float((root.get("height") or "0pt")[:-2])
    return vb[2] * 0.75, vb[3] * 0.75


def pdf_page_pt(pdf):
    r = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
    m = re.search(r"Page size:\s+([0-9.]+) x ([0-9.]+) pts", r)
    pages = re.search(r"Pages:\s+(\d+)", r)
    return float(m.group(1)), float(m.group(2)), int(pages.group(1)) if pages else 0


def text_of(svg_path):
    root = ET.parse(svg_path).getroot()
    return " ".join(t for t in root.itertext()), root


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="diagram-readback-")
    os.makedirs(out, exist_ok=True)
    bad = []
    svgs = sorted(glob.glob(os.path.join(D, "svg", "*.svg")))
    for p in svgs:
        n = os.path.basename(p)[:-4]
        try:
            txt, root = text_of(p)
        except ET.ParseError as e:
            bad.append("%s: not XML (%s)" % (n, e)); continue
        if re.search(r"foreignObject", open(p, encoding="utf-8").read()):
            bad.append("%s: carries foreignObject (HTML labels)" % n)
        if PHRASE not in re.sub(r"\s+", " ", txt):
            bad.append("%s: its text does not say it is a design diagram of an unbuilt prototype" % n)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        kw = {"executable_path": os.environ["CHROME_BIN"]} if os.environ.get("CHROME_BIN") else {}
        br = pw.chromium.launch(args=["--no-sandbox"], **kw)
        pg = br.new_page(device_scale_factor=1)
        for p in svgs:
            n = os.path.basename(p)[:-4]
            _, root = text_of(p)
            vb = [float(x) for x in (root.get("viewBox") or "0 0 %s %s" % (root.get("width"), root.get("height"))).replace(",", " ").split()]
            w, h = vb[2], vb[3]
            k = MAX_PX / max(w, h)                    # every raster MAX_PX on its long side, so small drawings are read in detail too
            W, H = int(w * k) + 1, int(h * k) + 1
            pg.set_viewport_size({"width": W, "height": H})
            wrap = os.path.join(out, n + ".view.html")   # a file page, so the browser may load the file:// image
            open(wrap, "w").write("<html><body style='margin:0;background:#fff'><img src='file://%s' style='width:%dpx;height:%dpx'>"
                                  "</body></html>" % (p, W - 1, H - 1))
            pg.goto("file://" + wrap); pg.wait_for_load_state("load")
            ok = pg.evaluate("() => { const i = document.querySelector('img'); return i.complete && i.naturalWidth > 0; }")
            if not ok: bad.append("%s: the browser could not load the SVG as an image" % n)
            pg.screenshot(path=os.path.join(out, n + ".png"), timeout=120000)
            print("%-34s drawing %6.0f x %-6.0f  raster %5d x %-5d  %s" % (n, w, h, W, H, os.path.join(out, n + ".png")))
        br.close()
    if shutil.which("pdftoppm") and shutil.which("pdfinfo"):
        for p in sorted(glob.glob(os.path.join(D, "pdf", "*.pdf"))):
            n = os.path.basename(p)[:-4]
            pw, ph, pages = pdf_page_pt(p)
            svg = os.path.join(D, "svg", n + ".svg")
            if os.path.exists(svg):
                nw, nh = natural_pt(ET.parse(svg).getroot())
                k = pw / nw if nw else 0
                print("%-34s pdf %8.1f x %-7.1f pt, %d page(s); drawing %8.1f x %-7.1f pt natural; scale %.2f" % (n, pw, ph, pages, nw, nh, k))
                if k < 0.9:
                    bad.append("%s: the PDF prints the drawing at %.2f of its natural size" % (n, k))
            else:
                bad.append("%s: a PDF with no SVG beside it" % n)
            if pages != 1:
                bad.append("%s: the PDF has %d pages, 1 expected" % (n, pages))
            subprocess.run(["pdftoppm", "-scale-to", str(MAX_PX), "-f", "1", "-l", "1", "-png", p, os.path.join(out, n + "-pdf")], check=True)
    else:
        print("PDF checks not run: pdftoppm or pdfinfo (poppler) not found")
    print("problems: %s" % ("none" if not bad else ""))
    for b in bad:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
