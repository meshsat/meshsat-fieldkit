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
