# L4-E5: source control for board A's charger on the ORed bus (MESHSAT-1357, 1 October 2026)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured, and no generator, registry, rendered page
or `HW-FW-CONTRACT.md` in the tree is edited. Implementable choice 1, SOURCE CONTROL, of `../l4e/L4-ENERGY-ARCHITECTURE.md`
(finding A-2 and its per-source closure after review L4-R04). Every figure is printed, with its basis, by
`l4e5_source_control.py` (`l4e5_source_control.out`, sections named "out N"). Section 0 of the script reproduces
`../l4e4/l4e4_limits.out` and `../r11dep/r11_dep.out` byte for byte in child processes, then runs `l4e4_limits.compute()` and
`l4e_replay.main()` in-process and checks that they print their records byte for byte, so every L4-E4 and energy figure
below comes from those records' own functions. Labels: MAKER, NETLIST, MODELED, INFERRED, ASSUMPTION, SESSION (a choice
this record makes), INCONCLUSIVE.

## The decision

**H3: U3's input-current limit is made a function of VIN_RAW in hardware, on U3's own ILIM_HIZ pin.** The function is
FW-A16's line from REQ-015's 9 V floor up, and a knee into HIZ below that floor. The tracker's output ceiling is raised so
that the line admits REQ-016's window. Firmware holds IIN_HOST at L4-E4's 4.70 A ceiling and no longer reads VIN_RAW for
control. This is the session's engineering decision. It changes no approved requirement: REQ-015, REQ-016 and REQ-072 stand
as written.

- **The pin.** On board A, a network drives U3 pin 6 (CHG_ILIM) from VIN_RAW in place of R19 and R20's fixed divider from
  REGN. Q6's HIZ pull-down stays.
  - At and above 9.0 V: V(ILIM_HIZ) = 1.000 V + 0.0690 V/V x VIN_RAW. U3's input is then 0.17252 A/V x VIN_RAW at R16's
    10 mOhm (MAKER SLUSE66A p.6: V = 1 V + 40 x IDPM x RAC).
  - Below 9.0 V, a knee (SESSION). Each threshold is TI's, with the network's +-0.5 % (ASSUMPTION) carried through it
    (out 3; nominal, then low to high):
    - the zero-current target, the pin at 1.0 V (p.6's equation at no current): 8.750 V (8.706 to 8.794 V);
    - HIZ entry, the pin falling to 0.4 V (p.17 VHIZ_HIGH, p.6): 8.508 V (8.466 to 8.551 V);
    - HIZ exit, the pin rising to 0.8 V (p.17 VHIZ_LO, p.6, p.27): 8.669 V (8.626 to 8.713 V).
  - So U3 is certainly in HIZ below 8.466 V, 0.156 V above the restart guard's highest falling threshold of 8.31 V, and
    certainly converting above 8.713 V. Between the two, the state depends on the sweep's direction and on the comparator's
    unprinted spread. At 8.70 V the pin is at 0.876 V nominal, so HIZ is not the specified state there.
  - The knee's slope at the pin is 2.484 V/V, so it needs a gain stage, not a divider (OWED).
  - U3 uses the lower of the pin and IIN_HOST, reads the pin continuously, and EN_EXTILIM is 1b at reset (MAKER pp.6, 26 and
    63).
- **The tracker's ceiling.** On board E, R10 goes from 115 k to 232 k (E96). The ceiling becomes 28.28 / 29.21 / 30.15 V,
  inside REQ-015's 36 V (INFERRED: the FBOUT rows of 8705af p.4, R10 and R11 at 1 %). The line's minimum then covers the
  window's 4.517 A from 27.98 V up.
  - TRK_OUT's C26 and C27 (10u 25V) would see 121 % of their rating and must be re-rated.
  - C24 and C25 (35 V polymer) would see 86 %, for the derating gate to judge.
  - The tracker never sits at this ceiling while charging. It holds the panel at its hold (FBIN), and the bus settles where
    the line takes what the panel gives.
- **Firmware.** IIN_HOST is a constant 4.70 A (code 94, 0x5E00), rewritten after every adapter removal, with EN_EXTILIM kept
  at 1b. VINDPM is about 18.5 V as before. A stale VIN_MON changes nothing. Details are under the behaviours below and in
  `apply_fw_a16.py`.

**Why.**
- **The sources cannot be told apart from what is drawn.** U3's VINDPM watches VBUS20 (NETLIST: U3 pin 1), which the front
  end regulates. Board A has no reading of VIN_RAW at all (NETLIST: no IC pin on VIN_RAW, FE_UVS or FE_RUN reaches a
  controller). There are three candidate signals on board E, and none works:
  - **VIN_MON's value.** REQ-015 admits every voltage from 9 to 36 V, so no voltage band belongs to the tracker alone.
  - **DCIN_PGD.** The tracker back-feeds DC_P through the hot-swap FET's body diode (NETLIST: Q7's source on DC_HS, its drain
    on HS_S). The LM5069 then raises PGD with OUT above SENSE (MAKER SNVS452G pp.3 and 12), so PGD reads high with no vehicle
    connected (INFERRED). The vehicle's own ideal diode blocks the back-feed at DC_F (SNOSD17G p.12).
  - **The LT8705A's SRVO pins.** These pins would tell "the panel limits" from "the tracker regulates" (8705af pp.11 and 19),
    but they are unconnected (NETLIST: U5 pins 25 to 28).
