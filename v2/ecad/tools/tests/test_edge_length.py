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
from harness import rest, Skip
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
    # a declaration that is a sentence answers nothing since CSI-D1 (29 September 2026): it is refused, the reading
    # FAILS and the net stays layout-bound
    with _board({"critical_k": 6, "signal_classes": [HS, EN],
                 "edge_allow": [{"pattern": "USB_DN", "why": "fixture: run under the critical length by placement"}]},
                _src(doc)):
        r2 = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r2) == "FAIL" and any("edge_allow refused" in f and "no ruled_by" in f for f in r2["fails"]), r2["fails"]
    assert "USB_DN" in next(x for x in r2["rows"] if x["pattern"] == "USB_*")["layout_bound"]
    # the schematic answers it: a declaration in edge_allow that carries its basis, and the reading passes
    with _board({"critical_k": 6, "signal_classes": [HS, EN], "edge_allow": [_allow(repo)]}, _src(doc)):
        r3 = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r3) == "PASS", (r3["fails"], [x.get("layout_bound") for x in r3["rows"]])
    assert r3["counts"]["allowed_nets"] == 1, r3["counts"]


ALLOW_MD = "> The data lines are wired directly, using short connections to maintain the signal integrity.\n"
ALLOW_LST = "   USB_DN     12.50 mm  vias 0  layers F.Cu\n   reference t_pd 5.572 ps/mm: the fixture's microstrip\n"
ALLOW_TPD = 7.1541528   # the fixture stack's slowest layer (JLC06161H-3313), as worst_delay reads it


