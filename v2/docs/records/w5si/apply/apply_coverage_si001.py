#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, RE-ISSUED 28 September 2026 by stream w5si2,
MESHSAT-1357, layer 9): SI-001's coverage record says what the reading now is. pcb_rules_coverage.yaml is the integrator's; this script makes the change and the
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

RE-ISSUED on the drafts check's B2 (AI review, 28 September 2026). The draft of 27 September wrote two sentences that
were typed and not read: "13 models filed under v2/vendor/ti/ibis and v2/vendor/st/ibis", and, of EVERY undecided net,
"the nets no signal-class declaration names". With the models withheld it exited 0 and would have written both, false:
of 470 undecided nets 73 had that reason and 397 waited on a model that was not in the tree. NOW NOTHING THE PARAGRAPH
SAYS OF THE READINGS IS TYPED: the number of models comes from the manifest, THE STATE THE MODELS WERE IN comes from the
readings (inputs.model_state) and is written into the paragraph, the undecided nets are counted by the KIND of their
reason as the tool set it (no declaration, a model that is not in the tree, other), and the nets decided by a
published figure are counted by what the figure is (a maker's IBIS model, a specification's class record, a minimum
the maker prints), which the draft of 27 September called "a maker's figure" for all 138 where 64 were the USB 2.0
records (M7). What it prints says that PCB-GOLDEN-RULES.md and PCB-GAP-REGISTER.md are owed a re-render (M2).

HOW: the record is found by its id; the old remediation text is asserted; the new text is parsed and COMPARED WITH THE
OLD ONE AS STRUCTURE before anything is written: every other record unchanged, and in SI-001 every key unchanged but
`note`, which must be the old note with the paragraph after it, and `remediation.action`. A second run is refused.

Applied by the integrator on the integrated tree (after set 6), with the data file and the manifest committed; the
models are never committed, and the paragraph says which state they were in when it was written:
    python3 v2/docs/records/w5si/apply/apply_coverage_si001.py [--root <tree>] [--dry-run]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _apply as AP

ROOT = AP.root_of(HERE) if "--root" not in sys.argv or sys.argv.index("--root") + 1 < len(sys.argv) else os.path.abspath(".")
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
        assert c["undecided_nets"] == c["undecided_no_declaration_nets"] + c["undecided_model_absent_nets"] + c["undecided_other_nets"], (L, c)
        assert not r["fails"], "board %s's reading FAILS, and a coverage note is not written over a failing reading: %s" % (L.upper(), r["fails"][:2])
        c = dict(c)
        # by what a published figure is, and the kinds of the undecided as the tool set them (never read from words)
        for row in r["rows"]:
            for e in (row.get("net_edges") or {}).values():
                if e["decided_by"] == "MAKER": c["by_" + e["basis"]] = c.get("by_" + e["basis"], 0) + 1
        assert sum(v for k, v in c.items() if k.startswith("by_")) == c["maker_edge_nets"], (L, c)
        kinds = [k for row in r["rows"] for k in (row.get("undecided_kind") or {}).values()]
        assert len(kinds) == c["undecided_nets"] and kinds.count("MODEL_ABSENT") == c["undecided_model_absent_nets"], (L, c)
        ms = r["inputs"]["model_state"]
        assert ms["state"] != "DIFFERS", "board %s read a model that is not the file the manifest pins" % L.upper()
        out.append((L, r["inputs"]["netlist"]["sha256_16"], c, E.schematic_result(r), ms))
    return out, E.RATES.get("sha16")


def models(rd):
    """(the words for the state the models were in, the manifest's path, how many it pins): read from the readings and
    the manifest of this tree."""
    import ibis_manifest as IM
    man = IM.load(ROOT)
    assert not man["why"] and not man["refusals"], "the manifest does not stand: %s %s" % (man["why"], man["refusals"][:2])
    asked = sorted({f for _L, _s, _c, _v, ms in rd for f in ms.get("absent_files") or []})
    states = [ms["state"] for _L, _s, _c, _v, ms in rd if ms["state"] != "NOT_ASKED"]
    here = [IM.state_of(ROOT, r)[0] for r in man["models"].values()]
    assert IM.DIFFERS not in here, "a model in this tree is not the file the manifest pins"
    if not asked and all(x == "PRESENT" for x in states):
        words = ("PRESENT: every model a reading asked for was in the tree and was the file pinned (%d of the %d the manifest "
                 "pins were in the tree)" % (here.count(IM.PRESENT), len(here)))
    else:
        words = ("%s: %d model(s) a reading asked for were NOT in the tree (%s), so every net that waits on one reads UNDECIDED, "
                 "naming it, and the counts below are those of a tree without them; with the models fetched "
                 "(tools/ibis_fetch.py) those nets are decided and this paragraph is superseded by the re-taken readings"
                 % ("ABSENT" if not here.count(IM.PRESENT) else "PARTIAL", len(asked), ", ".join(os.path.basename(f) for f in asked)))
    return words, man["path"], len(man["models"]), bool(asked)


