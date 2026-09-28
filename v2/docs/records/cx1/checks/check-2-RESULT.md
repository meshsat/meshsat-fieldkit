# RESULT-2: AI review, second pass, of the corrected cx1 pilot (finding I-03, IF-AB-POWER), MESHSAT-1357

Independent checker, 28 September 2026 20:24 CEST. Corrected commit 8d9dec44 on fnd/cx1 (the pilot b1c744db, my
first check filed at 6e149d46 as `v2/docs/records/cx1/checks/check-1-*`). The sources did not change between the
two commits (the two intent files, both generators, the contract and the five maker documents carry the same sha256
as in my phase 1), so the phase 1 figures in `PHASE1.md` / `phase1.out` stand and were reused. Worktree read-only
throughout (`git status --short` empty before and after every step); every run was from scratch copies under
`_scratch/chk-cx1/pert2/`. Prototype framing: nothing built, ordered or measured; an AI review, not a qualified review.

## 1. WHAT THE FIRST ANSWER MISSED (from check 1)

- B1: the empty draft left board A's +5V_S2 at the AP64500-era 2.5 / 5.0 A while board B derives 4.157 / 5.628 A
  from held maker pages; one conductor cannot carry two declarations, and `dc_drop` and `derate` judge A's copper at
  the declared current.
- B2: the +5V_DEV converter-side coincidence was computed (8.9 A) but not called: A's declared peak 6.9 A = B 6.0 +
  wall 0.9 with the D8 mezzanine at zero, nothing in the record makes D8 or the wall port non-coincident, and the
  registry's own HIGH case (7.8 A, POWER-THERMAL.md lines 709 and 1037) already sits in the LM5176 loop's band.
- M1: the registry's PS-ALLTX model (POWER-THERMAL.md) was not cited at all. M2: U26's KSZ core figure was labelled
  "unverified" although PWR-F03 verifies the maker's 1.21 A. M3: copper constants not the tree's (1.724e-8, 1.31 mm2
  against `dc_drop.py:23` 1.72e-8 and the catalogue's 1.25 mm2). M4: a new mode name "PS-ALLTX-3LOADED". M5: the .out
  copied verbatim into ANALYSIS.md. M6: the script printed the input hashes but refused nothing. M7: three board B
  inconsistencies (supervisor LDOs 0.05 A against 0.12 / 0.25 A children, LoRa 0.60 against Ebyte's 0.65 A, the
  +3V3_DEV "1.4 A" comment against 1.2 A). M8: the contract's and ARCHITECTURE's "JST-VH datasheet not held" is stale.
  M9 was my own error (the TPS23861 sheet is held), not the candidate's.

## 2. WHAT THE CORRECTION CHANGED (file by file, with the numbers)

**`if_ab_power.py`** (+69 / -): literal sha256 pins for both intent files (`INPUT_SHA256`), checked before parsing;
a mismatch or a missing file exits nonzero naming the path, nothing on stdout. Copper constants now rho 1.72e-8 ohm m
(`dc_drop.py:23`) and areas 1.25 / 0.83 mm2 (JST catalogue p.2): 16 AWG pair 4.128000 mOhm at 20 C, 4.776922 at
60 C (was 3.948092 / 4.568732); 18 AWG 6.216867 / 7.194159 (was 6.284326 / 7.272222). Mode name PS-ALLTX. New rows:
S1 "registry PLAN comparison" 4.574938 A against POWER-THERMAL's 4.65 A (difference -0.075 A); S2 "INTERIM draft
alignment" line (4.2 / 5.63, Q28 2.215509 to 2.22, bound 7.281560 A over the loop minimum); +5V_DEV rows "INTERIM B
typical + D8 typical + parent wall" 5.100000 A (converter margin +1.995710 A to the 7.095710 onset) and "B peak +
D8 typical + wall peak coincidence" 7.900000 A (margin -0.804290 A, -11.33 percent); U26 inferred 0.341647 A from the
KSZ maker typical; the 7.8 A HIGH case named with margin -0.704290 A; the +5V_DEV verdict line now says the held ends
DISAGREE and the draft supplies an INTERIM alignment. Still writes nothing but stdout (no write call in the source).

**`if_ab_power.out`**: 29,914 bytes, sha256 `d9fa215b08b8928641a02394449d3e80ca4bdf41c894321b5a7dbdeb9156545a`,
the output of the script above; every other row unchanged from the pilot except where the copper figures moved.

**`apply_declarations_draft.py`**: four entries and a `--check` flag that validates in memory and returns before the
marker or any write. B1-A-S2 (`gen_sch_a.py:111`): S2 typical 2.5 to 4.2, peak 5.0 to 5.63, load J_5V_S2 5.0 to
5.63, slots 1 and 3 kept by `if _n == "2"` (A's loop variable is a string). B1-A-Q28 (`gen_sch_a.py:48`): VBAT load
Q28 2.0 to 2.22. B1-B-S2 (`gen_sch_b.py:79`): B's S2 peak 5.0 to 5.63 by `if _n == 2` (B's loop variable is an int).
B2-A-DEV (`gen_sch_a.py:120`): typical 4.0 to 5.1, loads J_5V_DEV 3.2 to 3.8 and U23 0.5 to 1.0 (D8's declared
typical), U32 0.3 kept, peak 6.9 kept and flagged stale in two comment lines above the call. Each entry adds two or
three comment lines carrying INTERIM, INCONCLUSIVE, and the 7.28 A bound against the 7.10 to 7.17 A loop minimum.

**`ANALYSIS.md`** (535 lines changed): the verbatim .out copy removed (it now names the .out and its sha256); the
mode is PS-ALLTX; a new source row K1 (Microchip DS00002330D Table 6-1 p.169); the +5V_DEV hand arithmetic added
(7.9 / 8.9 A against 7.095710 / 7.166667 / 8.333333 A, the registry HIGH 7.8 A, the lead at 6.0 A: wire60 plus four
contacts 0.268661530 V against the whole 0.100 V budget); a "Comparison with the registry's PS-ALLTX model" section;
a "recommended session decision" for A's +5V_DEV peak (8.9 A coincident bound, 7.9 A with D8 typical, LM5176
average-loop fold-back named as the limiter), explicitly left to the session and not applied.

