# S-99 correction record, 28 September 2026

Job `cx3-s99-correction`, base `684639c4feb39b425d9e51590df80a45442f966e`.
Prototype design: no board has been built, ordered or measured. This is an author correction following the
**AI review** in `checks/codex-check-1.md`, not acceptance or qualified review. Only this record folder changed.
ACCEPTED below means the finding is accepted for correction, never that S-99 is closed. The review has eleven
bullets: its final arithmetic and counts/authority bullets are grouped as F10, as this job requires.
The valid sense paths, topology, original input hashes and load arithmetic are reused. No input was changed or
re-pinned. The four SHA256 pins remain in `dev_stage.py`; a stale 0.89 A netlist label is explicitly identified
as held text, not used as the corrected wall limit. All source pages below are held locally; no network was used.

## F1. TPS2596 equation sign: ACCEPTED

**Source and conditions:** TI TPS2596 SLVSET8A, revised August 2019, `v2/vendor/power/tps2596.pdf`,
printed p.28 equation 7, visually confirmed by the coordinator in this job; p.6 electrical characteristics.
The p.6 current rows use VDS = 0.5 V; general conditions include VIN = 12 V, -40 to +125 C junction unless noted.

**Correction:** RILM [ohm] = 903 [A ohm] / (ILIM [A] - 0.0112 [A]), hence positive load current
ILIM = 903/RILM + 0.0112 A. At 1000 ohm: **0.9142 A**. Reusing the 909 ohm row's high/typical ratio
1.051/1.005 gives an estimated high 0.956043980 A. At R186 = 990 ohm (-1 percent), the same extrapolation gives
0.965582681 A. Neither is a published guaranteed maximum at 1 kohm. P before the split becomes
9.761220451/9.770759151 A without/with R186 tolerance; after the split 8.171220451/8.180759151 A.

**Propagation:** `dev_stage.py` constants and sections 3,4a,5,6; regenerated `dev_stage.out`;
`ANALYSIS.md` sections 0,1,2,3c,3d,4a,5; actionable +5V_DEV row; registry draft sections 1,2; draft comments.
**Verification:** held pp.6,28 read with pdftotext (the flattened equation's sign relies on the coordinator's
rendered-page confirmation). `correction_checks.py` (c) recomputes with Decimal exactly 0.9142 A and checks
both extrapolations and P totals; PASS. The guarantee remains INCONCLUSIVE, not manufactured by extrapolation.

## F2. Re-rating at 5.0 mohm: ACCEPTED

**Source:** TI LM5176 SNVSAI1D, revised August 2021, `v2/vendor/ti/lm5176-datasheet.pdf`, printed p.7;
Vishay WSL document 30100, revision 23-Nov-2023, `v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf`, pp.1-2;
JST VH catalogue, no printed revision, `v2/vendor/connectors/jst-vh-catalogue.pdf`, p.1.
VSNS = 43/50/57 mV at ISNS- = 24 V, swept ISNS+, VSS = 0.8 V. F-code resistance tolerance is +/-1 percent;
component TCR is +/-110 ppm/K for 5 to 6.9 mohm. The 50 K temperature change is an assumption.

**Correction:** positive output current I [A] = positive sense voltage [V] / R [ohm]. At 5.0 mohm,
initial min/typ/max = 0.043/(0.005*1.01), 0.050/0.005, 0.057/(0.005*0.99) =
**8.514851/10.000000/11.515152 A** (8.51/10.00/11.52 A). With the assumed TCR term the extremes divide
by another 1.0055/0.9945: **8.468276/11.578835 A**. At 5.6 mohm the initial values are
7.602546/8.928571/10.281385 A and the hot maximum 10.338246 A.
Re-rating is rejected BOTH because 8.9 A exceeds its own minimum and because the maximum exceeds the
10 A AWG16/standard-header lead rating. Raising a threshold alone is not proof of capacity.

**Propagation:** script/output section 5, analysis sections 0,5, registry 1 and draft explanatory comment.
**Verification:** the cited held pages were read; `correction_checks.py` recomputes initial and hot 5 mohm
limits and asserts both failures, PASS. Script section 5 also prints the 5.6 mohm results.

## F3. Timing evidence: ACCEPTED

**Source:** SNVSAI1D, revised August 2021, printed pp.6-7,16-17. VSS(CL) 1.21 V and gm 1 mS are typical;
gm is tested at 55 mV differential and VSS = 0.5 V. There is no closed-loop time constant or onset bound.
Ebyte E22-900M30S manual v1.20 printed p.2 (PDF p.3) states no packet airtime.

