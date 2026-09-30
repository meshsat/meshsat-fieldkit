#!/usr/bin/env python3
"""Read stream l3batt's runtime.out by exact keys (layer 3 round 5, MESHSAT-1357, 30 September 2026).

The pattern of v2/docs/records/l3r2/basis_reader.py: every figure is the text the output prints, found by the exact form
of its line, and a section that does not carry the number of lines it must is refused (RuntimeFormatError), never read in
part. Nothing is computed here.

  battery_only(text)  section 1: {arrangement: {usable_20, usable_m10, hours_20, hours_m10}} for D06, A35, the 21700 lids
                      and the external packs X-NH1, X-NH2
  store_start(text)   section 2: {base, lid, total}, the usable store at the start (aged)
  solar(text)         section 2: {(hours, case, build): {status, stops, unserved}}, hours 48 and 72, cases DRAWN, NOM,
                      NOM90, WE, WE90, builds TYP and WAB
  upgrade(text)       section 3: {(hours, case, build): {lid, cells, wh}}, the addition over the both-kept 4S9P lid, cases
                      NOM, WE, NOM90
  hf_listening(text)  section 3's sensitivity: {(hours, case): {lid, cells, wh}}, TYP, cases NOM and WE
  coverage(text)      section 4: {(hours, case): (kept, comb, each)} for the both-kept lid
  reproduced(text)    True when both of the output's reproduction lines read yes

Usage: python3 runtime_reader.py [PATH]   (prints what it reads, as JSON)
"""
import json
import re
import sys

ARR = ("D06", "A35", "A21-P45B", "A21-50E", "A21-M50LT", "X-NH1", "X-NH2")
CASES2 = ("DRAWN", "NOM", "NOM90", "WE", "WE90")
CASES3 = ("NOM", "WE", "NOM90")


class RuntimeFormatError(Exception):
    pass


def _section(text, start, end):
    a = text.find(start)
    if a < 0: raise RuntimeFormatError("runtime.out carries no %r" % start)
    b = text.find(end, a + len(start))
    if b < 0: raise RuntimeFormatError("runtime.out carries no %r after %r" % (end, start))
    return text[a:b]


def battery_only(text):
    s = _section(text, "1. BATTERY-ONLY ENDURANCE", "2. BATTERY PLUS SOLAR")
    rx = re.compile(r"^\s+(%s): .*?usable\s+(\d+\.\d) Wh /\s+(\d+\.\d) Wh:\s+(\d+\.\d\d) h at \+20 C,\s+(\d+\.\d\d) h at -10 C$"
                    % "|".join(re.escape(a) for a in ARR), re.M)
    out = {}
    for m in rx.finditer(s):
        if m.group(1) in out: raise RuntimeFormatError("%s is printed twice" % m.group(1))
        out[m.group(1)] = {"usable_20": m.group(2), "usable_m10": m.group(3), "hours_20": m.group(4), "hours_m10": m.group(5)}
    if sorted(out) != sorted(ARR): raise RuntimeFormatError("section 1 carries %s, not %s" % (sorted(out), sorted(ARR)))
    return out


def store_start(text):
    m = re.findall(r"the store at the start \(usable, aged\): base (\d+\.\d) Wh at \+20 C and lid (\d+\.\d) Wh at 13\.23 C, "
                   r"(\d+\.\d) Wh together", text)
    if len(m) != 1: raise RuntimeFormatError("the store at the start is printed %d times" % len(m))
    return {"base": m[0][0], "lid": m[0][1], "total": m[0][2]}


