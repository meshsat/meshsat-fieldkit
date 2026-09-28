# CHECK (phase 2): the cx1 candidate against the checker's own phase 1

AI review, MESHSAT-1357, 28 September 2026 19:29 CEST. Independent checker; the candidate is commit b1c744db
(base 6b419b02) on branch fnd/cx1, four files under `v2/docs/records/cx1/`, written by the Codex worker. Phase 1
(`PHASE1.md`, `phase1.py`, `phase1.out` beside this page) was written before any candidate file was opened.
Prototype framing: nothing built, ordered or measured; every figure is a desk figure.

## 1. Figures: mine beside the candidate's, and every disagreement

| item | checker (phase 1) | candidate | agree? | who is right, and why |
|---|---|---|---|---|
| A / B declarations, all five rails | as the table in PHASE1.md section 1 | identical (its "End" tables, read from the same intent files) | yes | same parse |
| B load sums | S1..S3 4.751 A, DEV 5.180 A, POE 0.600 A | 4.751000 / 5.180000 / 0.600000 | yes | |
| LM5176 loop limit, R35 and R43 6 mOhm | 7.167 / 8.333 / 9.500 A (nominal shunt) | same nominal; adds the 1 percent shunt: 7.095710 to 9.595960 A | yes | the candidate's tolerance step is correct and sourced (Vishay 30100 p.1, F = 1 percent); a bound labelled as onset |
| LM5176 loop limit, R71 20 mOhm | 2.150 / 2.500 / 2.850 A | same; 2.128713 to 2.878788 with tolerance | yes | |
| +5V_S2 typical from sources | 4.157 A | 4.157470 A | yes | |
| +5V_S2 coincident (contract's 5.63) | 5.628 A (CM5 1.6, card 4 A, rest typical) | 5.626523 without the 1 mA gate, 5.627523 with | yes | same decomposition |
| +5V_S2 worst bound | 6.382 A with the CM5 at the PROJECT allowance 1.6 A | 7.281560 A with the CM5 at the MAKER's 2.5 A (CM5 datasheet B.3, PDF p.36: "Power supply designs should accommodate 5 V at up to 2.5 A") | no | **the candidate**: 2.5 A is a maker's supply-design figure and the better-sourced bound; my 1.6 A was the generator's own headroom. With it the all-peak bound crosses the loop's minimum |
| +5V_S1 mode figure | 4.575 A (CM5 1.6, card 9.1 W) against POWER-THERMAL's 4.65 A | "planning mix" 3.407 A (CM5 0.9, card 7 W average); bound 6.228975 A (CM5 2.5, card 9.1 W, child peaks) | partly | both arithmetic lines are right for their inputs; the candidate did not compare with the registry's own PS-ALLTX model (POWER-THERMAL.md line 707: 4.65 A PLAN), which is the record's existing mode figure |
| +5V_S3 in the mode | treated as slot 1 | card OFF (K4: the standby card is off), 4.201346 A bound | no | **the candidate**: CONOPS section 5 K4 and the Reduced-mode row hold card 2 off by software; I missed it |
| +5V_DEV at the converter, typicals | 5.10 A (B 3.8 + D 1.0 + wall 0.3) | 4.6 A (B 3.8 + A's local 0.8) and 5.3 A (B 3.8 + A's child typicals 1.0 + 0.5) | partly | both are readings of the same intent; the candidate's 5.3 uses A's own VBUS_WALL typical 0.5 A, mine the parent's 0.3: A's parent load map and its child rails disagree with each other (the candidate says so explicitly, section "Method") |
| +5V_DEV at the converter, peaks | 8.89 A (wall at its 0.89 A ILM) | 8.9 A (wall at its declared 0.9 A peak) | yes | rounding of the same bound |
| +5V_DEV, the registry's own mode figure | POWER-THERMAL line 709: 5.89 A PLAN, 7.8 A HIGH, HIGH over the 7.167 minimum | not cited | no | the candidate did not read POWER-THERMAL.md (0 mentions); the page's HIGH case is the record's own statement that the device rail can reach the loop's band |
| lead pair resistance, 16 AWG, 300 mm | 4.128 mOhm (1.25 mm2 from the JST catalogue p.2; rho 1.72e-8 from dc_drop.py) | 3.948 mOhm at 20 C (1.31 mm2, 1.724e-8), 4.569 mOhm at 60 C | no (5 percent) | both are labelled models; the candidate states its constants are not from a held maker document and gives the 1.25 mm2 alternative (factor 1.048); it does not cite the tree's own rho in `dc_drop.py:23` |
| four VH contacts at the 10 mOhm initial maximum | 168 mV at 4.2 A, 225 mV at 5.63 A | 0.168 / 0.225 V inside its "wire + contact" columns | yes | |
| the 2 percent budget has no share for the lead | stated | stated ("No cable share is reserved") | yes | |
| JST rating for AWG 18 on the standard header | not stated by the catalogue | INCONCLUSIVE, same reading | yes | |
| TPS23861 document | I wrote "not held" (SOURCES.yaml line 149) | held at `v2/vendor/ti/tps23861-datasheet.pdf`, SLUSBX9I p.7 IVPWR 7 mA max at 57 V | no | **the candidate**: the file exists and the row is on p.7; SOURCES.yaml line 149 is a comment about missing part ENTRIES, not the document. My phase 1 erred here |
| +54V_POE in the mode | 0 A (interlock) | 0 A "commanded OFF, ideal settled", leakage INCONCLUSIVE | yes | |

The candidate's marginal case, reproduced by hand (its record: 7.281560 A, margin -0.185850 A):

```
card buck input, 4 A peak      = 4.0 x 3.456 / (0.88 x 5.1)   = 3.080214 A   (Quectel v1.1 p.30 peak; 3.456 V gen_sch_b.py:169; 0.88 gen_sch_b.py:170)
NVMe + switch buck, 1.8 A peak = 1.8 x 3.3 / (0.88 x 5.1)     = 1.323529 A   (project allowance, gen_sch_b.py:182)
1.0 V core buck, 1.2 A peak    = 1.2 x 1.0 / (0.85 x 5.1)     = 0.276817 A   (project allowance, gen_sch_b.py:186)
CM5 at the maker's supply figure                               = 2.5 A        (CM5 datasheet release 3, B.3, PDF p.36)
fan 0.1 (TBD) + gate 0.001                                     = 0.101 A
sum                                                            = 7.281560 A
loop minimum with R35 at +1 percent: 0.043 / 0.00606           = 7.095710 A   (SNVSAI1D p.7; Vishay 30100 p.1)
margin                                                         = -0.185850 A  (-2.62 percent)
nominal shunt: 0.043 / 0.006 = 7.166667; margin                = -0.114893 A
```

Inputs: each is what its source says, and each is labelled by kind in the candidate's table. Physical meaning: it is
a sum of four PEAKS and two supply-design figures that need not coincide, and the LM5176's average loop (SNVSAI1D
7.3.6 p.17: it discharges the soft-start capacitor, a slow loop) acts on the average over its time constant, not on
an instantaneous sum; the 5G figure is a burst peak (v1.0 Figure 5 "Burst Transmission", p.28) that the socket's two
220 uF carry in part. So the case is meaningful as a DESIGN BOUND and not as an average demand. Label: the candidate
calls it "conditional loaded BOUND", "not a guaranteed upper bound", "does not establish a real failure waveform",
and never a circuit defect. Honest. What it means in the circuit if the average did reach it: a fold-back of the
5.1 V slot rail (the loop lowers the output voltage), a brown-out of slot 2 during a 5G transmit, not a trip.

