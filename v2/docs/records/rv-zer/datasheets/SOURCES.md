# Documents fetched for the ZEROIZE feasibility study (MESHSAT-1357, 26 September 2026)

Fetched on 2026-09-26 between 14:20 and 14:35 CEST from the runner. Microchip's own hosts (`www.microchip.com`,
`ww1.microchip.com`) and `trustedcomputinggroup.org` answered HTTP 403 to the runner, and `nxp.com` answered 404 for
the direct links, so those files are the Internet Archive's byte copies of the vendor URL (the `id_` form, no archive
banner). Every file below is a vendor or standards-body publication; none is an NDA document. Where a vendor
publishes a document only under NDA (the full ATECC608A and ATECC608B data sheets), nothing was fetched from any
third-party mirror.

| File | Publisher, document, revision | Original URL | How fetched | sha256 |
|---|---|---|---|---|
| `microchip-atecc508a-complete-20005927A.pdf` | Microchip, ATECC508A CryptoAuthentication Device Complete Data Sheet, DS20005927A (2017, PDF ModDate 2017-12-18), 109 pp. | http://ww1.microchip.com/downloads/en/DeviceDoc/20005927A.pdf | Wayback capture 20190618060547 | `3e79484ff38cde1980159af097487ea336774016d4e64965b0ba666bb8d66bc0` |
| `microchip-atecc608a-40001977A.pdf` | Microchip, ATECC608A Data Sheet SUMMARY, DS40001977A (2017), 28 pp. Fetched to check whether Microchip ever released the full ATECC608A data sheet publicly at this number: it did not; the footer reads "Datasheet Summary" | http://ww1.microchip.com/downloads/en/DeviceDoc/40001977A.pdf | Wayback capture 20260301151407 | `3e971d6d284ebc64fc81d168788b9abd32da81a90ce1e0bb56037b0ca16a4a26` |
| `microchip-atecc608b-tngtls-DS40002250.pdf` | Microchip, ATECC608B-TNGTLS CryptoAuthentication Data Sheet, DS40002250B (2020-2023, PDF ModDate 2023-04-11), 56 pp. | https://ww1.microchip.com/downloads/aemDocuments/documents/SCBU/ProductDocuments/DataSheets/ATECC608B-TNGTLS-CryptoAuthentication-Data-Sheet-DS40002250.pdf | Wayback capture 20230519035216 | `db25050e016b887c578795e79c0ece0532dc176c5ef3ef4fb2f46b3eae0127b5` |
| `microchip-atecc608b-tflxtls-DS40002249.pdf` | Microchip, ATECC608B-TFLXTLS CryptoAuthentication Data Sheet, DS40002249B (PDF ModDate 2023-04-12), 63 pp. | https://ww1.microchip.com/downloads/aemDocuments/documents/SCBU/ProductDocuments/DataSheets/ATECC608B-TFLXTLS-CryptoAuthentication-Data-DS40002249.pdf | Wayback capture 20230803212920 | `b4601f1c2dc395af532d556010ace8b19ca792368d4cda8bfc960a6d3018646d` |
| `microchip-dm320118-users-guide-DS50002921A.pdf` | Microchip, DM320118 CryptoAuth Trust Platform User's Guide, DS50002921A (2019) | http://ww1.microchip.com/downloads/en/DeviceDoc/CryptoAuth-Trust-Platform-Users-Guide-DS50002921A.pdf | Wayback capture 20240510124055 | `6951ca754fad1f9e78c9f63a5f788fe183e21ca01b5358f10ee4cfa6001df3b1` |
| `infineon-slb9673-fw26-datasheet-rev1.4.pdf` | Infineon, OPTIGA TPM SLB9673 TPM 2.0 FW26.xx Datasheet, Revision 1.4, 2024-11-13, 49 pp. | https://www.infineon.com/dgdl/Infineon-SLB9673-TPM20-I2C_FW26xx_DS_Rev1-4-2024-11-13-DataSheet-v01_00-EN.pdf?fileId=8ac78c8c93dda25b01944055dd2c5d11 | direct, HTTP 200 | `0750aaaba4f59ef5208c97af10b89bc616dd69a075ebda0225b57109b9d24001` |
| `nxp-se050-datasheet.pdf` | NXP, SE050 Plug & Trust Secure Element product data sheet, Rev. 3.8, 18 October 2023, 30 pp. | https://www.nxp.com/docs/en/data-sheet/SE050-DATASHEET.pdf?pspll=1 | Wayback capture 20260313115240 | `b47c8a5d40191f31b78e48f6c60c6ba17c3eac56bf97976212ade786ee3ee83c` |
| `nxp-an12413-se050-apdu.pdf` | NXP, AN12413 SE050 APDU Specification, Rev. 2.12, 24 March 2021, 138 pp. | https://www.nxp.com/docs/en/application-note/AN12413.pdf | Wayback capture 20260916110513 | `e98a72e4215ba2886d777509f066ff620925ae65999d9c28cbcf24b7f2cf5622` |
| `tcg-tpm2-r1p59-part1-architecture.pdf` | Trusted Computing Group, TPM Library Family 2.0, Level 00 Revision 01.59, Part 1: Architecture, 8 November 2019 | https://trustedcomputinggroup.org/wp-content/uploads/TCG_TPM2_r1p59_Part1_Architecture_pub.pdf | Wayback capture 20260904023834 | `18e393ef8f61d4c5deebb578cc4220b025fdaff2c28a7e3264f16e37796c3d9b` |
| `tcg-tpm2-r1p59-part3-commands.pdf` | Trusted Computing Group, TPM Library Family 2.0, Level 00 Revision 01.59, Part 3: Commands, 8 November 2019 | https://trustedcomputinggroup.org/wp-content/uploads/TCG_TPM2_r1p59_Part3_Commands_pub.pdf | Wayback capture 20260428182655 | `d2e5e7187574d383b00ff966c33b30a96e3f5165cbfae20a4d094e5794f3b9bb` |

