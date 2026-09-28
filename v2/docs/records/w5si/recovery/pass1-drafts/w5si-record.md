# Stream w5si: rule SI-001's edge rates as data (layer 9, MESHSAT-1357)

Written 27 September 2026, 19:45 CEST, in worktree `fnd/w5si` from `c23c5e76`. Prototype design work: nothing here has
been built or measured; every edge below is a maker's figure, a standard's, or a bound stated with its derivation.
For filing under `v2/docs/records/w5si/` by the integrator. The review this answers is
`v2/docs/reviews/2026-09-27-third-checkpoint-review.md` sections 5 and 6: "for undocumented signal edge rates, do not
insert convenient values simply to turn SI-001 green. Record a justified design bound or suitable model, its
applicability and the verification still required. If the uncertainty decides feasibility, keep that decision open."

## 1. What was built

| File | What it is |
|---|---|
| `v2/ecad/tools/pcb_edge_rates.yaml` (sha256/16 `26ef827a1d9ff277`) | THE DATA: every edge the SI-001 reading uses, with document, quoted words, conditions, applicability and verification owed. 6 interface records, 58 driver families, 29 far ends. Its header holds the schema and session decisions ER-D1 to ER-D12. **A configuration input of the edge_length verdict** |
| `v2/ecad/tools/ibis_read.py` (new) | reads a maker's IBIS model per pin: the fastest driven 20 to 80 percent transition over the admitted models and all three corners; an open drain drives only its fall; an input drives nothing; an unknown pin is UNKNOWN |
| `v2/ecad/tools/edge_length.py` | the schematic-phase reading now resolves each net's drivers (section 2); `EDGE_SOURCES` is the data file's STANDARD records; the verdict records the data file, every cited document and every other board's netlist it read, by sha |
| `v2/ecad/tools/tests/test_edge_length.py` | 10 new tests (28 in the file): the reader, fixtures both ways, the maker-held against bound-decided split, a contradicted model FAILs, a typical or maximum refused, far ends and the series-resistor hop, continuations pin by pin, and the real data file held against its documents, its models and the committed netlists |
| `v2/vendor/ti/ibis/*.ibs` (12), `v2/vendor/st/ibis/stm32h742_743_750_753_lqfp100.ibs` | the makers' IBIS models, each with a `sources.txt` and a `vendor-status.txt` line |

The runner reached TI directly; ST's archive came from the Wayback Machine (`id_`, st.com refuses the host). Nexperia
(browser challenge), Diodes and Microchip (refused) could not be fetched; Raspberry Pi and Silicon Labs offer no IBIS
model for the RP2040, the CM5 or the CP2102N on their public pages.

## 2. How a net's edge is decided (the instrument)

1. A net whose signal-class entry an **interface record** covers takes its edge (the USB 2.0 minimums; instantaneous
   bounds for board B's controlled links, the RF lines, the power-stage nodes and the oscillator nodes). A board
   table's own `rise_ns` must agree, or the reading FAILs.
2. Otherwise every IC or module (`U...`) and transistor (`Q...`) on the net is asked for its **family**, by the part
   number at the start of its value field (never an order code). IBIS families are read **per pin**; a pin the maker
   types as an input drives nothing. **A part with no record leaves the net UNDECIDED, named.**
3. A connector's pin (and a passive switch's through pin) takes the **far end**: a board of this set that the net
   continues onto is read from its own committed netlist, pin by pin; a part beyond the set is a named family.
4. A net takes the drivers **one series resistor away**, once (their edge only slows through it).
5. The **fastest** candidate decides. A layout-bound net that **no maker's figure on it holds** (none, or the fastest
   gives a critical length past the board's corner-to-corner run) is named **BOUND_DECIDES** and holds the reading
   INCONCLUSIVE; one a maker's figure holds is the maker's, whatever bound sits beside it.

## 3. Readings before and after (scratch, committed netlists at `c23c5e76`, k = 6, slowest layer of each board's stacks)

