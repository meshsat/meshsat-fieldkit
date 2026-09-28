# IF-AB-POWER: I-03 source reconciliation candidate

Correction job `cx1-if-ab-power-c1`, 28 September 2026, of authoring job
`cx1-if-ab-power`. Base supplied by the launcher:
`6e149d4660b3598af77f1f4b97f72d74ace0528c`. Prototype design: no V2 board has
been built, ordered or measured. This is desk calculation and AI review,
not a qualified engineering review or acceptance of I-03.

## Result and operating mode

The held evidence does not establish a typical current and a coincident peak
for every lead in the requested mode. All five mode verdicts remain
**INCONCLUSIVE**. The unexecuted draft now aligns the two ends provisionally:
A's +5V_S2 to 4.2 A typical / 5.63 A peak, J_5V_S2 to 5.63 A and Q28 to
2.22 A; B's S2 peak to 5.63 A. A's J_5V_DEV becomes 3.8 A and converter
typical 5.1 A, including D8's 1.0 A allocation. These interim declarations
follow the sourced derivation and the existing downstream declarations;
they do not establish the mode currents. For the +5V_DEV converter peak,
recommend a session decision on the 8.9 A coincident bound with LM5176
average-loop fold-back named as the limiter. The 7.9 A D8-typical case
already exceeds the earliest loop threshold. See the decision section and
[CORRECTION.md](CORRECTION.md) for B1, B2 and M1 to M8.

The single named mode here is **PS-ALLTX**: CONOPS PS-ALLTX with all
three compute slots loaded, slot 1 the active link-card bank and slot 3 its
standby. All mission transmitters key together, including the CM5 radio,
5G, active WiFi card, LoRa, Zigbee, satellite, SDR, VHF and HF. REQ-018's
explicit acceptance conditions still apply: the standby WiFi card, pack
heater, PoE outlet and USB-C power outlet are off, accessory contract 0 W.
The third CM5 and its storage/switch remain loaded; turning off its standby
card is not turning off its compute slot. Swapping the active WiFi bank
exchanges the slot 1 and slot 3 cases because their converters are identical.

REQ-018 requires regulation throughout a 60 s key-down begun at pack rest
voltage at least 15.5 V and every cell at most +55 C. CONOPS section 5 also
specifies the preconditions and early-stop controls. None is relaxed here.
The separate PA-alone 12.4 V case is not used to size these leads. A positive
current margin in this record does not establish that REQ-018 is met.

The generic intent declarations are not tagged with an operating mode.
Their audit rows below are retained as declarations, not substituted for
PS-ALLTX demand. In particular, the PoE 0.3/0.6 A figures describe
an enabled rail, not the commanded-off rail during PA key-down. The
commanded-off settled ideal is 0 A; actual leakage, stored-charge discharge
and shutoff timing are INCONCLUSIVE. They cannot be called measured zeros.

| Rail | Declaration comparison | Verdict in PS-ALLTX | Exact missing basis for replacement or acceptance |
|---|---|---|---|
| +5V_S1 | A and B agree at 2.5 A typical / 5 A peak; B mixed entries sum to 4.751 A | INCONCLUSIVE | Loaded CM5 current profile, exact fan, NVMe/PCIe concurrent input currents and guaranteed converter efficiency at hot input/output corners. The active AW7915 sheet already invalidates treating the card's 1.5 A child allocation as its maximum. Conditional loaded demand is 6.228975 A against the AP64500's 5 A rating. |
| +5V_S2 | A 2.5 A typical and B 4.2 A typical DISAGREE; both 5 A peaks conflict with the conditional 5.63 A quoted in the contract | INCONCLUSIVE | A sourced or measured loaded CM5/5G/NVMe/PCIe coincidence profile, buck efficiency bounds and burst duration/input transfer response. The draft aligns A's typical and both peaks to 4.2/5.63 A INTERIM; neither is a verified mode figure. A conditional loaded case reaches 7.281560 A. |
| +5V_S3 | A and B generic scalars agree; generic B entries also sum to 4.751 A | INCONCLUSIVE | Same compute/fan/storage evidence as slot 1 plus standby-card shutdown leakage. With the card commanded off, the conditional loaded case is 4.201346 A; the lower current does not prove a typical or a worst case. |
| +5V_DEV | A lead allocation 3.2 A and B typical 3.8 A DISAGREE; B entries sum to 5.18 A | INCONCLUSIVE | One concurrent load profile for all 19 B entries, exact LimeSDR revision/configuration, RockBLOCK input configuration, panel/camera/QMX/HDMI loads, and A's D8/host local loads. A's 4/6.9 A totals cannot simply be copied to the lead. B peak plus A child peaks gives a conditional converter demand of 8.9 A. |
| +54V_POE | A and B generic scalars agree at 0.3/0.6 A; B 0.593+0.007 A is a peak allocation | INCONCLUSIVE | Mode shutdown transient/leakage evidence and JST current rating for the actual standard B2P-VH header with AWG18. The held 7 A rating is expressly for a different, shrouded header. No numerical contact rating is inferred for the fitted combination. |

