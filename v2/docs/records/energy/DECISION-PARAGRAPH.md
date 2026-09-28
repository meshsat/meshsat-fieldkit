# Decision sheet: the 72-hour relay mission on battery and solar (M1)

Stream energy, MESHSAT-1357, 28 September 2026 (second issue, after an independent AI review). A prototype
design: nothing built or measured. AI analysis; the figures are in `ENERGY-RECONCILIATION.md`.

The kit cannot run the 72-hour relay mission on battery and solar as written; no option changes that. A
September night needs about 500 watt-hours; the aged battery holds 108. Choose: (1) accept this, a
12-volt source carrying each night; or (2) change the mission's night mode to one computer on 16 watts keeping
LoRa, Iridium, APRS and GNSS, with the monitor, 5G, WiFi link, Zigbee and two computers off, plus a second
battery (no place proven), a 200-watt panel with the solar input limited or re-rated, and a lower battery
shutdown line. On planning figures option 2 carries an average September night only with the battery above 17 C
(at 15 C it fails), never December. I recommend 2.
