**ROUND FET (W136, branch `fnd/l4fet` from main `be07863b`, 7 October 2026): DONE on the desk. DONE: L4A-70, the search of 16 makers' sheets on printed maxima (none meets TI's 5 nF, the 40.78 K/W bar and the held 23.93 A together, at any count), (i)(a) kept CONDITIONAL on E-05, the fallback (ii) DRAFTED (`fallback/apply_gen_sch_a_fetpair.py`, `fallback/check_fetpair_netlist.py`, `fallback/apply_check_dd7_fetpair.py`), composed with board A's drafts, five mutations FAIL; L4A-71, the UDC-1 table and the SESSION selection (M-A first, M-B second, each with its end condition). NOT DONE: no independent check of this round; E-05 itself (vendor or bench); TP-E11-29's design target at the pair's bar. NEXT: one focused check (L4A-69's slot); L4A-66 released for M-A by decision L4E11-FET-D2.**

# L4-E11 round FET: a battery-FET set robust to Q-TI-17 (L4A-70) and row (c)'s selection gate (L4A-71) (MESHSAT-1357)

Desk engineering on the makers' printed figures. Nothing here is bought, built, measured or sent, and no V2 board exists. Every figure is
printed by `l4e11_fet.py` in `l4e11_fet.out` (cited below as [OUT n], its section n); the tests are `t_*` in
`v2/ecad/tools/tests/test_l4e11_fet.py`. Labels: MAKER (a printed figure, its class typ or max kept), INFERRED (arithmetic on printed
figures by a stated rule), SESSION (a choice this record takes, with its reason and reversal), READING (a value read from a rendered
page). This round closes no cx46 item; it is the author's own work and UNVERIFIED until checked.

**Why.** The AI-scope register (`_runs/l4ai/REGISTER.draft.md` section 9, dispatch items 6 and 7; `register.tsv` rows L4A-70 and
L4A-71) and W127's challenge (check 1c, finding 5): row (c)'s gate is a battery-FET set robust to Q-TI-17, and the selection between
RE-10's survivable series parts (M-A, first) and an automatic diagnostic (M-B, second). HO-L is E11-37: the charger's BATDRV into three
BUK6Y10-30P (Q39, Q40, Q42) against TI's "the Ciss of P-channel MOSFET should be chosen less than 5 nF" (SLUSE65A p.92), with Q-TI-17
drafted and UNSENT (`clarification/TI-QUESTIONS.md`). Round 11 (`l4e11_power.out` 21b to 21e) compared three approaches and selected
(i)(a), the three; the pair (ii) is under 5 nF only on a typical; L4-E9's UDC-1 records (S3), "a P-FET whose sheet prints both hot
RDS(on) at -8.5 V and Ciss maxima: none found among the parts read".

