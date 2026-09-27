# Audio codec and APRS sound-path documents

Documents behind the sound path of the compute-module respin study (MESHSAT-709, appendix 32.35, `docs/respin-research-cm5-2026-09-04.md`): an I2S codec on the module's PCM pins weighed against the CM108 USB codec that PCB-D uses, with Direwolf as the consumer of either. Fetched 4 September 2026. The licence remark of the parent folder applies. Nothing here has been built.

| File | Source | Date | What it is used for |
|---|---|---|---|
| `rpi-RP-009699-WP-1-using-the-i2s-peripherals-on-raspberry-pi-sbcs.pdf` | https://pip-assets.raspberrypi.com/categories/1259-audio-camera-and-display/documents/RP-009699-WP-1-Using%20the%20I2S%20peripherals%20on%20Raspberry%20Pi%20SBCs.pdf | 4 Sep 2026 (build 20 February 2026) | the Raspberry Pi white paper: the I2S/PCM interface on the 40-pin header, clocking, device-tree overlays and driver setup for an external codec |
| `cirrus-wm8960-datasheet-rev4.4.pdf` | https://statics.cirrus.com/pubs/proDatasheet/WM8960_v4.4.pdf through the Wayback Machine (snapshot of 8 March 2021; statics.cirrus.com refuses the runner with 403) | 4 Sep 2026 (Rev 4.4) | the stereo codec with class-D speaker drivers: I2S and I2C interfaces, microphone bias, register map, package, the on-carrier codec candidate |
| `waveshare-wm8960-audio-hat-wiki.md` | https://www.waveshare.com/wiki/WM8960_Audio_HAT (text extract of the wiki page) | 4 Sep 2026 | a working WM8960 wiring on a Raspberry Pi: header pins, overlay and driver installation, ALSA controls; the page links the HAT schematic and user manual |
| `direwolf-user-guide-1.8.pdf` | https://github.com/wb2osz/direwolf/raw/master/doc/User-Guide.pdf | 4 Sep 2026 (version 1.8, October 2025) | the software TNC: sound-device and PTT configuration (GPIO, CM108 GPIO, serial), the audio-level requirements the codec has to meet |
| `cmedia-cm108b-datasheet-v1.41.pdf` | https://www.cmedia.com.tw/storage/upload/sync_file/E02-0045%20CM108B_Datasheet_v1.41.pdf | 4 Sep 2026 (v1.41) | the USB codec of PCB-D's audio path (the AIOC design in `../aioc/`): the GPIO pins used for PTT, the audio paths, the package |
