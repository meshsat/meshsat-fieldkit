# PicoAPRS V4, manufacturer documents

The APRS transceiver of the V1 kits since the owner ruling of 8 September 2026 (MESHSAT-748), replacing the
Quansheng UV-K5(8) plus AIOC chain and the NiceRF DMR858M that had been planned for it.

| File | What it is |
|---|---|
| `picoaprs-v4-user-manual-wimo-2023-11-20.pdf` | the manufacturer's user manual, "PicoAPRS V4 Engineered by Taner Schenker DB1NTO Usermanual", WiMo Antennen und Elektronik GmbH, dated 20 November 2023, as published at wimo.com |
| `picoaprs-v4-user-manual-text.txt` | the same manual as text (`pdftotext -layout`), so a grep finds a figure without opening the PDF |

The figures the kit design uses are in the design record (`v2/docs/MESHSAT-709-geometry-appendix.md`, the section
of 8 September 2026): TX 144.000 to 146.000 MHz on the EU market at a maximum of 1 watt, RX 136.000 to 174.000 MHz
from firmware V13, FM/AFSK at 1200 baud AX.25, a KISS TNC over the USB-C virtual COM port at 115200 baud as well as
over TCP on WiFi, Bluetooth Classic and BLE, 5.0 V and at most 500 mA at the USB port, a 3.7 V 850 mAh removable
Li-Ion battery, a built-in GPS receiver, approximately 35 x 67 x 25 mm and about 60 grams, an operating range of
-10 C to +45 C, an SMA antenna socket, and no protection against water.

These are third-party documents, republished here unmodified so the build record stands on its own sources.
Rights remain with their authors. If you hold the rights and would rather they were not here, ask and they go.
