#!/usr/bin/env python3
"""apply_l5r4.py: Layer 5's round 4, the panel firmware's finding F-14 decided (MESHSAT-1357, set 29, 3 October 2026; record l5r4,
L5-R4-SLOT-FAULTS.md; authority SESSION, Layer 5's author of the panel contract). It writes one slot-fault rule for a compute module
lost at start-up and one lost while running into v2/docs/PANEL.md section 5 and v2/docs/HW-FW-CONTRACT.md (FW-C05 carries the rule,
FW-C02 keeps a slot left off across a controller reset, V-C05 tests both cases, a change-record row). `CONOPS.md` section 4e (the row
"a compute module lost"), section 3's M5 and section 4's Startup row are the source and are not edited. Its follow-up, the panel
firmware's F-15 and S-37 (fnd/fw-r4 at 8d396dfd): a power-on reset read as CHIP_RESET's HAD_POR set and the watchdog's REASON zero
(RP2040 datasheet 2.12.1, 2.12.7, 4.7.1, Table 548), and the slot record beside the wipe journal, never inside it.

Usage:  apply_l5r4.py [--check | --write] [--panel PATH] [--hwfw PATH]     (default --check; default targets: the tree's)
IDEMPOTENT: every old text present once and no new text yet: --check prints CHECK OK, --write applies; every old text gone and every
new text present: "already applied", nothing written, exit 0; anything else refused, nothing written. After patching: every table
row keeps its table's cell count, the contract's row ids stay unique, the sentences other records and tests read stay present (the
firmware's constants "stays flat for 60 s", "rail off 5 s", "declare it lost after 3 s without an edge"; round 3's F-09 excerpt),
"until the operator acts." (round 3's withdrawn ending) stays absent, and no em or en dash appears. Exit 0: checked, written or
already applied; 3: refused."""
import os
import re
import sys

NAME = "apply_l5r4"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
PANEL = "v2/docs/PANEL.md"
HWFW = "v2/docs/HW-FW-CONTRACT.md"
R4 = "finding F-14 of the panel firmware, record l5r4, SESSION"

PANEL_OLD = (
    "A slot whose heartbeat stays flat for 60 s after its rail came up is shown as a slot fault (MASTER CAUT, the e-paper names the "
    "slot); the controller power-cycles it once (rail off 5 s) and then leaves it off until the operator acts: from the touch UI, by "
    "a retry command over the bridge protocol (owed with MESHSAT-837; the panel firmware's F-02 and S-04), or by restarting the kit "
    "with MAIN, after which every slot is raised again (decided 3 October 2026, F-09, record l5r2, `L5-PANEL-R3.md`: the sentence "
    "named no control).")
PANEL_NEW = (
    "**Slot faults, one rule for a module lost at start-up and one lost while running** (decided 3 October 2026, %s; the source is "
    "`CONOPS.md` section 4e's row \"a compute module lost\", with section 3's M5 and section 4's Startup row: the slot is cycled once "
    "and then left off until the operator acts). A slot is supervised while its `SLOT_EN` is high and the controller has asked "
    "nothing of it: no shutdown on `PI_SHDN_REQ`, no hot stop (FW-C13), no shed to the reduced mode or the heat stage (FW-C09), no "
    "ZEROIZE (section 6). It is lost when its heartbeat has had no edge for 3 s after an edge (FW-C05), or when it stays flat for 60 s "
    "after its rail came up; either way it is shown as a slot fault (MASTER CAUT, the e-paper names the slot). When a supervised "
    "slot's heartbeat has had no edge for 60 s, counted from its rail coming up or from its last edge, whichever is later, the "
    "controller acts on its rail: the first time it power-cycles the slot once (rail off 5 s), which spends the slot's one retry; "
    "the next time, whether the slot stayed flat after its cycle or came back and was lost later, it drops `SLOT_EN` and then leaves "
    "it off until the operator acts: from the touch UI, by a retry command over the bridge protocol (owed with MESHSAT-837; the panel "
    "firmware's F-02 and S-04), or by restarting the kit with MAIN, after which every slot is raised again (decided 3 October 2026, "
    "F-09, record l5r2, `L5-PANEL-R3.md`: the sentence named no control); each of the three re-arms the slot's retry. A controller "
    "reset (watchdog, RUN or SWD) is not an operator act: the controller keeps each slot's spent retry and left-off state beside the "
    "wipe-pending record, in the same flash but never inside its journal (the panel firmware's S-37: `feasibility/ZEROIZE.md`'s "
    "invariant I3 reads a torn journal entry as a pending wipe, so a slot record torn there by a power loss would start a "
    "crypto-erase), and after the reset raises only the slots that state allows (FW-C02). Only a power-on reset of the controller "
    "clears it, with every slot, and the controller reads one as `CHIP_RESET`'s `HAD_POR` set and the watchdog's `REASON` zero "
    "(decided 3 October 2026, finding F-15 of the panel firmware, record l5r4: RP2040 datasheet 2.12.7, `CHIP_RESET` gives the "
    "source of the most recent chip-level reset, and a watchdog reset is not one (2.12.1, 4.7.1), so `HAD_POR` alone still reads 1 "
    "after a power-on followed by a watchdog reset; Table 548, `REASON`: both bits are zero for a hardware reset); a MAIN restart, "
    "a loss of the panel's supply and a brown-out are such resets. A module that restarts on its own (its software, or a restart "
    "the bridge commands) "
    "is not told apart: it is cycled if it shows no edge for 60 s; a bridge message that suspends the supervision for a planned "
    "restart is owed with MESHSAT-837." % R4)

