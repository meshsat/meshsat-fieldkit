#!/usr/bin/env python3
"""Read the deliverable back (MESHSAT-862, 8 Sep 2026; appendix 27.2 listed these properties on 3 Sep and no gate read them until now).
Asserts: every item of the deliverable folder is present and non-empty; the gerber zip carries one copper gerber per copper layer of the
board (F_Cu .gtl, In<k>_Cu .g<k>, B_Cu .gbl), the mask, paste, silk and edge layers, the Excellon drill file and its map; the JLC BOM is in
the JLC form and every designator in it is in the CPL (bench-fitted parts excepted by prefix); the CPL has only Top and Bottom in its side
column and no `?` designator; the DRC report exists. Prints one line per property with its count and the denominator.

Usage: verify_deliverable.py <deliverable dir> <name> <copper layers> [--bench-prefixes H,S_,TP,J_,U_MOD]   -> exit 1 on any FAIL."""
import sys, os, csv, zipfile, re

ITEMS = ["%s-gerbers.zip", "%s-bom.csv", "%s-cpl.csv", "README-fab.txt", "%s-drc.rpt", "%s-schematic.pdf", "%s-render-top.png", "%s-render-bottom.png",
         "%s-1to1-top.pdf", "%s-1to1-bottom-mirrored.pdf", "%s.kicad_pcb", "%s.kicad_sch", "%s.kicad_pro", "%s-bom.status", "meshsat.pretty"]

def check_dir(D, name, ncu, bench=("H", "S_", "TP")):
    fails, lines = [], []
    def ok(cond, text):
        lines.append(("PASS  " if cond else "FAIL  ") + text)
        if not cond: fails.append(text)
    for it in ITEMS:
        p = os.path.join(D, it % name if "%s" in it else it)
        ok(os.path.exists(p) and (os.path.isdir(p) or os.path.getsize(p) > 0), "deliverable item %s present and non-empty" % os.path.basename(p))
    z = os.path.join(D, "%s-gerbers.zip" % name)
    if os.path.exists(z):
        try: names = zipfile.ZipFile(z).namelist()
        except zipfile.BadZipFile: names = []; ok(False, "gerber zip readable")
        cu = [n for n in names if re.search(r"-(F_Cu\.gtl|B_Cu\.gbl|In\d+_Cu\.g\d+)$", n)]
        ok(len(cu) == ncu, "gerber zip carries %d of %d copper layers (%s)" % (len(cu), ncu, ", ".join(sorted(re.sub(r".*-", "", n) for n in cu))))
        for tag in ("F_Mask.gts", "B_Mask.gbs", "F_Paste.gtp", "B_Paste.gbp", "F_Silkscreen.gto", "B_Silkscreen.gbo", "Edge_Cuts.gm1"):
            ok(any(n.endswith(tag) for n in names), "gerber zip carries %s" % tag)
        ok(any(n.endswith(".drl") for n in names), "gerber zip carries the Excellon drill file")
        ok(any(n.endswith("drl_map.gbr") for n in names), "gerber zip carries the drill map")
    bom = os.path.join(D, "%s-bom.csv" % name); cpl = os.path.join(D, "%s-cpl.csv" % name); cpl_refs = set()
    if os.path.exists(cpl):
        rows = list(csv.DictReader(open(cpl)))
        ok(rows and list(rows[0].keys())[:5] == ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"], "CPL in the JLC form (Designator, Mid X, Mid Y, Layer, Rotation)")
        sides = {r.get("Layer", "") for r in rows}
        ok(sides <= {"Top", "Bottom"}, "CPL side column only Top or Bottom (%s)" % sorted(sides))
        ok(all(r.get("Mid X", "").endswith("mm") and r.get("Mid Y", "").endswith("mm") for r in rows), "CPL positions in mm (drill-file origin)")
        cpl_refs = {r["Designator"] for r in rows}
        ok(not any("?" in r for r in cpl_refs), "no '?' designator in the CPL")
    if os.path.exists(bom):
        rows = list(csv.DictReader(open(bom)))
        ok(rows and list(rows[0].keys())[:4] == ["Comment", "Designator", "Footprint", "LCSC Part #"], "BOM in the JLC form (Comment, Designator, Footprint, LCSC Part #)")
        refs = []
        for r in rows:
            for x in r.get("Designator", "").split(","):
                x = x.strip(); m = re.match(r"^([A-Za-z_]+)(\d+)-\1?(\d+)$", x)   # a range in an older deliverable is expanded for the CPL comparison; the form itself is judged below
                refs += ["%s%d" % (m.group(1), k) for k in range(int(m.group(2)), int(m.group(3)) + 1)] if m else ([x] if x else [])
        ok(not any(re.match(r"^[A-Za-z_]+\d+-", x) for r in rows for x in r.get("Designator", "").split(",")), "BOM designators listed one by one, no ranges")
        ok(not any("?" in r for r in refs), "no '?' designator in the BOM")
        if cpl_refs:
            missing = [r for r in refs if r not in cpl_refs and not r.startswith(bench)]
            ok(not missing, "every BOM designator is in the CPL (%d of %d; missing %s)" % (len(refs) - len(missing), len(refs), missing[:8]))
        blank = [r for r in rows if not r.get("LCSC Part #")]
        lines.append("INFO  BOM lines without an LCSC code: %d of %d (%s)" % (len(blank), len(rows), ", ".join(r.get("Designator", "")[:20] for r in blank[:6])))
    return fails, lines

def main(a):
    if len(a) < 3: print(__doc__); return 2
    bench = tuple(a[a.index("--bench-prefixes") + 1].split(",")) if "--bench-prefixes" in a else ("H", "S_", "TP")
    fails, lines = check_dir(a[0], a[1], int(a[2]), bench)
    for l in lines: print("verify_deliverable: " + l)
    print("verify_deliverable: %s (%d of %d properties)" % ("ALL PASS" if not fails else "%d FAIL" % len(fails), len(lines) - len(fails) - sum(1 for l in lines if l.startswith("INFO")), len(lines) - sum(1 for l in lines if l.startswith("INFO"))))
    return 1 if fails else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
