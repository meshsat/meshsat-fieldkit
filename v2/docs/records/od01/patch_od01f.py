#!/usr/bin/env python3
"""The integrator's answers to the end-to-end check 6 of the OD-01 package (MESHSAT-1357, 29 September 2026; the check is
`checks/check-6.md`). The verification block of TEST-PROCEDURE.md section 3 is replaced again as one text (the method of
patch_od01e.py), and the set-up, the steps, the patch runs, the stop limits, the records, the brief, the checkout list's
small items and the README are brought to it. B1: the thermostat chain's two wires cross the seals each on a run of its
own, at least 50 mm from the other and from every heater lead, so no single pinch at a seal (H1's band or the lid gasket)
can bypass the chain; the lid-closed crossings are stated as not tested; V4's heading no longer claims a check after the
lid change it does not make. B2: the heaters are switched off for good before the patch runs, and the second-supply
clause is gone. B3: the air gun is on the buy list (a hot plate serves V1 only). Minor q1 to q16 answered. Old texts are
matched with any whitespace between words, each exactly once; refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OD = "v2/docs/records/od01/"
DASHES = ("—", "–")


def refuse(m):
    print("patch_od01f: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    pat = r"\s+".join(re.escape(w) for w in old.split())
    hits = list(re.finditer(pat, t))
    if len(hits) != 1: refuse("%s: expected once, found %d: %r" % (where, len(hits), old[:70]))
    if any(d in new for d in DASHES): refuse("%s: a dash character in the new text" % where)
    m = hits[0]
    return t[:m.start()] + new + t[m.end():]


def edit(path, pairs, fn=None):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = t
    if fn: t2 = fn(t2)
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if t2 == t: refuse("%s unchanged" % path)
    if any(d in t2 for d in DASHES): refuse("%s: a dash character" % path)
    open(p, "w", encoding="utf-8").write(t2)


VERIFY = """**Verification (before the case is heated, each result recorded in `checks.csv`; section 4 says when each part runs;
what it shows and what it does not is stated after V4):**
- **V1, each thermostat alone.** Clamp it cap-down on an aluminium block of about 50 x 50 x 10 mm with one thermocouple
  taped beside it, on a hot plate or under the hot-air gun held 20 cm off. Multimeter on its terminals (continuity). Warm
  at no more than 2 K per minute over the last 15 K. Record the block temperature when it opens and, cooling, when it
  closes. **Pass:** TS1 opens between 84 and 96 C; TS2 and TS3 between 57 and 63 C; TS4 between 136 and 144 C; each
  closes again on cooling. A part outside its band is rejected, not adjusted.
- **V2, the latch on the bench** (before any thermostat is fitted in the case). Wire the arrangement on the bench at
  12.0 V, the heaters' link block open so nothing heats, a multimeter on volts at the link block's input (the load side
  of K2, after both contacts): it reads the supply's volts only while both relays are in. A thermocouple is taped beside
  each thermostat.
  (a) START, pressed and released: K1 and K2 pull in and stay in, the meter reads 12. STOP/TEST: both relays are heard
  to drop, the meter reads 0 and stays 0 when the button is released. START again: 12.
  (b) Warm each thermostat in turn with the air gun until it opens: 0. Let it cool until its thermocouple reads 5 K under
  its V1 closing temperature (so it has reclosed): **the meter stays at 0** until START.
  (c) The series wiring. Supply off, K2's A1 lead off its socket terminal; supply on, hold START: K1 pulls in and the
  meter reads 0 (K2's contact 11-14 is in the heater path); release START: K1 drops (K2's contact 21-24 is in the hold
  path). Supply off, refit the lead, take K1's A1 lead off and repeat: K2 pulls in, the meter reads 0, K2 drops on
  release. Supply off, refit the lead.
  **Pass:** every action behaves so.
