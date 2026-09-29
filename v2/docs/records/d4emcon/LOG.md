# Stream d4emcon, running log (MESHSAT-1357, FEA-002 layout-entry stage)

Newest last. Times CEST, read from `date`. Prototype framing: nothing is built; every reading is of a committed netlist
or a maker's document.

## Resumed 29 September 2026 (brief `_runs/claude/d4emcon/20260929T0200/BRIEF.md`)

- 01:56 Brief and WORKER-RULES read. Branch `fnd/d4emcon` at `88013380` (4 commits ahead of main, 175 behind).
- 01:55 Main (`c5f93464`, set 9) merged with `--no-ff` under the owner's identity: merge commit `fe501d26`, no conflict
  (main had touched none of `tools/tx_inhibit.py`, `tests/test_tx_inhibit.py`, `EMCON.md` or this folder since the
  branch point `73ae2f21`).
- 01:55 to 01:58 Re-run on main's committed netlists, on this host (pure Python, no KiCad needed: the netlists are
  committed files and the tools parse them with `tx_inhibit.parse_netlist`): `tools/path_walk.py`,
  `tools/walk_report.py` (RF-002's walk, `tx_inhibit.py` sha256/16 `326d0a4832273004`, this branch's) and
  `tools/fault_levels.py`. Output under `readings/set9/`. Every reading is byte-identical to the set 6 reading apart
  from the two netlist hashes that moved (A `0a2b59087bcc2678` to `599ee964a9c23d6e`, B `028997a6c5e8810f` to
  `21a1f74a3ec1ae28`). What moved on the netlists is in `readings/set9/WHAT-MOVED.md`.
- 01:59 to 02:08 Board C's L1 lamp row first. New read-only tool `tools/lamp_check.py` (parses C's and B's committed
  netlists, classifies parts with the instrument's own firmware classes): L-1 to L-4 PASS on C `3fddbb3edcd4248a` and B
  `21a1f74a3ec1ae28` (`readings/set9/lamp-check-set9.txt`). One firmware pin sits one resistor from the path (GPIO26
  behind R15 10 k on `LED_RAIL_SW`): it can neither light the lamp nor darken it in DAY or NIGHT.
- 02:05 `tools/fault_levels.py` fixed: a FET's gate current is now looked up by the part's identity (the value's
  leading token), not by any word of its description. Board C's Q7 (Si2300DS, whose value says "like the 2N7002
  symbol") had been read with the JSCJ 2N7002's 25 C row; it now reads the Vishay row (also 25 C only, so the row's
  verdict is unchanged, UNDECIDED). The only line that moved is the lamp's (b) row. `--tag` names the output files.
- 02:08 Finding D4E-F1 (new, L4 case (2) on board C): with board C's +3V3 in its 0 to 1.65 V band and the toggle at
  EMCON, U9's output is unspecified up to 1.65 V on `EMCON_HW`, which board B's readers (VIL 0.8 V at VCC 3 to 3.6 V)
  cannot be shown to read LOW; every board B row reads `EMCON_HW` alone. EMCON.md's L4 row lists C's U9 among the parts
  of case (2) but no section closes or assigns it. Remedy drafted for board C's author (see README and the apply script).
- 02:08 to 02:10 D4E-F1's remedy drafted for board C's author as `apply_c_d4e_f1.py` (U9 pin 4 onto a new net
  `EMCON_HW_DRV`, R52 330R 1 percent to `EMCON_HW`, D23 BAT46W-7-F anode `EMCON_HW` cathode `TX_INHIBIT_n`); dry-run
  on a scratch copy of `gen_sch_c.py` only (applies once, refuses a second run, the result parses). NOT applied to the
  tree, not regenerated, not re-taken.
- 02:10 STOP by the integrator (the owner re-assigned both worker slots). Everything committed as a checkpoint; no box
  was used by this resumption and no process is running here.

## Where the stream stands at the stop (resume from here)

Done: main merged; set 9 re-run (byte-identical to set 6 but for two hashes, `readings/set9/WHAT-MOVED.md`); the lamp
read back (`readings/set9/lamp-check-set9.txt`, CLOSED at desk on C `3fddbb3edcd4248a`); L1 closed at desk on set 9
by RF-002's line reading (`readings/set9/walk/walk-full.txt`: `EMCON_HW` and `TX_INHIBIT_n` PASS, nothing but the
source can drive either); D4E-F1 found and its remedy drafted.

