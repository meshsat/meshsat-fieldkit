#!/usr/bin/env python3
"""The inventory REL-001 is asked about (`wear_inventory.py`, 28 September 2026, MESHSAT-1357).

A candidate is decided from what a part IS DRAWN AS, its reference class and its land, never from the words of
its description; a land or a class nobody declared makes the part a candidate; the words are a second net that
adds and never removes. Isolated fixtures; the real netlists are read once, read-only, at the end.
"""
import os, sys, re, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import wear_inventory as WI

INV = {"reference_classes": {"J": {"kind": "mechanical", "what": "a connector"},
                             "U": {"kind": "electrical", "what": "an integrated circuit"},
                             "D": {"kind": "electrical", "what": "a diode"},
                             "T": {"kind": "electrical", "what": "magnetics"}},
       "footprint": {"mechanical_libraries": ["Connector*"], "mechanical_names": ["*Conn*", "*target*"],
                     "soldered_libraries": ["Package_*", "Diode_*"], "soldered_names": ["Pulse_H5007NL"]}}
WEAR = re.compile(r"socket|receptacle|holder|header", re.I)


def _ident(v):
    import reliability
    return reliability.identity(v)


def _write(text):
    d = tempfile.mkdtemp(prefix="inv-")
    p = os.path.join(d, "x.net"); open(p, "w", encoding="utf-8").write(text); return p


def t_the_reference_class_is_the_letters_a_reference_begins_with():
    for ref, want in (("J_RF1", "J"), ("SW_SOS", "SW"), ("CAM_H1", "CAM"), ("U30A", "U"), ("TP6", "TP"), ("L_SIG", "L"),
                      ("T_CN1", "T"), ("WH_CN", "WH"), ("PAD_W1", "PAD"), ("1X", ""), ("", ""), (None, "")):
        assert WI.ref_class(ref) == want, (ref, WI.ref_class(ref), want)


def t_a_land_is_mechanical_soldered_undeclared_or_absent_and_mechanical_is_asked_first():
    assert WI.land_kind("Connector_JST:JST_VH_B2P", INV) == ("mechanical", "library Connector*")
    assert WI.land_kind("meshsat:CM5_Conn_A_10164227", INV) == ("mechanical", "name *Conn*")
    assert WI.land_kind("Mill-Max_0858_target", INV) == ("mechanical", "name *target*")        # a board file's bare name
    assert WI.land_kind("Package_TO_SOT_SMD:SOT-23-5", INV) == ("soldered", "library Package_*")
    assert WI.land_kind("meshsat:Pulse_H5007NL", INV) == ("soldered", "name Pulse_H5007NL")
    assert WI.land_kind("meshsat:Something_New", INV) == ("undeclared", "")
    assert WI.land_kind("", INV) == ("absent", "") and WI.land_kind(None, INV) == ("absent", "")
    # a land both lists could match is mechanical
    inv = dict(INV, footprint=dict(INV["footprint"], soldered_names=["*Conn*"]))
    assert WI.land_kind("meshsat:CM5_Conn_A", inv)[0] == "mechanical"


