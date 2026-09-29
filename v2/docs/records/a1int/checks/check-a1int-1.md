acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). B1 and M3, M7 answered by reconcile_lid_panel.py's second issue (U3 at its minimum 6.1 A and the 6.0 A bracket, U3B at code 62, the model pinned); M1, M2, M6 stated in its notes; M4, M5 in RECONCILE.md; M8 recorded there. The checker's own scripts stay in its scratch clone. -->

# AI review: independent check of the two-pack lid reconciliation, fnd/a1int at 7613c072 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. Every figure below is a model result on the September
reference day (nothing is built or measured). Checked 29 September 2026, 12:01 to about 12:40 CEST, in a shared clone
detached at 7613c0720d4c56cb07c57ba5d4b718c478125c01. Read-only on every worktree; my scripts and outputs are in
`_chk/` (untracked): `indep.py` (my own two-store balance, which imports neither energy_budget.py nor
energy_two_pack.py), `sens.py`, `prod_sens.py`, `ledger.py`, `planes.py`, their `.out` files, and `txt/` (pdftotext of
SLUSE66A, the 35E spec and the XT60 sheet).

Materiality used: blocking = a verdict changes, a quoted lowest store moves by more than 5 percent or a quoted lid
threshold by more than 0.5 K, a modelled current or power exceeds a recorded limit, or the 72 h balance does not close.

**Verdicts at the lid basis (13.23 C) all stand**: 4S9P NOT MET under A, B and C and at +40 C; 4S14P and 4S15P MEET
under A, B and C, in the production model and in mine, with every sensitivity below. One margin set does not stand as
quoted: the adverse-ratio (C) figures.

## Blocking items

**B1. The ratio-C lowest stores and lid thresholds hold only for a NOMINAL U3 input limit.**
`reconcile_lid_panel.py` lines 45-46 run `TP.base_cfg()`'s entry E2, which caps U3's input at IIN_HOST 6.2 A nominal
(`energy_two_pack.py` line 138). CHARGER.md's own rule is that a limit holding a load is taken at its minimum.
SLUSE66A prints no 10 mOhm accuracy row; its 5 mOhm rows are plus or minus 200 mA about the code (8.5, page 10:
7,800 mA gives 7,600 / 7,800 / 8,000), and 9.6.22 (page 80) adds 100 mA for the maximum at 10 mOhm, so the 10 mOhm
minimum reads as 6.1 A (6.0 A on the printed 5 mOhm spread). The earlier check's N5 found the 4S12P case at ratio A
insensitive down to 5.85 A; that does not carry to ratio C, where the packs no longer refill each day and the E2 cap
binds for five hours (G at or above 433 W/m2). Both models agree (production model with the cap re-set, `prod_sens.out`;
mine, `sens.out`):

| case | as claimed | U3 at 6.1 A | U3 at 6.0 A | smallest U3 IIN that meets at 13.23 C |
|---|---|---|---|---|
| 4S14P, C: lowest both / lid threshold | 90.9 Wh / +4.1 C | 87.4 Wh / +5.95 C (+4.6 C at 0.1 h steps) | 77.6 Wh / +6.1 C | 5.57 A |
| 4S15P, C: lowest both / lid threshold | 122.4 Wh / +2.1 C | 118.5 Wh / +2.2 C | 108.7 Wh / +4.0 C | 5.43 A |
| 4S14P, B and 4S15P, B | 93.7 / 125.2 Wh, +3.8 / +1.5 C | unchanged | unchanged | 5.32 A / 5.18 A |

Fix: in `reconcile_lid_panel.py` add U3's IIN_HOST at its minimum as a run (the entry dict with `u3_in_w` = 6.1 x 20.7,
state the reading, and 6.0 A as the bracket) and print the C rows at it; in RECONCILE.md lines 42-44 and in the owner's
figures, quote the C case as 87.4 Wh and +6.0 C (4S14P) and 118.5 Wh and +2.2 C (4S15P), or say plainly that 90.9 /
122.4 Wh and +4.1 / +2.1 C assume a nominal U3. The B figures stand.

## Claims against my independent model

Mine uses the same inputs (energy_inputs.yaml, the pinned PVGIS monthly file, energy_runs.out section 2, the circuit
figures of TOPOLOGY.md and CHARGER.md) with its own code; at a 1 h step it reproduces every production figure to 0.05 Wh.

