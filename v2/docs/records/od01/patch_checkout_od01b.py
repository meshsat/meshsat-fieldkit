#!/usr/bin/env python3
"""Stream od01b (MESHSAT-1357, 29 Sep 2026): correct CHECKOUT-LIST.md in place. Each replacement asserts its old text is
present exactly once; the result must differ, carry no em or en dash, keep the reviewed totals of lines 1 to 8, and a
second run is refused."""
import sys, os
FN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHECKOUT-LIST.md")
s = open(FN, encoding="utf-8").read(); s0 = s
MARK = "> **Revised 29 September 2026 (stream od01b)**"
if MARK in s: sys.exit("already applied")

# the added lines, priced from the seller's pages (incl. 21 % VAT as shown; excl. = incl. / 1.21, rounded per line)
ADDED = [("10", "TS1", "Elmwood (Honeywell) 2455R thermostat, 90 C, normally closed, automatic reset; reichelt \"2455R 90 NC\"", 12.71, 1, "O21", "23:31"),
         ("11", "TS2, TS3", "Elmwood (Honeywell) 2455R thermostat, 60 C +-3 C, normally closed, closes at 45 C, with bracket B203-S; reichelt \"2455R 60 NC\"", 13.47, 2, "O20", "23:31"),
         ("12", "TS4", "Elmwood (Honeywell) 2455R thermostat, 140 C, normally closed; reichelt \"2455R 140 NC\"", 23.69, 1, "O22", "23:24"),
         ("13", "K1", "Finder 40.52.9.012.0000 relay, 2 changeover, 8 A, 12 V DC coil; reichelt \"FIN 40.52.9 12V\"", 4.98, 1, "O23", "23:33"),
         ("14", "X1", "Finder 95.05 relay socket for the 40.52, screw terminals, DIN rail; reichelt \"FIN 95.05\"", 4.73, 1, "O24", "23:33")]
rows, ex_sum, in_sum = [], 0.0, 0.0
for n, ref, part, incl, q, src, t in ADDED:
    ex_unit = round(incl / 1.21, 2); ex_line = round(incl * q / 1.21, 2); in_line = round(incl * q, 2)
    ex_sum += ex_line; in_sum += in_line
    rows.append("| %s | %s (%s) | reichelt elektronik, Netherlands shop (%s) | EUR %.2f \"incl. 21 %% VAT\" (EUR %.2f excl., arithmetic) | %d | EUR %.2f excl., %.2f incl. | as line 5 (one reichelt parcel; \"Shipping costs from EUR 6.95\") | \"in stock, delivery within 2 - 3 business days\" | %s |"
                % (n, part, ref, src, incl, ex_unit, q, ex_line, in_line, t))
ex_sum, in_sum = round(ex_sum, 2), round(in_sum, 2)
assert (ex_sum, in_sum) == (60.37, 73.05), (ex_sum, in_sum)

