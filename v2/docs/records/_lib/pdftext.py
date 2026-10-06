#!/usr/bin/env python3
"""pdftext.py: the extracted text of a maker's PDF as a committed verbatim input (MESHSAT-1357, Q-41 item 1, W34, 6 October 2026).

THE DEFECT (a tool/integration defect under the constitution's section 4). The records' generators ran `pdftotext` on the makers'
PDFs WHEN THEY RAN, so a record's output depended on the host's poppler build and data: on 6 October 2026 the JST VH catalogue
(CID Type 0C fonts, Identity-H) extracted to 184 bytes on a box image without the `poppler-data` package against the runner's 39318,
151 tests failed on the first suite box of set 30, and six records had to run on a second box. The outputs pinned the PDFs' digests,
not the text that was actually read.

THE CORRECTION (the coordinator's ruling, authority SESSION). A generator never runs pdftotext. Each one declares, in a module-level
literal `PDFTEXT = {<pdf, repository-relative>: [<pdftotext options>, ...]}`, every extraction it reads; the re-take script
(`retake_pdf_text.py <record dir> [<pdf> ...]`, beside this file) runs the runner's pdftotext once per declared extraction and writes
the text and a sidecar; this module returns that text byte for byte and REFUSES (exit 2, naming the re-take command) when it is
absent. The generator prints each text's sha256 as an input line, beside the PDF's own pin, which it keeps.

WHERE THE TEXT LIVES (a SESSION decision under the owner's standing rule of 26 September 2026, taken against the brief's
`<record>/inputs/pdftext/`; reason and reversal in PDFTEXT-INVENTORY.md, section 3): beside the PDF it was taken from, in a
`pdftext/` folder, named `<pdf stem>.<options tag>.txt`, with the sidecar `<that name>.meta.json` (the PDF's sha256, the text's
sha256 and length, the options, `pdftotext -v`'s first line, the poppler-data version, the date). A held-back PDF's text is itself
held back: it lands under the PDF's `held/` folder, which .gitignore already excludes, because every held sheet's terms (each
record's fetch_held_back.py header) grant no redistribution, and the full text of a sheet is a copy of it. It is refused when absent
exactly as the PDF is, and the route the refusal names is the fetch script that fetches THAT sheet (FETCH below: often another
record's, W36's finding F-P2, restated by W37 on 6 October 2026), then the re-take.

THE INVENTORY (every .py under v2/docs/records/ that mentions pdftotext on the base aed4bd23: 63 files, classified; the table with the
PDFs each reads, committed or held back, and the reasons is PDFTEXT-INVENTORY.md beside this file):
  RUN-TIME EXTRACTION, CONVERTED (25 by W34, 1 by W55; the generator reads the committed text through this module):
    the brief's six records: efuse/efuse_check.py; l5r2/l5r2_interfaces.py; l8r2/l8r2_drafts.py, l8r2_gndret.py, l8r2_p0.py;
    l4e13/l4e13_panel.py (its own pages; the replay it runs still extracts); l4e11/l4e11_power.py; l4e9/l4e9_power_path.py;
    then l4e10/l4e10_cell_thermal.py, l4e12/l4e12_thermal.py, l7pwr/l7pwr_fans_th1.py, l7r2/l7r2_items.py, l8p/l8p_drafts.py,
    l8p/l8p_guard.py, l9pwr/l9pwr_budget.py, l9stk/l9stk_copper.py, l9stk/l9stk_protection.py, l9t5/l9t5_a1.py, l9t5_case.py,
    l9t5_cm5.py, l9t5_drafts.py, l9t5_f01.py, l9t5_paloop.py, l9t5_t10.py, l4e8/ripple_dense.py (its own pages; r11dep still extracts)
    W55 (6 October 2026): l8p/l8p_c4.py, which named no pdftotext at the base but ran it through l8p_guard.pdftext(), so the census
    by name missed it; it now declares and reads its three sheets with its own table (test_pdftext_input's static check finds such
    a read, W53's finding)
  RUN-TIME EXTRACTION, NOT CONVERTED (15): the l4e7 KEY group (l4e7/l4e7_stage_settings.py, l4e/l4e_replay.py, l4e5/
    l4e5_source_control.py, r11dep/r11_dep.py, l3plane/energy_basis.py, l3plane/vbus20_range.py); the accepted Layer 3 records
    (l3batt/tablet.py, l3feas/hf_wab.py, l3feas/solar_interface.py, l3plane/curve_readings.py, l3plane/weather_basis.py); the
    coordinator's checker l4close/verify_risks.py; historical a1elec/gauge_scale.py, rv-dec/dec_mmscan.py, s122/verdicts.py
  FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (8, untouched): d6dec/box/basis_check.py, d6rel/revision_scan.py, d8dec31/ledger_pages.py,
    int16/apply_hold_back_panjit.py, w5identc/scan_vendor.py, w5si/apply/apply_board_c_declarations.py, w5si/tools/cite_fill.py,
    w5si/tools/edge_search.py (retake_pdf_text.py beside this file is the re-take itself)
  DRY-RUN OR TRANSCRIPT, no call of its own (15, untouched): cx1/checks/check-1-phase1.py, d6dec/make_basis_md.py,
    l4e4/l4e4_limits.py and l4e6/l4e6_fault_handling.py (through r11dep), l4e7/l4e7_p0sol.py (a sentence on the re-key host),
    l6pwr/l6pwr_parts.py and l6r2/l6r2_passives.py (through v2/ecad/tools/part_identities.py), l8r2/l8r2_dist.py,
    l9t5/l9t5_connected.py, l9t5/l9t5_f01_drafts.py (through converted modules), r4b/pin_parity.py (a usage line),
    s122/apply_docs_s122_r4.py, s122/judgements.py, w4dp/patch_vendor_index.py, w5identc/build_table.py

Use, from a generator (the records import their siblings by path):
    _sp = importlib.util.spec_from_file_location("records_pdftext", os.path.join(<records dir>, "_lib", "pdftext.py"))
    PT = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(PT)
    text = PT.pdf_text(TOP, "v2/vendor/connectors/jst-vh-catalogue.pdf", ["-layout"], PDFTEXT, "v2/docs/records/l4e11")
Stdlib only. It never runs pdftotext, on any path."""
import hashlib
import json
import os
import sys

