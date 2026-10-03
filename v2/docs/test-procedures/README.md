# Test procedures for the prototype qualification (MESHSAT-1357; the supplier's phase 2)

**Status: PROPOSED, for the supplier to review and agree before execution.** Written 3 October 2026 under MESHSAT-1357 on the
owner's instruction of the same day (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-03-SUPPLIER.md`). The MeshSat field kit V2 is an
**unbuilt prototype design**: no board has been fabricated, assembled, powered or measured, and nothing in these procedures has
been run. They were written by an AI agent session from the project's records; none of them is an electrical engineer's
sign-off, and none has been reviewed by a test laboratory.

**What this folder is.** The records already specify each experiment the power design still needs (what to measure, on which
specimen, against which limit, and what a result may be used for). This folder turns those specifications into procedures a
supplier's engineers can price, review, correct and run. It changes no specification: every pass condition is quoted word for
word from the register row or the record that owns it, and `tp_check.py` holds each quote to its source in this tree. Where a
procedure needs a figure no record states, it writes `TBD (owed by <row>)` naming the register row that owes it; it never
invents the figure. Method details that the records leave open (a sampling rate, the order of runs, a proposed instrument
class) are marked as this folder's **proposal**, for the supplier to accept or replace.

The entry page of the supplier package is `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`; its sections 5 and 6 explain why
these experiments exist. The route table these procedures implement is section 5d of
`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`; each board A specimen's own block is section 17d of
`v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md`; the acceptance of every row is in
`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`.

## 1. The procedures

| Procedure | File | Register rows | What it decides | Performer (from 5d) |
|---|---|---|---|---|
| TP-TH1 | `v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md` (written earlier, not in this folder, not rewritten here) | R-104, R-151 | U-02: the sealed case's conductance per required mode | an engineer, on a bench |
| TP-E11-29 | TP-E11-29.md | R-159 | D-14's installed thermal path of the battery switch Q39, Q40 | an engineer, on a bench (the body diode's VSD method) |
| TP-E11-30 | TP-E11-30.md | R-160 | D-14's docking pulse: the whole hot waveform in one body diode | an engineer, on a bench (a capacitor-discharge rig) |
| TP-E11-36 | TP-E11-36.md | R-182 | D-14's RDS(on) allowance at VGS -8.5 V and a 150 C junction | an engineer, on a bench (an oven to 150 C, a pulsed Kelvin reading) |
| TP-E11-37 | TP-E11-37.md | R-183 | BATDRV with the FET pair: the pair (S1) or one FET with a case heat path (S2) | an engineer, on a bench |
| TP-E11-31 | TP-E11-31.md | R-161 | U-04: source-only start and the held states on the BQ25730 | an engineer, on a bench |
| TP-E11-38 | TP-E11-38.md | R-184 | D-15: the eFuse U42 and the dock's VSYS branch through cases (a) to (h) | an engineer, on a bench |
| TP-E11-35 | TP-E11-35.md | R-179, R-188 | the mixer fans' start current and PWM level, and the firmware's stagger (E11-35, E11-39) | an engineer, on a bench |
| TP-SOLAR | TP-SOLAR.md | R-176, R-189, R-174 | D-10, D-11 and D-16: the solar input guard's thresholds and waveforms at U5's pins, and the sense in operation | an engineer, on a bench; CS116 and CS115 a MIL-STD-461 laboratory |
| TP-EPAPER | TP-EPAPER.md | R-185 | U-02's missing storage qualification of the e-paper (M6, M7) | an engineer with an oven, or a laboratory |
| TP-CELL | TP-CELL.md | R-168, R-169 | U-01's Saft route: the one-cell limited sample qualification | a laboratory |

**One warning carried by TP-SOLAR.** The drafted solar guard is known, on the desk model, to FAIL its own row at a fault at the
connector: U5's sense pins reach past their absolute maximum (handover row P1, task P1-1). TP-SOLAR therefore measures the
supplier's **corrected** network (the output of phase 1's task P1-1), and says how to treat the drafted one if it is ever
stepped.

