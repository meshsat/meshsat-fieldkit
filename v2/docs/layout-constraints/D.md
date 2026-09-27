# Board D (APRS): layout constraints

**Bound to the H2 line (after H2, 27 September 2026).** Candidate re-read at `ef144760`: phase D12, netlist
`v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net` sha256/16 `76700a687eb6187f` (round 8 at `76235aad`, set 5 at `b7f96784`),
intent `pcb-d-aprs-intent.json` `443fd745879d3022`; the committed board file `929bf82d2bf6eed4` is D12. Section 2's
table is regenerated from `calc/rail_widths.py` on that intent: the `+5V_TX` rail the paragraph below announced is
in it (marked **H2**), the other rails read the same. Board D is not at layout entry: **8 reasons at H2**
(`CURRENT-EVIDENCE.md`): PWR-001 INCONCLUSIVE (RLY_K, S-76), SI-001 INCONCLUSIVE, RF-002 FAIL (EQ-25), decision 31's
protection review, FEA-002, FEA-004, FEA-006, FEA-007 (its desk item W4-F17, board A's J_AB2 in board D's rectangle,
alone; no mock-up check holds board D). Known changes of the H2 line: round 8 (`76235aad`: the transmit chain powered
only while its EMCON gates are in range, the PA flange temperature read) and set 5 (`b7f96784`: every supply PWR-001
refused declared, the transmit supply behind U21). Every other line below is the reading at `e3aedb25`, not re-read against the H2 netlist; where it and a record disagree, the record governs (README).

As first written: a view over the records at `main` `e3aedb25` (conventions and shared rules: [README.md](README.md)),
candidate then netlist `f13d8b70099ab03e`, intent `59591c54eb29ab64`, 15 blocker lines.
**Round 8** (`fnd/r8int1`, on `main` as `53a98a71` since this sheet was first written) changes board D: it adds a
`+5V_TX` rail (0.37 A typical, 1.15 A peak: 0.08 mm on one outer face, two 0.3 mm barrels) and draws PWR-F15's flange
sensor (a Semitec 103AT-2 NTC on a two-wire lead to `J_FLANGE`, read by U22, a TI ADS1115 at 0x48 on the kit bus;
`POWER-THERMAL.md` PWR-F15 row on that branch). Re-read this sheet on the merge commit's netlist.

## 1. Stackup and layer use: DECIDED, four layers

- **JLC04161H-7628, 1.6 mm, 1 oz outer, 0.0152 mm inner** (`v2/docs/STACKUP-DECISIONS.md` section 3.4): the RF reason,
  a solid ground plane under the SA868 exciter, the PA path and the filter.
- **Layer use:** F sig, **In1 GND**, **In2 a plane** (+5V_D8 and GND pours; D12 carries 6 track segments on In2), B sig.
  The In2-as-plane arm routed 0 hard and 0 unrouted over three rounds (decision 27's D measurement,
  `OWNER-DECISIONS-2026-09-11.md`).
- Two sides assembled (D12 carries 71 SMD footprints on its back); conformally coated.

## 2. Power

| rail | typ / peak A | one outer face, mm | inner, mm | barrels 0.3 / 0.4 / 0.5 mm |
|---|---|---:|---:|---|
| +5V_D8 (from board A over J_PWR1) | 1.00 / 2.00 | 0.30 | 1.80 | 3 / 3 / 2 |
| +5V_SA (the exciter, behind FB1) | 0.35 / 1.10 | 0.07 | 0.42 | 2 / 2 / 2 |
| +5V_TX (**H2**: the transmit supply, round 8 and set 5) | 0.37 / 1.15 | 0.08 | 0.46 | 2 / 2 / 2 |
| +3V3_D8, +3V4_HUB, +3V3 | 0.04 to 0.06 / up to 0.17 | under 0.02 | | 1 / 1 / 1 |

- **+5V_SA's layer transition needs two barrels** (D12's single barrel at (71.4, 74.2) carries 1.10 A of the solved
  mesh against 0.90 A for its wall; `boards/d.json` `_via_sizing_why`; answered on D15 by one parallel barrel).
- **The mezzanine 5 V drop share is 2 points of the codec's 6 percent** (decision 33; PCM2912A VBUS 4.35 V minimum),
  judged by PI-002 on the routed board.
- **FB1** (600 ohm, 2 A) separates the exciter's rail from the board's, with bulk capacitance on both sides; the transmit
  key pulls about an amp through the shared 5 V (`pcb_emc.yaml` board d).

## 3. RF lines and pairs

