# L4-E11: questions for TI (drafted, not sent; MESHSAT-1357, 2 October 2026)

**Drafts for the owner to send** (E2E forum or TI support), each with the part and the document. Nothing here has been sent,
and no answer is assumed. They complete the TI list of `v2/docs/review-packets/battery/REVIEW-REQUEST.md` section 4
(Q-TI-1 to Q-TI-10), which this record does not edit: the dependency round of `L4E11-SOURCE-ONLY-AND-ENTRY.md`
(section 11, rows D1 to D10) found these missing there. Each question names the dependency row it would settle; an answer
stated as a limit settles the row for production, a typical figure does not.

**Already partly answered:** Q-TI-2 (does the BQ25731 charge before any host write). TI's expert on E2E thread 1316778
(held, `v2/vendor/ti/ti-e2e-1316778-bq25731-chargecurrent-por.html`) answered that ChargeCurrent()'s POR value is 256 mA and
the register description's 0 A is in error. Section 9.6.3's "the charge will start when the host writes ChargeCurrent()"
was not addressed, so Q-TI-2 stays as REVIEW-REQUEST.md words it (row D4).

## To TI

- **Q-TI-3, addendum (row D3).** BQ25731 (SLUSE66A), 4S with CELL_BATPRESZ strapped, no battery FET: the same question with
  ChargeCurrent() = 0 instead of CHRG_INHIBIT = 1, and in two cases: (a) no battery connected; (b) a battery that can take
  charge but not discharge (its pack's discharge FET open, the charge path through that FET's body diode). In each, does the
  converter keep regulating VSYS from the adapter, at what voltage, and with which loop?
- **Q-TI-11 (rows D1, D2).** BQ25731 (SLUSE66A), 4S, no battery current possible (no battery, or both pack FETs open), the
  adapter present and CHRG_OK high:
  - Is VSYS regulated at ChargeVoltage(), and does VBAT_REG_ACC's +-0.5 % (p.9) apply in that mode? Over what temperature
    range (the row says 0 to 85 C)?
  - What are VSYS's deviation and recovery time for a system load step of 0 to 4 A at 16.8 V with no battery (Figure 10-17
    shows the OTG output only)? Is there a minimum loop bandwidth?
  - Is there a maximum effective VSYS capacitance for stable regulation in this mode (10.1 states a 50 uF minimum)?
- **Q-TI-12 (rows D7, D8).** BQ25731 (SLUSE66A 8.5, p.10):
  - The battery low-voltage clamp, 384 mA typical with VSRN under VSYS_MIN: its minimum and maximum, and over temperature.
  - ChargeCurrent()'s regulation accuracy at 0x0200 (1024 mA, 5 mOhm RSR) outside the printed 0 to 85 C, and for settings
    under 0x0200. Is the printed 0 to 85 C a junction or an ambient temperature?
- **Q-TI-13 (row D9).** TPS4811-Q1 (SLUSEE5E, p.10): the overcurrent protection delay with CTMR 22 nF is printed at 370 us
  typical only; what are its minimum and maximum over -40 to 125 C? And the short-circuit threshold V(SNS_SCP) with RISCP
  3.01 k (printed at 2.1 k and 750 Ohm only): its minimum and maximum?
- **Q-TI-14 (row D10).** CSD19536KTT (SLPS540C, p.3): gfs is printed as 329 S typical at VDS 10 V and 100 A only; is a
  maximum, or the spread of the transfer characteristic (Figure 4-3) across units and temperature, available?

## Not for TI (named for completeness)

- **Row D5 (N4):** the effective capacitance at 16.9 V of DC bias of the 1210 X7R parts on VBAT is the capacitor makers'
  item (the held Yageo CC sheet prints none); the dependency round's direct EEHZK1V181P removes the question by design.
- **Row D6 (Q-TI-7):** already in REVIEW-REQUEST.md, unchanged.

## After the consolidation round (2 October 2026, record sections 12 to 14)

The session selected TI's BQ25730 (SLUSE65A) with a battery FET (arrangement (B1)). Once board A carries it (E11-27), the
addendum to Q-TI-3 (D3) and Q-TI-11's first bullet (D1) fall away: SLUSE65A prints VSYS's regulation with no battery (VSYS_MIN_REG_ACC,
p.10) and with the charge disabled (VSYSMAX_ACC, p.9), and D4 is printed (ChargeCurrent's reset 0000h, p.49). Q-TI-12's second
bullet (D8) stays, now for the BQ25730's identical row. What (B1) asks instead, drafted, not sent:

- **Q-TI-15 (row D2, BQ25730).** SLUSE65A, 4S, no battery current, VSYS regulated at VSYS_MIN 12.3 V by the BATFET in LDO mode:
  VSYS's deviation and recovery time for a system load step of 0 to 4 A (Figure 9-22, p.96, shows the peak power mode at 4 ms a
  division only), and is there a minimum loop bandwidth in this mode?
- **Q-TI-16 (row D1's upper side, BQ25730).** SLUSE65A p.10: VSYS_MIN_REG_ACC prints -2 % in both its minimum and its maximum
  column for every setting. Is the maximum +2 %?

## Not for TI: the battery FET's maker (drafted, not sent)

- **Q-AOS-1 (E11-30).** AONS21357 (Rev 2.1): the body diode's non-repetitive pulse capability (peak current, or I2t) for a
  pulse of about 240 A decaying with a 34 us time constant, at TJ 62 C; the sheet prints IS 36 A continuous and IDM 144 A for the
  channel only.

## After the fix round (2 October 2026, record section 15)

Q-AOS-1 is withdrawn: the fix round selects two Nexperia BUK6Y10-30P, whose sheet prints a body-diode pulse rating (ISM 320 A
each, tp at most 10 us). What remains for the docking pulse is the split between the two body diodes and the rating hot (E11-30), a
bench or layout item; a question to Nexperia on ISM above 25 C is optional and is not drafted. Q-TI-15 and Q-TI-16 stand.
