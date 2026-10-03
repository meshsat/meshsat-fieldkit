accepted: no

# L4-CLOSE: the coordinator's check 3, after the collaborator's targeted recheck (cx37, NOT YET) and the owner's reviews

This is the coordinator's closing check, not a model review and not an Astra check. Both collaborator runs for L4-CLOSE are spent
(cx36, `astra-check-l4close-1.md`, NOT YET on `8fbb68b6`; cx37, `astra-check-l4close-2.md`, NOT YET on `b138fec0`); their verdicts
stand as filed and are never restated as accepted. This check reads each correction made after cx37 at the commit that made it,
recomputes what it states it recomputed, and says plainly where it only read a statement. `accepted: no` above is this check's own
first line: the closure gate it would serve stays BLOCKED (the owner's three decisions), so nothing here accepts the design.

Candidate read: `94971c8ce81a0276a22c4ff3c7594dc3deb46736` (set 27's frozen candidate; runner checks: targeted modules 274 passed, 0 failed, 1 gated skip; every validator current and 0 errors; the box suite's result is the promotion record's). The corrections' commits: L4-E11 `b929d8be` and `a1d15601`;
L4-E7 `1a73f5b4`, `eb49d179` (the output's residues), `04707e3c` (the compute/render split and the sentence-keyed lead scan), `d562e75a` (R-176's 63 A; set 28); L4-E11 `73d68c8c` (the summary's residue), `1080e085` (board E's fan capacitors renumbered against the integrated drafts); L4-E9 `20188e03`, `22cb4c16`, `4e044c2c`, `1ba24ca6`, `a8888abc`, `0862053d`, `938e442a`.

## cx37's six blocking items

| # | The item (cx37's words, short) | Correction, commit | What this check did | State after the correction |
|---|---|---|---|---|
| 1 | apply_gen_sch_e_aux.py reuses U18, R59 to R65, C65 to C71 of the solar drafts | L4-E11 `b929d8be`: U22, R103 to R109, C135 to C141; a test composing every board E draft in the change list's order | RAN `t_the_board_e_drafts_add_disjoint_designators` and `t_the_board_a_drafts_add_disjoint_designators` at `b929d8be`'s descendant `a1d15601`: both PASS (test_l4e11 54 passed, 0 failed) | CLOSED (the defect is corrected and a test holds it; nothing is applied). Set 27's targeted run then found a SECOND collision the branch could not see (L4-E11's C135, C136 against L4-E7's port bank): corrected at `1080e085` (C142 to C148), and d8dec31's board E capacitor draft placed last in board E's round (`938e442a`); the composed board E generator carries no duplicate (L4-E9's test) |
| 2 | B6's 3.30 uH passing floor contradicts the pin budget; a connector fault credits lead resistance | L4-E7 `1a73f5b4`: the passing floor withdrawn, both fault positions, the connector case with no lead resistance; the complete pin budget both polarities; the stage question to the engineer (B6-ENG-1) | READ the record and the draft at `1a73f5b4` and the output's residues corrected at `eb49d179` (no passing loop; the turn-off compared with the absolute maximum in words matching its sign); did NOT recompute the budget (it needs the model's waveform at Q12's turn-off instant) | the overclaim CLOSED AS CONDITIONAL (a correct statement, handed to the engineer); the DESIGN ITEM B6 is NOT CLOSED and WORSE than before: at a connector fault the pins reach -0.3021 V, past the -0.3 V absolute maximum (an absolute-rating violation, kept apart from the missed 0.240 V target); INP and PV_F over their margin and recommended rows there |
| 3 | sense_ripple keeps negative monitor current; the error's direction and the "no damage" consequence unsupported | L4-E7 `1a73f5b4`: `avg_clip` = mean of min(max(v, 0), vlim) (8705af p.31); +7.9 % at the regulation's current, -10.2 % at the trip, MODELED on a clipping model the sheet does not print; "no damage" withdrawn, -0.4329 V at 10 ns named | READ the function at the source (line 538: rectified at zero, clipped at vlim); did NOT recompute the percentages (the reviewer's own reconstruction read +4.41 %; both high, magnitude model-dependent) | CLOSED AS CONDITIONAL (Analog Devices item 7, bench R-189); D-16 OPEN (the demonstrated operating-range exceedance stands) |
| 4 | B2's pair lacks hot resistance, installed coupling, BATDRV loading and the hot docking waveform | none needed beyond the statement: cx37 asked to keep them open; L4-E11 `a1d15601` (L4-QR01) gave every specimen row its thermal boundaries, extrapolation and re-test triggers | READ 17d at `a1d15601`; RAN its property test (PASS) | CLOSED AS CONDITIONAL (E11-29, E11-30, E11-36, E11-37 on named specimens); the design item NOT CLOSED |
| 5 | CP01's 566 A from RON specified at 0.6 to 6 A; 1.5 s a timeout, not a duration | L4-E11 `b929d8be`: 17a states 566 A as a resistive extrapolation and E11-38 (c)'s test target, the start into a short not bounded by printed data, the retry duty withdrawn; E11-38 (d) and (h) | READ 17a rows (2) and (3) and the L4-F03 status row at the source; FOUND a residue: the record's opening summary (line 85 at `a1d15601`) still reads "a short's ceiling 566 A for 4.5 us, inferred; the start into a short up to 1.5 s" | CLOSED AS CONDITIONAL (E11-38 on the bench): the residue was corrected at `73d68c8c` (READ at the source: the summary now reads the 566 A as a resistive extrapolation and a test target and the start into a short as not bounded by printed data; a test holds the withdrawn phrases to withdrawal sentences) |
| 6 | L4-F04: one failed arrangement read as a requirement conflict; the e-paper soak at ambient +55 / +60 C | L4-E9 `20188e03` (L4-E12's CONFLICT_RULE and the soak): a conflict needs every arrangement the design admits measured failing, or a bound; the soak at +70 C on the glass for E5's 6 h and E3-O's 4 h with recovery reads | READ the rule's text in both records at the source; the test holding it PASS (test_l4e9 and test_l4e12 at `22cb4c16`: 88 passed) | CLOSED (the rule and the specimen corrected; thermal feasibility itself stays open on T-H1 and the storage evidence) |

## cx37's minors

| Item | Correction | State |
|---|---|---|
| R96 at 1 % against the analysis's 0.1 % | L4-E7 `1a73f5b4`: R96 100k 0.1 % 25 ppm (YAGEO RT0603BRD07100KL); the test reads both resistors' tolerances from the draft (READ at the source: draft lines 24 and 71) | CLOSED |
| 16d's withdrawn sentence | L4-E11 `b929d8be`: marked historical, overridden by 17b | CLOSED |
| the fan rail's window without the divider | L4-E11 `b929d8be`: 11.512 to 12.431 V with the 1 % divider, inside 10.8 to 13.2 V | CLOSED |

## The owner's reviews, their items' states

| Item | Source | Correction | State |
|---|---|---|---|
| L4-F01 (B6) | review of the provisional fixes | L4-E7 rounds 2 to 5 | the design item NOT CLOSED (an absolute-rating violation at a connector fault); the handoff B6-ENG-1 states it |
| L4-F02 (B2) | same | L4-E11 sections 16, 17b, 17d | CLOSED AS CONDITIONAL as a statement; the design item open on its specimens |
| L4-F03 | same | L4-E11 16e, 17a, 18 (U42) | "sustained-overload remedy drafted; fault qualification open" |
| L4-F04 | same | L4-E12 17.9 and L4-E9 (20188e03) | CLOSED (the classes and the rule) |
| L4-CP01 | review of the 22:30 checkpoint | as cx37 item 5 | as cx37 item 5 |
| L4-CP02 | same | L4-E11 17b, 17d (a1d15601) | CLOSED AS CONDITIONAL (E11-30's six-sample test, prototype evidence for that lot) |
| L4-CP03 | same | L4-E11 `apply_gen_sch_a_charger.py`, its test | CLOSED (cx37 read it CLOSED) |
| L4-QR01 | review of the qualification route | L4-E11 `a1d15601`, L4-E9 `4e044c2c` | CLOSED (the transfer rule per specimen row; acceptance stays with the measurements) |
| L4-QR02 | same | L4-E9 `4e044c2c` | CLOSED (R-167 blocks the proposed pack's adoption and its mechanical release only) |

## What this check does not establish

No circuit is applied, built or measured. No figure of the solar guard's budget, the sense model or the thermal lines was
recomputed here beyond what the rows say. The design's three decisions stand: architecture candidate CONDITIONAL; power-design
closure gate BLOCKED (B6 an absolute-rating violation at a connector fault, D-16 OPEN, the battery switch and the eFuse's fault
envelope on their specimens, U-01, U-02, U-04); fabrication release BLOCKED; the engineer handoff READY TO START, provisional.

## The supplier handover reviews (the owner's, 3 October 2026)

L4-SH01 (the thermal acceptance, G_measured - U_G >= G_required), L4-SH02 (the replay levels, recipient replay pending until the
commit is public) and L4-SH03 (the headline names the open design defects) were corrected in `v2/docs/handover/supplier/
SUPPLIER-HANDOVER.md` (`d48becdc`); the owner's follow-up review read them CLOSED at the documentation level and the package READY
for an initial supplier engineering review and quotation (`records/l4close/REVIEW-SUPPLIER-HANDOVER-FOLLOWUP-AS-RECEIVED.md`).
