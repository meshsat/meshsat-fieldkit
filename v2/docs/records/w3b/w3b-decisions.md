# Board B, stream w3b (MESHSAT-1357, 27 September 2026): PWR-001 declarations, decision 42 classes, CFL-010

Base: main `38dcd764`. Worktree `fnd/w3b`. Author of `v2/ecad/tools/gen_sch_b.py` and board B's schematic-phase files under
`v2/ecad/pcb-b-compute-b19/` (schematic, netlist, intent, provenance sidecar); `tools/boards/b.json` is unchanged. Nothing is
committed or pushed. Prototype framing: no board of the set has been built and nothing here was measured on hardware. Every
figure is a maker's published figure or arithmetic on one, or is marked INFERRED. This is a source-backed desk review of the
changes, with the gates that read them run in scratch; it is not an automated PASS of anything the gates do not read.

Generator sha256/16 `6957adda1bb5f23a` (main `af6e5821e21b70ef`). Netlist `8b78c59754a6a0c7` (main `adcc3c6736c90e9f`),
schematic `76c29fa7f88a39e0`, intent `162fcb9b95f680a7` (277 decoupling declarations, 58 rails, 154 nodes), sidecar `dd9ea6514913d703`. The box run's own
identities are in `evidence/box/` (`incoming.sha256`, `prov-after-cand.txt`: "written by this tree's own generator").

## 1. What changed, by goal

**(1) PWR-001 on board B.** Main's netlist read FAIL: 28 power nets undeclared, 26 undecided. Every one is now declared in
the intent `gen_sch_b.py` writes, each from its maker's sheet (the citation is in the declaration):

| kind | nets | why that kind |
|---|---|---|
| rail (7 of the 28) | VBAT_RTC (was VBAT), VBUS_FLASH1 to 3, SIM1_VCC, SIMC2_VCC, GNSS_VDD_RF | current reaches the supply pins of two or more parts, or leaves a module's power output (RM520N USIM_VDD PO, LG290P VDD_RF PO) |
| node (21 of the 28) | the 14 bootstraps (AP64500 BOOT, TPS62933 and AP63203 BST), GNSS/ZBA/ZBB/RB_3V3 (CP2102N regulator outputs), IOCA to IOCC_VCAP | one part's own supply: rides_on its switch node with the maker's BST-SW bias (6.0 V AP64500 and AP63203 absolute, 5.5 V TPS62933 recommended), VREGOUT 3.6 V, VCORE 1.40 V |
| rail (10 of the 26) | GNSS_BIAS, GNSS_ANT (series segments of GNSS_VDD_RF), SIM2_VCC, POE_P, MDI_A_P/N (series of +54V_POE), MDI_B_P/N, POE_DRAIN, POE_SEN (returns of +54V_POE, switched by Q1 through POE_GATE) | they carry a supply current: the antenna's LNA feed, the SIM's supply before its eSIM link, the PoE port's feed and return (802.3 Alternative A on this board) |
| node (16 of the 26) | IOCA to IOCC_RST_n, nRPIBOOT1 to 3, Q1C to Q3C (PWR-LED feeds, about 1 mA), LORA_ANT (22.4 V: 31 dBm into 50 Ohm, doubled at full reflection), MDI_C/D_P/N (57 V, the port's cable side), POE_GATE (VGOH 12.5 V), POE_RST_n | a signal or one part's input, with the largest voltage a part on it sees |
| node (3 new) | GNSS_RF_IN, POE_SEN_PIN, POE_DRAIN_PIN | GNSS_RF_IN became marked (C42 to the now-declared feed); the other two are W3B-F1's new nets |

Two existing declarations were wrong and are corrected: `+54V_POE`'s loads sent the port's 0.60 A into U5 (the TPS23861's VPWR
draws at most 7 mA, SLUSBX9I 6.5); it now names R13 (0.593 A) and U5 (0.007 A). U11's `+3V3_DEV` load was 0.05 A where the
LG290P draws 135 mA peak at VCC (Table 11) plus its antenna's 30 mA through VDD_RF: 0.165 A.

**(2) Decision 42's classes.** `gen_sch_b.py` writes `class` and `basis` (with `value_floor` and `esr_max` on class L,
`same_side` on class R) onto every declaration before the sheet is laid out, from the part each capacitor serves, its pin and
its value, with the maker's clause, document, revision and page; an entry without a class stops the generator. Against the
round 8 map (`v2/docs/records/r8b/decoupling-classes-b.json`) every class agrees except four corrections (`evidence/
decoupling-classes-w3b.txt`, 0 unexplained): C508 and C509 serve the SN74LVC1G08 gates U503 and U504 and are class D (TI
SCES217AA), where the map had class R with the AP64500's clause; C65 and C66 keep class D with the SN74LVC1G08 clause where the
map carried the PI7C9X2G404SL's and the TUSB8041's. Three entries are new (C72 to C74, W3B-F2, class D). Board B: 277 of 277
entries classed (R 29, D 224, L 11, B1 3, B2 10); the census of the other five boards' intents: A 55 of 55, C 24 of 24, D 31 of
31, E 25 of 25, P 4 of 4.

