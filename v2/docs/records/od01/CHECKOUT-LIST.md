# OD-01: the checkout list for the minimum physical test package, one prototype case

> **Revised 29 September 2026 (stream od01b)** after the owner's instruction of that day: the quoted totals of lines 1 to
> 8 stay as recomputed (EUR 416.40 excl. VAT; EUR 511.80 and 503.85 with VAT); the shipping figure EUR 30.26 is now
> labelled for what it is, a "from" price plus an exchange-rate ESTIMATE, not a delivered total; lines 10 to 14 are added
> for the automatic over-temperature shutdown the owner asked for (R5), each priced from the seller's page with the time
> read, and line 15 lists the small items left unpriced. Nothing was bought, carted or asked.

> **Revised by the coordinator on 28 September 2026 after the independent AI check** (`checks/check-1.md` beside this file): line 4 removed (B2), line 8 at Pico's EUR price with its stated freight (m1), the totals recomputed from the line values (B3), the case variant's evidence strengthened (m2), a Dutch alternative seller named (m9). Every part number, price and stock figure was re-read by the check between 21:00 and 21:07 UTC and had not moved.

MESHSAT-1357, stream od01, 28 September 2026, prepared by an AI session for the owner's ruling D-19 (OD-01). **Nothing on
this page has been bought, carted, ordered or asked of anyone.** No account was logged into, no basket was filled, no
message was sent. The MeshSat field kit V2 is an unbuilt prototype design: no board has been made, and the two tests this
list serves (the empty-case heat-balance test and the case mock-up, `TEST-BRIEF.md`) have not run. **Buying these parts
closes no measurement gate** (D-19); only the readings of the tests do.

**How figures are marked.** Every price, stock and shipping figure below was read from the public page named in section
5 at the UTC time given there, in the page's own currency and with the VAT note the page itself shows. Nothing was read
from a basket or a checkout, because the session may not fill one; so no shipping figure below is a quoted freight. A
figure converted from USD or GBP is labelled **ESTIMATE** (ECB reference rates of 28 September 2026, section 5, O16:
1 EUR = 1.1378 USD = 0.85785 GBP). Where a page shows only a price including VAT, the price excluding VAT is that figure
divided by 1.21 (arithmetic, the Dutch rate the page names). A line with no page the session could read says **TBD by
quote**; no price is invented.

## 1. The case variant (the owner's condition: "confirm the exact case variant before ordering")

**What Peli's own pages say.** Peli's sites refused this host (HTTP 403 on every product URL tried at 20:40 and 20:42
UTC), so the three pages were read from the Internet Archive's copies with the `id_` flag, as the vendor-fetch note
directs (section 5, O4 to O7):

| Page | Capture | What it says |
|---|---|---|
| Peli EU, 1450PF Special Application Panel Frame (O5), and the same page for Great Britain (O6) | 7 and 8 February 2025 | "1450PF Special Application Panel Frame for 1450EU Protector Case"; "COMPATIBLE WITH 1450EU Protector Case"; kit: "1 panel frame, 1 o-ring, 10 inserts, 4 self-tapping screws" |
| Peli EU, 1450EU Protector Case (O4) | 8 June 2026 | "1450EU Protector Case"; configurations With Padded Dividers (1454), No Foam (1450NF), With Foam (1450WF); "Made in Germany"; interior 37.4 x 26 x 15.4 cm, exterior 40.9 x 33.1 x 17.5 cm, lid depth 4.4 cm, bottom depth 11.1 cm; the 1450PF listed among its accessories; body polypropylene; maximum temperature "190° F (88 ° C)"; IP67 |
| Pelican US, 1450 Protector Case (O7) | 29 March 2026 | "1450 Protector Case", SKU 1450-000-110, "Made in the USA"; exterior 41.76 x 33.02 x 17.32 cm, interior 37.24 x 26.01 x 15.54 cm, lid 4.45 cm, bottom 11.1 cm; no 1450PF in the text read |

**What the seller sells.** The listing W1 is titled "Peli Protector 1450" and does not print "1450EU". But (O1, read
20:40 UTC) every one of its nine variants carries a Peli part number ending in **E** (for example `1450-001-110E`,
"Peli Protector 1450 Case Black Empty"), its product images are named `peli-1450eu-...`, and its figures (internal
374 x 260 x 154 mm, external 409 x 331 x 175 mm, lid 44 mm, base 111 mm) are exactly the 1450EU page's and not the US
page's. The frame listing (O2) is `1450-300-110E`, "Fits Peli 1450 Case". **The seller sells the 1450EU** (INFERRED
from the part-number suffix and the figures; the listing text does not say so in words). Peli's page says the 1450PF is
for the 1450EU, so **the frame fits what the seller sells, on Peli's own statement.**

