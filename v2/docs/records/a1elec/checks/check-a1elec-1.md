acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026); the scratch paths are redacted. -->

# Independent check of the Option A(i) electrical package, fnd/a1elec at a21eca38 (MESHSAT-1357)

**AI review** (one Claude checker who wrote none of the work), 29 September 2026, 02:53 to 03:12 CEST. Not a
qualified review. Read-only: scratch clone `_scratch/chk-a1elec` (git clone --shared of the main checkout, fnd/a1elec
fetched from the a1elec worktree, detached at a21eca38). Nothing committed, pushed or run on a box; no Agent, Workflow or
Codex call. Scope: the a1elec commits 1e12b9e1..a21eca38 (records/a1elec/ and the three files under v2/vendor/ti/); the
earlier commits on the branch (set 10's d6dec, diag and energy2 merges) were not checked.

Verdict: the energy model, its equivalence, the gauge scaling and most maker figures reproduce and check out. Two
statements are wrong against held documents or against the package's own circuit description, and both reach what a
generator owner or the qualified battery review would take from it. Neither changes an M1 verdict on the model.

## Blocking items

**B1. The front end's current limit is taken at its maximum, not its limit.** The held LM5176 datasheet (TI SNVSAI1D,
`v2/vendor/ti/lm5176-datasheet.pdf`, 6.5 Electrical Characteristics, PDF page 7, "CONSTANT CURRENT LOOP, VSNS Average
current loop regulation target": 43 / 50 / 57 mV min / typ / max) gives the as-generated front end 4.3 / 5.0 / 5.7 A over
R11 10 mOhm. The package's own cited source says so: `gen_sch_e.py:104-107` reads "limits its OUTPUT at VSNS 57 mV
**maximum** (SNVSAI1D, ... 43 / 50 / 57 mV)", a bound chosen there for copper sizing. The package uses it as the limit:
- `energy_two_pack.py` PAR `fe_out_w` (117.99 W): "board A's front end U2 limits at VSNS 57 mV over R11 10 mOhm, 5.7 A".
  The typical part delivers 5.0 A (103.5 W), the minimum 4.3 A (89.0 W).
- Entry E1 (`.out` 0 and 5, CHARGER.md 1, README): "U3's IIN_HOST at 5.40 A, about 5 percent under the front end's 5.7
  A so that U3's input loop, not the front end's current limit, holds the bus". 5.40 A is above the typical 5.0 A: in a
  typical part the front end's loop holds the bus, the opposite of the stated rule.
- CHARGER.md 2: "R11 6.0 mOhm (57 mV / 6.0 mOhm = 9.5 A ...)" and U3 "IIN_HOST 8.6 A nominal ... under the front end's
  new limit". The drafted limit is 7.17 / 8.33 / 9.5 A; 8.6 A nominal (8.8 A maximum, SLUSE66A 9.6.22) is above its
  minimum and its typical, so the draft breaks the page's own rule, and E2's "nothing under the stage's window caps the
  node" does not hold for a minimum part (7.17 A against the peak hour's 8.20 A).
Effect on the verdicts, on the package's own model (energy_two_pack.sim, lid 13.23 C, E2 otherwise): front end at 4.3 A
NOT MET (329.4 Wh unserved), 5.0 A NOT MET (119.1 Wh), 5.7 A MEETS (18.6 Wh); threshold 5.56 A (115.1 W at VBUS20); the
drafted R11 at its 7.17 A minimum MEETS (31.1 Wh). So "as generated does not meet" survives for typical and minimum parts
and E2 survives, but E1's premise and the drafted R11 / IIN_HOST pair are wrong. The package says "this stream has not
read the LM5176's VSNS tolerance", yet the sheet is held and the generator it cites quotes the triple (worker rules,
"sources first"). Fix: state the front end at 43 / 50 / 57 mV; re-run E1 on the as-generated front end at its minimum and
typical; set U3's IIN_HOST maximum under the front end's minimum limit, or size R11 so that 43 mV / R11 clears U3's
IIN_HOST maximum (for 8.8 A, R11 at most about 4.9 mOhm); re-state the LM5176 stage current the generator owner checks.

