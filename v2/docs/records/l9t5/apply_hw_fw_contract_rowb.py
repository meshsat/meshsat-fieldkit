#!/usr/bin/env python3
"""apply_hw_fw_contract_rowb.py: DRAFT apply script on v2/docs/HW-FW-CONTRACT.md (Layer 9 record l9t5, round 10; Layer 4 task L4A-61,
the propagation of row (b) of the AI-scope register; MESHSAT-1357, 7 October 2026, W151). UNAPPLIED: the integrator runs it; this record
runs it only on scratch copies (v2/ecad/tools/tests/test_l9t5_rowb.py).

WHAT IT IS: the Layer 5 rows row (b)'s drafts change, restated, and the in-service limiter test added as a new row pair. Row (b)'s drafts
(none applied): record l9t5 `apply_gen_sch_b_canmb.py` (W137, W143: the peers' TXD reads and 2-of-2 SHDN votes, the share limiters
removed), `apply_gen_sch_b_regstage.py` (W138: a TPS2553-1 latch-off limiter ahead of a TPS73733DCQRM3 at each supervisor, the rail
trips removed), `apply_gen_sch_b_canen.py` (W143: the peers' 2-of-2 route on the limiter's EN) and `apply_gen_sch_b_hodtest.py` (W146:
the peers' in-service test of each limiter). The edits, all on the state `apply_hw_fw_contract_t10.py` then
`apply_hw_fw_contract_canq.py` leave (it refuses a page without canq's change record):
  FW-B20  restated: each supervisor's regulator and its limiter (the rail trip gone), its enabled set with TIM3 and an ADC (row (b)'s
          captures and reads), BOR level 2; the sustained bound at the limiter's printed maximum (record l9t5 `l9t5_t10.out` 11a);
  FW-B21  restated: SHDN OR'd with the two peers' 2-of-2 vote (canmb) in place of the share limiter; W139's stop at the loss count kept;
  FW-B22  canq's RESTART rule kept as W143 worded it, with the in-service test's exception added (no automatic restart of a peer under
          test: the test restores it itself); W143's DAR = 1 text (ES0392 2.24.5's workaround) and the self-test kept word for word;
  V-B20   restated: the regulator's site read by E-17 (its pass limit), the supply current under the limiter's least;
  V-B21   restated: the regulator named, its current against the limiter's least;
  V-B23   restated on the limiter (its band, its latch, the peers' restart); round 6's rail trip and its 0.2 s WITHDRAWN;
  FW-B24  NEW: the peers' in-service test of each limiter (HO-D under the limiter, record l4hod, W146), its preconditions, schedule, steps,
          thresholds, failure response and continuous checks; V-B25 NEW: its bench rows (record l4hod's supplier tasks).
FW-B23 and V-B24 are left to HO-E's draft (`apply_hw_fw_contract_hoe.py` on fnd/l4hoe, L4A-59): this script reads them when present and
never writes them. FINDING W151-F3 (the coordinator): canq's and hoe's scripts each refuse unless T10's change record is the page's last
row, so as written they cannot both apply; one of them needs its anchor restated before set 33 takes both.
REASON: the ledger's RE-5 to RE-8 and HO-C to HO-D (`records/l4close/REMAINING-ENGINEERING.md`); row (b)'s drafts change what FW-B20 to
FW-B22 and V-B20 to V-B23 say, and W146-F7 asks for the test's rows. A Layer 5 row brought forward as a named prerequisite of the Layer
4 power gate (the owner's instruction of 5 October 2026, section 4), like t10's and canq's.
ACCEPTANCE: the rows' V items; the desk acceptance is record l9t5 `l9t5_t10.out` 11a (L4A-57, DONE AS CONDITIONAL on E-17) and record
l4hod `L4HOD.md` (L4A-58); PROVISIONAL until row (b)'s check (L4A-62).
Usage:  apply_hw_fw_contract_rowb.py [TARGET] [--check | --write]   (default TARGET: the tree's v2/docs/HW-FW-CONTRACT.md;
        default --check: nothing is written)
Exit 0: checked (or written); 3: refused (canq's change absent, already applied, an anchor missing or not unique, or the result does
not re-parse)."""
import difflib
import os
import re
import sys

NAME = "apply_hw_fw_contract_rowb"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = os.path.join(REPO, "v2", "docs", "HW-FW-CONTRACT.md")

