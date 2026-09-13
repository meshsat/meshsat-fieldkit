#!/usr/bin/env python3
"""Build the EasyEDA Pro import archives for the CURRENT state of every V2 board (MESHSAT-776, 862).

EasyEDA Pro imports a KiCad project directly (Start Page > Import KiCad), so an archive of the project file,
the schematic, the board, `fp-lib-table` and the footprints IS the interchange format: there is no conversion
step of ours in the middle and nothing to go wrong in it. The first set was built by hand on 8 September for
A22, B16, C7, D8, E6, E5 and P2; every one of those is a generation behind now, which is what this tool is
for. It is a rebuild, not a one-off.

TWO RULES FROM THE SEPTEMBER SET, both kept:
  - The archive is built from the DELIVERABLE snapshot where one exists, never from the working folder, so
    what a reviewer opens is the same copper the gerbers were cut from. A board with no deliverable yet (B, C)
    is taken from its phase directory and SAYS SO in its note.
  - The import is ONE WAY. Nothing edited on the site comes back here; findings return as notes and are fixed
    in the generators. A board file is an output of `tools/gen_*.py` and is never hand-edited.

Every archive gets a note naming the board's measured state, because handing someone a board without its
numbers invites them to assume it is finished. B19 in particular is thirty hard violations and unrouted.
"""
import os, sys, json, zipfile, subprocess, datetime

ECAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(ECAD))
OUT = os.path.join(ECAD, "easyeda-pro", "import")

# (letter, rev, project stem, source directory relative to the repo, measured state)
# The state lines are measurements, each taken with tools/drc.sh plus tools/hardset.py on the board named.
BOARDS = [
    ("A", "A24", "pcb-a-power", "v2/release/revA/boards/meshsat-pcb-a-revA-A24",
     "routed and cut: 0 hard of the fifteen types, 0 unrouted, gate ALL PASS on 798 checks, netlist 2004 of 2004, "
     "three USB pairs matched to 0.23, 0.13 and 0.00 mm. Open against it: eight of its twelve rails exceed IPC-2221 "
     "current density, VBAT worst at 8.2x, which became a verdict on 13 September and re-opens this deliverable."),
    ("B", "B19", "pcb-b-compute", "v2/ecad/pcb-b-compute-b19",
     "NOT ROUTED, and this is the working phase directory rather than a deliverable. The board as it stands is "
     "hard 30 (clearance 14, shorting_items 8, solder_mask_bridge 8) and 499 unrouted, AFTER the pair pre-router "
     "laid 37 of its 113 differential pairs. The placed board underneath, before any pair copper, is hard 0. "
     "Read this one for the floor plan, the schematic and the fabric, not for finished copper."),
    ("C", "C10", "pcb-c-display", "v2/ecad/pcb-c-display-c8",
     "routed, not yet cut as a deliverable, from the working phase directory: 0 hard of the fifteen types and "
     "1 unrouted. Read it as TWO open: the closure that took it from two to one was laid at 0.25 mm by a tool "
     "whose net class lookup was dead, against the 0.5 mm this rail's class declares, and at the real width it "
     "does not fit. /+3V3 at U3 pad 10 needs room, which is a placement change."),
    ("D", "D10", "pcb-d-aprs", "v2/release/revA/boards/meshsat-pcb-d-revA-D10",
     "routed and cut: 0 hard, 0 unrouted, gate ALL PASS on 231 checks, netlist 994 of 994, four of four pairs "
     "within 1 mm. Its last connection was closed by hand after three measured refusals. Open against it: the "
     "5 V rail's class width is under review and its current density exceeds IPC-2221 by 1.4x."),
    ("E1", "E7", "pcb-e1-dock", "v2/release/revA/boards/meshsat-pcb-e-revA-E7",
     "routed and cut: 0 hard, 0 unrouted, 415 vias, gate 88 of 88, netlist 816 of 816. Open against it: both "
     "rails exceed IPC-2221 current density, VIN_RAW at 3.4x."),
    ("E5", "E5", "pcb-e5-block", "v2/release/revA/boards/meshsat-pcb-e5-revA-E5",
     "routed and cut, two layers at 2 oz. A bare contact board with no schematic by design: every target carries "
     "the net of the spring pin above it, read from board A. Nothing is open against it."),
    ("P", "P3", "pcb-p-pack", "v2/release/revA/boards/meshsat-pcb-p-revA-P3",
     "routed and cut: 0 hard, 0 unrouted, 55 vias, every part certified against JLCPCB's catalogue. Open against "
     "it: two of three rails exceed IPC-2221 current density at the 2 oz copper it is ordered on."),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    stamp = datetime.date.today().isoformat()
    made, missing = [], []
    for letter, rev, stem, src, state in BOARDS:
        s = os.path.join(REPO, src)
        pcb = os.path.join(s, stem + ".kicad_pcb")
        if not os.path.exists(pcb):
            missing.append("%s: no board at %s" % (rev, os.path.relpath(pcb, REPO))); continue
        pretty = os.path.join(s, "meshsat.pretty")
        if not os.path.isdir(pretty):
            pretty = os.path.join(ECAD, "meshsat.pretty")        # a phase directory shares the tree's library
        fplib = os.path.join(s, "fp-lib-table")
        if not os.path.exists(fplib):
            fplib = os.path.join(ECAD, stem, "fp-lib-table")     # the deliverables carry no fp-lib-table
        if not os.path.exists(fplib):
            missing.append("%s: no fp-lib-table for %s" % (rev, stem)); continue

        zp = os.path.join(OUT, "%s-%s-import.zip" % (stem, rev))
        n_mod = 0
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for ext in ("kicad_pro", "kicad_sch", "kicad_pcb"):
                f = os.path.join(s, "%s.%s" % (stem, ext))
                if os.path.exists(f): z.write(f, "%s/%s.%s" % (stem, stem, ext))
            z.write(fplib, "%s/fp-lib-table" % stem)
            for m in sorted(os.listdir(pretty)):
                if m.endswith(".kicad_mod"): z.write(os.path.join(pretty, m), "meshsat.pretty/" + m); n_mod += 1
            z.writestr("%s/IMPORT-NOTE.txt" % stem, "\n".join([
                "MeshSat V2 PCB-%s, revision %s" % (letter, rev),
                "Archive built %s from %s" % (stamp, src),
                "",
                "STATE OF THIS BOARD",
                state,
                "",
                "HOW TO IMPORT",
                "EasyEDA Pro: Start Page > Import KiCad (or File > Import), choose this zip, Import Document,",
                "associate footprint and 3D model automatically. Read the Log tab afterwards: footprints moved",
                "between layers and unbound 3D models are reported there and are expected on some boards.",
                "",
                "WHAT THIS IS NOT",
                "The import is one way. Nothing changed on the site comes back into this project, because every",
                "board file here is generated by the Python in v2/ecad/tools/ and a defect is fixed in the",
                "generator, never in the board. Send findings as notes and they land in the generator.",
                "",
                "Nothing is ordered from these files and no cart line is touched.",
            ]) + "\n")
        made.append((rev, stem, os.path.getsize(zp), n_mod, os.path.relpath(zp, REPO)))

    for rev, stem, size, n_mod, rel in made:
        print("easyeda: %-5s %-15s %6.1f MB, %3d footprint(s) -> %s" % (rev, stem, size / 1e6, n_mod, rel))
    if missing:
        for m in missing: print("easyeda: MISSING " + m)
        return 1
    print("easyeda: %d archive(s) built for the current state of every board" % len(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
