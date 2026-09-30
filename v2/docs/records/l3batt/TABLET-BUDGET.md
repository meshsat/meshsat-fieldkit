# The lid tablet's USB-C service budget, and Options A and B carried with it (stream l3batt, MESHSAT-1357)

**30 September 2026.** Branch `fnd/l3batt`. Source: `tablet.out` (from `tablet.py`), with `runtime.out`,
`load_trace.out` and `PROVENANCE.md` in this folder. This page answers the owner's instruction of that day:

> "The USB-C outlet's 45 W rating is peak capability, not continuous mission consumption. Check what the existing
> 42.8 W budget includes and prevent double-counting. [...] A specific tablet is useful for later verification, but its
> absence must not prevent proposing a measurable USB-C service budget now. Label that budget as a proposal, not
> verified tablet endurance. Do not assume maximum charging power throughout the mission, or remove charging to obtain
> a pass."

**What this page is.** The author's analysis, AI arithmetic; not a qualified review and not the independent check.
- **Prototype design:** nothing is bought, built, powered or measured.
- **The budget is a PROPOSAL**, measurable at the outlet. It is not verified tablet endurance, and no tablet model is
  picked (REQ-011's acceptance, "A tablet model is named", stays open, SC-45).
- Every figure is labelled MAKER, NETLIST, MODELED, INFERRED, ASSUMPTION or PROPOSAL.
- **The corrected power path is HYPOTHETICAL** and CONDITIONAL on three undocumented efficiencies; the circuit as drawn
  fails.
- **External packs are a PROPOSAL.**

## 1. No double counting (`tablet.out` 1)

**The 42.8 W holds nothing of the tablet or the outlet.**
- PS-IDLE-SPEC's 39 shares name no tablet, USB-C, outlet or PDO row.
- `load_trace.out` gives the tablet no row, and the outlets are off in every state.
- `pwr_budget.py` carries the outlet stage only as node PDO (efficiency 0.93, DECLARED), and only for its section 7.1
  variants.

**So every figure below is added to the 42.8 W.** That includes the outlet converter's own draw when enabled.

**The outlet converter's idle draw, enabled and not loaded: 1.09 W typ, 1.44 W max (INFERRED).** It is built from the
makers' terms on board A's drawn stage (U19 LM5176 fed and biased from VBAT, forced CCM, 206 kHz, four CSD18510Q5B;
U18 TPS25740A):

| Term | Typ / max | Basis |
|---|---|---|
| LM5176 VIN operating current, not switching | 2 / 4 mA at 14.4 V: 0.029 / 0.058 W | MAKER, LM5176 p.6 |
| Gate drive, four FETs switching (the 15 V contract) | 89 / 115 nC at VCC 7.35 V, x 206 kHz x 14.4 V: 1.057 / 1.370 W | MAKER, CSD18510Q5B p.3 (interpolated) |
| (two FETs switching, the 5 and 9 V contracts) | 0.529 / 0.685 W | INFERRED |
| TPS25740A while a sink is attached | 1 / 3 mA at 5 V over a 0.90 converter: 0.006 / 0.017 W | MAKER p.8, INFERRED |

The inductor's ripple and core losses at no load are not in any sheet held, so the true idle draw is higher by an
amount not quantified. **The budget takes 1.44 W.**

## 2. The proposed USB-C service budget (PROPOSAL, `tablet.out` 2 and 3)

**The class (MAKER, held back, cited in `v2/vendor/sources.txt`):**
- Zebra ET40/ET45, p.3: 8 in. 23.61 Wh; 10 in. 29.41 Wh.
- Samsung Galaxy Tab Active5, 8 in., p.2: 5,050 mAh typical, 4,900 mAh rated minimum. No Wh is printed; at a 3.85 V
  nominal it is about 19 Wh (INFERRED).

**The outlet as drawn (NETLIST, MAKER Tables 2, 3 and 5):**
- **The PD straps:** U18's straps advertise 5, 9 and 15 V at 3 A, **45 W peak**. Nothing can lower that in the field.
- **The enable:** PD_EN is the AND of PD_SW_EN (an output of the U28 PCA9555 expander) and OUTLET_OK. So the converter
  can already be switched by software.
- **No meter:** no INA226 monitors the outlet, so the kit cannot meter the energy it delivers there.

| Budget field | Proposed value | How it is held and measured |
|---|---|---|
| **Peak output power (P_CAP)** | **18 W at the outlet** | The TPS25740A's own setting (Table 5: PSEL direct to GND, PCTRL low, HIPWR high: 5 V 3.0 A, 9 V 2.0 A, 15 V 1.2 A). **It needs a strap change on board A (PSEL and PCTRL to GND), an electrical correction not designed or checked.** Measured with a USB-C power meter at the outlet |
| **Charging schedule** | **One 2 h window a day, 13 to 15 UTC**; the converter off otherwise | A software rule on the existing expander line PD_SW_EN. Measured by the line's state |
| **Energy delivered a day (E_OUT)** | **at most 36 Wh at the outlet** (= 18 W x 2 h) | A ceiling the strapped board and the window enforce without a meter. It covers one full recharge a day of the class's largest battery (29.41 Wh), allowing up to 22 % lost in the tablet's own charger (no sheet gives that loss). Measured in Wh a day at the outlet |
| **Starting charge** | **Tablet full at the mission start** | Every day's window, the first included, delivers the day's full budget, so the kit's energy does not depend on it |
| **Converter loss** | **0.930**, the lower of the declared 0.93 and the maker's curve (0.945 at 18 W: LM5176 Figure 6-2, the VIN 24 V curve at 1.5 A; typical, 25 C, the maker's circuit) | INFERRED (a pixel reading) |
| **Energy at VBAT a day** | **38.7 Wh** (19.4 W for 2 h); **peak 19.4 W** on top of the kit's load | INFERRED |

