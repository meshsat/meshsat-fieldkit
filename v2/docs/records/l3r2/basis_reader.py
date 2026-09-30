#!/usr/bin/env python3
"""Read the energy basis's outputs by exact keys (L3-R2, MESHSAT-1357, 30 September 2026).

Stream l3plane's energy basis prints its figures in two outputs, `weather_basis.out` and `energy_basis.out`
(v2/docs/records/l3plane/ once filed). This module reads the tables layer 3's rows need, each row by an exact key and each
column by an exact pattern, and refuses (BasisError) when a section, a header or a key is not where the format puts it: a
figure is never found by searching for its digits. Figures are kept as the text the output prints them ("3.80", not 3.8), so a figure on
the pages is the basis's own. Written against the format of the basis's fourth issue (fnd/l3plane 06b8ecea, whose
weather_basis.out and energy_basis.out equal the third issue's, 868c321f); any other format is refused, never guessed. Nothing here writes; fill_l3r2_from_basis.py writes what it returns,
and od_l3_6.py re-reads the filed outputs through it and compares with l3r2.yaml before any answer is written.

  sizing(text)          weather_basis.out B: {(basis, build): row}, basis 'mean-day', '50', '80' or '95', build TYP or WAB
  coverage(text)        weather_basis.out A: {(lid, case): {STOP, COMB, EACH}}, e.g. ('4S15P QMX out', 'WE TYP')
  stores(text)          weather_basis.out B: the lids' current stores at WE on the mean day
  allowances(text)      weather_basis.out B: the allowances between nominal and usable, per pack of the 4S21P kit
  reference_plane(text) energy_basis.out 5: {(lid, case): {TYP, TYP_lines, WAB, WAB_lines}}
  four_cases(text)      three_cases.out 2: {(case, inputs, lid): {TYP, TYP_lines, WAB, WAB_lines}}, case a (as drawn), a'
                        (the derated variant), b (resistor-only, its lower bound: INCONCLUSIVE), c (the corrected path:
                        HYPOTHETICAL); inputs NOM or WE
  four_coverage(text)   three_cases.out 3: {(case, inputs, lid): {STOP, COMB, EACH}}
  derated_setting(text) three_cases.out 1: U3's setting in the derated variant, e.g. '4.05'
Every table is read whole: its row count is checked (CHECK-3 of L3-R2, minor 5).

Usage: python3 basis_reader.py WEATHER_OUT ENERGY_OUT [THREE_CASES_OUT]   (prints what it reads, for a look at a basis
       before filing)
"""
import re
import sys

LIDS = {"4S9P both kept": "both-kept", "4S14P tablet out": "tablet-out", "4S15P QMX out": "qmx-out"}
BASES = {"(i) SC-37's mean day, 40/0": "mean-day"}
NUM = r"(\d+(?:\.\d+)?)"


class BasisError(Exception):
    pass


def section(text, start, end):
    """The lines from the one line that begins with `start` up to the next that begins with `end` (exact, at column 0)."""
    lines = text.split("\n")
    a = [i for i, l in enumerate(lines) if l.startswith(start)]
    if len(a) != 1: raise BasisError("section %r occurs %d times" % (start, len(a)))
    b = [i for i, l in enumerate(lines) if i > a[0] and l.startswith(end)]
    if not b: raise BasisError("section %r has no end %r" % (start, end))
    return lines[a[0]:b[0]]


SIZING_HEAD = re.compile(r"^\s+basis\s+build\s+usable, Wh\s+lid, 4SnP\s+cells \(4S\)\s+nominal, Wh\s+mass, kg\s+"
                         r"volume, l \(cyl / box\)\s+x the 4S21P: Wh; cells\s+fits\?\s*$")
SIZING_ROW = re.compile(r"^\s{3}(\(i\) SC-37's mean day, 40/0|\(ii\) (\d+) % of the windows)\s{2,}(TYP|WAB)\s+" + NUM +
                        r"\s+(4S\d+P)\s+(\d+)\s+" + NUM + r"\s+" + NUM + r"\s+" + NUM + r" / " + NUM + r"\s+" + NUM +
                        r"; " + NUM + r"\s+(fits .+?)\s*$")


