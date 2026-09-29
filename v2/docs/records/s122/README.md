# Stream s122: the documents CFL-016 names, re-read against the netlists (S-122, MESHSAT-1357)

Prototype design: nothing here is built, bought or measured. Rounds 1 to 3 ran on `fnd/s122` and `fnd/s122b` (from
`main` at `b874b744`, set 13 promoted as `32f26b41`); set 14 (`fnd/int15`) carried them to `1bafab8c`, where
`apply_registry_s122.py` has run. Round 4 runs on `fnd/s122c` from `1bafab8c`, 29 September 2026. The stream changes
documents and its own records only; no generator, netlist or registry file is edited on its branches (the registry
changes are `apply_registry_s122.py`, `apply_registry_s122_r4.py` and `close_s122.py`, for the integrator).

Round 1 corrected 43 passages. The independent check of round 1 (`checks/check-s122-1.md`, filed byte for byte from the
checker's `<scratch>/chk-s122/CHECK.md`) read all 43 true and found 3 blocking and 12 minor items. Round 2 answers them under the coordinator's ruling on CONOPS.md's
baseline. The independent check of round 2 (`checks/check-s122-2.md`, filed byte for byte from the checker's
`<scratch>/chk-s122/CHECK-2.md`) found 1 blocking and 8 minor items; round 3 answers them and changes the method so the
blocking item's class cannot recur (below). Set 14's integration checks
(`v2/docs/records/int15/checks/check-int15-1.md` to `-3.md`, and a fourth check of set 14 held by the integrator)
found five sentences in scope naming parts no generator carries, which the finder could not see because it did not read
makers' part numbers; round 4 answers them and check-s122-3's three minors (below). Every statement below about what
was read is what one of these scripts read, or a filed check's own words quoted with its file.

## Round 4: makers' part numbers (set 14)

* **The finder** (`s122lib.partnos`, returned by `names()` under `parts`) reads a maker's part number by its shape, not
  from a list: a letter-led token of capitals and digits with a run of three digits (TMDS341A, LM5069, E22-900M30S,
  D38999/26FC4SN), a digit-led token with a capital and four digits (74LVC1G157GW, 2N7002), a digit token with a dash
  and six digits (2199119-3), a series word of two to four capitals before a digit-led number with a dash and three
  digits (TEN 40-2412WIN), and the same shapes in the file names of the makers' sheets a sentence cites
  (`m2/amphenol-mdt420b01001-m2-b-key.pdf`). It leaves out tokens with a lower-case letter (commits, units), registry
  and standard identifiers (letters, dashes, one number: CFL-016, MIL-STD-810), tokens led by a standard body, and pure
  ranges of two numbers of up to four digits (144-146). A table cell carries its row's label (`names()["row"]`).
* **The judgement** (`verdicts.check_parts`): each part number is looked up in the part values of the six netlists. One
  on no netlist, or not on the one board a sentence and its row label name, makes a TRUE judgement STALE and a NOT
  DERIVABLE one UNJUDGED, unless the judgement's `parts_ok` names it: an own assertion that names it (a generator or a
  netlist at a commit, a document, a part value), or a reason that starts with a kind (`document`, `case`, `bought`,
  `stock`, `stackup`, `withdrawn`, `owed`, `module`, `elsewhere`; `elsewhere` is refused unless the part is on some
  netlist). A dated heading excuses no part: the boards table's rows are judged part by part.