**Correction:** CSS/gm = 47 nF / 1 mS = 47 us is only a dimensional ratio. Assume initial SS 1.21 V,
VREF 0.8 V, constant positive overdrive DeltaV, constant typical gm and NET discharge current gm*DeltaV.
Then t [s] = CSS [F]*(1.21-0.8) [V]/(gm [A/V]*DeltaV [V]). Positive discharge means dVSS/dt < 0.
This assumes a net-current model, including its balance with the pullup; it does not establish that model.
No ISS offset is added to VSNS. At 0.3/3.4/10.4 mV: **64.233/5.668/1.853 ms**, illustrative estimates,
not bounds. Assuming output tracks SS with gain 5.088/0.8 gives illustrative droop magnitudes
40.6/460.1/1407.3 V/s, dVOUT/dt < 0. The separate nominal soft-start estimate is 7.52 ms,
not a loop-response bound. The 60 s coincident plateau is a scenario, not an established radio waveform.

**Propagation:** script/output 4b, analysis 0,1,2,3a,3d,4b,5, registry 1 and actionable PT-2/PT-4.
**Verification:** held LM5176 pages read; script 4b and independent check print the above estimates, PASS
as arithmetic only. All onset-bound and universal burst-duration conclusions removed. A/B owners must
measure simultaneous SS, rail voltage and branch/load current through actual bursts and controlled
steps to decide onset, droop and recovery. Timing remains INCONCLUSIVE.

## F4. LDO model and collapse: ACCEPTED

**Source:** AP2112 DS39724 Rev.2-2, June 2017, `v2/vendor/diodes/diodes-ap2112-ldo.pdf`, printed pp.2,8.
**Correction:** IIN = IOUT + IGND [A], positive current entering VIN and leaving through load/GND.
This is a linear-regulator current balance, not constant power. Page 8 gives no-load IQ 55 uA typical /
80 uA maximum at VIN 4.3 V, IOUT = 0; that is not a loaded ground-current bound. Retained M/P allocations
approximate input by output and explicitly omit ground current pending reconciliation, rather than
silently inventing a maximum. Bucks may increase input current while regulating fixed output power;
LDO dropout and load/UVLO responses prevent a blanket regenerative-collapse conclusion.

**Propagation:** script/output 3 and 4b, analysis 3a,4b,5, registry 1 and actionable +5V_DEV/PT-4.
**Verification:** pdftotext of both source pages confirms the topology, conditions and quiescent row;
inspection of corrected 4b shows the constant-power claim limited to regulating bucks. PASS as a source/model
correction; rail collapse stays INCONCLUSIVE. A/B owners measure load current versus rail voltage,
dropout/UVLO transitions and restart under actual loads to decide it. No new collapse number is asserted.

## F5. Capacitor support: ACCEPTED

**Source:** Quectel RM520N Series Hardware Design v1.1,
`v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf`, printed p.29 (PDF p.30).
It specifies at least 3 A continuous and 4 A peak capability, two 220 uF low-ESR capacitors, supply above
3.135 V and ripple below 100 mV, but no burst duration.

**Correction:** Q [C] = C [F]*positive allowed droop [V] = 440 uF*0.100 V = **44 uC**.
At constant positive deficit ILOAD-ICONVERTER = 1 A, t = Q/I = **44 us**, an illustrative ideal-capacitor
estimate. The actual deficit integral, effective capacitance, ESR and converter response decide support.
A duration below an illustrative loop onset is no proof of capacitor support.

**Propagation:** actionable +5V_S2 acceptance, missing inputs, A/B ownership and PT-2; analysis 4b,5.
**Verification:** held printed p.29 read; `correction_checks.py` recomputes 44 uC/44 us, PASS. The reused
7.281560 A case remains 0.224663 A above the conditional minimum. Board B measures the socket/buck
waveform; board A assesses the upstream loop; the integrator reconciles declarations.

## F6. AP64500 shutdown: ACCEPTED

**Source:** DS41979 Rev.5-2, `v2/vendor/diodes/diodes-ap64500.pdf`, printed p.6.
**Correction:** positive input supply current ISHDN is **1 uA typical / 3 uA maximum at VEN = 0 V**.
Typical conditions are +25 C, VIN 12 V; min/max apply over -40 to +85 C and VIN 3.8 to 40 V unless noted.
The conditional S3 allocation becomes 4.201346 A + 3e-6 A = **4.201349 A**, leaving **0.798651 A** below
5 A before any further branch leakage/back-power. Zero was an idealisation, not a bound.
This IC bound does not bound the whole card branch, transient stored charge or signal back-power.