R = []
R.append(("""# OD-01: the checkout list for the minimum physical test package, one prototype case

""", """# OD-01: the checkout list for the minimum physical test package, one prototype case

> **Revised 29 September 2026 (stream od01b)** after the owner's instruction of that day: the quoted totals of lines 1 to
> 8 stay as recomputed (EUR 416.40 excl. VAT; EUR 511.80 and 503.85 with VAT); the shipping figure EUR 30.26 is now
> labelled for what it is, a "from" price plus an exchange-rate ESTIMATE, not a delivered total; lines 10 to 14 are added
> for the automatic over-temperature shutdown the owner asked for (R5), each priced from the seller's page with the time
> read, and line 15 lists the small items left unpriced. Nothing was bought, carted or asked.

"""))
R.append(("""| 9 | Dummy stack plate and dummy pack block | the machining request (`MACHINING-RFQ.md`, lines H2 and H3) or the operator's workshop | TBD by quote | 1 set | TBD | TBD | TBD | |
""", """| 9 | Dummy stack plate and dummy pack block | the machining request (`MACHINING-RFQ.md`, lines H2 and H3) or the operator's workshop | TBD by quote | 1 set | TBD | TBD | TBD | |

**Added 29 September 2026: the automatic over-temperature shutdown** (`TEST-PROCEDURE.md` section 3; the owner's
instruction R5). Read at reichelt's Netherlands shop on 28 September 2026 between 23:24 and 23:33 UTC (29 September,
01:24 to 01:33 CEST), in the same parcel as lines 5 to 7. The thermostats' maker states AC contact ratings only, so they
carry only the relay coil's 54 mA and the relay (DC1 breaking capacity 8 A at 30 V, Finder's sheet) switches the heaters.

| # | Part (exact number) | Seller and page | Unit price as shown, VAT status | Qty | Line total | Shipping to NL as stated | Stock or lead as shown | Read (UTC) |
|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + """
| 15 | Unpriced small items: two panel pushbuttons (one normally open START, one normally closed STOP/TEST, each 1 A at 24 V DC or more); two in-line blade fuse holders with a 7.5 A and a 1 A fuse; a three-way link block; four M4 x 45 mm PA66 (nylon) stand-offs; M3 A2 screws, nuts and washers; heat-resistant matt black paint rated to 200 C or more (H2) | not read | **unpriced** | 1 set | unpriced | - | - | |

Lines 10 to 14 together: **EUR %.2f excl. VAT, EUR %.2f incl. 21 %% VAT** (arithmetic from the page prices). They are not
added into the totals of section 3, which stay the reviewed figures for lines 1 to 8; with them, lines 1 to 14 would be EUR
%.2f excl. VAT (arithmetic).
""" % (ex_sum, in_sum, 416.40 + ex_sum)))
R.append(("""| **Total, lines 1 to 8** | **EUR 416.40** (of which EUR 69.42 ESTIMATE by conversion, the arrestor) | **EUR 511.80** with the case line as its page shows it (25 %), or **EUR 503.85** with the case line at 21 % (ESTIMATE) | **separate line: EUR 30.26 known (reichelt 6.95 "from", Pico about 23.31 ESTIMATE), plus two sellers' freight not shown (flight-cases.eu, PolyPhaser)** |""",
"""| **Total, lines 1 to 8** | **EUR 416.40** (of which EUR 69.42 ESTIMATE by conversion, the arrestor) | **EUR 511.80** with the case line as its page shows it (25 %), or **EUR 503.85** with the case line at 21 % (ESTIMATE) | **separate line, not a delivered total: EUR 30.26 is reichelt's "from EUR 6.95" (a from price, the real figure shown only at checkout) plus Pico's GBP 20 registered converted at the ECB rate (EUR 23.31, an exchange-rate ESTIMATE); two sellers' freight is not shown at all (flight-cases.eu, PolyPhaser), and import charges on the PolyPhaser and Pico parcels are not included** |"""))
R.append(("""- The made parts: the face-plate blank for the heat test (H1), the four setting legs (C6) for both tests, then C1, C3
  and the two C4 plates: `MACHINING-RFQ.md`.""",
"""- The made parts: the heat-test plate blank H1 (its own sheet H1-1 since 29 September), the four setting legs (C6) for
  both tests, then C1, C3 and the two C4 plates: `MACHINING-RFQ.md`, released for cutting only after the receipt checks
  of its section 6.
- The shutdown's small items (line 15), unpriced."""))
R.append(("""| O19 | https://www.rapidonline.com/arcol-hs100-2r2-j-100w-aluminium-clad-resistor-62-8180 | 20:49:22 | runner, `9524c67ef7b041ed` | "No longer stocked" |""",
"""| O19 | https://www.rapidonline.com/arcol-hs100-2r2-j-100w-aluminium-clad-resistor-62-8180 | 20:49:22 | runner, `9524c67ef7b041ed` | "No longer stocked" |
| O20 | https://www.reichelt.com/nl/en/shop/product/thermostat_60_c_-3_c_nc_contact-263592 (29 Sep, od01b) | 23:31:50 | runner, `3ffa38c2edeb4c29` | "2455R 60 NC", "ELMWOOD SENSORS", "Opening temperature: 60°C", "Closing temperature: 45°C", "With mounting bracket B203-S", "Tolerance ±3 °C", "240 V AC", current 10, "€13.47 incl. 21% VAT" (struck "€13.68"), in stock, 2 to 3 business days; datasheet link 2455R_DB_EN.pdf |
| O21 | https://www.reichelt.com/nl/en/shop/product/thermostat_90_c_-3_c_nc_contact-263595 (od01b) | 23:31:51 | runner, `f081eb0dd0bfe75d` | "2455R 90 NC", "ELMWOOD SENSORS", "Tolerance ±6 °C" (the title says +-3; the procedure takes +-6), "€12.71 incl. 21% VAT" (struck "€12.91"), in stock |
| O22 | https://www.reichelt.com/nl/en/shop/search/bimetallschalter (od01b) | 23:24:26 | runner, `3b4040d679ca8321` | 13 results, the 2455R series; "2455R 140 NC", "Thermostat 140°C ±4°C, NC contact", "€23.69 incl. 21% VAT", in stock |
| O23 | https://www.reichelt.com/nl/en/shop/product/plug-in_relay_2x_um_250_v_8_a_12_v_rm_5_0_mm-8105 (od01b) | 23:33:25 | runner, `fa0dfa3fcea4143d` | "40.52.9.012.0000", "FINDER", "€4.98 incl. 21% VAT", in stock; datasheet link FIN_40_DB_EN.pdf |
| O24 | https://www.reichelt.com/nl/en/shop/search/finder%2040.52 (od01b) | 23:33:00 | runner, `7825e364d17a1a76` | "FIN 95.05", "Relay base for relay Fin 40..", "For FIN 40.51, 40.52, 40.61", "10 A, 250 V", "€4.73 incl. 21% VAT", in stock |
| O25 | makers' sheets filed in the tree (od01b): `v2/vendor/elmwood/honeywell-commercial-thermostats-2455r.pdf` (Honeywell "Commercial Thermostats", 2455R pages 4 and 5), `v2/vendor/finder/finder-40-series-en.pdf` (Finder 40 series, XI-2018), `v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf` (Arcol HS, 12/14.08) | 23:24 to 23:33 | sha256 in each folder's `sources.txt` | the thermostats' tolerance bands (Table 1) and AC-only contact ratings (Table 4); the relay's 8 A and DC1 8 A at 30 V, coil 0.65 W; the HS resistors' ratings, heatsinks and hole sizes |"""))

for a, b in R:
    n = s.count(a)
    assert n == 1, ("expected once", n, a[:80])
    s = s.replace(a, b)
assert s != s0
assert "\u2014" not in s and "\u2013" not in s
for keep in ("**EUR 416.40**", "**EUR 511.80**", "**EUR 503.85**"):
    assert keep in s, keep
open(FN, "w", encoding="utf-8").write(s)
t = open(FN, encoding="utf-8").read()
assert MARK in t and t.count("| 15 | Unpriced") == 1
print("CHECKOUT-LIST.md patched: %d replacements; added lines 10 to 14: EUR %.2f excl., %.2f incl." % (len(R), ex_sum, in_sum))