Already in the tree and re-read, not re-fetched: `v2/vendor/microchip/microchip-atecc608b-datasheet.pdf` (ATECC608B
Summary Data Sheet DS40002239A, sha256 `519e2edac0deefe1755a98e30b8ce2a5a2ff9b9c39acda333bb625b87bdac3ff`, as
`v2/vendor/SOURCES.yaml` records it), `v2/vendor/rp2040/rpi-rp2040-datasheet.pdf` (build-version 3184e62, sha256
`be56fbb75ba0ae9e26558a73c93ac3e75c2ad4e6878d3b6703de2a76d886ea8c`) and
`v2/vendor/winbond/winbond-w25q16jv-serial-flash.pdf` (Revision H, sha256
`81af3f69b0bff95fd1097949a1005431dc5b3a6ecb5f1947e695a17298e7cf1b`).

Source code read (public repositories, cloned read-only into the session scratchpad, not vendored):

| Repository | Commit | Used for |
|---|---|---|
| github.com/MicrochipTech/cryptoauthlib | `d49c7d578efb09d4a498d5ab86839d4c17812f15` (Release v3.8.0, 2026-05-14) | command modes, ATECC608 execution times, default I2C configuration, the ATECC608 test configuration and the tests that run GenKey and ECDH on a data-locked device |
| github.com/wolfSSL/wolfTPM | `0f639565564b91e86eff7b4dff877128e1a48f59` (2026-09-24) | which TPM stack supports the SLB9673 over I2C, its licence and its HAL model |
| github.com/raspberrypi/pico-sdk | `079c6f39023649b154152db30f1d781e884879bc` (tag 2.3.1, "SDK 2.3.1 Release", 2026-09-04) | the I2C calls with and without a timeout, the controller reset in `i2c_init`, the flash-programming interrupt rule, interrupt priorities and the watchdog's reset scope (ZEROIZE.md 3.4, E20, E22). Five files fetched raw from raw.githubusercontent.com at that commit on 2026-09-26T14:38Z, not cloned: `src/rp2_common/hardware_i2c/i2c.c` sha256 `62aa67cd0b687e7ed39b56a88343939535e11dbf55602d995787f0466e881673`, `src/rp2_common/hardware_i2c/include/hardware/i2c.h` `ba330ff219f3844a05479ec30101ba5640773b04c990c00032e8b160359a558a`, `src/rp2_common/hardware_flash/include/hardware/flash.h` `34bcc266f4535e6cbb57a289c5cb6d92583926fd6f6882ad5032598872523d19`, `src/rp2_common/hardware_irq/include/hardware/irq.h` `85fabc3046de2b00f979b87a8c8b226e2515470466bda524b29af21bb4dff526`, `src/rp2_common/hardware_watchdog/watchdog.c` `e7052da8894a7f125b0f6a5abad3298c9a0d4fc4967b678099eedd160241c727` |

Catalogue reads (`../prices/`): the JLCPCB public component search the tree's own `v2/ecad/tools/jlc_certify.py:66`
uses, asked on 2026-09-26T12:27:48Z for `ATECC608B-SSHDA-T`, `SLB9673`, `SLB9672`, `SE050C2HQ1` and `SE050E2HQ1`; the
raw responses are kept. `initialPrice` is read as the unit price at the smallest quantity tier, which is an inference
from the field name.

Filing note for the integrator: the vendor data sheets belong under `v2/vendor/{microchip,infineon,nxp}/` with
`sources.txt`, `vendor-status.txt` and `SOURCES.yaml` lines, as the tree files every other vendor PDF. The two TCG
specifications (7.6 MB together) are cited by URL, revision and sha256 in `v2/docs/feasibility/ZEROIZE.md`; whether
to vendor them is the integrator's call.