def t_candidacy_by_class_by_land_by_the_undeclared_and_by_words():
    parts = {"J1": {"value": "x", "footprint": "Package_SO:SOIC-8", "pins": 2},        # mechanical class: always
             "U30A": {"value": "receptacle", "footprint": "meshsat:CM5_Conn_A", "pins": 100},     # land mechanical
             "U9": {"value": "a module", "footprint": "meshsat:New_Module", "pins": 9},           # land undeclared: asked
             "U8": {"value": "a chip", "footprint": "", "pins": 5},                                # no land: asked
             "U7": {"value": "AND gate: card-socket supply enable", "footprint": "Package_TO_SOT_SMD:SOT-23-5", "pins": 5},
             "U6": {"value": "DF40 receptacle: module A", "footprint": "Package_TO_SOT_SMD:SOT-23-5", "pins": 100},
             "D2": {"value": "SMCJ40A holder", "footprint": "Diode_SMD:D_SMC", "pins": 2},        # never by words
             "T1": {"value": "magnetics", "footprint": "meshsat:Pulse_H5007NL", "pins": 24},      # soldered: out
             "ZZ1": {"value": "?", "footprint": "Package_SO:SOIC-8", "pins": 8}}                   # class nobody declared
    f = WI.candidates(parts, INV, (WEAR, ("D",), _ident))
    c = f["candidates"]
    assert sorted(c) == ["J1", "U30A", "U6", "U8", "U9", "ZZ1"], sorted(c)
    assert "reference class J" in c["J1"] and "mechanical or mating land" in c["U30A"], c
    assert "neither mechanical nor soldered" in c["U9"] and "carries no land" in c["U8"], c
    assert "names a receptacle" in c["U6"] and "not declared in the inventory" in c["ZZ1"], c
    assert f["by_words"] == ["U6"] and f["prose_only"] == ["U7"] and f["undeclared_class"] == ["ZZ1"], f
    assert f["how"] == {"reference_class": 1, "land": 1, "land_undeclared": 1, "no_land": 1, "undeclared_class": 1, "words": 1}, f["how"]
    # without the word net the soldered receptacle is out, and the rest is unchanged
    g = WI.candidates(parts, INV, None)
    assert sorted(g["candidates"]) == ["J1", "U30A", "U8", "U9", "ZZ1"], sorted(g["candidates"])


def t_the_rules_are_checked_before_they_are_used():
    assert WI.check_rules(None) and WI.check_rules({}) and WI.check_rules({"reference_classes": {}, "footprint": {}})
    bad = {"reference_classes": {"J": {"kind": "maybe", "what": "x"}, "U": {"kind": "electrical"}},
           "footprint": {"mechanical_libraries": "Connector*", "mechanical_names": [], "soldered_libraries": [], "soldered_names": []}}
    r = WI.check_rules(bad)
    assert any("J is declared with no kind" in x for x in r) and any("U does not say what" in x for x in r), r
    assert any("mechanical_libraries` is not a list" in x for x in r), r
    assert WI.check_rules(INV) == []


def t_a_netlist_is_read_with_its_lands_and_its_pin_counts():
    p = _write('(export (version "E")\n  (components\n    (comp (ref "J1")\n      (value "a \\"quoted\\" jack")\n'
               '      (footprint "Connector_Coaxial:SMA"))\n    (comp (ref "U1")\n      (value "chip"))\n  )\n'
               '  (nets\n    (net (code "1") (name "/A")\n      (node (ref "J1") (pin "1"))\n      (node (ref "U1") (pin "3")))\n'
               '    (net (code "2") (name "/B")\n      (node (ref "J1") (pin "2"))\n      (node (ref "NOBODY") (pin "1")))\n  )\n)\n')
    parts, raw = WI.read_netlist(p)
    assert parts == {"J1": {"value": 'a "quoted" jack', "footprint": "Connector_Coaxial:SMA", "pins": 2},
                     "U1": {"value": "chip", "footprint": "", "pins": 1}}, parts
    assert raw == open(p, "rb").read()


def t_what_cannot_be_read_says_why():
    for text, why in (("", "is empty"), ("   \n", "is empty"), ("(export (components (comp (ref \"J1\"))", "never close"),
                      ("hello (export)", "does not begin"),
                      ("(export (components))\n)", "text follows"), (")(export)", "never opened"), ("(export (components)) (more)", "text follows"),
                      ("(kicad_pcb (version 1))", "not a (export"), ('(export (comp (ref "J1")))', "no (components"),
                      ('(export (components (comp (value "x"))))', "carries no reference"),
                      ('(export (components (comp (ref "J1")) (comp (ref "J1"))))', "there twice")):
        try:
            WI.read_netlist(_write(text))
        except WI.Unreadable as e:
            assert why in str(e), (text, str(e))
        else:
            raise AssertionError("read: %r" % text)
    p = _write("x"); open(p, "wb").write(b"(export \xff\xfe)")
    try: WI.read_netlist(p)
    except WI.Unreadable as e: assert "UTF-8" in str(e), str(e)
    else: raise AssertionError("read bytes that are not text")
    try: WI.read_netlist(os.path.join(tempfile.gettempdir(), "no-such-file-anywhere.net"))
    except WI.Unreadable as e: assert "cannot be opened" in str(e), str(e)
    else: raise AssertionError("read a file that is not there")


