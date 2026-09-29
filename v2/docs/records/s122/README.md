# Stream s122: the documents CFL-016 names, re-read against the netlists (S-122, MESHSAT-1357)

Prototype design: nothing here is built, bought or measured. Rounds 1 to 3 ran on `fnd/s122` and `fnd/s122b` (from
`main` at `b874b744`, set 13 promoted as `32f26b41`); set 14 (`fnd/int15`) carried them to `1bafab8c`, where
`apply_registry_s122.py` has run. Round 4 runs on `fnd/s122c` from `1bafab8c`, 29 September 2026. The stream changes
documents and its own records only; no generator, netlist or registry file is edited on its branches (the registry
changes are `apply_registry_s122.py`, `apply_registry_s122_r4.py` and `close_s122.py`, for the integrator).

Round 1 corrected 43 passages. The independent check of round 1 (`checks/check-s122-1.md`, filed byte for byte from the
checker's `<scratch>/chk-s122/CHECK.md`) read all 43 true and found 3 blocking and 12 minor items. Round 2 answers them under the coordinator's ruling on CONOPS.md's
baseline. The independent check of round 2 (`checks/check-s122-2.md`, filed byte for byte from the checker's
`<scratch>/chk-s122/CHECK-2.md`) found 1 blocking and 8 minor items; round 3 answers them and changes the method so the
blocking item's class cannot recur (below). Set 14's integration checks
(`v2/docs/records/int15/checks/check-int15-1.md` to `-3.md`, and a fourth check of set 14 held by the integrator)
found five sentences in scope naming parts no generator carries, which the finder could not see because it did not read
makers' part numbers; round 4 answers them and check-s122-3's three minors (below). The independent checks of rounds 4
and 5 (`checks/check-s122-4.md`, `checks/check-s122-5.md`) found a part in a role it does not hold and a rating the
closing list carried unjudged; rounds 5 and 6 answer them (below). The independent check of round 6
(`checks/check-s122-6.md`) found a figure bound to a source that did not state it and six minors; round 7 answers them
under the coordinator's change of diagnosis (below). The independent check of round 7 (`checks/check-s122-7.md`) found
one phrase of the registry's scope statement false and five minors; round 8 answers it (below). Every statement below about what was read is what one
of these scripts read, or a filed check's own words quoted with its file.

## Round 8: one phrase of the scope statement (check-s122-7)

The independent check of round 7 (`checks/check-s122-7.md`, filed byte for byte from the checker's report) found 1
blocking and 5 minor items. It reads the 45 figures of the closing lines against their sources and reports "0
mismatches", and replays the set 15 order (review D first, then S-122: the follow-up opens as S-135, CFL-016 reads PASS,
0 errors).

* **B1, the finder's clause of the scope statement.** Round 7's sentence said the finder reads "a DS code of four or
  five digits (Maxim's DS3231 and DS12887 shapes among them)" as part numbers; `s122lib.PN_LIT` drops a five-digit DS
  code, so that was false. The clause now reads, in the check's wording: "a DS code of four digits (Maxim's DS3231
  shape) and the EMC test methods' names (CE102, RE102) as part numbers, which a judgement must then excuse, and do not
  read a DS code of five digits (Dallas's DS12887 shape, which the literature filter drops), 'SMBJ15A-based' or a plural
  'SMBJ15As'". The script's read-back compares S-122's title with the constant it appends, so the constant and the
  read-back stay one text.
* **m4, one list.** The escape classes are one constant, `apply_registry_s122_r4.ESCAPES`, which S-122's title sentence
  and the follow-up item's title both read, so the item names every class the scope statement names. The list now also
  carries check-s122-7 m3's two role mutants, each read TRUE here with its row's judgement ("the PCM2912A USB codec and
  amplifier", read only as the USB codec; "the CSD18510Q5B VBUS20 switch", a qualifier holding a digit), a load named in
  words other than "to the", the one-word test's two limits, the list item judged by the target rule, two figure forms
  the scan does not read ("135-175 MHz", "25 °C"), and the finder's "Lapp article" miss (m5). "An upper-case commit"
  is now "some upper-case commits (1C187977)" (the check: 1BAFAB8C is not read).
* **m1.** Correction 36 now also says the closing check "compares a unit only where the source states one"
  (`apply_docs_s122_r8.py`, 1 edit after reading that V2-SPEC.md is not a baseline; `apply_docs_s122_r7.py`'s committed
  text is kept and extended, not rewritten; refuses a second run). The closure's evidence says the same.
* **m2.** The closure's evidence names `apply_docs_s122_r7.py` and `apply_docs_s122_r8.py`. Round 7's README said it
  named `_r7.py`; it did not (the check's m2), and that sentence of round 7's replay is corrected below.
* **m3 and m5 stay minors.** m3's two mutants are in the list (above). Of m5: the "Lapp article" miss is in the list;
  "135-175 MHz" and "25 °C" are in the list; the eight-digit date does not reproduce here (`s122lib.names` returns no
  part for "on 20260929 the" or "20260929"; the report does not give the form it ran).
* **Outputs.** Regenerated; only the header lines of `inventory.out` and `verdicts.out` move (V2-SPEC.md's sha); the
  other seven are byte identical. `test_close_s122.py`: ALL PASS.

The scope statement's list, as `ESCAPES` holds it:

> a number with no unit (a form factor such as 2242, a port such as USB 3, 'an NVMe 2280 socket'), a figure in a form the scan does not read ('135-175 MHz', '25 °C'), and any figure off the closing list; a role noun outside the rule's list (FET, source, generator, interface: 'the TPS22810 bias FET', 'the TPS22810 bias source', 'the TLV75801 gate-bias generator'); a second role noun joined by 'and' with no part of its own ('the PCM2912A USB codec and amplifier', read only as the USB codec); a qualifier holding a digit, which forms no role phrase ('the CSD18510Q5B VBUS20 switch'); a part named after its load in words other than 'to the'; the one-word qualifier test, which takes only active parts (U and Q designators) as the holders of a function and sets aside a value that names '<qualifier> <noun>' as its load; a list item '<part> <noun> on <slot or rail>', judged by the target rule, not the list rule; a stale part in a clause that states a date or a history word ('the TUSB2046B hub fitted since 26 September 2026', 'the grade that was bought', 'named on the BOM'); a designator written beside a part it does not carry ('the TLV75801 gate-bias LDO on PA_KEY (U17', 'the AP64500 buck on slots 1 and 3, U5 and U7'), which needs lists of parts and designators paired in order ('the BME688 and BMI270 (U14, U15'); and the finder's shapes, which still read some upper-case commits (1C187977), 'SMBJ15A/BAT54' as one token, a DS code of four digits (Maxim's DS3231 shape) and the EMC test methods' names (CE102, RE102) as part numbers, which a judgement must then excuse, and do not read a DS code of five digits (Dallas's DS12887 shape, which the literature filter drops), 'SMBJ15A-based' or a plural 'SMBJ15As', nor a maker's number after 'Lapp article' ('The Lapp article 0021917 cable').

## Round 7: the instrument's scope, and one follow-up item (check-s122-6)

The independent check of round 6 (`checks/check-s122-6.md`, filed byte for byte from the checker's report) found 1
blocking and 6 minor items. **The coordinator's change of diagnosis for this round:** S-122 is about the documents. The
check lists the 45 figures of the closing lines with the source it read for each, says of the rest of each line "I also
read the rest of each line against the netlists", and of its role mutants "None of these stands in the committed
documents." What remains are escapes of the regression instrument under planted mutants, not stale text. So round 7 fixes the blocking binding and the cheap, sound minors, writes the instrument's known escape
classes into its scope statement (the registry sentence `apply_registry_s122_r4.py` adds to S-122's title, and the list
below), and opens ONE follow-up item for instrument hardening.

* **B1, line 81's 14.4 V node.** Round 6 bound it to the BQ4050 sheet's "VCC = 14.4 V", TI's characterisation
  condition, which holds whatever pack board P carries. It is now bound to `gen_sch_p.py`'s declaration of board P's
  cell node, `_intent.rail("CELL4", 14.4, 10.0, 18.0, "W_BP"`, with board P's `J_CELL` ("4S block"), the generator's
  "one 4S3P block of Samsung INR18650-35E" and the 35E sheet's "3.3 Nominal Voltage 3.60V" beside it as the
  judgement's assertions; the BQ4050 binding is dropped. Every figure of the closing list, one row each:

  | Line | Figure | Bound to | What the source states (as `verdicts.run_assert` reads it) | Why it is the figure's claim |
  |---|---|---|---|---|
  | V2-SPEC 47 | 2 W | `D:U2~NiceRF SA868 VHF 2 W exciter` | D U2 value has 'NiceRF SA868 VHF 2 W exciter' (netlist: 'NiceRF SA868 VHF 2 W exciter, bench-fitted (castellated; VBA') | the line names board D's U2 by its rating; U2's value is that rating (the sheet v1.3's high row tops out at 33 dBm, 2.0 W) |
  | V2-SPEC 47 | 30 W | `PDF:v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf~RA30H1317M1 RoHS Compliance, 135-175MHz 30W 12.5V` | v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf's text holds 'RA30H1317M1 RoHS Compliance, 135-175MHz 30W 12.5V' | the line names the RA30H1317M1 by its power; the maker's sheet states it in its page heading |
  | V2-SPEC 81 | 240 x 160 mm | `PCB:A:outline=240x160` | board A's outline is 240x160 mm (asserted 240x160) | the row gives board A's size; the board file's Edge.Cuts outline is that size |
  | V2-SPEC 81 | six | `PCB:A:layers=6` | board A has 6 copper layers (asserted 6) | the row gives the board's copper layer count; the board file's layer table has that count |
  | V2-SPEC 81 | 14.4 V | `DOC:v2/ecad/tools/gen_sch_p.py~_intent.rail("CELL4", 14.4, 10.0, 18.0, "W_BP"` | v2/ecad/tools/gen_sch_p.py says '_intent.rail("CELL4", 14.4, 10.0, 18.0, "W_BP"' | the row gives the kit's node; board P's generator declares its cell node CELL4 at 14.4 V nominal (10.0 to 18.0 V), the 4S block of J_CELL; the generator names the cells Samsung INR18650-35E, whose sheet gives 3.60 V nominal, four times which is the same figure |
  | V2-SPEC 81 | 9 to 36 V | `E:J_DCIN~9 to 36 V` | E J_DCIN value has '9 to 36 V' (netlist: 'JST-VH socket, 10 A: vehicle and shore DC in 9 to 36 V (lead') | the row gives the input's range; the input connector's value states it |
  | V2-SPEC 81 | three | `A:#val~5.1 V rail to B16=3` | board A: 3 parts whose value holds '5.1 V rail to B16' (read: 3, J_5V_S1,J_5V_S2,J_5V_S3) | the row counts the slot rails and gives their voltage; three connectors each carry a 5.1 V slot rail to B16 |
  | V2-SPEC 81 | 5.1 V | `A:#val~5.1 V rail to B16=3` | board A: 3 parts whose value holds '5.1 V rail to B16' (read: 3, J_5V_S1,J_5V_S2,J_5V_S3) | the row counts the slot rails and gives their voltage; three connectors each carry a 5.1 V slot rail to B16 |
  | V2-SPEC 81 | four | `CNT@b2709118:v2/ecad/tools/gen_sch_a.py~AP64500 5.1 V + INA226=4` | v2/ecad/tools/gen_sch_a.py at b2709118 holds 'AP64500 5.1 V + INA226' 4 times (read: 4) | the row's history counts the AP64500 rails of 7 September; the generator at b2709118 (7 September) has four AP64500 rail groups |
  | V2-SPEC 81 | 13.8 V | `A:U13~+13V8_PA` | A U13 value has '+13V8_PA' (netlist: 'LM5176PWPR buck-boost controller, +13V8_PA from VBAT') | the row gives the PA rail's voltage; U13's value names its output net +13V8_PA |
  | V2-SPEC 81 | 12 V | `A:U15~+12V_HF` | A U15 value has '+12V_HF' (netlist: 'LM5176PWPR buck-boost controller, +12V_HF from VBAT') | the row gives the HF rail's voltage; U15's value names its output net +12V_HF |
  | V2-SPEC 81 | 54 V | `A:U16~+54V_POE` | A U16 value has '+54V_POE' (netlist: 'LM5176PWPR buck-boost controller, +54V_POE from VBAT') | the row gives the PoE rail's voltage; U16's value names its output net +54V_POE |
  | V2-SPEC 81 | 45 W | `A:U18~45 W outlet` | A U18 value has '45 W outlet' (netlist: 'TPS25740ARGER USB-C PD source controller, 45 W outlet (5, 9,') | the row gives the outlet's power; U18's value states a 45 W outlet |
  | V2-SPEC 81 | 3.3 V | `A:U12~3.3 V logic` | A U12 value has '3.3 V logic' (netlist: 'TPS62933DRLR 3 A buck, 3.3 V logic') | the row gives the logic rail's voltage; U12's value states 3.3 V logic |
  | V2-SPEC 81 | eleven | `A:#fp~Radiall_SMPMAX=11` | board A: 11 parts whose footprint holds 'Radiall_SMPMAX' (read: 11, J_BM1,J_BM10,J_BM11,J_BM2,J_BM3,J_BM4,J_BM5,J_BM6,J_BM7,J_BM8,J_BM9) | the row counts the blind-mate sites; board A carries eleven SMP-MAX receptacle footprints |
  | V2-SPEC 81 | 2x13 | `A:J_AB1~IDC 2x13` | A J_AB1 value has 'IDC 2x13' (netlist: "A-B interconnect (IDC 2x13, top side) to B16's underside hea") | the row gives the ribbon's header; J_AB1's value states an IDC 2x13 |
  | V2-SPEC 82 | 330 x 200 mm | `PCB:B:outline=330x200` | board B's outline is 330x200 mm (asserted 330x200) | the row gives board B's size; the board file's outline is that size |
  | V2-SPEC 82 | six | `PCB:B:layers=6` | board B has 6 copper layers (asserted 6) | the row gives the board's copper layer count; the board file's layer table has that count |
  | V2-SPEC 82 | 5 V | `PCB:B:zone=In4.Cu~+5V` | board B has a zone on In4.Cu whose net holds '+5V' (/+5V_DEV,/+5V_S1,/+5V_S2,/+5V_S3) | the row says In4 carries the 5 V planes; the board file's In4 zones are on the +5V nets |
  | V2-SPEC 82 | eight | `DEC:43.outcome~board B is regenerated and routed once on eight layers` | decision 43's outcome says 'board B is regenerated and routed once on eight layers' | the row cites decision 43's layer measure; the decision's outcome says it |
  | V2-SPEC 82 | three | `B:#fp~CM5_Conn_A_10164227=3` | board B: 3 parts whose footprint holds 'CM5_Conn_A_10164227' (read: 3, U30A,U31A,U32A) | the row counts the compute slots; board B carries three CM5 receptacle A footprints, one per slot |
  | V2-SPEC 82 | three | `B:#val~STM32H743=3` | board B: 3 parts whose value holds 'STM32H743' (read: 3, U41,U51,U61) | the row counts the supervisors; three values name the STM32H743 |
  | V2-SPEC 82 | two | `B:U41~two CAN-FD fabrics` | B U41 value has 'two CAN-FD fabrics' (netlist: 'STM32H743VIT6 I/O supervisor A: 2-of-3 quorum on two CAN-FD ') | the row counts the fabrics; U41's value states two CAN-FD fabrics |
  | V2-SPEC 82 | seven | `B:#net~_CA=7` | board B: 7 nets whose name ends in '_CA' (read: 7, HUBRST1_CA,HUBRST2_CA,HUBRST3_CA,SEL1_CA,SEL2_CA,SEL3_CA,WSEC_CA) | the row counts the voters; each voter drives one CA product net (out = AB + BC + CA, gen_sch_b.py) and board B has seven |
  | V2-SPEC 82 | two | `B:#val~TS3DV642=2` | board B: 2 parts whose value holds 'TS3DV642' (read: 2, U3,U4) | the row counts the display switches; two values name the TS3DV642 |
  | V2-SPEC 82 | two | `B:#val~E72-2G4M20S1E=2` | board B: 2 parts whose value holds 'E72-2G4M20S1E' (read: 2, U13,U14) | the row counts the E72 modules; two values name the E72-2G4M20S1E |
  | V2-SPEC 83 | 344 x 228 | `PCB:C:outline=344x228` | board C's outline is 344x228 mm (asserted 344x228) | the row gives board C's size; the board file's outline is that size |
  | V2-SPEC 83 | 240 x 176 | `PCB:C:hole=240x176` | board C has an inner cutout 240x176 mm: yes | the row gives the ring's void; the board file has an inner cutout of that size |
  | V2-SPEC 83 | four | `PCB:C:layers=4` | board C has 4 copper layers (asserted 4) | the row gives the board's copper layer count; the board file's layer table has that count |
  | V2-SPEC 83 | six | `DEC:27.outcome~six layers for board C` | decision 27's outcome says 'six layers for board C' | the row cites decision 27's six layers; the decision's outcome says it |
  | V2-SPEC 83 | seventeen | `C:#val~3 mm=17` | board C: 17 parts whose value holds '3 mm' (read: 17, D1,D10,D11,D12,D13,D14,D15,D16,D2,D22,D3,D4,D5,D6,D7,D8,D9) | the row counts the LEDs and gives their size; seventeen values on board C state 3 mm |
  | V2-SPEC 83 | 3 mm | `C:#val~3 mm=17` | board C: 17 parts whose value holds '3 mm' (read: 17, D1,D10,D11,D12,D13,D14,D15,D16,D2,D22,D3,D4,D5,D6,D7,D8,D9) | the row counts the LEDs and gives their size; seventeen values on board C state 3 mm |
  | V2-SPEC 83 | two | `C:#val~PCA9555=2` | board C: 2 parts whose value holds 'PCA9555' (read: 2, U1,U2) | the row counts the expanders; two values name the PCA9555 |
  | V2-SPEC 84 | 100 x 80 mm | `PCB:D:outline=100x80` | board D's outline is 100x80 mm (asserted 100x80) | the row gives board D's size; the board file's outline is that size |
  | V2-SPEC 84 | four | `PCB:D:layers=4` | board D has 4 copper layers (asserted 4) | the row gives the board's copper layer count; the board file's layer table has that count |
  | V2-SPEC 84 | two | `D:#ref~J_HS=2` | board D: 2 parts whose designator holds 'J_HS' (read: 2, J_HS1,J_HS2) | the row counts the headset jacks; board D carries two J_HS designators |
  | V2-SPEC 86 | 267 x 68 mm | `PCB:E:outline=267x68` | board E's outline is 267x68 mm (asserted 267x68) | the row gives board E's size; the board file's outline is that size |
  | V2-SPEC 86 | four | `PCB:E:layers=4` | board E has 4 copper layers (asserted 4) | the row gives the board's copper layer count; the board file's layer table has that count |
  | V2-SPEC 86 | 9 to 36 V | `E:J_DCIN~9 to 36 V` | E J_DCIN value has '9 to 36 V' (netlist: 'JST-VH socket, 10 A: vehicle and shore DC in 9 to 36 V (lead') | the row gives the input's range; the input connector's value states it |
  | V2-SPEC 86 | 25 A | `E:F3~25 A mini blade` | E F3 value has '25 A mini blade' (netlist: '25 A mini blade (Keystone 3568 holder): pack to the block') | the row gives the pack fuse's rating; F3's value states it |
  | V2-SPEC 86 | eleven | `PCB:E:zones~no copper under the float clamp=11` | board E's board file: 11 zones whose name holds 'no copper under the float clamp' (read: 11) | the row counts the float clamps; board E's file carries one named keep-out per clamp, eleven |
  | V2-SPEC 86 | two | `E:#ref~J_FAN=2` | board E: 2 parts whose designator holds 'J_FAN' (read: 2, J_FAN1,J_FAN2) | the row counts the mixer fan headers; board E carries two J_FAN designators |
  | OPERATING-ENVELOPE 77 | 9 to 36 V | `E:J_DCIN~9 to 36 V` | E J_DCIN value has '9 to 36 V' (netlist: 'JST-VH socket, 10 A: vehicle and shore DC in 9 to 36 V (lead') | the row names the input the LM5069 sits on; the input connector's value states its range |
  | OPERATING-ENVELOPE 77 | -40 to +125 C | `PDF:v2/vendor/ti/ti-lm5069.pdf~TJ Junction temperature -40 125 °C\|(1) For detailed information on soldering plastic VSSOP` | v2/vendor/ti/ti-lm5069.pdf's text holds 'TJ Junction temperature -40 125 °C\|(1) For detailed information on soldering pla' | the row gives the LM5069's range; the maker's recommended junction row gives it, with its sign |
  | OPERATING-ENVELOPE 83 | -40 to +80 C | `PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~Service Temperature -40 ~ +80` | v2/vendor/m2/te-2199119-m2-b-key.pdf's text holds 'Service Temperature -40 ~ +80' | the row gives the socket's range; the maker's service temperature gives it, with its sign |

* **m1, figures compared as values.** `verdicts._fig_match` needs the token's values in the same order, one after the
  other, in the assertion's content, each the same signed number, with the token's unit wherever the source states one
  (a count or an "NxM" matches only numbers with none). `verdicts._values` reads 13V8 as 13.8 V and 240x160 as 240 and
  160, a spelled count as its number, a minus or plus as a sign only after a space or bracket (135-175MHz is 135 and
  175), and no number inside a name (In4, CELL4, the digits of a part number). The PDF reader reads a sheet's minus
  printed as U+2013 or U+2212 as "-", so the LM5069's range is asserted "TJ Junction temperature -40 125 °C" (the round 4
  TRACO judgement's assertion too). The check's plants with their keys rewritten and the assertions kept, "160 x 240
  mm", "2x2 ribbon", "+40 to +80 C" and "+40 to +125 C", with line 47's 1 W, are refused (`close_s122.KEYED`, in the
  gate's condition (e)). `test_close_s122.py`'s T4 now rewrites the keys that span the changed figure and keeps the
  assertions, so each of its 45 refusals comes from the comparison; T5 replaces `_fig_match` with one that accepts
  everything, and then T4 fails (45 of 45 changes pass) and the gate refuses.
* **m2, the role rule.** Two one-line fixes, each pinned by a mutant and a switch of `verdicts.ROLE_TESTS`:
  * "wordmatch": a qualifier is read in a value as a word, so VBUS is not found in "VBUS20" ("the CSD19532Q5B VBUS
    switch" reads STALE);
  * "load": the forward test drops a value's "to the <load>" phrase, so D `U6`'s "stereo output to the headphone
    amplifier" does not make the PCM2912A an amplifier ("the PCM2912A headphone amplifier" and the check's swap with
    "USB interface" read STALE).
  The other classes are named, not chased (the escape classes below).
* **m3.** Correction 36 now says the closing check "asserts every figure with a unit, and every spelled count, on the
  lines it closes (a number with no unit is outside it ...)" (`apply_docs_s122_r7.py`, 1 edit, after reading that
  V2-SPEC.md is not a baseline; refuses a second run). The sources are named in full in the registry sentence and in the
  closure's evidence: a netlist value, a board file's outline, layers, cutout or zones, a maker's page, a generator's
  text (gen_sch_p.py's cell node; gen_sch_a.py at `b2709118` for "all four AP64500 on 7 September", `CNT@b2709118`), or
  a decision's record.
* **m4, the finder.** A token right after a maker's name or "article" is that maker's number when it holds a digit:
  ABLIC S-8261, TI bq2970, u-blox ANN-MB2, Xenarc 709GNK, Amphenol 132170, Lapp's article 0021917 and MG Chemicals 422B
  now read as parts, and the twelve sentences they stand in are judged (seven newly inventoried, 1004 sentences became 1011: the Xenarc
  monitor bought, Amphenol's couplers case items the case set of 27 September 2026 retired, the u-blox antenna and the
  Lapp cable bought, the coating a material, decision 40's two single-cell protectors set aside). The literature filter
  keeps ST's shapes only: RM, ES and PM with a leading 0 and TN with 0 or 1, so RM3100 and TN2106 read as parts; ST's
  DS with five digits keeps the shape of Dallas's DS12887, which the filter still drops (a stated limit). The dead date
  guard inside the nine-digit rule is gone. Conservative false hits stay, each needing a judgement's excuse: an
  upper-case commit, "SMBJ15A/BAT54" as one token, a DS code of four digits, the MIL-STD-461 methods CE102, CS101,
  CS114 and RE102, DCF77, TE's product specifications and JLC04162H-7628.
* **m5, set 15.** The run order below has a section for `fnd/int16` (`36bb1d12`).
* **m6.** `figures_uncovered` reads a `counts_ok` that is a string as covering nothing (no crash), and a hex address
  (0x22) is not an "NxM" figure.

**The instrument's known escape classes** (what the gate does not catch; carried by the follow-up item; round 8
keeps them in one list, `ESCAPES`, above, which adds to these):
* a number with no unit (a form factor such as 2242, a port such as USB 3) and any figure off the closing list (the
  check's "an NVMe 2280 socket" on line 82, "`Y1` 16 MHz" on PANEL.md line 55);
* a role noun outside `ROLE_NOUN` (the check's FET, source, generator, interface: "the TPS22810 bias FET", "the TPS22810
  bias source", "the TLV75801 gate-bias generator");
* a stale part placed in a clause that states a date or a history word (the check's "the TUSB2046B hub fitted since
  26 September 2026", "the grade that was bought", "named on the BOM"): the tie should be to a past-tense verb on the
  part itself;
* a designator written beside a part it does not carry (the check's "the TLV75801 gate-bias LDO on `PA_KEY` (`U17`",
  "the TPS22810 load switch of the exciter's `+5V_TX` (`U15`)", "the AP64500 buck on slots 1 and 3, `U5` and `U7`"): not
  a one-line fix, since lists pair in order ("the BME688 and BMI270 (`U14`, `U15`" is TRUE and a nearest-part rule
  would refuse it);
* the one-word qualifier test takes only active parts (U and Q) as holders of a function, and a value that names
  "<qualifier> <noun>" as its load is set aside there (so "the CSD19532Q5B VBUS switch" is refused through `U32`'s
  "VBUS_WALL", not through `Q27`);
* a part named after its load in words other than "to the" (the "load" switch reads only that phrase);
* the finder's shapes: the conservative false hits above, and "SMBJ15A-based" and a plural "SMBJ15As" not read.

**The follow-up item.** `apply_registry_s122_r4.py` opens it at the next free S number of the registry it runs on (the
highest S number of the open and closed items, plus one; never hard-coded: on set 15, S-125 is taken and review D takes
S-126 to S-134 if it is applied first), class SESSION, status OPEN, disposition PROCESS, in no record's waits_on and not
in CFL-016's, with this text (the script screens it for claim words and dashes):

  > **title:** (stream s122, the regression instrument's known escape classes; the independent checks v2/docs/records/s122/checks/check-s122-5.md and check-s122-6.md, m2 and m4) Harden S-122's regression instrument (v2/docs/records/s122: s122lib.py's part-number finder, verdicts.py's role rule and figure scan, close_s122.py's gate) against the escape classes its scope statement names: a role noun outside ROLE_NOUN read as no role (check-s122-6's 'the TPS22810 bias FET', 'the TPS22810 bias source', 'the TLV75801 gate-bias generator'); a stale part in a clause that states a date or a history word ('the TUSB2046B hub fitted since 26 September 2026', 'the grade that was bought', 'named on the BOM'), for which a history excuse should tie to a past-tense verb on the part itself; a designator written beside a part it does not carry ('the TLV75801 gate-bias LDO on PA_KEY (U17', 'the AP64500 buck on slots 1 and 3, U5 and U7'), which needs a rule that pairs a list of parts with a list of designators in order ('the BME688 and BMI270 (U14, U15'); a number with no unit and any figure off the closing list ('an NVMe 2280 socket'); and the finder's conservative false hits and misses (an upper-case commit, 'SMBJ15A/BAT54' as one token, a DS code of four or five digits, the EMC test methods' names (CE102, RE102), 'SMBJ15A-based', a plural 'SMBJ15As'). Open until each class is closed by a rule with a fixture that close_s122.py runs, or carried with its reason.
  >
  > **disposition_why:** The documents S-122 names are the subject of S-122 and CFL-016; this item is about detecting a
  > regression in them. The classes are escapes of the instrument under planted mutants, not stale text: of its role
  > mutants check-s122-6 says 'None of these stands in the committed documents.' So no record's verdict waits on this
  > item, and CFL-016 does not.

  `close_s122.py` refuses unless that item is open once with disposition PROCESS and no record waits on it, and names it
  in S-122's closing evidence.
* **What round 7's tools find:** on the documents at `1c187977` (`verdicts-r6.out`, new) 0 STALE; at `a6429e66` 1 (line
  47); at `edead832` 5; on set 14's 10; the base's 74.

## Round 6: figures on the closing list (check-s122-5)

The independent check of round 5 (`checks/check-s122-5.md`, filed byte for byte from the checker's report) found 1
blocking and 4 minor items.

* **B1, the exciter's rating.** V2-SPEC.md line 47 named the NiceRF SA868 a 1 W part, the figure of the device set of
  6 September (the appendix's section 32.49: "NiceRF SA868 1 W module plus a 30 W VHF amplifier stage"). Board D's `U2`
  is "NiceRF SA868 VHF 2 W exciter"; `gen_sch_d.py` says "2 W high / 0.5 W low" at `bdfc7b3f` and not at its parent;
  the maker's sheet v1.3 reads "31 32.5 33 dBm" on high power and "24 25 26 dBm" on low. V2-SPEC.md is not a baselined
  definition: `apply_docs_s122_r6.py` reads the table of `handover/DEFINITION-STATUS.md`'s "## The two baselines"
  (`v2/docs/PRODUCT-BRIEF.md` and `v2/docs/CONOPS.md`) and `s122lib.BASELINED`, and refuses if either names V2-SPEC.md.
  It corrects line 47 to "NiceRF SA868 VHF 2 W exciter (`U2`, correction 36)", keeps no 1 W on the line, and writes
  correction 36 (2 edits, 9 assertions held first; refuses a second run).
* **The method: every figure on the closing list is bound, and only there.** The instrument is not widened to judge
  every figure of every sentence. `verdicts.figure_tokens` reads a sentence's figure-and-unit tokens: a number with W,
  mW, kW, V, mV, A, mA, Wh, Ah, mAh, dBm, dB, mm, cm, C, Hz, kHz, MHz, GHz, ohm or oz, a range or a product of two, an
  "N x M" size, an "NxM" header, and a spelled count from two to twenty. A judgement's `figures_ok` maps a phrase of its
  sentence that holds a token to `asserted: <one of its own assertions>`, and `verdicts.figures_uncovered` needs the
  assertion's stated content (after its subject) to carry the token's numbers (13.8 is read in `+13V8_PA`; a spelled
  count in its numeral or its word; since round 7 as ordered, signed values with their units, above); an `asserted:`
  entry of `counts_ok` covers the same way. `verdicts.check_figs`
  holds a judgement that declares `figures_ok` to it; `close_s122.py`'s condition (f) scans every sentence of every line
  of the closing list, read whole from its document (the two OPERATING-ENVELOPE.md range cells the inventory does not
  take among them, their judgements' assertions run by the gate), and refuses a token no assertion covers. A figure
  with no source to assert against would take its line off the closing list, NOT DERIVABLE: none does. The 45 tokens
  of the eight lines are bound to:

  | Line | Figures | Bound to |
  |---|---|---|
  | V2-SPEC.md 47 | 2 W, 30 W | `D:U2~NiceRF SA868 VHF 2 W exciter`; the RA30H1317M1 sheet's "135-175MHz 30W 12.5V" |
  | V2-SPEC.md 81 | 240 x 160 mm, six layers, 14.4 V, 9 to 36 V, three 5.1 V slot rails, all four AP64500 on 7 September, 13.8 V, 12 V, 54 V, 45 W, 3.3 V, eleven sites, 2x13 | board A's file (outline, 6 copper layers); for 14.4 V, since round 7, `gen_sch_p.py`'s cell node CELL4 (round 6 bound it to the BQ4050 sheet's test condition, check-s122-6 B1); `E:J_DCIN`; `A:#val~5.1 V rail to B16=3`; `gen_sch_a.py` at `b2709118` holding "AP64500 5.1 V + INA226" 4 times; the values of `U13`, `U15`, `U16`, `U18`, `U12`; eleven `Radiall_SMPMAX` footprints; `J_AB1` "IDC 2x13" |
  | V2-SPEC.md 82 | 330 x 200 mm, six layers, 5 V planes, eight layers, three slots, three supervisors, two fabrics, seven voters, two display switches, two E72 | board B's file (outline, 6 layers, In4 zones on the `+5V` nets); decision 43's outcome; three `CM5_Conn_A_10164227` footprints; `#val~STM32H743=3`; `U41` "two CAN-FD fabrics"; seven nets ending `_CA`, one per voter (`out = AB + BC + CA`, `gen_sch_b.py`); `#val~TS3DV642=2`; `#val~E72-2G4M20S1E=2` |
  | V2-SPEC.md 83 | 344 x 228, 240 x 176, four layers, six (decision 27), seventeen 3 mm LEDs, two PCA9555 | board C's file (outline, inner cutout, 4 layers); decision 27's outcome; seventeen values holding "3 mm"; `#val~PCA9555=2` |
  | V2-SPEC.md 84 | 100 x 80 mm, four layers, two jacks | board D's file; `#ref~J_HS=2` |
  | V2-SPEC.md 86 | 267 x 68 mm, four layers, 9 to 36 V, 25 A, eleven float clamps, two fans | board E's file (outline, 4 layers, eleven zones named "no copper under the float clamp"); `J_DCIN`; `F3` "25 A mini blade"; `#ref~J_FAN=2` |
  | OPERATING-ENVELOPE.md 77 | 9 to 36 V; -40 to +125 C | `E:J_DCIN`; the LM5069 sheet's recommended junction row |
  | OPERATING-ENVELOPE.md 83 | -40 to +80 C | the TE sheet's "Service Temperature -40 ~ +80" |

  New assertion forms for this (`verdicts.py`'s docstring): the board file beside a netlist (`PCB:<b>:layers=`,
  `outline=`, `hole=`, `zone=<layer>~<net>`, `zones~<name>=N`), nets by the end of their name (`#net~`), a text's count
  in a file at a commit (`CNT@`), and a decision's field (`DEC:`).
* **m1, the role rule's blind spots.** `rail_lists` reads every list after a rail phrase, takes each comma item's part
  and drops the trailing role and qualifier words ("EMCON gated", "bias switch"), so a non-part item no longer drops the
  sentence; an item "<part> <noun> on <slot or rail>" is judged by the new `target_roles` against that slot's or rail's
  converters (a rail by its word, its voltage or, for the USB-C outlet, `PD_VPWR`); a one-word qualifier the part's own
  values do not state, while an active part (U or Q) of the board states it, is refused; `ROLE_NOUN` takes supply and
  driver; and in a TRUE sentence a `parts_ok` history excuse holds only in a clause that states history. The gate's
  condition (e) judges fourteen mutants of the A22 and D8 rows as they stand (`close_s122.MUTANTS`), each with the
  judgement its row carries; each reads STALE: the check's "(AP64500, EMCON gated)" on the PA and HF rails, the PA
  and HF rails "(AP64500)", "the 3.3 V logic rail (LM5176)", the PoE rail "(AP64500)", line 81's two converters
  swapped, the outlet's stage named AP64500, the TPS22810 "bias switch" and "gate-bias switch", the TPS22810
  "gate-bias supply" and "gate-bias driver", the TPS55288 and the TUSB2046B put back as current, the codec and the
  amplifier swapped, and the TPA6132A2 named a codec.
* **m2, the forward test pinned.** The role rule's four tests and the history tie can be switched off one at a time
  (`verdicts.ROLE_TESTS`); `test_close_s122.py` does so and shows, for each, the mutants that then read TRUE and the
  gate refusing: forward (the TPA6132A2 named a codec), reverse1 (the bias switch), reverse2 (the gate-bias switch; the
  gate refuses first at round 5's fixture), rails (six), history (the TUSB2046B). The check's swapped codec and
  amplifier also stays STALE with the forward test off, because the one-word test reads its "USB".
* **m3.** The closure's evidence names `apply_docs_s122_r5.py` and `apply_docs_s122_r6.py` with the four before them.
* **m4, the finder.** L76K reads as a part (a designator only when a netlist carries it); an all-digit number of nine
  digits or more reads as a part (5023520600), a date of eight does not; literature and manual codes (SNVA559,
  SLVA505, AN2606, RM0433, ES0392, PM0253, UM2179, TN1204, and ST's DS with five digits), RJ and RS numbers (RJ45,
  RS485, and the test method RS103), `NBASE-T` names, UN38.3 and the netlists' own net names (VBUS20) do not. DS1234
  still reads as a part: DS with four digits is the shape of Maxim's parts (board B's DS3231SN). Three sentences left the inventory
  with it, each NOT DERIVABLE before and naming nothing else: ASSEMBLY.md line 148's two RJ45 cells and TEST-PLAN.md
  line 43's RS103 cell. The netlist-drawn probe is kept, with the two limits check-s122-5 states in its own words:
  it "skips a token that the finder's own `PN_PIN` excludes (one today: C `D18`, "GPIO25")", and it "leaves out
  connectors, although the documents name TE 2199119-3, R222M00720, 813-S1-012-10-016101, B4B-XH-A and XT60". Still
  read as part numbers, and so needing a judgement's excuse, never passing: an upper-case commit and "SMBJ15A/BAT54"
  as one token; not read: "SMBJ15A-based" and a plural "SMBJ15As" (of these three SMBJ15A forms, in the check's words,
  "The documents hold none of these.").
* **What round 6's tools find** on the documents at `a6429e66` (`verdicts-r5.out`): 1 STALE, line 47; at `edead832`
  (`verdicts-r4.out`): 5, line 47 and the four round 5 corrected; on set 14's (`verdicts-set14.out`): 10.

## Round 5: parts in their roles (check-s122-4)

The independent check of round 4 (`checks/check-s122-4.md`, filed byte for byte from the checker's report) found 1
blocking and 3 minor items: two parts named in roles the netlists no longer give them read TRUE, because round 4's
judgement asked only whether a part number is on the board.

* **The role rule** (`verdicts.check_roles`, applied with the part check: a failure makes a TRUE judgement STALE and a
  NOT DERIVABLE one UNJUDGED). A part named with a role ("the X gate-bias switch", "the X USB codec", "the X buck") is
  read against the designators whose netlist values carry it:
  * forward: one of them states the role's noun (`ROLE_SYN` lists the words a value states a noun by: a "SPDT antenna
    changeover" is a switch, a "buck-boost controller" a stage);
  * reverse: when the role's qualifier is specific (two words or more, "gate bias"), no designator that does not carry
    the part states it while none that carries the part does;
  * rails: a plain list of parts after a phrase naming rails (slot, device, PA, HF, PoE) must be the part of every
    converter whose value states that rail's net, and a part marked "monitored" of every monitor of it;
  * `roles_ok` binds a role the netlist states in other words or by a net to one of the judgement's own assertions on a
    designator that carries the part (the LM5176 as A22's front end, `U2` "VBUS20 from VIN_RAW"; the LT8705A as the
    solar tracker, `U5` pin 32 on `PV_P`; C7's PCA9555 as the panel expanders, `U1`).
* **Its tests** are in `close_s122.py`'s gate, condition (e): the check's two sentences as they stood at `edead832`
  (the D8 row's "TPS22810 gate-bias switch", the A22 row's "(AP64500, INA226 monitored)"), judged TRUE with the check's
  own reading (`D:U21~TPS22810`, `A:U4~AP64500`), must be refused by the role rule and must not read TRUE; and in (b)
  the corrected rows must read TRUE with their role assertions.
* **The corrections** (`apply_docs_s122_r5.py`: 5 edits, 33 assertions held first, refuses a second run), V2-SPEC.md's
  correction 35:

  | Line (at `edead832`) | What it said | What the netlists carry | Now |
  |---|---|---|---|
  | 84, D8 row | "the TPS22810 gate-bias switch" | board D's gate bias is `U15`, TLV75801 "PA gate bias VGG ... while PA_KEY is high", EN (pin 4) on `PA_KEY`, since `faf8c981`; the only TPS22810 is `U21`, "load switch, +5V_TX"; at `b2709118` a TPS22810 switched the bias | "the TLV75801 gate-bias LDO on `PA_KEY` (`U15`; on 7 September a TPS22810 switched the bias, correction 35), the TPS22810 load switch of the exciter's `+5V_TX` (`U21`)" |
  | 81, A22 row | "three 5.1 V slot rails and a device rail (AP64500, INA226 monitored)" | `U4` and `U6` AP64500 (`+5V_S1`, `+5V_S3`); `U5` and `U7` LM5176 (`+5V_S2`, `+5V_DEV`); all four AP64500 at `b2709118` | "(the AP64500 buck on slots 1 and 3, `U4` and `U6`, and LM5176 stages on slot 2 and the device rail, `U5` and `U7`, all four AP64500 on 7 September, correction 35; INA226 monitored)" |
  | 86, E6 row (m2) | "the sensor controller with the BME688, BMI270 and magnetometer" | board E carries the BME688 `U14` and the BMI270 `U15` and no magnetometer; `gen_sch_e.py`: "the magnetometer sits in the outside pod (32.57)", reached through `J_POD` (`SDA1`, `SCL1`) | "the sensor controller with the BME688 and BMI270 (`U14`, `U15`; the magnetometer is in the outside pod, reached through `J_POD`, correction 35)" |
  | 83, C7 row (m3) | "sixteen LEDs under light guides" | seventeen `LED_D3.0mm` on board C, `D22` the EMCON lamp; S-44 open | "seventeen 3 mm LEDs under light guides (`D1` to `D16` and ... `D22`, whose guide in the plate is owed, open item S-44; correction 35)" |
* **The finder, widened (m1).** New shapes: letter-led with two digits and two capitals (TI's SN74 gates, BAT46W, BAT54,
  USBLC6-2SC6, E72-2G4M20S1E, SMBJ5.0A, XT60), letter-led with four capitals and an inner digit (LIS3MDL, B2B-XH-A),
  mixed case with two capitals and three digits (Si2300DS, nRF52840), all-digit numbers after a maker's name (Molex
  5023520600); round 4's shapes kept. New exclusions by shape: designators (TP10), TI literature numbers (SLUSE66A),
  month codes (JUN26), a series and pitch (XH2.5), finding identifiers (F-DEC40, W3-F01), band lists (L1/L2/L5/E6), a
  dotted digit-led table number (516.8-IX). The gate's probe (a) now also takes every part number a semiconductor's,
  crystal's or relay's value in the six netlists starts with (the maker's name skipped; ratings, values and pins not),
  so a finder that misses a family the boards carry cannot pass.
* **What round 5's tools found on the documents at `edead832`** (`verdicts-r4.out` as round 5 wrote it): 4 STALE,
  V2-SPEC.md lines 81, 83, 84 and 86, each corrected above; on set 14's documents (`verdicts-set14.out`) 10.

## Round 4: makers' part numbers (set 14)

* **The finder** (`s122lib.partnos`, returned by `names()` under `parts`) reads a maker's part number by its shape, not
  from a list: a letter-led token of capitals and digits with a run of three digits (TMDS341A, LM5069, E22-900M30S,
  D38999/26FC4SN), a digit-led token with a capital and four digits (74LVC1G157GW, 2N7002), a digit token with a dash
  and six digits (2199119-3), a series word of two to four capitals before a digit-led number with a dash and three
  digits (TEN 40-2412WIN), and the same shapes in the file names of the makers' sheets a sentence cites
  (`m2/amphenol-mdt420b01001-m2-b-key.pdf`). It leaves out tokens with a lower-case letter (commits, units), registry
  and standard identifiers (letters, dashes, one number: CFL-016, MIL-STD-810), tokens led by a standard body, and pure
  ranges of two numbers of up to four digits (144-146). A table cell carries its row's label (`names()["row"]`).
* **The judgement** (`verdicts.check_parts`): each part number is looked up in the part values of the six netlists. One
  on no netlist, or not on the one board a sentence and its row label name, makes a TRUE judgement STALE and a NOT
  DERIVABLE one UNJUDGED, unless the judgement's `parts_ok` names it: an own assertion that names it (a generator or a
  netlist at a commit, a document, a part value), or a reason that starts with a kind (`document`, `case`, `bought`,
  `stock`, `stackup`, `withdrawn`, `owed`, `module`, `elsewhere`; `elsewhere` is refused unless the part is on some
  netlist). A dated heading excuses no part: the boards table's rows are judged part by part.
* **New assertion forms:** a held maker's sheet read with `pdftotext` (`PDF:<path>~words`).
* **What it found on set 14's documents** (`verdicts-set14.out`, the documents at `1bafab8c` judged by round 4's tools):
  7 STALE, each corrected by `apply_docs_s122_r4.py` (12 edits, 51 assertions held first):

  | Where (at `1bafab8c`) | What it named | What the netlists carry | Correction |
  |---|---|---|---|
  | V2-SPEC.md line 82, B16 row | the TMDS341A display switch (no schematic generator has held one, `git log --all -S TMDS341`) and the DS3231M clock | board B's `U3` and `U4` TS3DV642A0RUAR (`gen_sch_b.py` held the TS3DV642 at `b2709118`, when the table was written); `U9` DS3231SN | "the two TS3DV642 display switches (`U3`, `U4`)", "the DS3231SN clock (`U9`; the DS3231M on 7 September)" |
  | V2-SPEC.md line 84, D8 row | the TUSB2046B hub | board D's `U4` TUSB2046IBVFR (the industrial grade since 26 September 2026, W6-F5) | "the TUSB2046I hub (`U4`, TUSB2046IBVFR ...; the TUSB2046B on 7 September)" |
  | V2-SPEC.md line 86, E6 row | the LM5176 9 to 36 V front end on E6 | board E's `U6` LM5069MM-2 hot swap; the LM5176 front end is board A's `U2`, as `gen_sch_e.py` said at `b2709118` | "the LM5069 hot swap on the 9 to 36 V input (`U6`), which passes the bus up to A22's LM5176 front end (`U2`)" |
  | V2-SPEC.md line 47, APRS row | the WM8960 codec, and the PA's sheet "owed" | board D's `U6` PCM2912A (the WM8960 left `gen_sch_d.py` at `bdfc7b3f`); the RA30H1317M1's sheet held in `v2/vendor/mitsubishi/` | "Direwolf on D8's PCM2912A USB codec (`U6`)", the sheet held |
  | OPERATING-ENVELOPE.md line 77 | TRACO TEN 40-2412WIN, -40 to +75 C | no TRACO part on any netlist (`gen_sch_e.py`: the TRACO converter of E4 is gone); board E's input part is `U6` LM5069 | "TI LM5069 hot-swap controller on the 9 to 36 V input (board E `U6`)", junction -40 to +125 C from `ti/ti-lm5069.pdf` (SNVS452G, 7.3, read by pdftotext) |
  | OPERATING-ENVELOPE.md line 83 | Amphenol M.2 B-key socket, MDT420B01001 (in its source's file name) | board B's `J_M2C2` TE 2199119-3; Amphenol's MDT420M02001 are the M-key NVMe sockets | "TE 2199119-3 M.2 B-key socket (board B `J_M2C2`)", -40 to +80 C service temperature from `m2/te-2199119-m2-b-key.pdf` (Performance Ratings) |
  | CONOPS.md line 1056, section 7's D-13 row | the STM32H753 in the schematic, the mismatch open | `U41`, `U51`, `U61` STM32H743VIT6 since `458b2873`; CON-017 PASS | the baseline stays; row DC-10 on the status page (check-s122-3 m1) |

  V2-SPEC.md records the four lines as correction 34; OPERATING-ENVELOPE.md carries a correction note after its table;
  in check-int15-1's words (B1 fix) no envelope number depends on either row.
* **check-s122-3's minors:** m1, row DC-10 (above); m2, the absent rule reads the wordings the check swept ("has no",
  "does not have", "only through", "in the schematic", "nothing does", "lacks", "no path", "no hardware", "not gated",
  "driven only", "until ... generator", besides the four words): the committed `verdicts.out` at `d38c6b4d` held 35
  CONOPS sentences with those wordings (18 with the four words), and it holds 51 now, 16 TRUE, 18 BASELINE, 17 NOT
  DERIVABLE with each wording bound to a phrase that is not about the circuit, 0 STALE, 0 UNJUDGED; the sentences it
  added include section 7a's HOT-R1 row's second cell (BASELINE on DC-02) and section 7's D-13 row; m3, the CON-003
  note below.
* **check-int15-1's m7:** `apply_registry_s122_r4.py` appends to CFL-016's `notes` the reading of its acceptance through
  the status page.
* **The fourth check of set 14:** q1 (S-122's row clause) is answered by `apply_registry_s122_r4.py`'s appended
  sentence; q2 and q3 by `close_s122.py`'s gate (below); q4 by `apply_docs_s122_r4.py`'s edit of
  `records/int15/apply_check15c_fixes.py`'s docstring (its filing note ends each check) and the gate's rewritten
  docstring.

## The baseline rule, and what it changed

`CONOPS.md` is a BASELINED layer 2 definition. Its head, and `handover/DEFINITION-STATUS.md`, say that a changed count or
a circuit correction updates the status page and the records it names, not the baseline. Set 12's two circuit commits
(`a46db71b`, `7a9f7b5b`) and round 1 of this stream edited CONOPS against that rule. So round 2:

* **restores `CONOPS.md` to its text at `c5430071`** (the owner's rulings of 28 September, the last change the rule
  allows). `apply_docs_s122_r2.py` asserts the restored file equals `git show c5430071:v2/docs/CONOPS.md` byte for byte
  (sha256/16 `6cb7b241cb84d729`) and that the needs table is unchanged;
* **keeps the current circuit where the rule's own dependency list says**:
  * `feasibility/EMCON.md` gains **section 0a.1**: CONOPS 4b's table and the EMCON row's cells as `7a9f7b5b` wrote them
    (the text of `records/int13/apply_conops_4b_set12.py`, which the script checks is what `7a9f7b5b` committed),
    re-asserted on set 13's netlists;
  * `handover/DEFINITION-STATUS.md` gains the section "Current values of CONOPS's circuit passages (stream s122,
    29 September 2026)" and a row in its dependency table. It states that CONOPS's circuit passages and their "as
    generated" remarks are baseline values, and names where each current value is kept: DC-01 EMCON (EMCON.md 0a.1),
    DC-02 HOT-R1 (board E `Q11`, `HOT_R1_G` on `U10` pin 30, `R58`, `BLK_SPARE` at `J_BLK` pin 12; board A `J_DOCK`
    pin 12, `R216`, `U27` pin 18; REQ-077 INCONCLUSIVE, waiting on S-58), DC-03 the TX lamp (it needs the panel
    controller: `D3` from `LED_RAIL`, `Q1`'s drain, which only `Q2` turns on from `PANEL_PWM`), DC-04 the device rails
    (`U7` on A, `U25` on B), DC-05 a loss of `+3V3_DEV`, DC-06 generator line numbers; since round 3 DC-07 the
    supervisors' I2C status path, DC-08 the fabric's break-before-make and back-power gating, DC-09 board A's CC array.
* **reads CONOPS through the status page**: a CONOPS sentence whose value differs from the netlists, or that cites a
  generator line, is **BASELINE** when a DC row keeps its current value, and **STALE** when none does. The status
  page's section and EMCON.md 0a.1 are judged directly.

## Files

| File | What it is |
|---|---|
| `s122lib.py` | the parser, the name finder and `SCOPE`; reads the six netlists with `tx_inhibit.parse_netlist`; `S122_AT=<commit>` reads the documents (not the netlists) at a commit |
| `inventory.py` | writes `inventory.out` |
| `judgements.py` | the stream's judgement of each sentence, keyed by its digest, with its assertions |
| `verdicts.py` | looks up every named part, reads every cited generator line, evaluates every assertion and every stated count of parts, applies the baseline rule and the absent rule, writes `verdicts.out` |
| `sweep_absent.py` | counts the CONOPS.md sentences of a `verdicts.out` (the working file, a path, or the file at a revision) that state something absent or owed (the wordings of `s122lib.ABSENT`), by verdict |
| `inventory-base.out`, `verdicts-base.out` | the base's documents at `e57a7365` (run with `S122_AT=e57a7365`), judged on the committed netlists |
| `inventory-set14.out`, `verdicts-set14.out` | set 14's documents at `1bafab8c` (run with `S122_AT=1bafab8c`), judged by the current tools |
| `verdicts-r4.out` | round 4's documents at `edead832` (run with `S122_AT=edead832`), judged by the current tools |
| `verdicts-r5.out` | round 5's documents at `a6429e66` (run with `S122_AT=a6429e66`), judged by the current tools |
| `verdicts-r6.out` | round 6's documents at `1c187977` (run with `S122_AT=1c187977`), judged by the current tools |
| `inventory.out`, `verdicts.out` | the documents as they stand: 1011 sentences, 0 STALE, 0 UNJUDGED |
| `apply_docs_s122.py` | round 1's 43 passages (on this branch in `51952c0c`; refuses a second run) |
| `apply_docs_s122_r2.py` | round 2: the CONOPS restore, EMCON.md 0a.1, the status page's section, 16 passages; 497 assertions held first (on this branch in `29acd948`) |
| `apply_docs_s122_r3.py` | round 3: the status page's rows DC-07 to DC-09, the notes of DC-03 and DC-04 and the section's lead, the baselines table's `c5430071` file, the EMCON citations of PANEL.md and V2-SPEC.md and V2-SPEC.md's correction 33; 144 assertions held first; refuses a second run |
| `apply_docs_s122_r4.py` | round 4: V2-SPEC.md lines 47, 82, 84 and 86 and correction 34, OPERATING-ENVELOPE.md's two rows and note, row DC-10, the int15 docstring; 51 assertions held first; refuses a second run |
| `apply_docs_s122_r5.py` | round 5: V2-SPEC.md lines 81, 83, 84 and 86 and correction 35; 33 assertions held first; refuses a second run |
| `apply_docs_s122_r6.py` | round 6: V2-SPEC.md line 47 and correction 36, after reading that V2-SPEC.md is not a baseline; 9 assertions held first; refuses a second run |
| `apply_docs_s122_r7.py` | round 7: correction 36's wording (figures with a unit and spelled counts), after reading that V2-SPEC.md is not a baseline; refuses a second run |
| `apply_docs_s122_r8.py` | round 8: correction 36 compares a unit only where the source states one; refuses a second run |
| `test_close_s122.py` | rounds 6 and 7: the gate's fixture and mutation tests (T1 to T5); writes nothing |
| `checks/` | the filed independent checks, `check-s122-1.md` to `check-s122-7.md` (rounds 1 to 7) |
| `apply_registry_s122.py` | rounds 1 to 3's registry script (run at set 14, `9eaf406f`; refuses since) |
| `apply_registry_s122_r4.py` | for the integrator: the rebinds for rounds 4 to 7 (re-issued in rounds 5 to 7 for their diffs), CFL-016's entry and note, S-122's title sentence, the envelope re-pin, and the follow-up item (round 7) |
| `close_s122.py` | S-122's closure, for the integrator, last |
| `LOG.md` | the stream's log |

## Scope (`s122lib.SCOPE`) and the finder

PANEL.md sections 1, 2, 3, 5, 6, 7, 9 and 10; CONOPS.md sections 2a, M2, M4, **4 with 4a to 4f** (round 2: every row of
section 4, and 4c and 4d, which the check showed are subsections of section 4), and 5; V2-SPEC.md and TEST-PLAN.md
whole; OPERATING-ENVELOPE.md sections 2 to 4; ASSEMBLY.md **sections 2** (every step since round 2), 4, 8 and 9;
decisions 28 and 40; EMCON.md section 0a.1 and the status page's new section; and, since round 3, every sentence of
CONOPS.md in any section that states something absent, owed, not drawn or not connected (18 sentences). Not read:
PANEL.md's head and sections 4, 8 and 11; CONOPS.md's other sections but for those sentences; OPERATING-ENVELOPE.md
sections 1 and 5 to 8; ASSEMBLY.md's other sections.

A sentence is inventoried when it names a part designator, a net, a board, a rail, a gate function, a generator line,
**EMCON**, or a **spelled count of parts** (round 2). The count rule: a sentence that states a count of parts (two to
twenty LEDs, pins, sockets, cards and the like) is UNJUDGED until each count is covered. Round 3 (check-s122-2 m8: two
excuses named the wrong count, and the script did not read them) makes the cover checkable: with one count, a count
assertion of the same number or a reason; with several, `counts_ok` maps each count phrase to a reason that names what
the phrase counts (its noun), or to `asserted: <assertion>`, one of the judgement's own count assertions whose number
is the phrase's. V2-SPEC.md line 41's two SIM holders are now `asserted: B:#ref~J_SIM=2`, ASSEMBLY.md line 92's two
headset jacks `asserted: C:#ref~J_HSJ=2`.

The parser (round 3, check-s122-2 m7) keeps a wrapped list item's indented continuation lines with the item, so a
sentence across them is judged whole; the merged items were judged again (CONOPS.md section 4d's four steps, V2-SPEC.md's
corrections, OPERATING-ENVELOPE.md section 4's two items).

**The absent rule (round 3, check-s122-2 B1).** A CONOPS.md statement that the supervisors' I2C status path is "absent
as generated" was judged NOT DERIVABLE and had no row, while the netlists carry the path since `458b2873`. Now every
sentence of CONOPS.md that states something absent, owed, not drawn or not connected is inventoried, in any section, and
judged against the netlists, TRUE or BASELINE. A NOT DERIVABLE judgement of such a sentence must bind each of those words
to a phrase quoted from the sentence that is not about the generated circuit (`absent_ok`); otherwise the sentence is
UNJUDGED and the closure refuses. `sweep_absent.py` counts them:

| `verdicts.out` | CONOPS.md sentences with the words | TRUE | STALE | BASELINE | NOT DERIVABLE | UNJUDGED |
|---|---|---|---|---|---|---|
| before the re-sweep (`83cb0640`) | 14 | 1 | 0 | 7 | 6 | 0 |
| after (this commit) | 18 | 3 | 0 | 11 | 4 | 0 |

The four added are outside round 2's scope (section 2's need, section 7's D-17 row, section 7a's BANK-R1 and HOT-R1
rows). The four NOT DERIVABLE bind "absent" in section 2's need (the setting the kit serves), "owed" in section 2a (a
case measurement), in section 4's charger cell (a bench confirmation) and in section 4e's reading date. The inventory takes every
such sentence of the file, in any section.

## What the verdicts mean

* **TRUE**: judged true on reading, and every check `verdicts.py` runs holds (every named part is on a netlisted board,
  every cited generator line holds a named part at the commit it is dated to, every assertion and every stated count).
  What a TRUE sentence says beyond the netlists is named in its judgement and not judged.
* **STALE**: the netlists or generators no longer carry it.
* **BASELINE**: a CONOPS passage whose value is the baseline's, its current value kept in a DC row of the status page;
  its assertions, which state the current value, must hold, or it is STALE (round 3).
* **NOT DERIVABLE**: HISTORY (a dated record), FIRMWARE, HELD DOCUMENT, TEST, CASE or LEAD; left as it stands.
* **UNJUDGED**: no judgement, a count not covered, or an absent statement judged NOT DERIVABLE without its phrase
  bound; the closure refuses on any.

## Counts per document

| Document | Base (`e57a7365`): sentences | STALE | Set 14 (`1bafab8c`): sentences | STALE | Round 4 (`edead832`): STALE | Round 5 (`a6429e66`): STALE | Round 6 (`1c187977`): STALE | After: sentences | TRUE | STALE | BASELINE | NOT DERIVABLE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PANEL.md | 164 | 10 | 167 | 0 | 0 | 0 | 0 | 167 | 131 | 0 | 0 | 36 |
| CONOPS.md | 290 | 31 | 288 | 1 | 0 | 0 | 0 | 288 | 51 | 0 | 40 | 197 |
| V2-SPEC.md | 140 | 11 | 149 | 6 | 5 | 1 | 0 | 159 | 64 | 0 | 0 | 95 |
| OPERATING-ENVELOPE.md | 64 | 7 | 64 | 3 | 0 | 0 | 0 | 67 | 22 | 0 | 0 | 45 |
| TEST-PLAN.md | 110 | 2 | 110 | 0 | 0 | 0 | 0 | 110 | 18 | 0 | 0 | 92 |
| ASSEMBLY.md | 160 | 13 | 160 | 0 | 0 | 0 | 0 | 160 | 91 | 0 | 0 | 69 |
| decisions 28 and 40 | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 10 | 6 | 0 | 0 | 4 |
| EMCON.md 0a.1 | 0 | 0 | 26 | 0 | 0 | 0 | 0 | 26 | 22 | 0 | 0 | 4 |
| DEFINITION-STATUS.md (the section) | 0 | 0 | 22 | 0 | 0 | 0 | 0 | 24 | 17 | 0 | 0 | 7 |
| total | 938 | 74 | 996 | 10 | 5 | 1 | 0 | 1011 | 422 | 0 | 40 | 549 |

Every file is judged by round 7's tools (0 UNJUDGED in each). 3340 assertions are evaluated after. Before round 7 the
committed `verdicts.out` read 1004 sentences, 422 TRUE, 0 STALE, 40 BASELINE, 542 NOT DERIVABLE, 3338 assertions; the
seven sentences more are those the finder's maker rule now reads (round 7, m4). Before round 6, 1005 sentences, 420
TRUE, 545 NOT DERIVABLE; before round 5, 985 sentences, 410 TRUE, 0 STALE, 40 BASELINE, 535 NOT DERIVABLE; before round
4, 862, 339 TRUE, 0 STALE, 38 BASELINE, 485 NOT DERIVABLE. The 40 BASELINE sentences of CONOPS point to DC-01 (11),
DC-02 (8), DC-03 (1), DC-04 (1), DC-05 (1), DC-06 (14), DC-07 and DC-08 (the same 2), DC-09 (1) and DC-10 (1). The
absent sweep reads 51 CONOPS sentences, 16 TRUE, 18 BASELINE, 17 NOT DERIVABLE.

## The check's items (check-s122-1)

| Item | Answer |
|---|---|
| B1 (CONOPS section 4 and 4c say HOT-R1 is owed, 4f says drawn) | the baseline rule: 4f's round 1 edit withdrawn with the restore; lines 311, 312, 4c's HOT-R1 passages and 4f are BASELINE on DC-02, which carries HOT-R1 as drawn and REQ-077's reading, asserted on the netlists and the registry |
| B2 (ASSEMBLY section 9's counts) | lines 87, 217, 218 and 219 corrected with count assertions (17 Mill-Max 0858 pins by footprint, two E-key card sockets, 17 LEDs on `LED_D3.0mm`); the count rule stops a count from passing unasserted again |
| B3 (CONOPS 4e: the TX lamp acts without the controller) | its TRUE withdrawn; BASELINE on DC-03, which states the lamp needs the controller, asserted on board C (`R36`, `Q1`, `R17`, `Q2`, `R19`, `R20`) |
| m1 (4b's preamble overstates the script) | the preamble is withdrawn with the restore; EMCON.md 0a.1 says what `apply_docs_s122_r2.py` asserted, and its list covers `U214`/`U314`'s inputs, `U547` to `U550`'s inputs, `U540` to `U542`'s inputs and supply, and the QMX's USB supply (`F3` from `+5V_DEV`) |
| m2 (OPERATING-ENVELOPE.md dropped the PA bias) | restored: "a hardware line on every transmitter and on the PA's rail and bias", with board D's `U15` on `PA_KEY` asserted |
| m3 (CONOPS 4e header) | withdrawn with the restore |
| m4 (ASSEMBLY line 204's short citation) | dated at `e57a7365` |
| m5 (ASSEMBLY line 180 omits `J_VN1` to `J_VN4`) | added |
| m6 (PANEL line 156's "SPI lines") | "TXEN, RXEN, NRST, MOSI, SCK and NSS", MISO through `U553` |
| m7 (V2-SPEC lines 81 and 82 judged HISTORY) | judged STALE at the base and corrected (the TPS55288 had left before 7 September, `gen_sch_a.py:267` at `c5de605d`; the supervisors read H743 and CON-017 reads PASS); round 2 also found line 30's "five-port" switch chip (the KSZ9897R is seven-port) |
| m8 (correction 32 under the 27 September heading) | under its own "Corrections, 29 September 2026"; line 3 names it |
| m9 (rebind reasons not record specific) | each entry now names which parts and nets of the changed sentences the record's own text names |
| m10 (a staged check closes S-122) | the closure compares the check with HEAD's blob; the replay refused a staged fixture |
| m11 (the closure's 605 are SCOPE's) | the closure's entries say "in the scope s122lib.SCOPE sets" and name what is outside it |
| m12 (the finder leaves in-scope sentences out) | EMCON and counts of parts added; the sentence CFL-016 names in TEST-PLAN.md (line 54) is inventoried now. Not added: transmitter, radio, lamp and supply as keywords; the check says of the 155 sentences with those words that it "found no further stale statement" |

## The check's items (check-s122-2)

| Item | Answer |
|---|---|
| B1 (the supervisors' I2C status path "absent as generated", CONOPS lines 310 and 490 to 492, NOT DERIVABLE with no row) | row DC-07: `U41`, `U51`, `U61` pin 93 (PB7) on `SDA` and pin 92 (PB6) on `SCL` since `458b2873` (both unconnected at its parent `1f614233`), at `45bde541`, at `95e078a1` where the passages were written, and at `c5430071`; the TCA9517A segment of SC-HF-02 is what is owed. Row DC-08 for the clauses beside it: the break-before-make of FAB-03 and the back-power gating of FAB-02 (b) and (c) (`U513` to `U520`, `U530` to `U535`) are drawn since board B's round 8, present at `95e078a1` and `c5430071`, absent at `45bde541`; S-42 OPEN, CON-003 and CON-022 INCONCLUSIVE waiting on it. Both sentences BASELINE on DC-07 and DC-08. The absent rule, and the sweep above, which added DC-09 (D-17's CC array, `U31`, drawn since `458b2873`) and section 7a's HOT-R1 row to DC-02 |
| m1 (PANEL.md line 156 cites CONOPS 4b) | cites `feasibility/EMCON.md` section 0a.1, which the script asserts names `U540`, `R536` and `R537` |
| m2 (V2-SPEC.md line 24 cites CONOPS 4b) | cites EMCON.md section 0a.1; V2-SPEC.md's correction 33 records it |
| m3 (DC-03 and DC-04 were wrong at the baseline's reading) | both rows say so, asserted at `45bde541` and `a9f212c7`; the section's lead says what such a note means |
| m4 (the baselines table lacks `c5430071`'s file) | `6cb7b241cb84d729` at `c5430071` added to CONOPS's row |
| m5 (495, not 497) | the judgement and this README say 497 |
| m6 (the README cited commits of `fnd/s122`) | this branch's `51952c0c` and `29acd948` |
| m7 (wrapped list items split) | the parser keeps continuation lines; the merged items judged again |
| m8 (two count excuses name the wrong count; `counts_ok` not checked) | the count rule above checks each cover |

## Set 13 (main `32f26b41`, milestone `b874b744`)

Board C's netlist is `c9f7394594201045`: `R53` to `R56` (27R) put `U3`'s GPIO 2 to 5 on `EPD_SCL_R`, `EPD_SDA_R`,
`EPD_DC_R` and `EPD_CS_R`. PANEL.md section 3's two rows are corrected, and line 180's provenance names set 13's
netlists. The promoted registry carries S-122's set 13 addition, with its closing clause (the rows re-derived like the EMCON
statements), and S-123.

## The scripts for the integrator, and what they assert

* `apply_registry_s122.py`:
  * rebinds the 20 records bound to the seven changed documents (PANEL.md, CONOPS.md, V2-SPEC.md,
    OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, EMCON.md), CONOPS.md to `c5430071`'s `6cb7b241cb84d729`;
  * gives each rebind a reason read from the diff, from the sentence sets and the two verdict files, and from the
    record's own text;
  * moves the needs pin to `c5430071`'s full sha after asserting the diff starts after the needs table;
  * appends three CFL-016 entries: the inventory (rounds 2 and 3, with the absent sweep in its scope), the baseline
    rule with round 3's absent rule, and check-int13-4's n1 and n2;
  * appends n3 and n4 to S-122's title;
  * re-pins the envelope and ENV-001 after asserting no envelope number left OPERATING-ENVELOPE.md;
  * asserts every other record and item unchanged, re-parses, and refuses a second run.
* `apply_registry_s122_r4.py` (round 4, re-issued in rounds 5 and 6; after `apply_registry_s122.py`, which has run at set 14):
  * rebinds the records bound to V2-SPEC.md (REQ-005, CFL-010, CFL-013, CFL-016), OPERATING-ENVELOPE.md (CFL-014,
    CFL-016) and DEFINITION-STATUS.md (CFL-016) at their set 14 shas, each reason read from the diff against
    `1bafab8c`, the sentence sets, `verdicts-set14.out` and `verdicts.out`, and the record's own text;
  * appends CFL-016's round 4 inventory entry (the finder, the judgement, the counts it reads, the corrections) and a
    sentence to its `notes` (m7); appends one sentence to S-122's title stating what the gate checks since round 4 (q1);
  * re-pins the envelope and ENV-001 after asserting no envelope number left OPERATING-ENVELOPE.md and the diff stays in
    section 2; CONOPS.md is unchanged, so the needs pin does not move;
  * asserts every other record and item unchanged, re-parses, and refuses a second run.
* `close_s122.py <check>`, its gate (`gate_set14`, rewritten in round 4):
  * (a) probes the finder with the five part numbers check-int15-1 found and ten made up at run time in five shapes,
    and with five made-up non-parts it must not read;
  * (b) finds the corrected sentences by what they say ("<part> display switch", "<part> codec", "<part> hot swap",
    "<part> hot-swap controller", "<part> M.2 B-key socket" in V2-SPEC.md and OPERATING-ENVELOPE.md outside their
    correction notes), and needs each to name the generated part, be TRUE and not HISTORY, and assert that part on its
    board; it refuses the TMDS341A, the WM8960, a TRACO part or the MDT420B there, and the LM5176 in a dock strip
    sentence other than as A22's;
  * since round 5 also the rows round 5 corrected ("<part> gate-bias", "<part> buck on slots 1 and 3", "<part> stages
    on slot 2 and the device rail", "<n> LEDs under light guides"), no dock strip sentence with a magnetometer outside
    the pod, and neither of check-s122-4's two role phrasings; the probe of (a) also takes the netlists' semiconductor
    part numbers;
  * (c) needs the check to carry the heading "## S-122 closing check" and under it each such sentence by its document
    and line; on this commit those are V2-SPEC.md lines 47, 81, 82, 83, 84 and 86 and OPERATING-ENVELOPE.md lines 77
    and 83;
  * (d) needs the check to name check-int15-1 and to have been committed on a line that carries `097d2517`;
  * (e) the role rule's tests: check-s122-4's two sentences as they stood at `edead832`, judged TRUE with the check's
    own reading, must be refused by `verdicts.check_roles` and must not read TRUE; since round 6 the fourteen mutants
    of the rows as they stand must read STALE, and line 47 with the 1 W planted back must be refused by (b) and by
    (f)'s scan alone;
  * (f) since round 6, the scan of every figure-and-unit token on the closing list's lines (above);
  * since round 6 (b) also needs "SA868 <n> W" to name 2 W, with `U2`'s assertion;
* and then, as before:
  * checks the rebinds of both registry scripts are in and current;
  * re-runs the inventory and verdicts, and needs 0 STALE and 0 UNJUDGED, identical to the committed outputs;
  * needs CFL-016's baseline entry, the status page's rows, and sentences judged in EMCON.md and DEFINITION-STATUS.md;
    the absent rule holds through its 0 UNJUDGED;
  * needs the check committed at HEAD, starting `mergeable: yes`, and naming every document and `verdicts.out`;
  * then closes S-122 and sets CFL-016 to PASS.
* **Round 7, replayed on two throwaway clones (deleted after):**
  * of the tip `c3490c9b`: the nine outputs reproduce byte for byte (`inventory.out`, `verdicts.out`, `-base` at
    `e57a7365`, `-set14` at `1bafab8c`, `verdicts-r4.out` at `edead832`, `verdicts-r5.out` at `a6429e66`,
    `verdicts-r6.out` at `1c187977`); `apply_docs_s122_r7.py` refuses on the tip, with V2-SPEC.md checked out from
    `1c187977` writes 1 edit and the file equals the tip, and a second run refuses; `test_close_s122.py` ALL PASS;
  * of `fnd/int16` at `36bb1d12` (set 15; S-125 open, CFL-016 FAIL waiting on S-122), with int16's ignored files
    installed from its worktree and `43b5a25c` merged with no conflict: `apply_registry_s122_r4.py` rebound 5 records
    (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005), opened S-126 (the highest S number there was S-125) with disposition
    PROCESS and no record waiting on it, re-pinned the envelope and ENV-001, and refused a second run; `rules_lib.py
    requirements` 144 records, 0 errors, 0 warnings; `rules_render.py --requirements`; `rules_status.py` (gate state
    NOT_READY: 39 FAIL, 104 INCONCLUSIVE, 195 PASS of 338) and the full `rules_render.py`, which moved
    CURRENT-EVIDENCE.md from `c9b98931` to `0f2c59cb` and the seven status pages, after which `rules_lib.py
    requirements` read 0 errors and 2 warnings, CON-010 and REQ-044; `inventory.py` and `verdicts.py` re-run (their
    header line moved, 1011 sentences, 0 STALE, 0 UNJUDGED) and committed with the registry and the pages; a fixture
    check (not filed; the marker and the eight lines) refused while only staged, then committed; `test_close_s122.py`
    ALL PASS; `close_s122.py` closed S-122 (CFL-016 PASS, its waits_on dropped; the closing evidence names S-126 and
    the apply scripts to `_r6.py`, not `_r7.py`, which round 8 corrects, check-s122-7 m2; S-123 to S-126 still open)
    and refused a second run; after it
    `rules_lib.py requirements` 0 errors and the same 2 warnings, `rules_lib.py` 59 rules and 0 errors, the tests 72
    passed after the trace page's render, `claims_check` PASS, 91 of 91.
  * The first run of that sequence, on `c3490c9b`, refused at the registry script: its screen reads a standard's
    number ("MIL-STD-461") as a claim word, and the follow-up item's title named the EMC test methods by it.
    `43b5a25c` names them without it.
* **Round 6, replayed on a throwaway clone of `19bddf75` (deleted after):**
  * the eight outputs reproduce byte for byte (`inventory.out`, `verdicts.out`, `-base` at `e57a7365`, `-set14` at
    `1bafab8c`, `verdicts-r4.out` at `edead832`, `verdicts-r5.out` at `a6429e66`);
  * `apply_docs_s122_r6.py` refuses on the tip; with V2-SPEC.md checked out from `a6429e66` it reads V2-SPEC.md outside
    the baselines, writes 2 edits after 9 assertions and the tree equals the tip; a second run refuses;
  * `apply_registry_s122_r4.py` rebound 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005) and refused a second
    run; `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings; `rules_lib.py`: 59 rules, 0 errors;
    `test_envelope_data` with `test_requirements`: 69 passed and 2 failed (the trace page) before
    `rules_render.py --requirements`, 71 passed after;
  * with a fixture check committed (not filed; the marker and the eight lines), the closure refused nine mutants of
    the files: line 47 with the 1 W planted back, its judgement moved to the new text and the outputs regenerated (at
    (b), STALE) and without a judgement (UNJUDGED); the forward test off (at (e), the TPA6132A2 named a codec reads
    TRUE); the check's "(AP64500, EMCON gated)" on line 81 with its judgement moved (STALE); OPERATING-ENVELOPE.md
    line 83 at -40 to +85 C with its judgement moved (at (f), no assertion covers it); line 47's judgement without its
    `figures_ok` (at (f), 2 W and 30 W uncovered); line 86's twelve float clamps and line 82's 330 x 210 mm with their
    judgements moved (STALE); the rails test off (at (e), round 5's A22 fixture);
  * `test_close_s122.py`: ALL PASS; the closure refused the fixture while only staged, closed S-122 with it committed
    (1004 sentences, 0 STALE, 0 UNJUDGED; CFL-016 PASS; the closing evidence names `apply_docs_s122_r5.py` and
    `apply_docs_s122_r6.py`; S-42, S-123 and S-124 still open) and refused a second run; after it
    `rules_lib.py requirements` 0 errors, the tests 72 passed, `claims_check` PASS, 91 of 91.
  * `rules_render.py --check` reads `PCB-ETA.md` out of date on the branch and on the clone alike, a page this stream
    does not touch; the replay rendered only the trace page.
* **Round 5, replayed on a throwaway clone of `8d7874f5` (deleted after):**
  * the seven outputs reproduce byte for byte (`inventory.out`, `verdicts.out`, `-base` at `e57a7365`, `-set14` at
    `1bafab8c`, `verdicts-r4.out` at `edead832`);
  * `apply_docs_s122_r5.py` refuses on the tip; with V2-SPEC.md checked out from `edead832` it writes 5 edits after 33
    assertions and the tree equals the tip byte for byte; a second run refuses;
  * the gate refused: round 4's finder (at the netlists' SMCJ18A); the role rule switched off (condition (e), the D8
    fixture); V2-SPEC.md as at `edead832`; the TPS22810 gate-bias switch put back; the AP64500 list put back; the
    magnetometer put back; sixteen LEDs put back; a check whose closing section leaves out line 81;
  * `apply_registry_s122_r4.py` rebound 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005) and refused a second
    run; `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings; `rules_lib.py`: 59 rules, 0 errors;
  * `test_envelope_data` with `test_requirements`: 69 passed and 2 failed (the trace page) before
    `rules_render.py --requirements`, 71 passed after;
  * the closure refused the fixture while only staged, closed S-122 with it committed (not filed; the marker and the
    eight lines; 1005 sentences, 0 STALE, 0 UNJUDGED; CFL-016 PASS; S-42, S-123 and S-124 still open) and refused a
    second run; after it `rules_lib.py requirements` 0 errors, the tests 71 passed, `claims_check` PASS, 91 of 91.
* **Round 4, replayed on a throwaway clone of `e5fdf670` (deleted after):**
  * the six outputs reproduce byte for byte (`inventory.out` and `verdicts.out`; `-base` with `S122_AT=e57a7365`;
    `-set14` with `S122_AT=1bafab8c`);
  * `apply_docs_s122_r4.py` refuses on the tip; with the four files checked out from `1bafab8c` it writes 12 edits
    after 51 assertions and the tree equals the tip byte for byte; a second run refuses;
  * the gate refused: a finder rigged to know only check-int15-1's five part numbers (at a part number made up at run
    time); V2-SPEC.md and OPERATING-ENVELOPE.md put back to `1bafab8c` (line 47 still names the WM8960); the B16 row
    relabelled "B16 (compute)" with "TMDS351" in place of the TS3DV642 (named, not the generated part); the E6 row with
    "the LM5176 9 to 36 V front end, all under A22" (the LM5176 in a dock strip sentence other than as A22's); line 47
    with a WM8731 codec; the B-key row naming a Molex socket (no corrected sentence stands); a TRACO TEN 60 row; the
    B16 row judged HISTORY (not TRUE); the B16 row TRUE without its U3 and U4 assertions; a check without the marker;
  * `apply_registry_s122_r4.py` rebound 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005), wrote CFL-016's entry
    and note and S-122's sentence, re-pinned the envelope and ENV-001 to `26e98ecfd2e4ec2f`, and refused a second run;
    `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings; `rules_lib.py`: 59 rules, 0 errors;
  * `test_envelope_data` with `test_requirements`: 69 passed and 2 failed (the trace page) before
    `rules_render.py --requirements`, 71 passed after;
  * the closure refused the fixture while only staged (its provenance), closed S-122 with it committed (not filed; the
    marker and the six lines; 985 sentences, 0 STALE, 0 UNJUDGED; CFL-016 PASS; S-42, S-123 and S-124 still open) and
    refused a second run; after it `rules_lib.py requirements` 0 errors, the tests 71 passed, `claims_check` PASS, 91
    of 91.
* **Round 3, replayed on a throwaway clone of `89b9ac6b` (deleted after):**
  * the four outputs reproduce byte for byte, the base's with `S122_AT=e57a7365`;
  * `apply_docs_s122_r3.py` refuses on the tip; with PANEL.md, V2-SPEC.md and DEFINITION-STATUS.md checked out from
    `83cb0640` it writes 10 edits after 144 assertions and the tree equals the tip byte for byte; a second run refuses;
  * `apply_docs_s122_r2.py --check` with round 1's documents (`1594090e`): 16 edits, 497 assertions;
  * the registry script rebinds 20 records, writes CFL-016's entries with rows DC-01 to DC-09 and the absent rule, and
    refuses a second run; `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings; `rules_lib.py`: 59 rules,
    0 errors;
  * `test_envelope_data` with `test_requirements`: 69 passed and 2 failed (the trace page) before
    `rules_render.py --requirements`, 71 passed after;
  * the closure refused the fixture while only staged, closed S-122 with it committed (not filed; 862 sentences,
    0 STALE, 0 UNJUDGED; CFL-016 PASS; S-123 and S-42 still open) and refused a second run; after it
    `rules_lib.py requirements` 0 errors, the tests 71 passed, `claims_check` PASS, 91 of 91.
* **Replayed on a scratch clone of `53292087` (round 2), and again of `ede23557` on the promoted set 13 with the same results:**
  * the four outputs reproduce byte for byte;
  * `apply_docs_s122_r2.py` refuses a second run;
  * the registry script rebinds 20 records and refuses a second run;
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors;
  * `test_envelope_data`: 6 passed. `test_requirements`: 63 passed and 2 failed before `rules_render.py --requirements`, 65 passed after;
  * the closure refused a staged fixture and a fixture naming neither EMCON.md nor DEFINITION-STATUS.md, closed with a
    committed fixture (not filed), and refused a second run;
  * after it, `rules_lib.py requirements`: 0 errors. `test_requirements` with `test_envelope_data`: 71 passed. `claims_check`: PASS, 91 of 91.

## Integrator's run order

1. Merge `fnd/s122c` (from `1bafab8c`, set 14's line, where `apply_registry_s122.py` has run).
2. `python3 v2/docs/records/s122/apply_registry_s122_r4.py`
3. `rules_render.py --requirements`; `rules_status.py` and `rules_render.py` for the envelope pin (ENV-001's `verified_sha`, the PCB-RULE-STATUS pages, LAYER-STATUS).
4. An independent check filed under `v2/docs/records/s122/checks/` and committed. It must start `mergeable: yes`, name
   check-int15-1, PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, pcb_decisions.yaml,
   EMCON.md, DEFINITION-STATUS.md and `verdicts.out`, and carry the heading `## S-122 closing check` under which it names
   V2-SPEC.md line 47, V2-SPEC.md line 81, V2-SPEC.md line 82, V2-SPEC.md line 83, V2-SPEC.md line 84, V2-SPEC.md line
   86, OPERATING-ENVELOPE.md line 77 and OPERATING-ENVELOPE.md line 83 (the gate prints the list if a line moves), in
   its own words.
5. `python3 v2/docs/records/s122/test_close_s122.py` (it must end `ALL PASS`), then
   `python3 v2/docs/records/s122/close_s122.py v2/docs/records/s122/checks/<the check>`
6. `rules_render.py --requirements` again.

If a document of the scope changes on main before step 5, re-run `inventory.py` and `verdicts.py`, judge the new text
in `judgements.py`, and commit the outputs, or the closure refuses.

**On set 15 (`fnd/int16`, tip `36bb1d12`), round 7 (check-s122-6 m5); round 8: review D (`fnd/reviewdc`, `4795d5bf`)
goes first, by its own run order (its `apply_findings.py` opens S-126 to S-134); its merge conflicts with `fnd/int16` in
`v2/vendor/sources.txt` only, resolved by keeping both sides; this stream's registry script then opens its follow-up
item as S-135:**
1. Merge `fnd/s122c`, then `python3 v2/docs/records/s122/apply_registry_s122_r4.py`: it rebinds the records bound to
   V2-SPEC.md, OPERATING-ENVELOPE.md and DEFINITION-STATUS.md, re-pins the envelope and ENV-001, and opens the follow-up
   item at the next free S number (it prints the number).
2. `rules_render.py --requirements`; then `rules_status.py` and the full `rules_render.py`. The full render moves
   `v2/docs/CURRENT-EVIDENCE.md` (in check-s122-6's reading, SGN-001's seven readings leave CURRENT_CANDIDATE after the
   registry and ENV-001 change), and `rules_lib.py requirements` then reads 0 errors and 2 warnings, CON-010 and
   REQ-044, which the integrator rebinds as usual.
3. Re-run `python3 v2/docs/records/s122/inventory.py` and `python3 v2/docs/records/s122/verdicts.py` and commit both:
   `pcb_decisions.yaml` is `823a6b32`'s file on set 15 (decision 59), so the outputs' header line moves; their bodies
   do not.
4. The filed check (step 4 above), then `test_close_s122.py` (ALL PASS) and `close_s122.py`.

## What stays open

* S-122 and CFL-016, until the check of step 4 and the closure of step 5.
* The follow-up item of the instrument's escape classes (round 7), disposition PROCESS, at the number the registry
  script allocates; no record waits on it.
* CONOPS.md's 38 BASELINE passages stay as baselined. Their current values live on the status page until a reopening of
  the definition decides otherwise. `feasibility/ZEROIZE.md`'s citation `CONOPS.md:404` (the check's observation) is
  outside the scope.
* CON-003 and CON-022 (corrected in round 4, check-s122-3 m3 and its section 5): CON-003's evidence entry 2 says
  "R480 and R500 still 100k" of the netlist "at `eadbe571`", and CON-022's entry 1 says FAB-02's "remedy (b) and (c) is
  not drawn"; in check-s122-3's words (its section 5) their later entries record the change (CON-003: "R480 to R500,
  R15 and R16 are 10 k"; CON-022's entry 5: (b) and (c) "are drawn"), so these are dated readings in chronological
  lists, not the records' current claims.
  On board B's netlist `3ef9b8c49a01b728` `R480` and `R500` read 10k and `U513` to `U520` are drawn (asserted in the
  judgement of row DC-08's cell). S-42 stays open; its title's terms are the gate's assertion and its mutation for
  each fix.
* check-s122-2's observations: EXECUTION-PLAN.md line 629 and `feasibility/ZEROIZE.md`'s CONOPS line citations are
  outside the scope.
* The finder is a token finder. A circuit sentence that names none of its tokens is outside the inventory; V2-SPEC.md
  line 35 was found that way in round 1.
