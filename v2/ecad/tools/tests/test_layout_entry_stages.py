#!/usr/bin/env python3
"""Stage-specific gates (MESHSAT-1357, 26 September 2026; the review of the 22:35 progress report, finding A: "Decision
31's proposed hold requires a corrected layout and SCH-002 PASS before lifting. Layout entry requires that hold to be
absent. This is an explicit deadlock for A, D and E").

A hold and a feasibility blocker now name the stage they gate, and `rules_status.layout_entry` counts only what gates
layout entry, plus every layout-entry requirement a later-staged hold carries. Executed against fixtures:

  * a hold staged at FABRICATION_RELEASE does not hold layout entry, its unmet requirements do, and when they are met
    the board is ready on that account; a hold with no stage still holds layout entry;
  * each requirement kind is evaluated against the board's own evidence: rule_pass on a class that counts, fitted_parts
    on the netlist by part number, LCSC code and the conductor's net, review by the pinned text and the netlist it read;
  * the holds validator refuses a later-staged hold that names no layout-entry requirement (moving it would waive it);
  * a feasibility stage holds layout entry only at LAYOUT_ENTRY; an unstaged record holds layout entry as before;
  * the registry refuses a layout-entry stage that needs the final PCB, and a fabrication-release stage that needs the
    built kit;
  * a desk review bound to nets stops counting when one of them changes and not when the rest of the board does;
  * every per-board status page labels its percentage table as the historical aggregate of mixed revisions.
"""
import os, sys, json, hashlib, tempfile, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import rules_status as S
import rules_lib as R
import test_evidence_class as EC

NETLIST = '''(export (version "E")
  (components
    (comp (ref "D9")
      (value "PESD5V0S1BA bidirectional ESD clamp at the jack")
      (footprint "Diode_SMD:D_SOD-323")
      (fields
        (field (name "LCSC") "C19224")))
    (comp (ref "J_HS1")
      (value "headset jack")
      (footprint "meshsat:Jack")
      (fields
        (field (name "Footprint") "meshsat:Jack"))))
  (nets
    (net (code "1") (name "HS1_SPK")
      (node (ref "D9") (pin "2") (pintype "passive"))
      (node (ref "J_HS1") (pin "1") (pintype "passive")))
    (net (code "2") (name "GND")
      (node (ref "D9") (pin "1") (pintype "passive"))
      (node (ref "J_HS1") (pin "2") (pintype "passive")))
    (net (code "3") (name "HS1_MIC")
      (node (ref "J_HS1") (pin "3") (pintype "passive")))))
'''


def _net(body=NETLIST):
    d = tempfile.mkdtemp(prefix="stages-net-")
    p = os.path.join(d, "pcb-x.net"); open(p, "w").write(body)
    return p


def _audit(net_path, trn="PASS", trn_cls=S.CURRENT_CANDIDATE, netsha=EC.NET):
    rows = [EC._row("SCH-001", "SCHEMATIC", "PASS", S.CURRENT_CANDIDATE),
            EC._row("TRN-001", "SCHEMATIC", trn, trn_cls)]
    cand = dict(EC._cand(net=netsha), netlist=net_path)
    return {"board": "x", "candidate": cand, "rows": rows}