**Propagation:** actionable +5V_S3 and PT-3. **Verification:** held p.6 read; independent recomputation in
`correction_checks.py` PASS. Board B must confirm VEN and measure branch leakage/card voltage/back-power;
fan/NVMe/loaded-CM5 selections remain conditional. No unconditional S3 rail PASS is claimed.

## F7. PoE off state: ACCEPTED

**Source:** TPS23861 SLUSBX9I, revised July 2019, `v2/vendor/ti/tps23861-datasheet.pdf`, printed p.7;
REQ-017 acceptance in `pcb_requirements.yaml`; JST VH catalogue pp.1-2.
**Correction:** positive powered-controller IVPWR is 3.5 mA typical / **7 mA maximum at 57 V**.
It supplies no outlet-off or stored-charge transient bound. The measured outlet power is VOUT*IOUT [W],
positive delivery to the device, and its decay/remaining delivery must be judged against REQ-017's outlet-off
0 W minimum contract. No numeric shutdown bound is asserted. AWG18/standard-header remains unrated by
this catalogue; AWG16/standard-header has a stated 10 A rating against the 0.6 A allocation.

**Propagation:** actionable +54V_POE/PT-5. **Verification:** held p.7 and JST pp.1-2 read; REQ-017/018 and
IF-AB-POWER inspected. PASS for the source correction, INCONCLUSIVE for actual off behaviour. Owners are A/B
circuit owners for interlock/PSE/shutdown, cable owner for wire/header, integrator for contract. No generic
plausible connector rating or controller supply current replaces the missing evidence or weakens REQ-017.

## F8. Thermal scenario: ACCEPTED

**Source:** CSD19532Q5B SLPS414B, revised May 2017,
`v2/vendor/power/ti-csd19532q5b-n-fet.pdf`, printed p.3; LM5176 loss formulas pp.25-26.
Typical tr/tf = 6/6 ns at VDS 50 V, VGS 10 V, ID 17 A, RG 0; RDS(on) 5.7 mohm maximum at 6 V, 25 C;
RthJA 50 K/W depends on the documented 1 square inch, 2 oz pad, not the unbuilt board.

**Correction:** positive losses Pcond = duty*I^2*R and Psw = VIN*I*(tr+tf)*fsw/2 [W];
Tj [C] = Ta [C] + P [W]*theta [K/W]. Assuming RDS multiplied by 1.5, edges by 3 and the sheet's pad
produces about 1.24 W and **112 C at assumed +50 C air**, a scenario, not an upper bound. No thermal PASS.

**Propagation:** script/output 4d,4e, analysis 4d,4e,5, actionable +5V_DEV and registry PT-4.
**Verification:** held p.3 conditions read; regenerated output reproduces the scenario and removes the bound
claim. PASS as corrected labelling; physical result INCONCLUSIVE. A owner must calculate layout losses/thermal
paths then measure Q32-Q35/R43/R177 temperatures and switching waveforms over intended loads, VBAT and ambient,
including 60 s key-down/recovery. Actual temperature is not closed by documentation alone.

## F9. Retained generator note and integration: ACCEPTED

**Requirement:** the draft must describe its resulting circuit and corrected minimum, without claiming D8
is still a +5V_DEV load. SNVSAI1D p.7 / Vishay 30100 pp.1-2 give the conditional minimum as in F2.
**Correction:** S99-DEV now replaces the complete preceding comment and declaration, including its note.
The new loads are J_5V_DEV 3.8 A plus U32 0.3 A typical; U23 is removed. Peak remains declared 6.9 A.
The note states D8 is supplied separately and gives 7.095710 A initial / 7.056897 A assumed hot minimum.
These are positive rail currents; minimum = 0.043/(0.006*1.01*1.0055) A for the latter.
**Propagation:** `apply_d8_split_draft.py` S99-DEV/NEW_STAGE; analysis 7 and registry 4.
**Verification:** `--check` exits 0, all five anchors unique, result parses, ten new references unused.
`correction_checks.py` reconstructs in memory and checks loads/note with AST, PASS. The generator is not applied.

The integrator **must rebase S99-DEV's old text onto stream s98's integrated line**. This worktree holds
the original line, so its successful check does not establish an anchor on the integration branch.
The expected s98 line below is derived exactly from held cx1 entry B2-A-DEV (5.1 A, J_5V_DEV 3.8 A,
U23 1.0 A); the integration branch itself is not present/read here. Compare the actual line and retain any
additional integrated edits before application. Replace its stale note and preceding historical/interim
comments with the complete new block below; then run --check on that integrated source.

