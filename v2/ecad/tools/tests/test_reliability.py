#!/usr/bin/env python3
"""What carries load and what sees cycling (rule REL-001, 16 September 2026; the inventory, 28 September 2026).

The kit is carried, so every connector mated in the field is a wear item and every board-mounted jack is a
lever with the case as its fulcrum. The rule asks for the list per board with the cycles, the load and the
measure; it read "no verification" on seven boards.

The check that makes it a gate is completeness, and until 28 September 2026 its denominator was the parts whose
VALUE TEXT matched twelve words. The independent review of handover H3 (finding H3-01) showed an undeclared
"RJ45 MagJack" reading PASS, and a board with no netlist reading PASS of zero parts. The population is now an
inventory by reference class and land (`wear_inventory.py`), a missing input is INCONCLUSIVE, and the netlist is
the declared phase's, recorded by sha. The tests of the inventory itself are in test_reliability_inventory.py.

Every fixture is its own temporary tree with its own manifest, profiles, vendor folder and list; nothing is
written in this tree. It tests nothing physical, and says so: REL-001 is verified at the PROTOTYPE and no board
has been built.
"""
import os, sys, json, hashlib, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import reliability as REL

DOC = b"%PDF-1.4 a fixture document of test_reliability.py\n"
SHA = hashlib.sha256(DOC).hexdigest()[:16]
# The land a fixture part gets when its test names none, by reference class: a connector land for a J, a
# soldered package for a U. A part given as (value, land) keeps the land it names; ("value", "") has no land.
LANDS = {"J": "Connector_Generic:Conn_01x02", "U": "Package_TO_SOT_SMD:SOT-23-5", "D": "Diode_SMD:D_SMC",
         "TP": "TestPoint:TestPoint_Pad_D1.0mm", "F": "Fuse:Fuse_1812_4532Metric"}


def _net(comps):
    import wear_inventory as WI
    c, n, code = "", "", 0
    for r, v in sorted(comps.items()):
        value, land = v if isinstance(v, tuple) else (v, LANDS.get(WI.ref_class(r), ""))
        c += '    (comp (ref "%s")\n      (value "%s")%s)\n' % (r, value, ('\n      (footprint "%s")' % land) if land else "")
        code += 1
        n += '    (net (code "%d") (name "/N%d")\n      (node (ref "%s") (pin "1") (pintype "passive")))\n' % (code, code, r)
    return '(export (version "E")\n  (components\n%s  )\n  (nets\n%s  )\n)\n' % (c, n)


def _tree(comps, stem="pcb-x-test", letter="x", phase=None, text=None, no_chain=False):
    """A fixture world: ecad/<phase or stem>/out/<stem>.net, its own manifest, profiles and vendor folder."""
    d = tempfile.mkdtemp(prefix="rel-")
    ecad = os.path.join(d, "ecad"); prj = os.path.join(ecad, phase or stem)
    os.makedirs(os.path.join(prj, "out")); os.makedirs(os.path.join(d, "vendor", "fixture"))
    os.makedirs(os.path.join(d, "profiles", "routeflow"))
    open(os.path.join(d, "vendor", "fixture", "doc.pdf"), "wb").write(DOC)
    if comps is not None or text is not None:
        open(os.path.join(prj, "out", stem + ".net"), "w", encoding="utf-8").write(_net(comps) if text is None else text)
    b = {"project": stem, "required": True}
    if no_chain: b["no_chain"] = True
    json.dump({"boards": {letter: b}}, open(os.path.join(d, "manifest.json"), "w"))
    if phase:
        json.dump({"board": stem, "project": "v2/ecad/" + phase},
                  open(os.path.join(d, "profiles", "routeflow", letter + ".json"), "w"))
    return d


def _pin(d, sheet, letters=("x", "a", "y", "q")):
    """The fixture list bound to the fixture artefact it is judged against (`written_against`, 28 September 2026),
    the way the committed list is bound to the committed netlists: for every board key the sheet declares whose
    declared phase's artefact exists in the fixture, its sha256 goes under the key. A sheet that already carries a
    pin is left as written (the mismatch tests write their own)."""
    if "written_against" in sheet: return sheet
    import wear_inventory as WI
    with WI.declared(os.path.join(d, "manifest.json"), os.path.join(d, "profiles")):
        for L in letters:
            key = " %s:\n" % L
            if key not in sheet: continue
            kind, path = WI.artefact(L, os.path.join(d, "ecad"))
            if not path or not os.path.isfile(path): continue
            try: _parts, raw = WI.read(kind, path)
            except WI.Unreadable: continue
            sheet = sheet.replace(key, key + '   written_against: {sha256_16: "%s"}\n' % hashlib.sha256(raw).hexdigest()[:16], 1)
    return sheet


def _judge(d, sheet, letter="x", vendor=True, pin=True):
    p = os.path.join(d, "rel.yaml"); open(p, "w", encoding="utf-8").write(_pin(d, sheet) if pin else sheet)
    return REL.judge(p, os.path.join(d, "ecad"), letter, vendor=os.path.join(d, "vendor") if vendor else os.path.join(d, "none"),
                     manifest=os.path.join(d, "manifest.json"), profiles=os.path.join(d, "profiles"))


def _run(sheet, comps, **kw):
    return _judge(_tree(comps, **kw), sheet)["x"]


def _cli(d, sheet, letter="x", extra=()):
    """The command line, in process: (exit code, the verdict it wrote). The verdict goes to the fixture."""
    p = os.path.join(d, "rel.yaml"); open(p, "w", encoding="utf-8").write(_pin(d, sheet))
    out = os.path.join(d, "verdicts")
    rc = REL.main(["--rel", p, "--ecad", os.path.join(d, "ecad"), "--board", letter, "--vendor", os.path.join(d, "vendor"),
                   "--manifest", os.path.join(d, "manifest.json"), "--profiles", os.path.join(d, "profiles"),
                   "--out-dir", out] + list(extra))
    return rc, json.load(open(os.path.join(out, "reliability.verdict.json")))


SRC = 'source: {document: "v2/vendor/fixture/doc.pdf", sha256_16: "%s", page: "1", words: "the figure"}' % SHA
HEAD = """
schema_version: "2.0.0"
inventory:
  reference_classes:
    J:  {kind: mechanical, what: "a connector"}
    F:  {kind: mechanical, what: "a fuse"}
    TP: {kind: mechanical, what: "a test point"}
    U:  {kind: electrical, what: "an integrated circuit or a module"}
    D:  {kind: electrical, what: "a diode"}
  footprint:
    mechanical_libraries: ["Connector*", "TestPoint*"]
    mechanical_names: ["*Conn*", "*Socket*"]
    soldered_libraries: ["Package_*", "Diode_*"]
    soldered_names: ["Fixture_Module"]
open_items:
  O-1: {what: "the part is not picked", next_action: "pick it and file its sheet"}
boards:
 x:
   classes:
"""
GOOD = HEAD + ('    - {name: "the jacks", refs: ["J_RF*"], cycles: 500, %s, basis: "the SMA standard", '
               'load: "a wrench", measure: "the case wall takes it"}\n' % SRC)
