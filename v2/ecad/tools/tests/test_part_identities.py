#!/usr/bin/env python3
"""The part identity table (EQ-21, pre-PCB layer 6; MESHSAT-1357, stream w5ident 27 September 2026, and stream w5identc
29 September 2026 for board C's slice).

Properties, stated on fixtures and on the committed table, never on today's counts (a rule that fails when its subject
is fixed is a rule about history):

  * a value string is read as the number it states (100n, 4.7u, 60R4, 10mOhm, 2m 2512, 0.47R);
  * two rows whose requirements differ are never one selection, even when one part would meet both, and rows whose
    requirements agree are;
  * a stated voltage rating is never lowered by the derivation, and a BOUND on an undeclared net never raises a stated
    one (it is recorded instead);
  * ground never sets the ceiling of another net, a switch node behind an inductor is declared or UNBOUNDED, and (w5ident's
    second check, W5I-C2-B1) a declared return a little above ground is a floor and never a ceiling, and a connector's
    pin is set on its far side;
  * RULE D-2 (w5ident's second check, ID-B1 to ID-B3): a document is bound to a part only where the cited page's text
    layer prints the part number; a document that does not print it is REFUSED, a part number inside a longer one is not
    a match, and a sha256 that differs is refused;
  * the committed table is internally whole: every id is the digest of its key, every row is in one selection, a
    RESOLVED selection has a maker, a part number and a document with its sha256 and page, and every UNRESOLVED or
    NOT_A_PART selection says why (an UNRESOLVED one also its reason class and its next action).

The resolver's rules of w5ident (catalogue lines judged on every requirement, the blade fuse rule, the SOURCES join, the
declared mismatches) are not here: stream w5identc brought no resolver over (its table's identities are carried or
decided by hand in v2/docs/records/w5identc/build_table.py), so its tests stay with fnd/w5ident.

Freshness against the netlists of the day is `part_identities.py check`, not a test: after the netlists change the table
is re-derived, and a test that failed on every regeneration would be a test about history.
"""
import os, sys, collections, shutil, tempfile, hashlib

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import part_identities as PI
from harness import Skip, need


def FakeBoard(on, rails=None, nodes=None, values=None, pinfn=None):
    """A board from dictionaries: the nets of each fixture part and the intent's rails and nodes. No file is read.
    Built by hand where the tool under test predates Board.from_data, so the two V-1 rules below can be run against
    the tool of pass 1 and be seen to FAIL there (records/w5ident/evidence/v1-tests-on-the-pass-1-tool.txt)."""
    if hasattr(PI.Board, "from_data"): return PI.Board.from_data(on, rails, nodes, values, pinfn)
    b = PI.Board.__new__(PI.Board)
    b.letter = "x"; b.on = on; b.rails = rails or {}; b.nodes = nodes or {}; b.values = values or {}; b.pinfn = pinfn or {}
    b.by_net = collections.defaultdict(set)
    for r, pins in on.items():
        for p_, n in pins.items(): b.by_net[n].add((r, p_))
    b.comps = set(on); b._bound = {}
    return b


GND0 = {"GND": {"v_max": 0.0, "v_min": 0.0}}          # every intent file declares its ground like this


def _row(board, ref, value, fp):
    p = PI.props(board, ref, value, fp, "")
    PI.requirements(p)
    p["key"] = PI.key_of(p)
    return p


def t_values_read_as_the_numbers_they_state():
    assert abs(PI.cap_value("100n") - 100e-9) < 1e-15
    assert abs(PI.cap_value("4.7u 25V") - 4.7e-6) < 1e-12
    assert abs(PI.cap_value("9.1p 50V C0G") - 9.1e-12) < 1e-18
    assert abs(PI.res_value("60R4 1%") - 60.4) < 1e-9
    assert abs(PI.res_value("10mOhm 1% 2512 (CS)") - 0.010) < 1e-12
    assert abs(PI.res_value("2m 2512 2W (sense)") - 0.002) < 1e-12
    assert abs(PI.res_value("0.47R 1%") - 0.47) < 1e-12
    assert abs(PI.res_value("4.7k") - 4700) < 1e-9
    assert abs(PI.res_value("1M (GD to VPWR, 9.1.3)") - 1e6) < 1e-3
    assert PI.res_value("0R (break link)") == 0.0
    assert abs(PI.res_value("33") - 33.0) < 1e-12


