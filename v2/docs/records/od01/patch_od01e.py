#!/usr/bin/env python3
"""The integrator's answers to the independent check 5 of the OD-01 package (MESHSAT-1357, 29 September 2026; the check is
`checks/check-5.md`). A change of method after five rounds: the checks kept finding a defect the previous correction had
made in the shutdown's verification, because each correction replaced single lines. This script instead replaces the whole
verification block of TEST-PROCEDURE.md section 3 (V1 to V4, what they show and what they do not, the residual risk) as one
text, and every step of sections 5 and 6 that refers to V3 or V4 with it. B1 (V4's STOP/TEST press after a supply cycle
proved nothing, and section 5.1 still defined V4 as that press), p1 to p9 answered; p10: the log's box paths are
generalised, and `patch_od01d.py` is left as it ran (it is the record of its run). H1's MANIFEST is rewritten by
`v2/cad/case_manifest.py` itself. Every old text asserted exactly once; refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OD = "v2/docs/records/od01/"
H1 = "v2/release/case-2026-09-27/h1-heat-test-plate"
DASHES = ("—", "–")


def refuse(m):
    print("patch_od01e: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    if t.count(old) != 1: refuse("%s: expected once, found %d: %r" % (where, t.count(old), old[:70]))
    if any(d in new for d in DASHES): refuse("%s: a dash character in the new text" % where)
    return t.replace(old, new)


def edit(path, pairs, fn=None):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = t
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if fn: t2 = fn(t2)
    if t2 == t: refuse("%s unchanged" % path)
    if any(d in t2 for d in DASHES): refuse("%s: a dash character" % path)
    open(p, "w", encoding="utf-8").write(t2)


VERIFY = """**Verification (before the case is heated, each result recorded in `checks.csv`; what it shows and what it does not is
stated after V4):**
- **V1, each thermostat alone.** Clamp it cap-down on an aluminium block of about 50 x 50 x 10 mm with one thermocouple
  taped beside it, on a hot plate (or under a hot-air gun held 20 cm off). Multimeter on its terminals (continuity). Warm
  at no more than 2 K per minute over the last 15 K. Record the block temperature when it opens and, cooling, when it
  closes. **Pass:** TS1 opens between 84 and 96 C; TS2 and TS3 between 57 and 63 C; TS4 between 136 and 144 C; each
  closes again on cooling. A part outside its band is rejected, not adjusted.
- **V2, the latch on the bench.** Wire the arrangement on the bench (not in the case) at 12.0 V, the heaters' link block
  open so nothing heats, a multimeter on volts at the link block's input (the load side of K2, after both contacts): it
  reads the supply's volts only while both relays are in.
  (a) START: K1 and K2 pull in (audible), the meter reads 12. STOP/TEST: 0, and it stays 0 when the button is released.
  START again: 12.
  (b) Warm each thermostat in turn with the air gun until it opens: 0; let it cool until it closes: **the meter stays at
  0** until START.
  (c) The series wiring. Supply off, K2's A1 lead off its socket terminal; supply on, hold START: K1 pulls in and the
  meter reads 0 (K2's contact 11-14 is in the heater path); release START: K1 drops (K2's contact 21-24 is in the hold
  path). Supply off, refit the lead, take K1's A1 lead off and repeat: K2 pulls in, the meter reads 0, K2 drops on
  release. Supply off, refit the lead.
  **Pass:** every action behaves so.
- **V3, in place.**
  (a) With each thermostat fixed at its place, H1 lifted and the link block open (nothing heats): START, the meter at the
  link block reads 12. Disconnect one lead at each thermostat in turn: the meter falls to 0 and stays 0 when the lead is
  refitted, until START, which is pressed before the next thermostat.
  (b) With H1 screwed on and the leads out under the seal, the link block still open: START, 12; STOP/TEST, 0, and it
  stays 0 on release; START, 12. Then warm H1's top face over TS3 (X 0, Y -99) with the air gun held 20 cm off, a
  thermocouple taped to H1's top beside the spot: the meter falls to 0 before that thermocouple reads 70 C (if it does
  not, stop the gun: V3 has failed). Let H1 cool: the meter stays 0 until START.
  **Pass:** every action behaves so.
- **V4, before every step and after each lid change.**
  (a) With the heaters on (the step just ended; before S1, after a START with the link block set for S1), press
  STOP/TEST: the heater current falls to zero and stays zero when the button is released.
  (b) Switch the supply off. A continuity check reads open across each relay's contacts 11-14 and 21-24 (four readings)
  and across START (S1): no contact has welded and START has not stuck.
  (c) With the supply still off, set the link block and the lid for the next step. Supply on, START: the heater current
  returns. Record the time.

**What the verification shows, and what it does not.** V1 shows each thermostat's opening temperature before it is
mounted. V2 shows the latch, its reset only by START, and both relays' contacts in series in the heater path and in the
hold path. V3 shows each installed thermostat in the chain, the chain intact with H1 closed (through the flat pair under
the seal: a short between its two conductors would bypass all four thermostats and the meter would stay at 12), and TS3
opening on heat in its place. V4 shows, before each step, that STOP/TEST drops both relays, that no relay contact has
welded and that START has not stuck. **Not shown in place:** that TS1, TS2 and TS4 still open on heat after mounting.
V1 proved each before it; the M3 through TS1's bracket and the tape on TS2 and TS4 do not load the disc (INFERRED);
heating them in place would heat the case, which is the test itself. The stop limits of section 8 stay the second line.

