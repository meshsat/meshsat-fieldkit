# Stream s99a: S-99's accepted correction applied to board A's generator

MESHSAT-1357, 28 September 2026, branch `fnd/s99a` from `36e10781` (set 8's candidate `2f051e71` with the S-99
record and its correction merged). **AI engineering work** (desk arithmetic on makers' documents and the project's
declarations), not a qualified review. Prototype design: no board has been built, ordered or measured, and nothing
here was regenerated (no KiCad on this host). The stream owns `v2/ecad/tools/gen_sch_a.py`; `gen_sch_d.py` was not
changed (item 4 below). Inputs, not re-derived: `v2/docs/records/s99/CORRECTION.md` (accepted), `checks/codex-check-1.md`,
`checks/check-2-claude.md`, `checks/int9_old_block.txt` and `int9_new_block.txt`, `apply_d8_split_draft.py`,
`ANALYSIS.md` section 5 (decision 55, option B), `REGISTRY-DRAFT.md`.

## 1. Item 1: the draft rebased and applied (commit 0068876c)

`apply_d8_split_rebased.py` is the s99 draft with entry S99-DEV's old text replaced by `checks/int9_old_block.txt`
verbatim (the eleven lines 125 to 135 of set 8's generator, sha256 of the file e25c6e47...) and its new text
`int9_new_block.txt` with "S-98 reconciliation" read as "I-03's M/P adequacy" (S-98 is closed on this line). The
other four entries are the draft's. `--check` on this tree's generator (sha256/16 ebb5c0f250780a48, the file the
Claude check named): exit 0, last line `CHECK ONLY: 5 entries, 1 generator; no writes, no marker.`, the hash
unchanged (`rebased_check.out`). Applied once (the marker `apply_d8_split_draft.applied` beside it refuses a second
run); the diff is exactly five hunks: VBAT's load map (U41 0.4 A), the +5V_DEV block, the stage block before U23 with
U23 on +5V_D8IN, +5V_D8IN in the PWR_FLAG list, and the ten references in the eFuse section.

## 2. Item 2: TPS2596 equation 7's sign in the generator (commit 80ebde44)

Source: TI TPS2596 SLVSET8A (May 2019, revised August 2019), `v2/vendor/power/tps2596.pdf`, printed p.28, equation 7:
RILM = 903 / (ILIM - 0.0112); the page's worked example 903 / (1 - 0.0112) = 913.2 ohm fixes the sign independent of
glyph rendering (read with pdftotext here). So ILIM = 903 / RILM + 0.0112 A.

| Site in gen_sch_a.py | Old | New | Basis |
|---|---|---|---|
| eFuse helper comment | RILM = 903 / (ILIM + 0.0112) | RILM = 903 / (ILIM - 0.0112), ILIM = 903 / RILM + 0.0112, with the nominal limits listed | p.28 |
| U32 ILM resistor R186 (value text), its comment | 1k 1% (ILM: 0.89 A); "1.00 k gives 0.89 A" | 1k 1% (ILM: 0.91 A); 0.9142 A nominal | 903/1000 + 0.0112 |
| VBUS_WALL peak and its load J_USBW; note | 0.9 A, 0.9 A; "limit 0.89 A" | 0.9142 A, 0.9142 A; "limit 0.9142 A nominal" | U32's nominal limit |
| +5V_DEV declared peak | 6.9 A (B 6.0 + wall 0.9) | 6.9142 A (B 6.0 + wall 0.9142) | the wall at its corrected limit |
| +5V_DEV margin to the loop minimum 7.056897 A | 0.156897 A | 0.142697 A | 7.056897 - 6.9142 |
| U39 ILM resistor R210 (value text), its comment | 4.7k 1% (ILM: 0.18 A); "903 / 4700 - 0.0112 = 0.18 A" | 4.7k 1% (ILM: 0.20 A); "903 / 4700 + 0.0112 = 0.20 A" | 0.2033 A |
| pre-split figures in the S-99 stage comment | wall 0.5 to 0.9 A; 8.9 A at every declared limit | 0.5 to 0.91 A; 8.91 A | the same correction |

Unchanged because they are right at the precision written: U21 750R "1.2 A" (1.2152 A), U22 909R "1.0 A"
(1.0046 A), U23 453R "2.0 A" (2.0046 A; +5V_D8 and +5V_D8IN keep their 2.0 A peak, 4.6 mA under U23's nominal limit,
inside the declared precision). `lcsc_fill.py` line 46's "301R ... at 3.0 A" is right too (3.0112 A).

+5V_DEV after the split and the correction (hot minimum 0.043 / (0.006 x 1.01 x 1.0055) = 7.056897 A; initial
7.095710 A): declared 6.9142 A, margin **0.142697 A** (0.181510 A at the initial minimum); with the wall at the 909
ohm row's extrapolated 0.956044 A, 0.100853 A; with R186 at -1 percent (0.965583 A), 0.091314 A. These two are
estimates from a ratio of p.6 rows, not a guaranteed 1 kOhm maximum. The M-tier (5.942235 A, margin 1.114661 A) and
the P-tier (8.171220 A, 8.180759 A with R186 tolerance, over by 1.114324 A and 1.123863 A) are unchanged: the
corrected figures were already in them.

Text outside this stream's file that still quotes 0.89 A is listed for the integrator in `REGISTRY-DRAFT.md`
section 4 (`pcb_interfaces.yaml` line 359, `HW-FW-CONTRACT.md` line 85, `ASSEMBLY.md` line 151,
`reviews/DECISION-31-PROTECTION-TOPOLOGY.md` line 244).

## 3. Item 3: VBAT's load map (commit 80ebde44)

The draft added U41 at 0.4 A and kept Q32 at 2.0 A, which was the pre-split stage's input (5.1 A x 5.088 V / (0.90 x
14.4 V) = 2.002222 A), so the mezzanine's input was counted twice (about 0.39 A). By the S-98 method of Q28's 2.22 A
(the stage's declared load sum at its output voltage over the declared efficiency and VBAT's 14.4 V nominal):

