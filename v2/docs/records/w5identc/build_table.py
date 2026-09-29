#!/usr/bin/env python3
"""build_table.py: write board C's part identity table (MESHSAT-1357, stream w5identc, 29 September 2026).

Reads board C's selections from the committed netlist with tools/part_identities.py, takes each selection's identity
from stream w5ident's table where the selection's key is unchanged (w5ident-board-c-identities.json, extracted from
fnd/w5ident c08f4d5a) or from this stream's own decisions below (DECISIONS, keyed by selection id), and then applies
RULE D-2 to every identity that claims a document: this script READS the document's text layer page by page
(part_identities.find_pages) and binds the first page that prints the part number. A document that prints it on no
page is not bound, and the selection is UNRESOLVED (DOCUMENT_DOES_NOT_NAME_THE_PART) with what was read. Nothing is
taken from w5ident's word: its RESOLVED selections are re-read here.

It refuses (and writes nothing) when a selection has neither a carried identity nor a decision, when a decision names
an id that is not a selection, or when a document's sha256 is not the one recorded.

Usage: build_table.py [--out TABLE]   (default v2/ecad/tools/pcb_part_identities.yaml)"""
import collections, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(REPO, "v2", "ecad", "tools")
sys.path.insert(0, TOOLS)
import part_identities as PI          # noqa: E402
from verdict import opt               # noqa: E402

CARRIED = os.path.join(HERE, "w5ident-board-c-identities.json")
W5IDENT = "c08f4d5a1330be8ec5253192a7d36c5f94b3e025"   # fnd/w5ident, the commit its three checks read
DATE = "29 September 2026"
TAKEN = "MESHSAT-1357 stream w5identc, %s, on main b874b744 (set 13)" % DATE
SESSION = ("SESSION, under the owner's standing rule of 26 September 2026 (engineering decisions are the session's); "
           "reverse by editing DECISIONS in v2/docs/records/w5identc/build_table.py and re-running it")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# This stream's own decisions: the selections board C gained or changed since w5ident's table (set 7's R50 and R51,
# set 12's R52 and D23, set 13's R53 to R56 which join an existing 27R selection, R14's value, and C28's requirement
# now that EPD_VCC is declared), and the documents this stream fetched. Each identity that claims a document names its
# path and the sha256 read when it was fetched; the page is found by rule D-2, never typed.
DECISIONS = {
    "S-479b8ebac6": dict(  # d:D23, set 12
        status="RESOLVED", maker="Diodes Incorporated", mpn="BAT46W-7-F",
        datasheet=dict(path="v2/vendor/diodes/diodes-bat46w.pdf"),
        chosen_by="the part the generator's value names (BAT46W-7-F) and its order code C83152; the document is the one "
                  "SOURCES.yaml entry buck-boost-bootstrap-diodes already holds for this part number",
        order_code=dict(code="C83152", route="the generator's LCSC field")),
    "S-d499541fe0": dict(  # c:R50, 10k 1%
        status="UNRESOLVED", reason_class="DOCUMENT_OWED", maker="UNI-ROYAL (Uniroyal Electronics)", mpn="0603WAF1002T5E",
        reason="the generator's order code C25804 is Uniroyal 0603WAF1002T5E by stream w5ident's catalogue reading of 27 "
               "September 2026 (its selection S-d499541fe0 on boards A, B and E, the same key); the only Uniroyal "
               "document either stream holds for it is the thick film series sheet w5ident filed, whose text layer prints "
               "no complete part number (read by this stream on all 9 pages: an ordering scheme, not the part)",
        next_action="file a Uniroyal document that prints 0603WAF1002T5E (a part specification or a certificate of "
                    "conformance), or take a 10 kOhm 1 percent 0603 part whose maker prints its part number",
        order_code=dict(code="C25804", route="the generator's LCSC field")),
    "S-bf6f910c86": dict(  # c:R14, 2.2k 1% since set 12
        status="UNRESOLVED", reason_class="DOCUMENT_OWED", maker="UNI-ROYAL (Uniroyal Electronics)", mpn="0603WAF2201T5E",
        reason="the generator's order code C4190 is Uniroyal 0603WAF2201T5E by stream w5ident's catalogue reading of 27 "
               "September 2026 (its selection S-099e530a08); no held document prints that part number (the series sheet "
               "w5ident filed prints none)",
        next_action="file a Uniroyal document that prints 0603WAF2201T5E, or take a 2.2 kOhm 1 percent 0603 part whose "
                    "maker prints its part number",
        order_code=dict(code="C4190", route="the generator's LCSC field")),
    "S-f8c96deae3": dict(  # c:R52, 330R 1%, set 12
        status="UNRESOLVED", reason_class="DOCUMENT_OWED", maker="UNI-ROYAL (Uniroyal Electronics)", mpn="0603WAF3300T5E",
        reason="the generator's order code C23138 is Uniroyal 0603WAF3300T5E by stream w5ident's catalogue reading of 27 "
               "September 2026 (its selection S-c62c375c58 on board B); no held document prints that part number",
        next_action="file a Uniroyal document that prints 0603WAF3300T5E, or take a 330 Ohm 1 percent 0603 part whose "
                    "maker prints its part number",
        order_code=dict(code="C23138", route="the generator's LCSC field")),
    "S-5ae2e5c268": dict(  # c:C28 (4.7u 0805 on EPD_VCC), whose voltage was open in w5ident's table (S-4fb1ca0365)
        status="UNRESOLVED", reason_class="CHOICE_OWED",
        reason="w5ident left this capacitor UNRESOLVED because EPD_VCC was undeclared; board C's intent now declares "
               "EPD_VCC at 3.3 V (a rail), so the requirement is known (4.7 uF, 0805, X7R by rule C-D3, at least 6.3 V at "
               "the 20 percent margin, 10 percent) and no part has been chosen for it by either stream",
        next_action="choose a 4.7 uF X7R 0805 part of at least 6.3 V whose maker prints its part number, file that "
                    "document, and give the row an order code"),
}


