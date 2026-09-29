#!/usr/bin/env python3
"""Stream od01b (MESHSAT-1357, 29 Sep 2026): write PACKAGE.md and PACKAGE.sha256 beside this file, the list of every file an
engineer needs for the OD-01 machining quotes and the two tests, by repository path and sha256, so the coordinator can
export the package without guessing. Stdlib only. Run from anywhere: `python3 v2/docs/records/od01/make_package.py`.
It refuses to write if a listed file is missing. Verify later from the repository root with
`sha256sum -c v2/docs/records/od01/PACKAGE.sha256`."""
import os, sys, hashlib, datetime, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REL = "v2/release/case-2026-09-27/"
OD = "v2/docs/records/od01/"

# (group, path, what it is for)
FILES = [
    ("A. Read first", OD + "README.md", "the package's index and what remains"),
    ("A. Read first", OD + "TEST-BRIEF.md", "the operator's two-page brief"),
    ("A. Read first", OD + "TEST-PROCEDURE.md", "the complete procedure: what the heat test proves, the shutdown and its verification, set-up, steps, patch runs, test B, stop limits, records"),
    ("A. Read first", OD + "MACHINING-RFQ.md", "the request for quote (NOT SENT) and section 6, the receipt checks R1 to R8 that gate cutting"),
    ("A. Read first", OD + "CHECKOUT-LIST.md", "what to buy, priced, with sources; lines 10 to 15 the shutdown"),
    ("A. Read first", OD + "checks/check-1.md", "independent AI check 1 of the package (28 Sep)"),
    ("A. Read first", OD + "checks/check-2.md", "independent AI check 2: the lead exit's bias under 1 percent, H2's size"),
    ("B. Quote: H1 (heat test)", REL + "h1-heat-test-plate/h1-heat-test-plate-drawing.pdf", "sheet H1-1, governs"),
    ("B. Quote: H1 (heat test)", REL + "h1-heat-test-plate/h1-heat-test-plate.step", "H1 solid"),
    ("B. Quote: H1 (heat test)", REL + "h1-heat-test-plate/h1-heat-test-plate.dxf", "H1 outline and features by layer"),
    ("B. Quote: H1 (heat test)", REL + "h1-heat-test-plate/h1-heat-test-plate.stl", "H1 mesh (viewing)"),
    ("B. Quote: H1 (heat test)", REL + "h1-heat-test-plate/h1-heat-test-plate-check.out", "the generator's check against C1's DXF (PASS of 15)"),
    ("B. Quote: H1 (heat test)", REL + "h1-heat-test-plate/README.md", "H1's definition, choices and provenance"),
    ("B. Quote: H1 (heat test)", REL + "h1-heat-test-plate/MANIFEST.sha256", "H1 folder manifest"),
    ("C. Quote: C6 legs", REL + "drawings/frame-and-legs-drawing.pdf", "sheet 2"),
    ("C. Quote: C6 legs", REL + "frame-legs/frame-leg.dxf", "the leg profile, 4 off"),
    ("C. Quote: C6 legs", REL + "frame-legs/frame-leg.step", "the leg solid"),
    ("C. Quote: C6 legs", REL + "frame-legs/frame-legs-4.step", "all four legs in place"),
    ("C. Quote: C6 legs", REL + "frame-legs/leg-locator.stl", "printed locator (operator's)"),
    ("C. Quote: C6 legs", REL + "frame-legs/wedge.stl", "printed centring wedge (operator's)"),
    ("D. Quote: C1 face plate", REL + "drawings/face-plate-drawing.pdf", "sheet 1"),
    ("D. Quote: C1 face plate", REL + "face-plate/face-plate.step", "C1 solid"),
    ("D. Quote: C1 face plate", REL + "face-plate/face-plate.dxf", "C1 outline and features by layer"),
    ("D. Quote: C1 face plate", REL + "templates/face-plate-1to1-A3.pdf", "1:1 check print (optional)"),
    ("E. Quote: C4 entry plates and gaskets", REL + "drawings/rf-entry-plates-drawing.pdf", "sheet 4"),
    ("E. Quote: C4 entry plates and gaskets", REL + "rf-entry-plates/rf-entry-plate-east.step", "C4-E solid"),
    ("E. Quote: C4 entry plates and gaskets", REL + "rf-entry-plates/rf-entry-plate-east.dxf", "C4-E profile"),
    ("E. Quote: C4 entry plates and gaskets", REL + "rf-entry-plates/rf-entry-plate-west.step", "C4-W solid"),
    ("E. Quote: C4 entry plates and gaskets", REL + "rf-entry-plates/rf-entry-plate-west.dxf", "C4-W profile"),
    ("E. Quote: C4 entry plates and gaskets", REL + "rf-entry-plates/rf-entry-gasket-east.dxf", "G2"),
    ("E. Quote: C4 entry plates and gaskets", REL + "rf-entry-plates/rf-entry-gasket-west.dxf", "G3"),
    ("F. Quote: C3 connector plate (quote only)", REL + "drawings/connector-plate-drawing.pdf", "sheet 3"),
    ("F. Quote: C3 connector plate (quote only)", REL + "connector-plate/connector-plate.step", "C3 solid"),
    ("F. Quote: C3 connector plate (quote only)", REL + "connector-plate/connector-plate.dxf", "C3 profile"),
    ("F. Quote: C3 connector plate (quote only)", REL + "connector-plate/connector-plate-gasket.dxf", "G1"),
    ("G. Quote: L1 lid plate (optional)", REL + "lid-tray-qmx-r2/lid-tray-qmx-r2-drawing.pdf", "sheets 14r2-1 to 14r2-3"),
    ("G. Quote: L1 lid plate (optional)", REL + "lid-tray-qmx-r2/lid-plate-qmx-r2.step", "L1 solid"),
    ("G. Quote: L1 lid plate (optional)", REL + "lid-tray-qmx-r2/lid-plate-qmx-r2.dxf", "L1 profile"),
    ("G. Quote: L1 lid plate (optional)", REL + "lid-tray-qmx-r2/lid-tray-qmx-r2.stl", "the printed tray (build stage)"),
    ("G. Quote: L1 lid plate (optional)", REL + "lid-tray-qmx-r2/lid-tray-qmx-r2-frame.stl", "the printed tray's frame (build stage)"),
    ("H. Tests: drilling, stand-ins, margins", REL + "templates/case-templates-1to1.pdf", "1:1 wall templates and check prints (T5, T6, R8)"),
    ("H. Tests: drilling, stand-ins, margins", REL + "drawings/case-drawings-2-to-14.pdf", "sheets 2 to 14 in one file (stack, plan, envelopes)"),
    ("H. Tests: drilling, stand-ins, margins", REL + "drawings/board-envelope-a.pdf", "board A stand-in (T4)"),
    ("H. Tests: drilling, stand-ins, margins", REL + "drawings/board-envelope-b.pdf", "board B stand-in (T4)"),
    ("H. Tests: drilling, stand-ins, margins", REL + "drawings/board-envelope-e.pdf", "board E stand-in (T4)"),
    ("H. Tests: drilling, stand-ins, margins", REL + "zstack/zstack.json", "the pack pocket and the stack heights (H2's and H3's places)"),
    ("H. Tests: drilling, stand-ins, margins", REL + "margins/CASE-FIT-UNCERTAINTIES.md", "the OPEN rows each check closes"),
    ("H. Tests: drilling, stand-ins, margins", REL + "margins/frame_seat.out", "the 70 margins and their verdicts"),
    ("H. Tests: drilling, stand-ins, margins", REL + "README.md", "the case release's README"),
    ("H. Tests: drilling, stand-ins, margins", REL + "MANIFEST.sha256", "the case release's manifest"),
    ("I. Makers' documents", "v2/vendor/peli/1450/1451-931-customer-drawing-2025-01-15.pdf", "Peli's customer drawing 1451-931 (the moulding the design targets, D-08a)"),
    ("I. Makers' documents", "v2/vendor/peli/1450/1450_pf.pdf", "Peli's 1450PF frame sheet (1453-314-000 rev A)"),
    ("I. Makers' documents", "v2/vendor/peli/panel-frame-inst.pdf", "Peli's panel frame mounting instructions"),
    ("I. Makers' documents", "v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf", "Arcol HS resistors: ratings, heatsinks, hole sizes"),
    ("I. Makers' documents", "v2/vendor/elmwood/honeywell-commercial-thermostats-2455r.pdf", "the 2455R thermostats: tolerance bands, AC-only ratings"),
    ("I. Makers' documents", "v2/vendor/finder/finder-40-series-en.pdf", "the Finder 40.52 relay: 8 A, DC1 8 A at 30 V"),
    ("I. Makers' documents", "v2/vendor/polyphaser/polyphaser-gth-sff-al-sma-surge-protector.pdf", "the arrestor (T11)"),
    ("I. Makers' documents", "v2/vendor/xenarc/xenarc-709gnk-dimensional-drawing-v3.pdf", "the monitor's outline and depth for its stand-in (T4)"),
    ("J. Sources of the procedures", "v2/docs/feasibility/POWER-THERMAL.md", "section 10: the heat-balance experiment"),
    ("J. Sources of the procedures", "v2/docs/CASE-MARGINS.md", "sections 2, 5 and 7: Peli's figures, checks T1 to T11, when each runs"),
    ("K. Generators (to regenerate H1)", "v2/cad/h1_heat_test_plate.py", "H1's DXF, STEP, STL and check"),
    ("K. Generators (to regenerate H1)", "v2/cad/h1_heat_test_plate_drawing.py", "sheet H1-1"),
    ("K. Generators (to regenerate H1)", "v2/cad/drawing_kit.py", "the sheets' shared helpers"),
    ("K. Generators (to regenerate H1)", "v2/ecad/tools/panel1450.py", "the single geometry source of C1 and H1"),
    ("K. Generators (to regenerate H1)", "v2/cad/case_manifest.py", "writes a release folder's manifest"),
    ("K. Generators (to regenerate H1)", "v2/cad/requirements-cad.lock", "the pinned CAD venv"),
    ("L. Independent checks 3 to 6, and the records the documents cite", OD + "checks/check-3.md", "independent AI check 3 (29 Sep) of the corrected package; its items answered by patch_od01c.py"),
    ("L. Independent checks 3 to 6, and the records the documents cite", OD + "checks/check-4.md", "independent AI check 4 (29 Sep): N1 and N2 and the minor items answered by patch_od01d.py, n6 carried"),
    ("L. Independent checks 3 to 6, and the records the documents cite", OD + "checks/check-5.md", "independent AI check 5 (29 Sep): B1 (V4) and the minor items answered by patch_od01e.py"),
    ("L. Independent checks 3 to 6, and the records the documents cite", OD + "checks/check-6.md", "independent AI check 6 (29 Sep), the first end-to-end: B1 to B3 and q1 to q16 answered by patch_od01f.py"),
    ("L. Independent checks 3 to 6, and the records the documents cite", "v2/docs/reviews/READY-TO-ACT.md", "the ready-to-act review the checkout list and RFQ cite"),
    ("L. Independent checks 3 to 6, and the records the documents cite", "v2/docs/ASSEMBLY.md", "the assembly steps the RFQ and the procedure cite"),
    ("L. Independent checks 3 to 6, and the records the documents cite", REL + "lid-tray-qmx-r2/README.md", "the lid tray r2 the RFQ names as printed, not machined"),
    ("L. Independent checks 3 to 6, and the records the documents cite", "v2/vendor/pem/pem-cl-self-clinching-nuts-bulletin.pdf", "PEM bulletin CL: the S-M3-2 nut, its 4.22 +0.08 hole, insertion after finishing"),
]


