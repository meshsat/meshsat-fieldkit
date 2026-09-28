# Correction cx1-if-ab-power-c1

28 September 2026. Launcher base `6e149d4660b3598af77f1f4b97f72d74ace0528c`.
Prototype design: no V2 board has been built, ordered or measured. Desk
arithmetic and AI review, not qualified review or closure of I-03.
`checks/check-1-RESULT.md` was read first, in full, then the comparison and
blind reproduction. All requested items are accepted. Mode figures remain
INCONCLUSIVE. All edits are under `v2/docs/records/cx1/`.

## B1. Interim +5V_S2 alignment

Changed `apply_declarations_draft.py` to carry real, unexecuted entries.
The header and notes beside them say INTERIM and mode INCONCLUSIVE, retaining
the 7.28 A all-peak conditional bound against the 7.10 to 7.17 A loop minimum.
One conductor needs a common declaration even while its mode current is unknown.

| Target as held | Old A | New A | Basis |
|---|---:|---:|---|
| A slot-2 typical, `gen_sch_a.py:111` | 2.5 | 4.2 | 4.157470 A mix below, rounded to one decimal |
| A slot-2 peak, same call | 5.0 | 5.63 | 5.627523 A coincidence below, rounded to two decimals |
| A `J_5V_S2`, same call | 5.0 | 5.63 | Same conductor and coincidence |
| A VBAT `Q28`, `gen_sch_a.py:48` | 2.0 | 2.22 | 5.63*5.1/(0.90*14.4) = 2.215509 A |
| B slot-2 peak, `gen_sch_b.py:79` | 5.0 | 5.63 | B's own comment and the reconstruction below |

A uses string `_n == "2"`; B uses integer `_n == 2`. Slots 1 and 3 retain
their declarations. Q28 is the buck-side high FET, not a controller bias pin.
Its allocation uses A's nominal 14.4 V and assumed 0.90 efficiency
(`gen_sch_a.py:47,112`); 2.22 A is not a low-battery bound.

Held maker basis: CM5 release 3, build 08/06/2026,
`v2/vendor/cm5/cm5-datasheet.pdf`, PDF p.16 section 3.3 and pp.27-28 Table 9:
0.9 A typical, no maximum. Quectel RM520N-GL Hardware Design v1.0,
`v2/vendor/quectel/quectel-rm520n-gl-hardware-design-v1.0.pdf`, PDF p.28
(printed p.27): at least 3 A continuous supply capability. RM520N Series
Hardware Design v1.1, `v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf`,
PDF p.30 (printed p.29): at least 4 A peak supply capability. Neither
Quectel figure is a measured consumption maximum. Board B sets 3.456 V
and assumes efficiency 0.88 (`gen_sch_b.py:169-170`). Its other child rails
declare 0.9/1.8 A at 3.3 V, efficiency 0.88, and 0.8/1.2 A at 1.0 V,
efficiency 0.85 (`:182-188`). The 1.6 A CM5, 0.1 A fan and 0.001 A gate
are project allocations (`:48-53`).

```text
Other typical inputs = 0.9*3.3/(0.88*5.1) + 0.8/(0.85*5.1) = 0.846309112 A
S2 mix = 0.9 + 3*3.456/(0.88*5.1) + 0.846309112 + 0.101
       = 4.157469540 A -> 4.2 A
S2 coincidence = 1.6 + 4*3.456/(0.88*5.1) + 0.846309112 + 0.101
               = 5.627523016 A -> 5.63 A
Q28 allocation = 5.63*5.1/(0.90*14.4) = 2.215509259 A -> 2.22 A
All-peak conditional bound = 2.5 + 4*3.456/(0.88*5.1)
                          + 1.8*3.3/(0.88*5.1) + 1.2/(0.85*5.1) + 0.101
                          = 7.281560 A
Loop minimum, nominal shunt = 0.043/0.006 = 7.166667 A
Loop minimum, +1% shunt = 0.043/0.00606 = 7.095710 A
```

