# Stream w5si: rule SI-001's edge rates as data, second pass (layer 9, MESHSAT-1357)

Written 27 September 2026, 23:40 CEST, on branch `fnd/w5si` from `c23c5e76`. Prototype design work: nothing here has
been built or measured. Every edge is a maker's figure, a standard's, or a bound stated with its derivation, and no
reading of this page is a PASS. The checks named here are the stream's own and an AI review of the first pass; none is
a qualified engineering review.

This is the record of the second and last pass of the loop. The first pass's record is kept as it was recovered
(`recovery/pass1-drafts/w5si-record.md`) and is superseded by this page wherever they differ. How the first pass was
rebuilt from its transcripts is `RECOVERY.md`. The instruction this stream answers is the third checkpoint review's:
"for undocumented signal edge rates, do not insert convenient values simply to turn SI-001 green. Record a justified
design bound or suitable model, its applicability and the verification still required. If the uncertainty decides
feasibility, keep that decision open."

## 1. The result in one table

SI-001 at the schematic phase, taken in scratch outside any tree. The denominator is the signal nets outside
LOW_SPEED_OR_DC, the class the rule asks no edge of. Netlists at `c23c5e76`; data file sha256/16 `bbeb1a47f7d8710b`.

| Board | Signal nets | Slow | Non-slow | Decided by a maker's figure | Decided by a bound | Undecided | Verdict |
|---|---|---|---|---|---|---|---|
| A | 290 | 170 | 120 | 7 | 75 | 38 | INCONCLUSIVE |
| B | 882 | 320 | 562 | 103 | 451 | 8 | INCONCLUSIVE |
| C | 134 | 97 | 37 | 4 | 29 | 4 | INCONCLUSIVE |
| D | 135 | 88 | 47 | 20 | 19 | 8 | INCONCLUSIVE |
| E | 82 | 41 | 41 | 4 | 37 | 0 | INCONCLUSIVE |
| P | 44 | 22 | 22 | 0 | 5 | 17 | INCONCLUSIVE |
| all | 1567 | 738 | 829 | 138 | 616 | 75 | |

Each row sums: non-slow = maker's figure + bound + undecided (120 = 7 + 75 + 38, and so on; 829 = 138 + 616 + 75).

Of the decided nets, what the netlist already answers and what is left to the layout:

| Board | Decided | Answered in the netlist | Layout-bound | of which held by a maker's figure | of which BOUND_DECIDES |
|---|---|---|---|---|---|
| A | 82 | 19 | 63 | 1 | 62 |
| B | 554 | 361 | 193 | 40 | 153 |
| C | 33 | 10 | 23 | 0 | 23 |
| D | 39 | 26 | 13 | 2 | 11 |
| E | 41 | 10 | 31 | 0 | 31 |
| P | 5 | 4 | 1 | 0 | 1 |
| all | 754 | 430 | 324 | 43 | 281 |

Each row sums: decided = answered + layout-bound, and layout-bound = maker-held + BOUND_DECIDES.

**Every board stays INCONCLUSIVE.** A board is INCONCLUSIVE while a net is undecided or layout-bound; on every board
at least one layout-bound net is decided by a bound. That is the reading, not a shortfall of the work: the makers of
those drivers publish no minimum edge, and a number written in their place would be this stream's.

The nets behind every figure, with the driver that governs each: `readings/si001-c23c5e76.txt`.

## 2. The same on set 6

The integration candidate `fnd/r8int6` (read at `73ae2f21`, NOT merged by this stream) regenerates every netlist. The
readings were taken in a scratch extract of that tree with this stream's tool, data file and test laid over it and
none of its drafts applied. Listing: `readings/si001-set6-73ae2f21.txt`.