HEAD = re.compile(r"^### 3\.3 Board B: modules, supervisors and board B's devices \(FW-B01 to FW-B2[23]\)\n", re.M)
HEAD_NEW = "### 3.3 Board B: modules, supervisors and board B's devices (FW-B01 to FW-B24)\n"
OLD_B20 = ("| FW-B20 | the three supervisors `B:U41`, U51, U61 (STM32H743VIT6, silicon revision V only, record l9t5 L9T5-D7: revision X "
           "held until its own qualification, V-B20), each on its private AP2112K-3.3 (U40, U50, U60) from `+5V_IOC` pre-regulated to ")
FW_B20 = (
    "| FW-B20 | the three supervisors `B:U41`, U51, U61 (STM32H743VIT6, silicon revision V only, record l9t5 L9T5-D7: revision X held "
    "until its own qualification, V-B20), each on its private TPS73733DCQRM3 (U40, U50, U60; new silicon only, the M3 suffix) behind its "
    "TPS2553-1 latch-off limiter (U45, U55, U65; RILIM 49.9 kOhm 1 %: IOS 0.4702 to 0.5704 A, latched at most 10 ms after it limits; "
    "record l9t5 `apply_gen_sch_b_regstage.py`, DRAFTED, W138; round 6's rail trip removed) from `+5V_IOC` pre-regulated to 4.01 V by "
    "board A's U601 (R602 14.0 k; `apply_gen_sch_a_iocpre.py` with `apply_gen_sch_a_iocset.py`, DRAFTED); the regulator's junction "
    "bounded at constant maximum dissipation at the limiter's printed maximum (record l9t5 `l9t5_t10.out` 11a: CONDITIONAL on E-17, "
    "PROVISIONAL until row (b)'s check) | Run each supervisor at voltage scale VOS3 with the CPU clock (frcc_c_ck) at most 144 MHz and "
    "every bus and kernel clock at most the CPU clock; the reset state (HSI at 64 MHz, VOS3; RM0433 Rev 8 p.279 and p.349) is inside the "
    "bound; enable only FDCAN (both instances), I2C1, the GPIO ports in use (A, B, C, D, E, H), SYSCFG, TIM3 (the peers' TXD captures, "
    "FW-B22), the ADC of ADC1 or ADC2 that reads the peers' limiter outputs (FW-B24, powered only for its conversions), the HSE and the "
    "IWDG; read the clock tree and the voltage scale back at start and stay in reset-safe outputs if they differ; never raise either at "
    "run time; BOR at level 2 (FW-B24's second barrier) | L9T5-F06, L9T5-F13 (record l9t5 `l9t5_t10.out` sections 8, 10c and 11a: the "
    "regulator's junction at the bounded state and at the limiter's maximum, the enabled set's current against the limiter's window; "
    "ST DS12110 Rev 10 Tables 30, 39, 129, 137 and 184, TI SLVS841F 7.5, SBVS067W 5.4); a Layer 5 row brought forward as a named "
    "prerequisite of the Layer 4 power gate; a VOS0 entry is HO-E's (L4A-59, its own row) | V-B20 | OWED (DRAFTED, record l9t5 rounds "
    "5 and 10) |\n")
B21_OLD = ("through a 1N4148W, OR'd with each transceiver's transmit-share limiter (`apply_gen_sch_b_iocguard.py`, DRAFTED: SHDN high by "
           "hardware while the TXD's dominant share is over 4.7 to 12.3 %)")
B21_NEW = ("through a 1N4148W, OR'd through its own 1N4148W with the two peers' 2-of-2 vote (record l9t5 `apply_gen_sch_b_canmb.py`, "
           "DRAFTED: an SN74LVC1G08 on the target's own rail lifts SHDN only while both other controllers vote, FW-B22's attribution rule; "
           "round 6's transmit-share limiter removed, W137)")
B21_SRC_OLD = "| L9T5-F13, F16, F17 (record l9t5 `l9t5_t10.out` sections 10d to 10f); CON-004; TI SLLSEQ7F 5.5, 6.3.1, Table 6-5 | V-B21 | OWED (DRAFTED, record l9t5 round 5) |"
B21_SRC_NEW = ("| L9T5-F13, F16, F17 (record l9t5 `l9t5_t10.out` sections 10d to 10f, restated in 11a (j)); CON-004; TI SLLSEQ7F 5.5, 6.3.1, "
               "Table 6-5 | V-B21 | OWED (DRAFTED, record l9t5 rounds 5 and 10) |")
B22_OLD = ("at most once in 10 s per peer, never on a message received over a fabric; the peer's limiter's EN is pulled low only while "
           "both other controllers vote.")
