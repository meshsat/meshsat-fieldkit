#!/usr/bin/env python3
"""apply_l5r3.py: Layer 5's third round on the panel's contract (MESHSAT-1357, 3 October 2026). The Layer 5 author owns PANEL.md,
ASSEMBLY.md and HW-FW-CONTRACT.md for this round, so this script was RUN ONCE on the tree by that author and is kept beside the
record as the exact statement of the change; a second run refuses.

What it writes (L5-PANEL-R3.md gives each decision's evidence and reason):
  PANEL.md            the panel firmware's findings F-04 to F-13 resolved in place (the expander order, NVG against the TX lamp's
                      floor, the lamp test's chirp, the slot fault's indicator, the e-paper pacing, the operator's retry, the margin
                      hold's SOS text, the HDMI select encoding); record l8r2's PI button texts in sections 1, 4 and 5 (DRAFTED,
                      PROVISIONAL); a new section 9a with the firmware's session choices adopted into the contract, with credit, and
                      those not adopted with their reason.
  HW-FW-CONTRACT.md   FW-C03's PI input (l8r2, PROVISIONAL), FW-C14's start-up read (F-10), FW-C15's SOS text (F-12), FW-D01's
                      boot levels (F-11), FW-C06's encoding pointer (F-13); a section 3.8 binding the adopted choices to their rows;
                      the change record.
  ASSEMBLY.md         line 127, the PI button's lead row (l8r2, PROVISIONAL).

Usage:  apply_l5r3.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must not occur yet; every table row keeps its table's cell count;
no em or en dash. Exit 0: checked (or written); 3: refused."""
import difflib
import os
import re
import sys

NAME = "apply_l5r3"
PI_TRIG = "PROVISIONAL until l8r2's apply_gen_sch_c_pibtn.py is released and board C regenerated"
L8R2 = "record l8r2 at `29ffb518` (section 3d, copied into `records/l5r2/inputs/`)"
R3 = "record l5r2, `L5-PANEL-R3.md`"


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