def paragraph(rd, sha):
    per = lambda f: ", ".join("%s %s" % (L.upper(), f(c)) for L, _s, c, _v, _f in rd)
    tot = lambda k: sum(c.get(k, 0) for _L, _s, c, _v, _f in rd)
    state, manifest, pinned, absent = models(rd)
    figures = [("a maker's IBIS model", tot("by_IBIS")), ("a specification's class record, the USB 2.0 minimums", tot("by_STANDARD")),
               ("a minimum the maker prints in its own table", tot("by_DATASHEET"))]
    assert sum(n for _w, n in figures) == tot("maker_edge_nets"), figures
    by_what = ", ".join("%d by %s" % (n, w) for w, n in figures if n) or "none"
    kinds = [("with no signal-class declaration", tot("undecided_no_declaration_nets")),
             ("waiting only on a model that is not in the tree", tot("undecided_model_absent_nets")),
             ("for another reason, named per net in the reading", tot("undecided_other_nets"))]
    assert sum(n for _w, n in kinds) == tot("undecided_nets"), kinds
    by_kind = ", ".join("%d %s" % (n, w) for w, n in kinds if n) or "none"
    non = tot("signal_nets") - tot("low_speed_nets")
    assert non == tot("maker_edge_nets") + tot("bound_edge_nets") + tot("undecided_nets") + tot("contradicted_nets")
    verdicts = sorted({v for _L, _s, _c, v, _f in rd})
    text = (
        "\n     28 September 2026 (streams w5si and w5si2, MESHSAT-1357, layer 9, after two AI reviews, neither a qualified"
        " engineering review): " + MARK + "."
        " tools/pcb_edge_rates.yaml (sha256/16 " + str(sha) + " when this paragraph was written), a configuration input of the"
        " edge_length verdict, holds every edge the reading uses. Each record carries its document with the sha256/16 of the"
        " held file, the page or the IBIS keyword, the words or the cell quoted, its conditions, its applicability and the"
        " verification owed, and the tool checks all of it on every run. ONLY A PUBLISHED MINIMUM IS A MAKER'S FIGURE: a"
        " maker's IBIS model at its fastest corner, a"
        " minimum the maker prints in its own table, or a specification's minimum that the part's own datasheet claims; a"
        " typical or a maximum is refused; where a maker publishes none the instantaneous bound stands in and is named a"
        " bound; a pin whose [Ramp] cell the model's own V-t table contradicts has no figure and takes the bound. THE MODELS"
        " ARE NOT IN THE REPOSITORY: " + manifest + " pins " + str(pinned) + " of them by the sha256 of the extracted file,"
        " tools/ibis_fetch.py fetches them from the makers' own addresses, and a model that is not in the tree decides"
        " nothing. THE STATE OF THE MODELS WHEN THESE COUNTS WERE TAKEN: " + state + ". THE GOVERNING EDGE of a net is the fastest any driver on it can produce, so ONE driver with no published"
        " minimum makes the net decided by a bound, whatever the other drivers' makers publish. An open-drain net has two"
        " edges: its fall is the driver's and governs, its rise is the pull-up's and is stated beside it. Counts on the"
        " declared netlists of this tree, per board, taken in memory when this paragraph was written (netlists " +
        ", ".join("%s %s" % (L.upper(), s) for L, s, _c, _v, _f in rd) + "): signal nets outside LOW_SPEED_OR_DC " +
        per(lambda c: c["signal_nets"] - c["low_speed_nets"]) + " (" + str(non) + " in all); of them decided by a published"
        " figure on every driver " + per(lambda c: c["maker_edge_nets"]) + " (" + str(tot("maker_edge_nets")) + ": " + by_what +
        "), decided by a bound " + per(lambda c: c["bound_edge_nets"]) + " (" + str(tot("bound_edge_nets")) + "), undecided " +
        per(lambda c: c["undecided_nets"]) + " (" + str(tot("undecided_nets")) + ": " + by_kind + ")."
        " Of the decided, answered in the netlist " + per(lambda c: c["answered_nets"]) + " (" + str(tot("answered_nets")) +
        ") and layout-bound " + per(lambda c: c["layout_bound_nets"]) + " (" + str(tot("layout_bound_nets")) + "); of the"
        " layout-bound, held by a published figure on every driver " + per(lambda c: c["maker_held_nets"]) + " (" +
        str(tot("maker_held_nets")) + ") and decided by a bound, BOUND_DECIDES, " + per(lambda c: c["bound_decided_nets"]) +
        " (" + str(tot("bound_decided_nets")) + "). Every reading is " + " or ".join(verdicts) + "; none is a PASS, and a"
        " board stays INCONCLUSIVE wherever a bound decides a net whose length is the layout's. The nets, the drivers that"
        " govern them and the ones that carry a maker's figure beside a bound are listed per board in"
        " v2/docs/records/w5si/readings/ and v2/docs/records/w5si2/readings/. Two findings go with it: the power-stage nodes (gate, bootstrap and switch nodes)"
        " are asked the wrong question by this rule and no rule asks the right one"
        " (v2/docs/records/w5si/F-Q1-power-stage-nodes.md), and board B's BOB is a common-mode termination that no signal"
        " class fits (v2/docs/records/w5si/F-BOB-common-mode-termination.md). Session decisions ER-D1 to ER-D17 are in the"
        " data file's header.")
    assert '"' not in text and "\\" not in text, "the paragraph would break the quoted string it is put in"
    assert "\u2014" not in text and "\u2013" not in text
    return text, state, absent


