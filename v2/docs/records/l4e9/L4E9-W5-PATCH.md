**DONE:** W5's findings W5-F1 to W5-F3 and W5-D1 (queue rows Q-22 and Q-23) written as 27 exact rows for the coordinator: the three verbatim l8p inputs with their diffs against W5's files, both digests, the re-take and what pins them (WP-01 to WP-06), the release companions in the generator's change list, the page and the register (WP-07 to WP-21), R-208's stale section (WP-22), and the docstring rows with every file that pins each draft (WP-23 to WP-27). **NOT DONE:** nothing applied: L4-E9's page, register, generator, output and inputs are the integration's files, the drafts are records l8p's and l4e11's; no generator, regen_out, capture or suite was run. **NEXT:** the coordinator applies sections 3 to 5 in the next set after `fnd/w5l8p` is merged, and section 6 only with the next circuit change to those drafts.

# W5's findings on L4-E9's side: the patch for the coordinator (W13, MESHSAT-1357, 6 October 2026)

**What this is.** Exact text corrections to L4-E9's generator `v2/docs/records/l4e9/l4e9_power_path.py`, its page `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` and its register `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`, the re-take of three copies in `v2/docs/records/l4e9/inputs/`, and five docstring rows in drafts of records l8p and l4e11, written by worker W13 on branch `fnd/w13l4e9` from W7's tip `3e566c551498f66bda0c092581ce71016ea9bd30` (set 30's integration commit 2c `53a68c7c` plus W7's two patch files). Every file a row names is byte for byte the same at the integration's committed `6bc4424e` (read with `git diff --stat`); the integration's uncommitted regenerated outputs of 2b were not read. No file a row names is edited here. The rows restate record text and bindings; none designs anything, computes a figure, changes a predicate, a pin's meaning or a verdict, or consumes a review. Prototype framing: nothing in the kit is built, bought, powered or measured.

**The findings it answers**, as W5 filed them on `fnd/w5l8p` at `cd19df597350b8f56b78fc172e6966e78dba8049`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14 (lines 1592 to 1665), and as the queue carries them (Q-22: "the L4-E9 verbatim inputs `records/l4e9/inputs/l8p-*-515f6cf2.txt` still read LM5069MM-2 (a re-take of the inputs); the change-list order data and R-246 name fewer release companions than six; R-208's row cites a stale section (W5-F1)"; Q-23: "the board A and E drafts' docstrings and record l4e11's DD-7 draft line 50 name only round 1's release companions (W5-F2, W5-F3); the breaker draft's lines 55-56 (W5-D1)").

## 1. How to apply

