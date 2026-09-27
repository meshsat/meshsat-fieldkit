# MeshSat field kit V2: engineering questions for the blocked items

Written 27 September 2026 (MESHSAT-1357) from the layer-by-layer audit of the repository at commit `e3aedb25`. Paths
are repository paths; file:line citations are lines at `e3aedb25` (including the few that cite a Markdown page by
line), which the public repository serves at `https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/e3aedb25/<path>`.
**Handover H1 adds EQ-15 to EQ-21**, the questions circuit round 8 (main `84e52461`) and the handover closers raised;
their citations are at the H1 source commit named in the snapshot's `SOURCE.txt` (`8a19fe29` for H1; H1.1 changes no
design file those questions cite). **After H1.1 (set 4, branch `fnd/r8int4`, 27 September 2026)** EQ-22 to EQ-24 are added, EQ-05 carries the hot stop's firing inside the envelope and EQ-20 its merge; their citations are at that branch's commits. **Set 5 (branch `fnd/r8int5`, 27 September 2026)** answers EQ-16 (board E's and board A's dock halves), EQ-17 (board A), EQ-18 (the tool) and EQ-19 (boards A, B, D and E) in their attempts rows and adds EQ-25, the fail-safe level EQ-18's re-take found on TX_INHIBIT_n; their citations are at that branch's commits. Internal names are defined in `v2/docs/handover/GLOSSARY.md`. Every blocked question the audit found in the nine
pre-PCB layers is here once, deduplicated across layers, in the form the owner asked for
(`v2/docs/reviews/2026-09-27-handover-execution-prompt.md` section 6): the exact issue, what it affects, the evidence,
what was tried, the viable options, the recommended next action, the expertise or equipment needed, and cost and lead
time where known.

**Prototype framing.** Nothing of the V2 kit has been built, ordered, powered or measured. Prices and stock figures
marked VERIFIED were read from public pages at the times recorded in `v2/docs/reviews/READY-TO-ACT.md` section 10;
they are dated readings, not quotes. Nobody has been contacted and nothing has been bought.

**Recommendations are the session's, not the owner's.** Where an option is a desk engineering choice, the closer who
takes it records it in `v2/ecad/tools/pcb_requirements.yaml` `session_choices` (SC-nn: question, taken, why, "Reverse
by ...") under the owner's standing rule of 26 September 2026. Money, outside contact, publication and promotion stay
with the owner; `v2/docs/reviews/READY-TO-ACT.md` section 0 lists the authorisations still missing, and its section 9
holds the prepared request texts (not sent).

## Index

| Id | Question | Group | Layers | Boards | What it holds today |
|---|---|---|---|---|---|
| EQ-01 | Can board B route at all, on which stack and escape method, inside its outline? | A. design work | 4, 5, 7, 8, 9 | B (case layout) | B's layout entry (FEA-003); B's outline and connector places |
| EQ-02 | Does the RockBLOCK 9704 stop transmitting within 1 s under EMCON? | A. design work | 4, 8 | B | FEA-002's RockBLOCK row |
| EQ-03 | How may the kit travel with its 145 Wh built-for-the-kit pack? | A. design work | 2, 3 | none | a transport claim only |
| EQ-04 | Does a CM5 radio keep its certification through a blind-mate and a bulkhead? | A. design work | 3 | B, case | nothing if the recommended route is taken |
| EQ-05 | What is the sealed case's thermal conductance, and is the hot end feasible (the hot stop's firing inside the envelope included)? | B. physical evidence | 2, 3, 4, 7, 9 | A, B, D, P | freezing hot-part placement and the pack location; the +35 and +25 C figures; REQ-052 and REQ-024 at +40 C wherever the hot stop fires |
| EQ-06 | Can the fitted ATECC608B's keys be destroyed after lock, safely under power loss? | B. physical evidence | 4, 6, 8 | B | B's layout entry for the U8 site |
| EQ-07 | Does the chemical fuse F2 hold 18 A for 60 s from a +55 C block? | B. physical evidence | 4, 9 | P (A) | P's fabrication release; P's F2 part identity |
| EQ-08 | Do the case margins that rest on unpublished tolerances hold? | B. physical evidence | 7 | A, B, C, E, P | final outlines and connector places |
| EQ-09 | Does the CM5's PHY accept a capacitively coupled link? | B. physical evidence | 8, 9 | B | nothing before layout if a magnetics footprint is provided; INT-003 at prototype |
| EQ-10 | Qualified battery review R-BAT and the protection coordination | C. external authorisation | 4, 8 | P (A) | P's fabrication release and the pack build; the battery part of layer 4 |
| EQ-11 | Qualified power review R-PWR | C. external authorisation | 6, 8, 9 | A (E, B) | A's layout commitment (as the records time it); layer 8 COMPLETE for A |
| EQ-12 | Qualified high-speed review R-HSD | C. external authorisation | 5, 8, 9 | B | B's layout commitment; layer 8 COMPLETE for B |
| EQ-13 | The M1 mission duration (L-02), reserved to the owner | C. external authorisation | 2, 3 | none once REQ-016 is split | nothing, once REQ-016 is split |
| EQ-14 | Fabricator prices per board at each layer count and copper weight | C. external authorisation | 9 | all | the cost half of every stackup decision (STK-002) |
| EQ-15 | Board P's discharge current through Q1's body diode with CHGIN = 1 (BAT-F20) | A. design work | 2, 4, 8 | P | S-46; the pack ladder, mode table, F2 analysis and the E3-A, E4-O and P12 pass lines |
| EQ-16 | The dock's VIN_RAW contacts at 3.53 A each against a 3.5 A rating (R8E-N01) | A. design work | 5, 8 | A, E, E5 | the A to E interface's power capacity |
| EQ-17 | Board A's +3V3 overvoltage window between the SN74AUP1G08's 4.6 V maximum and D3's 6.4 V clamp | A. design work | 4, 8 | A | the EMCON gating on A's PA and HF rails |
| EQ-18 | RF-002 cannot decide TX_INHIBIT_n through board C's U14 (SN74LVC1G57) | A. design work | 4, 8, 9 | C (A, B, D) | RF-002 on every board whose transmitter rides TX_INHIBIT_n |
| EQ-19 | PWR-001's undeclared supplies on boards A, B, D and E | A. design work | 8, 9 | A, B, D, E (C, P) | PWR-001 on four boards on current evidence; their layout entry |
| EQ-20 | Board B's round 8 circuit (merged at `b76c18cb` after H1.1), with a sub-13 ns enable pulse window left | A. design work | 4, 8 | B | the residual's judgement (R-HSD); FEA-003's fabric half |
| EQ-21 | The generators write no MPN; 1497 of 2205 BOM rows carry no order code | A. design work | 6, 8 | all six | layer 6's exact identity per BOM line |
| EQ-22 | The hot stop's signal path HOT-R1 is in neither board A's nor board E's generator | A. design work | 2, 3, 5, 8 | A, E | REQ-077 (FAIL until drawn); the layout entry of A and E |
| EQ-23 | Does a non-destructive, firmware-free hardware stage stand behind the hot stop (S-58)? | C. external authorisation | 2, 3, 4, 8 | A, E, P | the layout entry of A, E and P; REQ-044, REQ-046, REQ-077 |
| EQ-24 | The QMX lid tray does not fit the unit's connector layout (jacks on both end panels) | A. design work | 7 | none (a made part) | printing the tray (S-63) |
| EQ-25 | TX_INHIBIT_n's fail-safe level with board C unpowered, 1.09 V against a 0.8 V VIL (W3T-F1) | A. design work | 4, 8, 9 | C (A, B, D) | RF-002 on boards A to D and board D's SA868 keying (S-64) |

Group A items can be answered under existing authority; group B needs hardware and so a purchase; group C needs the
owner's money, outside contact or a value only he can set.

---

## A. Design work

### EQ-01. Board B's routability, stackup, escape method and outline

