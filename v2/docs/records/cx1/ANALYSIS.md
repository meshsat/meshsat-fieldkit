# IF-AB-POWER: I-03 source reconciliation candidate

Job `cx1-if-ab-power`, 28 September 2026. Base supplied by the launcher:
`6b419b021b48a4676b845a7390442650945089c2`. Prototype design: no V2 board has
been built, ordered or measured. This is desk calculation and AI review,
not a qualified engineering review or acceptance of I-03.

## Result and operating mode

The held evidence does not establish a typical current and a coincident peak
for every lead in the requested mode. The two known disagreements are real,
but copying either end's numbers would not reconcile them from sources.
All five mode verdicts are therefore **INCONCLUSIVE**, with the precise
missing evidence below. The numeric comparisons remain useful warnings.

The single named mode here is **PS-ALLTX-3LOADED**: CONOPS PS-ALLTX with all
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
PS-ALLTX-3LOADED demand. In particular, the PoE 0.3/0.6 A figures describe
an enabled rail, not the commanded-off rail during PA key-down. The
commanded-off settled ideal is 0 A; actual leakage, stored-charge discharge
and shutoff timing are INCONCLUSIVE. They cannot be called measured zeros.

| Rail | Declaration comparison | Verdict in PS-ALLTX-3LOADED | Exact missing basis for replacement or acceptance |
|---|---|---|---|
| +5V_S1 | A and B agree at 2.5 A typical / 5 A peak; B mixed entries sum to 4.751 A | INCONCLUSIVE | Loaded CM5 current profile, exact fan, NVMe/PCIe concurrent input currents and guaranteed converter efficiency at hot input/output corners. The active AW7915 sheet already invalidates treating the card's 1.5 A child allocation as its maximum. Conditional loaded demand is 6.228975 A against the AP64500's 5 A rating. |
| +5V_S2 | A 2.5 A typical and B 4.2 A typical DISAGREE; both 5 A peaks conflict with the conditional 5.63 A quoted in the contract | INCONCLUSIVE | A sourced or measured loaded CM5/5G/NVMe/PCIe coincidence profile, buck efficiency bounds and burst duration/input transfer response. A's typical and both peaks need reconciliation, but neither 4.2 nor 5.63 A is a verified replacement. A conditional loaded case reaches 7.281560 A. |
| +5V_S3 | A and B generic scalars agree; generic B entries also sum to 4.751 A | INCONCLUSIVE | Same compute/fan/storage evidence as slot 1 plus standby-card shutdown leakage. With the card commanded off, the conditional loaded case is 4.201346 A; the lower current does not prove a typical or a worst case. |
| +5V_DEV | A lead allocation 3.2 A and B typical 3.8 A DISAGREE; B entries sum to 5.18 A | INCONCLUSIVE | One concurrent load profile for all 19 B entries, exact LimeSDR revision/configuration, RockBLOCK input configuration, panel/camera/QMX/HDMI loads, and A's D8/host local loads. A's 4/6.9 A totals cannot simply be copied to the lead. B peak plus A child peaks gives a conditional converter demand of 8.9 A. |
| +54V_POE | A and B generic scalars agree at 0.3/0.6 A; B 0.593+0.007 A is a peak allocation | INCONCLUSIVE | Mode shutdown transient/leakage evidence and JST current rating for the actual standard B2P-VH header with AWG18. The held 7 A rating is expressly for a different, shrouded header. No numerical contact rating is inferred for the fitted combination. |

The evidence gap is an engineering finding, not a failure to create the job's
four deliverables. No declaration is lowered to obtain a favourable result.

## Held sources, revisions and quotations

Pages below are printed document pages, with PDF page numbers where different.
All PDF readings used `pdftotext -layout <file> -`. Source documents were not
modified. The complete numeric tables below identify which input is a maker
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

The read-only design sources are the two supplied intent files (hashes in the
calculation), their generator declarations, `ASSEMBLY.md` section 4, CONOPS
sections 4a and 5, REQ-018, and IF-AB-POWER. The newest EXECUTION-PLAN checkpoint
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
pairs and AWG18 for PoE. Nominal assumed copper areas are 1.31 and
0.823 mm2; assumed annealed-copper resistivity at 20 C is 1.724e-8 ohm m,
with temperature coefficient 0.00393 / C. These are explicit ideal-copper
model inputs, **not facts from a held wire maker document**. No exact wire
part, stranding, plated-conductor resistance, cut-length tolerance or
resistance-temperature specification is held for these assembled leads.
Thus actual cable voltage drop is INCONCLUSIVE; the following numbers
are conditional calculations, not certified cable bounds. The 1.25 mm2
metric size also printed in JST's AWG16 contact table would increase these
AWG16 wire-only drops by 1.31/1.25 = 1.048 at the same length/resistivity.

R(T) = rho20 * 0.300 / area_m2 * [1 + 0.00393 * (T-20)]. For AWG16 this
is 3.948092 mOhm at 20 C and 4.568732 mOhm at 60 C; for AWG18 it is
6.284326 and 7.272222 mOhm. The 60 C point is copper temperature, not
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

