# Board P (pack BMS), Review D round 4 with its fix-up: the choices taken and the netlist they produce

MESHSAT-1357, 26 September 2026. Worktree `fnd/r4p` at main 82dd1e4d, nothing committed or pushed. This is a prototype design:
no board of this set has been built, and nothing here has been measured on hardware.

Files changed against 82dd1e4d:
- `v2/ecad/tools/gen_sch_p.py`, `v2/ecad/tools/gen_pcb_p.py`, `v2/ecad/tools/gen_pcb_p3.py`
- two new lands in `v2/ecad/meshsat.pretty/`, each carrying its land review note in its own description:
  `Texas_RSM0032A_VQFN-32-1EP_4x4mm_P0.4mm_EP1.4x1.4mm.kicad_mod` (TI drawing 4219107/A) and
  `Eaton_SCF9550_9.5x5.0mm.kicad_mod` (Eaton ELX1135 page 3). Both are written by `drafts/scripts/make_fp.py`.

The first round-4 pass (author report of 01:59) was reviewed APPROVE_WITH_FIXES with three blocking findings. A first fix-up
died on an infrastructure error after editing the generators; the fix-up of 09:08 to 09:45 verified its edits against the primary
documents, finished them, and re-ran the box. Its re-review (APPROVE_WITH_FIXES) confirmed all three blocking findings resolved and
raised one new blocking item and seven minor ones; the second fix-up (09:57 to 10:20) resolves them, section 0b. Where a choice
remained, the session took the option the evidence recommends; each is marked **taken by the session under the owner's standing rule
of 26 September 2026**. Primary documents: URL, revision and sha256 in `drafts/datasheets/SOURCES.txt`. Box results:
`drafts/box/fixup2/` (the second fix-up, the current state), `drafts/box/fixup/` (the first fix-up), `drafts/box/final/` (the first pass).

## 0. The review's findings and what the fix-up did