- Q32 = 4.1 A x 5.088 V / (0.90 x 14.4 V) = **1.609630 A, declared 1.61 A** (old 2.0 A).
- U41 = 1.0 A (+5V_D8IN typical) x 5.002 V / (0.90 x 14.4 V) = **0.385957 A, declared 0.4 A** as drafted (the
  draft's 0.392593 A used 5.088 V; `u41_divider.out` prints 0.385947 A because it uses the unrounded 5.001869 V). 0.90 is the project's efficiency figure for the TPS62933, not a maker's reading.

VBAT's load map sums 11.57 A (was 11.96 A with the double count). On the PWR-002 feed sums (typical), +5V_DEV's
child draw falls by 0.39 A and +5V_D8IN's adds 0.39 A, so VBAT's draw stays at 17.62 A against its declared 10.0 A: a
pre-existing shortfall on this line (read with `power_path.feed_sums` on the tree's current intent), not changed here
and not this stream's. On peaks, VBAT's children rise from 24.76 A to about 25.54 A (+5V_D8IN's 2.0 A peak is 0.77 A
at VBAT); computed by hand from the declarations, to be read on the regenerated intent.

## 4. Item 4: U41 against board D's v_work (commit 80ebde44, board A only)

The drafted divider (53.6k over 10k, 1 percent) with VFB 784 to 816 mV over TJ -40 to 150 C (SLUSEA4D, June 2021,
revised August 2022, 8.5 printed p.6) and the FB leakage (0.15 uA maximum, p.6, sign not given) reaches 5.286 V,
5.345 V with 100 ppm/C over 65 K: over board D's declared v_work of 5.23 V on +5V_D8 (`gen_sch_d.py` line 56).

- **Raise board D's v_work instead: refused.** Board D's PCM2912A codec sits on +5V_D8 with a recommended VBUS of
  4.35 to 5.25 V (TI SLES230A, revised August 2015, 7.3 p.5); a 5.29 V rail puts it above its recommended maximum at
  light load. It would also change a second board's declarations and the board D derivations that quote 5.23 V.
- **No 1 percent divider fits both ends** of the window both boards' +5V_D8 notes assume (4.90 V source minimum,
  5.23 V maximum): the reference and 1 percent resistors alone spread 1.0765 against the window's 1.0673
  (`u41_divider.out`). A 1 percent divider low enough for 5.23 V (52.3k over 10k, not certified) reaches 5.235 V with
  its TCR and drops the bottom to 4.74 V.
- **Chosen: 56.2k over 10.7k, both 0.1 percent 25 ppm/C YAGEO RT0603 (C705784, C861078), the pair board D already
  certifies as R80 and R81** (`JLC-CERTIFIED.tsv`, CERTIFIED, 2026-09-26). Nominal 5.002 V; 4.872 to 5.133 V over
  the reference, both tolerances, 25 ppm/C over 65 K and the leakage. The top is 0.097 V under 5.23 V, so board D's
  declarations stand and board D is not regenerated. At the bottom, U23's on resistance (SLVSET8A printed p.7: 89
  mOhm typical, 115.3 mOhm maximum over -40 to 85 C, 131 mOhm to 125 C) and the 6 percent drop budget leave the codec
  4.44 to 4.48 V at the 1.0 A typical, 0.09 to 0.13 V over its 4.35 V; with +5V_D8IN's own 2 percent also spent the
  margin is 0.007 V (U23 at its 85 C maximum) to -0.009 V (125 C); at the 2.0 A peak the codec is under 4.35 V, which
  predates the split (U23 was in series and the LM5176 source's bottom was 4.875 V). `codec_floor.out`, open item
  S-116 (`OPEN-ITEM-CODEC-FLOOR.md`). (The first version of this record said 4.57 V and 0.22 V, leaving out U23 and
  +5V_D8IN's budget; corrected after the independent check.) U23's OVLO pin sits at 0.97
  to 1.02 V (0.5 to 2 V recommended) and its re-close (5.33 V at the extremes) stays above 5.133 V. At 16.8 V in the
  ripple is 1.033 A and the peak 2.517 A at 2.0 A (2.646 A with L at -20 percent) against IHS_LIMIT 4.2 A minimum.
  The 53.6k over 10k pair at 0.1 percent would also fit (4.956 to 5.221 V) but neither code is certified and its
  top sits 9 mV under 5.23 V. Authority SESSION (engineering; no class of `tools/reserved.json` names gen_sch_a.py;
  no purchase beyond two BOM lines of certified parts). Reversal: R217/R218 back to 53.6k/10k 1 percent and board D's
  v_work question reopened.
- +5V_D8IN now declares v_work 5.14 V (the band's top rounded up), and board A's +5V_D8 note gains one sentence with
  the new source band. Board D's own notes that quote the old source (the +5V_D8 note's "4.90 V" and "250 mV in
  hand", the lines 46 to 49 comment naming an AP64500 on 792 to 808 mV, D1's "5.09 V mezzanine rail" value text,
  U17's efficiency 3.44 / 5.09 = 0.676, which at 5.002 V is 0.688, so the declared figure is the conservative side)
  are stale TEXT for board D's owner at its next circuit round; no declared figure a rule judges changes.

## 5. Item 5: the layout generator (not changed)

`gen_pcb_a3.py` refuses a board with unplaced parts (line 312) and builds +5V_DEV's outlet island from U23, R100 and
C103 (lines 583 to 586), which moved to +5V_D8IN. The open-item text is `OPEN-ITEM-LAYOUT-A.md` (proposed S-115,
disposition LAYOUT_STAGE, owner: board A's layout generator owner in board A's layout phase).

## 6. Checks run here

- Both generators parse (`ast.parse`): gen_sch_a.py, gen_sch_d.py (and gen_pcb_a3.py, untouched).
- `compare_calls.py 36e10781` (`compare_calls.out`): 14 statements ADDED (the ten references U41, L13, C227 to
  C232, R217, R218, the `_cls` loop over C229/C230, the +5V_D8IN rail, the nodes D8B_SW and D8B_BST), 0 REMOVED,
  9 CHANGED: VBAT (loads), +5V_DEV (typ 5.1 to 4.1, peak 6.9 to 6.9142, loads without U23, note), +5V_D8 (note),
  efuse U23 (input +5V_D8IN), efuse U39 and U32 (ILM value text), VBUS_WALL (peak, load, note), the PWR_FLAG loop
  (+5V_D8IN), SECTIONS (the ten references). No other statement changed. Comments are not statements; the diff shows them.
- Tests: `env -C <worktree>/v2/ecad/tools python3 tests/run.py contract interfaces power_path rail_loads current_model
  netlist_classes`, last line `tests: 128 passed, 0 failed, 4 skipped` (the four skips are test_block_contract's,
  "no pcbnew here"); `tests.out`.
- `dev_stage.py` reproduces its filed output byte for byte only in a scratch root with its four pinned inputs from
  2b7c9374; on this tree it already refuses (board A's intent was regenerated by set 7 and set 8), and after the box
  regeneration it will refuse by design. Not re-pinned (`dev_stage_repro.txt`).
- The d8dec31 draft for board A (`apply_gen_sch_a_mainpb.py`, R219 and C233) still passes its `--check` on a scratch
  copy of this generator, so the two changes do not collide.
- No gate, verdict writer, suite, KiCad or network was run.

## 7. What the box regeneration must rebuild

Board A only (board D is unchanged by item 4): from `fnd/s99a`, the schematic-phase regeneration of
`v2/ecad/pcb-a-power-a23/` (the retake path of set 8's S-98 regeneration, `v2/docs/records/int9/box/`):
`pcb-a-power.kicad_sch`, `out/pcb-a-power.net`, `out/pcb-a-power.net.prov.json`, `out/pcb-a-power-intent.json`, with
ERC and the BOM read (the BOM gains U41, L13, C227 to C232, R217, R218). Then check_contracts, `records/s98/lead_ends.py`
(it should print +5V_DEV AGREE at the lead with A's typical 4.10 = 3.8 + U32 0.30 and A's peak 6.91 A), PWR-001 and
INT-001 re-taken on board A. `pcb-a-power.kicad_pcb` is NOT regenerated (layout phase, S-115). List also in
`regen_files.txt`.

## 8. What stays open, with its owner

| Item | Owner | Next action |
|---|---|---|
| The box regeneration and the re-takes (section 7) | integrator | regenerate board A from fnd/s99a, read intent, netlist and ERC, re-take PWR-001 and INT-001 |
| M and P tiers against the loop (P 8.171220 A over the 7.056897 A minimum by 1.114324 A) | board B's owner (children), integrator (contract) | reconcile board B's +5V_DEV children (LDO ground current, U26, U25's 2.0 A) or show non-coincidence by a document; bench PT-4 |
| A guaranteed TPS2596 limit at 1 kOhm (only the 909 ohm row's extrapolation is held) | board A's owner | a maker's statement or a measurement of R186's setting; until then 0.956044 A is an estimate |
| Timing and capacitor support (no onset bound published) | A and B owners | PT-2 and PT-4: simultaneous SS, rail voltage and branch current through actual bursts and controlled steps |
| Collapse and recovery | A and B owners | PT-4: current against falling voltage, dropout, UVLO and restart with fitted loads |
| U41's loss and temperature, the 22 uF capacitors' DC-bias derating at 5 V, the 0.90 efficiency | board A's owner | routed-copper calculation at layout, then prototype measurement |
| The LM5176 stage's FET and shunt temperatures and switching waveforms (112 C is a scenario) | board A's owner | layout loss and thermal calculation, PT-4 over VBAT, load and ambient including the 60 s key-down |
| +54V_POE off behaviour and AWG18 header rating; +5V_S1 and S3 selections and back-power | A and B owners, cable owner | PT-5, PT-1, PT-3 (RAILS-ACTIONABLE.md) |
| The layout generator (S-115) | board A's layout owner | `OPEN-ITEM-LAYOUT-A.md` |
| Parts: board A's BOM gains C705784 and C861078 (certified for board D) and the XAL6060-682ME, which `tools/jlc-handfit.txt` does not list (only -472ME) | parts stream | add board A's use to the certification table and a hand-fit line for XAL6060-682ME |
| Board D's stale source text (section 4) | board D's owner | rewrite at its next circuit round; no declaration changes |
| The codec's floor at the +5V_D8 peak (S-116) | boards A and D | `OPEN-ITEM-CODEC-FLOOR.md`: tighten +5V_D8IN's budget, raise U41's set point, or bound the peak the codec must run through |
| dev_stage.py's pins and its D-tier line (6.9142 A, 0.142697 A) | integrator | re-pin on the regenerated inputs when the record is next reproduced |
| Shared-file text: S-99, decision 55, IF-AB-POWER, 0.89 A pages | integrator | `REGISTRY-DRAFT.md` |

## 9. After the independent check of 29 September 2026 (`_scratch/chk-s99a/RESULT.md`: accepted, no blocking item)

- (1) The codec floor is restated with U23's drop and +5V_D8IN's budget in the generator (+5V_D8 note, the divider
  comment), section 4 above, `REGISTRY-DRAFT.md` and the new open item S-116 (`OPEN-ITEM-CODEC-FLOOR.md`), from
  `codec_floor.py`. No declared figure changed.
- (2) PWR_FLAG: +5V_D8IN went in at position 17 of the flag tuple, so the twelve virtual parts #FLG17 to #FLG28 shift
  to other nets and #FLG29 is new; check_contracts ignores `#FLG`, but the regenerated netlist will show twelve changed flags.
- (3) SD_OUT, the intent series segment of +5V_DEV, follows it: typical 5.1 to 4.1 A, peak 6.9 to 6.9142 A (R43's load 5.1 to 4.1 A).
- (4) U41's VBAT share at 5.002 V is 0.385957 A (the generator comment now says so); the declared 0.4 A stands.
- (5) The 4.872 to 5.133 V band is a DC set-point band: the TPS62933's PFM ripple at light load (SLUSEA4D 9.3.2) and
  the load-step overshoot at the exciter's unkey are not in it; a bench item under S-99 (d) and PT-4.
- (9) After the split the INA226 U11 (0x45, across R43) no longer sees the mezzanine's supply: a telemetry loss for
  the HAL's power accounting and an item for the firmware contract's owner (FW-A09's text stays true).
- (10) C231 and C232's "22u 10V X7R 1210" maps to C2918511, Samwha CS3225X7R226K250NRL, 22 uF +/-10 percent X7R
  25 V 1210 (JLC-CERTIFIED.tsv line 241; LCSC reading of 2026-09-27). No DC-bias curve of that part is held, so the
  "about 30 uF effective at 5 V" is an estimate OWED on that part; Table 10-2 asks 10 uF minimum effective.
- (7) The IF-AB-POWER +5V_DEV row's `status` is restated in `apply_if_ab_power_dev.py` (with `a_declares` and the wall
  line's "limit 0.89 A"), for the integrator: `--check` on this tree exit 0, last line `CHECK ONLY: no writes, no marker.`
