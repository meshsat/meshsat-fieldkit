**HO-E REGISTER ROWS (Layer 4 task L4A-59 corrected on its focused check L4A-100, 7 October 2026, W145, branch `fnd/l4hoe`; R-3 restated and R-4 added by W152 the same day on the targeted recheck W150's F3, F4 and F6): DONE: four row texts for the coordinator, R-1 and R-2 for W144's finding F6 (the states S-f and S-g, which the drafted monitor does not end and nobody owned after L4REG-F7), R-3 for its finding F3 (the self-test's firmware row FW-B23, drafted in `apply_hw_fw_contract_hoe.py`, its hold check on the LSI-clocked RTC at 12 ms and its marker rule since W152) and R-4 for W150's F3 (S-m, the self-reset loop, W148-F4's case). NOT DONE: no row is entered in `_runs/l4ai/register.tsv` (the coordinator is its one writer); nothing applied. NEXT: the coordinator assigns ids and enters the rows.**

# HO-E: register rows for the coordinator

Record l9t5, `HO-E-COMPARISON.md` and `l9t5_hoe.out` (sections 6 and 9). Prototype design: nothing in this kit has been built, bought,
powered or measured. Each row follows the constitution's section 4 closure contract (defect or question, inputs, requirement, smallest
deliverable, acceptance, owner, dependency, checkpoint). Ids are proposals; the coordinator assigns the register's own.

## R-1: S-f, VOS2 with VCAP under the monitor's trip (W144's F6)

- **Class and state:** DEFECT (a state the protection admits that nothing ends), OPEN.
- **Question:** the drafted monitor trips from 1.0969 to 1.1303 V; ST prints VOS2's VCAP at 1.05 to 1.15 V and VOS3's at 0.95 to 1.05 V
  (DS12110 Rev 11 Table 112, p.209), so the bands meet at 1.05 V and VCAP cannot tell VOS2 from VOS3; VOS2 at its printed 300 MHz reads
  about 139.6 C at the case's 76.25 C air (W144's reviewer MODEL on Table 119, p.215), over VOS2's 125 C (Table 113, p.210).
- **Inputs:** `l9t5_hoe.out` sections 5d and 6 (S-f); FW-B20 as drafted in `apply_hw_fw_contract_t10.py` and restated by W140-F1;
  W138's L4REG-F7 (record l4reg, filed in `inputs/`).
- **Requirement:** HO-E's acceptance, "the controller inside its junction limit in every state the protection admits".
- **Task:** read every VOS2 operating point at this air on the printed rows (Tables 119 to 121, one supply corner), and either bound
  the state by a firmware row whose verification is named (FW-B20's static check: no write of PWR_D3CR's VOS other than Scale 3 and
  FW-B23's Scale 1, no PLL setting over 144 MHz; V-B20's read-back at start), or name a hardware ending; what neither covers is
  written as a residual with its fault basis.
- **Deliverable:** a short record section (record l9t5 or the firmware task's), its figures printed by a script, and the
  verification rows' text if any changes.
- **Acceptance:** each VOS2 state at or under 125 C on printed figures, or bounded by a named verified row, or written as a residual
  in REMAINING-ENGINEERING with its owner; no state left without one of the three.
- **Owner:** the firmware rows' author (L4A-61's).
- **Dependency:** L4A-61 (FW-B20 restated); after L4A-100's targeted recheck.
- **Checkpoint:** with L4A-61's first checkpoint.

## R-2: S-g, VOS3 above its printed 200 MHz (W144's F6)

- **Class and state:** DEFECT (a state with no printed current), OPEN.
- **Question:** ST prints VOS3's maximum frequency as 200 MHz (Table 113, p.210) and no current over it; a firmware that sets the PLL
  over 200 MHz in VOS3 runs outside every printed row, and the monitor (it watches VCAP) does not see it.
- **Inputs:** `l9t5_hoe.out` section 6 (S-g); FW-B20; T10's bounded state (`l9t5_t10.out` 10c).
- **Requirement:** HO-E's acceptance, as R-1.
- **Task:** bound the state by FW-B20's clock bound with its static check and V-B20's read-back named as the verification, and state
  the residual (a firmware fault that writes the PLL past the bound) with its fault basis; a hardware clock limit is named if one is
  found in a maker's document (none is in the pages record l9t5 read).
- **Deliverable:** as R-1.
- **Acceptance:** the state bounded by a named verified row, or a printed hardware limit quoted with its page, or written as a
  residual in REMAINING-ENGINEERING with its owner.
- **Owner:** the firmware rows' author (L4A-61's).
- **Dependency:** L4A-61; after L4A-100's targeted recheck.
- **Checkpoint:** with L4A-61's first checkpoint.

## R-3: FW-B23, the VCORE monitors' self-test (W144's F3 and F11)