B22_NEW = ("at most once in 10 s per peer, never on a message received over a fabric, and never on a peer under the in-service limiter test "
           "(FW-B24), whose step 4 restores it; the peer's limiter's EN is pulled low only while both other controllers vote.")
OLD_VB20 = "| V-B20 | FW-B20 | at start, each supervisor's clock tree and voltage scale read over SWD equal the row and its REV_ID reads "
V_B20 = (
    "| V-B20 | FW-B20 | at start, each supervisor's clock tree and voltage scale read over SWD equal the row and its REV_ID reads 0x2003 "
    "(revision V); each supervisor's supply current (its TPS73733's output) measured in the bounded state with its traffic at the FW-B21 "
    "share, its enabled set as the row lists it and a supervisor junction of at least 105 C: at or under record l9t5's bounded figure "
    "(`l9t5_t10.out` 10c) and under the limiter's least 0.4702 A with the window `l9t5_t10.out` 11a (g) states; E-17 (record l9t5 "
    "`l9t5_t10.out` 11a (e)): on the first-article board B in still air at 76 C, each TPS73733's junction with its input current held at "
    "the limiter's printed maximum 0.5704 A, its input at 4.1174 V and its output in regulation, from its case-top temperature by its "
    "printed psi-JT, its ground current read: at most 125 C, and its rise in 10 ms of 2.348 W at most 36.2 K (or W151-1's exclusion kept); "
    "this reading decides the condition the sustained bound rests on (the printed theta is a JEDEC best case), the others confirm the "
    "firmware's implementation |\n")
VB21_OLD = "and each AP2112K's output current averaged over 1 s is at or under record l9t5's response figure (`l9t5_t10.out` 10e)"
VB21_NEW = ("and each TPS73733's output current averaged over 1 s is at or under record l9t5's response figure (`l9t5_t10.out` 10e) and "
            "under the limiter's least 0.4702 A")
OLD_VB23 = "| V-B23 | FW-B20 | each supervisor's rail loaded to 0.30 A: its LDO's EN reads low and the supervisor is unpowered, the time "
V_B23 = (
    "| V-B23 | FW-B20 | each supervisor's limiter (TPS2553-1, RILIM 49.9 kOhm 1 %) loaded from its bounded state through an external "
    "load drawing over 0.5704 A: its output current read limited inside 0.4702 to 0.5704 A, its FAULT low and the limiter latched off 5 to "
    "10 ms after it limits (TI SLVS841F 7.5 and 9.3.1), the supervisor unpowered, and the supervisor restarted by its two peers' 2-of-2 "
    "EN route within record l4canen's recovery bound; at the largest served state (0.4240 A, `l9t5_t10.out` 11a (g)) for 60 s the limiter "
    "does not limit; round 6's rail trip and its 'within 0.2 s' are WITHDRAWN (the rail trip is removed, W138-2) |\n")
FW_B24 = (
    "| FW-B24 | the in-service test of each supervisor's TPS2553-1 (U45, U55, U65) by its two peers through the drafted test path (record "
    "l9t5 `apply_gen_sch_b_hodtest.py`, DRAFTED, W146: a 3.0 Ohm load on the limiter's output through two AO3400A in series, the upper "
    "gated by the next controller and the lower by the one after it, PE12 and PE13 on each; each peer reads that limiter's FAULT through "
    "its own BAT46W (PE14, PE15) and its output on its own 10 kOhm over 20 kOhm divider (PC0, PC1, the ADC); a BAT46W holds the tested "
    "regulator off while the load conducts) | PRECONDITIONS, each peer on its own observation: all three in the quorum on both fabrics for "
    "the last 10 windows, no other test and no contained node, the target's FAULT high and its output in band. SCHEDULE: the first round "
    "60 s after the quorum first holds (A, B, C 20 s apart), then each supervisor every 3600 s, the three 1200 s apart. STEPS: 0 mark the "
    "target under test in both peers' state frames (FW-B22's restart rule and its self-test then leave it alone); 1 both peers assert "
    "their restart votes: the output falls under 2.0 V within 1.384 s, and after release it is back over 3.3 V within 0.804 s, else RESTORE "
    "ROUTE and abort with nothing latched; then the output at 3.3 V for 20 ms; 2 the upper half alone for 4 ms, then the lower alone for "
    "4 ms: no drop under 2.5 V, else SWITCH STUCK ON; 3 the upper closes, then the lower; the closer finds the output under 2.5 V 0.2 ms "
    "after closing (the other peer 3.2 ms after its own), else LIMIT NOT SHOWN and both open; each peer reads I = V / 3.0 Ohm 1 to 4 ms "
    "after the drop it sees, PASS 0.4345 to 0.6140 A, else LIMIT HIGH or LIMIT LOW; FAULT falls 4.75 to 10.25 ms after the drop, else "
    "FAULT NOT SEEN or FAULT EARLY; the output under 0.3 V 1 ms after FAULT, else NO LATCH; both halves open by 12 ms; the two peers' "
    "readings agree, else PEERS DISAGREE; 4 both restart votes for 2.0 s, then the output back over 3.3 V and FAULT high, the target "
    "rejoining within 0.800 s, else RESTORE FAILED (the restart rule then retries every 10 s). ANY FAILURE: both peers open their halves, "
    "report the verdict in their state frames and the kit's status path, restore the target if latched, and stop that supervisor's tests "
    "until the next start. Each peer records the target and the step in its backup registers before step 3 and clears them after step 4; "
    "a peer that boots with a step 3 recorded takes that test as failed. CONTINUOUS CHECKS every window: each peer reads both targets' "
    "FAULT and output; FAULT low with the output normal, or the output out of band, is a test-path fault on its second consecutive failure. "
    "BOR at level 2 (FW-B20) | HO-D under the limiter (the ledger's HO-D; record l4hod `L4HOD.md` sections 2 to 6 and `l4hod.out`: the "
    "test's acceptance on printed figures, a lost limit found within 3602.341 s, 102.341 s for one present at start-up, the target out "
    "of the quorum 5.945 s a test, 0.50 % of the time, 35 fault rows of the test path each found); TI SLVS841F 7.5 (the deglitch 5 to "
    "10 ms), 9.3.1 and 9.3.3 | V-B25 | OWED (DRAFTED, record l4hod; PROVISIONAL: the supply's dip at the load step, W146-F10) |\n")
