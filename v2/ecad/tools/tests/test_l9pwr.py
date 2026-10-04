"""Layer 9 record l9pwr (MESHSAT-1357, 3 October 2026, round 2 on 4 October 2026; v2/docs/records/l9pwr/): item 9.1, the power
budget brought to the current design with margins and sensitivities, held as predicates on what l9pwr_budget.py computes.

Round 2: the DRAFTED tree carries record l8r2's round 6 drafts (fnd/l8r3 at 89924e40) and record l9stk's section 15 (fnd/l9stk at
2c8b29fb) from copies in inputs/; each copy must equal git show of its source where the commit is present. Round 1's DRAFTED tree
is rebuilt beside it and reproduces what L4-E9 round 7 and record l8r2 took from round 1.

The predicates: the committed .out is what the script prints and every pinned input is present at the sha256 the output names;
the script's evaluator reproduces record rv-pwr's model on rv-pwr's own tree (to 1e-9 W) and rv-pwr's committed headline table;
each reconciliation line with Layer 4 (L4-E9's modes, the review's and L4-E12's B4 and B7, L4-E11's VSYS_E declaration and the
battery FET pair's loss, L4-E12's fans' share and heat stage, Layer 7's fan heat, rv-pwr's D-11 margin on main, L4-E9 round 7's
modes and D-17 floor) and with records l8r2 (round 6's slot envelope) and l9stk (the breaker and the third FET) reproduces the
other record's figure from its own inputs; the drafts are labelled DRAFTED and the waterfall runs from RV to DRAFTED; D-11's
all-transmit floor holds on the drawn tree and fails on the drafted one, and round 7's 16.1 V covers round 1's drafts and not
round 2's (finding L9P-F01); slots 1 and 3 sit within their LM5176 loop (L9P-F02 resolved in the drafts); the findings carry a
class among the owner's three and an owner; the page carries the output's figures; the record's files carry no long dashes, no
claim words and no private path. These are software predicates on the record's own arithmetic: they establish no property of
any board, converter, fan or pack, and nothing here is measured.

Round 3 (4 October 2026, the integration of set 29): a rail's declaration and the battery FETs are parsed from L4-E11's drafts,
not matched by a one-line pattern (the defect: L4-E11's round 9 broke +12V_FAN's declaration over two lines and the pattern
for its efficiency refused), which fixtures hold both ways; record l9stk's protection output is read from this tree, and the
breaker's variant is the one that output selects.
"""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l9pwr")
INPUTS = os.path.join(REC, "inputs")
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


def t_every_copy_in_inputs_equals_its_source():
    """Each copy in inputs/ is git show of its source at the commit its name carries (whole, or the lines ORIGIN names), where the
    commit is present in this checkout; the script pins each copy and SOURCES.txt names it with its sha256."""
    m = _M()
    assert _pred("every copy in inputs/ is pinned and named with its sha256 in SOURCES.txt")
    if shutil.which("git") is None:
        raise Skip("git is needed")
    seen = 0
    for key, (branch, commit, src, lines) in m.ORIGIN.items():
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, src)], capture_output=True)
        if r.returncode != 0:
            continue
        body = r.stdout
        if lines is not None:
            body = b"".join(body.splitlines(keepends=True)[lines[0] - 1:lines[1]])
        assert open(os.path.join(ROOT, m.PINS[key]), "rb").read() == body, "%s is not %s at %s" % (m.PINS[key], src, commit)
        seen += 1
    if not seen:
        raise Skip("none of the source commits is in this checkout")


