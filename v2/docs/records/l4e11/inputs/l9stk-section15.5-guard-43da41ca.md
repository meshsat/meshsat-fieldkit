**THE THERMAL GUARD, as first selected, and restated in round 4** (owners: board A's generator with L4-E11 for the element
beside the battery FETs, board P's generator for the divider). It guards against the installed path never being met, unit by
unit, which a coupon cannot.
- **The part as drafted.** The kit's PRF15BB103 chip PTC, 10 kOhm plus or minus 50 %, 32 V, already on board P as RT1, in the
  enable loop on the battery FETs' copper.
- **The misread, corrected.** This section read "47 kOhm at 130 C plus or minus 3 C" for it. Murata's line-up (DM-SA16-E056
  Rev.1, p.4) prints the 10 kOhm group under the header "at 100 kOhm, at 4.7 MOhm": **100 kOhm at a sensing temperature over
  110 C** (no upper bound) and **4.7 MOhm at 130 plus or minus 3 C**. The 47 kOhm column stands over the 470 ohm groups only.
  Board P's author found it (record l8p's finding L8P-F07) and the check V2 confirmed it from the sheet.
- **The loop as drawn** (nominal). The first inverter stays on while RT1 is under 61.3 kOhm at 10.6 V (115.8 kOhm at 16.8 V)
  and is off from 201.2 kOhm at 10.6 V (337.6 kOhm at 16.8 V). With the tolerances and board A's loads: 58.4 and 110.9 kOhm,
  203.4 and 341.2 kOhm (15.9).
- **The trip side is PRINTED.** Over 4.7 MOhm from 133 C, so the breaker is off before the PTC passes 133 C. A junction leads
  its copper by 1.88 K at 23.93 A at an even split and 2.12 K on the worst split (Rth(j-mb) 1.4 K/W). The copper under the
  hottest FET leads the PTC's site by an amount no record bounds (E-13).
- **The no-trip side is NOT PRINTED.** Under 100 kOhm to 110 C only, and nothing between 110 and 127 C, while the service at
  the allowances reads 118.0 C. The earlier "9.0 to 15.0 K under the band" **does not stand**. On Murata's typical curve
  (which is not this part's own) the guard may open the breaker in the 18 A service: C-PROT's "18 A for 60 s never
  interrupted" is not shown against this guard. **Finding L8P-F07, OPEN.**
- **Round 4's selection (15.9).** A guard whose two sides are both printed replaces the PTC: a factory-set temperature switch
  (no trip under 127.8 C, tripped from 132.2 C) that pulls the loop's return, with a fixed resistor in RT1's place. It is
  drafted by its owners; until that draft is checked, the PTC above is what the drafts draw and L8P-F07 stays OPEN.
- **Restart.** After a trip the breaker restarts through the RC hold when the guard cools.