The evidence gap is an engineering finding, not a failure to create the job's
five deliverables. No declaration is lowered to obtain a favourable result.

## Held sources, revisions and quotations

Pages below are printed document pages, with PDF page numbers where different.
All PDF readings used `pdftotext -layout <file> -`. Source documents were not
modified. The numeric tables in `if_ab_power.out` identify which input is a maker
fact, a project declaration, an assumed conversion or an unresolved estimate.

| Key | Held source and revision | Page and relevant text | Use and limitation |
|---|---|---|---|
| L1 | `v2/vendor/ti/lm5176-datasheet.pdf`, TI SNVSAI1D, revised August 2021 | p.7, VSNS: "Average current loop regulation target", minimum/typical/maximum 43/50/57 mV; p.17 section 7.3.6, equation 4: 50 mV / RSNS | Output average-current-loop threshold, not a fixed output-current rating or a hard instantaneous peak clamp. Electrical-characteristic test conditions apply. |
| D1 | `v2/vendor/diodes/diodes-ap64500.pdf`, Diodes DS41979 Rev. 5-2, December 2024 | p.1: "5A Continuous Output Current" | U4 and U6 output rating. The high-side switch's larger current-limit value is not substituted for it. |
| J1 | `v2/vendor/connectors/jst-vh-catalogue.pdf`, revision not printed; SOURCES.yaml identifies PDF of 9 January 2026 | p.1: "10 A" with "AWG #16 with the standard type header"; "7A" with "AWG #18 with the shrouded type header"; initial/after-test contact resistance 10/20 mOhm maximum | 10 A applies to four AWG16 leads with standard headers; neither 10 A nor 7 A is stated for the actual AWG18/standard combination. p.2 lists SVH-41T-P1.1 for AWG20 to AWG16. pp.3 to 5 distinguish B2P-VH standard and B2P-VH-FB-B shrouded. |
| Q10 | `v2/vendor/quectel/quectel-rm520n-gl-hardware-design-v1.0.pdf`, Version 1.0, 2022-07-15 | p.27 (PDF p.28), section 3.3.1: "continuous current capability of the power supply is 3.0 A at least" | A supply-capability requirement, not 3 A typical consumption. This held revision does not supply the 4 A claim. Its reference consumption results on pp.65 to 66 are mode-specific and not a universal peak. |
| Q11 | `v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf`, Version 1.1, 2023-03-16, indexed in SOURCES.yaml and sources.txt | p.29 (PDF p.30), section 3.3.1: continuous capability at least 3 A and "peak current capability of the power supply is 4 A at least" | Source of the contract's 4 A input. These are lower bounds on required supply capability, not measured typical/maximum currents. They do not bound all bursts from above. |
| C1 | `v2/vendor/cm5/cm5-datasheet.pdf`, Raspberry Pi Compute Module 5, release 3, build date 08/06/2026 | p.15 (PDF p.16), section 3.3; Table 9 pp.26 to 27 (PDF pp.27 to 28): operation 900 mA typical, no maximum. p.35 (PDF p.36), B.3: "Power supply designs should accommodate 5 V at up to 2.5 A" | 0.9 A typical is not loaded all-transmit demand. 2.5 A is a design allowance, not a characterised waveform. The 5 A USB-PD input capability is not CM5 consumption. |
| W1 | `v2/vendor/wifi/asiarf-AW7915-AED_V1.pdf`, AsiaRF AW7915-AED_0721R per SOURCES.yaml; held sheet footer last updated 30/05/2023 | PDF p.4: maximum 9.1 W, average 7 W; power-supply design 3.3 V 3.5 A, minimum 3.3 V 3 A | Applies to the named AW7915-AED, not the similarly named NP1 or AE1. Average lacks a workload definition. The newer one-page `asiarf-AW7915-AED-datasheet.pdf`, footer 04/22/2026, was also read and gives no replacement current or power figure. |
| P1 | `v2/vendor/ti/tps23861-datasheet.pdf`, TI SLUSBX9I, revised July 2019 | p.7, IVPWR at VVPWR=57 V: 3.5 mA typical, 7 mA maximum | B U5's 7 mA is a maximum at this condition; the 0.593 A port allocation is the residual of a project 0.6 A budget. |
| R1 | `v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf`, Vishay 30100, revision 23-Nov-2023 | p.1: WSL2512 1 W; F tolerance code +/-1% | Corroborates the generator's 6 mOhm WSL25126L000FEA initial tolerance. No unproved hot shunt/PCB/filter error bound is added. |
| G1 | `v2/vendor/ti/ti-sn74lv1t08.pdf`, TI SCLS739F, revised October 2025 | p.6, ICC 10 uA maximum at static inputs and no output load | The 1 mA entry is a design allocation; dynamic current is additional. |
| E1 | `v2/vendor/lora/ebyte-e22-900m30s-user-manual-en-v1.20.pdf`, held v1.20 | p.2 (PDF p.3): TX current 650 mA typical, "Instant power consumption" | B U21's 600 mA is not this figure. No maximum TX current is printed in that table. |
| S1 | `v2/vendor/silabs/silabs-cp2102n.pdf`, Silicon Labs revision 1.5 | p.10 Table 3.2: 9.5 mA typical at 115200 baud, 13.7 mA typical at 3 Mbaud, continuous bidirectional data; maximum blank | Each bridge's 20 mA is an allocation, not either maker typical or a stated maximum. |
| N1 | `v2/vendor/storage/cervoz-m2-2242-nvme-titan.pdf`, Cervoz T405 Rev.2.0, 2025.06.10 | p.6: active <2600 mW; idle <1050 mW | A held candidate-family bound, not evidence that the socket's exact installed drive, capacity and load are fixed; it does not supply the whole NVMe plus PCIe switch input current. |
| RB1 | `v2/vendor/rockblock/rb9704-datasheet-RB9704-001-JUN26.pdf`, RB9704-001-JUN26 | p.2: "60mW Idle, 1.4W Max" | Module/product power does not establish the input recharge waveform. Held Ground Control hardware page, snapshot 2026-09-27, `groundcontrol-docs-rockblock-9704-hardware-20260927.txt`, sections DC input and supercapacitor charge current: 500 mA DC input maximum, about 460 mA default charge limit, optional about 800 mA. Web snapshot has no page number or printed revision. Do not replace the 0.45 A burst allocation with a lower limit. |
| M1 | `v2/vendor/limesdr/myriadrf-limesdr-mini-2-0-page-20260925.html` and `myriadrf-limesdr-mini-2-0-user-setup-20260926.html`, maker page snapshots dated in filenames | Specification table: 4.5 W; setup power paragraph: 5 V, 900 mA. Unpaginated, no printed revision | Does not state the generator's 1.2 A, nor validate its 3 A eFuse allocation as a Mini 2.4 operating peak. Exact revision/configuration and startup waveform remain missing. |
| K1 | `v2/vendor/microchip/microchip-ksz9897-datasheet.pdf`, Microchip DS00002330D, 2019 | p.169 Table 6-1: AVDDL 460 mA + DVDDL 750 mA at 1.2 V, full 1000 Mb/s, all ports 100% utilisation, 25 C | VERIFIED maker typical 1.21 A, no maximum. U26 input is inferred from this and assumed 0.85 efficiency. POWER-THERMAL PWR-F03 also flags AVDDH 330 mA at 2.5 V. |