The 2.5 A CM5 supply-design allowance is release 3 B.3, PDF p.36. The loop
figures are TI LM5176 SNVSAI1D (August 2021),
`v2/vendor/ti/lm5176-datasheet.pdf`, p.7 VSNS and p.17 section 7.3.6.
The 1% initial tolerance is Vishay 30100 (23-Nov-2023),
`v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf`, p.1, F code.
Every requested checker figure reproduces; none is rejected.

## B2. +5V_DEV coincidence and lead alignment

Changed the draft's A J_5V_DEV from 3.2 to 3.8 A, following B's typical
(`gen_sch_b.py:97`), and its converter typical from 4.0 to 5.1 A:
3.8 + D8 1.0 + wall 0.3. D8's 1.0 A is declared at both ends
(`gen_sch_a.py:169`, `gen_sch_d.py:56`); the parent wall allocation is
0.3 A (`gen_sch_a.py:119`). Also aligned that parent's U23 from 0.5 to
1.0 A so its branches sum to 5.1 A. These are interim project figures.
A's child VBUS_WALL typical remains 0.5 A (`:1535`), giving the separate
child-typical sensitivity 3.8 + 1.0 + 0.5 = 5.3 A. Its owner must reconcile
these two typical models; the 0.3 A parent allocation is not silently
presented as the child's declaration.

```text
A's held converter peak = 6.9 = B 6.0 + wall 0.9 + D8 ZERO
D8 at declared typical: 6.0 + 1.0 + 0.9 = 7.9 A coincident
Every declared limit:   6.0 + 2.0 + 0.9 = 8.9 A coincident bound
```

B's 6.0 A is a declared lead peak, not a verified physical limiter. D8's
2.0 A is its declared peak and U23 nominal eFuse limit (`gen_sch_a.py:1308`);
wall 0.9 A rounds U32's nominal 0.89 A limit (`:1533-1535`). The nominal
0.89 A gives 7.89/8.89 A, not a tolerance bound justifying a lower declaration.
Nothing makes these loads non-coincident: U30/U26 drop only POE_EN and PD_EN
(`:1320-1321,1376`), not D8_EN or USBX_EN.

`ANALYSIS.md` recommends a session decision to declare A's converter peak
at the 8.9 A coincident bound, retaining the 7.9 A D8-typical case and naming
LM5176 average-loop fold-back as the limiter. If demand persists above the
actual threshold, output voltage falls, risking device brown-out and loss
of the shared fabric. This does not satisfy REQ-018's regulation requirement.
No peak decision is applied or claimed accepted; the draft leaves 6.9 A
pending that decision and labels it stale.

## M1. Existing PS-ALLTX model

Added comparison in `ANALYSIS.md` and `if_ab_power.py`.
`v2/docs/feasibility/POWER-THERMAL.md:706-711` gives S1 PLAN/HIGH
4.65/4.66 A and DEV 5.89/7.8 A. Its `:1037-1038` says DEV HIGH is inside
the LM5176 band. PWR-F01 to PWR-F03 at `:960-962` respectively flag the
WiFi child declaration below maker requirements, infer S1's 4.65 A PLAN,
and verify the KSZ maker currents. S1 with 1.6 A CM5 allowance, AsiaRF's
9.1 W maximum (AW7915-AED_V1, 30/05/2023, PDF p.4), other children typical,
fan and gate is about 4.575 A, within 0.1 A of 4.65 A. The original 3.407 A
mix instead uses CM5 0.9 A and WiFi 7 W. Neither establishes a waveform.
DEV's 7.8 A HIGH already supports calling fold-back risk; 7.9/8.9 A here
use explicit interface declarations rather than the full thermal model.

## M2. U26 and KSZ9897R