def t_a_drafts_rail_and_battery_fets_are_parsed_not_matched_on_one_line():
    """The defect of 4 October 2026: a pattern that wanted `_intent.rail("+12V_FAN", ...` and its efficiency on one source line
    refused when L4-E11's round 9 broke the declaration over two. The call is now parsed out of the draft's string constants;
    one line or two read the same, and a draft that writes the rail twice, differently, refuses."""
    m = _M()
    one = '_intent.rail("+12V_X", 12.0, 0.34, 0.34, "L4", always_on=True, converted=True, efficiency=0.85, fed_from="VSYS_E")'
    two = ('_intent.rail("+12V_X", 12.0, 0.34, 0.34, "U22", source_ic="U22 VOUT (its switches are inside the IC) "\n'
           '             "and L4 is not on the rail", always_on=True, converted=True, efficiency=0.85, fed_from="VSYS_E")')
    old = re.compile(r'_intent\.rail\(\\?"\+12V_X\\?", [^\n]*?efficiency=([\d.]+)')        # the round 2 pattern, the defect's witness
    tdir = tempfile.mkdtemp(prefix="t_l9pwr_")
    tmp = os.path.join(tdir, "draft_fixture.py")      # an absolute path: the script's path() joins it to the root unchanged
    seen = {}
    try:
        for name, body in (("one", one), ("two", two), ("twice", one + "\n" + two.replace("0.85", "0.80"))):
            # the draft's form: each generator line is its own string literal on its own source line
            draft = "_A = (" + "\n      ".join(repr(x + "\n") for x in ["# a generator comment"] + body.split("\n")) + ")\n"
            open(tmp, "w", encoding="utf-8").write(draft)
            m.PINS["_fixture"] = tmp
            if name == "twice":
                try:
                    m.draft_rail_call("_fixture", "+12V_X")
                except SystemExit:
                    continue
                raise AssertionError("two differing declarations of one rail were read as one")
            got = m.draft_rail_call("_fixture", "+12V_X")
            seen[name] = (got["pos"][1], got["pos"][4], got["kw"]["efficiency"], got["kw"]["fed_from"], bool(old.search(draft)))
        # the battery FETs: the nfet calls on the battery nets, whatever the loop's form or the part's sentence
        nets = '"CH_BATDRV", "CH_BATQ", "VBAT", fp="LFPAK56")'
        forms = {"loop": 'for _qb in ("Q39", "Q40", "QX"): nfet(_qb, "BUK6Y10-30PX (one of three in parallel)", ' + nets,
                 "renamed": 'for _q in ("Q39", "Q40", "QX"): nfet(_q, "BUK6Y10-30PX, side by side", ' + nets,
                 "singles": "; ".join('nfet("%s", "BUK6Y10-30PX", %s' % (q, nets) for q in ("Q39", "Q40", "QX")),
                 "pair": 'for _qb in ("Q39", "Q40"): nfet(_qb, "BUK6Y10-30PX (one of two in parallel)", ' + nets}
        for name, body in sorted(forms.items()):
            open(tmp, "w", encoding="utf-8").write("_B = (%r\n      %r)\n" % ("# a generator comment\n", body + "\n"))
            seen["fets " + name] = m.draft_battery_fets("_fixture")[0]
        open(tmp, "w", encoding="utf-8").write("_B = (%r)\n" % (forms["loop"].replace('"CH_BATQ", "VBAT"', '"VBAT", "CH_BATQ"') + "\n"))
        try:
            m.draft_battery_fets("_fixture")
        except SystemExit:
            seen["fets swapped"] = "refused"
    finally:
        m.PINS.pop("_fixture", None)
        shutil.rmtree(tdir, ignore_errors=True)
    assert seen["fets loop"] == seen["fets renamed"] == seen["fets singles"] == ("Q39", "Q40", "QX") and seen["fets pair"] == ("Q39", "Q40")
    assert seen.get("fets swapped") == "refused", "FETs with the drain and the source swapped were read as battery FETs"
    assert seen["one"] == (12.0, "L4", 0.85, "VSYS_E", True)
    assert seen["two"] == (12.0, "U22", 0.85, "VSYS_E", False), "the two-line declaration reads, where the old pattern did not match"
    # the tree's drafts: +12V_FAN's efficiency is the parsed declaration's, and the battery FETs are the charger draft's
    F = _C["R"]["F"]
    assert F["fan12_eff_draft"] == F["fan12_decl"]["kw"]["efficiency"] and F["fan12_decl"]["kw"]["fed_from"] == "VSYS_E"
    assert F["fan12_decl"]["pos"][1] == 12.0 and "source_ic" in F["fan12_decl"]["kw"], "L8P-F03's correction: the source named with source_ic"
    assert len(F["bat_refs"]) == int(F["bat_fets"][0]) and F["bat_refs"][:2] == ("Q39", "Q40")
    assert _pred("L4-E11's charger draft writes the battery FETs record l9stk selected, the third beside Q39 and Q40 (D10)")
    # record l9stk's output is read from this tree, not from a copy, and the breaker's variant is the one it selects
    assert not m.PINS["l9stk_prot"].startswith("v2/docs/records/l9pwr/inputs/") and "l9stk_prot" not in m.ORIGIN and "l9stk_prot" in m.IN_TREE
    sel = re.search(r"SELECTED: the (-\d) \(([a-z-]+)\)", open(os.path.join(ROOT, m.PINS["l9stk_prot"]), encoding="utf-8").read())
    assert sel and F["brk_variant"] == (sel.group(1), sel.group(2))
    assert ("the LM5069%s (%s, l9stk 15.4b)" % F["brk_variant"]) in _C["text"]
    other = "-2" if F["brk_variant"][0] == "-1" else "-1"
    assert ("LM5069" + other) not in _C["text"], "the output names the variant record l9stk did not select"
    page = open(PAGE, encoding="utf-8").read()
    assert ("LM5069%s" % F["brk_variant"][0]) in page and "Round 3" in page


