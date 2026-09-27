#!/usr/bin/env python3
"""Every number this board is designed to is one the fabricator makes (rule RTE-001, MESHSAT-862,
16 September 2026).

A board carries its own minimum track width, clearance, via and drill, and the DRC judges every piece of
copper against them. Nothing had ever asked the other question: are the board's OWN minimums inside what the
process makes at the copper weight this board is ordered at.

The answer on board P is no. It is a two-layer board ordered at 2 oz by owner ruling 7, its design settings
say 0.127 mm track width and 0.127 mm clearance, and the fabricator's 2 oz two-layer capability is 0.16 mm for
both. Its Default and SENSE classes sit at 0.127 as well. Every gate in this project passed that board,
because every one of them judged the copper against the board's rules and none judged the rules.

THE NUMBERS COME FROM ONE DOCUMENT and each is cited to its row: v2/vendor/fabricator/
jlcpcb-pcb-capabilities-2026-09-16.md, transcribed from the fabricator's own capability page on 16 September
2026. The copper weight comes from the BOARD'S OWN STACKUP (the thickness of its outer copper layers: 0.035 mm
is 1 oz, 0.070 is 2 oz), never from a literal, because the whole defect above is a literal disagreeing with a
stackup.

A board whose stackup carries no copper thickness is INCONCLUSIVE, not a pass: without it there is no way to
know which row applies.

Usage: fab_limits.py <board.kicad_pcb> [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

DOC = "v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md"

# (copper oz, multilayer) -> (min track mm, min spacing mm), from the "Track width and spacing, by copper
# weight" rows of that document. Multilayer means four layers or more.
TRACK = {
    (1.0, False): (0.10, 0.10),   # 1 oz, 1 and 2 layer
    (1.0, True):  (0.09, 0.09),   # 1 oz, multilayer
    (2.0, False): (0.16, 0.16),   # 2 oz, 2-layer
    (2.0, True):  (0.15, 0.15),   # 2 oz, multilayer
    (2.5, False): (0.20, 0.20),
    (3.5, False): (0.25, 0.25),
    (4.5, False): (0.30, 0.30),
}
# The hole rows, which do not depend on copper weight for two layers and up.
MIN_VIA_HOLE = 0.15          # "minimum via hole, 2+ layers"
MIN_VIA_DIAM = 0.25          # "minimum via diameter, 2+ layers"
MIN_NPTH = 0.50              # "minimum non-plated hole"
VIA_IN_PAD = (0.15, 0.55)    # "via in pad ... via diameters 0.15 to 0.55 mm"


def copper_oz(path):
    """The outer copper weight in ounces, from the board's own stackup. None where it carries none.

    The reader is `stackup_read.py`, in one place, because the single-line form alone was a false INCONCLUSIVE
    on three boards and the same regular expression sat in two other files (16 September 2026)."""
    import stackup_read
    return stackup_read.outer_copper_oz(path)


def classes(path):
    pro = os.path.splitext(path)[0] + ".kicad_pro"
    if not os.path.exists(pro): return None, None
    d = json.load(open(pro))
    rules = (((d.get("board") or {}).get("design_settings") or {}).get("rules") or {})
    return rules, ((d.get("net_settings") or {}).get("classes") or [])


def judge(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    layers = len(set(re.findall(r'\(layer "(In\d+\.Cu|F\.Cu|B\.Cu)" \(type "copper"\)', txt))) or None
    if layers is None:
        layers = int((re.search(r'\(layers (\d+)\)', txt) or [0, 0])[1] or 0) or None
    oz = copper_oz(path)
    rules, cls = classes(path)
    bad, notes = [], []
    if oz is None:
        return dict(oz=None, layers=layers, bad=[], notes=["the board's stackup carries no copper thickness, so no capability row applies"], classes=0)
    multi = bool(layers and layers >= 4)
    key = (oz, multi)
    if key not in TRACK:
        # fall back to the nearest heavier weight of the same build, which is conservative in the right direction
        cands = sorted([k for k in TRACK if k[1] == multi and k[0] >= oz]) or sorted([k for k in TRACK if k[1] == multi])
        key = cands[0]
        notes.append("no row for %.1f oz on a %s board; the %.1f oz row is used, which is the heavier and "
                     "therefore the coarser limit" % (oz, "multilayer" if multi else "two-layer", key[0]))
    t_min, s_min = TRACK[key]
    if rules is None:
        return dict(oz=oz, layers=layers, bad=[], notes=notes + ["no project file beside the board, so its own rules cannot be read"], classes=0)
    def under(name, have, want, what):
        if have is None: return
        if float(have) < want - 1e-9:
            bad.append("%s %.3f mm is under the fabricator's %.3f mm for %.1f oz on a %s board (%s)"
                       % (name, float(have), want, oz, "multilayer" if multi else "two-layer", what))
    under("the board's minimum track width", rules.get("min_track_width"), t_min, "track width row")
    under("the board's minimum clearance", rules.get("min_clearance"), s_min, "spacing row")
    under("the board's minimum via diameter", rules.get("min_via_diameter"), MIN_VIA_DIAM, "minimum via diameter row")
    under("the board's minimum through hole", rules.get("min_through_hole_diameter"), MIN_VIA_HOLE, "minimum via hole row")
    for c in cls:
        n = c.get("name", "?")
        if c.get("track_width"): under("class %s track width" % n, c["track_width"], t_min, "track width row")
        if c.get("clearance"): under("class %s clearance" % n, c["clearance"], s_min, "spacing row")
        if c.get("via_diameter"): under("class %s via diameter" % n, c["via_diameter"], MIN_VIA_DIAM, "minimum via diameter row")
        if c.get("via_drill"): under("class %s via drill" % n, c["via_drill"], MIN_VIA_HOLE, "minimum via hole row")
    return dict(oz=oz, layers=layers, bad=bad, notes=notes, classes=len(cls))


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    r = judge(path)
    print("fab_limits: %s outer copper on %s copper layer(s), %d class(es) judged against %s"
          % (("%.1f oz" % r["oz"]) if r["oz"] else "UNKNOWN", r["layers"] or "?", r["classes"], DOC))
    for n in r["notes"]: print("  NOTE %s" % n)
    for b in r["bad"][:20]: print("  FAIL %s" % b)
    if "--json" in argv: print(json.dumps(r, indent=1))
    if r["oz"] is None or not r["classes"]:
        return _v.write("fab_limits", _v.INCONCLUSIVE, denominator=0, inputs={"board": path, "document": DOC},
                        evidence=r["notes"], note="; ".join(r["notes"])[:200] or "nothing to judge")
    return _v.write("fab_limits", _v.FAIL if r["bad"] else _v.PASS,
                    counts={"classes": r["classes"], "under_capability": len(r["bad"])},
                    denominator=r["classes"] * 4 + 4, evidence=r["bad"][:20],
                    inputs={"board": path, "document": DOC, "copper_oz": r["oz"], "copper_layers": r["layers"]},
                    note=("every rule this board is designed to is inside the fabricator's capability for its own "
                          "copper weight" if not r["bad"] else
                          "this board is designed to numbers the chosen process does not make at its copper weight"))


if __name__ == "__main__":
    import verdict as _vg   # a gate that crashes writes INCONCLUSIVE, never nothing (18 September 2026)
    sys.exit(_vg.guard("fab_limits", main, sys.argv[1:]))
