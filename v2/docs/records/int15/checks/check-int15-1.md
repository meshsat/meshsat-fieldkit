mergeable: no

# AI review: independent check of integration set 14, fnd/int15 at 1f3dd306 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. I did not write any of the work under check. Checked 29
September 2026 from 19:41 to 20:09 CEST (times read with `date`). Everything below is what I read or ran myself.

**Set up**
* Tip clone: `<scratch>/chk-int15`, a shared clone detached at `1f3dd306215f80aa6eb57334fc29db8078ac48ba`, still the
  tip of `fnd/int15` at 20:06. Archive `int15-evidence-1f3dd306.tar` installed: sha256 `74e95c9762a705e1...`, 939
  files, none of them tracked (the four held TI sheets and the thirteen IBIS models among them).
* Main clone: `<scratch>/chk-int15-base`, detached at `b874b744`, with `int14-evidence-a906b932.tar` (sha256
  `dae5201ad41d5dc4...`, 939 files).
* Replay clones (throwaway, in my session scratchpad under `c15/`): `r1` at `853beff6`, `r3` at `9eaf406f`. My helper
  scripts and outputs are there too.
* Every tool ran from a scratch cwd (`env -C`, no `cd`) with `VERDICT_DIR` in the scratchpad. `git status` of both
  check clones is clean apart from this file. No commit, no push, no agent, no other model, no box. The full suite was
  not run.

**Counts: 2 blocking, 8 minor.**

## Blocking items

**B1. CFL-016 reads PASS while five sentences in its own scope name parts that no generator carries.**

CFL-016's acceptance (`v2/ecad/tools/pcb_requirements.yaml` line 13456) is that each named document "describes the
circuit as generated". `s122lib.SCOPE` reads V2-SPEC.md whole and OPERATING-ENVELOPE.md sections 2 to 4. In that scope:

1. **`v2/docs/V2-SPEC.md` line 82 (the B16 row): "the TMDS341A display switch".**
   * No generator has ever carried a TMDS341A: `git log --all -S TMDS341` touches only documents, vendor records and
     `make_handoff.py`.
   * Board B's display switches are `U3` and `U4`, TI TS3DV642A0RUAR, on the set 13 netlist. `gen_sch_b.py` carries the
     TS3DV642 since `273c5431` (7 September, 05:45), and it did so at `b2709118`, the commit that wrote this table.
   * `feasibility/FAILOVER-FABRIC.md` lines 103 to 105 already record the TMDS341A as NOT_FITTED.
   * `verdicts.out` line 2118 judges the sentence NOT DERIVABLE, as HISTORY, under `judgements.py` line 417 (T7, "the
     boards table is headed 'as generated on 7 September 2026', a dated record") and entry `b1e7494b6d` (line 973).
     None of its three assertions is about the display switch.
   * The premise is false for this row. The TMDS341A was never what was generated on 7 September. The row is not a 7
     September record either: `gen_sch_b.py` at `b2709118` holds no TMUXHS4212, TS3USB221A or STM32H7, and the row's
     supervisors' clause states the present (CON-017 PASS).
   * The same table's TPS55288 was corrected in this set (correction 32) on exactly this ground, that it had left
     before 7 September. The TMDS341A is the same class, and it was missed.
2. **V2-SPEC.md line 86 (the E6 row): "the LM5176 9 to 36 V front end".**
   * The LM5176 front end is board A's `U2` ("VBUS20 from VIN_RAW").
   * Board E carries the LM5069MM-2 hot swap `U6`.
   * On 7 September too: `gen_sch_e.py` line 104 at `b2709118` says the bus "climbs the dock contacts into A22's LM5176
     front end".
   * `verdicts.out` line 2144 judges it NOT DERIVABLE under the same T7.
3. **V2-SPEC.md line 47: "Direwolf on the WM8960 codec".**
   * The WM8960 left the design with the D8 generators at `bdfc7b3f` (7 September). Board D's codec is `U6`, TI PCM2912A.
   * The cell is not inventoried: only the row's third cell, "D8, west jack", is judged (`verdicts.out` line 2040).
   * The same cell says the RA30H1317M sheet is "*owed*". OPERATING-ENVELOPE.md section 2 records that sheet as held
     since 27 September.
4. **`v2/docs/OPERATING-ENVELOPE.md` line 77: "TRACO TEN 40-2412WIN | dock strip, inside".**
   * No TRACO part is on any set 13 netlist.
   * `gen_sch_e.py` line 210 (line 107 at `b2709118`) reads "the isolated TRACO converter of E4 is gone".
   * The row was written at `d122a261` (16 September), after that. It is not inventoried.
5. **OPERATING-ENVELOPE.md line 83: "Amphenol M.2 B-key socket", citing `amphenol-mdt420b01001`.**
   * Board B's only B-key socket is `J_M2C2`, TE 2199119-3. It was TE 1-2199119-5 at `d122a261`, when the row was
     written.
   * No generator has ever carried an MDT420B.
   * The row is not inventoried.

*The two causes:*
* The HISTORY judgement of the boards table excuses every part it names without checking any of them at the table's
  own date.
* The finder inventories designators, nets and boards, not makers' part numbers (README lines 242 and 243 say so).

CFL-016's inventory entry (line 14261) nevertheless describes the inventory as every sentence "that names a part".
Its closing entry (line 14320) turns the result to PASS on "no sentence of the five correctable documents ... is judged
to describe a replaced circuit". That is true of the judgements, but not of the documents.

*Why it blocks:*
* CFL-016 is a BLOCKER, and this set turns it from FAIL to PASS on its acceptance.
* Its `prototype_1_why` names exactly this harm: reviewers and the firmware are "written against these contracts".
* The int14 check held set 13 on a false clause that could let CFL-016 close with a stale document. Here it has
  closed with five.

*Fix (either):*
1. Correct the five sentences. V2-SPEC.md takes a correction 34 with the TS3DV642 `U3` and `U4`, the E6 row's LM5069
   `U6` (the LM5176 `U2` on A22), the PCM2912A `U6` on D8 and the held RA30H1317M1 sheet. OPERATING-ENVELOPE.md loses
   the TRACO row and gets TE 2199119 for the B-key row, which needs a re-pin of ENV-001 (no envelope number depends on
   either row: both ranges are wider than the bound).
   Then:
   * judge HISTORY rows' parts at the row's stated date, or re-derive them;
   * inventory makers' part numbers;
   * re-run `inventory.py` and `verdicts.py`;
   * rebind the records bound to the two documents (CFL-010, CFL-013, CFL-014, CFL-016, REQ-005);
   * append to CFL-016 a correcting entry that withdraws the closing entry's claim for these five sentences.
2. Or return CFL-016 to FAIL, waiting on a new S item that names the five sentences and the two causes. S-122 stays
   closed, and a correcting entry on CFL-016 says why.

**B2. CFL-016's PASS rests on three files it is not bound to.**

* `rules_lib.py` line 557: "a desk or physical reading names by content every file it read".
* CFL-016 is DESK_REVIEW. Its closing entry (line 14320) reads CONOPS "through its status page", and it names three
  places:
  * `handover/DEFINITION-STATUS.md` (rows DC-01 to DC-09);
  * `feasibility/EMCON.md` section 0a.1, "which were judged directly";
  * ASSEMBLY.md, one of "the five correctable documents".
* Its `evidence_bound_to` (lines 14335 to 14347) holds none of the three. No record in the registry binds
  DEFINITION-STATUS.md.
* So an edit to a DC row or to 0a.1, the places that now carry the current values of CONOPS's 38 BASELINE sentences,
  leaves CFL-016 reading PASS and current. The same edit to CONOPS.md would be an error under `rules_lib`.
* Fix: bind CFL-016 to `v2/docs/handover/DEFINITION-STATUS.md@2db0ad36da754fa4`,
  `v2/docs/feasibility/EMCON.md@c8eb306265110076` and `v2/docs/ASSEMBLY.md@942d562edd128759`, with an entry saying why.
  Carry the same in `close_s122.py` or its successor.

## What was checked, item by item

### 1. Replays (all byte for byte)

* **`apply_registry_s120.py close 853beff6`** on `r1` at `853beff6`:
  * `--check` writes nothing;
  * the real run closes S-120 by `commit 853beff637b0cd87d30ddab8dfead3e6057d4f23` (40 characters) and opens S-124;
  * a second run refuses ("S-120 is already closed").
* **`apply_registry_s122.py`** on that result:
  * it rebinds 20 records;
  * `pcb_requirements.yaml`, `pcb_envelope.yaml` and `pcb_rules_coverage.yaml` are identical to `9eaf406f`'s;
  * a second run refuses.
* **9eaf406f's pages.** With main's archive installed in `r1`, I ran `rules_render.py --requirements`, `rules_status.py`
  and `rules_render.py`. All nine pages equal `9eaf406f` byte for byte: CURRENT-EVIDENCE.md, the seven PCB-RULE-STATUS
  pages and REQUIREMENTS-TRACE.md. The tenth file, `checks/check-s122-3.md`, equals `<scratch>/chk-s122/CHECK-3.md` byte
  for byte. `check-s122-1.md` and `-2.md` equal `CHECK.md` and `CHECK-2.md` byte for byte.
* **`close_s122.py v2/docs/records/s122/checks/check-s122-3.md`** on `r3` at `9eaf406f`:
  * it closes S-122 "at 9eaf406f" with 862 sentences, 0 STALE and 0 UNJUDGED, re-running and matching both committed
    outputs;
  * the registry is identical to `1f3dd306`'s;
  * a second run refuses.
  * Then `rules_render.py --requirements` gives `1f3dd306`'s REQUIREMENTS-TRACE.md (`rules_lib requirements` reads
    0 errors and 2 warnings there, CON-010 and REQ-044 on the transient page).
  * With the tip's archive, one status run and one render give `1f3dd306`'s CURRENT-EVIDENCE.md.