- **The RF path** (`boards/d.json` external_ports J_PAOUT, read off the netlist): RF_PAOUT, L1, RF_LPF_M, L2, RF_LPF_OUT,
  the T/R relay K1 (pins 5 and 6), RF_ANT, J_ANT. It is 50 ohm single-ended on F.Cu over the In1 plane: the RF class
  0.35 mm reads 48.5 ohm by atlc and 50 ohm is at 0.332 mm (`calc/stack_solves.out`, se-4L); RF-001 passes on D12's
  twelve segments. The low-pass filter's values are flagged for a simulation that has not run (RF-001's coverage note,
  `pcb_rules_coverage.yaml`).
- **Current and voltage on it (INFERRED arithmetic):** at the RA30H1317M1's 30 W into 50 ohm, 0.77 A rms and 54.8 V
  peak; at a 2:1 mismatch about 73 V peak. The 0.35 mm line is rated about 1.1 A at 10 K under decision 35.
- **A gap this sheet names (INFERRED):** ISO-001 selects its high-voltage conductors from the declared rails at or above
  20 V (`spacing.py`) and applies to boards A, B and E only (`pcb_rules.yaml`), so it never sees board D's RF path.
  The RF class clearance, 0.3 mm (project file), is above the coated column's 0.160 mm for that voltage, but the
  coating is masked at the RF bodies (`spacing.py` header), where the bare column asks at least 0.500 mm. **Constraint
  for the next D layout: 0.5 mm from the RF path's copper to any other net at J_ANT, J_PAOUT and K1 where the coating
  is masked.** Whether ISO-001 should read RF nets is a question put to the registry writer with this layer's drafts.
- **USB (hub, codec, bridges):** full speed by their own datasheets, no impedance target (`pcb_interfaces.yaml`
  USB_FULL_SPEED; `boards/b.json` `_pair_inner_layer_why` last sentence); the USB class is 0.3 / 0.2 mm; route coupled
  over the plane.

## 4. Return paths

`return_reach_mm: 3.0` (decision 32). With In2 a plane, the RET-001 misses on the measurement arm were the nets' own
via anti-pads, 0.6 to 1.0 mm of track over each of 15 to 36 vias per net (`OWNER-DECISIONS-2026-09-11.md`, decision 27,
"Measured again"): fewer layer changes per net is the lever, not a plane.

## 5. Decoupling (decision 42)

- **TPA6132A2 (U7): C31 at HPVDD and C32 at VDD become 2.2 uF, X5R or better, both within 5 mm of their pins with a
  minimum-length ground return** (G12; SLOS597B section 9, the only maker in the tree that gives a distance, so it is a
  hard limit). On D12 they sit 18.1 mm and 13.6 mm from their pins.
- **Far side allowed on D** outside every fan box at in-plane distance plus 2.3 mm (JLC04161H-7628); **C15 and C16 come
  out of U7's fan box and C17 out of U5's** (`DECOUPLING.md` sections 7 and 10). C61 and C62 under U15 (WSON-6-1EP) are
  refused.
- G14: classes on every entry (C8 and C9 class L, C17 class B1). 29 bypass entries in the committed intent, none
  classified.

## 6. Placement

1. **The codec's pin field (decision 44):** nine back-side parts of the AUDB region sit inside the TQFP-32's own box and
   wall off U6 pad 20 (its ground pin); decision 44 accepted it for D12 and says "if board D is re-cut for another
   reason, the rectangle move goes in that commit". Round 8 re-cuts D, so the AUDB rectangle moves off U6's pin field in
   the next D placement; it is a floor-class edit to `gen_pcb_d3.py` REGIONS under owner ruling 13 and needs its
   authority named in that commit.
2. **Sensitive analogue nodes** (`pcb_sensitive.yaml` board d): MIC_IN, MIC_SUM, MICAMP_IN_N, VREF, HS1_MIC, HS2_MIC
   each at least 1.0 mm from the exciter's supply and the RF path; the headset microphone lines leave the board.
3. **The transmit inhibit:** U12's AND gate takes `TX_INHIBIT_n` with R2 holding it down (`boards/d.json` safety_lines);
   keep R2 at the harness entry so an open harness reads inhibit.
4. **The PA flange sensor (round 8):** the NTC is bonded to the RA30H1317M1's flange beside a mounting screw on the
   plate; `J_FLANGE` (JST XH) is keyed apart from `J_VGG`'s PH; the flange is the module's RF ground (pin 5). The lead is
   the board-to-device contract IF-A-PA's (`pcb_interfaces.yaml`), and its routing inside the case is `ASSEMBLY.md`'s.