def t_two_capacitors_of_one_value_on_different_rails_are_two_selections():
    b = FakeBoard({"C1": {"1": "+3V3", "2": "GND"}, "C2": {"1": "VBUS20", "2": "GND"}, "C3": {"1": "+3V3", "2": "GND"}},
                  rails={"+3V3": {"volts": 3.3}, "VBUS20": {"volts": 20.0}})
    c1 = _row(b, "C1", "100n", "Capacitor_SMD:C_0603_1608Metric")
    c2 = _row(b, "C2", "100n", "Capacitor_SMD:C_0603_1608Metric")
    c3 = _row(b, "C3", "100n", "Capacitor_SMD:C_0603_1608Metric")
    assert c1["key"] == c3["key"], "the same requirement on the same rail is one selection"
    assert c1["key"] != c2["key"], "a 3.3 V and a 20 V capacitor of one value were merged"
    assert c2["requirements"]["v_rating_min"] == 25.0, c2["requirements"]


def t_a_stated_rating_is_never_lowered_and_a_bound_never_raises_it():
    # C1 states 50 V on a 3.3 V rail: the requirement stays 50 V. C2 states 16 V on a net nobody declared, bounded by a
    # 36 V part: the stated 16 V stands and the bound is recorded as a finding, not written over it.
    b = FakeBoard({"C1": {"1": "+3V3", "2": "GND"}, "C2": {"1": "COMP", "2": "GND"}, "U1": {"1": "COMP", "2": "VIN", "3": "GND"}},
                  rails={"+3V3": {"volts": 3.3}, "VIN": {"volts": 12.0, "v_work": 36.0}})
    c1 = _row(b, "C1", "100n 50V", "Capacitor_SMD:C_0603_1608Metric")
    c2 = _row(b, "C2", "220n 16V", "Capacitor_SMD:C_0603_1608Metric")
    assert c1["requirements"]["v_rating_min"] == 50.0
    assert c2["requirements"]["v_rating_min"] == 16.0
    assert "V_BOUND_ABOVE_STATED" in c2.get("findings", []), c2.get("findings")


def t_an_unstated_rating_on_an_undeclared_net_takes_the_bound():
    b = FakeBoard({"C2": {"1": "COMP", "2": "GND"}, "U1": {"1": "COMP", "2": "VIN", "3": "GND"}},
                  rails={"VIN": {"volts": 12.0, "v_work": 36.0}})
    c2 = _row(b, "C2", "220n", "Capacitor_SMD:C_0603_1608Metric")
    assert c2["requirements"]["v_rating_min"] == 50.0, c2["requirements"]          # 36 V x 1.2 = 43.2 -> 50 V
    assert "BOUND" in c2["requirement_basis"]["v_rating_min"]


def t_ground_never_sets_the_ceiling_of_another_net():
    """The first check of pass 1, blocking item 1: the intent declares GND at v_max 0, so an IC whose only declared
    pin was ground bounded its other pins at 0.0 V, labelled BOUND, on 83 row-nets (p:C1 on the BQ4050's PBI read
    6.3 V where the pack is 16.8 V). Ground is a floor. Three shapes of it: an IC's ground pin, a resistor to
    ground, and a net the intent declares at or below 0 V (board D's charge-pump negative rail)."""
    b = FakeBoard({"U1": {"1": "PBI", "2": "GND"}, "C1": {"1": "PBI", "2": "GND"},
                   "R8": {"1": "SRP_F", "2": "GND"}, "C9": {"1": "SRP_F", "2": "GND"},
                   "U8": {"1": "HP_OUT", "2": "AMP_HPVSS", "3": "GND"}, "C40": {"1": "HP_OUT", "2": "GND"}},
                  nodes=dict(GND0, AMP_HPVSS={"v_max": 0.0, "v_min": -3.3}))
    for net in ("PBI", "SRP_F", "HP_OUT"):
        hi, lo, how = b.bound(net)
        assert hi is None and how.startswith("UNBOUNDED"), "%s: ground set a ceiling: %r" % (net, (hi, lo, how))
    for ref in ("C1", "C9", "C40"):
        c = _row(b, ref, "100n", "Capacitor_SMD:C_0603_1608Metric")
        assert c["requirements"]["v_rating_min"] is None, "%s was given a rating from a 0 V ceiling: %s" % (ref, c["requirements"])
        assert "V_UNBOUNDED" in c.get("findings", []), c.get("findings")
    # and a declared pin above ground still bounds, with ground left out of the maximum and kept as the floor
    b = FakeBoard({"U1": {"1": "COMP", "2": "GND", "3": "VIN"}, "C1": {"1": "COMP", "2": "GND"}},
                  rails={"VIN": {"volts": 12.0}}, nodes=dict(GND0))
    assert b.bound("COMP")[0] == 12.0 and b.bound("COMP")[2].startswith("BOUND"), b.bound("COMP")


