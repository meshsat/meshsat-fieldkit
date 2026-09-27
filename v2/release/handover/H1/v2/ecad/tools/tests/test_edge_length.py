#!/usr/bin/env python3
"""A net is a transmission line because of its EDGE and its length (rule SI-001, MESHSAT-862, 16 Sep 2026).

The registry's note read "no net in this project has ever been classified by edge rate", and half of that was
already wrong: every net is classified by spectral content. What was missing is the arithmetic that turns a
class into a length, and the number that arithmetic needs is a rise time, which belongs to a DRIVER and not to
a class name: board A's fast nets are gate drives and board B's are a memory bus."""
import os, sys, math

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import rest
import edge_length as E
SRC = open(os.path.join(TOOLS, "edge_length.py"), encoding="utf-8").read()


def t_the_propagation_delay_lands_on_the_textbook_numbers():
    """About 5.5 ps/mm on an outer layer and 6.9 on an inner one, for FR-4 at er 4.3: roughly 6 inches per
    nanosecond, which is the figure every transmission-line table starts from. A formula that disagreed with it
    would have a unit error in it."""
    micro = E.t_pd_ps_per_mm(4.3, True); strip = E.t_pd_ps_per_mm(4.3, False)
    assert 5.2 < micro < 5.8, micro
    assert 6.6 < strip < 7.2, strip
    assert strip > micro, "a stripline's field is all laminate, so it must be the slower of the two"


def t_a_one_nanosecond_edge_is_about_thirty_millimetres_at_the_sixth_criterion():
    crit = 1000.0 / (6 * E.t_pd_ps_per_mm(4.3, True))
    assert 28 < crit < 32, crit


def t_a_net_with_no_declared_edge_is_named_and_never_estimated():
    assert "undeclared.append" in SRC, "a net with no declared edge is silently skipped"
    assert "no_declared_edge" in SRC, "the verdict does not carry how many nets have no edge"
    i = SRC.index("tr, _why = rise_for")
    assert "if not tr:" in rest(SRC, i), "a missing rise time falls through to a default"


def t_the_rise_time_comes_from_the_declaration_beside_the_class_entry():
    assert "def rise_for(" in SRC and "fnmatch" in SRC, "the per-entry rise time is not matched per net"
    assert "a property of the DRIVER" in SRC, "the tool does not say why a class name is not enough"


def t_being_a_transmission_line_is_not_by_itself_a_defect():
    """The first version failed every net past its critical length. At a 200 ps edge that is every net on a
    285 mm board, and a verdict that fails all of them reports physics rather than a defect. A net past its
    critical length is asked what it HAS first: an impedance target, a series resistor, or a declaration."""
    assert "def mitigation(" in SRC, "nothing asks a long net what it has"
    i = SRC.index("if L > crit:")
    w = SRC[i:i + 700]
    assert "mitigation(" in w, "the length test does not consult the mitigation"
    assert "mitigated.append" in w and "over.append" in w, "a long net has only one outcome"
    assert "long_and_answered" in SRC, "the verdict does not separate the answered from the unanswered"


def t_a_pull_up_is_not_a_series_termination():
    """A resistor to a rail damps nothing on the line: it sets a level. Only a resistor between two SIGNAL
    nets is the shape of a source termination, and the value has to be in the range one is built from."""
    i = SRC.index("for fp in b.GetFootprints():")
    w = SRC[i:i + 900]
    assert "_is_rail(a_) or _is_rail(b_)" in w, "a resistor to a rail counts as a termination"
    assert "10.0 <= ohm <= 150.0" in w, "any resistance counts as a termination"
    assert "a_ == b_" in w, "a resistor with both ends on one net counts"


def t_the_series_reading_declares_itself_a_screen():
    """The board file knows neither which end drives nor what sits at the far end, so this reading can accept
    a damping resistor in a filter. It says so where it is written down, because a screen presented as a proof
    is how a rule stops finding anything."""
    assert "SCREEN and says so" in SRC or "This is a SCREEN" in SRC, "the limitation is not written down"


def t_the_criterion_carries_the_calibration_it_was_chosen_against():
    assert "ECSS-E-HB-20-07A" in SRC, "the criterion cites no document at all"
    assert "35 mm" in SRC and "200 ps" in SRC, "the handbook's worked case is not the calibration point"


# ------------------------------------------------------------------------------------------------------------------
# SI-001 AT THE SCHEMATIC PHASE (26 September 2026, MESHSAT-1357): the table from the netlist, the held documents and
# the declared stack. The fixtures below run with no KiCad. A fixture board ("zz") has no table in boards/, so the
# board-table read and the signal-class declarations are handed in for the length of one call and put back after.
# ------------------------------------------------------------------------------------------------------------------
import json, tempfile, contextlib


