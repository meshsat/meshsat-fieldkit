# Stream s122: the documents CFL-016 names, re-read against the netlists (S-122, MESHSAT-1357)

Prototype design: nothing here is built, bought or measured. Branch `fnd/s122b` from `main` at `b874b744` (set 13 promoted as `32f26b41`, its
milestone `b874b744`), carrying this stream's seven commits of `fnd/s122` by cherry-pick, 29 September 2026. The stream changes documents only; no
generator, netlist or registry file is edited on this branch (the registry changes are `apply_registry_s122.py` and
`close_s122.py`, for the integrator).

Round 1 corrected 43 passages. The independent check of round 1 (`checks/check-s122-1.md`, filed byte for byte from the
checker's `<scratch>/chk-s122/CHECK.md`) read all 43 true and found 3 blocking and 12 minor items. Round 2 answers them under the coordinator's ruling on CONOPS.md's
baseline. Every statement below about what was read is what one of these scripts read, or a filed check's own words
quoted with its file.

## The baseline rule, and what it changed

`CONOPS.md` is a BASELINED layer 2 definition. Its head, and `handover/DEFINITION-STATUS.md`, say that a changed count or
a circuit correction updates the status page and the records it names, not the baseline. Set 12's two circuit commits
(`a46db71b`, `7a9f7b5b`) and round 1 of this stream edited CONOPS against that rule. So round 2:

* **restores `CONOPS.md` to its text at `c5430071`** (the owner's rulings of 28 September, the last change the rule
  allows). `apply_docs_s122_r2.py` asserts the restored file equals `git show c5430071:v2/docs/CONOPS.md` byte for byte
  (sha256/16 `6cb7b241cb84d729`) and that the needs table is unchanged;
* **keeps the current circuit where the rule's own dependency list says**:
  * `feasibility/EMCON.md` gains **section 0a.1**: CONOPS 4b's table and the EMCON row's cells as `7a9f7b5b` wrote them
    (the text of `records/int13/apply_conops_4b_set12.py`, which the script checks is what `7a9f7b5b` committed),
    re-asserted on set 13's netlists;
  * `handover/DEFINITION-STATUS.md` gains the section "Current values of CONOPS's circuit passages (stream s122,
    29 September 2026)" and a row in its dependency table. It states that CONOPS's circuit passages and their "as
    generated" remarks are baseline values, and names where each current value is kept: DC-01 EMCON (EMCON.md 0a.1),
    DC-02 HOT-R1 (board E `Q11`, `HOT_R1_G` on `U10` pin 30, `R58`, `BLK_SPARE` at `J_BLK` pin 12; board A `J_DOCK`
    pin 12, `R216`, `U27` pin 18; REQ-077 INCONCLUSIVE, waiting on S-58), DC-03 the TX lamp (it needs the panel
    controller: `D3` from `LED_RAIL`, `Q1`'s drain, which only `Q2` turns on from `PANEL_PWM`), DC-04 the device rails
    (`U7` on A, `U25` on B), DC-05 a loss of `+3V3_DEV`, DC-06 generator line numbers.
* **reads CONOPS through the status page**: a CONOPS sentence whose value differs from the netlists, or that cites a
  generator line, is **BASELINE** when a DC row keeps its current value, and **STALE** when none does. The status
  page's section and EMCON.md 0a.1 are judged directly.

## Files

| File | What it is |
|---|---|
| `s122lib.py` | the parser, the name finder and `SCOPE`; reads the six netlists with `tx_inhibit.parse_netlist`; `S122_AT=<commit>` reads the documents (not the netlists) at a commit |
| `inventory.py` | writes `inventory.out` |
| `judgements.py` | the stream's judgement of each sentence, keyed by its digest, with its assertions |
| `verdicts.py` | looks up every named part, reads every cited generator line, evaluates every assertion and every stated count of parts, applies the baseline rule, writes `verdicts.out` |
| `inventory-base.out`, `verdicts-base.out` | the base's documents at `e57a7365` (run with `S122_AT=e57a7365`), judged on set 13's netlists |
| `inventory.out`, `verdicts.out` | the documents as they stand: 849 sentences, 0 STALE, 0 UNJUDGED |
| `apply_docs_s122.py` | round 1's 43 passages (committed in `cb446b03`; refuses a second run) |
| `apply_docs_s122_r2.py` | round 2: the CONOPS restore, EMCON.md 0a.1, the status page's section, 16 passages; 495 assertions held first (committed in `c263ddce`) |
| `apply_registry_s122.py` | for the integrator: rebinds, CFL-016's three entries, S-122's title correction, the envelope re-pin |
| `close_s122.py` | S-122's closure, for the integrator, last |
| `LOG.md` | the stream's log |

## Scope (`s122lib.SCOPE`) and the finder

PANEL.md sections 1, 2, 3, 5, 6, 7, 9 and 10; CONOPS.md sections 2a, M2, M4, **4 with 4a to 4f** (round 2: every row of
section 4, and 4c and 4d, which the check showed are subsections of section 4), and 5; V2-SPEC.md and TEST-PLAN.md
whole; OPERATING-ENVELOPE.md sections 2 to 4; ASSEMBLY.md **sections 2** (every step since round 2), 4, 8 and 9;
decisions 28 and 40; EMCON.md section 0a.1 and the status page's new section. Not read: PANEL.md's head and sections
4, 8 and 11; CONOPS.md's other sections; OPERATING-ENVELOPE.md sections 1 and 5 to 8; ASSEMBLY.md's other sections.

A sentence is inventoried when it names a part designator, a net, a board, a rail, a gate function, a generator line,
**EMCON**, or a **spelled count of parts** (round 2). Round 2's count rule: a sentence that states a count of parts
(two to twenty LEDs, pins, sockets, cards and the like) is UNJUDGED until its judgement asserts the count on a netlist
(by footprint, value or designator) or says why the count is not a netlist's.

## What the verdicts mean

* **TRUE**: judged true on reading, and every check `verdicts.py` runs holds (every named part is on a netlisted board,
  every cited generator line holds a named part at the commit it is dated to, every assertion and every stated count).
  What a TRUE sentence says beyond the netlists is named in its judgement and not judged.
* **STALE**: the netlists or generators no longer carry it.
* **BASELINE**: a CONOPS passage whose value is the baseline's, its current value kept in a DC row of the status page.
* **NOT DERIVABLE**: HISTORY (a dated record), FIRMWARE, HELD DOCUMENT, TEST, CASE or LEAD; left as it stands.
* **UNJUDGED**: no judgement, or a count not asserted; the closure refuses on any.

## Counts per document

| Document | Base (`e57a7365` on set 13): sentences | STALE | After: sentences | TRUE | STALE | BASELINE | NOT DERIVABLE |
|---|---|---|---|---|---|---|---|
| PANEL.md | 158 | 10 | 161 | 126 | 0 | 0 | 35 |
| CONOPS.md | 249 | 25 | 247 | 27 | 0 | 34 | 186 |
| V2-SPEC.md | 111 | 6 | 119 | 34 | 0 | 0 | 85 |
| OPERATING-ENVELOPE.md | 32 | 4 | 32 | 8 | 0 | 0 | 24 |
| TEST-PLAN.md | 99 | 2 | 99 | 17 | 0 | 0 | 82 |
| ASSEMBLY.md | 147 | 13 | 147 | 85 | 0 | 0 | 62 |
| decisions 28 and 40 | 9 | 0 | 9 | 6 | 0 | 0 | 3 |
| EMCON.md 0a.1 | 0 | 0 | 21 | 17 | 0 | 0 | 4 |
| DEFINITION-STATUS.md (the new section) | 0 | 0 | 14 | 7 | 0 | 0 | 7 |
| total | 805 | 60 | 849 | 327 | 0 | 34 | 488 |

2431 assertions are evaluated after (1937 at the base). The 34 BASELINE sentences of CONOPS point to DC-01 (11), DC-02
(6), DC-03 (1), DC-04 (1), DC-05 (1) and DC-06 (14).

## The check's items (check-s122-1)

| Item | Answer |
|---|---|
| B1 (CONOPS section 4 and 4c say HOT-R1 is owed, 4f says drawn) | the baseline rule: 4f's round 1 edit withdrawn with the restore; lines 311, 312, 4c's HOT-R1 passages and 4f are BASELINE on DC-02, which carries HOT-R1 as drawn and REQ-077's reading, asserted on the netlists and the registry |
| B2 (ASSEMBLY section 9's counts) | lines 87, 217, 218 and 219 corrected with count assertions (17 Mill-Max 0858 pins by footprint, two E-key card sockets, 17 LEDs on `LED_D3.0mm`); the count rule stops a count from passing unasserted again |
| B3 (CONOPS 4e: the TX lamp acts without the controller) | its TRUE withdrawn; BASELINE on DC-03, which states the lamp needs the controller, asserted on board C (`R36`, `Q1`, `R17`, `Q2`, `R19`, `R20`) |
| m1 (4b's preamble overstates the script) | the preamble is withdrawn with the restore; EMCON.md 0a.1 says what `apply_docs_s122_r2.py` asserted, and its list covers `U214`/`U314`'s inputs, `U547` to `U550`'s inputs, `U540` to `U542`'s inputs and supply, and the QMX's USB supply (`F3` from `+5V_DEV`) |
| m2 (OPERATING-ENVELOPE.md dropped the PA bias) | restored: "a hardware line on every transmitter and on the PA's rail and bias", with board D's `U15` on `PA_KEY` asserted |
| m3 (CONOPS 4e header) | withdrawn with the restore |
| m4 (ASSEMBLY line 204's short citation) | dated at `e57a7365` |
| m5 (ASSEMBLY line 180 omits `J_VN1` to `J_VN4`) | added |
| m6 (PANEL line 156's "SPI lines") | "TXEN, RXEN, NRST, MOSI, SCK and NSS", MISO through `U553` |
| m7 (V2-SPEC lines 81 and 82 judged HISTORY) | judged STALE at the base and corrected (the TPS55288 had left before 7 September, `gen_sch_a.py:267` at `c5de605d`; the supervisors read H743 and CON-017 reads PASS); round 2 also found line 30's "five-port" switch chip (the KSZ9897R is seven-port) |
| m8 (correction 32 under the 27 September heading) | under its own "Corrections, 29 September 2026"; line 3 names it |
| m9 (rebind reasons not record specific) | each entry now names which parts and nets of the changed sentences the record's own text names |
| m10 (a staged check closes S-122) | the closure compares the check with HEAD's blob; the replay refused a staged fixture |
| m11 (the closure's 605 are SCOPE's) | the closure's entries say "in the scope s122lib.SCOPE sets" and name what is outside it |
| m12 (the finder leaves in-scope sentences out) | EMCON and counts of parts added; the sentence CFL-016 names in TEST-PLAN.md (line 54) is inventoried now. Not added: transmitter, radio, lamp and supply as keywords; the check says of the 155 sentences with those words that it "found no further stale statement" |

## Set 13 (main `32f26b41`, milestone `b874b744`)

Board C's netlist is `c9f7394594201045`: `R53` to `R56` (27R) put `U3`'s GPIO 2 to 5 on `EPD_SCL_R`, `EPD_SDA_R`,
`EPD_DC_R` and `EPD_CS_R`. PANEL.md section 3's two rows are corrected, and line 180's provenance names set 13's
netlists. The promoted registry carries S-122's set 13 addition, with its closing clause (the rows re-derived like the EMCON
statements), and S-123.

## The scripts for the integrator, and what they assert

* `apply_registry_s122.py`:
  * rebinds the 20 records bound to the seven changed documents (PANEL.md, CONOPS.md, V2-SPEC.md,
    OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, EMCON.md), CONOPS.md to `c5430071`'s `6cb7b241cb84d729`;
  * gives each rebind a reason read from the diff, from the sentence sets and the two verdict files, and from the
    record's own text;
  * moves the needs pin to `c5430071`'s full sha after asserting the diff starts after the needs table;
  * appends three CFL-016 entries: the inventory, the baseline rule, and check-int13-4's n1 and n2;
  * appends n3 and n4 to S-122's title;
  * re-pins the envelope and ENV-001 after asserting no envelope number left OPERATING-ENVELOPE.md;
  * asserts every other record and item unchanged, re-parses, and refuses a second run.
* `close_s122.py <check>`:
  * checks the rebinds are in and current;
  * re-runs the inventory and verdicts, and needs 0 STALE and 0 UNJUDGED, identical to the committed outputs;
  * needs CFL-016's baseline entry, the status page's rows, and sentences judged in EMCON.md and DEFINITION-STATUS.md;
  * needs the check committed at HEAD, starting `mergeable: yes`, and naming every document and `verdicts.out`;
  * then closes S-122 and sets CFL-016 to PASS.
* **Replayed on a scratch clone of `53292087`:**
  * the four outputs reproduce byte for byte;
  * `apply_docs_s122_r2.py` refuses a second run;
  * the registry script rebinds 20 records and refuses a second run;
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors;
  * `test_envelope_data`: 6 passed. `test_requirements`: 63 passed and 2 failed before `rules_render.py --requirements`, 65 passed after;
  * the closure refused a staged fixture and a fixture naming neither EMCON.md nor DEFINITION-STATUS.md, closed with a
    committed fixture (not filed), and refused a second run;
  * after it, `rules_lib.py requirements`: 0 errors. `test_requirements` with `test_envelope_data`: 71 passed. `claims_check`: PASS, 91 of 91.

## Integrator's run order

1. Merge `fnd/s122b` (from main `b874b744`).
2. `python3 v2/docs/records/s122/apply_registry_s122.py`
3. `rules_render.py --requirements`; `rules_status.py` and `rules_render.py` for the envelope pin (ENV-001's `verified_sha`, the PCB-RULE-STATUS pages, LAYER-STATUS).
4. An independent check filed under `v2/docs/records/s122/checks/` and committed. It must name PANEL.md, CONOPS.md,
   V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, pcb_decisions.yaml, EMCON.md, DEFINITION-STATUS.md and
   `verdicts.out`, in its own words.
5. `python3 v2/docs/records/s122/close_s122.py v2/docs/records/s122/checks/<the check>`
6. `rules_render.py --requirements` again.

If a document of the scope changes on main before step 5, re-run `inventory.py` and `verdicts.py`, judge the new text
in `judgements.py`, and commit the outputs, or the closure refuses.

## What stays open

* S-122 and CFL-016, until the check of step 4 and the closure of step 5.
* CONOPS.md's 34 BASELINE passages stay as baselined. Their current values live on the status page until a reopening of
  the definition decides otherwise. `feasibility/ZEROIZE.md`'s citation `CONOPS.md:404` (the check's observation) is
  outside the scope.
* The finder is a token finder. A circuit sentence that names none of its tokens is outside the inventory; V2-SPEC.md
  line 35 was found that way in round 1.