POWER = '    - {name: "power", refs: ["J_PWR*"], cycles: 30, %s, basis: "JST VH", load: "a lead", measure: "a tie"}\n' % SRC


def t_a_wear_part_in_no_class_is_refused():
    """THE DEFECTIVE FIXTURE: two jacks declared, a third connector on the board and nobody has looked at it."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "J_RF2": "SMA jack", "J_PWR1": "JST-VH socket"})
    assert any("J_PWR1" in f for f in r["fails"]), r["fails"]


def t_the_same_board_with_every_class_declared_passes():
    r = _run(GOOD + POWER, {"J_RF1": "SMA jack", "J_PWR1": "JST-VH socket"})
    assert not r["fails"], r["fails"]
    assert r["result"] == "PASS", r


def t_a_class_with_no_cycle_figure_must_say_why():
    sheet = GOOD.replace("cycles: 500", "cycles: null")
    r = _run(sheet, {"J_RF1": "SMA jack"})
    assert any("does not say why" in f for f in r["fails"]), r["fails"]
    # A SENTENCE IN `basis` IS NOT A REASON ANY MORE (28 September 2026). The gate used to accept a class with no
    # figure when its basis carried the letters "no " or "not ", which is a search in prose. The reason is a
    # declared kind now: the maker's documents that were read state none, nothing is mated, or it is owed.
    prose = GOOD.replace('cycles: 500, %s, basis: "the SMA standard"' % SRC,
                         'cycles: null, basis: "no mating-cycle figure is published for this part"')
    assert prose != GOOD
    r1 = _run(prose, {"J_RF1": "SMA jack"})
    assert any("does not say why" in f for f in r1["fails"]), r1["fails"]
    sheet2 = GOOD.replace('cycles: 500, %s' % SRC,
                          'cycles: null, no_figure: {kind: none_published, statement: "the catalogue gives none", '
                          'looked_in: [{document: "v2/vendor/fixture/doc.pdf", sha256_16: "%s"}]}' % SHA)
    assert sheet2 != GOOD
    r2 = _run(sheet2, {"J_RF1": "SMA jack"})
    assert not r2["fails"] and r2["result"] == "PASS", r2
    # and it says WHERE it looked, or it is refused
    sheet3 = sheet2.replace(', looked_in: [{document: "v2/vendor/fixture/doc.pdf", sha256_16: "%s"}]' % SHA, "")
    assert sheet3 != sheet2
    r3 = _run(sheet3, {"J_RF1": "SMA jack"})
    assert any("does not say where it looked" in f for f in r3["fails"]), r3["fails"]


def t_a_class_without_a_load_or_a_measure_is_refused():
    for k in ("load", "measure"):
        sheet = GOOD.replace('%s: "%s"' % (k, {"load": "a wrench", "measure": "the case wall takes it"}[k]), '%s: ""' % k)
        assert sheet != GOOD
        r = _run(sheet, {"J_RF1": "SMA jack"})
        assert any(("carries no %s" % k) in f for f in r["fails"]), (k, r["fails"])


def t_a_declared_count_that_does_not_match_the_board_is_refused():
    sheet = GOOD.replace('refs: ["J_RF*"]', 'refs: ["J_RF*"], count_expected: 3')
    r = _run(sheet, {"J_RF1": "SMA jack", "J_RF2": "SMA jack"})
    assert any("expects 3" in f for f in r["fails"]), r["fails"]


# THE PART'S IDENTITY DECIDES, NOT THE DESCRIPTION OF WHAT IT DOES (27 September 2026). A value is written
# `<the part and its properties>: <what it does in this circuit>`. The word list was searched in all of it, so
# three AND gates on board B whose description says they enable a card SOCKET's supply were refused as
# load-bearing parts in no declared class, and the set 6 candidate's suite read 2010 passed, 1 failed.
# Since 28 September 2026 the words are the SECOND net below the inventory, and these cases hold there: the gate
# is on its own land, a SOT-23-5, which the inventory declares soldered.
GATE = ("SN74LV1T08DBVR AND, 5 V supply, TTL-level inputs (1 A 2 B 3 GND 4 Y 5 VCC): slot 1's card-socket supply "
        "enable = EMCON AND PCIE_PWR_EN1, run from +5V_S1, that supply's own input (W4B-D3)")


def t_a_logic_gate_that_enables_a_sockets_supply_is_no_wear_part():
    """THE DEFECTIVE READING, on board B's own text: `U116` beside one declared jack. The board passes with no
    class for the gate, the jack is still counted, and the gate is NAMED as set aside rather than dropped in
    silence. The unfixed tool fails the first assertion with the refusal the box suite printed."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "U116": GATE})
    assert not r["fails"], r["fails"]
    assert r["covered"] == 1, r
    assert r["prose_only"] == ["U116"], r
    assert any("U116" in n and "description" in n for n in r["notes"]), r["notes"]


def t_a_real_socket_with_a_description_after_the_colon_is_still_a_wear_part():
    """THE ACCEPTABLE READING the change must not lose: the socket is named BEFORE the colon. It holds on the
    unfixed tool too, which is what makes it the control of the test above."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "J5": "M.2 key-E socket (TE 2199230-4): WiFi card"})
    assert any("J5" in f and "in no declared class" in f for f in r["fails"]), r["fails"]
    assert r["covered"] == 1, r


def t_a_module_receptacle_is_a_wear_part_though_its_reference_is_a_u():
    """Why a prefix cannot decide this: a receptacle drawn as `U30A` and a logic gate drawn as `U116` share
    theirs, and `U` must stay out of NOT_WEAR_PREFIX. It holds on the unfixed tool too. Here the receptacle sits
    on a land the inventory declares SOLDERED, the worst case: the land says nothing, and the word net finds it."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "U30A": "CM5 receptacle DF40HC(3.0)-100DS-0.4V: module connector A"})
    assert any("U30A" in f and "in no declared class" in f for f in r["fails"]), r["fails"]
    assert r["by_words"] == ["U30A"], r
    sheet = GOOD + '    - {name: "module", refs: ["U30*"], cycles: 30, %s, basis: "Hirose DF40", load: "the module", measure: "four screws"}\n' % SRC
    r2 = _run(sheet, {"J_RF1": "SMA jack", "U30A": "CM5 receptacle DF40HC(3.0)-100DS-0.4V: module connector A"})
    assert not r2["fails"] and r2["covered"] == 2, r2