| claim | independent (1 h / 0.01 h step) | production | agree | reason for any difference |
|---|---|---|---|---|
| 4S9P A, B, C NOT MET, 164.8 / 165.6 / 172.5 Wh unserved, not at +40 C | same, stops [23, 11] | same | yes | |
| 4S14P B MEETS 93.7 Wh (base 49.0, lid 44.7) | 93.7 / 92.9 | 93.7 | yes | 0.8 Wh: hourly taper (M1) |
| 4S14P C MEETS 90.9 Wh | 90.9 / 88.5 | 90.9 | yes on its basis | 2.4 Wh: M1; B1 at a minimum U3 |
| 4S15P B MEETS 125.2 Wh (57.1, 68.1) | 125.2 / 124.4 | 125.2 | yes | 0.8 Wh: M1 |
| 4S15P C MEETS 122.4 Wh | 122.4 / 120.0 | 122.4 | yes on its basis | 2.4 Wh: M1; B1 |
| lid thresholds +3.8 / +4.1 (14P B / C) | +3.82 / +4.10 (1 h); +3.91 / +4.33 (0.1 h) | +3.82 / +4.10 | yes | B1 moves C |
| lid thresholds +1.5 / +2.1 (15P B / C) | +1.50 / +2.10 (1 h); +1.59 / +1.99 (0.1 h) | +1.50 / +2.10 | yes | B1 moves C |
| ratios applied as energy_runs.py applies them | `r["pr"]` replaced, 40/0 profile, E2 | same code path | yes | |
| results hold on the 40 degree south plane | only 40/0 was run | only 40/0 | yes | M5 on the plane text |
| energy balance closes over 72 h | closes to 1e-12 Wh with a named clamp term | closes only with 23.1 to 57.8 Wh unreported | yes, once named | M2 |
| equal-SOC allocation (TOPOLOGY 3b's law) instead of the capacity split | 14P 93.7 / 90.9; 15P 125.2 / 122.4 (charge); 93.9 / 84.5, 125.4 / 122.6 (charge and discharge) | not run | n/a | only 14P C moves (-6.4 Wh), verdict holds |

## Limits against the lid charge current and the stage

Settings: the reconciliation scales U3B's ChargeCurrent to 9.259 A (4S14P) and 9.920 A (4S15P). Modelled flows (both
models, every hour of both starts): lid charge at most 3.88 A (14P) and 3.96 A (15P) at the terminals, U3B input at
most 58.1 / 59.3 W (4.01 / 4.09 A from VBAT at 14.50 V), lid discharge at most 2.07 / 2.11 A, node at most 125.8 W.
The E2 cap, not the charger setting, sets the lid current; clipping U3B to 7.936 A leaves every figure unchanged.

| limit | source, page | value | setting / modelled | within |
|---|---|---|---|---|
| U3B ChargeCurrent range and step (5 mOhm RSR) | SLUSE66A 9.6.2, p.45; Table 9-7, p.40 | 0 to 16.256 A, 128 mA | 9.259 / 9.920 A are not codes (72 = 9.216 A, 77 = 9.856 A) | range yes |
| U3B charge-current accuracy | SLUSE66A 8.5, p.10 | +-3 % at 8.192 A | setting maximum 9.54 / 10.22 A | see OCC1 |
| lid gauge OCC1 | GAUGE.md 4; TOPOLOGY 4 | 10.0 A true, 2 s | modelled 3.88 / 3.96 A; 15P setting max 10.22 A | modelled yes; 15P setting no (M3) |
| lid gauge charge current and host cap | GAUGE.md 4-5; TOPOLOGY 3b, 4; CHARGER 2 | 8.0 A true; U3B at most 7.936 A | settings 9.26 / 9.92 A; modelled 3.96 A | modelled yes; settings no (M3) |
| gauge Low Temp range (T1-T2 = 1-12 C), where the thresholds lie | GAUGE.md 4; PRIMARY-CONFIGURATION 2 | 4.0 A true | modelled 3.88 / 3.96 A | yes (0.04 A spare at 15P) |
| gauge design-capacity word (I2) | SLUUAQ3A 14.13.5.2, p.180; GAUGE.md 3 | 32,767 | at k = 2: 33,768 (14P), 36,180 cWh (15P) | no: k = 3 for both (M4) |
| U3B IIN_HOST | TOPOLOGY 3b; SLUSE66A 8.5, p.10 | 8.0 A (116.0 W) | 4.01 / 4.09 A | yes |
| LM5069-2 limit at its minimum | SNVS452G p.6 via TOPOLOGY 3c | 8.7 A | discharge 2.11 A; 10 A kit share 7.00 / 7.14 A; charge does not pass it (UVLO held low while U3B runs) | yes |
| LM74700-Q1 ideal diode | SNOSD17G 6.5, p.6 | V(AK) 13 / 20 / 29 mV | 20 mV at 2.1 A | yes |
| U3 IIN_HOST (entry E2) | CHARGER.md 1-2 | 6.2 A nominal; need 5.56 A (12P) | need 5.57 / 5.43 A at C | verdict yes; margins B1 |
| LM5176 front end at its minimum | SNVSAI1D 6.5, p.7 via CHARGER 2 | 6.94 A, 143.6 W | 128.3 W | yes |
| stage window | CHARGER.md 1 | 200 W in | panel into the stage at most 194.2 (B) / 178.6 W (C); E2 lets through at most 148.3 W | yes (never clips) |
| F_LA, board A's end of the lid lead | TOPOLOGY 4 (Littelfuse 297) | 15 A MINI | 9.92 A setting | yes |
| J_LID XT60 | amass-xt60-spec-tme.pdf | 30 A rated | 9.92 A | yes |
| hinge harness 12 AWG | TOPOLOGY 9 (no maker rating held) | assumed at most 7.936 A charging | settings above it; modelled 3.96 A | modelled yes |
| 35E cell charge | spec 3.5, 3.7, 3.12 | 2.0 A max, 1.02 A cycle life, 0 to 45 C | 0.661 A a cell set, 0.28 A modelled; thresholds 1.5 to 4.3 C over the gauge's UTC 1.0 C | yes |

