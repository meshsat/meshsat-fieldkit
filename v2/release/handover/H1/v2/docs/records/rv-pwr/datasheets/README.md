# Documents fetched by stream PWR on 26 September 2026 (for filing under v2/vendor/ by the integrator)

| File | URL | Revision | sha256 |
|---|---|---|---|
| asiarf-AW7915-AED_V1.pdf | https://asiarf.com/wp-content/uploads/2023/09/AW7915-AED_V1.pdf | v1.0, 2023-08-17 | af1a93ef3b484a3da4354779f0b2a8a2537c94d71025eb68b82a4d4879f8e8db |
| asiarf-aw7915-aed-product-page.html | https://asiarf.com/product/wifi-6-11ax-m-2-ae-key-module-aw7915-aed/ | as served 26 Sep 2026 | b153fe713673d0f6df7936038333096e8fc14842609d90e8d8b1e7694c120846 |
| limesdr-mini-v2-introduction.html | https://myriadrf.org/projects/limesdr-mini-2-0 | docs v2.4, last updated 8 Jun 2026 | f1146105a3c09ebcf786d217fbf0053f8e6df3c5192efcf666e731281be4c4f1 |
| limesdr-mini-v2-user-setup.html | https://myriadrf.org/projects/limesdr-mini-2-0/user/setup.html | docs v2.4, last updated 8 Jun 2026 | 87b2e5605196b5c5f48e9175991c63143152dbb694d6f4faeba85d6cdaeca3b3 |
| advantech-sqflash-720-d-m2-2242-v1.9.pdf | https://advdownload.advantech.com/productfile/Downloadfile2/1-2MDTFS2/Advantech%20SQFlash_PCIe%20NVMe%20M.2%202242_M%20Key_720-D-DS_v1.9_20240709.pdf | Rev 1.9, 2024-07-09 | 4176a46e8474f74102cf139b4fd61dea45f2f46c7062d1ddb786732c2107b7ba |
| cervoz-m2-2242-nvme-titan.pdf | https://www.cervoz.com/products/download/8r0k7y0bWdEw/Cervoz_Industrial_Embedded_Module_M.pdf | T405 datasheet Rev 2.0 | 30b3c59cd3332952f91eb825cd6bb9ebcbea3281fca4bd6a3277ddd03ce032b9 |
| sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf | https://www.sunon.com/en/MANAGE/Docs/PRODUCT/286/360/Sunon%20DC%20Brushless%20Fan%20&%20Blower_(240-A).pdf | catalogue 240-A; PDF pages 18 and 40 extracted with pdfseparate and pdfunite | extract fae7e21365939be5c3bbf156be3522b364037a637590f5079538d63456bca63b; full original bd47c70496d8ee47585ece647c9f7202966f52439d1b48265bf9b4f3031cec80 (not kept, 8.4 MB) |
| xenarc-709gnk-product-page.html | https://www.xenarc.com/709GNK.html | as served 26 Sep 2026 | dc32f6556d6ddc398064e3a15eec0c600937b2235138cbd10e0ed344d708bf93 |

An attempt at ADATA's IM2P32A4 2242 datasheet (industrial-ad.adata.com) failed on the host's certificate chain and was
not retried with verification disabled, so no ADATA figure is used.

Added in the second cycle (26 September 2026):

| File | URL | Revision | sha256 |
|---|---|---|---|
| ti-bq4050-trm-sluuaq3a.pdf | https://www.ti.com/lit/ug/sluuaq3/sluuaq3.pdf | BQ4050 Technical Reference Manual, SLUUAQ3A, April 2016, revised October 2022 | 525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad |

Used for: section 2.5 (two independent overcurrent-in-discharge protections, OCD1 and OCD2) and sections 14.9.6 to
14.9.8 (each with a threshold in mA and a delay of 0 to 255 s; defaults -6000 mA / 6 s and -8000 mA / 3 s). The
datasheet SLUSC67B in the tree (`v2/vendor/battery/ti-bq4050.pdf`) points to this manual for every protection detail
(section 7.3.1) but the manual itself was not in the tree.

Added in the third cycle (26 September 2026):

| File | URL | Revision | sha256 |
|---|---|---|---|
| keystone-m65-p42-mini-fuse-holders.pdf | https://www.keyelco.com/userAssets/file/M65p42.pdf | Keystone catalogue M65, page 42 ("Mini" automotive fuse clips and holders; PDF created 26 Jun 2015) | caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395 |

Used for: the Keystone 3568 mini blade holder that carries the three 25 A blades of the pack path
(`pcb_energy_chain.yaml` lines 58, 111 and 143). The page sets one specification block between the low-profile
3557-2 and the 3568 holders: UL current rating 30 A at 500 V AC, UL temperature rating -50 to +145 C. That the block
covers the 3568 is read from the page's layout (INFERRED). The tree holds pages 39 to 41, 43 and 44 of the same
catalogue under `v2/vendor/battery/keystone/`, not this one.

The BQ4050 manual above is used in this cycle also for: 3.5 and 14.10.4 (Safety Overcurrent in Discharge, a
permanent failure, default -10000 mA for 5 s), 14.2.5.1 (Enabled PF A, default 0x00), 5.2 (NORMAL mode: readings
every 250 ms, status decisions at 1 s intervals) and 14.9.8 (OCD recovery, default +200 mA for 5 s).