def t_a_board_file_is_read_from_its_footprints_with_pads_as_pins():
    p = _write('(kicad_pcb (version 20241229) (generator "fixture")\n'
               '  (footprint "Mill-Max_0858_target" (layer "F.Cu") (at 1 2)\n    (property "Reference" "T_CN1" (at 0 0))\n'
               '    (property "Value" "return target" (at 0 0))\n    (pad "1" smd circle (at 0 0) (size 1 1))\n  )\n'
               '  (footprint "WireLands_2x6" (layer "F.Cu")\n    (property "Reference" "L_SIG")\n    (property "Value" "lands")\n'
               '    (pad "1" thru_hole circle (at 0 0) (size 1 1) (drill 0.5))\n    (pad "2" thru_hole circle (at 1 0) (size 1 1) (drill 0.5))\n  )\n'
               '  (gr_text "legend" (at 0 0))\n)\n')
    parts, _raw = WI.read_board(p)
    assert parts == {"T_CN1": {"value": "return target", "footprint": "Mill-Max_0858_target", "pins": 1},
                     "L_SIG": {"value": "lands", "footprint": "WireLands_2x6", "pins": 2}}, parts
    f = WI.candidates(parts, dict(INV, reference_classes=dict(INV["reference_classes"], L={"kind": "electrical", "what": "an inductor"})),
                      None)
    assert sorted(f["candidates"]) == ["L_SIG", "T_CN1"], f       # electrical classes, found by their lands
    try: WI.read_board(_write('(export (version "E"))'))
    except WI.Unreadable as e: assert "not a (kicad_pcb" in str(e), str(e)
    else: raise AssertionError("a netlist read as a board")


def t_land_patterns_match_the_whole_land_and_its_bare_name():
    assert WI.land_matches("Connector_JST:JST_VH_B2P-VH_1x02", ["Connector_JST:JST_VH_*"])
    assert WI.land_matches("Connector_JST:JST_VH_B2P-VH_1x02", ["JST_VH_*"])
    assert WI.land_matches("JST_VH_B2P-VH_1x02", ["JST_VH_*"])
    assert not WI.land_matches("Connector_JST:JST_PH_B4B", ["JST_VH_*"])
    assert not WI.land_matches(None, ["JST*"])


def t_the_declared_phase_is_resolved_as_rules_status_resolves_it():
    """`wear_inventory.artefact` answers with `phase_artefacts`, and the suite holds that equal to
    `rules_status._phase_dir` for every board of the manifest (test_artefact_recording). Here: every manifest
    board resolves to a file under its phase directory, E5 to its board file, and an unknown letter to nothing."""
    import phase_artefacts as PA, rules_status as S
    m = S.manifest()
    for letter in PA.letters():
        kind, path = WI.artefact(letter)
        assert path and os.path.dirname(path).startswith(S._phase_dir(letter, m)), (letter, path)
        assert kind == ("board_file" if PA.no_schematic(letter) else "netlist"), (letter, kind)
        assert path.endswith(".kicad_pcb" if kind == "board_file" else ".net"), path
    assert WI.artefact("zz") == (None, None)


def t_every_reference_class_of_the_real_artefacts_is_declared():
    """A new prefix on a board must be classed deliberately: the committed list declares every class the six
    netlists and board E5's board file use, read here without any gate."""
    import yaml, reliability as REL, phase_artefacts as PA
    d = yaml.safe_load(open(REL.REL, encoding="utf-8"))
    declared = set(d["inventory"]["reference_classes"])
    used = set()
    for letter in PA.letters():
        kind, path = WI.artefact(letter)
        parts, _raw = WI.read(kind, path)
        used |= {WI.ref_class(r) for r in parts}
    assert used <= declared, "reference classes on the boards that the inventory does not declare: %s" % sorted(used - declared)
    assert {"J", "U", "TP", "SW", "H", "W", "F", "BT", "K", "T", "L", "WH"} <= used, sorted(used)
