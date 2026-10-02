accepted: yes

# Layer 4, L4-E11: Claude's check of the charger selection at 2718e9e0 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. The owner asked for the charger implementation that supports the battery-present,
battery-absent and charging-inhibited modes, with the BQ25730 evaluated against TI's datasheet and our actual circuit. The
round (sections 12 to 14) compares (A) the drawn BQ25731 with the hold-up bank, (B1) the BQ25730 with an added battery FET, and
(B2), for which none was found. **It selects (B1): the BQ25730 with Q39 (AOS AONS21357).**

**Verified by the coordinator, on the held datasheet itself** (TI SLUSE65A, February 2021, revised January 2024, sha256
`e41ef289...`, held back under TI's terms in `v2/vendor/ti/held/`):
- *The pin change:* pin 21 is BATDRV on the BQ25730 (p.4 pin table). The round reads it as NC on the drawn BQ25731, and the
  draft adds Q39 between VSYS and a new node CH_BATQ.
- *Battery absent:* section 8.4.1.1 (p.38): "When the battery is below minimum system voltage setting, the BATFET operates in
  linear mode (LDO mode), and the system is regulated at VSYS_MIN register value". The accuracy table (p.10) prints a 12.30 V row
  at REG0x0D/0C() = 0x7B00H with a -2 % minimum (EN_OOA = 0b). So VSYS is at least 12.054 V, a printed bound at the 4S default, not
  an extrapolation from the 15.40 V row. The maximum column prints -2 % as well. That is the gap the round names, and no claim
  rests on it.
- *The cell-count strap:* section 8.3.7 (p.29) loads VSYS_MIN 3.6 V, SYSOVP 25 V and a 4.2 V charge voltage when CELL_BATPRESZ is
  pulled low "because of battery removal". The round keeps the pin a fixed 4S strap (75.14 % of VDDA, Table 8-2: VSYS_MIN 12.3 V,
  SYSOVP 19.5 V) never wired to battery presence, so a removed pack cannot load those defaults. This is a condition on the
  schematic that the draft must keep, and the register carries it.
- *Charging inhibited:* section 8.4.1.1: "system voltage is regulated 150 mV above battery voltage when BATFET is turned off (no
  charging or no supplement current)". The VSYSMAX_ACC rows (p.9) print VSRN + 150 mV within +-2 % at the 16.8 V and 12.6 V
  settings (charge disabled, EN_OOA 0b). EN_OOA must be written to 0 at boot, and that is a firmware rule in the round.
- *Q39's loss in separate arithmetic:* the profile's (42.8 / 14.4)^2 A^2 x 10.7 mOhm (RDS(on) at 125 C, the maker's sheet) =
  0.0945 W, the round's figure. The thermal bar (at most 20.54 C/W installed) and the docking pulse (about 243 A for 17.7 us
  through the body diode, which has no printed pulse rating) are new items, each with a register row and a fallback.
- *Reproduction:* `l4e11_power.py` re-run at `2718e9e0`, its output equal to the committed `.out` byte for byte; `test_l4e11`,
  `test_l4e_svg_readers` and `test_public_hygiene` 42 passed, 0 failed. No em or en dash.

**Why the selection is the right engineering call:**
- it replaces compensating circuitry (the hold-up bank, which leaned on an assumed 1 ms response) with a part whose maker's sheet
  bounds VSYS in all three modes;
- it keeps L4-E4 to L4-E8's rows (98 of 107 identical);
- it costs less.

**What it does not settle:**
- D2: load steps with no battery, against a 2.054 V margin;
- Q39's installed thermal resistance and the docking pulse;
- D6, D8, D9 and D10;
- REQ-015 at the plug;
- the BQ25730's supply (0 at LCSC).

Each is a downstream row with an owner and a fallback.

**Accepted:** U-04 becomes a downstream qualification test with bounded evidence and a workable fallback, once the draft
(`apply_gen_sch_a_charger.py`, release-guarded) is applied. On the board as drawn, U-04 stays the architecture-level choice of
section 11. The selection is the session's under the ruling of 21 September 2026: it touches no reserved line and spends nothing
beyond parts.
