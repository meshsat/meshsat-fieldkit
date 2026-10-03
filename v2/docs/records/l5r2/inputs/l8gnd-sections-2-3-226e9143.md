<!-- COPIED INPUT (MESHSAT-1357, Layer 5 round 2, record l5r2, 3 October 2026). Source: branch fnd/l8gnd at commit 226e9143, file v2/docs/records/l8gnd/L8-GND002-SLOTEN.md, whose sha256 at that commit is 1e92b0d8f66c2b6c89bf8f9f5ed09616e249294f00c5f393ffc0bc0c8d7a163c. Copied: sections 2 (2a to 2f, GND-002's four changes) and 3 (3a to 3i, the SLOT_EN hold), from section 2's heading to the line before section 4's, verbatim between the two markers below; the body's own sha256 is 60ee25758268bea97c01a852f6d07eebdebd136099643e41b582fd8eb5be3baa (l5r2_interfaces.py recomputes it and refuses a copy that differs). Copied because the commit is not in this branch's history; no git command reads it. -->
<!-- BODY BEGIN -->
## 2. GND-002: the four changes drawn

### 2a. The strategy's points and the clause

GROUNDING-AND-SHIELDS.md's strategy: one ground per board and it is signal ground (point 1); the face plate bonded to board C's
ground at eight points, as built (point 2); the connector plate is the kit's cable-entry reference, every cable shield terminates
on it at the connector (point 3); **the plate and the boards are joined at ONE point, deliberately, through a defined impedance: a
single bonding strap from the connector plate to board A's ground near the dock, plus the 1 nF 2 kV capacitor already on board
B's common node moved from signal ground to that plate node** (point 4); a cable shield is never a signal return (point 5); the
pack has no enclosure to bond and nothing of the case metal may touch its return (point 6).

The clause behind changes 2 and 3 is held: Microchip, KSZ989x/KSZ956x/KSZ9477 Hardware Design Checklist, DS00004151A p.10
(`v2/vendor/cluster/ksz989x-hw-design-checklist.pdf`, sha256 `2a9d80931a0bed4b`), the voltage-mode driver points: "All line-side
transformer center taps should be individually terminated to a common node through 75 Ohm resistors. The common node is then
connected to chassis ground through a 1000 pF, 2 kV capacitor." and "The metal case shield of the RJ45 connector is also tied to
chassis ground." As generated (`gen_sch_b.py` lines 1243 to 1245) R9 and R10 take MCT3 and MCT4 (the H5007NL's line-side centre
taps, pins 18 and 15, Pulse HC500.O pin table) to the common node BOB, C33 (1n 2kV, 1812) returns BOB to **GND**, and J_ETH's
shield tabs (Amphenol RJHSE-5380, "Shield: Stainless Steel with tin dipped tails", `amphenol-rjhse5380-rj45-jack.pdf`) sit on
**GND**: the one mismatch the page records.

### 2b. Board A: changes 1 and 4 (`apply_gen_sch_a_gnd002.py`)

| ref | value and land | nets | basis |
|---|---|---|---|
| H1 | M4 bonding pad, `meshsat:ChassisLug_M4_CHASSIS` (drafted: plated hole 4.3, 12.0 ring both sides, `*.Cu` and `*.Mask`) | pin 1 `CHASSIS` | change 4: the strap's landing. M4 is the plate's own screw size (CASE-MARGINS.md: six M4 x 25 on the connector plate; the stud an M6 class, item F); 4.3 is the fine clearance hole for M4 (the KiCad library's own M4 pad uses it); a 12.0 ring takes an M4 ring lug up to 11 mm across (BOUND: the lug is Layer 7's pick, F07) |
| R229 | `0R 2512 (CHASSIS bond link)`, `RS2512` (R_2512) | pin 1 `CHASSIS`, pin 2 `GND` | change 1: the ONE defined impedance between the plate and the boards, 0 Ohm (SESSION, section 2f); `lcsc_fill.py`'s rule `^0R 2512` on an R_2512 land gives C25469, the part board B's POE_P link R13 carries (to be confirmed on the regenerated BOM, F09) |
| `_intent.node("CHASSIS", 0.0, ...)` | | | the node declared to the intent: joined to GND by R229 alone, so at this board's reference; it carries cable-borne common-mode and discharge current, never a supply or a return |
| `"LUGM4": "meshsat:ChassisLug_M4_CHASSIS"` | | | the land's key in the footprint table, beside RS2512 |
| a SECTIONS entry | "CHASSIS BOND (GND-002): THE CONNECTOR PLATE'S STRAP PAD H1 AND ITS 0 OHM LINK R229 TO GND" | | the two parts on their own schematic block |

