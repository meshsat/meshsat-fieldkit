# Decision 31, the protection topology review of boards A, D and E (AI review)

**MESHSAT-1357, 28 September 2026. An AI review, written by a session (worker d8dec31). It is not a qualified
review and it replaces none: the qualified power review R-PWR stands as the records time it.** Nothing of this kit
has been built, ordered or measured; every statement below is about schematics and makers' documents.

This is the review record that the holds of boards A, D and E ask for in `v2/ecad/tools/pcb_board_holds.yaml`
(`layout_entry_requires`, kind `review`, document `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md`):
"decision 31's protection topology reviewed on this board's current netlist: every exposed conductor, the part it
meets first, the clamp's rating against decision 34's level, and the placement and return-path constraints the
layout must keep (the clamp at the entry, its ground return short and on the plane)".

**That the record exists says the topology was read. It does not say the topology is sound.** Sections 2 and 9 say
what was found, and four of the findings are circuit changes.

**Why this review exists now, and what it closes.** The independent review of handover H3
(`v2/docs/reviews/2026-09-27-h3-independent-review.md`) found **H3-02**: TRN-001 on board A judged nothing of VIN_RAW's
entry, because `boards/a.json` named J_DOCK pins 1 and 2, ground since SC-55; `v2/docs/handover/RELEASE-H3.md` carries
it as **erratum f**, and the requirements registry as open item **S-88**, which limits TRN-001's reading on board A
wherever it is quoted. This review is the repair S-88 names: the declaration corrected (finding A-F1,
`apply_port_declarations.py`), the checker refusing a declared port that names no conductor and reporting a connector
pin no entry covers, the regression that a declared entry moved, narrowed, reclassified or omitted demands
reconciliation and never shrinks the coverage in silence (section 10, the reviewed set), and TRN-001 re-taken on board
A on the corrected declaration, which is the integrator's on the KiCad host. **S-88 closes on that re-take**
(`apply_registry_d31.py --close-s88` refuses until the reading is in the tree), not on this document.

## 1. What was read, and how

| input | identity |
|---|---|
| board A's netlist | `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net`, sha256 `0a2b59087bcc2678dac7e05b8b67c669f3d1957af846a0827bf59289dcea77d7` |
| board D's netlist | `v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net`, sha256 `7a2c0ac2190b141abd4793819a61bb975961527dc9e45716918bc7930d34f324` |
| board E's netlist | `v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net`, sha256 `56adc9746d61c4e016bbf8afe0d6f62d8f595c6c91bddadea9f9cd231edf715e` |
| board C's netlist, for one conductor of board A | `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`, sha256 first 16 `3fddbb3edcd4248a` |
| the tree | branch `fnd/d8dec31`, from `73ae2f21`, the tip of the set 6 candidate |
| the current readings of TRN-001 | branch `fnd/retake6` at commit `50e3b60b`: `port_protect_a` PASS of 26, `port_protect_d` PASS of 21, `port_protect_e` PASS of 13, each on the netlist above, written by `port_protect.py` sha16 `2d69facd3c25c8a4` |
| the ruled level | decision 34 and `v2/docs/OPERATING-ENVELOPE.md` sections 6 and 8 |
| the declarations | `v2/ecad/tools/boards/a.json`, `d.json`, `e.json` at `73ae2f21` |
| where each lead goes | the interface contracts of `v2/ecad/tools/pcb_interfaces.yaml` (named IF-... below), `v2/docs/GROUNDING-AND-SHIELDS.md`, `v2/docs/CASE-MARGINS.md` |

**Method.** The netlists were parsed by an S-expression reader (`v2/docs/records/d8dec31/netread.py`); nothing
was read by searching text. Every connector-class part was listed pin by pin
(`dump_connectors.py`, `readings/connectors-a.txt`, `-d.txt`, `-e.txt`), every candidate conductor was walked
from its pin through its series parts (`walk.py`, `readings/walk-*.txt`), and the tables of sections 4, 5 and 6
were written from the netlists by `make_pin_tables.py`, which stops if a pin that carries a supply or a signal is
covered by no entry. The declarations were treated as one of the things under review, not as the list of what to
review. Every rating quoted is in the ledger of section 8 with its document, its revision and its page.

**What a verdict means here.**

| verdict | meaning |
|---|---|
| PROTECTED AS DRAWN | a protection part rated to the ruled level stands on the conductor, the right way round, ahead of every semiconductor, and what it lets through is inside the rating of what stands behind it |
| PROTECTED WITH A CONSTRAINT | the same, provided the layout keeps what section 7 states, or provided a named part rating holds |
| NOT PROTECTED | a circuit finding: by the makers' own figures the protection does not keep the parts behind it inside their ratings. A change is proposed as an apply script |
| NOT PROTECTED, BY A BOUND | a conservative model's answer, not a demonstrated circuit defect: with every coulomb of the discharge network on the conductor and none into its loads, the conductor rises above a part's absolute maximum. The bound is stated with what it leaves out, and a change is proposed that puts the same bound under the ratings |
| CANNOT BE JUDGED AT THE DESK | no document held decides it. What would decide it is stated |

## 2. The result