def t_a_switch_node_behind_an_inductor_is_declared_or_unbounded():
    """The first check of pass 1, blocking item 1: an inductor was a series element the bound passed through, so a
    boost's switch node read its INPUT rail (c:C31 read 3.3 V through L1 where EPD_SW reaches the pump's output). The
    project states switch nodes in the intent and states no ringing figure, so an undeclared one is UNBOUNDED; a
    declared one reads its declaration; a ferrite is still a series conductor."""
    on = {"L1": {"1": "VIN", "2": "SW"}, "Q1": {"1": "GATE", "2": "GND", "3": "SW"}, "D1": {"1": "VOUT", "2": "SW"},
          "C5": {"1": "SW", "2": "GND"}, "C6": {"1": "VOUT", "2": "GND"}, "U1": {"1": "GATE", "2": "VIN", "3": "GND"},
          "FB1": {"1": "VIN", "2": "VIN_F"}, "R9": {"1": "VIN_F", "2": "GND"}, "C7": {"1": "VIN_F", "2": "GND"}}
    values = {"L1": "10uH 0.8 A (the boost inductor)", "FB1": "ferrite 600R", "Q1": "N-FET", "D1": "SS2040FL"}
    pinfn = {("Q1", "1"): "G", ("Q1", "2"): "S", ("Q1", "3"): "D"}
    b = FakeBoard(on, rails={"VIN": {"volts": 3.3}}, nodes=dict(GND0), values=values, pinfn=pinfn)
    for net in ("SW", "VOUT"):
        hi, lo, how = b.bound(net)
        assert hi is None and how.startswith("UNBOUNDED"), "%s took a voltage through the boost inductor: %r" % (net, (hi, lo, how))
    c5 = _row(b, "C5", "4.7u", "Capacitor_SMD:C_0603_1608Metric")
    assert c5["requirements"]["v_rating_min"] is None and "V_UNBOUNDED" in c5.get("findings", []), c5["requirements"]
    assert b.bound("VIN_F")[0] == 3.3, "a ferrite is a series conductor: %r" % (b.bound("VIN_F"),)
    # declared as the project declares its switch nodes: v_max the larger rail it reaches, a diode drop below ground
    b = FakeBoard(on, rails={"VIN": {"volts": 3.3}, "VOUT": {"volts": 20.0}},
                  nodes=dict(GND0, SW={"v_max": 20.0, "v_min": -1.0}), values=values, pinfn=pinfn)
    assert b.bound("SW") == (20.0, -1.0, "DECLARED"), b.bound("SW")
    c5 = _row(b, "C5", "4.7u", "Capacitor_SMD:C_0603_1608Metric")
    assert c5["requirements"]["v_rating_min"] == 25.0, c5["requirements"]          # 20 V x 1.2 = 24 -> 25 V


def t_a_net_the_intent_declares_with_no_maximum_is_not_bounded_by_its_neighbours():
    # board C's e-paper pump nodes: the intent names them and leaves the voltage to the panel maker's own parts list
    b = FakeBoard({"U1": {"1": "EPD_VGH", "2": "+3V3", "3": "GND"}, "C30": {"1": "EPD_VGH", "2": "GND"}},
                  rails={"+3V3": {"volts": 3.3}}, nodes=dict(GND0, EPD_VGH={"v_max": None, "v_min": 0.0, "basis": "the panel maker states the part"}))
    hi, lo, how = b.bound("EPD_VGH")
    assert hi is None and "no maximum" in how, (hi, lo, how)
    c = _row(b, "C30", "1u 25V", "Capacitor_SMD:C_0603_1608Metric")
    assert c["requirements"]["v_rating_min"] == 25.0 and "V_UNBOUNDED" in c.get("findings", []), (c["requirements"], c.get("findings"))


