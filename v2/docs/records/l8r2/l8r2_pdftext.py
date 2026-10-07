"""l8r2_pdftext.py: the makers' PDF texts record l8r2's TESTS read (MESHSAT-1357, W81, 6 October 2026). Declarations only: nothing
here runs.

test_l8r2.t_round4_the_catalogue_figures_read_from_the_held_pages reads the four held San Ace catalogue pages (C1152B001
'25.10, pp. 362, 616, 623 and 633) against the cooler's figures l8r2_drafts.py types in V and F. It ran the host's pdftotext
on each page until W81's census of the test modules found it.
A module's table holds its own reads (PDFTEXT-INVENTORY.md section 2; W55 declined to put a read in a table whose script does not make
it, because that script's output would then print an input it never reads), so these reads are declared here, apart from the
generators' tables: the record's outputs and its generators are unchanged. The test reads each text through
v2/docs/records/_lib/pdftext.py with this table (PT.declared_in), so the reading no longer depends on the host's poppler, the defect
W34 corrected in the generators (pdftext.py's header). The pages are held back by their terms (l8r2's fetch_held_back.py), so their
texts are held back beside them, under
held/pdftext/. Re-take after a sheet changes:
    python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l8r2
"""
PDFTEXT = {
    "v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0362.pdf": [["-layout"]],
    "v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0616.pdf": [["-layout"]],
    "v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0623.pdf": [["-layout"]],
    "v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0633.pdf": [["-layout"]],
}
