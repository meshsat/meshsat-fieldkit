# Citations carried by fnd/hc3's apply script and re-read by hand at the r8int4 integration

MESHSAT-1357, 27 September 2026, branch `fnd/r8int4` from main `38dcd764` (board B's round 8 and H1.1 on main). The
layer-3 closer's apply script (`records/hc3/apply_registry.py`) accepts a citation whose text was rewritten where it
stood only on a file the closer read by hand (`records/hc3/reviewed-citations.json`, `reviewed-pairs.json`). On this
tree it refused the twenty below, because main moved after the closer's simulation on `a8652172` (board B's round 8
changed `gen_sch_b.py`, `ARCH-PCB-B-IOHA.md`, `PANEL.md` and `V2-SPEC.md`) and because this integration edited
`V2-SPEC.md` line 29 (NEED-03, correction 29), `OPERATING-ENVELOPE.md` section 4 and `pcb_envelope.yaml`. Each was
read here, old text against new (`--citation-report`), against what its record relies on. All twenty still say it,
so the registry change was applied without re-anchoring first (`--no-reanchor`, documents and registry in one
commit) and the re-anchoring was run afterwards with `--accept-rewritten`. Prototype design: nothing here is measured.

| Record | Citation (at `eadbe571`, now) | What the record relies on | Read |
|---|---|---|---|
| REQ-001, REQ-002, CHO-001 | `V2-SPEC.md:37-51`, same lines | the bearers and radios table | the same table; round 8 and the layer-1 closer changed cells, not the table's rows: holds |
| REQ-006 | `V2-SPEC.md:29`, same line | NEED-03's requirement row | the same row, with "four shared elements are outside it (correction 29)" added: holds |
| CFL-016, SPD-006 (historical) | `V2-SPEC.md:76`, same line | the owed list as it read | kept as history by the script: holds |
| SPD-006, CFL-010 (historical) | `V2-SPEC.md:41`, same line | the cellular row as it read | kept as history by the script: holds |
| CON-003 | `ARCH-PCB-B-IOHA.md:87-89`, now 87-93 | section 5's items 2 and 3 (fail-safe defaults, break before make) | the same items with their corrections and round 8's drawn text: holds |
| CON-003 | `ARCH-PCB-B-IOHA.md:178-189`, now 185-205 | the pull-downs and the break-before-make paragraph | the same paragraphs with the corrections of FAB-03 and FAB-04: holds |
| CON-004, CON-020 | `ARCH-PCB-B-IOHA.md:96`, now 102 | the supervisors' status path on the kit I2C bus | the same paragraph, addresses now 0x34 to 0x36 (I3-F01): holds for the path; CON-020's own statement still says 0x30 to 0x32 (a registry item, listed as remaining) |
| REQ-024 | `OPERATING-ENVELOPE.md:128-139`, now 205-247 | section 4's carve-out list | the same list, the hot end restated on measured temperatures: holds |
| ASM-004 | `pcb_envelope.yaml:36-41`, now 37-95 | the 10 K and 16 K rise estimates | the same keys, marked superseded, with the bounds after them: holds |
| CFL-003 (historical) | `pcb_envelope.yaml:15-19`, same lines | the envelope file's pin as it read | kept as history by the script: holds |
| REQ-032 | `gen_sch_b.py:716-741`, now 813-880 | the module radios' EMCON disables | round 8's U{s}12 to U{s}15, the same function run from each module's own 3.3 V: holds |
| REQ-032 | `gen_sch_b.py:449-456`, now 511-531 | the WiFi cards' supply removed by EMCON | the same block, with slot 2's supply removal added: holds |
| CON-020 | `gen_sch_b.py:1140`, now 1381-1387 | the supervisor's I2C pins | the same pin map (92 SCL, 93 SDA), with the I3-F01 comment: holds |
| CFL-010 (historical) | `gen_sch_b.py:672-697`, now 759-794 | the SIM section as it read | kept as history by the script: holds |
| REQ-040 | `PANEL.md:144`, now 170-171 | the 0x68 holdover clock row | the 0x68 row (DS3231SN, U9), with the 0x60 row beside it: holds |

Two readings the script left for a hand re-read (`HAND RE-READ`) were read and rebound by
`r8int4/post_c23_registry.py`: CFL-016 on `CONOPS.md` (the EMCON row now states the 5G module's supply removed by
hardware, board B's round 8) and on `V2-SPEC.md` (line 41's closing clause). Two warnings left after it were read and
rebound by `r8int4/post_c23_registry2.py`: REQ-052 on `gen_sch_b.py` (round 8 moves no device between banks) and
CFL-006 on `pcb_energy_chain.yaml` (the 4S3P block named at lines 19 and 46). The script's one expected refusal,
CON-025's FAIL reading taken on `gen_sch_b.py` at `dedaf34ce285e5ff`, does not apply: main carries board B's round 8,
on which the PASS reading (TPD4E001 U222 and U223) was written.