def _allow(repo, text=ALLOW_MD, **more):
    """An edge_allow entry for USB_DN with its basis: a held fixture document, its sha, where the words are, the words;
    a checked row quoting the length measured on a reference layout and one quoting that layout's delay; and max_mm, at
    most the length scaled by the delays (12.50 x 5.572 / 7.154 = 9.74 mm)."""
    p = os.path.join(repo, "v2", "vendor", "fix", "layout-guide.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)
    open(os.path.join(repo, "v2", "vendor", "fix", "lengths.txt"), "w").write(ALLOW_LST)
    row = lambda q: {"document": "v2/vendor/fix/lengths.txt", "sha256_16": _s16(ALLOW_LST), "where": "the fixture's line", "quote": q}
    e = {"pattern": "USB_DN", "why": "fixture: the maker asks for a short direct run and the layout holds it",
         "ruled_by": "SESSION (fixture)", "document": "v2/vendor/fix/layout-guide.md", "sha256_16": _s16(ALLOW_MD),
         "where": "the fixture's one line", "quote": "wired directly, using short connections to maintain",
         "checked": [row("USB_DN 12.50 mm"), row("reference t_pd 5.572 ps/mm")], "reference_ps_per_mm": 5.572,
         "max_mm": 9.7, "max_mm_basis": "the fixture maker's reference layout runs it at 12.50 mm, scaled to this stack"}
    e.update(more)
    return e


def t_si001_an_allowance_answers_only_with_its_basis_held():
    """CSI-D1 and CSI-D2 (with the independent check of 29 September 2026, B2 and m7): an edge_allow entry answers a
    layout-bound net only when its citation holds, as a record's must, and its max_mm is tied to what it cites. Each
    case below is refused, FAILS the reading and leaves the net layout-bound; a held entry answers, and the documents it
    cites are inputs of the reading by sha."""
    p, d = _fixture(usb_class="Default")
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "high-speed differential rise and fall times must be 500 ps or longer")
    good = _allow(repo)
    outside = os.path.join(os.path.dirname(repo), os.path.basename(repo) + "-outside")
    os.makedirs(outside, exist_ok=True)
    open(os.path.join(outside, "layout-guide.md"), "w").write(ALLOW_MD)
    cases = {"does not contain the words quoted": dict(good, quote="routed on any layer at any length"),
             "not the file the record was read from": dict(good, sha256_16="0" * 16),
             "no basis": {k: v for k, v in good.items() if k not in ("document", "sha256_16", "where", "quote")},
             "no ruled_by": dict(good, ruled_by=""),
             "no page and no clause": {k: v for k, v in good.items() if k != "where"},
             # B2: the length is tied to what the entry cites, and an entry holds a length or answers nothing
             "above what its checked rows support": dict(good, max_mm=500.0),
             "no max_mm": {k: v for k, v in good.items() if k != "max_mm"},
             "no checked row quotes the measured length": dict(good, checked=[good["checked"][1]]),
             "quoted by no checked row": dict(good, reference_ps_per_mm=7.0),
             "no reference_ps_per_mm": {k: v for k, v in good.items() if k != "reference_ps_per_mm"},
             # m7: a pattern names nets, a quote is a sentence, a PDF is cited by its page, a document is of this tree
             "names no nets": dict(good, pattern="*"),
             "shorter than 5 words": dict(good, quote="wired"),
             "with no page": dict(good, document="v2/vendor/fix/guide.pdf", where="p. 999"),
             "outside the repository": dict(good, document="../%s/layout-guide.md" % os.path.basename(outside))}
    for want, entry in cases.items():
        with _board({"critical_k": 6, "signal_classes": [HS, EN], "edge_allow": [entry]}, _src(doc)):
            r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
        assert E.schematic_result(r) == "FAIL", (want, r["fails"])
        assert any(want in f for f in r["fails"] if f.startswith("edge_allow refused")), (want, r["fails"])
        row = next(x for x in r["rows"] if x["pattern"] == "USB_*")
        assert "USB_DN" in row["layout_bound"] and r["counts"]["allowed_nets"] == 0, (want, row)
    with _board({"critical_k": 6, "signal_classes": [HS, EN],
                 "edge_allow": [good, dict(good, pattern="USB_DP")]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "PASS", (r["fails"], r["counts"])
    assert r["counts"]["allowed_nets"] == 2 and r["counts"]["answered_nets"] == 2, r["counts"]
    assert {"path": "v2/vendor/fix/layout-guide.md", "sha256_16": _s16(ALLOW_MD)} in r["inputs"].values(), r["inputs"]
    assert {"path": "v2/vendor/fix/lengths.txt", "sha256_16": _s16(ALLOW_LST)} in r["inputs"].values(), r["inputs"]


def t_si001_an_allowance_hands_its_length_to_the_layout_and_the_routed_half_holds_it():
    """CSI-D2: an entry's max_mm is the length the layout may route the nets it answers, at most the length its checked
    rows quote scaled by the delays. The schematic table hands it on (row length_limits, the evidence line ALLOWED,
    "pending the layout"); allow_answers answers a routed net only while its length is at most that and says both
    numbers when it is past it; an entry without max_mm answers nothing."""
    p, d = _fixture(usb_class="Default")
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    doc = _doc(repo, "high-speed differential rise and fall times must be 500 ps or longer")
    held = _allow(repo)
    lim, how = E.allow_limit(held, ALLOW_TPD)
    assert abs(lim - 12.5 * 5.572 / ALLOW_TPD) < 1e-6 and "12.50 mm measured" in how, (lim, how)
    assert E.allow_refusal(dict(held, max_mm=9.8), ALLOW_TPD), "a max_mm past the scaled length was held"
    assert E.allow_refusal(held, ALLOW_TPD) is None, E.allow_refusal(held, ALLOW_TPD)
    with _board({"critical_k": 6, "signal_classes": [HS, EN], "edge_allow": [held]}, _src(doc)):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "USB_*")
    assert row["length_limits"] == {"USB_DN": 9.7} and "pending the layout: at most 9.7 mm" in row["answered"]["USB_DN"], row
    out = tempfile.mkdtemp(prefix="si001-v-")
    E.write_schematic_verdict(r, out_dir=out, quiet=True, table_file=False)
    v = json.load(open(os.path.join(out, "edge_length.verdict.json")))
    assert any(e.startswith("ALLOWED 1 net(s), pending the layout") and "USB_DN <= 9.7 mm" in e for e in v["evidence"]), v["evidence"]
    ok, words = E.allow_answers(held, 9.6)
    assert ok and "within its 9.7 mm" in words, words
    ok, words = E.allow_answers(held, 9.8)
    assert not ok and "routed 9.8 mm, past the 9.7 mm" in words, words
    assert not E.allow_answers({k: v for k, v in held.items() if k != "max_mm"}, 1.0)[0], "an entry with no max_mm answered"
    for bad, want in ((dict(held, max_mm_basis=""), "no max_mm_basis"), (dict(held, max_mm=0), "not a length"),
                      (dict(held, max_mm=True), "not a length")):
        assert want in (E.allow_refusal(bad, ALLOW_TPD) or ""), (bad, E.allow_refusal(bad, ALLOW_TPD))


@contextlib.contextmanager
def _routed_stubs(nets, series=()):
    """edge_length.routed_main on a board without KiCad (the independent check's routed_stub.py, as a fixture): stub
    modules for pcbnew, intent, signalnets, impedance_check and signal_class; nets [(name, mm, class)], each one straight
    track; series [(ref, value, net a, net b)] two-pad resistors. Everything is put back."""
    import types
    class P_:
        def __init__(s, x, y): s.x, s.y = x, y
    class Tr:
        def __init__(s, net, mm): s.net, s.mm = net, mm
        def GetClass(s): return "PCB_TRACK"
        def GetNetname(s): return s.net
        def GetStart(s): return P_(0, 0)
        def GetEnd(s): return P_(int(s.mm * 1e6), 0)
        def GetLayer(s): return 0
    class Pad:
        def __init__(s, net): s.net = net
        def GetNetname(s): return s.net
    class Fp:
        def __init__(s, ref, val, a, b): s.ref, s.val, s.pads = ref, val, [Pad("/" + a), Pad("/" + b)]
        def GetReference(s): return s.ref
        def GetValue(s): return s.val
        def Pads(s): return s.pads
    class Board:
        def GetTracks(s): return [Tr("/" + n, mm) for n, mm, _c in nets]
        def GetFootprints(s): return [Fp(*x) for x in series]
    mods = {}
    m = types.ModuleType("pcbnew"); m.LoadBoard = lambda p: Board(); m.F_Cu, m.B_Cu = 0, 2; mods["pcbnew"] = m
    m = types.ModuleType("intent"); m.load = lambda p: {}; mods["intent"] = m
    m = types.ModuleType("signalnets"); m.classify = lambda b, p, r: (set(), None); m.is_signal = lambda n, s: True; mods["signalnets"] = m
    m = types.ModuleType("impedance_check"); m.read_stackup = lambda p: [("core1", "core", 0.2, 4.3)]; mods["impedance_check"] = m
    m = types.ModuleType("signal_class"); m.classify = lambda b, p, t, x: ({"/" + n: (c, "stub") for n, _mm, c in nets},); mods["signal_class"] = m
    saved = {k: sys.modules.get(k) for k in mods}
    sys.modules.update(mods)
    try: yield
    finally:
        for k, v in saved.items():
            if v is None: sys.modules.pop(k, None)
            else: sys.modules[k] = v


def _routed(nets, series=()):
    d = tempfile.mkdtemp(prefix="si001-routed-")
    path = os.path.join(d, "pcb-c-display.kicad_pcb")
    open(path, "w").write("(kicad_pcb)\n")
    with _routed_stubs(nets, series):
        E.routed_main([path])
    return json.load(open(os.path.join(d, "out", "edge_length_routed.verdict.json")))


def t_si001_the_routed_half_holds_every_allowance_net_to_its_declared_length():
    """The independent check of 29 September 2026, B1 and m10: routed_main holds EVERY net a held edge_allow entry names
    to its max_mm, on board C's committed table, whatever the net's class (none of board C's allowance classes declares a
    rise time), its critical length, or a series resistor on it. C24's lengths (QSPI_SCLK 63.82 mm, XIN 167.59 mm) FAIL;
    within the limits the reading passes. On the tool before this check the same board read INCONCLUSIVE with nothing
    over its declared limit."""
    held, refused = E.load_allow("c")
    assert not refused and {e["pattern"] for e in held} >= {"QSPI_SCLK", "QSPI_D?", "XIN"}, refused
    v = _routed([("QSPI_SCLK", 63.82, "HIGH_SPEED_DIGITAL"), ("QSPI_D0", 40.0, "HIGH_SPEED_DIGITAL"),
                 ("QSPI_D0_B", 1.0, "HIGH_SPEED_DIGITAL"), ("XIN", 5.0, "HIGH_SPEED_DIGITAL")],
                series=[("R99", "22", "QSPI_D0", "QSPI_D0_B")])
    assert v["verdict"] == "FAIL", v
    assert v["counts"]["over_declared_limit"] == 2 and v["counts"]["held_within_declared_limit"] == 1, v["counts"]
    ev = " ".join(v["evidence"])
    assert "OVER ITS DECLARED LIMIT QSPI_SCLK: routed 63.8 mm, past the 8.0 mm" in ev and "QSPI_D0: routed 40.0 mm" in ev, ev
    v2 = _routed([("QSPI_SCLK", 7.9, "HIGH_SPEED_DIGITAL"), ("XIN", 5.0, "HIGH_SPEED_DIGITAL")])
    assert v2["verdict"] == "PASS" and v2["counts"]["over_declared_limit"] == 0, v2


def t_si001_the_board_tables_allowances_hold_against_their_documents():
    """Every edge_allow entry the committed board tables carry holds (CSI-D1) and names the length it holds a net to
    with its basis wherever it states one: a refused entry would FAIL the board's reading."""
    import boardtable
    n = 0
    for letter in ("a", "b", "c", "d", "e", "p"):
        held, refused = E.load_allow(letter)
        assert not refused, (letter, refused)
        n += len(held)
        for e in held:
            assert e.get("max_mm") is None or str(e.get("max_mm_basis") or "").strip(), (letter, e["pattern"])
    assert n >= 1, "no board table carries an edge_allow entry"


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


# ------------------------------------------------------------------------------------------------------------------
# THE EDGE RATES AS DATA (27 September 2026, MESHSAT-1357, layer 9): tools/pcb_edge_rates.yaml, read per driver. The
# fixtures hand edge_length a data file of their own for one call ("zz" is a board no real record names), and a small
# IBIS file written here, so they run with no KiCad and without the held models.
# ------------------------------------------------------------------------------------------------------------------
import ibis_read as IB

FIX_IBS = """[IBIS Ver] 3.2
[File Name] fix.ibs
|  a fixture: one input, one output through a selector (3.3 V and 5 V), one open drain, ground and power
[Component] FIX_PKG
[Manufacturer] fixture
[Pin] signal_name model_name R_pin L_pin C_pin
1 A IN_33
2 Y OUT_SEL
3 GND GND
4 INT OD_33
5 VCC POWER
[Model Selector] OUT_SEL
OUT_33 3.3 V
OUT_50 5 V
[Model] IN_33
Model_type Input
[Model] OUT_33
Model_type Output
[Ramp]
dV/dt_r 1.0/0.40n 0.8/0.80n 1.2/0.30n
dV/dt_f 1.0/0.50n 0.8/0.90n 1.2/0.25n
R_load = 50
[Model] OUT_50
Model_type Output
[Ramp]
dV/dt_r 1.5/0.20n 1.2/0.40n 1.7/0.10n
dV/dt_f 1.5/0.20n 1.2/0.40n 1.7/0.10n
R_load = 50
[Model] OD_33
Model_type Open_drain
[Ramp]
dV/dt_r 1.0/0.05n 0.8/0.06n 1.2/0.04n
dV/dt_f 1.0/2.00n 0.8/3.00n 1.2/1.50n
R_load = 500
[End]
"""


def t_ibis_reader_takes_the_fastest_driven_transition_and_an_open_drain_falls_only():
    """The number is the maker's file's: the fastest 20-80 transition over the admitted models and all three corners
    (ER-D5). An open drain drives only its fall (its model's rise is the fixture pull-up); an input, ground or power pin
    drives nothing; a pin the component does not list is UNKNOWN, never a default."""
    ib = IB.parse(FIX_IBS)
    st, e, how = IB.pin_edge(ib, "FIX_PKG", "2", "_33$")
    assert st == "DRIVES" and abs(e - 0.25) < 1e-9 and "f max" in how, (st, e, how)
    st, e, _ = IB.pin_edge(ib, "FIX_PKG", "2", None)
    assert abs(e - 0.10) < 1e-9, "the filter is what keeps the 5 V model out: %s" % e
    st, e, how = IB.pin_edge(ib, "FIX_PKG", "4", "_33$")
    assert st == "DRIVES" and abs(e - 1.5) < 1e-9, "an open drain's fixture rise was read as its edge: %s %s" % (e, how)
    assert IB.pin_edge(ib, "FIX_PKG", "1", "_33$")[0] == "INPUT"
    assert IB.pin_edge(ib, "FIX_PKG", "3", "_33$")[0] == "INPUT"
    assert IB.pin_edge(ib, "FIX_PKG", "9", "_33$")[0] == "UNKNOWN"
    assert IB.pin_edge(ib, "OTHER", "2", "_33$")[0] == "UNKNOWN"
    assert IB.pin_edge(ib, "FIX_PKG", "2", "_18$")[0] == "UNKNOWN", "a filter that admits nothing must not read as an input"
    assert abs(IB.fastest(ib, "FIX_PKG", "_33$")[0] - 0.25) < 1e-9


def t_ibis_reader_reads_the_scale_suffixes_as_ibis_defines_them():
    """IBIS's M is mega and m milli: a reader that took M for milli would read ST's 40 Mohm R_load as 40 milliohm."""
    assert abs(IB.num("40.000000M") - 40e6) < 1e-3 and abs(IB.num("79.88890m") - 0.0798889) < 1e-12 and abs(IB.num("0.45102n") - 0.45102e-9) < 1e-21
    assert abs(IB.num("0.140000k") - 140.0) < 1e-9 and abs(IB.num("1.62E-09") - 1.62e-9) < 1e-21


import hashlib

MCU_MD = "The MCU datasheet: a slew-rate control bit per pad, and no transition time for either setting.\n"
SPEC_MD = "Table 9. tof output fall time from VIHmin to VILmax: Fast-mode minimum 12 ns at 3.3 V.\n"
CLAIM_MD = "The PHY datasheet: the I2C interface timing adheres to the bus specification. SCL is a clock input.\n"


def _s16(text): return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _listing_text(docs):
    """A search listing as edge_search.py writes one: a line per document with the sha256/16 it was read at."""
    return "".join("== %s (sha256/16 %s, 1 page(s)); cited by a fixture: 0 line(s)\n" % (d, _s16(t)) for d, t in docs)


LISTING = "v2/docs/records/fix/edge-search.txt"
LISTING_TEXT = _listing_text([("v2/vendor/fix/mcu.md", MCU_MD)])


@contextlib.contextmanager
def _rates(families=(), interfaces=(), far_ends=(), open_drain=(), listing=True):
    """Hand edge_length a data file of the fixture's own for one call, validated as the real one is."""
    old = (E.RATES, E.RATES_REFUSALS, E.EDGE_SOURCES)
    d = tempfile.mkdtemp(prefix="si001-rates-")
    p = os.path.join(d, "pcb_edge_rates.yaml")
    import yaml
    doc = {"interfaces": list(interfaces), "families": list(families), "far_ends": list(far_ends),
           "open_drain": list(open_drain)}
    if listing: doc["search_listing"] = {"path": LISTING, "sha256_16": _s16(LISTING_TEXT)}
    yaml.safe_dump(doc, open(p, "w"))
    rates, refusals = E.load_rates(p)
    E.RATES, E.RATES_REFUSALS, E.EDGE_SOURCES = rates, refusals, E._standards(rates)
    try: yield refusals
    finally:
        E.RATES, E.RATES_REFUSALS, E.EDGE_SOURCES = old


FIX_MODEL = "v2/vendor/fix/ibis/fix.ibs"
FIX_MANIFEST = "v2/vendor/ibis-manifest.yaml"


def _manifest_row(file=FIX_MODEL, text=None, **more):
    """One row of a model manifest as ibis_manifest accepts it, pinning `text` (the fixture model by default)."""
    text = FIX_IBS if text is None else text
    return dict({"id": "fix-model", "maker": "fixture", "part": "GATE", "file": file, "url": "https://example.invalid/fix.ibs",
                 "container": "ibs", "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "bytes": len(text.encode("utf-8")),
                 "fetched": "never: a fixture", "notice": {"kind": "COPYRIGHT_NO_GRANT", "says": "a fixture",
                                                           "quotes": [{"lines": "1", "text": "a fixture"}]}}, **more)


def _fix_repo(listing_text=None, model=True, manifest=True, rows=None, model_text=None):
    """A repository of the fixture's own: the documents, the search listing, the manifest that pins the fixture model
    (`manifest`, `rows`) and the model itself (`model`; False is the state of a clean clone, where the models are
    withheld)."""
    repo = tempfile.mkdtemp(prefix="si001-repo-")
    os.makedirs(os.path.join(repo, "v2", "vendor", "fix", "ibis"), exist_ok=True)
    os.makedirs(os.path.join(repo, os.path.dirname(LISTING)), exist_ok=True)
    if model: open(os.path.join(repo, FIX_MODEL), "w").write(FIX_IBS if model_text is None else model_text)
    if manifest:
        import yaml
        yaml.safe_dump({"schema_version": 1, "models": [_manifest_row()] if rows is None else rows},
                       open(os.path.join(repo, FIX_MANIFEST), "w"))
    open(os.path.join(repo, "v2", "vendor", "fix", "mcu.md"), "w").write(MCU_MD)
    open(os.path.join(repo, "v2", "vendor", "fix", "spec.md"), "w").write(SPEC_MD)
    open(os.path.join(repo, "v2", "vendor", "fix", "claim.md"), "w").write(CLAIM_MD)
    open(os.path.join(repo, LISTING), "w").write(LISTING_TEXT if listing_text is None else listing_text)
    return repo


def _cite(doc, text, quote, **more):
    return dict({"document": doc, "quote": quote, "sha256_16": _s16(text), "where": "the fixture's one paragraph"}, **more)


MCU_BOUND = {"id": "FIX-MCU", "kind": "BOUND", "parts": ["MCU"], "edge_ns": 0.0,
             "derivation": "the fixture MCU publishes no transition; instantaneous (ER-D8)",
             "checked": [_cite("v2/vendor/fix/mcu.md", MCU_MD, "no transition time for either setting")],
             "applicability": "the fixture MCU", "verification_owed": "a measurement"}
GATE_IBIS = {"id": "FIX-GATE", "kind": "IBIS", "parts": ["GATE"], "edge_ns": 0.25,
             "ibis": {"file": FIX_MODEL, "component": "FIX_PKG", "models": "_33$", "sha256_16": _s16(FIX_IBS),
                      "keyword": "[Model] OUT_33 [Ramp] dV/dt_f max", "ramp": "1.2/0.25n"},
             "applicability": "the fixture gate at 3.3 V", "verification_owed": "none"}


def _clk_fixture(extra_nets=(), extra_comps=None):
    """A clocked net SPI_SCK between the MCU's pin 7 and a gate's input (pin 1), and the gate's output (pin 2) on
    SPI_Q, beside the USB fixture."""
    comps = {"U3": "GATE fixture"}
    comps.update(extra_comps or {})
    nets = [("SPI_SCK", "Default", [("U2", "7"), ("U3", "1")]), ("SPI_Q", "Default", [("U3", "2"), ("U2", "8")])]
    return _fixture(extra_nets=nets + list(extra_nets), extra_comps=comps)


def t_si001_a_net_whose_driver_has_no_record_stays_undecided_and_names_it():
    p, d = _clk_fixture()
    repo = _fix_repo()
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    assert "SPI_SCK" in row["undecided"] and any("U2 MCU" in w and "no family" in w for w in row["undecided"]["SPI_SCK"]), row["undecided"]
    assert "SPI_SCK" not in row["net_edges"], "a net with an unrecorded driver was given an edge"
    assert E.schematic_result(r) == "INCONCLUSIVE"


def t_si001_a_bound_record_decides_and_the_reading_marks_it_as_a_bound():
    """A bound is a design input, never a pass: the net is decided, its basis reads BOUND, and a layout-bound net that
    only the bound holds is named under BOUND_DECIDES (ER-D8, ER-D9)."""
    p, d = _clk_fixture()
    repo = _fix_repo()
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
        out = tempfile.mkdtemp(prefix="si001-v-")
        E.write_schematic_verdict(r, out_dir=out, quiet=True, table_file=False)
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    sck = row["net_edges"]["SPI_SCK"]
    assert sck["basis"] == "BOUND" and sck["edge_ns"] == 0.0 and sck["maker_edge_ns"] is None, sck
    assert "SPI_SCK" in row["layout_bound"] and "SPI_SCK" in row["bound_decides"], row
    assert r["counts"]["bound_decided_nets"] >= 1 and r["counts"]["bound_edge_nets"] >= 1, r["counts"]
    v = json.load(open(os.path.join(out, "edge_length.verdict.json")))
    assert v["verdict"] == "INCONCLUSIVE", v["verdict"]
    assert any(e.startswith("BOUND_DECIDES") and "SPI_SCK" in e for e in v["evidence"]), v["evidence"]
    assert v["inputs"]["edge_rates"]["sha256_16"], "the data file is a configuration input and is not recorded by sha"


def t_si001_one_driver_with_no_published_minimum_makes_the_net_bound_decides_whatever_the_others_publish():
    """ER-D13, the independent check's first blocking item. SPI_Q carries the gate's output, whose maker publishes
    0.25 ns in its IBIS model, and the MCU, whose maker publishes nothing. The governing edge of a net is the fastest
    ANY driver on it can produce, and the MCU's is not known: the net is decided by a bound and named BOUND_DECIDES,
    its critical length is the bound's, and the gate's figure is recorded beside it and decides nothing."""
    p, d = _clk_fixture()
    repo = _fix_repo()
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
        out = tempfile.mkdtemp(prefix="si001-v-")
        E.write_schematic_verdict(r, out_dir=out, quiet=True, table_file=False)
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    q = row["net_edges"]["SPI_Q"]
    assert q["decided_by"] == "BOUND" and q["basis"] == "BOUND" and q["source"] == "FIX-MCU" and q["edge_ns"] == 0.0, q
    assert abs(q["maker_edge_ns"] - 0.25) < 1e-9 and "FIX-GATE" in q["maker_by"], "the maker's figure is not recorded beside the bound: %s" % q
    assert any("FIX-MCU" in x for x in q["bound_drivers"]), "the driver with no published minimum is not named: %s" % q
    assert "SPI_Q" in row["bound_decides"] and "SPI_Q" not in row["maker_holds"], row
    assert row["critical_by_net"]["SPI_Q"] == 0.0, "the critical length is not the bound's: %s" % row["critical_by_net"]
    assert E.schematic_result(r) == "INCONCLUSIVE"
    v = json.load(open(os.path.join(out, "edge_length.verdict.json")))
    assert any(e.startswith("BOUND_DECIDES") and "SPI_Q" in e for e in v["evidence"]), v["evidence"]
    assert not any(e.startswith("MAKER_HELD") and "SPI_Q" in e for e in v["evidence"]), v["evidence"]
    assert not any(e.startswith("LAYOUT_BOUND") and "SPI_Q" in e and "0.250 ns" in e for e in v["evidence"]), \
        "the net is shown under the maker's edge, which does not govern it: %s" % v["evidence"]


def t_si001_a_net_whose_every_driver_has_a_published_minimum_is_held_by_the_makers_figure():
    """The other side of ER-D13: SPI_Y carries one gate's output (0.25 ns in its maker's model) and another gate's
    input, and no part without a figure. It is decided by the maker's figure and held to the length that gives."""
    extra = [("SPI_Y", "Default", [("U4", "2"), ("U5", "1")])]
    p, d = _clk_fixture(extra_nets=extra, extra_comps={"U4": "GATE fixture", "U5": "GATE fixture"})
    repo = _fix_repo()
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    y = row["net_edges"]["SPI_Y"]
    assert y["decided_by"] == "MAKER" and y["basis"] == "IBIS" and abs(y["edge_ns"] - 0.25) < 1e-9 and not y["bound_drivers"], y
    assert "SPI_Y" in row["maker_holds"] and "SPI_Y" not in row["bound_decides"], row
    assert 5.0 < row["critical_by_net"]["SPI_Y"] < 6.5, row["critical_by_net"]
    _sums(r["counts"])
    assert r["counts"]["maker_held_nets"] == 1 and r["counts"]["maker_edge_nets"] >= 1, r["counts"]


def _sums(c):
    """The sums a reader checks the counts with."""
    assert c["signal_nets"] == c["low_speed_nets"] + c["decided_nets"] + c["undecided_nets"] + c["contradicted_nets"], c
    assert c["undecided_nets"] == c["undecided_no_declaration_nets"] + c["undecided_model_absent_nets"] + c["undecided_other_nets"], c
    assert c["decided_nets"] == c["maker_edge_nets"] + c["bound_edge_nets"], c
    assert c["may_be_long_nets"] == c["answered_nets"] + c["layout_bound_nets"], c
    assert c["layout_bound_nets"] == c["maker_held_nets"] + c["bound_decided_nets"], c


def t_si001_the_counts_sum_on_every_committed_netlist():
    """Per board: signal nets = slow + decided + undecided + contradicted; decided = by a maker's figure + by a bound;
    layout-bound = held by a maker's figure + BOUND_DECIDES. Taken in memory from the committed netlists; nothing is
    written."""
    import phase_artefacts as PA
    seen = 0
    for L in "abcdep":
        net = PA.netlist(L)
        if not (net and os.path.exists(net)): continue
        r = E.schematic_table(net, L)
        if r.get("missing_input"): continue
        _sums(r["counts"]); seen += 1
        for row in r["rows"]:
            for n in row.get("maker_holds") or []:
                e = row["net_edges"][n]
                assert e["decided_by"] == "MAKER" and e["basis"] in E.MAKER_KINDS and not e["bound_drivers"], (L, n, e)
            for n in row.get("bound_decides") or []:
                e = row["net_edges"][n]
                assert e["decided_by"] == "BOUND" and e["bound_drivers"], (L, n, e)
    assert seen, "no committed netlist was read"


def t_si001_an_ibis_record_its_own_file_contradicts_fails_the_reading():
    p, d = _clk_fixture()
    repo = _fix_repo()
    wrong = dict(GATE_IBIS, edge_ns=0.40)
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[wrong, MCU_BOUND]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "FAIL" and any("FIX-GATE" in f and "CONTRADICTED" in f for f in r["fails"]), r["fails"]


def t_si001_a_typical_or_maximum_is_not_an_edge_and_a_bound_needs_its_derivation():
    """ER-D8: only a published minimum bounds the fastest edge. The STM32H743's datasheet publishes MAXIMUM rise times
    (Table 53); a record built on one is refused, and so is a bound that says nothing about how it was reached."""
    typ = dict(_cite("v2/vendor/fix/mcu.md", MCU_MD, "slew-rate"), id="FIX-TYP", kind="DATASHEET", parts=["MCU"], edge_ns=1.5,
               statistic="max", applicability="x", verification_owed="y")
    bare = dict(MCU_BOUND, id="FIX-BARE", derivation="")
    with _rates(families=[typ, bare]) as refusals:
        pass
    assert any("FIX-TYP" in x and "MINIMUM" in x for x in refusals), refusals
    assert any("FIX-BARE" in x and "derivation" in x for x in refusals), refusals


def t_si001_a_connector_needs_its_far_end_named_and_a_series_resistor_carries_the_far_side():
    """A pin on a connector is driven from the far side (ER-D2, ER-D7): unnamed, the net is UNDECIDED naming it. And a
    net nothing drives but one series resistor away from a driven net takes that net's drivers (ER-D6)."""
    extra = [("SPI_MOSI", "Default", [("U3", "1"), ("J9", "3")]),
             ("SPI_G", "Default", [("R7", "2"), ("Q4", "1")]),
             ("SPI_D", "Default", [("R7", "1"), ("U2", "9")])]
    p, d = _clk_fixture(extra_nets=extra, extra_comps={"J9": "header", "R7": "1k", "Q4": "2N7002"})
    repo = _fix_repo()
    fe = {"id": "FIX-FAR", "board": "zz", "nets": ["SPI_MOSI"], "via": ["J9"], "families": ["FIX-MCU"],
          "basis": "the fixture's far side", "members": ["an MCU"]}
    fet = {"id": "FIX-FET", "kind": "BOUND", "parts": ["2N7002"], "edge_ns": 0.0, "inputs": "^G$", "input_pins": ["1"],
           "derivation": "a FET's drain; the gate drives nothing", "applicability": "x", "verification_owed": "y",
           "checked": [_cite("v2/vendor/fix/mcu.md", MCU_MD, "slew-rate")]}
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND, fet]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    assert any("reaches J9" in w for w in row["undecided"].get("SPI_MOSI", [])), row["undecided"]
    g = row["net_edges"].get("SPI_G")
    assert g and g["by"].startswith("across R7 from SPI_D"), row
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND, fet], far_ends=[fe]):
        r2 = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row2 = next(x for x in r2["rows"] if x["pattern"] == "SPI_*")
    assert "SPI_MOSI" in row2["net_edges"] and row2["net_edges"]["SPI_MOSI"]["by"].startswith("beyond J9"), row2