def fits(text):
    """'fits no established arrangement' -> []; 'fits 4S14P tablet out, 4S15P QMX out' -> ['tablet-out', 'qmx-out']."""
    if text == "fits no established arrangement": return []
    if not text.startswith("fits "): raise BasisError("a fit reads %r" % text)
    out = []
    for part in text[5:].split(", "):
        if part not in LIDS: raise BasisError("a fit names %r, which is not one of the lids %s" % (part, sorted(LIDS)))
        out.append(LIDS[part])
    return out


def sizing(text):
    sec = section(text, "B. THE STORE EACH WEATHER BASIS WOULD NEED", "C. ")
    heads = [i for i, l in enumerate(sec) if SIZING_HEAD.match(l)]
    if len(heads) != 1: raise BasisError("weather_basis.out B's sizing header occurs %d times" % len(heads))
    out = {}
    for l in sec[heads[0] + 1:]:
        m = SIZING_ROW.match(l)
        if not m:
            if out: break
            raise BasisError("the line after the sizing header is not a sizing row: %r" % l[:80])
        basis = m.group(2) or BASES[m.group(1)]
        key = (basis, m.group(3))
        if key in out: raise BasisError("sizing row %s occurs twice" % (key,))
        out[key] = {"usable_wh": m.group(4), "lid_block": m.group(5), "cells": int(m.group(6)),
                    "nominal_wh": m.group(7), "mass_kg": m.group(8), "volume_cyl_l": m.group(9),
                    "volume_box_l": m.group(10), "x_wh": m.group(11), "x_cells": m.group(12),
                    "fits": fits(m.group(13))}
    want = {(b, c) for b in ("mean-day", "50", "80", "95") for c in ("TYP", "WAB")}
    if set(out) != want: raise BasisError("sizing rows %s, not %s" % (sorted(out), sorted(want)))
    return out


COV_ROW = re.compile(r"^\s{3}(4S\d+P [A-Za-z ]+?)\s{2,}((?:WE-LO|WE-MKR|WE60|WEL|WE|WA|NOM) (?:TYP|WAB))\s+" +
                     r"\s+".join([r"(\d+ of \d+ \(\s*\d+\.\d %\))"] * 3) + r"\s*$")


def coverage(text):
    sec = section(text, "A. THE MODELLED HISTORICAL COVERAGE", "B. ")
    heads = [i for i, l in enumerate(sec) if re.match(r"^\s+lid\s+case\s+windows kept: no STOP\s+COMB above the floor\s+"
                                                    r"EACH above the floor\s*$", l)]
    if len(heads) != 1: raise BasisError("weather_basis.out A's coverage header occurs %d times" % len(heads))
    out = {}
    for l in sec[heads[0] + 1:]:
        m = COV_ROW.match(l)
        if not m:
            if out: break
            raise BasisError("the line after the coverage header is not a coverage row: %r" % l[:80])
        if m.group(1) not in LIDS: raise BasisError("coverage names the lid %r" % m.group(1))
        out[(m.group(1), m.group(2))] = {k: " ".join(m.group(i).split()) for k, i in (("STOP", 3), ("COMB", 4), ("EACH", 5))}
    want = {(lid, c) for lid in LIDS for c in ("WE TYP", "WE WAB", "WE-LO TYP", "WE-MKR TYP", "NOM TYP")}
    if set(out) != want: raise BasisError("weather_basis.out A reads %d coverage rows, not the %d of three lids by five cases: %s"
                                          % (len(out), len(want), sorted(set(want) ^ set(out))[:4]))
    return out


STORE_ROW = re.compile(r"^\s+(4S\d+P [A-Za-z ]+?)\s+(\d+) cells, " + NUM + r" Wh nominal, " + NUM + r" Wh usable \(" + NUM +
                       r" of nominal")


def stores(text):
    sec = section(text, "B. THE STORE EACH WEATHER BASIS WOULD NEED", "C. ")
    out = {}
    for l in sec:
        m = STORE_ROW.match(l)
        if m:
            if m.group(1) not in LIDS: raise BasisError("a store names the lid %r" % m.group(1))
            out[m.group(1)] = {"cells": int(m.group(2)), "nominal_wh": m.group(3), "usable_wh": m.group(4),
                               "fraction": m.group(5)}
    if set(out) != set(LIDS): raise BasisError("the current stores name %s, not %s" % (sorted(out), sorted(LIDS)))
    return out