Relabelled U26 and added recomputation in `if_ab_power.py` and `ANALYSIS.md`;
the raw held entries remain visible. `POWER-THERMAL.md:145,962` cites
Microchip DS00002330D Table 6-1, p.169,
`v2/vendor/microchip/microchip-ksz9897-datasheet.pdf`: AVDDL 460 mA +
DVDDL 750 mA = 1.21 A at 1.2 V, typical at 25 C, all ports fully utilised
at 1000 Mb/s. That maker figure is VERIFIED; no maximum is published.
U26 input at assumed 0.85 efficiency and declared 5.0 V is
1.21*1.2/(0.85*5.0) = 0.341647059 A, against 0.15 A held. Replacing only
this entry moves the mixed sum 5.18 to 5.371647059 A, not a new mode total.
Board B's owner also owes PWR-F03's 2.5 V discrepancy: 0.330 A maker
typical against 0.15/0.25 A declared.

## M3. Copper inputs

Changed the script and hand arithmetic to rho20 = 1.72e-8 ohm m from
`v2/ecad/tools/dc_drop.py:23` (read only, not imported or run), and areas
1.25 mm2 at AWG16 and 0.83 mm2 at AWG18 from JST VH catalogue p.2.
These replace 1.724e-8, 1.31 and 0.823. JST gives range endpoints, not a
finished-cable resistance guarantee; the catalogue has no printed revision
(source index dates its PDF 9 January 2026). The 0.00393/C coefficient
stays an explicit ideal-copper assumption because neither source provides
it or an assembled cable part. The 60 C results remain conditional.

## M4. Mode name

Changed analysis and script to **PS-ALLTX**, REQ-018 and CONOPS section 5,
case S3 over S2, with three loaded compute slots stated as its condition.
The standby WiFi card, heater and outlets remain off.

## M5. Single output copy

Removed the verbatim output block from `ANALYSIS.md`; its reproduction
section references `if_ab_power.out` and that file's SHA256.

## M6. Enforced pins

Changed the script to compare both intent inputs against literal SHA256
pins before parsing or emitting calculations, failing nonzero and naming
the file on mismatch or absence. It parses the exact checked bytes.
Refreshed `if_ab_power.out`; the rerun and scratch perturbation are below.

## M7. Board B owner findings

No generator or intent was edited. Findings for the board B owner:

| Finding | Held basis | Action |
|---|---|---|
| Supervisor LDOs U40/U50/U60 each allocated 0.05 A | `gen_sch_b.py:95,209`; their +3V3_IOCx child rails declare 0.12/0.25 A | Reconcile parent and child currents; an LDO takes output current plus bias. Retain PWR-F04's thermal/firmware constraint. |
| LoRa U21 allocated 0.60 A | `gen_sch_b.py:87`; Ebyte E22-900M30S v1.20, PDF p.3: 0.650 A typical instantaneous TX | Reconcile the allocation; no maker maximum is stated. |
| U25 comment says 1.4 A on +3V3_DEV | `gen_sch_b.py:86` against 1.2 A typical / 2.0 A peak at `:130` | Reconcile comment, branch allocation and operating basis. |

## M8. Integrator findings

The IF-AB-POWER `contact_rating` at `pcb_interfaces.yaml:388` and
`ARCHITECTURE.md:1187` say the JST-VH document is not held. It is held at
`v2/vendor/connectors/jst-vh-catalogue.pdf`. Page 1 gives 10 A for AWG16
with standard header and 7 A for AWG18 with shrouded header; p.3 lists
the fitted B2P-VH standard header. The integrator owns these stale lines
and the contract current alignment. Preserve INCONCLUSIVE for AWG18
with the fitted standard header, for which JST states no current rating.

## Correction checks

All four requested checks ran and passed. These are reproduction and AI
review checks, not electrical acceptance. Only the draft's `--check` path
ran; the application stays unexecuted.

### (a) Calculation, deterministic rerun and changed-input refusal

Ran `python3 v2/docs/records/cx1/if_ab_power.py > v2/docs/records/cx1/if_ab_power.out`:
exit 0. An inline standard-library Python harness then ran it twice with
`subprocess.run`, asserted zero exit and empty stderr, and compared the
captured bytes to the saved file. It copied the script and both input
files, at the same relative paths, into a temporary tree under
`v2/docs/records/cx1/scratch/`. For each input separately it changed the
first ASCII `0` byte to `1`, verified exactly one byte differed and that
the changed JSON still parsed, and ran the copied script. Both refusals
were nonzero, named the input, and emitted no calculation on stdout.
The harness exited 0 and removed its own scratch fixtures.

