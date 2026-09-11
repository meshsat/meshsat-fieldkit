#!/usr/bin/env python3
"""Which files in this tree may produce a fab artefact, pinned (MESHSAT-862, 11 September 2026).

The idea is finops-agora's `agora/validation/execution_paths.py`, about sixty-five lines: a pinned allowlist of the
call sites that may actuate, a scan of the tree, and a gate that fails when the real set differs from the pin. It
exists there because an evidence string claimed a "sole authority" the code did not have. **The analogue here is a pin
on which files may write a gerber, a BOM, a CPL or an order set**, because those are the artefacts that leave this
repository and become money and fibreglass.

What counts as producing one is a short closed list, not a name match: exporting gerbers or a drill file through
`kicad-cli`, writing a `-bom.csv` or `-cpl.csv`, zipping a gerber archive, or writing into `release/<rev>/order/`.
A file that merely READS those names is not an actuator, and the difference is the whole point: `verify_deliverable.py`
opens every gerber zip and `jlc_certify.py` reads every BOM, and neither may ever write one.

A new file that produces one of these fails this gate until a person adds it to PIN with a reason. That is the same
admission rule the gate fixtures use, applied to the surface that reaches the fab.

Usage: execution_paths.py [--list]    exit 0 the real set matches the pin, 1 it does not, 3 the tree could not be read
"""
import os, re, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

TOOLS = os.path.dirname(os.path.abspath(__file__))

# The pin. Every entry is a file that MAY produce a fab artefact, with what it produces and why it is allowed to.
PIN = {
    "build_pcb.sh":     "exports the gerbers and the drill files of a board through kicad-cli; the deliverable's copper",
    "build_e2.sh":      "the same for E2, the retired RF junction strip, kept so its deliverable can be rebuilt",
    "build_e5.sh":      "the same for E5, the dock block, a bare board with no assembly",
    "export_jlc.sh":    "writes the JLC BOM and CPL from a board file, and the fab README beside them",
    "finish_board.sh":  "the deliverable writer: calls build_pcb and export_jlc, gates the result and stages the folder",
    "make_handoff.py":  "builds release/<rev>/order/ and review/ from the deliverable folders; the order set itself",
    "lcsc_fill.py":     "rewrites the BOM in place to fill and check its LCSC codes; the only writer of a code into a BOM",
    "jlc_certify.py":   "writes release/revA/order/JLC-CERTIFIED.tsv, its own verdict table; it reads every BOM and writes none",
}

# Producing a fab artefact, as a closed list of the things that actually produce one.
SIGNS = [
    (re.compile(r"kicad-cli\s+pcb\s+export\s+(gerbers|drill)"), "exports gerbers or drill through kicad-cli"),
    (re.compile(r"\bzip\b[^\n]*gerbers\.zip"), "zips a gerber archive"),
    (re.compile(r">\s*[^\s|;&]*-(bom|cpl)\.csv"), "redirects into a BOM or CPL"),
    (re.compile(r"open\(\s*[^)]*-(bom|cpl)\.csv[^)]*,\s*[\"']w"), "opens a BOM or CPL for writing"),
    (re.compile(r"open\(\s*(?:path|bom|cpl|out|dst|p)\s*,\s*[\"']w[\"']"), "opens a path variable for writing"),
    (re.compile(r"(shutil\.copy\w*|os\.replace)\([^)]*\border\b"), "copies into the order set"),
    (re.compile(r"RELEASE=|\$RELEASE/|release/\$\{MESHSAT_FK_REV"), "stages a folder into the release tree"),
    (re.compile(r"csv\.(DictWriter|writer)\("), "writes a CSV"),
]

# A file may name these artefacts without producing one. Reading is not actuating, and saying so here is what keeps
# the pin honest rather than merely short.
READERS = {
    "verify_deliverable.py": "opens every gerber zip and both CSVs to read the deliverable back; writes none of them",
    "routeflow.py":          "names the deliverable folder to judge a finish; writes no artefact in it",
    "build_sch.sh":          "exports the schematic and the netlist, which are not fab artefacts",
    "kb/kb_inventory.py":    "writes its own inventory CSV, which is a report about documents",
}


def producers(root=TOOLS):
    """Every file under the tools tree with write-shaped evidence of producing a fab artefact."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "bench", "experiments", "cloud")]
        for fn in sorted(filenames):
            if not fn.endswith((".py", ".sh")): continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            if rel.startswith("tests" + os.sep): continue        # a fixture builds a fake deliverable on purpose
            # The scanner carries every pattern it looks for, so it matches itself. That is the same self-match the
            # record already pays for with `pkill -f`, and the fix is the same: keep the rule out of its own scan.
            if rel == os.path.basename(__file__): continue
            try: src = open(os.path.join(dirpath, fn), errors="replace").read()
            except Exception: continue
            why = []
            for pat, what in SIGNS:
                for line in src.splitlines():
                    t = line.strip()
                    if t.startswith("#") or t.startswith("//"): continue
                    if pat.search(t):
                        # a CSV writer only counts when the file is about a BOM, a CPL or the order set
                        if what == "writes a CSV" and not re.search(r"-(bom|cpl)\.csv|\border\b", src): break
                        if what == "opens a path variable for writing" and not re.search(r"-(bom|cpl)\.csv", src): break
                        why.append(what); break
            if why: found[rel] = sorted(set(why))
    return found


def main(a):
    try: found = producers()
    except Exception as e:
        print("execution_paths: could not scan the tree (%s)" % e)
        return verdict.write("execution_paths", verdict.INCONCLUSIVE, denominator=0, note=str(e))
    if "--list" in a:
        for f, why in sorted(found.items()): print("  %-24s %s" % (f, "; ".join(why)))
    unpinned = sorted(f for f in found if f not in PIN and f not in READERS)
    gone = sorted(f for f in PIN if f not in found)
    for f in unpinned:
        print("execution_paths: FAIL %s produces a fab artefact and is in neither PIN nor READERS (%s)" % (f, "; ".join(found[f])))
    for f in gone:
        print("execution_paths: FAIL %s is pinned as a producer and no longer produces one; remove it from PIN" % f)
    ok = not unpinned and not gone
    print("execution_paths: %d producer(s) found, %d pinned, %d declared readers; %s"
          % (len(found), len(PIN), len(READERS), "the real set matches the pin" if ok else "THE REAL SET DIFFERS FROM THE PIN"))
    return verdict.write("execution_paths", verdict.PASS if ok else verdict.FAIL,
                         counts={"found": len(found), "pinned": len(PIN), "unpinned": len(unpinned), "stale_pin": len(gone)},
                         denominator=len(found), evidence=unpinned + ["%s no longer produces" % f for f in gone],
                         note="a pin on which files may write a gerber, a BOM, a CPL or an order set")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