| Finding | Resolution | Evidence |
|---|---|---|
| **B1 (blocking).** The BQ77207's 70 C over-temperature drives COUT, which fires F2; TEST-PLAN E3 (+71 C storage, +55 C operation) and D-02a (survive and recover) collide with it. | U2's TS pin is held by a fixed 10 kohm to VSS (R33). The second level has no temperature function; J_TS2 and its NTC are gone. Over-temperature stays with the gauge's four NTCs and the PTC. RP-17, RP-18. | SLUSEG7D 7.1, 7.3.3, Table 7-1, 6.5 (OT and UT tables), section 4 (no UT column); netlist: U2.12 on TS_SEC with R33 to GND. |
| **B2 (blocking).** D1 lost its certified code; R23, R29, R31 had no code path. | Codes now in the generator: D1 C364296 (both the `tvs()` and the fallback call), R23 C23025, R29 C4184, R31 C23196, each read back from JLC's API. `lcsc_fill.py` on the new BOM: PASS, 34 rows, 4 blank, all 4 allow-listed (the 12 AWG lands). Full blank list in O-3. | `drafts/box/fixup/new/v/lcsc_fill.log`, `new/files/pcb-p-pack-jlc-bom.filled.csv`. |
| **B3 (blocking).** F2 (Dexerials SFK-1830A) had no maker land, no stated temperature range, and its land was outside the library. | F2 is now an **Eaton SCF9550-30-05** (same heater and fuse figures), whose data sheet states -20 to +60 C operating and gives a recommended pad layout. The land is in `v2/ecad/meshsat.pretty/`, drawn pad for pad from ELX1135 page 3 and read back with pcbnew on the box. Hand-fit route: Digi-Key (907 in stock). RP-04, RP-16. | `drafts/datasheets/eaton-scf9550-elx1135.pdf` (sha256 3ecc2424...); `drafts/box/fixup/landcheck.txt`. |
| m1. RP-07 arithmetic left out R32. | R32 is 1 Mohm. Gauge alone: 3.78 V at the gate; COUT alone: 4.25 V at 88 uA (inside the 100 uA where VOH is at least 6 V). RP-07. | gen_sch_p.py fuse-drive comment. |
| m2. Q5 differs from TI's Figure 8-1 (Q2's source is PACK_P). | Recorded, not clamped: under a UV hold VGS(Q2) = -V(PACK_P), 3.2 V margin at 16.8 V; a charger fault above 20 V would exceed Q2's gate rating. RP-02. | gen_sch_p.py Q5 comment. |
| m3. RVD and RIN 20 to 25 mm from U2 (SLUSEG7D 8.4.1). | U2 and all its RC filters (R23..R27, C14..C18) and R33 share region SEC. Q3 is fixed under F2, out of the packer, so the pairs sit in the rows directly below U2, VDD first: 5.1 to 16.0 mm from U2's centre. Pin-adjacent placement belongs to the 4-layer regeneration (O-11). RP-20. | `drafts/box/fixup/new/place/place_report.txt`, `placement.png`. |
| m4. O-10 asked Safety UV to fire FUSE, against RP-02's own reasoning. | O-10 corrected: Safety UV is not a fuse event (the heater is rated only from 10.5 V). | section 5. |
| m5. S-09 evidence cited TRN-001, which judged 0 ports. | The fix is proven by the netlist (D1.1, the cathode, on PACK_P); TRN-001 is not cited as evidence. | netlist_diff.txt. |
| m6. S-05 "removes the parallel ground path" overstated. | Corrected: both returns are on the load side of the shunt, so counting is right; the lead's ground still carries about 4 % of the return (about 0.7 A at 18 A). A harness item for O-5. | gen_sch_p.py J_SMB comment. |
| m7. TI Figure 30 has 200 ohm plus 100 ohm around the SMBus clamp. | Recorded deviation: one 100 ohm, pin side; kept for rise time; ESD level is a test item (TEST-PLAN M7). RP-09. | gen_sch_p.py SMBus comment. |
| m8. RSM0032A corner pads 0.18 mm apart diagonally. | Stated in the land's description; pcbnew read-back gives 0.183 mm at 1/32, 8/9, 16/17, 24/25 (TI's own example geometry). | landcheck.txt. |
| m9. PRF15BE103 rated -20 to +110 C; E4 stores at -33 C. | PRF15BE103 is obsolete (Digi-Key) and JLC holds none; PRF15BB103 (-20 to +140 C, JLC 5,388) replaces it. E4's -33 C is still below Murata's -20 C cold test: O-15. RP-12. | SOURCES.txt distributor readings. |
| m10. Second distributor for the BQ7720700 and the PTC. | Digi-Key: BQ7720700DSSR 2,588 at 2.12 USD (1.567 at 10); PRF15BB103RB6RC 20 at 0.17 USD. | SOURCES.txt. |
| m11. D-06 docstring dropped "subject to the case measurement". | Restored in the docstring; its gloss corrected at the second fix-up (D-08 reversed, section 0b R-m1). | gen_sch_p.py docstring. |
| m12. Stale C10 comment. | Removed. | gen_sch_p.py decoupling comment. |
| m13. No test point on FUSE_GQ. | TP14 on FUSE_GQ; JP1's closure is verified by continuity TP11 to TP14, **with the meter's COM (black) lead on TP14** (second fix-up, section 0b R-B1). | netlist; gen_sch_p.py JP1 comment. |
| m14. Two layers; check_pcb_p 4 failures. | Unchanged, owners named: O-11 and O-1. | section 5. |
| O-12 (the first pass's own observation). C11 and C12 in parallel across the terminals. | In series through PACK_MID, as TI asks (SLUSC67B 8.2.2.1.5). PACK_MID declared as a node at 16.8 V so CMP-001 still judges both. RP-22. | netlist: C11.2 and C12.1 on PACK_MID; derate judged 6, 0 undeclared. |
| Fix-up run 1 DRC: a ground stitch via 0.10 mm from F2's heater pad (PWR clearance 0.30). | The stitch grid now keeps every pad's outline 0.75 mm away, not only its centre 1.6 mm. Final DRC: 0 clearance, courtyard, short or mask-bridge items. RP-21. | `drafts/box/fixup/new/place/drc_summary.txt`. |

## 0b. The re-review's findings and what the second fix-up did (26 September 2026, 09:57 to 10:20)

The re-review confirmed B1, B2 and B3 resolved, reproduced the netlist and its provenance, and raised the items below. No netlist
change was needed for any of them: the second fix-up's netlist has the same content hash as the first fix-up's (9bf3a3a46b5d95a6,
PARITY_AFTER_NOISE, `drafts/box/fixup2/netlist_compare_vs_fixup1.json`); only comments, the TPS2 list order and the provenance
hash of the generator changed.

| Finding | Resolution | Evidence |
|---|---|---|
| **R-B1 (blocking).** The JP1 closure check that m13 added (continuity TP11 to TP14, cells on, no polarity) can fire F2 in the very fault it looks for, a closure that did not wet: about 98.6 % of the meter's open-circuit voltage lands across R32 (1 Mohm), which is Q3's gate, so a red lead on TP14 puts +2 to +3.3 V on a gate whose VGS(th) is 0.65 to 1.45 V. And TPS2 put TP13 (SCP_OUT, 10 to 16.8 V) 2.25 mm from TP14. | **1. The check has a polarity:** continuity (or resistance) TP11 to TP14 with the meter's COM (black) lead on TP14 and the red lead on TP11, after the meter's source polarity and open-circuit voltage are confirmed on the range used (a second meter across its leads in DC volts; an analogue ohmmeter reverses the polarity), that voltage under the gate's +-12 V. Closed reads about 0 ohm; open reads about 1 Mohm with Q3's gate held negative. Of the reviewer's two options this one is **taken by the session under the owner's standing rule of 26 September 2026**: the other, TP14 to TP8 (PACK_N) with COM on TP14, drives FUSE_G negative when JP1 IS closed and through R30 and R29 risks the BQ4050's FUSE pin and the BQ77207's COUT below their -0.3 V absolute minimum (SLUSC67B 6.1, SLUSEG7D 6.1); the check taken drives only JP1's FET side negative, and only in the open state. **2. TPS2 order TP14, TP11, TP12, TP13, west to east** (the reviewer's example was TP11, TP14, TP12, TP13), **taken by the session under the same rule**: TP14 is Q3's gate directly, so it takes the end, with TP11 as its only test-point neighbour (a bridge there is a closure, harmless once TP11 has been read low). In the reviewer's example TP14 sits beside TP12 (SEC_DOUT, about 6 V under an under-voltage or open wire), a bridge that fires F2 with JP1 open; here TP12 neighbours TP11, which reaches the gate only through a closed JP1. TP13 takes the east end beside TP12 only (at most 16.8 V on DOUT, rated 45 V, and on Q5's +-20 V gate: DSG held off, recoverable). Measured on the placed board: TP14's nearest exposed pad outside the row R10.1 (GND) 1.72 mm; TP13's W_N (PACK_N) 2.83 mm, where the third position gives 2.41 mm to R10.2, so the cell node is not brought closer to ground; the stitch vias nearer the ends (0.73 mm from TP13, 0.93 mm from TP14) are tented. RP-06, RP-15, O-9. | gen_sch_p.py JP1 and test-point comments; gen_pcb_p3.py TPS2; `drafts/box/fixup2/new/place/place_report.txt`, `tps2_neighbours.txt`, `placement.png`; AOS AO3400A Rev 3.1 (VGS +-12 V, VGS(th) 0.65 to 1.45 V). |
| **R-m1** (m11 gone stale; a citation). The D-06 gloss named D-08's measurement, which the owner reversed at about 09:30; the -20 C floor was cited to "owner condition 1", which in the plan's section 9b is the H753/H743 substitution rule. | The docstring keeps the ruling's words, "subject to the case measurement", and says what they mean now: the measurement request is withdrawn, every case-dependent margin is held against the worst of Peli's own figures for the current 1450 moulding (1451-931 drawing of 2025-01-15, the STEP, the web page; D-08a), and sealing and stack-up are verified on the prototype build with a new case. The -20 C floor is cited to D-02a's -20 to +40 C use envelope (RT1 and F2 comments, RP-04, O-8). Also corrected: RP-07's numbers comment cited "owner condition 2" (the runtime rule); it now cites the review minor it answers. | gen_sch_p.py docstring and comments; memory project_owner_rulings_2026_09_25.md (D-08 REVERSED, D-08a, D-02a). |
| **R-m2.** "Heater loop about 2 mm" measures only SCP_HTR; the return from Q3's source is left to the router with one 0.6/0.3 mm ground-class via, and the board has no top-side ground pour. | The claim now names the segment it measures: SCP_HTR, F2 pin 3 to Q3 pin 3, **1.05 mm pad edge to pad edge** (measured). The return, Q3.2 (GND, F.Cu) to the B.Cu ground and W_BN, goes into the route brief (O-11, O-14): **at least five 0.3 mm or four 0.4 mm barrels at Q3's source**, the tree's own `via_current.barrels_for(3.5 A)` at 10 K and 18 um plating (a steady-state figure, so conservative for the 60 s pulse; 0.74 A per 0.3 mm barrel). Today's nearest stitch via is 3.77 mm from Q3.2. RP-20. | gen_pcb_p3.py Q3 comment; `tps2_neighbours.txt` (heater segment, Q3.2 vias). |
| **R-m3.** C19, the gate's RFI capacitor, sits in EAST at the far end of a board-crossing FUSE_GQ held only by 1 Mohm while JP1 is open. | Recorded, not moved in this pass: listing JP1 and C19 in SEC would sort JP1 (larger than an 0603) straight after U2 and push U2's RC pairs away again (undoing m3), and there is no free site beside Q3 without redrawing GAUGE and SEC. They move beside Q3 when the regions are next redrawn, at the 4-layer regeneration (O-11). SLUSC67B 8.2.2.2.5 lets C3 go because the fuse is slow, so there is no function risk meanwhile. | gen_pcb_p3.py EAST comment; O-11. |
| **R-m4.** O-1 checks only the FUSED bands; the power path gained a band. | O-1 also asks check_pcb_p.py for the locked band of SCP_OUT on F.Cu and B.Cu. | O-1. |
| **R-m5.** O-8 counted only the air (40 + 10 = 50 C against 60 C). | F2's own dissipation at the 18 A peak is 0.32 to 0.81 W (1.0 to 2.5 mohm, ELX1135), on top of the air, and ELX1135 has no current derating at all, even inside the use envelope: low risk at 60 % of rating, judged, not proven. | gen_sch_p.py F2 comment; RP-04; O-8. |
| **R-m6.** F2 breaks 80 A; the 4S3P block's prospective fault is several hundred amperes. | 240 to 480 A at this node (pcb_energy_chain.yaml, PACK_CELLS). F2 is not meant to clear it: the gauge's short circuit in discharge opens the FETs after its programmed delay (SLUSC67B 6.32: 0 to 915 us, or 1850 us with SCDDx2, plus 160 us detection at most), inside F1's 4.3 to 17 ms melting time; if the FETs failed closed, F1 (1000 A interrupting) must open before F2's element. ELX1135 gives no melting I2t for F2, so that order is not proven: O-13 and the D-09 battery-and-protection packet. | gen_sch_p.py F2 comment; O-13. |
| **R-m7.** Q5's off-state leakage loads the gauge's DSG charge pump. | IDSS 80 nA maximum at 25 C and 60 V (JCET 2N7002, J Sep 2016), no figure above 25 C; SLUSC67B 6.18 specifies the DSG drive only into 10 Mohm. Bench item: DSG_G with DSG on at E3's +55 C operating phase (O-9). | gen_sch_p.py Q5 comment; `drafts/datasheets/lcsc-C8545.pdf`. |

## 1. The round-4 items (first pass), as they stand after the fix-up

| Item | State |
|---|---|
| S-09 / A03: D1 reversed | DONE. SMBJ20A (unidirectional) with its cathode (pin 1, pad 1) on PACK_P, drawn with Device:D_Zener, code C364296 in the generator. |
| W6-F2: wrong U1 land | DONE. U1 on TI's RSM0032A land (4 x 4 mm, 0.4 mm pitch, EP 1.4 x 1.4 printed 1.3 x 1.3; drawing 4219107/A). |
| F-BP-01: USBLC6-2 on VCC_F | DONE. One PESD5V0S1BA per SMBus line to PACK_N; R20 and R21 stay. |
| F-PK-02: one thermistor | DONE. Four 103AT-2 NTCs on TS1..TS4 through J_TS (JST-PH 1x5, C157993). |
| D-15 / decision 40 | DONE for the design: BQ7720700 second level (OV 4.325 V, UV 2.25 V, open wire; no temperature function), Eaton SCF9550-30-05 chemical fuse fired by COUT and the gauge's FUSE through JP1, UV holding the discharge FET off, PTC input enabled with a PRF15BB103. Open for others: the yaml (O-4), the order route (O-3), the bench (O-9), the golden image (O-10). |
| S-05: J_SMB pin 3 | DONE. Pin 3 on PACK_N; PRES through R22 (1k). Pinout 1 SMBC, 2 SMBD, 3 GND, 4 PRES. |
| D-06: 4S3P | DONE in text, with the ruling's words "subject to the case measurement" and what they mean since D-08 was reversed (margins against Peli's own worst figures for the current moulding, D-08a). pack_4s.py not touched. |

