#!/usr/bin/env python3
"""apply_l4small_revx.py: register task L4A-60 (RE-8, the remaining-engineering ledger's cx46 item 8) on record l9t5's own files
(MESHSAT-1357, worker W133, branch fnd/l4small, 7 October 2026). UNAPPLIED on its branch: the set 33 integrator runs it on the
integrated tree (set 32, fnd/int32, changes T10-ROUND5.md and l9t5_t10.py), then regenerates l9t5_t10.out and its dependants.

WHAT IT DOES: it records SESSION decision L9T5-D11 (revision X is NOT ADMITTED: the supervisors are silicon revision V only, a part
or lot of any other revision is refused, and the rev X qualification is an UNSELECTED OPTION outside the scope) as section W133 of
T10-ROUND5.md, and restates every current instruction of the record that still named an admission route for revision X: each by
INSERTION, the earlier words kept as labelled history (record l9t5's rule since W9: no base text removed, no line moved), except the
contract draft's FW-B20 row, which is a text to be applied to HW-FW-CONTRACT.md and so states only the current instruction.
  T10-ROUND5.md       line 1, sections 3 (1), 3 (5), 3 (6) (the Layer 12 row), 5, 6 (row 1), 8 (L9T5-D7's reversal), 10 (L9T5-F23),
                      12 (f), and section W133 appended
  L9T5-CASES.md       the two lines that named the V-B20 route
  l9t5_t10.py         10a, 10h (1), 10i, 10j (f), the 10j disposition, L9T5-F22 and the round 5 predicate's words (same printed lines)
  l9t5_connected.py   section 10's three revision X lines (same printed lines)
  apply_hw_fw_contract_t10.py  FW-B20's row and the docstring
No figure, net, part, verdict or state changes; no cx46 item closes. Nothing in this kit has been built, bought, powered or measured.
Engine and its checks E1 to E6: v2/docs/records/l4small/l4small_edit.py.
Usage:  apply_l4small_revx.py [ROOT] [--check | --write]   (default ROOT: this tree; default --check: nothing is written)
Exit 0: checked or written; 2: usage; 3: refused (already applied, an anchor missing or not unique, or the result does not parse)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l4small"))
import l4small_edit as E  # noqa: E402

NAME = "apply_l4small_revx"
R5 = "v2/docs/records/l9t5/T10-ROUND5.md"
CASES = "v2/docs/records/l9t5/L9T5-CASES.md"
T10 = "v2/docs/records/l9t5/l9t5_t10.py"
CON = "v2/docs/records/l9t5/l9t5_connected.py"
CTR = "v2/docs/records/l9t5/apply_hw_fw_contract_t10.py"
D = "SESSION L9T5-D11"
NA = "revision X NOT ADMITTED"

EDITS = [
    # ------------------------------------------------------------------------------------------------ T10-ROUND5.md (insertions)
    (R5, "revision X held with no admission route. What stays:",
         "revision X held with no admission route [%s since 7 October 2026, %s, section W133]. What stays:" % (NA, D), True),
    (R5, "a rev X part's qualification is\nREMAINING ENGINEERING (section 12).",
         "a rev X part's qualification is\nREMAINING ENGINEERING (section 12) [superseded 7 October 2026 by %s, section W133: %s; its "
         "qualification an UNSELECTED OPTION outside the scope, not remaining engineering]." % (D, NA), True),
    (R5, "(125.9 C): a rev X part still waits on V-B20. The service",
         "(125.9 C): a rev X part still waits on V-B20 [as written at round 5; superseded by %s, 7 October 2026: %s, no V-B20 "
         "reading admits it]. The service" % (D, NA), True),
    (R5, "a lot with any other code held;",
         "a lot with any other code held [and refused: %s, %s];" % (NA, D), True),
    (R5, "- **Revision X: HELD** (not fitted, round 6) until its own qualification:",
         "- **Revision X: HELD** [NOT ADMITTED since 7 October 2026, %s, section W133; the rest of this item is round 6's text, kept as "
         "history: the qualification it names is an UNSELECTED OPTION] (not fitted, round 6) until its own qualification:" % D, True),
    (R5, "fit rev V (L9T5-D7); revision X HELD | three rev X STM32H743VIT6 on the first-article board B:",
         "fit rev V (L9T5-D7); revision X HELD [NOT ADMITTED, %s] | [no supplier task since 7 October 2026, %s: the rev X "
         "qualification is an UNSELECTED OPTION; round 5's text kept as history:] three rev X STM32H743VIT6 on the first-article board B:"
         % (D, D), True),
    (R5, "| a rev X part only after its own qualification (V-B20 at most 0.2183 A) |",
         "| a rev X part only after its own qualification (V-B20 at most 0.2183 A) [and only after %s is reversed, section W133] |" % D,
         True),
    (R5, "its qualification is REMAINING ENGINEERING. No purchase",
         "its qualification is REMAINING ENGINEERING [superseded 7 October 2026 by %s, section W133: %s, a lot of it refused at "
         "goods-in; its qualification an UNSELECTED OPTION, not remaining engineering]. No purchase" % (D, NA), True),
    (R5, "| a rev X part's qualification, resting on (e) |",
         "| a rev X part's qualification, resting on (e) [an UNSELECTED OPTION since 7 October 2026, %s, section W133: not a task] |" % D,
         True),
    # ------------------------------------------------------------------------------------------------ L9T5-CASES.md (insertions)
    (CASES, "L9T5-F22's shortcut SUPERSEDED), R602 14.0 k",
            "L9T5-F22's shortcut SUPERSEDED; since 7 October 2026 %s, %s, `T10-ROUND5.md` section W133), R602 14.0 k" % (NA, D), True),
    (CASES, "and a rev X part waits on V-B20, unless the set point moves (L9T5-F22, R602 14.0 k, Slot A's draft).",
            "and a rev X part waits on V-B20, unless the set point moves (L9T5-F22, R602 14.0 k, Slot A's draft) [as written at round 5; "
            "both routes superseded: %s since 7 October 2026, %s]." % (NA, D), True),
    # ------------------------------------------------------------------------------------------- l9t5_t10.py (insertions in literals)
    (T10, "the revision whose printed rows hold; a rev X part is\")",
          "the revision whose printed rows hold; [SUPERSEDED 7 October 2026 by %s: %s; round 5's words kept as history:] "
          "a rev X part is\")" % (D, NA), True),
    (T10, "settled at assembly: the fitted part is V or X. DS12110",
          "settled at assembly: the fitted part is V or X [CON-017 (5)'s bound; the fitted part is revision V only, %s, 7 October "
          "2026]. DS12110" % D, True),
    (T10, "admitted only by V-B20 (10h (1)); the proof above",
          "admitted only by V-B20 (10h (1)) [as written at round 5; SUPERSEDED by %s: %s]; the proof above" % (D, NA), True),
    (T10, "thermal acceptance it would rest on are REMAINING ENGINEERING ((e)); the rail trip's least",
          "thermal acceptance it would rest on are REMAINING ENGINEERING ((e)) [the rev X part's admission and qualification: an "
          "UNSELECTED OPTION since 7 October 2026, %s, not remaining engineering]; the rail trip's least" % D, True),
    (T10, "a rev X part's qualification; VOS0 under the trip\")",
          "a rev X part's qualification [an UNSELECTED OPTION since 7 October 2026, %s]; VOS0 under the trip\")" % D, True),
    (T10, "revision X stays HELD until its own qualification (10j (f))\")",
          "revision X stays HELD until its own qualification (10j (f)) [superseded 7 October 2026 by %s: NOT ADMITTED; its "
          "qualification an UNSELECTED OPTION]\")" % D, True),
    (T10, "do not hold 125 C at that corner (a rev X part waits on V-B20)\"]",
          "do not hold 125 C at that corner (a rev X part waits on V-B20 [as at round 5; %s: NOT ADMITTED])\"]" % D, True),
    # ------------------------------------------------------------------------------------- l9t5_connected.py (insertions in literals)
    (CON, "in its bounded state (V-B20, 10j (f)), and a draw over\"",
          "in its bounded state (V-B20, 10j (f)) [%s since 7 October 2026, %s], and a draw over\"" % (NA, D), True),
    (CON, "current, so revision X stays HELD on V-B20 (Slot C, 10j (f));\")",
          "current, so revision X stays HELD on V-B20 (Slot C, 10j (f)) [superseded: NOT ADMITTED, %s];\")" % D, True),
    (CON, "(its bounded state over the trip's least; HELD on V-B20); the LDO input headroom",
          "(its bounded state over the trip's least; HELD on V-B20 [superseded: NOT ADMITTED, %s]); the LDO input headroom" % D, True),
    # ------------------------------------------------------------------------- apply_hw_fw_contract_t10.py (the contract's FW-B20)
    (CTR, "FW-B20 restated on revision V only (rev X held until its qualification) and the 14.0 k set",
          "FW-B20 restated on revision V only (rev X held until its qualification; since 7 October 2026 NOT ADMITTED, %s) and the "
          "14.0 k set" % D, True),
    (CTR, "L9T5-D7: revision X \"\n          \"held until its own qualification, V-B20), each on",
          "L9T5-D7: revision X \"\n          \"NOT ADMITTED, record l9t5 %s), each on" % D, False),
]

APPENDS = [(R5, """
## W133 (7 October 2026): SESSION decision L9T5-D11, revision X not admitted

