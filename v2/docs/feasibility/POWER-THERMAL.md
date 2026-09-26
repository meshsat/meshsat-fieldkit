# MeshSat field kit V2: power and thermal feasibility

**Status: PROVISIONAL.** Written 26 September 2026 for MESHSAT-1357, executing section 4 of the review of the 26 September
progress report (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`). Prototype design: nothing in this kit has
been built, powered or measured, and no figure below is a measurement. Every number is one of: a primary document read
by this stream (VERIFIED, with its clause), arithmetic on such numbers (INFERRED, with the arithmetic), a design
declaration in a generator (DECLARED), or TBD with the effect of not knowing it.

**Revision this page describes.** Every citation is anchored at `main` `01469100` (fifth cycle). `main` moved from
`b69f20db` to `01469100` while this cycle ran; of the files this page cites by line, only `gen_sch_p.py` changed
(board P's second-level over-temperature, `d90f30e4`), and its lines are re-pointed. The battery stream's review
packet (`v2/docs/review-packets/battery/`) arrived in the same commits and is cited where it bears on PWR-F12. The
model computes every board as generated at `1f614233`. Since then `458b2873` merged the round-4 and round-6
corrections of boards A, B and D, among them the two candidates earlier cycles named: board A's (`fnd/r4a`: F-PR-01,
F-PR-04, S-04, S-14, S-20, F-SQ-06) and board B's (`fnd/r4b`: F-PR-05). `main`'s `gen_sch_a.py` and `gen_sch_b.py` are
byte-identical to those two candidates. `b69f20db` changed no generator (it records the case margins, appendix
32.367). Where the merge changes a power figure the page gives both, "at `1f614233`" and "on `main`". The one change
that moves a D-11 floor, board A's charge shunt R17 in the pack's discharge path (S-04), is computed in sections 1 and
7.2. The requirements registry (`fnd/i1`: REQ-014, REQ-018, CON-019) and `ARCHITECTURE.md` (`fnd/i3`) are still
pending merge, and a candidate is not the design until it merges.

**The model.** `drafts/pwr_budget.py` (stdlib, under a second; its full output is `drafts/pwr_budget.out` and
`drafts/pwr_budget.json`) computes every table here. It replaces the W2 round-2 model whose figures `CONOPS.md` section
4a carries on `main`. The documents this stream fetched are in `drafts/datasheets/`, listed with URL, date and sha256
in section 12. Both are drafts for the integrator to file (proposal in section 11).

## 0. What this page establishes

1. **The undocumented share of the budget is down from about half to about a fifth, and the budget went up.** Six
   of the eight loads the review named now carry a maker's figure or a maker's bound; the camera and the Geiger module
   are bounded only by their port and switch declarations (section 2). On the same state
   definitions, the planning figures at the pack terminals become PS-IDLE 39.7 W (was 29.4), PS-IDLE-SPEC 42.8 W (was
   32.4), PS-TYP 63.0 W (was 60.1) and PS-ALLTX 203.8 W (was 227.0). The loads with no document at all now carry 8.4 of
   42.8 W in PS-IDLE-SPEC and 11.7 of 63.0 W in PS-TYP. A further 11.3 and 21.0 W sit inside a maker's bound at an
   assumed duty or workload (section 4). PS-BUSY, TBD on `main` for want of duty cycles, is bounded at 92.0 W
   (54.6 to 134.4 W) as a sustained case with its transmitters at full duty.
2. **The two idle figures are two scenarios at the same boundary, not a defect.** Both 29.4 W and about 32 W are
   battery-terminal figures. The difference is the monitor at 6 W instead of 4 W plus 0.9 W of APRS beacons on the PA
   rail (section 5).
3. **Runtime at +20 C on an aged (80 percent) 4S3P pack is 2.5 h in PS-IDLE-SPEC and 1.7 h in PS-TYP.** The documented
   bounds are 1.3 to 3.3 h and 0.9 to 2.3 h. The derating chain is in section 6. None of this is a requirement value:
   REQ-014's "aged" is still TBD.
4. **D-11's thresholds, and the same rules for the PA keyed on its own, are set, PROVISIONAL, by the session under
   the owner's standing rule of 26 September 2026** (section 7.2).
   - All-transmit is allowed only above a pack rest voltage of 15.5 V (3.88 V per cell). The PA keyed on its own,
     with the other transmitters idle, is allowed only above 12.4 V (3.10 V per cell).
   - Every PA key-down lasts at most 60 s and starts only with every cell at most +55 C and the PA's flange at most
     +75 C. It runs with the outlets, the pack heater and the standby WiFi card off, and an in-key guard ends it
     early above 18 A, at a low cell, or at +85 C on the PA's flange.
   - The design record carries two key-down figures: 32.53's "lasts minutes" for the 200 W peak into 8 to 10 kJ/K
     (appendix line 2860), and 32.56's "20 s key-down at 45 W" that warms the plate's local patch under the PA's
     flange by about 15 K (line 2940). The 60 s sits between them: it tightens the first and is three times the
     second.
   - On the record's own patch figure, taken linear in time (INFERRED; spreading lowers it), a 60 s key-down from a
     +50 C plate ends past the PA maker's 90 C reliability figure at 45 W of heat and past its +100 C case rating
     at 68 W, before the flange interface. So on the PA side the 60 s holds only with the flange reading, which no
     board carries yet (PWR-F15).
   - The basis is the gauge's 20 A over-current trip with 10 percent margin, and the cells' 60 C discharge window.
   - The distribution resistance carries the chemical fuse F2 (third cycle). On the boards as generated at
     `1f614233` the all-transmit basis case needs 15.22 V, with 0.28 V of stated margin. On `main`, whose pack path
     also carries board A's 5 mOhm charge shunt R17 since `458b2873`, it needs 15.31 V, with 0.19 V of margin. With
     the heater on it would need 15.79 V, which is why the heater is off during a key-down.
   - **A key-down near 18 A is above the chain's declared 10 A continuous current. So it holds only once the chain
     is re-declared with a short-time rating, board A's pack-node copper is judged at it, and the chemical fuse F2 is
     shown inside its +60 C operating rating at it (PWR-F12).**
5. **The +35 C and +25 C restrictions are proposed controls, not established limits.** With this page's heat per
   state, even the design record's own enclosure conductance puts the charge hold-off for three typical modules at
   +19.5 to +21.6 C, not +25 C. The independent bound puts it anywhere from -18 to +19 C. On that bound, three typical
   modules at +20 C put the cells anywhere from 45 C to 81 C, past their 60 C discharge limit. The hot end is
   undecided until the enclosure conductance is measured. Section 9 proposes controls driven by measured current and
   temperatures, and section 10 an early heat-balance test.
6. **Two bought parts are outside the adopted envelope, and neither is in `pcb_part_temps.yaml`:** the AW7915-AED WiFi
   card (0 to +70 C, or -10 to +70 C on the maker's current page) and the LimeSDR Mini v2.4 (0 to +70 C operating
   *and* storage). The NVMe drive, not yet picked, has to be a -20 C grade (section 9.4).
7. **Not every combination the design can switch on is a sustained mode on battery.** Each combination section 7.1
   lists was checked against the declared 10 A continuous pack current and the cells' 60 C discharge and 45 C charge
   windows at +20 C:
   - PS-TYP with both outlets draws 10.4 A at 14.4 V and puts the cells at 69 to 71 C, even on the design record's
     own conductance.
   - PS-BUSY puts them at 58 to 61 C.
   - The PA keyed on its own over PS-TYP draws 10.0 A at 14.4 V and 14.6 A at 10.0 V. At the PA's 113 W upper bound
     it passes 18 A below a 10.42 V stack. It is a bounded key-down, not a sustained mode.
   All three now carry a control, taken by the session: an outlet budget, a current trigger for the module shedding,
   and the key-down rules of section 7.2. They are driven by the gauge's pack current and its four cell thermistors
   (section 9.3). A gauge backstop is proposed to the battery stream. What the controls cost the operator is PWR-F13.
8. **The chemical fuse F2 is the one protective part whose margin during a key-down is unknown.** It sits at the
   block's temperature, is rated -20 to +60 C with no current derating published, and dissipates 0.32 to 0.81 W of
   its own at 18 A (section 7.2). Its opening would end the pack. The gauge's Safety Overcurrent in Discharge would
   also fire it on most key-downs longer than 5 s if the golden image enabled it at its default of 10 A for 5 s.
   PWR-F12 keeps that permanent failure off, and adds a reading of F2's body to the protection test.

## 1. Conventions

- **Power states** are `CONOPS.md` section 4a's (lines 237 to 247). This page keeps their definitions and applies
  three rules from the architecture that the W2 model did not:
  - **Only one WiFi link card is live** (`ARCH-PCB-B-IOHA.md` line 209, and line 324: card 2 is "standby, radio
    disabled").
  - **The reduced mode's one module is slot 3**, because the LoRa mesh the owner named for it (D-02b) is on slot 3's
    SPI (`V2-SPEC.md` line 32).
  - **The two mixer fans run in every powered state**, lid open or closed, because the fans-on conductance of appendix
    32.53 assumes them.
    The W2 model had them off in PS-IDLE. This choice was taken by the session under the owner's standing rule of 26
    September 2026.
- **Three values per load and per state**, in watts at the load's own supply pins:
  - **LOW** is the lowest figure a document supports, or else the planning value;
  - **PLAN** is the headline figure;
  - **HIGH** is the highest figure a document supports: a maker's maximum, a port contract or a declared peak.
  HIGH puts every load at its maximum at once. It is an upper bound, not a scenario.
- **Tier of PLAN:**
  - **S**: a primary document gives the number.
  - **R**: a primary document bounds the load, and PLAN sits inside that bound by a stated duty or workload assumption.
  - **D**: a declaration in a generator.
  - **T**: a placeholder with no document.
- **Conversion boundaries.** "At the loads" is the sum of load-pin watts. "At VBAT" adds each converter's loss. "At
  the pack terminals" (battery W) adds 22.5 mOhm of distribution I2R:
  - VERIFIED: three 2.52 mOhm blades, two 0.69 mOhm FETs, the 2 mOhm shunt, and the chemical fuse F2 at the top of its
    1.0 to 2.5 mOhm (Eaton ELX1135, Product specifications, read in `fnd/r4p`'s filed copy; quoted in `gen_sch_p.py`
    lines 273 and 274);
  - INFERRED: about 9 mOhm of lead and contacts (W2 assumption A10, whose 20 mOhm predates F2; F2 is added in the
    third cycle, at its maximum, the conservative direction for every limit here).
  - **On `main` since `458b2873`, 5 mOhm more.** Board A's charge-current shunt R17 ("5mOhm 1% 2512", a 3 W part)
    now carries the pack's discharge current too, because S-04 moved the loads to the charger's system side
    (`gen_sch_a.py` lines 26 to 37 and 716 to 722). It dissipates 1.62 W at 18 A. The tables keep 22.5 mOhm, the
    boards as generated at `1f614233`. At 27.5 mOhm, battery W rises by at most 1.92 W, the pack current at 10.0 V
    by at most 0.47 A, and the inside air by at most 1.6 K on the lowest conductance. Every "stack voltage below
    which" figure of section 7.1 moves up by 0.05 V at 10 A and 0.09 V at 18 A (`drafts/pwr_budget.json`
    `d11.main_pack_path_R17`). The D-11 floors are re-solved with it in section 7.2.

  The pack's own fuses, FETs and shunt are inside those 22.5 mOhm, so "the pack terminals" here means the cell stack
  under load. "At the dock input" divides battery W by the charger and front end (section 5).
- **Pack current** is solved at the stack voltage, V x I = W at VBAT + I² x 22.5 mOhm, so the distribution drop is
  counted once (sections 7.1 and 7.3).

## 2. The dominant undocumented loads, now sourced or bounded

The W2 table left 29.7 of PS-TYP's 60.1 W on loads with no document (`CONOPS.md` line 241). This table takes those
loads roughly in order of their battery-side share in PS-TYP.

| Load (count) | W2 placeholder at the load | Now | Source (clause) | Tier |
|---|---|---|---|---|
| AW7915-AED WiFi link card (2) | 1 W idle, 3 W typical, 10 W peak per card | **live card: 4 to 8 W average, 9 W maximum (maker's page), or 7 W average and 9.1 W maximum (maker's 2023 PDF)**. The supply design must give 3.3 V at 3 A (2.5 A minimum) per the page, or 3.5 A (3 A minimum) per the PDF. There is no idle or radio-disabled figure. PLAN is 4 W for an idle link, 6 W typical and 9.1 W transmitting. The standby card is T: 1 W, bounded above by 9.1 W, and 0 W if its module holds PCIE_PWR_EN low. | AsiaRF product page, fetched 26 Sep 2026 (`drafts/datasheets/asiarf-aw7915-aed-product-page.html`); AsiaRF `AW7915-AED_V1.pdf` v1.0, 2023-08-17, Specifications. The in-tree one-page datasheet (`v2/vendor/wifi/asiarf-AW7915-AED-datasheet.pdf`, 2026) gives no power figure. | R (live), T (standby) |
| Xenarc 709GNK monitor | 4 W dimmed, 6 W on | **at most 10 W; no typical figure published** (operating voltage 10 to 35 V) | `xenarc-709gnk-product-manual-v2.pdf` specifications; xenarc.com/709GNK.html fetched 26 Sep 2026 | T, bounded 10 W |
| NVMe 2242 (3), no part picked | 0.3 W idle, 1 W typical, 4 W peak | **idle 0.90 to 1.05 W; active 2.6 to 3.6 W** (both at 3.3 V, Gen3 x4) for two industrial 2242 drives taken as representatives. Neither sheet gives an APST or L1.2 figure. | Advantech SQFlash 720-D DS v1.9 (2024-07-09) section 9; Cervoz T405 DS Rev 2.0 (file dated 28 Jul 2025) section 2.1 | S idle, R typical |
| LimeSDR Mini 2.4 | 3 W typical | **"Maximum Power 4.5 W, USB 3.0 power limit"; "power consumption depends on configuration"**. The host must supply 5 V at 900 mA. PLAN 3 W stays T. | LimeSDR Mini v2 documentation v2.4, Introduction and Hardware Setup (last updated 8 Jun 2026), fetched 26 Sep 2026 | T, bounded 4.5 W |
| KSZ9897R Ethernet switch | 1.8 W lumped at 72 % | **2.54 W at the part** with all ports at 1000 Mb/s and 100 % utilisation: AVDDH 330 mA at 2.5 V, VDDIO 80 mA at 3.3 V, AVDDL 460 mA plus DVDDL 750 mA at 1.2 V. **0.37 W** in energy-detect mode. Typical at 25 C; no maximum published. | Microchip DS00002330D Table 6-1 (`v2/vendor/microchip/microchip-ksz9897-datasheet.pdf`, sha256 72b89179ed6a42a7) | S |
| slot cooler fans (3) | 0.5 W each | **0.36 to 0.56 W** for Sunon's 30 x 30 x 6 mm 5 V fans (MF30060V2, MF30060V1), representative only: they are not IP68, and the pick waits on D-18. Declared 0.1 A (`gen_sch_b.py` line 46). | Sunon catalogue 240-A p. 16 (extract in `drafts/datasheets/`) | R |
| mixer fans (2) | 0 W idle, 0.7 W each typical | **0.39 to 1.50 W each** at 12 V for Sunon's 60 x 60 x 15 mm IP68 range (GF60151B9 to B6). On CELL_F they see 10 to 16.8 V, so power above 12 V is INFERRED higher. Declared 0.1 A each (`gen_sch_e.py` line 34). | Sunon catalogue 240-A p. 38 | R |
| camera (part TBD) | 1 W typical | **0 to 2.5 W**, bounded by its port contract of 0.5 A at 5 V (`gen_sch_b.py` line 233) | design contract | T, bounded |
| Geiger module | inside E's 0.8 W | **up to 0.5 W** by the load switch declaration (`gen_sch_e.py` line 142). RadiationD-v1.1 class (`open-picks.txt` line 22); no maker sheet exists. | DECLARED | D |
| three STM32H743 supervisors | inside "B logic" 1.5 W at 59 % | **33 mA at 200 MHz VOS3 with peripherals off; 71 mA at 400 MHz VOS1 with peripherals off; 165 mA at 400 MHz with all peripherals on (typical); 400 mA maximum at TJ 85 C**. PLAN takes 71 mA per controller plus its 0.06 A of other parts. | ST DS12110 Rev 10 Table 30 (`st-stm32h743xi-datasheet.pdf`) | R |
| three TUSB8041 hubs | 0.1 W idle, 0.5 W typical each | **0.04 W disconnected; 0.35 W with a 2.0 host and four HS devices; 0.72 W with one SS device in U0 plus one HS; 1.02 W with four SS devices in U0** | TI SLLSEE4E section 7.7 | R |
| PCIe switch (3) | 0.62 W lumped | **3.3 V rails 355 mW typical, 390 mW maximum; 1.0 V rails 270 mW typical, 676 mW maximum** | Diodes DS40068 Rev 5-2 Table 12-8 | S |
| E72 (2) | 0.26 W declared | **RX 7.3 mA, TX 106 mA at 3.3 V** | Ebyte E72-2G4M20S1E manual 2.2 | S |
| RM520N-GL 5G | watts taken at 3.3 V | the same currents at the table's own 3.7 V condition: idle 0.22 W, RF disabled 0.017 W, LTE CA 5.59 W | Quectel RM520N series HD v1.1 Tables 42 and 43 | S |

Still with no document (tier T in PLAN):
- the monitor's typical power;
- the LimeSDR's receive-only power;
- the camera;
- the standby WiFi card with its radio disabled;
- the APRS beacon interval (0.9 W average at 75 W input means one 1 s key every 83 s, a planning placeholder);
- the duty cycles behind every R row.

Section 10 drafts the maker questions that would close three of these; the rest close on the bench.

## 3. Conversion losses per rail, from the converters' own datasheets

Each efficiency is read off the maker's plot at the output current that state asks of the converter (points in the
model), then interpolated linearly in input voltage between the two plotted curves:
- PLAN uses the pack at 14.4 V;
- LOW uses 12 V (the better case for these bucks);
- HIGH uses 16.8 V, the full pack, which is the worst point of the pack range.

The plots are the maker's typical curves on its own evaluation parts at 25 C. Applying them to this design's parts
and switching frequency is INFERRED. Board A's LM5176 stages run at 206 kHz with different FETs (`fnd/r4a`
`r4-open-items.md` item O-04).

| Rail (part) | Plot used | PS-IDLE: current, efficiency PLAN (LOW to HIGH) | PS-TYP | PS-ALLTX | Declared floor |
|---|---|---|---|---|---|
| +5V_S1..3 (AP64500) | DS41979 Rev 5 Fig. 4 and 5, VOUT 5 V | S1 1.71 A, 0.926 (0.935 to 0.921) | S1 2.68 A, 0.929 | S1 4.65 A, 0.911 | 0.90 |
| +5V_DEV (AP64500 at `1f614233`; an LM5176 stage on `main`, below) | same | 2.18 A, 0.930 | 3.44 A, 0.923 | **5.89 A on a 5 A part**, 0.908 | 0.90 |
| slot card and NVMe 3.3 V from 5.1 V (AP64500) | Fig. 4, VOUT 3.3 V at VIN 12 V: NOT PLOTTED at VIN 5 V, used as the conservative case | card 1: 1.21 A, 0.904 | 1.82 A, 0.913 | 2.76 A, 0.911 | 0.88 |
| +3V3_DEV (AP63203 from 5 V) | DS41326 Rev 3 Fig. 4, VOUT 3.3 V at VIN 12 V: NOT PLOTTED at VIN 5 V | 1.15 A, 0.913 | 0.912 | 0.904 | 0.88 |
| board E 5 V (AP63205 on CELL_F) | DS41326 Rev 3 Fig. 4 and 5 | 0.21 A, 0.916 | 0.916 | 0.916 | 0.88 |
| +13V8_PA (LM5176) | SNVSAI1D Fig. 6-2, VOUT 12 V | off | off | 5.43 A, 0.983 (0.986 to 0.980) | 0.93 |
| +12V_HF (LM5176) | same; 0.08 A is below the lowest plotted point (0.2 A at VIN 12 V), so that point is used and the figure is optimistic | off | 0.08 A, 0.848 | 1.0 A, 0.961 | 0.93 |
| 1.0 to 1.2 V cores (TPS62933) | SLUSEA4D Fig. 10-2 plots VOUT 5 V only: NOT PLOTTED | 0.85 declared | 0.85 | 0.85 | 0.85 |
| board A +3V3 (TPS62933) | NOT PLOTTED | 0.88 declared | 0.88 | 0.88 | 0.88 |
| +54V_POE, PD outlet (LM5176) | NOT PLOTTED | off | off | off (D-11 interlock) | 0.88, 0.93 |
| LDOs: KSZ AVDDH 2.5 V from 3.3 V; supervisors 3.3 V from 5.1 V; board E 3.3 V from 5 V | Vout / Vin, exact | 0.758; 0.647; 0.66 | same | same | 0.76; 0.66; 0.66 |
| BQ25731 charger (charging only) | SLUSE66A Fig. 8-4, VIN 20 V, VOUT 14.8 V | | about 0.98 at 2 to 6 A | | |

**Total conversion loss at PLAN: 6.0 W in PS-IDLE, 8.0 W in PS-TYP, 11.5 W in PS-BUSY, 15.6 W in PS-ALLTX.**
Distribution I2R at 14.4 V adds 0.17 W, 0.43 W, 0.92 W and 4.5 W respectively. The two outlets' stages add 7.8 W of
loss inside when both deliver their contracts (declared floors 0.88 and 0.93, NOT PLOTTED).

**Merged at `458b2873`.** On `main` +5V_S2 and +5V_DEV are LM5176 stages (F-PR-04; `gen_sch_a.py` lines 873 and
881). Their 5.1 V output is not plotted (Fig. 6-2 is VOUT 12 V), so on `main` those two rows are NOT PLOTTED,
INFERRED near the AP64500's values the model uses, until a bench reading exists (FW-A15).

## 4. Power per state

PLAN battery W is at the pack terminals. The LOW to HIGH range is documented loads at their lowest or highest, with
efficiency at 12 V or 16.8 V. The tier split is battery-side watts by the tier of each load's PLAN figure.

| State (CONOPS 4a) | At the loads, PLAN | Battery W: LOW / PLAN / HIGH | `main` CONOPS 4a | S / R / D / T (W) | T share |
|---|---|---|---|---|---|
| PS-IDLE (three idle, monitor dimmed, radios receiving, SDR off) | 33.5 | 30.9 / **39.7** / 81.7 | 29.4 | 16.8 / 11.3 / 6.3 / 5.3 | 13 % (was 41 %) |
| PS-IDLE-SPEC (monitor on, APRS beacons) | 36.5 | 33.1 / **42.8** / 82.8 | 32.4 | 16.8 / 11.3 / 6.3 / 8.4 | 20 % |
| PS-TYP (three typical, monitor on, SDR on, HF receiving) | 54.5 | 46.9 / **63.0** / 120.6 | 60.1 | 22.1 / 21.0 / 8.2 / 11.7 | 19 % (was 49 %) |
| PS-BUSY (three loaded, 5G and WiFi link passing traffic, Iridium and LoRa sending), as a sustained bound | 79.6 | 54.6 / **92.0** / 134.4 | TBD | 19.3 / 26.3 / 34.6 / 11.8 | 13 % |
| PS-RED (slot 3 only, monitor off, lid closed) | 18.5 | 12.7 / **22.2** / 45.9 | 19.7 | 10.8 / 5.4 / 6.1 / 0 | 0 % |
| PS-RED-b (three idle, monitor off) | 29.6 | 26.9 / **35.7** / 71.5 | 25.4 | 16.8 / 11.3 / 6.3 / 1.3 | 4 % |
| PS-EMCON (PS-TYP with the gated radios off) | 46.1 | 37.3 / **53.1** / 103.3 | 47.6 | 20.9 / 11.0 / 7.9 / 13.2 | 25 % |
| PS-ALLTX (every transmitter keyed, monitor full, outlets off) | 183.7 | 168.9 / **203.8** / 272.0 | 227.0 | 60.9 / 98.0 / 40.8 / 4.1 | 2 % |

PS-EMCON's T share is high because nobody knows what a WiFi card draws with W_DISABLE1# asserted (`CONOPS.md` section
4b). PS-ALLTX falls against `main` because only the live WiFi card transmits: 9.1 W instead of 2 x 10 W.

**PS-BUSY as modelled here** (`drafts/pwr_budget.py`, the BUSY state). Every load is at its PS-TYP figure except
these, each at 100 % duty:
- each CM5 at board B's declared 1.6 A, 8 W (D; the datasheet gives no maximum, CM5 datasheet 3.3 and Table 9);
- each NVMe at 2.6 W active (Cervoz T405), HIGH 3.6 W (Advantech);
- the live WiFi card at 8 W, the top of AsiaRF's average (HIGH 9.1 W);
- the 5G module at LTE CA, 5.59 W;
- the RockBLOCK at 1.4 W;
- the LoRa module transmitting, 3.25 W.

It is a SUSTAINED BOUND for judging allowed modes and heat, not a duty-cycle estimate. The duty cycles stay TBD, and
the real PS-BUSY sits between PS-TYP and this figure.

**Variants that matter for the requirement states:**
- **PS-IDLE-SPEC with both WiFi link cards held off** (no peer kit linked, PCIE_PWR_EN held low by software): 36.9 W,
  saving 5.9 W.
- **PS-TYP with the standby card held off**: 61.7 W.
- **PS-ALLTX with the non-transmitting loads at typical and the standby card off**: 181.3 W PLAN, 247.5 W HIGH. D-11
  uses this case (section 7).

**What `CONOPS.md` section 4a does not say, and the session took under the owner's standing rule of 26 September
2026:** PS-IDLE-SPEC, one of REQ-014's two requirement states, is computed with the kit-to-kit link card up and idle.
This is the conservative reading of "radios idle". The link-off variant is the operator's saving.

**Heater overlay (cold only).** At `1f614233` the mat was on unregulated VBAT: 10.8 W at 14.4 V and 14.7 W at 16.8 V
(7.5 W at 12 V, RS PRO 245-556; W2 F-PR-06). On `main` since `458b2873` it is regulated to 12 V (TPS62933 U33,
`gen_sch_a.py` line 1065), so 7.5 W plus the buck's loss. The model keeps the unregulated figure, which overstates the
heater on `main`. It is switched by a software pin, HEAT_EN (U27 pin 6, line 1119), behind the eFuse U22 (line 1064).
`CONOPS.md` lines 280 and 281 count it on the battery in the cold, still at the unregulated 10.8 W; the 4 September
pad rule (appendix 32.32, line 2466) ran it only with shore present. This page takes the battery reading, the
conservative one: section 7.1 judges it over PS-TYP and PS-RED, and K4 keeps it off during every PA key-down (section
7.2).

**Accessory outlets on top of PS-TYP** (never while the PA keys; on battery only inside the outlet budget C2 of section
9.3): PoE 0.6 A at 54 V (32.4 W, 0.88) and USB-C 15 V 3 A (45 W, 0.93) add 85.2 W at VBAT, which gives 150.2 W at the
pack terminals. 77.4 W of it leaves the enclosure through the outlets.

**Off (PS-OFF), revised.** On `main` board P's SMBus clamp no longer drains the pack (F-BP-01 fixed at `faf8c981`,
`gen_sch_p.py` line 317), and the Geiger module is off the always-on domain (F-BP-02, `gen_sch_e.py` line 132). What
is left is board E's always-on domain, 0.2 to 1.7 W depending on its firmware's sleep state (TBD), plus the gauge's 336
uA. Storage uses the gauge's shutdown over SMBus (`gen_sch_e.py` line 213).

## 5. The idle figures reconciled

| Figure | Where it appears | Scenario | Boundary |
|---|---|---|---|
| 29 W | `V2-SPEC.md` line 23 until 26 Sep (withdrawn), from appendix 32.49 line 2775 | **one** compute module, monitor on, radios idle, APRS beacons; the device set before the three-module cluster of 32.50 | treated as battery-side: 8 to 9.5 h was the BB-2590's nominal 232 to 276 Wh over 29 W, with no derating (`CONOPS.md` section 6) |
| 29.4 W | `CONOPS.md` line 247 (PS-IDLE); the report's "12.2 of 29.4 W" | **three** modules idle, monitor dimmed (4 W), radios receiving, SDR off, no transmit, mixer fans off | pack terminals: per-rail declared floors plus 20 mOhm |
| about 32 W (32.4 W) | `CONOPS.md` line 248 (PS-IDLE-SPEC); the report's section 4.4 "Idle (as V2-SPEC defines it)" | PS-IDLE plus monitor on (6 W) plus 0.9 W average of APRS beacons on the PA rail | same boundary |

**The arithmetic.** Start from 29.4 W. Add the monitor's 2.0 W (eFuse path, efficiency 1.00) and the beacons' 0.9 W /
0.93 = 0.97 W. Add 0.02 W of extra I2R. That gives 32.4 W. The report quoted the first figure for its runtime row and
the second for its TBD share. They are two scenarios at the same boundary, and neither is a defect. The coincidence
of 29 W and 29.4 W is a trap: one module against three.

**On this page's model the same two scenarios** are 39.7 W and 42.8 W at the pack terminals, and 33.5 W and 36.5 W at
the loads. The 3.1 W between them is the same monitor and beacon increment plus I2R.

**Other boundaries of PS-IDLE-SPEC:**
- **VBAT:** 42.6 W.
- **Dock input on shore:** about 45 W. In `main`'s VSYS topology (S-04, since `458b2873`; `gen_sch_a.py` lines 26 to
  48) shore carries the loads through the BQ25731 (about 0.98, Fig. 8-4) and the LM5176 front end (0.95 to 0.97,
  INFERRED: VOUT 20 V is not plotted).
- **At `1f614233`:** every load sat behind the charge shunt (W2 F-CH-03), so shore carried the loads only up to
  ChargeCurrent.

## 6. Battery energy after derating, and runtime

The pack is the owner's D-06 pack: 4S3P Samsung INR18650-35E. The cell specification is Ver. 1.1
(`v2/vendor/battery/samsung-35e-orbtronic.pdf`, sha256 5ec577b952b9dc51).

| Step | Basis | PS-IDLE-SPEC, new | PS-TYP, new | aged 80 % |
|---|---|---|---|---|
| nominal at minimum capacity | 12 cells x 3.35 Ah (3.1, 7.2: 0.2C, 2.65 V cut-off, 23 C) x 3.60 V (3.3) | 144.7 Wh | 144.7 Wh | |
| rate factor | 7.8: 100 % at 0.68 A, 97 % at 3.4 A per cell; interpolated, INFERRED | x 0.997 (0.99 A per cell) | x 0.991 (1.46 A per cell) | |
| voltage sag | (3.60 - I x 0.05 Ohm) / 3.60. The DC resistance is INFERRED; 7.4 gives only the AC 1 kHz figure, at most 35 mOhm. | 142.2 Wh | 140.6 Wh | |
| temperature | 1.00 at +20 C: inside the 23 +- 3 C standard condition, and 7.5 gives 97 % at both 23 C and 40 C at 1C. Cold: 0.41 at -10 C at 3.4 A (7.5), with no point between -10 C and 23 C, so it is a bracket. | 142.2 Wh | 140.6 Wh | |
| cut-off | the capacity is specified to 2.65 V (3.9). The gauge's 2.50 V trip (`pcb_pack_protection.yaml` line 101) adds under 2 % and is not counted. | | | |
| shutdown reserve | 5 %, INFERRED: the graceful shutdown is TBD (`CONOPS.md` Shutdown row) | 135.1 Wh | 133.5 Wh | |
| ageing | 80 % is an assumption. The sheet guarantees only 60 % after 500 cycles (7.9: 2,010 mAh). | | | **108.1 Wh** / **106.8 Wh** |

**Runtime, 4S3P, +20 C (hours):**

| State | New, PLAN (LOW to HIGH bound) | Aged 80 %, PLAN (bound) | Aged 60 %, PLAN | Cold, new, low end of the bracket |
|---|---|---|---|---|
| PS-IDLE | 3.4 (1.6 to 4.4) | 2.7 (1.3 to 3.5) | 2.0 | 1.4 |
| **PS-IDLE-SPEC** (REQ-014) | 3.2 (1.6 to 4.1) | **2.5 (1.3 to 3.3)** | 1.9 | 1.3 |
| PS-IDLE-SPEC, link cards off | 3.7 | 2.9 | | |
| **PS-TYP** (REQ-014) | 2.1 (1.1 to 2.9) | **1.7 (0.9 to 2.3)** | 1.3 | 0.9 |
| PS-BUSY, sustained bound (energy only: not a sustained mode at +20 C, section 7.1) | 1.4 (1.0 to 2.5) | 1.1 (0.8 to 2.0) | 0.9 | 0.6 |
| PS-RED (slot 3 only) | 6.2 (2.9 to 10.8) | 4.9 (2.4 to 8.7) | 3.7 | 2.5 |
| PS-RED-b | 3.8 (1.9 to 5.1) | 3.0 (1.5 to 4.1) | 2.3 | 1.6 |
| PS-EMCON | 2.5 (1.3 to 3.6) | 2.0 (1.0 to 2.9) | 1.5 | 1.0 |
| PS-ALLTX (energy only; D-11 bounds it) | 0.61 | 0.49 | 0.36 | 0.25 |

**Against `main` (CONOPS 4a):** PS-IDLE-SPEC aged moves from 3.4 h to 2.5 h, and PS-TYP aged from 1.8 h to 1.7 h.

**For REQ-014.** Its values stay TBD for two reasons. First, "aged" is undefined: the 80 % and 60 % columns bracket it.
Second, the requirement states are measured on the prototype. The published figure must never exceed the measured one.

**Cells above +20 C air.** At +20 C ambient the cells run warmer than the air (section 9.2). The 7.5 factor is 97 %
at 40 C, so capacity holds, but the 60 C discharge window can end the run early.

## 7. Allowed simultaneous modes, D-11 and the basis of peak current

### 7.1 What may run together

The combinations judged here are the eight power states of section 4, each outlet and both, PS-BUSY with both
outlets, charging on shore, the vehicle input, the heater overlay over PS-TYP and PS-RED, the PA keyed on its own over
PS-IDLE-SPEC and PS-TYP, and the all-transmit case. Each is judged against three limits, with the same models as the
rest of this page:
- **The pack's declared continuous current, 10 A** (`pcb_pack_protection.yaml` line 28; every stage of
  `pcb_energy_chain.yaml`, lines 48, 69, 87, 106, 122, 138 and 153; the protection test proves 10 A for an hour,
  line 114). It is checked at every cell-stack voltage down to the gauge's under-voltage trip of 2.50 V per cell,
  10.0 V (line 101).
- **The declared peak, 18 A** (line 29), for which neither YAML file declares a duration, and the gauge's 20 A for
  2 s trip (line 110). The design record gives two key-down figures, both written before this pack was ruled (32.62,
  line 3054): 32.53's "lasts minutes" for the 200 W peak into 8 to 10 kJ/K (appendix line 2860), and 32.56's 20 s
  key-down at 45 W for the plate's local patch under the PA's flange (line 2940). Section 7.2 sets 60 s, between
  the two.
- **The cells' windows at the cell surface**: discharge -10 to +60 C and charge 0 to +45 C (sheet 3.12; gauge
  lines 154 and 145). They are checked at +20 C ambient, the runtime requirement's own condition, with the pack model
  of section 9.2. The heater rows are judged at the envelope's cold end instead, since the heater runs only there.

A combination the table does not list, for example the heater with an outlet, is still bounded by the controls,
because they act on measured pack current and temperatures (C1 to C4, section 9.3) and on every PA key-down (the
key-down rules of section 7.2). It is not tabulated.

Pack current is solved at the stack voltage, counting the 22.5 mOhm distribution drop once: V x I = W at VBAT + I² x
22.5 mOhm. Cell temperature is the ambient, plus all the heat inside over the enclosure conductance, plus the cells'
own I2R over the pack block's 0.148 to 0.445 W/K. The heat inside is battery W, less what the outlets deliver
outside, plus the cells' own I2R. On W4's bound the block's conductance goes with the enclosure's: the lowest with the
lowest, the highest with the highest. On 32.53's conductance the block is taken at its mid value, 0.30 W/K. That
pairing is why W4's best case can read cooler than 32.53's, as it does for PS-TYP with both outlets. PS-BUSY is
modelled as a sustained bound (section 4). C1 to C4 are the controls of section 9.3; K1 to K5 are the key-down rules
of section 7.2.

| Combination | Battery W PLAN (HIGH); W delivered outside | Pack current PLAN (HIGH): at 14.4 V; at 10.0 V | Stack voltage below which PLAN (HIGH) passes 10 A | Cells at +20 C: on 32.53's conductance; on W4's bound | Verdict | Enforced by |
|---|---|---|---|---|---|---|
| PS-IDLE | 39.7 (81.7) | 2.8 (5.7); 4.0 (8.2) | never (never) | 33.9 to 35.1; 35.3 to 56.4 | within 60 C at every corner; past C1's +55 C at the worst corner | C1 at the worst corner only, from +18.6 C ambient there |
| PS-IDLE-SPEC | 42.8 (82.8) | 3.0 (5.7); 4.3 (8.4) | never (never) | 35.1 to 36.5; 36.6 to 59.6 | within 60 C, by 0.4 K at the worst corner; past C1's +55 C there | C1 at the worst corner only, from +15.4 C ambient there |
| PS-RED, lid closed | 22.2 (45.9) | 1.5 (3.2); 2.2 (4.6) | never (never) | 31.7 to 35.4; 29.3 to 42.2 | within, and under C1's +55 C at every corner | none at +20 C (C1 from +32.8 C at the worst corner) |
| PS-RED-b, lid closed | 35.7 (71.5) | 2.5 (5.0); 3.6 (7.2) | never (never) | 39.4 to 45.5; 35.4 to 56.8 | within 60 C; past C1's +55 C at the worst corner | C1 at the worst corner only, from +18.2 C ambient there |
| PS-EMCON | 53.1 (103.3) | 3.7 (7.2); 5.3 (10.5) | never (10.4 V) | 39.4 to 41.0; 41.0 to 70.3 | HIGH passes 10 A in the last 0.4 V; cells past 60 C at the pessimistic end | C3 (current), C1 (cells) |
| PS-TYP | 63.0 (120.6) | 4.4 (8.4); 6.3 (12.2) | never (12.1 V) | 43.8 to 45.7; 45.4 to 81.3 | PLAN within; HIGH over 10 A below 12.1 V; cells past 60 C at the pessimistic end | C3, C1 |
| PS-TYP plus PoE | 100.4 (158.5); 32.4 | 7.0 (11.0); 10.2 (16.2) | 10.2 V (15.8 V) | 52.6 to 54.7; 52.3 to 100.3 | PLAN passes 10 A only at the very end; cells past C2's +50 C on every conductance in the record | **C2** |
| PS-TYP plus USB-C | 112.3 (170.5); 45.0 | 7.8 (11.8); 11.4 (17.4) | 11.3 V (every voltage) | 55.3 to 57.5; 54.2 to 105.8 | over 10 A late in the discharge; cells past +50 C | **C2** |
| PS-TYP plus both outlets | 150.2 (208.9); 77.4 | 10.4 (14.5); 15.3 (21.5) | 15.0 V (every voltage) | 68.7 to 71.2; 64.4 to 134.6 | over 10 A for most of the discharge; HIGH over 18 A below 11.75 V; cells past 60 C on every conductance | **not a sustained mode on battery: C2** |
| PS-BUSY (sustained bound) | 92.0 (134.4) | 6.4 (9.3); 9.3 (13.7) | never (13.5 V) | 57.9 to 60.8; 59.4 to 116.0 | PLAN within 10 A; cells past C1's +55 C on every conductance | **a bounded-duration mode: C1 ends it**; C3 at HIGH |
| PS-BUSY plus both outlets | 179.8 (223.0); 77.4 | 12.5 (15.5); 18.4 (22.9) | every voltage (every voltage) | 89.3 to 92.7; 83.0 to 182.7 | over 10 A at every voltage; over 18 A at the end of discharge | **not allowed on battery: C2** |
| PS-TYP while charging on shore at 3 A | loads from shore; about 46.5 W into the pack | charging | n/a | 43.4 to 45.5; 45.6 to 82.8, against the **45 C** charge window | the charge window closes at +20 C at the top of 32.53's figure | the gauge's charge window (line 145) stops the charge; the loads carry on from shore |
| operating from a 12 V vehicle | the LM5069 limits at 4.85 A minimum: 58 W in, about 55 W at VSYS against PS-TYP's 63.0 W | the pack gives about 8 W, under 1 A | never | as PS-TYP, plus the front end's loss | as PS-TYP | C1 |
| PS-TYP plus the heater (cold overlay, on the battery) | 73.9 (135.7) | 5.1 (9.4); 7.5 (13.8) | never (13.6 V) | a cold row: at -20 C ambient the inside air sits at 2.9 to 5.2 C on 32.53's conductance and 6.6 to 42.0 C on W4's bound, the mat's heat included | PLAN within 10 A; HIGH over 10 A below 13.6 V; nothing near 60 C | C3 at HIGH; K4 turns the heater off during any PA key-down |
| PS-RED plus the heater (cold overlay), lid closed | 33.1 (60.7) | 2.3 (4.2); 3.3 (6.1) | never (never) | a cold row: at -20 C the inside air sits at -3.3 to 2.3 C on 32.53's and -6.6 to 11.5 C on W4's, the mat's heat included | within 10 A at every corner | K4 |
| **the PA keyed alone over PS-IDLE-SPEC, PA at 75 W** | 122.4 (203.7) | 8.5 (14.1); 12.4 (20.9) | 12.3 V (every voltage); 18 A: never (11.5 V) | a burst: one 60 s key-down at up to 12.4 A adds 0.7 to 1.5 K, adiabatic. Keyed continuously, which K1 forbids: 74.8 to 78.7; 75.5 to 156.8 | PLAN over 10 A in the last part of the discharge; the every-load-at-maximum corner passes 18 A below 11.5 V | K1 to K5 and C4 (section 7.2); the corner by K4 |
| **the same, PA at 113 W, the rest at PLAN** | 162.3 | 11.3; 16.6 | 16.2 V; 18 A: never | a burst: 1.2 to 2.8 K per 60 s at up to 16.6 A. Keyed continuously: 100.3 to 105.5; 99.0 to 217.1 | over 10 A for almost the whole discharge; under 18 A at every voltage | K1 to K5, C4 |
| **the PA keyed alone over PS-TYP, PA at 75 W** | 143.9 (243.5) | 10.0 (16.9); 14.6 (25.1) | 14.4 V (every voltage); 18 A: never (13.6 V) | a burst: 0.9 to 2.1 K per 60 s at up to 14.6 A. Keyed continuously: 88.1 to 92.7; 87.8 to 188.4 | over 10 A for most of the discharge; under 18 A at every voltage; the every-load-at-maximum corner passes 18 A below 13.6 V | K1 to K5 and C4; the corner by K4 |
| **the same, PA at 113 W, the rest at PLAN** | 184.0 | 12.8; 18.8 | every voltage; 18 A below 10.42 V | a burst: 1.4 to 3.2 K per 60 s at the 18 A C4 allows. Keyed continuously: 115.8 to 121.7; 112.9 to 253.2 | over 10 A at every voltage; over 18 A below a 10.42 V stack | **the PA-alone floor of 12.4 V (K5)**, C4 |
| every transmitter keyed (PS-ALLTX) | 203.8 (272.0) | 14.2 (18.9); 20.9 (28.2) | every voltage | a burst: 1.4 to 3.2 K per 60 s at 18 A | above the 10 A continuous rating for the whole key-down | **only inside D-11's floor and the key-down rules (section 7.2), and only once the chain carries a short-time rating (PWR-F12)** |
| any PA key-down with the heater on | the mat adds 8.5 W on `main`, regulated (10.1 W with `1f614233`'s unregulated mat) | | | | **no**: it would use the all-transmit floor's whole margin (section 7.2) | K4: HEAT_EN off before the PA keys |
| PS-ALLTX with the outlets on (was PS-ALLTX-OUT) | 316 W on `main`'s old figures | | | | **no** (D-11) | S-14 (U30 on `main`); K4 |

In the PA rows the heat inside counts the PA's 30 W of RF as heat, which overstates it; the continuous-keying figures
are shown only to say why K1 bounds every key-down. The PA rows keep board D's SA868 at its transmitting figure and
every other load at the base state's own figure, with the outlets and the heater off. Their HIGH column is every load
at its maximum with the PA at 113 W, which K4 excludes as it does for the all-transmit case. The heater rows carry the
mat at its 14.4 V power (PLAN) or its 16.8 V power (HIGH) at every stack voltage; a resistive mat draws less below
those voltages, so its current is overstated there.

How the outlets are held off during a PA key-down: on `main` since `458b2873` (S-14) the NAND U30 gives OUTLET_OK =
NOT (TR_APRS AND PA_EN) (`gen_sch_a.py` line 1104), and U26's two spare gates make POE_EN = POE_SW_EN AND OUTLET_OK
and PD_EN = PD_SW_EN AND OUTLET_OK (lines 1095 and 1103). At `1f614233` the outlet enables were software expander
pins only. The floors and the key-down time are firmware (panel and bridge), reading the gauge's pack voltage,
current and cell temperatures and, for K2 and C4, the PA's flange temperature (PWR-F15).

Operating while charging on shore: in `main`'s VSYS topology (S-04) the front end gives about 100 W (5 A at
20 V). PS-TYP takes 63.0 W, so the pack gets about 35 W, about 2.3 A (INFERRED). The charging row is computed at the
full 3 A, which overstates the charge path's heat, so it errs on the safe side. At `1f614233` the loads sat behind
the charge shunt, and shore carried load and pack together only up to ChargeCurrent (W2 F-CH-03). With both outlets on,
PS-TYP's 150.2 W is more than the input carries, so the pack discharges and C2's temperature trigger still applies.

**What the table shows.** The first version of this table allowed PS-TYP with both outlets, and PS-BUSY, with "none
needed". It checked them only against the 18 A peak and the 8 A per-cell limit. Checked against the declared
continuous current and the cells' 60 C window, neither holds as a sustained mode on battery at +20 C, on any
conductance in the record. Both now carry a named control (section 9.3). The second version left out the PA keyed on
its own and the heater. The PA keyed alone is above the continuous rating for most of the discharge, and at 113 W
passes 18 A near its end: it is now bounded by the key-down rules and a floor of its own (section 7.2). The heater is
within every current limit on its own, and is kept off during any key-down. What the controls cost the operator is
PWR-F13.

### 7.2 D-11 and every PA key-down: the thresholds

These are **PROVISIONAL, taken by the session under the owner's standing rule of 26 September 2026** (REQ-018 names
the session as the setter, S-14). D-11 rules on the all-transmit case. This cycle applies the same thresholds to the
PA keyed on its own, for two reasons:
- `CONOPS.md` line 345 gives the PA's worst duty as "key-down for minutes (32.53 line 2860), inside the key-down
  bound of D-11". The citation is right: appendix 32.53, line 2860, reads "The 200 W peak (PA key-down) lasts minutes
  and goes into about 8 to 10 kJ/K of thermal mass, about +10 K transient";
- section 7.1 shows that such a key-down passes the declared continuous current for most of the discharge.

The design record states two key-down durations, not one. Besides 32.53's "minutes", appendix 32.56, line 2940 (7
September 2026, 01:17, 22 minutes after 32.53), which moves the PA's flange to the face plate, says: "the plate is
the heatsink (3 mm, 0.7 kg, 660 J/K: a 20 s key-down at 45 W warms the local patch about 15 K; the average at APRS
duty is a few watts)". K1's 60 s below sits between the two: it **tightens 32.53's "minutes" and is three times
32.56's 20 s**. It is not a gap filled. Its reasons, and what the longer time costs the PA, are under "The key-down
time".

**The current contract.** The pack's declared peak is 18 A (`pcb_pack_protection.yaml` line 29). That is 90 % of the
gauge's discharge over-current trip of 20 A for 2 s (line 110), and no duration is declared for it. The declared
continuous current is 10 A (line 28). Every all-transmit case below draws more than 10 A for the whole key-down, and
the PA keyed alone over PS-TYP does below a 14.4 V stack. **Every PA key-down therefore makes up to 18 A a service
current for the key-down time, which the chain's declaration does not yet carry** (PWR-F12).

The parts along the path, each by its own document or declaration:
- **Rated above 18 A continuous:**
  - the cells: 8 A continuous per cell (sheet 3.8), 24 A for 3P;
  - the 25 A ATOF blades F1 on board P, F3 on board E and F1 on board A: 19 A continuous at the 65 C column of the
    maker's derating (`pcb_fuse_derating.yaml` line 46);
  - their Keystone 3568 holders: UL 30 A, -50 to +145 C. This is from the Keystone catalogue M65, page 42, fetched by
    this stream. The page sets one specification block between the 3557-2 and 3568 holders; that it covers the 3568
    is read from the layout (INFERRED);
  - the charge and discharge FETs Q1 and Q2, CSD17570Q5B: 53 A continuous at 25 C on a 1 in² 2 oz pad, with the
    junction rated to 150 C and 0.92 mOhm maximum at a 4.5 V gate (SLPS471D, Absolute Maximum Ratings, 5.1 and 5.2).
    At 18 A each dissipates about 0.3 W, about +15 K on that pad (INFERRED);
  - the XT60 at 30 A and the dock block at 4 x 9 A (`pcb_energy_chain.yaml` lines 93 and 124);
  - the 2 oz bands on boards P and E, declared 25 A (lines 50 and 108).
- **Declared only:**
  - the 2 mOhm shunt R10, "2m 2512 2W (sense)" (`gen_sch_p.py` line 209). It dissipates 0.65 W at 18 A against a
    declared 2 W, and has no part number or maker sheet;
  - on `main` since `458b2873`, board A's charge-current shunt R17, "5mOhm 1% 2512", in the discharge path (S-04). It
    dissipates 1.62 W at 18 A against the 3 W of its fitted part, whose maker's sheet is not held (`gen_sch_a.py`
    lines 716 to 722).
- **Not proven at 18 A: the chemical fuse F2**, Eaton SCF9550-30-05, in series between the blade and Q1 on `main`
  (`gen_sch_p.py` lines 64 to 76 and 247 to 289).
  - It is rated 30 A, 100 % of rating for one hour minimum, and -20 to +60 C operating, with no current derating
    against temperature published (Eaton ELX1135, quoted at lines 255 to 256 and 272).
  - At 18 A it dissipates 0.32 to 0.81 W of its own. The tree's record says "the risk is judged low, not proven: F2's
    case temperature is a thermal-test reading" (lines 273 to 276; `fnd/r4p` `drafts/r4-decisions.md` O-8; the
    battery stream's `FUSE-INTERPRETATION.md`). The energy chain does not carry it (O-13).
  - It sits on board P at the block's temperature, and K2 lets a key-down start with a cell at +55 C. **Its margin
    to +60 C during a key-down is therefore unknown**, since no thermal resistance is published. Its permanent
    opening would end the pack.
  - The gauge can also fire it. Its Safety Overcurrent in Discharge is a permanent failure, default 10 A for 5 s
    (SLUUAQ3A 3.5 and 14.10.4). Every all-transmit key-down of more than 5 s would pass it, and so would the PA keyed
    alone over PS-TYP below a 14.4 V stack. Its default is off (Enabled PF A 0x00, 14.2.5.1), though the battery
    stream found the manual's text for that word contradictory (`PRIMARY-CONFIGURATION.md` line 79). That stream's
    proposed golden image writes Enabled PF A = 0x53 with SOCD at 0 until its reviewer answers (line 137). PWR-F12
    keeps it so, or above the 20 A trip.
- **Not yet judged at 18 A: board A's pack-node copper** (appendix 32.244). `dc_drop` judges a conductor at the
  rail's typical current, 10 A on VBAT (`dc_drop.py` lines 258 to 264). Appendix 32.244 gives 7.19 mm of 1 oz copper for 10 A and 16.18 mm
  for 18 A (3.60 and 8.09 mm at 2 oz), and records that nobody had written down whether 18 A is a service current or a
  fault current. D-11 answers that: it is a service current for the key-down time.

An all-transmit that pulls more than 20 A for 2 s opens the discharge FET, and the whole kit goes dark. The
thresholds exist to keep that from happening.

**The key-down rules, for every PA key-down** (all-transmit or the PA alone):
- **K1, time.** At most 60 s per key-down, and at least 2 s between key-downs.
  - The 2 s gives the gauge at least one status decision under the OCD1 backstop's threshold, which returns OCD1
    from Alert to Normal (SLUUAQ3A 2.5, the state table; status decisions at 1 s intervals, 5.2).
  - Beyond that the repeat rate is set by K2's gates on measured temperatures, not by assumption. A fixed rate, if
    one is wanted, is TBD from the measured plate and cell heating (TEST-PLAN E3 and section 10).
- **K2, temperatures at key-on.** Every cell at most +55 C on the gauge's thermistors, the inside air at most +50 C
  (C1's air trigger), and the PA's flange at most +75 C (fifth cycle; the sensor is PWR-F15). The flange gate bounds
  the repeat rate on the PA side: the PA keys again only once its flange has cooled under +75 C.
- **K3, current at key-on.** The gauge's pack current, averaged over 10 s, at most 9.0 A. So C2 and C3 act before
  the PA keys, and the OCD1 timer is not already running when it does.
- **K4, the other loads while keyed:**
  - the outlets off (the S-14 NAND U30 on `main`, behind the software holds POE_SW_EN and PD_SW_EN);
  - the heater off (HEAT_EN, U27 pin 6, `gen_sch_a.py` line 1119);
  - the standby WiFi card off, and no compute stress, so the non-transmitting loads run at typical.
- **K5, the state-of-charge floors:**
  - all-transmit (the PA with any other transmitter sending) only above a pack rest voltage of **15.5 V**;
  - the PA keyed alone, with the other transmitters' queued sends deferred (LoRa, Iridium, HF, and no bulk 5G or
    WiFi link transfer), only above **12.4 V**;
  - below 12.4 V the PA does not key, and the operator is told.
- **C4, the in-key guard (section 9.3).** The PA unkeys if the gauge reads more than 18 A, any cell under 2.70 V, or
  the PA's flange +85 C (fifth cycle; the sensor is PWR-F15).

**The state-of-charge floors.** They are expressed as pack REST voltages, because the gauge measures voltage directly
and the 35E's open-circuit-voltage curve is not in this tree, so the matching RSOC is TBD until the pack's learning
cycle.

The firmware reads the rest voltage while loads run as the gauge's cell-stack voltage plus the present pack current
times 0.047 Ohm. That is the lowest pack resistance in the inferred range (4 x 0.035 / 3), so it under-states the
rest voltage and errs toward refusing a key-down. The measured pack impedance, or RSOC after the learning cycle,
replaces it at bring-up.

The arithmetic, with the distribution drop counted once:
- VBAT under load is W at VBAT divided by 18 A. W at VBAT is battery W less the distribution loss (section 1).
- The cell stack stands 18 A x 22.5 mOhm, 0.41 V, above VBAT.
- The rest voltage adds 18 A across the pack's own resistance, 4 x R_cell / 3.

**Corrected in the second cycle.** The first version divided battery W, which already carries the distribution loss,
by 18 A and then added the distribution drop again. That put every rest voltage 0.17 to 0.39 V high. The first
version's figures are kept in `drafts/pwr_budget.json` as `V_rest_pack_prev_method`, reproduced with its own 20 mOhm.
**In the third cycle** the distribution resistance took F2 at 2.5 mOhm (section 1), which raised every rest voltage
below by 0.04 to 0.05 V. **In the fifth**, `main`'s R17 adds 5 mOhm more (section 1): 18 A x 5 mOhm, 0.09 V, on
every rest voltage at 18 A. The rows marked "on `main`" carry it.

| All-transmit case | W at VBAT (battery W) | VBAT at 18 A | Cell stack at 18 A | Rest voltage at R_cell 0.035 / 0.05 / 0.06 Ohm | Per cell |
|---|---|---|---|---|---|
| PLAN, all non-transmit loads at their PS-ALLTX PLAN | 199.3 (203.8) | 11.07 V | 11.48 V | 12.32 / 12.68 / 12.92 V | 3.08 to 3.23 V |
| HIGH, every load at its maximum | 264.0 (272.0) | 14.67 V | 15.07 V | 15.91 / 16.27 / 16.51 V | 3.98 to 4.13 V: deliverable from full charge at every resistance in the range, but not covered by the floor below |
| non-transmit loads at typical, standby card off, PLAN | 177.8 (181.3) | 9.88 V | 10.28 V | 11.12 / 11.48 / 11.72 V | 2.78 to 2.93 V |
| the same, HIGH (the PA at 113 W, W2 F-PR-02) | 240.8 (247.5) | 13.38 V | 13.78 V | 14.62 / 14.98 / **15.22 V** | 3.66 to 3.81 V |
| the same, HIGH, with the heater ON (what K4 prevents), `1f614233`'s unregulated mat | 240.8 plus the mat's 10.1 | 13.94 V | 14.35 V | 15.19 / 15.55 / **15.79 V** | 3.80 to 3.95 V |
| the same, the regulated mat of `main` (without R17) | 240.8 plus 8.5 | 13.85 V | 14.26 V | 15.10 / 15.46 / 15.70 V | 3.78 to 3.93 V |
| **on `main`** (R17 in the pack path, 27.5 mOhm): non-transmit loads at typical, standby card off, HIGH | 240.8 (249.1) | 13.38 V | 13.87 V | 14.71 / 15.07 / **15.31 V** | 3.68 to 3.83 V |
| **on `main`**, the same with the regulated mat on (what K4 prevents) | 249.4 (258.2) | 13.85 V | 14.35 V | 15.19 / 15.55 / **15.79 V** | 3.80 to 3.95 V |

**Taken for all-transmit:**
- **The declared floor stays a pack rest voltage of at least 15.5 V (3.88 V per cell).**
  - Its basis is the "non-transmit loads at typical, HIGH" row, which needs 15.22 V at the highest cell resistance
    in the INFERRED range on the boards as generated at `1f614233`, and 15.31 V on `main`, with R17 in the pack path.
  - The other 0.28 V (0.19 V on `main`) is a deliberate margin, not arithmetic. With the heater off (K4) it keeps the
    floor good up to a cell DC resistance of 0.072 Ohm, 19 % above the top of the range (0.068 Ohm, 13 % above, on
    `main`). The floor is not raised for R17: the basis still sits inside it at every resistance in the range, and
    C4 enforces the 18 A where it mispredicts.
  - **The heater would use the whole margin.** With the mat on, the same row needs 15.79 V on `main` (the regulated
    mat's 8.5 W plus R17), as it did at `1f614233` with the unregulated mat's 10.1 W at 13.94 V (15.70 V for the
    regulated mat without R17). The floor would then cover a cell resistance only up to 0.048 Ohm. That is why K4
    turns it off. A key-down lasts at most 60 s, and its own I2R warms
    the cells by 1.4 to 3.2 K, so the heater's pause costs the cells nothing.
  - **The floor is not shown to hold in the cold or on an aged pack.** No document in the tree gives the cells' DC
    resistance, its growth with ageing, or its value below 23 C. The sheet's 7.5, 40 % of capacity at -10 C to a
    2.65 V cut-off at 3.4 A, suggests it grows steeply in the cold.
  - The same margin also has to absorb two more things. One is the gauge's voltage error: SLUSC67B 6.16 gives an ADC
    gain error up to ±0.8 % of full-scale range over temperature, and the error at the pack voltage after the
    calibration 8.2.1 asks for is TBD. The other is the charge the key-down draws, 0.30 Ah or 3 % of the block, whose
    voltage effect needs the open-circuit-voltage curve (TBD).
  - Where the floor mispredicts, the in-key guard C4 ends the key-down early instead of letting the gauge trip. The
    floor is re-derived at bring-up from two measurements: the pack's DC impedance at +20, 0 and -10 C, and the PA's
    drain current at 13.8 V (F-PR-02: 5.4 to 8.2 A, the largest single uncertainty).
  - The protective direction does not change: this corrects the basis and does not weaken the threshold.
- **The "every load at its maximum" row is outside the floor.** It needs 15.91 to 16.51 V, and the floor covers it
  only up to R_cell 0.018 Ohm. It is excluded by K4, not by the floor.

**Taken for the PA keyed alone** (the rows of section 7.1; the model's `pa_only` block):

| PA-alone case | W at VBAT (battery W) | Cell stack at 18 A | Rest voltage at R_cell 0.035 / 0.05 / 0.06 Ohm |
|---|---|---|---|
| over PS-TYP, PA at 75 W | 141.7 (143.9) | 8.28 V | 9.12 / 9.48 / 9.72 V: under 18 A down to the gauge's 10.0 V |
| over PS-TYP, PA at 113 W, the rest at PLAN | 180.3 (184.0) | 10.42 V | 11.26 / 11.62 / **11.86 V** |
| over PS-IDLE-SPEC, PA at 113 W, the rest at PLAN | 159.4 (162.3) | 9.26 V | 10.10 / 10.46 / 10.70 V |
| over PS-TYP, every load at its maximum | 237.0 (243.5) | 13.57 V | 14.41 / 14.77 / 15.01 V: excluded by K4 |

- **The PA-alone floor is a pack rest voltage of at least 12.4 V (3.10 V per cell).** Its basis is the PS-TYP row
  with the PA at 113 W, which needs 11.86 V at the highest cell resistance (11.95 V on `main`, with R17). The other
  0.54 V (0.45 V on `main`) covers a cell resistance up to 0.082 Ohm (0.079 Ohm on `main`), with the same caveats
  for cold and ageing and the same guard.
- Above 12.4 V a PA-alone key-down stays under the 18 A service current at every cell resistance in the range. With
  the PA at 75 W it stays under 18 A down to the gauge's 10.0 V at any resistance.
- At 12.4 V and 18 A the cells stand at about 2.74 V under load (3.10 V less 6 A x 0.06 Ohm). That is above C4's
  2.70 V and the gauge's 2.50 V.
- This is what the second cycle's "below the floor it serialises" now means: below 15.5 V the PA keys only alone,
  and below 12.4 V it does not key. Where 12.4 V sits in the pack's charge is TBD with the open-circuit-voltage curve.

On `main` since `458b2873` the PA stage's average current loop limits at 7.2 to 9.5 A (F-PR-01, `gen_sch_a.py`
lines 903 to 914), so the PA path is bounded in hardware at 99 to 131 W. That is not a tighter bound than F-PR-02.
Board D's gate bias is regulated on `main` too (VGG 4.30 to 4.68 V, `gen_sch_d.py` lines 624 to 645), which keeps the
RA30H1317M1 sheet's "VGG<5V" condition for its 45 W output rating; the drain at 13.8 V is still a bench item, so the
113 W bound stands.

**The key-down time.** At 18 A the 12 cells dissipate 15.1 to 25.9 W (R_cell 0.035 to 0.06 Ohm). On 600 g of cells
(3.10: 50 g maximum each), with a specific heat of 0.8 to 1.1 J/gK (INFERRED; no Samsung figure), that is **1.4 to
3.2 K per minute, adiabatic**. The sheet gives only a maximum mass, so this is the smallest rise it allows. The worst
rise would use the whole 5 K between the 55 C gate and the 60 C window only at 32.4 g per cell (INFERRED). The PA
dumps about 45 W into the plate. Spread over the whole plate that is **6.7 K per minute** on W4's 403 J/K (4.1 K on
32.56's 660 J/K) before any loss (INFERRED). That is a whole-plate average: the PA's flange sits on a local patch
that warms far faster (below).

**What the design record says.** It gives two key-down figures.
- **32.53, line 2860 (7 September 2026, 00:55):** "The 200 W peak (PA key-down) lasts minutes and goes into about 8
  to 10 kJ/K of thermal mass, about +10 K transient." Read literally, with all 200 W as heat and no loss to ambient,
  that is 1.2 to 1.5 K per minute of the whole mass, and the +10 K takes 400 to 500 s, about 7 to 8 minutes
  (INFERRED, `drafts/pwr_budget.json` `d11.record_3253`). Set against the cell-only figure above:
  - the 12 cells hold 480 to 660 J/K (600 g at 0.8 to 1.1 J/gK), about 5 to 8 % of the record's lumped mass;
  - their own I2R at 18 A heats them at 1.4 to 3.2 K per minute, 0.9 to 2.7 times the lumped rate, on top of
    whatever the inside air does;
  - so the lumped +10 K does not bound the cells. At those rates the 5 K between K2's +55 C gate and the 60 C window
    lasts 93 to 219 s. Two minutes at 18 A use it at the worst rate, and the literal reading's 7 to 8 minutes would
    pass it at every rate.
- **32.56, line 2940 (01:17 the same night):** "the plate is the heatsink (3 mm, 0.7 kg, 660 J/K: a 20 s key-down at
  45 W warms the local patch about 15 K; the average at APRS duty is a few watts)". The RA30H1317M1's copper flange
  bolts to that patch (the same line). The figure implies a patch of about 60 J/K (45 W x 20 s / 15 K, INFERRED).
  Taken linear in time, the patch warms 0.75 K per second at 45 W: 45 K in 60 s, three times the record's 20 s.
  Linear is the upper reading of the record's figure: spreading into the rest of the plate and loss to ambient
  lower it, by an amount no held document gives.

Both entries predate this pack. 32.62 (13:10 the same day, line 3054) withdrew the BB-2590/U that 32.49 had put on
the 14.4 V node (line 2771: "14.4 V or 28.8 V, 250 to 300 Wh ... 10 A continuous and 18 A pulse per section") for a
smaller pack of the same 14.4 V class, 4S Li-ion. So both predate the pack and the current contract this page judges
against.

**The PA's case against its limits** (`drafts/pwr_budget.json` `d11.pa_case_record_3256`). The RA30H1317M1 sheet
(Mitsubishi, October 2011, sha256 9fda757ab1acfb6b) rates the case at -30 to +100 C in operation (Maximum ratings,
"Tcase(OP) Operation Case Temperature Range"). Under "Thermal Design of the Heat Sink" it adds: "For long-term
reliability, it is best to keep the module case temperature (Tcase) below 90°C." It recommends a thermal compound
under the flange and publishes no contact resistance ("Mounting"). The comparison is made at K2's worst key-on:
- the inside air at +50 C, at the envelope's +40 C ambient, and the plate under the flange taken at that +50 C
  (INFERRED: the plate sits between the inside air and the ambient when shaded, as 32.53 requires, and when no
  earlier key-down's heat is left in it, which K2 did not check before this cycle);
- the patch's rise linear in time, on the record's 60 J/K;
- the flange interface TBD, so every figure is the patch's, before the interface's own rise.

| PA heat at the flange | Patch after 20 s / 30 s / 60 s | From +50 C to the 90 C reliability figure / the +100 C rating |
|---|---|---|
| 45 W: 30 W out at the sheet's 40 % minimum (32.52 item 6, 32.56; the sheet's own worked example gives 45.05 W) | 65.0 / 72.5 / **95.0 C** | 53 s / 67 s |
| 68 W: F-PR-02's 113 W in, 45 W out (the output rating) at 40 % | 72.7 / 84.0 / **118.0 C** | 35 s / 44 s |
| 83 W: 113 W in at 30 W out, outside the sheet's 40 % condition | 77.7 / 91.5 / **133.0 C** | 29 s / 36 s |

So **a 60 s key-down is not supported on the PA side by the record's own figure.**
- At 45 W it ends 5 K past the maker's 90 C, with 5 K left under the rating for the interface.
- At the PA's upper drain bound it passes the rating at 44 s.
- Spreading lowers these figures, by an amount no held document gives.
- Repeated key-downs are worse: a key-down 2 s after the last one starts from a hot patch, and K2 checked only the
  cells and the air.
- A mismatched antenna turns more of the drain into heat still. That case is not computed here.

**Taken: 60 s continuous per PA key-down (K1); key-on only while every cell reads at most 55 C and the PA's flange at
most 75 C (K2); the PA unkeyed at +85 C on the flange (C4).** K1 is a **PROVISIONAL tightening of 32.53's "lasts
minutes"**, taken by the session under the owner's standing rule of 26 September 2026. It is three times 32.56's
20 s, which is why the PA side needs the flange limits. The reasons for 60 s rather than minutes:
- **the chain's current declarations:** 10 A continuous and an 18 A peak with no duration (`pcb_pack_protection.yaml`
  lines 28 and 29). A key-down over PS-TYP draws more than 10 A for most of the discharge (section 7.1), so a key-down
  of minutes would ask the chain for a short-time rating it does not declare. PWR-F12 drafts 18 A for 60 s, not for
  minutes;
- **F2:** its margin to its +60 C during an 18 A key-down is unknown (above), and a longer key-down only adds to its
  self-heating;
- **the cells' window:** 60 s sits inside the 93 s in which the worst adiabatic rate uses the 5 K.

**The flange limits**, PROVISIONAL, taken by the session under the same rule (fifth cycle):
- **Why a measured limit and not a shorter K1.** Four things are unmeasured: the record's patch figure, the spreading,
  the interface, and how fast the patch cools between key-downs. The last decides the repeat rate, and no held
  document gives it. A reading on the flange makes the key-down indifferent to all four, as C1 to C4 make the pack
  indifferent to the enclosure conductance.
- **C4 at +85 C:** 5 K under the maker's 90 C reliability figure and 15 K under the +100 C rating. The 5 K and 15 K
  cover the sensor's offset from the hottest point of the flange and its lag. At the record's patch rate, up to 1.4 K
  per second at 83 W, a 1 s reading interval lags by about 1.4 K (INFERRED). The offset is checked at bring-up
  against a thermocouple on the flange.
- **K2 at +75 C:** 10 K under the cut. So a key-down that starts gets at least 7 s before the cut at the highest heat
  above (13 s at 45 W), longer than an APRS frame (this page's planning placeholder is a 1 s key). The gate also sets
  the repeat rate on the PA side by measurement.
- **From K2's worst key-on (+50 C),** on the record's linear figure, the cut ends a key-down after about 47 s at 45 W,
  31 s at 68 W and 25 s at 83 W. Spreading lengthens these. So at the hot end of the envelope the flange, not K1,
  sets how long a key-down lasts. That is part of PWR-F13's cost.
- **No board carries the sensor.** No temperature part on `main` sits on or near the flange: they are board P's four
  cell thermistors, its second level's own thermistor (since `d90f30e4`) and the PTC element beside its FETs, board
  E's BME688 and board B's TMP117 under the coolers (PWR-F15).
- **Without it,** the record's figure bounds one key-down from a +50 C plate at about 30 s (84.0 C at 68 W, 6 K under
  the 90 C for the interface; 91.5 C at 83 W), and gives no bound for repeated key-downs. That is OPEN. It is not a
  fallback this page takes.

What K1, K2 and C4 give, and what they depend on:
- They leave the 60 C discharge window (`pcb_pack_protection.yaml` line 154) at least 1.8 K more than the worst
  adiabatic rise of a 60 s burst (3.2 K).
- **On the plate:** the whole plate's average rises at most 6.7 K per 60 s key-down at 45 W (W4's 403 J/K; 4.1 K on
  32.56's 660 J/K), and 10.1 K at 68 W. The local patch under the flange is bounded by C4's +85 C, not by the 60 s.
  The Xenarc monitor sits elsewhere in the same plate (-20 to +70 C, `pcb_part_temps.yaml` line 43); its own
  temperature through a key-down is TBD (TEST-PLAN E3).
- **They hold only once PWR-F12 and PWR-F15 close.**
  - PWR-F12 needs three things: the chain carries a declared short-time rating of at least 18 A for 60 s; board A's
    pack-node copper has been judged at it; and F2's body is shown at or under +60 C after 18 A for 60 s from a +55 C
    block.
  - PWR-F15 needs the flange sensor fitted and its offset read against a thermocouple.
  - Until then the 60 s bounds the cells' heating and the state of charge, not the path's current rating, F2's
    temperature or the PA's case.
- The gauge backstop proposed in section 9.3 (OCD1 at 11 A for 90 s) lets a 60 s key-down pass with 30 s to spare.

### 7.3 The basis of peak current

**Pack current is solved at the cell-stack voltage:** V x I = W at VBAT + I² x 22.5 mOhm. W at VBAT is the sum of each
load at the figure section 2 names, divided through its converter chain at that state's current. PLAN assumes no
diversity beyond the state definition. HIGH assumes none at all. The lowest column is the gauge's under-voltage trip,
2.50 V per cell (`pcb_pack_protection.yaml` line 101), where the kit still runs.

| Case | Battery W | 16.8 V | 14.4 V | 12.0 V | 10.0 V | Per cell at 12.0 V (3P) | Against |
|---|---|---|---|---|---|---|---|
| PS-TYP PLAN / HIGH | 63.0 / 120.6 | 3.7 / 7.2 A | 4.4 / 8.4 A | 5.3 / 10.1 A | 6.3 / 12.2 A | 1.8 / 3.4 A | 10 A continuous: HIGH passes it below 12.1 V |
| PS-BUSY PLAN / HIGH | 92.0 / 134.4 | 5.5 / 8.0 A | 6.4 / 9.3 A | 7.7 / 11.3 A | 9.3 / 13.7 A | 2.6 / 3.8 A | HIGH passes 10 A below 13.5 V |
| PS-TYP plus both outlets, PLAN / HIGH | 150.2 / 208.9 | 8.9 / 12.4 A | 10.4 / 14.5 A | 12.6 / 17.6 A | 15.3 / 21.5 A | 4.2 / 5.9 A | PLAN passes 10 A below 15.0 V; HIGH passes 18 A below 11.75 V |
| the PA keyed alone over PS-TYP, 75 W / 113 W | 143.9 / 184.0 | 8.5 / 10.9 A | 10.0 / 12.8 A | 12.1 / 15.5 A | 14.6 / 18.8 A | 4.0 / 5.2 A | 10 A below 14.4 V at 75 W; 18 A below a 10.42 V stack at 113 W, which the 12.4 V PA-alone rest floor excludes |
| PS-ALLTX PLAN | 203.8 | 12.1 A | 14.2 A | 17.2 A | 20.9 A | 5.7 A | the 18 A peak at an 11.48 V stack; the 20 A trip (2 s) at 10.42 V |
| PS-ALLTX HIGH | 272.0 | 16.1 A | 18.9 A | **23.0 A** | **28.2 A** | 7.7 A | the 20 A trip below 13.65 V; the 25 A blades below 11.12 V |
| PA key-on step at the pack | 76 to 115 at VBAT | | | 6.4 to 9.6 A | | | sag = step x (pack DCR + 22.5 mOhm), 0.5 to 1 V (W2 section 6) |

**Converter peaks (PS-ALLTX PLAN / HIGH):**
- **+5V_S1:** 4.65 / 4.66 A against the AP64500's 5 A. This is `fnd/r4a` open item O-15, now quantified with AsiaRF's
  9.1 W.
- **+5V_DEV:** 5.89 / 7.8 A. At `1f614233` this was over the AP64500's 5 A (W2 F-PR-04). On `main` the rail is an
  LM5176 stage whose current loop holds 7.2 to 9.5 A (`gen_sch_a.py` lines 110 to 115): PLAN is under it, and HIGH,
  7.8 A, is inside that band, so a stage at the band's low end would limit there (INFERRED).
- **+13V8_PA:** 5.4 / 8.2 A.

## 8. Charging, briefly

- **Charge current.** The session item under D-06 is `fnd/r4a` S-20: ChargeCurrent at most 3.0 A for 4S3P. That is
  1.0 A per cell, the sheet's cycle-life charge current (3.5: 1,020 mA). At 3.0 A, 46.5 W goes into the pack.
- **Heat added inside while charging.** The charger at about 0.98 (Fig. 8-4) and the front end at 0.95 to 0.97 add
  **2.4 to 3.4 W** of converter heat on the power into the pack. The same stages lose **3.3 to 4.7 W** more on the
  loads' own power when PS-TYP runs from shore. The pack's own I2R adds **0.4 to 0.7 W**.
- **Time.** The constant-current phase to about 80 % takes about 2.7 h (0.8 x 10.05 Ah / 3 A, INFERRED). The CV tail
  is TBD.
- **Charging at 0 C** gives only 60 % capacity (7.6).
- **Without a host** (the 256 mA default) and the rest of the charger state sequence: that is the battery-protection
  stream's review item (review section 2), not repeated here.

## 9. Thermal

### 9.1 Heat and enclosure state, applied only where they belong

Heat inside is battery W plus the cells' own I2R, less what the outlets deliver outside. This slightly overstates it,
by what the antennas radiate and what the monitor glass sheds outward. Each state is applied only to the enclosure
state it runs in:
- lid open with fans for the normal states;
- lid closed with fans for the reduced mode (D-02b) and for PS-RED-b in transport;
- lid open for PS-RED above +35 C.

PS-ALLTX, and the PA keyed on its own, are bursts (section 7.2), never steady states.

**Corrected in the second cycle:** the first version added the cells' own I2R only to the cells' rise over the air
around them. The same watts also warm that air, and they are now counted there too (0.2 W in PS-RED to 2.7 W in
PS-BUSY, and 7.25 W with both outlets on). On shore, the front end's and charger's loss on the loads' own power is
now counted as well as the loss on the power into the pack.

**Conductance, inside air to ambient (W/K):**
- **W4's independent lumped bound:** 1.22 to 2.85 with the lid open and fans on, 1.06 to 2.49 lid closed, and 0.77 to
  1.57 lid open with fans off. It uses textbook film coefficients (`fnd/w4` `drafts/w4-scratch-thermal.py`), and
  `ARCHITECTURE.md` section 8.2 carries it on `fnd/i3`.
- **Appendix 32.53's own figures** (line 2860): 3.0 to 3.3 lid open with fans, "about 2.1 W/K still" lid open with
  no internal fans (the plate's 1 W/K and the walls' 1.1 W/K with still air inside), and 1.5 to 2 lid closed with
  fans. 32.53 gives no lid-closed figure without fans.
- Neither is a measurement.

| State, enclosure | Heat inside, PLAN (HIGH) W | Rise on W4's bound, PLAN heat (K) | Rise on 32.53's conductance (K) | Worst corner, HIGH heat on the lowest conductance (K) |
|---|---|---|---|---|
| PS-IDLE-SPEC, lid open, fans | 43.4 (85.4) | 15.2 to 35.6 | 13.2 to 14.5 | 70.0 |
| PS-TYP, lid open, fans | 64.2 (126.2) | **22.5 to 52.7** | 19.5 to 21.4 | 103.4 |
| PS-TYP, lid open, **fans off** (a fan failure; the fans' own 3.1 W still counted, see below) | 64.2 (126.2) | 40.9 to 83.4 | 30.6 (2.1 W/K still) | 163.9 |
| PS-TYP plus both outlets, lid open, fans (77.4 W leaves by the outlets) | 80.0 | 28.1 to 65.6 | 24.3 to 26.7 | |
| PS-BUSY, lid open, fans (sustained bound) | 94.7 (141.4) | 33.2 to 77.6 | 28.7 to 31.6 | 115.9 |
| PS-EMCON, lid open, fans | 54.0 (107.4) | 18.9 to 44.2 | 16.4 to 18.0 | 88.0 |
| PS-RED, **lid closed**, fans | 22.4 (46.7) | 9.0 to 21.1 | 11.2 to 14.9 | 44.0 |
| PS-RED-b, lid closed, fans | 36.1 (73.5) | 14.5 to 34.1 | 18.1 to 24.1 | 69.3 |

The fans-off row keeps the fans' own power in the heat, 3.1 W at PLAN and 4.9 W at HIGH at the battery, but a failed
fan draws nothing. The row therefore overstates the rise by up to 1.5 K (2.3 K at HIGH) on 32.53's 2.1 W/K and 2.0
to 4.0 K on W4's still-air bound, in the safe direction (`drafts/pwr_budget.json` `thermal.TYP_fans_off`).

The envelope's 10 K (one module) and 16 K (three loaded) (`OPERATING-ENVELOPE.md` line 91; `pcb_envelope.yaml`
`inside_air_rise_k`) sit below even 32.53's conductance applied to this page's PS-TYP heat, and far below PS-BUSY's.

### 9.2 Local temperatures against their limits

The margins above inside air are TBD for most modules: no maker publishes a module's own rise, and the east pocket
under board B has no local model. So each ceiling below is the **highest ambient at which the inside air alone
reaches the part's limit, or, for the cells, the inside air plus the cells' own I2R**. A part's real ceiling is lower
by its own rise.

**The pack model.** The pack block is 56.65 x 133.5 x 38.1 mm (A06), 0.030 m², at 5 to 15 W/m²K (INFERRED), which
gives 0.148 to 0.445 W/K. The cells' I2R is taken at the 14.4 V nominal, the run's average; the end of the discharge
is higher.
- In PS-TYP the pack I2R is 1.27 W. It puts the cells 2.9 to 8.6 K above the air around them, and adds 0.4 to 1.0 K
  to that air.
- In PS-BUSY it is 2.7 W, and with PS-TYP plus both outlets 7.25 W.
- While charging at 3 A it is 0.42 to 0.72 W.

**Ambient ceiling (C), worst to best on W4's bound, then [on 32.53's conductance].** For each limit, this is the
ambient at which it is reached. The charge column includes the charging heat: the charge path's loss, plus, on shore,
the front end's and charger's loss on the loads' power. Where the input cannot carry both, this is an upper bound.
The bracketed figures pair 32.53's enclosure conductance with the pack block's mid conductance, 0.30 W/K; W4's pair
the enclosure's and the block's extremes, lowest with lowest (section 7.1). The fans-off row's bracket is a single
figure because 32.53 gives a single still-air conductance, 2.1 W/K.

| Case | cells, **charge** 0 to 45 C (sheet 3.12; gauge line 145) | cells, **discharge** -10 to 60 C (3.12; gauge line 154) | SGP41 +55 C absolute (Table 5; recommended -10 to +50 C, Table 4) | AW7915-AED +70 C (own 4 to 9 W rise TBD) | LimeSDR Mini v2.4 +70 C (own rise TBD; its maker suggests extra cooling) | RM520N-GL +75 C, 3GPP range (up to 5.6 W own rise TBD) |
|---|---|---|---|---|---|---|
| PS-IDLE-SPEC, lid open | -0.1 to 26.8 [26.6 to 28.1] | 20.4 to 43.4 [43.5 to 44.9] | 19.4 to 39.8 [40.5 to 41.8] | 34.4 to 54.8 [55.5 to 56.8] | off | 39.4 to 59.8 [60.5 to 61.8] |
| PS-TYP, lid open | **-17.8 to 19.4 [19.5 to 21.6]** | **-1.3 to 34.6 [34.3 to 36.2]** | 2.4 to 32.5 [33.6 to 35.5] | 17.4 to 47.5 [48.6 to 50.5] | 17.4 to 47.5 [48.6 to 50.5] | 22.4 to 52.5 [53.6 to 55.5] |
| PS-TYP, lid open, fans off | -52.1 to -0.5 [9.4] | -32.0 to 16.2 [25.1] | -28.4 to 14.1 [24.4] | -13.4 to 29.1 [39.4] | -13.4 to 29.1 [39.4] | -8.4 to 34.1 [44.4] |
| PS-TYP plus both outlets, lid open | not charging: the outlets take the input's headroom | **-54.6 to 15.6 [8.8 to 11.3]** | -10.6 to 26.9 [28.3 to 30.7] | 4.4 to 41.9 [43.3 to 45.7] | 4.4 to 41.9 [43.3 to 45.7] | 9.4 to 46.9 [48.3 to 50.7] |
| PS-BUSY, lid open | -43.4 to 8.6 [9.2 to 12.3] | **-36.0 to 20.6 [19.2 to 22.1]** | -22.6 to 21.8 [23.4 to 26.3] | -7.6 to 36.8 [38.4 to 41.3] | -7.6 to 36.8 [38.4 to 41.3] | -2.6 to 41.8 [43.4 to 46.3] |
| PS-EMCON, lid open | -9.1 to 23.0 [23.0 to 24.8] | 9.7 to 39.0 [39.0 to 40.6] | 10.8 to 36.1 [37.0 to 38.6] | 25.8 to 51.1 [52.0 to 53.6] | off (gated) | 30.8 to 56.1 [57.0 to 58.6] |
| PS-RED, lid closed | 14.6 to 33.1 [24.9 to 29.4] | 37.8 to 50.7 [44.6 to 48.3] | 33.9 to 46.0 [40.1 to 43.8] | off | off | off |
| PS-RED, lid open (above +35 C) | 18.1 to 34.4 [33.9 to 34.8] | 40.6 to 51.8 [52.0 to 52.7] | 36.7 to 47.2 [47.5 to 48.2] | off | off | off |
| PS-RED-b, lid closed | 1.0 to 27.4 [15.3 to 22.2] | 23.2 to 44.6 [34.5 to 40.6] | 20.9 to 40.5 [30.9 to 36.9] | 35.9 to 55.5 [45.9 to 51.9] | off | 40.9 to 60.5 [50.9 to 56.9] |

**Cells in PS-TYP at +20 C ambient, lid open, fans on: 45.4 to 81.3 C** (43.8 to 45.7 C on 32.53's conductance). At
the pessimistic end of the independent bound, the runtime requirement's own condition would open the gauge's
discharge FET. At the optimistic end it runs with 15 K to spare. Above the discharge window the protection is
permanent: on `main` since `d90f30e4` the second level's own thermistor opens F2 at 62.7 to 77.5 C, and the battery
stream's proposed image adds the gauge's SOT permanent failure at 65 C for 5 s (`review-packets/battery/`
`PROTECTION-ARCHITECTURE.md` line 170). So C1's +55 C and the gauge's +60 C, which act first and recover, are what keep
a hot kit usable. Every other allowed combination is in the table of
section 7.1.

**With the fans off** (a fan failure) at +20 C, on 32.53's own 2.1 W/K still-air figure:
- with the fans' own 3.1 W counted, as the rows above count it, the inside air reaches about 50.6 C and C1 acts on
  its +50 C air trigger. The cells, at about 54.9 C, sit 0.1 K under its +55 C cell trigger;
- with the fans stopped and drawing nothing, the air is about 49.0 C and the cells about 52.9 C. That is under both
  of C1's triggers, and 7.1 K inside the 60 C window, so C1 need not act.

On W4's still-air bound the cells reach 63.8 to 112.0 C, less 2 to 4 K for the fans' own power (INFERRED, the
fans-off rows of 9.1 and above), and C1 sheds to slot 3. So on the design record's own conductance PS-TYP at +20 C
keeps about 5 to 7 K to the discharge window once the fans stop, and sits at C1's triggers; on the independent
bound it does not hold.

**The other +70 C rows of `pcb_part_temps.yaml` share the AW7915-AED and LimeSDR column.** They are the Pulse
H5007NL magnetics (line 22, 0 to +70 C), the Xenarc 709GNK (line 43, -20 to +70 C, in the plate) and the SA868 (line
83, -30 to +70 C). The model prints the SA868 and Xenarc rows beside the two modules (`drafts/pwr_budget.out`). The
same ceilings apply to the H5007NL, with its own rise TBD.

**The chemical fuse F2 against its +60 C.** F2 (Eaton SCF9550-30-05, -20 to +60 C operating) sits on board P beside the
block, taken here at the cells' temperature (INFERRED). Its ceiling in every row is the discharge column's, less its
own rise over the cells. That rise is TBD: 0.1 to 0.25 W at 10 A and 0.32 to 0.81 W at 18 A of its own, with no
thermal resistance or current derating published (section 7.2). So its margin is unknown in every row. Wherever a
cell may reach +55 C, which C1 and K2 allow, F2's margin is at most 5 K less its own rise. At the pessimistic end of
the bound in PS-TYP at +20 C, F2 is past +60 C wherever the cells are. PWR-F12 carries the reading that closes it.

**Parts with a published thermal resistance:**
- **KSZ9897RTXI:** 11.3 C/W on a 6-layer JESD51 board (DS00002330D Note 6-3) times 2.54 W gives +28.7 K
  junction-to-air. It is rated -40 to +85 C ambient (industrial, Note 6-1).
- **PI7C9X2G404SL:** 25.5 C/W times 0.62 to 1.07 W gives +16 to +27 K, with a 125 C junction maximum (DS40068 Table
  13-1). It is rated -40 to +85 C ambient (Table 12-7).
- **AP2112K LDOs in SOT-23-5 (184 C/W, DS39724 Rev 2-2; 150 C junction absolute maximum):**
  - U27, the KSZ's 2.5 V from 3.3 V, at 0.33 A: 0.26 W, **+49 K**.
  - U40, U50 and U60, the supervisors' 3.3 V from 5.1 V: 0.24 W at PLAN (**+43 K**); 0.34 W with the H743 at 200 MHz
    VOS3 at its 85 C maximum (+63 K); **0.83 W at the H743's 400 MHz all-peripherals maximum (+152 K), past the
    part's absolute maximum at any inside air.**

### 9.3 The +35 C and +25 C restrictions are proposed controls, and the controls this page takes

The owner accepted both with D-02b: one module above +35 C ambient, and charging held off above about +25 C with three
loaded modules. They are derived from `OPERATING-ENVELOPE.md` section 3's 10 K and 16 K rises. With this page's heat
per state:
- **+25 C** is not supported even on 32.53's own conductance. The charge ceiling for three *typical* modules is +19.5
  to +21.6 C, and PS-BUSY's is +9 to +12 C. On the independent bound it is anywhere from -18 to +19 C.
- **+35 C** is supported for the discharge window only at the optimistic end. PS-TYP reaches the cells' 60 C at
  ambients from about -1 C to +35 C on the bound, and +34 to +36 C on 32.53's conductance.
- **In the reduced mode** (lid closed), charging holds off above +15 to +33 C on the bound, and +25 to +29 C on 32.53's
  conductance. The envelope does not say so today.

Both stay **proposed controls until analysis and measurement support them**. That means TEST-PLAN E3 plus the owed
inside-air rise test per state, lid open and closed (`ARCHITECTURE.md` section 8.2).

**Taken by the session under the owner's standing rule of 26 September 2026 (PROVISIONAL):** implement the
restrictions as controls driven by *measured* pack current and temperatures, keeping the ambient figures only as
documentation. This makes the design indifferent to the conductance uncertainty instead of betting on one end of it.
The sensors exist on `main`:
- the gauge's pack current through the 2 mOhm shunt R10 (`gen_sch_p.py` line 209);
- the four cell thermistors TS1 to TS4, one per series group (`gen_sch_p.py` lines 210 to 221), read by the gauge;
- the inside air: the BME688 on board E (`gen_sch_e.py` lines 543 to 545) and the TMP117 under the coolers on board B
  (`gen_sch_b.py` line 1050).

The controls:
- **Charging (existing, in the gauge):** the gauge's own 0 to 45 C cell window (`pcb_pack_protection.yaml` line 145)
  holds the charge whatever the ambient. It is a data-flash setting in the gauge, independent of the host.
- **C1, module shedding (firmware, panel and bridge):** shed to one module (slot 3) when the inside air reaches +50 C
  (the SGP41's recommended maximum) or any cell thermistor reaches +55 C. Restore 5 K below.
- **C2, the outlet budget (new, firmware, panel and bridge):**
  - The triggers: the gauge's pack discharge current, averaged over 10 s, above 9.0 A; or any cell thermistor at
    +50 C.
  - The order: the USB-C outlet is shed first, then PoE.
  - The restore, so that it cannot cycle:
    - After a current shed, an outlet comes back only when the PREDICTED current has stayed under 8.0 A for 60 s.
      The prediction is the measured 10 s average plus the outlet's own contract at the present stack voltage: 32.4 W
      / 0.88 for PoE, 45 W / 0.93 for USB-C, each over the stack voltage.
    - Example: PS-TYP with PoE draws 7.0 A at 14.4 V. With USB-C back it predicts 10.4 A, so USB-C stays off.
    - A shed on temperature latches until the operator re-enables the outlet. The bridge tells the operator which
      trigger acted.
  - The software enables are `PD_SW_EN` (U28 pin 13) and `POE_SW_EN` (U27 pin 8) on `main` (`gen_sch_a.py` lines
    1124 and 1119). The stage enables PD_EN and POE_EN are those ANDed with the S-14 NAND's OUTLET_OK (lines 1095
    and 1103). At `1f614233` the software pins were PD_EN and POE_EN themselves.
  - The 9.0 A trigger sits 1.0 A under the declared continuous rating, for the current measurement's error. The
    coulomb counter's gain error is up to ±0.8 % of full-scale range, whose limits are ±VREF1/10, about ±0.12 V
    (SLUSC67B 6.14). Through the 2 mOhm shunt that is 0.5 A if the percentage is of one side of the range, and 1.0 A
    if it is of the whole span. The error after calibration (SLUSC67B 8.2.1) is TBD, so the trigger is re-derived at
    bring-up.
  - The temperature trigger sits 5 K under C1's, so the outlets, which serve no core function, go before any module.
- **C3, a current trigger for C1 (new, firmware):**
  - The trigger: with both outlets already off, a 10 s average pack current above 9.0 A for 30 s sheds to one
    module, as C1 does. It bounds the HIGH corners of PS-TYP, PS-EMCON, PS-BUSY and the heater overlay at the end of
    discharge.
  - The restore: the shed modules come back when the predicted current has stayed under 8.0 A for 60 s and C1's
    triggers are clear. The prediction is the measured 10 s average plus 8.7 W per module at the pack (board B's
    declared 1.6 A at 5 V through its rail at about 0.92) over the stack voltage. A shed on C1's temperatures restores
    as C1 states.
- **C2 and C3 ignore a PA key-down.** Their averages and timers are held while PA_EN is asserted and for 10 s after it
  drops. So a transmission is never cut by a module or outlet shed; K1 to K5 and C4 bound it instead. K3 makes C2 and
  C3 act before a key-down starts, not during it.
- **C4, the in-key guard (new, firmware):**
  - During any PA key-down, the panel and bridge read the gauge's pack current and cell voltages at its 1 s update
    (SLUUAQ3A 5.2: readings every 250 ms, status decisions at 1 s intervals).
  - They unkey the PA when the current reads more than 18 A, or any cell under 2.70 V.
  - They also unkey it when the PA's flange reads +85 C, and K2 keeps it from keying above +75 C (fifth cycle;
    section 7.2 gives the basis). The flange is read at the same 1 s interval. The sensor is PWR-F15.
  - The 1 s update fits inside the gauge's OCD2 delay of 2 s at 20 A and its CUV delay of 4.0 s at 2.50 V per cell
    (`pcb_pack_protection.yaml` lines 110 and 101). So a key-down the floors mispredict ends as a short transmission,
    not as a dark kit. Mispredictions include a cold or aged pack and a PA drawing more than 113 W. The timing
    margin, about 1 s against OCD2, is INFERRED and is checked at bring-up.
- **Backstop, not a control (battery-protection stream):**
  - Today nothing acts between 10 A and 20 A, for any duration. The gauge trips at 20 A for 2 s (line 110), and the
    blades carry 19 A at 65 C (`pcb_fuse_derating.yaml` line 46).
  - The gauge has two independent over-current-in-discharge levels, each with a threshold and a delay of 0 to 255 s
    (SLUUAQ3A section 2.5 and 14.9.6 to 14.9.7).
  - Proposed: OCD1 at 11 A for 90 s. A sustained current above the continuous rating then opens the discharge FET if
    C2 and C3 fail, while a 60 s key-down passes. K1's 2 s gap returns OCD1 to Normal between key-downs, and K3
    keeps its timer from running into a key-down. OCD2 stays the 20 A for 2 s now declared.
  - The recovery the proposal assumes is the manual's default, kept: +200 mA for 5 s (SLUUAQ3A 14.9.8). The
    discharge FET closes again only after the pack has been charged at 200 mA or more for 5 s. So on battery a
    backstop trip leaves the kit dark until an input returns. This is taken as the safe state: a trip means C2 to C4
    have failed, and restarting into the same load would repeat it. It is part of PWR-F13's cost.
  - The gauge's permanent Safety Overcurrent in Discharge stays off the FUSE list, or above OCD2 (section 7.2,
    PWR-F12).
  - **Which level carries what is OPEN with the battery stream** (fifth cycle). This page calls the declared 20 A for
    2 s trip (`pcb_pack_protection.yaml` lines 107 to 110) OCD2 and the backstop OCD1. The battery stream's proposed
    golden image, on `main` at `01469100`, puts the 20 A for 2 s on OCD1 and proposes OCD2 at 24 A for 1 s, "TBD
    by the reviewer" (`review-packets/battery/PRIMARY-CONFIGURATION.md` lines 120 and 121). The gauge has two
    firmware levels (SLUUAQ3A 2.5), so the two proposals together ask for three settings. This page needs one level
    at 11 A for 90 s and one at the declared 20 A for 2 s; the names are immaterial. Above 20 A the AFE's AOLD (30 A
    class, 20 ms, the same packet's line 122) already acts in hardware. If the 24 A level is kept, the backstop has
    no level and nothing acts between 10 A and 20 A if C2 and C3 fail. The golden image is the battery stream's.

These are firmware contract items for the panel and bridge (W5 contract), not board changes. What they cost the
operator is PWR-F13.

### 9.4 Parts outside the adopted envelope, found by this stream

| Part | Maker's range | Envelope | What follows | Owner |
|---|---|---|---|---|
| AsiaRF AW7915-AED (two, bought) | operating 0 to +70 C (PDF v1.0, 2023) or -10 to +70 C (product page, 2026); storage -20 to +90 C | -20 to +40 C in use | outside at the cold end; at the hot end its own 4 to 9 W rise is TBD and no heat path is designed | session (parts); a row is proposed for `pcb_part_temps.yaml` (section 11) |
| LimeSDR Mini v2.4 (bought) | operating **0 to +70 C**, storage **0 to +70 C**, "Commercial-grade" | -20 to +40 C in use; -20 to +45 C storage; +71 C storage margin | outside at the cold end in use and in storage, and below the +71 C storage margin (D-02a); the maker notes extra cooling may be needed | session (parts) |
| NVMe 2242 (not picked) | commercial grades 0 to +70 C; the representatives offer -20 to +85 C (Advantech "Minus Temperature") and -40 to +85 C (both) | -20 C | the pick must be a -20 C or industrial grade | session (parts) |
| Eaton SCF9550-30-05 chemical fuse F2 (on `main`) | operating -20 to +60 C; no current derating published (ELX1135, quoted in `gen_sch_p.py` lines 255 to 272) | -20 to +40 C in use | inside the ambient range, but it sits at the block's temperature plus its own 0.1 to 0.81 W; its margin at C1's +55 C cell trigger and during a key-down is unknown (section 9.2) | battery-protection stream (PWR-F12); a row is proposed for `pcb_part_temps.yaml` |
| Mitsubishi RA30H1317M1 VHF PA (the pick; its flange bolts to the plate) | case -30 to +100 C in operation; "best to keep the module case temperature (Tcase) below 90°C" for long-term reliability (Maximum ratings; Thermal Design of the Heat Sink) | -20 to +40 C in use | inside at rest. During a key-down its flange sits on the plate's local patch, which the record's own figure takes past 90 C within 60 s (section 7.2) | board D's owner (PWR-F15); a row is proposed for `pcb_part_temps.yaml` |
| KSZ9897RTXI, PI7C9X2G404SL, TUSB8041I, E72, E22, LG290P | -40 to +85 C | | inside | none |

## 10. Findings, the proposed experiment and prepared questions

| ID | Finding | Status | Bound and owner |
|---|---|---|---|
| PWR-F01 | Board B declares the WiFi card rails +3V3_S1A and +3V3_S3A at 0.5 A typical and 1.5 A peak (`gen_sch_b.py` lines 154 and 158 on `main`, where `fnd/r4b` merged at `458b2873`: slot 2's socket went to 3.0 and 4.0 A for the RM520N-GL, F-PR-05, and the note for slots 1 and 3 still says "the AsiaRF AW7915-AED, 1.5 A", line 164). AsiaRF asks for a 3.3 V supply of 3 A (2.5 A minimum), or 3.5 A (3 A minimum) in its 2023 PDF, and gives a 9 to 9.1 W maximum (2.76 A). | VERIFIED maker figure; the declaration is below it | declare at least 3.0 A peak so dc_drop and derate judge the copper at the right current; board B's owner |
| PWR-F02 | Slot 1's 5 V rail reaches 4.65 A in PS-ALLTX PLAN against the AP64500's 5 A, with the card at 9.1 W and the module at its declared 1.6 A. This is O-15 of `fnd/r4a` quantified. | INFERRED | 7 % margin; board A's owner |
| PWR-F03 | KSZ9897R at 1000 Mb/s draws 1.21 A typical on its 1.2 V rails against +1V2_KSZ's 0.5 / 0.8 A declaration (`gen_sch_b.py` line 204), and 330 mA on AVDDH against +2V5_KSZ's 0.15 / 0.25 A (line 208). The parts (TPS62933 3 A, AP2112K 0.6 A) can carry it; the declarations cannot. | VERIFIED datasheet, declaration below it | board B's owner |
| PWR-F04 | The supervisor LDOs dissipate (5.1 - 3.3) V x I in SOT-23-5 at 184 C/W. At the H743's own maximum they pass the 150 C junction limit. | VERIFIED data, INFERRED arithmetic | bound the supervisor firmware clock and peripheral set (at most 200 MHz VOS3 keeps the LDO under +63 K), or feed the LDOs from 3.3 V; board B's owner and the firmware contract |
| PWR-F05 | TUSB8041's four-SS-devices row is 778 mA on VDD against +1V1_Sx's 0.7 A peak (`gen_sch_b.py` line 178). The kit's device mix (one SS device, the LimeSDR) uses the 395 mA row. | VERIFIED | minor; board B's owner |
| PWR-F06 | The slot 3.3 V bucks are AP64500SP-13 (`gen_sch_b.py` lines 346 to 351 on `main`), while line 58 still calls "the twelve per-slot rails" AP63203. The rail note that did the same at `1f614233` (its line 144) was corrected when `fnd/r4b` merged (line 161 now says AP64500). | VERIFIED comment drift | minor; board B's owner |
| PWR-F07 | The planning budget rose: PS-IDLE-SPEC 32.4 to 42.8 W, PS-TYP 60.1 to 63.0 W. Aged runtime falls to 2.5 h and 1.7 h. | PROVISIONAL | integrator: CONOPS 4a and 6, ARCHITECTURE 8 and 11 |
| PWR-F08 | The +25 C charge restriction is not supported on 32.53's conductance with this page's heat (+19.5 to +21.6 C), and the +35 C one only at the optimistic end. | INFERRED | proposed controls stand; measured-current and measured-temperature controls taken (section 9.3); integrator: OPERATING-ENVELOPE section 3 wording |
| PWR-F09 | AW7915-AED and LimeSDR Mini v2.4 are outside the envelope's cold end (and the LimeSDR its storage range), and neither is in `pcb_part_temps.yaml`. | VERIFIED | session (parts): accept as carve-outs warmed by the kit, or replace; rows proposed |
| PWR-F10 | `pcb_part_temps.yaml` still lists the cells under `owed` (line 95) while `OPERATING-ENVELOPE.md` cites the Samsung sheet's 3.12 (line 55). | VERIFIED | integrator: move the cells to a real row with clause 3.12 |
| PWR-F11 | The SGP41's short-term storage maximum is +70 C (Table 5), under the +71 C storage margin (D-02a), and its recommended storage is 5 to 30 C (Table 4). | VERIFIED | survive-and-recover judgement at E3; the battery or sensor stream |
| PWR-F12 | **The pack chain's current contract needs re-declaring.** (1) Every stage declares 10 A continuous and 18 A peak, with no duration for the peak (`pcb_energy_chain.yaml` lines 48 and 49 and the six stages after; `pcb_pack_protection.yaml` lines 28 and 29). The protection test proves 10 A for an hour (line 114), and board A's copper is judged at 10 A (`dc_drop.py` lines 258 to 264). (2) Against it: modes the design can switch on sustain more than 10 A (section 7.1), and every PA key-down makes up to 18 A a service current for its 60 s, the all-transmit case and the PA keyed alone alike. That is the question appendix 32.244 left unwritten. (3) Nothing protective acts between 10 A and 20 A for any duration (section 9.3). (4) The parts on the path (section 7.2). Rated above 18 A: the cells, the blades, their Keystone 3568 holders, Q1 and Q2, the XT60, the dock block and the 2 oz bands. Declared only: the shunt R10 at 2 W, and on `main` board A's R17 (5 mOhm, 1.62 W at 18 A against a 3 W part whose sheet is not held). Not yet judged at 18 A: board A's pack node, 7.19 mm of 1 oz copper at 10 A and 16.18 mm at 18 A, or 3.60 and 8.09 mm at 2 oz (appendix 32.244); appendix 32.246 already found VBAT's 10 A under its own loads' 15.18 A typical. Not proven at 18 A: the chemical fuse F2 (SCF9550-30-05), -20 to +60 C with no current derating published, 0.32 to 0.81 W of its own at 18 A, at the block's temperature; its margin during a key-down from a +55 C cell is unknown (`gen_sch_p.py` lines 273 to 276; `fnd/r4p` O-8), and the energy chain does not carry it (O-13). (5) F2 is also a target of the gauge's permanent failures: Safety Overcurrent in Discharge at its default, 10 A for 5 s (SLUUAQ3A 3.5, 14.10.4), would fire it on most key-downs longer than 5 s. It is off by default (14.2.5.1), and the battery stream's proposed image keeps SOCD at 0 (`PRIMARY-CONFIGURATION.md` line 137). | VERIFIED declarations and documents; INFERRED arithmetic | **Taken by the session under the owner's standing rule of 26 September 2026:** declare 10 A continuous, held by C2 and C3; 18 A for 60 s as the service rating every PA key-down needs; 20 A for 2 s as the trip. Judge board A's pack-path copper at 18 A (on `main` CELL+, CELL_FUSED and VBAT, `gen_sch_a.py` lines 24, 34 and 47; VBAT and CH_SRP at `1f614233`), unless a transient analysis of that copper at 60 s shows otherwise. Carry F2 as a stage of the energy chain. Extend the protection test: 18 A for 60 s from a block at +55 C, with a thermocouple on F2's body reading at most +60 C. Keep Safety Overcurrent in Discharge off the FUSE list, or above OCD2. Set OCD1 at 11 A for 90 s with the default recovery (SLUUAQ3A 14.9.6, 14.9.8); which level carries it is OPEN with the battery stream, whose proposed image uses both levels (section 9.3). Draft: `drafts/pwr-chain-redeclaration.yaml`. Owners: the battery-protection stream (the two YAML files, the gauge, the golden image, the test, and Eaton's answer on F2 above +60 C); board A's owner (the copper); the owner only for the price of 2 oz if that is the answer. **The 60 s of every PA key-down holds only once this closes** (and, on the PA side, PWR-F15). If F2's body reads above +60 C, K2's +55 C gate comes down by F2's measured rise over the cells. |
| PWR-F13 | **On battery at +20 C, the outlets, PS-BUSY and long transmissions are bounded, not sustained** (section 7.1). Under C2, with three typical modules, 32.53's conductance holds the cells under C2's +50 C only below about +15.3 to +17.4 C ambient with PoE alone, and +12.5 to +14.7 C with USB-C alone. Both outlets together stay on only near 0 C, or at the top of the charge, where the current stays under 9 A above a 16.6 V stack. On W4's bound it is far lower. PS-BUSY reaches C1's +55 C at +20 C on every conductance in the record; how long it runs first depends on heat capacities that are TBD (TEST-PLAN E3). A transmission lasts at most 60 s (K1), and less at the hot end of the envelope, where C4's flange cut ends it (on 32.56's figure about 25 to 47 s from a +50 C plate), and the PA keys again only once its flange is under +75 C (K2, PWR-F15). A key-down waits for C2 and C3 when the pack is over 9.0 A (K3), which can delay it by up to about 40 s (C3's 30 s plus the 10 s average). The PA stops keying below a 12.4 V rest voltage (K5). A backstop trip on battery leaves the kit dark until an input returns (section 9.3). | INFERRED | REQ-017 (outlets; deferred for prototype 1, `fnd/i1`) should carry "on battery, inside the outlet budget"; the runtime and PS-BUSY rows in CONOPS 4a should say "bounded"; the VHF rows should state the 60 s key-down. Session (requirements), through the `fnd/i1` integrator; the owner only if it becomes a product claim. |
| PWR-F14 | **The PA keyed on its own, and the heater, were not judged in the second cycle.** (1) The PA keyed alone over PS-TYP draws 10.0 A at a 14.4 V stack and 14.6 A at 10.0 V; at the PA's 113 W it draws 10.9 A at a full 16.8 V stack to 18.8 A at 10.0 V, and passes 18 A below a 10.42 V stack (section 7.1). `CONOPS.md` line 345 gives its worst duty as "key-down for minutes (32.53 line 2860), inside the key-down bound of D-11", and the citation is right: appendix line 2860 (32.53's thermal basis) reads "The 200 W peak (PA key-down) lasts minutes and goes into about 8 to 10 kJ/K of thermal mass, about +10 K transient". The record's second key-down figure is 32.56, line 2940: "a 20 s key-down at 45 W warms the local patch about 15 K", the patch the PA's flange bolts to. The PA's own key-down heat is 32.52 item 6 (line 2852), "45 W at key-down at APRS duty". (Corrected in the fourth cycle: this row had said that line 2860 holds no duration. Corrected in the fifth: the fourth had called 32.53's "minutes" the record's only key-down duration.) (2) The heater is on VBAT behind a software pin (HEAT_EN, `gen_sch_a.py` line 1119 on `main`), and `CONOPS.md` lines 280 and 281 count it on the battery in the cold. Nothing turned it off during a key-down, and with it on the all-transmit basis needs 15.79 V, past the 15.5 V floor (section 7.2). | VERIFIED sources; INFERRED arithmetic | **Taken by the session under the owner's standing rule of 26 September 2026:** the key-down rules K1 to K5 for every PA key-down, the PA-alone floor of 12.4 V, and the in-key guard C4 (sections 7.2 and 9.3). K1's 60 s sits between the record's two figures. It is a PROVISIONAL tightening of 32.53's "lasts minutes", not a gap filled: the chain declares 10 A continuous and an 18 A peak with no duration (`pcb_pack_protection.yaml` lines 28 and 29), F2's margin at 18 A is unknown, and at the worst adiabatic rate the cells use the 5 K between K2's +55 C and the 60 C window in 93 s (section 7.2). It is three times 32.56's 20 s, so on the PA side it holds only with PWR-F15's flange limits. Owners: session, through the W5 contract (panel and bridge); the integrator for `CONOPS.md` line 345's duty, a change to the record from "minutes" to at most 60 s per key-down with its 32.53 citation kept and 32.56's added, and REQ-018's wording. |
| PWR-F15 | **The PA's case during a key-down is bounded by nothing the design measures.** The design record gives the plate's local patch under the RA30H1317M1's flange +15 K for a 20 s key-down at 45 W (appendix 32.56, line 2940). Taken linear, a 60 s key-down from a +50 C plate ends at 95 C at 45 W and 118 C at 68 W, before the flange interface, which the sheet does not publish. The maker's limits are "below 90°C" for long-term reliability and -30 to +100 C in operation (RA30H1317M1 sheet, October 2011, Thermal Design of the Heat Sink and Maximum ratings; section 7.2). Repeated key-downs start from a hot patch. No temperature part on any board sits on or near the flange. On `main` they are board P's cell thermistors TS1 to TS4 (`gen_sch_p.py` lines 210 to 221), its second level's own thermistor on J_TS2 (line 418, since `d90f30e4`) and the PTC element RT1 beside Q1 and Q2 (line 243), board E's BME688 (`gen_sch_e.py` lines 543 to 545) and board B's TMP117 under the coolers (`gen_sch_b.py` line 1050). | VERIFIED record and datasheet; INFERRED arithmetic | **Taken by the session under the owner's standing rule of 26 September 2026 (PROVISIONAL):** a temperature sensor on the PA's flange, read by the panel and the bridge; K2 gates key-on at +75 C on it and C4 unkeys at +85 C (sections 7.2 and 9.3). Board D already sits on the kit I2C bus (its PCA9555 at 0x26, `gen_sch_d.py` line 15), as board B's TMP117 does. Owners: board D's owner (the sensor, its lead and its bus address; the flange is the module's RF ground, pin 5); the W5 contract (the two thresholds); bring-up or TEST-PLAN E3 (the flange against a thermocouple through 60 s key-downs at 13.8 V into a dummy load from a +50 C plate, and the patch's cooling after one). Until the sensor exists, one key-down from a +50 C plate is bounded at about 30 s on the record's figure, and repeated key-downs are OPEN. |

**Corrections made in the second cycle (26 September 2026, the checker's blocking items), each in the conservative
direction or neutral:**
- **Section 7.1** allowed PS-TYP with both outlets, and PS-BUSY, as "none needed". Both now carry a control.
- **Section 7.2's rest voltages** counted the distribution drop twice. They were 0.17 to 0.39 V high, and the
  sentence calling the HIGH case "not deliverable" was false. The 15.5 V floor stands, with its basis corrected and
  its margin stated.
- **The thermal model** now counts the cells' own I2R in the inside air, and on shore the charge path's loss on the
  loads' power. No ceiling moved up: they fell by up to 4 K with the fans on, and by up to 6.8 K for the charge
  window with the fans off.

**Corrections made in the third cycle (26 September 2026, the checker's three blocking items), each in the
conservative direction or neutral:**
- **Section 7.1** now judges the PA keyed on its own and the heater overlay. The PA-alone key-down is bounded by the
  key-down rules and a floor of its own (PWR-F14), and the section 11 claim is restated to what is tabulated.
- **Section 7.2's floor** claimed a margin "for cold" that the heater alone would use. The heater is now off during
  every key-down (K4), the heater-on case is computed, and the cold is stated as not shown, with the in-key guard C4
  as the enforcement.
- **PWR-F12's parts list** left out the chemical fuse F2, Q1 and Q2, the shunt and the fuse holders. F2 is now named
  as not proven at 18 A near its +60 C, with the gauge's permanent-fail path to it.
- **The distribution resistance** carries F2 at its 2.5 mOhm maximum: 22.5 mOhm instead of 20. Battery W rises by
  at most 0.95 W (PS-ALLTX HIGH), pack currents by at most 0.2 A, and cell temperatures by at most 0.7 K; no ceiling
  rose, and none fell by more than 0.7 K. Every table on this page is re-run with it; the all-transmit basis moves
  from 15.18 V to 15.22 V.

**Corrections made in the fourth cycle (26 September 2026, the checker's blocking item on 32.53):**
- **The key-down duration.** PWR-F14 and integrator item 1 had said that appendix line 2860 "holds no duration" and
  asked for `CONOPS.md` line 331's citation (line 345 at `01469100`) to be corrected. Both statements were wrong: line
  2860 says the 200 W PA key-down "lasts minutes". The citation stands. K1's 60 s is now stated as a PROVISIONAL
  tightening of that record, with its three reasons (section 7.2), and the record's 8 to 10 kJ/K is compared with the
  cells' own heat capacity. No threshold moved. (This cycle also called 32.53's "minutes" the record's only key-down
  duration and closed that as exact. It was false: see the fifth cycle below.)
- **The fans-off conductance.** Section 9.1's fans-off row read "not stated" in the 32.53 column. Line 2860 gives
  2.1 W/K still: a 30.6 K rise for 64.2 W. The model (`G_3253`) now carries it, and the fans-off rows of 9.1 and 9.2
  take their 32.53 figures. The same model run also fills 9.1's fans-off worst corner (163.9 K). No other figure on
  the page changed (the model's output differs only in these rows and two added records).

**Corrections made in the fifth cycle (26 September 2026, the checker's blocking item on 32.56), each in the
conservative direction or neutral:**
- **The record's key-down durations.** The fourth cycle called 32.53's "minutes" the design record's only key-down
  duration, in sections 7.1 and 7.2, PWR-F14 and the draft YAML, and closed that as exact. It was false: 32.56, line
  2940, gives a 20 s key-down at 45 W that warms the plate's local patch about 15 K. Both figures are now cited
  wherever the duration is. K1's 60 s tightens the first and is three times the second.
- **The plate and the PA's case.** Section 7.2 had said a 60 s key-down "costs the plate at most 6.7 K against the
  RA30H1317M1's +100 C case limit". The 6.7 K is W4's whole-plate average. The flange sits on the local patch, which
  the record's figure, taken linear, takes past the maker's 90 C in 53 s at 45 W and past the +100 C rating in 44 s
  at 68 W. The PA side of a key-down is now bounded by a flange reading (K2 at +75 C, C4 at +85 C), whose sensor no
  board carries (PWR-F15); until it exists, repeated key-downs are OPEN.
- **The fans-off row** kept the fans' own power (3.1 W at PLAN) in the heat, which a failed fan does not draw: up to
  1.5 K on 32.53's 2.1 W/K and 2.0 to 4.0 K on W4's bound, in the safe direction. The 9.2 note now gives both
  readings: C1 acts on the 50.6 C air with the fans' power counted, and need not act (49.0 C air, 52.9 C cells) without
  it.
- **`main` moved to `b69f20db` and then to `01469100`**, and every citation is re-anchored at `01469100` (section 12
  lists what moved). The merged
  board A carries its charge shunt R17 in the pack's discharge path (S-04), 5 mOhm more than the tables' 22.5. The
  all-transmit basis moves from 15.22 V to 15.31 V and the PA-alone basis from 11.86 V to 11.95 V, inside the
  unchanged floors of 15.5 V and 12.4 V (section 7.2). R17 joins PWR-F12's parts list. The battery stream's proposed
  golden image (`01469100`) uses both of the gauge's over-current-in-discharge levels, one of which PWR-F12's backstop
  needs: that is now an open item with that stream (section 9.3).
- **Wording.** 32.62 withdrew the BB-2590/U of 32.49 for a smaller pack of the same 14.4 V class, 4S Li-ion; section
  7.2 had said it replaced the pack "with a 4S one". The 7 to 8 minutes is this page's literal reading of 32.53, not
  the record's words. At `main`'s +5V_DEV the HIGH current, 7.8 A, is inside the LM5176 stage's 7.2 to 9.5 A band,
  not under it.
- No threshold was loosened. Two were added: the flange gate and the flange cut. The model's output differs from the
  fourth cycle's only in three added records (`d11.pa_case_record_3256`, `d11.main_pack_path_R17`, the fans-off
  row's fan power) and in the two heater labels, which now read `1f614233` and `main` instead of `main` and
  `fnd/r4a`.

**The experiment this page recommends before more layout.** An **empty-case heat-balance test**:
- **Set-up:** a current-moulding Peli 1450 with a 3 mm aluminium face plate blank and the 1450PF frame, 20, 40 and 60 W
  of resistive heat spread on a dummy stack, the fans running (and not), and thermocouples on air, plate, walls and a
  dummy pack block.
- **Measures:** the conductance for lid open and closed, fans on and off.
- **Also, on the same plate blank:** a 45 to 83 W resistive block bolted with thermal compound where the PA's flange
  sits, run for 20, 30 and 60 s from a warm plate, with thermocouples under it and at 50 and 100 mm. That measures the
  patch rise and its cooling, which PWR-F15's thresholds and the repeat rate need, before any PA is fitted.
- **Closes:** W4 T9 and the 2.3 x spread that decides the hot end, and 32.56's patch figure, weeks before a populated
  build.

Appendix 32.367 (line 18893) already plans a targeted unpowered mock-up at the build stage in a new case of the
current moulding (D-08 reversed, D-08a), so this only buys that case earlier. The purchase is money,
which D-09 and the house rules keep with the owner: prepared here, not decided.

**Bench readings owed at bring-up** (each replaces a T or R row, or checks a control):
- the monitor at three brightness settings;
- each WiFi card with its link up and idle, passing traffic, and with W_DISABLE1# asserted;
- the LimeSDR receiving;
- the NVMe drive idle through the PCIe switch, with ASPM L1.2 and APST on and off;
- the PA drain at 13.8 V (F-PR-02);
- the PA's flange temperature, from the flange sensor and a thermocouple beside it, through 60 s key-downs at 13.8 V
  into a dummy load from a +50 C plate, and its cooling after one (K2's and C4's flange limits are re-derived from
  it, PWR-F15);
- the supervisors' supply current at their chosen clock;
- the pack's DC impedance at +20, 0 and -10 C (the floors of section 7.2 are re-derived from it);
- the time from a pack current step past 18 A to the PA unkeying under C4, against the gauge's 2 s OCD2 delay;
- the pack current and the four cell thermistors in PS-TYP with each outlet at its contract, lid open, at a stated
  ambient (C2's thresholds are re-derived from this).

**Prepared questions (text only; nothing has been sent):** `drafts/pwr-maker-questions.md`:
- to AsiaRF: idle and radio-disabled power, the W_DISABLE1# behaviour, which temperature range is current;
- to Xenarc: typical power at brightness steps;
- to Lime Microsystems: receive-only power at a stated sample rate.

## 11. Closed, open, and the handover

**Closed by this page (evidence in the sections named):**
- **The dominant undocumented loads:** sourced or bounded (section 2). The T share of PS-TYP is 19 %, down from 49 %.
- **Conversion losses:** read per rail from the converters' datasheets at the state's current. The rails with no plot
  near their point are named (section 3).
- **Idle figures:** 29.4 W against about 32 W is reconciled by scenario and boundary (section 5).
- **Battery energy after derating:** shown step by step, including the cell minimum, rate, sag, cut-off, temperature,
  reserve and 80 % against 60 % ageing (section 6).
- **D-11 and every PA key-down:** the floors, the key-down time and the key-down rules are set, PROVISIONAL
  (section 7.2):
  - the all-transmit floor's basis is corrected (the distribution drop counted once, F2 carried in it) and its
    0.28 V margin is stated (0.19 V on `main`, whose pack path carries R17), with the heater held off during the
    key-down so the margin stands;
  - the PA keyed alone has a floor of its own, 12.4 V, and the same 60 s bound;
  - the 60 s is placed between the design record's two key-down figures, 32.53's "minutes" and 32.56's 20 s, and
    the PA's case is compared with its maker's 90 C and +100 C on 32.56's patch figure. The PA side is bounded by a
    flange gate and cut (K2, C4) whose sensor is open (PWR-F15);
  - the cold and aged pack are stated as not shown, and the in-key guard C4 enforces the 18 A where the floors
    mispredict;
  - the key-down's dependence on the chain's current rating and on F2 is recorded (PWR-F12);
  - the peak-current basis is stated per state, down to the gauge's 10.0 V under-voltage trip (section 7.3).
- **Allowed simultaneous modes, at desk level:** the combinations of section 7.1 are judged against the declared
  continuous and peak pack current and the cells' windows. They are the eight power states, each outlet and both,
  PS-BUSY with both outlets, charging on shore, the vehicle input, the heater overlay over PS-TYP and PS-RED, the PA
  keyed alone over PS-IDLE-SPEC and PS-TYP at 75 W and 113 W, and the all-transmit case. Every row that passes a limit
  names the rule or control that bounds it. A combination not tabulated is bounded by the same controls, since they act
  on measured current and temperature and on every key-down, but it is not judged row by row. The controls C2 to C4
  and the rules K1 to K5 are PROVISIONAL firmware contract items, verified at bring-up.
- **Thermal, at desk level:** each estimate is applied only to its load and enclosure state. The cells'
  temperatures, with their own I2R, are compared with their charge and discharge windows for every state of
  section 4 and every row of section 7.1. The parts in `pcb_part_temps.yaml` and those this stream adds are compared
  as inside-air ceilings, since no module's own rise is known; the chemical fuse F2 is compared at the cells'
  temperature with its own rise TBD (section 9.2), and the PA's case on the plate's local patch during a key-down
  (section 7.2). Both restrictions are recorded as proposed controls, with
  measured-current and measured-temperature controls taken (section 9.3). Nothing here is a measurement.

**Open, each with its bound and owner:**

| Item | Bound today | Owner |
|---|---|---|
| monitor typical power | 0 to 10 W | session: bench at bring-up, or the prepared question |
| WiFi card idle and standby power, W_DISABLE1# effect | 0 to 9.1 W per card | session: bench; prepared question |
| LimeSDR receive power | up to 4.5 W | session: bench |
| NVMe pick and its idle through the switch | 0.9 to 1.05 W idle each (lower only if L1.2 or APST work) | session (parts) |
| PA drain at 13.8 V | 75 to 113 W | session: bench (F-PR-02) |
| enclosure conductance | 1.22 to 2.85 W/K lid open with fans (W4) against 3.0 to 3.3 (32.53); fans off 0.77 to 1.57 (W4) against 2.1 (32.53) | owner (money for an early case) or TEST-PLAN E3 on the build |
| "aged" for REQ-014 | 60 % to 80 % of the minimum capacity | session (requirements); the owner if it becomes a product claim |
| RSOC of the two floors | the 15.5 V and 12.4 V rest voltages are known; the RSOC is TBD | session: the pack's learning cycle |
| the floors in the cold and on an aged pack | covered up to a cell DC resistance of 0.072 Ohm (all-transmit) and 0.082 Ohm (PA alone), or 0.068 and 0.079 Ohm on `main` with R17; the cold and aged resistance is TBD | session: the pack's DC impedance at +20, 0 and -10 C at bring-up; C4 enforces meanwhile |
| cold capacity between -10 C and 23 C | factor 0.41 to 1.00 | session: bench at 0 C and -10 C, or the maker's cold-rate curve |
| board E always-on drain (PS-OFF) | 0.2 to 1.7 W | session: firmware sleep state |
| fan picks (D-18) | 0.36 to 0.56 W per 30 mm fan; 0.39 to 1.50 W per 60 mm IP68 fan | session (parts); the owner only if D-18 comes to him |
| duty cycles (5G, LoRa, beacons, SDR, HF), PS-BUSY | PS-BUSY between PS-TYP (63.0 W) and its sustained bound (92.0 W PLAN, 134.4 W HIGH) | session (requirements) |
| the PA's key-down repeat rate | at most 60 s per key-down, at least 2 s apart, gated at +55 C cells, +50 C air and +75 C on the PA's flange (the last needs PWR-F15); a fixed rate beyond the gates TBD | session: TEST-PLAN E3 (plate and cells) |
| the PA's case during a key-down (PWR-F15) | on 32.56's patch figure, linear, a 60 s key-down from a +50 C plate ends at 95 to 118 C before the flange interface (45 to 68 W), against the maker's 90 C and +100 C. Bounded by K2 at +75 C and C4 at +85 C on a flange sensor no board carries; without it one key-down is bounded at about 30 s and repeated key-downs are OPEN | board D's owner (the sensor); W5 (the thresholds); bring-up or TEST-PLAN E3 (the flange against a thermocouple, the patch's cooling), or the plate test of section 10 |
| the pack chain's current contract (PWR-F12) | 10 A continuous declared, 18 A peak with no duration. Asked of it: 15.3 A (PS-TYP with both outlets) and 18.4 A (PS-BUSY with both) at the end of discharge if nothing sheds them, and 18 A for 60 s by every PA key-down | battery-protection stream (the two YAML files, the gauge's OCD1 and golden image, the protection test); board A's owner (the pack-node copper at 18 A); the owner only for a 2 oz price |
| the gauge's two over-current-in-discharge levels | this page asks for 11 A for 90 s and the declared 20 A for 2 s; the battery stream's proposed image asks for 20 A for 2 s and 24 A for 1 s (TBD by its reviewer); two levels exist | battery stream (the golden image); the integrator if the two streams disagree |
| F2 at 18 A for 60 s | 0.32 to 0.81 W of its own at the block's temperature; -20 to +60 C with no derating published; margin unknown | battery-protection stream: the extended protection test, or Eaton's answer on behaviour above +60 C |
| C1 to C4 and K1 to K5 in firmware | thresholds PROVISIONAL: 9.0 A over 10 s, cells +50 C (outlets) and +55 C (modules and key-on), inside air +50 C, 18 A and 2.70 V in-key, the PA's flange +75 C at key-on and +85 C in-key | session: W5 contract (panel and bridge); re-derived at bring-up from the readings of section 10 |
| how long PS-BUSY runs before C1 sheds it at +20 C | TBD: depends on the pack's and the air's heat capacities | session: TEST-PLAN E3, or the empty-case test of section 10 |

**For the integrator.** Proposed; this stream writes only this page and `drafts/`:
1. **`CONOPS.md`:**
   - section 4a table and line 241: replace the battery W and hours with section 4 and section 6, add the S/R/D/T
     split, and add the three architecture rules of section 1;
   - section 5, S1 row: 29.4 W becomes 39.7 W, and the 32 W reconciliation of section 5 goes in;
   - section 6: 3.4 h and 1.8 h aged become 2.5 h and 1.7 h;
   - line 345, the APRS row: the worst duty becomes key-downs of at most 60 s each under section 7.2's rules. This
     is a change to the record, not a citation fix: the row's citation of 32.53 line 2860 is right, and that line
     says the 200 W PA key-down "lasts minutes". The record has a second figure the row does not cite: 32.56, line
     2940, "a 20 s key-down at 45 W warms the local patch about 15 K", the patch under the PA's flange. The row
     should keep the 32.53 citation, add 32.56's, and say that the session set 60 s between them, PROVISIONAL: a
     tightening of "minutes" for the chain's 10 A and 18 A declarations, F2 and the cells' window, and three times
     the 20 s, which is why every key-down is also gated and cut on the PA's flange temperature (section 7.2,
     PWR-F14, PWR-F15). The PA's own key-down heat is 32.52 item 6, line 2852;
   - lines 280 and 281, the cold overlay: the heater is regulated to 12 V on `main` (7.5 W plus the buck's loss,
     about 8.5 W), not the unregulated 10.8 W.
2. **`ARCHITECTURE.md` (`fnd/i3`):**
   - section 8.1: heat per state from section 4;
   - section 8.4: add AW7915-AED, LimeSDR and the AP2112K supervisor LDOs;
   - section 11: runtime and power rows.
3. **`OPERATING-ENVELOPE.md` section 3:**
   - mark the +35 C and +25 C rows as proposed controls;
   - add "in the reduced mode, lid closed, charging holds off above about +15 to +33 C" (INFERRED; +25 to +29 C on
     32.53's own conductance);
   - cite this page.

   The document is pinned by `pcb_envelope.yaml`'s `document_sha256`, so an edit re-pins it.
4. **`pcb_part_temps.yaml`:**
   - add rows for the AW7915-AED, the LimeSDR Mini v2.4, the cells (from `owed` to a row with clause 3.12) and the
     chemical fuse F2, and the RA30H1317M1 PA in the plate (fifth cycle). Drafts are in
     `drafts/pwr-part-temps-rows.yaml`;
   - the row at line 88, "the pack's protection board" matched on PCB-LIS1A15, describes the retired 1S module of
     appendix 32.31, not board P. The battery stream owns what replaces it.
5. **`pcb_requirements.yaml` (`fnd/i1`) REQ-018:**
   - the two floors and the key-down rules of section 7.2, as the session's PROVISIONAL thresholds, with the bring-up
     re-derivation as acceptance;
   - D-11's "outlets at their minimum contract" stated as 0 W, the outlets off, which is what S-14 implements and
     what this page assumes.
6. **Filing:** the fetched documents of section 12 under `v2/vendor/` with their `SOURCES.yaml` rows, and the model
   beside this page (proposal: `v2/docs/feasibility/power_thermal_model.py`).
7. **Board B's owner** (on `main` since `fnd/r4b` merged): PWR-F01, F03, F04, F05 and F06. **Board A's owner:**
   PWR-F02, and PWR-F12's copper judgement at 18 A, with R17 on the path (1.62 W at 18 A against a 3 W part whose
   maker's sheet is not held). **Board D's owner:** PWR-F15, the PA's flange sensor.
8. **`pcb_pack_protection.yaml` and `pcb_energy_chain.yaml` (battery-protection stream):** PWR-F12, drafted in
   `drafts/pwr-chain-redeclaration.yaml`. It carries the continuous rating, the 18 A for 60 s service rating, F2 as a
   stage, the OCD1 backstop with its recovery, the constraint on Safety Overcurrent in Discharge and the extended
   protection test.
9. **The W5 firmware contract:** C1 to C4 of section 9.3 with their thresholds and restore rules, and K1 to K5 of
   section 7.2, including the PA's flange gate (K2, +75 C) and cut (C4, +85 C).
10. **`pcb_requirements.yaml` (`fnd/i1`) REQ-017:** add "on battery, inside the outlet budget" (PWR-F13).
    **`CONOPS.md` section 4a, PS-BUSY row:** the sustained bound of section 4, marked "bounded mode" (section 7.1).
11. **`main` is at `01469100`**, and every citation on this page is anchored there (fifth cycle). `458b2873`
    merged the round-4 and round-6 corrections of boards A, B and D: board A carries the regulated heater (U33 at
    `gen_sch_a.py` line 1065, U22 at 1064), the outlet interlock (U30, line 1104), the VSYS topology with R17 in the
    pack's discharge path (S-04), and HEAT_EN at line 1119; board D regulates the PA's gate bias. `b69f20db` changed
    `CONOPS.md` (the APRS row is now line 345, the heater's lines 280 and 281, D-11 line 419; content unchanged in the
    rows this page cites), `OPERATING-ENVELOPE.md` (sections 4 and 8; lines 55 and 91 unchanged) and
    `pcb_envelope.yaml`'s `document_sha256`, and appended 32.367 to the appendix; it changed no generator. On `main`
    the heater-on basis is 15.79 V (the regulated mat plus R17) and K4 still decides it. `gen_sch_e.py`,
    `gen_sch_p.py`, the two pack YAML files, `pcb_fuse_derating.yaml`, `pcb_part_temps.yaml`, `dc_drop.py`,
    `ARCH-PCB-B-IOHA.md` and `open-picks.txt` are unchanged from `1f614233` to `b69f20db`, and every appendix line
    this page cites keeps its number: the appendix only gained 32.367, at its end (from line 18871). From `b69f20db`
    to `01469100` (eight commits, 18:05 to 18:25) the only file this page cites by line that changed is
    `gen_sch_p.py` (`d90f30e4`: board P's second level gets its own thermistor, and F2's temperature reading is
    redone), whose lines are re-pointed; the battery stream's review packet arrived in the same commits.

## 12. Sources

**Fetched by this stream on 26 September 2026** (`drafts/datasheets/`):

| File | URL | Revision | sha256 |
|---|---|---|---|
| `asiarf-AW7915-AED_V1.pdf` | https://asiarf.com/wp-content/uploads/2023/09/AW7915-AED_V1.pdf | Version 1.0, release date 2023-08-17 | af1a93ef3b484a3da4354779f0b2a8a2537c94d71025eb68b82a4d4879f8e8db |
| `asiarf-aw7915-aed-product-page.html` | https://asiarf.com/product/wifi-6-11ax-m-2-ae-key-module-aw7915-aed/ | page as served 26 Sep 2026 (links a datasheet dated 2026-05-20) | b153fe713673d0f6df7936038333096e8fc14842609d90e8d8b1e7694c120846 |
| `limesdr-mini-v2-introduction.html` | https://myriadrf.org/projects/limesdr-mini-2-0 | LimeSDR Mini v2 documentation v2.4, last updated 8 Jun 2026 | f1146105a3c09ebcf786d217fbf0053f8e6df3c5192efcf666e731281be4c4f1 |
| `limesdr-mini-v2-user-setup.html` | https://myriadrf.org/projects/limesdr-mini-2-0/user/setup.html | same | 87b2e5605196b5c5f48e9175991c63143152dbb694d6f4faeba85d6cdaeca3b3 |
| `advantech-sqflash-720-d-m2-2242-v1.9.pdf` | https://advdownload.advantech.com/productfile/Downloadfile2/1-2MDTFS2/Advantech%20SQFlash_PCIe%20NVMe%20M.2%202242_M%20Key_720-D-DS_v1.9_20240709.pdf | Rev 1.9, 9 Jul 2024 | 4176a46e8474f74102cf139b4fd61dea45f2f46c7062d1ddb786732c2107b7ba |
| `cervoz-m2-2242-nvme-titan.pdf` | https://www.cervoz.com/products/download/8r0k7y0bWdEw/Cervoz_Industrial_Embedded_Module_M.pdf | T405 datasheet Rev 2.0 (file created 28 Jul 2025) | 30b3c59cd3332952f91eb825cd6bb9ebcbea3281fca4bd6a3277ddd03ce032b9 |
| `sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf` | https://www.sunon.com/en/MANAGE/Docs/PRODUCT/286/360/Sunon%20DC%20Brushless%20Fan%20&%20Blower_(240-A).pdf | catalogue 240-A (file created 7 Dec 2018); PDF pages 18 and 40 extracted by this stream (printed pages 16 and 38) | extract fae7e21365939be5c3bbf156be3522b364037a637590f5079538d63456bca63b; full original bd47c70496d8ee47585ece647c9f7202966f52439d1b48265bf9b4f3031cec80 (8.4 MB, not kept) |
| `xenarc-709gnk-product-page.html` | https://www.xenarc.com/709GNK.html | page as served 26 Sep 2026 | dc32f6556d6ddc398064e3a15eec0c600937b2235138cbd10e0ed344d708bf93 |
| `ti-bq4050-trm-sluuaq3a.pdf` (second cycle) | https://www.ti.com/lit/ug/sluuaq3/sluuaq3.pdf | BQ4050 Technical Reference Manual SLUUAQ3A, April 2016, revised October 2022; sections 2.5, 14.9.6 to 14.9.8, and in the third cycle 3.5, 5.2, 14.2.5.1 and 14.10.4 | 525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad |
| `keystone-m65-p42-mini-fuse-holders.pdf` (third cycle) | https://www.keyelco.com/userAssets/file/M65p42.pdf | Keystone catalogue M65, page 42 (PDF created 26 Jun 2015); the 3568 mini blade holder | caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395 |

**In the tree, read for this page** (the first 16 hex digits of each sha256):

| Document | Clause used | sha256 |
|---|---|---|
| `battery/samsung-35e-orbtronic.pdf` (INR18650-35E Ver. 1.1) | 3.1, 3.3, 3.5, 3.8, 3.9, 3.10, 3.12, 7.2, 7.4 to 7.9 | 5ec577b952b9dc51 |
| `cm5/cm5-datasheet.pdf` (Release 3, build 08/06/2026) | 3.3; 4.3.3 Table 9; 4.4 | 80070fefd8db6e8a |
| `battery/ti-csd17570q5b.pdf` (SLPS471D, revised May 2017; third cycle) | Absolute Maximum Ratings, 5.1, 5.2 | 596555c33dce1fca |
| `battery/ti-bq4050.pdf` (SLUSC67B, revised October 2017) | 6.14 (coulomb counter), 6.16 (ADC), 7.3.1 (points to SLUUAQ3 for every protection), 8.2.1 (calibration) | 2664e33fe6d6ebed |
| `diodes/diodes-ap64500.pdf` (DS41979 Rev 5) | Fig. 4, 5 | d3bcdc7dd4ca44cb |
| `diodes/diodes-ap63200-series-buck.pdf` (DS41326 Rev 3) | Fig. 4, 5 | ef99daa3789d835b |
| `diodes/diodes-ap2112-ldo.pdf` (DS39724 Rev 2-2) | absolute maximum ratings, recommended operating conditions | ef8d376f2ec356e2 |
| `diodes/diodes-pi7c9x2g404sl.pdf` (DS40068 Rev 5-2) | Tables 12-7, 12-8, 13-1 | 675fa7ee40c91ad6 |
| `ti/lm5176-datasheet.pdf` (SNVSAI1D) | Fig. 6-1, 6-2 | 98191bec36d43771 |
| `ti/ti-tps62933.pdf` (SLUSEA4D) | Fig. 10-2 | 16ec2eac43c7374e |
| `ti/bq25731-datasheet.pdf` (SLUSE66A) | Fig. 8-4 | 3e5e927fdf63cf6a |
| `ti/ti-tusb8041.pdf` (SLLSEE4E) | 7.7 | b715bce72e988310 |
| `microchip/microchip-ksz9897-datasheet.pdf` (DS00002330D) | Table 6-1, Notes 6-1 to 6-4 | 72b89179ed6a42a7 |
| `st/st-stm32h743xi-datasheet.pdf` (DS12110 Rev 10) | Table 30 | 9b27d1d993a8bc5b |
| `quectel/quectel-rm520n-series-hardware-design-v1.1.pdf` | Tables 42, 43 | 2bae882148b45172 |
| `zigbee/ebyte-e72-2g4m20s1e-user-manual.pdf` | 2.1, 2.2 | 4bae5b3e67483b0b |
| `mitsubishi/ra30h1317m1-datasheet.pdf` (Publication Date Oct. 2011) | maximum ratings (Tcase(OP) -30 to +100 C), electrical characteristics; fifth cycle: Thermal Design of the Heat Sink ("best to keep the module case temperature (Tcase) below 90°C"; Rth(ch-case) 2.9 and 0.7 °C/W) and Mounting (thermal compound recommended; M3 at 4.0 to 6.0 kgf-cm) | 9fda757ab1acfb6b |
| `xenarc/xenarc-709gnk-product-manual-v2.pdf` | specifications | ba3b1474406fdaf5 |
| `rockblock/rb9704-datasheet-RB9704-001-JUN26.pdf` | electrical power | d48acbea28ee2a7d |
| `lora/ebyte-e22-900m30s-user-manual-en-v1.20.pdf` | 2.2 | d864e9ca390f15c9 |
| `nicerf/nicerf-sa868-datasheet-v1.3.pdf` | current consumption | 938ef5ef5007df6b |
| `qrp-labs/qmx-operating-manual-1_04_004.pdf` | receive current. The transmit 0.7 to 1.1 A is appendix 32.51 line 2816 and was not re-read in a held document. | 7d2616cdcadd2f7c |
| `quectel/lg290p03-hardware-design-v1.1.pdf` | power consumption | 422ca9a2aa5495c1 |
| `sensirion/sgp41-datasheet.pdf` (version 1.0, December 2021) | Tables 4, 5 | 331f35ed1f027a74 |

**Design sources:**
- the generators, registries and documents at `01469100`, lines as cited (fifth cycle). The earlier cycles read them
  at `1f614233`; their entries below keep the lines they read, and the fifth-cycle entry maps the ones that moved;
- second cycle, at `1f614233`:
  - `pcb_pack_protection.yaml` lines 28, 29, 101, 110, 114, 145 and 154;
  - `pcb_energy_chain.yaml` lines 48 to 153 (the continuous and peak declarations and the part ratings);
  - `pcb_fuse_derating.yaml` line 46 (the ATOF 25 A row, extracted from `battery/littelfuse-287-atof.pdf` and tested
    against it);
  - `dc_drop.py` lines 258 to 264;
  - `gen_sch_a.py` lines 483 to 488, 542 and 547;
  - `gen_sch_p.py` lines 207 to 219;
  - `MESHSAT-709-geometry-appendix.md` 32.244 to 32.246 (lines 12813 to 12924);
- third cycle, at `1f614233`:
  - `gen_sch_p.py` lines 62 to 74 (the FUSED and SCP_OUT nodes), 207 (R10) and 245 to 279 (F2, quoting Eaton ELX1135);
  - `gen_sch_a.py` lines 528 (the heater eFuse U22) and 542 (HEAT_EN on U27 pin 6);
  - `pcb_pack_protection.yaml` lines 101 and 110 (the CUV and OCD2 delays);
  - `pcb_energy_chain.yaml` lines 58, 111 and 143 (the Keystone 3568 holders);
  - `pcb_part_temps.yaml` lines 22, 43, 83 and 88;
  - `CONOPS.md` lines 266, 331 and 402;
  - `MESHSAT-709-geometry-appendix.md` 32.31 (line 2456), 32.32 (line 2466, the pad rule), 32.52 item 6 (line 2852)
    and 32.53 (line 2860);
- fourth cycle, at `1f614233` and unchanged at `458b2873`:
  - `MESHSAT-709-geometry-appendix.md` 32.53, line 2860, re-read in full: "total about 2.1 W/K still, about 3.0 to
    3.3 W/K with fans" and "The 200 W peak (PA key-down) lasts minutes and goes into about 8 to 10 kJ/K of thermal
    mass, about +10 K transient"; 32.62 (line 3054, the pack ruling of 7 Sep 2026 13:10);
  - `pcb_pack_protection.yaml` lines 28, 29 and 154;
  - `fnd/r4p` `drafts/r4-decisions.md` O-8, O-10 and O-13, and its `drafts/datasheets/eaton-scf9550-elx1135.pdf`
    (sha256 3ecc2424acfa1753);
- fifth cycle, at `01469100`:
  - `MESHSAT-709-geometry-appendix.md` 32.56, line 2940 (7 Sep 2026 01:17): "the plate is the heatsink (3 mm, 0.7 kg,
    660 J/K: a 20 s key-down at 45 W warms the local patch about 15 K; the average at APRS duty is a few watts)";
    32.49 item 12, line 2771 (the BB-2590/U, "10 A continuous and 18 A pulse per section"); 32.62, line 3054 and
    the research gate after it ("a rechargeable pack of the 14.4 V class (4S Li-ion, about 100 to 150 Wh)"); 32.367,
    lines 18875 to 18996 (the D-08 reversal, D-08a, the case margins);
  - `gen_sch_a.py` lines 26 to 48 (S-04: CELL_FUSED, VBAT as VSYS), 106 to 118, 124, 873, 881 and 110 to 115 (the
    LM5176 stages), 903 to 914 (F-PR-01), 977 to 982 (PD_VPWR), 1064 and 1065 (U22, U33), 1095, 1103 and 1104 (S-14),
    1119 and 1124 (U27, U28), 716 to 722 (R17);
  - `gen_sch_b.py` lines 46, 58, 82, 83, 87, 90, 95 to 108, 150 to 167 (the card rails; `fnd/r4b` merged), 178, 204,
    208, 222, 233, 346 to 351, 833 and 1050;
  - `gen_sch_d.py` lines 15 (the PCA9555 on the kit I2C bus) and 624 to 645 (the regulated VGG);
  - `CONOPS.md` lines 241, 246 to 256, 280, 281, 345 and 419;
  - `gen_sch_p.py` lines 64 to 76 (FUSED, SCP_OUT), 209 (R10), 210 to 221 (the cell thermistors), 247 to 289 (F2;
    255 and 256 quote ELX1135, 272 to 276 the no-derating line and "judged low, not proven"), 243 (RT1), 317
    (F-BP-01) and 418 (J_TS2); `gen_sch_e.py` lines 543 to 545 (the BME688);
  - `v2/docs/review-packets/battery/PRIMARY-CONFIGURATION.md` lines 79, 120 to 122 and 137, and
    `PROTECTION-ARCHITECTURE.md` line 170 (the battery stream's proposed golden image and its permanent-fail map);
    `pcb_pack_protection.yaml` lines 107 to 110 (the declared 20 A for 2 s);
  - the lines the earlier cycles read at `1f614233` that moved: `gen_sch_a.py` 483 to 488 are 977 to 982, 528 is
    1064, 542 is 1119, 547 is 1124; `gen_sch_b.py` 141 is 154 and 158, 144 is 161, 154 is 178, 180 is 204, 184 is
    208, 209 is 233, 318 to 321 are 346 to 351, 754 is 1050; `CONOPS.md` 232 is 241, 238 and 239 are 247 and 248,
    244 is 253, 266 is 280, 331 is 345, 402 is 419; `gen_sch_p.py` (moved at `d90f30e4`) 62 to 74 are 64 to 76, 207
    is 209, 208 to 219 are 210 to 221, 245 to 279 are 247 to 289, 253 and 254 are 255 and 256, 265 to 270 are 272 to
    276 (reworded), 307 is 317. The other files and lines are unchanged (section 11, item 11);
- `fnd/r4a` `drafts/r4-decisions.md` (S-14, S-20, F-PR-01, F-PR-04, F-PR-06) and `r4-open-items.md` (O-04, O-15);
  the generator itself is `main`'s since `458b2873`;
- `fnd/w2` `drafts/w2-power.md` and `w2-runtime.md`;
- `fnd/w4` `drafts/w4-mech-thermal-rf.md` section 4;
- `fnd/i3` `ARCHITECTURE.md` sections 8 and 11;
- `fnd/i1` `pcb_requirements.yaml` (REQ-014, REQ-018, CON-019, SC-05).