## 2. Choices taken by the session under the owner's standing rule of 26 September 2026

**RP-01. The second-level protector: TI BQ7720700DSSR (C3681715).** Unchanged from the first pass. It covers under-voltage in
hardware for about 0.5 to 0.8 USD more than an OV-only BQ7718 at a comparable threshold (JLC 2.12 against 1.30 to 1.59 USD), which is
"near the OV-only part's cost" (D-15). Stock: JLC 3 against 5 boards; Digi-Key 2,588 at 2.12 USD (1.567 at 10). Set aside: BQ7718 and
BQ2947 (OV only), BQ77216 (3.97 USD, none in stock), ABLIC S-8254A (none in stock, a primary protector), Renesas ISL9420x (primary).

**RP-02. The second level's UV output holds the discharge FET off (Q5 pulls DSG_G to VSS); it does not fire the fuse.** UV is
recoverable, charging continues through Q2's body diode, and the SCF9550-30-05 heater is rated only from 10.5 V (2.63 V per cell).
Recorded departure from SLUSEG7D Figure 8-1 (fix-up): TI pulls down a DSG FET whose source is on the cell side; Q2's source is PACK_P,
so during a UV hold VGS(Q2) = -V(PACK_P), set by whatever drives the terminal. Margin 3.2 V at 16.8 V against the CSD17570Q5B's
+-20 V; a charger fault above 20 V during a UV hold exceeds it, and D1 (VBR 22.2 V minimum) does not prevent it. No gate-source clamp
is added, because it would load the gauge's DSG charge pump with an unspecified leakage. Bench item O-9.

**RP-03. UV threshold 2.25 V +-50 mV accepted as a backstop behind the gauge's 2.50 V.** Up to 100 mV below the Samsung guideline's
2.30 V, above the 2.00 V BMS shut-down. The 4.275 V OV variants (00701, 00702, 00704, 00705) can trip at 4.225 V, below the gauge's
4.25 V trip, and would blow the fuse on a normal charge. Route to 2.35 V: a custom BQ77207xy ("contact TI").