| Board | Netlist sha256/16 at c23c5e76 | at set 6 | Non-slow (c23c5e76, set 6) | Maker's figure | Bound | Undecided (c23c5e76, set 6) | Layout-bound: maker-held + BOUND_DECIDES |
|---|---|---|---|---|---|---|---|
| A | da05dc02bc1e612f | 0a2b59087bcc2678 | 120, 120 | 7, 7 | 75, 75 | 38, 38 | 63 = 1 + 62, the same |
| B | 8b78c59754a6a0c7 | 028997a6c5e8810f | 562, 562 | 103, 103 | 451, 451 | 8, 8 | 193 = 40 + 153, the same |
| C | 11eabc2dddca5161 | 3fddbb3edcd4248a | 37, 37 | 4, 4 | 29, 29 | 4, 4 | 23 = 0 + 23, the same |
| D | 76700a687eb6187f | 7a2c0ac2190b141a | 47, 47 | 20, 20 | 19, 19 | 8, 8 | 13 = 2 + 11, the same |
| E | d6137f50059e5cbc | 56adc9746d61c4e0 | 41, 41 | 4, 4 | 37, 37 | 0, 0 | 31 = 0 + 31, the same |
| P | 085f833362fbbda8 | 760ac6f74d62d194 | 22, 20 | 0, 0 | 5, 5 | 17, 15 | 1 = 0 + 1, the same |
| all | | | 829, 827 | 138, 138 | 616, 616 | 75, 73 | 324 = 43 + 281, the same |

What set 6 moves: board B has 886 signal nets (324 slow) against 882 (320); board E 83 (42 slow) against 82 (41);
board P 40 (20 slow) against 44 (22), with 15 undecided against 17 (SCP_HTR and SEC_VDD are gone from its list). No
decided count moves and every reading is INCONCLUSIVE on both.

## 3. Before this stream, and the correction of the first pass's sentence

With the tool of `c23c5e76` (re-taken in scratch on 27 September 2026; it gives the six headlines the first pass
recorded, word for word): decided A 6, B 30, C 4, D 20, E 4, P 0, in all **64**; undecided 114, 532, 33, 27, 37, 22,
in all **765**; together the same 829 non-slow nets. The decided were the USB 2.0 lines only.

**The first pass's summary said "753 of the 765 nets that had no decided edge are now decided". That was wrong**, as
the independent check found. 753 was the TOTAL decided after the first pass, out of 829. Of the 765 nets that were
undecided before, 689 were decided after the first pass and 76 remained (75 with no signal-class declaration, and
board B's BOB). After this pass 690 of the 765 are decided and 75 remain: BOB now reads decided by a bound (section
6), and the 75 are the nets no declaration names.

## 4. What was built and changed

| File | What it is |
|---|---|
| `v2/ecad/tools/pcb_edge_rates.yaml` | THE DATA, a configuration input of the `edge_length` verdict. 7 interface records, 58 driver families, 32 far ends, 1 open-drain record. Its header holds the schema and the session decisions ER-D1 to ER-D15 |
| `v2/ecad/tools/ibis_read.py` | reads a maker's IBIS model per pin. Second pass: a model with no Model_type is UNKNOWN and never an input; `[Model Selector]` is read in both spellings; `fastest_cite` gives the keyword and the cell a record cites |
| `v2/ecad/tools/edge_length.py` | the schematic-phase reading. Second pass: the governing edge (`net_edge`), the counts and their sums, the check of every citation (sha256/16, page, words), the search listing, the open-drain rise, a passive switch's unnamed pin and a continued board's unnamed connector as reasons, the unasked parts named |
| `v2/ecad/tools/tests/test_edge_length.py` | 36 tests (18 before this stream, 28 after the first pass) |
| `v2/vendor/ti/ibis/*.ibs` (12), `v2/vendor/st/ibis/stm32h742_743_750_753_lqfp100.ibs` | the makers' models, fetched again; all 13 byte-identical to the first pass's (`RECOVERY.md`) |
| `v2/vendor/sources.txt`, `v2/vendor/vendor-status.txt` | 13 lines each |
| `v2/docs/records/w5si/` | this record, `RECOVERY.md`, two findings, their evidence, the readings, the tools that made them, the five drafts for the integrator (`apply/`), the first pass as recovered (`recovery/`) and its check (`check-1/`) |

