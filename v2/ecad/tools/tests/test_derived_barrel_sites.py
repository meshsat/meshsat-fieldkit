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
