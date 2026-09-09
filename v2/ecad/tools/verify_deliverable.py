#!/usr/bin/env python3
"""Read the deliverable back (MESHSAT-862, 8 Sep 2026; appendix 27.2 listed these properties on 3 Sep and no gate read them until now).
Asserts: every item of the deliverable folder is present and non-empty; the gerber zip carries one copper gerber per copper layer of the
board (F_Cu .gtl, In<k>_Cu .g<k>, B_Cu .gbl), the mask, paste, silk and edge layers, the Excellon drill file and its map; the JLC BOM is in
the JLC form and every designator in it is in the CPL (bench-fitted parts excepted by prefix: H mounting, S_ shield, TP test point,
W_ solder wire land, JP solder jumper, none of which JLC places); the CPL has only Top and Bottom in its side
column and no `?` designator; the DRC report exists. Prints one line per property with its count and the denominator.

Usage: verify_deliverable.py <deliverable dir> <name> <copper layers> [--bench-prefixes H,S_,TP] [--bare]   -> exit 1 on any FAIL."""
import sys, os, csv, zipfile, re

ITEMS = ["%s-gerbers.zip", "%s-bom.csv", "%s-cpl.csv", "README-fab.txt", "%s-drc.rpt", "%s-schematic.pdf", "%s-render-top.png", "%s-render-bottom.png",
         "%s-1to1-top.pdf", "%s-1to1-bottom-mirrored.pdf", "%s.kicad_pcb", "%s.kicad_sch", "%s.kicad_pro", "%s-bom.status", "meshsat.pretty"]

BARE_SKIP = ("%s-bom.csv", "%s-cpl.csv", "README-fab.txt", "%s-schematic.pdf", "%s.kicad_sch", "%s-bom.status")   # a bare board (E5) has no schematic, BOM or CPL

def check_dir(D, name, ncu, bench=("H", "S_", "TP", "W_", "JP"), bare=False):
    fails, lines = [], []
    def ok(cond, text):
        lines.append(("PASS  " if cond else "FAIL  ") + text)
        if not cond: fails.append(text)
    for it in ITEMS:
        if bare and it in BARE_SKIP: continue
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
    if os.path.exists(cpl) and not bare:
        rows = list(csv.DictReader(open(cpl)))
        ok(rows and list(rows[0].keys())[:5] == ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"], "CPL in the JLC form (Designator, Mid X, Mid Y, Layer, Rotation)")
        sides = {r.get("Layer", "") for r in rows}
        ok(sides <= {"Top", "Bottom"}, "CPL side column only Top or Bottom (%s)" % sorted(sides))
        ok(all(r.get("Mid X", "").endswith("mm") and r.get("Mid Y", "").endswith("mm") for r in rows), "CPL positions in mm (drill-file origin)")
        cpl_refs = {r["Designator"] for r in rows}
        ok(not any("?" in r for r in cpl_refs), "no '?' designator in the CPL")
    if os.path.exists(bom) and not bare:
        rows = list(csv.DictReader(open(bom)))
        ok(rows and list(rows[0].keys())[:4] == ["Comment", "Designator", "Footprint", "LCSC Part #"], "BOM in the JLC form (Comment, Designator, Footprint, LCSC Part #)")
        # No code this project has already proved wrong at JLCPCB (tools/lcsc-blocked.txt). A finish re-exports the BOM from the board file it
        # already has and never re-runs the schematic generator, so a code corrected in a generator does not reach a deliverable until that
        # board is regenerated: on 9 September 2026 a red team found all 23 of the codes corrected on 8 September still in five shipped
        # deliverable BOMs, among them a PCA9555 that is a 74HC245PW and a BAT54 that is an LED. This is the gate that was missing.
        _bl = {}
        _blf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lcsc-blocked.txt")
        if os.path.exists(_blf):
            for _ln in open(_blf):
                if _ln.startswith("#") or not _ln.strip(): continue
                _f = _ln.split()
                if len(_f) >= 2: _bl[_f[0]] = " ".join(_f[1:])
        _hit = sorted({(r.get("LCSC Part #") or "").strip() for r in rows if (r.get("LCSC Part #") or "").strip() in _bl})
        ok(not _hit, "no LCSC code the record has proved wrong (%s)" % (", ".join("%s: %s" % (h, _bl[h]) for h in _hit) if _hit else "none of %d blocked codes" % len(_bl)))
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
    # the silk names this deliverable's phase and no other (8 Sep 2026: every placement generator hard-coded the PREVIOUS phase, so the
    # released P2 carries "REV A (P1)" on its underside and D9 would have shipped stamped D8; the deliverable folder name is the authority)
    ph = os.path.basename(D.rstrip("/")).rsplit("-", 1)[-1]
    if re.fullmatch(r"[A-Z][A-Z]?\d\d?", ph or ""):
        bf = os.path.join(D, name + ".kicad_pcb")
        if os.path.exists(bf):
            texts = re.findall(r'\(gr_text\s+"([^"]*)"', open(bf, errors="replace").read())
            here = {t for txt in texts for t in re.findall(r"\b" + re.escape(ph[0]) + r"\d\d?\b", txt)}
            ok(ph in here, "the silk names the phase %s (found %s in %d legend texts)" % (ph, ", ".join(sorted(here)) or "no phase token", len(texts)))
            ok(not (here - {ph}), "no other phase of this board on the silk (stale: %s)" % ", ".join(sorted(here - {ph})))
    return fails, lines

def main(a):
    if len(a) < 3: print(__doc__); return 2
    bench = tuple(a[a.index("--bench-prefixes") + 1].split(",")) if "--bench-prefixes" in a else ("H", "S_", "TP", "W_", "JP")
    fails, lines = check_dir(a[0], a[1], int(a[2]), bench, "--bare" in a)
    for l in lines: print("verify_deliverable: " + l)
    print("verify_deliverable: %s (%d of %d properties)" % ("ALL PASS" if not fails else "%d FAIL" % len(fails), len(lines) - len(fails) - sum(1 for l in lines if l.startswith("INFO")), len(lines) - sum(1 for l in lines if l.startswith("INFO"))))
    return 1 if fails else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
