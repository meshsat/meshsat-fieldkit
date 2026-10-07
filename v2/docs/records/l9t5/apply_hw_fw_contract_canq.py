#!/usr/bin/env python3
"""apply_hw_fw_contract_canq.py: DRAFT apply script on v2/docs/HW-FW-CONTRACT.md (Layer 9 record l9t5, Layer 4 task L4A-55, MESHSAT-1357,
7 October 2026, W139). UNAPPLIED: the integrator runs it; this record runs it only on scratch copies.

ROUND 9 (W143, fnd/l4canmb, the same day): the row's text corrected before row (b)'s check, the edits unchanged in number: ES0392's
workaround quoted with its page, the self-test's cycle, phases and precondition worded so that every S phase runs as worded and the
attribution path is exercised (W139-F5, W139-F8), and the latched supervisor's restart rule (W139-F2, apply_gen_sch_b_canen.py).
WHAT IT IS: three edits. FW-B22 (the quorum's schedule) restated on the two fabrics for method M-B (the peers' buffered TXD observation and 2-of-2
SHDN vote, record l9t5 `apply_gen_sch_b_canmb.py`, W137), with its verification item V-B22 restated (round 6's V-B22 tested the
transmit-share limiter, which M-B removes: W137-F6); and FW-B21's stop and V-B21's stop time restated at FW-B22's loss count (the
drafted stop, 'no valid frame for 100 ms', is one window of FW-B22's schedule, so one lost state frame stopped a fabric for a second:
`l9t5_canq.out` row F2, quorum lost; the share, not the stop's delay, bounds each window's fault current, `l9t5_t10.out` 10h (3)). It composes AFTER `apply_hw_fw_contract_t10.py` (which adds FW-B20 to FW-B22 and
V-B20 to V-B23) and refuses a page without them: the tree's page today. A Layer 5 row brought forward as a named prerequisite of the
Layer 4 power gate (the owner's instruction of 5 October 2026, section 4), like t10's.
CON-004 IS RESTATED, NOT AMENDED: the script reads CON-004 in REQUIREMENTS-TRACE.md, refuses if its text is not the one below, and
writes nothing to that file. The rows keep CON-004's two independent fabrics, IOHA row 7 and test A7 as accepted.
REASON: the ledger's RE-5 and HO-C (cx46 item 5 NOT CLOSED): FW-B22 as drafted was a traffic model; the quorum's service under every
fault row needs the slots, the decision from either fabric, the attribution rule and the self-test's own segment this row carries
(record l9t5 `l9t5_canq.out` sections 4 to 9).
ACCEPTANCE: V-B22 as restated below; the desk acceptance is `l9t5_canq.out` section 9 (each row's outcome against its required one).
Usage:  apply_hw_fw_contract_canq.py [TARGET] [--check | --write]   (default TARGET: the tree's v2/docs/HW-FW-CONTRACT.md;
        default --check: nothing is written)
Exit 0: checked (or written); 3: refused (t10's rows absent, already applied, an anchor missing or not unique, CON-004 changed, or
the result does not re-parse)."""
import difflib
import os
import re
import sys

NAME = "apply_hw_fw_contract_canq"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = os.path.join(REPO, "v2", "docs", "HW-FW-CONTRACT.md")
TRACE = os.path.join(REPO, "v2", "docs", "REQUIREMENTS-TRACE.md")
CON004 = ("Each I/O supervisor has its own regulator branch, reset supervisor, watchdog, crystal and SWD pads, and the three talk over "
          "two independent CAN-FD fabrics with separate transceivers and termination.")
