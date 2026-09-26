# Round 4, board B (compute): what changed in gen_sch_b.py, the decisions behind it, and what is still open

MESHSAT-1357, Review D (parts and circuits), round 4, board B author (r4b), 26 September 2026.
Prototype design: nothing in this kit has been built. Everything below is a statement about the generator, its
netlist and the documents it cites, never about hardware.

- Worktree: `scratchpad/wt/r4b`, branch `fnd/r4b` at main `82dd1e4d`. Written: `v2/ecad/tools/gen_sch_b.py`,
  `v2/ecad/tools/check_pcb_b.py` (fix-up pass 2, which made this author its writer) and `drafts/*`. Nothing committed
  or pushed.
- **Round 6 (section 1e: O-18 rebuilt on main faf8c981, the pass-3 re-review's blocking item; R4T-F9, SD-B-22)**:
  generator sha256 `6e3d880901fd30306c0fa8bda35a86da6450d7e4bb15217f9cc3225da8d5faef`, check_pcb_b.py sha256
  `28904a37f2f1810399e553f522d73fcc7848afc4d6ce3cce21556bffd70ccd4d`. Box directory `/root/r6/b/out6` (run 6,
  `drafts/box/r6-run6/`). The worktree's branch point stays 82dd1e4d. Main changed neither file; of board B's sch_prov identity
  it added `gen_footprints_e.py` and three lands in meshsat.pretty (boards E and P), and `sch_prov.py` itself changed, so
  the two files apply to faf8c981 unchanged but B's sidecar must be the one written on faf8c981 (O-18).
- **Fix-up pass 3 (section 1d, the round-5 re-review's blocking item)**: generator sha256
  `9b85ada81f0adab67fcef2f3e6e969a9f755c55314dc9bd77962af38e9483d84`, check_pcb_b.py sha256
  `720892aefe56ceb2dff099b16dd7421d2f78c42b86ccb49629085872a834c324`. Box directories `/root/r5/b/out4` (run 4, the
  regeneration and every gate, `drafts/box/r6-run4/`) and `/root/r5/b/out5` (run 5, the final gate file on B21 and the
  suite, `drafts/box/r6-run5/`). Diffs against pass 2: `drafts/box/gen_sch_b-fixup3.diff`, `drafts/box/check_pcb_b-fixup3.diff`.
- **Fix-up pass 2 (section 1c)**: generator sha256 `8a980c57669be838a4bdcc6dfd40336d8f1dc8d299443a8c8fd216ff5cea5c26`,
  check_pcb_b.py sha256 `5d52b0e2b34f289b17610924bb36a4e8289ac12fc0feade6e9461bcaafa6428a`. Box directory
  `/root/r5/b` (runs 1 to 3, `drafts/box/r5-run1`, `r5-run2`, `r5-run3`).
- Generator after the round-4 fix-up pass: sha256 `b24e88ceeef97aefc3601ee46b860cf2be89166c357d3fa52880fa8033898ab3`
  (the same file ran on the box, `drafts/box/out/gen_sch_b.sha256`). The first round-4 generator was `5f8b00ae...`;
  its box run is kept in `drafts/box/out-r4-first/` and its reports as `drafts/box/*-r4-first.*`.
- The fix-up pass answers the independent review (APPROVE_WITH_FIXES, two blocking items). Section 1b says what
  changed and why.
- Box: vast.ai 52646493, own directory `/root/r4/b` (a `--no-local` clone of the box's main clone at `82dd1e4d`;
  the main clone's `git status` was empty before and after every run, `drafts/box/out/main-status-*.txt`).

## 1. The items, one line each

| Item | Change in the generator | Status |
|---|---|---|
| W3-F01 | Socket maps swapped so the switch's transmitter reaches each socket's PETp0/PETn0 (keys M and B: 49/47; key E: 35/37) and PERp0/PERn0 return to the switch; 12 series 220 nF (C{s}53 to C{s}56) at the switch's PET1/PET2 | DONE in the generator, and since fix-up pass 2 in `check_pcb_b.py` itself (section 1c); both land in the same commit |
| W3-F02 | Hub DN1 receiver takes LIME_SSRX from J_LIME 6/5; C161/C162 now carry the hub's transmitter to J_LIME 9/8 (SSTX) | DONE in the generator and, since fix-up pass 2, in `check_pcb_b.py` |
| W3-F03 | REFCLKO0 to REFCLKP/N through 100 nF, C{s}95/C{s}96, six capacitors; fix-up: every used REFCLKO pair (O0, O1, O2, three slots) terminated at the source with 33.2 Ohm series and 49.9 Ohm to ground, 36 resistors (DS40068 Table 8-1 note 1) | DONE after the fix-up (O-03 closed) |
| S-12 / A08 | J_M2C2 is TE 2199119-3, key B, C590866; its land checked pad by pad against drawing C-2199119 rev F sheet 3 | PARTIAL: the land lacks the two locating holes (O-01) |
| D-07 (ANT3) | No board B net exists for any 5G antenna: the socket carries no RF, the module's IPEX receptacles take the pigtails. ANT0, ANT2 and conditional ANT3 recorded in J_M2C2's value and in r4-interfaces.md | DONE on B; board A owns the blind-mate net |
| S-13 | SIM 2 on 40 NC (DET), 42 DATA, 44 CLK, 46 RST, 48 VDD; both SIMs per HD Figure 18 (22 Ohm series at the holder, 10 pF, 100 nF); fix-up: SIM 2 also per Figure 19, four 0 Ohm links at the module (R287 to R289 on RST/CLK/DATA, R272 on VDD) ahead of the 22 Ohm | PARTIAL: the pins and the Figure 18/19 parts are done; the HD 4.1.7 TVS array is not (O-04) |
| F-PR-05 | +3V3_S2A and its socket segment declared 3.0 A / 4.0 A; 2 x 220 uF KEMET T520B227M006ATE025 (C212684), the HD's MLCC array (6.8 nF, 2 x 220 pF, 2 x 68 pF, 15 pF, 9.1 pF, 4.7 pF plus 2 x 100 nF), SMBJ5.0A TVS; +5V_S2 typical 4.1 A | DONE; fix-up pass 2 set the card buck to 3.456 V and compensated it for the 0.5 mF (SD-B-18, O-17 closed); +5V_S2 typical 4.2 A (board A peak question, r4-interfaces.md I-03) |
| S-01 | CM5 WL_nDisable/BT_nDisable on open-drain 2N7002 pull-downs (Q{s}09, Q{s}10) driven by U{s}11 (SN74LVC32A): KILL = software request OR EMCON_ON; requests default to OFF (10 k pull-ups); AW7915 supplies (slots 1, 3) pulled off by EMCON through Q{s}11; one EMCON inverter Q11/R513. Fix-up pass 3: the three W_DISABLE1# stages, whose body diodes lifted EMCON_HW to a HIGH with the panel absent, are now open drains Q{s}06 from EMCON_ON (SD-B-20), and R58 is 10 k (SD-B-21) | DONE after fix-up pass 3: with the panel absent B's radios are dark, proven at the datasheet leakage maxima (section 1d). Firmware and bench items O-06, O-07; the fail-open on a lost +3V3_DEV is O-14 (SD-B-14), which now covers W_DISABLE1# too |
| R4T-F9 (round 6) | R514 to R517, 10 k from LIME_EN, RB_EN, E22_EN and E72_EN to GND: an EMCON gate (U19, U20 on +3V3_DEV) that loses its own supply leaves its switch's EN held OFF instead of floating (SD-B-22); check_pcb_b.py asserts one pull-down to GND of 200 Ohm to 49.5 kOhm on each | DONE in round 6 (section 1e); the wider +3V3_DEV fail-open (module kills, card supplies, W_DISABLE1#) stays O-14 |
| S-08 (B) | R48, R50 to R53 from 100 k to 4.7 k; R60 to R62 to 4.7 k as well (session decision SD-B-04) | DONE |
| W5-F3 / W6-F4 | Supervisor kit I2C from PB1/PB2 (35/36, no I2C) to PB6 = I2C1_SCL (92) and PB7 = I2C1_SDA (93) | DONE |
| D-13 | Symbol STM32H743VI, value "STM32H743VIT6 ...", C114409; comments cite the ruling; pin identity re-proven 100/100 against both datasheets | DONE |
| W5 TESTACCESS-B | 6 GND pads, a 5 mOhm Kelvin shunt with two pads on each card-socket rail, a fit-to-disable jumper on each supervisor LDO EN (fix-up: on the SMD 1x02 land), 35 pads on the voted lines, the controllers' outputs and the CAN fabrics, and a 0 Ohm break link pair per CAN fabric | DONE (placement seats owed, O-02; the jumper's unpowered-controller state, O-16, is closed by DS12110 Tables 21 and 22 in fix-up pass 2) |
| W7-R2-01 | Confirmed: the SMD land PH1x5S is the generator's intent (17 September 2026 reason in the file); the committed B21 board lags. No change | DONE (confirmation) |
| D-12 | Board B already sends bank 3 port 3 (USB_WALL) to board A on J_AB2 pins 1/2; only the J_AB2 text changed. Board A's routing to the Glenair is in its own generator (r4a) and in r4-interfaces.md | DONE on B |
| S-16 | Recorded in section 4 and in U6's comment; no net was missing | DONE |

## 1b. The fix-up pass: the review's two blocking items and its minor items

The independent review returned APPROVE_WITH_FIXES with two blocking items. Both are resolved below. The review's own
reading of everything else (the netlist diff, W3-F01, W3-F02, S-13's pins, F-PR-05, S-01's logic, S-08, W5-F3, D-13,
TESTACCESS-B and S-12) was confirmed and is not repeated here.

**B-1: REFCLKO had no termination (W3-F03, and O-03 was filed as open). The reviewer is right, and it is fixed.**
- The held datasheet does say enough to act on. DS40068 Rev 5-2 (v2/vendor/diodes/diodes-pi7c9x2g404sl.pdf, sha256
  675fa7ee...) section 3.1:
  - REFCLKO_P/N[3:0] are "100MHz external differential HCSL clock outputs";
  - IREF is an "External resistor (475 Ohm +/- 1%) connection to set the differential reference clock output current".
- Table 8-1 note 1 gives the load the outputs are measured into: "Test configuration is Rs=33.2 Ohm, Rp=49.9 Ohm, and 2pF".
- A current-mode output only develops its swing across a resistor to ground. Round 4 AC-coupled REFCLKO0 into
  REFCLKP/N with no Rp, so it had no DC path, the PHY had no clock, and no link in any bank could train.
  O-03 was wrong to say no primary document decides this.
- The change: on each used pair (REFCLKO0 to the switch's own REFCLKP/N, REFCLKO1 to the NVMe socket, REFCLKO2 to the
  card socket) in all three slots:
  - the pin now carries `*_SRC_x` to a 33.2 Ohm series resistor, R{s}75/76, R{s}79/80 and R{s}83/84;
  - the line after it carries 49.9 Ohm to ground, R{s}77/78, R{s}81/82 and R{s}85/86;
  - the line keeps the name the long run already had (PCIE{s}_RCLK0_x, NVME{s}_CLK_x, CARD{s}_CLK_x).
  That is 36 resistors. REFCLKO3 (75/76) stays unused and open.
- Parts: UNI-ROYAL 0603WAF332JT5E (C23004) and 0603WAF499JT5E (C23185). Both are 0603, 1%, 1/10 W, -55 to +155 C.
  The series datasheet decodes both codes (drafts/datasheets/SOURCES.txt).
- Dissipation, worst case: Table 8-1's VHIGH maximum of 1.15 V held continuously gives 26.5 mW in Rp and 17.6 mW in
  Rs, against 100 mW for each part.
- Intent: 30 new nodes (18 `*_SRC_x` and the 12 NVMe and card clock lines), declared like PCIE{s}_RCLK0_x.
- `check_contracts` now reads 18 more lines, "R{s}75 (33.2R ...) is in series with a real pin on both sides", and
  PASSES 91 of 91.

**B-2: check_pcb_b.py fails on round 4's netlist. The reviewer is right. The change is drafted and proven; it is not
applied, because the file is W6/W7's.**
(Fix-up pass 2: the integrator made this author the writer of check_pcb_b.py, and the change is now APPLIED in the
worktree, byte for byte the patch below; section 1c.)
- `drafts/check_pcb_b-r4.patch` is written against 82dd1e4d. `git apply --check` is clean in this worktree, and
  nothing was applied. It does three things:
  - It builds `bypad` (net to (reference, pad)) beside `bynet`, so that a lane's DIRECTION can be judged.
  - It replaces lines 126-127 with pad-level checks:
    - each switch transmitter (PETP/N1 100/101, PETP/N2 106/107) reaches the socket's PET pin (keys M and B 49/47,
      key E 35/37) through exactly one series capacitor (`*_RX_SW_x` to `*_RX_x`);
    - the socket's PER pin (43/41 on M and B, 41/43 on E) returns on `*_TX_x` to the switch receiver (97/98 and
      102/103);
    - each used REFCLKO pin (81/80, 78/77) meets one series resistor, then one resistor to ground on the line, and
      the line reaches the socket's REFCLK (55/53, 47/49);
    - REFCLKO0 (85/83) is terminated the same way and AC coupled into REFCLKP/N (110/111).
  - It replaces the LIME line with pin checks: the hub's SSTX (U102 pins 3/4) reaches J_LIME 9/8 through one capacitor,
    and J_LIME 6/5 returns to the hub's SSRX (pins 6/7). This is W3's direction check in the gate's own terms.
- Evidence, all brought back under `drafts/box/check_pcb_b/`:
  - `drafts/check_pcb_b_emul.py` runs the gate's OWN net section on a netlist. It parses the check file with `ast` and
    executes exactly the statements of `if placed:` between the `bynet` loop and `import fnmatch`, with `bynet` and
    `bypad` taken from the netlist.
  - The committed gate on the committed netlist: 132 checks, 0 FAIL.
  - The committed gate on the round-4 netlist: 13 FAIL. That is the reviewer's seven (NVME/CARD1-3_RX_P, LIME_SSTX_P)
    plus the six NVME/CARD CLK lines, which now reach Rs and Rp instead of the switch. So without the patch the next
    board-phase gate fails.
  - The patched gate on the committed netlist: 159 checks, 46 FAIL. These are every crossed lane, every unterminated
    clock and all four LimeSDR legs of B21. The patched gate WOULD have caught W3-F01, W3-F02 and W3-F03.
  - The patched gate on the round-4 netlist: 159 checks, 0 FAIL.
  - With pcbnew, on the box, on the committed B21 board:
    - the committed gate reads ALL PASS of 2169;
    - the patched gate reads FAIL, 46 of 2196;
    - those 46 are line for line the emulation's 46 (`new_fails_on_B21.txt`);
    - no line the committed gate failed or reported goes away (`comm` of the two logs: 0 lines lost).
  - Until a placement seats the new parts (O-02), the patched gate fails B21 on exactly these 46. That is the truth
    about B21, the same fact SCH-002 reports.
