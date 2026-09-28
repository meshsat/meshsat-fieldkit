#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, MESHSAT-1357, layer 9): SI-001's coverage
record says what the reading now is. pcb_rules_coverage.yaml is the integrator's; this script makes the change and the
integrator runs it. It replaces the first pass's draft, filed as recovered under ../recovery/pass1-drafts/, whose
paragraph described 40 nets by a maker's figure that did not govern them (the independent check's first blocking item).

WHAT IT CHANGES in record SI-001 of v2/ecad/tools/pcb_rules_coverage.yaml, and nothing else:
  * a paragraph is appended to its note: the edge rates as data, the governing-edge rule, and the counts per board;
  * its remediation's `action` text is replaced. Its owner and execution STAY LAB and HARDWARE: what is left is desk
    work for the nets a termination or an impedance target answers, and for every net a bound decides it is still a
    maker's model or a measurement at bring-up (the check's finding on the first draft, which had moved them to
    SESSION and PARALLEL_AGENT).

THE COUNTS ARE NOT TYPED HERE. They are taken when the script runs, in memory, by edge_length.schematic_table on the
declared netlist of each board OF THE TREE IT RUNS IN, so the paragraph describes the integrated netlists and not
this stream's. Nothing is written by taking them. The sums are checked before the paragraph is composed.

HOW: the record is found by its id; the old remediation text is asserted; the new text is parsed and COMPARED WITH THE
OLD ONE AS STRUCTURE before anything is written: every other record unchanged, and in SI-001 every key unchanged but
`note`, which must be the old note with the paragraph after it, and `remediation.action`. A second run is refused.

Applied by the integrator on the integrated tree (after set 6), with the data file and the IBIS models committed:
    python3 v2/docs/records/w5si/apply/apply_coverage_si001.py [--root <tree>] [--dry-run]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
if "--root" in sys.argv: ROOT = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
TARGET = os.path.join(TOOLS, "pcb_rules_coverage.yaml")
sys.path.insert(0, TOOLS)

MARK = "THE EDGE RATES ARE DATA"
OLD_REM = ('",\n   remediation: {action: "decision 39 rules the criterion k as a declared calibration (21 September 2026), so '
           'the whole of what is left is an edge rate for the classes whose drivers publish none')
OLD_TAIL = ('A direct question to a vendor is the only shortcut and nobody has asked one", owner: LAB, execution: HARDWARE, '
            'depends_on: [],')
NEW_REM = ('",\n   remediation: {action: "since the edge rates became data (27 September 2026, stream w5si) what is left is'
           ' of two kinds. DESK: a schematic answer for each layout-bound net that has one (an impedance target, a series'
           ' termination at the driver, a firmware obligation that slows the driver), a signal-class declaration for each'
           ' net that carries none, and the two rules this stream\'s findings propose (a power-stage layout rule, F-Q1, and'
           ' a class for the cable side of an isolation barrier, F-BOB). BENCH OR MAKER: for every net a bound decides,'
           ' the edge of the driver that publishes none, from the maker\'s IBIS model where one exists and this host could'
           ' not fetch it (Nexperia, Diodes, Microchip, Winbond: a browser fetch) or from an oscilloscope at bring-up, which'
           ' is why the owner stays LAB and the execution HARDWARE. Asking a maker for a model it does not publish is'
           ' outside contact and is the owner\'s to send", owner: LAB, execution: HARDWARE, depends_on: [],')


def readings():
    """[(letter, netlist sha256/16, counts)] taken in memory on the tree's declared netlists; nothing is written."""
    import edge_length as E, phase_artefacts as PA
    assert not E.RATES_REFUSALS, "the data file refuses records: %s" % E.RATES_REFUSALS[:3]
    out = []
    for L in "abcdep":
        net = PA.netlist(L, os.path.join(ROOT, "v2", "ecad"))
        assert net and os.path.exists(net), "board %s has no declared netlist in this tree" % L
        r = E.schematic_table(net, L)
        assert not r.get("missing_input"), (L, r.get("missing_input"))
        c = r["counts"]
        assert c["signal_nets"] == c["low_speed_nets"] + c["decided_nets"] + c["undecided_nets"] + c["contradicted_nets"], (L, c)
        assert c["decided_nets"] == c["maker_edge_nets"] + c["bound_edge_nets"], (L, c)
        assert c["layout_bound_nets"] == c["maker_held_nets"] + c["bound_decided_nets"], (L, c)
        assert c["may_be_long_nets"] == c["answered_nets"] + c["layout_bound_nets"], (L, c)
        out.append((L, r["inputs"]["netlist"]["sha256_16"], c, E.schematic_result(r), bool(r["fails"])))
    return out, E.RATES.get("sha16")