def _k9(d, comps, nets, stem="pcb-zz-si"):
    """A netlist in KiCad 9.0.9's shape and its intent beside it. nets: [(name, class, [(ref, pin)])]."""
    os.makedirs(os.path.join(d, "out"), exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in comps.items())
    body = []
    for i, (name, klass, nodes) in enumerate(nets, 1):
        ns = "\n".join('      (node (ref "%s") (pin "%s") (pintype "passive"))' % (r, p) for r, p in nodes)
        body.append('    (net (code "%d") (name "/%s") (class "%s")\n%s)' % (i, name, klass, ns))
    p = os.path.join(d, "out", stem + ".net")
    open(p, "w").write("(export (version \"E\")\n  (components\n%s  )\n  (nets\n%s)))\n" % (c, "\n".join(body)))
    json.dump({"rails": {"+3V3": {}}, "nodes": {}, "bypass": [], "pair_classes": {"USB": {"z_diff": 90.0}, "DIFF100": {}}},
              open(os.path.join(d, "out", stem + "-intent.json"), "w"))
    return p


@contextlib.contextmanager
def _board(table, sources=None):
    """Hand a fixture board table to boardtable.value and signal_class.declarations for one call, and the edge
    sources to edge_length; everything is put back, whatever the call does."""
    import boardtable, signal_class
    ov, od, osrc = boardtable.value, signal_class.declarations, E.EDGE_SOURCES
    boardtable.value = lambda letter, key, default=None: table.get(key, default) if letter == "zz" else ov(letter, key, default)
    signal_class.declarations = lambda letter: ([(e["pattern"], e["class"], e["basis"]) for e in table.get("signal_classes", [])], []) \
        if letter == "zz" else od(letter)
    if sources is not None: E.EDGE_SOURCES = sources
    try: yield
    finally:
        boardtable.value, signal_class.declarations, E.EDGE_SOURCES = ov, od, osrc


FACTS = {"zz": {"stackup": "JLC06161H-3313", "routing_layers": ["F.Cu", "In2.Cu", "In3.Cu", "B.Cu"], "outline_mm": [100, 80]}}
HS = {"pattern": "USB_*", "class": "HIGH_SPEED_DIGITAL", "basis": "a USB 2.0 high-speed data line", "rise_ns": 0.5}
EN = {"pattern": "*_EN", "class": "LOW_SPEED_OR_DC", "basis": "an enable held for seconds at a time"}
CK = {"pattern": "SPI_*", "class": "CLOCKED_DIGITAL", "basis": "an SPI bus at a few MHz from the MCU"}