## 2. Citations opened

Every row of the candidate's source table, opened at the cited page of the held file:

| key | confirmed? | what I found |
|---|---|---|
| L1 SNVSAI1D p.7 VSNS 43/50/57; p.17 7.3.6 eq. 4 | yes | PDF p.7 "VSNS Average current loop regulation target 43 50 57 mV"; p.17 Equation 4 |
| D1 DS41979 Rev. 5-2, December 2024, p.1 "5A Continuous Output Current" | yes | p.1 features; footer "December 2024" |
| J1 JST VH p.1 10 A / 7 A / 10 and 20 mOhm; p.2 SVH-41T-P1.1; pp.3 to 5 standard vs shrouded; SOURCES "PDF of 9 January 2026" | yes | p.1, p.2, p.3 row B2P-VH, p.4 "Header (Shrouded Header)", p.5 "B 2P - VH - FB - B"; SOURCES.yaml:3183 |
| Q10 RM520N-GL v1.0 p.27 (PDF 28) 3.0 A; pp.65-66 consumption | yes | PDF p.28 printed 27; Table 37 PDF p.66-67 printed 65-66 |
| Q11 RM520N series v1.1 p.29 (PDF 30) "4 A at least" | yes | PDF p.30 printed 29; history p.5 item 4 says the peak requirement was added in 1.1 |
| C1 CM5 release 3, build 08/06/2026; p.15 (PDF 16) 3.3; Table 9 pp.26-27 (PDF 27-28); p.35 (PDF 36) B.3 2.5 A | yes | all four, words as quoted |
| W1 AW7915-AED_V1 PDF p.4 9.1 W max, 7 W average, 3.3 V 3.5 A, minimum 3 A; footer 30/05/2023 | yes | p.4 line "Power consumption maximum is 9.1W, average is 7W. Main board Power Supply design please provide 3.3V 3.5A, minimum 3.3V 3A" |
| P1 TPS23861 SLUSBX9I revised July 2019, p.7 IVPWR 3.5 typ 7 max mA at 57 V | yes | p.7 |
| R1 Vishay 30100 rev 23-Nov-2023 p.1 WSL2512 1.0 W, F = 1 percent | yes | p.1 table and part-number key |
| G1 SCLS739F revised October 2025 p.6 ICC 10 uA max | yes | p.6 |
| E1 Ebyte E22 v1.20 PDF p.3 TX 650 mA "Instant power consumption" | yes | PDF p.3 |
| S1 CP2102N Rev. 1.5 p.10 9.5 / 13.7 mA | yes | p.10 lines 509 and 512 |
| N1 Cervoz T405 Rev 2.0, 2025.06.10, p.6 active <2600 mW, idle <1050 mW | yes | p.6 |
| RB1 RB9704-001-JUN26 p.2 "60mW Idle, 1.4W Max"; Ground Control text 500 mA, about 460 mA, about 800 mA | yes | p.2; the .txt lines 310, 364, 365 |
| M1 LimeSDR page snapshots 4.5 W; 5 V 900 mA | yes | strings present in both held html files |