Usable capacity: the lid's temperature factor (energy_inputs line through -10 C 0.4124 and +20 C 1.0) is 0.8674 at
13.23 C, 0.683 at 3.8 C and 0.638 at 1.5 C; full stores 660.5 Wh (14P) and 692.1 Wh (15P) at the basis. The line is a
lower bound at the lid's 0.15 A a cell (energy_inputs.yaml), so the thresholds err toward NOT MET.

## Minor items

- **M1** (energy_two_pack.py lines 229-250): the taper cap is evaluated once per hour, and the store is clamped at
  full; the base's taper time constant is about 0.57 h (0.15 x 218 Wh / 57.5 W), so the 1 h step fills faster than
  its own taper law. A 0.01 h step lowers the lowest stores by 0.8 Wh (B) and 2.4 Wh (C) and moves the thresholds by
  -0.1 to +0.2 K. Under the materiality line; state it or step finer.
- **M2** (same lines 245 and 250): 23.1 to 57.8 Wh of node power over 72 h is counted as used and charged U3B's loss,
  then discarded at the full clamp. No energy is created and no lowest point moves, but the loss figures
  (energy_two_pack.out 3c; CHARGER.md line 94, "22.3 to 31.7 Wh in U3B") include loss on discarded energy. Report
  the term or cap the allocation at the headroom.
- **M3** (reconcile_lid.py lines 18 and 25; reconcile_lid_panel.py lines 22 and 45): the per-string scaling contradicts
  TOPOLOGY 3b and 4 (at most 7.936 A, host cap 2 x ChargingCurrent() on an 8.0 A image) and, at 4S15P, the +3 %
  maximum of 9.92 A exceeds OCC1 10.0 A. No figure depends on it. Fix: state U3B at code 62 (7.936 A) for both lids,
  or re-derive the lid image with OCC1 above 1.03 x the setting.
- **M4** (RECONCILE.md lines 30-31 and 48): 4S15P needs k = 3 as well (72,360 cWh at the specification minimum; at
  k = 2, 36,180); line 48 still names the k = 2 calibration.
- **M5** (RECONCILE.md lines 44-46): the plane window is stream a1solar's 4S12P result. Re-run for these lids
  (`planes.out`, the plane files and ratios of energy_runs.out section 6): 4S14P meets in B and C at 20 to 50 degrees
  from -30 to +45 (50: to +30), and at 10 degrees within 15 of south; 4S15P at 10 to 50 degrees over nearly every
  azimuth; flat: 4S14P NOT MET, 4S15P MEETS typical (26.4 Wh, the production model too) and NOT MET adverse. The
  stated rule is sufficient; "laid flat does not meet" is not true of 4S15P typical.
- **M6**: the lid path's standby drain (TOPOLOGY 9: 1.38 to 1.73 mA) and board PL's own supply are outside the 42.8
  W: about 1.5 to 1.8 Wh over 72 h plus the gauge's draw, not read.
- **M7**: the reconcile scripts import energy_two_pack.py without pinning it; its sha256 at 7613c072 (81694b2b...)
  equals the pin in energy_runs.py.
- **M8**: U3B at its 0.96 bracket costs 3.2 / 3.5 Wh at C (14P / 15P), nothing at B. The 4.0 A Low Temp clip never
  binds; with it, 4S15P C's threshold moves to +1.76 C (the capacity split's spill), not a loss.

## Reproduced

- `env -C <clone> python3 v2/docs/records/a1int/reconcile_lid_panel.py`, `.../reconcile_lid.py` and
  `v2/docs/records/a1elec/energy_two_pack.py`: exit 0, byte-identical to the committed outputs (sha256 e1695103...,
  4da1b5d3..., and the .out of energy_two_pack by cmp).
- `python3 _chk/indep.py <clone>`: every claimed row within 0.05 Wh and 0.01 K at a 1 h step (`indep` in the table).
- `_chk/sens.py`, `_chk/prod_sens.py` (production model with the lid clipped to 7.936 A and to the register codes, the
  Low Temp clip, U3 at 6.1 and 6.0 A, the requirement search), `_chk/ledger.py` (72 h ledgers; mine closes to 1e-12 Wh,
  the production trace closes once the clamp term is added), `_chk/planes.py` (40/0 anchor reproduced to 7e-5 W/m2).