OLD_B22_START = "| FW-B22 | the quorum's messages on fabrics A and B (CON-004) | In every 100 ms window each supervisor sends on each "
OLD_VB22_START = "| V-B22 | FW-B22 | the frames of 10 s of traffic counted per window and supervisor: at most six, none over 8 data bytes; each "
FW_B22_CANQ = (
    "| FW-B22 | the quorum's messages on fabrics A and B (CON-004, restated, not amended: two independent CAN-FD fabrics, each controller "
    "on both through its own transceiver), with method M-B's observation and vote (record l9t5 `apply_gen_sch_b_canmb.py`, DRAFTED: each "
    "TXD buffered to the other two controllers' TIM3 captures through 2.2 kOhm, twelve 2-of-2 SHDN votes) | In every 100 ms window on "
    "each fabric a controller's frames go only in its own 10 ms slot (A from 10 ms, B from 20 ms, C from 30 ms): one state frame and at "
    "most five event frames, classic frames of at most 8 data bytes; DAR = 1 with ES0392 Rev 15 2.24.5's printed workaround (page 48/73: "
    "'Upon failure, clear the corresponding Tx buffer transmission request bit TRPx of the FDCAN_TXBRP register and set the "
    "corresponding cancellation finished bit CFx of the FDCAN_TXBCF register, then restart the transmission.'), the restart inside its "
    "own slot only. THE SELF-TEST acts only in its own segment, its hold 52 ms to 88 ms with one test frame per controller (A at 60 ms, "
    "B at 70 ms, C at 80 ms), never over a state slot: in window n of a 12-window cycle fabric A's target is A, B or C by (n mod 12) div "
    "4 and fabric B's the next controller, both fabrics at once, and the phase is S, P1, P2 or V by n mod 4 (S: the target's own SHDN "
    "request over the hold, its test frame received by no peer and no peer's received by it; P1, P2: one peer's vote alone over the "
    "hold, every test frame received both ways; V: the target's one malformed test frame of 12 dominant bit-times at the hold's start, "
    "its only frame in that hold, struck by both readers through their attribution paths, their votes acting to the hold's end and the "
    "target receiving no peer's test frame); a fabric's phase runs when in the previous window every controller received every other's "
    "state frame on that fabric, no controller has stopped it, no vote on it is asserted outside the test and all three are "
    "functional, else it is skipped and each controller's published phase counter shows the skip; the restart route's phases ride in "
    "the fabric A target's windows (P1, P2: one peer's restart vote pulsed from 68 ms to 72 ms; V: both; the target reading its "
    "restart gate's output from 66 ms to 74 ms; the verdicts on either fabric); a phase is declared failed on its second consecutive "
    "failure. A "
    "peer's state frame for a window is taken from either fabric and counted only in its sender's slot with its sender's identifier (a "
    "frame carrying another controller's identifier is discarded), two copies that differ discard that peer's state for the window, a "
    "peer is lost after 3 consecutive windows with no valid state frame on either fabric, decisions 2 of 3 as before. ATTRIBUTION: each "
    "controller classifies, within 1 ms and on one time base (TIM3 for its captures and, with FDCAN_TSCC.TSS = 10, for its FDCANs' "
    "timestamps), the TXDs it reads against the frames on the bus (a dominant run over 11 bit-times, edges closer "
    "than half a bit-time, a malformed frame it owns, the first dominant bit where a frame's owner sends recessive outside the ACK slot, "
    "a start of frame outside its slot or over its count), strikes only when its own FDCAN reports a protocol error or loses its "
    "scheduled frame within that frame (never on a TXD reading alone), and on a strike asserts its own vote on that transceiver for 1 s, "
    "doubled for each strike within 10 s of a release, at most 64 s; it never votes on a message received over a fabric. RESTART (the "
    "latched supervisor's EN route, record l9t5 `apply_gen_sch_b_canen.py`, DRAFTED): a controller asserts its restart vote on a peer "
    "for 2 s when it has captured no edge on either of that peer's TXDs and received no state frame of it on either fabric for 2 s, "
    "at most once in 10 s per peer, never on a message received over a fabric; the peer's limiter's EN is pulled low only while both "
    "other controllers vote. A controller "
    "returning from reset or power-off listens in bus monitoring mode for 2 windows and sets its votes and voted outputs to the "
    "read-back before it sends | record l9t5 `l9t5_canq.out` (L4A-55): the quorum under IOHA rows 3, 5, 7 and 8 and M-B's vote-path "
    "faults; record l9t5 `l9t5_canmb.out` section 7 and record l4canen (round 9, the self-test and the restart route); RM0433 Rev 8 "
    "pp.2469, 2470, 2529, 2530, 2532 to 2535; ES0392 Rev 15 2.24.5 (page 48/73); SLLSEQ7F 5.6 and Table 6-5; SLVS841F 7.3 and 7.5 | "
    "V-B22 | OWED (DRAFTED, "
    "record l9t5 L4A-55; PROVISIONAL until independently checked) |\n")
V_B22_CANQ = (
    "| V-B22 | FW-B22 | the frames of 10 s of traffic counted per window, slot and controller: none outside its slot, at most six, none "
    "over 8 data bytes; each controller's TX pin in turn driven as a GPIO (held low; toggled at the bit rate; toggled once a window into "
    "a peer's state frame), on one fabric and then on both: its transceivers' SHDN reads high within `l9t5_canq.out` section 4's figure "
    "and the other two never miss each other for 3 windows; fabric A and then fabric B shorted and cut at A7's links with the self-test "
    "running: no controller voted off; each latent fault of `l9t5_canq.out` section 7 injected: found within its bound; each "
    "controller's restart route with the self-test running: its P1, P2 and V pulses read at the target as low, low and high, and each "
    "latent fault of record l4canen's route table injected: found within its bound; one supervisor's limiter latched by an over-limit "
    "load and restarted by its two peers within record l4canen's recovery bound, and with one peer's restart vote held asserted the "
    "supervisor never switched off; the times read "
    "and reported (MODEL figures until then) |\n")