# Documents the tree already held for a part number w5ident left without one (its SOURCES join did not reach them):
# found by this stream by reading every PDF of 21 vendor folders for each owed part number (LOG.md, 29 September
# 2026). Each is bound only if the builder's own page-by-page reading finds the part number (rule D-2). The Raspberry
# Pi RP2040 documents also print ABM8-272-T3, as their recommended crystal; they are not Abracon's and are not bound.
HELD = {
    "S-55e88b2fbd": "v2/vendor/power/aos-ao3401a-p-mosfet.pdf",
    "S-cae89bf0ce": "v2/vendor/power/aos-ao3401a-p-mosfet.pdf",
    "S-8362226c90": "v2/vendor/vishay/veml7700-datasheet.pdf",
    "S-3da103208a": "v2/vendor/power/ti-tlv755p-ldo.pdf",
    "S-dfbcfc88f2": "v2/vendor/winbond/winbond-w25q16jv-serial-flash.pdf",
}


# A maker's name as its own sheet prints it, where w5ident's catalogue reading spelt it otherwise (w5ident's second check,
# identity lens, minor: page 1 of v2/vendor/power/jscj-2n7002-c8545.pdf reads "JIANGSU CHANGJIANG ELECTRONICS
# TECHNOLOGY CO.", read by this stream with pdftotext on 29 September 2026).
MAKER_AS_PRINTED = {"S-b9d2bcde2e": "Jiangsu Changjiang Electronics Technology Co., Ltd."}


# DECODED bindings (the session's decision of 29 September 2026, drafted by apply_decision_decoded.py): the maker's own
# ordering-code table decodes the part number field by field. Each spec names the document, the page of the table, the
# maker's mark and publisher, and for each field of the part number the row of that page that states it (as the text
# layer prints it, whitespace collapsed) and the meaning the row gives the code. part_identities.read_binding asserts
# every row against the page and every decoded property against the selection; nothing here is taken on trust.
YAGEO_SCHEME = "CC XXXX X X X7R X BB XXX"
YAGEO_ROWS = {
    "size": {"0402": "0402 (1005)", "0603": "0603 (1608)", "0805": "0805 (2012)", "1206": "1206 (3216)"},
    "tolerance": {"J": ("J = ± 5%", "± 5%"), "K": ("K = ± 10%", "± 10%"), "M": ("M = ± 20%", "± 20%")},
    "packaging": {"R": ("R = Paper/PE taping reel; Reel 7 inch", "Paper/PE taping reel"),
                  "K": ("K = Blister taping reel; Reel 7 inch", "Blister taping reel")},
    "voltage": {"5": ("5 = 6.3 V", "6.3 V"), "6": ("6 = 10 V", "10 V"), "7": ("7 = 16 V", "16 V"),
                "8": ("8 = 25 V", "25 V"), "9": ("9 = 50 V", "50 V")},
}
UNIROYAL_ROWS = {
    "size": "1st~4th codes: Part name. E.g.: 01005, 0201, 0402, 0603, 0805, 1206 ,1210, 2010,1812, 2512.",
    "power": ("E.g.: WA=1/10W W4=1/4W", "1/10W"),
    "tolerance": ("7th code: Tolerance. E.g.: D=±0.5% F=±1% G=±2% J=±5%", "±1%"),
    "value": "2.4.2 If value belongs to standard value of ≤2% series, 8th~10th codes are significant figures of the "
             "resistance, and 11th code is the power of ten.",
    "power_of_ten": "0=100 1=101 2=102 3=103 4=104 5=105 6=106 J=10-1 K=10-2 L=10-3 M=10-4 N=10-5 P=10-6",
    "packaging": ("12th code: Packaging Type. E.g.: C=Bulk T=Tape/Reel", "Tape/Reel"),
    "quantity": ("4=4000pcs 5=5000pcs C=10000pcs D=20000pcs E=15000pcs", "5000pcs"),
    "special": ("E = Environmental Protection, Lead Free, or Standard type.", "Environmental Protection"),
}


def decode_spec(mpn):
    """The DECODED binding this stream drafts for a part number, or None when no maker's table is read for its series."""
    import re
    m = re.match(r"^CC(\d{4})([JKM])([RK])(X7R)([5-9])(BB)(\d{3})$", mpn)
    if m:
        size, tol, pack, diel, volt, proc, val = m.groups()
        if size not in YAGEO_ROWS["size"]: return None
        return dict(binding="DECODED", scheme="yageo-cc-x7r-v26-p2", path="v2/vendor/passives/yageo-cc-series.pdf", page=2,
                    publisher="YAGEO", table="YAGEO product specification, Surface-Mount Ceramic Multilayer Capacitors, "
                    "General Purpose & High Cap., X7R 6.3 V to 250 V, V.26 of 19 November 2024: ORDERING INFORMATION, "
                    "GLOBAL PART NUMBER",
                    fields=[dict(field="series", code="CC"),
                            dict(field="size", code=size, row=YAGEO_ROWS["size"][size]),
                            dict(field="tolerance", code=tol, row=YAGEO_ROWS["tolerance"][tol][0], means=YAGEO_ROWS["tolerance"][tol][1]),
                            dict(field="packaging", code=pack, row=YAGEO_ROWS["packaging"][pack][0], means=YAGEO_ROWS["packaging"][pack][1]),
                            dict(field="dielectric", code=diel),
                            dict(field="voltage", code=volt, row=YAGEO_ROWS["voltage"][volt][0], means=YAGEO_ROWS["voltage"][volt][1]),
                            dict(field="process", code=proc),
                            dict(field="value", code=val, rule="pf_2sig", row="2 significant digits+number of zeros")])
    m = re.match(r"^(0603)(WA)(F)(\d{3}[0-9J])(T)(5)(E)$", mpn)
    if m:
        size, pw, tol, val, pack, qty, sp = m.groups()
        U = UNIROYAL_ROWS
        return dict(binding="DECODED", scheme="uniroyal-thick-film-p2", path="v2/vendor/passives/held/uniroyal-series-11cd644d.pdf",
                    page=2, publisher="UNI-ROYAL (Uniroyal Electronics Global Co., Ltd.)", held_back=True,
                    fetch="v2/docs/records/w5identc/fetch_held_back.py",
                    table="Uniroyal Thick Film Chip Resistors data sheet, section 2, Explanation of Part No. System",
                    fields=[dict(field="size", code=size, row=U["size"]),
                            dict(field="power", code=pw, row=U["power"][0], means=U["power"][1]),
                            dict(field="tolerance", code=tol, row=U["tolerance"][0], means=U["tolerance"][1]),
                            dict(field="value", code=val, rule="ohm_3sig", row=U["value"], means_row=U["power_of_ten"]),
                            dict(field="packaging", code=pack, row=U["packaging"][0], means=U["packaging"][1]),
                            dict(field="quantity", code=qty, row=U["quantity"][0], means=U["quantity"][1]),
                            dict(field="special", code=sp, row=U["special"][0], means=U["special"][1])])
    return None


