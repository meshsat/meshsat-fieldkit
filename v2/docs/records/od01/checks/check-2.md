# RESULT-2: focused re-check of fnd/od01 at 60187f22 against 78dd3e29 (AI review, independent checker; not a qualified review)

**checkout-ready: no.** It is close. What is left in CHECKOUT-LIST.md is text only:
- a one-cent total;
- the columns of two rows (lines 4 and 8) that were not updated;
- a stale README.

Separately, the new H2 size (a made part, not on the list) cannot carry test A's 42 and 64 W steps inside the brief's
own H2 stop limit. Test A needs that fixed before it runs. Worktree read-only; nothing edited or committed; read
21:30 to 21:40 UTC, 28 Sep 2026.

## Item by item

| Item | Verdict | Evidence |
|---|---|---|
| B1 | **Done, two gaps** | RFQ lines 69 to 71: H1 has FOUR PEM S-M3 in 4.2 holes on 35.0 x 37.0 centred on the PA flange site, and C1 keeps two nuts 60 apart. TEST-BRIEF line 15 bolts the patch resistor to "H1's four S-M3 nuts". Gap 1: RFQ line 64 still says "where a DXF or STEP and the PDF differ, the PDF governs", and sheet 1 (and the H1/C1 STEP and DXF) carry two nuts 60 apart. Add "for H1 this text governs over sheet 1". Gap 2: the pattern has no orientation. Arcol's F 35.0 runs along the resistor's axis and G 37.0 across; state which one runs along the plate's X. |
| B2 | **Done, one gap** | CHECKOUT-LIST line 78 says the line is REMOVED, gives the reason (Raspberry Pi brief, 12.7 mm, passive, no fan, against 21.0 mm and a clip-on cooler with a fan lead) and names the 21.0 mm printed stand-in; TEST-BRIEF test B names it too. Gap: line 78's columns still read "1 \| EUR 4.49 excl. \| Shipping from EUR 4.22 ... \| 75 piece(s) in stock". Blank the quantity, total and shipping columns so nobody carts it. |
| B3 | **One figure still wrong** | Excl. 416.40: agrees (the sum of the rounded lines; unrounded it is 416.405, so 416.41). Incl., case at 21 %: 503.85 agrees. **Incl., case at 25 %: 511.80, not 511.79.** Sellers: 248.33 + 84.00 + 28.22 + 151.25 = 511.80, and unrounded 511.8024. Shipping known: 6.95 + 20 / 0.85785 (23.3141, so 23.31) = **30.26**, agrees. Line 107. |
| m1 | **Totals done; row not** | The totals table (line 106) has Pico at 125.00 excl., 151.25 incl. (21 % import VAT on goods), and GBP 20 registered (23.31) or GBP 30 courier. But line 82's own columns still read "\| 10 \| GBP 105.00; EUR 122.40 ESTIMATE \| not shown \|". Set them to EUR 12.50 each, EUR 125.00, and GBP 20 registered / GBP 30 courier as stated by Pico. |
| m2, m9 | **Done** | The case evidence (Peli GB O6 "SKU: 1450-300-110E"; Pelican US O7 `1450-001-110` = No Foam, Black) is at the end of the list's section 5. Multi-Cases.nl is in the alternatives paragraph (line 85), with its VAT basis marked as not read. |
| m3 | **Done as asked, but the size is too small (blocks test A)** | RFQ line 23: H2 at 200 x 150 x 3.0, heaters bolted with compound. See the section below. |
| m4 | **Done** | pandoc with xelatex, `-V geometry:a4paper,margin=2cm -V fontsize=10pt`: **2 pages** with the default font and 2 pages with DejaVu Sans. |
| m5 limits | **Done** | TEST-BRIEF line 63 lists wall 70 C, H1 edge over the o-ring 70 C, H2 100 C, heater body 150 C (one thermocouple on one heater), patch 110 C, plus a 6.5 A limit, fused leads and hourly checks or logger alarms. |
| m5 lead exit | **Valid for the purpose, with two corrections** | See the section below. |
| m6 | **Done** | CHECKOUT-LIST section 6 now says the stand-in "serves every other reading of the checks run now" and that T7, T9 and M3r2.XENARC_WINDOW need the real monitor at the build, and the stand-in carries no rear frame. |
| m7 | **Done** | TEST-BRIEF line 13: "3 h or more; ... about 50 min, INFERRED". Line 19's "about 2 days" for six steps is consistent. |
| m8 | **Done, but one saw lost** | Line 41 now lists hole saws of 29, 22 and 18 mm, drills of 8 and 4.5 mm and a step drill. **The 27 mm hole saw for the end walls' arrestor holes was dropped** (sheet 4: "dotted: the 27 mm wall hole"). Put it back, and add a 5.0 mm drill for the entry plates' M4 wall holes (M11e: "its 5.0 wall hole"). |

## m3: why H2 at 200 x 150 x 3.0 is too small (INFERRED, this checker's estimate)

