# Stream s120, running log (MESHSAT-1357, S-120)

Newest last. Times CEST, read from `date`. Prototype framing: nothing is built; every reading is of a committed netlist or
a maker's document. AI engineering work, not a qualified review. No agent, no other model, no box, no purchase, no contact.

## 29 September 2026 (brief `_runs/claude/s120/BRIEF.md`)

- 17:11 Brief and `_bin/WORKER-RULES.md` read. Worktree `/home/claude-runner/worktrees/meshsat-fieldkit/s120`, branch
  `fnd/s120` from main `e57a7365` (set 12: decision 57's FETs on board A, S-117 and S-118 closed, S-120 open). The four held
  TI FET sheets copied from `int13/v2/vendor/ti/held/` into this worktree's ignored `v2/vendor/ti/held/`; their sha256 match
  `v2/vendor/sources.txt` lines 454 to 457 (c8595fa8 CSD17577Q5A, f1aad251 CSD17578Q5A, 05fea7ab CSD17579Q5A, 99d50d88
  CSD17581Q5A). `git check-ignore` confirms the folder is ignored.
- 17:12 to 17:20 Read S-120, S-111 and REQ-015 (`tools/pcb_requirements.yaml`), decision 57 (`tools/pcb_decisions.yaml`),
  `records/s117/README.md`, `gen_sch_a.py` (the LM5176 helper, the front end's call and its comments, the restart guard, U3
  and the FET loop), `gen_sch_e.py` (the vehicle entry and its clamps). Read with pdftotext page by page (printed page equals
  the PDF page in both): SNVSAI1D 6.1 and 6.3 p.5, 6.5 pp.6 to 8, 7.1 p.13, 7.3.11 p.18, 7.4.2 p.20, 8.2.2.12 p.25 and the
  output FET paragraph p.26; SLUSE66A 8.1 and 8.3 p.8, 8.5 pp.9, 11, 13 to 16, the pin table pp.5 and 6, 10.1 and Figure
  10-1 p.83, 10.2.2.1 and 10.2.2.2 p.84, 10.2.2.4 to 10.2.2.6 p.86; SLPS526 and SLPS516 pp.1 and 3; SNVS452G p.5 (OVLOTH);
  Littelfuse SMCJ page 2 of 6.
- 17:20 Findings. The LM5176's OVP threshold is given only as a TYPICAL 10 percent over VREF (p.8), and it reads the same FB
  pin, so it bounds the bus against every in-service mechanism and against nothing that blinds FB. No clamp sits on VBUS20.
  U3's OTG/VAP/FRS pin is on GND, so the charger cannot drive VBUS20. TI prefers 30 V FETs for a 19 to 20 V input (SLUSE66A
  p.86); board A's DC band reaches 20.96 V with the divider's TCR. No TI note giving a layout-independent ringing bound is
  held in the tree (searched `v2/vendor/` and `sources.txt`).
- 17:26 to 17:28 `vbus20_bound.py` (parses both netlists, 18 circuit facts, then sections 2 to 12) and `.out`: bus bound
  23.19 V (the OVP trip at VREF maximum and the worst divider ratio, plus L1's energy at its peak limit), 6.81 V under the
  FETs' 30 V; the switch node INCONCLUSIVE with a 9.04 V budget over the steady bus.
- 17:28 Checkpoint `5a868570` (the script, its output, this log).
- 17:29 to 17:33 `vbus20_bound.py` leaves its figures in `FIG` for the registry script (output unchanged byte for byte);
  the CH_ACN figure is worded as the square root of L it is. `apply_registry_s120.py` drafted (one phase, `close <commit>`).
  `README.md` written: answer (a).
- 17:33 Dry run into `dryrun.out` at `3ca20d5a`: `--check` on the tree's registry writes nothing (sha256/16 c88d7528
  before and after); on a scratch copy one write (S-120 closed, S-123 opened, REQ-015 on S-106, S-107, S-111, S-123, S-111's
  title extended) and a refused second run; refusals for a commit without the records, no commit, and an uncommitted change
  to LOG.md (appended, refused, restored byte for byte); `rules_lib.py requirements` 0 errors and 0 warnings on both copies;
  `vbus20_bound.py` exit 1 on three netlist mutants (R6 249k, U3 pin 5 off GND, a diode on VBUS20). The S-111 wording and
  one refusal message sharpened before the recorded run.