- **V3, in place.** Heat-resistant gloves near H2 and the heaters whenever they are warm.
  (a) With the thermostats fitted and wired (section 4 item 4) and the leads laid (item 7), H1 lifted and the link block
  open (nothing heats): START, the meter at the link block reads 12. Disconnect one lead at each thermostat in turn: the
  meter falls to 0 and stays 0 when the lead is refitted, until START, which is pressed before the next thermostat.
  (b) With H1 screwed on and the leads out under its seal (section 4 item 8), the lid open and the link block still open:
  START, 12; STOP/TEST, 0, and it stays 0 on release; START, 12. Then move CH4 for this check to H1's rebated band at
  X 0, Y -121 (over the o-ring nearest TS3) and CH3 to H1's top face at X 20, Y -99 (beside TS3's place, outside the
  jet), and stand a card shield on the case's front rim between the jet and the rim. Warm H1's top face over TS3 (X 0,
  Y -99) with the air gun at its lowest heat setting held 20 cm off: the meter falls to 0 before CH3 or CH4 reads 65 C
  (if it does not, stop the gun: V3 has failed). Let H1 cool until CH3 reads 5 K under TS3's V1 closing temperature: the
  meter stays 0 until START. Put CH3 and CH4 back on the channel map in use.
  **Pass:** every action behaves so.
- **V4, before every step (the lid and the link block are set in (c)).**
  (a) With the heaters on (the step just ended; before step S1, after a START with the link block set for S1), press
  STOP/TEST: both relays are heard to drop, the heater current falls to zero and stays zero when the button is
  released.
  (b) Switch the supply off and pull F2. A continuity check reads open across each relay's contacts 11-14 and 21-24
  (four readings) and across the START button: no contact has welded and START has not stuck. Refit F2.
  (c) With the supply still off, set the link block and the lid for the next step; after a lid change, see that every
  lead still lies flat on its own straight run of the gasket (section 4 item 7). Supply on, START: the heater current
  returns. Record the time.

**What the verification shows, and what it does not.** V1 shows each thermostat's opening temperature before it is
mounted. V2 shows the latch, its reset only by START, and both relays' contacts in series in the heater path and in the
hold path. V3 shows each installed thermostat in the chain, the chain intact with H1 closed (a short at H1's seal between
the chain's two wires, or from a heater lead to the wire that returns to the coils, would bypass the thermostats and the
meter would stay at 12), and TS3 opening on heat in its place. V4 shows, before each step, that STOP/TEST stops the
heating with both relays heard to drop, that no relay contact has welded and that START has not stuck. **Not shown in
place:** (1) that TS1, TS2 and TS4 still open on heat after mounting: V1 proved each before it; the M3 through TS1's
bracket and the tape on TS2 and TS4 do not load the disc (INFERRED); heating them in place would heat the case, which is
the test itself. (2) The chain's crossings under the lid gasket with the lid closed (steps S2, S3 and S6): they are not
tested. Because the chain's two wires cross each on a run of its own, at least 50 mm from each other and from every
heater lead (wiring item 2), a single pinch there cannot bypass the chain; two pinches at once could. The stop limits of
section 8 are a second line only while someone attends; unattended, a TS1, TS2 or TS4 that failed to open in place has
only the other thermostats' indirect cover.