HWFW_EDITS = [
    ("FW-C05",
     "Inputs only, no pad pulls; a slot is alive while its line toggles at 1 Hz; declare it lost after 3 s without an edge; the display "
     "owner is re-elected from the live slots | section 2 | V-C05 | DRAWN |",
     "Inputs only, no pad pulls; a slot is alive while its line toggles at 1 Hz; declare it lost after 3 s without an edge; the display "
     "owner is re-elected from the live slots. Slot faults, one rule for a slot lost at start-up and one lost while running "
     "(decided 3 October 2026, %s; `CONOPS.md` section 4e governs, `PANEL.md` section 5 states it): supervise a slot while its "
     "SLOT_EN is high and no shutdown, hot stop (FW-C13), shed (FW-C09) or ZEROIZE is asked of it; show it as a slot fault when it is "
     "lost (3 s without an edge after an edge, or flat 60 s after its rail came up); at 60 s without an edge, counted from the later "
     "of its rail coming up and its last edge, power-cycle it once (SLOT_EN low 5 s), its one retry; at the next such 60 s drop "
     "SLOT_EN and leave it off until the operator acts (the touch UI, the bridge's retry command, MAIN), each act re-arming the "
     "retry; keep the spent retry and the left-off state beside the wipe-pending record, in the same flash but never inside its "
     "journal (S-37: `feasibility/ZEROIZE.md`'s invariant I3 reads a torn journal entry as PENDING), across a watchdog, RUN or SWD "
     "reset; clear them only on a power-on reset, read as CHIP_RESET HAD_POR set and the watchdog's REASON zero (F-15: RP2040 "
     "datasheet 2.12.7, CHIP_RESET gives the most recent chip-level reset, which a watchdog reset is not, 2.12.1 and 4.7.1; Table "
     "548, REASON: both bits zero for a hardware reset) | section 2; `CONOPS.md` section 3 (M5), section 4 (Startup) and section "
     "4e; REQ-062; F-14, F-15, S-37 | V-C05 | DRAWN; the slot-fault rule FIRMWARE (F-14) |" % R4),
    ("FW-C02",
     "then FW-C01's order applies to every slot read low.",
     "then FW-C01's order applies to every slot read low that FW-C05's slot-fault state allows (a slot left off stays off across a "
     "watchdog, RUN or SWD reset, F-14; only a power-on reset as FW-C05 reads it, HAD_POR set and REASON zero, clears it, F-15)."),
    ("V-C05",
     "| V-C05 | FW-C05, B01 | stop the bridge on one slot: its line stops toggling, the panel declares it lost within 3 s and moves the "
     "display |",
     "| V-C05 | FW-C05, B01 | stop the bridge on one slot: its line stops toggling, the panel declares it lost within 3 s and moves the "
     "display; F-14's rule: with the bridge stopped on a running slot the panel cycles it once (SLOT_EN low 5 s) 60 s after its last "
     "edge; with the bridge kept stopped the slot is left off 60 s after its rail came back, and stays off across a panel watchdog "
     "reset taken after a power-on (CHIP_RESET's HAD_POR still 1, the watchdog's REASON not zero: F-15) and across a RUN reset, and "
     "a power-on clears it; a slot held flat from its start is cycled 60 s after its rail came up and left off the same way; the "
     "touch UI's retry, the bridge's retry and MAIN each raise it again with its retry re-armed |"),
]
LOG_AFTER = "| 2 (L5-PWR, set 28) |"
LOG_ROW = ("| 2 (L5-R4) | 3 October 2026 | By Layer 5's round 4 (MESHSAT-1357, `records/l5r4/`): the panel firmware's finding F-14 "
           "decided: FW-C05 carries one slot-fault rule for a slot lost at start-up and one lost while running (`PANEL.md` section 5 "
           "states it, `CONOPS.md` section 4e is its source), FW-C02 keeps a slot left off across a controller reset, V-C05 tests both "
           "cases; the follow-up F-15: a power-on reset read as HAD_POR set and the watchdog's REASON zero, and the slot record beside "
           "the wipe journal, never inside it (S-37) |")