- 17:35 Final commit of the stream (README section 10 and this log).

## 29 September 2026, second round (the check `_scratch/chk-s120/CHECK.md`: not mergeable, B1 to B3, m1 to m11)

- 18:44 Check read in full. Merged main `b874b744` (set 13: S-121 closed, S-122 and S-123 open) into `fnd/s120` as
  `a757e840` with the owner's flags; `vbus20_bound.py` reprinted the committed `.out` byte for byte after the merge (the
  netlists of A and E did not move).
- 18:46 to 18:50 `vbus20_bound.py` rewritten whole (second issue). B1: Q7 and Q8 on separate rows, Q7 carrying Q8's VSD
  1.0 V (SLPS516 p.3) in the margins, the budget and the allowances. B2: the bound printed INFERRED wherever it is stated,
  with its sensitivity for Q7 (37.7 %) and Q8 (42.5 %). m4: L1's largest current is buck mode at U2's 60 V (valley 94 mV plus
  the 1.9 mV of IOFFSET(CS/CSG) across R150 and R151, plus the ripple at the trip), 29.51 A, where the first issue took the
  boost limit's 28.28 A: the bound moves from 23.186 to 23.198 V, printed 23.20 V, so every margin at the bound is 0.01 V
  under the coordinator's figures (Q7 5.80 V, not 5.81). m5: the response time argued (18.6 V per ms at most, 0.37 ms of full
  current past the trip to reach 30 V). m6: the dump takes L1's energy at that largest current (22.24 V at 8.0 A). m7: Q7's
  turn-on (the 6 Ohm driver, the valley current, Q8's Qrr stated only at 300 A/us: INCONCLUSIVE), U3's VBUS pin named, the
  missing CACP and CACN of Figure 10-3 read as a fact. m8: Figure 10-3 p.85; OTG 9.3.9 p.27 and EN_OTG p.64, VAP IN_VAP p.49;
  ACOV, SYSOVP and BATOVP p.14. m9: detail strings print what the netlist holds; VBUS20's whole membership (39 pins) and the
  CELL_BATPRESZ strap (74.76 to 75.51 percent of VDDA against 68.4 to 81.5, p.18) and the CS filter are facts: 21 of 21.
  m1: section 11 rewritten (SW1 near VBAT through Q10's body diode; the order shown for a Q2 short only). Checkpoint
  `fbed9a7b`.
- 18:50 to 18:53 `apply_registry_s120.py`: the three texts rewritten from the new figures (B1, B2, B3, m1, m2, m7, m8);
  `closed_by` resolved to the full sha (m3); `--check` on the merged tree opens S-124 (m10). This log's escaped backticks
  removed (m11). README rewritten whole.
- 18:53 Commit `5078ee24` (README rewritten whole, the registry script, this log). Dry run into `dryrun.out` at `5078ee24` on
  the merged line: `--check` writes nothing (the tree's registry sha256/16 1dde1fd1 before and after); a scratch copy takes one
  write (S-120 closed by the full sha, S-124 opened, REQ-015 on S-106, S-107, S-111, S-124, S-111's title extended) and
  refuses a second run; refusals for e57a7365 (records not carried), 0004b8a7 (README differs), no commit, and an
  uncommitted change to LOG.md (appended, refused, restored byte for byte); `rules_lib.py requirements` 144 records, 0
  errors and 0 warnings on both copies; `vbus20_bound.py` exit 1 on four mutants (R6 249k, U3 pin 5 off GND, a diode on
  VBUS20, a new part on VBUS20), each FAIL line printing what the mutant holds.