def try_decode(ident, req, sid, log, kind=None):
    """(datasheet, None) when the maker's table decodes the part for this selection, else (None, why)."""
    ds = decode_spec(ident.get("mpn") or "")
    if ds is None: return None, None
    full = os.path.join(REPO, ds["path"])
    if not os.path.exists(full):
        raise SystemExit("build_table: %s is held back and not fetched: run %s first" % (ds["path"], ds.get("fetch")))
    ds["sha256"] = sha(full)
    r = PI.read_binding(ds, ident["mpn"], maker=ident.get("maker"), req=req, kind=kind)
    log.append(dict(selection=sid, mpn=ident["mpn"], document=ds["path"], binding="DECODED", page=ds["page"],
                    sha256=ds["sha256"], state=r["state"], why=r["why"], not_established=r.get("not_established")))
    if r["state"] == "DECODED":
        ds["established"] = r.get("established"); ds["not_established"] = r.get("not_established") or []
        return ds, None
    return None, "%s page %d, DECODED binding refused: %s" % (ds["path"], ds["page"], r["why"])


def rules(w5):
    """w5ident's rules, carried, with V-1 amended and D-2 added by this stream; the resolver's own rules (D-1, M-1, I-1,
    I-2, F-2) are carried as the rules the carried identities were chosen under, and this stream ran no resolver."""
    out = []
    for r in w5:
        r = dict(r)
        if r["id"] == "V-1":
            r["rule"] += (". AMENDED by stream w5identc (%s), answering w5ident's second check W5I-C2-B1: (a') a net the "
                          "intent marks as a return, or declares with a maximum of at most 0.5 V (board P's PACK_N at 0.05 V), "
                          "is a floor and never a ceiling; (g) a connector's pin is set on its far side, so a connector is a "
                          "source of unknown level for an undeclared net unless its value names a passive far end (a button, "
                          "a reed switch, a thermistor)" % DATE)
            r["why"] += "; the second check found PACK_N bounding six SMBus nets at 0.05 V and connectors read as active parts"
        if r["id"] in ("D-1", "M-1", "I-1", "I-2", "F-2"):
            r["scope_note"] = ("a rule of w5ident's resolver: the carried identities were chosen under it; stream w5identc ran no "
                               "resolver and asked no catalogue")
        out.append(r)
    out.append(dict(
        id="D-2",
        rule=("A RESOLVED selection names a maker, a manufacturer part number and a held maker's document with a page, "
              "bound one of two ways (decision 59, the session's, 29 September 2026). PRINTED: the page's text layer prints "
              "the part number, letter case aside (the characters on either side are not letters or digits); where the "
              "part number carries the maker's packing code, the page may print it as the maker's placeholder (Hirose's "
              "FH34SRJ-24S-0.5SH(##)) if the same page keys the placeholder to that code (\"(##) : (50)\"); a part number "
              "that carries no packing code (SS2040FL) is printed as it is, the reel being the order code's business; "
              "and the part must be the one the design names: the value text names it (less its packing code or a reel "
              "suffix) or the netlist's order code reads as it in this tree's catalogue reading. "
              "DECODED: the page is the maker's own ordering-code table for a scheme written in part_identities.SCHEMES "
              "(the document pinned by sha256), the tool reads the layout from the page, slices the whole part number by "
              "it, reads each code's meaning in its own part of the page and requires every deciding property of the kind "
              "(capacitor: value, package, tolerance, rated voltage, dielectric, construction; resistor: value, package, "
              "tolerance, power) to meet the selection's requirements as the check derives them from the netlist. A "
              "DECODED binding is counted apart and never as PRINTED. LIMIT: it shows what the part number means in the "
              "maker's scheme, not that the maker makes that value at that rating (the range table). A document held back "
              "from the public tree is cited by address and sha256 and read where it is fetched"),
        why=("w5ident's second check, ID-B1 to ID-B3: selections were RESOLVED on documents that do not name the part; "
             "round 3's check of this stream, B1 and B2: the check judged on the table's own requirements, and the first "
             "DECODED reader accepted permutations and padding"),
        reversal=("decision 59's reversed_by (pcb_decisions.yaml); a range-table citation added as a second requirement of a "
                  "DECODED binding would narrow it"),
        authority=SESSION))
    return out


def classify(ident):
    """The reason class of an identity w5ident left UNRESOLVED, from its own reason text (its words are carried)."""
    r = (ident.get("reason") or "").lower()
    if "unbounded" in r or "voltage this capacitor must be rated for is not known" in r: return "REQUIREMENT_OPEN"
    if "inferred" in r: return "PART_NUMBER_INFERRED"
    return "CHOICE_OWED"