Not started (the next steps, in order): (1) `README.md` of this folder, one row per section 4 row and line item with
CLOSED at desk / OPEN (what closes it, owner) / bench-only, and per board what remains of FEA-002's layout-entry stage;
(2) EMCON.md updated in place with a dated note (the lamp and L1 closed at desk on set 9, D4E-F1 added to L4 and to
section 7, row 2's latency bound below); (3) the back-feed census of SD-EMC-2 for the E22, both E72, the RockBLOCK and
the AW7915 cards (readings so far, not filed: into the E72 the CP2102N's TXD idles HIGH push-pull with no series
resistance, and the gated `+3V3_ZB` has only U22's QOD, 250 to 400 Ohm at 5 V, to hold it; into the E22 nine CM5
slot 3 lines with no series resistance and R25 10 k to `+3V3_S3B` on NSS: both OPEN on the bound, the remedy a series
resistance per line sized against RPD and the module minimum, owner board B's author); (4) U536's L4 band on board B
(RockBLOCK ENABLE, the maker's VIL 0.4 V makes a divider remedy fail: a supervisor on `+3V3_DEV` powered from
`+5V_DEV` with a series resistance is the direction, owner board B's author); (5) row 2's latency at desk: path (b)
VGG falls through R82 plus R83 (81.5 k, 1 percent) with C62 2.2 uF (+20 percent taken) from 4.6 V to 0.5 V in at most
0.48 s, and K1 releases in 3 ms maximum (Omron G6K, stated without saying whether a coil diode is fitted, D2 is), so
the row's bound under 1 s rests on U15's unstated disable delay and on K1 with D2 (both INFERRED milliseconds; bench
E-02); (6) an apply script for FEA-002's evidence line once EMCON.md's new hash is known.

## Resumed 29 September 2026, second time (the integrator's brief of set 10)

- 12:02 Brief read; branch `fnd/d4emcon` at `89815e4f`. Read this log, EMCON.md (sections 0, 0a, 2, 3, 4, 4.4, 4.5,
  4b, 4c, 5a, 6, 7), `apply_c_d4e_f1.py`, FEA-002 (its LAYOUT_ENTRY stage) and S-01, S-02, S-44, S-65, S-87, S-92, S-93.
- 12:03 Main (`7b2caadd`, set 10) merged with `--no-ff` under the owner's identity: merge commit `da31586e`, no conflict.
- 12:03 to 12:04 Re-run on set 10's committed netlists (`readings/set10/`): `netdiff.py` finds no part or net
  difference on any of the six boards against set 9 (only the `source` and `date` header lines moved); the path walk,
  RF-002's walk, the fault levels and the lamp check are byte-identical to set 9 but for the six hashes
  (`readings/set10/WHAT-MOVED.md`). So D4E-F1's anchors in `gen_sch_c.py` and every set 9 reading stand.
- 12:05 to 12:19 The back-feed census of SD-EMC-2 on set 10's board B (`tools/netq.py`, every node of every signal pin of
  J_RB9704, U12, U13, U14 and of the pull-ups on them) and the makers' figures: Ground Control's hardware page (inputs
  "tristate (high-Z) or logic low" with I_BTD low; Logic In LOW 0.4 V max; Logic Out HIGH 2.9 to 3.4 V at 2 mA; P_EN
  "Leaving open or driving LOW enables the charge circuit"); CP2102N Rev 1.5 (IPU 10 to 30 uA; VOH VIO - 0.7 V at 7 mA);
  TPS22810 SLVSDH0C (RPD stated at VIN 5, 12, 18 V only, not at U22's 3.3 V); E72 manual (1.9 to 3.8 V); E22 manual v1.20
  (2.5 to 5.5 V, SPI 0 to 10 Mbps, 3.3 V logic); PCA9555 SCPS131J (IIL -100 uA); SN74LVC2G07 SCES308L; TPS3808 SBVS050N
  (VOL 0.4 V at 1 mA; VIT 2.79 V +-1.25 percent; td 180 to 420 ms with CT to VDD, 12 to 28 ms open; SENSE-to-RESET 20 us
  typical, no maximum); RM520N HD v1.1 Table 9 (FULL_CARD_POWER_OFF# VIL max 0.2 V, VIH min 1.19 V, 100 k pull-down inside).
  Findings: series resistance cannot close the E22 (at the SPI's edge budget, 680 Ohm at most, nine lines hold +5V_LORA at
  about 2.8 V against U21's 400 Ohm RPD, over the module's 2.5 V minimum); the E72 rail's only sink, U22's RPD, is unstated
  at 3.3 V; four RockBLOCK pins carry a live 3.3 V with the module off, against its maker's rule. New finding D4E-F2: U221's
  Tpr hold is not shown under Quectel's 0.2 V VIL (U221 sinks R238's 0.31 mA or more, and SBVS050N states VOL only at 1 mA).
- 12:19 to 12:22 `apply_b_d4e.py` drafted for board B's author (B-1 RockBLOCK gates and pull-downs, B-2 E72 open drains and
  the rail's bleeder, B-3 E22 gates and buffers on slot 3's own 3.3 V, B-4 U543 TPS3808G30 on +5V_DEV holding RB_IEN in
  U536's band, B-5 D4E-F2: U554 SN74LVC2G07 repeats U221, R238 100 k); dry run and a scratch copy: every anchor once, the
  result parses, a second run refused. `tools/readback_d4e.py` written (net by net MUST and MUST NOT nodes, values and
  supply pins, for B and C); on set 10's committed netlists it reads B 56 checks FAIL and C 4 FAIL
  (`readings/set10/readback/`), as it must before regeneration. `apply_c_d4e_f1.py` re-run on a scratch copy of set 10's
  `gen_sch_c.py` (unchanged since `e28f91a6`): applies once, refuses a second run.