- **A firmware rule cannot act inside a step.**
  - VIN_RAW and TRK_OUT hold 129 uF nominal (NETLIST). From the tracker's 15.09 V to the latch's 8.31 V that is 10.23 mJ, so
    a deficit of 1, 3 or 10 W collapses the bus in 10.2, 3.4 or 1.0 ms (INFERRED; nominal estimates, pending evidence of
    the effective capacitance).
  - The vehicle entry's fault timer runs 3.13 / 4.71 / 8.16 ms (NETLIST C5 100 nF; MAKER SNVS452G p.6).
  - FW-E04 reports VIN_MON once a second. It reaches the charger's only host, the panel controller, only through a running
    compute module, because board E is on bank 3 and the panel on bank 1 (FW-C12).
  - So FW-E04's period is 319 times the entry's shortest fault timeout.
- **Only a line on VIN_RAW itself acts at the converters' speed, and it needs no source identity.**
  - **Vehicle.** The line keeps the front end's input current at or under 4.629 A at the worst point (9 V), against the
    entry's 4.80 A basis and 4.85 A minimum.
  - **Solar.** The pin takes what the panel gives, and the bus settles above the knee.
- **Why the ceiling must rise.** Under a source-blind line the front end's input is bounded at about 3.84 A at any voltage.
  So the tracker's power is admitted only at a bus voltage of at least its power over 3.84 A. At the drawn 15.09 V that is
  O-33's 54 W.
- **Why the knee.** Without it, H1 and H2 collapse the bus below 36.2 W at VBUS20 (the line is a near-constant-current load
  on a power-limited source). On the candidate panel's mean September day that is 9 hours and 187.5 of 302.7 Wh (out 4).

**The candidates not chosen** (out 3 and 4; solar given up per day at VBUS20, lower to upper bound, against the uncapped
tracker; A2's unserved at 48 h on the 100 W screening case and on the candidate panel):

| Candidate | What it needs that is not drawn | Solar given up, screening / candidate panel | A2 unserved at 48 h, screening / candidate | Why not |
|---|---|---|---|---|
| (a) FW-A16 as written | nothing (needs a running module for VIN_MON) | 336.0 to 371.2 / 0.0 to 302.7 Wh | 587.9 to 629.0 / 1196.1 to 1555.1 Wh | O-33's cap; collapses whenever the panel gives under its 47.9 W; its register reaches 6.20 A at 36 V (above L4-E4's 4.70 A from 27.6 V); no transient action |
| (b) per-source firmware, solar at 4.70 A | SRVO_FBIN or SRVO_FBOUT to U10's spare GPIO20/21 with pull-ups; still a 1 s path through a module | 0.0 to 849.8 / 0.0 to 302.7 Wh | 286.3 to 1555.1 / 1196.1 to 1555.1 Wh | a fixed solar setting collapses every hour the panel gives less; the 1 s path cannot follow a cloud |
| (c-i) a status line read by firmware directly | a dock contact (J_DOCK has none spare) and an expander input | not computed (bounded as (b)) | not computed | the interrupt, two I2C transfers and U3's own loop race a 1 to 10 ms collapse |
| H1: the line, tracker as drawn | the board A network | 374.9 to 410.2 / 0.0 to 187.5 Wh | 899.9 to 979.1 / 1196.1 to 1555.1 Wh | keeps O-33's cap; collapses under 36.2 W |
| H2: H1 and the raised ceiling | network, R10 | 0.0 to 35.2 / 0.0 to 187.5 Wh | 286.3 to 319.4 / 1196.1 to 1555.1 Wh | collapses under 36.2 W |
| offset line through zero at 8.4 V | network | not computed (no collapse) | not computed | a 12 V vehicle gets 0.81 A against FW-A16's 2.07 A |
| **H3 (chosen)** | network with the knee (a gain stage), R10, TRK_OUT's 25 V parts | **0.0 to 0.1 / 0.0 to 7.1 Wh** | **286.3 to 286.6 / 1196.1 to 1202.8 Wh** | |