- **Order of adoption.** Apply nothing here before `fnd/w5l8p` (`cd19df59`) is merged: every row cites record l8p's section 6 item 1 as W5 restated it ("One release for the six drafts", lines 266 to 289); at the base that item still reads "One release for the five drafts".
- **Section 3 (WP-01 to WP-06)** together, in one commit with the re-take of section 2: the three new copies written, the three old ones removed, the three pins and the three From cells changed.
- **Sections 4 and 5 (WP-07 to WP-22)** together in one commit: each generator row WP-07, 09, 11, 13, 15, 17 with its page row WP-08, 10, 12, 14, 16, 18 (test_l4e9 line 1169: "the page's change list is the script's"); the register rows WP-19 to WP-22 beside them. Sections 3 to 5 may share that commit.
- **Then regenerate** `l4e9_power_path.out` through `_bin/regen_out.py <worktree> v2/docs/records/l4e9/l4e9_power_path.py v2/docs/records/l4e9/l4e9_power_path.out` (its R4 binds the three new copies' printed pins). What moves in the output: lines 52 to 54 and 2299 to 2301 (the copies' names and sha256/16, section 2) and the change list's rows 32, 34, 35, 66, 92 and 93 (lines 1343, 1345, 1346, 1377, 1403 and 1404 at the base, section 17); no figure, count or verdict line. The page's section 3 table is hand text held equal to the script by the test, so WP-08 to WP-18 are its edit.
- **Readers of the changed files by path** (the coordinator's usual re-pin step at the freeze; at the base no committed file carries the current sha256 of the page, register, generator or output, by a 16-hex search): `v2/docs/records/l4e11/l4e11_power.py` (pins `arch` and `l4e9`), `v2/docs/records/l4e10/l4e10_cell_thermal.py`, `v2/docs/records/l5pwr/l5pwr_contracts.py`, `v2/docs/records/l4close/verify_risks.py`, and `v2/docs/records/l9t5/apply_l4e9_changelist_p0.py`, whose applied-state reader tests the presence of its rows by id only (its lines 117 to 122), so the changed texts of R-222 and R-244 do not refuse it.
- **Section 6 (WP-23 to WP-27) ONLY WITH THE NEXT CIRCUIT CHANGE TO THESE DRAFTS:** each is a docstring of a draft pinned by sha256 down to record l9t5's stability digests (the tables of section 6 list every pin); W5's SESSION decision W5-D1 left them for that reason, and this file keeps it.
- The module `v2/ecad/tools/tests/test_w13l4e9.py` holds every row: its Old text where the row says at the base (or every New text once applied, never half), the copies' digests and diffs recomputed, the re-taken bytes still meeting the generator's two checks on a copy, each generator row equal to its page cell on both sides, the six companions as W5's section 6 item 1 table names them, R-208's citations read at both commits, the docstring rows changing nothing but a docstring, and every listed pin line read.

## 2. The verbatim inputs (W5-F1's PC-04 part; Q-22's first item)

**W5's words** (`fnd/w5l8p` `cd19df59`, `L8P-BREAKER.md` lines 1621 to 1625): "**The copies that name the -2 for U101 are L4-E9's, not this folder's:** `v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-515f6cf2.txt` (round 1's bytes: U101 as the -2 at its lines 10, 61, 65, 90, 113 and 175) and `.../l8p-apply_gen_sch_a_ptc-515f6cf2.txt` (line 45); the third, `.../l8p-apply_gen_sch_e_enable-515f6cf2.txt`, names no LM5069. They are verbatim copies pinned by L4-E9's generator (`l4e9_power_path.py` lines 109 to 111): rewriting one would falsify a copy, so they stay as they are; R-206's From calls them superseded (the register's line 302) and their re-take is the coordinator's (PC-04; SET31-CHANGES.md lines 118 to 119)." Read here: each copy is byte for byte its draft at `515f6cf2` (`git show`), and the LM5069 lines W5 names are the copies' only LM5069 lines.

**The re-take: no capture script exists.** Record l4e9's folder holds one fetch script, `fetch_held_back.py`, which downloads the Littelfuse 0997 sheet into the ignored `v2/vendor/power/held/` and never writes `inputs/`; the three copies entered with round 8's commit `5eb6e74f` (4 October 2026) as plain files with no script committed (`git show --stat 5eb6e74f`), and at the base no file names them by file name outside the generator and its output. The coordinator's set 30 re-pin tool (`repin_l4e9.py`, outside the tree) re-pins a pin to the bytes at the SAME path, so it cannot rename a copy. The re-take is therefore the round 8 method by hand, for each copy (never run here; `<wt>` the integration worktree):

```text
git -C <wt> show 6eeb6cfe:v2/docs/records/l8p/apply_gen_sch_p_breaker.py > <wt>/v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-6eeb6cfe.txt
git -C <wt> show 69b8c3bb:v2/docs/records/l8p/apply_gen_sch_e_enable.py > <wt>/v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_e_enable-69b8c3bb.txt
git -C <wt> show 8e6a938c:v2/docs/records/l8p/apply_gen_sch_a_ptc.py > <wt>/v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_a_ptc-8e6a938c.txt
git -C <wt> rm -q v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-515f6cf2.txt
git -C <wt> rm -q v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_e_enable-515f6cf2.txt
git -C <wt> rm -q v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_a_ptc-515f6cf2.txt
```

then WP-01 to WP-06 and the regeneration of section 1. **SESSION decision W13-D1** (authority: SESSION, under the owner's standing rule of 26 September 2026): each new copy is named after the commit that last changed its draft's bytes (`git log -1` on the draft: `6eeb6cfe`, `69b8c3bb`, `8e6a938c`, each an ancestor of `6bc4424e` and of `cd19df59`, where the bytes are the same), as round 8 named its copies after the commit they came from. Reason: the name then says where the bytes can be read again. To reverse: name all three after the integration commit of the re-take and change WP-01 to WP-03's paths to match.

**What pins the copies.** By digest, only the generator's PINS lines 109 to 111 (WP-01 to WP-03), printed again by its output at lines 52 to 54 and 2299 to 2301 on regeneration. The page names neither the copies nor their digests. The register names them by commit, not digest, in the From cells of R-206 to R-208 (WP-04 to WP-06). No test pins them: `test_l4e11.py` line 1056 pins `c8e4eeb499491eab...` for `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` read at record l8p's commit `b1295c1e` that L4-E11's round 9 names (`R9_COMMITS`, `l4e11_power.py` line 3228), the same bytes as the PTC copy, and is untouched by the re-take; `test_l4e9.py` line 418 accepts a copy under `inputs/` only for a board E draft that is not in the tree, and the tree holds record l8p's. **What the generator reads from a copy** (lines 5309 to 5315): a draft marker in its first 3000 characters (`NOT\s+APPLIED|DRAFT\s+for\s+the\s+integrator`) and its target's name; W5's bytes carry both (the test reads them), so the re-take adds no refusal and moves no figure.

#### The copy `v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-515f6cf2.txt`

- The base copy: sha256 `ddc7258038c86b6ad03416dafcaab68bb8133cb25540b7fb2cba1263874ff541` (the generator's pin `l8p_breaker`, line 109); round 1's draft at `515f6cf2`, byte for byte.
- W5's file: `v2/docs/records/l8p/apply_gen_sch_p_breaker.py` at `cd19df59`, sha256 `e8f1294bb0f76c75d146332e41d3783256474804905faa296bcdca8bc0cf2693`; the same bytes at `6eeb6cfe` (its last change), at the base and at `6bc4424e`.
- The copy's LM5069 lines: 10, 61, 65, 90, 113, 175.
- The re-taken copy: `v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-6eeb6cfe.txt`, sha256 `e8f1294bb0f76c75d146332e41d3783256474804905faa296bcdca8bc0cf2693`.
- The lines that differ (unified diff, three lines of context, 342 lines):

```diff
--- a/v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-515f6cf2.txt
+++ b/v2/docs/records/l8p/apply_gen_sch_p_breaker.py@cd19df59
@@ -1,40 +1,58 @@
 #!/usr/bin/env python3
-"""apply_gen_sch_p_breaker.py: DRAFT for board P's generator owner (Layer 8 record l8p, MESHSAT-1357, 4 October 2026). NOT
-APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).
-
-The defect: W4DP-F2 (record l9stk section 15, DD-1 and DD-6, on branch fnd/l9stk at 2c8b29fb, independently checked
-CONFIRMED AS CONDITIONAL). With board P's FETs Q1 and Q2 welded and no firmware, nothing on this board opens the discharge path
-on current alone (l9stk 15.2), and a docking with a breaker that is already on reaches E11-30's 242.9 A (15.4, B-P1).
+"""apply_gen_sch_p_breaker.py: DRAFT for board P's generator owner (Layer 8 record l8p, MESHSAT-1357, 4 October 2026; round 2
+of the same day). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).
+
+The defects: W4DP-F2 (record l9stk section 15, DD-1, DD-6 and DD-8, branch fnd/l9stk at 0d72880b; its latest changes checked
+CONFIRMED AS CONDITIONAL). With board P's FETs Q1 and Q2 welded and no firmware, nothing on this board opens the discharge path on
+current alone (15.2); a docking with a breaker already on reaches E11-30's 242.9 A (15.4, B-P1); and a hot restart of the latching
+breaker into the worst resistive fault reaches 0.82 of the FET's derated SOA (15.4b, B-R1, DD-8).
 
 The correction drawn here, every value from record l9stk by its section (the record page's section 2 lists each with its source):
-  C-1 (15.4)    U101 LM5069MM-2 (C111822, board E's U6 part) from Q2's source, the new net BRK_VIN, to the pack terminal PACK_P;
-                the sense pair R101 4 mOhm and R102 7.5 mOhm in parallel (1 %, at most 50 ppm/K); Q101 and Q102 CSD18510Q5B
-                (C2876544, board A's PA stage part) from BRK_SNS to PACK_P; R103 RPWR 8.45 kOhm; C101 timer 10 nF; C102 dv/dt
-                22 nF on the gate; D101 SMCJ18A (C374030, board A's VBAT clamp part) on BRK_VIN; OVLO, the controller's ground,
-                the clamp and the small parts on PACK_N (IF-6).
+  C-1 (15.4, 15.4b)  U101 LM5069MM-1, the latch-off variant (the -2's retry overheats its own FET under a persistent fault, 15.4b;
+                the family and the VSSOP-10 land of board E's U6; the -1's order code is Layer 6's to file, owed) from Q2's source,
+                the new net BRK_VIN, to the pack terminal PACK_P; the sense pair R101 4 mOhm and R102 7.5 mOhm in parallel; Q101 and
+                Q102 CSD18510Q5B; R103 RPWR 8.45 kOhm; C101 timer 10 nF; C102 dv/dt 22 nF; D101 SMCJ18A on BRK_VIN; OVLO, the
+                controller's ground, the clamp and the small parts on PACK_N (IF-6).
   C-1b (15.4)   the make-last enable LOOP into UVLO with its RC hold: R106 10 kOhm from BRK_VIN onto J_SMB pin 7 (DOCK_EN_OUT),
-                out over board E and the dock to board A's thermal guard RT1 and back on J_SMB pin 5 (DOCK_EN_RET) into R107
-                22 kOhm on the first inverter Q103 (2N7002); Q103 holds the second inverter Q104's gate, R108 and R109 1 MOhm
-                each from BRK_VIN (l9stk_protection.py's R_G, prot 3a), low; Q104 discharges UVLO through R105 150 ohm; R104
-                200 kOhm from BRK_VIN and C103 3.3 uF 50 V make the RC hold. J_SMB pin 6 is the ground contact between the two
-                loop conductors (C2), J_SMB a JST-XH 1x7 (pins 1 to 4 unchanged).
-  IF-6          the gauge's PACK and VCC taps R6 and R7, and Q2's gate-source resistor R19, follow Q2's source to BRK_VIN; D1
-                stays on PACK_P; VCC_F is fed from BRK_VIN.
+                through board E, the dock and board A's thermal guard RT1 and back on J_SMB pin 5 (DOCK_EN_RET) into R107 22 kOhm on
+                the first inverter Q103; Q103 holds the second inverter Q104's gate (R108, R109 1 MOhm, l9stk_protection.py's R_G)
+                low; Q104 pulls UVLO DIRECTLY. The hold: R104 200 kOhm from BRK_VIN charges C103 3.3 uF 50 V on the node BRK_H, which
+                reaches UVLO through R105 150 ohm and D102 1N4148W, so C103 drains behind Q104 and the turn-off is 0.41 ms; the
+                release 0.110 to 0.907 s after the enable mates. J_SMB pin 6 is the ground between the loop conductors (C2).
+  C-1c (15.4b)  the restart inhibit on the breaker pad (DD-8): RT101, Murata NXRT15XH103FA1B010, bonded on the breaker FETs' pad
+                (10 mm leads to two lands), under R110 150 kOhm from BRK_VIN; a ratiometric reference R111 147 kOhm over R112 1.62
+                kOhm (1653.06 ohm equivalent, the trip's 1653); U102, a zero-drift OPA187 used as the comparator, with R113 15 MOhm
+                of hysteresis; it pulls UVLO through Q105 only while PGD is low (Q106 holds Q105's gate low while PGD is high), so it
+                never turns off a running breaker. Window: allow from 77.25 C, block from 83.20 C, trip 80.22 C +-2.97 K.
+  IF-6          the gauge's PACK and VCC taps R6 and R7, and Q2's R19, follow Q2's source to BRK_VIN; D1 stays on PACK_P.
+  B-R2 (route R1, record l8p round 3; L4-E11 19h): THE REVERSE-CHARGE DETECTOR. While the breaker is off (latched, holding or
+                guard-tripped) a source on board A can push a charge backwards through Q101's and Q102's body diodes, and
+                nothing on board A could tell that from a running breaker (PGD reads good with VDS negative). U103 (OPA187)
+                reads the charge into the cells on the gauge's own sense R10 (its cell side through R120 against R118 1.15
+                MOhm over R119 200 ohm from BRK_VIN through R129 under D103's BZT52C12: 0.368 A at least, 1.213 A at most);
+                U104 (OPA187) reads the body diodes conducting (PACK_P over R121 and R122 against BRK_SNS over R123 and R124:
+                PACK_P above BRK_SNS by 0.044 to 0.268 V); both high turn Q107 and Q108 on in series and hold the loop's
+                return DOCK_EN_RET low, which the existing contact J_DOCK pin 3 carries to board A (its charge inhibit sets,
+                L4-E11's to draw) and which resets the -1 as an undocking does; the restart then has no forward current. C107
+                and C108 the bypass, C109 and C110 the filters, R125 to R128 halve the outputs for the 2N7002 gates, TP107 and
+                TP108 (E-12c).
 SESSION choices (under the owner's standing rule of 26 September 2026; L8P-BREAKER.md section 3): the designators (the free
-100 block: U101, Q101 to Q104, D101, R101 to R109, C101 to C105, TP101 to TP104), the net names, J_SMB's pin assignment, the
-input bypass at the sense pair (TI SNVS452G section 10 and 11.1.1) as C104 and C105, 2.2 uF 50 V in series (board P's own O-12
-rule for a part across the pack), PGD left open, the four test points for E-12.
+100 block), the net names, J_SMB's pin assignment, the input bypass C104 and C105 in series, the four E-12 test points; in round 2
+the comparator part (OPA187, its held sheet read for its offset over temperature), the reference values 147k and 1.62k, the
+hysteresis resistor, the PGD gating pair Q105 and Q106 with R114 to R117, C106, TP105 and TP106 (E-12b), the NTC's lead lands;
+in round 3 the reverse-charge detector (B-R2, route R1): U103, U104, Q107, Q108, D103, R118 to R129, C107 to C110, TP107, TP108.
 
 What it changes in v2/ecad/tools/gen_sch_p.py, and nothing else:
   1. PACK_P's declaration: the breaker's output (loads Q101 and Q102, switch U101 on BRK_UVLO); BRK_VIN and BRK_SNS declared as
      segments of PACK_P (BRK_VIN switched by the gauge as PACK_P was);
   2. R6 and R7 on BRK_VIN;
   3. Q2's source and R19 on BRK_VIN;
-  4. the breaker and the enable loop drawn before the pack leads W_P and W_N, with their node declarations;
+  4. the breaker, the enable loop, the hold, the restart inhibit and the reverse-charge detector drawn before the pack leads W_P
+     and W_N, with their node declarations and C106's, C107's and C108's decoupling entries;
   5. J_SMB a 1x7 with the loop on pins 5 and 7 and the return on pin 6 (no order code: the 7-way code is Layer 6's, L8P-06);
   6. VCC_F fed from BRK_VIN;
   7. one schematic section for the new parts.
-Order (L8P-BREAKER.md section 4): released together with apply_gen_sch_e_enable.py and apply_gen_sch_a_ptc.py (never alone:
+Order (L8P-BREAKER.md section 5): released together with apply_gen_sch_e_enable.py and apply_gen_sch_a_ptc.py (never alone:
 J_SMB's two ends and the dock's two ends must change together), with l6r2's two board P drafts in either order.
 
 Usage:  apply_gen_sch_p_breaker.py TARGET [--check | --write]     (default --check: nothing is written)
@@ -49,20 +67,25 @@
 import sys
 
 NAME = "apply_gen_sch_p_breaker"
-ADDS = ("U101", "Q101", "Q102", "Q103", "Q104", "D101", "R101", "R102", "R103", "R104", "R105", "R106", "R107", "R108", "R109",
-        "C101", "C102", "C103", "C104", "C105", "TP101", "TP102", "TP103", "TP104")
-NETS = ("BRK_VIN", "BRK_SNS", "BRK_GATE", "BRK_TMR", "BRK_PWR", "BRK_UVLO", "BRK_G2", "BRK_DIS", "BRK_CMID", "DOCK_EN_OUT", "DOCK_EN_RET")
+ADDS = ("U101", "U102", "Q101", "Q102", "Q103", "Q104", "Q105", "Q106", "D101", "D102", "RT101", "R101", "R102", "R103", "R104",
+        "R105", "R106", "R107", "R108", "R109", "R110", "R111", "R112", "R113", "R114", "R115", "R116", "R117", "C101", "C102",
+        "C103", "C104", "C105", "C106", "TP101", "TP102", "TP103", "TP104", "TP105", "TP106",
+        "U103", "U104", "Q107", "Q108", "R118", "R119", "R120", "R121", "R122", "R123", "R124", "R125", "R126", "R127", "R128",
+        "C107", "C108", "C109", "C110", "TP107", "TP108", "R129", "D103")
+NETS = ("BRK_VIN", "BRK_SNS", "BRK_GATE", "BRK_TMR", "BRK_PWR", "BRK_UVLO", "BRK_G2", "BRK_H", "BRK_HD", "BRK_PGD", "BRK_CMID",
+        "INH_NTC", "INH_REF", "INH_OUT", "INH_G", "DOCK_EN_OUT", "DOCK_EN_RET", "REV_ISNS", "REV_IREF", "REV_IOUT", "REV_IG",
+        "REV_VP", "REV_VN", "REV_VOUT", "REV_VG", "REV_MID", "REV_VZ")
 
 _OLD_RAIL = (
     '_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", loads={"Q2": 10.0}, switch="U1", enable_net="DSG_R", v_work=16.8, converted=False,   # the GAUGE\'s own pin; R18, 5.1k, sits between it and the FET gate DSG_G\n'
     '             note="the pack lead. THE SWITCH IS THE GAUGE: Q2 is the discharge FET and the BQ4050 drives its gate on DSG_G, so the pack terminal is live only while the gauge allows it, which is the first stage of the energy chain")\n')
 _NEW_RAIL = (
     '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1 and C-1b, IF-5, IF-6): THE PACK TERMINAL IS THE BREAKER\'S\n'
-    '# OUTPUT. Q2\'s source is the net BRK_VIN, the LM5069-2 breaker U101 (drawn below, before the pack leads) passes BRK_VIN through\n'
+    '# OUTPUT. Q2\'s source is the net BRK_VIN, the LM5069-1 breaker U101 (drawn below, before the pack leads) passes BRK_VIN through\n'
     '# its sense pair to BRK_SNS and through Q101 and Q102 to PACK_P, so the terminal is live only while the gauge holds Q2 on AND\n'
     '# the dock\'s enable loop is closed. BRK_VIN and BRK_SNS are segments of the one pack path whose power PACK_P counts.\n'
     '_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", loads={"Q101": 5.0, "Q102": 5.0}, switch="U101", enable_net="BRK_UVLO", v_work=16.8, converted=False,\n'
-    '             note="the pack lead, the breaker\'s output (record l8p; l9stk 15.4 C-1, IF-6): U101 (LM5069-2) drives Q101 and Q102 '
+    '             note="the pack lead, the breaker\'s output (record l8p; l9stk 15.4 C-1, IF-6): U101 (LM5069-1, latch-off) drives Q101 and Q102 '
     '(CSD18510Q5B, an even split when enhanced, SLVA673A 2.4) from BRK_SNS; its UVLO is held low unless the dock\'s enable loop '
     'is closed (C-1b), so the terminal is live only while the gauge holds Q2 on and the kit is docked (IF-5)")\n'
     '_intent.rail("BRK_VIN", 14.4, 10.0, 18.0, "Q2", loads={"R101": 6.52, "R102": 3.48}, switch="U1", enable_net="DSG_R", series_of="PACK_P",\n'
@@ -85,34 +108,60 @@
 _ANCHOR_WP = 'part("W_P", "Connector", "Conn_01x01_Pin", "pack lead + (12 AWG to the XT60 on E6 J_BATT pin 2)", "WIRE", {"1": "PACK_P"})\n'
 _BREAKER = (
     '# =========================================================================================================================\n'
-    '# RECORD l8p (MESHSAT-1357, 4 October 2026): W4DP-F2\'S FIRMWARE-INDEPENDENT ELEMENT, drawn from record l9stk section 15\n'
-    '# (branch fnd/l9stk at 2c8b29fb, CONFIRMED AS CONDITIONAL). With Q1 and Q2 welded and no firmware, nothing on this board\n'
-    '# opened the discharge path on current alone (l9stk 15.2). C-1 (15.4): the LM5069-2 circuit breaker U101 from BRK_VIN (Q2\'s\n'
-    '# source) to PACK_P. The sense pair R101 4 mOhm and R102 7.5 mOhm in parallel, 2.6087 mOhm, 1 percent and at most 50 ppm/K\n'
-    '# (current limit 18.32 to 23.93 A, breaker 30.21 to 50.59 A); Q101 and Q102 CSD18510Q5B, 40 V; RPWR R103 8.45 kOhm (32.52 W\n'
-    '# nominal); the timer C101 10 nF (clearing at most 1.292 ms); the dv/dt capacitor C102 22 nF on the gate (a start is 0.659 A at\n'
-    '# most); the input clamp D101 SMCJ18A. The clamp, the controller and its small parts return to PACK_N (IF-6), and OVLO is\n'
-    '# tied there (15.4, the controller row). D1 stays on PACK_P and carries the lead\'s freewheel at turn-off (15.4, the clamps\n'
-    '# row). Where an older comment above names PACK_P as Q2\'s source, read BRK_VIN.\n'
-    '# C-1b (15.4, B-P1, conditions C1 and C2): THE MAKE-LAST ENABLE IS A LOOP. R106 10 kOhm from BRK_VIN onto J_SMB pin 7\n'
-    '# (DOCK_EN_OUT); board E passes it to the dock, board A passes it through its thermal guard RT1 (a PRF15BB103 on the battery\n'
-    '# FETs\' copper, 15.5) and back; it returns on J_SMB pin 5 (DOCK_EN_RET) into R107 22 kOhm on the first inverter Q103\'s gate.\n'
-    '# Q103 holds the second inverter Q104\'s gate (R108 and R109, 1 MOhm each: half of BRK_VIN, l9stk_protection.py\'s R_G) low;\n'
-    '# Q104, when on, discharges UVLO through R105 150 ohm. UVLO charges from BRK_VIN through R104 200 kOhm into C103 3.3 uF 50 V:\n'
-    '# the gate rises 0.110 to 0.593 s after the enable mates and a dv/dt start follows; the loop opening turns the gate off in\n'
-    '# 1.51 ms; an open or a short to ground on either conductor holds the breaker off. J_SMB pin 6 is the ground contact between\n'
-    '# the two conductors (C2). The order of mating (every power pin before the enable, 1 mm short) is Layer 7\'s (C1).\n'
+    '# RECORD l8p (MESHSAT-1357, 4 October 2026, round 2): W4DP-F2\'S FIRMWARE-INDEPENDENT ELEMENT, drawn from record l9stk section\n'
+    '# 15 (branch fnd/l9stk at 0d72880b, its latest changes CONFIRMED AS CONDITIONAL). With Q1 and Q2 welded and no firmware,\n'
+    '# nothing on this board opened the discharge path on current alone (l9stk 15.2).\n'
+    '# C-1 (15.4, 15.4b): the LM5069-1 circuit breaker U101, THE LATCH-OFF VARIANT (the -2\'s retry takes its own FET past TI\'s\n'
+    '# margin in a hard short and past 150 C in a resistive fault on VSYS, 15.4b), from BRK_VIN (Q2\'s source) to PACK_P. The sense\n'
+    '# pair R101 4 mOhm and R102 7.5 mOhm in parallel, 2.6087 mOhm, 1 percent and at most 50 ppm/K (current limit 18.32 to 23.93 A,\n'
+    '# breaker 30.21 to 50.59 A); Q101 and Q102 CSD18510Q5B, 40 V; RPWR R103 8.45 kOhm; the timer C101 10 nF (clearing at most\n'
+    '# 1.292 ms); the dv/dt capacitor C102 22 nF on the gate (a start is 0.659 A at most); the input clamp D101 SMCJ18A. The clamp,\n'
+    '# the controller and its small parts return to PACK_N (IF-6), and OVLO is tied there. D1 stays on PACK_P and carries the\n'
+    '# lead\'s freewheel at turn-off. Where an older comment above names PACK_P as Q2\'s source, read BRK_VIN. The -1\'s order code\n'
+    '# is Layer 6\'s to file (the -2 is C111822 on the same land): OWED.\n'
+    '# C-1b (15.4, conditions C1 and C2): THE MAKE-LAST ENABLE IS A LOOP. R106 10 kOhm from BRK_VIN onto J_SMB pin 7 (DOCK_EN_OUT);\n'
+    '# board E passes it to the dock, board A through its thermal guard RT1 (a PRF15BB103 on the battery FETs\' copper, 15.5) and\n'
+    '# back on J_SMB pin 5 (DOCK_EN_RET) into R107 22 kOhm on the first inverter Q103\'s gate. Q103 holds the second inverter Q104\'s\n'
+    '# gate (R108 and R109, 1 MOhm each, l9stk_protection.py\'s R_G) low; Q104, when on, pulls UVLO DIRECTLY. THE HOLD: R104 200\n'
+    '# kOhm from BRK_VIN charges C103 3.3 uF 50 V on the node BRK_H, which reaches UVLO through R105 150 ohm and D102 1N4148W, so\n'
+    '# when Q104 pulls UVLO, C103 drains behind it through R105 and D102 (107 mA at most, 0.11 of D102\'s 1 A 1 ms surge and 0.71\n'
+    '# of its 150 mA average) and the turn-off no longer waits for C103: the gate is low 0.41 ms after the loop opens, before the\n'
+    '# pins part at a withdrawal under 2.42 m/s. The release is 0.110 to 0.907 s after the enable mates, then a dv/dt start. An\n'
+    '# open or a short to ground on either conductor holds the breaker off. J_SMB pin 6 is the ground contact between the two\n'
+    '# conductors (C2). The order of mating (every power pin before the enable, 1 mm short) is Layer 7\'s (C1).\n'
+    '# C-1c (15.4b, DD-8): THE RESTART INHIBIT ON THE BREAKER PAD. RT101, the Murata NXRT15XH103FA1B010 NTC (10 kOhm 1 percent,\n'
+    '# B25/50 3380 K 1 percent, B25/85 3434 K a reference value), BONDED ON THE BREAKER FETS\' PAD with an electrically insulating,\n'
+    '# thermally conducting adhesive over the pad\'s solder mask (the pad is BRK_SNS, about BRK_VIN), its 10 mm leads soldered to\n'
+    '# two lands beside it; R110 150 kOhm 0.1 percent over it from BRK_VIN (0.111 mA at most, under its 0.12 mA). The reference is\n'
+    '# ratiometric from the same BRK_VIN: R111 147 kOhm over R112 1.62 kOhm, both 0.1 percent (1653.06 ohm equivalent against the\n'
+    '# trip\'s 1653). U102, a TI OPA187 zero-drift amplifier used as the comparator (+IN the reference, -IN the NTC: its output is\n'
+    '# high while the pad is hot), R113 15 MOhm from its output to the reference for the hysteresis. Its output drives Q105\'s gate\n'
+    '# through R114 and R115 (100 kOhm each, under the 2N7002\'s 20 V), and Q105 pulls UVLO. PGD gates it: R116 and R117 (1 MOhm\n'
+    '# each) hold U101\'s open-drain PGD at half BRK_VIN while the breaker runs, and Q106 then holds Q105\'s gate low, so the inhibit\n'
+    '# acts only while PGD is low (the breaker off, starting or in a fault, VDS over 1.62 to 3.4 V) and never turns off a running\n'
+    '# breaker. Pulling UVLO resets the -1\'s latch; the breaker restarts through the hold once the pad cools under the trip, so\n'
+    '# any further event starts at 83.2 C at most. THE WINDOW: allow from 77.25 C, block from 83.20 C, trip 80.22 C +-2.97 K: the\n'
+    '# NTC takes +-1.02 K (its tolerance at 80 C ASSUMED: the held sheet is Murata\'s product search sheet and B25/85 a reference\n'
+    '# value; to be confirmed by Murata\'s approval sheet or E-15). THE +-1.95 K LEFT, BY PART CHOICE (l8p_drafts.out section 3):\n'
+    '# the OPA187 with its offset over temperature, bias and offset currents and supply rejection at most 0.02 K; the three bridge\n'
+    '# resistors at 0.1 percent and at most 25 ppm/K between 25 C and the held 101.0 C case at most 0.32 K; the NTC\'s own heating\n'
+    '# 0.014 K; the hysteresis at most 0.37 K, on the allow side; the remainder, at least 1.2 K on the allow side, for the\n'
+    '# pad-to-NTC gradient E-15 measures (the checker asked for about 0.9 K). AN OPEN OR DETACHED NTC READS COLD AND SILENTLY\n'
+    '# REMOVES THE INHIBIT: E-12b at commissioning and each service reads TP105 against TP101 (the NTC\'s fraction of BRK_VIN at the\n'
+    '# ambient, 0.0625 at 25 C; near 1 is an open NTC, near 0 a short) with TP106 low. THE LOCKOUT AT THE ALLOW EDGE: a unit\n'
+    '# tripping at 77.25 C needs its pad within 1 K of a 76.25 C inside air before it restarts, and at that air the cells\' hot stop\n'
+    '# has already shut the kit down. E-10 gains: VDS under 1.62 V during current-limit excursions (PGD stays high, so the inhibit\n'
+    '# stays gated).\n'
     '# SESSION choices of record l8p (L8P-BREAKER.md section 3): the designators (the free 100 block), the net names, J_SMB\'s pin\n'
-    '# assignment, the input bypass C104 and C105 at the sense pair (TI SNVS452G section 10, "a 1-uF ceramic capacitor to ground close\n'
-    '# to the drain of the hot swap MOSFET", and 11.1.1, the bypass "close to Rsns instead of the VIN pin"), drawn as two 2.2 uF 50 V\n'
-    '# in SERIES through BRK_CMID (1.1 uF) for the reason C11 and C12 are (O-12, SLUSC67B 8.2.2.1.5): one shorted part across the\n'
-    '# pack must not short it; PGD left open (IF-1\'s PGD option\n'
-    '# would need a conductor to board A: L4-E11\'s), TP101 to TP104 for E-12 (BRK_VIN, the hold on BRK_UVLO, both loop conductors).\n'
+    '# assignment, the input bypass C104 and C105 at the sense pair (TI SNVS452G section 10 and 11.1.1), two 2.2 uF 50 V in SERIES\n'
+    '# through BRK_CMID (1.1 uF) as C11 and C12 are (O-12): one shorted part across the pack must not short it; the comparator part,\n'
+    '# the reference values, the hysteresis, the PGD gating, C106, the test points TP101 to TP106.\n'
     '# IF-2 for the layout (gen_pcb_p3.py): each breaker FET\'s installed RthJA at most 52.5 C/W (1 in2 of 2 oz each gives the\n'
-    '# sheet\'s 50), U101 beside the sense pair with Kelvin taps (E-9), C104 and C105 at the sense pair. Nothing here is built or measured.\n'
-    'ic("U101", 10, "LM5069MM-2 circuit breaker on the pack path (record l8p; l9stk 15.4 C-1): 1 SENSE, 2 VIN, 3 UVLO, 4 OVLO, 5 GND, 6 TIMER, 7 PWR, 8 PGD, 9 OUT, 10 GATE",\n'
+    '# sheet\'s 50), U101 beside the sense pair with Kelvin taps (E-9), C104 and C105 at the sense pair, RT101 on the FETs\' pad\n'
+    '# with U102 and its bridge away from it. Nothing here is built or measured.\n'
+    'ic("U101", 10, "LM5069MM-1 circuit breaker, latch-off, on the pack path (record l8p; l9stk 15.4 C-1 and 15.4b): 1 SENSE, 2 VIN, 3 UVLO, 4 OVLO, 5 GND, 6 TIMER, 7 PWR, 8 PGD, 9 OUT, 10 GATE",\n'
     '   "Package_SO:VSSOP-10_3x3mm_P0.5mm", {"1": "BRK_SNS", "2": "BRK_VIN", "3": "BRK_UVLO", "4": "PACK_N", "5": "PACK_N", "6": "BRK_TMR",\n'
-    '   "7": "BRK_PWR", "8": "NC", "9": "PACK_P", "10": "BRK_GATE"}, "C111822")\n'
+    '   "7": "BRK_PWR", "8": "BRK_PGD", "9": "PACK_P", "10": "BRK_GATE"})   # the -1\'s order code: Layer 6, owed\n'
     'r("R101", "4m 1% 2512 (breaker sense, at most 50 ppm/K; 2 W at the band\'s temperature, E-6)", "BRK_VIN", "BRK_SNS", "RS2512")\n'
     'r("R102", "7.5m 1% 2512 (breaker sense, at most 50 ppm/K; 2 W at the band\'s temperature, E-6)", "BRK_VIN", "BRK_SNS", "RS2512")\n'
     'pfet5("Q101", "CSD18510Q5B 40 V N-FET, breaker pass (one of two in parallel; IF-2: RthJA at most 52.5 C/W installed)", "BRK_GATE", "BRK_SNS", "PACK_P", "C2876544")\n'
@@ -128,24 +177,118 @@
     'r("R106", "10k", "BRK_VIN", "DOCK_EN_OUT"); r("R107", "22k", "DOCK_EN_RET", "PACK_N")\n'
     'nfet("Q103", "DOCK_EN_RET", "PACK_N", "BRK_G2", "2N7002 60 V N-FET: the enable loop\'s first inverter, on while the loop is closed")\n'
     'r("R108", "1M", "BRK_VIN", "BRK_G2"); r("R109", "1M", "BRK_G2", "PACK_N")\n'
-    'nfet("Q104", "BRK_G2", "PACK_N", "BRK_DIS", "2N7002 60 V N-FET: the enable loop\'s second inverter, discharges UVLO while the loop is open")\n'
-    'r("R105", "150R", "BRK_DIS", "BRK_UVLO"); r("R104", "200k 1%", "BRK_VIN", "BRK_UVLO")\n'
-    'c("C103", "3.3u 50V X7R 1206 (UVLO: the RC hold)", "BRK_UVLO", "PACK_N", "C1206")\n'
-    'for _i8, _n8 in enumerate(("BRK_VIN", "BRK_UVLO", "DOCK_EN_OUT", "DOCK_EN_RET"), 101):\n'
-    '    part("TP%d" % _i8, "Connector", "TestPoint", _n8, "TP", {"1": _n8})   # E-12: the input, the hold\'s release, each loop conductor to ground in turn\n'
+    'nfet("Q104", "BRK_G2", "PACK_N", "BRK_UVLO", "2N7002 60 V N-FET: the enable loop\'s second inverter, pulls UVLO while the loop is open")\n'
+    'r("R104", "200k 1%", "BRK_VIN", "BRK_H"); c("C103", "3.3u 50V X7R 1206 (the RC hold on BRK_H)", "BRK_H", "PACK_N", "C1206")\n'
+    'r("R105", "150R", "BRK_H", "BRK_HD")\n'
+    'part("D102", "Device", "D", "1N4148W (the hold\'s diode: BRK_H through R105 to UVLO; C103 drains behind Q104 through it)", "SOD123", {"1": "BRK_UVLO", "2": "BRK_HD"}, "C81598")   # Device:D, pin 1 K, pin 2 A\n'
+    'part("RT101", "Device", "Thermistor_NTC", "NXRT15XH103FA1B010 NTC 10k 1%, B25/50 3380K 1%, 10 mm leads (Murata): the restart inhibit\'s sensor, bonded on the breaker FETs\' pad", "meshsat:LeadLands_1x02",\n'
+    '     {"1": "INH_NTC", "2": "PACK_N"})   # its order code: Layer 6, owed\n'
+    'r("R110", "150k 0.1% 25ppm (the NTC bridge)", "BRK_VIN", "INH_NTC"); r("R111", "147k 0.1% 25ppm (the trip reference)", "BRK_VIN", "INH_REF")\n'
+    'r("R112", "1.62k 0.1% 25ppm (the trip reference)", "INH_REF", "PACK_N"); r("R113", "15M 1% (the hysteresis)", "INH_OUT", "INH_REF")\n'
+    'ic("U102", 5, "OPA187IDBVR zero-drift amplifier as the restart inhibit\'s comparator (record l8p; l9stk 15.4b C-1c): 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+",\n'
+    '   "Package_TO_SOT_SMD:SOT-23-5", {"1": "INH_OUT", "2": "PACK_N", "3": "INH_REF", "4": "INH_NTC", "5": "BRK_VIN"})   # its order code: Layer 6, owed\n'
+    'c("C106", "100n 50V X7R (U102\'s supply bypass)", "BRK_VIN", "PACK_N")\n'
+    '_intent.bypass("C106", "U102", "5", "BRK_VIN", cls="D", basis="TI OPA187 SBOS807E, revised May 2020 (v2/vendor/ti/held/ti-opa187-sbos807e.pdf, "\n'
+    '               "fetched by record l8p): 10.1 Layout Guidelines \\"Low-ESR, 0.1-uF ceramic bypass capacitors must be connected between each "\n'
+    '               "supply pin and ground; place the capacitors as close to the device as possible. A single bypass capacitor from V+ to "\n'
+    '               "ground is applicable to single-supply applications\\" (p.27); the 100n drawn at U102\'s V+ (pin 5)")\n'
+    'r("R114", "100k", "INH_OUT", "INH_G"); r("R115", "100k", "INH_G", "PACK_N")\n'
+    'nfet("Q105", "INH_G", "PACK_N", "BRK_UVLO", "2N7002 60 V N-FET: the restart inhibit pulls UVLO while the pad is hot and PGD is low")\n'
+    'r("R116", "1M", "BRK_VIN", "BRK_PGD"); r("R117", "1M", "BRK_PGD", "PACK_N")\n'
+    'nfet("Q106", "BRK_PGD", "PACK_N", "INH_G", "2N7002 60 V N-FET: PGD high (the breaker running) holds the inhibit\'s gate low")\n'
+    'for _i8, _n8 in enumerate(("BRK_VIN", "BRK_UVLO", "DOCK_EN_OUT", "DOCK_EN_RET", "INH_NTC", "INH_OUT"), 101):\n'
+    '    part("TP%d" % _i8, "Connector", "TestPoint", _n8, "TP", {"1": _n8})   # E-12 and E-12b: the input, the hold\'s release, each loop conductor to ground in turn, the NTC\'s reading and the inhibit\'s state\n'
     '_intent.node("BRK_GATE", 29.4, "the breaker FETs\' gate: OUT (PACK_P, at most the pack\'s 16.8 V) plus the gate drive, at most 12.6 V above OUT "\n'
     '             "(VGATE, SNVS452G 7.5; record l9stk 15.4, the FETs row)", rides_on="PACK_P", bias_v=12.6)\n'
-    '_intent.node("BRK_UVLO", 29.2, "the breaker\'s UVLO, charged from BRK_VIN through R104 200 kOhm: at most BRK_VIN, the pack\'s 16.8 V in "\n'
-    '             "service and the input clamp D101\'s 29.2 V (SMCJ18A, VC at 51.4 A; record l9stk 15.4, the clamps row)", v_work=16.8)\n'
+    '_intent.node("BRK_UVLO", 29.2, "the breaker\'s UVLO, a diode drop under BRK_H and at most BRK_VIN: the pack\'s 16.8 V in service and the "\n'
+    '             "input clamp D101\'s 29.2 V (SMCJ18A, VC at 51.4 A; record l9stk 15.4, the clamps row)", v_work=16.8)\n'
+    '_intent.node("BRK_H", 29.2, "the RC hold\'s node, charged from BRK_VIN through R104 200 kOhm: at most BRK_VIN, the input clamp\'s 29.2 V "\n'
+    '             "(record l9stk 15.4, the hold)", v_work=16.8)\n'
+    '_intent.node("BRK_HD", 29.2, "between R105 and D102\'s anode: at most BRK_H (record l9stk 15.4, the hold)", v_work=16.8)\n'
     '_intent.node("BRK_G2", 14.6, "the second inverter\'s gate, half of BRK_VIN through R108 and R109 (1 MOhm each): at most half the "\n'
     '             "clamp\'s 29.2 V (record l9stk 15.4, the inverters\' bounds)")\n'
+    '_intent.node("BRK_PGD", 14.6, "U101\'s open-drain PGD held at half of BRK_VIN by R116 and R117 (1 MOhm each) while released: at most "\n'
+    '             "half the clamp\'s 29.2 V, under Q106\'s 20 V gate rating and PGD\'s 100 V (SNVS452G 7.1)")\n'
     '_intent.node("BRK_CMID", 29.2, "the midpoint of the series input bypass C104 and C105: about half of BRK_VIN in service, and the "\n'
     '             "whole of it, at most the input clamp\'s 29.2 V, across one part when the other has shorted (the case the pair exists "\n'
     '             "for, as PACK_MID)", v_work=16.8)\n'
+    '_intent.node("INH_NTC", 29.2, "the NTC\'s node under R110 150 kOhm from BRK_VIN: 0.0625 of it at 25 C, 0.0109 at the trip, and BRK_VIN "\n'
+    '             "itself with the NTC open, at most the clamp\'s 29.2 V", v_work=16.8)\n'
+    '_intent.node("INH_REF", 1.0, "the trip reference, 0.0109 of BRK_VIN through R111 and R112 (0.32 V at the clamp\'s 29.2 V with the "\n'
+    '             "hysteresis), lifted on the cold side by U102\'s back-to-back input diodes (SBOS807E 7.3) through the bridge\'s "\n'
+    '             "resistance by under 0.4 V more: under 1 V")\n'
+    '_intent.node("INH_OUT", 29.2, "U102\'s output, rail to rail from PACK_N to BRK_VIN: at most the clamp\'s 29.2 V", v_work=16.8)\n'
+    '_intent.node("INH_G", 14.6, "Q105\'s gate, half of U102\'s output through R114 and R115 (100 kOhm each): at most half the clamp\'s "\n'
+    '             "29.2 V, under the 2N7002\'s 20 V")\n'
     '_intent.node("DOCK_EN_OUT", 29.2, "the enable loop leaving board P, BRK_VIN through R106 10 kOhm and BRK_VIN itself with the loop open: "\n'
     '             "at most the input clamp\'s 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
     '_intent.node("DOCK_EN_RET", 17.4, "the enable loop\'s return, the first inverter\'s gate over R107 22 kOhm: at most 17.4 V under the "\n'
     '             "clamp\'s 29.2 V with RT1 at its least 5 kOhm (record l9stk 15.4, the inverters\' bounds)")\n'
+    '# B-R2, ROUTE R1 (record l8p round 3, 4 October 2026; L4-E11 section 19h, its checker\'s B-R2): THE REVERSE-CHARGE DETECTOR.\n'
+    '# While the breaker is off (latched, in its hold, held by C-1c or by the thermal guard) a source on board A can hold CELL+ and\n'
+    '# so PACK_P above BRK_VIN through the battery FETs, and push a charge backwards through Q101\'s and Q102\'s body diodes. The -1\n'
+    '# then reads nothing (PGD is high on VDS alone, and VDS is negative: SNVS452G pin 8), and board A sees CELL+ alive, so its\n'
+    '# hardware inhibit (L4-E11\'s Q47 to Q49) never sets: the charge rested on the firmware. THE TWO CONDITIONS, BOTH HELD HERE:\n'
+    '# U103 (OPA187) reads the charge INTO THE CELLS on the gauge\'s own sense R10 (2 mOhm, cell side GND, pack side PACK_N): its\n'
+    '# +IN on GND through R120 200 ohm and C109 470 nF (94 us), its -IN on R118 1.15 MOhm over R119 200 ohm from REV_VZ, which is\n'
+    '# BRK_VIN through R129 47 kOhm held under D103\'s BZT52C12: 0.0869 A per volt of REV_VZ, so 0.368 A at least at the LDO-mode\n'
+    '# precharge\'s floor (BRK_VIN 4.7 V), 0.661 to 0.922 A at the pack\'s 10.6 V, 1.213 A at most anywhere (the zener at 13.46 V hot),\n'
+    '# with every tolerance: above the charger\'s LDO-mode precharge (0.336 A at most, L4-E11 section 15) and its power-on 256 mA,\n'
+    '# under the latched FET\'s 1.405 A (L4-E11 E-14), so a charge it lets pass holds the FET at 139.9 C at most. It reads the\n'
+    '# cells\' current whatever Q1 and Q2 do (welded or not) and reads nothing while the gauge sleeps, so a dead pack\'s wake through\n'
+    '# the body diodes (mA, the gauge off) never trips it. U104 (OPA187) reads the BODY DIODES CONDUCTING: PACK_P over R121 332 kOhm\n'
+    '# and R122 33.2 kOhm on +IN against BRK_SNS over R123 328 kOhm and R124 33.2 kOhm on -IN, high when PACK_P exceeds BRK_SNS by\n'
+    '# 1.107 % of it (0.044 to 0.268 V over BRK_VIN 7.6 to 16.8 V with every tolerance; R121 to R124 0.05 % and at most 10 ppm/K),\n'
+    '# C110 1 nF across its inputs. A running breaker passing any charge up to the pack path\'s 23.93 A shows at most 20.7 mV there\n'
+    '# (two CSD18510Q5B channels hot); its body diodes at the threshold\'s least current about 0.35 V (TI\'s typical figure, 150 C):\n'
+    '# U104 never reads a running breaker. BOTH HIGH: Q107 and Q108 (2N7002, in series, gates through R125 to R128 at half of each\n'
+    '# output) hold DOCK_EN_RET under 0.05 V. That is the loop\'s return held low, as an undocking holds it: the existing contact\n'
+    '# J_DOCK pin 3 carries it to board A, whose inhibit sets on it (L4-E11 extends DD-7: DOCK_EN_RET under 1.0 V with DOCK_EN_OUT at\n'
+    '# 2.0 V or over sets the inhibit within 1 ms and holds it at least 1.0 s after the return rises over 2.5 V), and Q103 and Q104\n'
+    '# reset the -1 (UVLO pulled). The charge stops, U103 releases, the hold (0.110 to 0.907 s) and the dv/dt start (40.7 ms)\n'
+    '# restart the breaker with board A\'s battery FETs held off, so the start meets no forward current. The detector never acts on a\n'
+    '# running breaker: discharging, U103 reads a negative drop; charging through the channel, U104 reads under its threshold. It\n'
+    '# pulls from BRK_VIN 7.6 V (the -1\'s PORIT; the 2N7002 gates at half of it); under that the -1 cannot run or stay latched.\n'
+    '# Its own failures and E-12c: the record page, section 12. Nothing here is built or measured.\n'
+    'ic("U103", 5, "OPA187IDBVR zero-drift amplifier as the reverse-charge detector\'s current comparator (record l8p, B-R2): 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+",\n'
+    '   "Package_TO_SOT_SMD:SOT-23-5", {"1": "REV_IOUT", "2": "PACK_N", "3": "REV_ISNS", "4": "REV_IREF", "5": "BRK_VIN"})   # U102\'s part; its order code: Layer 6, owed\n'
+    'r("R129", "47k 1% (the reference\'s feed)", "BRK_VIN", "REV_VZ")\n'
+    'part("D103", "Device", "D_Zener", "BZT52C12-7-F zener, the charge threshold\'s ceiling (11.4 to 12.7 V at 5 mA, DS18004)", "SOD123", {"1": "REV_VZ", "2": "PACK_N"}, "C124196")\n'
+    'r("R118", "1.15M 0.1% 25ppm (the charge threshold\'s reference)", "REV_VZ", "REV_IREF"); r("R119", "200R 0.1% 25ppm (the charge threshold\'s reference)", "REV_IREF", "PACK_N")\n'
+    'r("R120", "200R (Kelvin from R10\'s cell-side pad)", "GND", "REV_ISNS"); c("C109", "470n 25V X7R (the charge sense\'s filter)", "REV_ISNS", "PACK_N")\n'
+    'c("C107", "100n 50V X7R (U103\'s supply bypass)", "BRK_VIN", "PACK_N")\n'
+    'ic("U104", 5, "OPA187IDBVR zero-drift amplifier as the reverse-charge detector\'s body-diode comparator (record l8p, B-R2): 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+",\n'
+    '   "Package_TO_SOT_SMD:SOT-23-5", {"1": "REV_VOUT", "2": "PACK_N", "3": "REV_VP", "4": "REV_VN", "5": "BRK_VIN"})   # U102\'s part; its order code: Layer 6, owed\n'
+    'r("R121", "332k 0.05% 10ppm (PACK_P\'s divider)", "PACK_P", "REV_VP"); r("R122", "33.2k 0.05% 10ppm (PACK_P\'s divider)", "REV_VP", "PACK_N")\n'
+    'r("R123", "328k 0.05% 10ppm (BRK_SNS\'s divider)", "BRK_SNS", "REV_VN"); r("R124", "33.2k 0.05% 10ppm (BRK_SNS\'s divider)", "REV_VN", "PACK_N")\n'
+    'c("C110", "1n 50V C0G (across U104\'s inputs)", "REV_VP", "REV_VN"); c("C108", "100n 50V X7R (U104\'s supply bypass)", "BRK_VIN", "PACK_N")\n'
+    '_intent.bypass("C107", "U103", "5", "BRK_VIN", cls="D", basis="TI OPA187 SBOS807E, revised May 2020 (v2/vendor/ti/held/ti-opa187-sbos807e.pdf, "\n'
+    '               "fetched by record l8p): 10.1 Layout Guidelines \\"Low-ESR, 0.1-uF ceramic bypass capacitors must be connected between each "\n'
+    '               "supply pin and ground; place the capacitors as close to the device as possible\\" (p.27); the 100n drawn at U103\'s V+ (pin 5)")\n'
+    '_intent.bypass("C108", "U104", "5", "BRK_VIN", cls="D", basis="TI OPA187 SBOS807E, revised May 2020 (v2/vendor/ti/held/ti-opa187-sbos807e.pdf, "\n'
+    '               "fetched by record l8p): 10.1 Layout Guidelines \\"Low-ESR, 0.1-uF ceramic bypass capacitors must be connected between each "\n'
+    '               "supply pin and ground; place the capacitors as close to the device as possible\\" (p.27); the 100n drawn at U104\'s V+ (pin 5)")\n'
+    'r("R125", "100k", "REV_IOUT", "REV_IG"); r("R126", "100k", "REV_IG", "PACK_N")\n'
+    'r("R127", "100k", "REV_VOUT", "REV_VG"); r("R128", "100k", "REV_VG", "PACK_N")\n'
+    'nfet("Q107", "REV_IG", "REV_MID", "DOCK_EN_RET", "2N7002 60 V N-FET: the reverse-charge detector, a charge over the threshold into the cells (in series with Q108)")\n'
+    'nfet("Q108", "REV_VG", "PACK_N", "REV_MID", "2N7002 60 V N-FET: the reverse-charge detector, the breaker\'s body diodes conducting (in series with Q107)")\n'
+    'for _i8, _n8 in enumerate(("REV_IOUT", "REV_VOUT"), 107):\n'
+    '    part("TP%d" % _i8, "Connector", "TestPoint", _n8, "TP", {"1": _n8})   # E-12c: each comparator\'s state\n'
+    '_intent.node("REV_ISNS", 0.11, "R10\'s cell side through R120 1 kOhm: the cells\' charge current times 2 mOhm, at most the breaker\'s "\n'
+    '             "largest 50.59 A discharge (0.101 V under PACK_N) and its 23.93 A (0.048 V) either way (record l9stk 15.4)", v_min=-0.11)\n'
+    '_intent.node("REV_VZ", 13.5, "the reference\'s feed, BRK_VIN through R129 47 kOhm under D103 (BZT52C12: 12.7 V at most at 5 mA, "\n'
+    '             "plus 10 mV/K to the held 101.0 C, 13.46 V; 0.34 mA at the input clamp\'s 29.2 V)", v_work=12.7)\n'
+    '_intent.node("REV_IREF", 0.003, "the charge threshold\'s reference, REV_VZ through R118 1.15 MOhm over R119 200 ohm: 1.739e-4 of it, "\n'
+    '             "2.34 mV at the zener\'s 13.46 V")\n'
+    '_intent.node("REV_VP", 3.0, "PACK_P over R121 and R122 (1/11): 2.95 V at D1\'s 32.4 V clamp (SMBJ20A), 1.53 V at the pack\'s 16.8 V")\n'
+    '_intent.node("REV_VN", 2.7, "BRK_SNS over R123 and R124 (1/11.04): 2.65 V at the input clamp\'s 29.2 V")\n'
+    '_intent.node("REV_IOUT", 29.2, "U103\'s output, rail to rail from PACK_N to BRK_VIN: at most the clamp\'s 29.2 V", v_work=16.8)\n'
+    '_intent.node("REV_VOUT", 29.2, "U104\'s output, rail to rail from PACK_N to BRK_VIN: at most the clamp\'s 29.2 V", v_work=16.8)\n'
+    '_intent.node("REV_IG", 14.6, "Q107\'s gate, half of U103\'s output through R125 and R126: at most half the clamp\'s 29.2 V, under the "\n'
+    '             "2N7002\'s 20 V")\n'
+    '_intent.node("REV_VG", 14.6, "Q108\'s gate, half of U104\'s output through R127 and R128: at most half the clamp\'s 29.2 V, under the "\n'
+    '             "2N7002\'s 20 V")\n'
+    '_intent.node("REV_MID", 17.4, "between Q107 and Q108: at most DOCK_EN_RET\'s 17.4 V while Q108 is off (record l9stk 15.4)")\n'
     '# =========================================================================================================================\n')
 
 _OLD_JSMB = (
@@ -172,9 +315,12 @@
              '_intent.rail("VCC_F", 14.4, 0.0, 0.00034, "R7", loads={"U1": 0.00034}, fed_from="BRK_VIN", converted=False, v_work=16.8,\n')
 
 _ANCHOR_SEC = 'placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}\n'
-_SEC = ('SECTIONS.append(("PACK BREAKER LM5069-2 (W4DP-F2), ITS FETS, SENSE PAIR AND CLAMP; THE DOCK ENABLE LOOP, ITS INVERTERS AND THE RC HOLD (RECORD l8p)",\n'
+_SEC = ('SECTIONS.append(("PACK BREAKER LM5069-1 (W4DP-F2), ITS FETS, SENSE PAIR AND CLAMP; THE DOCK ENABLE LOOP, ITS INVERTERS AND THE RC HOLD; THE RESTART INHIBIT; THE REVERSE-CHARGE DETECTOR (RECORD l8p)",\n'
         '                 ["U101", "R101", "R102", "Q101", "Q102", "R103", "C101", "C102", "C104", "C105", "D101", "R106", "R107", "Q103", "R108", "R109",\n'
-        '                  "Q104", "R105", "R104", "C103", "TP101", "TP102", "TP103", "TP104"]))\n')
+        '                  "Q104", "R104", "C103", "R105", "D102", "RT101", "R110", "R111", "R112", "R113", "U102", "C106", "R114", "R115", "Q105",\n'
+        '                  "R116", "R117", "Q106", "TP101", "TP102", "TP103", "TP104", "TP105", "TP106",\n'
+        '                  "U103", "R129", "D103", "R118", "R119", "R120", "C109", "C107", "U104", "R121", "R122", "R123", "R124", "C110", "C108",\n'
+        '                  "R125", "R126", "R127", "R128", "Q107", "Q108", "TP107", "TP108"]))\n')
 
 EDITS = [
     (_OLD_RAIL, _NEW_RAIL),
```

#### The copy `v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_e_enable-515f6cf2.txt`

- The base copy: sha256 `3323d1831fd1dc46664b739f51d981ab0c9c84f49838e7c8f62053782fc0caa9` (the generator's pin `l8p_enable`, line 110); round 1's draft at `515f6cf2`, byte for byte.
- W5's file: `v2/docs/records/l8p/apply_gen_sch_e_enable.py` at `cd19df59`, sha256 `c1fa1713c6e5fe291984e8f31e8a47eff447743c38dfc364d05b9e80dcfe5912`; the same bytes at `69b8c3bb` (its last change), at the base and at `6bc4424e`.
- The copy's LM5069 lines: none (W5: "names no LM5069").
- The re-taken copy: `v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_e_enable-69b8c3bb.txt`, sha256 `c1fa1713c6e5fe291984e8f31e8a47eff447743c38dfc364d05b9e80dcfe5912`.
- The lines that differ (unified diff, three lines of context, 11 lines):

```diff
--- a/v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_e_enable-515f6cf2.txt
+++ b/v2/docs/records/l8p/apply_gen_sch_e_enable.py@cd19df59
@@ -3,7 +3,7 @@
 APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).
 
 Board E's half of the pack breaker's make-last enable loop (record l9stk section 15.4, C-1b, conditions C1 and C2; DD-6's owner
-row "board E's generator (two J_SMB contacts with a ground between)"; branch fnd/l9stk at 2c8b29fb). Board E is a pass-through:
+row "board E's generator (two J_SMB contacts with a ground between)"; branch fnd/l9stk at 2c8b29fb, unchanged at 0d72880b). Board E is a pass-through:
 the loop comes from board P on the SMBus lead and leaves for the dock block on the signal lands, and nothing on this board
 touches it. Board P's draft (apply_gen_sch_p_breaker.py) drives it, board A's (apply_gen_sch_a_ptc.py) closes it through the
 thermal guard RT1.
```

#### The copy `v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_a_ptc-515f6cf2.txt`

- The base copy: sha256 `c8e4eeb499491eab773332b090ef1ebb8f0d14975ffedf9e750f5c64ff89d92f` (the generator's pin `l8p_ptc`, line 111); round 1's draft at `515f6cf2`, byte for byte.
- W5's file: `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` at `cd19df59`, sha256 `cedae4eb4572a6a5b137dfc151b07d96ac9004e332317dba1c6d703941ce95c0`; the same bytes at `8e6a938c` (its last change), at the base and at `6bc4424e`.
- The copy's LM5069 lines: 45.
- The re-taken copy: `v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_a_ptc-8e6a938c.txt`, sha256 `cedae4eb4572a6a5b137dfc151b07d96ac9004e332317dba1c6d703941ce95c0`.
- The lines that differ (unified diff, three lines of context, 50 lines):

```diff
--- a/v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_a_ptc-515f6cf2.txt
+++ b/v2/docs/records/l8p/apply_gen_sch_a_ptc.py@cd19df59
@@ -3,11 +3,16 @@
 to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).
 
 Board A's half of the pack breaker's make-last enable loop (record l9stk section 15.4, C-1b, and 15.5, THE THERMAL GUARD,
-SELECTED; owners "board A's generator with L4-E11 for the PTC beside the battery FETs"; branch fnd/l9stk at 2c8b29fb). The loop
+SELECTED; owners "board A's generator with L4-E11 for the PTC beside the battery FETs"; branch fnd/l9stk at 2c8b29fb, unchanged at 0d72880b). The loop
 from board P crosses the dock on two contacts and passes, on this board, the kit's PRF15BB103 chip PTC on the battery FETs'
-copper: 10 kOhm +-50 % cold, 47 kOhm at 130 +-3 C, 32 V. The first inverter on board P stays on to 47 kOhm at 10.6 V and is off
-from 338 kOhm at 16.8 V, so the breaker opens between the PTC's 47 kOhm point (127 to 133 C) and its 338 kOhm point (E-13), a
-guard against the battery FETs' installed path never being met, unit by unit.
+copper. Murata prints for PRF15BB103RB6RC (DM-SA16-E056 Rev.1 201608, 3.1, p.4): 10 kOhm +-50 % at 25 C, 100 kOhm at a sensing
+temperature over 110 C, 4.7 MOhm at 130 +-3 C, 32 V. The first inverter on board P is surely off from 341.2 kOhm at 16.8 V (the
+loop's parts at 1 %), so the breaker is off before the PTC's copper passes 133 C: a guard against the battery FETs' installed path
+never being met, unit by unit. Its no-trip side is NOT printed (finding L8P-F07, OPEN: L8P-BREAKER.md section 12j; E-13): the
+guard's design is record l9stk's next round, and this draft draws the part that record selected.
+(Rounds 1 to 5 quoted record l9stk 15.5 here, a 47 kOhm point at 130 +-3 C and a trip between it and a 338 kOhm point: that
+column of Murata's table belongs to its 470 ohm parts, not to this one. Corrected in round 6, in this text, in the comment the
+draft writes and in RT1's value text.)
 
 What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
   J_DOCK  pins 3 and 5 (until now ground) carry DOCK_EN_RET and DOCK_EN_OUT, pin 4 the ground between them in the 2 x 6 field's
@@ -42,12 +47,13 @@
                 "INT = shutdown request, KILL from the panel controller through Q1\n")
 _LOOP = (
     '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1b and condition C2, and 15.5, THE THERMAL GUARD): THE PACK\n'
-    '# BREAKER\'S DOCK ENABLE LOOP CROSSES THIS BOARD. Board P\'s LM5069-2 breaker (record l8p\'s apply_gen_sch_p_breaker.py) is held off\n'
+    '# BREAKER\'S DOCK ENABLE LOOP CROSSES THIS BOARD. Board P\'s LM5069-1 breaker (record l8p\'s apply_gen_sch_p_breaker.py) is held off\n'
     '# unless a loop from its input, out over board E and the dock and back, is closed: J_DOCK pins 5 (DOCK_EN_OUT) and 3 (DOCK_EN_RET)\n'
     '# with pin 4, between them in the 2 x 6 field\'s first row, still ground (C2: a short between the two conductors meets ground\n'
-    '# first). On this board the loop passes RT1, the kit\'s PRF15BB103 chip PTC, on the battery FETs\' copper: the breaker opens\n'
-    '# between RT1\'s 47 kOhm point (127 to 133 C) and its 338 kOhm point (E-13), the guard against the battery FETs\' installed path\n'
-    '# never being met. The two enable contacts mate at least 1 mm after every power pin (C1, Layer 7). The third battery FET is\n'
+    '# first). On this board the loop passes RT1, the kit\'s PRF15BB103 chip PTC, on the battery FETs\' copper: Murata prints 100 kOhm\n'
+    '# over 110 C and 4.7 MOhm at 130 +-3 C, so the breaker is off before RT1\'s copper passes 133 C (its no-trip side is not printed:\n'
+    '# record l8p\'s L8P-F07, OPEN; E-13), the guard against the battery FETs\' installed path never being met. The two enable\n'
+    '# contacts mate at least 1 mm after every power pin (C1, Layer 7). The third battery FET is\n'
     '# L4-E11\'s to draw and name; RT1 sits beside all three. The map is changed after the call, which is left for the drafts that\n'
     '# edit it (L4-E11\'s pin 1); it refuses if pins 3 to 5 are not all ground any more.\n'
     'for _p8 in P:\n'
@@ -60,7 +66,7 @@
     '        if _v8 == _p8["value"]:\n'
     '            raise SystemExit("record l8p: J_DOCK\'s description no longer names its ground pins as 1-7 or 2-7")\n'
     '        _p8["value"] = _v8\n'
-    'part("RT1", "Device", "Thermistor_PTC", "PRF15BB103RB6RC chip PTC 10k, 47k at 130 C (Murata): the pack breaker\'s thermal guard in the dock enable loop, on the battery FETs\' copper (record l8p; l9stk 15.5)",\n'
+    'part("RT1", "Device", "Thermistor_PTC", "PRF15BB103RB6RC chip PTC 10k, 100k over 110 C, 4.7M at 130 C (Murata): the pack breaker\'s thermal guard in the dock enable loop, on the battery FETs\' copper (record l8p; l9stk 15.5)",\n'
     '     "Resistor_SMD:R_0402_1005Metric", {"1": "DOCK_EN_OUT", "2": "DOCK_EN_RET"}, "C443668")\n'
     '_intent.node("DOCK_EN_OUT", 29.2, "the pack breaker\'s enable loop from board P (its BRK_VIN through 10 kOhm, BRK_VIN itself with the "\n'
     '             "loop open), J_DOCK pin 5 to RT1: at most the breaker\'s input clamp, 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
```

## 3. The rows of the re-take (WP-01 to WP-06)

### WP-01. The generator's pin `l8p_breaker`: the copy re-taken at `6eeb6cfe` (PINS)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 109
- Kind: line
- Pairs with: WP-04 to WP-06; the copy's re-take (section 2)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14, lines 1621 to 1625 (the copies L4-E9's, their re-take the coordinator's); the draft's bytes at `6eeb6cfe` (git log -1 on the draft, section 2)
- Class: BINDING (a pin follows its re-taken copy; the generator reads only the copy's draft marker and target name, lines 5310 to 5314, so no figure, predicate or verdict moves)
- Old:

```text
    "l8p_breaker": ("v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-515f6cf2.txt", "ddc7258038c86b6ad03416dafcaab68bb8133cb25540b7fb2cba1263874ff541"),
```

- New:

```text
    "l8p_breaker": ("v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_p_breaker-6eeb6cfe.txt", "e8f1294bb0f76c75d146332e41d3783256474804905faa296bcdca8bc0cf2693"),
```

### WP-02. The generator's pin `l8p_enable`: the copy re-taken at `69b8c3bb` (PINS)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 110
- Kind: line
- Pairs with: WP-04 to WP-06; the copy's re-take (section 2)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14, lines 1621 to 1625 (the copies L4-E9's, their re-take the coordinator's); the draft's bytes at `69b8c3bb` (git log -1 on the draft, section 2)
- Class: BINDING (a pin follows its re-taken copy; the generator reads only the copy's draft marker and target name, lines 5310 to 5314, so no figure, predicate or verdict moves)
- Old:

```text
    "l8p_enable": ("v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_e_enable-515f6cf2.txt", "3323d1831fd1dc46664b739f51d981ab0c9c84f49838e7c8f62053782fc0caa9"),
```

- New:

```text
    "l8p_enable": ("v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_e_enable-69b8c3bb.txt", "c1fa1713c6e5fe291984e8f31e8a47eff447743c38dfc364d05b9e80dcfe5912"),
```

### WP-03. The generator's pin `l8p_ptc`: the copy re-taken at `8e6a938c` (PINS)

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 111
- Kind: line
- Pairs with: WP-04 to WP-06; the copy's re-take (section 2)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14, lines 1621 to 1625 (the copies L4-E9's, their re-take the coordinator's); the draft's bytes at `8e6a938c` (git log -1 on the draft, section 2)
- Class: BINDING (a pin follows its re-taken copy; the generator reads only the copy's draft marker and target name, lines 5310 to 5314, so no figure, predicate or verdict moves)
- Old:

```text
    "l8p_ptc": ("v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_a_ptc-515f6cf2.txt", "c8e4eeb499491eab773332b090ef1ebb8f0d14975ffedf9e750f5c64ff89d92f"),
```

- New:

```text
    "l8p_ptc": ("v2/docs/records/l4e9/inputs/l8p-apply_gen_sch_a_ptc-8e6a938c.txt", "cedae4eb4572a6a5b137dfc151b07d96ac9004e332317dba1c6d703941ce95c0"),
```

### WP-04. The register's R-206, its From cell after the re-take

- File: `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`
- Line: 302
- Kind: fragment
- Pairs with: WP-01 to WP-03 (apply only with the re-take)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14, lines 1621 to 1625; this file's section 2
- Class: BINDING (the provenance text follows the re-take; no claim of the row changes)
- Old:

```text
the copies at `515f6cf2` in this folder's inputs are superseded, their pins the coordinator's to re-take) | Layer 8 board P generator owner
```

- New:

```text
the copies in this folder's inputs taken again from the drafts' current bytes; round 1's copies at `515f6cf2` retired) | Layer 8 board P generator owner
```

### WP-05. The register's R-207, its From cell after the re-take

- File: `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`
- Line: 303
- Kind: fragment
- Pairs with: WP-01 to WP-03 (apply only with the re-take)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14, lines 1621 to 1625; this file's section 2
- Class: BINDING (the provenance text follows the re-take; no claim of the row changes)
- Old:

```text
the copies at `515f6cf2` in this folder's inputs are superseded, their pins the coordinator's to re-take) | Layer 8 board E generator owner
```

- New:

```text
the copies in this folder's inputs taken again from the drafts' current bytes; round 1's copies at `515f6cf2` retired) | Layer 8 board E generator owner
```

### WP-06. The register's R-208, its From cell after the re-take

- File: `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`
- Line: 304
- Kind: fragment
- Pairs with: WP-01 to WP-03 (apply only with the re-take)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14, lines 1621 to 1625; this file's section 2
- Class: BINDING (the provenance text follows the re-take; no claim of the row changes)
- Old:

```text
the copies at `515f6cf2` in this folder's inputs are superseded, their pins the coordinator's to re-take) | Layer 8 board A generator owner
```

- New:

```text
the copies in this folder's inputs taken again from the drafts' current bytes; round 1's copies at `515f6cf2` retired) | Layer 8 board A generator owner
```

## 4. The release companions (W5-F1; Q-22's second item)

Record l8p's one `RELEASE.md` covers six drafts, named with their register rows in W5's section 6 item 1 table (lines 274 to 279): `apply_gen_sch_p_breaker.py` R-206, `apply_gen_sch_p_idealdiode.py` R-246, `apply_gen_sch_e_enable.py` R-207, `apply_gen_sch_a_ptc.py` R-208, `apply_gen_sch_a_thguard.py` R-222, `apply_gen_sch_a_thgfs.py` R-244. Every new text names the other five in the register's order (R-206, R-207, R-208, R-222, R-244, R-246) with "(record l8p's drafts, L8P-BREAKER.md section 6 item 1)", the words the register's R-206 to R-208 already use (lines 302 to 304). The release guard column, the order constraints and every state stay as they are. **Line 6571 (`ORDER_CONSTRAINTS`, "l8p's ideal diode after its breaker", R-206 before R-246)** names an order, not a release, and agrees with W5's section 6 item 2: no row. **R-217** (DD-7, the change list's "in the release of R-206 to R-208 (L4-E11 19h)", line 6469 and page line 458; the register's line 313) cites record l4e11, whose own row still reads three: section 7.

### WP-07. The generator's CHANGE_ORDER row R-208, its Depends text

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 6468
- Kind: line
- Pairs with: WP-08
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row); section 6 item 4, line 303 (the order constraint once round 1's section 5, `515f6cf2` line 106: finding 3)
- Class: BINDING (the companions as record l8p's section 6 item 1 names them; no order constraint, script, guard or state moves); its section citation corrected from round 1's number to the current one (finding 3)
- Old:

```text
    ("3g", "R-208", GA, "after 3g's other drafts and before d8dec31's R-193 (l8p section 5); in one release with R-206 and R-207", G_L8P),
```

- New:

```text
    ("3g", "R-208", GA, "after 3g's other drafts and before d8dec31's R-193 (l8p section 6 item 4); in one release with R-206, R-207, R-222, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)", G_L8P),
```

### WP-08. The page's change list, R-208's Depends cell (section 3)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 457
- Kind: fragment
- Pairs with: WP-07
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row); section 6 item 4, line 303 (the order constraint once round 1's section 5, `515f6cf2` line 106: finding 3); test_l4e9's t_consolidation (line 1169: the page's change list is the script's)
- Class: BINDING (the page cell of WP-07)
- Old:

```text
(l8p section 5); in one release with R-206 and R-207
```

- New:

```text
(l8p section 6 item 4); in one release with R-206, R-207, R-222, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)
```

### WP-09. The generator's CHANGE_ORDER row R-207, its Depends text

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 6504
- Kind: line
- Pairs with: WP-10
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row)
- Class: BINDING (the companions as record l8p's section 6 item 1 names them; no order constraint, script, guard or state moves)
- Old:

```text
    ("4e", "R-207", GE, "after L4-E11's aux (R-177), before d8dec31's input capacitor (R-16); in one release with R-206 and R-208", G_L8P),
```

- New:

```text
    ("4e", "R-207", GE, "after L4-E11's aux (R-177), before d8dec31's input capacitor (R-16); in one release with R-206, R-208, R-222, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)", G_L8P),
```

### WP-10. The page's change list, R-207's Depends cell (section 3)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 491
- Kind: fragment
- Pairs with: WP-09
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row); test_l4e9's t_consolidation (line 1169: the page's change list is the script's)
- Class: BINDING (the page cell of WP-09)
- Old:

```text
in one release with R-206 and R-208
```

- New:

```text
in one release with R-206, R-208, R-222, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)
```

### WP-11. The generator's CHANGE_ORDER row R-206, its Depends text

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 6531
- Kind: line
- Pairs with: WP-12
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row)
- Class: BINDING (the companions as record l8p's section 6 item 1 names them; no order constraint, script, guard or state moves)
- Old:

```text
    ("P", "R-206", GP, "board P's round with l6r2's two board P tables in either order; in one release with R-207 and R-208; board P regenerated on the box after it", G_L8P),
```

- New:

```text
    ("P", "R-206", GP, "board P's round with l6r2's two board P tables in either order; in one release with R-207, R-208, R-222, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1); board P regenerated on the box after it", G_L8P),
```

### WP-12. The page's change list, R-206's Depends cell (section 3)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 517
- Kind: fragment
- Pairs with: WP-11
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row); test_l4e9's t_consolidation (line 1169: the page's change list is the script's)
- Class: BINDING (the page cell of WP-11)
- Old:

```text
in one release with R-207 and R-208
```

- New:

```text
in one release with R-207, R-208, R-222, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)
```

### WP-13. The generator's CHANGE_ORDER row R-246, its Depends text

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 6532
- Kind: line
- Pairs with: WP-14
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row)
- Class: BINDING (the companions as record l8p's section 6 item 1 names them; no order constraint, script, guard or state moves)
- Old:

```text
    ("P", "R-246", GP, "AFTER R-206 (it reads BRK_VIN and refuses a target without the breaker draft); in one release with R-206, R-207 and R-208; l6r2's two board P tables before or after the pair; board P regenerated on the box after it", G_L8P),
```

- New:

```text
    ("P", "R-246", GP, "AFTER R-206 (it reads BRK_VIN and refuses a target without the breaker draft); in one release with R-206, R-207, R-208, R-222 and R-244 (record l8p's drafts, L8P-BREAKER.md section 6 item 1); l6r2's two board P tables before or after the pair; board P regenerated on the box after it", G_L8P),
```

### WP-14. The page's change list, R-246's Depends cell (section 3)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 518
- Kind: fragment
- Pairs with: WP-13
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row); test_l4e9's t_consolidation (line 1169: the page's change list is the script's)
- Class: BINDING (the page cell of WP-13)
- Old:

```text
in one release with R-206, R-207 and R-208
```

- New:

```text
in one release with R-206, R-207, R-208, R-222 and R-244 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)
```

### WP-15. The generator's CHANGE_ORDER row R-222, its Depends text

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 6470
- Kind: line
- Pairs with: WP-16
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row)
- Class: BINDING (the companions as record l8p's section 6 item 1 names them; no order constraint, script, guard or state moves)
- Old:

```text
    ("3g", "R-222", GA, "AFTER R-208 (the loop it rewrites: RT1 out, the guard's pair in) and R-217 (DD-7's readers on the loop); before d8dec31's R-193", G_L8P_THG),
```

- New:

```text
    ("3g", "R-222", GA, "AFTER R-208 (the loop it rewrites: RT1 out, the guard's pair in) and R-217 (DD-7's readers on the loop); before d8dec31's R-193; in one release with R-206, R-207, R-208, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)", G_L8P_THG),
```

### WP-16. The page's change list, R-222's Depends cell (section 3)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 459
- Kind: fragment
- Pairs with: WP-15
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row); test_l4e9's t_consolidation (line 1169: the page's change list is the script's)
- Class: BINDING (the page cell of WP-15)
- Old:

```text
and R-217 (DD-7's readers on the loop); before d8dec31's R-193 |
```

- New:

```text
and R-217 (DD-7's readers on the loop); before d8dec31's R-193; in one release with R-206, R-207, R-208, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1) |
```

### WP-17. The generator's CHANGE_ORDER row R-244, its Depends text

- File: `v2/docs/records/l4e9/l4e9_power_path.py`
- Line: 6471
- Kind: line
- Pairs with: WP-18
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row)
- Class: BINDING (the companions as record l8p's section 6 item 1 names them; no order constraint, script, guard or state moves)
- Old:

```text
    ("3g", "R-244", GA, "AFTER R-222 (a delta on the guard: it refuses a target without it); before d8dec31's R-193", G_L8P_THG),
```

- New:

```text
    ("3g", "R-244", GA, "AFTER R-222 (a delta on the guard: it refuses a target without it); before d8dec31's R-193; in one release with R-206, R-207, R-208, R-222 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)", G_L8P_THG),
```

### WP-18. The page's change list, R-244's Depends cell (section 3)

- File: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
- Line: 460
- Kind: fragment
- Pairs with: WP-17
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280 (the six drafts by register row); test_l4e9's t_consolidation (line 1169: the page's change list is the script's)
- Class: BINDING (the page cell of WP-17)
- Old:

```text
(a delta on the guard: it refuses a target without it); before d8dec31's R-193 |
```

- New:

```text
(a delta on the guard: it refuses a target without it); before d8dec31's R-193; in one release with R-206, R-207, R-208, R-222 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1) |
```

### WP-19. The register's R-246, its Acceptance names the six

- File: `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`
- Line: 341
- Kind: fragment
- Pairs with: none (the register; the generator prints no Acceptance cell of R-246)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280; section 14, W5-F1 (lines 1647 to 1654)
- Class: BINDING (the companions as record l8p's section 6 item 1 names them, in the words R-206 to R-208 already use)
- Old:

```text
released with R-206, R-207 and R-208 and record l8p's guard (L8P-BREAKER.md section 6 item 1)
```

- New:

```text
in one release with R-206, R-207, R-208, R-222 and R-244 (record l8p's drafts, L8P-BREAKER.md section 6 item 1)
```

### WP-20. The register's R-222, its Acceptance gains the release

- File: `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`
- Line: 318
- Kind: fragment
- Pairs with: none
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280; section 14, W5-F1 (lines 1651 to 1652: R-222's and R-244's name no release)
- Class: BINDING (as WP-19; the row's order and acceptance unchanged)
- Old:

```text
| Applied after R-208 (the loop it rewrites) and R-217 (DD-7's readers on the loop);
```

- New:

```text
| In one release with R-206, R-207, R-208, R-244 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1); applied after R-208 (the loop it rewrites) and R-217 (DD-7's readers on the loop);
```

### WP-21. The register's R-244, its Acceptance gains the release

- File: `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`
- Line: 339
- Kind: fragment
- Pairs with: none
- Source: as WP-20
- Class: BINDING (as WP-19; the row's order, acceptance, class and PROVISIONAL marks unchanged)
- Old:

```text
| Applied after the guard (R-222) and before d8dec31's R-193;
```

- New:

```text
| In one release with R-206, R-207, R-208, R-222 and R-246 (record l8p's drafts, L8P-BREAKER.md section 6 item 1); applied after the guard (R-222) and before d8dec31's R-193;
```

## 5. R-208's stale section (W5-F1; Q-22's third item)

R-208's Acceptance (register line 304) and its change-list row (generator line 6468, page line 457; WP-07 and WP-08 correct those two) cite "l8p section 5". At `515f6cf2` section 5 was "Order constraints for L4-E9's change list" (line 106) and it read "It adds no R or C, so d8dec31's mainpb (R-193, 3h) still takes R248 and C247." (line 123); on W5's branch section 5 is "Designators per draft" (line 251) and the order constraints are section 6, the PTC draft's item 4 (line 303), which reads "It adds no R or C, so by itself it composes anywhere" (line 306) and, since round 8, "With the guard before it, mainpb takes R264 and C264 on this tree's order." (lines 318 to 319). The cell's designators are round 1's, so a citation alone would point at a section that does not print them: the row restates the cell with the current section and keeps R248 and C247 as round 1's, dated.

### WP-22. The register's R-208, its Acceptance's section citation

- File: `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`
- Line: 304
- Kind: fragment
- Pairs with: WP-07 and WP-08 (the same citation in the change list)
- Source: `515f6cf2` `v2/docs/records/l8p/L8P-BREAKER.md` line 106 (round 1's '## 5. Order constraints for L4-E9's change list') and line 123 ('It adds no R or C, so d8dec31's mainpb (R-193, 3h) still takes R248 and C247.'); fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` line 251 ('## 5. Designators per draft'), line 264 ('## 6. Order constraints for L4-E9's change list'), line 303 (item 4), line 306 ('It adds no R or C, so by itself it composes anywhere') and lines 318 to 319 ('With the guard before it, mainpb takes R264 and C264 on this tree's order.')
- Class: CLAIM CHANGE, narrowing (round 1's designator reading R248 and C247 kept as round 1's, the record's current reading quoted beside it with its section; no designator, order or state of the register moves)
- Old:

```text
which still takes R248 and C247 (l8p section 5)
```

- New:

```text
which takes the next free R and C at apply time (l8p section 6 item 4, which reads R264 and C264 on the tree's order with the guard, R-222, before it; R248 and C247 were round 1's reading, its section 5 at `515f6cf2`)
```

## 6. ONLY WITH THE NEXT CIRCUIT CHANGE TO THESE DRAFTS (W5-F2, W5-F3, W5-D1; Q-23)

Each row changes one docstring sentence and nothing the draft executes (the test parses each draft before and after and finds the same syntax tree once the module docstring is set aside). Each draft's sha256 is printed by records' outputs, and those outputs are pinned in turn down to record l9t5's stability digests, so a docstring edit alone would move the whole cascade below for no change of circuit (W5-D1's reason, kept here). Apply a row only in the commit that changes that draft's bytes for a circuit reason, then regenerate the cascade in dependency order. The tables list every pin found by searching the tree at the base for the 64-hex and 16-hex sha256 of the draft and, level by level, of each file that pins it (a level-n file pins a file of level n - 1, or the draft at level 1). Readers by name with no digest (`v2/docs/records/l6r2/l6r2_passives.out` prints the sha256 of each composed generator, not of the draft; `test_l8p.py`, `test_l4e7.py` line 1074 and `test_l4e11.py` read the drafts by path) change only when a draft's drawn text changes (INFERRED from what they print; not run).

#### The pins of `v2/docs/records/l8p/apply_gen_sch_p_breaker.py` (sha256/16 `e8f1294bb0f76c75`): 2 files at level 1, 6 files in the cascade

| Level | File | Line | Pins | sha256/16 |
|---|---|---|---|---|
| 1 | `v2/docs/records/efuse/efuse_check.out` | 38 | `v2/docs/records/l8p/apply_gen_sch_p_breaker.py` | `e8f1294bb0f76c75` |
| 1 | `v2/docs/records/l8p/l8p_drafts.out` | 81 | `v2/docs/records/l8p/apply_gen_sch_p_breaker.py` | `e8f1294bb0f76c75` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 17 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 18 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l8p/l8p_guard.out` | 12 | `v2/docs/records/l8p/l8p_drafts.out` | `e3565680d08348ce` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 21 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/stability/RUN-cr3-pass1.log` | 18 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |

#### The pins of `v2/docs/records/l8p/apply_gen_sch_e_enable.py` (sha256/16 `c1fa1713c6e5fe29`): 3 files at level 1, 8 files in the cascade

| Level | File | Line | Pins | sha256/16 |
|---|---|---|---|---|
| 1 | `v2/docs/records/efuse/efuse_check.out` | 37 | `v2/docs/records/l8p/apply_gen_sch_e_enable.py` | `c1fa1713c6e5fe29` |
| 1 | `v2/docs/records/l8p/l8p_drafts.out` | 83 | `v2/docs/records/l8p/apply_gen_sch_e_enable.py` | `c1fa1713c6e5fe29` |
| 1 | `v2/docs/records/l8r2/l8r2_drafts.out` | 95 | `v2/docs/records/l8p/apply_gen_sch_e_enable.py` | `c1fa1713c6e5fe29` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 17 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 18 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l8p/l8p_guard.out` | 12 | `v2/docs/records/l8p/l8p_drafts.out` | `e3565680d08348ce` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-4d0ff8a2.txt` | 16 | `v2/docs/records/l8r2/l8r2_drafts.out` | `40a1de51ca309c6b` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 17 | `v2/docs/records/l8r2/l8r2_drafts.out` | `40a1de51ca309c6b` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 21 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/stability/RUN-cr3-pass1.log` | 18 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |

#### The pins of `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` (sha256/16 `cedae4eb4572a6a5`): 6 files at level 1, 13 files in the cascade

| Level | File | Line | Pins | sha256/16 |
|---|---|---|---|---|
| 1 | `v2/docs/records/efuse/efuse_check.out` | 35 | `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` | `cedae4eb4572a6a5` |
| 1 | `v2/docs/records/l8p/apply_test_l4e11_ptc_pin.py` | 27 | `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` | `cedae4eb4572a6a5` |
| 1 | `v2/docs/records/l8p/l8p_drafts.out` | 84 | `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` | `cedae4eb4572a6a5` |
| 1 | `v2/docs/records/l8r2/l8r2_gndret.out` | 76 | `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` | `cedae4eb4572a6a5` |
| 1 | `v2/docs/records/l9t5/l9t5_drafts.out` | 28 | `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` | `cedae4eb4572a6a5` |
| 1 | `v2/ecad/tools/tests/test_l4e11.py` | 1357 | `v2/docs/records/l8p/apply_gen_sch_a_ptc.py` | `cedae4eb4572a6a5` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 17 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 18 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l8p/l8p_guard.out` | 12 | `v2/docs/records/l8p/l8p_drafts.out` | `e3565680d08348ce` |
| 2 | `v2/docs/records/l8r2/l8r2_dist.out` | 8 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l8r2/l8r2_p0.out` | 7 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/l9t5_drafts.out` | 61 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/l9t5_t10.out` | 20 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 7 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 16 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 2 | `v2/docs/records/l9t5/l9t5_t10.out` | 22 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 12 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 21 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/stability/RUN-cr3-pass1.log` | 18 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 24 | `v2/docs/records/l8r2/l8r2_dist.out` | `64d7d7021d64d23f` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 9 | `v2/docs/records/l8r2/l8r2_dist.out` | `64d7d7021d64d23f` |
| 3 | `v2/docs/records/l8r2/l8r2_dist.out` | 10 | `v2/docs/records/l8r2/l8r2_p0.out` | `4e6fa442cc3f45ee` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 22 | `v2/docs/records/l8r2/l8r2_p0.out` | `4e6fa442cc3f45ee` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 8 | `v2/docs/records/l8r2/l8r2_p0.out` | `4e6fa442cc3f45ee` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 20 | `v2/docs/records/l9t5/l9t5_t10.out` | `94071bc12ccf5389` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 13 | `v2/docs/records/l9t5/l9t5_t10.out` | `94071bc12ccf5389` |

#### The pins of `v2/docs/records/l8p/apply_gen_sch_a_thguard.py` (sha256/16 `544a462a9031862a`): 5 files at level 1, 20 files in the cascade

| Level | File | Line | Pins | sha256/16 |
|---|---|---|---|---|
| 1 | `v2/docs/records/efuse/efuse_check.out` | 36 | `v2/docs/records/l8p/apply_gen_sch_a_thguard.py` | `544a462a9031862a` |
| 1 | `v2/docs/records/l4e11/l4e11_power.out` | 18 | `v2/docs/records/l8p/apply_gen_sch_a_thguard.py` | `544a462a9031862a` |
| 1 | `v2/docs/records/l4e11/l4e11_power.py` | 64 | `v2/docs/records/l8p/apply_gen_sch_a_thguard.py` | `544a462a9031862a` |
| 1 | `v2/docs/records/l8p/l8p_c4.out` | 16 | `v2/docs/records/l8p/apply_gen_sch_a_thguard.py` | `544a462a9031862a` |
| 1 | `v2/docs/records/l8p/l8p_drafts.out` | 85 | `v2/docs/records/l8p/apply_gen_sch_a_thguard.py` | `544a462a9031862a` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 17 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 18 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l4e7/l4e7_p0sol.out` | 16 | `v2/docs/records/l4e11/l4e11_power.out` | `40ca9c0311440ca0` |
| 2 | `v2/docs/records/l4e7/l4e7_p0sol.out` | 32 | `v2/docs/records/l4e11/l4e11_power.out` | `40ca9c0311440ca0` |
| 2 | `v2/docs/records/l9pwr/l9pwr_budget.out` | 18 | `v2/docs/records/l4e11/l4e11_power.out` | `40ca9c0311440ca0` |
| 2 | `v2/docs/records/l9stk/l9stk_copper.out` | 19 | `v2/docs/records/l4e11/l4e11_power.out` | `40ca9c0311440ca0` |
| 2 | `v2/docs/records/l9stk/l9stk_protection.out` | 20 | `v2/docs/records/l4e11/l4e11_power.out` | `40ca9c0311440ca0` |
| 2 | `v2/docs/records/l4e11/l4e11_power.out` | 16 | `v2/docs/records/l8p/l8p_c4.out` | `3dbd9bda6bce760d` |
| 2 | `v2/docs/records/l4e11/l4e11_power.py` | 62 | `v2/docs/records/l8p/l8p_c4.out` | `3dbd9bda6bce760d` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 19 | `v2/docs/records/l8p/l8p_c4.out` | `3dbd9bda6bce760d` |
| 2 | `v2/docs/records/l8p/l8p_guard.out` | 12 | `v2/docs/records/l8p/l8p_drafts.out` | `e3565680d08348ce` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 21 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/stability/RUN-cr3-pass1.log` | 18 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 23 | `v2/docs/records/l4e7/l4e7_p0sol.out` | `a343ccfe29ba9a60` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 20 | `v2/docs/records/l4e7/l4e7_p0sol.out` | `a343ccfe29ba9a60` |
| 3 | `v2/docs/records/efuse/efuse_check.out` | 54 | `v2/docs/records/l9pwr/l9pwr_budget.out` | `39b34accbd29b4fd` |
| 3 | `v2/docs/records/l8r2/l8r2_dist.out` | 14 | `v2/docs/records/l9pwr/l9pwr_budget.out` | `39b34accbd29b4fd` |
| 3 | `v2/docs/records/l9t5/l9t5_case.out` | 9 | `v2/docs/records/l9pwr/l9pwr_budget.out` | `39b34accbd29b4fd` |
| 3 | `v2/docs/records/l9t5/l9t5_cm5.out` | 9 | `v2/docs/records/l9pwr/l9pwr_budget.out` | `39b34accbd29b4fd` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 15 | `v2/docs/records/l9pwr/l9pwr_budget.out` | `39b34accbd29b4fd` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 6 | `v2/docs/records/l9pwr/l9pwr_budget.out` | `39b34accbd29b4fd` |
| 3 | `v2/docs/records/l9stk/l9stk_protection.out` | 11 | `v2/docs/records/l9stk/l9stk_copper.out` | `69c3c88558b3c65d` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 4 | `v2/docs/records/l9stk/l9stk_copper.out` | `69c3c88558b3c65d` |
| 3 | `v2/docs/records/l9pwr/l9pwr_budget.out` | 30 | `v2/docs/records/l9stk/l9stk_protection.out` | `f76dac5a2cc7cc24` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 18 | `v2/docs/records/l9stk/l9stk_protection.out` | `f76dac5a2cc7cc24` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 5 | `v2/docs/records/l9stk/l9stk_protection.out` | `f76dac5a2cc7cc24` |
| 4 | `v2/docs/records/l9t5/l9t5_connected.out` | 24 | `v2/docs/records/l8r2/l8r2_dist.out` | `64d7d7021d64d23f` |
| 4 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 9 | `v2/docs/records/l8r2/l8r2_dist.out` | `64d7d7021d64d23f` |
| 4 | `v2/docs/records/l9t5/l9t5_a1.out` | 12 | `v2/docs/records/l9t5/l9t5_case.out` | `9154ee149c9d0b44` |
| 4 | `v2/docs/records/l9t5/l9t5_drafts.out` | 59 | `v2/docs/records/l9t5/l9t5_case.out` | `9154ee149c9d0b44` |
| 4 | `v2/docs/records/l9t5/l9t5_f01.out` | 9 | `v2/docs/records/l9t5/l9t5_case.out` | `9154ee149c9d0b44` |
| 4 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 10 | `v2/docs/records/l9t5/l9t5_case.out` | `9154ee149c9d0b44` |
| 4 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 14 | `v2/docs/records/l9t5/l9t5_cm5.out` | `a6ea395a23a8ba42` |
| 5 | `v2/docs/records/l9t5/l9t5_f01.out` | 6 | `v2/docs/records/l9t5/l9t5_a1.out` | `5c9a84af6589727f` |
| 5 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 11 | `v2/docs/records/l9t5/l9t5_a1.out` | `5c9a84af6589727f` |
| 5 | `v2/docs/records/l9t5/l9t5_connected.out` | 16 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 5 | `v2/docs/records/l9t5/l9t5_t10.out` | 22 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 5 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 12 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 5 | `v2/docs/records/l9t5/l9t5_connected.out` | 21 | `v2/docs/records/l9t5/l9t5_f01.out` | `2aa78a957e497677` |
| 5 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 15 | `v2/docs/records/l9t5/l9t5_f01.out` | `2aa78a957e497677` |
| 5 | `v2/docs/records/l9t5/stability/RUN-cr3-pass1.log` | 12 | `v2/docs/records/l9t5/l9t5_f01.out` | `2aa78a957e497677` |
| 6 | `v2/docs/records/l9t5/l9t5_connected.out` | 20 | `v2/docs/records/l9t5/l9t5_t10.out` | `94071bc12ccf5389` |
| 6 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 13 | `v2/docs/records/l9t5/l9t5_t10.out` | `94071bc12ccf5389` |

#### The pins of `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` (sha256/16 `bc3fb88bae6a166f`): 6 files at level 1, 13 files in the cascade

| Level | File | Line | Pins | sha256/16 |
|---|---|---|---|---|
| 1 | `v2/docs/records/efuse/efuse_check.out` | 12 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8p/inputs/SOURCES.txt` | 69 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8p/inputs/SOURCES.txt` | 76 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8p/inputs/SOURCES.txt` | 157 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8p/inputs/SOURCES.txt` | 177 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8p/l8p_drafts.out` | 39 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8p/l8p_drafts.out` | 53 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8p/l8p_drafts.py` | 177 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l8r2/l8r2_gndret.out` | 77 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 1 | `v2/docs/records/l9t5/l9t5_drafts.out` | 14 | `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py` | `bc3fb88bae6a166f` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 17 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 18 | `v2/docs/records/efuse/efuse_check.out` | `bb631b8dafdbd5de` |
| 2 | `v2/docs/records/l8p/l8p_drafts.out` | 63 | `v2/docs/records/l8p/inputs/SOURCES.txt` | `8a18d275ea479d83` |
| 2 | `v2/docs/records/l8p/l8p_guard.out` | 12 | `v2/docs/records/l8p/l8p_drafts.out` | `e3565680d08348ce` |
| 2 | `v2/docs/records/l8r2/l8r2_dist.out` | 8 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l8r2/l8r2_p0.out` | 7 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/l9t5_drafts.out` | 61 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/l9t5_t10.out` | 20 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 7 | `v2/docs/records/l8r2/l8r2_gndret.out` | `6963c627ab37427c` |
| 2 | `v2/docs/records/l9t5/l9t5_connected.out` | 16 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 2 | `v2/docs/records/l9t5/l9t5_t10.out` | 22 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 2 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 12 | `v2/docs/records/l9t5/l9t5_drafts.out` | `3fb9f1c34d865e50` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 21 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/stability/RUN-cr3-pass1.log` | 18 | `v2/docs/records/l9t5/l9t5_connected.out` | `3c550f076642773b` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 24 | `v2/docs/records/l8r2/l8r2_dist.out` | `64d7d7021d64d23f` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 9 | `v2/docs/records/l8r2/l8r2_dist.out` | `64d7d7021d64d23f` |
| 3 | `v2/docs/records/l8r2/l8r2_dist.out` | 10 | `v2/docs/records/l8r2/l8r2_p0.out` | `4e6fa442cc3f45ee` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 22 | `v2/docs/records/l8r2/l8r2_p0.out` | `4e6fa442cc3f45ee` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 8 | `v2/docs/records/l8r2/l8r2_p0.out` | `4e6fa442cc3f45ee` |
| 3 | `v2/docs/records/l9t5/l9t5_connected.out` | 20 | `v2/docs/records/l9t5/l9t5_t10.out` | `94071bc12ccf5389` |
| 3 | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` | 13 | `v2/docs/records/l9t5/l9t5_t10.out` | `94071bc12ccf5389` |

Beside the table of `apply_gen_sch_a_ptc.py`: `v2/docs/records/l8p/apply_test_l4e11_ptc_pin.py` names the same digest by its first eight characters in its text at lines 7 and 58, and record l4e11's copy `v2/docs/records/l8p/inputs/l4e11r17-apply_gen_sch_a_dd7-ecb598c5.py` line 50 is a verbatim copy of DD-7's line 50 (pinned by `inputs/SOURCES.txt`): it stays as it is, as every verbatim copy does.

### WP-23. The breaker draft's Order sentence (W5-D1's reversal, word for word)

- File: `v2/docs/records/l8p/apply_gen_sch_p_breaker.py`
- Line: 55
- Kind: lines
- Pairs with: none (record l8p's draft)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 14, W5-D1, lines 1640 to 1643 (the replacement text, quoted)
- Class: PRESENTATION (a docstring; the draft's code, its released() check and its RELEASE.md unchanged)
- Old:

```text
Order (L8P-BREAKER.md section 5): released together with apply_gen_sch_e_enable.py and apply_gen_sch_a_ptc.py (never alone:
J_SMB's two ends and the dock's two ends must change together), with l6r2's two board P drafts in either order.
```

- New:

```text
Order (L8P-BREAKER.md section 6 item 1): released with the five other drafts that read the same RELEASE.md
(apply_gen_sch_p_idealdiode.py, apply_gen_sch_e_enable.py, apply_gen_sch_a_ptc.py, apply_gen_sch_a_thguard.py and
apply_gen_sch_a_thgfs.py), never alone, with l6r2's two board P drafts in either order.
```

### WP-24. The board E draft's Order sentence (W5-F2)

- File: `v2/docs/records/l8p/apply_gen_sch_e_enable.py`
- Line: 23
- Kind: lines
- Pairs with: none (record l8p's draft)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 280; section 14, W5-F2 (lines 1655 to 1657)
- Class: PRESENTATION (as WP-23)
- Old:

```text
Order: released with apply_gen_sch_p_breaker.py and apply_gen_sch_a_ptc.py (never alone: J_SMB's two ends and the dock's two
ends must change together); in board E's round in any position (no other board E draft touches J_SMB, the J_BLK pins it moves,
```

- New:

```text
Order (L8P-BREAKER.md section 6 item 1): released with the five other drafts that read the same RELEASE.md
(apply_gen_sch_p_breaker.py, apply_gen_sch_p_idealdiode.py, apply_gen_sch_a_ptc.py, apply_gen_sch_a_thguard.py and
apply_gen_sch_a_thgfs.py), never alone (J_SMB's two ends and the dock's two ends must change together); in board E's round in any
position (no other board E draft touches J_SMB, the J_BLK pins it moves,
```

### WP-25. The board A PTC draft's Order sentence (W5-F2)

- File: `v2/docs/records/l8p/apply_gen_sch_a_ptc.py`
- Line: 29
- Kind: lines
- Pairs with: none (record l8p's draft)
- Source: as WP-24
- Class: PRESENTATION (as WP-23)
- Old:

```text
Order: released with apply_gen_sch_p_breaker.py and apply_gen_sch_e_enable.py (never alone: the dock's two ends change together);
```

- New:

```text
Order (L8P-BREAKER.md section 6 item 1): released with the five other drafts that read the same RELEASE.md
(apply_gen_sch_p_breaker.py, apply_gen_sch_p_idealdiode.py, apply_gen_sch_e_enable.py, apply_gen_sch_a_thguard.py and
apply_gen_sch_a_thgfs.py), never alone (the dock's two ends change together);
```

### WP-26. The board A guard draft's release sentence (W5-F2)

- File: `v2/docs/records/l8p/apply_gen_sch_a_thguard.py`
- Line: 39
- Kind: lines
- Pairs with: none (record l8p's draft)
- Source: as WP-24
- Class: PRESENTATION (as WP-23)
- Old:

```text
and C264 on this tree's order). Released with the board P and board E drafts of record l8p, never alone.
```

- New:

```text
and C264 on this tree's order). Released with the five other drafts that read the same RELEASE.md (L8P-BREAKER.md section 6
item 1: apply_gen_sch_p_breaker.py, apply_gen_sch_p_idealdiode.py, apply_gen_sch_e_enable.py, apply_gen_sch_a_ptc.py and
apply_gen_sch_a_thgfs.py), never alone.
```

### WP-27. Record l4e11's DD-7 draft, its release sentence (W5-F3)

- File: `v2/docs/records/l4e11/apply_gen_sch_a_dd7.py`
- Line: 50
- Kind: lines
- Pairs with: record l4e11's E11-43 row (section 7: its own author's)
- Source: fnd/w5l8p at `cd19df59`, `v2/docs/records/l8p/L8P-BREAKER.md` section 6 item 1, lines 266 to 289 (the six; DD-7 reads record l4e11's own RELEASE.md, line 285); section 14, W5-F3 (lines 1658 to 1660)
- Class: CLAIM CHANGE, record l4e11's text (the companion count follows record l8p's section 6 item 1; nothing widened: DD-7 still reads its own RELEASE.md and keeps its order)
- Old:

```text
the three battery FETs, C238); before d8dec31's mainpb; released with l8p's three drafts and this record's charger draft.
```

- New:

```text
the three battery FETs, C238); before d8dec31's mainpb; released with record l8p's six drafts (L8P-BREAKER.md section 6 item 1,
which read record l8p's RELEASE.md; this draft reads this record's own) and this record's charger draft.
```

## 7. What this file leaves to others, and its SESSION decisions

- **R-217's release words (record l4e11's first):** the register's R-217 Acceptance (line 313) "released with l8p's three drafts (R-206 to R-208)", the change list's R-217 row "in the release of R-206 to R-208 (L4-E11 19h)" (generator line 6469, page line 458) and their source, L4-E11's E11-43 (`l4e11_power.py` line 7128, `l4e11_power.out` line 514, `L4E11-SOURCE-ONLY-AND-ENTRY.md` line 733: "released with l8p's three drafts"). DD-7 reads record l4e11's own `RELEASE.md` (W5's line 285), so its companions are record l4e11's to restate first, with WP-27; L4-E9's three texts follow that restatement. No row here, so no L4-E9 text runs ahead of its source.
- **Not in W5's findings, read in passing and left:** R-208's change-list text "after 3g's other drafts" predates the P0 round's later 3g rows (R-217, R-222, R-244, R-223 onward), whose order the list's own constraints hold; the PTC draft's "in board A's round in any position" (its line 30) is round 1's, where W5's section 6 item 4 now places it before DD-7; the generator's comment and output header "their commits are outside this branch's history" (line 5183, out line 2290) are round 8's. W5 quotes the ideal diode draft's "released with it" at line 37; it stands at line 35 at the base and at `cd19df59`, true as W5 says, and needs no row.
- **The integration's uncommitted 2b outputs** were not read (another worktree's working tree): if they changed a file this file lists, the coordinator re-reads that file's pin lines before applying.
- **SESSION decisions** (under the owner's standing rule of 26 September 2026):
  1. *W13-D1, the copies' names* (section 2). Reversed by: naming them after the re-take's commit.
  2. *W13-D2, R-222 and R-244 in the register gain the release sentence* (WP-20, WP-21), although Q-22 names only R-246: W5-F1 lists both as naming no release (W5's lines 1651 to 1652) and gives one reading for each. Reversed by: dropping WP-20 and WP-21.
  3. *W13-D3, R-208's designators kept as round 1's* (WP-22) instead of a bare citation swap, so the citation never points at a section that does not print the cell's figures. Reversed by: the cell restated from section 6 item 4 alone.
  4. *W13-D4, WP-23 takes W5-D1's reversal text word for word*; WP-24 to WP-26 use its words for their own five, each keeping its own reason in brackets. Reversed by: record l8p's author's own wording at the draft's next change.