The block sits in the dock section, written in front of the LTC2954 comment that opens the main power control block, so that it
reads beside J_DOCK ("near the dock"); its placement beside J_DOCK on the back-wall side is a layout-entry item (F08). Why 0 Ohm:
the strategy asks for ONE bond "through a defined impedance" and names its purpose, a short path for a discharge at the plate
into the boards' ground and a single point for cable-borne common-mode current; a link makes the bond a named component that a
pre-compliance measurement (the page's own list: bond resistance with a four-wire meter, the radiated sweep, the discharge test)
can open or exchange for an RC without a board change, and no measurement in this tree supports a value other than a bond. The
link carries no service current (point 6 keeps the pack's return off the case metal) and a fault current only in the case of a
wall receptacle's shell meeting its own supply inside a plug, where the vehicle fuse F1 clears; the 2512 land is board A's own.
What the strap's other end meets is the plate's stud F (CASE-MARGINS.md: "inside a washer of 12, the ring lug of the one bonding
strap of GROUNDING-AND-SHIELDS.md item 4, and a Nyloc").

### 2c. Board B: changes 2 and 3 (`apply_gen_sch_b_gnd002.py`)

| ref | before | after | basis |
|---|---|---|---|
| C33 | `c("C33", "1n 2kV", "BOB", "GND", "C1812")` | `c("C33", "1n 2kV", "BOB", "CHASSIS", "C1812")` | change 2: DS00004151A p.10, "connected to chassis ground through a 1000 pF, 2 kV capacitor"; the part, value and land are unchanged (C36077 by `lcsc_fill.py`'s `^1n 2kV` rule) |
| J_ETH pin SH | `"SH": "GND"` | `"SH": "CHASSIS"` | change 3: the same page, "The metal case shield of the RJ45 connector is also tied to chassis ground"; the shell is the patch lead's shield, a cable shield by definition (point 5) |
| `_intent.node("CHASSIS", 0.0, ...)` | | added after J_ETH | the cable-shield reference on this board: no part joins it to GND here, by design |

No part is added on board B and no other draft of the tree targets `gen_sch_b.py`, so there is no order to keep. Board B's
CHASSIS has **no DC bond to GND on board B**: it reaches the kit's one bond (R229 on board A) over the patch lead's shield, the
sealed wall RJ45 and the connector plate. That path is the wall RJ45 pick's obligation and it is a finding (F01): the held
Bulgin PX0833 sheet gives "Body Material: Polyester (PET), Plastic Body" and offers the PX0888 "Shielding Backshell available
separately - fits to rear of connector to maintain RJ45 coupler shielding directly to panel", while `ASSEMBLY.md` marks the pick
OPEN. Until a pick carries the shield to the plate, C33 and the shell float and change 2 does nothing; with the shell on GND, as
generated, they would instead put every cable's common-mode current into board B's ground, which is what the clause forbids.

### 2d. What is not drawn, and why

No change on boards C, D, E or P: C's eight rings on GND are the as-built bond of point 2 and the check holds them to it; E and P
carry no chassis net by point 6 and the check holds them to that. No test point on CHASSIS: H1 is a 12 mm plated pad and is its
own probe. No change to the arrestor leads, the stud or the plates: conductors of the case (Layer 7). No `pcb_decisions.yaml`
entry: the registry is the integrator's (F05 drafts S-50's text). No `boards/a.json` or `b.json` edit (F02, F03 draft the lines).

### 2e. The check GND-002's tool reads on the regenerated netlist

`check_gnd002_netlist.py` parses a KiCad netlist (an s-expression reader, no grep) and judges per board:

| board | reads DRAWN (or HOLDS) when | otherwise |
|---|---|---|
| A | net `CHASSIS` carries exactly H1 pin 1 and R229 pin 1; R229 pin 2 is `GND` and its value begins `0R`; H1's land is `meshsat:ChassisLug_M4_CHASSIS`; **R229 is the only part with pins on both CHASSIS and GND** | NOT DRAWN without the net; FAIL with a second bridge, another part on the net, a non-zero link or another land |
| B | net `CHASSIS` carries exactly C33's cold end and J_ETH pin SH; C33's other pin is `BOB`; R9 joins MCT3 to BOB and R10 joins MCT4 to BOB; **no part bridges CHASSIS and GND** | NOT DRAWN without the net; FAIL with a bridge, a capacitor left on GND or a tap not on BOB |
| C | H1 to H8 pin 1 on `GND`; no chassis, shield or earth net | FAIL |
| D, E, P | no chassis, shield or earth net (E: point 6) | FAIL |

On the committed netlists (`l8gnd_drafts.out` section 7, each pinned by sha256) it reads **NOT DRAWN on A and B** (A has no
CHASSIS net; on B C33 returns to GND and J_ETH SH sits on GND), HOLDS on C, D, E and P, and **GND-002 on the kit: NOT DRAWN**,
which is today's true state. On two fixture netlists built inside the script with the drafted changes it reads DRAWN on A and on
B, and the test makes it FAIL on a second bond, on a capacitor left on GND and on a chassis net on E. The reading on the boards
regenerated with the drafts is the box's (section 7).

### 2f. Decisions this record takes (SESSION, under the owner's standing rule of 26 September 2026)

| id | taken | why | reverse by |
|---|---|---|---|
| L8G-D1 | the one bond is a 0 Ohm 2512 link, R229 | GND-002 asks ONE bond through a defined impedance and a discharge path into the boards' ground; a link is a named component the pre-compliance measurements can open or exchange; no measurement supports a filter value | exchanging R229 for an RC or a ferrite once a chamber reading asks for it; removing it leaves the plate bonded only through the antenna leads (the page's finding) |
| L8G-D2 | the strap lands on an M4 pad with a 12.0 ring and a 4.3 hole, H1 | M4 is the plate's screw size and the common bonding-lug size; the ring takes any M4 ring lug up to 11 mm; the lug and strap are Layer 7's (F07) | a different land once the lug is picked (an M3 lug would take the existing `BackerScrew_M3_GND`, 6.0 ring) |
| L8G-D3 | board B's CHASSIS has no DC bond on board B | point 4: a second bond would put every cable's common-mode current through the board between the two | a bond on B only together with removing R229 (the single point moves, it does not multiply) |

## 3. The SLOT_EN hold

### 3a. The circuit (`apply_gen_sch_a_hotr1.py`)

A KEEPER on each of the three lines, on board A beside the slot rails: U43, an SN74LVC08APWR (TSSOP-14, the part board A fits as
U26, C465737), gate n with both inputs on `SLOT_ENn` and its output `SLOT_ENn_K` back onto `SLOT_ENn` through 4.7 k (R230, R231,
R232); gate 4 unused (inputs GND, output NC, as U26 does); C240 100 nF (C14663) on pin 14, declared decision 42 class D. Nothing
else changes: R30, R34 and R38 stay, the ribbons' pin maps stay, the converters' enables stay on the lines.

```
panel C U3 GPIO13..15 ---- J_PANEL ---- board B ---- J_AB1 17..19 ---- SLOT_ENn ----+---- U4/U5/U6 EN (the slot rail)
                                                                                     +---- R30/R34/R38 100 k to GND
                                                                                     +---- U43 gate n, inputs A and B
                                                                                     +---- R23x 4.7 k ---- SLOT_ENn_K (U43 gate n output)
```

Why this form (SESSION): A01 took the hold and left its place open, "board C (the source) or board A (their loads)", "for example
a latch the panel sets and clears". A latch needs a set or clear control the panel can express, and J_AB1 has no free contact (its
26 pins are allocated; AB_SPARE lost its seat on 10 September 2026) and IF-BC-PANEL's 26 are allocated too, so a latch enable
would change both ribbons. A keeper needs no control line: it distinguishes the panel's DRIVE (a 4 mA pad) from the panel's RESET
state (an input with 50 to 80 k to ground) by impedance alone. Board A is the place because board A's +3V3 is the supply that
falls with PI_KILL, which is exactly when the hold must vanish (3d), while a hold on board C would share the panel's own supply
and reset.

### 3b. The arithmetic (from `l8gnd_drafts.out` section 3; each figure with its class)

| figure | value | class | source |
|---|---|---|---|
| the pad's reset state | input, pull-down enabled | MAKER | RP2040 datasheet 2.19.6.3, PADS_BANK0 GPIOx: `PDE` reset 0x1, `PUE` 0x0, `DRIVE` 0x1 (4 mA) |
| the pad's pull-down RPD | 50 to 80 kOhm | MAKER | RP2040 Table 625 |
| the pad's VOH, VOL at IOVDD 3.3 V | at least 2.62 V; at most 0.5 V (IOH or IOL 2, 4, 8 or 12 mA) | MAKER | Table 625 |
| VIH, VIL at 3.3 V | 2.0 V; 0.8 V | MAKER | RP2040 Table 625; SN74LVC08A at 2.7 to 3.6 V, TI SCAS283W |
| U43's VOH, VOL at 100 uA | VCC less 0.2 V; 0.2 V | MAKER | SCAS283W |
| the enables' thresholds | AP64500 VEN_H at most 1.25 V, VEN_L at least 1.03 V (Diodes DS41979); LM5176 VEN(OP) rising at most 1.29 V, VEN(STBY) at least 0.55 V (TI SNVSAI1D) | MAKER | the held sheets |
| the enables' input current at the held level | SOURCED by both parts, bounded at 20 uA and taken the worse way for each level | INFERRED | AP64500: an internal 1.5 uA pull-up source, IEN 1 to 2 uA at 1 V and 5.5 uA typical at 1.5 V (DS41979 Rev 5-2, the Enable section and the table); LM5176: IEN(STBY) 1 to 3 uA at 1.1 V, the hysteresis current 2.15 to 4.25 uA at 1.5 V (SNVSAI1D); no figure at the held levels |
| board A's +3V3 low end | 3.2 V | BOUND | the keeper is judged there |
| R30/R34/R38, R230 to R232 | 100 k; 4.7 k | MAKER / BOUND | `gen_sch_a.py`; this draft |
| **held HIGH, worst**, the pad at 50 k | **2.547 V** (the divider 2.629 V less 20 uA through the line's 4.12 k) | derived | margin 0.547 V over VIH, 1.257 V over the highest ON threshold |
| held HIGH, the pad at 80 k | 2.628 V | derived | the 50 k pad is the worse case for the high |
| **held LOW, worst**, the pad at 80 k | **0.266 V** (the divider 0.181 V plus 20 uA through the line's 4.25 k) | derived | margin 0.534 V under VIL, 0.284 V under the lowest OFF threshold (LM5176 standby 0.55 V) |
| held LOW, the pad at 50 k | 0.258 V | derived | the 80 k pad is the worse case for the low |
| the panel overriding a held output | 0.70 mA; sinking a held high 0.66 mA | derived | under the pad's 4 mA default drive; the panel's own levels (2.62 V, 0.5 V) pass the gate's thresholds with 0.62 V and 0.30 V |

### 3c. Power-up

At the MAIN press board A's +3V3 rises while every SLOT_EN line sits at 0 V through its 100 k and the panel's pad (the panel
is not yet up, or holds the line low by FW-C01). An AND gate with both inputs low outputs low at every supply where its
transistors conduct, so the keeper cannot raise a line as VCC passes through the sheet's unspecified region under 1.65 V: this is
the gate's function, INFERRED (SCAS283W prints nothing under 1.65 V), and `TEST-PLAN` row V-C01 (a scope on every enable from the
MAIN press, no glitch high) is the measurement that would show it. The line-state table of `ARCHITECTURE.md` 4.3 stays true:
SLOT_EN1..3 deasserted at power-up.

### 3d. The states, including the hot stop

| state | the lines | why |
|---|---|---|
| the panel drives a line high or low | follow the panel within U43's propagation; the keeper then holds the new level | 0.70 mA against a 4.7 k, inside the pad's 4 mA |
| a RUN reset, an SWD reset, the ROM bootloader, a brownout of the panel's 3.3 V that resets the RP2040 while IOVDD stays up | **held at their last driven level** (2.55 V or more, 0.27 V or less) | the pad is an input with 50 to 80 k to ground; the keeper's 4.7 k wins. This is A01's hold. The firmware re-adopts the level at boot (3f) |
| a watchdog reset with FW-C02's scope (PADS_BANK0 excluded) | unchanged by the pads; the keeper agrees with the pad | both hold the same level |
| hot stop H1 (FW-C13) | the panel drives each line low after the module's shutdown or 60 s; the keeper follows and holds low through any panel reset during the stop | a driven low overrides the keeper |
| hot stop H2 (FW-C13, FW-C14) | PI_KILL takes KILL low, RAIL_EN falls, +3V3 falls, U43 loses its supply and the hold with it; the lines fall to 0 V through R30, R34, R38; the restart begins with every slot OFF and the panel reads HOT-R1 before raising one | the hold lives on the rail PI_KILL removes |
| the ZEROIZE alarm cut (FW-C04, 3.0 s) | the panel drives the lines low; the keeper follows | as H1 |
| a ribbon pulled with the kit running (forbidden, SC-61) | the lines keep their last level instead of dropping; MAIN still stops the kit through U1 | a change to IF-BC-PANEL and IF-AB-RIBBON's `cable_out_states` (3g) |
| the panel's IOVDD lost (its LDO off, the ribbon's PANEL_5V lost) while board A's +3V3 stays | a held-high line is clamped by the unpowered pad's protection to about a diode above 0 V, under VIL: the keeper flips low and the slots drop, as they do today | the keeper's limit: it holds across a RESET, not across a loss of the panel's supply (BOUND; the pad's clamp current through 4.7 k is at most 0.7 mA) |
| U43 failed with an output stuck at either rail | the panel's drive wins through 4.7 k: no failure of U43 can raise a slot the panel holds low or hold one it drives low | 0.70 mA against 4 mA |
| a panel that hangs with the slots up while HOT-R1 reads H2 | unchanged from today: the watchdog restarts the panel, which re-adopts the held state and then acts on the line (FW-C14) | the stop stays firmware (SC-49); S-58 is the open question on a firmware-free stage |

### 3e. What the hold is not

It is not a protection and it adds none: the pack's own protections, the hot stop's firmware and PI_KILL's hardware path are as
they were. It changes one safety property of the ribbons: with a ribbon out the slots no longer drop (3d), which the contracts
record (3g); the kit is still stopped by MAIN on board A (U1, no ribbon in the path) and SC-61 mates the ribbons with the kit off.

### 3f. Firmware texts drafted (for `HW-FW-CONTRACT.md`, the integrator's file)

- **FW-C02, the hardware column:** "RP2040 watchdog; SLOT_EN1..3 held at their last driven level across a panel reset by board A's
  keepers U43 with R230 to R232 (4.7 k), under R30, R34, R38 (100 k) and the pad pull-downs (the hold of ARCHITECTURE.md 4.3,
  drafted by record l8gnd)". **The firmware column gains:** "At boot, before the GPIO13 to 15 pads are made outputs, read each as an
  input (the pull-down may stay on: a held high reads at least 2.55 V) and drive it at the level read, so a reset never glitches a
  running slot; then FW-C01's order applies to every slot read low. A wipe pending or ZEROIZE_SW closed at boot drives all three
  low first (D-03). The watchdog scope rule stays." **The status column:** "FIRMWARE; the hold DRAFTED (record l8gnd), not applied".
- **FW-C01, step 6:** "SLOT_EN1..3 one at a time, each after the keeper's level has been read and adopted (FW-C02)".
- **FW-C14, the start-up read:** add "a slot found held up at boot is acted on by the same rules once the line's state is known:
  held low, PI_KILL; at 5 Hz, H1's shutdown of that slot".
- **Section 9, open items:** replace "The SLOT_EN hold across a panel reset (FW-C02) is not drawn; while it is not, a panel reset
  powers off every module." with "The SLOT_EN hold is drafted on board A (record l8gnd, U43 and R230 to R232), not applied; until
  applied a panel reset powers off every module."

### 3g. Contract texts drafted (for `pcb_interfaces.yaml`, the integrator's file)

- **IF-BC-PANEL `slot_power_semantics`:** "the panel is the only path to slot power, by D-03's boot order; SLOT_EN powers up OFF
  (R30, R34, R38 and the pad pull-downs). The hold of ARCHITECTURE.md 4.3 is DRAFTED on board A (record l8gnd): keepers U43 with
  R230 to R232 keep each line at its last driven level while the panel's pad is in its reset state, so a panel reset or in-system
  update no longer drops the running slots; the panel reads each line at boot before driving it. Not applied."
- **IF-BC-PANEL `cable_out_states` SLOT_EN1..3:** "as generated LOW, every compute slot OFF (A R30, R34, R38, 100k to GND); with the
  hold applied the LAST DRIVEN LEVEL, kept by A's U43 while A's +3V3 is up, LOW from a power-up; the ribbons are mated with the kit
  off (SC-61) and MAIN stops the kit without them."
- **IF-AB-RIBBON `cable_out_states`:** the same sentence for SLOT_EN1..3; **`hot_plug`:** "a partly seated ribbon can assert
  PI_KILL; with the hold applied it no longer drops SLOT_EN".

### 3h. Verification rows (drafted for `TEST-PLAN.md` and `HW-FW-CONTRACT.md` section 5)

- V-C01 as it stands covers the keeper's power-up (no glitch high on any enable from the MAIN press).
- **V-C02 extended:** "watchdog reset, RUN reset and SWD reset with three slots running, and the panel's firmware reloaded by SWD:
  no slot rail drops; each SLOT_EN read on a scope at or above 2.5 V throughout (the held high); then a MAIN tap and PI_KILL: every
  rail off, and at the next MAIN every SLOT_EN at 0 V before the panel runs".

### 3i. Decisions this record takes (SESSION)

| id | taken | why | reverse by |
|---|---|---|---|
| L8G-D4 | the hold is a keeper on board A, one SN74LVC08A gate per line with 4.7 k feedback | no free control line for a latch enable on either ribbon; board A's +3V3 is the supply PI_KILL removes; the part is board A's own U26 | a latch with an enable once a ribbon contact is freed; or a hold on board C if the panel's supply is ever made independent of PI_KILL |
| L8G-D5 | 4.7 k | holds 2.55 V against the pad's 50 k and the 100 k (0.55 V over VIH) and is overridden by 0.70 mA (a sixth of the pad's default drive); 10 k would hold 2.15 V at 50 k, only 0.15 V over VIH; 2.2 k would ask 1.5 mA of the pad | another E24 value if a measured RPD or an enable's input current moves the margins |

<!-- BODY END -->
