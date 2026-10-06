"""l5r4_pdftext.py: the makers' PDF texts record l5r4's evidence is read from (MESHSAT-1357, W81, 6 October 2026). Declarations only:
nothing here runs.

test_l5r4.t_the_power_on_reading_rests_on_the_held_datasheet reads F-15's sentences from five pages of the RP2040 datasheet. It ran
the host's pdftotext on each page until W81 (6 October 2026); it now reads the committed extraction of each page through
v2/docs/records/_lib/pdftext.py against this table, so the reading no longer depends on the host's poppler (the defect W34 corrected
in the generators, pdftext.py's header). The datasheet is committed, so each page's text and sidecar are committed beside it in
v2/vendor/rp2040/pdftext/. Re-take after the datasheet changes:
    python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l5r4
"""
PDFTEXT = {
    "v2/vendor/rp2040/rpi-rp2040-datasheet.pdf": [["-f", "160", "-l", "160"], ["-f", "164", "-l", "164"], ["-f", "169", "-l", "169"],
                                                  ["-f", "545", "-l", "545"], ["-f", "549", "-l", "549"]],
}
