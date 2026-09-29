# s119: the energy chain's charger rows restated, U3B drawn on U3's 400 kHz row, the lid reconciliation re-run (S-119, MESHSAT-1357)

Stream s119, branch `fnd/s119` from set 12's tip `a1f8ec70` (`fnd/int13`), 29 September 2026, two rounds: the first
(15:30 to 16:00) restated the rows; its independent AI check (`_scratch/chk-s119/CHECK.md`: mergeable yes, 0 blocking, 7
minor) led to the second (16:15 to 16:45), which draws U3B's FETs and answers M1 to M7. **Prototype design: nothing is
built, bought or measured. Every figure is the record's model on the September reference day, AI arithmetic on the makers'
figures; it is not a review by a person and not a measurement.** No requirement is changed: M1 and REQ-072 stand as
written, battery plus solar stays the basis, external DC stays optional, and REQ-072 stays FAIL. The owner decisions Q1 to
Q4 of the EXECUTION-PLAN (the standing rule of 29 September 12:03) are not taken; every result is given per lid option.

## What changed

**The two charger rows**, each by TI SLUSE66A Equations 6 to 22 (printed pages 86 to 88) with its sense resistors inside it
and the inductor's core loss excluded:

| Row | First issue | Now | Basis |
|---|---|---|---|
| U3, board A's charger (`energy/energy_inputs.yaml`, solar.chain) | 0.98 (0.965 to 0.984), Figure 8-4 read by an AI, FETs not named | **0.979 (0.972 to 0.983)** | decision 57's FETs as drawn on board A (Q7 CSD17578Q5A, Q8 to Q10 CSD17577Q5A), S-117's row (XAL1010-472ME, 400 kHz), the reference day weighted by energy at entry E2 (`records/s117/efficiency.out` section 7) |
| vehicle_entry chain_eta (same file) | 0.9114 | **0.9105** | the front end's 0.93 times U3's row |
| U3B, the lid charger (`a1elec/energy_two_pack.py`, eta_u3b) | 0.975 (0.96 to 0.985), Figure 8-3 | **0.972 (0.963 to 0.978)** | U3's 400 kHz row, which the session decision below draws for U3B, in the buck-boost bound at every hour and weighted by energy over the model's own hours; the lowest over both lid options, both ratio cases and both starts, rounded down (`u3b_hourly.out`) |
| U3B's input limit (iin_lid_a) | 8.0 A on 5 mOhm | **6.2 A** on R16B 10 mOhm | code 124; 6.3 A maximum under the 6.35 A clamp (9.3.5, page 25); the model's largest U3B input is 4.08 A |
| the lid's charge loop (r_lid_chg) | 28 mOhm | **23 mOhm** | U3B's RSR is inside its efficiency and was counted twice (check item M3) |

The first round carried U3B at 0.961, the 800 kHz row at the model's peak hour (55.3 W from VBAT), which is U3B's most
favourable load; over the model's own hours that row weighs 0.957 to 0.960 and its worst hour of 5 W or more 0.906 (the
check's M1, reproduced in `u3b_hourly.out`). On the 400 kHz row the same weighting gives 0.972 to 0.974 and the worst hour
of 5 W or more 0.943. The model carries the weighted figure, as it carries U3's; `reconcile_s119.py` section 3 also runs
U3B's efficiency hour by hour as a function of its input power (the model's `eta_at`, used by the analysis scripts only).