def t_a_crystal_load_and_a_small_capacitor_are_c0g_and_bulk_is_x7r():
    b = FakeBoard({"C1": {"1": "XI", "2": "GND"}, "Y1": {"1": "XI", "2": "XO"}, "C2": {"1": "+3V3", "2": "GND"},
                   "C3": {"1": "+3V3", "2": "GND"}, "C4": {"1": "+3V3", "2": "GND"}},
                  rails={"+3V3": {"volts": 3.3}})
    assert _row(b, "C1", "18p", "Capacitor_SMD:C_0402_1005Metric")["requirements"]["dielectric"] == "C0G"
    assert _row(b, "C2", "1n", "Capacitor_SMD:C_0603_1608Metric")["requirements"]["dielectric"] == "C0G"
    assert _row(b, "C3", "10u", "Capacitor_SMD:C_0805_2012Metric")["requirements"]["dielectric"] == "X7R"
    assert _row(b, "C4", "47u 6.3V X5R 1210", "Capacitor_SMD:C_1210_3225Metric")["requirements"]["dielectric"] == "X5R"


def t_a_shunt_is_rated_on_its_rail_current_and_a_pull_up_is_not():
    b = FakeBoard({"R1": {"1": "CELL", "2": "VBAT"}, "R2": {"1": "+3V3", "2": "SDA"}},
                  rails={"CELL": {"volts": 14.4, "amps_peak": 10.0}, "VBAT": {"volts": 14.4, "amps_peak": 10.0}, "+3V3": {"volts": 3.3, "amps_peak": 0.6}})
    r1 = _row(b, "R1", "5mOhm 1% 2512", "Resistor_SMD:R_2512_6332Metric")
    r2 = _row(b, "R2", "4.7k", "Resistor_SMD:R_0603_1608Metric")
    assert r1["requirements"]["resistor_kind"] == "current sense"
    assert r1["requirements"]["power_min_w"] == 1.0, r1["requirements"]          # 10^2 x 0.005 = 0.5 W, twice -> 1 W
    assert r2["requirements"]["power_min_w"] == 0.1, r2["requirements"]          # the 0603 standard rating
    assert r1["key"] != _row(b, "R1", "5mOhm 5% 2512", "Resistor_SMD:R_2512_6332Metric")["key"], "a 1 and a 5 percent shunt were merged"


def t_two_rows_whose_requirement_is_unknown_are_one_selection_only_across_the_same_nets():
    # rule K-1: unknown is not "the same". PBI and SRP_F are both UNBOUNDED; their capacitors must not be merged, and
    # two capacitors across PBI and ground are one selection (whatever that voltage is, it is one voltage)
    b = FakeBoard({"U1": {"1": "PBI", "2": "GND", "3": "SRP_F"}, "C1": {"1": "PBI", "2": "GND"}, "C2": {"1": "PBI", "2": "GND"},
                   "C9": {"1": "SRP_F", "2": "GND"}}, nodes=dict(GND0))
    c1, c2, c9 = (_row(b, r, "100n", "Capacitor_SMD:C_0603_1608Metric") for r in ("C1", "C2", "C9"))
    assert c1["requirements"]["v_rating_min"] is None and c9["requirements"]["v_rating_min"] is None
    assert c1["key"] == c2["key"], "two capacitors across the same two nets are two selections"
    assert c1["key"] != c9["key"], "capacitors on two unbounded nets were merged: their requirements are not known to agree"
    # and a stated rating that nothing checks is not merged with one that is checked
    b = FakeBoard({"U1": {"1": "PBI", "2": "GND"}, "C1": {"1": "PBI", "2": "GND"}, "C2": {"1": "+3V3", "2": "GND"}},
                  rails={"+3V3": {"volts": 3.3}}, nodes=dict(GND0))
    c1, c2 = (_row(b, r, "1u 25V", "Capacitor_SMD:C_0603_1608Metric") for r in ("C1", "C2"))
    assert c1["requirements"]["v_rating_min"] == c2["requirements"]["v_rating_min"] == 25.0
    assert c1["key"] != c2["key"], "a rating nothing checks shares a selection with one that is checked"