| Board | Netlist sha256/16 | Before: decided / undecided / layout-bound | After: decided / undecided / layout-bound | answered | maker-held | bound decides | Verdict |
|---|---|---|---|---|---|---|---|
| A | da05dc02bc1e612f | 6 / 114 / 0 | 82 / 38 / 63 | 19 | 5 | 58 | INCONCLUSIVE, unchanged |
| B | 8b78c59754a6a0c7 | 30 / 532 / 0 | 553 / 9 / 193 | 360 | 67 | 126 | INCONCLUSIVE, unchanged |
| C | 11eabc2dddca5161 | 4 / 33 / 0 | 33 / 4 / 23 | 10 | 6 | 17 | INCONCLUSIVE, unchanged |
| D | 76700a687eb6187f | 20 / 27 / 2 | 39 / 8 / 13 | 26 | 5 | 8 | INCONCLUSIVE, unchanged |
| E | d6137f50059e5cbc | 4 / 37 / 0 | 41 / 0 / 31 | 10 | 0 | 31 | INCONCLUSIVE, unchanged |
| P | 085f833362fbbda8 | 0 / 22 / 0 | 5 / 17 / 1 | 4 | 0 | 1 | INCONCLUSIVE, unchanged |

Readings: `$SP/w5si/before/<board>/` and `$SP/w5si/after/<board>/` (verdict and table JSON, printed table), summaries
copied to `drafts/w5si/readings/`. No reading moved class; each now names why it is INCONCLUSIVE. **What is still
undecided** is 75 nets that no signal-class declaration names (A 38, B 8, C 4, D 8, P 17: mostly converter sense and
feedback nodes, supervisor and protector pins, listed in `readings/bound_decides.txt`) and board B's BOB (section 5).

## 4. Where the bound, not a maker's figure, decides the verdict, and whether it decides feasibility

Every net below is LAYOUT_BOUND only because its edge is a bound (all bounds here are the instantaneous one, ER-D8).
Full lists per board: `readings/bound_decides.txt`.