Method:
- Heated flat plate in still air: upward face h = 1.52 dT^(1/3), downward face h = 0.59 (dT/L)^(1/4).
- Radiation from bare aluminium at emissivity 0.1.
- Inside air, lid closed, fans off: +10, +20 and +30 K over a 25 C room (the record's 2.1 W/K).
- The heaters' own fins are ignored, and so is the hotter air near H2.

| H2 | 21.2 W | 42.4 W | 63.5 W |
|---|---|---|---|
| 200 x 150 x 3.0, bare | about 97 C | about 150 C | about 195 C |
| 330 x 200 x 3.0 (board B's outline, zstack.json `/boards/b/outline` +-165 x +-100), bare | about 69 C | about 103 C | about 133 C |
| 330 x 200 x 3.0, black (emissivity about 0.9) | about 52 C | about 74 C | about 93 C |

At 200 x 150, the 42 and 64 W steps trip the brief's own H2 stop at 100 C and, through the heater bodies, the 150 C
stop. At 64 W, H2 nears the HS50's 200 C hot spot.

Recommendation:
- Make H2 at the stack's outline, 330 x 200 x 3.0. The procedure spreads the heat "on a dummy stack", and READY-TO-ACT 5.2
  says "at the stack's outline".
- Make it matt black, anodised or painted. That is also closer to FR4 boards than bare aluminium.
- Spread the heaters over it.
- Put the H2 thermocouple next to the hottest heater.

Fix: RFQ line 23 and TEST-BRIEF lines 12 and 61. This does not touch the checkout list.

## m5: the lead exit

Peli's customer drawing 1451-931 (15 Jan 2025, held) shows the "AUTOMATIC PRESSURE EQUALIZATION VALVE" on the base's
front wall. It opens into the heated volume under H1.

**Under the gaskets is valid for the test's purpose, and preferable to the gland.**
- Leakage heat: one small opening at one place gives buoyant exchange of the order of milliwatts, against about 63 W at
  64 W and 2.1 W/K.
- Conduction along six copper leads of 0.75 mm2 over about 0.3 m: about 0.006 W/K, against 2.1 W/K (0.3 percent).
- So the bias is HIGH in sign, as the brief says, but negligible (INFERRED). The brief should say "negligible, well under 1
  percent" rather than presenting it as the price of the route.

Two corrections:
1. **It names the wrong seal.** The heated volume is the base under H1, sealed by the 1450PF's o-ring under H1's edge (T3;
   kit "1 o-ring"). The leads must pass between H1 and that o-ring, and, lid closed, also under the lid gasket. The brief
   (line 68) names only the lid gasket.
2. **Place the exit on a straight run of each seal, not "at one corner"**, where the o-ring turns. Use the thinnest flat
   conductors that carry 5.3 A. Confirm that H1's screws still seat it and that the lid latches without force.

**The purge-valve gland is not "reads it right".**
- It removes the case's pressure equalisation, which the design keeps (appendix 32.53 item 1: "Peli's own pressure
  equalisation valve stays").
- Sealed, the base air heated by about 35 K rises about 12 percent in pressure, about 12 kPa. That is about 1.2 kN on H1's
  0.099 m2, which is held by ten hand-tight 6-32 screws in Peli's inserts (INFERRED).
- The test would then no longer be the design's case.
- The valve port's thread is on no held sheet.

## Also still wrong

- README.md line 9 still says "eight priced lines from five sellers", "EUR 418.29 excl. VAT and EUR 514.09 incl. (EUR
  506.14 ...)" and "EUR 11.17 known, three sellers not shown". It should now say seven lines, four sellers, 416.40 /
  511.80 / 503.85, and 30.26 known with two sellers not shown.
- README.md line 28 still says "Kiwi's page gives SC1752 as 12.7 mm". Raspberry Pi's brief states it, and line 4 is removed.

## Recomputed totals

| Figure | Coordinator | Checker |
|---|---|---|
| Excl. VAT, lines 1 to 8 (line 4 removed) | 416.40 | 416.40 (rounded lines; 416.41 unrounded) |
| Incl., case at 25 % | 511.79 | **511.80** |
| Incl., case at 21 % (ESTIMATE) | 503.85 | 503.85 |
| Shipping known | 30.26 | 30.26 (reichelt 6.95 "from", Pico GBP 20 at 0.85785 = 23.31 ESTIMATE); flight-cases.eu and PolyPhaser not shown |

The ECB rates for 28 Sep 2026 are the same file as before: USD 1.1378, GBP 0.85785.

## To reach checkout-ready: yes

1. CHECKOUT-LIST line 107: 511.79 -> 511.80.
2. Line 78: blank the quantity, total, shipping and stock columns.
3. Line 82: EUR 12.50, EUR 125.00, and Pico's stated freight in its columns.
4. README lines 9 and 28.

Before test A runs, also fix:
- H2's size and finish (RFQ line 23; brief lines 12 and 61);
- the seal the leads pass (brief line 68);
- the H1 note and orientation (RFQ lines 64 and 69);
- the 27 mm saw and the 5.0 mm drill (brief line 41).
