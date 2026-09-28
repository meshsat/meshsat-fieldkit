acceptable: yes
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026); its remaining minor items r1 to r5 are answered in section 9 and the decision paragraph the same day. -->

# AI review, second check: fnd/energy2 at 820f17e6, answering CHECK.md on 3af58534 (MESHSAT-1357)

This is an AI review made on 29 September 2026, from 01:41 to about 01:50 CEST. It is not a qualified review. It checks only whether each item of CHECK.md is answered correctly. It does not repeat the full review. Prototype design: nothing has been built, ordered or measured.

The work was done in the same scratch clone (`_scratch/chk-energy9/repo`), fetched from the `energy2` worktree and checked out at 820f17e6. My additional code and its output are `recheck2.py` and `recheck2.out`, beside this file. No commit was made and no branch was touched. I briefly edited the clone's own `energy_budget.py` and `energy_inputs.yaml` to test the refusals, then restored both. `git status` is clean.

## Reproduction

- **The five scripts.** I ran them again in the README's order and all exited 0. Every output is byte-identical to the committed file (`git status` clean).
- **The filed `checks/recompute.py`.** It runs from its relative root and reproduces the filed `checks/recompute.out` byte for byte. Apart from the `REPO` line it is identical to my script.
- **The filed `checks/check-section9.md`.** It differs from my CHECK.md only in two places: the filing comment added at the top, and the scratch path replaced by "a scratch clone".

## The items

**B1: answered correctly.**
- 9i now presents REQ-016 as a trade against the array's size, not a hard conflict:
  - kept at 100 W, M1 needs a large array of 12 V class panels in parallel, with no margin at +15 C;
  - raised to 200 W, 400 Wp with 4S18P gives margin.
- The 50 V is stated as a design choice. 9g sets out way (i) and way (ii).
- 9d gives the 4S18P loads by array: 41.35, 42.20 and 42.77 W.
- Out sections 9 and 10 print the trade.
- I checked independently with `energy_budget.simulate()` and every figure matches:
  - the lowest cell temperature at which a design still meets M1:
    - +18.9 C for 4S18P at 1600 Wp in the 100 W window;
    - +19.9 C for 4S19P at 1300 Wp in the 100 W window;
    - +19.7 C for 4S15P at 650 Wp in the 200 W window;
    - +18.4 C for 4S16P at 400 Wp in the 200 W window;
    - +11.2 C for 4S18P at 650 Wp in the 200 W window;
  - the lowest energy points of 14.7 Wh and 1.3 Wh;
  - the out's frontier giving 4S16P from 2100 Wp.
- Way (ii) figures: 1600 Wp is sixteen panels with a fault current near 100 A at 6.25 A per panel. The extra charge offered is about 42 W (84.8 minus 42.8).

**B2: answered correctly.**
- No transport route is claimed in 9h, 9i or either sheet.
- 9h and option A cite REQ-069.
- A search of the energy folder's pages finds no "by air", "by road" or "by sea" outside the filed review's quotation of the old text.

**m1: answered.** The Peli sentence now reads "not tested by this model: the energy model has no geometry", and says the fit rests on the 9h estimate.

**m2: answered.** 9i names 16a and 16d (appendix 32.50, 6 Sep 2026) and says the HF module's new place is not answered. See r4 for a wording nit.

**m3: answered for the temperature.**
- 9h states that the +20 C basis rests on the kit's own heat inside the closed base, which a pack in the open lid does not get, and gives +12.9 C.
- Out section 10 bisects the lowest cell temperature for each candidate.
- Not taken up: my suggestion to list the lid's mass as a tipping load with the lid open (r5).

**m4: answered.** The series-pair figures are labelled ESTIMATE, from the 36-cell class of `energy_inputs.yaml`: about 22 V open circuit at 25 C and about 25 V cold (line 183). The option of wiring all four in parallel at 25 V and about 25 A is also given.