def solar(text):
    s = _section(text, "2. BATTERY PLUS SOLAR", "3. THE STORE THAT CARRIES")
    out = {}
    for hours, head, nxt in (("48", "   48 HOURS\n", "   72 HOURS\n"), ("72", "   72 HOURS\n", "   the cases:")):
        blk = _section(s, head, nxt)
        rx = re.compile(r"^\s+(%s)\s+TYP (NOT MET|MET), stops at h (\d+/\d+), (\d+\.\d) unserved\s+WAB (NOT MET|MET), stops at h "
                        r"(\d+/\d+), (\d+\.\d) unserved$" % "|".join(CASES2), re.M)
        got = rx.findall(blk)
        if [g[0] for g in got] != list(CASES2): raise RuntimeFormatError("the %s h block carries %s" % (hours, [g[0] for g in got]))
        for g in got:
            out[(hours, g[0], "TYP")] = {"status": g[1], "stops": g[2], "unserved": g[3]}
            out[(hours, g[0], "WAB")] = {"status": g[4], "stops": g[5], "unserved": g[6]}
    return out


def upgrade(text):
    s = _section(text, "3. THE STORE THAT CARRIES", "SENSITIVITY, the QMX receiving")
    rx = re.compile(r"^\s+(48|72) h (NOM|WE|NOM90)\s+(TYP|WAB): lid (4S\d+\.\d\dP), against the both-kept 4S9P: \+(\d+\.\d) 35E "
                    r"cells, \+(\d+\.\d) Wh usable$", re.M)
    out = {}
    for m in rx.finditer(s):
        k = (m.group(1), m.group(2), m.group(3))
        if k in out: raise RuntimeFormatError("%s is printed twice" % (k,))
        out[k] = {"lid": m.group(4), "cells": m.group(5), "wh": m.group(6)}
    want = {(h, c, b) for h in ("48", "72") for c in CASES3 for b in ("TYP", "WAB")}
    if set(out) != want: raise RuntimeFormatError("section 3 carries %d of the %d additions" % (len(set(out) & want), len(want)))
    return out


def hf_listening(text):
    s = _section(text, "SENSITIVITY, the QMX receiving", "4. THE MODELLED HISTORICAL COVERAGE")
    flat = " ".join(s.split())
    m = re.findall(r"(48|72) h (NOM|WE) TYP lid (4S\d+\.\d\dP) \(\+(\d+\.\d) cells, \+(\d+\.\d) Wh usable over 4S9P\)", flat)
    out = {(g[0], g[1]): {"lid": g[2], "cells": g[3], "wh": g[4]} for g in m}
    if len(m) != 4 or len(out) != 4: raise RuntimeFormatError("the HF-receiving sensitivity carries %d of 4 lines" % len(m))
    return out


def coverage(text):
    s = _section(text, "4. THE MODELLED HISTORICAL COVERAGE", "MODELLED HISTORICAL COVERAGE: the share")
    rx = re.compile(r"^\s+(48|72) h (%s)\s+both kept \(4S9P lid\):\s+(\d+) \(\s*[\d.]+ %%\) /\s+(\d+) \(\s*[\d.]+ %%\) /\s+(\d+) "
                    r"\(\s*[\d.]+ %%\)$" % "|".join(CASES2), re.M)
    out = {(m.group(1), m.group(2)): (m.group(3), m.group(4), m.group(5)) for m in rx.finditer(s)}
    if len(out) != 10: raise RuntimeFormatError("section 4 carries %d of 10 coverage lines" % len(out))
    return out


def reproduced(text):
    a = re.findall(r"^0\. REPRODUCTION: [^\n]*\n\s+(yes|no)$", text, re.M)
    b = re.findall(r"^\s+Reproduction: 72 h, [^\n]*: (yes|no)$", text, re.M)
    return a == ["yes"] and b == ["yes"]


def read_all(text):
    return {"battery_only": battery_only(text), "store_start": store_start(text), "solar": solar(text),
            "upgrade": upgrade(text), "hf_listening": hf_listening(text), "coverage": coverage(text),
            "reproduced": reproduced(text)}


def main(argv):
    path = argv[0] if argv else "v2/docs/records/l3batt/runtime.out"
    try:
        got = read_all(open(path, encoding="utf-8").read())
    except RuntimeFormatError as e:
        print("runtime_reader: REFUSED: %s" % e)
        return 2
    print(json.dumps({k: ({" ".join(kk) if isinstance(kk, tuple) else kk: vv for kk, vv in v.items()} if isinstance(v, dict) else v)
                      for k, v in got.items()}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
