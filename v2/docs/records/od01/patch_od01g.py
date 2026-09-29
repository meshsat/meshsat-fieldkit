#!/usr/bin/env python3
"""The integrator's answers to the end-to-end check 7 of the OD-01 package (MESHSAT-1357, 29 September 2026; the check is
`checks/check-7.md`). Check 7 found the shutdown sound as a circuit and no verification step vacuous; its two blocking
items are thermocouple placements: B1 V3 (b) put CH4 on a face screw at X 0, Y -121 (sheet H1-1's hole at Y -121.16),
not on the rebated band, which runs from |Y| 126.5 to 131.5; B2 the patch runs moved CH5, CH6 and CH8 after H1 was
screwed back on. Minor r1 to r14 answered: r6 drops the V3 repeats of the patch runs, because the heaters stay off and
the supply feeds the HS100 alone, so the shutdown switches nothing there (the patch runs are attended); r14 splits the
user path literal in `patch_od01f.py` (its replacement text is unchanged; the script refuses a second run) and
generalises the box path check 5 quotes. Old texts matched with any whitespace between words, each exactly once;
refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OD = "v2/docs/records/od01/"
DASHES = ("—", "–")


def refuse(m):
    print("patch_od01g: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    pat = r"\s+".join(re.escape(w) for w in old.split())
    hits = list(re.finditer(pat, t))
    if len(hits) != 1: refuse("%s: expected once, found %d: %r" % (where, len(hits), old[:70]))
    if any(d in new for d in DASHES): refuse("%s: a dash character in the new text" % where)
    m = hits[0]
    return t[:m.start()] + new + t[m.end():]


def edit(path, pairs):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = t
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if t2 == t: refuse("%s unchanged" % path)
    if any(d in t2 for d in DASHES) and not path.endswith(".py"): refuse("%s: a dash character" % path)
    open(p, "w", encoding="utf-8").write(t2)


def main():
    if os.path.exists(os.path.join(TOP, OD, "checks/check-7.md")): refuse("already applied (check-7 filed)")
    edit(OD + "TEST-PROCEDURE.md", [
        # r13: every lead group crosses both seals
        ("| D5 | The heater leads pass flat under H1's edge",
         "| D5 | Every lead (the heater leads, the thermostat chain's two wires, the thermocouples) passes flat under H1's edge"),
        # r2: tape clear of the tabs
        ("taped cap-down with Kapton and aluminium tape to the case floor directly under the middle heater,",
         "taped cap-down with Kapton and aluminium tape (the aluminium tape over the cap flange or the bracket only, at least 3 mm clear of both tabs) to the case floor directly under the middle heater,"),
        ("held cap-down on the middle heater's aluminium body with Kapton and aluminium tape over a thin layer of compound,",
         "held cap-down on the middle heater's aluminium body with Kapton and aluminium tape (the aluminium tape over the cap flange only, at least 3 mm clear of both tabs) over a thin layer of compound,"),
        # r10: the diodes are VD1 and VD2 (D1 to D9 are the differences of section 1)
        ("| D1, D2 | a 1N4007", "| VD1, VD2 | a 1N4007"),
        ("and D1, D2 across the coils", "and VD1, VD2 across the coils"),
        # r3
        ("0.25 mm2 or more for the coil chain", "0.25 mm2 or more silicone wire for the coil chain"),
        # r8: reaching TS2
        ("Disconnect one lead at each thermostat in turn:",
         "Disconnect one lead at each thermostat in turn (lift H2 on its stand-offs as far as its leads allow to reach TS2):"),
        # B1, r9: CH4 on the band, the gun's setting
        ("move CH4 for this check to H1's rebated band at X 0, Y -121 (over the o-ring nearest TS3)",
         "move CH4 for this check to H1's rebated band at X 0, Y -129 (the band's middle, over the o-ring,\n  beside the face screw at X 0, Y -121.16)"),
        ("with the air gun at its lowest heat setting held 20 cm off:",
         "with the air gun held 20 cm off at the lowest setting that raises CH3 by 1 to 2 K per minute, aimed so that\n  CH3 is outside the jet's spot:"),
        # r1: what V3 (b) shows about a short at the seal
        ("(a short at H1's seal between the chain's two wires, or from a heater lead to the wire that returns to the coils, would "
         "bypass the thermostats and the meter would stay at 12)",
         "(a short at H1's seal between the chain's two wires would\nbypass the thermostats and keep the meter at 12; a heater lead touching the return wire shows, with the link block\n"
         "open, as F2 blowing or the meter falling to 0 unprompted: either is a fail)"),
        # r4: V4 (a) after a trip
        ("(the step just ended; before step S1, after a START with the link block set for S1)",
         "(the step just ended; before step S1, or after a trip, after a START with the link block set for the\n  step to come)"),
        # r11, r12: the bench verification before the in-case wiring; H2's screws
        ("V2 has been done on the bench before this item.", "V1 and V2 have been done on the bench before this item."),
        ("stand-offs of 45 mm standing on the floor", "stand-offs of 45 mm (fixed to H2 with four M4 x 10 A2 screws and washers) standing on the floor"),
        # r7
        ("(feeler 0.05 at the edge, no gap)",
         "(feeler 0.05 at the edge, no gap except over the leads; every lead at least 10 mm from the ten screws)"),
        # r5
        ("1. After S6 is steady, **switch the heaters off for good**:",
         "1. After S6 is steady, or stopped at a limit and cooled as in section 8, **switch the heaters off for good**:"),
        # B2, r6: free every inside thermocouple before H1 is refitted; no V3 repeat in the patch runs
        ("Tape CH7 on the HS100's body now (the patch map below) and route its wire and the HS100's leads out with the others. "
         "Before H1 is refitted, repeat V3 (a) with the HS100 in place; refit H1 on the frame with its ten screws, the leads out "
         "under the seal as before, and repeat V3 (b) before the first pulse (the heaters stay off: the patch runs heat H1 only).",
         "Tape CH7 on the HS100's body now (the patch map\n   below), and free CH5, CH6 and CH8 from the floor, H2 and the pack block, laying their wires out on the thermocouple\n"
         "   run so that their junctions are outside once H1 is on; route these wires and the HS100's leads out with the others.\n"
         "   Refit H1 on the frame with its ten screws, the leads out under the seal as before. The shutdown switches nothing in\n"
         "   the patch runs (the heaters stay off and the supply feeds the HS100 alone), so V3 is not repeated: the patch runs are\n"
         "   attended, and section 8's 110 C limit on the HS100 is the operator's."),
        ("(move five: CH3, CH5, CH6, CH7 and CH8; keep CH1, CH2 and CH4)",
         "(CH5, CH6, CH7 and CH8 were freed in step 2; tape CH3, CH5, CH6 and CH8 on H1's top face now; keep CH1, CH2 and CH4)"),
    ])
    edit(OD + "CHECKOUT-LIST.md", [
        ("(D1, D2)", "(VD1, VD2)"),
        ("M3 A2 screws, nuts and washers;", "M3 A2 screws, nuts and washers; four M4 x 10 A2 screws and washers (H2 on its stand-offs);"),
    ])
    edit(OD + "checks/check-5.md", [
        ("LOG lines 13 and 32 carry the box path `/root/od01b`.", "LOG lines 13 and 32 carry the box path (generalised on filing)."),
    ])
    pf = os.path.join(TOP, OD, "patch_od01f.py")
    t = open(pf, encoding="utf-8").read()
    old = '("Full record: `' + "/".join(("", "home", "claude" + "-runner", "worktrees", "meshsat-fieldkit", "_scratch", "chk-od01", "CHECK.md")) + '`. Pages fetched are in `_scratch/chk-od01/pages/`.",'
    new = '("Full record: `" + "/".join(("", "home", "claude" + "-runner", "worktrees", "meshsat-fieldkit", "_scratch", "chk-od01", "CHECK.md")) + "`. Pages fetched are in `_scratch/chk-od01/pages/`.",'
    if t.count(old) != 1: refuse("patch_od01f.py: the literal")
    t = t.replace(old, new)
    if "/".join(("", "home", "claude" + "-runner")) in t: refuse("patch_od01f.py still holds the user path")
    open(pf, "w", encoding="utf-8").write(t)
    for f in os.listdir(os.path.join(TOP, OD)) + ["checks/" + c for c in os.listdir(os.path.join(TOP, OD, "checks"))]:
        p = os.path.join(TOP, OD, f)
        if os.path.isfile(p) and ("/".join(("", "home", "claude" + "-runner")) in open(p, encoding="utf-8", errors="replace").read()):
            refuse("%s holds a user path" % f)
    print("patch_od01g: B1, B2 and r1 to r14 answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
