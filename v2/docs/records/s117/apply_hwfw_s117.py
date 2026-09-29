#!/usr/bin/env python3
"""S-117's firmware line (stream s117, MESHSAT-1357, 29 September 2026): FW-A17 and V-A05 in v2/docs/HW-FW-CONTRACT.md, the
page where this repository documents the bridge's charger setup (FW-A01 to FW-A16: RSNS_RAC, ChargeCurrent, the watchdog,
IIN_HOST). DRAFT for the contract's writer, run at the merge that applies apply_gen_sch_a_s117.py; the author ran --check.
No other repository is touched: the bridge's code implements the row, this page states it.

What it writes: the FW-A17 row after FW-A16 (PWM_FREQ held at its power-on 1b, 400 kHz, the row TI pairs with the 4.7 uH
L2 and 191 kOhm on IADPT; ChargeOption0 written only read-modify-write; REG0x01 read once after every charger POR before
any host write); V-A05 after V-A04; section 3.1's heading to FW-A17; FW-C01's step 5 names A17; a change-record row.
SLUSE66A: ChargeOption0 REG0x01/00, reset E70Eh (9.6.1, printed page 42), PWM_FREQ is REG0x01 bit 1, "0b: 800kHz, 1b: 400
kHz <default at POR>", "Recommend 800 kHz with 2.2 uH, and 400 kHz with 4.7 uH" (Table 9-8, continued on page 43; the
brief and set 10's check cite it as Table 9-9, which is REG0x00's table on the same page).

Guards: each anchor is found once by the table's first cell or the exact text; the rows are parsed back as markdown table
rows with the table's column count; nothing else moves (the file outside the five edits is compared line for line); a
second run refuses (FW-A17 is there); no dash character. --check writes nothing.

Usage: python3 apply_hwfw_s117.py [--check]"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
DOC = os.path.join(TOP, "v2/docs/HW-FW-CONTRACT.md")

HEAD_OLD = "### 3.1 Board A: power controller, charger, monitors and enables (FW-A01 to FW-A16)"
HEAD_NEW = "### 3.1 Board A: power controller, charger, monitors and enables (FW-A01 to FW-A17)"
C01_OLD = "5. the charger (FW-A01 to A03, A16);"
C01_NEW = "5. the charger (FW-A01 to A03, A16, A17);"
FW_A17 = ("| FW-A17 | BQ25731 `A:U3` ChargeOption0 (REG 0x01/00, reset E70Eh, SLUSE66A 9.6.1 p.42): PWM_FREQ is REG0x01 bit 1, "
          "1b = 400 kHz at POR (Table 9-8, p.43); `A:L2` 4.7 uH XAL1010-472ME with `A:R219` 191 k 1 % on IADPT (Table 9-4, p.27) "
          "and the compensation of Table 9-5's 400 kHz row, `A:R25`, `C26`, `C234`, `R220`, `C235`, `C27` (pp.27 and 28), drawn "
          "by S-117 (`records/s117/apply_gen_sch_a_s117.py`) | Keep PWM_FREQ = 1b (400 kHz): write ChargeOption0 only "
          "read-modify-write of the whole word, never clearing REG0x01 bit 1, in every write that touches it (FW-A03's WDTMR_ADJ, "
          "FW-C13's CHRG_INHIBIT, EN_LWPWR, EN_OOA); after every charger POR read REG0x01 once BEFORE any host write and log it, "
          "then read it back at every service; never write 0b while L2 is the 4.7 uH part with 191 k on IADPT | TI pairs 400 kHz "
          "with 4.7 uH (Table 9-8's own note, Tables 9-4 and 9-5); at 800 kHz the drawn `Q7` and `Q8` (CSD18510Q5B) would ask "
          "93 to 120 mA of gate drive from REGN, whose current limit is 50 mA minimum (8.5, p.11), and the drawn compensation is "
          "not the 800 kHz row (`records/s117/charger_l_f.out`); the maker does not say whether the IADPT reading writes the "
          "register, and with 191 k both select 400 kHz | V-A05 | FIRMWARE |")
V_A05 = ("| V-A05 | FW-A17 | after a charger POR with shore present and before any host write, read REG0x01 and record PWM_FREQ; "
         "with the converter running at light load and at the front end's limit, the switching frequency at `A:L2`'s CH_SW1 pad "
         "is inside 340 to 460 kHz (SLUSE66A 8.5 FSW, p.16); REG0x01 bit 1 reads 1b after every panel reboot |")
LOG = ("| 1 (S-117) | 29 September 2026 | By stream s117 (MESHSAT-1357): FW-A17 holds the charger's PWM_FREQ at its 400 kHz "
       "power-on value, the row TI pairs with the 4.7 uH `L2` and 191 k on IADPT that S-117's session decision draws "
       "(`records/s117/`), with V-A05; FW-C01's step 5 names it |")


def refuse(m):
    print("apply_hwfw_s117: REFUSED: %s" % m)
    sys.exit(2)


def cells(line):
    """A markdown table row's cells (the row is split on its unescaped pipes)."""
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")): return None
    return [c.strip() for c in s[1:-1].split("|")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t = open(DOC, encoding="utf-8").read()
    lines = t.split("\n")
    first = [(i, cells(l)) for i, l in enumerate(lines)]
    if any(c and c[0] == "FW-A17" for _, c in first): refuse("FW-A17 is already a row (a second run)")
    a16 = [i for i, c in first if c and c[0] == "FW-A16"]
    va4 = [i for i, c in first if c and c[0] == "V-A04"]
    if len(a16) != 1 or len(va4) != 1: refuse("FW-A16 found %d times, V-A04 %d times" % (len(a16), len(va4)))
    if cells(FW_A17) is None or len(cells(FW_A17)) != len(first[a16[0]][1]): refuse("FW-A17 does not have FW-A16's %d cells"
                                                                                   % len(first[a16[0]][1]))
    if len(cells(V_A05)) != len(first[va4[0]][1]): refuse("V-A05 does not have V-A04's cells")
    for what, old in (("section 3.1's heading", HEAD_OLD), ("FW-C01's step 5", C01_OLD)):
        if t.count(old) != 1: refuse("%s occurs %d times, not once" % (what, t.count(old)))
    k = len(lines) - 1
    while k >= 0 and not lines[k].strip(): k -= 1
    last = cells(lines[k])
    if not last or not last[0].startswith("1 (HOT-R1 drawn)"): refuse("the change record's last row is not as read")
    if len(cells(LOG)) != len(last): refuse("the change-record row does not have the table's cells")
    new = list(lines)
    new.insert(k + 1, LOG)
    new.insert(va4[0] + 1, V_A05)
    new.insert(a16[0] + 1, FW_A17)
    out = "\n".join(new).replace(HEAD_OLD, HEAD_NEW).replace(C01_OLD, C01_NEW)
    if "\u2014" in out or "\u2013" in out: refuse("a dash character")
    # nothing else moved: drop the three inserted rows and undo the two replacements, and the old text must return
    back = "\n".join(l for l in out.split("\n") if l not in (FW_A17, V_A05, LOG)).replace(HEAD_NEW, HEAD_OLD).replace(C01_NEW, C01_OLD)
    if back != t: refuse("something beyond the five edits moved")
    rows = [cells(l) for l in out.split("\n")]
    for rid in ("FW-A17", "V-A05"):
        if sum(1 for c in rows if c and c[0] == rid) != 1: refuse("%s is not one table row after the edit" % rid)
    print("apply_hwfw_s117: FW-A17 after FW-A16, V-A05 after V-A04, section 3.1's heading, FW-C01's step 5, one change-record "
          "row; %d lines -> %d" % (len(lines), len(out.split("\n"))))
    if a.check:
        print("CHECK ONLY: HW-FW-CONTRACT.md not written.")
        return 0
    open(DOC, "w", encoding="utf-8").write(out)
    if open(DOC, encoding="utf-8").read() != out: refuse("the written file differs")
    print("APPLIED: v2/docs/HW-FW-CONTRACT.md written once.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