**Conductors that leave the case or that a person touches, as this review enumerated them: 32 on 35 pins**
(board A 19, board D 8, board E 5), against 19 that the three declarations as they stood judged (20 with the conductor board A's J_DOCK entry meant and missed). **Verdicts: 2 protected as
drawn, 9 protected with a constraint, 4 not protected (3 demonstrated by the makers' own figures: D-F1 twice, on the two
push-to-talk conductors, and E-F1; 1 by a conservative bound: E-F3), 17 that cannot be judged at the desk.**

| board | conductors | as drawn | with a constraint | not protected | cannot be judged |
|---|---|---|---|---|---|
| A | 19 | 2 (PD_CC1, PD_CC2) | 6 (VIN_RAW, VBUS_WALL, USB_WALL_P, USB_WALL_N, PD_VBUS, MAIN_PB) | 0 | 11 (the antenna conductors) |
| D | 8 | 0 | 2 (the microphone conductors) | 2 (the push-to-talk conductors) | 4 (the antenna path twice, the speaker conductors) |
| E | 5 | 0 | 1 (PV_IN) | 2 (DC_IN, by the maker's own criterion; the pod's 3.3 V, by a bound) | 2 (the pod's SDA1 and SCL1) |

**The findings, by kind.** CIRCUIT is a defect or an omission of the design, shown by the makers' own figures; BOUND
is a conservative model's answer, which is not a demonstrated circuit defect and is never labelled one; INSTRUMENT is a
defect of a declaration or of a tool; NOTE is handed to a named reader and changes no verdict.

| id | kind | board | what | what is proposed |
|---|---|---|---|---|
| A-F1 | INSTRUMENT | A | the declaration named J_DOCK pins 1 and 2 as the shore and vehicle input; they are ground since SC-55, VIN_RAW stands on J_VR1 to J_VR4 in no entry, and TRN-001 read PASS having judged nothing of it. Thirteen more conductors of board A were in no entry: the MAIN button's lead and eleven antenna conductors | `apply_port_declarations.py`; the tool change of section 10 |
| A-F2 | CIRCUIT | A | the MAIN button's lead runs from the face to the LTC2954's PB pin with nothing on this board; the maker asks for a 5.1 k and 0.1 uF network at the pin for a button that is not beside the chip | `apply_gen_sch_a_mainpb.py` |
| X-C1 | CIRCUIT, not judged | C | the clamp of the MAIN button's pair, board C's U10, is referenced to board C's +3V3, which is off while the kit is off; the PB pin's microamp bias can then drain through the array's upper diode, and the button would read as pressed | for board C's owner: section 4.4 |
| A-N1 | NOTE for R-PWR | A | D2 clamps VIN_RAW at 64.5 V at its rated pulse; U2's VIN and VISNS are rated 60 V | section 4.3 |
| A-N2 | NOTE | A | D3 and D4 carry no distributor code on the netlist, so the netlist does not fix their maker | section 4.3 |
| D-F1 | CIRCUIT | D | the push-to-talk clamp breaks down at 5.5 to 9.5 V and clamps at 10 to 14 V on the same net as a gate input rated 6.5 V and -50 mA; in a negative discharge the gate's input conducts first | `apply_gen_sch_d_ptt.py` |
| D-F2 | CIRCUIT, not judged | D | the speaker clamp stands on the amplifier's output with nothing in series; the amplifier's output conducts before the clamp does, and its maker gives a human body model figure only | section 5.3 |
| D-F3 | CIRCUIT, not judged | D | J_USB3 is the touch lead of the monitor on the face since SC-HF-06: no clamp on the pair, and none of the port parts the hub's maker asks for on a downstream port | section 5.3 |
| D-F4 | CIRCUIT | D | C41 and C42 (1 uF) stand on the microphone conductors behind a clamp that reaches 37 V, and their value text states no voltage | a value text with the voltage, 50 V or more: section 5.3 |
| D-N1 | NOTE | D, A | the arrestor's turn-on is 90 V and the intent's own figure for the antenna conductor in transmit is 110 V | a question for the maker: section 9.3 |
| E-F1 | CIRCUIT | E | the ideal diode controller has no input capacitor, against its maker's minimum; with none, a negative discharge puts the clamp's voltage plus DC_P's across Q1 (60 V) and U3 (75 V) | `apply_gen_sch_e_cin.py` |
| E-F2 | CIRCUIT | E | F1 is a MINI blade of the 297 series class, rated 32 V DC, on a line specified to 36 V whose hot swap lets 40 V in | a fuse rated above 40 V: section 6.3 |
| E-F3 | BOUND, a conservative model's answer | E | the pod's 3.3 V conductor is the rail itself; its clamp breaks down above every part's rating on the rail, and the rail's 4.3 uF does not hold the bound under them | `apply_gen_sch_e_pod.py` |
| E-F4 | CIRCUIT, not judged | E | the pod's lead has no series element: a short outside takes the sensor controller's rail, and the pod shares SDA1 and SCL1 with five parts inside (U10, U14, U15, U17 and the module on J_LTG) | options in section 6.3; the pod's part is not picked |
| E-N1 | NOTE | E | a reversed panel finds D4's forward path at the panel's short-circuit current, which is below F2's rating | section 6.3 |
| E-N2 | NOTE for R-PWR | E | D10 clamps at 64.5 V at its rated pulse and U3's ANODE is rated 65 V | section 6.3 |
| T-1 | INSTRUMENT | tool | `port_protect.py` skipped a declared ground pin and never asked whether a connector was in any entry | done: section 10 |
| T-2 | INSTRUMENT | B, C | with the tool change boards B and C read INCONCLUSIVE until their tables name their internal connectors (290 and 39 pins) | for the owners of those two tables |
| T-3 | INSTRUMENT | tool | an `off_board` entry is believed on its text: the tool cannot ask what the named part is rated for | an open item: section 9.2 |

## 3. The level, and what it is not

**Decision 34 (ruled by the session on 21 September 2026) sets one transient level: IEC 61000-4-2 level 4, 8 kV
contact and 15 kV air**, for "every surface and conductor a person can touch" (`OPERATING-ENVELOPE.md` section
6). It is a design level and the level of test M7, not a compliance claim (owner ruling D-04). **No surge level is
ruled.** The envelope's second row "describes what is fitted", and the vehicle entry "is recorded as not qualified
for vehicle surge" (owner ruling D-16). The fast transient row has no source and is not a requirement.

So each conductor below is judged against an electrostatic discharge, and where a clamp is a surge part the
review says what the part is rated for and that no surge level asks anything of it. **An electrostatic discharge
rating is not a surge rating and neither is a human body model figure**: decision 31 said the second of these
itself, of the shore inlet's FET.

**The discharge, as a held document states it.** Nexperia's PESD5V0S1BA sheet (26 April 2024, Fig. 7, p.5) gives
the "IEC 61000-4-2 network" as "CZ = 150 pF; RZ = 330" ohm. This tree does not hold the standard, so the
figures this review uses are arithmetic on those two elements, and each is a bound:

| | 8 kV | 15 kV | what it bounds |
|---|---|---|---|
| charge, CZ times V | 1.2 uC | 2.25 uC | the rise of a conductor that carries capacitance to its return: charge over capacitance, with nothing taken by a clamp or a load |
| energy, half CZ times V squared | 4.8 mJ | 16.9 mJ | what any one part can be asked to absorb |
| V over RZ | 24.2 A | 45.5 A | the current the network's resistor allows. The standard's own first peak is not held here and is higher than this figure at 8 kV (INFERRED from the reviewer's knowledge of the standard, not from a document of this tree) |

## 4. Board A

### Board A: every connector pin (pcb-a-power.net, sha256 0a2b59087bcc2678)

56 connector-class parts, 156 pins, of which 82 carry a supply or a signal and 74 are ground.

| connector | pins that carry a supply or a signal (pin: net) | ground pins | class | where the lead goes |
|---|---|---|---|---|
| J_54V | 1: +54V_POE | 2 | INTERNAL | the 54 V lead to board B's PoE injector, inside the case (IF-AB-POWER); the conductor that leaves the case is board B's Ethernet jack, which board B declares |
| J_5V_DEV | 1: +5V_DEV | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_5V_S1 | 1: +5V_S1 | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_5V_S2 | 1: +5V_S2 | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_5V_S3 | 1: +5V_S3 | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_AB1 | 1: USB_D8_P; 2: USB_D8_N; 9: PI_SHDN_REQ; 10: PI_KILL; 11: SDA; 12: SCL; 13: EXP_INT; 14: TR_APRS; 15: EMCON_HW; 16: TX_INHIBIT_n; 17: SLOT_EN1; 18: SLOT_EN2; 19: SLOT_EN3; 20: ZEROIZE_HW; 21: SHORE_INHIBIT; 25: USB_E6_P; 26: USB_E6_N | 3 to 8, 22 to 24 | INTERNAL | the control ribbon to board B above this board, inside the case (IF-AB-RIBBON) |
| J_AB2 | 1: USB_WALL_P; 2: USB_WALL_N | 3 to 10 | INTERNAL | the wall-port ribbon to board B, inside the case (IF-AB-WALL): it carries the wall USB pair on from J_USBW, which is declared external and clamped on this board by U29 |
| J_BM1 | 1: RF_VHF | 2 | EXTERNAL, protection claimed off this board, not judged here | the VHF antenna conductor: it crosses this board from the SMA jack J_RF1 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM2 | 1: RF_HF | 2 | EXTERNAL, protection claimed off this board, not judged here | the HF antenna conductor: it crosses this board from the SMA jack J_RF2 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM3 | 1: RF_WIFI24 | 2 | EXTERNAL, protection claimed off this board, not judged here | the WIFI 2.4 antenna conductor: it crosses this board from the SMA jack J_RF3 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM4 | 1: RF_GNSS | 2 | EXTERNAL, protection claimed off this board, not judged here | the GNSS antenna conductor: it crosses this board from the SMA jack J_RF4 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM5 | 1: RF_SDR | 2 | EXTERNAL, protection claimed off this board, not judged here | the SDR antenna conductor: it crosses this board from the SMA jack J_RF5 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM6 | 1: RF_P2PA | 2 | EXTERNAL, protection claimed off this board, not judged here | the WIFI P2P A antenna conductor: it crosses this board from the SMA jack J_RF6 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM7 | 1: RF_P2PB | 2 | EXTERNAL, protection claimed off this board, not judged here | the WIFI P2P B antenna conductor: it crosses this board from the SMA jack J_RF7 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM8 | 1: RF_5G1 | 2 | EXTERNAL, protection claimed off this board, not judged here | the 5G MAIN antenna conductor: it crosses this board from the SMA jack J_RF8 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM9 | 1: RF_5G2 | 2 | EXTERNAL, protection claimed off this board, not judged here | the 5G DIV antenna conductor: it crosses this board from the SMA jack J_RF9 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM10 | 1: RF_IRIDIUM | 2 | EXTERNAL, protection claimed off this board, not judged here | the IRIDIUM antenna conductor: it crosses this board from the SMA jack J_RF10 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM11 | 1: RF_LORA | 2 | EXTERNAL, protection claimed off this board, not judged here | the LORA antenna conductor: it crosses this board from the SMA jack J_RF11 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_CN1 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CN2 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CN3 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CN4 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CP1 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_CP2 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_CP3 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_CP4 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_DOCK | 8: SHORE_INHIBIT; 9: USB_E6_P; 10: USB_E6_N; 12: DOCK_SPARE | 1 to 7, 11 | INTERNAL | signals between board A and board E inside the case, through the dock block E5 (interface contract IF-AE-DOCK): SHORE_INHIBIT on pin 8, the sensor controller's USB pair on pins 9 and 10, the hot stop line HOT-R1 on pin 12; the other pins are ground |
| J_HEAT | 1: VHEAT | 2 | INTERNAL | the pack heater mat in the pack bay, inside the case (IF-A-HEAT) |
| J_HF | 1: +12V_HF | 2 | INTERNAL | 12 V to the QMX HF unit in the lid tray, in the lid harness (IF-LID-HF). The lead stays inside the case; the unit's own panel is touched by the operator, and what reaches this lead through the unit is recorded in the review of decision 31 as not judged at the desk |
| J_MAINSW | 1: MAIN_PB | 2 | EXTERNAL, protected off this board (read on board C's netlist) | the MAIN button's lead from the panel: a person presses the button on the face, and its contact reaches the LTC2954's PB pin on this board |
| J_MEZZ1 | 1: USB_D8_P; 2: USB_D8_N; 7: TR_APRS; 8: TX_INHIBIT_n; 9: PA_EN; 10: SDA; 11: SCL; 12: EXP_INT; 13: +3V3; 15: ZEROIZE_HW; 16: AB_SPARE | 3 to 6, 14 | INTERNAL | the mezzanine harness to board D, inside the case (IF-AD-HARNESS) |
| J_MEZZ_PWR1 | 1: +5V_D8 | 2 | INTERNAL | board D's 5 V lead behind the eFuse U23, inside the case (IF-AD-HARNESS) |
| J_MON | 1: VMON | 2 | INTERNAL | the supply lead of the Xenarc monitor on the face, behind the eFuse U21 (IF-MON). The lead stays inside the case; the monitor's glass and bezel are touched by the operator, and what reaches this lead through the monitor is recorded in the review of decision 31 as not judged at the desk |
| J_PA | 1: +13V8_PA | 2 | INTERNAL | 13.8 V to the power amplifier module on the inside of the face plate (IF-A-PA); the lead stays inside the case |
| J_PRE1 | 1: PRECHG | none | INTERNAL | the pre-charge pin of the pack's positive over the dock block, inside the case: it mates first and reaches CELL+ through R1 (10 R) |
| J_RF1 | 1: RF_VHF | 2 | INTERNAL | the SMA jack of the pigtail to the VHF radio inside the case: the same conductor as J_BM1, which is declared external, and no part of this board is on it |
| J_RF2 | 1: RF_HF | 2 | INTERNAL | the SMA jack of the pigtail to the HF radio inside the case: the same conductor as J_BM2, which is declared external, and no part of this board is on it |
| J_RF3 | 1: RF_WIFI24 | 2 | INTERNAL | the SMA jack of the pigtail to the WIFI 2.4 radio inside the case: the same conductor as J_BM3, which is declared external, and no part of this board is on it |
| J_RF4 | 1: RF_GNSS | 2 | INTERNAL | the SMA jack of the pigtail to the GNSS radio inside the case: the same conductor as J_BM4, which is declared external, and no part of this board is on it |
| J_RF5 | 1: RF_SDR | 2 | INTERNAL | the SMA jack of the pigtail to the SDR radio inside the case: the same conductor as J_BM5, which is declared external, and no part of this board is on it |
| J_RF6 | 1: RF_P2PA | 2 | INTERNAL | the SMA jack of the pigtail to the WIFI P2P A radio inside the case: the same conductor as J_BM6, which is declared external, and no part of this board is on it |
| J_RF7 | 1: RF_P2PB | 2 | INTERNAL | the SMA jack of the pigtail to the WIFI P2P B radio inside the case: the same conductor as J_BM7, which is declared external, and no part of this board is on it |
| J_RF8 | 1: RF_5G1 | 2 | INTERNAL | the SMA jack of the pigtail to the 5G MAIN radio inside the case: the same conductor as J_BM8, which is declared external, and no part of this board is on it |
| J_RF9 | 1: RF_5G2 | 2 | INTERNAL | the SMA jack of the pigtail to the 5G DIV radio inside the case: the same conductor as J_BM9, which is declared external, and no part of this board is on it |
| J_RF10 | 1: RF_IRIDIUM | 2 | INTERNAL | the SMA jack of the pigtail to the IRIDIUM radio inside the case: the same conductor as J_BM10, which is declared external, and no part of this board is on it |
| J_RF11 | 1: RF_LORA | 2 | INTERNAL | the SMA jack of the pigtail to the LORA radio inside the case: the same conductor as J_BM11, which is declared external, and no part of this board is on it |
| J_USBC_OUT | 1: PD_VBUS; 2: PD_CC1; 3: PD_CC2 | 4, 5 | EXTERNAL | the USB-C outlet on the connector plate, out of the case: VBUS meets D4 (SMBJ18A) and CC1 and CC2 meet U31 (TPD2E2U06QDBZRQ1, the owner's D-17 array) at the connector, and port_protect judges both |
| J_USBW | 1: VBUS_WALL; 2: USB_WALL_N; 3: USB_WALL_P | 4 | EXTERNAL | the wall USB host port through the MIL-DTL-38999 receptacle: a person plugs a stranger's stick into this |
| J_VN1 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VN2 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VN3 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VN4 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VR1 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |
| J_VR2 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |
| J_VR3 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |
| J_VR4 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |

Not connectors, and on no lead: test points (25: TP3 to TP27).

### 4.1 The declaration, as it stood

`boards/a.json` declared three ports: J_DOCK pins 1 and 2 "shore and vehicle DC arriving over the dock from the
wall receptacle", J_USBW and J_USBC_OUT. **Finding A-F1, confirmed and sized.** Session choice SC-55 (EQ-16, 27
September 2026) moved VIN_RAW to four 9 A power pins, J_VR1 to J_VR4, and J_DOCK pins 1 to 4 "become ground". On
the netlist J_DOCK pins 1 to 7 and 11 are GND. `port_protect.py` skips a ground pin, so the J_DOCK entry judged
no conductor, and its 12 pins were still counted in the verdict's denominator of 26. VIN_RAW, the conductor the
entry was written for, was judged by nothing. It does carry its clamp (D2 on the pins' own net), so the PASS was
true of the board by accident and false of the instrument.

Beyond VIN_RAW the declaration missed thirteen conductors: MAIN_PB on J_MAINSW (board C declares the other end of
the same lead external, "the main switch on the face, which a person touches") and the eleven antenna conductors
that cross the board from J_RF1..11 to J_BM1..11.

### 4.2 Every exposed conductor

| conductor | pins | the first parts it meets | the protection that serves it | verdict |
|---|---|---|---|---|
| VIN_RAW | J_VR1.1 to J_VR4.1 | D2 (clamp), C11 and C12 (10 uF 100 V each), Q2 drain, D19 anode, R14, R195, R196, R200, TP13 | D2, SMCJ40A, on the pins' own net; ahead of it, on board E, the whole entry of section 6 | PROTECTED WITH A CONSTRAINT |
| VBUS_WALL | J_USBW.1 | C156 (22 uF 25 V), U29 pin 5, U32 pin 5 (the eFuse's output) | U29, USBLC6-2SC6, VBUS element, and C156 | PROTECTED WITH A CONSTRAINT |
| USB_WALL_N, USB_WALL_P | J_USBW.2, .3 | U29 pins 3 and 4, 1 and 6; then J_AB2 to board B's hub | U29 | PROTECTED WITH A CONSTRAINT |
| PD_VBUS | J_USBC_OUT.1 | D4 (clamp), C120 (10 uF 25 V), R138 (10 mOhm) to Q27 and U18, R139 (43 R) to U18, U18 pin 21 | D4, SMBJ18A, and C120 | PROTECTED WITH A CONSTRAINT |
| PD_CC1, PD_CC2 | J_USBC_OUT.2, .3 | U31 pins 1 and 2, C96 and C97 (330 pF), U18 pins 2 and 3 | U31, TPD2E2U06QDBZRQ1, and U18's own rated pins | PROTECTED AS DRAWN |
| MAIN_PB | J_MAINSW.1 | U1 pin 2, the LTC2954's PB input. Nothing else | off this board: board C's U10 behind FB1 and FB2, with C26 | PROTECTED WITH A CONSTRAINT, with findings A-F2 and X-C1 |
| RF_VHF, RF_HF, RF_WIFI24, RF_GNSS, RF_SDR, RF_P2PA, RF_P2PB, RF_5G1, RF_5G2, RF_IRIDIUM, RF_LORA | J_BM1.1 to J_BM11.1, with J_RF1.1 to J_RF11.1 on the same nets | no part of this board: each net is two connector pins | off this board: the arrestor that is the port's bulkhead | CANNOT BE JUDGED AT THE DESK |

### 4.3 Conductor by conductor

**VIN_RAW.** Clamp: D2, value text `SMCJ40A`, Littelfuse, code C224052. Stand-off 40.0 V against a line
specified 9 to 36 V (the intent's `v_work` 36.0); board E's hot swap stops above 40 V. Breakdown 44.40 to
49.10 V at 1 mA; clamping 64.5 V at 23.3 A; 1500 W at 10/1000 us; "IEC-61000-4-2 ESD 30kV(Air), 30kV (Contact)".
Polarity: a one-way part, cathode (pin 1, K) on VIN_RAW and anode on GND, drawn with a symbol that names its
cathode; the tool reads 0 reversed. Behind it: C11 and C12 100 V, Q2 100 V, D19 100 V, U34's supply behind R196
(1 k) 70 V, all above 64.5 V. **Not above it: U2, the LM5176, VIN and VISNS 60 V absolute maximum.** VIN stands
behind D19 and C207 (1 uF), which follow the peak; VISNS stands behind R195 (2 k), the resistor the maker asks
for above 40 V (SNVSAI1D 7.3.7), which limits a current and does not lower a voltage.
*Against the ruled level:* the conductor carries 20 uF, so the whole charge of the network moves it 0.06 V at
8 kV and 0.11 V at 15 kV (0.3 V and 0.56 V if bias left a fifth of the capacitance; the capacitors' bias curve is
not held). The clamp is not reached. *Against surge:* none is ruled. **Note A-N1 for R-PWR:** at D2's own rated
pulse the front end's controller is 4.5 V outside its absolute maximum. What bounds VIN_RAW on this board in
service is board E's hot swap (it stops above 40 V) with three SMCJ40 parts in a row (E's D10, D1 and D2, then
this D2), and whether that chain holds U2 under 60 V is a coordination to be computed by the qualified power
review, not asserted here. A straight line through the sheet's two points (49.10 V at 1 mA, 64.5 V at 23.3 A)
puts 60 V at about 16 A; that is this review's arithmetic, not a maker's figure.
*The path of the discharge:* D2's anode to board A's ground plane, then to board E over J_VN1 to J_VN4 and the
ground pins of J_DOCK, then through the second winding of board E's choke L2 to GND_V and the receptacle's return
pin. So this clamp is not at the entry and must not be counted as the entry's clamp: the entry's clamps are board
E's D10 and D1, which return to GND_V ahead of the choke.
*Between the clamp and the parts:* D19 and C207 to U2's VIN; R195 to VISNS; R14 over R15 to U34's sense; R196
and C210 to U34's supply; upstream, board E's F1.

**VBUS_WALL and the wall USB pair.** Clamp: U29, `USBLC6-2SC6`, ST, C7519, pins 1 and 6 on USB_WALL_P, 3 and 4 on
USB_WALL_N, 5 on VBUS_WALL, 2 on GND. "IEC 61000-4-2 level 4: 15 kV (air discharge), 8 kV (contact discharge)",
which is the ruled level exactly, with no margin stated above it at the contact figure on the front page
(Table 1 gives 15 kV for both as the absolute rating). Leakage is specified at 5.25 V; breakdown between VBUS and
GND 6 V minimum; clamping 12 V at 1 A and 17 V at 5 A, any I/O pin to GND; 3.5 pF maximum per line, "Compliant
with USB 2.0 requirements". VBUS_WALL is 5.0 V behind the eFuse U32 (limit 0.89 A), whose output is rated to the
smaller of 21 V and its input plus 0.3 V: the array's clamping voltage is above that, and what holds the rail in
a discharge is C156: 22 uF, 0.055 V at 8 kV and 0.10 V at 15 kV. The pair goes on to board B over J_AB2 with no
part of this board in series; the hub pins it reaches are board B's and were not read here.

**PD_VBUS.** Clamp: D4, value text `SMBJ18A (VBUS clamp at the outlet)`. **Note A-N2:** the netlist line carries
no distributor code (D3, `SMBJ5.0A` on +3V3, carries none either), so the netlist does not fix the maker;
`v2/vendor/SOURCES.yaml` names C151256, Littelfuse, for D4, and the figures here are that maker's. Stand-off
18.0 V against a line of 15 V at most (the outlet offers 5, 9 and 15 V); breakdown 20.00 to 22.10 V; clamping
29.2 V at 20.6 A; 600 W at 10/1000 us; 30 kV contact and air. One-way, cathode on PD_VBUS. Behind it: U18's
VBUS, ISNS and DSCG pins, 30 V sustained and 30 V for 1 ms: 0.8 V above the clamp at its rated pulse. Q27 40 V.
C120 is a 25 V part, under the clamp's voltage at its rated pulse and above the line's 15 V. The conductor
carries 10 uF: 0.12 V and 0.225 V. The clamp is not reached by the ruled level. The maker's own application
section (SLVSDG8B 9.1.1, p.36) shows a clamp on the VBUS path for exactly this.

**PD_CC1, PD_CC2.** Two layers. U31, `TPD2E2U06QDBZRQ1`, TI, C488151: stand-off 5.5 V against a line of 5.5 V
at most (the intent's node); breakdown 6.5 to 8.5 V; clamping 9.7 V at 1 A and 12.4 V at 5 A (typical, by
transmission line pulse); "IEC 61000-4-2 ... Contact discharge +-25000 ... Air-gap discharge +-30000" volts;
1.5 pF typical and 1.9 pF maximum. And U18's own pins: "IEC 61000-4-2 contact discharge, CC1, CC2 +-8000 ...
air-gap discharge, CC1, CC2 +-15000", with the maker's note that these "were passing limits that were obtained
on an application-level test board", and its statement that "The device has ESD protection built into the CC1
and CC2 pins so that no external protection is necessary" (9.1.1). U18's sustained rating on these pins is 6 V,
under U31's clamping voltage; it is the pins' own rating at the ruled level that carries the verdict, and U31
stands in front of it. Capacitance: 330 pF and 1.9 pF against the receiver's window of 200 to 600 pF
(SLVSDG8B p.7, C(RX)).

**MAIN_PB.** On this board the net is J_MAINSW pin 1 and U1 pin 2. The lead is made up at build (interface
contract IF-AC-MAINSW) and its other end is board C's J_MAINSW; read on board C's netlist, the switch SW_MAIN
(C&K ATP19) reaches that lead through the beads FB1 and FB2 (600 R), with C26 (100 nF) across the pair and U10,
a USBLC6-2SC6, on both conductors. That is the clamp at the entry, rated to the ruled level, and board A's
corrected declaration names it. U1's own figure is "+-10kV ESD HBM on PB Input" (2954fb p.1), a human body
model figure; its PB pin is rated -6 to 33 V. **Finding A-F2:** between board C's clamp and U1 there is the
lead and nothing, and the maker asks for a network at the pin when the button "is physically located far from
the LTC2954 PB pin": "A 5.1k resistor and a 0.1uF capacitor should suffice for most noisy applications"
(2954fb p.12 and p.13). The proposed change draws it.

### 4.4 Finding X-C1, on board C, for its owner

U10's pin 5 is on board C's +3V3. Board C's only supply is PANEL_5V from +5V_DEV (interface contract
IF-BC-PANEL), a rail that starts after a MAIN press. So while the kit is off, U10's rail pin is at 0 V and the
PB conductor is live: the LTC2954 runs from VBAT and holds its PB pin at its open-circuit voltage, 1 to 2 V,
from a source of microamps (2954fb p.3: 1 to 12 uA at 1 V, 3 to 15 uA at 0.6 V). An array of this kind joins each
line to its rail pin through a diode (DS4260 p.5, the device's own diagram). With the rail at 0 V that diode is
forward biased by the PB conductor, and the pin's few microamps flow into the dead rail. The PB threshold is 0.6
to 1.0 V, falling. **If the diode holds less than that at a few microamps, the LTC2954 reads a pressed button for
as long as the kit is off.** A silicon junction at microamps holds a few hundred millivolts (INFERRED: DS4260
gives the forward voltage at 10 mA only, 1.1 V maximum, and no curve). **CANNOT BE JUDGED AT THE DESK.** What
would decide it: the array's forward characteristic at 1 to 15 uA from ST, or one measurement on a bench. What
would remove the question: a clamp that refers to no rail, such as the two-way single-line part board D already
buys (PESD5V0S1BA: stand-off 5 V, leakage 5 nA typical and 100 nA maximum at 5 V), which is a substitution and
a mismatch until board C's owner has proven it. The same question stands for U11 on the PI button's pair, held
at board A's +3V3 through R3 while board C's +3V3 may be off.

### 4.5 The antenna conductors, and two leads that are not exposed

**Eleven antenna conductors cross board A with no part on them.** Each leaves through the dock plug, a jumper
of RG-316 and a gas-discharge arrestor that is the port's bulkhead (interface contract IF-AE-RF; CASE-MARGINS.md
C2 and C4). The arrestor's sheet (PolyPhaser GTH-SFF-AL) states: DC to 6 GHz, "Operating Voltage (DC) 60 Volts"
maximum, "Input Power, CW 150 Watts", "Surge Current 10 kA", "Turn On Voltage 90 Volts" typical. It states no
waveform for the 10 kA, no let-through voltage or energy, and no IEC 61000-4-2 figure. **The part is rated for
surge and the ruled level is an electrostatic discharge.** A gas tube turns on at a voltage that rises with the
steepness of the edge, and a discharge of this kind may have passed before it does (INFERRED, general knowledge;
the sheet does not say). What the conductor then meets is the radio at the far end of its pigtail, which is on
another board or is a bought module. **CANNOT BE JUDGED AT THE DESK**, for all eleven. What would decide it: the
maker's let-through figures (section 9.3), each radio's own antenna-port rating, or test M7. For board A itself
the constraint of section 7 is what matters: nothing of this board may share a path with these conductors.

**J_MON and J_HF stay inside the case** and are declared internal. Each feeds a bought unit that the operator
touches (the monitor's glass and bezel; the HF unit's panel), and the envelope's own test names "the display
bezel" as a discharge point. What reaches the lead through the unit depends on the unit. VMON carries no
capacitor on this board (the net is J_MON pin 1 and U21 pin 5); +12V_HF carries 330 uF. Not exposed conductors,
not judged, and recorded so that test M7 looks at both.

## 5. Board D

### Board D: every connector pin (pcb-d-aprs.net, sha256 7a2c0ac2190b141a)

10 connector-class parts, 42 pins, of which 26 carry a supply or a signal and 16 are ground.

| connector | pins that carry a supply or a signal (pin: net) | ground pins | class | where the lead goes |
|---|---|---|---|---|
| J_ANT | 1: RF_ANT | 2 | EXTERNAL, protection claimed off this board, not judged here | the VHF antenna SMA: an outdoor conductor with a 30 W transmitter behind it, arrested in the wall rather than on the board |
| J_FLANGE | 1: FLANGE_NTC | 2 | INTERNAL | the thermistor lead of the power amplifier's flange, inside the case (IF-D-FLANGE) |
| J_HARN1 | 1: USB_D8_P; 2: USB_D8_N; 7: TR_APRS; 8: TX_INHIBIT_n; 9: PA_EN; 10: SDA; 11: SCL; 12: EXP_INT; 13: +3V3; 15: ZEROIZE_HW; 16: AB_SPARE | 3 to 6, 14 | INTERNAL | the mezzanine harness from board A, inside the case (IF-AD-HARNESS) |
| J_HS1 | 1: HS1_SPK; 3: HS1_MIC; 5: PTT_HS1_n | 2, 4 | EXTERNAL | a headset jack on the face, which a person plugs a headset into |
| J_HS2 | 1: HS2_SPK; 3: HS2_MIC; 5: PTT_HS2_n | 2, 4 | EXTERNAL | the second headset jack |
| J_PAIN | 1: RF_DRV | 2 | INTERNAL | the drive coax to the power amplifier module on the inside of the face plate (IF-A-PA) |
| J_PAOUT | 1: RF_PAOUT | 2 | EXTERNAL, protection claimed off this board, not judged here | the power amplifier output to the antenna path, which reaches the same arrested bulkhead |
| J_PWR1 | 1: +5V_D8 | 2 | INTERNAL | the 5 V lead from board A's eFuse U23, inside the case (IF-AD-HARNESS) |
| J_USB3 | 1: +5V_D8; 2: USB3_N; 3: USB3_P | 4 | INTERNAL | the touch USB lead of the Xenarc monitor on the face (IF-MON, session choice SC-HF-06). The lead stays inside the case; the monitor's glass and bezel are touched by the operator, no clamp stands on this pair, and the review of decision 31 records it as finding D-F3, not judged at the desk |
| J_VGG | 1: VGG_SW | 2 | INTERNAL | the gate bias lead to the power amplifier module on the inside of the face plate (IF-A-PA) |

Not connectors, and on no lead: solder jumpers (2: JP1 to JP2); the relay (1: K1); indicator LEDs on the board (6: LED1 to LED6); test points (27: TP1 to TP27).

### 5.1 The declaration, as it stood

Four ports: J_ANT and J_PAOUT, each declared protected off the board by the arrestor, and the two headset leads
J_HS1 and J_HS2. No entry names a ground pin. It covers every conductor of this board that leaves the case. It
does not name J_USB3, which session choice SC-HF-06 (27 September 2026) gave to the touch lead of the monitor
on the face; the corrected table declares it internal and says what is not judged.

### 5.2 Every exposed conductor

| conductor | pin | the first parts it meets | the protection that serves it | verdict |
|---|---|---|---|---|
| RF_ANT | J_ANT.1 | K1 pin 6, the relay's moving contact. At rest the relay joins it to U2 pin 12, the exciter's antenna pin; keyed, to L2, L1 and J_PAOUT | off this board: the arrestor at the VHF bulkhead | CANNOT BE JUDGED AT THE DESK |
| RF_PAOUT | J_PAOUT.1 | C58 (22 pF 500 V), L1 (68 nH); beyond the coax, the power amplifier module's output | the same arrestor, through K1 and the filter | CANNOT BE JUDGED AT THE DESK |
| HS1_SPK, HS2_SPK | J_HS1.1, J_HS2.1 | D9, D12 (clamps); U7 pins 16 and 5, the amplifier's outputs | D9 and D12, PESD5V0S1BA | CANNOT BE JUDGED AT THE DESK (finding D-F2) |
| HS1_MIC, HS2_MIC | J_HS1.3, J_HS2.3 | D10, D13 (clamps); C44, C45 (1 nF NP0); C41, C42 (1 uF) into R40, R41 (4.7 k); JP1, JP2 into R43, R44 (2.2 k) | D10 and D13, PESD12VL1BA | PROTECTED WITH A CONSTRAINT (finding D-F4) |
| PTT_HS1_n, PTT_HS2_n | J_HS1.5, J_HS2.5 | D11, D14 (clamps); C49, C50 (100 nF); R68, R70 (10 k); U9 pins 1 and 2; Q4 and Q5 source | D11 and D14, PESD5V0S1BA | NOT PROTECTED (finding D-F1) |

### 5.3 Conductor by conductor

**The antenna path.** The arrestor is the part of section 4.5. In transmit the conductor carries 30 W: 38.7 V
rms and 54.8 V peak into 50 ohm, and the intent's own node gives 110 V for RF_ANT, the peak with the wave wholly
reflected. **Note D-N1:** that is above the arrestor's "Turn On Voltage 90 Volts" and its "Operating Voltage
(DC) 60 Volts", while its "Input Power, CW 150 Watts" is 122 V peak into a matched load. The sheet does not say
at what peak radio-frequency voltage the tube conducts, nor into what load the 150 W holds. What the relay K1
(Omron G6K-2F-Y) adds: "impulse withstand voltage of 2,500 V for 2 x 10 us" between contacts on the -Y models. The
exciter's sheet (NiceRF SA868, v1.3) gives no rating for its antenna pin and no discharge figure; the power
amplifier's (Mitsubishi RA30H1317M1) gives "Load VSWR Tolerance ... No degradation or destroy" at 20:1 and no
discharge figure. **CANNOT BE JUDGED AT THE DESK.**

**The speaker conductors (finding D-F2).** D9 and D12, `PESD5V0S1BA`, Nexperia, C19224: two-way; stand-off 5 V
against a swing the board's author reads as 1.9 V at most; breakdown 5.5 to 9.5 V; clamping 10 V at 1 A and 14 V
at 12 A; 130 W and 12 A at 8/20 us; "IEC 61000-4-2 (contact discharge) 30 kV"; 35 pF typical, 45 pF maximum
(177 kohm at 20 kHz: nothing to an audio output). Behind it, on the same net, U7's output. TI gives the output
no absolute maximum voltage; its recommended conditions allow "Voltage applied to Output; OUTR, OUTL (when EN =
0 V) -0.3 3.6 V", and its discharge figure is a human body model one, "+-8000" on OUTL and OUTR, which the front
page says is "simplifying end equipment compliance to the IEC 61000-4-2 ESD standard". The amplifier's output
works inside rails of 1.9 V and minus 1.9 V, so its own structures conduct from about 2.5 V in either direction
(INFERRED), well before the clamp's 5.5 V, and nothing in series makes the current choose the clamp. What the
output then takes no document states. **CANNOT BE JUDGED AT THE DESK.** What would decide it: TI's figure for
these outputs under IEC 61000-4-2 on a board (the sheet has none), or test M7. What would remove the question: a
series element between the jack's clamp and the output, a few ohms or a bead, whose size the headset's impedance
decides; that is board D's owner's.

**The microphone conductors (finding D-F4).** D10 and D13, `PESD12VL1BA`, Nexperia, C38558: two-way; stand-off
12 V against 5.23 V at most (the electret bias with no headset); breakdown 14.2 to 16.7 V at 5 mA; clamping 20 V
at 1 A and 37 V at 5 A; 200 W and 5 A at 8/20 us; "IEC 61000-4-2; contact discharge ... 30 kV", "air discharge
15 kV"; 19 pF typical. Behind the clamp no pin stands on the conductor: C41 and C42 lead through R40 and R41
(4.7 k) to the amplifier U8, whose inputs are rated 10 mA (TLV9062, SBOS839N p.10): 37 V over 4.7 k is 7.9 mA.
JP1 and JP2 lead through R43 and R44 (2.2 k) to +5V_D8, which carries 120 uF and its own clamp D1. **The
constraint is a part rating:** C44 and C45 carry code C113780 and the value `1n NP0`; C41 and C42 carry the
value `1u`, no code and no voltage, on a conductor whose clamp reaches 37 V and breaks down at 16.7 V at the
most. They need a part of 50 V or more, said in the value text so the bill carries it.

**The push-to-talk conductors (finding D-F1).** D11 and D14 are the speaker's part. On the same net stand C49
and C50 (100 nF), the pull-ups R68 and R70, U9's inputs and the sources of Q4 and Q5. U9 is `74LVC1G08`, code
C19829591, a TECH PUBLIC 74LVC1G08GV; its sheet has no text layer and was read from a render of page 2: "Input
Voltage VIN -0.5 ~ 6.5 V", "Input Clamp Current IIK VIN<0 -50 mA", and note 2, "The input and output voltage
ratings may be exceeded if the input and output current ratings are observed". Rule TRN-001 asks that the
protection "clamps below the protected part's absolute maximum". *Positive:* the clamp may not begin to conduct
until 9.5 V and clamps at 10 to 14 V, above 6.5 V; and the 100 nF takes 0.55 uC to reach 5.5 V and then holds
what the clamp left until the pull-up has taken it away, 1 ms (10 k, 100 nF). *Negative:* the gate's input clamp
conducts from 0.5 V below ground, the external clamp from 5.5 V below it at the earliest, so the gate's own input
is the first part to conduct and nothing limits its current. Q4 and Q5 see at most 17.3 V gate to source (3.3 V
on the gate, the source at minus 14 V) against 20 V (JSCJ 2N7002, p.1), and conduct, which passes the negative
voltage on to U16's input behind them. **NOT PROTECTED.** The proposed change puts 1 k between the jack side and
the logic side and two Schottky diodes from the logic side to its rails, with parts the set already buys.

**J_USB3, declared internal (finding D-F3).** USB3_P and USB3_N go from the header through 22 ohm to the hub's
port 3 (U4, TUSB2046I: pins rated to its supply plus 0.5 V, human body model 4000 V), with 15 k to ground, and
pin 1 is the rail +5V_D8 itself. No clamp stands on the pair, where the pair of the same hub that comes from
board A carries one (U5). The hub's maker asks two things of a downstream port (SLLS413L p.17): "A large bulk
low-ESR capacitor of 22 uF or larger is required on each downstream port's VBUS", and "ferrite beads on the VBUS
pins of the downstream USB port connections are recommended for both ESD and EMI reasons. A 0.1-uF capacitor on
the USB connector side of the ferrite provides a low impedance path to ground for fast rise time ESD current".
Neither is drawn, and the record already carries that a fault on this lead is cleared only by board A's eFuse
(HF-F06). The lead stays inside the case; what reaches it through the monitor is not known. **CANNOT BE JUDGED AT
THE DESK**; what would remove the question is the array the design already buys, at the header, and the maker's
two port parts.

## 6. Board E

### Board E: every connector pin (pcb-e1-dock.net, sha256 56adc9746d61c4e0)

18 connector-class parts, 51 pins, of which 32 carry a supply or a signal and 19 are ground.

| connector | pins that carry a supply or a signal (pin: net) | ground pins | class | where the lead goes |
|---|---|---|---|---|
| J_BATT | 2: CELL+ | 1 | INTERNAL | the pack's power lead from board P on its XT60, inside the case (IF-PE-PACK); the pack's own protection is on board P |
| J_BLK | 8: SHORE_INHIBIT; 9: USB_E6_P; 10: USB_E6_N; 12: BLK_SPARE | 1 to 7, 11 | INTERNAL | the twelve signal wires to the dock block E5 and through it to board A, inside the case (IF-AE-DOCK): SHORE_INHIBIT, the sensor controller's USB pair and the hot stop line HOT-R1 |
| J_DCF | 1: +3V3_E6; 3: DCF_PULSE | 2 | INTERNAL | the DCF77 receiver module beside this board, inside the case (IF-E-SENSORS) |
| J_DCIN | 1: DC_IN | 2 | EXTERNAL | shore and vehicle DC entry from the MIL-DTL-38999 wall receptacle |
| J_FAN1 | 1: CELL_F; 2: FAN1_SW; 3: FAN1_TACH | none | INTERNAL | mixer fan 1 under the plate, inside the sealed case (IF-E-FANS) |
| J_FAN2 | 1: CELL_F; 2: FAN2_SW; 3: FAN2_TACH | none | INTERNAL | mixer fan 2 under the plate, inside the sealed case (IF-E-FANS) |
| J_GEIGER | 1: +5V_GEIGER; 3: GEIGER_PULSE | 2 | INTERNAL | the Geiger counter module beside this board, inside the case (IF-E-SENSORS) |
| J_LTG | 1: +3V3_E6; 3: SDA1; 4: SCL1; 5: LTG_IRQ | 2 | INTERNAL | the lightning sensor module beside this board, inside the case (IF-E-SENSORS). It shares the sensor bus SDA1 and SCL1 with the outside pod J_POD, which is declared external |
| J_POD | 1: +3V3_E6; 3: SDA1; 4: SCL1 | 2 | EXTERNAL | the outside climate and ultraviolet sensor pod, through an M8 sealed receptacle on the connector plate |
| J_SMB | 1: SMBC; 2: SMBD; 4: PRES_LEAD | 3 | INTERNAL | the SMBus lead to board P's gauge, inside the case (IF-PE-PACK) |
| J_SOLAR | 1: PV_IN | 2 | EXTERNAL | the solar input, a long outdoor lead by definition |
| J_TAMP | 1: TAMPER_LEAD | 2 | INTERNAL | the lid and tamper reed sensor's lead under the frame, inside the case (IF-E-TAMP) |
| PAD_W1 | 1: WATER_A | none | INTERNAL | water electrode A on the case floor, bare copper under the plate, inside the sealed case (IF-E-WATER): fed from +3V3_E6 through R38 (1 M) |
| PAD_W2 | 1: WATER_SENSE | none | INTERNAL | water electrode B on the case floor, bare copper under the plate, inside the sealed case (IF-E-WATER): into the sensor controller's ADC0 past R39 (1 M) and C51 (100 nF) |
| P_CN | none | 1 | carries no conductor | a return: every pin is on GND |
| P_CP | 1: CELL_F | none | INTERNAL | the pack's positive to the dock block E5 on a 12 AWG wire, inside the case (IF-AE-DOCK) |
| P_VN | none | 1 | carries no conductor | a return: every pin is on GND |
| P_VR | 1: VIN_RAW | none | INTERNAL | VIN_RAW to the dock block E5 on a 12 AWG wire, inside the case (IF-AE-DOCK): the bus behind this board's own entry protection, which board A declares external at J_VR1 to J_VR4 |

Not connectors, and on no lead: solder jumpers (1: JP1); indicator LEDs on the board (2: LED1 to LED2); test points (13: TP1 to TP13).

### 6.1 The declaration, as it stood

Three ports: J_DCIN, J_SOLAR and J_POD. No entry names a ground pin, and the three cover every conductor of this
board that leaves the case. J_DCIN pin 2 is on GND_V, the entry's own return, which the tool reads as a ground
and skips; it is a conductor that leaves the case, and section 6.3 says what it meets.

### 6.2 Every exposed conductor

| conductor | pin | the first parts it meets | the protection that serves it | verdict |
|---|---|---|---|---|
| DC_IN | J_DCIN.1 | F1 (the 10 A blade), TP1; behind F1 on DC_F: D10 (clamp), Q1 source, U3 pins 3 and 6, C4 (to U3's VCAP), R1 | D10, SMCJ40CA, behind the fuse and ahead of Q1; D1, SMCJ40A, behind Q1 | NOT PROTECTED in the negative direction (finding E-F1); finding E-F2 |
| GND_V, the entry's return | J_DCIN.2 | the anodes of D10 and D1, C2, C6, U3 pin 2, U6 pin 5, Q8 source, three resistors, and L2's second winding to GND | it is the clamps' return | not a verdict: see 6.3 |
| PV_IN | J_SOLAR.1 | F2 (10 A blade); behind it on PV_P: D4 (clamp), 225 uF, Q3 drain, U5 pins 32 to 34, R8, R14, TP5 | D4, SMCJ28A, and the bulk capacitors | PROTECTED WITH A CONSTRAINT |
| +3V3_E6 | J_POD.1 | the rail: sixteen capacitors, U10, U11, U14, U15, U17 pin 5, D9 pin 5, the modules on J_DCF and J_LTG, eighteen resistors | D9's VBUS element, and the rail's 4.3 uF | NOT PROTECTED, by a bound (finding E-F3) |
| SDA1, SCL1 | J_POD.3, .4 | D9 pins 1 and 6, 3 and 4; R36, R37 (4.7 k); U10, U14, U15, U17, and the module on J_LTG | D9, USBLC6-2SC6 | CANNOT BE JUDGED AT THE DESK (finding E-F4) |

### 6.3 Conductor by conductor

**DC_IN.** The chain, read from the netlist: J_DCIN.1, F1, DC_F with D10 to GND_V, Q1 (source on DC_F, drain on
DC_P), DC_P with D1 and C2 to GND_V, R19, Q7 (the hot swap), L2, VIN_RAW with D2 to GND. D10, `SMCJ40CA`,
Littelfuse, C80273: the two-way part of the SMCJ40 row, stand-off 40.0 V against a line of 36 V and a hot swap
that stops above 40 V, breakdown 44.40 to 49.10 V, clamping 64.5 V at 23.3 A, either way round. D1, `SMCJ40A`,
C224052, one-way, cathode on DC_P. The clamps' return is GND_V, the receptacle's own return pin, ahead of the
choke: the discharge does not cross the board's ground to return. That is the right shape, and it is what
decision 31 ruled.

**Finding E-F1.** U3 is an LM74700-Q1. Its maker: "Minimum required capacitance for charge pump VCAP and
input/output capacitance are: VCAP: Minimum 0.1 uF ... CIN: minimum 22 nF of input capacitance; COUT: minimum 100
nF of output capacitance" (SNOSD17G 10.1.1.2.3, p.17). C4 is the VCAP capacitor and C2 is COUT; **DC_F carries
no capacitor to GND_V.** With none, a discharge drives DC_F to D10's voltage. *Positive:* 64.5 V at 23.3 A
against U3's ANODE, 65 V (**note E-N2:** 0.5 V at the clamp's rated pulse, and the network allows 24.2 A at 8
kV); Q1 conducts forward into DC_P. *Negative:* D10 conducts from 44.4 V and clamps at 64.5 V, and Q1 then
carries that plus whatever DC_P holds, up to 36 V: 80 to 100 V across a 60 V FET and across U3's CATHODE to
ANODE, rated 75 V. The maker names exactly this as the criterion: "the cathode to anode voltage seen is equal to
(TVS Clamping voltage + Output capacitor voltage)" (10.1.1.3, p.18). Q1 is "100% avalanche tested" and its single
pulse avalanche energy is 50 mJ, above the 16.9 mJ the network holds at 15 kV, so the FET itself is bounded; U3's
pin is not. The generator's own comment records the negative case for a surge, which is not claimed; for a
discharge, which is the ruled level, it is a finding. **NOT PROTECTED in the negative direction.** With 1 uF from
DC_F to GND_V the whole charge moves DC_F 1.2 V at 8 kV and 2.25 V at 15 kV, and ten times that if bias left a
tenth of it: the clamp is not reached in either direction. After the change: PROTECTED WITH A CONSTRAINT.

**Finding E-F2.** F1's value is `10 A mini blade (Keystone 3568 holder): vehicle input`, with no code; the
holder takes "Littelfuse Mini 297 or 997 series/Bussmann ATM series or equivalent" (Keystone, catalogue page
M65), and the 297 series the record holds is "MINI BLADE FUSE RATED 32V": "Voltage Rating: 32 VDC",
"Interrupting Rating: 1000A @ 32 VDC". The line is specified to 36 V and the hot swap admits 40 V. **Between 32
and 40 V the fuse is asked to clear a fault above its voltage rating**, and the fault it must clear is a short
behind it fed by a vehicle battery. The same part on the panel input (F2, 25 V at most) and on the pack (F3,
16.8 V at most) is inside its rating. Proposed: a fuse of the same form rated above 40 V. The maker's 58 V MINI
series is the candidate, and its sheet is not held: littelfuse.com answered this host 403 and the Internet
Archive held no copy at the addresses tried on 27 September 2026. That its series number is 997, the one the
holder's page names, is INFERRED and owed a document. No apply script is written for a part whose sheet nobody
has read.

**The entry's return, GND_V.** It reaches the board's ground through L2's second winding and through nothing
else. A discharge to the return pin itself goes through the choke into the ground plane; one to the positive pin
returns through the clamps without crossing it. No chassis net exists on any board (GROUNDING-AND-SHIELDS.md;
rule GND-002 is open), so where a discharge to the receptacle's shell goes is decided there, not here.

**PV_IN.** D4, `SMCJ28A`, Littelfuse, C224047: one-way, cathode on PV_P; stand-off 28.0 V against 25 V at most
(a cold 36-cell panel open circuit, the generator's figure); breakdown 31.10 to 34.40 V; clamping 45.4 V at
33.1 A. Behind it 225 uF (the two 100 uF parts are rated 35 V), Q3 60 V by its value text (the BSC028N06NS sheet
is not held), U5's VIN and sense pins 80 V. The whole charge of the network moves 225 uF by 0.005 V and 0.010 V.
The return is the board's ground directly (J_SOLAR.2 is GND, not GND_V). PROTECTED WITH A CONSTRAINT. **Note
E-N1:** D4 is one-way with its anode on ground, so a reversed panel finds its forward path at the panel's
short-circuit current, about 6 A (INFERRED in IF-EXT-DC), under F2's 10 A: nothing clears it, and the part's
rating for it is a surge figure ("Peak Forward Surge Current, 8.3ms ... 200 A"), not a continuous one. The
receptacle is keyed, so this takes a lead wired wrongly. For board E's owner.

**The pod's 3.3 V conductor (finding E-F3).** J_POD.1 is the rail. D9's VBUS element breaks down at 6 V at the
least, above the absolute maximum supply of every part on the rail (SGP41 VDDH 3.6 V, RP2040 IOVDD 3.63 V,
BMI270 4 V, BME688 4.25 V), so it clamps nothing before those ratings. The rail carries 4.3 uF. **The bound,
which is a conservative model's answer:** every coulomb on the rail, none into its loads, from the regulator's
maximum of 3.333 V (1 percent): 3.61 V at 8 kV and 3.86 V at 15 kV. The loads take the excess away in
microseconds (0.35 A typical), and an absolute maximum states no duration. By the bound, NOT PROTECTED; the
proposed change adds 20 uF at the header, which puts the same bound at 3.38 V and 3.43 V.

**The pod's lead (finding E-F4).** Nothing limits the current into the outside lead: a short of its 3.3 V
conductor to its return takes +3V3_E6, and with it the sensor controller and the hot stop line it drives. SDA1
and SCL1 are one net each from the pod's pin to the sensor controller, the climate sensor, the motion sensor,
the battery-bay gas sensor and the lightning module, with D9 on them and no series part: a fault on the outside
lead is a fault of the whole sensor bus, and what D9 lets through reaches five parts whose pins are rated to
their supply plus 0.3 to 0.5 V. D9 clamps a line to its rail pin plus a diode and to ground (DS4260 p.5), so its
voltage on these lines is the rail's plus about a volt, which is above those pin ratings as any clamp of this
kind is; what each pin takes of it no document states. **CANNOT BE JUDGED AT THE DESK.** What would decide it:
test M7 at the pod's receptacle. What would remove the question: series resistors between D9 and the bus inside,
or the pod on a bus of its own; and a series element on the feed, sized by the pod's supply current, which waits
for the pod's part (IF-E-POD lists it TBD). The contract's own open line, "ESD protection at the plate", stands.

## 7. What the layout must keep

These are the constraints this review hands on. Each is a condition of the verdicts above.

**For every clamp** (the makers' own clauses: Nexperia PESD5V0S1BA section 10, p.6, items 1, 2, 3, 4, 6, 7 and 8;
ST DS4260 2.3, p.6; TI SLLS413L 11.1.1 item 2):

1. The clamp sits at the connector, between the connector's pin and everything else: the conductor reaches the
   clamp's pad first and leaves from that pad. No branch leaves between the pin and the clamp.
2. The clamp's return is its own via or vias into the ground plane at its pad, not a track and not a via shared
   with another part's return ("Avoid using shared transient return paths to a common ground point").
3. Nothing runs between the connector and the clamp, and no conductor behind a clamp runs beside one ahead of it
   ("Avoid running protected conductors in parallel with unprotected conductors").
4. For an array that refers to a rail (U29 on board A, U5 and D9 on boards D and E): "the track from data lines
   to I/O pins, from VCC to VBUS pin and from GND plane to GND pin must be as short as possible", and a capacitor
   of the rail stands at the rail pin.

**Per port.**

| port | the clamp and where it sits | its return | what must not run between | the figure |
|---|---|---|---|---|
| A, VIN_RAW | D2 at the four pins J_VR1 to J_VR4, with C11 and C12 beside it | D2's anode into the plane beside J_VN1 to J_VN4, the return pins of the same conductor | no signal of the front end; R195, R14, R196 and R200 leave from D2's pad, not from the pins | the pins to D2: as short as the four pins' own pour allows, and D2 inside that pour |
| A, J_USBW | U29 and C156 at the header; the pair passes U29's pads before J_AB2's | U29 pin 2 and C156 into the plane at their pads | the pair is routed as a pair from the header through U29 to J_AB2, beside nothing | header to U29 within the 3 mm this project already uses for a part at its pin |
| A, J_USBC_OUT | D4, C120 and U31 at the header, ahead of R138, R139 and U18; C96 and C97 at U18 | D4 and U31 each into the plane at its pad | the CC pair beside PD_VBUS only ahead of the clamps | the same 3 mm |
| A, J_MAINSW (after A-F2) | the 5.1 k and the 100 nF at U1 pin 2 ("close to the PB pin") | the 100 nF into the plane at U1's ground pin | MAIN_PB_LEAD away from the switching nodes of the seven power stages | the lead side of the resistor as short as the header allows |
| A, J_BM and J_RF | no part: the conductor is a 50 ohm track between two connectors | the connectors' own ground pins into the plane, with ground vias beside the track | nothing of this board beside or under these tracks on the next layer except ground | clearance of these tracks to every other net by the 31 to 500 V row below, since the arrestor turns on at 90 V |
| D, J_ANT, J_PAOUT | as board A's antenna conductors; K1, L1, L2, C58 to C60 are the only parts on them | the same | the same | the same row |
| D, J_HS1, J_HS2 | the six clamps at the jack's pins (the generator's author placed them 2.25 mm from their pins), C44, C45, C49 and C50 with them | each clamp into the plane at its pad, its own via | the jack side of a conductor never beside its logic side (after D-F1: PTT_HSn_LEAD never beside PTT_HSn_n) | 2.25 mm as placed, and no more than 3 mm |
| E, J_DCIN | F1 at the header; D10 at F1's far pad; after E-F1 the input capacitor at U3 pin 6 and Q1's source, which is at D10 | D10, D1, C2 and the input capacitor into GND_V's own copper, which reaches the header's pin 2 without crossing L2 | nothing on GND and nothing behind L2 runs beside DC_IN, DC_F or DC_P | header to F1 to D10 in one run, D10 ahead of Q1 |
| E, J_SOLAR | F2 at the header, D4 at F2's far pad, the bulk capacitors behind it | D4 into the plane at its pad | nothing of the tracker's control beside PV_IN | the same |
| E, J_POD | D9 at the header; after E-F3 the two capacitors at pin 1; the bus passes D9's pads before any part of the bus inside | D9 pin 2 into the plane at its pad | the outside side of SDA1 and SCL1 never beside their inside side | the same 3 mm |

**Insulation distance for the 36 V and 54 V conductors.** Decision 34 rules ISO-001 against ECSS-Q-ST-70-12C Table
13-3 "per voltage band, per layer, on the column the board's own coating selects", and the standard's clause
13.8.2 b says the rating applies "to the worst-case peak transient voltage". The peak of the 36 V conductors
(board A's VIN_RAW; board E's DC_IN, DC_F, DC_P, HS_S, DC_HS and VIN_RAW) is their clamps' 64.5 V; board A's
+54V_POE carries no clamp on board A and reaches board B's. Both stand in the row 31 to 500 V, and up to 80 V
that row's floors govern every column. Boards A, D and E declare a conformal coat.

| where | the row's figure at 64.5 V | the distance to keep |
|---|---|---|
| outer layer under the coat | 2 um per volt and 160 um: 129 and 160 | 0.160 mm |
| outer layer where the coat cannot be: the lands of the headers, of the fuse holders and of the spring pins, the test points TP1, TP2, TP3 (board E) and TP13 (board A) | 5 um per volt and 500 um: 323 and 500 | 0.500 mm |
| inner layer, conductor to conductor | 1 um per volt and 150 um | 0.150 mm |
| inner layer, conductor to a hole wall, and to the board's edge (13.8.2 h) | 1 um per volt plus 50 um, and 200 um | 0.200 mm |
| hole wall to hole wall | 2 um per volt and 350 um | 0.350 mm |

The same row is handed on for the antenna conductors, whose arrestor turns on at 90 V: above 80 V the per-volt
figure of the uncoated column passes its floor, so at the connectors' lands the distance is 5 um per volt of
whatever the arrestor lets through, which is not known (section 9.3). The standard is written for space hardware;
that it governs is decision 34's ruling and not this review's.

## 8. The ratings ledger

Every figure quoted above, with its document as held under `v2/vendor/`, its revision and its page. A page is
the page of the PDF file.

| part | document, revision | page | what is quoted |
|---|---|---|---|
| SMCJ40A, SMCJ40CA, SMCJ28A, SMCJ18A | `power/littelfuse-smcj-series-tvs.pdf`, Littelfuse SMCJ series, "Revised: 11/20/15" | 1 | "Peak Pulse Power Dissipation ... by 10/1000us Waveform ... 1500 W"; "Peak Forward Surge Current, 8.3ms ... 200 A"; "IEC-61000-4-2 ESD 30kV(Air), 30kV (Contact)"; "Fast response time: typically less than 1.0ps from 0V to BV min" |
| | | 2 | SMCJ40A / SMCJ40CA: VR 40.0 V, VBR 44.40 to 49.10 V at 1 mA, VC 64.5 V at IPP 23.3 A. SMCJ28A: 28.0; 31.10 to 34.40; 45.4 V at 33.1 A. SMCJ18A: 18.0; 20.00 to 22.10; 29.2 V at 51.4 A |
| SMBJ18A, SMBJ6.0A | `power/littelfuse-smbj-series-tvs.pdf`, Littelfuse SMBJ series, "Revised: JC.07/04/25 v4" | 1 | "600 W peak pulse power"; "IEC-61000-4-2 ESD 30 kV(Air), 30 kV (Contact)" |
| | | 2 | SMBJ18A: VR 18.0 V, VBR 20.00 to 22.10 V at 1 mA, VC 29.2 V at 20.6 A. SMBJ6.0A: 6.0; 6.67 to 7.37 at 10 mA; 10.3 V at 58.3 A |
| SMBJ5.0A | `power/mdd-smbj-series-tvs.pdf`, MDD, "Rev:2025A7" | 2 | VRWM 5.0 V, VBR 6.40 to 7.00 V, VC 9.2 V at 65.3 A |
| PESD5V0S1BA | `nexperia/nexperia-pesd5v0s1ba.pdf`, product data sheet, 26 April 2024 | 3 | Table 5: PPPM 130 W, IPPM 12 A (8/20 us); VESD "IEC 61000-4-2 (contact discharge)" 30 kV; "HBM MIL-Std 883" 10 kV |
| | | 4 | Table 6: VRWM 5 V; VBR 5.5 to 9.5 V at 1 mA; IRM 5 nA typical, 100 nA maximum at 5 V; Cd 35 pF typical, 45 pF maximum; VCL 10 V at 1 A, 14 V at 12 A |
| | | 5, 6 | Fig. 7: "IEC 61000-4-2 network CZ = 150 pF; RZ = 330" ohm. Section 10, the eight layout clauses |
| PESD12VL1BA | `nexperia/nexperia-pesd12vl1ba.pdf`, product data sheet, 14 April 2023 | 3, 4 | Table 5: PPPM 200 W, IPPM 5 A; contact 30 kV, air 15 kV, HBM 10 kV. Table 6: VRWM 12 V; VBR 14.2, 15.9, 16.7 V at 5 mA; Cd 19 pF; VCL 20 V at 1 A, 37 V at 5 A |
| USBLC6-2SC6 | `st/st-usblc6-2-esd-protection.pdf`, DS4260 Rev 7, December 2021 | 1 | "IEC 61000-4-2 level 4: 15 kV (air discharge), 8 kV (contact discharge)"; "Compliant with USB 2.0 requirements" |
| | | 2 | Table 1: air 15, contact 15 kV. Table 2: IRM at VRM 5.25 V; VBR 6 V minimum "between VBUS and GND"; VF 1.1 V at 10 mA; VCL 12 V at 1 A and 17 V at 5 A, 8/20 us, "Any I/O pin to GND"; Ci/o-GND 2.5 typical, 3.5 pF maximum |
| | | 5, 6 | Figure 5, the clamping levels of the rail-to-rail structure; 2.3 "How to ensure good ESD protection" |
| TPD2E2U06-Q1 | `ti/ti-tpd2e2u06-q1.pdf`, SLLSEJ9E, revised October 2022 | 4 | 6.1: IPP 5.5 A, PPP 75 W (8/20 us). 6.3: contact +-25000 V, air-gap +-30000 V. 6.5: input pin voltage 0 to 5.5 V |
| | | 5 | 6.7: VRWM 5.5 V; VCLAMP 9.7 V at 1 A, 12.4 V at 5 A (TLP, typical); RDYN 0.6 ohm; CL 1.5 typical, 1.9 pF maximum; VBR 6.5 to 8.5 V |
| TPS25740A | `ti/ti-tps25740.pdf`, SLVSDG8B, revised June 2017 | 6 | 7.1: CC1, CC2 -0.3 to 6 V; VBUS, VPWR, ISNS, DSCG -0.5 to 30 V sustained and -1.5 to 30 V for 1 ms. 7.2: HBM +-2500; IEC 61000-4-2 contact, CC1, CC2 +-8000; air-gap +-15000; note 4 |
| | | 7, 36 | C(RX) 200, 560, 600 pF. 9.1.1 System-Level ESD Protection |
| TPS259631 | `power/tps2596.pdf`, TPS2596 SLVSET8A, revised August 2019 | 5 | 7.1: IN -0.3 to 21 V; OUT -0.3 to "min (21, VIN + 0.3)" |
| LTC2954 | `power/ltc2954.pdf`, 2954fb | 1, 2, 3 | "+-10kV ESD HBM on PB Input"; "PB ... -6V to 33V"; IPB -1, -6, -12 uA at 1 V and -3, -9, -15 uA at 0.6 V; VPB(VTH) 0.6, 0.8, 1 V falling; VPB(VOC) 1, 1.6, 2 V at -1 uA |
| | | 12, 13 | the network for a button far from the pin; "PB Pin in a Noisy Environment" |
| LM5176 | `ti/lm5176-datasheet.pdf`, SNVSAI1D, revised August 2021 | 5, 17 | 6.1: "VIN, EN/UVLO, VISNS, VOSNS, ISNS(+), ISNS(-) -0.3 60 V". 6.2: HBM +-2000. 7.3.7: "a 2-kohm resistor in series with the VISNS pin is required" above 40 V |
| TPS37A010122 | `ti/ti-tps37-snvsbj1e.pdf`, TPS37 SNVSBJ1E, revised August 2023 (filed by this stream) | 6 | 7.1: VDD, VSENSE, VRESET -0.3 to 70 V |
| CSD19532Q5B | `power/ti-csd19532q5b-n-fet.pdf`, SLPS414B, revised May 2017 | 1 | VDS 100 V, VGS +-20 V, "Avalanche Rated" |
| CSD18510Q5B | `battery/ti-csd18510q5b.pdf`, SLPS632, March 2017 | 1 | VDS 40 V, VGS +-20 V |
| BAT46W | `diodes/diodes-bat46w.pdf`, DS30044 Rev. 20 - 2 | 2 | VRRM 100 V; IF 150 mA; VF 0.45 V maximum at 10 mA |
| TPA6132A2 | `ti/ti-tpa6132a2.pdf`, SLOS597B, revised July 2017 | 1, 4 | "+-8 kV HBM ESD Protected Outputs"; 6.1 HPVDD -0.3 to 1.9 V; 6.2 HBM OUTL, OUTR +-8000, all other pins +-2000; 6.3 "Voltage applied to Output; OUTR, OUTL (when EN = 0 V) -0.3 3.6 V" |
| 74LVC1G08GV | `techpublic/techpublic-74lvc1g08gv-c19829591.pdf`, TECH PUBLIC, no revision printed; six pages of images, read from a render at 110 dpi | 2 | Input Voltage -0.5 to 6.5 V; Input Clamp Current -50 mA (VIN<0); note 2 |
| 2N7002 | `power/jscj-2n7002-c8545.pdf`, JSCJ, "J,Sep,2016" | 1 | VDS 60 V, VGS +-20 V |
| TLV9062 | `ti/ti-tlv9062-op-amp.pdf`, SBOS839N, revised July 2026 | 10 | signal input pins, common mode (V-) - 0.5 to (V+) + 0.5 V; HBM |
| TUSB2046I | `ti/ti-tusb2046b.pdf`, SLLS413L, revised June 2017 | 6, 17, 18 | 7.1: VI, VO -0.5 to VCC + 0.5 V. 7.2: HBM +-4000. The downstream port's capacitor and bead; 11.1.1 item 2 |
| GTH-SFF-AL | `polyphaser/polyphaser-gth-sff-al-sma-surge-protector.pdf`, PolyPhaser, copyright 2026 | 1 | DC to 6 GHz; "Operating Voltage (DC) 60 Volts" maximum; "Input Power, CW 150 Watts"; "Surge Current 10 kA"; "Turn On Voltage 90 Volts" typical |
| G6K-2F-Y | `omron/omron-g6k-signal-relay.pdf` | 1, 3 | "-Y models offer an impulse withstand voltage of 2,500 V for 2 x 10 us"; "Max. switching voltage 125 VAC, 60 VDC" |
| SA868 | `nicerf/nicerf-sa868-datasheet-v1.3.pdf` | 9 | pin 12 "ANT connect 50 ohm antenna"; no rating of the pin and no discharge figure anywhere in the sheet |
| RA30H1317M1 | `mitsubishi/ra30h1317m1-datasheet.pdf` | 2 | VDD 17 V, VGG 6 V, Pin 100 mW; "Load VSWR Tolerance ... No degradation or destroy", "Load VSWR=20:1"; no discharge figure |
| LM74700-Q1 | `ti/ti-lm74700-q1.pdf`, SNOSD17G, revised December 2020 | 5 | 6.1: ANODE to GND -65 to 65 V; CATHODE to ANODE -5 to 75 V. 6.2: HBM +-2000 |
| | | 17, 18, 19 | 10.1.1.2.3, the minimum capacitances; 10.1.1.3 and 10.1.1.4, the choice of the clamps |
| BSC039N06NS | `infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf`, Final Data Sheet Rev.2.4, 2020-02-03 (filed by this stream; it has a text layer) | 1, 3 | VDS 60 V; "100% avalanche tested"; EAS 50 mJ at ID 50 A; VGS -20 to 20 V. No discharge figure |
| LM5069 | `ti/ti-lm5069.pdf`, SNVS452G, revised January 2020 | 4 | VIN, SENSE, OUT, UVLO to GND -0.3 to 100 V; OVLO 7 V; HBM +-2000 |
| LT8705A | `power/lt8705a.pdf`, 8705af | 2 | VIN, EXTVCC -0.3 to 80 V; CSNIN, CSPIN, CSPOUT, CSNOUT -0.3 to 80 V; FBIN, SHDN -0.3 to 30 V |
| MINI blade fuse | `keystone/littelfuse-297-ficcorp.pdf`, Littelfuse 297 series, a distributor's copy | 1 | "Voltage Rating: 32 VDC"; "Interrupting Rating: 1000A @ 32 VDC" |
| the fuse holder | `keystone/M65p42.pdf`, Keystone catalogue page | 1 | Cat. No. 3568, "For Littelfuse Mini 297 or 997 series/Bussmann ATM series or equivalent" |
| TLV75533 | `power/ti-tlv755p-ldo.pdf`, SBVS320D, revised September 2024 | 1, 15 | "Output accuracy: 1% (maximum at 85 C)"; "requires an output capacitance of 0.47uF or larger"; "a maximum output capacitance value of 200uF" |
| RP2040 | `rp2040/rpi-rp2040-datasheet.pdf` | 615 | 5.5.3.1: IOVDD -0.5 to 3.63 V; voltage at IO -0.5 to IOVDD + 0.5 V. 5.5.3.2: HBM 2 kV |
| BME688 | `bosch/bosch-bme688.pdf`, BST-BME688-DS000-03, revision 1.3 | 15 | Table 11: supply pins -0.3 to 4.25 V; interface pins -0.3 to VDDIO + 0.3 V; HBM +-2 kV |
| BMI270 | `bosch/bosch-bmi270.pdf`, BST-BMI270-DS000-08, revision 1.6 | 16 | supply pin -0.3 to 4 V; logic pins -0.3 to VDDIO + 0.3 V and under 4 V; HBM 2 kV |
| SGP41 | `sensirion/sgp41-datasheet.pdf`, version 1.0, December 2021 | 7 | Table 5: supply voltage VDD and VDDH -0.3 to +3.6 V; ESD HBM 2 kV |
| the insulation table | `standards/ecss-q-st-70-12c-2014-07-14.md`, the project's transcription of ECSS-Q-ST-70-12C | | 13.8.2 a, b, d, h; Table 13-3, the three voltage rows |

**Ratings that stand on a value text and on no document held:** Q3 (BSC028N06NS, "60 V") on board E; the
voltage of C41, C42, C49 and C50 on board D, which no text states.

## 9. What this review could not judge, and what it hands on

### 9.1 Not judged, plainly

1. **Seventeen conductors**, by the verdicts above: every antenna conductor, the speaker conductors, the pod's
   two bus lines.
2. **Any layout.** No board of the declared phases carries these circuits in copper. Section 7 is a list of what
   the layout must keep, and nothing here says that any layout keeps it.
3. **Surge.** No level is ruled. Where a clamp's own rated pulse carries a part behind it outside its rating
   (A-N1, E-N2), the review says so and hands the coordination to R-PWR.
4. **The discharge path to the enclosure.** Rule TRN-001's acceptance asks for it and no board draws a chassis
   net. Every "return" above ends on a ground plane or on GND_V. What joins those to the plates and the stud is
   rule GND-002's, which is open.
5. **The parts that are not picked:** the receptacle on the connector plate, the M8 receptacle, the pod, the
   headset jack's pin assignment (IF-HS: "TBD: the jack's drawing").
6. **Boards B, C, E5 and P**, except the one conductor of board C that is board A's.
7. **Direct voltage bias on the capacitors that carry the bounds.** No bias curve is held for any of them. The
   bounds are stated at the nominal value and at a named fraction of it.
8. **The fuses against their tracks.** That is rule PWR-003's. At `fnd/retake6` `50e3b60b` its reading is PASS of
   3 stages on board E and PASS of 4 on board A, and those stages are the stored-energy chain's, which the shore
   fuse is not part of.
9. **No generator was run.** This host has no KiCad. The four circuit apply scripts were tested as edits, on
   copies, and no netlist of any proposed change exists.

### 9.2 What is handed on, as scripts under `v2/docs/records/d8dec31/`

| script | what it changes | whose file | tested |
|---|---|---|---|
| `apply_port_declarations.py` | the three board tables: board A's external list corrected, `internal_ports` on all three | the integrator's | on a scratch copy of the tree; second run refused; TRN-001 then read on the copy (section 10) |
| `apply_gen_sch_e_cin.py` | E-F1: 1 uF 100 V from DC_F to GND_V, declared at U3's ANODE | board E's generator | on a copy; syntax tree read back; second run refused; together with the next in either order |
| `apply_gen_sch_e_pod.py` | E-F3: two 10 uF 25 V at J_POD pin 1 | board E's generator | the same |
| `apply_gen_sch_a_mainpb.py` | A-F2: 5.1 k and 100 nF at U1's PB pin, the two nodes, the signal class | board A's generator and table | the same |
| `apply_gen_sch_d_ptt.py` | D-F1: per push-to-talk line 1 k and two BAT46W | board D's generator | the same |
| `apply_registry_d31.py` | the fourteen open items of this review at the next free numbers, each linked from the record(s) whose verdict it can move (so `rules_lib.py requirements` passes); its second stage `--close-s88 <commit>` closes S-88 and refuses until the re-taken reading of TRN-001 on board A is in the tree (PASS, the declared phase's netlist, the changed tool, 0 disagreements) | the integrator's | on a copy of main's registry: 0 errors after stage 1; every refusal of stage 2 exercised, then the closure, 0 errors |
| `apply_holds_review_pin.py` | the sha256 of this file and the three netlists it read, into the three holds | the integrator's | on a copy |
| `make_port_reviews.py` | writes `v2/ecad/tools/pcb_port_reviews.json`, the reviewed set (section 10); the file is committed on this branch and the script's `--check` confirms it is what the corrected declarations give | this stream's (a new file) | on a copy: "exactly what this script would write" after `apply_port_declarations.py` |
| `apply_config_inputs_port_reviews.py` | declares `tools/pcb_port_reviews.json` a configuration input of `port_protect.py` in `rules_status.CONFIG_INPUTS`, so a change to the reviewed set makes TRN-001's readings stale | the integrator's | on a copy; the patched module imported and its entry read back |
| `apply_interfaces_mainsw.py` | IF-AC-MAINSW's board A end after A-F2: pin 1 on MAIN_PB_LEAD; refuses while board A's netlist still has J_MAINSW.1 on MAIN_PB (run it after the generator) | the integrator's | on a copy: refused on today's netlist; the change checked with `--force-netlist --check` |
| `apply_sources_d31.py` | the `SOURCES.yaml` entries of the two sheets this stream filed (Infineon BSC039N06NS, TI TPS37) | the integrator's | on a copy; second run refused |
| `regress_reclassify.py` | the three shapes of moving an entry on the three REAL corrected tables, in a scratch tree (`readings/regress-reclassify.txt`) | a scratch driver | 21 cases, 0 failed |

**Any of the four circuit changes moves its board's netlist, and the hold's pin names a netlist.** After the
circuit round the pinned review reads "re-review it" by the rule's own text, and this review is owed again on
the new netlists, which is as it should be.

### 9.3 Questions prepared, not sent

Nothing here was sent to anybody. Outside contact is the owner's.

**To PolyPhaser, about the GTH-SFF-AL** (expertise: the maker's applications engineer):
"1. For an IEC 61000-4-2 contact discharge of 8 kV applied to the centre conductor of the unprotected port, what
peak voltage and what energy appear at the protected port into 50 ohm? 2. What is the impulse spark-over voltage
at 1 kV per microsecond, and which waveform is the 10 kA rated for? 3. At 144 to 146 MHz, at what peak
radio-frequency voltage does the tube conduct, and does the 150 W continuous rating hold into a load of 3:1?"
Evidence to send with it: the part number and the four figures of its sheet. Options if no answer comes: test M7
with the radio replaced by a 50 ohm load and a probe; an arrestor with a stated let-through for the ports that
carry no direct current.

**To ST, about the USBLC6-2SC6** (for finding X-C1): "With pin 5 at 0 V, what voltage does an I/O pin hold when
1 to 15 uA is driven into it, from -20 to +60 C?"

**To the qualified power review, R-PWR:** notes A-N1 and E-N2, finding E-F2, and the coordination of board E's
hot swap with the four SMCJ40 parts between the receptacle and board A's front end.

**Equipment for what the desk cannot decide:** an IEC 61000-4-2 generator and a test house, which is test M7 of
`v2/docs/TEST-PLAN.md`; a curve tracer or a source meter for X-C1.

## 10. The instrument

**The defect class.** A declared port on a ground pin was judged PASS while the supply's own pin was in no
entry. Two things made it possible: `port_protect.py` skipped a ground pin without asking whether the entry had
any pin left, and nothing asked whether a connector was in any entry at all.

**The change** (`v2/ecad/tools/port_protect.py`, commit `d3125b1e` on this branch).
1. An entry that names no conductor is refused, and the rule reads FAIL: a listed pin the connector does not
   have; a listed pin on a ground or a no-connect; an entry none of whose pins carries a supply or a signal; an
   internal entry with no reason; a pin declared both ways.
2. A new list, `internal_ports`, of {ref, pins, why}, says where a lead that stays inside the case goes. Every
   pin of every connector (a reference J, P, PAD or W) that carries a supply or a signal is in one list or the
   other; a pin in neither is printed `UNCOVERED` and the rule reads INCONCLUSIVE while one stands. A connector is
   read by its reference and never by its library, because these generators draw several integrated circuits and
   a choke with connector symbols.
3. The ground pins of the declared ports are printed by name, which the tool's own description had promised.
4. A board that declares a zero of external ports with its reason is read as before (board P), unless a review holds
   pins of it external (below).
5. **The reviewed set** (second commit of this branch after the fresh check, item B1, for open item S-88's condition
   "moving or omitting a declared entry demands reconciliation and never shrinks the coverage in silence"). Items 1
   and 2 catch an entry moved onto ground pins (FAIL) and an entry removed (INCONCLUSIVE); they did not catch an entry
   moved from `external_ports` into `internal_ports` with a twenty-character reason: on the corrected `a.json`,
   J_USBW moved that way read PASS of 38 instead of 42, in silence. Now `v2/ecad/tools/pcb_port_reviews.json`
   holds, for each board, the external pins this review enumerated from the netlist, pin by pin with the net each
   carried (22 on board A, 8 on D, 5 on E: the 35 pins of section 2), the review it rests on and the netlist's
   sha256/16. `port_protect.py` holds the declaration's external pins against that set and reads INCONCLUSIVE by name
   for a reviewed pin declared internal (RECLASSIFIED), covered by no entry (REVIEWED, beside UNCOVERED), gone from
   the netlist or moved to ground (the J_DOCK shape, for an entry that lists no pins), and for a declared external
   pin no review holds (NOT REVIEWED), until the set is changed with its reason and the review it rests on (a
   `changes` entry of forty characters or more naming a review in the tree); a board that declares external ports
   and has no reviewed set reads INCONCLUSIVE, and a declared zero while a review holds pins is not a PASS. **Why a
   separate file and not a key in the board table:** the tables are written by many hands and a reclassification made
   in one would carry its own approval in the same hunk; the reviewed set has one purpose and one writer, and its
   change is visible as a change to that file alone. It is a configuration input of the tool
   (`apply_config_inputs_port_reviews.py`) and every reading records it by sha. Thirteen fixture tests
   (`tests/test_port_protect.py`, the reviewed-set block) and `regress_reclassify.py` on the three real corrected
   tables (21 cases, 0 failed) cover the three shapes; the reclassification of J_USBW now reads INCONCLUSIVE of 38
   with the three pins named, and reads PASS of 38 only once the reviewed set carries the change with its reason.

**The test** (`v2/ecad/tools/tests/test_port_protect.py`, seven tests added, then thirteen for the reviewed set). On
the tool as it stood at `73ae2f21`: 40 passed, 7 failed, the seven new ones, and the first of them with the tool's own
words, "verdict: port_protect PASS of 2", for a port declared on two ground pins. On the changed tool: 48 passed, 0
failed (the 47 of this file and one of `test_artefact_recording.py` whose name matches); with the reviewed set, 61
passed, 0 failed. Five neighbouring test files that
import or name the tool: 77 passed, 0 failed, 2 skipped for want of KiCad on this host. The full suite was not
run here; it runs on the KiCad host. Readings: `readings/test-port-protect-before.txt` and `-after.txt`.

**TRN-001 on the three boards, read in a scratch copy of the tree and written to a scratch directory**
(`VERDICT_DIR`; nothing was written into the tree's evidence). Readings: `readings/trn001-scratch/`.

| board | the committed declaration, the changed tool | the corrected declaration, the changed tool |
|---|---|---|
| A | **FAIL** of 26: 2 entries refused (J_DOCK.1 and J_DOCK.2 on GND), 76 connector pins in no entry | **PASS** of 42: 18 ports, 0 unprotected, 0 behind an active part, 0 refused, 0 uncovered, 60 pins internal, 15 ground pins named, 5 clamps and 0 reversed |
| D | INCONCLUSIVE of 21: 18 connector pins in no entry | **PASS** of 21: 4 ports, 0 unprotected, 0 uncovered, 18 pins internal, 7 clamps and 0 reversed |
| E | INCONCLUSIVE of 13: 27 connector pins in no entry | **PASS** of 13: 3 ports, 0 unprotected, 0 uncovered, 27 pins internal, 5 clamps and 0 reversed |
| B, C, P | B INCONCLUSIVE of 17 (290 pins in no entry); C INCONCLUSIVE of 4 (39); P PASS of 3, a declared zero | not written: those tables are not this review's |

**What a PASS of this rule says, and what it does not.** It says that every declared conductor meets a protection
part before a semiconductor, that every clamp points the right way, and now that every connector pin is in a
list, and that the external pins are exactly the ones a review enumerated. It does not compare a clamp's voltage with
the rating of what stands behind it, and it believes an `off_board` entry on its text (T-3): **TRN-001's PASS of 42 on
board A believes 12 of its 18 entries on that text**, the eleven antenna conductors (J_BM1 to J_BM11), which this
review could not judge at the desk, and J_MAINSW, whose clamp this review read on board C's netlist; the tool judged
6 entries on 10 pins itself. Board A reads PASS with finding A-F2 open, board D with D-F1 open and board
E with E-F1, E-F2 and E-F3 open. **That is why this rule's PASS and this record are two requirements of the hold
and not one.**
