# Second WiFi radio of the V2 kit (kit-to-kit link), documents

Owner rulings of 5 September 2026 (appendix 32.35): the wireless CM5 keeps the operator hotspot on its own radio; a second 2x2 radio of the Alfa AWUS036ACM's driver family (Linux mt76) carries the kit-to-kit link without an access point (the V1 kits run it as IBSS with a fixed BSSID, `meshsat-p2p-link.service` in the bridge repo). No embeddable MT7612U module exists with a datasheet, so the second radio is a PCIe card on the CM5's lane.

| File | Source | What it is |
|---|---|---|
| `linux-mt76x2-usb-device-table.c` | torvalds/linux master, `drivers/net/wireless/mediatek/mt76/mt76x2/usb.c` | the MT7612U device list: consumer sticks (Alfa AWUS036ACM on MediaTek's reference ID 0e8d:7612) and OEM modules with non-standard connectors only |
| `asiarf-AW7915-AED-datasheet.pdf` | asiarf.com | M.2 A/E-key, MediaTek MT7915DAN + MT7975D, 2T2R dual band dual concurrent (573 + 1201 Mbps), PCIe 2.1, 2 x IPEX, 52 x 30 mm, 3.3 V, average 4 to 8 W, maximum 9 W (supply design 3.3 V at 3 A, 2.5 A minimum), -10 to +70 C, USD 24 (5 Sep 2026) |
| `asiarf-AW7915-NPD-2X-datasheet.pdf` | asiarf.com | the same chip on mini PCIe, 2 x MMCX, 50.95 x 30 mm, FCC and CE stated (IDs on request), USD 28 |
| `asiarf-AW7915-NP1-datasheet.pdf` | asiarf.com | mini PCIe 4T4R (MT7915AN), 4 x IPEX, FCC ID TKZAW7915NP1, IC 9968A-AW7915NP1, USD 30 |
| `asiarf-AW7916-AED-datasheet.pdf` | asiarf.com | M.2 A/E-key WiFi 6E (MT7916AN), 3 x IPEX, maximum 10 W, USD 29.90; its mini PCIe sibling AW7916-NPD carries FCC ID TKZAW7916-NPD |
| `asiarf-AW7915-AE1-datasheet.pdf` | asiarf.com | M.2 A/E-key 4T4R; the maker states no mass production plan, MOQ 500: not a pick |

Driver facts checked in the kernel sources on 5 September 2026 (`mt7915/init.c`, `mt76x02_util.c`, `mt7615/init.c`, `mt7921/main.c`): the mt7915 driver (MT7915, MT7916, MT7981, MT7986) advertises ADHOC, AP, MESH_POINT and STATION interface types, as do mt76x2 (MT7612) and mt7615; the mt7921 driver (MT7921, MT7922, the AMD RZ608/RZ616 cards) offers STATION, AP and P2P only, so those cards cannot run the kit-to-kit ad-hoc link.

Compute Module 5 side (CM5 datasheet 2.3): one PCIe Gen 2 x1 lane, 100 MHz clock out, `PCIe_nRST` output, `PCIe_CLK_nREQ` input, `PCIE_PWR_EN` output, `PCIE_nWAKE` unsupported in software, AC coupling capacitors on the module's TX pair (the card carries its own on its TX), 90 ohm pairs. The CM5IO's M.2 socket and its PCIe power supply (CM5IO datasheet figure 6) are the reference for the socket power on the carrier.

Published as-is for reference; the makers hold the rights, takedown on request.