PANEL_EDITS = [
    ("`SW_PI` (16 mm, lead pads `PIJ2_A/B`)",
     "`SW_PI` (16 mm, lead pads `PIJ2_A/B`; as generated read by no controller pin, the panel firmware's F-01; DRAFTED by %s, "
     "%s: read by U1 P1.3)" % (L8R2, PI_TRIG)),
    ("| 3 | CHARGING (white, `D10`) | SPARE1 (test point) |",
     "| 3 | CHARGING (white, `D10`) | SPARE1 (test point), as generated; DRAFTED by %s, %s: PI_BTN_n, the PI button, low = pressed "
     "(PIJ2_A2; R57 10 k to +3V3, C27 100 nF to GND, tau 1.0 ms); raises EXP_INT on a change; the SPARE1 test point becomes the "
     "button's |" % (L8R2, PI_TRIG)),
    ("On boot the firmware first writes the configuration registers so every LED bit is an input, then the output registers to 0, "
     "then enables outputs one by one.",
     "On boot the firmware writes the output registers to 0 first (every LED bit is still an input at power-up, so nothing lights), "
     "then the configuration registers with every LED bit an input, then enables outputs one by one; every configuration write is "
     "preceded by an output write, the rule of every expander (section 5, HW-FW-CONTRACT.md FW-A08 and section 3.8). Decided 3 "
     "October 2026 (finding F-04 of the panel firmware, %s): this sentence ordered the configuration first, against section 5 and "
     "FW-A08; both orders are safe on U1 and U2, so the one rule stands." % R3),
    ("then leaves it off until the operator acts.",
     "then leaves it off until the operator acts: from the touch UI, by a retry command over the bridge protocol (owed with "
     "MESHSAT-837; the panel firmware's F-02 and S-04), or by restarting the kit with MAIN, after which every slot is raised again "
     "(decided 3 October 2026, F-09, %s: the sentence named no control)." % R3),
    ("with the panel absent B's `R15`/`R16` (10 k) hold both selects low, slot 1.",
     "with the panel absent B's `R15`/`R16` (10 k) hold both selects low, slot 1. **The encoding** (F-13, read from `gen_sch_b.py` "
     "lines 1342 to 1348 with TI SCDS343F Table 1: `U3` passes slot 1 or 2 by `HDMI_SEL1`, `U4` passes `U3`'s output or slot 3 by "
     "`HDMI_SEL2`): slot 1 = both selects low; slot 2 = `HDMI_SEL1` high, `HDMI_SEL2` low; slot 3 = `HDMI_SEL2` high (`U4` then "
     "passes slot 3 whatever `HDMI_SEL1` is; the controller drives `HDMI_SEL1` low). With every slot dark the selection stays where "
     "it was (the firmware's S-31)."),
    ("hold 8 s = `PI_KILL`.",
     "hold 8 s = `PI_KILL` (read on U1 P1.3, PI_BTN_n, at every EXP_INT and the once-a-second poll: DRAFTED by %s, %s; as "
     "generated no controller pin reads the button, the panel firmware's F-01)." % (L8R2, PI_TRIG)),
    ("The TX lamp is never dimmed below 10 % duty; in BLACKOUT it is dark like everything else (EMCON sits next to it for that case).",
     "The TX lamp follows the panel's duty in every position (DAY 100 %%, NIGHT 15 %%, NVG 2 %%); in BLACKOUT it is dark like "
     "everything else (EMCON sits next to it for that case). Decided 3 October 2026 (F-05, %s): this sentence set a 10 %% floor, "
     "which bites only in NVG, and the TX lamp `D3` shares `LED_RAIL` behind `Q1` with every panel LED (section 1), so the floor "
     "would raise every lit red and amber LED to 10 %% during a key-down, against `CONOPS.md` section 4's NVG row (the panel at "
     "2 %%) and its NVIS target (section 7a); CONOPS decides the behaviour. Both LIGHTING inputs low, which a sound toggle cannot "
     "give, is read as NIGHT (fail dim) and reported (the firmware's S-13)." % R3),
    ("(SOS active, ZEROIZE armed, thermal trip, pack under-voltage, slot fault)",
     "(SOS active, ZEROIZE armed, thermal trip, pack under-voltage, two compute modules lost; decided 3 October 2026, F-07, %s: "
     "this list named a slot fault, which section 5 and the amber list give MASTER CAUT; `CONOPS.md` section 4e gives one module "
     "lost MASTER CAUT and two lost MASTER WARN)" % R3),
    ("for 3 s, a chirp, the battery bar after",
     "for 3 s, a double chirp (F-06: this sentence said a chirp, the sounder patterns below a double chirp; the double chirp is "
     "taken, so the lamp test is told from an acknowledge), the battery bar after"),
    ("refresh at most once a minute, full refresh once an hour and after ZEROIZE;",
     "a change of page refreshes at once and the idle page's content at most once a minute (decided 3 October 2026, F-08, %s: the "
     "minute had delayed the QR's removal and the SOS and ZEROIZE pages; the firmware's S-16), full refresh once an hour and after "
     "ZEROIZE; the panel's own least interval between refreshes is stated by none of PDi's held documents (the E2370KS0C1 flyer, "
     "the driving note rev 02, the UC8253C sheet), owed to Layer 6 (PDi's statement);" % R3),
    ('"SOS QUEUED: EMCON ON, OPEN EMCON TO SEND".',
     '"SOS QUEUED: EMCON ON, OPEN EMCON TO SEND". Queued under the margin hold (HW-FW-CONTRACT.md FW-C15): `D4` keeps flashing, '
     'nothing transmits, and the e-paper shows "SOS QUEUED: MARGIN HOLD, COOLING" (decided 3 October 2026, F-12, the firmware\'s '
     'S-12: the EMCON text would ask the operator for the wrong action).'),
    ("double chirp (lamp test)", "double chirp, 50 ms on, 100 ms off, 50 ms on (lamp test; the firmware's S-15)"),
]
SEC9A = """## 9a. Values the contract takes from the panel firmware (3 October 2026, record l5r2 round 3)

The panel firmware's author (branch `fnd/fw-panel` at `42c27369`, `v2/firmware/panel/README.md` section 6, copied into
`v2/docs/records/l5r2/inputs/`) took 36 session choices where this page and the contract left the firmware a choice. Those that are
the contract's matter (an operator-visible behaviour, a timing another board or the bridge relies on, a boot or default level) are
adopted here with credit, so the firmware and the contract agree; `HW-FW-CONTRACT.md` section 3.8 binds the ones that belong to an
FW row. Each is the firmware's choice, taken under the owner's standing rule of 26 September 2026 and adopted by the session (Layer 5,
`L5-PANEL-R3.md`); each is reversed as its own row says.

| Choice | Adopted as | Where it binds |
|---|---|---|
| S-01 | every hold time (TEST 2 s and 5 s, SOS 2 s, ZEROIZE 5 s, PI 8 s) runs from the debounced edge, never shorter than stated | section 9 |
| S-02 | MASTER WARN and MASTER CAUT flash at 4 Hz (inside 3 to 5 Hz); the low battery LED at 2 Hz | section 9 |
| S-03 | the slots are raised 1 s apart | section 5's boot order; FW-C01 step 6 |
| S-04 | the operator's retry of a faulted slot is a command over the bridge protocol (F-09) | section 5 |
| S-05 | a clean shutdown waits at most 60 s for the heartbeats, then PI_KILL | FW-C03 |
| S-06 | "no host" is no bridge session: the panel cannot tell a module without its bridge from no module | section 9's SOS indications |
| S-12 (one text) | "SOS QUEUED: MARGIN HOLD, COOLING" (F-12); the firmware's other texts (IDLE, ENROLMENT QR, SOS SENT, the secure element's absence, EMCON ON) stay the firmware's wording | section 9; FW-C15 |
| S-13 | both LIGHTING inputs low is read as NIGHT (fail dim) and reported | section 8 |
| S-14 | battery LED k is lit above 20 x (k - 1) percent | section 9 |
| S-15 | the double chirp is 50 ms on, 100 ms off, 50 ms on; the incomplete pulses 200 ms apart | section 9's sounder patterns |
| S-16 | a change of page refreshes at once (F-08) | section 9 |
| S-21 | after a complete wipe the slots power again when the ZEROIZE toggle returns (`feasibility/ZEROIZE.md` 3.5's re-armed row) | section 9; FW-C04 |
| S-22 | the lamp test fires at 2 s on the way to a 5 s QR hold | section 9 |
| S-23 | NVG's red-and-amber rule applies to the lamp test | sections 8 and 9 |
| S-24 | the sounder sounds in DAY, NIGHT and NVG; ACK mutes the SOS and ZEROIZE-incomplete patterns until the condition rises again | sections 8 and 9 |
| S-25 | ZEROIZE arming and incomplete force MASTER WARN to flash, complete forces it steady, whatever the ACK | section 9 |
| S-31 | with every slot dark the display selection stays where it was | section 5; FW-C06 |
| S-33 | a TEST, SOS or PI switch already closed at power-up counts its hold from the controller's start: an SOS toggle left closed arms SOS 2 s after boot | section 9 |
| S-34 | no slot is newly raised while ZEROIZE is armed (the 5 s) or wiping; a running slot is left to the wipe's step 6 | section 9; FW-C04 |

Bound in `HW-FW-CONTRACT.md` section 3.8 only (FW rows): S-07, S-08, S-09, S-10, S-17, S-18, S-20, S-26, S-27, S-28, S-29, S-32,
S-35 and S-36's definition of a reading. **Not adopted, with the reason:** S-11 (board D's U16 written 0 at boot: it would hold the
SA868 powered down; FW-D01 takes the generator's power-up levels instead, F-11); S-19 (after H1 only the heat stage's module until
the next start: the firmware's interim while FW-C09's restore is unimplemented; the contract's restore 5 K below stands); S-30 (the
EXP_INT service and LED retry intervals: internal to the firmware); S-36's polling period and the VEML7700's gain (internal).

"""
HWFW_EDITS = [
    ("(`C:J_PIJ2`, short press)",
     "(`C:J_PIJ2` as generated, read by no controller pin, the panel firmware's F-01; DRAFTED: `C:U1` P1.3 (PI_BTN_n) by %s, %s; "
     "short press)" % (L8R2, PI_TRIG)),
    ("at 5 Hz, raise no slot until it is back at 1 Hz",
     "at 5 Hz, enter H1 with the stop dated at the start-up and raise no slot until the line is back at 1 Hz and 30 minutes have "
     "passed, FW-C13's exit (decided 3 October 2026, F-10, %s: this row's 'back at 1 Hz' alone would let a restart shorten the hot "
     "stop's 30 minutes; the firmware's S-18)" % R3),
    ("queued as under EMCON (D-10) and the operator told",
     "queued as under EMCON (D-10) and the operator told, the e-paper showing \"SOS QUEUED: MARGIN HOLD, COOLING\" (F-12, the "
     "firmware's S-12; `PANEL.md` section 9)"),
    ("| Outputs before configuration; the PTT and KEY states are read-backs only (the KEY gate is hardware) |",
     "| Outputs before configuration, at the levels the generator designs at power-up so the change of direction moves no line: "
     "X_SA_PD 1 (the exciter on and receiving, `gen_sch_d.py`: 'PD from the expander (default on)'), X_AMP_EN 1 (the headset "
     "amplifier as at power-up through its level stage's 10 k pull-up), X_MMUTE 0 (the codec's mute off, the defined default of "
     "`gen_sch_d.py`'s R33 and R34); the PTT and KEY states are read-backs only (the KEY gate is hardware). Decided 3 October 2026 "
     "(F-11, %s): the row stated no boot level; the firmware's S-11 (all 0) is not adopted, since it would hold the SA868 powered "
     "down against `CONOPS.md` section 4's 'the VHF path keeps listening' |" % R3),
    ("| Follow the bridge's display owner; with no instruction select the lowest slot with a live heartbeat; never select a dark slot |",
     "| Follow the bridge's display owner; with no instruction select the lowest slot with a live heartbeat; never select a dark slot; "
     "the encoding (slot 1 both low, slot 2 HDMI_SEL1 high, slot 3 HDMI_SEL2 high) is `PANEL.md` section 5's (F-13); with every slot "
     "dark the selection stays (S-31) |"),
]
SEC38 = """### 3.8 Values adopted from the panel firmware (3 October 2026, record l5r2 round 3)

The panel firmware's session choices (branch `fnd/fw-panel` at `42c27369`, `v2/firmware/panel/README.md` section 6, copied into
`records/l5r2/inputs/`) that fix a value an FW row left open are adopted here with credit; `PANEL.md` section 9a carries the
operator-visible ones and the choices not adopted, with their reasons.

| Row | Adopted value | Firmware choice |
|---|---|---|
| in FW-C01 step 6 | the slots raised 1 s apart | S-03 |
| in FW-C02 | the watchdog's period 1 s (over the 235 ms worst GenKey); pico-sdk's `runtime_init_early_resets()` resets IO_BANK0 and PADS_BANK0 on every boot, so the firmware overrides it to keep the reset scope (the firmware's finding F-03; whether the PSM's RESETS bit must also be cleared is INFERRED, read at V-C02) | S-09 |
| in FW-C03 | a clean shutdown waits at most 60 s for the heartbeats; the controller's own pull on PI_SHDN_REQ, and 5 ms after it, is never read as a MAIN tap | S-05, S-29 |
| in FW-C04 | no slot newly raised while ZEROIZE is armed or wiping; after a complete wipe the slots power again when the toggle returns; an absent secure element retried every 60 s | S-34, S-21, S-35 |
| in FW-C06 | with every slot dark the selection stays where it was | S-31 |
| in FW-C09 | the pack readings' 10 s fallback starts only after the readings were seen once; with no bridge every switched load stays off | S-26, S-27 |
| in FW-C13 | H2 drives PI_KILL once its page is shown or after 30 s; "two readings in a row" of the TMP117 are two conversions (Data_Ready) | S-08, S-36 |
| in FW-C14 | HOT-R1 classified as 5 Hz on five or more edges in 2 s, held after 3 s without an edge, 1 Hz only after 2 s of samples; decided only on reads at most 1.5 s old (1.5 to 3 s keeps the last verdict, over 3 s is the detector lost); unreadable at start-up = held high; a 5 Hz line at start-up enters H1 (F-10); every EXP_INT service reads every input expander and writes the command byte to each | S-07, S-32, S-17, S-18, S-28 |
| in FW-C15 | the margin reference's offset 0 until T-H1 calibrates it (PROVISIONAL with the row) | S-20 |
| in FW-A08 | every configuration write preceded by an output write (an expander reset by a brownout returns to FFh) | S-10 |
| in FW-D01 | not adopted: S-11 (all 0); the generator's power-up levels instead (F-11) | S-11 |

"""
H_LOG = ("| 2 (L5-R3) | 3 October 2026 | By Layer 5's third round (MESHSAT-1357, `records/l5r2/`, `L5-PANEL-R3.md`): FW-C03's PI input "
         "(record l8r2, DRAFTED, PROVISIONAL), FW-C14's start-up read (F-10), FW-C15's SOS text (F-12), FW-D01's boot levels (F-11), "
         "FW-C06's encoding (F-13); section 3.8 binds the panel firmware's adopted session choices with credit |")