V_B25 = (
    "| V-B25 | FW-B24 | on the first-article board B, each supervisor's test run: PASS, the reading inside 0.4345 to 0.6140 A, FAULT 4.75 "
    "to 10.25 ms after the drop, LATCHED, restored within 5.945 s; a lost limit injected on one supervisor (RILIM shorted): LIMIT NOT SHOWN "
    "or LIMIT HIGH at its next test, the two survivors' 3.3 V rails, reset flags and board B's +5V_IOC recorded through the step: no "
    "survivor resets, each survivor's 3.3 V stays over 2.37 V and +5V_IOC is back over 3.5127 V within 26.3 us (W146-F10), and the same "
    "with a healthy limiter's step; each half's drain and source bridged in turn: SWITCH STUCK ON at step 2 with nothing latched; the load "
    "opened, then shorted: LIMIT NOT SHOWN, LIMIT LOW; a FAULT read diode opened: PEERS DISAGREE; the restart route's RC capacitor "
    "shorted: step 1 aborts with nothing latched; the output's draw in the reading window at most 0.5 mA with the regulator's BAT46W "
    "fitted and at most 20 mA without it; each peer's reading against a reference at 1.3 to 1.8 V within 10 mV at its pin; the limiter "
    "settled within 1 ms of the load's closure (record l4hod `L4HOD.md` section 11) |\n")
CHANGE = ("| 4 (row b) | 7 October 2026 | By record l9t5's round 10, Layer 4 task L4A-61 (MESHSAT-1357, W151, `records/l9t5/T10-ROUND10.md`, "
          "`apply_hw_fw_contract_rowb.py`), after `apply_hw_fw_contract_canq.py`: row (b)'s drafts propagated: FW-B20 (the regulator and "
          "its limiter, the rail trip gone, TIM3 and an ADC enabled, BOR level 2), FW-B21 (SHDN OR'd with the peers' 2-of-2 vote, the "
          "share limiter gone), FW-B22's restart rule (no automatic restart of a peer under test), V-B20 (E-17's site reading), V-B21, "
          "V-B23 (the limiter, the rail trip's 0.2 s WITHDRAWN), and the in-service limiter test FW-B24 with V-B25 (record l4hod); "
          "FW-B23 and V-B24 left to HO-E's draft; OWED (DRAFTED, PROVISIONAL until row (b)'s check L4A-62) |\n")


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


def one(text, prefix):
    hit = [l for l in text.splitlines(True) if l.startswith(prefix)]
    if len(hit) != 1:
        refuse("the row starting %r is not in the file once" % prefix[:40])
    return hit[0]