**The session decision on U3B** (`apply_decision_s119.py`, for `tools/pcb_decisions.yaml`, the next free number, 58 on
the tree this stream started from; authority SESSION with its fields): U3B takes U3's 400 kHz row and the FET pair of
decision 57. Q7B and Q9B CSD17578Q5A where each leg hard-switches, Q8B and Q10B CSD17577Q5A on the synchronous side, L2B
Coilcraft XAL1010-472ME, 191 k on IADPT (Table 9-4, page 27), Table 9-5's 400 kHz compensation (pages 27 and 28), PWM_FREQ
at its power-on 400 kHz (Table 9-8, page 43, where TI recommends 400 kHz with 4.7 uH), R16B 10 mOhm and R17B 5 mOhm,
IIN_HOST 6.2 A, the ILIM_HIZ divider at 3.48 V. REGN then asks 10.5 mA typical in buck mode and 32.6 mA at the makers'
maxima in buck-boost at 460 kHz against IREGN_LIM's 50 mA minimum (8.5, page 11), where the drafted CSD18510Q5B asked 120
to 240 mA and the 800 kHz row with CSD17578Q5A x 4 asks 49.9 mA (inside, no margin). **It is drawn** in
`records/a1elec/TOPOLOGY.md` 3b (a parts table, second issue, with the settings, the ILIM_HIZ divider, the section 8
limit row and the daughter-board line) and `CHARGER.md` 2 (U3B's paragraph) and 3 (the loss table). The check of stream
s119 read the same REGN figures and supported this row.

**The inductor at 400 kHz** (`inductor_u3b.py` and `.out`; Coilcraft Document 804-1, revised 02/25/26, page 1; SLUSE66A
10.2.2.3, page 85; FSW 340 / 400 / 460 kHz, 8.5, page 16), over U3B's envelope (VBAT and the lid each 12.0 to 16.8 V;
7.936 A charge in buck and buck-boost, 6.3 A input in boost):

| Check | Worst case | Maker's figure |
|---|---|---|
| ripple, 400 kHz, nominal L | 1.16 to 2.44 A p-p, 15 to 31 percent of 7.936 A | TI's guidance 20 to 40 percent (page 85) |
| ripple, 340 kHz, L 20 percent low | up to 3.62 A p-p (the buck-boost bound) | |
| peak, Equation 2 | 9.74 A | Isat 25.4 A (typical, a 30 percent drop; no minimum printed) |
| RMS | 8.00 A; copper loss at most 0.37 W (DCR 5.70 mOhm maximum) | Irms 17.5 A (20 C rise), 24.0 A (40 C rise), for reference |
| fault bound | the input comparator trips at 15 A (150 mV over R16B, VOCP_lim_ACX, page 15): at most 15 A in boost, 21 A average in buck at 16.8 V into 12.0 V | under the typical Isat; not a bound on a part at its worst |

The inductance against current is s117's INFERRED reading of 804-2's curve (91 percent at the worst peak).

**The core loss (check item M2).** No held Coilcraft document gives a core-loss figure or model data for the XAL1010:
Document 804-1 page 1 says "Core and winding loss: See www.coilcraft.com/coreloss", 804-2 to 804-4 give only inductance
against current and frequency, and the held XAL1510, XAL40xx and XAL60xx sheets say the same or "Go to online calculator".
The public site refused this host on 29 September 2026 (HTTP 403 for `https://www.coilcraft.com/coreloss` and the XAL1010
product page; the same through `web.archive.org/web/2026id_/`), so no public document was read; the stream uses no other
model or search service. The core loss stays EXCLUDED, and its sign is known: every efficiency is high by it. What the
record gives is the room, now hour by hour (`reconcile_s119.out` section 6b): a constant loss added in every hour the
charger runs, with U3B on its hourly curve and U3 at 6.1 A:

| Lid option, ratio | U3 alone | U3B alone | the same in both | 0.5 W in each | 1.0 W in each |
|---|---|---|---|---|---|
| 4S14P (tablet out), B | 7.3 W | 8.9 W | 4.0 W | 92.5 Wh | 91.5 Wh |
| 4S14P (tablet out), C | 4.5 W | 5.6 W | 2.5 W | 73.2 Wh | 61.1 Wh |
| 4S15P (QMX out), B | 8.6 W | 10.5 W | 4.8 W | 124.0 Wh | 123.0 Wh |
| 4S15P (QMX out), C | 5.8 W | 7.2 W | 3.3 W | 104.3 Wh | 92.1 Wh |