Not confirmed by me: the AsiaRF "AW7915-AED_0721R" designation attributed to SOURCES.yaml (not looked up; immaterial);
the printed page numbers the candidate gives beside PDF pages were spot-checked (Quectel, CM5) and agree.
Nothing the candidate quotes is absent from the page it names.

## 3. The verdicts, rail by rail: earned, over-cautious or over-bold

- **+5V_S1, +5V_S3: INCONCLUSIVE, earned.** The ends agree; no held document gives a CM5 maximum (Table 9 has none,
  "Actual figures greatly depend on the end application"), the drive is a family bound (Cervoz), the fan is TBD. The
  candidate's S3 card-off reading is right and I had missed it. Over-cautious in one respect: the registry's own
  mode model (POWER-THERMAL.md, PS-ALLTX PLAN 4.65 A on S1, finding PWR-F02) was not compared; a record on this
  finding should say whether it agrees with the record's existing figure. It does, within 0.1 A, at the 1.6 A module
  allowance.
- **+5V_S2: INCONCLUSIVE on the mode figure, earned; over-cautious on the declaration.** No held document states an
  average demand in the mode; the maker figures are supply-capability bounds (3.0 A, 4 A, 2.5 A) and a typical
  (0.9 A). The candidate is right that neither 4.2 A nor 5.63 A is a verified mode figure. But the two ends of one
  conductor cannot stand at 2.5/5.0 and 4.2/5.0: board A's text is the AP64500-era note ("5 A peak at the module",
  gen_sch_a.py:104-113, kept when F-PR-04 moved slot 2 to the LM5176), and the declared current is what `dc_drop` and
  `derate` judge board A's copper at (gen_sch_b.py:29-33 states the rule). Leaving A at 2.5 A judges A's S2 copper
  1.66 A low; understating is not the conservative side, and it is not "never pick the number that passes" either,
  because 2.5 A is simply the stale number. The held sources support an INTERIM alignment of A to B's derivation
  (typ 4.2, peak 5.63, load J_5V_S2 5.63, VBAT load Q28 2.0 to 2.22) and of B's peak from 5.0 to 5.63 (B's own note
  derives 5.63 and declares 5.0), each labelled "aligned to the end that derives its figure; the mode figure stays
  INCONCLUSIVE; the all-peak bound is 7.28 A against a 7.10 to 7.17 A loop minimum". The candidate names these as
  "bookkeeping alternatives, not recommended". I disagree with the recommendation, not with the arithmetic.
