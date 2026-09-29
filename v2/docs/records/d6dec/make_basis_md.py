#!/usr/bin/env python3
"""BASIS.md from basis.json (stream d6dec, 29 September 2026). Usage: make_basis_md.py <basis.json> <BASIS.md>

basis.json is what box/basis_check.py wrote on the six boards' committed intent files. The three NOT_FOUND rows carry
a reading of the held document's text layer each, made by this stream with pdftotext and quoted in NOTES below; that
reading is the only hand-written part."""
import sys, json, collections

NOTES = {
    "board A C4 at U1.1 class D": (
        "The held v2/vendor/power/ltc2954.pdf reads \"VIN (Pin 1/Pin 4): Power Supply Input: 2.7V to 26.4V.\" "
        "The basis drops \"(Pin 1/Pin 4)\" inside its quotation marks with no ellipsis. The substance is the maker's; "
        "the quotation is not verbatim. Next action: board A's writer quotes it whole (gen_sch_a.py, on the set 9 line)."),
    "board B C71 at U10.4 class D": (
        "The held v2/vendor/ti/ti-tmp117-temperature.pdf (SNOSD82D) reads \"A recommended value for this supply bypass "
        "capacitor is 100 nF\" (Power Supply Recommendations). The basis writes \"The\" where the maker writes \"A\". "
        "The value and the clause are the maker's. Next action: board B's writer corrects the article in gen_sch_b.py."),
    "board E C58 at U17.5 class D": (
        "The held v2/vendor/sensirion/sgp41-datasheet.pdf, section 2.5, reads in its text layer \"... a capacitor of "
        "1 F is recommended\": the micro sign is not in the text layer, so the words cannot be matched as written. "
        "The first piece of the quotation is found. This is the document's text layer, not a misquote; no action."),
}


def main(a):
    d = json.load(open(a[0], encoding="utf-8"))
    per = collections.defaultdict(collections.Counter)
    for r in d["rows"]:
        for u in r["used_by"]:
            b = u.split()[1] if u.startswith("board ") else "table"
            kind = "loop" if " loop of " in u else "entry"
            per[(b, kind)][r["status"]] += 1
    order = ["FOUND", "PAGE", "ELSEWHERE", "NOT_FOUND", "NO_QUOTE"]
    L = []
    L.append("# The decoupling declarations' maker clauses, looked up in the held documents (d6dec, 29 September 2026)\n")
    L.append("Written by `make_basis_md.py` from `basis.json`, which `box/basis_check.py` wrote on this host (bounded: "
             "pdftotext on %d held PDFs, two jobs at the lowest priority) from the six boards' COMMITTED intent files, "
             "`v2/ecad/pcb-*-<phase>/out/*-intent.json` at this branch's merge of main 9147db5d. It reads what each "
             "`basis` puts in quotation marks and searches the document the basis names for those words. It judges "
             "the quotation, not the engineering: a FOUND row says the maker wrote those words, not that the class "
             "drawn from them is right.\n" % d["documents"])
    L.append("**What a result means.** FOUND: every quoted passage is in the named document word for word after the "
             "normalisation of the tool's docstring (case, white space, typographic quotes and dashes, the micro "
             "sign, a line-end hyphen). PAGE: found, on another page than the basis states (a basis may count printed "
             "pages where the tool counts the PDF's own; the RP2040 datasheet's printed page is one less than its PDF "
             "page, which is every PAGE row of boards C and E). ELSEWHERE: found in a held document the basis does "
             "not name. NOT_FOUND: a quoted passage is in no held document as written. NO_QUOTE: the basis quotes "
             "nothing (most say the maker states no capacitor and the generator's own count stands, rule D1), so "
             "nothing can be looked up.\n")
    L.append("%d declarations and power-loop rows read, %d distinct bases; %d held PDFs have no text layer (drawings "
             "and one schematic; none is named by a basis that reads NOT_FOUND).\n" % (d["claims"], d["distinct_bases"],
             len(d["documents_with_no_text"])))
    L.append("## Counts per board (each declaration counted once, with its basis's result)\n")
    L.append("| board | what | " + " | ".join(order) + " | total |")
    L.append("|---|---|" + "---|" * (len(order) + 1))
    tot = collections.Counter()
    for (b, kind) in sorted(per):
        c = per[(b, kind)]; tot.update(c)
        L.append("| %s | %s | %s | %d |" % (b, "bypass entries" if kind == "entry" else "power loops (`power_loops`)",
                                          " | ".join(str(c.get(k, 0)) for k in order), sum(c.values())))
    L.append("| all | | %s | %d |" % (" | ".join(str(tot.get(k, 0)) for k in order), sum(tot.values())))
    L.append("")
    L.append("## Every NOT_FOUND row\n")
    for r in d["rows"]:
        if r["status"] != "NOT_FOUND": continue
        for u in r["used_by"]:
            L.append("### %s\n" % u)
        L.append("- basis: %s" % r["basis"].replace("|", "/"))
        L.append("- document named: %s" % (", ".join("`%s`" % x for x in r["documents_named"]) or "none held"))
        for q in r["quotes"]:
            L.append("- passage %s: \"%s\"%s" % (q["status"], q["quote"][:200],
                                                 ("; pieces not found: %s" % q.get("pieces_not_found")) if q.get("pieces_not_found") else ""))
        n = NOTES.get(r["used_by"][0])
        L.append("- reading of the held text: %s\n" % (n or "none made"))
    L.append("## Every PAGE row (found, on another page than stated)\n")
    L.append("| declaration(s) | stated | found (document, PDF page) | passage |")
    L.append("|---|---|---|---|")
    for r in d["rows"]:
        if r["status"] != "PAGE": continue
        for q in r["quotes"]:
            if q["status"] != "PAGE": continue
            L.append("| %s | %s | %s | %s |" % ("; ".join(r["used_by"])[:160], q["pages_stated"],
                                              ", ".join("%s p.%s" % (h["document"].split("/")[-1], h["pages"]) for h in q["found"][:2]),
                                              q["quote"][:90].replace("|", "/")))
    L.append("")
    L.append("Every PAGE row but one is a one-page offset between the page the basis states and the PDF's own page "
             "(the RP2040 datasheet on boards C and E, the TUSB8041, RM520N and LG290P documents on board B). The one "
             "that is not, read with `pdftotext -f <page> -l <page>`: board B's C37 and C38 at the TS3DV642. The quoted "
             "\"Decoupling capacitors should be used between power supply pin and ground ...\" is on PDF page 23 "
             "(layout guidelines); page 18 carries a different sentence, \"Decoupling capacitors may be used to reduce "
             "noise and improve power supply integrity\". DECOUPLING.md G5 cites SCDS343F pp.18 and 23, so the record "
             "names both pages and the basis states only the first. It changes no value and no class; it is board B's "
             "writer's basis text to correct.\n")
    open(a[1], "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("make_basis_md: %s" % a[1])


if __name__ == "__main__": main(sys.argv[1:])