def _models_state():
    """(the manifest, {file: state}) of the real tree."""
    import ibis_manifest as IM
    man = IM.load(E.REPO)
    return man, {f: IM.state_of(E.REPO, r)[0] for f, r in man["models"].items()}


def t_si001_the_data_file_holds_against_its_documents_the_manifest_and_the_committed_netlists():
    """WHAT HOLDS IN EVERY STATE OF THE MODELS, a clean clone included (the makers' IBIS models are withheld from the
    repository): no record refused, every quoted word in its held document, every IBIS record's file PINNED by the
    tracked manifest at the sha256/16 the record cites, no pin without a record, every far end's family defined, every
    family met on a committed netlist or declared far_only, and the kit-bus far ends held to the netlists. What needs
    the models themselves is the next test, which says so when it cannot run."""
    import fnmatch, phase_artefacts as PA, ibis_manifest as IM
    rates, refusals = E.load_rates()
    assert not refusals, refusals
    man = IM.load(E.REPO)
    assert not man["why"] and not man["refusals"], (man["why"], man["refusals"])
    cited = set()
    for sect in ("interfaces", "families", "open_drain"):
        for rec in rates[sect]:
            why = E.record_holds(rec, E.REPO, rates)
            # a record that cites a model holds, or says the model is withheld; nothing else may stop it
            assert why is None or (getattr(why, "kind", None) == "MODEL_ABSENT" and why.file in man["models"]), (rec["id"], why)
            for c in E.citations(rec):
                if E.model_record(E.REPO, c["document"]) is None: continue
                row = IM.pin(man, c["document"])
                assert row is not None and row["sha256"].startswith(c["sha256_16"]), "%s cites the model %s, which the manifest does not pin at %s" % (
                    rec["id"], c["document"], c["sha256_16"])
                cited.add(c["document"])
            if rec.get("kind") == "IBIS":
                ib = rec["ibis"]
                row = IM.pin(man, ib["file"])
                assert row is not None, "%s cites %s, which the manifest does not pin" % (rec["id"], ib["file"])
                assert row["sha256"].startswith(ib["sha256_16"]), "%s cites %s at %s and the manifest pins %s" % (
                    rec["id"], ib["file"], ib["sha256_16"], row["sha256"][:16])
                cited.add(ib["file"])
            for c in E.citations(rec):
                assert c["sha256_16"] and (c["page"] or c["where"]), (rec["id"], c)
                if c["document"].lower().endswith(".pdf"): assert c["page"], "%s cites a PDF with no page: %s" % (rec["id"], c)
            if rec.get("kind") in ("STANDARD", "DATASHEET"): assert rec.get("statistic") == "min", rec["id"]
            for pe in rec.get("pin_edges") or []:
                if pe["kind"] in ("STANDARD", "DATASHEET"): assert pe.get("statistic") == "min", (rec["id"], pe)
    assert cited == set(man["models"]), "a model is pinned that no record reads, or read that is not pinned: %s" % sorted(cited ^ set(man["models"]))
    values = {}
    for L in "abcdep":
        net = PA.netlist(L)
        if net and os.path.exists(net):
            values[L] = E.read_netlist(net)
    fams = rates["families"]
    seen = {f["id"] for L, (nets, vals) in values.items() for v in vals.values() for f in [E._family_for(v, fams)] if f}
    for f in fams:
        assert f.get("far_only") or f["id"] in seen, "family %s matches no part on any committed netlist: stale" % f["id"]
    for fe in rates["far_ends"]:
        # a continuation names boards and net names that must exist on the committed netlists, or it answers nothing
        nets_here = values.get(fe["board"], ({}, {}))[0]
        assert any(fnmatch.fnmatchcase(n, pat) for pat in fe["nets"] for n in nets_here) or fe["board"] not in values, \
            "%s: board %s has no net matching %s" % (fe["id"], fe["board"], fe["nets"])
        for L2 in fe.get("continues") or []:
            nets2 = values.get(L2, ({}, {}))[0]
            for pat in fe["nets"]:
                here = [n for n in nets_here if fnmatch.fnmatchcase(n, pat)]
                assert all(n in nets2 for n in here), "%s: board %s carries no %s" % (fe["id"], L2, [n for n in here if n not in nets2])