The read-only design sources are the two supplied intent files (hashes in the
calculation), their generator declarations, `ASSEMBLY.md` section 4, CONOPS
sections 4a and 5, REQ-018, IF-AB-POWER, and
`feasibility/POWER-THERMAL.md` lines 145, 706-711, 960-962 and 1037-1038. The newest EXECUTION-PLAN checkpoint
is 28 September 2026 18:50 CEST; CODEX-WORKER and the handover pages preserve
layers 1 to 3 as complete and later layers as open. Nothing in this authoring
job changes that status. The decisions registry was read, not changed.

ARCHITECTURE's I-03 and F-PR-05 entries correctly retain the disagreement.
Its statement that the JST-VH document is not held, repeated in IF-AB-POWER,
is stale: J1 is held and identifies both the applicable AWG16 rating and the
AWG18/header evidence gap. That shared-registry wording is for its owner to
update after review, outside this draft's permitted numerical changes.

## Method, units and uncertainty

Current is in amperes, voltage/drop in volts, resistance in ohms, copper
length in metres and area in square millimetres. Signed margin is limit
minus demand, with percentage relative to that limit. It is not a PASS.
All generic declared typical and peak currents and B load sums are read
directly from the intents. B's load map does not contain per-entry typical
or peak tags; the classification table gives the generator's purpose and
does not invent a maker classification where none exists.

