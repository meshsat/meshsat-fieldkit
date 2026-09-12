#!/usr/bin/env python3
"""Bring a ROUTED board's part values and LCSC codes up to date with its schematic, without touching copper.

MESHSAT-862, 12 September 2026. Owner ruling 10 replaced twenty-five `22u 50V X7R 1210` capacitors on board A
with a part that exists, in the same land, and ruled "no layout change and no re-route". A finish re-exports
the BOM from the BOARD, never from the schematic (appendix 32.72: that is how 49 wrong codes survived a
correction pass), so a value corrected in a generator does not reach a deliverable until the board is
regenerated, which on A means hours of routing for a text change.

This is the post-route text swap of section 8 made into a tool: it reads the netlist the schematic generator
just wrote and writes each reference's VALUE and LCSC field onto the routed board. It touches no pad, no
track, no via and no zone, and it refuses a reference the board does not carry rather than inventing one.

Usage: apply_netlist_values.py <board.kicad_pcb> <netlist.net> [--dry]
"""
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict


def netlist_parts(path):
    """{ref: (value, lcsc)} from a KiCad s-expression netlist."""
    # Each component runs from its own `(comp (ref "X")` to the next one. Closing on an indent was the first
    # try and it matched nothing at all, which is the failure mode a parser must never have: it reported
    # "0 of 0 updated" on a netlist carrying 22 corrected values and looked like a clean run.
    src = open(path, encoding="utf-8", errors="replace").read()
    starts = [(m.start(), m.group(1)) for m in re.finditer(r'\(comp\s+\(ref\s+"([^"]+)"\)', src)]
    out = {}
    for i, (pos, ref) in enumerate(starts):
        body = src[pos:starts[i + 1][0] if i + 1 < len(starts) else len(src)]
        v = re.search(r'\(value\s+"([^"]*)"\)', body)
        lc = re.search(r'\(field\s+\(name\s+"LCSC"\)\s*"([^"]*)"\)', body)
        out[ref] = (v.group(1) if v else "", lc.group(1) if lc else "")
    return out


def main(a):
    if len(a) < 2:
        print(__doc__); return verdict.USAGE
    board_path, net_path = a[0], a[1]
    dry = "--dry" in a
    import pcbnew
    want = netlist_parts(net_path)
    if not want:
        return verdict.write("apply_netlist_values", verdict.INCONCLUSIVE, counts={"netlist_refs": 0},
                             denominator=0, evidence=["the netlist parsed to no components: %s" % net_path],
                             inputs={"board": board_path, "netlist": net_path},
                             note="a netlist with no components says nothing about the board")
    b = pcbnew.LoadBoard(board_path)
    on_board = {f.GetReference(): f for f in b.GetFootprints()}
    changed, missing, evidence = 0, [], []
    for ref, (val, lcsc) in sorted(want.items()):
        f = on_board.get(ref)
        if f is None:
            missing.append(ref); continue
        hits = []
        if val and f.GetValue() != val:
            hits.append("value %r -> %r" % (f.GetValue(), val))
            if not dry: f.SetValue(val)
        if lcsc:
            cur = f.GetFieldByName("LCSC").GetText() if f.HasFieldByName("LCSC") else ""
            if cur != lcsc:
                hits.append("LCSC %r -> %r" % (cur, lcsc))
                if not dry:
                    if f.HasFieldByName("LCSC"): f.GetFieldByName("LCSC").SetText(lcsc)
                    else: f.AddField(pcbnew.PCB_FIELD(f, f.GetFieldCount(), "LCSC")).SetText(lcsc)
        if hits:
            changed += 1
            evidence.append("%s: %s" % (ref, "; ".join(hits)))
    if changed and not dry:
        pcbnew.SaveBoard(board_path, b)
    print("apply_netlist_values: %d of %d reference(s) updated%s%s"
          % (changed, len(want), " (dry run)" if dry else "",
             ", %d in the netlist and not on the board" % len(missing) if missing else ""))
    for e in evidence[:12]:
        print("   " + e)
    if len(evidence) > 12:
        print("   ... %d more" % (len(evidence) - 12))
    # A reference in the netlist that the board does not carry means the two are not the same design, which
    # is exactly what this tool must never paper over.
    v = verdict.FAIL if missing else verdict.PASS
    return verdict.write("apply_netlist_values", v,
                         counts={"updated": changed, "netlist_refs": len(want),
                                 "board_footprints": len(on_board), "missing_on_board": len(missing)},
                         denominator=len(want), evidence=(evidence[:20] + ["not on the board: " + ", ".join(missing[:12])] if missing else evidence[:20]),
                         inputs={"board": board_path, "netlist": net_path},
                         note="the schematic's values and codes on the routed board; no copper touched")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
