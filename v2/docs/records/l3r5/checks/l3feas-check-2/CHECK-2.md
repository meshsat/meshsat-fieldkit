accepted: yes
tip: c11b99d3301537c23fef6c729fa21e66543f5ebf

# CHECK-2 of fnd/l3feas: delta check of the second issue (stream l3feas, MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 13:10 CEST.
- **The branch** is `fnd/l3feas`, tip `c11b99d3301537c23fef6c729fa21e66543f5ebf` (confirmed), on `c0324564`, on CHECK-1's
  `24942a5f`.
- **Scope:** `git diff 24942a5f..c11b99d3` only, against CHECK-1's B1 and minors 1 to 7.
- **The clone.** A `--no-local --single-branch` clone (`_scratch/chk-l3feas2`, removed after the check), with
  `int17-evidence-de11cc4e.tar` extracted and int16's held sheets added. All of them are ignored files; `git status`
  stayed clean.
- The checker wrote none of it.

## Blocking items

None.

## Minors

None new.

## What holds

**B1, R1's own Kelvin criterion.**
- **Where it now appears.** `hf_wab.out` section 4, section 1b's table, and section 1c item 3 ("in place of C-1's
  0.29 mOhm") all carry it.

  | Current through R11 | Working temperature | At 25 C, copper at 100 C | At 25 C, copper at 62.1 C | At 6.0 A on the bench |
  |---|---|---|---|---|
  | 6.569 A | 0.215 mOhm | 0.166 mOhm | 0.188 mOhm | 1.00 mV |
  | 6.588 A (four FETs) | 0.196 mOhm | 0.152 mOhm | 0.171 mOhm | 0.91 mV |

- **Recomputed, the 6.569 A row.** 42.7 mV over 6.56875 A, less R11's 6.2855 mOhm maximum, is 0.2150 mOhm. That is
  0.1660 mOhm at 25 C (copper at 100 C) and 0.1876 mOhm at 62.1 C, and 0.996 mV at 6.0 A.
- **The drafted row** (0.351 / 0.271 / 0.306 mOhm, 1.63 mV, with four FETs) also checks.
- **The statement "closing C-1 at its drafted 0.29 mOhm does not admit R1"** is on the page and in the output. It
  recomputes: 43.754 mV against 42.7 mV. CHECK-1's 43.76 mV used 6.569 A rounded.

**The minors.**
1. **O-1 now has a closure criterion (3a):**
   - the maker's sheet for the revision bought is filed, with its revision mark and sha256 in `sources.txt`;
   - `array_calc.py` is re-run on it, taking the worse sheet for every rating;
   - the ratios, the 34.29 V set point and the voltage basis are re-derived.

   The 3b rows now point to it.
2. **Disposition (c)** is reached "only on a re-run, not on any threshold alone": every measured value together, R1 and
   R2 included. The offsetting is stated.
3. **The kit-level line is named by its conditions:** 1 and 2 met on the model, 3 INFERRED, 4 NOT ESTABLISHED.
4. **REQ-016 is named** beside "No approved requirement moves": the stage's in-service input rises from 154.9 W to
   158.6 W, recomputed as 6.569 A x 20.887 V / 0.93 / 0.93, deepening the owner's open exceedance.
5. **The 6.35 A basis.**
   - It now cites SLUSE66A 9.6.22 (p.80: "50 mA to 6350 mA ... DAC clamp", with no inductance condition) and Table 9-1's
     RSNS_RAC = 0b rows (p.26, 6.35 A).
   - It says why 9.3.5 is not cited (it assumes both sense resistors at 10 mOhm; R17 is 5 mOhm) and that the 4.7 uH row
     is absent.
   - ILIM_HIZ checks: 5.7 V x 34.8 / 51.3 = 3.87 V, giving 7.17 A by the p.6 pin formula ("V(ILIM_HIZ) = 1 V + 40 x IDPM x
     Rac") at 10 mOhm, above 6.509 A. The pin reads 4.07 V at REGN's 6.0 V typical. REGN's 5.7 V minimum is on p.11, as
     cited.
6. **The 60 V ceiling is labelled** "the coordinator's 60 V safety extra-low-voltage ceiling". The quoted "the standard
   behind it is not held" is in `array_calc.out` section 2 (line 96).
7. **The LT8705A is cited as pp.11 (CSNOUT, VOUT) and 12 (CSPIN, VIN).**

**The outputs.**
- **`hf_wab.out`:** everything before section 4 is byte identical to `24942a5f`'s (5245 bytes compared). Section 4 gains
  only the two Kelvin blocks, the stage's input per setting, the "does not admit R1" line and the ILIM_HIZ check.
- **`solar_interface.out`:** the diff touches only minor 6's wording (the 60 V ceiling, in sections 1 and 4) and minor
  7's page citation (section 3). Every figure is unchanged.
- **Reruns.** Both outputs rerun byte identical at the tip.

**Hygiene.**
- The added lines carry no U+2013 or U+2014, no host names and no user paths.
- The diff touches only the five files of `v2/docs/records/l3feas/`, and nothing under `v2/ecad/` or `v2/vendor/`:
  `pcb_requirements.yaml` is untouched and no held file is committed.
- Both commits are in the owner's name with no trailer.

## Files at the tip

```
d6c15694322dfbe315db7a0efdbf131e08fe28ea76445b6d887e0b85409f1f8b  v2/docs/records/l3feas/L3-FEASIBILITY.md
c63ab64ac2732199b0a603ea8b5d68dff55c8c4efdef84f58abe519b76040075  v2/docs/records/l3feas/hf_wab.py
febb772026648511bd62905e438b3d4a5f1d029346b6133a1a86dca7920b26ea  v2/docs/records/l3feas/hf_wab.out
191431b01260e8f7b7c8151dbe21817c9fce714563e84cc811165928dbebc07b  v2/docs/records/l3feas/solar_interface.py
7d85dc88ebe8b493af2c474a2f7978583b649dd654e4f7a8985d1e3089a9609e  v2/docs/records/l3feas/solar_interface.out
```

## Figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| R1 Kelvin, 6.569 A: working / 25 C (100 C) / 25 C (62.1 C) / bench | 0.215 / 0.166 / 0.188 mOhm / 1.00 mV | 0.2150 / 0.1660 / 0.1876 mOhm / 0.996 mV |
| R1 Kelvin, 6.588 A | 0.196 / 0.152 / 0.171 mOhm / 0.91 mV | 0.196 / 0.152 / 0.171 mOhm / 0.91 mV (CHECK-1) |
| Drafted, four FETs | 0.351 / 0.271 / 0.306 mOhm / 1.63 mV | 0.351 / 0.271 / 0.306 mOhm / 1.63 mV |
| C-1's 0.29 mOhm layout at 6.569 A | 43.75 mV against 42.7 mV | 43.754 mV |
| Stage input in service, 6.2 A to R1 | 154.9 to 158.6 W | 154.9 to 158.6 W |
| ILIM_HIZ at REGN 5.7 V | 3.87 V, 7.17 A | 3.867 V, 7.17 A |