**What to order.** The 1450EU in the empty configuration (Peli's 1450NF; the seller's "Empty", part numbers
`1450-001-xxxE`) and the 1450PF kit `1450-300-110E`. Empty, because the frame and the test hardware take the base and
the mock-up drills it. Colour does not enter either test (both run indoors, out of the sun); the list carries black
`1450-001-110E` (EUR 169.00 excl. VAT), and the orange, yellow, desert tan and OD green empty variants at EUR 168.90
are interchangeable for the tests (session choice under the standing rule of 26 September 2026; reversal: pick any of
them). A lighter colour takes less sun in the field, which the thermal model does not yet quantify.

**What stays unresolved, exactly.** D-08a fixes the design on the moulding of Peli's customer drawing 1451-931 dated 15
January 2025 (`v2/vendor/peli/1450/1451-931-customer-drawing-2025-01-15.pdf`, title "1450 PROTECTOR", Pelican Products
Inc., Torrance). No page read says whether the 1450EU made in Germany is that moulding. For it: the owner supplied the
1451-931 files among Peli's "EU case bodies" (appendix 32.41), and Peli's EU CAD package for the 1400EU held in this
tree (`v2/vendor/peli/1400/1400EU_pdf_peli.zip`) carries the drawing `1402-931 PID 7-24-2025.pdf`, the same family as
the 1450's `1451-931 PID 7-24-2025` (INFERRED by analogy). Against certainty: the three sets of outside figures differ
in their last millimetres (drawing 411 x 329, depth 109 + 45; EU page 409 x 331; US page 417.6 x 330.2), and Peli states
no tolerance. Check T1 at receipt (date wheel, moulded markings, photographs of both long walls and the back wall)
settles it under D-08a, and the seller states "60 days free Returns" (O1) and, for private customers, "60 days' full
right of return" (O3), so a case of an older moulding goes back rather than being adapted.

**The question the owner would ask the seller (prepared, NOT SENT; Guardique Products A/S, flight-cases.eu):**