def resolve_document(ident, sel_id, log):
    """Rule D-2 on an identity that claims a document: bind the first page that prints the part number."""
    ds = dict(ident.get("datasheet") or {})
    path, mpn = ds.get("path"), ident.get("mpn")
    full = os.path.join(REPO, path)
    where = "this tree"
    if not os.path.exists(full):
        # a document w5ident filed on its branch and never merged: read it from that commit, into a scratch file, so
        # the reason says what was read (it is not brought into this tree unless it names the part)
        import subprocess, tempfile
        data = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (W5IDENT, path)], capture_output=True).stdout
        if not data:
            return None, "the document %s is not in this tree and could not be read from %s" % (path, W5IDENT[:8])
        full = os.path.join(tempfile.mkdtemp(prefix="w5identc-"), os.path.basename(path))
        open(full, "wb").write(data)
        where = "fnd/w5ident %s (not in this tree)" % W5IDENT[:8]
    got = sha(full)
    if ds.get("sha256") and ds["sha256"] != got:
        raise SystemExit("build_table: %s: %s reads sha256 %s, the identity recorded %s" % (sel_id, path, got[:16], ds["sha256"][:16]))
    pages = PI.find_pages(full, mpn, limit=1)
    n = PI.page_count(full)
    log.append(dict(selection=sel_id, mpn=mpn, document=path, read_from=where, sha256=got, pages=n, first_page_naming_it=pages[0] if pages else None))
    if not pages:
        return None, ("%s (read from %s, sha256 %s, %d pages) prints %s on none of its pages (read page by page by this "
                      "stream, rule D-2)" % (path, where, got[:16], n, mpn))
    if where != "this tree":
        return None, "%s names it on page %d but is not in this tree (read from %s); file it first" % (path, pages[0], where)
    ok, line = PI.names_part(PI.page_text(full, pages[0]), mpn)
    return dict(path=path, sha256=got, page=pages[0], names=line, joined_by=ds.get("joined_by") or "this stream"), None


# ------------------------------------------------------------------------------------------------ round 3: re-read
# Every UNRESOLVED reason re-read against the tree (round 3's check, B5). A reason names only facts this builder reads:
# the netlist's own value (`value_has`), a held document's page (`on_page`), the vendor scan (`scan_vendor.py`'s reading),
# a line of a tree file (`file_has`). Each fact is ASSERTED here; a fact that stops holding stops the build.
SCAN = os.path.join(HERE, "readings", "vendor-scan-unresolved.json")
LCSC_READING = os.path.join(REPO, "v2", "docs", "parts", "readings", "lcsc-2026-09-27.json")


def on_page(path, page, phrase):
    """Assert a held document prints `phrase` on `page` (text layer, whitespace collapsed); return the page."""
    txt = PI._flat(PI.page_text(os.path.join(REPO, path), page))
    if PI._flat(phrase) not in txt:
        raise SystemExit("build_table: %s page %d does not print %r" % (path, page, phrase))
    return page


def page_with(path, phrase):
    for pg in range(1, PI.page_count(os.path.join(REPO, path)) + 1):
        if PI._flat(phrase) in PI._flat(PI.page_text(os.path.join(REPO, path), pg)): return pg
    raise SystemExit("build_table: %s prints %r on no page" % (path, phrase))


def line_of(path, start):
    """(line number, text) of the one line of a tree file that begins with `start` (whitespace aside)."""
    hits = [(i + 1, l) for i, l in enumerate(open(os.path.join(REPO, path), encoding="utf-8").read().splitlines())
            if l.strip().startswith(start)]
    if len(hits) != 1: raise SystemExit("build_table: %s has %d lines beginning %r" % (path, len(hits), start))
    return hits[0]


def file_has(path, phrase):
    if phrase not in open(os.path.join(REPO, path), encoding="utf-8").read():
        raise SystemExit("build_table: %s does not carry %r" % (path, phrase))
    return path


def value_has(s, *phrases):
    for v in s["values"]:
        for ph in phrases:
            if ph not in v: raise SystemExit("build_table: a value of %s does not say %r" % (sorted(s["rows"])[0], ph))
    return True


def scan_hits(scan, mpn):
    return scan["part_numbers"].get(mpn)


def scanned(scan, mpn):
    h = scan_hits(scan, mpn)
    if h is None: raise SystemExit("build_table: the vendor scan did not search %s; re-run scan_vendor.py" % mpn)
    return h


def scan_words(scan):
    return "scan_vendor.py read %d PDFs under v2/vendor by their text layer (%d have none)" % (scan["pdfs_read"], len(scan["pdfs_without_text"]))


