#!/usr/bin/env python3
"""apply_hw_fw_contract_t10.py: DRAFT apply script on v2/docs/HW-FW-CONTRACT.md (Layer 9 record l9t5, task T10 round 5,
MESHSAT-1357, 5 October 2026). UNAPPLIED: the integrator runs it; record l9t5 runs it only on scratch copies.

WHAT IT IS: two Layer 5 rows brought forward as a NAMED PREREQUISITE of the Layer 4 power gate (the owner's instruction of
5 October 2026 14:20, section 4: "a narrowly necessary ... interface correction ... may be brought forward solely as a named
prerequisite of the current power gate. It must have a stated reason and acceptance check"). It restarts no other Layer 5 work.
  FW-B20, the supervisors' run state (T10-A1). REASON: L9T5-F06 and L9T5-F13 (record l9t5 `l9t5_t10.out` sections 8 and 10c):
    with no row the supervisors' state is unbounded and each private AP2112K-3.3 passes its 150 C absolute maximum junction at
    the case's own figure; the bound plus the pre-regulator (apply_gen_sch_a_iocpre.py) holds the regulator under 125 C.
  FW-B21, the fabrics' transmit share and fault handling. REASON: L9T5-F13 (both transceivers dominant, held: 125 C exceeded),
    L9T5-F16 and L9T5-F17 (one and both fabrics faulted: 125 C and 150 C exceeded), all covered by CON-004 (REQUIREMENTS-TRACE.md;
    ARCH-PCB-B-IOHA.md section 12 rows 7 and 8, test A7). With FDCAN_CCCR.DAR = 1 every transmission is a scheduled one, so the
    share the schedule sets bounds each transceiver's average current whatever the bus fault (l9t5_t10.out section 10d and 10e).
ACCEPTANCE (the rows' verification items, added to section 5): V-B20, each supervisor's supply current MEASURED at the bound (the
    AP2112K's output current, a supervisor junction of at least 105 C, traffic at the FW-B21 share) at or under the record's bounded
    figure, and the LDOs' case temperature in a 76 C chamber (T10-A5); V-B21, the share read on each TXD, and each credible bus fault
    injected with traffic running. Those measurements CONFIRM the firmware's implementation of a bound whose feasibility the record
    establishes on printed figures; they do not decide it (record l9t5 T10-ROUND5.md, "what the bench confirms").
The rows cite record l9t5's drafts and are written OWED (DRAFTED): no supervisor firmware exists (v2/firmware holds the panel's).
Usage:  apply_hw_fw_contract_t10.py [TARGET] [--check | --write]   (default TARGET: the tree's v2/docs/HW-FW-CONTRACT.md;
        default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, an anchor missing or not unique, or the result does not re-parse)."""
import difflib
import os
import re
import sys

NAME = "apply_hw_fw_contract_t10"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = os.path.join(REPO, "v2", "docs", "HW-FW-CONTRACT.md")

HEAD_OLD = "### 3.3 Board B: modules, supervisors and board B's devices (FW-B01 to FW-B19)\n"
HEAD_NEW = "### 3.3 Board B: modules, supervisors and board B's devices (FW-B01 to FW-B21)\n"
FW_B20 = ("| FW-B20 | the three supervisors `B:U41`, U51, U61 (STM32H743VIT6, silicon revision V or X by CON-017 (5)), each on its private "
          "AP2112K-3.3 (U40, U50, U60) from `+5V_IOC` pre-regulated to 4.18 V by board A's U601 (record l9t5 T10, "
          "`apply_gen_sch_a_iocpre.py`, DRAFTED) | Run each supervisor at voltage scale VOS3 with the CPU clock (frcc_c_ck) at most "
          "144 MHz and every bus and kernel clock at most the CPU clock; the reset state (HSI at 64 MHz, VOS3; RM0433 Rev 8 p.279 and "
          "p.349) is inside the bound; enable only FDCAN (both instances), I2C1, the GPIO ports in use (A, B, C, D, E, H), SYSCFG, the HSE "
          "and the IWDG; read the clock tree and the voltage scale back at start and stay in reset-safe outputs if they differ; never "
          "raise either at run time | L9T5-F06, L9T5-F13 (record l9t5 `l9t5_t10.out` sections 8 and 10c: the regulator's junction at the "
          "bounded state, ST DS12110 Rev 10 Tables 30, 39, 129 and 137); a Layer 5 row brought forward as a named prerequisite of the "
          "Layer 4 power gate | V-B20 | OWED (DRAFTED, record l9t5 round 5) |\n")
FW_B21 = ("| FW-B21 | the six TCAN334D `B:U43`, U44, U53, U54, U63, U64 on fabrics A and B, each fed from its supervisor's `+3V3_IOCx`; "
          "SHDN (pin 5) from PD2 (fabric A) and PB14 (fabric B) with 100 k to GND (record l9t5 `apply_gen_sch_b_canshdn.py`, DRAFTED; as "
          "drawn pin 5 rests on the part's internal pull-down) | FDCAN_CCCR.DAR = 1 on both fabrics, so every transmission is a "
          "scheduled one (RM0433 Rev 8 p.2470 and p.2527); nominal and data rates between 125 kbit/s and 1 Mbit/s (FW-B09's ceiling "
          "kept); each supervisor's own TXD dominant at most 2 % of every 100 ms window on each fabric, its frames, their error flags and "
          "its acknowledgements counted; a fabric at error passive or bus-off (FDCAN_PSR.EP, PSR.BO; on bus-off the device sets INIT "
          "itself, p.2464 and p.2534), or with a frame pending and no valid frame for 100 ms, is stopped at once (INIT kept set) and its "
          "transceiver put in shutdown (SHDN high); it is probed no more than once a second, SHDN low and INIT cleared for at most 100 ms, "
          "inside the same share; the other fabric carries the quorum meanwhile (IOHA FMEA row 7); with both fabrics stopped the "
          "supervisor does not act (row 8, FW-B09) | L9T5-F13, F16, F17 (record l9t5 `l9t5_t10.out` sections 10d to 10f); CON-004; "
          "TI SLLSEQ7F 5.5, 6.3.1, Table 6-5 | V-B21 | OWED (DRAFTED, record l9t5 round 5) |\n")
