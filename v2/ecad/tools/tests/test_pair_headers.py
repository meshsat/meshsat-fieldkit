#!/usr/bin/env python3
"""Where a differential pair may sit on a two-row 2.54 mm header, checked in the generators that write the pin map.

Measured on D's /USB_D8 (11 September 2026, MESHSAT-862). J_HARN1 is a 2x8 at 2.54 mm with 1.70 mm pads, so the
channel between the two columns is 2.54 - 1.70 = 0.84 mm. A 0.30/0.20/0.30 pair needs its own 0.80 mm plus the
class clearance on both sides, 1.20 mm at 0.20. The pins are through-hole, so the channel is 0.84 mm on every
layer and no inner row can be left coupled in any direction. The pre-router had been reporting exactly that for
two days as "the legs clear no smoothing of the centreline", each leg about 1.0 mm from a neighbouring pin's pad,
and the reading of that line as a smoothing problem is what cost the time: it is an escape that does not exist.

Two placements do work and the rule admits both:
  an END row (pins 1/2 or the last two), which escapes past the end of the connector into free board;
  the same column on adjacent rows, which escapes sideways away from the other column.
On a ribbon only the first is available, because the cable pairs adjacent conductors and the same column is
conductors n and n+2. Anything else is declared in tools/pair-header-allow.txt with its reason."""
import os, re, ast

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREE = os.environ.get("PAIR_HEADER_TREE", TOOLS)   # so the rule can be run against a pre-fix copy of the tree
PART = re.compile(r'part\(\s*"([^"]+)"\s*,\s*"Connector_Generic"\s*,\s*"(Conn_02x(\d+)_Odd_Even)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*,\s*"([^"]*)"\s*,\s*(\{.*?\})\s*\)', re.S)


def headers():
    """[(file, ref, rows, {pin: net})] for every two-row connector a schematic generator writes."""
    out = []
    for fn in sorted(os.listdir(TREE)):
        if not (fn.startswith("gen_sch_") and fn.endswith(".py")): continue
        for m in PART.finditer(open(os.path.join(TREE, fn), errors="replace").read()):
            try: pins = ast.literal_eval(m.group(6))
            except (ValueError, SyntaxError): continue
            out.append((fn, m.group(1), int(m.group(3)), {int(k): v for k, v in pins.items() if k.isdigit()}))
    return out


def pairs_of(pins):
    """[(p_pin, n_pin, stem)] for every _P/_N pair both of whose halves are on this connector."""
    ps = {v[:-2]: k for k, v in pins.items() if v.endswith("_P")}
    ns = {v[:-2]: k for k, v in pins.items() if v.endswith("_N")}
    return [(ps[s], ns[s], s) for s in sorted(set(ps) & set(ns))]


def allowed():
    """{(ref, stem): reason} from tools/pair-header-allow.txt. A line with no reason declares nothing."""
    out = {}
    p = os.path.join(TOOLS, "pair-header-allow.txt")
    if not os.path.exists(p): return out
    for ln in open(p, errors="replace"):
        ln = ln.strip()
        if not ln or ln.startswith("#") or "#" not in ln: continue
        key, reason = ln.split("#", 1)
        f = key.split()
        if len(f) == 2 and reason.strip(): out[(f[0], f[1])] = reason.strip()
    return out