## 5. How a net's edge is decided (the instrument)

1. A net whose signal-class entry an **interface record** covers takes its edge: the two USB 2.0 minimums (a
   standard's, so a published figure), and instantaneous bounds for board B's controlled links, the RF lines, the
   power-stage nodes, the oscillator nodes and BOB.
2. Otherwise every IC or module (`U...`) and transistor (`Q...`) on the net is asked for its **family**, by the part
   number at the start of its value field, never an order code. An IBIS family is read per pin. A pin the maker types
   as an input drives nothing. A part with no record leaves the net UNDECIDED, named.
3. A connector's pin takes the **far end**: a board of the set is read from its own netlist, pin by pin; a part beyond
   the set is a named family. A connector no record names leaves the net UNDECIDED, on the board that asks and on the
   board it continues onto.
4. A net takes the drivers **one series resistor away**, once.
5. **The governing edge is the fastest edge any driver on the net can produce (ER-D13).** A driver with no published
   minimum has no known fastest edge. One such driver makes the net `decided_by: BOUND`, whatever the makers of the
   other drivers publish; their figures are recorded beside it (`maker_edge_ns`) and decide nothing. A net is decided
   by a maker's figure only when every driver on it has one.
6. **What counts as a maker's figure:** a maker's IBIS model at its fastest corner, a minimum the maker prints in its
   own table, or a specification's minimum that the part's own datasheet claims. A typical or a maximum is refused
   when the data file is read. A bound is named a bound.
7. **Every citation is checked on every run:** the document is held, it is the file the record was read from
   (sha256/16), and the quoted words are on the page named. An IBIS record's keyword, cell and number must be the
   file's. A bound's documents must be in the search listing at their held sha256/16. A record that fails any of it
   decides nothing; a number its own model contradicts FAILs the reading.

## 6. The three blocking items of the independent check, answered

### 6.1 "Maker-held" nets whose governing edge is a bound

**Closed.** The tool implements the rule of step 5 above in `edge_length.net_edge`, and the records follow it.

- The first pass called 83 layout-bound nets maker-held. **40 of them carried a bound beside the maker's figure**, as
  the check counted. They are BOUND_DECIDES now. 43 remain held by a maker's figure on every driver: board A's
  INA_ALERT; board B's 24 STM32H743 outputs (the CAN lines, SEL?_A to C, WSEC_A to C), its 12 SN74LVC08A voter
  outputs, its 3 SN74LVC32A outputs BBM?_RA and KSZ_RST; board D's HUB_DM4 and HUB_DP4.
- BOUND_DECIDES went from 241 to 281 (241 + 40).
- **The 40, with the drivers that govern them:** on boards A, B, C and D the kit bus SCL (RP2040, the bus master, and
  the VEML7700), SDA (ATECC608B, BQ25731, RP2040, VEML7700) and EXP_INT (DS3231, KSZ9897R, TPS23861, RP2040): 12 nets;
  board A's PROCHOT (BQ25731); board B's and board C's HB1 to HB3 (a discrete FET's drain and the RP2040): 6; board
  B's BBM1 to BBM3 and their `_ARMR`, `_MOV` and `_REQ` nets (Nexperia 74LVC1G157, Diodes 74LVC1G17): 12; BSEL1 to
  BSEL3 (74LVC1G157): 3; the SWCLK and SWDIO of its three supervisors (a bench probe): 6.
- **The test the check asked for** is
  `t_si001_one_driver_with_no_published_minimum_makes_the_net_bound_decides_whatever_the_others_publish`: a net driven by a gate with a published figure (0.25 ns) and an MCU with none reads
  BOUND_DECIDES, critical length 0.0 mm, with the gate's figure recorded and the MCU named. Its mirror holds the other
  side, and `t_si001_the_counts_sum_on_every_committed_netlist` holds the sums on the six netlists.