def t_a_colon_inside_a_bracket_does_not_end_the_identity():
    """89 of the 2630 values of the six netlists carry their first colon inside a bracket, which is a remark on
    the part. A plain split at the first colon would cut the identity there and DROP a connector named in the
    remark, in silence, which is the direction a completeness gate must never fail in."""
    v = "fan lead (mates: JST-SH socket of the cooler): 5V GND TACHO PWM"
    r = _run(GOOD, {"J_RF1": "SMA jack", "J_FAN1": v})
    assert any("J_FAN1" in f for f in r["fails"]), r["fails"]
    assert REL.identity(v) == "fan lead (mates: JST-SH socket of the cooler)", REL.identity(v)
    for value, want in (
            ("USB-C 2.0 receptacle", "USB-C 2.0 receptacle"),                        # no colon: all identity
            ("SMCJ40A (bus clamp: 40 V standoff on the bus)", "SMCJ40A (bus clamp: 40 V standoff on the bus)"),
            ("lead (JST-VH: + -", "lead (JST-VH: + -"),                              # a bracket that never closes
            ("ratio 1:1 transformer: the link", "ratio 1:1 transformer"),            # a colon with no space after it
            ("U.FL: MHF4 pigtail: chain A", "U.FL"),                                 # the FIRST such colon
            (GATE, "SN74LV1T08DBVR AND, 5 V supply, TTL-level inputs (1 A 2 B 3 GND 4 Y 5 VCC)"),
            ("", ""), (None, "")):
        assert REL.identity(value) == want, (value, REL.identity(value))
    # and on a soldered land, where only the words can find it: the remark's socket still asks for the part
    r2 = _run(GOOD, {"J_RF1": "SMA jack", "U9": v})
    assert any("U9" in f for f in r2["fails"]) and r2["by_words"] == ["U9"], r2


def t_a_diodes_standoff_voltage_is_never_a_wear_word():
    """16 September 2026, kept: a transient suppressor's value says what it STANDS OFF."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "D2": "SMCJ40A (40 V standoff on a line specified to 36 V)"})
    assert not r["fails"] and r["candidates"] == 1 and r["prose_only"] == [] and r["by_words"] == [], r


# ------------------------------------------------------------------------------------------------------------------
# THE REVIEWER'S FOUR-CASE MATRIX (the independent review of handover H3, finding H3-01), through the command
# line as the reviewer ran it: the board is `a`, its netlist sits in the stem's own directory, and the verdict and
# the exit code are read. v2/docs/records/d6rel/matrix-on-unrepaired-tool.txt holds the same four cases on the tool
# as it was at 73ae2f21: cases 3 and 4 read PASS, exit 0.
# ------------------------------------------------------------------------------------------------------------------
JST = ("JST-VH socket, 10 A: 5 V from the fixture: + -", "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical")
IDC = ("fixture ribbon (IDC 2x5)", "Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical")
RJ45 = ("RJ45 MagJack", "Connector_RJ:RJ45_Amphenol_RJHSE5380")
ONE_JST = HEAD.replace(" x:\n", " a:\n") + (
    '    - {name: "the power header", refs: ["J_PWR1"], footprints: ["Connector_JST:JST_VH_*"], cycles: 30, %s, '
    'load: "a lead pulled during service", measure: "the lead is tied beside the header"}\n' % SRC)


def _matrix(comps, sheet=ONE_JST):
    d = _tree(comps, stem="pcb-a-power", letter="a")
    return _cli(d, sheet, "a")


def t_matrix_1_one_declared_jst_connector_passes():
    rc, v = _matrix({"J_PWR1": JST})
    assert rc == 0 and v["verdict"] == "PASS", (rc, v["verdict"], v["evidence"])
    assert v["counts"]["candidates"] == 1 and v["counts"]["classed"] == 1 and v["counts"]["refused"] == 0, v["counts"]
    assert v["denominator"] == 1, v["denominator"]


def t_matrix_2_an_undeclared_idc_header_fails():
    rc, v = _matrix({"J_PWR1": JST, "J_RIB1": IDC})
    assert rc == 1 and v["verdict"] == "FAIL", (rc, v["verdict"])
    assert v["counts"]["refused"] == 1 and any("J_RIB1" in e for e in v["evidence"]), v


def t_matrix_3_an_undeclared_rj45_magjack_fails():
    """SILENT ON THE UNREPAIRED TOOL: `RJ45 MagJack` carries none of the twelve words, so the part left the
    denominator and the board read PASS of one covered part. It is a J on a connector land: a candidate."""
    assert not REL.WEAR.search(RJ45[0]), "the fixture must be a value the word list does not find"
    rc, v = _matrix({"J_PWR1": JST, "J_ETH": RJ45})
    assert rc == 1 and v["verdict"] == "FAIL", (rc, v["verdict"])
    assert v["counts"]["candidates"] == 2 and v["counts"]["refused"] == 1, v["counts"]
    assert any("J_ETH" in e and "in no declared class" in e for e in v["evidence"]), v["evidence"]


def t_matrix_4_a_declaration_with_no_netlist_is_inconclusive():
    """SILENT ON THE UNREPAIRED TOOL: board A's declaration and no netlist read PASS of zero covered parts.
    Board A's own committed declaration is used, as the reviewer did."""
    import yaml
    real = yaml.safe_load(open(REL.REL, encoding="utf-8"))
    real["boards"] = {"a": real["boards"]["a"]}
    d = _tree(None, stem="pcb-a-power", letter="a")
    p = os.path.join(d, "rel.yaml"); open(p, "w", encoding="utf-8").write(yaml.safe_dump(real))
    out = os.path.join(d, "verdicts")
    rc = REL.main(["--rel", p, "--ecad", os.path.join(d, "ecad"), "--board", "a", "--manifest", os.path.join(d, "manifest.json"),
                   "--profiles", os.path.join(d, "profiles"), "--out-dir", out])
    v = json.load(open(os.path.join(out, "reliability.verdict.json")))
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE", (rc, v["verdict"], v["evidence"])
    assert v["missing_input"] and "no netlist of its declared phase" in v["missing_input"], v["missing_input"]
    assert v["denominator"] == 0 and v["counts"]["classed"] == 0 and v["counts"]["candidates"] == 0, v
    assert "netlist" not in v["inputs"], "a netlist is recorded that was never read: %r" % v["inputs"]


# ------------------------------------------------------------------------------------------------------------------
# EVERY CANDIDATE IS DISPOSED: exactly one class, or one exclusion that gives its reason and its land
# ------------------------------------------------------------------------------------------------------------------
EXCL = ('   exclusions:\n    - {refs: ["TP*"], footprints: ["TestPoint:*"], reason: "a test point: a bare pad touched '
        'by a probe, nothing is mated"}\n')


