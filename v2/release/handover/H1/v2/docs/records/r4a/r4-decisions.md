# Board A, round 4: decisions and changes (MESHSAT-1357, Review D)

Author: round-4 board A author, 26 September 2026. Worktree `wt/r4a`, branch `fnd/r4a` at main `82dd1e4d`.
Only `v2/ecad/tools/gen_sch_a.py` and `drafts/*` were written. Nothing was committed or pushed.

Every choice below that had more than one option is **taken by the session under the owner's standing rule of
26 Sep 2026** ("the owner is not asked anything; where a choice remains, take the option the evidence
recommends"). Each entry names the options, the one taken and why. Evidence levels: VERIFIED (read in a held
primary document or measured on the regenerated netlist), INFERRED (arithmetic on held figures), TBD.

**Round 4 FOURTH fix-up (the third re-review, 26 September 2026): section 7 below.** It resolves the third
re-review's one blocking item (the front end restarting into its own charged VBUS20 was not assessed): assessed on paper
it is not bounded as drawn (VIN_RAW to U2's 60 V absolute maximum and L1 at three times its saturation current at every
crank), and it is fixed by a restart guard that owns U2's enable (R4A-N15). It takes the minor items (the bulk's layout
conditions, the panel-only charge reduction, VISNS's 2 k and the clamp item, C7 at 4.7 uF) and records one related new
finding (R4A-N16, the energy an ordinary charger load release returns into VIN_RAW). The FINAL regeneration is now
`drafts/box/fixup4-run3/` (generator sha256 a0452054...455a83c, the file in this worktree); the third fix-up's state is `drafts/box/fixup3-run2/`,
kept unchanged, and sections 1 to 6 are its record, amended only where section 7 says so.

**Round 4 THIRD fix-up (the second re-review, 26 September 2026): section 6 below.** It resolves the second
re-review's two blocking items (the front end's bulk was judged only at the endpoints of bands that hold a resonance,
B3; the front end's 47 nF soft start overloads board E's vehicle entry, B4), reconciles board A's VIN_RAW declaration
with board E's on main faf8c981, resolves R4A-N11, fixes one new finding on the same node (R4A-N14) and records three
(R4A-N12, R4A-N13 and the MLCC ripple item). The FINAL regeneration is now `drafts/box/fixup3-run2/` (generator
sha256 17c204ad...34e272, the file in this worktree); the second fix-up's state is `drafts/box/fixup2-run1/`, kept
unchanged, and sections 1 to 5 are its record, amended only where section 6 says so (the B3 figures of section 5 and
the FE row of the section 4 table are marked CORRECTED in place).