RETAKE = "v2/docs/records/_lib/retake_pdf_text.py"
FOLDER = "pdftext"
_SHA = {}

# The held-back sheets the PDFTEXT tables declare, each with the records whose fetch_held_back.py fetches it (W37, 6 October 2026,
# W36's finding F-P2: the refusal named "the record's fetch_held_back.py", the wrong script for 12 reads: efuse and l4e8 have no fetch
# script of their own; l4e12's CSD17577/CSD17578 come from s117's, l4e13's SunPower sheets from a1solar's, l9t5's INA250 from l4e7's,
# l9t5_t10's INA169 and TPS3701 from l4e7's and l6pwr's, l4e8's Uniroyal sheet from w5identc's). Read from each fetch script's own
# document list (parsed, never run); test_pdftext_input re-derives the map from those scripts and refuses a difference. A refusal names
# the reading record's own script when it is listed, else the first. No declared held sheet lacks a fetch route on 6 October 2026; one
# that did would read () here and its refusal would say so (a sheet with no fetch route is a finding, never a silent gap).
FETCH_SCRIPT = "v2/docs/records/%s/fetch_held_back.py"
FETCH = {
    "v2/vendor/adi/held/adi-adl5513-revb.pdf": ("l9t5",),
    "v2/vendor/adi/held/adi-adl5902-revb.pdf": ("l9t5",),
    "v2/vendor/adi/held/adi-ltc5582-revd.pdf": ("l9t5",),
    "v2/vendor/battery/held/lg-inr18650hg2-rev0-2014.pdf": ("l4e10",),
    "v2/vendor/battery/held/saft-lsh20-31015-2-0426.pdf": ("l4e10",),
    "v2/vendor/battery/held/saft-mp176065xtd-31109-2-0625.pdf": ("l4e10", "l6pwr"),
    "v2/vendor/battery/held/samsung-inr18650-30q-v1.0-2015.pdf": ("l4e10",),
    "v2/vendor/battery/held/samsung-inr18650-30q6-draft-v0.1-2024.pdf": ("l4e10",),
    "v2/vendor/battery/held/samsung-inr18650-30q6-v1.0-2020.pdf": ("l4e10",),
    "v2/vendor/battery/held/tdk-ptc-limit-sensors-smd-superior-2019-08.pdf": ("l8p",),   # W81: l8p_drafts' table (test_l8p's read)
    "v2/vendor/nexperia/held/nexperia-an11158-rev7.pdf": ("l4e11",),
    "v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf": ("l4e11", "l6pwr"),
    "v2/vendor/nexperia/held/nexperia-pxp9r1-30ql.pdf": ("l4e11",),
    "v2/vendor/passives/held/moolee-hollr2512-ho-a0-2022-01-06.pdf": ("l4e11",),
    "v2/vendor/passives/held/murata-grm3195c1h104ga05-01a-2026-06-11.pdf": ("l4e11",),
    "v2/vendor/passives/held/murata-grm3195c1h683ja05-01a-2026-06-11.pdf": ("l4e11",),
    "v2/vendor/passives/held/uniroyal-series-11cd644d.pdf": ("w5identc",),
    "v2/vendor/power/held/adi-ltc3115-1-rev-e.pdf": ("l4e11",),
    "v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf": ("l4e11",),
    "v2/vendor/power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf": ("l4e11", "l6pwr"),
    "v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf": ("l4e11", "l4e9"),
    "v2/vendor/power/held/vishay-sqj403ep-67109-reva.pdf": ("l4e11",),
    "v2/vendor/power/held/vishay-sqj407ep-62806-revb.pdf": ("l4e11",),
    "v2/vendor/solar/held/solbian-sx-series-datasheet-eng-2023-02.pdf": ("l4e13",),
    "v2/vendor/solar/held/sunpower-flex-safety-installation-524958-revf.pdf": ("a1solar",),
    "v2/vendor/solar/held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf": ("a1solar",),
    "v2/vendor/ti/held/ti-bq25730-sluse65a.pdf": ("l4e11", "l6pwr"),
    "v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf": ("s117",),
    "v2/vendor/ti/held/ti-csd17578q5a-slps526.pdf": ("s117",),
    "v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf": ("l4e11", "l6pwr"),
    "v2/vendor/ti/held/ti-ina169-sbos181f.pdf": ("l4e7", "l6pwr"),
    "v2/vendor/ti/held/ti-ina250-sbos511c.pdf": ("l4e7",),
    "v2/vendor/ti/held/ti-lm26lv-snis144g.pdf": ("l8p",),
    "v2/vendor/ti/held/ti-lmh2110-snws022d.pdf": ("l9t5",),
    "v2/vendor/ti/held/ti-opa187-sbos807e.pdf": ("l8p",),
    "v2/vendor/ti/held/ti-slva673a.pdf": ("l9stk",),
    "v2/vendor/ti/held/ti-spra953c-thermal-metrics.pdf": ("l4e11",),
    "v2/vendor/ti/held/ti-tlv755p-c404027.pdf": ("l4e12",),
    "v2/vendor/ti/held/ti-tps1663-slvset9g.pdf": ("l4e11", "l6pwr"),
    "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf": ("l4e7", "l6pwr"),
    "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf": ("l4e11", "l4e7", "l6pwr", "l8r2"),
    "v2/vendor/ti/held/ti-tps55340-slvsbd4e.pdf": ("l4e11",),
    "v2/vendor/ti/held/ti-tps63070-slvsc58b.pdf": ("l4e11",),
    "v2/vendor/ti/held/ti-tps709-sbvs186h.pdf": ("l8p",),
}


