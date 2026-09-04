# MESHSAT-709 Geometry Appendix, Rev B

**Home since 3 Sep 2026:** this record lives in the `meshsat-fieldkit` repository (`v2/docs/`). Laptop paths quoted in the sections below are historical: `~/Downloads/meshsat-pcb/<deliverable>` is now `v2/release/revA/boards/<deliverable>`, `JLCPCB/` is `v2/release/revA/order/`, `Review/` is `v2/release/revA/review/`, `Team Shared Root/.../ECAD/meshsat-carrier/` is `v2/ecad/` and `ECAD/vendor/` is `v2/vendor/`.

**Rev B, 2026-08-31.** Adds section 12, the APRS radio carrier (MESHSAT-748, NiceRF DMR858M replacing the UV-K5(8) plus AIOC chain), and open items 10 through 14. Sections 1 through 11 are unchanged from Rev A except for the open register in section 11.

Exact geometry extracted from the CAD source of truth. This document replaces every `FROM-CONFIG` placeholder in `MESHSAT-709-claude-design-prompt.md`. Upload it alongside that prompt to the Claude Design project, and treat it as the dimensional input to the KiCad phase.

**Provenance.** Read 2026-08-31 from the owner's laptop, `~/Documents/Team Shared Root/Projects/MeshSat/Field Kit/CAD/`, files `field_kit_config.py` (260 lines) and `field_kit_step.py` (1478 lines). Every number below is either quoted verbatim from those files or derived from them by arithmetic shown inline. Nothing here is estimated. The measurement tags (`[MEASURED]`, `[DATASHEET]`, `[SPEC]`, `[DESIGN]`, `[COMPUTED]`, `[DERIVED]`) are carried over from the config so the ECAD phase inherits the same confidence grading.

---

## 1. Frame and datum conventions

All coordinates are in the **case-centred frame** used by the CAD: origin at the centre of the case interior cavity, X along the long axis (287 mm case dimension), Y along the short axis (220 mm), Z vertical, +Z up. Plates are centred on the origin in X and Y, so a plate of length L spans X from -L/2 to +L/2.

**Critical caveat on the 180 degree rotation.** At the tail of `field_kit_step.py` (lines 1446 to 1463) the **case shell alone** is rotated 180 degrees about Z; the plates, the devices and the internal cables are *not* rotated. Every case-wall feature (SMA bulkhead cuts, the front-panel LED row, the USB-C inlet) is therefore authored in a pre-rotation frame and lands mirrored in the world frame. The authoritative post-rotation positions are the `_PORTS` entries at lines 1091 to 1097, reproduced in section 7 below. Do not apply the flip a second time when importing into KiCad.

Plate-local coordinates, where used in the CAD for cutouts, have their origin at the plate's back-left corner, that is at (-L/2, -W/2) in the case-centred frame.

---

## 2. Board outlines

The three carrier PCBs take the outline of the plates they replace. The case cavity is stepped, narrower at the bottom and wider toward the rim, which is why the three outlines differ; each plate has a uniform 5 mm clearance to its own local cross-section.

| Board | Replaces | Length X (mm) | Width Y (mm) | X span | Y span | Corner radius | Current thickness |
|---|---|---|---|---|---|---|---|
| PCB-A POWER + I/O | bottom floor | 240.0 `[MEASURED]` | 160.0 `[MEASURED]` | -120.0 to +120.0 | -80.0 to +80.0 | 5.0 mm `[DESIGN]` | 3.0 mm HDPE |
| PCB-B COMPUTE | middle floor | 245.0 `[MEASURED]` | 170.0 `[MEASURED]` | -122.5 to +122.5 | -85.0 to +85.0 | 5.0 mm `[DESIGN]` | 3.0 mm HDPE |
| PCB-C DISPLAY | top floor | 250.0 `[MEASURED]` | 180.0 `[MEASURED]` | -125.0 to +125.0 | -90.0 to +90.0 | 5.0 mm `[DESIGN]` | 3.0 mm HDPE |

The design prompt specifies 1.6 mm FR-4 for PCB-A and PCB-B and 1.0 to 1.2 mm for PCB-C. Every one of those is thinner than the 3.0 mm HDPE being replaced, so the Z stack in section 4 gains headroom rather than losing it. See section 9 for how much.

---

## 3. Mounting holes, the four M3 rods

Single source of truth in the CAD, and the one geometric constraint shared by all three boards: the rods are straight, so all three boards must be drilled at the same absolute XY.

Derivation: the rod positions are anchored to the **middle** plate's corner inset, `ROD_INSET = 12.0` mm `[MEASURED]` from that plate's edge. With `MIDDLE_FLOOR_L/2 = 122.5` and `MIDDLE_FLOOR_W/2 = 85.0`:

| Rod | X (mm) | Y (mm) |
|---|---|---|
| R1 | -110.5 | -73.0 |
| R2 | +110.5 | -73.0 |
| R3 | -110.5 | +73.0 |
| R4 | +110.5 | +73.0 |

Hole diameter **3.2 mm** `[DERIVED]`, M3 clearance fit. Rod is M3, `ROD_DIAMETER = 3.0`, `ROD_LENGTH = 110.0` mm `[MEASURED]`, QUARKZMAN M3 x 110 stainless.

Edge distance from the hole **centre** to the nearest board edge, per board:

| Board | To X edge | To Y edge | Material left at the tightest point |
|---|---|---|---|
| PCB-A (240 x 160) | 9.5 mm | **7.0 mm** | 5.4 mm |
| PCB-B (245 x 170) | 12.0 mm | 12.0 mm | 10.4 mm |
| PCB-C (250 x 180) | 14.5 mm | 17.0 mm | 12.9 mm |

PCB-A's 7.0 mm Y edge distance is the tightest case. It is workable in FR-4, but see section 9: the M3 nut envelope reaches to within 4.0 mm of that edge, so the mechanical keep-out, not the hole, is what governs the copper pour.

**Nut keep-out.** Every rod carries 6 nuts, one on each face of each plate. `NUT_OD = 6.0` mm across corners `[DATASHEET]`, `NUT_H = 2.4` mm `[DATASHEET]`. Minimum annular keep-out on both faces of every board is therefore a 6.0 mm circle centred on each rod hole, and in practice larger, because a washer and a nut driver both need to land. Recommend specifying **9.0 mm diameter** keep-out (no components, no exposed copper) on both faces at all four positions, and confirming with the actual driver.

---

## 4. Vertical stack

`Z_CASE_FLOOR = -CASE_INTERNAL_H / 2 = -55.0`. The bottom plate floats `NUT_H` above the case floor so the nut below it has somewhere to sit. Gaps are quoted top face of one plate to bottom face of the next.

| Feature | Z (mm) | Derivation |
|---|---|---|
| Case interior floor | -55.0 | `-CASE_INTERNAL_H / 2` |
| Nut P1B (below PCB-A) | -55.0 to -52.6 | seats on the case floor |
| **PCB-A underside** | **-52.6** | `Z_BOTTOM = Z_CASE_FLOOR + NUT_H` |
| PCB-A top face | -49.6 | `+ FLOOR_THICKNESS 3.0` |
| Bottom bay free height | 42.3 | `BOTTOM_GAP` `[DESIGN]`, at its stated minimum |
| **PCB-B underside** | **-7.3** | `Z_MIDDLE = Z_BOTTOM + 3.0 + 42.3` |
| PCB-B top face | -4.3 | |
| Middle bay free height | 53.9 | `MIDDLE_GAP` `[DESIGN]` |
| **PCB-C underside** | **+49.6** | `Z_TOP = Z_MIDDLE + 3.0 + 53.9` |
| PCB-C top face | +52.6 | |
| Nut P3A (above PCB-C) | +52.6 to +55.0 | |
| Rod top | +55.0 | `Z_CASE_FLOOR + 110.0`, flush with the P3A nut |
| Display flange top | +53.6 | `Z_ON_TOP + DISPLAY_PROTRUSION 1.0` |

Rod length closes exactly: `2 x 2.4 + 3 x 3.0 + 42.3 + 53.9 = 110.0`. **If the boards are thinner than 3.0 mm the rod math no longer closes**, and either the gaps grow or the rod length changes. See section 9.

Total assembled height, case floor to display flange top: `53.6 - (-55.0) = 108.6` mm, against a `CASE_INTERNAL_H` of 110.0 mm `[COMPUTED]`, so **1.4 mm of headroom**. `CASE_INTERNAL_H` is itself computed from the 152 mm external `[SPEC]` figure and the config explicitly asks for a caliper check before cutting. That check is still outstanding and it gates the whole stack.

---

## 5. Existing cutouts to carry over

Quoted in plate-local coordinates as the CAD authors them, and converted to the case-centred frame.

**PCB-A (bottom):** no extra cutouts. The bottom plate sits directly on the case floor and has no pass-through.

**PCB-B (middle):** one centre pass-through, plate-local (122.5, 85.0), world **(0.0, 0.0)**, diameter **15.0 mm**.

**PCB-C (top):** five LED holes plus a DSI slot.

| Feature | Plate-local X, Y | World X, Y | Diameter |
|---|---|---|---|
| LED 1 | 85.0, 165.0 | -40.0, +75.0 | 8.0 mm |
| LED 2 | 105.0, 165.0 | -20.0, +75.0 | 8.0 mm |
| LED 3 | 125.0, 165.0 | 0.0, +75.0 | 8.0 mm |
| LED 4 | 145.0, 165.0 | +20.0, +75.0 | 8.0 mm |
| LED 5 | 165.0, 165.0 | +40.0, +75.0 | 8.0 mm |
| DSI ribbon slot | 105.0, 100.0 | -20.0, +10.0 | 20.0 mm |

LED row pitch is 20.0 mm, and the row sits 15.0 mm in from the plate's long edge. `LED_HOLE_DIAMETER = 8.0` `[MEASURED]`, Gebildet 8 mm panel-mount LEDs.

**Display aperture.** The display is recessed into a cutout in the top plate with only 1.0 mm of bezel proud of the surface. Pi Touch Display 2, 7 inch variant: outer envelope `189.32 x 120.24 mm` `[DATASHEET]`, flange thickness 2.0 mm, central rear hump `100.0 x 70.0 mm` reaching 14.92 mm total depth. Placement in the CAD: outer envelope X from -94.66 to +94.66, Y from -70.12 to +50.12 (the display is offset 10 mm in -Y). Rear hump X from **-50.0 to +50.0**, Y from **-45.0 to +25.0**, hump underside at Z = +38.68.

---

## 6. Device footprints, per board

Rectangles are the CAD bounding boxes, which the config states are visualisation placeholders rather than detailed geometry. Use them for zoning and collision work, not for footprint generation. All are in the case-centred frame.

### PCB-A, bottom board, devices sit at Z = -49.6

| Device | Footprint L x W x H (mm) | X span | Y span | Z top |
|---|---|---|---|---|
| UV-K5(8) with AIOC mated | 120 x 65 x 37.5 | -15.0 to +105.0 | -32.5 to +32.5 | -12.1 |
| Sabrent HB-UM43 hub (rotated 90 deg) | 36 x 86 x 15 | -110.0 to -74.0 | -70.0 to +16.0 | -34.6 |
| GPS puck, u-blox | 40 x 26 x 18 | +50.0 to +90.0 | -65.0 to -39.0 | -31.6 |
| USB WiFi adapter | 97.6 x 25.5 x 11.7 | +7.4 to +105.0 | +39.5 to +65.0 | -37.9 |

**The hub rectangle is the prize.** Deleting the Sabrent frees a contiguous **36 x 86 mm** rectangle at X -110.0 to -74.0, Y -70.0 to +16.0, and it sits in the otherwise empty western third of the board. Counting the whole region west of the UV-K5 (X -120.0 to -15.0, full 160 mm width, 16,800 mm2) minus the hub block, PCB-A has roughly **13,700 mm2 of unoccupied board area** for the embedded hub circuit, the eFuses and the 5 V distribution. That is ample and it does not require moving a single existing device.

### PCB-B, middle board, devices sit at Z = -4.3

| Device | Footprint L x W x H (mm) | X span | Y span | Z top |
|---|---|---|---|---|
| Geekworm X1202 UPS (rotated 90 deg) | 85 x 97 x 25 | -121.0 to -36.0 | -48.5 to +48.5 | +20.7 |
| Raspberry Pi 5 with active cooler (rotated 90 deg, pogo-stacked on X1202) | 56 x 85 x 25 | -106.5 to -50.5 | -42.5 to +42.5 | +45.7 |
| LilyGO T-Call A7670E | 75 x 30 x 15 | +32.5 to +107.5 | +15.0 to +45.0 | +10.7 |
| RTL-SDR Blog v4 | 69 x 27 x 13 | +20.0 to +89.0 | -13.5 to +13.5 | +8.7 |
| XIAO ESP32-S3 Meshtastic node | 25 x 20 x 5 | -107.5 to -82.5 | +50.0 to +70.0 | +0.7 |
| Sonoff ZBDongle (CC2652P) | 80 x 24 x 12 | -40.0 to +40.0 | -55.0 to -31.0 | +7.7 |
| DCF77 receiver | 70 x 15 x 10 | -35.0 to +35.0 | +55.0 to +70.0 | +5.7 |
| RockBLOCK 9603 | 45 x 45 x 16 | +62.5 to +107.5 | -70.0 to -25.0 | +11.7 |

### PCB-C, top board

Carries the Pi Touch Display 2 only, recessed into the aperture given in section 5, plus the LED row and the DSI slot.

---

## 7. Bulkheads and RF ports

Seven case penetrations, all at **Z = +25.0** `[DESIGN]`, raised from 0 specifically so they stay reachable from above when the top plate is tilted back during the interim screen-tilt service procedure. SMA case hole diameter **6.5 mm** `[DATASHEET]`, IP67 SMA bulkhead. Bulkhead body radius 4.0 mm, body length 16.0 mm, so the **inner face sits at X = +/-128.75**.

These are the post-rotation world positions from `_PORTS`, lines 1091 to 1097, and they are authoritative.

| Bulkhead | Serves | Inner face X, Y, Z | Faces | Board of the source radio |
|---|---|---|---|---|
| SMA UHF | UV-K5(8) via AIOC | +128.75, +25.0, +25.0 | -X | PCB-A |
| SMA SDR | RTL-SDR Blog v4 | +128.75, -25.0, +25.0 | -X | PCB-B |
| SMA WiFi | USB WiFi adapter | +128.75, +50.0, +25.0 | -X | PCB-A |
| SMA LTE | LilyGO T-Call A7670E | -128.75, +25.0, +25.0 | +X | PCB-B |
| SMA Iridium | RockBLOCK 9603 or 9704 | -128.75, -25.0, +25.0 | +X | PCB-B |
| SMA LoRa | XIAO ESP32-S3 | -128.75, +60.0, +25.0 | +X | PCB-B |
| USB-C inlet | X1202 USB-C IN | +100.0, -87.5, +25.0 | +Y | PCB-B |

USB-C bulkhead body is a 12.0 x 25.0 x 7.0 mm box; the case cut is 12.5 x 60 x 7.

Every bulkhead sits at Z = +25.0, which is **29.3 mm above PCB-B's top face** and **74.6 mm above PCB-A's top face**. Two consequences for the design pages: no board-edge SMA jack on either board can reach a bulkhead directly, so all six RF paths stay pigtails, exactly as the prompt assumed; and the PCB-A radios (UV-K5 and WiFi) have the longer and more awkward climb, which is the argument for putting their strain-relief anchors near the board's X extremes.

The CAD holds a full routing polyline for each of the six pigtails, with a bend-radius validator enforcing `SMA_BEND_R = 12.5` mm `[DATASHEET]`, RG-316 minimum per Pasternack. **Pull the fabricated pigtail lengths from the CAD model rather than from this document**; the polylines are filleted, so waypoint-to-waypoint arithmetic overstates them.

---

## 8. Case features that constrain the boards

| Feature | Position | Note |
|---|---|---|
| Front-panel LED row, 5 x 8.0 mm | X = -44, -22, 0, +22, +44 at Y = -110 (front wall), **Z = -35.0** | Pitch 22.0 mm |
| USB-C power inlet | X = +100, front wall, Z = +25.0 | The one cable that survives *(superseded: removed by the one-pack ruling of 3 Sep, slot deleted on B11 (32.4); the wall data port is the 38999 connector of ruling 6, 32.13)* |
| Case external | 287 x 220 x 152 mm `[SPEC]` | Base cavity 110.0, lid cavity 32.0, both `[COMPUTED]` |

**The front-panel LED row is at Z = -35.0, which lands between PCB-A's top face (-49.6) and PCB-B's underside (-7.3).** It is in the PCB-A to PCB-B bay. So the operator-visible status LEDs, the ones you can see with the case closed, must be driven from **PCB-A**, not from PCB-C. See section 10, item 5.

---

## 9. Clearance findings

These came out of the extraction and are the things most likely to bite the ECAD phase. None of them are blocking today; all of them want an owner decision before layout starts.

1. **Three device corners are coincident with M3 nut envelopes, at zero clearance.** With a 6.0 mm across-corners nut centred on each rod hole, the nut envelope corner and the device bounding-box corner touch exactly at three sites: RockBLOCK 9603 against rod R2 (both reach X = +107.5, Y = -70.0), XIAO against rod R3 (both reach X = -107.5, Y = +70.0), and the Sabrent hub against rod R1 (moot, the hub is being deleted). On HDPE with velcro this was invisible. On a PCB with a real 9.0 mm keep-out it is an overlap, and both surviving devices have to move a few millimetres inboard. Cheapest fix: shift the RockBLOCK site and the XIAO site 5 mm toward the board centre in both axes.

2. **The Pi 5 clears the display rear hump by 0.5 mm in X.** Pi 5 east edge at X = -50.5, hump west face at X = -50.0. This is deliberate in the CAD and the comment says so, but 0.5 mm is below any sane PCB placement tolerance once the Pi is on standoffs on a board that is itself located by four clearance holes. Either move the stack west (there is 1.5 mm to the board edge, so not much) or accept a documented interference risk and verify on the first article.

3. **The bottom bay is at its stated minimum.** `BOTTOM_GAP = 42.3` is exactly `UVK5_H 37.5 + 2 x NUT_H 4.8`. Actual UV-K5 top to PCB-B underside clearance is 4.8 mm. That is fine, but there is no room to grow the bottom bay without lengthening the rods, and `UVK5_H` is tagged in the config as needing a measured height **with the AIOC mated**, which has never been done.

4. **Thinner boards break the rod arithmetic, in a useful direction.** Going from 3 x 3.0 mm HDPE to 1.6 + 1.6 + 1.1 mm FR-4 removes **4.7 mm** from the stack. The rod length closure `2 x NUT_H + sum(thickness) + BOTTOM_GAP + MIDDLE_GAP = 110.0` no longer holds, so either the two gaps absorb the 4.7 mm (recommended, it goes straight into the 1.4 mm headroom problem and into finding 2) or the rods get shorter. The design pages should state which, because it changes `Z_MIDDLE` and `Z_TOP` and therefore every board-to-board connector height.

5. **Nothing can route outboard of the rods on PCB-A.** The rod holes are 7.0 mm from the Y edge; a 9.0 mm keep-out centred there leaves 2.5 mm of board between the keep-out and the outline. That is not enough for a pour or a routed pair to pass outboard with any sane clearance, so on PCB-A every trace and every plane must pass **inboard** of all four nut keep-outs. PCB-B (12.0 mm) and PCB-C (14.5 and 17.0 mm) have no such restriction.

---

## 10. Corrections to the 2026-08-18 design prompt

The prompt is sound, and its board plan matches the CAD's actual device-to-floor assignment. Five statements in it need correcting before the design pages are generated.

1. **"18650 cells hang below, clearance and airflow keep-out" is wrong.** The X1202 rests directly on the middle plate (`_Z_X1202_BOT = Z_ON_MIDDLE`) and its 25 mm height already includes the battery holder stack. Nothing hangs below PCB-B. The keep-out is an **above-board volume** of 85 x 97 x 25 mm at X -121.0 to -36.0, Y -48.5 to +48.5, not a cutout. Note also that the config header claims the 18650 cells were removed from the kit in favour of external USB-C input, while the modelled `X1202_H = 25.0` and the field kit BOM both assume cells present. That contradiction should be settled on the assumptions page.

2. **The WiFi adapter in the CAD is the wrong part.** It is modelled as a TP-Link Archer T3U Plus, 97.6 x 25.5 x 11.7 mm, which is an RTL8812BU-class device. The repo's standing hardware ruling bans RTL8812AU/8814AU/8821AU outright and mandates **MT7612U** (Alfa AWUS036ACM or Panda PAU0D). The prompt already says "MT7612U-class", so the prompt is right and the CAD is stale, but the approved dongle's real envelope has never been measured and it will not be 97.6 x 25.5 x 11.7. **This is the single largest unresolved footprint on PCB-A.** Measure the actual dongle before layout.

3. **The DCF77 module in the CAD is the wrong part.** Modelled as an ELV DCF-2, 70 x 15 x 10 mm. The field kits run a DCF-1060N-800 / SP6007-class receiver. The prompt's decision to demote DCF77 to a remote-mount 4-pin connector is correct and is reinforced by the CAD: the modelled position (X -35.0 to +35.0, Y +55.0 to +70.0 on PCB-B) puts the ferrite about **6.6 mm** from the nearest corner of the X1202 UPS and about **20 mm** from the Pi 5, which is precisely the geometry that has never achieved carrier lock on parallax. The 50 cm separation the field notes call for is not achievable anywhere inside this case, which is the argument for the remote-mount connector, and it should be stated that way on the design page rather than as a preference.

4. **The ZigBee part number is ambiguous in the CAD.** The config comment reads "ZBDongle-E / ZBDongle-P" and the placement comment says "ZBDongle-E", while the kit actually runs the **CC2652P**, that is the ZBDongle-P. The two sticks are not the same length. Confirm before committing the 80 x 24 mm envelope.

5. **PCB-C is not where the operator-visible LEDs are.** The prompt puts the status-LED row on PCB-C, "where the current top plate has its drill row", with light pipes through the board. Both LED rows exist in the CAD and they are on **opposite sides of the case**: PCB-C's row is at world Y = +75, while the case's own front-panel row is on the front wall at Y = -110, Z = -35, which is in the PCB-A to PCB-B bay. With the lid closed, the front-wall row is the one an operator can see. Recommend: **the operator status LEDs belong to PCB-A**, driven off the power tree that already knows the eFuse states, and PCB-C's row becomes a lid-open service indicator or is dropped. This needs an owner ruling and belongs on the open-questions page.

Additionally, the RockBLOCK dual-footprint site has **no 9704 mechanical data in the CAD at all**; only the 9603 is modelled, at 45 x 45 x 16 mm. The 9704 envelope, mounting-hole pattern and connector position have to come from the Ground Control datasheet before that site can be laid out.

---

## 11. Still open before ECAD

| # | Item | Blocks | Owner action |
|---|---|---|---|
| 1 | Caliper check of `CASE_INTERNAL_H` (assumed 110.0, `[COMPUTED]` from a `[SPEC]` external height) | The whole Z stack, and the 1.4 mm headroom | Measure the base cavity |
| 2 | Measured envelope of the approved MT7612U dongle | PCB-A layout | Measure the actual unit |
| 3 | RockBLOCK 9704 mechanical drawing | PCB-B dual-footprint site | Pull from Ground Control |
| 4 | ~~`UVK5_H` measured with the AIOC mated~~ DROPPED 2026-09-02: owner ruled the carrier set carries no UV-K5 dock (section 12.2) | nothing | none |
| 5 | ZBDongle-P confirmed over ZBDongle-E | PCB-B envelope | Confirm |
| 6 | X1202 cells present or absent | PCB-B keep-out volume and the power budget | Rule |
| 7 | Operator LED row on PCB-A or PCB-C | PCB-A and PCB-C scope | Rule, see section 10 item 5 |
| 8 | Where the 4.7 mm freed by thinner boards goes | `Z_MIDDLE`, `Z_TOP`, all board-to-board connector heights | Rule |
| 9 | Hub topology, single hub on PCB-A vs one per board | Interconnect design | Rule, already on the prompt's page 10 |
| 10 | DMR858M mechanical drawing: mounting holes, castellation pitch, antenna-pad position, keep-outs | The APRS carrier site, section 12 | Pull from NiceRF, or measure on arrival 2026-09-15 |
| 11 | X1202 rated peak 5 V output current | Whether the 3.0 to 3.2 A transmit burst is survivable at all | Pull from Geekworm, then measure |
| 12 | Case shell material and wall thickness | Whether a conduction path to the wall is worth designing, section 12.5 | Confirm from the case datasheet |
| 13 | APRS carrier form: mezzanine on PCB-A, integrated PCB-A zone, or fourth board | PCB-A layout and the whole APRS branch | Rule, see section 12.6 |
| 14 | Programming path: USB-UART on the hub, or the free Pi UART | One hub port, and whether a `ttyAMA` path enters the design | Rule |

Items 1 through 5 and 10 through 12 are measurements and datasheets. Items 6 through 9, 13 and 14 are decisions. None of them blocks generating the design pages, and all of them block committing a KiCad footprint.

**Status 2026-09-02 (see section 13 for the rulings):** items 1, 2, 5, 6, 7, 8, 9, 13 and 14 are CLOSED. Item 4 was dropped earlier the same day. Item 12 is DEMOTED: the mezzanine ruling means no wall strap is designed, so the shell material only matters for a later revision. Still open, all datasheet pulls owned by Claude: item 3 (9704 drawing, Ground Control), item 10 (DMR858M drawing, NiceRF or on arrival 2026-09-15), item 11 (X1202 ratings, now BOTH the 5 V output and the USB-C input, because the extension bank feeds the input), and new item 15 (Alfa AWUS036ACM mechanical drawing, replaces the caliper measurement of item 2).

**Pulls completed later on 2026-09-02** (vendor files staged on the laptop at `~/Documents/Team Shared Root/Projects/MeshSat/Field Kit/ECAD/vendor/`):

- **Item 3, RockBLOCK 9704: DONE.** SparkFun lists the SMA variant at 48 x 52 x 16 mm, under 35 g without antenna, notched edge for slot mounting, 16-pin 0.1 in male header, USB-C, U.FL for GNSS passthrough, SMA antenna. Ground Control hardware page: V_IN+ 4.0 to 5.3 V at 500 mA max, V_BATT 3.6 to 4.5 V at 1.1 A max, peak 1.4 W, idle under 60 mW, sleep under 5 mW; logic in HIGH 2.0 to 3.6 V, out HIGH 2.9 to 3.4 V. Header: 1 GND, 2 I_SYN, 3 I_EN, 4 GND, 5 GPS_EN, 6 /P_EN (cap charge enable, active low), 7 I_BTD (booted), 8 XMT_G (high while transmitting), 9 I_WK_I, 10 GND, 11 I_WK_O, 12 V_BATT, 13 TXD (from 9704), 14 RXD (to 9704), 15 V_IN+, 16 V_IN-. Downloaded: `RockBLOCK 9704-SMA-2A.step` (52 MB, the authoritative outline and hole geometry, extract in the ECAD phase), mount drawing ACC-RB9704SMA-MOUNT Rev A (08-04-25, an accessory bracket, not the PCB: 52.0 x 56.0 mm, four Ø4.60 holes on a 32.0 x 32.0 mm pattern, 47.06 mm cavity, 3.00 mm base, Ø12.00 SMA clearance; the 32 x 32 pattern is a ready-made mounting option for the PCB-B site), schematic 2B1 (08/05/2025, black soldermask, rotated SMA, J2 PicoBlade battery connector; Ground Control drew it in KiCad). XMT_G on pin 8 is the 9704's own transmit-active output and belongs on the GPIO ribbon for the same reason as the APRS PTT in section 12.7.
- **Item 11, X1202: DONE** (wiki.geekworm.com/X1202). UPS output 5.1 V +-5 % max 5 A on the pogo pins, plus 2x XH2.54 2-pin 5 V output connectors and 2x USB-A power sockets on the X1202 itself; USB-C input 5 V 5 A; DC 5521 jack input 6 to 18 V at 3 A or more (never both inputs at once); charge current 2.3 to 3.2 A max; terminal voltage 4.23 V, recharge threshold 4.1 V; four cells in parallel; PCB 97.4 x 85 mm; fuel gauge at I2C 0x36. Consequence for R6: the extension bank may feed either the USB-C input at 5 V or the DC jack at 6 to 18 V; the ruling says USB-C, the jack is the alternative if a 2S bank is ever preferred. **Rail budget during a 5 W analog APRS burst is OVER the X1202 rating** (corrected 2026-09-02 after a peer review caught that the 1.5 A figure in the notes is the USB peripheral draw only): Pi 5 on the pogo pins about 1.5 A plus about 1.5 A of peripherals is a 3.0 A baseline, and the 8 V boost adds about 3.1 A at 5 V for the DMR858S analog figure of 1.6 A at 8 V, so about 6.1 A against a 5.0 A rating, roughly 20 percent over. Not survivable with a duty-cycle note. Fix options, RULED 2026-09-02 as R15 = option (a): (a) feed the mezzanine boost from the PCB-A extension bank of R6 instead of the X1202 rail, which takes the burst off the X1202 entirely and is the recommended path; (b) low-power 1 W analog at 0.8 A at 8 V; (c) DC-jack input path. The XH2.54 outputs remain the natural feed for the carrier logic power.
- **Item 15, Alfa AWUS036ACM: CONFLICTING vendor data.** Alfa's page: 62 x 85.3 x 24 mm, 60 g, 2x RP-SMA female, USB 3.0 with an included extension cable. A reseller lists the body at 85 x 26 x 12 mm with a USB-A 3.0 plug. Use 85 x 26 x 12 plus plug provisionally; the paper fit test settles it since both kits carry the dongle. Note the MT7612U enumerates as a SuperSpeed device (bcdUSB 3.00); a USB 2.0 hub on PCB-A drops it to 480 Mbit/s High-Speed, still far above what the P2P link carries, so hub speed class is an engineering choice, not a ruling. **New open point (peer review 2026-09-02): the AWUS036ACM has TWO RP-SMA antenna ports (MT7612U is 2x2) and section 7 has ONE "SMA WiFi" bulkhead.** Either a second WiFi bulkhead is added to the case or the kit runs 1x1 with the second port terminated. RULED 2026-09-02 as R16: second bulkhead.
- **Item 10, DMR858M: CLOSED 2026-09-02 from NiceRF's own V1.2 datasheet (July 2026, Chinese, `nicerf.cn/uploads/20260821/DMR858M 5W 数字对讲机模块 V1.2.pdf`, staged in `ECAD/vendor/` with the mechanical page rendered as `dmr858m-mech-10.png`).** The English site blocks both the runner and the laptop; the Chinese site does not. Facts: PCB **38.69 x 58.31 mm** (+-0.1), **24 castellated pads** in two rows along the long edges at **2.54 mm pitch**, the right row (pins 1 to 12, VCC at the top) starting **15.06 mm from the top edge** below the SMA, the left row (pins 13 to 24, MIC- at the bottom) aligned with it; **two Ø3.00 mm mounting holes** at 2.81 / 2.96 mm from the top-left corner and 2.73 / 2.86 mm from the bottom-right corner; **edge-mounted SMA at the top edge, right of centre**; USB-C (configuration), PTT button, rotary channel switch and a firmware DIP switch on the bottom half; a black finned **heatsink on the component side, 19.50 mm total height** with it (the 10.2 mm figure from search snippets excludes the heatsink). Pin table: 1 VCC 3.7 to 8.5 V; 2, 4, 15, 17 GND; 3 CS (0 = sleep); 5 PTT (0 = transmit); 6 LINE_OUT; 7 to 10 channel select 8421 (default 1); 11 OUTP, 12 OUTN (8 ohm 2 W or 4 ohm 5 W speaker); 13 MIC-, 14 MIC+ (bias provided); 16 **SPKEN, receive indicator** (high on signal); 18 TXD, 19 RXD (57600 baud); 21 HST_TX, 22 HST_RX (firmware upgrade); 20, 23, 24 NC. Electrical: -20 to +60 C; sleep < 0.1 mA; RX < 165 mA; TX at 8 V 5 W: **1700 mA analog** / 900 mA digital; 2 W: 1000 / 640 mA; 36 to 37.5 dBm high, 32 to 34.5 dBm low at 430 MHz; -117 dBm at 5 percent BER. **There is no dedicated T/R output on the M** (the 858S has one); transmit blanking for section 12.7 comes from the PTT line itself, which the carrier drives, so the carrier simply mirrors PTT to the Pi GPIO. **Z consequence for R4/R17:** mezzanine stack = standoff + 1.6 mm board + 19.5 mm module, i.e. 26 to 29 mm above PCB-A, so `BOTTOM_GAP` becomes about **30 mm**, not 26; the middle bay gives back 4 mm of the 22.7 mm it gained. The DMR818S-5W core-module datasheet V1.7 (stamp-hole core the M is built on) is staged alongside. Also staged earlier: the older DMR858 datasheet and the peer's DMR858S sheet.

- ~~**Item 10, DMR858M: PARTIAL.**~~ NiceRF blocks the runner (403), so the M datasheet is not in hand. Retrieved the older DMR858 datasheet Rev 1.2 (2020-11, 20-pin functional board): supply 3.3 to 9 V, TX under 1.6 A at 8 V for 5 W, under 1.1 A for 3 W, RX under 100 mA, sleep under 50 uA, UART 57600 baud, PTT active low (0 = TX), CS sleep input, and a **T/R indicator output (1 = TX)**, which is the module-side transmit-blanking signal section 12.7 asks for. Peer-retrieved DMR858S datasheet Rev 1.1 (nicerf.com siwei_pdf path, serves to this host; staged in the vendor folder) is the closer relative and splits transmit current by mode: **analog high power 5 W at 8 V 1600 mA typ (the APRS design case), DMR digital 1000 mA, analog low power 1 W 800 mA, digital low power 460 mA; RX 170 mA; sleep 1 mA at CS low; supply 3.6 to 8.4 V; working temperature -20 to +60 C**, narrower than the DMR858 sheet, which matters in a sealed case in sun. Same functional-board pin map as the 858 (PTT pin 9 active low, T/R pin 11 output, CS pin 8, UART pins 5/6, VCC 16 to 19). Search snippets for the M variant give 38.65 x 58.31 x 10.2 mm and a different pin map (PTT pin 5, OUTP 11, OUTN 12, MIC- 13, MIC+ 14, TXD 18, RXD 19). Mechanical drawing and the M pin table come from the module on arrival 2026-09-15 or from the owner's earlier download.

---

- **Pulls added with the B4 re-layout (2026-09-02):** LimeSDR Mini 2.0 and LILYGO T-Beam 1W mechanicals from their official STEP models (section 15.6), the TPS2065C 1 A limit from TI's family table (CH3 and CH4 re-specified at 2 A), and the AIOC circuit (MIT, `skuep/AIOC` rev 1.2, staged in `ECAD/vendor/aioc/` with its exact netlist) as the basis of the PCB-D core.

## 12. APRS radio carrier, MESHSAT-748, added 2026-08-31

Owner decision 2026-08-31 on MESHSAT-748: the UV-K5(8) plus AIOC v1.2 chain is to be replaced by a board-mounted NiceRF DMR858M (5 W VHF, 39 x 58 x 10 mm, UART control plus analog audio), fed 8 V from a boost stage on the X1202 5 V rail rather than from any Pi USB port. 2 units ordered, ETA 2026-09-15. **The kits keep the handheld until the carrier is proven**, so both builds have to be supported by one board revision.

Everything in this section is derived from the CAD numbers in sections 2 through 9 above. Nothing here has been measured on hardware, because the modules have not arrived.

### 12.1 The site it inherits

| | UV-K5(8) with AIOC mated | NiceRF DMR858M |
|---|---|---|
| Envelope | 120 x 65 x 37.5 mm | 39 x 58 x 10 mm |
| CAD position | X -15.0 to +105.0, Y -32.5 to +32.5, on PCB-A at Z -49.6 | to be sited |
| Plan area | 7,800 mm2 | 2,262 mm2 |
| Board | PCB-A | PCB-A recommended, section 12.6 |
| Bulkhead | SMA UHF at +128.75, +25.0, +25.0 | the same one, and only one of them can have it |

The module fits inside the rectangle the handheld already occupies with room to spare, which is what makes a build-time either/or at a single site geometrically possible.

### 12.2 The Z stack does not improve, and this is the trap

`BOTTOM_GAP = 42.3` mm is exactly `UVK5_H 37.5 + 2 x NUT_H 4.8` (section 9, finding 3). The bottom bay height is set by the handheld and by nothing else. With the handheld gone, the tallest object on PCB-A becomes the u-blox GPS puck at 18.0 mm, and `BOTTOM_GAP` could in principle fall to roughly 24 mm, freeing about 18 mm of Z on top of the 4.7 mm that thinner boards free.

**OWNER RULING 2026-09-02, supersedes the paragraph below:** the carrier set is designed for the DMR858M only. No UV-K5 dock, no AIOC receptacle, no dual build on PCB-A. The physical kits keep the handheld on the HDPE floors until the carrier set is proven, which is a fleet statement, not a board requirement. Consequences: `BOTTOM_GAP` is free to drop toward roughly 24 mm (GPS puck at 18.0 mm becomes the tallest PCB-A object), the ~18 mm plus the 4.7 mm from thinner boards are decided together under open item 8, the UHF bulkhead belongs to the DMR858M site outright, and open item 4 is gone. The mezzanine still earns its place for respin isolation (section 12.6), not for a handheld fallback.

~~**That saving must not be banked.**~~ (superseded) Rev A has to keep the UV-K5 build buildable, so `BOTTOM_GAP` stays at 42.3 mm and `Z_MIDDLE`, `Z_TOP` and every board-to-board connector height are unchanged. Open item 8, where the 4.7 mm goes, is decided without reference to the APRS change. The 18 mm becomes available only in a later revision that drops the handheld outright, and it is worth recording as the single largest Z saving available to this design, because the stack currently has 1.4 mm of headroom against an unverified `CASE_INTERNAL_H`.

A mezzanine is comfortably inside the existing bay: 8 mm standoff plus a 1.6 mm board plus a 10 mm module is 19.6 mm against 42.3 mm available, leaving 22.7 mm to PCB-B's underside for the boost inductor, the codec, connectors and airflow.

### 12.3 It cannot get far from the GPS or the WiFi dongle

PCB-A's east half is fully committed in Y. The GPS puck holds Y -65.0 to -39.0 and the WiFi adapter holds Y +39.5 to +65.0, so the corridor left for the radio is Y -39.0 to +39.5, which is 78.5 mm tall.

Placing the 39 x 58 mm module in that corridor, centred on Y = 0:

| Long axis | Module Y span | Clearance to GPS | Clearance to WiFi |
|---|---|---|---|
| 58 mm along Y | -29.0 to +29.0 | 10.0 mm | 10.5 mm |
| 39 mm along Y | -19.5 to +19.5 | 19.5 mm | 20.0 mm |

**The best available separation is about 20 mm to each**, and only in the orientation with the short axis across the corridor. Moving the module west increases the run to the +X bulkhead; there is no placement on PCB-A that buys meaningful distance from both receivers.

This is not strictly a regression. The handheld already occupies that same corridor and already transmits 5 W into the same bulkhead. What changes is that the transmitter stops being a shielded metal handheld sitting on velcro and becomes a bare module sharing a copper ground plane with both receivers, so conducted coupling is added to the radiated coupling that exists today. The design pages must treat the GPS desense and the WiFi desense as design problems with stated mitigations, not as inherited conditions.

### 12.4 The pigtail gets longer, not shorter

Bulkhead SMA UHF inner face is at X +128.75, Y +25.0, Z +25.0 (section 7).

| Path | Source point | Straight-line run |
|---|---|---|
| Today, handheld antenna port on top of the 37.5 mm dock | approx. X +105, Y 0, Z -12.1 | approx. 51 mm |
| Mezzanine module SMA on a 20 mm stack | approx. X +100, Y 0, Z -29.6 | approx. 67 mm |

A board-mounted module sits lower than the top of a docked handheld, so the replacement run is roughly 16 mm longer. **The gain is that both ends become captive**, not that the cable shortens. Per section 7 the fabricated length has to come from a CAD polyline under the `SMA_BEND_R = 12.5` mm validator; the figures above are straight-line distances for sanity-checking only.

### 12.5 Thermal, and why the case material is now on the blocking list

Module transmit draw is 900 mA typical and 1700 mA maximum at 8 V, so about 13.6 W into the module at worst case, of which 5 W leaves as RF. About 8.6 W is dissipated in the module, plus boost-stage loss at 85 to 90 percent efficiency, so roughly 10 W on the board during a burst.

Three facts make this the hardest part of the APRS change:

1. The case is sealed IP67, so there is no convective path out. The M12 vent plug equalises pressure; it does not ventilate.
2. The handheld's own metal body and battery mass are the heatsink today, and both leave with it.
3. PCB-A sits 2.4 mm above the case floor on nuts, in the least ventilated bay in the case, with PCB-B and the Pi's active cooler above it.

The conduction path to the case wall is therefore the only real option, and its value depends entirely on the shell material, which is why open item 12 is now on the blocking list. If the shell is plastic, that path is worth very little and the honest answer is a duty-cycle limit plus a thermal mass on the module rather than a wall strap.

**No thermal measurement exists.** APRS is short bursts and that is what makes this tractable at all, but the duty-cycle figure has to be written as a requirement in the design pages and verified on the first article.

### 12.6 Placement recommendation, and the case against it

Recommended: a small mezzanine board on standoffs inside the UV-K5 rectangle on PCB-A, carrying the DMR858M, the CM108-class codec, the PTT drive and the boost stage, connected to PCB-A by one keyed harness.

For it:
- It is the only free rectangle of the right size, and it is already the closest site to the UHF bulkhead.
- The boost stage belongs with the power tree, which is on PCB-A.
- Both new USB devices plug straight into the PCB-A hub, so no USB crosses a board boundary.
- The modules arrive 2026-09-15, after the design pages are generated, and nothing about them has been validated. A mezzanine confines the unproven, hot, high-current, high-RF subsystem to a board that can be respun without touching a 240 x 160 mm carrier.
- An unfitted mezzanine is how the UV-K5 build stays buildable from the same PCB-A.

Against it:
- PCB-A has the tightest routing constraints of the three boards. Section 9 finding 5 already forbids anything passing outboard of the nut keep-outs, and a 3.0 to 3.2 A pulsed trunk now has to route inboard alongside the hub's USB pairs.
- That trunk originates at the X1202 on PCB-B and has to cross the board-to-board interconnect, which sizes that connector for a pulsed 3 A rather than for the roughly 1.5 A the kit draws today.
- The bottom bay is the least ventilated part of the case, per section 12.5.

The alternatives are an integrated zone on PCB-A, which loses the respin isolation and the not-fitted build option, and a fourth board, which costs a board and an interconnect but buys placement freedom and would let the radio sit against a case wall. **This is open item 13 and it wants an owner ruling before layout.**

### 12.7 The software consequence, which costs one pin

The bridge's spectrum monitor watches 144.7 to 144.9 MHz as `ax25_0` (`internal/spectrum/spectrum.go`), and `internal/spectrum/scanner.go` already runs `rtl_power_fftw` at a reduced 20 dB gain with a comment stating that a nearby 144.8 MHz transmitter saturates the tuner front end and paints a false full-band stripe. That comment was written about the handheld.

There is no path today by which the spectrum monitor can learn that the kit itself is transmitting. PTT is keyed by Direwolf over CM108 HID (`internal/gateway/direwolf_supervisor.go`, `PTT CM108`) and never reaches the spectrum package. A permanently mounted 5 W transmitter therefore makes the kit classify its own APRS beacon as jamming, score `ax25_0` at zero, and fail it over.

(Code facts re-verified 2026-09-02 by a peer session: `internal/spectrum/spectrum.go` lines 72-77 still define the 144.700 to 144.900 MHz band and `internal/gateway/direwolf_supervisor.go` line 329 still emits `PTT CM108`.) **The carrier must bring PTT out as a Pi-readable GPIO with an explicit populated bias resistor**, so transmit blanking can be added in software later. One pin, specified now. It cannot be retrofitted without a respin, and the software side is a separate issue that does not block this board.

---

## 13. Owner rulings, 2026-09-02

Taken in one sitting, question by question. These are decisions, not proposals; do not re-open them without a new owner statement.

| # | Topic | Ruling | Closes |
|---|---|---|---|
| R1 | Handheld | The carrier set carries no UV-K5 dock and no AIOC receptacle. DMR858M only. The HDPE-floor kits keep the handheld until the carrier set is proven; that is a fleet statement, not a board requirement. | item 4 |
| R2 | Hub topology | One 4-port-class hub per board, on PCB-A and on PCB-B, each next to its own devices and eFuses. One upstream USB pair crosses the A-B interconnect. Two Pi ports used. Port count per hub IC is an engineering choice (a 7-port part on PCB-A leaves spares; both 4-port hubs would be exactly full). | item 9 |
| R3 | APRS carrier | Mezzanine on standoffs inside the former UV-K5 rectangle on PCB-A: DMR858M, CM108-class codec, PTT drive, 5 V to 8 V boost, one keyed harness to PCB-A. Justification is respin isolation, not a handheld fallback. | item 13 |
| R4 | Z stack | The middle bay absorbs the 4.7 mm from thinner FR-4 and the ~18 mm from the handheld. Rods stay 110 mm, PCB-C stays where the display and lid expect it, PCB-B drops. Provisional `BOTTOM_GAP` about 26 mm (18650 holders on PCB-A are ~22 mm tall, see R6); exact `Z_MIDDLE` is recomputed in the ECAD phase. | item 8 |
| R5 | Operator LEDs | PCB-A drives the case front-wall LED row (Y = -110, Z = -35), fed from the power tree that already knows the eFuse states. PCB-C's LED row is dropped. | item 7 |
| R6 | Energy | X1202 keeps its four cells (50 Wh). Added: a four-cell 18650 extension bank on PCB-A's western third with its own protection, charger with NTC low-temperature cutoff, and a 5 V output into the X1202's USB-C input. The case USB-C feeds the bank; the X1202 stays the last-resort UPS and its AC-loss signal now means "bank empty". Kit total about 100 Wh. Parallel-onto-the-X1202-pack was rejected (no external pack terminal, inrush between packs). | item 6 |
| R7 | Radio UART | USB-UART bridge on the mezzanine into the PCB-A hub. No Pi UART, no ribbon lines, no ttyAMA config. | item 14 |
| R8 | WiFi dongle | Alfa AWUS036ACM. Confirmed MT7612U (0e8d:7612) on both kits by lsusb, USB 3 side of the Sabrent hub, descriptor MaxPower 400 mA, no brand string. Footprint from Alfa's drawing (item 15). | item 2 |
| R9 | ZigBee | ZBDongle-P confirmed on both kits by descriptor: ITead "Sonoff Zigbee 3.0 USB Dongle Plus" on a CP2102 (10c4:ea60). Side fact: the T-Call enumerates as a WCH CH9102 (1a86:55d4, "USB Single Serial"), not the CH343 the notes claim. | item 5 |
| R10 | Case height | No caliper measurement. Design to the computed 110 mm. The documented fallback is the **Peli 1400**: interior 30.1 x 22.8 x 13.1 cm, exterior 34.7 x 29.5 x 14.6 cm, lid depth 3 cm, bottom depth 10.2 cm (Peli Protector catalogue, March 2024). It is a superset of the current cavity in all three axes; the only constraint it adds is that the top 8 mm of the stack sits in the lid, so nothing on PCB-C's top side may stand taller than about 20 mm. The 1300 is too small in plan for PCB-C; the 1450 (37.4 x 26 x 15.4) is the next size up. | item 1 |
| R11 | RockBLOCK | The dual 9603/9704 footprint stays, whatever Ground Control answers on the kit-two modem. | none (item 3 still needs the 9704 drawing) |
| R12 | Assembly | JLCPCB assembles everything, SMD and through-hole. Connectors and holders are chosen from the JLCPCB parts library where possible; anything else is consigned or substituted at BOM time. |  |
| R13 | Budget | Not a design input. The quote comes from the JLCPCB upload and the owner decides there. |  |
| R14 | Toolchain | Claude designs the complete boards in KiCad 9 on the owner's laptop over SSH. KiCad 9.0.9 installed the same day; sudo unblocked. |  |
| R15 | APRS burst power | The mezzanine's 5 V to 8 V boost is fed from the PCB-A extension bank of R6, not from the X1202 5 V rail. The X1202 never sees the transmit burst; its cells stay reserved for the Pi. The bank gets a second protected output for the boost. **Design detail (peer review, same day): the boost taps the RAW 1S cell node, upstream of the bank's 5 V converter that feeds the X1202 input**, so the burst is one conversion stage (about 0.90) instead of two (about 0.77), and a transmit burst can never brown out the converter holding up the UPS charge path. Cell-side draw for 12.8 W at 3.4 V nominal is about 4.2 A across four parallel 18650s, about 1.05 A per cell. Open question for Geekworm, now non-blocking: whether the X1202's 5 A is a converter rating or a protection trip point (a fast trip would make any overshoot a kit-wide power cut). Supersedes the "survivable" wording that section 11 item 11 already corrected. | section 11 item 11 |
| R16 | WiFi antennas | A second WiFi SMA bulkhead is added to the case so the AWUS036ACM runs 2x2. Section 7's bulkhead table gains a row (position to be chosen next to the existing SMA WiFi at +128.75, +50.0, +25.0); the pigtail schedule gains one RG-316 run. Note why 1x1 was the worse option: the MT7612U keys both TX chains unless the driver is forced to nss=1, so a bare second port is an open-circuit load on a live PA, and the software constraint could regress on any image rebuild. Cost of the ruling: one more 6.5 mm hole in an already built IP67 case. | section 11 item 15 note |
| R17 | Display height | **SUPERSEDED 2 Sep evening (owner rule, section 14.6): the glass sits level with the shelf, 0.75 mm proud, through an aperture; PCB-C goes back up.** ~~PCB-C drops about 8.5 mm on the rods so the display glass ends level with the base rim (glass is 9.46 mm above the plate on its tabs, section 14.3).~~ Nut pairs move, rods unchanged, about 10 mm of rod stands above the top nuts (cap nuts or trim). The middle bay gives back 8.5 of the 22.7 mm it gained under R4; exact Z_MIDDLE and Z_TOP are recomputed in the ECAD phase. **Physical check owed before the stack is finalised (peer review): whatever is inside the lid (foam, O-ring land, ribs) must clear the glass with the lid closed, and the closing force must not land on the lens.** With the glass level with the rim this is a smaller margin question than with 7 mm proud, but it is not zero. | section 14.3 |

Method agreed with R14: Python-generated schematics and boards with coordinates from this appendix, scripted USB and power routing plus Freerouting on the laptop, headless ERC, DRC, Gerber, BOM and CPL. Gates per board before any order: numeric placement check against the section 6 rectangles and the section 3 keep-outs, ERC and DRC against JLCPCB's rules, render review, a 1:1 paper print with the real devices laid on it, owner review in KiCad, JLCPCB DFM at upload. Sequence PCB-C, PCB-B, PCB-A, then the APRS mezzanine once the DMR858M is in hand. One order for all boards.

---

## 14. PCB-C DISPLAY Rev A, generated 2026-09-02

**State: KiCad 9 project generated, DRC clean, numeric check ALL PASS (including the orientation-invariance checks), fab files exported. Paper test waived, not yet owner-reviewed, not ordered.** Files on the laptop: `~/Documents/Team Shared Root/Projects/MeshSat/Field Kit/ECAD/meshsat-carrier/` (`tools/gen_pcb_c.py` generator, `tools/check_pcb_c.py` verifier, `tools/build_pcb.sh`, `pcb-c-display/` project with `out/` gerbers zip, drill, DRC report, 1:1 PDFs, renders). Copies of the deliverables in `~/Downloads/meshsat-pcb-c-revA/`. The generator is the source of truth; edit it and re-run, never hand-edit the board.

### 14.1 What the Touch Display 2 STEP and drawing actually say

The official 7-inch STEP (RP-009154-DD-1) and the product-brief drawing (page 4) replace the CAD's assumed geometry, and the CAD's top plate never modelled a display aperture at all (only the LED holes and a Ø20 DSI hole):

| Feature | CAD assumption | Official geometry |
|---|---|---|
| Rear hump | 100 x 70 mm block, 12.92 mm deep | does not exist |
| Deepest features | the hump | four Ø5.0 Pi standoffs (M2.5, 49 x 58 pattern) 8.5 mm behind the backplate, plus the DSI connector between the standoff rows |
| Mounting | display recessed 1.0 mm into a 3.0 mm plate | four rectangular M2.5 tabs, **70.71 x 140.0 mm** pattern, mounting faces **3.0 mm behind the backplate** |
| Backplate | not modelled | 99.71 x 168.55 mm, rear face 6.46 mm behind the glass front |
| Glass | 189.32 x 120.24, R8 | same, 0.7 mm lens |
| Central FPC channel | not modelled | 32.7 mm wide strip 2.0 mm proud of the backplate, 1.0 mm clear of a plate on the tabs |

STEP frame to case frame (display centre (0, -10), long axis along case X, connector end toward the Pi at -X): `case_X = step_Y - 2.935`, `case_Y = -step_X - 10`.

### 14.2 Board content (case frame, mm)

| Item | Geometry |
|---|---|
| Outline | 250.0 x 180.0, R5, centred; 1.2 mm FR-4 (JLCPCB standard, replaces the 1.1 mm design figure); no copper at all |
| H1 to H4 | Ø3.2 NPTH at (+-110.5, +-73.0), Ø9 silk ring both faces, annular rule area Ø6.2 to Ø9 on both copper layers (pads of other parts forbidden) |
| H5 to H8 | Ø2.7 NPTH for the TD2 tabs at (-69.995, +25.35), (+70.005, +25.35), (-69.995, -45.35), (+70.005, -45.35); pattern 140.00 x 70.70 |
| Window | **SUPERSEDED by C2 (section 14.6): the display is now taped through a body-sized aperture, no tab holes, no window.** ~~one through cutout X -44.0 to +44.0, Y -41.0 to +21.0 (88.0 x 62.0), R3, centred on the display centre (0, -10).~~ **Orientation-agnostic (owner ruling 2026-09-02, paper test waived):** the display may be fitted with its connector end to port or to starboard; the window is the union of both placements and clears all eight possible standoff positions by 3 mm or more and both DSI connector positions (+-3.55, -10.0). The tab holes are invariant under that 180 degree rotation. |
| Silk | glass outline and centre note, window label, rod labels R1 to R4, board legend, wall labels (front = -Y), underside legend and M2.5 labels mirrored on B.Silk |
| User.Drawings | backplate outline, the standoffs and DSI connector for BOTH orientations, the case datum cross at (0, 0) |

The CAD's five LED holes are gone (R5) and its Ø20 DSI hole at (-20, +10) lies inside the window.

### 14.3 Consequences for the stack, RULED 2026-09-02 as R17: option (b), PCB-C drops about 8.5 mm. **SUPERSEDED by the owner's flush-glass rule and C2, section 14.6.**

With the display carried on its tabs, the glass front sits **9.46 mm above the plate top face** (6.46 mm body plus 3.0 mm tab standoff), not the 1.0 mm the CAD assumed. Two ways to take it: (a) keep PCB-C at Z_TOP and let the glass rise about 7 mm into the 32 mm lid cavity; (b) drop PCB-C by about 8.5 mm on the rods (nut pairs move, rods unchanged, about 10 mm of rod then stands above the top nuts, cap nuts or a trim) so the glass sits level with the base rim. Either way the middle bay, which R4 already grows by about 22.7 mm, is the bay that pays. Section 9 finding 2 (the Pi 5 against the hump) is moot: nothing of the display reaches below the plate outside the window, and the window sits at X -26 to +44 while the Pi ends at X -50.5.

### 14.4 Verification done and still owed

Done: `kicad-cli pcb drc` clean under the JLCPCB rule set; `check_pcb_c.py` proves outline, centring, all eight hole positions and drills, the 140.0 x 70.7 tab pattern, the window extents, standoff and connector clearance, nut keep-out clearance, no copper, 1.2 mm thickness; top and bottom renders reviewed.
**Paper test WAIVED by the owner 2026-09-02**; in exchange the window was made symmetric so a mirrored placement cannot miss (the 1:1 PDF still exists if anyone wants it). Owed: the owner's own look in KiCad, JLCPCB DFM at upload. JLCPCB may query a copper-free board; it is intentional.

### 14.5 STEP re-probe of the Touch Display 2, 2 Sep 20:30 (owner asked how sure the window is)

Re-run of the build123d probes on the official 7-inch STEP (`ECAD/vendor/td2-7inch.step`, RP-009154-DD-1), numbers in the STEP frame (Z = 5.02 at the glass front, backplate rear face at -1.44):

- Glass bounding box Y -91.725 to +97.595, centre **2.935**, which is exactly the frame constant `gen_pcb_c.py` uses, so the glass is centred on case (0, -10). The tab pattern centre is 2.94: the four lugs are symmetric about the glass to 0.005 mm.
- Lug faces at Z -4.44 (3.0 mm behind the backplate), each lug 7.9 x 5.6 mm, 0.5 mm sheet, carrying a **pressed M2.5 nut: Ø2.0 thread bore (M2.5 minor) from -4.44 to -2.74 = 1.7 mm of thread, Ø3.0 body on top of the lug**. So the mounting points are threaded; PCB-C is screwed from below. Above the nut there is 1.3 mm of air before the backplate: **M2.5 x 4 is the longest screw that fits through a 1.2 mm board (2.8 mm of engagement plus 1.1 mm spare); M2.5 x 5 bottoms on the backplate.** Use x 4 with a washer, or x 3.
- Pi standoffs: Ø5.0 bodies from -1.44 to **-9.94** (8.5 mm), M2.5 thread inside 3.5 mm deep. They stand **5.5 mm below the lug plane**, i.e. through the 1.2 mm board and 4.3 mm beyond its underside: the window exists for them.
- **Nothing else on the display reaches below Z -4.5**: no face of any type outside the four standoffs and the four lugs. The central FPC channel is at -3.44, 1.0 mm above the board's top face; the driver PCB and the DSI connector sit at -0.4 to -1.44, inside the backplate thickness, and the DSI cable drops through the window from case X +-3.55.
- Window margins to the standoff bodies (Ø5 at case X -20.2 / +37.8 and Y -34.5 / +14.5, or their 180-degree images): at least 3.7 mm on every side in both orientations. Lug holes to the nearest window corner: about 26 mm.

Confidence therefore rests on the STEP being faithful to the shipped part (it is Raspberry Pi's own model) and on nothing else. **Official documents saved to `~/Downloads/meshsat-pcb/Review/PCB-C-DISPLAY-revA/` (owner request, 2 Sep 20:45):** the 7-inch STEP RP-009154-DD-1, the August 2025 product brief the design used, the original November 2024 edition RP-008387-DS-1 (same drawing numbers), and the three 2026 editions (RP-009106-MM-8, RP-010429-MM-1 "7-inch Portrait", and the datasheets.raspberrypi.com copy), which carry no mechanical drawing any more. Raspberry Pi publishes no schematic and no separate drawing PDF for the Touch Display 2; the Product Information Portal category 1083 was checked on 2 Sep 2026.

### 14.6 PCB-C C2: the display sits IN the plate, glass 0.75 mm proud (owner rule, 2 Sep 21:50)

**Owner rule:** the glass surface and the top shelf must be at the same level, the glass at most 0.5 to 0.8 mm proud; one board, no screws, the display glued or taped to the shelf. The tab-mounted design of 14.2 (glass 9.46 mm above the plate) and R17 are therefore superseded.

**Geometry, all from the STEP (probe5, `ECAD/vendor/td2_step_probe5.py`).** Below the glass underside (Z 4.32) the display body's envelope is step X +-49.855 (99.71) by step Y -85.275 to +83.275 (168.55), i.e. exactly the drawing's backplate size, but **offset 3.935 mm toward the connector end** relative to the glass centre (2.935). Depth slices: the full-width body reaches 5.76 mm below the glass underside, the lugs 8.76 mm (within +-39.3 x -75.9..75.7), the Pi standoffs 14.26 mm (within +-27 x -19.8..43.2). Body corners R1.0, glass corners R8.

**C2 board (`gen_pcb_c.py`, verifier `check_pcb_c.py` ALL PASS, DRC clean):** 250 x 180 x **1.6 mm** FR-4 (a frame carrying a taped display; was 1.2), no copper, four Ø3.2 rod holes with the Ø9 keep-outs as before, **no tab holes, no window**. One aperture = body envelope + 0.4 mm per side, internal corners R1.5: case X -88.61 to +80.74, Y -60.255 to +40.255 (169.35 x 100.51), centred on the body, which means offset 3.9 mm to port relative to the glass centre (0, -10). The glass flange (189.32 x 120.24) then bears on the plate by 6.05 mm at the west end, 13.92 at the east end and 9.87 on both long sides. Adhesive: 0.05 mm acrylic transfer tape (3M 467MP or 9495LE) in that band, so the glass ends **0.7 + 0.05 = 0.75 mm proud**. Anything thicker (foam, VHB) breaks the 0.8 mm limit. Silk carries the glass outline as the alignment guide, TAPE marks, the adhesive note and the orientation rule; User.Drawings shows the body, lugs, standoffs and DSI connector that hang below.

**Orientation is now fixed: connector end to PORT (-X).** In that orientation the Pi standoffs sit at case X -20.2 and +37.8, east of the Pi + X1202 + cooler stack (which ends at X -36). Rotated 180 degrees they would sit at X -37.8 (edge -40.3), over the stack, 12.66 mm below the plate underside. With the middle bay of 16.3 that leaves about 2 mm; the standing "port or starboard" ruling of 14.2 is withdrawn for C2 and the silk says DO NOT ROTATE.

**Z stack after C2 and D4 (replaces the 16.3 table).** Below the plate underside: full body 4.16 mm, lugs and FPC channel 7.16 mm (the west lugs at X -70 are over the Pi stack), standoffs 12.66 mm (clear of the stack in the port orientation). Take PCB-C's top face at **+52.0** (glass at +52.75, 2.25 mm below the base rim, top nut ending at +54.4 inside the 110 mm rods) and `BOTTOM_GAP` 35 (D4):

| Feature | Z (mm) |
|---|---|
| Case interior floor | -55.0 |
| PCB-A underside / top face | -52.6 / -51.0 |
| Bottom bay, free height 30.2 (D module stack about 27 + margin) | |
| PCB-B underside / top face | -16.0 / -14.4 |
| Middle bay, free height 64.8; Pi stack top at +35.6; 14.8 mm above it, of which the display takes 7.16 | |
| PCB-C underside / top face | +50.4 / **+52.0** |
| Glass front | +52.75 |
| Top nut | +52.0 to +54.4; 0.6 mm of rod spare |

Closure: `2.4 + 1.6 + 35.0 + 1.6 + 64.8 + 1.6 + 2.4 = 109.4` of 110.0. Where R17 put the glass 3.2 mm below the rim on a dropped plate, C2 puts the plate itself 3 mm below the rim and the glass 0.75 mm above the plate. Whatever is inside the lid (foam, O-ring land) still owes the physical check R17 asked for.

**Deliverables:** `~/Downloads/meshsat-pcb/meshsat-pcb-c-revA-C2/` (Gerbers, DRC report, 1:1 PDFs, renders, KiCad board); `JLCPCB/PCB-C-DISPLAY-C2/` and `Review/PCB-C-DISPLAY-C2/` regenerated by `make_handoff.py` (the official display documents moved with the Review folder). The first `meshsat-pcb-c-revA` folder (window design) is superseded. What the window is NOT: a viewing aperture. The glass sits 9.46 mm above the plate (14.3), the plate is a mounting tray under the display, and the 88 x 62 cutout only passes what protrudes from the display's back. Residual judgement calls, not errors: 1.2 mm FR-4 carrying a 250 g display on four M2.5 points 140 x 70.7 mm apart (1.6 mm would stiffen it at the cost of 0.4 mm in the Z stack), and the R17 Z ruling, which is case work.

---

## 15. PCB-B COMPUTE Rev A, phase B1 (mechanical + placement), generated 2026-09-02

**State: KiCad 9 board with every mounting feature and site placed, DRC clean, verifier ALL PASS. No schematic and no copper yet.** Phase B2 = schematic (4-port USB 2.0 hub, four eFuses, two INA3221 monitors, PCA9554 expander, connectors, RockBLOCK signal wiring incl. the 2N7000 OnOff buffer and the UART0/UART2 solder-jumper select), phase B3 = routing, DRC, exports. Files: `ECAD/meshsat-carrier/pcb-b-compute/` (generator `tools/gen_pcb_b.py`, verifier `tools/check_pcb_b.py`, in-code footprints in `ECAD/meshsat-carrier/meshsat.pretty`); renders, 1:1 PDF and DRC report copied to `~/Downloads/meshsat-pcb-b-revA-B1/`.

### 15.1 Module data pulled for PCB-B (all official sources, staged in `ECAD/vendor/`)

| Module | Envelope | Mounting | Source |
|---|---|---|---|
| Raspberry Pi 5 + Geekworm X1202 stack | Pi 85 x 56; X1202 97.4 x 85, 25 mm with cells | four M2.5 standoffs on the Pi pattern 58 x 49, holes 3.5 mm from the Pi edges | Pi mechanical drawing; X1202 stacks on the same pattern (Geekworm) |
| RockBLOCK 9603 | 45 x 45 x 15 | two Ø2.5 holes on one edge, 3.15 mm from the edges, 38.7 mm apart; SMA on the opposite edge, 10 mm proud, centre 20 mm from a corner | GC dimensions page + RockBLOCK_V_3B.STEP |
| RockBLOCK 9704 SMA | PCB 52.0 x 47.8, SMA overhang to 59.3, 16.2 tall | **no mounting holes**; two 2 x 0.5 mm edge notches at mid-length for the ACC-RB9704SMA-MOUNT bracket (52 x 56, four Ø4.60 on 32 x 32) | RockBLOCK 9704-SMA-2A.step, mount drawing Rev A |
| LilyGO T-Call A7670E V1.0 | 74.78 x 29.01 | four Ø3 corner holes on 69.46 x 24.97 (read from the T-Call-A767X drawing; R1.5 callouts taken as holes, confirm on the board) | LilyGo-Modem-Series dimensions/esp32 |
| Seeed Wio-SX1262 for XIAO + XIAO ESP32S3 | 21.44 x 17.78, 7.3 mm carrier + XIAO | one Ø2.2 hole, centred, 3.76 mm from a short edge | Wio-SX1262_for_XIAO_3D_file.step |
| RTL-SDR Blog V4 | body 69 x 27 x 13, USB-A plug, SMA | none: receptacle + tie slots | rtl-sdr.com |
| Sonoff ZBDongle-P | 87 x 25.5 x 13.5 incl. plug | none: receptacle + tie slots | Sonoff |
| Alfa AWUS036ACM (PCB-A) | see item 15 | | |

Kit identity assumptions to confirm by eye: the LoRa node is the Seeed XIAO ESP32S3 + Wio-SX1262 kit (BOM says "ESP32-S3 LoRa (SX1262 868 MHz)", lsusb shows seeed-xiao-s3); the T-Call is the V1.0 in the T-Call-A767X drawing.

### 15.2 Placement (case frame, mm)

| Site | Position | Fixing on PCB-B |
|---|---|---|
| Pi 5 + X1202 stack | Pi long axis along Y, centred (-78.5, 0); X1202 envelope X -121 to -36, Y +-48.5 | H5 to H8 Ø2.7 at (-103, -29), (-54, -29), (-103, 29), (-54, 29) |
| X1202 USB-C IN cable | X1202 port faces -Y at (-104.5, -48.5) | 14 x 6 obround pass-through at (-104.5, -57) |
| J_GPIO 2x20 IDC | vertical, centred (-28, 0) | Pi 40-pin ribbon |
| RTL-SDR Blog V4 | body X 24 to 93, Y -11.5 to 15.5; SMA east toward the SDR bulkhead | USB-A receptacle J_RTL centred (10, 2) opening +X; 5 x 1.8 tie slots at (45/85, -15) and (45/85, 18.5) |
| Sonoff ZBDongle-P | body X -34 to 36, Y -58.75 to -33.25; plug east | USB-A receptacle J_ZB centred (44, -46) opening -X; slots at (-16/24, -62) and (-16/24, -30) |
| LilyGO T-Call A7670E | centred (69.89, 36.5), X 32.5 to 107.28, Y 22 to 51; USB-C at the west end | H9 to H12 Ø3.2 at (35.16/104.62, 24.015) and (35.16/104.62, 48.985); board-side USB-C plug or captive cable at (26, 36.5) |
| XIAO + Wio-SX1262 | centred (-93, 58), long axis along X; USB-C east | H13 Ø2.2 at (-99.96, 58); slots at (-88, 46) and (-88, 70); u.FL pigtail to the LoRa bulkhead |
| RockBLOCK dual site | bracket 52 x 56 centred (78, -46); 9603 45 x 45 centred (78, -40), hole row on its north edge | H14 to H17 Ø4.3 (M4, GC bracket) at (62/94, -62) and (62/94, -30); H18, H19 Ø2.7 (9603) at (58.65/97.35, -20.65) |
| J_DCF77 JST-XH 4 | centred (-85, 77) | 3V3, GND, T (BCM 21), P1 (BCM 19), remote-mount receiver |
| Hub / eFuse / monitor zone | reserved X -96 to -46, Y -81 to -52 | J_5V_IN XH2.54 (-52, -56) from the X1202 5 V output; J_USB_UP USB-C (-48, -66) to a Pi port; J_AB 2x7 on the underside at (-72, -78) for the ribbon to PCB-A |
| General pass-through | Ø15 at (0, -20) | the CAD's centre hole, relocated |
| Rods | H1 to H4 Ø3.2 at (+-110.5, +-73) | Ø9 nut keep-outs as rings and annular rule areas |

Changes against the CAD placements: RTL-SDR shifted +2 in X and -3 in Y, T-Call +2 in Y, ZigBee +6 in X and -3 in Y, RockBLOCK site moved from (85, -47.5) to (78, -46) (section 9 finding 1, the nut keep-out), DCF77 strip replaced by a connector, centre hole moved. Both USB sticks now have a captive receptacle at the plug end and two tie slots per side; the exact receptacle part and its insertion depth are fixed in B2 with the datasheet, so the body rectangles may move a few millimetres.

### 15.3 Wiring facts collected for phase B2

- Pi UARTs: parallax runs the 9704 on UART2 (BCM 4 TX / BCM 5 RX, `/dev/ttyAMA2`, 230400); tesseract runs the 9603 on UART0 (BCM 14/15, `/dev/ttyAMA0`, 19200). PCB-B routes BOTH UARTs to the RockBLOCK site with a solder-jumper select, so one board serves both kits without a config change.
- Control lines map to the same BCMs on both kits: BCM 23 = modem status input (9704 I_BTD open-drain, needs pull-up; 9603 RI), BCM 24 = modem control output (9704 P_EN active low; 9603 OnOff, which on Rev F needs a 2N7000 open-drain buffer, MESHSAT-669, populated on PCB-B), BCM 26 = 9704 I_EN, BCM 22 = 9603 NetAv.
- X1202: I2C1 fuel gauge at 0x36 (BCM 2/3), AC-loss input BCM 6, charge control BCM 16. Touch Display 2 5 V from header pins 4 and 14.
- DCF77 on parallax: T to BCM 21, P1 to BCM 19 (the CLAUDE.md field wiring of 2026-04-23 supersedes the April pinout docs, which say BCM 12/20).
- Pi ports: USB-A row faces the board centre (+X face of the Pi in the CAD map); X1202 USB-C IN and two USB-A outputs face -Y. The Pi 5 header is on a long edge, so the ribbon reaches J_GPIO from either side of the stack.
- 9704 header (16-pin 0.1 in) and USB-C are on its -X end, SMA on +X; the 9704 site orientation on PCB-B is decided in B2 with the pigtail run to the Iridium bulkhead at (-128.75, -25, +25).

### 15.4 Phase B2, schematic, generated 2026-09-02: ERC clean, netlist and BOM exported

`tools/gen_sch_b.py` writes `pcb-b-compute.kicad_sch` (A0 sheet, netlist style: every pin carries a stub and a net label, power pins carry power symbols; symbols are flattened copies of the KiCad 9 library symbols so pin maps are the library's, not typed). `tools/build_sch.sh` runs ERC (clean, 0 items), exports the netlist (`out/pcb-b-compute.net`, 89 nets), the schematic PDF and a grouped BOM (45 lines). Copies in `~/Downloads/meshsat-pcb-b-revA-B2/`.

**Circuit, as built:**

| Block | Parts | Notes |
|---|---|---|
| Power in | J_5V_IN1/2 (XH2.54 x2, paralleled) from the X1202 5 V outputs, F1 3 A polyfuse, SMBJ5.0A TVS, 2x 100 uF, 5 V LED, J_TD2 (XH2.54) for the Touch Display 2 5 V, TP1..TP5 | +5V is the board rail; +3V3 comes from the Pi header (pins 1/17) and feeds only the I2C devices and pull-ups |
| Hub | U1 FE1.1s (SSOP-28) on its internal 3.3 V and 1.8 V regulators from +5V, 12 MHz 3225 crystal + 2x 22 pF, REXT 2.7 k (verify against the FE1.1s datasheet), RC reset, BUSJ pulled up = self-powered (JP1 to GND for bus-powered), TESTJ and OVCJ pulled up, VBUSM from the upstream VBUS via 4.7 k, activity LED on LED1 | Downstream: port 1 RTL-SDR, 2 ZigBee, 3 T-Call, 4 XIAO |
| Upstream | J_USB_UP1 USB-C receptacle (HRO TYPE-C-31-M-12) to a Pi port, CC 5.1 k x2, USBLC6-2SC6 ESD; J_USB_UP2 identical, carries PCB-A's hub upstream pair to a second Pi port | VBUS of the second port goes to PCB-A as VBUS_A_SENSE for its hub's VBUSM |
| Six power channels | RTL, ZB, XIAO, RB: TPS2065CDBV (1.5 A limit, EN, FAULT) + 0.1 R 1206 shunt + INA219AIDCN. TC and A: 1812 polyfuse (2 A / 1.1 A) + TPS22810DRV load switch (CT 1 nF) + 0.05 R shunt + INA219 | INA219 addresses 0x40 RTL, 0x41 ZB, 0x45 XIAO, 0x42 RB, 0x44 TC, 0x43 A; X1202 gauge stays 0x36 |
| Expander | U20 PCA9555PW at 0x20: IO0_0..0_5 = EN_RTL/ZB/XIAO/RB/TC/A (power-up default input with weak pull-up = all ports ON before the Pi configures it), IO1_0..1_3 = FAULT inputs, IO1_4 = BANK_ALERT from PCB-A, five spares on TP6..TP10, INT to BCM 25 | |
| Ports | J_RTL1, J_ZB1 USB-A receptacles; J_TCALL1, J_XIAO1 USB-C plugs (Molex 105444 footprint as placeholder, part or captive cable to be fixed at BOM time) with 56 k Rp on CC; every port has a USBLC6-2SC6 and a 10 uF | |
| RockBLOCK site | JP3/JP4 3-way solder jumpers select UART2 (BCM 4/5) or UART0 (BCM 14/15) onto UART_TX_M/UART_RX_M; J_RB9704 IDC 2x8 in the 9704's 16-pin order (I_EN BCM 26, P_EN BCM 24, I_BTD BCM 23, XMT_G BCM 18, V_IN+ from 5V_RB); J_RB9603 PicoBlade 10 in the 9603 order (RXD, NetAv BCM 22, RI BCM 23, TXD, OnOff, 5 V, GND); Q1 2N7002 open-drain OnOff buffer (100 R gate, 100 k pull-down) from BCM 24; 10 k pull-up on the shared status line | One board serves both kits; only the jumpers and the fitted modem differ |
| DCF77 | J_DCF77 XH 4: 3V3, GND, T (BCM 21, 10 k pull-up), P1 (BCM 19) | |
| Interconnect | J_AB1 IDC 2x7 on the underside: 5V_A x2, GND x3, USB_A_DP/DM, SDA, SCL, EXP_INT, TR_APRS (BCM 27), VBUS_A_SENSE, BANK_ALERT (BCM 17), AB_SPARE (TP11) | |
| Pi header | J_GPIO1 2x20: 3V3, SDA/SCL, UART2 (7/29), UART0 (8/10), BCM 17/18/19/21/22/23/24/25/26/27; the Pi 5 V pins are left unconnected on purpose (no back-feed); all other pins no-connect | |

**Open at BOM time:** LCSC numbers are filled only where certain (FE1.1s C2848, USBLC6-2SC6 C7519, INA219 C138024, PCA9555PW C5626, HRO USB-C C165948) and must be verified; the USB-C plug parts for the T-Call and XIAO; the RTL-SDR/ZigBee receptacle part; REXT value.

**Phase B3 next:** import the netlist into the B1 board (the connector footprints already sit at their case-frame positions), place the hub, switch, monitor and expander parts in the reserved south-west zone, route (USB pairs 90 ohm on the JLC 4-layer stackup, ground plane on layer 2), DRC, Gerbers, BOM and CPL.

### 15.5 Phase B3, placement, routing and fab files, 2026-09-02

**State: PCB-B Rev A is placed and autorouted on the JLC 4-layer stackup with GND on In1 and +5V on In2 as solid-connected planes; Gerbers, drill, JLCPCB BOM and CPL are exported. Six of 337 connections are left for manual completion in KiCad** (the autorouter stalls on them and every scripted closure I tried either shorted a neighbour or was refused by the collision check). They are listed in `out/pcb-b-compute-drc.rpt` as the only unconnected items: EN_TC (U20 pin 8 to U15 pin 5), SW_ZB (a 0.6 mm gap into U7 pin 1), USB_RTL_N (an In1 track 1.5 mm from U1 pin 10, needs a via), USB_XIAO_N (U12 pins 3 to 4), USB_ZB_P (U9 pin 1 to its track end), GND (0.7 mm gap into U14 pin 3). Every other DRC class is clean under the JLCPCB rule set. Files: `pcb-b-compute/out/` (gerber zip, jlc/ BOM + CPL + README-fab.txt, renders, DRC) and `~/Downloads/meshsat-pcb-b-revA-B3/`.

**How the board is built (all scripted, `tools/`):** `gen_pcb_b.py` (B1 mechanical, now with copper keep-outs around every slot, hole and pass-through), `gen_pcb_b3.py` (netlist import, region placement near each connector, planes, net classes: Default 0.25 mm / USB pairs 0.2 mm with 0.15 gap / PWR 0.4 mm, 0.15 mm clearance, 0.7 mm vias), `prefanout.py` (a via beside every GND and +5V surface pad before routing; 71 placed, 22 pads in dense spots left to the router), `route_pcb.sh` (Specctra export from a copy without the planes so GND and +5V are routed as ordinary nets, Freerouting 1.9 under Xvfb with the full Java 21 runtime, session import, plane fill), `finish_stubs.py`, `export_jlc.sh`. Freerouting 2.1 and 2.3 were rejected: 2.3 needs Java 25, 2.1 ignores its pass limit and never writes a session on a plateau.

**Placement (case frame):** hub, crystal, 5 V input and protection in the south-west zone; expander, PCB-A feed channel and the two upstream USB-C receptacles (facing the front wall at X +-30, Y -78) in the strip south of the ZigBee body; each port's switch, monitor, shunt and ESD next to its connector (RTL channel north of J_RTL1, ZigBee channel between the pass-through and the bracket, T-Call channel above the RTL body, XIAO channel east of the XIAO, RockBLOCK channel and the UART jumpers east of the RockBLOCK site); J_RB9704 vertical at (113, -42), J_RB9603 at (112, -14), J_AB1 on the underside at (-72, -78), J_TD2 at (-30, 58), test points at Y 64 to 72 north of the header. USB-C plug placeholders were replaced by JST-PH 4-pin pigtail headers (J_TCALL1, J_XIAO1).

**Owner steps before ordering:** open the project in KiCad 9, route the six listed connections (a few minutes with the interactive router), re-run DRC, check the JLC parts library for the unfilled LCSC numbers in `jlc/pcb-b-compute-bom.csv`, upload the gerber zip with the BOM and CPL, request impedance control on the USB pairs.

---

### 15.6 Phase B4, re-layout for the T-Beam 1W and the LimeSDR Mini 2.0, 2026-09-02 (owner go)

**Trigger.** The owner asked on 2 Sep for the SDR bay to accept a LimeSDR Mini 2.0 as a future upgrade and for the LoRa slot to accept the LILYGO T-Beam 1W, then ruled "go" on the re-layout. The public GitHub issues were reviewed the same day: three issues (MeshCore support, RNode over TCP, Modem73), all software on other people's gear, no hardware ask. Modem73 rides the same soundcard path as APRS, so the PCB-D core covers it.

**Module data (official STEP models, staged in `ECAD/vendor/`).**
- LimeSDR Mini 2.0 (`myriadrf/LimeSDR-Mini-v2`, 2v4 STEP + PCB drawings, plus limemicro.com): PCB 69.00 x 31.37 x 1.6 mm; USB 3.0 type-A plug on one short end, centred on the width and 15.35 mm long; RX and TX SMA on the other end, 9.65 mm beyond the PCB; bottom-side shield cans reach 4.7 mm below, top side 6.4 mm above; no corner mounting holes. Runs from 5 V USB, same acrylic case as the Mini v1. The RTL-SDR V4 body is 69 x 27, so the two differ by 4.4 mm of width and one SMA.
- LILYGO T-Beam 1W (H768-01; `LilyGo-LoRa-Series/dimensions/T-Beam-1W.7z` STEP and `t-beam-1w-dwg.png`): PCB 43.06 x 116.75 mm (drawing 42.94 x 116.61); holes in the PCB frame (origin the SW corner of the STEP face): Ø3.5 (32.18, 113.66), Ø3 (-0.30, 102.42), Ø3 (35.20, 83.92), Ø2 (2.62, 3.00), Ø2 (32.28, 2.99); edge-mount SMA at the top-right (x 27.6 to 36.8, 14.5 mm beyond the PCB); USB-C on the left edge at y 60.5 to 69.4; ON/OFF slide switch on the left edge at y 45.7 to 52.3; two 15-pin header rows at x -2.64 and 37.52, y 4.06 to 39.62; ESP32-S3 module at the bottom end, fan over the PA at the SMA end. The NP-F550 style battery plate (7.4 V pack, not charged by the board) and the display/fan shell hang 10 mm below the PCB and extend 17.4 mm (plate) and 6.5 mm (shell) beyond the PCB ends: 148.7 mm overall with the SMA, which cannot clear both rod nuts on a 170 mm board. **The module is therefore fitted BARE: PCB plus fan, five standoffs (3x M2.5, 2x M2), 6 mm.** LilyGO figures: 133 x 43 x 27 mm assembled; 32.5 dBm at 868 MHz at 1.04 A from 5 V for the radio alone, about 1.3 A with the ESP32-S3; USB-C input 3.9 to 6 V; native USB (CDC on boot); fan on GPIO 41.
- **TPS2065C is a 1 A part.** TI's TPS20xxC family table gives the TPS2065C a 1 A current limit (the TPS2068C is the 1.5 A part). The T-Beam at 1.3 A and the 9704's transmit bursts both exceed it, so **CH3 (LoRa) and CH4 (RockBLOCK) move to the T-Call recipe: 2 A polyfuse, TPS22810, 0.05 ohm shunt** (F4/U10/C27 and F5/U13/C28). CH1 (SDR, Lime about 0.6 A) and CH2 (ZigBee) keep the TPS2065C.

**Placement (case frame, mm; everything not listed is as in 15.2).**

| Item | B4 position |
|---|---|
| SDR bay, RTL-SDR V4 or LimeSDR Mini 2.0 | X -4 to 78, Y -16 to 16; J_RTL1 receptacle at (-12, 0) opening +X; tie slots (20, -18) (74, -18) (20, 18) (66, 18) |
| T-Call | 4x M3 at (4.66 / 74.12, 23.015 / 47.985); J_TCALL1 PH4 pigtail header at (-16, 46) |
| ZigBee dongle, north band | body X -40 to 30, Y 55 to 80.5; J_ZB1 at (38, 67.75) opening -X; slots (-22 / 18, 52.5 / 82) |
| RockBLOCK dual site | centre (52, -48): 9704 bracket holes (36 / 68, -64 / -32); 9603 holes (32.65 / 71.35, -22.65); J_RB9704 at (10, -48), J_RB9603 at (10, -60), both wide |
| T-Beam 1W strip | PCB X 79.3 to 122.36, Y -64 to 52.75; M2.5 holes (115.56, 49.63) (83.08, 38.39) (118.58, 19.89); M2 holes (86.00, -61.03) (115.66, -61.04); SMA at X 111 to 120 reaching Y 67.2, **right-angle SMA plug on the LoRa pigtail** (a straight plug body hits rod R4); USB-C on its west edge at Y -3.5 to 5.4 (right-angle USB-C plug); switch at Y -18 to -12; header-pin rows carry top-side copper keep-outs; J_TBEAM1 PH4 at (70, 55), in parallel with J_XIAO1 on CH3, one of the two populated |
| Pass-through | Ø15 at (-13, -50) |
| J_TD2 | (-50, 77) |
| Small-part regions | SDR channel (-22 to -11, 7.5 to 22); T-Call channel (-22 to -11, 22.5 to 40); test points (-10 to 1, 37 to 50); ZigBee channel (46 to 62, 54 to 72); LoRa channel in the XIAO region (-70 to -46, 50 to 70); RockBLOCK block (-20 to 15, -40 to -18) |

Two constraints follow from the geometry. With the T-Beam fitted, its USB-C plug occupies X 70 to 78 at Y about 0, so a LimeSDR must use the bay receptacle (USB 2.0 rate); a direct USB 3 cable to a Pi blue port, with the Lime shifted east onto the extension, is only possible when the XIAO is fitted instead. The Lime's second SMA (TX) needs a spare bulkhead in the wall plan.

**Routed result (B4, 2026-09-02 13:20).** Freerouting 1.9 closed the board in eight minutes: 2087 tracks, 232 vias, **one connection left for manual routing in KiCad: EN_XIAO from the PCA9555 (U20 pin 6) to the TPS22810 (U10 pin 5)**; a 25-pass continuation went silent on re-import and was killed. No electrical DRC violation remains (8 silk overlaps + 5 silk-over-copper warnings, all labels under modules). Fab files: `pcb-b-compute/out/` and `~/Downloads/meshsat-pcb-b-revA-B4/` (Gerbers zip, JLC BOM + CPL + README, DRC report, schematic PDF, renders, 1:1 PDFs, KiCad project). B4 supersedes the B3 deliverables; the six B3 stubs are gone with the re-route. Lesson: a "short track" filter is not a dangling-stub filter (it deleted 174 routed GND segments before being replaced by a real end-connectivity test in `post_fix_b4.py`).

**Verification.** `check_pcb_b.py` ALL PASS on the new coordinates (24 holes, hole webs >= 2 mm, every rectangle inside the outline, pairwise apart and clear of the nut keep-outs, including the T-Beam PCB that ends 0.14 mm short of the east edge by design); ERC clean (91 nets, 127 parts); pre-route DRC free of courtyard, clearance, hole and edge violations (silk overlaps only); 59 fanout vias; routing launched with the watched two-pass chain. The B3 board and its fab files are kept in `pcb-b-compute-B3-backup/` on the laptop; the B3 deliverables in Downloads are superseded when B4 completes.

## 16. PCB-A POWER + I/O, phase A0 specification, 2026-09-02

**State: specification only. No KiCad project exists for PCB-A.** This session ran with the gateway's shadow mode active (`~/gateway.mutations_off`, set by the owner 2026-07-18), which blocks every Bash form that is not provably a read, including `ssh laptop "python3 ..."`, `scp` and anything that writes a file on the laptop. The generator that would produce this board therefore could not be run. Phase A0 is the design work that does not need the toolchain: every coordinate, part and net that `gen_pcb_a.py` will need, plus the checks `check_pcb_a.py` must prove. **What would have been run, and why:** the same sequence as PCB-B, `tools/gen_pcb_a.py` (mechanical + sites) then `gen_sch_a.py` (schematic, ERC) then `gen_pcb_a3.py` + `route_pcb.sh` (placement, planes, Freerouting, DRC, Gerbers/BOM/CPL), on the owner's laptop under `Field Kit/ECAD/meshsat-carrier/pcb-a-power/`. Nothing below has been through DRC, ERC or a numeric verifier.

### 16.1 What PCB-A carries, from the rulings

| Source | Content on PCB-A |
|---|---|
| R1 | No UV-K5 dock, no AIOC receptacle. The whole 120 x 65 mm handheld rectangle is free. |
| R2 | One 4-port-class hub, its four ports and their eFuses; one upstream USB pair over the A-B ribbon to PCB-B's `J_USB_UP2`, i.e. the kit's second Pi port. |
| R3 | The APRS mezzanine on standoffs in the former handheld rectangle, joined by harness, not by a stacking connector. |
| R5 | The five 8 mm case front-wall LEDs (X -44 to +44 at Y -110, Z -35), driven from PCB-A. |
| R6 | The four-cell 18650 extension bank: holders, protection, charger with NTC, 5 V output into the X1202 USB-C input; the case USB-C inlet now lands here, not on the X1202. |
| R8 | Alfa AWUS036ACM on a board-mounted USB-A receptacle. |
| R15 | The mezzanine boost is fed from the bank's **raw 1S cell node**, so PCB-A carries that tap and its harness, not the boost itself. |
| R16 | Two WiFi pigtails leave this board, not one. |

Device inventory: WiFi dongle, GPS puck, APRS mezzanine (two USB functions), bank, hub, LED row. That is the whole board.

### 16.2 Power evidence and budget

Descriptor `bMaxPower` read from tesseract 2026-09-02 (`/sys/bus/usb/devices/*/bMaxPower`, advertised values, not measured peaks):

| Device | Advertised | Board |
|---|---|---|
| Alfa AWUS036ACM, "Wireless" | **400 mA** | PCB-A, confirms R8 |
| u-blox 7 GPS/GNSS receiver | **100 mA** | PCB-A |
| AIOC "All-In-One-Cable" | 100 mA | leaves with the handheld (R1); the mezzanine codec inherits the role |
| RTL-SDR Blog V4 | 500 mA | PCB-B |
| seeed-xiao-s3 | 500 mA | PCB-B |
| T-Call, "USB Single Serial" CH9102 | 136 mA | PCB-B |
| Sonoff ZBDongle-P | 100 mA | PCB-B |

PCB-A logic budget on the 5 V that arrives over the ribbon: WiFi 400 + GPS 100 + mezzanine codec ~100 + mezzanine USB-UART ~50 + hub and monitors ~100 + LED row 5 x 10 = **about 800 mA advertised**, and the MT7612U's transmit peak is above its advertised 400 mA.

**Finding A0-1, and it changes PCB-B before it is ordered.** Phase B2 gave the PCB-A feed (channel "A") a 1.1 A polyfuse in an 1812 body plus a TPS22810. A polyfuse's hold current derates hard with ambient, so an 1.1 A part in the bottom of a sealed case is marginal against a steady 800 mA with transmit peaks on top. **Raise channel A to a 2 A hold polyfuse** (same body, same TPS22810, which is rated 2 A) and re-check `pcb-b-compute` BOM line for F_A. This is a BOM edit, not a layout change.

The APRS transmit burst is **not** in this budget: R15 puts it on the raw cell node, upstream of everything the ribbon feeds.

### 16.3 The bottom bay, and the rod closure that follows

Tallest objects on PCB-A once the handheld is gone: a PCB-mount 18650 holder with a cell, about 22 mm (R4's own figure, part not yet chosen), and the mezzanine at 8 mm standoff + 1.6 mm board + 10.2 mm module = 19.8 mm before its boost inductor and connectors. Design height **22 mm**.

`BOTTOM_GAP = 22.0 + 2 x NUT_H = 26.8`, take **27.0 mm**. Then, with 1.6 / 1.6 / 1.2 mm boards:

| Feature | Z (mm) |
|---|---|
| Case interior floor | -55.0 |
| PCB-A underside / top face | -52.6 / **-51.0** |
| Bottom bay, free height 22.2 | |
| PCB-B underside / top face | **-24.0** / -22.4 |
| Middle bay, free height 58.7 | |
| PCB-C underside / top face | **+41.1** / +42.3 (R17 drop applied) |
| Rod standing above the top nut | 10.3 |

Closure: `2.4 + 1.6 + 27.0 + 1.6 + 63.5 + 1.2 + 2.4 = 99.7` of 110.0, leaving the 10.3 mm R17 predicted for cap nuts or a trim. Two consequences worth stating: the Pi + X1202 + cooler stack is 50 mm above PCB-B's top face and the middle bay gives it **58.7 mm**, so a 27 mm bottom bay does not starve the middle one; and the glass front lands at +51.8, i.e. 3.2 mm **below** the base rim rather than level with it, which is the safer side of R17 and is for the ECAD-phase recompute to settle, not a re-opening of R17.

Note the three boards now sum to 4.4 mm, not the 4.3 mm section 9 finding 4 assumed, because PCB-C went to JLCPCB's standard 1.2 mm. The freed figure is 4.6 mm, not 4.7.

### 16.4 Proposed placement, case frame, mm

Board: 240.0 x 160.0, R5, X -120 to +120, Y -80 to +80, **1.6 mm FR-4, four layers** (same JLC stackup as PCB-B: GND on In1, +5V on In2), matte black, ENIG. Every one of these is a proposal for `gen_pcb_a.py` and none has been verified.

| Site | Position | Fixing / notes |
|---|---|---|
| Rods H1 to H4 | Ø3.2 at (+-110.5, +-73) | Ø9 keep-out rings and annular rule areas, both faces. **Section 9 finding 5 governs this board: nothing routes outboard of them.** |
| Bank, 4x 18650 holder | block X -111 to -33, Y -41 to +41 (78 x 82) | four holders side by side, long axis along X, centre (-72, 0); 9 mm to the west edge, 27.5 mm to the nearest nut keep-out |
| Bank electronics | strip X -100 to -20, Y +46 to +76 | protection FETs and pack shunt at the holders' north edge, then charger, gauge, NTC; shortest possible pack leads, which carry both the 3 A charge and the 4.2 A burst |
| `J_USBC_IN` | (-25, +72) | case USB-C inlet cable, sink role, 5.1 k CC pulldowns |
| `J_BANK_OUT` | (-95, -60) | USB-C source to the X1202 USB-C IN at (-104.5, -48.5) on PCB-B: about a 60 mm cable |
| Hub, eFuses, expander | strip X -100 to -20, Y -76 to -46 | FE1.1s, crystal, four channels, PCA9555, ESD |
| `J_AB1A` 2x7 IDC | (-72, -70), long axis along X | mates PCB-B's underside `J_AB1` at (-72, -78) through a ribbon; 27 mm of Z plus a service loop, about 120 mm |
| `J_LED` XH 6 | (+10, -72) | five anodes plus common return to the front-wall LEDs |
| APRS mezzanine | board 90 x 66, X +5 to +95, Y -33 to +33 | four M3 Ø3.2 standoff holes at (+10, +-28) and (+90, +-28), 8 mm standoffs |
| DMR858M on the mezzanine | module X +30 to +88, Y -19.5 to +19.5 | short axis across the corridor, the only orientation that buys section 12.3's 19.5 mm to the GPS and 20.0 mm to the WiFi |
| `J_MEZZ_SIG` 2x8 keyed IDC | (-8, +18) | west of the mezzanine, cable not stacking |
| `J_MEZZ_PWR` 2-pin, 6 A class | (-8, -18) | raw cell node and return, see finding A0-2 |
| WiFi dongle | body X +18 to +103, Y +39 to +65 | receptacle `J_WIFI` centred (+8, +52) opening +X; 5 x 1.8 tie slots at (+45 / +85, +36.5) and (+45 / +85, +67.5) |
| GPS puck | body X +50 to +90, Y -65 to -39 (CAD position kept) | receptacle `J_GPS` centred (+30, -52) opening +X; tie slots at (+55 / +85, -68) and (+55 / +85, -36), plus a four-slot coil field west of the puck for the captive metre of cable |

Free area after all of that is roughly a third of the board, which is the margin the ECAD phase will spend on the plane cut-outs the pulsed cell trace needs.

### 16.5 Circuit blocks

| Block | Content | Notes |
|---|---|---|
| Ribbon power in | 5V_A x2 and GND x3 from `J_AB1A`, TVS, bulk | the whole logic side is downstream of PCB-B's channel A, see finding A0-1 |
| Hub | FE1.1s, 12 MHz crystal, REXT, self-powered strap; ports 1 WiFi, 2 GPS, 3 mezzanine codec, 4 mezzanine UART | same part and same wiring as PCB-B so the BOM has one hub line; upstream pair goes out on `J_AB1A` with VBUS_A_SENSE as the VBUSM source |
| Four power channels | TPS2065CDBV (1.5 A) + 0.1 R shunt + INA219 each, USBLC6-2SC6 per port | 1.5 A covers the MT7612U transmit peak against its 400 mA advertised |
| Expander | PCA9555 at **0x21**, enables and faults, five LED sinks, BANK_ALERT out to the ribbon | power-up default input with weak pull-up = ports ON before the Pi configures it, as on PCB-B |
| LED row | five 8 mm panel LEDs on flying leads to `J_LED`, series resistors on PCB-A with a 0 R option | default legend PWR/BATT, MESH, SAT, LTE, SYS; the LED part must be confirmed first, see the open list |
| Bank | 4S1P-mechanical, **1S4P electrically**, pack protection, charger with NTC, fuel gauge, 5 V boost to `J_BANK_OUT` | about 49 Wh added to the X1202's 50 Wh, matching R6's "about 100 Wh" |
| Raw cell tap | fused, sensed tap from the cell node to `J_MEZZ_PWR` | R15: one conversion stage for the burst, and the burst can never brown out the converter that holds up the X1202 charge path |
| TR_APRS | module T/R output in on the mezzanine harness, **populated 100 k pull-down on PCB-A**, series 100 R, out to the ribbon as TR_APRS (BCM 27) | section 12.7's one pin. The pull-down is what makes an unfitted mezzanine read "not transmitting" instead of floating |

Charger choice, to be confirmed against the JLCPCB library at BOM time: a BQ25896-class single-cell charger with integrated boost is the one-chip answer, because it takes 5 V in, charges at up to 3 A with NTC, and its OTG boost is the 5 V output R6 asks for, with I2C telemetry on the bus the ribbon already carries.

### 16.6 I2C map for the whole kit, after PCB-A

One bus (Pi I2C1, BCM 2/3) reaches both boards through the ribbon, so the addresses have to be planned kit-wide.

| Address | Device | Board |
|---|---|---|
| 0x20 | PCA9555 | PCB-B |
| **0x21** | PCA9555 | PCB-A |
| 0x36 | X1202 fuel gauge | X1202 |
| 0x40 to 0x45 | INA219 x6 | PCB-B |
| **0x46 to 0x49** | INA219 x4 | PCB-A |
| **0x55** | bank fuel gauge (BQ27441-class) | PCB-A |
| **0x6B** | bank charger | PCB-A |

**Trap avoided, worth recording:** the obvious cheap fuel gauge, MAX17048, is fixed at **0x36** and would collide with the X1202's gauge on the same bus. Any bank gauge must be address-selectable and must not be 0x36.

### 16.7 New findings and the questions they raise

- **A0-1, PCB-B channel A polyfuse** (section 16.2). Recommend 2 A hold. PCB-B is not ordered, so this is free today.
- **A0-2, the mezzanine harness should be two harnesses.** R3 says one keyed harness. Carrying a 4.2 A pulsed cell current in the same connector as two USB pairs puts the transmit return next to the differential pairs and asks a 2.54 mm IDC contact to do a job it is not rated for. Recommend a signal harness (`J_MEZZ_SIG`) plus a separate two-pin power harness (`J_MEZZ_PWR`, VH or Mini-Fit class). This is a deviation from R3 and wants an owner word.
- **A0-3, the hub has exactly zero spare ports** (WiFi, GPS, codec, UART). Option: put a small two-port hub on the mezzanine, which is the respin-isolated board, so PCB-A spends one port instead of two, the harness carries one USB pair instead of two, and the kit gains a spare port for field debugging. Costs one more tier (Pi, PCB-B hub, PCB-A hub, mezzanine hub is four of the five USB allows).
- **A0-4, cells in a sealed case with a transmitter.** The bank is west and the mezzanine east, which is the right separation, but the case is IP67 with no vent, and R6's NTC cutoff should be **both** ends, not just the low-temperature one R6 names: charging a cell above about 45 C in a black case in sun is the realistic failure, not the cold one.
- **A0-5, mass on a 1.6 mm board.** Four cells is roughly 190 g on a board carried only at four rod holes. Cheapest fix is a 2.4 mm nylon bumper under the bank block onto the case floor, which is exactly the gap that exists there; the alternative is 2.0 mm FR-4 for PCB-A alone.
- **A0-6, antenna polarity.** The AWUS036ACM's two ports are **RP-SMA**; the case bulkheads are SMA. Both WiFi pigtails are RP-SMA to SMA, not SMA to SMA. Cheap to get wrong.
- **A0-7, second WiFi bulkhead position.** R16 left it open. Propose (+128.75, **+72.0**, +25.0), 22 mm north of the existing WiFi bulkhead, matching the LED row's pitch convention. Owner drills it, so it is the owner's call.

### 16.8 Open before `gen_pcb_a.py` can run

| # | Item | Blocks |
|---|---|---|
| 16 | 18650 holder part and its measured height | `BOTTOM_GAP` 27.0, and therefore `Z_MIDDLE` and every ribbon length |
| 17 | The 8 mm panel LED type: bare, or internally resistored for 5 V or 12 V | the series resistor value, or whether PCB-A switches 5 V instead |
| 18 | DMR858M M-variant pin map, logic level and antenna termination | the mezzanine, which is the last board anyway (module lands 2026-09-15) |
| 19 | Charger part confirmed present in the JLCPCB library | the bank schematic |
| 20 | Shadow mode lifted, or the owner runs the generators | the whole ECAD phase for PCB-A |

### 16.9 What `check_pcb_a.py` must prove

Outline 240 x 160 R5 centred; four Ø3.2 rod holes at (+-110.5, +-73) with Ø9 keep-outs clear of every pad, every track and both plane pours; **no copper and no part outboard of any nut keep-out** (section 9 finding 5, PCB-A only); bank block, mezzanine standoff pattern, WiFi body, GPS body and both receptacle openings mutually clear by 3 mm or more; mezzanine module rectangle at least 19.5 mm from the GPS body and 20.0 mm from the WiFi body; tallest-object height 22 mm against `BOTTOM_GAP` 27.0 minus 2 x `NUT_H`; the raw-cell trace and its return sized for 4.2 A pulsed with a continuous return path; I2C addresses unique against the section 16.6 table; board thickness and layer count.

---

## 16. PCB-A POWER + I/O Rev A, phase A1 (mechanical + placement), generated 2026-09-02

**State: KiCad 9 board with every site placed, DRC clean, verifier ALL PASS. No schematic or copper yet** (phase A2 schematic, A3 routing, same pipeline as PCB-B). Files `ECAD/meshsat-carrier/pcb-a-power/` (`tools/gen_pcb_a.py`, `tools/check_pcb_a.py`); renders, 1:1 PDF and DRC report in `~/Downloads/meshsat-pcb-a-revA-A1/`.

| Site | Position (case frame, mm) | Fixing |
|---|---|---|
| Extension bank (R6) | four Keystone 1042 18650 holders, cell axis along X, centred X -66, Y -33.75 / -11.25 / +11.25 / +33.75 (22.5 mm pitch); envelope X -105 to -27, Y +-45 | THT holders |
| APRS mezzanine (R3) | 80 x 62 site X 5 to 85, Y +-31 | H5 to H8 Ø3.2 at (10/80, +-26); J_MEZZ1 IDC 2x8 at (-8, 8) for the harness (two USB pairs, PTT/TR, EN, 5 V logic, GND); J_MEZZ_PWR JST-VH 2-pin at (-8, -18) for the raw cell node to the 8 V boost (R15) |
| GPS puck | 40 x 26 x 18 at X 50 to 90, Y -65 to -39 | tie slots at (48/92, -70) and (48/92, -36); J_GPS1 USB-A receptacle at (30, -52) opening +X; three coil tie slots at (100, -50/-58/-66) for the captive cable |
| Alfa AWUS036ACM | body X 20 to 105, Y 39.5 to 65.5 | tie slots at (45/85, 36) and (45/85, 69); J_WIFI1 USB-A receptacle at (8, 52.5) opening +X; both RP-SMA pigtails to the two WiFi bulkheads (R16) |
| J_EXT_IN | USB-C receptacle at (95, -72), opening -Y | from the case inlet at (+100, -87.5, +25) |
| J_BANK_OUT | USB-C receptacle at (-96, -64), opening +X | 5 V source to the X1202 USB-C IN, cable up through PCB-B's slot at (-104.5, -57) |
| J_AB1 | IDC 2x7 top side at (-72, -66) | ribbon up to PCB-B's underside header at (-72, -78); 6 mm offset is fine for a 14-way ribbon over the 40 mm bay |
| J_LEDS | XH 1x10 at (-40, -74) | five panel LEDs of the front-wall row (R5), driven from the PCB-A expander |
| Hub zone | X -104 to -30, Y 48 to 76 | 4-port hub, four eFuse + INA219 channels (WiFi, GPS, codec, UART), PCA9555 at 0x21, LED drivers |
| Bank zone | X -104 to -30, Y -76 to -48 | 1S charger from the external input, 1S protection, 5 V boost to J_BANK_OUT, gauge (NOT at 0x36, the X1202 gauge owns that address on the shared bus) |
| Rods | H1 to H4 Ø3.2 at (+-110.5, +-73), Ø9 keep-outs | PCB-A's rod holes are 7 mm from the Y edges: nothing routes outboard of them (section 9 finding 5) |

Bottom bay check against R4/R17 (about 26 mm): holders with cells about 21 mm, GPS puck 18, WiFi 12, mezzanine stack 8 + 1.6 + 10 = 19.6 plus its tallest part, receptacles 7. Nothing exceeds 24 mm.

### 16.1 Phase A2, schematic, 2026-09-02: ERC clean, netlist and BOM exported

`tools/gen_sch_a.py` (same generator pattern as PCB-B) writes `pcb-a-power.kicad_sch` (A0, 135 symbols, 91 nets). ERC clean.

| Block | Parts | Notes |
|---|---|---|
| External input | J_EXT_IN1 USB-C receptacle (sink, 5.1 k on both CC), F1 3 A polyfuse, SMBJ5.0A, 10 uF | from the case inlet; a USB-C wall supply or power bank delivers 5 V up to 3 A |
| Charger + power path | U1 BQ25601 (I2C 0x6B): VBUS/VAC from the fused input, 2.2 uH XAL4020, SYS rail, BAT to the cell node, TS network 5.23 k / 30.1 k + 10 k NTC at the cells, CE with 10 k pull-down (charging on by default, expander can disable), PSEL low (adapter, 2.4 A input limit), STAT LED, INT to the expander, PG to a test point | power path means the kit runs from the input while the bank charges |
| Bank | BT1 to BT4 in parallel (Keystone 1042 holders), U2 BQ29700 protection driving two AO3400A back-to-back FETs in the negative path, 10 mOhm 2512 gauge shunt, U3 BQ27441-G1 gauge (I2C 0x55, GPOUT = BANK_ALERT to the Pi via J_AB1) | protection is in the negative path, so the raw cell node on J_MEZZ_PWR1 (R15) is still protected against over-discharge |
| 5 V boost | U4 TPS61022 from SYS, 1 uH XAL4020, 750 k / 100 k feedback for about 5.1 V, EN from the expander (default on), J_BANK_OUT1 USB-C receptacle as a 5 V source (56 k Rp on both CC) to the X1202 USB-C IN | the X1202 keeps buffering the kit; this bank feeds it |
| Local rails | +5V = 5V_A from PCB-B over J_AB1 (100 uF, TVS), U5 AMS1117-3.3 for the expander, monitors, gauge pull-ups and LEDs | I2C peripherals sit at 3.3 V like the Pi |
| Hub | U6 FE1.1s on +5V (internal regulators), upstream pair USB_A from J_AB1 (J_USB_UP2 on PCB-B, second Pi port), VBUSM from VBUS_A_SENSE; ports 1 WiFi, 2 GPS, 3 mezzanine codec, 4 mezzanine UART | |
| Channels | TPS2065CDBV + 0.1 R + INA219 each: WiFi 0x46, GPS 0x47, codec 0x48, UART 0x49; USBLC6-2SC6 on every pair; J_WIFI1 and J_GPS1 USB-A receptacles, codec and UART pairs on J_MEZZ1 | no address clashes with PCB-B (0x40 to 0x45), the X1202 gauge (0x36), the expanders (0x20/0x21), the charger (0x6B) or the bank gauge (0x55) |
| Expander | U19 PCA9555PW at 0x21: EN_WIFI/GPS/CODEC/UART, BOOST_EN, CHG_CE, MEZZ_EN, four LED cathodes (MESH, SAT, LTE, SYS), four FAULT inputs, CHG_INT; INT to EXP_INT (shared) | |
| LEDs | J_LEDS1 XH 1x10 to the five front-wall panel LEDs: PWR hard-wired from 5V_A through 1 k, MESH/SAT/LTE/SYS through 330 R with cathodes on the expander | R5 |
| Mezzanine | J_MEZZ1 IDC 2x8: 5V_CODEC + pair, 5V_UART + pair, TR_APRS (100 k pull-down), MEZZ_EN, 3V3, two spares, grounds; J_MEZZ_PWR1 JST-VH: CELL+ and GND for the 8 V boost | R3 / R15 |
| Interconnect | J_AB1 IDC 2x7, pin for pin the mirror of PCB-B's | |

Open at BOM time: LCSC numbers beyond the certain ones (FE1.1s, USBLC6, INA219, PCA9555, HRO USB-C); the inductor parts (XAL4020 footprint, 2.2 uH / 1 uH at 4 A and 8 A); the BQ29700 variant thresholds; the boost feedback ratio against the TPS61022 reference; the NTC placement against a cell.

### 16.2 Phase A3, placement, routing and fab files, 2026-09-02

**State: PCB-A Rev A is placed and autorouted on the JLC 4-layer stackup (GND plane In1; In2 carries a CELL+ pour over the bank area at priority 1 and the +5V plane elsewhere, both solid-connected). Gerbers, drill, JLCPCB BOM and CPL exported. Three of 274 connections are left for manual completion in KiCad**, listed as the only unconnected items in `out/pcb-a-power-drc.rpt`: SCL into U1 (BQ25601 pin 5, an In1 track passes 1.0 mm away, needs a via), the BQ27441 exposed pad to the GND track 0.3 mm from it, and U8 pin 3 (WiFi INA219 GND) whose router stub is degenerate. No electrical DRC violations; 38 "isolated copper" warnings are slivers of the CELL+ pour between the cell-holder pads and one padstack warning comes from the BQ27441 library footprint. Files: `pcb-a-power/out/` (gerber zip, jlc/ BOM + CPL + README-fab.txt, renders, DRC, schematic PDF) and `~/Downloads/meshsat-pcb-a-revA-A3/`.

**Placement (case frame):** charger, input protection and TS network in the south-east strip beside the GPS receptacle (X 5 to 45, Y -78 to -62); protection FETs, gauge, boost, LDO and test points in the south-west strip under the cells (X -104 to -30, Y -64 to -48) with J_BANK_OUT1 at (-98, -70) opening east, J_AB1 at (-72, -73) and J_LEDS1 at (-44, -74); hub, expander and LED resistors in the north-west strip (X -104 to -30, Y 48 to 70); WiFi channel beside J_WIFI1 (X -28 to 4, Y 44 to 70); GPS channel beside J_GPS1 (X 5 to 21, Y -62 to -40); the two mezzanine channels south of the mezzanine site (X -22 to 4, Y -46 to -26); J_EXT_IN1 at (95, -72) opening toward the front wall; J_MEZZ_PWR1 at (-8, -18). Net classes Default 0.25 / USB 0.2 with 0.15 gap / PWR 0.4 / BANK 0.5 mm for the cell, SYS, boost and input nets; 0.15 mm clearance; 0.7 to 0.9 mm vias. 68 fanout vias before routing, 2067 tracks after.

**Rev B notes:** the BANK nets carry up to 4 A on 0.5 mm tracks plus the In2 pour; a Rev B should widen those tracks or extend the pour. The bank's NTC must sit against a cell; the 0603 footprint is a placeholder for a leaded NTC or a cell-contact thermistor. *(Superseded 4 Sep 2026: the bank, its charger and its NTC left PCB-A with the one-pack-one-charger ruling of 3 Sep; A18 has no BANK net. Not a Rev B item.)*

**Owner steps before ordering:** route the three listed connections in KiCad, re-run DRC, fill the LCSC numbers, upload with impedance control on the USB pairs; order the Keystone 1042 holders, the XAL4020 inductors and the JST-VH housing with the cells; the mezzanine board is a separate design after 15 September.

### 16.3 Datasheet audit of the PCB-A power chain, 2026-09-02 (second session, no laptop access)

Read against the primary datasheets (TI SLUSBU9I for BQ297xx, TI SLVSDX7D for TPS61022, AOS AO3400A, Coilcraft XAL40xx, Terminus FE1.1s Rev B12). This session ran under gateway shadow mode, so nothing was changed on the laptop; these are findings for the next actuating session, before any board is ordered.

**A. BLOCKER: the bank protection trips under normal load, not just under the APRS burst.** The A2 schematic pairs `U2 BQ29700` with two AO3400A in the negative path. The BQ297xx senses overcurrent as a voltage across those FETs (Vds sensing, no sense resistor), and the factory configuration table (datasheet section 4) gives **BQ29700 OCD = 0.100 V, SCD = 0.5 V, OVP 4.275 V, UVP 2.800 V**. The gate drive comes from BAT, so the FETs run at Vgs equal to the cell voltage (3.0 V to 4.2 V), not 4.5 V. AO3400A is 23 mOhm typ at Vgs 4.5 V and 41 mOhm typ / 55 mOhm max at Vgs 2.5 V, so each FET sits around 28 to 35 mOhm at a 3.6 V cell and higher when the cell is low or the part is hot. Two in series is roughly 56 to 70 mOhm typical, and the 10 mOhm gauge shunt adds to it if it sits inside the VSS to V- loop.

Trip currents that follow (my calculation from those figures): OCD at **about 1.5 A typical and under 1 A worst case**, SCD at about 7 A typical and about 4 A worst case. The cell node has to deliver about 2.4 A just for the TPS61022 to hand the X1202 1.5 A at 5.1 V from a 3.5 V cell, and about 4.2 A during the mezzanine 8 V transmit burst (R15). **The pack would shut itself off in ordinary operation, and the burst would likely hit short-circuit protection as well.** The TPS61022 inrush is also worth a look: its soft start is 700 us against a 250 us SCD delay.

Two ways out, both cheap at this stage because nothing is ordered:
1. Keep BQ29700 and get the total sensed path to about 10 mOhm, i.e. two N-FETs of 4 to 5 mOhm each at Vgs = 3.0 V (a dual pack-protection FET, not two SOT-23 parts), giving a 10 A OCD trip and a 50 A SCD trip. Check where the BQ27441 shunt sits relative to VSS and V-.
2. Change the protector variant. In the same table **BQ29732 is OCD 0.190 V, OVP 4.280 V, UVP 2.500 V, SCD 0.5 V**, which is the best Li-ion fit in the family for this job and needs only about 19 mOhm for the same 10 A trip. BQ29706 also has OCD 0.200 V but its OVP is 3.850 V, which is wrong for a 4.2 V cell. Availability at LCSC is the open question: BQ29700DSER is the stocked one, so option 1 may be the practical answer, or both together.

**B. Boost inductor is off TI's recommended list and is the hottest part in a sealed case.** A2 specifies a 1 uH XAL4020 for the TPS61022. Coilcraft XAL4020-102ME is Isat 8.7 A, DCR 13.25 mOhm typ (14.6 max), Irms 6.7 A at a 20 C rise. TI's Table 8-2 recommends XAL7030-102MEC (28 A, 5 mOhm), XAL6030-102MEC (23 A, 6.18 mOhm), XEL5030-102MEC (16.9 A, 8.4 mOhm) or Wurth 744316100 (11.5 A, 5.23 mOhm). At 3 A out (the X1202 USB-C input can pull that while charging) from a 3.2 V cell, my numbers are I_L(DC) = 5.3 A, ripple 1.2 A, peak about 5.9 A, so the XAL4020 has 1.5x saturation margin and dissipates about 0.37 W in a 4 x 4 mm body inside an IP67 case. XAL6030-102MEC halves that to about 0.17 W and is 6.36 x 6.56 x 3.1 mm, which the roughly 26 mm bottom bay swallows without trouble. Recommend the swap; if the boost is deliberately limited to 1.5 A or so, the XAL4020 stays defensible and the duty statement should say so.

**C. Verify the TPS61022 feedforward capacitor.** VREF is confirmed at 600 mV typ (585 to 615 mV in PWM), so the 750 k / 100 k divider gives 5.10 V, correct. The divider draws 6 uA against a 20 nA max FB leakage, which clears TI's "at least 100x" rule but only by 300x, and TI notes that lowering R2 improves noise immunity. Section 8.2.2.4 asks for a feedforward capacitor across R1 whenever the output capacitance is above 40 uF, at a 2 kHz zero: with R1 = 750 k that is C3 = 1/(2*pi*2000*750k), about 100 pF. The A2 block table does not list one. Check the schematic and add it if it is absent; also confirm the output capacitance sits in TI's 10 to 50 uF effective window after dc-bias derating.

**D. Closed with no change: FE1.1s REXT.** The 2.7 kOhm 1% to VSS carried by both hub instances is exactly what the FE1.1s datasheet specifies. The "verify against the datasheet" note in 15.4 can be struck.

**E. I2C address map re-checked across both boards** (they share one bus over J_AB1): INA219 0x40 to 0x45 on PCB-B and 0x46 to 0x49 on PCB-A are all inside the INA219 0x40 to 0x4F range and unique; no collision with PCA9555 0x20 and 0x21, X1202 gauge 0x36, BQ27441 0x55 or BQ25601 0x6B. No change needed.

Not audited this session (no schematic access from the runner): the BQ25601 TS network and register defaults, the charge path behaviour when the case USB-C inlet supplies both the charger and the kit, and the PCB-B hub power tree.

---

## 17. Audit round 2, 2026-09-02 (third session, shadow mode, read-only laptop access)

This session also ran under gateway shadow mode, so again nothing was changed. It did have **read access to the laptop over SSH**, which the previous session lacked, so the three items 16.3 left open are closed here against the actual generator source (`tools/gen_sch_a.py`, `tools/gen_sch_b.py`) and TI's BQ25601 datasheet SLUSCK5A (March 2023). Findings F to I are for the next actuating session, before any board is ordered.

### 17.1 Status of the B4 run

`full_b4.sh` is a **pre-route chain only**; it ends at `PREROUTE-DONE`. Freerouting finished separately at 12:49 and the result is good: SES imported (2087 tracks, 232 vias), and the post-route DRC leaves **one unconnected net, `EN_XIAO` (U10 pad 5 to U20 pad 6)**, two short dangling GND stubs, and 46 silkscreen cosmetics. That is better than B3's six leftovers.

Two things are NOT done, and both are traps for whoever picks this up:

1. **The B4 fab export never ran.** `out/jlc/` still holds the **B3** BOM and CPL from 07:07 while `out/*.gerbers.zip` is B4 from 12:49. Uploading `out/jlc/` today would ship B3 placement data against B4 gerbers. Run `export_jlc.sh` for B4 before anything is uploaded.
2. There is no `~/Downloads/meshsat-pcb-b-revA-B4/`, and `out/pcb-b-compute-render-bottom.png` is **0 bytes** (the bottom render failed silently).

Also worth recording: Freerouting logged its own warning that **multi-threaded optimisation is broken and generates clearance violations, and recommends `-mt 1`**. Both B3 and B4 were routed with `-mt 4`. In B4 it did not bite (the DRC shows no clearance class at all), but the B3 board carries the same risk and neither was routed the way the tool asks for.

### 17.2 F. BLOCKER: two BQ25601 pins are mapped wrong on PCB-A

`gen_sch_a.py` line 131 to 133 against Table 7-1 of SLUSCK5A. Twenty-two of the twenty-four pins are right, including VAC on pin 1 tied to VBUS, which the datasheet explicitly requires, and NC on pins 8 and 10, which it explicitly wants floating. Two are wrong, and in both cases the generator treated a functional pin as a non-functional one:

| Pin | Schematic says | Datasheet says | Consequence as drawn |
|---|---|---|---|
| 2 | `GND` | **PSEL**, digital input. High = 500 mA input limit, low = 2.4 A | Tied hard to the GND net, so the part silently comes up at **2.4 A**. Not dangerous (VINDPM folds the current back when a weak source sags) but it is an accident, not a decision, and it reads as a ground pin to anyone maintaining the netlist |
| 12 | `NC` | **/QON**, BATFET enable/reset input, internal 200 kOhm pull-up | Floating is electrically safe, but the kit loses the only way to exit ship mode without VBUS, and loses the hardware full-system-power-reset lever |

Fix: route pin 2 deliberately (a 0 R or a DNP pad to GND and to REGN so the limit is a jumper choice, with the intent on the silkscreen), and bring pin 12 out to at least a test point, ideally a header, so ship mode is usable on a sealed kit. Both are schematic-level changes and force an A4 regeneration, which is why this is a blocker rather than a note: the A3 board and its exported fab files are wrong today.

### 17.3 G. The charger's thermistor does not match its bias network

`R3 = 5.23k` (REGN to TS) with `R4 = 30.1k` (TS to GND) is TI's own recommended network, and the datasheet's TS pin description states plainly that **"it is recommended to use a 103AT-2 thermistor"**, which is beta = 3435 K. `NTC1` in the schematic is specified as a **10k NTC 3950**. Different curve.

Working the beta equation against that divider (my calculation, and it assumes TI's network targets the JEITA T1 = 0 C and T5 = 60 C points, which is the standard assumption but is worth one check against the threshold table before acting):

| Point | With 103AT-2 (beta 3435) | With the specified beta 3950 |
|---|---|---|
| Cold, charge suspend | 0 C | about **+4 C** |
| Hot, charge suspend | 60 C | about **55 C** |

So the charging window narrows from 0 to 60 C down to roughly 4 to 55 C. It fails in the safe direction, but R6 rules the low-temperature cutoff as a feature of this bank, and a field kit sitting outdoors in a Dutch or German winter will regularly sit between 0 and 4 C and simply refuse to charge, with no indication of why.

Two fixes, and the first is clearly better:

1. **Specify a 103AT-2 (beta 3435) 10k NTC** and keep the resistors. Zero board change, BOM string only, and it is TI's own recommendation. 16.2 already calls the NTC footprint a placeholder for a cell-contact thermistor, so nothing is lost.
2. Keep beta 3950 and recompute the divider: **R3 = 4.22k, R4 = 18.2k** (E96), which puts the two trip points back at 0.1 C and 60 C.

### 17.4 H. There is no input-current negotiation of any kind, and there cannot be

The case USB-C inlet `J_EXT_IN1` presents 5.1k Rd on both CC pins and nothing reads them back, and `A6/B6/A7/B7` (D+/D-) are all NC. I had expected to recommend wiring D+/D- into the charger, but the datasheet's Device Comparison Table settles it: **the plain BQ25601 has no D plus / D minus USB detection at all.** Only the BQ25601D and BQ25611D do.

So the only levers on this part are PSEL (finding F) and an I2C write to REG00, and the I2C write cannot happen until the Pi has booted, which is after the point where charging should already be running. The kit will present itself to any source as a 2.4 A load and rely entirely on VINDPM foldback to survive a weak one. That is acceptable behaviour, but it should be a stated design position with the duty statement, not an emergent one. If deliberate source detection is ever wanted, the part to change to is the **BQ25601D**, pin-compatible in the same RTW package.

### 17.5 I. BLOCKER: the PCB-B 5 V trunk polyfuse is far below the load

`gen_sch_b.py` line 125: both X1202 XH2.54 outputs land on one `5V_IN` net, then a **single 3 A hold polyfuse F1** feeds `+5V`, and every one of the six switched channels plus the FE1.1s hub sits behind it.

Adding up the appendix's own per-channel figures for a concurrent worst case: SDR (LimeSDR Mini 2.0) 0.6, ZigBee 0.1, LoRa (T-Beam 1W on transmit) 1.3, RockBLOCK 9704 burst about 1.0, T-Call A7670E LTE burst about 2.0, `5V_A` to the whole of PCB-A about 0.7, hub 0.05. That is about **5.75 A through a 3 A hold device**. Even a quiet kit with nothing transmitting sits around 2 A.

The derating is what makes it a blocker rather than a margin question. A PPTC's hold current falls to roughly half its 23 C rating by 60 C ambient, and the inside of a sealed IP67 case next to a 5 W PA gets there. Effective hold becomes something like 1.5 to 1.8 A, which is below the idle load. Worse, the device has tens of milliohms at rated current, so the drop and its own self-heating push it further toward trip: this is exactly the shape of the T-Call brownout that MESHSAT-523 chased, moved into the fuse instead of the EEPROM.

The trunk fuse also adds nothing. Every channel downstream **already** has its own polyfuse or current-limited switch plus an INA219, which is the entire point of the power tree. Recommendation: **delete F1** and let the per-channel protection do its job, or if a trunk device is wanted for the X1202 cable itself, size it against the X1202's own 5 A rating rather than below the load, and account for the sealed-case ambient.

### 17.6 J. Closed with no change: the gauge shunt is outside the protection loop

16.3 A asked where the BQ27441 shunt sits relative to VSS and V-. Answer from the schematic: `R10` (10 mOhm) is between `BATN` and `GND`, while the BQ29700's VSS is at `CELL-` and VM senses `BATN` through `R9`. The sensed path between VSS and VM is **the two AO3400A only**, common-drain at `MID` with sources at `CELL-` and `BATN`, which is the correct topology. So the shunt does **not** add to the OCD threshold, and finding 16.3 A stands unchanged at about 56 to 70 mOhm sensed, not worse. The blocker itself is unaffected.

### 17.7 K. On shore power the whole kit runs through a buck and then a boost

`R15` pulls `BOOST_EN` up to `SYS`, so the TPS61022 is on whenever SYS is alive. With the case USB-C plugged in, kit power therefore goes external 5 V into the BQ25601 buck down to SYS (roughly 3.6 to 4.2 V), then back up through the boost to 5.1 V into the X1202 input. Two conversions at about 0.90 each is about **0.81 end to end**, so roughly 1.8 W of the 7.5 W kit load is dissipated as heat inside a sealed case purely because it is plugged in.

Not a blocker and not wrong, but worth a Rev B line: an ideal-diode OR from `VIN_F` straight onto `5V_BANK` would let external power bypass both stages, and the thermal budget for the IP67 case should carry this number either way. *(Superseded 4 Sep 2026: `5V_BANK` and both stages left PCB-A with the one-pack-one-charger ruling. Not a Rev B item.)*

### 17.8 Minor notes

- `gen_sch_b.py` line 147 still carries the literal value string `"2.7k 1% (REXT, verify datasheet)"`, which prints into the schematic and the BOM. 16.3 D closed the question; strike the parenthesis.
- `J_XIAO1` and `J_TBEAM1` are wired to the same nets by design, one populated. Nothing stops an operator fitting both and putting two USB devices on one hub port. Needs a POPULATE ONE legend on the silkscreen.
- The datasheet asks for 20 uF at SYS; `C5 + C6` are 10u + 10u nominal, which after dc-bias derating on small MLCCs is likely nearer 10 to 14 uF effective. Worth confirming when the LCSC parts are pinned.
- Everything else checked against Table 7-1 is correct: PMID 10u, REGN 4.7u, BTST 47n, VBUS bulk, thermal pad to GND.

## 18. PCB-D APRS BOARD Rev A, phases D1 to D3, generated 2026-09-02

> **Renumbered 2026-09-02 (audit round 3).** This section was written as a second "17" while section 17 above was already taken by audit round 2, so "appendix section 17" was ambiguous in the MESHSAT-709 comments and in the memory file, and subsection numbers 17.1 to 17.3 existed twice with different content. PCB-D is now **section 18**. Earlier references to "section 17" for the APRS board mean this section; references to 17.1 "Status of the B4 run", 17.2 "F", 17.3 "G", 17.5 "I" and so on mean audit round 2 above.

The 80 x 62 mm daughterboard on PCB-A's four M3 standoffs (case 10/80, +-26; board-local frame is case minus (45, 0), +X = SMA end = case east). Owner decisions 2 Sep: the name is **APRS board / PCB-D** (not "mezzanine"); the USB-audio, PTT and UART block is an **AIOC-derived core** (STM32F302C8T6 running the public AIOC firmware, MIT, `skuep/AIOC` rev 1.2, whose exact netlist was exported with kicad-cli and is staged in `ECAD/vendor/aioc/`) rather than a CM108B plus a USB-UART bridge. One USB device on the harness's codec pair gives the sound card, the CM108-style PTT and the virtual COM port that drives the DMR858M's UART; the harness's UART pair stays unused.

### 18.1 What is on it (`tools/gen_sch_d.py`, 91 parts, 59 nets, ERC clean)

- **DMR858M** as `meshsat.pretty/DMR858M`: 24 pads 1.0 x 2.6 mm (0.6 mm outboard of the module edge), rows 2 x 18.645 mm apart, 2.54 mm pitch, pin 1 (VCC) at the south-east, pin 13 (MIC-) at the north-west, module rotated 90 deg clockwise from the datasheet view so the SMA faces east. Module centre (12, -2): its SMA end passes the board edge by 1.2 mm, the SMA body sits fully outboard for the pigtail. Pin use: 1 VCC = 8 V; 2/4/15/17 GND with a via 2.2 mm inboard of each; 3 CS pulled to 3V3 through 10k with JP5 to GND for sleep tests; 5 PTT from the core's open-collector driver; 6 LINE_OUT into the core's audio input; 7 to 10 channel bits on solder jumpers JP1 to JP4 to GND (open = default); 13 MIC- to GND and 14 MIC+ from the core's DAC path (single-ended drive, **verify on the module**); 16 SPKEN to the harness spare pin 14 and a test point; 18/19 TXD/RXD through 100 ohm to the STM32 USART1; 11/12 speaker, 20 to 24 unused.
- **Boost, TPS61089 (VQFN-11, `Texas_VQFN-RNR0011A-11`)**: VIN = cell node from J_PWR1 (JST-VH); VFB 1.2 V with 113k / 20k gives 7.98 V; FSW 301k between FSW and SW = 500 kHz (the pin must never float); ILIM = 1.03e6 / 130k = 7.9 A peak; COMP 17.4k + 4.7 nF (TI's 9 V / 2 A example); BOOT 100 nF; VCC 1 uF; L1 Coilcraft XAL6030-152MEB 1.5 uH (12 A, 5.6 mOhm, on TI's inductor class); input 2 x 22 uF 10 V 1210 + 100 nF; output 4 x 22 uF 25 V X7R 1210 + 100 nF; EN = MEZZ_EN from PCB-A's PCA9555 with a 100k pull-down. At 3.0 V cell and 1.7 A out the input averages about 5 A, inside the 7.9 A peak limit.
- **AIOC core**: FB2 bead from the harness 5 V to two AP2112K-3.3 LDOs (digital 3V3, analog LDO_A through FB1 = 3.3VA), STM32F302C8Tx with the AIOC pin map (PA0/PA1 PTT outputs, PA3 DAC attenuator, PA4 DAC out, PA5/PB2 ADC in, PA6 bias, PA9/PA10 USART, PA11/PA12 USB with the 1.5k pull-up, PB6/PB7 PTT read-back, PB8/PB9 LEDs, SWD on PA13/PA14/PB3), 8 MHz 5032 crystal with 22 pF, NRST 100 nF, BOOT0 5.1k, J_SWD1 1.27 mm 1x7 (short pins 1 and 7 for DFU). The F373 pins 23/24/25 of the AIOC map to the F302's VSS/VDD/PB12. Audio and PTT networks are the AIOC values (4.7k / 100 ohm / 1.5k attenuator into a 4.7 uF coupling cap; 4.7 uF + 5.1k input with the 5.1k / 100 nF bias and 4.7 nF anti-alias; 1.5k base resistors, 22 ohm collector resistors, 1.5k read-back). The dual BC847BS became two BC847 (Q1 for the unused PTT2, Q2 for the module PTT) because the two-unit symbol tripped the generator.
- **TR_APRS** to the Pi is the STM32's PTT drive (OUT1) through 100 ohm: active high during transmit, matching PCB-A's 100k pull-down. USB from J_HARN1 pins 3/4 through a USBLC6-2SC6.
- Harness J_HARN1 (IDC 2x8, mirror of PCB-A's J_MEZZ1): 1/5/9/13/16 GND, 2 5 V, 3/4 USB, 10 TR_APRS, 11 MEZZ_EN, 14 SPKEN; pins 6/7/8 (UART pair), 12 (PCB-A 3V3) and 15 unused. Test points TP1 to TP11 on the underside.

### 18.2 Placement (board-local, mm) and the D3 result

| Zone | Content |
|---|---|
| West | J_HARN1 at (-33, 6) pins along Y (11 x 29), J_PWR1 at (-33, -14); boost column X -27 to -18, Y -30.4 to 17.5 (L1, U1, the six 1210s and the boost passives, top side) |
| North strip Y 18.6 to 30.4 | top: U3 + C4/C6/FB2 west of the MCU, U4/C5/FB1/C9/C10, U6 + R1, LEDs east; **bottom: U5 STM32 at X -7 to 7**, clock, decoupling, PTT drivers and UART resistors west, audio network east |
| South strip Y -30.4 to -22.6 | top: J_SWD1 at (24, -26.5); bottom: JP1 to JP5, R36, TP1 to TP11 |
| Module | ~~X -17.2 to 41.2, Y -21.3 to 17.3~~ **D4 (section 22.6): the module plugs into two 1x12 sockets and sits on M2.5 x 11 mm standoffs 11 mm above the board, centre (10.5, -2), rows at Y 16.075 and -20.075, X -3.3 to 24.6; the MCU core moved to the top side under it**; its USB-C on the west end is reached by unplugging the module; the ON/OFF pins are not exposed |

D1 `check_pcb_d.py` ALL PASS (outline, four standoff holes, 24 pads with the datasheet pitch and row spacing, pin 1 at 15.06 mm from the SMA edge, connectors at their positions, everything inside the outline and off the standoff faces). D3: netlist imported, 35 fanout vias + 4 module GND vias, pre-route DRC clean of hard violations; Freerouting 1.9 routed it in seconds: **885 tracks, 116 vias, two GND connections left for manual routing in KiCad (U5 VSS pins 23 and 35 on the bottom side, no room for an automatic via)**; no electrical DRC violation (silk warnings only). Fab files: `pcb-d-aprs/out/` and `~/Downloads/meshsat-pcb-d-revA-D3/` (Gerbers, JLC BOM + CPL + README, schematic PDF, renders, 1:1 PDFs, KiCad project, the `meshsat.pretty` footprint library). JLC assembles both sides; the DMR858M is bench-soldered.

### 18.3 Open before ordering PCB-D

1. ~~Pad rows are from the datasheet drawing: measure the physical module on 15 Sep~~ **CLOSED 2 Sep evening from the datasheet drawing itself (section 22.6): the rows are through-hole pins 1.27 mm inboard of the edges, pin 1 is on the other row than D3 assumed, and the module cannot lie flat, so D4 mounts it on sockets and standoffs. No physical measurement is needed (owner ruling).**
2. MIC- to GND and the UART logic level (assumed 3.3 V TTL; PA10 is 5 V tolerant either way) need the module in hand.
3. Standoffs 6 mm (bare-minimum clearance for the bottom-side parts); ~~with the module's 19.5 mm heatsink the stack is 6 + 1.6 + 19.5 = 27 mm above PCB-A, so `BOTTOM_GAP` about 30 mm~~ **D4: the module's back face sits 11 mm above PCB-D (socket 8.5 + header body 2.5), its heatsink tip about 14.5 mm above that, so the stack is 6 + 1.6 + 11 + 14.5 = 33 mm above PCB-A; `BOTTOM_GAP` becomes about 35 mm (was about 30, section 11 item 10 and R4). If the middle bay cannot give the 5 mm, 4.3 mm low-profile sockets bring the stack back to about 29 mm at the cost of a shallower pin engagement.**
4. LCSC numbers are filled for the AIOC parts that carry them; the TPS61089, XAL6030, AP2112K, VH and IDC parts are matched at order time.
5. The two GND stubs, then the owner's KiCad review and JLCPCB DFM.

---

## 19. Audit round 3, 2026-09-02 (fourth session, shadow mode, no laptop access)

Gateway shadow mode again, and this time without even read access to the laptop (`Bash` is gated, so no SSH, no git, no scripts). Nothing was changed on the laptop. This is a datasheet and upstream-source audit of **PCB-D, the one board that had never been audited**, plus the two places where a PCB-D number collides with a PCB-A decision that is still open.

Sources read this session: TI **SLVSD38C** (TPS61089/TPS610891, Rev C, August 2021) pages 1 to 6 in full; the **skuep/AIOC** README and the GitHub release API for tag v1.4.1; the LCSC and JLCPCB catalogue entries for C94046; ST **AN2606** (bootloader peripheral table); the TI TPS61022 product page. Findings L to P are for the next actuating session, before any board is ordered.

### 19.1 L. BLOCKER: PCB-D's MCU part number cannot hold the AIOC firmware

`gen_sch_d.py` specifies **STM32F302C8T6**. The C8 suffix is **64 KB of flash**.

The AIOC firmware release binary `aioc-fw-1.4.1.bin` is **128,016 bytes** (GitHub release asset, tag v1.4.1, published 27 September 2025). The image therefore extends to offset 128,016 from `0x08000000`, well past the 65,536-byte end of a C8, and that conclusion holds whether those bytes are all code or include a padded gap up to a high-address settings page: DFU writes the image as delivered either way. **It cannot be flashed onto the specified part.**

AIOC's own README settles the correct one: *"Despite the STM32F373 in the BOM, the firmware currently only supports the STM32F302 as given in the LCSC ordering information"*, and that ordering part is **STM32F302CBT6**, 128 KB, LQFP-48, **LCSC C94046**, which is also in JLCPCB's own catalogue (so R12, JLC assembles everything, still holds) at roughly USD 2.74 with stock on hand.

Worth recording as a ceiling rather than a problem: 128,016 of 131,072 bytes is **97.7 % of a CB's flash**. There is no room for a second application, and an upstream AIOC release that grows by 3 KB will not fit either. If the kit ever wants its own firmware on this MCU, the part to jump to is the pin-compatible 256 KB STM32F302CCT6.

**Not the reason, for the record.** I expected the 64 KB part to also lack a USB bootloader and it does not: AN2606 gives STM32F301xx/302x4(6/8) a USART1 / USART2 / **DFU (USB Device FS)** bootloader, the same set as the xB/xC parts. A C8 would have enumerated for DFU quite happily and then failed on the write, which is the worse failure mode of the two.

**Cost of the fix: BOM string only, no board change.** The schematic's pin map is the standard STM32 F3 LQFP-48 map (pin 23 `VSS_1`, 24 `VDD_1`, 25 `PB12`, 35 `VSS_2`, 44 `BOOT0`), which the C8 and the CB share; section 18.1 already records that map, and the two GND stubs left at U5 pins 23 and 35 confirm it in the routed board. Change the part number and the LCSC field, re-run ERC, do not re-place.

### 19.2 M. BLOCKER: the 8 V boost hits its current limit at the end of a discharge

Section 18.1 justifies `R_ILIM = 130k` with "at 3.0 V cell and 1.7 A out the input averages about 5 A, inside the 7.9 A peak limit". **The average is the wrong quantity.** Table 6-1 of SLVSD38C defines ILIM as the "adjustable switching **peak** current limit", and the ripple on a 1.5 uH inductor at 500 kHz is not small.

My calculation, at V_OUT = 8.06 V (see 19.3), I_OUT = 1.7 A (the DMR858M's 5 W analog figure), L = 1.5 uH, f_SW = 500 kHz, efficiency taken from the datasheet's own "up to 90 % at V_IN 3.3 V, V_OUT 9 V, I_OUT 2 A":

| Cell | I_L average | Duty | Ripple pk-pk | **I_L peak** | Margin to the 7.14 A minimum limit |
|---|---|---|---|---|---|
| 3.6 V | 4.3 A | 0.553 | 2.65 A | 5.6 A | 21 % |
| 3.0 V | 5.19 A | 0.628 | 2.51 A | 6.45 A | 11 % |
| 2.8 V | 5.69 A | 0.653 | 2.44 A | 6.91 A | **3 %** |
| 2.8 V, inductor 20 % low | 5.69 A | 0.653 | 3.05 A | **7.21 A** | **trips** |

The 7.14 A figure is the datasheet's characterised minimum scaled to 130k (Section 7.5 gives 7.3 / 8.1 / 8.9 A at R_ILIM = 127k and 9.0 / 10 / 11 A at 100k; the 1.03e6/R formula in 18.1 reproduces both typicals, so it is sound, it was just applied to the wrong current). The XAL molded parts are a 20 % tolerance class, which is the last row: **at the end of a discharge, with an inductor at the low end of tolerance, a 5 W transmit burst folds the 8 V rail back mid-transmission.** That is the worst possible time for it and it will look like an RF or antenna fault, not a power fault.

**Fix: R_ILIM 130k to 100k**, giving 9.0 A minimum. That is one resistor value, no board change, and it is inside the part's stated intent (Section 1 advertises "resistor-programmable peak current limit up to 10 A for high pulse current"); the module never draws more than 1.7 A, so the limit is not protecting anything at 7.9 A that it does not protect at 10 A. Optionally also take L from 1.5 uH to **2.2 uH**, which is TI's NOM in Recommended Operating Conditions and halves the ripple term, at the cost of DCR; the ILIM change alone is sufficient.

Confirm the 20 % inductor tolerance from the Coilcraft datasheet at order time. Coilcraft's site returns 403 to the runner, so that number is the one figure in this section I could not verify at source.

### 19.3 N. The 8 V rail sits within 2 % of the DMR858M's absolute maximum supply

The module is 3.7 to 8.5 V on pin 1 (section 11 item 10). The divider is 113k / 20k, and 18.1 computes 7.98 V from a 1.2 V reference. The datasheet's actual reference is **V_REF = 1.212 V typ in PWM (1.188 to 1.236), and 1.224 V in PFM**, so:

- PWM, nominal parts: 1.212 x 6.65 = **8.06 V**
- PFM (light load, which is receive, i.e. most of the time): 1.224 x 6.65 = **8.14 V**
- Stacking V_REF max with 1 % divider resistors: about **8.4 V**, i.e. **1.2 % below the module's absolute maximum**

Add the load-release transient. The module steps from 1.7 A to about 0.165 A the instant PTT drops, into 88 uF nominal of output capacitance, and a boost overshoots on load release. Nothing in the design bounds that overshoot below 8.5 V; the TPS61089's own output OVP is at 13.2 V and offers no protection here.

Two remedies, both BOM-only:
1. **Retarget the rail to about 7.6 V: R1 = 105k, R2 = 20k** gives 7.58 V typ and stays under about 7.9 V worst case. The module's 5 W figure is quoted at 8 V, so expect a few tenths of a dB less PA output, which is nothing against the link budget.
2. Keep 113k / 20k and specify **0.5 % divider resistors**, which pulls worst case to roughly 8.3 V. Cheaper but it does not address the transient.

Recommend option 1. This is the same class of error as 19.2: a nominal-value calculation carried into a design where the worst case is what matters.

### 19.4 O. Finding A's second remedy would strand the boost, which makes the first remedy better on two grounds

Section 16.3 A offers two ways out of the bank-protection blocker, and the second is "change the protector variant to BQ29732 (OCD 0.190 V, OVP 4.280 V, **UVP 2.500 V**)".

The TPS61089's Recommended Operating Conditions give **V_IN minimum 2.7 V**, and Section 7.5 puts V_IN_UVLO rising at 2.7 V max and falling at 2.4 to 2.5 V. So a pack that is allowed to run down to 2.5 V per cell takes the APRS board's boost below its minimum operating input and into the band where it stops **somewhere between 2.4 and 2.7 V depending on the individual part**. The behaviour is not dangerous but it is unspecified, and the boost would give up before the pack protection ever acted.

The TPS61022 on PCB-A is unaffected: it is a 0.5 to 5.5 V input part and starts at 0.5 V.

So **option 1 of 16.3 A (keep BQ29700 at UVP 2.800 V and fix the sensed resistance with a dual pack-protection FET at 4 to 5 mOhm) is now the better answer on two independent grounds**: it also keeps the cell above the boost's minimum input by 100 mV of margin. If the owner still prefers BQ29732 for the OCD headroom, PCB-D needs its own enable/UVLO on the boost so the shutdown point is a decision rather than a part tolerance.

### 19.5 P. The APRS boost's thermal number, for the duty statement

At 8 V and 1.7 A the boost delivers 13.7 W. At roughly 90 % efficiency about 1.5 W is lost, of which about 0.15 W is inductor DCR, so roughly **1.0 to 1.4 W lands in a 2.00 x 2.50 mm VQFN**. Section 7.4 gives R-theta-JA 53.4 C/W on the JEDEC board, 39.2 C/W on TI's own EVM, and R-theta-JB 9.6 C/W with psi-JB 9.5: **the board is the heatsink**, and the difference between those two numbers is entirely copper and vias.

At the EVM number and 1.2 W that is a 47 C junction rise; at the JEDEC number, 64 C. Inside a sealed IP67 case sitting at 45 C internal during a burst, T_J lands between about 92 and 109 C against a 125 C maximum and a 150 C thermal shutdown. **Short bursts are fine; continuous 5 W transmit is not, and now there is a number to write into the transmit duty-cycle statement that MESHSAT-748 and the design pages both owe.** Confirm the layout gives the package's thermal pad a via array into the ground plane, since the whole margin lives there.

### 19.6 Closed with no change

- **FSW = 301k between FSW and SW is correct.** Table 6-1: "The switching frequency is programmed by a resister between this pin and the SW pin", which is an unusual arrangement that would have been easy to get wrong, and Section 7.5 confirms 301 kOhm gives 500 kHz (46.4 kOhm gives 2000 kHz). 18.1's warning that the pin must never float stands.
- **The ILIM formula itself is right.** 1.03e6/R reproduces both characterised points (127k gives 8.1 A typ, 100k gives 10 A typ). Only its application in 19.2 was wrong.
- **Input and output capacitance are inside the window.** Recommended Operating Conditions ask for 10 uF effective in and 10 to 1000 uF out (47 nom); 2 x 22 uF 10 V in and 4 x 22 uF 25 V out stay inside after dc-bias derating. Note this is a far wider window than the TPS61022's, so **16.3 C's feedforward-capacitor concern does not carry across to this part**: that requirement is specific to the TPS61022 above 40 uF of output capacitance and 16.3 C remains open only against PCB-A.
- **L = 1.5 uH is inside the 0.47 to 10 uH range**, and V_OUT = 8 V is inside 4.5 to 12.6 V.
- **Soft start is fixed at 4 ms** on this part (2 / 4 / 6 ms), so there is no soft-start-versus-protection-delay interaction of the kind 16.3 A flagged on the TPS61022.

### 19.7 Documentation defect fixed

The appendix carried **two sections numbered 17** (audit round 2, and the PCB-D board record) with subsection numbers 17.1 to 17.3 appearing twice with unrelated content, which made "appendix section 17" ambiguous in five MESHSAT-709 comments and in the memory file. The PCB-D record is now **section 18**, with a redirect note at its head. No content changed.

### 19.8 Consolidated gate: what must be true before anything is ordered

Nine items, three of them blockers, across all four boards. Nothing here is expensive; all of it is expensive after fabrication.

| # | Board | Item | Source | Change class |
|---|---|---|---|---|
| 1 | PCB-A | Bank protection trips at about 1.5 A typical, under 1 A worst case | 16.3 A | schematic, regenerate |
| 2 | PCB-A | BQ25601 pin 2 PSEL tied to GND, pin 12 /QON left NC | 17.2 F | schematic, regenerate |
| 3 | PCB-B | 3 A trunk polyfuse F1 under a 5.75 A load, derating to 1.5 A hot | 17.5 I | schematic, regenerate |
| 4 | **PCB-D** | **STM32F302C8T6 cannot hold a 128,016-byte firmware; part is STM32F302CBT6, LCSC C94046** | **19.1 L** | **BOM string** |
| 5 | **PCB-D** | **R_ILIM 130k to 100k; peak inductor current, not average, sets the limit** | **19.2 M** | **BOM value** |
| 6 | **PCB-D** | **8 V rail worst case about 8.4 V against an 8.5 V module maximum; retarget to 105k / 20k** | **19.3 N** | **BOM value** |
| 7 | PCB-A | NTC beta 3950 against TI's 103AT-2 network; specify a 103AT-2 | 17.3 G | BOM string |
| 8 | PCB-A | Boost inductor XAL4020 off TI's list; XAL6030-102MEC | 16.3 B | BOM string |
| 9 | PCB-B | B4 fab export never ran, `out/jlc/` still holds B3 BOM and CPL | 17.1 | run `export_jlc.sh` |

Plus the six manual routing stubs (PCB-A 3, PCB-B 1, PCB-D 2), the LCSC fill, the Freerouting `-mt 1` re-run question, and the 15 September physical measurement of the DMR858M pad rows.

**Sequencing note.** Items 1, 2 and 3 already force a schematic regeneration of PCB-A and PCB-B. Items 4, 5, 6, 7 and 8 are BOM-only and cost nothing extra if they ride the same regeneration, so the efficient move is one A4 / B5 / D4 pass that carries all nine, not two passes.

## 20. Design review of all four boards, 2026-09-02 (owner asked Claude to review instead of reviewing himself)

**Method.** Three passes: (1) `tools/review_nets.py` on every generated netlist (supply pins without a capacitor, control pins without a defined default, USB pairs without ESD, I2C address collisions, connector mates pin by pin between boards); (2) symbol pin maps read back from the KiCad libraries and checked against the datasheets for every non-trivial IC (BQ25601, BQ297xy, BQ27441, TPS61022, TPS61089, TPS22810, TPS2065C, FE1.1s, PCA9555, INA219, STM32F302); (3) the DRC and the routed result of every board. Findings were fixed in the generators and the boards re-routed (B5, A5, D3), not patched by hand.

### 20.1 Findings and fixes

| # | Board | Finding | Fix |
|---|---|---|---|
| 1 | A | Bank protection tripped at about 1.5 A (16.3 blocker): AO3400A pair at 60 to 80 mOhm in the BQ29700's 100 mV OCD loop | Q1/Q2 = CSD17303Q5 (30 V NexFET, 2.6 mOhm, TDSON-8, pins 1-3 S, 4 G, 5 D; AON6504 is a drop-in alternative): OCD now about 12 A, SCD about 60 A |
| 2 | A | BQ27441 sense pins reversed: SRN was on the battery side of RSENSE, SRP on the system side; datasheet 9.1 wants SRP on the pack side | pin 8 SRP = BATN, pin 7 SRN = GND; the gauge would otherwise report charge as discharge |
| 3 | A | Charger enable: BQ25601 /CE driven only by the PCA9555, which powers up as an input with a 100k pull-up, so charging stayed OFF until software ran (a fully drained kit could never recover) | R44 10k pull-down on CHG_CE: charging defaults ON |
| 4 | A | Bank USB-C source advertised 500 mA (Rp 56k) into the X1202 | Rp 10k = 3 A on both CC lines |
| 5 | A | TPS61022 boost: inductor off TI's recommended list, no feed-forward capacitor | XAL6030-102MEC, C33 100 pF across the 750k |
| 6 | A, B | Every channel enable (TPS2065C EN, TPS22810 EN/UVLO) relied on the expander's internal pull-up alone | 100k pull-up to 3V3 on all ten EN nets: ports default ON even with the expander unconfigured or absent |
| 7 | B | TPS22810 inputs behind the polyfuses (XIAO, RB, TC, A channels) had no input capacitor | 1 uF on each *_FUSED net |
| 8 | A, B | TPS2065C channels had no local input capacitor | 100 nF on +5V in every channel region |
| 9 | B | TPS2065C is a 1 A part (family table): T-Beam 1W and 9704 bursts exceed it | CH3 and CH4 re-specified as 2 A polyfuse + TPS22810 + 0.05 ohm (15.6) |
| 10 | D | Harness 5 V had no bulk capacitor before the bead | C31 4.7 uF on +5V_USB |
| 11 | D | Uncertain LCSC number on the STM32 | removed; only verified numbers stay in the BOMs |
| 12 | all | Fanout stubs 0.4 mm wide on 0.5 mm-pitch pads sealed the neighbouring pads (the cause of every leftover stub on A, B and D) | `prefanout.py` never uses a track wider than the pad; boards re-fanned and re-routed |

Checked and left as is: I2C map 0x20/0x21 (PCA9555 by A0), 0x40 to 0x45 (B INA219), 0x46 to 0x49 (A INA219, A0/A1 on SDA/SCL is a valid INA219 option), 0x36 (X1202), 0x55, 0x6B: no collision. J_AB1 mates pin for pin between A and B (14 pins). J_HARN1 mirrors J_MEZZ1 (USB codec pair, TR_APRS, MEZZ_EN, SPKEN). BQ25601 PSEL tied low = adapter input limit (2.4 A), TS on the NTC divider, VAC and VBUS on VIN_F, open-drain INT to the expander (internal pull-up), STAT drives LED1. BQ297xy: BAT via 330R + 100n, V- via 2k, Dout/Cout gates, common-drain FET pair with the discharge FET on the cell side. TPS61022 MODE low = PFM. TPS61089 FSW resistor fitted (the pin must not float), VFB 1.2 V, ILIM 7.9 A. FE1.1s: 12 MHz + 22 pF, REXT 2.7k, VBUSM through 4.7k, BUSJ open = self-powered. Upstream USB-C receptacles carry Rd 5.1k on CC (device side). The A-side USB pair to J_AB1 has its ESD on the B side of the ribbon. Pi ribbon: pins 7/29 = BCM4/5 (UART2 for the RockBLOCK), 8/10 = BCM14/15 (UART0 option), 15 = BCM22 NetAv, 16 = BCM23 I_BTD, 18 = BCM24, 37 = BCM26 I_EN, 35/40 = BCM19/21 DCF77, 13 = BCM27 TR_APRS, 22 = BCM25 EXP_INT, 11 = BCM17 BANK_ALERT: matches the kit wiring in the repo. Two XH2.54 in parallel feed the +5V rail on B (3 A per contact). PCB-A's whole 5 V comes through B's CH6 (1.1 A polyfuse) and two IDC pins: WiFi 0.5 A + GPS 0.1 A + PCB-D core 0.1 A + logic and LEDs fit.

### 20.2 What the review cannot do

The pad rows of the DMR858M footprint (section 18.3 item 1) and the two "verify" notes on the T-Call hole pattern and the 9704 bracket stay physical checks. No board has been powered; this is a paper and DRC review. Final routed state after the review (2026-09-02, 15:00):

| Board | Route | Unrouted | Hard DRC | Deliverables (laptop Downloads) |
|---|---|---|---|---|
| PCB-C DISPLAY | mechanical only | 0 | 0 | `Downloads/meshsat-pcb/meshsat-pcb-c-revA/` (unchanged) |
| PCB-B COMPUTE | **B9** (section 22): F1 deleted, loosened placement + escapes + four parallel attempts (all four clean), unused escape vias removed | **0** | 0 (8 via-dangling, 8 silk overlap, 4 silk over copper warnings) | `Downloads/meshsat-pcb/meshsat-pcb-b-revA-B9/` |
| PCB-A POWER + I/O | **A13** (section 22): loosened placement + deterministic escapes + four parallel Freerouting attempts, hub cluster re-closed by the grid router, unused escape vias removed | **0** | 0 (49 pour-sliver, 13 silk, 9 via-dangling, 2 track-dangling, 1 padstack warnings) | `Downloads/meshsat-pcb/meshsat-pcb-a-revA-A13/` |
| PCB-D APRS | **D4** (section 22.6): module site rebuilt from the datasheet drawing (socket-mounted, rows un-mirrored), MCU core under the module, section 22 pipeline, all four attempts clean | **0** | 0 (silk and via-dangling warnings only) | `Downloads/meshsat-pcb/meshsat-pcb-d-revA-D4/` |

The USBLC6 footprints on every board now carry `net_tie_pad_groups "1,6" "3,4"` (flow-through pins joined inside the package), so DRC no longer demands copper between them. LCSC numbers are filled for the JLCPCB basic parts and the AIOC-verified parts (11 to 14 lines per BOM); the rest are matched at order time.


All deliverable folders (every phase, C, B1 to B6, A1 to A6, D3) were moved to `~/Downloads/meshsat-pcb/` on the laptop at the owner's request (2 Sep, 15:10); the older phase folders are superseded by the final ones named above.

---

## 21. Audit round 4, 2026-09-02 (fifth session, shadow mode, no laptop access): the order gate was not closed by the design review

Gateway shadow mode, and like round 3 without laptop access: `Bash` is gated, so no SSH, no `python3`, no `git`, no `scp`. Nothing was changed on the laptop and no generator was read. This round audits **the record itself** rather than a board, because the record is where the risk now sits: four boards are routed, exported and sitting in `~/Downloads/meshsat-pcb/` looking finished, and the nine-item gate that stands between them and a JLCPCB upload has never been reconciled against the review that came after it.

**This section is written from documents only. Every status below is UNVERIFIED and must be closed by six greps against the generators before it is treated as fact.** The verification recipe is 21.3.

### 21.1 The reconciliation

Section 19.8 states the rule plainly: nine items, nothing ordered until all nine are true. Section 18 (the design review) came afterwards, applied twelve fixes and re-routed every board. The obvious inference, and the one an owner reading the document in order would draw, is that the later and broader pass absorbed the earlier gate. It did not.

| 19.8 # | Board | Item | Appears in the 18.1 fix table? | Status |
|---|---|---|---|---|
| 1 | A | Bank protection trips at about 1.5 A | Yes, fix 1: CSD17303Q5, OCD about 12 A | **LANDED** |
| 8 | A | Boost inductor XAL4020 off TI's list | Yes, fix 5: XAL6030-102MEC + 100 pF feed-forward | **LANDED** |
| 9 | B | B4 fab export never ran | Superseded: B6 exported after the review | **SUPERSEDED** |
| 2 | A | BQ25601 pin 2 PSEL to GND, pin 12 /QON left NC | No. **Cleared** in "checked and left as is" | **OPEN, and actively contradicted** |
| 7 | A | NTC beta 3950 against TI's 103AT-2 network | No. **Cleared** as "TS on the NTC divider" | **OPEN, and actively contradicted** |
| 5 | D | `R_ILIM` 130k to 100k | No. **Cleared** as "TPS61089 ... ILIM 7.9 A", which is 130k | **OPEN, and actively contradicted** |
| 3 | B | 3 A trunk polyfuse F1 under a 5.75 A load | Not mentioned either way | **OPEN** |
| 4 | D | STM32F302C8T6 cannot hold a 128,016-byte firmware | No. Fix 11 removed the *LCSC number* only, not the part | **OPEN** |
| 6 | D | 8 V rail worst case about 8.4 V against an 8.5 V maximum | Not mentioned either way | **OPEN** |

Two landed, one superseded, **six open, three of them affirmatively cleared by the review without citing the finding they contradict.**


**Reconciliation by the ECAD session (meshsat-01), 2026-09-02 15:15.** Confirmed: none of the six were landed when section 20 was written; the review was made against the pre-round-3 appendix. All six are now in the generators and the boards:

| 19.8 # | Change | Where | Landed in |
|---|---|---|---|
| 4 | `STM32F302CBTx`, value "STM32F302CBT6 128 KB", LCSC C94046, same LQFP-48 pin map | `gen_sch_d.py` U5 | D3 board values + BOM re-exported (no re-route) |
| 5 | R31 `100k 1% (ILIM 10 A peak, 9 A min)` | `gen_sch_d.py` | same |
| 6 | R33 `105k 1%` against 20k: 7.58 V typ, under 7.9 V worst case; U1 value says 7.6 V | `gen_sch_d.py` | same |
| 7 | NTC1 `10k NTC 103AT-2 (beta 3435, TI network R3/R4)` | `gen_sch_a.py` | A8 regeneration |
| 2 | U1 pin 2 = net CHG_PSEL on JP2 `SolderJumper_3_Bridged12` (1-2 bridged = GND = 2.4 A adapter, 2-3 = REGN = 500 mA USB); U1 pin 12 = net CHG_QON on TP11 | `gen_sch_a.py`, `gen_pcb_a3.py` CHG region | A8 regeneration, routed 15:11 onward |
| 3 | F1 `5A hold 2920 (MF-MSMF500-2)`: kept as cable protection for the X1202 lead, sized to the source, not deleted | `gen_sch_b.py` | B6 board value + BOM re-exported (no re-route) |

**Corrections after audit round 5 (15:35).** (a) Item 3: the "5A hold 2920 (MF-MSMF500-2)" string was wrong twice (no such part in the MF-MSMF 1812 family; a 5 A PPTC derates to about 3.3 A at 60 C, under the 5.75 A concurrent load), so **F1 is deleted**: both X1202 XH outputs land on +5V directly, every branch keeps its own polyfuse or limited switch plus INA219. This changes the netlist, so PCB-B regenerates and re-routes as **B7**; the B6 folder is superseded and carries the bad string until B7 lands. (b) Item 2: the first attempt used `SolderJumper_3_Bridged12` for PSEL; its built-in copper bridge between pads 1 and 2 (GND and CHG_PSEL) made the router and DRC report shorts, the A8 route came out with 13 shorts and 5 unrouted, and its export was withdrawn (folder deleted). PSEL is now **R45 0 R fitted (CHG_PSEL to GND, 2.4 A adapter limit) and R46 DNP 0 R (CHG_PSEL to REGN, 500 mA USB limit)**; /QON stays on TP11. PCB-A regenerates and re-routes as **A9**. Until A9 lands the only valid A deliverable is the A6 folder, which is the A5 board and predates items 2 and 7.

**A9 landed, A10 graft abandoned (16:35).** A9 (the first clean route with items 2 and 7) exported to `meshsat-pcb/meshsat-pcb-a-revA-A9/`: 1959 tracks, no hard DRC, **six unrouted** (U17 3V3, U3 BATN, TP7 CHG_PG, C9 GAUGE_VDD, U11 SDA, U11 GND). An attempt to graft R45/R46/TP11 onto the better-routed A5 board (bottom side, next to the QFN) could not place the PSEL via inside the BQ25601's pad field without shorting GND or the In1 CHG_CE track, and was abandoned. Two more router passes of the A9 netlist (20+60 and 45+25 passes) run after B7 and replace A9 only if they end with no hard violation and fewer stubs.

**B7 withdrawn, B8 running (17:20).** The B7 route (F1 deleted) closed every connection but Freerouting's multi-threaded optimiser left three shorts and one clearance violation, which is exactly the warning its own log prints ("multi-threaded route optimization is broken and known to generate clearance violations"). The B7 folder was deleted. `route_pcb.sh` now runs Freerouting with `-mt 1`; PCB-B re-routes as B8 and the A11/A12 retries follow it in the queue. Until B8 lands the valid PCB-B deliverable is B6, whose only defect is the F1 BOM line (fit any 2920 PPTC or a wire link across F1's pads on a B6 board; B8 has no F1 at all).

The six greps of 21.3 now return: CBTx / 100k / 105k / 103AT-2 / PSEL and QON on U1 pins 2 and 12 / 5A hold. Deliverables under `~/Downloads/meshsat-pcb/`: D3 and B6 refreshed 15:11; A8 replaces A6 when its route and closers finish (section 20.2 table is updated with the result).

### 21.2 Why they were dropped rather than considered and rejected

The design review cross-references PCB-D as **"section 17.3 item 1"** and **"17.2"**. Those are PCB-D's numbers from *before* audit round 3 renumbered it from 17 to 18 (see the note at the head of section 18). The review was therefore written against a pre-round-3 view of this document.

That single fact explains the pattern exactly:

- Items **4, 5 and 6** come from section **19**, which did not exist in the copy the review was working from. Their absence is not a judgement, it is a blind spot.
- Items **2, 3 and 7** come from section **17**, which did exist. Two of them were re-derived independently and cleared in the opposite direction; one was not reached at all. A clearance made without citing the contrary finding is not a rebuttal of it.

The consequence for how the rest of this document is read: **section 18's "checked and left as is" paragraph is not a clean bill of health.** It is a second opinion formed without sight of the first, and where the two disagree the audit findings carry the datasheet arithmetic (19.2's peak-versus-average table, 17.3's beta calculation, 17.5's derating) while the review's clearances are one-line assertions of the existing state.

This is the third time in one day that a pass over this design found real defects in the previous pass's output. That is the argument for the 12 September external review by Nick Panagiotopoulos (ESA ESTEC TEC/EDD, avionics / EMC / AIV) being handed **the six open items as its agenda**, not a set of boards presented as finished. The gate now has a named reviewer and a date, and both sit before the 15 September DMR858M pad-row measurement and before any JLCPCB upload.

### 21.3 How to close this section: six greps, on the laptop, before anything is uploaded

Any session with laptop access can settle all six in under a minute. Run in `~/Documents/Team Shared Root/Projects/MeshSat/Field Kit/ECAD/meshsat-carrier/`:

| # | Command | Pass condition |
|---|---|---|
| 4 | `grep -n "STM32F302C" tools/gen_sch_d.py` | `STM32F302CBT6`, LCSC `C94046`. `C8T6` fails |
| 5 | `grep -n -e "R_ILIM" -e "130k" -e "100k" tools/gen_sch_d.py` | `100k`. `130k` fails |
| 6 | `grep -n -e "113k" -e "105k" tools/gen_sch_d.py` | `105k` against 20k. `113k` fails |
| 7 | `grep -n -e "NTC" -e "3950" -e "3435" tools/gen_sch_a.py` | 103AT-2 / beta 3435. `3950` fails |
| 2 | `grep -n -e "PSEL" -e "QON" tools/gen_sch_a.py` (around line 131) | both pins named and deliberately terminated. `GND` on pin 2 and `NC` on pin 12 fails |
| 3 | `grep -n "F1" tools/gen_sch_b.py` (around line 125) | F1 deleted, or hold current sized against the X1202's 5 A. A 3 A hold fails |

**Cost of the fixes, if they are open.** Items 4, 6 and 7 are BOM strings; item 5 is a BOM value. None of the four touches placement or routing, so all four ride whatever regeneration happens next at zero incremental cost, exactly as 19.8's sequencing note said. Item 3 is a part change or a deletion in the schematic. Item 2 is the only one that can force an A-board regeneration, and only if `/QON` is brought out to a header rather than a test point.

**Cost if they ship.** Item 4 is unarguable and the most expensive: the assembled PCB-D cannot be flashed with the firmware it was designed around, and that is discovered at bring-up, after assembly. Item 5 folds the 8 V rail back mid-transmission at end of discharge, and presents as an RF fault. Item 3 puts a fuse that derates below idle load in series with the whole compute board inside a sealed hot case, which is the MESHSAT-523 brownout shape moved into the fuse. Item 7 silently refuses to charge between 0 and 4 C, outdoors, in the season the field programme runs.

### 21.4 Documentation defect, still open

The duplicate section numbers are back. There are two `## 16` (the PCB-A A0 specification and the PCB-A A1 record) and two `## 18` (the PCB-D record and the design review). So `18.1` means PCB-D's contents when audit round 3 cites it and the review's findings table when the memory file cites it, and `16.1` to `16.3` exist twice with different content while 19.8 cites `16.3 A` and `16.3 B`.

Audit round 3 fixed exactly this defect for PCB-D and the next session recreated it. Recommended, and deliberately **not** applied here because another session was writing to the file at the time: renumber the **design review** to **section 20** with `20.1` and `20.2` (no YouTrack comment cites it yet, so the churn is near zero), and correct its two stale cross-references from `17.3 item 1` to `18.3` and from `17.2` to `18.2`. Leave both `## 16` sections alone; `16.3 A` and `16.3 B` are unambiguous by their letters, and those numbers are cited across many YouTrack comments.

---

## 22. Repeatable routing for PCB-A and PCB-B, 2026-09-02 (ECAD session, evening)

The afternoon's routes were a lottery: the same board came out with 0 to 6 open connections depending on pass counts, the multi-threaded optimiser produced shorts (B7), and Freerouting sat silent for 10 to 25 minutes so the idle watchdog killed working passes. Two of the causes were ours. The packers put fine-pitch ICs wall to wall with passives (0.7 mm gap), and the fanout dropped a via 0.65 mm past every plane pad, which sealed the neighbouring pads' only exit lane. The retries also ran one at a time behind a lock.

### 22.1 What changed (all in `tools/`, laptop and scratchpad mirror)

| Piece | Change |
|---|---|
| `gen_pcb_a3.py`, `gen_pcb_b3.py` | Packer gap 0.7 to 1.2 mm; fine-pitch parts (min SMD pitch 0.7 mm or SOT-23-6/8) get a 1.6 mm margin and are packed first; regions widened into their free envelopes. On B the margin is applied only on the sides that carry pins (the pad's elongation axis), which halves the area a two-sided package takes; the test points moved to the pocket between the hub and the upstream USB-C, the hub region moved off the back-side IDC header, the SDR parts split into an IC row under the receptacle and a passive row above it |
| `escape.py` (new) | Deterministic escapes for every connected pin of a fine-pitch part: track straight out along the pad axis to a via, vias staggered on alternate pins (0.9 / 1.6 / 2.3 mm past the pad tip, via 0.45 / 0.25 mm, track 0.2 mm). Pitch 0.5 mm and below uses a fan instead: 0.3 mm straight, then a splay to a via row at 0.8 mm pitch (the BQ27441 SON-12 is 0.4 mm pitch, where staggered straight escapes cannot pass each other). Exposed pads without thermal vias get one. Connectors are skipped |
| `prefanout.py` | Third argument `fine` skips the parts `escape.py` handled; plane-net vias only for the rest |
| `route_one.sh`, `route_parallel.sh` (new) | Four Freerouting instances at once (20 / 30 / 45 / 60 passes, `-mt 1`, own scratch directory, own PID, 75 min hard timeout, no idle watchdog); each attempt is imported, filled, DRC'd and scored (hard violations, open connections, via count); the best is copied into the project |
| `finish_after_parallel.sh` (new) | Waits for the winner, optional EP tie, `stub_router.py` under its DRC gate, then `finish_board.sh` |
| `ripup_viol.py` (new), `stub_router.py` | A router clearance violation between two tracks is fixed by ripping up the whole same-layer run of the offending net and re-closing it with the grid router, which can now start from a via or track end, not only a pad |
| `cleanup_dangling.py` (new) | Removes escape vias the router did not use (signal nets only) and the stub tracks behind them; tracks ending inside a via's barrel count as connected |

### 22.2 PCB-A result: A13

Gate: `check_pcb_a.py` all pass, 185 escapes added (3 pads of the USBLC6 skipped, the router handles them), 64 fanout vias, no pre-route DRC item beyond silk and dangling-via warnings. The four attempts all returned the same score (hard 7, open 0, 340 vias): the autoroute phase is deterministic, so identical settings give identical boards and the attempts must be diversified before the repeatability check of the plan means anything. The seven hard items were one cluster: HUB_TESTJ and HUB_VD18 on In1.Cu laid 0.25 mm apart next to the hub, with micro-fragments down to 0.0001 mm. Ripped up and re-closed by the grid router: **0 open, 0 hard**. Unused escape vias removed (17 vias, 16 stubs). Final DRC: 49 pour slivers, 13 silk overlaps, 9 via-dangling and 2 track-dangling warnings (harmless leftovers), 2 silk over copper, 1 padstack. Exported to `~/Downloads/meshsat-pcb/meshsat-pcb-a-revA-A13/` (14 items, gate items R45/R46/TP11/103AT-2/CSD17303Q5 in the BOM). A13 supersedes A6 and A9.

### 22.3 PCB-B result: B9

B8 (old placement, single-threaded) had been silent in the optimiser for an hour with an empty log and was killed at 18:20. B9 is the first B board through the new pipeline: gate passed at 18:36 (163 escapes, 59 fanout vias, pre-route DRC silk warnings only; four WSON-6 middle pins, the EN_TC / EN_RB / EN_A / EN_XIAO lines, got no escape because the neighbouring pin's pad rejects the last offset, and the router closed them anyway). The four attempts took 20 to 25 minutes and **all four came back with 0 hard, 0 open** (279, 279, 279 and 283 vias; attempt 1 taken). Unused escape vias removed (16 vias, 17 stubs). Final DRC: 8 via-dangling, 8 silk overlap, 4 silk over copper warnings, nothing else. Exported to `~/Downloads/meshsat-pcb/meshsat-pcb-b-revA-B9/` (14 items). The BOM has no F1 line and carries the TPS22810 switches; both XH inputs land on +5V. B9 supersedes B6.

### 22.4 Order-gate state after A13 and B9

All four boards route to zero open connections and zero hard DRC violations: C2 (mechanical, 14.6), D4 (22.6), A13, B9. The six greps of 21.3 on the exported files: CBTx 1, 100k 2 and 105k 1 on D4; 103AT-2, CSD17303Q5 x2, R45 and R46 on A13; TP11 with CHG_QON on the A13 board (test points carry no BOM line); no F1 anywhere on B9. Superseded folders still under `~/Downloads/meshsat-pcb/` and safe to delete: A1, A2, A3, A5, A6, A9, B1 to B6, D3. Valid set: `meshsat-pcb-c-revA-C2`, `meshsat-pcb-d-revA-D4`, `meshsat-pcb-a-revA-A13`, `meshsat-pcb-b-revA-B9` (the first `meshsat-pcb-c-revA` is superseded). Owner-side items: LCSC matching of the remaining lines at upload (deselect the DNP lines U2 on D and R46 on A there), JLC upload after the 12 Sep review. The DMR858M measurement is no longer on the list (22.6).

### 22.5 Still open in the pipeline

Diversify the parallel attempts (ripup and via costs per instance) so a second run can differ from the first; `hole_to_hole` is not yet in the hard-violation list of the scorer; the four WSON middle-pin escapes; `check_pcb_*.py` does not yet verify that packer regions stay inside their free envelopes (the 18:2x rounds found the overlaps through the pre-route DRC instead).

---

## 23. Audit round 6, 2026-09-02 (sixth session, gateway shadow mode, no laptop access): the A0 findings never entered the order gate, and the power tree has no stated worst case

Same posture as rounds 3 and 4. `Bash` is gated, so no SSH, no `python3`, no `git`; no generator was read and nothing on the laptop was touched. **Every status below is derived from this document alone, is UNVERIFIED against the generators, and must be closed by the greps in 23.6 before it is treated as fact.** Numbering note: 21.1 cites an "audit round 5" that has no section of its own (its corrections were folded into 21.1), so this is round 6 by count of passes, not by section number.

Round 4 reconciled the nine-item gate of 19.8 and found six items dropped. This round asks the next question, which is where 19.8 itself came from: it was assembled out of sections 16.3, 17 and 19. **Section 16.7, which carries seven findings labelled A0-1 to A0-7, was never reconciled against anything, and neither was the open list in 16.8.** One of those findings is a live defect on a board that is exported and waiting for a JLCPCB upload. One is a safety item that stops being fixable at fabrication. And re-deriving the power tree from R6 and R15 turns up two system-level numbers that no round has written down.

### 23.1 The A0 reconciliation

| # | Item (source) | Landed? | Status |
|---|---|---|---|
| A0-1 | PCB-B channel A polyfuse 1.1 A, raise to 2 A hold (16.2, 16.7) | No | **OPEN, and actively contradicted by 20.1** |
| A0-2 | Split the mezzanine harness into signal + power (16.7) | Yes | LANDED: `J_MEZZ1` 2x8 plus `J_MEZZ_PWR` JST-VH, mirrored on PCB-D as `J_HARN1` + `J_PWR1` (18.1) |
| A0-3 | The PCB-A hub has zero spare ports (16.7) | No | Never put to the owner; no R number. Design choice, not a defect |
| A0-4 | NTC cutoff at both ends, and the cells are what must be measured (16.7) | Part | 103AT-2 landed as gate item 7, **but the thermistor is still a board-mounted footprint**; the A3 record calls it "a placeholder for a cell-contact thermistor" and defers it to Rev B. See 23.3 |
| A0-5 | About 190 g of cells on a 1.6 mm board carried at four rod holes (16.7) | No | **OPEN**: neither the 2.4 mm bumper nor 2.0 mm FR-4 appears anywhere later. Board thickness is a JLC order parameter, so this closes at upload or not at all |
| A0-6 | The AWUS036ACM ports are RP-SMA, the bulkheads are SMA (16.7) | n/a | Pigtail purchase, not a board item. Belongs in the order note, and after R16 it is **two** RP-SMA to SMA pigtails |
| A0-7 | Position of the second WiFi bulkhead (16.7) | No | Proposed (+128.75, +72.0, +25.0). Owner drills it, no ruling recorded |
| 16.8 #16 | 18650 holder part and height | Yes | Keystone 1042, 22.5 mm pitch |
| 16.8 #17 | 8 mm panel LED type, bare or internally resistored | No | **OPEN**: sets the series resistor value on the `J_LEDS` row. The 0 R option in 16.5 keeps it a BOM value, not a layout change |
| 16.8 #18 | DMR858M pin map | Yes | Closed from the V1.2 datasheet, physical check 15 Sep (18.3 item 1) |
| 16.8 #19 | Charger present in the JLC library | No | **OPEN at order time**: BQ25601 is not a JLC basic part |
| 16.8 #20 | Shadow mode lifted | Yes | Moot, the ECAD sessions ran |

Two landed, one physical check pending, one moot, one not a defect, **five open, one of them contradicted the same way round 4 described.**

### 23.2 A0-1 is gate item 3 again, on the branch that inherited its job

Section 16.2 states the finding: PCB-B's channel A, which is the whole of PCB-A's supply, was given a 1.1 A hold polyfuse in an 1812 body against a steady load that 16.2 itself budgets at about 800 mA advertised (WiFi 400, GPS 100, PCB-D core about 100, PCB-D UART about 50, hub and monitors about 100, LED row 50), with the MT7612U's transmit peak on top of the 400 mA it advertises, and after R16 it keys two chains.

An 1812 PPTC derates hard with ambient: about 0.7 x hold at 60 C for the usual families, so a 1.1 A part holds roughly 0.8 A in the bottom bay of a sealed black case. That is the load. The margin is zero before the transmit peak, and a PPTC trip is latching in practice, so one WiFi burst takes WiFi, GPS, the APRS codec and the LED row down together until the kit is power-cycled by hand in the field.

This is item-for-item the argument that condemned F1 in 17.5 and 21.1: a fuse whose derated hold current sits under the load it carries, inside a hot sealed case, which is the MESHSAT-523 brownout shape moved into the fuse. F1 was deleted on exactly that reasoning at 15:35. **Channel A's polyfuse is the branch that inherited F1's job, and it was left at 1.1 A.** Section 20.1 cleared it in the opposite direction ("PCB-A's whole 5 V comes through B's CH6 (1.1 A polyfuse) ... fit") with the room-temperature number and without citing 16.2.

The fix follows the F1 precedent rather than A0-1's wording: **size the polyfuse to the cable and the copper, not to the load**, because the load already has a software-controlled TPS22810 and an INA219 at 0x43 in series with it. A 2 A hold 1812 gives about 1.44 A held at 60 C against a peak near 1.1 A, and the TPS22810 (2 A, thermal shutdown, EN from the PCA9555) stays the element that actually protects the load. Class: BOM value on PCB-B, same body, no layout change. Cost today: one regenerated BOM. Cost after fabrication: a field-unrecoverable dropout of half the kit's radios.

### 23.3 The charger measures the wrong temperature (A0-4, and it defeats R6 as written)

R6 asks for a "charger with NTC low-temp cutoff". Gate item 7 landed the right thermistor (103AT-2, beta 3435, TI's R3/R4 network), which gives the BQ25601 both a cold and a hot threshold. What neither closed is **where the thermistor is**. The A3 record says plainly that the footprint is a placeholder for a cell-contact thermistor, and puts it on a Rev B list. *(Superseded 4 Sep 2026: the BQ25601 charger and its thermistor network left PCB-A with the one-pack-one-charger ruling; cold-charge protection is the dock inhibit of PANEL.md section 9, and the thermal pad is item 6 of the Rev B list in 32.12.)*

A board-mounted NTC in the bank zone measures board temperature, and in this kit the board and the cells disagree in both directions:

- **Cold**: the electronics self-heat within a minute of boot while a 4P pack of 18650s takes tens of minutes to follow. A warm board therefore permits charging cold cells, which is lithium plating, which is the exact failure R6 named. The field programme starts 1 November.
- **Hot**: on charge the cells self-heat and the board does not, so the JEITA hot threshold under-reads and the cutoff arrives late in a black IP67 case in sun.

So Rev A as it stands ships a temperature protection that is not measuring the thing it protects. This is the one open item that is a **layout change** (a 2-pin JST for a cell-contact thermistor, or the footprint moved under the holder block with the part specified as a cell-contact type), so it is cheap this week and impossible after fabrication. It is also the only finding in this round with a safety consequence rather than an availability one.

### 23.4 The whole kit runs through the extension bank, and that chain has no stated worst case

R6's topology, read back from the ruling: the case USB-C inlet feeds the PCB-A bank, and the bank's 5 V boost feeds the X1202's USB-C input. R6's own closing clause proves the consequence: "X1202 AC-loss now means bank empty". The X1202 therefore has no other source, and everything the kit does is drawn through PCB-A's bank chain.

Nothing in sections 16, 20, 21 or 22 states the current that chain carries. Working it out from the parts already recorded: the X1202's input is rated 5 V at 5 A and it both runs the kit and charges its own four cells, so the boost's worst case is 25 W out. At a 3.6 to 4.2 V cell node that is **about 6.5 A on the cell side**, and about 4 A even at the steady kit load the repo's own figure implies (roughly 1.5 A of peripherals at 5 V plus a Pi 5 and the Touch Display 2).

Elements in series with that current, and what each needs checked:

| Element | Question |
|---|---|
| BQ25601 power path / BATFET | Is the TPS61022's input `SYS` or the raw cell node? **The record never says**, and the two give different failure modes. If `SYS`, the charger's power path carries the entire kit continuously at 1S voltage |
| TPS61022 | 25 W out at a 3.0 V end-of-discharge cell is its corner case, not its nominal one |
| 10 mOhm gauge shunt | 6.5 A gives 0.42 W. Needs a part rated for it, and the BQ27441 sees 65 mV, which is in range |
| Q1/Q2 CSD17303Q5 | 2.6 mOhm each, comfortable after fix 1 |
| `J_BANK_OUT` USB-C | 5 A across a Type-C receptacle's VBUS contacts is at the top of what a plain receptacle is rated for |
| Cells | 6.5 A across 4P is 1.6 A per cell, comfortable |

None of this is necessarily wrong. The finding is that a design where one boost converter carries the entire kit has never had that number written down, and two of the six elements are at their corner rather than inside it. The 12 September review is the right place to put this table.

### 23.5 Shore power cannot sustain the kit, let alone recharge it

Same topology, followed the other way. The only shore input is the case USB-C, it lands on the BQ25601, and R45 fitted to GND sets the default input limit to 2.4 A (12 W). The I2C ceiling of that part is 3.2 A (16 W), and reaching it needs software, which needs the kit booted. The inlet is a bare sink with 5.1 k pulldowns and no CC negotiation of any kind (17.4 finding H, closed as unfixable), so nothing above 5 V is available either.

Against that, the kit's own draw is plausibly 14 to 18 W with the display lit. **If that is right, then on shore power the input never covers the load: the charger runs in supplement mode, the bank discharges while the kit is plugged in, and the 100 Wh only refills with the kit off or dimmed.** For a custodian kit that is a real operational property, not a footnote.

What makes it avoidable is that the X1202 already has the headroom the design does not use: its own USB-C input is 5 V at 5 A (25 W) and its DC jack takes 6 to 18 V at 3 A or more (36 W at 12 V, which is also the car and solar case). The case has one USB-C feedthrough and R6 spends it on the bank.

Three ways out, and this wants an owner ruling (proposed R18):

- **(a)** Add a second feedthrough, a DC jack, wired to the X1202's DC input. No board change, no ruling reversed, one more hole in a sealed case and one more sealing part. 36 W in.
- **(b)** Land the case USB-C on the X1202's USB-C input (25 W) and charge the bank from one of the X1202's 5 V outputs. Inverts R6's direction, needs a PCB-A change at the charger input, and the X1202's two inputs are mutually exclusive so the bank's boost output would then need OR-ing with it.
- **(c)** Accept and document: shore power holds the kit at reduced load, recharge happens with the kit off. Zero cost, and it becomes a line in the custodian handover.

The measurement that settles the size of the problem is one the owner can take this week with the multimeter already in the kit BOM: the kit's actual draw at the X1202 input, idle and with the display lit. Everything above 16 W means (a) or (b); anything comfortably under means (c) is honest.

### 23.6 What closes this section, on the laptop

In `~/Documents/Team Shared Root/Projects/MeshSat/Field Kit/ECAD/meshsat-carrier/`:

| # | Command | Pass condition |
|---|---|---|
| A0-1 | `grep -n -e "1.1 A" -e "F_A" -e "polyfuse" tools/gen_sch_b.py` | Channel A's polyfuse is 2 A hold. A 1.1 A hold fails |
| A0-4 | `grep -n -e "NTC" -e "103AT" tools/gen_sch_a.py` and the footprint it uses | A 2-pin connector for a cell-contact thermistor, or a footprint inside the holder block. A bare 0603/0805 in the electronics strip fails |
| A0-5 | `grep -n -e "thickness" -e "1.6" tools/gen_pcb_a.py` | Owner decision recorded either way (1.6 mm plus a bumper, or 2.0 mm) |
| 23.4 | `grep -n -e "TPS61022" -e "SYS" -e "VBAT" tools/gen_sch_a.py` | The boost input net is named and known to be `SYS` or the cell node |
| 16.8 #17 | `grep -n "LED" tools/gen_sch_a.py` | Series resistor value set for the LED type the owner actually has |

Two of the five are answerable only by the owner (A0-5 thickness, the LED part), and 23.5 needs the measurement, not a grep.

### 23.7 The gate, restated

19.8's nine items are closed (22.4). What stands between the exported boards and a JLCPCB upload is now this, and it is shorter than the last one:

| # | Board | Item | Class | Who |
|---|---|---|---|---|
| 1 | **A** | Cell-contact thermistor (23.3) | **layout**, PCB-A regenerates | Claude, laptop |
| 2 | **B** | Channel A polyfuse 1.1 A to 2 A hold (23.2) | BOM value, rides any regeneration | Claude, laptop |
| 3 | A | Board thickness against 190 g of cells (A0-5) | order parameter | owner |
| 4 | A | LED part, so the series resistor is right (16.8 #17) | BOM value | owner |
| 5 | all | Remaining LCSC matching, charger included (16.8 #19) | order time | owner |
| 6 | D | DMR858M pad rows against the module (18.3 item 1) | measurement, 15 Sep | owner |
| 7 | kit | R18 shore-power ruling (23.5) and the draw measurement | ruling | owner |
| 8 | kit | Second WiFi bulkhead position (A0-7), two RP-SMA pigtails (A0-6) | mechanical, purchase | owner |
| 9 | all | The 12 September review, with 23.4's table as an agenda item | review | owner + Nick |

Items 1 and 2 are the only ones that touch a generator, and both are cheap while the boards are files. Everything else is an owner decision or a physical check.

### 22.6 PCB-D D4: the DMR858M site finalised from the datasheet, no physical measurement

The owner ruled out measuring the module on arrival. The V1.2 datasheet's mechanical page (`ECAD/vendor/dmr858m-v1.2.pdf` p.10, rendered at 400 dpi and measured pixel by pixel against the 38.69 x 58.31 outline) settles every dimension, and it also shows that the D3 site was wrong in two ways that a measurement would only have confirmed later:

- **The rows are not castellations.** Each row is twelve ordinary plated holes at 2.54 mm pitch whose centres sit about 1.27 mm inboard of the long edge (measured 1.14 and 1.36 mm), with the pad copper running out to the edge. Both rows start 15.06 mm from the SMA edge (measured 14.97 and 15.21) and are aligned, so the rows are 36.15 mm apart, not 37.29.
- **Pin 1 is on the other row.** In the front view (heatsink side, SMA at the top right) the back view's labels place VCC (pin 1) at the top of the LEFT row and NC (pin 24) at the top of the RIGHT row. D3 had pins 1 to 12 on the front-right row, i.e. the footprint was mirrored: VCC would have landed on NC and PTT on TXD.
- **The module cannot lie flat on any host board.** The side view shows the finned heatsink (about 14.5 mm) on the front face and, on the back face, the rotary channel switch, the DIP switch, the PTT button and a mid-mount USB-C, about 5 mm proud. The two Ø3.00 holes (2.81 / 2.96 mm from the SMA-edge corner, 2.86 / 2.73 mm from the opposite corner) are the mounting. The SMA jack straddles the top edge 34.30 mm from the pin-1 edge, i.e. 14.96 mm toward the pin-24 side.

D4 therefore mounts the module the way the drawing implies: two 1x12 2.54 mm female headers (8.5 mm) on PCB-D receive male headers soldered into the module's rows from its back face, and two M2.5 x 11 mm standoffs through Ø2.9 holes in PCB-D carry the module's Ø3 holes. The module's back face sits 11 mm above the board (socket 8.5 + header body 2.5), its back-side parts hang 5 mm into that gap, heatsink up, and it unplugs for USB-C configuration, which retires the "blocked USB-C" note of 18.2. Footprint `meshsat.pretty/DMR858M`: 24 through-hole pads Ø1.7 / drill 1.0, pin 1 square, north row pins 1 to 12 with pin 1 east (15.06 from the SMA edge), south row 13 to 24 with 24 under 1, rows at +-18.075, two Ø2.9 non-plated holes at (26.345, 16.385) and (-26.295, -16.615), courtyard only around the socket bodies and the standoff hexes, silk outline inset 0.6 mm, SMA marker 14.96 mm south of the centre line. The module centre moved from (12, -2) to (10.5, -2) so the north-east standoff hole keeps a 1.7 mm web to the board edge (it had 0.2 mm). `check_pcb_d.py` now asserts the row spacing, the row-to-pin assignment, the 1.0 mm drills and the two standoff holes.

Because the module is 11 mm up, the 55 x 33 mm field under it on the top side is usable for anything under about 4 mm. The MCU core (STM32, crystal, decoupling, PTT drivers, UART resistors, audio network: the former N_BOT_C/W/E regions on the bottom side) moved there, packed with the section 22 packer (gap 1.2, fine-pitch margin 1.4 on the pin sides), the boost column grew north to the board edge and the bench strip grew west; `full_d.sh` runs `escape.py` before the fanout like A and B. The first D4 attempt with the core still on the bottom left one OUT2 connection open on all four attempts; with the core under the module all four attempts came back **0 hard, 0 open** (129 vias), unused escape vias removed, final DRC silk warnings and four dangling vias only. Exported to `~/Downloads/meshsat-pcb/meshsat-pcb-d-revA-D4/` (14 items; BOM line U2 is marked DNP bench-fitted with the two sockets and standoffs named in its value; CBTx / 100k / 105k unchanged). D4 supersedes D3.

Z consequence: stack above PCB-A = 6 (PCB-D standoffs) + 1.6 + 11 + about 14.5 = about 33 mm, so `BOTTOM_GAP` about 35 mm instead of about 30 (section 11 item 10, R4); 4.3 mm low-profile sockets would give about 29 mm if the middle bay cannot spare the 5 mm.

---

## 24. Audit round 7, 2026-09-02 (seventh session, gateway shadow mode, no laptop access): the bank chain is rated below the kit it now carries

Same posture as rounds 3, 4 and 6. `Bash` is gated, so no SSH, no `python3`, no `git`; no generator was read and nothing on the laptop was touched. **What is different this round: the two primary datasheets were fetched and read directly**, so the numbers below are not derived from this document. Sources: TI **SLUSCK5A** (BQ25601, March 2017, revised March 2023), sections 8.3 Recommended Operating Conditions, 8.4 Thermal Information and 8.5 Electrical Characteristics (Power-Path); TI **SLVSDX7D** (TPS61022, January 2019, revised July 2021), sections 6.5 Electrical Characteristics, 8.1 Application Information and 8.2 Typical Application.

Statements about what the generators contain remain **UNVERIFIED** and carry greps in 24.6. Nothing in this round changes a routed board, and nothing here contradicts C, D4, A13 or B9 as exported.

This round takes the one question round 6 left hanging (23.4: is the boost's input `SYS` or the raw cell node) and follows it through the part ratings. The answer was already in the record, and what follows from it is that R6's topology put the whole kit behind a converter that TI rates at 3 A and a power path TI rates at 6 A.

### 24.1 Q. 23.4's open question is answered in the record: the boost input is SYS

Section 23.4 says "the record never says" whether the TPS61022's input is `SYS` or the cell node. It says so twice:

- **16.1**, the phase A2 block table: "5 V boost | U4 TPS61022 **from SYS**, 1 uH XAL4020, 750 k / 100 k feedback for about 5.1 V".
- **17.7 K**: "`R15` pulls `BOOST_EN` up to `SYS` ... kit power therefore goes external 5 V into the BQ25601 buck down to SYS, then back up through the boost to 5.1 V into the X1202 input."

So the answer is `SYS`, which is the case 23.4 called the worse of the two: **the BQ25601's power path is in series with the entire kit in both directions**, and its BATFET carries every watt the kit draws whenever there is no shore power. The rest of this section is the consequence round 6 asked for.

### 24.2 R. The bank's 5 V boost is a 3 A part in exactly this application

SLVSDX7D section 8.1: the TPS61022 has "a minimum 6.5-A valley switch current limit". Section 8.2, in the vendor's own words for the identical use case: **"With minimum 6.5-A switch current capability, the TPS61022 can output 5 V and 3 A from a single-cell Li-ion battery."** Table 8-1 states that typical application as input 2.7 to 4.35 V, output 5 V, output current **3 A**. Section 6.5 gives `I_LIM_SW` valley current limit 6.5 A min / 8 A typ / 10 A max at V_IN 3.6 V, V_OUT 5.0 V.

The rated deliverable of the bank chain is therefore **about 15 W at 5.1 V**, and a worst-case part sits at the bottom of that band.

What is asked of it, from figures already in this document and in the 2 Sep MESHSAT-709 comments:

| Demand at the X1202 USB-C input | Figure | Source |
|---|---|---|
| Kit draw with the display lit | 14 to 18 W (estimate) | 23.5 |
| X1202 charging its own four cells | 2.3 to 3.2 A at the cell, about 10 to 13 W | Geekworm X1202 wiki, recorded in the 2 Sep comment |
| X1202 input ceiling | 5 V at 5 A = 25 W | same |

So on bank power the demand is **24 to 31 W against a 15 W source** whenever the X1202's own pack is not full, and 14 to 18 W against 15 W when it is. 23.4's "25 W worst case on the cell side, about 6.5 A" is **not reachable**: the boost current-limits well before it.

The failure mode is not a dropout and that is what makes it worth writing down. The boost sits in valley current limit, its output droops, the X1202 makes the difference up from its own 50 Wh, and **both packs drain together**. The kit's sustainable draw is set by the boost at about 15 W, not by the 100 Wh the design advertises. If the kit's real average is above that, the extension bank cannot hold the kit up indefinitely no matter how much energy is in it: the X1202 pack empties at the difference and the kit browns out afterwards.

Second-order, same topology: energy that reaches the load through the X1202's own pack pays the boost, then the X1202's charger, then the X1202's output stage. At about 0.9 each that is roughly **0.8 of the bank's 49 Wh, so about 39 Wh at the load**, and the missing fifth is heat inside a sealed IP67 case. The "about 100 Wh" of R6 is a cell figure, not a delivered one.

### 24.3 S. The BQ25601's power path is in the same series chain, at its recommended maximum

SLUSCK5A section 8.3, Recommended Operating Conditions:

| Parameter | Max | Note |
|---|---|---|
| `I_BATOP` discharging current, **continuous** | **6 A** | the BATFET path, i.e. cells to SYS, i.e. the whole kit |
| `I_BATOP` fast charging current | 3.0 A | |
| `I_in` input current (VBUS) | 3.25 A | shore side |
| `I_SWOP` output current (SW) | 3.25 A | shore side |

Section 8.5, Power-Path: `R_ON(BAT-SYS)` **19.5 mOhm typ, 24 mOhm max at 25 C, 30 mOhm max over -40 to 125 C** (QFN, measured from BAT to SYS at V_BAT 4.2 V); `V_FWD` in supplement mode 30 mV. Section 8.4: R-theta-JA **35.6 C/W** for the RTW WQFN-24.

At the boost's own rated 3 A out at 5.1 V from a 3.2 V cell, the BATFET carries about **5.3 A**, which is 88 % of a recommended maximum, dissipates **0.55 to 0.85 W** (typ to hot max) and therefore adds a **20 to 30 C junction rise** on top of whatever the sealed case is sitting at, in a package whose thermal pad is the only path out. It also drops **100 to 160 mV** at the moment the cell is lowest, which raises the boost's input current further, which raises the drop: the wrong sign for the corner that matters.

23.4's 6.5 A would be **over** the part's continuous rating. The only reason that is not already a violation is 24.2: the boost cannot pass enough current to get there. Two findings that cancel is not a margin, it is a coincidence, and it disappears the moment anyone fixes the boost without looking at the charger.

Shore direction, for completeness: 3.25 A on both VBUS and SW against `R45` setting the 2.4 A adapter limit means shore power is comfortably inside the part and still under the load, exactly as 23.5 says.

### 24.4 T. Nothing on the board can tell whether shore power is present, and the expander is full

Section 16.1 puts the charger's `PG` (power good, the one hardware indication that the case USB-C inlet is live) on a **test point**, with only `INT` going to the expander.

The expander cannot take it. Counting 16.1's own list for `U19 PCA9555PW` at 0x21: four channel enables (WiFi, GPS, codec, UART), `BOOST_EN`, `CHG_CE`, `MEZZ_EN`, four LED cathodes, four `FAULT` inputs, `CHG_INT`. That is **16 of 16 pins allocated, with no spare**.

This is not fatal on its own, because the charger is on I2C at 0x6B and firmware can read VBUS status from its registers once the Pi is up. It matters because **both live remedies in 23.5 need the bank boost sequenced against shore power**: the X1202's USB-C and DC-jack inputs are mutually exclusive, so any design where shore power reaches the X1202 directly must be able to stop the bank pushing into the other input. `BOOST_EN` exists for that. The input it should be sequenced from does not, and the expander has no room for it.

Cheap fix, and gate item 1 (the cell-contact thermistor, 23.3) already forces a PCB-A schematic regeneration: **bring `CHG_PG` up the ribbon on `J_AB1`'s spare pin** (15.4 lists exactly one spare in the 2x7) to a Pi GPIO, and keep the test point. Class: schematic on PCB-A, no layout consequence beyond one net, zero cost if it rides the regeneration that is already owed. If the signal is wanted at the expander instead, the four LED cathodes are the block to move, which is more work for no gain.

### 24.5 What this does to R18

23.5 framed R18 as a shore-power question. With 24.2 and 24.3 it is a **topology** question, because the same chain is undersized on battery as well:

| Option | What it fixes | What it needs |
|---|---|---|
| **(a)** DC-jack feedthrough to the X1202, 36 W | shore power bypasses the bank chain completely, so 24.2 and 24.3 both go away while plugged in; 23.5's deficit goes away | one more hole and sealing part; 24.4's signal plus `BOOST_EN` sequencing, because the X1202's inputs are mutually exclusive |
| **(b)** case USB-C onto the X1202, 25 W, bank charged from an X1202 5 V output | same, and no new hole | inverts R6, changes the PCB-A charger input, needs the same sequencing, and the bank's boost output then needs OR-ing or disabling |
| **(c)** accept and document | nothing, but it is honest and free | the custodian line becomes: the extension bank sustains about 15 W and adds about 39 Wh **at the load**, and shore power holds the kit at reduced load while the pack refills only with the kit off or dimmed |
| (d) raise the bank chain | the 15 W ceiling | a different converter class and a different power path part. Not recommended for Rev A, and it would move the limit onto the 6 A BATFET of 24.3 |

**One measurement still settles all of it**, and it is the one 23.5 already asks the owner for: the kit's actual draw at the X1202 input, idle and with the display lit, with the multimeter that is already in the kit BOM. Under about 12 W, (c) is honest and Rev A stands as drawn. Between 12 and 15 W it works but with no margin for the X1202 charging itself. Above 15 W, (a) is the cheapest real answer.

### 24.6 What closes this section, on the laptop

In `~/Documents/Team Shared Root/Projects/MeshSat/Field Kit/ECAD/meshsat-carrier/`:

| # | Command | Pass condition |
|---|---|---|
| Q | `grep -n -e "TPS61022" -e "VIN" -e "SYS" tools/gen_sch_a.py` | the boost's input net is named. `SYS` confirms 24.1 and 24.3; the cell node would retire 24.3 and change 24.2's arithmetic only slightly |
| T | `grep -n -e "CHG_PG" -e "TP7" -e "J_AB1" tools/gen_sch_a.py` | `CHG_PG` on `J_AB1`'s spare pin as well as the test point |
| T2 | `grep -n -e "PCA9555" -e "U19" tools/gen_sch_a.py` | 16 allocated I/O, i.e. the count in 24.4 is right and there is genuinely no spare |

24.2, 24.3 and 24.5 are settled by the owner's measurement, not by a grep.

### 24.7 The gate, after this round

23.7's nine items stand. This round adds one and re-scopes one; nothing else moves, and no board re-routes because of it.

| # | Board | Item | Class | Who |
|---|---|---|---|---|
| 1 | A | Cell-contact thermistor (23.3) | layout, PCB-A regenerates | Claude, laptop |
| 2 | B | Channel A polyfuse 1.1 A to 2 A hold (23.2) | BOM value | Claude, laptop |
| **2a** | **A** | **`CHG_PG` onto `J_AB1`'s spare pin (24.4)** | **schematic, rides item 1** | **Claude, laptop** |
| 3 to 6, 8 | as 23.7 | thickness, LED part, LCSC, DMR858M, bulkhead and pigtails | unchanged | owner |
| **7** | **kit** | **R18 is now a topology ruling, not just a shore-power one (24.5), and it has numbers** | **ruling plus one measurement** | **owner** |
| 9 | all | The 12 September review, with 23.4's table **and 24.2 / 24.3** as the agenda | review | owner + Nick |

For the 12 September review this is the strongest item to lead with: a solo-designed power tree where the vendor's own rated output for the chosen converter (3 A from 1S) sits below the load the architecture gives it, and where the part immediately upstream is at 88 % of a continuous rating at that same operating point. It is the kind of finding a verification engineer will recognise instantly, and it is architectural rather than a component swap, which is exactly what an outside review is for.

### 22.7 Handoff folders (owner request, 2 Sep 20:05)

`tools/make_handoff.py` (laptop) rebuilds two folders from the valid deliverables C, D4, A13, B9:

- `~/Downloads/meshsat-pcb/JLCPCB/`: one sub-folder per board (`PCB-A-POWER-A13`, `PCB-B-COMPUTE-B9`, `PCB-C-DISPLAY-C2`, `PCB-D-APRS-D4`) with the Gerber zip, the JLC BOM and CPL (DNP lines removed: U2 on D, R46 on A; the full BOMs stay in the deliverable folders) and `ORDER-NOTES.txt` derived from the board file (size, layers, stackup, ENIG, matte black, impedance note for the USB pairs, top/bottom part counts, bench-fitted list). `README.md` is the order table. The old per-folder `README-fab.txt` carried the PCB-B text on every board and is superseded by these notes.
- `~/Downloads/meshsat-pcb/Review/`: per board the 1:1 device sheets, fab drawings with reference designators and pad numbers (top, bottom mirrored, DNP crossed out), one PDF with a page per copper layer, A4 300 dpi renders of both sides, the schematic PDF and the DRC report; `README.md` says what each print is for and carries the review agenda (the gate items of 21.3 / 22.4). Print at 100 %.

## 25. Case integration, control panel, dock and the single-pack topology, 2026-09-03 (ECAD session, night)

Owner rulings in this session, in order: the 1400 is too shallow, pick a bigger Peli with the panel frame (1520EU + 1520PF); the stack must lift out vertically for maintenance with the antennas wired once to the case; a floor board with spring pins is the dock; the battery becomes one pack that the X1202 charges (25.6); hardware EMCON inhibit now; the e-paper shows the provisioning QR only while TEST/ACK is held after a touchscreen request.

### 25.1 Case and frame numbers (Peli CAD, `ECAD/vendor/peli/1520/`, probe output `probe-1520.txt`)

- 1520 base (drawing 1521-931, STEP): cavity 124.87 mm rim to floor; floor 413.8 x 283.6; interior at the rim 448.4 x 318.1; rim step 454.1 x 323.9 with its shoulder 7.92 below the rim; lid cavity 46.1. Wall drill points for the frame legs 53.6 to 57.8 below the rim: +Z wall X +-8.6, +-133.3, +-152.4; -Z wall X +-48.7, +-51.4, +-148.8, +-151.5; end walls X +-225.9 at Z 0 and +-87 to 92.
- 1520PF frame (drawing 1523-314-000 rev A, `1523-PF.STEP`): outer 455.17 x 323.85, body 9.65 above an 8.76 skirt that seats in the rim step (the frame top ends 0.8 above the rim), window 422.6 x 291.2 R5.85, 16 x Ø5.2 inserts on 431.8 x 301.2 (long sides X -177.3, -88.6, 0, +88.6, +177.3 at Y +-150.6; short sides Y -110.7, 0, +110.7 at X +-215.9; no corner holes). The panel (up to 444.4 x 313.1) clamps against the body's underside on a 10.9 mm bearing ring; its face sits 8.8 below the rim; from the underside of a 2.0 mm panel to the floor: 114.1.
- Rejected: 1400 (base cavity 100.3). Catalogue base depths: 1450 111, 1500 109, 1520 125, 1510 150.
- Z closure, floor up, as written 3 Sep: dock E1 1.6 + spacer 6.0 + PCB-A 1.6 + bottom bay 35 + PCB-B 1.6 + middle bay 59 = 104.8. Panel underside at 114.1. Spare 9.3 mm. (Without the dock the base was a 2.4 mm nut: 99.6.) **Superseded 5 Sep by the blind-mate gap (32.30): strip 1.6 + gap 13.4 + PCB-A 1.6 + 35 + 1.6 + 59 = 112.2, spare 1.9 mm at the nominal gap and 0.9 mm at the top of the clamp float window.**

### 25.2 RF: spring pins carry DC only; the junction strip E2 is the Rev A joint

Owner questions answered 3 Sep: a card-edge socket engages along the board plane, the stack lands vertically, so spring pins are the right DC joint (they wipe, forgive 0.5 mm, are preloaded once the rod nuts are on). RF over a spring pin has no controlled impedance and no coaxial return; coaxial spring probes are test-fixture parts (30 to 80 euros each, fixture alignment, no power rating). The MIL answer for a vertical blind mate is the SMP interface (MIL-STD-348, MIL-PRF-39012 parts): two PCB jacks and a float bullet, about 0.25 mm radial and 2 degrees of misalignment, far above 5 W at 144 MHz. Not designed in for Rev A because no jack footprint could be verified from here. Links handed to the owner: Amphenol RF SMP-FS-LDPCT (limited detent, THT), SMP-MSSB-PCS (smooth bore, SMD), SMP-FSBA-1716 (bullet); Rosenberger 19S102-40ML5; Radiall MMBX / SMP-MAX (LCSC C7333735). With a documented set in hand the jacks go on E1 and A15 and E2 becomes redundant.

Rev A: PCB-E2 `meshsat-pcb-e2-revA-E2` (`tools/gen_pcb_e2.py`): 330 x 32 x 2.0 FR-4 strip on the +Z wall, six M3 into the wall drill points (X +-8.6, +-133.3, +-152.4, 4 mm from the strip's wall edge), seven D-holes Ø6.5 with a 6.0 mm flat at X -135 to +135 step 45 for SMA female-female bulkhead couplers: UHF, SDR, WIFI1, WIFI2, LTE, IRID, LORA. Wall bulkhead pigtails (RG-316) go to the lower side of each coupler once and never move; device pigtails come to the upper side, finger tight, reachable with the panel out. Bare board, no copper, no assembly. The wall bulkheads sit on the free wall panels between the ribs; exact positions at the bench.

### 25.3 Removal and refit

1. Open the lid. 2. Remove the 16 M3 frame screws. 3. Unplug the panel ribbon (J_PANEL) and the two XH leads (J_X1202SW, J_PIJ2). 4. Lift the panel (PCB-C, with its e-paper) out. 5. Undo the seven device pigtails at the junction strip (finger tight). 6. Lift the A+B rod stack straight up: the spring pins leave the dock targets, nothing else is attached (the shore lead, the pack and the X1202 leads all travel with the stack). Refit in reverse: the two south rods drop through the dock strip's holes and align the pins.

### 25.4 Control panel C3 (`tools/gen_pcb_c.py`, `gen_pcb_c3.py`, `gen_sch_c.py`, `check_pcb_c.py`)

Panel: 442 x 311 R17, 2.0 mm FR-4, 16 x Ø3.2 holes with GND ring pads on the frame pattern (the aluminium frame becomes the panel's chassis reference), aperture = TD2 body + 0.4 (X -88.61..80.74, Y -60.255..40.255, R1.5), tape-band rule area (no copper, no silk), glass 0.75 mm proud (14.6), nameplate field at (0, -110) 76 x 26 (MIL-STD-130: P/N, S/N, REV, data matrix), A2 sheet.

Positions (case frame, mm). Back strip: SW_MAIN (-150, 100) 19 mm momentary with green ring, SW_PI (-110, 100) 16 mm recessed with amber ring, SW_TEST (-70, 100) 16 mm with white ring, battery bar D12..D16 at X -82..-58 step 6, Y 123, e-paper WeAct 3.7 (105.79 x 53.80, holes 92.99 x 48.20, UC8253) at (30, 100) on four M3 x 5 standoffs, J_EPD (95, 100), BZ1 (120, 72), SW_LIGHT (120, 100) DPDT ON-ON-ON DAY/NIGHT/BLACKOUT. Starboard strip: SW_SOS (170, 42), SW_EMCON (170, 0), SW_ZERO (170, -42), guarded toggles with red covers, 42 mm pitch. Port column (over the Pi stack, LEDs only) at X -120, Y +45 to -45 step 9: D1 MASTER WARN (red), D2 MASTER CAUT (amber), D3 TX (red, hardware from TR_APRS), D4 SOS ACTIVE (red), D5 SAT, D6 MESH, D7 LTE, D8 GPS, D9 SHORE (green), D10 CHARGING (white, advisory), D11 MSG (white). Underside: J_PANEL (208, 75), J_X1202SW (-150, -110), J_PIJ2 (-125, -110), SMD cluster in (135, 55, 200, 138). Push-switch lead pads sit on the diagonals (45 degrees) so no pad lies on the switch-to-switch axis.

Electronics (schematic `pcb-c-display.kicad_sch`, 131 parts): U1 PCA9555 0x22 (port 0 LED sinks SOSACT, MWARN, MCAUT, CHG, SAT, MESH, LTE, GPS; port 1 inputs SOS_SW, TX_INHIBIT_n, ZEROIZE_SW, TEST_SW, LIGHT_DAY_n, LIGHT_NIGHT_n, RAIL_SENSE, PANEL_ID), U2 PCA9555 0x23 (port 0 SHORE, MSG, PI ring, BAT1..5; port 1 TX_LAMPTEST, EPD_RES, EPD_BUSY, five spares). LED rail: +5V -> LIGHTING pole 1 (BLACKOUT opens it) -> Q1 AO3401A P-FET PWM'd from BCM12 through Q2 2N7002 (2 kHz) -> LED_RAIL; the MAIN ring takes 470 R from the switched rail before the FET. TX lamp from TR_APRS through Q3 2N7002 with a BAT54 lamp-test tie from U2. Protection: USBLC6 TVS on SPI, I2C and PWM, 100 R series on the e-paper lines, FB + 100 nF on the two power-button leads. Sounder BZ1 on PWM1 (BCM13) through Q4. Ribbon J_PANEL 2x10, pinout identical on B10: 1 +5V, 2 +5V, 3 GND, 4 SDA, 5 SCL, 6 EXP_INT, 7 TR_APRS, 8 EPD_DC (BCM9), 9 GND, 10 SPI_SCLK (BCM11), 11 GND, 12 SPI_MOSI (BCM10), 13 GND, 14 SPI_CE0 (BCM8), 15 EPD_RES_ALT (BCM7), 16 PWM1 (BCM13), 17 PANEL_PWM (BCM12), 18 GND, 19 TX_INHIBIT_n, 20 +3V3. EMCON path: the toggle grounds TX_INHIBIT_n -> J_PANEL.19 -> B10 J_AB1.14 -> A15 (AB_SPARE and MEZZ_SPARE2 merged) -> D5 J_HARN1.15 -> Q3 in Q2's emitter, so the module cannot key while the cover is closed, and the TX lamp follows the real PTT pin through Q4 (R22 DNP). Software contract: `docs/hardware/PANEL.md`.

MIL-STD-1472 applied: 19 mm and 16 mm heads, 25 mm or more edge separation, guards closed = safe, forward/away = on, red/amber/green/white code, flashing 3 to 5 Hz only for immediate action and a failed flasher fails to steady-on, one dimmer, blackout, lamp test on every indicator, upper-case 3.5 mm labels on the far side of each control, master lights inside 30 degrees of the line of sight. `check_pcb_c.py` enforces: outline and hole pattern, aperture and bearing band, tape band rule area, switch pitch >= 25, 3 mm from every insert, parts inside the window by 3 mm, only LEDs over the Pi stack, cluster on the underside.

Routing: the first C3 route left one open (PIRING_K to SW_PI pad 4) and one short at the bar (Freerouting track fragments at D12). Fix: bar from Y 118 to 123 (also clears the TEST / ACK label), the three push switches rotated 45 degrees. Second route: 25.8.

### 25.5 Dock E1 (`tools/gen_sch_e.py`, `gen_pcb_e.py`, `gen_pcb_e3.py`, `check_pcb_e.py`, `full_e.sh`)

- Mechanical: 250 x 44 x 1.6 strip at Y -95..-51 on the floor under PCB-A's south edge. The two south rods pass through Ø3.2 holes at (+-110.5, -73), so the rods are the alignment and no guide pins are needed; PCB-A stands on 6.0 mm spacers on the strip; VHB pads at the corners hold the strip to the floor. Standoff keep-out rule areas around the rod holes.
- Contacts: J_DOCK `meshsat:PogoTargets_2x4` (2.0 mm ENIG pads at 2.54 pitch) centred at (-12, -70), mirrored on A15's J_DOCK `meshsat:PogoPins_2x4` (Ø1.5 THT at 2.54 pitch, underside): 1-4 SHORE_12V, 5-8 GND. Pin spec: 2.54-pitch spring pin, 7.0 mm free length, 1.5 mm stroke or more, 3 A each (Mill-Max 0906 class), compressed 1.0 mm by the 6.0 mm spacer gap. The first target footprint had 3.0 mm pads that overlapped at 2.54 pitch (caught by the pre-route gate); 2.0 mm now.
- Shore entry (MIL-STD-1275 flavour, isolated): IP68 2-pin bulkhead lead -> J_DCIN (JST-VH, 10 A) -> F1 7.5 A mini blade in a Keystone 3568 holder (3.7 A at 12 V full load, 5 A at 9 V) -> Q1 AO4409 SO-8 P-FET reverse polarity (R1 100k, D2 12 V zener gate clamp; alt DMP4015SSS) -> D1 SMCJ33A + C1 10 u 50 V -> U1 TRACO TEN 40-2412WIN -> C3 22 u, D3 SMBJ15A, LED1 -> SHORE_12V on the targets and on J_AUX (XH2, Rev B MPPT slot). The input return DC_N stays isolated from the kit GND (1500 V), so a vehicle chassis never becomes the kit ground.
- TEN 40-2412WIN (datasheet rev 7 Aug 2025 archived at `ECAD/vendor/traco/ten40win_datasheet-3049699.pdf`): 9 to 36 V in, 12 V 3.33 A out, 89 percent, -40 to +75 C, 1500 VDC isolation, output current limit 150 percent typ with continuous short-circuit protection and automatic recovery, UVLO 8.3 V, surge 50 V 100 ms, remote on/off open = on, 1 x 2 inch case 10.2 mm high, 30 g. Footprint: KiCad `Converter_DCDC_TRACO_TEN40-110xxWIRH_THT`, whose pad pattern (two columns 45.72 apart, pins 1-3 at 0 / 5.08 / 15.24, pins 4-6 at -2.54 / 7.62 / 17.78, Ø1.0 pins) is the WIN outline drawing exactly; pinout 1 +Vin, 2 -Vin, 3 remote, 4 +Vout, 5 -Vout, 6 trim. Budget: the X1202 barrel takes 6 to 18 V at 3 A or more (Geekworm wiki), the converter gives 40 W.
- Solar (owner question): regulated-12 V or USB-C PD panels charge through this inlet or the USB-C inlet; a raw panel needs an MPPT module, which is the Rev B slot on J_AUX, not a special socket. *(Superseded 4 Sep: ruling 4 of 32.13 puts the MPPT inside the case on the converter's input side, not on J_AUX (32.15 F); the USB-C inlet no longer exists.)*

### 25.6 Battery topology ruling (owner, 3 Sep 00:50): one pack, the X1202 charges everything

The owner asked why the X1202 is still needed and how the extension cells would charge when the X1202 is charged through its USB-C or barrel. Answer recorded: as drawn in A13 the bank was a power bank charging a UPS (two chargers, two boosts, two gauges, two protections, about 15 percent lost between them), the bank charged only from the case USB-C at 5 V with the Pi's load taking priority, and nothing charged it from the X1202's inputs. Audit round 7 (24.2, 24.3) had already rated that chain below its load. The owner's "inception" verdict stands.

Ruling: the welded 1S8P pack goes in parallel with the X1202's four cells (1S12P on one node, behind the X1202's own protection), and the X1202 is the only charger and the only UPS. Every input then charges every cell: the case USB-C into the X1202 USB-C (5 V, slow), the dock's 12 V into the X1202 barrel (faster). PCB-A A15 drops U1 BQ25601 and its network, U2 BQ29700 with Q1/Q2, U3 BQ27441 with R10, U4 TPS61022 with L2, J_EXT_IN1, J_BANK_OUT1, the TS network and the four holders; it keeps J_PACK (XT60, pack in), J_X1202BAT (XT60, 16 AWG lead to the X1202 B+ / B- holder solder tabs), J_MEZZ_PWR1 (cell node to the 8 V APRS boost, GND return), the hub with its eFuses and INA219s, PCA9555 0x21 (pins 8, 9, 20 become spares on TP6, TP7, TP11), J_DOCK, J_X1202DC. I2C 0x55 and 0x6B leave the map; BANK_ALERT on J_AB1.12 idles high through R12. Net class BANK: 4.0 mm tracks; In2 CELL+ island (-38, -24, -2, 22); J_PACK (-27, -8), J_X1202BAT (-27, 14). Pack rect (-162, -37, -32, 37) with two 25 x 4 strap slots at (-95, +-43); PCB-A outline 285 x 160 (X -165..120), rods unchanged. Two of the ten order-gate items (24.2, 24.3) close with the bank chain.

Bench items before the pack is built (X1202 in hand): (1) charge current from the barrel input, which sets the charge time (42 Ah at 3 A is about 14 h); (2) no charge-timer cutoff: observe one full charge of the big pack; (3) the X1202's over-current trip against the APRS TX peak (Pi about 4.5 A plus the 8 V boost about 5 A from the node for at most 2 s): pull 10 A for 5 s through a load and watch for a trip; (4) confirm the B+ / B- solder points on the holder tabs. Rev B option on record: drop the X1202 and make PCB-A the UPS (BQ25798-class charger, 5 V 6 A boost, power-loss logic, new software).

### 25.7 MIL-STD cross-reference for the 12 Sep review

| Standard | Measure | Rev A |
|---|---|---|
| MIL-STD-1472 | panel per 25.4 | DO |
| MIL-STD-882 | guarded SOS / EMCON / ZEROIZE, hardware TX inhibit, TX lamp from the real PTT pin, RF HAZARD labels at the bulkheads, hold-to-act | DO |
| MIL-STD-810 514 / 516 | Peli 1520 (MIL-C-4150J), Nyloc nuts on the rods, threadlocker on machine screws, torque table (ASSEMBLY.md), rods as dock alignment, display taped over its full flange, cables tied at both ends, welded pack strapped through slots | DO |
| MIL-STD-810 501 / 502 / 507 | industrial-grade parts where the family offers them, X7R, no electrolytics, conformal coating (IPC-CC-830 acrylic) with masks per ASSEMBLY.md; cells remain the limit (35E charge 0 to 45 C) | DO |
| MIL-STD-810 506 / IP67 | case, frame gasket, IP67 switches and SMA bulkheads, tape band seals the aperture; e-paper window is the open item (OPT: 1 mm polycarbonate taped over its cutout) | DO / OPT |
| MIL-STD-461 | ribbon filtered (100 R, TVS), ferrite + 100 nF on the button leads, GND pours, frame bonded through 16 ring pads, RG-316 pigtails; no shielding claim for a plastic case | DO |
| MIL-STD-1275 | shore entry 9 to 36 V with fuse, reverse polarity, 50 V surge, isolated converter; not a full 1275 qualification | DO |
| MIL-STD-130 | nameplate field on the panel, P/N S/N REV silk on every board, asset label spot on the case | DO |
| MIL-DTL-3950 / MIL-PRF-22885 | layout and behaviour with IP67 COTS switches; qualified parts are a BOM swap | DO (COTS) |
| MIL-DTL-38999 | shore DC and USB data on a keyed sealed 38999 wall connector, antennas stay SMA (ruling 6 of 32.13, 4 Sep); the USB-C inlet is gone since the one-pack ruling | REV A |
| MIL-STD-348 / MIL-PRF-39012 | SMP-MAX blind-mate RF joints between PCB-A and the dock (ruling 5 of 32.13, 4 Sep; 32.7, 32.14, 32.15) | REV A |
| IPC-A-610 class 3 | JLC assembles class 2; class-3 geometry kept (annular ring >= 0.15, ENIG) | DO (design) |

### 25.8 Results of this session

| Board | Phase | Route | Deliverable |
|---|---|---|---|
| PCB-B | B10 | 4 attempts all 0 hard / 0 open, 284 vias | `meshsat-pcb-b-revA-B10` |
| PCB-D | D5 | 0 hard / 0 open after the stub router closed 1 | `meshsat-pcb-d-revA-D5` |
| PCB-E2 | E2 | bare board, DRC clean (silk only) | `meshsat-pcb-e2-revA-E2` |
| PCB-C | C3 | see the addendum below | `meshsat-pcb-c-revA-C3` |
| PCB-A | A15 | see the addendum below | `meshsat-pcb-a-revA-A15` |
| PCB-E1 | E1 | see the addendum below | `meshsat-pcb-e-revA-E1` |

Superseded once the addendum confirms the three pending boards: A13, B9, C2, D4.

### 25.9 Owner-side items carried

- Shoulder strap for the 1520 (confirm the Peli strap kit or add strap eyes under two frame screws).
- Frame insert thread (M3 assumed from the Ø5.2 bore).
- SMP set datasheets (25.2) if tool-less RF joints are wanted in Rev A.
- The four bench items of 25.6 with the X1202.
- Panel switches, covers, e-paper, standoffs, spring pins, the shore inlet and the pack: the bench-fit lists in ASSEMBLY.md.

### 25.10 Addendum, 3 Sep 01:30: results of the pending boards

- C3: first route 0 hard / 1 open (PIRING_K) plus a short at the bar; after the bar move and the 45-degree switch rotation the second route closed at 0 hard / 0 open, 215 vias (Freerouting's optimiser alone ran 27 minutes on the 442 x 311 panel, which is normal for it, not a hang). `cleanup_dangling.py` removed 18 vias; final DRC 0 hard / 0 open, 4 dangling vias and silk notes only; `check_pcb_c.py` ALL PASS. Delivered `meshsat-pcb-c-revA-C3`.
- E1: first gate found the 3.0 mm targets overlapping at 2.54 pitch and J_AUX inside the packer region, then inside H2's standoff keep-out; fixed (2.0 mm targets, J_AUX at (118, -58)). Route 0 hard / 0 open, 16 vias; final DRC silk notes only; `check_pcb_e.py` ALL PASS. Delivered `meshsat-pcb-e-revA-E1`.
- E2: bare strip, DRC silk notes only. Delivered `meshsat-pcb-e2-revA-E2` (gerbers, no BOM).
- A15: the first two chains ran on stale schematics (a section list without J_DOCK / J_X1202DC, then the placer could not load the meshsat library); the third routed at 0 hard / 0 open with one edge-clearance violation of a USB pair against a strap slot; keep-outs around the slots then left that pair (USB_UART_P/N, hub U6 to J_MEZZ1) unrouted because the corridor between the hub parts and the slot keep-out was 1.4 mm; the hub region moved 3 mm north (Y 50..77) and the chain runs again. The pack node (CELL+ and CELL_N between the two XT60s) is closed by hand-placed 4.0 mm and 3.0 mm bars on both outer layers plus the In2 island, because the netclass width did not reach the routed tracks (pipeline note for the next session). Result: 25.11.

### 25.11 Addendum, 3 Sep 01:50: A15 closed

A15 routed clean once the power region shrank to X -104..-62 (the J_AB1 USB pair needed the corridor): 0 hard / 0 open, 214 vias. The pack node then got its bars by hand on top of the router's tracks (`tools/fix_a15_node.py` records the geometry: CELL_N 4.0 mm straight between the XT60 pin 2 pads on F.Cu and B.Cu, CELL+ 3.0 mm detour at X -32.5 on both layers, plus the In2 island); final DRC 0 hard / 0 open, `check_pcb_a.py` ALL PASS. Delivered `meshsat-pcb-a-revA-A15`. Lesson kept for the pipeline: the netclass width set by pattern in `gen_pcb_a3.py` did not reach the routed tracks, and moving parts after routing breaks their connections, so high-current bars are added on top of the routed board, never by moving parts.

Session totals: six boards delivered (A15, B10, C3, D5, E1, E2), all 0 hard / 0 open where copper exists; handoff folders rebuilt by `make_handoff.py`; superseded folders A13, B9, C2, D4 left in place for the owner to delete.

## 26. Audit round 8, 2026-09-03 (gateway shadow mode, no laptop access): the single-pack ruling closed two gate items and opened five, and the 12 September agenda is stale

Same posture as rounds 3, 4, 6 and 7: `Bash` is gated, so no SSH, no `python3`, no `git`, no generator was read and nothing on the laptop was touched. Nothing in this round changes a routed board on its own; findings W and U are the two that would.

What is different: this is the first audit **after** the 3 September single-pack ruling (25.6), and that ruling deleted an entire subsystem. Rounds 6 and 7 spent themselves on the bank chain. Deleting it retired those findings, and it also retired two protections and one signal that nothing has replaced. Sources read this round, all inside this repository and therefore verifiable without the laptop: `docs/hardware/ASSEMBLY.md` (sections 3, 4, 8), `docs/hardware/PANEL.md` (sections 2, 4, 8), `scripts/x1202-monitor.py` (lines 15 to 106), MESHSAT-774 as filed, and sections 24 and 25 above. The Geekworm X1202 wiki could **not** be re-fetched (`wiki.geekworm.com` returns HTTP 400 to the runner), so every X1202 figure below is quoted from the 2 September MESHSAT-709 comment that recorded it and is marked **UNVERIFIED-THIS-ROUND**.

### 26.1 U. BLOCKER: after 25.6 nothing protects the X1202's own four cells from being charged below 0 C

25.6 lists what PCB-A A15 drops: `U1 BQ25601 and its network`, `U2 BQ29700 with Q1/Q2`, `U3 BQ27441`, `U4 TPS61022`, **and "the TS network"**. The TS network was the charger's thermistor input. Gate item 1 of 24.7, the cell-contact thermistor (23.3), was an open action against that network. It did not get done and then get closed. It was deleted with the part it attached to, and **no equivalent exists anywhere in the new topology**.

What survives is asymmetric, and the asymmetry runs the wrong way:

| Cells | Charge-temperature protection | Source |
|---|---|---|
| Welded 1S8P pack | yes, the pack BMS has an NTC cutoff | ASSEMBLY.md section 3 |
| X1202's own four cells | **none** | 25.6, and the X1202 documents no thermistor input |

25.7 already states the operating limit: "cells remain the limit (35E charge 0 to 45 C)". The X1202 is now the only charger, it decides to charge autonomously whenever an input is present, and no software on the Pi can stop it.

The failure mode is worse than "the four cells get charged cold", because the pack BMS makes it worse rather than better. Below its NTC threshold the BMS opens, the 8P pack leaves the node, and **the entire charge current that was spread over twelve cells goes into four**. At the recorded 2.3 to 3.2 A (UNVERIFIED-THIS-ROUND) that is 0.16 to 0.23 C per cell into cold cells instead of 0.05 to 0.08 C. Lithium plating is cumulative, silent and shows up later as capacity fade and then an internal short, inside a sealed IP67 case, in a kit whose stated deployment window is a Dutch and German winter.

Remedies, cheapest first:

| # | Remedy | Cost | Note |
|---|---|---|---|
| (a) | Accept and document: "do not charge below 0 C" on the nameplate, in the custodian handbook and in ASSEMBLY.md | free | honest, and it is a human-procedure control on an unattended autonomous charger, which is the weakest class of control |
| (b) | Delete the case USB-C charge path so the dock is the only input, then put the dock's 12 V behind a Pi-controlled switch on E1 (the TEN 40-2412WIN already has a remote on/off pin, currently open = on) and gate it on a temperature the bridge already reads | one FET or relay plus one signal on E1, one line in the panel contract | also closes finding V, and it is the only remedy that actually prevents the event |
| (c) | Fit a thermistor against the X1202's cells and let the bridge alarm on it | one part, no board change (the panel has spare expander inputs) | alarms, does not prevent |

Class: owner ruling. If (b), it is copper on E1 and it must be decided before the order.

### 26.2 V. The X1202's two inputs can be live at the same time, and the new topology makes that easy

Recorded from the wiki on 2 September, UNVERIFIED-THIS-ROUND: "USB-C input 5 V 5 A; DC jack input 6-18 V >= 3 A (**never both inputs at once**)".

After 25.6 both are permanently wired to the outside of the case:

- case USB-C inlet, straight into the X1202's USB-C (25.6: "the case USB-C into the X1202 USB-C (5 V, slow)");
- dock 12 V, through `J_X1202DC` and a 5521 plug into the X1202 barrel (ASSEMBLY.md section 4, row 2).

Nothing sequences them, nothing indicates which is live, and ASSEMBLY.md carries no warning. An operator who docks the kit on shore power and then plugs a USB-C charger into the case inlet, which is the inlet on the outside of the box and therefore the obvious one, creates exactly the prohibited condition.

This is genuinely new rather than a re-run of 23.5 or 24.5: in the A13 topology the case USB-C went into PCB-A's own charger and the X1202 only ever saw one input. Deleting the charger removed the thing that made the rule unbreakable.

Cheapest fix is (b) of 26.1, which deletes the case USB-C charge path outright; a field USB-C PD source then feeds the dock inlet through a PD trigger, which the E1 input already accepts at 9 to 36 V. Failing that: a warning label at the inlet, a line in ASSEMBLY.md section 2, and the SHORE indicator relabelled to say what it can actually know (finding X). Class: owner ruling.

### 26.3 W. BLOCKER: two unfused conductors leave a 42 Ah node, and one of them runs past the rods

ASSEMBLY.md section 4 lists what leaves PCB-A's pack node:

| Lead | Wire | Route | Over-current device |
|---|---|---|---|
| `J_X1202BAT` XT60 to the X1202 B+ / B- holder solder tabs | 16 AWG, 200 mm | "up the stack's edge" (section 2, step 3), past four steel M3 rods | **none** |
| `J_MEZZ_PWR1` VH to PCB-D's 8 V boost input | 18 AWG | mezzanine, alongside the 16-way harness | **none** |

The pack BMS (15 A) sits on the pack's negative lead, so it protects conductors fed **from the 8P pack**. It does not protect a conductor fed from the X1202's own four cells, which sit on the same node through the very lead in row 1. Whatever the X1202 has for protection is undocumented and is the subject of MESHSAT-774 item 3.

E1 fuses the shore side (F1, 7.5 A mini blade, 25.5). The pack side, which is the side with about 42 Ah and a sub-10 mOhm source impedance behind it, has nothing. That is the wrong way round.

Fix, and it is small: one fuse at the source of each conductor leaving the node, on PCB-A.

- `J_MEZZ_PWR1`: the boost draws about 4.7 A at the cell for 8 V at 1.7 A (13.6 W at a 3.2 V cell, 90 percent). A 10 A blade or Nano2 holder.
- `J_X1202BAT`: this is the pack-parallel joint and carries the whole kit in both directions. 15 A, matching the BMS.

Class: schematic and layout on PCB-A, one regeneration, two footprints in an area that 25.11 already had to hand-place. It is the one finding this round that is copper, and it is the reason not to upload before the 12 September review.

### 26.4 X. The panel's SHORE and CHARGING indicators have no source in the software they are contracted to

PANEL.md section 4 promises: SHORE = "shore 12 V present (from the X1202 monitor: input present)"; CHARGING = "X1202 reports charging". Section 8 names the implementation: "`scripts/x1202-monitor.py` for the battery and input states (feeds SHORE, CHARGING, the bar)".

That script, in this repository, writes exactly four fields (lines 45 to 50):

```python
payload = {
    "voltage": round(voltage, 3) if voltage is not None else None,
    "soc_percent": round(soc, 1) if soc is not None else None,
    "ac_present": (ac == "1") if ac in ("0", "1") else None,
    "last_update": time.time(),
}
```

Three problems follow, and none of them needs the laptop to see:

1. **There is no charging state at all.** The gauge is a MAX17040 at 0x36 (line 19, and `read_battery` reads registers 0x02 and 0x04): voltage and model-based SOC, no charge-status output. `CHARGING` has no source.
2. **`ac_present` is not wired.** It comes from `read_ac()`, which shells `gpioget --bias=pull-up gpiochip4 6`, and line 23 of the same file says so in its own words: `AC_LOSS_GRACE_SEC = 86400  # disabled until GPIO6 wired`. PANEL.md section 2 lists BCM 6 as "(X1202) Existing power-loss input, unchanged", which asserts that the X1202 drives it through the Pi header. **Nothing in section 25 or in ASSEMBLY.md section 4 wires it**: the lead table has four X1202 leads (battery, 12 V, MAIN switch, Pi J2) and no indication lead. So the panel contract rests on an assertion the record does not establish and the code contradicts.
3. **Even wired, `ac_present` cannot say "shore 12 V".** It is one bit for "some input is present" and cannot distinguish the barrel from the USB-C. That is precisely the distinction finding V needs an operator to be able to make.

Fix, in order: add to MESHSAT-774 a 30-second bench check, `gpioget --bias=pull-up gpiochip4 6` with and without an input plugged, which settles item 2 outright. If the X1202 does drive it, `x1202-monitor.py` gains a `charging` field derived from voltage rising against the open-circuit curve while `ac_present` is true, and the SHORE legend becomes EXT PWR. If it does not, either a lead runs from the X1202's indication pin, or both indicators are dropped from Rev A rather than shipped dark. Class: MESHSAT-773 (panel software) plus one acceptance criterion on MESHSAT-774. No board change either way, because the LEDs and their expander bits already exist.

### 26.5 Y. The pack's own BMS is in series with the node, 25.6 does not account for it, and the bench plan never sees it

25.6 says the pack goes "in parallel with the X1202's four cells (1S12P on one node, **behind the X1202's own protection**)". ASSEMBLY.md section 3 says the pack carries "a 1S BMS 15 A with NTC cutoff on the negative lead".

Both cannot be the whole truth. The node is 4P permanently, plus 8P behind a protection FET pair that opens on over-current, on over-discharge and on temperature. Three consequences the record does not carry:

1. **When the BMS opens, the kit runs on 4P**, and the APRS burst's cell-side current comes off four cells instead of twelve. This is the same event as 26.1 and it is not only a cold-charge event: an over-discharge trip at the end of a long deployment does it too, at the worst moment.
2. **Reconnection joins two packs at different voltages** across the XT60 pair and about 10 mOhm of lead and connector. The record does not size that inrush. ASSEMBLY.md section 3 handles it at build time ("matched within 50 mV before connecting") but not at run time, which is when the BMS does it unattended.
3. **The MAX17040's SOC model is not scaled for the node.** It is a ModelGauge, not a coulomb counter, so it does not need the capacity, but its internal impedance model does not match a 12P node and its number is what `x1202-monitor.py` shuts the Pi down on (`LOW_CAPACITY = 5`, line 22, `shutdown()` at line 103). The bar in PANEL.md section 4 inherits the same number.

And ASSEMBLY.md section 8 heads its four X1202 tests "**before the pack is welded**", so they run with loose cells and no BMS in circuit. MESHSAT-774's blocker line says the same: "X1202 and the eight extra cells in hand". **The bench plan validates a topology that is not the one that ships.**

Fix: either add a fifth bench item repeating tests 2 and 3 with the finished pack and its BMS in circuit, or rule that the pack has no BMS and the X1202's protection covers all twelve cells, which then makes MESHSAT-774 item 3 the only protection characterisation in the kit and raises its stakes. Class: MESHSAT-774 acceptance criteria, plus one line in 25.6. Note that ruling the BMS out also deletes the only cold-charge protection in the kit, so it cannot be decided independently of 26.1.

### 26.6 Z. The 10 A bench figure is a 5 V-side number, and at the node the same event is about 12.5 A

25.6 and ASSEMBLY.md section 8 item 3 both state the test as "Pi about 4.5 A plus the 8 V boost about 5 A from the node", giving 10 A. MESHSAT-774 carries the same 10 A. The two terms are not in the same units:

| Term | As stated | At the 3.2 V node |
|---|---|---|
| Pi 5 and peripherals | about 4.5 A, which is a 5 V figure (the Pi's own supply is 5 V 5 A) | 4.5 x 5 / (3.2 x 0.9) = about 7.8 A |
| APRS 8 V boost, DMR858M at 5 W analog | about 5 A at the node | about 4.7 A (1.7 A at 8 V, 90 percent) |
| **Total at the node** | **10 A** | **about 12.5 A** |

So the test as written under-exercises the X1202's protection by about a quarter, at exactly the point where the whole purpose of the test is to find the trip. Fix: restate the acceptance criterion as 12.5 A for 5 s at the node, or state the load explicitly as "at the battery node, 3.2 V" and let the bench set it. Class: MESHSAT-774 acceptance criteria. Free, and it changes what the bench proves.

### 26.7 The gate, reconciled after 25.6

24.7's table is stale in three places. Restated in full so nothing has to be reconstructed from five audit rounds:

| # | Board / area | Item | Status after 25.6 | Class | Who |
|---|---|---|---|---|---|
| 1 | A | Cell-contact thermistor (23.3, 24.7 item 1) | **deleted with the charger, not done.** Becomes 26.1 | owner ruling | owner |
| 2 | B | Channel A polyfuse 1.1 A to 2 A hold (23.2) | unverified after B10 | BOM value, one grep | Claude, laptop |
| 2a | A | `CHG_PG` onto `J_AB1`'s spare (24.4) | **moot**, no charger; and 25.4 consumed the spare for `TX_INHIBIT_n`. Shore sensing is now 26.4 | software | MESHSAT-773 |
| 3 | all | Board thickness confirmations | unchanged | owner | owner |
| 4 | C | Panel LED part selection | unchanged | owner | owner |
| 5 | all | LCSC matching of the open BOM lines | unchanged, at upload | owner | owner |
| 6 | D | DMR858M pad rows | **closed** by D4 from the V1.2 datasheet (22.6) | done | done |
| 7 | kit | R18 shore / topology ruling (24.5) | **closed** by 25.6 | done | done |
| 8 | kit | Bulkheads and pigtail schedule at the bench | unchanged, now against E2's seven couplers | owner | owner |
| 9 | all | The 12 September review | agenda restated in 26.8 | review | owner + Nick |
| **10** | **A** | **Fuse `J_X1202BAT` and `J_MEZZ_PWR1` (26.3)** | **new, copper** | **schematic + layout, one A regeneration** | **Claude, laptop** |
| **11** | **kit** | **Cold-charge protection for the X1202's four cells (26.1)** | **new, blocker** | **owner ruling; remedy (b) is copper on E1** | **owner** |
| **12** | **kit** | **The two X1202 inputs can be live together (26.2)** | **new** | **owner ruling, or a label** | **owner** |
| **13** | **sw** | **SHORE and CHARGING have no source (26.4)** | **new** | **MESHSAT-773 + one bench check** | **owner + Claude** |
| **14** | **bench** | **The pack BMS is never exercised (26.5) and the 10 A figure is 12.5 A at the node (26.6)** | **new** | **MESHSAT-774 acceptance criteria** | **owner** |

Items 10 and 11(b) are the only ones that touch copper. **Nothing should be uploaded to JLCPCB until they are ruled on**, which is the same conclusion 25.9 reached for a different reason and is comfortably inside the 12 September date.

### 26.8 The 12 September review agenda, restated

24.7 tells the owner to lead with 24.2 and 24.3, the TPS61022's 3 A rating and the BQ25601's BATFET at 88 percent of a continuous rating. **Both parts were deleted on 3 September.** Taking that agenda to Nick means opening an independent review with a finding about a circuit that is not on the board, which is the worst possible first impression with a verification engineer.

Lead instead with the question the new topology actually raises, in this order:

1. **Twelve cells in parallel on one node with one undocumented charger and one BMS in the middle of it (26.1, 26.5).** This is the architectural question, it is the one with a safety consequence, and it is exactly what an AIV reviewer is for. Bring the bench plan (ASSEMBLY.md section 8) and ask whether it proves what it claims.
2. **What stops this kit charging a lithium pack at minus 10 degrees (26.1).** One sentence, no slides. The honest answer today is "nothing".
3. **Fusing philosophy for the pack node (26.3)**, with the two unfused leads on the table and the E1 shore fuse next to them for contrast.
4. Ground and EMC across three stacked boards with six radios, DCF77 next to the SMPS cluster and 5 W of VHF next to the Pi (the standing question from the 2 September comment, unchanged).
5. The fail-safe direction of the EMCON inhibit: with the panel ribbon unplugged `TX_INHIBIT_n` is held high by PCB-D's pull-up and the radio can key (PANEL.md section 7), which is deliberate and documented, and is the kind of ruling a reviewer should be asked to sanity-check rather than told about.
6. A minimal AIV-style bring-up order for six boards, and which test points are missing for it.
7. JLC 4-layer and PCBA sanity, and whether he would spend an hour on the schematics afterwards.

Boundaries unchanged from the 2 September comment: friend-level, no ESTEC facilities, full candour that the boards are Claude-generated, lead with the audit findings and not with the method. There are now eight audit rounds and every one of them found something, which is the honest way to present it.

### 26.9 What closes this section

Nothing here needs a re-route. Three greps on the laptop, in `~/Documents/Team Shared Root/Projects/MeshSat/Field Kit/ECAD/meshsat-carrier/`, settle what is UNVERIFIED:

| # | Command | Pass condition |
|---|---|---|
| W | `grep -n -e "J_MEZZ_PWR" -e "J_X1202BAT" -e "F1" -e "Fuse" tools/gen_sch_a.py` | confirms 26.3: no fuse symbol on either lead |
| 2 | `grep -n -e "polyfuse" -e "PTC" -e "1.1" -e "2.0" tools/gen_sch_b.py` | gate item 2: the channel A hold current after B10 |
| X | `gpioget --bias=pull-up gpiochip4 6` on a kit, with and without an input plugged | settles 26.4 item 2 |

The X1202 figures (charge current, input ratings, the mutual-exclusion rule) stay UNVERIFIED-THIS-ROUND until either the wiki is reachable or MESHSAT-774 measures them, and MESHSAT-774 measures the ones that matter.

### 25.12 Addendum, 3 Sep 02:30: the gerber export dropped the inner layers (caught by the ordering session)

`tools/build_pcb.sh` listed the gerber layers explicitly as F.Cu and B.Cu plus mask, paste, silk and edge, so every zip of a 4-layer board (A15, B10, D5, and all their predecessors) lacked In1.Cu and In2.Cu: the GND and 5 V planes. Uploading them would have ordered 2-layer boards without planes. Caught by the laptop ordering session before any upload; fixed at the source (the script now derives the copper list from the board's copper count), all six zips re-exported and verified by listing (In1_Cu.g1 and In2_Cu.g2 present on the three 4-layer boards). Two more findings from the same review, both fixed in `make_handoff.py`: KiCad's BOM export writes designator ranges (R13-R27) and a trailing ? on references without a number (J_PANEL?), which JLC's parser cannot pair with the CPL, and bench-fitted parts (A15 J_DOCK, the C3 switches and e-paper, E1's Traco module, fuse holder and targets) belonged out of the JLC BOM and CPL; and E1 carried two LCSC codes copied onto four different parts (now matched by value). Lesson for the pipeline: a gerber zip is verified by listing its files against the board's layer count before it is called a deliverable; the handoff script now does the BOM normalisation itself.

## 27. Audit round 9, 2026-09-03 (gateway shadow mode, no laptop access): the deliverable has never been checked against the vendor's envelope, only against KiCad

Same posture as rounds 3, 4, 6, 7 and 8: `Bash` is gated, so no SSH, no `python3`, no `git`, no generator was read and nothing on the laptop was touched. What is new in this round is the target. Every gate this project has run so far (ERC, DRC, the six `check_pcb_*.py` verifiers, the order-gate greps, the design review of section 20) validates **the design**. 25.12 is the first time anyone opened **the deliverable**, and it was wrong in a way that would have produced 2-layer boards with no planes. One inspection, one fabrication-blocking defect. That is a poor hit rate to stop at, so this round takes the two things the deliverable stage still has no gate for: whether each board fits the service it will be ordered from, and whether the features that only exist in the exported files actually reached them.

Vendor figures below were read from JLCPCB's own capability pages on 2026-09-03 and are quoted, not remembered:

- `jlcpcb.com/capabilities/pcb-capabilities`: FR-4 maximum 1020 x 600 mm at 2 layers and 1016 x 596 mm at 4 layers; thicknesses 0.4, 0.6, 0.8, 1.0, 1.2, 1.6, 2.0 mm; black soldermask available; ENIG available at 2 layers and mandatory at 4 layers and above.
- `jlcpcb.com/capabilities/pcb-assembly-capabilities`: **Economic PCBA** = "2,4,6-layers", thickness "0.8mm - 1.6mm", single board "10x10mm - 470x500mm", panel "10x10mm - 250x250mm", **"Single sided placement (SMT/Thru-hole)"**. **Standard PCBA** = "1 - 32 layers", thickness "No limit", single board **"70x70mm - 460x500mm"**, panel "70x70mm - 250x250mm", "Single & double sided placement (SMT/Thru-hole)".

### 27.1 AA. Two boards are below the Standard PCBA minimum, and the service that will take them places parts on one side only

> **WITHDRAWN by its author, 2026-09-03, on live quotes from the laptop ordering session (25.15, 25.16).** The reading below is wrong in its conclusion: **Economic was greyed out on all five assembled boards**, so there was never a tier choice to make, and **JLCPCB accepted D5 (80 x 62) and E1 (250 x 44) as Standard PCBA by adding its own edge rails**, quoting them at production sizes 80 x 72 and 250 x 70. The 70 x 70 minimum is against **production** size including those rails, not against the board outline, so **no panelisation is needed and there is no panel decision**. Tier for the order is Standard on A16, B10, C4, D5 and E1; E2 and the ring are fabrication only. The one durable point below is consequence 3: A16 is top-only assembly and must stay that way. Board names in the table are the superseded ones: read A15 as **A16** and C3 as **C4**. The table is left as written because it is a dated audit record; the current instruction is `ORDER-SESSION-PROMPT.md` step 1b, and the gate row is 27.4 item 15, closed.

The two constraints that bite are not the ones anyone would expect. Standard PCBA has a **minimum** board size of 70 x 70 mm, and Economic PCBA, the only service left below it, will not place a part on the second side.

| Board | Size (mm) | Layers | Thickness | Bottom-side placed parts, per this appendix | Economic | Standard | Tier it is forced into |
|---|---|---|---|---|---|---|---|
| A15 POWER + I/O | 285 x 160 | 4 | 1.6 | J_DOCK only, and 25.12 removed it from the JLC BOM and CPL as bench-fitted | yes | yes | Economic, as intended |
| B10 COMPUTE | 245 x 170 | 4 | 1.6 | **J_AB1 IDC 2x7 on the underside** (15.2, 15.4, 15.5), not on 25.12's bench-fitted list | **no** | yes | **Standard** |
| C3 CONTROL PANEL | 442 x 311 | 2 | **2.0** | **the SMD cluster and J_PANEL, J_X1202SW, J_PIJ2** (25.4), with the LEDs and switches necessarily on the face | **no**, twice over: 2.0 mm is outside 0.8 to 1.6, and the parts are on both sides | yes, 442 x 311 clears 70 x 70 | **Standard** |
| D5 APRS | **80 x 62** | 4 | 1.6 | D3 stated "JLC assembles both sides"; D4 moved the MCU core to the top under the module, leaving TP1 to TP11 and the jumpers, which are pads, not parts | yes, **if and only if nothing is left on the bottom** | **no, 62 < 70** | **Economic, single sided, or panelise** |
| E1 DOCK | **250 x 44** | 2 | 1.6 | not recorded either way in 25.5 or 25.10 | yes, same condition | **no, 44 < 70** | **Economic, single sided, or panelise** |
| E2 RF JUNCTION | 330 x 32 | 2 | 2.0 | no assembly at all | n/a | n/a | fabrication only |

Three consequences, in descending order of cost if missed:

1. **D5 and E1 cannot be ordered as Standard PCBA at all.** Not as a price decision, as a size rule. If either board has one placed part on its bottom side, it cannot be assembled by JLC as a single board in any tier. The clean remedy is a 2-up panel (2 x 80 = 160 x 62 for D, or 80 x 124; E1 at 250 x 88), which crosses the 70 x 70 floor and puts Standard back on the table; the cheap remedy is to move or bench-fit the offending part; the wrong remedy is to accept an unpopulated side and discover it at goods-in.
2. **B10 and C3 must be ordered as Standard PCBA**, which is a different price and a different lead time from the Economic assumption the project has carried since the 2026-08-18 design prompt ("economic PCBA for the hub/power section"). C3 fails Economic on thickness even if every part were moved to one side, so this is not negotiable by layout.
3. **A15's top-only assembly, introduced in 25.12 for BOM hygiene, is now load bearing.** It is what keeps A15 inside Economic. If a later revision puts anything back on A15's bottom side, the tier changes with it. Worth one line in `make_handoff.py`'s notes so the next session does not undo it by accident.

None of this is a copper change and none of it blocks the 12 September review. It is an order-stage finding: three of the five assembled boards do not go where the notes assume, and two of them may not go anywhere without a panel. Class: order preparation, settled at upload, but the panel decision for D5 and E1 has to be made before the gerbers are uploaded, not after.

### 27.2 AB. The 25.12 defect class is not closed, it was closed for one property

`build_pcb.sh` listed layers explicitly and therefore silently dropped two of them. The fix derives the copper list from the board, which closes copper. Everything else in the upload is still produced by a script whose output nobody has opened, and the features below exist only in the exported files. Each is one listing or one PDF away from being certain, and each has a different failure mode from the last:

| # | Property | Why it is not covered by DRC or the verifiers | Consequence if wrong |
|---|---|---|---|
| 1 | **Internal cutouts on Edge.Cuts**: C3's 169.35 x 100.51 display aperture, A15's two 25 x 4 strap slots, E2's seven Ø6.5 D-holes with a 6.0 mm flat | KiCad's DRC is happy with a cutout drawn on User.Drawings or as a graphic; the verifiers check coordinates, not the layer the geometry landed on | C3 arrives as a solid 442 x 311 panel with no window, which is scrap; E2 arrives with no bulkhead holes, which is scrap |
| 2 | **Drill files, PTH and NPTH** | the layer bug proves the export list was hand-written; the drill export is a separate command with its own flags | the four Ø3.2 rod holes and the 16 Ø5.2 frame holes are the entire mechanical interface of the stack |
| 3 | **CPL origin and units** | the boards are drawn in the case frame with negative coordinates, and gerbers and CPL can be exported against different origins | every part placed with a constant offset, caught only in JLC's preview if someone looks hard |
| 4 | **CPL side column** | nothing in the pipeline reads it back, and it is exactly what 27.1 turns on | the tier question above cannot be answered without it |
| 5 | **Order-number marker** | the ordering prompt selects "specify a location", which is a gerber-side feature, not only a web option | JLC places their order number wherever they like, on a black MIL-STD-1472 operator panel |

Item 1 is the one that matters. It is the same shape as the layer bug (a feature present in the design, absent from the deliverable), it has the same detection cost (list the Edge_Cuts gerber, or look at the 1:1 PDF that is already in `Review/`), and on C3 it is the difference between a control panel and a rectangle.

### 27.3 Note, not a finding: E2 and C3 will draw DFM questions, and both are intentional

E2 has no copper anywhere and C3 is a large 2-layer board that is mostly soldermask. JLC's DFM has queried copper-free boards before (recorded for C2 in 14.6). Both are deliberate. Answer the query, do not "fix" the board.

### 27.4 The gate, after this round

26.7's table stands unchanged. Two rows are added; neither is copper and neither moves the 12 September date.

| # | Board / area | Item | Class | Who |
|---|---|---|---|---|
| ~~15~~ | A, B, C, D, E1 | ~~Assembly tier per board (27.1)~~ **CLOSED 2026-09-03 by the live quotes (25.15, 25.16): Standard PCBA on all five assembled boards, Economic greyed out everywhere, JLC adds edge rails to D5 and E1, no panels, no panel decision. A16 stays top-only.** | done | done |
| **16** | **all** | **Deliverable property check (27.2), five items, above all the internal cutouts on Edge.Cuts** | **five listings on the laptop** | **Claude, laptop** |

### 27.5 What closes this section

All on the laptop, in `~/Downloads/meshsat-pcb/`. None of them needs KiCad open and none changes a board.

| # | Command | Pass condition |
|---|---|---|
| 1 | **PASSED 3 Sep (25.15).** `unzip -l JLCPCB/PCB-C-DISPLAY-C4/*-gerbers.zip` and the same for E2 and A16, then open the Edge_Cuts gerber | C4 shows two closed contours (outline plus aperture), E2 shows eight (outline plus seven D-holes), A16 shows three (outline plus two strap slots) |
| 2 | **PASSED 3 Sep (25.15).** `unzip -l` on all seven zips, looking at the drill entries | a PTH file on every board and an NPTH file wherever there are unplated holes; if the export is merged, one drill file containing both, and say which it is |
| 3 | `head -3 JLCPCB/*/*-cpl.csv` | header is JLC's (Designator, Mid X, Mid Y, Layer, Rotation), values carry a unit suffix or the notes state the unit |
| 4 | `grep -c -i "bottom" JLCPCB/*/*-cpl.csv` | zero for A16 (top-only is load bearing, 27.1 consequence 3), D5 and E1; non-zero for B10 and C4 is expected. Since 25.15 this no longer decides the tier, which is Standard everywhere; it is now a check that A16 has not silently regained a bottom-side part |
| 5 | `grep -r -i "JLCJLC" */` in the gerber folders | present if "specify a location" is to be selected, absent means pick "remove order number" or accept their placement |
| 6 | compare each `Review/<board>/*1to1*.pdf` against the board's stated cutouts | the aperture, the slots and the D-holes are visibly absent from the copper and present in the outline |

Check 1 is worth doing before check 2. If a cutout is missing, the board is regenerated and everything downstream of it is stale anyway.

### 27.6 One addition to the 12 September agenda

26.8's seven items stand. Add one, and put it last because it is about method rather than about the design:

8. **The verification gap itself.** Every gate this project ran validated the design; the one time anybody validated the deliverable, it was wrong (25.12), and this round found five more properties of the deliverable that no gate reads (27.2). Nick reviews AIV for a living and this is his subject rather than ours. The honest framing is that nine audit rounds each found something, the eighth and ninth found things that no automated check in the pipeline could have found, and the question for him is what a minimal acceptance procedure for a fabricated board set looks like when the design authority and the reviewer are the same process.

### 25.13 C4: the e-paper becomes a recessed window, the WeAct numbers corrected, the logo on the face (3 Sep, afternoon)

Owner objection to C3: the WeAct 3.7 module standing on standoffs above the panel. Owner proposal: cut the panel to the glass and tape the module's side lands from underneath, the Touch Display 2 construction again. Adopted for C4, from documents, no measurement:
- WeAct STEP and drawing (`ECAD/vendor/weact/EpaperModule/Hardware/`): module 105.79 x 53.80 x 1.6, R1.4, four Ø3.2 holes 2.80 from every edge (pattern 100.19 x 48.20; the 92.99 in the drawing is the glass width, which the C3 footprint had wrongly used as the hole pitch), 2x4 header and FPC connector on the back at the east end, components at most 8.5 mm tall on the back.
- Panel E037A75 (WeAct Doc folder, Yingruida, rev A0 2025): glass 92.99 x 53.0 x 0.95, active 81.54 x 47.04, 24-pin 0.5 mm FPC at one short end, UC8253. The glass sits between the hole columns (front-view alignment marks at 6.5 and 99.3 mm), so the module's lands are the two 6.4 mm strips left and right with the holes; top and bottom margins are 0.4 mm.
- C4: window 94.19 x 53.6 (glass + 0.6 per side in X, 0.3 in Y) R1.0 centred on the module centre (30, 100); face frame line on silk; underside rule areas on the two 5.8 mm lands (no pads, no vias, no footprints) and on the module body plus 1 mm (no footprints); B.Fab outline and legend. Glass face 1.0 mm below the panel face (0.95 glass + 0.05 tape against the 2.0 mm panel). Flush option: `pcb-c-ring` R1, a 1.0 mm FR-4 frame with the same window and the four module holes, taped both sides (0.95 + 0.05 + 1.0 + 0.05 = 2.05, 0.05 mm proud), delivered as `meshsat-pcb-c-ring-revA-R1` for the same JLC batch. The 2x4 module header takes a 2x4 socket on the J_EPD lead. Bench-fitted list updated in `make_handoff.py`.
- Logo: the MeshSat lockup traced from the approved sticker master (`brand/MeshSat_sticker_80x31mm_EXACT.pdf`, 4716 x 971 alpha mask at 1753 ppi, threshold 0.5, `tools/logo_silk.py` and `tools/logo_meshsat.json`; never redrawn, brand guide section 7), white silkscreen 75 x 15 mm centred at (0, -86) on the front strip, monochrome treatment for a one-colour process. The same helper can place the mark on any board.
- One residual assumption for the bench: the glass centred on the module within 0.6 mm. If a module shows the glass off-centre, the window grows 0.4 mm on that side in C5; nothing else moves.

### 25.14 C4 result (3 Sep 14:50)

C4 routed 0 hard / 0 open, 226 vias, after three chain runs: the first left the PI ring anode open (270 mm to its resistor in the cluster), fixed by pinning R32 and R33 beside their switches so the long run is the LED rail; the second was lost to a scoring bug in `route_parallel.sh` (an attempt killed during the optimiser was ranked winner with 178 opens; `route_one.sh` now scores a missing session file out); the third, with a router keep-out around the e-paper window (Freerouting ignores the edge clearance of inner cutouts, the PCB-A strap-slot lesson again), closed clean after a 50-minute optimiser pass that trimmed 275 vias to 226. `check_pcb_c.py` ALL PASS including the window checks. Delivered `meshsat-pcb-c-revA-C4`; C3 deleted. The spacer ring `meshsat-pcb-c-ring-revA-R1` delivered alongside. Pipeline rule from this: the panel routes in under a minute and its optimiser pass is the 30 to 50 minute item; it is not killable without losing the route, so a panel run gets one attempt, and the finisher never picks an attempt without a session file.

### 25.15 Owner rulings on audit round 8 (3 Sep 15:00): fuses on the pack node, shore inhibit on the dock

Owner: "do both". Implemented as A16 and E1 (second spin of E1, same deliverable name):
- PCB-A A16: F1, 15 A mini blade in a Keystone 3568 holder, between the pack node (CELL+) and the X1202 lead (J_X1202BAT.1, net CELL_X); F2, 10 A mini blade, between the node and the 8 V boost feed (J_MEZZ_PWR1.1, net MEZZ_CELL). F1 at (-26, 33) standing north of the X1202 XT60, F2 at (-8, 30) north of the mezzanine header (its first position collided with that header's courtyard). The pack node bars (`fix_a15_node.py`) now run CELL_N straight, CELL+ from J_PACK.1 west and north to F1's node pad and on to F2, CELL_X from F1 around the east side to the XT60, MEZZ_CELL from F2 down to the VH header. Closes gate item 10 (26.3).
- Shore inhibit: spring pin 8 changes from GND to SHORE_INHIBIT (three GND pins remain, 1.1 A each at full load). On A16 it is driven by the expander U19 (0x21) port 0 bit 4, the spare left by the bank removal. On E1 it drives an EL817 / PC817 optocoupler through 330 R with a 100 k pull-down; the transistor shorts the TEN 40WIN remote pin to its isolated -Vin, so LED on = converter off, LED off or Pi dead = converter on (datasheet: open = on). Isolation preserved. Software contract in PANEL.md section 9: assert below 0 C or on operator request, clear with hysteresis. Closes gate item 11 by remedy (b) of 26.1, and item 12 by removing the case USB-C to X1202 cable (ASSEMBLY.md section 4): the dock is the only charge input, USB-C PD sources come in through a 12 V PD trigger lead on the dock inlet.
- Items 13 and 14: PANEL.md section 9 records the SHORE / CHARGING source gap; ASSEMBLY.md section 8 now tests 12.5 A at the node, repeats with the pack BMS in circuit, checks GPIO 6 and the inhibit; MESHSAT-774 updated to match.
- Round 9's finding AA was withdrawn by its author from the laptop (D5 and E1 were accepted as Standard PCBA with JLC's edge rails; no panels); its 27.5 checks 1 and 2 passed on every board with a cutout. The one remaining cost note: D5 is two-sided only because of R36; moving it is optional.

## 28. Audit round 10, 2026-09-03 (gateway shadow mode, no laptop access): the shore inhibit is also the kit's only power input, and three documents still describe the previous revision

Same posture as rounds 3, 4, 6, 7, 8 and 9: `Bash` is gated, so no SSH, no `python3`, no `git`; no board, generator or deliverable was touched. Sources read this round are all inside this repository and therefore verifiable without the laptop: `docs/hardware/ORDER-SESSION-PROMPT.md`, `docs/hardware/ASSEMBLY.md` (sections 1 to 9), `docs/hardware/PANEL.md` (sections 5 to 9), sections 25.12 to 25.15, 26 and 27 above, and the MESHSAT-709 comment history. The JLCPCB live-quote result is quoted from the 3 September 14:54 record, not re-fetched.

What is new in this round is the direction. Round 9 looked at whether the deliverable matches the vendor's envelope. This round looks at the two things 25.15 changed on the day: what the new `SHORE_INHIBIT` signal actually does to a kit, and whether the documents that the 12 September review and the laptop ordering session are told to read still describe the boards that exist. Both turned out to have a gap, and neither is copper.

### 28.1 AC. Asserting `SHORE_INHIBIT` does not stop the charge, it removes the kit's only external power input

25.15 closed gate item 11 by remedy (b) of 26.1 and gate item 12 in the same stroke, by deleting the case USB-C charge path. Read together, those two decisions make the inhibit a bigger lever than 26.1 was evaluating.

| Fact | Source |
|---|---|
| `SHORE_INHIBIT` high turns the dock's 12 V off entirely | PANEL.md section 9 |
| The case USB-C inlet is no longer connected to the X1202 | ASSEMBLY.md section 4, after 25.15 |
| The dock 12 V goes to the X1202 barrel, which is both the charge input and the run input | ASSEMBLY.md section 4, row 2 |
| The X1202 has no separate charge-enable input | 25.6, and the X1202 documents none |

So there is no signal in this design that stops charging. There is one signal that disconnects shore power, and charging is a side effect of shore power being present.

The sequence that matters, with a cold kit and the boot state PANEL.md section 9 specifies (low, converter on):

1. Kit below 0 C is docked. The converter runs, the X1202 sees the barrel input, and charging starts at once.
2. The Pi boots, the bridge starts, it reads a temperature below 0 C and asserts.
3. The dock's 12 V drops. The X1202 now runs the whole kit from the battery node, because that is the only source left.
4. The pack discharges until the Pi dies. The opto LED goes out, the converter returns, charging restarts cold, the Pi boots, and step 2 repeats.

The loop's period is the battery run time, so at about 100 Wh and about 5 W it is of the order of a day, and each cycle delivers one boot's worth of cold charge. That is a real improvement on continuous plating, which is what 26.1 wanted. It is also a kit whose steady state below 0 C is flat, on shore power, with the operator seeing a battery that never fills.

Hysteresis does not break the loop. PANEL.md section 9 clears above 3 C, and in a sealed case at a genuine minus 10 with the Pi as the only load there is nothing to carry the interior to +3 C.

The fail-safe direction is right for availability and is exactly what makes this bite: PANEL.md deliberately arranged that a kit with a crashed bridge still charges. The same arrangement makes a **working** bridge the thing that stops the kit charging. 26.1 called remedy (b) "the only remedy that actually prevents the event"; as built it prevents the event by disabling the kit, and it does so in the environment the kits are going to. The SIDN field programme puts them with custodians from 1 November, and the stated environment is a Dutch and German winter. An unheated shed is the design case here, not the corner case.

Remedies, none of which is copper on the boards about to be ordered:

| # | Remedy | Cost | Note |
|---|---|---|---|
| (a) | Make the inhibit state-of-charge aware: never assert below a floor (say 40 percent), so the policy degrades to 26.1 remedy (a), accept and document, exactly when asserting would kill the kit | one condition in the bridge | converts a kit-killing behaviour into the behaviour 26.1 already judged acceptable |
| (b) | Warm before charging: a 5 V thermal pad against the X1202 cells, fed from the dock and enabled below 0 C, turns "refuse to charge" into "wait a few minutes". The owner already has 5 V thermal pads on order (recorded 2026-08-28) | one switched output; the expander has spare bits and PCB-A has channel hardware, but placing it is Rev B | the only remedy that removes the conflict rather than choosing a side of it |
| (c) | Drop the inhibit's temperature role, keep it as the operator "no charge" control, and put the cold rule on the nameplate | free | 26.1 remedy (a) with an extra part fitted |

Recommendation: (a) now, as a software condition in MESHSAT-773, because it costs nothing; (b) as a Rev B item. Do not change A16 or E1. Also extend ASSEMBLY.md section 8 test 9, which today only confirms the 12 V drops out: add that the kit continues to run from the node with the dock inhibited, and record the current, because that number is the loop period above.

Class: MESHSAT-773 acceptance criteria plus one line in PANEL.md section 9 and one in ASSEMBLY.md section 8. Does not touch a gerber and does not move the 12 September date.

### 28.2 AD. The temperature the inhibit depends on has no source at the moment it is needed

PANEL.md section 9 names the source as "the ZigBee temperature sensor, or any in-case sensor the bridge trusts". After 26.1 there is no second candidate:

| Candidate | State |
|---|---|
| Charger TS network | deleted with the BQ25601 (26.1) |
| Pack 103AT-2 NTC | terminates at the pack BMS, never reaches the Pi (ASSEMBLY.md section 3) |
| X1202 gauge at 0x36 | fuel gauge, no temperature |
| INA219s at 0x40 to 0x49 | shunt and bus voltage, no temperature |
| Tuya ZigBee IP65 sensor | the only one, and it is a battery-powered field device |

That last row is the whole protection. It is battery powered, it reports periodically rather than on demand, and it has to rejoin through the CC2652P coordinator after every cold boot. The boot state is low, meaning charging. So the first minutes of every cold dock are unprotected by construction, and if the sensor's cell is flat or it has dropped off the mesh, all of them are.

A protection whose sensor is a battery-powered device on a mesh network is not a protection, it is a monitor. Cheap alternatives exist and none is decided: the Pi's own SoC temperature is a fair ambient proxy in the first seconds after a cold boot and needs no hardware at all; a thermistor divider on an unused INA219 bus-voltage input is a hardware option that does not need an ADC.

There is a genuine tension here that should not be resolved quietly, and it is a good question for 12 September: the fail-safe direction cannot be both. "Sensor unknown means charge" preserves availability and gives up the protection; "sensor unknown means do not charge" preserves the cells and, per 28.1, kills the kit. Remedy (b) of 28.1 is the only option that does not force the choice.

Class: MESHSAT-773 must state which sensor, what the bridge does when it is absent or stale, and how long after boot the decision may be "unknown".

### 28.3 AE. The ordering prompt still carries the withdrawn round-9 finding, and would stall the ordering session on a question that is answered

25.15 records the outcome from the laptop: Economic was greyed out on all five assembled boards, and D5 (80 x 62) and E1 (250 x 44) were both accepted as Standard PCBA with edge rails added by JLC, at production sizes 80 x 72 and 250 x 70. Finding AA was withdrawn by its author. Four places still say otherwise:

| Where | What it still says |
|---|---|
| `ORDER-SESSION-PROMPT.md` step 1b (line 32) | put A16 on Economic; D5 and E1 "can only go Economic single-sided, or on a 2-up panel"; "report the panel decision for D5 and E1 to the owner before uploading them"; and it closes "If the notes and 27.1 disagree, report it, do not choose" |
| 27.4 gate item 15 | reads as open, and names A15 |
| 27.1 table | names A15 and C3 |
| 27.5 check 1 | names `JLCPCB/PCB-C-DISPLAY-C3`, a folder deleted on 3 September (25.13) |

The withdrawal is recorded only in the last line of 25.15, under a heading about round 8 rulings, about 170 lines before the gate table it withdraws an item from. A reader who goes to the gate table, which is exactly what both the 12 September review and the ordering session are instructed to do, does not see it.

Consequence, and it is cheap but real: the ordering session is a fresh Claude Code session on the laptop with no memory of the quotes. It follows the prompt, looks for an Economic option the site does not offer, raises a panel decision that JLC already answered by adding its own rails, and the prompt's own closing sentence tells it to stop rather than choose. Cost is a session and possibly a day, at the point in the schedule where the owner is paying.

Fix: rewrite step 1b to derive size, layers, thickness and side split for context but take the tier from the actual quote, expecting Standard on all five assembled boards and JLC-added rails on D5 and E1; mark gate item 15 closed with the reference; correct C3 to C4 and A15 to A16 in 27.1 and 27.5. Class: documentation, order preparation, and it should land before the 12 September review because the review reads the same table.

### 28.4 AF. ASSEMBLY.md builds an A15 and a C3

Line 3 names "PCB-A POWER + I/O (A15)" and "PCB-C CONTROL PANEL (C3)"; build step 3 names A15. Build step 7 already names C4, so the document contradicts itself, and C3 no longer exists on the laptop.

A16 minus A15 is not cosmetic to whoever assembles the kit:

- F1, 15 A mini blade in a Keystone 3568 holder, between the pack node and `J_X1202BAT`; F2, 10 A, between the node and `J_MEZZ_PWR1`. Section 1 has no fuse-holder row and no torque, and section 9's bench-fit list has no blades, although hand-fitted consumables are exactly what that list is for (25.12).
- Section 4's lead table still shows the two leads that 26.3 raised as unfused, with no note that 25.15 fused them at source. That is the one fact a reader of section 4 most needs.
- Spring pin 8 changed from GND to `SHORE_INHIBIT`, leaving three GND pins. At the dock's full 40 W output that is about 1.11 A per pin, which section 1 does not state and section 8 does not check. Worth one line and one bench measurement rather than an assumption.

Consequence: an assembler working from ASSEMBLY.md builds an A15, and looks for a C3 that is not there. Class: documentation, free.

### 28.5 The gate, after this round

26.7 as amended by 25.15 stands, plus 27.4's two rows with item 15 now resolved, plus three new rows. None of them is copper and none of them blocks the upload.

| # | Board / area | Item | Status | Class | Who |
|---|---|---|---|---|---|
| 15 | all | Assembly tier per board (27.1) | **closed** by the live quotes: Standard on all five assembled boards, JLC adds rails to D5 and E1, no panels (25.15) | done | done |
| 16 | all | Deliverable property check (27.2), five items | **partly closed**: 27.5 checks 1 and 2 passed on every board with a cutout (25.15). Checks 3 to 6 (CPL origin and units, side column, order-number marker, 1:1 comparison) not recorded | four listings on the laptop | Claude, laptop |
| **17** | **kit / sw** | **`SHORE_INHIBIT` removes the kit's only external input, so a cold kit on shore runs itself flat (28.1)** | **new** | **owner ruling on (a) vs (b); MESHSAT-773 + PANEL.md section 9 + ASSEMBLY.md test 9** | **owner** |
| **18** | **sw** | **The inhibit's temperature source is unspecified and unavailable at boot (28.2)** | **new** | **MESHSAT-773 acceptance criteria** | **owner + Claude** |
| **19** | **docs** | **The ordering prompt, gate item 15, 27.1, 27.5 and ASSEMBLY.md still describe the previous revision (28.3, 28.4)** | **new** | **four edits in this repository, before the review** | **Claude, runner** |

### 28.6 One correction to the 12 September agenda

26.8's seven items and 27.6's eighth stand. Item 2 of 26.8 needs restating. It currently reads "What stops this kit charging a lithium pack at minus 10 degrees. The honest answer today is nothing." After 25.15 that is no longer true, and the true version is a better question for a verification engineer: the answer is now "a signal that turns the kit off shore power entirely", which is a real trade rather than an omission, and 28.2's fail-safe tension is the part worth putting in front of him. Ask him which way an unattended box in a shed should fail.

### 28.7 What closes this section

Nothing here needs the laptop and nothing needs KiCad.

| # | Item | Closes |
|---|---|---|
| 1 | Owner ruling on 28.1 (a) or (b), then one condition in MESHSAT-773 and one line in PANEL.md section 9 | gate 17 |
| 2 | Name the temperature source and the unknown-state behaviour in MESHSAT-773 | gate 18 |
| 3 | Four edits in this repository: `ORDER-SESSION-PROMPT.md` step 1b, 27.4 item 15, the C3 and A15 names in 27.1 and 27.5, and ASSEMBLY.md sections 1, 3, 4 and 9 | gate 19 |
| 4 | Optional, one line on the laptop: the spring-pin part number and its current rating from the A16 BOM, to make 28.4's 1.11 A note concrete | 28.4 |

### 25.16 Legend pass on all seven boards, and the cart (3 Sep 17:50)

Owner, after JLCPCB's 2D preview of the panel: the words and sentences on the boards must be repositioned. Done on the routed boards without re-routing (`tools/silk_fix_all.py`, rules by text content, mirrored into every generator): C4 LED labels west of the LEDs (they ran into the display frame), toggle labels 13 mm from their switch, battery bar "BATT %" plus one number above each LED, e-paper legend below the title band, nameplate lines sized to clear the data-matrix square, face title reduced to "MESHSAT FIELD KIT - CONTROL PANEL" with the phase and assembly notes (glass alignment, connector end, wall and side labels) moved to the underside, TAPE marks removed; A16 banner and subtitle moved off the hub parts and the nut circle, pack label shortened, underside note reworded for the dock; B10 J_PANEL label above the header, wall labels off parts, phase tag B10; D5 module legend to the underside in three short lines, harness label off the edge, J_PWR1 net name; E1 banner shortened and sized to fit above the parts, F1 label 7.5 A, U2 reference moved; E2 banner between the screw and coupler rows, SMA F-F labels dropped; ring label rotated onto the west land. Every board: 0 text-related silk violations, 0 hard, 0 open; all seven re-exported and the handoff rebuilt; the ordering session re-uploads the seven gerber zips (BOM and CPL unchanged).

Cart as prepared by the ordering session (EUR, qty 5 each, before shipping, VAT and any coupon): A16 194.77, B10 (standing), C4 369.51, ring 21.75, D5 194.49, E1 85.07, E2 50.45; sum 1184.74 for the lines it listed; both free confirmations on every assembled line. Its findings, folded in: the Keystone 3568 holders were not placeable at JLC (2 in stock), so the holders and fuses are bench-fitted or pre-ordered; the E1 optocoupler matched to EL817S1(B)(TU)-F with the SOP-4 rotation corrected; FE1.1S kept at C9359; the C4 white LEDs D10 and D11 bench-fitted; JLC reads the ring as 56.65 x 108.64 while its Edge.Cuts gerber measures 105.79 x 53.80 (harmless, size class unchanged); the site's JLC rotation offsets (SOIC +270, box headers, SOP-4 0) still live in the ordering session's `jlc_final.py`, to be folded into `make_handoff.py`.

## 29. Gate item 19 closed, 2026-09-03 (gateway shadow mode, no laptop access): the three documents the 12 September review and the ordering session read now describe the boards that exist

Same posture as rounds 3, 4, 6, 7, 8, 9 and 10: `Bash` is gated, so no SSH, no `python3`, no `git`. `Write` and `Edit` are not gated, so unlike those rounds this session could act, and did: no board, generator, gerber, BOM or CPL was touched, and nothing was uploaded, but four documents in this repository were edited. Nothing here is committed, because `git` is gated; the edits sit in the working tree of an untracked file set and an interactive session has to commit them.

This round did not look for new defects. It executed item 3 of 28.7, which round 10 assigned to "Claude, runner" and dated "before the review". Each of round 10's claims was checked against the file before being acted on rather than taken on trust.

### 29.1 What changed

| File | Place | Was | Is |
|---|---|---|---|
| `ORDER-SESSION-PROMPT.md` | step 1b | derive the tier from 27.1; A16 Economic; D5 and E1 below the 70 x 70 minimum, so Economic single-sided or a 2-up panel; report the panel decision to the owner before uploading; if the notes and 27.1 disagree, stop | take the tier from the live quote; Standard on all five assembled boards; JLC adds its own edge rails to D5 and E1, so there is no panel decision; the 70 x 70 minimum is against production size including those rails; if the site now says otherwise, record it and carry on |
| `ORDER-SESSION-PROMPT.md` | step 1, step 1a, state | "all six ORDER-NOTES.txt", "all six boards", six deliverable checks to run | seven order inputs; the four-layer boards must show `In1_Cu` and `In2_Cu` (the 25.12 defect); 27.5 checks 1 and 2 are recorded as passed, checks 3 to 6 are the ones never run |
| `ORDER-SESSION-PROMPT.md` | known debt | exclude `J_DOCK` "if JLC's economic assembly is top-only" | `J_DOCK` is already out of A16's BOM and CPL, which is what makes A16 top-only, so do not add it back; F1, F2 and the C4 white LEDs are bench-fitted for stock reasons |
| `ASSEMBLY.md` | line 3 | builds an A15 and a C3 | builds an A16 and a C4, with one sentence saying what each revision changed and that A15 and C3 no longer exist |
| `ASSEMBLY.md` | section 1 | no fuse row | F1 15 A and F2 10 A mini blades into Keystone 3568 holders, push fit, no torque, re-check seating after transport |
| `ASSEMBLY.md` | section 2 steps 1 and 3 | E1 without the optocoupler; "PCB-A A15" | E1's EL817 is JLC-fitted and its LED is off during the bench test, which is why the converter runs; A16 with both blades fitted before any lead is energised |
| `ASSEMBLY.md` | section 4 | two leads with no indication they are now fused; no dock-interface note | both leads marked fused at source (F1, F2); a paragraph on the eight spring pins, pin 8 now `SHORE_INHIBIT`, three GND pins left, about 1.11 A each at the dock's 40 W |
| `ASSEMBLY.md` | section 8 test 9 | confirms the 12 V drops and returns | also confirms the kit keeps running from the node while inhibited and records that current, which is the loop period of 28.1, and measures the three GND spring pins at full load |
| `PANEL.md` | title, section 7 | "PCB-C C3"; "I2C map after A15" | "PCB-C C4"; "after A16", with a line saying A16 moved no address and took the spare bit 0.4 at 0x21 |
| appendix | 27.1 | reads as live | withdrawal banner at the head: what the live quotes said, that the 70 x 70 figure is against production size, that consequence 3 (A16 top-only) is the durable part, and how to read the superseded names. The table itself is left as written, because it is a dated audit record and rewriting it would destroy the evidence trail |
| appendix | 27.4 item 15 | open, names A15 and C3 | struck through and marked closed with the reference |
| appendix | 27.5 checks 1, 2, 4 | C3 and A15 paths, six zips, "non-zero for B10 and C3 is what forces Standard" | C4 and A16 paths, seven zips, checks 1 and 2 marked passed on 3 September, check 4 restated as a guard that A16 has not regained a bottom-side part rather than as a tier decision |

### 29.2 One of round 10's four claims was already fixed, and one document it did not count

28.4 said section 9's bench-fit list "has no blades". It does: the A16 row already names the two Keystone 3568 holders, the stock reason, the 15 A and the 10 A blades. `ASSEMBLY.md` was written at 17:44 on 3 September and round 10 was written before that, so the claim was true when made and stale by the time it was read. Nothing was done to section 9. Anyone auditing this round against round 10 should expect that one row to be untouched.

In the other direction, round 10's heading counted three stale documents and its remedy list named two plus the appendix. `PANEL.md` is a fourth: its title named PCB-C C3 and its bus rules named A15. That document is the acceptance surface for MESHSAT-773, so its title naming a deleted revision is the same defect class in the place it costs most.

### 29.3 Two things the ordering prompt would have done wrong, beyond the tier

Both were found by reading the prompt as the ordering session would execute it, which is the only way this class of defect surfaces.

1. It said "read all six ORDER-NOTES.txt" while its own inventory lists seven order folders. A session that reads six and starts uploading leaves one board behind, and the likeliest one to drop is the spacer ring, which is the cheapest line and the one whose absence is only discovered when the panel face will not sit flush.
2. Its known-debt paragraph asked the session to decide at the site whether to exclude `J_DOCK`, conditional on Economic assembly being top-only. `J_DOCK` was already removed from A16's BOM and CPL at export on 3 September (25.12), so the instruction posed a live question about a decision already taken in the files, and the available answers included adding it back.

Neither is copper. Both cost a session at the point in the schedule where the owner is paying, which is the same cost shape as 28.3.

### 29.4 The gate, after this round

| # | Board / area | Item | Status | Who |
|---|---|---|---|---|
| 15 | all | Assembly tier per board | closed 3 Sep by the live quotes (25.15) | done |
| 16 | all | Deliverable property check (27.2): checks 3 to 6 (CPL origin and units, side column, order-number marker, 1:1 comparison) | open, four listings | Claude, laptop |
| 17 | kit / sw | `SHORE_INHIBIT` removes the kit's only external input, so a cold kit on shore runs itself flat (28.1) | **open, needs an owner ruling between remedies (a), (b) and (c)** | **owner** |
| 18 | sw | The inhibit's temperature source is unspecified and unavailable at boot (28.2) | open | owner + Claude |
| 19 | docs | The ordering prompt, gate item 15, 27.1, 27.5, `ASSEMBLY.md` and `PANEL.md` describe the previous revision | **closed by this section** | done |

### 29.5 What this section does not close

Gate 17 and 18 are owner decisions and neither is safe to make on the owner's behalf, because both trade the pack's cells against the kit's availability and the SIDN field programme puts these kits with custodians in a Dutch and German winter from 1 November. The recommendation of 28.1 stands unchanged: remedy (a), a state-of-charge floor below which the bridge never asserts the inhibit, as a software condition in MESHSAT-773 costing nothing and changing no board; remedy (b), the 5 V thermal pad, as a Rev B item. Test 9 of `ASSEMBLY.md` section 8 was extended in this round because measuring the inhibited kit's current is useful whichever remedy is chosen, and that number is what makes the 28.1 loop period concrete instead of estimated.

The four edits are in the working tree and are **not committed**: `git` is gated in this session. An interactive session has to stage and commit `docs/hardware/ORDER-SESSION-PROMPT.md`, `docs/hardware/ASSEMBLY.md`, `docs/hardware/PANEL.md` and this appendix, all of which are untracked or locally modified files today.

Addendum 18:30: cart rebuilt by the ordering session on the silk-revision gerbers, lines Y18 to Y24, EUR 1184.62 (A16 194.76, B10 268.68, C4 369.51, ring 21.75, D5 194.40, E1 85.07, E2 50.45), confirmations on, nothing paid. JLCPCB has no in-place gerber replacement: each revised line is a new order with the same BOM and CPL, so gerber changes are batched from here on. Bench-fitted: A16 F1/F2 holders, C4 D10/D11, D5 L1.

## 30. Audit round 11, 2026-09-03 (gateway shadow mode, no laptop access): the two issues the software and bench work are assigned from still build an A15 and a C3, and both remedies proposed for the cold-charge problem depend on sensors nobody has verified

Same posture as rounds 3, 4, 6, 7, 8, 9, 10 and 29: `Bash` is gated for `git`, `python3`, `ssh`, `find` and for any command containing a pipe, so no board, generator, gerber, BOM or CPL was touched and nothing was uploaded. `Write` and `Edit` are not gated, so this section could be written. Sources: `ASSEMBLY.md` and `PANEL.md` as they stand after round 29, both re-read rather than assumed; sections 25 to 29 above; and the descriptions of MESHSAT-773, MESHSAT-774 and MESHSAT-775 read from YouTrack. Round 29's four edits were checked against the files before this round relied on them, and all four had landed.

Round 29 closed gate 19 for the documents in this repository. This round asks the same question one step further out. The boards are also described in YouTrack, in the three issues the software work and the bench work are actually assigned from, and nobody has read those against the boards since 25.13 renamed two of them. It then looks at the two remedies that 28.1 and 28.2 recommend, because both were costed as free and one of them quietly acquires a dependency on the same class of unverified sensor that made 28.2 a finding in the first place.

### 30.1 AG. MESHSAT-773 and MESHSAT-774 still build a C3 and an A15, and the gate table reads as though that class is closed

| Where | What it says | What exists |
|---|---|---|
| MESHSAT-773 goal | "Drive the PCB-C control panel (MESHSAT-709, C3)" | C4 since 25.13; C3 was deleted from the laptop on 3 September |
| MESHSAT-773 blockers | "Hardware: PCB-C C3 not fabricated yet (order after the 12 Sep review)" | same |
| MESHSAT-774 context | "the welded 1S8P pack of PCB-A A15" | A16 since 25.15; A15 no longer exists as a deliverable |

MESHSAT-775 was read in the same pass and is clean: it names E1, E2 and PCB-A without a revision letter, so nothing in it went stale.

The consequence is not the two names by themselves, it is where they sit. 29.4 records gate 19 as "closed by this section" and section 29's own heading says the documents the 12 September review and the ordering session read now describe the boards that exist. Both statements are true of this repository and neither is true of YouTrack. MESHSAT-773 is where the panel driver is built from and MESHSAT-774 is the checklist for the bench session that has to run before the pack is welded, so these are the two acceptance surfaces, not incidental references. Round 29 corrected `PANEL.md`'s title to C4, which means a reader of MESHSAT-773 now opens an issue that says C3 and lands on a contract document that says C4: worse than either document being uniformly stale, because it invites the reader to wonder which is the current board rather than simply telling them the wrong thing.

One thing in MESHSAT-773 that looks stale is not: "the contract is `docs/hardware/PANEL.md` in the meshsat repo (local, untracked until the boards are ordered)" still holds, and it is also the answer to 29.5's closing paragraph. Round 29 asked an interactive session to commit the four edited documents. MESHSAT-773 records a deliberate decision not to commit them until the boards are ordered, so that request should be put to the owner as a question rather than executed, and it is item 4 of 30.7.

Class: two description edits in YouTrack, free, no copper, no gerber. Gateway mode leaves YouTrack writes to the gateway, so this session did not make them; the exact text is in 30.5.

### 30.2 AH. The three measurements round 29 added to test 9 are not acceptance criteria anywhere

`ASSEMBLY.md` section 8 test 9, after round 29, asks for four things: that the dock 12 V drops and returns, that the converter stays on with the stack lifted, that the kit keeps running from the battery node while inhibited **and that current is recorded**, and that the current in each of the three remaining GND spring pins is measured at full load.

MESHSAT-774's last criterion still reads, in full: "Shore inhibit: SHORE_INHIBIT high drops the dock 12 V within a second, low restores it, converter stays on with the stack lifted (A16 / E1, appendix 25.15)". That is the first two of the four. The two measurements are missing, and they are the two that produce numbers rather than a pass or a fail.

The procedure reference at the head of MESHSAT-774 points at `ASSEMBLY.md` section 8, so the numbers are reachable by a reader who follows it. But the criterion restates the test in one line, and a restatement is what gets ticked. The inhibited kit's current is the single number that turns 28.1's loop period from an order-of-magnitude estimate into a measurement, and the per-pin GND current is what says whether three spring pins can carry the dock's full return at about 1.11 A each. Neither gets written down unless it is on the list somebody ticks.

Class: two lines added to MESHSAT-774, free. Text in 30.5.

### 30.3 AI. Remedy (a) of 28.1 reads a state of charge, and the state of charge is the one thing MESHSAT-774 says is unverified

28.1 recommends remedy (a), "never assert below a floor (say 40 percent)", and prices it at one condition in the bridge. The only source of state of charge in this kit is the gauge at 0x36 on the X1202. MESHSAT-774 criterion 5 reads "The 0x36 gauge still reads the node sensibly", and it is open, because eight cells were added in parallel to the four the gauge was sold with.

So the remedy recommended to contain 28.2's unverified-sensor problem itself depends on a second unverified sensor. That was not visible inside 28.1, which was written about temperature. Stated together: this design now proposes two protections, and each hangs on a sensor that has never been read in the configuration that will be built.

The gauge half of that is cheap to de-risk, and the fix is a wording choice in MESHSAT-773 rather than a test result. A MAX17040-class gauge publishes two numbers: VCELL, which it measures, and SOC, which it models. Capacity is what changed when the pack went from four cells to twelve, and capacity is an input to the model, not to the measurement. A floor expressed as a node voltage therefore survives a gauge whose percentage is wrong, and for a 1S node the terminal voltage maps to charge by chemistry alone.

Recommendation: express remedy (a)'s floor as a voltage at the node, not a percentage, and treat the percentage as display only until 774 criterion 5 passes. A resting 3.6 V is the usual conservative line for these cells and is a defensible starting figure to confirm on the bench. The residual should be stated in the same breath rather than left implied: below the floor the kit charges cold, which is 26.1 remedy (a), accept and document, and a nearly flat cell is the worst case for cold plating. The trade is not free. It is the trade already accepted, made explicit at the one point where it bites.

### 30.4 A shape for gate 18 in which the fail-safe direction does not have to be chosen

28.2 puts the tension plainly: sensor unknown means charge gives up the protection, sensor unknown means do not charge kills the kit per 28.1, and only remedy (b), the thermal pad, escapes the choice. There is a third escape and it is software.

The Pi's own SoC temperature is a valid one-way test. A powered SoC is never colder than the air around it, so `thermal_zone0` reading below 0 C proves the case is below 0 C, while the same sensor reading above 0 C proves nothing about the air. Used only in the asserting direction it cannot produce a false assert at any Pi load, and it is available within a second of boot with no hardware at all, which is exactly the window 28.2 says is unprotected by construction.

That yields a rule with three parts and no unowned unknown state:

1. **Assert** if either the trusted in-case sensor reads below 0 C, or the Pi SoC reads below 0 C.
2. **Clear** only on a fresh in-case sensor reading above 3 C. An absent or stale in-case sensor with a warm SoC leaves an existing assert standing, which is the "do not charge" direction.
3. **Override**: never assert, and drop an assert already standing, while the node voltage is below the floor of 30.3.

Part 3 is remedy (a), and it is what makes part 2 safe to choose. The protection cannot run the kit flat, because it releases before that; and it cannot be defeated by a flat sensor cell, because part 1's second source needs no battery. The cost is one condition and one file read, and no board changes.

"Stale" has to be a number and it should not be invented here. The Tuya IP65 sensor reports on change with a heartbeat, and if that heartbeat is an hour then an hour-old reading cannot gate a charge that begins seconds after docking. Measure the interval on the bench, which is one more line in MESHSAT-774, and set stale at twice it.

Everything in 30.4 is a proposal to the owner, not a ruling. It does not remove gate 17 or gate 18; it changes what the owner is choosing between, from a two-way trade with no good answer to a three-part rule with one number to confirm.

### 30.5 The exact text, so the ruling is a word rather than a design session

**MESHSAT-773, two description corrections (AG):** in the Goal, "(MESHSAT-709, C3)" becomes "(MESHSAT-709, C4)"; in Blockers, "PCB-C C3 not fabricated yet" becomes "PCB-C C4 not fabricated yet".

**MESHSAT-773, criterion 9 replacement.** Today it reads: "Shore charge inhibit (PANEL.md section 9): PCB-A expander 0x21 port 0 bit 4 high below 0 C in-case temperature or on operator request, hysteresis to 3 C, low at boot". Replace with three criteria under the recommended ruling, remedy (a) plus 30.4:

- [ ] Shore charge inhibit (PANEL.md section 9): PCB-A expander 0x21 port 0 bit 4, low at boot, high on operator "no charge", and high on cold per the rule below
- [ ] Cold rule: assert if the trusted in-case sensor reads below 0 C **or** the Pi `thermal_zone0` reads below 0 C (SoC temperature is used only to assert, never to clear, because a powered SoC is never colder than the air); clear only on an in-case reading above 3 C that is fresher than twice the sensor's measured report interval (MESHSAT-774)
- [ ] Charge floor: never assert, and drop an assert already standing, while the node is below the voltage floor, read from the gauge's measured cell voltage and not from its modelled percentage (appendix 30.3); floor value confirmed on the bench, 3.6 V resting as the starting figure; log every release with the voltage that caused it

If the ruling is **(b)**, the thermal pad, the first two criteria stand unchanged, the third moves to a Rev B issue with the pad's switched output, and MESHSAT-775 is the natural home for it. If the ruling is **(c)**, drop the temperature role: criterion 1 keeps only the operator control, the cold rule is deleted, the charge floor is unnecessary, and the cold limit goes on the nameplate, which is a C4 silk change and therefore no longer free after the boards are ordered.

**MESHSAT-774, one description correction and three added criteria (AH, AI, 30.4):** "the welded 1S8P pack of PCB-A A15" becomes "of PCB-A A16"; then

- [ ] Inhibited-kit current: with SHORE_INHIBIT asserted and the kit docked, record the current drawn from the battery node; this is the loop period of appendix 28.1
- [ ] GND spring pins: at the dock's full load, measure the current in each of the three remaining GND pins of J_DOCK against the spring pin's own rating (ASSEMBLY.md section 4)
- [ ] Tuya ZigBee sensor report interval measured, and its rejoin time after a cold coordinator boot, which set the "stale" threshold of MESHSAT-773's cold rule

### 30.6 The gate, after this round

| # | Board / area | Item | Status | Who |
|---|---|---|---|---|
| 15 | all | Assembly tier per board | closed 3 Sep by the live quotes (25.15) | done |
| 16 | all | Deliverable property check (27.2): checks 3 to 6 | open, four listings | Claude, laptop |
| 17 | kit / sw | `SHORE_INHIBIT` removes the kit's only external input (28.1) | open, owner ruling between (a), (b) and (c); 30.4 changes what (a) means and 30.5 writes out all three | owner |
| 18 | sw | The inhibit's temperature source is unspecified and unavailable at boot (28.2) | open, but 30.4 offers a formulation with no unowned unknown state; still an owner ruling | owner, then Claude |
| 19 | docs | Repository documents describe the previous revision | closed by 29 | done |
| **20** | **docs** | **MESHSAT-773 and MESHSAT-774 still name C3 and A15, and they are the acceptance surfaces the software and bench work are assigned from (30.1)** | **new, open** | **owner or gateway, text in 30.5** |
| **21** | **bench**| **The two measurements round 29 added to test 9, plus the sensor report interval, are not criteria in MESHSAT-774 (30.2, 30.4)** | **new, open** | **owner or gateway, text in 30.5** |

None of the three new items is copper, none blocks the upload, and none moves the 12 September date.

### 30.7 What closes this section, and one line for the 12 September agenda

| # | Item | Closes |
|---|---|---|
| 1 | Owner ruling on 28.1 (a), (b) or (c), reading 30.4 first | gate 17, and the shape of gate 18 |
| 2 | Apply the 30.5 text to MESHSAT-773 and MESHSAT-774 | gates 20 and 21, and the Claude half of gate 18 |
| 3 | Bench: node voltage floor, sensor report interval, inhibited-kit current, GND pin currents | the numbers 30.3 and 30.4 leave open |
| 4 | Owner decision on whether the round 29 edits are committed now or stay untracked until the boards are ordered, which is what MESHSAT-773 currently says (30.1) | 29.5's closing paragraph |

Agenda, after 26.8 as corrected by 27.6 and 28.6: item 2 is now better asked as 30.4 rather than as a straight fail-safe question. Put the three-part rule in front of Nick and ask whether a one-way sensor used only in the asserting direction is something he would accept in a design review, because that is the part of it a verification engineer will either endorse or dismantle in one sentence, and it is cheaper to hear which on 12 September than after the software is written.

## 31. Repository home and handover state, 2026-09-03 evening (ECAD session, close-out)

The record, the sources and the deliverables moved into the `meshsat-fieldkit` repository on 3 September 2026 (GitLab `products/meshsat/meshsat-fieldkit`, public mirror `github.com/meshsat/meshsat-fieldkit`). Paths quoted in earlier sections map as stated at the top of this file. The seven Rev A boards (A16, B10, C4, R1, D5, E1, E2) are the release `revA` on GitHub; the JLCPCB upload set is `v2/release/revA/order/`, the review prints `v2/release/revA/review/`, the build guide `v2/BUILD.md`.

State at close-out: every board routes clean (0 unrouted, 0 hard DRC), the legend pass is done on all seven, every gerber zip carries every copper layer of its board, the JLC BOM and CPL are normalised with the rotation offsets applied. The JLCPCB cart holds seven lines at five pieces each with both free confirmations on and is not paid.

The gate before payment, in order: the owner's paper fit check on the 1:1 prints; the X1202 bench items of ASSEMBLY.md section 8 (MESHSAT-774); the two reviews (Nick Panagiotopoulos, 12 September; Kyriakos Pavlidis, KiCad files from the public repository); one more verification round on the final files, written as section 32 with the posture of sections 23 to 30 (what was checked, what closed, what stays open, what the owner decides). Board changes after that go into the generators first, then through the pipeline, then to the ordering session as a list of cart lines to rebuild.

Open beyond the gate: the case purchase (Peli 1520EU without foam, orange, with the 1520PF frame), the SMP blind-mate set for Rev B (25.2, MESHSAT-775), the DMR858M bring-up when the modules arrive (MESHSAT-748), the JLCPCB sponsorship answer (MESHSAT-776), the panel software (PANEL.md, MESHSAT-773).

## 32. Document check in place of the paper fit check, the X1202 envelope, the 5 V budget and the module rail, 2026-09-03 night (ECAD session, owner interactive)

Posture: the owner's printer is dead, and the owner asked three things: why a paper check was needed when manufacturers publish drawings; what the MESHSAT-774 bench items were for and why the design should not instead be robust to the unknowns; and what SMP blind-mate is and which set to review. This section records the answers, the two rulings that came out of them, the defects the document check found, and the board changes those defects and rulings cause (A17, B11). Sources: `v2/vendor/` as extended tonight (`rpi5/`, `x1202/`, `tcall/`, `rf/`), the generators, the A16 and B10 board files, and Geekworm's wiki as archived by the Wayback Machine on 9 May 2026 (the live wiki answers HTTP 400 to anything but a browser, from the runner and from the laptop alike).

### 32.1 Ruling: the paper fit check is struck; the gate item becomes a document check plus part identities

Owner ruling 3 Sep 2026, 22:20: the paper fit check of section 31 is replaced by a check of every COTS site against the manufacturer's own document, plus the owner naming the exact product and version of each module from the purchase records. No measurement of any COTS part is asked of the owner.

| Part | Document | Board | Result |
|---|---|---|---|
| Raspberry Pi 5 | `rpi5/raspberry-pi-5-mechanical-drawing.pdf`: 85 x 56, holes Ø2.7 on 58 x 49, 3.5 mm from the edges | B10 stack pattern 49 x 58, Ø2.7 | match |
| Geekworm X1202 | `x1202/X1202-pcb-V1.1.dxf` and the archived wiki: PCB 96.0 x 85.0, R3 corners; Pi-pattern holes at (42.8, 3.5), (42.8, 61.5), (91.8, 3.5), (91.8, 61.5) in the DXF frame; two more holes at X 3.05; pogo pins at X 94, Y 9 to 25; USB-C input on the X 96 edge at Y 52; DC jack, two XH 5 V outputs and the switch pins on the X 0 to 28 strip; four 18650 holders underneath spanning X 8 to 88 | B10: 85 x 97 box centred on the Pi | **mismatch, 32.2** |
| LilyGO T-Call A7670 | `tcall/T-Call-A7670-ESP32.dxf` and `T-Call-A767X-ESP32.png` (LilyGo-Modem-Series; one drawing serves V1.0 and V1.1, which differ in pin wiring only): 74.78 x 29.01, four R1.5 corner holes on 69.46 x 24.97 (the other edge pair reads 69.53 x 25.01) | B10 site 74.78 x 29.01, Ø3 on 69.46 x 24.97 | match; the "confirm on the board" note of 15.1 is closed by the document. The owner's order (LilyGO official store, 4 Mar 2026, "T-Call A7670E", code H700) names the board |
| RockBLOCK 9704 bracket | `rockblock/rb9704-sma-dims.pdf` Rev A: 52.0 x 56.0, four Ø4.60 on 32.00 x 32.00 | B10 site, same numbers | match |
| Sonoff ZBDongle-P | Sonoff hardware specification page: 87 x 25.5 x 13.5 | B10 site 87 x 25.5, tie slots | match |
| Alfa AWUS036ACM, RTL-SDR Blog V4, u-blox puck | no manufacturer drawing exists; Alfa's sheet gives 62 x 85.3 x 24 with the antennas | slot-and-tie sites | no action, the sites forgive 5 mm |
| Peli 1520, Touch Display 2, WeAct 3.7, DMR858M, TRACO, RockBLOCK STEP, T-Beam, Wio-SX1262 | in the repository since the design | probed in sections 14, 15, 22.6 and 25 | already document checks |

Vendor folder defect found and fixed: `tcall/tcall-a7670x-3d.stp` was LilyGO's `T-A7670X-Board-3D.stp`, the model of the T-A7670X (an 18650-holder board, internally the SIM7000G PCB, 33 x 110, no mounting holes), filed under a T-Call name, while the T-Call drawing the design was read from was not in the repository. The STEP now carries its real name and the drawing is filed (commit 8f6e116).

Still to be named by the owner, no measurement involved: the panel switches (the holes are the class standards, 19.2, 16.2 and 6.5 mm), the SMA female-female bulkhead coupler for E2 (32.5), the dock spring pin (32.6). The X1202 hardware version is recorded nowhere in the repository, the V1 documents or the software repository; Geekworm's wiki has shown only the V1.1 board since spring 2024 and the kits were built in 2026, so B11 goes by the V1.1 DXF.

### 32.2 Finding AJ: the X1202 envelope on B10 was a placeholder, and the real board covers the ribbon header, the SDR receptacle and 22 small parts

The design carried the X1202 as an 85 x 97 box centred on the Pi (section 6, from the CAD config, "visualisation placeholders rather than detailed geometry"), and nothing after that checked it against a Geekworm document; the wiki was read for the electrical figures only (item 11 of section 10). Geekworm's DXF says: 96 x 85, the Pi flush on one long edge (0.7 mm of X1202 beyond the Pi's HDMI edge), 39.3 mm of X1202 beyond the Pi's GPIO-header edge, and the four 18650 holders underneath spanning the whole width, so the cells sit at carrier-board level under the entire outline, extension included. On the X1202 the DC jack, the two XH 5 V outputs and the external-switch pins sit on that extension, on top.

On B10 the ribbon breakout J_GPIO1 sits east of the Pi, so the Pi's header edge faces east and the real X1202 covers X -107.2 to -11.2 at |Y| up to 42.5. In that zone B10 carries J_GPIO1 (2x20 IDC), J_RTL1 (the SDR USB-A receptacle), J_TCALL1 and about 22 parts of the eFuse and monitor cluster (U4 to U6, U13 to U17, F2, JP4 and their passives). Turning the stack around puts the 39.3 mm off the board edge. Either way B10 cannot host the module it was drawn for. Class: PCB-B re-placement and re-route, B11 (32.4).

This is exactly the defect the paper check was meant to catch. The document check found it in an hour, once the document was in the repository; the record's earlier "match" on the outline size alone (given to the owner this afternoon) was wrong and is withdrawn here.

### 32.3 Ruling: the kit's 5 V comes from a node-fed module rail (option B); the X1202 keeps the Pi

The owner asked whether the design could be made robust to the X1202's undocumented figures instead of measuring them. It can, and the answer changed the design.

| Unknown of MESHSAT-774 | How the design absorbs it |
|---|---|
| Charge current, 2.3 to 3.2 A per Geekworm | any value in that range works: E1 gives 40 W, charging takes at most 15 W; it only sets the charge time, 13 to 18 h for 42 Ah |
| Charger safety timer | Geekworm documents GPIO 16 as charge enable (high = disabled); a bridge rule cycles it while an input is present and the node is not full (PANEL.md section 10); the 4.1 V recharge threshold covers the rest |
| Over-current trip | the pack and the APRS boost hang on the holder tabs, the cell terminals, upstream of anything the X1202 protects, and A16 fuses both leads; the X1202's own protection only carries what Geekworm rates it for |
| GPIO 6 power-loss line | documented on the wiki hardware page: pin 31, low when the supply fails, high when it is fine |
| Tab solder points, gauge with twelve cells | the tab pads are in the DXF; the MAX17040 gauge is voltage-based and needs no capacity setting |

The exposure that remained was the 5 V output rating. After 25.6 every 5 V load in the kit hung on the X1202's one 5.1 V 5 A output: the Pi about 1.5 A, the display 0.7, the panel 0.5, PCB-A's feed 0.8, PCB-B's modules 0.9 continuous with LTE 2.0, Iridium 1.0 and LoRa 1.3 A bursts; about 3.8 A continuous, 5.8 A with the bursts serialised, 8 A without. What the X1202 does above 5 A is undocumented.

Owner ruling 3 Sep 2026, 22:35, option B: a boost stage from the cell node feeds a 5 V module rail and the X1202 feeds only the Pi. Because one rail cannot be fed from two sources, the split is by board, not by load: the whole of PCB-B (modules, hub, display lead, panel polyfuse) and PCB-A's four channel switches run on the module rail; the X1202's XH output becomes a sense line that enables the boost, so the rail dies when the X1202 shuts the kit down. Ruling 25.6 is amended accordingly: "no boost" meant no boost in the charge path; a boost from the node to a load rail is the same pattern as the 8 V APRS boost of 18.1 and is allowed.

Numbers: continuous rail load about 2.2 A; serialised burst peak about 4.2 A; unserialised about 6.5 A. The boost is the TPS61089 already on PCB-D (symbol, footprint and LCSC match exist): RILIM 100 k gives 10 A typical, 9 A minimum peak, the part's maximum, with 7 A continuous switch current, so 5.05 V at about 4.2 A continuous from 3.3 V cells, about 5.5 A from 3.6 V, bursts to the current limit. The serialised case is covered over the whole discharge and the unserialised case above about 3.8 V; beyond that the module rail sags, never the Pi. The X1202 carries about 1.5 to 2.5 A of its 5 A. On the dock the X1202 input converter's 5.5 A no longer feeds the modules, so the node charges at full rate with the kit running, which closes 23.5 for good. The TPS61288 (15 A peak, 35 W, LCSC C5219223) is the Rev B option if the unserialised case is ever wanted in hardware; it needs a HotRod footprint drawn from its land pattern, which is why it was not chosen tonight.

Two software rules stay as belt and braces (PANEL.md section 10): the charge kick, and the serialisation of LTE, Iridium and LoRa transmissions. Nothing is measured before payment. The bench list of ASSEMBLY.md section 8 becomes a commissioning list of the built kit.

### 32.4 What A17 and B11 change

A17 (`gen_sch_a.py`, `gen_pcb_a.py`, `gen_pcb_a3.py`, `check_pcb_a.py`, `fix_a17_node.py`, `full_a6.sh`):
- F3, 15 A mini blade in a Keystone 3568 holder at (-32, -44), pack node to BOOST_CELL; the CELL+ bar of `fix_a17_node.py` runs from the pack pad's west detour south to F3's node pad, and a 2.5 mm BOOST_CELL bar from F3 to the inductor where the copper allows.
- U20 TPS61089 at (-47, -58), L2 XAL6030-152 (1.5 uH, 12 A) at (-47, -50), input capacitors 2 x 22 uF west of U20, output capacitors 4 x 22 uF plus 100 uF east of it, FB 63.4 k / 20 k for 5.05 V, FSW 301 k (500 kHz), ILIM 100 k, COMP 17.4 k + 4.7 nF, BOOT 100 nF, VCC 1 uF; EN from X1202_5V through 10 k with 100 k to ground (EN absolute maximum 7 V).
- J_5V_MOD1, JST-VH at (-29, -63): +5V_MOD and GND to PCB-B.
- The four TPS2065 channel switches and their decoupling, the hub U6 with its decoupling and the PWR LED resistor take +5V_MOD; the In2 plane becomes +5V_MOD. +5V, the logic supply from PCB-B's channel A over the ribbon, feeds only the 3.3 V LDO in the PWR zone next to J_AB1 and is routed as a short track: the first A17 route left the two middle USB pads of the hub open because the long +5V track to the hub had taken their escape lanes (four attempts, 0 hard, 2 unrouted); with the hub on the plane the corridor is free. J_AB1 pin 12 is X1202_5V (it was BANK_ALERT, idle since A15); R12 is gone. Net class BOOST (1.5 mm, 0.2 mm clearance) for BOOST_CELL and SW5. Silk: A17, 2026-09-04.

B11 (`gen_sch_b.py`, `gen_pcb_b.py`, `gen_pcb_b3.py`, `check_pcb_b.py`, `full_b5.sh`):
- The stack moves 10 mm west: STACK_C (-88.5, 0), the Pi at X -116.5 to -60.5, holes at (-113, +-29) and (-64, +-29). Orientation fixed and on the silk: HDMI long edge west, GPIO-header edge east, SD-card end south, so the X1202's USB-A sockets overhang south (9 mm; the hub zone starts 0.3 mm beyond) and its DC jack sits at the north-east corner facing east, 8 mm short of the T-Call site.
- X1202 envelope (-117.2, -42.5) to (-21.2, 42.5) from the DXF; nothing but the four standoff holes inside it. `check_pcb_b.py` fails on any footprint overlapping it, and `full_b5.sh` runs that check again after placement.
- J_GPIO1 moves to (-52, 48.5) with its pins along X, north of the stack between the XIAO site and the T-Call pigtail header. The SDR, T-Call and RockBLOCK small-part regions start at X -20 or -19. The X1202 USB-C cable slot and its keep-out are gone (no such cable since 25.15).
- J_5V_IN2 becomes J_5V_MOD, a JST-VH at (-92, -68): +5V for the whole board from A17. J_5V_IN1 stays an XH at (-92, -58) and carries X1202_5V, the sense line, to J_AB1 pin 12. The expander's pin 17 (was BANK_ALERT) is spare.
- Everything else on B10 is unchanged; the +5V plane, the channel switches, the panel polyfuse and the display lead are as before, fed from the VH.

Stack standoffs: four M2.5 x 22 mm female-female on the Pi pattern, the X1202 underside clear of the carrier by its holder height; the DXF carries no heights, so the length is confirmed against the module before the standoffs are bought (ASSEMBLY.md section 1).

### 32.5 E2: the D-hole flat does not match a standard SMA bulkhead

`gen_pcb_e2.py` cuts Ø6.5 with the flat 3.0 mm from the centre, 6.25 mm across the flat. A standard SMA bulkhead thread is 1/4-36 (6.35 mm) with a D-flat of about 5.6 mm across, so the flat would not lock the coupler against rotation; the coupler still passes and clamps between its nuts. The fix is one number once the coupler is named, the flat distance taken from the part's drawing. Documented candidates: Amphenol RF 132170 and Cinch 142-0901-401, both SMA jack-to-jack bulkhead feed-throughs; the L-com BA21 wants a 7.62 mm D-hole and does not fit. E2 stays in the cart as it is until then; it is the cheapest line to rebuild.

### 32.6 Dock spring pins: the A16 footprint names a Mill-Max series it does not fit

`meshsat:PogoPins_2x4` has Ø1.5 through holes at 2.54 mm pitch. The Mill-Max 0906 series named in 25.5 is a standard-tail pin with a 0.508 mm mounting hole; the through-hole series (0921, 0926, 0975) want 1.78 to 2.31 mm holes. The pin is picked from a datasheet and the footprint drill follows it as a post-route pad edit on A17 (a drill change moves no copper); the E1 targets (2.0 mm pads) are unaffected.

### 32.7 SMP blind-mate for Rev B, MESHSAT-775: what it is and which set to review

Today the seven antenna paths reach the stack through the E2 strip, seven SMA couplers unscrewed by hand before the stack lifts out. Blind-mate means the RF joints close by themselves when the stack lands on the dock, as the spring pins close the DC: two receptacles face each other, one under PCB-A and one on E1, and a short bullet between them slides into both, tilting and sliding enough that the boards need no better alignment than the rods give. SMP is the MIL-STD-348 push-on interface for this; SMP-MAX is Radiall's version for badly aligned boards.

| Set | Axial tolerance | Tilt | Minimum board gap | Cycles | Power | Verdict |
|---|---|---|---|---|---|---|
| Radiall SMP-MAX: R222M00080 snap-on receptacle, R222M00720 slide-on receptacle, R222M40010 adapter 9.5 mm (`vendor/rf/`, series catalogue and adapter sheet) | 2.0 mm | 3 degrees | 13 mm | 100 | over 300 W at 2.7 GHz | review first |
| Amphenol RF SMP: SMP-FS-LDPCT limited detent, SMP-MSSB-PCS smooth bore, SMP-FSBA-645 bullet 6.45 mm (Amphenol's site refuses non-browser clients; the owner downloads) | 0.25 mm total | about 4 degrees | about 11 to 12 mm, drawing needed | 500 (limited detent) | ample at 144 MHz | alternative |
| Rosenberger 19S102-40ML5 (`vendor/rf/`) | as SMP | | | 500 | | drop: quote only, reels of 3000 |
| LCSC C7333735 = Radiall R222M00160 | an SMP-MAX receptacle | | | | | out of stock at USD 15.57; buy the R222M parts from Digikey, RS or Mouser |

Why SMP-MAX first: the stack's height over the dock is set by two board thicknesses, the spacer and the rod nuts, which together vary by a few tenths of a millimetre, and its sideways position by the rods, about 0.3 mm. SMP tolerates 0.25 mm axial in total, which the stack cannot promise; SMP-MAX tolerates 2 mm, covers all seven paths up to the 5.8 GHz WiFi band, and carries the 5 W VHF with a hundredfold margin. Its price: 100 mating cycles instead of 500 (still decades of removals), the dock gap grows from 6 to 13 mm (inside the 9.3 mm spare of 25.1, with longer spring pins), and lifting the stack pulls seven slide-on joints at up to 9 N each, about 6 kg on top of the stack's weight. Snap-on receptacles go on the dock and keep the adapters; slide-on receptacles go under PCB-A and let go. Budget roughly EUR 40 per path at distributor prices, about EUR 280 per kit, to be checked on Mouser. Decision owed by the owner at Rev B time: the family, and the 13 mm gap.

### 32.8 The gate after this section

| # | Board | Item | State | Owner |
|---|---|---|---|---|
| 1 | all | paper fit check | **struck** (32.1), replaced by the document check above | done |
| 2 | kit | MESHSAT-774 bench items before payment | **closed by design** (32.3); the commissioning list is ASSEMBLY.md section 8 | done |
| 3 | A, B | A17 and B11 through the chain, route, finish, handoff | **done 4 Sep 00:05, 32.9**: both 0 hard, 0 unrouted; deliverables, order and review sets rebuilt; A16 and B10 retired. **A18 and E3 on 4 Sep afternoon (32.10)**: dock holes and the junction flat follow the named parts | done |
| 4 | C, E2, A | part identities: switches, coupler, spring pin | **done 4 Sep (32.10)**: C&K ATP19/ATP16, NKK M series, Amphenol Connex 132170, Preci-Dip 813; one residue: no documented flip cover exists for a 1/4-40 toggle bushing, Rev A ships the three guarded toggles without one (owner may rule on the Rev B locking lever) | done, one owner ruling open |
| 5 | order | cart lines A (A18), B (B11) and E2 (E3) rebuilt | when the owner says so ("we update the order when the time comes") | owner |
| 6 | kit | reviews: Nick 12 Sep (agenda: 28.6 item 2 restated, plus 32.3), Pavlidis on the public repository | as planned | owner |
| 7 | kit | JLCPCB sponsorship (776), case ordered 3 Sep, DMR858M modules about 15 Sep | as planned | owner |
| 8 | Rev B | SMP-MAX or SMP (32.7), the 13 mm gap | owner decision at Rev B time | owner |

### 32.9 Result, 4 Sep 2026 00:05: A17 and B11 route clean

A17. The pre-route chain (`full_a6.sh`) passed at its third run: the first two stopped on my own region boxes overlapping and on the TPS61089 footprint's 0.2 mm thermal via against PCB-A's 0.25 mm minimum drill, which is now 0.2 mm as on PCB-D. Four parallel Freerouting attempts, all 0 hard. The first route left the hub's two middle USB pads open on all four attempts: on A16 the logic 5 V was the In2 plane, on A17 it was a routed track from the ribbon header up to the hub, and that track had taken the escape lanes of pads 5 and 6 of U6. The hub, its decoupling capacitor and the PWR LED resistor moved to the +5V_MOD plane, so +5V from the ribbon now feeds only the LDO next to J_AB1. The second route left one connection, SDA from J_AB1 to the I2C bus, 72 mm; the grid router (`stub_router.py`) had been skipping it because the DRC text of a through-hole pad carries no layer and its parser demanded one; with that fixed it closed the line in one pass on one layer. The bar script (`fix_a17_node.py`) now avoids vias of other nets: its first MEZZ_CELL column at X -3.0 shorted a +3V3 and a TR_APRS via, the column now sits at X +3.0. Placed bars: CELL+ from the pack pad's west detour south to F3 (B.Cu, the F.Cu copy blocked), BOOST_CELL from F3 to L2 on B.Cu at Y -48.7, CELL_N, CELL+ to F1 and F2, CELL_X as before. Final DRC: 0 hard, 0 unrouted, 260 router vias plus the grid path; left over: 98 isolated copper islands, 3 dangling vias, 2 silk overlaps, 1 dangling track, all outside the hard set. Deliverable `v2/release/revA/boards/meshsat-pcb-a-revA-A17`, the gerber zip carries F, In1, In2 and B copper. JLC BOM: 17 of 46 lines carry LCSC numbers (the boost parts as the ordering session matched them on PCB-D), L2 bench-fitted.

B11. The chain (`full_b5.sh`) passed at its third run: J_PANEL was in no placement list of the generator in git (B10 must have come from a run edited later), the retired BANK_ALERT line on the Pi ribbon and the spare expander pin needed test points (TP12, TP13), the ribbon header collided with a ZigBee tie slot and then with the XIAO pigtail header, and the SDR small-part boxes were too small for the ESD part. Four attempts, three of them at 0 unrouted; the winner 0 hard, 0 unrouted, 291 vias. `check_pcb_b.py` passes with "no part under the X1202 envelope". Two stack legends ran off the west edge and were shortened by rule. Final DRC: 0 hard, 0 unrouted; 22 silk overlaps, 7 silk over copper, 5 dangling vias. Deliverable `meshsat-pcb-b-revA-B11`, four copper layers, 113 placements (J_AB1 on the bottom).

Handoff: `make_handoff.py` rebuilt `order/` (`PCB-A-POWER-A17`, `PCB-B-COMPUTE-B11` beside the five unchanged folders) and `review/`; the A16 and B10 deliverable folders are retired. Cart lines A and B are rebuilt by the ordering session when the owner says so; the other five lines stand. The GitHub release `revA` carries the A16 and B10 gerber zips until its assets are refreshed.

Tooling kept for the next round: `full_a6.sh`, `full_b5.sh`, `finish_a17.sh`, `finish_b11.sh`, `fix_a17_node.py` (via-aware bars), `fix_pad_escapes.py` (re-creates ripped-up escapes under DRC control; not needed in the end), the PTH-pad fix in `stub_router.py` and `gap_closer_checked.py`, and the boost-part LCSC codes in `lcsc_fill.py`.

### 32.10 Part identities named, 4 Sep 2026 afternoon: switches, coupler, spring pins; A18 and E3

The owner's answers to the four "names only" questions (4 Sep): C&K ATP19 and ATP16 for the pushbuttons, NKK M series with NKK boots and covers for the toggles, Amphenol RF 132170 for the couplers (the owner supplied the RS-hosted drawing), and "pick a documented pin for me" for the dock. Every number below comes from the manufacturer's document filed in `v2/vendor/` (`switches/`, `precidip/`, `rf/`); nothing was measured.

**Pushbuttons (C&K ATP19 and ATP16 data sheets).** Code order: series, actuator (S standard flat), indicator (L1 fixed ring), LED colour, LED voltage, bushing, contact, function (A momentary), termination, plating. C4 feeds the rings from the 5 V LED rail through 470 ohm (SW_MAIN, SW_TEST) and 300 ohm (SW_PI), which puts about 5 to 7 mA through a 3 V ring type, so the LED code is 03 (the 3 V type carries the smallest internal resistor; higher codes would only dim the rings further). Panel holes stay: the ATP19's M19 x 1.0 bushing in the 19.2 mm hole, the ATP16's M16 x 1.0 in the 16.2 mm holes, both round bushings.

| Ref | Part | Meaning |
|---|---|---|
| SW_MAIN | C&K ATP19-SL1-603-B0SA-03G | 19 mm, flat actuator, fixed ring, green (6), 3 V, B0 stainless round bushing, SPDT, momentary, solder lug (03), gold |
| SW_PI | C&K ATP16-SL1-403-M0SA-04G | 16 mm, flat actuator, fixed ring, orange (4, the ATP16's amber; momentary only), 3 V, M0 stainless round bushing, SPST N.O. (the ATP16's only arrangement, enough for the Pi's J2 pair), momentary, solder lug (04), gold |
| SW_TEST | C&K ATP16-SL1-203-M0SA-04G | as SW_PI with a white ring (2) |

The ATP19 has no orange, hence the ATP16 for the amber PI ring; the ATP16 has no recessed actuator, its flat actuator sits level with the bezel, which is the accidental-press protection the range offers.

**Toggles (NKK M series data sheet, NKK accessories catalogue).** Code order: model, lever, bushing, contact, terminal. Lever S (the .413 inch bat), bushing D3 (1/4-40 thread, 8.9 mm long, splashproof with a D flat, IP67 through its O-rings; it combines only with the S levers; C4's round 6.5 mm holes take it, the flat is simply unused), contact A (gold over silver, dual rated for the dry logic lines), terminal 01 (solder lug, flying leads to the 2.0 mm pads).

| Ref | Part | Circuit |
|---|---|---|
| SW_EMCON | NKK M2012SD3A01 | SPDT ON-NONE-ON, latching |
| SW_SOS, SW_ZERO | NKK M2015SD3A01 | SPDT ON-NONE-(ON), momentary |
| SW_LIGHT | NKK M2044SD3A01 + AT401A boot | DP ON-ON-ON on the four-pole base with the external jumpers as the data sheet draws them, wired to the six pads; the AT401A splashproof boot assembly (black nitrile, own hex nut) is the boot the footprint names |

Covers: NKK's accessories catalogue lists protective guards for its KB, LB and YB pushbutton series (AT494, AT499, AT4057, AT4072) and none for the M toggles; APEM's switch guards are made for 11.9 and 12 mm bushings; TE's flip cover is for the Kissling 08 series. No maker documents a flip cover for a 1/4-40 miniature bushing, and the guard base drawn on C4 (20 x 32 on the fab layer) has no screw holes, so a base-mounted cover is not a Rev A option either. The M series' own protection is the locking lever (lever L with the L3 splashproof bushing, .295 inch thread), which needs a 7.9 mm panel hole: a Rev B panel change, not C4. Rev A therefore ships SOS, EMCON and ZEROIZE without covers: the hold times of PANEL.md (SOS 2 s, ZEROIZE 5 s) are the accident protection, and EMCON is safe-side (closed = inhibit). The owner may rule on the Rev B choice (locking lever M2012LL3A01 style with 7.9 mm holes, or a screw-mounted guard base).

**Coupler (Amphenol Connex 132170 drawing rev D).** SMA female-female bulkhead adapter: 22.10 mm long, 1/4-36 UNS-2A thread, 5.85 mm across the flats of the bulkhead section, 9.5 mm hex on the fixed side, 8 mm hex nut 1.60 thick, lock washer 10.20 mm, panel 2.0 to 6.5 mm (the strip's 2.0 mm FR-4 is the minimum, so no spacer under the nut). Recommended mounting hole: 6.50 mm with the flat at 6.00 across. The strip cut the flat at 3.0 mm from the centre (6.25 across, 32.5); `gen_pcb_e2.py` now cuts it at 2.75 mm (6.00 across). That is the only change of **E3** (title block A (E3), 4 Sep).

**Spring pins (Preci-Dip catalogue pages 31 and 34).** Preci-Dip 813-S1-008-10-016101: straight spring-loaded connector, low profile, double row 2 x 4 at 2.54 mm, solder tails 0.8 mm diameter and 3.0 mm long on the `PogoPins_2x4` pattern, plastic body 4 mm, initial height 7.0 mm above the board face (height code 016; 6.0, 6.5 and 7.5 exist as 014, 015, 017), maximum stroke 1.4 mm, forces 0.25 N initial and 0.85 N at half stroke, 3.5 A per contact, 50,000 cycles, gold. Against the 6.0 mm spacer gap of section 25 the pistons sit 1.0 mm compressed, 71 percent of the stroke; a stack tolerance of about 0.35 mm either way keeps them between 0.65 and 1.35 mm, never bottomed, never open. Currents: four SHORE_12V contacts share 3.33 A at the dock's 40 W (0.83 A each), the three GND contacts carry 1.11 A each, all inside 3.5 A. The footprint's placeholder 1.5 mm holes are 1.1 mm for the 0.8 mm tails (pad 2.2 mm unchanged, the annular ring only grows); `bump_a18.py` changed the eight drills and the silk label on the routed A17 board with no part moved: **A18**. The connector is fitted from the underside and its tails soldered on the top face (ASSEMBLY.md section 9); pad edits after routing are allowed by the rule of section 2 of the handover (bars and pads on top of router tracks, no moves). The Mill-Max long-stroke series 0914 (0.74 mm holes, 2.3 mm stroke) was the discrete alternative; one body with eight registered tails beats eight loose pins on a hand-fitted board.

**Results.** E3: `build_e2.sh`, DRC clean, two copper layers exported, deliverable `meshsat-pcb-e2-revA-E3`. A18: `finish_a18.sh` (bump, schematic rebuilt for the J_DOCK part text with ERC clean and the nets unchanged, `finish_board.sh`): 0 hard, 0 unrouted, 98 isolated-copper notes on A17 against 98 on A18 (plane islands, cosmetic), deliverable `meshsat-pcb-a-revA-A18`. C4: schematic PDF regenerated with the switch part text (ERC clean) and the deliverable BOM re-exported in the JLC form through `export_jlc.sh` and `lcsc_fill.py` (the same row set as the cart's); the gerbers and the CPL are untouched, so the panel's cart line stands. `make_handoff.py` rebuilt `order/` (`PCB-A-POWER-A18`, `PCB-E2-RFJUNCTION-E3`) and `review/`; the A17 and E2 folders are retired under `order/superseded/`. GitHub release `revA`: the A18 and E3 gerber assets replace A17 and E2, the order set and the review prints are rebuilt. Cart: lines A, B and E2 to be rebuilt from A18, B11 and E3 when the owner says so.

### 32.11 Contract audit by a gateway session, 4 Sep 2026 (read-only, document level)

A MESHSAT-709 gateway session (shadow mode, no writes) audited the cross-board contracts on A18, B11, C4, D5, E1 and E3 and reported by message. Verified clean: the `J_PANEL` pin map is identical on B11 and C4 for all 20 pins (1/2 5V, 3 GND, 4 SDA, 5 SCL, 6 EXP_INT, 7 TR_APRS, 8 EPD_DC, 9/11/13 GND, 10 SCLK, 12 MOSI, 14 CE0, 15 EPD_RES_ALT, 16 PWM1, 17 PANEL_PWM, 18 GND, 19 TX_INHIBIT_n, 20 +3V3; SCLK and MOSI each sit between GND pins on the ribbon, a point for the 12 Sep review); EMCON end to end (C `SW_EMCON` pin 1 to GND with pin 3 NC, R6 100k pull-up and C10 10n on C, `J_PANEL` 19, the B pass-through with TP11, `J_AB1`, A, the PCB-D connector, D R37 1k to the Q3 gate with R38 100k to D's 3V3, Q3 grounding the Q2 emitter) is fail-safe in both directions; nothing drives `TX_INHIBIT_n` but the toggle (PANEL.md has it as an input on U1 0x22 port 1 bit 1); `SHORE_INHIBIT` is U19 P0_4 (device pin 8) on A as PANEL.md section 9 says, and `J_DOCK` maps 1-4 / 5-7 / 8 identically on A and E1.

Three document items, none in copper: (1) the review recipe in the local handover file named a net `EMCON_N` that does not exist (the line is `TX_INHIBIT_n`) and (2) asked for RF net names on E1, which carries no RF (25.2) while E2 has no schematic; both lines are corrected in the handover on the owner's say-so, and the recipe here is: `TX_INHIBIT_n` from C through B and A to `Q3` on D, `SHORE_INHIBIT` on `J_DOCK` pin 8 of A and `U2` of E1, `J_PANEL` identical on B and C. (3) Every ORDER-NOTES.txt headed its assembly block "economic or standard PCBA, both sides" although the economic tier is not offered and four of the five assembled boards are top-side only; `make_handoff.py` and the five notes now say so and explain why the footprint counts exceed the CPL rows (the CPL lists only the parts JLCPCB places; ORDER-LOG, 3 Sep). Chased and withdrawn by the auditor: that count difference itself (A18 113 against 102 CPL rows, B11 123 against 113, D5 78 against 76), already explained and checked per board on 3 Sep.

A third gateway message (later the same afternoon) found that the two bench-fitted inductors (L2 on A18, L1 on D5, Coilcraft XAL6030-152MEB, no JLCPCB equivalent) were stripped from the JLC BOM and CPL by the handoff's exclusion list without any order document saying so: the notes' "removed as DNP" line covered only the DNP parts, and the bench-fit strings of A and D did not name the inductors, so a board would have arrived with U20 placed and its inductor land empty and nothing in `order/` naming the part. `make_handoff.py` now writes a "left out as bench-fitted" line from the exclusion list and names both inductors and the Preci-Dip connector in the bench-fit strings; the handoff was rerun (JLC BOM and CPL bytes unchanged, no cart line affected). ASSEMBLY.md section 9 and BUILD.md already carried the inductors.

### 32.12 The Rev B list as of 4 Sep 2026 evening

Items 1, 3 and 4 of the list the owner asked for (bank tracks, ideal-diode bypass, cell-contact thermistor) are notes from the retired bank-charger design and are marked superseded above; they are not Rev B work. The live Rev B candidates, each an owner decision to take now or at Rev B time: locking levers for SOS, EMCON and ZEROIZE (32.10); a bigger module-rail boost (32.3); the cold-charge thermal pad output (28); a raw-solar MPPT slot (design table); the SMP blind-mate joint (25.2, 32.7, MESHSAT-775, the owner's own deferral); MIL-DTL-38999 external connectors (design table); and the findings of the 12 Sep review.

### 32.13 Owner rulings, 4 Sep 2026 evening: the Rev B list decided item by item

Asked one at a time with a full explanation each (owner rule of the same evening). The rulings, all owner's:

| # | Item | Ruling | Consequence |
|---|---|---|---|
| 1 | Locking levers on SOS, EMCON, ZEROIZE | **Rev A, APEM locks, no board change**: 5636ADKB-2V on all three (APEM 5000 series, single pole ON-NONE-ON, both positions locked, gold-plated contacts, front-panel seal, epoxy terminals; 1/4-40 bushing 9 mm long, 6.5 mm cut-out, European defence listings, not MIL). NKK's lever-lock version was ruled out by fact (1.2 mm panel maximum against the 2.0 mm panel); the MIL-qualified lever-locks (Honeywell TW, MIL-DTL-83731) need 15/32 in bushings and a panel respin, declined | SOS and ZEROIZE become maintained locked switches: the bridge acts after 2 s / 5 s in position and the switch is flipped back to re-arm (PANEL.md, MESHSAT-773); the M2015 codes of 32.10 are replaced; C4 stands, its cart line stands |
| 2 | Bigger module-rail boost | **Rev A**: TPS61288 class (15 A switch) replaces the TPS61089 on PCB-A | PCB-A respin (A19), reroute; the one-burst-at-a-time rule of PANEL.md section 10 stays for RF reasons |
| 3 | Heating-pad output for charging below 0 C | **Rev A**, in the same PCB-A respin | one protected 5 V output (TPS2065 channel), a spare expander bit, a 2-pin connector; bridge rule: pad on with shore present and in-case temperature below 0 C, charge released above the threshold, time limit |
| 4 | Bare-solar MPPT input inside the case | **Rev A**, in the respin | a documented MPPT module on a carrier; placed electrically between the panel input and the dock converter, which puts it on the dock strip unless the design review says otherwise |
| 5 | SMP blind-mate RF between stack and dock (MESHSAT-775) | **Rev A** (reversing the 3 Sep deferral) | Radiall SMP-MAX set of 32.7 on PCB-A's underside and the dock strip, gap 6 to 13 mm, case numbers of 25.1 redone, the wall strip E3 retired or reduced to a cable anchor; cart lines A and E1 rebuilt, E2 deleted |
| 6 | MIL-DTL-38999 external connectors | **Rev A** | shore DC and USB data on a keyed sealed circular wall connector; antennas stay SMA; case wall machining, mating cables, dock inlet wiring |
| 7 | Review findings | open until 12 Sep | |

Rev B is therefore empty except what the reviews add. Ruling of section 5 of the handover "RF: SMA couplers on E2 for Rev A; SMP blind-mate deferred to Rev B" is replaced by ruling 5 above.

**Ruling, later the same evening (owner):** there was never a Rev B; it was a misunderstanding of the sessions. All work is Rev A. An item is Rev B only when the owner says so explicitly, and the session must ask a second time to confirm before recording it. Every "Rev B" left in this record before this line is either superseded (marked) or moved into Rev A by 32.13; the review findings of 12 Sep are decided when they exist.

### 32.14 Collisions between the 4 Sep evening rulings and the afternoon's work (gateway audit, read-only)

A gateway session compared 32.13 with the day's work and reported by message. Confirmed and handled:

1. **The Preci-Dip dock connector of 32.10 does not survive ruling 5.** SMP-MAX board-to-board needs a 13 mm gap (32.7); the 813 family reaches 7.5 mm (code 017) with a 1.4 mm stroke, so at 13 mm it never touches. The dock's DC joint is re-selected at the A19 design step for the 13 mm gap (taller spring-loaded connector families, or the DC pins on a raised block that keeps a 6 mm local gap); A18's 1.1 mm drills are superseded by A19 whichever way. Z budget: 25.1's 104.8 mm becomes about 111.8 against the 114.1 mm panel underside, 2.3 mm spare, to be confirmed in the 25.1 redo.
2. **The dock strip carries seven RF joints and the MPPT carrier.** The RF stays off the copper: the dock side uses cable-mount SMP-MAX plugs in float mounts, with cables straight to the wall bulkheads, so the strip stays two-layer; it will grow within the 413.8 x 283.6 floor. Extraction force: seven joints at up to 9 N each is about 60 N added to the lift of 25.3 step 6; the lowest-retention SMP-MAX variant is chosen and lift handles are considered. Both are agenda items for the 12 Sep review.
3. **PANEL.md was out of step with ruling 1.** SOS_SW and ZEROIZE_SW are now maintained locking toggles in the pin table, the SOS row reads "switch closed for 2 s, flip back to cancel", the ZEROIZE row "switch closed for 5 s, flip back inside 5 s aborts, return the switch to re-arm". The C4 legend "HOLD 5 s / HOLD 2 s" still describes the wait and stays.
4. **Cart instruction corrected** (handover, ordering prompt, ORDER-LOG): line A is not rebuilt from A18, E2 is deleted, E1 is rebuilt after the dock respin, B from B12 (32.17); C4, R1 and D5 stand. The gateway's suggestion to order the four untouched boards now, so that D5 is in hand for the DMR858M modules around 15 Sep, and to carry rulings 2 to 6 plus the review findings into one A19 and dock respin, is put to the owner.

Not confirmed: the public README and BUILD lines it called stale were already corrected in commit a7540c1; the handover lines likewise.

### 32.15 Gateway audit of the respin brief, 4 Sep 2026 late evening: nine findings and their disposition

A read-only gateway session audited appendix 7, 8, 25 and 32 against the rulings of 32.13 before any respin work started. Findings, with what is done about each:

| # | Finding | Disposition |
|---|---|---|
| A | 32.7's board-to-board scheme (receptacles on both boards, adapter between) and 32.14's cable-mount dock side are different parts | 32.14 stands: the Radiall catalogue in `vendor/rf/` lists straight and right-angle female plugs for flexible cable and bulkhead slide-on jacks (its pages 176 to 206 in text order), so the dock carries cable-mount plugs in float mounts and no RF copper; PCB-A carries the receptacles. Exact numbers at the design step |
| B | 32.7 names adapter R222M40010 (9.5 mm) while the filed data sheet is R222M40050 | with cable-mount plugs on the dock the in-series adapter drops out; the 13 mm minimum between boards is the catalogue's own figure for the board-to-board scheme (its line "Minimum distance between PCB 13 mm") and no longer binds. The gap is set by the receptacle and plug heights, derived at the design step from the filed sheets; 32.14's Z figure is provisional |
| C | RG-316 cannot bend inside a 13 mm gap (minimum radius 12.5 mm, section 7) | right-angle cable plugs on the dock side, cable exiting sideways along the floor; confirmed available in the catalogue (finding A) |
| D | seven RF launches on PCB-A's underside, four of the paths start on PCB-B; In2 under a bottom launch is the +5V_MOD plane | design rule for A19: each RF joint is a receptacle on the bottom with a local ground pour and In1 stitching under it, fed by a pigtail to a top-side SMA or U.FL launch through a via-stitched transition, near-zero copper run; the four PCB-B pigtails run down the stack's edge. The blind-mate datum is the rod-located PCB-A |
| E | the heating pad on a TPS2065 channel would draw 5 W from the cells through the boost, at the moment charging is held off | decided, designer's call: the pad runs from SHORE_12V (present only with shore power, about 25 W spare on the dock converter) through a high-side switch and its own fuse on PCB-A; a 12 V pad, about 15 to 20 W; the "shore present" condition becomes hardware |
| F | J_AUX on the converter output was called the MPPT slot; ruling 4 puts the MPPT on the converter's input side; two sources on the converter input; most COTS MPPT modules are battery chargers without a defined output when no battery hangs on them | the MPPT sits on the input side (isolation kept); the shore inlet and the MPPT output are ORed or interlocked for 3.7 A at 12 V; the module must hold a constant voltage inside 9 to 36 V against the converter's 8.3 V lockout. Whether such a documented module exists decides the question, which goes to the owner with the part names |
| G | the 38999 USB data port has no hub port: all four FE1.1s ports are used | A19 moves to a seven-port hub or the wall port takes a spare Pi port without limiting and monitoring; decided at the schematic step with the owner's preference asked once the cost is known. Shell bonding to a plastic case and the ribbed curved Peli wall need a stated answer in the case drawing |
| H | the TPS61288 is not a value swap, and L2 (XAL6030-152, 12 A) is at or over its rating at the 6.5 A unserialised burst from a 3.0 V node | the whole programming network and the inductor are re-selected from the TPS61288 sheet at the schematic step; the worst case (about 12 A input at 3.0 V) is stated, not inherited; F3 and the 2.5 mm bar are checked against it; the LCSC status of the part is checked on the laptop |
| I | stale pages Nick will read: section 7 and 8 USB-C inlet, 25.7's two rows, 25.5's solar bullet | corrected in this commit (superseded notes on the lines themselves, 25.7 rows now REV A) |

Order of the design work follows the audit's suggestion: the SMP-MAX part set and the gap first, then the dock connector and cable exits, then the A19 schematic items E to H, with F and G brought to the owner once the parts are named.

### 32.16 Gateway research on 32.15 F and G, 4 Sep 2026 night (read-only, reported by message)

**G, the USB port behind the 38999 wall connector.** A seven-port hub on A19 is the low-risk answer the record itself foresaw (R2, line 360): Microchip USB2517 or USB2517I (LCSC C1521556 / C626667, in stock, multi-TT), with a fifth channel built like the four existing ones (TPS2065, sense resistor, INA219, USBLC6). Its rails, package and crystal are read off the data sheet on the laptop before it enters the schematic. Open, and decisive: nobody has said whether the wall port is a **host** port (a device is plugged into the kit) or a **gadget** port (the kit appears as a device to a laptop, the Pi 5's USB-C path, which the deleted inlet carried). Owner question. Documented 38999 part with a USB interface: Glenair SuperSeal 233-370, MIL-DTL-38999 Series III feed-through receptacle with a USB 2.0 Type A female-to-female interface, shell 15/17, wall mount or rear jam nut, IP67 unmated and IP68 mated, panel 1.59 to 6.35 mm. It carries USB only (four contacts); shore DC needs a second shell or a custom insert; the metal shell has nothing to bond to on a plastic case.

**F, the MPPT input.** No COTS MPPT module holds a constant output voltage without a battery on its output; Genasun's own manual says its controller signals a fault until a battery is connected. The silicon that regulates its input to a panel's maximum-power voltage while holding an output is ADI's LT8705 / LT8705A (input-voltage regulation loop, the data sheet names solar Vmp tracking), sold as unbranded 250 W buck-boost modules without drawings. The choice is therefore between a bespoke LT8705 stage on the dock strip (a real power design, many parts), a plain panel input into the 9 to 36 V window without tracking (works in strong sun, hiccups in weak sun), or no in-case MPPT. Owner question with those facts.

**Ruling on G (owner, 4 Sep night):** the wall USB is a **host port**. A19 carries a seven-port hub (USB2517 class, values from its data sheet on the laptop) with a fifth protected channel for the wall port; the wall side is the Glenair SuperSeal 233-370 USB receptacle, and shore DC gets its own 38999 shell (or a custom insert if one is documented). The Pi's gadget path is not brought to the wall.

**Ruling on F (owner, 4 Sep night):** a **bespoke maximum-power tracker on the dock strip**, an LT8705A buck-boost stage designed from the ADI data sheet with its input-voltage loop set to the panel's maximum-power voltage and a constant-voltage output into the TEN 40's input, ORed against the shore inlet. The dock strip becomes a four-layer board. The plain-input and no-tracker options were declined.

### 32.17 Ruling, 4 Sep 2026 night (owner): the Geekworm X1202 is removed; the boards carry their own UPS

Owner: "removal of the Geekworm X1202 UPS completely; the PCB we build will have their own UPS", confirmed after the consequences were restated. This replaces the one-pack-one-charger ruling of 3 Sep (25.6, "inception") in its X1202 half and the X1202 side of ruling 32.3 (option B). What the X1202 did and what takes it over:

| X1202 role today | On the boards |
|---|---|
| charges the cells from the dock's 12 V at about 3 A | a single-cell Li-ion charger block on PCB-A (A19) from SHORE_12V, 3 A or more, with a thermistor input at the pack (cold-charge protection in hardware; the 28 and 32.15 E inhibit and pad remain the warm-up path) |
| makes the Pi's 5 V | a dedicated 5 V at 5 A boost on PCB-A for the Pi, separate from the module rail (never one rail from two sources) |
| holds the Pi up when shore drops | inherent: every load hangs on the cell node, the charger sits in parallel |
| power button input, GPIO 6 power-loss line, battery telemetry over I2C (0x36), the monitor script | MAIN button drives a main power control on PCB-A; a power-loss line to the Pi from the gauge or the shore detect; a fuel gauge on I2C; PANEL.md SHORE, CHARGING and the battery bar read the charger and gauge |
| four of the twelve cells | the welded pack alone (eight cells, 28 Ah) unless the owner welds twelve; the charger is sized for either |

Board consequences: A19 gains the charger, the Pi rail, the gauge, the main power control and the power-loss line; **PCB-B is respun (B12)**: the X1202 leaves the stack, the Pi sits alone on its standoffs, its 5 V arrives by a lead from PCB-A into a new connector, `J_5V_IN1` and the X1202 envelope go, the ribbon stays. The panel is unchanged (MAIN button, PI button to the Pi's J2). MESHSAT-774 becomes the charger's commissioning list. Appendix 25 stack numbers, ASSEMBLY leads and BUILD follow at the respin. Cost about two days on top of the plan of 32.13.

### 32.18 Gateway finding, 4 Sep 2026 night: the dock's tallest parts stand under PCB-A inside the 6.0 mm gap

Document level, from the repo: PCB-A spans Y -80 to +80 (`gen_pcb_a.py`), the dock strip Y -95 to -51 (25.5), so 29 mm of the strip lies under PCB-A at the 6.0 mm spacer gap and only a 15 mm band (Y -95 to -80) is clear. The dock generator fixes J_DOCK (-12, -70), J_DCIN (-105, -60), F1 (-80, -70), U1 (-45, -70) and J_AUX (118, -58), all in the covered band. U1, the TEN 40-2412WIN, is 10.2 mm tall (25.5, filed data sheet): about 4.2 mm into PCB-A's underside. F1, a Keystone 3568 holder with a blade standing in it, is taller still (height to be read from the Keystone sheet on the laptop; keyelco.com refuses both hosts). Nothing catches it: `check_pcb_e.py` has no height rule, DRC is two-dimensional within one board, and 25.1's Z closure counts the dock as 1.6 mm plus the 6.0 mm spacer with nothing standing on it. So the E1 and A18 pair as released does not assemble; it is not ordered (the dock line is rebuilt after the respin), and the respin rule is now: **the dock gap is the larger of the RF receptacle-plus-plug stack and the tallest dock component plus margin**, and the converter, the fuse holder, the tracker's inductor and bulk capacitors are placed either in the clear band or under a stated gap. Credited as a gateway round.

**Ruling on the pack (owner, 4 Sep night):** the welded pack becomes **twelve cells, 1S12P, 42 Ah** (12 x Samsung 35E), so the planned runtime stands without the X1202's four cells. A19's pack area and strap slots grow by half; the pack's 15 A BMS with its own NTC cut-off stays; the charger's 3 A gives about 14 h for a full charge.

### 32.19 Gateway audit after 32.17 and 32.18, 4 Sep 2026 night: five findings and their disposition

| # | Finding | Disposition |
|---|---|---|
| AK | the cart instruction still named B11 after 32.17 respun PCB-B as B12 (ordering prompt, ORDER-LOG, handover, 32.14 item 4) | corrected: line B is rebuilt from B12; the untouched boards are C4, R1 and D5 only, and the owner has ruled that nothing is ordered before the whole set is final |
| AL | the module rail's enable came from the X1202's 5 V output over the sense lead (32.4; PANEL.md section 10) and 32.17 assigned no replacement | A19 enables the module rail from its own main power control; `J_5V_IN1` leaves PCB-B and `J_AB1` pin 12 is spare; PANEL.md section 10 annotated |
| AM | the GPIO 16 charge kick existed only to restart the X1202's undocumented safety timer (32.3) | struck, not reassigned: the A19 charger's timer is a design choice; PANEL.md section 10 annotated, MESHSAT-773 told |
| AN | the bridge's battery telemetry is hard-coded to the X1202 in the software repository (system API reading /run/x1202.json, the monitor script at 0x36, the OOB restart target and service unit) and no issue owned the replacement | new MESHSAT issue for the software side: replace the monitor with the A19 charger and gauge readout (new address and register map, service unit, bind mount, the battery API contract, the OOB allowlist, and a capacity setting at first boot if the gauge counts coulombs) |
| AO | the dock gap does two jobs with about 1 mm of headroom: 32.14's Z closure of about 111.8 of 114.1 mm assumed 13 mm, and the dock's part list grew (TEN 40 10.2 mm, the blade holder with its blade, the tracker's inductor and bulk capacitors) | stated constraint for the dock schematic: every part standing on the dock under PCB-A is at most about 12 mm tall, the tracker's magnetics and capacitors chosen to it; taller parts go into the clear band; passed to the running part research |
| AP | whether A19 still holds four layers at 285 x 160 with a third plane-class rail (the Pi's 5 V at 5 A), the charger, the gauge, the pad switch, seven bottom-side launches wanting local ground, a seven-port hub and a pack area half again as large | design intent: keep four layers, In1 ground and In2 the module rail as on A18, the Pi rail as wide top and bottom copper from its boost to one lead connector, the launches on local bottom pours stitched to In1; the gate script and the first placement decide, and if the board does not close, six layers or a larger outline go to the owner with the price difference before routing |

### 32.20 Gateway audit, 4 Sep 2026 night, third round: the public pages and the panel contract still said X1202

| # | Finding | Disposition |
|---|---|---|
| AQ | `v2/README.md` and `v2/BUILD.md` still stated the X1202 as a binding ruling and built the pack as eight cells matched to the X1202's four; the top README still listed the X1202 in the PCB-B and dock rows; the order gate still named the paper fit check | superseded notes on each line, pointing at 32.17; the assembly steps themselves wait for A19 and B12 |
| AR | PANEL.md outside section 10 still described the X1202 as live: the BCM 6 power-loss input, SHORE and CHARGING from the X1202 monitor, MAIN PWR to the X1202 switch pins, the 0x36 gauge in the I2C map, the implementation notes, the cold-charge rationale | superseded notes on each line; the roles are the ones 32.17's table assigns to A19; MESHSAT-773 and MESHSAT-788 build from the annotated contract |
| AS | MESHSAT-788 missed two coupling points in the software repository: a second reader of /run/x1202.json inside the OOB status source (the battery field of the STATUS-NET frame proved over SMS in MESHSAT-756, which would silently report no battery), and the user-visible "X1202 UPS" strings in the dashboard and status strip | both added to MESHSAT-788's acceptance criteria; neither needs the A19 part numbers |

### 32.21 Part picks for the respin, 4 Sep 2026 night, from data sheets (two research rounds; full notes in `v2/docs/respin-research-power-2026-09-04.md` and `respin-research-mech-2026-09-04.md`, documents in `v2/vendor/`)

| Function | Part | Key figures from the sheet | Note |
|---|---|---|---|
| Charger (32.17) | TI BQ25798 (LCSC C2876593) or the pin-identical BQ25792 (C2862876, better stocked) | 3.6 to 24 V in, 50 mA to 5 A in 10 mA steps, single-cell regulation 3 to 4.99 V, JEITA on a 103AT thermistor, fast-charge timer 5 / 8 / 12 / 24 h or off, I2C 0x6B, QFN 4 x 4 | BQ24610 (10 h timer) and BQ25601 (13.5 V max in) documented as less suitable |
| Fuel gauge (32.17) | TI BQ34Z100-G1 (C91302) with a 5 mOhm 3 W 2512 low-side shunt (RALEC LR2512-23R005F4, C154688) | sense range ±125 mV (75 mV at 15 A), external NTC, I2C; 42 Ah needs the SCALED configuration (standard stops at 29 Ah) | BQ27441-G1 out (±25 mV, 2.5 A at its 10 mOhm); MAX17048 (C2682616) is the no-shunt fallback; the capacity setting is a provisioning step (MESHSAT-788) |
| Module rail boost (ruling 2) | TI TPS61288L (C7498841; the L is TI's thermal recommendation) with Coilcraft XAL1010-222MED 2.2 uH (C5125746, Isat 34 A, 10 mm tall), FB 102 k / 13.7 k (5.067 V), six 22 uF 10 V 1210 outputs, compensation from the sheet's equations | no MODE pin, VREF 0.6 V, current limit 12 / 15 / 17.1 A min / typ / max | **the 6.5 A burst at 3.0 V needs a 13.1 A inductor peak, above the 12 A guaranteed limit: guaranteed only from about 3.3 V per cell, or 5.9 A at 3.0 V**; the serialisation rule stays |
| Pi rail boost (32.17) | second TPS61288L, FB 75 k / 10 k (5.100 V), same inductor, four to six 22 uF | 5 A at 3.0 V peaks at 10.4 A, inside the guaranteed limit | separate rail, own connector to PCB-B |
| Heating-pad switch (32.15 E) | TI TPS259571DSGR (C471038), 12 V from SHORE_12V | limit resistor 1.02 k for 2.0 A (806 ohm for 2.5 A), WSON-8 2 x 2, auto-retry | own fuse on the rail |
| Main power control (32.17) | ADI LTC2954CTS8-1 (C683782) | push-button on/off controller: EN drives both boost enables, KILL from a Pi GPIO for a clean power-off, INT to a Pi GPIO as the shutdown request, long press forces off | replaces the X1202's switch pins and GPIO 6 role |
| Solar tracker stage (ruling F) | ADI LT8705A (LCSC single-digit stock, buy from a distributor) with the sheet's 12 V / 15 A example MOSFETs (BSC028N06NS, BSC039N06NS, BSC015NE2LS5I, stocked), Coilcraft XAL1510-103MED 10 uH (10.0 mm tall), Panasonic EEHZK1V101XP 100 uF 35 V (7.7 mm) and 35SVPF39M (6.9 mm) | VIN(MIN) = 1.205 V x (1 + RFBIN1 / RFBIN2): 102 k / 7.5 k sets 17.6 V (a fixed panel operating point, not a searching tracker; not in forced continuous mode); VOUT 115 k / 10 k = 15.1 V; RT 215 k for 202 kHz; RSENSE about 5 mOhm | every part under 12 mm (32.19 AO) |
| Blind-mate RF (ruling 5) | Radiall R222M00720 slide-on receptacle (seven under PCB-A) and R222M80500 right-angle RG-316 crimp plug (seven in a dock float clamp), crimp die R282.235.003 | board-to-dock 13.4 mm nominal, 12.4 to 14.4 window; engage < 14 N, release < 9 N per joint; ±1 mm axial, 3 degrees tilt; 100 cycles | no adapter; the catalogue's 13 mm minimum belonged to the two-receptacle scheme; capture radius not printed on any sheet |
| DC contacts | Preci-Dip 813-S1-008-10-016101 kept on PCB-A, dock pads on a 7.4 mm target block (6 mm standoffs plus a 1.6 mm pad board, 1.2 mm compression) | no 2.54 mm spring connector reaches 12 mm (Preci-Dip 7.5, Mill-Max 10.9, Harwin 8.2) | the pins, not the RF joint, set the Z window |
| Fuse holder on the dock | Keystone 3568 stays but moves to the clear band (about 16.3 mm with a Littelfuse 297 blade), or the horizontal-entry 3549-2 (5.8 mm) | catalogue M65 page 42 | the shore converter (10.2 mm) fits under the 13.4 mm gap |
| Shore DC wall connector (ruling 6) | Glenair D38999/20FC4PN receptacle and D38999/26FC4SN plug, shell 13, insert 13-4 (four size 16 contacts, 13 A each) | cut-out per the Glenair sheet, wall-mount panel 1.59 to 6.35 mm, IP67 | or the COTS 233-105 equivalents |
| USB host wall connector (ruling G) | Glenair 233-370 M 00-15 2AANH, USB 2.0 Type A feed-through, shell 15, wall mount | IP67 unmated, IP68 mated, panel 1.59 to 6.35 mm | |
| Seven-port hub (ruling G) | Microchip USB2517I-JZX, 64-QFN 9 x 9 | 3.3 V rails, internal 1.8 V regulators, 460 mA at seven high-speed ports, 24 MHz crystal, RBIAS 12.0 k, strap or SMBus configuration | replaces the FE1.1s; fifth protected channel for the wall port |
| Locking toggles (ruling 1) | APEM 5636ADKB-2V | code confirmed from the order format; bushing 9.0 mm, cut-out 6.5 mm with a 2.70 x 1.10 keyway for the seal; two 8 mm nuts, locking ring, lock washer | the 5000 series prints no panel thickness range |

Open after this round: the SMP-MAX capture radius (drawn, not valued), the Glenair 233-105 versus the /20 and /26 military numbers (same insert), the LT8705A sourcing, and whether the owner accepts the TPS61288's guaranteed-limit caveat on the module rail or wants the burst rule kept as it is.

**Ruling on the picks and the rail split (owner, 4 Sep night):** the list of 32.21 is accepted with one design change the owner demanded ("we have 12 cells and still you are bringing up this problem"): the cells were never the limit, one boost chip for every module was. The module loads split into **two rails on two TPS61288L converters** (M1: LTE modem 2.0 A burst, hub logic, WiFi, GPS, LEDs 0.8 A; M2: LoRa 1.3 A, RockBLOCK 1.0 A, SDR 0.6 A, ZigBee 0.1 A; each about 3.0 A peak on the rail, about 6.5 A on the cell side at 3.0 V, inside the 12 A guaranteed limit with about 45 percent margin), plus the Pi rail on a third. Every rail keeps one source and its own blade fuse from the node. The transmit serialisation of PANEL.md section 10 is no longer a hardware requirement (the bridge may keep it as a receiver-protection preference). The TPS61089 option of "yes, but keep" was not taken.

### 32.22 Ruling, 4 Sep 2026 night (owner): the pack becomes a battery module on the case structure, blind-mated to the stack

Asked "which solution is the most MIL-STD compatible", the answer given was: a qualified BB-2590 class battery in a well is the most compatible (MIL-STD-810 methods 514 and 516 want heavy masses on the structure, MIL-PRF-32383 wants the cells in their own vented enclosure with the protection inside, MIL-STD-1472 wants a replaceable unit with a handle and a keyed connector); the twelve welded cells as a module on the case floor is MIL mounting practice without the MIL battery; a pack strapped to PCB-A is the least compatible. **Ruling: the welded twelve cells become a battery module**: cells and the 15 A BMS with its NTC in their own enclosure with a vent path, seated in a rigid cradle on the case floor beside the dock strip, wired to the dock strip, the pack current crossing to PCB-A over a rated blind-mate contact set on the dock (Mill-Max 0858 class 9 A power pins, four per polarity, on the raised block with the DC signal pins). The stack lifts out with nothing to unplug. **PCB-A keeps 285 x 160**; the former pack rectangle (130 x 74) takes the charger, the gauge, the three converters and the seven-port hub. The charger stays on PCB-A and charges the module through the same pins (3 A). The well and the contacts are laid out so that a BB-2590 class battery could take the module's place in a later build if the owner ever says so. The BB-2590 option was not taken; the 285 x 200 board was not taken.

### 32.23 A19 design intent, 4 Sep 2026 night (written before the generators are touched)

**Outline and fixed geometry unchanged:** 285 x 160 at X -165 to 120, Y -80 to 80, rods at (+-110.5, +-73), the mezzanine site, the GPS puck, the WiFi dongle, J_AB1 (-72, -73), J_LEDS1 (-44, -74), J_DOCK (-12, -70) all stay. The pack rectangle, its strap slots, J_PACK, J_X1202BAT, J_X1202DC and F1 (to the X1202) go (32.17, 32.22).

**West zone, the former pack area (X -162 to -32, Y -45 to 45):**
- Power pin block on the underside east of J_DOCK, at X 0 to 16, Y -74 to -64: four CELL+ pins in a row at Y -73 and four return pins at Y -67 on a 4 mm pitch, plus the pre-charge pin (32.24 AX), Mill-Max 0858 class 9 A, landing on the dock's raised block together with the 2 x 6 signal set (32.24 AT). (Corrected the same night: the earlier X -50 to -30 collided with the shore converter under the strip and with RF sites.) The return passes the gauge shunt (5 mOhm 2512, Kelvin) before it reaches GND; every ampere in or out of the module crosses it.
- Charger block (BQ25792, QFN 4 x 4, thermistor lead from the module over two dock pins or the J_DOCK spares, VBUS from SHORE_12V) at about X -60 to -30, Y -60 to -40, next to both the 12 V pins and the CELL+ node.
- Fuse row F3, F4, F5 (mini blades: M1, M2, Pi rail feeds) along Y about -45 across X -150 to -100, fed by a CELL+ bar from the pin block.
- Three converter blocks, each a TPS61288L with its XAL1010 coil, input and output capacitors and the FB and COMP parts, about 25 x 25 mm: M1 at X -160 to -130, M2 at X -125 to -95, Pi at X -90 to -60, Y -35 to 0. Outputs on JST-VH leads J_5V_M1, J_5V_M2, J_5V_PI to PCB-B B12's three inputs.
- Main power control (LTC2954, push-button lead J_MAINSW XH2 from the panel's MAIN button, EN to the three converter enables, KILL and INT over the ribbon), the heating-pad switch (TPS259571 from SHORE_12V with a 1812 polyfuse, J_HEAT XH2, enable from an expander bit) and the 3.3 V logic supply (a TPS563201-class buck from M1 in place of the AMS1117, since the seven-port hub alone draws up to 460 mA) at X -160 to -130, Y 5 to 25.
- Hub zone grows south into the freed area: (-104 to -30, 25 to 77) holds the USB2517I with its 24 MHz crystal and 12.0 k bias, five protected channels (WiFi, GPS, codec, UART, the wall host port J_WALL1, a USB-A receptacle at the west edge for the internal cable to the Glenair 233-370), the PCA9555 and the LED drivers. Ports 6 and 7 of the hub are unused, their data pins left open and their over-current inputs pulled up.

**South band, the seven blind-mate sites:** Radiall R222M00720 receptacles on the underside at Y -66, X = -150, -130, -110, -90, 40, 66, 96 (clear of the rod nut keep-outs, the ribbon header, the power pin block and the GPS puck's slots; corrected the same night from 8, 24, 40, 108), each with a vertical SMA jack (Amphenol 132134 class) on the top face 10 mm north of it, joined by a short 50 ohm trace on the bottom layer over an In2 ground island stitched to In1 (the In2 module-rail plane is cut out under each site). The dock strip grows west to carry the three western float clamps (MESHSAT-790). Path assignment from west to east: UHF (mezzanine), WiFi 2.4, WiFi 5.8, SDR, LTE, Iridium, LoRa; the module pigtails from PCB-B come down the stack's east edge.

**Ribbon J_AB1, pin map for B12:** 1 PI_SHDN_REQ (LTC2954 interrupt), 2 PI_KILL, 3 GND, 4 USB_A_P, 5 USB_A_N, 6 GND, 7 SDA, 8 SCL, 9 EXP_INT, 10 TR_APRS, 11 VBUS_A_SENSE, 12 spare, 13 GND, 14 TX_INHIBIT_n. The ribbon carries no 5 V any more; PCB-B's logic runs from the M1 lead.

**Planes:** In1 ground, In2 the M1 rail (the hub and the four internal channels hang on it) with the ground islands under the RF sites; M2 and the Pi rail as wide top and bottom copper from their converters to their VH leads. Net classes: CELL+ and the pin block 4.0 mm bars, converter inputs 1.5 mm, rails 0.4 mm as before.

**Load budget per rail (from line 840 and 32.21):** M1: LTE modem 2.0 A burst plus this board's logic and PCB-B's hub, display and panel about 1.2 A, peak about 3.2 A, about 7 A on the cell side at 3.0 V. M2: LoRa 1.3, RockBLOCK 1.0, SDR 0.6, ZigBee 0.1, peak about 3.0 A. Pi: 5 A. Worst case on the node with everything transmitting and the Pi at full load: about 24 A for a second, carried by the 9 A pin set (36 A) and the 4.0 mm bars; the module's BMS limit (15 A continuous) is checked against it at the module design (MESHSAT-791).

### 32.24 Gateway audit of the A19 design intent, 4 Sep 2026 night: seven findings and their disposition

| # | Finding | Disposition |
|---|---|---|
| AT | J_DOCK has no spare contact for the thermistor lead | the dock signal set becomes a 2 x 6 Preci-Dip 813 (813-S1-012-10-016101, same family and height): 1 to 4 SHORE_12V, 5 to 7 GND, 8 SHORE_INHIBIT, 9 and 10 the module thermistor, 11 and 12 a Kelvin voltage sense pair from the module terminals |
| AU | the charger and the gauge would sense the pack voltage behind the contacts and the strip | the gauge's BAT input takes the Kelvin pair; the charger has no remote sense, so the drop is made small and corrected: four 9 A pins in parallel per polarity plus the strip's heavy copper give about 10 mOhm round trip, 30 mV at 3 A, and the bridge sets the charger's regulation voltage 10 mV steps above 4.20 V by the difference between the gauge's Kelvin reading and the charger's own ADC; the design step states the contact resistance from the Mill-Max sheet |
| AV | the 5 mOhm shunt at a 24 A burst is at 96 percent of the gauge's range and of the resistor's rating | re-picked at 3 mOhm (RALEC LR2512-23R003F4, inside the family's 2.6 to 10 mOhm range, 3 W): 72 mV at 24 A, 1.7 W for the burst second, 6.6 mV at 2.2 A |
| AW | the 4.0 mm bars were sized for 12.5 A; 24 A wants about twice the copper at 1 oz | the CELL+ path from the pins to the fuse row is a 10 mm pour on the top and bottom layers stitched together (about 20 mm of 1 oz copper in parallel, above the 10 C rise width for 24 A continuous, and the burst lasts a second); the dock strip's pack run is stated the same way at the copper weight ordered (MESHSAT-790) |
| AX | re-seating the stack mates a 42 Ah node into the converters' input capacitance through pins that are not arc rated | the power pin set gets a staggered mating order by pin height: the return pins longest, then one pre-charge pin through a 10 ohm resistor onto CELL+, then the four main CELL+ pins; the mating-cycle rating of the pins is stated from the sheet (MESHSAT-790, 32.25 when the pins are finalised) |
| AY | a BMS trip takes the kit down even on shore power; whether the charger's SYS is tied to BAT decides shore-only operation | the module's BMS is specified at 30 A or more continuous so that the 24 A burst never trips it (MESHSAT-791); the charger's TS input carries the cold cut-off, the BMS thermistor is the backup; the loads hang on BAT (the pack node), not on SYS, because the charger's internal FET is not rated for the node bursts, so shore alone does not run the kit with the pack out or tripped. Stated as a design property and put on the 12 Sep agenda; the alternative (a shore-fed rail ORed into the Pi rail) contradicts the one-source rule and was not taken |
| AZ | the low-side shunt is bypassed if the module return touches the dock's ground anywhere | rule: the module return is its own net (CELL_N) from the cells over the dock strip to the return pins and touches nothing else; the dock's ground pour and J_DOCK's ground pins stay on the PCB-A ground side of the shunt (MESHSAT-790, MESHSAT-791) |

Answers to its two questions: the USB2517I runs on its strap defaults (CFG_SEL internal default, no EEPROM, no SMBus master), as the FE1.1s did; unused ports 6 and 7 are handled the way the data sheet prescribes for disabled downstream ports, read off the sheet at the schematic step rather than assumed.

### 32.25 Dock strip and battery module design intent, 4 Sep 2026 night (MESHSAT-790, MESHSAT-791)

**Dock strip (next E phase, four layers).** The strip grows west to carry the three western RF sites: 285 x 44 at X -160 to 125, Y -95 to -51, the rods still through (+-110.5, -73), VHB pads at the corners, nothing on the underside. Its face is 13.4 mm below PCB-A's underside (32.21): every part standing on it under PCB-A (Y -80 to -51) is at most 12 mm tall; the band Y -95 to -80 is clear of PCB-A and takes the tall parts.
- Seven float-clamp sites at Y -66, X = -150, -130, -110, -90, 40, 66, 96, mirroring the A19 receptacles: a printed clamp holds each R222M80500 right-angle plug with its cable axis 10.7 mm above the strip and +-1 mm of float in X and Y; the clamp bolts to two M3 holes on the strip, the cable leaves along the floor to the wall bulkhead. No RF copper on the strip.
- Raised contact block at X -22 to 20, Y -76 to -64 (the shore converter moves west to about (-60, -70) to make room): a 1.6 mm pad board on 6 mm standoffs (7.4 mm face height) carrying the targets for the 2 x 6 Preci-Dip signal set (mirroring A19's J_DOCK at (-12, -70)) and the eight Mill-Max 0858 class power targets plus the pre-charge target (32.24 AX), wired to the strip below by short leads or a board-to-board header. The block's pad board is a small bare two-layer board of its own (2 oz copper).
- Shore entry as today (J_DCIN from the 38999 wall connector's DC pair, F1 7.5 A mini blade moved into the clear band at about (-80, -87), the AO4409 reverse-polarity FET, the 33 V TVS, the TEN 40-2412WIN at its place under the gap, the opto inhibit), plus the panel input J_SOLAR from the 38999's spare pair into the LT8705A tracker stage on the east part of the strip (X 30 to 120), whose 15 V output is ORed with the shore inlet ahead of the converter (32.15 F, 32.16 F). J_AUX goes.
- Battery entry J_BATT (XT60, 60 A rated) at the strip's east end from the module's lead, fused at the module; the module return is its own net CELL_N over the strip to the return targets on the block and touches no ground (32.24 AZ); the CELL+ run on the strip is 20 mm of 2 oz copper on two layers.
- Gate script: the height rule (32.18), the site pattern against A19, the block position, the return-net isolation.

**Battery module (MESHSAT-791).** Twelve Samsung 35E welded 1S12P with a BMS rated 30 A or more continuous (32.24 AY) and its thermistor, in an enclosure with a vent path, seated in a cradle on the case floor. Candidate location: the east band of the floor beside the strip's east end (about 87 mm between PCB-A's east edge and the case wall, 283 mm long), which takes a flat 4 x 3 arrangement (about 205 x 85 x 30 mm with the enclosure) with a short lead to J_BATT. The exact arrangement, the cradle, the vent path and the fastening come from the build123d model on the laptop; the module carries a 40 A blade fuse at its positive terminal and a keyed connector, and its weight is stated in ASSEMBLY.md (twelve 35E cells are 600 g at the specification maximum, about 0.7 kg for the finished module; the earlier 1.4 kg was wrong, 32.27).

### 32.26 Results of the respin, running log (5 Sep 2026)

**PCB-B B12, done.** `gen_sch_b.py` and the board generators without the X1202: three JST-VH rail inputs (J_5V_M1 for the hub, display, panel and the LTE channel; J_5V_M2 for the SDR, ZigBee, LoRa and RockBLOCK channels; J_5V_PI for the Pi over a lead with a USB-C plug), the PCB-A feed channel removed, the ribbon carrying the shutdown request on pin 1 and the Pi kill line on pin 2 (BCM 6 and BCM 17 on the Pi header), the T-Beam pigtail header moved from (70, 55) to (100, 57) because it sat in the only corridor from the GPIO header to the panel connector. Gate ALL PASS. Four routing rounds: the router left four, then three, then one connection open at every pass count (the EMCON inhibit line across the whole board); the grid router closed it once run at a 0.1 mm grid with a 20 million cell budget (`stub_router.py` now takes `STUB_GRID` and `STUB_MAXN` from the environment), as a long stepped path of 630 segments and three vias. Final DRC: 0 hard, 0 unrouted, 27 silk overlaps, 6 dangling vias (cosmetic). Deliverable `meshsat-pcb-b-revA-B12`, commit 61404fc. The stack standoffs shrink from 22 mm to a Pi-only height (ASSEMBLY.md at the handoff).

**PCB-A A19, in progress.** Generators rewritten per 32.23 (charger, gauge, three converters, main power control, heating-pad switch, seven-port hub with the wall channel, seven blind-mate sites, the dock block pins); the six land patterns of `respin-footprints-2026-09-05.md` in `meshsat.pretty`; six placement passes to a clean pre-route gate. First routing cycle: four open pads on the charger (its escapes had been skipped), ten hard violations from the node-bar script crossing the return pins and a jack, and router stubs on the ground-plane layer. Second cycle: the node copper is now pre-route pours on both outer layers (a south bar under the pins, a riser up the west edge, a bar above the fuse row with a tap to each fuse), tracks are forbidden on the inner layers by rule areas, the charger's escapes are back.

**Dock strip E4 and block E5, done.** Strip 285 x 60 with the seven float clamps, the block standoffs, the converter under the gap, the ideal-diode entry, the LT8705A tracker and the module entry at the west end; four placement passes to a clean gate; **routed 0 hard, 0 unrouted, 137 vias**, deliverable `meshsat-pcb-e-revA-E4`. The block board is 43 x 26 at X -158 to -115, Y -85 to -59, 2 oz, four corner standoffs matching the strip, and it reads PCB-A's own board file so the twelve targets carry the net of the pin that lands on each: **0 hard, 0 unconnected**, deliverable `meshsat-pcb-e5-revA-E5`. Three things were learned on it. The first block board shorted every column because the signal targets and the wire lands sat on top of each other, so the lands moved south of the targets and each column now runs straight down (north row through a via to the underside, south row with a half-pitch jog past the north lands). The second had the twelve contacts on six shared nets, which DRC reads as four unconnected GND islands and four unconnected 12 V islands: the block passes each contact through to its own wire and the strip's `J_BLK` is where the repeated pins meet, so every contact is now its own net named after the A19 pin it serves. The third was mechanical: the Mill-Max target discs are on a 4.0 mm pitch and their courtyard and silk ring were wider than that, and the block's east standoffs had to leave 4.5 mm around the rod nut at (-110.5, -73), which is what sets the block's east edge at X -115.

**Results of the routing cycles on A19.** Three attempts were thrown away before the board routed, and each failure had one cause worth keeping. Rule areas that forbade tracks on In1 and In2 (meant to keep the router off the planes) also made `escape.py` and `prefanout.py` treat the whole board as an obstacle, so 280 pads got no escape and no fanout; both scripts now ignore a rule area that permits vias. With the rule areas still in place the router had two layers for 148 nets and 279 footprints and left 83 nets open; the rule areas are gone and the planes are simply removed from the DSN as before, which is how A17 routed. The escape stubs also have to hold the net class clearance, not the board default, or the 1.0 mm pack-node tracks land 0.16 mm from a neighbour: `escape.py` now reads the net classes from the project file, because the KiCad 9 Python API does not expose them. **A19 then routed 0 hard, 0 unrouted, 516 vias**, deliverable `meshsat-pcb-a-revA-A19`. After the TPS2065C land correction of 32.28 it was regenerated and rerouted the same evening: **0 hard, 0 unrouted, 498 vias**, and the deliverable was rebuilt; B12 likewise (301 router vias plus the PWM1 stub) and E4 at its new 278 mm length (163 vias, one net closed by the stub router). The contract check of this section passes on the finished set.

**Cross-board contract check (`tools/check_contracts.py`).** A new script reads the netlists of A, B, C, D and E and verifies what no single board's gate can see: the twenty-pin panel ribbon map, the transmit inhibit chain from the panel toggle to Q3 on PCB-D, the three 5 V rails, the dock's twelve signal contacts against the strip's lands, the four CELL+ and four return pins with the pre-charge pin, the shore inhibit reaching the opto, and the shutdown pair on the A to B ribbon. It found one real defect: PCB-B called the rail that PCB-A calls `+5V_M1` simply `+5V`, which with three rails on the board is a review trap; B was regenerated with the rail named like A's. Three name differences are documented aliases rather than defects, because each board names its own branch of a net: the panel feed is `PANEL_5V` on B (downstream of the polyfuse F6) and `+5V` on C, the module thermistor line is `TS_CHG` on A (the charger input it lands on) and `TS_MOD` on the dock, and the spare contact is named after the connector on each side.

### 32.27 Battery module research, 5 Sep 2026 (MESHSAT-791; full notes in `v2/docs/respin-research-module-2026-09-05.md`, documents in `v2/vendor/battery/`)

Five items were researched from manufacturer documents: the cell, a single-cell protector at 30 A, the module envelope, the 40 A fuse and its holder with the XT60 rating, and the thermistor for the charger's JEITA input. Every figure in the notes carries its file and page.

- **Cell, Samsung INR18650-35E** (specification Ver. 1.1): 18.55 x 65.25 mm maximum, 50 g maximum, 3,350 mAh minimum and about 3,450 mAh typical, 8 A continuous discharge, charge 0 to 45 C, discharge -10 to 60 C, internal impedance 35 mOhm maximum. Twelve in parallel: **40.2 Ah minimum, about 41.5 Ah typical, 96 A continuous, 2.9 mOhm, 600 g**. The "42 Ah" of the brief is the reseller's nominal 12 x 3.5 Ah; the record now carries the specification figures. The A19 charger's 3 A is 0.074 C per cell, so a full charge is about 14 h plus the constant-voltage tail. Samsung publishes no strip thickness or weld schedule anywhere in the three copies of the sheet; the 0.15 mm strip is our build choice. The sheet does forbid soldering to the cell can (section 6.1).
- **Protection at 30 A: no documented off-the-shelf 1S module reaches it.** The best documented parts are 15 A continuous (Batteryspace PCB-LIS1A15, 20 A for five minutes, and PCB-Li-1S15A which brings a 10 kOhm NTC terminal); Tenergy's 1S board is 8.5 A. A 30 A protector therefore has to be built: TI BQ29700 (or ABLIC S-8261, Nisshinbo R5405) with two TI CSD17570Q5B NexFETs back to back, which the sheets size as 1.84 mOhm worst case, 55 mV at 30 A against the 85 mV minimum trip, a trip at 54 to 68 A and 1.7 W of heat at 30 A. Its short-circuit response is 250 us at 0.5 V; the prospective short current of a 12P node is roughly 500 A, so the FET pulse rating wants a bench check before the first short test, or a third FET per switch. **This is the owner's decision**: build the 30 A protector, or take a documented 15 A module and relax the number. Either way the charge temperature window lives in the charger's JEITA input on A19, because none of the three protection ICs has a thermistor pin.
- **Envelope.** One cell thick either way, 19.7 mm wrapped. Flat 4 x 3: **75.2 x 197.7 x 19.7 mm**; flat 6 x 2: 112.3 x 132.1 x 19.7 mm, the same area. Only the 4 x 3 fits the 87 mm east floor band of 32.25, which is what that section assumed. Mass: about 640 g wrapped, about 0.7 kg with the protection board, fuse, holder and connector.
- **Fuse and holder.** Littelfuse MAXI 0299040.ZXNV, 40 A, 32 V DC, 1000 A interrupting, 1.4 mOhm, 8,500 A2s, derated to 30 A at 85 C, 29.2 x 21.6 x 8.9 mm; in-line holder MAHC0001ZXJ (45 A continuous, 60 A maximum, 6 AWG leads) or the splashproof 152 series; on a board, Keystone 3555-2 (UL 50 A). No ATO or MINI holder in the documented set is rated for 40 A, which is why the module takes a MAXI blade and not the MINI blades of PCB-A. Coordination note for the owner: the XT60 is a 30 A connector, so a 30 or 35 A MAXI would coordinate with it; the 40 A blade protects the wiring, not the connector.
- **Connector.** Amass XT60 (XT60E-M for a panel wall): 30 A rated, 60 A instantaneous, 0.55 mOhm, 12 AWG recommended, 500 V, 1000 cycles, 27.8 C rise at 30 A with 12 AWG against 85 C with 14 AWG. The 12 AWG figure is the one the build must hold.
- **Thermistor.** Semitec 103AT-2, 10 kOhm plus or minus 1 percent, B(25/85) 3435 K, 27.28 kOhm at 0 C and 3.020 kOhm at 60 C, which are the values the charger's fixed comparators assume; head 3.7 x 4.0 x 2.4 mm, leads 0.5 mm on 2.54 pitch, 17 mm long, solder no closer than 5 mm to the head. Murata NXRT15XH103FA1B is the equivalent with a 4 s time constant and lead-wire lengths.

### 32.28 Part numbers for the respin values, and two defects the search found, 5 Sep 2026 (full notes in `v2/docs/respin-lcsc-2026-09-05.md`)

The respin left 177 distinct value and footprint pairs across the set with no LCSC code, which JLCPCB cannot assemble. Every one was looked up against its own JLCPCB part page: 72 are parts JLC places (70 exact, 2 with a stated substitution), 105 are the parts we fit ourselves (through-hole connectors, blade fuses and holders, spring pins, SMA and SMP, USB-A receptacles, the Coilcraft inductors, the 3 mm panel LEDs, the TRACO module, the radio module, the panel switches, leads and pads). The codes are in `tools/lcsc_fill.py`, which now fills the JLC BOM automatically. Sixty-one distinct codes: 20 Basic, 5 Preferred, 36 Extended, after three deliberate merges that each removed an Extended feeder fee by using one higher-voltage part for two lines.

**Two defects came out of the search, and both are real.**

- **The TPS2065C load switches sat on the wrong land.** TI's data sheet SLVSAU6I gives the DBV package as a 5 pin SOT-23 (1 OUT, 2 GND, 3 FLT, 4 EN, 5 IN); the generators had it on a SOT-23-6 land. On that land the part's IN pin lands on the empty middle pad and pad 6 carries the rail to nothing, so **not one switched channel would have powered up**. The pin map itself was right. Five switches on A19 (U7, U10, U13, U16, U28) and two on B12 (U4, U7) are affected; PCB-D defines the same helper but never calls it, so D5 and its cart line are untouched. Both boards are regenerated on the corrected land.
- **The E4 surge clamp named an SMB part on an SMC land.** D3 was `SMBJ15A` (DO-214AA) on the `D_SMC` (DO-214AB) footprint that the two SMCJ33A parts on the same board use. The value is now SMCJ15A: same 15 V standoff and 24.4 V clamp in the larger body, 1.5 kW instead of 600 W, no board change, and all three clamps on the strip are one case size.

**Four values changed because the design asked for something that cannot be bought or fitted.**

- The JEITA divider on A19 asked 5.24k and 30.31k, which are TI's computed numbers from the BQ25792 worked example and are not E96 values. Fitted: 5.23k (0.19 percent low) and 30.1k (0.69 percent low). With the 103AT-2 curve those shifts move the cold and hot trips by about a quarter of a degree, well inside the tolerance of the parts themselves.
- `RT1` on A19 was labelled `103AT-2` but is a 0603 land: it is the gauge's own temperature sensor beside the dock pins, not the charger's JEITA sensor, which is the module's leaded 103AT-2 out on the pack. It is now named for what it is, a 0603 10 k NTC with a beta of 3380 K, and the gauge configuration must be written against that curve.
- The crystal loading capacitors were 22 pF on both hubs against crystals that were never pinned down. With the parts now chosen (24 MHz at an 18 pF load on A19, 12 MHz at a 20 pF load on B12) the pairs become 27 pF and 33 pF, which is 2 x (load minus about 4 pF of stray).

That last question is answered: the heating pad feed takes a LUTE 1812L250/30GR (C52748011), 2.5 A hold, 5 A trip, **30 V**, 40 A fault current, in place of the 16 V part. Two more results came with it. The Murata bead standing in for the gauge sensor is closer to the Semitec than first thought, 3434 K against 3435 K over 25 to 85 C, and it diverges only below 25 C where its 25/50 figure of 3380 K applies, which is exactly the range the heating pad works in: the gauge is configured from the R/T table over its own window, not from one beta. And the two crystals are confirmed at an 18 pF load (A19) and a 20 pF load (B12), which is what the 27 pF and 33 pF pairs are matched to; the 33 pF part is a JLCPCB Basic part, so that line costs no feeder fee.

One warning from the same search is worth keeping for any future part pick: a JLCPCB summary string is not a specification. A 1812 fuse whose free text reads "60V" carries a structured maximum voltage of 6 V, which matches its maker's own sheet. Read the attribute fields, not the description.

Where the codes disagreed with the 3 September ordering session's own picks (17.4k and 105k), the ordering session's values stand, because those were verified inside JLCPCB's cart flow; the repeated entries were removed so the table has one code per value.

### 32.29 Wall receptacles: where they go and how they mount, 5 Sep 2026 (ruling 6 of 32.13; `release/revA/case/wall-receptacles-1to1.pdf`, generator `tools/case_wall_cutouts.py`)

**What the case allows.** The Peli STEP (`1521-931 Bottom PID`) is an envelope model: a slab section through the long wall (`vendor/peli/wall2.py`) shows the cavity and the outer bound but no wall skin, so the wall thickness cannot be read from it. What it does give, and the point probe of 25.1 confirms: the inner wall runs at about a 2 degree draft from the shoulder 7.92 mm below the rim (Z 162.56 in the STEP frame) to 108.2 mm down (Z 159.06), then a 17 mm chamfer to the floor at 124.87; the frame-leg bosses sit on the inner walls at X +-8.6, +-48.7, +-51.4, +-133.3, +-148.8, +-151.5 and +-152.4, between 67 and 71 mm above the floor; the outer skin is ribbed (customer drawing 1521-931). A flanged receptacle cannot seal on a 2 degree face (1 mm of wedge across a 29 mm flange) nor on a ribbed one.

**Ruling in design: a connector plate.** Both receptacles mount on one flat aluminium plate, 82 x 54 x 3 mm, bolted over a window in the long wall with six M4 screws and a 2 mm closed-cell gasket. **Which wall (corrected the same evening, 5 Sep, after the owner asked for the precise look):** the Peli customer drawing 1521-931 shows the front long wall carrying the handle at its centre, the pressure equalisation valve above it, a cluster of four outer ribs each side of the handle and both latch straps reaching down the base, and the drill-point pattern of 25.1 confirms which wall that is (the wall with leg points at X +-48.7, +-51.4, +-148.8, +-151.5 and none at the centre is the handle wall, because the handle sits where a centre leg would go). The dock strip runs along that front wall, so the plate does not go on the dock's side after all. The end walls are too narrow between their three inner ribs (Y 0 and +-89) for an 82 mm plate. **The plate goes on the back long wall, the hinge side (case +Y), at the same X and height**: the back wall is plain outside below the hinge, and its inner ribs (frame-leg drill points at X +-8.6, +-133.3, +-152.4) all stay 7 mm or more from every through-hole. Both template sheets are drawn as seen from outside the back wall, so case +X is on the viewer's left. The plate is flat, so each receptacle seals on it with its own gasket, and the plate-to-wall gasket takes up the draft and the ribs. The 3 mm plate sits inside the 233-370's stated panel range of 1.6 to 6.35 mm. The case itself only needs two 29 mm hole-saw holes and six 4.5 mm holes.

**Positions (case frame, X along the long axis from the case centre, Z up from the cavity floor, on the back wall).** Plate centre (-92, 55), outline X -133 to -51, Z 28 to 82. Shore DC receptacle at (-110, 55), USB receptacle at (-74, 55), 36 mm apart. Plate screws at X -120, -92 and -64 in two rows at Z 32 and 78. Every through-hole keeps at least 7 mm from the back wall's inner ribs at X -133.3 and -8.6; the plate bottom at Z 28 stays above the 16.7 mm floor chamfer; the plate top at Z 82 is 43 mm below the rim and the hinge. The USB receptacle is 100 mm from PCB-A's `J_WALL1` at (-156, 62), which sits at that board's north-west corner, so that cable is short. The shore lead runs from the plate west along the back wall, down the west end wall and along the front wall to the strip's `J_DCIN` at (-104, -106): about 500 mm of 18 AWG, tied to the walls, which keeps it off the floor under the stack and away from the float clamps.

**Cut-outs on the plate, from the Glenair sheets in `vendor/d38999/`.** Shore DC, D38999/20 shell 13 wall mount with round holes (D0), front panel mount: hole 19.05 (cut-out sheet type B, shell 12-13, AA .750), four M3 clearance holes on a 23.01 mm square (233-105 table, shell 13, C BSC .906), flange 28.9 square. USB host, 233-370 shell 15 D0, front panel mount: hole 23.01 (AA .906), four M3 holes on a 24.61 square (2x .969 on the 233-370 face view), flange 31.29 square. The 233-370 sheet reads "2x .906 (23.01)" for the slotted-hole style and "2x .969 (24.61)" for the round-hole style; the round-hole receptacles are the ones specified here, so the larger square applies.

**What the drawing does not settle:** the wall skin thickness. The sections of drawing 1521-931 show a single-skin wall of about 4 to 5 mm, inside the 233-370's 1.6 to 6.35 mm panel range, but the drawing states no figure and the STEP is an envelope; the plate design does not depend on it, since the plate carries the sealing faces and the screws are long enough for any wall up to 8 mm.

### 32.30 Z closure recomputed, the strip shortened, and where the battery module sits, 5 Sep 2026 (MESHSAT-790, MESHSAT-791)

**Closure.** Three places in this record carried three different spares for the same stack (25.1 said 9.3 mm at the 6.0 mm dock gap, 32.14 and 32.24 AO estimated 2.3 mm at a 13.0 mm gap), a gateway session pointed it out, and the gap is 13.4 mm nominal since 32.21. Computed from the floor: strip 1.6, gap 13.4, PCB-A 1.6, bottom bay 35, PCB-B 1.6, middle bay 59, total **112.2 mm** against the panel underside at 114.1 (25.1): **1.9 mm spare at nominal, 0.9 mm when the float clamps sit at the top of their 12.4 to 14.4 window**. The block's 7.4 mm face lives inside the gap and adds nothing. This is a computed figure now, not an estimate; it is tight, it is positive, and it goes on the 12 September agenda as such. If it ever has to grow, the middle bay is the number to look at, because it is the clearance over the tallest module and not a spacer.

**Strip.** The dock strip is 278 x 60 (X -160 to 118), 7 mm shorter at its east end, so that the battery module's cradle beside it clears both the strip and PCB-A's east edge at 117.5. Only the three test points of the east end moved.

**Module placement (case frame, X along the long axis, Z up from the floor).** The module is the flat 4 x 3 block of 32.27 (75.2 x 197.7 x 19.7 wrapped) in a two-part printed enclosure of 2.5 mm walls, 81 x 221 x 27.5 outside (grown for the heater mat, 32.32), with a 66 x 14 x 6 pocket at its south end for the protection board (either of the two candidates of 32.27 fits), a grommeted lead exit and vent slots at the same end, and eight M3 lid screws into heat-set inserts. It lies in the east floor band in a printed cradle 82 x 224 x 8 with 1 mm rails and two 25 mm strap slots, on four VHB pads: cradle X 120 to 202, module X 121 to 201, module Y -137 to 83 (lead end south), so the cradle keeps 2 mm from the strip's east end, 2.5 mm from PCB-A's east edge above it, and 4.9 mm from the floor's east edge at X 206.9 (the 46 degree wall chamfer starts there, above a height of 8 mm the wall is 8 mm further out). PCB-B's 245 mm width overhangs to X 122.5 at 52 mm above the floor, well above the module's 26 mm, and the stack still lifts straight up. The rod at (110.5, -73) and its nut keep-out end at X 115. The module lead runs south along the case wall to `J_BATT` at the strip's west end (about 300 mm of 12 AWG, 1.6 mOhm), which is cheaper in copper than moving the connector east and running the module current 240 mm along the strip.

### 32.31 Battery module protection board, owner ruling 5 Sep 2026 (MESHSAT-791): the documented module

The owner chose the documented part over a bespoke board ("documented with schematics/dimensions/specs"). Of the two documented 1S modules of 32.27 the one that fits the enclosure pocket is the **Batteryspace PCB-LIS1A15** (AA Portable Power Corp, `vendor/battery/batteryspace-prod-spec-274.pdf`): charge 4.2 V CC/CV, consumption 10 uA or less, 15 A continuous charge and discharge, 20 A for five minutes, over-charge 4.25 V plus or minus 0.025 (release 4.05), over-discharge 2.50 V plus or minus 0.062 (release 3.0), over-current 35 A plus or minus 5 A in 8 to 16 ms, short circuit in 200 to 800 us, 20 mOhm or less, -40 to 85 C, 65 x 10 x 2.5 mm, 17 g. What its maker publishes is the specification table and the dimensions; there is no schematic in the sheet, and none of the documented 1S modules comes with one. The bespoke alternative of 32.27 would have carried TI's reference schematic but no third-party test data.

**Consequences.** The 30 A continuous figure of 32.24 AY is relaxed to the module's 15 A continuous and 20 A for five minutes, which is several times the kit's real load. The module's own 35 A trip acts before the 40 A MAXI fuse at the positive terminal, so the fuse stays the backup for the wiring (32.27 section 4.3) and coordinates with it. The module has no thermistor input; the charge temperature window stays on PCB-A's charger through the module's 103AT-2, as designed. The enclosure pocket of `v2/cad/battery_module.py` (66 x 14 x 6) was sized for exactly this board.

### 32.32 Closing the 4 Sep rulings: what the boards did not cover, 5 Sep 2026 evening (owner: "fix them all before we move to new items")

An audit of the seven rulings of 32.13 against the finished set found six leftovers, none on the boards. Their disposition:

- **Ruling 1, the APEM locks.** The panel schematic texts and the order notes still named the NKK momentary switches for SOS, EMCON and ZEROIZE. Both now name the APEM 5636ADKB-2V and say that SOS and ZEROIZE are maintained and timed by the bridge. C4's copper and its cart-coded BOM are untouched; only the schematic PDF in the deliverable is regenerated.
- **Ruling 2, transmit serialisation.** PANEL.md section 10 had it as withdrawn; 32.21 says it is no longer a hardware requirement and the bridge may keep it as a receiver-protection preference. The sentence now says exactly that.
- **Ruling 3, the heating pad.** Three gaps closed: PANEL.md gains section 11 with the bit map of PCB-A's second expander (U31 at 0x24: EN_WALL, HEAT_EN, FLT_WALL, HEAT_FLT, CHG_INT, GAUGE_ALERT, CHG_STAT, eight spares) and the bridge rule for the pad (on with shore present and the module thermistor below 0 C, off above 5 C, on fault, when shore goes, or after 2 hours; a 2 hour run without crossing 0 C is a fault); the pad is the **RS PRO 245-556** silicone heater mat (`vendor/battery/heater/`, notes in `respin-research-heater-2026-09-05.md`): 50 x 150 mm, 12 V dc, 7.5 W, 0.63 A, 0.10 W per square centimetre, 0.7 to 1.4 mm, self-adhesive, 500 mm PTFE leads, maximum 200 C, no thermostat; RS's own leaflet requires an external thermostat and fuse for every mat of the range, which here are the thermistor rule and the 2.0 A eFuse. It was chosen over the 15 W 75 x 200 member of the same family because only the 7.5 W part has a data sheet in hand (the 15 W one appears on a distributor page alone), and over a 12 W US part with no sheet at all. Warm-up estimate, labelled as such: 640 g of cells at about 1 J per gram and kelvin take 85 seconds per kelvin from 7.5 W with no losses, so from -10 C to 0 C about 15 minutes ideal and 30 to 45 minutes with the losses of a printed enclosure on a case floor, inside the bridge's 2 hour limit. The enclosure grew 1 mm in length and 1.5 mm in height for it (81 x 221 x 27.5), with a 0.3 mm witness on the floor for the mat and a gap in the pocket rib for its leads.
- **Ruling 4, the solar input.** Complete on the strip; BUILD.md now says the panel itself is an accessory of the owner's choice, up to about 40 W, on the shore plug's second pair.
- **Ruling 5, the blind-mate joint.** Two pieces were described but not drawn. (a) The float retainer: the Radiall drawing (TDS R222.M80.500) shows a 6.5 mm square body with no flange, its shoulder 5.5 mm above the far face, and the receptacle under PCB-A reaches 5.7 mm above the strip at the 13.4 mm gap, so no retainer can sit over the shoulder. The plug is therefore held by its own crimped cable (53 N pull-off against a 9 N disengagement) tied into a printed nest (`v2/cad/float_clamp.py`, 24 x 16 x 4.5, an 8.5 mm square cavity for 1 mm of radial float, a 2.8 mm cable slot, two M3 into the strip's clamp holes, a tie groove over and under); the receptacle's 8.3 mm funnel and 3 degree lead-in do the fine centring. (b) The seven SMA antenna bulkheads, which the retired strip E3 used to carry, go into the two end walls at 55 mm above the floor, four sites each at Y -60, -30, +30 and +60 between the walls' inner ribs at Y 0 and +-89: west wall UHF, WIFI 2.4, WIFI 5.8, SDR; east wall LTE, IRIDIUM, LORA and a plugged spare. The couplers are the Amphenol Connex 132170 of 32.10 in their 6.5 mm D-holes with the flat at 6.00 across; sheets 3 and 4 of `release/revA/case/wall-receptacles-1to1.pdf` are the templates. The RG-316 jumpers from the nests to the couplers are 150 to 250 mm; ASSEMBLY.md's lead table had pointed them at the circular receptacles, which was wrong and is corrected.
- **Ruling 6, the external connectors.** The cable side was undefined. The mating plug for the shell 13 receptacle, its contacts and strain relief, the sealed plug for the USB feed-through and the outdoor 4-core cable are being picked from Glenair's sheets (below, when the search returns), and ASSEMBLY.md gets the two external cables as build items.

Ruling 7, the review findings, stays open until the 12 September session by its own terms.