* **New assertion forms:** a held maker's sheet read with `pdftotext` (`PDF:<path>~words`).
* **What it found on set 14's documents** (`verdicts-set14.out`, the documents at `1bafab8c` judged by round 4's tools):
  7 STALE, each corrected by `apply_docs_s122_r4.py` (12 edits, 51 assertions held first):

  | Where (at `1bafab8c`) | What it named | What the netlists carry | Correction |
  |---|---|---|---|
  | V2-SPEC.md line 82, B16 row | the TMDS341A display switch (no schematic generator has held one, `git log --all -S TMDS341`) and the DS3231M clock | board B's `U3` and `U4` TS3DV642A0RUAR (`gen_sch_b.py` held the TS3DV642 at `b2709118`, when the table was written); `U9` DS3231SN | "the two TS3DV642 display switches (`U3`, `U4`)", "the DS3231SN clock (`U9`; the DS3231M on 7 September)" |
  | V2-SPEC.md line 84, D8 row | the TUSB2046B hub | board D's `U4` TUSB2046IBVFR (the industrial grade since 26 September 2026, W6-F5) | "the TUSB2046I hub (`U4`, TUSB2046IBVFR ...; the TUSB2046B on 7 September)" |
  | V2-SPEC.md line 86, E6 row | the LM5176 9 to 36 V front end on E6 | board E's `U6` LM5069MM-2 hot swap; the LM5176 front end is board A's `U2`, as `gen_sch_e.py` said at `b2709118` | "the LM5069 hot swap on the 9 to 36 V input (`U6`), which passes the bus up to A22's LM5176 front end (`U2`)" |
  | V2-SPEC.md line 47, APRS row | the WM8960 codec, and the PA's sheet "owed" | board D's `U6` PCM2912A (the WM8960 left `gen_sch_d.py` at `bdfc7b3f`); the RA30H1317M1's sheet held in `v2/vendor/mitsubishi/` | "Direwolf on D8's PCM2912A USB codec (`U6`)", the sheet held |
  | OPERATING-ENVELOPE.md line 77 | TRACO TEN 40-2412WIN, -40 to +75 C | no TRACO part on any netlist (`gen_sch_e.py`: the TRACO converter of E4 is gone); board E's input part is `U6` LM5069 | "TI LM5069 hot-swap controller on the 9 to 36 V input (board E `U6`)", junction -40 to +125 C from `ti/ti-lm5069.pdf` (SNVS452G, 7.3, read by pdftotext) |
  | OPERATING-ENVELOPE.md line 83 | Amphenol M.2 B-key socket, MDT420B01001 (in its source's file name) | board B's `J_M2C2` TE 2199119-3; Amphenol's MDT420M02001 are the M-key NVMe sockets | "TE 2199119-3 M.2 B-key socket (board B `J_M2C2`)", -40 to +80 C service temperature from `m2/te-2199119-m2-b-key.pdf` (Performance Ratings) |
  | CONOPS.md line 1056, section 7's D-13 row | the STM32H753 in the schematic, the mismatch open | `U41`, `U51`, `U61` STM32H743VIT6 since `458b2873`; CON-017 PASS | the baseline stays; row DC-10 on the status page (check-s122-3 m1) |

  V2-SPEC.md records the four lines as correction 34; OPERATING-ENVELOPE.md carries a correction note after its table;
  in check-int15-1's words (B1 fix) no envelope number depends on either row.
* **check-s122-3's minors:** m1, row DC-10 (above); m2, the absent rule reads the wordings the check swept ("has no",
  "does not have", "only through", "in the schematic", "nothing does", "lacks", "no path", "no hardware", "not gated",
  "driven only", "until ... generator", besides the four words): the committed `verdicts.out` at `d38c6b4d` held 35
  CONOPS sentences with those wordings (18 with the four words), and it holds 51 now, 16 TRUE, 18 BASELINE, 17 NOT
  DERIVABLE with each wording bound to a phrase that is not about the circuit, 0 STALE, 0 UNJUDGED; the sentences it
  added include section 7a's HOT-R1 row's second cell (BASELINE on DC-02) and section 7's D-13 row; m3, the CON-003
  note below.
* **check-int15-1's m7:** `apply_registry_s122_r4.py` appends to CFL-016's `notes` the reading of its acceptance through
  the status page.
