#!/usr/bin/env python3
"""OD-01, the coordinator's corrections after the independent AI check of fnd/od01b at b9b9b32a (checks/check-3.md):
B1 one gate table (MACHINING-RFQ.md section 6) and every other document citing it by part; B2 TS3 moved wholly inside the
frame window; m2 a second relay in series; m3 a diode across each coil; m4 "supply loss"; m5 V3 shows each installed
thermostat in the chain; m6 the fuses named F1 and F2 and F1 placed before K1; m7 the patch runs lift and refit H1 and repeat
V3; m8 the brief's uncertainty rounded outward; m11 R2 read at the rim face; m12 PEM hardware after anodising; the checkout
list's relay and socket lines at two each with the subtotal recomputed. Each old text is asserted once; a second run is
refused. The drawing items (m1 the PEM hole, m10 the relief's position) are made by the H1 drawing generator, not here.
Run from the repository root."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
D = os.path.join(TOP, "v2/docs/records/od01")
edits = {}


def refuse(m):
    print("patch_od01c: REFUSED: %s" % m); sys.exit(2)


def ed(name, old, new):
    p = os.path.join(D, name)
    t = edits.get(p) or open(p, encoding="utf-8").read()
    if t.count(old) != 1: refuse("%s: %r found %d times" % (name, old[:70], t.count(old)))
    edits[p] = t.replace(old, new)


def main():
    if "K2, X2" in open(os.path.join(D, "TEST-PROCEDURE.md"), encoding="utf-8").read(): refuse("already applied")
    P = "TEST-PROCEDURE.md"
    # B1
    t = open(os.path.join(D, P), encoding="utf-8").read()
    a = t.index("**No fit-dependent part"); b = t.index("**", a + 2) + 2
    ed(P, t[a:b], "**Each fit-dependent part is released for cutting only when every receipt check its row names in the table of\n"
       "   `MACHINING-RFQ.md` section 6 has passed; that table governs: H1 and C1 after R1, R2, R3, R5 and R6; C6 after R1, R3,\n"
       "   R4 and R5; the entry plates C4 and the connector plate C3 after R1, R3, R7 and R8 (C3 is not released before the\n"
       "   build).**")
    ed("TEST-BRIEF.md", "before the receipt checks R1 to R8 (R6)", "before the receipt checks that gate it (the table of `MACHINING-RFQ.md` section 6) (R6)")
    ed("MACHINING-RFQ.md", "cut only after R1, R7 and R8 |", "cut only after R1, R3, R7 and R8 |")
    ed("MACHINING-RFQ.md", "quote now, **do not release for cutting** (note 3) |", "quote now, **do not release for cutting** (note 3); when released, after R1, R3, R7 and R8 |")
    # B2
    ed(P, "taped cap-up to H1's underside 5 mm inside the frame window's edge at X 0, Y -112 (the front, away from the patch)",
       "taped cap-up to H1's underside with the body's centre at X 0, Y -104 (the front, away from the patch): the body, 16.0 mm across and 11.91 mm tall (Honeywell 2455R, Figure 3, page 5), spans Y -112 to -96, 4.9 mm inside the frame window's edge at Y -116.92, so H1 still sits flat on the ring")
    # m2, m3, m6: a second relay, coil diodes, the fuses named
    ed(P, "- The heater current (up to 5.3 A at 12.0 V) passes one normally open contact of a relay K1.",
       "- The heater current (up to 5.3 A at 12.0 V) passes a normally open contact of each of two relays, K1 and K2, in series.")
    ed(P, "| F1 | an in-line blade fuse holder with a 7.5 A fuse in the heater lead after K1, and one with a 1 A fuse in the coil chain | not priced | outside the case |",
       "| K2, X2 | a second Finder 40.52.9.012.0000 on its own 95.05 socket, as K1 and X1; its contact in series with K1's in the heater lead, its coil in parallel with K1's | as K1 and X1 | outside the case |\n"
       "| D1, D2 | a 1N4007 (or equivalent) across each relay coil, cathode to A1 (the + side), so no thermostat breaks an inductive current | a standard rectifier | at each socket |\n"
       "| F1, F2 | in-line blade fuse holders: F1 with a 7.5 A fuse in the heater lead at the supply's +, before K1; F2 with a 1 A fuse at the start of the coil chain | not priced | outside the case |")
    ed(P, "1. Supply + -> F1 (7.5 A) -> K1 contact 11-14 (normally open) ->",
       "1. Supply + -> F1 (7.5 A) -> K1 contact 11-14 (normally open) -> K2 contact 11-14 (normally open) ->")
    ed(P, "2. Supply + -> F1 (1 A) -> S2 STOP/TEST", "2. Supply + -> F2 (1 A) -> S2 STOP/TEST")
    ed(P, "-> K1 coil A1 -> A2 -> supply -.", "-> K1 coil A1 -> A2 -> supply -, with K2's coil A1 -> A2 in parallel with K1's (both drop together) and D1, D2 across the coils.")
    t = edits[os.path.join(D, P)]
    a = t.index("**Residual risk with this arrangement:**"); b = t.index("\n\n", a)
    edits[os.path.join(D, P)] = t[:a] + ("**Residual risk with this arrangement:** one relay's contact welding closed no longer leaves the heaters on through a\n"
        "trip: the other relay's contact, in series, still opens (a second relay, about EUR 9 with its socket). Both welding in\n"
        "the same step would; V4 reads each contact on its own before every step. A step started without V4, or with any V1 to\n"
        "V3 failed, is an attended step.") + t[b:]
    ed(P, "- **V4, at the start of every step and after each lid change.** Press STOP/TEST once: the heater current falls to zero\n  (this also shows K1's contact has not welded).",
       "- **V4, at the start of every step and after each lid change.** With the supply switched off, a continuity check across\n  K1's contact 11-14 and across K2's reads open on each (neither has welded). Supply on: press STOP/TEST once, the heater\n  current falls to zero.")
    # m4
    ed(P, "supply dips), the coil drops", "supply is lost: the relays drop out below 0.1 of their rated voltage), the coils drop")
    ed("TEST-BRIEF.md", "a supply dip turns", "a supply loss turns")
    # m5
    ed(P, "- **V3, in place.** With the thermostats fixed at their places, H1 screwed on",
       "- **V3, in place.** First, with each thermostat fixed at its place and H1 lifted, warm each in turn with the air gun until\n  the meter at the link block reads 0, let it cool and press START: each installed thermostat is shown to be in the chain.\n  Then, with H1 screwed on")
    # m7
    ed(P, "unless a second supply is available for the patch; open the\n   lid.", "unless a second supply is available for the patch; open the\n   lid and lift H1 off the frame (its ten screws) to reach its underside.")
    ed(P, "(the tag is 2.9 mm from the frame window's edge).", "(the tag is 2.9 mm from the frame window's edge). Refit H1 on the frame with its\n   ten screws, the leads out under the seal as before, and repeat V3 before any heating.")
    # m8
    ed("TEST-BRIEF.md", "-3 to +8 % at 21 W", "-4 to +8 % at 21 W (rounded outward)")
    # m11, m12
    ed("MACHINING-RFQ.md", ", mid-length and mid-width, 2 mm below the rim face |", ", mid-length and mid-width, the jaws' tips at the rim face, where Peli's STEP figures are taken |")
    ed("MACHINING-RFQ.md", "please state whether you insert the PEM hardware before or after anodising.", "the PEM hardware is inserted after anodising (PEM's own instruction, bulletin CL).")
    # the checkout list: two relays, two sockets, diodes; the subtotal recomputed
    C = "CHECKOUT-LIST.md"
    ed(C, '| 1 | EUR 4.12 excl., 4.98 incl. |', '| 2 (K1, K2) | EUR 8.24 excl., 9.96 incl. |')
    ed(C, '| 1 | EUR 3.91 excl., 4.73 incl. |', '| 2 (X1, X2) | EUR 7.82 excl., 9.46 incl. |')
    ed(C, "two in-line blade fuse holders with a 7.5 A and a 1 A fuse;", "two in-line blade fuse holders with a 7.5 A and a 1 A fuse (F1, F2); two 1N4007 diodes (D1, D2);")
    ed(C, "**EUR 60.37 excl. VAT, EUR 73.05 incl. 21 % VAT**", "**EUR 68.40 excl. VAT, EUR 82.76 incl. 21 % VAT** (with the second relay and socket of the independent check's m2)")
    ed("README.md", "(EUR 60.37 excl., 73.05 incl.,", "(EUR 68.40 excl., 82.76 incl.,")
    for p, t in edits.items():
        if "—" in t or "–" in t: refuse("a dash in %s" % p)
        open(p, "w", encoding="utf-8").write(t)
    print("patch_od01c: %d files corrected (B1, B2, m2 to m8, m11, m12, the checkout lines)" % len(edits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