* **The merges.** Both are exact `git merge-tree` results, trees `280611d3` and `fe4f2158`. `fnd/s120` and `fnd/s122b`
  are still at the checked tips `1561ff88` and `d38c6b4d`.

### 2. Registry, parsed, main `b874b744` against the tip

* **Top level:** only `needs_document_sha256` moves, from `3c5d4907...` to `6cb7b241...`, which is c5430071's CONOPS.
  CONOPS's diff starts at line 315, after the needs table (lines 75 to 145).
* **Records:** 144, same order. 21 records change, every old evidence list kept as a prefix.
  * 20 rebinds: REQ-005, CFL-001, REQ-012, CON-018, REQ-030, REQ-071, REQ-032, CFL-005, CON-010, CON-021, FEA-002,
    REQ-050, CFL-016, CFL-007, CFL-008, CFL-009, CFL-010, CFL-013, CFL-014 and CFL-015. They take 28 entries, one per
    document, and only `evidence` and `evidence_bound_to` move.
  * REQ-015: `waits_on` goes from S-106, S-107, S-111, S-120 to S-106, S-107, S-111, S-124.
  * CFL-016: FAIL to PASS, `waits_on` [S-122] dropped, evidence +9 (five rebinds, the inventory, the baseline rule,
    the n1 and n2 correction, and the closure). Its bindings move on five documents.
  * No other result moved.
* **Items:**
  * Open items go from 86 to 85. S-120 and S-122 leave. S-124 takes S-120's place (line 3547; SESSION, OPEN). S-111's
    title gains S-120's residual, its old title kept as a prefix.
  * Closed items go from 67 to 69: S-122 first (line 3600, m3) and S-120 last (line 4414).
  * S-123 is identical and still open. S-122 was closed with its title extended by the n3 and n4 sentence, which
    matches check-int13-4's fixes.