**RP-04 (REVISED AT THE FIX-UP). The chemical fuse: Eaton Bussmann SCF9550-30-05 (LCSC C3670061), replacing the Dexerials SFK-1830A.**
- Same electrical figures: 4 to 5 cells, 30 A, heater 4.8 to 8.0 ohm, heater operating voltage 10.5 to 23.5 V, fuse 1.0 to 2.5 mohm,
  80 A breaking, rated voltage 62 V (ELX1135 page 2).
- What decides it: Eaton STATES "Operating temperature: -20 C to +60 C" (page 4), which meets the -20 C floor of D-02a's -20 to +40 C use envelope as a
  rating; Dexerials states no range. Eaton publishes a recommended pad layout (page 3); Dexerials does not. cURus E19180.
- Opening: 100 % of rating 1 h minimum, 200 % 60 s maximum, the heater at its operating voltage 60 s maximum.
- Reliability runs: +105 C 1000 h, -40 C 500 h, 85 C / 85 % RH 500 h.
- The session's reading of the line "Storage temperature: -10 C to +40 C < 90% RH, Storage duration: 1 year": the shelf condition of
  the reeled part before assembly (a one-year duration fits nothing else), not a limit on the mounted part, whose endurance the
  reliability runs bracket (E3's +71 C and E4's -33 C storage).
- Residual: at E3's +55 C operating margin the part sits at about 65 to 71 C, above its 60 C operating rating, carrying at most 18 A
  (60 % of 30 A); Eaton gives no temperature derating curve. O-8.
- Residual inside the envelope too (second fix-up, R-m5): the 50 C of the ruled rise is the air; at the 18 A peak the part adds
  0.32 to 0.81 W of its own (1.0 to 2.5 mohm), and ELX1135 publishes no current derating at any temperature. Low risk at 60 % of
  rating, judged, not proven. O-8.
- Breaking capacity 80 A (the SFK-1830A's figure too) against a prospective fault of 240 to 480 A (pcb_energy_chain.yaml,
  PACK_CELLS): F2 must not be the part that clears a hard short. The gauge's short circuit in discharge and F1 (1000 A interrupting)
  are; F2's melting I2t is not published, so the order is not proven (R-m6, O-13, the D-09 packet).
- Order: JLC C3670061 stock 0 (1.09 USD); Digi-Key 283-SCF9550-30-05CT-ND active, 907 in stock, 5.82 USD. Hand-fit, O-3.
- Set aside: Dexerials SFK-1830A (no range, no land, not at JLC), SFK-1445A (heater from 13 V), Littelfuse ITV4030 (15 A, -10 C),
  Prosemi DHC45 (two-terminal).

**RP-05. The chemical fuse sits between F1 and Q1's source (TI Figure 21).** Its heater is fed from the cells whatever the FETs do.
New net SCP_OUT.

**RP-06. JP1, the arming jumper, is open as built and closed at commissioning** (after the cells are on, TP11 has been read low, and
the golden image is written and read back: the data-flash verification D-15 names). TI's EVM ships the fuse unfitted and warns the
second level "could blow the fuse" at cell connection (SLUUBF9 2.5.2; SLUSEG7D 8.1.2.1). R32 (1 Mohm since the fix-up) holds Q3's gate
low while it is open. JP1 is copper, left out of the BOM (in_bom False).
The closure is verified by continuity TP11 to TP14 **with the meter's COM (black) lead on TP14** and the red lead on TP11, after the
meter's source polarity and open-circuit voltage (under 12 V) are confirmed on the range used (second fix-up, R-B1): in the fault the
check looks for, a closure that did not wet, nearly all of that voltage lands on Q3's gate, and this polarity makes it negative.

**RP-07 (NUMBERS CORRECTED AT THE FIX-UP). The fuse-drive divider:** 20 kohm from COUT (R29), 5.1 kohm from FUSE (R30), into 51 kohm
(R31) and 0.1 uF (C19); R32 1 Mohm on the FET side of JP1. With JP1 closed, R31 || R32 = 48.5 kohm:
- the gauge alone (COUT inactive, sinking, so R29 is 20 kohm to ground): 6 V x 14.2 / (3.2 + 5.1 + 14.2) = 3.78 V at the gate;
- the protector alone (the FUSE pin an input with 150 to 330 nA of pull-up): 6 V x 48.5 / 68.5 = 4.25 V at 88 uA, inside the
  100 uA at which COUT's VOH of at least 6 V is specified; the FUSE pin reads it as a second-level trip (VIH 2.5 V maximum).
Both are above the AO3400A's 1.45 V maximum threshold. The first pass's R32 of 100 kohm pulled COUT to about 112 uA.

**RP-08. The fuse FET: AO3400A (C20917).** 30 V, VGS +-12 V, VGS(th) 0.65 to 1.45 V, RDS(on) under 48 mohm at 2.5 V. Heater current
1.3 to 3.5 A for at most 60 s: about 0.5 W, RthJA 90 C/W (t under 10 s) to 125 C/W steady (AOS Rev 3.1).

**RP-09. SMBus clamps: PESD5V0S1BA (C19224), one per line to PACK_N.** 45 pF maximum against the MM3Z5V6's 200 pF (about 0.9 us
against 2.5 us of rise with E's 4.7 kohm; SMBus tR 1 us maximum). Recorded deviation from TI Figure 30: one 100 ohm (R20, R21) between
the pin and the clamp, none to the connector, and a clamp higher than TI's 5.6 V zener; the pins carry integrated high-voltage ESD
protection (SLUSC67B 8.2.2.2.4). ESD level: a test item.

**RP-10. PRES series resistor R22, 1 kohm** (SLUSC67B Figure 29).

**RP-11 (REVISED AT THE FIX-UP). Thermistors: four gauge NTCs on one JST-PH 1x5 socket (common return).** The second level's own NTC
and its socket J_TS2 are removed with its temperature function (RP-17).

**RP-12 (REVISED AT THE FIX-UP). The PTC element: Murata PRF15BB103RB6RC (C443668).** 10 kohm +-50 % at 25 C, 100 kohm not before
110 C, 4.7 Mohm at 130 +-3 C, operating -20 to +140 C (Murata DM-SA16-E056 page 4). The gauge trips at 1.2 to 3.95 Mohm, so the trip
lies between about 110 and 133 C at the element: a guaranteed trip for a failing FET (CSD17570Q5B junction limit 150 C), nowhere near
E3's +71 C. The first pick, PRF15BE103RB6RC (4.7 Mohm at 100 C), is obsolete (Digi-Key: "obsolete and no longer manufactured",
PRF15BB103RB6RC named as its substitute) and JLC holds none. Only the 10 kohm types meet TI's "10-kOhm typical" (SLUUAV7C 4.5); of
those, BB103 is the one stocked. Stock: JLC 5,388 (0.126 USD), Digi-Key 20 (0.17 USD).