| Group | Nets | Why the bound decides | Does it decide feasibility? |
|---|---|---|---|
| Power-stage nodes (gate drives, bootstrap, switch nodes, hot-swap and ideal-diode gates) | A 57, B 14, C 1 (EPD_SW), E 10 | no maker states a lowest edge for these circuits (LM5176's datasheet: switching times come "from the MOSFET data sheet ... or measured in the lab") | **No.** These nodes have no logic receiver, so SI-001's failure modes (overshoot into a receiver's clamp, double clocking) do not arise; their length is a power-loop question. The schematic answer is a declaration in `edge_allow` naming what holds the length, and **no registry rule states a length for a switch node or gate drive yet** (open item Q1) |
| Oscillator nodes | B 8, C 3, D 5, E 3 | no maker states an oscillator amplifier's transition; the GPIO model of the pin does not describe it | **No.** Placement and loading are CLK-001's; the answer is a declaration naming CLK-001's placement once CLK-001 states a length (Q2) |
| RF lines with no impedance target | B: GNSS_RF_IN, LORA_ANT | recorded as a bound; any band edge would do the same (0.255 / f: LoRa 930 MHz 0.27 ns, 6.4 mm; GNSS L1 1.61 GHz 0.16 ns, 3.7 mm) | **No.** The answer is the RF class (draft W5SI-D1 for GNSS_RF_IN; LORA_ANT takes it from gen_pcb_b3.py's `*_ANT` pattern at the next generation) |
| Modules and bridges whose makers publish no edge, on board | B: CM5 GPIO behind its receptacles 27, E72 10, E22 7, PI7C9X2G404SL SMBus 6, CP2102N 5, LG290P 5, discrete FETs 9; C: RP2040 11 (QSPI, e-paper, SWDIO); D: SA868 2, TUSB2046B reset 1; E: RP2040 14, BMI270 1, fan FETs 2; A: TPS25740 PD_VTX 1; P: BQ4050 BTP_INT 1 | the maker publishes no transition (RP2040: a slew bit and no number; CM5: "set drive and slew as low as necessary") | **No.** Each has an answer independent of the edge: a series resistor at the driver, a firmware obligation that slows the driver (RP2040 SLEWFAST 0, CM5 drive and slew, a layer 5 obligation), or a declared layout length once the edge is known. Which one each takes is open design work (Q3) |
| Logic of another maker than TI in board B's control plane | B: Nexperia 74LVC1G157 9, Diodes 74LVC1G17 15 | no IBIS model held (fetch refused) | **No, and the bound hardly matters:** the TI LVC models of the same family give 0.11 to 0.28 ns (critical 2.6 to 6.5 mm), so these nets need the same answer as the TI-driven voters beside them (Q4) |
| Far ends beyond the kit | B: RM520N SIM 3, RockBLOCK 9704 1, monitor DDC 2, bench headers 3; C: e-paper flex via RP2040, TR_APRS gate Q3_G 1, SWCLK 1; E: SWCLK 1 | the far part publishes no edge; a bench probe is not the kit's | **No.** A cable run is long at any plausible edge; a series resistor or the far part's own figure answers it |

**Conclusion for the review's question:** the bound decides 241 nets' verdicts across the six boards and decides
feasibility nowhere; each such net has a schematic answer that does not depend on its edge, and none needs an
architecture or interface change. Those decisions stay open as design work, named per net, and the readings stay
INCONCLUSIVE until each is answered.

## 5. Findings the maker's figures make (not the bound), and other findings

1. **Board B's high-availability control plane is a set of transmission lines at the makers' own edges.** TI's IBIS
   models put the voters' outputs at 0.11 to 0.22 ns (SN74LVC08A, SN74LVC32A, SN74LVC86A) and ST's puts the STM32H743's
   outputs at 0.451 ns at the very-high-speed setting: critical lengths 2.6 to 10.5 mm on board B's slowest layer,
   against nets that run between three supervisors, the voters and the hub and multiplexer banks across a 530 mm
   board. SEL*, WSEC_*, BBM*, BSEL1 to BSEL3, the CAN lines to the TCAN334s (10.5 mm) and the heartbeats HB1 to HB3
   (0.451 ns, over the panel ribbon) are maker-held. **Engineering question Q4** below.
2. **The kit I2C bus and EXP_INT** (boards A to D) are held by the STM32H743's I2C1 pins (0.451 ns at the
   very-high-speed setting; its Fm+ pad would give 8.83 ns and the low-speed setting 6.70 ns) and the PCA9555's INT
   open drain (0.121 ns), on a bus of about 1.5 m of copper and 490 mm of ribbon (HW-FW-CONTRACT.md section 6). The
   ADS1115's SDA pull-down is 0.786 ns in TI's model. **Q5.**
3. **Board B's table declares three entries for nets they do not describe:** `SW?_IN` and `SW?_O?` ("a voter
   input/output") match only the SKY13351 RF switch ports; `BOB` ("the break-before-make timing node") matches only the
   Ethernet magnetics' Bob Smith termination. And gen_pcb_b3.py puts the switch ports and the card RF lines in the USB
   pair class and GNSS_RF_IN in no class. Draft `apply_board_b_declarations.py` (W5SI-D1, W5SI-D2).
4. **An instrument limit:** GNSS_ANT is declared a rail (it carries the active antenna's bias) and so leaves SI-001's
   signal set although it is also the GNSS RF line; RF-001 governs its impedance, SI-001 cannot see it.
5. **The routed half** (`edge_length_routed`, which decides no rule) still reads the board tables' `rise_ns`, not the
   data file. It should adopt the data file when the layout gate adopts it.

## 6. Session decisions (ruled_by: SESSION, stream w5si, under the owner's standing rule of 26 September 2026)

ER-D1 to ER-D12 are written in `pcb_edge_rates.yaml`'s header with their reasons and reversals: the data file is the
declaration (D1); drivers are U and Q parts, a connector's pin is its far side (D2); identity by part number, never
order code (D3); the fastest candidate decides (D4); the IBIS reading rule (D5, with the die-revision caveat); one
series-resistor hop (D6); a far end family's fastest pin (D7); only a published minimum is an edge, otherwise the
instantaneous bound (D8); BOUND_DECIDES holds the reading (D9); firmware-set speeds taken at their fastest (D10); the
STM32H743's HSLV pins read with the io8_ft 3.3 V models (D11); a bound that decides nothing counts as decided (D12).
W5SI-D1 and W5SI-D2 are in `apply_board_b_declarations.py`.

## 7. Open, each with its engineering question

- **Q1, power-stage nodes (82 nets).** What length holds each gate, bootstrap and switch node, and from which rule?
  Recommended: a per-stage model from the driver's resistance and the chosen FET's charge (the LM5176 and LT8705A
  sheets state the drivers), a power-loop length rule in the registry, then `edge_allow` declarations naming it.
  Expertise: power-stage layout review.
- **Q2, oscillator nodes (19 nets).** CLK-001 to state each crystal's maximum node length; then declarations naming it.
- **Q3, unknown-edge drivers (114 nets).** Per net: series resistor at the driver, a firmware slew obligation, or
  a declared layout length once the edge is measured. Cost: a resistor footprint per line, or a HW-FW-CONTRACT row.
- **Q4, board B's control plane, CAN and heartbeats (maker-held).** Series source resistors at each LVC and STM32
  output that drives a run longer than its critical length (typically a value near the line impedance less the
  driver's output resistance), and/or a firmware obligation holding the STM32 outputs at OSPEEDR 00 (6.70 ns, about
  156 mm). A schematic change to gen_sch_b.py, owed to board B's author; whether any of these inputs is edge-sensitive
  (double-clocking) decides how urgent it is.
- **Q5, the kit I2C bus and EXP_INT (maker-held).** Fold into SC-HF-02's segment design (HW-FW-CONTRACT.md 6.5): a
  firmware obligation for the STM32H743's I2C1 pins (Fm+ pad or OSPEEDR 00), series resistors at the sub-nanosecond
  pull-downs (UM10204 allows series Rs), and the TCA9517A's own output edges once it is drawn; bench check V-K0x.
- **Q6, the 75 nets with no class declaration.** Board-table entries (most are analog sense and feedback: LOW_SPEED_OR_DC
  with a basis). Not drafted here because `fnd/r8int6` is rewriting `tools/boards/*.json`; the list is in the readings.
- **Q7, the makers' models this runner could not fetch.** Nexperia 74LVC1G157, Diodes 74LVC1G17 and 74LVC1G34,
  Microchip KSZ9897R, Winbond W25Q16JV: a browser fetch (no login is needed; the sites refuse or challenge this host).
- **Q8, publication of the IBIS files.** TI's headers say "Unauthorized reproduction and/or distribution is strictly
  prohibited"; ST's carry a copyright. They are filed under `v2/vendor/README.md`'s standing terms (the makers'
  property, takedown on request), as the datasheets are. Publication is the owner's; if they are withheld, the records
  that cite them read UNDECIDED (fail closed) and the sources lines keep URL and sha.

## 8. For the integrator

- `tools/pcb_edge_rates.yaml` is a **configuration input**: commit it (and the IBIS files) **before** running
  rules_status and rules_render, or every SI-001 reading reads CONFIG_CHANGED.
- Apply the drafts in this order on the post-set-6 tree, each asserting its anchors and refusing a second run:
  1. `python3 drafts/w5si/apply_rules_status_config_inputs.py` (declares the data file, 60 cited documents and the six
     declared netlists in `CONFIG_INPUTS["edge_length.py"]`; derived at apply time);
  2. `python3 drafts/w5si/apply_sources_yaml_ibis.py` (9 document rows, 1 owed line);
  3. `python3 drafts/w5si/apply_board_b_declarations.py` (board B's table and gen_pcb_b3.py; re-run board B's
     schematic chain only if the integration regenerates it anyway);
  4. `python3 drafts/w5si/apply_coverage_si001.py` (SI-001's coverage note and remediation; re-derive its readings
     sentence if the re-take moved the numbers).
  All four were dry-run on a copy of this tree; with all four applied, `test_edge_length`, `test_signal_class`,
  `test_evidence_class`, `test_rules_status`, `test_rules_registry`, `test_netlist_classes` and `test_netclass` pass
  (117 passed, 2 skipped for no git and no set-level evidence in the copy).
- Then re-take SI-001 on the integrated netlists (the continuation reads every board's declared netlist, so re-take all
  six together).