- The integrator applies the patch in the same commit as the generator and its regenerated outputs (O-18).

**The review's minor items:**

| Minor | Done |
|---|---|
| S-01 fails open when +3V3_DEV is lost | The misleading comment is corrected in the generator. The review's remedy (KILL's 100 k up to +3V3_CM{s}) was NOT taken: it back-feeds the unpowered module in the normal slot-off state. See SD-B-14; the remedy is O-14 |
| J_IOCOFF_x on a through-hole land in the controller pockets | Now the SMD 1x02 land `PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left` (in KiCad 9's library on the box; pin_map_lands PASS 1098 of 1098), SD-B-16 |
| The jumper-fitted state drives TT_a pins of an unpowered H743 | Recorded in the generator's comment and as O-16 |
| SIM 2 and Figure 19: 0 Ohm near the module and 22 Ohm near the holder | Done: R287 to R289 (0 Ohm, C21189) at the module on RST/CLK/DATA, and R272's value says "at the module". The run between them is SIMR2_x, declared at 3.3 V. SD-B-07 and section 8 now agree. The TVS array stays O-04, so S-13 is PARTIAL |
| The +5V_S2 comment stated the burst as a fact | Rewritten: it is not computed on B. The 5.49 A coincident case is I-03 on board A |
| Supply margin at the RM520N and the buck's compensation | O-17 |
| R240 pulls RESET# (a 1.8 V pin) to 3.3 V | Confirmed from HD v1.1 Table 12 and Figure 12. Not changed in this pass; O-15 |
| sch_prov: the commit must carry the regenerated outputs | O-18 |
| "368 pins moved" against 112 itemised | The header counted the pins of added parts as moved. `drafts/netdiff_report.py` now states the two numbers apart. The first run was 112 moved pins plus 256 pins of the 129 added parts. After the fix-up it is 130 moved plus 334 pins of 168 added parts (section 6) |
| Evidence gaps (2199119-3 temperature, C696846, C114409's certified row) | Added to O-05 with the two new codes |
| ASSEMBLY.md:99 still names MAIN/DIV | Unchanged, O-09, integrator |

## 1c. Fix-up pass 2 (26 September 2026, 09:20 to 10:30 CEST)

This pass was started because the previous fix-up could not close B-2 (it did not own `check_pcb_b.py`), and the
round-5 re-review's own box run (`/root/r5rev/b`, 07:14 UTC) logged a new symptom. The integrator made this author the
writer of `check_pcb_b.py`. Every item below is resolved in the worktree or proven from a primary document.

**The two blocking items of the round-4 review:**
- **B-1 (REFCLKO termination): DONE since the first fix-up, re-verified.** The 36 resistors R{s}75 to R{s}86 are in
  this pass's netlist unchanged; check_contracts judges the 18 series parts "in series with a real pin on both sides"
  (ALL PASS 91 on 82dd1e4d). The edited gate checks every one of the nine terminated pairs (below).
- **B-2 (the board gate): DONE, applied.** `v2/ecad/tools/check_pcb_b.py` now carries the pad-level direction checks
  of `drafts/check_pcb_b-r4.patch` byte for byte (sha256 5d52b0e2...). Evidence:
  - with pcbnew on the committed B21 board (run 1, `drafts/box/r5-run1/t82/v/`): the committed gate ALL PASS of 2169,
    the edited gate FAIL 46 of 2196; `comm` of the two FAIL lists gives 46 new lines and 0 lost, and the 46 are
    line for line the first fix-up's 46 (`new_fails_on_B21.txt`). They are every crossed lane, unterminated clock
    and LimeSDR leg of B21, the truth about that board until a placement seats the new parts (O-02);
  - on this pass's netlist, the gate's own net section (`drafts/check_pcb_b_emul.py`, ast-extracted): edited 0 FAIL of
    159, committed 13 FAIL of 132; on the committed netlist, edited 46 FAIL of 159
    (`drafts/box/r5-run3/check_pcb_b/`).
  - the gate's tests on the box, in the suite below (test_board_gates, test_pair_gate, test_interfaces,
    test_gate_crash_guard, test_verdict_channel, test_driver_hygiene run there with pcbnew).

**The review's minor items that were still open, resolved in this pass:**
- **O-15, R240 on RESET#: fixed (SD-B-17).** R240 is removed; Q208 alone drives pin 67, as Quectel's Figure 12 draws.
  HD v1.1 Table 50 puts digital pins at 2.3 V absolute maximum, which the 10 k to 3.3 V exceeded.
- **O-16, the dark controller's TT_a pins: the reviewer's premise is refuted by the datasheet, no change.** DS12110
  Rev 10 Table 21: input voltage on TT_xx pins, absolute maximum 4.0 V (not relative to VDD); Table 22 note 3:
  "Positive injection is not possible on these I/Os and does not occur for input voltages lower than the specified
  maximum value". The generator's comment now states this instead of calling it an open item.
- **O-17, the 5G supply's margin and loop: fixed (SD-B-18).** Slot 2's card buck is set to 3.456 V and compensated for
  its 0.5 mF on DS41979's own equations; the first-order sag at a 4 A step goes from about 0.45 V to 86 mV.

**New in this pass, O-19: board B's paged schematic PDF was empty (SD-B-19, a drafted tool patch).**
- The re-review's log: "Page annotations object (page 1) is likely malformed. Too big: (10471)" and "sch_pages: 6 x 7
  cells, 0 pages kept of 42 tiles", with build_sch.sh exiting 0.
- Measured here (`drafts/box/r5-run3/run.log`, `annots.py` over mutool): KiCad's property popups are JavaScript link
  annotations, 10480 on this pass's one-page sheet (the committed B21 sheet 9561; board A 3614, C 1372, D 1622, E 1320,
  P 450). `mutool poster` copies all of them onto each of the 42 tiles (440160 in the tile PDF). Poppler refuses a
  page with more than 10000, pdftoppm writes blank tiles and exits 0, sch_pages.py keeps none, and `mutool merge`
  writes a 230-byte PDF with no page ("Pages: 0", "malformed page tree"). So every regeneration of board B after
  round 4 ships an empty schematic PDF without any gate noticing.
- `drafts/sch_pages-popups-r5.patch` (against 82dd1e4d; main has not touched these files since): build_sch.sh exports
  the sheet with `--exclude-pdf-property-popups` (a kicad-cli 9.0.9 option, read from its own help on the box);
  sch_pages.py refuses a multi-cell sheet on which no tile carries ink; tests/test_schematic_pages.py gains two tests,
  a rule on the export line and a fixture pair (a two-cell sheet with no ink must be refused, one with a filled square
  in one cell must give one page).
- Proven: on the runner, the two new tests FAIL on the unpatched tools and PASS on the patched ones (7 of 7 in that
  file). On the box, main 26b80900 plus this pass's two files plus the patch (tree t26p): build_sch.sh 0 poppler
  errors, paged schematic 38 pages; the six boards' committed schematics page to the same counts with and without the
  patch (A 11 of 12, B 37 of 42, C 5 of 6, D 6 of 6, E 4 of 4, P one page); test_schematic_pages and
  test_box_packages pass on t26p.
- Not my files, so it is a patch for the integrator; it should land in the same commit (O-19).

**Regeneration, parity and the difference (runs 2 and 3, `drafts/box/r5-run3/`):**
- The same generator (sha256 8a980c57...) on 82dd1e4d (t82) and on main 26b80900 (t26): W7's comparator reads
  schematic PARITY, netlist PARITY_AFTER_NOISE (content hash fe7fc5df9809f9ea on both), intent PARITY_AFTER_NOISE,
  BOM PARITY and ERC PARITY_AFTER_NOISE. Provenance reads DIFFERENT only in `generator_file_sha`, `generator_files`,
  `generator_sha` and `identity_since`, which is 6104cb81's new sch_prov identity on main, not a design change.
- The t26p netlist (with the paging patch) equals t26's: 0 components, 0 pins, 0 nets different.
- The round-4 baseline `/root/r4/b/out/base/pcb-b-compute.net` equals main's committed netlist byte for byte.
- This pass against the first fix-up (`drafts/box/netdiff-r5-pass2.txt`): R240 removed; R202 31.6k to 33.2k 1%
  (C23003); R205 22k to 120k 1% (C25808); C298 added (68p C0G, C107009, S2A_COMP to GND); Q208's value text. Nothing else.
- Against the committed B21 netlist (`drafts/box/netdiff-r5.txt`): 931 to 1099 components (169 added, 1 removed, 21
  changed), 1852 to 1929 nets, 132 pins of existing components on another net (the first fix-up's 130 plus R240's two),
  336 pins of the added parts. Section 6 lists them by item.

**Gates (run 3; on t82 = 82dd1e4d plus the two files, and t26 = main 26b80900 plus the two files):** see section 5.
On t26 check_contracts reads INCONCLUSIVE (84, 0 FAIL) because A, C, D, E and P carry sidecars written before
6104cb81's identity; main as committed (tmain) reads INCONCLUSIVE of 48 with all six boards so. That is main's state,
not this change: on 82dd1e4d the same netlist reads ALL PASS 91.

## 1d. Fix-up pass 3 (26 September 2026, 10:40 to 11:40 CEST): the round-5 re-review's blocking item

The re-review (APPROVE_WITH_FIXES) confirmed B-1, B-2, O-15, O-16, O-17 and O-19 and found one blocking item: with the
panel absent, EMCON_HW is lifted to a logic HIGH, so I-04's "B's radios are dark" was false. **The reviewer is right,
and it is fixed in the circuit (SD-B-20, SD-B-21), in the gate (check_pcb_b.py) and in the record (I-04, O-08).**

**The defect, measured on the netlist and the datasheets.**
- Q106, Q206 and Q306 (CJ 2N7002, SOT-23 1 G 2 S 3 D) had G on +3V3_S{s}A, S on W_DISABLE1# (R{s}37 10 k up to
  +3V3_S{s}A) and D on EMCON_HW. The body diode's anode is the source, so it conducts from W_DISABLE1# into EMCON_HW.
- With the ribbon out, or board C's U9 unpowered, EMCON_HW is held only by R58 (100 k) and A's R102 (100 k).
- Slot 2's +3V3_S2A is not EMCON-gated (it follows PCIE_PWR_EN2), so it is up whenever slot 2's module runs.
- EMCON_HW then settles at about (3.456 V - 0.5 V) x 50 k / 60 k = 2.46 V, above the SN74LVC08A's VIH of 2.0 V
  (SCAS283W 5.4). U19, U20 and A's U26 read "no EMCON", Q11 pulls EMCON_ON low, and the kill gates, the slot 1 and 3
  card supplies and (by the same path) their W_DISABLE1# are released.
- The committed B21 netlist has the same wiring (`drafts/box/r6-run4/check_pcb_b/emul-pass3-gate-on-committed-net.txt`).

**What changed in the generator** (sha256 `9b85ada81f0adab67fcef2f3e6e969a9f755c55314dc9bd77962af38e9483d84`):
- Q106, Q206, Q306: gate EMCON_ON, source GND, drain WIFI_W_DIS_n / 5G_W_DIS_n / WIFI2_W_DIS_n; R{s}37 unchanged
  (SD-B-20). Value text "2N7002: EMCON_ON pulls W_DISABLE1# low (open drain)".
- R58: 100 k to 10 k (SD-B-21).
- Comments: the new block above the card sockets, the R58/Q11 block, and (re-review minors 1 and 4) the buck33
  docstring and the O-17 comment now state what the 68 k RT sets and give Eq. 19 with its max() second term. No other
  line of the generator changed.

**What changed in the gate** (check_pcb_b.py sha256 `720892aefe56ceb2dff099b16dd7421d2f78c42b86ccb49629085872a834c324`;
run 4 ran `70a03fe8...`, which differs only in how two messages print a transistor's pads: pcbnew and the netlist
iterate pads in different orders, so the final file prints them as a fixed "G .. S .. D .." and a line reads the
same from a board and from a netlist), in its net section after the LimeSDR checks, on pads:
1. every resistor on EMCON_HW goes to GND or a signal, never to a rail;
2. every transistor on EMCON_HW meets it with pad 1 (the SOT-23 gate) only;
3. no other pad of such a transistor reaches a slot rail (+3V3_S*, +3V3_M2C*, +3V3_CM*, +1V8_CM*, +5V_S*, +1V0_S*,
   +1V1_S*) directly or through one resistor, which is the re-review's rule;
4. Q11 inverts EMCON_HW into EMCON_ON with its pull-up to +3V3_DEV, and each Q{s}06 is the open drain from EMCON_ON
   onto its socket's W_DISABLE1# (J_M2C1.56, J_M2C2.8, J_M2C3.56) with one pull-up to its own card rail.

**Evidence** (`drafts/box/r6-run4/`):
- The gate's own net section, emulated (`drafts/check_pcb_b_emul.py`):

| Gate | Committed netlist (82dd1e4d) | Pass 2 netlist | Pass 3 netlist |
|---|---|---|---|
| Committed gate | 0 FAIL of 132 | 13 FAIL of 132 | 13 FAIL of 132 |
| Pass 2 gate | 46 FAIL of 159 | 0 FAIL of 159 | 0 FAIL of 159 |
| Pass 3 gate | 56 FAIL of 170 (the 46 plus 10 EMCON lines) | 9 FAIL of 172 (Q106/Q206/Q306: 2 each, plus 3 W_DISABLE1# lines) | 0 FAIL of 166 |

- Mutation controls (`drafts/check_pcb_b_emcon_mutations.py`, `check_pcb_b/emcon-mutations.txt`): on the pass 3
  netlist, five planted defects are each caught (a resistor from EMCON_HW to +3V3_DEV; B21's stage back on slot 2; a
  new FET with its source on EMCON_HW and its drain pulled to +3V3_M2C3; a gate-only FET whose drain sits on +5V_S1;
  Q306 with source and drain swapped), and the unmutated netlist reads 0 FAIL.
- With pcbnew on the committed B21 board (box, t82): pass 3's gate FAIL 56 of 2207 (the 46 of pass 2 plus the same 10
  EMCON lines). That is the truth about B21, which carries the back-feed. Run 5 repeated it with the final gate file: FAIL 56 of 2207, 0 of
  pass 2's 46 lost and 0 of the committed gate's lines lost, and the 10 new lines are byte for byte the emulation's 10
  (`drafts/box/r6-run5/v/new_vs_pass2.txt`). The full suite on main 29f00554 plus the two files: 1470 passed, 0
  failed, 12 skipped.
- The schematic-phase gates and the netlist differences are in sections 5 and 6. Against pass 2 exactly nine pins moved
  (Q106, Q206 and Q306, three each) and four value texts changed (the three FETs and R58). Nothing else changed: no
  part, net or intent entry was added or removed.

**The re-review's minors, answered in this pass:**
- Minor 1 (AP64500 RT): the reviewer is right (DS41979 Rev 5-2 Eq. 7 and the electrical table: 68 k sets 1.47 MHz).
  SD-B-18's "fsw/10 = 50 kHz" and "against 5.3 pF" are corrected, and the comments are corrected in the generator.
  The frequency itself is new open item O-20, on boards A and B, because the recipe is shared with A.
