# Draft for the owner of `v2/ecad/tools/pcb_energy_chain.yaml` (closer hc4, handover layer 4, 27 September 2026)

Not applied by hc4: the file is outside this closer's ownership, it is a gate input of `energy_chain.py` (rules BAT-002
and PWR-003), and the PWR-F12 re-declaration of the same file is already drafted by the power stream
(`v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml`). The audit names its writers as the battery-protection stream
(r8bat) and board A's writer (r8a). At `e3aedb25` no round 8 worktree (r8bat, r8int1, r8a) had changed the file.

Found by `v2/docs/diagrams/tools/power_tree.py`, which checks the typed parts of every power-tree stage against the
committed netlists (attribution and connectivity, not function; method and limits in `v2/docs/diagrams/power-tree.md`)
and reads each chain stage's protective element in the board's netlist (`v2/docs/diagrams/power-tree.md`, first
section). Tree `e3aedb25`; chain sha256/16 `935e524eed0ee4d1` (last changed `c161b3d8`, 17 September 2026).

| # | Where in the chain | What it says | What the netlist or ruling says | Proposed | Effect on a gate |
|---|---|---|---|---|---|
| 1 | stage PACK_FETS (`:65-67`); no F2 stage | PACK_FETS runs from FUSED | board P (netlist `4342c4cbe1b43dc4`): F1 CELL4 to FUSED, **F2 SCF9550-30-05 FUSED to SCP_OUT**, Q1 and Q2 SCP_OUT to PACK_P | take the rv-pwr re-declaration (F2 as a stage, 18 A for 60 s) as drafted; it already covers this | energy_chain.py must refuse or pass F2 as a stage; re-take BAT-002 and PWR-003 on P |
| 2 | stage PACK_CELLS `from` (`:46`) and the header (`:19`) | "the 4S block (4S3P or 4S4P, about 200 Wh; gen_sch_p.py header)" | owner ruling D-06: one 4S3P block of Samsung INR18650-35E, about 145 Wh (ARCHITECTURE.md 4.2) | "the 4S3P block of D-06 (12 x INR18650-35E, 144.7 Wh at minimum capacity)"; the prospective fault range may then narrow to the 4S3P figure (47 mOhm plus strip), which only the owner of the arithmetic should restate | text; if the range is narrowed, the fuse coordination checks re-run |
| 3 | stages B_PANEL_5V (`:235`), B_HDMI_5V and B_QMX_5V (the same basis) | prospective fault 6.8 to 9.2 A from "board A's AP64500 buck U7" (diodes-ap64500.pdf IPEAK_LIMIT) | board A (netlist `7b08510106687b3d`): U7 is **LM5176PWPR**, making +5V_DEV through the 6 mOhm shunt R43; its average current loop holds 43 to 57 mV across R43, 7.2 to 9.5 A (`gen_sch_a.py:110-115`, F-PR-04, TI SNVSAI1D VSNS) | basis text to the LM5176 stage and 7.2 to 9.5 A, citing SNVSAI1D and `gen_sch_a.py:110-115` | the three polyfuse stages' fault range moves up by about 0.3 to 0.4 A; B_PANEL_5V's known finding (a 2.0 A hold polyfuse on a 1.23 A track) is unchanged in direction |
| 4 | stage SHORE_INPUT note (`:213-215`) | "an ideal-diode FET and an SMCJ33A clamp sit behind this fuse; decision 31 records that the clamp's 33 V stand-off is wrong" | board E (netlist `d910e49c5f5f50b2`) carries no SMCJ33A: D10 SMCJ40CA on DC_F at the entry, D1 SMCJ40A on DC_P behind the ideal diode and D2 SMCJ40A on VIN_RAW (clamps corrected at `faf8c981`) | note to those clamps, and the decision 31 remark to "corrected at faf8c981" | text only |
| 5 | not in the chain | | board B's net `VBAT` is the CR2032 backup (BT1: the modules' RTCs, the LG290P, the DS3231), board A's `VBAT` is the pack node: one name on two boards, never joined | no chain change; a rename on board B (for example `VBAT_RTC`) is the board B writer's choice and changes nothing electrical | none; a reader or a cross-board tool that joins nets by name would merge them |

After any change: re-run `python3 v2/docs/diagrams/tools/build.py` (the power tree reads the chain) and
`build.py --check` before the handover snapshot.