ALLOW = re.compile(r"(base|lid) (4S\d+P) at ([+\-]?\d+(?:\.\d+)? C)\s+" + NUM + r" A a cell: .*?: " + NUM +
                   r" of nominal, " + NUM + r" Wh")


def allowances(text):
    sec = section(text, "B. THE STORE EACH WEATHER BASIS WOULD NEED", "C. ")
    a = [i for i, l in enumerate(sec) if l.strip().startswith("the allowances between nominal and usable")]
    b = [i for i, l in enumerate(sec) if l.strip().startswith("cell limits:")]
    if len(a) != 1 or len(b) != 1 or b[0] < a[0]: raise BasisError("the allowances block is not where B puts it")
    joined = " ".join(" ".join(sec[a[0] + 1:b[0]]).split())
    out = [{"pack": m.group(1), "block": m.group(2), "at": m.group(3), "a_cell": m.group(4),
            "fraction": m.group(5), "usable_wh": m.group(6)} for m in ALLOW.finditer(joined)]
    if [x["pack"] for x in out] != ["base", "lid"]: raise BasisError("the allowances are not one base and one lid line")
    return out


VAL = r"(NOT MET,\s+\d+\.\d unserved|\d+\.\d \(base\s+\d+\.\d, lid\s+\d+\.\d\))"
REF_ROW = re.compile(r"^\s{3}(4S\d+P)\s+([A-Z0-9]+)\s+" + VAL + r"\s+([YN]/[YN])\s+" + VAL + r"\s+([YN]/[YN])\s*$")


def reference_plane(text):
    sec = section(text, "5. THE CASES ON THE REFERENCE PLANE", "6. ")
    heads = [i for i, l in enumerate(sec) if re.match(r"^\s+lid\s+case\s+TYP\s+COMB/EACH WAB\s+COMB/EACH\s*$", l)]
    if len(heads) != 1: raise BasisError("energy_basis.out 5's header occurs %d times" % len(heads))
    out = {}
    for l in sec[heads[0] + 1:]:
        if not l.strip(): continue
        m = REF_ROW.match(l)
        if not m: raise BasisError("energy_basis.out 5 carries a line that is not a case row: %r" % l[:80])
        key = (m.group(1), m.group(2))
        if key in out: raise BasisError("case row %s occurs twice" % (key,))
        out[key] = {"TYP": " ".join(m.group(3).split()), "TYP_lines": m.group(4),
                    "WAB": " ".join(m.group(5).split()), "WAB_lines": m.group(6)}
    cases = ("NOM", "WE", "WE60", "WEL", "WA", "WE1", "GEN", "M207", "SC76")
    want = {(lid, c) for lid in ("4S9P", "4S14P", "4S15P") for c in cases}
    if set(out) != want: raise BasisError("energy_basis.out 5 reads %d case rows, not the %d of three lids by nine cases"
                                          % (len(out), len(want)))
    return out


# three_cases.out (the fourth issue): the four power-path cases, kept apart (D-24, D-25)
FOUR_HEADS = [
    ("AS DRAWN, NOM inputs:", ("a", "NOM")),
    ("AS DRAWN, WE inputs:", ("a", "WE")),
    ("DERATED VARIANT of AS DRAWN, NOM inputs:", ("a'", "NOM")),
    ("DERATED VARIANT, WE inputs:", ("a'", "WE")),
    ("RESISTOR-ONLY, lower bound under B-5's inferred collapse, NOM inputs (INCONCLUSIVE", ("b", "NOM")),
    ("RESISTOR-ONLY, lower bound under B-5's inferred collapse, WE inputs (INCONCLUSIVE", ("b", "WE")),
    ("CORRECTED PATH, HYPOTHETICAL, NOM inputs (", ("c", "NOM")),
    ("CORRECTED PATH, HYPOTHETICAL, WE inputs, CONDITIONAL", ("c", "WE")),
]
FOUR_ROW = re.compile(r"^\s{5}(4S\d+P [A-Za-z ]+?)\s{2,}TYP\s+" + VAL + r"\s+([YN]/[YN])\s+WAB\s+" + VAL + r"\s+([YN]/[YN])\s*$")


