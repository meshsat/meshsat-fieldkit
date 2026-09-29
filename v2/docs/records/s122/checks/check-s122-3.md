mergeable: yes

# AI review: independent check of stream s122, round 3, fnd/s122b at d38c6b4d (S-122, CFL-016, MESHSAT-1357)

This is an AI review, not a qualified engineering review. Everything below is what I read or ran myself.

**Set up**
* `fnd/s122b` at `d38c6b4dd191494d62ed06b8d8956bbb116cfc23` (`git rev-parse fnd/s122b`): two commits on `83cb0640`, `89b9ac6b` and `d38c6b4d`. No netlist or generator changes in them.
* `checks/check-s122-2.md` is byte identical to my `CHECK-2.md`.
* Shared clones in my session scratchpad: one at the tip to read, one to replay the round 3 document script, and one throwaway clone for the registry script and the closure. In the throwaway clone one commit of four fixture checks was made with the owner's `-c` flags; it was never pushed, and no real tree was touched.
* Time: 29 September 2026, 19:24 to 19:32 CEST (from `date`).
* Rule tools ran with `VERDICT_DIR` in scratch.

**Documents and lines I read** (the scope of S-122 and CFL-016, with round 1 and round 2's readings where a file has not changed since):
* `v2/docs/PANEL.md`: line 156 (its round 3 citation); lines 1 to 66, 84 to 217 in rounds 1 and 2; lines 89, 90 and 180 in round 2.
* `v2/docs/CONOPS.md`, unchanged since round 2 (`6cb7b241`): lines 27, 65, 107, 135, 154, 268, 297 to 324, 331, 357, 397 to 452, 478 to 524, 588 to 660, 688, 730 to 750, 817, 840 to 918, 1027 to 1119 (sections 7 and 7a whole).
* `v2/docs/V2-SPEC.md`: line 24 and correction 33 (lines 289 to 294); the whole file in round 1; lines 3, 30, 81, 82 and 262 to 290 in round 2.
* `v2/docs/OPERATING-ENVELOPE.md`, unchanged since round 2: section 4 (lines 203 to 300).
* `v2/docs/TEST-PLAN.md`, unchanged since round 1: lines 15, 45, 54, 58 to 104, 146, 173.
* `v2/docs/ASSEMBLY.md`, unchanged since round 2: lines 81 to 95, 116 to 181, 198 to 224.
* `v2/ecad/tools/pcb_decisions.yaml` decisions 28 and 40, unchanged since round 1: their `outcome` and `reversed_by`.
* `v2/docs/feasibility/EMCON.md` section 0a.1, unchanged since round 2: lines 212 to 246.
* `v2/docs/handover/DEFINITION-STATUS.md`: lines 17 to 23 (the baselines table), 92 to 104 (the dependency table), and the section "Current values of CONOPS's circuit passages" whole, rows DC-01 to DC-09.
* `v2/docs/records/s122/verdicts.out`: every entry that changed from round 2, every entry with a FAILS line (13, all expected), and the 18 entries `sweep_absent.py` lists. Also `README.md` (the answers table and "What stays open"), `verdicts.py` (`absent_rule` and `count_rule`), `sweep_absent.py`, `apply_docs_s122_r3.py` (by its run).
* In the registry: CON-003 and CON-022 (every entry), S-42, REQ-077, CON-017, and CFL-016's new entries after the registry script.
* Netlists, parsed with `tx_inhibit.parse_netlist`:
  * board B at `1f614233`, `458b2873`, `45bde541`, `95e078a1`, `c5430071` and the tip;
  * board A at the same commits;
  * set 13's six netlists (A `6c40250c`, B `3ef9b8c4`, C `c9f73945`, D `a2d48972`, E `2ed95a0e`, P `20c7b079`).

## Blocking items

None.

## 1. B1 and the new rows, at the commits named

* **DC-07** (the supervisors' I2C status path): true.
  * At `1f614233`, `U41`, `U51` and `U61` pins 93 and 92 are `unconnected-(Ux-PB7-Pad93)` and `unconnected-(Ux-PB6-Pad92)`.
  * At `458b2873`, `45bde541`, `95e078a1`, `c5430071` and the tip, pin 93 is on `SDA` and pin 92 on `SCL`, and `SDA` reaches `J_PANEL`.
  * No part on any set 13 board is a TCA9517A.
  * CONOPS lines 310 and 490 to 492 are BASELINE on it.
* **DC-08** (break-before-make, and back-power gating FAB-02 (b) and (c)): true.
  * `U513`, `U516`, `U519`, `U520`, `U530`, `U533`, `R191`, `R192` are absent at `1f614233`, `458b2873` and `45bde541`, and present at `95e078a1`, `c5430071` and the tip.
  * On set 13:
    * `R191` 1k from `+3V3_CM1` to `PG1` and `R192` 100k to GND;
    * `U530` 74LVC1G17 makes `PG1_S`, and `U533` inverts it to `PG1_n`;
    * `U513` 74LVC1G157 selects between `PG1_n` and `PG2_n` on `BSEL1_D2` into `PGSEL1_n`;
    * `U516` gives `BOE1_n` = `BBM1` ? 1 : `PGSEL1_n` (inputs 1 on +3V3_DEV, 3 on `PGSEL1_n`, select on `BBM1`), and `BOE1_n` reaches `U109` and `U110`;
    * `U519` drives `HDMI_EN1` (`U3` pin 2 EN) from `PG1_S`/`PG2_S` on `HDMI_SEL1`, and `U520` drives `HDMI_EN2`.
  * S-42 is open, and CON-003 and CON-022 read INCONCLUSIVE waiting on it.
* **DC-09** (D-17's CC array): true. Board A's `U31` (TPD2E2U06QDBZRQ1) has pin 1 on `PD_CC1` and pin 2 on `PD_CC2`, which are `J_USBC_OUT` pins 2 and 3. It is absent at `1f614233` and present at `458b2873`, `45bde541`, `c5430071` and the tip. CONOPS line 1060's D-17 row entered at `68bc9e8f` (26 September 08:58), before `458b2873` (16:48).
* **DC-02, DC-03 and DC-04:**
  * DC-02 now names section 7a's HOT-R1 row; line 1113's first cell is BASELINE on it.
  * DC-03's note is true: board C's `R36` is on `LED_RAIL` and `Q1` pin 3 on `LED_RAIL` at `a9f212c7` and at `45bde541`.
  * DC-04's note is true: board B's `U25` AP63203 has pin 1 on `+3V3_DEV` and pin 2 on `+5V_DEV` at both commits.

## 2. The sweep, and CONOPS statements without a row

* **The four NOT DERIVABLE sentences with the absent words are about non-circuit matters:**
  * line 79 (section 2's need: infrastructure "absent or down");
  * line 107 (the second pack's location and "no case measurement is owed");
  * line 313, the charger cell ("bench confirmation owed", TI's behaviour);
  * line 872 (4e's dated header, "unless a row says a fix is owed").
* **A wider sweep of my own.** I read every CONOPS sentence outside the appendix that says "no path", "does not have", "nothing does", "lacks", "has no", "no hardware", "not gated", "only through", "driven only", "in the schematic", "until ... generator" or "as generated ... no/not". That is about 50 sentences in sections 1, 2a, M1, M5, 4, 4a, 4b, 4b.1, 4c, 4e, 7 and 7a. On the netlists each is true, or BASELINE on a row, except the two below.
  * **Section 7, the D-13 row (line 1056):** "the component mismatch with the STM32H753 in the schematic closes only when the schematic text and the BOM are aligned to the H743". Board B's `U41`, `U51` and `U61` read STM32H743VIT6 since `458b2873`, and CON-017 reads PASS. The row has no DC row and is not inventoried: its words are none of the absent rule's. Minor m1, because section 7 is a table of rulings as ruled and is not among the sections CFL-016 names.
  * **Section 7a, the HOT-R1 row's second cell (line 1113):** "as generated the cells' temperature reaches the panel controller only through the bridge ...". This is stale since `c4ad8350`, but DC-02 names "section 7a's HOT-R1 row" whole, so its current value is kept. The sentence itself is not inventoried (observation).
  * Also checked true: section 1's "VHF band lock ... not in the generators yet" (no band lock part on board D or elsewhere); the heat stage's "bank 3 has no host" and "slot 1 alone has no GNSS" (bank hubs `U102`, `U202`, `U302` and the ring's failover); "its USB supply is not gated" (`F3` from `+5V_DEV`).

## 3. The minors of check-s122-2

* **m1 (PANEL line 156):** answered. The citation is `feasibility/EMCON.md` section 0a.1, whose E72 row names `U540` to `U542`, `R536` and `R537`.
* **m2 (V2-SPEC line 24):** answered. It cites 0a.1, and correction 33 records the change.
* **m3 (DC-03 and DC-04):** answered and true (above).
* **m4 (the baselines table):** answered. The table names `6cb7b241cb84d729` at `c5430071`.
* **m5 (the assertion count):** answered; the README says 497.
* **m6 (commit references):** answered; the README names `51952c0c` and `29acd948`.
* **m7 (wrapped list items):** answered. Section 4d's items read whole (`CONOPS.md#4d:L845:item:s1`).
* **m8 (count excuses):** answered. `count_rule` checks each cover. V2-SPEC line 41 is `asserted: B:#ref~J_SIM=2`, and ASSEMBLY line 92 is `asserted: C:#ref~J_HSJ=2`.

## 4. Replay

* **Documents.**
  * `apply_docs_s122_r3.py --check`, with PANEL.md, V2-SPEC.md and DEFINITION-STATUS.md taken from `83cb0640`: 10 edits located, 144 assertions hold.
  * The run gives all eight documents byte identical to `d38c6b4d` (CONOPS.md unchanged, `6cb7b241`); a second run refuses.
  * `inventory.py` and `verdicts.py` (with `--stdout`) at the tip and with `S122_AT=e57a7365` reproduce `inventory.out`, `verdicts.out`, `inventory-base.out` and `verdicts-base.out` byte for byte.
  * Totals: 862 sentences, 339 TRUE, 0 STALE, 38 BASELINE, 485 NOT DERIVABLE, 0 UNJUDGED, 2803 assertions. `sweep_absent.py` gives 18 (3 TRUE, 11 BASELINE, 4 NOT DERIVABLE).
* **Registry.** `apply_registry_s122.py` rebinds 20 records and refuses a second run. `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_lib.py`: 59 rules, 0 errors.
* **Closure**, in the throwaway clone:
  * a staged fixture refuses;
  * committed fixtures refuse without DEFINITION-STATUS.md, and with `mergeable: no`;
  * the full committed fixture closes S-122 and sets CFL-016 to PASS;
  * a second run refuses.
  * After it, `rules_lib.py requirements` gives 0 errors, and after `rules_render.py --requirements`, `tests/run.py test_requirements test_envelope_data` gives 71 passed, 0 failed, 1 skipped.

## 5. The author's out-of-scope note on CON-003 and CON-022

I agree in part.
* The words are there:
  * CON-003's entry 2 of 13 says "R480 and R500 still 100k". Its own text dates that reading to the netlist "at `eadbe571`".
  * CON-022's entry 1 of 12 says FAB-02's "remedy (b) and (c) is not drawn".
* On the bound netlist `3ef9b8c4`, `R480` and `R500` are 10k and FAB-02 (b) and (c) are drawn.
* But each record's later entries already record the change:
  * CON-003's later entries say "R480 to R500, R15 and R16 are 10 k" (and "still 10 k" after w3b and w4b);
  * CON-022's entry 5 says (b) and (c) "are drawn ... no longer holds".
* So these are superseded dated readings inside chronological evidence lists, not current claims. The note's "false on their bound netlist" is true of the words, but not of what the records now say.
* It does not affect CFL-016 or S-122:
  * neither record is a document CFL-016 names;
  * DC-08 states their current state (INCONCLUSIVE, waiting on S-42) truly.

## Minor items

* **m1.** `v2/docs/CONOPS.md` line 1056 (section 7, D-13) calls the supervisors' part "the STM32H753 in the schematic", with the mismatch still to close. It has read H743 since `458b2873`, and CON-017 reads PASS. There is no DC row (DC-09 covers the D-17 row of the same table). Fix: a row like DC-09, or a sentence on the status page that section 7's rows are the rulings as ruled.
* **m2.** The absent rule keys on four words ("absent", "owed", "not drawn", "not connected"). Round 2's B1 used one of them, but other wordings of the same class ("has no", "does not have", "only through", "in the schematic") are not inventoried unless they name a part. My sweep of them found only m1 and the row-covered 7a sentence.
* **m3.** The README's note quotes CON-003 without its "at `eadbe571`" and without the later entries that correct it (section 5 above).

## Counts

* **Blocking: 0. Minor: 3.**
* Documents named and read: PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, `pcb_decisions.yaml` decisions 28 and 40, `feasibility/EMCON.md`, `handover/DEFINITION-STATUS.md`, and `verdicts.out`.
* check-s122-2: B1 answered (DC-07 and DC-08 true at every commit named); m1 to m8 answered.
* DC rows true: 9 of 9. Round 3 document edits true: 10 of 10.
* Replays: byte identical; validators 0 errors; tests 71 passed, 0 failed.