def t_a_declared_return_is_a_floor_never_a_ceiling():
    """w5ident's second check, W5I-C2-B1: board P declares its pack negative PACK_N at 0.05 V (a return, 50 mV above
    ground at 25 A), and rule V-1 took it as a CEILING through the ESD diode D2 and the connector J_SMB, so six SMBus nets
    read BOUND at 0.05 V where board E pulls them to 3.3 V. The check's own counter-example, and its IC variant."""
    b = FakeBoard({"D2": {"1": "SMBC", "2": "PACK_N"}, "J_SMB": {"1": "SMBC", "3": "PACK_N"}, "C1": {"1": "SMBC", "2": "GND"}},
                  rails={"PACK_N": {"volts": 0.05, "v_work": 0.05}}, nodes=dict(GND0),
                  values={"J_SMB": "SMBus lead to the host", "D2": "PESD5V0S1BA"})
    hi, lo, how = b.bound("SMBC")
    assert hi is None and how.startswith("UNBOUNDED"), "a 0.05 V return set a ceiling: %r" % ((hi, lo, how),)
    c = _row(b, "C1", "100n", "Capacitor_SMD:C_0603_1608Metric")
    assert c["requirements"]["v_rating_min"] is None and "V_UNBOUNDED" in c.get("findings", []), c["requirements"]
    b = FakeBoard({"U1": {"1": "X", "2": "RET", "3": "GND"}, "C1": {"1": "X", "2": "GND"}},
                  rails={"RET": {"volts": 0.05, "v_work": 0.05}}, nodes=dict(GND0))
    assert b.bound("X")[0] is None, "an IC whose only declared pin is a return bounded its other pin: %r" % (b.bound("X"),)
    b = FakeBoard({"U1": {"1": "X", "2": "RET", "3": "GND"}}, rails={"RET": {"volts": 3.3, "returns": "the pack's"}}, nodes=dict(GND0))
    assert b.bound("X")[0] is None, "a net the intent marks as a return set a ceiling: %r" % (b.bound("X"),)
    # a declared pin above the return still bounds
    b = FakeBoard({"U1": {"1": "X", "2": "RET", "3": "VDD"}}, rails={"RET": {"volts": 0.05}, "VDD": {"volts": 3.3}}, nodes=dict(GND0))
    assert b.bound("X")[0] == 3.3 and b.bound("X")[2].startswith("BOUND"), b.bound("X")


def t_a_connector_pin_is_set_on_its_far_side():
    """W5I-C2-B1 part (b): a connector was read as an active part whose other pins bound it. Its pin is set by what is on
    the far side; an undeclared net on it is UNBOUNDED, a declared one reads its declaration, and a lead whose value names
    a passive far end (a button) still conducts."""
    b = FakeBoard({"J1": {"1": "SIG", "2": "+5V", "3": "GND"}, "C1": {"1": "SIG", "2": "GND"}},
                  rails={"+5V": {"volts": 5.0}}, nodes=dict(GND0), values={"J1": "ribbon from board B"})
    hi, lo, how = b.bound("SIG")
    assert hi is None and "connector" in how, (hi, lo, how)
    b = FakeBoard({"J1": {"1": "SIG", "2": "+5V", "3": "GND"}}, rails={"+5V": {"volts": 5.0}},
                  nodes=dict(GND0, SIG={"v_max": 3.3, "v_min": 0.0}), values={"J1": "ribbon from board B"})
    assert b.bound("SIG") == (3.3, 0.0, "DECLARED"), b.bound("SIG")
    b = FakeBoard({"J2": {"1": "BTN", "2": "+3V3"}, "C2": {"1": "BTN", "2": "GND"}}, rails={"+3V3": {"volts": 3.3}},
                  nodes=dict(GND0), values={"J2": "MAIN button lead to A22"})
    assert b.bound("BTN")[0] == 3.3, "a button lead's far end conducts: %r" % (b.bound("BTN"),)