* **The fourth check of set 14:** q1 (S-122's row clause) is answered by `apply_registry_s122_r4.py`'s appended
  sentence; q2 and q3 by `close_s122.py`'s gate (below); q4 by `apply_docs_s122_r4.py`'s edit of
  `records/int15/apply_check15c_fixes.py`'s docstring (its filing note ends each check) and the gate's rewritten
  docstring.

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
    (`U7` on A, `U25` on B), DC-05 a loss of `+3V3_DEV`, DC-06 generator line numbers; since round 3 DC-07 the
    supervisors' I2C status path, DC-08 the fabric's break-before-make and back-power gating, DC-09 board A's CC array.
* **reads CONOPS through the status page**: a CONOPS sentence whose value differs from the netlists, or that cites a
  generator line, is **BASELINE** when a DC row keeps its current value, and **STALE** when none does. The status
  page's section and EMCON.md 0a.1 are judged directly.

## Files

| File | What it is |
|---|---|
| `s122lib.py` | the parser, the name finder and `SCOPE`; reads the six netlists with `tx_inhibit.parse_netlist`; `S122_AT=<commit>` reads the documents (not the netlists) at a commit |
| `inventory.py` | writes `inventory.out` |
| `judgements.py` | the stream's judgement of each sentence, keyed by its digest, with its assertions |
| `verdicts.py` | looks up every named part, reads every cited generator line, evaluates every assertion and every stated count of parts, applies the baseline rule and the absent rule, writes `verdicts.out` |
| `sweep_absent.py` | counts the CONOPS.md sentences of a `verdicts.out` (the working file, a path, or the file at a revision) that state something absent or owed (the wordings of `s122lib.ABSENT`), by verdict |
| `inventory-base.out`, `verdicts-base.out` | the base's documents at `e57a7365` (run with `S122_AT=e57a7365`), judged on the committed netlists |
| `inventory-set14.out`, `verdicts-set14.out` | set 14's documents at `1bafab8c` (run with `S122_AT=1bafab8c`), judged by round 4's tools |
| `inventory.out`, `verdicts.out` | the documents as they stand: 985 sentences, 0 STALE, 0 UNJUDGED |
| `apply_docs_s122.py` | round 1's 43 passages (on this branch in `51952c0c`; refuses a second run) |
| `apply_docs_s122_r2.py` | round 2: the CONOPS restore, EMCON.md 0a.1, the status page's section, 16 passages; 497 assertions held first (on this branch in `29acd948`) |
| `apply_docs_s122_r3.py` | round 3: the status page's rows DC-07 to DC-09, the notes of DC-03 and DC-04 and the section's lead, the baselines table's `c5430071` file, the EMCON citations of PANEL.md and V2-SPEC.md and V2-SPEC.md's correction 33; 144 assertions held first; refuses a second run |
| `apply_docs_s122_r4.py` | round 4: V2-SPEC.md lines 47, 82, 84 and 86 and correction 34, OPERATING-ENVELOPE.md's two rows and note, row DC-10, the int15 docstring; 51 assertions held first; refuses a second run |
| `checks/` | the filed independent checks, `check-s122-1.md` to `check-s122-3.md` (rounds 1 to 3) |
| `apply_registry_s122.py` | rounds 1 to 3's registry script (run at set 14, `9eaf406f`; refuses since) |
| `apply_registry_s122_r4.py` | for the integrator: round 4's rebinds, CFL-016's entry and note, S-122's title sentence, the envelope re-pin |
| `close_s122.py` | S-122's closure, for the integrator, last |
| `LOG.md` | the stream's log |

## Scope (`s122lib.SCOPE`) and the finder

PANEL.md sections 1, 2, 3, 5, 6, 7, 9 and 10; CONOPS.md sections 2a, M2, M4, **4 with 4a to 4f** (round 2: every row of
section 4, and 4c and 4d, which the check showed are subsections of section 4), and 5; V2-SPEC.md and TEST-PLAN.md
whole; OPERATING-ENVELOPE.md sections 2 to 4; ASSEMBLY.md **sections 2** (every step since round 2), 4, 8 and 9;
decisions 28 and 40; EMCON.md section 0a.1 and the status page's new section; and, since round 3, every sentence of
CONOPS.md in any section that states something absent, owed, not drawn or not connected (18 sentences). Not read:
PANEL.md's head and sections 4, 8 and 11; CONOPS.md's other sections but for those sentences; OPERATING-ENVELOPE.md
sections 1 and 5 to 8; ASSEMBLY.md's other sections.

A sentence is inventoried when it names a part designator, a net, a board, a rail, a gate function, a generator line,
**EMCON**, or a **spelled count of parts** (round 2). The count rule: a sentence that states a count of parts (two to
twenty LEDs, pins, sockets, cards and the like) is UNJUDGED until each count is covered. Round 3 (check-s122-2 m8: two
excuses named the wrong count, and the script did not read them) makes the cover checkable: with one count, a count
assertion of the same number or a reason; with several, `counts_ok` maps each count phrase to a reason that names what
the phrase counts (its noun), or to `asserted: <assertion>`, one of the judgement's own count assertions whose number
is the phrase's. V2-SPEC.md line 41's two SIM holders are now `asserted: B:#ref~J_SIM=2`, ASSEMBLY.md line 92's two
headset jacks `asserted: C:#ref~J_HSJ=2`.

The parser (round 3, check-s122-2 m7) keeps a wrapped list item's indented continuation lines with the item, so a
sentence across them is judged whole; the merged items were judged again (CONOPS.md section 4d's four steps, V2-SPEC.md's
corrections, OPERATING-ENVELOPE.md section 4's two items).

**The absent rule (round 3, check-s122-2 B1).** A CONOPS.md statement that the supervisors' I2C status path is "absent
as generated" was judged NOT DERIVABLE and had no row, while the netlists carry the path since `458b2873`. Now every
sentence of CONOPS.md that states something absent, owed, not drawn or not connected is inventoried, in any section, and
judged against the netlists, TRUE or BASELINE. A NOT DERIVABLE judgement of such a sentence must bind each of those words
to a phrase quoted from the sentence that is not about the generated circuit (`absent_ok`); otherwise the sentence is
UNJUDGED and the closure refuses. `sweep_absent.py` counts them:

| `verdicts.out` | CONOPS.md sentences with the words | TRUE | STALE | BASELINE | NOT DERIVABLE | UNJUDGED |
|---|---|---|---|---|---|---|
| before the re-sweep (`83cb0640`) | 14 | 1 | 0 | 7 | 6 | 0 |
| after (this commit) | 18 | 3 | 0 | 11 | 4 | 0 |

The four added are outside round 2's scope (section 2's need, section 7's D-17 row, section 7a's BANK-R1 and HOT-R1
rows). The four NOT DERIVABLE bind "absent" in section 2's need (the setting the kit serves), "owed" in section 2a (a
case measurement), in section 4's charger cell (a bench confirmation) and in section 4e's reading date. The inventory takes every
such sentence of the file, in any section.

