# Board C (control panel backer): layout constraints

A view over the records at `main` `e3aedb25` (conventions and shared rules: [README.md](README.md)). Candidate: phase
C24, netlist `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net` sha256/16 `2834f0d8c4071d56`, intent
`pcb-c-display-intent.json` `5c8d991e3805016a`; the committed board file `2a273803757c68fb` is the four-layer C24.
Board C is not at layout entry: 10 blocker lines (`CURRENT-EVIDENCE.md` lines 98 to 107), among them FEA-002 (the
hardware EMCON lamp) and FEA-006 (G9, G13, G14). Round 8's board C stream is in its own worktree; re-read this sheet
on the netlist that merge commits.

## 1. Stackup and layer use: DECIDED, six layers

- **JLC06161H-3313, six layers, 1 oz outer, 0.0152 mm inner** (owner decision 27, 25 September 2026; the price is
  quoted in the ordering session before anything is paid). Board C is regenerated on it as its next phase; the board
  file and `boards/c.json` still say four (`v2/docs/STACKUP-DECISIONS.md` section 3.3).
- **Layer use:** F sig, **In1 GND**, In2 routing, In3 routing, **In4 GND**, B sig, "Every signal layer then has a
  plane next to it (In2 against In1, In3 against In4)" (decision 27, option 1). The reason is RET-001 and RET-002:
  C24's back-side nets had only In2, a routing layer, beside them, the worst `USB_PNL_P` 122.4 mm uncovered of 456.5
  and `SCL` 252.9 of 488.5 (`boards/c.json` `_ret002_c_why`).
- In2 and In3 are 0.1088 mm apart; where both carry long parallel runs they couple broadside. Board C has no
  impedance-targeted pair, so this is a routing guideline (cross at right angles where In2 and In3 runs overlap), not
  a hold.
- **Two sides assembled** (C24 carries 135 SMD footprints on its back), so a far-side decoupling seat is allowed under
  decision 42's conditions (section 5).
- C is not conformally coated (`boards/c.json` `conformal_coated: false`).

## 2. Power

