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

## After the review of the provisional fixes (2 October 2026, record section 16)

The external review asked for margin on TI's BATFET rule (SLUSE65A p.92) from printed data. The BUK6Y10-30P prints Ciss as a
typical only (2.36 nF at -15 V; its Fig. 12 reads about 2.87 nF near 0 V), so the pair is 4.72 nF at the maker's test point and about
5.74 nF near 0 V. Drafted, not sent:

- **Q-TI-17 (E11-37, BQ25730).** SLUSE65A p.92: "the Ciss of P-channel MOSFET should be chosen less than 5 nF". At which
  drain-source voltage is that Ciss meant (the maker's test point or near 0 V, where the battery FET works), and what does the 5 nF
  protect: the ideal diode's regulation at VBATDRV_DIODE 30 mV, LDO mode at VSYS_MIN, or the supplement entry time? Is a total gate
  charge limit at VGS -10 V the better statement, and if so, what is it? Two BUK6Y10-30P in parallel (QG(tot) at most 64 nC each at
  -10 V) are the case in hand.

## After the second review (2 October 2026, record section 17)

Drafted, not sent:

- **Q-TI-18 (E11-38, TPS16630).** SLVSET9G 6.1 (p.7) prints OUT at -0.3 V minimum, and 9.4.1 and 9.5.1 recommend a Schottky diode from
  OUT to GND for the negative spike when the device interrupts a short. With a B540C-13-F at OUT and an output loop of 60 mm of 24 AWG
  and a spring contact, interrupting up to a few hundred amperes: what negative excursion at OUT does TI accept, for how long, and
  does the hot-short response (1 us typical, p.10) have a maximum? Is I(OL) at 11.0 kOhm specified at VIN - VOUT of 17 V?

## Not for TI: the battery FETs' maker (drafted, not sent)

- **Q-NXP-1 (E11-30, BUK6Y10-30P).** The body diode's acceptance of a single exponential pulse of 242.9 A peak with a 33.8 us time
  constant (over IS's 80 A for about 38 us), from a mounting base at +70 C, about 1000 times over the part's life at most once per 10 s;
  Table 5 (p.3) prints ISM 320 A for tp at most 10 us at Tmb 25 C only. Is the pulse inside the part's capability, and what VSD does
  the part show at 80 A and 240 A at a 70 C and a 150 C junction?

## Round 9 (4 October 2026, record section 19d): Q-TI-17 extended to three devices

Drafted, not sent:

- **Q-TI-17, extended (E11-37, BQ25730; record l9stk's C3).** The case in hand is now three Nexperia BUK6Y10-30P in parallel on one
  BATDRV pin, their gates on one node: Ciss 7.08 nF typical at VDS -15 V and about 8.61 nF near 0 V for the three (no maximum printed),
  QG(tot) at most 192 nC at -10 V for the three (64 nC each). Beyond the questions above: (a) does the 5 nF figure apply to the total
  gate load of paralleled FETs, and is three acceptable for the ideal diode's regulation at VBATDRV_DIODE 30 mV, LDO mode at VSYS_MIN and
  the supplement entry; (b) with one gate node and three thresholds, does TI expect the FETs to share in LDO mode and as an ideal diode,
  or must the design assume one FET carries the LDO-mode current; (c) does BATDRV's drive (RBATDRV_ON at most 6 kOhm, RBATDRV_OFF at most
  2.1 kOhm) remain within its limits with that load, and does TI recommend a series gate resistor per FET.
  (d) Record section 19h adds a hardware charge inhibit: while the pack's breaker is off with its cells present, an external P-channel FET
  holds the battery FETs' gates (BATDRV's node) at VSYS whatever BATDRV drives, so BATDRV may sink up to its 11.5 V over its 3 kOhm least
  RBATDRV_ON (about 3.8 mA) for minutes or hours. Is that within BATDRV's capability, and does the charger fault, latch or change mode when
  its battery FETs do not turn on while it drives them (charging, LDO mode or supplement)?

## Round 11 (4 October 2026, record section 21d): Q-TI-17 (e) and (f)

Drafted, not sent. Round 11 keeps the three BUK6Y10-30P and sizes their thermal path for the worst split of the RDS(on) spread
(section 21); E11-37 stays open on TI's answer or the bench, and on a negative answer the supplier's correction scope is two FETs.
That fallback is under 5 nF only on a typical figure, so the questions name it.

- **Q-TI-17 (e) (E11-37, BQ25730).** SLUSE65A 9.2.2 (p.92) gives the 5 nF without a drain-source voltage. Nexperia prints the
  BUK6Y10-30P's Ciss as 2.36 nF typical at VDS -15 V and no maximum (17 April 2020, Table 7); its Fig. 12 reads about 2.87 nF typical
  at VDS -0.1 V (this record's reading of the rendered page, `inputs/`). Two in parallel are 4.72 nF typical at -15 V and about 5.74 nF typical near 0 V. At which VDS should a design read Ciss
  against the 5 nF, and with what margin for the part-to-part spread a maker does not print: is the pair within TI's rule?
- **Q-TI-17 (f) (E11-37, BQ25730).** If the 5 nF stands for a property of BATDRV's loops (the ideal diode's regulation at
  VBATDRV_DIODE 30 mV, LDO mode at VSYS_MIN, the supplement entry), what gate load does TI accept on BATDRV over -20 to 70 C, stated
  as Ciss at a named VDS or as QG(tot) at -10 V (three BUK6Y10-30P: 192 nC at most at VDS -15 V, 7.08 nF typical at -15 V)? SLUSE65A names no
  external driver or buffer on BATDRV; does TI support one in any of the three modes, and if so with what added delay or offset?