def t_si001_the_data_file_holds_against_the_makers_models():
    """NEEDS THE MODELS, and is skipped with the reason where they are not in the tree (a clean clone, the public
    repository, a handover ZIP): every IBIS record's number, keyword, cell and flagged pins are the ones its model
    gives, each model present is the file the manifest pins, and its header says what the manifest quotes from it."""
    import ibis_manifest as IM
    man, states = _models_state()
    absent = sorted(f for f, st in states.items() if st == IM.ABSENT)
    if absent:
        raise Skip("%d of the %d makers' IBIS models are not in this tree (they are withheld from the repository and pinned by %s; "
                   "`python3 v2/ecad/tools/ibis_fetch.py --fetch` fetches them): %s" % (
                       len(absent), len(states), man["path"], ", ".join(absent)))
    assert all(st == IM.PRESENT for st in states.values()), "a model present is not the file the manifest pins: %s" % states
    for f, row in man["models"].items():
        assert IM.notice_holds(E.REPO, row) is None, IM.notice_holds(E.REPO, row)
    rates, _ = E.load_rates()
    ctx = E._Ctx("a", {}, {}, rates, E.REPO, [], set())
    for rec in rates["families"]:
        if rec.get("kind") == "IBIS":
            assert ctx.family_usable(rec) is None, (rec["id"], ctx.family_usable(rec))