**RP-13. U2's exposed pad (13) tied to VSS**, as TI ties the BQ2947's in SLUSC67B Figure 21.

**RP-14. The node after the chemical fuse is named SCP_OUT** (a 4- or 6-character name on Q1's source pins put the symbol off grid; O-6).

**RP-15 (UPDATED AT THE FIX-UP). Placement: sites, regions, net classes** (reserved-list classes: "region definitions in the packer",
"net class widths and clearances").
- Sites: F2 at (-3.9, 16.05) rotated 90 degrees (bounding-box centre; pads 1 (-5.95, 16.58) FUSED, 2 (-1.85, 16.58) SCP_OUT, heater
  3 (-3.90, 11.70)); Q1 (5.3, 15), Q2 (13.3, 15), J_TS (26.8, -12.7); RT1 (9.3, 11.0), C13 (12.0, 11.0); Q3 (-2.3, 7.9) rotated 90
  degrees and R32 (1.6, 8.3), fixed at the fix-up (RP-20). J_TS2 is gone.
- Regions (board frame, mm), all without overflow on the final run:

| Region | Before (82dd1e4d) | After | Holds |
|---|---|---|---|
| GAUGE | (-23, -10, 4, 12) | (-24.2, -10.9, -4.55, 10.8) | U1, C1..C9, R1..R9 |
| SIG | (4, -10, 22, 12) | (4.35, -13.6, 19.8, 10.0) | R14..R21, R28, C11, C12, D1..D3, Q5 |
| TPS | (-33, -12, -25, 8.5) | unchanged | TP1..TP10 |
| SEC | none | (-4.35, -21.3, 4.15, 5.7) | U2, C14..C18, R23..R27, R33 |
| EAST | none | (20.0, -9.6, 26.9, 9.7) | R22, R29, R30, R31, C19, JP1 |
| TPS2 | none | (-21.9, -21.3, -4.55, -17.2) | TP14, TP11, TP12, TP13, west to east (second fix-up, R-B1) |

- SCP_OUT (10 A) and SCP_HTR (the heater's switched lead, 1.3 to 3.5 A for up to 60 s) are in the PWR class (0.5 mm, 0.3 mm
  clearance).
- TPS2's order is a safety choice (second fix-up, R-B1), **taken by the session under the owner's standing rule of 26 September
  2026**: TP14 (Q3's gate) at the west end with only TP11 beside it, TP12 between TP11 and TP13, TP13 at the east end. The packer
  lays equal sizes in list order at a 3.75 mm pitch (2.26 mm pad gap). Placed: TP14 (-20.03, -19.08), TP11 (-16.28, -19.08),
  TP12 (-12.53, -19.08), TP13 (-8.78, -19.08).
- Cost: check_pcb_p.py's literals for U1's land and the Q1, Q2 and J_TS sites fail (O-1).

**RP-16 (REVISED AT THE FIX-UP). The F2 land is Eaton's own recommended pad layout, in the project library.**
`meshsat.pretty/Eaton_SCF9550_9.5x5.0mm`: pads 1 and 2 are 7.40 x 1.40 at y -+2.05 (inner edges 1.35 from the centre, 2.70 apart);
pad 3 is 3.00 tall at x -5.95, 0.75 straight, then a 1.40 taper to a 0.70 tip at x -3.80 (0.10 outboard of the long pads' ends).
Pins from page 1. Read back with pcbnew on the box: every extent as drawn; smallest copper gap heater to fuse pad 0.836 mm; courtyard
-6.20..5.15 by -+3.00. The Dexerials draft (drafts/footprints) is withdrawn and deleted; `make_fp.py` keeps its function as the record.

**RP-17 (NEW, B1). U2's TS pin is held by a fixed 10 kohm to VSS (R33); the second level has no temperature function.**
- Options: (a) TS open, which the pin table allows ("If not used, leave it NC"); (b) a custom BQ77207xy with a higher or disabled OT;
  (c) keep 70 C and have TEST-PLAN run E3 with JP1 open; (d) a fixed resistor that reads as neither fault.
- Taken: (d). The data sheet lists an under-temperature protection (6.5: TUT -30 to 0 C; RUT_EXT_NTC 26.7, 42.2, 68.9 and 111.1 kohm)
  that drives both outputs (7.1), and its variant table has no UT column, so whether the 00700 carries it is not stated. An open NTC
  input reads as infinite resistance, above every UT threshold: with UT enabled, (a) would hold COUT active from power-up and fire the
  fuse the moment JP1 closes. 10 kohm (the 103AT at 25 C) is 4.6 times the 00700's OT resistance (2195 ohm), 3.5 times the highest of
  any option (2850 ohm) and 2.7 times below the lowest UT resistance (26.7 kohm), so it reads as neither fault whatever the silicon
  carries. (b) is not orderable; (c) keeps a permanent fuse opening in a qualification test the kit must recover from (D-02a).
- Cost: a TS-to-VSS short (a bridge at R33, or pin 12 to the exposed pad) reads as over-temperature and fires the fuse once armed;
  the commissioning order (TP11 read low before JP1 is closed, O-9) finds it. TI's advice against a capacitor on TS is kept.

**RP-18 (NEW, B1's second half). Open wire and the oscillator health check still fire the fuse, on purpose.** Table 7-1 drives COUT on
both. An open tap blinds the second level on that cell and a failed oscillator blinds it everywhere, so a permanent opening is the
conservative answer; the only variants with open wire disabled (00705, 00706) fail RP-03. A tap must stay open for tOW_DELAY, 4 s
(6.6), and bounce shorter than that resets the timer (7.3.2). For TEST-PLAN E1 and E2: a J_CELL lead that backs out and stays out
opens F2; the functional check after the test finds it, and tap-harness retention is a pack-build item (O-9, O-16).

**RP-19 (NEW, B2). Every code the MAP cannot supply is in the generator, read back from JLC's API on 26 September 2026:** D1 C364296
(MDD SMBJ20A, DO-214AA, stock 165,282), R23 C23025 (300 ohm 1 %, basic, 1,671,357), R29 C4184 (20 kohm 1 %, basic, 8,361,114), R31
C23196 (51 kohm 1 %, basic, 3,074,745). R33 "10k" and R32 "1M" are MAP rules (C25804, C22935).

**RP-20 (NEW, m3). U2's RC filters beside U2.** SEC holds U2, R23..R27, C14..C18 and R33, listed in the order the pairs should sit
(VDD, V4, V3, V2, V1, TS; the packer keeps list order among equal sizes). Q3 and R32 are fixed directly under F2: Q3's drain pad is
1.05 mm below the heater pad (measured pad edge to pad edge on the second fix-up's board), so SCP_HTR, the heater loop's switched
segment from F2 pin 3 to Q3's drain, shrinks from about 10 mm to about 1 mm (the first fix-up called that segment the loop and said
2 mm; R-m2). The rest of the loop, Q3's source to the B.Cu ground and W_BN, is the router's: at least five 0.3 mm or four 0.4 mm
barrels at Q3's source (via_current.barrels_for at 3.5 A, 10 K), route brief O-11 and O-14. Q3 no longer sits between U2 and its
filters. Measured: pair rows 5.1, 7.8, 10.6, 13.3 and 16.0 mm from U2's centre (EAST put them 20 to 25 mm away). The fuse divider
(R29..R31, C19, JP1) moves to EAST by J_SMB: SLUSC67B 8.2.2.2.5 sets no layout rule for it beyond keeping C19 "for RFI immunity".
That leaves C19 at the far end of FUSE_GQ from Q3's gate; JP1 and C19 move beside Q3 at the next region redraw (R-m3, O-11).

**RP-21 (NEW). The ground stitch grid keeps every pad's outline 0.75 mm away** (via radius 0.3 + PWR clearance 0.3 + 0.15), as well
as its centre 1.6 mm. The centre rule let a via stand 0.10 mm from the SCF9550's 3.0 x 2.15 mm heater pad. 52 stitch vias (56 before).

**RP-22 (NEW, O-12). C11 and C12 in series through PACK_MID** (SLUSC67B 8.2.2.1.5: "The two devices in series ensure continued
operation of the pack if one of the capacitors becomes shorted"). Same parts and codes; 50 nF across the terminals. PACK_MID is
declared as an intent node at 16.8 V (the whole pack across one capacitor when its partner has shorted), so CMP-001 judges both.

## 3. The netlist difference (new against the 82dd1e4d baseline in /root/r4/p), every difference with its finding

Baseline parity: 82dd1e4d regenerated in /root/r5/p/f2 (second fix-up) gives PARITY_AFTER_NOISE against the committed netlist and
against the round-4 base in /root/r4/p (content hash 223025beeec21b62 all three; `drafts/box/fixup2/base_regen_vs_committed.json`,
`r5base_vs_r4base.json`). Components 56 to 82. The second fix-up changed no netlist content: its netlist against the first fix-up's
is PARITY_AFTER_NOISE (content hash 9bf3a3a46b5d95a6 both; `netlist_compare_vs_fixup1.json`, and `netlist_diff_vs_fixup1.txt` lists
no component, pin or net change), and its diff against the round-4 base is line for line the first fix-up's. New netlist provenance:
generator_sha 284f671249f2cb10 (d4f2f87640edd46f at the first fix-up; the change is gen_sch_p.py's comments), equal to
`sch_prov.generator_sha('p')` on the worktree; the box tree's five overlay files hash equal to the worktree's
(`drafts/box/fixup2/generator-sha256.txt`). Full text: `drafts/box/fixup2/netlist_diff.txt`.

| Difference | Finding |
|---|---|
| Removed C10, R11, R12, R13 | F-PK-02 |
| TS1: -C10.1; TS2/TS3/TS4: -R11.1/-R12.1/-R13.1, +J_TS.2/.3/.4; J_TS.5 on GND; J_TS PH2 to PH5 (C5251182 to C157993), value, lib Conn_01x05 | F-PK-02 |
| U1 footprint QFN-32 5x5 to meshsat RSM0032A; U1 value text | W6-F2 |
| D1 lib D_TVS to D_Zener; D1.1 PACK_N to PACK_P, D1.2 PACK_P to PACK_N; D1 value text; D1 LCSC blank to C364296 | S-09 / A03; B2 |
| D2 USBLC6-2SC6 (SOT-23-6, C7519) to PESD5V0S1BA (SOD-323, C19224); D2.2 GND to PACK_N; D2.3, D2.4, D2.5 (VCC_F), D2.6 dropped; + D3 on SMBD/PACK_N | F-BP-01 |
| J_SMB.3 GND to PACK_N; J_SMB.4 PRES to PRES_J; + R22 (PRES_J to PRES); J_SMB value text | S-05 |
| + U2, R23 (C23025), C14, R24..R27, C15..C18; nets SEC_VDD, SEC_V1..SEC_V4, SEC_COUT, SEC_DOUT; CELL1..CELL4 gain R24..R27 and CELL4 R23 | D-15 / decision 40 (RP-01); B2 |
| + R33 (TS_SEC to GND); net TS_SEC | B1 (RP-17) |
| + F2 SCF9550-30-05 (C3670061, meshsat Eaton land); FUSED loses Q1.1-3 and R17.2, gains F2.1; nets SCP_OUT (F2.2, Q1.1-3, R17.2) and SCP_HTR (F2.3, Q3.3) | D-15 (RP-04, RP-05); B3 |
| + Q3 AO3400A, JP1, R29 (C4184), R30, R31 (C23196), R32 1M, C19; nets FUSE_G, FUSE_GQ; FUSE gains R30.1 | D-15 (RP-06, RP-07); B2; m1 |
| + Q5 2N7002, R28; DSG_G gains Q5.3 | D-15 (RP-02) |
| + RT1 PRF15BB103RB6RC (C443668), C13; U1.23 GND to PTC, U1.24 GND to BAT_F; BAT_F gains RT1.2, C13.2 | D-15 PTC floor (RP-12); m9 |
| + TP11 FUSE_G, TP12 SEC_DOUT, TP13 SCP_OUT | D-15 commissioning (O-9) |
| + TP14 FUSE_GQ | m13 |
| C11.2 PACK_N to PACK_MID, C12.1 PACK_P to PACK_MID; net PACK_MID | O-12 (RP-22) |
| GND: -C10.2, D2.2, J_SMB.3, J_TS.2, R11.2, R12.2, R13.2, U1.23, U1.24; +C14.2, C15.2, C19.2, J_TS.5, Q3.2, Q5.2, R28.2, R31.2, R32.2, R33.2, U2.9, U2.13 | the rows above |
| Second fix-up: none. R-B1 (the JP1 check's polarity and the TPS2 order) and R-m1 to R-m7 changed comments, one placement list and the drafts only | R-B1, R-m1..R-m7 |

Against the round-4 first pass (`netlist_diff_vs_round4_pass.txt`): J_TS2 removed; R33 and TP14 added; F2 value, land and code
(SFK to SCF9550; pins 2 and 3 swap nets because the Eaton heater is pin 3); D1, R23, R29, R31 codes; R32 100k to 1M; RT1 BE103 to
BB103 (C882445 to C443668); U2 value; C11/C12 series (PACK_MID).

## 4. Gates, base (82dd1e4d regenerated) against new (drafts/box/fixup2/{base,new}/v and new/place; second fix-up, box run 08:13:59Z to 08:14:40Z)

| Gate | Base | New |
|---|---|---|
| build_sch | exit 0, one page | exit 0, two pages (pdftoppm now on the box) |
| ERC (erc_gate) | PASS, 87 warnings | PASS, 120 warnings: 103 library-table and 17 wire-endpoint warnings of the layout engine; 0 errors, 0 off-grid |
| TRN-001 port_protect | PASS, 0 ports | PASS, 0 ports (not cited as evidence) |
| SCH-005 pin_map_lands | PASS, 55 judged | PASS, 81 judged |
| CMP-001 derate | PASS, 6 judged, 12 unrated | PASS, 6 judged, 20 unrated, 0 undeclared nets |
| power_path | PASS, 4 rails, 1 feed, 1 node | PASS, 5 rails, 2 feeds, 2 nodes (GND, PACK_MID) |
| BAT-001 pack_protection (on the box; pdftotext present) | 1 failure | 1 failure, identical text: the yaml still declares no second protector (O-4) |
| check_contracts (set) | PASS 73 | PASS 73 |
| energy_chain | PASS 98 (one coordination finding) | same |
| lcsc_fill (JLC BOM as export_jlc.sh builds it) | PASS, 23 rows, 4 blank allow-listed | PASS, 34 rows, 4 blank allow-listed (W_BN, W_BP, W_N, W_P), 0 rejected codes |
| check_pcb_p (placed) | not run | FAIL 4 of 45: U1 land literal, Q1, Q2, J_TS site literals (O-1) |
| netlist_board (placed) | not run | PASS 349 of 349 |
| class_floor, jumper_clearance | not run | PASS; JP1 pads at 0.160 mm |
| DRC (placed, unrouted) | not run | 193 unconnected (no routing, by brief); 0 clearance, courtyard, short, mask-bridge, edge items; silk warnings only |
| Land read-back (pcbnew) | not run | both lands as drawn (landcheck.txt) |
| TPS2 neighbours (tps2_neighbours.py, pad polygons) | not run | TP14 (-20.03, -19.08), TP11, TP12, TP13 (-8.78, -19.08); pad gap 2.26 mm; TP14 to R10.1 (GND) 1.72 mm; TP13 to W_N (PACK_N) 2.83 mm; stitch vias 0.93 and 0.73 mm, tented; SCP_HTR F2.3 to Q3.3 1.05 mm; Q3.2's nearest ground via 3.77 mm |
| lcsc_fill against main 29f00554's re-certified table (runner, scratch copy of main's tools and table, read-only on main) | FAIL: F1 blank over allowance and U1's code rejected | FAIL: F1 blank over allowance only (O-3; not this branch's change) |

## 5. Open items, with who holds them

- **O-1 (owner of check_pcb_p.py).** Line 31 requires the QFN-32 5x5 land; the SITES table needs Q1 (5.3, 15), Q2 (13.3, 15),
  J_TS (26.8, -12.7) and new rows F2 (-3.9, 16.05), Q3 (-2.3, 7.9), RT1 (9.3, 11.0); U2 and F2 in the present list. No J_TS2.
  Its band checks cover FUSED only: the power path gained a node between F2 and Q1, so it should also ask for the locked band of
  SCP_OUT on F.Cu and B.Cu (second fix-up, R-m4).
- **O-2.** CLOSED at the fix-up: the F2 land is in `v2/ecad/meshsat.pretty/` with its land review note.
- **O-3 (owners of the order set, tools/jlc-handfit.txt and JLC-CERTIFIED.tsv).**
  - BOM rows with no LCSC code: W_BN, W_BP, W_N, W_P (12 AWG lands, allow-listed). JP1 is copper, not in the BOM.
  - Coded but not stocked at JLC: F2 C3670061 (0; Digi-Key 907, hand-fit route owed in jlc-handfit.txt).
  - Short at JLC: U2 C3681715 (3 for 5 boards; Digi-Key 2,588).
  - Not yet certified in JLC-CERTIFIED.tsv as the row reads now (a certifier run is owed): D1 (new comment), D2, D3, F2, J_SMB (new
    comment), J_TS, Q3, Q5, R29, R31, RT1, U1 (new comment and land), U2. lcsc_fill passes them because it refuses only codes the
    table has rejected. Main's 6104cb81 (after this worktree's base) makes SCH-002 compare part values and lands against the
    certification, so these rows will read there until the certifier has run; none of main's commits since 82dd1e4d touches a file
    this fix-up changed (checked with `git diff --stat 82dd1e4d HEAD` on the main checkout, read-only; re-checked at the second
    fix-up against main 29f00554).
  - Observed at the second fix-up, NOT this branch's change: main's 29f00554 re-took the certification (720 rows) and now marks F1's
    C4661 WRONG_MODEL ("the row names no part number and its land is drawn for 3568; the code's answer is 23.5*16*25", an XSD holder)
    on boards A, E and P, and U1's C157570 PACKAGE_MISMATCH against the old 5 x 5 land. main's lcsc_fill run on this branch's JLC BOM
    in a scratch copy of main's tools and table: FAIL, 34 rows, one blank over the allowance (F1). The same run on the 82dd1e4d BOM:
    FAIL, F1 blank and U1's code rejected. So this branch clears U1's row (its RSM0032A land) and F1 fails on main either way. The
    Keystone 3568 itself is C5249699 at JLC (Keystone, stock 0, 1.51 USD; JLC API, 26 September 2026), so F1 is a hand-fit or
    certified-code item for the order-set owner on all three boards, not a change taken in this pass (it would be a part
    substitution on three boards' generators, two of them not this author's).
- **O-4 (owner of pcb_pack_protection.yaml, BAT-001).** Set `secondary_protection.present: true`; add U2 (BQ7720700), F2
  (SCF9550-30-05), Q3, Q5, RT1 (PRF15BB103), JP1; hardware functions: cell OV 4.325 V fires F2; open wire (4 s) fires F2 and holds DSG;
  oscillator fault fires F2; cell UV 2.25 V holds DSG (does not fire F2); **no second-level over-temperature** (TS on a fixed 10 kohm,
  RP-17): over-temperature is the gauge's four NTCs and the PTC (trip about 110 to 133 C at the element). Correct the thermistor row
  (R10 is the shunt; the NTCs are Semitec 103AT-2 on J_TS). The 2.25 V against 2.30 V point (RP-03) belongs there.
- **O-5 (board E author, harness owner).** J_SMB as JST-XH 1x4: 1 SMBC, 2 SMBD, 3 GND, 4 PRES. Rise time about 0.9 us against 1.0 us
  with E's 4.7 kohm; stronger pull-ups (2.2 kohm) restore margin. The lead's ground carries about 4 % of the return (0.7 A at 18 A).
- **O-6 (owner of schlayout.py).** An even-length label on Conn_01x05 pins 1 to 3 lands the symbol 0.635 mm off grid (RP-14).
- **O-7.** CLOSED: the box now has pdftoppm and the paged schematic PDF is produced.
- **O-8 (TEST-PLAN owner, F2).** Eaton states -20 to +60 C operating: the -20 C floor of D-02a's -20 to +40 C use envelope is met by
  a rating. E3's +55 C operating phase puts the air round F2 at about 65 to 71 C, beyond that rating, at up to 60 % of its current
  rating, with no derating curve published. Inside the envelope too the count so far is the air only (40 C plus the ruled 10 K with
  one module, 50 C, against 60 C): at the 18 A peak F2 adds 0.32 to 0.81 W of its own (fuse DCR 1.0 to 2.5 mohm), and Eaton
  publishes no current derating at any temperature. Low risk at 60 % of rating, judged, not proven (R-m5). Either E3 states the
  pack's F2 as a known excursion (survive and recover, D-02a) or Eaton is asked for a derating curve; the D-09 battery-and-protection
  packet carries both points.
- **O-9 (bench, commissioning; D-09's battery-and-protection review sees this list before the pack is built).**
  - Read TP11 (FUSE_G) low with the cells on and JP1 open, which proves COUT inactive (no OV, open wire, oscillator fault, or a
    TS-to-VSS short at R33); then close JP1 and confirm TP11 to TP14 continuity **with the meter's COM (black) lead on TP14 and the
    red lead on TP11**, after confirming the meter's source polarity and open-circuit voltage (under 12 V) on the range used with a
    second meter in DC volts (an analogue ohmmeter reverses the polarity). Why: if the closure did not wet, about 98.6 % of the
    meter's open-circuit voltage lands across R32, which is Q3's gate; this polarity holds the gate negative, the other one turns
    Q3 on and the heater can open F2 on a healthy pack (R-B1). Do not use TP14 to TP8 instead (it pulls IC pins below VSS when
    JP1 is closed). Closed reads about 0 ohm, open about 1 Mohm.
  - TP13 is the cell node behind F2: its nearest exposed copper outside the row is W_N (PACK_N) at 2.83 mm, so a slip there
    shorts the cells through F1 and F2. Probe it with a fine or shrouded tip (the row's own gap is 2.26 mm).
  - DSG_G with DSG on at E3's +55 C operating phase: Q5's leakage (IDSS 80 nA maximum at 25 C, none stated above) and R19's
    roughly 1 uA load the gauge's DSG charge pump, which SLUSC67B 6.18 specifies only into 10 Mohm (R-m7).
  - The BQ4050 DSG pin held low through R18 while Q5 conducts (not specified).
  - Charging through Q2's body diode under a UV hold: the golden image needs precharge there.
  - BQ77207 customer-test-mode checks of COUT and DOUT (OV, UV, open wire), with JP1 open.
  - Q2's gate under a UV hold with a charger fault (RP-02).
- **O-10 (firmware / golden image; SLUUAQ3 not held).** TS1 to TS4 enabled as cell temperature; COV below 4.275 V (the second level's
  worst-case low trip); CUV 2.50 V; permanent-fail events that drive FUSE: second-level protector, PTC, open thermistor, safety OV,
  FET faults. **Safety UV is not a FUSE event** (corrected at the fix-up): the heater is rated only from 10.5 V, and UV is recoverable.
  Short circuit in discharge: its delay set so the FETs open well inside F1's 4.3 ms melting time at 480 A (O-13, R-m6).
- **O-11 (decision 28).** Board P is still generated at two layers; the 4-layer 2 oz regeneration and route are owed, and with it the
  pin-adjacent placement of U2's RC filters (RP-20). Decision 28's P8 evidence was taken on the wrong U1 land (N-01). When its
  regions are redrawn: JP1 and C19 move beside Q3, so FUSE_GQ stops crossing the board and C19 sits at the gate it protects
  (R-m3). Route brief for it and for O-14: at least five 0.3 mm or four 0.4 mm barrels at Q3's source (pin 2) to the ground
  plane, `via_current.barrels_for(3.5 A)` at 10 K and 18 um plating, or a top-side ground area from Q3.2 (R-m2); today's nearest
  stitch via is 3.77 mm away.
- **O-12.** CLOSED at the fix-up (RP-22).
- **O-13 (owners of pcb_sensitive.yaml, pcb_energy_chain.yaml, W6 SOURCES.yaml).** TS1's entry cites the removed 100 nF; TS2..TS4 and
  SEC_V1..V4 are candidates for the list (TS_SEC is a fixed resistor now); the energy chain does not yet carry F2 (SCF9550-30-05);
  W6's USB ESD array row still lists board P. The F2 entry should state its 80 A breaking capacity against the node's 240 to 480 A
  prospective fault (PACK_CELLS) and the order that must hold: the gauge's short circuit in discharge (SLUSC67B 6.32: tSCD1 0 to
  915 us, or 1850 us with SCDDx2, plus 160 us detection at most; its setting is O-10's) opens the FETs, and if they fail closed F1
  (1000 A interrupting, melting in 4.3 to 17 ms) opens before F2's element. ELX1135 publishes no melting I2t, so that order is not
  proven; it goes into the D-09 battery-and-protection packet (R-m6).
- **O-14.** Routing out of scope (193 unconnected); the silk legend pass is cosmetic. The route brief carries O-11's via count at
  Q3's source: the heater return is the one high-current path on this board that the locked bands do not lay.
- **O-15 (TEST-PLAN owner, RT1).** PRF15BB103 operating -20 to +140 C; Murata's cold test runs at -20 C only. E4's -33 C storage (the
  element biased with 200 to 350 nA) is outside anything Murata states; a cold excursion lowers the element's resistance and cannot
  trip, so the check after E4 is its 25 C resistance at commissioning.
- **O-16 (pack build).** Tap-harness retention on J_CELL (RP-18): a lead out for 4 s with JP1 closed opens F2 permanently.
