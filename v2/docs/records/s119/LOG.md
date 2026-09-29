# s119 log (MESHSAT-1357, S-119), 29 September 2026, times CEST

Prototype design; AI arithmetic on the record's model; nothing built or measured.

- **15:30** Brief and worker rules read; worktree `s119` at `a1f8ec70` (`fnd/int13`, set 12). Every script of the chain
  run as found: all reproduce their committed outputs except `energy/energy_4s6p.py`, which refuses because set 12's
  S-117 edits moved `gen_sch_a.py` (pinned `eb2e347e`, now `6a136fee`). Bindings found by sha and by import:
  energy_inputs.yaml (energy_budget, energy_4s6p); energy_budget.py (energy_architecture, energy_two_pack, energy_4s6p);
  energy_architecture.py (energy_runs); energy_two_pack.py (energy_runs, reconcile_lid_panel); unpinned importers:
  `energy/checks/recompute.py` (energy_budget and the inputs), `a1int/reconcile_lid.py` (energy_two_pack),
  `a1elec/checks/recheck_two_pack.py` (typed U3B 0.975 and the .out's figures). No record README binds a chain file's
  sha; REQ-072's evidence quotes figures of energy_budget.out (2120 Wh moves to 2121).
- **15:32** energy_inputs.yaml's second issue: U3 0.979 (0.972 to 0.983) and chain_eta 0.9105, parsed and compared as
  YAML (nothing else moved). energy_budget.py re-pinned; its section 4 printed 0.979 as 0.98 at two places, so it prints
  the chain to three. energy_architecture.py and energy_4s6p.py re-pinned; energy_4s6p's gen_sch_a.py pin moved after
  `cmp_gen_sch_a.py` found the three parsed calls identical. recompute.py issued a second time with pins. night_bounds,
  packfit_west, array_calc and gauge_scale re-run: unchanged to the byte.
- **15:38** Commit `51d1d4c9`. The 100 W window's knife-edge cases move (4S19P with 1300 Wp no longer meets; 4S16P no
  longer meets up to 3 kWp); the design cases move by 0.1 Wh.
- **15:39** energy_two_pack.py's second issue: EB_SHA256, eta_u3b 0.961 (0.947 to 0.971) with its source, section 4's
  U3B bracket rows at 0.947 and 0.971, section 7's U3 loss at the chain's figure and L2 as board A draws it (4.7 uH
  XAL1010-472ME at 400 kHz). The equivalence check holds; the design case keeps 31.0 Wh (was 31.1); the entry
  requirement 5.61 A (was 5.56). recheck_two_pack.py issued a second time (U3B 0.961, the new figures): every figure
  agrees. energy_runs.py's third issue (EA_SHA, TP_SHA, section 0's 90.9 and 31.0 Wh). Commit `fc8f5f85`.
- **15:41** reconcile_lid_panel.py's third issue (TP_SHA; its NOTES labelled as the checks' measurements at the second
  issue's rows, re-wrapped whole) and reconcile_lid.py's second issue (a TP pin); both regenerated. Adverse: 4S14P
  80.6 Wh (was 87.4), 4S15P 111.6 Wh (was 118.5); typical unchanged. Commit `027adc2c`.
- **15:47** `reconcile_s119.py`: reproduces reconcile_lid_panel.out's rows byte for byte, then the change from the
  accepted figures (read from git), the failing case (U3 0.939, U3B 0.802: NOT MET everywhere), the halves apart (U3 as
  drawn with U3B as drafted: adverse NOT MET for both lids), the sensitivity grid, the lowest efficiencies that still
  meet, and the rule's planes for 4S14P and 4S15P (every rule plane meets). Its first run printed "down to 0.8000" where
  the bisection sat on its floor; relabelled "0.80 or lower". Commit `f531d279`; the least current into U3 per lid added,
  `1c0c88e1`.
- **15:49** `headline_diff.py` (old and new headline lines from git) and its output, `f05b4c4c`.
- **15:54** The page scripts: one note per page (RECONCILE, ENERGY-RECONCILIATION, a1elec README, CHARGER, TOPOLOGY,
  a1solar README, ARRAY, a1mech README), each at the page's title, the first issue's figures left in place; tried on
  scratch copies: each applies once and refuses a second run. The records index row. Commit `2c7bf1c9`.
- **15:58** `apply_registry_s119.py close <commit>`: `--check` against HEAD passed with every script re-run to the byte
  (68 s); applied to a scratch copy of the registry, the diff is S-119 closed, the new item S-121 (the next free number
  today), REQ-072's waits_on and one evidence entry; a second run refuses. The page notes name the new item by the script
  that opens it, since another stream may take S-121 first. Commit `55257c3d`.
- **16:00** README and this log.

