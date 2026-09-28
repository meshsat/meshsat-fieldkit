acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). Its blocking items B1 and B2 and its minor items are answered in ENERGY-RECONCILIATION.md section 9 (second issue) and the owner sheets. -->

# AI review: fnd/energy2 at 3af58534, section 9 of the energy record (OD-02), MESHSAT-1357

AI review, 29 September 2026, 01:27 to about 01:50 CEST. An independent Claude check by a session that wrote none of this work. It is not a qualified review. Prototype design: nothing has been built, ordered or measured. Everything below is read against the tree at 3af58534 and the maker's documents held under `v2/vendor/`.

Scratch clone: `a scratch clone` (a `git clone --shared` of the main checkout, with `fnd/energy2` fetched from the `energy2` worktree and 3af58534 checked out detached). My own code and its output are beside this file: `recompute.py` and `recompute.out`. No commit was made, nothing was pushed, and no branch was touched.

## Verdict in one paragraph

The derivation reproduces to the last digit, and most of section 9 is sound. M1 is judged as the mission defines it (both start hours, aged to 80 percent, +20 C, the 3.00 V line). External DC and reduced service are not used as the basis, the reduced-service alternative is kept separate with its FAIL, and the 17 C and 100 W statements are scoped in the record. Two items block acceptance. (B1) The constraint list and both owner sheets say REQ-016 must change because M1 "needs at least 200 W" and "about 50 V". The record's own frontier and my recomputation contradict this: inside REQ-016 as written, the model meets M1 with packs the lid estimate says the case can hold, given a large enough array. The 50 V figure is a choice of array wiring, not something M1 needs. (B2) Both 9i and the options sheet claim a transport route for the pack, which REQ-069 forbids.

## Blocking items

**B1. REQ-016 is presented as a hard conflict with M1. On the record's own model it is a trade against array size.**
- The wrong text. In 9i: "Inside it no pack the case can hold carries 42.8 W (9d: 4S18P allows at most 41.4 W); M1 needs at least 200 W and about 50 V." `DECISION-OPTIONS.md` says the mission "needs ... at least 200 W of solar input where today's limit is 100 W" and "REQ-016, solar input from 100 W and 25 V to 200 W and about 50 V". `DECISION-PARAGRAPH.md` says the mission "needs ... at least 200 W of solar input (today 100 W)".
- Why "at most 41.4 W" is wrong. The figure 41.4 W is 9d's value at 1000 Wp, the largest array that section 6 of `energy_architecture.out` tries. It is not a maximum over arrays. In the same file, section 4 (the frontier) shows 42.8 W met inside the 100 W window by 4S19P with 1300 Wp. The record's 9c says the same. 9f's estimate gives the lid about 52 cells (4S13P), and 4S13P plus the base's 4S6P is exactly 4S19P. The recommended architecture already takes the whole lid, so this is the same assumption.
- My recomputation, calling `energy_budget.simulate()` with both start hours, aged to 80 percent, the 3.00 V line, and REQ-016's 100 W window:

  | pack | array | result at +20 C | lowest point | at +15 C |
  |---|---|---|---|---|
  | 4S19P | 1300 Wp | MEETS | 1.3 Wh | NOT MET |
  | 4S19P | 1500 Wp | MEETS | 34.5 Wh | NOT MET |
  | 4S18P | 1600 Wp | MEETS | 14.7 Wh | NOT MET |
  | 4S17P | 2000 Wp | MEETS | 31.4 Wh | NOT MET |
  | 4S16P | 3000 Wp | MEETS | 1.4 Wh | NOT MET |

  The largest load 4S18P carries rises with the array: 41.35 W at 1000 Wp, 42.20 W at 1300 Wp and 42.77 W at 1500 Wp.
- Why REQ-016 as written still holds. REQ-016's statement (`pcb_requirements.yaml`, REQ-016) caps each panel at 25 V open circuit and the stage input at 100 W. It sets no limit on array size. 12 V class panels wired in parallel meet it. The fault current of such an array needs F2 and J_SOLAR re-rated, and the record already treats that re-rating as compatible with REQ-016 as written (route B, section 6e).
- What the owner should be shown instead. Inside REQ-016 the model needs about 13 to 30 panels of 100 W in parallel (fault current about 81 A or more, at 6.25 A per 100 Wp as the record states) and the whole lid, with no margin at +15 C. A 200 W window does the job with 400 Wp and margin. That is a real trade for him to decide. It is not a necessity.
- The 50 V is a choice, not a need. It follows from wiring the 400 Wp as two series pairs (9g), which keeps the short-circuit current at 12.5 A. Four panels in parallel would stay inside the 25 V limit at about 25 A.
- Fix: restate 9i's REQ-016 item and the two sheets on these lines. Name the largest array the kit can plausibly carry as the constraint that actually binds (the "kit's claimed form" item). Present the voltage as a design option.