def where(p, n, rows):
    """"end row", "same column" or the reason it is neither."""
    lo, hi = min(p, n), max(p, n)
    if (lo, hi) == (1, 2) or (lo, hi) == (2 * rows - 1, 2 * rows): return "end row"
    if (hi - lo) == 2 and (lo % 2) == (hi % 2): return "same column"
    return "row %d, an inner row: the 0.84 mm channel between the columns does not pass a 0.80 mm pair" % ((lo + 1) // 2)


def t_every_header_pair_can_escape_coupled():
    bad, seen = [], 0
    ok = allowed()
    for fn, ref, rows, pins in headers():
        for p, n, stem in pairs_of(pins):
            seen += 1
            w = where(p, n, rows)
            if w in ("end row", "same column"): continue
            if (ref, stem) in ok: continue
            bad.append("%s %s pins %d/%d (%s): %s" % (fn, ref, p, n, stem, w))
    assert seen, "no two-row connector pair was found at all: the parser stopped matching"
    assert not bad, "a pair sits where no coupled escape exists and nothing declares it:\n  " + "\n  ".join(bad)


def t_a_declared_exception_carries_a_reason():
    """The erc-allow idiom: a line without a written reason silences nothing (it is not even parsed as a line)."""
    p = os.path.join(TOOLS, "pair-header-allow.txt")
    if not os.path.exists(p): return
    for ln in open(p, errors="replace"):
        s = ln.strip()
        if not s or s.startswith("#"): continue
        assert "#" in s and s.split("#", 1)[1].strip(), "declaration without a reason: " + s


def t_the_rule_places_the_two_fixed_boards_on_an_end_row():
    """D's J_HARN1 and A's J_MEZZ1 carry one map and it is the one this rule was written for."""
    got = {}
    for fn, ref, rows, pins in headers():
        if ref in ("J_HARN1", "J_MEZZ1"):
            for p, n, stem in pairs_of(pins): got[(ref, stem)] = where(p, n, rows)
    assert got, "neither harness connector was parsed"
    for k, v in got.items(): assert v == "end row", (k, v)


def t_the_two_maps_of_one_harness_agree():
    """The cable has one pinout. check_contracts compares the netlists; this compares the generators."""
    maps = {}
    for fn, ref, rows, pins in headers():
        if ref in ("J_HARN1", "J_MEZZ1"): maps[ref] = pins
    if len(maps) == 2:
        a, b = maps["J_HARN1"], maps["J_MEZZ1"]
        diff = [k for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
        assert not diff, "the harness maps differ at pins %s" % diff


def t_a_board_that_declares_no_coupled_fraction_keeps_the_10_september_rule():
    """Owner ruling 15 September 2026 02:40 CEST, delegating decision 24 to the session, which took option 2.
    Only a board that declares pair_coupled_fraction is judged on its coupled length; every other board is
    held until every pair is laid, the 10 September rule, and nothing weakens for A, C, D, E or P."""
    import json, os
    src = open(os.path.join(TOOLS, "impedance_check.py")).read()
    assert '_bd.get("pair_coupled_fraction")' in src, "the gate does not read the declaration"
    assert "res = _v.PASS if not miss else _v.FAIL" in src, "the undeclared board no longer refuses on one missed pair"
    full = open(os.path.join(TOOLS, "full.sh")).read()
    assert 'PCF="$(cfg pair_coupled_fraction)"' in full and 'if [ "$PP" -ne 0 ] && [ -n "$PCF" ]' in full, (
        "the pre-route pair gate does not read the declaration, so a fraction board would still be held on a count")
    assert "judges it by length, so the chain proceeds" in full, (
        "the pre-route gate compares a COUNT of pairs with a bar the ruling states as a LENGTH fraction")
    for letter in ("a", "c", "d", "e", "p"):
        d = json.load(open(os.path.join(TOOLS, "boards", letter + ".json")))
        assert d.get("pair_coupled_fraction") is None, "board %s declares a coupled fraction nobody ruled for it" % letter
    b = json.load(open(os.path.join(TOOLS, "boards", "b.json")))
    assert b.get("pair_coupled_fraction") == 0.80, "B does not declare the 0.80 the session took"
    assert "unblock B from my decision" in b.get("_pair_coupled_fraction_why", ""), "the declaration does not carry the owner's words"


def t_the_board_fraction_is_length_weighted_and_every_pair_is_still_named():
    import os
    src = open(os.path.join(TOOLS, "impedance_check.py")).read()
    assert "_cov_len = sum(r[10] * r[4] for r in _judged)" in src, "the board fraction is not weighted by each pair's judged length"
    assert 'evidence=["%s %s class %s target %s ohm" % (r[6], r[0], r[1], r[2]) for r in results if r[6] != "MET"]' in src, (
        "a pair that misses is no longer named in the verdict's evidence")