> We intend to buy one Peli 1450, black, empty (your SKU 1450-001-110E) and one 1450PF panel frame kit (1450-300-110E),
> delivered to the Netherlands. (1) Is 1450-001-110E the Peli 1450EU made in Germany, and which production month and
> year do the date wheels of your current stock show? (2) Is 1450-300-110E Peli's panel frame kit for the 1450EU, with
> the o-ring, ten inserts and four screws? (3) What is the freight to postcode [owner's postcode], and is VAT charged at
> the Dutch 21 % for a private buyer?

A second question, to Peli rather than the seller, would settle the drawing link directly (prepared, NOT SENT): "Does
customer drawing 1451-931 dated 15 January 2025 describe the current 1450EU moulding?"

## 2. The list

One line per part, in the brief's order. "Read" is the UTC time on 28 September 2026 (sources in section 5). Stock and
lead as the page shows them.

| # | Part (exact number) | Seller and page | Unit price as shown, VAT status | Qty | Line total | Shipping to NL as stated | Stock or lead as shown | Read |
|---|---|---|---|---|---|---|---|---|
| 1 | Peli 1450EU Protector, black, empty, part `1450-001-110E` | Guardique Products A/S (Denmark), https://flight-cases.eu/peli-1450.html (O1) | EUR 169.00 excl. VAT; EUR 211.25 incl. the page's VAT (Denmark's 25 %; the page shows both figures, no country chosen) | 1 | EUR 169.00 excl. | not shown: "add an item to the basket and you'll then receive a freight estimate" (O3) | "Normal in stock"; "orders placed before 12:00 are shipped the same day" (O3) | 20:40 |
| 2 | Peli 1450PF Special Application Panel Frame Kit, `1450-300-110E` | same seller, https://flight-cases.eu/peli-1450pf-special-application-panel-frame-kit.html (O2) | EUR 29.66 excl. VAT, EUR 37.08 incl. (special price; regular EUR 32.96 / 41.20) | 1 | EUR 29.66 excl. | as line 1 (one parcel) | "Normal in stock" | 20:42 |
| 3 | PolyPhaser GTH-SFF-AL, SMA F/F bulkhead arrestor, DC to 6 GHz | PolyPhaser (Infinite Electronics, USA), https://www.polyphaser.com/sma-surge-protector-6ghz-gas-discharge-tube-gth-sff-al (O8) | USD 78.99 at 1+, "All Prices are in US Dollars and do not include duties" | 1 | USD 78.99; EUR 69.42 ESTIMATE | not shown | "QTY available: Call us"; the text says it "is in-stock and will ship same-day" | 20:40 |
| 4 | REMOVED after the independent check (B2): the Raspberry Pi Compute Module 5 Passive Cooler, MPN `SC1752`, is not the cooler the stack assumes. Raspberry Pi's own product brief (December 2024, page 3) gives 56 x 41 x 12.7 mm, passive, no fan; M1's chain carries 21.0 mm and `ASSEMBLY.md` a clip-on cooler with a fan lead. Used at T4 it would make the monitor-depth limit up to 8.3 mm too generous. Until the heatsink is picked, T4 uses a printed stand-in of the chain's 21.0 mm (with the other stand-ins). Not bought. Was: (seller code KW-3425, EAN 5056561805283) | none (removed) | - | - | - | - | - | - |
| 5 | Stack heaters: Arcol `HS50 6R8 F`, 50 W, 6.8 ohm, 1 %, aluminium housed (reichelt code ARC HS50 6R8 F) | reichelt elektronik, Netherlands shop, https://www.reichelt.com/nl/en/shop/search/hs50%206,8 (O10) | EUR 3.56 "incl. 21 % VAT" (EUR 2.94 excl., arithmetic) | 3 | EUR 8.83 excl., 10.68 incl. | "Shipping costs from EUR 6.95" (page header) | "in stock, delivery within 2 - 3 business days" | 20:49 |
| 6 | PA patch block: Arcol `HS100 2R2 J`, 100 W, 2.2 ohm, 5 % (ARC HS100 2R2 J) | reichelt, https://www.reichelt.com/nl/en/shop/search/hs100%202,2 (O11) | EUR 10.88 "incl. 21 % VAT" (EUR 8.99 excl.) | 1 | EUR 8.99 excl., 10.88 incl. | as line 5 (one parcel) | "in stock, delivery within 2 - 3 business days" | 20:49 |
| 7 | Thermal compound: Amasan `WLP-T12 35G`, silicone heat-sink paste, 35 g cartridge, -30 to +200 C (AMA WLP-T12 35G) | reichelt, https://www.reichelt.com/nl/en/shop/search/thermal%20paste (O12) | EUR 6.66 "incl. 21 % VAT" (EUR 5.50 excl.) | 1 | EUR 5.50 excl., 6.66 incl. | as line 5 | "in stock, delivery within 2 - 3 business days" | 20:49 |
| 8 | Thermocouples: Pico `SE001`, type K, exposed tip, fibreglass insulated, 1 m, moulded flat-pin mini plug, tip -60 to +350 C. Revised after the check (m1): Pico charges in the currency selected (GBP, EUR or USD) and lists SE001 at EUR 12.50, so the line is EUR 125.00; Pico's how-to-order page states Europe delivery at GBP 20 registered or GBP 30 by courier, duties and taxes the receiver's. Buy these after the logger is chosen, so the plug suits it (m12) | Pico Technology (UK), https://www.picotech.com/accessories/type-k-thermocouple/thermocouple-type-k-glass-fibre-1-m (O13) | EUR 12.50 (Pico's own EUR price; GBP 10.50 in pounds; VAT status not stated in the text read) | 10 | EUR 125.00 | GBP 20 registered to Europe (about EUR 23.31 ESTIMATE) or GBP 30 by courier; duties and taxes the receiver's | "In stock. Available for despatch." | 20:48 |
| 9 | Dummy stack plate and dummy pack block | the machining request (`MACHINING-RFQ.md`, lines H2 and H3) or the operator's workshop | TBD by quote | 1 set | TBD | TBD | TBD | |

**Added 29 September 2026: the automatic over-temperature shutdown** (`TEST-PROCEDURE.md` section 3; the owner's
instruction R5). Read at reichelt's Netherlands shop on 28 September 2026 between 23:24 and 23:33 UTC (29 September,
01:24 to 01:33 CEST), in the same parcel as lines 5 to 7. The thermostats' maker states AC contact ratings only, so they
carry only the relay coil's 54 mA and the relay (DC1 breaking capacity 8 A at 30 V, Finder's sheet) switches the heaters.