## What the verdicts mean

* **TRUE**: judged true on reading, and every check `verdicts.py` runs holds (every named part is on a netlisted board,
  every cited generator line holds a named part at the commit it is dated to, every assertion and every stated count).
  What a TRUE sentence says beyond the netlists is named in its judgement and not judged.
* **STALE**: the netlists or generators no longer carry it.
* **BASELINE**: a CONOPS passage whose value is the baseline's, its current value kept in a DC row of the status page;
  its assertions, which state the current value, must hold, or it is STALE (round 3).
* **NOT DERIVABLE**: HISTORY (a dated record), FIRMWARE, HELD DOCUMENT, TEST, CASE or LEAD; left as it stands.
* **UNJUDGED**: no judgement, a count not covered, or an absent statement judged NOT DERIVABLE without its phrase
  bound; the closure refuses on any.

## Counts per document

| Document | Base (`e57a7365`): sentences | STALE | Set 14 (`1bafab8c`): sentences | STALE | After: sentences | TRUE | STALE | BASELINE | NOT DERIVABLE |
|---|---|---|---|---|---|---|---|---|---|
| PANEL.md | 164 | 10 | 167 | 0 | 167 | 131 | 0 | 0 | 36 |
| CONOPS.md | 286 | 31 | 284 | 1 | 284 | 50 | 0 | 40 | 194 |
| V2-SPEC.md | 137 | 10 | 146 | 4 | 150 | 56 | 0 | 0 | 94 |
| OPERATING-ENVELOPE.md | 56 | 6 | 56 | 2 | 60 | 20 | 0 | 0 | 40 |
| TEST-PLAN.md | 109 | 2 | 109 | 0 | 109 | 18 | 0 | 0 | 91 |
| ASSEMBLY.md | 156 | 13 | 156 | 0 | 156 | 90 | 0 | 0 | 66 |
| decisions 28 and 40 | 9 | 0 | 9 | 0 | 9 | 6 | 0 | 0 | 3 |
| EMCON.md 0a.1 | 0 | 0 | 26 | 0 | 26 | 22 | 0 | 0 | 4 |
| DEFINITION-STATUS.md (the section) | 0 | 0 | 22 | 0 | 24 | 17 | 0 | 0 | 7 |
| total | 917 | 72 | 975 | 7 | 985 | 410 | 0 | 40 | 535 |