**Rows of 5d's route table not written here**, each with its reason (machine-read by `tp_check.py`, which requires every 5d row
to be covered exactly once):

<!-- tp-index
external: TP-TH1 | v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md | R-104, R-151 | T-H1 (R-104, R-151; T-H1-PROCEDURE-DRAFT.md)
not-covered: The HL18650V lot soak (R-103, R-47; route (II) only) | the HL18650V route (II) is an alternative only; its soak is specified in 5d and L4-E10 15e and is not part of this set's request
not-covered: The fit mock-up (R-167) | a printed geometry check owned by Layer 7, no instrument and no pass line beyond the fit itself
not-covered: The documentary alternatives (the makers' statements) | not an experiment: the owner sends the drafted requests; a maker's printed limit closes a row for every lot
-->

- **TP-TH1** is the existing draft `v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md`; it is the model the others follow for depth.
- **The HL18650V lot soak** (route (II) only) is not written: it serves an alternative cell, not the selected route.
- **The fit mock-up** (R-167) is a print in the pocket, Layer 7's.
- **The documentary alternatives** are the makers' statements; a returned maker's limit closes its row for every lot and makes
  the matching procedure here unnecessary for that row.

## 2. How each procedure is laid out

Every TP file has the same eleven sections: (1) purpose and the decision it settles, with its register row; (2) the specimen and
what transfers, quoted from 5d and 17d; (3) safety; (4) equipment, with the accuracy each measurement needs and how that accuracy
follows from the pass limit and the uncertainty budget (an instrument class is named, never a brand); (5) setup and measurement
points; (6) the steps; (7) the data to record, as a table template; (8) pass, fail and inconclusive, quoted from the register or
the record; (9) the uncertainty budget's terms; (10) the consequence of a fail and the re-test triggers; (11) the authorisation
and purchases needed, quoted from 5d (nothing has been bought).

A metadata block at the top of each file (an HTML comment) names its id, title, register rows, L4-E11 rows and 5d route rows for
the checker. A quote sits between an opening HTML comment marker ("q", naming its source and, for a table cell, its row and column)
and a closing one ("/q"); the checker compares it with the source cell or text. A quote is the record's wording, including its own cross-references (section numbers such as "16b" or "17d"
are sections of the quoted record).

## 3. The verdict rule shared by every procedure

The records state the rule for a reading against a limit in two places:

<!-- q src="v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md" -->
> **Measurement uncertainty:** the K-factor within 2 %, the heating power within 1 %, the air within 1 K, stated as an expanded
> uncertainty on Zself + Zmut; a reading passes when it plus its uncertainty is under the limits of E11-29.
<!-- /q -->

<!-- q src="v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md" -->
> Per point: **pass** when the reading less its expanded uncertainty is at or over the line's need (the reading at or over the
> threshold below); **fail** when it is under; **inconclusive** when the endpoint is not met
<!-- /q -->

So, in every procedure here (the general form of those two sentences; nothing in it lowers a limit):

| Result | Against an upper limit L ("at most", "under") | Against a lower limit L ("at least", "over") |
|---|---|---|
| **PASS** | the reading plus its expanded uncertainty U is at or under L ("at most") or under L ("under") | the reading less U is at or over L ("at least") or over L ("over") |
| **FAIL** | otherwise, on a valid measurement. A reading that is itself inside L but whose band reaches past it does not pass: it is reported as FAIL, marked "within uncertainty", as T-H1 section 6 treats it; a repeat at a smaller U is a new run, and the first run stays in the record | the same |
| **INCONCLUSIVE** | a validity condition of the procedure is not met (the specimen differs from its block, the operating point is not held, an instrument is out of calibration or its uncertainty is not achieved, the endpoint is not reached); the run is repeated; an INCONCLUSIVE run is never a pass | the same |
| **RECORDED** | the record asks for a value and states no limit: the value and its U are filed and no verdict is given | the same |