**B2. A transport route is claimed for the pack, contrary to REQ-069.**
- The wrong text. 9i says "a pack that travels by road or sea as dangerous goods rather than by air". `DECISION-OPTIONS.md` option A says "(it travels by road or sea, not by air)".
- The rule it breaks. REQ-069 (`pcb_requirements.yaml`) states: "an unknown UN 38.3 status permits no route by itself". Its acceptance reads: "No document claims a transport route for the kit with its pack, or for the pack alone, until CONOPS and the operating instructions state for that route the pack's classification and the conditions or exception it travels under". SC-06 was withdrawn on 26 September 2026 for exactly this reading ("road carriage has its own dangerous-goods rules (the ADR)").
- "Not by air" is also unsourced. The record cites no air-transport regulation. 9h itself only says "above the 160 Wh passenger limit; UN 38.3 status unknown".
- Fix: replace both with something like "about 870 Wh nominal: well above the 160 Wh passenger limit; its transport route is not claimed until its classification is established (REQ-069, UN 38.3 status unknown)".

## Minor items

- **m1. The Peli 1450 sentence in 9i says more than the model can.** It reads "is not in conflict on this model: the architecture fits the fixed case if the lid findings of 9h close". The energy model contains no geometry, and the lid fit rests on an ESTIMATE of footprint arithmetic. Say "not shown to conflict; the fit is an ESTIMATE pending 9h".
- **m2. Two owner-approved functions lose their lid space, and the rulings that approved them are not named.**
  - The functions: the QMX-class HF module inside (16a) and the lid tablet bracket (16d). Both were approved in the owner's walk-through of 6 Sep 2026 23:25 to 23:37 (appendix `MESHSAT-709-geometry-appendix.md` line 2802, 32.50).
  - D-01 keeps every ruled function "designed and fitted where copper exists".
  - 9i and the sheets frame this only as D-01's deferral. They should name 16a and 16d and say where the HF module goes.
  - The 36-cell variant that keeps the QMX tray is 4S15P in total. It meets only at +20 C with 3.6 Wh left (9e).
- **m3. The +20 C basis is argued from the kit's own heat, which a pack in the open lid does not get.**
  - `energy_inputs.yaml` (mission.cell_temp_note) rests +20 C on "the kit's own heat inside" against a September mean air of 14 to 15 C. M1's setting is lid open (CONOPS M1).
  - My bisection puts the recommended 4S18P (400 Wp, 200 W window) at about +12.9 C as the lowest cell temperature at which it still meets M1.
  - 9h lists the lid in the sun and a cold-charge heater, but not this.
  - The sensitivity in out section 5 is run at a 300 W window, not the recommended 200 W.
  - 9h should also list the lid's mass as a tipping load with the lid open.
- **m4. The series-pair panel figures in 9g are derived, not taken from a panel datasheet.** The figures are about 35 V at maximum power, about 50 V open circuit when cold and about 12.5 A short circuit. They come from REQ-016's 25 V per panel and the record's 6.25 A per 100 Wp, not from a held panel sheet. Label them as derived or ESTIMATE, as 9f and 9h do for their own figures.
- **m5. The lid cell count is not quite what the stated arithmetic gives.**
  - At 18.55 mm pitch and 66.25 mm rows on 346.16 x 231.86 mm, the footprint gives 54 cells with rows across the short side, or 60 with rows along the long side.
  - "About 52 (4S13P)" is 54 rounded down to a multiple of four, in the less favourable orientation. The R 16.26 ceiling fillets (CASE-MARGINS.md) are not applied.
  - 66.25 mm is the cell's 65.25 mm maximum length plus 1 mm. Say so, and name the orientation.
  - Wording: the QMX tray hangs from the lid rather than standing on the face. ASSEMBLY step 11's rows also include the LED D1 and the QMX knob tips.
- **m6. A qualifier is dropped in 9f.** It says "A06's fit gives a 21700 4S2P the same 144 Wh". The record's own line 456 says that 144 Wh is "with a representative 5 Ah cell, no 21700 sheet held".
- **m7. Some unscoped wording remains, including in the tool output that the record says it quotes byte for byte.**
  - `energy_budget.out` line 542 ("at every worst"), line 543 ("94.9 W into the stage in every worst case") and line 603 ("at or above 17.21 C").
  - The record at line 446 ("its worst 94.9 W"), the table row at line 505 ("(its worst high)") and line 573 ("set 2 needs 17.21 C or more").
  - Scope them, or add a note that the .out keeps the earlier wording and section 9j governs.
- **m8. `energy_architecture.py` does not pin `energy_budget.py` by sha256.** It checks the yaml and the pinned list, while `energy_4s6p.py` does pin `energy_budget.py` (cf6c377f...). A changed model would silently move every section 9 figure. The README's "imports energy_budget.py unchanged" is not enforced. It also refuses with exit 1, not the 2 or 3 the README describes for the other scripts.
- **m9. The owner sheets have two smaller gaps.**
  - Option C states only the "about 17 C" condition. The record's second condition (the night state within 0.86 W of its plan) is missing.
  - `DECISION-OPTIONS.md` is 293 words in all and 259 without the heading and metadata. That is within the brief's 300, but section 8d (line 802) still says "at most 250 words". Update 8d.
  - `DECISION-PARAGRAPH.md` is 105 words of body (131 with the heading and metadata, the same as its parent), which is within 120.
  - Neither sheet contains an em or en dash.