Decisions taken (authority SESSION, each reversible by restoring the first issue's line):
1. U3's row is the reference day weighted by energy at entry E2 (0.979, bracket 0.972 to 0.983), not the peak hour's
   figure: the chain applies one efficiency to every hour, and E2 is the design case's entry. Reverse: the peak-hour row
   of efficiency.out section 2 (0.979, the same figure).
2. U3B stays at its drafted 800 kHz row and carries 0.961, the lower of U3B-NOTE's two ways; no 400 kHz decision is
   drafted. The FET choice for U3B's draft is left to its writer as a new open item (two ways stand, and way (a) sits at
   REGN's limit at the makers' maxima); the recommendation given is way (b).
3. The two unpinned importers are issued a second time with pins rather than left with outputs a re-run would not
   reproduce.

## Second round, after the independent check (29 September 2026, times CEST)

- **16:15** The check read in full (`_scratch/chk-s119/CHECK.md`: mergeable yes, 0 blocking, M1 to M7) with the
  coordinator's second-round list: draw U3B's FETs as a SESSION decision, carry U3B over the model's own hours (M1), the
  core-loss room hour by hour and a search for Coilcraft's loss data (M2), M3 to M7.
- **16:18** SLUSE66A re-read for U3B on the 400 kHz row: ILIM_HIZ (pin table, page 6; EN_EXTILIM, the lower limit applies;
  VDDA at REGN through 10 Ohm), Table 9-1 (page 26, no 4.7 uH row; 6.35 A at RSNS_RAC = 0b), FSW 340 / 400 / 460 kHz
  (page 16), 10.2.2.3 (page 85), VOCP_lim_ACX (page 15), PWM_FREQ's text (Table 9-8, page 43). Coilcraft 804-1 page 1
  read for the XAL1010-472ME. The Coilcraft site and its web.archive.org copies answered 403 to this host; no other
  model or search service was used.
- **16:20** energy_two_pack.py: `eta_at` (U3B's efficiency may be a function of its input power, for the analysis scripts),
  a guard for a zero efficiency, U3B's input limit 6.2 A on 10 mOhm, the charge loop 23 mOhm (M3), section 4's rows and
  section 7's losses with the sense resistors inside each charger. `u3b_hourly.py`: U3B's efficiency over the model's own
  hours from efficiency.py's equations; the 800 kHz row reproduces the check's 0.957 to 0.960 and 0.906; the 400 kHz row
  weighs 0.9724 to 0.9736, carried 0.972 (0.963 to 0.978). `inductor_u3b.py`: ripple, peak, RMS and the fault bound at
  400 kHz. efficiency.py's third issue pins energy_two_pack.py (M4) and names the rows before and after. recheck_two_pack.py
  typed the new figures and gained pins (M4): every figure agrees. Commit `37582c04`.
- **16:26** reconcile_lid and reconcile_lid_panel re-pinned and regenerated: adverse 85.5 and 116.6 Wh. Commit `e2361e4e`.
- **16:29** reconcile_s119.py rewritten whole: pins on energy_runs.py and u3b_hourly.py (M4), U3B hour by hour (85.8 and
  116.9 Wh adverse), the failing case, the sensitivity, the room for the core loss per charger in watts hour by hour (M2),
  the planes with U3B hourly. Commit `62bada16`.
- **16:35** The session decision's apply script (`apply_decision_s119.py`); TOPOLOGY.md 3b and CHARGER.md 2 and 3 drawn
  (U3B's parts table and settings, the loss table with the sense resistors counted once: 13.9 W, M3); the page notes
  restated (M6's wording in RECONCILE's note); `apply_records_readme_row.py` with `--check` and exits (M7); headline_diff
  naming file hashes (M5); `apply_registry_s119.py` closing S-119, filing U3B's finding closed and leaving REQ-072 on S-53,
  M-02 and S-114. Commit `c8b148a2`. On scratch copies: the decision applied as 58 and refused a second run; the registry
  closure `--check` re-ran all sixteen scripts to the byte (104 s), applied, and refused a second run.
- **16:45** README rewritten whole for the second round; this log.

Decisions taken in the second round (authority SESSION):
4. U3B on U3's 400 kHz row with the FET pair of decision 57 (drafted for the register by `apply_decision_s119.py`): REGN's
   margin, the lower loss and one part set for both chargers. Reverse: the decision's reversed_by.
5. U3B's row carried as the lowest energy-weighted figure over the model's own hours (0.972), as U3's is carried; the
   hour-by-hour run is printed beside it and reads 0.3 Wh higher in the adverse case, so the carried figure is the
   conservative one. Reverse: carry the peak-hour 0.974.
6. U3B's FET finding filed in the registry as a closed item rather than opened: the draft answers it on this branch, so
   REQ-072 is left waiting on what truly remains (S-53, M-02, S-114).
