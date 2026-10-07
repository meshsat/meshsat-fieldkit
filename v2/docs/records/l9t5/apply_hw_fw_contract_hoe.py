#!/usr/bin/env python3
"""apply_hw_fw_contract_hoe.py: DRAFT apply script on v2/docs/HW-FW-CONTRACT.md (record l9t5, Layer 4 task L4A-59, the ledger's HO-E,
corrected on its focused check L4A-100; MESHSAT-1357, W145, 7 October 2026; restated by W148 the same day for the hold stage that
replaces W145's CTR1 capacitor, and by W152 the same day on the targeted recheck's notes F4 and F6: the hold check's time base and
threshold, the marker rule). UNAPPLIED: the integrator runs it; record l9t5 runs it
only on scratch copies (l9t5_hoe.py section 8, test_l9t5_hoe).

WHAT IT IS: one Layer 5 row and its verification item, drafted for the register's firmware task L4A-61 (HO-E-REGISTER-ROWS.md, R-3):
  FW-B23, the VCORE monitors' self-test. REASON: the focused check W144's findings F3 and F11 (`_runs/claude/w144chkhoe/`): the
    test's PASSED read only RCC_RSR's PINRSTF, which ST's Table 56 (RM0433 Rev 8 8.4.4, p.332) also sets on a power-on, brownout,
    software, window watchdog, independent watchdog and low-power reset; and its window (VOSRDY within 1 ms, then 2 ms) did not time
    the ending a VOS0 entry relies on. The row reads PASSED only on Table 56's row 2 ("Pin reset (NRST)": PINRSTF and CPURSTF set,
    every other flag clear) after clearing the flags (RMVF), keeps its marker where NRST does not reach (Table 55, p.330: "Debug
    features, Flash memory, RTC and backup RAM are not reset"), and times the window from the Scale 1 write at t_resp (122.6 us,
    record l9t5 `l9t5_hoe.out` 5d, since W148's hold stage; 174.7 us in W145's draft), so every unit in service shows its own ending
    inside the interval S1's limit is read at; and (W148-3, restated by W152-1) it times the hold stage: the restart must come at least
    12 ms after the write (the hold's printed minimum is 14 ms, TI SBVS249B 7.6; its CT-open delay at most 1.3 ms), read on the RTC
    clocked by the LSI (ST RM0433 Rev 8 8.7.26 and 8.7.27, pp.426 and 428: neither stopped by a pin reset; the HSE is), whose printed
    band is 29.4 to 33.6 kHz (ST DS12110 Rev 11 Table 136, p.233). A start with the marker set evaluates the test it follows and does
    not test again (W152, the targeted recheck's F6).
  V-B24, its first-article verification (the S2 measurement the record names and the hold's confirmation; S5 retired by W148-1).
It applies AFTER apply_hw_fw_contract_t10.py (it extends that draft's FW-B20 to FW-B22 and V-B20 to V-B23 and its change record) and
refuses a file where those rows are absent. The rows cite record l9t5's drafts and are written OWED (DRAFTED): no supervisor firmware
exists (v2/firmware holds the panel's).
Usage:  apply_hw_fw_contract_hoe.py [TARGET] [--check | --write]   (default TARGET: the tree's v2/docs/HW-FW-CONTRACT.md;
        default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, T10's rows absent, an anchor missing or not unique, or the result does not
re-parse)."""
import difflib
import os
import re
import sys

NAME = "apply_hw_fw_contract_hoe"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = os.path.join(REPO, "v2", "docs", "HW-FW-CONTRACT.md")

HEAD_OLD = "### 3.3 Board B: modules, supervisors and board B's devices (FW-B01 to FW-B22)\n"
HEAD_NEW = "### 3.3 Board B: modules, supervisors and board B's devices (FW-B01 to FW-B23)\n"
FW_B23 = ("| FW-B23 | the three supervisors `B:U41`, U51, U61 and their VCORE monitors U810, U820, U830 (TI TPS37, record l9t5 "
          "`apply_gen_sch_b_vcoremon.py`, DRAFTED: each pulls its hold stage U811, U821, U831 (TI TPS3703F6050) while VCAP is over 1.0969 to "
          "1.1303 V, and the hold stage holds the controller's NRST then and at least 14 ms after) | The self-test is the one write of PWR_D3CR's VOS other than Scale 3, and SYSCFG_PWRCR.ODEN is never written "
          "(W140-F1). At every start and then once every 3600 s, one supervisor at a time and only while the other two serve: set "
          "RCC_RSR.RMVF; write a test marker and the RTC's time to the backup RAM or the RTC backup registers, the RTC clocked by the LSI "
          "(RCC_BDCR.RTCSEL = LSI with RTCEN set, never the HSE, which a pin reset stops) with PREDIV_A + 1 at most 8 (a sub-second step of "
          "at most 0.25 ms at 32 kHz); at HCLK at most 144 MHz write VOS = Scale 1 and wait 122.6 us from that write, with no wait on VOSRDY; still running, write VOS = Scale 3 within 10 us, clear the marker and "
          "report MONITOR FAILED in the state frame. After a reset with the marker set: PASSED only when RCC_RSR reads ST's Table 56 row 2, "
          "PINRSTF and CPURSTF set with LPWRRSTF, WWDG1RSTF, IWDG1RSTF, SFTRSTF, PORRSTF, BORRSTF, D2RSTF and D1RSTF clear; any other "
          "pattern is MONITOR FAILED; PASSED also needs the RTC's time from the write to the restart, read at the LSI's 32 kHz typical, at least "
          "12 ms, else HOLD FAILED (the hold stage's CT pull-up lost or its hold degraded); clear the marker; that start evaluates the test "
          "it follows and does not run the test again (the next test is the hourly one); count the test in FW-B22's state frame, the peers "
          "flagging a count that has not moved for 7200 s | HO-E (record l9t5 `l9t5_hoe.out` 5e; L4A-59, its focused check L4A-100, "
          "findings F3 and F11, and its targeted recheck's F4 and F6): ST RM0433 Rev 8 8.4.4 Table 56 (p.332), 8.4.2 and Table 55 (pp.329 "
          "and 330), 6.8.6 (p.309), 8.7.26 and 8.7.27 (pp.426 and 428), 46.6.5 (p.1932); ST DS12110 Rev 11 Table 136 (p.233: the LSI 29.4 "
          "to 33.6 kHz); TI SBVS249B 7.6 (p.7: tD 14 ms minimum, CT open 1.3 ms maximum); the window is t_resp, the interval S1's limit is "
          "read at | V-B24 | OWED (DRAFTED, record l9t5 W145, W148 and W152; PROVISIONAL on S2: a healthy regulator ramp longer than the "
          "window is read on the first article, then the window and S1 are re-read together; the hold check assumes VCAP's fall to the "
          "release and the boot under 8.474 ms, NRST's rise bounded at 1.254 ms, read by V-B24) |\n")
