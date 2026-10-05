# v0.6 response to the 5 Oct 2026 audit of v0.5

**Release status: cleared for PROTOTYPE printing (coupons, then one full prototype).
Not a final production release.** Items marked OPEN need physical parts, tests or
a vendor decision that CAD cannot supply.

All evidence below is reproducible with `bash validation/build_and_check.sh`.
Results are stored in `validation/build/`.

## What changed in method
- Both boards are now registered from the manufacturers' STEP files (tessellated in
  `reference-cad/meshes/`), not simplified ghosts. Transforms are echoed by the .scad
  (`PART="reg"`) and used by `validation/clash_check.py`.
- Clash check intersects every printed part, in assembled position, with every STEP
  body (non-watertight 9704 bodies replaced by their convex hulls, i.e. conservative).
  **Positive control:** lowering the Supreme 3 mm produces 40.3 mm³ of clash with the
  separator, so the check does detect real interference.
- Self-checks exported from the .scad must come back empty: open groove, rear and
  top insert bores, lid/body overlap. The rail-lip check must come back non-empty.

## Closure matrix

| ID | Finding | v0.6 action | Evidence | Status |
|---|---|---|---|---|
| F01 | Lid groove enclosed, lid/body overlap | Edge treatments clipped to 0..h; top edge is a 2.5 mm 45° chamfer; `assert` on profile | `chk_groove` and `chk_lid_body` empty; lid is 1 body | **Closed (CAD)** |
| F02 | Hold-downs hit board; roof clash; PCB 1.0 not 1.6 | PCB 1.0 mm. Cavity height = PCB underside + 10.81 (tallest STEP part) + 1.5. Seats and lid bosses moved to the only regions bare on both faces: 1.3 mm edge strips, board-y 5.7 to 39.7. Bosses sit directly over seats. Foam pads give defined compression; the lid closing on the rim is the hard stop. SMA-end stops sit below the STEP overhang; USB-end stops sit beyond 100.95 mm. Battery holder rests on 1.5 mm foam with loose saddles; the PCB lips are the datum. | Clash = 0.000 mm³ vs Supreme STEP for every part | **Closed vs STEP.** OPEN: holder not in STEP (from LilyGO shell); real-board dry fit |
| F03 | Rails had zero engagement, no lock | Rails now have 1.2 mm lips over each PCB edge, 0.3 mm side clearance, a lead-in, and an M3 lock screw per rail behind the board. Edge bands checked bare in the 9704 STEP (top ≤ 1.57, bottom ≥ −0.08). | `chk_rail_lip` = 190 mm³ engaged; clash 0.000 vs 9704 STEP | **Closed (CAD)**. OPEN: slot height 1.80 to be tuned on `coupon_rails` |
| F04 | Rear bores refilled by pillars | All bores cut after the full union; depth 7.0 | `chk_rearbores` and `chk_topbores` empty | **Closed (CAD)**. OPEN: insert SKU and pull-out |
| F05 | Screw stacks | Lid M3×8 (5.7 mm reach into a 7.0 mm pocket); retainer M2×6 (tip 2.0 mm inside the 5 mm wall); plate M3×8 countersunk (5.0 mm reach); 9704 lock M3×16 self-tapping | Arithmetic in README | **Closed (nominal)**. OPEN: coupon verification |
| F06 | Fit-check floated / misleading | Replaced by three grounded coupons: `rimlid` (seal, inserts, screws), `board` (upper bay with ledges, button holes and LoRa bulkhead, to take the separator, a real Supreme and the lid), `rails` (9704 slot fit) | Every coupon: no floating bodies | **Closed** |
| F07 | 96 % gland fill | 2.0 mm cord in a 2.7 × 1.5 mm groove: 77.6 % fill, 25 % squeeze. The rim land is the compression stop. | Calculation | **Closed (nominal)**. OPEN: leak test |
| F08 | Buttons misregistered, unsealed, untestable | Positions from STEP actuator faces (50.72 / 59.02 / 74.65 mm, 1.75 below the PCB). Split into a TPU membrane (prints flat), three rigid guided plungers (0.3 mm gap at rest, so no preload, and a 0.65 mm hard stop) and a 3 mm retainer with 6× M2. Flange compressed 0.3 mm, with the wall face as the stop. | Clash 0 vs STEP; plunger tip vs actuator face = 0.30 mm | **Closed (CAD)**. OPEN: force/travel, cycling, ingress |
| F09 | Unsupported features | Bed-facing fillets changed to 45° chamfers. SOS guard has a ≥45° gusset and a teardrop bore. Separator ribs moved to the top, so the underside is flat. Membrane, plungers and retainer orientations are printable. Carry plates are exported body-face down. | `mesh_report`: no floating bodies. Remaining >45° area is holes, slot ceilings and counterbores. | **Partly open:** MOLLE (26.5 mm) and belt (40 mm) tunnel roofs are bridges. Use bridge settings or supports. |
| F10 | Pane pocket had no allowance | 0.3 mm/side XY clearance, 0.2 mm bond line, exact 2.0 mm PC pane, 3.5 mm bezel overlap | none | **Closed (nominal)**. OPEN: adhesive choice and test |
| F11 | Panel hardware placeholders | USB-C hole moved so a 20 mm nut clears the corner pillar, with a notch in the separator. Vent moved to the right wall, because a 16 mm nut no longer fitted beside the USB on the end wall. Nut envelopes clash-checked. | Envelope checks = 0 | **OPEN:** exact SKUs and cut-outs |
| F12 | VBAT range | Not solved in CAD. Ground Control's installation page states battery supply must stay within 3.6 to 4.5 V. Options in the README. | none | **OPEN** |
| F13 | Co-located transmitters | Confirmed on Ground Control's installation page: Iridium certification of the 9704-SMA assumes no other transmitter in the same housing, the qualified helical antenna with ≤ 0.5 dB cable loss, and the antenna ≥ 1 m above ground or metal. This design has LoRa/BLE/WiFi in the same housing and adds a pigtail plus bulkhead. | none | **OPEN: vendor decision needed before a final build** |
| F14 | No qualification evidence | Test sequence in the README | none | **OPEN** |
| F15 | Metadata / hygiene | Header v0.6; envelope 62.5 × 146.0 × 62.71 mm (154.0 mm long including the SOS guard); MOLLE width 69.6; SHA-256 per STL in `mesh_report.json` | 4 zero-area triangles remain in the lid (removing them would open the mesh) | **Closed** except that cosmetic note |