**`CORRECTION.md`** (new, 258 lines): B1, B2 and M1 to M8 answered item by item with sources, and the four checks it
ran with their output lines.

## 3. WHICH CONCLUSIONS THE FINAL RECORD SUPPORTS

Per rail (the mode is PS-ALLTX, CONOPS section 5 S3 over S2, REQ-018, D-11):

| rail | INCONCLUSIVE earned? | interim alignment supported by the sources? | notes |
|---|---|---|---|
| +5V_S1 | yes: no CM5 maximum (Table 9), fan TBD, drive a family bound; the ends agree | no change proposed, correctly | the record now agrees with the registry's 4.65 A within 0.1 A; the 2.5 A typical on both ends stays low, consistently (PWR-F02's owner) |
| +5V_S2 | yes: the maker figures are supply-capability bounds (3.0 A, 4 A, 2.5 A) and one typical (0.9 A) | **yes**: A to 4.2 / 5.63 with J_5V_S2 5.63 and Q28 2.22, B's peak to 5.63; each figure reproduces from my phase 1 (4.157470, 5.627523, 2.215509) | the 7.28 A all-peak bound over the 7.10 to 7.17 A loop minimum is carried in the comments, labelled a bound |
| +5V_S3 | yes: as S1, plus the standby card's leakage unknown | no change proposed, correctly | |
| +5V_DEV | yes: the lead's 0.6 A gap is project typicals; the converter's peak needs a decision, not a document | **yes for the typicals**: J_5V_DEV 3.8, U23 1.0, converter 5.1 (3.8 + 1.0 + 0.3), reproducing my phase 1 | **the +5V_DEV finding stands**: A's 6.9 A peak omits D8; 7.9 A (D8 typical) and 8.9 A (every limit) both exceed the loop's 7.095710 A onset (-0.804290 and -1.804290 A) and 8.9 A exceeds even the 8.333 A typical target (-0.566667 A); the registry's HIGH 7.8 A is -0.704290 A. The record recommends the decision and leaves it to the session, which is where the authority sits |
| +54V_POE | yes: 0 A in the mode by hardware; no catalogue figure for AWG 18 on the standard header; the TPS23861 7 mA is a maximum at 57 V | no change proposed, correctly | |

Answers to my items, as CORRECTION.md gives them: B1 answered as asked (four entries, INTERIM labels, the bound kept).
B2 answered as asked, with the decision correctly left to the session (a bounded worker does not rule; the
recommendation is the 8.9 A bound with 7.9 A retained and fold-back named). M1 answered as asked (POWER-THERMAL
cited, S1 comparison 4.574938 A, HIGH case named). M2 answered as asked, with a source I had not opened: Microchip
DS00002330D Table 6-1, PDF p.169, "Supply Current - Full 1000 Mbps Operation": AVDDL 460 mA, DVDDL 750 mA, VDDIO
80 mA, AVDDH 330 mA, typicals, no maximum. I opened that page: confirmed word for word. M3 answered as asked (1.72e-8,
1.25 and 0.83 mm2; alpha kept as a declared assumption, which is right, no held document gives it). M4, M5, M6
answered as asked. M7 answered as findings for board B's owner (no generator edited), with the line references I
verified (gen_sch_b.py:86, 87, 95, 97, 130, 209). M8 answered as a finding for the integrator (pcb_interfaces.yaml:388
and ARCHITECTURE.md:1187 verified stale). M9 was mine and needed no answer.

Two residuals for the generator owners when the draft is applied, not defects of the record: the intent `note` texts
stay as held ("5 A peak at the module" on the slot rails, "the Glenair port's 0.9 A takes the peak to 6.9 A" on the
device rail), so the generated pages would carry the old rationale beside the new numbers until the owners rewrite
those notes; and CORRECTION.md cites `gen_sch_a.py:119` for the parent wall allocation where the call is on line 120
(119 is its comment), a one-line slip.