| # | Part (exact number) | Seller and page | Unit price as shown, VAT status | Qty | Line total | Shipping to NL as stated | Stock or lead as shown | Read (UTC) |
|---|---|---|---|---|---|---|---|---|
| 10 | Elmwood (Honeywell) 2455R thermostat, 90 C, normally closed, automatic reset; reichelt "2455R 90 NC" (TS1) | reichelt elektronik, Netherlands shop (O21) | EUR 12.71 "incl. 21 % VAT" (EUR 10.50 excl., arithmetic) | 1 | EUR 10.50 excl., 12.71 incl. | as line 5 (one reichelt parcel; "Shipping costs from EUR 6.95") | "in stock, delivery within 2 - 3 business days" | 23:31 |
| 11 | Elmwood (Honeywell) 2455R thermostat, 60 C +-3 C, normally closed, closes at 45 C, with bracket B203-S; reichelt "2455R 60 NC" (TS2, TS3) | reichelt elektronik, Netherlands shop (O20) | EUR 13.47 "incl. 21 % VAT" (EUR 11.13 excl., arithmetic) | 2 | EUR 22.26 excl., 26.94 incl. | as line 5 (one reichelt parcel; "Shipping costs from EUR 6.95") | "in stock, delivery within 2 - 3 business days" | 23:31 |
| 12 | Elmwood (Honeywell) 2455R thermostat, 140 C, normally closed; reichelt "2455R 140 NC" (TS4) | reichelt elektronik, Netherlands shop (O22) | EUR 23.69 "incl. 21 % VAT" (EUR 19.58 excl., arithmetic) | 1 | EUR 19.58 excl., 23.69 incl. | as line 5 (one reichelt parcel; "Shipping costs from EUR 6.95") | "in stock, delivery within 2 - 3 business days" | 23:24 |
| 13 | Finder 40.52.9.012.0000 relay, 2 changeover, 8 A, 12 V DC coil; reichelt "FIN 40.52.9 12V" (K1) | reichelt elektronik, Netherlands shop (O23) | EUR 4.98 "incl. 21 % VAT" (EUR 4.12 excl., arithmetic) | 2 (K1, K2) | EUR 8.24 excl., 9.96 incl. | as line 5 (one reichelt parcel; "Shipping costs from EUR 6.95") | "in stock, delivery within 2 - 3 business days" | 23:33 |
| 14 | Finder 95.05 relay socket for the 40.52, screw terminals, DIN rail; reichelt "FIN 95.05" (X1) | reichelt elektronik, Netherlands shop (O24) | EUR 4.73 "incl. 21 % VAT" (EUR 3.91 excl., arithmetic) | 2 (X1, X2) | EUR 7.82 excl., 9.46 incl. | as line 5 (one reichelt parcel; "Shipping costs from EUR 6.95") | "in stock, delivery within 2 - 3 business days" | 23:33 |
| 15 | Unpriced small items: two panel pushbuttons (one normally open START, one normally closed STOP/TEST, each 1 A at 24 V DC or more); two in-line blade fuse holders with a 7.5 A and a 1 A fuse (F1, F2); two 1N4007 diodes (D1, D2); a three-way link block; four M4 x 45 mm PA66 (nylon) stand-offs; M3 A2 screws, nuts and washers; heat-resistant matt black paint rated to 200 C or more (H2) | not read | **unpriced** | 1 set | unpriced | - | - | |

Lines 10 to 14 together: **EUR 68.40 excl. VAT, EUR 82.76 incl. 21 % VAT** (with the second relay and socket of the independent check's m2) (arithmetic from the page prices). They are not
added into the totals of section 3, which stay the reviewed figures for lines 1 to 8; with them, lines 1 to 14 would be EUR
476.77 excl. VAT (arithmetic).

Alternatives read, not on the list: for lines 1 and 2, Multi-Cases.nl lists `1450-001-110E` from EUR 158,00 (in stock) and `1450-300-110E` from EUR 31,00 (read by the independent check; its VAT basis was not read), a Dutch seller; also for line 8, Kiwi Electronics' Adafruit `P270` type K glass braid 1 m (bare wire
ends, no plug), EUR 11.48 incl. VAT, "EUR 9.49 Ex. VAT", "10 or more EUR 10.91 Ea.", "13 piece(s) in stock" (O17, 20:48),
an NL seller at Dutch VAT but needing a plug per channel unless the logger has screw terminals; for line 5, Rapid
Electronics (UK) `HS50 6R8 J` order code 62-8148, GBP 2.00 excl. VAT at 1+, "Despatched same day - 633 in stock" (O18,
20:45); for line 6, Rapid's `HS100 2R2 J` (62-8180) reads "No longer stocked" (O19, 20:49). If a logger is borrowed
with its own thermocouples, line 8 drops.

