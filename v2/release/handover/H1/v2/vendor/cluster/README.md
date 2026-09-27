# Three-module carrier documents

Documents behind the three-CM5 cluster carrier study (appendix 32.35, `docs/respin-research-cm5-2026-09-04.md`). Fetched 4 September 2026. Nothing here has been built.

| File | Source | What it is used for |
|---|---|---|
| `ksz9897.pdf` | Microchip DS00002330E | the 7-port Gigabit switch with five integrated PHYs (the pick), straps, rails, thermal |
| `ksz9893.pdf` | Microchip DS00002420 | the 3-port sibling, too small for three modules (comparison) |
| `ksz989x-hw-design-checklist.pdf` | Microchip DS00004151A | page 12: transformer-less PHY-to-PHY links through 0.1 uF capacitors |
| `an6048-daisy-chain-ksz.pdf` | Microchip AN6048 | cascading KSZ switches |
| `ts3usb221.pdf`, `ts3usb3031.pdf` | Texas Instruments SCDS220M, SCDS348D | USB 2.0 1:2 and 1:3 muxes for the shared LTE and SDR |
| `tca9548a.pdf` | Texas Instruments SCPS207H | the I2C switch (downstream fan-out; not the master selector) |
| `tmux1308.pdf` | Texas Instruments SCDS426E (March 2020, revised October 2022), https://www.ti.com/lit/ds/symlink/tmux1308.pdf; 4 Sep 2026 | the 8:1 analogue mux for UART, SPI, I2S and I2C lines |
| `pca9615.pdf` | NXP PCA9615 Rev. 2 (16 September 2021), https://www.nxp.com/docs/en/data-sheet/PCA9615.pdf through the Wayback Machine (2023 snapshot; the live link returns 404 to the runner); 4 Sep 2026 | differential I2C over a cable or a long backplane run |
| `computeblade-datasheet.pdf` | Uptime Lab, February 2024 | a CM4 blade with PoE, no switch on the carrier |
| `super4c.html` | DeskPi wiki | the four-CM5 board without a switch: per-module bucks, staggered start, ESP32 supervisor, INA3221 monitors |
| `super4c.md` | https://wiki.deskpi.com/super4c/ (text extract of the wiki page, 4 Sep 2026) | the same page as text, for grepping the pin tables and the power figures |
| `k3s-requirements.md` | https://docs.k3s.io/installation/requirements (text extract of the page, 4 Sep 2026) | the k3s node minimums (CPU, RAM, disk, ports, kernel) that size the cluster's modules |
| `geerling-nanocluster.html`, `geerling-cm5.html` | Jeff Geerling, 2025 and 2024 | measured power and thermal behaviour of CM5 clusters |
