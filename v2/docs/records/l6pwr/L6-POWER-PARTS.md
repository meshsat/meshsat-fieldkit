# L6: the component identities of the parts Layer 4 selected for the power design (MESHSAT-1357, 3 October 2026)

Prototype design: nothing is bought, built, powered or measured. Every figure on this page is printed, with its basis and its page,
by `l6pwr_parts.py` (`l6pwr_parts.out`, "out N" below); this page is the short form. The parts are Layer 4's selections (L4-E5 to
L4-E11) in release-guarded drafts on no committed netlist; this record records and sources them and **reselects nothing**. A
mismatch is a FINDING with the Layer 4 row it affects (section 3), never a change.

**Basis labels.** MAKER (the document, its revision and page, read here from the file), RECORD (a Layer 4 record's figure, its page
pinned in out 0), CATALOGUE (a dated public reading in `inputs/`, true at its time only), COMPUTED (arithmetic shown in the output).

## 1. The envelope the grades are judged against (out 1)

`pcb_envelope.yaml`, read back: in use -20 to 40 C ambient; the worst inside air, lid closed, **62.1 C** (the board air a part is judged
against until T-H1); storage 3 months -20 to 45 C; the owner's qualification margins (D-02a) +55 C operating, +71 C and -33 C storage,
survive and recover. INSIDE: the maker's operating row strictly covers -20 to 62.1 C; AT_LIMIT: an end met exactly; OUTSIDE: an end
missed; NOT READ: no row read at the source.

## 2. The parts in short (out 2; the full block per part, with every page citation, is in the output)

Grade is the maker's operating row against the envelope; "margins" says whether the storage row covers -33 to +71 C. Identity is
the table's vocabulary: RESOLVED (rule D-2 PRINTED: the cited page prints the part number, read here), or UNRESOLVED with its reason
class. Price is LCSC's USD at the quantity given, read 2 October 2026 23:20 UTC. Obligation names the Layer 4 rows (E11-xx of L4-E11,
R-xxx of L4-E9's register).