- **ER-D12's reason is corrected** in the data file's header. It said the bound "changes a number in the table and no
  outcome". The number is the critical length handed to the layout, so it is an outcome.
- **The remedies the first pass proposed (its Q4 and Q5) do not close these nets**, as the check said: slowing the
  STM32H743 or putting a resistor at an LVC output leaves the unmodelled driver on the net. They are restated in
  section 10 with what would close each.

### 6.2 The draft that deleted four USB pair classes

**Closed.** `apply/apply_board_b_declarations.py` is rewritten to operate on the parsed structure. It loads
`gen_pcb_b3.py` with `ast`, locates the one module-level assignment to PATTERNS, replaces the class constant of three
tuples at the positions the parser gives, inserts one tuple, and puts its comment on lines of its own above the
statement. After patching it parses the file again and asserts that the evaluated PATTERNS is the old list with
exactly the intended changes: 40 entries become 41, and `("GNSS_D*", "USB")`, `("ZBA_D*", "USB")`,
`("ZBB_D*", "USB")` and `("RB_D*", "USB")` are there.

- The helper is `apply/_pyedit.py`. **Every draft of this stream that edits Python uses it**: that one and
  `apply/apply_rules_status_config_inputs.py`. The three that edit YAML or JSON compare the parsed structure before
  and after in the same way.
- `apply/selftest.py` applies the FIRST draft's replacement to a fixture, shows that it parses, differs and loses the
  four entries, and that the comparison refuses it; then runs the new draft on the same fixture. 11 checks, 0 failures.
- The first pass's four drafts are kept as recovered with the suffix `.superseded-do-not-run`, so none can be run by
  mistake.

### 6.3 BOB's class

**Closed as far as this stream may close it; the class itself is proposed to the integrator.** Finding
`F-BOB-common-mode-termination.md`.

- None of the four signal classes fits. LOW_SPEED_OR_DC is skipped by `return_via.py` and `ref_change.py`. The other
  three ask for an adjacent reference plane, and the maker of board B's switch says of the line side: "there should be
  no signal ground under the magnetics, connector, and the area in between" (Microchip DS00004151A 6.5, p. 12).
- So BOB **keeps the class it has** (CLOCKED_DIGITAL, which both return rules judge) and only its basis is corrected.
  W5SI-D2 is replaced.
- A class for the cable side of an isolation barrier is proposed with four rules: the return, the keep-out, the
  clearance, and no edge asked by SI-001. Its name and numbers are not this stream's to rule.
