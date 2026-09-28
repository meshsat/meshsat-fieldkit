# Stream od01: the minimum physical test package for one prototype case (owner ruling D-19, OD-01)

MESHSAT-1357, 28 September 2026. Prepared by an AI session. The MeshSat field kit V2 is an unbuilt prototype design:
nothing here has been bought, made, fitted or measured, no seller or shop has been contacted, and no account, basket or
checkout was used. Buying these parts closes no measurement gate; only the tests' readings do.

| File | What it is |
|---|---|
| `CHECKOUT-LIST.md` | The case variant confirmed from Peli's pages (the seller sells the 1450EU; Peli states the 1450PF is for the 1450EU) and the one list: eight priced lines from five sellers, each with its part number, page, price and VAT status, quantity, shipping to the Netherlands as stated, stock and the UTC moment read; totals EUR 418.29 excl. VAT and EUR 514.09 incl. (EUR 506.14 with the case at the Dutch rate), conversions labelled ESTIMATE; shipping as a separate line (EUR 11.17 known, three sellers not shown); the monitor and the logger deferred with the reason; the sources table |
| `MACHINING-RFQ.md` | The request for quote for the made parts (H1 heat-test blank, C6 legs, C1 face plate, C4 entry plates, C3 connector plate, optional gaskets, dummy blocks, the QMX lid plate), the files to upload by path and sha256, what the quote must state, the two routes (JLCCNC upload, a local workshop). NOT SENT. The lid tray r2 is printed, not machined |
| `TEST-BRIEF.md` | The operator's brief: the heat test first, then the mock-up's checks; what each decides and which board gate it lifts; the competence and equipment; the time; what is recorded and how the results reach the session; safety; the monitor and logger answer |

## What remains the owner's

1. **Ordering**, seller by seller from `CHECKOUT-LIST.md` section 2, reading each seller's freight and VAT at checkout
   (not shown on any page read). Optionally first the prepared question to the seller of the case (section 1: the
   variant, the production date on the date wheels, the freight). The seller's 60-day return right covers a case of an
   older moulding, which check T1 finds at receipt.
2. **The machining quotes**: send `MACHINING-RFQ.md` section 3 with the files of its section 2, by upload or to a shop;
   approve one. H1 and C6 come first (the heat test needs them).
3. **Assigning the operator** against `TEST-BRIEF.md` sections 2 and 3, and borrowing a logger if one can be borrowed.

## What remains open for the session (no money involved)

- The jumper plug pick (M17g, M17x): until it is made check T10 cannot run and the T10 rows of boards B and E stay open.
- The fan pick (the mixer fans' speed code; the cooler fans, D-18): until then the heat test runs fans off only.
- The pack hold-down (S-27): it sets the dummy pack block's outline (H3) and lets T4 read M4a and M5 for boards A and P.
- The heatsink pick: Kiwi's page gives SC1752 as 12.7 mm tall while M1's chain carries 21.0 mm; which cooler the kit
  uses decides what T4 measures.
- Prices not found in the time box: 3M VHB 5952 and 6-32 x 1/2 in pan-head screws (TBD by quote).
- A drawing of H1 of its own would be cleaner than the layer instructions in the request (the case writer's, optional).
