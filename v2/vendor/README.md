# Vendor reference material

Third-party CAD models, drawings and datasheets that the V2 design was measured against. They are here so the generators and the appendix can be checked against the same files years from now. **They are not covered by this repository's licence.** Each file belongs to its manufacturer under that manufacturer's terms and is kept here as reference material for the design record. If you hold the rights to one of these files and want it removed, open an issue and it goes.

| Folder | Source | Used for |
|---|---|---|
| `peli/1520/`, `peli/1400/` | Peli Products customer drawings, STEP, DXF and Parasolid of the 1520EU and 1400EU cases and their PF panel frames (downloaded by the owner from peli.com); `proj.py`, `sect.py` are our probes | case cavity, frame ledge and hole pattern, panel outline (appendix section 25) |
| `td2/` | Raspberry Pi Touch Display 2 (7 inch) STEP model and the product-brief editions from raspberrypi.com | the display aperture and tape band on PCB-C |
| `weact/` | WeAct Studio e-paper module, 3.7 inch files only, see `weact/README.md` | the recessed e-paper window and ring on PCB-C |
| `rockblock/` | Ground Control RockBLOCK 9704 STEP, SMA drawing and schematic; RockBLOCK 9603 STEP | the modem bays on PCB-B |
| `tbeam/` | LilyGO T-Beam 1W shell and PCB models, drawing | the LoRa carrier on PCB-B |
| `limesdr/` | LimeSDR Mini 2.4 drawings and STEP | reserved bay, Rev B option |
| `wio/` | Seeed Wio-SX1262 STEP | LoRa module footprint |
| `tcall/` | LilyGO T-Call A7670 dimension drawing `T-Call-A7670-ESP32.dxf` and `T-Call-A767X-ESP32.png` (from `Xinyuan-LilyGO/LilyGo-Modem-Series`, `dimensions/esp32`): the source of the 74.78 x 29.01 outline and the four Ø3 holes on 69.46 x 24.97. `T-A7670X-Board-3D.stp` is LilyGO's model of the **T-A7670X** (the 18650-holder board, SIM7000G form factor), not the T-Call; it sat under a T-Call name until 3 Sep 2026 and stays only so the record remains reproducible | the cellular carrier on PCB-B |
| `traco/` | TRACO TEN 40WIN datasheet | the shore-power converter on PCB-E1 |
| `rpi5/` | Raspberry Pi 5 mechanical drawing and product brief (datasheets.raspberrypi.com) | the Pi 5 / X1202 stack pattern on PCB-B (58 x 49, Ø2.7, 3.5 mm from the edges) |
| `rf/` | Rosenberger 19S102-40ML5 SMP data sheet; Radiall SMP-MAX series catalogue (R222M) and the R222.M40.050 adapter data sheet | the Rev B blind-mate RF joint between the dock and PCB-A (MESHSAT-775) |
| `aioc/` | AIOC (All-In-One-Cable) KiCad sources and schematic, its own `LICENSE.md` applies | the CM108 audio path on PCB-D |
| `dmr858/` | NiceRF DMR858M and DMR858S datasheets and mechanical drawing, the vendor pages as saved | the APRS module on PCB-D |
| `probes/` | our own STEP probe scripts (build123d), kept with the models they read | reproducing the numbers in the appendix |

The files are ordinary git objects (the largest is about 50 MB).
