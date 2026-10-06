# MeshSat enclosure v0.6: LilyGO T-Beam Supreme + RockBLOCK 9704-SMA

**Status: cleared for PROTOTYPE printing. Not a final production release.**
See `AUDIT-RESPONSE.md` for how each audit finding (F01 to F15) was handled and what remains open.

Envelope (body + lid): **62.5 × 146.0 × 62.7 mm**; 154.0 mm long including the SOS guard.
With the MOLLE plate: 69.6 × 160.0 × 71.7 mm.

## Print in this order
| Step | File(s) | Material | Purpose / pass criterion |
|---|---|---|---|
| 1 | `coupons/meshsat-coupon_rails.stl` | PETG or ASA | The real 9704 PCB slides in with no flexing and no wobble. Otherwise change `rb_slot` (1.80) in the .scad. |
| 2 | `coupons/meshsat-coupon_rimlid.stl` | ASA | Inserts set flush; M3×8 screws close the lid onto the rim without bottoming; cord seats in the groove. |
| 3 | `coupons/meshsat-coupon_board.stl` + `print-stl/meshsat-separator.stl` + `print-stl/meshsat-lid.stl` | PLA ok | Real Supreme + 18650 seat on the separator. Lid closes without force. Buttons line up. OLED is centred in the window. |
| 4 | full set in `print-stl/` | PLA/PETG | Full prototype: assembly, wiring, dunk test |
| 5 | full set in `print-stl/` | **ASA** (orange) + TPU 95A | Only after steps 1 to 4 pass and the open items are closed |

| Part | Material | Orientation (already exported this way) | Notes |
|---|---|---|---|
| meshsat-body | ASA | open side up | 5 perimeters, ≥40 % infill; horizontal port holes may sag slightly, so deburr |
| meshsat-lid | ASA | outer face down | groove, pane pocket and hold-downs face up |
| meshsat-separator | ASA | flat underside down | 100 % infill |
| meshsat-membrane | TPU 95A | flange down, caps up | slow (20 to 30 mm/s) |
| meshsat-plungers ×3 | ASA/PETG | head down | |
| meshsat-retainer | ASA | flat | |
| meshsat-molle / -belt | ASA | body face down | tunnel roofs are 26.5 / 40 mm bridges: enable bridge settings or supports |

## Hardware
- **Lid:** 8× M3×8 socket head + 8× M3 heat-set inserts for a 4.0 mm hole, ≤ 5.7 mm long (pocket depth 7.0)
- **Carry plate:** 4× M3 heat-set inserts (same type) + 4× M3×8 countersunk
- **Button retainer:** 6× M2×6 self-tapping
- **9704 lock:** 2× M3×16 self-tapping, from above into the rail ends, after the board is slid in (fit before the separator)
- **Seal:** 2.0 mm silicone O-ring cord, ~450 mm. Groove 2.7 × 1.5 mm (77.6 % fill, 25 % squeeze). Join the ends with cyanoacrylate.
- **Foam:** 1.5 mm closed-cell foam: 1 strip ~15 × 70 under the 18650 holder, 4 pads 1.3 × 4 on the lid hold-downs (each compressed to 1.0 mm)
- **Window:** polycarbonate 24.0 × 38.0 × 2.0 mm (pocket 24.6 × 38.6 × 2.2), bonded with a neutral-cure silicone. Acetoxy (vinegar-smelling) silicone can craze polycarbonate.
- **Panel parts** (exact SKUs still open; check their cut-outs against the .scad):
  - 2× SMA female bulkhead pigtails with O-ring, Ø6.6 holes
  - IP67 panel USB-C, Ø16.2 hole; designed for a nut up to 20 mm across
  - M12 ePTFE vent, Ø12.3 hole on the right wall
  - 12 mm IP67 momentary switch, Ø12.2 hole, ≤ 20 mm deep behind the panel
- **Antennas:** Ground Control helical Iridium antenna (49 × 19 mm, SMA-M) + 868 MHz LoRa whip

## Assembly notes
1. RockBLOCK goes **component side down**. Slide it along the rails from the USB end until it hits the stop, then fit the two M3×16 lock screws.
2. Solder the harness wires directly to the 9704 header pins. There is ~3.9 mm under the pin tips, so Dupont housings won't fit. Anchor the bundle (adhesive tie mount in the free lower-bay area, y ≈ 25 to 55) so the solder joints carry no strain.
3. Fit the separator, then the foam strip, then the Supreme. Seat the PCB edges in the lips.
4. Fit the button membrane, plungers and retainer (6× M2×6) before closing.
5. Close the lid with even torque until it touches the rim. The rim is the hard stop, so don't overtighten.

## Electrical: open decisions (not designed here)
- **9704 power (F12):** Ground Control requires a battery supply to stay within 3.6 to 4.5 V on V_BATT. An 18650 drops below 3.6 V well before empty. Options:
  - (a) a 5 V boost converter feeding **V_IN+** (pin 15, 4.0 to 5.3 V, 500 mA); the lower bay has free space for one, y ≈ 22 to 56
  - (b) direct V_BATT with a firmware cutoff at about 3.7 V, accepting shorter runtime
  
  Use I_EN/I_BTD for start-up and shutdown. Connect all four 9704 grounds. Don't use the 9704's USB and header at the same time.
- **Co-location (F13):** Ground Control's installation page says the 9704-SMA Iridium certification assumes **no other transmitter in the same housing**, the qualified helical antenna with ≤ 0.5 dB feed loss, and the antenna ≥ 1 m above ground or metal. This design puts LoRa/BLE/WiFi in the same housing and adds a pigtail and bulkhead. **Get Ground Control's written position before a final build.**

## Rebuild and verify
`bash validation/build_and_check.sh` (OpenSCAD 2021.01+, Python: trimesh, numpy, scipy, manifold3d) regenerates every STL and reruns these checks:
- self-checks
- the clash check against the manufacturers' STEP meshes
- the mesh/printability report, including SHA-256 hashes

Results for this release are in `validation/build/`.

## Sources
- LilyGO T-Beam Supreme board STEP, DXF, schematic V3.1 and shell STLs: github.com/Xinyuan-LilyGO/LilyGo-LoRa-Series, commit 5e2da3f. © LilyGO; included for reference only.
- RockBLOCK 9704-SMA (2A) STEP, mount STEP + drawing, Maxtena antenna STEP: docs.groundcontrol.com/iot/rockblock-9704/hardware. © Ground Control; included for reference only.
- `reference-cad/meshes/*.stl` are tessellations of those STEP files, used for the assembly view and the clash check.
