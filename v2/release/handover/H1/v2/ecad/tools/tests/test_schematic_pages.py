#!/usr/bin/env python3
"""Every board's schematic is drawn by the page engine and cut into A3 pages (MESHSAT-862, 15 September 2026, appendix 32.196).

The owner opened the 15 September pack and found "one component connected to the next in straight endless lines": the
schematics were a netlist with pictures. `schlayout.py` replaces the layout with framed A3 pages of wired functional blocks,
proves the drawing's own connectivity against the generator's pin map before the file is written, and `sch_pages.py` cuts
the sheet along the cell grid so the PDF a reader opens is those pages. These rules keep every generator on that path."""
import glob, os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENS = sorted(glob.glob(os.path.join(TOOLS, "gen_sch_?.py")))


def t_every_schematic_generator_lays_out_through_the_page_engine():
    for g in GENS:
        s = open(g).read()
        assert "schlayout.run(" in s, "%s does not use schlayout" % os.path.basename(g)
        assert "kisch.reband(" not in s, "%s still folds a row of columns" % os.path.basename(g)


def t_the_engine_verifies_its_own_connectivity_before_the_file_is_written():
    s = open(os.path.join(TOOLS, "schlayout.py")).read()
    i = s.find("def run("); assert i > 0
    assert "verify(eng)" in s[i:], "run() does not verify the drawing against the pin map"
    assert "SHORT" in s and "UNNAMED" in s and "drawn %d times" in s, "the verifier does not name shorts, unnamed nets and missing parts"


def t_the_build_cuts_the_sheet_into_pages_without_the_drawing_sheet_border():
    b = open(os.path.join(TOOLS, "build_sch.sh")).read()
    assert "--exclude-drawing-sheet" in b, "the sheet PDF still carries the A0 frame across the cells"
    assert "sch_pages.py" in b, "the sheet is not cut into pages"


def t_the_sheet_pdf_carries_no_property_popups():
    """26 September 2026 (MESHSAT-1357): KiCad's per-field popups put 10480 link annotations on board B's one page, poppler
    refuses a page over 10000 and every tile rendered blank. The export must leave them out."""
    b = open(os.path.join(TOOLS, "build_sch.sh")).read()
    assert "--exclude-pdf-property-popups" in b, "the sheet PDF carries KiCad's property popups again"


def _pages_fixture(d, ink_cells):
    """A two-cell sheet (2 x 1 A3 cells of schlayout's grid) and its PDF, with a filled square in the cells named."""
    import subprocess
    w_mm, h_mm = 2 * 330 * 1.27, 234 * 1.27
    open(os.path.join(d, "s.kicad_sch"), "w").write('(kicad_sch (paper "User" %.2f %.2f))\n' % (w_mm, h_mm))
    w_pt, h_pt = w_mm / 25.4 * 72, h_mm / 25.4 * 72
    body = "".join("0 g %.1f 200 400 400 re f\n" % (c * w_pt / 2 + 200) for c in ink_cells)
    open(os.path.join(d, "page.txt"), "w").write("%%%%MediaBox 0 0 %.1f %.1f\n%s" % (w_pt, h_pt, body))
    subprocess.run(["mutool", "create", "-o", os.path.join(d, "sheet.pdf"), os.path.join(d, "page.txt")], check=True, capture_output=True)


def t_a_sheet_of_cells_with_no_ink_anywhere_is_refused_and_an_inked_one_is_paged():
    """THE DEFECTIVE FIXTURE is a two-cell sheet with no ink, which is what a sheet looks like to this tool when poppler
    refuses to render its tiles: it must exit non-zero rather than write a PDF with no page. THE ACCEPTABLE FIXTURE is
    the same sheet with one filled square in the second cell: one page kept, exit 0."""
    import shutil, subprocess, sys, tempfile
    from harness import Skip
    if not (shutil.which("mutool") and shutil.which("pdftoppm")): raise Skip("mutool or pdftoppm is not on this host")
    try: import PIL  # noqa: F401
    except ImportError: raise Skip("Pillow is not on this host")
    tool = os.path.join(TOOLS, "sch_pages.py")
    for cells, want_rc, want_pages in (((), "nonzero", None), ((1,), 0, 1)):
        d = tempfile.mkdtemp(prefix="schpages-fixture-")
        _pages_fixture(d, cells)
        p = subprocess.run([sys.executable, tool, os.path.join(d, "s.kicad_sch"), os.path.join(d, "sheet.pdf"), os.path.join(d, "out.pdf")],
                           capture_output=True, text=True)
        if want_rc == "nonzero":
            assert p.returncode != 0, "a sheet with no ink in any cell was paged into %s: %s" % (d, p.stdout + p.stderr)
            assert "not one tile carries ink" in p.stdout + p.stderr, p.stdout + p.stderr
        else:
            assert p.returncode == 0, p.stdout + p.stderr
            assert "%d pages kept of 2 tiles" % want_pages in p.stdout, p.stdout


def t_wires_are_cut_at_junctions_and_labels():
    s = open(os.path.join(TOOLS, "schlayout.py")).read()
    assert "junction" in s and "cuts = set(junctions)" in s, "a junction on an unsplit wire disconnects everything past it (measured 15 Sep 2026)"


def t_no_generator_comment_carries_a_call():
    import io, re, tokenize
    for g in GENS:
        for tok in tokenize.generate_tokens(io.StringIO(open(g).read()).readline):
            if tok.type == tokenize.COMMENT: assert not re.search(r";\s*[A-Za-z_]\w*\(", tok.string), "%s:%d" % (os.path.basename(g), tok.start[0])