**Why these values.** Line 5: three 6.8 ohm heaters at 12.0 V give 21.2 W each, so one, two or three give about 21, 42
and 64 W (arithmetic; `READY-TO-ACT.md` 5.2 asks for 20, 40 and 60 W), 1.76 A each. Line 6: 2.2 ohm gives 45 W at 9.95
V (4.5 A) and 83 W at 13.5 V (6.1 A), inside a 15 V, 7 A bench supply (arithmetic; the patch run asks for 45 to 83 W).
The 1 % part on line 5 replaces the 5 % one READY-TO-ACT named because the 5 % part was not on the NL page read; the
power is set by the measured voltage and current either way, so the tolerance does not enter a reading.

## 3. Totals

| Seller | Excl. VAT | Incl. VAT | Shipping to NL |
|---|---|---|---|
| flight-cases.eu (lines 1, 2) | EUR 198.66 | EUR 248.33 as the page shows it (25 %); EUR 240.38 at the Dutch 21 % (ESTIMATE: the EU's distance-selling rules tax a private buyer's order at the buyer's rate; the page does not show it) | not shown (basket only) |
| PolyPhaser (line 3) | EUR 69.42 ESTIMATE (USD 78.99) | EUR 84.00 ESTIMATE (21 % import VAT on the goods alone; duty, freight and the carrier's clearance fee not included, none shown) | not shown |
| Kiwi Electronics (line 4) | removed | removed | none |
| reichelt (lines 5 to 7) | EUR 23.32 | EUR 28.22 | from EUR 6.95 |
| Pico Technology (line 8) | EUR 125.00 (Pico's EUR price, 10 x 12.50) | EUR 151.25 ESTIMATE (21 % import VAT on the goods alone; duty and clearance not included) | GBP 20 registered, about EUR 23.31 ESTIMATE, or GBP 30 by courier |
| **Total, lines 1 to 8** | **EUR 416.40** (of which EUR 69.42 ESTIMATE by conversion, the arrestor) | **EUR 511.80** with the case line as its page shows it (25 %), or **EUR 503.85** with the case line at 21 % (ESTIMATE) | **separate line, not a delivered total: EUR 30.26 is reichelt's "from EUR 6.95" (a from price, the real figure shown only at checkout) plus Pico's GBP 20 registered converted at the ECB rate (EUR 23.31, an exchange-rate ESTIMATE); two sellers' freight is not shown at all (flight-cases.eu, PolyPhaser), and import charges on the PolyPhaser and Pico parcels are not included** |

Line 9 (the dummy blocks) and every made part are outside these totals: `MACHINING-RFQ.md`. B2B note: the seller of
lines 1 and 2 states "B2B NO VAT" (O1), so a buyer with a valid EU VAT number would pay the excl. figures there.

## 4. What the two tests also need, and what is deferred

**Needed, not priced here (so the list is not yet the whole spend):**
- The made parts: the heat-test plate blank H1 (its own sheet H1-1 since 29 September), the four setting legs (C6) for
  both tests, then C1, C3 and the two C4 plates: `MACHINING-RFQ.md`, released for cutting only after the receipt checks
  of its section 6.
- The shutdown's small items (line 15), unpriced.
- 3M VHB 5952 tape for the legs' pads (the legs are bonded to the frame, sheet 2) and ten 6-32 UNC x 1/2 in A2 pan-head
  screws for the plate into Peli's inserts (sheet 1): TBD by quote; no NL page listing either was found in the time box
  (reichelt's search for "vhb 5952" returned 0 results at 20:51 UTC).
- The fans for the "fans on" runs: two mixer fans (Same Sky CFM-6025BG68, the speed code still a pick) and three
  cooler-fan stand-ins (open pick D-18). Until they are picked the heat test runs fans off only, which is the record's
  conservative case (2.1 W/K still, `POWER-THERMAL.md` section 10); the fans-on conductance then stays open.
- The jumper plugs and RG-316 for check T10 (boards B and E): **not orderable, the plug pick is owed** (M17g and M17x
  "FAILS AS ASSUMED" until picked, `CASE-FIT-UNCERTAINTIES.md` section 2). T10 cannot run from this package.
- The arrestor's O-ring, hex nut and split lock washer are drawn on PolyPhaser's sheet held in
  `v2/vendor/polyphaser/`; the page read does not say all three ship with the part. Confirm at receipt (T11 needs them).
- A finding for the parts work, not a purchase (line 4 removed after the check): Raspberry Pi's own brief and Kiwi's page give the SC1752 as "56 mm x 41 mm x 12.7 mm", while M1's
  chain carries a 21.0 mm heatsink from the render scene and `READY-TO-ACT.md` 6.3 leaves open whether SC1752 is the
  "CM5 Cooler" of `ASSEMBLY.md`. Raspberry Pi states 12.7 mm itself (product brief, December 2024, page 3); the heatsink
  pick decides which part T4 measures, and T4 runs on a 21.0 mm printed stand-in until then.

**Deferred (the owner's condition: "unless the test procedure demonstrates they are necessary and existing or borrowed
equipment cannot suffice"):**

| Item | Price as read | Decision | Reason from the procedure (section 6 below) |
|---|---|---|---|
| Xenarc 709GNK monitor | USD 569.00 (O15, 20:52; the same bytes as W16 of 26 September); about EUR 500.09 ESTIMATE, excl. VAT, duty and freight | **DEFERRED** from this package | Every check the mock-up runs now takes a printed blank of the monitor's outline and 28.66 mm body depth (the Xenarc drawing v3 held in `v2/vendor/xenarc/`). One row needs the real part: M1 (board B's layout entry), because the body's depth tolerance and rear frame are on no held sheet. With the blank, T4 turns M1 into one number: the largest body depth the monitor may have. M1 closes when the monitor is bought and its body read with a caliper against that number (no case needed), or when Xenarc states the tolerance. Buy it when board B nears layout entry, not now. |
| PicoLog TC-08 logger, SKU PP222 | GBP 349 (O14, 20:40, "Currently In Stock"; the page's data also carries a euro price of 419); about EUR 406.83 ESTIMATE | **DEFERRED**: borrow first | The heat test needs eight type K channels logged together for hours, with cold-junction compensation, a resolution of 0.1 K or better and a file export. Any such logger does, or two four-channel logging thermometers started together; the mock-up needs none. Buy it only if no such logger can be borrowed. |

## 5. Sources read for this page (28 September 2026)

"runner" means the page was fetched by this host with curl; the hash is the first 16 hex digits of the sha256 of the
bytes received. The bytes are third-party pages kept in the session's scratch space, not published.

| ID | Page | Read (UTC) | How | What was read |
|---|---|---|---|---|
| O1 | https://flight-cases.eu/peli-1450.html | 20:40:29 | runner, `b380c4da2e26ae13` | "Peli Protector 1450", "Normal in stock", internal 374 x 260 x 154, external 409 x 331 x 175, lid 44, base 111; variant data: `1450-001-110E` "Black Empty" 169 / 211.25, `1450-001-150E` Orange, `-240E` Yellow, `-190E` Desert Tan, `-130E` OD Green Empty 168.9 / 211.125, with-foam variants 194.6; images `peli-1450eu-...`; "60 days free Returns", "B2B NO VAT"; Guardique Products A/S, DK44117487 |
| O2 | https://flight-cases.eu/peli-1450pf-special-application-panel-frame-kit.html | 20:42:53 | runner, `43befb86267189f7` | SKU "1450-300-110E", "Special Price EUR 37.08 EUR 29.66, Regular Price EUR 41.20 EUR 32.96", "Normal in stock", "Fits Peli 1450 Case" |
| O3 | https://flight-cases.eu/terms | 20:45:16 | runner, `0d2c6f04b6bae24b` | "add an item to the basket and you'll then receive a freight estimate"; same-day shipping before 12:00; private customers "60 days' full right of return" |
| O4 | https://web.archive.org/web/20260608110341id_/https://peli.com/eu/en/product/cases/protector/1450eu/ (live page: 403 at 20:42:52) | 20:43:17 | runner, `757b4c8632b02308` | as section 1 |
| O5 | https://web.archive.org/web/20250207065545id_/https://www.peli.com/eu/en/accessory/cases/special-application-panel-frame/1450PF/ (live: 403) | 20:43:18 | runner, `8ec875d36e9dcc4f` | as section 1 |
| O6 | https://web.archive.org/web/20250208013642id_/https://www.peli.com/gb/en/accessory/cases/special-application-panel-frame/1450PF/ | 20:43:21 | runner, `e75f9c3cffaefde6` | "for 1450EU Protector Case", "COMPATIBLE WITH 1450EU Protector Case" |
| O7 | https://web.archive.org/web/20260329041054id_/https://www.pelican.com/us/en/product/cases/protector/1450 (live: 403) | 20:43:20 | runner, `85cc10b72a93bab6` | as section 1 |
| O8 | https://www.polyphaser.com/sma-surge-protector-6ghz-gas-discharge-tube-gth-sff-al | 20:40:30 | runner, `b6d31d01e0343d0a` | SKU GTH-SFF-AL, "QTY available Call us", "1 + $78.99", "do not include duties" |
| O9 | https://www.kiwi-electronics.com/en/compute-module-5-passive-cooler-20297 | 20:47:58 | runner, `eda4a87c1af9be0c` | KW-3425, MPN SC1752, EAN 5056561805283, "EUR 5.43", "EUR 4.49 Ex. VAT", "75 piece(s) in stock", "Shipping from EUR 4.22 within The Netherlands", "56 mm x 41 mm x 12.7 mm" |
| O10 | https://www.reichelt.com/nl/en/shop/search/hs50%206,8 | 20:49:58 | runner, `1975aad1465b80e7` | "ARC HS50 6R8 F", "50 W, 6,8 Ohm, 1%", "EUR 3.56 incl. 21% VAT", "in stock, delivery within 2 - 3 business days", "Shipping costs from EUR 6.95" |
| O11 | https://www.reichelt.com/nl/en/shop/search/hs100%202,2 | 20:49:39 | runner, `3c65414aefe12bca` | "ARC HS100 2R2 J", "100 W, 2,2 Ohm, 5%", "EUR 10.88 incl. 21% VAT", in stock, 2 to 3 business days |
| O12 | https://www.reichelt.com/nl/en/shop/search/thermal%20paste | 20:49:59 | runner, `546cab365598c4a2` | "AMA WLP-T12 35G", "Amasan thermal paste T12, 35g cartridge", "-30 ... +200", "EUR 6.66 incl. 21% VAT", in stock |
| O13 | https://www.picotech.com/accessories/type-k-thermocouple/thermocouple-type-k-glass-fibre-1-m | 20:48:42 | runner, `3faa772a9ac29323` | "SE001", "GBP 10.5", "In stock. Available for despatch.", exposed junction, 1 m, "Molded flat pin mini-plug", IEC 60584 tolerances; page data price_euro 12.50 |
| O14 | https://www.picotech.com/data-logger/tc-08/thermocouple-data-logger | 20:40:34 | runner, `3e95e07eabfdc3d1` | "SKU: PP222", "GBP 349", "Currently In Stock", "8 input channels + CJC"; page data price_euro 419 |
| O15 | https://www.xenarcdirect.com/index.php?main_page=advanced_search_result&keyword=709GNK | 20:52:51 | runner, `08ecbbaa11cfb3a3` | "709GNK", "$569.00" (the bytes equal W16 of 26 September) |
| O16 | https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml | 20:50:27 | runner, `2d1636fbb9b263ce` | time "2026-09-28", USD 1.1378, GBP 0.85785 |
| O17 | https://www.kiwi-electronics.com/en/thermocouple-type-k-glass-braid-insulated-1m-809 | 20:48:31 | runner, `8b0d6a97247ff591` | ADA-270, MPN P270, as section 2 |
| O18 | https://www.rapidonline.com/arcol-hs50-6r8-j-aluminium-clad-resistor-50w-62-8148 | 20:45:52 | runner, `74e656788ecff59f` | as section 2 |
| O19 | https://www.rapidonline.com/arcol-hs100-2r2-j-100w-aluminium-clad-resistor-62-8180 | 20:49:22 | runner, `9524c67ef7b041ed` | "No longer stocked" |
| O20 | https://www.reichelt.com/nl/en/shop/product/thermostat_60_c_-3_c_nc_contact-263592 (29 Sep, od01b) | 23:31:50 | runner, `3ffa38c2edeb4c29` | "2455R 60 NC", "ELMWOOD SENSORS", "Opening temperature: 60°C", "Closing temperature: 45°C", "With mounting bracket B203-S", "Tolerance ±3 °C", "240 V AC", current 10, "€13.47 incl. 21% VAT" (struck "€13.68"), in stock, 2 to 3 business days; datasheet link 2455R_DB_EN.pdf |
| O21 | https://www.reichelt.com/nl/en/shop/product/thermostat_90_c_-3_c_nc_contact-263595 (od01b) | 23:31:51 | runner, `f081eb0dd0bfe75d` | "2455R 90 NC", "ELMWOOD SENSORS", "Tolerance ±6 °C" (the title says +-3; the procedure takes +-6), "€12.71 incl. 21% VAT" (struck "€12.91"), in stock |
| O22 | https://www.reichelt.com/nl/en/shop/search/bimetallschalter (od01b) | 23:24:26 | runner, `3b4040d679ca8321` | 13 results, the 2455R series; "2455R 140 NC", "Thermostat 140°C ±4°C, NC contact", "€23.69 incl. 21% VAT", in stock |
| O23 | https://www.reichelt.com/nl/en/shop/product/plug-in_relay_2x_um_250_v_8_a_12_v_rm_5_0_mm-8105 (od01b) | 23:33:25 | runner, `fa0dfa3fcea4143d` | "40.52.9.012.0000", "FINDER", "€4.98 incl. 21% VAT", in stock; datasheet link FIN_40_DB_EN.pdf |
| O24 | https://www.reichelt.com/nl/en/shop/search/finder%2040.52 (od01b) | 23:33:00 | runner, `7825e364d17a1a76` | "FIN 95.05", "Relay base for relay Fin 40..", "For FIN 40.51, 40.52, 40.61", "10 A, 250 V", "€4.73 incl. 21% VAT", in stock |
| O25 | makers' sheets filed in the tree (od01b): `v2/vendor/elmwood/honeywell-commercial-thermostats-2455r.pdf` (Honeywell "Commercial Thermostats", 2455R pages 4 and 5), `v2/vendor/finder/finder-40-series-en.pdf` (Finder 40 series, XI-2018), `v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf` (Arcol HS, 12/14.08) | 23:24 to 23:33 | sha256 in each folder's `sources.txt` | the thermostats' tolerance bands (Table 1) and AC-only contact ratings (Table 4); the relay's 8 A and DC1 8 A at 30 V, coil 0.65 W; the HS resistors' ratings, heatsinks and hole sizes |

Refused this host on 28 September 2026: peli.com and pelican.com (HTTP 403, every product URL, 20:40 and 20:42 UTC;
read through the Archive instead), tme.eu (403, 20:45), conrad.nl (403), nl.farnell.com (403), nl.mouser.com (an
"Access Denied" page, 20:45). Their figures are therefore not on this page.

**Case variant, the check's added evidence (m2):** Peli's GB page for the 1450PF (O6) prints "SKU: 1450-300-110E" and "for 1450EU"; Pelican's US page (O7) maps `1450-001-110` to No Foam, Black. Both support the inference that `1450-001-110E` is the 1450EU, no foam, black, and that the frame fits it. Still unresolved: whether the 1450EU is the moulding of drawing 1451-931 (T1 at receipt; the seller's 60-day return covers an older case).

## 6. The monitor and the logger: needed or deferred (moved here from the test brief, which the check found over two pages)

- **Monitor (Xenarc 709GNK): deferred.** No check of test A uses it (H1 is a blank). In test B only row M1 needs its
  real depth: the chain from the face to the heatsinks carries the body's 28.66 mm with no tolerance on the held
  drawing and a rear frame whose drawing is owed (`CASE-MARGINS.md` 3.1). A printed stand-in of the drawing's outline
  and depth serves every other reading of the checks run now (T7, T9 and the lid tray's M3r2.XENARC_WINDOW row need
  the real monitor at the build, and the stand-in carries no rear frame), and with it T4 yields the largest body depth the real monitor may have while
  keeping M1's 2.0 mm. M1, and so board B's layout entry on that row, then closes when the monitor is in hand and its
  body is read with a caliper against that number (no case needed), or when Xenarc states the tolerance. **Buy it when
  board B nears layout entry, not for this package.**
- **Logger: deferred; borrow first.** Test A needs eight type K channels logged together for hours, with cold-junction
  compensation and a file export. Nothing in the procedure needs the PicoLog TC-08 as such: any such logger, or two
  four-channel logging thermometers started together, serves. Before each run, soak all thermocouples together at room
  temperature for 15 minutes and record each channel's offset, so the rises are read differentially. Test B needs no
  logger. Buy the TC-08 (GBP 349) only if no logger can be borrowed.