**Residual risk with this arrangement:** one relay's contact welding closed no longer leaves the heaters on through a
trip: the other relay's contact, in series, still opens (a second relay, about EUR 9 with its socket). Likewise one
relay's self-hold contact 21-24 welding no longer makes the latch reset by itself: the other's, in series in the hold
path, opens, so the heaters stay off after a trip. START sticking closed during a step would let the heaters cycle on the
thermostats, which still hold every temperature they sit at; V4 reads START open before every step. Both contacts of one
pair welding in the same step would defeat the latch; V4 reads each contact on its own before every step. A step started
without V4, or with any of V1 to V3 failed, is an attended step.
"""


def procedure(t):
    i = t.index("**Verification (before the case is heated, and each result recorded in `checks.csv`):**")
    j = t.index("\n## 4. Test A set-up")
    if t.count("**Verification (before the case is heated") != 1: refuse("procedure: the verification block")
    return t[:i] + VERIFY + t[j:]


def main():
    if os.path.exists(os.path.join(TOP, OD, "checks/check-5.md")): refuse("already applied (check-5 filed)")
    edit(OD + "TEST-PROCEDURE.md", [
        ("(0.65 W each at 12 V, about 108 mA together)", "(0.65 W each at 12 V, about 110 mA together: 55 mA each on Finder's 12 V DC coil row)"),
        ("the coils'\n   108 mA is not in the heater reading.", "the coils'\n   110 mA is not in the heater reading."),
        ("and its bracket B203-S's tabs along X:", "and its bracket B203-S's tabs and its two terminals along X:"),
        ("its contact in series with K1's in the heater lead, its coil in parallel with K1's |",
         "its contact 11-14 in series with K1's in the heater lead and its 21-24 in series with K1's in the hold path, its coil in parallel with K1's |"),
        ("Changing the power:\nSTOP/TEST, change the link block outside the case, START (V4 is that STOP/TEST). Changing the lid: STOP/TEST, open or\n"
         "close it, check the leads still lie flat on a straight run of the gasket, START.",
         "Between steps V4 (section 3)\nruns in full: its STOP/TEST with the heaters on, the contacts and START read with the supply off, the link block (the\n"
         "power) and the lid set for the next step while the supply is off, then START. After a lid change, check before START\n"
         "that the leads still lie flat on a straight run of the gasket."),
        ("- V4 at the start. Record `start_utc`, the volts at the entry and the amps after K1,",
         "- V4 (section 3) at the start. Record `start_utc`, the volts at the entry and the amps after K2,"),
        ("Refit H1 on the frame with its\n   ten screws, the leads out under the seal as before, and repeat V3 before any heating.",
         "Before H1 is refitted, repeat V3\n   (a) with the HS100 in place; refit H1 on the frame with its ten screws, the leads out under the seal as before, and\n"
         "   repeat V3 (b) before any heating."),
    ], procedure)
    edit(OD + "CHECKOUT-LIST.md", [
        ("(about 108 mA, 54 mA each)", "(about 110 mA, 55 mA each on Finder's 12 V DC coil row)"),
    ])
    edit(OD + "TEST-BRIEF.md", [
        ("and at the start of every step each relay contact is read open with the supply off and STOP/TEST is pressed (V4).",
         "and before every step STOP/TEST is pressed with the heaters on, then each relay contact and START are read open with\n  the supply off (V4)."),
    ])
    edit(OD + "README.md", [
        ("page CL-4 gives S-M3-2", "page CL-5 gives S-M3-2"),
        ("| `checks/check-1.md`, `checks/check-2.md` | The two independent AI checks of 28 September (the lead exit's bias under 1 percent and H2's size rest on check-2) |\n",
         "| `checks/check-1.md`, `checks/check-2.md` | The two independent AI checks of 28 September (the lead exit's bias under 1 percent and H2's size rest on check-2) |\n"
         "| `checks/check-3.md` to `checks/check-5.md` | The independent AI checks of 29 September of this revision, each answered by the patch the log names |\n"),
        ("| `patch_rfq_od01b.py`, `patch_checkout_od01b.py`, `make_package.py` |",
         "| `patch_rfq_od01b.py`, `patch_checkout_od01b.py`, `patch_od01c.py`, `patch_od01d.py`, `patch_od01e.py`, `make_package.py` |"),
    ])
    # H1's manifest, written by its own tool, then the RFQ's statement of when it was verified
    subprocess.run([sys.executable, "v2/cad/case_manifest.py", H1, "--base", "e0cd5ec1"], cwd=TOP, check=True, capture_output=True)
    r = subprocess.run(["sha256sum", "-c", "--quiet", "MANIFEST.sha256"], cwd=os.path.join(TOP, H1), capture_output=True, text=True)
    if r.returncode: refuse("H1 MANIFEST does not verify")
    now = subprocess.run(["date", "+%H:%M"], capture_output=True, text=True).stdout.strip()
    edit(OD + "MACHINING-RFQ.md", [
        ("(verified on 29 September 2026 at 01:53 CEST, all files OK); its sheet is H1-1.",
         "(written by `v2/cad/case_manifest.py` after its README's last correction and verified on 29 September 2026 at %s CEST,\nall files OK); its sheet is H1-1." % now),
    ])
    edit(OD + "LOG-od01b.md", [
        ("| 03:50 | Independent check 4 of `a6420c37`", "| 03:40 | Independent check 4 of `a6420c37`"),
        ("| 03:55 | `patch_od01d.py`, text only", "| 03:47 | `patch_od01d.py`, text only"),
    ], lambda t: re.sub(r"`/root/od01b[^`]*`", "the box's work directory", t))
    print("patch_od01e: the verification block replaced as one text, sections 5.1, 5.2 and 6 aligned, p1 to p9 answered, the log's box paths generalised; H1's manifest rewritten by its tool at %s" % now)
    return 0


if __name__ == "__main__":
    sys.exit(main())