Exact old block matched in THIS worktree:

```python
# F-PR-04, 26 September 2026: the device rail's converter is an LM5176 stage now, not an AP64500. W2 found this
# rail declared at 6.0 A peak on a 5 A part (VERIFIED) and summed its loads to the same 6.0 A (INFERRED); D-12 adds
# the Glenair host port's own eFuse U32 (0.9 A limit) behind it, so the peak is 6.9 A. The LM5176 stage's average
# current loop holds 43 to 57 mV across its 6 mOhm ISNS shunt R43 (SNVSAI1D, VSNS), 7.2 to 9.5 A, above the 6.9 A
# peak and below the JST-VH lead's 10 A. The loads now name board A's own two eFuses as well as the lead to B.
_intent.rail("+5V_DEV", 5.0, 4.0, 6.9, "R43", loads={"J_5V_DEV": 3.2, "U23": 0.5, "U32": 0.3}, budget=0.02, share=0.005, switch="U7", efficiency=0.90, fed_from="VBAT", note="the USB devices, the LimeSDR bay and the RockBLOCK behind their switches, the D8 mezzanine behind U23 and the wall host port behind U32; the net starts at the ISNS shunt R43. 9 September 2026 (ARCH-PCB-B-IOHA): +0.8 A because B16's three hub banks had to leave the slot rails. 26 September 2026 (F-PR-04, D-12): the converter is an LM5176 stage with a 7.2 A minimum average limit, and the Glenair port's 0.9 A takes the peak to 6.9 A.")
```

Exact expected s98 old declaration line for the rebase (derived as described above):

```python
_intent.rail("+5V_DEV", 5.0, 5.1, 6.9, "R43", loads={"J_5V_DEV": 3.8, "U23": 1.0, "U32": 0.3}, budget=0.02, share=0.005, switch="U7", efficiency=0.90, fed_from="VBAT", note="the USB devices, the LimeSDR bay and the RockBLOCK behind their switches, the D8 mezzanine behind U23 and the wall host port behind U32; the net starts at the ISNS shunt R43. 9 September 2026 (ARCH-PCB-B-IOHA): +0.8 A because B16's three hub banks had to leave the slot rails. 26 September 2026 (F-PR-04, D-12): the converter is an LM5176 stage with a 7.2 A minimum average limit, and the Glenair port's 0.9 A takes the peak to 6.9 A.")
```

Exact new block (the final line is the new declaration for both held and s98 cases):

```python
# S-99 (28 September 2026): D8 leaves +5V_DEV for its own buck U41 and eFuse U23 on +5V_D8IN.
# The remaining loads are board B and the wall port: 4.1 A typical, 6.9 A declared peak (B 6.0 + wall 0.9).
# R43 6 mOhm gives 7.095710 to 9.595960 A at initial +/-1 percent; with assumed 50 K and +/-110 ppm/K
# it gives 7.056897 to 9.649029 A (SNVSAI1D p.7, Vishay 30100 pp.1-2). The declared margin is 0.156897 A.
# Conditional M-tier 5.942235 A passes by 1.114661 A; P-tier 8.171220 A (8.180759 A with R186 tolerance)
# fails the minimum. S-98 reconciliation and prototype current, timing, collapse/recovery and thermal tests remain.
_intent.rail("+5V_DEV", 5.0, 4.1, 6.9, "R43", loads={"J_5V_DEV": 3.8, "U32": 0.3}, budget=0.02, share=0.005, switch="U7", efficiency=0.90, fed_from="VBAT", note="the USB devices, LimeSDR bay and RockBLOCK behind board B's switches, plus the wall host port behind U32; D8 is supplied separately by U41 through U23 from +5V_D8IN. The net starts at the output ISNS shunt R43. LM5176 minimum average limit is 7.095710 A with initial +/-1 percent, or 7.056897 A with the assumed 50 K shunt temperature change and +/-110 ppm/K TCR. The 6.9 A declared peak (B 6.0 + wall 0.9) has 0.156897 A conditional margin; actual mode current, M/P reconciliation, timing, collapse/recovery and temperatures remain unverified (S-99).")
```

## F10. Arithmetic, counts and SESSION choice: ACCEPTED

**Source/requirement:** retained M-tier 5.442235294 + 1.380 + 0.500 = 7.322235294 A;
R43 6 mohm +/-1 percent (Vishay 30100 pp.1-2); 5.088 V nominal output (SNVSAI1D p.6 and 53.6k/10k);
REQ-018 all-transmit floor 15.5 V; project efficiency 0.90; draft CHANGES; owner's standing rule of
26 September, confirmed as applicable by this job and the review. This covers the review's last two bullets.