Register task L4A-60 (RE-8, cx46's item 8), worker W133 on branch `fnd/l4small`; adopted in the NEXT set (set 33) through
`apply_l4small_revx.py`. Record text and one SESSION decision with its reversal: no circuit, figure, verdict or state of a cx46 item
changes, and nothing is accepted, closed or released. Nothing in this kit has been built, bought, powered or measured.

| Field | L9T5-D11 |
|---|---|
| decision | Revision X is NOT ADMITTED. The three supervisors U41, U51 and U61 are STM32H743VIT6 of silicon revision V only (package marking revision code "V", DBGMCU_IDC REV_ID 0x2003, ES0392 Rev 15 Table 2). A part or lot of any other revision, X included, is refused at goods-in, not held for a later admission. The rev X qualification (V-B20 on a rev X part read against the selected regulator stage's window, record l9t5 `l9t5_t10.out` 11a (g), round 6's rail trip and its least 0.2183 A being removed by regstage, W138-2; its rows re-solved on RE-7's bound) is an UNSELECTED OPTION outside the scope, as route B2 is: no supplier task, no remaining-engineering item and no admission route rests on it. |
| authority | SESSION |
| authority_why | It changes no line a class of `v2/ecad/tools/reserved.json` protects (no part, net, value, land or order code changes: STM32H743VIT6, LCSC C114409, and L9T5-D7 already fits revision V); it spends nothing (no purchase and no distributor query; the lot availability of revision V against X is not read); it changes no claim about the kit (CON-017 (5), the erratum's bound V or X, stands as the requirement and the selection narrows inside it); and it accepts no residual risk a measurement could remove, because it removes the revision whose only cover rows fail. After the measurement one option stands: rev Y's rows, the only printed cover for a rev X part, miss 125 C at the drop's worst corner (125.2 C in the bounded state, section 3 (1)), and the method that would admit revision X (the register's RE-8 M-B, its qualification on RE-7's bound) rests on a bound RE-7 has not produced. |
| ruled_by | SESSION (W133, Claude) under the owner's ruling of 21 September 2026 and his standing rule of 26 September 2026 |
| ruled_on | 2026-10-07 |
| reversed_by | a ruling that takes up the register's RE-8 M-B: three rev X parts' V-B20 read on the selected stage (each supply current under the TPS2553-1's least with the served window of record l9t5 `l9t5_t10.out` 11a (g) kept positive; the rail trip is removed by regstage, W138-2, W159 on W157-F5) and their rows re-solved on RE-7's restated bound (11a (d)), then every row listed below restated to admit revision X; or an owner item if revision V's supply becomes a money or procurement question (M-A's end condition in the register) |

Rows restated, each by insertion with the earlier words kept as labelled history: on this page line 1, sections 3 (1), 3 (5), 3 (6)
(the Layer 12 row), 5, 6 (the first row), 8 (L9T5-D7's reversal), 10 (L9T5-F23) and 12 (f); `L9T5-CASES.md` (two lines);
`l9t5_t10.py` (10a, 10h (1), 10i, 10j (f), the disposition, L9T5-F22 and one predicate's words; the same printed lines);
`l9t5_connected.py` (three lines of section 10); `apply_hw_fw_contract_t10.py` (FW-B20's row now reads "revision X NOT ADMITTED",
and the docstring). Layer 6's rows, by `apply_l4small_layer6.py`: `v2/docs/parts/STM32H743-COMPATIBILITY.md` (F1, the five matrix rows
on the erratum's revisions, HC6-SC-1) and `v2/docs/parts/PROCUREMENT.md` (U41, U51, U61), with CON-017's pin of the page rebound.
The ledger's RE-8 and L4-E9's copy of its row: `records/l4close/apply_l4small_ledger.py`. Not restated, with the reason: CON-017 (5)
and its trace and Layer 3 copies (the requirement's bound, which revision V meets; narrowing it would be a registry amendment the
selection does not need), and the checks as received, the integration records and the K table (history).
""")]

if __name__ == "__main__":
    sys.exit(E.main(NAME, HERE, EDITS, APPENDS))