- **U** is the expanded uncertainty at a coverage factor k = 2, as T-H1 uses it, combined from the standard uncertainties of the
  budget's terms by root-sum-square where they are independent (the method of the ISO Guide to the Expression of Uncertainty in
  Measurement, JCGM 100:2008; not held in this tree). Each procedure lists its terms in its section 9.
- **A planning target, this folder's proposal:** an instrument chain whose U is at most a quarter of the margin it judges (a
  test uncertainty ratio of 4:1, the usual calibration-laboratory practice). It is not a validity condition: a larger U only makes
  a PASS harder to reach. Where a record states an accuracy (the 17d blocks do), the record's figure governs.
- **Every instrument** carries a calibration traceable to national standards and inside its interval; its model class, serial
  number and calibration date are recorded with the run.

## 4. What a result is, and what it is not

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" -->
> **The rule.** An evidence build proceeds under its own scope; the design and production release stays held until the
> measurements pass; a row is not closed because it has an owner and a future test. A sample result is evidence for that lot and
> that sample, never a production limit; only a maker's printed limit closes a row for every lot. Purchases and outside contact
> are the owner's: nothing here is bought or sent.
<!-- /q -->

<!-- q src="v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md" -->
> So **a coupon's thermal result transfers only where the final board's thermal boundaries are shown no worse by a named rule, and
> a sample's pulse result is prototype evidence for that lot and those conditions, never a production limit or an extension of the
> maker's guarantee.**
<!-- /q -->

## 5. Authorisation, acceptance and the record to keep

- **Authorisation to perform** a procedure (the bench, the people, the spend on parts and fixtures) is the owner's, as each 5d
  row states in its Authorisation column. Nothing here has been bought, sent or run.
- **Acceptance of a result** goes through the coordinator's check of the filed record against the register row and the record
  the procedure quotes, as T-H1 section 0 sets out for its own points. The owner's authorisation does not accept a result, and a
  passing result authorises nothing further.
- **No limit is relaxed to make a run pass.** A run that fails is reported as failing, with the consequence its section 10
  quotes.
- **The record to keep**, for every run: the raw instrument files; the specimen's identity (part numbers, lots, reels, date
  codes, the coupon's fabricator, stack-up and copper weight); photographs of the specimen and of every measurement point; the
  instruments' classes, serial numbers and calibration dates; the ambient and chamber logs; the reduction (a script or a
  worksheet) and its output; the verdict per pass line with the reading, its U and the limit; who ran it, where and when, under
  which authorisation. The filled table templates of each procedure's section 7 are the summary, not a replacement for the raw
  files.

## 6. Safety that applies to every procedure

Each procedure's section 3 names its own hazards. Common to all: the laboratory's own electrical-safety rules and permits apply
and take precedence over anything here; supplies are current-limited to the run's need; a specimen is never left energised
unattended unless the procedure provides an automatic abort; chambers and ovens are used within their ratings, with burn
protection for parts handled hot; a lithium-ion cell or pack is handled under the laboratory's battery-safety rules (a fire-rated
enclosure, voltage and temperature monitoring with automatic cut-off, an exhaust for venting gases). No procedure here is to be
run on the owner's kit hardware or by the owner.

## 7. The checker

`tp_check.py` (run from the repository root: `python3 v2/docs/test-procedures/tp_check.py`) checks every procedure against its
sources and prints the index, the coverage of 5d's route table and every TBD by the row that owes it. Its output is committed as
`tp_check.out` and is regenerated only through the project's `regen_out.py`, which refuses a failed or non-deterministic run.
The test `v2/ecad/tools/tests/test_test_procedures.py` holds the same properties (every procedure names its register row and
the row exists; every pass condition is quoted from its source; every procedure carries the PROPOSED mark; no long dash) and
checks that the committed output is what the script prints. The quotes are checked against the records as they stand in this
tree: if a record's acceptance changes, the check fails and the procedure is re-read before its output is regenerated.
