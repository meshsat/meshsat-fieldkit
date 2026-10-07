# The DESK-gate assessment's K table (K-01 to K-28) re-read on main `be07863b` (record l4k, MESHSAT-1357, 7 October 2026)

Register task L4A-87 (`_runs/l4ai/REGISTER.draft.md`, draft 2, section 9 item 2, a runner-local file). Written by worker W131 on branch
`fnd/l4k` from main `be07863bbca206a81ab42b9f96a7684c5c10a746`, read from 04:17 CEST. The table re-read is the one in section 5 of
`v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md` (28 rows, read there on the candidate `6bc4424e` and the promoted revision
`dd1aed00`: 19 standing, 6 of them with no restatement). Every evidence line below is `be07863b:<path>:<line>` followed by the
verbatim words on that line (whitespace, `*` and backtick marks aside); `test_l4k.py` holds each one against `git show be07863b:<path>`.

This is record text. It closes no cx46 item, changes no check's verdict and upgrades no state: cx46 reads CORRECTIONS NOT CLOSED,
Layer 4's DESK gate reads NOT PASSED, power-design closure and fabrication release read BLOCKED, as filed. Prototype framing:
nothing in the kit has been built, bought, powered or measured.

**The three states** (this record's reading, SESSION, W131): STANDING, both sides of the contradiction read as current on
`be07863b`; RESOLVED, one side was corrected or restated in its record (or the two sides are shown to name different things), so
no reader meets two current values; SUPERSEDED, one side's subject was replaced as a whole (a later revision adopted in its place).

**Counts on `be07863b`:** 28 rows; 7 STANDING, 20 RESOLVED, 1 SUPERSEDED. Of the 19 that stood on the candidate, 12 no longer
stand (set 31's merges of W3, W4, W5, W7, W9 and W11 and set 30's adoption); of the 6 the assessment found with no restatement,
K-15 is SUPERSEDED, K-18 RESOLVED by reading, and K-03, K-16, K-17 and K-22 stand.

**What this record does with the 7 STANDING rows:** K-16 is resolved on this branch (record efuse's page, a dated note in place);
K-03, K-13, K-17, K-23 and K-24 are resolved by apply scripts beside this file for set 33's integrated tree (each target is a file
set 32 changes or a file whose sha256 a set 32 output pins); K-22 is left STANDING (it changes no instruction, state, limit or
part; the figures belong to the ended rail-trip method, and their restatement is register task L4A-61's). The apply scripts also
date the ledger's items A, B and F (K-20, K-21, K-15), whose contradictions are resolved in the records but whose ledger text still
reads them as current.

## The rows

### K-01: RESOLVED (as on the candidate)
Set 29's criterion 2 text. `be07863b:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1007` "Set 29's inconsistency, corrected in the text."

### K-02: RESOLVED (as on the candidate)
The register's count. `be07863b:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1612` "DOWNSTREAM-REGISTER.md holds 235 items"; the
register carries 235 rows `| R-nn |` on `be07863b` (counted by `test_l4k.py`).

### K-03: STANDING; resolution prepared, `apply_l4k_lh12.py` (set 33)
LH-12 still proposes the fans off while keyed: `be07863b:v2/docs/records/l4e9/LAYER5-HANDOVER.md:28` "the outlets, the heater and the
fans off while keyed (the fans' supplies through FAN_OK, R-210 to R-212)", against the register's
`be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:134` "the fans NOT on it: round 8's fans while keyed WITHDRAWN 5 October 2026
with R-210 to R-212" and, on the same line, `be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:134` "LH-12's text is restated by
its owner record the same way (set 31, PC-08)", and `be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:306` "| WITHDRAWN | 3g |".
Authoritative: R-28 (the owner's rejection of FAN_OK). The script restates LH-12 in place (the fans clause quoted and WITHDRAWN,
round 8's basis kept as history, D-17's correction R-227 and R-238 named) and restates test_l4e9's one line that held the old text.
It touches the instruction Layer 5 would write into FW-A05, so it is in this task's scope (N2).

### K-04: RESOLVED (at set 30's adoption)
The P0 list's band and case. `be07863b:v2/docs/records/l4close/P0-POWER-LIST.md:68` "the revision 3 list carries the records' figure";
`be07863b:v2/docs/records/l9t5/l9t5_f01.out:132` "6.3518 to 6.9259 A over every corner"; `be07863b:v2/docs/records/l9t5/l9t5_f01.out:145`
"need 15.1308 V, a MODEL margin of 0.3692 V under 15.5 V". Round 2's band appears only as dated history.

### K-05: RESOLVED (as on the candidate)
`be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:337` "KNOWN ENGINEERING DEFECT | ASSIGN to the receiving company's remaining
engineering item RE-7" (R-242; R-244 and R-245 the same class at lines 339 and 340).

### K-06: RESOLVED (W7's rows P-01 to P-12, applied in set 31 at `467c2aaa`)
`be07863b:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1401` "(set 29's 45.88 K/W per FET of 4 October 2026, L4-E11's round 9,
SUPERSEDED as the per-FET bar)"; `be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:255` "each FET's (Zself + 2 Zmut) at most 40.78
K/W without m". Finding F-1 below (record l9stk, outside K-06's cited scope).

### K-07: RESOLVED (as on the candidate; W9-12 added the draft state on record l8r2's side)
`be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:154` "FIX: CHECK and APPLY record l8r2's VBUS20 over-voltage cut-off on
VIN_RAW"; `be07863b:v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md:11` "in DRAFT: nothing is applied and no independent check has
accepted these drafts".

### K-08: RESOLVED (W4 and W9 in set 31: every use of E-1 names its record)
`be07863b:v2/docs/records/l4e7/L4E7-P0SOL.md:130` "E-1 here is record l4e7's E-1"; `be07863b:v2/docs/records/l9t5/README.md:1`
"D-10 (record l4e7's E-1)"; `be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:255` "record l9stk 15.5, l9stk's E-1". The
identifier is not renamed; the two items are named apart wherever it is used (`test_w9l9t5.t_every_e1_names_its_record`).

### K-09: RESOLVED (W3's annex 6.5, merged in set 31: the reading stated, the identifier not renamed)
`be07863b:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:87` "D-06 in this section is the foundation decision of
the pack, not L4-E9's defect D-06 (section 6.5)."

### K-10: RESOLVED (as on the candidate)
`be07863b:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1031` "not independently accepted as closing D-16". The set 31 change that
took D-16 off OPEN is one of the unreviewed changes register task L4A-86 verifies; this record does not re-judge it.

### K-11: RESOLVED (as on the candidate)
`be07863b:v2/ecad/tools/tests/test_l4e9.py:686` "set 31: D-16 is ADDRESSED IN DRAFTS, not open".

### K-12: RESOLVED (W3's annex 6.2 and W7's R-08, in set 31)
`be07863b:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:193` "For layout the target is read as the row prints it,
at most 0.29 K/W, which meets both prints"; `be07863b:v2/docs/records/l4close/P0-POWER-LIST.md:177` "of the one computed target its
row E11-29 prints as 0.29 K/W".

### K-13: STANDING in two places; resolution prepared, `apply_l4k_p0sol.py` and `apply_l4k_p0list.py` (set 33)
The pages are restated (W4): `be07863b:v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:119-120` "ADDRESSED IN DRAFTS, PROVISIONAL, not
completed"; `be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:520` "ADDRESSED IN DRAFTS, PROVISIONAL, not completed". Still
current: record l4e7's generator output, `be07863b:v2/docs/records/l4e7/l4e7_p0sol.out:281-282` "Completed independently on the present
port network: D-16's correction (section 2)", printed by `be07863b:v2/docs/records/l4e7/l4e7_p0sol.py:1225` "Completed independently on
the present port network"; and the P0 list's quotation of the candidate's page, `be07863b:v2/docs/records/l4close/P0-POWER-LIST.md:124`
"Completed independently of E-1 ...: D-16's correction". Authoritative: the pages and R-240 (DRAFTED). The generator's sentence is
restated to the pages' state words (four printed lines kept); the P0 list keeps its quotation (true of its revision) with a dated
note beside it. It touches a state (D-16 read as completed), so it is in scope (N2).

### K-14: RESOLVED (W5, merged in set 31)
`be07863b:v2/docs/records/l8p/L8P-BREAKER.md:266` "One release for the six drafts that read this folder's one RELEASE.md."

### K-15: SUPERSEDED (set 30's adoption, `836f711b`: revision 3 adopted in place of revision 2)
`be07863b:v2/docs/records/l4close/P0-POWER-LIST.md:1` "revision 3: the state after cx46 and the disposition". The ledger still reads
`be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:732` "The P0 list is revision 2 (RE-1)": dated by `apply_l4k_remeng.py`
(item F). Revision 3's own check is register task L4A-86's (L4A-85 merged into it).

### K-16: STANDING on `be07863b`; RESOLVED on `fnd/l4k` (record efuse's page, two dated notes in place)
`be07863b:v2/docs/records/efuse/EFUSE-SETTINGS.md:213` "round 2 has none", against
`be07863b:v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:10` "P0-4: CONFIRMED AS CONDITIONAL on connector
thermal qualification and the RockBLOCK build condition" and
`be07863b:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:191` "16. P0-4 eFuse conditions retained: CLOSED AS
CONDITIONAL". The page is byte for byte the same at `06077cee`, `4d0ff8a2` and `be07863b` (sha256/16 d7f48ef5009684f9, held by
`test_l4k.py`). Each check's words stand as given; EF-F03 stays a design defect, OPEN. It touches a review state, so it is in scope.

### K-17: STANDING (the ledger's item C); resolution prepared, `apply_l4k_remeng.py` (set 33)
`be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:714-715` "records l9t5_f01.out at a sha256 that differs from the file on
1c6d56f5", against `be07863b:v2/docs/records/l9t5/stability/DIGESTS-cr3.txt:15` "v2/docs/records/l9t5/l9t5_f01.out pass 1:
sha256=2aa78a957e497677" (re-taken at CANDIDATE 3, `ac8efbca`; at `1c6d56f5` the same line read 2c590640, at `6bc4424e` the file
and the connected output's pin read 2aa78a957e497677, and on `be07863b` the pin and the file read f1aa6ae62223e936, each held by
`test_l4k.py`). A state of the ledger (a stability gap reported as open), so in scope.

