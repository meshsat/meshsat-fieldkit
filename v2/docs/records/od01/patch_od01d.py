#!/usr/bin/env python3
"""The integrator's answers to the independent check 4 of the OD-01 package (MESHSAT-1357, 29 September 2026; the check is
`checks/check-4.md`). Text only: no drawing, DXF, STEP or STL changes, so nothing is regenerated. Blocking N1 (the checkout
list's total of lines 1 to 14 after the second relay) and N2 (the request text's nut hole against sheet H1-1), and the
minor items n1 to n5 and n7 to n13; n6 (the check record prints the 4.22 hole with one decimal) is carried to H1's next
box build, because the format sits in the generator whose hash the sheet and the record print. H1's MANIFEST line for
its README is rewritten from the file's new sha256. Every old text is asserted exactly once and every new text is checked
for dash characters; refuses a second run. Run from the repository root: python3 <this file>."""
import hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
H1 = os.path.join(TOP, "v2/release/case-2026-09-27/h1-heat-test-plate")
DASHES = ("—", "–")


def refuse(m):
    print("patch_od01d: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    if t.count(old) != 1: refuse("%s: expected once, found %d: %r" % (where, t.count(old), old[:70]))
    if any(d in new for d in DASHES): refuse("%s: a dash character in the new text" % where)
    return t.replace(old, new)


def edit(path, pairs):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = t
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if t2 == t: refuse("%s unchanged" % path)
    open(p, "w", encoding="utf-8").write(t2)


OD = "v2/docs/records/od01/"


def main():
    if "484.80 excl. VAT (arithmetic: 416.40 + 68.40)" in open(os.path.join(TOP, OD + "CHECKOUT-LIST.md"), encoding="utf-8").read():
        refuse("already applied")
    # N1, n1, n4: the checkout list
    edit(OD + "CHECKOUT-LIST.md", [
        ("476.77 excl. VAT (arithmetic).", "484.80 excl. VAT (arithmetic: 416.40 + 68.40)."),
        ("carry only the relay coil's 54 mA and the relay (DC1 breaking capacity 8 A at 30 V, Finder's sheet) switches the heaters.",
         "carry only the two relay coils' current (about 108 mA, 54 mA each) and the relays' contacts in series (DC1 breaking capacity 8 A at 30 V each, Finder's sheet) switch the heaters."),
        ('reichelt "FIN 40.52.9 12V" (K1) |', 'reichelt "FIN 40.52.9 12V" (K1, K2) |'),
        ('reichelt "FIN 95.05" (X1) |', 'reichelt "FIN 95.05" (X1, X2) |'),
    ])
    # N2, n10: the request for quote
    edit(OD + "MACHINING-RFQ.md", [
        ("self-clinching nuts in 4.2 holes on 37.0 along X",
         "self-clinching nuts in 4.22 +0.08/-0.00 holes (PEM bulletin CL) on 37.0 along X"),
        ("| build (T7) | optional on this quote |",
         "| build (T7) | optional on this quote; if cut, only after R1 and R8 of section 6, and never before the plate each seals is released |"),
        ("everything below (H1, C6, C1, C4, C3)", "everything below (H1, C6, C1, C4, C3, G1 to G3)"),
        ("(the fit-dependent parts are H1, C6, C1, C4 and C3)", "(the fit-dependent parts are H1, C6, C1, C4, C3 and the gaskets G1 to G3)"),
    ])
    # n1, n3, n9, n10, n11, n12: the procedure
    edit(OD + "TEST-PROCEDURE.md", [
        ("**Each fit-dependent part is released for cutting only when every receipt check its row names in the table of\n"
         "   `MACHINING-RFQ.md` section 6 has passed; that table governs: H1 and C1 after R1, R2, R3, R5 and R6; C6 after R1, R3,\n"
         "   R4 and R5; the entry plates C4 and the connector plate C3 after R1, R3, R7 and R8 (C3 is not released before the\n"
         "   build).**",
         "**Each fit-dependent part is released for cutting only when every receipt check that its row in\n"
         "   `MACHINING-RFQ.md` section 1 names (the checks are the table of its section 6, whose last column names the same parts)\n"
         "   has passed: H1 and C1 after R1, R2, R3, R5 and R6; C6 after R1, R3, R4 and R5; the entry plates C4 and the connector\n"
         "   plate C3 after R1, R3, R7 and R8 (C3 is not released before the build); the gaskets G1 to G3 after R1 and R8, and\n"
         "   never before the plate each seals.**"),
        ("K1's coil is fed through a\n  chain of four normally closed bimetal thermostats TS1 to TS4, a normally closed STOP/TEST button, and, in parallel\n"
         "  with a normally open START button, K1's second contact (the self-hold).",
         "The two coils, in parallel, are fed\n  through a chain of four normally closed bimetal thermostats TS1 to TS4, a normally closed STOP/TEST button, and, in\n"
         "  parallel with a normally open START button, the second contacts of K1 and K2 in series (the self-hold)."),
        ("Pressing START energises K1; K1 holds itself.", "Pressing START energises K1 and K2; they hold themselves in."),
        ("The thermostats carry only the coil's current (0.65 W at 12 V, 54 mA)",
         "The thermostats carry only the two coils' current (0.65 W each at 12 V, about 108 mA together)"),
        ("with the body's centre at X 0, Y -104 (the front, away from the patch): the body, 16.0 mm across and 11.91 mm tall "
         "(Honeywell 2455R, Figure 3, page 5), spans Y -112 to -96, 4.9 mm inside the frame window's edge at Y -116.92, so H1 "
         "still sits flat on the ring",
         "with the body's centre at X 0, Y -99 (the front, away from the patch) and its bracket B203-S's tabs along X: the body, "
         "16.0 mm across and 11.91 mm tall (Honeywell 2455R, Figure 3, page 5), spans Y -107 to -91, and the bracket, whose "
         "largest dimension is 31.19 mm (Honeywell, Figure 18, B203S), reaches at most 15.6 mm from the centre, to Y -114.6, "
         "2.3 mm inside the frame window's edge at Y -116.92, so H1 still sits flat on the ring"),
        ("[S1 START (normally open) in parallel with K1 contact\n   21-24 (normally open)]",
         "[S1 START (normally open) in parallel with K1 contact\n   21-24 and K2 contact 21-24 in series (both normally open)]"),
        ("3. The ammeter in the heater lead after K1, the voltmeter across the heater leads where they enter the case: the coil's\n"
         "   54 mA is not in the heater reading.",
         "3. The ammeter in the heater lead after K2, the voltmeter across the heater leads where they enter the case: the coils'\n"
         "   108 mA is not in the heater reading."),
        ("a multimeter on volts at the link block's input (the load side of K1): it reads the supply's\n"
         "  volts when K1 is in and 0 when it is out. START: K1 pulls in (audible), the meter reads 12.",
         "a multimeter on volts at the link block's input (the load side of K2, after both contacts): it reads\n"
         "  the supply's volts when both relays are in and 0 when either is out. START: K1 and K2 pull in (audible), the meter\n"
         "  reads 12."),
        ("- **V3, in place.** First, with each thermostat fixed at its place and H1 lifted, warm each in turn with the air gun until\n"
         "  the meter at the link block reads 0, let it cool and press START: each installed thermostat is shown to be in the chain.",
         "- **V3, in place.** First, with each thermostat fixed at its place, H1 lifted and the link block open (nothing heats),\n"
         "  disconnect one lead at each thermostat in turn: the meter at the link block reads 0 and stays 0 when the lead is\n"
         "  refitted, until START. Each installed thermostat is so shown to be in the chain without heating anything inside the\n"
         "  case (V1 has proved its opening temperature)."),
        ("With the supply switched off, a continuity check across\n  K1's contact 11-14 and across K2's reads open on each (neither has welded).",
         "With the supply switched off, a continuity check across\n  each relay's contacts 11-14 and 21-24 reads open on all four (none has welded)."),
        ("(a second relay, about EUR 9 with its socket). Both welding in\nthe same step would;",
         "(a second relay, about EUR 9 with its socket). Likewise one relay's self-hold contact 21-24 welding no longer\n"
         "makes the latch reset by itself: the other's, in series in the hold path, opens, so the heaters stay off after a trip.\n"
         "Both relays' contacts of either pair welding in the same step would defeat it;"),
    ])
    # n2, n13: the brief
    edit(OD + "TEST-BRIEF.md", [
        ("H1, C6, C1 and the\nentry plates are released for cutting only after the checks their row names have passed; quotes may be asked earlier.",
         "H1, C6, C1, the\nentry plates C4 and the gaskets G1 to G3 are released for cutting only after the checks their row names have passed;\n"
         "the connector plate C3 is quoted only and waits for the build; quotes may be asked earlier."),
        ("thermostats holding a latching relay in the heater supply.",
         "thermostats holding two latching relays, K1 and K2, whose contacts are in series in the heater supply."),
        ("wiring a relay socket and two\npushbuttons", "wiring two relay sockets, two diodes and two\npushbuttons"),
        ("the four thermostats, the relay and its socket", "the four thermostats, the two relays with their sockets and diodes"),
        ("Elmwood 2455R thermostats in series with the coil of a Finder 40.52 relay that switches the heaters and holds itself in:",
         "Elmwood 2455R thermostats in series with the coils of two Finder 40.52 relays, K1 and K2 (a diode across each coil),\n"
         "  whose contacts in series switch the heaters and hold both relays in:"),
        ("and STOP/TEST is pressed at the start of every step (V4).",
         "and at the start of every step each relay contact is read open with the supply off and STOP/TEST is pressed (V4)."),
    ])
    # n7: the package README
    edit(OD + "README.md", [
        ("- PEM's S-type bulletin is not held (pemnet.com and its Archive copies answered 404 on 29 September): the nut code\n"
         "  S-M3-2 on sheet H1-1 is the session's reading (INFERRED) and the shop is asked to follow PEM's installation data.\n",
         "- Closed on 29 September: PEM's bulletin CL is held (`v2/vendor/pem/pem-cl-self-clinching-nuts-bulletin.pdf`). Its\n"
         "  page CL-4 gives S-M3-2 as the code for an M3 S nut in a sheet of 1.4 mm or more, in a 4.22 +0.08/-0.00 hole; sheet\n"
         "  H1-1, H1's DXF and the request text carry that hole, and the nuts are pressed after anodising (PEM's instruction).\n"),
    ])
    # n5: H1's README, then its manifest line
    rp = os.path.join(H1, "README.md")
    t = open(rp, encoding="utf-8").read()
    m = re.search(r"Generated on 29 September 2026 at 01:53 CEST.*?holds both scripts to that\)\.", t, re.S)
    if not m or t.count("Generated on 29 September 2026 at 01:53 CEST") != 1: refuse("H1 README: the source paragraph")
    new = ("Generated on 29 September 2026 at about 02:18 CEST (00:18 UTC, the drawing PDF's creation time) on the rented CAD box\n"
           "(Ubuntu 24.04, Python 3.12.3, x86_64) from branch `fnd/od01b` at `e0cd5ec1` (`CASE_BASE_COMMIT=e0cd5ec1`), after PEM's\n"
           "bulletin CL set the nut hole to 4.22 +0.08/-0.00: the four PEM holes, and so the STL and STEP, differ from every earlier\n"
           "build; the rest of the geometry does not. Four earlier builds carried a 4.2 nut hole: at `c0ec7684` the sheet misread the\n"
           "HS100's mounting hole, at `b8880536` its note 5 named the receipt checks R1 to R8 rather than the five that gate H1, at\n"
           "`f2294a69` the sheet still typed the insert pattern's spans and its title figures, which it now reads from `panel1450.py`\n"
           "(the rule `test_h1_heat_test_plate.t_h1_scripts_type_no_design_number` holds both scripts to that), and `c5a95973` was\n"
           "the last with the 4.2 hole.")
    t = t[:m.start()] + new + t[m.end():]
    t = once(t, "--base c5a95973     (after this README is written)", "--base e0cd5ec1     (after this README is written)", "H1 README")
    t = once(t, "Inputs, sha256 first 16: `v2/ecad/tools/panel1450.py` 3bdb88df98260244 (the same file the release names);",
             "Inputs, sha256 first 16: `v2/cad/h1_heat_test_plate.py` 9e949f9e1b9237a2 and `v2/cad/h1_heat_test_plate_drawing.py`\n"
             "8e0d56a6a030240f (the generator and the drawing script, as the check record and the sheet print them);\n"
             "`v2/ecad/tools/panel1450.py` 3bdb88df98260244 (the same file the release names);", "H1 README")
    t = once(t, "\n## Before cutting\n",
             "\nThe check record prints the PEM holes as \"4.2\" because that one line formats the diameter with one decimal; the value it\n"
             "compares, and the DXF's four circles, are 4.22. The format is corrected at H1's next build on the box (it sits in the\n"
             "generator, whose hash the sheet and the record print).\n\n## Before cutting\n", "H1 README")
    if any(d in t for d in DASHES): refuse("H1 README: a dash character")
    open(rp, "w", encoding="utf-8").write(t)
    mp = os.path.join(H1, "MANIFEST.sha256")
    mt = open(mp, encoding="utf-8").read()
    lines = [l for l in mt.split("\n") if l.endswith("  README.md")]
    if len(lines) != 1: refuse("H1 MANIFEST: README line")
    sha = hashlib.sha256(open(rp, "rb").read()).hexdigest()
    mt = mt.replace(lines[0], "%s  README.md" % sha)
    open(mp, "w", encoding="utf-8").write(mt)
    r = subprocess.run(["sha256sum", "-c", "--quiet", "MANIFEST.sha256"], cwd=H1, capture_output=True, text=True)
    if r.returncode: refuse("H1 MANIFEST does not verify: %s" % (r.stdout + r.stderr)[-300:])
    print("patch_od01d: N1 and N2 answered, n1 to n5 and n7 to n13 answered, n6 carried; H1's README line in its MANIFEST now %s" % sha[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