def four_cases(text):
    sec = section(text, "2. THE REFERENCE DAY AT 40/0", "3. ")
    out, key = {}, None
    for l in sec[1:]:
        s = l.strip()
        if not s: continue
        head = [k for p, k in FOUR_HEADS if s.startswith(p)]
        if head:
            key = head[0]
            if any(k[:2] == key for k in out): raise BasisError("three_cases.out 2 repeats the block %s" % (key,))
            continue
        m = FOUR_ROW.match(l)
        if m and key:
            if m.group(1) not in LIDS: raise BasisError("three_cases.out 2 names the lid %r" % m.group(1))
            out[key + (m.group(1),)] = {"TYP": " ".join(m.group(2).split()), "TYP_lines": m.group(3),
                                        "WAB": " ".join(m.group(4).split()), "WAB_lines": m.group(5)}
        elif l.startswith("     ") and not s.startswith(("the proposed", "the as-drawn")):
            raise BasisError("three_cases.out 2 carries a line that is neither a block head nor a row: %r" % l[:80])
    want = {k + (lid,) for _, k in FOUR_HEADS for lid in LIDS}
    if set(out) != want: raise BasisError("three_cases.out 2 reads %d rows, not the %d of eight blocks by three lids"
                                          % (len(out), len(want)))
    return out


FOUR_COV_LABELS = {"AS DRAWN, NOM (upper bound)": ("a", "NOM"), "DERATED VARIANT, NOM": ("a'", "NOM"),
                   "RESISTOR-ONLY lower bound, NOM": ("b", "NOM"), "RESISTOR-ONLY lower bound, WE": ("b", "WE"),
                   "CORRECTED PATH, HYPOTHETICAL, NOM": ("c", "NOM"), "CORRECTED PATH, HYPOTHETICAL, WE": ("c", "WE")}
COUNT = r"(\d+ \(\s*\d+\.\d %\))"
FOUR_COV = re.compile(r"^\s{3}(%s)\s{2,}(4S\d+P [A-Za-z ]+?)\s{2,}%s\s+/\s+%s\s+/\s+%s(?:\s+\(weather_basis\.out A, reproduced\))?\s*$"
                      % ("|".join(re.escape(k) for k in FOUR_COV_LABELS), COUNT, COUNT, COUNT))


def four_coverage(text):
    sec = section(text, "3. THE MODELLED HISTORICAL COVERAGE", "END.")
    out = {}
    for l in sec[1:]:
        m = FOUR_COV.match(l)
        if not m: continue
        if m.group(2) not in LIDS: raise BasisError("three_cases.out 3 names the lid %r" % m.group(2))
        key = FOUR_COV_LABELS[m.group(1)] + (m.group(2),)
        if key in out: raise BasisError("three_cases.out 3 repeats %s" % (key,))
        out[key] = {k: " ".join(m.group(i).split()) for k, i in (("STOP", 3), ("COMB", 4), ("EACH", 5))}
    want = {k + (lid,) for k in list(FOUR_COV_LABELS.values())[:4] for lid in LIDS} | \
           {k + (lid,) for k in list(FOUR_COV_LABELS.values())[4:] for lid in ("4S14P tablet out", "4S15P QMX out")}
    if set(out) != want: raise BasisError("three_cases.out 3 reads %d coverage rows, not %d" % (len(out), len(want)))
    return out


def derated_setting(text):
    sec = section(text, "1. THE ELECTRICAL LIMITS FED IN", "2. ")
    found = re.findall(r"the derated variant (\d+\.\d+) A", " ".join(" ".join(sec).split()))
    if len(found) != 1: raise BasisError("three_cases.out 1 names the derated setting %d times" % len(found))
    return found[0]


def main(argv):
    w, e = open(argv[0], encoding="utf-8").read(), open(argv[1], encoding="utf-8").read()
    c = open(argv[2], encoding="utf-8").read() if len(argv) > 2 else None
    try:
        for k, v in sorted(sizing(w).items()): print("sizing", k, v)
        for k, v in sorted(coverage(w).items()): print("coverage", k, v)
        for k, v in sorted(stores(w).items()): print("store", k, v)
        for v in allowances(w): print("allowance", v)
        for k, v in sorted(reference_plane(e).items()): print("reference", k, v)
        if c is not None:
            print("derated setting", derated_setting(c))
            for k, v in sorted(four_cases(c).items()): print("four-case", k, v)
            for k, v in sorted(four_coverage(c).items()): print("four-case coverage", k, v)
    except BasisError as x:
        print("basis_reader: REFUSED: %s" % x); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
