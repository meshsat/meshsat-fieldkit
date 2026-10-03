#!/usr/bin/env python3
"""A per-board bill of materials read from a committed KiCad netlist (MESHSAT-1357, the supplier handover of 3 October 2026).

The project commits each board's schematic and netlist, not a BOM file; a supplier quoting the work needs one per board. This
reads the netlist's `(comp ...)` blocks (reference, value, footprint, the LCSC field when present), groups identical lines and
writes a CSV whose first line names the netlist, its sha256 and the commit. It is a READING of the netlist, NOT_FOR_FAB: the
circuit changes the Layer 4 and Layer 8 records draft are not applied to the committed schematics, so they are not in it; a
part without an LCSC field is listed with the field empty, never guessed.

Usage: bom_from_netlist.py <netlist> <commit> <out.csv>"""
import csv, hashlib, re, sys

COMP = re.compile(r'\(comp \(ref "([^"]+)"\)(.*?)(?=\n\s*\(comp \(ref |\n\s*\)\s*\n\s*\(libparts|\Z)', re.S)
VALUE = re.compile(r'\(value "((?:[^"\\]|\\.)*)"\)')
FOOT = re.compile(r'\(footprint "((?:[^"\\]|\\.)*)"\)')
LCSC = re.compile(r'\(field \(name "LCSC"\) "([^"]*)"\)')


def parts(text):
    out = []
    for m in COMP.finditer(text):
        ref, body = m.group(1), m.group(2)
        v, f, c = VALUE.search(body), FOOT.search(body), LCSC.search(body)
        out.append((ref, v.group(1) if v else "", f.group(1) if f else "", c.group(1) if c else ""))
    return out


def natural(ref):
    m = re.match(r"([A-Za-z_]+)(\d+)(.*)", ref)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (ref, 0, "")


def main(net, commit, out):
    raw = open(net, "rb").read()
    rows = parts(raw.decode("utf-8"))
    if not rows:
        sys.exit("bom_from_netlist: no (comp ...) block read in %s; refusing to write an empty BOM" % net)
    groups = {}
    for ref, val, fp, lcsc in rows:
        groups.setdefault((val, fp, lcsc), []).append(ref)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        fh.write("# NOT_FOR_FAB. Read from %s (sha256 %s) at commit %s by bom_from_netlist.py; the drafted circuit changes are "
                 "NOT applied; %d references in %d lines\n" % (net, hashlib.sha256(raw).hexdigest(), commit, len(rows), len(groups)))
        w = csv.writer(fh)
        w.writerow(["quantity", "references", "value", "footprint", "lcsc"])
        for (val, fp, lcsc), refs in sorted(groups.items(), key=lambda kv: natural(sorted(kv[1], key=natural)[0])):
            refs = sorted(refs, key=natural)
            w.writerow([len(refs), " ".join(refs), val, fp, lcsc])
    print("bom_from_netlist: %s, %d references in %d lines, %d without an LCSC field" %
          (out, len(rows), len(groups), sum(1 for r in rows if not r[3])))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