def refuse(msg):
    sys.stderr.write("pdftext: %s; refusing\n" % msg)
    sys.exit(2)


def canon(options):
    """(mode, first, last) of a pdftotext option list, mode "layout" (-layout), "raw" (-raw) or "plain" (neither: pdftotext's
    reading order); an option this module does not know is refused, never guessed."""
    mode, first, last = "plain", None, None
    o = list(options)
    i = 0
    while i < len(o):
        a = str(o[i])
        if a in ("-layout", "-raw"):
            if mode != "plain":
                refuse("the pdftotext options %s name two text modes" % " ".join(map(str, o)))
            mode = a[1:]
            i += 1
        elif a in ("-f", "-l") and i + 1 < len(o) and str(o[i + 1]).isdigit():
            if a == "-f":
                first = int(o[i + 1])
            else:
                last = int(o[i + 1])
            i += 2
        else:
            refuse("the pdftotext option %r is not one this module knows (-layout, -raw, -f N, -l N)" % a)
    return mode, first, last


def run_args(options):
    """The options in the one order the re-take script runs them (pdftotext's output does not depend on the order)."""
    mode, first, last = canon(options)
    return (["-" + mode] if mode != "plain" else []) + (["-f", str(first)] if first else []) + (["-l", str(last)] if last else [])


def tag(options):
    """layout / raw / plain, then .pN for one page, .fN / .lN for a range end: the name part that keeps two extractions apart."""
    t, first, last = canon(options)
    if first and last and first == last:
        return t + ".p%d" % first
    return t + (".f%d" % first if first else "") + (".l%d" % last if last else "")


def held(pdf_rel):
    return "/held/" in "/" + pdf_rel.replace(os.sep, "/")


def text_path(pdf_rel, options):
    """The extraction's repository-relative path: beside the PDF, in pdftext/ (under held/ when the PDF is held back)."""
    d, b = os.path.split(pdf_rel)
    return "/".join(x for x in (d, FOLDER, "%s.%s.txt" % (os.path.splitext(b)[0], tag(options))) if x)


def meta_path(txt_rel):
    return txt_rel + ".meta.json"


def retake_command(record):
    return "python3 %s %s" % (RETAKE, record or "<record dir>")