**The chain, every script re-issued with its pins moved and every output regenerated by its own script** (sha256, first 16;
base `a1f8ec70` against this branch's tip):

| File | Was | Now |
|---|---|---|
| `energy/energy_inputs.yaml` | `64dd014bee56d855` | `74a6e4ab0074648e` |
| `energy/energy_budget.py` (INPUTS_SHA256; the chain printed to three places) | `cf6c377fa1015a46` | `6a8ac4642bd2aaf3` |
| `energy/energy_architecture.py` (EB_SHA256) | `5cab5edfadb736d3` | `18851486ce4304f1` |
| `energy/energy_4s6p.py` (PINS: energy_budget, energy_inputs, and gen_sch_a.py after `cmp_gen_sch_a.py`) | `a41a431071c81d80` | `b68738e17ddbae54` |
| `energy/checks/recompute.py` (pins added, algorithm unchanged) | `af8cb7134a18077b` | `c8b1b83d92545cd8` |
| `a1elec/energy_two_pack.py` (EB_SHA256; U3B's row, input limit and loop; eta_at; section 4's bracket rows; section 7's losses with the sense resistors inside) | `81694b2bfc5dfef1` | `a3426880bf607d38` |
| `a1elec/checks/recheck_two_pack.py` (U3B's figures typed; pins added, check item M4) | `740587ba109ff5dd` | `8f011971b49a1dad` |
| `s117/efficiency.py` (third issue: TP_SHA pin, check item M4; its closing sentence; no figure moves) | `748c1a9a8bdec44f` | `c24d5cfe209be3db` |
| `a1solar/energy_runs.py` (third issue: EA_SHA, TP_SHA, section 0's figures) | `a4c60344c7f7a72a` | `d0fd1949efce7186` |
| `a1int/reconcile_lid.py` (second issue: TP_SHA added) | `7ab77ef1f002ef87` | `7a53941f55b18329` |
| `a1int/reconcile_lid_panel.py` (third issue: TP_SHA; its NOTES labelled as measured at the second issue's rows) | `dd88cd39334709ff` | `9ebb0e5a619dba98` |
| `s119/reconcile_s119.py` (pins on energy_two_pack, energy_runs and u3b_hourly, check item M4) | new | `69c7ee96a87d3bcb` |
| `s119/u3b_hourly.py` (pins on efficiency.py and energy_two_pack.py), `s119/inductor_u3b.py` (pin on efficiency.py) | new | `4b435e4f0e272050`, `ed35929bf557792a` |

Unchanged and re-run to the byte: `night_bounds.out`, `packfit_west.out`, `a1solar/array_calc.out`, `a1elec/gauge_scale.out`.
`energy_4s6p.py` refused to run on `a1f8ec70` before any change of this stream (set 12 had moved `gen_sch_a.py`); its pin
moved after the three parsed calls compared identical. The headline figures before and after are `headline_diff.out`,
which now names each file by its sha256 instead of the commit it was run at (check item M5).

**Cross-checks.** energy_two_pack.py's equivalence check holds; the independent closed-form re-check agrees with every
figure of the regenerated `.out`; the section 9 recompute reproduces the architecture figures; `u3b_hourly.py`'s 800 kHz
row reproduces the check's own 0.957 to 0.960 and 0.906; `reconcile_s119.py` reproduces every row of
`reconcile_lid_panel.out` byte for byte before it prints anything; `apply_registry_s119.py close --check` re-ran all
sixteen scripts of the chain and each printed its committed output byte for byte.

## The figures per lid option (`reconcile_s119.out`)

400 Wp, the 200 W stage, entry E2, base at +20 C, lid at 13.23 C, both starts, 42.8 W, aged 80 percent, the 40 degree
south plane; U3 at its 6.1 A minimum; lowest store of both packs and the lowest lid temperature that still meets M1.
"Hour by hour" takes U3B's efficiency from its input power in each hour (section 3); "carried" is the chain's 0.972:

| Lid option | Typical, accepted | Typical, now (hour by hour) | Adverse, accepted | Adverse, now: hour by hour | Adverse, carried |
|---|---|---|---|---|---|
| 4S9P, both lid functions kept | NOT MET | NOT MET | NOT MET | NOT MET | NOT MET |
| 4S14P, the tablet out | 93.7 Wh, +3.8 C | **93.7 Wh, +3.8 C** | 87.4 Wh, +5.9 C | **85.8 Wh, +6.0 C** | 85.5 Wh, +6.0 C |
| 4S15P, the QMX out | 125.2 Wh, +1.5 C | **125.2 Wh, +1.5 C** | 118.5 Wh, +2.2 C | **116.9 Wh, +2.3 C** | 116.6 Wh, +2.3 C |

Hour by hour at the makers' maxima the adverse stores are 82.3 and 113.3 Wh, at the most favourable reading 88.0 and 119.2;
the 800 kHz way (a) hour by hour gives 79.8 and 110.9 (the check's 79.4 and 110.4 at the first round's 28 mOhm loop). With U3
at 6.2 A the adverse figures are 90.9 and 122.4 Wh; at the 6.0 A bracket 76.1 and 107.2 Wh. The least current into U3 that
still meets M1 at ratio C: 5.58 A (4S14P) and 5.44 A (4S15P), under U3's 6.1 A minimum. The first round's adverse
figures (80.6 and 111.6 Wh, U3B at 0.961 with the loop counted twice) are superseded.

**The failing case** (section 4): the chargers at the FETs first drawn and drafted, U3 0.939 and U3B 0.802: **every case NOT
MET** for both lids in both ratio cases. Apart: U3 as drawn with U3B on its first-drafted CSD18510Q5B (0.802) meets the
typical case but reads NOT MET adverse for both lids; U3 at 0.939 with U3B at 0.972 meets every case (25.3 and 56.0 Wh
adverse). The instrument still tells the circuits apart.

**The sensitivity** (section 5; adverse, U3 at 6.1 A, 4S14P / 4S15P): U3B 0.963 gives 81.8 / 112.9 Wh, 0.972 gives
85.5 / 116.6, 0.978 gives 87.9 / 119.1 and the first round's 0.961 gives 81.0 / 112.1; U3 at 0.972 gives 77.5 / 108.6 and at
0.983 88.9 / 120.1 (U3B 0.972). Every cell of the grid meets; the typical case moves by at most 0.3 Wh.

**The planes** (section 7, U3B hour by hour): every grid plane of the deployment rule (20 to 50 degrees, 15 degrees either
side of south) meets in both cases for both lid options; the weakest is 4S14P adverse at 20 degrees 15 degrees east of
south, 44.8 Wh. Laid flat, 4S14P does not meet and 4S15P meets in the typical case only (15.6 Wh). The carried figure gives
the same verdict on every plane. So Q4's recommended rule is still sufficient for both lid options. For a1elec's 4S12P lid
(`energy_runs.out` section 6) the plane 20 degrees and 15 degrees east of south now meets in the typical case only; 4S12P is
not an option the owner is asked to choose.

**Board A's charging peak** at the drafted entry: front end 9.7 W, U3 2.7 W, U3B 1.5 W, **about 13.9 W** (the first round's
15.1 W counted the sense resistors twice, check item M3; at 800 kHz it would have been 14.6 W).

## Is the two-pack M1 result re-established for the circuit as now drawn?

**On the model, yes, for board A as drawn and U3B as now drafted; nothing is measured and REQ-072 stays FAIL.** Board A's
U3 carries decision 57's FETs (regenerated in set 12) and supports 0.979; U3B is now drafted on U3's 400 kHz row with FETs
its REGN can drive (a draft on its page, on no generator), and supports 0.972. With both, the two lid options that fit meet
M1 on the model in the typical and the adverse case, tablet out 93.7 and 85.8 Wh and QMX out 125.2 and 116.9 Wh hour by
hour, and both lid functions kept still does not. This is a model result with the inductors' core loss excluded: the
model's result then applies to the circuit as drafted, within the room of section 6b (in the tablet-out adverse case, 4.5 W
constant on U3 alone, 5.6 W on U3B alone, or 2.5 W on each). Option A(i) is not adopted: Q1 to Q4 stay the owner's.

## Apply scripts (for the integrator; none has been run on the tree)

| Script | Changes | Asserts |
|---|---|---|
| `apply_decision_s119.py` | `v2/ecad/tools/pcb_decisions.yaml`: one decision, the next free number, SESSION, with authority, authority_why, ruled_by, ruled_on, reversed_by, ask, recommendation, evidence, blocks and holds_nothing_today | decision 57 is present; the texts pass int7's screen; only the new entry moves; it reads back as written; refuses a second run (the mark "(S-119 U3B)"); `--check` writes nothing |
| `apply_registry_s119.py close <commit>` | `v2/ecad/tools/pcb_requirements.yaml`: S-119 to closed_items; U3B's FET finding filed as a closed SESSION item with the next free S number (S-121 today); REQ-072 leaves S-119 in its waits_on (left with S-53, M-02, S-114) and gains one evidence entry | refuses unless every chain file (with TOPOLOGY.md and CHARGER.md) is tracked, unchanged against HEAD and identical at `<commit>`; the U3 row equals efficiency.out section 7 and eta_u3b and its bracket equal u3b_hourly.out (YAML reader, ast, the outputs parsed); every sha pin names the committed file (ast); every script re-run prints its committed output byte for byte (skip with `--no-rerun`; about two minutes); the failing case reads NOT MET; the decision "(S-119 U3B)" is ruled; TOPOLOGY.md 3b's parts table draws the 400 kHz parts. Re-parses; only S-119, the new item and REQ-072's waits_on and evidence may move; REQ-072 stays FAIL; screened; refuses a second run; `--check` writes nothing |
| `apply_note_reconcile.py` | `a1int/RECONCILE.md` | each note script: its anchor (the page's title line) occurs once; refuses a second run (the note's mark); no em or en dash; writes, re-reads, and checks the page is its old text plus the note; `--check` writes nothing (`pagenote.py`) |
| `apply_note_energy_reconciliation.py` | `energy/ENERGY-RECONCILIATION.md` | as above |
| `apply_note_a1elec_readme.py`, `apply_note_charger.py`, `apply_note_topology.py` | `a1elec/README.md`, `CHARGER.md`, `TOPOLOGY.md` | as above |
| `apply_note_a1solar_readme.py`, `apply_note_array.py` | `a1solar/README.md`, `ARRAY.md` | as above |
| `apply_note_a1mech_readme.py` | `a1mech/README.md` | as above |
| `apply_records_readme_row.py` | `v2/docs/records/README.md`: the `s119/` row after `a1solar/` | anchor row once; refuses a second run with an exit, not an assert (check item M7); the table gains exactly one row; `--check` writes nothing |

Each note adds the second issue's figures beside the first issue's at the top of the page and rewrites none of them.
TOPOLOGY.md 3b and CHARGER.md 2 and 3 are edited in place on this branch (U3B drawn); their notes cover the figures
elsewhere on those pages. The check records (`checks/check-*.md`, `int10/CHECK.md`) quote the first issue's figures and are
left as the record of their checks. The EXECUTION-PLAN's decision table is the coordinator's; its new figures are in this
stream's final message.

**What the integrator runs**, from the repository root after merging `fnd/s119`:
1. `python3 v2/docs/records/s119/apply_decision_s119.py --check`, then without `--check`; then
   `python3 v2/ecad/tools/decisions_render.py`.
2. the nine page scripts (the eight `apply_note_*.py` and `apply_records_readme_row.py`), any order, each `--check` first.
3. `python3 v2/docs/records/s119/apply_registry_s119.py close <the commit that carries this stream's files> --check`, then
   without `--check`; then `rules_lib.py requirements` and `rules_render.py --requirements` as for any registry edit.
The decision's and the new item's numbers are printed by their scripts; the page notes name them by the script that makes
them, not by number.

## What remains open

1. The core loss of both inductors: excluded, no maker figure held and the maker's site refuses this host; section 6b's
   room is what it may take. A bench item at bring-up (REQ-072's acceptance already repeats the balance with the stage's
   efficiency measured).
2. U3B's switch node, loop, REGN current and temperatures, and the ILIM_HIZ divider's accuracy at 10 mOhm (SLUSE66A prints
   it for 5 mOhm only): bench and layout items; U3B is on no generator.
3. The checks' notes in `reconcile_lid_panel.out` (the 0.01 h step, the thresholds' 1.5 K stability, the clamp, the standby
   drain) were measured at the first issue's rows and are not re-measured.
4. CHARGER.md's loss table: the E3 column's U3B is not re-derived. POWER-THERMAL's owner re-runs board A at about 13.9 W.
5. An independent check of this second round.
6. REQ-072 stays FAIL; Q1 to Q4 stay open; S-120 (the charge bus's worst case against the 30 V FETs) is not this stream's.

Files: `u3b_hourly.py`, `inductor_u3b.py`, `reconcile_s119.py`, `headline_diff.py`, `cmp_gen_sch_a.py` (each with its
`.out`), `pagenote.py`, the apply scripts above, `LOG.md`.