H3's residue is the hours under 5.8 W at VBUS20. There, the pin's own error (INFERRED +-0.2 A) can ask more than the stage
gives, so U3 cycles in and out of HIZ above the latch. The lower bound counts those hours as nothing. Against O-33's 93 W
tracker, H3 gives up nothing in steady state above that. The objective's own gap (REQ-072) is unchanged: A2 still misses 48 h
on both traces, as L4-E2 found.

## Per-source envelopes (steady state; out 3)

U3's and the pin's maxima are in board current, by L4-E4's rules. The front end's input is taken at VBUS20's 20.7 V maximum
and 0.93.

| VIN_RAW | H3's pin | U3 effective max | Front end's input, max | Against the 4.80 A basis | FW-A16's register for comparison |
|---|---|---|---|---|---|
| 9 V (vehicle floor) | 1.621 V | 1.793 A | 4.629 A | 96.4 % | 1.55 A, 4.333 A (90.3 %) |
| 12 V | 1.828 V | 2.323 A | 4.455 A | 92.8 % | 2.05 A, 4.190 A |
| 24 V | 2.656 V | 4.443 A | 4.194 A | 87.4 % | 4.10 A, 4.025 A |
| 36 V | 3.484 V | 4.884 A (IIN_HOST governs) | 3.069 A | 63.9 % | 6.20 A, 4.033 A |
| solar, window | settles at 24.61 V nominal (22.06 to 27.52 V) | 4.439 A | power-limited | | 2.60 A (O-33) |
| solar, 50 / 30 / 10 W at VBUS20 | settles at 14.03 / 8.98 / 8.82 V | the panel's | power-limited | | collapse |

- **Vehicle and shore, 9 to 36 V.** The entry never reaches its limit while the front end's efficiency at 9 V is at least
  0.897 (C-8: undocumented). VIN_RAW is the source's, above the latch. FE_PGOOD does not drop.
- **Solar.** Under H3, VIN_RAW settles above 12 V from 49.7 W at VBUS20 (44.5 W nominal). Below that it settles between the
  knee and 12 V, and FE_PGOOD does not drop down to 5.8 W.
- **The pin's range.** The pin stays inside it: 3.509 V at 36 V, and 5.496 V at the clamp's 64.5 V against 6.5 V recommended
  (MAKER p.8). It disables itself (above 4.0 V, p.80) only above 43.5 V.

