| Model | Maker | Size (mm) | V | Range (V) | A | W | rpm | CFM | Pa | dB(A) | Temp (C) | Life (h) | IP | Lines |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 9WPA0412P6G001 | Sanyo Denki | 40 x 40 x 20, plastic, ribbed | 12 | 10.8 to 13.2 | 0.17 | 2.0 | 13700 | 13.4 | 210 | 44 | -20 to +70 | 40,000 at 60 C | IP68 | pulse sensor, PWM (4 wires) |

### 2e. The identity rows for Layer 6 (`records/l6pwr` integrates them)

| Field | mixer | cooler fan |
|---|---|---|
| MPN | 9WL0612P4H001 | 9WPA0412P6G001 |
| maker, family | Sanyo Denki, San Ace 60W Splash Proof Fan | Sanyo Denki, San Ace 40W Splash Proof Fan (9WPA type) |
| package | 60 x 60 x 25 mm, aluminium frame, 120 g, four leads (12 V, GND, pulse sensor, PWM); the hole pattern NOT READ (CAD behind a form; the 60 mm class standard is 50.0 mm on 4.3 mm holes) | 40 x 40 x 20 mm, plastic frame, ribbed, 47 g, four leads; the hole pattern NOT READ (the 40 mm class standard is 32.0 mm on 4.3 mm holes) |
| document, revision | the maker's product-database page as served 3 October 2026 (sha256 of the HTML ec42c4a8744d8a2b...), transcribed in `v2/vendor/fans/sanyo-denki-splash-proof-fan-pages-2026-10-03.md`; the instruction manual M0011876C is behind a download form, NOT READ | the page as served 3 October 2026 (sha256 90a9c2d2fc1f7457...), the same file; manual M0011876C NOT READ |
| grade against the envelope and the margins | operating -20 to +70 C: INSIDE the envelope (-20 to +40 C) and the +55 C margin; the hold's 68.65 C mixed air 1.35 K under the limit; storage temperature NOT READ | the same |
| life | 180,000 h at 60 C (215,000 at 40 C), the maker's expected life | 40,000 h at 60 C (70,000 at 40 C) |
| price and availability (indicators) | USD 73.69 at 1, Sager, stock 0 (FindChips, 3 October 2026 00:27 UTC); no EU row | EUR 58.83 at 1, RS 101593, stock 51; Farnell 4218284 EUR 76.83, stock 0 (the same reading) |
| what is owed | the starting current (bench, E11-35); the PWM input level and the hole pattern (the manual); an EU price | the same, plus the fit (section 2g) |

Filed with the pick under `v2/vendor/fans/` as REQ-043 asks (the transcription; the pages are served by script), registered in
`v2/vendor/sources.txt` and `v2/vendor/SOURCES.yaml` (`documents_filed_l7pwr`), and in `PROCUREMENT.md` section 8.