### K-18: RESOLVED (by reading; the filed check is not edited)
`be07863b:v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:8` "e132db0e73da723cf18d32788aa8c9252c0bcfbe" is
the job's base; `be07863b:v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:20` "HEAD is
06077cee85d0ed44c74c2a06c9fbb2030a0dedbc" is the revision read; `be07863b:v2/docs/records/efuse/EFUSE-SETTINGS.md:3` "from fnd/p0base
e132db0e" names e132db0e as the P0 branches' base. Two fields, two meanings; every record names cx45's revision `06077cee`
(`be07863b:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1285` "| cx45 (Astra, the one focused check) | 06077cee |"). No record needs a change.

### K-19: RESOLVED (as on the candidate)
`be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:302` "U101 LM5069MM-1, the latch-off variant"; the change list's row 92
`be07863b:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:517` "LM5069MM-1, the latch-off variant".

### K-20: RESOLVED (W9-01 and W9-02, merged in set 31 at `0ed29a78`)
`be07863b:v2/docs/records/l9t5/T10-ROUND5.md:227` "renamed from L9T5-F26"; `be07863b:v2/docs/records/l9t5/README.md:196` "The
identifier is this finding's alone". The ledger's item A still reads the collision as current
(`be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:709` "One finding identifier, two findings."): dated by `apply_l4k_remeng.py`.