```text
PASS normal run 1: exit 0; 29914 bytes equal if_ab_power.out byte for byte
PASS normal run 2: exit 0; 29914 bytes equal if_ab_power.out byte for byte
SHA256 d9fa215b08b8928641a02394449d3e80ca4bdf41c894321b5a7dbdeb9156545a
PASS one-byte mutation: v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json: exit 1; stdout empty
Refused: input v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json: sha256 mismatch; expected 3422910a15c4d1450141aa9a5fd725ba75bca9fcb42ae8c87e4cf3385d7d4498, got 4bb680dd2c7490cc30c200a73c4cbcf34685c3aff45ab90a63fc61ba4f92f2ea
PASS one-byte mutation: v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json: exit 1; stdout empty
Refused: input v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json: sha256 mismatch; expected 96ee391b3e3f638d7436cad51fcabf77999b530d8734c1feb93f7766a4877d8a, got 9a800f78b18e95c48ee7b11443eb67c0a442becc3b5bc1ea686307e308ab76df
PASS scratch fixtures removed; held inputs untouched
```

### (b) Draft entries verified without writing

Ran `python3 v2/docs/records/cx1/apply_declarations_draft.py --check`: exit 0.
Then an inline Python harness ran the same check with `python3 -B`, comparing
the record tree and both generators before/after by file set, SHA256 and
modification time. They were unchanged, with no marker or new file. The
harness exited 0. Exact output:

```text
PASS B1-A-S2: v2/ecad/tools/gen_sch_a.py: exact old text occurs once
PASS B1-A-Q28: v2/ecad/tools/gen_sch_a.py: exact old text occurs once
PASS B1-B-S2: v2/ecad/tools/gen_sch_b.py: exact old text occurs once
PASS B2-A-DEV: v2/ecad/tools/gen_sch_a.py: exact old text occurs once
PASS AST: v2/ecad/tools/gen_sch_a.py: replaced text parses
PASS AST: v2/ecad/tools/gen_sch_b.py: replaced text parses
CHECK ONLY: 4 entries, 2 generators; no writes, no marker.
PASS read-only snapshot: record tree and both generators unchanged; no marker or new file
```

### (c) Draft parses

Ran the following command, exit 0, output `PASS draft AST parses`:

```sh
python3 -c "import ast; ast.parse(open('v2/docs/records/cx1/apply_declarations_draft.py').read()); print('PASS draft AST parses')"
```

### (d) Updated hand arithmetic

AI review of `ANALYSIS.md`'s displayed +5V_DEV calculations, independently
recomputed using inline Python `decimal.Decimal` at precision 40. The
harness asserted the rounded results and their presence in the analysis;
it also checked the percentages and the 5.1/5.3 A typical alternatives.
It exited 0. Selected exact result lines:

```text
PASS Decimal hand check: D8 typical coincidence = 7.9
PASS Decimal hand check: Every-limit bound = 8.9
PASS Decimal hand check: Earliest loop = 7.095709571
PASS Decimal hand check: D8 typical margin = -0.804290429
PASS Decimal hand check: Every-limit margin = -1.804290429
PASS Decimal hand check: Typical-loop margin = -0.566666667
PASS Decimal hand check: Registry HIGH margin = -0.704290429
PASS Decimal hand check: Wire60 plus contact bound = 0.268661530
PASS Decimal hand check: Whole-budget margin = -0.168661530
PASS Decimal hand check: U26 inferred input = 0.341647059
PASS Decimal hand check: S1 registry comparison = 4.574938345
PASS hand arithmetic in ANALYSIS.md: 7.9/8.9 A cases, loop margins, lead-only losses, U26 and S1 comparison
```

The unchanged sources keep their authority. These checks select no
favourable limit and close no mode verdict. The next action is coordinator
review, a session decision on DEV's coincident peak, and generator/contract
owner action on the interim alignment and the listed findings.