All three files are judged by round 4's tools (so the base and set 14 read part numbers too; 0 UNJUDGED in each).
3219 assertions are evaluated after (2492 at the base, 3148 on set 14's documents); 252 sentences name a part number.
Before round 4 the committed `verdicts.out` read 862 sentences, 339 TRUE, 0 STALE, 38 BASELINE, 485 NOT DERIVABLE.
The 40 BASELINE sentences of CONOPS point to DC-01 (11), DC-02 (8), DC-03 (1), DC-04 (1), DC-05 (1), DC-06 (14), DC-07
and DC-08 (the same 2), DC-09 (1) and DC-10 (1).

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

## The check's items (check-s122-2)

| Item | Answer |
|---|---|
| B1 (the supervisors' I2C status path "absent as generated", CONOPS lines 310 and 490 to 492, NOT DERIVABLE with no row) | row DC-07: `U41`, `U51`, `U61` pin 93 (PB7) on `SDA` and pin 92 (PB6) on `SCL` since `458b2873` (both unconnected at its parent `1f614233`), at `45bde541`, at `95e078a1` where the passages were written, and at `c5430071`; the TCA9517A segment of SC-HF-02 is what is owed. Row DC-08 for the clauses beside it: the break-before-make of FAB-03 and the back-power gating of FAB-02 (b) and (c) (`U513` to `U520`, `U530` to `U535`) are drawn since board B's round 8, present at `95e078a1` and `c5430071`, absent at `45bde541`; S-42 OPEN, CON-003 and CON-022 INCONCLUSIVE waiting on it. Both sentences BASELINE on DC-07 and DC-08. The absent rule, and the sweep above, which added DC-09 (D-17's CC array, `U31`, drawn since `458b2873`) and section 7a's HOT-R1 row to DC-02 |
| m1 (PANEL.md line 156 cites CONOPS 4b) | cites `feasibility/EMCON.md` section 0a.1, which the script asserts names `U540`, `R536` and `R537` |
| m2 (V2-SPEC.md line 24 cites CONOPS 4b) | cites EMCON.md section 0a.1; V2-SPEC.md's correction 33 records it |
| m3 (DC-03 and DC-04 were wrong at the baseline's reading) | both rows say so, asserted at `45bde541` and `a9f212c7`; the section's lead says what such a note means |
| m4 (the baselines table lacks `c5430071`'s file) | `6cb7b241cb84d729` at `c5430071` added to CONOPS's row |
| m5 (495, not 497) | the judgement and this README say 497 |
| m6 (the README cited commits of `fnd/s122`) | this branch's `51952c0c` and `29acd948` |
| m7 (wrapped list items split) | the parser keeps continuation lines; the merged items judged again |
| m8 (two count excuses name the wrong count; `counts_ok` not checked) | the count rule above checks each cover |

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
  * appends three CFL-016 entries: the inventory (rounds 2 and 3, with the absent sweep in its scope), the baseline
    rule with round 3's absent rule, and check-int13-4's n1 and n2;
  * appends n3 and n4 to S-122's title;
  * re-pins the envelope and ENV-001 after asserting no envelope number left OPERATING-ENVELOPE.md;
  * asserts every other record and item unchanged, re-parses, and refuses a second run.
* `apply_registry_s122_r4.py` (round 4; after `apply_registry_s122.py`, which has run at set 14):
  * rebinds the records bound to V2-SPEC.md (REQ-005, CFL-010, CFL-013, CFL-016), OPERATING-ENVELOPE.md (CFL-014,
    CFL-016) and DEFINITION-STATUS.md (CFL-016) at their set 14 shas, each reason read from the diff against
    `1bafab8c`, the sentence sets, `verdicts-set14.out` and `verdicts.out`, and the record's own text;
  * appends CFL-016's round 4 inventory entry (the finder, the judgement, the counts it reads, the corrections) and a
    sentence to its `notes` (m7); appends one sentence to S-122's title stating what the gate checks since round 4 (q1);
  * re-pins the envelope and ENV-001 after asserting no envelope number left OPERATING-ENVELOPE.md and the diff stays in
    section 2; CONOPS.md is unchanged, so the needs pin does not move;
  * asserts every other record and item unchanged, re-parses, and refuses a second run.
* `close_s122.py <check>`, its gate (`gate_set14`, rewritten in round 4):
  * (a) probes the finder with the five part numbers check-int15-1 found and ten made up at run time in five shapes,
    and with five made-up non-parts it must not read;
  * (b) finds the corrected sentences by what they say ("<part> display switch", "<part> codec", "<part> hot swap",
    "<part> hot-swap controller", "<part> M.2 B-key socket" in V2-SPEC.md and OPERATING-ENVELOPE.md outside their
    correction notes), and needs each to name the generated part, be TRUE and not HISTORY, and assert that part on its
    board; it refuses the TMDS341A, the WM8960, a TRACO part or the MDT420B there, and the LM5176 in a dock strip
    sentence other than as A22's;
  * (c) needs the check to carry the heading "## S-122 closing check" and under it each such sentence by its document
    and line; on this commit those are V2-SPEC.md lines 47, 82, 84 and 86 and OPERATING-ENVELOPE.md lines 77 and 83;
  * (d) needs the check to name check-int15-1 and to have been committed on a line that carries `097d2517`;
* and then, as before:
  * checks the rebinds of both registry scripts are in and current;
  * re-runs the inventory and verdicts, and needs 0 STALE and 0 UNJUDGED, identical to the committed outputs;
  * needs CFL-016's baseline entry, the status page's rows, and sentences judged in EMCON.md and DEFINITION-STATUS.md;
    the absent rule holds through its 0 UNJUDGED;
  * needs the check committed at HEAD, starting `mergeable: yes`, and naming every document and `verdicts.out`;
  * then closes S-122 and sets CFL-016 to PASS.
* **Round 4, replayed on a throwaway clone of `e5fdf670` (deleted after):**
  * the six outputs reproduce byte for byte (`inventory.out` and `verdicts.out`; `-base` with `S122_AT=e57a7365`;
    `-set14` with `S122_AT=1bafab8c`);
  * `apply_docs_s122_r4.py` refuses on the tip; with the four files checked out from `1bafab8c` it writes 12 edits
    after 51 assertions and the tree equals the tip byte for byte; a second run refuses;
  * the gate refused: a finder rigged to know only check-int15-1's five part numbers (at a part number made up at run
    time); V2-SPEC.md and OPERATING-ENVELOPE.md put back to `1bafab8c` (line 47 still names the WM8960); the B16 row
    relabelled "B16 (compute)" with "TMDS351" in place of the TS3DV642 (named, not the generated part); the E6 row with
    "the LM5176 9 to 36 V front end, all under A22" (the LM5176 in a dock strip sentence other than as A22's); line 47
    with a WM8731 codec; the B-key row naming a Molex socket (no corrected sentence stands); a TRACO TEN 60 row; the
    B16 row judged HISTORY (not TRUE); the B16 row TRUE without its U3 and U4 assertions; a check without the marker;
  * `apply_registry_s122_r4.py` rebound 5 records (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005), wrote CFL-016's entry
    and note and S-122's sentence, re-pinned the envelope and ENV-001 to `26e98ecfd2e4ec2f`, and refused a second run;
    `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings; `rules_lib.py`: 59 rules, 0 errors;
  * `test_envelope_data` with `test_requirements`: 69 passed and 2 failed (the trace page) before
    `rules_render.py --requirements`, 71 passed after;
  * the closure refused the fixture while only staged (its provenance), closed S-122 with it committed (not filed; the
    marker and the six lines; 985 sentences, 0 STALE, 0 UNJUDGED; CFL-016 PASS; S-42, S-123 and S-124 still open) and
    refused a second run; after it `rules_lib.py requirements` 0 errors, the tests 71 passed, `claims_check` PASS, 91
    of 91.
* **Round 3, replayed on a throwaway clone of `89b9ac6b` (deleted after):**
  * the four outputs reproduce byte for byte, the base's with `S122_AT=e57a7365`;
  * `apply_docs_s122_r3.py` refuses on the tip; with PANEL.md, V2-SPEC.md and DEFINITION-STATUS.md checked out from
    `83cb0640` it writes 10 edits after 144 assertions and the tree equals the tip byte for byte; a second run refuses;
  * `apply_docs_s122_r2.py --check` with round 1's documents (`1594090e`): 16 edits, 497 assertions;
  * the registry script rebinds 20 records, writes CFL-016's entries with rows DC-01 to DC-09 and the absent rule, and
    refuses a second run; `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings; `rules_lib.py`: 59 rules,
    0 errors;
  * `test_envelope_data` with `test_requirements`: 69 passed and 2 failed (the trace page) before
    `rules_render.py --requirements`, 71 passed after;
  * the closure refused the fixture while only staged, closed S-122 with it committed (not filed; 862 sentences,
    0 STALE, 0 UNJUDGED; CFL-016 PASS; S-123 and S-42 still open) and refused a second run; after it
    `rules_lib.py requirements` 0 errors, the tests 71 passed, `claims_check` PASS, 91 of 91.
* **Replayed on a scratch clone of `53292087` (round 2), and again of `ede23557` on the promoted set 13 with the same results:**
  * the four outputs reproduce byte for byte;
  * `apply_docs_s122_r2.py` refuses a second run;
  * the registry script rebinds 20 records and refuses a second run;
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors;
  * `test_envelope_data`: 6 passed. `test_requirements`: 63 passed and 2 failed before `rules_render.py --requirements`, 65 passed after;
  * the closure refused a staged fixture and a fixture naming neither EMCON.md nor DEFINITION-STATUS.md, closed with a
    committed fixture (not filed), and refused a second run;
  * after it, `rules_lib.py requirements`: 0 errors. `test_requirements` with `test_envelope_data`: 71 passed. `claims_check`: PASS, 91 of 91.

## Integrator's run order

1. Merge `fnd/s122c` (from `1bafab8c`, set 14's line, where `apply_registry_s122.py` has run).
2. `python3 v2/docs/records/s122/apply_registry_s122_r4.py`
3. `rules_render.py --requirements`; `rules_status.py` and `rules_render.py` for the envelope pin (ENV-001's `verified_sha`, the PCB-RULE-STATUS pages, LAYER-STATUS).
4. An independent check filed under `v2/docs/records/s122/checks/` and committed. It must start `mergeable: yes`, name
   check-int15-1, PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, pcb_decisions.yaml,
   EMCON.md, DEFINITION-STATUS.md and `verdicts.out`, and carry the heading `## S-122 closing check` under which it names
   V2-SPEC.md line 47, V2-SPEC.md line 82, V2-SPEC.md line 84, V2-SPEC.md line 86, OPERATING-ENVELOPE.md line 77 and
   OPERATING-ENVELOPE.md line 83 (the gate prints the list if a line moves), in its own words.
5. `python3 v2/docs/records/s122/close_s122.py v2/docs/records/s122/checks/<the check>`
6. `rules_render.py --requirements` again.

If a document of the scope changes on main before step 5, re-run `inventory.py` and `verdicts.py`, judge the new text
in `judgements.py`, and commit the outputs, or the closure refuses.

## What stays open

* S-122 and CFL-016, until the check of step 4 and the closure of step 5.
* CONOPS.md's 38 BASELINE passages stay as baselined. Their current values live on the status page until a reopening of
  the definition decides otherwise. `feasibility/ZEROIZE.md`'s citation `CONOPS.md:404` (the check's observation) is
  outside the scope.
* CON-003 and CON-022 (corrected in round 4, check-s122-3 m3 and its section 5): CON-003's evidence entry 2 says
  "R480 and R500 still 100k" of the netlist "at `eadbe571`", and CON-022's entry 1 says FAB-02's "remedy (b) and (c) is
  not drawn"; in check-s122-3's words (its section 5) their later entries record the change (CON-003: "R480 to R500,
  R15 and R16 are 10 k"; CON-022's entry 5: (b) and (c) "are drawn"), so these are dated readings in chronological
  lists, not the records' current claims.
  On board B's netlist `3ef9b8c49a01b728` `R480` and `R500` read 10k and `U513` to `U520` are drawn (asserted in the
  judgement of row DC-08's cell). S-42 stays open; its title's terms are the gate's assertion and its mutation for
  each fix.
* check-s122-2's observations: EXECUTION-PLAN.md line 629 and `feasibility/ZEROIZE.md`'s CONOPS line citations are
  outside the scope.
* The finder is a token finder. A circuit sentence that names none of its tokens is outside the inventory; V2-SPEC.md
  line 35 was found that way in round 1.
