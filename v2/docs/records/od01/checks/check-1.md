# RESULT: check of fnd/od01 at 78dd3e29 (AI review, independent checker; not a qualified review)

**checkout-ready: no.** Three blocking items, all fixable in text or in H1's drawing. All eight part numbers exist at the
prices, VAT status and stock the author read (re-read 21:00 to 21:07 UTC, 28 Sep 2026, none moved). Full record: the checker's scratch clone (not filed; its paths generalised on filing, 29 September 2026). Pages
fetched were kept there.

## Blocking
- **B1, incompatibility (line 6 against H1).** Arcol HS sheet 12/14.08, page 2: the HS100 fixes by four holes (Ø 3.2 max)
  on 35.0 x 37.0 mm (diagonal 50.9). H1 (RFQ; face-plate sheet 1, "PA flange: 2 x PEM S-M3 (4.2) 60 apart, underside")
  offers two M3 nuts 60 mm apart, and TEST-BRIEF test A bolts the patch block to them. That cannot be done. Fix: give H1
  four S-M3 on 35.0 x 37.0 at the PA flange site (H1 serves only the heat test). Line 6 can stay.
- **B2, compatibility not shown (line 4, SC1752).** Raspberry Pi's own product brief (December 2024, p. 3,
  datasheets.raspberrypi.com/cm5/cooler-product-brief.pdf, read 21:03 UTC): "56 mm x 41 mm x 12.7 mm". It is passive,
  screwed from below, with no fan. M1's chain carries 21.0 mm, and `ASSEMBLY.md` lines 63 and 152 describe a clip-on cooler
  with a fan lead. Used at T4 it would make the monitor-depth limit up to 8.3 mm too generous. Fix: drop the line
  (EUR 4.49) until the heatsink pick, or relabel it as a stand-in that does not serve M1. Also, the author's "a seller's
  figure, not a Raspberry Pi drawing" is wrong: Raspberry Pi states 12.7 mm itself.
- **B3, arithmetic (section 3).** With the case at 21 %, the incl.-VAT total is EUR 506.13, not 506.14. With the case at
  25 %, the author's own rounded lines sum to 514.08. The stated 514.09 comes only from unrounded conversions. One cent
  each.

## Minor
- m1. Pico bills "in your selected currency (GBP, Euro or USD)", and SE001's EUR price is 12.50. That makes line 8
  EUR 125.00, not the ESTIMATE 122.40. Pico's how-to-order page states Europe delivery at GBP 20 (about EUR 23) registered
  or GBP 30 courier. Import duties and taxes are the receiver's. The list says "not shown".
- m2. Peli GB (O6) prints "SKU: 1450-300-110E" for the 1450PF "for 1450EU". Pelican US (O7) maps `1450-001-110` to No
  Foam, Black. Cite both: they settle the frame and strengthen the case inference.
- m3. H2 has no size. The HS50 is rated only 14 W with no heatsink, so each 21.2 W heater must be bolted with compound to
  a stated plate, or a heater-body thermocouple added.
- m4. TEST-BRIEF renders to 3 A4 pages (pandoc and xelatex, 10 pt, 20 mm margins), over the two-page limit.
- m5. Safety gaps:
  - no heater-body temperature is stated (about 120 C in a closed case, INFERRED from 3.0 K/W);
  - no stop limit on the heaters or H2, nor at H1's edge over the frame's o-ring;
  - the brief does not say how the leads leave the sealed case.
- m6. The monitor stand-in serves every check run now (only M1 carries the monitor). T7, T9 and `M3r2.XENARC_WINDOW` need
  the real part at the build, and the Xenarc rear frame is not in a printed body.
- m7. "About 2 h per step" is likely short. The empty case alone is 2.5 kg (seller), so the time constant is about 50 min
  at 2.1 W/K and steady takes 3 h or more (INFERRED).
- m8. Name the back-wall hole sizes (29, 22, 18, 8, 4.5) in the equipment list.
- m9. A Dutch seller, Multi-Cases.nl, lists `1450-001-110E` ("Vanaf: EUR 158,00", in stock) and `1450-300-110E`
  (EUR 31,00). Its VAT basis was not read.
- m10. The reichelt lines cite search pages, not product pages.
- m11. PEM S-M3 are nuts, not studs.
- m12. Buying thermocouples with miniature plugs before the logger is chosen risks needing adaptors.

## Passed
- **Case:** `1450-001-110E` is the 1450EU, no foam, black. This is INFERRED from Peli's numbering on two Peli pages, the
  seller's name and figures, and a second seller. Peli's SKU page refused this host.
- **Frame:** `1450-300-110E` is the 1450PF kit for the 1450EU (VERIFIED, Peli GB).
- **Arrestor:** GTH-SFF-AL is SMA female to female, bulkhead, DC to 6 GHz, as `CASE-MARGINS.md` C2 and `READY-TO-ACT.md`
  6.3 name it.
- **Heater powers:** 21.18 W and 1.76 A each at 12.0 V. The patch block gives 45.00 W at 9.95 V and 82.84 W at 13.5 V
  (6.14 A), inside the HS100's 100 W rating on H1. H1 has practically Arcol's standard heatsink area (992 cm2 at 3 mm).
  Derated at a +50 C plate the rating is about 86 W.
- **Thermocouples:** SE001 is type K with a miniature flat-pin plug, which the TC-08's miniature inputs take.
- **Logger deferral:** drawn from the procedure.
- **RFQ:**
  - all 21 upload sha256 values, the two STL files and the Xenarc drawing equal the tree's;
  - the manifest reads 50 OK;
  - the release and procedure files are unchanged on main (4f1217f1);
  - the numbers agree with sheets 1 to 4.
- **Nothing sent:** both files say so.
- **Prose:** no dash characters, prototype framing throughout, and every list price carries its page and UTC time.

## Totals

| Figure | Author | Checker, author's basis | Checker, Pico at its EUR price |
|---|---|---|---|
| Excl. VAT | 418.29 | 418.29 | 420.89 |
| Incl., case at 25 % | 514.09 | 514.08 (rounded lines) | 517.23 |
| Incl., case at 21 % (ESTIMATE) | 506.14 | 506.13 | 509.28 |
| Shipping known | 11.17 | 11.17 | about 34.17 |

ECB reference rates, 28 Sep 2026 (the same file the author read): USD 1.1378, GBP 0.85785.

## Could not read
- Peli's `1450eu?sku=1450-001-110E` page: HTTP 403; its Archive copy answered 404, and the Archive index was offline at
  21:06.
- raspberrypi.com product pages: HTTP 403.
- PolyPhaser's shipping to the EU: no page found.
- Freight at flight-cases.eu: shown only in a basket, which was not used.
- Multi-Cases.nl's VAT basis.
- vonkbv.com: HTTP 429.

I edited or committed nothing in any worktree. I wrote only in the checker's scratch clone.