V_B20 = ("| V-B20 | FW-B20 | at start, each supervisor's clock tree and voltage scale read over SWD equal the row; each supervisor's supply "
         "current (its AP2112K's output) measured in the bounded state with its traffic at the FW-B21 share and a supervisor junction of "
         "at least 105 C: at or under record l9t5's bounded figure (`l9t5_t10.out` 10c); each LDO's case temperature in a 76 C chamber "
         "(T10-A5) |\n")
V_B21 = ("| V-B21 | FW-B21 | a scope on each TXD over 10 s of traffic: dominant at most 2 % of every 100 ms window; each fabric in turn "
         "shorted CANH to GND, CANH to CANL and CANL to GND, and opened at A7's break links, with traffic running: the supervisors stop "
         "the faulted fabric within 100 ms, its transceivers' SHDN reads high, the quorum holds on the other fabric, and each AP2112K's "
         "output current averaged over 1 s is at or under record l9t5's response figure (`l9t5_t10.out` 10e); both fabrics faulted: "
         "nothing moves |\n")
CHANGE = ("| 2 (T10, P0) | 5 October 2026 | By Layer 9 record l9t5's task T10, round 5 (MESHSAT-1357, `records/l9t5/T10-ROUND5.md`, "
          "`apply_hw_fw_contract_t10.py`), Layer 5 rows brought forward as a named prerequisite of the Layer 4 power gate under the "
          "owner's instruction of 5 October 2026: FW-B20 (the supervisors' run state, T10-A1) and FW-B21 (the fabrics' transmit share "
          "and fault handling, L9T5-F13, F16, F17, CON-004), with V-B20 and V-B21; both OWED (DRAFTED) |\n")


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def rows(text, prefix, cells):
    """the table rows that start with `prefix`, each checked to carry `cells` cells (a re-parse of the markdown tables)."""
    out = []
    for line in text.splitlines():
        if line.startswith(prefix):
            parts = line.strip().strip("|").split(" | ")
            if len(parts) != cells:
                refuse("a row %s carries %d cells, not %d" % (line[:20], len(parts), cells))
            out.append(parts[0].strip())
    return out


def patched(text):
    if "| FW-B20 |" in text or "| V-B20 |" in text:
        refuse("the change is already applied")
    b19 = [l for l in text.splitlines(True) if l.startswith("| FW-B19 |")]
    v19 = [l for l in text.splitlines(True) if l.startswith("| V-B19 |")]
    if len(b19) != 1 or len(v19) != 1:
        refuse("the anchors FW-B19 and V-B19 are not each in the file once")
    if text.count(HEAD_OLD) != 1:
        refuse("section 3.3's heading is not the one this draft was written against")
    if not text.endswith("\n") or not text.rstrip("\n").splitlines()[-1].startswith("| 2 "):
        refuse("the change record is not the file's last table")
    edits = [(HEAD_OLD, HEAD_NEW), (b19[0], b19[0] + FW_B20 + FW_B21), (v19[0], v19[0] + V_B20 + V_B21)]
    new = text
    for old, rep in edits:
        if rep == old or new.count(old) != 1:
            refuse("an anchor is not unique or its new text equals the old: %r" % old[:50])
        new = new.replace(old, rep)
    new = new + CHANGE
    if new == text:
        refuse("the result does not differ")
    # re-parse: the FW-B rows are B01 to B21 with six cells each, the V-B rows carry three cells, the change record four
    b = rows(new, "| FW-B", 6)
    if b != ["FW-B%02d" % i for i in range(1, 22)]:
        refuse("the FW-B rows do not read FW-B01 to FW-B21 in order: %s" % b)
    v = rows(new, "| V-B", 3)
    if v[-2:] != ["V-B20", "V-B21"] or len(v) != len(rows(text, "| V-B", 3)) + 2:
        refuse("the V-B rows do not end with V-B20 and V-B21")
    if rows(new, "| 2 (T10, P0) |", 3) != ["2 (T10, P0)"]:
        refuse("the change record row does not parse")
    if re.search("[" + chr(0x2013) + chr(0x2014) + "]", FW_B20 + FW_B21 + V_B20 + V_B21 + CHANGE):
        refuse("a long dash in the new text")
    return new


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) > 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = (args[0] if args else TREE), flags == ["--write"]
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/HW-FW-CONTRACT.md", "b/HW-FW-CONTRACT.md", n=0))
    if not write:
        print("%s: CHECK OK, 4 edit(s), nothing written" % NAME)
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new:
        refuse("the written file does not read back as the patched text")
    patched_again = "| FW-B20 |" in back and rows(back, "| FW-B", 6)[-1] == "FW-B21"
    if not patched_again:
        refuse("the written file does not re-parse")
    print("%s: WRITTEN, 4 edit(s)" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