def _tree_without_models():
    """A view of the real repository in which NO model is present, whatever the state of the tree the suite runs in:
    a temporary directory whose v2/vendor is the real one's children by symbolic link, the `ibis` folders left out.
    Nothing of the real tree is moved or written."""
    view = tempfile.mkdtemp(prefix="si001-nomodels-")
    real = os.path.join(E.REPO, "v2")
    os.makedirs(os.path.join(view, "v2", "vendor"))
    for name in os.listdir(real):
        if name != "vendor": os.symlink(os.path.join(real, name), os.path.join(view, "v2", name))
    for name in os.listdir(os.path.join(real, "vendor")):
        src = os.path.join(real, "vendor", name)
        if os.path.isdir(src) and os.path.isdir(os.path.join(src, "ibis")):
            os.makedirs(os.path.join(view, "v2", "vendor", name))
            for sub in os.listdir(src):
                if sub != "ibis": os.symlink(os.path.join(src, sub), os.path.join(view, "v2", "vendor", name, sub))
        else:
            os.symlink(src, os.path.join(view, "v2", "vendor", name))
    return view


def t_si001_fails_closed_on_every_committed_netlist_when_the_models_are_withheld():
    """THE STATE OF A CLEAN CLONE, asserted in every state the suite runs in: with no model in the tree no net is
    decided by an IBIS figure, every net that waits on a model is UNDECIDED naming the file (kind MODEL_ABSENT), no
    reading passes, and the reading says the state it was taken in. Nothing is written."""
    import phase_artefacts as PA
    view = _tree_without_models()
    seen = waiting = 0
    for L in "abcdep":
        net = PA.netlist(L)
        if not (net and os.path.exists(net)): continue
        r = E.schematic_table(net, L, repo=view)
        if r.get("missing_input"): continue
        seen += 1
        _sums(r["counts"])
        assert E.schematic_result(r) != "PASS", "board %s passes with no model in the tree" % L
        assert not r["fails"], (L, r["fails"][:3])
        ms = r["inputs"]["model_state"]
        assert ms["state"] in ("ABSENT", "NOT_ASKED") and ms["present"] == 0, (L, ms)
        assert ms["absent"] == r["counts"]["models_absent"] == len(ms["absent_files"]), (L, ms)
        assert not any(isinstance(v, dict) and str(v.get("path", "")).endswith(".ibs") and v.get("sha256_16")
                       for v in r["inputs"].values()), "board %s records a model it cannot have read" % L
        for row in r["rows"]:
            for n, e in (row.get("net_edges") or {}).items():
                assert e["basis"] != "IBIS", "board %s net %s is decided by an IBIS figure with no model in the tree" % (L, n)
            for n, kind in (row.get("undecided_kind") or {}).items():
                if kind != "MODEL_ABSENT": continue
                waiting += 1
                files = (row.get("undecided_models") or {}).get(n)
                assert files and all(f in ms["absent_files"] for f in files), (L, n, files)
                assert all(any(f in str(x) for f in files) for x in row["undecided"][n]), "board %s net %s does not name the absent file" % (L, n)
        assert r["counts"]["undecided_model_absent_nets"] == sum(1 for row in r["rows"] for k in (row.get("undecided_kind") or {}).values() if k == "MODEL_ABSENT")
    assert seen, "no committed netlist was read"
    assert waiting, "no net of any committed netlist waits on a model: the view is not the state it claims to be"


