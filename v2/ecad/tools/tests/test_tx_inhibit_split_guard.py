#!/usr/bin/env python3
"""RF-002's walk reads a split symbol in ONE form only (integration of 27 September 2026, MESHSAT-1357 round 8 set 2).

tx_inhibit._module_refs joins the parts that carry one module only when the family is numbered by its maker (the Compute
Module 5 alone), the reference ends in one letter A to H right after a digit, and the sibling's own value or symbol names
the same family: board B's U30A plus U30B, U31A plus U31B and U32A plus U32B. The final independent check of the walk's
twelfth pass found that every other drawing of a split symbol reads PASS, mostly with no word (U30 plus U30B, U30-A plus
U30-B, a sibling on a symbol that names no family, an STM32H7, an RP2040, a PCA9555 or a 74LVC32A with its power unit as
its own reference). That is a named limit of the walk ((8) in tx_inhibit.py's header and RF-002's coverage note), not a
closed one, so this guard makes it loud on the REAL design: it reads the six committed netlists of the declared phases
and fails if any board carries a reference that looks like a unit of a split symbol (a unit letter, or a '-A' style
suffix, after the designator's number) other than the known ones below, each held to what it is.

The known references are not a waiver of the limit: the three Compute Module pairs are the form the walk joins (checked
here through _module_refs itself, so the guard fails if the walk stops joining them), and the other five are whole parts
whose names end in a letter for another reason (checked by their own value and symbol). A new split drawing, or a new
whole part named this way, fails here until the walk reads its form or the part is added below with its reason."""
import os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import phase_artefacts as PA
import tx_inhibit as T

# a unit letter or a separator-and-letter after the designator's number: U30A, U30-A, U30_B, U30.C
UNIT = re.compile(r"^(?P<base>[A-Za-z][A-Za-z_]*?\d+)(?P<sep>[-_.]?)(?P<unit>[A-Za-z])$")

# board B's Compute Module 5 receptacle pairs: the one form _module_refs joins (the sibling named, both ways)
MODULE_PAIRS = {"b": (("U30A", "U30B"), ("U31A", "U31B"), ("U32A", "U32B"))}
# whole parts whose reference ends in a letter for another reason, each with the words its own record must carry
WHOLE = {
    ("a", "J_54V"): (r"54 V", "the 54 V PoE feed connector, named for its voltage"),
    ("b", "J_54V"): (r"54 V", "the 54 V PoE feed connector from board A, named for its voltage"),
    ("b", "J_W1A"): (r"Conn_Coaxial|U\.FL", "one whole U.FL connector per antenna chain of the slot 1 WiFi card (chain A)"),
    ("b", "J_W1B"): (r"Conn_Coaxial|U\.FL", "one whole U.FL connector per antenna chain of the slot 1 WiFi card (chain B)"),
    ("b", "J_W3A"): (r"Conn_Coaxial|U\.FL", "one whole U.FL connector per antenna chain of the slot 3 WiFi card (chain A)"),
    ("b", "J_W3B"): (r"Conn_Coaxial|U\.FL", "one whole U.FL connector per antenna chain of the slot 3 WiFi card (chain B)"),
}


def _netlists():
    out = []
    for letter in PA.letters():
        net = PA.netlist(letter)
        if net and os.path.exists(net): out.append((letter, net))
    return out


def t_the_six_committed_netlists_are_read():
    """The guard reads every board with a netlist (a, b, c, d, e, p; E5 has none), so a board left out cannot hide a
    split drawing."""
    got = sorted(l for l, _n in _netlists())
    assert got == ["a", "b", "c", "d", "e", "p"], got


def t_no_board_carries_a_split_symbol_the_walk_reads_part_by_part():
    """FAILS on any reference that looks like a unit of a split symbol other than board B's Compute Module pairs (joined by
    the walk) and the whole parts listed with their reasons."""
    bad = []
    for letter, net in _netlists():
        nl = T.parse_netlist(net)
        sib = {x: y for pair in MODULE_PAIRS.get(letter, ()) for x, y in (pair, pair[::-1])}
        for ref in sorted(nl["comps"]):
            if not UNIT.match(ref): continue
            if ref in sib:
                # a listed module part counts only while the walk joins it with its sibling (U30 plus U30B is not joined)
                if sib[ref] in T._module_refs(nl, ref, T.fw_family(nl, ref)): continue
                bad.append("board %s %s, listed as a Compute Module pair, but the walk no longer joins it with %s" % (
                    letter, ref, sib[ref])); continue
            known = WHOLE.get((letter, ref))
            c = nl["comps"][ref]
            if known and re.search(known[0], "%s %s" % (c.get("value", ""), c.get("lib", ""))): continue
            bad.append("board %s %s (%s)%s" % (letter, ref, c.get("value", "")[:60],
                                               ": listed as whole, but its record no longer says so" if known else ""))
    assert not bad, "a reference that looks like a unit of a split symbol, which RF-002's walk reads part by part " \
        "(tx_inhibit.py header (8)): " + "; ".join(bad)


def t_the_compute_module_pairs_are_the_form_the_walk_joins():
    """Each listed pair is on board B and _module_refs joins it both ways; if the walk stopped joining it, or a pair were
    renamed, the allowance above would be a silent one."""
    nets = dict(_netlists())
    for letter, pairs in MODULE_PAIRS.items():
        nl = T.parse_netlist(nets[letter])
        for a, b in pairs:
            assert a in nl["comps"] and b in nl["comps"], (letter, a, b)
            for x, y in ((a, b), (b, a)):
                got = T._module_refs(nl, x, T.fw_family(nl, x))
                assert y in got, (letter, x, got)


def t_the_guard_catches_the_forms_the_final_check_named():
    """The pattern catches every split form the final check probed and none of the plain references of a board."""
    for ref in ("U30B", "U30-A", "U30_B", "U41A", "U77B", "U66A", "U9B", "U5.C"):
        assert UNIT.match(ref), ref
    for ref in ("U30", "R151", "C1", "J_PANEL", "SW_EMCON", "TP10", "LED_STAT", "Q106"):
        assert not UNIT.match(ref), ref