def t_a_candidate_excluded_with_a_reason_is_no_refusal_and_is_printed():
    d = _tree({"J_RF1": "SMA jack", "TP1": "probe", "TP2": "probe"})
    r = _judge(d, GOOD + EXCL)["x"]
    assert not r["fails"] and r["result"] == "PASS", r
    assert r["candidates"] == 3 and r["covered"] == 1 and r["excluded"] == 2 and r["refused"] == 0, r
    assert r["excluded_by"] == [{"refs": ["TP*"], "parts": ["TP1", "TP2"],
                                 "reason": "a test point: a bare pad touched by a probe, nothing is mated"}], r["excluded_by"]
    # ...and the READING carries it: on the terminal and in the verdict's evidence
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc, v = _cli(d, GOOD + EXCL)
    assert rc == 0 and v["counts"]["excluded"] == 2, (rc, v["counts"])
    assert "excluded X: 2 part(s), TP1, TP2: a test point" in buf.getvalue(), buf.getvalue()
    assert any("2 part(s) excluded (TP1, TP2): a test point" in e for e in v["evidence"]), v["evidence"]
    # the same board with no exclusion declared: the two test points are refused, they are not dropped
    r0 = _run(GOOD, {"J_RF1": "SMA jack", "TP1": "probe", "TP2": "probe"})
    assert len([f for f in r0["fails"] if "TP" in f]) == 2 and r0["refused"] == 2, r0["fails"]


def t_an_exclusion_with_no_reason_is_refused():
    for bad in ('reason: ""', "reason: null"):
        sheet = GOOD + EXCL.replace('reason: "a test point: a bare pad touched by a probe, nothing is mated"', bad)
        assert bad in sheet
        r = _run(sheet, {"J_RF1": "SMA jack", "TP1": "probe"})
        assert any("the exclusion of TP*" in f and "gives no reason" in f for f in r["fails"]), (bad, r["fails"])
    # and one that does not name the land it speaks of is refused too: a reason is about a land
    sheet = GOOD + EXCL.replace('footprints: ["TestPoint:*"], ', "")
    r = _run(sheet, {"J_RF1": "SMA jack", "TP1": "probe"})
    assert any("does not name the land" in f for f in r["fails"]), r["fails"]


def t_an_exclusion_that_speaks_of_another_land_does_not_hide_the_part():
    """`F1` excluded as a soldered fuse. A later netlist fits a fuse HOLDER on F1: the exclusion is about a land
    the part no longer has, and it must not go on covering it."""
    x = ('   exclusions:\n    - {refs: ["F1"], footprints: ["Fuse:Fuse_1812_*"], reason: "a fuse soldered to the board"}\n')
    ok = _run(GOOD + x, {"J_RF1": "SMA jack", "F1": ("0.5A hold 1812", "Fuse:Fuse_1812_4532Metric")})
    assert not ok["fails"] and ok["excluded"] == 1, ok
    r = _run(GOOD + x, {"J_RF1": "SMA jack", "F1": ("25 A mini blade", "Fuse:Fuseholder_Blade_Mini_Keystone_3568")})
    assert any("F1" in f and "speaks of the lands" in f for f in r["fails"]), r["fails"]
    assert r["refused"] == 1 and r["excluded"] == 0, r


