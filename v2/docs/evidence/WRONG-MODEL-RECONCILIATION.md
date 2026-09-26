# The 40 rows newly WRONG_MODEL, reconciled by board and BOM revision

MESHSAT-1357, 26 September 2026. Review of that day (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`,
section 1): "Reconcile all 36 rows newly reported WRONG_MODEL by current board and exact BOM revision. Separate
obsolete order-folder defects from current procurement blockers." Prototype design: nothing is ordered, bought or
built; the order set stays quarantined under owner decision 41.

## Sources (VERIFIED, files read)

| what | where | identity |
|---|---|---|
| the table before the exact-part rule | `v2/release/revA/order/JLC-CERTIFIED.tsv` at `82dd1e4d` (unchanged since `6c06b89c`, 20 September) | git blob `ffa2dbd3`, sha256 `ca82215935b14ad621a74ba29a2ab982a6cef6c1d44f5a45e5e4ffdc7ed3b1a3`, 720 rows |
| the table after the live re-take | the same path at `29f00554` (26 September 09:56 CEST, after `6104cb81`) | git blob `18a6b215`, sha256 `807ed648bf87e92835475178d99350d88435df2cb39c5424187fb6e056f776ea`, 720 rows |
| what the table is built from | every deliverable folder's `*bom.csv` under `v2/release/revA/boards/`, all phases (`v2/ecad/tools/jlc_certify.py:554` `all_boms`, `:571` `rows_to_check`); a row is a distinct (comment, land) | the folder BOMs named per row below, by sha256/16 |
| the current candidate of each board | the netlist in its phase directory at `1f614233`: A `pcb-a-power-a23/out/pcb-a-power.net` aa1372ba3932610f (schematic label A65), B `pcb-b-compute-b19/out/pcb-b-compute.net` 0e72edb5d755316f (B21), C `pcb-c-display-c8/out/pcb-c-display.net` 2834f0d8c4071d56 (C24), D `pcb-d-aprs-d9/out/pcb-d-aprs.net` e2534f5e34c1f5bf (D37P), E `pcb-e1-dock-e7/out/pcb-e1-dock.net` d910e49c5f5f50b2 (E42P), P `pcb-p-pack-p2/out/pcb-p-pack.net` 3c925191447136ac (P4); C, D, E and P are the `faf8c981` corrections | matched by exact (value, land) against the table row |
| round-6 candidates, not merged, read for their direction only | A `wt/r4a/drafts/box/fixup3-run2/repo/pcb-a-power.net` daf132b22fad9854 (14:05), B `wt/r4b/drafts/box/r6-run6/tint/regen/pcb-b-compute.net` af8a9186f981210c (13:18), D `wt/r6d/drafts/box/rf002/new/pcb-d-aprs.net` 9aae5bf93a104abc (14:13) | the same match |
| the quarantined order set | `v2/release/revA/order/PCB-*/` at `29f00554` | every BOM file of each folder: the top-level `*-bom.csv` and, where the folder has one, the `upload/*-bom-jlc.csv` copy (the second revision of this page reads both; the first read only the top-level files) |

The report said 36 rows moved from CERTIFIED to WRONG_MODEL. Keyed by (comment, land), **40** rows are WRONG_MODEL at
`29f00554` that were not at `82dd1e4d`: the 36 from CERTIFIED and 4 from NO_STOCK. All 40 are reconciled here. The 13
rows that were WRONG_MODEL already at `82dd1e4d` were checked the same way: none is on any current netlist.

## Result

| class | rows | boards | what it means |
|---|---:|---|---|
| CURRENT procurement blocker | **27** (all among the 36) | A 12, B 11, E 3, P 1 | the exact (value, land) is on the board's committed candidate netlist; whether a BOM cut from it still fails depends on where the code comes from (next table): 21 codes are typed by generators, 6 came from the earlier table |
| OBSOLETE order-folder row | **13** (9 of the 36, and the 4 from NO_STOCK) | A 5, B 2, A and B 1 (shared), D 1, E 3, P 1 | carried only by deliverable folders of earlier phases; no current netlist has it |

None of the 40 is on the current netlists of boards C or D.

**Current blockers inside the quarantined order set (VERIFIED, every BOM file of `v2/release/revA/order/PCB-*/`
read).** Two of the 27 current rows are carried there with their wrong code, in two folders:

| folder | file:line | ref | row (# below) | code, JLCPCB model | on the committed candidate | named in the folder's readiness block |
|---|---|---|---|---|---|---|
| `PCB-P-PACK-P4` (P declares P4) | `pcb-p-pack-bom.csv:8` (sha256/16 f6430e90fa530a65); the folder has no `upload/` copy | F1 | 27 | C4661, 23.5*16*25 | P `3c925191447136ac`: F1 | yes, `ORDER-NOTES.txt:13` |
| `PCB-B-COMPUTE-B16` (B declares B21; the block says the files are an older phase) | `pcb-b-compute-bom.csv:129` (sha256/16 34e44c6bb1d698e0) and `upload/pcb-b-compute-bom-jlc.csv:129` (74e03ee6ea1349c8) | U9, "DS3231MZ+ holdover clock (I2C 0x68), CR2032 backed", `SOIC-8_3.9x4.9mm_P1.27mm` | 14 | C9866, DS3231SN#T&R (a SOIC-16 part on a SOIC-8 land) | B `0e72edb5d755316f`: U9, and the netlist itself carries field LCSC C9866 (`pcb-b-compute-b19/out/pcb-b-compute.net:11983`) | no: the block (`ORDER-NOTES.txt` lines 1 to 16) names no part, so nothing in the folder flags it |

BT1 (row 13) sits in the same B16 folder and is excluded from the blockers above, for this reason: the top-level BOM
carries it with no code (`pcb-b-compute-bom.csv:2`), so the row's WRONG_MODEL code C70377, which reached only the B19
quote folder, is not ordered from B16. The `upload/` copy is different: `upload/pcb-b-compute-bom-jlc.csv:2` carries
**C5199422** on BT1 (written by the 8 September quote cart, `14f96ffd`). No certification table in this tree names
that code, and `pcb-b-compute-b19/lcsc-allow.txt:18` declares the holder hand-fit because "JLCPCB stocks no CR2032
holder at all". Identity of C5199422: TBD, not queried (`jlc_certify.py` asks JLCPCB's API, which this stream does
not); effect: an order uploaded from that copy would place an unidentified part at BT1. It is not one of the 40 rows
(it is in no table at all) and is carried to the order-set rebuild under Owed.

Two further observations from the `upload/` copies, neither among the 40: `PCB-A-POWER-A22/upload/pcb-a-power-bom-jlc.csv`
lines 37 to 47 carry C3174425 on J_RF1 to J_RF11 under the A22 comment "SMA jack (Amphenol 132134, vertical), pigtail
from the ... device", which the table classes BENCH_FITTED (declared hand-fit, `pcb-a-power-a23/lcsc-allow.txt`) and
which no current netlist carries (A's current rows read "SMA jack, Amphenol 132134-11 vertical (pigtail to the ...
device)", rows 2 to 12): obsolete, but the upload copy and the hand-fit declaration disagree. D's TUSB2046BI row (36)
sits in `order/PCB-D-APRS-D8/`, an order folder of an old phase: obsolete. The retired folders under
`order/superseded/` are not the order set and are not counted; one of them repeats the B16 U9 line
(`superseded/meshsat-pcb-b-revA-B16-quote/pcb-b-compute-bom.csv:129`, C9866).

### The 27 current blockers, by mechanism, with what resolves each

| # rows | board, refs | mechanism (from `jlc_certify.py` and the table notes) | resolution | owner | state |
|---|---|---|---|---|---|
| 11 | A J_RF1 to J_RF11 | the generator types code C3174425 on a row naming Amphenol 132134-11 (`gen_sch_a.py:578`); JLCPCB answers model 132134 | take the code off and route the jack hand-fit as the earlier rows were (`pcb-a-power-a23/lcsc-allow.txt:11` matches "SMA jack (Amphenol 132134", not the new row text; `jlc-handfit.txt:41` names 132134 at Digi-Key), or establish from Amphenol's drawing that 132134 and 132134-11 are one part | board A generator (round-6 A writer) | OPEN. Identity of -11 against the base number: TBD, not checked here |
| 6 | B J_W1A, J_W1B, J_W3A, J_W3B, J_WOA, J_WOB | the generator types C434808 (`gen_sch_b.py:932` to `:934`), answered U.FL-R-SMT(10); the land names U.FL-R-SMT-1 | use C88373: the same table at `29f00554` certifies C88373 as U.FL-R-SMT-1(10) on the same land for B's J_GNSS1 and J_LORA1 and D's J_PAIN | board B generator (round-6 B writer) | OPEN, fix identified from the table itself |
| 3 | B U41, U51, U61 | the row still reads STM32H753VITx with code C114409 (STM32H743VIT6), `gen_sch_b.py:829` | the round-6 B candidate already reads STM32H743VIT6 (owner ruling D-13), which the same code answers; the H753/H743 compatibility proof of condition 1 goes with it | round-6 B integration | OPEN until merged; direction verified in the candidate netlist |
| 1 | B U9 | code C9866 is typed on DS3231MZ+ (`gen_sch_b.py:751`); JLCPCB answers DS3231SN#T&R, a SOIC-16 part, on a SOIC-8 land | take the code off and declare a purchase route, or choose a stocked part the land fits | board B generator | OPEN; JLCPCB availability of DS3231MZ+: TBD, not queried (no outside contact) |
| 1 | B BT1 | the row carries no code in the generator (`gen_sch_b.py:599`); C70377 reached the B19 quote BOM from the earlier table. `pcb-b-compute-b19/lcsc-allow.txt:18` declares it hand-fit | a BOM cut from the current design is answered by that declaration, because lcsc_fill no longer fills the code (probe below) | next B BOM cut | resolves at the next cut, INFERRED from code |
| 5 | A F1; E F1, F2, F3; P F1 | the rows name no part number on the Keystone 3568 land and carry no code in the generators (`gen_sch_a.py:161`, `gen_sch_e.py:194`, `:233`, `:380`, `gen_sch_p.py:244`); C4661 (XSD's "23.5*16*25", no package; its maker's sibling C4650 is a heat sink) and C10081 (model GL5528(10-20), not a fuse holder) entered the folder BOMs through lcsc_fill from the earlier table (`jlc_certify.py:887` to `:898`) | a BOM cut from the current design gets no code (probe below). The 25 A rows are then answered by A's declaration `pcb-a-power-a23/lcsc-allow.txt:17` ("25 A mini blade (Keystone 3568"), which the certifier merges across boards (`jlc_certify.py:667` to `:677`). E's two 10 A rows match no declaration, and `jlc-handfit.txt:66` ("3568") is never tried because the certifier takes part tokens of five characters or more (`jlc_certify.py:650`) | E's `lcsc-allow.txt` declares the 10 A holder; the P4 order BOM's C4661 goes with the next cut | E generator or allow list; order-set rebuild | OPEN for E F1/F2 (INFERRED: they would read NOT_IDENTIFIED or NOT_AT_JLC without a declaration, not verified because `jlc_certify.py` queries JLCPCB's API); P4 order line 8 OPEN |

**Probe (VERIFIED, run 26 September 2026 on the runner, offline):** the 27 rows written blank into a one-sheet BOM and
passed through this tree's `lcsc_fill.py` (`VERDICT_DIR` in the scratchpad): 0 lines filled, 27 left blank. The
earlier table's CERTIFIED rows no longer propagate a wrong code. The codes that remain are the ones generators type.

### The 13 obsolete rows

All carried only by folders of earlier phases (A19 to A21, B13 to B15, D8 to D11, E4, P1 to P2); none is on a
current or round-6 candidate netlist. Two notes where the same land is live today:

- A's 10 A and 15 A fuse rows (rows 28 to 31 below) are gone with A19 to A21, but A's F1 on the same Keystone 3568
  land is current (row 1).
- B's "CM5 cooler fan (JST-SH 1.0)" row is gone; the current B carries J_FAN1 to J_FAN3 on the same
  `JST_SH_BM04B-SRSS-TB` land under a new comment, which is not in the table at all (next section).

## What the table does not cover

The table is built from deliverable folders, and no current candidate has one (the layouts predate the corrected
netlists). Matched the same way, the committed candidate netlists carry distinct (value, land) component rows that no
table row covers, after the certifier's own lead, header and test-point filters (`jlc_certify.py` LEAD and BENCH_FP):
**A 5, B 4, C 6, D 18, E 9, P 12**, among them P's Eaton SCF9550 chemical fuse and the round-4 clamps on D, E and P.
Those parts are not certified for procurement by anything today. This is not a WRONG_MODEL finding; it is the bound
on what the 40 rows can say, and it closes only when the certification is taken over the current candidates' BOMs.

## Per row (VERIFIED against the files named above)

Folder BOMs by sha256/16; "(declared)" marks the folder of the phase the board declares. Round-6 column: "absent"
means the candidate netlist exists and lacks the exact row (A's F1 is renamed there, "pack node to the RSR shunt",
on the same land). The "order set" column names the order folder whose BOM carries the row by (comment, land), NOT by
code: row 13 (BT1) names PCB-B-COMPUTE-B16 because its BOMs carry the CR2032 holder at BT1, with no code at top level
and C5199422 in `upload/`, not C70377 (the section on current blockers above says so line by line).

| # | class | board | row (comment, land) | code, JLCPCB model | carried by (folder, BOM sha256/16) | current netlist | round-6 candidate | order set |
|---|---|---|---|---|---|---|---|---|
| 1 | CURRENT | A | 25 A mini blade (Keystone 3568 holder): pack node to VBAT; `Fuseholder_Blade_Mini_Keystone_3568` | C4661, 23.5*16*25 | a-revA-A22 a5b73f33d2b2b52e; a-revA-A24 f59f0c5ecc5c74fa | A: F1 | absent | none |
| 2 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the 5G-DIV device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF9 | A: J_RF9 | none |
| 3 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the 5G-MAIN device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF8 | A: J_RF8 | none |
| 4 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the GNSS device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF4 | A: J_RF4 | none |
| 5 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the HF device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF2 | A: J_RF2 | none |
| 6 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the IRID device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF10 | A: J_RF10 | none |
| 7 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the LORA device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF11 | A: J_RF11 | none |
| 8 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the P2P-A device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF6 | A: J_RF6 | none |
| 9 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the P2P-B device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF7 | A: J_RF7 | none |
| 10 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the SDR device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF5 | A: J_RF5 | none |
| 11 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the VHF device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF1 | A: J_RF1 | none |
| 12 | CURRENT | A | SMA jack, Amphenol 132134-11 vertical (pigtail to the WIFI24 device); `SMA_Amphenol_132134-11_Vertical` | C3174425, 132134 | a-revA-A24 f59f0c5ecc5c74fa | A: J_RF3 | A: J_RF3 | none |
| 13 | CURRENT | B | CR2032 holder Keystone 3034: VBAT for the three modules' RTCs, the LG290P backup and the D; `BatteryHolder_Keystone_3034_1x20mm` | C70377, CR2032-BS-6-1 | b-revA-B19-quote 931f4a6e5b8c1707 | B: BT1 | B: BT1 | PCB-B-COMPUTE-B16 |
| 14 | CURRENT | B | DS3231MZ+ holdover clock (I2C 0x68), CR2032 backed; `SOIC-8_3.9x4.9mm_P1.27mm` | C9866, DS3231SN#T&R | b-revA-B19-quote 931f4a6e5b8c1707 | B: U9 | B: U9 | PCB-B-COMPUTE-B16 |
| 15 | CURRENT | B | STM32H753VITx I/O supervisor A: 2-of-3 quorum on two CAN-FD fabrics, bank ownership and hu; `LQFP-100_14x14mm_P0.5mm` | C114409, STM32H743VIT6 | b-revA-B19-quote 931f4a6e5b8c1707 | B: U41 | absent | none |
| 16 | CURRENT | B | STM32H753VITx I/O supervisor B: 2-of-3 quorum on two CAN-FD fabrics, bank ownership and hu; `LQFP-100_14x14mm_P0.5mm` | C114409, STM32H743VIT6 | b-revA-B19-quote 931f4a6e5b8c1707 | B: U51 | absent | none |
| 17 | CURRENT | B | STM32H753VITx I/O supervisor C: 2-of-3 quorum on two CAN-FD fabrics, bank ownership and hu; `LQFP-100_14x14mm_P0.5mm` | C114409, STM32H743VIT6 | b-revA-B19-quote 931f4a6e5b8c1707 | B: U61 | absent | none |
| 18 | CURRENT | B | U.FL: MHF4 pigtail from the slot 1 WiFi card, chain A; `U.FL_Hirose_U.FL-R-SMT-1_Vertical` | C434808, U.FL-R-SMT(10) | b-revA-B19-quote 931f4a6e5b8c1707 | B: J_W1A | B: J_W1A | none |
| 19 | CURRENT | B | U.FL: MHF4 pigtail from the slot 1 WiFi card, chain B; `U.FL_Hirose_U.FL-R-SMT-1_Vertical` | C434808, U.FL-R-SMT(10) | b-revA-B19-quote 931f4a6e5b8c1707 | B: J_W1B | B: J_W1B | none |
| 20 | CURRENT | B | U.FL: MHF4 pigtail from the slot 3 WiFi card, chain A; `U.FL_Hirose_U.FL-R-SMT-1_Vertical` | C434808, U.FL-R-SMT(10) | b-revA-B19-quote 931f4a6e5b8c1707 | B: J_W3A | B: J_W3A | none |
| 21 | CURRENT | B | U.FL: MHF4 pigtail from the slot 3 WiFi card, chain B; `U.FL_Hirose_U.FL-R-SMT-1_Vertical` | C434808, U.FL-R-SMT(10) | b-revA-B19-quote 931f4a6e5b8c1707 | B: J_W3B | B: J_W3B | none |
| 22 | CURRENT | B | U.FL: pigtail to A22's P2P jack, chain A; `U.FL_Hirose_U.FL-R-SMT-1_Vertical` | C434808, U.FL-R-SMT(10) | b-revA-B19-quote 931f4a6e5b8c1707 | B: J_WOA | B: J_WOA | none |
| 23 | CURRENT | B | U.FL: pigtail to A22's P2P jack, chain B; `U.FL_Hirose_U.FL-R-SMT-1_Vertical` | C434808, U.FL-R-SMT(10) | b-revA-B19-quote 931f4a6e5b8c1707 | B: J_WOB | B: J_WOB | none |
| 24 | CURRENT | E | 10 A mini blade (Keystone 3568 holder): panel input; `Fuseholder_Blade_Mini_Keystone_3568` | C10081, GL5528(10-20) | e-revA-E6 d4edc62fa1fc1c3f; e-revA-E7 033d26ec324de498; e-revA-E9 4b9f0664542f73b0 | E: F2 | no round-6 candidate | none |
| 25 | CURRENT | E | 10 A mini blade (Keystone 3568 holder): vehicle input; `Fuseholder_Blade_Mini_Keystone_3568` | C10081, GL5528(10-20) | e-revA-E6 d4edc62fa1fc1c3f; e-revA-E7 033d26ec324de498; e-revA-E9 4b9f0664542f73b0 | E: F1 | no round-6 candidate | none |
| 26 | CURRENT | E | 25 A mini blade (Keystone 3568 holder): pack to the block; `Fuseholder_Blade_Mini_Keystone_3568` | C4661, 23.5*16*25 | e-revA-E6 d4edc62fa1fc1c3f; e-revA-E7 033d26ec324de498; e-revA-E9 4b9f0664542f73b0 | E: F3 | no round-6 candidate | none |
| 27 | CURRENT | P | 25 A mini blade (Keystone 3568 holder): the pack's fuse; `Fuseholder_Blade_Mini_Keystone_3568` | C4661, 23.5*16*25 | p-revA-P1 7b319dd178c332eb; p-revA-P2 6ab92c9570f266af; p-revA-P3 57a9a5ba3a7d0bba; p-revA-P4 (declared) 57a9a5ba3a7d0bba | P: F1 | no round-6 candidate | PCB-P-PACK-P4 |
| 28 | OBSOLETE | A | 10 A mini blade (Keystone 3568 holder): pack node to the 8 V boost feed; `Fuseholder_Blade_Mini_Keystone_3568` | C4650, 15*10*20 UType heat sink White | a-revA-A19 9602f568967434f8; a-revA-A20 1e2991530bc611c2; a-revA-A21 1e2991530bc611c2 | absent | absent | none |
| 29 | OBSOLETE | A | 10 A mini blade (Keystone 3568 holder): pack node to the M1 converter; `Fuseholder_Blade_Mini_Keystone_3568` | C4650, 15*10*20 UType heat sink White | a-revA-A19 9602f568967434f8; a-revA-A20 1e2991530bc611c2; a-revA-A21 1e2991530bc611c2 | absent | absent | none |
| 30 | OBSOLETE | A | 10 A mini blade (Keystone 3568 holder): pack node to the M2 converter; `Fuseholder_Blade_Mini_Keystone_3568` | C4650, 15*10*20 UType heat sink White | a-revA-A19 9602f568967434f8; a-revA-A20 1e2991530bc611c2; a-revA-A21 1e2991530bc611c2 | absent | absent | none |
| 31 | OBSOLETE | A | 15 A mini blade (Keystone 3568 holder): pack node to the Pi converter; `Fuseholder_Blade_Mini_Keystone_3568` | C2467, FR157 | a-revA-A19 9602f568967434f8; a-revA-A20 1e2991530bc611c2; a-revA-A21 1e2991530bc611c2 | absent | absent | none |
| 32 | OBSOLETE | A | 3 mOhm 1% 3 W 2512 shunt (RALEC LR2512-23R003F4): gauge SRP/SRN Kelvin (32.24 AV); `R_2512_6332Metric` | C154688, LR2512-23R005F4 | a-revA-A19 9602f568967434f8; a-revA-A20 1e2991530bc611c2; a-revA-A21 1e2991530bc611c2 | absent | absent | none |
| 33 | OBSOLETE | A,B | USB2517I-JZX seven-port USB 2.0 hub (strap defaults, ports 6-7 disabled); `QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm` | C1521556, USB2517-JZX | a-revA-A19 9602f568967434f8; b-revA-B13 f76b1fe38655ed77; b-revA-B14 1cc6a03e235ce1f4; b-revA-B15 1cc6a03e235ce1f4 | absent | absent | none |
| 34 | OBSOLETE | B | CM5 cooler fan (JST-SH 1.0): 5V GND TACHO PWM; 5 V from the Pi rail so the fan stops with ; `JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical` | C160404, SM04B-SRSS-TB(LF)(SN) | b-revA-B13 f76b1fe38655ed77; b-revA-B14 1cc6a03e235ce1f4; b-revA-B15 1cc6a03e235ce1f4 | absent | absent | none |
| 35 | OBSOLETE | B | Touch Display 2 FPC 22-pin 0.5 mm (Hirose FH12-22S-0.5SH), Standard-Mini 22-to-15 cable; `Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal` | C9900246727, F_22PIN | b-revA-B13 f76b1fe38655ed77; b-revA-B14 1cc6a03e235ce1f4; b-revA-B15 1cc6a03e235ce1f4 | absent | absent | none |
| 36 | OBSOLETE | D | TUSB2046BI four-port USB 2.0 full-speed hub (LQFP-32; BUSPWR low = self-powered, EXTMEM hi; `LQFP-32_7x7mm_P0.8mm` | C167642, TUSB2046BVFR | d-revA-D10 6ee4ea42deced5fb; d-revA-D11 11d96a7f283afdca; d-revA-D8 61928f0559028793; d-revA-D9 bee4e3b5d9dfeae5 | absent | absent | PCB-D-APRS-D8 |
| 37 | OBSOLETE | E | 10 A mini blade (Keystone 3568 holder, in the clear band): panel input; `Fuseholder_Blade_Mini_Keystone_3568` | C4650, 15*10*20 UType heat sink White | e-revA-E4 dd7d0cf8041fc156 | absent | no round-6 candidate | none |
| 38 | OBSOLETE | E | 7.5 A mini blade (Keystone 3568 holder, in the clear band): 3.7 A at 12 V full load, 5 A a; `Fuseholder_Blade_Mini_Keystone_3568` | C9900125840, 7.5u | e-revA-E4 dd7d0cf8041fc156 | absent | no round-6 candidate | none |
| 39 | OBSOLETE | E | module thermistor lead (XH2.5): 103AT to the charger TS pin over the block; `JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` | C2975490, SD103ATW-TP | e-revA-E4 dd7d0cf8041fc156 | absent | no round-6 candidate | none |
| 40 | OBSOLETE | P | cell thermistor (JST-PH 1x2): the 103AT in the block; `JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical` | C2975490, SD103ATW-TP | p-revA-P1 7b319dd178c332eb; p-revA-P2 6ab92c9570f266af | absent | no round-6 candidate | none |

## Owed, outside this stream's files

- Round-6 A writer: the eleven SMA rows (code or declaration) and F1's declaration under its new comment.
- Round-6 B writer: C88373 on the six U.FL rows; U9's code; the H743 text lands with the compatibility proof.
- Board E owner: a declaration for the two 10 A Keystone 3568 holders.
- Order-set rebuild (decision 41 follow-up, after layout): P4's F1 line (`PCB-P-PACK-P4/pcb-p-pack-bom.csv:8`);
  B16's U9 line (`PCB-B-COMPUTE-B16/pcb-b-compute-bom.csv:129` and `upload/pcb-b-compute-bom-jlc.csv:129`) and its
  BT1 upload line (`upload/pcb-b-compute-bom-jlc.csv:2`, C5199422, identity TBD), and B16's readiness block, which
  names neither; the `upload/` copies reconciled with the hand-fit declarations (A22's eleven SMA lines); certification
  taken over the current candidates' BOMs, which needs a BOM per candidate and a `jlc_certify.py` run (it queries
  JLCPCB's API, so it runs in the ordering session or on the box, not from here). Nothing is ordered from the set
  meanwhile (owner decision 41).