For converters, the relevant load is total converter output. For a lead,
it is only that lead's current. A's +5V_DEV local U23 and U32 do not flow
through J_5V_DEV, but do consume converter headroom. A declares local
0.5+0.3=0.8 A in its parent load map; its own child rails instead declare
1.0+0.5=1.5 A typical and 2.0+0.9=2.9 A peak. The D8 feed and USB host port
are not the PoE/USB-C power outlets that D-11 turns off. No extra exclusion
has been invented for them.

S2 and DEV: 43 mV / 6 mOhm = 7.166667 A at nominal resistance, commonly
rounded to 7.2 A in the contract. With the drawn 1% initial resistance
tolerance the earliest threshold is 43 mV / 6.06 mOhm = 7.095710 A; latest
is 57 mV / 5.94 mOhm = 9.595960 A. The latter has only 0.404040 A, 4.04%,
arithmetic margin to the 10 A contact rating, not guaranteed protection
coordination. For PoE, R71 is 20 mOhm, not the separate 10 mOhm cycle-sense
resistor: corresponding limits are 2.128713 to 2.878788 A with initial
tolerance. These limits are found in the `lm5176` helper's output ISNS path
and its S2, SD and POE calls. They do not prove the inductor, FETs, thermal
design, input source or transient response can support those currents.
Shunt temperature rise/TCR and sense-filter mismatch are not fully bounded.

The converted-load relationship is Iin = Vout * Iout / (Vin * efficiency).
The child intents' 0.88 and 0.85 efficiencies are project assumptions,
not guaranteed minima from their makers at these operating corners. Using
them creates a **conditional design bound** only. Reduced voltage at B,
additional losses and lower efficiency increase current. No converter
quiescent-current or wiring-loss correction has been silently credited.
The reported six decimal places permit reproduction, not that precision
in the engineering inputs. All actual all-transmit typical/peak results
remain INCONCLUSIVE.

Every lead has 150 mm supply plus 150 mm return. The calculation assumes
all its current returns on that paired conductor, with no credit for
parallel signal-ground paths. ASSEMBLY specifies AWG16 for the four 5 V
pairs and AWG18 for PoE. Use the tree's rho20 = 1.72e-8 ohm m
(`v2/ecad/tools/dc_drop.py:23`, read only) and JST J1 p.2's conductor-size
range endpoints, 1.25 mm2 for AWG16 and 0.83 mm2 for AWG18. These align
the desk model with held inputs; they are not a guarantee of a particular
finished cable's area or resistance. The temperature coefficient remains
an explicit ideal-copper assumption, 0.00393/C: no held document gives it
for the assembled lead. Exact cable, stranding, plating and cut-length
resistance tolerances remain INCONCLUSIVE. The 60 C calculations therefore
remain conditional rather than certified cable bounds.

R(T) = rho20 * 0.300 / area_m2 * [1 + 0.00393 * (T-20)]. For AWG16 this
is 4.128000 mOhm at 20 C and 4.776922 mOhm at 60 C; for AWG18 it is
6.216867 and 7.194159 mOhm. The 60 C point is copper temperature, not
ambient or a prediction of self-heating. No cable thermal qualification
is implied. The contact's +105 C maximum includes its current-induced
rise; J1 gives no application-specific current/temperature derating curve.