**Closure contract (constitution section 4; the register's entries restated).** Type: unresolved design choice (L4A-70, L4A-71) resting
on missing vendor evidence (E-05). Inputs: the records named in [OUT 1], all at `be07863b`. Requirement: C-PROT rev 1 (every series part
within its limits below and above the trip) and TI's BATDRV selection rule. Smallest deliverable: this page, the script, its output, the
fallback draft with its check and the test. Acceptance: the selection's gate load on printed maxima, or the fallback draft composed with
failing mutations; it fails on a typical Ciss used as a limit. Owner: this record. Dependency: none for the desk part; E-05 for the
closure. Checkpoint: one focused independent check.

## 1. The case and the inputs ([OUT 1])

- **E-1's case** (record l9stk `l9stk_protection.out`; MAKER rows through RECORD): the hottest battery FET at most its limit **held at
  23.93 A** (the breaker's held current, record l8p `L8P-BREAKER.md`) from L4-E12's 76.25 C air, the band 9.16 K, R17 (5 mOhm) dissipating
  2.86 W in place with its coupling at most 1 K/W designed apart; the budget at a 150 C limit is 64.59 K for the FETs and R17's coupling.
- **The bar** (round 11, INFERRED): the three's worst-split (Zself + 2 Zmut) at most **40.78 K/W**; the pair's (Zself + Zmut) at most
  **20.39 K/W**; the RDS(on) allowance 21.136 mOhm at -8.5 V and 150 C (15c's two chords, E11-36). This round's rules reproduce all three
  within 0.1 % and take the records' printed figures (`t_the_screen_reproduces_the_records_figures`).
- **TI's drive** (MAKER, SLUSE65A): BATDRV is the "P-channel battery FET (BATFET) gate driver output" (p.5); VBATDRV_ON 8.5 / 10 / 11.5 V,
  RBATDRV_ON 3 / 4 / 6 kOhm (p.17); the 5 nF rule names no drain-source voltage (p.92).
- **The docking pulse** (16d, E11-30): 242.9 A peak, taken whole in one body diode, no sharing credited.

## 2. The screen (SESSION: scope and readings; INFERRED: arithmetic) ([OUT 2])

- **Scope (SESSION).** P-channel parts, |VDS| at least 30 V (VBAT's SMCJ18A clamp at 29.2 V with the cells' side near 0 V, 20g),
  |VGS| rating at least 11.5 V (BATDRV's largest printed drive), like parts in parallel on one BATDRV node. Read in full: the makers whose
  sheets print a Ciss or QG(tot) maximum, Vishay's automotive SQ P-channel range (SQJ403EP, SQJ407EP, SQJA37EP, SQJQ131EL, SQS407ENW,
  SQS415ENW, SQS401EN) and Infineon's -30 V OptiMOS P3 range as its 2023 P-channel selection guide lists it (BSC030P03NS3 G,
  BSC060P03NS3E G, BSC084P03NS3 G, BSZ086P03NS3 G, BSZ120P03NS3 G, BSZ180P03NS3 G); the record's earlier parts restated (Nexperia
  BUK6Y10-30P and PXP9R1-30QL, AOS AONS21357). Sixteen parts. **An N-channel FET is outside the drive the design has**: BATDRV pulls the
  gate 10 V below VSYS (p.5), a high-side N-channel part needs a gate above its source, and TI's BATDRV loops are P-channel loops.
  Not read: makers whose sheets print typical capacitances only (the class's usual practice; a typical gives no limit), and TI's own
  P-channel NexFET range, which this round did not open (a search line for the supplier's phase 1).
- **G, TI's 5 nF on PRINTED maxima.** The count's summed Ciss maximum under 5 nF at the maker's own VDS (-15 to -25 V; near 0 V is not
  bounded by any row, so a G pass still rests on Q-TI-17 (e)), or the summed QG(tot) maximum at -10 V under 50 nC, the charge a 5 nF
  capacitance takes over BATDRV's 10 V (a SESSION reading TI does not state; Q-TI-17 asks whether a charge limit is the better statement).
  A sheet that prints a typical only gives no G: the script refuses a limit read from a typical (`limit()`, GuardError).
- **T, the 40.78 K/W bar.** Round 11's worst split generalised to n like FETs with no printed RDS(on) minimum: one FET at R / x and n - 1
  at R, the hottest rise I^2 R Zself (x + m (n - 1)) / (x + n - 1)^2, largest over x and m at m = 0 and x = n - 1, a factor
  **F0 = n^2 / (4 (n - 1))** over the even split for n at least 3 (9/8 for three) and 1 for one or two; a brute-force search over the split
  and the coupling confirms it (`t_the_worst_split_factor_is_the_largest_of_a_search_over_split_and_coupling`). The set's own bar on
  (Zself + (n - 1) Zmut) per FET is B n^2 / (I^2 R F0) and must be at least 40.78 K/W.
- **H, the held 23.93 A on printed figures.** The bar is computed at E-1's current with R the allowance at -8.5 V and the part's limit
  (25 K under its rating) by 15c's two chords on printed maxima. A sheet with no printed hot maximum (the six Infineon parts) gives no
  allowance: the screen then uses its -10 V, 25 C maximum, under any hot -8.5 V figure, which can show a FAIL and never a PASS.
- **D, information.** The docking pulse against the printed body-diode pulse rating, whole in one FET (E11-30's rule).

The rows the screen uses are read back from each sheet's cited page (pdftotext); five Infineon sheets of 16 November 2009 carry no usable
text layer, so their rows are this record's READING of the rendered pages (`inputs/fet-search-readings-2026-10-07.json`, each with its
sha256). The eleven sheets new to the tree are held back by their terms (`fetch_held_back_fet.py`, sha256 pinned).

## 3. The candidates ([OUT 3]; MAKER rows, INFERRED figures; the best set each part allows under G)

| Part (maker; sheet) | Rating, limit | R at -8.5 V and the limit, mOhm | Ciss typ / MAX at VDS; QG(tot) MAX at -10 V | Largest count under 5 nF (Ciss; QG) | Bar for that count, K/W (needs 40.78) | Held at the 40.78 bar | Device Rth max; ISM | Verdict |
|---|---|---|---|---|---|---|---|---|
| BUK6Y10-30P (Nexperia, 17 Apr 2020) | 175 C, 150 C | 21.136 allowance | 2.36 typ, **no max**; 64 nC | none; 0 | no set | | 1.4 K/W; 320 A | no G on printed maxima |
| PXP9R1-30QL (Nexperia, 5 Jan 2021) | 150 C, 125 C | 15.619 allowance | 2.86 typ, **no max**; 86 nC | none; 0 | no set | | 2.5 K/W; none | no G |
| AONS21357 (AOS, Rev 2.1) | 150 C, 125 C | 12.384 allowance | 2.83 typ, **no max**; 70 nC | none; 0 | no set | | 2.6 K/W; none | no G |
| SQJ403EP (Vishay, Rev A 2015) | 175 C, 150 C | 19.166 allowance | 3.40 / 4.50 at -15 V; 109 nC | 1; 0 | 5.62 | 8.89 A | 2.2 K/W; 84 A | FAILS T |
| SQJ407EP (Vishay, Rev B 2022) | 175 C, 150 C | 7.471 allowance | 8.20 / 10.70 at -25 V; 260 nC | 0; 0 | no set | | 2.2 K/W; 155 A | no G |
| SQJA37EP (Vishay, Rev B 2022) | 175 C, 150 C | 13.573 allowance | 3.62 / **4.90** at -25 V; 100 nC | **1**; 0 | **7.94** | 10.56 A | 3.3 K/W; 120 A | FAILS T |
| SQJQ131EL (Vishay, Rev A 2021) | 175 C, 150 C | 2.369 allowance | 23.59 / 33.05 at -15 V; 731 nC | 0; 0 | no set | | 0.25 K/W; 1100 A | no G |
| SQS407ENW (Vishay, Rev A 2018) | 175 C, 150 C | 19.083 allowance | 3.52 / 4.57 at -20 V; 77 nC | 1; 0 | 5.65 | 8.91 A | 2.4 K/W; 64 A | FAILS T |
| SQS415ENW (Vishay, Rev C 2019; 40 V) | 175 C, 150 C | 28.481 allowance | 3.71 / 4.83 at -25 V; 82 nC | 1; 0 | 3.78 | 7.29 A | 2.4 K/W; 64 A | FAILS T |
| SQS401EN (Vishay, Rev D 2022; 40 V) | 175 C, 150 C | 54.956 allowance | 1.57 / **1.88** at -20 V; QG max at -4.5 V only | **2**; not shown | **7.85** | 10.50 A | 2.4 K/W; 64 A | FAILS T |
| BSZ086P03NS3 G (Infineon, Rev 2.4 2019) | 150 C, 125 C | 8.6 bound | 3.19 / 4.79 at -15 V; 57.5 nC | 1; 0 | 7.46 (bound) | 10.23 A | 1.8 K/W; 160 A | FAILS T |
| BSC030P03NS3 G (Infineon, Rev 2.1 2009) | 150 C, 125 C | 3.0 bound | 10.5 / 14.0 at -15 V; 186 nC | 0; 0 | no set | | 1.0 K/W; 200 A | no G |
| BSC060P03NS3E G (Infineon, Rev 2.1 2009) | 150 C, 125 C | 6.0 bound | 4.53 / 6.02 at -15 V; 81 nC | 0; 0 | no set | | 1.5 K/W; 200 A | no G |
| BSC084P03NS3 G (Infineon, Rev 2.1 2009) | 150 C, 125 C | 8.4 bound | 3.19 / 4.79 at -15 V; 58 nC | 1; 0 | 7.64 (bound) | 10.35 A | 1.8 K/W; 200 A | FAILS T |
| BSZ120P03NS3 G (Infineon, Rev 2.1 2009) | 150 C, 125 C | 12.0 bound | 2.24 / 3.36 at -15 V; 45 nC | 1; 1 | 5.34 (bound) | 8.66 A | 2.4 K/W; 160 A | FAILS T |
| BSZ180P03NS3 G (Infineon, Rev 2.1 2009) | 150 C, 125 C | 18.0 bound | 1.48 / **2.22** at -15 V; 30 nC | **2**; 1 | **14.25** (bound) | 14.15 A | 3.1 K/W; 160 A | FAILS T |

"Bound" is the favourable -10 V, 25 C maximum: an upper bound on the bar, so each such FAIL holds at any hot figure. Every printed ISM above is
under the 242.9 A docking pulse except the BUK6Y10-30P's 320 A and the SQJQ131EL's 1100 A; the PXP9R1-30QL and the AONS21357 print
none (D, information).

## 4. The class bound ([OUT 4]; INFERRED)

For n like FETs, G by Ciss and T together need Ciss(max) x R under 5 nF x 4 (n - 1) B / (bar I^2 n), which rises with n towards
**52.87 nF.mOhm** for a part rated 175 C (limit 150 C) and **31.45 nF.mOhm** for a part rated 150 C (limit 125 C); by QG the same limit is
528.7 and 314.5 nC.mOhm. Every part read with a printed Ciss maximum sits above its own limit (from 36.1 nF.mOhm, the BSC060P03NS3E G on
its favourable bound against 31.45, to 137.4, the SQS415ENW on its allowance against 52.87), and the parts with no printed maximum give no
G at all. So **no set of the parts read meets G and T together at any count**, whatever pour the count is given. The reason is physical
and general: a lower gate load means a smaller die and a higher RDS(on), and the product of the two printed maxima, not either alone,
decides; no P-channel technology read reaches the product the case needs.

## 5. L4A-70: the selection, and the fallback drafted ([OUT 5], [OUT 6])

**The record's options on the same basis:** (i)(a) the three: no Ciss maximum printed (7.08 nF typical at -15 V, about 8.61 near 0 V),
QG(tot) 192 nC at most against 50, bar 40.78 K/W, held at the 40.78 bar 23.94 A: T and H MEET, CONDITIONAL on E11-29 and E11-36, G NOT
SHOWN. (ii) the pair: 4.72 nF typical at -15 V (about 5.74 near 0 V), 128 nC at most, bar 20.39 K/W (half), held at the 40.78 bar
16.93 A. (S2) one: 2.36 nF typical, 64 nC at most, bar 5.10 K/W on E-1's case, held at the 40.78 bar 8.46 A. **Guard:** the pair's
4.72 nF is a typical; read as a limit it would pass G; the screen refuses that reading, and the test relabels it as a maximum to show
that its predicate catches the change (`t_a_typical_used_as_a_limit_is_refused`).

**Selection (SESSION, decision L4E11-FET-D1 in section 7):** no set meets the three limits on printed figures, so **(i)(a) stays
selected, CONDITIONAL on E-05** (TI's answer to Q-TI-17 stated as a limit, or the bench of block E11-37), with E11-29 and E11-36 as
before. **E11-37 stays OPEN.** Nothing about the drawn circuit changes.

**The fallback (ii), drafted now so that a negative E-05 needs no new engineering** (in `fallback/`, outside L4-E9's change list on
purpose: `l4e9_power_path.py` reads every `records/l4e*/apply_*.py` as a pending baseline draft and refuses one its list does not name;
a fallback is not the baseline, as record l4e7's `apply_gen_sch_e_p0sol_b2.py` is not; on a negative E-05 its owner adds the row):
- `fallback/apply_gen_sch_a_fetpair.py` (DRAFT, NOT APPLIED, gated as the charger draft is by `RELEASE.md`, and applied only on a negative E-05):
  after `apply_gen_sch_a_charger.py`, which it requires, it removes Q42, draws Q39 and Q40 "one of two in parallel", restates the battery
  FETs' comment for the pair (TI's rule against the pair's TYPICAL Ciss, the pair's bar 20.39 K/W, the layout with record l8p's PTC or
  guard at the two drain tabs' centroid), sets CH_BATQ's loads to Q39 and Q40 at 5.0 A each and drops Q42 from U3's value text, the
  section comment, VBAT's always_on_why and the sheet group. No pin map changes and no designator is added; the result names no Q42.
- `fallback/check_fetpair_netlist.py` reads a regenerated board A netlist: the set exactly the pair (or the three with `--want three`), each pad
  map (source on VBAT, gate on CH_BATDRV, drain tab on CH_BATQ), CH_BATDRV reaching only U3's BATDRV, the set's gates and DD-7's Q49,
  CH_BATQ reaching only the set, R17 and R149.
- `fallback/apply_check_dd7_fetpair.py`: DD-7's check names the three in its BODY group; on adopting the pair its tuple becomes Q39 and Q40.
- **Composition and mutations** (`t_the_fallback_composes_runs_reads_the_pair_and_its_mutations_fail`): board A composed in main's L4-E9
  order with record l8p's PTC, this record's DD-7, record l8p's thermal guard and its fail-safe delta before d8dec31's mainpb, then the
  fallback: the generator runs to its end (781 parts, one fewer than the three's 782), the pair reads DRAWN, DD-7's check reads DRAWN on the
  pair; refused on a board without the charger draft, a second time and on the tree's own generator; five mutations each fail (the
  three left drawn, a third P-channel gate on BATDRV, Q40 reversed, Q40's gate off BATDRV: the pair's check FAILS; CH_BATQ's intent still
  naming Q42: the generator refuses). A mutation of the draft's comment that states the pair's 4.72 nF as a maximum fails the text check.
- **What the fallback still rests on (it is never written as a pass):** the pair is under 5 nF only on a TYPICAL at -15 V, so it rests on
  Q-TI-17 (e); its bar 20.39 K/W is shown achievable by no printed figure, so E11-29's coupon decides it on the pair; TP-E11-29's design
  target with its fixture allowance (37.59 K/W for the three, round 16) is restated at the pair's bar before layout, a step this round
  does not take; a result with the three does not transfer to the pair.

**Closure credit, stated by the common brief's three parts:** (a) the fallback composes with board A's pending drafts in L4-E9's order
and the generator runs: YES; (b) its changed nets are read in the regenerated netlist with mutations that fail: YES; (c) its electrical
acceptance on its case on printed figures: NOT SHOWN (the pair's gate load rests on a typical, its bar on the coupon). L4A-70 reads
**DONE AS CONDITIONAL on E-05** as the register's section 1 defines it: the AI deliverable is complete, what remains is E-05 whose AI
preparation (Q-TI-17, drafted) is done, and no further desk work removes the condition.

## 6. L4A-71: the UDC-1 table ([OUT 7]; coupling HO-L, RE-10's M-A and E11-29)

| Option | FETs | RDS(on) at -8.5 V and the limit | Gate load on printed maxima against 5 nF | Zth: the needed installed bar per FET (device's own) | Against 40.78 K/W | Held at the 40.78 bar (needs 23.93 A) | HO-L (E11-37) | RE-10 M-A | E11-29 |
|---|---|---|---|---|---|---|---|---|---|
| (i)(a) three BUK6Y10-30P, drawn | 3 | 21.136 mOhm allowance (E11-36) | NOT SHOWN: 7.08 nF typ, 192 nC max | 40.78 K/W (1.4 K/W) | meets, CONDITIONAL | 23.94 A | OPEN on E-05 | holds 23.93 A at its bar, CONDITIONAL on E11-29, E11-36, E-05 | the coupon at 40.78 K/W (design target 37.59) |
| (ii) the pair, Q42 removed: the fallback, drafted | 2 | 21.136 allowance | NOT SHOWN: 4.72 nF typ (5.74 near 0 V), 128 nC max | 20.39 K/W (1.4) | fails: half | 16.93 A | rests on Q-TI-17 (e) | holds 23.93 A only at 20.39 K/W | the coupon at 20.39 K/W |
| (S2) one BUK6Y10-30P, a case path | 1 | 21.136 allowance | NOT SHOWN: 2.36 nF typ, 64 nC max | 5.10 K/W junction to air (1.4) | fails | 8.46 A | rests on Q-TI-17 (e) | only with a case path at 5.10 K/W (Layer 7) | no pour coupon |
| 2 x BSZ180P03NS3 G (best G set) | 2 | 18.0 bound (no hot max printed) | MEETS at -15 V: 4.44 nF max | at most 14.25 K/W (3.1) | fails | 14.15 A | Q-TI-17 (e) only | fails (bar); ISM 160 A under the pulse | tighter than the pair's |
| 1 x SQJA37EP | 1 | 13.573 allowance | MEETS at -25 V: 4.90 nF max | 7.94 K/W junction to air (3.3) | fails | 10.56 A | Q-TI-17 (e) only | only with a case path; ISM 120 A | no pour coupon |
| 2 x SQS401EN | 2 | 54.956 allowance | MEETS at -20 V: 3.75 nF max | 7.85 K/W (2.4) | fails | 10.50 A | Q-TI-17 (e) only | fails (bar); ISM 64 A | tighter than the pair's |
| M-B (method, not a FET set): an automatic self-checking diagnostic | n/a | n/a | n/a | n/a | n/a | n/a | independent | replaces M-A's survival by bounded detection; needs an observer off board A and new inter-board lines (BRK:1400-1402's objection unanswered); HO-B stays open | n/a |

**What the table shows.** HO-L's gate-load limit and M-A's survival pull in opposite directions through one quantity, the die: among the parts read, every set
light enough for TI's 5 nF on a printed maximum holds at most about 14 A at the 40.78 K/W bar, and the only set that holds 23.93 A at it
is the drawn three, whose gate load is not shown on printed figures. So the coupling is decided by E-05, not by a part search: on a
positive E-05 the three carry M-A (with E11-29 and E11-36); on a negative one the fallback carries HO-L only at its typical and M-A only
at 20.39 K/W.

## 7. The SESSION decisions (L4A-70 and L4A-71)

The two-part test of 21 September 2026 sends neither to the owner: no class of `v2/ecad/tools/reserved.json` names `gen_sch_a.py` or a
record's draft, nothing is bought or changed in the drawn circuit, no claim about the kit changes, and the residual risk each carries is
removed by a named measurement or vendor statement (E-05, E11-29, E11-36).

```yaml
- id: L4E11-FET-D1
  title: "L4A-70: the battery-FET set robust to Q-TI-17: none exists among the parts read; (i)(a) kept, the fallback (ii) drafted"
  authority: SESSION
  authority_why: "it changes no line a class of reserved.json protects (gen_sch_a.py and the records' drafts are none of them), spends nothing, changes no claim about the kit, and the residual risk it carries is removed by a named vendor statement or bench (E-05) and the coupon (E11-29); after the search only one option keeps both the 40.78 K/W bar and the held 23.93 A, so no choice for the owner is standing (the owner's ruling of 21 September 2026 makes such an engineering decision the session's)"
  ruled_by: "SESSION (W136) under the owner's rulings of 21 and 26 September 2026"
  ruled_on: 2026-10-07
  reversed_by: "a printed Ciss or QG(tot) maximum, on a sheet this round did not read, that puts a set of P-channel parts under 5 nF with its own worst-split bar at or above 40.78 K/W at the breaker's held 23.93 A on printed RDS(on) maxima (l4e11_fet.py's screen reads it MEETS ALL THREE); or a negative E-05, which applies fallback/apply_gen_sch_a_fetpair.py and fallback/apply_check_dd7_fetpair.py through RELEASE.md"
  outcome: "No set of the 16 parts read meets TI's 5 nF on printed maxima, the 40.78 K/W bar and the held 23.93 A together, at any count (the class bound: Ciss max x R above 52.87 nF.mOhm for 175 C parts and 31.45 for 150 C parts). (i)(a), the three BUK6Y10-30P, stays selected and CONDITIONAL on E-05, E11-29 and E11-36; E11-37 OPEN. The fallback (ii), the pair with Q42 removed, is drafted, composed and mutated, and stays conditional on Q-TI-17 (e) and on its 20.39 K/W bar."
- id: L4E11-FET-D2
  title: "L4A-71: row (c)'s selection gate between RE-10's M-A and M-B, coupled with HO-L and E11-29"
  authority: SESSION
  authority_why: "it orders two drafted-or-to-be-drafted engineering methods and changes no protected line, spends nothing and changes no claim; it adds protection and lowers none (no limit, floor, fan or service is touched); the evidence that ends M-A (E11-29's coupon, E11-36, E-05) is a named measurement or vendor statement; W127's challenge (check 1c, finding 5) recommends the same order"
  ruled_by: "SESSION (W136) under the owner's rulings of 21 and 26 September 2026"
  ruled_on: 2026-10-07
  reversed_by: "M-A's end condition below, which enters M-B; or an independent check that finds M-A's FET part unsupported on the same printed figures (two negative checks end M-A by the constitution's section 5)"
  outcome: "M-A first, M-B second. M-A (L4A-66, released by this decision): every series part of the pack path held indefinitely at the breaker's held 23.93 A from 76.25 C inside its PRINTED limits, so a latent guard failure no longer removes protection and path 2's retries never exceed a current the parts hold (HO-A's consequence and HO-B closed together when L4A-66's acceptance holds); its FET part is (i)(a) at the 40.78 K/W bar, CONDITIONAL on E-05, E11-29 and E11-36; L4A-66 drafts and checks the other series parts (R17, F1, the pours and the pack-path contacts). M-A's END CONDITION, any one of: (1) E11-29's coupon reads the three's hottest junction over 150 C at 23.93 A held from 76.25 C at the 40.78 K/W bar, or E11-36 reverses the allowance beyond what the bar absorbs; (2) E-05 is negative AND the pair's coupon refuses 20.39 K/W, so no FET set both satisfies TI and holds 23.93 A on a pour; (3) L4A-66 finds a series part over its printed limit at 23.93 A held with no supported correction after two negative checks of that correction. Then M-B. M-B: an automatic self-checking diagnostic with a bounded detection and response interval covering faults after start-up and faults of the diagnostic itself (the owner's part 24), the breaker never opened by the test in service, answering L8P-BREAKER.md's objection (a test of a shunt opens the breaker in service; a cross-check of the two VTEMP outputs sees the switches, not the gate networks or the shunts), with an observer off board A (a board B supervisor or the panel RP2040) over new inter-board lines; drafted, composed, mutations failing; HO-B then stays L4A-65's. M-B's END CONDITION: two negative checks of the same diagnostic end it; the item is then handed over as the receiving company's fault-tolerant redesign (RE-10's own words) with the cases named, and an owner item is prepared only if the evidence shows a requirement change is necessary."
```

## 8. What stays open, and findings for other records

- **Open:** E11-37 (HO-L) on E-05; E11-29 and E11-36 as before; RE-10 until L4A-66's acceptance holds (or M-B's); TP-E11-29's design
  target at the pair's 20.39 K/W bar, owed only if the fallback is triggered.
- **For the coordinator (the register is yours):** L4A-66's row reads "M-B ... only if L4A-71 shows no FET set meets the held current,
  TI's 5 nF and the 40.78 K/W bar together". Read literally on this round's result it would select M-B now. Decision L4E11-FET-D2 reads
  TI's 5 nF as missing vendor evidence (E-05), not a demonstrated failure (constitution section 4; Amendment 1 item 2), keeps M-A first
  on (i)(a) CONDITIONAL, and states M-A's end conditions; the row's release text would be restated to "released by L4A-71's selection
  (L4E11-FET-D2): M-A first, CONDITIONAL on E-05, E11-29 and E11-36; M-B on M-A's end condition". L4A-70 reads DONE AS CONDITIONAL on
  E-05 (register section 1, the case it names).
- **For L4-E9's UDC-1 row (record l4e9, its owner's):** the (S3) cell, "none found among the parts read (L4-E11 16a, 16c)", can cite this
  round: 16 parts, the class bound, the best printed-maximum sets each under the bar.
- **For REMAINING-ENGINEERING HO-L (record l4close):** "(ii) two FETs, the BUK6Y10-30P pair ... a draft then owed" is now drafted
  (`fallback/apply_gen_sch_a_fetpair.py`), still conditional.
- **For the supplier's phase 1:** TI's P-channel range and makers that print typical capacitances only were not read; a part found there
  enters the same screen (`l4e11_fet.py`), and the class bound says what it must beat.

## 9. Status

| Item | State |
|---|---|
| L4A-70 | DONE AS CONDITIONAL on E-05: no set meets the three limits on printed figures; (i)(a) kept; the fallback (ii) drafted, composed, mutated; E11-37 OPEN |
| L4A-71 | DONE: the UDC-1 table; L4E11-FET-D2, M-A first (released to L4A-66), M-B second, each with its end condition |
| closure credit | no circuit of the tree changed; the fallback's (a) and (b) shown, (c) NOT SHOWN (typical gate load, coupon bar) |
| independent check | none yet (UNVERIFIED) |

Not claimed: nothing here is verified, built or measured; the software tests establish this record's own behaviour only.
Acknowledgement: the execution constitution (sections 3 to 5 and 8) was read and applied: one system basis (E-1's case), a bounded
closure contract, a single search method with a stated end (the class bound), and tests that fail on the defect they guard.