def t_the_reconciliation_lines_with_layer_4():
    """Each line reproduces the other record's figure from its own inputs; the current design's figure beside it."""
    for rid in ("R1", "R1b", "R1c", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12"):
        assert _pred("reconciliation %s: the other record's figure reproduced from its own inputs" % rid), rid
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
    r = _rec("R1c")
    assert r["repro"] == (44.205, 209.007, 287.912, 165.76), "L4-E9 round 7's restated modes from round 1's tree"
    r = _rec("R11")
    assert r["repro"][6] == 15.986 and r["repro"][12] == 16.1, "L4-E9 round 7's D-17 from round 1's tree"
    r = _rec("R9")
    assert r["theirs"][0] == 23.197 and r["repro"][0] == 23.197 and r["repro"][3] == 4.9019, "record l8r2's round 6 envelope"
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
    # round 4: C1 takes the standby card's 1.0 W PLAN placeholder out of PS-ALLTX (REQ-018, CONOPS 4a), so PS-ALLTX joins PS-SURV
    assert _pred("DRAFTED's PLAN is above round 1's DRAFTED in every state but PS-SURV, where slots 1 and 3 are off, and PS-ALLTX, where C1 removes the standby card's 1.0 W")
    st = [s[1] for s in m.STEP_TEXT]
    # round 4: C1, the state's definition corrected (no drawing, no draft), is the last step
    assert st[0] == "RV" and set(st[1:6]) == {"ON MAIN"} and set(st[6:16]) == {"DRAFTED"} and st[16:] == ["CORRECTED"] and len(st) == 17
    for sid, status, tx in m.STEP_TEXT[6:16]:
        assert "not applied" in tx, "%s does not say it is not applied" % sid
    assert m.STEP_TEXT[16][0] == "C1" and "no drawing and no draft" in m.STEP_TEXT[16][2]


def t_margins_and_findings():
    assert _pred("D-11's all-transmit floor holds on RV and DRAWN and fails on DRAFTED")
    assert _pred("L4-E9 round 7's all-transmit floor covers round 1's drafted basis and not this round's")
    assert _pred("D-11's PA-alone floor holds on every tree")
    assert _pred("no converter is over its limit at PLAN in any state, DRAWN or DRAFTED")
    assert _pred("slots 1 and 3 are within their LM5176 loop on DRAFTED in every state: at HIGH at 5.1 V and at the least load voltage, in the bounded start and with a degraded cooler")
    assert _pred("the device rail's LM5176 is over its loop at HIGH in PS-ALLTX on DRAWN and DRAFTED (L9P-F03)")
    assert _pred("the drafted fan row equals the envelope over the step-up's low efficiency at 5.0 V, to 0.01 A")
    assert _pred("every margin finding has a class among the instruction's three and an owner")
    assert _pred("the findings are L9P-F01 to L9P-F06")
    F = {x["id"]: x for x in _C["R"]["classified"]}
    assert F["L9P-F01"]["class"] == "DEMONSTRATED ANALYSIS DEFECT" and "L4-E9" in F["L9P-F01"]["owner"] and F["L9P-F01"]["status"].startswith("OPEN")
    fr = _C["R"]["floor_rule"]
    assert fr["need"] > fr["floor_r7"] and fr["floor_req"] >= fr["need"] + fr["over"] - 1e-9 and fr["floor_req"] - fr["step"] < fr["need"] + fr["over"]
    assert F["L9P-F02"]["status"].startswith("RESOLVED IN THE DRAFTS") and "CONDITIONAL" in F["L9P-F02"]["status"]
    assert F["L9P-F04"]["class"] == "PHYSICAL QUESTION" and "specimen" in F["L9P-F04"]["action"]
    for k in ("L9P-F02", "L9P-F03", "L9P-F05", "L9P-F06"):
        assert F[k]["class"] == "ASSUMPTION TO BOUND", k


def t_round4_c1_and_the_case_row():
    """Round 4 (T5): C1 takes the standby card out of PS-ALLTX on DRAFTED and leaves DRAWN as rv-pwr's state; out 7b computes
    C-ALLTX rev 2 from the row's text at the VBAT the case sets, and its parts close on the cells' EMF."""
    m = _M()
    for k in ("C1: PS-ALLTX on DRAFTED carries the standby card at 0 W in every scenario, and DRAWN keeps rv-pwr's state",
              "C-ALLTX rev 2's row: every transmitter at its HIGH, the outlets, the heater and the standby card at 0 W, the compute modules at 4.5 W",
              "C-ALLTX rev 2's row closes on itself: load pins, conversion, path and cells sum to the cell EMF at 18 A plus the deficit"):
        assert _pred(k), k
    ca = _C["R"]["calltx"]
    nw = ca["new"]
    assert abs(nw["vbat"] * 18.0 - nw["p"]) < 1e-6 and nw["vbat"] < 14.4
    assert abs(nw["allow"] - 18.0 * (15.5 - 18.0 * (nw["r_path"] + 4 * 0.06 / 3.0))) < 1e-9
    assert ca["old_raw"]["standby"] == 9.1 and ca["raw_fixed"]["standby"] == 0.0 and ca["old_raw"]["p"] - ca["raw_fixed"]["p"] > 9.1
    # the row's text against D-11's basis: only non-transmit loads differ, and each is taken at its PS-ALLTX PLAN in the row
    D = _C["R"]["cfgs"]["DRAFTED"]
    for n, v in ca["vals"].items():
        if abs(v - ca["basis_vals"][n]) > 1e-9 and not n.startswith("CM5"):
            assert n not in m.CASE_TX and v == D.load(n)["d"]["ALLTX"][1], n
    assert nw["need"] < ca["old_basis"]["V_rest"]["hi"] and round(ca["old_basis"]["V_rest"]["hi"], 3) == 16.214
    assert ca["cm5_8"]["need"] > nw["need"] > ca["fans_plan"]["need"]


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
    fr = R["floor_rule"]
    for s in ("50.043663", "2.06349", "1.3208", "L9P-F01", "L9P-F06", "%.3f V" % fr["need"], "%.1f V" % fr["floor_req"], "%.3f V" % fr["need_mk"]):
        assert s in page, "the page does not carry %r" % s
    for st in ("IDLESPEC", "ALLTX"):
        t = R["tot"][("DRAFTED-R1", st)]
        s = "%.2f / %.2f / %.2f" % (t["lo"]["pb"], t["plan"]["pb"], t["hi"]["pb"])
        assert s in page, "the page does not carry %s's round 1 DRAFTED %s" % (st, s)
    need(README, "the README")
    rd = open(README, encoding="utf-8").read()
    assert "9.1" in rd and "LAYER-STATUS" in rd


def t_record_hygiene_no_long_dashes_no_claim_words_no_private_paths():
    files = [SCRIPT, OUT, PAGE, README, os.path.abspath(__file__)]
    copies = [os.path.join(INPUTS, f) for f in sorted(os.listdir(INPUTS))] if os.path.isdir(INPUTS) else []
    for p in copies:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in inputs/%s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in inputs/%s" % os.path.basename(p)
    for p in files:
        need(p, os.path.basename(p))
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        if p != os.path.abspath(__file__):
            m = CLAIM.search(t)
            assert not m, "a claim word %r in %s" % (m.group(0), os.path.basename(p))
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