V_B24 = ("| V-B24 | FW-B23 | on three first-article supervisors in a 76 C chamber at the rail's top: the self-test run 100 times on each; "
         "every run PASSED with Table 56's row 2 read back; the interval from the Scale 1 write to NRST under 0.3 VDD scoped on every run, "
         "at most 122.6 us (S2, on the real VCAP ramp); each monitor's divider opened in turn: MONITOR FAILED reported; each hold stage's CT "
         "pull-up opened in turn: HOLD FAILED reported; NRST's low time after each pass scoped against the hold's printed 14 ms minimum (a "
         "confirmation; S5 retired); VCAP's fall to the release and the time from NRST's release to the restart read, together under "
         "8.474 ms; the RTC's reading of each test against the scoped interval from the write to the restart (the LSI-clocked RTC counting "
         "through NRST) |\n")
CHANGE = ("| 2 (HO-E, P0) | 7 October 2026 | By Layer 4 task L4A-59's correction on its focused check L4A-100 (MESHSAT-1357, W145, "
          "`records/l9t5/HO-E-COMPARISON.md`, `apply_hw_fw_contract_hoe.py`, applied after `apply_hw_fw_contract_t10.py`): FW-B23, the VCORE "
          "monitors' self-test (findings F3 and F11) with the hold stage's timing (W148-3, restated by W152-1), with V-B24; OWED (DRAFTED) |\n")


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
    if "| FW-B23 |" in text or "| V-B24 |" in text or "| 2 (HO-E, P0) |" in text:
        refuse("the change is already applied")
    if "| FW-B22 |" not in text or "| V-B23 |" not in text or "| 2 (T10, P0) |" not in text:
        refuse("the T10 rows (FW-B20 to FW-B22, V-B20 to V-B23, change record 2 (T10, P0)) are absent: apply_hw_fw_contract_t10.py first")
    b22 = [l for l in text.splitlines(True) if l.startswith("| FW-B22 |")]
    v23 = [l for l in text.splitlines(True) if l.startswith("| V-B23 |")]
    if len(b22) != 1 or len(v23) != 1:
        refuse("the anchors FW-B22 and V-B23 are not each in the file once")
    if text.count(HEAD_OLD) != 1:
        refuse("section 3.3's heading is not the one this draft was written against")
    if not text.endswith("\n") or not text.rstrip("\n").splitlines()[-1].startswith("| 2 (T10, P0) |"):
        refuse("the change record's last row is not T10's")
    edits = [(HEAD_OLD, HEAD_NEW), (b22[0], b22[0] + FW_B23), (v23[0], v23[0] + V_B24)]
    new = text
    for old, rep in edits:
        if rep == old or new.count(old) != 1:
            refuse("an anchor is not unique or its new text equals the old: %r" % old[:50])
        new = new.replace(old, rep)
    new = new + CHANGE
    if new == text:
        refuse("the result does not differ")
    # re-parse: the FW-B rows are B01 to B23 with six cells each, the V-B rows three cells ending V-B24, the change record three
    b = rows(new, "| FW-B", 6)
    if b != ["FW-B%02d" % i for i in range(1, 24)]:
        refuse("the FW-B rows do not read FW-B01 to FW-B23 in order: %s" % b)
    v = rows(new, "| V-B", 3)
    if v[-5:] != ["V-B20", "V-B21", "V-B22", "V-B23", "V-B24"] or len(v) != len(rows(text, "| V-B", 3)) + 1:
        refuse("the V-B rows do not end with V-B20 to V-B24")
    if rows(new, "| 2 (HO-E, P0) |", 3) != ["2 (HO-E, P0)"]:
        refuse("the change record row does not parse")
    if re.search("[" + chr(0x2013) + chr(0x2014) + "]", FW_B23 + V_B24 + CHANGE):
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
    if not ("| FW-B23 |" in back and rows(back, "| FW-B", 6)[-1] == "FW-B23"):
        refuse("the written file does not re-parse")
    print("%s: WRITTEN, 4 edit(s)" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