**B2. Single faults that defeat the join limit or the reverse block are missing or classed as double faults.**
TOPOLOGY.md 6 names Q_LD welded as a single-point failure, but:
- **Q_LS shorted (or U_LS's gate stuck on)** is not named. It removes the 8.7 to 11.0 A limit that decision 2 (default
  ON) rests on ("limited in hardware to at most 11.0 A ... whatever the voltage difference", TOPOLOGY 1.3 and 3c; README
  "Shown at desk"), and it defeats the interlock that holds the lid path off while U3B runs (3b), so U3B's output can
  circulate back into VBAT. The join is then bounded only by the loops (about 59 A at a 4.8 V gap on `.out` 8's 80.9
  mOhm, an upper bound), the lid AFE's overload and the base's OCC1 (5.0 A, 2 s).
- **The U3B row is wrong to call pack-to-pack conduction a double fault** ("Two shorted switches (Q7B and Q10B) would join
  lid and node directly ... a double fault"). By the page's own body-diode orientation (3b item 3: each high-side body
  diode conducts from its switching node to its own terminal), a single shorted Q10B gives lid -> SW2 -> L2B -> SW1 ->
  Q7B's body diode -> VBAT (lid to node above one diode drop, bypassing U_LD and U_LS), and a single shorted Q7B gives
  VBAT -> SW1 -> L2B -> SW2 -> Q10B's body diode -> lid (the base charging the lid, bypassing the ideal diode). Each is
  bounded only by the gauges (lid OCC1 10 A true or base OCC1 5 A, 2 s) and the AFEs, as the Q_LD row is.
Fix: add the Q_LS and single high-side U3B rows, name them for D-09 with Q_LD, and qualify "limited in hardware to at
most 11.0 A" and "base to lid: blocked in hardware" as statements about a fault-free path.

## Minor items