def paragraph(rd, sha):
    per = lambda f: ", ".join("%s %s" % (L.upper(), f(c)) for L, _s, c, _v, _f in rd)
    tot = lambda k: sum(c[k] for _L, _s, c, _v, _f in rd)
    non = tot("signal_nets") - tot("low_speed_nets")
    assert non == tot("maker_edge_nets") + tot("bound_edge_nets") + tot("undecided_nets") + tot("contradicted_nets")
    verdicts = sorted({v for _L, _s, _c, v, _f in rd})
    text = (
        "\n     27 September 2026 (stream w5si, MESHSAT-1357, layer 9, second pass after an independent check): " + MARK + "."
        " tools/pcb_edge_rates.yaml (sha256/16 " + str(sha) + " when this paragraph was written), a configuration input of the"
        " edge_length verdict, holds every edge the reading uses. Each record carries its document with the sha256/16 of the"
        " held file, the page or the IBIS keyword, the words or the cell quoted, its conditions, its applicability and the"
        " verification owed, and the tool checks all of it on every run. ONLY A PUBLISHED MINIMUM IS A MAKER'S FIGURE: a"
        " maker's IBIS model at its fastest corner (13 models filed under v2/vendor/ti/ibis and v2/vendor/st/ibis), a"
        " minimum the maker prints in its own table, or a specification's minimum that the part's own datasheet claims; a"
        " typical or a maximum is refused; where a maker publishes none the instantaneous bound stands in and is named a"
        " bound. THE GOVERNING EDGE of a net is the fastest any driver on it can produce, so ONE driver with no published"
        " minimum makes the net decided by a bound, whatever the other drivers' makers publish. An open-drain net has two"
        " edges: its fall is the driver's and governs, its rise is the pull-up's and is stated beside it. Counts on the"
        " declared netlists of this tree, per board, taken in memory when this paragraph was written (netlists " +
        ", ".join("%s %s" % (L.upper(), s) for L, s, _c, _v, _f in rd) + "): signal nets outside LOW_SPEED_OR_DC " +
        per(lambda c: c["signal_nets"] - c["low_speed_nets"]) + " (" + str(non) + " in all); of them decided by a maker's"
        " figure on every driver " + per(lambda c: c["maker_edge_nets"]) + " (" + str(tot("maker_edge_nets")) + "), decided by a"
        " bound " + per(lambda c: c["bound_edge_nets"]) + " (" + str(tot("bound_edge_nets")) + "), undecided " +
        per(lambda c: c["undecided_nets"]) + " (" + str(tot("undecided_nets")) + ", the nets no signal-class declaration names)."
        " Of the decided, answered in the netlist " + per(lambda c: c["answered_nets"]) + " (" + str(tot("answered_nets")) +
        ") and layout-bound " + per(lambda c: c["layout_bound_nets"]) + " (" + str(tot("layout_bound_nets")) + "); of the"
        " layout-bound, held by a maker's figure on every driver " + per(lambda c: c["maker_held_nets"]) + " (" +
        str(tot("maker_held_nets")) + ") and decided by a bound, BOUND_DECIDES, " + per(lambda c: c["bound_decided_nets"]) +
        " (" + str(tot("bound_decided_nets")) + "). Every reading is " + " or ".join(verdicts) + "; none is a PASS, and a"
        " board stays INCONCLUSIVE wherever a bound decides a net whose length is the layout's. The nets, the drivers that"
        " govern them and the ones that carry a maker's figure beside a bound are listed per board in"
        " v2/docs/records/w5si/readings/. Two findings go with it: the power-stage nodes (gate, bootstrap and switch nodes)"
        " are asked the wrong question by this rule and no rule asks the right one"
        " (v2/docs/records/w5si/F-Q1-power-stage-nodes.md), and board B's BOB is a common-mode termination that no signal"
        " class fits (v2/docs/records/w5si/F-BOB-common-mode-termination.md). Session decisions ER-D1 to ER-D15 are in the"
        " data file's header.")
    assert '"' not in text and "\\" not in text, "the paragraph would break the quoted string it is put in"
    return text


def main():
    import yaml
    s = open(TARGET, encoding="utf-8").read()
    before = yaml.safe_load(s)
    a = s.index("\n SI-001: {")
    b = s.index("\n CLK-001: {", a)
    rec = s[a:b]
    assert MARK not in rec, "already applied"
    assert rec.count(OLD_REM) == 1, "SI-001's remediation no longer opens as written: re-read the record"
    i = rec.index(OLD_REM)
    j = rec.index(OLD_TAIL, i)
    rd, sha = readings()
    para = paragraph(rd, sha)
    rec2 = rec[:i] + para + NEW_REM + rec[j + len(OLD_TAIL):]
    out = s[:a] + rec2 + s[b:]
    assert out != s
    d = yaml.safe_load(out)
    # THE STRUCTURE, before against after
    assert set(d) == set(before) and set(d["coverage"]) == set(before["coverage"]), "a record was added or lost"
    for k in before:
        if k != "coverage": assert d[k] == before[k], "the top-level key %s changed" % k
    for k, v in before["coverage"].items():
        if k != "SI-001": assert d["coverage"][k] == v, "record %s changed and was not to" % k
    old, new = before["coverage"]["SI-001"], d["coverage"]["SI-001"]
    assert set(old) == set(new)
    for k in old:
        if k not in ("note", "remediation"): assert new[k] == old[k], "SI-001's %s changed" % k
    assert new["note"].startswith(old["note"]) and MARK in new["note"][len(old["note"]):], "the note is not the old note with the paragraph after it"
    assert set(old["remediation"]) == set(new["remediation"])
    for k in old["remediation"]:
        if k != "action": assert new["remediation"][k] == old["remediation"][k], "the remediation's %s changed" % k
    assert new["remediation"]["action"] != old["remediation"]["action"]
    assert new["remediation"]["owner"] == "LAB" and new["remediation"]["execution"] == "HARDWARE"
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: SI-001's note would gain %d characters and its remediation's action would change" % (
            len(new["note"]) - len(old["note"])))
        print(new["note"][len(old["note"]):].strip())
        return
    open(TARGET, "w", encoding="utf-8").write(out)
    print("pcb_rules_coverage.yaml SI-001: note extended by %d characters, remediation's action replaced, owner and execution kept" % (
        len(new["note"]) - len(old["note"])))


if __name__ == "__main__":
    main()