The extra contact-bound tables apply four mated contacts per complete
loop, two at A and two at B, each at J1's initial 10 mOhm or after-test
20 mOhm maximum. No unsupported temperature correction to those maxima
is made. These are conditional contact bounds plus the assumed copper
resistance, not measured losses or a bound on every crimp's added loss.
Crimp quality, actual contact temperature and board copper still require
evidence. The AWG16 10 A current rating does not promise a small enough
voltage drop at a given current.

The intents allow 2% end-to-end voltage loss: A has 0.5 percentage point
and B 1.5, already the full allowance. No cable share is reserved. The
tables compare cable loss with the entire 2% only as a generous necessary
test; positive remainder is not permission to add that loss to both
boards' full shares. There is no raised budget. For +5V_DEV the declared
5.0 V is used; its drawn 53.6k/10k divider and 0.8 V reference imply
5.088 V nominal before tolerance (ASSEMBLY calls it 5.1 V). That nominal
distinction does not authorise more drop or fix the current disagreement.
The CM5's 4.75 V minimum (C1 p.15) is not substituted for the stricter
existing 2% design budget.

## Conditional cases recomputed by hand (correction check d)

For S2, the contract's 5.63 A is reproducible, but its assumed CM5 load
is 1.6 A and its other converters are at their typical declarations:

```text
5G buck input = 4.0 A * 3.456 V / (0.88 * 5.1 V) = 3.080213904 A
NVMe/switch input, typical = 0.9 * 3.3 / (0.88 * 5.1) = 0.661764706 A
PCIe core input, typical = 0.8 * 1.0 / (0.85 * 5.1) = 0.184544406 A
Old total = 1.6 + 3.080213904 + 0.661764706 + 0.184544406 + 0.1
          = 5.626523016 A, rounds to 5.63 A.
The later gate allocation adds 0.001 A: 5.627523016 A.
At quoted 5.63 A: earliest-loop margin = 7.095709571 - 5.63 = +1.465709571 A.
Contact margin = 10 - 5.63 = +4.37 A (43.7%).
```

In the same mode, use C1's 2.5 A CM5 design allowance and the child
intents' peak figures. No capacitor smoothing is assumed. Quectel's
two 220 uF capacitors do not establish the upstream current waveform
without burst duration, ESR, tolerances and loop response.

```text
NVMe/switch input, declared peak = 1.8 * 3.3 / (0.88 * 5.1) = 1.323529412 A
PCIe core input, declared peak = 1.2 * 1.0 / (0.85 * 5.1) = 0.276816609 A
Conditional loaded total = 2.5 + 3.080213904 + 1.323529412 + 0.276816609
                         + 0.100 + 0.001 = 7.281559925 A (rounding in terms).
R35 maximum initial resistance = 0.006 * 1.01 = 0.00606 ohm
Earliest average-loop threshold = 0.043 / 0.00606 = 7.095709571 A
Margin = 7.095709571 - 7.281559925 = -0.185850354 A, about -2.62%.
Contact margin = 10 - 7.281559925 = +2.718440075 A, about +27.18%.
Rpair20 = 1.72e-8 * 0.300 / (1.25e-6) = 0.004128000000 ohm
Rpair60 = Rpair20 * (1 + 0.00393 * 40) = 0.004776921600 ohm
Wire drop20 = 7.281559925 * Rpair20 = 0.030058 V
Wire drop60 = 7.281559925 * Rpair60 = 0.034783 V
Initial contact maximum contribution = 7.281559925 * 4 * 0.010 = 0.291262 V
Wire60 + initial contact bound = 0.326046 V
Whole existing drop allowance = 5.1 * 0.02 = 0.102 V
Whole-budget margin at this contact bound = 0.102 - 0.326046 = -0.224046 V
```

The exact unrounded script value is 7.281560 A to six decimals. This
conditional case exceeds the earliest average-limit threshold and the
contact-drop bound exceeds even the whole rail loss budget. It does not
establish a real failure waveform: demand, efficiency and duration are
unproven. Nor does using the 8.333 A typical threshold justify a PASS.
The positive 10 A contact-current margin does not resolve voltage loss.

For the +5V_DEV converter, use B's declared peak and A's declared local
loads. This distinguishes the lead's 6.0 A from the converter's full demand:

```text
B peak = 6.0 A                         (gen_sch_b.py:97)
D8 typical / peak = 1.0 / 2.0 A        (gen_sch_a.py:169; gen_sch_d.py:56)
Wall peak = 0.9 A                      (gen_sch_a.py:1535)
Held A peak = 6.9 = 6.0 + 0.0 + 0.9 A (D8 omitted)
D8 typical coincidence = 6.0 + 1.0 + 0.9 = 7.9 A
All-declared-peak bound = 6.0 + 2.0 + 0.9 = 8.9 A
Earliest loop = 0.043 / (0.006*1.01) = 7.095709571 A
Nominal-shunt minimum = 0.043 / 0.006 = 7.166666667 A
Margin, D8 typical = 7.095709571 - 7.9 = -0.804290429 A (-11.33%)
Margin, every limit = 7.095709571 - 8.9 = -1.804290429 A (-25.43%)
Typical loop = 0.050 / 0.006 = 8.333333333 A
Margin, every limit at typical loop = 8.333333333 - 8.9 = -0.566666667 A
Latest initial loop = 0.057 / (0.006*0.99) = 9.595959596 A
Registry HIGH earliest margin = 7.095709571 - 7.8 = -0.704290429 A

Interim converter typical = B 3.8 + D8 1.0 + parent wall 0.3 = 5.1 A
Child-typical sensitivity = B 3.8 + D8 1.0 + child wall 0.5 = 5.3 A
J_5V_DEV carries only B: 6.0 A at its declared peak, not 8.9 A
Lead contact-current margin = 10.0 - 6.0 = 4.0 A
Lead pair R20 = 1.72e-8 * 0.300 / 1.25e-6 = 0.004128 ohm
Lead pair R60 = 0.004128 * (1 + 0.00393*40) = 0.0047769216 ohm
Wire drop20 = 6.0 * 0.004128 = 0.024768 V
Wire drop60 = 6.0 * 0.0047769216 = 0.028661530 V
Wire60 + initial contact bound = 0.028661530 + 6.0*4*0.010 = 0.268661530 V
Whole existing allowance = 5.0*0.02 = 0.100 V
Whole-budget margin at this bound = 0.100 - 0.268661530 = -0.168661530 V
```

The eFuse settings support the local declared cases: D8 U23 is nominally
2.0 A (`gen_sch_a.py:1308`); wall U32 is nominally 0.89 A (`:1533`), rounded
to its declared 0.9 A. Using 0.89 A would give 7.89/8.89 A. That is a
nominal setting, not a worst-tolerance cap and not a reason to lower the
0.9 A declaration. B's 6.0 A is a declared peak, not an upstream clamp.

## Comparison with the registry's PS-ALLTX model

`feasibility/POWER-THERMAL.md:706-711` gives S1 PLAN/HIGH 4.65/4.66 A and
+5V_DEV PLAN/HIGH 5.89/7.8 A. Lines 1037-1038 explicitly place DEV HIGH
inside the loop band; the low end can limit. PWR-F01 to PWR-F03 at lines
960-962 identify the understated WiFi child declarations, S1's 4.65 A
inferred PLAN current, and verified KSZ9897R maker currents respectively.
Those findings remain with their circuit owners.

For a comparable S1 mix, rather than the original 0.9 A CM5 and 7 W WiFi:

```text
S1 comparison = 1.6 + 9.1/(0.88*5.1) + 0.9*3.3/(0.88*5.1)
              + 0.8/(0.85*5.1) + 0.100 + 0.001
              = 4.574938345 A
Difference from PLAN = 4.574938345 - 4.65 = -0.075061655 A
```

It agrees within 0.1 A. AsiaRF W1 p.4 supplies the 9.1 W maximum; the
1.6 A CM5 and other child currents/efficiencies are project allowances.
The original 3.407024 A mix uses different inputs, not a different named
mode. The 2.5 A CM5 plus child peaks still gives S1's conditional 6.228975 A
bound against the AP64500's 5 A rating. No mode verdict is reopened.
The DEV HIGH 7.8 A is a distinct thermal-model case; it supports the same
fold-back concern as this record's explicit 7.9/8.9 A interface coincidence.

K1 and PWR-F03 correct the U26 evidence classification. The maker's full
1000 Mb/s typical at 25 C is verified, while the converter input remains
inferred at an assumed efficiency:

```text
KSZ 1.2 V typical = 0.460 + 0.750 = 1.210 A (DS00002330D p.169 Table 6-1)
U26 input = 1.210*1.2/(0.85*5.0) = 0.341647059 A
Increase over held allocation = 0.341647059 - 0.150 = 0.191647059 A
B mixed sum with only U26 corrected = 5.180 + 0.191647059 = 5.371647059 A
```

This is not a verified mode total or a maker maximum. The output table
retains the held 0.15 A in its **Declared A** column, explicitly labels it
below the verified maker typical, and supplies the 0.341647 A inference.
PWR-F03 also reports AVDDH 0.330 A at 2.5 V above its 0.15/0.25 A declaration.

## Declaration draft and recommended session decision

`apply_declarations_draft.py` contains four exact-text entries covering
all interim changes in CORRECTION B1/B2. Its application remains unexecuted.
Only `--check` ran: all old text occurs exactly once in the held generators,
all resulting generator text parses with `ast`, and this branch returns
before any marker or file write. Its owner application still validates all
files before writing and refuses a second attempt via an exclusive marker.
The conditional slot expressions preserve slots 1 and 3. Q28's 2.22 A is
5.63*5.1/(0.90*14.4) rounded up, not a low-input-voltage current bound.

**Recommendation for session decision (`authority: SESSION`, pending):**
declare board A's +5V_DEV converter peak at **8.9 A**, the explicit bound
B 6.0 + D8 2.0 + wall 0.9, and retain **7.9 A** as the case with D8 at its
1.0 A typical. Name the **LM5176 average-current loop's fold-back** as the
limiter. Nothing in the held circuit or CONOPS prevents this coincidence:
U30/U26 gate POE_EN and PD_EN only (`gen_sch_a.py:1320-1321,1376`), whereas
D8 and the wall host use D8_EN and USBX_EN (`:1308,1533`). They are not the
accessory power outlets. A's present 6.9 A omits the mezzanine entirely.

TI SNVSAI1D p.17 section 7.3.6 says the average-current amplifier gradually
discharges the soft-start capacitor and lowers the output voltage. It is
not an instantaneous 7.10 A clamp or a clean trip. If coincident demand
persists above the actual threshold, shared devices may brown out and the
always-on fabric may lose service. Burst duration and the loop time constant
are not established here. The 8.9 A bound exceeds even the nominal typical
8.333 A threshold but does not prove fold-back for every part or waveform.
The declaration must expose this demand, not imply delivery in regulation.
REQ-018 still requires every rail in regulation for its stated 60 s and
start conditions; the decision cannot close that requirement or I-03.
If prototype evidence confirms fold-back, converter capacity, load placement
or an explicitly authorised operating policy needs engineering action.

The draft changes the interim typicals only for DEV; its 6.9 A peak stays
labelled stale pending the session's recorded peak decision. The integrator
must reconcile contract currents after review. No decision is claimed taken
by this worker. Remaining evidence is the concurrent mode load profile,
selected fan and NVMe, efficiency and burst-transfer bounds, and prototype
rail/contact measurements. The cable owner still needs an exact wire/crimp
specification, an AWG18/standard-header rating and a loss allocation inside
the existing 2%. No requirement, protection or limit has been lowered.

## Reproduction and correction checks

The complete tables are in [if_ab_power.out](if_ab_power.out), SHA256
`d9fa215b08b8928641a02394449d3e80ca4bdf41c894321b5a7dbdeb9156545a`.
They are not copied into this analysis. Both runtime intent inputs are pinned
to literal SHA256 values in the script and checked before parsing or output;
a mismatch returns nonzero and names the file. Maker constants remain
explicitly cited constants, not automatically extracted datasheet values.

```sh
python3 v2/docs/records/cx1/if_ab_power.py > v2/docs/records/cx1/if_ab_power.out
python3 v2/docs/records/cx1/apply_declarations_draft.py --check
python3 -c "import ast; ast.parse(open('v2/docs/records/cx1/apply_declarations_draft.py').read())"
```

The four requested correction checks and their actual outputs are recorded
in [CORRECTION.md](CORRECTION.md). The calculation writes only stdout.
No generator application, gate or verdict writer was run.