**Correction:** Pshunt = I^2 R [W], positive dissipation: **0.321690778 W nominal / 0.324907686 W at +1 percent**.
IBAT = VOUT*IOUT/(VBAT*eta) [A], positive draw: **2.670647540 A** at 5.088 V, 15.5 V and 0.90.
The draft adds **ten references: U41, L13, C227-C232, R217, R218**, in **five replacements**.
B and B plus the wall-port interlock remain configurations. SESSION can choose B under the standing rule;
the reason is preserving console availability while meeting conditional declared demand, not lack of alternatives.

**Propagation:** script/output 4d,4g,5,6, analysis 4d,4g,5, registry 2 and this handoff.
**Verification:** independent formulas in `correction_checks.py` reproduce both losses and battery current,
PASS. Draft --check reports five entries and ten unused new references, PASS. Inspection confirms both
configurations remain explicitly named and authority does not depend on a uniqueness claim.

## Additional failed-check coverage and reused work

Review (a) was PASS and is reused. Review (b) FAIL is corrected by F1 and source classifications:
Ebyte 650 mA is typical with no published maximum/airtime; Microchip DS00002330D p.169's 1.21 A is typical
at 25 C, not a maximum (analysis 2,3a and script table now explicit); 0.85 buck efficiency is project input.
LimeSDR supply figures do not establish a transmit waveform. RockBLOCK default 500 mA input maximum is
kept distinct from the optional approximately 800 mA charging configuration; no charger limit establishes
a duration. Project allocations and the conditional USB-device bound remain labelled. Microchip printed p.169 was also read directly with pdftotext, confirming the typical column and 25 C
condition. Other source classifications and unchanged sums were reused from review (b); this is not a claim of new load measurements.

Review (c) FAIL maps to F3/F4; (d) to F1/F2/F10; (e) to F9/F10; (f) to F5/F6/F7/F8.
For (f)'s remaining ownership points, S1 retains B ownership of loaded-CM5/fan/NVMe selections and A of
converter capacity (CM5 release 3 pp.26-27,35; AP64500 DS41979 Rev.5-2 pp.1,7). Its reused conditional
6.228975 A exceeds 5 A, not a demonstrated maximum. S2 now explicitly assigns upstream-loop assessment to
A. No failed review sub-item is treated as resolved by weakening a requirement; actual evidence remains open.

## Required verification actually run

Command: `python3 v2/docs/records/s99/correction_checks.py > v2/docs/records/s99/correction_checks.out`.
The retained output records all four checks; the checker writes only disposable scratch copies under this folder
and stdout. No gate or ECAD verdict writer was run.

- (a) PASS: `dev_stage.py` exits 0 twice; both byte streams match `dev_stage.out`.
  Four separate one-byte mutations (one in each input) in `scratch/` are each refused by exact filename,
  exit 1, empty stdout. Scratch removed in finally; original hashes unchanged, no re-pinning.
- (b) PASS: draft `--check` exits 0; all five anchors and syntax pass, ten new references are unused.
  Before/after metadata for all v2 entries (excluding the captured check output) is unchanged; no marker.
  AST inspection also verifies the resulting DEV load map and corrected note without running the generator.
- (c) PASS: Decimal recomputation 903/1000 + 0.0112 = 0.9142 A; dependent P values independently checked.
- (d) PASS: all nine changed files scanned for Unicode dash U+2010 through U+2015 and minus U+2212; none.

## Recommendation after correction

Retain **option B as the next circuit candidate for SESSION review**. The 6.900 A declared demand remains
0.156897 A below the conditional 7.056897 A minimum; M = 5.942235 A is 1.114661 A below it. Before the split,
M = 7.322235 A exceeds the minimum by 0.265339 A. After the split, P = 8.171220 A (8.180759 A with R186
tolerance) still exceeds it by 1.114324 A (1.123863 A). The 50 K shunt term is assumed, not measured.

S-99 stays open: S-98 reconciliation and maker limits/actual coincident current decide M/P adequacy;
actual SS/current/voltage waveforms decide timing and capacitor support; load/dropout/UVLO/restart
measurements decide collapse/recovery; routed loss/thermal calculations and prototype temperatures decide
thermal capacity. A guaranteed 1 kohm TPS2596 maximum is not held. B plus the wall-port interlock remains a
second configuration, with a console-availability tradeoff. This correction accepts no residual physical risk,
changes no requirement and applies no circuit or registry draft.