What the correction claims that I could not confirm: the internals of its own check harness (`subprocess` runs,
scratch fixtures under `v2/docs/records/cx1/scratch/` created and removed): I reproduced every outcome it reports
independently, including the identical mismatch hashes `4bb680dd...` and `9a800f78...` from a one-byte change of the
first "0" in each input, and the worktree holds no scratch folder and no marker, which is consistent with its claim;
the AsiaRF "AW7915-AED_0721R" designation attributed to SOURCES.yaml (not looked up, immaterial to any figure);
whether the LM5176 average loop would act on the 7.28 A or 8.9 A bounds (burst duty and the soft-start time constant
are computed nowhere in the tree; a bench item, as the record says).

**final record acceptable: yes**
**supports the interim declaration change: yes** (the four entries, as INTERIM, with the mode figures INCONCLUSIVE and
the +5V_DEV peak left to the session's decision)

## What I ran, and its exact result lines

- `env -C /home/claude-runner/worktrees/meshsat-fieldkit/cx1 python3 v2/docs/records/cx1/if_ab_power.py > rerun2.out`:
  `rerun2 exit 0; stderr bytes 0`; `cmp` with the filed .out: `BYTE-FOR-BYTE IDENTICAL`; sha256 of both
  `d9fa215b08b8928641a02394449d3e80ca4bdf41c894321b5a7dbdeb9156545a`; `29914 .../if_ab_power.out`; write-call grep of
  the script: `grep exit 1 (1 = none)`; worktree status count `0`.
- Scratch copies (`pert2/`), unchanged: `unchanged copies exit 0`, `unchanged copies IDENTICAL to filed`. One byte
  changed in the A intent (offset 41, still valid JSON): `exit 1; stdout bytes 0; stderr: Refused: input
  v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json: sha256 mismatch; expected 3422910a...d7d4498, got
  4bb680dd2c7490cc30c200a73c4cbcf34685c3aff45ab90a63fc61ba4f92f2ea`. One byte changed in the B intent (offset 43):
  `exit 1; stdout bytes 0; stderr: Refused: input v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json: sha256
  mismatch; expected 96ee391b...4877d8a, got 9a800f78b18e95c48ee7b11443eb67c0a442becc3b5bc1ea686307e308ab76df`.
- Draft `--check` on scratch copies of both generators as held (sha256 before `9684e7a9...4e55` and `25fa2401...2ba4f3`,
  equal to the worktree's): six `PASS` lines (`B1-A-S2`, `B1-A-Q28`, `B1-B-S2`, `B2-A-DEV`: exact old text occurs
  once; `AST` for both generators: replaced text parses), `CHECK ONLY: 4 entries, 2 generators; no writes, no marker.`,
  `check exit 0`; sha256 after identical to before; `no file added or removed by --check`; `no marker`. Independent
  count of each old text in the held generators: `old count 1` for all four, `new count in held 0`.
- Draft apply path in scratch only: `apply exit 0`, marker created, `both patched scratch generators parse`; the diff
  shows exactly the four intended lines (A:48 Q28 2.22; A:111 to 113 the S2 call with the two comment lines; A:120 to
  125 the +5V_DEV call with three comment lines; B:79 to 81 the S2 call); a second run, even `--check`: `Refused: this
  draft has already been applied or attempted.`, exit 1.
- Arithmetic against phase 1: `Q28 = 5.63*5.1/(0.90*14.4) = 2.215509 -> 2.22`; `S2 mix 4.157470 -> 4.2`;
  `S2 coincidence 5.627523 -> 5.63`; `+5V_DEV typ 3.8+1.0+0.3 = 5.1`; `DEV coincidence D8 typical 7.9, every limit
  8.9; loop min nominal 7.166667, +1% 7.095710; typ 8.333333`; `margins: 7.9 vs 7.095710 = -0.804290; 8.9 vs 7.095710
  = -1.804290; 8.9 vs 8.333333 = -0.566667; HIGH 7.8 vs 7.095710 = -0.704290`; `16 AWG 1.25 mm2: R20 0.004128 R60
  0.004777 ohm; at 6.0 A wire60+4x10mOhm = 0.268662 V; budget 0.1 V margin -0.168662`; `U26 inferred 0.341647`;
  `S1 registry mix 4.574938`. All equal the correction's figures.
- Citations opened: Microchip DS00002330D PDF p.169 Table 6-1 (460 / 750 / 80 / 330 mA, typicals, no maximum);
  POWER-THERMAL.md lines 145, 1037-1038; gen_sch_a.py lines 47, 48, 111, 112, 120, 169, 1308, 1320-1321, 1376, 1533,
  1535; gen_sch_b.py lines 79, 86, 87, 95, 97, 130, 209; gen_sch_d.py:56; pcb_interfaces.yaml:388: all as the
  correction states (the one slip: :119 for the +5V_DEV call, which is line 120).
- Dash scan (U+2014, U+2013) of the five record files: `dash grep exit 1 (1 = none)`. `git show --stat 8d9dec44`:
  five files, 644 insertions, 469 deletions, author Kyriakos Papadopoulos, no trailer.
