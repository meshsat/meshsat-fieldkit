"""Layer 9 record l9pwr (MESHSAT-1357, 3 October 2026; v2/docs/records/l9pwr/): item 9.1, the power budget brought to the
current design with margins and sensitivities, held as predicates on what l9pwr_budget.py computes.

The predicates: the committed .out is what the script prints and every pinned input is present at the sha256 the output names;
the script's evaluator reproduces record rv-pwr's model on rv-pwr's own tree (to 1e-9 W) and rv-pwr's committed headline table;
each reconciliation line with Layer 4 (L4-E9's modes, the review's and L4-E12's B4 and B7, L4-E11's VSYS_E declaration and the
battery FET pair's loss, L4-E12's fans' share and heat stage, Layer 7's fan heat, l8r2's choice (a), rv-pwr's D-11 margin on main)
reproduces the other record's figure from its own inputs; the drafts are labelled DRAFTED and the waterfall runs from RV to
DRAFTED; D-11's all-transmit floor holds on the drawn tree and fails on the drafted one (finding L9P-F01); the findings carry a
class among the owner's three and an owner; the page carries the output's figures; the record's files carry no long dashes, no
claim words and no private path. These are software predicates on the record's own arithmetic: they establish no property of
any board, converter, fan or pack, and nothing here is measured.
"""
import hashlib
import importlib.util
import os
import re
import shutil
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l9pwr")
SCRIPT = os.path.join(REC, "l9pwr_budget.py")
OUT = os.path.join(REC, "l9pwr_budget.out")
PAGE = os.path.join(REC, "L9-POWER-BUDGET.md")
README = os.path.join(REC, "README.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l9pwr record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l9pwr_budget_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for rel in m.PINS.values():
            need(os.path.join(ROOT, rel), "a pinned input of the l9pwr record")
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l9pwr_budget.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def _pred(key):
    _M()
    P = _C["R"]["pred"]
    assert key in P, "no predicate %r" % key
    return P[key]


def _rec(rid):
    _M()
    for r in _C["R"]["rec"]:
        if r["id"] == rid:
            return r
    raise AssertionError("no reconciliation line %s" % rid)


def t_output_reproduced_byte_for_byte():
    _M()
    need(OUT, "the committed output")
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l9pwr_budget.out is not what the script prints"


def t_every_input_is_pinned_and_present():
    m = _M()
    for key, rel in m.PINS.items():
        sha = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        assert ("%s  sha256 %s" % (rel, sha[:16])) in _C["text"], "%s is not pinned at its current sha256" % rel


def t_the_evaluator_reproduces_rv_pwr():
    assert _pred("this evaluator reproduces rv-pwr on its own tree within 1e-9 W")
    assert _pred("rv-pwr's committed headline table equals this evaluator at 0.1 W")
    assert _C["R"]["check_worst"] < 1e-9


def t_the_reconciliation_lines_with_layer_4():
    """Each line reproduces the other record's figure from its own inputs; the current design's figure beside it."""
    for rid in ("R1", "R1b", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10"):
        assert _pred("reconciliation %s: Layer 4's figure reproduced from its own inputs" % rid), rid
    r = _rec("R2")
    assert r["theirs"][2] == 50.043663 and r["repro"][2] == 50.043663, "B4: the review's 50.043663 W"
    assert r["ballast"][1] == 52.133663 and r["ballast"][2] == 52.133663
    r = _rec("R3")
    assert r["theirs"][1] == 2.06349 and r["repro"][1] == 2.06349, "B7: the review's 2.06349 h"
    assert r["repro"][2] == 54.467
    r = _rec("R4")
    assert r["theirs"][0] == 1.3208 and r["repro"][0] == 1.3208, "L4-E11's VSYS_E 1.3208 A"
    assert r["repro"][2] == 89.8
    r = _rec("R1")
    assert r["repro"] == (42.8, 203.8, 272.0, 162.3)
    # the current design moves them, and the waterfall carries the difference step by step
    R = _C["R"]
    for st in ("IDLESPEC", "ALLTX"):
        steps = [R["wf"][i][st] - R["wf"][i - 1][st] for i in range(1, len(R["wf"]))]
        assert abs(sum(steps) - (R["wf"][-1][st] - R["wf"][0][st])) < 1e-9
    assert R["rec"][0]["cur"]["DRAFTED"][0] > 42.8


def t_drafts_are_drafted_and_the_trees_are_ordered():
    assert _pred("every drafted node and row is labelled DRAFTED")
    assert _pred("the waterfall's last step is DRAFTED and its first RV, on every state")
    assert _pred("DRAFTED's PLAN is above DRAWN's in every state")
    assert _pred("DRAWN's PLAN is above RV's in every state but PS-EMCON, where the link cards are unpowered")
    m = _M()
    st = [s[1] for s in m.STEP_TEXT]
    assert st[0] == "RV" and set(st[1:6]) == {"ON MAIN"} and set(st[6:]) == {"DRAFTED"}
    for sid, status, tx in m.STEP_TEXT[6:]:
        assert "not applied" in tx, "%s does not say it is not applied" % sid


def t_margins_and_findings():
    assert _pred("D-11's all-transmit floor holds on RV and DRAWN and fails on DRAFTED")
    assert _pred("D-11's PA-alone floor holds on every tree")
    assert _pred("no converter is over its limit at PLAN in any state, DRAWN or DRAFTED")
    assert _pred("every margin finding has a class among the instruction's three and an owner")
    assert _pred("the findings are L9P-F01 to L9P-F06")
    F = {x["id"]: x for x in _C["R"]["classified"]}
    assert F["L9P-F01"]["class"] == "DEMONSTRATED ANALYSIS DEFECT" and "L4-E9" in F["L9P-F01"]["owner"]
    assert F["L9P-F04"]["class"] == "PHYSICAL QUESTION" and "specimen" in F["L9P-F04"]["action"]
    for k in ("L9P-F02", "L9P-F03", "L9P-F05", "L9P-F06"):
        assert F[k]["class"] == "ASSUMPTION TO BOUND", k


def t_sensitivities_cover_every_state():
    m = _M()
    S = _C["R"]["sens"]
    assert set(S) == set(m.STATES)
    for st, v in S.items():
        assert len(v["top"]) == 5, st
        sw = [abs(r[3] - r[2]) for r in v["top"]]
        assert sw == sorted(sw, reverse=True), st
        assert len(v["assumptions"]) >= 4, st
    C = _C["R"]["curves"]
    assert C["vs"][0] == 12.0 and C["vs"][-1] == 16.8


def t_the_page_carries_the_outputs_figures():
    _M()
    R = _C["R"]
    need(PAGE, "the page")
    page = open(PAGE, encoding="utf-8").read()
    for st in ("IDLESPEC", "TYP", "BUSY", "ALLTX", "SURVR"):
        t = R["tot"][("DRAFTED", st)]
        s = "%.2f / %.2f / %.2f" % (t["lo"]["pb"], t["plan"]["pb"], t["hi"]["pb"])
        assert s in page, "the page does not carry %s's DRAFTED %s" % (st, s)
    for s in ("50.043663", "2.06349", "1.3208", "L9P-F01", "L9P-F06", "%.2f V" % R["d11"]["DRAFTED"]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"]["V_rest"]["hi"]):
        assert s in page, "the page does not carry %r" % s
    need(README, "the README")
    rd = open(README, encoding="utf-8").read()
    assert "9.1" in rd and "LAYER-STATUS" in rd


def t_record_hygiene_no_long_dashes_no_claim_words_no_private_paths():
    files = [SCRIPT, OUT, PAGE, README, os.path.abspath(__file__)]
    for p in files:
        need(p, os.path.basename(p))
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        if p != os.path.abspath(__file__):
            m = CLAIM.search(t)
            assert not m, "a claim word %r in %s" % (m.group(0), os.path.basename(p))
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