| | |
|---|---|
| **Exact issue** | Board B (three Compute Module 5 on 0.4 mm receptacles, three PCIe switches, three USB 3 hubs, the failover muxes, HDMI switching and three voting supervisors on a 330 x 200 mm outline) has never routed. Its feasibility on any stackup is not shown, and its stackup (six or eight layers), escape method and whether the outline holds are undecided. |
| **Affected** | FEA-003 (FB-FAB-6, FB-FAB-7); decision 43; B's stack, outline, connector places and possible partitioning; NEED-03; R-HSD (EQ-12); the case layout; layers 4, 5, 7, 8, 9 for board B. |
| **Evidence** | `v2/docs/B-FEASIBILITY.md` sections 1, 3.1, 3.2, 7.8, 7.9; `v2/docs/feasibility/FAILOVER-FABRIC.md` sections 7 and 8.3; `v2/docs/CURRENT-EVIDENCE.md` (B21: 416 open). On six layers as used, inner pairs solve to 140.5 ohm against 100 (B-FEASIBILITY 3.2). |
| **Attempts and results** | B21 routed about 40 h and stopped at 416 open; B22 and B23 tried further levers (RECORDED in `v2/ecad/tools/boards/b.json`); the placement predictor read about ten escape collisions of 75 fine-pitch parts under every lever. Q-B-ESC-1 (26 September, EXPERIMENTAL, on the uncorrected B21): the six-layer arm was cut at 33 open while still falling; the eight-layer-signal arm plateaued at 16 to 18, with the in-region residue at the bare north-row pads of the switch U301 and hub U302, a band bounded by placement (INFERRED). Result INCONCLUSIVE. |
| **Viable options** | A1 eight layers (decision 43's measurement); A2 six layers re-assigned (In3 as GND); A3 via-in-pad, only where the fabricator's process covers the pad; A4 a floor-plan change; A6 a larger outline within the 1450 window; A7 pin swaps. A8, feature cuts, is excluded by D-01. |
| **Recommended next action** | After round 8's board B netlist merges: run the `impedance_2d` solves for A2 and JLC08161H-2116 at desk; run Q-B-ESC-2 as specified (B-FEASIBILITY 7.9, cap 5 USD); then decision 43's whole-board eight-layer run with a cap recorded before it starts, EXPERIMENTAL; derive the channel budgets from primary documents; put the resulting candidate to R-HSD. Choose between A2, A1, A3 and A4 by the residue's causes, and record the choice as a session decision with its measurement and cost (P0 rule). |
| **Expertise or equipment** | A KiCad 9.0.9 host with the Freerouting 1.9.0 per-pass build; a high-speed digital reviewer (EQ-12); a 2D field solver (`v2/ecad/tools/impedance_2d.py`); the fabricator's via-in-pad and impedance answers. |
| **Cost and lead time** | Box runs of at most 5 USD each within existing authority (about 3 box-hours per run, about 0.43 USD at the recorded rate). R-HSD and the eight-layer fabrication price TBD by quote (L-05, L-01). When read on 21 September, JLCPCB published controlled-impedance stacks for four and six layers only (`boards/b.json`), so an eight-layer result needs the fabricator's stack answer before impedance can be judged. |

### EQ-02. The RockBLOCK 9704 under EMCON

| | |
|---|---|
| **Exact issue** | After its supply eFuse opens, the RockBLOCK 9704 keeps running on its two 10 F supercapacitors (about 16 J), and its ENABLE is held only by firmware on expander U6. No held document says what the 9704 does when ENABLE falls, so REQ-071's 1 s latency cannot be shown for this transmitter. |
| **Affected** | FEA-002 row 4 (`v2/docs/feasibility/EMCON.md` section 4.4); board B's RockBLOCK control path; REQ-030, REQ-071; D-05. |
| **Evidence** | EMCON.md sections 0a and 4.4; `v2/vendor/rockblock/rb9704-sch-2B1.pdf` pages 2 to 5. |
| **Attempts and results** | The sixth revision of EMCON.md reopened the row; no maker statement is held. |
| **Viable options** | (a) Force ENABLE low with the EMCON hardware line, and obtain Ground Control's or Iridium's statement of the module's response. (b) Bench-test ENABLE on a 9704. (c) A module-independent remedy: an EMCON-gated discharge of the supercapacitors, or an RF path gate (its L-band insertion loss budgeted). |
| **Recommended next action** | Draw (a) in round 8 now. If no maker statement arrives before board B's layout entry, add (c)'s supercapacitor discharge. Keep (b) as a prototype verification row. Record the choice as a session choice. |
| **Expertise or equipment** | For (b), an RF and embedded bench with an external receiver. |
| **Cost and lead time** | The circuit parts are minor. The maker's lead time is unknown; outside contact is the owner's (the question is among those prepared, READY-TO-ACT section 9). |

### EQ-03. Transport classification of the pack

| | |
|---|---|
| **Exact issue** | Road, air or parcel carriage of the kit with its 145 Wh 4S3P pack, built for the kit and without a UN 38.3 test summary, has no established classification (REQ-069). It blocks only a transport claim; REQ-069's statement ("no route claimed until established") is settled. |
| **Affected** | REQ-069; the CONOPS Transport row, mission M2 and section 7a; operating instructions; no board. |
| **Evidence** | `pcb_requirements.yaml` line 2831; SC-06, withdrawn on 26 September after the owner's review (`v2/docs/reviews/2026-09-26-foundation-progress-review.md` section 5 and reference R5); the pack is 144.7 Wh at the cells' minimum capacity (V2-SPEC, battery row). |
| **Attempts and results** | SC-06 (road carriage as the operator's own equipment) was taken and withdrawn the same day: an unknown UN 38.3 status does not leave road carriage open, because road carriage has its own dangerous-goods rules. |
| **Viable options** | (a) A desk classification from the ADR text: UN 3480 or 3481, class 9, special provision 188 not applicable above 100 Wh, and the prototype and low-production provisions with their packing instruction. (b) UN 38.3 tests on the built pack design. (c) A dangerous-goods safety adviser's written opinion. |
| **Recommended next action** | (a) now, filing the ADR clauses under `v2/vendor/` with `SOURCES.yaml` entries; (c) only if (a) leaves the route open; no carriage claimed meanwhile. |
| **Expertise or equipment** | A dangerous-goods safety adviser (ADR) if needed; a UN 38.3 laboratory only for (b). |
| **Cost and lead time** | Desk: hours. An adviser's opinion: short and paid, cost not known in the tree. UN 38.3: a laboratory quote, weeks, and built packs. |

### EQ-04. CM5 radio certification through a blind-mate and a bulkhead

| | |
|---|---|
| **Exact issue** | Whether a Compute Module 5's radio keeps its certification when Raspberry Pi's approved antenna is reached through a blind-mate joint and a wall bulkhead (CON-011); the datasheet does not say. Which slot feeds the WIFI 2.4 jack, and what the other two modules use, is also open (S-16). |
| **Affected** | CON-011, S-16, NEED-16; board B's J_BM3 blind-mate path; the case's WIFI 2.4 jack; the EMCON rows of the three CM5 radios. |
| **Evidence** | `pcb_requirements.yaml` line 5807 (notes: "whether the intermediate path voids the certification is an inference; the datasheet does not say"); `v2/vendor/cm5/cm5-datasheet.pdf`. |
| **Attempts and results** | Datasheet read; no maker statement held. |
| **Viable options** | (a) The certified antenna kit fixed inside the plastic case wall, with no bulkhead in the RF path and one jack fewer. (b) Keep the bulkhead and ask Raspberry Pi (outside contact, text prepared by the session, sent by the owner). (c) Disable the CM5 radios and let the AW7915-AED cards carry local WiFi. |
| **Recommended next action** | (a), recorded as a session choice with the slot assignment for the other two modules. It changes CASE-MARGINS C2's jack list and board B's J_BM3 path, so it is taken before those are regenerated. |
| **Expertise or equipment** | None for (a); Raspberry Pi's compliance contact for (b). |
| **Cost and lead time** | (a): none beyond the antenna kit already in the device set. (b): unknown lead time. |

---

### EQ-15. Board P's discharge current through Q1's body diode (BAT-F20)

| | |
|---|---|
| **Exact issue** | With the BQ4050's FET Options bit CHGIN = 1, the charge inhibit above T3 and the T1 range below it hold board P's charge FET Q1 off whenever the pack is not charging, discharge included, so the kit's discharge current runs through Q1's body diode: about 2 to 3 W at the reduced load and about 7 W at 10 A on board P. |
| **Affected** | S-46 in `v2/ecad/tools/pcb_requirements.yaml`; board P's thermal design; the pack's temperature ladder (`v2/docs/review-packets/battery/THERMAL-COORDINATION.md`), the mode table, F2's analysis and the E3-A, E4-O and P12 pass lines of `TEST-PLAN.md`; R-BAT (EQ-10). |
| **Evidence** | S-46's title (TI SLUUAQ3A sections 4.12, 4.13 and 14.2.1.1); the battery packet's REVIEW-REQUEST.md question Q-P18 and the TI question Q-TI-10. |
| **Attempts and results** | Found by the battery stream's second independent check in round 8 (27 September 2026); not yet answered. |
| **Viable options** | (a) A FET Options setting that keeps discharge on, with the charge-start protection kept another way; (b) a separate charge-path FET; (c) a thermal budget for the diode. |
| **Recommended next action** | Ask the qualified battery reviewer Q-P18 and TI Q-TI-10 in the prepared texts (the owner's contact); meanwhile carry option (c)'s budget on board P as a bound, not as the answer, and keep S-46 open. |
| **Expertise or equipment** | A battery protection engineer familiar with the BQ4050 (R-BAT). |
| **Cost and lead time** | Inside R-BAT's cost (EQ-10); TI's answer time unknown. |

### EQ-16. The dock's VIN_RAW contacts over their rating (R8E-N01)

| | |
|---|---|
| **Exact issue** | Since round 8 board E declares 14.10 A on its own VIN_RAW (the vehicle entry at most 6.15 A plus the panel tracker 10.33 A, limited by what board A's front end draws). Across the four Preci-Dip 813 VIN_RAW contacts that is 3.53 A each with even sharing, 101 percent of the 3.5 A rating, so the contract is NOT MET at nominal; board A still declares 12.31 A. |
| **Affected** | The A to E interface's `power_capacity` in `v2/ecad/tools/pcb_interfaces.yaml` (findings R8E-N01, R4A-N13); boards A, E and E5; the contact count of the dock block. |
| **Evidence** | `pcb_interfaces.yaml`, the A to E contract's `e_declares` and `margin` (Preci-Dip 813, "OPERATING CURRENT Max. 3.5 A", `v2/vendor/precidip/`). |
| **Attempts and results** | Recorded by round 8's board E stream; no remedy drawn. |
| **Viable options** | (a) A fifth VIN_RAW contact; (b) a front-end input current bound in hardware on board A; (c) the host's IIN_HOST limit extended to the panel, a firmware bound only. |
| **Recommended next action** | (a) or (b), decided by board A's stream with the dock block's outline (layer 7); (c) alone does not meet the rule because it is not hardware. |
| **Expertise or equipment** | None beyond the design streams. |
| **Cost and lead time** | Desk work. |

### EQ-17. Board A's +3V3 overvoltage window

| | |
|---|---|
| **Exact issue** | Round 8 put SN74AUP1G08 gates on board A's +3V3 to read both EMCON lines for the PA and HF rails. The SN74AUP1G08's absolute maximum supply is 4.6 V (TI SCES502Q section 5.1), but the rail's clamp D3, an SMBJ5.0A, starts at 6.40 V minimum breakdown, so a fault between 4.6 V and 6.4 V on +3V3 can destroy the gates that hold the transmit rails off. |
| **Affected** | Board A's EMCON gating (`c0133147`); `v2/docs/feasibility/EMCON.md` sections 4a and 7 (an OPEN item there); the SOURCES entry of the part. |
| **Evidence** | Commit `c0133147`'s body; EMCON.md sections 4a and 7. |
| **Attempts and results** | Recorded OPEN in round 8; no change drawn. **Set 5 (board A stream w3a, integrated in `fnd/r8int5`):** option (c) is taken without the local clamp it names; the eFuse's lockout and a filter bound the gates' supply instead. U35 to U38 run from `+3V3_EMCON` behind the eFuse U39 (TPS259631DDAR, overvoltage lockout at 3.83 to 4.11 V of +3V3, SLVSET8A) and a 100 Ohm filter into their own 100 nF, and the software holds reach them through U40 (SN74LVC2G07, open drain, 6.5 V) pulled up to the protected rail. The bound: with D3 holding +3V3 at 9.2 V or less the gates stay under 4.6 V unless U39's tOVLO (1.3 us typical, no maximum stated) exceeds about 9.5 us, which bench E-11's injection checks. (a) was refused because no clamp holds under 4.6 V at U12's 4.2 to 5.8 A, (b) because the SN74LVC1G08 is rated 6.5 V, inside D3's range, and undoes round 8's hold. Board A regenerated with parity; RF-002's walk on A prints the same verdicts before and after. The rest of +3V3 against D3 (U30 on `PA_EN`, U40) is a registry open item. **Status:** closed at desk with that bound; R-PWR (EQ-11) reviews it. |
| **Viable options** | (a) A lower-voltage clamp on +3V3 whose clamping voltage sits below 4.6 V at the fault current; (b) a gate family rated above the clamp; (c) a series element and a local clamp at the gates only. |
| **Recommended next action** | Board A's stream picks one with the maker's clamping curve read, and the RF-002 walk is re-taken on A. |
| **Expertise or equipment** | None beyond the design streams; R-PWR (EQ-11) reviews it. |
| **Cost and lead time** | Desk work. |

### EQ-18. RF-002 cannot decide TX_INHIBIT_n through board C's U14

| | |
|---|---|
| **Exact issue** | Board C's hardware EMCON lamp (round 8, SD-EMC-6) put U14, a TI SN74LVC1G57 configurable gate, on TX_INHIBIT_n and EMCON_HW. The RF-002 walk (`v2/ecad/tools/tx_inhibit.py`) has no row for that family, whose function depends on how its In1 pin is wired, so it reads the TX_INHIBIT_n line UNDECIDED ("an active pin no held document shows to be an input") and every option riding that line inherits it: inhibit_chain A FAIL (1 fail, 5 pass, 3 undecided), B FAIL, C FAIL, D INCONCLUSIVE, E and P PASS. |
| **Affected** | RF-002 on every board whose transmitter inhibit rides TX_INHIBIT_n; FEA-002; board C's U14. |
| **Evidence** | Commit `9f28c238`'s body; `v2/docs/feasibility/EMCON.md` section 8 (the pin map, II and Ioff handed to the tools author). |
| **Attempts and results** | The session chose not to add an unchecked LOGIC row (a tool change without its independent check); the walk fails closed meanwhile. **Set 5 (stream w3t, integrated in `fnd/r8int5`):** option (a) is taken. `tx_inhibit.py` has a row for the SN74LVC1G57 (SCES414P: the pin map, II 1 uA, Ioff 10 uA, the input clamp row and the 6.5 V rating) read only in Figure 7's wiring, In1 on the part's own GND pin, where Table 1 gives Y = NOR(In0, In2); any other wiring reads UNDECIDED by any pin, and a HIGH at a Schmitt input never passes (limits 13 and 14). Five fixtures both ways, SCES414P Table 1 transcribed as the independent check, three mutations caught; an independent AI check reproduced the readings (not a qualified review). On main `38dcd764`'s netlists the `EMCON_HW` line now reads PASS and board B's RockBLOCK 9704 and E22 with it; `TX_INHIBIT_n` reads FAIL on its fail-safe state (EQ-25). Record: `v2/docs/records/w3t/`. **Status:** the tool question is closed; the circuit question moves to EQ-25. |
| **Viable options** | (a) A LOGIC row conditioned on In1's wiring, with its fixture and an independent check; (b) a fixed-function gate on board C instead of the SN74LVC1G57. |
| **Recommended next action** | (a) by the tools stream, then the RF-002 re-take on all six boards. |
| **Expertise or equipment** | None. |
| **Cost and lead time** | Desk work. |

### EQ-19. PWR-001's undeclared supplies on boards A, B, D and E

| | |
|---|---|
| **Exact issue** | Since round 8 set 2, PWR-001 is judged on the committed netlist and fails closed on every supply. It reads FAIL on current evidence on A (VMON, the bootstraps, PD_VTX, PD_VAUX, PD_DVDD), B (28 supplies undeclared, 26 undecided; declared since stream w3b, 27 September 2026: 17 rails and 40 nodes, each from its maker's sheet, and PWR-001 read PASS of 59 in the stream's scratch on the candidate netlist, awaiting the consolidated re-take), D (AMP_CPN, AMP_CPP, AMP_HPVSS, the PCM2912A's regulator outputs, SAU_3V3) and E (E6_BST, E6_DVDD, SGP_VDD, TRK_LDO33, TRK_LSENSE); on C and P the FAIL was read on an older netlist and awaits the re-take. |
| **Affected** | PWR-001 and the layout entry of every board; each generator's intent declarations. |
| **Evidence** | Commit `84e52461`'s body; `v2/docs/CURRENT-EVIDENCE.md`; `v2/docs/records/ts-net/ts-net-decisions.md` (TSN-D1, what counts as a power net). |
| **Attempts and results** | The rule's instrument changed in `940cbcdf`; no board's intent has been extended yet. **Set 5 (`fnd/r8int5`), board A (stream w3a):** VMON, PRECHG, +3V3_EMCON_EF and +3V3_EMCON declared as rails, B33_BST, HT_BST, S1_BOOT, S3_BOOT, PD_VTX, PD_VAUX, PD_DVDD, PD_CC1 and PD_CC2 as nodes, each from its maker's sheet; PWR-001 on A's regenerated netlist reads PASS of 35 (34 declared rails, 0 undecided). **Board B (stream w3b):** every one of the 28 undeclared and 26 undecided nets declared, a rail where it carries a current (VBAT_RTC, the coin-cell net renamed from VBAT by W3B-R1, the three flashing VBUS, the SIM supplies, the GNSS antenna feed, the PoE port's feed and return conductors) and a node where it is one part's own supply or a signal (the fourteen bootstraps, the four CP2102N regulator outputs, the three STM32H743 VCAP, the resets, nRPIBOOT, the PWR-LED feeds, the RF pads, the PoE control lines); one more net, GNSS_RF_IN, became undecided once the antenna feed was declared and is declared too; PWR-001 read PASS of 59 in the stream's scratch. Reading the TPS23861 and LG290P sheets for it found W3B-F1 and W3B-F2 (drawn) and S-71 to S-73 (open). D and E stay open. |
| **Viable options** | Declare each supply in the board's intent (rail or node, with its source and limits), or show it is not a supply by the rule's own definition. |
| **Recommended next action** | Each board stream declares its list, then the consolidated re-take. |
| **Expertise or equipment** | None. |
| **Cost and lead time** | Desk work. |

### EQ-20. Board B's round 8 circuit, not merged

| | |
|---|---|
| **Exact issue** | Board B's round 8 circuit (the failover fabric's lock and re-arm timing, among others) exists only in the worktree `fnd/r8b` (bundled since H1.1 as the UNACCEPTED candidate patch `v2/docs/handover/candidates/r8b.patch`, base `fc144600`), so H1's board B is the pre-round-8 B21 netlist. Its own record states one residual: a vote returning within about 13 ns of the select buffer's threshold decision (its 7.0 ns delay plus an XOR's 5.8 ns) while a flapping vote has parked ARM's node within about 30 uV of ARM's lower threshold could make an enable pulse under 13 ns; no single change and no single return reaches it, and the simulation's aimed adversary did not. |
| **Affected** | Board B's netlist and every reading on it; FEA-003's fabric half; `ARCH-PCB-B-IOHA.md` (r8b's patch must be re-derived on the text hc6 reconciled); FAILOVER-FABRIC. |
| **Evidence** | `drafts/r8-decisions.md` of `fnd/r8b`, with the simulator `drafts/b/tools/bbm_sim_r8b.py` and its outputs `drafts/b/evidence/bbm-sim-*.txt`: not in H1's design; since H1.1 all are inside `v2/docs/handover/candidates/r8b.patch` (apply it to `fc144600`, or read the added files in the patch text). The candidate's last independent check (an AI review) had no blocking finding (`candidates/README.md`). |
| **Attempts and results** | The record's break-before-make simulation on the regenerated netlist (seed 27, 1,500 random waveforms per bank): 19,976 runs, 56,342 select moves, 0 violations, least lead 61.5 us, least hold 198 us; with the static-1 hazard in every 74LVC1G157, 22,121 runs, 0 violations. A simulation, not a bench result. |
| **Viable options** | Merge with the residual stated as a bounded risk, or add a minimum-pulse filter on the enable and re-simulate. |
| **Recommended next action** | Merge r8b (apply `candidates/r8b.patch` to `fc144600`, re-derive its drafted page patches on the current text) with parity and the residual written into FAILOVER-FABRIC; R-HSD (EQ-12) judges whether a sub-13 ns enable pulse matters to the switches it drives. **Done for the merge after H1.1:** board B's round 8 is on main at `b76c18cb` (integrated in `cc3313f3`) and FAILOVER-FABRIC states the residual (its round 8 section); what remains is R-HSD's judgement and the re-take of B's readings on its new netlist. |
| **Expertise or equipment** | A high-speed or logic-timing reviewer. |
| **Cost and lead time** | Desk work; R-HSD's cost. |

### EQ-21. No MPN in the generators, no order code on most BOM rows

| | |
|---|---|
| **Exact issue** | The schematic generators write Reference, Value, Footprint, Description, Datasheet and, where one is chosen, an LCSC order code; they write no manufacturer part number. At H1, 1497 of the 2205 per-reference rows of the six schematic BOMs carry no LCSC code, 1322 of them resistors, capacitors and inductors named by value and land; `lcsc_fill.py` assigns codes at the JLC BOM stage. The schematic BOM alone therefore does not give the exact manufacturer, MPN, package and grade layer 6 asks for. |
| **Affected** | Layer 6 on every board; the NOT_FOR_FAB BOMs in `v2/release/handover/_generated/`. |
| **Evidence** | Those BOMs; `v2/docs/handover/REGENERATE.md` section 5; decided identities live in `v2/vendor/SOURCES.yaml`. |
| **Attempts and results** | Found by the handover packer; counts re-read at H1. |
| **Viable options** | (a) An MPN field written by each generator from SOURCES.yaml, with a check that every fitted line carries one; (b) a per-board identity BOM generated from the netlist and SOURCES.yaml, passives resolved by rule (series, tolerance, voltage, dielectric); (c) accept LCSC codes as identity for passives, stated as such. |
| **Recommended next action** | (b) first, since it changes no generator; then (a). |
| **Expertise or equipment** | None. |
| **Cost and lead time** | Desk work. |

### EQ-22. The hot stop's signal path, HOT-R1, is in no generator (S-57)

| | |
|---|---|
| **Exact issue** | Past the heat stage the kit acts on the pack's measured cell temperature (the hot stop, `v2/docs/CONOPS.md` section 4c; requirement REQ-077; session choices SC-49 and SC-50). Board E's sensor controller is the pack gauge's only SMBus host; the panel controller, which owns the slot enables, the switched loads and `PI_KILL`, reaches it as generated only over USB through a compute module's bridge, which the heat stage as board B is generated does not host and which the stop's own first step removes. HOT-R1, the session's line from the sensor controller's GPIO19 through an open-drain 2N7002 on board E over the dock's spare contact (E `J_BLK` pin 12 to A `J_DOCK` pin 12) to board A's expander input and `EXP_INT`, with a 10 k pull-up on A, is drawn on neither board. |
| **Affected** | REQ-077 (FAIL on the generated boards until drawn), boards A and E, IF-AE-DOCK's pin 12, the sensor and panel controllers' firmware contracts, `TEST-PLAN.md` E3-H. |
| **Evidence** | `gen_sch_e.py` at `a8652172` (unchanged since): `J_BLK` pin 12 (`BLK_SPARE`) reaches only TP7, U10's GPIO19 (pin 30) is not connected; `gen_sch_a.py`: `J_DOCK` pin 12 (`DOCK_SPARE`) lands on U27 pin 18, whose `EXP_INT` (R110) is the panel controller's interrupt; `gen_sch_c.py` (U3 GPIO24 `EXP_INT`, GPIO13 to 15 `SLOT_EN`, GPIO19 `PI_KILL`); `v2/docs/records/hc3/blocked-questions-layer-3.md` item 13. |
| **Attempts and results** | A stand-in on board B's TMP117 was drafted and kept only as the fallback for a lost sensor controller (+55.0 and +56.0 C), because the finding asks for the cells' own temperature on every input state. |
| **Viable options** | (a) HOT-R1 as taken (SC-50): four line states (1 Hz ok, 5 Hz H1, held low H2, held high detector lost); (b) a USB-only path, which needs a module hosting both controllers' banks to keep running in the heat stage (not as generated; H1 stops it anyway); (c) a kit-bus device on board E that the panel polls (a part and a bus branch through a dock with no spare pair). |
| **Recommended next action** | (a) at the next regeneration of boards A and E, before their layout entry; then E3-H on the bench. |
| **Expertise or equipment** | The board A and E authors; the E3-H bench check. |
| **Cost and lead time** | One transistor and two resistors per kit; desk work at the next regeneration. |

### EQ-25. TX_INHIBIT_n's fail-safe level with board C unpowered (W3T-F1)

| | |
|---|---|
| **Exact issue** | With board C unpowered, `TX_INHIBIT_n` is held low only by its three 100 kOhm pull-downs (board A R145, board B R59, board D R2; 35 kOhm together at 5 percent) against 31 uA of stated pin current: board C's U9 (74LVC1G17, Ioff 10 uA, DS35124) and U14 (SN74LVC1G57, Ioff 10 uA, SCES414P 6.5), board D's U12 (10 uA) and board A's U35 and U37 (0.5 uA each). That is 1.09 V, over the 0.8 V VIL the RF-002 walk applies to its readers (TI states 0.9 V for A's SN74AUP1G08s and 0.8 V for D's U12, which reads the line when only board C is off), so RF-002's fail-safe state FAILS on boards A to D and board D's SA868 keying inherits it. Before round 8's lamp gate U14 the same state read 0.74 V. |
| **Affected** | RF-002 (`inhibit_chain_a` to `_d`), board D's SA868 keying row in `v2/docs/feasibility/EMCON.md`, FEA-002; the open item S-64 in `v2/ecad/tools/pcb_requirements.yaml`. |
| **Evidence** | `v2/docs/records/w3t/w3t-decisions.md` section 5 and `HANDOFF.md` section 2 (the arithmetic of every option); `readings/inhibit-chain-before-after.txt` there; board C's `gen_sch_c.py` (R14, U9, U14). |
| **Attempts and results** | Found by stream w3t's re-take after EQ-18's row (27 September 2026, integrated in `fnd/r8int5`). The FAIL rests on the walk's worst-case leakage convention (round 6: an unpowered part passes its Ioff, a part that may be either the larger of II and Ioff). The three sheets also state II at VCC 0 V (SCES414P 1 uA, DS35124 5 uA, SCES217AA 5 uA): with only U14 at II the line reads about 0.77 V, with U9, U14 and D's U12 at II about 0.42 V. So it is a FAIL under the tree's convention, not a demonstrated defect; the remedy is margin. Each option below was checked with the walk on an in-memory copy of the netlists and reads the line PASS; board D's SA868 then returns to its own UNDECIDED (its maker states no PTT threshold). |
| **Viable options** | (a) Board C: R14 10 k to 2.2 k 1 percent and a new 10 k 1 percent pull-down on `TX_INHIBIT_n`: about 0.24 V failed safe, idle HIGH 2.57 V nominal and 2.37 V at the adverse ends (above U14's about 2.04 V and U9's about 2.15 V VT+ at 3.3 V), the toggle sinking 1.6 mA; one board. (b) Board B's R59 to 10 k 1 percent with R14 2.2 k: 0.26 V, idle 2.41 V adverse; two boards. (c) All three pull-downs to 47 k with R14 4.7 k: 0.51 V, idle 2.27 V adverse; four boards. Main's idle HIGH is 2.54 V nominal and 2.11 V adverse: every option widens it. |
| **Recommended next action** | (a) at board C's next circuit round, regenerated with parity, then the RF-002 re-take on boards A to D. |
| **Expertise or equipment** | None beyond the board C stream; bench E-01 and E-11 for the lines' real levels. |
| **Cost and lead time** | One resistor changed and one added on board C; desk work. |

### EQ-24. The QMX lid tray does not fit the unit's connector layout (S-63)

| | |
|---|---|
| **Exact issue** | The QMX lid tray released in `v2/release/case-2026-09-27/lid-tray-qmx/` (sheet 14) has cable notches in one end wall only, while the held QRP Labs QMX manual (1_04_004, pages 7 to 9) puts the DC jack on the left panel and the BNC and USB-C on the right panel. The unit's 95 x 63 x 25 and the notch heights are checked against no maker drawing. |
| **Affected** | The tray (a made part) and its print; the lid harness' route; nothing on a board (`J_QMX`, `J_HF` and `J_RF2` stay). |
| **Evidence** | `v2/docs/CASE-FIT-UNCERTAINTIES.md` section 3; sheet 14 note 4; `ASSEMBLY.md`'s QMX row; the release README; `v2/docs/records/hc7/c7-response.md`. |
| **Attempts and results** | Found by the layer 7 fixer c7 while drawing sheet 14, which draws the part where `scene.py` places it with its turned-end twin dotted; no direction is chosen for the notched end. |
| **Viable options** | (a) Revise the tray from the QMX enclosure drawing (notches or openings at both ends, the pocket from the maker's figures) before it is printed; (b) keep the tray and route the DC lead round the unit (a cable strain and a lid-closing risk); (c) a strap-only mount without a tray (loses the tray's retention). |
| **Recommended next action** | (a): desk work on a made part, no board moves and no money. |
| **Expertise or equipment** | The case writer; the maker's enclosure drawing (to be filed in `v2/vendor/`). |
| **Cost and lead time** | Desk work; a reprint of the tray when the prototype's printed parts are made. |

## B. Physical evidence

### EQ-05. The sealed case's thermal conductance and the hot end

| | |
|---|---|
| **Exact issue** | The inside-air-to-ambient conductance of the sealed Peli 1450 with its aluminium face plate and fans is known only as a bound: 1.22 to 2.85 W/K lid open with fans on (1.06 to 2.49 lid closed) on the independent W4 model, against 3.0 to 3.3 W/K in appendix 32.53, a spread of about 2.3 times. On the low end, three typical modules at +20 C put the cells at up to 81 C against their 60 C discharge limit, the charge hold-off could fall anywhere from -18 to +19 C, and the PA's flange patch reaches 95 to 118 C in a 60 s key-down against the maker's 90 C reliability and +100 C case figures. The bound includes failure and nothing has been measured. **Since the layer 2 merge (set 4, `95e078a1`) the question also decides whether the hot stop fires inside the envelope:** past the heat stage the kit sheds to its minimum load when the hottest cell reads +56.5 C and shuts down at +57.0 C (REQ-077, SC-49); at the independent bound's worst corner its first step acts from +33.2 C lid closed and +36.1 C lid open, on appendix 32.53's conductance not below +40.3 C and +48.1 C (`v2/docs/records/hc2/hotstop_bounds.out`, INFERRED). Where it fires at +40 C the kit runs no module there on any supply, so REQ-052's stage criteria and REQ-024's use at +40 C are not met there (recorded, not waived); REQ-077 requires the stop to keep the cells inside +60 C and the design intends it to, once HOT-R1 is drawn (EQ-22) and on the provisional error budget (`TEST-PLAN.md` P14). |
| **Affected** | FEA-004; REQ-077 and, wherever the hot stop fires at +40 C, REQ-052's stage criteria and REQ-024's use at +40 C; D-02b's reduced mode (S-24) and its accepted consequences; the +35 C and +25 C controls; CON-013, REQ-014, REQ-052, REQ-059; THM-001 on every board; hot-part placement on A, B, D and P; the pack location; fans (D-18); board D's flange sensor (PWR-F15); NEED-03 availability across the envelope; possibly the thermal architecture. |
| **Evidence** | `v2/docs/feasibility/POWER-THERMAL.md` section 0 items 5 and 7, sections 9.1 to 9.3 and 10 (lines 745 to 770, 794 to 806, 851 to 863, 1043 to 1056); `v2/docs/ARCHITECTURE.md` sections 8.2 and 8.4; `v2/docs/records/w4/w4-scratch-thermal.py`; appendix 32.53 (line 2860) and 32.56 (line 2940); the owner's second review, finding B; for the hot stop, `v2/docs/CONOPS.md` section 4c, `v2/docs/records/hc2/hotstop_bounds.py` and `.out`, and `v2/docs/records/hc3/blocked-questions-layer-3.md` item 15. |
| **Attempts and results** | Two independent desk models and five checker cycles on POWER-THERMAL narrowed the loads but cannot narrow the conductance. The session made the behaviour control-driven (C1 to C4, key-down rules K1 to K5, PROVISIONAL) so it no longer bets on either end. |
| **Viable options** | (a) The empty-case heat-balance test now, on the prototype's own case: a plate blank, 20, 40 and 60 W of resistive heat on a dummy stack, fans on and off, lid open and closed, plus a 45 to 83 W block at the PA flange site run for 20, 30 and 60 s. (b) A desk lumped or CFD model to narrow the bound; it does not replace the test. (c) Wait for TEST-PLAN E3 on the built kit, accepting that placement and the three-module claim may change after fabrication. (d) Design to the pessimistic bound (shedding to one module from low ambients), which narrows a core function and needs the owner. Lowering the hot end of the envelope is not an option: it lowers a requirement. |
| **Recommended next action** | Now: (b), define the reduced mode S-24 against the pessimistic bound, and state behaviour on measured internal thresholds so layer 2 can close. Before hot-part placement of A, B, D and P and the pack location are frozen: (a). The case and frame are prototype parts bought early, so the decision is when to buy them, not whether; run the heat test first while the case is undrilled, then the mock-up (EQ-08) in the same case (READY-TO-ACT section 11, S-1). Restage FEA-004 so the test gates hot-part placement and holds board B too. |
| **Expertise or equipment** | A current-moulding Peli 1450 with the 1450PF frame; a 3 mm aluminium plate blank (the C1 outline); three 50 W-class wirewound resistors (6.8 ohm at 12 V gives about 21 W each); a 100 W-class 2.2 ohm block for the PA site; two mixer fans and cooler-class fans; a PicoLog TC-08 with ten type K thermocouples; a supply of at least 15 V and 7 A; a person to run several multi-hour soaks and a way for the data to reach the design. |
| **Cost and lead time** | VERIFIED: case EUR 168.90 and frame EUR 29.66 excl. VAT (in stock), logger GBP 349 (in stock). Plate blank by quote, from 2 days at JLCCNC; heaters, fans, thermocouples and supply TBD (READY-TO-ACT sections 5.2 and 5.3). Authorisation missing: the purchase, who runs it, and where. |

### EQ-06. ZEROIZE on the fitted ATECC608B, and board B's U8

| | |
|---|---|
| **Exact issue** | ZEROIZE (D-03) destroys two key-encryption keys in the secure element with GenKey mode 0x04 after the zones are locked. Public Microchip documents support the mechanism at desk level, but two properties are unpublished: what GenKey does when power fails part-way through its write (U1), and the fitted ATECC608B-SSHDA-T's factory configuration, including its default address (U4). They decide whether U8 stays the ATECC608B or switches to the Infineon SLB 9673 TPM 2.0 (or NXP SE050E2HQ1). |
| **Affected** | FEA-001; board B's U8 part and land (SOIC-8, or UQFN-32 for the TPM); the panel firmware; REQ-035, REQ-038, ASM-005; D-03; decision 30; NEED-10 (core); the R-SEC review's scope. |
| **Evidence** | `v2/docs/feasibility/ZEROIZE.md` sections 1, 5 and 7; `v2/docs/records/rv-zer/zeroize/zer_config.py` and `zer_budget.py`; `v2/vendor/SOURCES.yaml` owed list (the full datasheet is under NDA); CURRENT-EVIDENCE line 97. |
| **Attempts and results** | Desk study from DS40002250B, DS40002249B and the CryptoAuthLib v3.8.0 tests: mechanism supported at desk, part OPEN. Nine software fixtures pass; the owner's second review notes that fixtures do not prove silicon permissions, interrupted-power behaviour or worst-case timing. |
| **Viable options** | (a) Z-EXP-A (function on the fitted MPN, about 2 h, three parts) and Z-EXP-B (power cut during GenKey 1,000 times on each of two parts) on a development rig. (b) The SLB 9673 fallback under ZEROIZE.md's switch conditions, after checking its documents, interfaces and availability (JLCPCB showed no stock of any variant on 26 September). (c) The SE050E2HQ1 with its own bench run. (d) Microchip's NDA datasheet, through the owner. |
| **Recommended next action** | Authorise the bench parts and run (a) before board B's layout entry. Draw (b)'s alternate footprint only if the bench fails. Do not switch parts merely to escape the uncertainty. |
| **Expertise or equipment** | An embedded engineer; Microchip DM320118 or a SOIC socket board (the MikroE Secure SOIC click), a Raspberry Pi Pico, a load switch; a lab host the session can reach. |
| **Cost and lead time** | VERIFIED: USD 8.09 (ten ATECC608B), USD 2.95 (breakouts), GBP 3.80 (Pico); USD 58.00 more for the MikroE board if still obtainable. DM320118 and instruments TBD; lead time TBD (READY-TO-ACT sections 3.3 and 3.4). Authorisation missing: L-06 (D-09: nothing beyond the voucher without a quote and the owner's approval). |

### EQ-07. The chemical fuse F2 at 18 A for 60 s

| | |
|---|---|
| **Exact issue** | F2 (Eaton SCF9550-30-05, rated -20 to +60 C, no current derating published) dissipates 0.32 to 0.81 W at 18 A and sits at the cell block's temperature. Every PA key-down makes up to 18 A a 60 s service current (PWR-F12), and F2's margin during a key-down from a +55 C block is unknown; its opening ends the pack. |
| **Affected** | FEA-004 (P's fabrication release; P's layout entry once restaged); REQ-018's key-down time; K1, K2 and SC-10; the pack protection test; P's F2 part and land (the evaluated alternative, Littelfuse ITV9550L1430, publishes 25 A at 60 C). F2 also read stock 0 at JLCPCB on 25 and 26 September (SOURCES.yaml). |
| **Evidence** | POWER-THERMAL.md lines 971 and 1136 and section 0 item 8; `gen_sch_p.py` lines 247 to 289; `v2/vendor/battery/eaton-scf9550-elx1135.pdf`; `v2/docs/review-packets/battery/FUSE-INTERPRETATION.md` lines 49 to 101 and 185 to 193. |
| **Attempts and results** | The maker's document read; a desk bound only. Eaton questions Q-E1 to Q-E5 are prepared (FUSE-INTERPRETATION section 7), not sent. |
| **Viable options** | (a) Eaton's written answer on behaviour above +60 C at 18 A. (b) A coupon test of the part alone at 18 A for 60 s from +55 C with a thermocouple on its body. (c) Lower K2's +55 C start gate by F2's measured rise, shortening key-downs at the hot end. (d) Change F2 to the ITV9550L1430, with its own land and qualification. |
| **Recommended next action** | (b), with (a) sent in parallel. Until then keep K2 at +55 C and state the unknown; hold P's layout entry on F2's identity. |
| **Expertise or equipment** | A bench supply or electronic load of at least 20 A, a temperature-controlled block, a thermocouple and a logger; or the owner's contact with Eaton. |
| **Cost and lead time** | Part cost TBD by quote; Eaton's lead time TBD. |

### EQ-08. Case margins that rest on unpublished tolerances

| | |
|---|---|
| **Exact issue** | 30 of the 70 case margins, the frame seat M20 and the arrestor thread M13 rest on allowances no source states: Peli's unpublished moulding tolerance, the frame ring and skirt, hand marking, the legs' locator, gasket compression and bundle ties. The jumper rows need the real plug and cable (M17g at -2.43 mm and M17x at -0.38 mm fail with the geometry as assumed). Only hardware in a current-moulding 1450 settles them. |
| **Affected** | Board A (east edge at X 120, RF sites, wall-port leads), board B (east edge at X 165 and east-end tall parts, stack height under the monitor), board C (the backer under the face), board E (clamps, south edge, corner pads), board P (pocket place); REQ-019, CON-006, REQ-047; D-07's ANT3; the drilling of the connector and entry plates. |
| **Evidence** | `v2/docs/CASE-MARGINS.md` section 3.2 (35 MET as sensitivity readings, 35 OPEN), section 5 (checks T1 to T11), section 7 (the board each check decides); `v2/vendor/peli/1450/frame_seat.out`, reproduced byte-identical. |
| **Attempts and results** | Seven revisions of CASE-MARGINS on 26 September with agent (AI) checks. The owner's own measurement (D-08) was withdrawn by the owner. The design is held against the worst of Peli's figures with every unstated allowance doubled as a sensitivity test, which bounds nothing that rests on an unstated tolerance. |
| **Viable options** | (a) Authorise the case and frame now, machine the made parts, and run the targeted checks before layout entry of A, B, C, E and P. (b) Enter layout on the design basis and carry the rows to fabrication release, accepting a layout change if a check moves an outline or a connector (CASE-MARGINS section 7 option c). (c) A partial mock-up: case, frame, legs, one arrestor on a spot-faced coupon, the picked jumper plugs with RG-316, and stand-in blocks (T1, T2, T5, T6, T10, T11), buying the monitor only if M1 stays under 2.0 mm after its lookups. |
| **Recommended next action** | Close the desk items first (the jumper plug pick, the sealed RJ45 re-pick; the drawings of the made parts are done, `v2/release/case-2026-09-27/`), then (c) in the same case after the heat test (EQ-05), before the layout entry of boards A, B, E and P, which is BLOCKED on the purchase since 27 September 2026 (FEA-007, L-07; `v2/docs/CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7); option (b) is withdrawn by that allocation (the owner's execution prompt of 27 September 2026, sections 2 and 5). With one case the mock-up follows the heat test, so boards B and E wait on that test too; a second case would decouple them (`v2/docs/reviews/READY-TO-ACT.md` S-1). |
| **Expertise or equipment** | A mechanical assembler with a height gauge, calipers, feeler gauges, hole saws of 27, 29, 22 and 18 mm and a drill; a CNC shop for the plates and legs; an SMA crimp tool for RG-316. |
| **Cost and lead time** | VERIFIED: case EUR 168.90 and frame EUR 29.66 excl. VAT (in stock); one arrestor USD 78.99 (twelve at USD 947.88); monitor USD 569.00; CM5 passive cooler GBP 4.80. Machining by quote once drawn (JLCCNC from 3 business days); jumper plugs and cable TBD (READY-TO-ACT section 6). |

### EQ-09. The CM5's Ethernet PHY on a capacitively coupled link

| | |
|---|---|
| **Exact issue** | The Compute Module 5's Broadcom BCM54210PE termination and common-mode requirements for a capacitively coupled PHY-to-PHY gigabit link are unpublished. Board B's three transformerless module links to the KSZ9897 (decision 29) are "defensible to lay out; not shown to work". |
| **Affected** | Decision 29; INT-003; board B's parts (24 coupling capacitors against three magnetics) and the Ethernet region's area; a respin if INT-003 fails with no footprint provision. |
| **Evidence** | `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` sections 4, 5 and 7; `v2/ecad/tools/pcb_rules.yaml` lines 1540 to 1648; Microchip DS00004151A section 6.6. |
| **Attempts and results** | A desk assessment (AI, labelled): the switch vendor's clause matched item by item; the CM5 IO board's reference design read (centre taps on a capacitor to ground, INFERRED voltage mode). |
| **Viable options** | (a) A written answer from Raspberry Pi or Broadcom. (b) Keep the capacitive links and add a do-not-fit magnetics footprint so the fallback is not a respin. (c) A development-hardware link test before layout (a CM5 IO board, a KSZ9897 evaluation board, a traffic generator). (d) Fit extended-temperature magnetics now. INT-003 on the built board stays the acceptance test in every case. |
| **Recommended next action** | (b) now as a session choice, stating the coupling capacitors' voltage and dielectric in the netlist; (a) in parallel (text prepared by the session, sent by the owner); (c) if it is cheap. |
| **Expertise or equipment** | An Ethernet PHY engineer, or a bench with the boards above. |
| **Cost and lead time** | The question: no cost, lead time unknown. The footprint provision: board area only. The development test: not priced. |

---

## C. External authorisation

### EQ-10. Qualified battery review R-BAT and the pack protection coordination

| | |
|---|---|
| **Exact issue** | Board P's protection (BQ4050 primary, BQ7720700 second-level protector, SCF9550 chemical fuse) has only AI review, and owner ruling D-09 requires a qualified battery and protection review before the pack is built. Open within it: the second level's over-temperature window of 62.7 to 77.5 C is not coordinated with the cells' 60 C limit (thresholds, tolerance, sensor placement and lag, behaviour with the primary failed); F1 opening before F2 on a hard short (Q-E4) is unproven; FET safe operating area (BAT-F07), BAT-F12 and BAT-F14 are open; F2's rating is EQ-07. |
| **Affected** | FEA-005 and FEA-004 (PWR-F12); board P's circuit (U2 option, thermistor network, F2) and possibly its protection strategy after layout; board A's charger interaction; REQ-044; decision 40; D-09; the pack build; the storage configuration decision (CFL-017) interacts with it. |
| **Evidence** | `v2/docs/review-packets/battery/REVIEW-REQUEST.md`; `SECONDARY-OT-DECISION.md` lines 110 to 165; `FUSE-INTERPRETATION.md` lines 49 to 101 and 185 to 193; POWER-THERMAL section 0 item 8; the owner's second review, finding B. |
| **Attempts and results** | Agent-only reviews, stated as such. The secondary over-temperature was restored on its own thermistor (`d90f30e4`). `evidence/check_manifest.py` reads RELEASE CHECK PASS (132 rows) on an export of `e3aedb25`. The packet's charger reading is board A at `1f614233` plus an uncommitted candidate, and its manifest does not bind `gen_sch_a.py`. A coordination draft exists in an unmerged branch. |
| **Viable options** | (a) The owner sends the prepared request to the three shortlisted firms and approves a quote. No other option satisfies D-09. |
| **Recommended next action** | Finish the secondary over-temperature coordination at desk; bind the charger reading to main's board A (add `gen_sch_a.py` to the manifest's cited documents); confirm `check_manifest.py` passes at the commit whose link is sent; then the owner sends the request (READY-TO-ACT section 2.1) and the Eaton questions. |
| **Expertise or equipment** | A qualified Li-ion pack protection engineer outside the authoring agents (gauges, second-level protectors, chemical fuses; IEC 62133-2 and UN 38.3 familiarity). The packet's shortlist, read from public pages and not contacted: Accutronics Ltd (UK), Engineering Spirit B.V. (the Netherlands), Jauch Quartz GmbH battery technology (Germany); TI's partner directory as a fourth source. |
| **Cost and lead time** | TBD by quote; no candidate publishes a price. Approved in principle by D-09 (open item L-03: the quote and the owner's approval). |

### EQ-11. Qualified power review R-PWR

| | |
|---|---|
| **Exact issue** | Board A's corrected power design (the LM5176 four-switch buck-boost stages, the BQ25731 charger, the TPS25740A USB-C PD stage, the TPS259631 eFuses, the LTC2954 push-button controller, the pack node at 18 A), board E's input stage and board B's TPS23861 PoE PSE have only AI review. `v2/docs/reviews/REVIEW-ROUTES.md` line 22 and open item L-04 time a qualified power review before board A enters layout; D-09 did not approve it. The records disagree on its staging (EXECUTION-PLAN lines 118 to 126 and FEA-004 do not gate on it). |
| **Affected** | Board A's layout commitment and layer 8 completion for A; board E's input stage; board B's PSE; FEA-004; CMP-001 on A; REQ-014, REQ-018. |
| **Evidence** | REVIEW-ROUTES.md, R-PWR questions 1 to 8; ARCHITECTURE.md section 14.2, row A; READY-TO-ACT section 2.3; `v2/docs/records/r4a/r4-decisions.md` and `r4-open-items.md`. |
| **Attempts and results** | Rounds 4 to 6 AI author and refuter reviews and board A's calculation record. The scripts behind the record (`loop_design.py`, `bulk_ripple.py`, `ripple_dense.py`, `softstart.py`, `restart.py`, `comp9_corners.py` and their runs) are not in the tree, so a reviewer can check each figure by hand but cannot re-run the searches. No board A review packet exists at any revision. |
| **Viable options** | (a) Commission R-PWR as written, possibly with the R-BAT engineer, since the charger sits in both scopes. (b) A narrower review of the PoE and USB-C PD stages and the eFuses only. (c) Restage R-PWR to fabrication release, with the owner accepting in writing the risk of layout rework. (d) Proceed on AI review only, which the records do not accept for board A. |
| **Recommended next action** | File board A's converter scripts into `v2/docs/records/r4a/`; build board A's packet at the round 8 merge; reconcile R-PWR's staging in one place; then commission (a), combined with R-BAT where one engineer covers both. |
| **Expertise or equipment** | A power-electronics design engineer (four-switch buck-boost, NVDC chargers, eFuses, PoE PSE, USB-C PD). Provider options read from public pages, not contacted: Elteknik P.C. (Greece), VDL Sintecs (the Netherlands; power integrity side only), the How2Power consultants directory, TI's partner directory. |
| **Cost and lead time** | TBD by quote; not covered by D-09 (open item L-04: the decision to commission, a spend ceiling or an approved quote). |

### EQ-12. Qualified high-speed digital review R-HSD

| | |
|---|---|
| **Exact issue** | Board B's PCIe, USB 3 and HDMI fabric (switch lanes, AC coupling, reference clocks, HCSL terminations, the three transformerless module Ethernet links, the stackup) has only AI review. REVIEW-ROUTES line 23 and open item L-05 time R-HSD before a board B layout is committed, its findings can change the schematic, and it is not commissioned. |
| **Affected** | Board B's schematic and layout; FEA-003 (fabrication stage); INT-003; decisions 29 and 43; layer 8 completion for B. |
| **Evidence** | REVIEW-ROUTES.md, section R-HSD; ARCHITECTURE.md section 14.2, row B; READY-TO-ACT section 2.4 and text T2 (the statement of work); CURRENT-EVIDENCE line 187. |
| **Attempts and results** | AI desk reviews: the fabric map (202 of 202 rows OK on the netlist), the INT-002 assessment (desk PASS); Q-B-ESC-1 INCONCLUSIVE. The AI reviews did find and fix real defects (PCIe pairs wired transmitter to transmitter; FAB-01 to FAB-04 drafted in round 8). |
| **Viable options** | (a) Commission R-HSD as written, with T2. (b) A narrower pre-layout SI review of the failover USB 3 and HDMI channels only. (c) The fabricator's stackup engineering for the impedance question alone. (d) Proceed to EXPERIMENTAL layout only and hold the committed layout on R-HSD. (e) Proceed on AI review, which the records do not accept for board B's layout commitment. |
| **Recommended next action** | (a), once round 8's board B merges, Q-B-ESC-2 has reported and board B's packet is built with `review_packet.py`; meanwhile only experimental layout on board B (standing condition 7). |
| **Expertise or equipment** | A high-speed digital or signal-integrity engineer with PCIe Gen 2 and USB 3 board experience, ideally with 2.5D or 3D field tools. Provider options read from public pages, not contacted: VDL Sintecs (a published pre-layout SI service that asks for a statement of work and schematic PDFs); for the stack question alone, JLCPCB's impedance calculator. |
| **Cost and lead time** | TBD by quote; not covered by D-09 (open item L-05). The eight-layer fabrication price is also a quote (L-01). |

### EQ-13. The M1 mission duration (L-02)

| | |
|---|---|
| **Exact issue** | Owner ruling D-06 leaves the mission duration for M1's pack-plus-solar energy balance for the owner to set later (open item L-02, class OWNER_ACTION), while his standing rule says he is not asked further questions. REQ-016 carries the solar requirement TBD because of it. |
| **Affected** | REQ-016's energy-balance half only, once split; CONOPS mission M1; no board once the solar input window is set. |
| **Evidence** | `pcb_requirements.yaml` line 713 (L-02) and line 2541 (REQ-016); the text of D-06. |
| **Attempts and results** | None: the value is reserved by D-06 and the standing rule forbids asking. |
| **Viable options** | (a) Split REQ-016: settle the hardware window now (open-circuit maximum, tracking range and maximum input power of board E's LT8705A stage) as a core requirement, and let the energy balance wait for L-02 as an advisory record. (b) Keep REQ-016 TBD and layer 3 open. (c) Have the session set the duration from the use case under the standing rule and record it reversibly. |
| **Recommended next action** | (a). The owner may set L-02 whenever he chooses, and no hardware waits on it. Option (c) is not recommended because D-06 reserves the value to the owner; the standing rule stops questions, it does not transfer a value the owner kept. |
| **Expertise or equipment** | None. |
| **Cost and lead time** | None. |

### EQ-14. Fabricator prices per layer count and copper weight

| | |
|---|---|
| **Exact issue** | No fabricator price exists for any board at its alternative layer counts (4, 6, 8) or copper weights, so rule STK-002 cannot close, decision 27's "six if the price is close" for board C is unpriced, decision 43's eight-layer board B is unpriced, and board A's 2 oz option for the 18 A pack path is unpriced. |
| **Affected** | STK-002 on all seven boards; board B (eight layers, L-01); board C (six); board A (2 oz outer); board P (the inner copper weight); the cost half of every written layer decision under the P0 rule. |
| **Evidence** | `v2/docs/LAYER-DECISIONS-2026-09-11.md`, "What is still missing"; decisions 27 and 43 in `v2/ecad/tools/pcb_decisions.yaml`; open item L-01. |
| **Attempts and results** | JLCPCB's public API has no PCB price endpoint (the paths its parts API suggests return 404 without a session); by the project's rule the session never logs into a fabricator account. |
| **Viable options** | (a) The owner's ordering session takes one quote per board at its real outline and quantity five, at each candidate layer count and copper weight, nothing else changed. (b) Proceed at the ruled counts and accept a possible reversal before any order, with the reversal cost stated per board. |
| **Recommended next action** | (a) once round 8 has fixed the outlines; (b) meanwhile. |
| **Expertise or equipment** | The owner's fabricator account. |
| **Cost and lead time** | No cost; minutes per board. |

### EQ-23. A non-destructive hardware stage behind the hot stop (S-58)

| | |
|---|---|
| **Exact issue** | The hot stop is firmware in two controllers (the sensor controller detects, the panel controller acts). What stands behind it on an input is destructive: board P's second level from 62.7 C blows the chemical fuse F2, and the gauge's SOT from 64.2 C and the PTC are permanent. Whether a firmware-free stage that removes the kit's heat without destroying the pack is required is a protection-architecture judgement. |
| **Affected** | REQ-077, REQ-044, REQ-046; boards A, E and P; Q-P15 of the battery packet. |
| **Evidence** | `v2/docs/review-packets/battery/THERMAL-COORDINATION.md` sections 4 (L8 to L12), 7 and 8 (the hold that would enforce 60 C in hardware opens the pack's FETs, which removes no heat on an input); `v2/docs/records/hc3/blocked-questions-layer-3.md` item 14. |
| **Attempts and results** | None drawn; the battery packet's section 8 put its hold to the reviewer rather than adding it. |
| **Viable options** | (a) None: the firmware stop, then the destructive backstops (TI's own layering); (b) the packet's hold on board P alone (removes no heat on an input); (c) a comparator on its own thermistor on the hottest cell, at most 57.5 C with its tolerance and 5 K of hysteresis, taking board A's `KILL` low without firmware (a second dock contact, or a hardware decode of HOT-R1's held-low state on board A). |
| **Recommended next action** | (c), put to the D-09 battery-and-protection reviewer (R-BAT, EQ-10) together with Q-P15; the session keeps (a) with HOT-R1 until the review answers. Decided before the layout entry of boards A, E and P. |
| **Expertise or equipment** | Battery protection and functional safety (the D-09 reviewer); the bench readings P14 and E3-H. |
| **Cost and lead time** | A comparator, a reference, a thermistor and a transistor per kit (no part filed: TBD); R-BAT's quote and lead time (the owner's money, approved in principle by D-09). |