### K-21: RESOLVED (W9-03 to W9-06, merged at `0ed29a78`)
`be07863b:v2/docs/records/l9t5/README.md:59` "27.9108 A in this one-node model"; `be07863b:v2/docs/records/l9t5/README.md:147` "the
study's own declared upper bound, 27.8159 A"; `be07863b:v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md:1081` "every 'declared upper
bound' of this paragraph is that figure". The ledger's item B (`be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:712` "Two
figures for the declared upper bound of the return."): dated by `apply_l4k_remeng.py`.

### K-22: STANDING; left STANDING, owner register task L4A-61
`be07863b:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:89` "= 0.9259 s" against
`be07863b:v2/docs/records/l9t5/l9t5_t10.out:585` "reaches the trip's maximum after 0.98 s"; the countermodel's
`be07863b:v2/docs/records/l9t5/l9t5_t10.out:620` "127.54 C, OVER 125 C" against cx46's 127.55 C (its finding 7, line 91). Two MODEL
readings from two starting states, a filed check never edited; the ledger states both and
`be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:721` "Neither difference changes a state". No instruction, state, limit
or part rests on the difference: both belong to the RC-averaged rail trip, the ended method of RE-6 and RE-7, whose V-B23 and T10
rows are restated by register task L4A-61 after the new method (L4A-56, L4A-57). Not changed here.

### K-23: STANDING in the generator; resolution prepared, `apply_l4k_p0sol.py` (set 33)
The pages are restated (W4): `be07863b:v2/docs/records/l4e7/B2-PRESENCE.md:184` "REMAINING ENGINEERING inside E-1" and
`be07863b:v2/docs/records/l4e7/B2-PRESENCE.md:185-186` "P1-1's S1 row (b) is the later validation of that computation, not a
substitute for it". Still current: `be07863b:v2/docs/records/l4e7/l4e7_p0sol.out:403` "Validation: P1-1's S1 (the first two added to
its rows)", printed by `be07863b:v2/docs/records/l4e7/l4e7_p0sol.py:1353` "Validation: P1-1's S1 (the first two added to its rows)".
Authoritative: the pages and the ledger's HO-F. A state (an engineering case read as validation only), so in scope.