**(3) CFL-010, the SIM TVS array.** It is drawn since round 8: U222 and U223, TI TPD4E001DBVR, 1.5 pF typical (SLLS682P 5.5),
on the holder side, VCC on the SIM supply, with the maker's 0.1 uF (C286, C289). Documented (`v2/vendor/ti/ti-tpd4e001.pdf`,
SOURCES.yaml VERIFIED) and certifiable: `tools/jlc_certify.py`'s own `certify()` on the two BOM rows reads CERTIFIED (model
TPD4E001DBVR, Texas Instruments, SOT-23-6, stock 17,211 against 5 needed, 27 September 2026; `evidence/jlc-certify-w3b.txt`).
The constraint on board B is met; CFL-010 stays FAIL on its other clause, the order code of an eSIM-fitted RM520N-GL, which no
board change reaches (S-13, reworded by the registry patch to that clause alone).

## 2. Circuit changes (found while reading the makers' sheets for (1))

| id | change | source | reversal |
|---|---|---|---|
| W3B-F1 | R525 22 Ohm between POE_SEN and the TPS23861's SEN1 (new net POE_SEN_PIN); R526 47 Ohm between POE_DRAIN and DRAIN1 (POE_DRAIN_PIN). 0603, 75 V; R526 carries C23182 (no MAP line for 47R), R525 no code (MAP gives every 22R C23345), both CERTIFIED at JLCPCB | SLUSBX9I p.5 ("connect to current-sense resistor through a 22-Ohm resistor", "connect to output port through a 47-Ohm resistor"), 6.5's conditions "RSENS = 22 Ohm, RDRAIN = 47 Ohm", p.1 | remove the two resistors |
| W3B-F2 | C72 4.7 uF, C73 100 nF, C74 33 pF at the LG290P's V_BCKP (pin 22), declared class D; the TVS of the same sentence not drawn (S-49) | LG290P(03) hardware design V1.1 3.2.2, p.25, Figure 6 | remove C72 to C74 |
| W3B-R1 | the coin-cell net VBAT renamed VBAT_RTC | board A's pack node is VBAT (14.4 V); `check_contracts` pairs two boards' rails by name and read the two as one conductor crossing A/B (INCONCLUSIVE, "rail VBAT crosses A/B"); a distinct conductor takes a distinct name | name it VBAT again |

Each is taken by the session under the owner's standing rule of 26 September 2026 (recommended option: follow the maker; for
R1, the naming that keeps the name-keyed contracts true). Knock-on outside this stream's files: `gen_pcb_b3.py`'s class pattern
`("VBAT", "PWR")` becomes `("VBAT_RTC", "PWR")` (drafted in `page-drafts.md` section 4).

## 3. Session decisions

| # | decision | reason | reversal |
|---|---|---|---|
| W3B-D1 | a conductor that carries a supply current is a RAIL, however small (VBUS_FLASH at 150 nA, the SIM supplies, the MDI pairs that carry the PoE feed); a net that is one part's own supply or a signal is a NODE | PWR-001's own definitions (threshold 0 A, "a node that carries the supply pins of two or more parts is refused"); a rail is judged by PI-001 to PI-003, a node by CMP-001 only | declare the MDI pairs as nodes, which drops their PoE current from the copper rules |
| W3B-D2 | the bootstrap bias is the maker's ceiling where no working figure is given (6.0 V AP64500 and AP63203, VBST absolute maximum) and the recommended maximum where one is (5.5 V TPS62933) | the node's bias is what the capacitor across BST and SW is judged against; the larger figure is the safe direction | 5.0 V, the AP64500's test condition |
| W3B-D3 | 50 mA peak on the SIM supplies, INFERRED from SIMCom's figure for the same output (A7672X/A7670X HD V1.03), and 20 mA typical / 30 mA peak for the GNSS antenna, INFERRED | the RM520N HD states no USIM_VDD current; no held document states the antenna's; each is marked INFERRED where it is declared | the maker's figure when held (S-48 for the antenna) |
| W3B-D4 | the MDI_C/D pairs and the monitor net POE_DRAIN_PIN at 57 V | the port's cable side, TPS23861 VVPWR maximum (SLUSBX9I 6.3) | the pairs' signal amplitude if a reviewer rules the cable side is not reachable by the feed |
| W3B-D5 | the four class corrections of section 1 (2) | the capacitor serves the SN74LVC1G08; its role, not its number, gives the class (DECOUPLING.md section 6) | the map's classes |
| W3B-D6 | the V_BCKP TVS is not drawn in this stream | a pick needs a held datasheet and a standby leakage the coin cell can carry, and the board feeds V_BCKP from an on-board cell rather than the maker's always-on supply (S-49) | draw it with the pick |

