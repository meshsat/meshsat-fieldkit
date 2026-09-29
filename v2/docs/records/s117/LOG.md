# Stream s117, running log (MESHSAT-1357, S-117)

Newest last. Times CEST, read from `date`. Prototype framing: nothing is built; every reading is of a committed netlist or
a maker's document. No agent, no other model, no box, no purchase, no contact.

## 29 September 2026 (brief `_runs/claude/s117/BRIEF.md`)

- 12:37 Brief read. Worktree `/home/claude-runner/worktrees/meshsat-fieldkit/s117`, branch `fnd/s117` from main
  `867a18a7`. Read S-117 (`tools/pcb_requirements.yaml`), `records/int11/CHECK.md` B1 and `CHECK-2.md` N1 and N2,
  `records/r4a/r4-open-items.md` O-24 and `r4-decisions.md` R4A-N9, `records/int11/apply_s117_restate.py`, and stream
  d4emcon's LOG row 3 (S-93, board A's LM5176 gate hold: not taken on; this stream touches no LM5176 line). No other branch
  changes `gen_sch_a.py`, `pcb_emc.yaml`, `pcb_decisions.yaml` or `HW-FW-CONTRACT.md` against main.
- 12:40 to 12:50 SLUSE66A read with pdftotext page by page (printed pages mapped from the footers): 9.3.11 and Table 9-4
  (p.27), Table 9-5 and Figure 9-2 (pp.27 and 28, the figure rendered and read), PWM_FREQ in Table 9-8 continued on p.43
  (the brief's "Table 9-9" is REG0x00's table), FSW (p.16), REGN (p.11), the pin table (pp.5 and 6), CIADPT_MAX (p.12),
  Table 9-1 (p.26), 10.2.2.2 to 10.2.2.6 (pp.84 to 88). Coilcraft 887-1 to 887-4 (XAL60xx, one land for 6030 and 6060) and
  804-1 to 804-4 (XAL1010), the L versus current pages rendered and read. TI SLPS632 (CSD18510Q5B) table p.3 and Figures 2
  to 4 p.5 rendered and read. The pack's voltages from `review-packets/battery/FUSE-INTERPRETATION.md`, the front end's
  current limit from `gen_sch_a.py` and `records/a1elec/CHARGER.md`.
- 12:50 Finding: L2 as drawn (XAL6030-332ME, Irms 8.0 A at 40 C rise) does not carry the charger's own input bound (11.8 A
  at a 10.0 V pack) at either row, nor does the XAL6060-472ME on the same land; the XAL1010 land (L1's and L8's) does.
- 12:55 Finding F1: with the drawn CSD18510Q5B, 2 x Qg x fS from REGN is 46 to 60 mA at a typical 400 kHz and 93 to 120 mA
  at 800 kHz, against IREGN_LIM's 50 mA minimum. The 400 kHz row is taken (decision drafted); F1 goes to the registry as
  its own item.
- 12:58 to 13:00 `charger_l_f.py` and `.out`; `apply_gen_sch_a_s117.py` (--check, then a write and a refused second run on a
  scratch copy); `readback_s117.py` (FAIL on the committed netlist, 4 of 17) and `selftest_readback_s117.py` (every case as
  it must). Checkpoint `c03aba4d`.
- 13:00 to 13:02 `apply_emc_s117.py` (emc_sheet.judge in memory: board A 0 failures before and after) and
  `apply_hwfw_s117.py` (FW-A17, V-A05; dry run on a scratch copy, second run refused). Checkpoint `dcd0057e`.
- 13:03 to 13:11 `apply_decision_s117.py` (decision 56 on this tree, SESSION) and `apply_registry_s117.py` (open: F1 as
  S-118, REQ-015 linked, S-115 extended; close: gated on sch_prov, the read-back, the EMC row, FW-A17 and the decision).
  Full dry run in a disposable worktree of this branch (`dryrun.out`), removed afterwards.
- 13:05 main found at `fe97c980` (set 11, committed 12:54: OD-01's package, Option A(i)'s records). None of this stream's
  target files moved; merged at 13:06 as `910494e7` under the owner's identity after the pre-commit check. The a1elec references now
  point at `v2/docs/records/a1elec/` on main.
- 13:12 README written; the U3B statement read from `records/a1elec/TOPOLOGY.md` 3b and `CHARGER.md` 2 (read only).
- 13:13 to 13:16 README and LOG committed (`e48d5a7d`); `readback_s117.py` gains `--against <old.net>` (the regenerated
  netlist held to exactly the drawn change) with three more self-test cases (`a57e69c4`); README corrected in five places
  (the front end's limit cited to SNVSAI1D 6.5, the nominal-pack figure stated with its condition, the XAL1010 order codes,
  Table 9-1's rows, the buck-boost expectation marked INFERRED).

## 29 September 2026, second issue (the coordinator's brief after the independent check, mergeable no on B1 and B2)

- 13:44 Brief read; the check's CHECK.md, `_chk/recompute.py` and `.out` read (not edited). Its drawn-FET figures are the
  ones efficiency.py reproduces.
- 13:45 to 13:50 FETs screened from the makers' own sites by curl (no other tool, no model): TI's CSD17578Q5A,
  CSD17577Q5A, CSD17579Q5A, CSD17581Q5A, CSD17575Q3 and CSD16570Q5B; onsemi refused the runner (403); Nexperia's
  PSMN4R0-30YLD and PSMN5R0-30YL fetched. Tables and the curves of Figures 4, 5 and 7 (p.5) and the PCB patterns (p.9)
  rendered and read. TI's terms forbid redistribution and Nexperia's reserve all rights: five files pinned by sha256 in
  `v2/vendor/sources.txt`, held in ignored folders, fetched by `fetch_held_back.py` (11:47Z and 12:00Z).
- 13:51 to 13:54 `efficiency.py`: the check's method (IL solved, R16 and R17, four readings) reproduced to the third decimal
  on the drawn FETs; the energy model's reference day read through `energy_two_pack.py` unchanged. Checkpoint `fe745dc0`.
- 13:55 to 14:00 The choice: Q7 CSD17578Q5A (fast), Q8 to Q10 CSD17577Q5A (low resistance), 0.979 at the peak by TI's
  method; REGN 10.5 mA; Q9 and Q10 replaced too because TI does not bound the buck-boost region. Drafts: the FET generator
  script, PWR-001's pin roles, the read-back's `--fets`, the FET decision, the registry's F1 restated, F2 opened for the
  energy writer and linked from REQ-072, and a `close-fets` phase. The check's m1 to m7 answered. Checkpoint `7cd95bf9`.
- 14:03 Second dry run in a disposable worktree (`dryrun2.out`), removed; stray bytecode from 12:44 removed from the tools
  folder.
- 14:05 to 14:08 `U3B-NOTE.md`, the energy table, README sections 6 to 12.

## Where the stream stands (resume from here)

Done: the choice and its figures; the efficiency by point and the energy rows; the FET remedy; every apply script with its
check output; the read-back and its self-test; both dry runs. Not done by design: nothing applied to the tree outside this
folder except the held-back pins (`.gitignore`, `v2/vendor/sources.txt`), nothing regenerated, no energy or a1elec record
edited. The integrator's order is README section 8; what stays open is README section 9.