def _doc(repo, text):
    p = os.path.join(repo, "v2", "vendor", "standards", "fixture-usb.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)
    return "v2/vendor/standards/fixture-usb.md"


def _src(doc, rise=0.5, patterns=("USB_*",)):
    return ({"id": "FIX", "rise_ns": rise, "document": doc, "clause": "fixture 7.1.2.2",
             "quote": "rise and fall times must be 500 ps or longer", "covers": {"zz": tuple(patterns)}},)


def _fixture(extra_nets=(), extra_comps=None, usb_class="USB"):
    d = tempfile.mkdtemp(prefix="si001-")
    comps = {"U1": "USB PHY", "J1": "USB-C", "U2": "MCU", "R1": "10k"}
    comps.update(extra_comps or {})
    nets = [("USB_DP", usb_class, [("U1", "1"), ("J1", "2")]), ("USB_DN", usb_class, [("U1", "2"), ("J1", "3")]),
            ("PHY_EN", "Default", [("U1", "3"), ("U2", "4"), ("R1", "1")]),
            ("+3V3", "Default", [("U1", "4"), ("U2", "5"), ("R1", "2")]), ("GND", "Default", [("U1", "5"), ("U2", "6")])]
    nets += list(extra_nets)
    return _k9(d, comps, nets), d


def t_si001_a_documented_edge_gives_a_critical_length_and_a_pair_with_a_target_answers_it():
    p, d = _fixture()
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "> the 10% to 90%\n> high-speed differential rise and fall times must be 500 ps or longer when\n")
    with _board({"critical_k": 6, "signal_classes": [HS, EN]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "PASS", (r["fails"], r["counts"], [x["status"] for x in r["rows"]])
    row = next(x for x in r["rows"] if x["pattern"] == "USB_*")
    # 0.5 ns on the 6-layer stack's slowest inner layer (core 4.6: 7.15 ps/mm, TI SCAA082A's stripline figure) at k 6
    assert 11.0 < row["critical_mm"] < 12.2, row
    assert row["may_be_long"] and not row["layout_bound"] and len(row["answered"]) == 2, row
    assert r["counts"]["low_speed_nets"] == 1, r["counts"]


def t_si001_a_class_with_no_documented_edge_is_undecided_and_names_its_ics():
    p, d = _fixture(extra_nets=[("SPI_SCK", "Default", [("U2", "7"), ("U1", "8")])])
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "high-speed differential rise and fall times must be 500 ps or longer")
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "INCONCLUSIVE", r["counts"]
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    assert row["status"] == "UNDECIDED" and "MCU" in row["drivers"], row
    assert "critical_mm" not in row, "an undecided class was given a length"


def t_si001_a_declared_edge_the_document_contradicts_fails():
    p, d = _fixture()
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "high-speed differential rise and fall times must be 500 ps or longer")
    fast = dict(HS, rise_ns=0.3)
    with _board({"critical_k": 6, "signal_classes": [fast, EN]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "FAIL" and any("states 0.5 ns" in f for f in r["fails"]), r["fails"]


def t_si001_a_document_that_does_not_say_it_decides_nothing():
    """The quote is the proof that a held document states the edge: a transcription that lost the words, or a rise
    time no source names at all, is UNDECIDED and the reading INCONCLUSIVE, never a pass."""
    p, d = _fixture()
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "this transcription carries some other clause")
    with _board({"critical_k": 6, "signal_classes": [HS, EN]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "INCONCLUSIVE", r["counts"]
    assert "does not contain the words" in next(x for x in r["rows"] if x["pattern"] == "USB_*")["why"]
    with _board({"critical_k": 6, "signal_classes": [HS, EN]}, ()):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "INCONCLUSIVE"
    assert "no held document is named" in next(x for x in r["rows"] if x["pattern"] == "USB_*")["why"]


def t_si001_a_fast_net_with_no_target_or_termination_is_bound_to_its_length_and_a_pull_up_is_not_a_termination():
    extra = [("USB_DP_R", "Default", [("R5", "2"), ("U2", "9")])]
    p, d = _fixture(extra_nets=extra, extra_comps={"R5": "22", "R6": "22"}, usb_class="Default")
    # R5 sits between USB_DP and USB_DP_R (a series termination); R6 pulls USB_DN up to +3V3 (not one)
    t = open(p).read()
    t = t.replace('(node (ref "J1") (pin "2") (pintype "passive"))',
                  '(node (ref "J1") (pin "2") (pintype "passive"))\n      (node (ref "R5") (pin "1") (pintype "passive"))')
    t = t.replace('(node (ref "J1") (pin "3") (pintype "passive"))',
                  '(node (ref "J1") (pin "3") (pintype "passive"))\n      (node (ref "R6") (pin "1") (pintype "passive"))')
    t = t.replace('(node (ref "R1") (pin "2") (pintype "passive"))',
                  '(node (ref "R1") (pin "2") (pintype "passive"))\n      (node (ref "R6") (pin "2") (pintype "passive"))')
    open(p, "w").write(t)
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "high-speed differential rise and fall times must be 500 ps or longer")
    with _board({"critical_k": 6, "signal_classes": [HS, EN]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "USB_*")
    assert "USB_DP" in row["answered"] and "R5" in row["answered"]["USB_DP"], row
    assert "USB_DN" in row["layout_bound"], "a pull-up to a rail was read as a termination: %s" % row
    # a layout-bound net is not a schematic failure, and nothing answers it at this phase either: INCONCLUSIVE, never a
    # pass (TSN-D18, reversing TSN-D8 on the second independent check's finding)
    assert E.schematic_result(r) == "INCONCLUSIVE", E.schematic_result(r)
    out = tempfile.mkdtemp(prefix="si001-v-")
    E.write_schematic_verdict(r, out_dir=out, quiet=True, table_file=False)
    v = json.load(open(os.path.join(out, "edge_length.verdict.json")))
    assert any(e.startswith("LAYOUT_BOUND USB_*") and "USB_DN" in e for e in v["evidence"]), v["evidence"]
    # the schematic answers it: a declaration in edge_allow, and the reading passes
    with _board({"critical_k": 6, "signal_classes": [HS, EN],
                 "edge_allow": [{"pattern": "USB_DN", "why": "fixture: run under the critical length by placement"}]},
                _src(doc)):
        r2 = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r2) == "PASS", [x.get("layout_bound") for x in r2["rows"]]


def t_si001_a_board_with_no_declared_outline_has_every_decided_net_possibly_long():
    """A missing outline_mm is no corner-to-corner run to compare with: every decided net may be long, and one with no
    answer holds the reading. With the outline declared, the same short board has nothing that may be long."""
    p, d = _fixture()
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "high-speed differential rise and fall times must be 500 ps or longer")
    tiny = {"zz": dict(FACTS["zz"], outline_mm=[5, 4])}
    bare = {"zz": {k: v for k, v in FACTS["zz"].items() if k != "outline_mm"}}
    with _board({"critical_k": 6, "signal_classes": [HS, EN]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=tiny, repo=repo)
        r2 = E.schematic_table(p, "zz", facts=bare, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "USB_*")
    assert not row["may_be_long"] and "corner-to-corner" in row["needs"], row
    row2 = next(x for x in r2["rows"] if x["pattern"] == "USB_*")
    assert row2["may_be_long"] and r2["inputs"]["extent_mm"] is None, row2


def t_si001_the_slowest_layer_of_the_declared_and_the_ruled_stacks_sets_the_length():
    """Board P is declared on two layers and ruled to four at 2 oz (decision 28): the ruled stack's inner layer is
    slower than any microstrip, so it governs, and the table holds whichever stack the layout is drawn on."""
    facts = {"p": {"stackup": "2L-2oz", "routing_layers": ["F.Cu", "B.Cu"], "outline_mm": [70, 44]}}
    tpd, chosen, cands, notes = E.worst_delay("p", facts)
    assert chosen[0] == "JLC04162H-7628" and not chosen[2][1], chosen
    two = max(x[2][2] for x in cands if x[0] == "2L-2oz")
    assert tpd > two, (tpd, two)
    d = {"d": {"stackup": "JLC04161H-7628", "routing_layers": ["F.Cu", "B.Cu"], "outline_mm": [100, 80]}}
    tpd_d, ch_d, _c, _n = E.worst_delay("d", d)
    assert ch_d[2][1], "a board routed on its outer layers only was judged on an inner one"


def t_si001_the_ruled_stacks_are_the_decisions_rulings_and_the_sources_agree_with_the_board_tables():
    import rules_lib as R, stackup_write, boardtable as bt
    dec = {str(x.get("n")): x for x in (R._yaml().safe_load(open(os.path.join(TOOLS, "pcb_decisions.yaml"))) or {}).get("decisions") or []}
    for letter, rows in E.RULED_STACKS.items():
        for n, name, _why in rows:
            assert (dec.get(str(n)) or {}).get("status") == "ruled", "decision %s is not ruled: RULED_STACKS is stale" % n
            assert name in stackup_write.STACKS, "%s is not a stack this project holds" % name
    repo = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
    for s in E.EDGE_SOURCES:
        doc = os.path.join(repo, s["document"])
        assert os.path.isfile(doc), doc
        assert E._norm(s["quote"]) in E._norm(open(doc, encoding="utf-8").read()), "%s no longer says %r" % (s["document"], s["quote"])
        for letter, pats in s["covers"].items():
            table = {e["pattern"]: e for e in bt.value(letter, "signal_classes", []) or []}
            for pat in pats:
                assert pat in table and table[pat].get("rise_ns") == s["rise_ns"], (letter, pat, table.get(pat))


def t_si001_the_board_run_keeps_the_routed_half_under_its_own_name():
    """The routed comparison is the layout gate's and writes edge_length_routed under its own crash guard; the
    schematic table is edge_length, the rule's own verdict, so a run on a layout that is not the candidate's can
    neither stand in front of the table nor have its crash filed under it."""
    assert 'guard("edge_length_routed", routed_main' in SRC, "the routed half is not guarded under its own name"
    body = SRC[SRC.index("def routed_main("):SRC.index("def _sha16(")]
    assert '_v.write("edge_length_routed"' in body and '_v.write("edge_length",' not in body, "the routed half writes the rule's verdict"
    assert 'if "--netlist" in a: return netlist_main(a)' in SRC


def t_si001_the_reading_records_its_inputs_by_sha_and_never_an_absolute_path():
    p, d = _fixture()
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "high-speed differential rise and fall times must be 500 ps or longer")
    out = tempfile.mkdtemp(prefix="si001-v-")
    with _board({"critical_k": 6, "signal_classes": [HS, EN]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
        rc = E.write_schematic_verdict(r, out_dir=out, quiet=True)
    v = json.load(open(os.path.join(out, "edge_length.verdict.json")))
    assert rc == 0 and v["verdict"] == "PASS" and v["rules"] == ["SI-001"], v
    assert v["inputs"]["netlist"]["sha256_16"] and v["inputs"]["netlist"].get("content16"), v["inputs"]
    for k, x in v["inputs"].items():
        if isinstance(x, dict) and x.get("path"): assert not x["path"].startswith("/"), (k, x)
    assert os.path.exists(os.path.join(out, "edge_length.table.json")), "the table was not written beside the verdict"
