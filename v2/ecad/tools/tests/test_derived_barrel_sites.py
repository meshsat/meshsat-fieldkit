#!/usr/bin/env python3
"""A barrel site in a placement generator is derived from a placed pad, never typed (MESHSAT-862, 21 September 2026).

`gen_pcb_e3.py`'s `_E_SITES` carried five coordinates typed from `barrel_sites --suggest` on E29's placement. E35
re-split the input side and moved TRKOUT, and on E35's pre-route board four of the five clusters (DC_HS, both DC_P,
TRK_OUT: 3, 7, 7 and 7 barrels) sat with NO pad of any net within 3 mm: twenty-four barrels of dead copper where the
parts used to be. The pad guard cannot see it (it refuses a barrel in ANOTHER net's pad, not one in nothing) and the
judge does not count it (outside every land's window), so nothing in the chain said a word. A typed coordinate is a
claim about a placement that was true once. Every site in the list is an expression of the placed pads now
(`_padc(ref, num)`), which is how VIN_RAW's island and barrels have been derived since E35."""
import ast, os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(TOOLS, "gen_pcb_e3.py")


def typed_sites(src):
    """The `_E_SITES` entries whose site is a literal pair of numbers (a typed coordinate)."""
    tree = ast.parse(src)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_E_SITES" for t in node.targets):
            if not isinstance(node.value, ast.List):
                continue
            for elt in node.value.elts:
                if isinstance(elt, ast.Tuple) and len(elt.elts) >= 2:
                    site = elt.elts[1]
                    if isinstance(site, ast.Tuple) and all(
                            isinstance(e, ast.Constant) or (isinstance(e, ast.UnaryOp) and isinstance(e.operand, ast.Constant))
                            for e in site.elts):
                        hits.append("line %d: %s" % (elt.lineno, ast.unparse(elt)[:80]))
    return hits


def t_every_barrel_site_of_the_e_generator_is_derived_from_a_placed_pad():
    hits = typed_sites(open(GEN).read())
    assert not hits, "a typed barrel site is a claim about a placement that was true once:\n" + "\n".join(hits)


def t_the_rule_names_a_typed_site_and_passes_a_derived_one():
    typed = '_E_SITES = [\n    ("DC_P", (-84.29, -92.64), 8.000, 0.40, "x"),\n]\n'
    derived = '_E_SITES = [\n    ("PV_P", _padc("Q3", "5"), 2.968, 0.30, "y"),\n]\n'
    assert typed_sites(typed) == ['line 2: (\'DC_P\', (-84.29, -92.64), 8.0, 0.4, \'x\')'], typed_sites(typed)
    assert typed_sites(derived) == []


def t_the_generator_still_declares_the_list_the_rule_reads():
    assert "_E_SITES = [" in open(GEN).read(), "the list moved or was renamed: the rule reads nothing"


def _skews(src):
    """Every skew a site in `_E_SITES` declares, read from the STATEMENT rather than from the words."""
    import ast
    t = ast.parse(src)
    out = []
    for n in ast.walk(t):
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "_E_SITES" for x in n.targets):
            for el in getattr(n.value, "elts", []):
                vals = getattr(el, "elts", [])
                if len(vals) >= 6 and isinstance(vals[5], ast.Constant):
                    out.append((getattr(vals[0], "value", "?"), float(vals[5].value)))
    return out


def _unrecorded(src, rec):
    """The sites whose skew is above an even split and whose number the board file does not carry."""
    return [(n, sk) for n, sk in _skews(src) if sk > 1.0 and ("%.2f" % sk) not in rec]


def t_a_site_that_declares_a_skew_carries_the_reading_that_measured_it():
    """A SKEW IS A MEASUREMENT AND NEVER A KNOB (21 September 2026, E39).

    `cluster(skew=)` multiplies the current a site is sized for, so a number typed into the generator buys
    barrels for a reason nobody can check. The project's own rule for that shape is the one every declaration
    here lives under: a declaration must never become an exemption, so the number has to be findable in the
    board file beside the reading that produced it. On E37's finished round-1 board PV_P's five barrels pass
    5.07 A with 1.747 A through one of them, which is the 1.72 the generator now declares.

    The defective fixture is a site declaring a skew the record does not carry; the acceptable one is the
    tree as it stands."""
    src = open(os.path.join(TOOLS, "gen_pcb_e3.py"), encoding="utf-8").read()
    rec = open(os.path.join(TOOLS, "boards", "e.json"), encoding="utf-8").read()
    assert _skews(src), "no site in _E_SITES carries a skew field, so this rule holds nothing"
    assert _unrecorded(src, rec) == [], \
        "sized at a skew boards/e.json carries no reading of: %s" % _unrecorded(src, rec)
    # THE SENTINEL MUST BE A NUMBER THE RECORD CANNOT CARRY, and the first one was not: 3.14 occurs in
    # boards/e.json as a real measurement, so the defective fixture read as already recorded and the rule
    # passed on a fixture that proved nothing. The fixture asserts its own absence now.
    assert "7.77" not in rec, "the sentinel occurs in the record, so this fixture would prove nothing"
    bad = "_E_SITES = [\n    ('PV_P', _padc('Q3', '5'), 2.968, 0.30, 'y', 7.77),\n]\n"
    assert _unrecorded(bad, rec) == [("PV_P", 7.77)], \
        "the defective fixture was not caught: %s" % _unrecorded(bad, rec)