def reread(sid, s, ident, scan):
    """The re-read identity of one selection (a dict of the fields to set), or None where the carried one stands."""
    rows = sorted(s["rows"])
    land = sorted(s["lands"])[0]
    if land == "LED_D3.0mm":                       # the seventeen panel lamps
        value_has(s, "3 mm", "sunlight viewable")
        file_has("v2/docs/ASSEMBLY.md", "Light guides, 17 x | Mentor 1282.5004")
        return dict(status="UNRESOLVED", reason_class="CHOICE_OWED",
                    reason="the netlist's value names a 3 mm lamp by its colour and 'sunlight viewable' and no part number, "
                           "luminous intensity or viewing angle (%r); each lamp shines through one of the 17 Mentor 1282.5004 "
                           "light guides ASSEMBLY.md names, so the intensity needed at the face is a requirement nobody has "
                           "stated" % sorted(s["values"])[0],
                    next_action="the board C author states each lamp's minimum intensity and viewing angle through the light "
                                "guide (or names the part); a part is then chosen and its maker's document filed")
    if sid == "S-a5c3762a4c":                       # BZ1
        value_has(s, "two flying leads", "Floyd Bell MC-09-530-Q class")
        doc = "v2/vendor/seals/floydbell-mc-09-530-q-spec.pdf"
        on_page(doc, 1, "MC-09-530-Q"); on_page(doc, 1, "Quick Connect Blades")
        return dict(status="UNRESOLVED", reason_class="CHOICE_OWED", maker="Floyd Bell", mpn="MC-09-530-Q",
                    reason="the netlist's value names Floyd Bell MC-09-530-Q as a class and asks two flying leads; Floyd Bell's "
                           "own sheet is held (%s, page 1 prints MC-09-530-Q) and gives its termination as Quick Connect "
                           "Blades (page 1), not flying leads, so the named part does not meet the value as written" % doc,
                    next_action="the board C author either accepts the blades (a lead with receptacles to the board's two "
                                "lands) and names MC-09-530-Q in the value, which then resolves PRINTED on page 1, or names a "
                                "flying-lead part and files its sheet")
    if sid == "S-13d7058c0e":                       # J_EPD
        doc = "v2/vendor/hirose/hirose-fh34-series-ffc-connectors.pdf"
        on_page(doc, 6, "FH34SRJ-24S-0.5SH(##)"); on_page(doc, 6, "(##) : (50)"); on_page(doc, 5, "(50): Standard")
        return dict(status="RESOLVED", maker="Hirose Electric", mpn="FH34SRJ-24S-0.5SH(50)",
                    datasheet=dict(path=doc, page=6, packing=dict(placeholder="(##)", code="(50)", key_row="(##) : (50)",
                                                                 means_page=5, means_row="(50): Standard"),
                                   joined_by="this stream: Hirose's FH34 catalogue, held (round 3's check, B5 item 1)"))
    if sid == "S-62ab53c6e1":                       # C31
        file_has("v2/ecad/tools/gen_sch_c.py", "# GRM188R61E475KE11D (0603, X5R, 4.7 uF, DC 25 V")
        if s["requirements"].get("dielectric") != "X7R": raise SystemExit("build_table: C31's requirement is no longer X7R")
        return dict(status="UNRESOLVED", reason_class="PART_DOES_NOT_MEET_THE_REQUIREMENT", maker="Murata", mpn="GRM188R61E475KE11D",
                    reason="the generator names GRM188R61E475KE11D in its comment (gen_sch_c.py: '0603, X5R, 4.7 uF, DC 25 V'); "
                           "the value '4.7u 25V' states no dielectric, so rule C-D3 asks X7R and an X5R part does not meet "
                           "it; and no PDF under v2/vendor prints the part number (%s)" % scan_words(scan),
                    next_action="either state X5R in the value with the hot-spot reasoning rule C-D3b asks (the part sits on "
                                "the e-paper pump), or choose an X7R 4.7 uF 25 V 0603 whose maker's document prints or "
                                "decodes it")
    sheets = {"S-0a37bce91a": ("v2/vendor/switches/ck-atp19-series-datasheet.pdf", "ATP19 - x - xx - x - xx - xx - x - x - xx - x"),
              "S-ff16699f19": ("v2/vendor/switches/ck-atp16-series-datasheet.pdf", "To order, simply select desired option from each category"),
              "S-b2e775c075": ("v2/vendor/switches/ck-atp16-series-datasheet.pdf", "To order, simply select desired option from each category"),
              "S-722b702520": ("v2/vendor/switches/nkk-m-series-toggles-datasheet.pdf", "ORDERING EXAMPLE")}
    if sid in sheets:
        doc, anchor = sheets[sid]
        pg = page_with(doc, anchor)
        value_has(s, ident["mpn"])
        if scanned(scan, ident["mpn"]): raise SystemExit("build_table: %s is printed somewhere now; bind it" % ident["mpn"])
        return dict(status="UNRESOLVED", reason_class="DOCUMENT_DOES_NOT_NAME_THE_PART",
                    reason="the netlist's value names %s; the maker's series sheet is held (%s, its ordering scheme on page "
                           "%d: %r) and prints no complete part number, and no PDF under v2/vendor prints %s (%s). Decision "
                           "59's DECODED schemes are written for capacitors and resistors only, so a switch's ordering scheme "
                           "is not decoded" % (ident["mpn"], doc, pg, anchor, ident["mpn"], scan_words(scan)),
                    next_action="a DECODED scheme for this switch series (each category of page %d aligned to the value's "
                                "words: size, function, ring colour), which widens decision 59 beyond capacitors and "
                                "resistors, or a %s document that prints %s" % (pg, ident.get("maker"), ident["mpn"]))
    if land == "PanelJack_17mm":                   # the two U-174/U headset jacks
        value_has(s, "U-174/U headset jack", "Amphenol Nexus class, drawing owed")
        file_has("v2/ecad/tools/jlc-handfit.txt", "U-174/U headset jack 1 (Amphenol Nexus class, drawing owed)")
        if scanned(scan, "U-174/U"): raise SystemExit("build_table: U-174/U is printed somewhere now")
        return dict(status="UNRESOLVED", reason_class="CHOICE_OWED",
                    reason="the netlist's value names a U-174/U jack as a class ('Amphenol Nexus class, drawing owed') and no "
                           "part number; jlc-handfit.txt declares a hand-fit route for it; no PDF under v2/vendor prints "
                           "U-174/U (%s)" % scan_words(scan),
                    next_action="the board C author names the jack (maker's part number) and files its drawing; the 17 mm "
                                "hole and the five leads to board D8 are then checked against it")
    if land == "LeadLands_1x02":                   # J_MAINSW and J_PIJ2: both leads are bought (rule N-1)
        if "XH2.5 at the A22 end" in sorted(s["values"])[0]:
            value_has(s, "MAIN button lead to A22 J_MAINSW", "two solder lands on the underside")
            n, line = line_of("v2/docs/ASSEMBLY.md", "| MAIN button | C7 `J_MAINSW`")
            for ph in ("24 AWG twisted", "XH2.5 at the A22 end"):
                if ph not in line: raise SystemExit("build_table: ASSEMBLY.md line %d no longer says %r" % (n, ph))
            return dict(status="UNRESOLVED", reason_class="CHOICE_OWED",
                        reason="the netlist's value names a lead soldered to two lands on the underside and plugged into "
                               "A22's J_MAINSW with an XH2.5 housing at that end; ASSEMBLY.md line %d (section 4, Leads) "
                               "gives the wire as 24 AWG twisted and the XH2.5 housing at the A22 end, and names no "
                               "insulation, length, maker, housing part number or crimp contacts: the lead is bought, so it "
                               "is not NOT_A_PART (rule N-1; w5ident's table called it NOT_A_PART)" % n,
                        next_action="the board C author names the wire (insulation, length, maker) and the XH2.5 housing "
                                    "and crimp contacts at A22's end by their part numbers")
        value_has(s, "PI button lead: two solder lands on the underside")
        n, line = line_of("v2/docs/ASSEMBLY.md", "| PI button | SW_PI's contacts | C7 `J_PIJ2`")
        for ph in ("24 AWG", "soldered, beaded"):
            if ph not in line: raise SystemExit("build_table: ASSEMBLY.md line %d no longer says %r" % (n, ph))
        return dict(status="UNRESOLVED", reason_class="CHOICE_OWED",
                    reason="the netlist's value names two solder lands on the underside for the PI button's lead; "
                           "ASSEMBLY.md line %d (section 4, Leads) gives that lead as 24 AWG, soldered and beaded, from "
                           "SW_PI's contacts to J_PIJ2, and names no insulation, length or maker: a wire soldered in is "
                           "bought, so it is not NOT_A_PART (rule N-1; round 4's check, BB2)" % n,
                    next_action="the board C author names the wire (insulation, length, maker) with the gauge ASSEMBLY.md "
                                "gives")
    if land == "BackerScrew_M3_GND":               # H1 to H8
        value_has(s, "M3 x 6", "GND bond to the plate")
        return dict(status="UNRESOLVED", reason_class="CHOICE_OWED",
                    reason="the netlist's value names an M3 x 6 screw into the face plate's self-clinching standoff as the "
                           "plate's ground bond, and no standard, head, material or plating; the screw carries the bond, so "
                           "its plating is a requirement nobody has stated",
                    next_action="the mechanical owner names the screw (standard, head, material, plating) against the "
                                "standoff's maker's document")
    if sid == "S-5ae2e5c268":                       # C28
        r = s["requirements"]
        if (r.get("v_rating_min"), r.get("dielectric"), r.get("package"), r.get("value")) != (6.3, "X7R", "0805", "4.7uF"):
            raise SystemExit("build_table: C28's requirement moved: %s" % r)
        return dict(status="UNRESOLVED", reason_class="CHOICE_OWED",
                    reason="the netlist's value is '4.7u' on an 0805 land with no order code; with EPD_VCC declared in board "
                           "C's intent the requirement derives as 4.7 uF, 0805, X7R (rule C-D3), at least 6.3 V (the 20 "
                           "percent margin), 10 percent; no part has been chosen for it",
                    next_action="choose a 4.7 uF X7R 0805 of at least 6.3 V whose maker's document prints or decodes it (a "
                                "Yageo CC0805 part would decode on the Yageo scheme if its range table lists it), and give "
                                "the generator its order code")
    far = {"S-8b55c1443b": ("v2/vendor/passives/fenghua-series-705023d3.pdf", "its How To Order table on page 4 is a column "
                            "layout this stream did not write a scheme for"),
           "S-8b1dfb7d63": ("v2/vendor/passives/fenghua-series-705023d3.pdf", "its How To Order table on page 4 is a column "
                            "layout this stream did not write a scheme for"),
           "S-23fe50c33a": ("v2/vendor/passives/arlitech-atnr-series-spec.pdf", "its page 4 prints the part as ATNR4010100[]T "
                            "with a tolerance placeholder, which neither binding reads"),
           "S-8fcb029420": ("v2/vendor/passives/uniroyal-cs03w5f470lt5e.pdf", "its part number page names the size code CS03 "
                            "and not the 0603 land, and the selection's temperature coefficient (200 ppm/K) is not a field "
                            "of the part number")}
    if sid in far:
        doc, why = far[sid]
        if os.path.exists(os.path.join(REPO, doc)): raise SystemExit("build_table: %s is in the tree now; bind it" % doc)
        other = scanned(scan, ident["mpn"])
        tail = ("; the only PDFs under v2/vendor that print %s are other makers' (%s)" % (ident["mpn"], "; ".join(
            "%s p. %s" % (h["document"], ",".join(str(x) for x in h["pages"])) for h in other))) if other else \
            "; no PDF under v2/vendor prints %s (%s)" % (ident["mpn"], scan_words(scan))
        return dict(status="UNRESOLVED", reason_class="DOCUMENT_DOES_NOT_NAME_THE_PART",
                    reason="w5ident's table names %s %s on %s, which is not in this tree (read from fnd/w5ident %s: it prints "
                           "no complete part number; %s)%s" % (ident.get("maker"), ident["mpn"], doc, W5IDENT[:8], why, tail),
                    next_action="file the maker's sheet (w5ident's copy, sources.txt of fnd/w5ident) and write its DECODED "
                                "scheme where its layout allows, or file a maker's document that prints %s" % ident["mpn"])
    if ident.get("mpn") in ("5636ADKB-2V",):
        if scanned(scan, "5636ADKB-2V") or scanned(scan, "5636ADKB"): raise SystemExit("build_table: 5636ADKB is printed somewhere now")
        return dict(status="UNRESOLVED", reason_class="DOCUMENT_OWED",
                    reason="the netlist's value names APEM 5636ADKB-2V; no PDF under v2/vendor prints 5636ADKB (%s); the "
                           "APEM document held (v2/vendor/switches/apem-switch-guards-series.pdf) is its guards series" % scan_words(scan),
                    next_action="file APEM's 5600 series document that prints or decodes 5636ADKB-2V")
    return None