- **Class and state:** DEFECT (a firmware row whose PASSED read a flag six other resets also set), CORRECTED AS A DRAFT, unapplied.
- **Question:** W140's self-test read PASSED on RCC_RSR's PINRSTF; RM0433 Rev 8 Table 56 (8.4.4, p.332) sets PINRSTF on a power-on,
  brownout, software, window watchdog, independent watchdog and low-power reset too; its window (VOSRDY within 1 ms, then 2 ms) did not
  time the ending S1's limit is read at.
- **Inputs:** `apply_hw_fw_contract_hoe.py` (FW-B23 and V-B24), `apply_hw_fw_contract_t10.py` (FW-B20 to FW-B22, V-B20 to V-B23),
  `l9t5_hoe.out` 5e and 8.
- **Requirement:** HO-E's acceptance; CON-004 (one supervisor out at a time, IOHA row 3).
- **Task:** take FW-B23 and V-B24 into L4A-61's propagation after T10's rows: clear the flags (RMVF), keep the marker where NRST does
  not reach (Table 55, p.330), write Scale 1 and wait t_resp (122.6 us since W148's hold stage; 174.7 us in W145's draft) from that
  write, write Scale 3 within 10 us if still running, and read PASSED only on Table 56's row 2 (PINRSTF and CPURSTF set, every other
  flag clear) with the restart at least 12 ms after the write on the RTC clocked by the LSI, never the HSE (W148-3 restated by W152-1
  on W150's F4: RM0433 Rev 8 pp.426 and 428, DS12110 Rev 11 Table 136 p.233, PREDIV_A + 1 at most 8); a start with the marker set
  evaluates the test it follows and does not test again (W150's F6).
- **Deliverable:** HW-FW-CONTRACT.md with FW-B20 to FW-B23 and V-B20 to V-B24, applied by the integrator in that order.
- **Acceptance:** both scripts apply in order on the tree's contract and re-parse (FW-B01 to FW-B23, V-B ending V-B24); FW-B23's
  PASSED pattern equals Table 56's row 2, its window equals `l9t5_hoe.out`'s t_resp, its hold check reads 12 ms on the LSI and its
  budget for VCAP's fall and the boot equals `l9t5_hoe.out` 5e's; test_l9t5_hoe passes.
- **Owner:** L4A-61's author; the integrator applies.
- **Dependency:** L4A-61, after L4A-100's targeted recheck; `apply_hw_fw_contract_t10.py` applied first.
- **Checkpoint:** with L4A-61's first checkpoint.

## R-4: S-m, the self-reset loop (W148-F4, given its own row by W150's F3)

- **Class and state:** MISSING PHYSICAL EVIDENCE (a state with a printed current whose cadence no printed figure bounds), CONDITIONAL.
- **Question:** an image that enters VOS1 or VOS0 and resets itself (a software or watchdog reset, RM0433 Rev 8 8.4.2, p.329) before
  the TPS37 registers the excursion never reaches the hold stage; its cadence is the internal reset (20 us minimum, p.329), NRST's
  recharge and the boot, none bounded by a printed figure beyond the 20 us; for scale (`l9t5_hoe.out` 5i, MODEL on T10's model) the
  loop's mean reaches 105 C at a duty of 5.34 % at the case's air. It is a VOS1 or VOS0 state, not S-g's (row R-2): W148's filing
  under R-2 is withdrawn.
- **Inputs:** `l9t5_hoe.out` 5i and 6 (S-m), 9 (S2 extended); the draft `apply_gen_sch_b_vcoremon.py`; FW-B23 (row R-3).
- **Requirement:** HO-E's acceptance, "the controller inside its junction limit in every state the protection admits".
- **Task:** S2 extended (SESSION W152-3), on the three first-article supervisors of S2 at 76 C and at -40 C: (a) the TPS37's shortest
  registered excursion on VCAP's own ramp to VOS1's and VOS0's bands, cut short by a software reset at stepped delays after the Scale 1
  write; (b) VCAP's fall after a reset to under the trip's least 1.0969 V; (c) 1000 self-reset cycles per supervisor and temperature at
  the image's earliest reset.
- **Deliverable:** the measured figures with their specimens, conditions and instruments, and the row's verdict restated in record
  l9t5 (or the first article's record).
- **Acceptance:** the least excursion of (b) at least twice the longest unregistered excursion of (a), and every cycle of (c) asserts
  RESET1 with NRST low at least 14 ms (zero escapes in 3000 per temperature): S-m becomes S-k's and is held by the hold stage's printed
  minimum. Otherwise the row is OPEN and a design change is owed that registers every excursion an image can make (for example a capture
  of VCAP's excursion that does not rest on the TPS37's sense delay), which no record has drafted.
- **Owner:** the first article's test owner (S2's); a failed acceptance goes to board B's generator owner for the design change.
- **Dependency:** the first article of board B with the drafted monitor applied; S2.
- **Checkpoint:** with S2.