**m5: answered.** The lid is given as 54 or 60 cells by orientation, with rows at the cell's 65.25 mm maximum length plus 1 mm, the fillets not applied, and the LED D1, the knob tips and the hanging tray named. See r1 for a consequence left unapplied.

**m6: answered.** The 21700 figure is given with a representative 5 Ah cell and the note that no datasheet is held.

**m7: answered.**
- Lines 446, 505 and 573 are scoped.
- 9j says `energy_budget.out` keeps its earlier wording and that section 9 governs how it is read.

**m8: answered and tested.**
- `EB_SHA256` pins `energy_budget.py`.
- I appended one line to the clone's `energy_budget.py`: the script refused with exit 3 and named the file.
- I appended one line to `energy_inputs.yaml`: it refused with exit 2.
- Both files were restored afterwards.

**m9: answered.**
- Option C now carries both conditions (about 17 C and the night load within 0.86 W).
- 8d's limit is now 300 words. That matches the owner's "at most 300 words" as recorded in memory, counted by whitespace split.
- `DECISION-OPTIONS.md` is exactly 300 words by that count (266 in the body).

**m10: answered.** 9c states that the sweep goes to 3 kWp and cites the review for 5 kWp and 20 kWp. I had computed those two points with no window. I re-ran them in the 200 W window and got the same answer: 4S15P at 3000 and 5000 Wp, 4S14P at 20 kWp. So the attribution holds.

**m11: answered.**
- The out's section 7 heading now names 4S18P.
- The night now comes from energy_budget.py's own section 3: 11.28 h and 482.7 Wh (the record's 9a follows).

## The owner sheets

Neither sheet claims anything beyond section 9, and neither contains an em or en dash. `DECISION-PARAGRAPH.md` has 109 words of body (131 with its heading and metadata, the same convention as before).

`DECISION-OPTIONS.md`:
- Option A's two ways match 9g: +13 C for way (i) and +19 C or warmer for way (ii).
- The 870 Wh, 72 cells and 3.6 kg figures match 9g.
- The approvals displaced (16a and 16d) and the absence of a transport claim match 9i and 9h.
- REQ-072 FAIL is stated in A, B and C.
- C is separate and conditional.

## Residual minor items (none blocks)

- **r1. The array range for keeping REQ-016 assumes a lid of at most 4S13P.** 9i says "kept, M1 needs about 1300 to 2100 Wp ... and 4S16P to 4S19P". 9f's corrected 60-cell count (a 4S15P lid, 4S21P in all) lowers the start of the range. On the model, 4S21P meets at 900 Wp (1.0 Wh at +20 C, needs about +19.9 C) and 4S20P at 1100 Wp (4.5 Wh, needs about +19.7 C). Neither meets at +15 C. Either state the range as about 900 to 2100 Wp with 4S16P to 4S21P, or name the lid capacity it assumes. The conclusion does not change.
- **r2. Two array sizes in 9c are not the smallest.** 9c gives "4S18P with 1600 Wp" and "4S17P with 2000 Wp", but out section 3 shows the smallest arrays as 1550 and 1950 Wp. "With" is not wrong, but it reads unlike "4S16P from 2100 Wp". This is cosmetic, because way (ii) uses whole 100 W panels.
- **r3. `DECISION-PARAGRAPH.md` gives way (ii) without its condition.** The paragraph sets "today's 100 W stage and sixteen" beside the 200 W way with no condition attached. Add "the second only at about +19 C or warmer", as option A and 9g state; the body would be about 116 words.
- **r4. A wording nit in 9i.** 9i says "D-01 defers the second pack and, with it, the lid tablet bracket and HF". D-01's deferred list names the three items separately, and "with it" suggests a dependency the ruling does not state.
- **r5. The open lid's tipping load is not listed.** 9h lists the lid's mass against the hinges and drop E1, but not as a tipping load with the lid open.
