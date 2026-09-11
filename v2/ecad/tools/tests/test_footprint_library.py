#!/usr/bin/env python3
"""Every footprint this tree names in its own library is IN its own library.

12 September 2026 (MESHSAT-862). The narrow-pad IDC headers were generated on the rented box, used by four
boards for a day, and never committed or declared: `git archive` of origin/main plus A's own chain stopped at
"footprint missing: meshsat:IDC-Header_2x13_P2.54mm_Vertical_NarrowPad", so the tree on origin could not build
the board its generators describe. It is the footprint version of the lesson of 10 September, when four routed
boards were lost with a destroyed box: an artefact that exists only on a rented machine exists nowhere.

Two rules, and the first fails on the tree of an hour ago:
  every `meshsat:NAME` a generator names has NAME.kicad_mod in `v2/ecad/meshsat.pretty`;
  a board whose generators name a footprint one of the footprint generators writes DECLARES that generator in
  `tools/boards/<letter>.json`, so the library can be rebuilt from the tree rather than from a box's history."""
import json, os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETTY = os.path.join(os.path.dirname(TOOLS), "meshsat.pretty")
sys.path.insert(0, TOOLS)


def _generators():
    return sorted(f for f in os.listdir(TOOLS) if re.match(r"gen_(sch|pcb)_\w+\.py$", f))


def _named(src):
    """Every meshsat: footprint a source names, literals plus the two IDC lands `idc()` can return."""
    s = open(os.path.join(TOOLS, src), errors="replace").read()
    out = set(re.findall(r'"meshsat:([A-Za-z0-9_.\-]+)"', s))
    for rows in re.findall(r'idc\("(2x\d\d)"\)', s):
        out.add("IDC-Header_%s_P2.54mm_Vertical_NarrowPad" % rows)
    return out


def t_every_named_footprint_is_in_the_library():
    missing = {}
    for g in _generators():
        for name in sorted(_named(g)):
            if not os.path.exists(os.path.join(PRETTY, name + ".kicad_mod")): missing.setdefault(name, []).append(g)
    assert not missing, "named but not in meshsat.pretty:\n  " + "\n  ".join("%s (%s)" % (k, ", ".join(v)) for k, v in sorted(missing.items()))


def t_a_board_declares_the_generator_that_writes_its_footprints():
    """The library file being there is not enough: it has to be rebuildable, or the next change to a land
    pattern is another hand-run on a machine that gets destroyed."""
    writers = {}   # footprint name -> the generator that writes it
    for g in sorted(f for f in os.listdir(TOOLS) if f.startswith("gen_footprints_")):
        s = open(os.path.join(TOOLS, g), errors="replace").read()
        for n in re.findall(r'"([A-Za-z0-9_.\-]*IDC-Header[A-Za-z0-9_.\-]*)"', s) + re.findall(r'_NarrowPad', s):
            writers[n] = g
        if "NarrowPad" in s: writers["NarrowPad"] = g
    bad = []
    for L in "abcdep":
        cfg = os.path.join(TOOLS, "boards", "%s.json" % L)
        if not os.path.exists(cfg): continue
        declared = json.load(open(cfg)).get("footprint_generator") or []
        if isinstance(declared, str): declared = [declared]
        names = set()
        for g in ("gen_sch_%s.py" % L, "gen_pcb_%s.py" % L, "gen_pcb_%s3.py" % L):
            if os.path.exists(os.path.join(TOOLS, g)): names |= _named(g)
        if any("NarrowPad" in n for n in names) and writers.get("NarrowPad") not in declared:
            bad.append("board %s names a narrow-pad land and declares %s" % (L, declared or "no footprint generator"))
    assert not bad, "\n  ".join(bad)
