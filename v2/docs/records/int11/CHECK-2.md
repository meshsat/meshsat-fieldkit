mergeable: yes
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). Its minor items N1 (U3's 800 kHz is provisional until S-117 is closed) and N2 (the capacitor is 100 pF or less; Table 9-5 is on printed pages 27 and 28) are carried in the milestone of v2/docs/EXECUTION-PLAN.md; N3 is answered there by the owner's own words. -->

# Focused AI re-check of integration set 10: fnd/int11 at f3d30ceb (MESHSAT-1357, 29 September 2026)

This is an AI review, not a qualified review, by the checker of CHECK.md. Its scope is only what the coordinator
asked: whether B1 and M9 are answered correctly, whether the carried minors are stated faithfully, and whether
anything moved beyond those files.

The candidate adds three commits on 2cbbef38: fdd50751, 77e0896a and f3d30ceb. All three are authored and committed
as the owner, with no co-author trailer. They change seven files: `pcb_emc.yaml`, `pcb_requirements.yaml`,
REQUIREMENTS-TRACE.md, and four records under `records/int11/`.

## B1: answered correctly against SLUSE66A

I checked each statement in the restated S-117 against the held datasheet
(`v2/vendor/ti/bq25731-datasheet.pdf`) and the committed netlist:
- **9.3.11 and Table 9-4 (printed p.27).** The frequency and inductance are read from the resistor on IADPT before
  start-up: 169 kOhm for 3.3 uH at 800 kHz, 191 or 187 kOhm for 4.7 uH at 400 kHz, and a 3 percent or better
  resistor. All correct.
- **IADPT net.** It carries only U3 pin 8 and TP19. Correct.
- **COMP networks.** S-117 says they match neither row of Table 9-5 (pp.27-28). This is correct and it is new to me.
  - Board A draws COMP1 as R25 10k in series with C26 10 nF, with no 33 pF across. It draws COMP2 as C27 1 nF only,
    with no R2 and no C22.
  - Table 9-5 gives 16.9k, 3.3 nF and 33 pF, then 15k, 1200 pF and 15 pF, for 3.3 uH at 800 kHz. It gives 40.2k,
    4.7 nF and 33 pF, then 15k, 680 pF and 15 pF, for 4.7 uH at 400 kHz.
- **PWM_FREQ.** The power-on default is 1b, 400 kHz, and TI pairs it with 4.7 uH (Table 9-9, p.43). Correct.
- **Round 4's O-24.** The citation is on file at `records/r4a/r4-open-items.md:53` and says the same.
- **Closing condition.** It now asks for the IADPT resistor and capacitor, the compensation networks from the table,
  the firmware's PWM_FREQ to match, and the EMC row at that frequency. That closes what B1 found.
- **Linking.** S-117 no longer carries a disposition. REQ-015 (the 9 to 36 V input that charges the pack) now waits
  on it, which satisfies the registry's open-item link rule; rules_lib reads 0 errors.
- **The U3 EMC row.** It now cites 9.3.11 and Table 9-4 and names the missing resistor and capacitor, and it says
  the start-up frequency is not established.
- **The apply script.** `apply_s117_restate.py` guards against a second run and checks that nothing else moved in
  the open items or the records. It re-parses what it wrote.

## M9: answered correctly

The U41 row now reads that its output "reaches board A's J_MEZZ_PWR1, to board D, as +5V_D8 through the eFuse U23".
In the netlist, U41 feeds D8B_SW, then L13 onto +5V_D8IN, then U23 (IN pin 4, OUT pin 5) onto +5V_D8, which lands on
J_MEZZ_PWR1. Correct.

## Carried minors: stated faithfully

The filed `records/int11/CHECK.md` matches mine except for its header comment and the words "co-author trailer"; the
findings are unchanged. CLOSURE.md states each carried item as follows:
- **M1 to M4.** Faithful. M4 as carried names only the coverage text, not the stale fingerprint comment beside it.
- **M5.** Faithful.
- **M6.** Faithful.
- **M8.** Faithful.
- **M7.** Not carried; the closure rewords the attribution instead (see N3).

## Nothing else moved

- CURRENT-EVIDENCE.md is unchanged, so it still carries 34 layout-entry reasons (13 plus 21).
- The new pages-run.log section reads the same totals: 195 PASS, 39 FAIL and 104 INCONCLUSIVE of 338, and 6, 8, 4,
  6, 3, 2 and 5 layout-entry reasons for A, B, C, D, E, E5 and P.
- REQUIREMENTS-TRACE.md moves only REQ-015's waits-on line and S-117's row.
- Validators, run in the clone with the int11 worktree's readings re-copied:
  - rules_lib: 59 rules, 0 errors.
  - rules_lib requirements: 144 records, 0 errors.
  - rules_render --check: 16 documents, 0 out of date.
  - rules_render --requirements --check: current.
  - decisions_render --check: exit 0.
  - constraints_bound: PASS.
- test_emc_sheet: 7 passed.

## Minor (none blocks)

- **N1. The row and S-117 can disagree.** The U3 row declares `f_khz: 800` as "the design's intent". S-117 leaves the
  inductor and frequency to board A's writer, and O-24 offers either 3.3 uH, 169k and 800 kHz or 4.7 uH, 191k and
  400 kHz. If the writer takes the second, the two records disagree. Mark the 800 as provisional pending S-117, or
  record it as a SESSION choice with its authority fields.
- **N2. Two small citation gaps.** The pin table (p.6) asks for a "100-pF or less" capacitor, where S-117 says "the
  100 pF capacitor". Table 9-5 is cited without its pages (27 and 28).
- **N3. The energy attribution points to a record that does not exist yet.** CLOSURE.md now says section 9 is kept
  as the reference analysis "by the owner's instruction of 29 September, recorded in v2/docs/EXECUTION-PLAN.md with
  this set's milestone". The plan at f3d30ceb does not record it yet. The instruction the tree does hold
  (`energy_architecture.py` docstring, ENERGY-RECONCILIATION.md's fourth issue) is that M1 and REQ-072 stay as
  written; it does not say that section 9 is the reference. Quote the owner's words in the milestone entry.
