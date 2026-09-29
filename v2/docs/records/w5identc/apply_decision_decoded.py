#!/usr/bin/env python3
"""apply_decision_decoded.py: record the session's DECODED binding decision in v2/ecad/tools/pcb_decisions.yaml and
rebind the records bound to that file (MESHSAT-1357, stream w5identc, 29 September 2026). For the integrator; the stream
edits neither registry.

The decision was taken by the session (the coordinator of round 2) under the owner's ruling of 21 September 2026 that
engineering decisions are the session's, and implemented in v2/ecad/tools/part_identities.py (read_decoded, SCHEMES)
with its fixture tests. This script appends one decision at the next free number (59 on b874b744 and on fnd/int15
097d2517, computed from the file), asserts that the highest number is the file's last entry, that the new text differs,
that the file re-parses with exactly one more decision carrying every authority field and every earlier decision
unchanged, and refuses a second run (its marker in a parsed title). Then it rebinds every record whose evidence is bound
to pcb_decisions.yaml (CFL-016 on main and on int15) through apply_rebind_decisions_w5identc.rebind, parsed against
HEAD's file. After it: decisions_render.py (OWNER-DECISIONS-OPEN.md lists every ruled decision) and rules_lib.py
requirements.
Usage: apply_decision_decoded.py [--check]   (--check: both changes computed in memory and asserted, nothing written)"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DEC = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_decisions.yaml")
MARKER = "(stream w5identc)"
REG = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
FIELDS = ("n", "title", "asked", "status", "authority", "authority_why", "ruled_by", "ruled_on", "outcome", "reversed_by",
          "ask", "recommendation", "evidence", "blocks", "holds_nothing_today")

ENTRY = dict(
    title="A part identity may be RESOLVED on the maker's ordering-code table: a DECODED binding, counted apart from "
          "PRINTED %s" % MARKER,
    asked="2026-09-29",
    status="ruled",
    authority="SESSION",
    authority_why="it changes no line the never-auto floor protects (no class of tools/reserved.json names "
                  "part_identities.py, pcb_part_identities.yaml or the identity rules), spends nothing (no part is "
                  "bought or changed: it decides how a held maker's document is read), changes no claim about the kit (a "
                  "DECODED binding is labelled so wherever it is counted), and accepts no residual risk that no "
                  "measurement in this tree can remove: its stated limit (the range table) is removed by reading the "
                  "maker's range tables, which the tree holds for Yageo (round 3's independent check read pages 5 and 6 of "
                  "the filed sheet and found 0603 50 V 100 nF, 0603 25 V 1 uF, 0603 16 V 1 uF and 0805 16 V 10 uF listed); "
                  "the owner's ruling of 21 September 2026 makes such an engineering decision the session's",
    ruled_by="SESSION under the owner's ruling of 21 September 2026",
    ruled_on="2026-09-29",
    outcome="A binding of a part identity to a document is PRINTED (the cited page prints the part number, letter case "
            "aside; a packing code may be printed as the maker's placeholder where the same page keys it) or DECODED. A "
            "DECODED binding cites the maker's own ordering-code table, one page, for a scheme written in "
            "part_identities.SCHEMES with the document's sha256 (a table cannot add or edit one). The tool reads the "
            "layout from that page (Yageo's numbered placeholders, Uniroyal's numbered code positions), slices the whole "
            "part number by it with nothing left over, requires each field to be the one the page puts at that position "
            "and each literal to equal the scheme's, reads each code but the value's in a row of its own part of the "
            "page that maps it to the meaning claimed, computes the value by the rule its row states (with the power of "
            "ten row for resistors), and requires every deciding property of the kind (capacitor: value, package, "
            "tolerance, rated voltage, dielectric, construction; resistor: value, package, tolerance, power) to meet the "
            "selection's requirements as the check derives them from the netlist, the intent and the generator's value, "
            "never as the table states them. It refuses another kind of part, a property the scheme cannot decode, a "
            "permuted or padded part number, and a distributor's page. A DECODED binding is marked so in "
            "pcb_part_identities.yaml and counted apart (resolved_by_binding). LIMIT, stated: it shows what a part "
            "number means in the maker's scheme, not that the maker makes that value at that rating (the range table), "
            "which w5ident's second check (ID-B1 items 2 to 4) found false for three part numbers. On board C at "
            "b874b744: 23 selections DECODED (Yageo CC X7R and Uniroyal 0603WAF), 21 PRINTED",
    reversed_by="set every DECODED binding of pcb_part_identities.yaml back to UNRESOLVED (DOCUMENT_DOES_NOT_NAME_THE_PART) "
                "by removing decode_spec from v2/docs/records/w5identc/build_table.py and re-running it, and remove the "
                "DECODED branch of part_identities.read_binding and SCHEMES; or add the range-table citation as a second "
                "requirement of a DECODED binding",
    ask="accept a maker's series sheet that prints an ordering scheme and not the part number (the Yageo and Uniroyal "
        "sheets bound here print none of the 20 part numbers w5ident bound to them, read page by page by build_table.py), "
        "or require a document that prints the part number",
    recommendation="DECODED, labelled apart from PRINTED, sliced by the layout the maker's page prints, every field read "
                   "on that page and every deciding property matched to the requirements derived from the netlist; the "
                   "range table stays a stated limit",
    evidence="v2/ecad/tools/part_identities.py (SCHEMES, scheme_slots, read_decoded, read_binding, check); "
             "tests/test_part_identities.py (t_a_decoded_binding_that_holds, "
             "t_a_decoded_tolerance_that_contradicts_the_selection_is_refused, "
             "t_a_decoded_binding_on_a_page_that_lacks_a_field_is_refused, "
             "t_a_decoded_binding_on_a_distributors_page_is_refused, "
             "t_the_checkers_scheme_probes_are_refused_on_the_makers_own_page, "
             "t_uniroyal_positions_refuse_a_permuted_part_number, t_the_check_judges_on_requirements_derived_from_the_netlist); "
             "v2/docs/records/w5identc/readings/check-board-c-b874b744.json; YAGEO CC X7R product specification V.26 "
             "page 2 (v2/vendor/passives/yageo-cc-series.pdf) and Uniroyal's thick film chip resistor data sheet page 2 "
             "(held back, v2/docs/records/w5identc/fetch_held_back.py); the independent check of round 3 "
             "(_scratch/chk-w5identc/CHECK.md)",
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
    import apply_rebind_decisions_w5identc as RB
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
    head = subprocess.run(["git", "-C", ROOT, "show", "HEAD:v2/ecad/tools/pcb_decisions.yaml"], capture_output=True, check=True).stdout
    if head.decode("utf-8") != txt: raise SystemExit("apply_decision_decoded: the tree's pcb_decisions.yaml is not HEAD's; commit or restore it first")
    reg_txt = open(REG, encoding="utf-8").read()
    reg_new, bound, o16, n16 = RB.rebind(reg_txt, head, new.encode("utf-8"))
    print(_block(n))
    print("apply_decision_decoded: %s rebound from pcb_decisions.yaml@%s to @%s" % (", ".join(bound), o16, n16))
    if check:
        print("apply_decision_decoded: --check, decision %d and the rebind hold every assertion, nothing written" % n); return 0
    open(DEC, "w", encoding="utf-8").write(new)
    yaml.safe_load(open(DEC, encoding="utf-8").read())
    open(REG, "w", encoding="utf-8").write(reg_new)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != yaml.safe_load(reg_new): raise SystemExit("re-parse differs")
    print("apply_decision_decoded: decision %d written, %s rebound; run decisions_render.py and rules_lib.py requirements next" % (n, ", ".join(bound)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
