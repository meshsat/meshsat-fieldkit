# L5-R2: the interface contracts' second round (MESHSAT-1357, 3 October 2026)

Prototype design: nothing here has been built, powered or measured. This page records Layer 5's second round on branch `fnd/l5r2`
from set 28's prepared line `a1f696de` (Layer 5's first pass at `1e18a1ca`, Layers 6 and 7's merged, the re-pins and the registry
rebind applied). It writes into the two files Layer 5 owns, `v2/ecad/tools/pcb_interfaces.yaml` and `v2/docs/HW-FW-CONTRACT.md`,
by `apply_l5r2.py`, and reads them back with `l5r2_interfaces.py` (its output `l5r2_interfaces.out` pins every file by sha256 and
refuses an excerpt that is not in its target, a figure no cited source prints, a lost leaf, or a tbd entry without an owner). No
requirement is changed, nothing is bought or sent, no L4 or L8 record and no generator is edited. Two inputs come from commits not
in this branch's history: L4-E11 section 18 at `b929d8be` and record l8gnd's sections 2 and 3 at `226e9143`; each is copied verbatim
into `inputs/` with its source and sha256, and every contract text resting on either is DRAFTED and PROVISIONAL until its release.

## 1. What was written, by contract (section 1 of the output prints each contract's fields before and after)