def _review(d, netsha=EC.NET):
    p = os.path.join(d, "review.md"); open(p, "w").write("the protection topology, reviewed\n")
    return {"kind": "review", "what": "the protection topology reviewed", "document": p,
            "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(), "netlist_sha16": netsha}


def _hold(reqs, stage="FABRICATION_RELEASE"):
    h = {"decision": 31, "ROUTING_STATUS": "PASS", "ELECTRICAL_PROTECTION_STATUS": "BLOCKED_DECISION_31",
         "FAB_READINESS": "NOT_READY", "PUBLICATION_STATUS": "HELD", "lifts_when": "the layout implements it"}
    if stage: h["stage"] = stage
    if reqs is not None: h["layout_entry_requires"] = reqs
    return h


def _parts(lcsc="C19224", at="J_HS1.1", part="PESD5V0S1BA"):
    return {"kind": "fitted_parts", "what": "the ruled clamp", "parts": [{"ref": "D9", "part": part, "lcsc": lcsc, "at": [at]}]}


def t_a_fabrication_release_hold_admits_layout_once_its_entry_requirements_are_met():
    net = _net(); d = os.path.dirname(net)
    reqs = [_review(d), _parts(), {"kind": "rule_pass", "what": "TRN-001 PASS on the current netlist", "rule": "TRN-001"}]
    le = S.layout_entry(_audit(net), {"x": _hold(reqs)}, req={})
    assert le["ready"], le["reasons"]
    assert le["holds_later"] and le["holds_later"][0]["stage"] == "FABRICATION_RELEASE" and not le["holds_at_entry"], le
    assert all(q["met"] for q in le["requirements"]), le["requirements"]
    # the same hold with no stage is a layout-entry hold, as every hold was before
    le2 = S.layout_entry(_audit(net), {"x": _hold(None, stage=None)}, req={})
    assert not le2["ready"] and any("held by decision 31 at layout entry" in r for r in le2["reasons"]), le2["reasons"]
    # and an unknown stage is read as layout entry, never as a later one
    le3 = S.layout_entry(_audit(net), {"x": _hold(reqs, stage="SOMEDAY")}, req={})
    assert not le3["ready"], le3


def t_each_unmet_requirement_holds_layout_entry_by_itself():
    net = _net(); d = os.path.dirname(net)
    good = [_review(d), _parts(), {"kind": "rule_pass", "what": "TRN-001 PASS", "rule": "TRN-001"}]
    cases = {
        "wrong LCSC": (lambda r: r.__setitem__(1, _parts(lcsc="C1")), _audit(net)),
        "wrong part": (lambda r: r.__setitem__(1, _parts(part="PESD5V0S2BT")), _audit(net)),
        "not at its conductor": (lambda r: r.__setitem__(1, _parts(at="J_HS1.3")), _audit(net)),
        "TRN-001 not current": (lambda r: None, _audit(net, trn_cls=S.AWAITING_REVALIDATION)),
        "TRN-001 FAIL": (lambda r: None, _audit(net, trn="FAIL")),
        "review on another netlist": (lambda r: r.__setitem__(0, _review(d, netsha="c" * 16)), _audit(net)),
        "review text edited": (lambda r: r[0].__setitem__("sha256", "0" * 64), _audit(net)),
        "no review written": (lambda r: r[0].update(document="v2/docs/reviews/NOT-WRITTEN.md", sha256=None), _audit(net)),
    }
    for what, (mut, st) in cases.items():
        reqs = copy.deepcopy(good); mut(reqs)
        le = S.layout_entry(st, {"x": _hold(reqs)}, req={})
        assert not le["ready"], "%s: the board read ready for layout" % what
        assert any("layout-entry requirement not met" in r for r in le["reasons"]), (what, le["reasons"])
    # a later-staged hold that names no requirement holds layout entry, and the validator refuses it on file
    le = S.layout_entry(_audit(net), {"x": _hold([])}, req={})
    assert not le["ready"] and any("names no layout-entry requirement" in r for r in le["reasons"]), le["reasons"]


def t_the_holds_validator_refuses_a_later_stage_hold_without_entry_requirements():
    if not hasattr(R, "STAGES"): raise Skip("rules_lib carries no STAGES: the r8prov rules_lib draft is not applied")
    d = tempfile.mkdtemp(prefix="stages-holds-")
    base = ("holds:\n e:\n   decision: 31\n   ROUTING_STATUS: PASS\n   ELECTRICAL_PROTECTION_STATUS: X\n"
            "   FAB_READINESS: NOT_READY\n   PUBLICATION_STATUS: HELD\n")
    for body, needle in ((base + "   stage: FABRICATION_RELEASE\n", "layout_entry_requires"),
                         (base + "   stage: LATER\n", "stage"),
                         (base + "   stage: FABRICATION_RELEASE\n   layout_entry_requires:\n     - {kind: guess, what: x}\n", "kind")):
        p = os.path.join(d, "h.yaml"); open(p, "w").write(body)
        try:
            R.board_holds(p)
        except ValueError as e:
            assert needle in str(e), (needle, e)
        else:
            raise AssertionError("the validator accepted %r" % body[-60:])
    p = os.path.join(d, "ok.yaml")
    open(p, "w").write(base + "   stage: FABRICATION_RELEASE\n   layout_entry_requires:\n"
                              "     - {kind: rule_pass, what: TRN-001 PASS, rule: TRN-001}\n")
    assert R.board_holds(p)["e"]["stage"] == "FABRICATION_RELEASE"


def _fea(stages=None, holds_layout_entry=("x",), status="FEASIBILITY_OPEN"):
    r = {"id": "FEA-900", "kind": "feasibility", "title": "fixture", "status": status,
         "holds_layout_entry": list(holds_layout_entry), "closing_evidence": "the fixture's closing evidence text",
         "owner": "the fixture's owner"}
    if stages is not None: r["stages"] = stages
    return {"records": [r]}


def t_a_feasibility_stage_holds_layout_entry_only_at_its_own_stage():
    net = _net()
    st = _audit(net)
    staged = _fea([{"stage": "LAYOUT_ENTRY", "holds": ["x"], "status": "OPEN", "requires": "a development-board test"},
                   {"stage": "FABRICATION_RELEASE", "holds": ["x"], "status": "OPEN", "requires": "the routed candidate"},
                   {"stage": "PROTOTYPE_VERIFICATION", "holds": ["kit"], "status": "OPEN", "requires": "the bench"}])
    le = S.layout_entry(st, {}, req=staged)
    assert not le["ready"] and [f["id"] for f in le["feasibility_at_entry"]] == ["FEA-900"], le
    assert [f["stage"] for f in le["feasibility_later"]] == ["FABRICATION_RELEASE"], le["feasibility_later"]
    staged["records"][0]["stages"][0]["status"] = "CLOSED"
    le2 = S.layout_entry(st, {}, req=staged)
    assert le2["ready"], "a closed layout-entry stage still held the board: %s" % le2["reasons"]
    assert le2["feasibility_later"], "the later stage vanished from the listing"
    # unstaged: the record holds layout entry of every board it names, exactly as before
    le3 = S.layout_entry(st, {}, req=_fea(None))
    assert not le3["ready"] and "unstaged" in le3["feasibility_at_entry"][0]["requires"], le3
    # a closed blocker holds nothing
    assert S.layout_entry(st, {}, req=_fea(None, status="FEASIBILITY_CLOSED"))["ready"]


def t_the_registry_refuses_a_stage_that_needs_what_only_a_later_stage_produces():
    if not hasattr(R, "STAGE_CANNOT_NEED"): raise Skip("the r8prov rules_lib draft is not applied")
    req = R.load_requirements()
    fea = [r for r in req["records"] if r.get("kind") == "feasibility" and r.get("stages")]
    if not fea: raise Skip("no feasibility record carries stages: the r8prov requirements draft is not applied")
    errs, _w = R.validate_requirements(req)
    assert not errs, errs[:5]
    bad = copy.deepcopy(req)
    r = next(x for x in bad["records"] if x.get("stages"))
    le = next(s for s in r["stages"] if s["stage"] == "LAYOUT_ENTRY")
    le["needs"] = list(le.get("needs") or []) + ["FINAL_PCB"]
    fr = next(s for s in r["stages"] if s["stage"] == "FABRICATION_RELEASE")
    fr["needs"] = list(fr.get("needs") or []) + ["BUILT_KIT"]
    errs, _w = R.validate_requirements(bad)
    assert any("LAYOUT_ENTRY needs FINAL_PCB" in e for e in errs), errs[:5]
    assert any("FABRICATION_RELEASE needs BUILT_KIT" in e for e in errs), errs[:5]
    # and the layout-entry stage's boards are the record's holds_layout_entry
    bad2 = copy.deepcopy(req)
    r2 = next(x for x in bad2["records"] if x.get("stages"))
    r2["holds_layout_entry"] = []
    errs2, _w = R.validate_requirements(bad2)
    assert any("holds_layout_entry" in e for e in errs2), errs2[:5]


def t_every_feasibility_blocker_is_staged_and_none_gates_its_own_layout_on_the_built_board():
    """The six blockers of the review, as the registry holds them after the r8prov draft."""
    req = R.load_requirements()
    fea = {r["id"]: r for r in req["records"] if r.get("kind") == "feasibility"}
    if not any(r.get("stages") for r in fea.values()):
        raise Skip("no feasibility record carries stages: the r8prov requirements draft is not applied")
    for rid in ("FEA-001", "FEA-002", "FEA-003", "FEA-004", "FEA-005", "FEA-006"):
        sts = {s["stage"]: s for s in fea[rid]["stages"]}
        assert set(sts) == set(S.STAGES), (rid, sorted(sts))
        assert not set(sts["LAYOUT_ENTRY"]["needs"]) & {"LAYOUT", "FINAL_PCB", "BUILT_KIT"}, (rid, sts["LAYOUT_ENTRY"]["needs"])
        assert sorted(sts["LAYOUT_ENTRY"]["holds"]) == sorted(fea[rid]["holds_layout_entry"]), rid


def t_the_committed_decision_31_holds_gate_fabrication_release_with_entry_requirements():
    """The committed state after the r8prov holds draft: A, D and E held at FABRICATION_RELEASE, each needing at layout
    entry the reviewed topology, the exact fitted parts of decision 31's executed record and TRN-001 PASS on the
    current netlist. The fitted parts are read off each board's committed netlist here."""
    h = R.board_holds()
    if not any("stage" in v for v in h.values()):
        raise Skip("no hold carries a stage: the r8prov holds draft is not applied")
    m = S.manifest()
    for L in ("a", "d", "e"):
        if L not in h: continue
        assert S.hold_stage(h[L]) == "FABRICATION_RELEASE", (L, h[L].get("stage"))
        kinds = sorted(q["kind"] for q in h[L]["layout_entry_requires"])
        assert kinds == ["fitted_parts", "review", "rule_pass"], (L, kinds)
        q = next(q for q in h[L]["layout_entry_requires"] if q["kind"] == "fitted_parts")
        net = S._board_netlist(L, m)
        if not net: raise Skip("board %s has no netlist in this tree" % L.upper())
        got = S._requirement(q, L, {"candidate": {"netlist": os.path.relpath(net, S.ECAD)}, "rows": []}, m)
        assert got["met"], (L, got["why"])
        assert next(q for q in h[L]["layout_entry_requires"] if q["kind"] == "rule_pass")["rule"] == "TRN-001"


def t_a_desk_review_bound_to_nets_stops_counting_only_when_they_change():
    net = _net()
    parsed = S.netlist_parse(net)
    dig = S.net_digest(parsed, ["HS1_SPK"])
    c = {"verified_nets": {"x": {"nets": ["HS1_SPK"], "digest": dig}}}
    keep = S._board_netlist
    try:
        S._board_netlist = lambda L, m: net
        ok, why = S.verified_nets_current(c, "x", {})
        assert ok and dig in why, why
        # a part ON the reviewed net changes its value (the jack is on HS1_SPK)
        open(net, "w").write(NETLIST.replace('(value "headset jack")', '(value "headset jack, 4 pole")'))
        S._NET_CACHE.clear()
        ok2, why2 = S.verified_nets_current(c, "x", {})
        assert not ok2, "a part on the reviewed net changed its value and the review still counted"
        open(net, "w").write(NETLIST.replace('(name "GND")', '(name "GND_A")'))
        ok3, _ = S.verified_nets_current(c, "x", {})
        assert ok3, "a change on a net the review did not read took its verification away"
        open(net, "w").write(NETLIST.replace('(node (ref "D9") (pin "2") (pintype "passive"))', ''))
        ok4, why4 = S.verified_nets_current(c, "x", {})
        assert not ok4 and "re-review" in why4, why4
        # an entry that binds no nets for this board is judged by its pin alone, as before
        assert S.verified_nets_current({}, "x", {})[0]
    finally:
        S._board_netlist = keep


def t_every_board_page_labels_its_percentage_table_as_the_historical_aggregate():
    import rules_render as RR
    st = {"board": "x", "manifest_version": "t", "rule_set_fingerprint": "f", "evidence_epoch": "e",
          "subject": {"dir": "pcb-x", "board": None},
          "rows": [dict(EC._row("SCH-001", "SCHEMATIC", "PASS", S.CURRENT_CANDIDATE), why="w")]}
    body = RR.board_doc("x", st, R.load(), S.coverage())
    i = body.index("**Historical aggregate of mixed revisions, not readiness.**")
    j = body.index("| historical aggregate, mixed revisions | rules |")
    assert i < j and "CURRENT-EVIDENCE.md" in body[i:j], body[i:j + 80]
    # and on the generated pages in this tree, which the suite also holds to the registry (rules_render --check)
    docs = os.path.join(TOOLS, "..", "..", "docs")
    pages = sorted(f for f in os.listdir(docs) if f.startswith("PCB-RULE-STATUS-"))
    if not pages: raise Skip("no generated status page in this tree")
    for f in pages:
        t = open(os.path.join(docs, f), encoding="utf-8").read()
        assert "Historical aggregate of mixed revisions, not readiness." in t and "CURRENT-EVIDENCE.md" in t, f


def t_a_requirement_with_nothing_to_read_is_not_met_and_never_crashes():
    """No netlist in the audit's candidate and no board of that letter in the manifest: the fitted parts cannot be read,
    so the requirement is NOT MET with its reason (absence is never a pass), and the test does not raise."""
    st = {"board": "x", "candidate": {}, "rows": []}
    q = _parts()
    got = S._requirement(q, "x", st, {})
    assert got["met"] is False and "no netlist" in got["why"], got
    le = S.layout_entry(st, {"x": _hold([q])}, req={})
    assert not le["ready"], le
    assert S._requirement({"kind": "someday", "what": "x"}, "x", st, {})["met"] is False
