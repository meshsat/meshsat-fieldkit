#!/usr/bin/env python3
"""apply_decision_decoded.py: record the session's DECODED binding decision in v2/ecad/tools/pcb_decisions.yaml
(MESHSAT-1357, stream w5identc, 29 September 2026). For the integrator; the stream does not edit the registry.

The decision was taken by the session (the coordinator of round 2) under the owner's ruling of 21 September 2026 that
engineering decisions are the session's, and implemented by this stream in v2/ecad/tools/part_identities.py
(read_decoded) with four fixture tests. This script appends one decision at the next free number (59 on b874b744,
computed from the file at apply time), asserts the file ends where it did when drafted (the last decision's final
line), that the new text differs, that the file re-parses with exactly one more decision carrying every authority
field, and refuses a second run (its marker is already present). After it: decisions_render.py (the generated
OWNER-DECISIONS-OPEN.md lists every ruled decision; test_decision_register refuses a stale page).
Usage: apply_decision_decoded.py [--check]   (--check: assert everything, print the entry, write nothing)"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DEC = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_decisions.yaml")
MARKER = "DECODED binding (stream w5identc)"
FIELDS = ("n", "title", "asked", "status", "authority", "authority_why", "ruled_by", "ruled_on", "outcome", "reversed_by",
          "ask", "recommendation", "evidence", "blocks", "holds_nothing_today")

ENTRY = dict(
    title="A part identity may be RESOLVED on the maker's ordering-code table: a DECODED binding (%s), never "
          "counted as PRINTED" % MARKER,
    asked="2026-09-29",
    status="ruled",
    authority="SESSION",
    authority_why="it changes no line the never-auto floor protects (no class of tools/reserved.json names "
                  "part_identities.py, pcb_part_identities.yaml or the identity rules), spends nothing (no part is "
                  "bought or changed: it decides how a held maker's document is read), and changes no claim about the "
                  "kit (a DECODED binding is labelled so wherever it is counted); the owner's ruling of 21 September "
                  "2026 makes such an engineering decision the session's",
    ruled_by="SESSION under the owner's ruling of 21 September 2026",
    ruled_on="2026-09-29",
    outcome="A binding of a part identity to a document is PRINTED (the cited page prints the full part number, letter "
            "case aside) or DECODED. A DECODED binding cites the maker's own ordering-code or part-numbering table, "
            "one page, and part_identities.py decodes the part number field by field on that page: the fields' "
            "codes spell the whole part number; each code is in its cited row, and for tolerance, voltage, power, "
            "packaging, quantity and special features the row maps the code to the meaning the binding claims; the "
            "value is computed from its code by the rule the row states (for resistors also the table's power of ten "
            "row); and the decoded value, package, tolerance, rated voltage and dielectric (and the construction a "
            "capacitor's series names) must meet the selection's deciding properties. It refuses a field not in the "
            "table, a field that contradicts the selection, fields that do not spell the part number, and a "
            "distributor's page (a publisher that is a distributor, or a page that prints a distributor's name, or "
            "that does not print the maker's mark). Power and temperature coefficient are compared where the part "
            "number carries them and are recorded as not established where it does not. A DECODED binding is marked "
            "so in pcb_part_identities.yaml and counted apart (resolved_by_binding); it still needs the maker's "
            "document. LIMIT, stated: a DECODED binding says what a part number means in the maker's scheme; it does "
            "not show that the maker makes that value at that rating (the range table), which w5ident's second check "
            "(ID-B1 items 2 to 4) found false for three part numbers. On board C at b874b744: 23 selections DECODED "
            "(Yageo CC X7R and Uniroyal 0603WAF), 20 PRINTED",
    reversed_by="set every DECODED binding of pcb_part_identities.yaml back to UNRESOLVED (DOCUMENT_DOES_NOT_NAME_THE_PART) "
                "by removing decode_spec from v2/docs/records/w5identc/build_table.py and re-running it, and remove the "
                "DECODED branch of part_identities.read_binding; or add the range-table citation as a second "
                "requirement of a DECODED binding",
    ask="accept a maker's series sheet that prints an ordering scheme and not the part number, or require a document "
        "that prints the part number (which Yageo and Uniroyal do not publish for these parts)",
    recommendation="DECODED, labelled apart from PRINTED, with every field read on the maker's table and matched to the "
                   "selection; the range table stays a stated limit",
    evidence="v2/ecad/tools/part_identities.py (read_decoded, read_binding); tests/test_part_identities.py "
             "(t_a_decoded_binding_that_holds, t_a_decoded_tolerance_that_contradicts_the_selection_is_refused, "
             "t_a_decoded_binding_on_a_page_that_lacks_a_field_is_refused, "
             "t_a_decoded_binding_on_a_distributors_page_is_refused); "
             "v2/docs/records/w5identc/readings/check-board-c-b874b744.json; YAGEO CC X7R product specification V.26 "
             "page 2 (v2/vendor/passives/yageo-cc-series.pdf) and Uniroyal's thick film chip resistor data sheet "
             "page 2 (held back, v2/docs/records/w5identc/fetch_held_back.py)",
    blocks={},
    holds_nothing_today="it releases no rule-board pair: no rule of pcb_rules.yaml reads part identities; it moves "
                        "board C's exact-part reading (LAYER-STATUS item 6.1, the open item of apply_identities_c.py)",
)


def _block(n):
    def fold(k, v):
        words, lines, cur = str(v).split(), [], ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > 112: lines.append(cur); cur = w
            else: cur = (cur + " " + w) if cur else w
        if cur: lines.append(cur)
        return "    %s: >-\n%s\n" % (k, "\n".join("      " + l for l in lines))
    out = "  - n: %d\n" % n
    for k in FIELDS[1:]:
        v = ENTRY[k]
        if k in ("asked", "ruled_on", "status", "authority"): out += "    %s: %s\n" % (k, v)
        elif k == "blocks": out += "    blocks: {}\n"
        else: out += fold(k, v)
    return out


def main(argv):
    import yaml
    check = "--check" in argv
    txt = open(DEC, encoding="utf-8").read()
    assert txt.endswith("\n"), "pcb_decisions.yaml does not end with a newline"
    reg = yaml.safe_load(txt)
    # read on the PARSED titles: the title is folded over lines in the file, so the marker is not one line of text
    assert not any(MARKER in " ".join(str(d.get("title", "")).split()) for d in reg["decisions"]), \
        "refused: the decision is already in pcb_decisions.yaml (a second run)"
    ns = [int(d["n"]) for d in reg["decisions"]]
    n = max(ns) + 1
    last = reg["decisions"][-1]
    assert int(last["n"]) == max(ns), "the last entry is not the highest number: the file changed shape"
    assert re.search(r"\n  - n: %d\n" % max(ns), txt), "decision %d's entry line is not in the file" % max(ns)
    new = txt + _block(n)
    assert new != txt
    reg2 = yaml.safe_load(new)
    assert len(reg2["decisions"]) == len(reg["decisions"]) + 1 and reg2["decisions"][:-1] == reg["decisions"]
    e = reg2["decisions"][-1]
    assert e["n"] == n and all(e.get(k) not in (None, "") for k in FIELDS if k != "blocks") and e["blocks"] == {}
    assert e["authority"] == "SESSION" and e["ruled_by"].startswith("SESSION") and MARKER in e["title"]
    print(_block(n))
    if check:
        print("apply_decision_decoded: --check, decision %d holds every assertion, nothing written" % n); return 0
    open(DEC, "w", encoding="utf-8").write(new)
    yaml.safe_load(open(DEC, encoding="utf-8").read())
    print("apply_decision_decoded: decision %d written; run decisions_render.py next" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
