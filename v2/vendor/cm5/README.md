# Raspberry Pi Compute Module 5 documents

Official Raspberry Pi documents behind the compute-module respin (appendix 32.35, `docs/respin-research-cm5-2026-09-04.md`). Fetched 4 September 2026 from datasheets.raspberrypi.com, pip.raspberrypi.com and the raspberrypi/documentation repository. Nothing here has been built: the CM5 carrier is a design in progress.

| File | Source | What it is used for |
|---|---|---|
| `cm5-datasheet.pdf` | https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf (release 3, 8 June 2026) | the two 100-pin connectors and their signal list, power, sequencing, routing rules, thermal and mechanical figures |
| `cm5-product-brief.pdf` | https://datasheets.raspberrypi.com/cm5/cm5-product-brief.pdf | variants and list prices |
| `cm5io-datasheet.pdf`, `cm5io-product-brief.pdf` | https://datasheets.raspberrypi.com/cm5/ | the official carrier: connector placement, USB current limit, display ports, jumpers |
| `cm5io-kicad.zip` | https://pip.raspberrypi.com/documents/RP-008099-DD (CM5 IO Board revision 2 design files) | the carrier-side connector footprint, the four-layer stackup, the net classes and the BOM of the reference carrier |
| `cm5-antenna-kit-product-brief.pdf` | https://pip.raspberrypi.com/documents/RP-008179-DS | the certified external antenna (valid for CM4 and CM5) |
| `rpi5-product-brief.pdf` | https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf | the Pi 5 figures for comparison |
| `doc-*.adoc` | https://github.com/raspberrypi/documentation (computers/compute-module and accessories/touch-display-2) | eMMC flashing, peripheral software guide, display connection on a Compute Module |
| `amphenol-10164227-bergstak-0.40mm-product-sheet.pdf` | Amphenol Communications Solutions, BergStak 0.40 mm product sheet, LCSC-hosted copy https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2411201534_Amphenol-ICC-10164227-1001A1RLF_C6782225.pdf (amphenol-cs.com refuses the runner with 403 and the Wayback Machine holds no copy); 4 Sep 2026 | the connector's 0.40 mm pitch, the 1.5 mm (10164227-xx01) and 4.0 mm (10164227-xx04, so the 10164227-1004A1RLF of the carrier) stack heights, the 10164228 mating header series and the durability figure of 30 cycles, which the Raspberry Pi documents omit |

The CM5 IO Board design files are published by Raspberry Pi Ltd for reuse in carrier designs; the footprints of the two connectors (`meshsat.pretty/CM5_Conn_A_10164227.kicad_mod` and `CM5_Conn_B_10164227.kicad_mod`, one part per receptacle so the assembler places two; `CM5_Amphenol_10164227.kicad_mod` is the whole-site reference they were cut from) are derived from them.
