# Power architecture review packet: MeshSat field kit V2 (MESHSAT-1357, layer 4)

**1 October 2026.** For an electronics engineer's review. This packet is the entry point only: it points into the
records listed in `PACKET-FILES.txt` and repeats none of them. **Prototype design:** nothing is bought, built, powered,
measured or fabricated, and no board of this set has a layout. Every figure is the records' desk arithmetic, labelled
there MAKER, NETLIST, MODELED, INFERRED, DECLARED or ASSUMPTION. The review runs beside the work; it pauses nothing.
**Second issue, 1 October 2026:** brought to the independent power review (`REVIEW-POWER-ARCHITECTURE-AS-RECEIVED.md`,
CONDITIONAL): a compliant panel is now pinned and evaluated with the proposed control (out 12), the undocumented loads
are listed (out 13), and O-2's status and the per-source acceptance are restated.

Where a figure comes from: `L4-ENERGY-ARCHITECTURE.md` ("the page"), `l4e_replay.out` ("out N", its section), and
`../r11dep/R11-DEPENDENCY.md` ("R11-DEP", its section).

## 1. What we ask of you

Short answers suffice: agree, disagree with the reason, or name what you would need to see.

1. **The charge path, the window and the hold.** Is it sound to size board A's charge path to REQ-016's 100 W into the
   stage (U3's IIN_HOST at 4.65 A, R11's stacked minimum above 4.829 A) rather than the 6.2 mOhm and 6.2 A drafted for
   200 W (out 8)? The pinned compliant panel (SunPower SPR-E-Flex-100) gives only 350.0 Wh a day into the stage on
   SC-37's day, and the LT8705A's input hold at 17.6 V (REQ-016's figure)
   sits above its 17.1 V maximum-power voltage: the hold's tolerance band alone moves the day from 280.6 to 373.5 Wh
   (out 12). What band would you design the hold to?
2. **Source control (A-2).** The LM5176 front end regulates VBUS20, so U3's input regulation cannot see a sagging panel;
   as drawn, U3's fixed 4.15 A asks more than the compliant panel ever gives, so the collapse bound loses the whole
   solar input (out 12). Is a firmware rule that lowers IIN_HOST with VIN_RAW (FW-A16, `HW-FW-CONTRACT.md`) acceptable,
   with per-source acceptance (solar inside REQ-016's window; vehicle and shore down to the 9 V floor) and with startup,
   source changes and stale telemetry covered, given that FW-E04 reports VIN_MON over USB only every 1 s? Or would you
   put source tracking in hardware? (page, A-2)
3. **O-2's bound on the stage's input power. B2: arithmetic corrected under stated assumptions (closed). O-2 physical
   compliance: OPEN.** The setting (3.548 A) and its corner check (worst 99.9984 W at 25 V, out 11) rest on EA2's and
   EA3's TYP-only gains, the line regulation printed at 25 C and not switching, two 1 % resistors with tolerance and
   drift unselected, and temperature ends that repeat the same bounds; EA2 at 120 V/V instead of 130 V/V gives
   100.0758831 W (the review's sensitivity). Which IC grade, RSENSE1 and RIMON_IN values and tolerance and drift budget
   would you choose, and what steady-state and transient acceptance? One compliant panel never reaches the limit on
   SC-37's day, two in parallel would (6 hours, out 12): is an input-current limit still the mechanism you would use?
4. **R138 on the USB-C outlet (DR-03).** Is TI's recommended 5 mOhm right for U18, TPS25740A, at its 3 A setting
   (HIPWR), given the table's own inconsistency on the HIPWR label (`../l3r5/checks/l3batt-check-3/CHECK-3.md`, minor
   1)?
5. **The front end in a fault (B-1, B-2).** Are the LM5176's hiccup mode and FETs and copper sized for the window-sized
   path's highest permitted current (INFERRED 6.66 to 7.21 A) adequate, with L1 an XAL1010-103ME (Isat 17.5 A typical)?
6. **VBUS20's bulk node (B-4).** The worst can is INFERRED at 2.85 to 3.09 A at a 2:1 ESR spread against 2.8 A a can
   (Panasonic EEHZK), by scaling the generator's node analysis in proportion to the current. Is that scaling acceptable,
   and would you resize the bank or bound the fault?
7. **The solar entry's protection against TRN-001.** D4, an SMCJ28A, begins to break down at 31.1 to 34.4 V but clamps
   up to 45.4 V at 33.1 A, while the two 100 uF bulk capacitors behind it are rated 35 V
   (`../../reviews/DECISION-31-PROTECTION-TOPOLOGY.md`, PV_IN). Breakdown onset is not protection. What surge should the
   entry be designed to take, and would you lower the clamp or raise the capacitors' rating? D4 is one-way, so a
   reversed panel forward-biases it at the panel's short-circuit current (its note E-N1).
8. **The three undocumented efficiencies (C-8).** The LT8705A stage at 17.6 V to 15.1 V, the LM5176 at 15.1 V to 20 V
   and the 4S pack's charge efficiency are carried at 0.93, 0.93 and 0.95 with no maker figure for these circuits. Which
   figures would you use, and which bench measurement would you make? Across their brackets A2's needed storage at 48 h
   runs from +131.4 to +344.0 Wh, and no value decides the verdict (out 6).

## 2. Fixed constraints (the owner's, not open to this review)

The Current owner brief heads `../../handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`; each item below is a record in
the registry `v2/ecad/tools/pcb_requirements.yaml`, cited by id and not restated:
- storage inside the Peli 1450, no external battery; battery and solar both required (D-28, D-32; REQ-014);
- HF and the tablet kept in the lid (D-28, D-33);
- 48 to 72 hours a design objective under REQ-072's stated profile, not a minimum (D-28; REQ-072);
- the solar window unchanged (D-34; REQ-016); the USB-C outlet's contracts (REQ-017); the 9 to 36 V vehicle input
  (REQ-015);
- the cells' temperature windows and the open cell and thermal obligations (REQ-046; FEA-008, D-29);
- D-06's single 4S3P pack stands; a second pack is a proposal only.

## 3. The power path as drawn

DRAWN = on a committed netlist. HYPOTHETICAL = a correction or draft on no generated board.

```
PANEL: none pinned (O-1). REQ-016: Voc <= 25 V at its coldest, held at 17.6 V, <= 100 W into the stage
  |  J_SOLAR, F2 10 A, D4 SMCJ28A                                       board E, gen_sch_e.py, pcb-e1-dock-e7   DRAWN
  v
U5 LT8705A buck-boost: FBIN 17.6 V (R8 102k, R9 7.50k), FBOUT 15.1 V                                            DRAWN
   input-current limit (IMON_IN) set to 3.548 A: CSPIN and CSNIN are tied to VIN as drawn          O-2 HYPOTHETICAL
  |  TRK_OUT 15.1 V, U4 ideal diode --+
VEHICLE AND SHORE 9 to 36 V: J_DCIN, E:F1 10 A, LM74700, U6 LM5069-2 --+--> VIN_RAW, up the dock contacts    DRAWN
  v
U2 LM5176 front end: R11 10 mOhm (average limit), L1 XAL1010-103ME, Q2 to Q5 CSD19532Q5B    board A, gen_sch_a.py,
   pcb-a-power-a23                                                                                              DRAWN
   R11 chosen for the window (stacked minimum above 4.829 A)                                         HYPOTHETICAL
  |  VBUS20 20 V, Panasonic EEHZK bulk
  v
U3 BQ25731: R16 10 mOhm (RAC), R17 5 mOhm (RSR), L2 XAL1010-472ME; IIN_HOST 4.15 A (entry E1, firmware)         DRAWN
   IIN_HOST 4.65 A under a VIN_RAW-dependent rule (A-1, A-2)                                         HYPOTHETICAL
  |  VBAT = U3's VSYS, the system node
  +--> A:F1 25 A, CELL+, board P (pcb-p-pack-p2), D-06's 4S3P of INR18650-35E: A1                                DRAWN
  +--> A2 only: U3B BQ25731, board PL, lid 4S9P, then LM74700-Q1 and LM5069 (5.6 mOhm) back to VBAT
       (../a1elec/TOPOLOGY.md, a draft)                                                              HYPOTHETICAL
  +--> the kit's load converters on boards A and B: PS-IDLE-SPEC 42.8 W at the pack terminals                  DRAWN
  +--> USB-C outlet: U19 LM5176 5 / 9 / 15 V stage, Q27, R138 10 mOhm (ISNS), J_USBC_OUT; U18 TPS25740A          DRAWN
       R138 at 5 mOhm (DR-03)                                                                        HYPOTHETICAL
```

The parts' sheets are listed in `PACKET-FILES.txt`; the netlists are the committed `out/*.net` files, and the schematic
PDFs are build outputs that git ignores.

## 4. The two architectures and their numbers

A1 is D-06's single 4S3P and changes no owner ruling. A2 is the base 4S6P plus a separately protected lid 4S9P with both
lid functions kept, a proposal that changes D-06 only. One assumption set (page, "The comparison"; out 1): REQ-072's
42.8 W, cells aged to 80 %, the 3.00 V line with the 5 % reserve, SC-37's mean September day at Leiden, TYP, starts 06
and 18 UTC, the hypothetical corrected path at ENERGY-BASIS's worst-established inputs (WE). Unserved energy is the
replay's service ledger (out 5); pairs are 06 / 18 UTC.

| | A1 | A2 |
|---|---|---|
| Usable store, aged | 107.9 Wh (+20 C), 44.5 Wh (-10 C) | 544.4 Wh, 224.5 Wh; 502.6 Wh at the solar runs' temperatures |
| Battery only | 2.52 h (+20 C), 1.04 h (-10 C) | 12.71 h, 5.24 h |
| 100 W screening case: first interruption | hour 13 / 2 | hour 23 / 11, both 05 UTC |
| 100 W: unserved at 48 h / 72 h | 907.4 / 923.5; 1382.5 / 1398.6 Wh | 270.1 / 286.3; 500.4 / 516.5 Wh |
| 100 W: least storage to add, 48 h / 72 h | +654.8 / +873.1 Wh | **+278.8 / +515.8 Wh** |
| As drawn (upper bound), 100 W: unserved at 48 h / 72 h | 907.3 / 923.5; 1382.4 / 1398.5 Wh | 332.7 / 348.9; 625.5 / 641.7 Wh |
| O-2's lower corner, 52.8 W: least storage to add | +995.0 / +1544.3 Wh | **+610.8 / +1167.3 Wh** |
| **Compliant panel** (SPR-E-Flex-100, 350.0 Wh a day into the stage): first interruption | hour 6 / 2 | hour 18 / 11 |
| Compliant panel, corrected: unserved at 48 h / 72 h | 1367.4 / 1368.1; 2103.9 / 2104.6 Wh | **986.9 / 1196.1; 1741.4 / 1950.7 Wh** |
| Compliant panel, corrected: least storage to add | +1361.5 / +2094.1 Wh | **+979.2 / +1719.7 Wh** |
| Compliant panel, as drawn: unserved (upper bound; collapse bound) | 1366.0 / 1366.8 and 2101.9 / 2102.6 Wh; 1946.5 and 2973.7 Wh | 985.6 / 1195.5 and 1739.5 / 1949.4 Wh; 1555.1 and 2582.9 Wh |
| Compliant panel: steady load carried 48 h / 72 h (a sensitivity; the profile stays 42.8 W) | 8.0 / 8.0 W | 21.1 / 17.5 W |

**The objective is missed by both.** A2, the larger store, stops at 05 UTC of the first night: 7 to 8 of 48 hours and 13
to 14 of 72 go unserved. To serve 48 h it would need a store of 781.4 Wh at the model's temperatures, and 1018.4 Wh for
72 h, against the 502.6 Wh it holds. No in-case place was found for more with both lid functions kept (39 lid places;
`../l3batt/SHORTLIST.md` 3). No efficiency up to 1.00 closes it. The 100 W case rests on a 400 Wp 2S2P availability
trace that REQ-016 does not admit, so it is a **conditional screening stimulus**, kept as a comparison. On the pinned
compliant panel the gap is about three times wider: A2 needs +979.2 / +1719.7 Wh, and would carry 48 h only at a steady
21.1 W, 21.7 W under the profile, against 8.4 W of undocumented loads (out 13). **Neither architecture is approved or
shown realizable;** A2 stays a proposal to change D-06, its mechanical fit and thermal obligations open.

## 5. The architecture decisions, one line each

Remedy, then closure. Detail in the page's section "The power-path corrections as architecture decisions" and in R11-DEP
2.

- **Governing:** size the charge path to REQ-016's window, not 200 W. Closure: the corrected result holds at the
  window-sized setting (out 8).
- **A-1:** U3 at 4.65 A (5.05 A at the 0.97 bracket), R11's stacked minimum above its maximum plus 0.079 A; drawn
  circuit at 4.00 A meanwhile. Closure: bench 7b.1 at -20, 25, 62 C.
- **A-2:** a VIN_RAW-dependent IIN_HOST rule for every source, covering startup, source changes and stale telemetry.
  Closure by source: solar (the panel or its simulator inside REQ-016's window) VIN_RAW above 12 V and FE_PGOOD held
  (7b.7); vehicle and shore from the 9 V floor, IIN_HOST per FW-A16 (a), the entry never at its LM5069 limit, VIN_RAW
  above the front end's latch; steady state and transients apart.
- **B-1:** the window-sized setting is at or under the 9 V schedule; L1 rated for the fault or the fault bounded.
  Closure: peak at most 90 % of Isat with C-5's derating; 7b.5.
- **B-2:** LM5176 hiccup (SNVSAI1D pp.17, 20); FETs and copper for the fault current. Closure: TJ at most 150 C at 9,
  15.1, 36 V in 62.1 C air; 7b.4.
- **B-3:** re-declare VBUS20, FE_OUT, VIN_RAW and the rest at the chosen currents; regenerate. Closure: dc_drop, derate,
  track-width gates PASS.
- **B-4:** re-run the node analysis at the fault current; resize, rebalance or bound. Closure: every can at most 2.8 A;
  7b.8.
- **B-5:** A-2's rule. Closure: 7b.7.
- **C-1:** Kelvin taps on R11, allowance recomputed for the chosen R11. Closure: kelvin_check; 7b.3.
- **C-2:** the chosen R11's catalogue part, 1 %, 50 ppm/K or better. Closure: its sheet filed.
- **C-3:** board A's own thermal resistance for Q2 to Q5. Closure: the figure at the chosen currents, or a measurement.
- **C-4:** C11 and C12 with a maker's ripple rating at 36 V. Closure: the figure filed; 7b.8.
- **C-5:** file Coilcraft's Isat derating. Closure: read at the part's temperature, fed to B-1.
- **C-6:** no 200 W stage; the stage stays in the 100 W class under O-2. Closure: O-2's; 7b.9.
- **C-7:** U3's input-current minimum. Closure: TI's figure or a bench reading at or above the setting less 0.1 A.
- **C-8:** the three efficiencies. Closure: the makers' figures or measurements, fed to the replay.
- **C-9:** R11 sized against 0.079 A of other VBUS20 loads. Closure: a bench reading of R11's current less R16's.
- **R138 (DR-03):** 5 mOhm, TI's recommendation (SLVSDG8B p.31). Closure: a 3 A load on each PDO without a trip.
- **O-1 (DR-04):** pinned, the SunPower SPR-E-Flex-100 (held sheet 523809 Rev D: Voc 21.4 V, -58.9 mV/K; 24.05 V at -20
  C cells), its trace computed (out 12). Closure: the revision bought confirmed against the sheet, its NOCT and
  low-irradiance data, O-3 to O-7 re-derived for one panel.
- **O-2 (DR-04):** the LT8705A's input-current limit (8705af pp.2, 4, 5, 29, 31). B2's arithmetic closed under stated
  assumptions; physical compliance OPEN. Closure: the grade, resistor values and tolerance budget chosen and run through
  the corner check; a bench sweep from 16.695 V to 25 V at both temperature ends, V_in x I_in at or under 100 W in
  steady state; transients accepted separately against a stated limit.

## 6. What stays INCONCLUSIVE, and what is NOT claimed

**Not claimed.** No circuit, board or kit is verified. The drawn charge path fails, and the corrected path is
hypothetical and not implemented. Nothing is fabricated or measured, and no layout exists for these netlists. No runtime
is demonstrated: every endurance figure is a model on one mean day.

**INCONCLUSIVE, with the evidence missing** (page, "What stays INCONCLUSIVE"):
- the compliant panel's trace: no NOCT, low-irradiance data or Voc tolerance on its sheet, a four-point diode fit, one
  mean day; REQ-016's -40 C reading (25.23 V) not met, named not decided;
- the drawn path between its upper and collapse bounds (bench 7b.7);
- the three efficiencies and U3's minimum (C-8, C-7);
- the 8.4 W of PS-IDLE-SPEC with no document (out 13: the monitor, the standby WiFi card, the VHF PA's beacon duty);
- the load converters down to the 12.0 V node;
- the lid pack's temperature and the cells against FEA-008;
- the window-sized fault currents (B-1 to B-4, INFERRED by scaling);
- the lid module's volume and base rows M4a, M5, M6w;
- the entry's ratings for an array above about 150 Wp;
- O-2's physical compliance: the TYP-only rows, the unselected resistors and the transient behaviour.

**What the engineer chooses next** (page, "The next implementable power-path choices", each with its acceptance): source
control, current-limit coordination, real component settings, fault handling and protection.

**Two findings about the accepted Layer 3 baseline** (page, "The Layer 3 finding, restated"; Layer 3's own records are
preserved unchanged):
- **The array.** Its headline solar-assisted figures were computed on proposal P-03's 400 Wp in 2S2P into a 200 W
  window, which REQ-016, kept by D-34, does not admit. Under the retained 100 W window, A2's storage need rises from
  +79.6 / +116.2 Wh to +278.8 / +515.8 Wh. DR-01 stands.
- **The double count.** The model's unserved counter credited a stopped hour's sun as served while it also charged the
  packs with it. Recounted by the service ledger on Layer 3's own inputs, the published 266.7 / 494.7 Wh (as drawn) are
  301.2 / 547.4 Wh, and 102.2 / 165.7 Wh (corrected, NOM) are 136.6 / 218.2 Wh (out 9).