FW_B21_OLD = "or with a frame pending and no valid frame for 100 ms, is stopped at once (INIT kept set)"
FW_B21_NEW = ("or with a frame pending and no valid frame for more than 3 windows (300 ms, FW-B22's loss count; frames lost to a deviation the "
              "peers attribute and silence do not stop it), is stopped at once (INIT kept set)")
VB21_OLD = "the supervisors stop the faulted fabric within 100 ms, its transceivers' SHDN reads high"
VB21_NEW = "the supervisors stop the faulted fabric within 400 ms (FW-B22's loss count and a slot), its transceivers' SHDN reads high"
CHANGE = ("| 3 (L4A-55) | 7 October 2026 | By record l9t5's Layer 4 task L4A-55 (MESHSAT-1357, `records/l9t5/T10-CANQ.md`, "
          "`apply_hw_fw_contract_canq.py`), after `apply_hw_fw_contract_t10.py`: FW-B21's stop at FW-B22's loss count (V-B21 with it), FW-B22 restated on the two fabrics for method M-B (slots, "
          "the decision from either fabric, the loss count, the attribution rule, the self-test's own segment, DAR = 1 with ES0392 "
          "2.24.5's workaround) and V-B22 restated (round 6's limiter removed by M-B), with L4A-54's round 9 corrections by W143 (the "
          "workaround quoted with its page, the self-test's cycle, phases and precondition worded, the restart route's rule); CON-004 "
          "restated, not amended; OWED (DRAFTED) |\n")


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def rows(text, prefix, cells):
    out = []
    for line in text.splitlines():
        if line.startswith(prefix):
            parts = line.strip().strip("|").split(" | ")
            if len(parts) != cells:
                refuse("a row %s carries %d cells, not %d" % (line[:20], len(parts), cells))
            out.append(parts[0].strip())
    return out


def con004_as_written():
    t = open(TRACE, encoding="utf-8").read()
    m = re.search(r"^\*\*CON-004\*\* \(constraint\)\. (.+)$", t, re.M)
    if not m or m.group(1) != CON004:
        refuse("CON-004 in REQUIREMENTS-TRACE.md is not the text this draft restates")


def patched(text):
    if "| 3 (L4A-55) |" in text or FW_B22_CANQ.strip() in text:
        refuse("the change is already applied")
    b22 = [l for l in text.splitlines(True) if l.startswith(OLD_B22_START)]
    vb22 = [l for l in text.splitlines(True) if l.startswith(OLD_VB22_START)]
    if len(b22) != 1 or len(vb22) != 1:
        refuse("apply_hw_fw_contract_t10.py's FW-B22 and V-B22 are not each in the file once (apply it first)")
    # W159 on W151-F3 (W157-F8): HO-E's apply_hw_fw_contract_hoe.py (fnd/l4hoe, L4A-59) also refuses unless t10's change record is
    # the page's last row and appends its own; this script now takes either as the last row, so the two apply in the order t10, hoe,
    # canq (hoe's own guard cannot take canq's row after t10's: that order is the only one both admit; test_l9t5_rowb)
    if not text.endswith("\n") or not text.rstrip("\n").splitlines()[-1].startswith(("| 2 (T10, P0) ", "| 2 (HO-E, P0) |")):
        refuse("neither t10's nor HO-E's change record is the file's last row")
    hoe = "| FW-B23 |" in text
    new = text
    for old, rep in ((b22[0], FW_B22_CANQ), (vb22[0], V_B22_CANQ), (FW_B21_OLD, FW_B21_NEW), (VB21_OLD, VB21_NEW)):
        if rep == old or new.count(old) != 1:
            refuse("an anchor is not unique or its new text equals the old: %r" % old[:50])
        new = new.replace(old, rep)
    new = new + CHANGE
    if new == text:
        refuse("the result does not differ")
    if rows(new, "| FW-B", 6) != ["FW-B%02d" % i for i in range(1, 24 if hoe else 23)]:
        refuse("the FW-B rows do not read FW-B01 to FW-B22 (FW-B23 with HO-E's) in order")
    if rows(new, "| V-B", 3) != rows(text, "| V-B", 3):
        refuse("the V-B rows changed in number or order")
    if rows(new, "| 3 (L4A-55) |", 3) != ["3 (L4A-55)"]:
        refuse("the change record row does not parse")
    if re.search("[" + chr(0x2013) + chr(0x2014) + "]", FW_B22_CANQ + V_B22_CANQ + CHANGE + FW_B21_NEW + VB21_NEW):
        refuse("a long dash in the new text")
    return new


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) > 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    con004_as_written()
    target, write = (args[0] if args else TREE), flags == ["--write"]
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/HW-FW-CONTRACT.md", "b/HW-FW-CONTRACT.md", n=0))
    if not write:
        print("%s: CHECK OK, 5 edit(s), nothing written" % NAME)
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or rows(back, "| FW-B", 6)[-1] not in ("FW-B22", "FW-B23") or FW_B22_CANQ.strip() not in back:
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN, 5 edit(s)" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