### K-24: STANDING at one of its two cited places; resolution prepared, `apply_l4k_changelist.py` (set 33)
The heading is restated (W4): `be07863b:v2/docs/records/l4e7/L4E7-P0SOL.md:121` "route B2 (UNSELECTED and WITHDRAWN AS DRAFTED, outside
the baseline)"; L4-E9's generator data `be07863b:v2/docs/records/l4e9/l4e9_power_path.py:4264` "UNSELECTED and WITHDRAWN AS DRAFTED,
outside the baseline, no protection credit and no owner item". Still current: the applier's docstring,
`be07863b:v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:23` "route B2 an unapproved PARTIAL proposal that does not resolve it".
The script marks the sentence as the text of `7070f106` and states the baseline's reading; the applier's data (what it applied) is
not edited. Any other B2 wording is register task L4A-80's sweep.

### K-25: RESOLVED (as on the candidate)
`be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336` "the receiving company's engineering item l4e7's E-1 (its later validation
step is S1".

### K-26: RESOLVED (W11-04 in the generator, the output regenerated in set 31)
`be07863b:v2/docs/records/l9t5/l9t5_connected.out:350` "revision X HELD with no admission route (round 5's V-B20 route SUPERSEDED, 10j
(f))". Revision X's admission elsewhere is register task L4A-60's (RE-8).

### K-27: RESOLVED (as on the candidate; Slot F's draft is not in the tree)
`be07863b:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:965` "The DESIGN gate (criteria 1 to 5 below) is not the DESK handover gate of
the owner's part 19".

### K-28: RESOLVED (W11-05 in the generator, the output regenerated in set 31)
`be07863b:v2/docs/records/l9t5/l9t5_connected.out:361` "APPLIED by the integrator at set 30's integration commit 7070f106"; L4-E9's
four cascade pins equal their files on `be07863b` (`be07863b:v2/docs/records/l4e9/l4e9_power_path.out:55` "30228a3a971405b0",
`be07863b:v2/docs/records/l4e9/l4e9_power_path.out:64` "36141414a1b60011", `be07863b:v2/docs/records/l4e9/l4e9_power_path.out:67`
"68d3df24f9e105cd", `be07863b:v2/docs/records/l4e9/l4e9_power_path.out:106` "3acf4672e3c85c03", each the sha256/16 of the file it
names, held by `test_l4k.py`).

## Findings for the coordinator (outside the K table; nothing changed for them here)

- **F-1 (K-06's family, record l9stk).** `be07863b:v2/docs/records/l9stk/README.md:116` "three at 45.88 K/W with R17 apart" states E-1's
  limit as set 29's even-split bar, while R-159 reads 40.78 K/W for each FET's (Zself + 2 Zmut) without m (K-06's evidence above), and
  record l4e11 states the same as its finding for record l9stk (`be07863b:v2/docs/records/l4e11/README.md:118` "record l9stk's E-1 bar
  45.88 K/W is the even split's"). K-06 cites L4-E9's page only, so this record does not widen to it: a K row or a line in register
  task L4A-71 (the selection gate on the 40.78 K/W bar) is the coordinator's choice.
- **F-2 (the register's count).** The register's L4A-87 row reads 19 standing on `dd1aed00` with 6 unrestated; on `be07863b` it is 7
  standing, of which 5 are resolved by this record's apply scripts only once set 33 applies them; until then the 7 stand on main.