def t_si001_a_model_that_is_absent_decides_nothing_and_the_reading_says_which_state_it_is_in():
    """The two states on one fixture. With the model in the tree the gate's output is decided by the maker's figure and
    the reading records the model by sha with the sha that pins it; with the model withheld the same nets are UNDECIDED
    naming the file, the record's own edge_ns is NOT used in its place, and the reading says ABSENT."""
    p, d = _clk_fixture(extra_nets=[("SPI_Y", "Default", [("U3", "2"), ("R9", "1")])], extra_comps={"R9": "10k"})
    got = {}
    for state, model in (("PRESENT", True), ("ABSENT", False)):
        repo = _fix_repo(model=model)
        with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND]):
            r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
        got[state] = r
        _sums(r["counts"])
        ms = r["inputs"]["model_state"]
        assert ms["state"] == state and ms["asked"] == 1, ms
        assert r["inputs"]["ibis_manifest"]["path"] == FIX_MANIFEST and r["inputs"]["ibis_manifest"]["sha256_16"], r["inputs"]
        m = r["inputs"]["model_1"]
        assert m["path"] == FIX_MODEL and m["pinned_sha256_16"] == _s16(FIX_IBS), m
        assert not any(k.startswith("document_") and str(v.get("path", "")).endswith(".ibs") for k, v in r["inputs"].items()
                       if isinstance(v, dict)), "a model is recorded as a document"
    row = [x for x in got["PRESENT"]["rows"] if x["pattern"] == "SPI_*"][0]
    assert row["net_edges"]["SPI_Y"]["basis"] == "IBIS" and abs(row["net_edges"]["SPI_Y"]["edge_ns"] - 0.25) < 1e-9, row["net_edges"]
    assert got["PRESENT"]["inputs"]["model_1"]["sha256_16"] == _s16(FIX_IBS) and not got["PRESENT"]["inputs"]["model_1"].get("absent")
    assert got["PRESENT"]["counts"]["undecided_model_absent_nets"] == 0
    row = [x for x in got["ABSENT"]["rows"] if x["pattern"] == "SPI_*"][0]
    assert "SPI_Y" not in row["net_edges"], "the record's own edge_ns was used with no model to hold it: %s" % row["net_edges"].get("SPI_Y")
    assert row["undecided_kind"]["SPI_Y"] == "MODEL_ABSENT" and row["undecided_models"]["SPI_Y"] == [FIX_MODEL], row
    assert all(FIX_MODEL in x for x in row["undecided"]["SPI_Y"]), row["undecided"]["SPI_Y"]
    assert got["ABSENT"]["inputs"]["model_1"].get("absent") is True and not got["ABSENT"]["inputs"]["model_1"].get("sha256_16")
    assert got["ABSENT"]["counts"]["undecided_model_absent_nets"] >= 1 and got["ABSENT"]["counts"]["models_absent"] == 1
    assert E.schematic_result(got["ABSENT"]) == "INCONCLUSIVE" and not got["ABSENT"]["fails"], got["ABSENT"]["fails"]
    # a net with a model absent AND another reason is not counted as waiting on the model alone
    p2, _ = _clk_fixture(extra_nets=[("SPI_Z", "Default", [("U3", "2"), ("U8", "1")])], extra_comps={"U8": "NOBODY looked this up"})
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND]):
        r = E.schematic_table(p2, "zz", facts=FACTS, repo=_fix_repo(model=False))
    row = [x for x in r["rows"] if x["pattern"] == "SPI_*"][0]
    assert row["undecided_kind"]["SPI_Z"] == "OTHER", row["undecided_kind"]


def t_si001_a_model_is_read_only_when_the_manifest_pins_the_file_present():
    """Four ways a model is not the one pinned, each deciding nothing and saying why: no manifest, a manifest that does
    not name the file, a file present that is not the file pinned, and a record that cites another file than the
    manifest pins (the data contradicts itself: a FAIL)."""
    p, d = _clk_fixture(extra_nets=[("SPI_Y", "Default", [("U3", "2"), ("R9", "1")])], extra_comps={"R9": "10k"})
    other = FIX_IBS.replace("0.25n", "0.35n")

    def read(repo, fam=GATE_IBIS):
        with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[fam, MCU_BOUND]):
            r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
        return r, [x for x in r["rows"] if x["pattern"] == "SPI_*"][0]
    r, row = read(_fix_repo(manifest=False))
    assert "SPI_Y" in row["undecided"] and "nothing pins" in row["undecided"]["SPI_Y"][0], row["undecided"]
    assert row["undecided_kind"]["SPI_Y"] == "OTHER", "a missing manifest is not a withheld model"
    r, row = read(_fix_repo(rows=[_manifest_row(file="v2/vendor/fix/ibis/another.ibs")]))
    assert "SPI_Y" in row["undecided"] and "names no" in row["undecided"]["SPI_Y"][0], row["undecided"]
    r, row = read(_fix_repo(model_text=other))
    assert "SPI_Y" in row["undecided"] and "is not the file" in row["undecided"]["SPI_Y"][0], row["undecided"]
    assert r["inputs"]["model_state"]["state"] == "DIFFERS", r["inputs"]["model_state"]
    r, row = read(_fix_repo(rows=[_manifest_row(text=other)]))
    assert E.schematic_result(r) == "FAIL" and any("FIX-GATE" in f and "pins it at" in f for f in r["fails"]), r["fails"]
    r, row = read(_fix_repo(rows=[dict(_manifest_row(), sha256="0" * 12)]))
    assert any("model manifest refused" in f for f in r["fails"]), r["fails"]


FIX_VT = """[IBIS Ver] 3.2
[File Name] vt.ibs
[Component] VT_PKG
[Manufacturer] fixture
[Pin] signal_name model_name R_pin L_pin C_pin
1 GOOD OUT_GOOD
2 SMALLDV OUT_SMALLDV
3 SHORTDT OUT_SHORTDT
4 BARE OUT_BARE
5 VCC POWER
6 GND GND
[Model] OUT_GOOD
Model_type Output
[Ramp]
dV/dt_r 1.8/1.20n 1.8/1.20n 1.8/1.20n
dV/dt_f 1.8/1.20n 1.8/1.20n 1.8/1.20n
R_load = 500
[Rising Waveform]
R_fixture = 500
V_fixture = 0.0
0.0n 0.0 0.0 0.0
1.0n 0.6 0.6 0.6
2.2n 2.4 2.4 2.4
3.2n 3.0 3.0 3.0
[Falling Waveform]
R_fixture = 500
V_fixture = 3.0
0.0n 3.0 3.0 3.0
1.0n 2.4 2.4 2.4
2.2n 0.6 0.6 0.6
3.2n 0.0 0.0 0.0
[Model] OUT_SMALLDV
Model_type Open_drain
[Ramp]
dV/dt_r 1.8/1.20n 1.8/1.20n 1.8/1.20n
dV/dt_f 1.8/1.20n 1.8/1.20n 0.45/0.30n
R_load = 500
[Falling Waveform]
R_fixture = 500
V_fixture = 3.0
0.0n 3.0 3.0 3.0
1.0n 2.4 2.4 2.4
2.2n 0.6 0.6 0.6
3.2n 0.0 0.0 0.0
[Model] OUT_SHORTDT
Model_type Open_drain
[Ramp]
dV/dt_r 1.8/1.20n 1.8/1.20n 1.8/1.20n
dV/dt_f 1.8/1.20n 1.8/1.20n 1.8/0.24n
R_load = 500
[Falling Waveform]
R_fixture = 500
V_fixture = 3.0
0.0n 3.0 3.0 3.0
1.0n 2.4 2.4 2.4
2.2n 0.6 0.6 0.6
3.2n 0.0 0.0 0.0
[Model] OUT_BARE
Model_type Output
[Ramp]
dV/dt_r 1.8/0.90n 1.8/0.90n 1.8/0.90n
dV/dt_f 1.8/0.90n 1.8/0.90n 1.8/0.90n
R_load = 500
[End]
"""


def t_ibis_reader_holds_a_ramp_cell_to_the_models_own_vt_table():
    """A [Ramp] cell is dV/dt with dV the 20 to 80 percent swing. A cell whose dV is a quarter of that, or whose dt is a
    fifth of the time the model's own table takes between the same two levels, is CONTRADICTED by its model: the pin
    reads FLAGGED and gives no edge, also when the contradicted cell is not its fastest, and the component's fastest
    pin is taken among the pins that have a figure. A model with no table cannot be contradicted and is read."""
    ib = IB.parse(FIX_VT)
    good = ib["models"]["out_good"]
    assert IB.cell_check(good, "r", 0)[0] == "HOLDS" and IB.cell_check(good, "f", 2)[0] == "HOLDS", IB.cell_check(good, "r", 0)
    st, why = IB.cell_check(ib["models"]["out_smalldv"], "f", 2)
    assert st == "CONTRADICTED" and "15 percent" in why, (st, why)
    st, why = IB.cell_check(ib["models"]["out_shortdt"], "f", 2)
    assert st == "CONTRADICTED" and "0.20 of the time" in why, (st, why)
    assert IB.cell_check(ib["models"]["out_bare"], "r", 0)[0] == "NO_TABLE"
    assert IB.model_unchecked(ib["models"]["out_bare"]) == ["r typ", "r min", "r max", "f typ", "f min", "f max"]
    st, e, how = IB.pin_edge(ib, "VT_PKG", "1")
    assert st == "DRIVES" and abs(e - 1.2) < 1e-9, (st, e, how)
    for pin in ("2", "3"):
        st, e, how = IB.pin_edge(ib, "VT_PKG", pin)
        assert st == "FLAGGED" and e is None and "contradicted" in how, (pin, st, e, how)
    st, e, _ = IB.pin_edge(ib, "VT_PKG", "4")
    assert st == "DRIVES" and abs(e - 0.9) < 1e-9, "a model with no table is read as the file states it: %s %s" % (st, e)
    assert [p for p, _h in IB.flagged_pins(ib, "VT_PKG")] == ["2", "3"]
    e, how = IB.fastest(ib, "VT_PKG")
    assert abs(e - 0.9) < 1e-9 and "pin 4" in how, "the fastest pin is taken among the pins that have a figure: %s %s" % (e, how)
    # the contradicted cell of pin 2 is its FASTEST (0.30 ns); leaving it out would read 1.2 ns where the table may hold less
    assert IB.model_edge(ib["models"]["out_smalldv"])[0] < 1.2