## 4. Readings, before (main 38dcd764) and after (the candidate), in scratch

| reading | before | after |
|---|---|---|
| PWR-001 (intent_rails, netlist) | FAIL of 70: 28 undeclared, 26 undecided | PASS of 59: 58 rails, 35 power nets declared as nodes, 0 undecided; census 58 counted, 154 declared node, 50 settled, 707 unmarked |
| check_contracts | PASS of 96 | PASS of 96 (INCONCLUSIVE with 1 unsplit rail before W3B-R1) |
| power_sequence | PASS of 41 | PASS of 58 (29 always on, 11 segments, 0 unresolved, 0 deadlocks) |
| power_path | PASS, 41 rails | PASS, 58 rails, 154 nodes, 0 feeds short |
| derate | PASS of 240 | PASS of 240 (425 unrated parts, the five new passives among them) |
| edge_length (SI-001) | INCONCLUSIVE, 888 signal nets | INCONCLUSIVE, 882 signal nets (the six nets now declared rails or nodes leave the signal set) |
| erc_gate (box) | PASS, 2869 violations, 7 allowed errors | PASS, 2879, the same 7 allowed errors; the ten new are warnings of the classes already there |
| port_protect, safe_lines, clock_check, ground_system, energy_chain, inhibit_chain (RF-002) | as before | unchanged (inhibit_chain_b FAIL 10, PASS 3, UNDECIDED 7 both times: EQ-18, not this stream's) |
| decoupling, desk census of the intent | 0 of 274 classed | 277 of 277 classed, 0 unexplained against the map |
| DEC-001 (intent_decoupling, board mode on the committed B21 placement, box) | FAIL of 274 (156 pass) | FAIL of 277 (156 pass; the three new capacitors are not on B21) |

DEC-001 on B21 is NOT evidence for either: it is a PLACED_BOARD rule, the placement predates round 8, and no tool reads the
class yet (DECOUPLING.md T2 and T5); the seats are read at board B's next placement. Tests that read board B's files
(`run.py sch_prov energy_chain order_codes interfaces tx_inhibit rails_census rails_netlist last_net kisch_tvs`): 284 passed, 0
failed, 3 skipped (two need KiCad, one the certification table). The registry check (`rules_lib.py requirements`) on a scratch
copy with `apply_registry.py` applied: 0 errors (before the patch: 6 errors and 12 stale-binding warnings).

## 5. Parity (box 52646493, `drafts/w3b/tools/w3b_box.sh`)

- Main's generator against main's committed board B files: schematic PARITY, netlist, intent, provenance and ERC
  PARITY_AFTER_NOISE, BOM PARITY.
- The candidate against main, read by the integration's own comparator (`v2/docs/records/r8b/integration/indep_cmp.py`) with
  `expected_w3b.json`: 5 parts added (R525, R526, C72, C73, C74), 1 changed (TP6's value, the net it names), 3 nets added
  (POE_SEN_PIN, POE_DRAIN_PIN, VBAT_RTC), 1 removed (VBAT), 3 changed (POE_SEN, POE_DRAIN, GND): 0 unexplained against the
  committed netlist and against main regenerated; dropping W3B-F1's parts from the list gives 2 unexplained (the comparator
  refuses). An intermediate run omitted GND from the list and was refused with 1 unexplained (`box/compare-intermediate-gnd-
  omitted.log`).
- The rename: VBAT_RTC carries every node VBAT carried plus C72 to C74 pin 1; U9's pin 14 function follows the net name (its
  symbol names pins after nets): `box/compare/rename_check.txt`, RENAME PARITY.
- Schematic: parts only in the candidate are the five, TP6's value changed, U9's symbol changed (the pin name); determinism:
  the candidate generator twice gives an identical schematic.

## 6. Open (numbers as the registry patch takes them)

- S-48 (W3B-A): the LG290P active antenna feed against Figure 17 (L1 at least 68 nH where L3 is 27 nH; C4 and C5 not drawn; no
  ESD part of at most 0.6 pF; C42 47 pF against 100 pF); the antenna's current from its maker.
- S-49 (W3B-B): the V_BCKP TVS, and the coin cell's stored drain (about 31 uA typical, 78 uA worst) against a CR2032 datasheet
  the tree does not hold, into CONOPS's storage scenario.
- S-50 (W3B-C): C34 undeclared against the TPS23861's VPWR; KSENSA's Kelvin tap at R12 as a layout constraint.
- Tools: `safe_lines.py <netlist>` ignores `VERDICT_DIR`; `check_contracts.py` pairs rails by name alone (`page-drafts.md` 5).
- The integrator: apply `apply_registry.py`, the page drafts, the SOURCES entry (`sources-entries.yaml`, with
  `vendor/slkor/`), then the consolidated re-take of board B's netlist readings and the re-render.
