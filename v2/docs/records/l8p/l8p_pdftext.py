"""l8p_pdftext.py: the makers' PDF texts record l8p's TESTS read (MESHSAT-1357, W81, 6 October 2026). Declarations only: nothing here runs.

test_l8p.t_round5_the_alternative_parts_typed_figures_are_tdks reads TDK's held B59721A sheet (August 2019) against the
figures l8p_drafts.py types in TDK_B59721. It read it through l8p_drafts.pdftext(), whose table does not declare the sheet
(l8p_drafts does not read it), and the helper refused: W66's full dry run of set 32, test_l8p.py:665, SystemExit 2.
A module's table holds its own reads (PDFTEXT-INVENTORY.md section 2; W55 declined to put a read in a table whose script does not make
it, because that script's output would then print an input it never reads), so these reads are declared here, apart from the
generators' tables: the record's outputs and its generators are unchanged. The test reads each text through
v2/docs/records/_lib/pdftext.py with this table (PT.declared_in), so the reading no longer depends on the host's poppler, the defect
W34 corrected in the generators (pdftext.py's header). The sheet is held back by its notice (l8p's fetch_held_back.py), so its text is
held back beside it, under held/pdftext/. Re-take after a sheet changes:
    python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l8p
"""
PDFTEXT = {
    "v2/vendor/battery/held/tdk-ptc-limit-sensors-smd-superior-2019-08.pdf": [["-layout"]],
}