5. **Mount and neighbours:** board D is a mezzanine on four M3 x 6 mm standoffs at board A's mezzanine site (5, +-35)
   and (95, +-35), its underside at Z 22.6, 6.0 mm above board A's top (`ASSEMBLY.md` line 44); board A's `J_AB2`
   header stands under it and is expected to collide on those standoffs, an OPEN finding (`ASSEMBLY.md` lines 9 and
   10), so board D's underside keep-out over `J_AB2` is owed before its placement is frozen. The headset jacks are panel
   jacks on the plate with five-lead pigtails to `J_HS1` and `J_HS2` (`ASSEMBLY.md` line 51). The PA module is on the
   face plate on its thermal pad, not on board D (`ASSEMBLY.md` line 73; `pcb_interfaces.yaml` IF-A-PA).
6. **Test access:** 25 test points; JP1 and JP2 (electret bias per headset). Bring-up: `PCB-BRING-UP.md` board D (+3V3
   at 3.3 V, 0.06 A; +5V_D8 at 5.0 V, 1.00 A; then +3V3_D8 and +3V4_HUB measured).

## 7. Protection placement (decision 31, TRN-001)

| Port | Conductor | Part at the jack (`pcb_board_holds.yaml` board d, fitted_parts) | Constraint |
|---|---|---|---|
| J_HS1 pins 1, 3, 5 | the jack's speaker, microphone and push-to-talk conductors (the speaker swings below ground, the microphone carries up to 5 V of electret bias; decision 31) | D9 PESD5V0S1BA, D10 PESD12VL1BA, D11 PESD5V0S1BA | at the jack, ground return short and on the plane |
| J_HS2 pins 1, 3, 5 | the same | D12 PESD5V0S1BA, D13 PESD12VL1BA, D14 PESD5V0S1BA | the same |
| J_ANT, J_PAOUT | the VHF antenna path | off board: the PolyPhaser GTH-SFF-AL SMA arrestor at the antenna bulkhead | nothing on board D; the bulkhead is `CASE-MARGINS.md` C2 and C4 |

The six parts are the session's substitution for the ruled PESD5V0S2BT (`pcb_board_holds.yaml` board d, why). The hold
gates fabrication release; its review record `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` is owed at layout
entry (`CURRENT-EVIDENCE.md` line 118). +5V_D8 carries D1 SMBJ6.0A (intent clamps).

## 8. Spacing

No declared rail reaches 20 V; ISO-001 is not applicable to D by the registry. The RF path is section 3's gap.

## 9. Thermal

No hot part on board D itself; the RA30H1317M1 bolts to the plate. Its flange during a 60 s key-down from a +50 C plate
reaches 95 to 118 C against the maker's 90 C reliability figure and +100 C case rating on the record's patch figure
(`POWER-THERMAL.md` PWR-F15); the sensor of section 6.4 feeds K2 (+75 C key gate) and C4 (+85 C unkey), both firmware.
**PWR-F16 (round 8, open):** with the panel and bridge hung and a PTT held, a key-down has no hardware time or
temperature limit; the candidates (a comparator on the flange NTC, or a hardware key-down timer, both on board D) touch
the EMCON gate chain and are not decided.

## 10. Analyses that need placed or routed geometry, or hardware

| Stage | What | Needs |
|---|---|---|
| PLACED_BOARD | SCH-002, DEC-001 (G12, the fan-box moves), IMP-002, ANA-001, THM-001, PLC-001, MEC-001 | the next D placement with the AUDB rectangle moved |
| ROUTED_BOARD | RF-001 (the RF path, the LPF simulation), PI-001 to PI-003 (+5V_SA's two barrels), RET-001 to RET-004, IMP-001, PAIR-001, GND-001, STK-001, EMC-001, RTE, VIA, PLN | the routed candidate |
| FABRICATION_RELEASE | decision 31 hold; FEA-002 (RF-002 on the current netlist); FEA-004 (the PA patch's rise in the heat-balance test); FEA-006 | the routed candidate; the owner's purchase for the heat-balance test |
| PROTOTYPE | the flange against a thermocouple through 60 s key-downs at 13.8 V into a dummy load from a +50 C plate (PWR-F15); `TEST-PLAN.md` M6 (self-compatibility), M7 (ESD at the headset jacks); transmit into a dummy load with the hub and codec running (`pcb_emc.yaml` board d, pre_compliance); `PCB-BRING-UP.md` board D | a built kit |
