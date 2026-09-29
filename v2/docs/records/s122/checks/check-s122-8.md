mergeable: yes

# AI review: delta check of stream s122, round 8, fnd/s122c at b1fb815f (S-122, CFL-016, MESHSAT-1357)

This is an AI review, not a qualified engineering review. Everything below is what I read or ran myself.

**Scope.** A delta check, by the coordinator's instruction: `git diff b76e5fd3..b1fb815f` only, against my check 7
(`checks/check-s122-7.md`). Blocking means one of: a closing line false against the netlist or a maker's page; a
closing figure with no binding, or a binding that does not state it; a change that breaks a replay or the integrator
sequence; a scope statement that claims more than the gate does.

**Set up**
* `fnd/s122c` is at `b1fb815f` (read with `git rev-parse`). The fix is `b53258bb`; `b1fb815f` adds the README and LOG.
* Check clone: a shared clone at `<scratch>/chk-s122-8`, detached at the tip, remote removed.
* Integration clone: a shared clone at `<scratch>/chk-s122-8-int`, on `fnd/int16`'s tip `36bb1d12`, remote removed
  before any commit, commits with the owner's `-c` flags, never pushed. int16's 945 ignored files under `v2/ecad` and
  `v2/vendor` (minus `__pycache__`) were copied in from its worktree.
* Both clones are removed when this report is written. No real branch was committed to or pushed.
* Time: 30 September 2026, 00:06 to 00:15 CEST (from `date`).
* S-122's scope is nine documents: PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md,
  pcb_decisions.yaml (decisions 28 and 40), EMCON.md (section 0a.1) and DEFINITION-STATUS.md (its section), extended at
  set 14 by check-int15-1's findings. Their verdicts are in `verdicts.out`.

**What I read**
* `git diff b76e5fd3..b1fb815f` of V2-SPEC.md, `apply_docs_s122_r8.py`, `apply_registry_s122_r4.py`, `close_s122.py`,
  `inventory.out`, `verdicts.out`, README.md and LOG.md.
* `checks/check-s122-7.md`: compared with `cmp`, byte identical to my CHECK-7.md.
* `verdicts.py`, `s122lib.py`, `judgements.py`, `inventory.py` and `test_close_s122.py` have no diff in this range.

## Blocking

None.

## Minor

**n1. README's file table still describes `apply_registry_s122_r4.py` as "the rebinds for rounds 4 to 7 (re-issued in
rounds 5 to 7 for their diffs)".** Round 8 re-issued it again (the finder's clause, `ESCAPES`, `REF` naming
`apply_docs_s122_r8.py`). One cell, wording only.

**n2. Check 7's m5 date remark: the form I ran.**
* The sentence was "On 20260929 it ran.", through `s122lib.partnos` with the six netlists' nets. At the tip it gives
  `20260929`, and so does `s122lib.names(...)["parts"]`.
* The path is `PN_MAKERNUM` (`\b([A-Z][a-z]{1,15}) (\d{7,})\b`): any capitalised word before seven or more digits,
  months excepted. `is_partno("20260929")` is False.
* The author's forms, "on 20260929 the" (lower case) and a bare "20260929", give no part number, as README says.
* It is a conservative false hit: a judgement would have to excuse it. It needs no entry in the escape list. No action.

## What holds