**A finding for the coordinator, restricted to H3.** Under H3's stated model, A-2's solar closure ("VIN_RAW settles above
12 V and FE_PGOOD never drops") is met from 49.7 W at VBUS20. Below that, H3's bus settles between the knee and 12 V
(out 3).
- **The trade any source-blind line faces.** The solar power that settles the bus at 12 V is the same number as the charge
  power the line admits from a 12 V source, because the pin's target is the same at the same VIN_RAW (INFERRED). So a
  source-blind line can lower H3's boundary, but only by charging a 12 V vehicle less.
- **The check's example.** H3's 9 V current held to 12 V, then rising with the same slope, the knee kept (out 3):
  - It meets the vehicle envelope: the front end's highest input is 4.629 A, as under H3.
  - Its 12 V boundary is 38.748 W, and at 40 W it settles at 12.342 V at the least (H3: 9.342 V).
  - At 12 V it admits 1.55 A (31.1 W at VBUS20 nominal) against H3's 2.07 A (41.4 W). The profile asks 42.8 W at the pack
    terminals.
  - Its window needs the tracker's ceiling at 30.98 V at the least (R10 261 k: 31.66 to 33.76 V), which puts the 35 V
    polymer at 96 % of its rating.
- **Source identity** would remove the trade. It is not necessary for any particular boundary.
- **Kept: H3 (engineering call).** REQ-015 asks the vehicle input to run the kit and charge the pack, and H3 gives the 12 V
  vehicle 10.3 W more toward the profile's load. The 12 V settle point is an acceptance wording with no physical need behind
  it here: the knee already prevents the collapse, and the front end's input on weak solar stays inside the vehicle envelope.
  The example also needs a higher ceiling with less margin on TRK_OUT's parts.
- **Not a blocker.** The 12 V figure is an acceptance statement of review L4-R04, not an approved requirement.
- **The engineering rewording of bench 7b.7, kept.** VIN_RAW settles at or above the knee, FE_PGOOD never drops, and the
  front end's input current stays inside the vehicle envelope.

## The behaviours, as contract rows (draft: `apply_fw_a16.py`, FW-A16 restated and FW-A18)

| Behaviour | Steady state | Transients |
|---|---|---|
| **Startup** (VIN_RAW unknown to firmware; U3 resets IIN_HOST once to 3.25 A after every adapter removal, SLUSE66A 9.3.6 p.26 and p.80) | The pin bounds U3's input to the line at the actual VIN_RAW from the first switching cycle, with no host. At POR, IIN_HOST holds its power-on value. p.80 annotates the reset as 2000h in the heading and 4100h in the figure, and Table 9-50's reset bits read 0x20 (3.2 A in the 5 mOhm terms of RSNS_RAC = 1b). Over R16, either annotation is at most 3.25 A of board current (INFERRED). V-A09 records the raw register and RSNS_RAC before and after FW-A01. The POR value is kept apart from the one-time 3.25 A reset after a removal. Firmware writes 4.70 A after FW-A01. On every removal, on CHRG_OK or FE_PGOOD falling (EXP_INT), it writes 4.70 A while the adapter is absent: 9.3.6 allows the write under battery only and does not reset it again at the next plug-in. Highest value ever held: 4.70 A | U3 is certainly in HIZ below 8.466 V and certainly converting above 8.713 V. HIZ entry falls at the pin's 0.4 V (8.508 V nominal), HIZ exit at the pin's 0.8 V (8.669 V nominal), and the zero-current target at 1.0 V (8.750 V). No firmware timing is involved. INCONCLUSIVE until V-A09's sweeps |
| **Source change** (the tracker and the vehicle ORed, each appearing or disappearing) | No firmware action. The higher source carries the bus. The front end's input stays inside the line for either, and for both together | The pin is read continuously (p.6) and acts through U3's input loop and the front end's loop (crossover 0.71 to 3.6 kHz, gen_sch_a.py, MODELED). U3's loop response is not printed: INCONCLUSIVE. It must beat the entry's 3.13 ms fault timeout and keep VIN_RAW above 8.41 V, the guard's highest 8.31 V plus 0.1 V (V-A08) |
| **Missing or stale telemetry** (VIN_MON older than 3 s: FW-E04's 1 s is not transient evidence) | Changes no setting: the line is hardware. Diagnostic only: with VIN_MON fresh and U3's input ADC above the pin's band by 0.3 A in three readings, report FW-A18 failed and fall back to the previous rule (the line at the reported VIN_RAW, at most 4.70 A; 1.55 A while stale). Verified by V-A10's fault injection | None needed |

## The consequence for L4-E4

**The highest IIN_HOST H3 ever writes or holds is 4.70 A.** The removal reset is 3.25 A; the POR value is at most 3.25 A of
board current on either of p.80's annotations, and so is the diagnostic fallback's highest register, 4.70 A at 36 V. So R11's coordination holds for every
register value: the margins are those of L4-E4 itself (out 7: +0.097 / +0.064 / +0.023 A with C-1's full taps at -20, 25 and
62.1 C).

**The pin adds one path above U3's own maximum.**
- **Where.** Between 26.50 and 27.24 V on a stiff source (a 24 V system's alternator), the pin's target is just under 4.70 A
  and governs with its own error. The INFERRED maximum is 5.016 A in board current, 5.095 A through R11.
- **The re-run.** Re-run with L4-E4's own `margins_for` and `tap_rule` (out 7):
  - R11 alone holds (+0.175 A worst), and so do kelvin_check's taps (+0.052 A worst).
  - C-1's full 0.38 mOhm allowance fails by up to 0.109 A (62.1 C).
  - The tap rule at 5.095 A gives 0.209 mOhm, under L4-E4's accepted 0.29 mOhm criterion.
- **What would change.** Nothing, if bench V-A07 shows the pin's error at 10 mOhm at most 0.071 A in that band. Otherwise,
  by L4-E4's own rule, R11 goes to 7 mOhm (C2904239: C-1 0.99 mOhm, highest permitted current 8.300 A against 7.262 A),
  carried to item 4.

For comparison, FW-A16 as written reaches 6.20 A at 36 V. That is 6.522 A through R11, 1.252 A over 8 mOhm's band, and would
need 6 mOhm.

## What stays INCONCLUSIVE

- **The pin's accuracy at R16's 10 mOhm.** p.10 prints +-0.4 A for a 5 mOhm RAC only. +-0.2 A is INFERRED (the same pin
  error).
- **The charger's behaviour with the pin between 0.4 and 1.15 V.** The regulation range is printed from 1.15 V (p.10).
- **The HIZ comparator's own spread.** p.17 prints one-sided limits (0.4 V falling, 0.8 V rising), and the network's
  tolerance is the only band carried.
- **The power-on value of IIN_HOST.** p.80 annotates 2000h and 4100h; V-A09 records it raw.
- **U3's input-loop response time** to a pin change. Not printed.
- **The composite loop's stability.** The tracker's FBIN loop, the front end and U3's input loop through the knee's
  2.48 V/V.
- **The front end's efficiency at 8.75 to 12 V** (C-8). It sets the 9 V envelope (passes down to 0.897) and the low-light
  energy.
- **The network's own tolerance and the knee's thresholds.** +-1 % and +-0.5 % are ASSUMPTIONS; the engineer's parts replace
  them in the same check.
- **TRK_OUT's 35 V polymer parts at 86 %** of their rating, for the derating gate.

## The bench rows that close them (V-A06 to V-A10 in the draft)

- **V-A06, steady state.** A stiff supply on VIN_RAW at 9, 12, 24, 27, 28 and 36 V, with U3 asking more than its limit. U3's
  input current must sit inside the line's band, and the front end's input at 9 V at most 4.80 A.
- **V-A07, the crossover.** VIN_RAW stepped from 26.0 to 28.5 V in 0.1 V steps. U3's input current at most 4.817 A x 10 mOhm
  over R16 measured; otherwise R11 to 7 mOhm.
- **V-A08, transients, recorded apart.** The vehicle supply stepped 24 to 12 V, 36 to 9 V and 12 to 24 V, plugged and
  unplugged, and a panel simulator stepped from 100 W to 50, 30 and 10 W and back, each under full demand. The LM5069's TIMER
  never reaches 3.76 V, VIN_RAW never falls below 8.41 V, and FE_PGOOD never drops. Peak and settling time recorded.
- **V-A09, startup and the knee.** With no host and U3 asked for full charge, VIN_RAW is swept quasi-statically (10 mV steps,
  each held 1 s) from 9.5 V down to 8.35 V and back up.
  - Pass: U3 converting at every VIN_RAW above 8.713 V, and in HIZ at every VIN_RAW below 8.466 V.
  - Recorded with the pin's voltage, each against its band: the HIZ entry on the falling sweep (8.508 V predicted, 8.466 to
    8.551 V), the HIZ exit on the rising sweep (8.669 V, 8.626 to 8.713 V) and the 1.0 V zero-current target (8.750 V,
    8.706 to 8.794 V).
  - U3's input current at most the line's band from 8.854 V up, where the pin enters the printed 1.15 to 4 V range. Below
    that it is recorded, and it must be at least 1.068 A at 9.0 V.
  - Then shore at 9, 12 and 24 V.
  - With the host: the raw IIN_HOST and RSNS_RAC at POR, before FW-A01 and after it; the one-time reset after a removal; then
    4.70 A.
  - The actual thresholds stay INCONCLUSIVE until measured.
- **V-A10, telemetry fault injection.** Every kit-bus write is logged, with U3 asked for more than its limit.
  - Reports stopped, then resumed: the sensor controller's reports stop for 30 s and then resume, on shore at 12 V and on the
    panel simulator at 50 W.
  - Telemetry absent from boot: the same two runs with no reports from the start.
  - In both cases there must be no write to IIN_HOST, ChargeOption2 or InputVoltage, IIN_HOST stays at 4.70 A, and U3's
    input current stays inside the band.
  - The network seen to fail: a laboratory supply on VIN_RAW at 12 V in place of the entry, the pin lifted above 4.0 V through
    a test link, for at most 10 s.
    - Two readings above 2.623 A (the band's 2.323 A plus 0.3 A) must not trigger the fallback; the third in a row must.
    - The fallback writes 2.05 A, then 1.55 A once VIN_MON is older than 3 s.
    - No write above 4.70 A at any point.
- **7b.7.** Restated as above, in the per-source finding.

## The check, and what changed

The collaborator's check `checks/astra-check-l4e5-1.md` read NOT YET, with no owner decision. The items, and what this round
changed in the page, the script and its output, `apply_fw_a16.py` and the tests:

| Item | What changed |
|---|---|
| B1, V-A09 required HIZ below 8.75 V, which contradicts the knee | The knee's three thresholds are computed from the transfer function and TI's levels: zero current at the pin's 1.0 V (8.750 V), HIZ entry at 0.4 V (8.508 V) and HIZ exit at 0.8 V (8.669 V). The network's +-0.5 % is carried through each, and also through the printed regulation range's start (8.810 V). U3 is certainly in HIZ below 8.466 V and certainly converting above 8.713 V. TI's current-loop error is no longer folded into the comparator, which moved the latch margin from 0.12 V to 0.156 V. V-A09 is rewritten as falling and rising sweeps, and FW-A18 and V-A08 (8.41 V) follow. Tests `t_v_a09_thresholds_agree_with_the_knee` and `t_knee_fits_between_the_latch_and_reqs_floor` |
| B2, the stale rule and the diagnostic had no verification | V-A10 added: reports stopped and resumed, telemetry absent from boot, and the network made to fail, with pass criteria. The two-reading no-trigger and third-reading trigger, the 2.05 A fallback at 12 V, 1.55 A once stale, and no write above 4.70 A. The script values the trip and the fallback. Test `t_v_a10_fault_injection_is_bounded` |
| B3, the 49.7 W boundary was claimed for every source-blind mechanism | Restricted to H3. The script evaluates the check's example line (38.748 W; 12.342 V at 40 W), and the necessity of source identity is withdrawn. The trade that does hold is stated: for any source-blind line, the 12 V solar boundary equals its 12 V vehicle charge power. H3 is kept, with reasons, and the 7b.7 rewording is kept. Test `t_b3_the_12_v_boundary_is_h3s_and_the_example_trades_the_vehicle` |
| Minor 1, the POR value was stated unqualified | p.80's 2000h and 4100h annotations and Table 9-50's reset bits are read back. The POR value (at most 3.25 A of board current, INFERRED) is kept apart from the removal reset. V-A09 records the raw IIN_HOST and RSNS_RAC before and after FW-A01. The 4.70 A ceiling stands. Test `t_startup_source_change_and_stale_rules_never_exceed_their_limits` |
| Minor 2, nominal capacitance called an upper bound | The collapse times are now nominal estimates, pending evidence of the effective capacitance (out 2 and above). Test `t_collapse_times_are_nominal_estimates` |

## For the generator owners (OWED, nothing applied)

- **Board A.** U3 pin 6's network (FW-A18): the line, the knee and the HIZ end, with Q6 kept and a single open part never
  raising the limit.
- **Board E.** R10 at 232 k, and TRK_OUT's 25 V ceramics re-rated. The circuit round re-runs L4-E4's section 0 (which refuses
  by design after any change to the netlist it reads) and this record's.