def main():
    missing = [p for _, p, _ in FILES if not os.path.isfile(os.path.join(REPO, p))]
    if missing: sys.exit("missing: " + ", ".join(missing))
    assert len(set(p for _, p, _ in FILES)) == len(FILES), "a path is listed twice"
    try:
        head = subprocess.check_output(["git", "-C", REPO, "rev-parse", "--short=8", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        head = "unknown"
    rows, sums, total = [], [], 0
    group = None
    for g, p, what in FILES:
        b = open(os.path.join(REPO, p), "rb").read(); h = hashlib.sha256(b).hexdigest(); total += len(b)
        if g != group:
            rows.append("\n### %s\n\n| Path | Bytes | sha256 | For |\n|---|---|---|---|" % g); group = g
        rows.append("| `%s` | %d | `%s` | %s |" % (p, len(b), h, what))
        sums.append("%s  %s" % (h, p))
    md = ["# OD-01: the package an engineer needs, by path and sha256",
          "",
          "MESHSAT-1357, stream od01b, 29 September 2026. Written by `make_package.py` beside this file (stdlib; it refuses to run if a",
          "listed file is missing) at tree `%s` plus the working files it hashed; the same list in `sha256sum` form is `PACKAGE.sha256`." % head,
          "Prototype: nothing in the package has been made, bought, sent or run. **Export:** copy every path below keeping the",
          "repository paths, then from the repository root `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` reads OK for all %d files" % len(FILES),
          "(%.1f MB in all). Groups A to G are what a shop needs for the quotes (each part's drawing PDF governs its DXF and STEP); A, H, I and J" % (total / 1e6),
          "what the operator needs for the tests; K regenerates H1; L holds the later independent checks and the records the documents cite. This file, `PACKAGE.sha256` and `LOG-od01b.md` are not in the list.",
          ""] + rows + [""]
    open(os.path.join(HERE, "PACKAGE.md"), "w", encoding="utf-8").write("\n".join(md))
    open(os.path.join(HERE, "PACKAGE.sha256"), "w", encoding="utf-8").write("\n".join(sums) + "\n")
    print("PACKAGE.md and PACKAGE.sha256: %d files, %d bytes" % (len(FILES), total))


if __name__ == "__main__":
    main()