def fetch_route(pdf_rel, record=None):
    """The words that name how a held-back sheet is fetched: the fetch script FETCH lists for it (the reading record's own when listed),
    or, for a sheet no script fetches, that finding."""
    recs = FETCH.get(str(pdf_rel).replace(os.sep, "/"), ())
    if not recs:
        return ("no record's fetch_held_back.py fetches the held-back sheet %s (a sheet with no fetch route is a finding: add it, with "
                "the address and sha256 v2/vendor/sources.txt records, to a fetch script and to pdftext.FETCH)" % pdf_rel)
    own = os.path.basename(os.path.normpath(record)) if record else None
    return "fetch the held-back sheet with python3 %s" % (FETCH_SCRIPT % (own if own in recs else recs[0]))


def _sha_file(p):
    st = os.stat(p)
    k = (p, st.st_size, st.st_mtime_ns)
    if k not in _SHA:
        _SHA[k] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return _SHA[k]


def read_pdf_text(pdf_path, txt_path, retake=None, universal_newlines=False, record=None):
    """The text at txt_path, as pdftotext wrote it at the re-take (decoded UTF-8, errors replaced, as the generators decoded their
    pipe). Refuses (exit 2) when the text or its sidecar is absent, when the text is not the bytes the sidecar records, or when the PDF
    is present and is not the file the text was taken from. universal_newlines=True gives what subprocess's text=True gave. A held-back
    sheet's route names the fetch script FETCH lists for it (fetch_route; record, when given, prefers the reader's own)."""
    route = retake or retake_command(None)
    if held(_rel(pdf_path)):
        route = "%s, then %s" % (fetch_route(_rel(pdf_path), record), route)
    if not os.path.isfile(txt_path):
        refuse("the extracted text %s of %s is absent; take it with: %s" % (_rel(txt_path), _rel(pdf_path), route))
    mp = txt_path + ".meta.json"
    if not os.path.isfile(mp):
        refuse("the sidecar %s is absent; take the text again with: %s" % (_rel(mp), route))
    try:
        meta = json.load(open(mp, encoding="utf-8"))
    except ValueError as e:
        refuse("the sidecar %s does not parse (%s)" % (_rel(mp), e))
    data = open(txt_path, "rb").read()
    if hashlib.sha256(data).hexdigest() != meta.get("text_sha256"):
        refuse("%s is not the text its sidecar records (changed after the re-take); take it again with: %s" % (_rel(txt_path), route))
    if os.path.isfile(pdf_path) and _sha_file(pdf_path) != meta.get("pdf_sha256"):
        refuse("%s was taken from another file than the present %s; take it again with: %s" % (_rel(txt_path), _rel(pdf_path), route))
    t = data.decode("utf-8", "replace")
    if universal_newlines:
        t = t.replace("\r\n", "\n").replace("\r", "\n")
    return t


def _declared(declared, pdf_rel, options):
    want = tag(options)
    return any(tag(o) == want for o in (declared or {}).get(pdf_rel, ()))


def pdf_text(top, pdf_rel, options, declared, record, universal_newlines=False):
    """The committed extraction of pdf_rel under options, which the record's PDFTEXT table must declare (so the re-take takes it)."""
    if not _declared(declared, pdf_rel, options):
        refuse("%s with %s is not declared in %s's PDFTEXT table; declare it, then %s" % (
            pdf_rel, " ".join(map(str, options)) or "(no options)", record, retake_command(record)))
    return read_pdf_text(os.path.join(top, pdf_rel), os.path.join(top, text_path(pdf_rel, options)), retake_command(record),
                         universal_newlines, record)


def inputs(top, declared):
    """[(text path, its sha256 or None when absent, held back?)] for every declared extraction, sorted by path: the input lines."""
    rows = []
    for pdf_rel in sorted(declared or {}):
        for o in declared[pdf_rel]:
            t = text_path(pdf_rel, o)
            p = os.path.join(top, t)
            rows.append((t, hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None, held(pdf_rel)))
    return sorted(set(rows))


def merge(*tables):
    """One PDFTEXT table from several (a script that reads through a module it imports prints that module's texts with its own)."""
    out = {}
    for t in tables:
        for pdf, opts in (t or {}).items():
            for o in opts:
                if tag(o) not in {tag(x) for x in out.get(pdf, [])}:
                    out.setdefault(pdf, []).append(list(o))
    return out


def declared_in(path):
    """The module-level PDFTEXT literal of the script at path, read with ast (the script is not imported); {} when it has none."""
    import ast
    for node in ast.parse(open(path, encoding="utf-8").read(), path).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PDFTEXT" for t in node.targets):
            return ast.literal_eval(node.value)
    return {}


def _rel(p):
    """A path as the messages print it: repository-relative where it can be (no host path reaches an output)."""
    p = os.path.abspath(p)
    parts = p.replace(os.sep, "/").split("/")
    return "/".join(parts[parts.index("v2"):]) if "v2" in parts else os.path.basename(p)