- **M1.** EN_FAST_5MOHM (ChargeOption1 bit 0, POR 1b; SLUSE66A Table 9-28, page 60) "IIN_HOST DAC is clamped at 6.4 A"
  when 1b, while Table 9-1 (page 26) gives 10 A for 169 k with either value. The drafts (U3 IIN_HOST 8.6 A, U3B 8.0 A)
  do not mention the bit; write 0b explicitly (TI's note: the fast compensation only works below 160 k anyway). Not
  blocking: on the model even a 6.4 A clamp on U3 still meets with 31.1 Wh.
- **M2.** CHARGER.md 3: "5.5 Wh in the discharge path (`.out` 3c)"; `.out` 3c prints 6.0 Wh for both starts.
- **M3.** CHARGER.md 3 and `.out` 7: "at its limit's maximum, 11.0 A ... the LM5069's FET 0.12 W ... for the fault timer's
  duration". 0.12 W is the fully enhanced FET (0.96 mOhm). In current limit the LM5069 holds the FET linear: about
  (gap - I x loop - V_AK) x I, up to roughly 43 W at a 4.8 V gap, bounded by PWR and the timer (SNVS452G's procedure, which
  the page leaves to board A's owner). Say that instead of 0.12 W.
- **M4.** The entry requirement is never stated. On the package's model the design case needs at least 5.56 A (115.1 W)
  at VBUS20, and about 5.9 A (122 W) recovers the full 31.1 Wh; the drafts are sized to the unconstrained 8.20 A peak.
  A U3 input of about 6.0 to 6.8 A puts U3's L2 peak at about 10.0 to 11.2 A at 400 kHz (14.5 V node), under the fitted
  part's 12.2 A value text, so the L2, R16 and 800 kHz changes are margin choices, not M1 needs. Decision 7's reason
  should carry the threshold so the generator owner can size the re-rate.
- **M5.** The fail-safe enable: the SN74LVC1G08 has Ioff (datasheet 7.3.2: outputs high impedance when unpowered), so
  "an unpowered gate ... leave U3B in HiZ" needs a named pull-down on the AND output (Q_E2's gate and the UVLO
  transistor's gate); TOPOLOGY 8 lists only LID_CHG_EN's. An open Q_E1 (or its gate pull-up) is a single fault that lets
  U3B run from VBAT at its POR default on battery at night with the lid path on; name it.
- **M6.** Shoulder hours: with CHRG_OK high and LID_CHG_EN high in a deficit hour (06 and 17 UTC on the reference day,
  18.4 and 16.4 W against 42.8 W), the interlock holds the lid path off, so the base carries the whole deficit and U3B's
  draw. The allocation law should drop LID_CHG_EN whenever U3's input is below the load. Not blocking: the model's total
  is insensitive to the split (30.1 to 31.5 Wh across `.out` 4's policies).
- **M7.** The 3b heading "U3B charges only from outside energy" is a firmware property; the hardware only requires
  outside energy to be present (CHRG_OK). The page says so later; reword the heading.
- **M8.** U3's L2 as generated: `gen_sch_a.py:861` has value "3.3uH XAL6030-332ME (Isat 12.2 A)" with footprint key
  "L6060" (XAL6060 class). No Coilcraft XAL6030 or XAL6060 sheet is held. The 13.11 / 12.29 A against 12.2 A comparison
  should name the mismatch (a pre-existing generator item, not a1elec's).
- **M9.** Quiescent drains of the new circuit are not listed: the LM5069 draws 1.3 to 1.6 mA enabled (SNVS452G page 5,
  IIN-EN) from the lid, which is default on, plus the LM74700-Q1's 80 to 130 uA (SNOSD17G 6.5) and U3B in HiZ from VBAT;
  about 1.1 Ah a month from the lid (ESTIMATE). A storage item for the record.
- **M10.** The model runs chg_a_base 4.0 A and chg_a_lid 8.0 A while the text states the register values 3.968 and
  7.936 A. Immaterial (the ceilings never bind at the basis, `.out` 4 gives the same 31.1 Wh), but the PAR text says 3.968
  A "is the nearest at or below" and then uses 4.0.

## The brief's six questions

1. **Reproduction.** All three scripts rerun from the scratch clone (Python 3, PyYAML, pdftotext) exit 0 and are
   byte-identical to the committed `.out` files; `git status` stays clean. The equivalence table reproduces (largest
   difference 2.86e-13 Wh). My own implementation (`_scratch/chk-a1elec/CHECK-own_two_pack.py`; reads only
   energy_inputs.yaml, the pinned PVGIS monthly JSON and the raw September profile, no import of energy_budget or
   energy_two_pack; closed-form quadratics for the lid path instead of bisection) gives: aggregate-equivalent case lowest
   90.9746 Wh on 655.30 Wh; design case base 218.4 / lid 378.9 Wh full, lowest **30.3 Wh base, 0.7 Wh lid, 31.1 Wh
   together**; lid 20 / 17 / 10 C: 89.0 / 63.3 / 3.6 Wh; 9.6 C meets with 0.2 Wh, 9.5 C does not; base 15 C: 8.9 / 0.7 /
   9.7 Wh; E1 stops at 48 / 59. All agree with `.out`. The trace shows why the charge side does not move the lowest
   point: both packs are full by 13 UTC every day, so the lowest point is one night from full (17 to 06 UTC, about 564 Wh
   at the node plus the lid path's losses) against 597.3 Wh usable.
2. **Lid temperature.** The basis is justified for the reference day: full mode has the lid open (ruling of 7 September),
   the lid module is outside the closed base, its self-heating is negligible (0.9 mW a cell discharging, checked), and
   holding the whole 72 h at the mean day's minimum is conservative against that day's own cycle (mean 15.55 C). It is not
   a typical night's minimum: 13.23 C is the minimum of PVGIS's hourly means, which sits above the mean of daily minima,
   and an open lid can sit below air on a clear night; the package says a real night is colder and lists chronological
   weather as open. **0.7 Wh is not a margin: the lid is at its floor (0.2 percent of 378.9 Wh).** The kit's margin is the
   base's 30.3 Wh, 31.1 Wh together (5.2 percent of 597.3 Wh usable, about 44 minutes of PS-IDLE-SPEC). The model's range:
   20 C 89.0 Wh, 17 C 63.3, 15.55 C 50.9, 13.23 C 31.1, 10 C 3.6, threshold 9.6 C, 7.5 C NOT MET (35.5 Wh unserved), 5 C
   NOT MET. The temperature factor is a steep lower bound at 0.16 A a cell (the package says so), so the real sensitivity is
   likely smaller. Nothing is claimed beyond this range; the README states the lid runs nearly empty.
3. **Gauge.** The E2E thread is tagged Part Number BQ4050; TI's engineer (TI Guru) answers "that's the only way, ie
   fooling the gauge via calibration" and "capacity and all current related parameters will be cut in half as well",
   citing SLUA760, which is written for the BQ34Z100-G1 (2.2, 2.3, 3.1 checked in the filed PDF). So k = 2 on the BQ4050
   rests on a TI forum answer, not a datasheet commitment, which the package states and carries as Q-TI-A1. File hashes
   match `v2/vendor/ti/sources.txt`. IPScale: both TRM passages confirmed (13.27 page 107 "Not supported ... MUST be set to
   0"; 14.14.1.5 lists 10E0 to 10E3). The 63 words: my own parse of SLUUAQ3A Table 14-1 (PDF pages 185 to 197) finds
   the same 63 rows in mA (48), mAh (11), cWh (2), cW (1) and 3 uA steps (1), with matching types, ranges and TI
   defaults; every written value is inside its range and is half its true value (two rounded up: 0x43c6 deadband, 0x4445
   WH alarm). The other current-related rows (CC Offset, Board Offset, CC Auto Offset) are raw calibration counts and the
   CEDV coefficients are fitted on scaled logs, as the page says. Not knowable before the bench: CC Gain and Capacity Gain
   after the k = 2 calibration (an inference, not TI's statement: the EVM's sense is 1 mOhm, SLUUBF9 R19, so if CC Gain
   scales with 1 / R and 1 / k it would read about 0.9 on 2 mOhm, inside 0.1 to 4.0), hidden firmware constants
   (Q-TI-A1), the CEDV fit, and the trips at true currents; all are on the page's bench list.
4. **Topology.** Checked against the held sheets: BQ25731 HiZ below 0.4 V, out above 0.8 V, REGN enabled in HiZ (9.3.8,
   pages 26 and 27), ILIM_HIZ 2.6 V = 7.6 / 8.0 / 8.4 A on 5 mOhm (Electrical Characteristics), VINPUT_OP 3.5 to 26 V, Table 9-1 and 9-4, IIN_HOST
   Table 9-50 (code 80 = 8.0 A, +200 mA maximum), ChargeCurrent 128 mA LSB on 5 mOhm; LM5069 VCL 48.5 / 55 / 61.5 mV,
   UVLO 2.45 / 2.5 / 2.55 V, 9 to 80 V, -2 auto-retry; LM74700-Q1 V(AK) 13 / 20 / 29 mV and -17 / -11 / -2 mV;
   CSD18510Q5B 0.79 mOhm; TCA9543A 0x70 to 0x73. With healthy parts: base to lid is blocked (ideal diode; U3B off);
   lid to base only when the lid is higher, at most 11.0 A (1.83 A a base cell), about 2.47 A at the 0.20 V join rule
   (my arithmetic agrees; it ignores the 20 mV drop, which errs high); U3B moves base energy to the lid only in daylight
   while its loop reacts, as stated. Kit off: the path is default on, joins at any gap under the limit. The single-fault
   gap is B2, the unpowered-gate pull-down M5.
5. **Charger page.** 8.20 A (196.1 W stage in, 169.6 W out) and 13.11 / 12.29 A peaks (3.29 / 1.65 A ripple at 14.5 V)
   are arithmetically right as the unconstrained peak (at noon the packs are near full, so the real node is higher and the
   currents lower, which the page notes). Board A's 19.0 W and 11.4 W sums check. XAL1010-332ME 27.4 A (30 percent drop)
   and 18.2 A confirmed. Wrong or incomplete: B1, M1 to M4. Nothing is claimed as done that is only drafted: every change
   is labelled a draft and nothing is applied to a generator ("answers S-117's frequency question" reads stronger than a
   draft direction, cosmetic).
6. **Framing.** README, TOPOLOGY and CHARGER state prototype, AI review, nothing built or measured, and "REQ-072 stays
   FAIL until the design is drawn, reviewed and tested". No page claims physical verification or fabrication readiness.
   No em dash in any a1elec page or output. No shared file is edited; the README row is an apply script, which I ran on a
   copy: it adds the row once and refuses a second run (exit 2), as stated.

## What I did not do

No KiCad, box or suite run (none needed). No web fetch: the TI documents were read from the filed copies. The
LM5069's power-limit and timer sizing, the LM5176 stage at the re-rated current and board A's thermal re-run are outside the brief and were
not attempted. The branch's non-a1elec commits were not checked.