| Contract | Fields added (or restated) | Content moved from older keys | Sources |
|---|---|---|---|
| IF-BC-PANEL | harness, judged_by, current (PANEL_5V, per_conductor, signals), protection, levels, default_state, sequencing, mating, tbd; parts named on both ends; slot_power_semantics and cable_out_states SLOT_EN1..3 extended with the keeper | cable to harness, power to current and protection, map_identity.judged_by to judged_by | HC6-SC-7 (PROCUREMENT.md 5) and the Wurth sheets; B19's F1 (MF-MSMF110-2) and Bourns' table; the intent files; record l8gnd 3b, 3g |
| IF-AB-RIBBON | harness, judged_by, levels, current, default_state, sequencing, mating, tbd; parts; cable_out_states and hot_plug extended with the keeper | cable, map_identity.judged_by | HC6-SC-7; A and B netlists; record l8gnd 3g |
| IF-AB-WALL | harness (its length TBD with its effect), judged_by, levels, current (n/a: data only), default_state, sequencing, mating, hot_plug (SESSION), tbd; parts | cable, map_identity.judged_by | HC6-SC-7; ASSEMBLY.md section 4 |
| IF-AD-HARNESS | harness, judged_by, current (power_lead with the VH contact, signals with the +3V3 conductor), levels, default_state, sequencing, mating, hot_plug (SESSION), tbd; parts on both ends | cable, power_lead (under current), map_identity.judged_by | HC6-SC-7; the JST VH catalogue; A's and D's intents (s99a's +5V_D8 band) |
| IF-AC-MAINSW | harness, levels, current, default_state, sequencing, mating, hot_plug (SESSION), tbd; parts on both ends | note to sequencing | the LTC2954 sheet 2954fb p.3; A and C netlists; ASSEMBLY.md |
| IF-AE-RF | harness, levels, current (n/a), default_state (n/a), sequencing, mating, hot_plug, tbd; parts on A and on E's clamp bar (ref: none, a board-file feature) | none | A netlist; ASSEMBLY.md's RF jumpers row |
| IF-A-PA | harness, levels (VDD, VGG, the 50 mW drive against Pin 100 mW), default_state, sequencing, mating, tbd; current.contact; D's part | none | D netlist and gen_sch_d.py's pad; the RA30H1317M1 sheet; the VH catalogue |
| IF-LID-HF | harness, levels, default_state, sequencing, mating, tbd; current.maker; A's part; B's part with finding L5R2-F04 | none | A and B netlists, gen_sch_b.py's land table; QRP Labs' product page; ASSEMBLY.md |
| IF-AE-DOCK | E5's end gains part, ref and src; grounding (GND-002); pin1_vsys_dock's round-2 sentence (the branch 1.3208 A) | none | the file's own E5 statements; L4-E11 18b; record l8gnd 2d |
| IF-E-FANS | ends (the fan named, the four-pin draft), harness, levels, current, power, sequencing, default_state, mating, tbd, findings restated | | Sanyo Denki's page and record l7pwr (D-18); L4-E11 18a to 18c |
| IF-B-FANS | device named, harness, levels, current, power, mating, tbd, findings restated (E11-40 PROVISIONAL) | | Sanyo Denki's page, l7pwr; L4-E11 18d |
| IF-EXT-ETH | grounding (GND-002 changes 2 and 3), a tbd (l8gnd F01), findings | | record l8gnd 2a, 2c |
| IF-EXT-DC | grounding (the one bond on A; no chassis net on E) | | record l8gnd 2d |
| IF-A-CHASSIS | a new contract, board to case: H1 and R229 on board A to the plate's stud F, every field | | record l8gnd 2b, 2e, 2f; ASSEMBLY.md's connector plate row |
| power_line_states | SLOT_EN1..3 restated (the keeper's hold and cable-out state); U22_RUN_12V_FAN added; FAN1_SW_FAN2_SW and VSYS_DOCK extended | | record l8gnd 3b, 3d, 3g; L4-E11 18a, 18b |
| HW-FW-CONTRACT.md | FW-C02, V-C02 (l8gnd 3f, 3h); FW-C01 step 6; FW-C14's start-up read; section 9's open item; FW-E07; FW-E11 (and R228 for R221); two rows of section 4.1; the version paragraph; the change record | | record l8gnd 3f, 3h; L4-E11 18a to 18c; L4-E11's 787e7b15 rename |

## 2. Inputs

Section 0 of the output pins every file: the two targets (the tree's and the base's at `a1f696de`), the two copied inputs (each body
hashed against its header), the netlists and intent files of boards A to D, `gen_sch_b.py` and `gen_sch_d.py`, ASSEMBLY.md,
PROCUREMENT.md, record l7pwr's page and the Sanyo Denki transcription, L4-E11's record (in this tree), the Wurth header, socket and
cable sheets, the JST VH catalogue, Bourns' MF-MSMF sheet, the LTC2954 and RA30H1317M1 sheets, QRP Labs' product page and hc5's
field checker.

## 3. Method

- **No loss.** Each of the eight first-twelve contracts was replaced as a block; `apply_l5r2.py` refuses if any string or number of
  the old block is not found inside the new one, and the reader proves it again (section 2 of the output: 303 leaves, all found).
  Where an old text had gone stale (IF-BC-PANEL's "F1 holds 2.0 A", IF-A-PA's "no board carries a flange sensor", the cable's "no
  datasheet is held") it is kept and marked "as first written", followed by the current fact.
- **Marks.** MAKER, NETLIST, VERIFIED, INFERRED, MODELED, RULE, TEST, NOT READ; DRAFTED for a release-guarded draft no generator
  carries; PROVISIONAL for an entry resting on an open condition, its trigger named. A figure no document states is TBD with its
  effect and an owner (section 4 of the output), never a guess.
- **The pins maps** are not touched; the test holds every contract's map against the committed netlists. L4-E11's
  `apply_pcb_interfaces_dock.py` still checks OK on the patched file.
- **The first round's reader** (`../l5pwr/`) now reads its three targets at `1e18a1ca`, the commit that carries that pass, so a later
  round's restatement in place does not make a finished record refuse; `test_l5pwr.py`'s three predicates that pinned the tree's
  state were re-stated on properties.

## 4. The table

<!-- l5r2-table:begin -->
| id | contract | field | text written (excerpt, verbatim in the target) | source (file; where) | mark | invalidation trigger | criterion (5.x) |
|---|---|---|---|---|---|---|---|
| R2-01 | IF-BC-PANEL | ends.b part | Wurth WR-BHD 61202621621 (session pick HC6-SC-7, JLCPCB C17586777; 3 A per contact at 25 C, -40 to +105 C, 30 mating cycles | PROCUREMENT.md; wurth-wr-bhd-box-header-61202621621.pdf; pcb-b-compute.net; PROCUREMENT.md 5 (HC6-SC-7); the header's sheet; B netlist | MAKER | a different pick under HC6-SC-7's reversal (a failed land comparison) | 5.2 |
| R2-02 | IF-BC-PANEL | ends.c part | XFCN BH254VS-26P (session pick HC6-SC-7, C48687640, no maker sheet read | PROCUREMENT.md; pcb-c-display.net; PROCUREMENT.md 5; C netlist | NETLIST; the part's sheet NOT READ | none: a TBD (the sheet), owner Layer 6 | 5.2 |
| R2-03 | IF-BC-PANEL | harness.rating (moved from cable) | sockets Wurth WR-BHD 61202623021 (1 A per contact max, -40 to +105 C, 30 mating cycles) on flat cable WR-CAB 63912615521CAB (1.27 mm, 28 AWG, 1 A per conductor max, -25 to +105 C, 300 V RMS) | wurth-wr-bhd-idc-socket-61202623021.pdf; wurth-wr-cab-ribbon-63912615521cab.pdf; PROCUREMENT.md; the socket's and the cable's sheets; HC6-SC-7 | MAKER | none | 5.9 |
| R2-04 | IF-BC-PANEL | current.per_conductor | F1 holds 1.10 A (0.55 A a conductor) and trips at 2.20 A at 23 C (Bourns MF-MSMF sheet, every MF-MSMF110 variant) | bourns-mf-msmf-pptc.pdf; pcb-b-compute.net; the MF-MSMF table; B netlist's F1 | MAKER, INFERRED (the per-conductor split); a TBD for the 2.0 to 2.2 A band | none: a TBD (the cable's capability above 1 A), owner Layer 6 | 5.5 |
| R2-05 | IF-BC-PANEL | protection (a stale statement corrected, kept) | since b76c18cb F1 IS the MF-MSMF110 (B19 netlist: '1.1A hold 1812 (Bourns MF-MSMF110-2)') | pcb-b-compute.net; B netlist's F1 | NETLIST | none | 5.13 |
| R2-06 | IF-BC-PANEL | cable_out_states.SLOT_EN1..3 | held high at least 2.547 V, held low at most 0.266 V, the worst cases of l8gnd 3b | l8gnd-sections-2-3-226e9143.md; l8gnd 3b | INFERRED (record l8gnd's arithmetic on MAKER rows); DRAFTED; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.7 |
| R2-07 | IF-BC-PANEL | slot_power_semantics | keepers U43 (SN74LVC08A, one gate a line) with R230 to R232 (4.7 k) on board A keep each line at its last driven level | l8gnd-sections-2-3-226e9143.md; l8gnd 3a, 3g | NETLIST (the draft's text); DRAFTED; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.6 |
| R2-08 | IF-AB-RIBBON | ends.a part | IDC 2x13, top side: Wurth WR-BHD 61202621621 (session pick HC6-SC-7, JLCPCB C17586777 | PROCUREMENT.md; pcb-a-power.net; HC6-SC-7; A netlist | MAKER | as R2-01 | 5.2 |
| R2-09 | IF-AB-RIBBON | hot_plug | with the hold applied (record l8gnd, DRAFTED) it no longer drops SLOT_EN | l8gnd-sections-2-3-226e9143.md; l8gnd 3g | DRAFTED; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.7 |
| R2-10 | IF-AB-WALL | ends.a part | IDC 2x5 vertical box header: Wurth WR-BHD 61201021621 (session pick HC6-SC-7, JLCPCB C4355000 | PROCUREMENT.md; pcb-a-power.net; HC6-SC-7; A netlist | MAKER | as R2-01 | 5.2 |
| R2-11 | IF-AB-WALL | current | VBUS_WALL does not cross this ribbon (it leaves board A on J_USBW behind the eFuse U32, 0.9142 A | ASSEMBLY.md; ASSEMBLY.md section 4, the wall USB host row | VERIFIED | none | 5.5 |
| R2-12 | IF-AB-WALL | hot_plug (a session choice) | not hot-pluggable (the session's choice in record l5r2 | this record, section 8 | RULE (SESSION) | an interlock that makes live mating safe | 5.10 |
| R2-13 | IF-AD-HARNESS | ends parts | J_MEZZ1 IDC 2x8 box header Wurth WR-BHD 61201621621 (session pick HC6-SC-7, | PROCUREMENT.md; pcb-a-power.net; pcb-d-aprs.net; HC6-SC-7; A and D netlists | MAKER, NETLIST | as R2-01 | 5.2 |
| R2-14 | IF-AD-HARNESS | current.power_lead.contact | the fitted lead is 18 AWG on the standard B2P-VH, a combination the catalogue does not rate | jst-vh-catalogue.pdf; ASSEMBLY.md; JST VH catalogue p.1; ASSEMBLY.md's mezzanine 5 V row | MAKER (INCONCLUSIVE for the fitted combination) | none: a TBD, owner Layer 6 | 5.5 |
| R2-15 | IF-AD-HARNESS | current.signals | board D's loads on it sum 0.0654 A (D intent: U16 0.06, U19 and U20 0.002 each, U22 0.0002, R92 0.0012) | pcb-d-aprs-intent.json; pcb-a-power-intent.json; D's and A's intent files | NETLIST (the intents' declarations) | none | 5.5 |
| R2-16 | IF-AD-HARNESS | levels | +5V_D8 from U41 at 4.872 to 5.133 V behind U23 (A intent, stream s99a), board D's codec 4.44 to 4.48 V at the 1.0 A typical | pcb-a-power-intent.json; A's intent, +5V_D8 and +5V_D8IN | INFERRED (stream s99a) | none (S-116 open, a TBD) | 5.4 |
| R2-17 | IF-AC-MAINSW | ends parts | JST-XH B2B-XH-A 1x2 (C158012; 3 A per contact with AWG 22, JST XH catalogue) (A netlist) | pcb-a-power.net; pcb-c-display.net; A and C netlists | NETLIST | none | 5.2 |
| R2-18 | IF-AC-MAINSW | levels | open-circuit 1 to 2 V at -1 uA, falling threshold 0.6 to 1 V, pin range -1 to 26.4 V (Analog Devices 2954fb, p.3, MAKER) | ltc2954.pdf; 2954fb p.3 | MAKER | none | 5.4 |
| R2-19 | IF-AC-MAINSW | current | -3 to -15 uA at 0.6 V and -1 to -12 uA at 1 V (2954fb p.3, | ltc2954.pdf; 2954fb p.3 | MAKER | none | 5.5 |
| R2-20 | IF-AC-MAINSW | sequencing (moved from note) | a tap while running raises PI_SHDN_REQ (FW-A10, FW-A12) | HW-FW-CONTRACT.md FW-A10, FW-A12 | VERIFIED (the contract's own rows) | none | 5.6 |
| R2-21 | IF-AE-RF | ends.a part | Radiall SMP-MAX slide-on receptacles R222M00720 (land meshsat:Radiall_SMPMAX_R222M00720) | pcb-a-power.net; A netlist | NETLIST | none | 5.2 |
| R2-22 | IF-AE-RF | ends.e part | holding eleven Radiall R222M80500 right-angle SMP-MAX plugs | ASSEMBLY.md; ASSEMBLY.md section 4, the RF jumpers row | VERIFIED | none | 5.2 |
| R2-23 | IF-AE-RF | harness | RG-316 jumpers, each cut to its route plus 20 mm, 252 to 432 mm, bend radius 12.5 mm | ASSEMBLY.md; ASSEMBLY.md section 4, the RF jumpers row | VERIFIED | the jumper plug's pick (M17g, M17x) | 5.9 |
| R2-24 | IF-A-PA | ends.d part | J_VGG JST-PH B2B-PH-K 1x2 (C131337); J_PAIN U.FL Hirose U.FL-R-SMT-1 (C88373); J_PAOUT SMA Amphenol 132134 vertical (C3174425) | pcb-d-aprs.net; D netlist | NETLIST | none | 5.2 |
| R2-25 | IF-A-PA | levels (the drive) | 50 mW at J_PAIN (gen_sch_d.py), against the module's Pin absolute 100 mW | gen_sch_d.py; ra30h1317m1-datasheet.pdf; gen_sch_d.py's pad; the module's sheet | MAKER, NETLIST | none | 5.4 |
| R2-26 | IF-A-PA | current.contact | the 6.0 A peak is 60 percent of it | jst-vh-catalogue.pdf; pcb-a-power-intent.json; the VH catalogue; A's intent | MAKER, INFERRED | F-PR-02 (the drain current characterised) | 5.5 |
| R2-27 | IF-LID-HF | ends.b part (finding L5R2-F04) | gen_sch_b.py's land key PH1x4 is Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | gen_sch_b.py; pcb-b-compute.net; gen_sch_b.py's footprint table; B netlist | NETLIST | board B's land changed to a JST-PH part, or the contract and ASSEMBLY.md to the pin header | 5.10, 5.13 |
| R2-28 | IF-LID-HF | current.maker | receive 80 mA, transmit around 0.7 A for 5 W with a 12 V supply | qmx-product-page-2026-09-27.txt; QRP Labs' product page | MAKER (approximate) | QRP Labs' manual's figure | 5.5 |
| R2-29 | IF-LID-HF | levels (RF) | the QMX's 3 to 5 W output at a 12 V supply | qmx-product-page-2026-09-27.txt; QRP Labs' product page | MAKER | none | 5.4 |
| R2-30 | IF-E-FANS | ends.device | two Sanyo Denki 9WL0612P4H001 (San Ace 60W, 60 x 60 x 25, IP68, 12 V, 10.8 to 13.2 V, 0.17 A, 2.04 W, -20 to +70 | sanyo-denki-splash-proof-fan-pages-2026-10-03.md; L7-FANS-AND-TH1.md; the maker's page as transcribed; l7pwr 2d | MAKER | a fan printing a covering range (D-18's reversal) | 5.2 |
| R2-31 | IF-E-FANS | levels | +12V_FAN 12.001 V (11.512 to 12.431 V at FB's limits) from U22 on VSYS_E, inside the fans' 10.8 to 13.2 V by 0.71 V below and 0.77 V above | l4e11-section-18-b929d8be.md; L4-E11 18a | MODELED; DRAFTED; PROVISIONAL | L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw | 5.4 |
| R2-32 | IF-E-FANS | current | at U22's input 0.5208 A for both at full speed at VSYS_E's floor (4.08 W over 0.85 at 9.508 V plus 16 mA), the dock branch 1.3208 A with U12, 89.8 percent of U42's least limit 1.4713 A | l4e11-section-18-b929d8be.md; L4-E11 18b | MODELED (0.85 an ASSUMPTION); DRAFTED; PROVISIONAL | L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw; the start current read (E11-35, R-179) | 5.5 |
| R2-33 | IF-E-FANS | power | RUN on at 8.33 V and off at 6.89 V of VSYS_E | l4e11-section-18-b929d8be.md; L4-E11 18a | INFERRED (the comparator's limits); DRAFTED; PROVISIONAL | L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw | 5.6 |
| R2-34 | IF-E-FANS | sequencing | never while U12 or U22 starts (FW-E11, E11-39, R-188; L4-E11 18c) | l4e11-section-18-b929d8be.md; L4-E11 18c | RULE (L4-E11, SESSION); PROVISIONAL | L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw | 5.6, 5.11 |
| R2-35 | IF-B-FANS | ends.device | three Sanyo Denki 9WPA0412P6G001 (San Ace 40W, 40 x 40 x 20, IP68, 12 V, 10.8 to 13.2 V, 0.17 A, 2.0 W | sanyo-denki-splash-proof-fan-pages-2026-10-03.md; L7-FANS-AND-TH1.md; the maker's page; l7pwr 2d | MAKER | as R2-30 | 5.2 |
| R2-36 | IF-B-FANS | levels (E11-40) | the slot's +5V_Sn at 5.1 V on pin 1 (B netlist; L4-E11 18d), OUTSIDE the fans' 10.8 to 13.2 V | l4e11-section-18-b929d8be.md; L4-E11 18d | NETLIST; PROVISIONAL (E11-40 open) | board B's owner drawing a regulated 12.0 V feed (E11-40) | 5.4 |
| R2-37 | IF-B-FANS | current | about 0.436 A each at full speed (record l7pwr, F-L7-02, INFERRED) | l4e11-section-18-b929d8be.md; L4-E11 18d | INFERRED; PROVISIONAL | E11-40's feed drawn (a step-up's efficiency or a 12 V feed changes the figure) | 5.5 |
| R2-38 | IF-AE-DOCK | pin1_vsys_dock (round 2) | is declared 1.3208 A (U12 0.8 A, U22 0.5208 A at the floor with both fans at full speed), 89.8 percent of U42's least limit 1.4713 A with 0.1504 A in hand | l4e11-section-18-b929d8be.md; L4-E11 18b | MODELED; DRAFTED; PROVISIONAL | L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw | 5.5 |
| R2-39 | IF-AE-DOCK | ends.e5 part | the dock block E5: twelve plated contact targets, four pack targets, a pre-charge target, eight VIN_RAW targets | pcb_interfaces.yaml; this file's boards.e5 and IF-AE-DOCK not_judged | VERIFIED (the file's own statements) | none | 5.2 |
| R2-40 | power_line_states | SLOT_EN1..3 hold | held HIGH at least 2.547 V (the pad's pull-down at 50 k), held LOW at most 0.266 V (at 80 k) | l8gnd-sections-2-3-226e9143.md; l8gnd 3b, 3d | INFERRED; DRAFTED; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.6, 5.7 |
| R2-41 | power_line_states | U22_RUN_12V_FAN | on at 8.33 V of VSYS_E (7.98 to 8.67 V) and off at 6.89 V (6.55 to 7.23 V) | l4e11-section-18-b929d8be.md; L4-E11 18a | INFERRED; DRAFTED; PROVISIONAL | L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw | 5.7 |
| R2-42 | IF-EXT-ETH | grounding | C33 to CHASSIS and J_ETH SH to CHASSIS, Microchip DS00004151A p.10 | l8gnd-sections-2-3-226e9143.md; l8gnd 2a, 2c | MAKER (the clause); DRAFTED; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.12 |
| R2-43 | IF-EXT-ETH | tbd (l8gnd F01) | the PX0833's plastic body, the PX0888 backshell | l8gnd-sections-2-3-226e9143.md; l8gnd 2c | VERIFIED (record l8gnd's reading of the held sheet) | the wall RJ45's pick | 5.12 |
| R2-44 | IF-A-CHASSIS | ends.a part | M4 bonding pad, land meshsat:ChassisLug_M4_CHASSIS (plated hole 4.3, 12.0 ring both sides) | l8gnd-sections-2-3-226e9143.md; l8gnd 2b | NETLIST (the draft's text); DRAFTED; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.2, 5.12 |
| R2-45 | FW-C02 | the keeper | SLOT_EN1..3 held at their last driven level across a panel reset by board A's keepers U43 (SN74LVC08A) with R230 to R232 | l8gnd-sections-2-3-226e9143.md; l8gnd 3f | DRAFTED; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.11 |
| R2-46 | V-C02 | extended | each SLOT_EN read on a scope at or above 2.5 V throughout (the held high) | l8gnd-sections-2-3-226e9143.md; l8gnd 3h | TEST; PROVISIONAL | record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record | 5.11 |
| R2-47 | FW-E11 | U42's ILIM resistor | R228 11.0 kOhm, renamed from R221 by L4-E11 at `787e7b15` | L4E11-SOURCE-ONLY-AND-ENTRY.md; L4-E11's record (in this tree since 787e7b15) | VERIFIED | none | 5.13 |
| R2-48 | FW-E11 | the start's room | leaves 0.1504 A of room, 1.21 W at the rail for the other fan's start (18b) | l4e11-section-18-b929d8be.md; L4-E11 18b | MODELED; DRAFTED; PROVISIONAL | L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw; the start current read (E11-35) | 5.11 |
<!-- l5r2-table:end -->

## 5. Readings before and after

| Check | Before (`a1f696de`) | After (this round) |
|---|---|---|
| `check_contracts.py` on the committed netlists (VERDICT_DIR in the session's scratchpad) | PASS of 99 (99 pass; RF-002's walk 15 PASS, 11 UNDECIDED) | PASS of 99, stdout identical line for line |
| `check_contract_fields.py --all` (hc5) | 18 of 18 new contracts pass; of the first twelve, IF-AB-POWER, IF-PE-PACK, IF-EXT-USB carry every field, IF-AE-DOCK carries every field with E5's end lacking part, src and ref, and eight lack fields (the list of section 1 of the output) | 18 of 18 new contracts pass; all thirteen others (IF-A-CHASSIS added) "carries every field" with no end remark |
| `interfaces.py` judge (INT-001 on the sheet, in-process) | 0 fails | 0 fails |
| L4-E11's `apply_pcb_interfaces_dock.py --check` on a copy | CHECK OK, 5 edits | CHECK OK, 5 edits |

**Why check_contracts.py did not move:** it reads the committed netlists and its own ALIAS table, not `pcb_interfaces.yaml`; this
round edits no netlist, no generator and not the checker, and keeps every `pins` map as the netlists'.

## 6. The Layer 5 criteria this round moves (Layer 5's reading; `LAYER-STATUS.md` is the integrator's page)

| Criterion | After this round |
|---|---|
| 5.2 every interface owned at both ends with its connector | PARTLY, further: all 31 contracts carry both ends with a part on every board end and every pass-2 field; not claimed MET: no census shows every interface of the netlists has a contract, and the generators still write no MPN (EQ-21) |
| 5.4 electrical levels per interface | PARTLY, further: the eight contracts, the fans and the chassis bond; the kit I2C's segments still owed (SC-59) |
| 5.5 power capacity with margin | PARTLY, further: PANEL_5V per conductor (with F1's trip band a TBD), the mezzanine's +3V3, the PA lead at 60 percent, the MAIN lead's microamps, the fans' branch 1.3208 A at 89.8 percent (DRAFTED) |
| 5.6 sequencing | PARTLY: the SLOT_EN hold DRAFTED (record l8gnd) and written PROVISIONAL into the contracts and FW-C02; H2's item stays open until the keeper is in a generator |
| 5.7 reset, default and cable-out states | PARTLY, further: default_state for the eight, SLOT_EN's cable-out with the keeper, U22's RUN line |
| 5.9 harnesses | PARTLY, further: harness fields from ASSEMBLY.md and HC6-SC-7; found L5R2-F04, J_AB2's length TBD |
| 5.10 mechanical mating | OPEN, further: mating fields everywhere; W4-F17, J_QMX's land and the fans' lead terminations keep it open |
| 5.11 firmware obligations | PARTLY, further: FW-C02, FW-C01, FW-C14, V-C02, FW-E07, FW-E11 (DRAFTED, PROVISIONAL) |
| 5.12 GND-002 | OPEN: the four changes DRAFTED by record l8gnd, carried PROVISIONAL (IF-A-CHASSIS, IF-EXT-ETH, IF-EXT-DC, IF-AE-DOCK) |
| 5.13 consistency with the tree | PARTLY, further: stale texts corrected with their history kept, FW-E11's R228; check_contracts PASS 99 of 99 unchanged; interfaces.py's readings owe a re-take |

## 7. The PROVISIONAL entries (section 5 of the output, 17)

- **Record l8gnd's release** (R2-06, R2-07, R2-09, R2-40, R2-42, R2-44, R2-45, R2-46): the SLOT_EN keeper (U43, R230 to R232; held
  high at least 2.547 V, held low at most 0.266 V; not across a loss of the panel's supply nor PI_KILL), GND-002's R229 and H1 on A
  and C33 and J_ETH SH to CHASSIS on B. Trigger: the release, or a change of those parts.
- **L4-E11 section 18's release** (R2-31 to R2-34, R2-38, R2-41, R2-48): +12V_FAN from U22 (12.001 V, RUN 8.33 / 6.89 V), the branch
  1.3208 A, the stagger never while U12 or U22 starts. Trigger: the release, a change of U22's network or the fans' declared draw,
  the fans' start current read (E11-35, R-179).
- **E11-40** (R2-36, R2-37): the coolers on +5V_Sn at 5.1 V, outside their 10.8 to 13.2 V. Trigger: board B's owner drawing a
  regulated 12.0 V feed.

## 8. The TBD entries and their owners (section 4 of the output, 44 entries over the touched contracts)

By owner: **Layer 6** (the ribbon's capability above 1 A, the XFCN header's sheet, the 18 AWG VH leads, SMP-MAX power handling, a DC
antenna feed, the QMX's current, the fans' PWM level, R229's code, the magnetics' surge rating, D-06's ratings, A-3(c)); **Layer 7**
(J_AB2's and the MAIN lead's lengths, W4-F17 with board A, the SMA plug M17g/M17x, the fans' lead terminations, the strap and lugs,
the sealed RJ45 and its shield path, the DC receptacle); **Layer 8** (board A: the SLOT_EN keeper's release, SEG-A's buffer, the
twelfth RF site, the +3V3 branch to board D; board B: E11-40, J_QMX's land, the MDI side; boards A and D: S-116; board E: PV_RTN, the
fans' rail with the Layer 4 coordinator); **Layer 9** (the wall link's speed, the PA's drain current, the fans' start current, the
bond resistance); **the firmware owner** (the band lock, the PoE class).

## 9. Findings for other layers and the integrator

| ID | For | Finding | Next action |
|---|---|---|---|
| L5R2-F01 | the integrator | This round changes `pcb_interfaces.yaml` (pinned as `ifaces` by `l4e9_power_path.py`) and `HW-FW-CONTRACT.md` (pinned as `hwfw` by `l4e9_power_path.py` and `l4e11_power.py`): both readers refuse "is not the pinned file" until re-pinned, and `pcb_interfaces.yaml` is a CONFIG_INPUT of `interfaces.py` (its readings owe a re-take). L4-E5's reader is unaffected (it reads the contract at `2c240414` when the tree's differs) | re-pin at the merge, as set 28's preparation did (its `apply_set28_repins.py`), and re-take interfaces.py |
| L5R2-F02 | the Layer 4 coordinator, Layer 8 | L4-E11 section 18 (`b929d8be`) and record l8gnd (`226e9143`) are not in this branch; the contracts carry them PROVISIONAL, from copies in `inputs/` | on their merge and release, lift the marks entry by entry (sections 7 and 3 of the output name them) |
| L5R2-F03 | Layer 6 | PANEL_5V on two ribbon conductors: F1 (MF-MSMF110-2) holds 1.10 A and trips at 2.20 A at 23 C, so a fault between 2.0 and 2.2 A may put up to 1.1 A on each conductor, 10 percent over the Wurth cable's and socket's 1 A maximum, until F1 trips | Wurth's statement of the short-time capability, or F1 one step lower |
| L5R2-F04 | Layer 8 board B, ASSEMBLY.md's owner | J_QMX's land is a 2.54 mm pin header (`gen_sch_b.py`'s key PH1x4), while IF-LID-HF and ASSEMBLY.md say PH 1x4: HF-F04's class, on J_QMX (IF-CAM already records it for J_CAM) | a JST-PH land on board B, or the lead made to the pin header and the texts corrected |
| L5R2-F05 | Layer 8 board A | board A's +3V3 reaches board D over one ribbon conductor (1 A) with no branch limiter | a limiter or a second conductor, or the converter's limit shown under the conductor's rating |
| L5R2-F06 | Layer 6, Layer 7 | the 18 AWG leads on standard VH headers (J_MEZZ_PWR1, J_HF, J_54V) have no stated JST rating | JST's statement, or 16 AWG leads (10 A stated) |
| L5R2-F07 | Layer 6 | the Sanyo Denki fans' behaviour with the PWM input released and their lead termination are NOT READ; with +12V_FAN up whenever VSYS_E is over 8.33 V, that behaviour is the fans' state at every reset | the maker's manual M0011876C (a request) or the bench |
| L5R2-F08 | the integrator (the registry's session choices) | three hot-plug rules taken here as SESSION by SC-HF-04's reasoning: IF-AB-WALL, IF-AD-HARNESS (kit off) and IF-AC-MAINSW (unplugged at A only with the kit off) | enter them beside SC-61, or leave them as this record's |

## 10. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

1. **Move, not copy, with a no-loss proof.** The older keys' content is moved into the pass-2 fields; nothing of an old block is
   dropped; a stale statement is kept and marked "as first written". *Reverse:* none needed; the old blocks are in git.
2. **IF-A-CHASSIS as its own contract** (board to case) rather than a field of IF-AE-DOCK, because the bond is an interface with two
   owned ends (H1 on board A, the stud on the plate) and a part between them (the strap); IF-AE-DOCK, IF-EXT-DC and IF-EXT-ETH point
   to it. *Reverse:* fold it into IF-AE-DOCK if the bond moves onto the dock.
3. **Three hot-plug rules** (finding L5R2-F08). *Reverse:* an interlock that makes live mating safe.
4. **E's clamp bar and E5 as ends without a designator** (`ref: "none: ..."`), because neither has a schematic; the part and the
   generator are named. *Reverse:* a schematic for either.
5. **The first round's reader reads its targets at its own commit.** *Reverse:* none needed.

## 11. What this record does not claim

Nothing is verified on hardware; every DRAFTED figure is a draft's and every PROVISIONAL entry stands on an open row. The criteria
table is Layer 5's reading. Software tests establish this record's own behaviour only.

## 12. Reproduce

`python3 v2/docs/records/l5r2/l5r2_interfaces.py` (needs pdftotext and PyYAML; a few seconds); the committed output is regenerated
only through `_bin/regen_out.py`. `env -C v2/ecad/tools/tests python3 run.py test_l5r2` holds the predicates. `apply_l5r2.py
<target> --check` on the tree refuses "already applied"; on the files at `a1f696de` it checks OK.