* **S-124 as written.** Its closing condition equals the s120 README's quotation (section 7) word for word. Its
  figures come from `vbus20_bound.FIG`, and the `.out` reprints at the tip, so they are the committed ones: 23.40 V,
  Q7 5.60 V, Q8 6.60 V, and 8.04, 9.04 and 3.0 V over the steady bus.
* **The rebind reasons** are what the script computes from the diff, the verdict files and each record's text, and my
  replay reproduces them. I read five in full (REQ-005, CON-010, CON-018, CFL-010, CFL-015).
  * They are true as mechanical statements, and each says it "does not re-read the rest of this record's argument".
  * For the PASS records whose named places changed, I checked the one that looked at risk. CFL-014 rests on CONOPS
    section 4's Charging row, and the CONOPS diff does not touch it. No result is at risk from the rebinds themselves.
  * The printed name lists are truncated (m6).
* **CFL-016's entries:**
  * The n1 and n2 correction and S-122's n3 and n4 sentence match check-int13-4 lines 102 to 104.
  * The baseline entry (line 14289) states CONOPS's rule (CONOPS.md lines 11 to 16) and the restore correctly.
  * The inventory entry's "names a part" overstates the finder (B1).
  * The closing entry: B1 and B2.

### 3. CFL-016's PASS on its own acceptance, and the sample

**Reading CONOPS through its status page.**
* It fits the H2 rule's words:
  * review section 4 (line 104): "A new circuit correction or changed count should update its engineering/status record";
  * CONOPS.md lines 11 to 16: a figure or "as generated" remark "is its value when this document was baselined; its
    current value is kept where the list below says".
* DC-01 keeps EMCON in EMCON.md 0a, as the head's list says, and DC-02 keeps HOT-R1 with REQ-077.
* DC-03, DC-04 and DC-07 say openly that the baseline was wrong when written, which the rows mark as such.
* Against CFL-016's acceptance it holds only under the reading its baseline entry records. The acceptance text is
  unchanged, and read literally it is not met by the 38 BASELINE sentences (m7). With B2 unbound, that reading is also
  unguarded.

**The sample against the set 13 netlists** (parsed with `tx_inhibit.parse_netlist`; generator lines read at the commits
cited):

* **PANEL.md, 20 sentences, all true.**
  * Section 1's EMCON row: `U9` 74LVC1G17, `R52` 330R and `D23` BAT46W; `R14` 2.2k and `R50` 10k; `U13` and `R46` to
    GPIO 21; `U14` SN74LVC1G57, `Q7`, `R47` and `D22` from `LED_RAIL_SW`.
  * Section 3's rows GPIO 2 to 7 through `R53` to `R56` 27R, and GPIO 20 `SHORE_INHIBIT` (section 10).
  * Section 6's two rows:
    * `C24`, and the 100k pull downs on A, B and D;
    * `U35` to `U38` on `+3V3_EMCON`, and `U26` now the outlet interlock (`gen_sch_a.py` 1572 to 1575 at `e57a7365`,
      1102 at `45bde541`);
    * `R58` 4.7k and `R102` 10k;
    * `U501` to `U505`, `U536` with `R532` and `U543`, `U112` to `U116` and their slot 2 and 3 twins, `U220`,
      `Q212` with `R295` 15R, and `U506`;
    * `U537` to `U539`, `U544` to `U550`, `U553`, `U540` to `U542`, and `R536` and `R537` to `+3V3_ZB`.
  * Section 7: `U6` carries `RB_SW_IEN` and `RB_CTRL_H`; `R102`, `R58`, `R145`, `R59`, `R2`, `R117` and `R118`.
  * Section 10: `R26` 13.3k over `R27` 40.2k, `R17` and `F1`.
