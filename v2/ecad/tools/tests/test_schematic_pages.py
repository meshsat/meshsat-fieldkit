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


def t_wires_are_cut_at_junctions_and_labels():
    s = open(os.path.join(TOOLS, "schlayout.py")).read()
    assert "junction" in s and "cuts = set(junctions)" in s, "a junction on an unsplit wire disconnects everything past it (measured 15 Sep 2026)"


def t_no_generator_comment_carries_a_call():
    import io, re, tokenize
    for g in GENS:
        for tok in tokenize.generate_tokens(io.StringIO(open(g).read()).readline):
            if tok.type == tokenize.COMMENT: assert not re.search(r";\s*[A-Za-z_]\w*\(", tok.string), "%s:%d" % (os.path.basename(g), tok.start[0])
