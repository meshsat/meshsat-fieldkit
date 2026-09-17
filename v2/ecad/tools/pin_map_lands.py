#!/usr/bin/env python3
"""Rule SCH-005 on a COMMITTED netlist: every pad of every part's land carries a net or a declared no-connect.

The engine (kisch.check_land) stops a NEW generation that gets this wrong. This judges the netlist a board was
cut from, so a board whose generator has since been corrected still reads as what it is: board E11's Q7 is a
PowerPAK SO-8 whose gate and drain nets sit on two SOURCE pins with the drain tab floating, and that netlist
says so whatever gen_sch_e.py says today (17 September 2026).

A no-connect written "NC" never reaches the netlist, so a pad that carries no node is either a deliberate NC or
a forgotten one and the netlist alone cannot tell them apart. What it CAN tell is the shape of the defect this
rule exists for: a part whose map names FEWER distinct pads than the land has AND whose missing pads include the
land's largest, or any part with a net on a pin the land does not carry and nowhere else. The first is the
PowerPAK case (the tab, pad 5, floating); the second is a net that never reaches the part.

Usage: pin_map_lands.py <netlist.net> <letter> [--lib-dir DIR ...]
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict, kisch
from netlist_board import read_netlist


def read_footprints(path):
    """{ref: footprint id} from the components section."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r'\(comp \(ref "([^"]+)"\)(.*?)(?=\n    \(comp |\n  \)\n)', txt, re.S):
        f = re.search(r'\(footprint "([^"]*)"\)', m.group(2))
        if f: out[m.group(1)] = f.group(1)
    return out


def land_geometry(fpid):
    """{pad number: area mm2} for the land, largest pad included, or None when it cannot be read."""
    pads = kisch.land_pads(fpid)
    if pads is None: return None
    # the largest pad by number: re-read the text for sizes (kisch keeps only the numbers)
    for d in kisch._fp_dirs():
        lib, name = fpid.split(":", 1)
        cand = os.path.join(d, name + ".kicad_mod") if d.endswith(lib + ".pretty") else os.path.join(d, lib + ".pretty", name + ".kicad_mod")
        if not os.path.exists(cand): continue
        txt = open(cand, errors="replace").read()
        area = {}
        for m in re.finditer(r'\(pad\s+"([^"]*)"\s+\S+\s+\S+.*?\(size ([\d.]+) ([\d.]+)\)', txt, re.S):
            if m.group(1) in pads:
                area[m.group(1)] = max(area.get(m.group(1), 0.0), float(m.group(2)) * float(m.group(3)))
        return area
    return {p: 0.0 for p in pads}


def main(a):
    if len(a) < 2: print(__doc__); return verdict.USAGE
    net_path, letter = a[0], a[1]
    for i, x in enumerate(a):
        if x == "--lib-dir" and i + 1 < len(a): os.environ["KISCH_FP_DIRS"] = a[i + 1]
    if not os.path.exists(net_path):
        return verdict.write("pin_map_lands_" + letter, verdict.INCONCLUSIVE, denominator=0, rules=["SCH-005"],
                             missing_input="no netlist at %s" % net_path)
    nl = read_netlist(net_path); fps = read_footprints(net_path)
    fails, judged, unread, phantom = [], 0, [], 0
    for ref, fpid in sorted(fps.items()):
        if not fpid or ":" not in fpid: continue
        geo = land_geometry(fpid)
        if geo is None: unread.append(fpid); continue
        judged += 1
        # KiCad gives every unconnected symbol pin a placeholder net named unconnected-(...); it is not a net the
        # design carries and a symbol pin without a pad is the shape the engine now refuses at generation.
        pins = {k: v for k, v in nl.get(ref, {}).items() if not v.startswith("unconnected-")}
        missing = sorted(p for p in geo if p not in pins)
        ghosts = {k: v for k, v in pins.items() if k not in geo}
        for k, v in ghosts.items():
            if not any(vv == v for kk, vv in pins.items() if kk in geo):
                fails.append("%s pin %s carries %s and the land %s has no pad %s, so the net never reaches the part" % (ref, k, v, fpid, k))
            else: phantom += 1
        # THE TAB RULE IS FOR A POWER PART, NOT A CONNECTOR. A connector's shield or retention tab with no node is a
        # choice (board B's JST-SH fan headers, its six M.2 sockets); an IC's or a transistor's tab with no node is
        # the defect, and a tab is a pad at least twice the land's median pad, so a SOT-23-5 whose pads are all
        # one size has none.
        if missing and geo and ref[:1] in ("U", "Q"):
            areas = sorted(geo.values()); median = areas[len(areas) // 2]
            biggest = max(geo, key=geo.get)
            if biggest in missing and len(pins) < len(geo) and geo[biggest] >= 2.0 * median:
                fails.append("%s on %s: pad%s %s carr%s no node and pad %s is the land's largest (%.2f mm2), the tab of a power part"
                             % (ref, fpid, "" if len(missing) == 1 else "s", ", ".join(missing), "ies" if len(missing) == 1 else "y",
                                biggest, geo[biggest]))
    for f in fails: print("pin_map_lands: FAIL " + f)
    print("pin_map_lands: board %s: %d part(s) judged against their land, %d failure(s), %d pin(s) on a merged pad, %d land(s) unreadable"
          % (letter.upper(), judged, len(fails), phantom, len(unread)))
    if unread and not fails:
        return verdict.write("pin_map_lands_" + letter, verdict.INCONCLUSIVE, {"judged": judged, "unreadable": len(unread)},
                             denominator=judged + len(unread), rules=["SCH-005"], inputs={"netlist": net_path},
                             missing_input="%d land(s) could not be read: %s" % (len(unread), ", ".join(sorted(set(unread))[:6])))
    return verdict.write("pin_map_lands_" + letter, verdict.FAIL if fails else verdict.PASS,
                         {"judged": judged, "failures": len(fails), "merged_pad_pins": phantom, "unreadable": len(unread)},
                         denominator=judged, evidence=fails[:20], rules=["SCH-005"], inputs={"netlist": net_path},
                         note=("every part's map names every pad of its land" if not fails else
                               "%d part(s) whose map leaves the land's tab floating or puts a net on no pad at all" % len(fails)))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