* **V2-SPEC.md, 16 sentences, 3 false** (B1 items 1 to 3).
  * True:
    * the KSZ9897R `U1`;
    * the DS3231SN `U9` on `SDA` and `SCL`;
    * the cooler fans from `U30A` Fan_PWM, and E's mixer fans through `Q9` and `Q10` from `U10`;
    * `U7` and `U25`;
    * `U536` and `U543`;
    * `J_M2C2` TE 2199119-3 with the `U222` and `U223` arrays, and two SIM holders;
    * A22's TPS25740A `U18` with LM5176 `U19`, and eleven Radiall sites;
    * B16's PI7C9X2G404, TUSB8041, TMUXHS4212 and TS3USB221A, and three STM32H743;
    * the D8 row's parts;
    * the B16 row's DS3231M, true as 7 September history (`gen_sch_b.py` at `b2709118`).
* **OPERATING-ENVELOPE.md, 15 sentences, 2 false** (B1 items 4 and 5).
  * True:
    * board P's `F2`, `U1` and `U2`;
    * the two AW7915 cards in slots 1 and 3;
    * the LimeSDR on `J_LIME`;
    * the SGP41 `U17` on E;
    * the RM520N-GL, E22, E72 and LG290P rows;
    * section 3's BQ4050 and BQ7720700;
    * HOT-R1 (`Q11`, `U27`);
    * the LT8705A `U5`;
    * the USB-C row;
    * EMCON on the PA bias (D's `U15` on `PA_KEY`);
    * the RockBLOCK ENABLE (`U536`).
* **TEST-PLAN.md, 12 sentences, all true:** `U1`, `Q1`, `Q2`, `U2` BQ7720700 with COUT through `R29`, `JP1` and `Q3`
  to `F2`, `Q5` from DOUT, `J_TS2`, `F1`, line 90's list, `J_BATT` and `J_SMB`, `J_TS` pins, HOT-R1 on A and E, and
  the second level since `faf8c981`.
* **ASSEMBLY.md, 16 sentences, all true:**
  * seventeen 0858 pins (`J_CP1` to `J_CP4`, `J_CN1` to `J_CN4`, `J_PRE1`, `J_VR1` to `J_VR4`, `J_VN1` to `J_VN4`),
    and `J_PRE1` through `R1` 10R;
  * eleven Radiall;
  * P's and E's `J_SMB` pin orders;
  * `J_5V_DEV` at both ends;
  * `J_USBC_OUT` with `U31`;
  * `J_USBW` with `U32` and `J_AB2`;
  * `J_HEAT`, `U33` and `U22`;
  * `J_TAMP`;
  * `J_WOA` and `J_WOB` through `U82` and `U83` to `J_RF6` and `J_RF7`;
  * `J_DOCK`'s twelve pins;
  * step 3's `U35` to `U38`, and `R102` and `R145` at `gen_sch_a.py` 1597 and 1598 at `e57a7365`;
  * C7's seventeen 3 mm LEDs (`D1` to `D16`, `D22`);
  * B16's two WiFi cards.
* **DC rows, 9 of 9 true:**
  * DC-01 (`U536`, `U543`, `U537` to `U553`, `U116`, `U216`, `U316`, `U35` to `U38`);
  * DC-02 (`Q11` gate `HOT_R1_G` from `U10` pin 30, `R58`, `J_BLK` pin 12, and on A `J_DOCK` pin 12, `R216` and
    `U27` pin 18);
  * DC-03 (`D3` through `R36` from `LED_RAIL`, which is `Q1`'s drain; `Q2` pulls `Q1`'s gate through `R18`, and `PANEL_PWM`
    (GPIO 8) drives `Q2` through `R19`);
  * DC-04;
  * DC-05 (`U112` on `+3V3_CM1`);
  * DC-06 (all ten generator citations at `e57a7365`);
  * DC-07 (`U41`, `U51`, `U61` pins 92 and 93 on `SCL` and `SDA`, which reach `J_PANEL`; no TCA9517A);
  * DC-08 (`R191` and `R192`, `U513` to `U520`, `U530` to `U535`);
  * DC-09 (`U31` on `PD_CC1` and `PD_CC2`, `J_USBC_OUT` pins 2 and 3).

### 4. CONOPS

`v2/docs/CONOPS.md` at the tip equals `git show c5430071:v2/docs/CONOPS.md` byte for byte (sha256 `6cb7b241cb84d729...`).
Its sha256 equals `needs_document_sha256`.

### 5. Pages and readings

* **`rules_status.py`, three times at the tip:**
  * exit 1 each time, with identical stdout: FAIL of 338 (PASS 195, INCONCLUSIVE 104, FAIL 39), NOT_READY;
  * the three audits are identical once time fields and the clone path are set aside, and run 1 equals the archive's
    audit (only `git_head` and `version` differ in the status verdict);
  * main's run in the base clone gives the same stdout.
* **`rules_render.py`, twice:** exit 0, nothing written, `git status` clean.
* **Checks:**
  * `--check`: 16 documents, 0 out of date;
  * `--requirements --check`: current;
  * `decisions_render.py --check`: exit 0;
  * `constraints_bound.py`: PASS;
  * `claims_check.py` (scratch `VERDICT_DIR`): PASS of 91.
* **The evidence page:** CURRENT-EVIDENCE.md at the tip is sha256 `c9b98931...`, main's. The PCB-RULE-STATUS pages
  differ from main only in ENV-001's line (sha 43361b02 to a8e65995), 7 of 7.
* **The explanation of `9eaf406f`'s page is right.**
  * `rules_status.CONFIG_INPUTS` (line 815) declares `tools/pcb_rules_coverage.yaml` for `rules_status.py`.
  * `_config_state` (lines 1123 to 1163) counts an uncommitted copy as changed (line 1151), and also a copy committed
    after the reading (line 1154). The rules_complete reading records no sha for it.
  * With the coverage file re-pinned and uncommitted, SGN-001 reads AWAITING_REVALIDATION (CONFIG_CHANGED) on all
    seven boards, its result still PASS. That moves 7 pairs from CURRENT_CANDIDATE and adds the CONFIG_CHANGED row.
    My replay reproduced that page exactly.
  * The tip's archive holds a rules_complete reading at 17:37:18Z. The coverage file was committed in `9eaf406f` at
    17:35:57Z, so the reading is current and the page returns to main's.
  * `9eaf406f`'s message words it wrongly (m1).
* **Readings, main against the tip:**
  * 339 rule and board rows: 0 results moved, 0 evidence classes moved.
  * Beyond ENV-001's sha, the audits differ only in SGN-001's `writers` (rules_render.py on main's first run against
    rules_status.py). That self reference predates this set.
  * Of the archives' 939 files, 930 are byte identical, the routed and unrouted readings among them. The nine that
    differ are the seven audits, the status verdict and `rules_complete` (PASS of 339 in both; writer, head and time
    differ).
  * No routed or schematic verdict changed.
* **Validators:** `rules_lib.py` 59 rules, 0 errors, 0 warnings; `rules_lib.py requirements` 144 records, 0 errors,
  0 warnings.
* **Tests:** test_requirements 66, test_rules_registry 5, test_decision_register 5 and test_envelope_data 6, which is
  82 passed and 0 failed.

### 6. Every changed file

`b874b744..1f3dd306` changes 44 files, each within its commit's stated scope:
* `7ef14d42`: the six `records/s120/` files.
* `853beff6`: the eight documents (ASSEMBLY, CONOPS, OPERATING-ENVELOPE, PANEL, TEST-PLAN, V2-SPEC, EMCON.md and
  DEFINITION-STATUS.md) and eighteen `records/s122/` files, exactly `b874b744..d38c6b4d`.
* `9eaf406f`: the nine pages, `check-s122-3.md`, and the envelope, requirements and coverage files.
* `1f3dd306`: CURRENT-EVIDENCE.md, REQUIREMENTS-TRACE.md and the requirements file.

The 29 commits all carry the owner's identity as author and committer and `[MESHSAT-1357]`, with no trailer. There is
no em or en dash in added text or in messages. No vendor, held, IBIS or Claude file is committed.

## Minor items

* **m1.** `9eaf406f`'s message says "The evidence and status pages moved only in ENV-001's verified sha". CURRENT-EVIDENCE.md
  also moved in SGN-001's seven rows, the count table and a CONFIG_CHANGED row. The message also says CON-010 and
  REQ-044 are "rebound after S-122's closure"; they were not rebound, because the page returned to `c9b98931`. It
  omits S-111's title addition. `1f3dd306`'s message states the page correctly. Fix: one line in the set's record.
* **m2.** S-120's closing evidence (registry line 4418, from `apply_registry_s120.py` line 155) says "third issue after
  the checks of stream s120". The merged records are the fourth issue (s120 README lines 9 to 11; the `.out` header).
  Fix: a correcting sentence at the next registry pass.
* **m3.** `close_s122.py` line 131 puts S-122 at the head of `closed_items` (line 3600). S-120 here, and S-119 and S-121
  in set 13, are appended at the end, so REQUIREMENTS-TRACE.md lists S-122 first. Fix: append at the end.
* **m4.** check-s122-3's minors are neither answered nor carried.
  * m1: CONOPS.md line 1056 (section 7, D-13) still says "the STM32H753 in the schematic", with the mismatch still to
    close, and has no DC row.
  * m2: the absent rule's four words.
  * m3: the README's CON-003 quote.
  * Fix: a DC row like DC-09, or an S item, and a README line.
* **m5.** The four checks of stream s120 are cited as `<scratch>/chk-s120/...` (s120 README lines 9 to 11; LOG lines 40,
  70 and 93), which is outside the repository. They are not filed under `records/s120/checks/`. `records/README.md` has
  no rows for `s120/` or `s122/`. Fix: file the checks and add the rows.
* **m6.** The rebind entries print at most 15 of the names they count: CON-010 says "names 23 of them" and lists 15,
  and CFL-015 does the same with 19 (`apply_registry_s122.py` line 252). Board names (`C7`, `D8`) are counted as
  parts. Cosmetic.
* **m7.** CFL-016's acceptance (line 13456) is unchanged. The rule that CONOPS is read through its status page lives
  only in an evidence entry (line 14289). Fix: record it on the record as a SESSION ruling or a note, with the status
  page named.
* **m8.** In `pcb_rules_coverage.yaml`, ENV-001's `_maturity_ruled` still ends "re-pinned 27 Sep 2026", while
  `verified_on` reads 2026-09-29. Cosmetic.

## Counts

* **Items:** blocking 2 (B1, B2); minor 8.
* **Replays:** 15 of 15 files byte for byte:
  * 3 registry files and 9 pages of `9eaf406f`;
  * 3 files of `1f3dd306`;
  * plus the filed check.
  * Every script refuses a second run. Both merges are exact.
* **Registry:** 21 records changed; 1 result moved (CFL-016, FAIL to PASS); S-120 and S-122 closed; S-124 opened;
  S-123 unchanged; REQ-015 waits on S-106, S-107, S-111 and S-124.
* **Sample:** 79 sentences in the five documents, with 5 false (all in scope, none judged STALE); DC rows 9 of 9 true.
  CONOPS equals `c5430071`.
* **Readings:** 339 rows, 0 results moved, 0 classes moved; 930 of 939 archive files identical, the 9 others explained.
* **Validators:** 0 errors, 0 warnings. Renderers current. `claims_check` PASS of 91.
* **Tests:** 82 passed, 0 failed.
* **Files:** 44 changed, all explained.