**Round 4 SECOND fix-up (the re-review of the fix-up, 26 September 2026): section 5 below.** It resolves the
re-review's one blocking item (the front end's bulk capacitor was over its rated ripple current) and its six minor
items, fixes one further defect found on the same node (R4A-N8: the charger's input capacitors sat after RAC) and
records three more (R4A-N9 to R4A-N11). The FINAL regeneration is now `drafts/box/fixup2-run1/` (generator sha256
b5ca65ff...2a2ef7, the file in this worktree); the fix-up state it corrects is `drafts/box/fixup-run2/`, kept
unchanged, and sections 1 to 4 below are the record of round 4 and the fix-up, amended only where section 5 says so.

**Round 4 fix-up (review A, 26 September 2026): section 4 below.** It resolves both blocking items of review A and
five of its minor items, and records three further findings (R4A-N6, R4A-N7 and a declaration inconsistency).
The FINAL regeneration is now `drafts/box/fixup-run2/` (generator sha256 b0a37a10...bebee170, the file in this
worktree); the round-4 state it corrects is `drafts/box/run6/`, kept unchanged below as the record of round 4.

Regeneration and gates (round 4, before the fix-up): `drafts/box/run6/` was final (generator sha256
0ff49a55...9aac27). `run1` to `run5` are the earlier iterations, kept: run1 found the heater buck's floating EN read
UNRESOLVED by power_sequence, run2 fixed it, run3 moved C1 to C3, changed the new stages' FETs and took the
controller's name out of the bootstrap diodes' value (suite 1 read it as a switching part), run4 and run5 changed
intent values only (VHEAT_IN's note, U22's share of VBAT, and VBAT's declared source to R17 alone), and run6 changed
comments only (its netlist and intent equal run5's). The netlist difference of run3 to run6 is the same line for
line. The difference against the regeneration of main `82dd1e4d` is `drafts/box/run6/netdiff.txt`, listed entry by
entry in `drafts/r4-netlist-diff.md`.

Schematic-phase gates on the final netlist (base in brackets): erc_gate PASS of 1319 warnings, 0 errors (1089);
port_protect PASS of 21 (21); pin_map_lands PASS of 504 (427); derate PASS of 188 (144); power_sequence PASS of 30
(27); power_path PASS, 30 rails, 67 nodes, 0 undeclared (27, 52); safe_lines PASS of 6 (6); check_contracts PASS of
73 (73); energy_chain PASS of 98 (98); clock_check not applicable (same). netlist_board (SCH-002, the committed A32
board against the netlist) FAIL 244 of 2148 against 60 on the base: expected, the board is not regenerated (O-01).
Full suite on the box with this generator and the regenerated artefacts: `drafts/box/suite3/` (the run5 generator,
which differs from the final one in comments only, and run5's artefacts, equal to run6's), `suite2` and `suite1`
(earlier generators); the failures and what closes each are `drafts/r4-open-items.md` O-02 to O-05.

## 1. Items of the brief

### S-03: charger cell-count strap (VERIFIED)
- Finding: R26 60.4k over R27 40.2k puts CELL_BATPRESZ at 39.96 % of VDDA (39.48 to 40.44 % at 1 %), inside
  SLUSE66A 8.5's VCELL_2S window (35 / 40 / 48.5 %). The charger would load 8.4 V and a 12 V SYSOVP.
- Options: (a) swap the two resistors: 60.04 %, which is **3S**, not a fix; (b) 13.3k over 40.2k: 75.14 %
  (74.76 to 75.51 % at 1 %), inside VCELL_4S (68.4 / 75 / 81.5 %); (c) any other 75 % pair.
- Taken: (b), A02's recommendation, verified against the window. R26 = UNI-ROYAL 0603WAF1332T5E, 13.3 k 1 %
  0603, LCSC C25952 (JLCPCB API 26 Sep 2026, `drafts/jlc/jlc-0603WAF1332T5E.json`). R27 unchanged.

### S-04: charger topology and host duty (VERIFIED topology, INFERRED currents)
- Finding (A02, W2 F-CH-03): every kit load sat on VBAT behind F1 on the PACK side of the RSR shunt R17, so
  shore could deliver no more than ChargeCurrent into load plus pack (256 mA at POR, TI E2E 1316778).
- Options: (a) TI's topology, SLUSE66A Figure 10-1 and 10.1: the system on VSYS, the pack on the far side of
  RSR; (b) keep the loads on CELL+ and make the host write ChargeCurrent = load + charge (a crashed host leaves
  the pack carrying the kit while on shore); (c) no change.
- Taken: (a). It is the only option under which shore carries the kit without any software; (b) is not a
  cheaper correct option, it is a software dependency with a known failure. Netlist change:
  - VBAT is now the charger's VSYS: Q10's drain, C23 to C25, R17 pin 1, R149 and U3 pin 22 moved from
    CH_SRP to VBAT; CH_SRP no longer exists.
  - F1 now runs CELL+ to a new net CELL_FUSED; R17 runs VBAT to CELL_FUSED; R148 (the SRN filter) taps
    CELL_FUSED. The pack reaches the system through F1 and R17 in series.
  - C1, C2 and C3 moved to CELL_FUSED: TI asks for "minimum 20-uF MLCC capacitors after the charge current
    sense resistor" (10.2.2.5; 2 x 10 uF plus 0.1 uF at BATT in Figure 10-1). About 25 uF effective at 16.8 V.
    VSYS keeps well over the 50 uF effective TI asks for (C23 to C25 plus every converter's input capacitors).
  - R17 now carries the pack's discharge current: 0.50 W at 10 A, 1.62 W at 18 A, 2.42 W at the provisional
    22 A of W2 F-PR-03, against the fitted part's 3 W (LCSC C500739, Milliohm LR2512D-3W-5mR-1%, JLCPCB API
    26 Sep 2026). **The maker's datasheet for C500739 is not held: open item O-07.**
- Host duty: RSNS_RAC = 0b (R16 is 10 mOhm) and the watchdog policy are firmware: `drafts/r4-hwfw-contract.md`.

### S-08: power-up (VERIFIED datasheet figures, INFERRED node voltages from A01)
Ten sub-items, each with its choice:
1. **R42 (DEV_EN)**: now a 100 k PULL-UP to board A's +3V3 (A01, W2 F-SQ-01). DEV_EN is 3.3 V whenever MAIN
   has enabled +3V3, whatever the PCA9555's internal pull-up; the panel can still shed the rail. No option
   remained open.
2. **4.7 k pull-downs** on R21, R103, R104, R111, R112, R113 (A01: worst case 0.49 V at the 100 uA IIL bound,
   under every OFF threshold). **R114 and R143 were added to the list**: the S-14 interlock made POE_SW_EN and
   PD_SW_EN logic inputs into U26, where the LM5176's collapsed 10 k divider used to hold them off. Options for
   the whole set: 4.7 k (taken, A01) or a PCA9535 swap (a part substitution, datasheet not held, a mismatch).
3. **U21/U22 OVLO**: 143 k over 10 k (A01's proposal). Verified against SLVSET8A: VOVLO(R) 1.17 / 1.20 / 1.22 V,
   VOVLO(F) 1.08 / 1.10 / 1.13 V. Trip 17.9 to 18.7 V nominal, **17.6 to 19.0 V** with both resistors at their
   1 % extremes: above 16.8 V by 0.8 V and at or under the 19 V recommended maximum input (21 V absolute).
   Release 16.2 to 17.6 V. OVLO pin at 14.4 V: 0.94 V (inside 0.5 to 2 V). 143 k = 0603WAF1433T5E, C22877.
   Options weighed: 140 k (trip 17.2 V minimum, margin 0.4 V) or 147 k (trip 19.6 V maximum, over 19 V);
   143 k is the only E96 value with both margins.
   **U23 (from +5V_DEV) also changed**, 100 k to 40.2 k: its OVLO pin sat at 0.46 V, under the 0.5 V
   recommended minimum (the minor half of W2 F-SQ-06). Trip 5.87 to 6.12 V nominal, release 5.33 V minimum
   with tolerances, above the 5.09 V rail. 40.2 k is C12447, already certified on this board. This was not
   named in the brief's S-08 line; it is the same finding and the same helper argument.
4. **KILL** (LTC2954 pin 8, absolute maximum 7 V) pulled to +3V3 instead of VBAT, the datasheet's own
   arrangement ("connect to a low voltage output supply"). +3V3 is up in milliseconds, inside the 400 to
   650 ms KILL blanking. Options: +3V3 (taken, W5-F15), a VBAT divider (W2) or a separate LDO. +3V3 also
   switches the kit off if the logic rail collapses, which W5 records as wanted.
5. **RAIL_EN** (TPS62933 EN, absolute maximum 6 V, 5.5 V recommended): R2 100 k over a new R184 39 k from
   VBAT: 4.71 V at 16.8 V, 5.05 V at the SMCJ18A's 18 V standoff, 2.81 V at 10 V, above VEN_RISE 1.28 V
   maximum. Options: delete R2 and rely on the TPS62933's 0.7 uA EN pull-up (the LTC2954's EN leakage is up to
   1 uA, so a floating open drain is not a defined high); W2's 100k/47k (5.75 V at 18 V, over the recommended
   5.5 V); 100k/39k (taken). 39 k = 0603WAF3902T5E, C23153 (basic part).
6. **LTC2954 grade**: LTC2954ITS8-1 (-40 to 85 C) for LTC2954CTS8-1 (0 to 70 C). Same datasheet (2954fb),
   same TS8 package, one TS8 pin configuration for both grades, same marking LTCJH (order information table):
   the pin map is identical. LCSC C580654 = LTC2954ITS8-1#TRMPBF, Analog Devices, TSOT-23-8, -40 to +85 C,
   stock 195 (JLCPCB API 26 Sep 2026, `drafts/jlc/jlc-C580654.json`); 5 needed.
7. **PDT** (pin 7) had floated, which forces the kit off after 52 to 82 ms of MAIN held (tPD,MIN). C152 680 nF to
   ground adds 6.4 s per uF: about 4.4 s typical, about 3.3 to 6.0 s over the 2.4 to 3.6 uA PDT current and
   the 10 % capacitor. Options: 470 nF (3.0 s; W5's first figure), 680 nF (taken: the four-second override
   convention), 1 uF (6.4 s, up to 8.8 s worst). C152 = YAGEO CC0603KRX7R7BB684, 680 nF 16 V X7R 0603, C107067.
   PANEL.md's MAIN hold time is W5's text to update (open item O-12).
8. **PI_KILL back-drive (W5-F5)**: R5 100 k to 1.0 k. Three powered slots back-driving through B's level stages
   (10 k pull-ups, body diodes) hold the net at about 0.65 to 0.70 V (INFERRED, W5's diode-drop assumption),
   under Q1's 1.0 V minimum threshold. The panel sources 3.3 mA to kill; Q1 needs only 33 uA through R4 (its
   VGS(th) is specified at 250 uA, so even a 2.62 V GPIO high at the 2.5 V maximum threshold sinks it). Options:
   (a) a unidirectional buffer per slot on board B (W5's recommendation, board B's generator); (b) a strong
   pull-down on A (taken on A). They are not exclusive: (b) makes A robust whatever B does, and (a) stays
   recommended to board B's author (`drafts/r4-interfaces.md` I-02).
9. **PI_SHDN_REQ dual drivers (W5-F6)**: R3 100 k to 10 k (W5's hardware recommendation: a clean idle high
   against the RP2040's 50 to 80 k reset pull-down). INT drives the net directly. **Corrected in the fix-up
   (review A, blocking item 1):** round 4 had put a new R185 1 k between U1 INT (net PI_SHDN_INT) and the net,
   claiming the net read "0.30 V plus INT's VOL". That ignored board B: the net also carries one 2N7002 level
   stage per slot (gen_sch_b.py:574, level(): drain on PI_SHDN_REQ, 10 k pull-up to the slot's 3.3 V on the
   source side, gen_sch_b.py:308-311), and each powered slot feeds up to 0.33 mA into a low net. The node
   equation (3.3 - V)(1 + N)/10k = (V - VOL)/1k gives 0.79 V for N = 2 and 0.97 V for N = 3 (0.70 and 0.84 V
   through the body diodes alone), against the RP2040's VIL of 0.8 V maximum: a MAIN tap stopped being a valid
   shutdown request with two or three modules up. The same pull-ups were counted in item 8 and missed here.
   Options: (a) remove R185, INT on the net as before this round (taken); (b) a series resistor of about
   220 R or less, which keeps V = 3.3 x R / (R + 2.5k) + VOL under 0.4 V but still lets a panel driving high
   push about 13 mA into INT, a pin with no current rating (2954fb absolute maximum ratings: INT -0.3 to 10 V
   only), so it bounds nothing to a rated figure. With (a), INT sinks R3's 0.33 mA plus up to 3 x 0.33 mA,
   about 1.2 mA, under the 3 mA at which VINT(VOL) is 0.11 V typical and 0.4 V maximum: the low is 0.4 V at
   worst with all three slots up. The protection of INT is the firmware contract alone (I-03, FW-A10: the panel
   emulates open drain and never drives the net high). R185 and PI_SHDN_INT no longer exist. **Taken by the
   session under the owner's standing rule of 26 Sep 2026.**

10. **SLOT_EN default** (W1's S-08 line says it is decided here, W3's pull-up proposal): kept OFF (R30, R34 and R38
   100 k pull-downs on A, the RP2040 pads' reset pull-downs). Options: (a) default off, "no panel, no compute", the
   panel updated by SWD or in-application with its watchdog configured to preserve the pads (W5-F4 option a, no
   board change); (b) default on through pull-ups, which is safe only once a powered slot can no longer kill the
   kit through PI_KILL (W5-F5) and which would power all three modules on every MAIN press whatever the panel says;
   (c) a latch on A holding the last commanded slot state across a panel reset. Taken: (a), W5's recommendation
   for now. With R5 at 1.0 k (item 8) the precondition for (b) holds on board A; (b) or (c) stays a design
   question for the IOHA review, because the three modules exist to remove single points of failure and the panel
   is one (appendix 32.52).

### S-14: outlet interlock (VERIFIED topology from gen_sch_d.py)
- The PA keys when board D's PA_KEY = KEY AND PA_EN is high (gen_sch_d.py U14). TR_APRS is KEY through 100 R
  (gen_sch_d.py R48, active high) and PA_EN is board A's own gate, so board A can form PA_KEY itself.
- Options: (a) NAND of TR_APRS and PA_EN gating both outlets' enables (taken); (b) an inverter on TR_APRS only
  (drops the outlets on an exciter-only transmission with the PA rail off, which the ruling does not ask);
  (c) firmware only (not a hardware interlock, rejected by D-11's wording).
- Built: U30 SN74LVC1G00DBVR (TI SCES212AC, DBV pinout 1 A, 2 B, 3 GND, 4 Y, 5 VCC, -40 to 125 C, LCSC C7826)
  makes OUTLET_OK = NOT (TR_APRS AND PA_EN). U26's two spare gates (tied off until now) make
  POE_EN = POE_SW_EN AND OUTLET_OK and PD_EN = PD_SW_EN AND OUTLET_OK. The expander bits are renamed
  POE_SW_EN (U27 pin 8) and PD_SW_EN (U28 pin 13); the LM5176 EN pins keep their net names. C153 decouples U30.
- D-11's bounded all-transmit (key-down time above a state of charge) is firmware thresholds: contract items.

### S-20: charge current (firmware, no resistor)
- The BQ25731 charge current is a register (ChargeCurrent, 256 mA at POR); no resistor on board A sets it
  (the ILIM_HIZ divider sets the INPUT limit). Recorded as a firmware item: ChargeCurrent at most 3.0 A for
  4S3P, three times the Samsung 35E's 1,020 mA cycle-life charge current (W2 runtime section 8, cell sheet 3.5).

### D-17: USB-C CC ESD array (VERIFIED datasheets)
- Part: TI TPD2E2U06QDBZRQ1 (SLLSEJ9E, Oct 2022): SOT-23 (DBZ) pin 1 IO1, pin 2 IO2, pin 3 GND; VRWM 5.5 V,
  VBR 6.5 to 8.5 V; CL 1.5 pF typ, 1.9 pF max; IEC 61000-4-2 25 kV contact; AEC-Q101; -40 to +125 C. LCSC
  C488151, stock 2,536. Against the TPS25740A's CC pins: 5.5 V recommended maximum and 6 V absolute (SLVSDG8B
  7.1, 7.3), so the array never conducts in service; C96/C97 (330 pF) stay inside the 200 to 600 pF C(RX)
  window with 1.9 pF added.
- Options: the DRL package of the same die (SOT-553, C1972959, 8,699 in stock) or the DBZ (taken: the SOT-23 land
  this board already uses, easier to assemble and inspect); a PESD-type single-line diode (higher capacitance).
- Placement at J_USBC_OUT is a layout item (O-01).

### D-12: USB-C power only, data to the Glenair 233-370
- The data path is unchanged in board B terms (bank 3 hub port 3, USB_WALL_P/N on J_AB2). J_USBW becomes the
  Glenair lead: PH 1x4 in USB order, pin 1 VBUS_WALL, 2 USB_WALL_N, 3 USB_WALL_P, 4 GND (same land, C131334).
  J_USBC_OUT is labelled power only (its pins never carried data).
- A host port needs VBUS. Options: (a) an eFuse on board A from +5V_DEV (taken: the TPS259631DDAR and its helper
  are already on the board, datasheet held, no board B change); (b) a port-power switch on board B carried over
  J_AB2 (needs B's generator and a ribbon pin change); (c) VBUS from the PD outlet (would tie the two ports).
- U32 TPS259631DDAR, EN = USBX_EN (U28 pin 4, formerly the spare EXP2_SPA, 4.7 k pull-down R190: off until the
  panel turns it on), FLT = USBX_FLT (U28 pin 5), ILM 1.00 k = 0.89 A (TPS2596 equation 7), OVLO 40.2k/10k
  (about 6 V). C156 22 uF on VBUS_WALL. The USBLC6-2 U29 takes its VBUS pin from VBUS_WALL.
- The interface record is `drafts/r4-interfaces.md` I-05.

### F-PR-01: PA 13.8 V rail protection (VERIFIED limits)
- Options: (a) the 10 A mini blade of 32.55 (does not act near 6 A: a blade carries well over its rating for
  minutes, and the cycle limit already bounds a hard short); (b) an eFuse such as the TPS25982 (15 A class,
  datasheet held) as a new controller in the 6 A path; (c) the stage's own average current loop with a 6 mOhm
  ISNS shunt (taken): 43 to 57 mV across 6 mOhm is 7.2 to 9.5 A (SNVSAI1D VSNS), above the 6.0 A peak and the
  5.4 A of 30 W at 40 %, below the JST-VH lead's 10 A, self-recovering, no new part or land.
- R55 = Vishay WSL25126L000FEA, 6 mOhm 1 % 2512, 1.0 W at 70 C, AEC-Q200 (Vishay 30100 rev 23-Nov-2023,
  `drafts/datasheets/vishay-wsl.pdf`), LCSC C843882, 0.54 W at 9.5 A. The INA226 U14 shares it: calibration
  changes (firmware). The energy-chain stage for the PA branch is the integrator's (O-09).

### F-PR-04: +5V_DEV and slot 2 over the AP64500's 5 A (VERIFIED rating, INFERRED sums)
- Options: (a) split the device rail (W2's first recommendation: needs board B to re-feed three radios from a
  second lead, and cannot help slot 2, whose one module is its load); (b) a TPS56637 (6 A: no margin at 6.0 A
  and its RPA land is not in KiCad or meshsat.pretty, and footprints are not this author's file); (c) an LM5176
  stage (taken for both +5V_S2 and +5V_DEV): the part is certified five times on this board with its datasheet
  held and every land in the KiCad library, and its average loop limits at 7.2 to 9.5 A across a 6 mOhm ISNS
  shunt, above both peaks (6.9 A on +5V_DEV with the Glenair port, 5.8 A in slot 2's 5G burst).
- FETs for the two new stages: CSD19532Q5B (SLPS414B held; 48 nC at 10 V; C473333) rather than the PA stage's
  CSD18510Q5B (118 nC typ, 153 nC max at 10 V, SLPS632 fetched): the LM5176's VCC current limit is 65 mA minimum
  (SNVSAI1D IVCC), and two switching gates at the real 206 kHz take about 14 mA with the CSD19532Q5B against
  about 41 mA with the CSD18510Q5B (INFERRED from the Qg curves; round 4 wrote 300 kHz, 21 and 60 mA).
- **Status after the second fix-up: DONE (schematic only).** The values are uncertified (O-06), the board is not
  regenerated (netlist_board FAIL, O-01) and the bench loop reading is owed (FW-A15 item 7), so the label is the
  schematic's (the re-review's minor item 4). **Status after the fix-up read: DONE (paper design).** Review A marked
  this item PARTIAL until the two new stages' loops were designed; section 4 B2 designs them (and the other five), with three EEHZK1E151XP bulk capacitors
  on each of +5V_S2 and +5V_DEV, and BIAS moved to VBAT (R4A-N6). The bench reading is FW-A15.
- Inductor XAL1010-682ME (C3911637, certified), output capacitors 3 x 22 uF 25 V 1210 (C2918511), ISNS and INA226
  shunt WSL25126L000FEA (C843882), EN/UVLO driven directly (no divider, `en_div=False`), SLOT_EN2 held off by R34
  and DEV_EN held on by R42 to +3V3. U5/U7 change land (SO-8EP to HTSSOP-28) and L4/L6 change land (XAL6060 to
  XAL1010): a placement item (O-01).
- Slots 1 and 3 keep their AP64500s: open item O-15 (their continuous sum reaches 5.0 A if the AW7915 draws the
  3 A its buck is sized for; INFERRED).

### F-PR-06: heater mat at 196 % of rating (VERIFIED mat rating)
- Options: (a) firmware duty limit (12/VBAT)^2 on HEAT_EN (a crashed panel leaves 196 %); (b) a series element
  (7.7 Ohm and 3 W at 16.8 V, or U22 in current limit dissipating the same until it cycles thermally); (c) a mat
  rated for the 4S range (an off-board part, not a board fix); (d) a regulated 12 V rail (taken): the only option
  that bounds the mat's power in hardware at every pack voltage.
- Built: U33 TPS62933DRLR (SLUSEA4D held, C3200405) behind U22, TI Table 10-2's 12 V row (140 k over 10 k),
  L12 Coilcraft XAL4040-153ME 15 uH (Isat 2.9 A; the larger of TI's 12 uH typical keeps slope margin; datasheet
  held, hand-fit like every Coilcraft part on this board), two 22 uF 25 V 1210 out (about 18 uF effective at 12 V,
  TI: 10 uF minimum), 10 uF 25 V plus 100 nF in, SS 10 nF, RT open (500 kHz), EN on a 100k/20k divider from
  VHEAT_IN (starts at about 7.3 V; 2.8 V at 16.8 V and 3.2 V at 19 V, inside EN's 5.5 V). A floating EN would
  also enable it, and the first regeneration used that; power_sequence then read the rail UNRESOLVED, so the
  enable is defined. U22 keeps the switch, the 1.0 A input limit, the fault line and the OVLO. Below about
  12.9 V of VBAT the buck runs at maximum duty and the mat gets less than 7.5 W.

### A04: D2 (keep)
- A03's clamp table reads board A's D1 to D4 orientation CORRECT (cathode pad 1 on the protected net) and D2 is
  SMCJ40A (C224052) in the generator. Nothing changed. A03's separate verdict that the Device:D_TVS symbol is
  bidirectional for these one-way parts is S-09's, not in this brief: open item O-13.

## 2. Defects found while doing F-PR-04, fixed in the shared helper (new findings)

These were not in the brief. They are fixed because the two new stages of F-PR-04 are built by the same helper
and would carry the same defects, and because this author is the only writer of `gen_sch_a.py` this round. Both
are open to the reviewer's challenge.

- **R4A-N1 (critical, VERIFIED): no LM5176 stage had bootstrap diodes.** SNVSAI1D 7.3.14: "The CBOOT1 and CBOOT2
  capacitors are charged through external Schottky diodes connected to the VCC pin as shown in Figure 8-1"; the
  functional block diagram (7.2) has no internal bootstrap diode (rendered and read,
  `drafts/scratch/lm5176_p14-14.png`, `lm5176_p21-21.png`). In buck mode HDRV2 stays on and HDRV1 switches, both
  from bootstrap capacitors nothing charged: none of the five stages (FE, PA, HF, PoE, PD) could have started.
  Fix: two BAT46W-7-F per stage (Diodes DS30044 Rev. 20-2: 100 V, 150 mA, SOD-123, -55 to +125 C; C83152),
  anode on VCC, cathode on BOOT. Reverse voltage at most 54 V (PoE BOOT2), average current about 16.5 mA at the
  real 206 kHz (the round-4 text said 24 mA at 300 kHz; corrected in the fix-up).
- **R4A-N2 (major, VERIFIED): the SLOPE pin carried a 30 k resistor.** The pin table: "A capacitor connected
  between the SLOPE pin and AGND provides the slope compensation ramp"; 8.2.2.8 Equation 26: CSLOPE =
  gmSLOPE x L / (RSENSE x ACS). Fix: a C0G capacitor per stage at the E12 value at or below dead-beat (TI's own
  example takes the smaller value): FE 10 uH / 5 mOhm = 800 pF, 680 pF (C30816); PA, HF, PD and the two new
  stages 6.8 uH / 5 mOhm = 544 pF, 470 pF (C27694); PoE 22 uH / 10 mOhm = 880 pF, 820 pF (C99081; the fix-up
  replaced it with 560 pF, C43962, for the 15 uH of R4A-N7). The five
  30 k resistors R9, R53, R63, R69 and R79 are retired and the capacitors take new references C147 to C151.
  COMP-range check (Equation 7) for the 5 V stages at 16.8 V: about 1.4 V, above the 0.3 V floor (INFERRED).
- The helper now refuses a stage without its slope capacitor and bootstrap diodes.

## 3. Findings recorded, not fixed (not in the brief)

- **R4A-N3 (major, INFERRED)**: the PA, HF and PD stages use CSD18510Q5B (153 nC maximum at 10 V). In the
  buck-boost transition region all four gates switch: about 4 x 95 nC x 206 kHz = 78 mA from a VCC regulator
  limited at 65 mA minimum (the round-4 text said 120 mA at 300 kHz; review A minor 1 corrected the frequency,
  and the conclusion stands). Recommended fix: the CSD19532Q5B used by the front end and the two new
  stages (same land). Needs the Qg-at-7.35 V reading confirmed from the curves and a loss check at 6 A.
- **R4A-N4 (minor, VERIFIED text)**: the helper's CS filter uses 1 nF across the pins with 100 R each (200 ns),
  where TI's Figure 8-1 uses 47 pF. The helper's comment argues the choice; a loop check is owed.
- **R4A-N5**: the helper's compensation (10 k, 10 nF, 100 pF) was identical for every stage. **Re-rated
  CRITICAL for all seven stages and RESOLVED on paper in the fix-up (section 4, B2); for the front end only after the
  second fix-up (section 5, B3), which gave VBUS20 the bulk its ripple current needs and a loop designed on it.** The soft start (47 nF)
  is still one value for all seven; it is not a stability item.

## 4. Round 4 fix-up (review A, 26 September 2026)

Review A (APPROVE_WITH_FIXES) raised two blocking items and ten minor ones. Both blocking items are fixed; the
disposition of every minor item is in the table at the end of this section. Every choice below that had more than
one option is **taken by the session under the owner's standing rule of 26 Sep 2026**. Only
`v2/ecad/tools/gen_sch_a.py` and `drafts/*` were written; nothing was committed or pushed.

**Regeneration.** Box vast.ai 52646493, `/root/r5/a` only, from main `82dd1e4d` with this generator (sha256
b0a37a10...bebee170): `drafts/box/fixup-run2/` (final; `fixup-run1` differs only in the VHEAT_IN declaration,
and its netlist difference is identical). The netlist is diffed against the 82dd1e4d baseline regenerated in
round 4 (`/root/r4/a/out/base`, read only) and against the round-4 author's own regeneration (`/root/r4/a/out/repo`).
Gates on the final netlist (round 4 in brackets): erc_gate PASS of 1344 warnings, 0 errors, the same three baseline
warning types (1319); port_protect PASS of 21 (21); pin_map_lands PASS of 518 (504); derate PASS of 218, 0
undeclared nets, 0 under-rated (188); power_sequence PASS of 30, 0 unresolved (30); power_path PASS, 30 rails,
67 nodes, 0 undeclared, two short feeds that the baseline has too (VBAT and VIN_RAW; round 4 had a third, VHEAT_IN,
fixed here); safe_lines PASS of 6 (6); check_contracts PASS of 73 (73); energy_chain PASS of 98 (98); clock_check
not applicable (same). netlist_board (the committed A32 board against the new netlist) FAIL 258 of 2162 (244 of
2148; 60 on the base): expected until the board is regenerated (O-01). build_sch.sh now completes (exit 0):
pdftoppm is present on the box. The main clone's status was the same before and after. Full suite on the box with
this generator and its regenerated artefacts (`drafts/box/fixup-suite/`, `drafts/scripts/r5a_suite_box.sh`): 1399
passed, 4 failed, 2 skipped, the same four failures with the same causes as round 4 (O-02 to O-05: pcb_emc.yaml
lacks U33, pcb_sensitive.yaml names CH_SRP, PCB-BRING-UP.md needs its render (identical diff to round 4's),
test_sensitive_nodes asserts the old R148/R149 lines); the suite also rewrites ROTATION-CHECKLIST.md, now with
two polymer lands on board A as well (O-05).

### B1: PI_SHDN_REQ, R185 removed (review A blocking item 1) (VERIFIED)
- Finding confirmed from the netlists: board B hangs three 2N7002 level stages on PI_SHDN_REQ (gen_sch_b.py:574,
  level(): drain on PI_SHDN_REQ, a 10 k pull-up to each slot's 3.3 V on the source side, gen_sch_b.py:308-311).
  With INT behind R185 (1 k) the low sat at 0.79 V with two slots and 0.97 V with three, against the RP2040's
  0.8 V VIL maximum. Round 4 missed these pull-ups here while counting them for PI_KILL.
- Options: (a) remove R185, INT directly on the net as before round 4 (taken); (b) a series resistor of about
  220 R or less, which keeps the low under 0.4 V + VOL but still passes about 13 mA into INT if the panel drives
  the net high, and INT has no current rating to hold that against (2954fb lists INT only as -0.3 to 10 V), so
  it bounds nothing to a rated figure.
- Result: U1 pin 5 is back on PI_SHDN_REQ; R185 and the net PI_SHDN_INT are gone. INT sinks R3's 0.33 mA plus up
  to three slots' 0.33 mA, about 1.2 mA, under the 3 mA at which VINT(VOL) is 0.4 V maximum: 0.4 V worst case.
  R3 stays 10 k. INT's only protection against a panel driving high is the firmware contract (I-03, FW-A10), now a
  hard contract. S-08 item 9 above, I-01, I-03 and FW-A10 are rewritten; the generator's comment item 5 too.

### B2: every LM5176 stage gets its own loop design (review A blocking item 2; R4A-N5 re-rated CRITICAL)
- Finding confirmed and widened. The helper's single set (Rc1 10 k, Cc1 10 nF, Cc2 100 pF) on SNVSAI1D's
  small-signal model gives, on the seven stages as built in round 4, a worst-corner phase margin of -120 (FE),
  -44 (S2), -45 (SD), -107 (PA), -104 (HF) and -117 degrees (PD), and +21 degrees with 2.4 dB of gain margin on
  PoE (`drafts/box/loop/search/out-*_0.txt`, the helper line). The review's hand figure (Equation 44, crossover
  about 200 to 290 kHz on S2 and SD's local ceramics) agrees in order.
- The model (`drafts/scripts/loop_design.py`): peak/valley current mode with the sampling double pole at Fsw/2
  (Q 0.4 to 0.8), the boost RHP zero and R/2 output pole (Equations 38 and 40), gmEA 1.31 mS, 20 MOhm, ACS 5,
  RT 40.2 k = 206 kHz (Equation 5; 180 to 232 kHz over fSW(1)), and a two-node output network: the stage's own
  ceramics and bulk, a lead (R + sL) and the load's own decoupling at the far end. **Validation:** the same code
  on TI's worked example (6 V to 12 V, 6 A, 4.7 uH, 8 mOhm, Rc1 10 k, Cc1 33 nF, Cc2 560 pF, 412 uF) gives 4.19 kHz
  at 67 degrees and 12 dB, TI's designed 4 kHz; the script refuses to design if that check fails.
- Corners per stage: every input mode (buck and boost ends), every output (PD's 5, 9 and 15 V), ceramics at two
  DC-bias bands, remote capacitance absent and at two values behind two lead inductances, full and light load,
  Q 0.4 and 0.8, fSW 180 and 232 kHz, gm x0.8 and x1.2, and for bulk C x0.8 and x1.2 with ESR at 0.3 and 2.0 of
  the maximum. The ceramic bands and remote capacitances are INFERRED (no DC-bias curves or load decoupling
  figures are held); each stage's band is written beside it in the script.
- Pass (all corners): PM 50 degrees or more, GM 10 dB or more, |1 + T| 0.5 or more, every corner crossing unity
  inside the grid, every crossover at or under Fsw/20 (TI 8.2.2.14, 10.3 kHz) and fRHP/3, Cc2's pole under
  Fsw/2 and over 3 x the zero, and the closed-loop output impedance at the stage's output under the rail's bound.
  The bound is a SESSION design target: 5 percent of VOUT over the stage's load step, and a third of V^2/P where
  the load is a converter (Middlebrook); FE has only the Middlebrook bound, because the BQ25731 regulates its own
  input current and backs off on a VBUS droop ("Input current and voltage regulation (IINDPM and VINDPM) against
  source overload", SLUSE66A features).
- **No compensation alone passes on six stages** (FE, S2, SD, PA, HF, PD: no stable set in the searched E6/E12
  values with no bulk; `search/out-*_0.txt`). Their ceramics are 15 to 57 uF effective while the lead and the
  load's decoupling add 0 to 300 uF behind 0.08 to 1 uH: an undamped resonance and a capacitance spread no single
  Rc1/Cc1/Cc2 spans. The review's own suggestion for S2 and SD (Rc1 about 0.34 to 0.5 k for a 10 kHz crossover on
  the local 45 to 66 uF) was checked (`drafts/box/loop/final/s2_local_only.txt`): on the local ceramics alone,
  Rc1 330 to 470 R crosses at 6 to 22 kHz over the corners with at most 42 degrees of phase margin, and the output
  impedance it leaves is 5 to 38 times the rail's bound; with board B's bulk behind the 150 mm lead no set from
  330 R upward is stable at all. Options weighed per stage: 0 to 3 hybrid-polymer bulk capacitors of four Panasonic ZK
  parts (one series sheet, held at v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf: EEHZK1V101XP 100 uF 35 V,
  EEHZK1E151XP 150 uF 25 V, EEHZK1V181P 180 uF 35 V, EEHZK1E471P 470 uF 25 V; no DC-bias loss, and their ESR
  damps the resonance), or more ceramics (PoE, where 35 V parts cannot sit on 54 V). Taken per stage: the
  smallest bulk that passes under the strict Fsw/20 ceiling, preferring the small D8 land where it passes, then
  the set with the highest worst-case phase margin (to 65 degrees), then the fastest. The search is
  `drafts/box/loop/search/` (58 runs); the final sets are re-read over every corner in `drafts/box/loop/final/`
  (the final script, with the every-corner-crosses check added after the search):

The table as amended by the second fix-up (section 5) and **the third (section 6): the FE row is now the third
fix-up's node** (six EEHZK1V331P, C13 to C15 on FE_OUT, eighteen ceramics on VBUS20; the same compensation, re-read
on that node; the bulk figure from `drafts/scripts/ripple_dense.py` over the whole INFERRED bands, which replaces the
second fix-up's endpoint figure of 2.66 A, 95 percent, CORRECTED to 3.43 A, 122 percent, for its own node). Before
that, the FE row was the second fix-up's design (the fix-up's row
read 1.5 k / 220 nF / 2.2 nF with one EEHZK1V101XP, PM 66.1, GM 11.7 dB on the old node, and is replaced), and the
last two columns are new: the worst per-part ripple current of each stage's bulk against its rated figure
(`drafts/scripts/bulk_ripple.py`: SNVSAI1D Equation 19's current split harmonic by harmonic between the parts, over
every corner; `drafts/box/loop2/ripple.txt`), and the gain margin on the widened band (Q 0.4 to 1.5, L 0.8 to 1.2 of
nominal, the re-review's minor item 1; `drafts/box/loop2/wide/`, phase margins unchanged to within 1.2 degrees).

| Stage | Rc1 / Cc1 / Cc2 (LCSC) | Local addition (LCSC) | PM | GM | abs(1+T) min | Crossover | Zout peak / bound | Bulk ripple, worst part (rated; the stage's Eq. 19 total) | GM, widened band |
|---|---|---|---|---|---|---|---|---|---|
| FE (U2) VIN_RAW to VBUS20 (third fix-up) | 15 k / 220 nF / 680 pF (C22809, C160828, C30816) | 6 x EEHZK1V331P 330 uF 35 V, C163, C178 to C180, C199, C200 (C278516); C13 to C15 on FE_OUT before R11 (R4A-N14); 15 more 10u 50V on VBUS20, C181 to C189 and C201 to C206 (C596319), with C20 to C22 (R4A-N8) | 73.1 | 15.7 dB | 0.79 | 0.71 to 3.6 kHz | 89 mOhm / 1.17 Ohm | 2.10 A (2.8 A, 75 % matched; 87 % at a 2:1 ESR spread; 6.3 A at 9 V and 5.7 A, plus the charger's up to 5.7 A, SLUSE66A Eq. 4; dense bands) | 14.0 dB (PM 72.9) |
| FE, second fix-up (superseded) | 15 k / 220 nF / 680 pF (C22809, C160828, C30816) | 4 x EEHZK1V331P 330 uF 35 V, C163 and C178 to C180 (C278516); 9 more 10u 50V, C181 to C189 (C596319); C20 to C22 moved here (R4A-N8) | 66.3 | 12.2 dB | 0.69 | 1.05 to 5.4 kHz | 89 mOhm / 1.17 Ohm | CORRECTED: 3.43 A (122 %) inside the bands; the 2.66 A (95 %) read at their endpoints; 6.3 A at 9 V and 5.7 A, plus the charger's up to 5.7 A, SLUSE66A Eq. 4) | 10.5 dB (PM 64.8) |
| S2 (U5) +5V_S2 | 2.2 k / 100 nF / 1 nF (C4190, C14663, C1588) | 3 x EEHZK1E151XP 150 uF 25 V, C164 to C166 (C542453) | 68.3 | 15.1 dB | 0.79 | 2.6 to 9.4 kHz | 72 / 85 mOhm | 0.28 A (1.8 A, 15 %; buck, the triangle's 0.84 A) | 9.4 dB |
| SD (U7) +5V_DEV | 2.2 k / 100 nF / 1 nF | 3 x EEHZK1E151XP, C167 to C169 | 68.3 | 15.1 dB | 0.79 | 2.9 to 9.4 kHz | 72 / 85 mOhm | 0.28 A (1.8 A, 15 %; buck, 0.84 A) | 9.4 dB |
| PA (U13) +13V8_PA | 6.8 k / 100 nF / 1.5 nF (C23212, C14663, C37788) | 2 x EEHZK1E471P 470 uF 25 V, C170, C171 (C242138) | 64.9 | 12.8 dB | 0.73 | 1.5 to 5.4 kHz | 86 / 127 mOhm | 2.15 A (2.8 A, 77 %; 3.7 A at 10 V and 6 A) | 9.9 dB |
| HF (U15) +12V_HF | 3.3 k / 100 nF / 1 nF (C22978, C14663, C1588) | 2 x EEHZK1E151XP, C172, C173 | 67.1 | 12.7 dB | 0.75 | 2.5 to 9.1 kHz | 134 / 300 mOhm | 0.55 A (1.8 A, 31 %; 0.89 A at 10 V) | 8.2 dB |
| PoE (U16) +54V_POE | 4.7 k / 100 nF / 470 pF (C23162, C14663, C27694) | 2 more 10 uF 100 V 1210, C176, C177 (five in all) | 64.7 | 13.1 dB | 0.70 | 1.5 to 8.6 kHz | 3.8 / 4.5 Ohm | no bulk; worst ceramic 0.37 A (1.3 A at 10 V) | 12.0 dB |
| PD (U19) PD_VPWR | 3.3 k / 220 nF / 1.5 nF (C22978, C160828, C37788) | 2 x EEHZK1E471P, C174, C175 | 70.3 | 15.0 dB | 0.78 | 0.65 to 8.4 kHz | 206 mOhm peak, 0.83 of its per-profile bound | 1.25 A (2.8 A, 45 %; 2.1 A at 10 V to 15 V 3 A) | 9.85 dB |

- Load steps and bounds per stage (session targets, in the script): S2 and SD 3 A (a 5G burst, INFERRED) and
  29.5 / 35 W converter loads; PA 5.4 A (a 30 W carrier keyed); HF 2 A and 24 W; PoE 0.6 A and 32 W; PD 3 A at
  each profile and 3 A x VOUT; FE Middlebrook at 100 W.
- Every value's LCSC code was read back from the JLCPCB parts API on 26 September 2026 (`drafts/jlc/`); 150 nF
  was avoided (C159800, stock 0). Stock against five boards: EEHZK1E151XP 478 for 40, EEHZK1E471P 930 for 20,
  EEHZK1V101XP 4,101 for 5 more.
- The helper now REFUSES a stage without its own compensation, and refuses a bulk part run above 80 percent of
  its rating. The Cc1 values stay at or under 220 nF (TI's example: 33 nF), so COMP charges quickly at start-up.
- It is a paper design (TI: "Each design should be tuned in the lab"). FW-A15 item 7 is the bench reading
  (injection Bode per stage and the load steps above), and the loop script's INFERRED bands are the first thing
  to replace with measured values.

### R4A-N6 (new, VERIFIED text): BIAS below its recommended range on the 5.1 V stages and PD's 5 V profile
- SNVSAI1D 6.3 recommends BIAS at 8 to 36 V when VCC is in regulation, and 7.3.2 recommends BIAS to VOUT only
  above 8.5 V. The helper tied BIAS to VOUT, so S2, SD (5.1 V) and PD at 5 V sat under it (review A minor 3 named
  S2 and SD; PD at its 5 V profile is the same case).
- Options: BIAS to GND or open (the pin table only says VCC draws from VIN when no supply is on BIAS); BIAS to
  VBAT (taken): 10 to 16.8 V, 29 V at the SMCJ18A's clamp, inside 8 to 36 V and the 40 V absolute maximum, and VCC
  then draws from BIAS, which is the input anyway. Netlist: U5.24, U7.24 and U19.24 move to VBAT. FE, PA and HF
  (20, 13.8 and 12 V) keep BIAS on VOUT; PoE already had it on VBAT.

### R4A-N7 (new, VERIFIED): the PoE stage's 22 uH inductor does not exist
- XAL1010-223ME is in neither the held Coilcraft XAL1010 sheet (Document 804-1, 0.22 to 15 uH) nor the JLCPCB
  catalogue (`drafts/jlc/jlc-XAL1010_223.json`, 0 hits); jlc-handfit.txt already called its Isat unverified.
- Options: fetch a newer Coilcraft sheet (coilcraft.com answers the runner 403); a different series in 22 uH (new
  land, new datasheet); XAL1010-153ME, 15 uH, the series' largest part, same land (taken): Isat 15.5 A, Irms 9.9 A,
  DCR 18.6 mOhm maximum, LCSC C2802562 (XAL1010-153MED, stock 1,362), so L10 is now JLC-assembled instead of
  hand-fit. At 10 V in and 0.6 A out: 3.24 A average, 2.6 A ripple, 4.6 A peak. CSLOPE follows Equation 26:
  600 pF dead-beat, 560 pF C0G (FH 0603CG561J500NT, C43962, stock 2,936; the Samsung CL10C561 has 0 stock).
  Equation 9 puts COMP at 2.48 V at 10 V in and full load, under 3 V (corrected in the second fix-up: this line read
  2.59 V; the re-review's figure, reproduced by `drafts/scripts/comp9_corners.py`). At the tolerance corners (L at
  -20 percent, fSW 180 kHz, the slope current at +24 percent, CSLOPE at -5 percent) it reaches 2.84 V at 10 V in and
  2.89 V at 9 V: 0.11 to 0.16 V under the ceiling, where round 4's 22 uH / 820 pF gave 2.50 V (the re-review's minor
  item 3). Small but positive; the bench reading is FW-A15 item 7.
  The PoE loop (B2) is designed with 15 uH.

### Declaration fix: VHEAT_IN typical current
- Round 4 declared VHEAT_IN at 0.55 A typical while its own note computes 7.5 W / 0.9 / 14.4 V = 0.58 A;
  power_path read the feed SHORT (the U33 buck draws 0.58 A). Now 0.58 A typical, 0.9 A peak. Intent only.

### Review A minor items
| Minor item | Disposition |
|---|---|
| 1. RT 40.2 k labelled 300 kHz (it is 206 kHz) | Fixed: the seven RT values read "40.2k (206 kHz)"; the helper's bootstrap figure, the F-PR-04 gate-charge figures and R4A-N3 are recomputed at 206 kHz (16.5 mA, 14 / 41 mA, 78 mA; no conclusion changes). pcb_emc.yaml carries 300 kHz for U2, U13, U15, U16, U19: O-04 now asks 206 kHz (180 to 232) for all seven |
| 2. R17 carries the pack current; its maker datasheet is not held | Open (O-07). Moving R17 to the held RALEC LR2512-23R005F4 (C154688) was weighed and not taken: 26 in stock on 20 Sep against board E's 20 and board A's gauge shunt row on the same code |
| 3. BIAS tied to 5.1 V outputs | Fixed: R4A-N6 above |
| 4. port_protect answers PD_CC1/2 by U18, not U31 | The answer comes from boards/a.json's `protected_in_part` declaration (lines 508 to 516), which is not this author's file: O-20 asks the integrator to remove it so port_protect finds U31 (its value names "ESD", which the protector pattern matches) |
| 5. XAL1010-682ME text says Isat 17 A (sheet: 21.8 A) | Fixed on L4, L6, L8; L1's XAL1010-103ME text corrected to 17.5 A and given its JLC code C6358489 (stock 1,051) |
| 6. R186 (C21190) had no JLC read-back | Done: `drafts/jlc/jlc-C21190.json`, UNI-ROYAL 0603WAF1001T5E, 1 k 1 %, basic, stock 23.8 M |
| 7. U21/U22 release at 16.2 to 17.6 V after an OVLO trip | Recorded for PANEL/firmware text (O-12) |
| 8. BAT46W bootstrap recharge peaks not assessed | Added to the bench list, FW-A15 item 6 |
| 9. C156 22 uF against USB 2.0's 120 uF | Unchanged, disclosed (O-14) |
| 10. CS filter 1 nF against TI's 47 pF, 8 mV offset | Open (R4A-N4, O-18): a current-limit and loop item for the bench, not changed on paper |

## 5. Round 4 second fix-up (the re-review of the fix-up, 26 September 2026)

The re-review (APPROVE_WITH_FIXES) found both of review A's blocking items resolved and raised one new blocking item
(the front end's bulk capacitor C163 over its rated ripple current) and six minor ones. All are dispositioned below.
Every choice with more than one option is **taken by the session under the owner's standing rule of 26 Sep 2026**.
Only `v2/ecad/tools/gen_sch_a.py` and `drafts/*` were written; nothing was committed or pushed; the main clone was
not touched (its status is the same before and after every box run).

**Regeneration.** Box vast.ai 52646493, `/root/r5/a/run3` only (the fix-up's `/root/r5/a/out` and the round-4
directories were read, never written), from main `82dd1e4d` with this generator (sha256 b5ca65ff...2a2ef7):
`drafts/box/fixup2-run1/` (`drafts/scripts/r5a2_box.sh`). Gates on the final netlist (the fix-up in brackets):
erc_gate PASS of 1376 warnings, 0 errors, the same three warning types (1344); port_protect PASS of 21 (21);
pin_map_lands PASS of 539 (518); derate PASS of 242, 0 undeclared nets, 0 under-rated (218); power_sequence PASS of
30, 0 unresolved (30); power_path PASS, 30 rails, 67 nodes, 0 undeclared, the same two short feeds (VBAT, VIN_RAW;
O-21); safe_lines PASS of 6 (6); check_contracts PASS of 73 (73); energy_chain PASS of 98, the same one board B
coordination finding (98); clock_check not applicable (same). netlist_board (the committed A32 board against the new
netlist) FAIL 282 of 2183 (258 of 2162; 60 on the base): expected until the board is regenerated (O-01).
build_sch.sh exit 0. **Netlist difference** against the fix-up: 21 parts added, 1 part changed, 2 values changed, 3
pins moved, 0 nets added or removed (`drafts/box/fixup2-run1/netdiff-vs-fixup.txt`; every entry with its finding ID in
`r4-netlist-diff.md`, "Every entry against the fix-up": 37 entries, 0 unexplained, by
`drafts/scripts/classify_diff_fixup2.py`, which also classifies all 451 entries against the base). **Full suite** on the box (`drafts/box/fixup2-suite/`, `drafts/scripts/
r5a2_suite_box.sh`): 1399 passed, 4 failed, 2 skipped, the same four failures with the same messages as the fix-up
(O-02 to O-05; `suite-failures.txt` is byte-identical to the fix-up's, and so is the rendered PCB-BRING-UP.md
difference; the rotation checklist differs only in the example reference of two land rows).

### B3: the front end's bulk, sized for its ripple current (the re-review's blocking item) (VERIFIED ratings and datasheet text; INFERRED parasitics)
- **Finding confirmed, and larger than stated.** The ZK series sheet (`v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf`,
  Characteristics list) rates EEHZK1V101XP at 1700 mA rms (100 kHz, +125 C; the frequency correction is 1.00 from
  100 kHz up for 100 uF and more) and says "Do not allow an excessively large ripple current (larger than the rated
  ripple current specified in the specifications)". My split reproduces the re-review's corner exactly (FE's own
  current, the fix-up's netlist, 5 A, ESR 10.5 / 35 mOhm, the re-review's ESL: 3.87 / 2.16 A at 9 V, 2.88 / 1.66 A at
  12 V). Two things neither the fix-up nor the re-review counted make it worse:
  1. The stage's output is bounded by its ISNS loop at **5.7 A**, not 5 A (SNVSAI1D VSNS 43 / 50 / 57 mV over R11's
     10 mOhm), and the charger can ask for it in service: ILIM_HIZ sits at 3.87 to 4.27 V, over the pin's 4 V range
     (O-16), and IIN_HOST goes to 6.35 A (SLUSE66A 9.3.5). Over every corner C163 carries **5.38 A** (316 percent).
  2. **The BQ25731 draws its input current from the same node in pulses.** SLUSE66A 10.2.2.4 Equation 4: ICIN =
     I x sqrt(D (1 - D)), "half of the charging current (plus system current ...) when duty cycle is 0.5", up to
     5.7 A rms (a 10 V pack, D = 0.5). With it C163 carries **8.13 A** (478 percent).
  The corner is reachable: 9 V in at 5.7 A out needs about 13 A at VIN_RAW; board E's LM5069 limits the vehicle entry
  at 4.85 to 6.15 A (VCL 48.5 / 55 / 61.5 mV over its R19, 10 mOhm), but the solar tracker ORed into VIN_RAW (LT8705A,
  15.1 V, up to about 93 W, gen_sch_e.py) supplies the rest when the panel and the vehicle are both connected. (The
  vehicle alone cannot hold that corner; that is R4A-N10 below, and it is not relied on here.)
- **The model** (`drafts/scripts/bulk_ripple.py`): each converter's switch current built from its topology (the
  FE's boost output current, IL during 1 - D; or its buck triangle; the charger's buck input current, IL during D;
  each with its triangular ripple) and split, harmonic by harmonic to the 60th, between every capacitor on a
  two-node network: VBUS20 (the bulk, the FE's ceramics and, after R4A-N8, the charger's C20 to C22) and CH_ACN (the
  half bridge's 10 nF and 1 nF) joined by R16 and its copper; the two converters are not synchronised, so each part's
  RMS is the root of the sum of squares. Its total reproduces Equation 19 (6.32 A computed against 6.30 A at 9 V and
  5.7 A) and Equation 4 (5.75 against 5.70 A). Corners: VIN_RAW 9, 10, 12, 13.8, 16, 24, 36 V; VBAT 10, 12, 12.3, 14.4,
  16.8 V; the FE's fSW 180, 206, 232 kHz; the charger at 400 kHz (PWM_FREQ at POR) or 800 kHz; bulk C x0.8 / x1.2 and
  ESR x0.3 / x1.0 / x2.0 of the sheet maximum. INFERRED, each a corner: ceramic effective capacitance 4 to 7 uF (50 V
  parts) and 4 to 6 uF (35 V), ceramic ESR 2 to 5 mOhm and ESL 0.8 to 1.5 nH each, polymer ESL 1.5 to 3.5 nH, R16's
  copper 5 to 20 nH. PASS: the worst part at or under its rated current at every corner, no uplift for a cooler case
  (the sheet gives none). The script checks its ratings against loop_design.py's single copy.
- **Options** (`drafts/box/ripple/explore1.json` and `explore2.json`, 105 combinations over the whole corner grid,
  the same model functions as the final script; the scripts differ only in their report section):
  - At the stage's 5.7 A: V101, V181 or V331, one to five of them, with none to eighteen more 10u 50V. One V331:
    337 to 374 percent; two: 168 to 244 percent; three: 123 to 184 percent; four with no more ceramics 129 percent;
    four V181 or four V101 with eighteen more ceramics 114 percent. **Four V331 with nine more ceramics: 95 percent**;
    with twelve 93, fifteen 92; five V331 with twelve: 80 percent.
  - A hardware cap on the charger's input current under the stage's minimum limit (the ILIM_HIZ pin, 4.24 A at
    most over REGN's 5.7 to 6.3 V and the pin's accuracy): three V331 with six more ceramics 92 percent, four V331
    96 percent. **Not taken**: it guarantees only about 3.1 A (61 W) at the charger's input where the stage
    guarantees 4.3 A (86 W), and plan section 10 forbids a feature reduction without an owner ruling.
  - A firmware rule lowering IIN_HOST at a low VIN_RAW: **not taken**. VIN_RAW is measured by board E's controller
    (VIN_MON), not by the host that writes the charger, and S-04 already rejected a charge limit that depends on host
    software being right.
- **Taken: four EEHZK1V331P and nine more 10u 50V.** C163 becomes EEHZK1V331P (330 uF 35 V, 20 mOhm max, 2.8 A rms,
  G 10 x 10.2, the CP_Elec_10x10 land the PA and PD bulk already use; 20 V is 57 percent of its rating) and C178 to
  C180 are three more of it, one part number as the sheet asks for parallel parts ("use capacitors with the same part
  number" so ripple does not concentrate); C181 to C189 are nine more of the stage's own 10u 50V X7R 1210 (the
  certified C596319). With C20 to C22 the node carries fifteen ceramics. **Result** (`drafts/box/loop2/ripple-final/`,
  final scripts, identical to the first run): **[CORRECTED in section 6 B3: these figures came from the endpoints of the
  INFERRED bands and the nominal switching frequencies; inside the bands this node reads 3.43 A, 122 percent, at 5.7 A
  and 3.01 A, 107 percent, at 5 A]** worst part **2.66 A rms, 95 percent of 2.8 A** (9 V in, a 10 V pack,
  the charger at 800 kHz, fSW 232 kHz, ESR x0.3, C x0.8, ESL 3.5 nH); **2.33 A (83 percent)** at the declared 5 A;
  worst ceramic 1.03 A (no MLCC ripple rating is held; INFERRED as comfortable for a 1210 part). **Residue,
  disclosed:** one part at the low-ESR corner with its three siblings at the sheet maximum would carry 4.12 A (147
  percent). The sheet's remedy is the one part number (taken) and a symmetrical layout (O-01); the ESR spread inside
  one part number is not published.
- **The loop on the new node.** loop_design.py's FE stage is re-described (fifteen local ceramics, 60 to 102 uF; no
  remote capacitance, only the 11 nF behind R16; 5.7 A; Middlebrook's bound at 114 W, 1.17 Ohm) and the search ran on
  the WIDENED band (Q 0.4 to 1.5, L 0.8 to 1.2; minor item 1). Taken: **Rc1 15 k, Cc1 220 nF, Cc2 680 pF**
  (UNI-ROYAL 0603WAF1502T5E C22809, stock 4.7 M, certified on boards B and D; C160828 as the fix-up; Samsung
  CL10C681JB8NNNC C0G C30816, the FE SLOPE capacitor's part). Read back over every corner (`drafts/box/loop2/final`,
  `final-wide`): default band PM 66.3 degrees, GM 12.2 dB, |1 + T| 0.69, crossover 1.05 to 5.4 kHz, 89 mOhm against
  1.17 Ohm; widened band PM 64.8, GM 10.5 dB, |1 + T| 0.66. The fix-up's 1.5 k / 220 nF / 2.2 nF reads PM 26 degrees
  on the new node and is replaced (R10 and C6 change value; C5 is unchanged). Three V331 would have given a better
  loop (GM 11.3 dB) and fail the ripple. Equation 9 at 5.7 A: COMP 2.05 V at 9 V in, 2.12 V at the tolerance corners,
  under 3 V. L1 carries 12.7 A average and 14.0 A peak at 9 V in, under its 17.5 A.
- **Reproducibility.** The six unchanged stages' final sets, re-read with the second fix-up's loop_design.py on the
  default band, reproduce the fix-up's figures exactly (`drafts/box/loop2/repro/`).
- **JLCPCB parts API read-backs, 26 September 2026** (`drafts/jlc/`): C278516 = Panasonic EEHZK1V331P, SMD D10 x L10.2,
  330 uF 35 V 20 mOhm, stock 6,551 (twenty needed for five boards); C596319 = YAGEO CC1210KKX7R9BB106, 10 uF 50 V X7R
  1210, stock 82,885; C22809 = UNI-ROYAL 0603WAF1502T5E, 15 k 1 %, stock 4,697,705; C160828 stock 31,432; C30816 stock
  60,807; C57112 = FH 0603B103K500NT, 10 nF 50 V X7R, stock 7.1 M; C1588 = Samsung CL10B102KB8NNNC, 1 nF 50 V X7R,
  stock 8.2 M; C14663 = YAGEO CC0603KRX7R9BB104, 100 nF 50 V, stock 51 M.
- **Every other stage's bulk is inside its rating** on the same model (the table in section 4): PA 2.15 A per
  EEHZK1E471P (77 percent), PD 1.25 A (45 percent), HF 0.55 A per EEHZK1E151XP (31 percent), S2 and SD 0.28 A (15
  percent). The re-review's estimates (PA 1.5 to 2.0 A, PD 1.1 to 1.2 A, HF 0.4 to 0.5 A each) are inside these.
  Each is judged at its stage's declared peak load (PA 6 A, PD 3 A at 15 V, HF 2 A, S2 5.8 A, SD 6.9 A), the load its
  own consumer draws in service; their ISNS limits (PA 7.2 to 9.5 A) are fault limits a consumer does not hold. The
  front end is the exception, and is judged at its limit, because its consumer (the charger) can ask for it.

### R4A-N8 (new, VERIFIED text and figures): the charger's input capacitors sat after RAC
- C20 to C22 (3 x 10u 35V) were on CH_ACN, between the input sense resistor R16 and the half bridge. SLUSE66A 10.2.2.4:
  the input capacitor "should be placed in front of RAC current sensing and as close as possible to the power stage
  half bridge MOSFETs", and "Capacitance after RAC before power stage half bridge should be limited to 10 nF + 1 nF
  ... Because too large capacitance after RAC could filter out RAC current sensing ripple information". Figure 10-1
  draws 6 x 10 uF on VBUS before RAC and Figure 10-3 the 10 nF and 1 nF at Q1's drain after it (pages 83 and 85
  rendered and read: `drafts/scratch/bq25731_p83_top.png`, `bq25731_p85_top.png`). 10.2.2.2: "The input current
  sensing through ACP/ACN is critical to recover inductor current ripple".
- Fix: C20 to C22 move to VBUS20 (with the front end's twelve 10u 50V the node has fifteen ceramics, more than
  Figure 10-1's six), and C190 (10 nF, C57112) and C191 (1 nF, C1588), the certified 0603 50 V parts, sit on CH_ACN at
  Q7's drain. CH_ACN's declaration note now names them. It moves the charger's input ripple onto VBUS20, which is why
  B3 counts it there.

### BIAS bypass on every stage (the re-review's minor item 5) (VERIFIED text)
- SNVSAI1D 9.1: "Place the BIAS bypass capacitor close to the controller IC, between the BIAS and PGND pins. A 0.1-uF
  ceramic capacitor is typically used." No stage had one, not only U5, U7 and U19. The helper now requires one:
  C192 (FE, on VBUS20), C193 and C194 (S2 and SD, VBAT), C195 (PA, +13V8_PA), C196 (HF, +12V_HF), C197 (PoE, VBAT),
  C198 (PD, VBAT), each 100n (C14663, 50 V) declared as its controller's pin 24 bypass, so the placement reserves a
  seat at the pin and DEC-001 measures it (O-01).

### Findings recorded, not fixed (outside the blocking item)
- **R4A-N9 (VERIFIED text): the charger's inductance resistor, compensation and frequency.** The BQ25731's IADPT pin
  has no resistor to ground (only TP19); SLUSE66A 9.3.11: "The charger reads both converter operation frequency and
  the inductance value through the resistance tied to IADPT pin before the converter starts up", Table 9-4: 169 k for
  the fitted 3.3 uH ("recommended for 800 kHz"), and the pin table asks a 100 pF or smaller decoupling capacitor.
  COMP1 is 10 k + 10 nF (no C12) and COMP2 1 nF alone, where Table 9-5 gives 16.9 k + 3.3 nF with 33 pF (COMP1) and 15 k
  + 1.2 nF with 15 pF (COMP2) for 3.3 uH at 800 kHz, and "It is not recommended to change the compensation network
  value". PWM_FREQ is 400 kHz at POR (Table 9-8), a frequency TI pairs with 4.7 uH. Recommended: either 3.3 uH with
  169 k, the 800 kHz row and a firmware PWM_FREQ = 0b written before the charge current is raised, or 4.7 uH with
  191 k and the 400 kHz row (host-free consistent at POR); either needs the charger inductor's saturation checked at
  the 5.7 A input and low-pack corner (about 11 A output), which is why it is not changed in this pass. The ripple
  check of B3 covers both frequencies.
- **R4A-N10 (VERIFIED arithmetic on held figures): the vehicle input cannot feed the front end's full output at a
  low voltage.** At 9 V and 5.7 A out the stage draws about 12.7 A (20 x 5.7 / 9 / 0.93); board E's LM5069 limits the
  entry at 4.85 to 6.15 A (`v2/vendor/ti/ti-lm5069.pdf`, VCL) and then times out (the -2 part restarts), and its
  SRF1260-4R7Y choke is rated 7.18 A rms in the sheet's parallel connection and 3.59 A in its series one
  (`v2/vendor/power/bourns-srf1260-common-mode-choke.pdf`); with one winding in each line both windings carry the
  line current, which heats it as the series connection does (INFERRED; gen_sch_e.py's value text says 7.2 A per
  winding, a board E question). So with the vehicle alone the kit hiccups whenever the
  charger asks for more than the entry allows at that voltage; at 12 V the stage's 5.7 A needs 10.2 A. This extends
  O-21 (the power_path short on VIN_RAW) from a declaration to a coordination defect: the fix is an input-power bound
  (the FE's ISNS on its input side, or a charger input limit that follows VIN_RAW) or a stronger entry on board E, a
  W2 and board E decision.
- **R4A-N11 (VERIFIED text, not assessed): external BIAS without the input diode.** SNVSAI1D 9.1: "When using external
  BIAS, use a diode between input rails and VIN pins to prevent reverse conduction when VIN < VCC." FE, PA and HF
  take BIAS from their own outputs (20, 13.8 and 12 V); as the input collapses at power-down, BIAS can keep VCC up
  while VIN falls under it. S2, SD, PD and PoE take BIAS from VBAT, their own input rail, and are not affected.

### The re-review's minor items
| Minor item | Disposition |
|---|---|
| 1. Loop corners hold Q at 0.4 to 0.8 and L at nominal; the helper's comment claims every corner of Q | loop_design.py gains `LOOP_WIDE=1` (Q 0.4, 0.8, 1.2, 1.5; L 0.8, 1.0, 1.2 in the RHP zero; the default band is unchanged and reproduces every fix-up figure). The six unchanged stages' margins on the widened band are stated in the helper comment, on each call and in the section 4 table: PM unchanged, GM S2/SD 9.4, PA 9.9, HF 8.2, PD 9.85, PoE 12.0 dB (the re-review's figures, reproduced, `drafts/box/loop2/wide/`). The front end was designed on the widened band: GM 10.5 dB. The claim in the helper comment is corrected. Redesigning the other six to 10 dB on the widened band is not done in this pass (O-22) |
| 2. PD's large-signal transitions (15 to 5 V, 9 to 5 V) not assessed: reverse inductor current into VBAT, and the downward slew against USB PD's 30 mV/us | Added to FW-A15 as item 8 (the transitions, the reverse current through L11 against its Isat, and the slew against SLVSDG8B 9.1.5's 30 mV/us), and recorded as O-23 with the design option (slew control per 9.1.5). Not changed on paper |
| 3. PoE COMP headroom at the tolerance corners | Recorded in R4A-N7 above and in the generator: 2.48 V nominal (the fix-up's 2.59 V corrected), 2.84 V at 10 V and 2.89 V at 9 V at the corners (`drafts/scripts/comp9_corners.py`, SNVSAI1D Equation 9 read from the page) |
| 4. F-PR-04 'DONE (paper design)' should say schematic only; R4A-N5 cannot read RESOLVED for FE until B3 | F-PR-04 now reads DONE (schematic only); R4A-N5 names B3 for the front end |
| 5. BIAS bypass for U5, U7 and U19 | Fixed for all seven stages (above), C192 to C198 |
| 6. loop_design.py docstring cites TI's Cc2 pole at seven to ten times fbw while the rule enforced is weaker | The docstring now states what is enforced (the pole at least 3 x the zero and at or under Fsw/2) and that the margins carry the pole's phase |

## 6. Round 4 third fix-up (the second re-review, 26 September 2026)

The second re-review (APPROVE_WITH_FIXES) found review A's and the first re-review's items resolved and raised two
blocking items (B3: the VBUS20 bulk result was demonstrated only at the endpoints of bands that contain a resonance;
B4: the front end's 47 nF soft start, unchanged while its output grew tenfold, overloads board E's vehicle entry) and
seven minor ones. The integration brief added a third item: reconcile board A's VIN_RAW declaration (8 / 10 A) with
board E's 6.15 A on main faf8c981. All are dispositioned below. Every choice with more than one option is **taken by
the session under the owner's standing rule of 26 Sep 2026**. Only `v2/ecad/tools/gen_sch_a.py` and `drafts/*` were
written; nothing was committed or pushed; the runner's main clone was not touched, and the box's main clone read the
same status before and after every run.

**Regeneration.** Box vast.ai 52646493, `/root/r6/a/run1` and `run2` only, from 82dd1e4d (this worktree's base):
`drafts/box/fixup3-run2/` (`drafts/scripts/r6a_box.sh run2`) with this generator (sha256 17c204ad4fb0...32734e272) is
FINAL. `fixup3-run1/` (sha256 65a115bb...0dbc10a29c) is the first regeneration: run2 differs from it only in the
schematic section lists, which now seat the fourteen new parts in their stages' blocks instead of the "OTHER PARTS"
block; the two netlists are identical by netdiff.py (0 entries; the files differ in their source-path and date
header lines), the intent files differ only in their "written" minute, and every gate reads the same except
erc_gate's warning count. Gates on the final netlist (the second fix-up in brackets): erc_gate PASS of 1431
warnings, 0 errors, the same three warning types, off-grid endpoints and unconnected wire ends up with the section
placement (run1: 1395; 1376); port_protect PASS of 21 (21); pin_map_lands PASS of 553 (539); derate PASS of 266, 0 undeclared nets, 0
under-rated (242); power_sequence PASS of 30, 0 unresolved (30); power_path PASS, 30 rails, 70 nodes (67), 0
undeclared, ONE short feed, VBAT's (two: VIN_RAW's typical is no longer short, see "VIN_RAW" below); safe_lines PASS of
6 (6); check_contracts PASS of 73 (73); energy_chain PASS of 98 with the same one board B coordination finding (98);
clock_check not applicable. netlist_board (the committed A32 board against the new netlist) FAIL 302 of 2197 (282 of
2183; 60 on the base): expected until the board is regenerated (O-01). build_sch.sh exit 0.
**Cross-check on main faf8c981** (`drafts/box/fixup3-run2/x6main/`, `drafts/scripts/r6a_x6.sh run2`; run1 has its
own): the same generator, run inside a `git archive` of faf8c981's `v2/ecad` with main's own tools, builds a netlist IDENTICAL to run2 (0
differences; the intent file differs only in its "written" minute), so the change merges onto main as it stands.
check_contracts in that tree: 31 PASS, 0 FAIL, 24 unjudged, INCONCLUSIVE only because main's own board B netlist
carries a sidecar from before 26 September ("UNKNOWN GENERATOR", board B is held on main); every A-to-E and A-to-D
contract passes, among them "dock 2x6 contact map identical on A (J_DOCK) and E (J_BLK)" and "rail VIN_RAW: the shares
sum to 2.0% within the 2.0% the rail declares". (`x6main/run.log` fails its own SHA256SUMS line because that run's script summed
run.log before its last line was written; `r6a_x6.sh` now leaves run.log out, as `r6a_box.sh` does, and every other
file verifies. `x6/` is a first attempt that copied only the netlist and intent into
main's tree; main's staleness guard refused it by the schematic's hash, which is why the second run regenerates inside
the tree. Kept as the record.)
**Full suite** (`drafts/box/fixup3-suite/` on run2, `drafts/scripts/r6a_suite_box.sh run2`; `fixup3-suite-run1/` on
run1 reads the same): 1399 passed, 4 failed, 2 skipped, the
same four integrator-owned failures (O-02 to O-05); `suite-failures.txt` is byte-identical to the second fix-up's. The
rendered PCB-BRING-UP.md differs from the second fix-up's render in one row only, VIN_RAW 8.00 A to 12.31 A. The suite
rewrote ROTATION-CHECKLIST.md as before (O-05); its diff was not captured this time (the clone was removed), but board
A's footprint set is measured unchanged, 41 lands in both regenerations, so only an example designator could differ.
**Netlist difference** against the second fix-up: 540 to 554 parts, 326 to 329 nets, 34 entries, 0 unexplained
(`drafts/scripts/classify_diff_fixup3.py`; the table is in `r4-netlist-diff.md`); against round 4: 145 entries, and
against the 82dd1e4d base: 482 entries, 0 unexplained in both (`drafts/box/fixup3-run2/classified-vs-*.md`, identical
to run1's).

### B3: the VBUS20 bulk, judged inside its bands (the second re-review's blocking item 1) (VERIFIED ratings and datasheet text; INFERRED parasitics)
- **Finding confirmed, and larger.** `bulk_ripple.fe_case` at the re-review's point (ESL 2.6 nH, ceramic 4.0 uF,
  C x1.2, 5.7 A, 9 V, 232 kHz, a 10 V pack, the charger at 800 kHz) gives 2.968 A, the re-review's 2.97 A. Two
  switching frequencies were held at their nominal values as well: SLUSE66A 8.5, "PWM switching frequency",
  Reg0x01[1] = 0: 680 / 800 / 920 kHz, = 1: 340 / 400 / 460 kHz; and the LM5176's 180 to 232 kHz. With every band
  sampled the second fix-up's node reads **3.43 A rms, 122 percent** (ESL 3.5 nH, ceramic 4.0 uF, the charger at
  680 kHz, VIN 9 V, VBAT 10 V; 4,450 of 110,700 passive sets over 2.8 A), 3.01 A (107 percent) at 5 A, and 3.31 A
  (118 percent) at a 2:1 ESR spread. The endpoint-only figure of that run is the same 3.43 A: what the second fix-up
  missed at its endpoints was the charger's frequency band, and what it missed at 800 kHz was the interior of the ESL
  band.
- **The model** (`drafts/scripts/ripple_dense.py`): bulk_ripple.py's physics (each converter's switch current from its
  topology, 60 harmonics, split between every part, root sum of squares for the two unsynchronised sources), with
  one more node, FE_OUT, for ceramics before R11 (R11 plus its copper, L11 INFERRED 1 to 5 nH). Bands: polymer ESL
  1.5 to 3.5 nH in 0.05 nH steps (41), ceramic effective C 4 to 7 uF in 0.125 uF steps (25), ceramic ESL 0.8 / 1.15
  / 1.5 nH, ceramic ESR 2 and 5 mOhm, L16 5 and 20 nH, bulk C x0.8 / 1.0 / 1.2, bulk ESR x0.3 / 1.0 / 2.0; VIN_RAW
  9 to 36 V (7), fsw 11 points over 180 to 232 kHz, VBAT 10 to 16.8 V (10), fch 7 points over each charger band. The
  maximum over the product of corners is exact without enumerating it: the FE's share depends on (VIN, fsw), the
  charger's on (VBAT, fch), so each passive set's worst mean square is the sum of the two maxima. **Self-check**:
  where the networks are the same it reproduces `bulk_ripple.fe_case` at 40 random points to a relative 8.7e-16
  (`drafts/box/fixup3/ripple/selfcheck.json`), and it is run before anything is reported.
- **Options** (`drafts/box/fixup3/ripple/`): a SCREEN of 120 options (4, 5, 6, 7, 8 or 10 cans; 6 to 30 ceramics;
  0, 3 or 6 of them on FE_OUT) at 5.7 A with the damping bands at their least-damping corner (`grid/summary.txt`),
  then eight options on the full bands at 5.7 A and 5 A and at ESR spreads 1.0, 1.5 and 2.0 (one can at the corner's
  ESR, its siblings at s times it; `short/`, `summary-table.md`). Worst can at 5.7 A, matched / 1.5:1 / 2:1:

  | Node | 5.7 A | 5 A |
  |---|---|---|
  | 4 cans, 15 ceramics on VBUS20 (the second fix-up) | 122 / 112 / 118 % | 107 / 98 / 104 % |
  | 5 cans, 21 + 3 on FE_OUT | 81 / 88 / 100 % | 71 / 77 / 87 % |
  | 5 cans, 24 + 3 | 81 / 87 / 99 % | 72 / 77 / 87 % |
  | 5 cans, 27 + 3 | 81 / 87 / 98 % | 71 / 76 / 86 % |
  | 6 cans, 15 + 3 | 80 / 78 / 88 % | 70 / 69 / 77 % |
  | **6 cans, 18 + 3 (taken)** | **75 / 75 / 87 %** | **66 / 66 / 76 %** |
  | 6 cans, 21 + 3 | 71 / 75 / 86 % | 63 / 66 / 76 % |
  | 7 cans, 15 + 3 | 73 / 70 / 77 % | 64 / 62 / 68 % |

  The screen's other rows (`grid/summary.txt`): moving three of the same total to FE_OUT lowers the worst can in 39 of
  the 42 like-for-like pairs (the three exceptions are within 6 points: six ceramics in all with eight or ten cans, and
  thirty with six cans), and four cans reach 90 percent at best (24 on VBUS20 and 6 on FE_OUT).
- **Taken: SIX EEHZK1V331P** (C163, C178 to C180, C199, C200; one part number, as the sheet asks for parallel parts),
  **the stage's own C13 to C15 moved to FE_OUT** before the ISNS shunt (R4A-N14 below), and **eighteen ceramics on
  VBUS20** (C181 to C189, C201 to C206 and the charger's C20 to C22, all 10u 50V X7R 1210, C596319). Worst can over
  the whole bands: **2.10 A rms, 75 percent of 2.8 A** at 5.7 A (ESL 3.5 nH, ceramic 4.0 uF, VIN 9 V, fsw 196 kHz,
  VBAT 10 V, the charger at 800 kHz: the FE's share 1.38 A, the charger's 1.58 A); 2.11 A (75 percent) at a 1.5:1
  spread; **2.43 A (87 percent) at a 2:1 spread** (ESL 1.8 nH, the charger at 340 kHz); at the declared 5 A 1.85 /
  1.86 / 2.14 A (66 / 66 / 76 percent). 0 of 332,100 passive sets exceed 2.8 A in any of these six runs. The
  endpoint-only worst of the matched run is within 0.003 A of the dense worst, which the dense sweep is what shows.
  Worst ceramic: 1.09 A on VBUS20 and 1.55 A on FE_OUT (no MLCC ripple rating held; about 12 mW a part at the band's
  5 mOhm, INFERRED; O-30). **Residue, disclosed:** one can at the low-ESR corner with its five siblings at the sheet's
  maximum ESR (a 3.3:1 spread) reads 3.24 A, 116 percent (86,256 of 332,100 passive sets over;
  `extreme/b6_a18_o3_i5.7_s3.33.json`; the second fix-up's node read 4.16 A, 149 percent, on the same model): the
  sheet's remedy, one part number and a symmetrical layout (O-01), and the bench share reading (FW-A15 item 9, O-26).
- **Rejected:** five cans (98 to 100 percent at a 2:1 spread); seven (10 more points at a 2:1 spread for one more
  can, and a 2.97 mF node for the soft start); four cans with more ceramics (90 percent at best); a hardware cap on
  the charger's input (a feature reduction, plan section 10, as in section 5).
- **The loop on the new node** (`drafts/box/fixup3/loop/`, `drafts/scripts/r6a_loop_box.sh`): the FE stage run at six
  V331 and 21 ceramics (loop_variant / loop_verify, the band scaled from fifteen to 21 parts; the three FE_OUT parts
  sit behind 10 mOhm, nothing beside their reactance at the loop's frequencies, so they count with the local bank). The
  second fix-up's set, **Rc1 15 k, Cc1 220 nF, Cc2 680 pF, is kept**: default band PM 73.1 degrees, GM 15.7 dB,
  |1 + T| 0.79, crossover 0.71 to 3.6 kHz, 89 mOhm against 1.17 Ohm; widened band (Q 0.4 to 1.5, L 0.8 to 1.2) PM
  72.9, GM 14.0 dB, |1 + T| 0.76. The search's own pick for the node, 22 k / 220 nF / 470 pF, crosses faster (1.0 to
  5.3 kHz) with less margin (widened GM 10.8 dB); the helper's old single set reads PM -55 degrees on the widened band.
  No compensation part changes. Equation 9 is unchanged (COMP 2.05 V at 9 V in).
- **Every other stage's bulk figure stands**: the re-review re-ran PA, PD, HF, S2 and SD inside their bands and read
  2.15, 1.25, 0.55 and 0.28 A, unchanged.

### B4: the front end's soft start (the second re-review's blocking item 2) (VERIFIED datasheet figures; INFERRED BIAS draw)
- **Finding confirmed.** SNVSAI1D Equation 3 and FB following SS during the ramp make the output slew
  (1 + 240k/10k) x ISS / CSS; ISS 3.75 / 5 / 6.35 uA (6.5). With 47 nF on the new node (2.61 mF at its largest: six
  cans at +20 percent, 21 ceramics unbiased at +10 percent) the worst stack (ISS maximum, CSS at -23.5 percent for
  X7R's tolerance and temperature, the divider at its 1 percent corner) charges 11.7 A, 29 A at 9 V in; the
  re-review's 3.8 A nominal and 6.8 A at 12 V are the nominal side of the same arithmetic on the smaller node. Board E's
  LM5069 (R19 10 mOhm, VCL 48.5 / 55 / 61.5 mV, ti-lm5069.pdf) limits the vehicle entry at 4.85 to 6.15 A, 4.80 A
  with R19's 1 percent, and the front end is a constant-power load: when U6 limits, VIN_RAW collapses to the FE's UVLO
  (62k / 10k, about 8.6 V) and the stage restarts. The limit must not be reached.
- **The load at start.** VBUS20's only load besides the stage's own BIAS is the charger. SLUSE66A 9.3.1: its converter
  powers up after VBUS qualification, and CHRG_OK "is HIGH after 50-ms deglitch time" once VBUS passes 3.5 V (a
  typical; no minimum is given), so on a ramp of a few hundred milliseconds the charger may be converting before the
  ramp ends and is counted as present at the end of it, drawing up to IIN_DPM: with a host, what the host wrote
  (FW-A16 below holds it at 80 percent of the entry); host-free, the POR limit, IIN_HOST 3.2 A at the RSNS_RAC = 1b
  scale (+200 mA maximum, 9.6.22) against this board's 10 mOhm R16, 1.72 A.
- **Taken: C7 = 3.3 uF** (CCTC TCC0805X7R335K250FT, C7393948, 25 V X7R 0805, stock 169,678, certified on board A; the
  helper takes a per-stage soft-start capacitor now). `drafts/scripts/softstart.py`, `drafts/box/fixup3/softstart-6-21.*`,
  every worst corner stacked (VBUS20 20.7 V, efficiency 0.93, BIAS 0.05 A INFERRED): ramp 0.31 / 0.53 / 0.91 s; the
  stage's own draw at the end of the ramp, and the totals with each load at start, as a share of the entry's 4.80 A:

  | VIN_RAW | 9 V | 10 V | 12 V | 13.8 V | 16 V | 24 V | 36 V |
  |---|---|---|---|---|---|---|---|
  | ramp and BIAS alone | 11.2 % | 10.1 % | 8.4 % | 7.3 % | 6.3 % | 4.2 % | 2.8 % |
  | with the charger at FW-A16's 80 % | 91.2 % | 90.1 % | 88.4 % | 87.3 % | 86.3 % | 84.2 % | 82.8 % |
  | with the charger host-free at POR (1.72 A) | 99.6 % | 89.6 % | 74.7 % | 64.9 % | 56.0 % | 37.3 % | 24.9 % |

  3.3 uF is the smallest E6 value that keeps every case under the entry at every VIN_RAW: 2.2 uF reads 103.9 percent
  host-free at 9 V, and 4.7 uF buys 2.6 points there (97.0 percent) for a 43 percent longer constant-current response.
  With the host contract the margin is about 9 percent or more at every voltage; host-free at 9 V it is 0.4 percent,
  and that figure is the charger's own POR limit (88.6 percent of the entry by itself), which is the steady state of
  R4A-N10 and not something a soft start can move.
- **The cost, stated as the re-review asked.** The average-current loop acts by discharging CSS from its 1.21 V clamp
  (VSS(CL)) down to VREF with its 1 mS gm (7.3.4, 7.3.6; the pin table calls it "a slow constant current (CC) control
  loop"). With 3.3 uF it acts after 176 ms at 10 mV over VSNS, 352 ms at 5 mV and 70 ms at 25 mV, and 235 ms at the
  charger's largest request (IIN_HOST 6.35 A + 0.1 A over a 57 mV unit), where 47 nF acted after 1 to 5 ms. Meanwhile
  the charger's own IIN_DPM bounds the current (at 6.45 A and 9 V in, L1 carries 14.8 A average and 16.2 A peak, under
  its 17.5 A; the vehicle entry could not supply it at 9 V anyway) and the cycle-by-cycle limit bounds a fault. A 13
  percent excursion of the bulk's ripple for a quarter of a second is inside a thermal rating. Recorded as O-31, bench
  item FW-A15 (10).
- **The other six stages keep 47 nF.** They start from VBAT, where no entry limits them. softstart.py's worst stack at
  VBAT 10 V: S2 0.57 A, SD 0.51 A, PA 5.85 A, HF 1.72 A, PoE 2.16 A and PD 0.78 A from VBAT, each for at most 13 ms
  (11.6 A if all six started in the same instant), inside the pack path's 25 A blade and the gauge's 20 A for 2 s and
  30 A for 20 ms (pcb_pack_protection.yaml).
- **Host contract (new, FW-A16)** and bench (FW-A15 item 10) in `r4-hwfw-contract.md`.

### VIN_RAW reconciled with board E (the integration brief's item; board E's F-IN-02 on main faf8c981) (VERIFIED declarations; INFERRED current split)
- Board E declares its VIN_RAW at 6.15 A typical and peak (U6's VCL max over R19: "what the path must CARRY
  CONTINUOUSLY"), and its comment hands this board's 8 / 10 A and the IIN_HOST rule to the board A author. **But the
  dock carries more than the vehicle entry**: E ORs its panel tracker's output (TRK_OUT, 6.16 A typical and peak, 93 W
  over 15.1 V) onto VIN_RAW through the ideal diode U4 / Q2 behind the hot-swap, so A's J_DOCK receives both sources,
  up to 12.31 A, and A's front end can draw it (5.7 A at 20.7 V needs 12.3 A at 10.3 V).
- **Taken: VIN_RAW 12.31 A typical and peak on board A** (board E's two declared figures summed, on E's own basis: the
  most the path carries continuously with no limiter acting; loads Q2 11.31, C11 0.5, C12 0.5 as before). It tightens
  the rail against 8 / 10 A; the A32 copper was laid for 8 A and is regenerated anyway (O-01). The shares are
  unchanged (A 1.5, E 0.5 of 2 percent) and check_contracts passes them on main's tree. power_path now reads the feed
  as 12.31 A against the front end's 10.75 A typical (no longer short) and 14.34 A peak, the latter from VBUS20's
  declared 8 A peak, above the stage's 5.7 A ISNS maximum and left as the conservative figure for VBUS20's copper
  (O-21). The rendered PCB-BRING-UP.md row changes to 12.31 A.
- **R4A-N12 (new, board E, recorded):** E's VIN_RAW is declared from L2 alone, but its copper from Q2's drain to J_BLK
  carries the tracker's current as well; and with the bus pulled under 15.1 V the tracker's output is bounded by the
  panel's power (93 W at 10.3 V is 9.0 A), not by 6.16 A. O-28, I-14.
- **R4A-N13 (new, recorded):** at 12.31 A each of the four Preci-Dip 813 VIN_RAW contacts carries 3.08 A of its
  "OPERATING CURRENT Max. 3.5 A" (v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf) if they share
  evenly: 88 percent, and spring contacts do not share evenly. O-29.

### R4A-N11 (resolved on paper): the VIN pin's blocking diode (the second re-review's minor item 3)
- SNVSAI1D 7.3.2: "use a series blocking diode between the input supply and the VIN pin (Figure 7-1). This prevents
  VCC from back-feeding into VIN through the body diode of the VCC regulator"; 9.1: "When using external BIAS, use a
  diode between input rails and VIN pins to prevent reverse conduction when VIN < VCC". The front end's BIAS source,
  VBUS20, now holds 2.6 mF: with the charger idle it holds BIAS above the 8 V switchover for up to about a second after
  the vehicle is removed (INFERRED: 2.6 mF against the controller's tens of milliamps), and VCC (7.6 V) back-feeds
  VIN_RAW through that body diode; at about 6.9 V the EN/UVLO divider's 0.96 V then sits at the top of VEN(STBY)'s
  0.55 to 0.97 V, so the regulator can hold itself on (INFERRED). Fixed on the three stages whose BIAS is their own output: D19, D20, D21
  (BAT46W-7-F, the bootstrap diodes' part, 100 V, 150 mA; C83152) feed pin 2 of U2, U13 and U15 through FE_VINP,
  PA_VINP and HF_VINP, each with its pin's own capacitor (C207 1 uF 100 V X7R 1210, PSA FS32X105K101EFG, C382212, for
  VIN_RAW's 64.5 V clamp; C208 and C209 1 uF 50 V X5R 0603, C15849, on VBAT), declared as pin 2's bypass; VISNS (pin 3)
  stays on the power stage's input rail. The pin sits a diode drop (about 0.5 V at the controller's bias current,
  INFERRED) below the rail, above VIN's 4.2 V recommended minimum at every input (8.5 V at a 9 V vehicle). The helper now refuses a stage whose BIAS is not its input
  rail without the diode, and declares each VINP node at the rail's service maximum (derate judges C207 against 36 V).
  In the intent file the pin-2 bypass declarations move from the power stages' input capacitors C11, C63 and C74 to
  C207, C208 and C209 (55 declarations before and after); C12, C64 and C108 still serve VISNS (pin 3).

### R4A-N14 (new, VERIFIED text): no output capacitance before the ISNS shunt (the second re-review's minor item 1)
- SNVSAI1D 9.1: "When using the average current loop, divide the overall capacitor (CIN or COUT) between the two sides
  of the sense resistor to ensure small cycle-by-cycle ripple"; Figure 10-1 draws COUT on both sides of RISNS. Every
  <p>_OUT net carried the shunt alone, so each ISNS shunt sat in its stage's boost hot loop with its ESL and fed the
  ISNS filter the pulsed current. **Front end: fixed** in B3 (C13 to C15 on FE_OUT, which also lowers the bulk's worst
  current in 39 of the 42 like-for-like screen pairs). **The other six stages: O-27**, recommended, each with its loop re-read.

### The second re-review's minor items
| Minor item | Disposition |
|---|---|
| 1. <p>_OUT has no capacitor on any of the seven stages (SNVSAI1D 9.1); consider with B3 | R4A-N14: the front end fixed with B3 (C13 to C15 on FE_OUT); the other six recorded as O-27 |
| 2. R4A-N9 / O-24: IADPT open, and at 800 kHz C121 can be left open (SLUSE66A 10.2.2.2) | O-24 amended to name C121 in the 800 kHz option; not changed on paper (pre-existing, disclosed) |
| 3. R4A-N11 / O-25 matters more with 1.1 to 1.7 mF on the BIAS source | Resolved on paper: D19 to D21 and C207 to C209 (above); O-25 closed |
| 4. SLUSE66A Table 12-1 asks 0402 for the post-RAC 10 nF + 1 nF; C190, C191 are 0603 | Acceptable, noted in O-01 with their seat at Q7's drain |
| 5. C20 to C22 read '10u 35V 1210' while lcsc_fill.py buys C596319, a 50 V part | Fixed: their value text is now '10u 50V X7R 1210' (the same certified code); the ripple model's ceramic band is one band |
| 6. O-26's sentence rests on the endpoint result | Rewritten on the dense result; the old sentence is withdrawn |
| 7. The imbalance residue at realistic spreads (1.2 to 2.0) | On the new node: 75 percent at 1.5:1 and 87 percent at 2:1; the 3.3:1 extreme is 116 percent, disclosed in B3 and O-26 |

### Commit text proposed for the integrator
Subject: `fix(board-a): VBUS20 bulk sized on the dense bands, front-end soft start for the vehicle entry, VIN_RAW reconciled with board E [MESHSAT-1357]`
Body: the second re-review's two blocking items: six EEHZK1V331P on VBUS20 with C13 to C15 moved before the ISNS shunt
(SNVSAI1D 9.1) and eighteen ceramics on VBUS20, worst can 2.10 A of 2.8 A (75 percent) and 87 percent at a 2:1 ESR
spread, over the whole INFERRED bands and both switching-frequency bands (drafts/scripts/ripple_dense.py), where the
second fix-up's 95 percent was an endpoint figure (122 percent inside the bands); the front end's soft start 3.3 uF,
so its ramp draws 11 percent of board E's vehicle entry at 9 V; VIN_RAW declared 12.31 A, board E's vehicle entry plus
its panel tracker; series VIN blocking diodes on the three stages with external BIAS (SNVSAI1D 7.3.2); C20 to C22's
value text names the 50 V part bought. Taken by the session under the owner's standing rule of 26 Sep 2026. Paper
design, not built or tested; the bench readings are FW-A15 items 9 and 10, and the host's side is FW-A16.

## 7. Round 4 fourth fix-up (the third re-review, 26 September 2026)

The third re-review (APPROVE_WITH_FIXES) confirmed B3 and B4 on its own independent model and raised one blocking item:
the front end restarting into its own charged VBUS20 had not been assessed. It also raised five minor items. All are
dispositioned below. Every choice with more than one option is **taken by the session under the owner's standing rule
of 26 Sep 2026**. Only `v2/ecad/tools/gen_sch_a.py` and `drafts/*` were written. Nothing was committed or pushed, the
runner's main clone was not touched, and the box's main clone read the same status before and after every run.

**Regeneration.** Box vast.ai 52646493, `/root/r6/a/run3` to `run7` and `/root/r6/a/restart` only, from 82dd1e4d (this
worktree's base), `drafts/scripts/r7a_box.sh`. `drafts/box/fixup4-run3/` (run7, generator sha256 a0452054...455a83c, the
file in this worktree) is FINAL. The earlier runs:
- `fixup4-run1/` (run5, generator 097d2eae...02bdd1c) is the first complete regeneration. It fed U2's EN from FE_RUN
  through 4.7 k alone with 10 nF. The session's own check of the guard below U34's power-on-reset level found that with
  U34's outputs undetermined, EN then followed FE_VZ, and FE_VZ follows VIN_RAW under the zener's knee. So run7 adds R206
  (100 k, EN to ground), raises R199 to 47 k and lowers C213 to 2.2 nF: 3 netlist entries against run5 (R206 added,
  R199 and C213 re-valued), each an R4A-N15 item.
- run6 changed two comment lines only (netlist identical to run5's by netdiff.py) and was superseded by run7; its copy
  was not kept.
The generator's difference against the third fix-up is `fixup4-run3/generator-vs-fixup3.diff`.
Gates on the final netlist (the third fix-up in brackets):
- erc_gate PASS of 1450 warnings, 0 errors, the same three warning types (1431);
- port_protect PASS of 21 (21);
- pin_map_lands PASS of 575 (553);
- derate PASS of 268, 0 undeclared nets, 0 under-rated (266);
- power_sequence PASS of 30, 0 unresolved (30);
- power_path PASS, 30 rails, 80 nodes (70), 0 undeclared, one short feed, VBAT's (one);
- safe_lines PASS of 6 (6); check_contracts PASS of 73 (73); energy_chain PASS of 98 with the same one board B
  coordination finding (98); clock_check not applicable.
- netlist_board (the committed A32 board against the new netlist) FAIL 327 of 2219 (302 of 2197; 60 on the base):
  expected until the board is regenerated (O-01).

The first attempt at the zener (run3) read derate FAIL of 2: D22's value said "12 V", and derate.py read that as a
voltage rating against the 12.7 V the clamp itself makes. The value now names no volts (the circularity derate.py
already removed for TVS parts; open item O-35). run4 is void: a comment swallowed C214's call, the generation failed,
and the script went on to judge the committed schematic. r7a_box.sh now stops when the generation fails.
**Cross-check on main faf8c981** (`fixup4-run3/x6main/`; run5's has its own): the same generator run inside a `git archive` of faf8c981's
`v2/ecad` with main's own tools builds a netlist identical to run7's (0 differences). check_contracts there reads 31
PASS, 0 FAIL, 24 unjudged, INCONCLUSIVE in the tool's words because "B [is] absent from this tree, so nothing that names
them was judged" (missing_boards 1): the same 31 / 0 / 24 as the third fix-up's cross-check. Every A-to-E contract passes there: the dock's 2x6 map on J_DOCK and
J_BLK, J_DOCK pin 8 SHORE_INHIBIT, the four CELL+ and four return pins, and "rail VIN_RAW: the shares sum to 2.0% within the 2.0%".
power_path there passes with the same one short feed.
**Full suite** (`drafts/box/fixup4-suite/` on run7's artefacts, the final generator's, `drafts/scripts/r7a_suite_box.sh run7`; a first run on run5's artefacts read the same): 1399 passed, 4 failed, 2 skipped, the same four integrator-owned failures (O-02 to O-05); `suite-failures.txt` is byte-identical to the third fix-up's, and the rendered PCB-BRING-UP.md difference is the third fix-up's line for line. The suite rewrote ROTATION-CHECKLIST.md as before (O-05; its diff was not captured, the clone is removed); board A's land set gains exactly one land, U34's WSON-10-1EP_2.5x2.5mm (42 lands against 41, measured on the two netlists), so the re-render gains that row.
**Netlist difference** against the third fix-up: 554 to 576 parts, 329 to 341 nets, 46 entries, 0 unexplained
(`drafts/scripts/classify_diff_fixup4.py`; the table is in `r4-netlist-diff.md`). Against round 4 there are 186 entries
and against the 82dd1e4d base 523, 0 unexplained in both.

### R4A-N15: the front end's restart into a charged VBUS20 (the third re-review's blocking item) (VERIFIED datasheet text; INFERRED controller behaviour at the COMP floor)

**What the sheet says** (SNVSAI1D, read on the page):
- 7.3.8: "In CCM operation, the inductor current can flow in either direction".
- 7.3.13: COMP spans 0.3 to 3 V. Equations 7 and 9 place the current command on a 1.6 V offset. In CCM buck at no
  load, "the maximum VIN for which the converter can regulate the output at no load is when VCOMP reaches 0.3 V".
  COMP below 1.6 V therefore commands a negative current. At the floor that is (1.6 - 0.3) / (ACS 5 x RSENSE 5 mOhm)
  = **-52 A**.
- 6.5: the error amplifier sinks 280 uA. Across Rc1's 15 k that is 4.2 V, more than COMP's whole range, so COMP reaches
  its floor within microseconds of a large FB error.
- 7.3.5 limits only the forward valley (buck) and forward peak (boost). No negative limit is named.
- 7.3.4: SS is discharged on EN/UVLO below threshold, VCC UV, hiccup and thermal shutdown. The sheet describes no
  pre-biased start.
- 7.3.11: OVP stops the gate drives without discharging SS, so OVP gives no restart.
- MODE (R119 to VCC): hiccup is disabled on this stage.

**Why VBUS20 stays charged.** Once the stage stops, the charger stops at its VINDPM (18.5 V, FW-A16 (c)). The 250 k
divider is then the only load, so the bank holds 18.5 to 20.7 V on 1.67 to 2.61 mF for minutes.

**Case 1: a dip that discharges SS** (every crank under the old 62k / 10k UVLO, every reconnection, every LM5069 retry).
`drafts/scripts/restart.py` (`drafts/box/fixup4/restart/`, run on the box) integrates the stage at its COMP floor.
It covers 48 corners: VBUS20 18.5 and 20.7 V; bank 1.67 and 2.61 mF; VIN_RAW 20 and 32 uF; L1 8 and 12 uH; restart at
the old UVLO's 8.24 V, at 12 V and at 28 V. The SMCJ40A is modelled from the Vishay row: VBR 49.1 V, rd 0.66 Ohm,
64.5 V at 23.3 A. Board E's ideal diodes block every reverse ampere. Results:
- VIN_RAW peaks at **57.8 to 60.1 V**. U2's absolute maximum on VIN, EN/UVLO, VISNS, ISNS and SW1 is 60 V (its
  recommended VIN maximum 55 V); the worst corners pass it for up to 25 us, from 77 to 102 us after the restart.
- L1 is driven to **-52 A** against its 17.5 A Isat. Saturation is not modelled, and it would only make the current rise
  faster.
- The clamp absorbs **0.23 to 0.53 J at every event**.
- At the peak, board E's LM74700 cathode sits 51 V above a 9 V vehicle (75 V rated), and E's VIN_MON reads 5.5 V at
  its ADC.
Not bounded.

**Case 2: a dip that leaves SS partly discharged.** If SS is still above FB, the stage resumes forward. Its recovery
of a sagged bank then runs at the cycle-by-cycle limit, board E limits, and VIN_RAW collapses. If SS is below FB,
forced CCM pulls the bank down to the lower target and returns C x V x dV. VIN_RAW's room from the restart level to 36 V
is 5 to 20 mJ, which is used up by a pull-down of 0.1 to 0.36 V: an SS shortfall of only **3.8 to 14.6 mV** under FB
(restart.py). The sheet gives no SS discharge rate, so no dip length is safe. Not bounded.

**The fix taken: the reviewer's second example.** A supervisor holds U2's enable low from any VIN_RAW undervoltage until
VBUS20 has been bled under 0.8 V, so every start is from an empty bank. The generator comment at U34 holds the full
design. In short:
- **U34** is a TPS37A010122DSKR (TI SNVSBJ1E, fetched from ti.com, `drafts/datasheets/ti-tps37.pdf`; LCSC C3685740,
  stock 738). VDD runs 2.7 to 65 V (70 V absolute), taken straight from VIN_RAW through R196 1 k and C210. The SENSE and
  RESET pins are 65 V graded and independent of VDD. Both channels are at 0.800 V (0.792 to 0.808) with 2 percent
  hysteresis, and both outputs are open drain, active low. Below VDD's UVLO both outputs are asserted.
- **Channel 2 (UV) is now the stage's UVLO.** R14 and R15 (the old pair, re-valued 91k over 10k) set it at 7.86 / 8.08 /
  8.31 V falling and 8.01 / 8.24 / 8.48 V rising, under the 9 V service floor. As drawn, the old divider's rising
  threshold reached 9.23 V at its tolerance corner (restart.py), so the stage might not have started at a 9 V vehicle;
  that is gone too. C212 (100 nF on CTR2) holds the release for 79 / 127 / 201 ms as a debounce (SNVSBJ1E Eq. 1 to 3).
- **Channel 1 is the latch.** SENSE1 reads VBUS20 through R197 (100 k). Q36 grounds it while FE_RUN is high, so while
  the stage runs, channel 1 cannot assert. When FE_RUN falls, channel 1 holds it low until VBUS20 is under 0.766 / 0.784
  / 0.792 V, whatever channel 2 does. Its state is the bank itself, so it is rebuilt at every power-up of U34.
- **FE_RUN** (both RESET pins) is pulled to FE_VZ by R198 (100 k). FE_VZ is VIN_RAW through R200 (33 k), clamped by D22
  (BZT52C12-7-F, Diodes DS18004, `drafts/datasheets/diodes-bzt52c.pdf`). At the lowest UV fall it sits at 6.0 V while
  held (Q38's gate) and 5.4 V while running; it carries 0.63 mA in the zener at 36 V and puts 85 mW in R200 at 64.5 V.
- **U2's EN/UVLO** takes 0.68 of FE_RUN over R199 (47 k) and R206 (100 k), with C213 (2.2 nF) at the pin
  (restart.py, `guard()`):
  - While held, EN sits at 0.44 V at most: U34's 0.3 V VOL plus the pin's own 7 uA into 32 k. That is under VEN(STBY)'s
    0.55 V, so U2 is in shutdown.
  - EN needs at least 44.5 us to fall through VEN(OP), and channel 1 latches within 18 us of FE_RUN falling (tCTS open,
    17 us). So a supervisor glitch shorter than the latch cannot disable U2, and a longer one leaves it held.
  - Below U34's VPOR (1.4 V) its outputs are undetermined. With RESET floating, EN reaches VEN(OP)'s 1.17 V minimum only
    at VIN_RAW 3.28 V, above U34's own 2.7 V UVLO, where both outputs are asserted.
  - Running at the lowest UV fall: FE_VZ 5.4 V, FE_RUN 3.2 V (Q36 and Q37 need at most 2.5 V), EN 2.2 V.
- **The bleed.** While FE_RUN is low, Q37 releases FE_BLEED_G. R201 lifts it to FE_VZ, and Q38 (CSD19532Q5B, VGS(th)
  3.2 V at most, SLPS414B) puts R202 to R205 across VBUS20: four 510 Ohm 1 W 2512 parts (UNI-ROYAL 25121WJ0511T4E, LCSC
  C36171), 121 to 134 Ohm together.
  - Power: 1.00 W per part at 22 V with the resistor 5 percent low. That is inside the continuous rating, so no pulse
    rating is needed.
  - Energy: 0.63 J per event at most, 0.16 J per part.
  - Time: tau 0.20 to 0.35 s, and 0.64 to 1.17 s to the release level.
  - While VIN_RAW is absent nothing is bled, and nothing needs to be, because U2 cannot start.

**What is left.**
- A start from at most 0.792 V is the bank ringing into L1 through the buck low side. The peak is 0.792 x sqrt(2.61 mF
  / 8 uH) = **14.3 A**, under Isat 17.5 A, and the energy is 0.82 mJ. If every joule came back, VIN_RAW would reach
  12.1 V from the release level, or 37.1 V from 36 V.
- U2's thermal shutdown also discharges SS and is not guarded. The controller's own loss is its gate drive, so reaching
  165 C needs a board far outside the envelope. This is recorded, not fixed.

**Cost.** 21 new parts (one new IC) and the old UVLO pair re-valued. A restart now waits for the bleed and the soft
start: a dip under 8 V interrupts charging for about 1 to 2.5 s.

**Rejected:**
- **A pre-biased start.** SS would have to reach FB in the microseconds COMP takes to reach its floor, which cannot be
  done with a 4.7 uF CSS. A source strong enough would also override the CC loop and the chip's own fault discharge.
- **A reverse-blocking element between the stage and the bank.** An ideal-diode controller regulates its forward drop
  (20 mV on the LM74700-Q1). At light load that puts 20 mV / I inside the voltage loop, 0.4 Ohm at the 50 mA BIAS load,
  and B3's loop design would no longer hold. A Schottky instead costs 2.6 W at 5.7 A in a sealed case.
- **More VIN_RAW capacitance.** With a larger C, the LC transfer from the bank peaks higher, not lower (restart.py
  reasoning: I = dV x sqrt(C / L)).

The bench readings owed are FW-A15 item 10: the restart with a charged bank, the hold and bleed times, VIN_RAW's peak
and any LM5069 event.

### R4A-N16 (new, INFERRED, recorded): an ordinary charger load release returns energy into VIN_RAW
The mechanism is the same as R4A-N15, without any restart. When the charger's input current stops abruptly (HiZ through
CHG_INHIBIT, a host write, a fault, or the kit's own load falling while the charger is at IIN_DPM), VBUS20 overshoots.
Forced CCM then pulls the overshoot back through the stage and returns about C x V x dV into VIN_RAW, whose sources
block. The third fix-up's loop reads a closed-loop output impedance of up to 89 mOhm on this node. A 5.7 A release is
therefore dV = 0.51 V and 27 mJ back:
- from 12 V: 43 to 54 V;
- from 24 to 36 V: at the clamp.
A 3 A release returns 14 mJ: 32 to 40 V from 12 V (restart.py).

It is bounded, not harmless:
- The SMCJ40A clamps at a few amperes at about 45 to 52 V (VBR 44.4 to 49.1 V plus 0.66 Ohm), under U2's 60 V.
- Board E's OVLO (40 V) then turns E's path off, VIN_RAW falls to the guard's UV, and the guard holds and restarts the
  stage. So it becomes a charging interruption, not damage.
- E's VIN_MON over-range at its ADC is E's item.

Options (O-32):
- a VIN_RAW OV hold on the stage (a second TPS37's OV channel at about 38 V);
- more VIN_RAW capacitance on A (about 85 uF in all, some 55 to 65 uF more, keeps a 28 V line under 38 V after a 5.7 A
  release);
- a faster FE loop at the corner that gives 89 mOhm.
Each has to be weighed with E's inrush and the loop. The 89 mOhm is the loop model's (INFERRED), and the bench reading
is FW-A15 item 11.

### The third re-review's minor items

| Minor item | Disposition |
|---|---|
| 1. B3's worst case sits at the edge of every INFERRED band; the loop inductance and the cans' ESL are layout and part requirements | O-01 now states them as conditions of B3's 75 / 87 percent: the loop from FE_OUT through R11 to the VBUS20 bank at or under 5 nH (L11) and the cans' mounted ESL at or under 3.5 nH, placed symmetrically. The reviewer's sensitivity (10 nH 97 percent, 15 nH 105 percent matched) is quoted there. FW-A15 item 9 now reads both back on the bare board |
| 2. FW-A16 (d) holds IIN_HOST at the vehicle's figure when only the panel feeds, a D-01 charge-power reduction | FW-A16 (d) now states the consequence: 2.61 A at the tracker's 15.1 V, about 54 W at the charger's input against TRK_OUT's 93 W, and vehicle plus panel capped at the vehicle's figure. It is recorded as the reduction it is until board E routes TRK_IMONO (R17, 10 k to GND, gen_sch_e.py:483) or PV_P's level to the sensor controller. That is O-33, a board E item |
| 3. U2's 60 V pins against the SMCJ40A's 64.5 V clamp; SNVSAI1D 7.3.7's 2 k in series with VISNS above 40 V | **VISNS fixed:** R195 (2 k, C22975) in series with U2 pin 3, no capacitor at the pin (Figure 8-1, page 21 rendered). The lm5176 helper takes `visns_r`, and C12 is no longer declared as pin 3's bypass. **The clamp:** O-34 records it with the option that fits: SMCJ36A (VWM 36 V, VBR 40.0 to 44.2 V, VC 58.1 V at 25.8 A, Vishay row), whose clamp is under 60 V. The swap moves surge current from E's clamps to A's through the dock contacts, so it is a coordination item with board E, not a one-board change. R4A-N15's guard removes the stage's own route to the clamp |
| 4. B4's host-free 99.6 percent at 9 V rests on CSS at 0.765; X7R aging takes it lower | **C7 is 4.7 uF** (YAGEO CC0805KKX7R8BB475, C354262, the 0805 4.7u lcsc_fill already maps). softstart.py with `--kmin 0.70`: 3.3 uF reads 100.4 percent host-free at 9 V and 4.7 uF 97.6 (97.0 at 0.765). Ramp 0.41 / 0.75 / 1.29 s. The CC loop now acts after 251 ms at 10 mV and 335 ms at the charger's largest request (O-31). Below 9 V, inside the guard's enable window, the host-free charger alone passes the entry (109 percent at 8.0 V). That is R4A-N10's steady state, and the guard turns it into a hold and restart, not damage |
| 5. power_path marks SHORT only on VBAT | Noted for the integrator in O-21, no action: VIN_RAW's peak shortfall (14.34 A drawn against 12.31 A declared) is the conservative VBUS20 8 A peak |
| 6. Verified, no action | Recorded |

### I-14's back-feed sentence, corrected
The sentence "VBUS20 no longer back-feeds VIN_RAW" rested on D19, which blocks only the VCC regulator's body-diode path
(SNVSAI1D 7.3.2). The power stage itself is bidirectional (7.3.8). It returned the bank into VIN_RAW on a restart (R4A-N15,
now prevented by the guard) and still returns overshoot energy after a charger load release (R4A-N16, open). I-14 now says
this.

### Commit text proposed for the integrator
Subject: `fix(board-a): front-end restart guard holds the stage until VBUS20 is bled, VISNS behind 2 k, soft start 4.7 uF [MESHSAT-1357]`
Body:
- The third re-review's blocking item. U2 restarting with its soft start discharged into VBUS20's 2.6 mF commanded -52 A
  at its COMP floor (SNVSAI1D 7.3.8, 7.3.13, Eq. 7). With board E's ideal diodes blocking, that drove VIN_RAW to U2's
  60 V absolute maximum at every crank (drafts/scripts/restart.py).
- A TPS37A010122 (U34) now owns U2's enable, through a divider that keeps U2 off until U34 is valid. Its UV channel on VIN_RAW (8.08 V) is the stage's UVLO, and its second
  channel latches the stage off until VBUS20 is under 0.8 V. Q38 and four 510 Ohm 1 W resistors bleed the bank in 0.6
  to 1.2 s.
- VISNS behind 2 k (SNVSAI1D 7.3.7).
- C7 4.7 uF, so the host-free start holds under board E's entry with X7R aging.
- Taken by the session under the owner's standing rule of 26 Sep 2026. Paper design, not built or tested. The bench
  readings are FW-A15 items 9 to 11.