- **+5V_DEV: INCONCLUSIVE, earned; the converter-side inconsistency under-stated.** The lead disagreement (3.2
  against 3.8) is 0.6 A of project typicals; no document decides it. The candidate computes 8.9 A at the converter
  but does not say that A's own declared peak 6.9 A equals B's 6.0 plus the wall port's 0.9 with the D8 mezzanine at
  zero, and that nothing in the record makes D8 and the wall port non-coincident with B's peak (neither is an outlet
  the D-11 interlock drops; the candidate itself notes "No extra exclusion has been invented for them"). That is an
  engineering decision the record could have recommended (WORKER-RULES: take the recommended option, record it as the
  session's): either declare the coincident peak 6.0 + 2.0 + 0.9 = 8.9 A (or 7.9 A with D at its 1.0 A typical) and
  record the loop fold-back as the limiter, or write why they cannot coincide. The registry's own HIGH case, 7.8 A
  (POWER-THERMAL.md lines 709 and 1037), already sits in the loop's band; the candidate did not cite it.
- **+54V_POE: INCONCLUSIVE, earned.** Ends agree; in the mode the rail is off by hardware; the AWG 18 on a standard
  header has no catalogue figure. The candidate's reading is right, and it is right that the TPS23861 sheet is held
  (my phase 1 was wrong there).

Can the two disagreements be reconciled from held sources? Not to a verified mode figure: what is missing is (a) a
CM5 loaded-module measurement (no maker maximum exists; TEST-PLAN power tests on the prototype, FW-A15's bench
reading for the LM5176 stages at 5.1 V out), (b) the picked NVMe drive and fan (parts not chosen; the drive's family
bound is held), (c) the 5G card buck's efficiency at 5.1 V in (not plotted by Diodes; a bench reading), and (d) for
+5V_DEV a session decision on coincidence. What CAN be reconciled now is the bookkeeping: one figure per conductor
on both ends, taken from the end that derives it, labelled interim.

## 4. The script

- `env -C <worktree> python3 v2/docs/records/cx1/if_ab_power.py > <scratch>/rerun.out`: exit 0; `cmp` against the
  filed `if_ab_power.out`: **identical**; sha256 of both `e4a0397a63082be4802c20e6b1fce3314110bc3966d9deb8b9805fa3c82e1092`,
  27,262 bytes, as the candidate states. The block after `<!-- BEGIN REPRODUCED CALCULATION -->` in ANALYSIS.md
  equals the .out line for line (diff empty).
- Writes: none. Read of the source shows no `open(... "w")`, no `write_text`, no marker; `Path.read_text` and
  `read_bytes` only. Confirmed before running it in the worktree; the worktree stayed clean (`git status` empty).
- Inputs: the declarations (volts, amps_typ, amps_peak, source, loads, note) are READ from the two intent files; the
  maker figures, the shunt values, the gauges and the copper constants are typed in, each with a source comment. It
  pins nothing: it PRINTS the sha256 of both intent files and does not compare them with an expected value, so a
  changed input is visible in the output but not refused.
- Perturbation (scratch copies at the same relative depth, B's U31A changed 1.6 to 2.0): exit 0, 24 differing lines,
  the sha256 line of the B input changed, the +5V_S2 load sum went 4.751 to 5.151 and every row that carries the raw
  sum followed; the "conditional bound" rows did NOT change because they use the typed-in CM5 figures (0.9, 1.6, 2.5),
  not the load entry. So the output follows the declarations, and the typed constants are independent of them, as
  the comments say.
- Constants with a maker's document are cited in the code (SNVSAI1D p.7 and p.17, DS41979 p.1, the catalogue p.1,
  the CM5 pages, the AsiaRF sheet p.4, SCLS739F p.6, SLUSBX9I p.7 in a row string). The copper rho and AWG areas
  are declared as model inputs and not maker facts, which is correct; the tree's own rho in `dc_drop.py:23`
  (1.72e-8) is not mentioned. `RAILS` order, `GAUGES` and the 150 mm are from ASSEMBLY.md section 4 as stated.

## 5. The draft

Read: `CHANGES = []`; `main()` exits with "Refused: no sourced replacement currents; empty draft writes nothing"
before any file is read or written; the marker is created with `open("x")` only after every entry validated. Run in
a scratch copy (with copies of both generators and the same relative depth): as delivered, exit 1, no marker, the
generator copies untouched. With one entry added in scratch copies: old text absent, AssertionError, no marker;
old text occurring twice (`_intent.rail(`), AssertionError; new equal to old, AssertionError; new text that breaks
the syntax, SyntaxError from `ast.parse` before any write, generator untouched; a valid entry, exit 0, the one line
changed, the marker created; a second run, "Refused: this draft has already been applied or attempted", exit 1. The
safeguards hold. Two notes: the marker is written before the generator (a partial write leaves the marker, which the
docstring says is intended), and `ALLOWED` limits targets to the two generators, which is right for I-03.

## 6. Scope and prose

- `git show --stat b1c744db`: exactly the four files, 1,112 insertions, author Kyriakos Papadopoulos, no trailer.
- No em dash (U+2014) and no en dash (U+2013) in any of the four files (grep, exit 1).
- "AI review" present (ANALYSIS.md lines 5, 268, 276; the .out's first line); prototype framing present ("no V2
  board has been built, ordered or measured"); the intents' word "measured" is explained as a desk figure.
- No claim of a result not obtained that I could find: the two checks it says it ran (byte-identical rerun, the
  AST parse) reproduce; the hand arithmetic reproduces; the draft was not run and it says so.
- No requirement lowered: REQ-018's acceptance is restated unchanged; the 2 percent budget is kept whole; the
  outlets' 0 W is kept.
- Minor prose: it names the mode "PS-ALLTX-3LOADED", a new label for what CONOPS section 5 already defines as S3
  over S2 (three modules loaded); the registry's name is PS-ALLTX. Half of ANALYSIS.md is a verbatim copy of the
  .out, harmless but doubling the record.