def patched(text):
    if "| 4 (row b) |" in text or "| FW-B24 |" in text or "| V-B25 |" in text:
        refuse("the change is already applied")
    if "| 3 (L4A-55) |" not in text:
        refuse("apply_hw_fw_contract_canq.py's change record is absent: apply t10's, then canq's, first")
    if not text.endswith("\n") or not re.match(r"\| (3 \(L4A-55\)|2 \(HO-E, P0\)) \|", text.rstrip("\n").splitlines()[-1]):
        refuse("the change record's last row is neither canq's nor HO-E's")
    heads = HEAD.findall(text)
    if len(heads) != 1:
        refuse("section 3.3's heading is not the one this draft was written against")
    b20, b21, b22 = one(text, OLD_B20), one(text, "| FW-B21 |"), one(text, "| FW-B22 |")
    v20, v21, v23 = one(text, OLD_VB20), one(text, "| V-B21 |"), one(text, OLD_VB23)
    b_last = one(text, "| FW-B23 |") if "| FW-B23 |" in text else b22
    v_last = one(text, "| V-B24 |") if "| V-B24 |" in text else v23
    for old, where in ((B21_OLD, b21), (B21_SRC_OLD, b21), (B22_OLD, b22), (VB21_OLD, v21)):
        if where.count(old) != 1:
            refuse("an old text is not in its row once: %r" % old[:50])
    b21n = b21.replace(B21_OLD, B21_NEW).replace(B21_SRC_OLD, B21_SRC_NEW)
    b22n = b22.replace(B22_OLD, B22_NEW)
    v21n = v21.replace(VB21_OLD, VB21_NEW)
    new = text.replace(heads[0], HEAD_NEW)
    for old, rep in ((b20, FW_B20), (b21, b21n), (v20, V_B20), (v21, v21n), (v23, V_B23)):
        if rep == old or new.count(old) != 1:
            refuse("an anchor is not unique or its new text equals the old: %r" % old[:50])
        new = new.replace(old, rep)
    # FW-B22's restart rule and the new rows after the last FW-B and V-B rows (HO-E's FW-B23 and V-B24 when present)
    if b_last is b22:
        if new.count(b22) != 1:
            refuse("FW-B22 is not in the file once")
        new = new.replace(b22, b22n + FW_B24)
    else:
        if new.count(b22) != 1 or new.count(b_last) != 1:
            refuse("FW-B22 or FW-B23 is not in the file once")
        new = new.replace(b22, b22n).replace(b_last, b_last + FW_B24)
    vl = V_B23 if v_last is v23 else v_last
    if new.count(vl) != 1:
        refuse("the last V-B row is not in the file once")
    new = new.replace(vl, vl + V_B25)
    new = new + CHANGE
    if new == text:
        refuse("the result does not differ")
    # re-parse: FW-B01 to FW-B22 (FW-B23 when HO-E's is there) and FW-B24 in order, six cells; the V-B rows three cells, V-B25 last of
    # them; the change record's row three cells
    b = rows(new, "| FW-B", 6)
    want = ["FW-B%02d" % i for i in range(1, 23)] + (["FW-B23"] if "| FW-B23 |" in text else []) + ["FW-B24"]
    if b != want:
        refuse("the FW-B rows do not read %s to FW-B24 in order: %s" % (want[0], b[-4:]))
    v = rows(new, "| V-B", 3)
    if v[-1] != "V-B25" or len(v) != len(rows(text, "| V-B", 3)) + 1 or "V-B20" not in v or "V-B23" not in v:
        refuse("the V-B rows do not end with V-B25")
    if rows(new, "| 4 (row b) |", 3) != ["4 (row b)"]:
        refuse("the change record's row does not parse")
    added = FW_B20 + B21_NEW + B22_NEW + V_B20 + VB21_NEW + V_B23 + FW_B24 + V_B25 + CHANGE
    if re.search("[" + chr(0x2013) + chr(0x2014) + "]", added):
        refuse("a long dash in the new text")
    return new


def main(argv):
    target = TREE
    mode = "--check"
    for a in argv:
        if a in ("--check", "--write"):
            mode = a
        else:
            target = os.path.abspath(a)
    if not os.path.isfile(target):
        refuse("no target %s" % target)
    old = open(target, encoding="utf-8").read()
    new = patched(old)
    n = sum(1 for l in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0) if l.startswith("+") and not l.startswith("+++"))
    if mode == "--write":
        tmp = target + ".rowb-tmp"
        open(tmp, "w", encoding="utf-8").write(new)
        os.replace(tmp, target)
        print("%s: WRITTEN, %d line(s) added or changed" % (NAME, n))
    else:
        print("%s: CHECK OK, %d line(s) would be added or changed (nothing written)" % (NAME, n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
