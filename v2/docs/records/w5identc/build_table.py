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
        rule=("A RESOLVED selection names a maker, a manufacturer part number and a held document with a page, and that page's "
              "text layer PRINTS the part number, letter case aside and nothing else (the characters on either side are not "
              "letters or digits). The builder finds the first such page by reading the document page by page; "
              "part_identities.py check reads the cited page again, checks the document's sha256, and refuses the binding "
              "otherwise. A series sheet that prints an ordering scheme and not the part number does not name the part: the "
              "selection is UNRESOLVED (DOCUMENT_DOES_NOT_NAME_THE_PART) until a document that prints it is held. A document "
              "held back from the public tree is cited by address and sha256 and read where it is fetched"),
        why=("w5ident's second check, ID-B1 to ID-B3: nine passive selections and five others were RESOLVED on documents that "
             "do not name the part, and nothing in the check read a document"),
        reversal=("a predicate that also accepts a decoded ordering scheme with the value listed at the rating in the maker's "
                  "range table (ID-B3's alternative) is a change of this rule, taken by the integrator, not a reading of it"),
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
        if d.get("chosen_by"): ident["chosen_by"] = d["chosen_by"]
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
    t = collections.OrderedDict(
        schema_version=2,
        what=("The identity of every distinct part selection on the boards in `scope` (layer 6's exact-part requirement: "
              "LAYER-STATUS item 6.1, EXECUTION-PLAN review D, EQ-21): the BOM parts of the committed netlist grouped by "
              "every property that decides the part, each selection RESOLVED to a maker, a manufacturer part number and a "
              "held document whose cited page prints that part number (rule D-2, read by part_identities.py check), or "
              "UNRESOLVED with its reason class, reason and next action. Written by v2/docs/records/w5identc/build_table.py; "
              "a prototype record: nothing is ordered by it."),
        taken_by=TAKEN, authority=SESSION, scope=["c"],
        inputs=[dict(board=m["board"], phase=m["phase"], netlist=m["netlist"], netlist_sha256=m["netlist_sha256"],
                     intent=m["intent"], intent_sha256=m["intent_sha256"], bom_export=m["bom_export"],
                     bom_export_sha256=m["bom_export_sha256"], bom_export_agrees=m["bom_export_agrees"],
                     bom_export_differences=m["bom_export_differences"], rows=m["rows"],
                     excluded_from_bom=m["excluded_from_bom"]) for m in meta],
        rules=rules(carried["w5ident_rules"]),
        counts=dict(rows=len(rs), selections=len(table_sel), identity_status=dict(st), unresolved_by_reason=dict(rc),
                    rows_by_identity_status=dict(rows_by)),
        selections=table_sel)
    import yaml
    txt = ("# pcb_part_identities.yaml: GENERATED by v2/docs/records/w5identc/build_table.py; edit its DECISIONS, not this file.\n"
           + yaml.safe_dump(json.loads(json.dumps(t)), sort_keys=False, allow_unicode=True, width=120))
    open(out, "w", encoding="utf-8").write(txt)
    json.dump(dict(what="rule D-2 as the builder read it: every identity that claimed a document, the pages read and the first page printing the part number",
                   documents=log), open(os.path.join(HERE, "readings", "builder-document-reads.json"), "w"), indent=1, sort_keys=True)
    print("build_table: %d rows, %d selections, %s, unresolved by reason %s -> %s" % (len(rs), len(table_sel), dict(st), dict(rc), os.path.relpath(out, REPO)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