| Id | Board, refs | Maker, MPN (package) | Grade | Document (revision; sha256/16) | Code, stock, price | Alternative (same footprint) | Obligation rows | Identity |
|---|---|---|---|---|---|---|---|---|
| L6P-01 | A U3 | TI BQ25730RSNR (WQFN-32 RSN 4x4) | industrial; TJ rec. -20 to 125 C: **AT_LIMIT** cold (F07); margins covered | SLUSE65A Jan 2024, held; `e41ef289ce1de377` | C5219071, **0**, 2.8553 (1) | BQ25731RSNR (drawn, same land): no battery FET | E11-27, -28, -31, -32, -37; R-157, R-158, R-161, R-162, R-183 | RESOLVED (p.104) |
| L6P-02 | A Q39, Q40 | Nexperia BUK6Y10-30P, code's model BUK6Y10-30PX (LFPAK56) | automotive AEC-Q101; Tj -55 to 175 C INSIDE | sheet 17 Apr 2020, held; `ba928dfe6a851344` | C3278350, 67, 2.0603 (1) | Vishay SQJ403EP: other land drawing, one FET: not a drop-in | E11-27, -29, -30, -32, -36, -37; R-157, R-159, R-160, R-162, R-182, R-183 | PART_NUMBER_INFERRED (the PX suffix, F02) |
| L6P-03 | A U42 | TI TPS16630PWPR (HTSSOP-20 PWP) | industrial; TJ -40 to 125 C INSIDE | SLVSET9G Apr 2026, held; `8f91a0db2daf2da3` | C1849461 (this reading), 1141, 2.8002 (1) | none on the PWP land | E11-27, -35, -38, -39; R-157, R-179, R-181, R-184, R-188 | RESOLVED (p.36) |
| L6P-04 | A R221, C237, C238, C239 | values only (11k 0.1 %, 22 nF C0G, 1 uF, 100 nF) | NOT READ | none | none | none | E11-27 | CHOICE_OWED; **R221 collides with L4-E8 (F01)** |
| L6P-05 | A D23 | Diodes B540C-13-F (SMC) | commercial; TJ -55 to 150 C INSIDE | DS13012 Rev. 18-2, held; `1b1de94df0a7729f` | C72264, 52515, no ladder at 1 | B550C-13-F (50 V, VF 0.70 V) | E11-27, E11-38; R-157, R-184 | PART_NUMBER_INFERRED (the B5xxC-13-F pattern, F03) |
| L6P-06 | A R11 | Milliohm HoJLR2512-3W-8mR-1% (2512, 3 W) | industrial; -50 to 170 C INSIDE | HoJLR2512 sheet 2020-04-13, in tree; `3224518dbc8bdc85` | C2904240, 9600, 0.0832 (10); 7 mOhm C2904239 1830 | WSL2512 at 8 mOhm: 1 W, not a drop-in on power | R-04, R-37, R-62, R-75, R-155, R-73, R-101 | PART_NUMBER_INFERRED (the numbering scheme, F03) |
| L6P-07 | A R12 | Milliohm HoJLR2512-3W-12mR-1% | as R11 | as R11 | C2904242, 3405 | WSL2512 at 12 mOhm | R-01, R-02, R-64, R-66 | PART_NUMBER_INFERRED |
| L6P-08 | A R227 | Milliohm HoJLR2512-3W-5mR-1% | as R11 | as R11 | C2903482, 106575 | none at 1 W (1.037 W fault bound) | R-06, R-27, R-84, R-97, R-101, R-117, R-120, R-121 | PART_NUMBER_INFERRED |
| L6P-09 | A R221 to R226 | Milliohm HoJLR2512-3W-45mR-1% | as R11 | as R11 | C2903491, 15860, 0.0621 (10) | WSL2512 at 45 mOhm | R-07, R-09, R-40, R-68, R-91 | PART_NUMBER_INFERRED |
| L6P-10 | A C163, C178, C179, C180, C199, C200 | Panasonic EEHZK1V331P (can G 10 x 10.2) | industrial AEC-Q200; -55 to 125 C INSIDE | ZK series sheet, in tree (LCSC's copy); `5455014606c0b676` | C278516, 6246, 0.8074 (1) | EEHZK1V331V (vibration-proof) | R-07, R-68, R-102, R-51 | RESOLVED (p.2) |
| L6P-11 | A C236 | Panasonic EEHZK1V181P (can F 8 x 10.2) | as above | as above | C242139, 2843, 1.1407 (1) | EEHZK1V181V | E11-27, E11-07 | RESOLVED (p.2) |
| L6P-12 | A C6 | Samsung CL10B332KB8NNNC (0603) | NOT READ | none read | C1613, 32760 | any 3.3 nF 50 V X7R 0603 | R-07, R-66 | DOCUMENT_OWED |
| L6P-13 | E U21 (guard), U6 (entry) | TI TPS48110AQDGXRQ1 (VSSOP-19 DGX) | automotive AEC-Q100 grade 1; TJ -40 to 125 C INSIDE | SLUSEE5E Apr 2026, held; `3cfe41fef1407b85` | C17556513, 326, 4.4674 (1) | TPS48111AQDGXRQ1: no OV pin, latch-off | E11-01, -17, -20; R-123, R-153, R-173, R-174, R-176 | RESOLVED (p.44); U21 PROVISIONAL |
| L6P-14 | E Q7 | TI CSD19536KTT (D2PAK) | industrial; TJ -55 to 175 C INSIDE | SLPS540C May 2025, held; `19e1a9660fac8577` | C2687963, 611, 4.4897 (1) | NOT READ (the family's SOA decides) | E11-01, -14, -17, -20; R-123, R-153 | RESOLVED (p.1) |
| L6P-15 | E Q12, Q13 (guard), Q1 (entry) | TI CSD19532Q5B (VSON-CLIP 5x6) | industrial; TJ -55 to 150 C INSIDE | SLPS414B May 2017, in tree; `353ce937cff0b719` | C473333, 2522, 2.1572 (1) | NOT READ | R-17, R-112, R-173, R-176 | RESOLVED (p.1); Q12, Q13 PROVISIONAL |
| L6P-16 | E D4 | Littelfuse SMCJ30A (SMC) | industrial; TJ -65 to 150 C INSIDE; margins covered | SMCJ sheet 11/20/15, in tree; `6e610db955ed8763` | C224048 (this reading), 15670, 0.2982 (5) | Diodes SMCJ30A-13-F: another maker, condition 1 | R-173, R-174, R-176 | RESOLVED (p.2); PROVISIONAL |
| L6P-17 | E D11 | Littelfuse SMCJ40CA (SMC) | as D4 | as D4 | C80273, 4925 | SMCJ40A: not equivalent for D-11 | R-173, R-174, R-176 | RESOLVED (p.2); PROVISIONAL |
| L6P-18 | E C131, C132, C135, C136 | Samsung CL32B225KCJSNNE (1210, 2.2 uF 100 V X7R) | NOT READ at the source (F08) | the maker's page (excerpt in inputs/) | C55151 (this reading), LCSC **0** / JLCPCB 4654, 0.1599 (1) | another maker's part, re-bounded on its curves | R-173, R-176, R-180, R-186, R-187 | PART_NUMBER_INFERRED (the page prints CL32B225KCJSNN); PROVISIONAL |
| L6P-19 | E C133, C134, C71 to C74 | Samsung CL32B106KBJNNNE (1210, 10 uF 50 V X7R) | NOT READ (F08) | the maker's page | C138687 (this reading), 16710 / 30940, 0.3288 (1) | as above | R-173, R-21, R-176, R-36 | PART_NUMBER_INFERRED; PROVISIONAL |
| L6P-20 | E C13, C14 (drawn) | Samsung CL31B106KBHNNNE (1206, 10 uF 50 V X7R) | NOT READ (F08) | the maker's page | C89632, LCSC **0** / JLCPCB 109264 | as above | R-176, R-36 | PART_NUMBER_INFERRED; PROVISIONAL |
| L6P-21 | E R60 to R64 | Vishay Dale WSL2512R0700FEA (2512, 1 W) | industrial; -65 to 170 C INSIDE | Document 30100 Rev 23-Nov-2023, in tree; `96c2dc89ae1e3039` | C2076144, 1970, 0.8059 (1) | WSL2512R0700DEA (0.5 %) | R-21, R-98, R-101, R-70 | PART_NUMBER_INFERRED (the global numbering example, F03) |
| L6P-22 | E U18 | TI INA169NA/3K (SOT-23-5) | industrial; specified -40 to 85 C INSIDE | SBOS181F Feb 2017, held; `dbb74b6cdc543135` | C44322, 61868, 1.138 (1) | INA139NA/3K (40 V, same land) | R-21, R-33, R-101, R-70 | RESOLVED (p.21) |
| L6P-23 | E U19 | TI TPS3701DDCR (SOT-23-THIN-6) | industrial; TJ -40 to 125 C INSIDE | SBVS240C Feb 2019, held; `27c94a6c3a243bf5` | C132788, 26813, 0.6932 (1) | TPS3700DDCR (18 V) | R-21, R-70 | RESOLVED (p.21) |
| L6P-24 | E U20 | TI TPS3808G33DBVR (SOT-23-6) | industrial; TJ -40 to 125 C INSIDE | SBVS050N Aug 2026, in tree; `74d889c0f68af880` | C43698, 36030, 0.4435 (1) | TPS3808G33DBVT (same part, small reel) | R-21, R-70 | RESOLVED (p.22) |
| L6P-25 | E R97 | value only: 28.0k, the draft 1 %, the brief 0.1 % | NOT READ | none | none | none | R-173, R-176 | CHOICE_OWED; **tolerance F04**; PROVISIONAL |
| L6P-26 | E R19 (entry), R87 (guard) | Milliohm HoLLR2512-3W-4.5mR-1% (the code's model) | NOT READ (no HoLLR sheet held, F09) | none held | C2985708, 4225 | a HoJLR2512 4.5 mOhm code, if one exists | E11-01, E11-17; R-123, R-173 | DOCUMENT_OWED |
| L6P-27 | P, the 12 cells 4S3P (D-06) | Samsung SDI INR18650-35E (18650) | cell rows: discharge -10 to 60 C, charge 0 to 45 C: OUTSIDE at the cell's own rows, carried by the envelope's heater-mat carve-out (F11); storage 3 months -20 to 45 C, the margins outside every printed row (L4-E10, U-01) | Ver. 1.1 (distributor's copy), in tree; `5ec577b952b9dc51` | owner-side; USD 8.25 a cell (indicator) | INR18650-30Q (30Q6), compared by L4-E10, not adopted; a cell change is the owner's | R-47, R-103, R-109, R-110; U-01 | RESOLVED (p.3) |
| L6P-28 | P, PROPOSAL only: 4 cells 4S1P | Saft MP 176065 xtd (prismatic 18.65 x 60.5 x 68.7 mm) | industrial; charge -30 to 85, discharge -40 to 85, storage -40 to 85 C: INSIDE including the margins | Doc. 31109-2-0625 June 2025, held; `8ca0a3e09997a4a3` | owner-side; NZ$ 238.72 a cell (listing archived 2025-01-16) | none (it is the alternative) | R-167, R-168, R-169; U-01 the owner's | RESOLVED (p.1) |

**Count:** 28 selections; RESOLVED 14; UNRESOLVED 14 (PART_NUMBER_INFERRED 10, CHOICE_OWED 2, DOCUMENT_OWED 2); grades read at the
source for 21, NOT READ for 7 (out 2, the identity count line).

**Ratings and derating (out 2, "rating used" lines, one example per class).** The charger: VBUS 19.15 to 20.96 V against the
recommended 0 to 26 V (80.6 percent, no further derating). The battery FETs: ISM 320 A (10 us, 25 C) against the 242.9 A docking
pulse, derated x0.7 at the +70 C air, one FET at most 0.848 of it; RDS(on) 21.136 mOhm at -8.5 V and 150 C is an allowance no printed
point bounds (E11-36); the junction limit 150 C, 25 K under the 175 C rating. The eFuse: I(OL) 1.4713 to 1.8018 A INFERRED between the
printed 9 and 30 kOhm rows. The Milliohm resistors: 3 W at 70 C derated linearly to zero at 170 C (R227 1.037 W at the stage's fault
bound, 3 W at 62.1 C). The ZK cans: ripple 2800 mA rms at 100 kHz and 125 C against each can's bound 2.4096 A (86 percent at R11 8 mOhm)
or 2.7661 A (98.8 percent at 7 mOhm); the rated rise not printed (L4-E8 B4). The guard: V(VS) 3.5 to 80 V against the entry's 43.18 V
and the guard's 36 V cold, 80.6 V at the modelled step (F10); INP's 20 V absolute maximum with L4-E7's 18 V line. The cells: 8,000 mA
continuous against 3.33 A a cell at 10 A held and 6 A at 18 A for 60 s; the charger's 3.0 A against 2,000 mA max charge (1.0 A a cell).

## 3. Findings (out 4; each with the Layer 4 row it affects; nothing applied)

| Id | Finding | Affects |
|---|---|---|
| L6P-F01 | **Designator collision, board A:** L4-E8's bank draft reserves R221 to R226 for the ballasts and L4-E11's charger draft adds R221 for U42's ILIM resistor; read by parsing both drafts, the common designator is R221; whichever applies second refuses or renumbers | R-07; R-157 / R-181 (E11-27) |
| L6P-F02 | **Identity, Q39 and Q40:** the fitted code resolves to BUK6Y10-30PX; Nexperia's sheet prints BUK6Y10-30P only (its ordering table names the type without a suffix); the X is INFERRED to be a packing code | E11-27, E11-32 (R-157, R-162) |
| L6P-F03 | **Identity (rule D-2):** six selections rest on sheets that print a numbering scheme, not the part number (B540C-13-F; the four HoJLR2512 values; WSL2512R0700FEA): PART_NUMBER_INFERRED; a DECODED scheme in `part_identities.SCHEMES` would bind them | R-04, R-01, R-06, R-07, R-21, R-157 (tools, no circuit change) |
| L6P-F04 | **Tolerance, R97:** the draft prints 1 percent, the brief 0.1 percent; at 1 percent (R96 low, R97 high) the INP divider's ratio rises 1.57 percent and INP reads 18.186 V at the modelled peak, over L4-E7's own 18 V line by 0.186 V and 1.81 V under the 20 V absolute maximum; at 0.1 percent it reads 17.933 V and the line holds (COMPUTED from the pinned stage-settings output) | R-173, R-176 row 3 |
| L6P-F05 | **Availability:** BQ25730RSNR LCSC 0 against a need of 5; CL32B225KCJSNNE LCSC 0 (JLCPCB 4654) against 20; CL31B106KBHNNNE LCSC 0 (JLCPCB 109264) against 10; two stock pools | E11-32 (R-162); R-173; PROCUREMENT.md section 8 |
| L6P-F06 | **Codes the drafts owe:** TPS16630PWPR C1849461; Littelfuse SMCJ30A C224048; CL32B225KCJSNNE C55151; CL32B106KBJNNNE C138687 (readings, not selections; the generator edit is Layer 8's) | E11-27 / R-181; R-173; R-21 |
| L6P-F07 | **Grade AT_LIMIT, U3:** the recommended operating junction temperature is -20 to 125 C (the electrical table -40 to +125 C); the envelope's floor is -20 C; the drawn BQ25731 prints the same row. Information for the cold-start bench row | none new (E11-23 / R-137) |
| L6P-F08 | **Grade NOT READ, the Samsung ceramics:** the maker's pages print no temperature range; X7R's -55 to +125 C is the EIA class, not a reading | R-173 |
| L6P-F09 | **Document owed, R19 and R87:** the code C2985708 resolves to Milliohm's HoLLR2512 series; the tree holds the HoJLR2512 sheet only, so the drafts' "3W 50ppm" is the catalogue's description | E11-01 (R-123), R-173 |
| L6P-F10 | **Rating basis, U21 and Q12:** the guard's modelled PV_F excursion 80.6 V exceeds the TPS4811-Q1's recommended operating V(VS) 80 V while L4-E7 judges against the 100 V absolute maximum less 10 percent; L4-E7 states which row an 11 us excursion is judged on | R-173, R-176 row 3 |
| L6P-F11 | **Grade OUTSIDE at the cell's own rows, the INR18650-35E:** discharge -10 to 60 C, charge 0 to 45 C against the -20 C floor, carried by the envelope's heater-mat carve-out; the margins unsuitable on published evidence (L4-E10). Information only | none new (R-47, R-103, U-01) |

## 4. The Layer 6 criteria moved for these parts (out 5)

| Item | Before (LAYER-STATUS) | For the 28 power parts now |
|---|---|---|
| 6.1 exact manufacturer, MPN, package and grade | OPEN (no MPN field; board C's slice only) | 14 RESOLVED on a page that prints the part number, 14 UNRESOLVED with their reason; grades read at the source for 21; the block `drafted_identities_l4_power` in `pcb_part_identities.yaml` holds them: **toward PARTLY** |
| 6.2 documents with revision, source, currency | PARTLY | 17 makers' documents named with title, revision, URL, sha256; 10 held back under their terms with one fetch script, every one fetched and matching on 3 October 2026; Samsung's pages excerpted: **PARTLY, the power parts covered** (the ZK URL and the 35E maker copy still owed) |
| 6.3 selection rationale | PARTLY (critical parts) | one sentence per part pointing at its Layer 4 decision: **PARTLY, these parts covered** |
| 6.6 procurement constraints and alternatives | PARTLY | dated readings for 32 codes, an alternative or NOT READ per part, the five-kit need against stock, PROCUREMENT.md section 8: **PARTLY, these parts covered** |
| 6.8 a current, versioned BOM with identity per board | PARTLY | **NOT MOVED**: these parts are on no committed BOM; their identities are staged for the Layer 8 regeneration |

## 5. What this record did not do, and who does it

- Reselected nothing; changed no draft, generator or Layer 4 record. The findings' remedies are Layer 4's (F01, F04, F10) or Layer 8's
  (F06) or the tools' (F03).
- Bought nothing, contacted nobody: Nexperia's packing legend (F02), Samsung's catalogue (F08), Milliohm's HoLLR sheet (F09) and the
  clarification drafts of L4-E7, L4-E10 and L4-E11 stay as drafts for the owner.
- The guard's rows (U21, Q12, Q13, D4, D11, the Samsung ceramics, R97, R87) are PROVISIONAL on L4-E7's round 3; when it lands they are
  re-read against its draft and the output regenerated.
