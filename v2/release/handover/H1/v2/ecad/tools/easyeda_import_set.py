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
    ("A", "A32", "pcb-a-power", "v2/ecad/pcb-a-power-a23",
     "routed and closed by hand to 0 hard of the fifteen types and 0 unrouted (15 September 2026), from the working "
     "phase directory, NOT cut as a deliverable: eight of its twelve rails meet IPC-2221 current density and four miss "
     "on one pour cell each (VBAT 1.42x at the plane under U2's escape fan, VIN_RAW 2.70x at the head island, VBUS20 1.73x "
     "at R16's vias, the PA rail 1.61x where J_AB2's pins stand in its run); A33 and A34 carry the copper for those four "
     "and are routing. The BOM is certified against JLCPCB with owner ruling 10's 10 uF 50 V and 100 V capacitors."),
    ("B", "B19", "pcb-b-compute", "v2/ecad/pcb-b-compute-b19",
     "NOT ROUTED, and this is the working phase directory rather than a deliverable: the placed board reads 0 hard of the "
     "fifteen types; the pair pre-router lays 66 of its 113 differential pairs and twelve of those come off again for "
     "legality, so 54 stay coupled and the rest are the router's; the first plain route of 15 September left about 500 "
     "connections open after one 2 h 40 pass, and the route campaign continues under a coupled-length judgement of 0.80 "
     "(owner decision 24, delegated). Read this one for the floor plan, the schematic and the fabric, not for finished copper."),
    ("C", "C17", "pcb-c-display", "v2/release/revA/boards/meshsat-pcb-c-revA-C17",
     "routed and cut (15 September 2026, the first C deliverable): 0 hard, 0 unrouted, check ALL PASS, its 5 V rail MET, "
     "netlist 852 of 852, contracts ALL PASS, verify_deliverable 36 of 36 and the final gate 38 of 38. Its only pair, the "
     "RP2040's full-speed USB, is declared with no impedance target. Nothing is open against it."),
    ("D", "D11", "pcb-d-aprs", "v2/release/revA/boards/meshsat-pcb-d-revA-D11",
     "routed and cut (14 September 2026): 0 hard, 0 unrouted, four of four pairs within 1 mm and on target, contracts 42 of 42; "
     "owner ruling 15 built, the 1 A rail carried in locked inner copper with the PWR class back at 0.5 mm. Nothing is open against it."),
    ("E1", "E9", "pcb-e1-dock", "v2/release/revA/boards/meshsat-pcb-e-revA-E9",
     "routed and cut (14 September 2026): 0 hard, 0 unrouted, check_pcb_e ALL PASS, both rails MET on the fill the board is cut with, "
     "verify_deliverable 36 of 36. The LT8705A U5 is hand-fitted on every board (owner ruling 12). Nothing is open against it."),
    ("E5", "E5", "pcb-e5-block", "v2/release/revA/boards/meshsat-pcb-e5-revA-E5",
     "routed and cut, two layers at 2 oz. A bare contact board with no schematic by design: every target carries "
     "the net of the spring pin above it, read from board A. Nothing is open against it."),
    ("P", "P4", "pcb-p-pack", "v2/release/revA/boards/meshsat-pcb-p-revA-P4",
     "routed and cut (14 September 2026): 0 hard, 0 unrouted, three of three rails MET at the 2 oz copper it is ordered on "
     "(owner ruling 7), 36 of 36, every part certified against JLCPCB's catalogue. Nothing is open against it."),
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
            # The note sits at the archive ROOT, not inside the project folder. The folder that the importer
            # reads has to match the structure proved on 8 September exactly: project, schematic, board,
            # fp-lib-table and nothing else. An unexplained extra file in there is a variable nobody has
            # tested, and the September run already needed retries on three boards for the site's own
            # reasons; adding one more unknown to a flaky step is how a reviewer's evening gets wasted.
            z.writestr("IMPORT-NOTE.txt", "\n".join([
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
