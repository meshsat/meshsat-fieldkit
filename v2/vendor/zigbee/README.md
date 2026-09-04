# Zigbee coordinator documents

Documents behind the Zigbee side of the compute-module respin study (MESHSAT-709, appendix 32.35, `docs/respin-research-cm5-2026-09-04.md`): a coordinator module on the carrier instead of a USB dongle, with the firmware and the host-side settings that would drive it. Fetched 4 September 2026. The licence remark of the parent folder applies; the Sonoff readme comes from ITEAD's firmware repository and the Zigbee2MQTT page from the project's documentation. Nothing here has been built.

A note on the E180-ZG120B: it is often listed as an EFR32MG21 module, but Ebyte's own specification (second row) gives the SoC as the EFR32MG1B232F256GM32, a Series 1 part. The Sonoff Dongle-E (fourth row) is an EFR32MG21 design, so its NCP image does not apply to the E180 as it stands; the module choice needs a second look before any of this is drawn.

| File | Source | Date | What it is used for |
|---|---|---|---|
| `ebyte-e72-2g4m20s1e-user-manual.pdf` | https://www.cdebyte.com/pdf-down.aspx?id=770 | 4 Sep 2026 | the TI CC2652P 20 dBm module: pinout, UART and debug pins, RF figures, footprint; the Z-Stack coordinator candidate |
| `ebyte-e180-zg120b-product-specification-cdebyte-id3309.pdf` | https://www.cdebyte.com/pdf-down.aspx?id=3309 (the "Manual" entry on the E180-ZG120B downloads tab, https://www.cdebyte.com/products/E180-ZG120B/4) | 4 Sep 2026 | the E180-ZG120A/B product specification: the EFR32MG1B SoC with a 20 dBm PA, size and pin definition, RF figures |
| `ebyte-e180-zg120-user-manual-software-cdebyte-id1921.pdf` | https://www.cdebyte.com/pdf-down.aspx?id=1921 (the "E180-ZG120series_Software_Datasheet_EN" entry on the same tab) | 4 Sep 2026 (V1.0) | the user manual of Ebyte's own ad hoc network firmware (AT and HEX command modes); relevant only if the module keeps the factory firmware rather than an NCP image |
| `sonoff-dongle-e-ncp-readme.md` | https://raw.githubusercontent.com/itead/Sonoff_Zigbee_Dongle_Firmware/master/Dongle-E/NCP/README.md | 4 Sep 2026 | the Silicon Labs EmberZNet NCP coordinator firmware of the Dongle-E (EFR32MG21) with the standard EZSP interface: the model for what an on-carrier Silicon Labs module runs and how the host talks to it |
| `zigbee2mqtt-adapter-settings.md` | https://www.zigbee2mqtt.io/guide/configuration/adapter-settings.html (text extract of the page) | 4 Sep 2026 | the serial section of Zigbee2MQTT's configuration.yaml: port, adapter type, baud rate and flow control, which a carrier-mounted coordinator on a UART has to satisfy |