def main():
    import yaml
    AP.need_stream(ROOT)
    AP.need(os.path.exists(TARGET), "v2/ecad/tools/pcb_rules_coverage.yaml is not in the tree %s" % ROOT)
    s = open(TARGET, encoding="utf-8").read()
    before = yaml.safe_load(s)
    AP.need(s.count("\n SI-001: {") == 1, "pcb_rules_coverage.yaml does not hold the record SI-001 once, as this draft read it")
    a = s.index("\n SI-001: {")
    nxt = s.find("\n CLK-001: {", a)
    AP.need(nxt != -1, "the record after SI-001 is no longer CLK-001, by which this draft finds SI-001's end: re-read the file")
    b = nxt
    rec = s[a:b]
    AP.need(MARK not in rec, "already applied")
    assert rec.count(OLD_REM) == 1, "SI-001's remediation no longer opens as written: re-read the record"
    i = rec.index(OLD_REM)
    j = rec.index(OLD_TAIL, i)
    rd, sha = readings()
    para, state, absent = paragraph(rd, sha)
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
    owed = ("  THE MODELS WHEN THE COUNTS WERE TAKEN: %s\n"
            "  OWED after this draft: `rules_render.py`, because v2/docs/PCB-GOLDEN-RULES.md and v2/docs/PCB-GAP-REGISTER.md are rendered "
            "from this file and are out of date until they are rendered again (`rules_render.py --check` says which)%s" % (
                state, "\n  AND: this paragraph was written WITHOUT the models. It says so. When the models are in the tree and SI-001 is "
                       "re-taken, the paragraph's counts are those of another state: say so in the record that re-takes" if absent else ""))
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: SI-001's note would gain %d characters and its remediation's action would change\n%s" % (
            len(new["note"]) - len(old["note"]), owed))
        print(new["note"][len(old["note"]):].strip())
        return 0
    AP.write(TARGET, out)
    assert yaml.safe_load(open(TARGET, encoding="utf-8").read()) == d, "the file read back is not the text that was written"
    print("pcb_rules_coverage.yaml SI-001: note extended by %d characters, remediation's action replaced, owner and execution kept\n%s" % (
        len(new["note"]) - len(old["note"]), owed))
    return 0


if __name__ == "__main__":
    AP.run(main)
