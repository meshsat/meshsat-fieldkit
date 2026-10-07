**HO-E REGISTER ROWS (Layer 4 task L4A-59 corrected on its focused check L4A-100, 7 October 2026, W145, branch `fnd/l4hoe`): DONE: three row texts for the coordinator, R-1 and R-2 for W144's finding F6 (the states S-f and S-g, which the drafted monitor does not end and nobody owned after L4REG-F7) and R-3 for its finding F3 (the self-test's firmware row FW-B23, drafted in `apply_hw_fw_contract_hoe.py`). NOT DONE: no row is entered in `_runs/l4ai/register.tsv` (the coordinator is its one writer); nothing applied. NEXT: the coordinator assigns ids and enters the rows; the targeted recheck of L4A-100 reads them with condition C5.**

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
  not reach (Table 55, p.330), write Scale 1 and wait t_resp (174.7 us) from that write, write Scale 3 within 10 us if still running,
  and read PASSED only on Table 56's row 2 (PINRSTF and CPURSTF set, every other flag clear).
- **Deliverable:** HW-FW-CONTRACT.md with FW-B20 to FW-B23 and V-B20 to V-B24, applied by the integrator in that order.
- **Acceptance:** both scripts apply in order on the tree's contract and re-parse (FW-B01 to FW-B23, V-B ending V-B24); FW-B23's
  PASSED pattern equals Table 56's row 2 and its window equals `l9t5_hoe.out`'s t_resp; test_l9t5_hoe passes.
- **Owner:** L4A-61's author; the integrator applies.
- **Dependency:** L4A-61, after L4A-100's targeted recheck; `apply_hw_fw_contract_t10.py` applied first.
- **Checkpoint:** with L4A-61's first checkpoint.
