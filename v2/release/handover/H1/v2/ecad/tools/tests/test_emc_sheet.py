#!/usr/bin/env python3
"""Source, path, victim, and the completeness that makes it a gate (rule EMC-001, 16 September 2026).

EMC-001 asks for an EMC sheet per board and read "no verification" on six of them. The sheet is data now, and
the check that makes it more than prose is the first one below: a sheet that lists thirteen of a board's
fourteen converters is worse than no sheet, because it reads as complete. The part list comes from the board's
own netlist by part number.

The gate found its own two defects on the first run: the sheet named `J_LORA` and `J_SA1` as victims and those
references do not exist; the parts are `U12`, an SX1262 module, and `U2`, the SA868 exciter.
"""
import os, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import emc_sheet as E


def _tree(comps):
    d = tempfile.mkdtemp(prefix="emc-")
    prj = os.path.join(d, "pcb-x-test"); os.makedirs(os.path.join(prj, "out"))
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    open(os.path.join(prj, "out", "pcb-x-test.net"), "w").write(
        "(export (version E)\n  (components\n%s  )\n  (nets\n  )\n)\n" % c)
    return d


def _sheet(d, body):
    p = os.path.join(d, "emc.yaml"); open(p, "w").write(body); return p


GOOD = """
schema_version: "1.0.0"
boards:
 x:
   title: test
   sources:
    - {ref: U1, part: AP64500, what: "a buck", f_khz: 500, basis: "v2/vendor/diodes/diodes-ap64500.pdf"}
   victims:
    - {what: "a receiver", refs: [U9], why: "it listens"}
   paths:
    - {from: "the switch node", to: "the receiver", mechanism: "coupling", measure: "a filter", evidence: "the schematic"}
   pre_compliance: ["a scan"]
"""


def _run(sheet, comps, facts_stem="pcb-x-test"):
    d = _tree(comps)
    import rules_lib as R
    keep = R.board_facts
    try:
        R.board_facts = lambda *a, **k: {"x": {"project": facts_stem}}
        return E.judge(_sheet(d, sheet), d, "x")["x"]
    finally:
        R.board_facts = keep


def t_an_undeclared_converter_is_a_failure():
    """THE DEFECTIVE FIXTURE and the reason this is a gate: the board has two bucks and the sheet lists one."""
    r = _run(GOOD, {"U1": "AP64500SP-13 5 A buck", "U2": "TPS62933DRLR buck", "U9": "a receiver"})
    assert any("U2" in f and "does not declare it" in f for f in r["fails"]), r["fails"]


def t_the_same_sheet_with_both_declared_passes():
    sheet = GOOD.replace('   victims:',
                         '    - {ref: U2, part: TPS62933, what: "another buck", f_khz: 500, basis: "RT open, 500 kHz"}\n   victims:')
    r = _run(sheet, {"U1": "AP64500SP-13 5 A buck", "U2": "TPS62933DRLR buck", "U9": "a receiver"})
    assert not r["fails"], r["fails"]


def t_a_victim_or_source_the_netlist_does_not_have_is_refused():
    """The gate's own first finding: two victims named by references that do not exist."""
    r = _run(GOOD, {"U1": "AP64500SP-13 5 A buck"})
    assert any("U9" in f and "victim" in f for f in r["fails"]), r["fails"]


def t_a_board_with_no_source_must_say_why():
    sheet = GOOD.replace("""   sources:
    - {ref: U1, part: AP64500, what: "a buck", f_khz: 500, basis: "v2/vendor/diodes/diodes-ap64500.pdf"}""", "   sources: []")
    r = _run(sheet, {"U9": "a receiver"})
    assert any("does not say why" in f for f in r["fails"]), r["fails"]


def t_a_path_without_a_measure_or_its_evidence_is_refused():
    for k in ("measure", "evidence"):
        sheet = GOOD.replace('%s: "%s"' % (k, {"measure": "a filter", "evidence": "the schematic"}[k]), '%s: ""' % k)
        r = _run(sheet, {"U1": "AP64500SP-13 5 A buck", "U9": "a receiver"})
        assert any(("carries no %s" % k) in f for f in r["fails"]), (k, r["fails"])


def t_a_board_without_a_pre_compliance_plan_is_refused():
    """The paper half of this rule cannot close the measurement half and must not look as though it has."""
    sheet = GOOD.replace('   pre_compliance: ["a scan"]', "   pre_compliance: []")
    r = _run(sheet, {"U1": "AP64500SP-13 5 A buck", "U9": "a receiver"})
    assert any("pre-compliance" in f for f in r["fails"]), r["fails"]


def t_the_committed_sheet_passes_on_every_board():
    r = E.judge()
    fails = [f for v in r.values() for f in v["fails"]]
    assert not fails, fails
    assert len(r) == 7, sorted(r)
    assert sum(v["sources"] for v in r.values()) >= 27, r