def t_si001_a_pin_whose_ramp_cell_its_own_table_contradicts_takes_the_bound_and_the_record_names_it():
    """ER-D16 on a netlist: the flagged pin's net is decided by a bound at 0 ns, never by a maker's figure; the net of
    a pin that holds is decided by the maker's figure; and a record that does not name the flagged pins its own model
    gives is contradicted by it (a FAIL)."""
    vt = {"id": "FIX-VT", "kind": "IBIS", "parts": ["VTGATE"], "edge_ns": 0.9, "flagged_pins": ["2", "3"],
          "ibis": {"file": FIX_MODEL, "component": "VT_PKG", "models": ".", "sha256_16": _s16(FIX_VT),
                   "keyword": "[Model] OUT_BARE [Ramp] dV/dt_r typ", "ramp": "1.8/0.90n"},
          "applicability": "a fixture", "verification_owed": "none"}
    comps = {"U7": "VTGATE fixture", "R8": "10k", "R9": "10k"}
    nets = [("SPI_GOOD", "Default", [("U7", "1"), ("R8", "1")]), ("SPI_FLAG", "Default", [("U7", "2"), ("R9", "1")])]
    p, d = _fixture(extra_nets=nets, extra_comps=comps)
    repo = _fix_repo(model_text=FIX_VT, rows=[_manifest_row(text=FIX_VT)])
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[vt, MCU_BOUND]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert not r["fails"], r["fails"]
    row = [x for x in r["rows"] if x["pattern"] == "SPI_*"][0]
    g, f = row["net_edges"]["SPI_GOOD"], row["net_edges"]["SPI_FLAG"]
    assert g["decided_by"] == "MAKER" and g["basis"] == "IBIS" and abs(g["edge_ns"] - 1.2) < 1e-9, g
    assert f["decided_by"] == "BOUND" and f["basis"] == "BOUND" and f["edge_ns"] == 0.0 and f["maker_edge_ns"] is None, f
    assert "contradicted" in f["by"], f
    _sums(r["counts"])
    silent = dict(vt, flagged_pins=[])
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[silent, MCU_BOUND]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    assert E.schematic_result(r) == "FAIL" and any("FIX-VT" in x and "names the pins" in x for x in r["fails"]), r["fails"]


def t_si001_a_net_that_continues_onto_another_board_takes_that_boards_own_drivers_pin_by_pin():
    """The kit bus's far side is answered from the other board's netlist, pin by pin, not by each family's fastest
    pin: a family's INT pin must not stand in for its SDA (ER-D7 applies only where no board of this set is beyond)."""
    p, d = _clk_fixture()
    repo = _fix_repo()
    other = tempfile.mkdtemp(prefix="si001-other-")
    # board "yy": SPI_SCK carries the gate's INPUT pin (1) and its open-drain pin (4, fall 1.5 ns); its output (2) is elsewhere
    op = _k9(other, {"U5": "GATE fixture"}, [("SPI_SCK", "Default", [("U5", "1"), ("U5", "4"), ("J2", "1")]),
                                               ("OTHER", "Default", [("U5", "2"), ("J2", "2")])], stem="pcb-yy-si")
    t = open(p).read().replace('(node (ref "U3") (pin "1") (pintype "passive"))',
                               '(node (ref "U3") (pin "1") (pintype "passive"))\n      (node (ref "J1") (pin "5") (pintype "passive"))')
    open(p, "w").write(t)
    fe = {"id": "FIX-CONT", "board": "zz", "nets": ["SPI_SCK"], "via": ["J1"], "continues": ["yy"],
          "basis": "the fixture net continues onto board yy", "members": ["yy: GATE U5"]}
    back = {"id": "FIX-BACK", "board": "yy", "nets": ["SPI_SCK"], "via": ["J2"], "continues": ["zz"],
            "basis": "board yy's connector J2 is the same link, seen from its side", "members": ["zz: MCU U2"]}
    gate_only = dict(GATE_IBIS)
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[gate_only, MCU_BOUND], far_ends=[fe, back]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo, netlists={"yy": op})
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    e = row["net_edges"]["SPI_SCK"]
    assert e["maker_edge_ns"] is not None and abs(e["maker_edge_ns"] - 1.5) < 1e-9, \
        "the far board's open drain (1.5 ns) should be the maker's figure, not the family's fastest pin (0.25 ns): %s" % e
    assert e["decided_by"] == "BOUND", "the MCU on this board has no figure, so the bound governs the net (ER-D13): %s" % e
    assert r["inputs"].get("far_netlist_yy", {}).get("sha256_16"), "the continued board's netlist is not recorded by sha"
    # a connector of the continued board that no record names is a reason there as it is here, never silence
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[gate_only, MCU_BOUND], far_ends=[fe]):
        r2 = E.schematic_table(p, "zz", facts=FACTS, repo=repo, netlists={"yy": op})
    row2 = next(x for x in r2["rows"] if x["pattern"] == "SPI_*")
    assert any("board YY" in w and "reaches J2" in w for w in row2["undecided"].get("SPI_SCK", [])), row2["undecided"]


def t_si001_a_citation_names_the_held_file_by_sha_and_the_place_of_its_words():
    """The acceptance of the second pass: every citation carries its document, the sha256/16 of the held file, where
    in it the words are and the words. A record with no sha or no place is refused when the data file is read; one
    whose document is no longer the file it was read from decides nothing, and its nets read UNDECIDED."""
    no_sha = dict(MCU_BOUND, id="FIX-NOSHA", checked=[{"document": "v2/vendor/fix/mcu.md", "quote": "slew-rate", "where": "x"}])
    no_place = dict(MCU_BOUND, id="FIX-NOPLACE", checked=[{"document": "v2/vendor/fix/mcu.md", "quote": "slew-rate", "sha256_16": _s16(MCU_MD)}])
    no_kw = dict(GATE_IBIS, id="FIX-NOKW", ibis={k: v for k, v in GATE_IBIS["ibis"].items() if k != "keyword"})
    with _rates(families=[no_sha, no_place, no_kw]) as refusals:
        pass
    assert any("FIX-NOSHA" in x and "sha256_16" in x for x in refusals), refusals
    assert any("FIX-NOPLACE" in x and "no page" in x for x in refusals), refusals
    assert any("FIX-NOKW" in x and "keyword" in x for x in refusals), refusals
    p, d = _clk_fixture()
    repo = _fix_repo()
    open(os.path.join(repo, "v2", "vendor", "fix", "mcu.md"), "a").write("A later revision adds a line.\n")
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    assert any("is not the file the record was read from" in w for w in row["undecided"].get("SPI_SCK", [])), row["undecided"]
    # and an IBIS record whose keyword or cell is not the file's is contradicted, a FAIL
    repo2 = _fix_repo()
    wrong = dict(GATE_IBIS, ibis=dict(GATE_IBIS["ibis"], ramp="1.2/0.26n"))
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[wrong, MCU_BOUND]):
        r3 = E.schematic_table(p, "zz", facts=FACTS, repo=repo2)
    assert E.schematic_result(r3) == "FAIL" and any("FIX-GATE" in f and "cell" in f for f in r3["fails"]), r3["fails"]


def t_si001_a_bound_shows_its_documents_were_searched():
    """A quote of the part's name proves a document is held, not that anyone looked in it for a transition time (the
    independent check of 27 September 2026). A bound decides only while the data file's search listing holds every
    document it cites at the held file's sha256/16."""
    p, d = _clk_fixture()
    for listing_text, rates_kw, want in (
            (_listing_text([]), {}, "the search listing does not hold v2/vendor/fix/mcu.md"),
            (_listing_text([("v2/vendor/fix/mcu.md", "an older text")]), {}, "the search listing read v2/vendor/fix/mcu.md at"),
            (None, {"listing": False}, "the data file names no search listing")):
        repo = _fix_repo(listing_text)
        with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND], **rates_kw):
            if listing_text is not None: E.RATES["search_listing"]["sha256_16"] = _s16(listing_text)
            r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
        row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
        assert any(want in w for w in row["undecided"].get("SPI_SCK", [])), (want, row["undecided"])