**The model charges the ceiling every day, at the cap for the whole window.** That is the kit side at its bound, not a
guessed tablet draw. Whether a given tablet takes a full recharge in 2 h at 18 W is for the named model's verification.

**The 45 W is never assumed.** Charging is never removed.

## 3. The schedule matters (`tablet.out` 5)

The table gives the extra usable store the mean day needs over the both-kept 4S9P lid. It is the corrected path, NOM,
TYP, with HF available; the figures are MODELED.

| Schedule | 48 h | 72 h |
|---|---|---|
| no tablet budget | +68.1 Wh | +68.1 Wh |
| **window 13 to 15 UTC (the proposal)** | **+68.1** | **+88.0** |
| window 10 to 12 UTC | +68.1 | +88.0 |
| window 19 to 21 UTC (after dark) | +107.2 | +130.9 |
| converter on all day, same 36 Wh (73.4 Wh at VBAT with 24 h of idle draw) | +139.7 | +197.4 |

**Why the two daylight windows read alike (from the model's own trace):**
- The node is level at 121.4 W, the path's limit in the model, from 09 to 14 UTC.
- The packs never fill that day.
- So a Wh the tablet takes in daylight is a Wh the packs do not take, whichever level hours the window holds.

**The rule this gives:** charge in a daylight window, and keep the converter off outside it. That rule is worth 43 to
109 Wh of store at 72 h.

## 4. Options A and B with the budget: the compact table

**Common to both options:**
- **HF profile:** the approved one is HF *available* (PS-IDLE-SPEC: the QMX's USB and HDMI 5 V, 0.32 W). HF
  *listening* (+1.14 W, PS-TYP's QMX HF row) is the sensitivity.
- **The case:** TYP. **WAB is a sensitivity.**
- **The store figures:** extra usable Wh over the both-kept store, at the lid's 13.23 C.
- **The corrected path:** HYPOTHETICAL and CONDITIONAL.

| Field | **Option A: 48 h required, 72 h desired** | **Option B: 72 h required, battery upgraded** |
|---|---|---|
| **HF operating profile** | available (case); listening (sensitivity) | the same |
| **Tablet service budget** | the PROPOSAL of section 2: 36 Wh a day at the outlet, 18 W peak, 13 to 15 UTC, full at start; 38.7 Wh a day at VBAT | the same |
| **Solar assumptions** | SC-37's mean September day at Leiden, one plane 40/0, 400 Wp in 2S2P into a 200 W stage window, starts 06 and 18 UTC, base +20 C, lid 13.23 C; TYP (WAB a sensitivity) | the same |
| **Usable storage needed**, HF available | present store 544.4 Wh at +20 C (502.6 Wh at the solar temperatures) **plus +68.1 (NOM), +114.7 (NOM90), +116.0 (WE), +164.3 (WE90)**; WAB +94.8 to +193.1 | the same present store **plus +88.0 (NOM), +186.8 (NOM90), +189.9 (WE), +286.1 (WE90)**; WAB +146.5 to +342.5 |
| **Usable storage needed**, HF listening | +105.1 (NOM), +156.3 (NOM90), +158.4 (WE), +206.0 (WE90) | +153.2 (NOM), +255.3 (NOM90), +260.2 (WE), +354.6 (WE90) |
| **Battery arrangement** | Option A(i), base 4S6P + lid 4S9P of 35E. It is not the ruled pack (D-06 is one 4S3P) and awaits L3-OD1. Plus an external store (PROPOSAL): 2 NH2054HD34-class packs (NOM to WE), 3 at WE90 (58 to 67 Wh a pack, INFERRED) | the same in-case store plus an external store (PROPOSAL): 2 packs (NOM), 3 to 4 (NOM90, WE), 5 (WE90) |
| **Mass and fit** | as checked: 3.0 kg of cells in-case, placement ESTABLISHED (a1mech A; three base rows OPEN). The packs add 0.87 kg (1.3 kg at WE90; 0.435 kg each, 150 x 77 x 23 mm), outside the case and not placed (PROPOSAL) | as checked in-case. The packs add 0.87 to 1.74 kg at NOM to WE (2.2 kg at WE90), outside the case (PROPOSAL) |
| **Electrical corrections** | the corrected power path (r11dep A-1, A-2, B-1 to B-5, C-1 to C-9; HYPOTHETICAL); the outlet's strap change for the 18 W cap; the window as a software rule. The external pack's join, connector, charge path and its 8.25 A limit: through the DC entry it is D-20's "external DC source" (EQ-13 (b)); at VBAT it reopens D-06 (EQ-13 (d)) | the same |
| **Battery-only endurance** (no solar; +20 C / -10 C; the window inside the run) | present store: 11.81 / 4.34 h (12.71 / 5.24 without the budget). With the NOM store: 13.40 / 4.99 h. With the WE store: 14.52 / 5.46 h | present store: the same. With the NOM store: 13.86 / 5.19 h. With the WE store: 16.24 / 6.17 h |
| **Solar-assisted endurance, present store** | **stops at the first dawn** (05 UTC; hour 23 or 11 of the 06 or 18 UTC start, about 11 to 23 h) in every case, with and without the budget. 48 h unserved, TYP: NOM 102.2, WE 104.6 Wh | the same first stop. 72 h unserved, TYP: NOM 165.7, WE 169.2 Wh |
| **Solar-assisted endurance, the option's store** | carries 48 h on the mean day (CONDITIONAL). **The 72 h desired is not reached:** the 48 h store stops at the third dawn (hour 48 of the 06 UTC start, 57 to 60 of the 18 UTC start), 15.3 (NOM) to 113.4 (WE90) Wh short | carries 72 h on the mean day (CONDITIONAL) |
| **As drawn** | fails: 302.7 Wh unserved at 48 h TYP; a store would need at least +328 Wh and cures no defect | fails: 566.6 Wh unserved at 72 h TYP; at least +614 Wh |
| **Recommendation** | **Relief of about one pack, not a cure.** The budget widens the gap between the options: A saves 20 Wh at NOM and 72 to 122 Wh at NOM90, WE and WE90 (TYP). It still needs an external store, because the first September night binds at either length, and it does not reach its desired 72 h | **Feasible on the model only with its store:** about **190 Wh usable** at TYP (WE, NOM90; 3 to 4 packs, 1.3 to 1.7 kg), or about 260 Wh with HF listening, **with** the corrected path and the outlet correction. Otherwise record M1 as not met (M-02) rather than shorten it |

**Battery-only and solar-assisted figures are kept apart,** as the owner asked.
- **Battery-only** is hours from full with no sun.
- **Solar-assisted** is the mean-day balance.
- **Neither is demonstrated capability.**

**Coverage of past September windows stays 0 %** (`runtime.out` 4, without the budget). The budget cannot raise it.

## 5. Provenance labels

- **72 hours is the session's figure.** It first appears as the layer 2 closer's SC-L2-05 (commit `de59686e`) and
  became **SC-21** (`authority: SESSION`) on 27 September 2026.
  - **D-20** (28 September) preserves M1 and REQ-072 "with their specified duration" without stating a number.
  - The owner's word "approved" first appears in **D-21** (30 September): "the approved 72-hour mission". No approval
    act is found before it (`PROVENANCE.md`).
  - Neither option treats 72 hours as an immutable owner ruling. The choice between A and B is the owner's
    requirement decision.
- **WAB is a sensitivity case.** No owner ruling in the tree makes it an acceptance condition; it stays a sensitivity
  unless the owner selects it.

## 6. What changes from `COMPARISON.md`

**What `COMPARISON.md` left open:**
- Its store figures carry no tablet energy. Its functions row calls tablet charging "UNQUANTIFIED".
- Its only bound was the outlet's 45 W contract.

**What this page changes:**
- **It quantifies tablet charging** with the proposed budget.
- **At 72 h TYP the store rises.** NOM goes from +68.1 to +88.0 Wh. WE and NOM90 go from about +117 to about +188 Wh.
- **So Option B's external store is about 190 Wh, not about 120 Wh.**
- **Option A's store is unchanged at NOM.** At WE and NOM90 it rises from about +80 to about +115 Wh.
- **One engineering change is added to both options:** the outlet's strap change, so that the board holds the 18 W cap.