def _pdf(pages):
    """A minimal PDF written by hand (no library): each page one text line, or a list of lines, in Helvetica with the
    WinAnsi encoding (so a plus-minus sign is one). The fixture a document reader must read."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", None,
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"]
    kids = []
    for text in pages:
        lines = [text] if isinstance(text, str) else list(text)
        body = " ".join("(%s) Tj 0 -16 Td" % l.replace("\\", "/").replace("(", "\\(").replace(")", "\\)") for l in lines)
        stream = "BT /F1 11 Tf 72 740 Td %s ET" % body
        objs.append("<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
        objs.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % (len(objs)))
        kids.append(len(objs))
    objs[1] = "<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % k for k in kids), len(kids))
    out, offs = "%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offs.append(len(out.encode("latin-1"))); out += "%d 0 obj\n%s\nendobj\n" % (i, o)
    x = len(out.encode("latin-1"))
    out += "xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1) + "".join("%010d 00000 n \n" % o for o in offs)
    out += "trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, x)
    return out.encode("latin-1")


def _fixture_doc(pages):
    if not (shutil.which("pdftotext") and shutil.which("pdfinfo")): raise Skip("pdftotext and pdfinfo are not on this host")
    d = tempfile.mkdtemp(prefix="pi-doc-")
    p = os.path.join(d, "doc.pdf")
    open(p, "wb").write(_pdf(pages))
    return d, p


def t_a_document_that_does_not_name_the_part_is_refused():
    """Rule D-2, the fixture ID-B3 asked for: a document that exists, whose sha256 is the one bound, and whose text holds
    neither the part number (a series sheet's ordering scheme) is REFUSED; the same binding to a document that prints the
    part number on the cited page is READ; the part number on another page than the one cited is REFUSED."""
    d, p = _fixture_doc(["CC0603 x R NPO 9 B N ordering scheme, 100 nF to 1 uF, 16 V to 50 V",
                         "Ordering information: PCA9555PWR TSSOP-24"])
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    rel = os.path.basename(p)
    r = PI.read_binding(dict(path=rel, sha256=h, page=1), "CC0603KRX7R9BB104", root=d)
    assert r["state"] == "REFUSED" and "does not name" in r["why"], r
    r = PI.read_binding(dict(path=rel, sha256=h, page=2), "PCA9555PWR", root=d)
    assert r["state"] == "READ" and "PCA9555PWR" in r["line"], r
    r = PI.read_binding(dict(path=rel, sha256=h, page=1), "PCA9555PWR", root=d)
    assert r["state"] == "REFUSED", "the part number on page 2 was accepted for page 1: %r" % (r,)
    r = PI.read_binding(dict(path=rel, sha256="0" * 64, page=2), "PCA9555PWR", root=d)
    assert r["state"] == "REFUSED" and "sha256" in r["why"], r
    r = PI.read_binding(dict(path=rel, page=2), "PCA9555PWR", root=d)
    assert r["state"] == "REFUSED", "a binding with no sha256 was read: %r" % (r,)
    assert PI.find_pages(p, "PCA9555PWR") == [2] and PI.find_pages(p, "CC0603KRX7R9BB104") == []
    r = PI.read_binding(dict(path="held/absent.pdf", sha256=h, page=1, held_back=True, fetch="fetch.py"), "X", root=d)
    assert r["state"] == "UNREAD", r


def t_a_part_number_inside_a_longer_one_is_not_a_match():
    assert PI.names_part("Order code: PCA9555PWR, 2000 per reel", "PCA9555PWR")[0]
    assert PI.names_part("order code pca9555pwr", "PCA9555PWR")[0], "letter case decides a match"
    assert not PI.names_part("PCA9555PWRG4 TSSOP", "PCA9555PWR")[0], "a longer part number named the shorter one"
    assert not PI.names_part("XPCA9555PWR", "PCA9555PWR")[0]
    assert PI.names_part("SS2040FL_R1_00001 SOD-123FL", "SS2040FL")[0], "a packing suffix after an underscore is a boundary"
    assert not PI.names_part("", "X1")[0] and not PI.names_part("X1", "")[0]


def t_an_html_page_is_read_by_its_parser():
    d = tempfile.mkdtemp(prefix="pi-html-")
    p = os.path.join(d, "spec.html")
    open(p, "w").write("<html><head><script>var p='CL10B104KB8NNNC';</script></head><body><h1>CL10A225KO8NNNC</h1></body></html>")
    assert PI.page_count(p) == 1
    assert PI.names_part(PI.page_text(p, 1), "CL10A225KO8NNNC")[0]
    assert not PI.names_part(PI.page_text(p, 1), "CL10B104KB8NNNC")[0], "a part number inside a script was read as text"


def t_the_committed_table_is_whole():
    import yaml
    t = yaml.safe_load(open(need(PI.TABLE, "the identity table")))
    assert t.get("scope"), "the table names no boards"
    ids, rows = set(), collections.Counter()
    for s in t["selections"]:
        assert s["id"] == PI.selection_id(s["key"]), "%s: id is not the digest of its key" % s["id"]
        assert s["id"] not in ids; ids.add(s["id"])
        for r in s["rows"]:
            rows[r] += 1
            assert r.split(":")[0] in t["scope"], "%s is outside the table's scope %s" % (r, t["scope"])
        assert s["n_rows"] == len(s["rows"])
        i = s["identity"]
        assert i["status"] in PI.STATUSES, i["status"]
        if i["status"] == "RESOLVED":
            ds = i.get("datasheet") or {}
            assert i.get("maker") and i.get("mpn"), s["id"]
            assert ds.get("path") and ds.get("sha256") and ds.get("page"), "%s is RESOLVED without a path, sha256 and page: %s" % (s["id"], ds)
            assert ds.get("held_back") or os.path.exists(os.path.join(PI.REPO, ds["path"])), "%s cites a document not in the tree" % s["id"]
            if s["kind"] == "capacitor":
                assert s["requirements"].get("v_rating_min") is not None, "%s names a capacitor whose voltage requirement is open" % s["id"]
        if i["status"] == "UNRESOLVED":
            assert i.get("reason_class") in PI.REASONS, (s["id"], i.get("reason_class"))
            assert i.get("next_action"), "%s is UNRESOLVED and names no next action" % s["id"]
        if i["status"] in ("UNRESOLVED", "NOT_A_PART"):
            assert i.get("reason"), "%s is %s without a reason" % (s["id"], i["status"])
    dup = [r for r, n in rows.items() if n > 1]
    assert not dup, "rows in two selections: %s" % dup[:5]
    c = t["counts"]
    assert c["rows"] == sum(rows.values()), "the counts disagree with the rows listed"
    assert c["selections"] == len(t["selections"])
    assert c["identity_status"] == dict(collections.Counter(s["identity"]["status"] for s in t["selections"]))
    assert sum(c["rows_by_identity_status"].values()) == c["rows"]
    assert {r["id"] for r in t["rules"]} >= {"K-1", "V-1", "V-2", "D-2", "N-1", "C-D3"}


YAGEO_PAGE = ["YAGEO Product specification", "Surface-Mount Ceramic Multilayer Capacitors X7R 6.3 V to 250 V",
              "YAGEO BRAND ordering code", "CC XXXX X X X7R X BB XXX", "0402 (1005)", "0603 (1608)",
              "K = ± 10%", "M = ± 20%", "R = Paper/PE taping reel; Reel 7 inch", "8 = 25 V", "9 = 50 V",
              "2 significant digits+number of zeros"]
CAP_REQ = {"value": "100nF", "package": "0603", "construction": "MLCC", "dielectric": "X7R", "v_rating_min": 6.3,
           "tolerance_max_pct": 10.0}


def _yageo_fields(tol="K", volt="9", volt_row="9 = 50 V", volt_means="50 V"):
    return [dict(field="series", code="CC", row="CC XXXX X X X7R X BB XXX", means="Ceramic Multilayer",
                 means_row="Surface-Mount Ceramic Multilayer Capacitors X7R 6.3 V to 250 V"),
            dict(field="size", code="0603", row="0603 (1608)"),
            dict(field="tolerance", code=tol, row="%s = ± %s%%" % (tol, {"K": 10, "M": 20}[tol]), means="± %s%%" % {"K": 10, "M": 20}[tol]),
            dict(field="packaging", code="R", row="R = Paper/PE taping reel; Reel 7 inch", means="Paper/PE taping reel"),
            dict(field="dielectric", code="X7R", row="CC XXXX X X X7R X BB XXX"),
            dict(field="voltage", code=volt, row=volt_row, means=volt_means),
            dict(field="process", code="BB", row="CC XXXX X X X7R X BB XXX"),
            dict(field="value", code="104", rule="pf_2sig", row="2 significant digits+number of zeros")]


def _decoded(page, fields, publisher="YAGEO", mark="YAGEO"):
    d, p = _fixture_doc([page])
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return d, dict(path=os.path.basename(p), sha256=h, page=1, binding="DECODED", publisher=publisher, maker_mark=mark, fields=fields)


def t_a_decoded_binding_that_holds():
    """The session's DECODED rule (29 September 2026): the maker's ordering-code table on the cited page decodes the
    part number field by field, each code with its meaning in the table's own row, and the decoded part meets the
    selection's value, package, tolerance, voltage and dielectric."""
    d, ds = _decoded(YAGEO_PAGE, _yageo_fields())
    r = PI.read_binding(ds, "CC0603KRX7R9BB104", root=d, maker="YAGEO", req=CAP_REQ)
    assert r["state"] == "DECODED" and r["binding"] == "DECODED", r
    assert set(r["established"]) >= {"value", "package", "tolerance", "voltage", "dielectric", "construction"}, r
    ds2 = dict(ds, fields=_yageo_fields()[:-1] + [dict(field="value", code="104", rule="pf_2sig", row="2 significant digits+number of zeros")])
    r = PI.read_binding(ds2, "CC0603KRX7R9BB105", root=d, maker="YAGEO", req=CAP_REQ)
    assert r["state"] == "REFUSED" and "spell" in r["why"], "fields that do not spell the part number were accepted: %r" % (r,)


def t_a_decoded_tolerance_that_contradicts_the_selection_is_refused():
    d, ds = _decoded(YAGEO_PAGE, _yageo_fields(tol="M"))
    r = PI.read_binding(ds, "CC0603MRX7R9BB104", root=d, maker="YAGEO", req=CAP_REQ)
    assert r["state"] == "REFUSED" and "tolerance" in r["why"], "a 20 percent part met a 10 percent selection: %r" % (r,)
    r = PI.read_binding(ds, "CC0603MRX7R9BB104", root=d, maker="YAGEO", req=dict(CAP_REQ, tolerance_max_pct=20.0))
    assert r["state"] == "DECODED", r


def t_a_decoded_binding_on_a_page_that_lacks_a_field_is_refused():
    page = [l for l in YAGEO_PAGE if l != "9 = 50 V"]       # the table page without the voltage code 9
    d, ds = _decoded(page, _yageo_fields())
    r = PI.read_binding(ds, "CC0603KRX7R9BB104", root=d, maker="YAGEO", req=CAP_REQ)
    assert r["state"] == "REFUSED" and "not on the cited page" in r["why"], r
    # and a row that is on the page but does not map the code to what the binding claims
    d, ds = _decoded(YAGEO_PAGE, _yageo_fields(volt_row="8 = 25 V", volt_means="50 V", volt="8"))
    r = PI.read_binding(ds, "CC0603KRX7R8BB104", root=d, maker="YAGEO", req=CAP_REQ)
    assert r["state"] == "REFUSED" and "does not map" in r["why"], r


def t_a_decoded_binding_on_a_distributors_page_is_refused():
    page = ["LCSC Electronics product detail"] + YAGEO_PAGE[1:]
    d, ds = _decoded(page, _yageo_fields(), publisher="LCSC Electronics", mark="LCSC")
    r = PI.read_binding(ds, "CC0603KRX7R9BB104", root=d, maker="YAGEO", req=CAP_REQ)
    assert r["state"] == "REFUSED" and "distributor" in r["why"], r
    d, ds = _decoded(page + ["YAGEO"], _yageo_fields())   # the maker named, but the page is the distributor's
    r = PI.read_binding(ds, "CC0603KRX7R9BB104", root=d, maker="YAGEO", req=CAP_REQ)
    assert r["state"] == "REFUSED" and "distributor" in r["why"], r


def t_resistor_values_decode_by_the_makers_power_row():
    assert abs(PI._decode_value("1002", "ohm_3sig") - 10000.0) < 1e-9
    assert abs(PI._decode_value("270J", "ohm_3sig") - 27.0) < 1e-9
    assert abs(PI._decode_value("104", "pf_2sig") - 100e-9) < 1e-18
    assert abs(PI._decode_value("1R5", "pf_2sig") - 1.5e-12) < 1e-21
    assert PI._decode_value("10", "pf_2sig") is None and PI._decode_value("1002", "nope") is None