- Minor 2 (O-15): the 80 nA IDSS is recorded as the datasheet's 25 C, VDS 60 V figure.
- Minor 3 (O-16): the caveat is recorded (dark-part leakage is unspecified by Table 60).
- Minor 4 (Eq. 19 in the comment): corrected.
- Minor 5 (O-19's failure message): recorded as cosmetic in O-19; the proven patch is unchanged.
- Found while fixing, not asked: the same stage topology on PI_KILL, PI_SHDN_REQ, GNSS_PPS and HB1 to HB3 (O-21),
  and the stale b.json text and safe_lines' blind spot for a sourcing path (O-22).

## 1e. Round 6 (26 September 2026, 12:40 to 13:40 CEST): O-18 rebuilt on main faf8c981, and R4T-F9

Main moved to `faf8c981` (boards C, D, E and P landed with their round-4 corrections; A, B and the shared tools were
held). The pass-3 re-review (APPROVE_WITH_FIXES) had one blocking item, O-18's file list, and the round-5 tools
re-review ruled R4T-F9 in scope for board B. Both are done here. Files: generator sha256
`6e3d880901fd30306c0fa8bda35a86da6450d7e4bb15217f9cc3225da8d5faef`, check_pcb_b.py sha256
`28904a37f2f1810399e553f522d73fcc7848afc4d6ce3cce21556bffd70ccd4d` (diffs against pass 3: `drafts/box/gen_sch_b-r6.diff`,
`drafts/box/check_pcb_b-r6.diff`; pass 3's files reconstructed from them hash to 9b85ada8... and 720892ae... exactly).
Box run 6: vast.ai 52646493, `/root/r6/b/out6` only, fetched to `drafts/box/r6-run6/` (script `drafts/box/r6b_box6.sh`,
runner reading `drafts/box/r6b_post6.sh`).

**O-18, the blocking item: the reviewer is right, and the set now carries every file the regeneration moves.** The
suite's `test_assembly_set` runs `assembly_set.py --checklist` with no path and so rewrites the tree's own
`v2/release/revA/order/ROTATION-CHECKLIST.md` from the tree's netlists; the regenerated B netlist moves that page, and
the pass-3 list left it out. Rebuilt on faf8c981 in the integration tree `tint` (main + the two files + the O-19 patch,
B regenerated in place), the checklist moves by exactly these lines and no others (`drafts/box/r6-run6/tint/rotation-checklist.diff`):

```
@@ -14,6 +14,7 @@
 | `BatteryHolder_Keystone_3034_1x20mm` | B | BT1 |  |  |
+| `CP_EIA-3528-21_Kemet-B` | B | C520 |  |  |
 | `CP_Elec_6.3x7.7` | E | C11 |  |  |
@@ -38,6 +39,7 @@
 | `PinHeader_1x02_P2.54mm_Vertical` | B | J_RPIBOOT1 |  |  |
+| `PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left` | B | J_IOCOFF_A |  |  |
 | `PinHeader_1x03_P2.54mm_Vertical` | B, E | J_GNSS2 |  |  |
@@ -57,4 +59,4 @@
-43 footprint(s) to compare, over 7 board(s).
+45 footprint(s) to compare, over 7 board(s).
```

On faf8c981 the page reads 43 (C, D, E and P already moved it from 44), so B takes it to 45, not the 46 the pass-3
re-review read on 29f00554. The two rows are C520/C521 (KEMET T520B, F-PR-05) and J_IOCOFF_A/B/C (SD-B-16); the four
new resistors of this round are not polarised and add no row. On clean faf8c981 main's own tool rewrites the committed
page byte for byte, so the diff is B's alone.
The same check found a second page O-18 lacked: **`v2/docs/PCB-BRING-UP.md`**, generated by `rules_render.py` from each
board's intent file. On clean faf8c981 `rules_render.py --check` refuses only PCB-ETA.md (a fresh tree holds no routeflow
journal, the integrator's finding); on tint it also refuses PCB-BRING-UP.md. Re-rendered with `--no-refresh`, PCB-ETA.md
put back to HEAD, it moves by 18 insertions and 15 deletions in board B's tables, every line from round-4 items
already in the netlist diff: +5V_S2 2.50 A to 4.20 A (F-PR-05, I-03), the three socket segments +3V3_M2C1/2/3 as new
derived rails behind R165/R265/R365 (F-PR-05, TESTACCESS-B Kelvin shunts), +3V3_S2A 3.46 V 3.00 A (F-PR-05, O-17/SD-B-18)
and the S1A/S3A loads now the shunts (`drafts/box/r6-run6/tint/docs-rerender.diff`). After it, `--check` refuses only
PCB-ETA.md again, as on clean main. `decisions_render.py --check` reads the same on tint as on clean main
(OWNER-DECISIONS-OPEN.md only). The full list is O-18 in section 7; the suite result on exactly that tree is in the evidence below.
For the suite owner (recorded in O-18): `test_assembly_set.t_the_checklist_flag_answers_a_missing_path_instead_of_raising`
writes the tree's own page; it should pass a temporary path.

**R4T-F9: pull-downs on the EMCON-gated enables (SD-B-22).** R514 (LIME_EN), R515 (RB_EN), R516 (E22_EN) and R517
(E72_EN), 10 k to GND. The basis is in SD-B-22: SCAS283W publishes no Ioff for the SN74LVC08A, so the sizing takes the
SN74LVC1G08's guaranteed 10 uA (SCES217AA) plus 0.1 uA of EN leakage; 10.1 uA into 10 k is 0.10 V, against the
TPS259631's VSD 0.53 V and VUVLO(F) 1.08 V minimum and the TPS22810's VSHUTF 0.5 V and VENF 1.08 V minimum. The gate
(check_pcb_b.py, net section, after the EMCON_HW block) asserts on pads that each of the four nets carries the gate's
output pad, the switch's EN pad and exactly one resistor, to GND, of 200 Ohm to 49.5 kOhm; the two bounds are computed
in the gate from the sheets' figures. A new `byval` map (reference to value, filled in the pad loop) gives it the size;
`drafts/check_pcb_b_emul.py` supplies the same map from a netlist.

**Evidence** (`drafts/box/r6-run6/`):
- Regeneration: `gen_sch_b.py` compiles under -W error, the swallowed-calls test exits 0, 1151 parts (pass 3: 1147),
  915 nets, 0 unintended single-pin nets, build_sch.sh exits 0; the paged schematic on tint (with the O-19 patch) has
  38 pages and 0 poppler errors.
- Parity: main's own generator on faf8c981 against the committed B21 files: schematic, netlist and intent
  PARITY_AFTER_NOISE, so the committed netlist is the base the diff below is taken from. t6 (main + the two files)
  against tint (the same plus the O-19 patch): schematic PARITY, netlist, intent, provenance and ERC
  PARITY_AFTER_NOISE, BOM PARITY, so the patch touches none of the four artefacts.
- The gate with pcbnew on the committed B21 board (t6): this round FAIL 60 of 2211; pass 3's gate FAIL 56 of 2207
  (the same as run 5 on 29f00554); committed gate ALL PASS. The 4 new lines are exactly LIME_EN, RB_EN, E22_EN and
  E72_EN with no pull-down, the truth about B21; 0 lines of pass 3's and 0 of the committed gate's are lost
  (`t6/v/new_vs_pass3.txt`, `lost_vs_*.txt`).
- The gate's net section emulated, and the mutation controls: section 5.
- Schematic-phase gates (t6): section 5. Every one reads as in pass 3 apart from the four resistors (ERC 2398, 5
  allowed errors, the same five; pin_map_lands 1102).
- The full suite once, on the integration tree exactly (tint, the 11 files of O-18): 1472 passed, 0 failed, 12
  skipped, and `git status` read the same before and after it, so no test rewrites a committed file of this set. The
  12 skips are listed with their reasons in section 5.
- Netlist differences: section 6. Against pass 3, four components added (R514 to R517) and nothing else.

**The pass-3 re-review's minor items:**
- Minor 1 (O-14 "not a regression" is wrong for W_DISABLE1#): the reviewer is right; O-14 corrected, with the
  per-slot inverter remedy recorded as the candidate. Not built in this round (a new circuit with its own review).
- Minor 2 (0.3 mA misstated): corrected in gen_sch_b.py, check_pcb_b.py, SD-B-20, O-08 and I-04.
- Minor 3 (PC5 pull-up): the firmware line is in O-06, the Table 60 note 4 arithmetic in O-08.
- Minor 4 (EMCON_ON's RC edge into the SN74LVC32A, 7 ns/V): new O-23.
- Minor 5 (the EMCON block's heading): narrowed to what it checks ("no pull-up, no transistor channel and no slot rail
  may reach it"); the allow-list idea is recorded, not built.
- Minor 6 (O-22, b.json text): unchanged, the integrator's. Minor 7 (O-21): the two points are added to O-21.
- Minor 8 (Q11's IGSS is a 25 C figure): recorded in O-08. Minor 9 (box disk): the box read 41 percent used at the
  start of this run.

## 2. Decisions taken by the session under the owner's standing rule of 26 September 2026

Each was an engineering choice with more than one option; none spends money, changes a reserved class or changes what
the kit is claimed to be. Each is taken by the session under the owner's standing rule of 26 Sep 2026.

**SD-B-01, S-01: how the module radio pins are driven.**
Options:
- (a) Keep U6 on the pins. This is refused by the CM5 datasheet: "may only be driven low", and "No pins should be powered before the 5 V rail is active".
- (b) A 2N7002 in the board's level-stage orientation, gate on the module's 3.3 V, driven by an AND of enable and EMCON. My first draft did this. It was rejected on review because the stage is bidirectional: if the module ever drives the pin low internally ("The WL_nDisable pin indicates the enable/disable state"), the FET turns on into a push-pull high, which is contention.
- (c) A true open drain: a 2N7002 with its source on GND and its drain on the pin, gated by OR(software off request, EMCON_ON).

Taken: (c). The pin is only ever pulled low, which the datasheet allows ("driven or tied low"). There is no contention in any state, and with the module off a pull-down powers nothing. The requests are active-high OFF with 10 k pull-ups, so the power-on state is radios dark by design. It does not depend on the PCA9555's internal pull-up (A01).
Cost per slot: one SN74LVC32APWR (C352974, already on the board), two 2N7002, two 10 k, two 100 k and one 100 nF. Plus one shared inverter Q11 with R513, which adds one FET gate to EMCON_HW instead of five logic inputs.

**SD-B-02, S-01: the two AW7915-AED cards under EMCON.**
Options:
- (a) W_DISABLE1# only, counted after a bench proof.
- (b) Remove the card's supply in hardware, and keep W_DISABLE1# as well.

Taken: (b). D-05 is "radios dark", and no maker's document states what W_DISABLE1# does on an MT7915 card.
How it is built: the buck enable S{s}A_EN follows PCIE_PWR_EN through 10 k, and Q{s}11, gated by EMCON_ON, pulls it low.
Consequences, recorded as O-06:
- After EMCON is released, the host must re-enumerate the card.
- While the card is unpowered, PERST# (the switch's DWNRST_L2) and PEWAKE# (10 k to +3V3_S{s}B) can feed its I/O. This path already existed whenever PCIE_PWR_EN was low with the module up.

**SD-B-03: the RM520N-GL supply is not gated by EMCON.**
Quectel documents W_DISABLE1# as airplane mode, in which "the RF function is invalid" (HD v1.1 3.1 and 3.1.2). It also writes "To avoid corrupting the data in the internal flash, DO NOT cut off the power supply before the module is completely turned off" (3.3.2).
The maker-documented hardware RF disable is therefore W_DISABLE1#, which is already on EMCON through Q206. This answers S-01's "decide whether 32.56's 5G supply switch is built": it is not built.

**SD-B-04, S-08: R60 to R62 (KSZ_RST, 5G_OFF, 5G_RESET).**
Options:
- (a) Leave them at 100 k. The states are then "nominally asserted" by the expander's pull-up: the gate sits near 1.7 V against a 1.0 to 2.5 V threshold, so they are undefined.
- (b) 4.7 k pull-downs. These give defined off states: the Ethernet switch runs, and the 5G module is neither held off nor held in reset.
- (c) Pull-ups, which assert them by design.

Taken: (b). A01 lists it as optional and recommends defined states.
- The M.2 default is the module powered.
- EMCON on the 5G module does not depend on this expander.
- Holding the Ethernet switch in reset until the panel firmware runs would take every module's network down for no safety gain.

**SD-B-05, F-PR-05: the two 220 uF.**
Options:
- (a) KEMET T520B227M006ATE025: EIA 3528, 25 mOhm, 2300 mA ripple at 45 C, -55/+105 C, C212684, 6571 in stock (JLC reading 26 Sep 2026 01:15 CEST).
- (b) Panasonic 6TPE220MI: 7343, 18 mOhm, C129173, 14511 in stock.
- (c) Aluminium polymer cans.

Taken: (a). Board B is the most crowded board (every region overflowed on B22/B23, `boards/b.json`). A 3528 case uses about 40 percent of the area of a 7343. 25 mOhm per part, two in parallel, meets "low ESR" as the HD uses it.

**SD-B-06, TESTACCESS-B: how the card-socket current is measured.**
Options:
- (a) A Kelvin shunt with two pads.
- (b) An INA226/INA219 on the kit bus. That adds a part family and three I2C addresses on a bus board A already fills with INA226s.
- (c) A 0 Ohm link that an ammeter replaces. The meter's burden would then sit in the 5G supply path.

Taken: (a). A 5 mOhm LR2512D-3W-5mR-1% (C500739, already certified for board A) sits after the buck's output capacitors, with TP{s}02 and TP{s}03 as the Kelvin pads.
At the 5G module's 4 A peak the drop is 20 mV of the 185 mV between the 3.32 V set point and the RM520N's 3.135 V minimum. The buck's feedback stays on the buck side.

**SD-B-07, S-13: the SIM circuit.**
The HD asks for 22 Ohm near the holder (Figure 18) and, for an eSIM-capable SIM 2, 0 Ohm links near the module (Figure 19).
The first round-4 draft used one part per line and could not honour both placements. The review caught it. Taken in the fix-up:
- 22 Ohm in RST, CLK and DATA of both SIMs, AT THE HOLDER (R266 to R271).
- On SIM 2 only, four 0 Ohm links AT THE MODULE: R287 to R289 on RST, CLK and DATA, and R272 on VDD (UNI-ROYAL 0603WAF0000T5E, C21189, already certified for board E).
- Net names: the module side is SIM2_x, the run between the parts is SIMR2_x, and the holder side is SIMC2_x.
- DET (pin 40) is open, as the HD asks when hot-plug is not used, so it needs no fifth link.

The second physical nano-SIM is kept, because the approved gap list names dual SIM. An eSIM-fitted module variant is built by leaving SIM 2's four 0 Ohm links off, as HD 4.1.6 requires ("pins 40, 42, 44, 46 and 48 ... must be kept open"). No stub is then left on the module's pins.
The optional 10 to 20 k DATA pull-up is not fitted. The HD calls it optional, and the module drives the line.

**SD-B-08, W5-F3: PB6/PB7 over PB10/PB11.**
Both pairs are free and I2C capable (DS12110 Rev 10 Table 11: PB6/PB7 AF4 I2C1, PB10/PB11 AF4 I2C2). Taken: PB6/PB7.
- They are FT_f/FT_fa, 5 V tolerant with Fm+, so an unpowered supervisor (IOHA A4/A6) does not clamp the powered kit bus through a protection diode to its dead VDD.
- PB10/PB11 are FT_f too. The tie-break is the standard I2C1 mapping.

**SD-B-09, TESTACCESS-B (A7): the CAN break links.**
Options:
- (a) Pads only, and short CANH to CANL to kill a fabric.
- (b) A 0 Ohm pair per fabric between controller A's pocket and the B/C segment.
- (c) A jumper header in the bus.

Taken: (b), plus pads on CANH/CANL of each fabric (TP535 to TP538), so both a partition (remove the links) and a dead fabric (short the pads) can be tested.
The links sit at A's end, and A's segment keeps the west termination R470 to R473 (IOCA pocket in `gen_pcb_b3.py`).

**SD-B-10, TESTACCESS-B (A4/A6): supervisor power.**
Taken: EN pulled to +5V_DEV through 100 k, with a two-pin bench jumper to GND (J_IOCOFF_x), not fitted in service.
The rejected alternative was a 0 Ohm link in the EN path, which needs a soldering iron for every run of the test.

**SD-B-11: net names for the corrected PCIe links.**
The switch side of each new capacitor is `*_RX_SW_*` and the socket side keeps `*_RX_*`. This keeps the device-side naming the board already used, and it matches the class patterns `NVME*_RX_*`, `CARD*_RX_*` and `PCIE*_RCLK*` in `boards/b.json` and `pcb_interfaces.yaml`. Neither file is mine, so a name that matched no pattern would have left the new nets unclassified.
The module-radio nets are `WL_nDIS*_OFF` and `WL_nDIS*_KILL`, matching `WL_nDIS*` and `BT_nDIS*`. EMCON_ON matches `*_ON`.

**SD-B-12, F-PR-05: +5V_S2's declared typical current is 4.1 A; its peak stays 5.0 A.**
The typical current adds up as follows:
- `power_path` sums the slot's three converters at their declared typical currents: 3.05 A on slot 2, of which 2.21 A is the card buck.
- The CM5 module's own draw is 0.9 A (Table 9), and the fan's is 0.1 A.
- Total: 4.05 A, where 2.5 A was declared.

On the peak side: the loads stay apportioned to 4.75 A, under the 5.0 A peak, and the 5G burst is carried by the socket bulk. The coincident worst case, 5.49 A, goes to board A in r4-interfaces.md.

**SD-B-13: explicit order codes on the new ceramics.**
The HD's values (6.8 nF, 220 pF, 68 pF, 15 pF, 9.1 pF, 4.7 pF, 10 pF) have no `lcsc_fill.py` entry, and that file is not mine. The generator names YAGEO CC0402 codes directly: C93654, C107001, C107009, C106997, C526972, C325453, C106199. This is the family board B already buys, and each code was read back from JLCPCB on 26 Sep 2026.

**SD-B-14, fix-up (S-01 minor): the kill gate fails open if +3V3_DEV is lost, and the review's remedy is not taken.**
Options:
- (a) Keep round 4's circuit and correct its comment. With +3V3_DEV lost and a slot up, KILL sits at 0 through R{s}73/R{s}74 and the module radios are released. That is how U6's direct drive behaved before round 4, so it is not a regression.
- (b) The review's remedy: take R{s}73/R{s}74 up to +3V3_CM{s}. This fails dark. But in the NORMAL slot-off state (requests high by default, so KILL high) U{s}11 then drives 3.3 V through 100 k into the unpowered module's CM5_3.3V: 33 uA per line, 66 uA per slot, continuously. The CM5 datasheet 3.1 says "No pins should be powered before the 5 V rail is active".
- (c) A diode per line, so U{s}11 can only pull KILL low, with 10 k from KILL to +3V3_CM{s}. This fails dark with no forward path into the unpowered rail. It adds six diodes and a part choice, and it needs a leakage analysis: a reverse-biased BAT54 leaks microamps at 85 C into the same rail, and a 1N4148W's forward drop leaves only a few tenths of a volt below the 2N7002's 1.0 V minimum threshold (an estimate, not yet computed from datasheets).

Taken: (a) now, with (c) written down as O-14. (b) trades a rare failure (U26 lost with a slot up) for a back-feed in every slot-off state. (c) is a new circuit and deserves its own review, not a fix-up line.

**SD-B-15, fix-up (B-1): how the REFCLKO outputs are terminated.**
Options:
- (a) The Table 8-1 load at the source: 33.2 Ohm series, then 49.9 Ohm to ground on the line side.
- (b) 49.9 Ohm to ground only.
- (c) Hold W3-F03 open until a Diodes reference schematic or EVB is found.

Taken: (a). It is the only configuration DS40068 characterises its VHIGH, VLOW, Vcross and edge limits in, and it is the review's required fix. (b) is outside what the datasheet measured. (c) leaves a board on which no PCIe link trains.
- 0603 rather than 0402: it is board B's resistor land and the UNI-ROYAL 0603WAF family the board already buys. C23185 is a basic part; C23004 is extended.
- Placement at the switch is a layout instruction (section 8).

**SD-B-16, fix-up (minor): the J_IOCOFF_x land.**
Options:
- (a) The through-hole PH1x2 of the first draft.
- (b) The SMD 1x02 header land `PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left`.
- (c) A solder-jumper pad pair.

Taken: (b). SD-B-10 wants a jumper that needs no soldering iron, and the file's 17 September 2026 record says a through-hole header in these pockets cost 29 hard violations. That is the reason the SWD land U42/U52/U62 is PH1x5S.

**SD-B-17, fix-up pass 2 (O-15): RESET# of the 5G module.**
Options:
- (a) Keep R240, 10 k from 5G_RST_n to +3V3_S2A.
- (b) Remove R240 and leave Q208 (2N7002, open drain) as the only host part on the pin.
- (c) Re-reference the pull-up to a 1.8 V source.

Taken: (b). RESET# (pin 67) is a 1.8 V DI "Internally pulled up to 1.8 V" (HD v1.1 Table 12; Figure 12 draws a 1.5 uA
source), and HD Table 50 gives "Voltage at Digital Pins" an absolute maximum of 2.3 V, so (a) held the pin above its
absolute maximum whenever the module ran. Quectel's own circuits (Figures 12 and 13) are an open collector or a button
with nothing else on the pin: "An open collector/drain driver or a button can be used to control RESET#" (HD 3.6).
(c) needs a 1.8 V source B does not have at that socket. Q208's off-state leakage is at most 80 nA at VDS 60 V (CJ
2N7002 datasheet, IDSS, C8545, drafts/datasheets), a twentieth of the 1.5 uA pull-up, and R62 (4.7 k) holds its gate
low. Taken by the session under the owner's standing rule of 26 Sep 2026.

**SD-B-18, fix-up pass 2 (O-17): slot 2's card buck, set point and compensation.**
Options:
- (a) Keep the recipe (31.6 k / 10 k, 3.328 V; 22 k / 3.3 nF compensation) under the two 220 uF polymer capacitors.
- (b) Keep 3.328 V and redesign only the compensation.
- (c) Redesign the compensation and raise the set point toward the module's nominal.

Taken: (c), on the AP64500's own equations (DS41979 Rev 5-2, v2/vendor/diodes/diodes-ap64500.pdf, sha256 d3bcdc7d...):
- Eq. 17, R5 = 4.67e3 x fc x VOUT x COUT (gm 0.15 mS, RT 0.089 V/A). COUT on this rail is about 0.50 mF: three
  22 uF X7R at their DC bias (about 53 uF), the socket's 22 uF (about 11 uF) and 2 x 220 uF polymer. With (a)'s 22 k
  the loop crosses over at 2.8 kHz, a mid-band output impedance 1/(2 pi fc COUT) of 0.11 Ohm: a 3 A step sags about
  0.34 V, below the module's 3.135 V from any set point in the M.2 range. That is (a) and (b)'s set point refused.
- R205 = 120 k: fc 14.7 kHz at 0.50 mF (18 kHz at 0.41 mF, 12 kHz at 0.62 mF), at the datasheet example's 15 kHz and
  far below fsw/10 at either switching frequency (147 kHz at the 1.47 MHz the fitted 68 k RT actually sets, 50 kHz at
  500 kHz; fix-up pass 3 corrects "fsw/10 = 50 kHz", see O-20); about 21 mOhm, so a 4 A step sags 86 mV.
- C5 (Eq. 18) = VOUT x COUT / (IOUT x R5) = 3.6 nF at 4 A: C217 stays 3.3 nF, its zero at 402 Hz on the 365 Hz load
  pole.
- C6 (Eq. 19) = max(RC x COUT / R5, 1 / (pi fsw R5)) = 52 to 84 pF for RC 12.5 to 20 mOhm (two 25 mOhm polymers, the
  shunt and copper between them and the sense point) against the second term's 1.8 pF at the fitted 1.47 MHz (5.3 pF
  at 500 kHz; fix-up pass 3 corrects "against 5.3 pF"): new C298, 68 pF C0G (C107009, already on this board), a pole
  at 19.5 kHz on the polymer's ESR zero (18 to 29 kHz).
- Set point: R202 = 33.2 k (C23003), 0.8 x 4.32 = 3.456 V, worst case 3.369 to 3.545 V (VFB 792 to 808 mV, 1 percent
  resistors). The module allows 3.135 to 4.4 V with 3.7 V nominal (HD v1.1 3.3.1); at nominal the rail is also inside
  the M.2 3.3 V + 5 percent (3.465 V) that any other key-B card would expect.
- Budget, 4 A step from idle at the worst set point: 3.369 V - 20 mV shunt - 50 mV ESR step (4 A x 12.5 mOhm) - 86 mV
  loop sag = 3.213 V, 78 mV above the module's minimum left for copper. The two drops are summed although in a
  first-order model they do not peak together.
- The rail keeps its name and declares 3.456 V (derate: the 6.3 V polymers at 55 percent, the SMBJ5.0A's 5.0 V
  standoff above 3.545 V). W_DISABLE1# (pin 8, 3.3 V I/O VIH max 3.6 V, HD Table 46) and FULL_CARD_POWER_OFF#
  (VIH max 4.4 V) stay inside their limits on the 10 k pull-ups to this rail. The new COMP node S2A_COMP is declared
  at its supply, +5V_S2.
- Knock-on: +5V_S2's typical goes 4.1 to 4.2 A (the card buck draws 2.31 A at 5.1 V instead of 2.21), and the
  coincident peak of I-03 goes 5.49 to 5.63 A (drafts/r4-interfaces.md). Both rest on an efficiency of 0.88 read for
  500 kHz; at the 1.47 MHz the RT actually sets, that figure is not measured (O-20).
Taken by the session under the owner's standing rule of 26 Sep 2026.

**SD-B-19, fix-up pass 2 (O-19): the paged schematic PDF.**
Options:
- (a) Export the sheet without KiCad's property popups (`--exclude-pdf-property-popups`, a kicad-cli 9.0.9 option).
- (b) Render the tiles with `mutool draw` instead of `pdftoppm`.
- (c) Split board B's schematic into sheets.

Taken: (a), with a refusal in sch_pages.py when no tile carries ink, drafted as `drafts/sch_pages-popups-r5.patch`
because build_sch.sh, sch_pages.py and their test file are not my files. (b) would still ship a paged PDF of 42 pages
each carrying all 10480 annotations, which poppler-based viewers refuse page by page. (c) is a layout-engine change.
Taken by the session under the owner's standing rule of 26 Sep 2026.

**SD-B-20, fix-up pass 3 (the round-5 re-review's blocking item): how EMCON reaches each card's W_DISABLE1#.**
The evidence: the stage Q{s}06 (gate on the card rail, source on W_DISABLE1# with R{s}37 10 k up to it, drain on
EMCON_HW) puts the MOSFET's body diode, anode at the source (CJ 2N7002 datasheet, sha 7941fb42..., VSD 0.55 to 1.2 V
at 115 mA), between a live card rail and EMCON_HW. With nothing driving EMCON_HW each stage sources current into R58
and A's R102 (up to 0.35 mA into a line at 0 V, 3.456 V / 10 k; about 50 uA against the 50 k that holds it,
(3.456 - 0.5) V / 60 k; corrected in round 6 from 'about 0.3 mA', the pass-3 re-review's minor 2) and lifts the line to about 2.3 to 2.5 V, above the SN74LVC08A's VIH of 2.0 V (SCAS283W 5.4).
Options:
- (a) Keep the stages and correct the claims (I-04, S-01): with the panel absent the kit is NOT dark while any card
  rail is up. Refused: D-05 is "radios dark", and slot 2's rail comes up with its module, so a booted 5G module alone
  would release every EMCON gate on B and on A.
- (b) Keep the stages and block the body diode with a series diode in each drain. Refused: the stage pulls W_DISABLE1#
  low by conducting from W_DISABLE1# into EMCON_HW, which is the body diode's own direction, so a diode that blocks one
  blocks the other.
- (c) Drive each W_DISABLE1# from a logic output on +3V3_DEV (the spare gates of U20). Refused: a push-pull high on
  +3V3_DEV into a card whose rail is off powers its pin, the back-feed O-06 already records for PERST#.
- (d) An open drain from EMCON_ON: Q{s}06 gate EMCON_ON, source GND, drain on W_DISABLE1#, R{s}37 kept to the card
  rail. It has no path from a card rail to EMCON_HW or EMCON_ON (gate insulated, drain diode to GND only), it pulls the
  pin low only, which is what an open-drain M.2 input expects, and it adds no part.
Taken: (d), the re-review's preferred remedy. Its cost: W_DISABLE1# now needs +3V3_DEV (R513) to be asserted, as the
module kill gates and the slot 1 and 3 supply switches already do (O-14, whose scope grows). A dedicated second
inverter for the cards would keep them independent of Q11, but U19 and U20 already read EMCON_HW directly for the
other five transmitters, and Q11 is one part of the same class as each Q{s}06.
check_pcb_b.py now asserts four properties of EMCON_HW on pads (section 1d). Taken by the session under the owner's
standing rule of 26 Sep 2026.

**SD-B-21, fix-up pass 3 (O-08): R58, the pull-down that holds EMCON_HW low with the panel absent.**
The evidence: with the sourcing path gone, what is left is input leakage. At the datasheet maxima (-40 to +85 C):
six SN74LVC08A inputs at +-5 uA (SCAS283W 5.7; B's U19 pins 1, 9, 12 and U20 pin 1, A's U26 pins 1 and 4), three
STM32H743 TT_a inputs at +-250 nA (DS12110 Rev 10 Table 60, PC5 of U41/U51/U61, while powered) and Q11's gate at
80 nA (CJ 2N7002 IGSS), 30.8 uA in all. A dark board C cannot lift the line: its U9 and R14 sit on its own dead +3V3.
Options:
- (a) Keep 100 k (50 k with A's R102): 30.8 uA gives 1.54 V, above the LVC08's VIL of 0.8 V (SCAS283W 5.4). The
  panel-absent LOW is not proven.
- (b) 10 k (9.09 k with R102): 0.28 V; the line reaches 0.8 V only at 88 uA. With J_AB1 unplugged, B alone: 20.8 uA
  into 10 k, 0.21 V. Cost: C7's U9 sources 0.33 mA while EMCON is released.
- (c) 4.7 k: 0.15 V, and 0.70 mA from U9.
Taken: (b). EMCON_HW has no pull-up anywhere: C7 drives it with a push-pull buffer since 9 September 2026 (U9,
74LVC1G34), so nothing needs the pull-down to be weak. The 9 September red-team rule that set 100 k was written for
TX_INHIBIT_n, which C holds up with a 10 k resistor, so R59 stays 100 k. U9's own datasheet is not held; the load is
0.33 mA against an LVC output that the sibling SN74LVC08A table specifies at 100 uA (VCC - 0.2 V) and 12 mA (2.4 V at
3 V). Board A's R102 is A's (r4-interfaces.md I-04 asks for 10 k there, for A alone with J_AB1 unplugged). Taken by
the session under the owner's standing rule of 26 Sep 2026.

**SD-B-22, round 6 (R4T-F9, ruled in scope by the round-5 tools re-review): what holds an EMCON-gated enable when its
gate loses its own supply.**
The evidence, from the netlist and the held sheets:
- LIME_EN, RB_EN and E22_EN each carried two pads and nothing else: U19's output (pins 6, 8, 11) and the switch's
  EN pin (U23.3 and U24.3, TPS259631; U21.5, TPS22810). E72_EN was the same with U20.3 and U22.5.
- U19 and U20 run on +3V3_DEV. U21, U23 and U24 take their input from +5V_DEV (pins 6, 4, 4), which stays up when
  +3V3_DEV is lost (U25, the AP63203, or L1 failed) or when a gate's own pin 14 opens. U22's input is +3V3_DEV itself,
  so it goes dark with the rail, but not with an open U20 pin 14.
- Both makers forbid a floating enable. TPS2596 SLVSET8A (sha 66f6bae4...) pin table: EN/UVLO "Do not leave floating".
  TPS22810 SLVSDH0C (sha 10450eed...) 9.3.3: "EN/UVLO terminal must not be left floating".
- The unpowered gate: SCAS283W (SN74LVC08A, sha 9cefbf42...) has no Ioff row and no partial-power-down feature. Its
  7.3.3 says the outputs carry clamp diodes to VCC and to GND (VO absolute maximum VCC + 0.5 V), and the inputs only a
  negative clamp. So with VCC at 0 V the output can only sink, into the dead rail, and with VCC open nothing in the
  part can source it. What is left is leakage the sheet does not bound. The sizing takes the Ioff that a same-family
  part with the feature guarantees, SN74LVC1G08 SCES217AA (sha 30b963cc..., `drafts/datasheets/ti-sn74lvc1g08-sces217aa.pdf`, the r4t worktree's copy):
  +-10 uA at VCC 0 V, VI or VO 0 to 5.5 V. Add the EN pin's own leakage, 0.1 uA maximum on both sheets (SLVSET8A
  IENLKG, SLVSDH0C IEN/UVLO): 10.1 uA.
- The thresholds: TPS259631 VUVLO(F) 1.08 V minimum (FET off below it), VSD 0.53 V minimum (lowest shutdown current
  below it), VUVLO(R) 1.22 V maximum (SLVSET8A 7.5). TPS22810 VENF 1.08 V minimum, VSHUTF 0.5 V minimum, VENR 1.3 V
  maximum (SLVSDH0C 7.5).
Options:
- (a) No pull, and a documented "the LVC08A output defaults low when unpowered". Refused: SCAS283W documents no such
  default, and both switch sheets forbid the floating pin.
- (b) 100 k to GND. 10.1 uA gives 1.01 V: below 1.08 V, but inside VSD's band and only 70 mV from OFF.
- (c) 10 k to GND. 10.1 uA gives 0.10 V: in full shutdown on both parts until 50 uA (five times the family Ioff) and
  OFF until 108 uA. The gate drives 3.3 V / 10 k = 0.33 mA per output when high, against SCAS283W 5.7's VOH of 2.4 V
  minimum at 12 mA (VCC 3 V, -40 to +85 C), far above 1.22 V and 1.3 V. 10 k is already on B's BOM (R58, R513).
- (d) 4.7 k (S-08's value). 0.05 V at 10.1 uA and 0.70 mA per output. It buys nothing (c) lacks: S-08 chose 4.7 k
  against the PCA9555's 100 uA pull-up; the leakage here is a tenth of that.
- (e) Move U19 and U20 onto +5V_DEV-derived supply. Refused: the SN74LVC08A's VCC is 3.6 V maximum, and the rail
  question is O-14's.
Taken: (c), R514 (LIME_EN), R515 (RB_EN), R516 (E22_EN) and R517 (E72_EN), all 10 k 0603 by lcsc_fill's `^10k$` key.
E72_EN is included although its switch goes dark with +3V3_DEV: an open U20 pin 14 leaves it floating with U22
powered, the same class of failure, for one resistor. check_pcb_b.py now asserts, on pads, that each of the four nets
carries the gate's output pad, the switch's EN pad and exactly one resistor, to GND, between 200 Ohm and 49.5 kOhm
(the bounds computed in the gate from the constants above, with their sources), with only a test point allowed
beside them. Taken by the session under the owner's standing rule of 26 Sep 2026.
Not covered by (c), recorded as O-24: a +3V3_DEV that sags into 0 to 1.65 V without collapsing (a regulator in
current limit) is outside SCAS283W's operating range, where the output state is not specified and no pull-down bounds
it; and the RB, LIME and LoRa module logic is not asked here, only their supply switches.

## 3. Part changes and their evidence (owner condition 1)

| Part | MPN, package, code | Evidence held | Temperature |
|---|---|---|---|
| J_M2C2 | TE 2199119-3, 67 pos key B, 3.2 mm, C590866 | TE drawing C-2199119 rev F (drafts/datasheets, sha ef35dbf8...): sheet 2 key B row, sheet 3 land; pad-by-pad check `drafts/land/m2b_land_check.txt`: 67 of 67 electrical pads and both retention pads match; the two locating holes are absent | -40 to +80 C (JLCPCB) |
| C520, C521 | KEMET T520B227M006ATE025, EIA 3528-21, C212684 | KEMET part sheet (drafts/datasheets, sha b00319d0...) | -55 to +105 C |
| D520 | MDD SMBJ5.0A, DO-214AA, C113974 (already certified) | MDD SMBJ datasheet (sha 95385273...): VRWM 5.0 V | -65 to +150 C |
| R{s}65 | Milliohm LR2512D-3W-5mR-1%, 2512, C500739 (certified for A) | datasheet (sha 3abd0675...) | -55 to +170 C |
| C522 to C530, C283/C284, C287/C288/C290/C291 | YAGEO CC0402 NP0/X7R, 0402 | YAGEO datasheets (sha 495287fc..., 61a60682...) | -55 to +125 C |
| R272, R508/R509/R511/R512 | UNI-ROYAL 0603WAF0000T5E, C21189 (certified for E) | datasheet (sha d20b4e5f...) | -55 to +155 C |
| R{s}75, 76, 79, 80, 83, 84 (18 parts) | UNI-ROYAL 0603WAF332JT5E, 33.2 Ohm 1% 1/10 W, 0603, C23004 (fix-up, B-1) | UNI-ROYAL thick film series datasheet (drafts/datasheets, sha 11cd644d...), part number decoded per its 2.2 to 2.4.3 | -55 to +155 C |
| R{s}77, 78, 81, 82, 85, 86 (18 parts) | UNI-ROYAL 0603WAF499JT5E, 49.9 Ohm 1% 1/10 W, 0603, C23185 (fix-up, B-1) | the same datasheet | -55 to +155 C |
| R287, R288, R289 | UNI-ROYAL 0603WAF0000T5E, 0 Ohm, 0603, C21189 (certified for E; fix-up, SIM 2 Figure 19) | datasheet (sha d20b4e5f...) | -55 to +155 C |
| J_IOCOFF_A/B/C | 2.54 mm 1x02 header on the SMD land (fix-up, SD-B-16); a bench part, no order code, as in round 4 | KiCad 9 library land, judged by pin_map_lands | not an assembled part |
| U{s}11 | TI SN74LVC32APWR, TSSOP-14, C352974 (certified for B) | v2/vendor/ti/ti-sn74lvc32a-quad-or.pdf (SCAS286U), pinout = the file's GATE table | -55 to +125 C column |
| Q{s}09/10/11, Q11 | CJ 2N7002, SOT-23, C8545 (certified) | A01's ds/cj_2n7002_C8545.pdf | as certified |
| R202 | UNI-ROYAL 0603WAF3322T5E, 33.2 kOhm 1%, 0603, C23003 (pass 2, SD-B-18; was 31.6 k by lcsc_fill) | the UNI-ROYAL series datasheet already held (sha 11cd644d...); JLCPCB readback `jlc/q_0603WAF3322T5E.json` | -55 to +155 C |
| R205 | UNI-ROYAL 0603WAF1203T5E, 120 kOhm 1%, 0603, C25808, basic (pass 2, SD-B-18; was 22 k) | the same datasheet; `jlc/q_0603WAF1203T5E.json` | -55 to +155 C |
| C298 | YAGEO CC0402JRNPO9BN680, 68 pF C0G 50 V, 0402, C107009 (pass 2, SD-B-18; the code C524/C527 already use) | YAGEO CC NP0 datasheet (sha 495287fc...) | -55 to +125 C |
| R240 | removed (pass 2, SD-B-17) | RM520N HD v1.1 Table 12, Figure 12, Table 50; CJ 2N7002 datasheet (drafts/datasheets, sha 7941fb42...) | none |
| Q106, Q206, Q306 | CJ 2N7002, SOT-23, C8545 (certified), unchanged part; fix-up pass 3 (SD-B-20) rewires them as open drains (gate EMCON_ON, source GND, drain W_DISABLE1#) and changes their value text | CJ 2N7002 datasheet (drafts/datasheets, sha 7941fb42...): VSD, IGSS, Vth 1.0 to 2.5 V at 250 uA; the 3.3 V gate drive from R513 against 0.35 mA of pull-up current is the same as Q{s}11's and Q11's | as certified |
| R58 | 10 kOhm 0603, value only (fix-up pass 3, SD-B-21; was 100 k), resolved by lcsc_fill's existing `^10k$` key like every other 10 k on this board | resistor, no rating question at 3.3 V (0.36 mA, 1.1 mW) | as the board's 0603 family |
| R514, R515, R516, R517 | 10 kOhm 0603, value only (round 6, SD-B-22, new), resolved by lcsc_fill's existing `^10k$` key like R58 and every other 10 k on this board | resistor, no rating question at 3.3 V (0.33 mA, 1.1 mW when the gate drives high) | as the board's 0603 family |
| U41/U51/U61 | ST STM32H743VIT6, LQFP-100, C114409 | DS12110 Rev 10 and DS12117 Rev 9 (v2/vendor/st); `drafts/pin_parity.py` on page 55 of each: 100 of 100 pins, 0 mismatches on both; a planted PB6/PB7 swap is caught (`drafts/parity/`) | suffix 6: -40 to +85 C |

Datasheet sources with URL and sha256: `drafts/datasheets/SOURCES.txt`. Text extractions of the vendor documents read here, with their sha256: `drafts/txt/SHA256-sources.txt`.

## 4. S-16 and W7-R2-01, recorded

**S-16.** Slot 1's CM5 feeds the WIFI 2.4 jack. ASSEMBLY.md:102 reads "one Compute Module's antenna-kit lead (slot 1)", going to A's `J_RF3` (RF_WIFI24).
- The module selects its U.FL with `dtparam=ant2` (CM5 datasheet 2.1).
- Slots 2 and 3 keep WiFi and Bluetooth dark: their OFF requests stay high, which is now the hardware default.
- Their on-module PCB antennas would sit inside a closed Peli case with an aluminium face and beside two 2.4 GHz E72 radios. That breaks the datasheet's own antenna guidance (4.1.2: 10 mm clearance, no metal, a plastic enclosure).
- If slot 1 is lost, moving local WiFi to slot 2 or 3 is a firmware choice. It would run on the internal antenna, degraded, and is not a design mode.

Certification position: the module is certified with its PCB antenna or with Raspberry Pi's own antenna kit, and "If you use a third-party antenna, you must obtain your own separate certification". The kit's lead runs through board A's blind-mate site, E6's clamp and a wall coupler, so it is not the certified configuration. D-04 already rules no CE/RED claim for the prototype, so this is recorded, not claimed.

**W7-R2-01.** `git show f2541bea -- v2/ecad/tools/gen_sch_b.py` changes U42/U52/U62 from `PH1x5` to `PH1x5S` (PinHeader_1x05_P2.54mm_Vertical_SMD_Pin1Left). The reason is recorded in the file: 17 September 2026, a through-hole header under the controller pocket was a front-side keep-out that caused 29 hard violations.
- The generator's SMD land is the intended part; the committed B21 board is behind it.
- Nothing changed in the generator. `pin_map_lands` judges the SMD land PASS.
- The FP table carries the key `PH1x5S` twice with the same value. That is harmless and was left alone.

## 5. What the box measured (drafts/box/out, drafts/box/out-r4-first, drafts/box/out-base)

**Round 6 (run 6, 26 September 2026 10:51 to 11:33 UTC, `/root/r6/b/out6`, fetched to `drafts/box/r6-run6/`, SHA256SUMS
verified on the runner; the box's main clone read empty `git status` before and after; the directory was deleted after
the fetch).** Trees: tclean (main faf8c981 as committed), t6 (main + the two files), tint (the integration tree).

| Gate | Fix-up pass 3 (run 4, main 29f00554) | Round 6 (t6, main faf8c981) |
|---|---|---|
| SCH-001 erc_gate | PASS of 2384, 5 allowed errors | PASS of 2398; the 5 allowed errors identical item for item; +14 warnings, all from the four new symbols (endpoint_off_grid +5, lib_symbol_issues +6, unconnected_wire_endpoint +3) |
| SCH-004 safe_lines | PASS of 5 | PASS of 5, log identical |
| SCH-005 pin_map_lands | PASS of 1098 | PASS of 1102 (the four resistors) |
| CMP-001 derate | PASS of 234, 0 undeclared | PASS of 234, 0 undeclared |
| PWR-002 power_sequence | PASS of 41, 0 deadlocks | PASS of 41, 0 deadlocks; the log now names R514 to R517 "on GND" beside U19/U20 as the enables' other element, which is the pull-down seen by the tool |
| power_path | PASS, 0 short, 105 nodes | the same |
| TRN-001 port_protect | PASS of 11 | the same |
| CLK-001 clock_check | PASS of 7 | the same |
| review_nets | 27 issues | 27 issues, identical apart from the header's part count |
| INT-001 check_contracts | INCONCLUSIVE of 84, 0 FAIL (C, D, E, P sidecars older than 6104cb81) | INCONCLUSIVE of 91, 0 FAIL, 59 PASS: only board A is absent now (held, its sidecar predates the widened identity) |
| PWR-003 energy_chain | PASS of 98, 1 coordination finding (B_PANEL_5V) | the same |
| SCH-002 netlist_board | FAIL 310 of 6920 | FAIL 314 of 6924 (+4: the resistors are only in the netlist, O-02) |
| SCH-002 netlist_parts | 26 value differences | FAIL of 1860: 26 values, 3 lands, 173 only in the netlist, 27 only on the board |
| check_pcb_b.py, pcbnew on B21 | this gate 56 of 2207 | this round FAIL 60 of 2211; pass 3's gate FAIL 56 of 2207; committed gate ALL PASS 2169; the 4 new lines are the enable pull-downs, byte for byte the emulation's 4 on the committed netlist; 0 lines lost |
| check_pcb_b.py net section, emulated | 0 FAIL of 166 on pass 3 | 0 FAIL of 170 on round 6; 4 FAIL of 170 on pass 3 (the four enables); 60 FAIL of 174 on the committed netlist; pass 3's gate reads 0 of 166 on round 6 |
| mutation controls | 5 of 5 (EMCON) | EMCON 5 of 5 on round 6; enables 6 of 6 each fail exactly their own line, the allowed test point passes, the unmutated netlist 0 FAIL (`r6-run6/check_pcb_b/`) |
| paged schematic | 38 pages with the O-19 patch | tint (with the patch): 38 pages, 0 poppler errors; tclean (main, no patch, B21's sheet): 37 pages, 0 errors |
| regeneration parity | t82 vs t29 | main's generator vs the committed B files: schematic, netlist, intent PARITY_AFTER_NOISE; t6 vs tint: schematic PARITY, netlist, intent, provenance, ERC PARITY_AFTER_NOISE, BOM PARITY |
| generated pages | not asked | ROTATION-CHECKLIST.md +2 rows, 43 to 45; PCB-BRING-UP.md +18/-15 in B's tables; rules_render and decisions_render --check then read exactly as on clean main (PCB-ETA.md, OWNER-DECISIONS-OPEN.md only) |
| full suite on the integration tree | 1470 passed, 0 failed, 12 skipped (main + the two files) | 1472 passed, 0 failed, 12 skipped on tint exactly, and the suite left tint's `git status` unchanged (the 11 files of O-18). The 12 skips are the integrator's 11 on the r5int commit tree plus test_layer_judge's "not a git worktree" (tint is a linked worktree whose .git is a file); each states its own reason, none is a pass (condition 6) |

The fix-up generator (b24e88ce...) ran on 26 September 2026 at 00:15 UTC, in /root/r4/b only. The main clone's
`git status` was identical before and after (`drafts/box/out/main-status-*.txt`).

| Gate | Committed B21 netlist | Round 4, first run | Round 4 after the fix-up |
|---|---|---|---|
| SCH-001 erc_gate | PASS of 2044 (6 errors allowed) | PASS of 2327 (5 errors allowed; the UIM-RESET pin_not_driven is gone, because the 22 Ohm now sits on that net) | PASS of 2392, 5 errors allowed, the same five (3 pin_to_pin, 2 power_pin_not_driven). Warnings rose with the part count: lib_symbol_issues 1637 to 1679 and unconnected_wire_endpoint 196 to 219. These are the layout engine's sub-0.15 mm stubs, the same class as before |
| SCH-004 safe_lines | PASS of 5 | PASS of 5 | PASS of 5, the same log |
| SCH-005 pin_map_lands | PASS of 930 | PASS of 1059 | PASS of 1098 (the 39 new resistors and the SMD jumper land) |
| CMP-001 derate | PASS of 162, 0 undeclared | PASS of 232, 0 undeclared | PASS of 232, 0 undeclared (resistors carry no rating) |
| PWR-002 power_sequence | PASS of 38 | PASS of 41, 0 deadlocks | PASS of 41, the same log |
| power_path | PASS, 0 short, 29 nodes | PASS, 0 short, 71 nodes | PASS, 0 short, 104 nodes (33 new: 30 clock nets and SIMR2_x) |
| TRN-001 port_protect | PASS of 11 | PASS of 11 | PASS of 11, the same log |
| CLK-001 clock_check | PASS of 7 | PASS of 7 | PASS of 7, the same log |
| INT-001/RF-002 check_contracts | ALL PASS, 73 | ALL PASS, 73 | ALL PASS, 91: the 18 Rs are judged "in series with a real pin on both sides" |
| PWR-003 energy_chain | PASS of 98, 1 coordination finding (B_PANEL_5V, existing) | the same | the same log |
| review_nets | 27 issues | 27 issues, the same list | 27 issues, the same list |
| SCH-002 netlist_board | not re-taken | FAIL 242 of 6883 | FAIL 299 of 6922. This is expected: the B21 board has none of the 168 new parts. It is informative only; no placement was run (O-02) |
| check_pcb_b.py net section (emulated, section 1b) | 0 FAIL of 132 | 7 FAIL (the review's count) | committed gate 13 FAIL; with `drafts/check_pcb_b-r4.patch`, 0 FAIL of 159 |

The build ran `build_sch.sh` as far as its sheet PDF. It then stopped at `sch_pages.py`, because `pdftoppm` is not on
the box (W7-R2-03), and the BOM line was run by hand. The baseline is the committed netlist with W7's content hash
`3d1d1506654d20b3`, the one round 2 proved by regeneration parity. The fix-up netlist's content hash is
`c50213262c9bb117`, and sch_prov records it as written by generator `22077343dbc6bcbb`.

**Fix-up pass 2 (run 3, generator 8a980c57..., check_pcb_b.py 5d52b0e2..., `drafts/box/r5-run3/`, 08:03 to 08:17 UTC in
/root/r5/b only; the box's main clone status was the same before and after).** Columns: t82 = 82dd1e4d plus the two
files; t26 = main 26b80900 plus the two files.

| Gate | t82 | t26 |
|---|---|---|
| SCH-001 erc_gate | PASS of 2392, the same 5 allow-listed errors (ERC reads PARITY_AFTER_NOISE against t26) | PASS of 2392, the same |
| SCH-004 safe_lines | PASS of 5 | PASS of 5 |
| SCH-005 pin_map_lands | PASS of 1098 | PASS of 1098 |
| CMP-001 derate | PASS of 234, 0 undeclared (C298 and the declared S2A_COMP; run 2 without that node read 1 undeclared) | PASS of 234, 0 undeclared |
| PWR-002 power_sequence | PASS of 41, 0 deadlocks | PASS of 41 |
| power_path | PASS, 0 short, 105 nodes; +5V_S2 declares 4.20 A typ / 5.00 peak and its converters draw 3.16 / 4.68 | the same |
| TRN-001 port_protect | PASS of 11 | PASS of 11 |
| CLK-001 clock_check | PASS of 7 | PASS of 7 |
| INT-001/RF-002 check_contracts | ALL PASS 91 | INCONCLUSIVE of 84, 0 FAIL: A, C, D, E and P carry sidecars from before 6104cb81's sch_prov identity; main as committed reads INCONCLUSIVE of 48 with all six so |
| PWR-003 energy_chain | PASS of 98, the one existing B_PANEL_5V finding | the same |
| review_nets | 27 issues, the list identical to the first fix-up's | the same |
| SCH-002 netlist_board | FAIL 301 of 6920 (the B21 board has none of the 169 new parts; expected, O-02) | the same, and main's netlist_parts FAIL 25 of 1860 (22 values, 3 lands, all of them the board lagging the generator, among them R202/R205 of this pass and the pre-existing U10, U42/U52/U62) |
| check_pcb_b.py, pcbnew on B21 (run 1) | edited FAIL 46 of 2196, committed ALL PASS 2169 | not repeated (same gate file, same board) |
| check_pcb_b.py net section, emulated | edited 0 FAIL of 159 on this netlist; committed 13 FAIL | |
| build_sch.sh paged schematic | Pages: 0, 336 poppler errors (O-19) | Pages: 0; with `drafts/sch_pages-popups-r5.patch` (t26p): 38 pages, 0 poppler errors |
| test suite (box, pcbnew present) | | main + the two files: 1456 passed, 0 failed, 12 skipped; main as committed (run 2): 1456, 0, 12; per-test results identical. t26p's page tests: 10 of 10 |

**Fix-up pass 3 (run 4, generator 9b85ada8..., `drafts/box/r6-run4/`, 08:51 to 09:13 UTC in /root/r5/b only; run 5
for the final gate file and the suite, `drafts/box/r6-run5/`; the box's main clone status was the same before and
after both).** Columns: t82 = 82dd1e4d plus the two files; t29 = main 29f00554 (the runner's main today) plus the two files.

| Gate | t82 | t29 |
|---|---|---|
| SCH-001 erc_gate | PASS of 2384, the same 5 allow-listed errors as pass 2, item for item. Warnings 8 fewer (lib_symbol_issues 1679 to 1674, unconnected_wire_endpoint 219 to 216): power-symbol placement around the three rewired FETs | PASS of 2384 (ERC PARITY_AFTER_NOISE against t82) |
| SCH-004 safe_lines | PASS of 5 (it counts EMCON_HW's pull-down; it could not see the sourcing path either, O-22) | PASS of 5 |
| SCH-005 pin_map_lands | PASS of 1098 | PASS of 1098 |
| CMP-001 derate | PASS of 234, 0 undeclared | the same |
| PWR-002 power_sequence | PASS of 41, 0 deadlocks | the same |
| power_path | PASS, 0 short, 105 nodes | the same |
| TRN-001 port_protect | PASS of 11 | the same |
| CLK-001 clock_check | PASS of 7 | the same |
| INT-001/RF-002 check_contracts | ALL PASS 91 | INCONCLUSIVE of 84, 0 FAIL (A, C, D, E and P sidecars predate 6104cb81's identity); main 29f00554 as committed reads INCONCLUSIVE of 48 (`/root/r5/b/out4b`), so that is main's state |
| PWR-003 energy_chain | PASS of 98, the one existing B_PANEL_5V finding | the same |
| review_nets | 27 issues | the same |
| SCH-002 netlist_board | FAIL 310 of 6920 (pass 2: 301; the 9 moved FET pins on the unplaced B21 board, O-02) | the same, and netlist_parts FAIL of 1860 with 26 value differences (pass 2: 22; Q106/Q206/Q306's text and R58's value) and the same 3 land differences |
| check_pcb_b.py, pcbnew on B21 | this pass FAIL 56 of 2207 (run 4; run 5 with the final file: FAIL 56 of 2207, its 10 new lines byte for byte the emulation's 10 on the committed netlist); pass 2's gate FAIL 46 of 2196; committed gate ALL PASS 2169 | |
| check_pcb_b.py net section, emulated | 0 FAIL of 166 on this netlist; 56 of 170 on the committed netlist; 9 of 172 on pass 2's | 0 FAIL of 166 |
| build_sch.sh paged schematic | Pages: 0, 336 poppler errors (O-19, unpatched) | with the O-19 patch (t29p): 38 pages, 0 poppler errors; the patch's tests 10 of 10 |
| regeneration parity t82 against t29 | | schematic PARITY, netlist PARITY_AFTER_NOISE, intent PARITY_AFTER_NOISE, BOM PARITY, ERC PARITY_AFTER_NOISE; provenance DIFFERENT only in generator_file_sha, generator_files, generator_sha and identity_since (6104cb81's sch_prov identity) |
| test suite (box, pcbnew present) | | run 4 (gate 70a03fe8): 1470 passed, 0 failed, 12 skipped; run 5 (final gate 720892ae): 1470 passed, 0 failed, 12 skipped |

## 6. Every netlist difference (drafts/box/netdiff.txt, .json; W7's comparator in drafts/box/regen_compare_net.json)

**Round 6, against the committed netlist** (`drafts/box/netdiff-r6b.txt`, .json; the base is main faf8c981's committed
`out/pcb-b-compute.net`, byte-identical to 82dd1e4d's and reproduced by main's own generator at PARITY_AFTER_NOISE;
W7's comparator `r6-run6/regen_compare_committed_new.json` reads DIFFERENT, as intended): 931 to 1103 components (173
added, 1 removed, 25 changed), 1852 to 1929 nets, 141 pins of existing components on another net (139 moved plus
R240's two, which leave with it), 344 pins of the added parts. That is pass 3's list exactly (same removed, same 25
changed, same moved pins, same nets) plus the four components below.

**Round 6 alone** (`drafts/box/netdiff-r6b-round6.txt`, pass 3's netlist against round 6's; W7's comparator
`r6-run6/regen_compare_pass3_new.json` DIFFERENT):

| Difference | Finding |
|---|---|
| R514 added, 10k 0603, 1 LIME_EN, 2 GND | R4T-F9, SD-B-22 |
| R515 added, 10k 0603, 1 RB_EN, 2 GND | R4T-F9, SD-B-22 |
| R516 added, 10k 0603, 1 E22_EN, 2 GND | R4T-F9, SD-B-22 |
| R517 added, 10k 0603, 1 E72_EN, 2 GND | SD-B-22 (the same class, an open U20 pin 14) |

No component changed or was removed, no pin of an existing component moved, no net was added or removed. The t6 and
tint netlists are equal under my own differ (0 components, 0 pins, 0 nets). Pass 3's intent file against round 6's differs
in one key, `written` (a key-by-key comparison on the runner), and t6 against tint reads PARITY_AFTER_NOISE.

**Fix-up pass 3, against the committed netlist** (`drafts/box/netdiff-r6.txt`, .json; the baseline is
`/root/r4/b/out/base/pcb-b-compute.net`, which equals main 29f00554's committed netlist byte for byte; W7's comparator
`drafts/box/r6-run4/regen_compare_base_new.json` reads DIFFERENT, as intended): 931 to 1099 components (169 added, 1
removed, 25 changed), 1852 to 1929 nets, 141 pins of existing components on another net, 336 pins of the added parts.
That is pass 2's list line for line plus the nine pins and four value texts below; nothing of pass 2's list is lost.

**Fix-up pass 3 alone** (`drafts/box/netdiff-r6-pass3.txt`, pass 2's netlist against this pass's; W7's comparator
`regen_compare_pass2_new.json` DIFFERENT, its intent comparison PARITY_AFTER_NOISE):

| Difference | Finding |
|---|---|
| Q106.1 +3V3_S1A to EMCON_ON; Q106.2 WIFI_W_DIS_n to GND; Q106.3 EMCON_HW to WIFI_W_DIS_n | the re-review's blocking item, SD-B-20 |
| Q206.1 +3V3_S2A to EMCON_ON; Q206.2 5G_W_DIS_n to GND; Q206.3 EMCON_HW to 5G_W_DIS_n | the same, SD-B-20 |
| Q306.1 +3V3_S3A to EMCON_ON; Q306.2 WIFI2_W_DIS_n to GND; Q306.3 EMCON_HW to WIFI2_W_DIS_n | the same, SD-B-20 |
| Q106, Q206, Q306 value text '2N7002 EMCON -> W_DISABLE1#' to '2N7002: EMCON_ON pulls W_DISABLE1# low (open drain)' | SD-B-20 |
| R58 value '100k' to '10k' | O-08, SD-B-21 |

No component, net or intent entry was added or removed, and no other pin moved. The t82 and t29 netlists are equal
under my own differ (0 components, 0 pins, 0 nets different).

**Fix-up pass 2, against the committed netlist** (`drafts/box/netdiff-r5.txt`, .json; W7's comparator
`drafts/box/r5-run3/regen_compare_base_new.json` reads DIFFERENT, as intended): 931 to 1099 components (169 added, 1
removed, 21 changed), 1852 to 1929 nets, 132 pins of existing components on another net (the fix-up's 130 plus R240's
two, which leave with it), 336 pins of the added parts.

**Fix-up pass 2 alone** (`drafts/box/netdiff-r5-pass2.txt`, the first fix-up's netlist against this pass's):
- **O-15 / SD-B-17:** R240 removed (it was 10 k from 5G_RST_n to +3V3_S2A). Q208's value text now says open drain, no
  pull-up.
- **O-17 / SD-B-18:** R202 31.6k 1% to 33.2k 1% (C23003); R205 22k to 120k 1% (C25808); C298 added, 68p 50V C0G
  (C107009), S2A_COMP to GND. In the intent: +3V3_S2A and +3V3_M2C2 declared at 3.456 V, +5V_S2 typical 4.2 A, and the
  node S2A_COMP at +5V_S2.
- Nothing else: no net added or removed, no other part or pin changed.

**Totals against the committed netlist, after the fix-up:**
- Components: 931 to 1099 (168 added, 0 removed, 18 changed).
- Nets: 1852 to 1929.
- Pins: 130 pins of existing components are on another net. The 168 added components bring 334 pins.
- 867 components show a uuid shift, because the uuid5 sequence moves when parts are inserted, as W7 described.

The first run's header said "368 pins on another net". That number counted the 256 pins of its 129 added parts, and
only 112 moved; the review counted 112 as well. `drafts/netdiff_report.py` now writes the two numbers apart.

**The fix-up alone** (`drafts/box/netdiff-fixup.txt`, the first round-4 netlist against the fix-up netlist):
- 39 resistors added, 4 components changed, 21 pins of existing components moved, 21 nets added, 0 removed.
- **B-1 (W3-F03 termination):**
  - U{s}01 pins 85/83, 81/80 and 78/77 move to PCIE{s}_RCLK0_SRC_x, NVME{s}_CLK_SRC_x and CARD{s}_CLK_SRC_x.
    That is 18 pins.
  - Added: R175-R186, R275-R286 and R375-R386. Each Rs sits from `*_SRC_x` to the line, and each Rp from the line to
    GND (itemised with every pin in the file).
- **SIM 2, Figure 19:**
  - R269.1, R270.1 and R271.1 (the 22 Ohm on SIM 2) move from SIM2_RST/CLK/IO to SIMR2_RST/CLK/IO.
  - R287 to R289 (0 Ohm) were added from SIM2_x to SIMR2_x.
  - R272's value now says "at the module".
- **SD-B-16:** J_IOCOFF_A/B/C change land to PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left. Their nets are unchanged.

No other net, part or pin changed between the two runs. W7's comparator over the committed netlist against the fix-up
netlist (`regen_compare_net.json`) reads DIFFERENT, as intended. It lists the same added and changed sets and the
7 unconnected-pin nets that disappeared.

**Every difference against the committed netlist is intended and belongs to an item (the first run's list, then the fix-up's):**

- **W3-F01:**
  - U{s}01 pins 100/101 and 106/107 move to `*_RX_SW_*`.
  - The three M-key sockets (41/43 against 47/49), the two E-key sockets (35/37 against 41/43) and J_M2C2 (41/43 against 47/49) have their pairs swapped.
  - Twelve 220 nF capacitors were added: C153-156, C253-256, C353-356.
- **W3-F02:** U102.6/.7 move to LIME_SSRX; C161.2/C162.2 move to LIME_SSTX.
- **W3-F03:** U{s}01.110/.111 move to PCIE{s}_RCLKIN; C195, C196, C295, C296, C395 and C396 were added. Fix-up: U{s}01.85/.83/.81/.80/.78/.77 move to the `*_SRC_x` nets, and R{s}75 to R{s}86 (36 parts) were added.
- **S-12:** J_M2C2's value and code change (C574849 to C590866).
- **S-13:**
  - J_M2C2 pin 40 goes to NC. Pins 44, 46 and 48 move to CLK, RST and VDD.
  - The J_SIM1/J_SIM2 contacts move to SIMC* nets.
  - C287, C288, C290 and C291 change from 33p to 10p 50V C0G, and C289 moves to SIMC2_VCC.
  - Added: C283, C284, R266-R271 (22 Ohm) and R272 (0 Ohm). Fix-up: R287-R289 (0 Ohm at the module), with SIM 2's 22 Ohm between SIMR2_x and SIMC2_x.
- **F-PR-05 and TESTACCESS-B shunts:**
  - The card-socket power pins and C{s}57/C{s}58 move to +3V3_M2C{s}.
  - Added: R165, R265 and R365 (5 mOhm), C520-C530 and D520.
  - The rail declarations changed in the intent file.
- **S-01:**
  - U6.13-18 move to `*_nDIS*_OFF`.
  - U103.3 and U303.3 move to S1A_EN/S3A_EN.
  - Added: U111, U211, U311, Q109/Q110, Q209/Q210, Q309/Q310, Q111, Q311, Q11, R162/R163, R262/R263, R362/R363, R164, R364, R173/R174, R273/R274, R373/R374, R513, C197, C297 and C397.
- **S-08:** R48, R50-R53 and R60-R62 change from 100k to 4.7k.
- **W5-F3:** U41, U51 and U61: 35/36 go to NC, and 92/93 take SCL/SDA.
- **D-13:** U41, U51 and U61 change symbol (STM32H753VI to STM32H743VI) and value.
- **TESTACCESS-B:**
  - U40.3, U50.3 and U60.3 move to IOCx_LDO_EN.
  - Added: R66, R78 and R90 (100 k), and J_IOCOFF_A/B/C (on the SMD 1x02 land since the fix-up).
  - U43.6/.7, U44.6/.7, R470.1, R471.2, R472.1 and R473.2 move to the `*1` CAN segment.
  - Added: R508, R509, R511 and R512 (0 Ohm), and TP101-103, TP201-203, TP301-303 and TP501-538.
- **D-12:** J_AB2's value text only.
- **S-01/S-16:** U6's value text.

## 7. Open items, each with its reason

| Id | Item | Why not done here | Owner |
|---|---|---|---|
| O-01 | The M2B land (`gen_footprints_b16.py`, `M2_B-Key_Socket_3052`) has no locating holes. TE sheet 3 asks for NPTH dia 1.1 +-0.05 at (-10.0, 0) (datum Y) and dia 1.6 +-0.05 at (+10.0, 0) (datum X), in the footprint's own coordinates, where the hole line is Y 0 (odd row Y -5.275, even row Y +2.275). Until they are drawn, J_M2C2 stays a mismatch under condition 1. Check the E-key and M-key lands against their drawings the same way | footprint generator, not my file | footprint owner |
| O-02 | Every new part needs a seat in `gen_pcb_b3.py` (REGIONS lists refs explicitly, and the placement refuses unplaced parts). The list is in section 8 | placement generator, not my file; no placement run authorised | placement owner |
| O-03 | CLOSED in the fix-up (B-1, SD-B-15). The first draft said the held datasheet did not decide whether REFCLKO needs external termination. It does: IREF "set[s] the differential reference clock output current" and Table 8-1 note 1 gives Rs 33.2 Ohm and Rp 49.9 Ohm. All nine used pairs are now terminated at the source | done | none |
| O-04 | SIM TVS array: HD 4.1.7 asks for "a TVS array of which the parasitic capacitance should be not higher than 10 pF" at each holder. No part is picked | needs a part and its datasheet; not in my item list beyond S-13's pins | board B author, next round |
| O-05 | Every value-only part added is covered by an existing `lcsc_fill.py` key (`^22R$` C23345, `^4\.7k$` C23162, `^10k$`, `^100k$`, `^100n` 0402 C60474, `^220n` 0402 C696846). `JLC-CERTIFIED.tsv` has no row for C696846 (the six upstream PCIe capacitors since 16 September, and now twelve more). It also has no row for any code named directly in round 4: C590866, C212684, C93654, C107001, C107009, C106997, C526972, C325453 and C106199, nor for the fix-up's C23004 (33.2 Ohm) and C23185 (49.9 Ohm), nor for pass 2's C23003 (33.2 kOhm) and C25808 (120 kOhm). The certified rows for C114409 (482 to 484) still carry the old value text "STM32H753VITx", so a rerun is owed. Evidence gaps named by the review: the -40 to +80 C rating of TE 2199119-3 comes from the JLCPCB listing, because TE product specification 108-115042 is not held and the socket sits under the 5G module; and C696846 (the 220 nF 0402 X7R on 18 PCIe capacitors) has no datasheet held | certification is a `jlc_certify.py` run, not my file; the TE spec and the CCTC sheet are fetches for the certification owner | W6/W7 |
| O-06 | Firmware contract (W5): (1) U6 bits 13 to 18 are OFF requests now; writing them LOW enables a module radio, and slot 1 is the WIFI 2.4 module. (2) After EMCON is released the host must rescan PCIe for the WiFi card on slots 1 and 3. (3) While a card's supply is off, PERST# from the switch and PEWAKE# (10 k to +3V3_S{s}B) can feed its I/O; the host should hold the port in reset (switch DWNRST) before EMCON, or the residual is accepted. This path existed before EMCON gating whenever PCIE_PWR_EN was low. (4) Round 6, from the pass-3 re-review's minor 3: PC5 (pin 33) of U41, U51 and U61 reads EMCON_HW and must stay an input with no pull and never an output. DS12110 Table 60 gives RPU 30 to 50 k; one enabled pull-up at 30 k against R58's 9.09 k gives 0.77 V, and about 0.98 V with the 30.8 uA of leakage, above VIL 0.8 V. The reset state is analog with no pull, so only firmware can break it | firmware and a bench test | W5 |
| O-07 | RF-002 needs its instrument to count the three CM5 radios and the two card supplies as gated (S-02) | tool, not my file | S-02 owner |
| O-08 | CLOSED on B in fix-up pass 3 (SD-B-21); board A's half is asked in r4-interfaces.md I-04. The item counted input leakage only and missed the sourcing path the round-5 re-review found: the three W_DISABLE1# stages' body diodes, about 50 uA per live card rail against the 50 k (up to 0.35 mA into a line at 0 V; SD-B-20 removes them). What is left on the line at the datasheet maxima (-40 to +85 C): six SN74LVC08A inputs at +-5 uA (SCAS283W 5.7; B's U19 x3 and U20 x1, A's U26 x2), three STM32H743 TT_a inputs at +-250 nA (DS12110 Rev 10 Table 60) and Q11's gate at 80 nA (CJ's 25 C IGSS at VGS 20 V, the pass-3 re-review's nuance; the sum is dominated by the 30 uA of LVC08A leakage either way), 30.8 uA. With 100 k on each board (50 k) that is 1.54 V, above VIL 0.8 V (SCAS283W 5.4); with R58 at 10 k (9.09 k) it is 0.28 V, and 0.8 V needs 88 uA. B alone, J_AB1 unplugged: 20.8 uA into 10 k, 0.21 V. A alone, J_AB1 unplugged: 10.0 uA into R102's 100 k, 1.0 V, which is A's to fix (10 k asked). The pass-3 re-review's minor 3 adds DS12110 Table 60 note 4, a 10 uA product-level term per device: even at 3 x 10 uA more the line sits at about 0.55 V at 9.09 k, so SD-B-21 holds; the PC5 firmware line it also asks for is in O-06 | B done; A's R102 is not my file | board A author |
| O-09 | Documents naming the H753, PB1/PB2 or the old U6 semantics: ARCH-PCB-B-IOHA.md:94,157 and section 6 (I2C slave pins), V2-SPEC.md:82, PANEL.md (U6 bits), ASSEMBLY.md:99 (MAIN/DIV names for the RM520N) | not my files | integrator |
| O-10 | CLOSED in fix-up pass 2. `check_pcb_b.py` is now changed in the worktree itself (this pass made the board B author its writer): the pad-level direction checks of `drafts/check_pcb_b-r4.patch`, byte for byte (sha256 5d52b0e2...). On the committed B21 board with pcbnew: the committed gate ALL PASS of 2169, the edited gate FAIL 46 of 2196, the same 46 lines as the first fix-up (`drafts/box/r5-run1/t82/v/new_fails_on_B21.txt`). On this pass's netlist, emulated: 0 FAIL of 159 (section 1c) | done | none |
| O-11 | The RM520N asks for 85 Ohm differential on PCIe (HD Table 18), and the board routes its PCIe at 90 Ohm (W6-F11) | layout class, not a generator item | layout |
| O-12 | `erc-allow.txt`'s `pin_not_driven|UIM-RESET` line no longer matches anything | not my file; harmless | board B allow-list owner |
| O-13 | W5's other board B rows (rail pads on +5V_S1..3, +3V3_CM, +3V3_IOCx and the rest, SWO on the SWD land) were not in my list | out of scope for round 4 | W5 |
| O-14 | S-01 fails open if +3V3_DEV is lost while a slot is up (SD-B-14). Since fix-up pass 3 (SD-B-20) the three card W_DISABLE1# open drains hang on EMCON_ON as well, so a lost +3V3_DEV also releases W_DISABLE1# on a card whose rail is up (slot 2's 5G above all, since its rail is not EMCON-gated); the remedy below must cover the three Q{s}06 gates too, for example a second EMCON_ON pull-up that does not share +3V3_DEV's regulator. Remedy to review: a diode per KILL line so U{s}11 can only pull it low, and 10 k from KILL to +3V3_CM{s}. The diode is to be chosen for leakage at 85 C and for forward drop against the 2N7002's 1.0 V minimum threshold. For the kill lines this is not a regression (U6's direct drive failed the same way). **For W_DISABLE1# it is a narrow regression of SD-B-20** (the pass-3 re-review's minor 1, corrected here): with +3V3_DEV lost and +5V_DEV up (U25 or L1 failed), the panel is still powered through F1, shows EMCON asserted, and EMCON_HW is correctly low, yet EMCON_ON floats low, so Q206 releases the 5G W_DISABLE1# that B21's stage held low in exactly this state. The reviewer's candidate remedy, recorded for this item: a per-slot inverter (2N7002, gate on EMCON_HW, drain to +5V_S{s} through 10 k, never +3V3_S{s}A, which Q{s}11 collapses) driving Q{s}06, Q{s}11 and a second open drain beside each Q{s}09/Q{s}10, so every kill depends only on the slot's own feed; check_pcb_b.py property 3 would then need narrowing to non-insulated pads (a MOSFET gate cannot source the line). Round 6's R514 to R517 (SD-B-22) take the three +5V_DEV switches out of this item: with +3V3_DEV lost they are now held OFF | a new circuit with a part choice; the review's one-line remedy back-feeds the module | board B author, next round |
| O-15 | CLOSED in fix-up pass 2 (SD-B-17): R240 is removed. HD v1.1 Table 12 and Figure 12 (RESET# a 1.8 V DI with an internal 1.5 uA pull-up, an open collector the only host part) and Table 50 ("Voltage at Digital Pins" 2.3 V absolute maximum) decide it; Q208's IDSS is at most 80 nA (CJ 2N7002 datasheet; the datasheet gives it only at 25 C and VDS 60 V, the re-review's note, so it is a 25 C figure; here VDS is at most 1.8 V). Pins 6 and 8 were checked on the same pages and are fine | done | none |
| O-16 | CLOSED in fix-up pass 2 by the datasheet, no change: DS12110 Rev 10 Table 21 gives TT_xx pins an ABSOLUTE maximum input of 4.0 V (not VDD-relative; FT_xxx: Min(VDD, ...) + 4.0 V, also 4.0 V unpowered), and Table 22 note 3 reads "Positive injection is not possible on these I/Os and does not occur for input voltages lower than the specified maximum value". So 3.3 V on PA6 (FT_a), PA7, PC4 and PC5 (TT_a) of a controller whose VDD is 0 neither exceeds a rating nor back-feeds it. The review's VDD + 0.3 V is Table 24's operating condition of a powered part. PA4 and PA5 (HUBRST2/3, IINJ 0/0) are the controller's outputs and carry only 100 k to GND. The generator's comment now says so. The IOHA A4/A6 procedure can still note that a dark controller's pins sit at the bus levels. The re-review's caveat, recorded: Table 60 specifies the TT_xx leakage only for 0 < VIN <= VDD, so a dark part's leakage is unspecified; the conclusion does not change | done | none |
| O-17 | CLOSED in fix-up pass 2 (SD-B-18): slot 2's card buck is set to 3.456 V (R202 33.2 k, worst case 3.369 to 3.545 V) and compensated for its 0.5 mF (R205 120 k, C217 3.3 nF kept, new C298 68 pF), per DS41979 Eq. 6 and 17 to 19; worst-case budget at a 4 A step 3.213 V against 3.135 V. Slots 1 and 3 keep the recipe: their sockets carry the AW7915-AED on 3 x 22 uF plus 22 uF, which is Table 1's own capacitance | done | none |
| O-18 | Integration, REBUILT IN ROUND 6 ON MAIN faf8c981 (supersedes the pass 2 and pass 3 lists; the pass-3 re-review's blocking item). One commit carries, all taken from `drafts/box/r6-run6/tint/set/` (sha256 list `drafts/box/r6-run6/tint/set.sha256`): (1) `v2/ecad/tools/gen_sch_b.py` (6e3d8809...) and `v2/ecad/tools/check_pcb_b.py` (28904a37...), equal to this worktree's; (2) the regenerated `v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_sch`, `out/pcb-b-compute.net`, `out/pcb-b-compute-intent.json` and `out/pcb-b-compute.net.prov.json`, written on faf8c981's sch_prov (identity since 2026-09-26, 59 lands); (3) `drafts/sch_pages-popups-r5.patch` (O-19) applied: `v2/ecad/tools/build_sch.sh`, `sch_pages.py`, `tests/test_schematic_pages.py`; (4) `v2/release/revA/order/ROTATION-CHECKLIST.md` re-rendered by `assembly_set.py --checklist`: exactly two rows added, `CP_EIA-3528-21_Kemet-B` (B, C520) after the Keystone 3034 row and `PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left` (B, J_IOCOFF_A) after the J_RPIBOOT1 row, and the count line 43 to 45 (section 1e); (5) `v2/docs/PCB-BRING-UP.md` re-rendered by `rules_render.py --no-refresh` (18 insertions, 15 deletions, all in board B's tables), with PCB-ETA.md left at HEAD because clean main refuses it too. Nothing else: PCB-ETA.md and OWNER-DECISIONS-OPEN.md refuse --check on clean faf8c981 as well. The commit body names the O-19 patch and both re-rendered pages. After it, SCH-002 (netlist_board FAIL 314 of 6924, netlist_parts FAIL of 1860 with 173 only in the netlist) and the B21 board gate (FAIL 60 of 2211) fail until a placement seats the new parts (O-02); check_contracts reads INCONCLUSIVE of 91 with 0 FAIL because board A's committed sidecar predates the widened identity (A is held), which is main's state. For the suite owner: `test_assembly_set.t_the_checklist_flag_answers_a_missing_path_instead_of_raising` writes the tree's own checklist and should pass a temporary path | integration, not my file set | integrator; the test fix is the suite owner's |
| O-19 | New in fix-up pass 2, found in the round-5 re-review's box log: board B's paged schematic PDF comes out EMPTY (0 pages, "malformed page tree") while build_sch.sh exits 0. KiCad's property popups put 10480 JavaScript link annotations on the sheet's one page (the committed B21 sheet already carries 9561), `mutool poster` copies all of them onto each of the 42 tiles, poppler refuses any page over 10000 ("Page annotations object (page 1) is likely malformed. Too big"), pdftoppm writes blank PNGs and exits 0, and sch_pages.py keeps no tile. `drafts/sch_pages-popups-r5.patch` (SD-B-19) adds `--exclude-pdf-property-popups` to build_sch.sh, makes sch_pages.py refuse a sheet of many cells with no ink, and adds two tests with a defective and an acceptable fixture. Proven in section 1c. It must land before board B's next deliverable and should land in the same commit. Cosmetic, from the re-review: the patched build_sch.sh's failure branch still blames mutool ('apt-get install mupdf-tools') when sch_pages.py now refuses a no-ink sheet; sch_pages.py's own message is right. Left as is, so the proven patch is unchanged | build_sch.sh, sch_pages.py and their test are not my files | integrator (tool owner) |
| O-20 | New in fix-up pass 3 (re-review minor 1), boards A and B: the AP64500's RT is 68 k on every buck33 on B (R{s}04 for S{s}A and R{s}09 for S{s}B, six parts, value text '68k (RT: 500 kHz)') and on board A's per-slot AP64500s (gen_sch_a.py, the same 68 k). DS41979 Rev 5-2 Eq. 7 is RT[kOhm] = 100000 / fsw[kHz], and the electrical table gives fSW 450 to 550 kHz at RT = 200 kOhm, so 68 k sets about 1.47 MHz. Checked here: O-17's values hold at either frequency (fc 12 to 18 kHz against fsw/10 of 147 or 50 kHz; Eq. 19's second term 1.8 or 5.3 pF against the 52 to 84 pF ESR term). Not settled: (1) the 0.88 efficiency behind +5V_S2's 4.2 A and I-03's 5.63 A is a 500 kHz reading; (2) Eq. 8 with the fitted 3.3 uH at VIN 5.1 V and VOUT 3.456 V gives a ripple of 0.68 A at 500 kHz and 0.23 A at 1.47 MHz, both below DS41979's 30 to 50 percent of 5 A, so the inductor choice is part of the same question; (3) A's slot bucks run from 14.4 V, where switching loss grows with fsw. Recommendation: RT = 200 k 1% on A and B in one change, since the recipe's L and Table 1 row are the 500 kHz ones, with the label corrected; or keep 1.47 MHz with a loss and thermal check. The generator's buck33 docstring and the O-17 comment now say what the RT sets; the part value text is left for that change | a cross-board recipe change (A's generator is not mine) with a part choice and a loss check | boards A and B, next round |
| O-21 | New in fix-up pass 3, found while fixing SD-B-20 and not judged here: the same bidirectional stage (gate on +3V3_CM{s}, source on the module side with 10 k up to +3V3_CM{s}, drain on the shared line) sits on PI_KILL (Q{s}03), PI_SHDN_REQ (Q{s}02), GNSS_PPS (Q{s}04) and HB1 to HB3 (Q{s}05). Its body diode lifts the shared line whenever a module is powered, its pin is not driven low and nothing else drives the line. PI_KILL is a declared safety line (tools/boards/b.json, safe state low): on A23 it is the gate of Q1 ('panel controller high = pull KILL low = power off') with R5 100 k to GND. So with the panel absent, or its RP2040 not driving pin 30, a powered module whose GPIO17 is not driven low would lift PI_KILL to roughly 2.5 V, above Q1's 1.0 V minimum threshold, and while the panel does drive PI_KILL low no module can raise it at all. Which of those is the intended kill path is a contract question for A, B and C. The pass-3 re-review confirmed the list (Q{s}02 PI_SHDN_REQ, Q{s}03 PI_KILL, Q{s}04 GNSS_PPS, Q{s}05 HB1 to HB3, no others) and added two points for the same question: with the panel present, a module that pulls GPIO17 low contends through Q{s}03 with board C's RP2040 if its pin 30 drives PI_KILL high push-pull; and the GNSS_PPS stages can lift the line into an unpowered LG290P's PPS pin | a cross-board contract, outside the re-review's items | boards A, B and C, next round |
| O-22 | New in fix-up pass 3, for the integrator: tools/boards/b.json's EMCON_HW row says 'the three W_DISABLE stages hang on it and R58 holds it down'; after SD-B-20 the stages hang on EMCON_ON and EMCON_HW carries only readers. safe_lines judges a pull-down's presence and cannot see a sourcing path (it passed B21 and pass 2 with the back-feed), so the check sits in check_pcb_b.py at board phase; a schematic-phase instrument (safe_lines asking that no transistor channel sit on a listened safe-low line) is owed to the safe_lines owner | not my files | integrator, safe_lines owner |
| O-23 | New in round 6, from the pass-3 re-review's minor 4: EMCON_ON's asserting edge is an RC edge, R513 10 k into about 0.3 nF (five 2N7002 gates at up to 50 pF each, six SN74LVC32A inputs, Q11's Coss), tau about 3 us (about 1.7 us before SD-B-20). It feeds U{s}11, whose input transition limit is 7 ns/V (SN74LVC32A SCAS286U, sha 807f6fff..., recommended operating conditions, all three temperature columns), so KILL can chatter for about a microsecond before it settles at kill. Functionally benign (it settles in the safe direction); the remedy is a Schmitt buffer (74LVC1G17, the part board C now uses for U9) between Q11 and the U{s}11 inputs. Dates from S-01 in pass 1 | a part choice; the same question as O-14's EMCON_ON source | board B author, with O-14 |
| O-24 | New in round 6 (SD-B-22's residual): (1) SCAS283W publishes no Ioff for the SN74LVC08A, so R514 to R517 are sized against the SN74LVC1G08's guaranteed 10 uA (SCES217AA), with a factor of five to full shutdown and ten to OFF; the tools owner's fail_safe() (R4T-D24, blocking 1 of the round-5 tools re-review) should carry the same figure and say it is a family figure, not this part's. (2) A +3V3_DEV held between 0 V and 1.65 V (a regulator in current limit or hiccup) is outside SCAS283W's operating range; the gates' output state there is unspecified and no pull-down bounds it. A rail-good qualification of the EMCON gates belongs with O-14's remedy | a tool figure and a rail-supervision question | tools owner (1); board B author with O-14 (2) |

## 8. Placement seats owed in gen_pcb_b3.py (O-02)

Per slot s (the same k in every slot, so `Cs(s, a, b)` style lists work):

| Group | Parts | Suggested region |
|---|---|---|
| PCIe downstream coupling | C{s}53, C{s}54 (NVMe), C{s}55, C{s}56 (card): 220 nF pairs, each pair a COUPLE (their nets are _P/_N partners) | S{s}_SWIC beside U{s}01, like C{s}51/52 |
| REFCLK coupling | C{s}95, C{s}96 | S{s}_SWIC, between pins 85/83 and 110/111 |
| REFCLKO termination (fix-up, B-1) | R{s}75 to R{s}86: the Rs pairs R{s}75/76, R{s}79/80, R{s}83/84 within a few mm of pins 85/83, 81/80 and 78/77, each Rp pair R{s}77/78, R{s}81/82, R{s}85/86 right after its Rs on the line side; each P/N pair a COUPLE | S{s}_SWIC, at the switch, before the long runs to the sockets |
| Module radio gate | U{s}11, C{s}97, Q{s}09, Q{s}10, R{s}62, R{s}63, R{s}73, R{s}74 | S{s}_SUP (the module's support pocket) |
| Card supply gate (slots 1, 3) | Q{s}11, R{s}64 | S{s}_RAIL beside U{s}03's EN |
| Card socket shunt and pads | R{s}65 (2512), TP{s}02, TP{s}03 (Kelvin at its pads), TP{s}01 (GND) | between the buck's output and the socket |
| Slot 2 only | C520-C530, D520 beside J_M2C2's pins 2/4 (C520, C522-C524) and 70/72/74 (C521, C525-C530); R272 and R287 to R289 (the SIM 2 0 Ohm links) AT J_M2C2's pins 48, 46, 44 and 42 (HD Figure 19, "near the module"); R266 to R271 (the 22 Ohm) and C283, C284, C286 to C291 AT J_SIM1/J_SIM2 (Figure 18, near the holder) | S2_SWEB / S2_SWE |
| Slot 2 card buck (pass 2, SD-B-18) | C298 (68 pF, COMP to GND) beside U203's COMP pin next to R205/C217; R202 and R205 keep their seats. R240 is gone from J_M2C2 pin 67 (SD-B-17) | S2_RAIL, at U203 |

Fix-up pass 3 adds no part, but it moves three: Q106, Q206 and Q306 keep their seats beside their sockets' W_DISABLE1# pins, and their gates now join EMCON_ON (Q11's drain at GAP12) instead of EMCON_HW; their sources go to GND. EMCON_ON is a slow logic line (R513 10 k) and needs no class of its own.

Round 6 (SD-B-22) adds four resistors: R514 on LIME_EN, R515 on RB_EN and R516 on E22_EN beside U19 (pins 6, 8 and 11), and R517 on E72_EN beside U20 (pin 3), each a 0603 from the gate's output to GND, in GAP12 with U19/U20; nothing about the line is fast, so the seat can be at either end of the net, the gate's end being the natural one.

Control plane: J_IOCOFF_A/B/C and R66/R78/R90 in IOCA/IOCB/IOCC; R508/R509/R511/R512 at the IOCA edge of the CAN run; TP501 to TP503 one per controller pocket; TP504 to TP538 on the voter band; Q11 and R513 beside U19/U20 (GAP12).