ASM_OLD = "C7 `J_PIJ2` lands (the panel controller reads it; nothing leaves the backer)"
ASM_NEW = ("C7 `J_PIJ2` lands (the panel controller reads it on U1 P1.3; nothing leaves the backer; DRAFTED by record l8r2 at `29ffb518`, "
           "%s; as generated no controller pin reads it, the panel firmware's F-01)" % PI_TRIG)


def cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def tables_ok(text):
    width = None
    for l in text.split("\n"):
        c = cells(l)
        if c is None:
            width = None
            continue
        if width is None:
            width = len(c)
        elif len(c) != width and not all(x.strip("-") == "" for x in c):
            refuse("a table row has %d cells under a header of %d: %s" % (len(c), width, l[:70]))


def exact(t, edits):
    for old, rep in edits:
        if t.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (t.count(old), old[:70]))
        if rep in t:
            refuse("already applied: %r" % rep[:70])
        t = t.replace(old, rep)
    return t


def patch_panel(t):
    if "## 9a. Values the contract takes from the panel firmware" in t:
        refuse("already applied")
    t = exact(t, PANEL_EDITS)
    anchor = "## 10. Shore charge inhibit and the pack\n"
    if t.count(anchor) != 1:
        refuse("section 10's heading is not where it was")
    t = t.replace(anchor, SEC9A + anchor)
    tables_ok(t)
    return t