def owed_reason(ident, oc, netlist_codes, s, scan):
    """The reason of an identity whose maker and part number are named and whose document is owed, on read facts."""
    mpn, code = ident.get("mpn"), (oc or {}).get("code")
    if any(mpn in v for v in s["values"]): src = "the part number the netlist's value names"
    elif code and code in netlist_codes: src = "stream w5ident's catalogue reading of %s, the order code the netlist carries" % code
    elif code: src = "stream w5ident's catalogue reading of %s (the netlist carries %s)" % (code, ", ".join(sorted(netlist_codes)) or "no code")
    else: src = "stream w5ident's choice"
    hits = scanned(scan, mpn)
    if hits:
        where = "; ".join("%s p. %s" % (h["document"], ",".join(str(x) for x in h["pages"])) for h in hits)
        return ("maker and part number: %s; the maker's own document is not held: the only PDFs under v2/vendor that print %s "
                "are other makers' (%s)" % (src, mpn, where))
    return "maker and part number: %s; no PDF under v2/vendor prints %s (%s)" % (src, mpn, scan_words(scan))


def main(argv):
    out = opt(argv, "--out") or PI.TABLE
    carried = json.load(open(CARRIED))
    old = {s["id"]: s for s in carried["board_c"]}
    rs, meta = PI.rows(boards=["c"])
    sel = PI.selections(rs)
    ids = {PI.selection_id(k) for k in sel}
    stray = sorted(set(DECISIONS) - ids)
    if stray: raise SystemExit("build_table: decisions name ids that are not selections now: %s" % stray)
    log, table_sel, uncovered = [], [], []
    scan = json.load(open(SCAN))
    lcsc = {r["code"]: r for r in json.load(open(LCSC_READING))["rows"]}
    rowp = {"%s:%s" % (p["board"], p["ref"]): p for p in rs}
    for key, s in sel.items():
        sid = PI.selection_id(key)
        if sid in DECISIONS:
            d = dict(DECISIONS[sid]); src = "stream w5identc (this builder's DECISIONS)"
            oc = d.pop("order_code", {})
        elif sid in old:
            d = dict(old[sid]["identity"]); src = "stream w5ident's table (fnd/w5ident %s), key unchanged" % carried["source_commit"][:8]
            oc = old[sid].get("order_code") or {}
            if sid in MAKER_AS_PRINTED:
                d["maker"] = MAKER_AS_PRINTED[sid]
            if sid in HELD:
                d["datasheet"] = dict(path=HELD[sid], joined_by="this stream: a held document found by reading the vendor folders")
                src += "; the document bound by stream w5identc"
        else:
            uncovered.append(sid); continue
        ident = collections.OrderedDict(status=d.get("status"))
        for k in ("maker", "mpn"):
            if d.get(k): ident[k] = d[k]
        st = d.get("status")
        if st in ("RESOLVED", "RESOLVED_DATASHEET_OWED") and (d.get("datasheet") or {}).get("path"):
            bound, why = resolve_document(d, sid, log)
            if bound:
                ident["status"] = "RESOLVED"; ident["datasheet"] = bound
            else:
                ident["status"] = "UNRESOLVED"; ident["reason_class"] = "DOCUMENT_DOES_NOT_NAME_THE_PART"
                ident["reason"] = ("%s names %s %s and binds a document that does not print it: %s"
                                   % ("w5ident's table" if sid not in DECISIONS else "this stream", d.get("maker"), d.get("mpn"), why))
                ident["next_action"] = ("file a document of %s's that prints %s (a part specification, not a series sheet), or "
                                        "take a part meeting the same requirement whose maker prints its part number"
                                        % (d.get("maker"), d.get("mpn")))
        elif st in ("RESOLVED", "RESOLVED_DATASHEET_OWED"):
            ident["status"] = "UNRESOLVED"
            inferred = "INFERRED" in (d.get("chosen_by") or "")
            ident["reason_class"] = "PART_NUMBER_INFERRED" if inferred else "DOCUMENT_OWED"
            ident["reason"] = ("maker and part number named (%s); no document held in this tree prints the part number"
                               % (d.get("chosen_by") or "carried").rstrip("."))
            ident["next_action"] = ("file %s's document that prints %s under v2/vendor/ (held back where its terms forbid "
                                    "redistribution, with a sources.txt line and a fetch script), and re-run this builder"
                                    % (d.get("maker"), d.get("mpn")))
        elif st == "UNRESOLVED":
            ident["reason_class"] = d.get("reason_class") or classify(d)
            ident["reason"] = d.get("reason"); ident["next_action"] = d.get("next_action")
        elif st == "NOT_A_PART":
            ident["reason"] = d.get("reason")
        else:
            raise SystemExit("build_table: %s has the status %r" % (sid, st))
        if ident["status"] == "UNRESOLVED" and ident.get("mpn") and ident.get("reason_class") in ("DOCUMENT_DOES_NOT_NAME_THE_PART", "DOCUMENT_OWED"):
            dec, why = try_decode(ident, s["requirements"], sid, log, kind=s["kind"])
            if dec:
                was = ident.pop("reason_class"); ident.pop("reason", None); ident.pop("next_action", None)
                ident["status"] = "RESOLVED"; ident["datasheet"] = dec
                ident["decoded_after"] = "%s under PRINTED" % was
            elif why:
                ident["reason"] += "; " + why
        netlist_codes = {rowp[r]["generator_lcsc"] for r in s["rows"] if rowp[r].get("generator_lcsc")}
        rr = reread(sid, s, ident, scan)
        if rr is not None:
            for k in ("reason_class", "reason", "next_action", "datasheet"): ident.pop(k, None)
            if rr.get("datasheet"):
                full = os.path.join(REPO, rr["datasheet"]["path"]); rr["datasheet"]["sha256"] = sha(full)
                r = PI.read_binding(rr["datasheet"], rr["mpn"], maker=rr.get("maker"), req=s["requirements"], kind=s["kind"])
                if r["state"] != "READ": raise SystemExit("build_table: %s: its re-read binding reads %s: %s" % (sid, r["state"], r["why"]))
                log.append(dict(selection=sid, mpn=rr["mpn"], document=rr["datasheet"]["path"], binding="PRINTED", page=rr["datasheet"]["page"], state=r["state"], why=r["why"]))
            ident.update(rr)
            src += "; re-read by stream w5identc round 3"
        elif ident["status"] == "UNRESOLVED" and ident.get("reason_class") == "DOCUMENT_OWED" and ident.get("mpn"):
            ident["reason"] = owed_reason(ident, oc, netlist_codes, s, scan)
            ident["next_action"] = ("a DECODED binding on the maker's ordering-code table where one is held and decision 59 "
                                    "has a scheme for it, else file %s's document that prints %s (held back where its terms "
                                    "forbid redistribution)" % (ident.get("maker"), ident["mpn"]))
        elif ident["status"] == "UNRESOLVED" and ident.get("reason_class") == "DOCUMENT_DOES_NOT_NAME_THE_PART":
            ident["next_action"] = ("a DECODED binding on the maker's ordering-code table (decision 59) where it decodes, else a "
                                    "maker's document that prints %s" % ident.get("mpn"))
        if d.get("chosen_by") and ident["status"] != "UNRESOLVED": ident["chosen_by"] = d["chosen_by"]
        # the order code: what the netlist carries, and whether this tree's own catalogue reading knows it (round 3, minors 9, 10)
        if oc or netlist_codes:
            oc = dict(oc)
            oc["netlist_codes"] = sorted(netlist_codes)
            if oc.get("code"):
                oc["netlist_agrees"] = (not netlist_codes) or netlist_codes == {oc["code"]}
                lr = lcsc.get(oc["code"])
                oc["in_this_trees_reading"] = bool(lr and lr.get("model"))
                oc["read_by"] = ("v2/docs/parts/readings/lcsc-2026-09-27.json: %s %s" % (lr.get("brand"), lr.get("model"))
                                 if lr and lr.get("model") else "stream w5ident's catalogue reading of 27 September 2026 (fnd/w5ident, not in this tree)")
            for c in sorted(netlist_codes - {oc.get("code")}):
                lr = lcsc.get(c)
                oc.setdefault("netlist_code_reads", {})[c] = ("%s %s" % (lr.get("brand"), lr.get("model"))) if lr and lr.get("model") else "not in this tree's catalogue reading"
        ident["from"] = src
        table_sel.append(collections.OrderedDict(
            id=sid, key=key, kind=s["kind"], n_rows=len(s["rows"]), rows=s["rows"], values=sorted(s["values"]),
            lands=sorted(s["lands"]), requirements=dict(s["requirements"]),
            basis={k: sorted(v) for k, v in s["basis"].items()}, findings=sorted(s["findings"]),
            identity=dict(ident), order_code=dict(oc)))
    if uncovered: raise SystemExit("build_table: selections with neither a carried identity nor a decision: %s" % uncovered)
    st = collections.Counter(x["identity"]["status"] for x in table_sel)
    rc = collections.Counter(x["identity"].get("reason_class") for x in table_sel if x["identity"]["status"] == "UNRESOLVED")
    rows_by = collections.Counter()
    for x in table_sel: rows_by[x["identity"]["status"]] += x["n_rows"]
    by_binding = collections.Counter(((x["identity"].get("datasheet") or {}).get("binding") or "PRINTED")
                                     for x in table_sel if x["identity"]["status"] == "RESOLVED")
    t = collections.OrderedDict(
        schema_version=2,
        what=("The identity of every distinct part selection on the boards in `scope` (layer 6's exact-part requirement: "
              "LAYER-STATUS item 6.1, EXECUTION-PLAN review D, EQ-21): the BOM parts of the committed netlist grouped by "
              "every property that decides the part, each selection RESOLVED to a maker, a manufacturer part number and a "
              "held maker's document whose cited page prints that part number (PRINTED) or is the maker's ordering-code "
              "table that decodes it against the selection (DECODED, decision 59, counted apart; it does not show the value "
              "is made at that rating), both read by part_identities.py check (rule D-2), or UNRESOLVED with its reason "
              "class, reason and next action. Written by v2/docs/records/w5identc/build_table.py; "
              "a prototype record: nothing is ordered by it."),
        taken_by=TAKEN, authority=SESSION, scope=["c"],
        inputs=[dict(board=m["board"], phase=m["phase"], netlist=m["netlist"], netlist_sha256=m["netlist_sha256"],
                     intent=m["intent"], intent_sha256=m["intent_sha256"], bom_export=m["bom_export"],
                     bom_export_sha256=m["bom_export_sha256"], bom_export_agrees=m["bom_export_agrees"],
                     bom_export_differences=m["bom_export_differences"], rows=m["rows"],
                     excluded_from_bom=m["excluded_from_bom"]) for m in meta],
        rules=rules(carried["w5ident_rules"]),
        counts=dict(rows=len(rs), selections=len(table_sel), identity_status=dict(st), unresolved_by_reason=dict(rc),
                    resolved_by_binding=dict(by_binding),
                    rows_by_identity_status=dict(rows_by)),
        selections=table_sel)
    import yaml
    txt = ("# pcb_part_identities.yaml: GENERATED by v2/docs/records/w5identc/build_table.py; edit its DECISIONS, not this file.\n"
           + yaml.safe_dump(json.loads(json.dumps(t)), sort_keys=False, allow_unicode=True, width=120))
    open(out, "w", encoding="utf-8").write(txt)
    json.dump(dict(what="rule D-2 as the builder read it: every identity that claimed a document, the pages read and the first page printing the part number",
                   documents=log), open(os.path.join(HERE, "readings", "builder-document-reads.json"), "w"), indent=1, sort_keys=True)
    print("build_table: %d rows, %d selections, %s, resolved by binding %s, unresolved by reason %s -> %s"
          % (len(rs), len(table_sel), dict(st), dict(by_binding), dict(rc), os.path.relpath(out, REPO)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