**1. Check 7's B1, the DS clause, is answered.**
* `S122_ADD4` now reads its escape classes from one constant, `ESCAPES`. Its finder clause says the finder reads "a DS
  code of four digits (Maxim's DS3231 shape) ... as part numbers, which a judgement must then excuse, and do[es] not
  read a DS code of five digits (Dallas's DS12887 shape, which the literature filter drops), 'SMBJ15A-based' or a plural
  'SMBJ15As', nor a maker's number after 'Lapp article'".
* Against the code (`s122lib.PN_LIT` holds `^DS\d{5}$`, applied in `is_partno` and in the maker rule), with
  `s122lib.partnos` and `s122lib.names`:
  * read as part numbers: "the DS3231 clock", "the DS1234 part", "the SMBJ15A/BAT54 clamp" (one token), "commit
    1C187977", "methods CE102 and RE102";
  * not read: "commit 1BAFAB8C" (so "some upper-case commits" is right).
  * no part number for DS12887 in any of five frames, with Maxim, Dallas, TI, Analog Devices or no maker's name.
  * not read: "an SMBJ15A-based clamp", "three SMBJ15As here" and "The Lapp article 0021917 cable.". The document's own
    form, "(article 0021917", is read.
* In the integration run, the S-122 title that the registry script wrote and the closure then kept contains the new
  clause. It contains neither "four or five digits" nor "DS12887 shapes among them".

**2. `ESCAPES`: one list for both texts, with check 7's m3 mutants.**
* `S122_ADD4` and `FOLLOW_TITLE` both concatenate `ESCAPES`. In the integration run, the whitespace-normalised
  `ESCAPES` stands whole in S-122's title and in S-135's title.
* The list carries both m3 mutants, and each is an escape at the tip, judged with its row's judgement:
  * "the PCM2912A USB codec and amplifier" reads TRUE (`role_phrases` gives only `USB codec`);
  * "the CSD18510Q5B VBUS20 switch" reads TRUE (no role phrase is formed).
* It also carries the check 7 m4 items (the load in other words, the one-word test's active-part limit and its
  load exception, which `check_roles` shows, and the list item) and the m5 items ("135-175 MHz" and "25 °C" give no
  figure token; the Lapp miss).
* These escapes also read TRUE with the scan passing, as listed: "the TPS22810 bias FET", "the TLV75801 gate-bias
  generator", the TUSB2046B hub "fitted since 26 September 2026 (`U4`", "on `PA_KEY` (`U17`" and "an NVMe 2280 socket".
* No entry claims the gate catches something it does not.
* Both titles passed the registry script's claim screen. Neither contains "MIL-STD".

**3. Check 7's m2.** The closed S-122's `closing_evidence` names `apply_docs_s122_r7.py`, `apply_docs_s122_r8.py` and
S-135. It also says each figure's unit is compared "where the source states one".

**4. Check 7's m1, `apply_docs_s122_r8.py`.**
* Refusals:
  * on the tip, it refuses (`2c722c9b`, not `4f1fd784`);
  * with `b76e5fd3`'s V2-SPEC.md, `--check` locates 1 edit;
  * pointing the CONOPS.md row of DEFINITION-STATUS.md's baselines table at V2-SPEC.md makes it refuse;
  * adding V2-SPEC.md to `s122lib.BASELINED` makes it refuse.
* Runs:
  * the real run writes a file identical to the tip, and a second run refuses;
  * from `1c187977`'s V2-SPEC.md, `apply_docs_s122_r7.py` then `apply_docs_s122_r8.py` also give the tip.
* The new wording holds. Correction 36 now says the closing check "compares a unit only where the source states one".
  That matches the scan: a unit changed where the source states one is refused (four plants below), and "330 x 200 cm"
  and "14.4 mV node" pass, because the board file and the rail intent state no unit.

**5. The outputs.**
* In `inventory.out` and `verdicts.out` only the header line moved, V2-SPEC.md's sha from `4f1fd784` to `2c722c9b`: 2
  lines removed, 2 added.
* Re-run at the tip, all nine outputs are byte identical to the committed files:
  * `inventory.out`, `verdicts.out`;
  * `-base` at `e57a7365`;
  * `-set14` at `1bafab8c`;
  * `verdicts-r4.out` at `edead832`;
  * `verdicts-r5.out` at `a6429e66`;
  * `verdicts-r6.out` at `1c187977`.

**6. `test_close_s122.py` at the tip: ALL PASS.** T4 refuses 45 of 45 changes. T5 lets 45 of 45 through and the gate
refuses.

**7. The set 15 order**, on the integration clone.
* **Review D first**, merging `4795d5bf`:
  * one conflict, `v2/vendor/sources.txt`, resolved by keeping both sides (int16's two passives lines, then review D's
    Arlitech line);
  * `facts.py`: 55 facts, 0 FAIL;
  * `test_refusals.py`: 17 cases, 0 FAIL;
  * `apply_findings.py --check`: RD-C-01 extends S-101; RD-C-02 to RD-C-09 and RD-C-24 open S-126 to S-134;
  * `apply_findings.py` wrote, and a second run refused;
  * `rules_lib.py requirements`: 0 errors, 0 warnings. The trace page was rendered and committed.
* **Then `b1fb815f`**, merged with no conflict.
  * **Registry script.** `apply_registry_s122_r4.py`:
    * rebound 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005);
    * opened **S-135** (SESSION, OPEN, PROCESS, in no record's `waits_on`);
    * re-pinned the envelope and ENV-001;
    * a second run refused.
  * **What moved.** Only those five records, S-122 and S-135 moved. Review D's `waits_on` on CON-009, REQ-007, REQ-008,
    REQ-012, REQ-035, REQ-052 and REQ-060 stand.
  * **Renders and status.**
    * `rules_lib.py requirements` read 0 errors, and the trace page rendered.
    * `rules_status.py` three times: exit 1 each, NOT_READY, 195 PASS, 39 FAIL, 104 INCONCLUSIVE of 338. The three
      outputs are identical.
    * The full render moved CURRENT-EVIDENCE.md to `0f2c59cb`. `rules_lib.py requirements` then read 0 errors and 2
      warnings, CON-010 and REQ-044, as README's order says.
  * **Outputs.** `inventory.py` and `verdicts.py` read 1011 sentences, 0 STALE, 0 UNJUDGED. Only the header moved, with
    `pcb_decisions.yaml` going from `a41df5d1` to `823a6b32`. Committed.
  * **Fixture check.** Refused while only staged, then committed.
  * **Closure.** `test_close_s122.py`: ALL PASS. `close_s122.py` closed S-122 with CFL-016 PASS. A second run refused
    ("S-122 is not open"). S-42, S-123 to S-126, S-134 and S-135 stay open.
  * **After it.** `rules_lib.py requirements`: 0 errors, 2 warnings (CON-010, REQ-044). `rules_lib.py`: 59 rules, 0
    errors. `tests/run.py test_requirements test_envelope_data`: 72 passed, 0 failed, 0 skipped, after the trace page's
    render. `claims_check.py`: PASS, 91 of 91.
* **This report as the filed check.** I also ran the closure a second time on the same clone, reset to the commit
  before the fixture, with this report filed at `checks/check-s122-8.md` and committed. The result is in the last line
  of this report.

**8. Text rules.**
* 482 added lines in the range: no U+2013, no U+2014, no internal host name, user path or address.
* CONOPS.md and PRODUCT-BRIEF.md have no diff in the range.

## S-122 closing check

These eight lines have the same text at `b1fb815f` as at `b76e5fd3`: I compared each line's hash for V2-SPEC.md
47, 81, 82, 83, 84 and 86, and OPERATING-ENVELOPE.md has no diff in the range. V2-SPEC.md's only change is correction
36, at line 324. The judgements and the tools that bind them have no diff either. So check 7's line by line reading
carries forward. I also re-ran at the tip the script that finds each figure token on these lines, the key that spans it
and its bound assertion: 45 tokens, each covered by a key whose assertion runs TRUE and matches in order, sign and
unit. My eight wrong-figure plants were refused again.

* **V2-SPEC.md line 47.** The exciter is board D's `U2`, whose value is the NiceRF SA868 VHF 2 W exciter, so "2 W" is
  the board's own rating. "30 W" is the RA30H1317M1's rating in its maker's page heading, "135-175MHz 30W 12.5V". The
  codec is D `U6`, the PCM2912A.
* **V2-SPEC.md line 81.** Board A's file:
  * 240 x 160 mm, six layers.
  * 14.4 V is the cell node CELL4 that `gen_sch_p.py` declares. Beside it: the 4S block of `J_CELL`, the INR18650-35E
    block, and the 35E sheet's 3.60 V nominal.
  * 9 to 36 V is board E's `J_DCIN`.
  * The three 5.1 V slot rails are `J_5V_S1` to `J_5V_S3`.
  * The four AP64500 of 7 September are the four rail groups of `gen_sch_a.py` at `b2709118`.
  * 13.8, 12 and 54 V are the output nets named in `U13`, `U15` and `U16`.
  * 45 W is `U18`'s outlet; 3.3 V is `U12`'s logic rail.
  * Eleven SMP-MAX sites are eleven Radiall footprints; 2x13 is `J_AB1`'s IDC header.
* **V2-SPEC.md line 82.** Board B's file: 330 x 200 mm, six layers, In4 zones on the +5V nets. Decision 43's outcome
  names eight layers. The netlist counts three CM5 receptacles, three STM32H743, two CAN-FD fabrics in `U41`'s value,
  seven voters (one `_CA` net each), two TS3DV642 and two E72.
* **V2-SPEC.md line 83.** Board C's file: a 344 x 228 outline with a 240 x 176 inner cutout, four layers. Decision 27
  rules six. The netlist has seventeen 3 mm LEDs (D1 to D16 and D22) and two PCA9555.
* **V2-SPEC.md line 84.** Board D's file: 100 x 80 mm, four layers, two headset jacks (`J_HS1`, `J_HS2`). The roles
  stand against the netlist: `U6` codec, `U7` amplifier, `U15` the TLV75801 on `PA_KEY`, `U21` the TPS22810 on
  `+5V_TX`.
* **V2-SPEC.md line 86.** Board E's file: 267 x 68 mm, four layers. 9 to 36 V is `J_DCIN`; the 25 A fuse is `F3`. There
  are eleven named float-clamp keep-outs and two fan headers (`J_FAN1`, `J_FAN2`).
* **OPERATING-ENVELOPE.md line 77.** The 9 to 36 V input is `J_DCIN`. "-40 to +125 C" is the LM5069 sheet's section
  7.3 junction row, with its minus sign, under recommended operating conditions as the row says.
* **OPERATING-ENVELOPE.md line 83.** "-40 to +80 C" is TE's service temperature for the 2199119 socket, board B's
  `J_M2C2`.

## Counts

Committed `verdicts.out` at `b1fb815f`, reproduced byte for byte:

| Document | Sentences | TRUE | STALE | BASELINE | NOT DERIVABLE | UNJUDGED | Assertions |
|---|---|---|---|---|---|---|---|
| PANEL.md | 167 | 131 | 0 | 0 | 36 | 0 | 787 |
| CONOPS.md | 288 | 51 | 0 | 40 | 197 | 0 | 784 |
| V2-SPEC.md | 159 | 64 | 0 | 0 | 95 | 0 | 486 |
| OPERATING-ENVELOPE.md | 67 | 22 | 0 | 0 | 45 | 0 | 165 |
| TEST-PLAN.md | 110 | 18 | 0 | 0 | 92 | 0 | 128 |
| ASSEMBLY.md | 160 | 91 | 0 | 0 | 69 | 0 | 242 |
| pcb_decisions.yaml | 10 | 6 | 0 | 0 | 4 | 0 | 17 |
| EMCON.md | 26 | 22 | 0 | 0 | 4 | 0 | 455 |
| DEFINITION-STATUS.md | 24 | 17 | 0 | 0 | 7 | 0 | 276 |
| **Total** | **1011** | **422** | **0** | **40** | **549** | **0** | **3340** |

This round's findings: 0 blocking, 2 minor (n1 a README cell; n2 the date remark's form, no action).

Result of the last item of section 7: with this report filed as `checks/check-s122-8.md` and committed (its text up to the line above), `close_s122.py` closed S-122 with CFL-016 PASS, and a second run refused; `rules_lib.py requirements` then read 0 errors.
