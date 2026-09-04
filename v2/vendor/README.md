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
| `x1202/` | Geekworm X1202 V1.1 PCB DXF and the wiki page as archived by the Wayback Machine on 9 May 2026 (the live wiki refuses non-browser clients), plus an overview photo | the Pi 5 / X1202 stack envelope on PCB-B: 96 x 85 with the Pi flush on one long edge and 39 mm of board past the GPIO-header edge, which B10 did not allow for (B11) |
| `rf/` | Radiall SMP-MAX R222M00720 receptacle and R222M80500 right-angle plug data sheets (the blind-mate pair, 32.21); Amphenol Connex 132170 SMA bulkhead female-female adapter drawing (rev D, the E2 D-hole: 6.50 with the flat at 6.00 across, panel 2 to 6.5 mm); Rosenberger 19S102-40ML5 SMP data sheet; Radiall SMP-MAX series catalogue (R222M) and the R222.M40.050 adapter data sheet | the Rev B blind-mate RF joint between the dock and PCB-A (MESHSAT-775) |
| `power/` | TI BQ25798 and BQ25792 charger, BQ34Z100-G1 gauge (and the MAX17048 fallback), TPS61288 boost, TPS2596 eFuse, LTC2954 push-button controller, ADI LT8705A buck-boost controller, Coilcraft XAL1010 and XAL1510 inductors, RALEC shunt, Panasonic low-profile capacitors | the A19 power tree and the dock tracker stage (design record 32.21) |
| `d38999/` | Glenair D38999/20 and /26 sheets, panel cut-outs, pin selection, environmental overview, the 233-370 USB feed-through; Amphenol Series III catalogue for the insert chart and contact ratings | the shore DC and USB host wall connectors (rulings 6 and G, 32.21) |
| `keystone/` | Keystone catalogue page with the 3568 and 3549-2 mini blade holders; Littelfuse 297 blade dimensions | the fuse holder heights on the dock strip (32.18, 32.21) |
| `usb2517/` | Microchip USB2517/USB2517i data sheet (LCSC-hosted copy) | the seven-port hub on A19 (ruling G) |
| `switches/` | C&K ATP19 and ATP16 anti-vandal pushbutton data sheets (ordering codes, panel holes 19.2 and 16.2); NKK M series miniature toggle data sheet (circuits, levers, bushings) and the NKK accessories and hardware catalogue (boots, nuts, guards) | the PCB-C panel controls named in `ASSEMBLY.md` section 9 |
| `precidip/` | Preci-Dip spring-loaded connector catalogue, pages 31 (general specifications) and 34 (813 series, 2.54 mm double row, solder tail, heights 6 to 7.5 mm) | the `J_DOCK` pin set on PCB-A (813-S1-008-10-016101) |
| `aioc/` | AIOC (All-In-One-Cable) KiCad sources and schematic, its own `LICENSE.md` applies | the CM108 audio path on PCB-D |
| `dmr858/` | NiceRF DMR858M and DMR858S datasheets and mechanical drawing, the vendor pages as saved | the APRS module on PCB-D |
| `probes/` | our own STEP probe scripts (build123d), kept with the models they read | reproducing the numbers in the appendix |

The files are ordinary git objects (the largest is about 50 MB).
