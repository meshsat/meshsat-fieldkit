# Sanyo Denki San Ace splash-proof (IP68) fans: the maker's product-database pages, transcribed

Read 3 October 2026, 00:12 to 00:25 UTC, by the Layer 7 author (stream l7pwr, MESHSAT-1357) from the maker's own product
database, `https://products.sanyodenki.com/en/sanace/dc/splash-proof-fan/<model>/`, with curl from the runner (HTTP 200, no
login). The pages are served by script and are not filed; each specification table is transcribed below exactly as the page
printed it (the "to" of each range is the page's wave dash), with the sha256 of the HTML as fetched (first 16 hex characters)
so a re-read can tell whether the page changed. The maker's instruction manual (M0011876C) and CAD are behind a download form
and were not read: the hole pattern, the PWM input levels and the starting current are NOT READ from the maker. Nothing here
has been bought or measured.

| Model | Page sha256/16 | Frame (mm) and material | Rated V | Operating voltage range (V) | Rated current (A) | Rated input (W) | Speed (min-1) | Max airflow (m3/min, CFM) | Max static pressure (Pa, inchH2O) | SPL (dB(A)) | Operating temperature (C) | Expected life (h) | Mass (g) | Sensor, PWM, IP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 9WL0612P4H001 (San Ace 60W) | ec42c4a8744d8a2b | 60 x 25, aluminium | 12 | 10.8 to 13.2 | 0.17 | 2.04 | 6150 | 0.78, 27.5 | 97, 0.389 | 36 | -20 to +70 | 180000/60 C (215000/40 C) | 120 | pulse sensor, PWM yes, IP68 |
| 9WL0612P4J001 (San Ace 60W) | 65acf7e8b4c445fd | 60 x 25, aluminium | 12 | 10.8 to 13.2 | 0.39 | 4.68 | 8650 | 1.1, 38.8 | 182, 0.73 | 47 | -20 to +70 | 180000/60 C (215000/40 C) | 120 | pulse sensor, PWM yes, IP68 |
| 9WL0612P4S001 (San Ace 60W) | 1bc61790238dcc78 | 60 x 25, aluminium | 12 | 10.8 to 13.2 | 0.67 | 8.04 | 11000 | 1.4, 49.4 | 300, 1.204 | 53 | -20 to +70 | 180000/60 C (215000/40 C) | 120 | pulse sensor, PWM yes, IP68 |
| 9WL0624P4H001 (San Ace 60W) | f540fc1c3d6c0728 | 60 x 25, aluminium | 24 | 21.6 to 26.4 | 0.08 | 1.92 | 6150 | 0.78, 27.5 | 97, 0.389 | 36 | -20 to +70 | 180000/60 C (215000/40 C) | 120 | pulse sensor, PWM yes, IP68 |
| 9WPA0412P6G001 (San Ace 40W) | 90a9c2d2fc1f7457 | 40 x 20, plastic, ribbed | 12 | 10.8 to 13.2 | 0.17 | 2.0 | 13700 | 0.38, 13.4 | 210, 0.84 | 44 | -20 to +70 | 40000/60 C (70000/40 C) | 47 | pulse sensor, PWM yes, IP68 |
| 9WPA0424P6G001 (San Ace 40W) | 559b1b7befa167a6 | 40 x 20, plastic, ribbed | 24 | 21.6 to 26.4 | 0.09 | 2.0 | 13700 | 0.38, 13.4 | 210, 0.84 | 44 | -20 to +70 | 40000/60 C (70000/40 C) | 47 | pulse sensor, PWM yes, IP68 |

Not on the maker's database: `9WP0412H6001` (a 40 mm IP68 model distributors list at 12 V, 0.1 A) answered HTTP 404 at
`https://products.sanyodenki.com/en/sanace/dc/splash-proof-fan/9WP0412H6001/` on 3 October 2026 (00:20 UTC), as did the
guessed lower-speed codes 9WPA0412P6H001, P6J001 and P6K001 and a 28 mm 9WPB0412P6G001: no 40 mm IP68 fan of the maker's
database under 2.0 W was found. The maker's splash-proof catalogue (C1111B002, `Splash_Proof_Oil_Proof_Fan.pdf`) answered
HTTP 403 from the maker's site and came back truncated from the Internet Archive (5,242,880 bytes, no trailer), so it is not
read here.