def t_si001_a_specification_binds_a_part_only_where_its_maker_claims_it():
    """ER-D14. UM10204's minimum fall is a published figure for a part whose own datasheet claims the specification's
    timing; for any other part it is somebody else's number. A STANDARD row with no quoted claim is refused; with one,
    the pin takes the figure, its clock input drives nothing, and the net is the maker's."""
    row = dict(_cite("v2/vendor/fix/spec.md", SPEC_MD, "Fast-mode minimum 12 ns at 3.3 V"), match="^SDA$", kind="STANDARD",
               edge_ns=12.0, statistic="min")
    base = {"id": "FIX-PHY", "kind": "BOUND", "parts": ["PHY"], "edge_ns": 0.0, "inputs": "^SCL$",
            "inputs_cited": [_cite("v2/vendor/fix/claim.md", CLAIM_MD, "SCL is a clock input.")],
            "derivation": "the fixture PHY publishes no transition of its own", "applicability": "x", "verification_owed": "y",
            "checked": [_cite("v2/vendor/fix/mcu.md", MCU_MD, "slew-rate")]}
    unclaimed = dict(base, id="FIX-UNCLAIMED", pin_edges=[row])
    claimed = dict(base, pin_edges=[dict(row, claimed_by=_cite("v2/vendor/fix/claim.md", CLAIM_MD, "the I2C interface timing adheres to the bus specification"))])
    with _rates(families=[unclaimed]) as refusals:
        pass
    assert any("FIX-UNCLAIMED" in x and "claims" in x for x in refusals), refusals
    d = tempfile.mkdtemp(prefix="si001-")
    comps = {"U7": "PHY fixture", "U8": "PHY fixture", "R1": "2.2k"}
    nets = [("SPI_SDA", "Default", [("U7", "1"), ("U8", "1"), ("R1", "1")]), ("SPI_SCL", "Default", [("U7", "2"), ("U8", "2")]),
            ("+3V3", "Default", [("R1", "2"), ("U7", "3")]), ("GND", "Default", [("U7", "4"), ("U8", "4")])]
    p = _k9(d, comps, nets)
    t = open(p).read()
    for ref in ("U7", "U8"):
        t = t.replace('(node (ref "%s") (pin "1") (pintype "passive"))' % ref, '(node (ref "%s") (pin "1") (pinfunction "SDA") (pintype "passive"))' % ref)
        t = t.replace('(node (ref "%s") (pin "2") (pintype "passive"))' % ref, '(node (ref "%s") (pin "2") (pinfunction "SCL") (pintype "passive"))' % ref)
    open(p, "w").write(t)
    repo = _fix_repo()
    rise = {"id": "FIX-RISE", "nets": {"zz": ["SPI_SDA"]}, "fall": "the pull-downs of the families",
            "rise": dict(_cite("v2/vendor/fix/spec.md", SPEC_MD, "Table 9."), kind="MODEL", edge_ns=150.0, measure="30 to 70 percent",
                         derivation="0.8473 Rp Cb with the fixture's values",
                         checked=[_cite("v2/vendor/fix/mcu.md", MCU_MD, "slew-rate")]),
            "applicability": "the fixture bus", "verification_owed": "a measurement"}
    with _board({"critical_k": 6, "signal_classes": [CK]}, ()), _rates(families=[claimed], open_drain=[rise]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row_ = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    sda = row_["net_edges"]["SPI_SDA"]
    assert sda["decided_by"] == "MAKER" and sda["basis"] == "STANDARD" and abs(sda["edge_ns"] - 12.0) < 1e-9, sda
    # AN OPEN-DRAIN NET HAS TWO EDGES: the rise is stated beside the fall and never governs
    assert sda["rising"]["edge_ns"] == 150.0 and sda["rising"]["basis"] == "MODEL" and sda["rising"]["source"] == "FIX-RISE", sda
    assert abs(sda["edge_ns"] - 12.0) < 1e-9, "the rise was taken as the governing edge: %s" % sda
    assert any("no part on the net" in w for w in row_["undecided"].get("SPI_SCL", [])), \
        "two clock INPUTS and no driver: the net has no edge to take, and says so: %s" % row_["undecided"]


def t_si001_a_passive_switch_pin_that_is_neither_through_nor_control_is_named():
    sw = {"id": "FIX-SW", "kind": "PASSIVE_SWITCH", "parts": ["SWITCH"], "through_pins": ["1", "3"], "input_pins": ["4"],
          "basis": "a fixture switch: pins 1 and 3 pass, pin 4 selects"}
    extra = [("SPI_A", "Default", [("U6", "1"), ("J9", "1")]), ("SPI_SEL", "Default", [("U6", "4"), ("U3", "2")]),
             ("SPI_ODD", "Default", [("U6", "7"), ("U3", "1")])]
    p, d = _clk_fixture(extra_nets=extra, extra_comps={"U6": "SWITCH fixture", "J9": "header"})
    repo = _fix_repo()
    fe = {"id": "FIX-FAR", "board": "zz", "nets": ["SPI_A"], "via": ["U6", "J9"], "families": ["FIX-MCU"],
          "basis": "the fixture's far side", "members": ["an MCU"]}
    with _board({"critical_k": 6, "signal_classes": [HS, EN, CK]}, ()), _rates(families=[GATE_IBIS, MCU_BOUND, sw], far_ends=[fe]):
        r = E.schematic_table(p, "zz", facts=FACTS, repo=repo)
    row = next(x for x in r["rows"] if x["pattern"] == "SPI_*")
    assert row["net_edges"]["SPI_A"]["by"].startswith("beyond"), row["net_edges"].get("SPI_A")
    assert row["net_edges"]["SPI_SEL"]["decided_by"] == "MAKER", "a control input of the switch drives nothing: %s" % row["net_edges"].get("SPI_SEL")
    assert any("neither a through pin nor a control input" in w for w in row["undecided"].get("SPI_ODD", [])), row["undecided"]


def t_ibis_reader_fails_closed_on_an_untyped_model_and_reads_both_spellings_of_a_keyword():
    """The independent check's finding: a model with no Model_type read as an input, and [Model_Selector] spelled with
    an underscore was not read at all. Both now answer UNKNOWN or the right model, never silence."""
    untyped = FIX_IBS.replace("[Model] OUT_33\nModel_type Output\n", "[Model] OUT_33\n")
    assert untyped != FIX_IBS
    st, e, how = IB.pin_edge(IB.parse(untyped), "FIX_PKG", "2", "_33$")
    assert st == "UNKNOWN" and "Model_type" in how, (st, how)
    under = FIX_IBS.replace("[Model Selector] OUT_SEL", "[Model_Selector] OUT_SEL")
    assert under != FIX_IBS
    st, e, how = IB.pin_edge(IB.parse(under), "FIX_PKG", "2", "_33$")
    assert st == "DRIVES" and abs(e - 0.25) < 1e-9, (st, e, how)
    assert IB.fastest_cite(IB.parse(FIX_IBS), "FIX_PKG", "_33$") == ("[Model] OUT_33 [Ramp] dV/dt_f max", "1.2/0.25n")


def t_si001_every_edge_of_the_data_file_carries_what_the_acceptance_asks():
    """The acceptance of 27 September 2026, held on the real data file: every edge carries its document (the file, its
    sha256/16, the page or the IBIS keyword), the words or the numbers quoted, its conditions or its derivation, its
    applicability and the verification still owed; only a MINIMUM is a published figure; a bound that cites no
    document says that none is held."""
    rates, refusals = E.load_rates()
    assert not refusals, refusals
    seen = 0

    def held(rid, rec, kind, parent=None):
        par = parent or {}
        if kind == "IBIS":
            ib = rec["ibis"]
            assert ib.get("file") and ib.get("sha256_16") and ib.get("keyword") and ib.get("ramp"), rid
        else:
            cites = E.citations(rec) if parent is None else E.citations({"checked": [rec]})
            assert cites or rec.get("no_document") or par.get("checked"), "%s gives an edge and cites nothing" % rid
            for c in cites:
                assert c["sha256_16"] and c["quote"] and (c["page"] or c["where"]), (rid, c)
        assert rec.get("conditions") or rec.get("derivation"), "%s states neither its conditions nor its derivation" % rid
        assert rec.get("applicability") or par.get("applicability"), "%s states no applicability" % rid
        assert rec.get("verification_owed") or par.get("verification_owed"), "%s states no verification owed" % rid
        if kind in ("STANDARD", "DATASHEET"): assert rec.get("statistic") == "min", "%s is a published figure that is not a minimum" % rid
        if kind in E.BOUND_KINDS: assert float(rec["edge_ns"]) >= 0 and rec.get("derivation"), rid

    for r in rates["interfaces"]:
        held(r["id"], r, r["kind"]); seen += 1
    for r in rates["families"]:
        if r["kind"] in E.EDGE_KINDS:
            held(r["id"], r, r["kind"]); seen += 1
        for j, pe in enumerate(r.get("pin_edges") or []):
            held("%s pin_edges[%d]" % (r["id"], j), pe, pe["kind"], r); seen += 1
    for r in rates["open_drain"]:
        held(r["id"] + " rise", dict(r["rise"], applicability=r["applicability"], verification_owed=r["verification_owed"]), r["rise"]["kind"])
        seen += 1
    assert seen >= 60, "the data file holds %d edges: it was not read whole" % seen
