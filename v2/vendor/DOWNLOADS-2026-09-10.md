# Datasheets fetched 10 September 2026 (MESHSAT-862)

The knowledge base over this folder (`v2/ecad/tools/kb/`) was asked which parts the schematic
generators instantiate and which of them this tree holds no document for. It named 47 entries,
collapsing to 26 distinct documents. Twenty six were fetched; one is owed and is listed at the end.

Provenance matters more than usual here, because two of these did not come from the manufacturer's
own server, and a document's authority is exactly the thing a reader needs to judge. Every file below
was opened after download and its first page read: the table records what that page says it is.

| Part on our boards | Filed as | Source |
|---|---|---|
| TMUXHS4212 | `ti/ti-tmuxhs4212.pdf` | ti.com/lit/ds/symlink/tmuxhs4212.pdf |
| TPS2065CDBV | `ti/ti-tps2065-tps2066-tps2067.pdf` | ti.com/lit/ds/symlink/tps2065.pdf |
| TCAN334D | `ti/ti-tcan334-can-fd-transceiver.pdf` | ti.com/lit/ds/symlink/tcan334.pdf |
| TLV9062IDGK | `ti/ti-tlv9062-op-amp.pdf` | ti.com/lit/ds/symlink/tlv9062.pdf |
| TMP117AIDRVR | `ti/ti-tmp117-temperature.pdf` | ti.com/lit/ds/symlink/tmp117.pdf |
| TPS22810 | `ti/ti-tps22810-load-switch.pdf` | ti.com/lit/ds/symlink/tps22810.pdf |
| INA219AIDCN | `ti/ti-ina219.pdf` | ti.com/lit/ds/symlink/ina219.pdf |
| PCA9555PW | `ti/ti-pca9555.pdf` | ti.com/lit/ds/symlink/pca9555.pdf |
| TS3USB221A | `ti/ti-ts3usb221a.pdf` | ti.com/lit/ds/symlink/ts3usb221a.pdf |
| TUSB8041 | `ti/ti-tusb8041-usb3-hub.pdf` | ti.com/lit/ds/symlink/tusb8041.pdf |
| TPS259571 | `power/ti-tps2595-efuse.pdf` | ti.com/lit/ds/symlink/tps2595.pdf (the TPS2595xx family sheet) |
| TLV75533PDBV | `power/ti-tlv755p-ldo.pdf` | ti.com/lit/ds/symlink/tlv755p.pdf |
| AO3401A | `power/aos-ao3401a-p-mosfet.pdf` | aosmd.com/res/data_sheets/AO3401A.pdf |
| IRF7404 | `power/infineon-irf7404-p-mosfet.pdf` | infineon.com/dgdl/irf7404pbf.pdf |
| SRF1260-4R7Y | `power/bourns-srf1260-common-mode-choke.pdf` | bourns.com/docs/product-datasheets/srf1260.pdf |
| AP2112K-2.5 and -3.3 | `diodes/diodes-ap2112-ldo.pdf` | diodes.com/assets/Datasheets/AP2112.pdf |
| AP63203WU-7, AP63205WU-7 | `diodes/diodes-ap63200-series-buck.pdf` | diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf |
| STM32H753VITx | `st/st-stm32h753xi-datasheet.pdf` | **Wayback Machine copy** of st.com/resource/en/datasheet/stm32h753vi.pdf |
| STM32H743VIT6 (the part bought, C114409) | `st/st-stm32h743xi-datasheet.pdf` | **Wayback Machine copy** of st.com/resource/en/datasheet/stm32h743vi.pdf |
| SMBJ18A, SMBJ20A | `vishay/vishay-smbj-series-tvs.pdf` | vishay.com/docs/88392/smbj.pdf |
| SMCJ18A, SMCJ33A | `vishay/vishay-smcj-series-tvs.pdf` | vishay.com/docs/88394/smcj.pdf |
| SKY13351-378LF | `rf/skyworks-sky13351-378lf-spdt.pdf` | skyworksinc.com, SKY13351_378LF_201132I.pdf |
| GCT SIM8060 | `connectors/gct-sim8060-nano-sim-socket.pdf` | gct.co/files/drawings/sim8060.pdf |
| Amphenol RJHSE5380 | `connectors/amphenol-rjhse5380-rj45-jack.pdf` | **Mouser's mirror** of Amphenol's `io_modjack_rjhse` sheet |
| XAL4020-222ME, -472ME, XAL4030-472ME | `coilcraft/coilcraft-xal40xx-series.pdf` | coilcraft.com, xal4000.pdf |
| XAL6060-332ME, -472ME | `coilcraft/coilcraft-xal60xx-series.pdf` | coilcraft.com, xal60xx.pdf |
| W25Q16JVUXIQ | `winbond/winbond-w25q16jv-serial-flash.pdf` | winbond.com resource file, W25Q16JV rev H |

## The two that are not from the manufacturer's own server, and why

**st.com refuses this host outright** (connection refused from both the runner and the rented box,
already recorded in section 7 of the handover). The Wayback Machine's stored copy was used, the same
route section 8 records for the Geekworm wiki. Both files open as STMicroelectronics documents with
the manufacturer's own metadata. **cs.amphenol.com refuses the connection too**, and Amphenol's own
CDN answered 403, so the RJHSE sheet is Mouser's mirror of Amphenol's `io_modjack_rjhse` document.
If either is ever used to settle a number that matters, re-fetch it from the vendor on a host that
can reach them and compare.

## The Quectel RM520N-GL, found on 11 September 2026

It was the one document owed, because quectel.com publishes module documents through a request form
and the first search returned only third-party document mirrors, none of them the manufacturer. A
second look found better sources, and all three files below are Quectel's own: their PDF metadata
carries Quectel authorship (`kingson.zhang@QUECTEL.COM`, and two Quectel names) and they are the
original Word and PowerPoint exports, not re-prints.

| Document | Filed as | Source |
|---|---|---|
| RM520N-GL Hardware Design v1.0, 2022-07-15, Released, 85 pages | `quectel/quectel-rm520n-gl-hardware-design-v1.0.pdf` | **forums.quectel.com**, which is Quectel's own domain |
| RM520N Series Hardware Design v1.1, 2023-03-16, Released, 98 pages | `quectel/quectel-rm520n-series-hardware-design-v1.1.pdf` | TI's E2E forum, hosting Quectel's own file |
| RM520N-GL 5G Specification, the two-page product brief | `quectel/quectel-rm520n-gl-5g-specification-brief.pdf` | a distributor's copy of Quectel's brief |

**Read v1.1 first: it supersedes v1.0** and covers the series rather than the one variant. v1.0 is
kept because it is the copy from Quectel's own server, so the two together settle any question of
whether a mirrored file was altered.

The B design assumes this module (a 6 September ruling records it as assumed, with the pick and the
antenna count still owed), and its M.2 B-key pinout, its supply current and its antenna count are
decided from these documents.

## What confirming a package looks like now

Section 8 of the handover carries the trap: a footprint key is a claim about a package and nobody
checks it, and `TPS2065CDBV` sat on a SOT-23-6 land for four board phases. Its sheet is now in the
tree, and its ordering table settles it in one line: `TPS2061DBVR ... SOT-23 (DBV) | 5`. The rule
that a package is confirmed from the same datasheet page can now actually be followed for this part.