def patch_hwfw(t):
    if "### 3.8 Values adopted from the panel firmware" in t:
        refuse("already applied")
    t = exact(t, HWFW_EDITS)
    anchor = "## 4. What round 8 changes in these rows\n"
    if t.count(anchor) != 1:
        refuse("section 4's heading is not where it was")
    t = t.replace(anchor, SEC38 + anchor)
    lines = t.split("\n")
    k = len(lines) - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    if not (cells(lines[k]) or [""])[0].startswith("2 (L5-R2)") or len(cells(H_LOG)) != len(cells(lines[k])):
        refuse("the change record's last row is not round 2's")
    lines.insert(k + 1, H_LOG)
    t = "\n".join(lines)
    tables_ok(t)
    seen = set()
    for l in t.split("\n"):
        c = cells(l)
        if c and re.match(r"^(FW|V)-[A-Z]\d\d$", c[0]):
            if c[0] in seen:
                refuse("row %s occurs twice" % c[0])
            seen.add(c[0])
    return t


def patch_assembly(t):
    if ASM_NEW in t:
        refuse("already applied")
    t = exact(t, [(ASM_OLD, ASM_NEW)])
    tables_ok(t)
    return t


KINDS = {"PANEL.md": patch_panel, "HW-FW-CONTRACT.md": patch_hwfw, "ASSEMBLY.md": patch_assembly}


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    fn = KINDS.get(os.path.basename(target))
    if fn is None:
        refuse("TARGET is none of %s" % ", ".join(sorted(KINDS)))
    text = open(target, encoding="utf-8").read()
    new = fn(text)
    if new == text:
        refuse("the result does not differ")
    if chr(0x2014) in new or chr(0x2013) in new:
        refuse("a dash character in the result")
    base = os.path.basename(target)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/" + base, "b/" + base, n=0))
    if not write:
        print("%s: CHECK OK %s, nothing written" % (NAME, base))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    if open(target, encoding="utf-8").read() != new:
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN %s (+%d lines)" % (NAME, base, new.count("\n") - text.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