## One failing conditional case recomputed by hand (check b)

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
Rpair20 = 1.724e-8 * 0.300 / (1.31e-6) = 0.003948091603 ohm
Rpair60 = Rpair20 * (1 + 0.00393 * 40) = 0.004568731603 ohm
Wire drop20 = 7.281559925 * Rpair20 = 0.028748 V
Wire drop60 = 7.281559925 * Rpair60 = 0.033267 V
Initial contact maximum contribution = 7.281559925 * 4 * 0.010 = 0.291262 V
Wire60 + initial contact bound = 0.324530 V
Whole existing drop allowance = 5.1 * 0.02 = 0.102 V
Whole-budget margin at this contact bound = 0.102 - 0.324530 = -0.222530 V
```

The exact unrounded script value is 7.281560 A to six decimals. This
conditional case exceeds the earliest average-limit threshold and the
contact-drop bound exceeds even the whole rail loss budget. It does not
establish a real failure waveform: demand, efficiency and duration are
unproven. Nor does using the 8.333 A typical threshold justify a PASS.
The positive 10 A contact-current margin does not resolve voltage loss.

Two further checks of scope explain why no single copied number fixes I-03:
S1's active card at 9.1 W draws 9.1/(0.88*5.1)=2.027629 A; with 2.5 A
CM5, 1.323529 A and 0.276817 A other converter inputs, fan and gate,
the conditional total is 6.228975 A, 1.228975 A over 5 A. For DEV,
B's 6 A declared peak plus A's 2 A D8 and 0.9 A wall-port peaks is 8.9 A,
1.804290 A over the 7.095710 A earliest average-loop threshold. These
remain bounds on declared scenarios with uncertain real concurrence.

## Declaration draft and disposition

`apply_declarations_draft.py` has an **empty CHANGES list** and was not run.
No current declaration should be changed to a new numerical typical/peak
by this job: the required sources for that substitution are missing. This
does not endorse the current declarations or close I-03. The draft refuses
an empty application without writing anything. Its owner-use implementation
also checks exact old text once, unequal replacement, parses every resulting
generator with `ast`, validates all files before writes, and uses an exclusive
marker to refuse a second application if supported edits are later authored.

Simply copying B would change A S2's 2.5 to 4.2 A and A DEV's lead 3.2 to
3.8 A, requiring its parent typical total to become 4.6 A with its current
0.8 A local allocation, or 5.3 A with its own child typicals. These are
**bookkeeping alternatives, not recommended declaration replacements**.
The 4.2 A derives from 0.9 A typical CM5 plus a minimum required modem supply
capability, not the loaded mode. The DEV 3.8 A is below its own 5.18 A mixed
entries. Choosing 4.751/5.18 A raw sums as new typicals would make the same
classification error. Choosing 5.63 A as a maximum would ignore both the
CM5 allowance and other coincident child peaks.

Owners next need one load-state specification tied to the named mode,
per-load typical and upper-bound currents with durations and maker references
or prototype waveforms, and conversion-efficiency/transient bounds. Then
both generator owners can use the same lead figures while retaining A's
separate local demand. The hardware may require increased converter capacity
or redistributed loads; a declaration edit alone cannot resolve the negative
conditional margins. The cable owner needs an exact wire/crimp specification,
AWG18/standard-header rating evidence, and a shared loss allocation inside
the existing 2%. Prototype cable/contact and rail transient measurements
remain owed. No protection or requirement should be reduced to fit a budget.

## Reproduction and required checks

Run from the repository root:

```sh
python3 v2/docs/records/cx1/if_ab_power.py > v2/docs/records/cx1/if_ab_power.out
python3 -c "import ast; ast.parse(open('v2/docs/records/cx1/apply_declarations_draft.py').read())"
```

Checks run on this candidate: (a) PASS, script exit 0 and a second run matched
the 27,262-byte output exactly, SHA256
`e4a0397a63082be4802c20e6b1fce3314110bc3966d9deb8b9805fa3c82e1092`;
(b) PASS, AI review of the displayed hand arithmetic, independently checked
with Python Decimal arithmetic; (c) PASS, the exact AST command above exited
0. The draft itself was not executed. Both Python files parsed, all four
deliverables existed, and the reproduced tables matched the saved output.

The calculation reads both intents and writes only stdout. It uses only the
Python standard library. No generator, gate or verdict writer was run. The
final job result records the actual reproducibility and AST check outcomes.
The hand arithmetic above is check (b), labelled AI review. The following
tables reproduce `if_ab_power.out`, including every B load entry, converter
and contact current margins, and both-conductor voltage drops for each
declared typical/peak and the conditional loaded stresses. The source notes'
word "measured" is quoted from historical intents and describes their desk
layout calculations; it is not evidence of a physical V2 measurement.

<!-- BEGIN REPRODUCED CALCULATION -->

# IF-AB-POWER calculation: prototype, AI review arithmetic
Mode: PS-ALLTX-3LOADED, REQ-018 / CONOPS section 5. Three CM5s loaded; standby WiFi in S3, PoE, USB-C outlet and heater off.

No sourced typical or guaranteed coincident peak is established. Generic declarations and conditional stresses follow; they are not alternate operating modes.

Input v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json: sha256 3422910a15c4d1450141aa9a5fd725ba75bca9fcb42ae8c87e4cf3385d7d4498
Input v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json: sha256 96ee391b3e3f638d7436cad51fcabf77999b530d8734c1feb93f7766a4877d8a

| Rail | AWG | Pair length m | Pair R20 ohm | Pair R60 ohm | Contact rating |
|---|---|---|---|---|---|
| +5V_S1 | 16 | 0.300 | 0.003948092 | 0.004568732 | 10 A, standard/AWG16 |
| +5V_S2 | 16 | 0.300 | 0.003948092 | 0.004568732 | 10 A, standard/AWG16 |
| +5V_S3 | 16 | 0.300 | 0.003948092 | 0.004568732 | 10 A, standard/AWG16 |
| +5V_DEV | 16 | 0.300 | 0.003948092 | 0.004568732 | 10 A, standard/AWG16 |
| +54V_POE | 18 | 0.300 | 0.006284326 | 0.007272222 | INCONCLUSIVE: 7 A quoted only for shrouded/AWG18 |

## +5V_S1

| End | V | Typical A | Peak A | Source | Raw load sum A | Loads |
|---|---|---|---|---|---|---|
| A converter | 5.1 | 2.5 | 5.0 | R31 | 5.000000 | {"J_5V_S1": 5.0} |
| B lead | 5.1 | 2.5 | 5.0 | J_5V_S1 | 4.751000 | {"J_FAN1": 0.1, "U103": 2.2, "U104": 0.7, "U105": 0.15, "U116": 0.001, "U30A": 1.6} |

A note: one CM5 slot with its cooler fan; 5 A peak at the module; the rail net starts at the INA226 shunt. This board's share of the 2 percent is 0.5 point, measured 0.07

B note: slot rail from A22 (JST-VH): the module, the two 3.3 V bucks, the 1.0 V switch core and the fan. THIS BOARD'S SHARE is 1.5 of the rail's 2 percent (16 September 2026): board A regulates it and measures 0.07 percent from its shunt to the header, and the long copper is this side, from the VH header across the board to a module receptacle carrying 2.5 A

B raw sum minus B typical = +2.251000 A; raw sum minus B peak = -0.249000 A. Mixed allocations, not a sourced operating total.

| B load | Function | A | Typical or peak? | Basis and uncertainty |
|---|---|---|---|---|
| U30A | CM5 | 1.600000 | estimate, neither sourced typical nor peak | CM5 Table 9: 0.9 A typical; B.3: 2.5 A design allowance; 1.6 A is generator headroom |
| U103 | card buck input | 2.200000 | capacity-derived estimate, not typical | generator applies 2.2 A to every slot; S2 is now 3.456 V; Q11 minimum supply 3/4 A; W1 applies to S1/S3 |
| U104 | NVMe and PCIe 3.3 V buck | 0.700000 | typical allocation, unverified | generator; child +3V3_SxB declares 0.9/1.8 A; selected SSD/workload and efficiency not established |
| U105 | PCIe 1.0 V buck | 0.150000 | typical allocation, unverified | generator; child +1V0_Sx declares 0.8/1.2 A; efficiency is an assumption |
| J_FAN1 | cooler fan | 0.100000 | estimate, typical/peak unspecified | generator; IF-CM5-FAN current is TBD with exact fan part |
| U116 | card enable gate | 0.001000 | design allowance, not typical/peak | generator 1 mA; TI SCLS739F p.6 ICC maximum 10 uA, switching current extra |

Converter U4 AP64500: rated continuous output 5.000000 A (D1 p.1), not its switch-current threshold.

Reconstruction uses child intent V, I and efficiency. Efficiency is an unverified assumption; the resulting stress is a CONDITIONAL BOUND, not a guaranteed upper bound.

| Case (conditional unless declaration) | Lead A | Converter A | Converter margin A (%) | Contact margin A (%) | Pair drop 20 C V | Pair drop 60 C V | Unused WHOLE 2% budget 20/60 C V |
|---|---|---|---|---|---|---|---|
| A declared typical | 2.500000 | 2.500000 | +2.500000 (+50.00%) | +7.500000 (+75.00%) | 0.009870 | 0.011422 | +0.092130 / +0.090578 |
| A declared peak | 5.000000 | 5.000000 | +0.000000 (+0.00%) | +5.000000 (+50.00%) | 0.019740 | 0.022844 | +0.082260 / +0.079156 |
| B declared typical | 2.500000 | 2.500000 | +2.500000 (+50.00%) | +7.500000 (+75.00%) | 0.009870 | 0.011422 | +0.092130 / +0.090578 |
| B declared peak | 5.000000 | 5.000000 | +0.000000 (+0.00%) | +5.000000 (+50.00%) | 0.019740 | 0.022844 | +0.082260 / +0.079156 |
| B mixed raw load sum | 4.751000 | 4.751000 | +0.249000 (+4.98%) | +5.249000 (+52.49%) | 0.018757 | 0.021706 | +0.083243 / +0.080294 |
| Sourced/intent planning mix, NOT typical | 3.407024 | 3.407024 | +1.592976 (+31.86%) | +6.592976 (+65.93%) | 0.013451 | 0.015566 | +0.088549 / +0.086434 |
| CM5 design + child peaks conditional BOUND | 6.228975 | 6.228975 | -1.228975 (-24.58%) | +3.771025 (+37.71%) | 0.024593 | 0.028459 | +0.077407 / +0.073541 |

| Case | Wire + initial contact MAX bound, 20/60 C V | Wire + after-test contact MAX bound, 20/60 C V | Whole-budget margin at 60 C, initial/after V |
|---|---|---|---|
| A declared typical | 0.109870 / 0.111422 | 0.209870 / 0.211422 | -0.009422 / -0.109422 |
| A declared peak | 0.219740 / 0.222844 | 0.419740 / 0.422844 | -0.120844 / -0.320844 |
| B declared typical | 0.109870 / 0.111422 | 0.209870 / 0.211422 | -0.009422 / -0.109422 |
| B declared peak | 0.219740 / 0.222844 | 0.419740 / 0.422844 | -0.120844 / -0.320844 |
| B mixed raw load sum | 0.208797 / 0.211746 | 0.398837 / 0.401786 | -0.109746 / -0.299786 |
| Sourced/intent planning mix, NOT typical | 0.149732 / 0.151847 | 0.286013 / 0.288128 | -0.049847 / -0.186128 |
| CM5 design + child peaks conditional BOUND | 0.273752 / 0.277618 | 0.522911 / 0.526777 | -0.175618 / -0.424777 |

Contact bounds apply the catalogue maximum to four mated contacts, without a further temperature correction not stated by JST. Crimp/wire tolerances and board drops are additional or uncharacterised. These are conditional resistance bounds, not measured drops.

Verdict: INCONCLUSIVE mode current. A/B scalar declarations AGREE, but neither the raw allocations nor conditional stress validate those scalars.

## +5V_S2

| End | V | Typical A | Peak A | Source | Raw load sum A | Loads |
|---|---|---|---|---|---|---|
| A converter | 5.1 | 2.5 | 5.0 | R35 | 5.000000 | {"J_5V_S2": 5.0} |
| B lead | 5.1 | 4.2 | 5.0 | J_5V_S2 | 4.751000 | {"J_FAN2": 0.1, "U203": 2.2, "U204": 0.7, "U205": 0.15, "U216": 0.001, "U31A": 1.6} |

A note: one CM5 slot with its cooler fan; 5 A peak at the module; the rail net starts at the INA226 shunt. This board's share of the 2 percent is 0.5 point, measured 0.07

B note: slot rail from A22 (JST-VH): the module, the two 3.3 V bucks, the 1.0 V switch core and the fan. THIS BOARD'S SHARE is 1.5 of the rail's 2 percent (16 September 2026): board A regulates it and measures 0.07 percent from its shunt to the header, and the long copper is this side, from the VH header across the board to a module receptacle carrying 2.5 A

B raw sum minus B typical = +0.551000 A; raw sum minus B peak = -0.249000 A. Mixed allocations, not a sourced operating total.

| B load | Function | A | Typical or peak? | Basis and uncertainty |
|---|---|---|---|---|
| U31A | CM5 | 1.600000 | estimate, neither sourced typical nor peak | CM5 Table 9: 0.9 A typical; B.3: 2.5 A design allowance; 1.6 A is generator headroom |
| U203 | card buck input | 2.200000 | capacity-derived estimate, not typical | generator applies 2.2 A to every slot; S2 is now 3.456 V; Q11 minimum supply 3/4 A; W1 applies to S1/S3 |
| U204 | NVMe and PCIe 3.3 V buck | 0.700000 | typical allocation, unverified | generator; child +3V3_SxB declares 0.9/1.8 A; selected SSD/workload and efficiency not established |
| U205 | PCIe 1.0 V buck | 0.150000 | typical allocation, unverified | generator; child +1V0_Sx declares 0.8/1.2 A; efficiency is an assumption |
| J_FAN2 | cooler fan | 0.100000 | estimate, typical/peak unspecified | generator; IF-CM5-FAN current is TBD with exact fan part |
| U216 | card enable gate | 0.001000 | design allowance, not typical/peak | generator 1 mA; TI SCLS739F p.6 ICC maximum 10 uA, switching current extra |

Converter U5 LM5176: shunt R35 = 0.006000 ohm +/-1%; nominal-R VSNS limits = 7.166667/8.333333/9.500000 A (min/typ/max).
Including initial shunt tolerance: 7.095710 to 9.595960 A. This is average-loop onset, not a guaranteed stage rating or instantaneous clamp.

Reproduce old S2 coincidence: 1.6 + 3.080213904 + 0.846309112 + 0.100000 = 5.626523016 A; with gate 5.627523016 A.

Reconstruction uses child intent V, I and efficiency. Efficiency is an unverified assumption; the resulting stress is a CONDITIONAL BOUND, not a guaranteed upper bound.

| Case (conditional unless declaration) | Lead A | Converter A | Converter margin A (%) | Contact margin A (%) | Pair drop 20 C V | Pair drop 60 C V | Unused WHOLE 2% budget 20/60 C V |
|---|---|---|---|---|---|---|---|
| A declared typical | 2.500000 | 2.500000 | +4.595710 (+64.77%) | +7.500000 (+75.00%) | 0.009870 | 0.011422 | +0.092130 / +0.090578 |
| A declared peak | 5.000000 | 5.000000 | +2.095710 (+29.53%) | +5.000000 (+50.00%) | 0.019740 | 0.022844 | +0.082260 / +0.079156 |
| B declared typical | 4.200000 | 4.200000 | +2.895710 (+40.81%) | +5.800000 (+58.00%) | 0.016582 | 0.019189 | +0.085418 / +0.082811 |
| B declared peak | 5.000000 | 5.000000 | +2.095710 (+29.53%) | +5.000000 (+50.00%) | 0.019740 | 0.022844 | +0.082260 / +0.079156 |
| B mixed raw load sum | 4.751000 | 4.751000 | +2.344710 (+33.04%) | +5.249000 (+52.49%) | 0.018757 | 0.021706 | +0.083243 / +0.080294 |
| Sourced/intent planning mix, NOT typical | 4.157470 | 4.157470 | +2.938240 (+41.41%) | +5.842530 (+58.43%) | 0.016414 | 0.018994 | +0.085586 / +0.083006 |
| CM5 design + child peaks conditional BOUND | 7.281560 | 7.281560 | -0.185850 (-2.62%) | +2.718440 (+27.18%) | 0.028748 | 0.033267 | +0.073252 / +0.068733 |
| Contract quoted 5.63 A conditional | 5.630000 | 5.630000 | +1.465710 (+20.66%) | +4.370000 (+43.70%) | 0.022228 | 0.025722 | +0.079772 / +0.076278 |
| CM5 design + 5G peak + other typical | 6.527523 | 6.527523 | +0.568187 (+8.01%) | +3.472477 (+34.72%) | 0.025771 | 0.029823 | +0.076229 / +0.072177 |

| Case | Wire + initial contact MAX bound, 20/60 C V | Wire + after-test contact MAX bound, 20/60 C V | Whole-budget margin at 60 C, initial/after V |
|---|---|---|---|
| A declared typical | 0.109870 / 0.111422 | 0.209870 / 0.211422 | -0.009422 / -0.109422 |
| A declared peak | 0.219740 / 0.222844 | 0.419740 / 0.422844 | -0.120844 / -0.320844 |
| B declared typical | 0.184582 / 0.187189 | 0.352582 / 0.355189 | -0.085189 / -0.253189 |
| B declared peak | 0.219740 / 0.222844 | 0.419740 / 0.422844 | -0.120844 / -0.320844 |
| B mixed raw load sum | 0.208797 / 0.211746 | 0.398837 / 0.401786 | -0.109746 / -0.299786 |
| Sourced/intent planning mix, NOT typical | 0.182713 / 0.185293 | 0.349012 / 0.351592 | -0.083293 / -0.249592 |
| CM5 design + child peaks conditional BOUND | 0.320011 / 0.324530 | 0.611273 / 0.615792 | -0.222530 / -0.513792 |
| Contract quoted 5.63 A conditional | 0.247428 / 0.250922 | 0.472628 / 0.476122 | -0.148922 / -0.374122 |
| CM5 design + 5G peak + other typical | 0.286872 / 0.290923 | 0.547973 / 0.552024 | -0.188923 / -0.450024 |

Contact bounds apply the catalogue maximum to four mated contacts, without a further temperature correction not stated by JST. Crimp/wire tolerances and board drops are additional or uncharacterised. These are conditional resistance bounds, not measured drops.

Verdict: INCONCLUSIVE replacement figures; definite A/B DISAGREEMENT remains. No verified typical or simultaneous peak may be selected from these mixed estimates.

## +5V_S3

| End | V | Typical A | Peak A | Source | Raw load sum A | Loads |
|---|---|---|---|---|---|---|
| A converter | 5.1 | 2.5 | 5.0 | R39 | 5.000000 | {"J_5V_S3": 5.0} |
| B lead | 5.1 | 2.5 | 5.0 | J_5V_S3 | 4.751000 | {"J_FAN3": 0.1, "U303": 2.2, "U304": 0.7, "U305": 0.15, "U316": 0.001, "U32A": 1.6} |

A note: one CM5 slot with its cooler fan; 5 A peak at the module; the rail net starts at the INA226 shunt. This board's share of the 2 percent is 0.5 point, measured 0.07

B note: slot rail from A22 (JST-VH): the module, the two 3.3 V bucks, the 1.0 V switch core and the fan. THIS BOARD'S SHARE is 1.5 of the rail's 2 percent (16 September 2026): board A regulates it and measures 0.07 percent from its shunt to the header, and the long copper is this side, from the VH header across the board to a module receptacle carrying 2.5 A

B raw sum minus B typical = +2.251000 A; raw sum minus B peak = -0.249000 A. Mixed allocations, not a sourced operating total.

| B load | Function | A | Typical or peak? | Basis and uncertainty |
|---|---|---|---|---|
| U32A | CM5 | 1.600000 | estimate, neither sourced typical nor peak | CM5 Table 9: 0.9 A typical; B.3: 2.5 A design allowance; 1.6 A is generator headroom |
| U303 | card buck input | 2.200000 | capacity-derived estimate, not typical | generator applies 2.2 A to every slot; S2 is now 3.456 V; Q11 minimum supply 3/4 A; W1 applies to S1/S3 |
| U304 | NVMe and PCIe 3.3 V buck | 0.700000 | typical allocation, unverified | generator; child +3V3_SxB declares 0.9/1.8 A; selected SSD/workload and efficiency not established |
| U305 | PCIe 1.0 V buck | 0.150000 | typical allocation, unverified | generator; child +1V0_Sx declares 0.8/1.2 A; efficiency is an assumption |
| J_FAN3 | cooler fan | 0.100000 | estimate, typical/peak unspecified | generator; IF-CM5-FAN current is TBD with exact fan part |
| U316 | card enable gate | 0.001000 | design allowance, not typical/peak | generator 1 mA; TI SCLS739F p.6 ICC maximum 10 uA, switching current extra |

Converter U6 AP64500: rated continuous output 5.000000 A (D1 p.1), not its switch-current threshold.

Reconstruction uses child intent V, I and efficiency. Efficiency is an unverified assumption; the resulting stress is a CONDITIONAL BOUND, not a guaranteed upper bound.

| Case (conditional unless declaration) | Lead A | Converter A | Converter margin A (%) | Contact margin A (%) | Pair drop 20 C V | Pair drop 60 C V | Unused WHOLE 2% budget 20/60 C V |
|---|---|---|---|---|---|---|---|
| A declared typical | 2.500000 | 2.500000 | +2.500000 (+50.00%) | +7.500000 (+75.00%) | 0.009870 | 0.011422 | +0.092130 / +0.090578 |
| A declared peak | 5.000000 | 5.000000 | +0.000000 (+0.00%) | +5.000000 (+50.00%) | 0.019740 | 0.022844 | +0.082260 / +0.079156 |
| B declared typical | 2.500000 | 2.500000 | +2.500000 (+50.00%) | +7.500000 (+75.00%) | 0.009870 | 0.011422 | +0.092130 / +0.090578 |
| B declared peak | 5.000000 | 5.000000 | +0.000000 (+0.00%) | +5.000000 (+50.00%) | 0.019740 | 0.022844 | +0.082260 / +0.079156 |
| B mixed raw load sum | 4.751000 | 4.751000 | +0.249000 (+4.98%) | +5.249000 (+52.49%) | 0.018757 | 0.021706 | +0.083243 / +0.080294 |
| Sourced/intent planning mix, NOT typical | 1.847309 | 1.847309 | +3.152691 (+63.05%) | +8.152691 (+81.53%) | 0.007293 | 0.008440 | +0.094707 / +0.093560 |
| CM5 design + child peaks conditional BOUND | 4.201346 | 4.201346 | +0.798654 (+15.97%) | +5.798654 (+57.99%) | 0.016587 | 0.019195 | +0.085413 / +0.082805 |

| Case | Wire + initial contact MAX bound, 20/60 C V | Wire + after-test contact MAX bound, 20/60 C V | Whole-budget margin at 60 C, initial/after V |
|---|---|---|---|
| A declared typical | 0.109870 / 0.111422 | 0.209870 / 0.211422 | -0.009422 / -0.109422 |
| A declared peak | 0.219740 / 0.222844 | 0.419740 / 0.422844 | -0.120844 / -0.320844 |
| B declared typical | 0.109870 / 0.111422 | 0.209870 / 0.211422 | -0.009422 / -0.109422 |
| B declared peak | 0.219740 / 0.222844 | 0.419740 / 0.422844 | -0.120844 / -0.320844 |
| B mixed raw load sum | 0.208797 / 0.211746 | 0.398837 / 0.401786 | -0.109746 / -0.299786 |
| Sourced/intent planning mix, NOT typical | 0.081186 / 0.082332 | 0.155078 / 0.156225 | +0.019668 / -0.054225 |
| CM5 design + child peaks conditional BOUND | 0.184641 / 0.187249 | 0.352695 / 0.355303 | -0.085249 / -0.253303 |

Contact bounds apply the catalogue maximum to four mated contacts, without a further temperature correction not stated by JST. Crimp/wire tolerances and board drops are additional or uncharacterised. These are conditional resistance bounds, not measured drops.

Verdict: INCONCLUSIVE mode current. A/B scalar declarations AGREE, but neither the raw allocations nor conditional stress validate those scalars.

## +5V_DEV

| End | V | Typical A | Peak A | Source | Raw load sum A | Loads |
|---|---|---|---|---|---|---|
| A converter | 5.0 | 4.0 | 6.9 | R43 | 4.000000 | {"J_5V_DEV": 3.2, "U23": 0.5, "U32": 0.3} |
| B lead | 5.0 | 3.8 | 6.0 | J_5V_DEV | 5.180000 | {"F1": 0.6, "F2": 0.2, "F3": 0.3, "U106": 0.1, "U15": 0.02, "U16": 0.02, "U17": 0.02, "U18": 0.02, "U206": 0.1, "U21": 0.6, "U23": 1.2, "U24": 0.45, "U25": 0.9, "U26": 0.15, "U28": 0.25, "U306": 0.1, "U40": 0.05, "U50": 0.05, "U60": 0.05} |

A note: the USB devices, the LimeSDR bay and the RockBLOCK behind their switches, the D8 mezzanine behind U23 and the wall host port behind U32; the net starts at the ISNS shunt R43. 9 September 2026 (ARCH-PCB-B-IOHA): +0.8 A because B16's three hub banks had to leave the slot rails. 26 September 2026 (F-PR-04, D-12): the converter is an LM5176 stage with a 7.2 A minimum average limit, and the Glenair port's 0.9 A takes the peak to 6.9 A.

B note: the device rail from A22; +0.8 A since the three hubs and their cores moved off the slot rails (ARCH-PCB-B-IOHA)

B raw sum minus B typical = +1.380000 A; raw sum minus B peak = -0.820000 A. Mixed allocations, not a sourced operating total.

| B load | Function | A | Typical or peak? | Basis and uncertainty |
|---|---|---|---|---|
| U23 | LimeSDR eFuse | 1.200000 | typical estimate, unverified | generator 1.2 A; held Mini 2.0 pages say 4.5 W / 5 V 900 mA; exact 2.4 configuration not established |
| U25 | shared 3.3 V buck | 0.900000 | typical allocation, assumed efficiency | 0.9 A matches child 1.2 A at 3.3 V with 0.88 efficiency; generator's 1.4 A comment is stale |
| U21 | LoRa switch | 0.600000 | transmit estimate, not maker peak | E22 v1.20 p.2 (PDF p.3) gives 0.650 A typical instantaneous TX, not 0.600 A |
| F1 | panel feed | 0.600000 | typical allocation, unverified | generator cites board C declaration; not a maker load or loaded-panel measurement |
| U24 | RockBLOCK eFuse | 0.450000 | burst estimate, not proven peak | held Ground Control input documentation: default charge limit about 0.460 A, input maximum 0.500 A; configurable 0.800 A |
| F3 | QMX USB VBUS | 0.300000 | allocation, typical/peak unspecified | generator only; HF main DC supply is separate; USB sink draw not established |
| U28 | camera switch | 0.250000 | typical estimate, unverified | child intent 0.250 A typical / 0.500 A port allocation; exact camera absent |
| F2 | HDMI VBUS | 0.200000 | allocation, neither child typical nor peak | generator comment wrongly names display switches; child +5V_HDMI declares 0.100/0.500 A at J_HDMI |
| U26 | KSZ 1.2 V buck | 0.150000 | typical allocation, unverified | child 0.500 A typical output, 0.85 assumed efficiency; not a measured input current |
| U106 | hub 1.1 V buck | 0.100000 | typical allocation, unverified | child 0.400 A typical / 0.700 A peak; 0.85 efficiency assumption |
| U206 | hub 1.1 V buck | 0.100000 | typical allocation, unverified | child 0.400 A typical / 0.700 A peak; 0.85 efficiency assumption |
| U306 | hub 1.1 V buck | 0.100000 | typical allocation, unverified | child 0.400 A typical / 0.700 A peak; 0.85 efficiency assumption |
| U40 | supervisor private LDO | 0.050000 | typical allocation, inconsistent | child +3V3_IOCx declares 0.120/0.250 A; LDO input current approximately output plus bias, not 0.050 A |
| U50 | supervisor private LDO | 0.050000 | typical allocation, inconsistent | child +3V3_IOCx declares 0.120/0.250 A; LDO input current approximately output plus bias, not 0.050 A |
| U60 | supervisor private LDO | 0.050000 | typical allocation, inconsistent | child +3V3_IOCx declares 0.120/0.250 A; LDO input current approximately output plus bias, not 0.050 A |
| U15 | CP2102N bridge | 0.020000 | design allocation, not maker typical/peak | Silicon Labs rev.1.5 p.10: 9.5/13.7 mA typical at 115200 baud/3 Mbaud; no max; generator allocates 20 mA |
| U16 | CP2102N bridge | 0.020000 | design allocation, not maker typical/peak | Silicon Labs rev.1.5 p.10: 9.5/13.7 mA typical at 115200 baud/3 Mbaud; no max; generator allocates 20 mA |
| U17 | CP2102N bridge | 0.020000 | design allocation, not maker typical/peak | Silicon Labs rev.1.5 p.10: 9.5/13.7 mA typical at 115200 baud/3 Mbaud; no max; generator allocates 20 mA |
| U18 | CP2102N bridge | 0.020000 | design allocation, not maker typical/peak | Silicon Labs rev.1.5 p.10: 9.5/13.7 mA typical at 115200 baud/3 Mbaud; no max; generator allocates 20 mA |

Converter U7 LM5176: shunt R43 = 0.006000 ohm +/-1%; nominal-R VSNS limits = 7.166667/8.333333/9.500000 A (min/typ/max).
Including initial shunt tolerance: 7.095710 to 9.595960 A. This is average-loop onset, not a guaranteed stage rating or instantaneous clamp.

A converter declared peak alone = 6.900000 A; onset margin +0.195710 (+2.76%); no per-lead peak apportioned by A.

| Case (conditional unless declaration) | Lead A | Converter A | Converter margin A (%) | Contact margin A (%) | Pair drop 20 C V | Pair drop 60 C V | Unused WHOLE 2% budget 20/60 C V |
|---|---|---|---|---|---|---|---|
| A J_5V_DEV allocation, local allocations | 3.200000 | 4.000000 | +3.095710 (+43.63%) | +6.800000 (+68.00%) | 0.012634 | 0.014620 | +0.087366 / +0.085380 |
| B declared typical + A local allocations | 3.800000 | 4.600000 | +2.495710 (+35.17%) | +6.200000 (+62.00%) | 0.015003 | 0.017361 | +0.084997 / +0.082639 |
| B raw loads + A local allocations | 5.180000 | 5.980000 | +1.115710 (+15.72%) | +4.820000 (+48.20%) | 0.020451 | 0.023666 | +0.079549 / +0.076334 |
| B declared typical + A child typical | 3.800000 | 5.300000 | +1.795710 (+25.31%) | +6.200000 (+62.00%) | 0.015003 | 0.017361 | +0.084997 / +0.082639 |
| B declared peak + A child peak BOUND | 6.000000 | 8.900000 | -1.804290 (-25.43%) | +4.000000 (+40.00%) | 0.023689 | 0.027412 | +0.076311 / +0.072588 |

| Case | Wire + initial contact MAX bound, 20/60 C V | Wire + after-test contact MAX bound, 20/60 C V | Whole-budget margin at 60 C, initial/after V |
|---|---|---|---|
| A J_5V_DEV allocation, local allocations | 0.140634 / 0.142620 | 0.268634 / 0.270620 | -0.042620 / -0.170620 |
| B declared typical + A local allocations | 0.167003 / 0.169361 | 0.319003 / 0.321361 | -0.069361 / -0.221361 |
| B raw loads + A local allocations | 0.227651 / 0.230866 | 0.434851 / 0.438066 | -0.130866 / -0.338066 |
| B declared typical + A child typical | 0.167003 / 0.169361 | 0.319003 / 0.321361 | -0.069361 / -0.221361 |
| B declared peak + A child peak BOUND | 0.263689 / 0.267412 | 0.503689 / 0.507412 | -0.167412 / -0.407412 |

Contact bounds apply the catalogue maximum to four mated contacts, without a further temperature correction not stated by JST. Crimp/wire tolerances and board drops are additional or uncharacterised. These are conditional resistance bounds, not measured drops.

Verdict: INCONCLUSIVE replacement figures; definite A/B DISAGREEMENT remains. No verified typical or simultaneous peak may be selected from these mixed estimates.

## +54V_POE

| End | V | Typical A | Peak A | Source | Raw load sum A | Loads |
|---|---|---|---|---|---|---|
| A converter | 54.0 | 0.3 | 0.6 | R71 | 0.300000 | {"J_54V": 0.3} |
| B lead | 54.0 | 0.3 | 0.6 | J_54V | 0.600000 | {"R13": 0.593, "U5": 0.007} |

A note: the TPS23861 PSE on B16; U16's EN/UVLO is POE_UVLO, 0.6 of the interlock gate's output POE_EN since 27 September 2026 (it sat on POE_EN itself behind a 62 k with both pins on that net)

B note: the Power over Ethernet feed arriving from board A's own +54V_POE stage: the port current through R13 to POE_P and the TPS23861 injector U5's own VPWR supply (at most 7 mA). It is a rail of board A and a load of this one

B raw sum minus B typical = +0.300000 A; raw sum minus B peak = +0.000000 A. Mixed allocations, not a sourced operating total.

| B load | Function | A | Typical or peak? | Basis and uncertainty |
|---|---|---|---|---|
| R13 | PoE port | 0.593000 | peak residual allocation, not maker figure | generator: 0.600 A total minus 0.007 A controller; disabled in named mode |
| U5 | TPS23861 VPWR | 0.007000 | maximum at stated test condition | TI SLUSBX9I p.7: 0.007 A max at 57 V; not a typical at 54 V; mode supply disabled |

Converter U16 LM5176: shunt R71 = 0.020000 ohm +/-1%; nominal-R VSNS limits = 2.150000/2.500000/2.850000 A (min/typ/max).
Including initial shunt tolerance: 2.128713 to 2.878788 A. This is average-loop onset, not a guaranteed stage rating or instantaneous clamp.

| Case (conditional unless declaration) | Lead A | Converter A | Converter margin A (%) | Contact margin A (%) | Pair drop 20 C V | Pair drop 60 C V | Unused WHOLE 2% budget 20/60 C V |
|---|---|---|---|---|---|---|---|
| A declared typical | 0.300000 | 0.300000 | +1.828713 (+85.91%) | INCONCLUSIVE (7 A is other header) | 0.001885 | 0.002182 | +1.078115 / +1.077818 |
| A declared peak | 0.600000 | 0.600000 | +1.528713 (+71.81%) | INCONCLUSIVE (7 A is other header) | 0.003771 | 0.004363 | +1.076229 / +1.075637 |
| B declared typical | 0.300000 | 0.300000 | +1.828713 (+85.91%) | INCONCLUSIVE (7 A is other header) | 0.001885 | 0.002182 | +1.078115 / +1.077818 |
| B declared peak | 0.600000 | 0.600000 | +1.528713 (+71.81%) | INCONCLUSIVE (7 A is other header) | 0.003771 | 0.004363 | +1.076229 / +1.075637 |
| B mixed raw load sum | 0.600000 | 0.600000 | +1.528713 (+71.81%) | INCONCLUSIVE (7 A is other header) | 0.003771 | 0.004363 | +1.076229 / +1.075637 |
| Named mode commanded OFF, ideal settled | 0.000000 | 0.000000 | +2.128713 (+100.00%) | INCONCLUSIVE (7 A is other header) | 0.000000 | 0.000000 | +1.080000 / +1.080000 |

| Case | Wire + initial contact MAX bound, 20/60 C V | Wire + after-test contact MAX bound, 20/60 C V | Whole-budget margin at 60 C, initial/after V |
|---|---|---|---|
| A declared typical | 0.013885 / 0.014182 | 0.025885 / 0.026182 | +1.065818 / +1.053818 |
| A declared peak | 0.027771 / 0.028363 | 0.051771 / 0.052363 | +1.051637 / +1.027637 |
| B declared typical | 0.013885 / 0.014182 | 0.025885 / 0.026182 | +1.065818 / +1.053818 |
| B declared peak | 0.027771 / 0.028363 | 0.051771 / 0.052363 | +1.051637 / +1.027637 |
| B mixed raw load sum | 0.027771 / 0.028363 | 0.051771 / 0.052363 | +1.051637 / +1.027637 |
| Named mode commanded OFF, ideal settled | 0.000000 / 0.000000 | 0.000000 / 0.000000 | +1.080000 / +1.080000 |

Contact bounds apply the catalogue maximum to four mated contacts, without a further temperature correction not stated by JST. Crimp/wire tolerances and board drops are additional or uncharacterised. These are conditional resistance bounds, not measured drops.

Verdict: INCONCLUSIVE for a sourced mode current/contact margin. Generic A/B declarations AGREE; mode demands outlet OFF, actual leakage/discharge needs evidence.

All current margins are limit minus current; positive is arithmetic headroom only. Negative conditional margins flag unresolved regulation risk. The 2% voltage column is the entire existing budget, NOT a new allowance for the cable; A/B shares already sum to 2%. No requirement, protection or declaration was changed.
