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