def t_a_class_that_speaks_of_another_land_does_not_cover_the_part():
    """Board D's list of 16 September put two JST-PH headers under a class written for socket strips."""
    sheet = GOOD.replace('refs: ["J_RF*"]', 'refs: ["J_RF*"], footprints: ["Connector_Coaxial:SMA_*"]')
    ok = _run(sheet, {"J_RF1": ("SMA jack", "Connector_Coaxial:SMA_Amphenol_132134_Vertical")})
    assert not ok["fails"] and ok["covered"] == 1, ok
    r = _run(sheet, {"J_RF1": ("U.FL socket", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical")})
    assert any("J_RF1" in f and "speaks of the lands" in f for f in r["fails"]) and r["covered"] == 0, r


def t_a_part_that_matches_two_classes_is_refused():
    sheet = GOOD + '    - {name: "every jack", refs: ["J_*"], cycles: 30, %s, load: "a lead", measure: "a tie"}\n' % SRC
    r = _run(sheet, {"J_RF1": "SMA jack"})
    assert any("J_RF1 falls in 2 classes" in f for f in r["fails"]), r["fails"]
    assert r["covered"] == 0 and r["refused"] == 1 and r["result"] == "FAIL", r


def t_a_part_that_is_classed_and_excluded_is_refused():
    x = '   exclusions:\n    - {refs: ["J_RF1"], footprints: ["Connector*"], reason: "not mated"}\n'
    r = _run(GOOD + x, {"J_RF1": "SMA jack"})
    assert any("J_RF1 is disposed 2 times" in f for f in r["fails"]), r["fails"]
    assert r["covered"] == 0 and r["excluded"] == 0 and r["refused"] == 1, r


def t_a_declaration_about_nothing_is_refused():
    """Board B's list carried a class for three soldered PCIe switches that covered no wear part, and board E5's
    classes named references its board does not carry. A class or an exclusion that covers no candidate says so."""
    r = _run(GOOD + POWER, {"J_RF1": "SMA jack"})
    assert any("class power covers no candidate part" in f for f in r["fails"]), r["fails"]
    r2 = _run(GOOD + EXCL, {"J_RF1": "SMA jack"})
    assert any("the exclusion of TP* covers no candidate part" in f for f in r2["fails"]), r2["fails"]


def t_a_reference_class_nobody_declared_is_refused_and_its_part_is_asked_for():
    r = _run(GOOD, {"J_RF1": "SMA jack", "XW3": ("something new", "Package_SO:SOIC-8")})
    assert any("reference class XW" in f and "not declared" in f for f in r["fails"]), r["fails"]
    assert any("XW3" in f and "in no declared class" in f for f in r["fails"]), r["fails"]
    assert r["candidates"] == 2, r


# ------------------------------------------------------------------------------------------------------------------
# THE FIGURE IS CITED TO A DOCUMENT IN THE TREE, BY THE BYTES THAT WERE READ
# ------------------------------------------------------------------------------------------------------------------
def t_a_cycle_figure_cites_its_document_its_page_and_its_words():
    comps = {"J_RF1": "SMA jack"}
    r = _run(GOOD.replace(", %s" % SRC, ""), comps)
    assert any("gives 500 cycles and cites no document" in f for f in r["fails"]), r["fails"]
    for k, v in (("page", '"1"'), ("words", '"the figure"')):
        sheet = GOOD.replace('%s: %s' % (k, v), '%s: ""' % k)
        assert sheet != GOOD
        r = _run(sheet, comps)
        assert any("cites its figure without the %s" % k in f for f in r["fails"]), (k, r["fails"])
    r = _run(GOOD.replace("v2/vendor/fixture/doc.pdf", "v2/vendor/fixture/absent.pdf"), comps)
    assert any("absent.pdf, which is not in this tree" in f for f in r["fails"]), r["fails"]
    r = _run(GOOD.replace(SHA, "0" * 16), comps)
    assert any("is not the one that was read" in f for f in r["fails"]), r["fails"]
    r = _run(GOOD.replace('sha256_16: "%s", ' % SHA, ""), comps)
    assert any("without the sha256" in f for f in r["fails"]), r["fails"]
    r = _run(GOOD.replace("v2/vendor/fixture/doc.pdf", "the SMA standard"), comps)
    assert any("not a document under v2/vendor/" in f for f in r["fails"]), r["fails"]
    for bad in ("0", "-5", "true", '"many"', "2.5"):
        r = _run(GOOD.replace("cycles: 500", "cycles: %s" % bad), comps)
        assert any("not a positive whole number" in f for f in r["fails"]), (bad, r["fails"])


def t_a_class_of_several_part_numbers_cites_each_document():
    two = ('source: [{document: "v2/vendor/fixture/doc.pdf", sha256_16: "%s", page: "2", words: "30"}, '
           '{document: "v2/vendor/fixture/other.pdf", sha256_16: "%s", page: "2", words: "30"}]' % (SHA, SHA))
    sheet = GOOD.replace(SRC, two)
    assert sheet != GOOD
    r = _run(sheet, {"J_RF1": "SMA jack"})
    assert any("other.pdf, which is not in this tree" in f for f in r["fails"]), r["fails"]
    assert len(r["fails"]) == 1, r["fails"]


def t_an_owed_figure_keeps_the_board_inconclusive_and_names_its_open_item():
    """NO NUMBER IS INVENTED. A part with no maker's part picked carries an open item, and the board does not read
    PASS while a figure is owed: a bar that was skipped is not a bar that held."""
    owed = GOOD.replace("cycles: 500, %s" % SRC, 'cycles: null, no_figure: {kind: owed, open_item: O-1, statement: "no part is picked"}')
    assert owed != GOOD
    r = _run(owed, {"J_RF1": "SMA jack"})
    assert not r["fails"] and r["refused"] == 0 and r["covered"] == 1, r
    assert r["result"] == "INCONCLUSIVE" and r["missing_input"] is None, r
    assert any("owes its cycle figure" in w and "O-1" in w and "the part is not picked" in w for w in r["inconclusive"]), r["inconclusive"]
    rc, v = _cli(_tree({"J_RF1": "SMA jack"}), owed)
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and v["missing_input"] is None, (rc, v)
    assert v["counts"]["figures_owed"] == 1 and v["counts"]["refused"] == 0, v["counts"]
    # an owed figure with no open item behind it is a refusal, and so is one naming an item the list does not hold
    for bad in ('open_item: O-9, ', ""):
        r2 = _run(owed.replace("open_item: O-1, ", bad), {"J_RF1": "SMA jack"})
        assert any("names no open item" in f for f in r2["fails"]) and r2["result"] == "FAIL", (bad, r2["fails"])
    # a figure and a reason it has none, both: refused
    both = GOOD.replace("cycles: 500,", 'cycles: 500, no_figure: {kind: not_mated, statement: "soldered"},')
    r3 = _run(both, {"J_RF1": "SMA jack"})
    assert any("a cycle figure and a reason it has none" in f for f in r3["fails"]), r3["fails"]


def t_an_owed_measure_keeps_the_board_inconclusive():
    sheet = GOOD.replace('measure: "the case wall takes it"', 'measure: "none is recorded", measure_owed: O-1')
    assert sheet != GOOD
    r = _run(sheet, {"J_RF1": "SMA jack"})
    assert not r["fails"] and r["result"] == "INCONCLUSIVE" and r["measures_owed"] == 1, r
    assert any("owes its measure" in w and "O-1" in w for w in r["inconclusive"]), r["inconclusive"]
    r2 = _run(sheet.replace("measure_owed: O-1", "measure_owed: O-9"), {"J_RF1": "SMA jack"})
    assert any("owes its measure and names no open item" in f for f in r2["fails"]), r2["fails"]


def t_nothing_mated_is_a_reason_and_needs_its_sentence():
    sheet = GOOD.replace("cycles: 500, %s" % SRC, 'cycles: null, no_figure: {kind: not_mated, statement: "a solder land"}')
    r = _run(sheet, {"J_RF1": "SMA jack"})
    assert not r["fails"] and r["result"] == "PASS" and r["figures"] == {"not_mated": 1}, r
    r2 = _run(sheet.replace('statement: "a solder land"', 'statement: ""'), {"J_RF1": "SMA jack"})
    assert any("its reason is empty" in f for f in r2["fails"]), r2["fails"]
    r3 = _run(sheet.replace("kind: not_mated", "kind: whatever"), {"J_RF1": "SMA jack"})
    assert any("does not say why" in f for f in r3["fails"]), r3["fails"]


# ------------------------------------------------------------------------------------------------------------------
# A MISSING REQUIRED INPUT IS INCONCLUSIVE, NEVER A PASS
# ------------------------------------------------------------------------------------------------------------------
def _inconclusive(r, words):
    assert r["result"] == "INCONCLUSIVE" and not r["fails"], r
    assert r["missing_input"] and words in r["missing_input"], r["missing_input"]
    assert r["candidates"] == 0 and r["covered"] == 0 and r["netlist"] is False, r


def t_a_board_with_no_netlist_of_its_declared_phase_is_inconclusive():
    _inconclusive(_run(GOOD, None), "has no netlist of its declared phase")
    rc, v = _cli(_tree(None), GOOD)
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and "no netlist of its declared phase" in v["missing_input"], (rc, v)


def t_a_netlist_with_no_component_is_inconclusive():
    empty = '(export (version "E")\n  (components\n  )\n  (nets\n  )\n)\n'
    r = _run(GOOD, None, text=empty)
    _inconclusive(r, "holds no component")
    assert r["artefact"] and r["artefact"]["parts"] == 0, "the empty netlist that was read is still named: %r" % r["artefact"]


def t_a_netlist_that_cannot_be_read_is_inconclusive():
    whole = _net({"J_RF1": "SMA jack"})
    for text, why in ((whole[:len(whole) // 2], "never close"),                       # cut short
                      ("(export (version \"E\")\n  (design)\n)\n", "no (components"),   # no components section
                      ("not a netlist at all\n", "does not begin with an expression"),
                      ("(kicad_pcb (version 1))\n", "is not a (export"),
                      (whole.replace('(comp (ref "J_RF1")', '(comp (ref "J_RF1")\n      (value "again"))\n    (comp (ref "J_RF1")'),
                       "is there twice")):
        r = _run(GOOD, None, text=text)
        _inconclusive(r, "cannot be read")
        assert why in r["missing_input"], (why, r["missing_input"])


def t_a_declared_board_the_manifest_does_not_know_is_inconclusive():
    d = _tree({"J_RF1": "SMA jack"})
    sheet = GOOD.replace(" x:\n", " q:\n")
    r = _judge(d, sheet, "q")["q"]
    _inconclusive(r, "is not a board of the manifest")


def t_a_board_of_the_manifest_with_no_declaration_is_inconclusive():
    d = _tree({"J_RF1": "SMA jack"})
    sheet = GOOD.replace(" x:\n", " q:\n")
    r = _judge(d, sheet, None)
    assert sorted(r) == ["q", "x"], sorted(r)
    assert r["x"]["result"] == "INCONCLUSIVE" and any("declares nothing for it" in w for w in r["x"]["inconclusive"]), r["x"]
    assert r["x"]["candidates"] == 0, "nothing is compared for a board that declares nothing: %r" % r["x"]


def t_a_vendor_library_that_is_not_there_leaves_the_citations_unjudged():
    r = _judge(_tree({"J_RF1": "SMA jack"}), GOOD, vendor=False)["x"]
    assert r["result"] == "INCONCLUSIVE" and not r["fails"], r
    assert any("vendor library is not in this tree" in w and "doc.pdf" in w for w in r["inconclusive"]), r["inconclusive"]


def t_a_list_that_cannot_be_read_is_inconclusive():
    d = _tree({"J_RF1": "SMA jack"})
    for sheet, why in (("boards: [", "could not be read"),
                       (GOOD.replace("inventory:", "inventory_gone:"), "no `inventory` section"),
                       (GOOD.replace('J:  {kind: mechanical, what: "a connector"}', 'J:  {kind: sometimes, what: "a connector"}'),
                        "reference class J is declared with no kind")):
        rc, v = _cli(d, sheet)
        assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and v["missing_input"], (rc, v)
        assert why in v["note"] or why in v["missing_input"], (why, v["note"])


def t_a_board_nobody_knows_asked_for_by_name_is_inconclusive():
    rc, v = _cli(_tree({"J_RF1": "SMA jack"}), GOOD, "z")
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and v["missing_input"], (rc, v)


# ------------------------------------------------------------------------------------------------------------------
# THE NETLIST OF THE DECLARED PHASE, BOUND BY CONTENT
# ------------------------------------------------------------------------------------------------------------------
def t_the_declared_phase_is_read_and_not_the_newest_file():
    """Two netlists of one stem. The OLDER is the declared phase's (the routeflow profile names its directory) and
    is complete; the NEWER, in another phase directory, carries a connector nobody declared. The unrepaired tool
    took the newest by file time."""
    d = _tree({"J_RF1": "SMA jack"}, phase="pcb-x-test-x2")
    old = os.path.join(d, "ecad", "pcb-x-test-x2", "out", "pcb-x-test.net")
    newer = os.path.join(d, "ecad", "pcb-x-test-x9", "out", "pcb-x-test.net")
    os.makedirs(os.path.dirname(newer))
    open(newer, "w", encoding="utf-8").write(_net({"J_RF1": "SMA jack", "J_NEW1": "a connector nobody declared"}))
    os.utime(old, (1_000_000_000, 1_000_000_000))
    assert os.path.getmtime(newer) > os.path.getmtime(old)
    r = _judge(d, GOOD)["x"]
    assert not r["fails"] and r["result"] == "PASS" and r["candidates"] == 1, r
    assert r["artefact"]["path"] == old, r["artefact"]
    assert r["artefact"]["sha256"] == hashlib.sha256(open(old, "rb").read()).hexdigest(), r["artefact"]
    # the control: declare the other phase and the same list is refused for the connector it does not know
    json.dump({"board": "pcb-x-test", "project": "v2/ecad/pcb-x-test-x9"},
              open(os.path.join(d, "profiles", "routeflow", "x.json"), "w"))
    r2 = _judge(d, GOOD)["x"]
    assert any("J_NEW1" in f for f in r2["fails"]) and r2["artefact"]["path"] == newer, r2


def t_the_reading_records_what_it_read_by_sha():
    d = _tree({"J_RF1": "SMA jack", "TP1": "probe"})
    rc, v = _cli(d, GOOD + EXCL)
    assert rc == 0, (rc, v)
    net = os.path.join(d, "ecad", "pcb-x-test", "out", "pcb-x-test.net")
    lst = os.path.join(d, "rel.yaml")
    n, l = v["inputs"]["netlist"], v["inputs"]["list"]
    assert v["inputs"]["board"] == "x", v["inputs"]
    assert n["path"] == net and n["sha256"] == hashlib.sha256(open(net, "rb").read()).hexdigest(), n
    assert n["sha256_16"] == n["sha256"][:16] and n["parts"] == 2 and n.get("content16"), n
    assert l["path"] == lst and l["sha256"] == hashlib.sha256(open(lst, "rb").read()).hexdigest(), l
    c = v["counts"]
    assert (c["candidates"], c["classed"], c["excluded"], c["refused"]) == (2, 1, 1, 0), c
    assert c["per_board"] == {"x": {"result": "PASS", "candidates": 2, "classed": 1, "excluded": 1, "refused": 0}}, c


def _content16(raw):
    import regen_compare
    return regen_compare.content_hash(raw.decode("utf-8"))


def t_a_declaration_written_against_another_netlist_is_inconclusive_and_says_whether_the_design_moved():
    """THE SHA MISMATCH (item 2 of stream d6rel's task). The list says which netlist its classes were written
    against. Re-exported with a new export header, the same design has another sha and the reading is INCONCLUSIVE
    saying so; with a connector added, the design changed, the reading says that too, and the refusal of the new
    connector is still made on the netlist that is there, so FAIL wins over INCONCLUSIVE. Never PASS."""
    d = _tree({"J_RF1": "SMA jack"})
    net = os.path.join(d, "ecad", "pcb-x-test", "out", "pcb-x-test.net")
    raw = open(net, "rb").read()
    pinned = GOOD.replace(" x:\n", ' x:\n   written_against: {sha256_16: "%s", content16: "%s"}\n'
                          % (hashlib.sha256(raw).hexdigest()[:16], _content16(raw)))
    assert pinned != GOOD
    r = _judge(d, pinned)["x"]
    assert r["result"] == "PASS" and r["pin"]["bound"] is True and r["pin"]["same_design"] is True, r["pin"]
    # the same design exported again: the export header is noise to the content identity, not to the sha
    again = raw.decode("utf-8").replace('(export (version "E")', '(export (version "E")\n  (design\n    (source "again")\n'
                                        '    (date "2026-09-28T16:00:00+0000")\n    (tool "fixture"))', 1).encode("utf-8")
    assert again != raw and _content16(again) == _content16(raw), "the fixture's re-export must keep the content identity"
    open(net, "wb").write(again)
    r2 = _judge(d, pinned)["x"]
    assert r2["result"] == "INCONCLUSIVE" and not r2["fails"], r2
    assert r2["pin"]["bound"] is False and r2["pin"]["same_design"] is True, r2["pin"]
    assert "written against" in r2["missing_input"] and "re-export of the same design" in r2["missing_input"], r2["missing_input"]
    assert r2["netlist"] is True and r2["candidates"] == 1 and r2["covered"] == 1, "the comparison of what is there still ran: %r" % r2
    rc, v = _cli(d, pinned)
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and "re-export of the same design" in v["missing_input"], (rc, v)
    assert v["inputs"]["netlist"]["sha256_16"] == hashlib.sha256(again).hexdigest()[:16], v["inputs"]
    # a changed design: the connector nobody declared is refused on the netlist that is there, and the pin says why
    open(net, "w", encoding="utf-8").write(_net({"J_RF1": "SMA jack", "J_NEW1": "a jack nobody declared"}))
    r3 = _judge(d, pinned)["x"]
    assert r3["result"] == "FAIL" and any("J_NEW1" in f for f in r3["fails"]), r3
    assert r3["pin"]["same_design"] is False and "the design changed" in r3["missing_input"], (r3["pin"], r3["missing_input"])
    rc3, v3 = _cli(d, pinned)
    assert rc3 == 1 and v3["verdict"] == "FAIL" and v3["missing_input"] is None, "a FAIL is a judgement of what is there: %r" % (rc3, v3["missing_input"])
    # a pin without the content identity still binds by sha, and a board file has no content identity to compare
    r4 = _judge(d, GOOD.replace(" x:\n", ' x:\n   written_against: {sha256_16: "%s"}\n' % hashlib.sha256(raw).hexdigest()[:16]))["x"]
    assert r4["pin"]["bound"] is False and r4["pin"]["same_design"] is None, r4["pin"]
    assert "carries no content identity" in r4["missing_input"] and "re-pin" in r4["missing_input"], r4["missing_input"]


def t_a_declaration_with_no_pin_is_inconclusive_and_never_pass():
    d = _tree({"J_RF1": "SMA jack"})
    r = _judge(d, GOOD, pin=False)["x"]
    assert not r["fails"] and r["result"] == "INCONCLUSIVE", r
    assert r["pin"] == {"declared": None, "read": r["artefact"]["sha256_16"], "bound": False, "same_design": None}, r["pin"]
    assert "does not say which netlist it was written against" in r["missing_input"], r["missing_input"]
    for bad in ('written_against: {sha256_16: "not a sha"}', 'written_against: {sha256_16: ""}', "written_against: 12"):
        r2 = _judge(d, GOOD.replace(" x:\n", " x:\n   %s\n" % bad), pin=False)["x"]
        assert r2["result"] == "INCONCLUSIVE" and "does not say which" in r2["missing_input"], (bad, r2["missing_input"])
    # and the same pin-less list on the command line declares its input missing
    p = os.path.join(d, "rel.yaml"); open(p, "w", encoding="utf-8").write(GOOD)
    out = os.path.join(d, "verdicts")
    rc = REL.main(["--rel", p, "--ecad", os.path.join(d, "ecad"), "--board", "x", "--vendor", os.path.join(d, "vendor"),
                   "--manifest", os.path.join(d, "manifest.json"), "--profiles", os.path.join(d, "profiles"), "--out-dir", out])
    v = json.load(open(os.path.join(out, "reliability.verdict.json")))
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and "written against" in v["missing_input"], (rc, v["missing_input"])


def t_pins_prints_every_boards_line_from_the_declared_phase_and_edits_nothing():
    import io, contextlib
    d = _tree({"J_RF1": "SMA jack"})
    m = json.load(open(os.path.join(d, "manifest.json")))
    m["boards"]["y"] = {"project": "pcb-y-test", "required": True}
    m["boards"]["e"] = {"project": "pcb-e-test", "required": True, "no_chain": True}
    json.dump(m, open(os.path.join(d, "manifest.json"), "w"))
    os.makedirs(os.path.join(d, "ecad", "pcb-e-test"))
    board = os.path.join(d, "ecad", "pcb-e-test", "pcb-e-test.kicad_pcb")
    open(board, "w", encoding="utf-8").write('(kicad_pcb (version 20241229)\n  (footprint "PogoTargets_2x6" (layer "F.Cu")\n'
                                             '    (property "Reference" "J_T1")\n    (property "Value" "targets")\n'
                                             '    (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu"))\n  )\n)\n')
    p = os.path.join(d, "rel.yaml"); open(p, "w", encoding="utf-8").write(GOOD)
    before = open(p, "rb").read()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = REL.main(["--pins", "--rel", p, "--ecad", os.path.join(d, "ecad"), "--manifest", os.path.join(d, "manifest.json"),
                       "--profiles", os.path.join(d, "profiles"), "--out-dir", os.path.join(d, "verdicts")])
    text = buf.getvalue()
    assert rc == 0 and open(p, "rb").read() == before, "--pins edited the list"
    assert not os.path.exists(os.path.join(d, "verdicts")), "--pins wrote a verdict"
    net = os.path.join(d, "ecad", "pcb-x-test", "out", "pcb-x-test.net")
    raw = open(net, "rb").read()
    assert (' x:\n   written_against: {artefact: netlist, path: "%s", sha256_16: "%s", content16: "%s"}' % (net, hashlib.sha256(raw).hexdigest()[:16], _content16(raw))) in text, text
    assert ' y:   # no netlist of the declared phase in this tree' in text, text
    assert (' e:\n   written_against: {artefact: board_file, path: "%s", sha256_16: "%s"}' % (board, hashlib.sha256(open(board, "rb").read()).hexdigest()[:16])) in text, text
    assert "read the values against the list before pasting" in text, text
    # what it prints is what the gate then accepts as bound
    x_line = [l for l in text.split("\n") if "artefact: netlist" in l][0].split("   #")[0].strip()
    r = _judge(d, GOOD.replace(" x:\n", " x:\n   %s\n" % x_line), pin=False)["x"]
    assert r["result"] == "PASS" and r["pin"]["bound"] is True, r


def t_a_board_with_no_schematic_is_read_from_its_board_file():
    """Board E5 has no schematic and no netlist by design (the manifest's no_chain): its board file is its design,
    and its contact targets are mated at every dock. The inventory is read from the board file's footprints with
    the project's S-expression reader; pcbnew is not needed."""
    d = _tree(None, no_chain=True)
    board = os.path.join(d, "ecad", "pcb-x-test", "pcb-x-test.kicad_pcb")
    sheet = GOOD.replace('refs: ["J_RF*"]', 'refs: ["J_T?"], footprints: ["PogoTargets_*"]')
    _inconclusive(_judge(d, sheet)["x"], "has no board file of its declared phase")
    fp = ('  (footprint "%s" (layer "F.Cu")\n    (property "Reference" "%s")\n    (property "Value" "%s")\n'
          '    (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu"))\n  )\n')
    open(board, "w", encoding="utf-8").write("(kicad_pcb (version 20241229)\n" + fp % ("PogoTargets_2x6", "J_T1", "targets")
                                             + fp % ("WireHole_2mm", "J_W1", "12 AWG") + ")\n")
    r = _judge(d, sheet)["x"]
    assert r["artefact_kind"] == "board_file" and r["artefact"]["path"] == board, r["artefact"]
    assert r["covered"] == 1 and any("J_W1" in f and "in no declared class" in f for f in r["fails"]), r
    rc, v = _cli(d, sheet)
    assert rc == 1 and v["inputs"]["board_file"]["sha256"] == hashlib.sha256(open(board, "rb").read()).hexdigest(), v["inputs"]


def t_the_set_reading_is_the_worst_of_its_boards_and_names_each_artefact():
    d = _tree({"J_RF1": "SMA jack"})
    m = json.load(open(os.path.join(d, "manifest.json")))
    m["boards"]["y"] = {"project": "pcb-y-test", "required": True}
    json.dump(m, open(os.path.join(d, "manifest.json"), "w"))
    sheet = GOOD + " y:\n   classes:\n" + ('    - {name: "the jacks", refs: ["J_RF*"], cycles: 500, %s, load: "a wrench", '
                                            'measure: "the case wall takes it"}\n' % SRC)
    p = os.path.join(d, "rel.yaml"); open(p, "w", encoding="utf-8").write(_pin(d, sheet))     # x pinned; y has no netlist yet
    out = os.path.join(d, "verdicts")
    argv = ["--rel", p, "--ecad", os.path.join(d, "ecad"), "--vendor", os.path.join(d, "vendor"),
            "--manifest", os.path.join(d, "manifest.json"), "--profiles", os.path.join(d, "profiles"), "--out-dir", out]
    rc = REL.main(argv)
    v = json.load(open(os.path.join(out, "reliability.verdict.json")))
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE", (rc, v["verdict"])      # board y has no netlist
    assert "netlist_x" in v["inputs"] and "netlist_y" not in v["inputs"] and "board" not in v["inputs"], v["inputs"]
    assert v["counts"]["per_board"]["x"]["result"] == "PASS" and v["counts"]["per_board"]["y"]["result"] == "INCONCLUSIVE", v["counts"]
    os.makedirs(os.path.join(d, "ecad", "pcb-y-test", "out"))
    open(os.path.join(d, "ecad", "pcb-y-test", "out", "pcb-y-test.net"), "w").write(_net({"J_RF1": "SMA jack", "J_X1": "unknown"}))
    open(p, "w", encoding="utf-8").write(_pin(d, sheet))                                        # both boards pinned now
    rc = REL.main(argv)
    v = json.load(open(os.path.join(out, "reliability.verdict.json")))
    assert rc == 1 and v["verdict"] == "FAIL" and v["missing_input"] is None, (rc, v)


def t_the_note_says_it_tests_nothing():
    rc, v = _cli(_tree({"J_RF1": "SMA jack"}), GOOD)
    assert "tests nothing" in v["note"] and "replaces no physical verification" in v["note"], v["note"]
    assert "no board has been built" in v["note"], v["note"]
    assert v["rules"] == ["REL-001"], v["rules"]


# ------------------------------------------------------------------------------------------------------------------
# THE REAL TREE
# ------------------------------------------------------------------------------------------------------------------
def t_the_committed_list_disposes_every_candidate_of_every_board():
    """Every board of the manifest, read at its declared phase: every candidate in one class or under one
    exclusion, no refusal of any kind, every class naming the land it speaks of. A board may read INCONCLUSIVE, and
    only because a figure or a measure is owed under an open item: never for a missing input."""
    import phase_artefacts as PA
    r = REL.judge()
    assert sorted(r) == sorted(PA.letters()), (sorted(r), PA.letters())
    fails = [f for v in r.values() for f in v["fails"]]
    assert not fails, fails
    for letter, v in sorted(r.items()):
        assert v["artefact"] and v["netlist"], "board %s was not read: %r" % (letter, v["inconclusive"])
        assert v["missing_input"] is None, (letter, v["missing_input"])
        assert v["refused"] == 0 and v["candidates"] == v["covered"] + v["excluded"], (letter, v["candidates"], v["covered"], v["excluded"])
        assert v["candidates"] == len(v["inventory"]) > 0, letter
        assert all(row["disposition"] in ("class", "exclusion") for row in v["inventory"]), letter
        assert all("owes its" in w for w in v["inconclusive"]), (letter, v["inconclusive"])
        assert v["result"] == ("INCONCLUSIVE" if v["inconclusive"] else "PASS"), (letter, v["result"])
    import yaml
    d = yaml.safe_load(open(REL.REL, encoding="utf-8"))
    for letter, b in d["boards"].items():
        for c in b["classes"]:
            assert c.get("footprints"), "board %s class %s does not name the land it speaks of" % (letter, c.get("name"))
            assert c.get("count_expected") is not None, "board %s class %s declares no count" % (letter, c.get("name"))
        # ...and every declaration is bound to the artefact it was written against, which is the one in this tree
        pin = b.get("written_against")
        assert isinstance(pin, dict) and pin.get("sha256_16") == r[letter]["artefact"]["sha256_16"], (letter, pin, r[letter]["artefact"])
        assert r[letter]["pin"]["bound"] is True, (letter, r[letter]["pin"])
        if r[letter]["artefact_kind"] == "netlist":
            assert pin.get("content16") == r[letter]["artefact"].get("content16"), (letter, pin)
            assert r[letter]["pin"]["same_design"] is True, (letter, r[letter]["pin"])
    assert sum(v["covered"] for v in r.values()) >= 100, r


def t_the_committed_list_covers_every_wear_part_of_every_board():
    """The name the suite knew this test by since 16 September 2026, kept: no refusal on the committed boards."""
    r = REL.judge()
    fails = [f for v in r.values() for f in v["fails"]]
    assert not fails, fails
    assert sum(v["covered"] for v in r.values()) >= 100, r


def t_the_parts_the_word_list_never_found_are_in_the_inventory():
    """The boards' own parts that finding H3-01 and the set 6 measurement name, each a candidate with a disposition."""
    r = REL.judge()
    want = {"a": ["J_CN1", "J_CP4", "J_VN2", "J_VR3", "J_DOCK", "J_PRE1"],
            "b": ["J_ETH", "J_SIM1", "J_SIM2", "J_CAM", "J_QMX"],
            "c": ["J_EPD", "J_HSJ1", "J_HSJ2", "SW_MAIN", "SW_PI", "SW_TEST", "SW_SOS", "SW_EMCON", "SW_ZERO", "SW_LIGHT"],
            "e": ["J_FAN1", "J_FAN2", "J_POD", "J_GEIGER", "J_LTG", "J_DCF", "J_BLK"],
            "p": ["W_BN", "W_BP"]}
    for letter, refs in want.items():
        rows = {row["ref"]: row for row in r[letter]["inventory"]}
        for ref in refs:
            assert ref in rows, "board %s: %s is not in the inventory" % (letter, ref)
            assert rows[ref]["disposition"] == "class", (letter, ref, rows[ref])
            assert not REL.WEAR.search(REL.identity(rows[ref]["value"])), \
                "%s %s is a part the word list finds, so it does not show the defect" % (letter, ref)