KEEP = {PANEL: ["stays flat for 60 s", "rail off 5 s",
                "then leaves it off until the operator acts: from the touch UI, by a retry command over the bridge protocol"],
        HWFW: ["declare it lost after 3 s without an edge"]}
GONE = {PANEL: ["until the operator acts."], HWFW: []}


def refuse(msg):
    sys.stderr.write("%s: %s; refusing, nothing written\n" % (NAME, msg))
    sys.exit(3)


def flat(s):
    return " ".join(s.split())


def cells(line):
    s = line.strip()
    return len(s[1:-1].split("|")) if s.startswith("|") and s.endswith("|") else None


def tables_ok(t, what):
    width = None
    for ln in t.split("\n"):
        c = cells(ln)
        if c is None:
            width = None
            continue
        if width is None:
            width = c
        elif c != width and not all(x.strip("-: ") == "" for x in ln.strip()[1:-1].split("|")):
            refuse("%s: a table row has %d cells under a header of %d: %s" % (what, c, width, ln[:70]))


def ids_unique(t):
    seen = set()
    for ln in t.split("\n"):
        m = re.match(r"^\| ((FW|V)-[A-Z]\d\d) \|", ln)
        if m:
            if m.group(1) in seen:
                refuse("row %s occurs twice" % m.group(1))
            seen.add(m.group(1))


def main(argv):
    mode = "--check"
    paths = {PANEL: os.path.join(REPO, PANEL), HWFW: os.path.join(REPO, HWFW)}
    a = list(argv)
    while a:
        x = a.pop(0)
        if x in ("--check", "--write"):
            mode = x
        elif x in ("--panel", "--hwfw") and a:
            paths[PANEL if x == "--panel" else HWFW] = os.path.abspath(a.pop(0))
        else:
            print(__doc__)
            return 2
    t = {k: open(p, encoding="utf-8").read() for k, p in paths.items()}
    edits = [("PANEL section 5", PANEL, PANEL_OLD, PANEL_NEW)] + [(i, HWFW, o, n) for i, o, n in HWFW_EDITS]
    for i, f, o, n in edits:
        if chr(0x2014) in n or chr(0x2013) in n:
            refuse("%s: a dash in the new text" % i)
    log_present = ("\n" + LOG_ROW + "\n") in t[HWFW] or t[HWFW].endswith("\n" + LOG_ROW)
    state = [(i, t[f].count(o), n in t[f]) for i, f, o, n in edits] + [("change record", 0 if log_present else 1, log_present)]
    if all(c == 0 and h for _i, c, h in state):
        print("%s: already applied (every old text gone, every new text present); nothing written" % NAME)
        return 0
    bad = [(i, c, h) for i, c, h in state if not (c == 1 and not h)]
    if bad:
        refuse("not in the state this script applies to: %s" % "; ".join("%s: old text %d time(s), new text %s" % (i, c, "present" if h else "absent")
                                                                         for i, c, h in bad))
    new = dict(t)
    for i, f, o, n in edits:
        new[f] = new[f].replace(o, n)
    lines = new[HWFW].split("\n")
    k = [j for j, ln in enumerate(lines) if ln.startswith(LOG_AFTER)]
    if len(k) != 1:
        refuse("the change record's row %s is not there once" % LOG_AFTER)
    lines.insert(k[0] + 1, LOG_ROW)
    new[HWFW] = "\n".join(lines)
    for f in (PANEL, HWFW):
        tables_ok(new[f], f)
        if new[f] == t[f]:
            refuse("%s is unchanged" % f)
        if chr(0x2014) in new[f] or chr(0x2013) in new[f]:
            refuse("%s carries an em or en dash" % f)
        ft = flat(new[f])
        for s in KEEP[f]:
            if s not in ft:
                refuse("%s no longer carries %r, which other records and tests read" % (f, s))
        for s in GONE[f]:
            if s in ft:
                refuse("%s carries %r again" % (f, s))
    ids_unique(new[HWFW])
    for i, f, o, n in edits:
        print("%s (%s)\n   old: %s\n   new: %s" % (i, os.path.basename(f), flat(o), flat(n)))
    print("change record (%s)\n   new row: %s" % (os.path.basename(HWFW), LOG_ROW))
    if mode == "--write":
        for f in (PANEL, HWFW):
            open(paths[f], "w", encoding="utf-8").write(new[f])
        print("%s: WRITTEN, %d edit(s) and a change-record row" % (NAME, len(edits)))
    else:
        print("%s: CHECK OK, %d edit(s) and a change-record row, nothing written" % (NAME, len(edits)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