- SI-001 reads BOB through a bound of its own (interface record CABLE-SIDE-TERMINATION).
- Two side findings on the same port: the two PoE pairs have no common-mode termination drawn (F-BOB-2, a circuit
  question for board B's author), and the termination returns to signal ground, which `GROUNDING-AND-SHIELDS.md`
  already records.

## 7. The open-drain I2C nets: physics before bounds

An open-drain net has two edges (ER-D14).

- **The fall** is set by the driver's pull-down. It is the figure every record states for an open-drain pin: an IBIS
  `dV/dt_f`, or a fall-time minimum the maker prints. For reflections it is the governing edge.
- **The rise** is set by the pull-up resistor charging the bus capacitance; no driver sets it. On the kit bus:
  T(30 to 70 percent) = 0.8473 x Rp x Cb (UM10204 Rev. 6, 7.1, p. 55) = 0.8473 x 1019 ohm x 174.3 pF = **150.5 ns**
  on SCL (152.2 ns on SDA), with Rp the drawn pull-ups at their low tolerance and Cb the pins at their makers'
  typical capacitance and the three ribbons, with no copper, which only adds (`records/hc5/
  kit_i2c_budget.round8-d.out.txt`). It is a MODEL, not a minimum, and it never governs. At k 6 on the slowest
  layer 150.5 ns is a length of 3.5 m, longer than any board.

**A specification's minimum.** UM10204 Rev. 6 (4 April 2014, held) states a minimum output fall time in Table 9
(p. 47), `tof`: Fast-mode and Fast-mode Plus, 20 ns x (VDD / 5.5 V), which is 12 ns at 3.3 V. Table 11 (p. 51) states
10 ns for Hs-mode. **Standard-mode states no minimum.** The DS3231's datasheet prints 20 + 0.1 Cb ns, the form this stream's brief
gives for earlier revisions of the specification; no earlier revision is held in this tree, so that attribution is
not checked here, and the DS3231's figure is taken from its own table. Such a figure is measured into a capacitive
bus load of 10 pF or more, not into a line, and each record says so.

It is a published figure only for a part whose own datasheet claims the specification's timing:

| Part on the kit bus | What its datasheet says | Its data pin's fall in the data file |
|---|---|---|
| KSZ9897R (B) | "The I2C interface timing adheres to the NXP I2C-Bus Specification (UM10204, Rev. 6) (high-speed mode and slower)", p. 172 | **10 ns, STANDARD**, the least of the modes the claim covers |
| DS3231SN (B) | its own table: "Fall Time of Both SDA and SCL", 20 + 0.1 Cb minimum, p. 4 | **20 ns, DATASHEET** |
| TPS23861 (B) | its own table: SDAO output fall time 21 ns minimum at Cb 10 pF, p. 11 | **21 ns, DATASHEET** |
| PCA9555 (A, B, C, D) | TI's IBIS model | 72.3 ns, IBIS |
| INA226 (A) | TI's IBIS model | 16.06 ns, IBIS |
| TMP117 (B) | TI's IBIS model | 7.68 ns, IBIS |
| ADS1115 (D) | TI's IBIS model, whose only SDA models are the high-speed ones | 0.786 ns, IBIS |
| STM32H743 (B, three) | ST's IBIS model, every speed setting admitted | 0.451 ns, IBIS |
| BQ25731 (A) | "I2C compatible"; SCL and SDA fall time 300 ns MAXIMUM, p. 18 | **bound** |
| ATECC608B (B) | input rise and fall only | **bound** |
| VEML7700 (C) | "compatible with I2C modes standard and fast"; its own table prints NO minimum fall | **bound** |
| RP2040 (C), the bus master | a slew bit and a drive field, no transition | **bound** |

SCL is driven by the master and by a target that stretches the clock. The clock pins of the BQ25731, KSZ9897R,
ATECC608B, DS3231 and TPS23861 are typed inputs from each maker's pin table, quoted with its page. The VEML7700's is
not, because its datasheet does not say input. **SCL and SDA stay decided by a bound on all four boards**: the master
publishes nothing.

## 8. The checker's minor list, item by item

| The check's item | What was done |
|---|---|
| The "753 of 765" sentence | corrected, section 3 |
| ER-D10's reason is wrong | corrected in the data file's header from `HW-FW-CONTRACT.md`: row FW-K02 holds the panel RP2040's GPIO0 and GPIO1 at the default 4 mA drive and slow slew, and row FW-B08 limits the STM32H743's PB6 and PB7 to I2C1 target duty. No figure changes: the RP2040 publishes no edge at either slew setting and FW-B08 fixes no OSPEEDR. FW-K02's sentence on the fall time is taken to Q5, section 10 |
| Families with no `inputs` count input pins as drivers | the clock inputs of five bus parts and the TPS23861's SDAI are typed, each with the maker's words and page (`inputs_cited`). Board A's SCL no longer names the BQ25731's input pin as its fastest driver |
| `ibis_read.py` fails open in two ways | both closed, with a test |
| A passive switch's pin that is neither through nor input is dropped | it is a reason now; each passive switch names its control inputs |
| SKY13351's through pattern matches net names | its pins are read by number |
| Relay K1, the SW_* switches and T1 are never asked | stated in every reading that has one: a note names the nets (board B's SWP4 pairs at T1, board D's RF lines at K1) and `unasked_part_nets` counts them. They are not asked: an instrument limit, section 11 |
| A connector leading off the set on a continued board gives no reason | it is a reason now. It found that TR_APRS had a far-end record for board C only; boards A, B and D have theirs |
| Only 6 of 13 IBIS families check the supply rail | all 13 do |
| The CONFIG_INPUTS draft names netlists by phase directory | kept, because the templates know only the judged board's phase, and said so in the draft; `--refresh` re-derives the entry when a phase moves |
| The decisions are recorded only in a header | `apply/apply_decisions_w5si.py` adds four rows to `pcb_decisions.yaml`, numbered from the next free number of the tree it runs in |
| The coverage draft moved the remediation to SESSION and PARALLEL_AGENT | it stays LAB and HARDWARE; the action text says which part is desk work. A request to Raspberry Pi for a model is outside contact and is the owner's |
| Many bounds quote only the part's name | `tools/edge_search.py` searched every document a bound cites for the words a transition time is written with; its listing is `readings/edge-search.txt` (41 documents), and the tool holds each bound's documents to it. It found one published minimum the first pass had not written down: the PI7C9X2G404SL's PCIe transmitter (0.125 and 0.15 unit intervals, p. 83). It moves nothing: those lanes carry a module or a card that publishes none. Four quotes of a part's or a pin's name were replaced (the 74LVC1G34's two sheets and the AS7331 by the row that speaks of a transition, the RP2040's XIN by the sentence on its oscillator); the rest stand as quotes of identity, and the listing is what shows the search |
| LVC1G34-BUFFER's owed verification names TI's model | it names Diodes', the part `SOURCES.yaml` pins |
| "none for the number" against ER-D5's die caveat | the IBIS records' owed verification carries the caveat |
| Q8, publication of the IBIS files | unchanged and still the owner's, section 12 |

## 9. Session decisions

All are the session's, under the owner's ruling of 21 September 2026 and his standing rule of 26 September 2026
(`authority: SESSION`, `ruled_by: SESSION (stream w5si)`). None is the owner's. ER-D1 to ER-D15 are written in the
data file's header with their reasons and how to reverse each.

| Id | Decision | Pass |
|---|---|---|
| ER-D1 to ER-D7, ER-D11 | the data file is the declaration; drivers are U and Q parts; identity by part number; the IBIS reading rule; one series-resistor hop; a far end's fastest pin; the STM32H743's HSLV pins | first, kept |
| ER-D8 | only a published minimum is an edge; otherwise the instantaneous bound | first, kept |
| ER-D9 | BOUND_DECIDES holds the reading INCONCLUSIVE | first, reworded |
| ER-D10 | firmware-set drive, slew and direction are taken at their fastest | first, its reason corrected |
| ER-D12 | an ANSWERED net decided by a bound counts as decided, under the bound's count | first, corrected: its maker-held half is withdrawn |
| ER-D13 | the governing edge is the fastest any driver can produce; one driver without a figure decides the net | second |
| ER-D14 | an open-drain net has two edges and the fall governs; a specification binds only a part that claims it | second |
| ER-D15 | every citation carries sha256/16 and page; every bound names what was searched | second |
| W5SI-D1 | board B's RF switch ports are RF lines | first, kept |
| W5SI-D2 | BOB keeps its class and gets a true basis; the class that fits is proposed | second, replaces the first pass's |
| W5SI-D3 | the power-stage nodes stay on their bound; no declaration is written for them | second |

## 10. Open, each with its next action

| Id | Open item | Next action | Whose |
|---|---|---|---|
| Q1 | 82 power-stage nets, BOUND_DECIDES | finding `F-Q1-power-stage-nodes.md`: a power-stage layout rule in the registry, then SI-001 excludes them by declaration | the registry writer, then the tool's owner |
| Q2 | 19 oscillator nets | CLK-001 states a maximum node length per crystal; declarations then name it | CLK-001's owner |
| Q3 | 178 BOUND_DECIDES nets governed by a part, a module or a far end whose maker publishes no edge (281 less the 82 power-stage nets, the 19 oscillator nets and the 2 RF lines); Q4's 39 and Q5's 12 are among them | per net: a series resistor at the driver, a firmware slew obligation, the maker's model, or the edge measured at bring-up | the board authors |
| Q4 | board B's control plane | the 40 maker-held nets there (voters, CAN, select lines at 0.136 to 0.451 ns, critical lengths 3.2 to 10.5 mm on a 530 mm board) need a series source resistor or an impedance target. The 39 nets a Nexperia 74LVC1G157 or a Diodes 74LVC1G17 governs (BBM*, BSEL*, BOE?_n), 15 of which carry a TI gate's figure beside the bound, need those parts' models FIRST: no resistor at a TI gate closes a net another maker's gate also drives | board B's author; the models by a browser fetch |
| Q5 | the kit bus and EXP_INT | they are decided by a bound, not by the STM32H743. What would close them: a figure for the RP2040's pads and for the ATECC608B, BQ25731 and VEML7700 (bench item V-K01 measures the fall on the bus). FW-K02 says the fall "sits between the specification's floor and the ATECC608B's 100 ns"; two makers' models (STM32H743 0.451 ns, ADS1115 0.786 ns, into a resistive fixture) are faster than that floor when unloaded, so the sentence rests on the bus capacitance and is V-K01's to show. A contract row fixing OSPEEDR 00 on PB6 and PB7 would admit 6.70 ns for the STM32H743 | layer 5's owner for the row; a bench for V-K01 |
| Q6 | 75 nets with no signal-class declaration (73 on set 6) | board-table entries, most of them LOW_SPEED_OR_DC with a basis; listed in the readings. Not drafted: set 6 rewrites `boards/*.json` | the board authors, after set 6 |
| Q7 | makers' models this host cannot fetch | Nexperia 74LVC1G157, Diodes 74LVC1G17 and 74LVC1G34, Microchip KSZ9897R, Winbond W25Q16JV: a browser fetch, no login | anyone with a browser |
| Q8 | publication of the IBIS files | section 12 | the owner |
| F-BOB | a class for the cable side of an isolation barrier | rule it | the integrator |
| F-BOB-2 | the PoE pairs' common-mode termination | decide it | board B's author |
| F-Q1 s.5 | six switch nodes in net class Default | the SW class in `gen_pcb_a3.py` and `gen_pcb_c3.py` | boards A and C, after set 6 |

**Does a bound decide feasibility anywhere?** Not that this stream can show, and it does not claim the opposite.
For the 281 BOUND_DECIDES nets the instantaneous bound says only that the net is a transmission line at any length;
each has an answer that does not depend on the edge (a termination, an impedance target, a slower driver). Whether
board B's control plane can be laid out with those answers on a 530 mm board is a layout question this reading does
not settle, so that decision stays open under Q4.

## 11. Instrument limits, said out loud

- Parts that are neither U nor Q are not asked for an edge: a relay's contact, a mechanical switch, a transformer's
  winding. The reading names the nets that carry one.
- GNSS_ANT is declared a rail (it carries the antenna's bias) and so leaves SI-001's signal set although it is an RF
  line; RF-001 covers it.
- The routed half (`edge_length_routed`, which decides no rule) still reads the board tables' `rise_ns`, not the data
  file.
- A continuation assumes the same net name on each board; the test holds the far-end records to the netlists.
- The series-resistor screen cannot tell a termination from a source resistor. It answers BOB with the termination's
  own resistors.
- An IBIS `[Ramp]` is the driver's edge into a resistive fixture, with no bus capacitance. It is the fastest the pin
  can launch into a line, which is what SI-001 asks, and it is faster than the same pin's fall on a loaded bus.
- The search for a published transition is by words. A figure printed only in a graph is not found.

## 12. For the integrator

1. **Commit order.** `tools/pcb_edge_rates.yaml`, the 13 IBIS files and `v2/docs/records/w5si/readings/edge-search.txt`
   are configuration inputs of the `edge_length` verdict. They are committed on this branch. After a merge, run
   nothing that writes evidence before they are in the tree, or every SI-001 reading reads CONFIG_CHANGED.
2. **The drafts**, each refusing a second run, each checked on a scratch copy of `c23c5e76` and of `fnd/r8int6` at
   `73ae2f21`. Run from anywhere; `--dry-run` writes nothing.

   | Order | Draft | What it changes |
   |---|---|---|
   | 1 | `apply/apply_rules_status_config_inputs.py` | `rules_status.CONFIG_INPUTS["edge_length.py"]`: 6 inputs become 76, re-derived on the tree it runs in |
   | 2 | `apply/apply_sources_yaml_ibis.py` | `v2/vendor/SOURCES.yaml`: 9 document rows and 1 owed line |
   | 3 | `apply/apply_board_b_declarations.py` | `boards/b.json` (3 entries) and `gen_pcb_b3.py` PATTERNS (40 entries become 41) |
   | 4 | `apply/apply_coverage_si001.py` | `pcb_rules_coverage.yaml`, record SI-001: a paragraph whose counts are taken when it runs, and the remediation's action |
   | 5, if wanted | `apply/apply_decisions_w5si.py` | `pcb_decisions.yaml`: four SESSION rows from the next free number; then `decisions_render.py` |

3. **Then re-take SI-001** on all six boards together with `retake_gate.sh`, never by hand in the tree: a
   continuation reads every board's netlist.
4. **A merge conflict to expect.** Set 6 appends to `v2/vendor/sources.txt` and `v2/vendor/vendor-status.txt`, and so
   does this branch (13 lines each). Both sides' lines are kept.
5. **Publication (Q8).** TI's IBIS headers say "Unauthorized reproduction and/or distribution is strictly
   prohibited" and ST's carry a copyright. They are filed under `v2/vendor/README.md`'s standing terms (the makers'
   property, taken down on request), as the datasheets are. `main` is mirrored publicly within minutes of a push.
   Whether these 13 files go out with it is the owner's decision, and it is not taken here. If they are withheld the
   records that cite them decide nothing and their nets read UNDECIDED: the tool fails closed.

## 13. What was run, and what it gave

| What | Where | Result |
|---|---|---|
| `python3 run.py test_edge_length.` on the recovered tree | the worktree | 28 passed, 0 failed |
| the same after the second pass | the worktree | 36 passed, 0 failed, 0 skipped |
| `apply/selftest.py` | a temporary directory | 11 checks, 0 failures |
| `tools/verify_citations.py` on the two evidence files | read-only | 46 and 9 citations, 0 do not hold |
| the five drafts, each run, run again and dry-run | scratch copies of `c23c5e76` and `73ae2f21` | each applies once and refuses the second run, on both |
| with all five applied: `test_edge_length.`, `test_signal_class.`, `test_netclass.`, `test_netlist_classes.`, `test_rules_registry.` | both scratch copies | 36, 8, 8, 2, 5 passed; 0 failed, on both |
| with all five applied: `test_rules_status.` | scratch copy of `c23c5e76` | 35 passed, 0 failed, 1 skipped |
| the same | scratch copy of `73ae2f21` | 34 passed, 1 failed, 1 skipped. The failure is the scratch copy's, not a draft's: it fails the same way with NO draft applied, because the copy puts set 6's registry beside this branch's generated pages |
| with all five applied: `test_evidence_class.`, `test_decision_register.` | both scratch copies | 26 passed, 0 failed, 1 skipped; 3 passed, 0 failed, 2 skipped, on both (the skips are the copies': no git, no set-level evidence) |
| `test_certify_mismatch.`, `test_review_packet.`, `test_handover_pack.`, which read the vendor lists | the worktree | 26, 15 and 15 passed; 0 failed |
| the readings | scratch, outside any tree | sections 1 to 3 |

The full suite was not run, and no KiCad step was needed: nothing here was run on the rented box, and nothing was
spent. No gate, `rules_status.py` or renderer was run in any tree. The worktree's own `out/` evidence is unchanged.