- **m10. "At least 546 Wh" depends on the sweep's upper bound.** In the sheet and in 9c it holds up to 5 kWp: 4S15P is needed at 1500, 2000 and 5000 Wp with no window. Only at 20 kWp does 4S14P meet (2.8 Wh). Add "for arrays up to 5 kWp", or fold this into B1's rewrite.
- **m11. Cosmetic items in the output.** Section 7's heading says "4S15P and 4S16P" but also prints 4S18P. The 11.28 h night figure is typed into the script, taken from the record's section 3. My own ephemeris gives 11.44 h sun-down on 15 September and 10.5 to 12.5 h across the month. This does not matter, because the storage floor comes from the hourly profile, not from 11.28 h.

## What I reproduced, and my figures

**The five scripts, run in the README's order from the clone's root with `env -C`, Python 3.11.2.** All exited 0. `git status` then showed every output byte-identical to the committed file. Run times:

| script | time |
|---|---|
| night_bounds | 0.05 s |
| packfit_west | 0.35 s |
| energy_budget | 0.11 s |
| energy_4s6p | 0.50 s |
| energy_architecture | 1.06 s |

**Independent recomputation (`recompute.py`).** It does not import `energy_architecture.py`. The September profile, the node power, the storage floor, the night figures and the search loops are my own code. `energy_budget.simulate()`, with the `Pack` it takes, is used only as the reference model. My profile matches `EB.profile` to 6e-14 W/m2.

**Demand.** 24 h is 1027.2 Wh and 72 h is 3081.6 Wh. The night at the record's 11.28 h is 482.8 Wh.

**Storage floor** (the same in the 100 W and 200 W windows):

| array | deficit (Wh/day) | harvest, 100 W window (Wh/day) | harvest, 200 W window (Wh/day) |
|---|---|---|---|
| 200 Wp | 606.7 | 640.8 | 640.8 |
| 400 Wp | 564.3 | 834.4 | 1281.6 |
| 800 Wp | 529.5 | 917.3 | 1668.7 |
| 20 kWp | 506.8 | 1023.9 | 2041.0 |

Each string holds 36.41 Wh usable at 15 to 18 strings.

**Smallest pack:**

| window | 400 Wp | 650 Wp |
|---|---|---|
| 100 W | 4S27P (983.0 Wh) | 4S23P (837.3 Wh) |
| 200 W | 4S16P (582.5 Wh) | 4S15P (546.1 Wh) |

**The recommended 4S18P, 200 W window:**

| array | lowest point at +20 C | lowest point at +15 C |
|---|---|---|
| 400 Wp | 91.0 Wh | 26.8 Wh |
| 650 Wp | 112.8 Wh | 48.6 Wh |

- 655.3 Wh usable, 868.2 Wh nominal, 3.6 kg of cells.
- At 400 Wp the peak stored charge is 117.3 W (123.5 W offered to the cells, a node peak of 166.3 W).
- It meets M1 down to about +12.9 C.

All of these match section 9 and `energy_architecture.out`. Also matched: 4S3P carries 9.11 W and 4S6P 18.07 W (400 Wp, 200 W window).

**Beyond the published sweep (the basis of B1).** The 100 W window runs are in the B1 table. With no window, 4S15P is needed up to 5 kWp and 4S14P meets at 20 kWp.

**TPS2596 equation 7 (the section 8 correction).**
- SLVSET8A, PDF page 28, prints RILM = 903 / (ILIM - 0.0112), with the worked example 903 / (1 - 0.0112) = 913.2 ohm.
- The table on page 6 gives 909 ohm as 0.949 / 1.005 / 1.051 A and 453 ohm as 1.83 / 2.004 / 2.147 A.
- So the corrected sign, the 1.00 A, the 454 ohm and the 2.004 A are right.
- The re-pin of `gen_sch_a.py` is justified. An AST dump of the three calls `energy_4s6p.py` parses (the VHEAT and VHEAT_IN rails, the U22 efuse) is identical between c4ad8350 and eb2e347e.

**Quotations checked against the tree.**
- D-06 matches `pcb_requirements.yaml` (one 4S3P, about 145 Wh, east pocket). So do D-01's deferred list (second pack, tablet bracket, HF), REQ-016's statement (25 V at coldest, 17.6 V, at most 100 W), REQ-072, REQ-014's "80 percent" and "+20 C", SC-21 and SC-37.
- The lid figures match `ASSEMBLY.md` step 11 (44.39 mm at the worst) and CASE-MARGINS (346.16 x 231.86 mm, and row M3 with its TBD lever heights).
- The "16 hours a day" of option C matches section 7c's table (set 2, September).