**Residual risk with this arrangement:** one relay's contact welding closed no longer leaves the heaters on through a
trip: the other relay's contact, in series, still opens (a second relay, about EUR 9 with its socket). Likewise one
relay's self-hold contact 21-24 welding no longer makes the latch reset by itself: the other's, in series in the hold
path, opens, so the heaters stay off after a trip. START sticking closed during a step would let the heaters cycle on the
thermostats, which still hold every temperature they sit at; V4 reads START open before every step. Both 11-14 contacts
welding in the same step would leave the heaters on through any trip, with no temperature held; both 21-24 contacts
welding would let them cycle on the thermostats; V4 reads each contact on its own before every step. A step started
without V4, or with any of V1 to V3 failed, is an attended step.
"""


def verify_block(t):
    i = t.index("**Verification (before the case is heated, each result recorded in `checks.csv`; what it shows and what it does not is")
    j = t.index("\n## 4. Test A set-up")
    return t[:i] + VERIFY + t[j:]


def main():
    if os.path.exists(os.path.join(TOP, OD, "checks/check-6.md")): refuse("already applied (check-6 filed)")
    edit(OD + "TEST-PROCEDURE.md", [
        # q8: the buttons are PB1 and PB2, so S1 to S6 name only the steps
        ("| S1, S2 | START: any panel pushbutton, normally open; STOP/TEST: any panel pushbutton, normally closed;",
         "| PB1, PB2 | START (PB1): any panel pushbutton, normally open; STOP/TEST (PB2): any panel pushbutton, normally closed;"),
        ("-> S2 STOP/TEST (normally closed) -> [S1 START (normally open)",
         "-> PB2 STOP/TEST (normally closed) -> [PB1 START (normally open)"),
        # B1: the chain's two wires cross apart
        ("The thermostat chain enters and leaves the case as one flat pair beside the heater leads.",
         "The thermostat chain enters the case\n   on one single wire (to TS1) and leaves it on another (from TS4 to the coils), each on its own straight run of the\n"
         "   seals (H1's band and, lid closed, the lid gasket), at least 50 mm from the other and from every heater lead, so that no\n"
         "   single pinch at a seal can join the chain's two ends or feed the coils from a heater lead (section 4 item 7)."),
        # q9: the order of the set-up and the verification
        ("TS1 and TS4 at the middle heater (section 3).",
         "V2 has been done on the bench before this item. TS1 and\n   TS4 at the middle heater (section 3; TS1's bracket on an M3 hole drilled 2.5 and tapped in H2 like the heaters'), TS2 on\n"
         "   the floor under it and TS3 on H1's underside, joined into the chain inside the case with the 6.3 mm receptacles of\n"
         "   `CHECKOUT-LIST.md` line 15 (heat-rated at TS4)."),
        ("6. **The thermocouples, steady-state channel map** (eight channels;",
         "6. **The thermocouples, steady-state channel map** (soaked first, item 9; eight channels;"),
        # B1, q16: the leads' exit
        ("7. **The leads' exit** (checked by check-2): the heater pair and the thermostat pair pass as flat silicone wires between "
         "H1's rebated band and the frame's o-ring, and, lid closed, under the lid gasket, each on a straight run of the seal, "
         "never where it turns a corner; the thermocouple wires the same way, side by side on the same straight run. Photograph "
         "it. Do not replace Peli's purge valve with a gland.",
         "7. **The leads' exit** (the method accepted by check-2): every lead passes as a flat silicone wire between H1's rebated\n"
         "   band and the frame's o-ring, and, lid closed, under the lid gasket, on a straight run of the seal, never where it\n"
         "   turns a corner. The four heater leads (three + and the common) lie side by side on one run, the thermocouple wires on\n"
         "   another; the thermostat chain's two single wires each on a run of its own, at least 50 mm from the other and from\n"
         "   every heater lead (section 3, wiring item 2). Photograph it. Do not replace Peli's purge valve with a gland. Then V3\n"
         "   (a), H1 still lifted."),
        ("lid latches without force over the leads.", "lid latches without force over the leads. Then V3 (b); V4 before step S1."),
        ("for 15 min before they are fitted;", "for 15 min before they are fitted (before item 6);"),
        # 5.1 and 5.2 (q12)
        ("After a lid change, check before START that the leads still lie flat on a straight run of the gasket.",
         "V4 (c) checks the leads after a lid change."),
        ("the amps after K2, every 30 minutes (a photograph of",
         "the amps after K2, every 30 minutes while attended and at least once in the step's last 30 minutes (a photograph of"),
        # B2, q10: the patch runs
        ("1. After S6 is steady, **switch the heaters off** (STOP/TEST) unless a second supply is available for the patch; open "
         "the lid and lift H1 off the frame (its ten screws) to reach its underside.",
         "1. After S6 is steady, **switch the heaters off for good**: STOP/TEST, supply off, link block open. Wait until CH6 and\n"
         "   CH7 read under 60 C, or wear heat-resistant gloves, before hands go near TS1 and TS4. Open the lid and lift H1 off the\n"
         "   frame (its ten screws) to reach its underside, turning it over on TS3's leads (leave them slack enough for that)."),
        ("Before H1 is refitted, repeat V3 (a) with the HS100 in place;",
         "Tape CH7 on the HS100's body now (the patch map\n   below) and route its wire and the HS100's leads out with the others. Before H1 is refitted, repeat V3 (a) with the\n"
         "   HS100 in place;"),
        ("repeat V3 (b) before any heating.",
         "repeat V3 (b) before the first pulse (the heaters stay off: the patch runs heat H1 only)."),
        ("(move four thermocouples; keep CH1, CH2 and CH4)", "(move five: CH3, CH5, CH6, CH7 and CH8; keep CH1, CH2 and CH4)"),
        ("The patch on its own supply (15 V, 7 A class, current limit 6.5 A), output off.",
         "The patch on the test A supply, moved to the HS100's leads (or a second supply of the same\n   class), current limit 6.5 A, output off; the heaters' link block stays open."),
        # q11: resuming after a trip, and its record
        ("photograph what tripped.",
         "photograph what tripped. To resume: when every channel reads within 5 K of the room, V4 in full, then the next step\n"
         "of the sequence, recorded as starting cold."),
        ("`step, lid, fans, heaters, volts, amps, start_utc, steady_utc, logger_file`",
         "`step, lid, fans, heaters, volts, amps, start_utc, steady_utc, logger_file, stopped_at_limit_utc,\n  tripped_by` (the last two empty for a step that reached steady state)"),
    ], verify_block)
    edit(OD + "TEST-BRIEF.md", [
        ("verification (about 2 h).",
         "verification (about 4 to 5 h: V1, V2 (b) and V3 (b) wait for each thermostat to reclose, near 45 C for TS2\n  and TS3; INFERRED)."),
        ("a hot plate or a hot-air gun and an aluminium block of about 50 x 50 x 10 mm (verification V1);",
         "a hot-air gun (V1 to V3; a hot plate may serve V1 only) and\n  an aluminium block of about 50 x 50 x 10 mm (V1);"),
        ("ten type K thermocouples with plugs to suit it; a second 15 V, 7 A supply if the patch runs are to keep the heaters on;",
         "ten type K thermocouples with plugs to suit it;"),
        ("and under the lid gasket with the lid closed, each on a straight run of the seal;",
         "and under the lid gasket with the lid closed, each on a straight run of the seal, the thermostat chain's two wires\n"
         "  each on a run of its own at least 50 mm from the other and from every heater lead;"),
    ])
    edit(OD + "README.md", [
        ("a 500 mm caliper and a hot plate or hot-air gun if they can be borrowed.",
         "a 500 mm caliper and a\n   hot-air gun if they can be borrowed."),
    ])
    edit(OD + "CHECKOUT-LIST.md", [
        ("heat-resistant matt black paint rated to 200 C or more (H2) |",
         "heat-resistant matt black paint rated to 200 C or more (H2); eight 6.3 x 0.8 mm receptacles for the thermostats' tabs "
         "(the two at TS4 uninsulated or rated for 150 C or more); aluminium tape rated for 150 C or more; a short DIN rail or a "
         "panel for the two 95.05 sockets; a meter or clamp ammeter rated for 6 A continuous in the heater lead |"),
    ])
    edit(OD + "checks/check-1.md", [
        ("Full record: `" + "/".join(("", "home", "claude" + "-runner", "worktrees", "meshsat-fieldkit", "_scratch", "chk-od01", "CHECK.md")) + "`. Pages fetched are in `_scratch/chk-od01/pages/`.",
         "Full record: the checker's scratch clone (not filed; its paths generalised on filing, 29 September 2026). Pages\nfetched were kept there."),
        ("I wrote only under `_scratch/chk-od01/`.", "I wrote only in the checker's scratch clone."),
    ])
    for f in ("TEST-PROCEDURE.md", "TEST-BRIEF.md", "README.md", "checks/check-1.md"):
        t = open(os.path.join(TOP, OD, f), encoding="utf-8").read()
        if "/home/" in t or "claude-runner" in t: refuse("%s still holds a user path" % f)
    t = open(os.path.join(TOP, OD, "TEST-PROCEDURE.md"), encoding="utf-8").read()
    for stale in ("flat pair", "S2 STOP/TEST", "S1 START", "second supply is available", "V4 is that"):
        if stale in t: refuse("TEST-PROCEDURE.md still reads %r" % stale)
    print("patch_od01f: the verification block replaced as one text again; B1 to B3 and q1 to q16 answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
