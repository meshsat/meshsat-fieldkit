# Quotes, 13 November 2026

Bare-board prices for the carrier board, taken from each maker's public price calculator on 13 November 2026. No account was made, nothing was put in a cart and nobody was contacted. The design files do not exist yet, so every quote is for a stated size and layer count, not for a design.

Board asked for: 100 x 80 mm, 4 layers, FR-4, 1.6 mm, quantity 5 (Aisler: sets of 3).

| Maker | Board price | Shipping | Build time | What the page said | Screenshot |
|---|---:|---:|---|---|---|
| JLCPCB | USD 8.00 for 5 | USD 26.08, UPS Express Saver (DDP), 2 to 4 business days, 0.26 kg | 3 to 4 days | Green mask, default finish. The USD 8.00 is shown as a "Special Offer"; the page says additional charges may apply. | `jlcpcb-2026-11-13.png` |
| PCBWay | USD 32.20 for 5 | USD 26.55, DHL, to the page's default destination (United States), so not the shipping to the Netherlands | 4 to 5 days | FR-4 TG150, 6/6 mil, 0.3 mm holes, green. "Final price is subject to our review." Customs and VAT not included. | `pcbway-2026-11-13.png` |
| Aisler | EUR 45.20 for 3, EUR 76.40 for 6 | not stated in the formula | not stated | From Aisler's published formula, not a calculator screenshot: 4 layers, 1.6 mm, ENIG, "Budget", EUR 14.00 plus EUR 0.13 per cm² per board, boards in sets of 3, excluding VAT (Aisler community forum, "Our Simple Pricing", 27 August 2023). Their calculator needs an uploaded design. | none |

## What these quotes do not cover

- **Assembly.** The calculators price bare boards. Factory assembly needs the design files and a parts list in the maker's format, so it can be quoted only once the board is drawn.
- **Parts.** Priced separately in `../bom.csv`, from JLCPCB's parts table (12 September 2026) and LCSC's listings (13 November 2026), at single-unit prices.
- **Leads.** The JST-GH to USB-C and JST-VH leads between the board and the modules.
- **VAT and import duties.**