| rail | typ / peak A | one outer face, mm | inner, mm | barrels 0.3 / 0.4 / 0.5 mm |
|---|---|---:|---:|---|
| +5V (from board B's PANEL_5V over J_PANEL) | 0.60 / 1.00 | 0.15 | 0.89 | 2 / 2 / 1 |
| +3V3 (TLV75533 LDO U5) | 0.12 / 0.20 | 0.02 | 0.10 | 1 / 1 / 1 |

The project file's PWR and RAIL classes are 0.5 mm wide; both rails are far inside them. Board C's feed is protected
upstream on board B (a 2.0 A hold polyfuse whose copper there is the constraint, `B.md` section 2).

## 3. Pairs

- **USB_PNL (the panel's USB port to the RP2040, full speed, 12 Mb/s):** no impedance target (`pcb_interfaces.yaml`
  USB_FULL_SPEED; the intent's USB class declares no z_diff). Edge rate 4 ns (USB 2.0 full speed TFR/TFF, `boards/c.json`
  signal classes). The class is 0.3 / 0.2 mm. Route it as a coupled pair over a plane (RET-001), not for impedance.
- **QSPI_* to the flash (133 MHz from the RP2040's ROM) and the 12 MHz crystal XIN/XOUT** are the board's fastest
  nets (`boards/c.json` signal classes); keep them short, on a layer adjacent to In1 or In4, and the crystal as the
  RP2040 hardware design guide places it (Y1 ABM8-272-T3 with two 15 pF, 3 pF of stray allowed, `boards/c.json`
  crystals).

## 4. Return paths

- `return_reach_mm: 3.0` (decision 32, the session's: the return-via fixer's own outermost ring). The six-layer stack
  is what answers RET-001 and RET-002 on this board (section 1). RET-004 on C24: 32 vias without a ground via within
  1.5 mm, each a move between two ground planes, which a ground via beside the transition answers (`boards/c.json`
  `_ret004_c_why`).

## 5. Decoupling (decision 42)

- **Generator items owed** (`DECOUPLING.md` section 8.3): G9 (RP2040 ADC_AVDD and USB_VDD, 100 nF each, class D),
  G13 (the DVDD net: one 1 uF at VREG_VOUT pin 45, class L; one 100 nF at each DVDD pin 23 and 50, class D; the
  VREG_IN 1 uF stays, class D; RP2040 guide 2.1.2 and 2.1.3), G14 (classes on every entry).
- **Far side allowed** outside every fan box, at in-plane distance plus 3.7 mm; **C24's C3 and C4 must come out of
  U11's fan box** (`DECOUPLING.md` section 10, T1).
- 19 bypass entries in the committed intent, none classified.

## 6. Placement

1. **The EMCON lamp (SD-EMC-6, CON-021):** board C gets a lamp driven from the `TX_INHIBIT_n` line state with no
   processor in its path (a lamp, a gate and a FET), and the face plate one light-guide hole for it
   (`v2/docs/feasibility/EMCON.md` lines 45 to 50 and 115 to 116; FEA-002's layout-entry stage). Its position on the
   panel is set with the face plate drawing (FEA-002's FABRICATION_RELEASE stage names the hole).
2. **The safety lines** (`boards/c.json` safety_lines): SW_EMCON shorts `TX_INHIBIT_n` to ground with R14 holding it
   up; U9 buffers the toggle into `EMCON_HW`; SW_ZERO shorts `ZEROIZE_SW` with R10 to +3V3, read by the panel
   controller's GPIO22, and U12 (74LVC1G17) copies it onto `ZEROIZE_HW`. `ZEROIZE_SW` never leaves the board; keep each
   pull resistor at its switch's conductor so a broken trace reads the safe state.
3. **Panel geometry:** board C is a 344 x 228 mm ring with a 240 x 176 mm void, hung under the 3 mm aluminium face
   plate (`V2-SPEC.md` lines 9 and 83); it is fixed to the plate by eight M3 screws into self-clinching standoffs
   through its GND rings, and its sixteen LEDs sit under light guides pressed into 2.6 mm holes in the plate
   (`ASSEMBLY.md` lines 39 and 42), so the LED, screw-ring and connector positions are the plate's
   (`panel1450.py`) and not the layout's to move. The monitor body over the CM5 heatsinks is `CASE-MARGINS.md` M1,
   OPEN. Board C's outline and connector positions are frozen for routing after the targeted
   checks of `CASE-MARGINS.md` finding 28, or with the OPEN rows named.
4. **The sounder and the LED rail:** the sounder's FET sits at the sounder, not beside the controller; the LED rail has
   its own bulk at the panel; the analogue inputs carry their own RC (`pcb_emc.yaml` board c, citing appendix 32.77).
5. **Test access:** 48 test points on the committed netlist; TP1 SWCLK, TP2 SWDIO, JP1 BOOTSEL (short while powering
   for the USB bootloader), TP48 BOOT_J; JP2 the PANEL_ID strap. First flash of the panel is over SWD only (IF-BC-PANEL,
   `ARCHITECTURE.md` line 194). Bring-up: `PCB-BRING-UP.md` board C (+5V at 5.0 V, 0.60 A limit; +3V3 measured at U5).

## 7. Protection placement (TRN-001)

| Port (`boards/c.json` external_ports) | What it is | Constraint |
|---|---|---|
| J_PIJ2 | the panel's exposed jack on the face | its protection at the jack, return short and on the plane |
| J_MAINSW | the main switch on the face, which a person touches | the same |

TRN-001 reads PASS on C (awaiting revalidation, `CURRENT-EVIDENCE.md` line 105). `TEST-PLAN.md` M7 applies ESD to
every face control at decision 34's level (8 kV contact, 15 kV air), which is the exposure this board has and the
others do not (`pcb_emc.yaml` board c, pre_compliance).

## 8. Spacing

No rail at or above 20 V on board C; ISO-001 does not apply (`pcb_rules.yaml` boards_affected a, b, e).

## 9. Thermal

No part is named hot on board C: the 3.3 V is a TLV75533 linear regulator at 0.12 A typical from 5 V (0.2 W,
INFERRED arithmetic). THM-001 still applies at PLACED_BOARD and reads no verification today.

## 10. Analyses that need placed or routed geometry, or hardware

| Stage | What | Needs |
|---|---|---|
| PLACED_BOARD | SCH-002, DEC-001 (G9, G13, G14; C3 and C4 out of U11's fan), GND-002, IMP-002, THM-001, PLC-001, MEC-001 | the six-layer regeneration |
| ROUTED_BOARD | RET-001 to RET-004 on the six-layer board, PAIR-001, PI-001 to PI-003, GND-001, STK-001, EMC-001, RTE, VIA, PLN | a routed six-layer C |
| FABRICATION_RELEASE | FEA-002 (RF-002 on the current netlist; the face plate drawing carries the EMCON lamp's light-guide hole); FEA-006 | the routed candidate |
| PROTOTYPE | `TEST-PLAN.md` M7 (ESD to every face control), E6 and E7 (the face's sealing); the IP67-class bench procedure of appendix 32.34 before any rating is claimed; `PCB-BRING-UP.md` board C | a built kit |
